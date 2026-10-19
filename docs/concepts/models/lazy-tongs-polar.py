"""lazy-tongs-polar: a spherical lazy-tongs (n rhombi) from a base hub on the scapula (pole p1) to an arm hub on the
posterior deltoid (direction e, fixed in the humerus); 3 ACTIVE DOF (theta_a, theta_b coaxial at the base hub, J3 at
the arm hub), 3n passive scissor pivots set by the tongs' closure.

Topology (scapula handler -> user's upper-arm cuff; every pivot axis radial through the GH centre):
    base plate (on the user's scapula handler) --theta_a--> root a half-bar (layer 1)
                                               --theta_b--> root b half-bar (layer 2)     (two coaxial eyes at p1)
    lazy-tongs of n rhombi along the great circle p1 -> e: crossing pivots C_1..C_(n-1), side pivots S_k+/- (k=1..n)
    end a half-bar (layer 1) + end b half-bar (layer 2) on two coaxial eyes at e (b vs a passive)
    --J3 (end a half-bar vs arm member, ACTIVE)--> arm member: O20 plate under the eyes + a strap (neck) toward the
    elbow (same 25 deg / 8 mm neck as tools/concept_baseline.py) -> the user's cuff via the user's passive slides.
DOF: bodies 2n+2 bars + arm = 2n+3, one-DOF joints 3n+3 -> spherical mobility 3(2n+3) - 2(3n+3) = 3 for any n: the
arm's 3 rotations. Given the arm rotation Q: e = Q e0 fixes Theta = angle(p1, e), hence the tongs' opening (all rhombi
congruent: each crossing bar is one rigid great-circle arc through its centre pivot), the azimuth of the band about p1
and J3. Nothing is undriven: no sag; 3 coordinates to drive / sense (theta_a, theta_b, J3).

Kinematics (exact, closed form, scapula frame S; HG / RS = the bench's pose file, as tools/concept_baseline.py):
    e = HG e0, Theta = acos(p1.e), m = unit(e - (p1.e) p1), bp = p1 x m, c(s) = cos s p1 + sin s m,
    d = Theta/n, half-width w = acos(cos l / cos(d/2)), C_j = c(j d), S_k+/- = cos w c((k-.5)d) +/- sin w bp.
    Taken only if 0 < d/2 < l (the tongs exist), Theta <= stretch * 2 n l (spec: 0.96), and the parts clear (below).

Geometry (idealised, every part at its real size; skin-facing faces sampled as tools/concept_baseline.py: straps every
~2 mm along x ~2 mm across incl. both edges, discs on a 2.5 mm grid; mm <-> angle at r_ref = the median fitted radius):
  * hubs (base at p1, arm at e): O20 disc, 12.25 mm stack (docs/HARDWARE.md v5 height) = lower plate F..F+3 (base plate
    / arm member) + eye a F+3.15..F+7.15 + eye b F+7.3..F+11.3 (6701-size thin-section bearing in each 4 mm eye) + cap
    to F+12.25. Root / end half-bars leave their eye at F+3.15 (a) and F+7.3 (b). Sampled: the plate's skin face at F.
  * bars: Ti 7 x 2.5 mm (bar_w x BAR_T), great-circle arcs; layer 1 (a-family) skin face at the node radius r_X, layer 2
    (b-family) at r_X + layer (3.0); between two nodes the face radius is piecewise linear with `knots` pieces (1 =
    straight, the spec; 2 = one formed bend at mid-segment, free height) - a fixed shape of each rigid bar.
  * pivots: O8 boss (MR63, O3 pin) at every C and S node, skin face r_X - 0.5 (pin head), stack r_X - 0.5 .. r_X + 5.8.
  * neck: humerus-fixed 8 mm strap from the arm hub toward the elbow, neck_deg (baseline convention), plate level.
Heights (one radius per node, one per hub, one per bend knot; fixed in the parts): a linear programme - minimise the
summed face radius of every sample subject to face >= the p-th percentile, over the kinematically valid bench poses,
of the outermost skin radius under that sample + clear (2 mm), and to the layer order near every pivot (layer 2's
underside >= layer 1's top + 0.15 wherever an a-bar and a b-bar overlap in plan, over the whole stroke). p is swept
(as the baseline): a skin bump above the fitted face in a pose counts as contact on the bench (pose not taken).
Taken (bench rules): tongs exist and inside the stretch limit; no interference between parts (non-adjacent >= 1 mm
plan-or-radial clearance, adjacent >= 0.15 mm radial wherever they overlap in plan: same-layer bars, bosses, hubs,
neck - centrelines every ~2 mm, tested in mm at the real radii); J3 within +-j3cap of its centre (the circular median
over the valid poses); along each fit clip, the path from the last followed frame (4 intermediate slerps) stays inside
the stretch / fold range and J3 inside its stops (no wrap) - else the frame is a flip (not followed).

    python3 docs/concepts/models/lazy-tongs-polar.py check [n_clip n_ws]   # a few poses + numbers on one config
    python3 docs/concepts/models/lazy-tongs-polar.py sweep                 # coarse -> refine on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "lazy-tongs-polar"
NAME = "Spherical lazy-tongs polar positioner (scapula pole hub -> posterior-deltoid hub, n rhombi)"
D2R = math.pi / 180
HUB_R, HUB_STACK, PLATE_T = 10.0, 12.25, 3.0
EYE_A, EYE_B = 3.15, 7.3                     # skin face of the root / end half-bars at a hub, above F
BAR_T = 2.5                                  # bar thickness
BOSS_R, PIN_DROP, BOSS_TOP = 4.0, 0.5, 5.8   # O8 pivot boss: face r - 0.5, top r + 5.8 (6.3 mm stack)
NECK_W, NECK_T = 8.0, 3.0
SP, SP_DISC = 2.0, 2.5
GAP_NONADJ, GAP_ADJ = 1.0, 0.15
Y_ARM = np.array([0.0, -1.0, 0.0])

PARAMS = dict(p1_az=-25.2, p1_el=16.8, e0_d=70.1, e0_az=-69.4, n=3, l=28.0, bar_w=7.0, layer=3.0, stretch=0.96,
              j3cap=160.0, knots=1, clear=2.0, neck_deg=25.0)
PCTS = (85, 90, 95, 98, 100)
SWEEP = dict(p1_az=(-60, 10), p1_el=(0, 40), e0_d=(60, 120), e0_az=(-110, -30), n=(2, 3, 4), l="Theta_max/(2n)+2..+8",
             bar_w=(6, 9), layer=(2.8, 3.5), j3cap=(120, 180), knots=(1, 2), p=PCTS)


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, az):
    d, a = d * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def ang_about(w, p, q):
    pp = p - (p * w).sum(-1, keepdims=True) * w; qq = q - (q * w).sum(-1, keepdims=True) * w
    return np.arctan2((w * np.cross(pp, qq)).sum(-1), (pp * qq).sum(-1))


def slerp_arc(u, v, t):
    """points on the great circle u -> v (P, 3) at fractions t (k,) -> (P, k, 3), and the arc normal (P, 3)"""
    ang = np.arccos(np.clip((u * v).sum(-1), -1, 1)); nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u))
    th = ang[:, None] * t[None]
    return np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None], nrm


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


# ======================================================================================================== design
class Design:
    """one configuration on one bench: kinematics for every bench pose, sample directions, skin radii, fit, scoring"""

    def __init__(self, prm, B, HG, RS, r_ref=None, log=print):
        self.p = p = dict(PARAMS, **prm); self.B = B; self.HG = HG; self.RS = RS; self.P = len(HG); self.log = log
        self.n = n = int(p["n"]); self.l = p["l"] * D2R; self.L = float(p["layer"]); self.K = int(p["knots"])
        self.p1 = unit(bvec(p["p1_az"], p["p1_el"])); self.e0 = unit(wdir(p["e0_d"], p["e0_az"]))
        h = np.array([0.0, 0.0, 1.0]) if abs(self.p1[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        self.f1 = unit(np.cross(self.p1, h)); self.f2 = np.cross(self.p1, self.f1)      # fixed tangent frame at p1
        t0 = np.cross(self.e0, Y_ARM); self.t0 = unit(t0)                               # J3 reference, arm-fixed
        self.r_ref = r_ref or 80.0
        # node index: 0 = C_0 (base hub), 1..n-1 = C_j, n = C_n (arm hub), n+k = S_k+, 2n+k = S_k-
        self.NN = 3 * n + 1
        Sp = lambda k: n + k; Sm = lambda k: 2 * n + k
        segs = []                                    # (from node, to node, layer 0/1, bar id)
        segs.append((0, Sm(1), 0, ("a", 0)))
        for k in range(1, n): segs += [(Sp(k), k, 0, ("a", k)), (k, Sm(k + 1), 0, ("a", k))]
        segs.append((Sp(n), n, 0, ("a", n)))
        segs.append((0, Sp(1), 1, ("b", 0)))
        for k in range(1, n): segs += [(Sm(k), k, 1, ("b", k)), (k, Sp(k + 1), 1, ("b", k))]
        segs.append((Sm(n), n, 1, ("b", n)))
        self.segs = segs
        # radius variables: [F_b, F_e, r(C_1..C_(n-1)), r(S_1+..S_n+), r(S_1-..S_n-), bend knots (K-1 per segment)]
        self.var_node = {0: None, n: None}; v = 2
        for j in list(range(1, n)) + [Sp(k) for k in range(1, n + 1)] + [Sm(k) for k in range(1, n + 1)]:
            self.var_node[j] = v; v += 1
        self.var_knot = {}
        for s in range(len(segs)):
            for q in range(1, self.K): self.var_knot[(s, q)] = v; v += 1
        self.NV = v
        self.kin()

    # ---- kinematics -------------------------------------------------------------------------------------------------
    def nodes(self, HG):
        """node directions (P, NN, 3) in the S frame, Theta, w, valid (tongs exist + stretch limit), J values (deg)"""
        n, l = self.n, self.l; p1 = self.p1
        E = HG @ self.e0; ct = np.clip(E @ p1, -1, 1); Th = np.arccos(ct)
        m = unit(E - ct[:, None] * p1); bp = np.cross(p1, m)
        d = Th / n; cw = math.cos(l) / np.cos(d / 2); ok = (cw <= 1.0) & (Th <= self.p["stretch"] * 2 * n * l) & (Th > 1e-3)
        w = np.arccos(np.clip(cw, -1, 1))
        c = lambda s: np.cos(s)[:, None] * p1 + np.sin(s)[:, None] * m
        N = np.zeros((len(HG), self.NN, 3))
        for j in range(n + 1): N[:, j] = c(j * d)
        N[:, n] = E
        for k in range(1, n + 1):
            ck = c((k - 0.5) * d)
            N[:, n + k] = np.cos(w)[:, None] * ck + np.sin(w)[:, None] * bp
            N[:, 2 * n + k] = np.cos(w)[:, None] * ck - np.sin(w)[:, None] * bp
        ta = ang_about(np.broadcast_to(p1, E.shape), np.broadcast_to(self.f1, E.shape), N[:, 2 * n + 1])   # root a -> S_1-
        tb = ang_about(np.broadcast_to(p1, E.shape), np.broadcast_to(self.f1, E.shape), N[:, n + 1])       # root b -> S_1+
        j3 = ang_about(E, N[:, n + n], HG @ self.t0)                                                       # end a -> S_n+
        return N, Th, w, ok, np.degrees(np.stack([ta, tb, j3], 1))

    def kin(self):
        self.N, self.Th, self.w, self.ok_kin, self.J = self.nodes(self.HG)
        v = self.ok_kin
        j3 = self.J[v, 2] * D2R if v.any() else np.zeros(1)
        cen = math.atan2(np.median(np.sin(j3)), np.median(np.cos(j3))) / D2R    # circular centre of J3's travel
        self.j3c = cen
        dj = (self.J[:, 2] - cen + 180) % 360 - 180
        self.ok_j3 = np.abs(dj) <= self.p["j3cap"] + 1e-9
        self.phi = np.arcsin(np.clip(np.sin(self.w) / math.sin(self.l), -1, 1))   # bar angle to the centreline

    # ---- samples ------------------------------------------------------------------------------------------------------
    def build_samples(self):
        """skin-facing sample directions (P, M, 3) in the S frame + per-sample linear radius model (A (M, NV), b (M))"""
        p, n, r = self.p, self.n, self.r_ref; P = self.P; N = self.N
        D, A, b, tag = [], [], [], []
        ns = max(3, int(round(self.l * r / SP)) + 1)
        cs = np.linspace(-p["bar_w"] / 2, p["bar_w"] / 2, max(2, int(math.ceil(p["bar_w"] / SP)) + 1))
        self.seg_t = []
        for si, (x, y, ly, bar) in enumerate(self.segs):
            t0 = HUB_R / (self.l * r) if x in (0, n) else 0.0; t1 = 1 - HUB_R / (self.l * r) if y in (0, n) else 1.0
            t = np.linspace(t0, t1, ns); self.seg_t.append(t)
            X, nrm = slerp_arc(N[:, x], N[:, y], t)                              # (P, ns, 3)
            Dd = unit(X[:, :, None, :] + nrm[:, None, None, :] * (cs / r)[None, None, :, None]).reshape(P, -1, 3)
            rows = np.repeat(self.prof_rows(si, t), len(cs), axis=0)
            D.append(Dd); A.append(rows[:, :-1]); b.append(rows[:, -1]); tag += [("seg", si)] * len(rows)
        g = np.arange(-BOSS_R, BOSS_R + 1e-6, SP_DISC); YY, ZZ = np.meshgrid(g, g); kk = YY ** 2 + ZZ ** 2 <= BOSS_R ** 2 + 1e-9
        boss = np.stack([YY[kk], ZZ[kk]], 1)
        g = np.arange(-HUB_R, HUB_R + 1e-6, SP_DISC); YY, ZZ = np.meshgrid(g, g); kk = YY ** 2 + ZZ ** 2 <= HUB_R ** 2 + 1e-9
        disc = np.stack([YY[kk], ZZ[kk]], 1)
        for j in range(self.NN):
            if j in (0, n):
                Dd = self.disc_dirs(N[:, j], disc, r); row = np.zeros(self.NV + 1); row[0 if j == 0 else 1] = 1.0
                tg = ("hub", j)
            else:
                Dd = self.disc_dirs(N[:, j], boss, r); row = np.zeros(self.NV + 1); row[self.var_node[j]] = 1.0; row[-1] = -PIN_DROP
                tg = ("boss", j)
            D.append(Dd); A.append(np.repeat(row[None, :-1], Dd.shape[1], 0)); b.append(np.full(Dd.shape[1], row[-1])); tag += [tg] * Dd.shape[1]
        self.D = np.concatenate(D, 1); self.A = np.concatenate(A, 0); self.b = np.concatenate(b, 0); self.tag = tag
        # neck (humerus-fixed strap toward the elbow): free profile, >= arm plate F_e near the hub
        ng = p["neck_deg"] * D2R; E = N[:, n]; harm = self.HG @ Y_ARM
        nk = unit(math.cos(ng) * E + math.sin(ng) * unit(harm - (harm * E).sum(-1, keepdims=True) * E))
        nsn = max(3, int(round(ng * r / SP)) + 1); tn = np.linspace(HUB_R / (ng * r), 1, nsn)
        X, nrm = slerp_arc(E, nk, tn)
        csn = np.linspace(-NECK_W / 2, NECK_W / 2, int(math.ceil(NECK_W / SP)) + 1)
        self.Dn = unit(X[:, :, None, :] + nrm[:, None, None, :] * (csn / r)[None, None, :, None]).reshape(P, -1, 3)
        self.neck_t = np.repeat(tn, len(csn)); self.neck_ctr = X; self.neck_tc = tn
        self.cs = cs

    def disc_dirs(self, u, yz, r):
        h = np.where(np.abs(u[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
        a = unit(np.cross(u, h)); bb = np.cross(u, a)
        return unit(u[:, None] + (yz[None, :, :1] * a[:, None] + yz[None, :, 1:] * bb[:, None]) / r)

    def node_row(self, j, ly):
        """linear model (NV+1,) of the face radius of layer ly at node j"""
        row = np.zeros(self.NV + 1)
        if j in (0, self.n): row[0 if j == 0 else 1] = 1.0; row[-1] = EYE_A if ly == 0 else EYE_B
        else: row[self.var_node[j]] = 1.0; row[-1] = 0.0 if ly == 0 else self.L
        return row

    def prof_rows(self, si, t):
        """face radius model rows (len(t), NV+1) along segment si at fractions t (from its first node)"""
        x, y, ly, _ = self.segs[si]; K = self.K
        knots = [self.node_row(x, ly)]
        for q in range(1, K):
            row = np.zeros(self.NV + 1); row[self.var_knot[(si, q)]] = 1.0; row[-1] = 0.0 if ly == 0 else self.L; knots.append(row)
        knots.append(self.node_row(y, ly)); knots = np.stack(knots)
        u = np.clip(np.asarray(t) * K, 0, K - 1e-9); q = np.floor(u).astype(int); f = (u - q)[:, None]
        return knots[q] * (1 - f) + knots[q + 1] * f

    # ---- skin radii ---------------------------------------------------------------------------------------------------
    def skin(self, poses):
        """outermost skin radius under every sample (and the neck) for the given poses (thorax frame = RS @ S frame)"""
        M = self.D.shape[1]; Mn = self.Dn.shape[1]
        self.R = np.zeros((self.P, M)); self.Rn = np.zeros((self.P, Mn))
        for i in poses:
            Dt = np.concatenate([self.D[i], self.Dn[i]]) @ self.RS[i].T
            rr = skin_radius(self.B, int(i), Dt); self.R[i] = rr[:M]; self.Rn[i] = rr[M:]

    # ---- fit ----------------------------------------------------------------------------------------------------------
    def fit(self, pct, valid):
        from scipy.optimize import linprog
        req = np.percentile(self.R[valid], pct, axis=0) + self.p["clear"]
        A, b = self.A, self.b
        # layer order where an a-bar and a b-bar meet at a pivot: the overlap reaches s = (w_bar + gap) / (2 sin(alpha/2))
        rows = []; rhs = []
        lmm = self.l * self.r_ref; W = self.p["bar_w"]
        phi = self.phi[valid]
        a_c = 2 * phi; a_s = math.pi - 2 * phi                           # crossing angles at C-type and S-type meetings
        for j in range(self.NN):
            inc = [(si, 0) for si, s in enumerate(self.segs) if s[0] == j] + [(si, 1) for si, s in enumerate(self.segs) if s[1] == j]
            la = [(si, e) for si, e in inc if self.segs[si][2] == 0]; lb = [(si, e) for si, e in inc if self.segs[si][2] == 1]
            for (sa, ea), (sb, eb) in itertools.product(la, lb):
                # which angle: same side of the centreline (C nodes, toward the same S side) -> 2 phi; else pi - 2 phi
                ang = self.pair_angle(j, sa, ea, sb, eb, valid)
                tov = min(1.0, (W + GAP_ADJ) / (2 * max(math.sin(ang / 2), 1e-3)) / lmm)
                for tt in sorted(set([tov] + [q / self.K for q in range(1, self.K) if q / self.K < tov])):
                    ra = self.prof_rows(sa, np.array([tt if ea == 0 else 1 - tt]))[0]
                    rb = self.prof_rows(sb, np.array([tt if eb == 0 else 1 - tt]))[0]
                    d = rb - ra; d[-1] -= BAR_T + GAP_ADJ                    # rb - ra - BAR_T - gap >= 0
                    rows.append(-d[:-1]); rhs.append(d[-1])
        c = A.sum(0)
        Aub = np.concatenate([-A, np.array(rows)]) if rows else -A
        bub = np.concatenate([b - req, np.array(rhs)]) if rows else b - req
        res = linprog(c, A_ub=Aub, b_ub=bub, bounds=[(20, 260)] * self.NV, method="highs")
        if res.status != 0: return None
        x = res.x; prof = A @ x + b
        # neck: free profile per sample, the first sixth on the arm plate level
        reqn = np.percentile(self.Rn[valid], pct, axis=0) + self.p["clear"]
        near = self.neck_t <= self.neck_t.min() + (1 - self.neck_t.min()) / 6
        profn = np.where(near, np.maximum(reqn, x[1]), reqn)
        return x, prof, profn

    def pair_angle(self, j, sa, ea, sb, eb, valid):
        """smallest angle over the valid poses between segments sa and sb at their common node j"""
        Nn = self.N[valid]
        oa = self.segs[sa][1 - ea]; ob = self.segs[sb][1 - eb]
        u = Nn[:, j]; ta = unit(Nn[:, oa] - (Nn[:, oa] * u).sum(-1, keepdims=True) * u)
        tb = unit(Nn[:, ob] - (Nn[:, ob] * u).sum(-1, keepdims=True) * u)
        return float(np.arccos(np.clip((ta * tb).sum(-1), -1, 1)).min())

    # ---- interference ---------------------------------------------------------------------------------------------------
    def parts(self, x):
        """centreline elements for the interference check: list of (name, dirs (P, k, 3), lo (k,), hi (k,), hw mm)"""
        n = self.n; out = []
        bars = {}
        for si, (xx, yy, ly, bar) in enumerate(self.segs):
            t = self.seg_t[si]; X, _ = slerp_arc(self.N[:, xx], self.N[:, yy], t)
            lo = self.prof_rows(si, t) @ np.r_[x, 1.0]
            bars.setdefault(bar, []).append((X, lo, lo + BAR_T, ly))
        for bar, L in bars.items():
            out.append((bar, np.concatenate([q[0] for q in L], 1), np.concatenate([q[1] for q in L]), np.concatenate([q[2] for q in L]), self.p["bar_w"] / 2, L[0][3]))
        for j in range(self.NN):
            if j in (0, n):
                F = x[0 if j == 0 else 1]; out.append((("hub", j), self.N[:, j:j + 1], np.array([F]), np.array([F + HUB_STACK]), HUB_R, -1))
            else:
                rj = x[self.var_node[j]]; out.append((("boss", j), self.N[:, j:j + 1], np.array([rj - PIN_DROP]), np.array([rj + BOSS_TOP]), BOSS_R, -1))
        return out

    def adjacency(self):
        """pairs of part names that share a joint (pivot / hub eye)"""
        n = self.n; adj = set(); bars_at = {}
        for si, (xx, yy, ly, bar) in enumerate(self.segs):
            for j in (xx, yy): bars_at.setdefault(j, set()).add(bar)
        for j, bs in bars_at.items():
            node = ("hub", j) if j in (0, n) else ("boss", j)
            for b1 in bs:
                adj.add(frozenset([node, b1]))
                for b2 in bs:
                    if b1 != b2: adj.add(frozenset([b1, b2]))
        adj.add(frozenset([("hub", n), "neck"]))
        for b1 in bars_at[n]: adj.add(frozenset([b1, "neck"]))
        return adj

    def interfere(self, x, profn, poses):
        """True where two parts collide in pose i (vectorised per pose over all element pairs)"""
        parts = self.parts(x)
        lo_n = profn.reshape(len(self.neck_tc), -1).min(1)                     # neck plate underside along its centreline
        parts.append(("neck", self.neck_ctr, lo_n, profn.reshape(len(self.neck_tc), -1).max(1) + NECK_T, NECK_W / 2, -2))
        adj = self.adjacency()
        names = [q[0] for q in parts]; sizes = [q[1].shape[1] for q in parts]
        pid = np.repeat(np.arange(len(parts)), sizes)
        lo = np.concatenate([q[2] for q in parts]); hi = np.concatenate([q[3] for q in parts]); hw = np.concatenate([np.full(s, q[4]) for s, q in zip(sizes, parts)])
        mid = (lo + hi) / 2
        npart = len(parts); same = pid[:, None] == pid[None]
        A = np.zeros((npart, npart), bool)
        for a_ in range(npart):
            for b_ in range(npart):
                if frozenset([names[a_], names[b_]]) in adj: A[a_, b_] = True
        adjm = A[pid][:, pid]
        # a bar is never checked against its own hub / boss (it is the joint); adjacent bars need radial order >= GAP_ADJ
        skip = same.copy()
        for a_ in range(npart):
            for b_ in range(npart):
                na, nb = names[a_], names[b_]
                if isinstance(na, tuple) and na[0] in ("hub", "boss") and A[a_, b_]: skip[np.ix_(pid == a_, pid == b_)] = True; skip[np.ix_(pid == b_, pid == a_)] = True
        gap_r = np.where(adjm, GAP_ADJ, GAP_NONADJ); gap_p = np.where(adjm, 0.0, GAP_NONADJ)
        rad_sep = np.maximum(lo[None] - hi[:, None], lo[:, None] - hi[None])      # > 0: radially separated by that much
        rmean = (mid[:, None] + mid[None]) / 2
        hit = np.zeros(self.P, bool)
        iu = np.triu_indices(len(pid), 1)
        keep = ~skip[iu]; I, J = iu[0][keep], iu[1][keep]
        rs = rad_sep[I, J]; gr = gap_r[I, J]; gp = gap_p[I, J]; hws = hw[I] + hw[J]; rm = rmean[I, J]
        rad_bad = rs < gr - 1e-6
        I2, J2 = I[rad_bad], J[rad_bad]; gp2 = gp[rad_bad]; hws2 = hws[rad_bad]; rm2 = rm[rad_bad]
        Dall = np.concatenate([q[1] for q in parts], 1)                          # (P, total, 3)
        self.why = {}
        for i in poses:
            U = Dall[i]; ch = np.linalg.norm(U[I2] - U[J2], axis=1) * rm2
            bad = ch < hws2 + gp2
            if bad.any():
                hit[i] = True; k = np.nonzero(bad)[0][0]; self.why[int(i)] = (names[pid[I2[k]]], names[pid[J2[k]]])
        return hit

    # ---- continuity along the clips ----------------------------------------------------------------------------------------
    def flips(self, taken):
        """bench indices of clip frames NOT followed: the slerp path from the last followed frame leaves the tongs' range
        or J3 crosses its stop (4 intermediate rotations per step)"""
        from scipy.spatial.transform import Rotation as Rot, Slerp
        bad = set()
        for clip, idx in self.B.clip_order().items():
            last = None
            for i in idx:
                if not taken[i]: continue
                if last is None: last = i; continue
                R = Rot.from_matrix(np.stack([self.HG[last], self.HG[i]])); sl = Slerp([0, 1], R)
                Hm = sl(np.linspace(0, 1, 6)[1:-1]).as_matrix()
                _, Th, w, ok, J = self.nodes(Hm)
                j3 = np.r_[self.J[last, 2], J[:, 2], self.J[i, 2]]
                j3u = np.unwrap(j3 * D2R) / D2R
                d0 = (self.J[last, 2] - self.j3c + 180) % 360 - 180
                path = d0 + (j3u - j3u[0])
                if (not ok.all()) or np.abs(path).max() > self.p["j3cap"] + 1e-9: bad.add(i); continue
                last = i
        return bad

    # ---- score --------------------------------------------------------------------------------------------------------
    def score(self, pcts=PCTS, quick_skin=True):
        P = self.P; v_kin = self.ok_kin & self.ok_j3
        valid = np.nonzero(v_kin)[0]
        if len(valid) < 5: return None, []
        self.build_samples(); t = time.time(); self.skin(valid); t_sk = time.time() - t
        out = []
        for pct in pcts:
            f = self.fit(pct, valid)
            if f is None: out.append(None); continue
            x, prof, profn = f
            coll = self.interfere(x, profn, valid)
            taken = v_kin & ~coll
            fl = self.flips(taken)
            B = self.B; B.reset()
            for i in range(P):
                if not taken[i] or i in fl: B.record(i, None); continue
                pts = np.concatenate([self.D[i] * prof[:, None], self.Dn[i] * profn[:, None]]) @ self.RS[i].T
                B.record(i, pts)
            r = B.report(); r.update(pct=pct, n_kin=int(v_kin.sum()), n_coll=int((coll & v_kin).sum()), n_flip=len(fl),
                                     r_med=float(np.median(prof)), F_b=float(x[0]), F_e=float(x[1]), t_skin=round(t_sk, 1))
            r["x"] = [round(float(q), 2) for q in x]
            out.append(r)
        good = [q for q in out if q is not None]
        best = min(good, key=lambda q: q["gap"]) if good else None
        return best, out


# ========================================================================================================= driver
def load_bench(n_clip, n_ws):
    import importlib; importlib.reload(CB)
    B = CB.Bench(n_clip, n_ws); Z = CB._poses_all()
    return B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float)


def evaluate(prm, B, HG, RS, log=print, pcts=PCTS, r_ref=None):
    """score one configuration (two passes: r_ref = 80 mm, then the median fitted face radius if it differs > 6 mm)"""
    d = Design(prm, B, HG, RS, r_ref=r_ref or 80.0, log=log)
    best, rows = d.score(pcts)
    if best is not None and r_ref is None and abs(best["r_med"] - d.r_ref) > 6:
        d = Design(prm, B, HG, RS, r_ref=best["r_med"], log=log); best, rows = d.score(pcts)
    return best, rows, d


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def check(n_clip=20, n_ws=40, prm=None):
    B, HG, RS = load_bench(n_clip, n_ws)
    print("bench", B.mode, len(B.poses))
    prm = prm or {}
    d = Design(prm, B, HG, RS)
    th = np.degrees(d.Th)
    print("Theta range clip %.1f..%.1f ws %.1f..%.1f; kin ok %d/%d; j3 ok %d; j3 centre %.1f" % (
        th[:B.kind.count("clip")].min(), th[:B.kind.count("clip")].max(), th[B.kind.count("clip"):].min(), th[B.kind.count("clip"):].max(),
        d.ok_kin.sum(), len(th), d.ok_j3.sum(), d.j3c))
    t = time.time(); best, rows, d = evaluate(prm, B, HG, RS); print("eval %.0f s" % (time.time() - t))
    for r in rows: print(r)
    print("why (collisions):", list(d.why.items())[:12])
    return best, d


SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def theta_hi(prm, HG, q=100):
    p = dict(PARAMS, **prm); p1 = unit(bvec(p["p1_az"], p["p1_el"])); e0 = unit(wdir(p["e0_d"], p["e0_az"]))
    return float(np.percentile(np.degrees(np.arccos(np.clip((HG @ e0) @ p1, -1, 1))), q))


def with_l(prm, HG, l_add):
    """l from the largest bench Theta: l = Theta_max / (2 n stretch) + l_add (deg)"""
    p = dict(PARAMS, **prm); th = theta_hi(p, HG)
    return dict(prm, l=round(th / (2 * int(p["n"]) * p["stretch"]) + l_add, 2))


class Sweep:
    def __init__(self, B, HG, RS, path=SWEEP_JSON, log=print):
        self.B, self.HG, self.RS, self.path, self.log = B, HG, RS, path, log
        self.rows = json.load(open(path)) if os.path.exists(path) else []
        self.seen = {json.dumps(r["params"], sort_keys=True): r for r in self.rows}

    def run(self, prm):
        full = dict(PARAMS, **prm); key = json.dumps({k: full[k] for k in PARAMS}, sort_keys=True)
        for r in self.rows:
            if json.dumps({k: r["params"][k] for k in PARAMS}, sort_keys=True) == key: return r
        t = time.time(); best, rows, d = evaluate(prm, self.B, self.HG, self.RS, log=self.log)
        prms = {k: full[k] for k in PARAMS}
        if best is None:
            r = dict(k=len(self.rows), t=now(), params=dict(prms, p=None), inband14=0.0, inband10=0.0, reach=0.0, follow=0.0, contact=0.0, gap=300.0,
                     note="no valid pose / LP infeasible", secs=round(time.time() - t))
        else:
            r = dict(k=len(self.rows), t=now(), params=dict(prms, p=best["pct"]), inband14=best["inband14"], inband10=best["inband10"], reach=best["reach"],
                     follow=best["follow"], contact=best["contact"], gap=best["gap"], n_kin=best["n_kin"], n_coll=best["n_coll"], n_flip=best["n_flip"],
                     r_med=round(best["r_med"], 1), r_ref=round(d.r_ref, 1), x=best["x"], secs=round(time.time() - t),
                     by_p=[dict(p=q["pct"], gap=q["gap"], inband14=q["inband14"], reach=q["reach"], follow=q["follow"], contact=q["contact"]) for q in rows if q])
        self.rows.append(r); tmp = self.path + ".tmp"; json.dump(self.rows, open(tmp, "w"), indent=1); os.replace(tmp, self.path)
        self.log(f"[{r['k']}] {r['t']} gap {r['gap']} ib14 {r['inband14']} ib10 {r['inband10']} reach {r['reach']} follow {r['follow']} "
                 f"contact {r['contact']} {r.get('secs')} s  {prm}", flush=True) if self.log is print else self.log(r)
        return r

    def best(self, k=1):
        return sorted(self.rows, key=lambda r: r["gap"])[:k]


def sweep():
    B, HG, RS = load_bench(60, 160)
    print("bench", B.mode, len(B.poses), flush=True)
    S = Sweep(B, HG, RS)
    base = dict(p1_az=-25.2, p1_el=16.8, e0_d=70.1, e0_az=-69.4)
    # stage 1: spec point, then n x l margin
    for n in (3, 2, 4):
        for la in (2.0, 5.0):
            S.run(with_l(dict(base, n=n), HG, la))
    # stage 2: base pole and arm hub direction (coarse grid around the spec, best n / l)
    b = S.best()[0]["params"]; nb = b["n"]; lab = None
    for dp in [(-15, 0), (15, 0), (0, -12), (0, 12), (-30, 0), (0, 24)]:
        S.run(with_l(dict(base, n=nb, p1_az=base["p1_az"] + dp[0], p1_el=base["p1_el"] + dp[1]), HG, 2.0))
    b = S.best()[0]["params"]
    for de in [(-10, 0), (10, 0), (20, 0), (0, -20), (0, 20), (0, -40)]:
        S.run(with_l(dict(b, e0_d=b["e0_d"] + de[0], e0_az=b["e0_az"] + de[1]), HG, 2.0))
    print("BEST", S.best(3), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        nc = int(a[1]) if len(a) > 1 else 20; nw = int(a[2]) if len(a) > 2 else 40
        check(nc, nw)
    elif a[0] == "sweep":
        sweep()
