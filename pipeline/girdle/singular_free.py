"""Can a 3R chain keep its singularity out of the whole plausible everyday workspace? For a1 = a2 = 90 deg the 3R
(J1 = b on the base, J3 = an arm-fixed direction w) is singular when R_arm w is parallel to +-b. Over the red team's
workspace (49,543 poses), search pairs (b, w) for the largest worst-case angle between R_arm w and +-b. w = the humerus
axis is the 2R + ring case (8.6 deg). -> singular_free.json"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "redteam")); import girdle as GD
from rt_common import plausible
pl, el, r = np.meshgrid(np.arange(-90, 151, 5.0), np.arange(0, 171, 5.0), np.arange(-90, 91, 5.0), indexing="ij"); pl, el, r = pl.ravel(), el.ravel(), r.ravel()
k = plausible(pl, el); P = np.c_[pl[k], el[k], r[k] - pl[k]]; RH = np.array([GD.Rh_of(*p) for p in P]); print(len(P), "poses", flush=True)
rng = np.random.default_rng(0); Wc = GD.unit(rng.normal(size=(400, 3))); Bc = GD.unit(rng.normal(size=(4000, 3)))
sub = RH[::7]; best = []
for w in Wc:
    D = sub @ w; ang = np.degrees(np.arccos(np.clip(np.abs(Bc @ D.T), 0, 1))).min(1); j = int(np.argmax(ang)); best.append((ang[j], Bc[j], w))
best.sort(key=lambda t: -t[0]); out = []
for a0, b, w in best[:10]:                                                   # verify on the full workspace + local polish
    from scipy.optimize import minimize
    def f(v):
        bb = GD.bvec(v[0], v[1]); ww = GD.w_dir(v[2], v[3]); return -float(np.degrees(np.arccos(np.clip(np.abs((RH @ ww) @ bb), 0, 1))).min())
    v0 = GD.azel(b) + GD.delaz(w); rr = minimize(f, v0, method="Nelder-Mead", options=dict(maxiter=400, xatol=0.05, fatol=0.01))
    out.append(dict(clearance_deg=round(-rr.fun, 1), b=[round(x, 1) for x in rr.x[:2]], w=[round(x, 1) for x in rr.x[2:]], b_vec=GD.bvec(*rr.x[:2]).round(3).tolist(), w_arm=GD.w_dir(*rr.x[2:]).round(3).tolist()))
    print(out[-1], flush=True)
hum = float(np.degrees(np.arccos(np.clip(np.abs(Bc @ (RH[::7] @ np.array([0, -1.0, 0])).T), 0, 1))).min(1).max())
res = dict(workspace_poses=int(len(P)), humerus_axis_w_clearance_deg=round(hum, 1), best=sorted(out, key=lambda d: -d["clearance_deg"]))
json.dump(res, open(os.path.join(HERE, "singular_free.json"), "w"), indent=1); print("best 3R clearance", res["best"][0]["clearance_deg"], "deg vs humerus-axis J3 (2R + ring)", res["humerus_axis_w_clearance_deg"])
