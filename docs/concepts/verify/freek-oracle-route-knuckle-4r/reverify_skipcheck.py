"""Verifier check (2026-10-18 re-dispatch): is the J3-dowel K reachable from the slaved state by a CONTINUOUS K self-motion at
the same arm pose? The model's j3stop() scans |dK| from the slaved value d0 upward and takes the first FEASIBLE sample with
q3 <= q3max, skipping infeasible samples in between. A skipped infeasible band means the spring-driven K cannot get there
without the arm moving (a static island). Kinematic only (no skin); bench poses = Bench(110,360) (and held)."""
import importlib.util, json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"
os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
sp = importlib.util.spec_from_file_location("fo_skip", os.path.join(REPO, "docs/concepts/models/freek-oracle-route-knuckle-4r.py"))
FO = importlib.util.module_from_spec(sp); sp.loader.exec_module(FO)
PK, KIT, CB, RM = FO.PK, FO.KIT, FO.CB, FO.RM
wear = sys.argv[1] if len(sys.argv) > 1 else "bench"
REC = []
orig = FO.ODesign.j3stop
def j3stop_rec(self, Q, q, ok):
    out = orig(self, Q, q, ok)
    q3max = self.p.get("q3max"); dkb = self.dKB(); grid = np.arange(0.0, dkb + 1e-9, 0.5)
    for i, v in out.items():
        d0 = abs(float(np.degrees(self._dK[i]))); g = grid[grid >= d0 - 1e-9]
        f = self.free_solve(np.repeat(Q[i][None], len(g), 0), g); qq = np.degrees(PK.wrap(f["q"][:, 2]))
        hit = np.nonzero(f["ok"] & (qq <= float(q3max)))[0]
        k = int(hit[0]) if len(hit) else len(g)
        bad = np.nonzero(~f["ok"][:k])[0]
        why = []
        for b in bad:
            why.append(dict(dK=round(float(g[b]), 1), m3e=round(float(f["m3e"][b]), 2), rel=round(float(f["rel"][b]), 2), q3=round(float(qq[b]), 2)))
        # also: does q3 decrease monotonically with K along the scan (spring stable)?
        dq = np.diff(qq[:k + 1]) if k < len(g) else np.diff(qq)
        REC.append(dict(n=len(Q), i=int(i), d0=round(d0, 2), hit=None if v is None else round(v, 2), state0=int(self._state[i]),
                        skipped=int(len(bad)), skipped_dK=[round(float(g[b]), 1) for b in bad][:8], why=why[:4],
                        d0_ok=bool(f["ok"][0]) if len(g) else None, q3_d0=round(float(qq[0]), 2) if len(g) else None,
                        dq3_pos=int((dq > 1e-6).sum())))
    return out
FO.ODesign.j3stop = j3stop_rec
P = FO.params({"q3max": 86}); P.pop("_seed", None)
FO.ODesign.SLOT55 = False; FO.ODesign.TAB = None
B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
REC.clear()
M = FO.KModel(B, dict(P))
nB = len(B.idx)
recs = [r for r in REC if r["n"] == nB]
print(json.dumps(dict(wear=wear, n=nB, engaged=len(recs), refused=sum(1 for r in recs if r["hit"] is None),
                      skipped_any=sum(1 for r in recs if r["skipped"] and r["hit"] is not None),
                      d0_infeasible=sum(1 for r in recs if r["d0_ok"] is False),
                      q3_rises=sum(1 for r in recs if r["dq3_pos"]),
                      kin_ok_engaged=sum(1 for r in recs if M.kin_ok[r["i"]] and r["hit"] is not None))))
json.dump(dict(wear=wear, recs=recs, kin_ok=[int(x) for x in np.nonzero(M.kin_ok)[0]]),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"reverify_skip_{wear}.json"), "w"), indent=1, default=float)
