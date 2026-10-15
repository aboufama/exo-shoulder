"""Pareto trade-off for the 3-DOF 2R shoulder + humeral-rotation ring: worst GH misalignment (exact minimax LP axis
points, girdle.py) vs ring travel (deg), singular margin >= 20 deg on the fitting clips. Fit on 6 clips, report
held-out. Weighted sum sweep: minimise worst + lam * travel.
    python3 ring_pareto.py -> ring_pareto.json"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import girdle as GD
C = json.load(open(os.path.join(HERE, "..", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = np.array([c["name"] for c in C["clips"] for f in c["frames"]]); W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
FIT = ~np.isin(names, ["Wave", "Walking arm swing"]); M = GD.Motion(W); MF = GD.Motion(W[FIT]); MT = GD.Motion(W[~FIT])
def ev(x, br, lam, exact, MM=MF, y=None):
    y = MM.lift if y is None else y
    ch = GD.Chain3(dict(b=(x[0], x[1]), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=br, w=None)); r = ch.kin(MM)
    if r is None: return 1e3, None
    A, mg, ok, *_ = r
    if not ok.all(): return 900.0, None
    res = (GD.fit_minimax(A, y, True, 60.0) if exact else GD.fit_lsq(A, y, True))[1]; tr = ch.joint_travel(MM)["J3"]["span"]
    return float(res.max()) + lam * tr + 10 * max(0.0, 20 - mg.min()), dict(worst=float(res.max()), travel=tr, margin=float(mg.min()))
rt = json.load(open(os.path.join(HERE, "ring_travel.json")))["best"]; p0 = json.load(open(os.path.join(HERE, "p0_results.json")))["architectures"]["3 DOF: 2R shoulder (offset axes) + humeral-rotation ring"]["params"]
seeds = [([rt["b"][0], rt["b"][1], rt["a1"], rt["a2"]], rt["branch"]), ([p0["b"][0], p0["b"][1], p0["a1"], p0["a2"]], int(p0["branch"]))]
out = []
for lam in (0.0, 0.01, 0.02, 0.04, 0.08, 0.16):
    best = None
    for x0, br in seeds:
        r = minimize(lambda x: ev(x, br, lam, False)[0], x0, method="Nelder-Mead", options=dict(maxiter=700, xatol=0.1, fatol=0.01))
        r = minimize(lambda x: ev(x, br, lam, True)[0], r.x, method="Nelder-Mead", options=dict(maxiter=200, xatol=0.05, fatol=0.005))
        if best is None or r.fun < best[0]: best = (r.fun, r.x, br)
    f, x, br = best; _, fit = ev(x, br, 0, True)
    ch = GD.Chain3(dict(b=(x[0], x[1]), a1=float(x[2]), a2=float(x[3]), branch=br, w=None)); A, mg, *_ = ch.kin(MF); xo, _ = GD.fit_minimax(A, MF.lift, True, 60.0)
    At, mgt, *_ = ch.kin(MT); rest = GD.residual(At, xo, MT.lift); trall = ch.joint_travel(M)["J3"]
    row = dict(lam=lam, b=[round(float(v), 1) for v in x[:2]], a1=round(float(x[2]), 1), a2=round(float(x[3]), 1), branch=br, worst_fit_mm=round(fit["worst"], 2),
               worst_held_out_mm=round(float(rest.max()), 2), ring_travel_fit_deg=round(fit["travel"], 1), ring_travel_all_deg=trall["span"],
               margin_fit_deg=round(fit["margin"], 1), margin_held_out_deg=round(float(mgt.min()), 1), _x=xo.tolist())
    out.append(row); print({k: v for k, v in row.items() if k != "_x"}, flush=True)
json.dump(out, open(os.path.join(HERE, "ring_pareto.json"), "w"), indent=1)
