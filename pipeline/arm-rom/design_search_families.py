"""Two further pivot-to-pivot shoulder families (same rules, body, scapula rhythm and poses as the other searches).

D. Redundant serial 4R:  J1 (scapula) -a1- J2 -a2- J3 -a3- J4 (upper-arm post, axis w in the humerus frame).
   One spare DOF: for each pose any J1 angle q1 that closes the chain (two branches for J3) may be used; a pose counts
   if some (q1, branch) keeps every triangle away from straight/folded by SING, J1 and J4 not aligned, and all three
   links off the body and the upper arm.
E. Spherical five-bar (parallel):  two pivots on the scapula (b1, b2) -p- elbows e1, e2 -d- output pin u0 = the
   upper-arm post (axis w in the humerus frame), BOTTOM on the post with a 180 deg range. Both drives sit on the
   scapula. Fixed assembly mode for the whole range. A pose counts if neither chain is straight/folded (type-I),
   the two distal links are not aligned at the output (type-II), the post is inside its window, and all four links
   stay off the body and the upper arm.

    python3 design_search_families.py D|E
"""
import json
import math
import os
import sys
import concurrent.futures as cf

import numpy as np
import design_search as D
D.POSES_HG_FULL, D.POSES_RS_FULL = D.HG, D.RS
from design_search_pivots import H_FRAMES, w_dir

SING = 12.0 * D.D2R
QS = np.radians(np.arange(0, 360, 15))


def set_stride(k, q_step=15):
    """Screening: evaluate on every k-th pose (and J1 sampled every q_step deg); stride 1 = the full pose set."""
    global H_FRAMES, QS
    import design_search_pivots as P
    H_FRAMES = P.H_FRAMES[::k]; QS = np.radians(np.arange(0, 360, q_step))
    D.HG = D.POSES_HG_FULL[::k]; D.RS = D.POSES_RS_FULL[::k]


def circ_int(c1, r1, c2, r2, sign):
    """Points at angular distance r1 from c1 and r2 from c2 (unit vectors, broadcast); sign picks the branch."""
    d = np.clip((c1 * c2).sum(-1), -1, 1)
    n = np.cross(c1, c2); s = np.linalg.norm(n, axis=-1, keepdims=True); n = n / (s + 1e-12)
    den = 1 - d ** 2 + 1e-12
    a = (math.cos(r1) - d * math.cos(r2)) / den; b = (math.cos(r2) - d * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2
    h2 = 1 - (p * p).sum(-1)
    ok = h2 > 0
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, ok


def off_body_and_arm(pts, h):
    ang = np.degrees(np.arccos(np.clip(np.einsum("...mj,...j->...m", pts, h), -1, 1)))
    ok = ang.min(-1) >= D.RHO_ARM
    P = np.einsum("nij,n...mj->n...mi", D.RS, pts * D.R_SHELL)
    return ok & ~D.in_body(P).any(-1)


def triangle_ok(x, y, a, b):
    """The links x->y (arc a) and y->z (arc b) are clear of straight/folded when angle(x,z) is inside the band."""
    t = np.arccos(np.clip((x * y).sum(-1), -1, 1))
    return (t >= abs(a - b) + SING) & (t <= min(a + b, 2 * math.pi - a - b) - SING)


def eval_D(design):
    b = np.asarray(design["b"], float); a1, a2, a3 = (design[k] * D.D2R for k in ("a1", "a2", "a3"))
    u4 = H_FRAMES @ w_dir(design["delta"], design["waz"]); h = D.HG; N = len(u4)
    # J2 on the circle of radius a1 around b, parameter q1
    e = np.cross(b, [0.0, 1.0, 0.0]); e = e / np.linalg.norm(e) if np.linalg.norm(e) > 1e-6 else np.array([1.0, 0, 0]); f = np.cross(b, e)
    c2 = math.cos(a1) * b + math.sin(a1) * (np.cos(QS)[:, None] * e + np.sin(QS)[:, None] * f)        # (Q, 3)
    C2 = np.broadcast_to(c2[None], (N, len(QS), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape)
    best = None
    for br in (+1, -1):
        c3, ok = circ_int(C2, a2, U4, a3, br)
        ok &= triangle_ok(C2, U4, a2, a3)
        bb = np.broadcast_to(b, C2.shape)
        ok &= np.abs((bb * U4).sum(-1)) <= math.cos(SING)                      # J1 and J4 not aligned
        ok &= triangle_ok(bb, c3, a1, a2)
        pts = np.concatenate([D.slerp_pts(bb, C2, 7), D.slerp_pts(C2, c3, 7), D.slerp_pts(c3, U4, 7)], axis=-2)
        ok &= off_body_and_arm(pts, np.broadcast_to(h[:, None], C2.shape))
        cov = float(ok.any(1).mean())
        if best is None or cov > best[0]: best = (cov, br)
    return dict(design, cov=best[0], branch=best[1])


def eval_E(design):
    b1, b2 = np.asarray(design["b1"], float), np.asarray(design["b2"], float); p, d = design["p"] * D.D2R, design["d"] * D.D2R
    u0 = H_FRAMES @ w_dir(design["delta"], design["waz"]); h = D.HG
    B1, B2 = np.broadcast_to(b1, u0.shape), np.broadcast_to(b2, u0.shape)
    best = None
    for s1 in (+1, -1):
        for s2 in (+1, -1):
            e1, k1 = circ_int(B1, p, u0, d, s1); e2, k2 = circ_int(B2, p, u0, d, s2)
            ok = k1 & k2 & triangle_ok(B1, u0, p, d) & triangle_ok(B2, u0, p, d)
            # type II: the distal links must not line up at the output pin
            t1 = e1 - (e1 * u0).sum(-1, keepdims=True) * u0; t2 = e2 - (e2 * u0).sum(-1, keepdims=True) * u0
            t1 /= np.linalg.norm(t1, axis=-1, keepdims=True) + 1e-12; t2 /= np.linalg.norm(t2, axis=-1, keepdims=True) + 1e-12
            cang = (t1 * t2).sum(-1)
            ok &= np.abs(cang) <= math.cos(SING * 1.5)
            pts = np.concatenate([D.slerp_pts(B1, e1, 7), D.slerp_pts(e1, u0, 7), D.slerp_pts(B2, e2, 7), D.slerp_pts(e2, u0, 7)], axis=-2)
            ok &= off_body_and_arm(pts, h)
            # post: BOTTOM's direction relative to the bisector of the distal links, about u0
            mid = t1 + t2; mid /= np.linalg.norm(mid, axis=-1, keepdims=True) + 1e-12
            th = h - (h * u0).sum(-1, keepdims=True) * u0; th /= np.linalg.norm(th, axis=-1, keepdims=True) + 1e-12
            post = np.degrees(np.arctan2((np.cross(mid, th) * u0).sum(-1), (mid * th).sum(-1)))
            for c in range(-180, 180, 15):
                dd = (post - c + 180) % 360 - 180
                cov = float((ok & (np.abs(dd) <= 90)).mean())
                if best is None or cov > best[0]: best = (cov, s1, s2, c)
    return dict(design, cov=best[0], modes=[best[1], best[2]], post_centre=best[3])


def base_dirs(step_az=30, els=(-15, 15, 45, 75)):
    out = []
    for az in range(0, 360, step_az):
        for el in els:
            b = np.array([-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)])
            if D.base_ok(b): out.append((az, el, b.round(5).tolist()))
    return out


if __name__ == "__main__":
    fam = sys.argv[1] if len(sys.argv) > 1 else "D"
    designs = []
    if fam == "D":
        for az, el, b in base_dirs(20, (-20, -5, 10, 25, 40, 55, 70, 85)):
            for a1 in (60, 90):
                for a2 in (60, 90):
                    for a3 in (60, 90):
                        for delta in (55, 70, 90):
                            for waz in range(-90, 181, 45):
                                designs.append(dict(b=b, az=az, el=el, a1=a1, a2=a2, a3=a3, delta=delta, waz=waz))
        fn = eval_D
    else:
        bs = base_dirs(30)
        for i, (az1, el1, b1) in enumerate(bs):
            for az2, el2, b2 in bs[i + 1:]:
                sep = math.degrees(math.acos(max(-1, min(1, np.dot(b1, b2)))))
                if not 25 <= sep <= 90: continue                     # both bases on the scapula plate
                for p_ in (50, 70, 90):
                    for d_ in (50, 70, 90):
                        for delta in (55, 70, 90):
                            for waz in range(-90, 181, 45):
                                designs.append(dict(b1=b1, b2=b2, az1=az1, el1=el1, az2=az2, el2=el2, p=p_, d=d_, delta=delta, waz=waz))
        fn = eval_E
    print(f"family {fam}: {len(designs)} designs", flush=True)
    # stage 1: screen every design on 1 pose in 6 (J1 every 30 deg); stage 2: full pose set on the best 40
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1), initializer=set_stride, initargs=(6, 30)) as ex:
        res = list(ex.map(fn, designs, chunksize=16))
    res.sort(key=lambda r: -r["cov"])
    print("screened; top screen %.1f%%" % (100 * res[0]["cov"]), flush=True)
    top = [{k: v for k, v in r.items() if k not in ("cov", "branch", "modes", "post_centre")} for r in res[:40]]
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1), initializer=set_stride, initargs=(1, 15)) as ex:
        res = list(ex.map(fn, top, chunksize=1))
    res.sort(key=lambda r: -r["cov"])
    for r in res[:10]:
        print("  cov %5.1f%%  " % (100 * r["cov"]) + "  ".join(f"{k} {v}" for k, v in r.items() if k not in ("b", "b1", "b2", "cov")))
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"design_search_{fam}.json"), "w"))
