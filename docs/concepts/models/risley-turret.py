"""risley-turret: J1 and J2 as two overlapping flat ring bearings on top of the scapula, one strap down to an O20 hub
on the lateral deltoid (3 ACTIVE DOF, 0 passive). Catalogue entry: docs/concepts/catalogue.json id "risley-turret".

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    S (handler) --J1: flat ring about b (S-fixed)--> L1 (a plate joining J1's upper race and J2's lower race)
    --J2: flat ring about p2 (A1 from b)--> L2 (J2's upper race + one strap down to W)
    --J3: O20 v5 hub about W (fixed in the humerus, A2 from p2)--> H (BOTTOM stub to the cuff).
DOF: a spherical 3R with a short first link. b is fixed in S, W in H; p2 is the two-circle intersection
(|b.p2| = cos A1, p2.W = cos A2) on the design branch -> the arm pose fixes all three angles. No passive element, no
spare: 3 active, 0 passive.

Kinematics = the band evaluator's (bvec / w_dir / circ_int / tri_ok from tools/concept_baseline.py): base axis b(az, el)
in the scapula frame, W = HG @ w_dir(delta, az), p2 = circ_int(b, A1, W, A2, branch), a pose is taken only if
sep = angle(b, W) lies in [|A2 - A1| + sing, A1 + A2 - sing] (sing = 10 deg, the baseline's margin). Scapula / humerus
rotations RS, HG per bench pose from the same pose file as the baseline.

Geometry (idealised, every part at its real size; skin-facing faces sampled on a ~2 mm grid = ~1 point / 4 mm2):
  * J1 ring: flat annulus about b, radii r_in..r_out (O30-48 at the defaults), axial [z1, z1 + ring_h] (8 mm). Lower
    race (lower half) on S, upper race (upper half) on L1 (a face-mounted, axially stacked slewing ring).
  * J2 ring: same annulus about p2, axial [z2, z2 + ring_h]; lower race on L1, upper race on L2. Where J2 lies over
    J1's footprint (+1 mm) its lower face stays >= j2_gap above J1's upper face (the overlap stack: 2 x 8 + 0.5 mm).
  * L1 plate: plate_t (3 mm) web over the convex hull of the two ring outlines (J2 projected along b onto J1's plane)
    minus the two ring footprints (the bores stay open: spec change, a lid over the bores only adds metal). Its
    underside blends from J1's upper race (top flush with J1's top) to J2's lower race (flush with J2's lower face),
    and never lower than the skin envelope + clear.
  * L2 strap: width x t_strap (14 x 3 mm Ti) on the great circle p2 -> W, from J2's outer rim (toward W) to the
    J3 hub. It starts at J2's upper race (underside z2 + ring_h / 2), lands on the hub's upper member (F3 + 3.15)
    within hub_r of W, ends ramp <= 35 deg; between, the radial profile (fixed in L2) = percentile q of the skin's
    exit radius over the valid poses + clear, and always (100th percentile) >= 1 mm over J1 and the L1 plate.
  * J3: O20 v5 hub (r 10, 12.25 mm stack) about W; its arm-side face F3 = envelope of the skin within 12 mm of W
    (percentile q) + clear. The strap rides on its upper member (F3 + 3.15).
  * BOTTOM stub (H): 14 x 6 mm (3 mm under the hub), from W 40 mm down the arm along the great circle W -> humerus axis;
    underside = hub face F3 inside the hub, then percentile-q skin envelope + clear with a <= 35 deg ramp.
Envelopes: the outermost-first skin crossing along rays from the GH centre (first exit from inside the body), fitted
like the baseline on the bench's own kinematically valid poses (held-out clips are never on the bench).
Taken: closure + singularity margin; every part >= 1 mm from every non-adjacent part (J1 / J2 rings, J3 hub as
solids; strap, stub, plate as sheets); strap vs stub (adjacent, outside the hub) >= 0.5 mm; no metal inside the body.
In-band samples: every part's skin-facing face (ring and hub lower faces, plate / strap / stub undersides; stacked
faces too, as the baseline counts a link over its hub). Contact: also ring tops and walls, hub wall and crown,
plate / strap / stub tops - one inside point is appended so the bench counts the pose as contact.
Continuity: the branch is fixed; the dense fit-clip frames (10 fps) are checked for joint jumps between consecutive
taken frames (reported; none expected inside the band).

    python3 docs/concepts/models/risley-turret.py check [n_clip n_ws]    # a few poses, numbers + reasons
    python3 docs/concepts/models/risley-turret.py sweep [n_clip n_ws]    # coarse -> refine sweep, writes sweeps/<id>.json
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                  # noqa: E402
import concept_baseline as BL                                               # noqa: E402

ID = "risley-turret"
NAME = "Risley turret: J1 and J2 as two overlapping rings on top of the scapula"
D2R = math.pi / 180
HUB_R, HUB_H, HUB_UP = 10.0, 12.25, 3.15        # O20 v5 joint
SP = 2.0                                        # sample spacing (mm) -> ~1 point / 4 mm2
R_REF = 55.0                                    # nominal radius (mm) for the angular spacing of strap / stub samples
GAP_NA, GAP_ADJ = 1.0, 0.5                      # non-adjacent / adjacent-outside-the-joint clearance (mm)
JUMP = 30.0                                     # deg between consecutive 10 fps frames = a branch flip

PARAMS = dict(b_az=32.55, b_el=80.56, w_delta=71.38, w_az=4.78, a1=40.0, a2=75.0, branch=-1, sing=10.0,
              r_in=15.0, r_out=24.0, ring_h=8.0, j2_gap=0.5, plate_t=3.0,
              width=14.0, t_strap=3.0, ramp=35.0, clear=2.0, q=100.0, hub_env_r=12.0, stub_len=40.0, stub_w=14.0, stub_t=6.0)
SWEEP = dict(a1=(30, 60), a2=(65, 95), w_delta=(60, 90), w_az=(-10, 30), b_az=(0, 60), b_el=(60, 90), branch=(-1, 1),
             r_in=(12, 20), clear=(2, 4), q=(80, 100))
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def wrap(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------- kinematics
def kin(p, HG, RS):
    """per pose (S frame): b, p2, W, humerus axis, the part frames, joint angles (deg) and validity"""
    A1, A2 = p["a1"] * D2R, p["a2"] * D2R
    n = len(HG); b = np.broadcast_to(BL.bvec(p["b_az"], p["b_el"]), (n, 3)).copy()
    W = HG @ BL.w_dir(p["w_delta"], p["w_az"]); darm = HG @ np.array([0.0, -1.0, 0.0])
    p2, ok = BL.circ_int(b, A1, W, A2, float(p["branch"]))
    ok = ok & BL.tri_ok(b, W, A1, A2, p["sing"] * D2R)
    e1 = unit(np.cross(b, [0.0, 0.0, 1.0])); e2 = np.cross(b, e1)                       # J1 / S frame (e1, e2, b)
    u = unit(p2 - (p2 * b).sum(-1, keepdims=True) * b); v = np.cross(b, u)              # L1 frame (u, v, b)
    wp = unit(W - (W * p2).sum(-1, keepdims=True) * p2); n2 = np.cross(p2, wp)          # L2 frame (p2, wp, n2)
    dp = unit(darm - (darm * W).sum(-1, keepdims=True) * W); n3 = np.cross(W, dp)       # H frame (W, dp, n3)
    th1 = np.arctan2((u * e2).sum(-1), (u * e1).sum(-1)) / D2R
    r2 = unit(b - (b * p2).sum(-1, keepdims=True) * p2)
    th2 = np.arctan2((np.cross(p2, r2) * wp).sum(-1), (r2 * wp).sum(-1)) / D2R
    r3 = unit(p2 - (p2 * W).sum(-1, keepdims=True) * W)
    th3 = np.arctan2((np.cross(W, r3) * dp).sum(-1), (r3 * dp).sum(-1)) / D2R
    sep = np.arccos(np.clip((b * W).sum(-1), -1, 1)) / D2R
    p2arm = np.arccos(np.clip((p2 * darm).sum(-1), -1, 1)) / D2R
    return dict(b=b, p2=p2, W=W, darm=darm, ok=ok, e1=e1, e2=e2, u=u, v=v, wp=wp, n2=n2, dp=dp, n3=n3,
                th=np.stack([th1, th2, th3], 1), sep=sep, p2arm=p2arm)


# ---------------------------------------------------------------- local sample sets (part frames)
def annulus(r0, r1, sp=SP):
    """(k, 2) in-plane points of an annulus on a ~sp mm grid (concentric circles)"""
    out = []
    for r in np.arange(r0 + sp / 2, r1, sp):
        m = max(6, int(round(2 * math.pi * r / sp))); t = np.arange(m) * 2 * math.pi / m
        out.append(np.c_[r * np.cos(t), r * np.sin(t)])
    return np.concatenate(out)


def circle(r, sp=SP):
    m = max(6, int(round(2 * math.pi * r / sp))); t = np.arange(m) * 2 * math.pi / m
    return np.c_[r * np.cos(t), r * np.sin(t)]


def disc(r, sp=SP):
    g = np.arange(-r, r + 1e-6, sp); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= r * r
    return np.c_[X[k], Y[k]]


def strap_local(ang, width, sp=SP, r_ref=R_REF, ang0=0.0):
    """(s_mm, c_mm) stations of a strap on a great circle from arc angle ang0 to ang (rad), width across"""
    L0, L1 = ang0 * r_ref, ang * r_ref; ns = max(2, int(math.ceil((L1 - L0) / sp)) + 1)
    s = np.linspace(L0, L1, ns); c = np.arange(-width / 2 + sp / 2, width / 2, sp) if width > sp else np.zeros(1)
    S, C = np.meshgrid(s, c, indexing="ij"); return S.reshape(-1), C.reshape(-1), ns, len(c)


def gc_dirs(e_from, e_to_perp, nrm, s_mm, c_mm, r_ref=R_REF):
    """unit directions (n, 3) at arc length s_mm (from e_from toward e_to_perp) and across offset c_mm (along nrm)"""
    th = s_mm / r_ref; cs = c_mm / r_ref
    D = np.cos(th)[:, None] * e_from + np.sin(th)[:, None] * e_to_perp
    return unit(D * np.cos(cs)[:, None] + nrm * np.sin(cs)[:, None])


# ---------------------------------------------------------------- skin tracing
_KD = {}


def _kd_exit(B, i, Dt, r0=8.0, rmax=250.0, it=80):
    """dev path (no distance cache): unsigned distance to dense skin samples (vertices + face centroids, KD-tree),
    marching outward from the GH centre; ~1 mm accurate. Only shapes the envelope fit; the bench scores exactly."""
    from scipy.spatial import cKDTree
    key = (B.key, i)
    if key not in _KD:
        if len(_KD) > 64: _KD.clear()
        V, F = B.skin(i); V = np.asarray(V, float); C = V[F].mean(1); X = np.r_[V, C]; X = X[np.linalg.norm(X, axis=1) < 320]
        _KD[key] = cKDTree(X)
    T = _KD[key]; k = len(Dt); r = np.full(k, r0); act = np.ones(k, bool); out = np.zeros(k)
    for _ in range(it):
        a = np.nonzero(act)[0]
        if not len(a): break
        d, _j = T.query(Dt[a] * r[a, None]); hit = d < 1.2
        out[a[hit]] = r[a[hit]]; act[a[hit]] = False
        r[a[~hit]] += np.maximum(d[~hit] - 1.0, 0.3); act &= ~(r > rmax)
    return out


_MT = {}; _VS = {}


def _skin_v(B, i):
    if getattr(B, "_V", None) is not None: return np.asarray(B._V[i], np.float32)
    key = (B.key, i)                                       # dev path (no bench cache): keep the posed skins of this bench
    if key not in _VS: _VS[key] = np.asarray(B.skin(i)[0], np.float32)
    return _VS[key]


def _mt_exit(B, i, Dt, rmax=300.0):
    """exact first exit of the posed skin along rays from the GH centre (inside the body): vectorised Moller-Trumbore
    on the skin triangles within rmax, candidates pruned by angle (KD-tree on triangle centroid directions; the few
    triangles wider than 0.12 rad seen from GH are tested against every ray). 0 = no exit."""
    from scipy.spatial import cKDTree
    import concept_bench as _cb
    key = (B.key, i)
    if key not in _MT:
        if len(_MT) > 3: _MT.clear()
        V = _skin_v(B, i).astype(float); F = np.asarray(_cb.BP.F)
        T = V[F]; keep = (np.linalg.norm(T, axis=2) < rmax).any(1); T = T[keep]
        Tu = unit(T); c = unit(Tu.mean(1)); ar = np.arccos(np.clip((Tu * c[:, None]).sum(-1), -1, 1)).max(1)
        big = ar > 0.12
        _MT[key] = (T[~big], c[~big], ar[~big], cKDTree(c[~big]), T[big])
    T, c, ar, tree, Tb = _MT[key]
    lists = tree.query_ball_point(Dt, 2 * math.sin(0.12 / 2) + 1e-6)
    ri = np.repeat(np.arange(len(Dt)), [len(l) for l in lists]); ti = np.fromiter((t for l in lists for t in l), int, len(ri))
    tt = np.full(len(Dt), np.inf)
    if len(ri):
        ok = (Dt[ri] * c[ti]).sum(-1) >= np.cos(ar[ti]) - 1e-9; ri, ti = ri[ok], ti[ok]
        _mt(Dt[ri], T[ti], ri, tt)
    if len(Tb):
        ri = np.repeat(np.arange(len(Dt)), len(Tb)); _mt(Dt[ri], np.tile(Tb, (len(Dt), 1, 1)), ri, tt)
    return np.where(np.isfinite(tt), tt, 0.0)


def _mt(d, T, ri, tt):
    v0 = T[:, 0]; e1 = T[:, 1] - v0; e2 = T[:, 2] - v0
    pv = np.cross(d, e2); det = (e1 * pv).sum(-1); inv = 1.0 / np.where(np.abs(det) < 1e-12, 1e-12, det)
    tv = -v0; u = (tv * pv).sum(-1) * inv; qv = np.cross(tv, e1); v = (d * qv).sum(-1) * inv; t = (e2 * qv).sum(-1) * inv
    hit = (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 1e-6)
    np.minimum.at(tt, ri[hit], t[hit])


def exit_radius(B, i, Dt, r0=8.0, rmax=250.0, it=60):
    return _mt_exit(B, i, Dt)
    """first exit of the posed skin along rays from the GH centre (unit directions Dt (k, 3), thorax frame): radius,
    0 where the ray never exits within rmax. Marches from inside with steps |d| (never past the first crossing)."""
    k = len(Dt); r = np.full(k, r0); act = np.ones(k, bool); out = np.zeros(k)
    for _ in range(it):
        a = np.nonzero(act)[0]
        if not len(a): break
        d = B.dist(i, Dt[a] * r[a, None])
        ex = d >= 0
        out[a[ex]] = np.maximum(r[a[ex]] - d[ex], 0.0); act[a[ex]] = False
        nx = a[~ex]; r[nx] += np.maximum(-d[~ex], 0.25)
        far = r > rmax; act &= ~far
    return out


# ---------------------------------------------------------------- the design
class Model:
    """fits the concept to the bench poses and produces metal samples per pose"""
    def __init__(self, B, p, log=lambda *a: None):
        self.B = B; self.p = p = dict(PARAMS, **p); self.log = log
        Z = CB._poses_all(); self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.K = kin(p, self.HG, self.RS); self.valid = np.nonzero(self.K["ok"])[0]
        A1, A2 = p["a1"] * D2R, p["a2"] * D2R; self.A1, self.A2 = A1, A2
        self.sA, self.cA = math.sin(A1), math.cos(A1)
        # local sample sets
        self.ring2d = annulus(p["r_in"], p["r_out"]); self.hub2d = disc(HUB_R); self.hubenv2d = disc(p["hub_env_r"])
        s, c, ns, nc = strap_local(A2, p["width"]); self.st_s, self.st_c, self.st_ns, self.st_nc = s, c, ns, nc
        L = p["stub_len"]; s, c, ns, nc = strap_local(L / R_REF, p["stub_w"]); self.sb_s, self.sb_c = s, c

    # ---- per-pose geometry in S --------------------------------------------------------------------------------
    def j1_pts(self, i, z, pl=None):
        K = self.K; pl = self.ring2d if pl is None else pl
        return z * K["b"][i] + pl[:, :1] * K["e1"][i] + pl[:, 1:] * K["e2"][i]

    def j2_local(self, z, pl=None):
        """J2 points in L1 coordinates (u, v, b): centre z*p2, plane basis u2 = (-cosA1, 0, sinA1), v2 = (0, -1, 0)"""
        pl = self.ring2d if pl is None else pl; sA, cA = self.sA, self.cA
        return np.c_[z * sA - pl[:, 0] * cA, -pl[:, 1], z * cA + pl[:, 0] * sA]

    def l1_to_s(self, i, X):
        K = self.K; return X[:, :1] * K["u"][i] + X[:, 1:2] * K["v"][i] + X[:, 2:] * K["b"][i]

    def hub_pts(self, i, z, pl):
        K = self.K; return z * K["W"][i] + pl[:, :1] * K["dp"][i] + pl[:, 1:] * K["n3"][i]

    def strap_dirs(self, i):
        K = self.K; return gc_dirs(K["p2"][i], K["wp"][i], K["n2"][i], self.st_s, self.st_c)

    def stub_dirs(self, i):
        K = self.K; return gc_dirs(K["W"][i], K["dp"][i], K["n3"][i], self.sb_s, self.sb_c)

    def plate_local(self, z1, z2):
        """L1 plate web samples (u, v) on a 2 mm grid and their blend underside height along b"""
        p = self.p; ro = p["r_out"]; sA, cA = self.sA, self.cA
        uc, ae, be = z2 * sA, ro * cA, ro                          # J2 outline projected along b: ellipse
        t = np.linspace(0, 2 * math.pi, 180, endpoint=False)
        pts = np.r_[np.c_[ro * np.cos(t), ro * np.sin(t)], np.c_[uc + ae * np.cos(t), be * np.sin(t)]]
        from scipy.spatial import Delaunay, ConvexHull
        hull = Delaunay(pts[ConvexHull(pts).vertices])
        g = np.arange(-ro - SP, uc + ae + SP, SP); h = np.arange(-ro - SP, ro + SP, SP); U, V = np.meshgrid(g, h)
        Q = np.c_[U.ravel(), V.ravel()]
        rho1 = np.hypot(Q[:, 0], Q[:, 1]); s2 = np.hypot((Q[:, 0] - uc) / ae, Q[:, 1] / be)
        k = (hull.find_simplex(Q) >= 0) & (rho1 > ro + 0.5) & (s2 > 1 + 0.5 / ae)
        Q = Q[k]; d1 = np.hypot(Q[:, 0], Q[:, 1]) - ro; d2 = (np.hypot((Q[:, 0] - uc) / ae, Q[:, 1] / be) - 1) * min(ae, be)
        w = d1 / np.maximum(d1 + d2, 1e-6)
        h1 = z1 + p["ring_h"] - p["plate_t"]; h2 = (z2 - Q[:, 0] * sA) / cA          # J2's lower plane along b
        return Q, (1 - w) * h1 + w * h2

    # ---- fit ---------------------------------------------------------------------------------------------------
    def trace_all(self, groups):
        """groups: {name: fn(i) -> (k, 3) S-frame points whose RAYS are traced}; -> {name: (P, k) exit radius}"""
        B = self.B; out = {}
        for nm in groups: out[nm] = None
        for i in self.valid:
            seg = []; D = []
            for nm, fn in groups.items():
                X = fn(int(i)); D.append(unit(X)); seg.append(len(X))
            D = np.concatenate(D) @ self.RS[i].T
            r = exit_radius(B, int(i), D); o = 0
            for nm, k in zip(groups, seg):
                if out[nm] is None: out[nm] = np.full((len(self.HG), k), np.nan)
                out[nm][i] = r[o:o + k]; o += k
        return out

    @staticmethod
    def axial(X, rho, axis):
        """skin height along axis under face points X (P, k, 3) from the exit radius along their rays"""
        return rho * (unit(X) * axis[:, None, :]).sum(-1)

    def fit(self, qs=(100.0,)):
        p = self.p; K = self.K; V = self.valid; t0 = time.time()
        if len(V) < 3: self.fits = None; return
        z1, z2, F3 = 52.0, 52.0, 52.0
        for ps in range(2):                                                        # pass 0 nominal heights, pass 1 fitted
            Q, hpl = self.plate_local(z1, z2)
            g = dict(j1=lambda i: self.j1_pts(i, z1), j2=lambda i: self.l1_to_s(i, self.j2_local(z2)),
                     pl=lambda i: self.l1_to_s(i, np.c_[Q, hpl]), hub=lambda i: self.hub_pts(i, F3, self.hubenv2d))
            if ps == 1: g.update(st=self.strap_dirs, sb=self.stub_dirs)
            R = self.trace_all(g)
            X1 = np.stack([self.j1_pts(i, z1) for i in V]); X2 = np.stack([self.l1_to_s(i, self.j2_local(z2)) for i in V])
            Xp = np.stack([self.l1_to_s(i, np.c_[Q, hpl]) for i in V]); Xh = np.stack([self.hub_pts(i, F3, self.hubenv2d) for i in V])
            H1 = self.axial(X1, R["j1"][V], K["b"][V]); H2 = self.axial(X2, R["j2"][V], K["p2"][V])
            Hp = self.axial(Xp, R["pl"][V], K["b"][V]); Hh = self.axial(Xh, R["hub"][V], K["W"][V])
            q0 = max(qs)
            z1 = float(np.percentile(H1, q0, axis=0).max()) + p["clear"]
            z2 = self._z2(float(np.percentile(H2, q0, axis=0).max()) + p["clear"], z1)
            F3 = float(np.percentile(Hh, q0, axis=0).max()) + p["clear"]
        self.Q = Q; self.raw = dict(H1=H1, H2=H2, Hp=Hp, Hh=Hh, ST=R["st"][V], SB=R["sb"][V])
        self.fits = {q: self._fit_q(q) for q in qs}
        self.log(f"  fit {len(V)} valid poses, {time.time() - t0:.0f} s")

    def _z2(self, z2_env, z1):
        p = self.p; z2 = z2_env; pl = self.ring2d; sA, cA = self.sA, self.cA
        for _ in range(8):
            X = self.j2_local(z2); rho = np.hypot(X[:, 0], X[:, 1])
            over = (rho >= p["r_in"] - 1) & (rho <= p["r_out"] + 1)
            if not over.any(): break
            need = float(((z1 + p["ring_h"] + p["j2_gap"] - pl[over, 0] * sA) / cA).max())
            if need <= z2 + 1e-3: break
            z2 = need
        return z2

    def _fit_q(self, q):
        """heights / profiles at percentile q (0-100) of the valid poses"""
        p = self.p; R = self.raw; V = self.valid; K = self.K; c = p["clear"]; tr = math.tan(p["ramp"] * D2R)
        f = dict(q=q)
        f["z1"] = z1 = float(np.percentile(R["H1"], q, axis=0).max()) + c
        f["z2"] = z2 = self._z2(float(np.percentile(R["H2"], q, axis=0).max()) + c, z1)
        Q, hpl = self.plate_local(z1, z2)
        Hp = R["Hp"]
        if Hp.shape[1] != len(Q):                                                   # plate grid moved with z2: nearest refit
            from scipy.spatial import cKDTree
            _, j = cKDTree(self.Q).query(Q); Hp = Hp[:, j]
        f["plate_Q"] = Q; f["plate_h"] = np.maximum(hpl, np.percentile(Hp, q, axis=0) + c)
        F3 = float(np.percentile(R["Hh"], q, axis=0).max()) + c
        # strap: radial profile in L2, from J2's rim (upper race, underside z2 + ring_h/2) to the hub's upper member
        s, cc, ns, nc = self.st_s, self.st_c, self.st_ns, self.st_nc
        th = s / R_REF; start_lvl = z2 + p["ring_h"] / 2
        th0 = math.atan2(p["r_out"], start_lvl)                                     # rim angle from p2
        env = np.percentile(R["ST"], q, axis=0) + c
        obs = self._strap_obstacles(z1, z2, Q, f["plate_h"])                        # (k,) max over valid poses
        prof = np.maximum(env, obs)
        thW = self.A2 - th                                                          # angle from W
        hubz = np.abs(thW) * R_REF <= HUB_R
        # the hub face must sit low enough for the strap (bolted at F3 + 3.15) to clear skin and obstacles over it
        F3 = max(F3, float((prof[hubz] * np.cos(thW[hubz])).max()) - HUB_UP) if hubz.any() else F3
        f["F3"] = F3
        r_start = start_lvl / np.cos(np.clip(th0, 0, 1.5)); ss = (th - th0) * R_REF
        r_hub = (F3 + HUB_UP) / np.cos(thW)
        dist_hub = np.maximum(np.abs(thW) * R_REF - HUB_R, 0)
        prof = np.maximum(prof, np.maximum(r_start - tr * np.maximum(ss, 0), 0))
        prof = np.where(hubz, r_hub, np.maximum(prof, (F3 + HUB_UP) / math.cos(HUB_R / R_REF) - tr * dist_hub))
        keep = th >= th0
        f["st_keep"] = keep; f["st_prof"] = prof
        # stub: hub face F3 inside the hub, then envelope with a ramp
        th_b = self.sb_s / R_REF; inside = self.sb_s <= HUB_R
        envb = np.percentile(R["SB"], q, axis=0) + c
        r_hb = F3 / np.cos(th_b)
        pb = np.maximum(envb, F3 / math.cos(HUB_R / R_REF) - tr * np.maximum(self.sb_s - HUB_R, 0))
        f["sb_prof"] = np.where(inside, r_hb, pb); f["sb_keep"] = ~inside
        f["sb_t"] = np.where(inside, 3.0, p["stub_t"])
        return f

    def _strap_obstacles(self, z1, z2, Q, hpl):
        """per strap sample: the largest radius (over the valid poses) of J1 or the L1 plate top under it, + 1 mm"""
        p = self.p; K = self.K; from scipy.spatial import cKDTree
        top = np.c_[Q, hpl + p["plate_t"]]; tdir = unit(top); rt = np.linalg.norm(top, axis=1)
        tree = cKDTree(tdir * R_REF) if len(top) else None
        out = np.zeros(len(self.st_s))
        for i in self.valid:
            D = self.strap_dirs(int(i)); b = K["b"][i]
            cb = D @ b; sb = np.sqrt(np.clip(1 - cb * cb, 0, 1))
            with np.errstate(divide="ignore", invalid="ignore"):
                lo = np.maximum(p["r_in"] / sb, z1 / cb); hi = np.minimum(p["r_out"] / sb, (z1 + p["ring_h"]) / cb)
                hit = (cb > 0.05) & (sb > 1e-3) & (lo <= hi + 1.5)
                ex = np.where(hit, hi, 0.0)
            out = np.maximum(out, np.where(hit, ex + GAP_NA, 0.0))
            if tree is not None:                                                    # plate top (L1 frame) under the strap
                DL = np.c_[D @ K["u"][i], D @ K["v"][i], D @ K["b"][i]]
                dd, j = tree.query(DL * R_REF, distance_upper_bound=SP * 1.2)
                m = np.isfinite(dd)
                out[m] = np.maximum(out[m], rt[j[m]] + GAP_ADJ)
        return out

    # ---- metal per pose ----------------------------------------------------------------------------------------
    def metal(self, i, f):
        """(face points (k,3) in S, extra contact-only points (m,3) in S, solids / sheets for the interference check)"""
        p = self.p; K = self.K; rh = p["ring_h"]; ri, ro = p["r_in"], p["r_out"]
        z1, z2, F3 = f["z1"], f["z2"], f["F3"]
        J1 = self.j1_pts(i, z1); J2 = self.l1_to_s(i, self.j2_local(z2))
        PL = self.l1_to_s(i, np.c_[f["plate_Q"], f["plate_h"]]); PLt = PL + p["plate_t"] * K["b"][i]
        HB = self.hub_pts(i, F3, self.hub2d)
        Ds = self.strap_dirs(i); ks = f["st_keep"]; ST = Ds[ks] * f["st_prof"][ks, None]; STt = Ds[ks] * (f["st_prof"][ks, None] + p["t_strap"])
        Db = self.stub_dirs(i); kb = f["sb_keep"]; SB = Db[kb] * f["sb_prof"][kb, None]; SBt = Db[kb] * (f["sb_prof"][kb] + f["sb_t"][kb])[:, None]
        faces = dict(j1=J1, j2=J2, plate=PL, hub=HB, strap=ST, stub=SB)
        # contact-only surfaces: ring tops / walls, hub crown / wall, sheet tops
        hz = np.arange(SP / 2, rh, SP)
        w1 = np.concatenate([np.concatenate([self.j1_pts(i, z1 + h, circle(ri)), self.j1_pts(i, z1 + h, circle(ro))]) for h in hz])
        w2 = np.concatenate([self.l1_to_s(i, np.r_[self.j2_local(z2 + h, circle(ri)), self.j2_local(z2 + h, circle(ro))]) for h in hz])
        hw = np.concatenate([self.hub_pts(i, F3 + h, circle(HUB_R)) for h in np.arange(SP / 2, HUB_H, SP)])
        extra = np.concatenate([self.j1_pts(i, z1 + rh), self.l1_to_s(i, self.j2_local(z2 + rh)), w1, w2,
                                self.hub_pts(i, F3 + HUB_H, self.hub2d), hw, PLt, STt, SBt])
        sheets = dict(strap=(Ds[ks], f["st_prof"][ks], np.full(ks.sum(), p["t_strap"])), stub=(Db[kb], f["sb_prof"][kb], f["sb_t"][kb]),
                      plate=(unit(PL), np.linalg.norm(PL, axis=1), np.full(len(PL), p["plate_t"])))
        surf = dict(j1=np.r_[J1, w1, self.j1_pts(i, z1 + rh)], j2=np.r_[J2, w2, self.l1_to_s(i, self.j2_local(z2 + rh))],
                    hub=np.r_[HB, hw, self.hub_pts(i, F3 + HUB_H, self.hub2d)])
        return faces, extra, sheets, surf

    def ring_sdf(self, X, axis, z):
        p = self.p; a = X @ axis; rho = np.linalg.norm(X - a[:, None] * axis, axis=1)
        dr = np.maximum(p["r_in"] - rho, rho - p["r_out"]); dz = np.maximum(z - a, a - (z + p["ring_h"]))
        return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))

    def hub_sdf(self, X, axis, z):
        a = X @ axis; rho = np.linalg.norm(X - a[:, None] * axis, axis=1)
        dr = rho - HUB_R; dz = np.maximum(z - a, a - (z + HUB_H))
        return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))

    @staticmethod
    def sheet_clear(A, Bs, excl=None):
        """min radial clearance between two radial-profile sheets where their footprints overlap (inf if they don't)"""
        from scipy.spatial import cKDTree
        (da, ra, ta), (db, rb, tb) = A, Bs
        if not len(da) or not len(db): return np.inf
        t = cKDTree(db * R_REF); dd, j = t.query(da * R_REF, distance_upper_bound=SP * 0.9)
        m = np.isfinite(dd)
        if excl is not None: m &= ~excl
        if not m.any(): return np.inf
        j = j[m]; a0, a1 = ra[m], ra[m] + ta[m]; b0, b1 = rb[j], rb[j] + tb[j]
        return float(np.maximum(b0 - a1, a0 - b1).min())

    def interference(self, i, f, faces, sheets, surf):
        """min clearance of non-adjacent pairs (and strap vs stub outside the hub); returns (ok, worst pair, value)"""
        p = self.p; K = self.K; z1, z2, F3 = f["z1"], f["z2"], f["F3"]
        b, p2, W = K["b"][i], K["p2"][i], K["W"][i]
        sheet_pts = lambda nm: np.r_[sheets[nm][0] * sheets[nm][1][:, None], sheets[nm][0] * (sheets[nm][1] + sheets[nm][2])[:, None]]
        chk = [("j1-strap", self.ring_sdf(sheet_pts("strap"), b, z1), GAP_NA),
               ("j1-stub", self.ring_sdf(sheet_pts("stub"), b, z1), GAP_NA),
               ("j1-hub", np.r_[self.ring_sdf(surf["hub"], b, z1), self.hub_sdf(surf["j1"], W, F3)], GAP_NA),
               ("j2-stub", self.ring_sdf(sheet_pts("stub"), p2, z2), GAP_NA),
               ("j2-hub", np.r_[self.ring_sdf(surf["hub"], p2, z2), self.hub_sdf(surf["j2"], W, F3)], GAP_NA),
               ("plate-hub", self.hub_sdf(sheet_pts("plate"), W, F3), GAP_NA)]
        worst = ("", np.inf)
        for nm, d, g in chk:
            m = float(d.min()) if len(d) else np.inf
            if m < g: return False, nm, m
            if m < worst[1]: worst = (nm, m)
        m = self.sheet_clear(sheets["plate"], sheets["stub"])
        if m < GAP_NA: return False, "plate-stub", m
        thW = (self.A2 - self.st_s / R_REF)[f["st_keep"]]
        m = self.sheet_clear(sheets["strap"], sheets["stub"], excl=np.abs(thW) * R_REF <= HUB_R + SP)
        if m < GAP_ADJ: return False, "strap-stub", m
        return True, worst[0], worst[1]

    def evaluate(self, q, why=None):
        """record every pose on the bench for the fit at percentile q -> bench report"""
        B = self.B; B.reset(); f = self.fits[q]; reasons = {}
        for i in range(len(B.poses)):
            if not self.K["ok"][i]:
                B.record(i, None); reasons[i] = "closure"; continue
            faces, extra, sheets, surf = self.metal(i, f)
            ok, nm, m = self.interference(i, f, faces, sheets, surf)
            if not ok:
                B.record(i, None); reasons[i] = f"interference {nm} {m:.1f}"; continue
            R = self.RS[i]; P = np.concatenate(list(faces.values())) @ R.T
            E = extra @ R.T; de = B.dist(i, E)
            if de.min() < 0: P = np.r_[P, E[np.argmin(de)][None]]
            d = B.record(i, P); reasons[i] = "contact" if d.min() < 0 else "taken"
        if why is not None: why.update(reasons)
        return B.report()


# ---------------------------------------------------------------- continuity on the dense clips
def continuity(p):
    Z = CB._poses_all(); names = list(Z["NAMES"]); fit_ids = [names.index(n) for n in CB.FIT]
    out = {}
    for c in fit_ids:
        idx = np.nonzero(Z["CID"] == c)[0]; idx = idx[np.argsort(Z["FI"][idx])]
        K = kin(dict(PARAMS, **p), Z["HG"][idx].astype(float), Z["RS"][idx].astype(float))
        ok = K["ok"]; th = K["th"]; both = ok[1:] & ok[:-1]
        jump = np.abs(wrap(np.diff(th, axis=0))).max(1)
        exc = int(((~ok[1:]) & ok[:-1]).sum())
        out[names[c]] = dict(frames=int(len(idx)), valid=round(float(ok.mean()), 3), max_jump=round(float(jump[both].max()), 1) if both.any() else None,
                             flips=int((jump[both] > JUMP).sum()), band_exits=exc)
    return out


# ---------------------------------------------------------------- driver
def run(B, p, qs=(100.0, 95.0, 90.0, 80.0), log=print, why=False):
    M = Model(B, p, log); M.fit(qs)
    if M.fits is None:
        r = B.report() if False else dict(reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0); r["gap"] = 300.0
        return dict(r, q=None), M, {}
    best = None; rs = []
    for q in qs:
        w = {} if why else None
        r = M.evaluate(q, w); r["q"] = q; r["z1"] = round(M.fits[q]["z1"], 1); r["z2"] = round(M.fits[q]["z2"], 1); r["F3"] = round(M.fits[q]["F3"], 1)
        rs.append((r, w))
        if best is None or r["gap"] < best[0]["gap"]: best = (r, w)
    return best[0], M, best[1]


def bench(n_clip=60, n_ws=160):
    return CB.Bench(n_clip=n_clip, n_ws=n_ws)


def pick_poses(B):
    """rest, overhead, across the body, behind the back (bench indices)"""
    P = B.poses; idx = range(len(P))
    rest = min(idx, key=lambda j: P[j]["elev"])
    over = max(idx, key=lambda j: P[j]["elev"])
    across = max(idx, key=lambda j: P[j]["plane"] + (0 if P[j]["elev"] > 60 else -999))
    back = [j for j in idx if B.clip[j] == "Reach back pocket"]
    back = min(back, key=lambda j: P[j]["axial"]) if back else min(idx, key=lambda j: P[j]["plane"])
    return dict(rest=rest, overhead=over, across=across, behind_back=back)


def check(n_clip=20, n_ws=40, p=None):
    B = bench(n_clip, n_ws); p = dict(PARAMS, **(p or {}))
    t = time.time(); best, M, why = run(B, p, qs=(100.0, 90.0), why=True)
    print("mode", B.mode, "time", round(time.time() - t), "s")
    print("BEST", json.dumps({k: v for k, v in best.items() if k != "poses"}))
    f = M.fits[best["q"]]
    print("heights z1 %.1f z2 %.1f F3 %.1f; plate samples %d; strap kept %d; stub %d" % (f["z1"], f["z2"], f["F3"], len(f["plate_Q"]), f["st_keep"].sum(), f["sb_keep"].sum()))
    from collections import Counter
    print("reasons", Counter(v.split(" ")[0] if not v.startswith("interference") else " ".join(v.split(" ")[:2]) for v in why.values()))
    K = M.K
    for nm, j in pick_poses(B).items():
        r = B.res[j]
        s = f"{nm:12s} pose {B.poses[j]} sep {K['sep'][j]:.0f} p2-arm {K['p2arm'][j]:.0f} -> {why.get(j)}"
        if r is not None:
            faces, extra, sheets, surf = M.metal(j, f); o = 0; parts = []
            for k, v in faces.items():
                d = r[o:o + len(v)]; o += len(v)
                parts.append(f"{k} {np.mean((d >= 2) & (d <= 14)):.2f}/{d.min():.1f}/{np.median(d):.1f}")
            s += "\n      in14/min/median: " + "; ".join(parts)
        print(s)
    print("continuity", json.dumps(continuity(p)))
    return M, best


def gap_row(r):
    return CB.gap_of(r["inband14"], r["follow"], r["reach"], r["contact"])


# ---------------------------------------------------------------- sweep
def kin_cover(p, HG, kind):
    K = kin(dict(PARAMS, **p), HG, np.zeros_like(HG)); ok = K["ok"]
    return float(ok[kind == "clip"].mean()), float(ok[kind == "ws"].mean())


def kin_best(B, a1, a2, n=1200, seed=0, top=3):
    """axes (b, W0) that maximise closure coverage of the bench poses for given link angles (kinematics only)"""
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); kind = np.array(B.kind); rng = np.random.default_rng(seed); res = []
    for _ in range(n):
        x = dict(b_az=rng.uniform(0, 60), b_el=rng.uniform(60, 90), w_delta=rng.uniform(55, 95), w_az=rng.uniform(-20, 40), a1=a1, a2=a2)
        c, w = kin_cover(x, HG, kind); res.append((-(max(0, .95 - c) + max(0, .9 - w)) + 0.05 * (c + w), x))
    res.sort(key=lambda t: -t[0]); return [r[1] for r in res[:top]]


def log_entry(out, k, params, r):
    rows = json.load(open(out)) if os.path.exists(out) else []
    rows.append(dict(k=k, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=params, inband14=r["inband14"], inband10=r["inband10"],
                     reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"]))
    json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
    return len(rows)


def eval_config(B, p, out, qs=(100.0, 95.0, 90.0, 80.0), log=lambda s: print(s, flush=True)):
    """fit + evaluate one geometric configuration at every percentile q; each q is one logged configuration"""
    p = dict(PARAMS, **p); M = Model(B, p); t = time.time(); M.fit(qs); res = []
    for q in qs:
        if M.fits is None: r = dict(reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, gap=300.0)
        else: r = M.evaluate(q)
        pp = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in dict(p, q=q).items()}
        k = log_entry(out, None, pp, r) if out else 0
        res.append((r["gap"], pp, r)); log(f"  [{k}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} in14 {r['inband14']:.3f} in10 {r['inband10']:.3f} contact {r['contact']:.3f} | {json.dumps({kk: pp[kk] for kk in ('a1', 'a2', 'b_az', 'b_el', 'w_delta', 'w_az', 'r_in', 'clear', 'branch', 'q')})} {time.time() - t:.0f}s")
    return res


def _renumber(out):
    rows = json.load(open(out))
    for j, r in enumerate(rows): r["k"] = j
    json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)


def sketch(M, q, path):
    """matplotlib sketch: rest and overhead, a slab of the skin around the b-W plane + every metal sample (part colours)"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    B = M.B; f = M.fits[q]; poses = pick_poses(B); K = M.K
    fig, axs = plt.subplots(1, 4, figsize=(16, 4.6))
    col = dict(j1="#1f77b4", j2="#ff7f0e", plate="#2ca02c", hub="#d62728", strap="#9467bd", stub="#8c564b")
    for ax, (nm, j) in zip(axs, poses.items()):
        if not K["ok"][j]:
            ax.set_title(f"{nm}: not taken (closure)"); ax.axis("off"); continue
        faces, extra, sheets, surf = M.metal(j, f); R = M.RS[j]
        b = K["b"][j] @ R.T; W = K["W"][j] @ R.T; nrm = unit(np.cross(b, W)); e1 = b; e2 = unit(np.cross(nrm, e1))
        V, _ = B.skin(j); V = np.asarray(V); sl = (np.abs(V @ nrm) < 3) & (np.linalg.norm(V, axis=1) < 160)
        ax.scatter(V[sl] @ e2, V[sl] @ e1, s=1, c="0.6")
        for k, P in faces.items():
            P = P @ R.T; m = np.abs(P @ nrm) < 8
            ax.scatter(P[m] @ e2, P[m] @ e1, s=3, c=col[k], label=k)
        ax.scatter([0], [0], marker="+", c="k"); ax.set_aspect("equal"); ax.set_xlim(-120, 120); ax.set_ylim(-80, 120)
        ax.set_title(f"{nm} (plane {B.poses[j]['plane']:.0f}, elev {B.poses[j]['elev']:.0f})", fontsize=9)
    axs[0].legend(fontsize=7, loc="lower left"); fig.suptitle(f"{ID}: section through b and W (8 mm slab), GH = +", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "check"
    nc = int(a[1]) if len(a) > 1 else (20 if cmd == "check" else 60); nw = int(a[2]) if len(a) > 2 else (40 if cmd == "check" else 160)
    if cmd == "check":
        check(nc, nw)
    elif cmd == "one":                                                           # one configuration from a JSON dict
        B = bench(nc, nw); print(B.mode); eval_config(B, json.loads(a[3]) if len(a) > 3 else {}, None)
