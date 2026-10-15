"""rolling-elbow-fivebar: a closed spherical five-bar (two legs from the scapula to one arm hub at the arm-fixed axis W)
plus an active roll about W, whose two elbows are hubless rolling-contact joints (Jacob's-ladder discs held by crossed
flexure straps). Concept screen on tools/concept_bench.py, idealised geometry at real part sizes.

Topology (docs/concepts/catalogue.json, id rolling-elbow-fivebar):
  leg k (k = 1, 2): S --A_k (ACTIVE, O20 hub, axis u_k fixed in the scapula)--> crank k = strap + edge disc (spherical
  cap of angular radius rho1 about c1k, fixed in the crank) ==rolling contact (no hub)== coupler k = edge disc (rho2
  about c2k) + strap --C (passive, axis W)--> arm hub. Coupler 1 --D (ACTIVE roll about W)--> arm-end plate --neck-->
  BOTTOM's bar. Joints: A1, A2, D active; C and the two rolling elbows passive (6 joints, mobility 3).
DOF: each rolling elbow is a 1-DOF spherical joint: coupler relative to crank M(psi) = R(c1, psi) R(c2_0, k psi),
k = sin rho1 / sin rho2 (no-slip: checked numerically in `check`). Given the arm pose, W is known; each leg's
(theta_k, psi_k) puts the coupler's W on the arm's W (2 equations, 2 unknowns, one monotone branch per design) and C, D
follow. Every passive coordinate is set by closure; nothing can sag.

Leg geometry (all axes through GH; angles in deg): crank arc a = u -> far rim point of the crank disc
(angle(u, c1) = a - rho1); contact at reference = the rim point between c1 and c2 (angle(c1, c2) = rho1 + rho2);
coupler arc c = near rim point -> W (angle(c2, W) = c - rho2). psi = 0 is the STRAIGHT leg (u, c1, c2, W on one great
circle), so angle(u, W) = a + c there (stationary, the stretch singularity); the leg bends to side sigma = sign(psi).
IK: f(psi) = angle(u, M(psi) W0) on a 0.5 deg grid on side sigma; the design's branch is the monotone run of f
holding the most target poses; its stationary ends (straight / antipode corner / fold) keep `sing` deg of f away, the
strap-wrap end |psi| = psi_max (120) is a hard stop. psi by bisection (residual < 1e-6 deg), theta = azimuth about u.
Taken pose (else None): both legs inside their windows; loop (parallel) singularity margin: n_k = unit(g_k x W) with
g_k the CONTACT generator (SPEC FIX: the spec writes c2k' x W; a rolling contact is instantaneously a pin at the
contact point, so the coupler is a two-force member g_k -> W), |n1 x n2| >= sin(par); contact generators >= sep deg
apart; along each clip the arm path between consecutive bench frames (12 slerp sub-steps) stays in both windows and the
margins with no joint step > 25 deg (A1, A2, psi1, psi2, C, D); no two non-adjacent parts within 1 mm (K6); no metal
inside the body (bench contact).

Geometry (mm, thorax frame of the bench, origin GH; every part at its real size, skin-facing undersides sampled on a
2 mm grid at r_ref 70 mm as tools/concept_baseline.py):
  * base hubs (O20 v5, docs/HARDWARE.md): 10 mm discs normal to u_k, lower face F_k = max over disc samples and fit
    poses of the K3 requirement projected on the axis; stack [F, F + 12.25]; crank underside F + 3.15. Coaxial option
    (coax=1): one double-row hub r 12, crank 1 at F + 3.15, crank 2 at F + 7.15, crown F + 16.
  * arm hub at W (fixed in the humerus): disc r 12, two bearing rows: arm-end plate [F_W, F_W + 3], coupler 1 underside
    F_W + 4, coupler 2 underside F_W + 8, crown F_W + 16.
  * straps 12 x 3 mm (K5) on great circles: crank u_k -> disc boundary, coupler disc boundary -> W hub edge; K3
    underside (q-quantile over fit poses), anchored at the hub level and the disc level, climbing at most 60 deg.
  * edge discs: 4 mm plates, spherical caps of angular radius rho1 / rho2 (the rolling faces are their 4 mm cone
    edges). Both discs of an elbow share ONE constant radius r_e (max K3 requirement over both discs and the fit
    poses), so the rolling faces always overlap over their full 4 mm (disc_mode 'const'); disc_mode 'split' lets each
    disc keep its own level within 2 mm of the other (>= 2 mm of rolling face engaged). Straps (0.1 mm) ignored.
  * neck (K7): 14 x 6 mm strap fixed in the humerus from the arm hub edge (level F_W) to BOTTOM's bar top
    (67.5 Wb + 40 Db, Wb = (0, -0.0713, 0.9975), Db = (0, -0.9975, -0.0713), humerus frame).
  * K3 requirement r_i(d): first t >= 15 mm along d with signed distance >= 2 mm and >= 0 over [t, t + 15].
Frames: humerus directions use the evaluator's humerus frame HG of the pose file (as tools/concept_baseline.py; the
thorax direction of a humerus vector v is RS HG v).

    python3 docs/concepts/models/rolling-elbow-fivebar.py check [n_clip n_ws]   # no-slip check + a few poses
    python3 docs/concepts/models/rolling-elbow-fivebar.py kin                   # kinematic screen (no distances)
    python3 docs/concepts/models/rolling-elbow-fivebar.py sweep [budget]        # the sweep (sweeps/, rows/)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                        # noqa: E402

ID = "rolling-elbow-fivebar"
D2R = math.pi / 180
HUB_R, HUB_H, STACK = 10.0, 12.25, 3.15                           # O20 v5
HUB_W_R, HUB_W_H, CPL_STEP = 12.0, 16.0, 4.0                      # two-row hubs (arm hub, coaxial base)
R_REF = 70.0                                                      # mm -> rad for sample spacing (as the baseline)
SP = 2.0                                                          # 2 mm grid = 1 point / 4 mm2
DISC_T = 4.0
L_STRAP = math.tan(60 * D2R)                                      # max climb along straps
PART_CLEAR = 1.0
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713]); BAR = 67.5 * WB + 40.0 * DB

PARAMS = dict(b1az=-60.0, b1el=40.0, b2az=-40.0, b2el=40.0, coax=0,  # base axes u1, u2 (scapula frame)
              a1=60.0, a2=60.0, c1=120.0, c2=120.0,                 # crank / coupler arcs (deg)
              rho=10.0, ratio=1.0,                                  # crank edge radius rho1 = rho, coupler rho2 = rho * ratio
              wd=71.38, wa=4.78,                                    # arm axis W (humerus frame, wdir)
              s1=1, s2=-1,                                          # elbow sides (branches)
              sing=8.0, par=12.0, sep=17.0, psi_max=120.0,
              q=1.0, disc_mode="const", strap_w=12.0, strap_t=3.0, neck_w=14.0, neck_t=6.0)
SWEEP = dict(b1az=(-90, 180), b1el=(35, 75), b2az=(-90, 180), b2el=(35, 75), coax=(0, 1), a1=(40, 70), a2=(40, 70),
             c1=(50, 130), c2=(50, 130), rho=(6, 15), ratio=(0.7, 1.4), wd=(60, 115), wa=(-60, 20), s1=(-1, 1), s2=(-1, 1),
             par=(8, 15), q=(0.93, 1.0), disc_mode=("const", "split"))
SWEEP_KEYS = ("b1az", "b1el", "b2az", "b2el", "coax", "a1", "a2", "c1", "c2", "rho", "ratio", "wd", "wa", "s1", "s2", "sing", "par", "q", "disc_mode")


def unit(v):
    v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, a):
    return np.array([math.sin(d * D2R) * math.sin(a * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(a * D2R)])


def rotv(ax, ang):
    """Rodrigues: rotations about unit axis ax (3,) by angles ang (n,) rad -> (n, 3, 3)"""
    ang = np.atleast_1d(np.asarray(ang, float)); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    s, c = np.sin(ang)[:, None, None], np.cos(ang)[:, None, None]
    return np.eye(3)[None] + s * K[None] + (1 - c) * (K @ K)[None]


def perp(u, ref=np.array([0.0, 0.0, 1.0])):
    p = ref - (ref @ u) * u
    if np.linalg.norm(p) < 1e-6: p = np.array([1.0, 0.0, 0.0]) - u[0] * u
    return unit(p)


def sang(a, b, ax):
    """signed angle (rad) from a to b about ax, all (n, 3) (projected on the plane normal to ax)"""
    ap = a - (a * ax).sum(-1, keepdims=True) * ax; bp = b - (b * ax).sum(-1, keepdims=True) * ax
    return np.arctan2((np.cross(ap, bp) * ax).sum(-1), (ap * bp).sum(-1))


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
        self.prev = {}
        for c, js in self.order.items():
            for a, b in zip(js[:-1], js[1:]): self.prev[b] = a
        self.trans = sorted(self.prev.items())                         # (frame b, previous frame a)
        ts = np.linspace(0, 1, 13)[1:-1]                               # 11 sub-step HG between consecutive clip frames
        self.SUB = np.concatenate([Slerp([0, 1], Rotation.from_matrix(self.HG[[a, b]]))(ts).as_matrix() for b, a in self.trans]) if self.trans else np.zeros((0, 3, 3))
        self.nsub = len(ts)


# ------------------------------------------------------------------------------------------------ kinematics
class Leg:
    """one leg in the scapula frame; crank frame at theta = 0 = scapula frame; coupler frame at psi = 0 = crank frame"""
    def __init__(self, u, a, c, rho1, rho2, sigma, psi_max, sing):
        self.u = u; e = perp(u, np.array([1.0, 0.0, 0.0])); self.e = e
        self.rho1, self.rho2 = rho1 * D2R, rho2 * D2R; self.k = math.sin(self.rho1) / math.sin(self.rho2)
        gc = lambda s: math.cos(s * D2R) * u + math.sin(s * D2R) * e
        self.a, self.c = a * D2R, c * D2R
        self.c1 = gc(a - rho1); self.g0 = gc(a); self.c2 = gc(a + rho2); self.W0 = gc(a + c)
        self.t0 = unit(self.c2 - (self.c2 @ self.W0) * self.W0)          # coupler's tangent at W toward its disc
        self.sigma = 1.0 if sigma >= 0 else -1.0; self.psi_max = psi_max; self.sing = sing

    def M(self, psi):
        """coupler -> crank rotation (n, 3, 3), psi rad (n,)"""
        psi = np.atleast_1d(np.asarray(psi, float)); return rotv(self.c1, psi) @ rotv(self.c2, self.k * psi)

    def f(self, psi):
        v = self.M(psi) @ self.W0; return np.arccos(np.clip(v @ self.u, -1, 1)) / D2R

    def segment(self, T):
        """monotone run of f(psi) on side sigma holding most targets T (deg) -> (psi grid deg, f grid, lo, hi, info)"""
        pg = self.sigma * np.arange(0.0, self.psi_max + 1e-9, 0.5); fg = self.f(pg * D2R)
        d = np.diff(fg); sg = np.sign(d); sg[sg == 0] = 1
        runs = []; j0 = 0
        for j in range(1, len(d) + 1):
            if j == len(d) or sg[j] != sg[j0]: runs.append((j0, j)); j0 = j
        best = None
        for j0, j1 in runs:                                           # grid points j0..j1
            lo_e, hi_e = (j0, j1) if fg[j1] >= fg[j0] else (j1, j0)  # indices of the low / high f end
            stat = lambda j: j != len(fg) - 1                          # every run end but the strap-wrap limit is singular
            lo = fg[lo_e] + (self.sing if stat(lo_e) else 0.0); hi = fg[hi_e] - (self.sing if stat(hi_e) else 0.0)
            if hi <= lo: continue
            sc = float(np.mean((T >= lo) & (T <= hi))) if T is not None else hi - lo
            if best is None or sc > best[0]: best = (sc, j0, j1, lo, hi)
        if best is None: return None
        _, j0, j1, lo, hi = best
        ps, fs = pg[j0:j1 + 1], fg[j0:j1 + 1]
        if fs[-1] < fs[0]: ps, fs = ps[::-1], fs[::-1]
        return ps, fs, lo, hi, dict(psi=[float(pg[j0]), float(pg[j1])], f=[float(fg[j0]), float(fg[j1])])

    def solve(self, T, seg):
        """psi (deg) on the branch for each target angle T (deg) inside the window; nan outside"""
        ps, fs, lo, hi, _ = seg; T = np.asarray(T, float); out = np.full(T.shape, np.nan)
        ok = (T >= lo) & (T <= hi)
        if not ok.any(): return out
        j = np.clip(np.searchsorted(fs, T[ok]) - 1, 0, len(fs) - 2)
        a, b = ps[j].copy(), ps[j + 1].copy(); fa = fs[j]; tt = T[ok]
        for _ in range(36):
            m = 0.5 * (a + b); fm = self.f(m * D2R); left = (fm - tt) < 0
            a = np.where(left, m, a); b = np.where(left, b, m)
        out[ok] = 0.5 * (a + b); return out

    def joints(self, w, psi):
        """w (n, 3) arm axis in the scapula frame, psi (deg) -> theta (rad), crank Rk, coupler Rc (scapula), contact g,
        coupler tangent at W, residual (deg)"""
        Mp = self.M(np.nan_to_num(psi) * D2R); v = Mp @ self.W0
        uu = np.broadcast_to(self.u, v.shape); th = sang(v, w, uu)
        Rk = rotv(self.u, th); Rc = Rk @ Mp
        res = np.arccos(np.clip(((Rc @ self.W0) * w).sum(1), -1, 1)) / D2R
        g = np.einsum("nij,nj->ni", Rk, rotv(self.c1, np.nan_to_num(psi) * D2R) @ self.g0)
        return th, Rk, Rc, g, Rc @ self.t0, res


class Kin:
    def __init__(self, p):
        self.p = p; u1 = bvec(p["b1az"], p["b1el"]); u2 = u1 if p["coax"] else bvec(p["b2az"], p["b2el"])
        r1, r2 = p["rho"], p["rho"] * p["ratio"]
        self.legs = [Leg(u1, p["a1"], p["c1"], r1, r2, p["s1"], p["psi_max"], p["sing"]),
                     Leg(u2, p["a2"], p["c2"], r1, r2, p["s2"], p["psi_max"], p["sing"])]
        self.Wh = wdir(p["wd"], p["wa"]); self.rh = perp(self.Wh)


def leg_state(K, HG, segs):
    """per-pose state for arm rotations HG (n, 3, 3): dict of legs' psi / theta / Rk / Rc / g / t, C, D, ok, margins"""
    w = HG @ K.Wh; out = dict(w=w, legs=[]); ok = np.ones(len(HG), bool)
    for L, seg in zip(K.legs, segs):
        T = np.arccos(np.clip(w @ L.u, -1, 1)) / D2R
        psi = L.solve(T, seg) if seg is not None else np.full(len(w), np.nan)
        th, Rk, Rc, g, t, res = L.joints(w, psi)
        good = np.isfinite(psi) & (res < 0.5); ok &= good
        out["legs"].append(dict(T=T, psi=psi, th=th, Rk=Rk, Rc=Rc, g=g, t=t, res=res))
    l1, l2 = out["legs"]
    n1 = unit(np.cross(l1["g"], w)); n2 = unit(np.cross(l2["g"], w))
    par = np.arcsin(np.clip(np.linalg.norm(np.cross(n1, n2), axis=1), 0, 1)) / D2R
    sep = np.arccos(np.clip((l1["g"] * l2["g"]).sum(1), -1, 1)) / D2R
    h = HG @ K.rh
    out["C"] = sang(l1["t"], l2["t"], w); out["D"] = sang(l1["t"], h, w)
    out["par"] = par; out["sep"] = sep
    ok &= (par >= K.p["par"]) & (sep >= K.p["sep"]); out["ok"] = ok
    return out


def kinematics(p, R):
    """per-pose closure: valid mask + joint values; continuity along the clips (sub-steps between frames)"""
    K = Kin(p); w = R.HG @ K.Wh
    segs = [L.segment(np.arccos(np.clip(w @ L.u, -1, 1)) / D2R) for L in K.legs]
    S = leg_state(K, R.HG, segs); valid = S["ok"].copy()
    cont = valid.copy(); jump = np.zeros(R.n)
    q = lambda st: np.c_[st["legs"][0]["th"], st["legs"][1]["th"], st["legs"][0]["psi"] * D2R, st["legs"][1]["psi"] * D2R, st["C"], st["D"]]
    Qall = q(S)
    if len(R.trans):
        Ss = leg_state(K, R.SUB, segs); oks = Ss["ok"].reshape(len(R.trans), R.nsub); Qs = q(Ss).reshape(len(R.trans), R.nsub, -1)
        for t, (b_, a_) in enumerate(R.trans):
            if not valid[b_] or not valid[a_]: continue               # previous frame not taken: re-entry on the unique branch
            if not oks[t].all(): cont[b_] = False; continue           # the arm path leaves the window / margins
            Qp = np.r_[Qall[a_][None], Qs[t], Qall[b_][None]]
            st = np.abs((np.diff(Qp, axis=0) + math.pi) % (2 * math.pi) - math.pi).max() / D2R; jump[b_] = st
            if st > 25: cont[b_] = False
    return dict(K=K, segs=segs, S=S, valid=valid, cont=cont, jump=jump)


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
    a0, a1 = start_mm / R_REF, ang - end_mm / R_REF
    if a1 <= a0 + 1e-6: a1 = a0 + 1e-3
    ns = max(2, int((a1 - a0) * R_REF / SP) + 1)
    th = np.linspace(a0, a1, ns); D = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    cs = np.arange(-width / 2 + SP / 2, width / 2, SP)
    out = unit(D[:, None, :] * np.cos(cs / R_REF)[None, :, None] + nrm[None, None, :] * np.sin(cs / R_REF)[None, :, None])
    return out, (a1 - a0) / max(ns - 1, 1), cs


def disc_off(axis, rad_mm):
    g = np.arange(-rad_mm + 1, rad_mm, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= rad_mm ** 2
    e1 = perp(axis); e2 = np.cross(axis, e1)
    return X[m][:, None] * e1 + Y[m][:, None] * e2                    # in-plane offsets (m, 3) mm


def cap_dirs(axis, ang):
    """directions of a spherical cap of angular radius ang (rad) about axis, 2 mm grid at r_ref"""
    R = R_REF * math.tan(ang); g = np.arange(-R + SP / 2, R, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= R ** 2
    e1 = perp(axis); e2 = np.cross(axis, e1)
    return unit(R_REF * axis + X[m][:, None] * e1 + Y[m][:, None] * e2)


def req_rigid(R, fit, Rot, U):
    """K3 requirement of directions U (m, 3) fixed in a member with thorax rotations Rot (n, 3, 3), fit poses -> (n_fit, m)"""
    D = np.einsum("pij,mj->pmi", Rot[fit], U).reshape(-1, 3); I = np.repeat(fit, len(U))
    return R.F.requirement(I, D).reshape(len(fit), len(U))


def hub_level(R, fit, Rot, axis, rad):
    off = disc_off(axis, rad); U = unit(R_REF * axis + off); r = req_rigid(R, fit, Rot, U)
    return float((r * (U @ axis)[None]).max()), off


def build(p, R, kin):
    """fit every part over the closed poses; returns the model dict"""
    K = kin["K"]; fit = np.nonzero(kin["valid"])[0]
    if len(fit) < 10: return None
    q = p["q"]; Q = lambda r: np.quantile(r, q, axis=0) if q < 1 else r.max(0)
    RS = R.RS; Rh = R.RH; S = kin["S"]; M = dict(p=p, kin=kin, fit=fit, legs=[])
    # --- hubs
    if p["coax"]:
        F, off = hub_level(R, fit, RS, K.legs[0].u, HUB_W_R); Fb = [F, F]; offb = [off, None]
        lvl = [F + STACK, F + STACK + CPL_STEP]
    else:
        Fb, offb = zip(*[hub_level(R, fit, RS, L.u, HUB_R) for L in K.legs]); lvl = [f + STACK for f in Fb]
    FW, offW = hub_level(R, fit, Rh, K.Wh, HUB_W_R)
    M.update(Fb=list(Fb), offb=list(offb), FW=FW, offW=offW)
    hb_r = HUB_W_R if p["coax"] else HUB_R
    for k, L in enumerate(K.legs):
        st = S["legs"][k]; Rk = RS @ st["Rk"]; Rc = RS @ st["Rc"]
        dk = cap_dirs(L.c1, L.rho1); dc = cap_dirs(L.c2, L.rho2)
        rk = Q(req_rigid(R, fit, Rk, dk)); rc = Q(req_rigid(R, fit, Rc, dc))
        if p["disc_mode"] == "split":
            ek, ec = float(rk.max()), float(rc.max()); ek, ec = max(ek, ec - 2.0), max(ec, ek - 2.0)
        else:
            ek = ec = float(max(rk.max(), rc.max()))
        # crank strap: hub -> disc boundary
        s1, ds1, _ = gc_strap(L.u, L.c1, p["strap_w"], start_mm=hb_r, end_mm=L.rho1 * R_REF)
        r1 = Q(req_rigid(R, fit, Rk, s1.reshape(-1, 3))).reshape(s1.shape[:2]).T     # (nc, ns)
        r1[:, 0] = np.maximum(r1[:, 0], math.hypot(lvl[k], hb_r)); r1[:, -1] = np.maximum(r1[:, -1], ek)
        r1 = envelope(r1, ds1 * R_REF, L_STRAP).T
        # coupler strap: disc boundary -> arm hub edge
        s2, ds2, _ = gc_strap(L.c2, L.W0, p["strap_w"], start_mm=L.rho2 * R_REF, end_mm=HUB_W_R)
        r2 = Q(req_rigid(R, fit, Rc, s2.reshape(-1, 3))).reshape(s2.shape[:2]).T
        r2[:, 0] = np.maximum(r2[:, 0], ec); r2[:, -1] = np.maximum(r2[:, -1], math.hypot(FW + CPL_STEP * (k + 1), HUB_W_R))
        r2 = envelope(r2, ds2 * R_REF, L_STRAP).T
        M["legs"].append(dict(dk=dk, dc=dc, ek=ek, ec=ec, s1=s1, r1=r1, s2=s2, r2=r2, rk_need=float(rk.max()), rc_need=float(rc.max())))
    # --- neck (humerus frame)
    ub = unit(BAR); nk, dsn, _ = gc_strap(K.Wh, ub, p["neck_w"], start_mm=HUB_W_R)
    rn = Q(req_rigid(R, fit, Rh, nk.reshape(-1, 3))).reshape(nk.shape[:2]).T
    rn[:, 0] = np.maximum(rn[:, 0], math.hypot(FW, HUB_W_R)); rn[:, -1] = np.maximum(rn[:, -1], float(np.linalg.norm(BAR)))
    M["nk"] = nk; M["rn"] = envelope(rn, dsn * R_REF, L_STRAP).T
    M["mass"] = mass(M); return M


def mass(M):
    p = M["p"]; rho = 4.43e-3                                         # Ti, g / mm3
    vol = 0.0; strap_vol = 0.0
    for lg in M["legs"]:
        for s, r in ((lg["s1"], lg["r1"]), (lg["s2"], lg["r2"])):
            strap_vol += s.shape[0] * s.shape[1] * SP * SP * (r.mean() / R_REF) ** 2 * p["strap_t"]
        for d, e in ((lg["dk"], lg["ek"]), (lg["dc"], lg["ec"])):
            vol += len(d) * SP * SP * (e / R_REF) ** 2 * DISC_T
    nk = M["nk"]; vol += nk.shape[0] * nk.shape[1] * SP * SP * (M["rn"].mean() / R_REF) ** 2 * p["neck_t"]
    nb = 1 if p["coax"] else 2
    hubs = nb * math.pi * HUB_R ** 2 * 6.0 + math.pi * HUB_R ** 2 * (HUB_H - 6.15) * 0.5 * nb + math.pi * HUB_W_R ** 2 * (9.0 + 4.0)
    return dict(g=round(rho * (vol + strap_vol + hubs), 1), g_straps_5p5=round(rho * (vol + strap_vol * 5.5 / p["strap_t"] + hubs), 1))


def parts_at(M, R, i):
    """per-pose parts: list of (name, group, dirs (n, 3), foot radius (n,), top radius (n,), points (n, 3))"""
    p = M["p"]; K = M["kin"]["K"]; S = M["kin"]["S"]; RS = R.RS[i]; RH = R.RH[i]; out = []
    if p["coax"]:
        P = (M["Fb"][0] * K.legs[0].u + M["offb"][0]) @ RS.T; n = np.linalg.norm(P, axis=1)
        out.append(("hub_b", "S", unit(P), n, n + HUB_W_H, P))
    else:
        for k in range(2):
            P = (M["Fb"][k] * K.legs[k].u + M["offb"][k]) @ RS.T; n = np.linalg.norm(P, axis=1)
            out.append((f"hub{k + 1}", "S", unit(P), n, n + HUB_H, P))
    P = (M["FW"] * K.Wh + M["offW"]) @ RH.T; n = np.linalg.norm(P, axis=1)
    out.append(("hubW", "A", unit(P), n, n + HUB_W_H, P))
    for k, lg in enumerate(M["legs"]):
        st = S["legs"][k]; Rk = RS @ st["Rk"][i]; Rc = RS @ st["Rc"][i]
        for nm, grp, U, r, Rot, t in ((f"crank{k + 1}", f"K{k + 1}", lg["s1"].reshape(-1, 3), lg["r1"].reshape(-1), Rk, p["strap_t"]),
                                      (f"disc_k{k + 1}", f"K{k + 1}", lg["dk"], np.full(len(lg["dk"]), lg["ek"]), Rk, DISC_T),
                                      (f"disc_c{k + 1}", f"C{k + 1}", lg["dc"], np.full(len(lg["dc"]), lg["ec"]), Rc, DISC_T),
                                      (f"coupler{k + 1}", f"C{k + 1}", lg["s2"].reshape(-1, 3), lg["r2"].reshape(-1), Rc, p["strap_t"])):
            D = U @ Rot.T; out.append((nm, grp, D, r, r + t, D * r[:, None]))
    D = M["nk"].reshape(-1, 3) @ RH.T; r = M["rn"].reshape(-1)
    out.append(("neck", "A", D, r, r + p["neck_t"], D * r[:, None]))
    return out


GROUPS = ("S", "K1", "K2", "C1", "C2", "A")


def collide(M, R, i, parts):
    """K6 between parts of different bodies, joint partners exempt near their joint -> list of (part a, part b, n)"""
    p = M["p"]; K = M["kin"]["K"]; RS = R.RS[i]; RH = R.RH[i]
    ub = [RS @ L.u for L in K.legs]; wW = RH @ K.Wh
    hb_r = HUB_W_R if p["coax"] else HUB_R
    exb = [math.atan((hb_r + 2) / M["Fb"][k]) for k in range(2)]; exW = math.atan((HUB_W_R + 2) / M["FW"])
    ex = {("S", "K1"): [(ub[0], exb[0])], ("S", "K2"): [(ub[1], exb[1])], ("C1", "A"): [(wW, exW)], ("C2", "A"): [(wW, exW)],
          ("C1", "C2"): [(wW, exW)], ("K1", "C1"): [], ("K2", "C2"): []}
    if p["coax"]: ex[("K1", "K2")] = [(ub[0], exb[0])]
    G = {}
    for nm, grp, D, r0, r1, _ in parts: G.setdefault(grp, []).append((nm, D, r0, r1))
    rmin = min(float(x[2].min()) for v in G.values() for x in v)
    hits = []
    for ia_, ga in enumerate(GROUPS):
        for gb in GROUPS[ia_ + 1:]:
            exr = ex.get((ga, gb), None)
            for na, Da, ra0, ra1 in G[ga]:
                for nb, Db, rb0, rb1 in G[gb]:
                    if na.startswith("disc_") and nb.startswith("disc_") and na[-1] == nb[-1] and exr is not None: continue   # rolling pair
                    tr = cKDTree(Db); lim = (SP + PART_CLEAR) / rmin * 1.05
                    pr = tr.query_ball_point(Da, lim)
                    ia = np.repeat(np.arange(len(Da)), [len(x) for x in pr])
                    if not len(ia): continue
                    ib = np.fromiter((j for x in pr for j in x), int, len(ia))
                    ang = np.arccos(np.clip((Da[ia] * Db[ib]).sum(1), -1, 1)); rm = np.minimum(ra0[ia], rb0[ib])
                    c = (ang * rm < SP + PART_CLEAR) & (ra0[ia] < rb1[ib] + PART_CLEAR) & (rb0[ib] < ra1[ia] + PART_CLEAR)
                    for ax, er in (exr or []):
                        c &= ~((Da[ia] @ ax > math.cos(er)) | (Db[ib] @ ax > math.cos(er)))
                    if c.any(): hits.append((na, nb, int(c.sum())))
    return hits


def evaluate(p, B, R=None, log=print):
    """build + score one configuration on bench B -> (report dict, model)"""
    R = R or Rig(B); p = {**PARAMS, **p}; t0 = time.time()
    kin = kinematics(p, R); M = build(p, R, kin)
    B.reset()
    info = dict(kin_valid=int(kin["valid"].sum()), cont_fail=int((kin["valid"] & ~kin["cont"]).sum()), coll=0, coll_pairs={})
    if M is None:
        for i in range(R.n): B.record(i, None)
        r = B.report(); r["note"] = "too few closed poses"; r.update(info); return r, None
    member_d = {}; taken = np.zeros(R.n, bool)
    for i in range(R.n):
        if not kin["cont"][i]: B.record(i, None); continue
        parts = parts_at(M, R, i); hits = collide(M, R, i, parts)
        if hits:
            info["coll"] += 1
            for a, b_, n in hits: info["coll_pairs"][f"{a}-{b_}"] = info["coll_pairs"].get(f"{a}-{b_}", 0) + 1
            B.record(i, None); continue
        P = np.concatenate([x[5] for x in parts]); d = B.record(i, P); taken[i] = d.min() >= 0
        if R.kind[i] == "clip" and d.min() >= 0:
            o = 0
            for x in parts:
                member_d.setdefault(x[0], []).append(d[o:o + len(x[5])]); o += len(x[5])
    r = B.report()
    cat = lambda v: np.concatenate(v)
    r["members"] = {k: round(float(np.mean((cat(v) >= 2) & (cat(v) <= 14))), 3) for k, v in member_d.items()}
    el = [x for k, v in member_d.items() if k.startswith("disc_") for x in v]
    r["elbow_inband14"] = round(float(np.mean((cat(el) >= 2) & (cat(el) <= 14))), 4) if el else None
    r["elbow_inband10"] = round(float(np.mean((cat(el) >= 2) & (cat(el) <= 10))), 4) if el else None
    tot = sum(int(sum(len(x) for x in v)) for v in member_d.values()) or 1
    r["share"] = {k: round(sum(len(x) for x in v) / tot, 3) for k, v in member_d.items()}
    kk = kin["K"]; seg = kin["segs"]
    r["windows"] = [None if s is None else [round(float(s[2]), 1), round(float(s[3]), 1)] for s in seg]
    r["kin_reach"] = round(float(np.mean(kin["valid"][R.kind == "ws"])), 4); r["kin_follow"] = round(float(np.mean(kin["cont"][R.kind == "clip"])), 4)
    r["max_jump"] = round(float(kin["jump"].max()), 1); r["mass"] = M["mass"]
    r["Fb"] = [round(x, 1) for x in M["Fb"]]; r["FW"] = round(M["FW"], 1)
    r["r_e"] = [[round(lg["ek"], 1), round(lg["ec"], 1)] for lg in M["legs"]]
    vp = kin["valid"]; r["psi_range"] = [[round(float(np.nanmin(st["psi"][vp])), 1), round(float(np.nanmax(st["psi"][vp])), 1)] for st in kin["S"]["legs"]] if vp.any() else None
    r.update(info); r["secs"] = round(time.time() - t0, 1); r["taken"] = taken
    return r, M


# ------------------------------------------------------------------------------------------------ checks
def check_rolling(p=PARAMS):
    """no-slip: the coupler material point at the contact has zero velocity relative to the crank; the contact stays
    on both rims"""
    K = Kin({**PARAMS, **p}); out = []
    for L in K.legs:
        for psi in (-1.5, -0.4, 0.3, 1.1):
            h = 1e-6; M0 = L.M(psi)[0]; Mp = L.M(psi + h)[0]; Mm = L.M(psi - h)[0]
            g = rotv(L.c1, psi)[0] @ L.g0; x2 = M0.T @ g
            vel = (Mp @ x2 - Mm @ x2) / (2 * h)
            out.append(dict(psi=psi, contact_rel_vel=float(np.linalg.norm(vel)),
                            on_crank_rim=float(abs(math.acos(np.clip(g @ L.c1, -1, 1)) - L.rho1)),
                            on_coupler_rim=float(abs(math.acos(np.clip(x2 @ L.c2, -1, 1)) - L.rho2))))
    return out


def named_poses(B):
    """bench indices of a few named poses: rest, overhead, across the body, behind the back (taken from the workspace)"""
    P = np.array([[p["plane"], p["elev"], p["axial"]] for p in B.poses]); ws = np.array([k == "ws" for k in B.kind])
    I = np.nonzero(ws)[0]; pick = lambda sc: int(I[np.argmax(sc[I])])
    return dict(rest=pick(-P[:, 1] - 0.01 * np.abs(P[:, 0] - 30)), overhead=pick(P[:, 1]),
                across=pick(P[:, 0] + 0.3 * P[:, 1] - 0.001 * np.abs(P[:, 1] - 90)), behind=pick(-P[:, 0] + 0.3 * P[:, 2]))


def pose_report(M, R, B, i):
    kin = M["kin"]; S = kin["S"]; parts = parts_at(M, R, i); hits = collide(M, R, i, parts)
    P = np.concatenate([x[5] for x in parts]); d = B.dist(i, P); o = 0; mem = {}
    for x in parts:
        dd = d[o:o + len(x[5])]; o += len(x[5]); mem[x[0]] = [round(float(dd.min()), 1), round(float(np.median(dd)), 1), round(float(np.mean((dd >= 2) & (dd <= 14))), 2)]
    return dict(pose={k: round(v) for k, v in B.poses[i].items()}, kind=B.kind[i], valid=bool(kin["valid"][i]), cont=bool(kin["cont"][i]),
                psi=[round(float(l["psi"][i]), 1) for l in S["legs"]], theta=[round(float(l["th"][i] / D2R), 1) for l in S["legs"]],
                par=round(float(S["par"][i]), 1), sep=round(float(S["sep"][i]), 1), collisions=hits,
                inband14=round(float(np.mean((d >= 2) & (d <= 14))), 3), min_d=round(float(d.min()), 1), members_min_med_in14=mem)


def sketch(M, R, B, idx, fn, title=""):
    """matplotlib sketch: skin points near the shoulder + the metal, per named pose, two views"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    col = dict(hub1="k", hub2="k", hub_b="k", hubW="k", crank1="tab:blue", crank2="tab:green", disc_k1="tab:orange", disc_k2="tab:orange",
               disc_c1="tab:red", disc_c2="tab:red", coupler1="tab:cyan", coupler2="tab:olive", neck="tab:purple")
    fig = plt.figure(figsize=(4.2 * len(idx), 8.4))
    for j, (nm, i) in enumerate(idx.items()):
        V, _ = B.skin(i); V = np.asarray(V); sel = np.linalg.norm(V, axis=1) < 230; Vs = V[sel][::4]
        parts = parts_at(M, R, i)
        for row, (el, az) in enumerate(((10, 0), (25, -90))):
            ax = fig.add_subplot(2, len(idx), 1 + j + row * len(idx), projection="3d")
            ax.scatter(Vs[:, 2], Vs[:, 0], Vs[:, 1], s=0.3, c="0.75", alpha=0.25, depthshade=False)
            for x in parts:
                Q = x[5]; ax.scatter(Q[:, 2], Q[:, 0], Q[:, 1], s=1.2, c=col.get(x[0], "m"), depthshade=False)
            ax.set_xlim(-200, 200); ax.set_ylim(-200, 200); ax.set_zlim(-200, 200); ax.view_init(el, az)
            ax.set_xlabel("z right"); ax.set_ylabel("x ant"); ax.set_zlabel("y up"); ax.set_box_aspect((1, 1, 1))
            if row == 0: ax.set_title(f"{nm} {B.poses[i]['plane']:.0f}/{B.poses[i]['elev']:.0f}/{B.poses[i]['axial']:.0f}", fontsize=9)
    fig.suptitle(title, fontsize=10); fig.tight_layout(); fig.savefig(fn, dpi=90); plt.close(fig)


def write_sweep(rows):
    os.makedirs(os.path.join(REPO, "docs", "concepts", "sweeps"), exist_ok=True)
    fn = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
    json.dump(rows, open(fn + ".tmp", "w"), indent=0); os.replace(fn + ".tmp", fn)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def kin_score(p, R):
    """cheap kinematic pre-screen (no distances): share of ws poses closed, share of clip frames followed"""
    kin = kinematics({**PARAMS, **p}, R); ws = R.kind == "ws"
    return float(kin["valid"][ws].mean()), float(kin["cont"][~ws].mean()), kin


def row_of(k, p, r):
    return dict(k=k, t=now(), params={kk: p[kk] for kk in SWEEP_KEYS}, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                follow=r["follow"], contact=r["contact"], gap=r["gap"],
                extra=dict(kin_reach=r.get("kin_reach"), kin_follow=r.get("kin_follow"), coll=r.get("coll"), coll_pairs=r.get("coll_pairs"),
                           windows=r.get("windows"), members=r.get("members"), elbow_inband14=r.get("elbow_inband14"),
                           mass_g=(r.get("mass") or {}).get("g"), r_e=r.get("r_e"), Fb=r.get("Fb"), FW=r.get("FW"), secs=r.get("secs")))


def log_line(k, tag, r):
    return (f"[{k}] {tag} gap {r['gap']} reach {r['reach']} follow {r['follow']} in14 {r['inband14']} in10 {r['inband10']} contact {r['contact']}"
            f" | kin {r.get('kin_reach')}/{r.get('kin_follow')} coll {r.get('coll')} {r.get('coll_pairs')} elbow14 {r.get('elbow_inband14')}"
            f" r_e {r.get('r_e')} Fb {r.get('Fb')} FW {r.get('FW')} mem {r.get('members')} {r.get('secs')} s")


W_SET = [(60.0, 30.0), (71.38, 4.78), (86.33, 21.83), (112.0, -15.0), (90.0, -30.0), (75.0, 45.0)]


def base_pair(az, el, d):
    return dict(b1az=az - d, b1el=el, b2az=az + d, b2el=el, coax=int(d == 0))


def prescreen(R, log=print):
    """stage A (kinematics only): A1 base pairs x W x branches at the spec arcs, A2 arcs x W on the best base pairs"""
    kscore = lambda kr, kf: min(kr, .92) + min(kf, .97)
    A1 = []
    for az in (-90, -60, -30, 0, 30, 60, 120, 150, 180):
        for el in (40, 55, 70):
            for d in (0, 10, 20, 30):
                for wd, wa in W_SET[:4]:
                    for s1, s2 in ((1, -1), (-1, 1)):
                        p = dict(base_pair(az, el, d), wd=wd, wa=wa, s1=s1, s2=s2)
                        kr, kf, _ = kin_score(p, R); A1.append((kscore(kr, kf), kr, kf, p))
    A1.sort(key=lambda x: -x[0]); log(f"A1: {len(A1)} kinematic configs, best {[(round(x[0], 3), x[3]) for x in A1[:5]]}")
    bases = []
    for x in A1:
        key = (x[3]["b1az"], x[3]["b1el"], x[3]["b2az"], x[3]["b2el"])
        if key not in bases: bases.append(key)
        if len(bases) >= 8: break
    A2 = []
    for b1az, b1el, b2az, b2el in bases:
        for a_ in (45, 60, 70):
            for c_ in (60, 90, 120):
                for wd, wa in W_SET:
                    for s1, s2 in ((1, -1), (-1, 1)):
                        p = dict(b1az=b1az, b1el=b1el, b2az=b2az, b2el=b2el, coax=int(b1az == b2az and b1el == b2el),
                                 a1=a_, a2=a_, c1=c_, c2=c_, wd=wd, wa=wa, s1=s1, s2=s2)
                        kr, kf, _ = kin_score(p, R); A2.append((kscore(kr, kf), kr, kf, p))
    A2.sort(key=lambda x: -x[0]); log(f"A2: {len(A2)} kinematic configs, best {[(round(x[0], 3), x[3]) for x in A2[:5]]}")
    return A1, A2


def run_sweep(B, log=print, budget=150, n_geo=36):
    import random
    R = Rig(B); rows = []; rng = random.Random(1); res = []
    def ev(p, tag):
        p = {**PARAMS, **p}; r, M = evaluate(p, B, R); r.pop("taken", None)
        rows.append(row_of(len(rows), p, r)); write_sweep(rows); log(log_line(len(rows) - 1, tag, r), flush=True); res.append((r, p))
        return r
    t0 = time.time(); A1, A2 = prescreen(R, log=lambda *x, **k: print(*x, flush=True)); log(f"prescreen {time.time() - t0:.0f} s", flush=True)
    # stage B: geometry on diverse kinematic leaders (one per base pair x arcs, best W / branch), plus the spec defaults
    picks = [dict()]; seen = set()
    for x in A2:
        p = x[3]; key = (p["b1az"], p["b1el"], p["b2az"], p["a1"], p["c1"])
        if key in seen or x[1] < 0.6: continue
        seen.add(key); picks.append(p)
        if len(picks) >= n_geo: break
    for p in picks:
        ev(p, f"B {p}")
    # stage C: variants on the best 5 (q, rho, ratio, disc mode, parallel margin)
    best5 = sorted(res, key=lambda x: x[0]["gap"])[:5]
    for r0, p0 in best5:
        for var in (dict(q=0.97), dict(q=0.93), dict(rho=7.0), dict(rho=14.0), dict(ratio=0.75), dict(disc_mode="split")):
            if len(rows) >= budget: break
            ev({**p0, **var}, f"C {var} of gap {r0['gap']}")
    # stage D: local refine around the current best (random perturbations)
    best_r, best_p = min(res, key=lambda x: x[0]["gap"])
    while len(rows) < budget:
        p = dict(best_p)
        for kk, sd in (("a1", 4), ("a2", 4), ("c1", 8), ("c2", 8), ("b1az", 10), ("b1el", 5), ("b2az", 10), ("b2el", 5), ("wd", 6), ("wa", 10), ("rho", 2)):
            if rng.random() < 0.35: p[kk] = round(p[kk] + rng.gauss(0, sd), 1)
        if rng.random() < 0.2: p["q"] = rng.choice((1.0, 0.97, 0.93))
        if p["coax"]: p["b2az"], p["b2el"] = p["b1az"], p["b1el"]
        if min(p["a1"], p["a2"]) < 2 * p["rho"] + 12 or p["rho"] < 5: continue
        r = ev(p, "D")
        if r["gap"] < best_r["gap"]: best_r, best_p = r, {**PARAMS, **p}
    return rows, best_r, best_p


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        print("rolling check:", json.dumps(check_rolling()))
        B = CB.Bench(nc, nw); print(B.mode); R = Rig(B)
        r, M = evaluate({}, B, R); r.pop("taken", None); print(json.dumps(r, default=str))
    elif a and a[0] == "kin":
        B = CB.Bench(60, 160); R = Rig(B)
        print(kin_score(dict(PARAMS), R)[:2])
    elif a and a[0] == "sweep":
        B = CB.Bench(60, 160); print(B.mode, flush=True)
        rows, best_r, best_p = run_sweep(B, budget=int(a[1]) if len(a) > 1 else 150)
        print("BEST", json.dumps(best_p), json.dumps(best_r, default=str))
