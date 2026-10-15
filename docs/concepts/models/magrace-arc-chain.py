"""Concept model: MAGRACE-ARC-CHAIN (id magrace-arc-chain) - "Hubless chain on magnet-preloaded open ball races"
(docs/concepts/catalogue.json, ideation E, overhead-first lens).

Chain (scapula handler -> user's upper-arm cuff), the spherical 3R of tools/concept_baseline.py realised as arcs:
    base --J1: race + carriage on a circle about b--> link 1 --J2: race + carriage about p2--> link 2
    --J3: race + carriage about W--> arm-end member (BOTTOM's neck) -> user's cuff.
Joint k is an open ball race: a Ti race plate (12 mm wide, 2.5 mm thick) lying on the circle at angular radius gamma_k
about the joint axis m_k (an axis through the GH centre), on ONE of the joint's two members (the proximal by default;
`s_k` = 1 puts it on the distal one: J3 on the arm with W = the humerus axis is the "humeral ring"); the OTHER member
carries a 25 mm carriage that rolls on it (O2 Si3N4 balls, magnet preload). Stack 7 mm: race 2.5 + balls 2 + carriage
2.5, the carriage on top (skin side = race). No hub sits at any axis pierce point.
DOF: 3 ACTIVE (the carriage's place along its race = the joint angle of the spherical 3R; the arm sets the three
angles uniquely through the two-circle closure on the design's branch), 0 PASSIVE (balls and magnets add no coordinate).
Nothing is spare; nothing can sag on its own (each carriage is held by the chain's closure).

SPEC CHANGES (said in docs/concepts/magrace-arc-chain.md):
  * a revolute race must be a surface of revolution about its axis, so the race's RUNNING surface sits at one constant
    distance R_k from GH (a circle about an axis through GH is equidistant from GH); the spec's "r_race(az) fitted per
    azimuth" can only be the plate's UNDERSIDE: option `contour` (mm) lets the plate thicken (2.5 mm minimum) so its skin
    side follows the fitted envelope per station, up to `contour` mm deeper than the flat plate (0 = flat 2.5 mm plate);
  * the race plate lies on the sphere of radius R_k about GH (normal radial from GH: tangent to the skin);
  * the carriage rides fully over its race (the race spans the carriage's travel + half a carriage + 1 mm at each end),
    so it has no exposed underside (the spec's "sample only its exposed underside" = nothing); its sides and the
    carriage itself still count for contact and part interference;
  * links: 14 mm x 3 mm straps on the great circle between the nearest points of the member's two elements (spec), the
    underside fitted per station; at a carriage the strap is at carriage level (underside R_k + 2), at a race at plate
    level (top flush with the running surface); away from the ends a strap may dip toward the skin at <= 45 deg;
  * stacking: where parts of different members overlap (seen from GH) the member that rides higher is lifted to the
    lower part's top + 1.6 mm (rank: the carriage member rides above the race member at every joint); the arm-end
    member carries BOTTOM's neck exactly as the baseline (8 x 3 strap, 25 deg toward the humerus axis).
Metal sampled (~1 point / 4 mm2, 2 mm grid at the part's real radius, as tools/concept_baseline.py): SCORED = race
undersides, link undersides, neck underside. CONTACT-ONLY = carriages (bottom, top), race / strap tops - one appended
when inside the body so the bench counts the pose as contact.
Fitting (the baseline's percentile rule): per kinematically valid pose the skin need of every sample (smallest radius
with >= 2 mm to the skin along the ray from GH: a precomputed per-pose need map, then corrected with the bench's own
distance at the fitted geometry), max with the stacking need; the part's fixed shape = the p-th percentile over the
valid poses (p swept).
Taken iff: closure on the branch with the evaluator's 10 deg fold / stretch margin; every carriage inside its race;
along each fit clip at its full 10 fps no joint steps > 30 deg between consecutive followed frames (a flip = that
frame not followed); no two non-adjacent parts on different members within 1.5 mm (volume samples, 2 mm grid, three
layers through the thickness; race k / carriage k are the adjacent pair); then the bench's contact rule.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/magrace-arc-chain.py [check|needmap|prescreen|sweep|best|sketch]
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "magrace-arc-chain"; NAME = "Hubless chain on magnet-preloaded open ball races"
D2R = math.pi / 180
RACE_W, RACE_T, BALL_GAP, CAR_T, CAR_L = 12.0, 2.5, 2.0, 2.5, 25.0     # spec (mm)
STACK = RACE_T + BALL_GAP + CAR_T                                       # 7 mm
LK_W, LK_T = 14.0, 3.0                                                  # link strap (spec: 14 mm strap)
NECK_W, NECK_T, NECK_DEG = 8.0, 3.0, 25.0                               # BOTTOM's neck as tools/concept_baseline.py
SP, CLEAR, LIFT, GAP_CHK, LAT = 2.0, 2.0, 1.6, 1.5, 3.0                 # grid, skin clearance, stack lift, part check, overlap
SING, FLIP, END_MARGIN = 10.0, 30.0, 1.0                                # fold margin (deg), largest step / frame (deg), race end mm
MAP_STEP = 1.5                                                          # need-map grid (deg)
CACHE = os.path.join(REPO, ".cache", "magrace")
Y_ARM = np.array([0.0, -1.0, 0.0])

SEEDS = dict(
    champ=dict(az=2.4305071427308924, el=80.67633718429899, a1=76.90180446920043, a2=66.74921235407174, wd=86.32769021001913,
               wa=21.829657347343378, branch=-1),                     # tools/concept_baseline.py CHAMP (r20 s1414 #4)
    final=dict(az=32.55, el=80.56, a1=77.41, a2=81.45, wd=71.38, wa=4.78, branch=-1),     # catalogue seed (1): cad_r18 final
    ring=dict(az=295.0, el=-35.0, a1=90.0, a2=90.0, wd=0.0, wa=0.0, branch=-1),           # seed (2): 2R (J1 into the back) + ring
)
PARAMS = dict(SEEDS["champ"], g1=40.0, c1=0.0, s1=0, g2=40.0, c2=0.0, s2=0, g3=40.0, c3=0.0, s3=1, cov=1.0, p=100.0, contour=0.0,
              R_est=70.0, passes=2)
SWEEP = dict(seed=list(SEEDS), g=(15, 165), c=(-180, 180), s=(0, 1), cov=(0.9, 1.0), p=(80, 100), contour=(0, 10))
KEYS = ("az", "el", "a1", "a2", "wd", "wa", "branch", "g1", "c1", "s1", "g2", "c2", "s2", "g3", "c3", "s3", "cov", "p", "contour")


# ---------------------------------------------------------------- small geometry
def bvec(az, el):                       # tools/concept_baseline.py
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):                   # tools/concept_baseline.py
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def perp(v, a): return unit(v - (v @ a) * a)


def wrapd(x): return (np.asarray(x) + 180.0) % 360.0 - 180.0


def circ_int(c1, r1, c2, r2, sign):     # tools/concept_baseline.py
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 0


def tri_ok(x, y, a, b, sing):           # tools/concept_baseline.py
    th = np.arccos(np.clip((x * y).sum(-1), -1, 1))
    return (th >= abs(a - b) + sing) & (th <= min(a + b, 2 * math.pi - a - b) - sing)


def frame(u, v):
    """orthonormal frames (n, 3, 3), columns [u, e, u x e], e = v made perpendicular to u"""
    e = unit(v - (v * u).sum(-1, keepdims=True) * u); return np.stack([u, e, np.cross(u, e)], -1)


def ang_about(w, p, q):
    """signed angle (rad) turning p onto q about the unit axis w (broadcasting)"""
    pp = p - (p * w).sum(-1, keepdims=True) * w; qq = q - (q * w).sum(-1, keepdims=True) * w
    return np.arctan2((w * np.cross(pp, qq)).sum(-1), (pp * qq).sum(-1))


def circ_range(a_deg, cov):
    """central `cov` share of circular angles (deg) -> (centre, half-span)"""
    a = np.asarray(a_deg, float)
    if not len(a): return 0.0, 0.0
    s = np.sort(wrapd(a)); g = np.diff(np.r_[s, s[0] + 360]); k = int(np.argmax(g)); c0 = s[(k + 1) % len(s)]
    rel = np.sort(wrapd(a - c0) % 360)
    lo, hi = (np.quantile(rel, [(1 - cov) / 2, 1 - (1 - cov) / 2]) if cov < 1 else (rel[0], rel[-1]))
    return float(wrapd(c0 + (lo + hi) / 2)), float((hi - lo) / 2)


# ---------------------------------------------------------------- the skin-need map (per bench pose, thorax frame)
class NeedMap:
    """per pose i: the smallest radius r >= 20 mm along each direction from GH with signed distance >= CLEAR (the first
    exit from the inside, sphere-traced on the bench's distance), on a lat-long grid (polar axis = +z, MAP_STEP deg)"""
    def __init__(self, B, log=print):
        self.B = B; self.th = np.arange(0, 180 + 1e-6, MAP_STEP) * D2R; self.ph = np.arange(0, 360, MAP_STEP) * D2R
        os.makedirs(CACHE, exist_ok=True)
        f = os.path.join(CACHE, f"need_{B.key}_{MAP_STEP}_{CLEAR}_{B.mode}.npy")
        if os.path.exists(f): self.M = np.load(f); return
        T, P = np.meshgrid(self.th, self.ph, indexing="ij")
        U = np.stack([np.sin(T) * np.cos(P), np.sin(T) * np.sin(P), np.cos(T)], -1).reshape(-1, 3)
        M = np.empty((len(B.poses), len(self.th), len(self.ph)), np.float32); t0 = time.time()
        for i in range(len(B.poses)):
            r = np.full(len(U), 20.0); act = np.ones(len(U), bool)
            for _ in range(80):
                if not act.any(): break
                a = np.nonzero(act)[0]; d = B.dist(i, U[a] * r[a, None]); st = CLEAR - d
                done = st < 0.15; act[a[done]] = False; r[a[~done]] += np.maximum(st[~done], 0.1)
                act &= r < 250
            r[r >= 250] = np.inf; M[i] = r.reshape(len(self.th), len(self.ph))
            if i % 20 == 0: log(f"  need map pose {i}/{len(B.poses)} {time.time() - t0:.0f} s")
        np.save(f + ".tmp.npy", M); os.replace(f + ".tmp.npy", f); self.M = M

    def __call__(self, ii, U):
        """skin need (mm) for poses ii (n,) and thorax unit directions U (n, m, 3) -> (n, m), bilinear"""
        th = np.arccos(np.clip(U[..., 2], -1, 1)) / (MAP_STEP * D2R); ph = (np.arctan2(U[..., 1], U[..., 0]) % (2 * math.pi)) / (MAP_STEP * D2R)
        nt, npp = self.M.shape[1:]
        t0 = np.clip(np.floor(th).astype(int), 0, nt - 2); ft = np.clip(th - t0, 0, 1)
        p0 = np.floor(ph).astype(int) % npp; fp = ph - np.floor(ph); p1 = (p0 + 1) % npp
        I = np.asarray(ii)[:, None] * np.ones_like(t0)
        M = self.M
        v = (M[I, t0, p0] * (1 - ft) * (1 - fp) + M[I, t0 + 1, p0] * ft * (1 - fp) + M[I, t0, p1] * (1 - ft) * fp + M[I, t0 + 1, p1] * ft * fp)
        return np.where(np.isfinite(v), v, 999.0)


# ---------------------------------------------------------------- kinematics (spherical 3R, member rotations)
class Kin:
    def __init__(self, d, HG, HGref):
        A1, A2 = d["a1"] * D2R, d["a2"] * D2R; self.b = bvec(d["az"], d["el"]); self.W0 = w_dir(d["wd"], d["wa"]); br = float(d["branch"])
        self.d = d; self.A1, self.A2, self.br = A1, A2, br
        p2r = None
        for H in [HGref] + list(HG):                       # reference = the rest frame if it closes, else the first that does
            p3 = H @ self.W0; p2, ok = circ_int(self.b[None], A1, p3[None], A2, br)
            if ok[0] and tri_ok(self.b[None], p3[None], A1, A2, SING * D2R)[0]: self.HGref = H; p2r = p2[0]; break
        self.okref = p2r is not None
        if p2r is None: self.HGref = HGref; p2r = perp(np.array([0.0, 1.0, 0.0]), self.b)
        self.p2r = p2r; self.p3r = self.HGref @ self.W0
        self.m = [self.b, self.p2r, self.p3r]                                  # joint axes, reference coordinates
        self.e = [perp(self.p2r, self.b), perp(self.p3r, self.p2r), perp(self.p2r, self.p3r)]   # azimuth 0 = toward the neighbour axis
        self.F1r = frame(self.b[None], self.p2r[None])[0]; self.F2r = frame(self.p2r[None], self.p3r[None])[0]

    def solve(self, HG):
        """-> ok (n,), T (4, n, 3, 3) member rotations (ref coords -> scapula frame), q (n, 3) deg"""
        n = len(HG); p3 = HG @ self.W0; b = np.broadcast_to(self.b, (n, 3))
        p2, ok = circ_int(b, self.A1, p3, self.A2, self.br); ok &= tri_ok(b, p3, self.A1, self.A2, SING * D2R); ok &= self.okref
        T = np.empty((4, n, 3, 3)); T[0] = np.eye(3)
        T[1] = frame(b, p2) @ self.F1r.T; T[2] = frame(p2, p3) @ self.F2r.T; T[3] = HG @ self.HGref.T
        q = np.empty((n, 3))
        for k in range(3):
            Rel = np.swapaxes(T[k], 1, 2) @ T[k + 1]; m, e = self.m[k], self.e[k]
            q[:, k] = ang_about(m, e, Rel @ e) / D2R
        return ok, T, q


# ---------------------------------------------------------------- sampled shapes (unit directions, reference coords)
def circle_strip(m, e, g, az, R, width=RACE_W, step=SP):
    """strip on the circle at polar g (rad) about m, azimuths az (rad, stations), on the sphere R: (ns, nc, 3)"""
    f = np.cross(m, e); ca, sa = np.cos(az)[:, None], np.sin(az)[:, None]
    rad = ca * e + sa * f
    D = math.cos(g) * m + math.sin(g) * rad; E = -math.sin(g) * m + math.cos(g) * rad        # E: across (meridian)
    c = np.arange(-width / 2, width / 2 + 1e-6, step) / R
    return unit(D[:, None, :] + c[None, :, None] * E[:, None, :])


def arc_az(lo, hi, g, R, step=SP):
    n = max(2, int(math.ceil(abs(hi - lo) * R * max(math.sin(g), 1e-3) / step)) + 1); return np.linspace(lo, hi, n)


def gc_strip(x0, x1, s0, s1, R, width, step=SP):
    """strap on the great circle x0 -> x1, from s0 mm past x0 to s1 mm short of x1 (sphere R): (ns, nc, 3), s (mm) or None"""
    ang = math.acos(float(np.clip(x0 @ x1, -1, 1))); a0 = s0 / R; a1 = ang - s1 / R
    if a1 - a0 < step / R: return None, None
    t = unit(x1 - (x1 @ x0) * x0); nrm = unit(np.cross(x0, t))
    s = np.linspace(a0, a1, max(2, int(math.ceil((a1 - a0) * R / step)) + 1))
    D = np.cos(s)[:, None] * x0 + np.sin(s)[:, None] * t
    c = np.arange(-width / 2, width / 2 + 1e-6, step) / R
    return unit(D[:, None, :] + c[None, :, None] * nrm[None, None, :]), s * R


class Part:
    def __init__(self, name, member, kind, D, t, joint=None, scored=True):
        self.name, self.member, self.kind, self.D, self.t, self.joint, self.scored = name, member, kind, D, t, joint, scored
        self.bot = None                                      # underside radius per station (ns,)
        self.R = None                                        # race: running-surface radius (constant)

    def topr(self): return np.full_like(self.bot, self.R) if self.kind == "race" else self.bot + self.t


# ---------------------------------------------------------------- design
class Design:
    def __init__(self, prm, ctx):
        self.p = p = dict(PARAMS, **prm); self.ctx = ctx; B = ctx.B
        self.kin = Kin(p, ctx.HG, ctx.HGref)
        self.ok, self.T, self.q = self.kin.solve(ctx.HG)
        okc, _, qc = self.kin.solve(ctx.HGc)                 # every fit-clip frame (10 fps): the races cover them too
        self.sides = [int(p["s1"]), int(p["s2"]), int(p["s3"])]
        # joint ranges: kinematically valid bench workspace poses + every valid fit-clip frame
        ws = np.array([k == "ws" for k in B.kind]) & self.ok
        self.qc, self.qh = [], []
        for k in range(3):
            c, h = circ_range(np.r_[self.q[ws, k], qc[okc, k]], p["cov"]); self.qc.append(c); self.qh.append(h)
        self.inr = self.in_range(self.q)
        # ranks: the carriage member rides above the race member at every joint
        rk = [0.0, 0, 0, 0]
        for k in range(3): rk[k + 1] = rk[k] + (1 if self.sides[k] == 0 else -1)
        self.rank = [r + 0.01 * j for j, r in enumerate(rk)]
        self.order = sorted(range(4), key=lambda j: self.rank[j])
        self.fitset = np.nonzero(self.ok & self.inr)[0]
        self.Rj = [p["R_est"]] * 3; self.Rl = {}
        for ps in range(int(p["passes"])):
            self.build(); self.fit()
            self.Rj = [float(min(x, 200.0)) for x in self.Rrun]
            for pt in self.parts:
                if pt.kind in ("strap", "neck"): self.Rl[pt.member] = float(np.clip(pt.bot.mean(), 30, 200))
        self.inr = self.in_range(self.q)
        self.token = (json.dumps({k: p[k] for k in KEYS}, sort_keys=True))

    # ---- joint ranges ------------------------------------------------------------------------------------------------
    def half_car(self, k, R):
        g = self.p[f"g{k + 1}"] * D2R; return (CAR_L / 2 + END_MARGIN) / (R * max(math.sin(g), 1e-3)) / D2R

    def in_range(self, q):
        out = np.ones(len(q), bool)
        for k in range(3):
            if self.qh[k] + self.half_car(k, self.Rj[k] if hasattr(self, "Rj") else self.p["R_est"]) >= 180: continue   # closed ring: no end
            out &= np.abs(wrapd(q[:, k] - self.qc[k])) <= self.qh[k] + 1e-6
        return out

    # ---- parts (reference coordinates of their member) -----------------------------------------------------------------
    def build(self):
        p = self.p; K = self.kin; self.parts = []; self.elem = {}
        self.Lh = []
        for k in range(3):
            g = p[f"g{k + 1}"] * D2R; R = self.Rj[k]; s = self.sides[k]; sgn = 1 if s == 0 else -1
            hc = self.half_car(k, R); Lh = min(180.0, self.qh[k] + hc); self.Lh.append(Lh)
            rm, cm = (k, k + 1) if s == 0 else (k + 1, k)
            c = p[f"c{k + 1}"] * D2R; az = arc_az(c - Lh * D2R, c + Lh * D2R, g, R)
            race = Part(f"race{k + 1}", rm, "race", circle_strip(K.m[k], K.e[k], g, az, R), RACE_T, joint=k)
            phi = c - sgn * self.qc[k] * D2R
            caz = arc_az(phi - (CAR_L / 2) / (R * max(math.sin(g), 1e-3)), phi + (CAR_L / 2) / (R * max(math.sin(g), 1e-3)), g, R)
            car = Part(f"car{k + 1}", cm, "car", circle_strip(K.m[k], K.e[k], g, caz, R), CAR_T, joint=k, scored=False)
            race.az = az; car.phi = phi; self.parts += [race, car]
            cl = circle_strip(K.m[k], K.e[k], g, az, R, width=0.0)[:, 0]          # race centreline
            cc = circle_strip(K.m[k], K.e[k], g, np.array([phi]), R, width=0.0)[0, 0]
            self.elem[(rm, k)] = dict(kind="race", pts=cl, ends=(cl[0], cl[-1]), part=race, R=R, closed=Lh >= 180, m=K.m[k])
            self.elem[(cm, k)] = dict(kind="car", pts=cc[None], part=car, R=R, m=K.m[k])
        for mem, (ja, jb) in ((1, (0, 1)), (2, (1, 2))):                     # link straps
            ea, eb = self.elem[(mem, ja)], self.elem[(mem, jb)]
            ang = np.arccos(np.clip(ea["pts"] @ eb["pts"].T, -1, 1)); ia, ib = np.unravel_index(np.argmin(ang), ang.shape)
            xa, xb = ea["pts"][ia], eb["pts"][ib]
            Rs = self.Rl.get(mem, 0.5 * (ea["R"] + eb["R"]))
            s0 = self.trim(ea, ia, xa, xb, Rs); s1 = self.trim(eb, ib, xb, xa, Rs)
            D, smm = gc_strip(xa, xb, s0, s1, Rs, LK_W)
            if D is not None:
                pt = Part(f"link{mem}", mem, "strap", D, LK_T); pt.smm = smm; pt.ends = (ea, eb); pt.Ltot = float(math.acos(np.clip(xa @ xb, -1, 1)) * Rs)
                self.parts.append(pt)
        ea = self.elem[(3, 2)]                                                # BOTTOM's neck, toward the humerus axis
        harm = self.kin.HGref @ Y_ARM
        if ea["kind"] == "car": x0 = ea["pts"][0]
        else: x0 = ea["pts"][np.argmin(np.arccos(np.clip(ea["pts"] @ harm, -1, 1)))] if not ea["closed"] else ea["pts"][len(ea["pts"]) // 2]
        th0 = math.acos(float(np.clip(x0 @ harm, -1, 1)))
        if th0 > 1e-3:
            x1 = unit(math.cos(min(NECK_DEG * D2R, th0)) * x0 + math.sin(min(NECK_DEG * D2R, th0)) * perp(harm, x0))
            Rs = self.Rl.get(3, ea["R"])
            D, smm = gc_strip(x0, x1, self.trim(ea, None, x0, x1, Rs), 0.0, Rs, NECK_W)
            if D is not None:
                pt = Part("neck", 3, "neck", D, NECK_T); pt.smm = smm; pt.ends = (ea, None); pt.Ltot = 1e9; self.parts.append(pt)

    @staticmethod
    def trim(el, i, x, y, R):
        """mm to skip from point x of element el along the great circle toward y (its footprint + 0.5 mm)"""
        t = unit(np.cross(el["m"], x)); n = unit(np.cross(x, t))                 # race tangent / across at x
        dvec = perp(y, x); ca = abs(float(dvec @ t)); sa = abs(float(dvec @ n))
        if el["kind"] == "car": return min((CAR_L / 2) / max(ca, 1e-6), (RACE_W / 2) / max(sa, 1e-6)) + 0.5
        if i is not None and not el["closed"] and i in (0, len(el["pts"]) - 1):
            out = el["pts"][0] - el["pts"][1] if i == 0 else el["pts"][-1] - el["pts"][-2]
            if float(dvec @ unit(out)) > 0: return 0.5                         # leaves the race end outward
        return min((RACE_W / 2) / max(sa, 1e-6), 40.0) + 0.5

    # ---- posing ----------------------------------------------------------------------------------------------------------
    def M(self, member, ii):
        """reference -> thorax rotations (n, 3, 3) of a member at bench poses ii"""
        return self.ctx.RS[ii] @ self.T[member][ii]

    def posed_dirs(self, part, ii):
        return np.einsum("nij,mj->nmi", self.M(part.member, ii), part.D.reshape(-1, 3))

    # ---- fitting ----------------------------------------------------------------------------------------------------------
    def fit(self):
        p = self.p; ctx = self.ctx; V = self.fitset; self.Rrun = list(self.Rj); placed = []
        if not len(V):
            for pt in self.parts: pt.bot = np.full(pt.D.shape[0], 999.0)
            return
        for mem in self.order:
            mine = [pt for pt in self.parts if pt.member == mem]
            for kind in ("race", "car", "strap", "neck"):
                for pt in [x for x in mine if x.kind == kind]:
                    if kind == "car":
                        k = pt.joint; pt.bot = np.full(pt.D.shape[0], self.Rrun[k] + BALL_GAP); continue
                    self.shape(pt, self.need(pt, V, placed), V, placed)
            placed += mine

    def need(self, pt, V, placed):
        """skin need (map) and stacking need, each (|V|, ns, nc)"""
        U = self.posed_dirs(pt, V); sh = (len(V),) + pt.D.shape[:2]
        skin = self.ctx.NM(V, U)
        low = [q for q in placed if self.rank[q.member] < self.rank[pt.member]]
        stack = self.stack_need(pt, V, U, low) if low else np.full(U.shape[:2], -1.0)
        return skin.reshape(sh), stack.reshape(sh)

    def stack_need(self, pt, V, U, low):
        out = np.full(U.shape[:2], -1.0)
        for j, i in enumerate(V):
            Y = np.concatenate([self.posed_dirs(q, np.array([i]))[0] for q in low]); top = np.concatenate([q.topr().repeat(q.D.shape[1]) for q in low])
            dd, ix = cKDTree(Y).query(U[j], k=16, distance_upper_bound=LAT / 35.0)
            hit = np.isfinite(dd)
            if not hit.any(): continue
            ixc = np.where(hit, ix, 0); lat = 2 * np.arcsin(np.clip(dd / 2, 0, 1)) * top[ixc]
            out[j] = np.where(hit & (lat < LAT), top[ixc] + LIFT, -1.0).max(1)
        return out

    def shape(self, pt, nds, V, placed):
        """fix the part's shape: the p-th percentile over the fit poses of the per-pose need; the skin need is then
        replaced twice by the bench's own distance at the fitted shape (radius + CLEAR - d), the map being bilinear"""
        p = self.p; pc = p["p"]; skin, stack = nds
        for it in range(3):
            st = np.maximum(skin, stack).max(2)                             # (|V|, ns) per-station need
            if pt.kind == "race":
                k = pt.joint
                if p["contour"] > 0:
                    u = np.percentile(st, pc, axis=0); R = float(u.max()) + RACE_T
                    pt.bot = np.maximum(u, R - RACE_T - p["contour"])
                else:
                    R = float(np.percentile(st.max(1), pc)) + RACE_T; pt.bot = np.full(st.shape[1], R - RACE_T)
                self.Rrun[k] = R; pt.R = R
            else:
                r = np.percentile(st, pc, axis=0); ea, eb = pt.ends
                lv = lambda e: (self.Rrun[e["part"].joint] + BALL_GAP) if e["kind"] == "car" else (self.Rrun[e["part"].joint] - LK_T)
                if ea is not None:
                    s = pt.smm - pt.smm[0]; r = np.maximum(r, lv(ea) - (s + 1.0)); r[0] = max(r[0], lv(ea))
                if eb is not None:
                    se = pt.smm[-1] - pt.smm; r = np.maximum(r, lv(eb) - (se + 1.0)); r[-1] = max(r[-1], lv(eb))
                pt.bot = r
            if it == 2: break
            U = self.posed_dirs(pt, V); rr = np.broadcast_to(pt.bot[:, None], pt.D.shape[:2]).reshape(-1)
            d = np.stack([self.ctx.B.dist(int(i), U[j] * rr[:, None]) for j, i in enumerate(V)])
            skin = np.minimum(rr[None] + CLEAR - d, 999.0).reshape(skin.shape)

    # ---- pose -> metal ----------------------------------------------------------------------------------------------------
    def volume(self, pt, i):
        """skin side, top and layers <= 2 mm apart through the thickness (thorax)"""
        M = self.M(pt.member, np.array([i]))[0]; U = (pt.D @ M.T).reshape(-1, pt.D.shape[1], 3)
        b = pt.bot[:, None]; tp = pt.topr()[:, None]; nl = max(3, int(math.ceil(float((tp - b).max()) / 2.0)) + 1)
        L = [(U * (b + (tp - b) * f)[..., None]).reshape(-1, 3) for f in np.linspace(0, 1, nl)]
        return L[0], L[-1], np.concatenate(L)

    def interfere(self, vols):
        names = list(vols)
        for a, b in itertools.combinations(names, 2):
            A, Bp = self.byname[a], self.byname[b]
            if A.member == Bp.member: continue
            if A.joint is not None and A.joint == Bp.joint and {A.kind, Bp.kind} == {"race", "car"}: continue
            X = vols[a]; Y = vols[b]
            ca, cb = X.mean(0), Y.mean(0)
            if np.linalg.norm(ca - cb) > np.linalg.norm(X - ca, axis=1).max() + np.linalg.norm(Y - cb, axis=1).max() + GAP_CHK: continue
            if cKDTree(X).query(Y, distance_upper_bound=GAP_CHK)[0].min() < GAP_CHK: return f"{a}/{b}"
        return None

    def metal(self, i):
        """(points (k, 3) thorax or None, reason)"""
        B = self.ctx.B
        if not self.ok[i]: return None, "closure"
        if not self.inr[i]: return None, "off race"
        if B.kind[i] == "clip":
            ok, why = self.ctx.clip_status(self, int(B.idx[i]))
            if not ok: return None, why
        if any(pt.bot.max() >= 900 for pt in self.parts): return None, "no radius"
        self.byname = {pt.name: pt for pt in self.parts}
        vols = {}; scored = []; other = []
        for pt in self.parts:
            bot, top, vols[pt.name] = self.volume(pt, i)
            (scored if pt.scored else other).append(bot); other.append(top)
        w = self.interfere(vols)
        if w: return None, "interference " + w
        P = np.concatenate(scored); O = np.concatenate(other); do = B.dist(i, O)
        if do.min() < 0: P = np.r_[P, O[np.argmin(do)][None]]
        return P, ""


# ---------------------------------------------------------------- context: bench, poses, need map, clip continuity
class Ctx:
    def __init__(self, B, log=print):
        Z = CB._poses_all(); self.B = B; self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        names = list(Z["NAMES"]); cid = Z["CID"]
        self.clip_ix = {n: np.nonzero(cid == names.index(n))[0] for n in CB.FIT}
        allc = np.concatenate(list(self.clip_ix.values())); self.HGc = Z["HG"][allc].astype(float); self.allc = allc
        self.HGref = Z["HG"][self.clip_ix["Raise overhead"][0]].astype(float)
        self.NM = NeedMap(B, log); self._cs = {}

    def clip_status(self, D, j):
        if D.token not in self._cs:
            okc, _, qc = D.kin.solve(self.HGc); inr = D.in_range(qc); st = {}; o = 0
            for n in CB.FIT:
                ix = self.clip_ix[n]; last = None
                for kk, jj in enumerate(ix):
                    g = o + kk
                    if not okc[g]: st[int(jj)] = (False, "closure"); continue
                    if not inr[g]: st[int(jj)] = (False, "off race"); continue
                    if last is not None and np.abs(wrapd(qc[g] - last)).max() > FLIP: st[int(jj)] = (False, "flip"); continue
                    st[int(jj)] = (True, ""); last = qc[g]
                o += len(ix)
            self._cs = {D.token: st}
        return self._cs[D.token].get(j, (False, "missing"))


def evaluate(prm, ctx):
    t = time.time(); D = Design(prm, ctx); B = ctx.B; B.reset(); why = {}
    for i in range(len(B.poses)):
        P, w = D.metal(i)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None)
        else:
            d = B.record(i, P)
            if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1)
    r["shape"] = dict(R=[round(x, 1) for x in D.Rrun], span=[round(2 * x, 1) for x in D.Lh], rank=[round(x, 2) for x in D.rank],
                      links={pt.name: [round(float(pt.bot.min()), 1), round(float(pt.bot.max()), 1)] for pt in D.parts if pt.kind in ("strap", "neck")},
                      kin_valid=round(float(D.ok.mean()), 3), fitset=int(len(D.fitset)))
    return r, D


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def sweep(configs, ctx, out=SWEEP_OUT, tag="", log=print):
    rows = json.load(open(out)) if os.path.exists(out) else []
    best = None
    for prm in configs:
        prm = dict(PARAMS, **prm)
        try: r, D = evaluate(prm, ctx)
        except Exception as e:
            import traceback; traceback.print_exc(); log(f"ERR {e}"); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params={k: prm[k] for k in KEYS}, inband14=r["inband14"],
                   inband10=r["inband10"], reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"],
                   mode=r["mode"], stage=tag)
        rows.append(row)
        if out:
            json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        log(f"[{row['k']}] {tag} gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
            f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r['secs']} s | " + " ".join(f"{k}={prm[k]}" for k in KEYS[7:]))
        if best is None or r["gap"] < best[0]["gap"]: best = (r, prm)
    return rows, best


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = (id(B), json.dumps(prm, sort_keys=True))
    if key not in _cache:
        _cache.clear(); ctx = Ctx(B); _cache[key] = Design(prm, ctx)
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=60, n_ws=160); ctx = Ctx(B)
        for s in ("champ", "ring"):
            sweep([dict(SEEDS[s])], ctx, out=None, tag="check")
