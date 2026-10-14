"""Serial 3R spherical shoulder: the tendon-friendly option (three large joints, all axes through the shoulder centre).

  J1  base joint on the scapula, axis b (fixed in the scapula frame)
  L1  curved link on the inner shell, arc alpha1 from J1 to J2
  J2  mid joint on the shell, axis c
  L2  curved link on the outer shell, arc alpha2 from J2 to the upper arm, then down the arm
  J3  ring bearing around the upper arm: axis = the humerus (takes axial rotation), travel +-RAIL about a neutral
Inverse kinematics is closed form (a spherical triangle b, c, h): two branches; one branch must serve the whole range
(switching means passing a singularity). A pose counts if, on the chosen branch, the arm direction keeps clear of both
singularities (J1 axis aligned with the arm; links straight or folded) by a margin, both links stay off the head,
neck, torso and the upper arm, and the ring stays within its travel. Same body, scapula rhythm and pose set as
design_search.py.

    python3 design_search_3r.py
"""
import json
import math
import os
import concurrent.futures as cf

import numpy as np
import design_search as D

SING = 12.0               # deg: keep the arm this far from J1's axis (gimbal lock) and from the straight/folded links


def evaluate(design):
    b = np.asarray(design["b"], float); a1, a2 = design["a1"] * D.D2R, design["a2"] * D.D2R
    h, x = D.HG, D.XG
    cb = np.clip(h @ b, -1, 1); beta = np.arccos(cb)                     # angle J1 axis -> arm
    lo, hi = abs(a1 - a2), min(a1 + a2, 2 * math.pi - a1 - a2)
    m = SING * D.D2R
    ok = (beta >= lo + m) & (beta <= hi - m) & (beta >= m) & (beta <= math.pi - m)
    # J2 direction c: angle a1 from b and a2 from h; two branches (sign)
    cosC = (math.cos(a2) - math.cos(a1) * cb) / (math.sin(a1) * np.sin(beta) + 1e-12)   # angle at b between arcs b->h and b->c
    C = np.arccos(np.clip(cosC, -1, 1))
    e = h - cb[:, None] * b; e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-12
    f = np.cross(b, e)
    out = {}
    for br in (+1, -1):
        dirc = np.cos(C)[:, None] * e + br * np.sin(C)[:, None] * f
        c = math.cos(a1) * b + math.sin(a1) * dirc
        # links: L1 b->c on the inner shell, L2 c->(arm keep-out boundary) on the outer shell
        pts1 = D.slerp_pts(np.broadcast_to(b, c.shape), c, 9)
        cut = (a2 - D.RHO_ARM * D.D2R) / a2
        stop = D.slerp_pts(c, h, 2)[:, 0] if False else None
        pts2 = D.slerp_pts(c, h, 9)[:, :max(2, int(9 * cut)), :]
        pts = np.concatenate([pts1, pts2], axis=1)
        okb = ok.copy()
        ang = np.degrees(np.arccos(np.clip(np.einsum("nmj,nj->nm", pts1, h), -1, 1)))
        okb &= ang.min(1) >= D.RHO_ARM                                     # L1 clear of the arm
        P = np.einsum("nij,nmj->nmi", D.RS, pts * D.R_SHELL)
        okb &= ~D.in_body(P).any(1)
        # ring angle: L2's orientation about the arm relative to the arm's anterior reference
        tc = c - (c * h).sum(1, keepdims=True) * h; tc /= np.linalg.norm(tc, axis=1, keepdims=True) + 1e-12
        x0 = x - (x * h).sum(1, keepdims=True) * h; x0 /= np.linalg.norm(x0, axis=1, keepdims=True)
        ring = np.degrees(np.arctan2((np.cross(x0, tc) * h).sum(1), (x0 * tc).sum(1)))
        best = (0, 0)
        for c0 in range(-180, 180, 10):
            d = (ring - c0 + 180) % 360 - 180
            cov = (okb & (np.abs(d) <= D.RAIL)).mean()
            if cov > best[0]: best = (float(cov), c0)
        out[br] = (best, float(okb.mean()))
    br = max(out, key=lambda k: out[k][0][0])
    return dict(design, cov=out[br][0][0], ring_neutral=out[br][0][1], branch=br, any_ring=out[br][1])


if __name__ == "__main__":
    designs = []
    for az in range(0, 360, 15):
        for el in range(-30, 91, 10):
            b = np.array([-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)])
            if not D.base_ok(b): continue
            for a1 in (60, 75, 90, 105):
                for a2 in (60, 75, 90, 105):
                    designs.append(dict(b=b.round(5).tolist(), az=az, el=el, a1=a1, a2=a2))
    print(f"{len(D.POSES)} poses, {len(designs)} serial designs", flush=True)
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        res = list(ex.map(evaluate, designs, chunksize=16))
    res.sort(key=lambda r: -r["cov"])
    for r in res[:12]:
        print(f"  cov {100 * r['cov']:5.1f}%  base az {r['az']:4d} el {r['el']:3d}  link arcs {r['a1']}/{r['a2']}  branch {r['branch']:+d}  ring neutral {r['ring_neutral']}  (any ring: {100 * r['any_ring']:.1f}%)")
    json.dump(res[:200], open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_search_3r.json"), "w"))
