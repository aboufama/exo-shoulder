"""The current CAD scissor (A) re-scored against the anatomical body, exactly as design_search_anat.py scores the new
families: base on the scapula, links at R - 5 = 119 mm kept >= 9 mm off the trunk / girdle skin and the upper-arm skin
(except within 15 deg of the output pin, where BOTTOM meets the arm), BOTTOM's post limited to 180 deg."""
import math
import numpy as np
import design_search as D
import design_search_anat as A
import rom as R
from current_rescore import LINK_PINS, Mt

res = []
for (plane, elev, axial, Hg, Rs) in D.POSES:
    Hc = Mt @ Hg; RB = Hc @ R.H_CAD.T; u0 = RB @ R.U0["p0"]
    th = math.degrees(math.acos(max(-1, min(1, u0[0])))); s = R.sigma_of(th)
    if s is None: res.append((False, None, None, None)); continue
    RI9, u0s = R.table_R(s, "I9")
    psi = math.atan2(u0[2], u0[1]) - math.atan2(u0s[2], u0s[1]); Rp = R.rot([1, 0, 0], psi)
    links = {k: Rp @ R.table_R(s, k)[0] for k in LINK_PINS}
    Rg = RB @ links["I9"].T
    g = math.degrees(math.atan2(np.dot(u0, [Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1]]), np.trace(Rg) - 1))
    Rd = links["O4"] @ links["I9"].T
    dl = math.degrees(math.atan2(np.dot(u0, [Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]]), np.trace(Rd) - 1))
    pts = []
    for k, pins in LINK_PINS.items():
        ps = [links[k] @ R.U0[p] for p in pins]
        for a, b in zip(ps, ps[1:]): pts += list(D.slerp_pts(a[None], b[None], 6)[0])
    res.append((True, g - dl / 2, np.array(pts) @ Mt, u0 @ Mt))
idx = [i for i, r in enumerate(res) if r[0]]
A.SUB = np.array(idx)
pts = np.array([res[i][2] for i in idx]); post = np.array([res[i][3] for i in idx])
ok = A.skin_clear(pts, 124.0, post)
gam = np.array([res[i][1] for i in idx])
best = max(((float((ok & (np.abs((gam - c + 180) % 360 - 180) <= 90)).sum()) / len(res), c) for c in range(-180, 180, 10)))
print(f"current CAD scissor vs the anatomical body (R 124, 180 deg post centre {best[1]}): {100 * best[0]:.1f}%   (ellipsoid body: 65.9%)")
