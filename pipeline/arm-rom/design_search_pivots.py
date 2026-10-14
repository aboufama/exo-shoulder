"""Shoulder morphology search under the real rules: both mounts are fixed pivots.

  J1  pivot fixed on the scapula, axis b (scapula frame; on the back or the top of the shoulder)
  L1  curved link, inner shell, arc a1
  J2  pivot between the links (inner and outer shells, so the links may cross)
  L2  curved link, outer shell, arc a2
  J3  pivot fixed on the upper-arm link, axis w fixed in the HUMERUS frame (the post: outside the arm, delta from
      the arm's axis, at azimuth az around it); the upper-arm link is rigid to the arm
All axes pass through the shoulder centre, all links on the ~124 mm shell (same form factor as now). The chain must
produce every humerus orientation itself (no ring): u3 = R_humerus w; the triangle (b, c, u3) gives J2 and the joint
angles, on ONE assembly branch for the whole range. A pose counts if the J1 and J3 axes stay >= SING from aligned
(gimbal lock), the links stay >= SING from straight or folded, and both links stay off the head, neck, torso and the
upper arm. Base rides on the scapula (same rhythm, body and poses as design_search.py).

    python3 design_search_pivots.py
"""
import json
import math
import os
import concurrent.futures as cf

import numpy as np
import design_search as D

SING = 12.0
H_FRAMES = np.array([p[3] for p in D.POSES])             # humerus frames in the scapula frame (N, 3, 3)


def w_dir(delta, az):
    """J3 axis in the humerus frame: delta from the arm axis (-Y), az around it (0 = lateral +Z, 90 = anterior +X)."""
    d, a = delta * D.D2R, az * D.D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def evaluate(design):
    b = np.asarray(design["b"], float); a1, a2 = design["a1"] * D.D2R, design["a2"] * D.D2R
    w = w_dir(design["delta"], design["waz"])
    u3 = H_FRAMES @ w                                       # (N, 3)
    h = D.HG
    cb = np.clip(u3 @ b, -1, 1); beta = np.arccos(cb)
    m = SING * D.D2R
    lo, hi = abs(a1 - a2), min(a1 + a2, 2 * math.pi - a1 - a2)
    ok = (beta >= max(lo, 0) + m) & (beta <= hi - m) & (beta >= m) & (beta <= math.pi - m)
    cosC = (math.cos(a2) - math.cos(a1) * cb) / (math.sin(a1) * np.sin(beta) + 1e-12)
    C = np.arccos(np.clip(cosC, -1, 1))
    e = u3 - cb[:, None] * b; e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-12
    f = np.cross(b, e)
    best = None
    for br in (+1, -1):
        c = math.cos(a1) * b + math.sin(a1) * (np.cos(C)[:, None] * e + br * np.sin(C)[:, None] * f)
        L1 = D.slerp_pts(np.broadcast_to(b, c.shape), c, 10)
        L2 = D.slerp_pts(c, u3, 10)
        pts = np.concatenate([L1, L2], axis=1)
        okb = ok.copy()
        ang = np.degrees(np.arccos(np.clip(np.einsum("nmj,nj->nm", pts, h), -1, 1)))
        okb &= ang.min(1) >= D.RHO_ARM                          # no link over the upper arm
        P = np.einsum("nij,nmj->nmi", D.RS, pts * D.R_SHELL)
        okb &= ~D.in_body(P).any(1)
        cov = float(okb.mean())
        if best is None or cov > best[0]:
            best = (cov, br)
    return dict(design, cov=best[0], branch=best[1])


if __name__ == "__main__":
    designs = []
    for az in range(0, 360, 20):
        for el in range(-20, 91, 15):
            b = np.array([-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)])
            if not D.base_ok(b): continue
            for a1 in (60, 75, 90, 105, 120):
                for a2 in (60, 75, 90, 105, 120):
                    for delta in (40, 55, 70, 90):
                        for waz in range(-90, 181, 30):
                            designs.append(dict(b=b.round(5).tolist(), az=az, el=el, a1=a1, a2=a2, delta=delta, waz=waz))
    print(f"{len(D.POSES)} poses, {len(designs)} pivot-pivot designs", flush=True)
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        res = list(ex.map(evaluate, designs, chunksize=64))
    res.sort(key=lambda r: -r["cov"])
    for r in res[:15]:
        print(f"  cov {100 * r['cov']:5.1f}%  base az {r['az']:3d} el {r['el']:3d}  arcs {r['a1']}/{r['a2']}  arm pivot delta {r['delta']} az {r['waz']:4d}  branch {r['branch']:+d}")
    json.dump(res[:300], open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_search_pivots.json"), "w"))
