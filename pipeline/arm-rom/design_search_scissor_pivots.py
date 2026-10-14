"""Your scissor topology, re-optimised under the pivot rules (no ring).

  J1  base pivot fixed on the scapula, axis b
  two-rhombus spherical scissor, link arc alpha (fold limit 14 deg, side pins >= 8 deg apart when stretched)
  output pin = the upper-arm post: axis w fixed in the humerus frame (delta from the arm axis, azimuth waz)
  BOTTOM on the post with a 180 deg range (centre optimised), rigid to the arm
The output pin direction is then fixed by the pose (u0 = R_humerus w): no redundancy. A pose counts if the scissor
can reach u0, the post angle is inside its 180 deg window, and the scissor links stay off the head, neck, torso and
the upper arm. Same body, scapula rhythm and poses as the other searches.

    python3 design_search_scissor_pivots.py
"""
import json
import math
import os
import concurrent.futures as cf

import numpy as np
import design_search as D
from design_search_pivots import H_FRAMES, w_dir


def evaluate(design):
    b = np.asarray(design["b"], float); alpha = design["alpha"] * D.D2R
    w = w_dir(design["delta"], design["waz"])
    u0 = H_FRAMES @ w; h = D.HG
    B = np.broadcast_to(b, u0.shape)
    pts, ok = D.scissor(B, u0, alpha)
    ang = np.degrees(np.arccos(np.clip(np.einsum("nmj,nj->nm", pts, h), -1, 1)))
    ok &= ang.min(1) >= D.RHO_ARM
    P = np.einsum("nij,nmj->nmi", D.RS, pts * D.R_SHELL)
    ok &= ~D.in_body(P).any(1)
    # post angle: BOTTOM's direction (toward the arm) relative to the scissor's midline (toward the base), about u0
    tb = B - (B * u0).sum(1, keepdims=True) * u0; tb /= np.linalg.norm(tb, axis=1, keepdims=True) + 1e-12
    th = h - (h * u0).sum(1, keepdims=True) * u0; th /= np.linalg.norm(th, axis=1, keepdims=True) + 1e-12
    post = np.degrees(np.arctan2((np.cross(tb, th) * u0).sum(1), (tb * th).sum(1)))
    best = (0.0, 0)
    for c in range(-180, 180, 10):
        d = (post - c + 180) % 360 - 180
        cov = float((ok & (np.abs(d) <= 90)).mean())
        if cov > best[0]: best = (cov, c)
    return dict(design, cov=best[0], post_centre=best[1], unlimited_post=float(ok.mean()))


if __name__ == "__main__":
    designs = []
    for az in range(0, 360, 20):
        for el in range(-20, 91, 15):
            b = np.array([-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)])
            if not D.base_ok(b): continue
            for alpha in (35, 39, 43):
                for delta in (40, 55, 70, 90):
                    for waz in range(-90, 181, 30):
                        designs.append(dict(b=b.round(5).tolist(), az=az, el=el, alpha=alpha, delta=delta, waz=waz))
    print(f"{len(designs)} scissor designs", flush=True)
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        res = list(ex.map(evaluate, designs, chunksize=32))
    res.sort(key=lambda r: -r["cov"])
    for r in res[:12]:
        print(f"  cov {100 * r['cov']:5.1f}%  base az {r['az']:3d} el {r['el']:3d}  alpha {r['alpha']}  post delta {r['delta']} az {r['waz']:4d}  post centre {r['post_centre']}  (unlimited post {100 * r['unlimited_post']:.1f}%)")
    json.dump(res[:300], open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_search_scissor_pivots.json"), "w"))
