"""deltoid-oval-track: J3 is a closed oval cam track fixed to the upper arm on the deltoid cap; the J2 hub rides it on a
bogie carriage; link 1 runs from the J1 hub on the acromion top to J2 (3 ACTIVE DOF: q1, q2, s; 0 passive).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    J1 (ACTIVE): O20 hub, axis b = bvec(b_az, b_el) fixed in the scapula frame (acromion top); the handler's boss is the
       lower member, link 1 the upper member (F1 + 3.15)
    -> link 1: strap w1 wide x 3 thick on the great circle b -> p2 (arc a1), underside fitted to the skin (K3), <= 60 deg
       ramps off the hub planes
    -> J2 (ACTIVE): O20 hub, axis p2 = u(s) (radial through the carriage); the carriage is the lower member (F2 = R_O + 4)
    -> J3 (ACTIVE): bogie carriage 20 along x 16 across, radial [R_O - 5, R_O + 4], on a CLOSED oval track (Ti, 8 wide x
       5 radial, radial [R_O - 5, R_O]) fixed to the arm; its arc position s on the oval is the joint value
    -> the oval is the arm end: a 14 x 6 neck strap joins it to BOTTOM's bar (the user's part, not modelled as metal).
Oval (evaluator humerus frame HG, the frame of band_impl.w_dir and of BOTTOM's bar):
    u(t) = w_dir(d0 + A cos t + f2d cos 2t, a0 + Bw sin t + f2a sin 2t), resampled by arc length (s, arc deg).
DOF: given the arm, the closure is ONE equation angle(b, HG u(s)) = a1 (a 1-D root along the oval, transversal by design);
q1 = azimuth of p2 about b, q2 = azimuth of b about p2 from the oval tangent. Three coordinates the arm drives, all
sensable, nothing free, nothing sags (the carriage is pinned by the closure).

SPEC CHANGES (stated in docs/concepts/deltoid-oval-track.md; the same ones the sibling scapula-halo-track made):
  1. The track runs at ONE radius R_O from GH (a curve on a sphere). The spec gave every track sample its own radius
     (K3 + 5): a carriage on such a track does not rotate about GH, so with J1, J2 axes through GH the chain binds; a
     varying radius needs a passive radial slide in J2 AND a pitch pivot in the bogie (2 more closure-set elements,
     not modelled). A deep skin-following web under a spherical rail head was rejected too: it would put a skin-facing
     face near the skin while the rail, carriage, hub and link stand off - it games the in-band proxy.
  2. Branch: the spec's sign((V x dV/dt).b) is the azimuthal direction of the oval at the crossing, which is not a
     branch invariant (it can change sign along a continuous root). The roots alternate in the sign of dV/ds . b
     (into / out of the circle about b), so sigma = sign(T . b) at the root (cphi = T.b / sin a1).
  3. Transversality: |cphi| >= sin(10 deg) (cphi = cos of the angle between link 1 and the oval tangent at J2; the
     evaluator's 10 deg singularity margin); residual < 0.5 deg after Newton.
  4. Clip continuity on EVERY 10 fps frame of each fit clip: jump <= 25 deg per frame in s (arc deg), q1, q2; a frame
     whose tracked root vanished is not followed (the next frames are compared with the last followed one).
  5. Link 1 over the oval: generic 1 mm clearance (the link's profile is lifted over the oval / neck where they pass
     under it, at the same quantile q), not the spec's + 4.5.
Geometry (every part at its real size; skin-facing faces sampled on a 2 mm grid at R_REF = 70 mm (1 point / 4 mm2, the
baseline's spacing); hub discs on the baseline's 2.5 mm disc grid; radii from the K3 requirement: first radius on the
ray >= 2 mm out of the skin with >= 15 mm free beyond, quantile q over the bench poses the chain closes in (clip frames
followed + workspace poses); one-radius rigid parts (oval + carriage, hub discs) take the quantile of their per-pose max).
Taken (bench rules): closure on the design branch, transversal, residual < 0.5 deg; clip frames followed; no
interference between non-adjacent parts (>= 1 mm; direction / radial-interval test, K6); no metal inside the body.

    python3 docs/concepts/models/deltoid-oval-track.py check        # spec seed on Bench(20, 40), per-pose reasons
    python3 docs/concepts/models/deltoid-oval-track.py sweep        # coarse -> refine sweep on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "deltoid-oval-track"
D2R = math.pi / 180
TR_W, TR_T = 8.0, 5.0                     # oval track section (spec: 8 wide x 5 radial)
CAR_L, CAR_W, CAR_T = 20.0, 16.0, 9.0     # carriage block (spec: 20 x 16, radial [R_O - 5, R_O + 4])
HUB_R, STACK, CROWN, PLATE = 10.0, 3.15, 12.25, 3.0   # O20 v5 joint (docs/HARDWARE.md): upper member F + 3.15, crown F + 12.25
L1_T = 3.0                                # link 1 strap thickness (width w1 is a parameter; spec K5: 12)
NK_W, NK_T = 14.0, 6.0                    # neck strap (spec K7)
SP = 2.0                                  # sample grid (1 point / 4 mm2)
RAMP = math.tan(60 * D2R)                 # strap leaves a hub plane at <= 60 deg
SING = 10.0                               # deg: transversality margin at the crossing
FLIP = 25.0                               # deg per 10 fps frame: larger jump = branch flip / not followed
CLR, WIN, T0, T1 = 2.0, 15.0, 15.0, 220.0  # K3 requirement
GAP = 1.0                                 # mm clearance between non-adjacent parts
NT = 360                                  # oval polyline samples (kinematics)
R_REF = 70.0                              # mm, radius used to space direction samples (concept_baseline.arc_dirs)
TI = 4.43e-3                              # g / mm3
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713])   # BOTTOM's bar (band_impl defaults, HG frame)
BAR0 = 67.5 * WB + 40.0 * DB              # bar start (mm from GH)

PARAMS = dict(b_az=106.0, b_el=64.0, a1=70.0, d0=95.0, a0=-10.0, A=30.0, Bw=60.0, f2d=0.0, f2a=0.0, sigma=1, q=1.0, w1=12.0)
SWEEP = dict(b_az=(60, 130), b_el=(45, 75), a1=(50, 95), d0=(85, 115), a0=(-30, 10), A=(8, 35), Bw=(35, 70), f2d=(-8, 8),
             f2a=(-8, 8), sigma=(-1, 1), q=(0.9, 0.95, 1.0), w1=(8, 12))
KIN_KEYS = ("b_az", "b_el", "a1", "d0", "a0", "A", "Bw", "f2d", "f2a", "sigma")
OVAL_KEYS = ("d0", "a0", "A", "Bw", "f2d", "f2a")


def bvec(az, el):
    """scapula frame: az 0 posterior, 90 lateral, 180 anterior, -90 medial (= concept_baseline.bvec)"""
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dirs(delta, az):
    """humerus (HG) frame: delta from the down-the-arm axis, az 0 lateral, +90 anterior (= band_impl.w_dir), vectorised"""
    d, a = np.asarray(delta, float) * D2R, np.asarray(az, float) * D2R
    return np.stack([np.sin(d) * np.sin(a), -np.cos(d), np.sin(d) * np.cos(a)], -1)


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def perp(v):
    a = np.array([1.0, 0.0, 0.0]) if abs(v[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    x = unit(a - (a @ v) * v); return x, np.cross(v, x)


def wrap(x, per=360.0):
    return (np.asarray(x) + per / 2) % per - per / 2


_Z = CB._poses_all()


# ---------------------------------------------------------------- oval
class Oval:
    """closed oval on the unit sphere, humerus (HG) frame, resampled by arc length: U, T (tangent), N = U x T"""
    def __init__(self, p):
        t = np.linspace(0, 2 * math.pi, 2880, endpoint=False)
        d = p["d0"] + p["A"] * np.cos(t) + p["f2d"] * np.cos(2 * t); a = p["a0"] + p["Bw"] * np.sin(t) + p["f2a"] * np.sin(2 * t)
        P = w_dirs(d, a)
        seg = np.arccos(np.clip((P * np.roll(P, -1, 0)).sum(1), -1, 1)); cum = np.r_[0, np.cumsum(seg)]; L = cum[-1]
        s = np.linspace(0, L, NT, endpoint=False); Pc = np.r_[P, P[:1]]
        U = unit(np.stack([np.interp(s, cum, Pc[:, j]) for j in range(3)], 1))
        self.U = U; self.L = L / D2R; self.ds = self.L / NT
        T = unit(np.roll(U, -1, 0) - np.roll(U, 1, 0)); T = unit(T - (T * U).sum(1, keepdims=True) * U)
        self.T = T; self.N = np.cross(U, T)
        dT = (np.roll(T, -1, 0) - np.roll(T, 1, 0)) / (2 * self.ds * D2R)
        self.kg = (dT * self.N).sum(1)                                   # signed geodesic curvature (1/rad)
        self.delta = np.degrees(np.arccos(np.clip(-U[:, 1], -1, 1))); self.az = np.degrees(np.arctan2(U[:, 0], U[:, 2]))

    def at(self, s):
        x = (np.asarray(s, float) % self.L) / self.ds; j = np.floor(x).astype(int) % NT; f = (x - np.floor(x))[..., None]
        k = (j + 1) % NT
        u = unit((1 - f) * self.U[j] + f * self.U[k]); T = unit((1 - f) * self.T[j] + f * self.T[k])
        T = unit(T - (T * u).sum(-1, keepdims=True) * u)
        return u, T, np.cross(u, T)

    def min_turn_radius(self, R):
        return R / max(float(np.abs(self.kg).max()), 1e-9)


# ---------------------------------------------------------------- kinematics
class Kin:
    def __init__(self, p, ov):
        self.p = p; self.ov = ov; self.b = bvec(p["b_az"], p["b_el"]); self.a1 = p["a1"] * D2R
        self.e0, self.f0 = perp(self.b); self.cmin = math.sin(SING * D2R)

    def cands(self, HGi):
        """roots on the design branch, transversal, residual < 0.5 deg: list of dict(s, u, t, n (HG frame), cphi, q)"""
        ov = self.ov; b_h = HGi.T @ self.b                               # b in the humerus frame
        f = np.arccos(np.clip(ov.U @ b_h, -1, 1)) - self.a1
        g = np.roll(f, -1); idx = np.nonzero(((f <= 0) & (g > 0)) | ((f > 0) & (g <= 0)))[0]
        out = []; sa = math.sin(self.a1)
        for j in idx:
            s = (j + f[j] / (f[j] - g[j])) * ov.ds
            for _ in range(2):
                u, T, _n = ov.at(s); c = min(1.0, max(-1.0, float(u @ b_h))); fs = math.acos(c) - self.a1
                dfs = -(T @ b_h) / max(math.sqrt(1 - c * c), 1e-6)
                if abs(dfs) > 1e-6: s = s - fs / dfs / D2R
            u, T, n = ov.at(s); res = abs(math.acos(min(1.0, max(-1.0, float(u @ b_h)))) - self.a1) / D2R
            cphi = float(T @ b_h) / sa
            if (1 if cphi > 0 else -1) != self.p["sigma"]: continue
            if abs(cphi) < self.cmin or res > 0.5: continue
            us = HGi @ u
            q1 = math.atan2(us @ self.f0, us @ self.e0) / D2R
            q2 = math.atan2(n @ b_h, T @ b_h) / D2R
            out.append(dict(s=float(s % ov.L), u=u, t=T, n=n, cphi=cphi, q=np.array([s % ov.L, q1, q2])))
        return out

    def jump(self, a, b):
        return max(abs(wrap(a[0] - b[0], self.ov.L)), abs(wrap(a[1] - b[1])), abs(wrap(a[2] - b[2])))

    def clips(self):
        """dense tracking on every fit-clip frame -> {pose-file index: root dict or reason str}"""
        names = list(_Z["NAMES"]); st = {}
        for nm in CB.FIT:
            ix = np.nonzero(_Z["CID"] == names.index(nm))[0]; ix = ix[np.argsort(_Z["FI"][ix], kind="stable")]
            last = None
            for j in ix:
                c = self.cands(_Z["HG"][j].astype(float))
                if not c: st[int(j)] = "closure"; continue
                if last is None: r = max(c, key=lambda r: abs(r["cphi"]))
                else:
                    r = min(c, key=lambda r: self.jump(r["q"], last))
                    if self.jump(r["q"], last) > FLIP: st[int(j)] = "flip"; continue
                st[int(j)] = r; last = r["q"]
        return st


# ---------------------------------------------------------------- K3 requirement, straps, quantiles (common kit)
def requirement(B, i, D):
    """first radius t in [T0, T1] along unit thorax dirs D (k, 3) with dist >= CLR and >= 0 over [t, t + WIN]; inf if none"""
    k = len(D); t = np.full(k, T0); c = t.copy(); chk = np.zeros(k, bool); res = np.full(k, np.inf); act = np.ones(k, bool)
    for _ in range(90):
        a = np.nonzero(act)[0]
        if not len(a): break
        x = np.where(chk[a], c[a], t[a]); d = B.dist(i, D[a] * x[:, None])
        s = ~chk[a]
        sa = a[s]; ds_ = d[s]; good = ds_ >= CLR
        chk[sa[good]] = True; c[sa[good]] = t[sa[good]] + np.maximum(ds_[good], 0.5)
        t[sa[~good]] += np.maximum(CLR - ds_[~good], 0.5)
        ca = a[~s]; dc = d[~s]; bad = dc < 0
        chk[ca[bad]] = False; t[ca[bad]] = c[ca[bad]] + CLR - dc[bad]
        c[ca[~bad]] += np.maximum(dc[~bad], 0.5)
        done = chk & (c >= t + WIN) & act; res[done] = t[done]; act &= ~done
        fail = act & (t > T1); act &= ~fail
    return res


def lip(req, x, hubs):
    """strap underside along x (n,) mm: >= req (n, m), slope <= RAMP, = hub level inside each hub zone"""
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


def disc_local(rad=HUB_R, step=2.5):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rad ** 2
    return X[k], Y[k]


def frame_dirs(c, e1, e2, x_mm, y_mm, r=R_REF):
    """directions of local tangent-plane offsets (x along e1, y along e2, mm at radius r) about the unit dir c"""
    return unit(c[None] + (np.asarray(x_mm)[:, None] * e1[None] + np.asarray(y_mm)[:, None] * e2[None]) / r)


def collide(A, Bp, gap=GAP):
    """K6: parts given as (dirs (k, 3), lo (k,), hi (k,)); True if a lateral neighbour pair's radial intervals are < gap apart"""
    Ua, la, ha = A; Ub, lb, hb = Bp
    if not len(Ua) or not len(Ub): return False
    th = (SP + gap) / max(30.0, min(float(la.min()), float(lb.min())))
    ca, cb = unit(Ua.mean(0)), unit(Ub.mean(0))
    ra = float(np.arccos(np.clip(Ua @ ca, -1, 1)).max()); rb = float(np.arccos(np.clip(Ub @ cb, -1, 1)).max())
    if math.acos(min(1.0, max(-1.0, float(ca @ cb)))) > ra + rb + th: return False
    tr = cKDTree(Ua); nb = tr.query_ball_point(Ub, th)
    for j, lst in enumerate(nb):
        if not lst: continue
        l = np.asarray(lst); g = np.maximum(la[l] - hb[j], lb[j] - ha[l])
        if (g < gap).any(): return True
    return False


# ---------------------------------------------------------------- design
class Ctx:
    """per-bench caches shared across configurations (kinematics per kinematic key, requirements per part key)"""
    def __init__(self, B):
        self.B = B; self.HG = _Z["HG"][B.idx].astype(float); self.RS = _Z["RS"][B.idx].astype(float)
        self.M = np.einsum("pij,pjk->pik", self.RS, self.HG); self.kin = {}; self.req = {}

    def reqc(self, key, i, D):
        k = (key, i)
        if k not in self.req:
            if len(self.req) > 40000: self.req.clear()
            self.req[k] = requirement(self.B, i, D)
        return self.req[k]


class Design:
    def __init__(self, p, ctx):
        self.p = p = dict(PARAMS, **p); self.ctx = ctx; B = ctx.B; self.n = len(B.idx)
        kk = json.dumps({k: p[k] for k in KIN_KEYS}, sort_keys=True)
        if kk not in ctx.kin:
            ov = Oval(p); kin = Kin(p, ov); st = kin.clips(); roots = []; why = []
            for i in range(self.n):
                if B.kind[i] == "clip":
                    r = st.get(int(B.idx[i]), "missing")
                    roots.append(r if isinstance(r, dict) else None); why.append("" if isinstance(r, dict) else r)
                else:
                    c = kin.cands(ctx.HG[i])
                    roots.append(max(c, key=lambda r: abs(r["cphi"])) if c else None); why.append("" if c else "closure")
            mult = np.mean([len(kin.cands(ctx.HG[i])) > 1 for i in range(self.n) if B.kind[i] == "ws"])
            if len(ctx.kin) > 6: ctx.kin.clear()
            ctx.kin[kk] = (ov, kin, roots, why, float(mult))
        self.ov, self.kin, self.roots, self.why, self.mult = ctx.kin[kk]
        self.valid = np.array([r is not None for r in self.roots])
        self.okey = json.dumps({k: p[k] for k in OVAL_KEYS}, sort_keys=True); self.bkey = (p["b_az"], p["b_el"])
        self._samples(); self._fit()

    # ---- samples (unit directions in each part's own frame) ------------------------------------------------------
    def _samples(self):
        p = self.p; ov = self.ov
        na = max(8, int(math.ceil(ov.L * D2R * R_REF / SP))); s = np.linspace(0, ov.L, na, endpoint=False)
        u, T, n = ov.at(s); cs = np.arange(-TR_W / 2, TR_W / 2 + 1e-6, SP)
        self.tr_dirs = unit(u[:, None, :] + cs[None, :, None] * n[:, None, :] / R_REF).reshape(-1, 3)   # HG frame
        self.tr_len = ov.L * D2R                                          # rad (x R_O = mm)
        # neck: from the oval point nearest the bar start to the bar start (HG frame), starting just outside the track
        bd = unit(BAR0); j = int(np.argmax(ov.U @ bd)); u0 = ov.U[j]
        ang = math.acos(min(1.0, float(u0 @ bd))); e = unit(bd - (bd @ u0) * u0); nn = np.cross(u0, e)
        s0 = (TR_W / 2 + GAP) / R_REF
        if ang - s0 > SP / R_REF:
            ns = max(2, int(math.ceil((ang - s0) * R_REF / SP)) + 1); ss = np.linspace(s0, ang, ns)
        else:
            ss = np.array([s0, s0 + SP / R_REF])
        self.nk_x = ss * R_REF; cn = np.arange(-NK_W / 2 + 1, NK_W / 2 - 1 + 1e-6, SP)
        D = np.cos(ss)[:, None] * u0 + np.sin(ss)[:, None] * e
        self.nk_dirs3 = unit(D[:, None, :] + cn[None, :, None] * nn[None, None, :] / R_REF)
        self.nk_dirs = self.nk_dirs3.reshape(-1, 3); self.nk_shape = self.nk_dirs3.shape[:2]
        # carriage footprint and J2 disc, local (along, across) mm
        ga = np.arange(-CAR_L / 2, CAR_L / 2 + 1e-6, SP); gc = np.arange(-CAR_W / 2, CAR_W / 2 + 1e-6, SP)
        X, Y = np.meshgrid(ga, gc, indexing="ij"); self.car_xy = (X.ravel(), Y.ravel())
        self.car_wing = np.abs(Y.ravel()) > TR_W / 2 + 1e-6
        dx, dy = disc_local(); self.j2_xy = (dx, dy)
        self.j2_out = (np.abs(dx) > CAR_L / 2 + 1e-6) | (np.abs(dy) > CAR_W / 2 + 1e-6)
        self.j1_xy = disc_local()
        e1, e2 = perp(np.asarray(self.kin.b)); self.j1_dirs = frame_dirs(self.kin.b, e1, e2, *self.j1_xy)   # scapula frame
        # link 1 in its own frame (b, e, b x e): sigma along 0..a1, across
        a1 = p["a1"] * D2R; nl = max(3, int(math.ceil(a1 * R_REF / SP)) + 1); sg = np.linspace(0, a1, nl)
        cl = np.linspace(-p["w1"] / 2, p["w1"] / 2, max(2, int(round(p["w1"] / SP)) + 1))
        self.l1_x = sg * R_REF; self.l1_c = cl; self.l1_shape = (nl, len(cl))
        self.l1_loc = np.stack([np.cos(sg)[:, None] * np.ones_like(cl)[None], np.sin(sg)[:, None] * np.ones_like(cl)[None],
                                np.broadcast_to(cl[None] / R_REF, (nl, len(cl)))], -1)            # (nl, nc, 3) in (b, e, n)

    def pose_dirs(self, i):
        """thorax-frame unit dirs of every part in bench pose i (needs a root)"""
        r = self.roots[i]; ctx = self.ctx; RS, HG, M = ctx.RS[i], ctx.HG[i], ctx.M[i]
        out = {}
        out["track"] = self.tr_dirs @ M.T
        out["neck"] = self.nk_dirs @ M.T
        out["j1"] = self.j1_dirs @ RS.T
        u, T, n = r["u"], r["t"], r["n"]
        out["car"] = frame_dirs(u, T, n, *self.car_xy) @ M.T
        out["j2"] = frame_dirs(u, T, n, *self.j2_xy) @ M.T
        b = self.kin.b; p2 = HG @ u; e = unit(p2 - (p2 @ b) * b); nb = np.cross(b, e)
        L = unit(self.l1_loc[..., 0:1] * b + self.l1_loc[..., 1:2] * e + self.l1_loc[..., 2:3] * nb)
        out["link1"] = L.reshape(-1, 3) @ RS.T
        return out

    # ---- fit radii -----------------------------------------------------------------------------------------------
    def _fit(self):
        p = self.p; ctx = self.ctx; q = p["q"]; V = np.nonzero(self.valid)[0]; self.V = V
        if not len(V): self.dead = True; return
        self.dead = False
        need_o, need_j1, nk_req, l1_req, D = [], [], [], [], {}
        for i in V:
            d = self.pose_dirs(i); D[i] = d
            rt = ctx.reqc(("tr", self.okey), i, d["track"]); rc = requirement(ctx.B, i, d["car"])
            need_o.append(max(rt.max(), rc.max()))
            need_j1.append(ctx.reqc(("j1", self.bkey), i, d["j1"]).max())
            nk_req.append(ctx.reqc(("nk", self.okey), i, d["neck"]))
        self.Rlo = float(qtl(np.array(need_o), q)); self.RO = self.Rlo + TR_T
        self.F1 = float(qtl(np.array(need_j1), q)); self.F2 = self.RO + CAR_T - TR_T
        nkq = qtl(np.array(nk_req), q).reshape(self.nk_shape)
        self.nk_prof, _ = lip(nkq, self.nk_x, [])
        # link 1: skin requirement, lifted over the oval / neck (1 mm clearance) where they pass under it
        th = (SP + GAP) / max(30.0, self.Rlo)
        nk_hi = (self.nk_prof + NK_T).reshape(-1)
        for i in V:
            d = D[i]; rq = requirement(ctx.B, i, d["link1"])
            obs = np.concatenate([d["track"], d["neck"]]); hi = np.r_[np.full(len(d["track"]), self.RO), nk_hi]
            nb = cKDTree(obs).query_ball_point(d["link1"], th)
            lift = np.array([hi[l].max() + GAP + 0.01 if l else 0.0 for l in nb])
            l1_req.append(np.maximum(rq, lift))
        lq = qtl(np.array(l1_req), q).reshape(self.l1_shape)
        x_end = self.l1_x[-1]
        self.l1_prof, self.hub_lv = lip(lq, self.l1_x, [(0.0, self.F1 + STACK), (x_end, self.F2 + STACK)])
        self.F1 = max(self.F1, self.hub_lv[0] - STACK)                     # link end sits on the hub (raise J1 if the link had to)
        self.D = D

    # ---- pose -> metal -------------------------------------------------------------------------------------------
    def parts(self, i):
        """per part: (dirs, lo, hi) volumes and skin-facing points"""
        d = self.D[i] if i in self.D else self.pose_dirs(i)
        RO, Rlo, F1, F2 = self.RO, self.Rlo, self.F1, self.F2
        f = lambda U, lo, hi: (U, np.broadcast_to(np.asarray(lo, float), (len(U),)).copy(), np.broadcast_to(np.asarray(hi, float), (len(U),)).copy())
        vol = dict(track=f(d["track"], Rlo, RO), car=f(d["car"], Rlo, F2), j2=f(d["j2"], F2, F2 + CROWN),
                   j1=f(d["j1"], F1, F1 + CROWN), link1=f(d["link1"], self.l1_prof.reshape(-1), self.l1_prof.reshape(-1) + L1_T),
                   neck=f(d["neck"], self.nk_prof.reshape(-1), self.nk_prof.reshape(-1) + NK_T))
        face = dict(track=d["track"] * Rlo, car=d["car"][self.car_wing] * Rlo, j2=d["j2"][self.j2_out] * F2, j1=d["j1"] * F1,
                    link1=d["link1"] * self.l1_prof.reshape(-1, 1), neck=d["neck"] * self.nk_prof.reshape(-1, 1))
        return vol, face

    PAIRS = [("j1", "track"), ("j1", "car"), ("j1", "j2"), ("j1", "neck"), ("link1", "track"), ("link1", "neck"),
             ("car", "neck"), ("j2", "neck")]

    def metal(self, i):
        """(points (k, 3) or None, reason)"""
        if self.dead or not self.valid[i]: return None, self.why[i] or "closure"
        if max(self.RO, self.F1 + CROWN, float(self.l1_prof.max())) > 200: return None, "no radius"
        vol, face = self.parts(i)
        for a, b in self.PAIRS:
            if a == "link1" and b == "track":                              # exempt the J2 end (joint partners within 12 mm)
                U, lo, hi = vol["link1"]; xe = np.repeat(self.l1_x, self.l1_shape[1]); k = xe < self.l1_x[-1] - (HUB_R + 2)
                if collide((U[k], lo[k], hi[k]), vol["track"]): return None, "interference link1/track"
                continue
            if collide(vol[a], vol[b]): return None, f"interference {a}/{b}"
        return np.concatenate(list(face.values())), ""

    def member_faces(self, i):
        return self.parts(i)[1]

    def mass(self):
        p = self.p; m = {}
        m["track"] = TR_W * TR_T * self.tr_len * (self.RO - TR_T / 2) * TI
        m["carriage"] = CAR_L * CAR_W * CAR_T * 0.5 * TI                  # bogie block, ~50 % solid
        al = p["a1"] * D2R * (float(self.l1_prof.mean()) + L1_T / 2)
        m["link1"] = p["w1"] * L1_T * al * TI; m["link1_5.5"] = p["w1"] * 5.5 * al * TI
        m["neck"] = NK_W * NK_T * (self.nk_x[-1] - self.nk_x[0] + TR_W / 2) * float(self.nk_prof.mean()) / R_REF * TI
        return {k: round(v, 1) for k, v in m.items()}


# ---------------------------------------------------------------- run on the bench
def run(p, ctx, members=False):
    t = time.time(); D = Design(p, ctx); B = ctx.B; B.reset(); why = {}; mem = {}
    taken_clip = []
    for i in range(len(B.idx)):
        P, w = D.metal(i)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, P)
        if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        elif B.kind[i] == "clip": taken_clip.append(i)
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1)
    if not D.dead:
        r["shape"] = dict(R_O=round(D.RO, 1), F1=round(D.F1, 1), F2=round(D.F2, 1), l1=[round(float(D.l1_prof.min()), 1), round(float(D.l1_prof.max()), 1)],
                          neck=[round(float(D.nk_prof.min()), 1), round(float(D.nk_prof.max()), 1)], oval_len_mm=round(D.tr_len * D.RO, 0),
                          turn_r_mm=round(D.ov.min_turn_radius(D.RO), 1), kin_valid=round(float(D.valid.mean()), 3), multi_root_ws=round(D.mult, 3),
                          mass_g=D.mass())
        if members and taken_clip:
            acc = {}
            for i in taken_clip:
                for k, P in D.member_faces(i).items():
                    if not len(P): continue
                    dd = B.dist(i, P); a = acc.setdefault(k, [0, 0, 0, []]); a[0] += len(dd); a[1] += int(((dd >= 2) & (dd <= 14)).sum())
                    a[2] += int(((dd >= 2) & (dd <= 10)).sum()); a[3].append(float(np.median(dd)))
            r["members"] = {k: dict(n=v[0], share=round(v[0] / sum(x[0] for x in acc.values()), 3), ib14=round(v[1] / v[0], 3),
                                    ib10=round(v[2] / v[0], 3), med_mm=round(float(np.median(v[3])), 1)) for k, v in acc.items()}
            # joint ranges used
            q = np.array([D.roots[i]["q"] for i in range(len(B.idx)) if D.roots[i] is not None])
            r["s_used_deg"] = [round(float(q[:, 0].min()), 1), round(float(q[:, 0].max()), 1), round(D.ov.L, 1)]
    return r, D


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = (id(B), json.dumps(prm, sort_keys=True))
    if key not in _cache:
        _cache.clear(); _cache[key] = Design(prm, Ctx(B))
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def sweep(configs, ctx, out=SWEEP_OUT, tag="", log=print):
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, ctx)
        except Exception as e:
            import traceback; traceback.print_exc(); log(f"ERR {p} {e}"); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r.get("shape"), mode=r["mode"], stage=tag)
        rows.append(row)
        if out:
            json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        log(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
            f"contact {r['contact']:.3f} | {r['why']} | {r.get('shape')} | {r['secs']} s | " + " ".join(f"{k}={p[k]}" for k in PARAMS))
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        B = CB.Bench(n_clip=nc, n_ws=nw); ctx = Ctx(B)
        r, D = run(dict(PARAMS), ctx, members=True)
        print(json.dumps({k: v for k, v in r.items()}, indent=1, default=str))
        for i in range(len(B.idx)):
            P, w = D.metal(i)
            dd = B.dist(i, P) if P is not None else None
            print(i, B.kind[i], {k: round(v) for k, v in B.poses[i].items()}, w or "ok",
                  "" if dd is None else f"min {dd.min():.1f} med {np.median(dd):.1f} ib14 {np.mean((dd >= 2) & (dd <= 14)):.2f}",
                  "" if D.roots[i] is None else np.round(D.roots[i]["q"], 1))
