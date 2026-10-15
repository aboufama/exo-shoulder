"""tongs-tripod: a spherical 3-RPR parallel mechanism whose three 'prismatic' legs are lazy-tongs scissor lattices
(3 ACTIVE DOF = the three leg extensions; every other pivot is passive and set by closure).

Topology (scapula handler -> user's upper-arm cuff), every pivot axis radial through the GH centre:
    S (scapula frame) --3 base bosses at a_k (scapula-fixed, joined by base struts)--> leg k = lazy tongs of n units on the
    great circle a_k -> b_k (its extension Theta_k = angle(a_k, b_k) is the leg's one DOF) --> arm boss at b_k on one
    humerus-fixed arm frame (pads + struts) --> neck --> BOTTOM (user part) -> cuff (user part).
DOF: one leg alone is R-P-R spherical (swivel about a_k, extension, swivel about b_k) and leaves the arm 3 DOF; with its
extension fixed it imposes a_k . b_k = const (one constraint along m_k = b_k x a_k). Three legs -> mobility 3
(spherical Gruebler: bodies 2 + 3 (4n - 2 + 4 ... ) , see docs/concepts/tongs-tripod.md), the three extensions active
(sensed at each base boss as the opening between its two coaxial half-bars), 3 (3n + 3) - 3 passive pivots, all set by
closure: given the arm pose, a_k, b_k and so every lattice node (at a fixed fraction of the arc a_k -> b_k) are known.

SPEC CORRECTIONS (stated in docs/concepts/tongs-tripod.md):
  * the catalogue's extension window [25, 125] deg cannot be reached by n = 2 units of beta = 15 deg bars: a lazy tongs of
    n units spans at most 2 n beta (fully stretched). The window used here is the lattice's own one, from its geometry:
    stretched until the two eyes of a lateral node pair are EYE_R*2 + 1 mm apart, folded until any two pivots / a pivot and
    a bar it does not carry / two same-layer bars / a bar and the other boss shaft come within 1 mm (eyes O8 for a 682
    2x5x1.5 bearing in a 2 mm bar; the spec's O7 pin disc cannot hold the MR63 it names). n 1-4 and beta 12-30 swept.
  * the three bosses at a_k are joined by base struts (10 x 4 mm, scapula-fixed) - a rigid base is needed and the
    scapula handler cannot be assumed to reach three spread points; the arm bosses sit on pads (O16) joined by two
    struts (10 x 4 mm, the 'frame' arm plate) or, as the spec says, on a hull plate covering the three b_k + 8 mm.
  * crossing legs: a leg may ride one level up (parameter 'level'); its profile then clears the lower legs' crowns
    wherever they overlap, measured pose by pose (the spec's flat +5 mm would collide with the 6 mm pin crowns).

Geometry (idealised, every part at its real size; skin-facing surfaces sampled like tools/concept_baseline.py: straps
every 2 mm along x 2 mm across incl. edges, discs on a 2.5 mm grid):
  * lattice: Ti bars 6 x 2 mm; family A (l_j+ -> c_j -> l_j+1-) and the base / arm half-bars c_0 -> l_1-, l_n+ -> c_n on
    layer 1, family B on layer 2 (+2.5 mm = 2 mm bar + 0.5 washer); eyes O8 at every lateral / centre pivot, pin crown
    +6 over the layer-1 underside. A material point of a bar keeps its fraction f along the lattice (exact at the
    pivots), so the lattice rides on one radial profile R(f) per leg (layer 2 at R + 2.5): piecewise linear with kpu
    knots per unit, every bar a rigid bent part. R(f) = the p-th percentile over the kinematically valid bench poses of
    the requirement in each f bin (outermost skin radius under the sample + 2 mm, as the baseline; over a lower part:
    its top + 1 mm), end knots on the bosses (flange top + 1 mm / arm pad top + 1 mm).
  * bosses O16: flange 2 mm (skin-facing disc r 8 at its fitted level), shaft O11 up to the crown at lattice level + 6.5.
  * arm frame (humerus-fixed): O16 pads at b_k, 4 mm, + 2 struts 10 x 4 mm (or the hull plate), + neck 14 x 6 mm to the
    start of BOTTOM's bar (67.5 Wb + 40 Db, band_impl HG frame); per-sample fitted radii (baseline convention).
Taken (bench rules): every leg's Theta inside its lattice window, |det[m_1; m_2; m_3]| >= det_min (forward singularity,
m_k = unit(b_k x a_k)), every fit-clip frame at 10 fps followed with no joint (3 extensions, 6 swivels) jumping more than
25 deg since the last followed frame, no interference between non-adjacent parts (lateral gap < 1 mm and radial gap < 1 mm;
the own boss is exempt within its radius + 2 mm), no metal inside the body (skin-facing samples and the parts' tops).

    python3 docs/concepts/models/tongs-tripod.py check        # a few poses + the default on Bench(20, 40)
    python3 docs/concepts/models/tongs-tripod.py sweep        # coarse -> refine on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "tongs-tripod"
D2R = math.pi / 180
BAR_W, BAR_T, PITCH = 6.0, 2.0, 2.5                 # Ti bars, layer pitch (2 mm + 0.5 washer)
EYE_R, PIN_CROWN = 4.0, 6.0                         # O8 eye (682 bearing 2x5x1.5), pin crown over the layer-1 underside
BOSS_R, FLANGE_T, SHAFT_R, BOSS_UP = 8.0, 2.0, 5.5, 6.5   # O16 boss: flange, shaft, crown over the lattice level
PLATE_T, STRUT_W = 4.0, 10.0                        # arm pads / struts / hull plate, base struts
NECK_W, NECK_T = 14.0, 6.0
SP, SP_DISC, SP_K6 = 2.0, 2.5, 1.5                  # sample grids (baseline), centreline step for interference
CLEAR, GAP, FLIP = 2.0, 1.0, 25.0
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713]); BAR0 = 67.5 * WB + 40.0 * DB
Y_ARM = np.array([0.0, -1.0, 0.0])

LEGS0 = [dict(a=[180, 40], b=[60, 20], n=2, beta=20, level=0),
         dict(a=[-30, 40], b=[100, -60], n=2, beta=20, level=0),
         dict(a=[150, 80], b=[115, 20], n=2, beta=20, level=0)]
PARAMS = dict(legs=LEGS0, plate="frame", base="frame", p=95.0, kpu=2, det_min=0.15)
SWEEP = dict(legs="3 x (a: bvec az -45..210, el 0..90; b: wdir d 60..115, az -62..+20; n 1-4; beta 12-30; level 0/1)",
             plate=("frame", "hull"), base=("frame", "none"), p=(80, 100), kpu=(2, 4), det_min=(0.1, 0.2))


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, az):
    d, a = d * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def disc_grid(rad, step=SP_DISC):
    g = np.arange(-rad, rad + 1e-6, step); Y, Z = np.meshgrid(g, g); k = Y ** 2 + Z ** 2 <= rad ** 2 + 1e-9
    return np.stack([Y[k], Z[k]], 1)


def tbasis(u):
    """tangent basis (a, b) at unit directions u (..., 3)"""
    ref = np.where(np.abs(u[..., 2:3]) < 0.9, np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]))
    a = unit(np.cross(u, ref)); return a, np.cross(u, a)


def disc_dirs(u, yz, r):
    """directions of tangent offsets yz (m, 2) mm around unit u (..., 3) at radius r -> (..., m, 3)"""
    a, b = tbasis(u)
    return unit(u[..., None, :] + (yz[:, 0, None] * a[..., None, :] + yz[:, 1, None] * b[..., None, :]) / r)


def slerp(P0, P1, L, s):
    """points at fractions s (m,) of the great arc P0 -> P1 of length L (rad): (..., m, 3)"""
    return (np.sin((1 - s) * L)[:, None] * P0[..., None, :] + np.sin(s * L)[:, None] * P1[..., None, :]) / math.sin(L)


def ang(u, v):
    return np.arccos(np.clip((u * v).sum(-1), -1, 1))


def skin_radius(B, i, D, r_max=260.0):
    """outermost skin radius along unit directions D (k, 3) from the GH centre in pose i (tools/concept_baseline.py)"""
    r = np.full(len(D), r_max); act = np.ones(len(D), bool); hit = np.zeros(len(D), bool)
    for _ in range(60):
        if not act.any(): break
        d = B.dist(i, D[act] * r[act, None]); a = np.nonzero(act)[0]
        done = d < 0.3; hit[a[done]] = True; act[a[done]] = False
        r[a[~done]] -= np.maximum(d[~done], 0.5)
        low = r < 15; act &= ~low
    return np.where(hit, r, 0.0)


# ======================================================================================================== one lattice
class Tongs:
    """lazy tongs of n units, bar half-arc beta: node ids c_j -> j (j = 0..n), l_j+ -> n+1+2(j-1), l_j- -> n+2+2(j-1)"""
    def __init__(self, n, beta_deg, r):
        self.n = n = int(n); self.beta = beta_deg * D2R; self.r = r
        self.nn = 3 * n + 1
        self.f = np.r_[np.arange(n + 1) / n, np.repeat((np.arange(1, n + 1) - 0.5) / n, 2)]
        self.prad = np.r_[SHAFT_R, np.full(n - 1, EYE_R), SHAFT_R, np.full(2 * n, EYE_R)]
        lp = lambda j: n + 1 + 2 * (j - 1); lm = lambda j: n + 2 + 2 * (j - 1)
        # (layer, start node, end node, length in beta, pivots on the bar [(node, s)])
        B = [(0, 0, lm(1), 1, [(0, 0.0), (lm(1), 1.0)]), (1, 0, lp(1), 1, [(0, 0.0), (lp(1), 1.0)])]
        for j in range(1, n):
            B.append((0, lp(j), lm(j + 1), 2, [(lp(j), 0.0), (j, 0.5), (lm(j + 1), 1.0)]))
            B.append((1, lm(j), lp(j + 1), 2, [(lm(j), 0.0), (j, 0.5), (lp(j + 1), 1.0)]))
        B += [(0, lp(n), n, 1, [(lp(n), 0.0), (n, 1.0)]), (1, lm(n), n, 1, [(lm(n), 0.0), (n, 1.0)])]
        self.bars = B
        self.end_nodes = (0, n)

    def nodes(self, a, b):
        """a, b (..., 3) unit -> nodes (..., 3n+1, 3), Theta, delta (rad)"""
        c = np.clip((a * b).sum(-1), -1, 1); Th = np.arccos(c)
        et = unit(b - c[..., None] * a); nh = unit(np.cross(a, b))
        g = lambda f: np.cos(f * Th)[..., None] * a + np.sin(f * Th)[..., None] * et
        cd = math.cos(self.beta) / np.cos(Th / self.n / 2); de = np.arccos(np.clip(cd, -1, 1))
        N = [g(j / self.n) for j in range(self.n + 1)]
        for j in range(1, self.n + 1):
            m = g((j - 0.5) / self.n); N += [np.cos(de)[..., None] * m + np.sin(de)[..., None] * nh, np.cos(de)[..., None] * m - np.sin(de)[..., None] * nh]
        return np.stack(N, -2), Th, de

    # ---- self-interference window (constant radius r) --------------------------------------------------------------
    def self_ok(self, Th):
        a = np.array([1.0, 0.0, 0.0]); b = np.array([math.cos(Th), 0.0, math.sin(Th)])
        Nd, _, de = self.nodes(a, b)
        if not np.isfinite(de) or de <= 1e-4 or Th / self.n / 2 >= self.beta: return False
        r = self.r
        D = ang(Nd[:, None], Nd[None]) * r; np.fill_diagonal(D, 1e9)
        if (D < self.prad[:, None] + self.prad[None] + GAP).any(): return False
        cl = []
        for (ly, i0, i1, Lm, piv) in self.bars:
            L = Lm * self.beta; s = np.linspace(0, 1, max(3, int(L * r / 1.0) + 1)); cl.append(slerp(Nd[i0], Nd[i1], L, s))
        on = [set(p for p, _ in piv) for (_, _, _, _, piv) in self.bars]
        for k, P in enumerate(cl):                                         # pivot vs bar it does not carry
            for j in range(self.nn):
                if j in on[k]: continue
                if (ang(P, Nd[j][None]) * r).min() < self.prad[j] + BAR_W / 2 + GAP: return False
        for k1, k2 in itertools.combinations(range(len(cl)), 2):           # same-layer bars without a shared pivot
            if self.bars[k1][0] != self.bars[k2][0] or on[k1] & on[k2]: continue
            if (ang(cl[k1][:, None], cl[k2][None]) * r).min() < BAR_W + GAP: return False
        return True

    def window(self):
        th = np.arange(0.5, 2 * self.n * self.beta / D2R, 0.25) * D2R
        ok = np.array([self.self_ok(t) for t in th])
        if not ok.any(): return 1.0, 0.0
        # largest contiguous valid interval
        best, cur = None, None
        for k, o in enumerate(ok):
            if o and cur is None: cur = k
            if (not o or k == len(ok) - 1) and cur is not None:
                e = k if o else k - 1
                if best is None or e - cur > best[1] - best[0]: best = (cur, e)
                cur = None
        return float(th[best[0]]), float(th[best[1]])

    # ---- material samples ------------------------------------------------------------------------------------------
    def templates(self):
        """per bar: underside grid (s (m,), c (m,), f (m,), layer offset, skin-facing flag) and centreline (s, f) for K6;
        eyes at the non-end pivots"""
        r = self.r; out = []
        for (ly, i0, i1, Lm, piv) in self.bars:
            L = Lm * self.beta; na = max(3, int(math.ceil(L * r / SP)) + 1); s = np.linspace(0, 1, na)
            c = np.arange(-BAR_W / 2, BAR_W / 2 + 1e-6, SP); S_, C_ = np.meshgrid(s, c, indexing="ij"); S_, C_ = S_.ravel(), C_.ravel()
            f0, f1 = self.f[i0], self.f[i1]; F_ = f0 + S_ * (f1 - f0)
            face = np.ones(len(S_), bool)
            for (p, sp) in piv:
                rp = BOSS_R if p in self.end_nodes else EYE_R
                face &= np.hypot((S_ - sp) * L * r, C_) >= rp
            sk = np.linspace(0, 1, max(3, int(math.ceil(L * r / SP_K6)) + 1))
            out.append(dict(ly=ly, i0=i0, i1=i1, L=L, s=S_, c=C_, f=F_, face=face, off=ly * PITCH, sk=sk, fk=f0 + sk * (f1 - f0)))
        eyes = [j for j in range(self.nn) if j not in self.end_nodes]
        return out, eyes


# ======================================================================================================== design
class Design:
    def __init__(self, p, B, HG, RS, log=None):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.n = len(HG)
        self.log = log or (lambda *a: None)
        self.RH = np.einsum("pij,pjk->pik", RS, HG)
        self.legs = [dict(L) for L in p["legs"]]; self.K = len(self.legs)
        self.a0 = np.array([bvec(*L["a"]) for L in self.legs]); self.b0 = np.array([wdir(*L["b"]) for L in self.legs])
        self.A = np.einsum("pij,kj->pki", RS, self.a0); self.Bv = np.einsum("pij,kj->pki", self.RH, self.b0)   # (P, K, 3)
        self.Th = ang(self.A, self.Bv)                                                                        # (P, K)
        m = unit(np.cross(self.Bv, self.A)); self.det = np.abs(np.linalg.det(m))
        self.t0 = time.time()
        self._radii_ref()
        self.tg = [Tongs(L["n"], L["beta"], self.r_leg[k]) for k, L in enumerate(self.legs)]
        self.win = [t.window() for t in self.tg]
        inw = np.stack([(self.Th[:, k] >= self.win[k][0]) & (self.Th[:, k] <= self.win[k][1]) for k in range(self.K)], 1)
        self.inw = inw; self.kin_ok = inw.all(1) & (self.det >= p["det_min"])
        self.valid = np.nonzero(self.kin_ok)[0]
        self.status = self.clip_status()
        self._build_samples(); self._requirements()

    # ---- reference radii (mm <-> rad) from the skin under the legs' centrelines, the pads and the base bosses ------
    def _radii_ref(self):
        ok = np.ones(self.n, bool); idx = np.nonzero(ok)[0][:: max(1, self.n // 40)]
        rl = [[] for _ in range(self.K)]; ra, rb = [], []
        for i in idx:
            D = []
            for k in range(self.K):
                f = np.linspace(0, 1, 7); a, b = self.A[i, k], self.Bv[i, k]; th = ang(a, b)
                if th < 0.05: D.append(np.repeat(a[None], 7, 0)); continue
                D.append(slerp(a, b, th, f))
            rr = skin_radius(self.B, int(i), np.concatenate(D)).reshape(self.K, 7)
            for k in range(self.K): rl[k] += list(rr[k][rr[k] > 0])
            ra += list(rr[:, 0][rr[:, 0] > 0]); rb += list(rr[:, -1][rr[:, -1] > 0])
        med = lambda x: float(np.median(x)) + CLEAR + 3.0 if len(x) else 70.0
        self.r_leg = [med(x) for x in rl]; self.r_base = med(ra); self.r_arm = med(rb)

    # ---- continuity on every fit-clip frame at 10 fps --------------------------------------------------------------
    def joint_vals(self, HG):
        """(m, 9) deg: per leg extension, base swivel (about a_k, scapula frame), arm swivel (about b_k, humerus frame)"""
        out = []
        for k in range(self.K):
            a0, b0 = self.a0[k], self.b0[k]; w = HG @ b0; ah = np.einsum("pji,j->pi", HG, a0)
            th = ang(a0[None], w) / D2R
            ta, tb = tbasis(a0); v = w - (w @ a0)[:, None] * a0; psi = np.arctan2(v @ tb, v @ ta) / D2R
            ua, ub = tbasis(b0); u = ah - (ah @ b0)[:, None] * b0; chi = np.arctan2(u @ ub, u @ ua) / D2R
            out += [th, psi, chi]
        return np.stack(out, 1)

    def kin_mask(self, HG):
        A = np.einsum("pij,kj->pki", np.repeat(np.eye(3)[None], len(HG), 0), self.a0); Bv = np.einsum("pij,kj->pki", HG, self.b0)
        Th = ang(A, Bv); m = unit(np.cross(Bv, A)); det = np.abs(np.linalg.det(m))
        ok = det >= self.p["det_min"]
        for k in range(self.K): ok &= (Th[:, k] >= self.win[k][0]) & (Th[:, k] <= self.win[k][1])
        return ok

    def clip_status(self):
        Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; HGa = Z["HG"].astype(float); st = {}; mx = 0.0
        for nme in CB.FIT:
            ix = np.nonzero(cid == names.index(nme))[0]; ok = self.kin_mask(HGa[ix]); q = self.joint_vals(HGa[ix]); last = None
            for k, j in enumerate(ix):
                if not ok[k]: st[int(j)] = (False, "kin"); continue
                if last is not None:
                    stp = float(np.abs(wrapd(q[k] - last)).max()); mx = max(mx, stp)
                    if stp > FLIP: st[int(j)] = (False, "flip"); continue
                st[int(j)] = (True, ""); last = q[k]
        self.max_step = mx
        return st

    # ---- samples ---------------------------------------------------------------------------------------------------
    def _build_samples(self):
        p = self.p; P = self.n
        # lattice templates
        self.tpl = []
        for k, t in enumerate(self.tg):
            bars, eyes = t.templates(); self.tpl.append((bars, eyes))
        # arm frame (humerus frame directions): pads, struts / hull, neck
        ra = self.r_arm; gd = disc_grid(BOSS_R)
        pads = [disc_dirs(self.b0[k], gd, ra) for k in range(self.K)]
        arm = [("pad", k, pads[k]) for k in range(self.K)]
        if p["plate"] == "hull":
            arm.append(("hull", -1, self._hull_dirs(self.b0, ra)))
        else:
            for (i, j) in self._tree_edges(self.b0):
                arm.append(("strut", -1, self._strut_dirs(self.b0[i], self.b0[j], ra, STRUT_W)))
        bd = unit(BAR0); kb = int(np.argmin(ang(self.b0, bd[None])))
        if ang(self.b0[kb], bd) * ra > BOSS_R + SP:
            arm.append(("neck", -1, self._strut_dirs(self.b0[kb], bd, ra, NECK_W, start_mm=BOSS_R)))
        self.arm = arm
        # base: flanges + struts (scapula frame)
        rb = self.r_base
        base = [("flange", k, disc_dirs(self.a0[k], gd, rb)) for k in range(self.K)]
        if p["base"] == "frame":
            for (i, j) in self._tree_edges(self.a0):
                base.append(("strut", -1, self._strut_dirs(self.a0[i], self.a0[j], rb, STRUT_W)))
        self.base = base

    @staticmethod
    def _tree_edges(U):
        d = {(i, j): ang(U[i], U[j]) for i, j in itertools.combinations(range(len(U)), 2)}
        return sorted(d, key=d.get)[:len(U) - 1]

    @staticmethod
    def _strut_dirs(u, v, r, w, start_mm=BOSS_R):
        """strap from u to v (unit), from start_mm off u to BOSS_R short of v (pads cover the ends); 2 mm grid"""
        L = ang(u, v); s0 = start_mm / r; s1 = max(s0 + 1e-3, L - BOSS_R / r) if w == STRUT_W else L
        if s1 <= s0: return np.zeros((0, 3))
        s = np.arange(s0, s1 + 1e-9, SP / r) / L
        Dd = slerp(u, v, L, s); nrm = unit(np.cross(u, v)); c = np.arange(-w / 2, w / 2 + 1e-6, SP) / r
        return unit(Dd[:, None, :] * np.cos(c)[None, :, None] + nrm[None, None, :] * np.sin(c)[None, :, None]).reshape(-1, 3)

    @staticmethod
    def _hull_dirs(U, r, margin=BOSS_R):
        """spherical triangle of U (3, 3) + margin mm, 2 mm grid in the gnomonic plane at the centroid"""
        c = unit(U.mean(0)); a, b = tbasis(c)
        pr = lambda X: np.stack([(X @ a) / (X @ c), (X @ b) / (X @ c)], -1) * r
        T = pr(U); lo = T.min(0) - margin - 2; hi = T.max(0) + margin + 2
        gx, gy = np.meshgrid(np.arange(lo[0], hi[0], SP), np.arange(lo[1], hi[1], SP)); G = np.stack([gx.ravel(), gy.ravel()], 1)
        def segd(Pp, A_, B_):
            ab = B_ - A_; t = np.clip(((Pp - A_) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(Pp - (A_ + t[:, None] * ab), axis=1)
        d = np.minimum.reduce([segd(G, T[i], T[(i + 1) % 3]) for i in range(3)])
        cr = lambda A_, B_, Pp: (B_[0] - A_[0]) * (Pp[:, 1] - A_[1]) - (B_[1] - A_[1]) * (Pp[:, 0] - A_[0])
        s1, s2, s3 = cr(T[0], T[1], G), cr(T[1], T[2], G), cr(T[2], T[0], G)
        inside = ((s1 >= 0) & (s2 >= 0) & (s3 >= 0)) | ((s1 <= 0) & (s2 <= 0) & (s3 <= 0))
        G = G[inside | (d <= margin)]
        return unit(c[None] + (G[:, :1] * a[None] + G[:, 1:] * b[None]) / r)

    def lattice_dirs(self, k, idx):
        """leg k at poses idx: underside dirs per bar (|idx|, m_b, 3), centreline dirs per bar, eye centres, nodes"""
        t = self.tg[k]; bars, eyes = self.tpl[k]; r = t.r
        Nd, Th, de = t.nodes(self.A[idx, k], self.Bv[idx, k])
        U, C = [], []
        for bt in bars:
            P0, P1 = Nd[:, bt["i0"]], Nd[:, bt["i1"]]; nb = unit(np.cross(P0, P1))
            D = slerp(P0, P1, bt["L"], bt["s"]); cc = (bt["c"] / r)[None, :, None]
            U.append(unit(D * np.cos(cc) + nb[:, None, :] * np.sin(cc)))
            C.append(slerp(P0, P1, bt["L"], bt["sk"]))
        return U, C, Nd

    # ---- skin requirements (pose by pose, once per geometry) ------------------------------------------------------
    def _requirements(self):
        B = self.B; v = self.valid; gdE = disc_grid(EYE_R)
        self.req_leg = []                                                  # per leg: (P, m) skin radius + CLEAR - offset (nan = invalid pose)
        nl = []
        for k in range(self.K):
            bars, eyes = self.tpl[k]
            nl.append(sum(len(bt["s"]) for bt in bars) + len(eyes) * len(gdE))
        na = sum(len(x[2]) for x in self.arm); nb_ = sum(len(x[2]) for x in self.base)
        RQ = np.full((self.n, sum(nl) + na + nb_), np.nan)
        for i in v:
            D = []
            for k in range(self.K):
                U, C, Nd = self.lattice_dirs(k, np.array([i]))
                D += [u[0] for u in U]; D.append(disc_dirs(Nd[0, self.tpl[k][1]], gdE, self.tg[k].r).reshape(-1, 3))
            D += [x[2] @ self.RH[i].T for x in self.arm] + [x[2] @ self.RS[i].T for x in self.base]
            D = np.concatenate(D)
            RQ[i] = skin_radius(B, int(i), D) + CLEAR
        o = 0; self.req_leg = []
        for k in range(self.K):
            self.req_leg.append(RQ[:, o:o + nl[k]]); o += nl[k]
        self.req_arm = RQ[:, o:o + na]; o += na; self.req_base = RQ[:, o:o + nb_]
        self.log(f"requirements: {len(v)} valid poses, {RQ.shape[1]} samples, {time.time() - self.t0:.0f} s")

    # ---- fit for one percentile -----------------------------------------------------------------------------------
    def fit(self, pct):
        v = self.valid; q = lambda X: np.nanpercentile(X[v], pct, axis=0) if len(v) else np.full(X.shape[1], 999.0)
        # arm frame: pads flat, the rest per sample
        ra = q(self.req_arm); o = 0; self.arm_r = []
        for (kind, k, D) in self.arm:
            x = ra[o:o + len(D)]; o += len(D)
            self.arm_r.append(np.full(len(D), x.max()) if kind == "pad" else x)
        rb = q(self.req_base); o = 0; self.base_r = []
        for (kind, k, D) in self.base:
            x = rb[o:o + len(D)]; o += len(D)
            self.base_r.append(np.full(len(D), x.max()) if kind == "flange" else x)
        self.R0 = [float(self.base_r[k][0]) + FLANGE_T + GAP for k in range(self.K)]
        self.R1 = [float(self.arm_r[k][0]) + PLATE_T + GAP for k in range(self.K)]
        # legs in level order; part requirements per pose from the parts already placed
        self.prof = [None] * self.K
        order = sorted(range(self.K), key=lambda k: self.legs[k].get("level", 0))
        placed = []
        for k in order:
            t = self.tg[k]; bars, eyes = self.tpl[k]; n = t.n; nb = 8 * n; gdE = disc_grid(EYE_R)
            fs = np.r_[np.concatenate([bt["f"] for bt in bars]), np.repeat(t.f[eyes], len(gdE))]
            off = np.r_[np.concatenate([np.full(len(bt["s"]), bt["off"]) for bt in bars]), np.zeros(len(eyes) * len(gdE))]
            fb = np.minimum((fs * nb).astype(int), nb - 1)
            REQ = np.full((self.n, nb), np.nan)
            for i in v:
                rq = self.req_leg[k][i] - off
                part = self._part_req(k, int(i), placed, fs, off)
                rq = np.maximum(rq, part)
                b_ = np.full(nb, -np.inf); np.maximum.at(b_, fb, rq); REQ[i] = b_
            Rb = np.nanpercentile(np.where(np.isfinite(REQ[v]), REQ[v], 0.0), pct, axis=0) if len(v) else np.full(nb, 999.0)
            Kn = int(self.p["kpu"]) * n; kf = np.linspace(0, 1, Kn + 1); fbc = (np.arange(nb) + 0.5) / nb; kr = np.zeros(Kn + 1)
            for j in range(Kn + 1):
                lo, hi = kf[max(j - 1, 0)], kf[min(j + 1, Kn)]; m = (fbc >= lo) & (fbc <= hi); kr[j] = Rb[m].max() if m.any() else 0.0
            kr[0] = max(kr[0], self.R0[k]); kr[-1] = max(kr[-1], self.R1[k])
            self.prof[k] = (kf, kr); placed.append(k)

    def Rf(self, k, f):
        kf, kr = self.prof[k]; return np.interp(f, kf, kr)

    # ---- per-pose part items (for the interference check and the lattice part requirements) -----------------------
    def items(self, i, legs=None, fixed=True):
        """list of (group, dirs (m, 3), hw (m,), lo (m,), hi (m,), owner (m,) leg id or -1, end tag (m,): 0 none, 1 near a_k, 2 near b_k)"""
        out = []
        if fixed:
            for (kind, k, D), r in zip(self.arm, self.arm_r):
                Dt = D @ self.RH[i].T; m = len(D)
                th = NECK_T if kind == "neck" else PLATE_T
                out.append(("ARM", Dt, np.full(m, SP / 2), r, r + th, np.full(m, k if kind == "pad" else -1), np.zeros(m, int)))
            for k in range(self.K):                                        # arm boss shafts
                u = self.Bv[i, k][None]; out.append(("ARM", u, np.array([SHAFT_R]), np.array([self.arm_r[k][0]]), np.array([self.R1[k] + BOSS_UP]), np.array([k]), np.zeros(1, int)))
            for (kind, k, D), r in zip(self.base, self.base_r):
                Dt = D @ self.RS[i].T; m = len(D)
                th = FLANGE_T if kind == "flange" else PLATE_T
                out.append(("BASE", Dt, np.full(m, SP / 2), r, r + th, np.full(m, k if kind == "flange" else -1), np.zeros(m, int)))
            for k in range(self.K):
                u = self.A[i, k][None]; out.append(("BASE", u, np.array([SHAFT_R]), np.array([self.base_r[k][0]]), np.array([self.R0[k] + BOSS_UP]), np.array([k]), np.zeros(1, int)))
        for k in (legs if legs is not None else range(self.K)):
            U, C, Nd = self.lattice_dirs(k, np.array([i])); bars, eyes = self.tpl[k]
            Ds, lo, hi, end = [], [], [], []
            for bt, c in zip(bars, C):
                c = c[0]; R = self.Rf(k, bt["fk"]) + bt["off"]; Ds.append(c); lo.append(R); hi.append(R + BAR_T)
                end.append(self._end_tag(k, i, c))
            e = Nd[0, eyes]; R = self.Rf(k, self.tg[k].f[eyes]); Ds.append(e); lo.append(R); hi.append(R + PIN_CROWN); end.append(self._end_tag(k, i, e))
            Ds = np.concatenate(Ds); m = len(Ds)
            hw = np.r_[np.full(m - len(eyes), BAR_W / 2), np.full(len(eyes), EYE_R)]
            out.append((f"L{k}", Ds, hw, np.concatenate(lo), np.concatenate(hi), np.full(m, k), np.concatenate(end)))
        return out

    def _end_tag(self, k, i, D):
        r = self.tg[k].r; t = np.zeros(len(D), int)
        t[ang(D, self.A[i, k][None]) * r < BOSS_R + 2] = 1; t[ang(D, self.Bv[i, k][None]) * r < BOSS_R + 2] = 2
        return t

    def _part_req(self, k, i, placed, fs, off):
        """lattice samples of leg k at pose i: requirement from the parts already placed (their top + GAP - offset)"""
        U, C, Nd = self.lattice_dirs(k, np.array([i])); bars, eyes = self.tpl[k]; gdE = disc_grid(EYE_R)
        D = np.concatenate([u[0] for u in U] + [disc_dirs(Nd[0, eyes], gdE, self.tg[k].r).reshape(-1, 3)])
        tag = self._end_tag(k, i, D)
        obs = self.items(i, legs=placed, fixed=True)
        req = np.full(len(D), -np.inf); r = self.tg[k].r
        for (g, Do, hw, lo, hi, own, end) in obs:
            if not len(Do): continue
            tree = cKDTree(Do * r); hwm = hw.max()
            res = tree.query_ball_point(D * r, hwm + SP / 2 + GAP)
            for j, lst in enumerate(res):
                if not lst: continue
                lst = np.array(lst)
                d = ang(D[j][None], Do[lst]) * r; keep = d < hw[lst] + SP / 2 + GAP
                if g in ("ARM", "BASE"):                                 # own boss: joint partner near its end
                    ex = (own[lst] == k) & (((g == "BASE") & (tag[j] == 1)) | ((g == "ARM") & (tag[j] == 2)))
                    keep &= ~ex
                if keep.any(): req[j] = max(req[j], float(hi[lst][keep].max()) + GAP - off[j])
        return req

    def interfere(self, i):
        it = self.items(i); groups = {}
        for x in it:
            g = x[0]
            if g in groups: groups[g] = tuple(np.concatenate([a, b]) if isinstance(a, np.ndarray) else a for a, b in zip(groups[g], x))
            else: groups[g] = x
        names = list(groups); rr = 70.0
        for g1, g2 in itertools.combinations(names, 2):
            if g1 in ("ARM", "BASE") and g2 in ("ARM", "BASE") and g1 == g2: continue
            _, D1, hw1, lo1, hi1, ow1, en1 = groups[g1]; _, D2, hw2, lo2, hi2, ow2, en2 = groups[g2]
            tree = cKDTree(D2 * rr); res = tree.query_ball_point(D1 * rr, (hw1.max() + hw2.max() + GAP) * rr / 40.0)
            for j, lst in enumerate(res):
                if not lst: continue
                lst = np.array(lst); rmin = np.minimum(lo1[j], lo2[lst])
                lat = ang(D1[j][None], D2[lst]) * rmin < hw1[j] + hw2[lst] + GAP
                rad = (lo1[j] < hi2[lst] + GAP) & (lo2[lst] < hi1[j] + GAP)
                hit = lat & rad
                if g1.startswith("L") and g2 in ("ARM", "BASE"):
                    k = int(g1[1:]); hit &= ~((ow2[lst] == k) & (((g2 == "BASE") & (en1[j] == 1)) | ((g2 == "ARM") & (en1[j] == 2))))
                if g2.startswith("L") and g1 in ("ARM", "BASE"):
                    k = int(g2[1:]); hit &= ~((ow1[j] == k) & (((g1 == "BASE") & (en2[lst] == 1)) | ((g1 == "ARM") & (en2[lst] == 2))))
                if hit.any(): return f"{g1}/{g2}"
        return None

    # ---- metal of one pose ----------------------------------------------------------------------------------------
    def face(self, i):
        """skin-facing samples (thorax mm) per part name, and the tops (for the inside check)"""
        out = {}; gdE = disc_grid(EYE_R); covers = []
        for (kind, k, D), r in zip(self.arm, self.arm_r):
            Dt = D @ self.RH[i].T; out.setdefault("arm", []).append(Dt * r[:, None]); covers.append((Dt, r))
        for (kind, k, D), r in zip(self.base, self.base_r):
            Dt = D @ self.RS[i].T; out.setdefault("base", []).append(Dt * r[:, None]); covers.append((Dt, r))
        cD = np.concatenate([c[0] for c in covers]); cR = np.concatenate([c[1] for c in covers]); tree = cKDTree(cD * 70.0)
        for k in range(self.K):
            U, C, Nd = self.lattice_dirs(k, np.array([i])); bars, eyes = self.tpl[k]
            pts = []
            for bt, u in zip(bars, U):
                u = u[0][bt["face"]]; R = self.Rf(k, bt["f"][bt["face"]]) + bt["off"]
                d, j = tree.query(u * 70.0); cov = (d < 1.5 * 70 / self.tg[k].r) & (cR[np.minimum(j, len(cR) - 1)] < R)
                pts.append((u * R[:, None])[~cov])
            e = disc_dirs(Nd[0, eyes], gdE, self.tg[k].r); R = self.Rf(k, self.tg[k].f[eyes])
            pts.append((e * R[:, None, None]).reshape(-1, 3))
            out[f"L{k}"] = pts
        return {k: np.concatenate(v) for k, v in out.items()}

    def tops(self, i):
        T = []
        for (g, D, hw, lo, hi, own, end) in self.items(i):
            T.append(D * hi[:, None])
        return np.concatenate(T)

    def metal(self, i):
        if not self.kin_ok[i]:
            if self.det[i] < self.p["det_min"]: return None, "singular"
            return None, "window L" + "".join(str(k) for k in range(self.K) if not self.inw[i, k])
        if self.B.kind[i] == "clip":
            ok, why = self.status.get(int(self.B.idx[i]), (False, "missing"))
            if not ok: return None, why
        w = self.interfere(i)
        if w: return None, "interference " + w
        F = self.face(i); P = np.concatenate(list(F.values()))
        T = self.tops(i); dt = self.B.dist(i, T)
        if dt.min() < 0: P = np.r_[P, T[np.argmin(dt)][None]]
        return P, ""


# ======================================================================================================== run / sweep
def run(p, B, HG, RS, pcts=None, log=print):
    t = time.time(); D = Design(p, B, HG, RS, log=log); best = None; rows = []
    for pct in (pcts or [p["p"]]):
        D.fit(pct); B.reset(); why = {}; per = {}
        for i in range(len(B.poses)):
            P, w = D.metal(i)
            if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
            d = B.record(i, P)
            if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
            elif B.kind[i] == "clip":
                for nm, X in D.face(i).items():
                    dd = B.dist(i, X); a = per.setdefault(nm, [0, 0]); a[0] += int(((dd >= 2) & (dd <= 14)).sum()); a[1] += len(dd)
        r = B.report(); r["why"] = why; r["pct"] = pct
        r["inband_part"] = {k: round(v[0] / max(v[1], 1), 3) for k, v in per.items()}
        r["npts_part"] = {k: v[1] for k, v in per.items()}
        rows.append(r)
        if best is None or r["gap"] < best["gap"]: best = r
    best["secs"] = round(time.time() - t, 1)
    best["shape"] = dict(win=[[round(w[0] / D2R, 1), round(w[1] / D2R, 1)] for w in D.win], r_leg=[round(x, 1) for x in D.r_leg],
                         r_arm=round(D.r_arm, 1), r_base=round(D.r_base, 1), kin_valid=round(float(D.kin_ok.mean()), 3),
                         det_ok=round(float((D.det >= p["det_min"]).mean()), 3), in_window=[round(float(D.inw[:, k].mean()), 3) for k in range(D.K)],
                         max_step=round(D.max_step, 1), prof=[[round(float(x), 1) for x in D.prof[k][1]] for k in range(D.K)] if D.prof[0] is not None else None,
                         th_range=[[round(float(np.percentile(D.Th[:, k], 2) / D2R), 1), round(float(np.percentile(D.Th[:, k], 98) / D2R), 1)] for k in range(D.K)])
    best["all_pct"] = [dict(pct=r["pct"], gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"]) for r in rows]
    return best, D


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _cache:
        Z = CB._poses_all(); _cache.clear(); D = Design(prm, B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float)); D.fit(prm.get("p", 95.0))
        _cache[key] = D
    D = _cache[key]
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return D.metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def sweep(configs, B, out=SWEEP_OUT, tag="", pcts=(80, 90, 95, 100)):
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, B, HG, RS, pcts=list(pcts), log=lambda *a: None)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", json.dumps(p), e, flush=True); continue
        pp = dict(p, p=r["pct"])
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=pp, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"], inband_part=r["inband_part"],
                   npts_part=r["npts_part"], all_pct=r["all_pct"], mode=r["mode"], stage=tag, secs=r["secs"])
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} p{r['pct']} | {r['why']} | {r['inband_part']} | {r['shape']} | {r['secs']} s | "
              + json.dumps({k: p[k] for k in ('legs', 'plate', 'base', 'kpu', 'det_min')}), flush=True)
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40); Z = CB._poses_all()
        r, D = run(dict(PARAMS), B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float), pcts=[95])
        print(json.dumps({k: v for k, v in r.items()}, default=str))
