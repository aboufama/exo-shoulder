"""human-closed-telescopes: human-closed 3-UPS 'artificial deltoid' - three straight telescopes from dome brackets
(scapula frame) to studs on the upper arm, no exo joint at GH (the user's own GH joint closes the loop). Concept screen.

Topology (docs/concepts/catalogue.json, id human-closed-telescopes):
    S -> bracket k (S-fixed plate on the dome) -> U-joint (passive, 2) -> telescope k (ACTIVE prismatic, keyed, its
    length sensed) -> arm-end joint (passive, 3) on an arm saddle / BOTTOM -> H.      k = 1, 2, 3 (anterior, middle, posterior)
DOF: 3 ACTIVE (the three strokes), 15 PASSIVE (3 x U 2 + 3 x 3 at the arm end), every passive coordinate set by the
arm's pose (closed form L_k = |B_k - A_k|, the U and arm-end angles follow from the strut direction) - no spare.

Model (thorax mm, origin = GH; scapula RS and humerus RS @ HG rotations of each bench pose from the bench's pose file,
as tools/concept_baseline.py; humerus frame = band_impl's: -y down the arm, +z lateral, +x anterior):
  * parts at their real size (spec, with the corrections marked SPEC FIX):
      - joints: O14 envelope (sphere r 7) at every anchor (U-joint) and every arm stud;
      - telescope, single stage: outer O10 tube from the U-joint, inner O8 tube from the arm joint, both of length
        Lt = L_lo - 2 x 7 - 2 (they just fit between the joints at the shortest stroke L_lo), >= 25 mm bushing overlap at
        the longest -> L_hi = 2 Lt + 14 - 25 = 2 L_lo - 43 mm. SPEC FIX: the spec's "0.55 L_min tubes, L_max <= 1.85
        L_min" contradict each other (0.55 L_min tubes give a 1.1 ratio); the real single-stage limit is 2 L_lo - 43
        (ratio 1.57 at L_lo 100, 1.69 at 140). L_lo is chosen per strut to cover the most bench poses.
      - S brackets: plate t 4 under each U-joint (pad r 9) + two 10-wide straps joining the anchors (the two shortest
        great-circle edges) - SPEC FIX: the spec left the three brackets unconnected; they must be one S-fixed part on
        the user's scapula handler. Undersides skin-fitted (K3: percentile p over the fit poses of the outermost skin
        crossing along the ray from GH, + 2 mm), the U-joint centre at pad top + 7 + h_A.
      - arm saddle: plate t 4 (pad r 9) under each skin-mounted stud, 12-wide straps joining the studs on each side of
        BOTTOM's bar and from the stud nearest the bar to the bar's edge (merged with BOTTOM, which may be cut / merged),
        K3-fitted in the humerus frame (rays from the humerus axis); the stud centre at pad top + 7 + h_B.
        SPEC FIX: the spec put B2 at 67.5 + 7 mm along Wb - inside BOTTOM's bar (underside 67.5, 76.1 beyond 56 mm
        down, 6.5 thick, band_impl). A stud whose footprint falls on the bar (|theta| < 22 deg, s >= 40) sits ON the bar:
        centre at bar top + 7 + h_B.
      - BOTTOM's bar (user part, band_impl geometry: 32 wide, 6.5 thick, 40-220 mm down) is an obstacle for every strut
        and joint not mounted on it (>= 1 mm).
  * taken iff: the closed form (residual 0) gives every L_k inside its stroke [L_lo, L_hi]; every U-joint bend inside
    +-60 deg (first axis fixed in the bracket / saddle, fitted to the strut directions; the second axis perpendicular
    to the strut; the arm end is a U-joint + strut-spin bearing - SPEC FIX: a ball stud would need the cone printed by
    `check`, far beyond a ball joint's +-25-30 deg); the conditioning |det [unit(B_k x u_k)]| >= det (0.10); no two
    non-adjacent parts within 1 mm (tube-tube, tube-joint, joint-joint, tube / joint vs bracket and saddle plates and
    BOTTOM's bar); along each fit clip at its full 10 fps no joint angle jumps > 30 deg between frames (the closed form
    has no branch, so this only fires near a U-joint singularity); then the bench's contact rule on every metal sample.
  * scored metal (bench in-band): skin-facing surfaces at ~1 point / 4 mm2: plate undersides on a 2 mm grid (as the
    baseline's strap undersides), tubes 16 (O10) / 13 (O8) points around every 2 mm along and joint spheres 154 points,
    of which the half nearer the skin is the skin-facing surface (the farther half can never be nearer the skin, so
    contact is decided exactly on the recorded half).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/human-closed-telescopes.py maps 60 160   # skin requirement maps
    ... human-closed-telescopes.py check [n_clip n_ws]    # spec default: per-strut table, a few poses
    ... human-closed-telescopes.py pairs                  # pair library (anchor x stud chords) on Bench(60, 160)
    ... human-closed-telescopes.py sweep                  # triples from the pair library, then the full model
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402
BP = CB.BP

ID = "human-closed-telescopes"
NAME = "Human-closed 3-UPS 'artificial deltoid': straight telescopes from dome brackets to arm studs"
D2R = math.pi / 180
R_J = 7.0                     # joint envelope (O14 U-joint / arm joint)
R_OUT, R_IN = 5.0, 4.0        # O10 outer / O8 inner tube
OVL, G_END = 25.0, 2.0        # bushing overlap at full stroke, end gap at the shortest
T_BR, W_BR = 4.0, 10.0        # S bracket plate, strap width
T_SD, W_SD = 4.0, 12.0        # arm saddle plate, strap width
PAD_R = 9.0                   # pad under each joint
CLEAR = 2.0                   # K3 clearance
SP = 2.0                      # sample spacing (1 point / 4 mm2)
GAP = 1.0                     # mm between non-adjacent parts
BETA = 60.0                   # U-joint bend limit (deg)
FLIP = 30.0                   # deg per 10 fps frame
WB = np.array([0.0, -0.0713, 0.9975]); WB /= np.linalg.norm(WB)          # BOTTOM's bar (band_impl): normal, along, across
DB = np.array([0.0, -0.9975, -0.0713]); DB = DB - (DB @ WB) * WB; DB /= np.linalg.norm(DB); EB = np.cross(WB, DB)
Z_BAR, JOG0, JOG1, JOG, T_BOT, BAR_HW, BAR_D0, BAR_D1 = 67.5, 34.0, 56.0, 8.6, 6.5, 16.0, 40.0, 220.0
TH_BAR = 22.0                 # |theta| below which a stud footprint falls on the bar

PARAMS = dict(a=[(150.0, 35.0), (85.0, 70.0), (-15.0, 40.0)],               # anchors bvec(az, el) in S (az 0 post., 90 lat., 180 ant.)
              b=[(95.0, -20.0), (85.0, 0.0), (105.0, 55.0)],               # studs (s mm down the humerus axis, theta deg, + posterior)
              h_A=0.0, h_B=0.0, p=100.0, det=0.10, beta=BETA)
SWEEP = dict(a="dome grid az -60..180 / el 0..85 (pair library), then +-10 deg refine", b="s 50..190 mm, theta -80..+110 deg",
             h_A=(0, 4, 8), h_B=(0, 4, 8), p=(90, 95, 100), selection="triples of pairs from the pair library (one per anchor region)")


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def bvec(az, el):
    az, el = np.asarray(az, float) * D2R, np.asarray(el, float) * D2R
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def adir(th):
    th = np.asarray(th, float) * D2R
    return np.stack([-np.sin(th), 0 * th, np.cos(th)], -1)


def perp(u):
    a = np.array([1.0, 0.0, 0.0]) if abs(u[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = unit(a - (a @ u) * u); return e1, np.cross(u, e1)


def zlo_bar(d):
    s = np.clip((np.asarray(d, float) - JOG0) / (JOG1 - JOG0), 0, 1); s = 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5
    return Z_BAR + JOG * s


# ------------------------------------------------------------------------------------------------ skin requirement maps
AZ = np.arange(-120.0, 213.0, 3.0); EL = np.arange(-30.0, 88.1, 3.0)     # dome: rays from GH, S frame
SS = np.arange(20.0, 241.0, 4.0); TH = np.arange(-110.0, 141.0, 5.0)     # arm: rays from the humerus axis, humerus frame


def frames(B):
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    return RS, np.einsum("nij,njk->nik", RS, HG)


def trace(B, i, O, D, r0, it=70):
    """outermost skin crossing along rays O + r D (k, 3), sphere tracing inward from r0 with B.dist: radius (k,);
    r0 if the start is inside the body, 0 if the ray never meets the skin"""
    r = np.full(len(D), float(r0)); act = np.ones(len(D), bool); hit = np.zeros(len(D), bool)
    for _ in range(it):
        if not act.any(): break
        a = np.nonzero(act)[0]; d = B.dist(i, O[a] + D[a] * r[a, None])
        done = d < 0.3; hit[a[done]] = True; act[a[done]] = False
        r[a[~done]] -= np.maximum(d[~done], 0.5); act &= ~(r < 3)
    return np.where(hit, r, 0.0)


def map_path(key):
    return os.path.join(REPO, ".cache", "concept_models", ID, f"req_{key}.npz")


def build_maps(B, log=print):
    path = map_path(B.key)
    if os.path.exists(path): log("exists " + path); return path
    os.makedirs(os.path.dirname(path), exist_ok=True); RS, RA = frames(B); t = time.time()
    Dd = bvec(*np.meshgrid(AZ, EL, indexing="ij")).reshape(-1, 3)
    Sg, Tg = np.meshgrid(SS, TH, indexing="ij"); Oa = np.stack([0 * Sg, -Sg, 0 * Sg], -1).reshape(-1, 3); Da = adir(Tg).reshape(-1, 3)
    MD = np.zeros((len(B.poses), len(AZ), len(EL)), np.float32); MA = np.zeros((len(B.poses), len(SS), len(TH)), np.float32)
    for i in range(len(B.poses)):
        MD[i] = trace(B, i, np.zeros_like(Dd), Dd @ RS[i].T, 230.0).reshape(len(AZ), len(EL))
        MA[i] = trace(B, i, Oa @ RA[i].T, Da @ RA[i].T, 140.0).reshape(len(SS), len(TH))
        if i % 10 == 0: log(f"  maps {i}/{len(B.poses)} {time.time() - t:.0f} s ({B.mode})")
    np.savez(path + ".tmp.npz", MD=MD, MA=MA); os.replace(path + ".tmp.npz", path); log(f"saved {path} {time.time() - t:.0f} s"); return path


def bilin(M, g1, g2, x1, x2):
    """M (n, a, b) on grids g1, g2 (uniform) at (x1, x2) (m,) -> (n, m)"""
    f1 = np.clip((np.asarray(x1) - g1[0]) / (g1[1] - g1[0]), 0, len(g1) - 1 - 1e-9); f2 = np.clip((np.asarray(x2) - g2[0]) / (g2[1] - g2[0]), 0, len(g2) - 1 - 1e-9)
    i1 = np.floor(f1).astype(int); i2 = np.floor(f2).astype(int); u = f1 - i1; v = f2 - i2
    return (M[:, i1, i2] * (1 - u) * (1 - v) + M[:, i1 + 1, i2] * u * (1 - v) + M[:, i1, i2 + 1] * (1 - u) * v + M[:, i1 + 1, i2 + 1] * u * v)


def azel(D):
    D = unit(D); return np.degrees(np.arctan2(D[..., 2], -D[..., 0])), np.degrees(np.arcsin(np.clip(D[..., 1], -1, 1)))


# ------------------------------------------------------------------------------------------------ sampled shapes
def gc_strap(u, v, width, r_ref=50.0):
    """unit directions of a strap on the great circle u -> v (S frame), 2 mm grid at r_ref: (m, 3)"""
    ang = math.acos(np.clip(u @ v, -1, 1)); n = unit(np.cross(u, v)); e2 = np.cross(n, u)
    s = np.linspace(0, ang, max(2, int(ang * r_ref / SP) + 1)); c = np.arange(-width / 2, width / 2 + 1e-6, SP) / r_ref
    D = np.cos(s)[:, None] * u + np.sin(s)[:, None] * e2
    return unit(D[:, None, :] * np.cos(c)[None, :, None] + n[None, None, :] * np.sin(c)[None, :, None]).reshape(-1, 3)


def dome_disc(u, rr, r_ref=50.0):
    g = np.arange(-rr, rr + 1e-6, SP); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rr ** 2 + 1e-9
    e1, e2 = perp(u); return unit(u[None] + (X[k][:, None] * e1 + Y[k][:, None] * e2) / r_ref)


def arm_strap(p1, p2, width, r_ref=55.0):
    """(s, theta) samples of a strap from p1 to p2 = (s, theta) on the arm, 2 mm grid (theta arc at r_ref): (m, 2)"""
    a = np.array([p1[0], p1[1] * D2R * r_ref]); b = np.array([p2[0], p2[1] * D2R * r_ref]); L = np.linalg.norm(b - a)
    if L < 1e-6: return np.zeros((0, 2))
    t = (b - a) / L; n = np.array([-t[1], t[0]])
    s = np.linspace(0, L, max(2, int(L / SP) + 1)); c = np.arange(-width / 2, width / 2 + 1e-6, SP)
    P = a[None, None] + s[:, None, None] * t + c[None, :, None] * n
    P = P.reshape(-1, 2); return np.stack([P[:, 0], P[:, 1] / (r_ref * D2R)], 1)


def arm_disc(p, rr, r_ref=55.0):
    g = np.arange(-rr, rr + 1e-6, SP); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rr ** 2 + 1e-9
    return np.stack([p[0] + X[k], p[1] + Y[k] / (r_ref * D2R)], 1)


def arm_pts(st, rho):
    """humerus-frame points of (s, theta) samples (m, 2) at radius rho (..., m) from the axis"""
    return np.stack([0 * st[:, 0], -st[:, 0], 0 * st[:, 0]], -1) + rho[..., None] * adir(st[:, 1])


def sphere_pts(n=154):
    k = np.arange(n) + 0.5; ph = np.arccos(1 - 2 * k / n); th = math.pi * (1 + 5 ** 0.5) * k
    return np.stack([np.cos(th) * np.sin(ph), np.sin(th) * np.sin(ph), np.cos(ph)], 1)


SPH = sphere_pts(int(round(4 * math.pi * R_J ** 2 / 4.0)))


def tube_pts(P0, P1, r):
    """(N, 3) start / end points of a tube axis -> ring samples (N, nr, na, 3), rings every 2 mm, na around (~2 mm)"""
    L = np.linalg.norm(P1 - P0, axis=-1); nr = max(2, int(np.nanmax(L) / SP) + 1); na = max(8, int(round(2 * math.pi * r / SP)))
    u = unit(P1 - P0); e1 = unit(np.cross(u, np.where(np.abs(u[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))))
    e2 = np.cross(u, e1); t = np.linspace(0, 1, nr); a = np.linspace(0, 2 * math.pi, na, endpoint=False)
    C = P0[:, None] + (P1 - P0)[:, None] * t[None, :, None]
    ring = np.cos(a)[None, :, None] * e1[:, None] + np.sin(a)[None, :, None] * e2[:, None]
    return C[:, :, None, :] + r * ring[:, None, :, :], L


def seg_seg(p0, p1, q0, q1):
    """distance between segments p0-p1 and q0-q1 (N, 3) each -> (N,)"""
    d1 = p1 - p0; d2 = q1 - q0; r = p0 - q0
    a = (d1 * d1).sum(-1); e = (d2 * d2).sum(-1); f = (d2 * r).sum(-1); c = (d1 * r).sum(-1); b = (d1 * d2).sum(-1)
    den = a * e - b * b
    s = np.clip(np.where(den > 1e-9, (b * f - c * e) / np.where(den > 1e-9, den, 1), 0.0), 0, 1)
    t = (b * s + f) / np.where(e > 1e-9, e, 1)
    t = np.clip(t, 0, 1); s = np.clip(np.where(a > 1e-9, (b * t - c) / np.where(a > 1e-9, a, 1), 0.0), 0, 1)
    return np.linalg.norm(p0 + d1 * s[..., None] - q0 - d2 * t[..., None], axis=-1)


def pt_seg(P, a, b):
    """distance of points P (N, m, 3) to segments a-b (N, 3) -> (N, m)"""
    d = b - a; L2 = (d * d).sum(-1)[:, None]; t = np.clip(((P - a[:, None]) * d[:, None]).sum(-1) / np.maximum(L2, 1e-9), 0, 1)
    return np.linalg.norm(P - a[:, None] - t[..., None] * d[:, None], axis=-1)


def bar_dist(Ph):
    """distance (mm) of humerus-frame points Ph (..., 3) to BOTTOM's bar box (0 inside)"""
    z, d, e = Ph @ WB, Ph @ DB, Ph @ EB; lo = zlo_bar(d)
    dz = np.maximum(np.maximum(lo - z, z - (lo + T_BOT)), 0); dd = np.maximum(np.maximum(BAR_D0 - d, d - BAR_D1), 0)
    de = np.maximum(np.abs(e) - BAR_HW, 0)
    return np.sqrt(dz ** 2 + dd ** 2 + de ** 2)


# ------------------------------------------------------------------------------------------------ context (per bench)
class Ctx:
    def __init__(self, B, log=print):
        self.B = B; self.RS, self.RA = frames(B); self.n = len(B.poses)
        path = map_path(B.key)
        if not os.path.exists(path): build_maps(B, log)
        z = np.load(path); self.MD = z["MD"].astype(float); self.MA = z["MA"].astype(float)
        self.clip = np.array([k == "clip" for k in B.kind]); self.ws = ~self.clip
        self.w = np.where(self.clip, 1.0 / self.clip.sum(), 1.0 / self.ws.sum())             # coverage weights (follow + reach)
        # full-rate continuity: per bench clip frame, the full-rate frames since the previous bench frame of its clip
        Z = CB._poses_all(); cid, fi = Z["CID"], Z["FI"]; self.Zfull = Z
        self.path = {}
        for c, js in B.clip_order().items():
            prev = None
            for j in js:
                zi = B.idx[j]; same = np.nonzero(cid == cid[zi])[0]; same = same[np.argsort(fi[same])]
                if prev is None: self.path[j] = np.array([zi])
                else:
                    a, b = fi[prev], fi[zi]; sel = same[(fi[same] >= min(a, b)) & (fi[same] <= max(a, b))]
                    self.path[j] = sel if a <= b else sel[::-1]
                prev = zi
        self.fullHG = Z["HG"].astype(float); self.fullRS = Z["RS"].astype(float)

    def dome(self, D, I=None):
        """outermost skin radius under S-frame unit directions D (m, 3) for poses I -> (n, m)"""
        a, e = azel(D); M = self.MD if I is None else self.MD[I]; return bilin(M, AZ, EL, a, e)

    def arm(self, st, I=None):
        M = self.MA if I is None else self.MA[I]; return bilin(M, SS, TH, st[:, 0], st[:, 1])


def fit(req, mask, p):
    """K3: percentile p over the masked poses of the requirement (n, m) + clearance -> (m,)"""
    r = req[mask] if mask.any() else req
    return np.percentile(r, p, axis=0, method="higher") + CLEAR


def best_axis(U, wts, beta):
    """first U-joint axis a (unit) maximising the weighted share of strut directions U (n, 3) within +-beta of the plane
    normal to a (ties: the smaller worst bend). Returns a, ok (n,), bend (n,) deg"""
    k = np.arange(2000) + 0.5; ph = np.arccos(1 - k / 2000); th = math.pi * (1 + 5 ** 0.5) * k        # hemisphere
    A = np.stack([np.cos(th) * np.sin(ph), np.sin(th) * np.sin(ph), np.cos(ph)], 1)
    bend = np.degrees(np.arcsin(np.clip(np.abs(U @ A.T), 0, 1)))                                          # (n, 2000)
    cov = (wts[:, None] * (bend <= beta)).sum(0); worst = np.where(bend <= beta, bend, 0).max(0)
    j = np.lexsort((worst, -cov))[0]; return A[j], bend[:, j] <= beta, bend[:, j]


def stroke_choice(L, okm, wts, two_stage=False):
    """choose L_lo per strut maximising the weighted coverage of the poses that pass everything else (okm) -> lo, hi, in (n, 3)"""
    c = 2 * R_J + G_END
    hi_of = (lambda lo: 3 * (lo - c) + 2 * R_J - 2 * OVL) if two_stage else (lambda lo: 2 * (lo - c) + 2 * R_J - OVL)
    lo = np.array([np.nanmin(L[:, k]) for k in range(3)]); lo = np.maximum(lo, c + OVL + 10)
    inr = lambda k, l: (L[:, k] >= l) & (L[:, k] <= hi_of(l))
    for _ in range(3):
        for k in range(3):
            others = okm.copy()
            for j in range(3):
                if j != k: others &= inr(j, lo[j])
            cand = np.unique(np.r_[np.maximum(L[okm, k], c + OVL + 10), lo[k]])
            sc = [(wts * (others & inr(k, l))).sum() for l in cand]
            lo[k] = cand[int(np.argmax(sc))]
    m = np.ones(len(L), bool)
    for k in range(3): m &= inr(k, lo[k])
    return lo, np.array([hi_of(l) for l in lo]), m


# ------------------------------------------------------------------------------------------------ design
class Design:
    def __init__(self, p, ctx, two_stage=False):
        self.p = p = dict(PARAMS, **p); self.c = ctx; n = ctx.n; self.two = two_stage
        self.ad = bvec(*np.array(p["a"]).T)                                  # (3, 3) anchor directions, S frame
        self.st = np.array(p["b"], float)                                    # (3, 2) studs (s, theta)
        self.onbar = (np.abs(self.st[:, 1]) < TH_BAR) & (self.st[:, 0] >= BAR_D0)
        fitmask = np.ones(n, bool)
        for it in range(2):
            self.shape(fitmask)
            self.kin()
            fitmask = self.kvalid if self.kvalid.sum() >= 10 else np.ones(n, bool)

    # ---- S-fixed and arm-fixed plates, joint centres -----------------------------------------------------------
    def shape(self, fm):
        p, c = self.p, self.c
        self.pads = [dome_disc(self.ad[k], PAD_R) for k in range(3)]
        rp = [fit(c.dome(D), fm, p["p"]) for D in self.pads]
        self.rpad = rp
        self.A = np.array([(rp[k].max() + T_BR + R_J + p["h_A"]) * self.ad[k] for k in range(3)])           # S frame
        ang = [(i, j, math.acos(np.clip(self.ad[i] @ self.ad[j], -1, 1))) for i, j in ((0, 1), (1, 2), (0, 2))]
        ang.sort(key=lambda x: x[2]); self.edges = [(i, j) for i, j, _ in ang[:2]]
        Ds = np.concatenate([gc_strap(self.ad[i], self.ad[j], W_BR) for i, j in self.edges] + self.pads)
        self.brD = Ds; self.brR = fit(c.dome(Ds), fm, p["p"])                                                    # bracket underside
        # arm side
        Bh = np.zeros((3, 3)); pieces = []
        for k in range(3):
            s, th = self.st[k]
            if self.onbar[k]:
                Bh[k] = (zlo_bar(s) + T_BOT + R_J + p["h_B"]) * WB + s * DB
            else:
                dk = arm_disc((s, th), PAD_R); r = fit(c.arm(dk), fm, p["p"]); pieces.append((dk, k))
                Bh[k] = np.array([0, -s, 0]) + (r.max() + T_SD + R_J + p["h_B"]) * adir(th)
        self.Bh = Bh
        sk = [k for k in range(3) if not self.onbar[k]]
        for side in (-1, 1):                                                   # anterior (theta < 0) / posterior side of the bar
            ks = sorted([k for k in sk if np.sign(self.st[k, 1]) == side or (self.st[k, 1] == 0 and side == 1)], key=lambda k: abs(self.st[k, 1]))
            for a_, b_ in zip(ks[:-1], ks[1:]): pieces.append((arm_strap(self.st[a_], self.st[b_], W_SD), -1))
            if ks:
                k0 = ks[0]; s0 = max(self.st[k0, 0], BAR_D0 + W_SD / 2)
                pieces.append((arm_strap(self.st[k0], (s0, side * TH_BAR * 0.8), W_SD), -1))                # to the bar's edge (merged)
        self.sdST = np.concatenate([q for q, _ in pieces]) if pieces else np.zeros((0, 2))
        self.sdR = fit(c.arm(self.sdST), fm, p["p"]) if len(self.sdST) else np.zeros(0)

    # ---- kinematics and validity -------------------------------------------------------------------------------
    def kin(self):
        p, c = self.p, self.c; n = c.n
        self.At = np.einsum("nij,kj->nki", c.RS, self.A); self.Bt = np.einsum("nij,kj->nki", c.RA, self.Bh)   # (n, 3, 3)
        V = self.Bt - self.At; self.L = np.linalg.norm(V, axis=-1); self.u = V / self.L[..., None]
        uS = np.einsum("nji,nkj->nki", c.RS, self.u); uH = np.einsum("nji,nkj->nki", c.RA, self.u)
        self.uS, self.uH = uS, uH
        J = unit(np.cross(self.Bt, self.u)); self.det = np.linalg.det(J); okdet = np.abs(self.det) >= p["det"]
        okj = np.ones(n, bool); self.axA = []; self.axB = []; self.bendA = np.zeros((n, 3)); self.bendB = np.zeros((n, 3))
        for k in range(3):
            a, oka, ba = best_axis(uS[:, k], c.w * okdet, p["beta"]); b, okb, bb = best_axis(uH[:, k], c.w * okdet, p["beta"])
            self.axA.append(a); self.axB.append(b); self.bendA[:, k] = ba; self.bendB[:, k] = bb; okj &= oka & okb
        self.okdet, self.okj = okdet, okj
        self.lo, self.hi, oks = stroke_choice(self.L, okdet & okj, c.w, self.two)
        self.oks = oks
        self.kvalid = okdet & okj & oks
        self.okc = self.collide(np.nonzero(self.kvalid)[0])
        self.okf = self.continuity()
        self.valid = self.kvalid & self.okc & self.okf

    def tube_segs(self, I):
        """per strut: list of (P0, P1, r) segments of exposed tube for poses I"""
        out = []
        for k in range(3):
            A, Bp, u, L = self.At[I, k], self.Bt[I, k], self.u[I, k], self.L[I, k]
            Lt = self.lo[k] - 2 * R_J - G_END
            if not self.two:
                e0 = A + R_J * u; e1 = A + (R_J + Lt) * u; f0 = Bp - R_J * u
                out.append([(e0, e1, R_OUT), (np.where((L > 2 * R_J + Lt)[:, None], e1, f0), f0, R_IN)])
            else:
                x = np.clip((L - Lt - 2 * R_J) / 2, 0, None)
                e0 = A + R_J * u; e1 = A + (R_J + Lt) * u; m1 = A + (R_J + x + Lt)[:, None] * u; f0 = Bp - R_J * u
                out.append([(e0, e1, R_OUT + 1), (np.where((m1 * u).sum(-1)[:, None] > (e1 * u).sum(-1)[:, None], e1, m1), m1, R_OUT),
                            (np.where(((f0 - m1) * u).sum(-1)[:, None] > 0, m1, f0), f0, R_IN)])
        return out

    def collide(self, I):
        ok = np.zeros(self.c.n, bool)
        if not len(I): return ok
        c = self.c; segs = self.tube_segs(I); good = np.ones(len(I), bool)
        At, Bt = self.At[I], self.Bt[I]
        for k in range(3):
            for j in range(k + 1, 3):
                for (p0, p1, r1) in segs[k]:
                    for (q0, q1, r2) in segs[j]:
                        good &= seg_seg(p0, p1, q0, q1) >= r1 + r2 + GAP
                good &= np.linalg.norm(At[:, k] - At[:, j], axis=-1) >= 2 * R_J + GAP
                good &= np.linalg.norm(Bt[:, k] - Bt[:, j], axis=-1) >= 2 * R_J + GAP
            for j in range(3):
                if j == k: continue
                for (p0, p1, r1) in segs[k]:
                    good &= pt_seg(At[:, j:j + 1], p0, p1)[:, 0] >= R_J + r1 + GAP
                    good &= pt_seg(Bt[:, j:j + 1], p0, p1)[:, 0] >= R_J + r1 + GAP
        # plates (underside and top) vs tubes and the other joints
        brS = self.brD * self.brR[:, None]; brT = self.brD * (self.brR + T_BR)[:, None]
        sdU = arm_pts(self.sdST, self.sdR); sdT = arm_pts(self.sdST, self.sdR + T_SD)
        PB = np.einsum("nij,mj->nmi", c.RS[I], np.concatenate([brS, brT]))
        PS = np.einsum("nij,mj->nmi", c.RA[I], np.concatenate([sdU, sdT])) if len(sdU) else np.zeros((len(I), 0, 3))
        for k in range(3):
            exA = np.linalg.norm(PB - At[:, k:k + 1], axis=-1) <= R_J + PAD_R + 3          # own bracket under its U-joint
            exB = np.linalg.norm(PS - Bt[:, k:k + 1], axis=-1) <= R_J + PAD_R + 3
            for (p0, p1, r1) in segs[k]:
                good &= np.where(exA, 1e9, pt_seg(PB, p0, p1)).min(1) >= r1 + GAP
                if PS.shape[1]: good &= np.where(exB, 1e9, pt_seg(PS, p0, p1)).min(1) >= r1 + GAP
            for j in range(3):
                if j == k: continue
                good &= np.where(exA | (np.linalg.norm(PB - At[:, j:j + 1], axis=-1) <= R_J + PAD_R + 3), 1e9,
                                 np.linalg.norm(PB - At[:, j:j + 1], axis=-1)).min(1) >= R_J + GAP
        # BOTTOM's bar (humerus frame)
        for k in range(3):
            for (p0, p1, r1) in segs[k]:
                t = np.linspace(0, 1, 40)
                P = p0[:, None] + (p1 - p0)[:, None] * t[None, :, None]
                Ph = np.einsum("nji,nmj->nmi", c.RA[I], P); dd = bar_dist(Ph)
                if self.onbar[k]: dd = np.where(np.linalg.norm(P - Bt[:, k:k + 1], axis=-1) <= R_J + 6, 1e9, dd)
                good &= dd.min(1) >= r1 + GAP
            if not self.onbar[k]:
                for P in (At[:, k], Bt[:, k]):
                    good &= bar_dist(np.einsum("nji,nj->ni", c.RA[I], P)) >= R_J + GAP
        ok[I] = good; return ok

    def joint_angles(self, RS, RA):
        """U-joint first-axis angles (deg) at both ends for rotations RS, RA (m, 3, 3) -> (m, 6)"""
        A = np.einsum("nij,kj->nki", RS, self.A); Bp = np.einsum("nij,kj->nki", RA, self.Bh); u = unit(Bp - A)
        uS = np.einsum("nji,nkj->nki", RS, u); uH = np.einsum("nji,nkj->nki", RA, u); out = []
        for k in range(3):
            for ax, U in ((self.axA[k], uS[:, k]), (self.axB[k], uH[:, k])):
                e1, e2 = perp(ax); out.append(np.degrees(np.arctan2(U @ e2, U @ e1)))
        return np.stack(out, 1)

    def continuity(self):
        c = self.c; ok = np.ones(c.n, bool)
        for j, zs in c.path.items():
            if len(zs) < 2: continue
            RS = c.fullRS[zs]; RA = np.einsum("nij,njk->nik", RS, c.fullHG[zs]); q = self.joint_angles(RS, RA)
            jump = np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max()
            ok[j] = jump <= FLIP
        return ok

    # ---- metal --------------------------------------------------------------------------------------------------
    def metal(self, i):
        """skin-facing metal samples of pose i (k, 3) and their part labels, or (None, None) if the pose is not taken"""
        if not self.valid[i]: return None, None
        c = self.c; parts = []
        parts.append(("bracket", self.brD * self.brR[:, None] @ c.RS[i].T, False))
        if len(self.sdST): parts.append(("saddle", arm_pts(self.sdST, self.sdR) @ c.RA[i].T, False))
        for k, segs in enumerate(self.tube_segs(np.array([i]))):
            for (p0, p1, r) in segs:
                P, L = tube_pts(p0, p1, r)
                if L[0] > 0.5: parts.append((f"tube{k + 1}", P[0], True))
            parts.append((f"U{k + 1}", self.At[i, k] + R_J * SPH, True)); parts.append((f"J{k + 1}", self.Bt[i, k] + R_J * SPH, True))
        return parts

    def record(self, B, i):
        parts = self.metal(i)
        if parts is None or parts == (None, None): B.record(i, None); return None
        allP = np.concatenate([P.reshape(-1, 3) for _, P, _ in parts]); d = B.dist(i, allP); o = 0; keep = []; lab = []
        for nm, P, half in parts:
            m = int(np.prod(P.shape[:-1])); dd = d[o:o + m]; o += m
            if half:                                                           # skin-facing half: per ring / per sphere
                dd = dd.reshape(P.shape[:-1]); dd = np.sort(dd, axis=-1)[..., : dd.shape[-1] // 2].reshape(-1)
            keep.append(dd); lab += [nm] * len(dd)
        B.res[i] = np.concatenate(keep)                                        # = B.record(i, skin-facing samples)
        return np.array(lab)

    def summary(self):
        c = self.c; f = lambda m: dict(clip=round(float(m[c.clip].mean()), 3), ws=round(float(m[c.ws].mean()), 3))
        return dict(det=f(self.okdet), joints=f(self.okj), stroke=f(self.oks), kin=f(self.kvalid), collide=f(self.okc | ~self.kvalid),
                    cont=f(self.okf), valid=f(self.valid), L_lo=np.round(self.lo, 1).tolist(), L_hi=np.round(self.hi, 1).tolist(),
                    A_r=np.round(np.linalg.norm(self.A, axis=1), 1).tolist(), B_r=np.round(np.hypot(self.Bh[:, 0], self.Bh[:, 2]), 1).tolist(),
                    onbar=self.onbar.tolist())


def evaluate(p, ctx, B=None, two_stage=False, per_part=False):
    B = B or ctx.B; D = Design(p, ctx, two_stage); B.reset(); labs = {}
    for i in range(ctx.n):
        lab = D.record(B, i)
        if lab is not None and per_part: labs[i] = lab
    r = B.report()
    if per_part:
        taken = [j for j in range(ctx.n) if ctx.clip[j] and B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        pp = {}
        for j in taken:
            for nm in np.unique(labs[j]):
                d = B.res[j][labs[j] == nm]; a = pp.setdefault(nm, [0, 0, 0]); a[0] += len(d); a[1] += int(((d >= 2) & (d <= 14)).sum()); a[2] += int(((d >= 2) & (d <= 10)).sum())
        r["parts"] = {k: dict(n=v[0], in14=round(v[1] / max(1, v[0]), 3), in10=round(v[2] / max(1, v[0]), 3)) for k, v in pp.items()}
    r["kin"] = D.summary(); return r, D


# ------------------------------------------------------------------------------------------------ entry points
def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "check"
    if cmd == "maps":
        B = CB.Bench(int(a[1]) if len(a) > 1 else 60, int(a[2]) if len(a) > 2 else 160); print(B.mode, B.key); build_maps(B)
    elif cmd == "check":
        B = CB.Bench(int(a[1]) if len(a) > 1 else 60, int(a[2]) if len(a) > 2 else 160); ctx = Ctx(B)
        r, D = evaluate({}, ctx, per_part=True); print(json.dumps(r, indent=1, default=str))
        print("L range per strut (all poses):", np.round(np.nanmin(D.L, 0), 1), np.round(np.nanmax(D.L, 0), 1),
              "ratio", np.round(np.nanmax(D.L, 0) / np.nanmin(D.L, 0), 2))
        for k in range(3):
            v = unit(D.uH[:, k].mean(0)); cone = np.degrees(np.arccos(np.clip(D.uH[:, k] @ v, -1, 1))).max()
            print(f"strut {k + 1}: ball-stud cone half-angle needed {cone:.0f} deg; U bend A max {D.bendA[:, k].max():.0f} B max {D.bendB[:, k].max():.0f}")
