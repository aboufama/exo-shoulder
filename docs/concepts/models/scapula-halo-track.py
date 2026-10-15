"""scapula-halo-track: J1 is a closed cam track on low-motion scapula skin, the J2 hub rides it on a bogie carriage
(3 ACTIVE DOF: s on the track, q2, q3; 0 passive on the bench).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    track T (fixed to the scapula handler): a closed halo drawn along an iso-motion contour of the scapula-frame skin
       (pipeline/conformal/analysis/skin_motion_map_14.json, threshold thr mm) around the acromion summit, + el offset
       + a 3-harmonic Fourier perturbation; a Ti ring, 8 wide x 5 radial
    -> J1 (ACTIVE): bogie carriage on T, 20 along x 16 across, radial [Rt, Rt + 9]; its position s along T is the joint
    -> J2 (ACTIVE): O20 hub on the carriage, axis p2 = u(s) (radial through GH); the carriage is the lower member
    -> link 2: strap 12 wide x 3 thick on the great circle p2 -> w, arc a2
    -> J3 (ACTIVE): O20 hub, axis w = HG W(delta, az) fixed in the humerus
    -> arm-end plate + neck (14 x 6 strap) to BOTTOM's bar (the user's part; not modelled as metal).
DOF: given the arm, w is known; s solves angle(u(s), w) = a2 (a 1-D root, transversal by design), q2 is the azimuth of
w about p2 from the track tangent, q3 the twist about w. Three real joints the arm drives, nothing free, nothing sags.

SPEC CHANGES (stated in docs/concepts/scapula-halo-track.md):
  1. The track is at ONE radius from GH (a curve on a sphere). The spec gave every track sample its own radius (skin
     requirement + 5). That is not buildable as a spherical joint: the carriage pose on the track must be a rotation
     about GH, so its rollers sweep a constant radius; a varying radius would push the J2 bearing along its axis while
     link 2 (rigid, both axes through GH) keeps its radius - it binds. A varying radius needs a passive radial slide
     AND a pitch pivot in the bogie; not modelled (would add 2 closure-set passive elements).
  2. Branch: the spec picks the root by sign((u x du/ds).w); for a convex loop both crossings of the circle about w
     have the SAME sign of that (mirror symmetry), so it cannot tell them apart. The roots alternate in the sign of
     du/ds.w (in / out of the circle), so sigma = sign(t . w) at the root.
  3. Transversality = |cos phi| >= sin(10 deg) (phi = angle between link 2 and the track tangent at J2, the evaluator's
     10 deg singularity margin); the spec's 0.5 deg per 3 deg-az sample depends on the sampling (at el 80 a 3 deg az
     step is only 0.5 deg of arc) - same order (sin 10 = 0.17 vs 0.5/3 = 0.17).
  4. Clip continuity is checked on EVERY 10 fps frame of each fit clip (the bench samples every ~6th frame), jump
     <= 25 deg per frame in s (arc deg), q2, q3; a frame whose tracked root vanished is not followed.
  5. Link 2 over the track: generic 1 mm clearance rule (the spec's +4.5 mm assumed a carriage passing under link 2,
     which cannot happen: the carriage is always at link 2's own J2 end).
Geometry (every part at its real size; skin-facing surfaces sampled on a 2 mm grid = 1 point / 4 mm2, the baseline's
convention; radii from the K3 requirement: first radius on the ray >= 2 mm out of the skin with >= 15 mm free beyond,
quantile q over the poses the chain closes in; flat hub discs; straps ramp at <= 60 deg from the hub plane).
Taken: closure on the design branch, transversal, residual < 0.5 deg; track span (open track); clip frames followed;
no interference between non-adjacent members (>= 1 mm, K6 with joint partners exempt within 12 mm of their joint);
no metal inside the body (tops / sides / crowns checked too: one inside sample is appended so the bench sees contact).

    python3 docs/concepts/models/scapula-halo-track.py check     # a few poses on the bench, numbers + reasons
    python3 docs/concepts/models/scapula-halo-track.py sweep     # coarse -> refine sweep on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "scapula-halo-track"
D2R = math.pi / 180
TR_W, TR_T = 8.0, 5.0                     # track section (spec: Ti ring 8 x 5)
CAR_L, CAR_W, CAR_T = 20.0, 16.0, 9.0     # carriage block (spec: 20 x 16, radial [Rt, Rt + 9])
HUB_R, STACK, CROWN, PLATE = 10.0, 3.15, 12.25, 3.0   # O20 v5 joint (docs/HARDWARE.md): upper member at F + 3.15, crown F + 12.25
L2_W, L2_T = 12.0, 3.0                    # link 2 strap (spec K5)
NK_W, NK_T = 14.0, 6.0                    # neck strap (spec K7)
SP = 2.0                                  # sample grid (1 point / 4 mm2)
RAMP = math.tan(60 * D2R)                 # strap leaves a hub plane at <= 60 deg
SING = 10.0                               # deg: transversality margin at the crossing (evaluator's sing_deg)
FLIP = 25.0                               # deg per 10 fps frame: larger joint jump = branch flip / not followed
CLR, WIN, T0, T1 = 2.0, 15.0, 15.0, 220.0  # K3 requirement: >= CLR out, free for WIN beyond, searched T0..T1 mm
GAP = 1.0                                 # mm clearance between non-adjacent members
EXEMPT = HUB_R + 2.0                      # joint partners exempt within this of their joint (mm)
NT = 360                                  # track polyline samples (kinematics)
R_REF = 60.0                              # mm, radius used to space the direction samples
TI = 4.43e-3                              # g / mm3

# BOTTOM's bar (spec K7), in the body_pose humerus frame (B.frames H); converted to the evaluator's HG frame below
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713])
BAR0_H = 67.5 * WB + 40.0 * DB

PARAMS = dict(thr=13, shrink=4.0, fh=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], W_delta=112.0, W_az=-15.0, a2=55.0, sigma=1, q=1.0,
              order="A", closed=1)
SWEEP = dict(thr=(8, 13, 20), shrink=(-4, 10), fh=("3 harmonics, +-8 deg",), W_delta=(75, 115), W_az=(-40, 55), a2=(45, 120),
             sigma=(-1, 1), q=(0.93, 0.97, 1.0), order=("A: arm-end plate lower at J3", "L: link 2 lower"), closed=(0, 1))


def bvec(az, el):
    """scapula frame: az 0 posterior, 90 lateral, 180 anterior, -90 medial (= concept_baseline.bvec)"""
    az, el = np.asarray(az, float) * D2R, np.asarray(el, float) * D2R
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def perp(v):
    a = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    x = unit(a - (a @ v) * v); return x, np.cross(v, x)


def wrap(x, per=360.0):
    return (np.asarray(x) + per / 2) % per - per / 2


# ---------------------------------------------------------------- frames
_Z = CB._poses_all()
_B0 = None


def _hg_from_h():
    """constant C with RS @ HG @ C = body_pose H (both frames are fixed to the humerus; checked on the bench poses)"""
    import body_pose as BP
    r = BP._rig(); p = _Z["POSE"][0]
    (T, S, H, Fa, Pr), lift = BP.segs(r.L, r.s, dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])))
    return (_Z["RS"][0].astype(float) @ _Z["HG"][0].astype(float)).T @ H[0]


C_HG_H = _hg_from_h()
BAR0 = C_HG_H @ BAR0_H                     # bar start in the HG frame (mm from GH)


# ---------------------------------------------------------------- track
_MAP = json.load(open(os.path.join(REPO, "pipeline", "conformal", "analysis", "skin_motion_map_14.json")))["scapula"]["grid"]


_IB = {}                                   # bench in-band map (set by Ctx): az, el grid and share of poses in band


def ib_map(B, RS):
    """the rawest guide for a scapula-fixed part: per scapula-frame direction (az step 6, el step 3), the K3 requirement
    in every bench pose; a part fixed at the worst-pose requirement is in band (2-14 mm) in pose i when
    max - req_i <= 12. Returns the share of poses in band per direction (and the max requirement)."""
    if "share" in _IB: return _IB
    AZ = np.arange(-180, 180, 6.0); EL = np.arange(-10, 89, 3.0)
    A, E = np.meshgrid(AZ, EL, indexing="ij"); U = bvec(A.ravel(), E.ravel())
    RQ = np.stack([requirement(B, i, U @ RS[i].T) for i in range(len(B.poses))])
    RQ = np.where(np.isfinite(RQ), RQ, 400.0).reshape(len(RQ), len(AZ), len(EL)); top = RQ.max(0)
    _IB.update(AZ=AZ, EL=EL, share=((top[None] - RQ) <= 12).mean(0), top=top)
    return _IB


def contour(thr):
    """el*(az) (deg): thr a number -> the skin-motion map's contour (lowest el above which every cell has
    0 <= motion <= thr); thr "ibNN" -> the bench in-band contour (lowest el above which every direction is in band in
    >= NN % of the bench poses, ib_map). 9-tap circular mean."""
    if isinstance(thr, str):
        S = _IB["share"] >= int(thr[2:]) / 100.0; EL = _IB["EL"]; el = np.empty(len(_IB["AZ"]))
        # erode the zone by one cell in el and two in az (the track is 8 mm wide and the carriage 16 mm; the raised arm's
        # edge crosses the map between grid points - measured: 165 mm requirement at az -79 el 71 in elev 165, map cell 56)
        S0 = S.copy()
        for da in (-2, -1, 1, 2): S &= np.roll(S0, da, 0)
        S[:, 1:] &= S0[:, :-1]; S[:, :-1] &= S0[:, 1:]
        for i in range(len(el)):
            k = len(EL) - 1
            if not S[i, k]: el[i] = EL[-1]; continue
            while k > 0 and S[i, k - 1]: k -= 1
            el[i] = EL[k]
        # conservative smoothing (into the zone): max over +-24 deg of az, then a 5-tap mean - a plain mean across the
        # zone's steep posteromedial edge (el -2 at az -24 vs 62 at az -36) drags the loop onto skin the raised arm
        # covers overhead (measured: requirement > 100 mm at az -74..-30 in elev 150-165)
        mx = np.array([np.max(np.take(el, range(i - 4, i + 5), mode="wrap")) for i in range(len(el))])
        sm = np.array([np.mean(np.take(mx, range(i - 2, i + 3), mode="wrap")) for i in range(len(el))])
        return _IB["AZ"], sm
    a = np.array(_MAP["a"], float); b = np.array(_MAP["b"], float); M = np.array(_MAP["motion"], float)
    el = np.empty(len(a))
    for i in range(len(a)):
        ok = (M[i] >= 0) & (M[i] <= thr); k = len(b) - 1
        if not ok[k]: el[i] = b[-1]; continue
        while k > 0 and ok[k - 1]: k -= 1
        el[i] = b[k]
    sm = np.array([np.mean(np.take(el, range(i - 4, i + 5), mode="wrap")) for i in range(len(a))])
    return a, sm


class Track:
    """closed smooth loop on the unit sphere (scapula frame). The iso-motion contour of the map (thr) is fitted by a
    small circle (centre c, angular radius rho0) + a 3-harmonic Fourier series rho(psi) about c (psi = azimuth about c);
    the design then shrinks it by `shrink` deg toward c and adds the perturbation fh = (a1, b1, a2, b2, a3, b3) deg.
    (Spec change: the spec's el*(az) curve has kinks and runs 4-8 deg from the scapula pole medially, i.e. turns with a
    radius of a few mm - no bogie can run it; a loop about its own centre is smooth by construction.)"""
    def __init__(self, thr, shrink, fh):
        a, e = contour(thr); P = bvec(a, e)
        c = unit(P.mean(0))
        for _ in range(60):                                          # small-circle fit
            ang = np.arccos(np.clip(P @ c, -1, 1))
            g = (ang - ang.mean())[:, None] * (-(P - (P @ c)[:, None] * c) / np.sin(ang)[:, None])
            c = unit(c - 0.5 * g.mean(0))
        x, y = perp(c); psi = np.arctan2(P @ y, P @ x); ang = np.arccos(np.clip(P @ c, -1, 1))
        A = np.stack([np.ones_like(psi)] + sum([[np.cos(k * psi), np.sin(k * psi)] for k in (1, 2, 3)], []), 1)
        co = np.linalg.lstsq(A, ang, rcond=None)[0]
        co[0] -= shrink * D2R; co[1:] += np.asarray(fh, float) * D2R
        self.c, self.co, self.ex, self.ey = c, co, x, y
        ps = np.linspace(-math.pi, math.pi, 1440, endpoint=False)
        Ad = np.stack([np.ones_like(ps)] + sum([[np.cos(k * ps), np.sin(k * ps)] for k in (1, 2, 3)], []), 1)
        rho = np.clip(Ad @ co, 5 * D2R, 85 * D2R)
        Pd = np.cos(rho)[:, None] * c + np.sin(rho)[:, None] * (np.cos(ps)[:, None] * x + np.sin(ps)[:, None] * y)
        seg = np.arccos(np.clip((Pd * np.roll(Pd, -1, 0)).sum(1), -1, 1)); cum = np.r_[0, np.cumsum(seg)]; L = cum[-1]
        s = np.linspace(0, L, NT, endpoint=False); Pc = np.r_[Pd, Pd[:1]]
        U = unit(np.stack([np.interp(s, cum, Pc[:, j]) for j in range(3)], 1))
        self.U = U; self.L = L / D2R; self.s = s / D2R; self.ds = self.L / NT
        T = unit(np.roll(U, -1, 0) - np.roll(U, 1, 0)); T = unit(T - (T * U).sum(1, keepdims=True) * U)
        self.T = T; self.N = np.cross(U, T)
        dT = (np.roll(T, -1, 0) - np.roll(T, 1, 0)) / (2 * self.ds * D2R)
        self.kg = (dT * self.N).sum(1)                               # signed geodesic curvature (1/rad)
        self.rho_deg = rho / D2R
        el = np.arcsin(np.clip(U[:, 1], -1, 1)) / D2R; az = np.arctan2(U[:, 2], -U[:, 0]) / D2R
        self.az, self.el = az, el

    def min_turn_radius(self, R):
        """smallest in-plane turning radius (mm) of the track at radius R (geodesic curvature)"""
        return R / max(float(np.abs(self.kg).max()), 1e-9)

    def at(self, s):
        """unit dir, tangent, normal at arc positions s (deg), interpolated"""
        x = (np.asarray(s, float) % self.L) / self.ds; j = np.floor(x).astype(int) % NT; t = (x - np.floor(x))[..., None]
        k = (j + 1) % NT
        u = unit((1 - t) * self.U[j] + t * self.U[k]); T = unit((1 - t) * self.T[j] + t * self.T[k])
        T = unit(T - (T * u).sum(-1, keepdims=True) * u)
        return u, T, np.cross(u, T)


# ---------------------------------------------------------------- kinematics
def roots(tr, w, a2, sigma):
    """all crossings of the track with the circle of radius a2 about w (scapula frame), on branch sigma.
    -> list of dict(s, u, t, cphi, res) ; cphi = cos of the angle between link 2 and the track tangent"""
    f = np.arccos(np.clip(tr.U @ w, -1, 1)) - a2
    g = np.roll(f, -1); idx = np.nonzero((f <= 0) & (g > 0) | (f > 0) & (g <= 0))[0]
    out = []
    for j in idx:
        t = f[j] / (f[j] - g[j]); s = (j + t) * tr.ds
        for _ in range(2):                                       # Newton on the interpolated curve
            u, T, _n = tr.at(s); fs = math.acos(min(1, max(-1, u @ w))) - a2
            dfs = -(T @ w) / max(math.sin(math.acos(min(1, max(-1, u @ w)))), 1e-6)
            if abs(dfs) > 1e-6: s = s - fs / dfs / D2R
        u, T, n = tr.at(s); res = abs(math.acos(min(1, max(-1, u @ w))) - a2) / D2R
        cphi = (T @ w) / max(math.sin(a2), 1e-6)
        if (1 if cphi > 0 else -1) != sigma: continue
        out.append(dict(s=float(s % tr.L), u=u, t=T, n=n, cphi=float(cphi), res=float(res)))
    return out


def joints(r, w, ref3):
    """joint values (deg): s, q2 (azimuth of w about p2 from the track tangent), q3 (azimuth of p2 about w from ref3)"""
    u, T, n = r["u"], r["t"], r["n"]
    q2 = math.atan2(n @ w, T @ w) / D2R
    y = np.cross(w, ref3); q3 = math.atan2(u @ y, u @ ref3) / D2R
    return np.array([r["s"], q2, q3])


def jump(a, b, L):
    return max(abs(wrap(a[0] - b[0], L)), abs(wrap(a[1] - b[1])), abs(wrap(a[2] - b[2])))


class Kin:
    """kinematics of one design on the bench poses + every frame of the fit clips (vectorised over poses)"""
    def __init__(self, p, tr, HG=None):
        self.p = p; self.tr = tr; self.W0 = w_dir(p["W_delta"], p["W_az"]); self.a2 = p["a2"] * D2R
        x, _ = perp(self.W0); self.R0 = x                       # q3 reference in the humerus frame
        self.cmin = math.sin(SING * D2R)

    def batch(self, HGs):
        """candidate roots (design branch, transversal, residual < 0.5 deg) for every pose: list of lists of dicts"""
        tr = self.tr; W = HGs @ self.W0; REF = HGs @ self.R0; Pn = len(W)
        Fm = np.arccos(np.clip(tr.U @ W.T, -1, 1)) - self.a2                 # (NT, P)
        G = np.roll(Fm, -1, 0); j, pi = np.nonzero(((Fm <= 0) & (G > 0)) | ((Fm > 0) & (G <= 0)))
        out = [[] for _ in range(Pn)]
        if not len(j): return out
        k = (j + 1) % NT; t = (Fm[j, pi] / (Fm[j, pi] - G[j, pi]))[:, None]
        u = unit((1 - t) * tr.U[j] + t * tr.U[k]); T = unit((1 - t) * tr.T[j] + t * tr.T[k]); T = unit(T - (T * u).sum(1, keepdims=True) * u)
        n = np.cross(u, T); w = W[pi]; ref = REF[pi]
        res = np.abs(np.arccos(np.clip((u * w).sum(1), -1, 1)) - self.a2) / D2R
        cphi = (T * w).sum(1) / max(math.sin(self.a2), 1e-6)
        q2 = np.arctan2((n * w).sum(1), (T * w).sum(1)) / D2R
        y = np.cross(w, ref); q3 = np.arctan2((u * y).sum(1), (u * ref).sum(1)) / D2R
        s = ((j + t[:, 0]) * tr.ds) % tr.L
        ok = (np.sign(cphi) == self.p["sigma"]) & (np.abs(cphi) >= self.cmin) & (res < 0.5)
        for m in np.nonzero(ok)[0]:
            out[pi[m]].append(dict(s=float(s[m]), u=u[m], t=T[m], n=n[m], cphi=float(cphi[m]), res=float(res[m]), q=np.array([s[m], q2[m], q3[m]])))
        return out

    def cands(self, HGi):
        return self.batch(HGi[None])[0]

    def clips(self):
        """dense tracking on every fit-clip frame -> {pose-file index: root dict or reason str}"""
        names = list(_Z["NAMES"]); st = {}
        for nm in CB.FIT:
            ix = np.nonzero(_Z["CID"] == names.index(nm))[0]; ix = ix[np.argsort(_Z["FI"][ix], kind="stable")]
            C = self.batch(_Z["HG"][ix].astype(float)); last = None
            for j, c in zip(ix, C):
                if not c: st[int(j)] = "closure"; continue
                if last is None:
                    r = max(c, key=lambda r: abs(r["cphi"]))
                else:
                    r = min(c, key=lambda r: jump(r["q"], last, self.tr.L))
                    if jump(r["q"], last, self.tr.L) > FLIP: st[int(j)] = "flip"; continue
                st[int(j)] = r; last = r["q"]
        return st


# ---------------------------------------------------------------- K3 requirement (sphere-traced march)
def requirement(B, i, D):
    """first radius t in [T0, T1] along unit thorax dirs D (k, 3) with dist >= CLR and >= 0 over [t, t + WIN]; inf if none"""
    k = len(D); t = np.full(k, T0); c = t.copy(); chk = np.zeros(k, bool); res = np.full(k, np.inf); act = np.ones(k, bool)
    for _ in range(80):
        a = np.nonzero(act)[0]
        if not len(a): break
        x = np.where(chk[a], c[a], t[a]); d = B.dist(i, D[a] * x[:, None])
        s = ~chk[a]
        # search mode
        sa = a[s]; ds_ = d[s]; good = ds_ >= CLR
        chk[sa[good]] = True; c[sa[good]] = t[sa[good]] + np.maximum(ds_[good], 0.5)
        t[sa[~good]] += np.maximum(CLR - ds_[~good], 0.5)
        # check mode
        ca = a[~s]; dc = d[~s]; bad = dc < 0
        chk[ca[bad]] = False; t[ca[bad]] = c[ca[bad]] + CLR - dc[bad]
        c[ca[~bad]] += np.maximum(dc[~bad], 0.5)
        done = chk & (c >= t + WIN) & act; res[done] = t[done]; act &= ~done
        fail = act & (t > T1); act &= ~fail
    return res


def lip(req, x, hubs):
    """strap underside along x (n,) mm: >= req (n, m), slope <= RAMP, = hub level inside each hub zone.
    hubs: list of (x0 centre, level). Returns (profile (n, m), raised hub levels)"""
    req = np.where(np.isfinite(req), req, 400.0)
    env = (req[None, :, :] - RAMP * np.abs(x[:, None, None] - x[None, :, None])).max(1)
    lv = []
    for x0, h in hubs:
        z = np.abs(x - x0) <= HUB_R
        h = max(h, float(env[z].max()) if z.any() else h); lv.append(h)
    out = env.copy()
    for (x0, _), h in zip(hubs, lv):
        out = np.maximum(out, (h - RAMP * np.maximum(np.abs(x - x0) - HUB_R, 0))[:, None])
        out[np.abs(x - x0) <= HUB_R] = h
    return out, lv


def qtl(a, q, axis=0):
    a = np.where(np.isfinite(a), a, 400.0)
    return np.quantile(a, q, axis=axis) if q < 1 else a.max(axis)


def smooth_up(r, x, slope, w, cyclic):
    """>= r, slope <= `slope`, then max-filter + box mean over +-w mm (still >= r, no kinks for the bogie)"""
    n = len(r); dx = np.abs(x[:, None] - x[None, :])
    if cyclic: P = x[-1] - x[0] + (x[1] - x[0]); dx = np.minimum(dx, P - dx)
    env = (r[None, :] - slope * dx).max(1)
    near = dx <= w
    mx = np.array([env[near[k]].max() for k in range(n)])
    return np.array([mx[near[k]].mean() for k in range(n)])


def circ_span(s, L, pad):
    """smallest arc [lo, hi] (deg, hi may exceed L) covering positions s on a loop of length L, + pad each side"""
    if not len(s): return 0.0, 0.0
    a = np.sort(np.asarray(s) % L); g = np.diff(np.r_[a, a[0] + L]); k = int(np.argmax(g))
    lo = a[(k + 1) % len(a)]; hi = a[k] if k + 1 < len(a) else a[k]
    if hi < lo: hi += L
    lo, hi = lo - pad, hi + pad
    if hi - lo >= L: return 0.0, L
    return lo, hi


def in_span(s, lo, hi, L):
    return ((np.asarray(s) - lo) % L) <= (hi - lo) + 1e-9


def grid2(L, W, step=SP):
    x = np.linspace(-L / 2, L / 2, int(round(L / step)) + 1); y = np.linspace(-W / 2, W / 2, int(round(W / step)) + 1)
    X, Y = np.meshgrid(x, y, indexing="ij"); return X.ravel(), Y.ravel()


def disc2(r=HUB_R, step=SP):
    g = np.arange(-r, r + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= r * r + 1e-9
    return X[k], Y[k]


DX, DY = disc2()
CX, CY = grid2(CAR_L, CAR_W)


class Ctx:
    """per-bench caches shared by every configuration of a sweep"""
    def __init__(self, B):
        self.B = B; self.HG = _Z["HG"][B.idx].astype(float); self.RS = _Z["RS"][B.idx].astype(float)
        self.tracks = {}; self.treq = {}; self.wreq = {}; self.clipst = {}
        ib_map(B, self.RS)

    def track(self, p):
        k = (p["thr"], round(p["shrink"], 3), tuple(round(v, 3) for v in p["fh"]))
        if k not in self.tracks:
            tr = Track(*k); n = max(8, int(round(tr.L * D2R * R_REF / SP)))
            sa = np.linspace(0, tr.L, n, endpoint=False); u, t, nn = tr.at(sa)
            cc = np.linspace(-TR_W / 2, TR_W / 2, int(round(TR_W / SP)) + 1)
            D = unit(u[:, None, :] + (cc[None, :, None] / R_REF) * nn[:, None, :])        # (n, 5, 3) scapula frame
            tr.sa, tr.su, tr.st, tr.sn, tr.cc, tr.D = sa, u, t, nn, cc, D
            self.tracks = {k: tr}; self.treq = {}
        return self.tracks[k], k

    def track_req(self, k, tr, I):
        """K3 requirement (max across the width) of every track sample in poses I -> dict i -> (n,)"""
        R = self.treq
        for i in I:
            if i not in R:
                R[i] = requirement(self.B, i, tr.D.reshape(-1, 3) @ self.RS[i].T).reshape(tr.D.shape[:2]).max(1)
        return R

    def arm_req(self, W0, I, Fn):
        """J3 disc + neck requirements (fixed in the humerus) per pose. Fn: nominal disc height (directions)"""
        key = (tuple(np.round(W0, 6)), round(Fn, 1))
        if key not in self.wreq: self.wreq = {key: {}}
        R = self.wreq[key]
        a, b = perp(W0)
        disc = Fn * W0 + DX[:, None] * a + DY[:, None] * b; ddir = unit(disc); off2 = DX ** 2 + DY ** 2
        bar = unit(BAR0); ang = math.acos(np.clip(W0 @ bar, -1, 1)); e = unit(bar - (bar @ W0) * W0); m = np.cross(W0, e)
        ns = max(3, int(ang * R_REF / SP) + 1); th = np.linspace(0, ang, ns)
        cc = np.linspace(-NK_W / 2, NK_W / 2, int(round(NK_W / SP)) + 1)
        ND = unit((np.cos(th)[:, None] * W0 + np.sin(th)[:, None] * e)[:, None, :] + (cc[None, :, None] / R_REF) * m)
        for i in I:
            if i not in R:
                M_ = self.RS[i] @ self.HG[i]
                rq = requirement(self.B, i, np.r_[ddir, ND.reshape(-1, 3)] @ M_.T)
                rd = rq[:len(ddir)]; fd = np.sqrt(np.clip(rd ** 2 - off2, 0, None))
                R[i] = (float(np.where(np.isfinite(fd), fd, 400).max()), rq[len(ddir):].reshape(ND.shape[:2]))
        return R, dict(a=a, b=b, ND=ND, th=th, cc=cc, e=e, m=m, ang=ang)

    def clips(self, p, tr):
        k = (p["thr"], round(p["shrink"], 3), tuple(p["fh"]), p["W_delta"], p["W_az"], p["a2"], p["sigma"])
        if k not in self.clipst:
            if len(self.clipst) > 64: self.clipst = {}
            self.clipst[k] = Kin(p, tr, None).clips()
        return self.clipst[k]


class Design:
    def __init__(self, p, ctx):
        self.p = p = dict(PARAMS, **p); self.ctx = ctx; B = ctx.B; self.B = B; n = len(B.poses)
        self.tr, tk = ctx.track(p); tr = self.tr; self.tk = tk
        self.K = Kin(p, tr, None); W0 = self.K.W0; self.W0 = W0
        st = ctx.clips(p, tr); self.why = {}
        self.cand = [None] * n
        CW = self.K.batch(ctx.HG)
        for i in range(n):
            if B.kind[i] == "clip":
                r = st.get(int(B.idx[i]), "missing")
                self.cand[i] = [r] if isinstance(r, dict) else r
            else:
                c = sorted(CW[i], key=lambda r: -abs(r["cphi"]))
                self.cand[i] = c if c else "closure"
        self.F = [i for i in range(n) if isinstance(self.cand[i], list)]
        self.closure = float(np.mean([isinstance(self.cand[i], list) or self.cand[i] == "flip" for i in range(n)]))
        if not self.F: self.ok = False; return
        self.ok = True; self.fit()

    # ---- radii ------------------------------------------------------------------------------------------------------
    def fit(self):
        p = self.p; tr = self.tr; ctx = self.ctx; B = self.B; F = self.F; q = p["q"]; RS = ctx.RS; HG = ctx.HG
        s_used = np.array([self.cand[i][0]["s"] for i in F])
        pad = CAR_L / 2 / R_REF / D2R
        self.span = circ_span(s_used, tr.L, pad) if not p["closed"] else (0.0, tr.L)
        lo, hi = self.span; on = in_span(tr.sa, lo, hi, tr.L) if hi - lo < tr.L else np.ones(len(tr.sa), bool)
        self.on = on
        TR = ctx.track_req(self.tk, tr, F)
        need = qtl(np.stack([TR[i] for i in F]), q)                          # (n_along,)
        # carriage footprint need at its root, per pose -> raises the track where the carriage runs
        cneed = np.zeros(len(F)); r_off2 = CX ** 2 + CY ** 2
        for k, i in enumerate(F):
            r = self.cand[i][0]; D = unit(r["u"][None] * R_REF + CX[:, None] * r["t"] + CY[:, None] * r["n"])
            rq = requirement(B, i, D @ RS[i].T); f = np.sqrt(np.clip(np.where(np.isfinite(rq), rq, 400) ** 2 - r_off2, 0, None))
            cneed[k] = f.max()
        dsa = tr.sa[1] - tr.sa[0]
        for j in np.nonzero(on)[0]:
            m = np.abs(wrap(s_used - tr.sa[j], tr.L)) <= pad
            if m.any(): need[j] = max(need[j], float(qtl(cneed[m], q)))
        xs = tr.sa * D2R * R_REF
        if p.get("mode", "slide") == "sphere":
            Rt = np.full(len(need), float(need[on].max()))
        else:
            Rt = smooth_up(need, xs, math.tan(30 * D2R), CAR_L / 2, cyclic=bool(p["closed"]) or hi - lo >= tr.L)
        self.Rt = Rt; self.need = need
        used = np.zeros(len(tr.sa), bool)
        for s in s_used: used[np.argmin(np.abs(wrap(tr.sa - s, tr.L)))] = True
        used = np.convolve(np.r_[used[-3:], used, used[:3]].astype(float), np.ones(7), "same")[3:-3] > 0
        self.H2 = float(Rt[used].max()) + CAR_T + 0.15                          # link 2 eye underside (fixed in link 2)
        self.slide = float(Rt[used].max() - Rt[used].min())                    # passive radial slide travel at J2
        # ---- J3 disc + neck
        R0, NG = ctx.arm_req(self.W0, F, 60.0)
        F3d = float(qtl(np.array([R0[i][0] for i in F]), q))
        if abs(F3d - 60.0) > 4: R0, NG = ctx.arm_req(self.W0, F, round(F3d))
        F3d = float(qtl(np.array([R0[i][0] for i in F]), q)); self.NG = NG
        nreq = qtl(np.stack([R0[i][1] for i in F]), q)                        # (ns, 8)
        # ---- link 2: samples in its own frame (theta along p2 -> w, c across)
        a2 = p["a2"] * D2R; ns = max(3, int(a2 * R_REF / SP) + 1); th = np.linspace(0, a2, ns)
        cc = np.linspace(-L2_W / 2, L2_W / 2, int(round(L2_W / SP)) + 1); self.l2 = (th, cc)
        F3n = F3d; F3_0 = F3d
        for _pass in range(3):                                                 # neck level <-> link 2 clearance
            F3d = F3_0
            L2req = []; on = self.on
            Np0, _ = lip(nreq, NG["th"] * 65.0, [(0.0, F3n)])                     # neck underside at the last pass's J3 level
            nkeep = NG["th"] * 65.0 > HUB_R; ntop = Np0.max(1) + NK_T; nbot = Np0.min(1)   # per neck station
            Td = unit(tr.D[on].reshape(-1, 3)); Ttop = np.repeat(self.Rt[on], len(tr.cc)) + TR_T; tree = cKDTree(Td)
            for i in F:
                r = self.cand[i][0]; D = self.l2dirs(i, r); Dd = D.reshape(-1, 3)
                rq = requirement(B, i, Dd @ RS[i].T)
                # link 2 must clear the track (top + GAP) and the carriage (top + GAP) wherever it passes over them
                far = np.arccos(np.clip(Dd @ r["u"], -1, 1)) * self.H2 > EXEMPT      # (was * 60 mm: link 2 runs at H2,
                # so samples 10-12 mm from J2 escaped this raise but not the K6 check -> carriage/link2 interference)
                M_ = tree.sparse_distance_matrix(cKDTree(Dd), (2.0 + GAP) / 35.0, output_type="ndarray")
                if len(M_):
                    lat = 2 * np.arcsin(np.clip(M_["v"] / 2, 0, 1)) * Ttop[M_["i"]]
                    k = (lat < 2.0 + GAP) & far[M_["j"]]
                    np.maximum.at(rq, M_["j"][k], Ttop[M_["i"][k]] + GAP)
                Rc = float(np.interp(r["s"] % tr.L, np.r_[tr.sa, tr.L], np.r_[self.Rt, self.Rt[0]]))
                loc = np.c_[Dd @ r["t"], Dd @ r["n"]] * Rc
                ov = far & (np.abs(loc[:, 0]) < CAR_L / 2 + 2 + GAP) & (np.abs(loc[:, 1]) < CAR_W / 2 + 2 + GAP)
                rq[ov] = np.maximum(rq[ov], Rc + CAR_T + GAP)
                # link 2 must clear the neck (top + GAP) wherever it passes over it away from J3 (measured: link2/armend
                # interference in 19 % of poses when the neck and link 2 leave J3 on close azimuths)
                w3 = HG[i] @ self.W0; NDi = (NG["ND"] @ HG[i].T)[nkeep].reshape(-1, 3); Ntop = np.repeat(ntop[nkeep], NDi.shape[0] // max(nkeep.sum(), 1)); Nbot = np.repeat(nbot[nkeep], NDi.shape[0] // max(nkeep.sum(), 1))
                far3 = np.arccos(np.clip(Dd @ w3, -1, 1)) * F3d > EXEMPT
                M_ = cKDTree(NDi).sparse_distance_matrix(cKDTree(Dd), (2.0 + GAP) / 35.0, output_type="ndarray")
                if len(M_):
                    lat = 2 * np.arcsin(np.clip(M_["v"] / 2, 0, 1)) * Nbot[M_["i"]]
                    k = (lat < 2.0 + GAP) & far3[M_["j"]]
                    np.maximum.at(rq, M_["j"][k], Ntop[M_["i"][k]] + GAP)
                L2req.append(rq.reshape(D.shape[:2]))
            lreq = qtl(np.stack(L2req), q)
            xl = th * 65.0; xn = NG["th"] * 65.0
            up = STACK                                                             # upper member underside above F
            for _ in range(3):
                l3 = F3d + (up if p["order"] == "A" else 0.0); n3 = F3d + (0.0 if p["order"] == "A" else up)
                Lp, (h2, h3) = lip(lreq, xl, [(0.0, self.H2), (xl[-1], l3)])
                Np, (hn,) = lip(nreq, xn, [(0.0, n3)])
                F3 = max(F3d, h3 - (l3 - F3d), hn - (n3 - F3d))
                if F3 <= F3d + 1e-6: break
                F3d = F3
            if F3d <= F3n + 0.25: break
            F3n = F3d
        self.H2 = max(self.H2, h2); self.F3 = F3d; self.Lp = Lp; self.Np = Np; self.xl, self.xn = xl, xn
        self.l3, self.n3 = l3, n3

    def l2dirs(self, i, r):
        th, cc = self.l2
        p2 = r["u"]; w = self.ctx.HG[i] @ self.W0; e = unit(w - (w @ p2) * p2); m = np.cross(p2, e)
        return unit((np.cos(th)[:, None] * p2 + np.sin(th)[:, None] * e)[:, None, :] + (cc[None, :, None] / R_REF) * m)

    # ---- one pose ---------------------------------------------------------------------------------------------------
    def parts(self, i, r):
        """members of pose i on root r: name -> dict(face (k,3) skin-facing pts, other (m,3), dirs, r0, r1) in the
        scapula frame (thorax = RS @)"""
        p = self.p; tr = self.tr; HG = self.ctx.HG[i]; out = {}
        on = self.on
        # track
        P0 = self.Rt[on, None, None] * tr.su[on, None, :] + tr.cc[None, :, None] * tr.sn[on, None, :]
        up = tr.su[on, None, :]
        face = P0.reshape(-1, 3); top = (P0 + TR_T * up).reshape(-1, 3)
        side = np.r_[P0[:, 0] + TR_T / 2 * up[:, 0], P0[:, -1] + TR_T / 2 * up[:, 0]]
        out["track"] = dict(face=face, other=np.r_[top, side], r0=np.repeat(self.Rt[on], len(tr.cc)), r1=np.repeat(self.Rt[on] + TR_T, len(tr.cc)))
        # carriage (flat plate tangent to the track at the carriage, pitched with the track slope)
        s = r["s"]; j = np.searchsorted(tr.sa, s % tr.L) % len(tr.sa); jp = (j - 1) % len(tr.sa)
        x0, x1 = tr.sa[jp], tr.sa[j]; tt = ((s - x0) % tr.L) / max((x1 - x0) % tr.L, 1e-9)
        Rc = (1 - tt) * self.Rt[jp] + tt * self.Rt[j]
        dR = (self.Rt[j] - self.Rt[jp]) / (((x1 - x0) % tr.L) * D2R)              # mm per rad
        u, t, n = r["u"], r["t"], r["n"]; t3 = unit(dR * u + Rc * t); u3 = np.cross(t3, n)
        Pc = Rc * u + CX[:, None] * t3 + CY[:, None] * n
        ctop = Pc + CAR_T * u3
        cside = np.r_[Pc[np.abs(CY) >= CAR_W / 2 - 1e-6] + CAR_T / 2 * u3, Pc[np.abs(CX) >= CAR_L / 2 - 1e-6] + CAR_T / 2 * u3]
        # J2: link-2 eye (O20 boss) at H2 on the slider pin; skin-facing only where it overhangs the carriage
        eye = self.H2 * u + DX[:, None] * t + DY[:, None] * n
        over = np.abs(DY) > CAR_W / 2
        crown = max(self.H2 + CROWN - STACK, Rc + CAR_T + self.slide + CROWN - STACK + 0.15)
        cap = crown * u + DX[:, None] * t + DY[:, None] * n
        out["carriage"] = dict(face=np.r_[Pc, eye[over]], other=np.r_[ctop, cside, cap],
                               r0=np.r_[np.full(len(Pc), Rc), np.full(len(DX), self.H2)], r1=np.r_[np.full(len(Pc), Rc + CAR_T), np.full(len(DX), crown)],
                               vd=np.r_[Pc, eye])
        # link 2
        D = self.l2dirs(i, r); xl = self.xl; L = xl[-1]
        keep = (xl > HUB_R) & (xl < L - HUB_R)
        Pl = D * self.Lp[:, :, None]
        out["link2"] = dict(face=Pl[keep].reshape(-1, 3), other=(D * (self.Lp + L2_T)[:, :, None])[keep].reshape(-1, 3),
                            r0=self.Lp[keep].ravel(), r1=(self.Lp + L2_T)[keep].ravel(), vd=Pl[keep].reshape(-1, 3))
        # J3 + arm-end plate + neck (fixed in the humerus)
        a, b = HG @ self.NG["a"], HG @ self.NG["b"]; w = HG @ self.W0
        disc = self.F3 * w + DX[:, None] * a + DY[:, None] * b
        c3 = (self.F3 + CROWN) * w + DX[:, None] * a + DY[:, None] * b
        ND = self.NG["ND"] @ HG.T; keep = self.xn > HUB_R
        Pn = ND * self.Np[:, :, None]
        out["armend"] = dict(face=np.r_[disc, Pn[keep].reshape(-1, 3)], other=np.r_[c3, (ND * (self.Np + NK_T)[:, :, None])[keep].reshape(-1, 3)],
                             r0=np.r_[np.full(len(DX), self.F3), self.Np[keep].ravel()],
                             r1=np.r_[np.full(len(DX), self.F3 + CROWN), (self.Np + NK_T)[keep].ravel()], vd=np.r_[disc, Pn[keep].reshape(-1, 3)])
        out["track"]["vd"] = face
        self._j2, self._j3 = u, w
        return out

    def interfere(self, P):
        """K6: lateral (centre spacing < 1 + 1 + GAP mm at the lower radius) and radial interval overlap (+ GAP)"""
        pairs = [("track", "link2", self._j2), ("track", "armend", None), ("carriage", "armend", None),
                 ("link2", "armend", self._j3), ("carriage", "link2", self._j2)]
        for an, bn, jx in pairs:
            A, Bm = P[an], P[bn]
            da, db = unit(A["vd"]), unit(Bm["vd"])
            ra0, ra1, rb0, rb1 = A["r0"], A["r1"], Bm["r0"], Bm["r1"]
            if jx is not None:
                ka = np.arccos(np.clip(da @ jx, -1, 1)) * ra0 > EXEMPT; kb = np.arccos(np.clip(db @ jx, -1, 1)) * rb0 > EXEMPT
                da, ra0, ra1 = da[ka], ra0[ka], ra1[ka]; db, rb0, rb1 = db[kb], rb0[kb], rb1[kb]
            if not len(da) or not len(db): continue
            M_ = cKDTree(da).sparse_distance_matrix(cKDTree(db), (2.0 + GAP) / 40.0, output_type="ndarray")
            if not len(M_): continue
            ia, ib = M_["i"], M_["j"]; rr = np.minimum(ra0[ia], rb0[ib])
            lat = 2 * np.arcsin(np.clip(M_["v"] / 2, 0, 1)) * rr
            hit = (lat < 2.0 + GAP) & (ra0[ia] < rb1[ib] + GAP) & (rb0[ib] < ra1[ia] + GAP)
            if hit.any(): return f"{an}/{bn}"
        return None

    def metal(self, i, detail=False):
        """(thorax points or None, reason, per-member face counts)"""
        c = self.cand[i]
        if not self.ok: return None, "no design", None
        if not isinstance(c, list): return None, c, None
        RS = self.ctx.RS[i]; last = None
        for r in c:
            if not self.p["closed"] and not in_span(r["s"], *self.span, self.tr.L): last = (None, "off track", None); continue
            P = self.parts(i, r); w = self.interfere(P)
            if w: last = (None, "interference " + w, None); continue
            face = np.concatenate([P[k]["face"] for k in P]) @ RS.T
            other = np.concatenate([P[k]["other"] for k in P]) @ RS.T
            do = self.B.dist(i, other)
            if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
            cnt = {k: len(P[k]["face"]) for k in P}
            return face, "", cnt
        return last


def run(p, ctx, log=None):
    t = time.time(); B = ctx.B; D = Design(p, ctx); B.reset(); why = {}; per = {}
    for i in range(len(B.poses)):
        P, w, cnt = D.metal(i)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, P)
        if d.min() < 0: why["contact"] = why.get("contact", 0) + 1; continue
        if B.kind[i] == "clip":
            o = 0
            for k, nk in cnt.items():
                dd = d[o:o + nk]; o += nk; a = per.setdefault(k, [0, 0, 0]); a[0] += len(dd); a[1] += int(((dd >= 2) & (dd <= 14)).sum()); a[2] += int(((dd >= 2) & (dd <= 10)).sum())
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1); r["closure"] = round(D.closure, 3)
    if D.ok:
        r["shape"] = dict(Rt=[round(float(D.Rt[D.on].min()), 1), round(float(D.Rt[D.on].max()), 1)], H2=round(D.H2, 1), slide=round(D.slide, 1),
                          F3=round(D.F3, 1), L2=[round(float(D.Lp.min()), 1), round(float(D.Lp.max()), 1)],
                          neck=[round(float(D.Np.min()), 1), round(float(D.Np.max()), 1)] if D.Np.size else None,
                          track_deg=round(D.span[1] - D.span[0], 1), track_L=round(D.tr.L, 1), turn_r=round(D.tr.min_turn_radius(float(D.Rt.mean())), 1),
                          per={k: (round(v[1] / max(v[0], 1), 3), round(v[2] / max(v[0], 1), 3), v[0]) for k, v in per.items()},
                          mass_g=round(mass(D), 1))
    return r, D


def mass(D):
    tr = D.tr; on = D.on; dl = (tr.sa[1] - tr.sa[0]) * D2R
    m = float((D.Rt[on] * dl).sum()) * TR_W * TR_T                         # track
    m += CAR_L * CAR_W * CAR_T * 0.5                                       # carriage (pocketed ~50 %)
    th, cc = D.l2; m += float((D.Lp.mean(1) * (th[1] - th[0])).sum()) * L2_W * L2_T
    if D.Np.size: m += float((D.Np.mean(1) * (D.NG["th"][1] - D.NG["th"][0])).sum()) * NK_W * NK_T
    m += 2 * math.pi * HUB_R ** 2 * 6.0                                    # two O20 hubs (~6 mm of solid Ti equivalent)
    m += math.pi * 4 ** 2 * (D.slide + 10)                                 # J2 slider pin
    return m * TI


# ---------------------------------------------------------------- task API, sweep
def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _cache:
        _cache.clear(); _cache[key] = Design(prm, Ctx(B))
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KEYS = ("thr", "shrink", "fh", "W_delta", "W_az", "a2", "sigma", "q", "order", "closed", "mode")


def sweep(configs, ctx, out=SWEEP_OUT, tag=""):
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, ctx)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], closure=r["closure"], why=r["why"],
                   shape=r.get("shape"), mode=r["mode"], stage=tag, secs=r["secs"])
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} clos {r['closure']} | {r['why']} | {r.get('shape')} | {r['secs']} s | "
              + " ".join(f"{k}={p.get(k)}" for k in KEYS), flush=True)
    return rows


def mini(B, keep):
    """debug: restrict a Bench to the poses `keep` (indices)"""
    keep = list(keep); B.idx = B.idx[keep]; B.kind = [B.kind[k] for k in keep]; B.clip = [B.clip[k] for k in keep]
    B.poses = [B.poses[k] for k in keep]; B.res = [None] * len(keep); B._frames = {}; B._ex = {}; B._skin = {}
    if B.grid is not None: B.grid = B.grid[np.array(sorted(set(keep)))] if False else None; B.mode = "exact"
    return B


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40)
        if "mini" in a:
            ws = [j for j, k in enumerate(B.kind) if k == "ws"]; cl = [j for j, k in enumerate(B.kind) if k == "clip"]
            B = mini(B, cl[::4] + ws[::8])
        ctx = Ctx(B); p = dict(PARAMS)
        for kv in a[1:]:
            if "=" in kv: k, v = kv.split("="); p[k] = json.loads(v)
        r, D = run(p, ctx)
        print(json.dumps({k: v for k, v in r.items()}, default=str))
        for i in range(len(B.poses)):
            P, w, cnt = D.metal(i)
            d = B.res[i]
            print(i, B.kind[i], B.clip[i], {k: round(v) for k, v in B.poses[i].items()}, w or "taken",
                  "" if d is None else f"min {d.min():.1f} med {np.median(d):.1f} ib14 {np.mean((d >= 2) & (d <= 14)):.2f}")
