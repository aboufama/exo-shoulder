"""skeptic read-only probe (proxtrack-relay-knuckle-4r): th margin per relayed pose, dK / phi spans over the taken poses, per-part in-band (bench, stackfix).
Run: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_skeptic_probe_proxtrack.py <out.json>. Known defect: the link_pts per-part slice uses len(tuple); rigid parts are correct."""
import importlib.util, json, os, sys, time, math
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
RID = "proxtrack-relay-knuckle-4r"
def _load(n, p):
    sp = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
BV = _load("bv_sk", os.path.join(REPO, "docs/concepts/verify", RID + "-buildability.py")); PT = BV.PT
t0 = time.time(); S = PT.prepare(BV.CLAIM, 110, 360, exact=True); M, B = S["M"], S["B"]
PT.bump_amounts = BV.stackfix_amounts
o = PT.wear(S, BV.CLAIM)
out = dict(gate=o["gate_gap"], plain=o["wear"]["gap"], secs=round(time.time() - t0, 1))
D = M.D; u1, u2, u3 = D.u; uK = D.uK
a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2
dK = np.asarray(M.dK, float); phi = np.asarray(S["phi_b"], float)
taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
rows = []
for i in taken:
    R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
    jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
    th = BV._ang(u1, j3); a1e = BV._ang(u1, j2); a2e = BV._ang(j2, j3); b1 = BV._ang(u1, jK); c = BV._ang(jK, j3)
    forced = abs(float(dK[i])) > 1e-6
    own = min(BV._dm(th, b1, c), BV._dm(th, a1e, a2e)) if forced else BV._dm(th, a1, a2)
    rows.append(dict(i=i, own=round(float(own), 4), forced=forced, phi=round(float(phi[i]), 3), dK=round(float(dK[i]), 5), kind=B.kind[i]))
rel = [r for r in rows if abs(r["phi"]) > 1e-9]
ro = sorted(r["own"] for r in rel)
out["relayed_taken"] = len(rel)
out["relayed_th"] = ro
out["relayed_th_le_5p01"] = sum(1 for x in ro if x <= 5.01)
out["relayed_th_le_5p1"] = sum(1 for x in ro if x <= 5.1)
out["relayed_th_median"] = float(np.median(ro)) if ro else None
allo = sorted(r["own"] for r in rows)
out["all_th_le_5p01"] = sum(1 for x in allo if x <= 5.01); out["n_taken"] = len(rows)
tk = np.array(taken)
out["dK_taken_deg"] = dict(min=round(math.degrees(float(dK[tk].min())), 2), max=round(math.degrees(float(dK[tk].max())), 2),
                           forced=int(sum(abs(dK[tk]) > 1e-6)))
out["phi_taken"] = dict(min=round(float(phi[tk].min()), 2), max=round(float(phi[tk].max()), 2), nonzero=int(sum(abs(phi[tk]) > 1e-9)))
# arrays of length n on M (knee readings, if any)
for k, v in vars(M).items():
    try:
        a = np.asarray(v, float)
        if a.ndim == 1 and len(a) == len(B.idx) and k not in ("dK",):
            out.setdefault("M_arrays", {})[k] = [round(float(a[tk].min()), 4), round(float(a[tk].max()), 4)]
    except Exception:
        pass
# per-part in-band (assumes B.res order = rigid then link_pts; checked by length)
try:
    parts = [(("rigid", k), len(X)) for k, (_, X) in M.rigid.items()] + [(("link", k), len(X)) for k, X in M.link_pts.items()]
    nC = sum(n for _, n in parts); pp = {}
    for i in taken:
        d = np.asarray(B.res[i], float)[:nC]; s = 0
        for (t, k), n in parts:
            x = d[s:s + n]; s += n
            e = pp.setdefault(f"{t}:{k}", [0, 0, 1e9]); e[0] += len(x); e[1] += int(((x >= 2) & (x <= 14)).sum()); e[2] = min(e[2], float(x.min()) if len(x) else 1e9)
    out["per_part"] = {k: dict(n=v[0], ib14=round(v[1] / max(v[0], 1), 4), min_mm=round(v[2], 2)) for k, v in pp.items()}
    out["per_part_note"] = f"nC {nC}; res len {len(B.res[taken[0]])}"
except Exception as ex:
    out["per_part_err"] = repr(ex)
json.dump(out, open(sys.argv[1], "w"), indent=1, default=float); print("done", out["secs"])
