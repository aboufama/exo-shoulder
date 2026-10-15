"""rail-elbow: a spherical 3R whose middle joint J2 is a curved rail on link 1, so link 2 shrinks to a carriage beside the
arm-end hub (3 ACTIVE DOF, 0 passive on the bench). Spec: docs/concepts/catalogue.json entry "rail-elbow".

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    base (scapula handler) -- J1 O20 hub, axis b fixed in the scapula frame
    -> link 1 = hub-1 upper plate + strap 1 (12 x 3) + a circular RAIL (8 wide x 5 radial) fixed on link 1: the circle at
       polar angle a2 + d_off about the J2 axis p2 (p2 is fixed in link 1, a1 from b), at one constant radius from GH.
       There is no hub and no metal at p2's pole.
    -- J2: a rolling carriage (20 x 16 footprint, 9 radial, underside at the rail's underside) on the rail; its azimuth
       psi about p2 is the J2 joint value
    -> link 2 = carriage + a short bridge strap (12 x 3) to the J3 upper plate
    -- J3 O20 hub, axis W fixed in the humerus (deltoid cap); lower member = the arm-end plate
    -> arm-end plate + neck (14 x 6 strap) to BOTTOM's bar (the user's part; merged with the neck, CLAUDE.md).
DOF: q1 (about b), psi (about p2) and q3 (about W) = a spherical 3R; all three follow from the two-circle closure of b
and HG W on the design's branch sigma, with no spare coordinate: 3 active, 0 passive. Only the physical form of J2
changes (a rail on a circle about p2 instead of a hub on p2).

Spec changes (stated in docs/concepts/rail-elbow.md):
  * humerus frame = the band evaluator's (thorax = RS @ HG @ u, as tools/concept_baseline.py), not B.frames()['H']
    (that frame is ~10 deg off the evaluator's, in which W and BOTTOM's bar are defined);
  * strap 1 joins the rail at its END nearest J1 (outside the carriage travel), not at its mid-point: a carriage that
    grips both rail edges cannot pass a mid-span support. The rail is then a cantilever from J1 (attach='end'), or is
    also held at its far end by a second strap from J1 (attach='both');
  * rail extent = carriage travel over the training poses (bench poses + every 10 fps frame of the fit clips, the
    central `cov` share) + half a carriage + a 3 mm end stop (the spec's +-15 deg first pass is replaced by this);
  * K3 requirement by sphere tracing (same rule: first t >= 15 mm with skin distance >= 2 mm and >= 0 over the next
    15 mm), +-0.5 mm.

Geometry (idealised, every part at its real size): skin-facing undersides sampled on a ~2 mm grid (1 point / 4 mm2, as
tools/concept_baseline.py); hubs are flat O20 discs (radius 10, lower face F at the K3 height along the axis, stack
12.25 mm to the crown); straps are shaped per sample (K3, quantile q over the fit poses), anchored to the plates they
leave and limited to a 60 deg climb; the rail and carriage ride at ONE constant radius (a carriage can only roll on a
circle about p2): the max over rail + carriage samples of their per-sample quantile requirement.
Taken (bench rules + honesty rules): closure on branch sigma with the evaluator's 10 deg singularity margin; the
carriage inside the rail; clip frames followed on every 10 fps frame (no joint jump > 25 deg since the last followed
frame); no two parts that do not share a joint (or share it but away from it) closer than 1 mm (sampled volumes, 0.75
mm sampling allowance), including BOTTOM's bar; no metal inside the body: skin-facing samples recorded, top / side
samples checked (the worst inside one is appended, so the pose counts as contact).

    python3 docs/concepts/models/rail-elbow.py check          # seed configs on Bench(20, 40) + a few named poses
    python3 docs/concepts/models/rail-elbow.py sweep [stage]   # sweep on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "rail-elbow"
D2R = math.pi / 180
HUB_R, LOW_T, UP_GAP, UP_T, CROWN = 10.0, 3.0, 3.15, 3.0, 12.25          # O20 hub (docs/HARDWARE.md v5)
RAIL_W, RAIL_T = 8.0, 5.0                                                 # rail section (spec)
CAR_L, CAR_W, CAR_T = 20.0, 16.0, 9.0                                     # carriage block (spec: [rho_T - 5, rho_T + 4])
STRAP_W, STRAP_T = 12.0, 3.0                                              # K5 strap (mass also at 5.5)
NECK_W, NECK_T = 14.0, 6.0                                                # K7 neck
SP = 2.0                                                                  # sample grid mm (1 point / 4 mm2)
R_REF = 65.0                                                              # mm, radius used to space angular samples
CLEAR, WIN = 2.0, 15.0                                                    # K3: >= 2 mm from the skin, >= 0 over the next 15 mm
FLIP = 25.0                                                               # deg per 10 fps frame
GAP_PART = 1.0                                                            # mm required between parts without a shared joint
COLL_D = GAP_PART + 0.75                                                  # sampled-volume distance that flags a collision
SLOPE = math.tan(60 * D2R)                                                # K5: a strap climbs at most 60 deg
END_STOP = 3.0                                                            # mm of rail beyond the carriage's last position
Y_ARM = np.array([0.0, -1.0, 0.0])
WB = np.array([0.0, -0.0713, 0.9975]); WB /= np.linalg.norm(WB)           # BOTTOM bar (evaluator, HG frame)
DB = np.array([0.0, -0.9975, -0.0713]); DB = DB - (DB @ WB) * WB; DB /= np.linalg.norm(DB); EB = np.cross(WB, DB)
ZBAR, JOG, T_BOT = 67.5, (34.0, 56.0, 8.6), 6.5
TI = 4.43e-3                                                              # g / mm3

SEED_A = dict(b_az=32.55, b_el=80.56, w_d=71.38, w_a=4.78, a1=77.41, a2=81.45, sigma=-1)       # r18 s1392 #1
SEED_B = dict(SEED_A, w_d=112.0, w_a=-15.0)
SEED_C = dict(b_az=2.43, b_el=80.68, w_d=86.33, w_a=21.83, a1=76.90, a2=66.75, sigma=-1)      # baseline r20 s1414 #4
PARAMS = dict(SEED_A, d_off=20.0, q=1.0, sing=10.0, cov=1.0, attach="end")
SWEEP = dict(b_az=(0, 180), b_el=(20, 90), w_d=(75, 115), w_a=(-40, 55), a1=(55, 100), a2=(55, 100), sigma=(-1, 1),
             d_off=(-30, 30), q=(0.85, 1.0), sing=(10, 10), cov=(0.9, 1.0), attach=("end", "both"))


# ---------------------------------------------------------------- small helpers
def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, a):
    d, a = d * D2R, a * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def rodn(k, th):
    """rotations about unit axis k (3,) by angles th (n,) rad -> (n, 3, 3)"""
    th = np.atleast_1d(th); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3)[None] + np.sin(th)[:, None, None] * K[None] + (1 - np.cos(th))[:, None, None] * (K @ K)[None]


def ang_about(w, p, q):
    """signed angle (rad) rotating p onto q about unit axes w (broadcast)"""
    pp = p - (p * w).sum(-1, keepdims=True) * w; qq = q - (q * w).sum(-1, keepdims=True) * w
    return np.arctan2((w * np.cross(pp, qq)).sum(-1), (pp * qq).sum(-1))


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def perp(k):
    a = np.array([0.0, 0.0, 1.0]) if abs(k[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    a = unit(a - (a @ k) * k); return a, np.cross(k, a)


# ---------------------------------------------------------------- sampled surfaces (unit directions in a body frame)
def circ_strap(k, ref, alpha, s0, s1, width, sgn=1.0):
    """strap on the circle at polar alpha (rad) about k, azimuth s (rad, sign sgn) from ref (ref _|_ k), s0..s1:
    (n_along, n_across, 3) unit dirs; across = the polar direction"""
    t = np.cross(k, ref); rr = max(R_REF * math.sin(alpha), 1e-6)
    n = max(2, int(math.ceil(abs(s1 - s0) * rr / SP)) + 1); s = sgn * np.linspace(s0, s1, n)
    c = np.linspace(-width / 2, width / 2, max(2, int(round(width / SP)) + 1)) / R_REF
    al = alpha + c
    D = (np.cos(al)[None, :, None] * k + np.sin(al)[None, :, None] * (np.cos(s)[:, None, None] * ref + np.sin(s)[:, None, None] * t))
    return unit(D)


def gc_strap(u, v, width, start_mm=0.0, end_mm=0.0):
    """strap on the great circle u -> v, from start_mm (arc at R_REF) after u to end_mm before v: (ns, nc, 3) or None"""
    ang = math.acos(np.clip(u @ v, -1, 1)); a0 = start_mm / R_REF; a1 = ang - end_mm / R_REF
    if a1 - a0 < SP / R_REF: return None
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u))
    ns = max(2, int(math.ceil((a1 - a0) * R_REF / SP)) + 1); th = np.linspace(a0, a1, ns)
    D = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    c = np.linspace(-width / 2, width / 2, max(2, int(round(width / SP)) + 1)) / R_REF
    return unit(D[:, None, :] * np.cos(c)[None, :, None] + nrm[None, None, :] * np.sin(c)[None, :, None])


def disc_off(k, rad=HUB_R, step=SP):
    """flat disc offsets (m, 3) _|_ k on a 2 mm grid, and their radii (m,)"""
    a, b = perp(k); g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2 + 1e-6
    O = X[keep][:, None] * a + Y[keep][:, None] * b
    return O, np.hypot(X[keep], Y[keep])


def lipschitz(r, ds):
    """upper envelope of r (ns, nc) along axis 0 with slope <= SLOPE (ds mm per station)"""
    r = r.copy(); k = SLOPE * ds
    for s in range(1, len(r)): r[s] = np.maximum(r[s], r[s - 1] - k)
    for s in range(len(r) - 2, -1, -1): r[s] = np.maximum(r[s], r[s + 1] - k)
    return r


# ---------------------------------------------------------------- K3 requirement (sphere tracing, vectorised)
WOFF = np.array([3.0, 6.0, 9.0, 12.0, 15.0])


def k3(B, i, U, t0=15.0, t1=220.0, it_max=160):
    """per unit direction U (k, 3) (thorax): first t >= t0 with dist >= CLEAR and >= 0 over [t, t + WIN]; inf if none"""
    k = len(U); t = np.full(k, t0); out = np.full(k, np.inf); act = np.ones(k, bool)
    for _ in range(it_max):
        ia = np.nonzero(act)[0]
        if not len(ia): break
        d = B.dist(i, U[ia] * t[ia, None]); good = d >= CLEAR
        if good.any():
            ig = ia[good]; dw = B.dist(i, U[ig, None, :] * (t[ig, None] + WOFF[None])[..., None]); bad = dw < 0
            okw = ~bad.any(1); out[ig[okw]] = t[ig[okw]]; act[ig[okw]] = False
            if (~okw).any():
                nb = ig[~okw]; t[nb] += WOFF[np.argmax(bad[~okw], 1)]
        ng = ia[~good]; dn = d[~good]
        t[ng] += np.where(dn < 0, np.maximum(-dn, 0.5), np.maximum(CLEAR - dn, 0.5))
        over = act & (t > t1); act &= ~over
    return out


# ---------------------------------------------------------------- the design
class Design:
    """kinematics + geometry of one configuration on bench B (HG, RS: the bench poses' humerus / scapula rotations)"""

    def __init__(self, p, B, HG, RS, clips):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.n = len(HG); self.clips = clips
        self.b = bvec(p["b_az"], p["b_el"]); self.W0 = wdir(p["w_d"], p["w_a"])
        self.a1, self.a2 = p["a1"] * D2R, p["a2"] * D2R; self.alpha = (p["a2"] + p["d_off"]) * D2R
        a1 = self.a1
        self.bL = np.array([1.0, 0.0, 0.0]); self.p2L = np.array([math.cos(a1), math.sin(a1), 0.0])
        self.refL = np.array([math.sin(a1), -math.cos(a1), 0.0]); self.tL = np.cross(self.p2L, self.refL)
        self.wL0 = math.cos(self.a2) * self.p2L + math.sin(self.a2) * self.refL          # J3 axis in link 2 (psi = 0)
        self.ref0 = perp(self.b)[0]                                                      # q1 reference
        self.r0H = unit(Y_ARM - (Y_ARM @ self.W0) * self.W0)                             # q3 reference in the humerus
        self.r2L = unit(self.p2L - (self.p2L @ self.wL0) * self.wL0)                     # q3 reference in link 2
        self.K = self.kin(HG)
        self.why_cfg = ""
        self.clip_kin()
        self.extent()
        if not self.why_cfg: self.build()

    # ---- kinematics ----------------------------------------------------------------------------------------------
    def kin(self, HG):
        p = self.p; b = self.b; a1, a2 = self.a1, self.a2
        w = HG @ self.W0; c = np.clip(w @ b, -1, 1); th = np.arccos(c)
        n = unit(np.cross(b[None], w)); den = 1 - c ** 2 + 1e-12
        A = (math.cos(a1) - c * math.cos(a2)) / den; Bq = (math.cos(a2) - c * math.cos(a1)) / den
        p0 = A[:, None] * b + Bq[:, None] * w; h2 = 1 - (p0 * p0).sum(1)
        p2 = unit(p0 + p["sigma"] * np.sqrt(np.clip(h2, 0, None))[:, None] * n)
        margin = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 2 * math.pi - a1 - a2 - th])
        ok = (h2 > 0) & (margin >= p["sing"] * D2R)
        e1 = unit(p2 - (p2 @ b)[:, None] * b); L1 = np.stack([np.broadcast_to(b, e1.shape), e1, np.cross(b[None], e1)], -1)
        wL = np.einsum("nji,nj->ni", L1, w)
        psi = np.arctan2(wL @ self.tL, wL @ self.refL)
        L2 = L1 @ rodn(self.p2L, psi)
        q1 = ang_about(b[None], self.ref0[None], e1)
        q3 = ang_about(w, np.einsum("nij,j->ni", L2, self.r2L), HG @ self.r0H)
        return dict(ok=ok, psi=psi / D2R, q1=q1 / D2R, q3=q3 / D2R, L1=L1, L2=L2, w=w, p2=p2, margin=margin / D2R)

    def clip_kin(self):
        """joint values on every 10 fps frame of the fit clips (training data)"""
        self.CK = {n: self.kin(HGc) for n, HGc in self.clips.items()}

    def extent(self):
        p = self.p; v = self.K["ok"]
        ps = [self.K["psi"][v]] + [ck["psi"][ck["ok"]] for ck in self.CK.values()]
        ps = np.concatenate(ps)
        if len(ps) < 5: self.why_cfg = "no closure"; return
        self.sgn = 1.0 if np.median(ps) >= 0 else -1.0
        s = self.sgn * ps; s = s[s > 0]
        if p["cov"] < 1: lo, hi = np.quantile(s, [(1 - p["cov"]) / 2, 1 - (1 - p["cov"]) / 2])
        else: lo, hi = s.min(), s.max()
        self.s_lo, self.s_hi = float(lo), float(hi)                       # carriage travel (deg, sgn * psi)
        if abs(p["d_off"]) * D2R * R_REF < HUB_R + RAIL_W / 2 + GAP_PART and abs(p["d_off"]) > 1e-6:
            pass                                                           # rail too close to the J3 hub: collisions decide
        rr = max(R_REF * math.sin(self.alpha), 10.0)
        self.ext = (CAR_L / 2 + END_STOP) / rr / D2R
        self.r_lo, self.r_hi = self.s_lo - self.ext, self.s_hi + self.ext  # rail extent (deg)

    def in_travel(self, psi):
        s = self.sgn * np.asarray(psi)
        return (s >= self.s_lo - 1e-6) & (s <= self.s_hi + 1e-6)

    # ---- geometry --------------------------------------------------------------------------------------------------
    def build(self):
        p = self.p; t0 = time.time()
        sg = self.sgn; al = self.alpha; dsg = 1.0 if p["d_off"] >= 0 else -1.0
        G = {}
        # rail (L1) + carriage (L2), constant radius
        G["rail"] = circ_strap(self.p2L, self.refL, al, self.r_lo * D2R, self.r_hi * D2R, RAIL_W, sg)
        rr = max(R_REF * math.sin(al), 10.0)
        hl = CAR_L / 2 / rr; car = circ_strap(self.p2L, self.refL, al, -hl, hl, CAR_W, sg)          # (11, 9, 3)
        cc = np.linspace(-CAR_W / 2, CAR_W / 2, car.shape[1])
        G["car"] = car; self.car_skin = np.abs(cc) > RAIL_W / 2 + 1e-6
        # bridge (L2): along the meridian at psi = 0 from the carriage edge to the J3 hub edge
        a_from = al - dsg * (CAR_W / 2) / R_REF; a_to = self.a2 + dsg * HUB_R / R_REF
        if dsg * (a_from - a_to) > SP / R_REF:
            n = max(2, int(math.ceil(abs(a_from - a_to) * R_REF / SP)) + 1); A = np.linspace(a_to, a_from, n)  # hub -> carriage
            c = np.linspace(-STRAP_W / 2, STRAP_W / 2, int(round(STRAP_W / SP)) + 1) / R_REF / max(math.sin(self.a2), 0.2)
            G["bridge"] = unit(np.cos(A)[:, None, None] * self.p2L + np.sin(A)[:, None, None] * (np.cos(c)[None, :, None] * self.refL + np.sin(c)[None, :, None] * self.tL * sg))
        # strap 1 (L1): J1 hub edge -> rail near end; strap 1b: J1 -> rail far end
        x = lambda a, s: math.cos(a) * self.p2L + math.sin(a) * (math.cos(sg * s) * self.refL + math.sin(sg * s) * self.tL)
        self.x_near = x(al, self.r_lo * D2R); self.x_far = x(al, self.r_hi * D2R)
        G["strap1"] = gc_strap(self.bL, self.x_near, STRAP_W, HUB_R, RAIL_W / 2)
        if p["attach"] == "both": G["strap1b"] = gc_strap(self.bL, self.x_far, STRAP_W, HUB_R, RAIL_W / 2)
        # neck (H): J3 hub edge -> BOTTOM's bar start (40 mm down the bar)
        s_ = (40.0 - JOG[0]) / (JOG[1] - JOG[0]); s_ = 10 * s_ ** 3 - 15 * s_ ** 4 + 6 * s_ ** 5
        self.Pbar = (ZBAR + JOG[2] * s_) * WB + 40.0 * DB
        G["neck"] = gc_strap(self.W0, unit(self.Pbar), NECK_W, HUB_R, 0.0)
        G = {k: v for k, v in G.items() if v is not None}
        self.G = G
        self.body = dict(rail="L1", car="L2", bridge="L2", strap1="L1", strap1b="L1", neck="H")
        self.O1, self.rho1 = disc_off(self.b); self.O3, self.rho3 = disc_off(self.W0)
        # ---- K3 fit over the fit poses: closure (bench poses), carriage inside the travel
        fit = np.nonzero(self.K["ok"] & self.in_travel(self.K["psi"]))[0]; self.fit = fit
        if len(fit) < 5: self.why_cfg = "no fit poses"; return
        names = list(G); sizes = [G[k].shape[0] * G[k].shape[1] for k in names]
        h0 = 60.0
        U1 = unit(h0 * self.b + self.O1); U3 = unit(h0 * self.W0 + self.O3)
        REQ = {k: np.zeros((len(fit), s)) for k, s in zip(names, sizes)}; R1 = np.zeros((len(fit), len(U1))); R3 = np.zeros((len(fit), len(U3)))
        for j, i in enumerate(fit):
            M = self.mats(i)
            U = [M[self.body[k]] @ G[k].reshape(-1, 3).T for k in names]
            U = np.concatenate([u.T for u in U] + [(M["S"] @ U1.T).T, (M["H"] @ U3.T).T])
            r = k3(self.B, int(i), U); o = 0
            for k, s in zip(names, sizes): REQ[k][j] = r[o:o + s]; o += s
            R1[j] = r[o:o + len(U1)]; o += len(U1); R3[j] = r[o:]
        q = p["q"]
        qt = lambda X: np.quantile(np.minimum(X, 900.0), q, axis=0, method="higher") if q < 1 else np.minimum(X, 900.0).max(0)
        # hubs: flat discs, lower face height along the axis
        self.F1 = float(np.sqrt(np.clip(qt(R1) ** 2 - self.rho1 ** 2, 0, None)).max())
        self.F3 = float(np.sqrt(np.clip(qt(R3) ** 2 - self.rho3 ** 2, 0, None)).max())
        # second pass for the hubs at their real height (directions change slightly)
        U1 = unit(self.F1 * self.b + self.O1); U3 = unit(self.F3 * self.W0 + self.O3)
        for j, i in enumerate(fit):
            M = self.mats(i); r = k3(self.B, int(i), np.concatenate([(M["S"] @ U1.T).T, (M["H"] @ U3.T).T]))
            R1[j] = r[:len(U1)]; R3[j] = r[len(U1):]
        self.F1 = float(np.sqrt(np.clip(qt(R1) ** 2 - self.rho1 ** 2, 0, None)).max())
        self.F3 = float(np.sqrt(np.clip(qt(R3) ** 2 - self.rho3 ** 2, 0, None)).max())
        # rail + carriage: one constant radius
        rq = {k: qt(REQ[k]).reshape(G[k].shape[:2]) for k in names}
        self.R_rail = float(max(rq["rail"].max(), rq["car"].max()))
        rad = {"rail": np.full(G["rail"].shape[:2], self.R_rail), "car": np.full(G["car"].shape[:2], self.R_rail)}
        ds = SP
        hub_up = lambda F: math.hypot(F + UP_GAP, HUB_R)                  # radius of the upper plate's edge
        hub_lo = lambda F: math.hypot(F, HUB_R)
        if "bridge" in G:                                                  # J3 upper plate -> carriage side
            r = rq["bridge"].copy(); r[0] = np.maximum(r[0], hub_up(self.F3)); r[-1] = np.maximum(r[-1], self.R_rail)
            rad["bridge"] = lipschitz(r, ds)
        for k in ("strap1", "strap1b"):
            if k in G:
                r = rq[k].copy(); r[0] = np.maximum(r[0], hub_up(self.F1)); r[-1] = np.maximum(r[-1], self.R_rail)
                rad[k] = lipschitz(r, ds)
        if "neck" in G:
            r = rq["neck"].copy(); r[0] = np.maximum(r[0], hub_lo(self.F3)); r[-1] = np.maximum(r[-1], np.linalg.norm(self.Pbar))
            rad["neck"] = lipschitz(r, ds)
        self.rad = rad; self.rq = rq
        self.thick = dict(rail=RAIL_T, car=CAR_T, bridge=STRAP_T, strap1=STRAP_T, strap1b=STRAP_T, neck=NECK_T)
        self.static_vol()
        self.secs_fit = time.time() - t0

    def mats(self, i):
        RS = self.RS[i]
        return dict(S=RS, L1=RS @ self.K["L1"][i], L2=RS @ self.K["L2"][i], H=RS @ self.HG[i])

    # ---- sampled volumes in the body frames (for collisions and the top / side contact check) --------------------
    def static_vol(self):
        V = {}; TOP = {}
        for k, D in self.G.items():
            r = self.rad[k]; t = self.thick[k]; nl = int(math.ceil(t / SP)) + 1
            lay = np.linspace(0, t, nl)
            V[k] = (D[:, :, None, :] * (r[:, :, None] + lay[None, None, :])[..., None]).reshape(-1, 3)
            top = (D * (r + t)[..., None]).reshape(-1, 3)
            side = np.concatenate([D[:, 0] * (r[:, 0] + t / 2)[:, None], D[:, -1] * (r[:, -1] + t / 2)[:, None],
                                   D[0] * (r[0] + t / 2)[:, None], D[-1] * (r[-1] + t / 2)[:, None]])
            TOP[k] = np.concatenate([top, side])
        for nm, k, O, F in (("hub1", self.b, self.O1, self.F1), ("hub3", self.W0, self.O3, self.F3)):
            lay = np.linspace(0, CROWN, int(math.ceil(CROWN / SP)) + 1)
            V[nm] = ((F + lay)[:, None, None] * k + O[None]).reshape(-1, 3)
            V[nm + "low"] = ((F + np.linspace(0, LOW_T, 3))[:, None, None] * k + O[None]).reshape(-1, 3)
            a, bb = perp(k); ring = np.linspace(0, 2 * math.pi, 32, endpoint=False)
            rim = (HUB_R * (np.cos(ring)[:, None] * a + np.sin(ring)[:, None] * bb))
            TOP[nm] = np.concatenate([(F + CROWN) * k + O, ((F + lay)[:, None, None] * k + rim[None]).reshape(-1, 3)])
        # BOTTOM bar (user part, H): collision only
        dl = np.arange(40.0, 160.0 + 1e-6, SP); el = np.arange(-16.0, 16.0 + 1e-6, SP)
        s_ = np.clip((dl - JOG[0]) / (JOG[1] - JOG[0]), 0, 1); zlo = ZBAR + JOG[2] * (10 * s_ ** 3 - 15 * s_ ** 4 + 6 * s_ ** 5)
        zl = np.linspace(0, T_BOT, 4)
        V["bar"] = (zlo[:, None, None, None] + zl[None, None, :, None]) * WB + dl[:, None, None, None] * DB + el[None, :, None, None] * EB
        V["bar"] = V["bar"].reshape(-1, 3)
        self.V = V; self.TOP = TOP
        self.vbody = dict(rail="L1", car="L2", bridge="L2", strap1="L1", strap1b="L1", neck="H", hub1="S", hub1low="S", hub3="H",
                          hub3low="H", bar="H")

    # collision pairs (parts in bodies that do not share a joint there); hub1 = S lower + L1 upper/crown, hub3 = H lower +
    # L2 upper/crown, so they are checked against the other two bodies only
    PAIRS = [("hub1", "car"), ("hub1", "bridge"), ("hub1", "hub3"), ("hub1", "neck"),
             ("strap1", "car"), ("strap1", "bridge"), ("strap1", "hub3"), ("strap1", "neck"),
             ("rail", "hub1low"), ("rail", "bridge"), ("rail", "hub3"), ("rail", "neck"),
             ("strap1b", "car"), ("strap1b", "bridge"), ("strap1b", "hub3"), ("strap1b", "neck"),
             ("car", "neck"), ("car", "hub3low"), ("bridge", "neck"),
             ("rail", "bar"), ("strap1", "bar"), ("strap1b", "bar"), ("car", "bar"), ("bridge", "bar"), ("hub1", "bar")]

    def world(self, i, sets, names):
        M = self.mats(i); return {k: sets[k] @ M[self.vbody[k]].T for k in names if k in sets}

    def interfere(self, i):
        names = set(itertools.chain(*self.PAIRS)); P = self.world(i, self.V, names)
        w = self.K["w"][i] @ self.RS[i].T
        for a, b in self.PAIRS:
            if a not in P or b not in P: continue
            A, Bv = P[a], P[b]
            if a == "bridge" and b == "neck":                              # exempt within the J3 hub (+2 mm)
                ta = np.linalg.norm(A - (A @ w)[:, None] * w, axis=1); tb = np.linalg.norm(Bv - (Bv @ w)[:, None] * w, axis=1)
                A, Bv = A[ta > HUB_R + 2], Bv[tb > HUB_R + 2]
                if not len(A) or not len(Bv): continue
            ca, cb = A.mean(0), Bv.mean(0)
            if np.linalg.norm(ca - cb) > np.linalg.norm(A - ca, axis=1).max() + np.linalg.norm(Bv - cb, axis=1).max() + COLL_D: continue
            if cKDTree(A).query(Bv, distance_upper_bound=COLL_D)[0].min() < COLL_D: return f"{a}/{b}"
        return None

    def skin_face(self, i):
        """skin-facing samples (thorax) per member"""
        M = self.mats(i); out = {}
        for k, D in self.G.items():
            X = D * self.rad[k][..., None]
            if k == "car": X = X[:, self.car_skin]
            out[k] = X.reshape(-1, 3) @ M[self.body[k]].T
        out["hub1"] = (self.F1 * self.b + self.O1) @ M["S"].T
        out["hub3"] = (self.F3 * self.W0 + self.O3) @ M["H"].T
        return out

    def taken(self, i):
        """(None, reason) or (skin-facing points dict, '')"""
        if self.why_cfg: return None, self.why_cfg
        if not self.K["ok"][i]: return None, "closure"
        if not self.in_travel(self.K["psi"][i:i + 1])[0]: return None, "off rail"
        if self.B.kind[i] == "clip":
            ok, why = self.clip_status(i)
            if not ok: return None, why
        w = self.interfere(i)
        if w: return None, "collide " + w
        return self.skin_face(i), ""

    def clip_status(self, i):
        if not hasattr(self, "_cs"):
            st = {}
            for n, ck in self.CK.items():
                inr = self.in_travel(ck["psi"]); last = None
                for f in range(len(ck["ok"])):
                    if not ck["ok"][f]: st[(n, f)] = (False, "closure"); continue
                    if not inr[f]: st[(n, f)] = (False, "off rail"); continue
                    q = np.array([ck["q1"][f], ck["psi"][f], ck["q3"][f]])
                    if last is not None and np.abs(wrapd(q - last)).max() > FLIP: st[(n, f)] = (False, "flip"); continue
                    st[(n, f)] = (True, ""); last = q
            self._cs = st
        return self._cs.get(self.bench_clip_frame[i], (False, "missing"))

    def metal(self, i):
        """(points (k, 3) or None, reason); a pose whose top / side samples enter the body gets its worst one appended"""
        P, why = self.taken(i)
        if P is None: return None, why
        face = np.concatenate(list(P.values()))
        T = self.world(i, self.TOP, list(self.TOP))
        top = np.concatenate(list(T.values())); dt = self.B.dist(i, top)
        if dt.min() < 0: face = np.r_[face, top[np.argmin(dt)][None]]
        return face, ""

    def mass(self, t_strap=STRAP_T):
        """titanium mass (g) of the custom metal: hubs as 20 mm x 12.25 discs at 40 % fill, rail, carriage at 50 %, straps"""
        m = 2 * math.pi * HUB_R ** 2 * CROWN * 0.4
        for k, D in self.G.items():
            area = D.shape[0] * D.shape[1] * SP * SP * np.mean((self.rad[k] / R_REF) ** 2)
            t = dict(rail=RAIL_T, car=CAR_T * 0.5, neck=NECK_T).get(k, t_strap)
            m += area * t
        return m * TI

    def shape(self):
        if self.why_cfg: return dict(why=self.why_cfg)
        return dict(F1=round(self.F1, 1), F3=round(self.F3, 1), R_rail=round(self.R_rail, 1),
                    travel=[round(self.s_lo, 1), round(self.s_hi, 1)], rail_deg=round(self.r_hi - self.r_lo, 1),
                    rail_len_mm=round((self.r_hi - self.r_lo) * D2R * self.R_rail * math.sin(self.alpha), 1),
                    n_fit=int(len(self.fit)), mass_g=round(self.mass(), 1), mass55_g=round(self.mass(5.5), 1),
                    n_pts={k: int(v.shape[0] * v.shape[1]) for k, v in self.G.items()})


# ---------------------------------------------------------------- bench plumbing
class Ctx:
    """bench + pose data shared by all configurations"""
    def __init__(self, B):
        self.B = B; Z = CB._poses_all(); names = list(Z["NAMES"])
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.clips = {}; where = {}
        for n in CB.FIT:
            ix = np.nonzero(Z["CID"] == names.index(n))[0]; self.clips[n] = Z["HG"][ix].astype(float)
            for f, j in enumerate(ix): where[int(j)] = (n, f)
        self.bcf = {i: where.get(int(j)) for i, j in enumerate(B.idx)}

    def design(self, p):
        D = Design.__new__(Design); D.bench_clip_frame = self.bcf; Design.__init__(D, p, self.B, self.HG, self.RS, self.clips); return D


def run(p, C):
    t = time.time(); D = C.design(p); B = C.B; B.reset(); why = {}
    for i in range(len(B.poses)):
        P, w = D.metal(i)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, P)
        if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1); r["shape"] = D.shape()
    if not D.why_cfg:                                          # in-band 2-14 per member over the clip frames taken
        per = {}
        for i in range(len(B.poses)):
            if B.kind[i] != "clip" or B.res[i] is None or B.res[i].min() < 0: continue
            for k, X in D.skin_face(i).items():
                d = B.dist(i, X); a = per.setdefault(k, [0, 0]); a[0] += int(((d >= 2) & (d <= 14)).sum()); a[1] += len(d)
        r["member_ib14"] = {k: round(a[0] / max(a[1], 1), 3) for k, a in per.items()}
        r["member_share"] = {k: round(a[1] / max(sum(x[1] for x in per.values()), 1), 3) for k, a in per.items()}
    return r, D


_CACHE = {}


def metal(pose, frames, params):
    """task API: metal samples (k, 3) in the thorax frame for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _CACHE:
        _CACHE.clear(); _CACHE[key] = Ctx(B).design(prm)
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _CACHE[key].metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KEYS = ("b_az", "b_el", "w_d", "w_a", "a1", "a2", "sigma", "d_off", "q", "sing", "cov", "attach")


def sweep(configs, C, out=SWEEP_OUT, tag=""):
    rows = json.load(open(out)) if out and os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, C)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"],
                   member_ib14=r.get("member_ib14"), member_share=r.get("member_share"), mode=r["mode"], stage=tag, secs=r["secs"])
        rows.append(row)
        if out:
            json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r.get('member_ib14')} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in KEYS), flush=True)
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40); C = Ctx(B); print("bench", B.mode, len(B.poses), flush=True)
        for p in [dict(SEED_A, d_off=20.0), dict(SEED_A, d_off=-20.0)]:
            sweep([p], C, out=None, tag="check")
