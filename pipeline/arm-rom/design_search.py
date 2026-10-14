"""Search for a better low-profile shoulder morphology.

Architecture (keeps the current form factor: every link on the same ~124 mm sphere about the shoulder centre):
  scapula-mounted base pin (direction b, anywhere on the back or top of the shoulder)
  -> two-rhombus spherical scissor (link arc alpha; output pin at arc theta0 = 4 atan(tan(alpha) cos(phi)) from b)
  -> proximal upper-arm link P on the output pin (180 deg post range, pointing away from the scissor)
  -> rotating part on the upper arm: a ring bearing concentric with the humerus (travel +-RAIL about a neutral)
  -> distal upper-arm link with the elbow joint (rigid to the humerus)
The output pin sits at angle delta from the humerus axis. Because the ring takes the arm's axial rotation, the
mechanism is redundant: for an arm direction h the output pin can be anywhere on the circle of radius delta around
h (parameter t, which is also the ring angle). A pose is reachable if some t keeps: the scissor inside its fold and
stretch limits, the post within its range, every link off the head, neck, torso and the upper arm itself, and the ring
within its travel.
The base rides on the scapula (simple scapulohumeral rhythm), so the mechanism sees glenohumeral motion only.

    python3 design_search.py
"""
import json
import math
import os
import concurrent.futures as cf

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R_SHELL = 124.0
S = float(os.environ.get("H_LEN", 411.0)) / 310.0   # body scale used by the viewer (exo arm length / adult arm)
ARM_R = 46 * S                                     # upper-arm radius near the shoulder
LINK_HW = math.degrees(math.asin(7.0 / R_SHELL))   # half the link width (14 mm), as an angle
RHO_ARM = math.degrees(math.asin(min(0.99, (ARM_R + 4) / R_SHELL))) + LINK_HW
TH_MIN = 14.0                                      # fully folded (pin bosses meet), as on the current mechanism
PIN_SEP = 8.0                                      # side pins may not get closer than this when stretched
RAIL = 100.0                                       # ring-bearing travel, +- deg about its neutral
D2R = math.pi / 180


def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


Ry = lambda a: rot([0, 1, 0], a); Rx = lambda a: rot([1, 0, 0], a); Rz = lambda a: rot([0, 0, 1], a)


def human_ok(plane, elev, axial):
    if elev < 0 or elev > 180 or plane < -60 or plane > 140: return False
    if plane < 0 and elev > 120: return False
    lo, hi = (-80, 80) if elev < 30 else (-90, 70)
    return lo <= axial <= hi


def scapula(elev):
    """Scapula rotation in the thorax (anterior, up, right) frame: upward rotation and posterior tilt."""
    n = np.array([math.cos(30 * D2R), 0, -math.sin(30 * D2R)])     # normal of the scapular plane
    ur = 0.36 * max(0.0, elev - 20) * D2R
    return Rz(0.12 * elev * D2R) @ rot(n, -ur)


# body primitives in the thorax frame, origin at the right shoulder centre (mm), as in the viewer
TORSO = (np.array([-15, -215, -180]) * S, np.array([112, 250, 138]) * S)
HEAD = (np.array([5, 300, -180]) * S, np.array([102, 122, 88]) * S)
NECK = (np.array([-20, 40, -180]) * S, np.array([-10, 175, -180]) * S, 55 * S)


def in_body(P):
    """P: (..., 3) points in the thorax frame -> bool, with a 5 mm margin."""
    def ell(c, r):
        d = (P - c) / (r + 5); return (d ** 2).sum(-1) < 1
    a, b, rr = NECK; ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
    neck = np.linalg.norm(P - (a + t[..., None] * ab), axis=-1) < rr + 5
    return ell(*TORSO) | ell(*HEAD) | neck


def poses():
    out = []
    for plane in range(-60, 141, 10):
        for elev in range(0, 181, 10):
            for axial in range(-90, 81, 15):
                if human_ok(plane, elev, axial):
                    H = Ry(plane * D2R) @ Rx(-elev * D2R) @ Ry(axial * D2R)
                    Rs = scapula(elev)
                    out.append((plane, elev, axial, Rs.T @ H, Rs))
    return out


POSES = poses()
HG = np.array([p[3] @ np.array([0, -1, 0.]) for p in POSES])            # arm direction, scapula frame
XG = np.array([p[3] @ np.array([1, 0, 0.]) for p in POSES])             # arm's anterior reference
RS = np.array([p[4] for p in POSES])
TS = np.radians(np.arange(0, 360, 15))


def slerp_pts(a, b, n):
    """n points along the great-circle arc a->b (unit vectors, broadcast over leading dims)."""
    cosw = np.clip((a * b).sum(-1, keepdims=True), -1, 1); w = np.arccos(cosw); s = np.sin(w) + 1e-9
    ts = np.linspace(0, 1, n)
    return np.stack([(np.sin((1 - u) * w) * a + np.sin(u * w) * b) / s for u in ts], axis=-2)


def scissor(b, u0, alpha):
    """Pins and sampled links of the two-rhombus scissor from b to u0 (broadcast). Returns points (..., M, 3) and ok."""
    cth = np.clip((b * u0).sum(-1), -1, 1); th = np.arccos(cth)
    tan_q = np.tan(th / 4) / math.tan(alpha)
    ok = np.abs(tan_q) <= 1
    phi = np.arccos(np.clip(tan_q, -1, 1))
    w = np.arcsin(np.clip(math.sin(alpha) * np.sin(phi), -1, 1))
    # centreline frame
    t1 = u0 - cth[..., None] * b; t1 /= np.linalg.norm(t1, axis=-1, keepdims=True) + 1e-12
    side = np.cross(b, t1)
    along = lambda s: np.cos(s)[..., None] * b + np.sin(s)[..., None] * t1
    def off(c, ww, sgn):
        sd = np.cross(c, side); sd = np.cross(sd, c)           # 'side' made tangent at c
        sd /= np.linalg.norm(sd, axis=-1, keepdims=True) + 1e-12
        return np.cos(ww)[..., None] * c + sgn * np.sin(ww)[..., None] * sd
    c1, c2, d1 = along(th / 4), along(3 * th / 4), along(th / 2)
    B1, C1, B2, C2 = off(c1, w, 1), off(c1, w, -1), off(c2, w, 1), off(c2, w, -1)
    links = [(b, B1), (b, C1), (B1, d1), (d1, C2), (C1, d1), (d1, B2), (B2, u0), (C2, u0)]
    pts = np.concatenate([slerp_pts(a, c, 4) for a, c in links], axis=-2)
    sep = 2 * w
    stretch_ok = np.degrees(sep) >= PIN_SEP
    fold_ok = np.degrees(th) >= TH_MIN
    return pts, ok & stretch_ok & fold_ok


def evaluate(design):
    """Fraction of natural shoulder poses reachable for one design (and the best ring neutral)."""
    b, alpha, delta = np.asarray(design["b"], float), design["alpha"] * D2R, design["delta"] * D2R
    h = HG[:, None, :]; e1 = XG - (XG * HG).sum(-1, keepdims=True) * HG; e1 /= np.linalg.norm(e1, axis=-1, keepdims=True)
    e2 = np.cross(HG, e1)
    ct, st = np.cos(TS)[None, :, None], np.sin(TS)[None, :, None]
    u0 = math.cos(delta) * h + math.sin(delta) * (ct * e1[:, None, :] + st * e2[:, None, :])     # (N, T, 3)
    B = np.broadcast_to(b, u0.shape)
    pts, ok = scissor(B, u0, alpha)
    # post: the upper-arm link points away from the scissor (angle at u0 between b and h >= 90 deg)
    tb = B - (B * u0).sum(-1, keepdims=True) * u0; th_ = h - (h * u0).sum(-1, keepdims=True) * u0
    ok &= (tb * th_).sum(-1) <= 0
    # links clear of the upper arm
    ang = np.degrees(np.arccos(np.clip((pts * h[:, :, None, :]).sum(-1), -1, 1)))
    ok &= ang.min(-1) >= RHO_ARM
    # links clear of the body (points in the thorax frame)
    P = np.einsum("nij,ntmj->ntmi", RS, pts * R_SHELL)
    ok &= ~in_body(P).any(-1)
    # ring travel: best neutral
    best = (0, 0)
    for c in range(0, 360, 15):
        d = (np.degrees(TS) - c + 180) % 360 - 180
        cov = (ok & (np.abs(d) <= RAIL)[None, :]).any(1).mean()
        if cov > best[0]: best = (float(cov), c)
    return dict(design, cov=best[0], ring_neutral=best[1], any_ring=float(ok.any(1).mean()))


def base_ok(b):
    p = b * R_SHELL
    return (b[0] <= 0.25) and (b[1] >= -0.35) and not in_body(p[None])[0]     # on the back or top, outside the body


if __name__ == "__main__":
    print(f"{len(POSES)} natural shoulder poses; arm keep-out {RHO_ARM:.1f} deg on the shell; ring +-{RAIL:.0f} deg", flush=True)
    designs = []
    for az in range(0, 360, 15):
        for el in range(-30, 91, 10):
            # b in the thorax/scapula frame (anterior, up, right): az measured from posterior toward lateral
            b = np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
            if not base_ok(b): continue
            for alpha in (35, 39, 43):
                for delta in (40, 55, 70, 85):
                    designs.append(dict(b=b.round(5).tolist(), az=az, el=el, alpha=alpha, delta=delta))
    print(f"{len(designs)} candidate designs", flush=True)
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        res = list(ex.map(evaluate, designs, chunksize=8))
    res.sort(key=lambda r: -r["cov"])
    for r in res[:12]:
        print(f"  cov {100 * r['cov']:5.1f}%  base az {r['az']:4d} el {r['el']:3d}  alpha {r['alpha']}  delta {r['delta']}  ring neutral {r['ring_neutral']}  (any ring angle: {100 * r['any_ring']:.1f}%)")
    json.dump(res[:200], open(os.path.join(HERE, "design_search.json"), "w"))
