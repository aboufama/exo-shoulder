"""rolling-cone-elbow: spherical 3-DOF chain whose middle joint is a pair of strap-bound cones rolling on each other
about the GH centre (no J2 hub). Concept screen on tools/concept_bench.py, idealised geometry at real part sizes.

Topology (docs/concepts/catalogue.json, id rolling-cone-elbow):
  scapula base --J1 (O20 hub, axis b, fixed in the scapula)--> link 1 = strap + SUN rim (cone, apex GH, axis s0,
  half-angle a1) ==J2 rolling contact== PLANET rim (cone, apex GH, axis c, half-angle a2, external contact
  angle(s0, c) = a1 + a2) + strap = link 2 --J3 (O20 hub, axis W, fixed in the humerus)--> arm-end plate + neck to
  BOTTOM's bar. Active DOF 3 (q1, psi, q3); passive 0. The rolling pair is a 1-DOF spherical joint (no slip + contact
  + crossed straps): link 2 relative to link 1 is M(psi) = R(s0, psi) R(c0, k psi), k = sin a1 / sin a2, a rotation
  about the contact generator g(psi) = R(s0, psi) g0 (checked numerically in `check`).

IK (closed chain, per pose): w = HG W (scapula frame), theta = angle(b, w). On link 1, link 2 carries w2 to
v(psi) = M(psi) w2; J1 can only rotate v about b, so the chain closes iff angle(b, v(psi)) = theta. theta(psi) is
evaluated on a 0.5 deg grid; the design's BRANCH is the monotone segment of theta(psi) that contains psi = 0 (gamma /
gamma2 set which one), so the root is unique and continuous in theta - no branch flips by construction. Stationary
ends of the segment are the fold singularities (b, g, v coplanar <=> d theta / d psi = 0): the window keeps `sing`
deg of theta away from them, exactly like the baseline's sing_deg on the 3R's triangle limits. The rims cannot be
longer than RIM_MAX deg of their own circle (crossed straps need two anchors): a longer segment is cut to the
sub-interval holding the most fit poses (a joint limit, no margin needed). Root by bisection (residual < 1e-6 deg),
q1 = signed angle about b from v to w, q3 = twist about W between link 2 and the humerus.

Geometry (mm, thorax frame of the bench, origin GH; every metal part at its real size):
  * O20 hubs (docs/HARDWARE.md v5): 10 mm radius discs normal to the axis, lower face F = max over disc samples and fit
    poses of the K3 requirement projected on the axis; stack F .. F + 12.25; upper member underside F + 3.15.
    J1: lower = base plate (scapula), upper = link 1. J3: lower = arm-end plate (humerus), upper = link 2.
  * Straps 12 x 3 mm (K5) on the great circle hub -> rim (link 1: b -> sun rim mid-arc, inner flange edge; link 2:
    planet rim mid-arc -> W). Underside per sample = K3 requirement (q-quantile over fit poses), anchored at the hub's
    upper-member level and at the rim foot, climbing / diving at most 60 deg (Lipschitz envelope along the strap).
  * Rims: 8 mm tall x 2 mm standing cone band (the rolling surface, radial) + an inward foot flange `flange` mm wide x
    2 mm (SPEC FIX: a free 2 x 8 band cantilevered 60-190 mm deflects ~4 mm under 10 N sideways; with a 6 mm flange
    ~0.3 mm). Sampled every 2 mm along the arc at the foot, rows 2 mm apart across band + flange. Span = the contact
    range visited over the fit poses +- 10 deg of psi (equal arc on both rims). SPEC FIX: the spec puts both rims at
    one constant radius rho_c; but sun point psi only ever touches planet point -k psi, so the two rims can follow a
    shared radial profile rho(psi) (rim_mode 'profile': each rim at its own requirement, matched points within
    8 - ov_min mm so >= ov_min mm of the contact line stays engaged, slope <= 45 deg along the arc). rim_mode 'const'
    is the literal spec (one rho_c for both rims).
  * Neck (K7): 14 x 6 mm strap fixed in the humerus from the J3 arm-end plate (level F3) to BOTTOM's bar top
    (67.5 Wb + 40 Db, Wb = (0, -0.0713, 0.9975), Db = (0, -0.9975, -0.0713), humerus frame).
  * K3 requirement r_i(d): first t >= 15 mm along d with signed distance >= 2 mm and >= 0 over [t, t + 15]
    (Lipschitz-safe march with a 1 mm minimum step on the bench's distance field).
Taken pose: chain closes in the window (residual < 0.5 deg), along each clip the arm path between consecutive bench
frames (12 slerp sub-steps) stays in the window with no joint step > 25 deg, no two non-adjacent parts closer than
1 mm (K6: lateral gap < 1 mm with radial intervals within 1 mm; joint partners exempt within 12 mm of their axis; the
two rims exempt within 12 mm of the contact generator), and no metal inside the body (bench contact).
Frames: humerus directions use the evaluator's humerus frame HG (pose file, like tools/concept_baseline.py and the
champion's W; HG differs from B.frames()['H'] by a constant ~10 deg rotation whose -y is the arm axis).

    python3 docs/concepts/models/rolling-cone-elbow.py check [n_clip n_ws]   # numeric checks + a few poses
    python3 docs/concepts/models/rolling-cone-elbow.py kin                   # kinematic window scan (no distances)
    python3 docs/concepts/models/rolling-cone-elbow.py sweep                 # the sweep (sweeps/, rows/)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                        # noqa: E402

ID = "rolling-cone-elbow"
D2R = math.pi / 180
HUB_R, HUB_H, STACK = 10.0, 12.25, 3.15                           # O20 v5
R_REF = 70.0                                                      # mm -> rad for sample spacing (as the baseline)
SP = 2.0                                                          # 2 mm grid = 1 point / 4 mm2
RIM_H, RIM_T = 8.0, 2.0                                           # standing band: radial height, thickness
RIM_MAX = 270.0                                                   # max rim arc (deg of its own circle)
PAD = 10.0                                                        # rim beyond the visited contact range (deg of psi)
L_STRAP, L_RIM = math.tan(60 * D2R), 1.0                          # max climb along straps / rims
PART_CLEAR = 1.0
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713]); BAR = 67.5 * WB + 40.0 * DB

PARAMS = dict(az=2.43, el=80.68, wd=86.33, wa=21.83,               # J1 axis b (scapula), J3 axis W (humerus) = champion's
              a1=40.0, a2=40.0, beta1=30.0, beta2=30.0,            # cone half-angles; b from s0, W from c0 (deg)
              gamma=0.0, gamma2=180.0, sing=10.0,                  # planet phase about s0, W azimuth about c0, fold margin
              q=1.0, rim_mode="profile", ov_min=5.0, lift=0.0, flange=6.0,
              strap_w=12.0, strap_t=3.0, neck_w=14.0, neck_t=6.0)
SWEEP = dict(a1=(25, 60), a2=(25, 60), beta1=(10, 50), beta2=(10, 50), gamma=(-180, 180), gamma2=(-180, 180),
             az=(-60, 60), el=(40, 90), wd=(75, 115), wa=(-60, 60), q=(0.93, 1.0), rim_mode=("profile", "const"), lift=(0, 3))


def unit(v):
    v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, a):
    return np.array([math.sin(d * D2R) * math.sin(a * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(a * D2R)])


def rotv(ax, ang):
    """Rodrigues: rotation matrices about unit axis ax (3,) by angles ang (n,) rad -> (n, 3, 3)"""
    ang = np.atleast_1d(np.asarray(ang, float)); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    s, c = np.sin(ang)[:, None, None], np.cos(ang)[:, None, None]
    return np.eye(3)[None] + s * K[None] + (1 - c) * (K @ K)[None]


def perp(u, ref=np.array([0.0, 0.0, 1.0])):
    p = ref - (ref @ u) * u
    if np.linalg.norm(p) < 1e-6: p = np.array([1.0, 0.0, 0.0]) - u[0] * u
    return unit(p)


def sph(axis, e0, alpha, phi):
    """directions at polar angle alpha (rad, scalar or (n,)) and azimuth phi (rad, (n,)) about axis, phi 0 along e0"""
    e1 = np.cross(axis, e0); alpha = np.broadcast_to(np.asarray(alpha, float), np.shape(phi))
    return (np.cos(alpha)[..., None] * axis + np.sin(alpha)[..., None] * (np.cos(phi)[..., None] * e0 + np.sin(phi)[..., None] * e1))


# ------------------------------------------------------------------------------------------------ distance field
class Field:
    """signed distance for (pose index, point) pairs; vectorised over poses on the bench's FAST grid when it exists"""
    def __init__(self, B):
        self.B = B; self.G = B.grid; self.n = None if B.grid is None else B.grid.shape[1]

    def dist(self, I, P):
        I = np.asarray(I); P = np.asarray(P, float)
        if self.G is None:
            out = np.empty(len(I))
            for i in np.unique(I):
                m = I == i; out[m] = self.B.dist(int(i), P[m])
            return out
        g = (P + CB.HALF) / CB.H_GRID; n = self.n
        ins = np.all((g >= 0) & (g <= n - 1 - 1e-9), axis=1); out = np.empty(len(P))
        if ins.any():
            gi = g[ins]; i0 = np.floor(gi).astype(np.int64); f = (gi - i0).astype(np.float32); ii = I[ins]; G = self.G
            x0, y0, z0 = i0.T; x1, y1, z1 = x0 + 1, y0 + 1, z0 + 1; fx, fy, fz = f.T
            c = lambda a, b, cc: G[ii, a, b, cc].astype(np.float32)
            v = (c(x0, y0, z0) * (1 - fx) * (1 - fy) * (1 - fz) + c(x1, y0, z0) * fx * (1 - fy) * (1 - fz) + c(x0, y1, z0) * (1 - fx) * fy * (1 - fz)
                 + c(x0, y0, z1) * (1 - fx) * (1 - fy) * fz + c(x1, y1, z0) * fx * fy * (1 - fz) + c(x1, y0, z1) * fx * (1 - fy) * fz
                 + c(x0, y1, z1) * (1 - fx) * fy * fz + c(x1, y1, z1) * fx * fy * fz)
            out[ins] = v * CB.Q
        if (~ins).any():
            jj = np.nonzero(~ins)[0]
            for i in np.unique(I[jj]):
                m = jj[I[jj] == i]; out[m] = self.B.dist(int(i), P[m])
        return out

    def requirement(self, I, D, t0=15.0, t1=220.0, clear=2.0, run=15.0):
        """K3: first t on the ray t*D (from t0) with dist >= clear and dist >= 0 over [t, t + run]; t1 if none"""
        I = np.asarray(I)
        if self.G is None and len(np.unique(I)) > 1:                   # exact path: one pose at a time (libigl tree cache)
            out = np.empty(len(I))
            for i in np.unique(I):
                m_ = I == i; out[m_] = self.requirement(I[m_], D[m_], t0, t1, clear, run)
            return out
        m = len(I); t = np.full(m, t0); found = np.full(m, t1); s = np.zeros(m); st = np.zeros(m, np.int8)
        for _ in range(400):
            a = np.nonzero(st < 2)[0]
            if not len(a): break
            pos = np.where(st[a] == 0, t[a], s[a]); d = self.dist(I[a], pos[:, None] * D[a]); sa = st[a]
            srch = sa == 0; hit = srch & (d >= clear)
            k = a[hit]; st[k] = 1; found[k] = t[k]; s[k] = t[k] + np.maximum(d[hit], 1.0)
            k = a[srch & ~hit]; t[k] += np.maximum(1.0, clear - d[srch & ~hit])
            ver = sa == 1; bad = ver & (d < 0)
            k = a[bad]; st[k] = 0; t[k] = s[k] + np.maximum(1.0, clear - d[bad])
            good = ver & ~bad; k = a[good]; s[k] += np.maximum(d[good], 1.0)
            k = k[s[k] > found[k] + run]; st[k] = 2
            over = (st == 0) & (t > t1); found[over] = t1; st[over] = 2
        return found


# ------------------------------------------------------------------------------------------------ pose data
class Rig:
    def __init__(self, B):
        self.B = B; Z = CB._poses_all()
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float); self.RH = self.RS @ self.HG
        self.kind = np.array(B.kind); self.order = B.clip_order(); self.F = Field(B); self.n = len(B.poses)
        self.prev = {}                                                 # clip frame -> previous frame of the same clip
        for c, js in self.order.items():
            for a, b in zip(js[:-1], js[1:]): self.prev[b] = a
        self.sub = {}                                                  # sub-step HG / RS between consecutive clip frames
        for b, a in self.prev.items():
            ts = np.linspace(0, 1, 13)[1:-1]
            self.sub[b] = (Slerp([0, 1], Rotation.from_matrix(self.HG[[a, b]]))(ts).as_matrix(),
                           Slerp([0, 1], Rotation.from_matrix(self.RS[[a, b]]))(ts).as_matrix())


# ------------------------------------------------------------------------------------------------ kinematics
class Kin:
    def __init__(self, p):
        self.p = p; a1, a2 = p["a1"] * D2R, p["a2"] * D2R; self.a1, self.a2 = a1, a2; self.k = math.sin(a1) / math.sin(a2)
        b = bvec(p["az"], p["el"]); self.b = b
        e = perp(b, np.array([1.0, 0.0, 0.0]))                       # azimuth of s0 about b: absorbed by q1
        s0 = math.cos(p["beta1"] * D2R) * b + math.sin(p["beta1"] * D2R) * e; self.s0 = s0
        f = unit(b - (b @ s0) * s0)                                   # in the (b, s0) plane, from s0 toward b
        cref = math.cos(a1 + a2) * s0 - math.sin(a1 + a2) * f         # planet axis on the far side of s0 from b
        c0 = rotv(s0, p["gamma"] * D2R)[0] @ cref; self.c0 = c0
        self.g0 = unit(math.sin(a2) * s0 + math.sin(a1) * c0)        # contact generator at psi = 0
        ts = unit(s0 - (s0 @ c0) * c0)                                # from c0 toward the sun
        self.w2 = sph(c0, ts, p["beta2"] * D2R, np.array(p["gamma2"] * D2R))
        self.Wh = wdir(p["wd"], p["wa"])
        self.u0s = unit(self.g0 - (self.g0 @ s0) * s0); self.u0p = unit(self.g0 - (self.g0 @ c0) * c0)
        self.r2 = perp(self.w2); self.rh = perp(self.Wh)

    def M(self, psi):
        """link 2 -> link 1 rotation (n, 3, 3) at rolling angles psi (rad, (n,))"""
        return rotv(self.s0, psi) @ rotv(self.c0, self.k * np.asarray(psi))

    def theta_of(self, psi):
        v = self.M(psi) @ self.w2; return np.arccos(np.clip(v @ self.b, -1, 1)) / D2R

    def segment(self, theta_fit=None):
        """monotone segment of theta(psi) containing psi = 0 -> (psi grid deg, theta grid, window lo, hi, info)"""
        pg = np.arange(-360.0, 360.001, 0.5); th = self.theta_of(pg * D2R); i0 = 720
        dth = np.diff(th); s = np.sign(dth[i0]) if dth[i0] != 0 else 1.0
        lo = i0
        while lo > 0 and np.sign(dth[lo - 1]) == s: lo -= 1
        hi = i0 + 1
        while hi < len(pg) - 1 and np.sign(dth[hi]) == s: hi += 1
        stat_lo, stat_hi = lo > 0, hi < len(pg) - 1
        span_max = min(RIM_MAX, RIM_MAX / self.k) - 2 * PAD           # psi span the rims allow
        if pg[hi] - pg[lo] > span_max:                                # cut: keep the sub-interval holding most fit poses
            w = int(round(span_max / 0.5)); best = None
            for a in range(lo, hi - w + 1, 2):
                tl, th_ = sorted((th[a], th[a + w]))
                tl += self.p["sing"] if (a == lo and stat_lo and s > 0) or (a + w == hi and stat_hi and s < 0) else 0.0
                th_ -= self.p["sing"] if (a + w == hi and stat_hi and s > 0) or (a == lo and stat_lo and s < 0) else 0.0
                sc = np.mean((theta_fit >= tl) & (theta_fit <= th_)) if theta_fit is not None else th_ - tl
                if best is None or sc > best[0]: best = (sc, a)
            a = best[1]
            stat_lo, stat_hi = stat_lo and a == lo, stat_hi and a + w == hi; lo, hi = a, a + w
        pseg, tseg = pg[lo:hi + 1], th[lo:hi + 1]
        if s < 0: pseg, tseg = pseg[::-1], tseg[::-1]; stat_lo, stat_hi = stat_hi, stat_lo
        tlo = tseg[0] + (self.p["sing"] if stat_lo else 0.0); thi = tseg[-1] - (self.p["sing"] if stat_hi else 0.0)
        return pseg, tseg, tlo, thi, dict(psi_lo=float(min(pseg[0], pseg[-1])), psi_hi=float(max(pseg[0], pseg[-1])), stat=(bool(stat_lo), bool(stat_hi)))

    def solve(self, theta, seg):
        """psi (deg) on the segment for each theta (deg) inside the window; nan outside"""
        pseg, tseg, tlo, thi, _ = seg; theta = np.asarray(theta, float); out = np.full(theta.shape, np.nan)
        ok = (theta >= tlo) & (theta <= thi)
        if not ok.any(): return out
        j = np.clip(np.searchsorted(tseg, theta[ok]) - 1, 0, len(tseg) - 2)
        a, b = pseg[j].copy(), pseg[j + 1].copy(); ta = tseg[j]
        for _ in range(40):
            m = 0.5 * (a + b); tm = self.theta_of(m * D2R); left = (tm - theta[ok]) * (tseg[j + 1] - ta) < 0
            a = np.where(left, m, a); b = np.where(left, b, m)
        out[ok] = 0.5 * (a + b); return out

    def joints(self, HG, psi):
        """q1, q3 (deg), link rotations L1, L2 (n, 3, 3, scapula frame) and the closure residual (deg)"""; psi_r = np.nan_to_num(psi) * D2R; w = HG @ self.Wh; Mp = self.M(psi_r); v = Mp @ self.w2
        b = self.b; vp = v - (v @ b)[:, None] * b; wp = w - (w @ b)[:, None] * b
        q1 = np.arctan2(np.cross(vp, wp) @ b, (vp * wp).sum(1))
        L1 = rotv(b, q1); L2 = L1 @ Mp
        res = np.arccos(np.clip(((L2 @ self.w2) * w).sum(1), -1, 1)) / D2R
        a = L2 @ self.r2; h = HG @ self.rh
        q3 = np.arctan2((np.cross(h, a) * w).sum(1), (h * a).sum(1))
        return q1 / D2R, q3 / D2R, L1, L2, res


def kinematics(p, R):
    """per-pose closure: valid mask, psi, q1, q3, L1, L2 + the segment; continuity along clips (sub-steps)"""
    K = Kin(p); w = R.HG @ K.Wh; theta = np.arccos(np.clip(w @ K.b, -1, 1)) / D2R
    seg = K.segment(theta)
    psi = K.solve(theta, seg); q1, q3, L1, L2, res = K.joints(R.HG, psi)
    valid = np.isfinite(psi) & (res < 0.5)
    cont = valid.copy(); jump = np.zeros(R.n)
    for b_, a_ in R.prev.items():                                     # path from the previous clip frame
        if not valid[b_] or not valid[a_]: continue                   # previous frame out of reach: re-entry is unique
        HGs, _ = R.sub[b_]; ths = np.arccos(np.clip((HGs @ K.Wh) @ K.b, -1, 1)) / D2R
        if not ((ths >= seg[2]) & (ths <= seg[3])).all():
            cont[b_] = False; continue                                # the arm path leaves the window between frames
        ps = K.solve(ths, seg); qa, qb, *_ = K.joints(HGs, ps)
        Q = np.c_[np.r_[psi[a_], ps, psi[b_]], np.r_[q1[a_], qa, q1[b_]], np.r_[q3[a_], qb, q3[b_]]]
        st = np.abs((np.diff(Q, axis=0) + 180) % 360 - 180).max(); jump[b_] = st
        if st > 25: cont[b_] = False
    return dict(K=K, theta=theta, seg=seg, psi=psi, q1=q1, q3=q3, L1=L1, L2=L2, res=res, valid=valid, cont=cont, jump=jump)


# ------------------------------------------------------------------------------------------------ parts
def envelope(h, ds, L):
    """Lipschitz upper envelope along axis -1: rho >= h, |d rho / ds| <= L"""
    f = h.copy(); st = L * ds
    for i in range(1, f.shape[-1]): f[..., i] = np.maximum(f[..., i], f[..., i - 1] - st)
    for i in range(f.shape[-1] - 2, -1, -1): f[..., i] = np.maximum(f[..., i], f[..., i + 1] - st)
    return f


def gc_strap(u, v, width, start_mm=0.0, end_mm=0.0):
    """directions of a strap on the great circle u -> v: (ns, nc, 3), along spacing (rad), across offsets (mm)"""
    ang = math.acos(np.clip(u @ v, -1, 1)); nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u))
    a0, a1 = start_mm / R_REF, ang - end_mm / R_REF; ns = max(2, int((a1 - a0) * R_REF / SP) + 1)
    th = np.linspace(a0, a1, ns); D = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    cs = np.arange(-width / 2 + SP / 2, width / 2, SP)
    out = unit(D[:, None, :] * np.cos(cs / R_REF)[None, :, None] + nrm[None, None, :] * np.sin(cs / R_REF)[None, :, None])
    return out, (a1 - a0) / max(ns - 1, 1), cs


def disc(axis):
    g = np.arange(-HUB_R + 1, HUB_R, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= HUB_R ** 2
    e1 = perp(axis); e2 = np.cross(axis, e1)
    return X[m][:, None] * e1 + Y[m][:, None] * e2                    # in-plane offsets (m, 3) mm


def req_rigid(R, fit, Rot, U):
    """K3 requirement of directions U (m, 3) fixed in a member with rotations Rot (n, 3, 3) thorax, over fit poses ->
    (n_fit, m)"""
    D = np.einsum("pij,mj->pmi", Rot[fit], U).reshape(-1, 3); I = np.repeat(fit, len(U))
    return R.F.requirement(I, D).reshape(len(fit), len(U))


def hub_level(R, fit, Rot, axis):
    off = disc(axis); U = unit(R_REF * axis + off); r = req_rigid(R, fit, Rot, U)
    return float((r * (U @ axis)[None]).max()), off


def build(p, R, kin=None, log=None):
    """fit every part; returns a model dict with per-pose metal (or None) and collision info"""
    p = {**PARAMS, **p}; kin = kin or kinematics(p, R); K = kin["K"]; fit = np.nonzero(kin["valid"])[0]
    if len(fit) < 10: return None
    q = p["q"]; Q = lambda r: np.quantile(r, q, axis=0) if q < 1 else r.max(0)
    RS = R.RS; Rl1 = RS @ kin["L1"]; Rl2 = RS @ kin["L2"]; Rh = R.RH
    # --- hubs
    F1, off1 = hub_level(R, fit, RS, K.b); F3, off3 = hub_level(R, fit, Rh, K.Wh)
    # --- rims over the visited psi range
    ps = kin["psi"][fit]; plo, phi = ps.min() - PAD, ps.max() + PAD; pmid = 0.5 * (ps.min() + ps.max())
    dpsi = SP / (R_REF * math.sin(K.a1)) / D2R; pv = np.linspace(plo, phi, max(3, int((phi - plo) / dpsi) + 1)) * D2R
    nfl = int(round(p["flange"] / SP)); offs = RIM_T / 2 + SP * np.arange(nfl + 1)          # 1, 3, 5, 7 mm inside
    sun = np.stack([sph(K.s0, K.u0s, K.a1 - o / R_REF, pv) for o in offs], 1)               # (ns, nr, 3) link 1
    pla = np.stack([sph(K.c0, K.u0p, K.a2 - o / R_REF, -K.k * pv) for o in offs], 1)        # link 2
    rs = Q(req_rigid(R, fit, Rl1, sun.reshape(-1, 3))).reshape(sun.shape[:2]).max(1) + p["lift"]
    rp = Q(req_rigid(R, fit, Rl2, pla.reshape(-1, 3))).reshape(pla.shape[:2]).max(1) + p["lift"]
    ds_rim = SP
    if p["rim_mode"] == "const":
        rs = rp = np.full(len(pv), max(rs.max(), rp.max()))
    else:
        tol = RIM_H - p["ov_min"]
        for _ in range(6):
            rs, rp = np.maximum(rs, rp - tol), np.maximum(rp, rs - tol)
            rs, rp = envelope(rs, ds_rim, L_RIM), envelope(rp, ds_rim, L_RIM)
    # --- straps
    imid = int(np.argmin(np.abs(pv - pmid * D2R)))
    A1 = sph(K.s0, K.u0s, K.a1 - (offs[-1] + SP) / R_REF, np.array(pmid * D2R))
    A2 = sph(K.c0, K.u0p, K.a2 - (offs[-1] + SP) / R_REF, np.array(-K.k * pmid * D2R))
    s1, ds1, cs1 = gc_strap(K.b, A1, p["strap_w"], start_mm=HUB_R); s2, ds2, cs2 = gc_strap(A2, K.w2, p["strap_w"], end_mm=HUB_R)
    if s1.shape[0] < 2 or s2.shape[0] < 2: return None
    r1 = Q(req_rigid(R, fit, Rl1, s1.reshape(-1, 3))).reshape(s1.shape[:2]).T              # (nc, ns)
    r2 = Q(req_rigid(R, fit, Rl2, s2.reshape(-1, 3))).reshape(s2.shape[:2]).T
    up1 = math.hypot(F1 + STACK, HUB_R); up3 = math.hypot(F3 + STACK, HUB_R)
    r1[:, 0] = np.maximum(r1[:, 0], up1); r1[:, -1] = np.maximum(r1[:, -1], rs[imid])
    r2[:, 0] = np.maximum(r2[:, 0], rp[imid]); r2[:, -1] = np.maximum(r2[:, -1], up3)
    r1 = envelope(r1, ds1 * R_REF, L_STRAP).T; r2 = envelope(r2, ds2 * R_REF, L_STRAP).T   # (ns, nc)
    # --- neck (humerus frame)
    ub = unit(BAR); nk, dsn, csn = gc_strap(K.Wh, ub, p["neck_w"], start_mm=HUB_R)
    rn = Q(req_rigid(R, fit, Rh, nk.reshape(-1, 3))).reshape(nk.shape[:2]).T
    rn[:, 0] = np.maximum(rn[:, 0], math.hypot(F3, HUB_R)); rn[:, -1] = np.maximum(rn[:, -1], float(np.linalg.norm(BAR)))
    rn = envelope(rn, dsn * R_REF, L_STRAP).T
    M = dict(p=p, kin=kin, F1=F1, F3=F3, off1=off1, off3=off3, pv=pv, offs=offs, sun=sun, pla=pla, rs=rs, rp=rp,
             s1=s1, r1=r1, s2=s2, r2=r2, nk=nk, rn=rn, imid=imid, fit=fit)
    M["mass"] = mass(M); return M


def mass(M):
    p = M["p"]; rho = 4.43e-3                                         # g / mm3
    L1 = M["s1"].shape[0] * SP; L2 = M["s2"].shape[0] * SP; Ln = M["nk"].shape[0] * SP
    rim = 2 * len(M["pv"]) * SP * (RIM_H * RIM_T + p["flange"] * RIM_T)
    straps = (L1 + L2) * p["strap_w"] * p["strap_t"] + Ln * p["neck_w"] * p["neck_t"]
    hubs = 2 * (math.pi * HUB_R ** 2 * 3.0 * 2 + math.pi * HUB_R ** 2 * (HUB_H - 6.15) * 0.5)   # plates + boss/cap (half solid)
    return dict(g=round(rho * (rim + straps + hubs), 1), g_straps_5p5=round(rho * (rim + straps * 5.5 / p["strap_t"] + hubs), 1),
                rim_mm=round(len(M["pv"]) * SP, 1), strap1_mm=L1, strap2_mm=L2, neck_mm=Ln)


def parts_at(M, R, i):
    """per-pose parts: list of (name, group, dirs (n, 3) thorax, foot radius (n,), top radius (n,), hw (n,), record)"""
    p = M["p"]; K = M["kin"]["K"]; RS = R.RS[i]; L1 = RS @ M["kin"]["L1"][i]; L2 = RS @ M["kin"]["L2"][i]; RH = R.RH[i]
    out = []
    P1 = (M["F1"] * K.b + M["off1"]) @ RS.T; d1 = unit(P1); n1 = np.linalg.norm(P1, axis=1)
    out.append(("hub1", "S", d1, n1, n1 + HUB_H, np.full(len(d1), SP / 2), P1))
    P3 = (M["F3"] * K.Wh + M["off3"]) @ RH.T; d3 = unit(P3); n3 = np.linalg.norm(P3, axis=1)
    out.append(("hub3", "H", d3, n3, n3 + HUB_H, np.full(len(d3), SP / 2), P3))
    nr = len(M["offs"])
    for nm, grp, U, rr, Rot in (("sun", "L1", M["sun"], M["rs"], L1), ("planet", "L2", M["pla"], M["rp"], L2)):
        D = (U.reshape(-1, 3) @ Rot.T); r = np.repeat(rr, nr); top = r + np.tile(np.r_[RIM_H, np.full(nr - 1, RIM_T)], len(rr))
        out.append((nm, grp, D, r, top, np.full(len(D), SP / 2), D * r[:, None]))
    for nm, grp, U, rr, Rot, t in (("strap1", "L1", M["s1"], M["r1"], L1, p["strap_t"]), ("strap2", "L2", M["s2"], M["r2"], L2, p["strap_t"]),
                                   ("neck", "H", M["nk"], M["rn"], RH, p["neck_t"])):
        D = U.reshape(-1, 3) @ Rot.T; r = rr.reshape(-1)
        out.append((nm, grp, D, r, r + t, np.full(len(D), SP / 2), D * r[:, None]))
    return out


PAIRS = [("S", "L2", None), ("S", "H", None), ("L1", "H", None), ("L1", "L2", "rim"), ("L2", "H", "J3"), ("S", "L1", "J1")]


def collide(M, R, i, parts):
    """K6 between non-adjacent parts -> list of colliding (part a, part b) names"""
    K = M["kin"]["K"]; RS = R.RS[i]
    ax = dict(J1=RS @ K.b, J3=R.RH[i] @ K.Wh)
    g = RS @ M["kin"]["L1"][i] @ (rotv(K.s0, M["kin"]["psi"][i] * D2R)[0] @ K.g0)
    hits = []
    G = {}
    for nm, grp, D, r0, r1, hw, _ in parts: G.setdefault(grp, []).append((nm, D, r0, r1, hw))
    rmin = min(float(x[2].min()) for v in G.values() for x in v)
    for ga, gb, ex in PAIRS:
        for na, Da, ra0, ra1, ha in G[ga]:
            for nb, Db, rb0, rb1, hb in G[gb]:
                tr = cKDTree(Db); lim = (ha.max() + hb.max() + PART_CLEAR) / rmin
                pr = tr.query_ball_point(Da, lim)
                ia = np.repeat(np.arange(len(Da)), [len(x) for x in pr]); ib = np.fromiter((j for x in pr for j in x), int, len(ia))
                if not len(ia): continue
                ang = np.arccos(np.clip((Da[ia] * Db[ib]).sum(1), -1, 1)); rm = np.minimum(ra0[ia], rb0[ib])
                lat = ang * rm < ha[ia] + hb[ib] + PART_CLEAR
                rad = (ra0[ia] < rb1[ib] + PART_CLEAR) & (rb0[ib] < ra1[ia] + PART_CLEAR)
                c = lat & rad
                if ex in ("J1", "J3"):
                    a_ = ax[ex]; ex_r = (HUB_R + 2) / R_REF
                    c &= ~((np.arccos(np.clip(Da[ia] @ a_, -1, 1)) < ex_r) | (np.arccos(np.clip(Db[ib] @ a_, -1, 1)) < ex_r))
                if ex == "rim" and na == "sun" and nb == "planet":
                    ex_r = 12.0 / R_REF
                    c &= ~((np.arccos(np.clip(Da[ia] @ g, -1, 1)) < ex_r) | (np.arccos(np.clip(Db[ib] @ g, -1, 1)) < ex_r))
                if c.any(): hits.append((na, nb, int(c.sum())))
    return hits


def evaluate(p, B, R=None, log=print, detail=False):
    """build + score one configuration on bench B -> (report dict, model, per-pose info)"""
    R = R or Rig(B); p = {**PARAMS, **p}; t0 = time.time()
    kin = kinematics(p, R); M = build(p, R, kin)
    B.reset()
    info = dict(kin_valid=int(kin["valid"].sum()), cont_fail=int((kin["valid"] & ~kin["cont"]).sum()), coll=0, coll_pairs={})
    if M is None:
        for i in range(R.n): B.record(i, None)
        r = B.report(); r["note"] = "too few closed poses"; return r, None, info
    member_d = {}
    for i in range(R.n):
        if not kin["cont"][i]: B.record(i, None); continue
        parts = parts_at(M, R, i); hits = collide(M, R, i, parts)
        if hits:
            info["coll"] += 1
            for a, b_, n in hits: info["coll_pairs"][f"{a}-{b_}"] = info["coll_pairs"].get(f"{a}-{b_}", 0) + 1
            B.record(i, None); continue
        P = np.concatenate([x[6] for x in parts]); d = B.record(i, P)
        if R.kind[i] == "clip" and d.min() >= 0:
            o = 0
            for x in parts:
                member_d.setdefault(x[0], []).append(d[o:o + len(x[6])]); o += len(x[6])
    r = B.report()
    r["members"] = {k: round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3) for k, v in member_d.items()}
    r["share"] = {k: int(sum(len(x) for x in v)) for k, v in member_d.items()}
    r["window"] = [round(float(kin["seg"][2]), 1), round(float(kin["seg"][3]), 1)]; r["seg"] = kin["seg"][4]
    r["kin_reach"] = round(float(np.mean(kin["valid"][R.kind == "ws"])), 4); r["kin_follow"] = round(float(np.mean(kin["cont"][R.kind == "clip"])), 4)
    r["max_jump"] = round(float(kin["jump"].max()), 1); r["mass"] = M["mass"]; r["F1"] = round(M["F1"], 1); r["F3"] = round(M["F3"], 1)
    r["rim_r"] = [round(float(M["rs"].min()), 1), round(float(M["rs"].max()), 1)]; r.update(info); r["secs"] = round(time.time() - t0, 1)
    return r, M, info


# ------------------------------------------------------------------------------------------------ checks
def check_rolling(p=PARAMS):
    K = Kin(p); out = []
    for psi in (-1.0, -0.3, 0.4, 1.2):
        g = rotv(K.s0, psi)[0] @ K.g0; h = 1e-6
        Mp, Mm = K.M(np.array([psi + h]))[0], K.M(np.array([psi - h]))[0]; M0 = K.M(np.array([psi]))[0]
        x2 = M0.T @ g                                                  # the contact point in link 2 coordinates
        vel = (Mp @ x2 - Mm @ x2) / (2 * h)
        ang = (Mp - Mm) / (2 * h) @ M0.T; om = np.array([ang[2, 1], ang[0, 2], ang[1, 0]])
        on_planet = abs(math.acos(np.clip(x2 @ K.c0, -1, 1)) - K.a2)
        out.append(dict(psi=psi, contact_rel_vel=float(np.linalg.norm(vel)), omega_x_g=float(np.linalg.norm(np.cross(unit(om), g))), on_planet_cone=on_planet))
    return out


def write_sweep(rows):
    os.makedirs(os.path.join(REPO, "docs", "concepts", "sweeps"), exist_ok=True)
    fn = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
    json.dump(rows, open(fn + ".tmp", "w"), indent=0); os.replace(fn + ".tmp", fn)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


SWEEP_KEYS = ("az", "el", "wd", "wa", "a1", "a2", "beta1", "beta2", "gamma", "gamma2", "q", "rim_mode", "flange", "lift", "sing")


def kin_score(p, R):
    """cheap kinematic pre-screen: share of ws / clip poses inside the window, rim span (deg of psi)"""
    K = Kin(p); w = R.HG @ K.Wh; th = np.arccos(np.clip(w @ K.b, -1, 1)) / D2R; seg = K.segment(th)
    inn = (th >= seg[2]) & (th <= seg[3]); ws = R.kind == "ws"
    return float(inn[ws].mean()), float(inn[~ws].mean()), seg[4]["psi_hi"] - seg[4]["psi_lo"]


def row_of(k, p, r):
    return dict(k=k, t=now(), params={kk: p[kk] for kk in SWEEP_KEYS}, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                follow=r["follow"], contact=r["contact"], gap=r["gap"],
                extra=dict(kin_reach=r.get("kin_reach"), kin_follow=r.get("kin_follow"), coll=r.get("coll"), window=r.get("window"),
                           members=r.get("members"), mass_g=(r.get("mass") or {}).get("g"), rim_mm=(r.get("mass") or {}).get("rim_mm"), secs=r.get("secs")))


def run_sweep(B, log=print, budget=150):
    """coarse (kinematic pre-screen -> geometry on the best), then variants (q, rim mode, flange), then a local refine"""
    import itertools, random
    R = Rig(B); rows = []; rng = random.Random(1)
    def ev(p, tag):
        p = {**PARAMS, **p}; r, M, info = evaluate(p, B, R); rows.append(row_of(len(rows), p, r)); write_sweep(rows)
        log(f"[{len(rows)}] {tag} gap {r['gap']} reach {r['reach']} follow {r['follow']} in14 {r['inband14']} in10 {r['inband10']} contact {r['contact']}"
            f" | kin {r.get('kin_reach')}/{r.get('kin_follow')} coll {r.get('coll')} {r.get('coll_pairs')} win {r.get('window')} mem {r.get('members')} {r.get('secs')} s", flush=True) if log is print else log(r)
        return r
    # stage A: kinematic pre-screen over axes x cones
    axes = [dict(az=2.43, el=80.68, wd=86.33, wa=21.83)] + [dict(az=a, el=e, wd=d, wa=w) for a, e, d, w in AXES_EXTRA]
    cand = []
    for ax in axes:
        for a1, a2, b1, b2, g, g2 in itertools.product((35, 45, 55), (35, 45, 55), (20, 30, 40), (20, 30, 40), range(-180, 180, 60), range(-180, 180, 60)):
            if b1 > a1 - 9 or b2 > a2 - 9: continue
            p = dict(ax, a1=a1, a2=a2, beta1=b1, beta2=b2, gamma=g, gamma2=g2); kr, kf, span = kin_score({**PARAMS, **p}, R)
            cand.append((min(kr, .92) + min(kf, .97) - 0.0004 * span * math.sin(a1 * D2R), p, kr, kf, span))
    cand.sort(key=lambda c: -c[0]); seen = []
    picks = []
    for c in cand:                                                    # diverse: skip near-duplicates
        key = (c[1]["az"], c[1]["el"], c[1]["a1"], c[1]["a2"], c[1]["beta1"], c[1]["beta2"])
        if seen.count(key) >= 2: continue
        seen.append(key); picks.append(c)
        if len(picks) >= 40: break
    log(f"stage A: {len(cand)} kinematic candidates, geometry on {len(picks)}")
    resA = [(ev(c[1], f"A kin {c[2]:.3f}/{c[3]:.3f} span {c[4]:.0f} {c[1]}"), c[1]) for c in picks]
    resA.sort(key=lambda x: x[0]["gap"])
    # stage B: variants on the best 5
    resB = []
    for r0, p0 in resA[:5]:
        for var in (dict(q=0.97), dict(q=0.93), dict(rim_mode="const"), dict(flange=4.0), dict(sing=7.0)):
            resB.append((ev({**p0, **var}, f"B {var} of gap {r0['gap']}"), {**p0, **var}))
    allr = sorted(resA + resB, key=lambda x: x[0]["gap"])
    # stage C: local refine (random perturbations around the current best)
    best_r, best_p = allr[0]
    while len(rows) < budget:
        p = dict(best_p)
        for kk, sd in (("a1", 4), ("a2", 4), ("beta1", 4), ("beta2", 4), ("gamma", 12), ("gamma2", 12), ("az", 8), ("el", 5), ("wd", 5), ("wa", 8)):
            if rng.random() < 0.4: p[kk] = round(p[kk] + rng.gauss(0, sd), 1)
        if rng.random() < 0.2: p["q"] = rng.choice((1.0, 0.97, 0.93))
        if p["beta1"] > p["a1"] - 9 or p["beta2"] > p["a2"] - 9 or min(p["beta1"], p["beta2"]) < 5: continue
        r = ev(p, "C")
        if r["gap"] < best_r["gap"]: best_r, best_p = r, p
    return rows, best_r, best_p


AXES_EXTRA = []


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        print("rolling check:", check_rolling())
        B = CB.Bench(nc, nw); print(B.mode); R = Rig(B)
        r, M, info = evaluate({}, B, R); print(json.dumps(r, default=str))
    elif a and a[0] == "kin":
        B = CB.Bench(60, 160); R = Rig(B)
        print(kin_score(dict(PARAMS), R))
    elif a and a[0] == "sweep":
        B = CB.Bench(60, 160); print(B.mode, flush=True)
        rows, best_r, best_p = run_sweep(B, budget=int(a[1]) if len(a) > 1 else 150)
        print("BEST", best_p, json.dumps(best_r, default=str))
