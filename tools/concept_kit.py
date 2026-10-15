"""Shared modelling kit for the morphology swarm (docs/concepts/KIT.md): the COMMON KIT K0-K7 of the catalogue specs,
vectorised over all bench poses, so a morphology model is members + a closure + params (~100-150 lines).

    import sys; sys.path.insert(0, "tools"); import concept_kit as K
    B = K.bench(60, 160); F = K.frames(B)               # F.RS, F.RHG (band humerus frame), F.RH (body_pose humerus)
    chain = my_build(B, F, params)                       # -> K.Chain(members=[K.Member...], ok=(P,), q=(P, nq) deg, joints)
    rep = K.evaluate(B, my_build, params)                # bench report + per-member in-band, Ti mass, closure share
    K.sweep(B, my_build, configs, "docs/concepts/sweeps/<id>.json")

Conventions are those of tools/concept_baseline.py (the champion 3R), so a kit model and the baseline are measured
identically: strap samples every 2 mm along / across at r_ref = 70 mm, cap hubs every 2.5 mm, profile = quantile q over
the fit poses of the per-sample skin requirement (+ 2 mm clearance), contact decided by B.dist on every metal sample.
"""
import datetime, json, math, os, sys
from dataclasses import dataclass, field
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

D2R = math.pi / 180
TI = 4.43e-3                                                 # g / mm3
HUB_R, STACK, CROWN = 10.0, 3.15, 12.25                      # O20 hub v5 (docs/HARDWARE.md): lower member [F, F+3], upper at F+3.15, crown F+12.25


def bench(n_clip=60, n_ws=160): return CB.Bench(n_clip, n_ws)
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


# ---- K0 frames and directions --------------------------------------------------------------------------------------
def bvec(az, el):
    """scapula-frame direction (deg): az 0 posterior, 90 lateral, 180 anterior, -90 medial (= band_impl.bvec)"""
    az, el = np.asarray(az, float) * D2R, np.asarray(el, float) * D2R
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def wdir(d, a):
    """humerus (band HG) frame direction (deg): d from the down-the-arm axis; a 0 lateral, +90 anterior (= band_impl.w_dir)"""
    d, a = np.asarray(d, float) * D2R, np.asarray(a, float) * D2R
    return np.stack([np.sin(d) * np.sin(a), -np.cos(d), np.sin(d) * np.cos(a)], -1)


@dataclass
class Frames:
    RS: np.ndarray        # (P, 3, 3) scapula: a scapula-frame direction u is RS @ u (= B.frames(i)['S'][0])
    RHG: np.ndarray       # (P, 3, 3) humerus in the BAND frame (RS @ HG): wdir / band W live here
    RH: np.ndarray        # (P, 3, 3) humerus in the body_pose frame (= B.frames(i)['H'][0] = RHG @ C_HG_H): BOTTOM's bar lives here
    clip: np.ndarray      # (P,) bool clip frame
    ws: np.ndarray        # (P,) bool workspace pose

    def S(self, u): return np.einsum("pij,...j->p...i", self.RS, np.asarray(u, float))
    def HG(self, u): return np.einsum("pij,...j->p...i", self.RHG, np.asarray(u, float))
    def H(self, u): return np.einsum("pij,...j->p...i", self.RH, np.asarray(u, float))


def frames(B):
    Z = CB._poses_all(); RS = Z["RS"][B.idx].astype(float); RHG = RS @ Z["HG"][B.idx].astype(float)
    f0 = B.frames(0); C = RHG[0].T @ f0["H"][0]                # constant ~12 deg between the two humerus frames
    k = np.array(B.kind)
    return Frames(RS=RS, RHG=RHG, RH=RHG @ C, clip=k == "clip", ws=k == "ws")


def axis_angle(k, ref, v):
    """signed angle (deg) about unit axes k (..., 3) from ref to v, both projected on the plane normal to k"""
    k, ref, v = np.broadcast_arrays(*(np.asarray(x, float) for x in (k, ref, v)))
    r = ref - (ref * k).sum(-1, keepdims=True) * k; w = v - (v * k).sum(-1, keepdims=True) * k
    return np.degrees(np.arctan2((np.cross(r, w) * k).sum(-1), (r * w).sum(-1)))


# ---- K1 two-circle closure -----------------------------------------------------------------------------------------
def closure(b, w, a1, a2, sigma, margin_deg=5.0):
    """the axis p with angle(p, b) = a1 and angle(p, w) = a2 (deg), on branch sigma = +-1 (sign of p . (b x w)).
    b, w: (P, 3) unit. Returns p (P, 3), ok (P,) (closes and margin >= margin_deg), margin (P,) deg."""
    b, w = unit(b), unit(w); c = np.clip((b * w).sum(-1), -1, 1); n = unit(np.cross(b, w)); A1, A2 = a1 * D2R, a2 * D2R
    den = 1 - c ** 2 + 1e-12; A = (math.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * math.cos(A1)) / den
    p0 = A[..., None] * b + Bq[..., None] * w; h2 = 1 - (p0 * p0).sum(-1)
    p = p0 + sigma * np.sqrt(np.clip(h2, 0, None))[..., None] * n
    th = np.degrees(np.arccos(c)); margin = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    return p, (h2 > 0) & (margin >= margin_deg), margin


def closure_residual(b, w, p, a1, a2):
    """max |angle error| (deg) of a closure: the honesty rule wants < 0.5 deg"""
    e1 = np.degrees(np.arccos(np.clip((unit(p) * unit(b)).sum(-1), -1, 1))) - a1
    e2 = np.degrees(np.arccos(np.clip((unit(p) * unit(w)).sum(-1), -1, 1))) - a2
    return np.maximum(np.abs(e1), np.abs(e2))


# ---- K2 continuity -------------------------------------------------------------------------------------------------
def continuity(B, q, ok, jump_deg=25.0, period=360.0):
    """walk B.clip_order(): a clip frame whose joint values q (P, nq) deg jump > jump_deg from the previous TAKEN frame
    is a branch flip -> not taken. Returns ok2 (P,) and the number of flips. period=None for slides (mm)."""
    ok2 = np.asarray(ok, bool).copy(); q = np.asarray(q, float).reshape(len(ok2), -1); flips = 0
    for _, js in B.clip_order().items():
        prev = None
        for j in js:
            if not ok2[j]: continue
            if prev is not None:
                d = q[j] - q[prev]
                if period: d = (d + period / 2) % period - period / 2
                if np.abs(d).max() > jump_deg: ok2[j] = False; flips += 1; continue
            prev = j
    return ok2, flips


def _slerp_frames(F, j0, j1, step_deg=2.0, max_sub=90):
    """frames interpolated from pose j0 to pose j1 (both ends included): RS, RHG, RH slerped together"""
    from scipy.spatial.transform import Rotation as R, Slerp
    ang = max(np.degrees(R.from_matrix(X[j0].T @ X[j1]).magnitude()) for X in (F.RS, F.RHG))
    n = int(min(max_sub, max(2, math.ceil(ang / step_deg) + 1))); s = np.linspace(0, 1, n)
    out = [Slerp([0, 1], R.from_matrix(np.stack([X[j0], X[j1]])))(s).as_matrix() for X in (F.RS, F.RHG, F.RH)]
    return Frames(RS=out[0], RHG=out[1], RH=out[2], clip=np.ones(n, bool), ws=np.zeros(n, bool))


def continuity_dense(B, F, build, params, ok, jump_deg=25.0, step_deg=2.0):
    """K2 along the real motion: between consecutive TAKEN clip frames the pose is interpolated (scapula and humerus
    slerped, <= step_deg per step) and the chain rebuilt; the frame is followed only if the chain closes at every step
    and no joint value (Chain.q) and no joint AXIS (Chain.joints) moves > jump_deg between steps (a branch flip, or a
    pass through a singularity; the axis test does not rely on the model's own q). build may only use F for its
    geometry (it is called with these interpolated frames). Returns ok2 (P,), flips."""
    ok2 = np.asarray(ok, bool).copy(); flips = 0
    for _, js in B.clip_order().items():
        prev = None
        for j in js:
            if not ok2[j]: continue
            if prev is not None:
                Fs = _slerp_frames(F, prev, j, step_deg); ch = build(B, Fs, params); n = len(Fs.RS); jmp = 0.0
                if ch.q is not None:
                    d = np.diff(np.asarray(ch.q, float).reshape(n, -1), axis=0)
                    if ch.q_period: d = (d + ch.q_period / 2) % ch.q_period - ch.q_period / 2
                    jmp = np.abs(d).max(initial=0)
                for ax in ch.joints.values():
                    ax = unit(np.asarray(ax, float).reshape(n, 3))
                    jmp = max(jmp, float(np.degrees(np.arccos(np.clip((ax[1:] * ax[:-1]).sum(-1), -1, 1))).max(initial=0)))
                if not (np.all(ch.ok) and jmp <= jump_deg): ok2[j] = False; flips += 1; continue
            prev = j
    return ok2, flips


# ---- distance on many poses at once --------------------------------------------------------------------------------
def dist_many(B, I, P):
    """signed distance of points P (N, 3) each in its own pose I (N,): one vectorised gather on the grid cache
    (same trilinear formula as Bench.dist); points outside the box and the no-cache case go to B.dist per pose"""
    I = np.asarray(I, np.int64); P = np.asarray(P, float); out = np.empty(len(P))
    if not len(P): return out
    if B.grid is None:
        for i in np.unique(I): m = I == i; out[m] = B.dist(int(i), P[m])
        return out
    n = B.grid.shape[1]; g = (P + CB.HALF) / CB.H_GRID
    ins = np.all((g >= 0) & (g <= n - 1 - 1e-9), axis=1)
    if ins.any():
        gi = g[ins]; i0 = np.floor(gi).astype(np.int64); f = gi - i0; fx, fy, fz = f.T
        G = B.grid.reshape(-1); base = ((I[ins] * n + i0[:, 0]) * n + i0[:, 1]) * n + i0[:, 2]
        v = 0.0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    wgt = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * (fz if dz else 1 - fz)
                    v = v + G[base + (dx * n + dy) * n + dz].astype(np.float32) * wgt
        out[ins] = v * CB.Q
    if (~ins).any():
        J = np.nonzero(~ins)[0]
        for i in np.unique(I[J]): m = J[I[J] == i]; out[m] = B.dist(int(i), P[m])
    return out


# ---- K3 skin requirement along rays --------------------------------------------------------------------------------
def requirement(B, I, D, t0=15.0, t1=220.0, clr=2.0, win=15.0, mode="march", O=None):
    """per ray (pose I (N,), unit dir D (N, 3), origin O (N, 3), default GH): the distance t along the ray (x = O + t D)
    metal must sit at (O = the in-plane offsets of a flat plate's samples, D = its normal: t is the plate height).
    mode 'march' (K3): the first t on the 1 mm lattice t0..t1 with dist(t) >= clr and dist >= 0 on t..t+win (inf if
    none); exact w.r.t. a brute 1 mm march, steps skip lattice points the 1-Lipschitz distance rules out.
    mode 'outer' (tools/concept_baseline.skin_radius + clr): sphere-trace inward from 260 mm to the OUTERMOST skin."""
    I = np.asarray(I, np.int64); D = np.asarray(D, float); N = len(D)
    O = np.zeros_like(D) if O is None else np.asarray(O, float)
    if mode == "outer":
        r = np.full(N, 260.0); act = np.ones(N, bool); hit = np.zeros(N, bool)
        for _ in range(60):
            a = np.nonzero(act)[0]
            if not len(a): break
            d = dist_many(B, I[a], O[a] + D[a] * r[a, None]); done = d < 0.3
            hit[a[done]] = True; act[a[done]] = False; r[a[~done]] -= np.maximum(d[~done], 0.5)
            act &= ~(r < 15)
        return np.where(hit, r, 0.0) + clr
    t = np.full(N, float(t0)); c = t.copy(); chk = np.zeros(N, bool); res = np.full(N, np.inf); act = np.ones(N, bool)
    for _ in range(400):
        a = np.nonzero(act)[0]
        if not len(a): break
        x = np.where(chk[a], c[a], t[a]); d = dist_many(B, I[a], O[a] + D[a] * x[:, None]); s = ~chk[a]
        sa, ds = a[s], d[s]; good = ds >= clr                                   # search: candidate t
        chk[sa[good]] = True; c[sa[good]] = t[sa[good]] + np.maximum(1.0, np.floor(ds[good]))
        t[sa[~good]] += np.maximum(1.0, np.ceil(clr - ds[~good] - 1e-9))
        ca, dc = a[~s], d[~s]; bad = dc < 0                                     # check: window point c
        chk[ca[bad]] = False; t[ca[bad]] = c[ca[bad]] + np.maximum(1.0, np.ceil(clr - dc[bad] - 1e-9))
        c[ca[~bad]] += np.maximum(1.0, np.floor(dc[~bad]))
        done = act & chk & (c > t + win); res[done] = t[done]; act &= ~done
        act &= ~(t > t1)
    return res


def quantile(R, q):
    """per-sample quantile over the fit poses (axis 0); inf (no clearance found) counts as 400 mm"""
    R = np.where(np.isfinite(R), R, 400.0)
    return R.max(0) if q >= 1 else np.quantile(R, q, axis=0)


# ---- sampling (the baseline's density) -----------------------------------------------------------------------------
def strap_dirs(u, v, ang=None, width=8.0, step=2.0, r_ref=70.0):
    """a strap on the great circle u -> v (P, 3), arc ang rad (default: the u-v angle of each pose, the sample count
    from its median, so the layout is pose-local): (P, ns, nc, 3), 2 mm along/across"""
    u, v = unit(u), unit(v)
    if ang is None: ang = np.arccos(np.clip((u * v).sum(-1), -1, 1))
    ang = np.broadcast_to(np.asarray(ang, float), (len(u),))
    ns = max(3, int(float(np.median(ang)) * r_ref / step) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); th = s[None, :] * ang[:, None]
    Dd = np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None]
    cs = np.arange(-width / 2, width / 2 + 1e-6, step) / r_ref
    return unit(Dd[:, :, None, :] * np.cos(cs)[None, None, :, None] + nrm[:, None, None, :] * np.sin(cs)[None, None, :, None])


def cap_dirs(k, rad=HUB_R, step=2.5, r_ref=70.0):
    """directions under a hub disc centred on axis k (P, 3): (P, m, 3) (baseline hubs: a spherical cap at one radius)"""
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2
    X, Y = X[keep] / r_ref, Y[keep] / r_ref; k = unit(k)
    a = unit(np.cross(k, np.array([0.0, 0.0, 1.0]) + 1e-3)); b = np.cross(k, a)
    return unit(k[:, None] + X[None, :, None] * a[:, None] + Y[None, :, None] * b[:, None])


def disc_xy(rad=HUB_R, step=2.0):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2 + 1e-9
    return np.stack([X[keep], Y[keep]], -1)


def rect_xy(L, W, step=2.0):
    x = np.linspace(-L / 2, L / 2, int(round(L / step)) + 1); y = np.linspace(-W / 2, W / 2, int(round(W / step)) + 1)
    X, Y = np.meshgrid(x, y, indexing="ij"); return np.stack([X.ravel(), Y.ravel()], -1)


def plane_frame(k, ref=None):
    """two unit vectors (P, 3) spanning the plane normal to k (P, 3); ref fixes the in-plane azimuth"""
    k = unit(k); ref = np.array([0.0, 0.0, 1.0]) + 1e-3 if ref is None else ref
    a = unit(np.cross(k, ref)); return a, np.cross(k, a)


# ---- the data model ------------------------------------------------------------------------------------------------
@dataclass
class Member:
    """one rigid part. Its skin-facing samples are unit directions D (P, m, 3) in the thorax frame per pose; kind:
      'free'  per-sample underside rho_j = quantile_q(requirement) (a rigid skin-fitted underside, K3);
      'cap'   one radius for all samples = max_j rho_j (the baseline's hub discs);
      'flat'  a flat plate normal to K (P, 3) at height h_F = max_j quantile_q(requirement_j) (K4), the requirement of
              sample j marched along K from its in-plane offset x A + y Bv (xy (m, 2), A, Bv (P, 3)): the samples are
              h_F K + x A + y Bv (D is only a nominal layout at h0, used by `over`).
    off: level added to the fitted underside (hub stack); grid (ns, nc) + climb_deg: strap climb limit along axis 0
    (step_mm apart); ramps: [(mask (m,), other member name, dz)]: final underside >= the other's level + dz there;
    over: [(other member name, gap)]: wherever it passes over that member (in any fit pose), underside >= the
    other's top + gap (the K6 clearance by construction; the other must not itself have `over`).
    joints: names of the joints it carries (K6 partners are exempt within HUB_R + 2 mm of a shared joint)."""
    name: str
    D: np.ndarray
    kind: str = "free"
    t: float = 3.0
    width: float = 8.0
    off: float = 0.0
    joints: tuple = ()
    grid: tuple = None
    climb_deg: float = None
    step_mm: float = 2.0
    ramps: list = field(default_factory=list)
    over: list = field(default_factory=list)   # [(other member name, gap mm)]: pass over it (K6 by construction)
    q: float = None
    K: np.ndarray = None
    A: np.ndarray = None
    Bv: np.ndarray = None
    xy: np.ndarray = None
    cell: float = 4.0         # mm2 per sample at r_ref (straps 2x2, caps 2.5x2.5)
    r_ref: float = 70.0
    hw: float = 1.0           # half extent of one sample (K6)
    strap: bool = False       # report mass at 5.5 mm too (K5)


@dataclass
class Chain:
    members: list
    ok: np.ndarray                          # (P,) closes (K1 margin, joint and slide ranges) - before continuity
    q: np.ndarray = None                    # (P, nq) joint values (deg) for K2; None = no continuity check
    joints: dict = field(default_factory=dict)   # name -> axis (P, 3) thorax
    q_period: float = 360.0
    info: dict = field(default_factory=dict)
    hubless: tuple = ()                     # joints declared WITHOUT an O20 hub (a rail carriage, a ring bearing...): the
                                            # audit then does not ask for a hub there, and the report lists them


def _levels(B, chain, fit, q, mode):
    """fit every member's underside (one batched requirement call over all members and fit poses)"""
    Pi = np.nonzero(fit)[0]; segs = []; rays = []; orig = []
    for m in chain.members:
        if m.kind == "flat":      # K4: march each plate sample along the plate normal from its true in-plane offset
            n = len(m.xy); Dm = np.broadcast_to(m.K[Pi][:, None, :], (len(Pi), n, 3))
            Om = m.xy[None, :, :1] * m.A[Pi][:, None, :] + m.xy[None, :, 1:] * m.Bv[Pi][:, None, :]
        else:
            Dm = m.D[Pi]; Om = np.zeros_like(Dm)
        segs.append(Dm.shape[1]); rays.append(Dm.reshape(-1, 3)); orig.append(Om.reshape(-1, 3))
    I = np.concatenate([np.repeat(Pi, s) for s in segs]) if len(Pi) else np.zeros(0, int)
    cat = lambda L: np.concatenate(L) if L else np.zeros((0, 3))
    R = requirement(B, I, cat(rays), mode=mode, O=cat(orig))
    out = {}; o = 0
    for m, s in zip(chain.members, segs):
        Rm = R[o:o + len(Pi) * s].reshape(len(Pi), s); o += len(Pi) * s; qq = m.q if m.q is not None else q
        out[m.name] = quantile(Rm, qq) if len(Pi) else np.full(s, 400.0)
    return out


def fit_profiles(B, chain, fit, q=1.0, mode="march"):
    """underside radius per sample (final, with offsets, flat levels, climb limit and ramps) -> {name: rho (m,)}"""
    raw = _levels(B, chain, fit, q, mode); prof = {}; level = {}
    order = sorted(chain.members, key=lambda m: (len(m.over) > 0, len(m.ramps) > 0))
    for m in order:
        r = raw[m.name].copy()
        if m.kind in ("cap", "flat"): r[:] = r.max()
        r = r + m.off
        for mask, other, dz in m.ramps: r[mask] = np.maximum(r[mask], level[other] + dz)
        if m.over: r = _over(chain, m, r, prof, fit)
        if m.climb_deg and m.grid:                            # K5: |d underside / d s| <= tan(climb) (raises only)
            ns, nc = m.grid; R2 = r.reshape(ns, nc); x = np.arange(ns) * m.step_mm; sl = math.tan(m.climb_deg * D2R)
            R2 = (R2[None, :, :] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1); r = R2.ravel()
        prof[m.name] = r; level[m.name] = float(r.max())
    return prof


def member_points(m, rho):
    """(P, m, 3) metal sample points of member m at its fitted underside rho"""
    if m.kind == "flat":
        return rho[0] * m.K[:, None, :] + m.xy[None, :, :1] * m.A[:, None, :] + m.xy[None, :, 1:] * m.Bv[:, None, :]
    return m.D * rho[None, :, None]


def hub_member(name, axis, joint, t=CROWN, rad=HUB_R, step=2.0, h0=70.0, ref=None):
    """K4: the O20 hub of joint `joint` as a flat disc (radius 10, 2 mm grid) normal to axis (P, 3); its level h_F (the
    lower member's skin face F) is fitted by the K3 march of every disc sample along the axis from its true in-plane
    offset (h0 only lays out the nominal directions D); t = 12.25 (F to the crown)"""
    k = unit(axis); a, b = plane_frame(k, ref); xy = disc_xy(rad, step)
    D = unit(h0 * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    return Member(name, D, kind="flat", t=t, width=2 * rad, joints=(joint,), K=k, A=a, Bv=b, xy=xy, cell=step * step)


def strap_member(name, u, v, joints, ang=None, width=12.0, t=3.0, ramp_to=(), climb_deg=60.0, end_mm=HUB_R + 2.0, **kw):
    """K5: a strap on the great circle u -> v (P, 3) (12 x 3 mm, 2 mm samples), K3 underside, climb <= 60 deg.
    ramp_to: ((hub member name or None, dz), (hub name or None, dz)) for its start / end: the first / last end_mm (at
    r_ref) sit >= that hub's F + dz (dz = STACK when this strap is the upper member of that joint, 0 when the lower)"""
    D = strap_dirs(u, v, ang, width=width); ns, nc = D.shape[1:3]
    n_end = int(math.ceil(end_mm / 2.0)) + 1; s = np.repeat(np.arange(ns), nc); ramps = []
    for (h, dz), m in zip(ramp_to, (s < n_end, s >= ns - n_end)):
        if h: ramps.append((m, h, dz))
    return Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=climb_deg,
                  ramps=ramps, strap=True, **kw)


# ---- K6 collisions -------------------------------------------------------------------------------------------------
def _scale(m, x):
    """how much a member's sample layout (made at r_ref) has grown at radius x (flat parts are laid out in mm: 1)"""
    return np.ones_like(x) if m.kind == "flat" else np.maximum(1.0, x / m.r_ref)


def _near(A, Bm, da, db, xa, xb, joints, shared, P, clear):
    """near mask of two members' samples on poses P: arc distance (angle * A's radius) < hw_a + hw_b + clear, the
    samples within HUB_R + 2 mm of a shared joint axis exempt. Returns (k, near (len(k), m, n)) for the poses k of P
    whose two sample cones can touch at all, or None. Squared chords instead of arccos (error < 0.05 % below 0.1 rad)."""
    ma = np.ones(xa.shape, bool); mb = np.ones(xb.shape, bool); sa, sb = _scale(A, xa), _scale(Bm, xb)   # layouts made at r_ref grow with radius
    for j in shared:
        k = unit(joints[j][P])
        ma &= np.arccos(np.clip(np.einsum("pmd,pd->pm", da, k), -1, 1)) * xa / sa > HUB_R + 2
        mb &= np.arccos(np.clip(np.einsum("pmd,pd->pm", db, k), -1, 1)) * xb / sb > HUB_R + 2
    ha, hb = A.hw * sa, Bm.hw * sb
    ca, cb = unit(da.mean(1)), unit(db.mean(1))                # cone prefilter per pose
    ra = np.arccos(np.clip(np.einsum("pmd,pd->pm", da, ca).min(1), -1, 1)); rb = np.arccos(np.clip(np.einsum("pmd,pd->pm", db, cb).min(1), -1, 1))
    sep = np.arccos(np.clip((ca * cb).sum(-1), -1, 1))
    reach = (ha.max(1) + hb.max(1) + clear) / np.minimum(xa.min(1), xb.min(1))
    k = np.nonzero((sep <= ra + rb + reach + 1e-6) & ma.any(1) & mb.any(1))[0]
    if not len(k): return None
    dot = np.matmul(da[k].astype(np.float32), db[k].astype(np.float32).transpose(0, 2, 1))
    thr = ha[k] + hb[k].max(1)[:, None] + clear                 # (k, m): B's largest sample half extent (conservative)
    cmin = (1.0 - 0.5 * (thr / xa[k]) ** 2).astype(np.float32)  # chord^2 = 2 (1 - dot) < (thr / rho_a)^2
    near = (dot > cmin[:, :, None]) & mb[k][:, None, :]
    near &= ma[k][:, :, None]
    return k, near


def collisions(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    """(P,) bool: any two members collide (arc distance < hw1 + hw2 + clear, and radial intervals [r, r + t] closer
    than `overlap` = 0.5 mm: the spec's K6, so the radial part-part clearance it enforces is 0.5 mm, the lateral 1 mm;
    `over` builds 1 mm); joint partners are exempt within HUB_R + 2 mm of a shared joint axis"""
    hit = np.zeros(len(ok), bool); M = chain.members; Pi = np.nonzero(ok)[0]
    if not len(Pi): return hit
    nr = {m.name: np.linalg.norm(pts[m.name], axis=-1) for m in M}; dr = {m.name: pts[m.name] / nr[m.name][..., None] for m in M}
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            A, Bm = M[a], M[b]; shared = set(A.joints) & set(Bm.joints); ra, rb = nr[A.name], nr[Bm.name]
            if ra[Pi].min() > rb[Pi].max() + Bm.t + overlap or rb[Pi].min() > ra[Pi].max() + A.t + overlap: continue
            for c0 in range(0, len(Pi), chunk):
                P = Pi[c0:c0 + chunk]; xa, xb = ra[P], rb[P]
                res = _near(A, Bm, dr[A.name][P], dr[Bm.name][P], xa, xb, chain.joints, shared, P, clear)
                if res is None: continue
                k, nm = res; xa, xb = xa[k], xb[k]
                ov = (xa[:, :, None] < xb[:, None, :] + Bm.t + overlap) & (xb[:, None, :] < xa[:, :, None] + A.t + overlap)
                hit[P[k]] |= (nm & ov).any((1, 2))
    return hit


def _over(chain, m, r, prof, fit, clear=1.0, chunk=24):
    """K6 by construction: raise member m's underside r (m,) to >= other top + gap wherever it passes over the members
    listed in m.over [(name, gap)] (max over the fit poses: one violated sample would reject the pose; the shared-joint
    zone is left to the hub stack)"""
    Pi = np.nonzero(fit)[0]; O = {o.name: o for o in chain.members}; need = np.full((len(Pi), len(r)), -np.inf)
    if not len(Pi): return r
    xa_all = np.broadcast_to(r, (len(m.D), len(r)))
    for name, gap in m.over:
        o = O[name]; po = member_points(o, prof[name]); xo = np.linalg.norm(po, axis=-1); do = po / xo[..., None]
        shared = set(m.joints) & set(o.joints)
        for c0 in range(0, len(Pi), chunk):
            P = Pi[c0:c0 + chunk]
            res = _near(m, o, m.D[P], do[P], xa_all[P], xo[P], chain.joints, shared, P, clear)
            if res is None: continue
            k, nm = res
            top = np.where(nm, (xo[P][k] + o.t + gap)[:, None, :], -np.inf).max(2)
            need[c0 + k] = np.maximum(need[c0 + k], top)
    need = np.where(np.isfinite(need), need, 0.0)
    return np.maximum(r, need.max(0))


# ---- K7 neck to BOTTOM ---------------------------------------------------------------------------------------------
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713])   # BOTTOM's bar, body_pose humerus frame
BAR0_H = 67.5 * WB + 40.0 * DB


def neck_member(F, p_from, name="neck", width=14.0, t=6.0, joints=(), ramps=None):
    """K7: a 14 x 6 strap fixed in the humerus from direction p_from (P, 3) (e.g. J3 axis / arm-end plate) to the start
    of BOTTOM's bar (direction of RH @ BAR0_H, 67.5 mm out along Wb, 40 mm down along Db); K3 underside, K5 climb.
    ramps: like strap_member's ramp_to, e.g. (("hub3", 0.0), (None, 0))"""
    return strap_member(name, p_from, F.H(unit(BAR0_H)), joints, width=width, t=t, ramp_to=ramps or ())


# ---- evaluate / sweep / record -------------------------------------------------------------------------------------
def evaluate(B, model, params, q=None, mode="march", cont=True, collide=True, jump_deg=25.0, verbose=False):
    """model: a module / object with build(B, F, params) -> Chain, or the build function itself. params['q'] (default 1.0)
    is the underside quantile. cont: True = K2 along the interpolated motion (continuity_dense), 'frames' = K2 between
    bench frames only (too strict on the sparse 60-frame bench: flags real fast motion as flips), False = off. Returns the bench report + per-member in-band, Ti mass, closure share and flags."""
    build = model if callable(model) else model.build
    held = set(json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"])
    if held & set(B.clip): raise ValueError("held-out clips in the bench")                       # honesty rule 7
    F = getattr(B, "_kitF", None) or frames(B); B._kitF = F
    ch = build(B, F, params); q = params.get("q", 1.0) if q is None else q
    ok = np.asarray(ch.ok, bool); flips = 0
    if cont and ch.q is None and not ch.joints:
        raise ValueError("cont requested but the Chain has neither q nor joints: K2 cannot be checked (honesty rule 6)")
    if cont == "frames" and ch.q is not None: ok, flips = continuity(B, ch.q, ok, jump_deg, ch.q_period)
    elif cont and cont != "frames": ok, flips = continuity_dense(B, F, build, params, ok, jump_deg)
    prof = fit_profiles(B, ch, ok, q, mode)
    pts = {m.name: member_points(m, prof[m.name]) for m in ch.members}
    hit = collisions(ch, pts, ok) if collide else np.zeros(len(ok), bool)
    take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)              # (n, k, 3)
    d = dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = d[j]
    r = B.report(); o = 0; per = {}; clip = np.array([B.kind[i] == "clip" for i in Pi], bool)
    good = d.min(1) >= 0
    for m in ch.members:
        s = pts[m.name].shape[1]; dm = d[clip & good, o:o + s]; o += s
        per[m.name] = round(float(((dm >= 2) & (dm <= 14)).mean()), 4) if dm.size else 0.0
    mass = mass55 = 0.0
    for m in ch.members:
        rho = np.linalg.norm(pts[m.name][Pi[:1]], axis=-1)[0] if len(Pi) else prof[m.name]
        area = float(m.cell * (((rho / m.r_ref) ** 2).sum() if m.kind != "flat" else rho.size))
        mass += area * m.t * TI; mass55 += area * (5.5 if m.strap else m.t) * TI
    problems, density = audit(B, F, build, params, ch, pts, take if take.any() else ok)
    checks = dict(mode=mode, cont=cont, collide=bool(collide), q=q)
    honest = mode == "march" and cont in (True, "frames") and bool(collide) and not problems
    r.update(inband_member=per, mass_g=round(mass, 1), mass_g_strap55=round(mass55, 1), closure=round(float(np.mean(ch.ok)), 4),
             flips=int(flips), collide=round(float(np.mean(hit[ok])) if ok.any() else 0.0, 4), q=q, kmode=mode, **ch.info)
    r.update(checks=checks, honest=honest, audit=problems, sample_mm=density, hubless=list(ch.hubless))
    if verbose: print(r)
    B._kit_last = dict(chain=ch, prof=prof, pts=pts, take=take, ok=ok, hit=hit)
    return r


def audit(B, F, build, params, ch, pts, sel):
    """honesty audit of a built chain (docs/concepts/KIT.md 'Verification'). Returns (problems [str], sample spacing
    {member: median nearest-neighbour mm}). Raises when a joint has no member centred on it at all (a skipped hub)
    unless it is declared in Chain.hubless. Problems (the report's `honest` turns False): a hub smaller than the O20
    disc (< 75 % of its 314 mm2 covered within 10.5 mm of the axis, or reaching < 9.5 mm), a member sampled sparser
    than 1 pt / 16 mm2 (median spacing > 4 mm at its real radius), a build that is not pose-local (its output on a
    subset of poses differs from the full build: it uses B or all poses, so dense K2 sees different geometry)."""
    problems = []; idx = np.nonzero(sel)[0]; i0 = int(idx[0]) if len(idx) else 0; density = {}
    for m in ch.members:
        X = np.asarray(pts[m.name][i0], float)
        if len(X) > 1:
            d2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1); np.fill_diagonal(d2, np.inf)
            density[m.name] = round(float(np.median(np.sqrt(d2.min(1)))), 2)
            if density[m.name] > 4.0: problems.append(f"{m.name}: sparse sampling ({density[m.name]} mm median spacing > 4 mm)")
    for j, axis in ch.joints.items():
        if j in ch.hubless: continue
        k = unit(np.asarray(axis, float)[i0]); best = None
        for m in ch.members:
            if j not in m.joints: continue
            X = np.asarray(pts[m.name][i0], float); L = X - (X @ k)[:, None] * k; lat = np.linalg.norm(L, axis=1)
            u = unit(X); Lu = u - (u @ k)[:, None] * k                                      # centred: sample directions around k
            if np.linalg.norm(Lu.mean(0)) > 0.25 * np.linalg.norm(Lu, axis=1).max() + 1e-9: continue   # (a link is not)
            cell = np.full(len(X), m.cell, float) if m.kind == "flat" else m.cell * (np.linalg.norm(X, axis=1) / m.r_ref) ** 2
            cov = float(cell[lat <= HUB_R + 0.5].sum() / (math.pi * HUB_R ** 2)); reach = float(lat.max())
            if best is None or cov > best[0]: best = (cov, reach, m.name)
        if best is None:
            raise ValueError(f"joint {j}: no member centred on its axis (an O20 hub, honesty rule 1); declare it in Chain.hubless if it has none")
        if best[0] < 0.75 or best[1] < HUB_R - 0.5:
            problems.append(f"{best[2]}: hub of {j} smaller than O20 (covers {best[0]:.2f} of the disc, reaches {best[1]:.1f} mm)")
    S = idx[np.linspace(0, len(idx) - 1, min(8, len(idx))).round().astype(int)] if len(idx) else idx
    if len(S):                                                                              # pose locality
        sub = Frames(RS=F.RS[S], RHG=F.RHG[S], RH=F.RH[S], clip=F.clip[S], ws=F.ws[S])
        try:
            c2 = build(B, sub, params)
            same = np.array_equal(np.asarray(c2.ok, bool), np.asarray(ch.ok, bool)[S]) and len(c2.members) == len(ch.members)
            same = same and all(np.allclose(np.asarray(c2.joints[j]), np.asarray(ch.joints[j])[S], atol=1e-6) for j in ch.joints)
            same = same and all(np.shape(a.D) == np.shape(b.D[S]) and np.allclose(a.D, b.D[S], atol=1e-6) for a, b in zip(c2.members, ch.members))
        except Exception as e:                                                             # noqa: BLE001
            same = False
        if not same: problems.append("build is not pose-local (uses B or statistics over all poses): dense K2 and the fit are not trustworthy")
    return problems, density


def sweep(B, model, configs, out_json, resume=False, log=print, **kw):
    """evaluate each params dict, writing out_json INCREMENTALLY as a list of {k, t, params, inband14, inband10, reach,
    follow, contact, gap}; returns (best entry, all entries)"""
    rows = json.load(open(out_json)) if resume and os.path.exists(out_json) else []
    best = min(rows, key=lambda e: e["gap"]) if rows else None
    for p in configs:
        r = evaluate(B, model, dict(p), **kw)
        e = dict(k=len(rows), t=now(), params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 closure=r["closure"], mass_g=r["mass_g"], honest=r["honest"], kmode=r["kmode"])
        rows.append(e); tmp = out_json + ".tmp"
        json.dump(rows, open(tmp, "w"), indent=1); os.replace(tmp, out_json)
        if best is None or e["gap"] < best["gap"]: best = e
        if log: log(f"[{e['k']}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} contact {e['contact']}")
    return best, rows


def write_row(id, name, rep, lens="", family="", active_dof=3, passive_dof=0, status="screened", n_configs=1, verdict="",
              note="", doc=None, force=False, **extra):
    """docs/concepts/rows/<id>.json with the fields the dashboard reads (docs/handoff/workflows/screen2.js). Refuses a
    report that is not `honest` (K3 march, K2 and K6 on, a clean audit) unless force=True (the row then says so)."""
    if not rep.get("honest") and not force:
        raise ValueError(f"not an honest report (checks {rep.get('checks')}, audit {rep.get('audit')}): fix it or pass force=True")
    extra = dict(extra, honest=bool(rep.get("honest")), checks=rep.get("checks"), audit=rep.get("audit"), hubless=rep.get("hubless"))
    row = dict(id=id, name=name, lens=lens, family=family, active_dof=active_dof, passive_dof=passive_dof, status=status,
               t_ideated=None, t_screened=now(), **{x: rep[x] for x in ("reach", "follow", "inband14", "inband10", "contact", "gap")},
               v_reach=None, v_follow=None, v_inband14=None, v_inband10=None, v_gap=None, n_configs=n_configs, verdict=verdict,
               note=note, doc=doc or f"docs/concepts/models/{id}.py", **extra)
    p = os.path.join(REPO, "docs", "concepts", "rows", f"{id}.json"); json.dump(row, open(p, "w"), indent=1); return p


def log_event(text, kind="milestone"):
    with open(os.path.join(REPO, "docs", "concepts", "events.jsonl"), "a") as f:
        f.write(json.dumps(dict(time=now(), kind=kind, event=text)) + "\n")
