"""which other parts' metal sits within 4 mm of hub 2's chamfer / flat regions (in hub 2's member frame, per taken pose on the fast bench)"""
import importlib.util, json, os
import numpy as np
REPO = "/home/user/exo-shoulder"; os.environ.pop("CB_EXACT", None)
sp = importlib.util.spec_from_file_location("h2f_n", os.path.join(REPO, "docs/concepts/models/conecut-h2facet-knuckle-3r.py")); H2 = importlib.util.module_from_spec(sp); sp.loader.exec_module(H2)
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-h2facet-knuckle-3r.json")))
P = H2._clamp(dict(H2.PARAMS, **row["best_params"]))
B = H2.CB.Bench(n_clip=60, n_ws=160); M = H2.CC.CCModel(B, dict(P)); M.run()
mem2, cen2, ax2 = M.cyl["hub2"]; u, e, f = H2.frame(ax2); F = H2.Facet(P)
names = {}
for k, (m, X) in M.rigid.items(): names[("r", k)] = (m, X)
for k, v in M.link_pts.items(): names[("l", k)] = (v[0], v[1])
out = {}
taken = [i for i in range(len(B.idx)) if bool(M.kin_ok[i])]
for key, (m, X) in names.items():
    if key == ("r", "hub2") or not len(X): continue
    best = (1e9, None)
    for i in taken:
        R7, t7 = M.T(mem2, i); Rm, tm = M.T(m, i)
        W = (Rm @ X.T).T + tm; L = (R7.T @ (W - t7).T).T     # into member-7 local
        r, az, z = H2.to_cyl(L, cen2, u, e, f)
        # distance to the chamfer sector edge region (r 10, z 0..1.4, |az-az0|<=hw) and to the flat region (az azf+-20, z 3.9..12.25)
        dch = np.where(np.abs(H2.wrapd(az - F.az0)) <= F.hw + 5, np.hypot(np.maximum(r - 10, 0) + np.maximum(8.6 - r, 0), np.maximum(z - 1.4, 0) + np.maximum(-z, 0)), 1e9)
        dfl = np.where(np.abs(H2.wrapd(az - F.azf)) <= 25, np.hypot(np.maximum(r - 10, 0) + np.maximum(9.4 - r, 0), np.maximum(z - 12.25, 0) + np.maximum(3.9 - z, 0)), 1e9)
        d = min(float(dch.min()), float(dfl.min()))
        if d < best[0]: best = (round(d, 2), dict(i=i, which="chamfer" if dch.min() <= dfl.min() else "flat", member=int(m)))
    out["%s:%s" % key] = best
print(json.dumps(out, indent=1, default=float))
