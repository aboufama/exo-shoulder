"""rolling-fin-j2: strap-constrained spherical rolling cones on top of the shoulder (3 ACTIVE DOF, 0 passive).

Topology (scapula handler -> user's upper-arm cuff), catalogue entry `rolling-fin-j2` (docs/concepts/catalogue.json):
    S --J1 (O20 v5 hub, axis b through GH, fixed in the scapula frame)--> L1 = J1 upper plate + strap (8 x 3 mm) to
    fin F1 (Ti wall 6 mm tall x 2.5 mm thick on the cone about u1 through GH, half-angle g1)
    --J2 = F2 rolls on F1 without slip (cone about u2, half-angle g2, angle(u1, u2) = g1 + g2; crossed flexure straps
    hold the pair)--> L2 = F2 + strap (8 x 3 mm) to J3 --J3 (O20 v5 hub, axis W fixed in the humerus)--> neck strap
    (25 deg, as the baseline's) -> cuff.
DOF: rolling couples the two cone rotations, L2 rel. L1 = M(phi) = rot(u1, phi) rot(u2, k phi), k = sin g1 / sin g2:
one coordinate phi, instantaneous axis = the contact generator c(phi) (verified: u1 + k u2 is parallel to c). With J1
and J3: exactly 3 active DOF, nothing passive, no spare. The arm pose fixes phi (b . M(phi) W_r = b . y, y = Y W_r),
then theta1 (about b) and theta3 (about W).

Kinematic facts used (derived here, checked numerically in `check`):
  * G(phi) = b . M(phi) W_r depends only on the design, and dG/dphi = |u1 + k u2| det[b, c(phi), M(phi) W_r], so the
    singular set det[b, c, W] = 0 is a set of FIXED phi values (the folds of G). The design branch is the monotone piece
    of G that holds phi = 0 (the reference pose); on it the root is unique, so there are no branch flips by
    construction (still checked on the full 10 fps clips). Reachable = the polar angle of y = HG W0 from b inside
    G's range on that piece, minus the baseline's 10 deg margin at each true fold (the 3R's sing_deg convention), and
    |det[b, c, W]| >= det_min (spec 0.1).
Geometry (idealised, every part at its real size, sampled like tools/concept_baseline.py: strap undersides on a 2 mm grid
at r_ref 70 mm, hub discs on a 2.5 mm grid; fin bottom edges every 2 mm along):
  * hubs J1 (at b) and J3 (at W): O20 discs r 10 mm, 12.25 mm stack (crown), upper member at +3.15; flat at the
    max of the profile under them (baseline convention). Hub cylinder walls (r 10, +4 / +8 / +12.25) are contact-only
    samples (not in the in-band share; a wall sample inside the body makes the pose contact).
  * fins: bottom edge at one radius R_f for both fins (they must meet along the contact generator over their 6 mm
    height), R_f = max of the profile under both fins. F1 azimuth range = contact range used by the valid fit poses
    +-6 deg; F2's = k x that + 12 deg (spec).
  * L1 strap: b -> the F1 bottom-edge sample nearest b; leaves J1's upper plate (h1 + 3.15), lands on F1 (underside
    >= R_f - 3 so the 3 mm strap meets the 6 mm fin), 60 deg max ramp.
  * L2 strap: the F2 sample nearest W -> J3's lower plate (h3), >= R_f - 3 at the fin; rides OVER the L1 parts and
    J1's crown where it passes above them (+1 mm).
  * neck: J3 upper plate (h3 + 3.15) -> 25 deg toward the humerus axis, rides over the L2 strap / fins / L1 parts.
  * option l1_over: the L1 strap rides over F2's sweep (F2 top + 1) instead of under it.
  Profile of every sample = the pct-th percentile, over the kinematically valid bench poses, of its obstacle radius
  (first skin exit from GH under it + clear, or the top of a lower part under it + 1 mm), the baseline's percentile
  rule; straps take the max across their 8 mm width (a strap section is straight across).
Taken (bench rules): closure solved (residual < 0.25 deg on the whole humerus rotation), inside the band with its
margins, no interference between non-adjacent parts (lateral gap < 1 mm with radial overlap < 1 mm) and, for clip frames,
joint values continuous along the full 10 fps clip (jump <= 30 deg per frame); then no metal inside the body (bench).
Skin under parts: .cache/concept_models/rolling-fin-j2/rmap_<bench key>.npy (_rollfin_rmap.py; bench poses only,
held-out clips never posed). Every score comes from concept_bench's signed distance of the final metal points.

    python3 docs/concepts/models/rolling-fin-j2.py check [n_clip n_ws]   # a few poses, kinematic + geometric numbers
    python3 docs/concepts/models/rolling-fin-j2.py sweep                  # coarse -> refine on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, HERE)
import concept_bench as CB                                                 # noqa: E402
import _rollfin_rmap as RM                                                 # noqa: E402

ID = "rolling-fin-j2"
D2R = math.pi / 180
HUB_R, HUB_H, STACK = 10.0, 12.25, 3.15             # O20 v5 joint
STRAP_W, STRAP_T = 8.0, 3.0                         # baseline strap section
FIN_H, FIN_T, FIN_PAD = 6.0, 2.5, 6.0               # fin wall (spec)
R_REF, SP, HUB_SP = 70.0, 2.0, 2.5                  # baseline sampling
RAMP = math.tan(60 * D2R)
FLIP = 30.0                                         # deg per 10 fps frame
GAP = 1.0                                           # mm, non-adjacent clearance
ARC_MAX = 300.0                                     # deg, longest fin arc

PARAMS = dict(b_az=32.55, b_el=80.56, w_delta=71.38, w_az=4.78, beta1=45.0, psi1=-45.0, chi=95.0, g1=25.0, g2=20.0,
              det_min=0.1, sing=10.0, pct=90.0, clear=2.0, l1_over=0, neck_deg=25.0)
SWEEP = dict(b_az=(0, 60), b_el=(65, 90), w_delta=(60, 95), w_az=(-20, 40), beta1=(0, 50), psi1=(-180, 180), chi=(-180, 180),
             g1=(8, 30), g2=(8, 30), pct=(80, 100), l1_over=(0, 1))

_BENCH = {}


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bvec(az, el):                                    # tools/concept_baseline.py convention
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def rot(a, t):
    """Rodrigues: rotation(s) about unit axis a (3,) by angle(s) t (rad) -> (..., 3, 3)"""
    a = unit(np.asarray(a, float)); t = np.asarray(t, float)[..., None, None]
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(t) * K + (1 - np.cos(t)) * (K @ K)


def rotv(A, t):
    """rotations about per-pose unit axes A (n, 3) by angles t (n,) -> (n, 3, 3)"""
    A = unit(A); z = np.zeros(len(A))
    K = np.stack([np.stack([z, -A[:, 2], A[:, 1]], -1), np.stack([A[:, 2], z, -A[:, 0]], -1), np.stack([-A[:, 1], A[:, 0], z], -1)], 1)
    s = np.sin(t)[:, None, None]; c = (1 - np.cos(t))[:, None, None]
    return np.eye(3)[None] + s * K + c * (K @ K)


# ------------------------------------------------------------------------------------------------ poses
class Poses:
    """bench poses + the full fit clips (10 fps) from the evaluator's pose file (held-out clips excluded)"""
    def __init__(self, B):
        Z = CB._poses_all(); names = list(Z["NAMES"]); fit_ids = [names.index(n) for n in CB.FIT]
        self.B = B; self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kc = np.array([k == "clip" for k in B.kind])
        r_idx = np.nonzero(np.isin(Z["CID"], fit_ids))[0][0]; self.HGr = Z["HG"][r_idx].astype(float)
        self.clip_rows = {}                              # clip name -> Z indices in time order (all fit frames)
        for c in fit_ids:
            j = np.nonzero(Z["CID"] == c)[0]; self.clip_rows[names[c]] = j[np.argsort(Z["FI"][j])]
        self.HGall = Z["HG"].astype(float); self.idx = B.idx
        path = RM.cache_path(B.key)
        self.maps = np.load(path, mmap_mode="r") if os.path.exists(path) else None


def get_bench(n_clip=60, n_ws=160):
    k = (n_clip, n_ws)
    if k not in _BENCH:
        B = CB.Bench(n_clip, n_ws); _BENCH[k] = Poses(B)
    return _BENCH[k]


# ------------------------------------------------------------------------------------------------ kinematics
def design(p, HGr):
    b = bvec(p["b_az"], p["b_el"]); W0 = w_dir(p["w_delta"], p["w_az"]); Wr = HGr @ W0
    ar = HGr @ np.array([0, -1.0, 0]); ea = unit(-(ar - (ar @ b) * b)); eb = np.cross(b, ea)
    be, ps = p["beta1"] * D2R, p["psi1"] * D2R
    u1 = math.cos(be) * b + math.sin(be) * (math.cos(ps) * ea + math.sin(ps) * eb)
    ew = unit(Wr - (Wr @ u1) * u1); ex = np.cross(u1, ew); ch = p["chi"] * D2R; t = math.cos(ch) * ew + math.sin(ch) * ex
    g1, g2 = p["g1"] * D2R, p["g2"] * D2R
    u2 = math.cos(g1 + g2) * u1 + math.sin(g1 + g2) * t; cr = math.cos(g1) * u1 + math.sin(g1) * t
    k = math.sin(g1) / math.sin(g2)
    d = dict(b=b, W0=W0, Wr=Wr, u1=u1, u2=u2, cr=cr, k=k, ar=ar, g1=g1, g2=g2)
    ph = np.arange(-360, 360.001, 0.1) * D2R
    MW = Mphi(d, ph) @ Wr; G = MW @ b; C = rot(u1, ph) @ cr
    Dt = np.einsum("i,pi->p", b, np.cross(C, MW))
    i0 = np.argmin(np.abs(ph)); s = np.sign(Dt[i0]); kk = max(1.0, k)
    d.update(ph=ph, G=G, D=Dt, ok=False)
    if s == 0 or s * Dt[i0] < p["det_min"]: return d
    # monotone piece (true folds where D changes sign), then the det_min piece inside it, arcs <= ARC_MAX
    pos = s * Dt > 0; lo = hi = i0
    while lo > 0 and pos[lo - 1]: lo -= 1
    while hi < len(ph) - 1 and pos[hi + 1]: hi += 1
    fold_lo, fold_hi = lo > 0, hi < len(ph) - 1
    th = np.arccos(np.clip(G, -1, 1)) / D2R
    good = s * Dt >= p["det_min"]; a = b_ = i0
    while a > lo and good[a - 1] and (ph[b_] - ph[a - 1]) / D2R * kk <= ARC_MAX: a -= 1
    while b_ < hi and good[b_ + 1] and (ph[b_ + 1] - ph[a]) / D2R * kk <= ARC_MAX: b_ += 1
    # polar band: values of th on [a, b_]; at a true fold end, keep sing deg away from the fold's polar value
    tseg = th[a:b_ + 1]; tmin, tmax = tseg.min(), tseg.max()
    for f_ok, j in ((fold_lo, lo), (fold_hi, hi)):
        if not f_ok: continue
        tf = th[j]
        if abs(tf - tmin) < abs(tf - tmax): tmin = max(tmin, tf + p["sing"])
        else: tmax = min(tmax, tf - p["sing"])
    d.update(ok=tmax > tmin, ia=a, ib=b_, sgn=s, tmin=tmin, tmax=tmax, phi_lo=ph[a] / D2R, phi_hi=ph[b_] / D2R)
    return d


def Mphi(d, ph):
    ph = np.asarray(ph, float)
    return rot(d["u1"], ph) @ rot(d["u2"], d["k"] * ph)


def ik(d, HG, HGr):
    """-> phi, th1, th3 (rad), ok (closure + band + det), resid (deg) for humerus rotations HG (n, 3, 3)"""
    n = len(HG); out = dict(phi=np.zeros(n), th1=np.zeros(n), th3=np.zeros(n), ok=np.zeros(n, bool), resid=np.full(n, 99.0))
    if not d["ok"]: return out
    b, Wr = d["b"], d["Wr"]; y = HG @ d["W0"]; gy = y @ b
    pol = np.arccos(np.clip(gy, -1, 1)) / D2R
    inb = (pol >= d["tmin"]) & (pol <= d["tmax"])
    seg = slice(d["ia"], d["ib"] + 1); php = d["ph"][seg]; Gp = d["G"][seg]
    o = np.argsort(Gp); phi = np.interp(gy, Gp[o], php[o])
    for _ in range(3):                                   # Newton on the exact G
        MW = Mphi(d, phi) @ Wr; C = rot(d["u1"], phi) @ d["cr"]
        Gd = np.einsum("i,ni->n", b, np.cross(C, MW)) * np.linalg.norm(d["u1"] + d["k"] * d["u2"])
        phi = np.clip(phi - (MW @ b - gy) / np.where(np.abs(Gd) > 1e-6, Gd, 1e-6), php[0], php[-1])
    M = Mphi(d, phi); m = M @ Wr
    th1 = np.arctan2(np.einsum("i,ni->n", b, np.cross(m, y)), (m * y).sum(1) - (m @ b) * gy)
    R1 = rot(b, th1); Y = HG @ HGr.T
    R3 = np.einsum("nji,njk->nik", R1 @ M, Y)
    v = np.stack([R3[:, 2, 1] - R3[:, 1, 2], R3[:, 0, 2] - R3[:, 2, 0], R3[:, 1, 0] - R3[:, 0, 1]], 1) / 2
    th3 = np.arctan2(v @ Wr, (np.trace(R3, axis1=1, axis2=2) - 1) / 2)
    FK = R1 @ M @ rot(Wr, th3)
    c = (np.trace(np.einsum("nji,njk->nik", FK, Y), axis1=1, axis2=2) - 1) / 2
    resid = np.arccos(np.clip(c, -1, 1)) / D2R
    out.update(phi=phi, th1=th1, th3=th3, ok=inb & (resid < 0.25), resid=resid, pol=pol)
    return out


def continuity(d, P):
    """per bench pose: False if a clip frame is reached only through a joint jump > FLIP (full 10 fps clip)"""
    okc = np.ones(len(P.idx), bool)
    pos = {int(z): j for j, z in enumerate(P.idx)}
    for name, rows in P.clip_rows.items():
        s = ik(d, P.HGall[rows], P.HGr); last = None; bad = np.zeros(len(rows), bool)
        for t in range(len(rows)):
            if not s["ok"][t]: continue
            q = np.array([s["phi"][t], s["th1"][t], s["th3"][t]])
            if last is not None:
                dq = np.abs((q - last + math.pi) % (2 * math.pi) - math.pi) / D2R
                if dq.max() > FLIP: bad[t] = True
            last = q
        for t, z in enumerate(rows):
            if int(z) in pos and bad[t]: okc[pos[int(z)]] = False
    return okc


# ------------------------------------------------------------------------------------------------ part samplers
def strap_dirs(u, v, width=STRAP_W):
    """baseline arc_dirs for one strap: great circle u -> v, 2 mm along / across at r_ref 70 -> (ns, nc, 3)"""
    ang = math.acos(np.clip(u @ v, -1, 1)); ns = max(3, int(ang * R_REF / SP) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); th = s * ang
    D = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    cs = np.arange(-width / 2, width / 2 + 1e-6, SP) / R_REF
    return unit(D[:, None, :] * np.cos(cs)[None, :, None] + nrm[None, None, :] * np.sin(cs)[None, :, None]), ang * R_REF / (ns - 1)


def disc_dirs(u, rad=HUB_R):
    g = np.arange(-rad, rad + 1e-6, HUB_SP); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2
    X, Y = X[keep] / R_REF, Y[keep] / R_REF
    a = unit(np.cross(u, np.array([0.0, 0.0, 1.0]) + 1e-3)); c = np.cross(u, a)
    return unit(u[None] + X[:, None] * a[None] + Y[:, None] * c[None]), a, c


def fin_dirs(u, cr, a0, a1, g):
    n = max(3, int(abs(a1 - a0) * D2R * R_REF * math.sin(g) / SP) + 1)
    a = np.linspace(a0, a1, n) * D2R
    return rot(u, a) @ cr


# ------------------------------------------------------------------------------------------------ the model
def build_parts(d, p, phi_used):
    """parts in their link frames (reference coordinates in S): name -> dict(link, dirs (n,3), h, t, kind, ...)"""
    k = d["k"]; P = {}
    a0, a1 = phi_used.min() / D2R - FIN_PAD, phi_used.max() / D2R + FIN_PAD
    if (a1 - a0) > ARC_MAX + 2 * FIN_PAD or k * (a1 - a0 - 2 * FIN_PAD) + 2 * FIN_PAD > ARC_MAX + 2 * FIN_PAD: return None
    F1 = fin_dirs(d["u1"], d["cr"], a0, a1, d["g1"])
    F2 = fin_dirs(d["u2"], d["cr"], -k * (a1 - FIN_PAD) - FIN_PAD, -k * (a0 + FIN_PAD) + FIN_PAD, d["g2"])
    hd, ha, hc = disc_dirs(d["b"]); P["hub1"] = dict(link="S", dirs=hd, h=0.5, t=HUB_H, kind="disc", axis=d["b"], e=(ha, hc))
    P["F1"] = dict(link="L1", dirs=F1, h=FIN_T / 2, t=FIN_H, kind="fin")
    P["F2"] = dict(link="L2", dirs=F2, h=FIN_T / 2, t=FIN_H, kind="fin")
    j1 = int(np.argmax(F1 @ d["b"])); S1, ds1 = strap_dirs(d["b"], F1[j1])
    P["L1"] = dict(link="L1", dirs=S1.reshape(-1, 3), shape=S1.shape[:2], ds=ds1, h=0.5, t=STRAP_T, kind="strap")
    j2 = int(np.argmax(F2 @ d["Wr"])); S2, ds2 = strap_dirs(F2[j2], d["Wr"])
    P["L2"] = dict(link="L2", dirs=S2.reshape(-1, 3), shape=S2.shape[:2], ds=ds2, h=0.5, t=STRAP_T, kind="strap")
    hd3, ha3, hc3 = disc_dirs(d["Wr"]); P["hub3"] = dict(link="L2", dirs=hd3, h=0.5, t=HUB_H, kind="disc", axis=d["Wr"], e=(ha3, hc3))
    ng = p["neck_deg"] * D2R; W = d["Wr"]; ar = d["ar"]
    nk_v = unit(math.cos(ng) * W + math.sin(ng) * unit(ar - (ar @ W) * W))
    SN, dsn = strap_dirs(W, nk_v)
    P["neck"] = dict(link="H", dirs=SN.reshape(-1, 3), shape=SN.shape[:2], ds=dsn, h=0.5, t=STRAP_T, kind="strap")
    P["_fin_range"] = (a0, a1)
    return P


ADJ = {("hub1", "L1"), ("L1", "F1"), ("F1", "F2"), ("F2", "L2"), ("L2", "hub3"), ("hub3", "neck"), ("L2", "neck")}
ORDER = ["hub1", "L1", "F1", "F2", "L2", "hub3", "neck"]


def adjacent(a, b):
    return (a, b) in ADJ or (b, a) in ADJ


def link_rots(d, s, P, i_sel):
    """per selected pose: dict link -> (n, 3, 3) rotation thorax <- link reference frame"""
    RS = P.RS[i_sel]; R1 = rot(d["b"], s["th1"][i_sel]); M = Mphi(d, s["phi"][i_sel]); Y = P.HG[i_sel] @ P.HGr.T
    return dict(S=RS, L1=RS @ R1, L2=RS @ R1 @ M, H=RS @ Y)


def overlap_top(DA, rA, hA, DB, loB, hiB, hB):
    """for columns A (dirs DA (n,3), underside rA (n,)) the highest top of overlapping B columns (lateral gap < GAP)"""
    out = np.full(len(DA), -np.inf)
    if not len(DA) or not len(DB): return out
    rmin = max(20.0, float(min(rA.min(), loB.min())))
    rad = (hA + hB + GAP) / rmin
    tA, tB = cKDTree(DA), cKDTree(DB)
    M = tA.sparse_distance_matrix(tB, rad, output_type="ndarray")
    if not len(M): return out
    i, j, dist = M["i"], M["j"], M["v"]
    lat = dist * np.minimum(rA[i], loB[j]); m = lat < hA + hB + GAP
    if m.any(): np.maximum.at(out, i[m], hiB[j[m]])
    return out


def interfere(DA, loA, hiA, hA, DB, loB, hiB, hB):
    """any column pair of A and B closer than GAP laterally whose radial intervals are closer than GAP"""
    if not len(DA) or not len(DB): return False
    rmin = max(20.0, float(min(loA.min(), loB.min()))); rad = (hA + hB + GAP) / rmin
    M = cKDTree(DA).sparse_distance_matrix(cKDTree(DB), rad, output_type="ndarray")
    if not len(M): return False
    i, j = M["i"], M["j"]; lat = M["v"] * np.minimum(loA[i], loB[j])
    return bool(np.any((lat < hA + hB + GAP) & (loA[i] < hiB[j] + GAP) & (loB[j] < hiA[i] + GAP)))


def ramp_lift(prof, ds, levels):
    """1-D strap profile (ns,) lifted so it stays >= each (index, level) constraint minus a 60 deg ramp"""
    s = np.arange(len(prof)) * ds
    for j, L in levels: prof = np.maximum(prof, L - RAMP * np.abs(s - s[j]))
    return prof


def fit(p, P):
    """kinematics + part profiles for one configuration -> (model or None, per-pose state, info)"""
    n = len(P.B.poses)
    if P.maps is None: raise SystemExit("radius maps missing: python3 docs/concepts/models/_rollfin_rmap.py")
    d = design(p, P.HGr); s = ik(d, P.HG, P.HGr)
    info = dict(kin_ok=bool(d["ok"]))
    if not d["ok"] or s["ok"].sum() < 5: info["why"] = "no kinematic band"; return None, None, info
    cont = continuity(d, P)
    kin = s["ok"].copy(); valid = np.nonzero(kin)[0]
    parts = build_parts(d, p, s["phi"][valid])
    if parts is None: info["why"] = "fin arc > 300 deg"; return None, None, info
    fr = parts.pop("_fin_range")
    Rk = link_rots(d, s, P, valid)
    Dth = {nm: np.einsum("pij,kj->pki", Rk[pt["link"]], pt["dirs"]) for nm, pt in parts.items()}      # (V, k, 3)
    rs = {nm: np.stack([RM.lookup(P.maps[i], Dth[nm][q]) for q, i in enumerate(valid)]) for nm in parts}  # first exit (V, k)
    for nm in rs: rs[nm] = np.minimum(rs[nm], RM.T_CAP) + p["clear"]
    pc = p["pct"]; prof = {}

    def pctl(x): return np.percentile(x, pc, axis=0)

    def obstacle(nm, lower, r_under=None):
        """per (pose, sample): max(skin + clear, top of an overlapping lower part + GAP); lower parts (name, mask)"""
        ob = rs[nm].copy(); pt = parts[nm]
        if not lower: return ob
        r0 = pctl(ob) if r_under is None else r_under
        for q in range(len(valid)):
            for lw in lower:
                lw, m = (lw, None) if isinstance(lw, str) else lw
                m = np.ones(len(prof[lw]), bool) if m is None else m
                top = overlap_top(Dth[nm][q], r0, pt["h"], Dth[lw][q][m], prof[lw][m], prof[lw][m] + parts[lw]["t"], parts[lw]["h"])
                ob[q] = np.maximum(ob[q], top + GAP)
        return ob

    def strap(nm, ob, levels):
        pt = parts[nm]; ns, nc = pt["shape"]; pr = pctl(ob).reshape(ns, nc).max(1)
        pr = ramp_lift(pr, pt["ds"], levels); return np.repeat(pr, nc)

    prof["hub1"] = np.full(len(parts["hub1"]["dirs"]), pctl(rs["hub1"]).max())
    h1 = prof["hub1"][0]
    R_f = max(pctl(rs["F1"]).max(), pctl(rs["F2"]).max())
    if p["l1_over"]:
        prof["F1"] = np.full(len(parts["F1"]["dirs"]), R_f); prof["F2"] = np.full(len(parts["F2"]["dirs"]), R_f)
        ns1 = parts["L1"]["shape"][0]
        prof["L1"] = strap("L1", obstacle("L1", ["F2"]), [(0, h1 + STACK), (ns1 - 1, R_f - STRAP_T)])
    else:
        # the L1 strap follows the skin and meets F1 through a foot under F2's path; F2 rides over the L1 strap where
        # it sweeps above it (raises both fins: they share R_f)
        prof["L1"] = strap("L1", rs["L1"], [(0, h1 + STACK)])
        ob2 = obstacle("F2", ["L1"], r_under=np.full(len(parts["F2"]["dirs"]), R_f))
        R_f = max(R_f, pctl(ob2).max())
        prof["F1"] = np.full(len(parts["F1"]["dirs"]), R_f); prof["F2"] = np.full(len(parts["F2"]["dirs"]), R_f)
    prof["hub3"] = np.full(len(parts["hub3"]["dirs"]), pctl(rs["hub3"]).max()); h3 = prof["hub3"][0]
    ns2 = parts["L2"]["shape"][0]
    prof["L2"] = strap("L2", obstacle("L2", ["hub1", "L1", "F1"]), [(0, R_f - STRAP_T), (ns2 - 1, h3)])
    # the L2 strap's last samples sit on J3's lower plate (inside the hub's footprint)
    away = np.arccos(np.clip(parts["L2"]["dirs"] @ d["Wr"], -1, 1)) * prof["L2"] > HUB_R + 2.0    # L2 outside J3's footprint
    prof["neck"] = strap("neck", obstacle("neck", ["hub1", "L1", "F1", "F2", ("L2", away)]), [(0, h3 + STACK)])
    names = list(parts)
    pairs = [(a, b) for ai, a in enumerate(names) for b in names[ai + 1:] if not adjacent(a, b) and parts[a]["link"] != parts[b]["link"]]
    pairs.append(("L2", "neck"))                                   # adjacent at J3 only: checked outside the hub
    model = dict(p=p, d=d, parts=parts, prof=prof, names=names, pairs=pairs, R_f=R_f, h1=h1, h3=h3, fin_range=fr)
    info.update(kin_ws=round(float(kin[~P.kc].mean()), 4), kin_clip=round(float(kin[P.kc].mean()), 4), flips=int((~cont & kin).sum()),
                k=round(d["k"], 3), band=[round(d["tmin"], 1), round(d["tmax"], 1)], fin_range=[round(fr[0], 1), round(fr[1], 1)],
                R_f=round(R_f, 1), h1=round(h1, 1), h3=round(h3, 1), n_metal={nm: len(parts[nm]["dirs"]) for nm in names})
    # ---- per pose: interference, metal points
    Rall = link_rots(d, s, P, np.arange(n)); per_pose = [None] * n; why_i = {}
    for i in range(n):
        if not kin[i] or not cont[i]: continue
        out = pose_points(model, {lk: Rall[lk][i] for lk in Rall})
        if out[0] is None: why_i[out[1]] = why_i.get(out[1], 0) + 1; continue
        per_pose[i] = out
    info.update(interf=int(sum(why_i.values())), interf_pairs={f"{a}-{b}": c for (a, b), c in why_i.items()})
    return model, per_pose, info


def score_many(plist, n_clip=60, n_ws=160, want_detail=False):
    """fit every configuration, then ONE signed-distance call per bench pose for all of them; bench report each"""
    P = get_bench(n_clip, n_ws); B = P.B; n = len(B.poses)
    fits = [fit(p, P) for p in plist]
    res = [[None] * n for _ in plist]; pb = [None] * len(plist)
    for c, (model, per_pose, info) in enumerate(fits):
        if model is not None: pb[c] = {nm: [] for nm in model["names"]}
    for i in range(n):
        chunks = []
        for c, (model, per_pose, info) in enumerate(fits):
            if model is not None and per_pose[i] is not None: chunks.append((c, per_pose[i]))
        if not chunks: continue
        X = np.concatenate([np.concatenate([pts, wall]) for _, (pts, wall, per) in chunks]); dX = B.dist(i, X); o = 0
        for c, (pts, wall, per) in chunks:
            dp = dX[o:o + len(pts)]; dw = dX[o + len(pts):o + len(pts) + len(wall)]; o += len(pts) + len(wall)
            res[c][i] = np.concatenate([dp, dw]) if dw.min() < 0 else dp
            if dw.min() >= 0 and dp.min() >= 0 and P.kc[i]:
                q = 0
                for nm in fits[c][0]["names"]: m = len(per[nm]); pb[c][nm].append(dp[q:q + m]); q += m
    out = []
    for c, (model, per_pose, info) in enumerate(fits):
        B.res = res[c]; r = B.report(); r.update(info)
        if model is not None:
            band = lambda v: round(float(np.mean((v >= 2) & (v <= 14))), 3)
            r["part_band14"] = {nm: (band(np.concatenate(v)) if v else None) for nm, v in pb[c].items()}
            _MODELS[_pkey(plist[c], n_clip, n_ws)] = model
            if want_detail: r["_model"] = model; r["_per_pose"] = per_pose
        out.append(r)
    B.reset()
    return out


def evaluate(p, n_clip=60, n_ws=160, want_detail=False):
    return score_many([p], n_clip, n_ws, want_detail)[0]


def pose_points(model, Rl):
    """metal of one pose given the link rotations Rl (link -> 3x3, thorax <- link reference frame):
    (facing points (k, 3), contact-only hub-wall points (m, 3), {part: points}) or (None, interfering pair)"""
    parts, prof, d = model["parts"], model["prof"], model["d"]
    Dp = {nm: (Rl[pt["link"]] @ pt["dirs"].T).T for nm, pt in parts.items()}
    for a, bb in model["pairs"]:
        selA = np.ones(len(Dp[a]), bool); selB = np.ones(len(Dp[bb]), bool)
        if (a, bb) == ("L2", "neck"):
            w = Rl["L2"] @ d["Wr"]; rr = HUB_R + 2.0
            selA = np.arccos(np.clip(Dp[a] @ w, -1, 1)) * prof[a] > rr; selB = np.arccos(np.clip(Dp[bb] @ w, -1, 1)) * prof[bb] > rr
        if interfere(Dp[a][selA], prof[a][selA], prof[a][selA] + parts[a]["t"], parts[a]["h"],
                     Dp[bb][selB], prof[bb][selB], prof[bb][selB] + parts[bb]["t"], parts[bb]["h"]):
            return None, (a, bb)
    per = {nm: Dp[nm] * prof[nm][:, None] for nm in model["names"]}
    wall = []
    for nm in ("hub1", "hub3"):
        ax = Rl[parts[nm]["link"]] @ parts[nm]["axis"]; e1 = unit(np.cross(ax, [0.0, 0.0, 1.0 + 1e-3])); e2 = np.cross(ax, e1)
        tt = np.linspace(0, 2 * math.pi, 16, endpoint=False)
        for z in (4.0, 8.0, HUB_H):
            wall.append((prof[nm][0] + z) * ax[None] + HUB_R * (np.cos(tt)[:, None] * e1 + np.sin(tt)[:, None] * e2))
    return np.concatenate(list(per.values())), np.concatenate(wall), per


_MODELS = {}


def _pkey(p, n_clip, n_ws):
    return json.dumps(dict(p, _b=[n_clip, n_ws]), sort_keys=True)


def metal(pose, frames, params=None, n_clip=60, n_ws=160):
    """the bench interface: skin-facing metal points (k, 3) in the thorax frame for one pose, or None when the
    mechanism cannot take it (no closure in the band / interference). The parts' profiles are fitted once per params
    on Bench(n_clip, n_ws) (evaluate()). Branch continuity needs the clip context and is checked in evaluate() only;
    the hub-wall contact-only samples are added there too."""
    p = dict(PARAMS, **(params or {})); key = _pkey(p, n_clip, n_ws)
    if key not in _MODELS: evaluate(p, n_clip, n_ws)
    model = _MODELS.get(key)
    if model is None: return None
    import body_pose as BP
    Rs, Rh = frames["S"][0], frames["H"][0]; HG = (Rs.T @ Rh @ np.array(BP._rig().L["rest_humerus"]))[None]
    P = get_bench(n_clip, n_ws); d = model["d"]; s = ik(d, HG, P.HGr)
    if not s["ok"][0]: return None
    R1 = rot(d["b"], s["th1"][0]); M = Mphi(d, s["phi"][0]); Y = HG[0] @ P.HGr.T
    out = pose_points(model, dict(S=Rs, L1=Rs @ R1, L2=Rs @ R1 @ M, H=Rs @ Y))
    return None if out[0] is None else out[0]


# ------------------------------------------------------------------------------------------------ checks / sweep
def check(n_clip=60, n_ws=160, p=None):
    p = dict(PARAMS, **(p or {})); P = get_bench(n_clip, n_ws)
    d = design(p, P.HGr)
    # rolling check: F2's contact sample coincides with c(phi); u1 + k u2 parallel to c
    for ph in (-0.6, 0.0, 0.4):
        c1 = rot(d["u1"], ph) @ d["cr"]; c2 = Mphi(d, ph) @ (rot(d["u2"], -d["k"] * ph) @ d["cr"])
        print(f"phi {ph / D2R:+.0f}: |c_F1 - c_F2| = {np.linalg.norm(c1 - c2):.2e}")
    w = d["u1"] + d["k"] * d["u2"]; print("angle(u1 + k u2, c_r) deg:", round(math.degrees(math.acos(unit(w) @ d["cr"])), 4))
    print("design ok", d["ok"], "band", d.get("tmin"), d.get("tmax"), "phi piece", d.get("phi_lo"), d.get("phi_hi"), "k", d["k"])
    s = ik(d, P.HG, P.HGr)
    print("kin ws", s["ok"][~P.kc].mean(), "clip", s["ok"][P.kc].mean(), "max resid (solved)", s["resid"][s["ok"]].max() if s["ok"].any() else None)
    probes = dict(rest=dict(plane=0, elev=5, axial=0, flex=12, pron=0), overhead=dict(plane=30, elev=160, axial=0, flex=12, pron=0),
                  across=dict(plane=120, elev=90, axial=0, flex=90, pron=0), behind=dict(plane=-40, elev=40, axial=-60, flex=90, pron=0))
    import body_pose as BP
    rig = BP._rig(); RH = np.array(rig.L["rest_humerus"])
    for nm, q in probes.items():
        (T, S, H, Fa, Pr), lift = BP.segs(rig.L, rig.s, q); HG = (S[0].T @ H[0] @ RH)[None]
        ss = ik(d, HG, P.HGr)
        print(f"  {nm:9s} pol {ss.get('pol', [np.nan])[0]:6.1f} ok {bool(ss['ok'][0])} phi {ss['phi'][0] / D2R:7.1f} th1 {ss['th1'][0] / D2R:7.1f} th3 {ss['th3'][0] / D2R:7.1f} resid {ss['resid'][0]:.3g}")
    t = time.time(); r = evaluate(p, n_clip, n_ws); print(round(time.time() - t, 1), "s"); print({k: v for k, v in r.items() if not k.startswith("_")})
    return r


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")


def log_cfg(rows, p, r):
    rows.append(dict(k=len(rows), t=now(), params={k: (round(v, 3) if isinstance(v, float) else v) for k, v in p.items()},
                     inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"],
                     extra={k: r[k] for k in ("kin_ws", "kin_clip", "interf", "flips", "R_f", "band", "fin_range", "k") if k in r}))
    os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
    json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)


def kin_cover(p, P):
    d = design(p, P.HGr); s = ik(d, P.HG, P.HGr)
    return s["ok"][~P.kc].mean(), s["ok"][P.kc].mean()


def _rand_cfg(rng, base, keys):
    q = dict(base)
    for k in keys:
        lo, hi = SWEEP[k]; q[k] = int(rng.integers(lo, hi + 1)) if k == "l1_over" else float(rng.uniform(lo, hi))
    return q


def _perturb(rng, base, scale):
    q = dict(base)
    for k, w in scale.items():
        lo, hi = SWEEP[k]
        if k == "l1_over": continue
        if k in ("psi1", "chi"): q[k] = float((q[k] + rng.normal(0, w) + 180) % 360 - 180)
        else: q[k] = float(np.clip(q[k] + rng.normal(0, w), lo, hi))
    return q


def sweep(n_clip=60, n_ws=160, n_coarse=60, n_refine=60, batch=10, log=print):
    """coarse: random shapes (beta1, psi1, chi, g1, g2, l1_over) at the spec's b / W0, pre-filtered on the free
    kinematic band (>= 0.85 of the workspace); refine: perturbations of the best 4 incl. b / W0; then pct per best."""
    P = get_bench(n_clip, n_ws); rng = np.random.default_rng(20261015); rows = []; t0 = time.time()

    def run(cfgs, tag):
        for j in range(0, len(cfgs), batch):
            rs = score_many(cfgs[j:j + batch], n_clip, n_ws)
            for q, r in zip(cfgs[j:j + batch], rs):
                log_cfg(rows, q, r)
            best = min(rows, key=lambda x: x["gap"])
            log(f"[{tag}] {len(rows)} configs, {time.time() - t0:.0f} s; best gap {best['gap']} (#{best['k']}) "
                f"reach {best['reach']} follow {best['follow']} in14 {best['inband14']} contact {best['contact']}", flush=True)

    shape = ["beta1", "psi1", "chi", "g1", "g2", "l1_over"]
    cand = []; tried = 0
    while len(cand) < n_coarse and tried < 20000:
        q = _rand_cfg(rng, PARAMS, shape); tried += 1
        kw, kcl = kin_cover(q, P)
        if kw >= 0.85 and kcl >= 0.95: cand.append(q)
    log(f"kinematic pre-filter: {len(cand)} of {tried} random shapes cover >= 85 % ws / 95 % clip", flush=True)
    run(cand, "coarse")
    top = sorted(rows, key=lambda x: x["gap"])[:4]
    ref = []
    for tr in top:
        for _ in range(n_refine // 4):
            q = _perturb(rng, dict(PARAMS, **tr["params"]), dict(beta1=5, psi1=12, chi=12, g1=3, g2=3, b_az=8, b_el=4, w_delta=6, w_az=8))
            if rng.random() < 0.25: q["l1_over"] = 1 - q["l1_over"]
            ref.append(q)
    run(ref, "refine")
    top = sorted(rows, key=lambda x: x["gap"])[:2]; pc = []
    for tr in top:
        for v in (80.0, 85.0, 95.0, 100.0):
            pc.append(dict(PARAMS, **tr["params"], pct=v))
    run(pc, "pct")
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    mode = a[0] if a else "check"
    if mode == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (60, 160)
        check(nc, nw)
    elif mode == "sweep":
        sweep()
