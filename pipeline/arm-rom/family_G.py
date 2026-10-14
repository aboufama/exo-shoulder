"""Family G: two scapula pivots point the arm; a VIRTUAL axial joint (spherical remote-centre linkage, pivots only)
turns the cuff about the humerus axis itself.

  J1 axis b (scapula), J2 axis c = s * (b x h)/|b x h|  (perpendicular to the base axis and the arm),
  J3 = virtual axis h (the humerus), realised by a spherical double-parallelogram whose pivots sit beside the arm.
Kinematic rules: |h . b| <= cos 12 deg (the one unavoidable gimbal pole), axial-joint travel <= +-TRAVEL about a
centre. Links: L1 (b..c) in its frame, L2 (c..RCM base) in the arm-pointing frame (h, c) - it does NOT turn with
axial rotation. The RCM linkage is checked as a sector beside the arm in that frame.
"""
import math, os, sys, json
import numpy as np
import design_search as D
import design_search_anat as A
import design_search_routed as R

TRAVEL = float(os.environ.get("TRAVEL", 90))


def kin(d):
    hf, h, x = A.HF_ALL[R.SUB], A.HG_ALL[R.SUB], A.XG[R.SUB] if hasattr(A, "XG") else None
    b = np.asarray(d["b"], float)
    c = np.cross(b, h); n = np.linalg.norm(c, axis=1); c = d["s"] * c / (n[:, None] + 1e-12)
    ok = np.abs(h @ b) <= math.cos(A.SING)
    # axial-joint angle: the arm's anterior axis vs c, about h
    xa = hf @ np.array([1.0, 0, 0])
    phi = A.about(c, xa, h)
    best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((phi - cc + 180) % 360 - 180) <= TRAVEL)).sum()
        if k > best[0]: best = (k, cc)
    alive = ok & (np.abs((phi - best[1] + 180) % 360 - 180) <= TRAVEL)
    return alive, c, h, best[1]


def evaluate(d, full=False):
    alive, c, h, pc = kin(d); kn = alive.mean()
    if full is None: return dict(d, kin=float(kn))
    b = np.broadcast_to(np.asarray(d["b"], float), c.shape)
    # RCM base direction in the arm-pointing frame: beta off the arm axis, azimuth gam from c
    e3 = np.cross(h, c)
    def dirn(beta, gam): return math.cos(beta) * h + math.sin(beta) * (math.cos(gam) * c + math.sin(gam) * e3)
    beta, gam = d["beta"] * D.D2R, d["gam"] * D.D2R
    q = dirn(beta, gam)
    pins = dict(b=b, c=c, q=q)
    links = [("b", "c"), ("c", "q")]
    # the RCM sector: points beside the arm at beta, azimuth gam +- 50 deg, are part of link L2's envelope
    alive2, det = R.route_design(pins, links, "q", alive.copy(), full)
    if det is None: return dict(d, cov=0.0, kin=float(kn))
    R2 = R.frame(pins["c"], pins["q"]); i0 = int(np.argmax(alive2)) if alive2.any() else 0
    sect = []
    for k in np.linspace(-50, 50, 9):
        p_ = dirn(beta, gam + k * D.D2R)[i0] * det["radius"]["q"]; sect.append(R.local(R2[i0], p_))
    Bq = R.blocked(R2, pins["q"] * det["radius"]["q"], True)
    for p_ in sect: alive2 &= ~Bq[:, R.nearest_voxel(p_)]
    return dict(d, cov=float(alive2.mean()), kin=float(kn), axial_centre=pc, **(det or {}))


if __name__ == "__main__":
    R.RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0; R.VX, R.ER, R.EC = R.voxels()
    R.set_stride(4)
    G = []
    for az, el, b in A.bases(20, range(-20, 91, 10)):
        for s in (1, -1): G.append(dict(b=b, az=az, el=el, s=s))
    ks = sorted((evaluate(dict(g), None) for g in G), key=lambda r: -r["kin"])
    print("best kinematic (2 pivots + virtual axial, travel +-%d):" % TRAVEL, [(round(100 * r["kin"], 1), r["az"], r["el"], r["s"]) for r in ks[:8]], flush=True)
    json.dump(ks[:40], open("family_G_kin.json", "w"))
