"""Family V: J1 (scapula pivot, axis b) -a1- J2 (axis c) -a2- virtual axial joint about the humerus axis h, realised by a
ring-free spherical remote-centre linkage (pivots only) on the cuff. Same rules as the routed searches: real skin,
links routed in their own frames, pins at free radii; the virtual joint has +-TRAVEL deg and its linkage is checked
as a sector beside the arm (it does not turn with the pointing links, only with axial rotation)."""
import math, os, sys, json, random
import numpy as np
import design_search as D
import design_search_families as F
import design_search_anat as A
import design_search_routed as R

TRAVEL = float(os.environ.get("TRAVEL", 110))


def evaluate(d, full=False):
    hf, h = A.HF_ALL[R.SUB], A.HG_ALL[R.SUB]
    b = np.broadcast_to(np.asarray(d["b"], float), h.shape); a1, a2 = d["a1"] * D.D2R, d["a2"] * D.D2R
    c, ok = F.circ_int(b, a1, h, a2, d["branch"])
    ok &= F.triangle_ok(b, h, a1, a2) & (np.abs((b * h).sum(-1)) <= math.cos(A.SING))
    xa = hf @ np.array([1.0, 0, 0]); phi = A.about(c, xa, h)          # virtual-joint angle: arm twist vs link 2
    best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((phi - cc + 180) % 360 - 180) <= TRAVEL)).sum()
        if k > best[0]: best = (k, cc)
    alive = ok & (np.abs((phi - best[1] + 180) % 360 - 180) <= TRAVEL); kin = alive.mean()
    if full is None or kin < 0.6: return dict(d, cov=0.0, kin=float(kin))
    e3 = np.cross(h, c); e3 /= np.linalg.norm(e3, axis=1, keepdims=True) + 1e-12
    cperp = c - (c * h).sum(-1, keepdims=True) * h; cperp /= np.linalg.norm(cperp, axis=1, keepdims=True) + 1e-12
    dirn = lambda beta, gam: math.cos(beta) * h + math.sin(beta) * (math.cos(gam) * cperp + math.sin(gam) * e3)
    beta, gam = d["beta"] * D.D2R, d["gam"] * D.D2R
    q = dirn(beta, gam)                                                # where link 2 meets the remote-centre linkage
    pins = dict(b=b, c=c, q=q)
    alive2, det = R.route_design(pins, [("b", "c"), ("c", "q")], "q", alive.copy(), full)
    if det is None: return dict(d, cov=0.0, kin=float(kin))
    R2 = R.frame(c, q); i0 = int(np.argmax(alive2)) if alive2.any() else 0
    Bq = R.blocked(R2, q * det["radius"]["q"], True)
    for k in (np.linspace(-45, 45, 7) if not os.environ.get('NO_SECTOR') else []):   # the linkage's sector beside the arm
        p_ = dirn(beta, gam + k * D.D2R)[i0] * det["radius"]["q"]
        alive2 &= ~Bq[:, R.nearest_voxel(R.local(R2[i0], p_))]
    return dict(d, cov=float(alive2.mean()), kin=float(kin), axial_centre=best[1], **det)


def bvec(az, el):
    return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
