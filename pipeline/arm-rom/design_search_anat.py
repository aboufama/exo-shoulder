"""Morphology searches re-run against the anatomical body (anatomy.js skin, sampled by make_skin_grids.mjs) instead of
the ellipsoid torso / neck / head and the upper-arm keep-out cone.

Same rules as before otherwise: base pivot(s) fixed on the scapula (same rhythm), pivots only, upper-arm post limited
to 180 deg (centre optimised), singularity margins, one assembly branch / mode for the whole range, 3,993 poses.
Clearance: every link sample (at the inner face of its shell, R - 5 mm) keeps >= CLEAR mm from the skin of the trunk,
neck, head and shoulder girdle (grid per arm elevation, since the scapula moves) and from the skin of the upper arm
(grid in the humerus frame), except within 15 deg of the post, which is where the rigid upper-arm link meets the arm;
the post bearing itself must clear the arm skin by 6 mm. The shell radius R is searched too (current design: 124 mm).

    python3 design_search_anat.py B|C|D|E
"""
import json
import math
import os
import sys
import concurrent.futures as cf

import numpy as np
from scipy.ndimage import map_coordinates
import design_search as D
import design_search_families as F
from design_search_pivots import w_dir

HERE = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(os.path.join(HERE, "skin_grids.json")))
NG, HG_, STEP = META["N"], META["H"], META["STEP"]
GRIDS = np.fromfile(os.path.join(HERE, "skin_grids.bin"), dtype=np.float32).reshape(-1, NG, NG, NG)
TRUNK, ARM = GRIDS[:-1], GRIDS[-1]
ELEVS = np.array(META["elevs"])
CLEAR, POST_CLEAR, POST_EXCL = float(os.environ.get("CLEAR", 9.0)), 6.0, 15.0
RADII = (124, 136, 148)
SING = F.SING

POSES = D.POSES
EBIN_ALL = np.array([int(np.argmin(np.abs(ELEVS - p[1]))) for p in POSES])
HF_ALL = np.array([p[3] for p in POSES])                   # humerus in the scapula frame
RS_ALL = np.array([p[4] for p in POSES])
HG_ALL = D.HG
SUB = slice(None)


def set_stride(k, q_step=15):
    global SUB, QS
    SUB = slice(None, None, k); QS = np.radians(np.arange(0, 360, q_step))


QS = np.radians(np.arange(0, 360, 15))


def lookup(grid, P):
    c = ((P + HG_) / STEP).reshape(-1, 3).T
    return map_coordinates(grid, c, order=1, mode="constant", cval=100.0).reshape(P.shape[:-1])


def skin_clear(pts, R, post, post_check=True):
    """pts (N, ..., M, 3) unit vectors in the scapula frame; post (N, ..., 3). Returns bool (N, ...)."""
    hf, rs, eb = HF_ALL[SUB], RS_ALL[SUB], EBIN_ALL[SUB]
    N = pts.shape[0]; shp = pts.shape[1:-1]
    P = pts.reshape(N, -1, 3) * (R - 5.0)
    Pt = np.einsum("nij,nmj->nmi", rs, P)                    # thorax frame
    Ph = np.einsum("nji,nmj->nmi", hf, P)                    # humerus frame
    dt = np.empty(Pt.shape[:2])
    for b in np.unique(eb):
        sel = eb == b; dt[sel] = lookup(TRUNK[b], Pt[sel])
    da = lookup(ARM, Ph)
    near = np.degrees(np.arccos(np.clip(np.einsum("nmj,nmj->nm", pts.reshape(N, -1, 3),
                                                  np.broadcast_to(post[..., None, :], pts.shape).reshape(N, -1, 3)), -1, 1))) < POST_EXCL
    ok = (dt >= CLEAR) & ((da >= CLEAR) | near)
    ok = ok.reshape((N,) + shp).all(-1)
    if not post_check: return ok
    pp = post.reshape(N, -1, 3) * R
    dpa = lookup(ARM, np.einsum("nji,nmj->nmi", hf, pp)).reshape(post.shape[:-1])
    return ok & (dpa >= POST_CLEAR)


BACK_MAX = float(os.environ.get("BACK_MAX", 0)) or None       # mm: max standoff of the exo's outer surface over the back
BACK_FACING = 0.5                                              # skin counts as "back" where its outward normal has n_x < -0.5


def back_ok(pts, r_face, top_off):
    """pts (N, ..., M, 3) unit vectors (scapula frame) of a member whose skin-side face is at r_face and whose outer
    surface is top_off mm above it. Where the trunk skin below faces backwards, the outer surface must stay within
    BACK_MAX of the skin. Returns bool (N, ...)."""
    if BACK_MAX is None: return np.ones(pts.shape[:-2], bool)
    rs, eb = RS_ALL[SUB], EBIN_ALL[SUB]
    N = pts.shape[0]; shp = pts.shape[1:-1]
    Pt = np.einsum("nij,nmj->nmi", rs, pts.reshape(N, -1, 3) * r_face)
    dt = np.empty(Pt.shape[:2]); gx = np.empty(Pt.shape[:2]); gn = np.zeros(Pt.shape[:2])
    for b in np.unique(eb):
        sel = eb == b; Q = Pt[sel]; dt[sel] = lookup(TRUNK[b], Q); g = []
        for k in range(3):
            e = np.zeros(3); e[k] = 3.0; g.append((lookup(TRUNK[b], Q + e) - lookup(TRUNK[b], Q - e)) / 6.0)
        gx[sel] = g[0]; gn[sel] = np.sqrt(g[0] ** 2 + g[1] ** 2 + g[2] ** 2) + 1e-9
    back = (gx / gn < -BACK_FACING) & (dt < 40.0)
    ok = ~back | (dt + top_off <= BACK_MAX)
    return ok.reshape((N,) + shp).all(-1)


POST_HALF = float(os.environ.get("POST_HALF", 90))


def post_window(post, ok):
    best = (0.0, 0)
    for c in range(-180, 180, 10):
        cov = float((ok & (np.abs((post - c + 180) % 360 - 180) <= POST_HALF)).mean())
        if cov > best[0]: best = (cov, c)
    return best


def about(frm, to, u):
    a = frm - (frm * u).sum(-1, keepdims=True) * u; a /= np.linalg.norm(a, axis=-1, keepdims=True) + 1e-12
    b = to - (to * u).sum(-1, keepdims=True) * u; b /= np.linalg.norm(b, axis=-1, keepdims=True) + 1e-12
    return np.degrees(np.arctan2((np.cross(a, b) * u).sum(-1), (a * b).sum(-1)))


def eval_B(d):
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b = np.asarray(d["b"], float); u0 = hf @ w_dir(d["delta"], d["waz"]); B = np.broadcast_to(b, u0.shape)
    pts, ok = D.scissor(B, u0, d["alpha"] * D.D2R)
    ok &= skin_clear(pts, d["R"], u0)
    cov, c = post_window(about(B, h, u0), ok)
    return dict(d, cov=cov, post_centre=c)


def eval_C(d):
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b = np.asarray(d["b"], float); u = hf @ w_dir(d["delta"], d["waz"]); B = np.broadcast_to(b, u.shape)
    a1, a2 = d["a1"] * D.D2R, d["a2"] * D.D2R
    c, ok = F.circ_int(B, a1, u, a2, d["branch"])
    ok &= F.triangle_ok(B, u, a1, a2) & (np.abs((B * u).sum(-1)) <= math.cos(SING))
    pts = np.concatenate([D.slerp_pts(B, c, 7), D.slerp_pts(c, u, 7)], axis=-2)
    ok &= skin_clear(pts, d["R"], u)
    cov, cc = post_window(about(c, h, u), ok)
    return dict(d, cov=cov, post_centre=cc)


def eval_D(d):
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b = np.asarray(d["b"], float); a1, a2, a3 = (d[k] * D.D2R for k in ("a1", "a2", "a3"))
    u4 = hf @ w_dir(d["delta"], d["waz"]); N = len(u4)
    e = np.cross(b, [0.0, 1.0, 0.0]); e /= np.linalg.norm(e); f = np.cross(b, e)
    c2 = math.cos(a1) * b + math.sin(a1) * (np.cos(QS)[:, None] * e + np.sin(QS)[:, None] * f)
    C2 = np.broadcast_to(c2[None], (N, len(QS), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape); bb = np.broadcast_to(b, C2.shape)
    H = np.broadcast_to(h[:, None], C2.shape)
    best = None
    for br in (+1, -1):
        c3, ok = F.circ_int(C2, a2, U4, a3, br)
        ok &= F.triangle_ok(C2, U4, a2, a3) & F.triangle_ok(bb, c3, a1, a2) & (np.abs((bb * U4).sum(-1)) <= math.cos(SING))
        pts = np.concatenate([D.slerp_pts(bb, C2, 7), D.slerp_pts(C2, c3, 7), D.slerp_pts(c3, U4, 7)], axis=-2)
        ok &= skin_clear(pts, d["R"], U4)
        post = about(c3, H, U4)
        for cp in range(-180, 180, 20):
            cov = float((ok & (np.abs((post - cp + 180) % 360 - 180) <= POST_HALF)).any(1).mean())
            if best is None or cov > best[0]: best = (cov, br, cp)
    return dict(d, cov=best[0], branch=best[1], post_centre=best[2])


def eval_E(d):
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b1, b2 = np.asarray(d["b1"], float), np.asarray(d["b2"], float); p, dd = d["p"] * D.D2R, d["d"] * D.D2R
    u = hf @ w_dir(d["delta"], d["waz"]); B1, B2 = np.broadcast_to(b1, u.shape), np.broadcast_to(b2, u.shape)
    best = None
    for s1 in (+1, -1):
        for s2 in (+1, -1):
            e1, k1 = F.circ_int(B1, p, u, dd, s1); e2, k2 = F.circ_int(B2, p, u, dd, s2)
            ok = k1 & k2 & F.triangle_ok(B1, u, p, dd) & F.triangle_ok(B2, u, p, dd)
            t1 = e1 - (e1 * u).sum(-1, keepdims=True) * u; t2 = e2 - (e2 * u).sum(-1, keepdims=True) * u
            t1 /= np.linalg.norm(t1, axis=-1, keepdims=True) + 1e-12; t2 /= np.linalg.norm(t2, axis=-1, keepdims=True) + 1e-12
            ok &= np.abs((t1 * t2).sum(-1)) <= math.cos(SING * 1.5)
            if not ok.any(): continue
            pts = np.concatenate([D.slerp_pts(B1, e1, 7), D.slerp_pts(e1, u, 7), D.slerp_pts(B2, e2, 7), D.slerp_pts(e2, u, 7)], axis=-2)
            ok &= skin_clear(pts, d["R"], u)
            cov, c = post_window(about(t1 + t2, h, u), ok)
            if best is None or cov > best[0]: best = (cov, s1, s2, c)
    if best is None: best = (0.0, 1, 1, 0)
    return dict(d, cov=best[0], modes=[best[1], best[2]], post_centre=best[3])


def bases(step_az=20, els=range(-20, 91, 15)):
    out = []
    for az in range(0, 360, step_az):
        for el in els:
            b = np.array([-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)])
            if D.base_ok(b): out.append((az, el, b.round(5).tolist()))
    return out


def designs_for(fam):
    out = []
    for R in RADII:
        if fam == "B":
            for az, el, b in bases(30):
                for alpha in (35, 39):
                    for delta in (55, 70, 90):
                        for waz in range(-90, 181, 45):
                            out.append(dict(R=R, b=b, az=az, el=el, alpha=alpha, delta=delta, waz=waz))
        elif fam == "C":
            for az, el, b in bases(30):
                for a1 in (60, 75, 90):
                    for a2 in (60, 75, 90):
                        for delta in (40, 55, 70):
                            for waz in range(-90, 181, 45):
                                for br in (1, -1):
                                    out.append(dict(R=R, b=b, az=az, el=el, a1=a1, a2=a2, delta=delta, waz=waz, branch=br))
        elif fam == "D":
            for az, el, b in bases(40, (55, 70, 85)):                 # narrowed to the region the ellipsoid search favoured
                for a1 in (60, 75):
                    for a2 in (75, 90):
                        for a3 in (75, 90):
                            for delta in (40, 55):
                                for waz in (-45, 0, 45):
                                    out.append(dict(R=R, b=b, az=az, el=el, a1=a1, a2=a2, a3=a3, delta=delta, waz=waz))
        else:
            bs = bases(45, (15, 45, 75))
            for i, (az1, el1, b1) in enumerate(bs):
                for az2, el2, b2 in bs[i + 1:]:
                    sep = math.degrees(math.acos(max(-1, min(1, np.dot(b1, b2)))))
                    if not 25 <= sep <= 90: continue
                    for p_ in (70, 90):
                        for d_ in (70, 90):
                            for delta in (40, 55):
                                for waz in (-45, 0, 45):
                                    out.append(dict(R=R, b1=b1, b2=b2, az1=az1, el1=el1, az2=az2, el2=el2, p=p_, d=d_, delta=delta, waz=waz))
    return out


if __name__ == "__main__":
    fam = sys.argv[1]
    fn = dict(B=eval_B, C=eval_C, D=eval_D, E=eval_E)[fam]
    designs = designs_for(fam)
    print(f"family {fam}: {len(designs)} designs (radii {RADII})", flush=True)
    with cf.ProcessPoolExecutor(max_workers=int(os.environ.get('WORKERS', 4)), initializer=set_stride, initargs=(6, 30)) as ex:
        res = list(ex.map(fn, designs, chunksize=16))
    keep = []
    for R in RADII:                                          # best 8 per radius go to the full pose set
        rr = sorted((r for r in res if r["R"] == R), key=lambda r: -r["cov"])[:8]
        print(f"  R {R}: screened best {100 * rr[0]['cov']:.1f}%", flush=True)
        keep += [{k: v for k, v in r.items() if k not in ("cov", "branch", "modes", "post_centre")} | ({"branch": r["branch"]} if fam == "C" else {}) for r in rr]
    with cf.ProcessPoolExecutor(max_workers=int(os.environ.get('WORKERS', 4)), initializer=set_stride, initargs=(1, 15)) as ex:
        full = list(ex.map(fn, keep, chunksize=1))
    full.sort(key=lambda r: (r["R"], -r["cov"]))
    for R in RADII:
        for r in [x for x in full if x["R"] == R][:3]:
            print("  R %d  cov %5.1f%%  " % (R, 100 * r["cov"]) + "  ".join(f"{k} {v}" for k, v in r.items() if k not in ("b", "b1", "b2", "cov", "R")), flush=True)
    json.dump(full, open(os.path.join(HERE, f"design_search_anat_{fam}" + ("" if CLEAR == 9.0 else f"_clear{int(CLEAR)}") + ("" if POST_HALF == 90 else f"_post{int(POST_HALF)}") + ".json"), "w"))


def eval_Dm(d):
    """4-pivot chain with a separate shell radius per link (d['Rs'] = [r1, r2, r3]; the post sits at r3)."""
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b = np.asarray(d["b"], float); a1, a2, a3 = (d[k] * D.D2R for k in ("a1", "a2", "a3"))
    u4 = hf @ w_dir(d["delta"], d["waz"]); N = len(u4)
    e = np.cross(b, [0.0, 1.0, 0.0]); e /= np.linalg.norm(e); f = np.cross(b, e)
    c2 = math.cos(a1) * b + math.sin(a1) * (np.cos(QS)[:, None] * e + np.sin(QS)[:, None] * f)
    C2 = np.broadcast_to(c2[None], (N, len(QS), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape); bb = np.broadcast_to(b, C2.shape)
    H = np.broadcast_to(h[:, None], C2.shape); r1, r2, r3 = d["Rs"]; best = None
    for br in (+1, -1):
        c3, ok = F.circ_int(C2, a2, U4, a3, br)
        ok &= F.triangle_ok(C2, U4, a2, a3) & F.triangle_ok(bb, c3, a1, a2) & (np.abs((bb * U4).sum(-1)) <= math.cos(SING))
        ok &= skin_clear(D.slerp_pts(bb, C2, 7), r1, U4) & skin_clear(D.slerp_pts(C2, c3, 7), r2, U4) & skin_clear(D.slerp_pts(c3, U4, 7), r3, U4)
        post = about(c3, H, U4)
        for cp in range(-180, 180, 20):
            cov = float((ok & (np.abs((post - cp + 180) % 360 - 180) <= POST_HALF)).any(1).mean())
            if best is None or cov > best[0]: best = (cov, br, cp)
    return dict(d, cov=best[0], branch=best[1], post_centre=best[2])


# ---------------------------------------------------------------- true hardware footprint (for the detailed design)
FP_W, FP_HUB = float(os.environ.get("FP_W", 20.0)), float(os.environ.get("FP_HUB", 44.0))
FP_RIN = float(os.environ.get("FP_RIN", 119.0)); FP_ROUT = float(os.environ.get("FP_ROUT", 126.5))
T_IN_TOP, T_OUT_TOP, J_TOP = (float(os.environ.get(k, v)) for k, v in (("T_IN_TOP", 5.0), ("T_OUT_TOP", 5.45), ("J_TOP", 14.2)))


def _widen(A_, B_, n_pts, r):
    """points across a link's width: centreline + both edges of a w-wide strip on the A->B great circle"""
    c = D.slerp_pts(A_, B_, n_pts)
    nrm = np.cross(A_, B_); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-12
    off = (FP_W / 2) / r; outs = [c]
    for sg in (-1, 1):
        q = c + sg * off * nrm[..., None, :]; outs.append(q / np.linalg.norm(q, axis=-1, keepdims=True))
    return np.concatenate(outs, axis=-2)


def _hub(P_, r, n=10):
    """points on the rim of a hub disc around pin direction P_ (angular radius = hub radius / r)"""
    t = np.cross(P_, [0.0, 0.0, 1.0]); t /= np.linalg.norm(t, axis=-1, keepdims=True) + 1e-12; s = np.cross(P_, t)
    a = (FP_HUB / 2) / r; out = [P_[..., None, :] * 1.0]
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    rim = math.cos(a) * P_[..., None, :] + math.sin(a) * (np.cos(ang)[:, None] * t[..., None, :] + np.sin(ang)[:, None] * s[..., None, :])
    return np.concatenate(out + [rim], axis=-2)


DROPIN = os.environ.get("DROPIN") == "1"                      # J4 = the post of the user's BOTTOM link (axis // elbow axis)
BAR_D = float(os.environ.get("BAR_D", 102.0)); BAR_T = 6.5; BAR_HW = 15.0


def bar_clear(pts, U4, r_in, r_out, skip_hub=None):
    """pts (N, Q, M, 3) unit dirs of a link on the shell r_in..r_out; U4 (N, Q, 3) the J4 axis = BOTTOM's post axis.
    BOTTOM is a flat bar (planes BAR_D..BAR_D+BAR_T from the centre, half width BAR_HW) running from the post along the
    humerus projected into its plane. A link point collides if its ray meets the bar's slab inside the shell and lies
    over the bar's footprint (from the post boss toward the elbow). Points within skip_hub (mm) of J4 are the joint stack."""
    hf = HF_ALL[SUB]; N = pts.shape[0]
    h = np.einsum("nij,j->ni", hf, np.array([0.0, -1.0, 0.0]))[:, None, None, :]           # arm direction, scapula frame
    W = U4[..., None, :]
    db = h - (h * W).sum(-1, keepdims=True) * W; db /= np.linalg.norm(db, axis=-1, keepdims=True) + 1e-12
    side = np.cross(W, db)
    c = (pts * W).sum(-1); c = np.where(c > 1e-3, c, 1e-3)
    t0, t1 = BAR_D / c, (BAR_D + BAR_T) / c                                                   # ray distances to the slab
    radial = (t0 < r_out) & (t1 > r_in)
    q = pts * (BAR_D / c)[..., None]; s = (q * db).sum(-1); y = (q * side).sum(-1)
    over = (np.abs(y) < BAR_HW + 1.0) & (s > -BAR_HW - 1.0)
    if skip_hub is not None: over &= np.hypot(s, y) > skip_hub
    return ~(radial & over).any(-1)


def eval_D_fp(d):
    """family D with the real link widths and hub discs; inner members (base, link 2, bar) at FP_RIN, outer links
    (1, 3) at FP_ROUT (inner faces). Same kinematic / post / singularity rules as eval_D."""
    hf, h = HF_ALL[SUB], HG_ALL[SUB]
    b = np.asarray(d["b"], float); a1, a2, a3 = (d[k] * D.D2R for k in ("a1", "a2", "a3"))
    u4 = hf @ w_dir(d["delta"], d["waz"]); N = len(u4)
    e = np.cross(b, [0.0, 1.0, 0.0]); e /= np.linalg.norm(e); f = np.cross(b, e)
    c2 = math.cos(a1) * b + math.sin(a1) * (np.cos(QS)[:, None] * e + np.sin(QS)[:, None] * f)
    C2 = np.broadcast_to(c2[None], (N, len(QS), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape); bb = np.broadcast_to(b, C2.shape)
    H = np.broadcast_to(h[:, None], C2.shape); best = None
    for br in (+1, -1):
        c3, ok = F.circ_int(C2, a2, U4, a3, br)
        ok &= F.triangle_ok(C2, U4, a2, a3) & F.triangle_ok(bb, c3, a1, a2) & (np.abs((bb * U4).sum(-1)) <= math.cos(SING))
        if not ok.any(): continue
        ok &= skin_clear(_widen(bb, C2, 7, FP_ROUT), FP_ROUT + 5, U4, False)              # link 1 (outer)
        ok &= skin_clear(_widen(C2, c3, 7, FP_RIN), FP_RIN + 5, U4)                       # link 2 (inner)
        ok &= skin_clear(_widen(c3, U4, 7, FP_ROUT), FP_ROUT + 5, U4, False)              # link 3 (outer)
        hubs = np.concatenate([_hub(C2, FP_RIN), _hub(c3, FP_RIN), _hub(U4, FP_RIN), _hub(bb, FP_RIN)], axis=-2)
        ok &= skin_clear(hubs, FP_RIN + 5, U4)                                              # every pivot has an inner member
        if DROPIN:                                                                          # links clear of BOTTOM
            ok &= bar_clear(_widen(c3, U4, 9, FP_ROUT), U4, FP_ROUT, FP_ROUT + T_OUT_TOP, skip_hub=FP_HUB / 2 + 1.0)
            ok &= bar_clear(_widen(C2, c3, 9, FP_RIN), U4, FP_RIN, FP_RIN + T_IN_TOP)
            ok &= bar_clear(np.concatenate([_hub(C2, FP_RIN), _hub(c3, FP_RIN)], axis=-2), U4, FP_RIN, FP_RIN + J_TOP)
        if BACK_MAX is not None:                                                            # low profile over the back
            ok &= back_ok(_widen(bb, C2, 7, FP_ROUT), FP_ROUT, T_OUT_TOP) & back_ok(_widen(c3, U4, 7, FP_ROUT), FP_ROUT, T_OUT_TOP)
            ok &= back_ok(_widen(C2, c3, 7, FP_RIN), FP_RIN, T_IN_TOP) & back_ok(hubs, FP_RIN, J_TOP)
        post = about(c3, H, U4)
        for cp in range(-180, 180, 20):
            cov = float((ok & (np.abs((post - cp + 180) % 360 - 180) <= POST_HALF)).any(1).mean())
            if best is None or cov > best[0]: best = (cov, br, cp)
    if best is None: best = (0.0, 1, 0)
    return dict(d, cov=best[0], branch=best[1], post_centre=best[2])
