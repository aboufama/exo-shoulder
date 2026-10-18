"""Auditor tool (new file, 2026-10-18 ~21:00 UTC): the J3-dowel reachability check (continuity of the K self-motion at a
fixed arm pose) for the freek-oracle-route-knuckle-4r FINAL POLISH pick1 - the claim the ledger keys (polished_gap 15.40).

The re-dispatched verifier's docs/concepts/verify/freek-oracle-route-knuckle-4r/reverify_skipcheck.py (WIP commit b31b802)
ran this check on the VERIFIED config (q3max 86) only: the model's ODesign.j3stop scans |dK| upward from the slaved value
d0 and takes the first FEASIBLE sample with q3 <= q3max, skipping infeasible samples in between; a skipped infeasible band
means the spring-driven K cannot reach the dowel without the arm moving (a static island, docs/ALIGNMENT.md S5). This file
runs the same record (same code, copied, the verify file is not imported or edited) with pick1's parameters: the model's
own params() with the row's polished_params_priced laid over them, exactly as tools/alignment_remeasure_freek_polish.py
does. Kinematic only (no skin, no score). It never edits the model, a bench, a judge or a row.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_freek_skipcheck_pick1.py bench|held
        -> docs/alignment/remeasure/freek_polish_pick1/skipcheck_pick1_<wear>.json
"""
import importlib.util, json, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RID = "freek-oracle-route-knuckle-4r"
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
PRICED = dict(ROW["polished_params_priced"])
OUTD = os.path.join(REPO, "docs", "alignment", "remeasure", "freek_polish_pick1")


def main(wear):
    t0 = time.time()
    sp = importlib.util.spec_from_file_location("fo_skip_pick1", os.path.join(REPO, "docs", "concepts", "models", RID + ".py"))
    FO = importlib.util.module_from_spec(sp); sp.loader.exec_module(FO)
    PK, CB, RM = FO.PK, FO.CB, FO.RM
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
            dq = np.diff(qq[:k + 1]) if k < len(g) else np.diff(qq)
            REC.append(dict(n=len(Q), i=int(i), d0=round(d0, 2), hit=None if v is None else round(v, 2), state0=int(self._state[i]),
                            skipped=int(len(bad)), skipped_dK=[round(float(g[b]), 1) for b in bad][:8],
                            d0_ok=bool(f["ok"][0]) if len(g) else None, q3_d0=round(float(qq[0]), 2) if len(g) else None,
                            dq3_pos=int((dq > 1e-6).sum())))
        return out
    FO.ODesign.j3stop = j3stop_rec
    P = FO.params({"q3max": PRICED["q3max"]}); P.pop("_seed", None); P.update(PRICED)
    FO.ODesign.SLOT55 = False; FO.ODesign.TAB = None
    B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
    REC.clear()
    M = FO.KModel(B, dict(P))
    nB = len(B.idx)
    recs = [r for r in REC if r["n"] == nB]
    summ = dict(wear=wear, config="pick1", params={k: P[k] for k in PRICED}, n=nB, engaged=len(recs),
                refused=sum(1 for r in recs if r["hit"] is None),
                skipped_any=sum(1 for r in recs if r["skipped"] and r["hit"] is not None),
                d0_infeasible=sum(1 for r in recs if r["d0_ok"] is False),
                q3_rises=sum(1 for r in recs if r["dq3_pos"]),
                kin_ok_engaged=sum(1 for r in recs if M.kin_ok[r["i"]] and r["hit"] is not None),
                secs=round(time.time() - t0, 1))
    os.makedirs(OUTD, exist_ok=True)
    json.dump(dict(summary=summ, recs=recs), open(os.path.join(OUTD, f"skipcheck_pick1_{wear}.json"), "w"), indent=1, default=float)
    print(json.dumps(summ, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bench")
