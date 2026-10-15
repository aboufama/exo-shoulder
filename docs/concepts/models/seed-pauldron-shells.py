"""seed-pauldron-shells: nested sliding spherical shells (a pauldron) + an open C-ring axial bearing on the upper arm
(3 ACTIVE DOF, 1 passive slide).

Topology (scapula handler -> user's upper-arm cuff):
    base shell (on the scapula handler, fixed in the scapula frame S) carrying a spherical GUIDE band G1 (circle about
    u1 through GH, colatitude g1) --J1: shell 1's SLIDER S1 runs on G1--> shell 1 (S1 + a web + a guide band G2 about
    u2, colatitude g2) --J2: shell 2's slider S2 runs on G2--> shell 2 (S2 + a web down the deltoid + the carriage)
    --J3: the carriage runs on an open C-track around the arm (axis = humerus long axis d)--> C-track on the user's
    cuff through a passive slide along the humerus.
Kinematics = the 2R + C-ring of seed-2r-cring (same closure, same singularity margin, same branch rule): J1 and J2 set
the humerus direction d (2-circle closure |u1.u2| = cos a1, u2.d = cos a2), the C-ring takes the axial rotation. The
morphology's own idea is the JOINT REALISATION: instead of O20 x 12.25 mm hubs, each revolute is a large-radius
sphere-on-sphere sliding pair (both members concentric with GH, iglidur liner): the distal shell's SLIDER (inner
member, 2 mm) runs under the proximal shell's GUIDE band (outer member, 2 mm, slotted along its centreline, 1 mm
liner); a stud through the slot carries the distal shell's web ABOVE the guide (1 mm running gap). Joint stack =
2 + 1 + 2 + 1 + 2 = 8 mm, spread over a band instead of piled on a 20 mm disc; the slider cannot lift off (the guide
holds it) nor sink (the stud head on the web holds it).

DOF: J1 (shell 1 about u1) + J2 (shell 2 about u2) + J3 (carriage on the C-ring about d) = 3 active rotations, all
axes through GH; the cuff slide along the humerus is set by the closure with the cuff (passive, not counted; on the
bench rig GH is fixed, so it sits at its nominal position). No undriven spare coordinate: the arm's 3 rotations fix
q1, q2, q3 uniquely on the design branch.

Spec corrections (said in docs/concepts/seed-pauldron-shells.md): "shell i rotates about u_i through GH" needs a
guide that constrains the other two rotations and retains the shell - modelled as the slotted guide + slider + stud
above; the ring is the seed-2r-cring C-track + carriage + passive slide (same sections). Two shell forms:
  * web='sphere' (the spec, armour lames): every shell is ONE sphere about GH, nested 3 mm apart: S1 slider at R,
    base guide G1 at R + 3, shell 1 (web + guide G2) at R + 6, S2 slider at R + 3, shell 2 at R + 9 (then a <= 60 deg
    ramp down to the carriage); R is the smallest radius that clears the skin envelope under every shell + clear.
  * web='skin' (improvement): only the sliding bands are spherical (they must be); each joint gets its own radius
    rho_J (slider underside = skin envelope under it + clear; guide underside rho_J + 3 >= its envelope + clear) and the
    webs between bands follow the skin envelope like the baseline's links (<= 60 deg ramps, >= 1 mm over every band
    they cross: the guide they leave, and the next joint's slider-web path).
Geometry (idealised, every part at its real size; 1 sample / 4 mm2 = 2 mm grid):
  * guide band: width band_w, arc = the slider's travel over the fit poses (cov quantiles) + the slider length; a full
    ring when that exceeds 360 deg. Slider: band_w x slider_len.
  * webs: web_w x 2 mm plates on great circles: shell 1 from the S1 stud to the inner edge of the G2 arc (at mid
    travel); shell 2 from the S2 stud along u2 -> d down to the carriage.
  * C-track 6 radial x 8 axial, carriage 25 x 12 x 6, passive slide 30 x 10 x 5 (as seed-2r-cring), inner radius =
    the arm-skin envelope under it + ring_clear.
Envelopes are fitted on the fit poses (fit-clip frames + a workspace subsample, held-out clips never posed; the cache
of seed-2r-cring, .cache/concept_models/seed-2r-cring/fit_skin.npz, built by docs/concepts/models/_seed2r_skin.py),
at quantile q of the per-pose envelopes.
Taken (bench rules, as seed-2r-cring): closure on the design branch with a 10 deg singularity margin, every slider
on its guide arc and the carriage on the C span, along each fit clip (all its frames, 10 fps) no joint jump > 30 deg
between consecutive frames, no interference (non-adjacent parts >= 1 mm, adjacent parts outside their shared joint
>= 0.15 mm). In-band samples: skin-facing surfaces (slider and guide undersides, web undersides, track inner face, carriage
overhangs, slide inner face); contact: every surface (tops and edges too) - a non-facing
sample inside the body is appended so the bench counts the pose as contact.

    python3 docs/concepts/models/seed-pauldron-shells.py check     # default params on Bench(20, 40) + a few poses
    python3 docs/concepts/models/seed-pauldron-shells.py sweep     # coarse -> refine on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, HERE)
import body_pose as BP                                                     # noqa: E402

ID = "seed-pauldron-shells"
D2R = math.pi / 180
SH_T, LINER = 2.0, 1.0                              # shell / band thickness, liner (= running gap guide -> web above)
TR_RAD, TR_AX = 6.0, 8.0                            # C-track section (seed-2r-cring)
CAR_ARC, CAR_AX, CAR_RAD = 25.0, 12.0, 6.0          # carriage
SL_LEN, SL_W, SL_RAD = 30.0, 10.0, 5.0              # passive slide block
SP = 2.0                                            # skin-facing sample grid (1 point / 4 mm2)
SP_O = 2.0                                          # other surfaces (contact only)
RAMP = math.tan(60 * D2R)                           # a web may leave a band level at <= 60 deg
SING = 10.0                                         # deg, fold / stretch singularity margin (band evaluator default)
FLIP = 30.0                                         # deg per 10 fps frame: larger joint jump = branch flip / not followed
FP_M = 2.0                                          # footprint margin (mm) around every part for the envelope fit
T_CAP = 200.0                                       # skin farther than this from GH never pushes a part up

PARAMS = dict(u1_az=57.0, u1_el=48.0, a1=90.0, a2=90.0, branch=1, g1=25.0, g2=25.0, band_w=12.0, slider_len=30.0,
              web_w=12.0, web="skin", cov=1.0, ring_L=100.0, open_dir=180.0, open_w=110.0, clear=3.0, ring_clear=3.0, q=1.0)
SWEEP = dict(u1_az=(0, 120), u1_el=(20, 85), a1=(60, 120), a2=(60, 120), branch=(-1, 1), g1=(12, 70), g2=(12, 45),
             band_w=(10, 16), slider_len=(24, 40), web_w=(10, 30), web=("skin", "sphere"), cov=(0.95, 1.0),
             ring_L=(60, 140), open_dir=(120, 240), open_w=(90, 120), clear=(2, 5), ring_clear=(2, 4), q=(0.97, 1.0))


def bvec(az, el):                                    # unit vector in the scapula frame: az from anterior (+x) to lateral (+z)
    a, e = az * D2R, el * D2R
    return np.array([math.cos(e) * math.cos(a), math.sin(e), math.cos(e) * math.sin(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def wrap(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------- rig constants
_R = BP._rig()
D_LOC = np.array(_R.L["elbow"], float); D_LOC /= np.linalg.norm(D_LOC)          # humerus long axis (GH -> elbow), local
_H0 = BP.segs(_R.L, _R.s, dict(plane=0, elev=0, axial=0, flex=12, pron=0))[0][2][0]
REF_LOC = _H0.T @ np.array([0.0, 0.0, 1.0]); REF_LOC = unit(REF_LOC - (REF_LOC @ D_LOC) * D_LOC)   # lateral at rest


def frames_of(pose):
    (T, S, H, Fa, Pr), lift = BP.segs(_R.L, _R.s, pose)
    return dict(S=S, H=H, lift=lift)


def chain(SR, HR, p):
    """IK of the 2R + ring (seed-2r-cring's closure) for scapula rotations SR (n,3,3), humerus rotations HR (n,3,3), on
    the design branch. Joint values: th1 = azimuth of u2 about u1 from a scapula-fixed reference (= where the J1 slider
    sits on its guide), th2 = azimuth of d about u2 from shell 1's reference (toward u1) (= J2 slider on its guide),
    psi = carriage angle on the C-track in the humerus frame."""
    SR = np.asarray(SR).reshape(-1, 3, 3); HR = np.asarray(HR).reshape(-1, 3, 3)
    b0 = bvec(p["u1_az"], p["u1_el"]); u1 = SR @ b0; d = HR @ D_LOC
    a1, a2 = p["a1"] * D2R, p["a2"] * D2R
    c = np.clip((u1 * d).sum(-1), -1, 1); s2 = 1 - c * c + 1e-12
    al = (math.cos(a1) - c * math.cos(a2)) / s2; be = (math.cos(a2) - c * math.cos(a1)) / s2
    pp = al[:, None] * u1 + be[:, None] * d; h2 = 1 - (pp * pp).sum(-1)
    n = unit(np.cross(u1, d)); u2 = unit(pp + p["branch"] * np.sqrt(np.clip(h2, 0, None))[:, None] * n)
    ang = np.arccos(c) / D2R
    lo = abs(p["a1"] - p["a2"]) + SING; hi = min(p["a1"] + p["a2"], 360 - p["a1"] - p["a2"]) - SING
    ok = (h2 > 0) & (ang >= lo) & (ang <= hi)
    r0 = np.cross(b0, [0.0, 1.0, 0.0]) if abs(b0[1]) < 0.95 else np.cross(b0, [1.0, 0.0, 0.0]); r0 = unit(r0)
    r1 = SR @ r0
    th1 = np.arctan2((np.cross(u1, r1) * u2).sum(-1), (r1 * u2).sum(-1)) / D2R
    r2 = unit(u1 - (u1 * u2).sum(-1, keepdims=True) * u2)
    th2 = np.arctan2((np.cross(u2, r2) * d).sum(-1), (r2 * d).sum(-1)) / D2R
    href = HR @ REF_LOC; hside = np.cross(d, href)
    ea = unit(u2 - (u2 * d).sum(-1, keepdims=True) * d)                   # carriage direction (toward u2, perp. to d)
    psi = np.arctan2((hside * ea).sum(-1), (href * ea).sum(-1)) / D2R
    return dict(u1=u1, u2=u2, d=d, ok=ok, th1=th1, th2=th2, psi=psi, href=href, hside=hside, ea=ea, r1=r1, r2=r2, b0=b0, r0=r0)


def in_span(psi, p, half_arc_deg):
    off = np.abs(wrap(psi - p["open_dir"]))
    return off >= p["open_w"] / 2 + half_arc_deg


def arc_range(vals, cov):
    """circular range (lo, hi) deg covering the cov-quantile band of the angles vals (hi - lo may exceed 360 -> full)"""
    v = np.asarray(vals, float)
    if not len(v): return 0.0, 0.0
    m = math.atan2(np.sin(v * D2R).mean(), np.cos(v * D2R).mean()) / D2R
    dv = wrap(v - m)
    if cov >= 1.0: lo, hi = dv.min(), dv.max()
    else: lo, hi = np.quantile(dv, (1 - cov) / 2), np.quantile(dv, (1 + cov) / 2)
    return float(m + lo), float(m + hi)


def on_arc(a, lo, hi, half):
    """angle a (deg) with a part of half-width half (deg) fully inside the arc [lo, hi]; full ring -> always"""
    if hi - lo >= 360 - 1e-6: return np.ones(np.shape(a), bool)
    rel = (np.asarray(a) - lo) % 360.0
    return (rel >= half) & (rel <= hi - lo - half)


# ---------------------------------------------------------------- fit-pose skin (dense samples)
class FitSkin:
    """skin of the fit poses (seed-2r-cring's cache: fit-clip frames + workspace subsample, shoulder-region vertices);
    samples = vertices + face centroids (the farthest point of a triangle from GH is one of its vertices), forearm and
    anything beyond T_CAP from GH dropped"""
    def __init__(self):
        import _seed2r_skin as SK
        if not os.path.exists(SK.OUT): SK.build()
        Z = np.load(SK.OUT); self.idx = Z["idx"]; self.vid = Z["vid"]; self.V = Z["V"]; self.POSE = Z["POSE"]; self.CID = Z["CID"]
        F = BP.F; m = np.zeros(len(BP.V0), bool); m[self.vid] = True; loc = -np.ones(len(BP.V0), int); loc[self.vid] = np.arange(len(self.vid))
        Fk = F[m[F].all(1)]; self.Fl = loc[Fk]
        V0 = BP.V0; arm = np.asarray(BP.ARMV); fore = arm & (V0[:, 1] < -300.0)
        vf = fore[self.vid]; va = arm[self.vid] & ~vf
        cf = vf[self.Fl].any(1); ca = va[self.Fl].all(1)
        self.s_fore = np.r_[vf, cf]; self.s_arm = np.r_[va, ca & ~cf]
        self.frames = [frames_of(dict(plane=float(q[0]), elev=float(q[1]), axial=float(q[2]), flex=float(q[3]), pron=float(q[4]))) for q in self.POSE]
        self.SR = np.stack([f["S"][0] for f in self.frames]); self.HR = np.stack([f["H"][0] for f in self.frames])
        self.n = len(self.idx); self._s = {}

    def samples(self, k):
        """(S (m, 3), r (m,), arm mask (m,)) float32, cached"""
        if k not in self._s:
            V = self.V[k]; S = np.r_[V, V[self.Fl].mean(1)].astype(np.float32)
            r = np.linalg.norm(S, axis=1); keep = (~self.s_fore) & (r < T_CAP)
            self._s[k] = (S[keep], r[keep], self.s_arm[keep])
        return self._s[k]


# ---------------------------------------------------------------- envelopes (max skin radius under a footprint)
def _sph(S, axis, ref, r=None):
    """colatitude (rad) about axis and azimuth (deg) from ref of points S"""
    side = np.cross(axis, ref); r = np.linalg.norm(S, axis=1) + 1e-9 if r is None else r + 1e-9
    col = np.arccos(np.clip(S @ axis / r, -1, 1)); az = np.arctan2(S @ side, S @ ref) / D2R
    return col, az, r


def env_band(S, r, axis, ref, g, w, lo, hi):
    """max distance from GH of skin samples under a spherical band about axis: colatitude g (rad) +- w/2 mm, azimuth
    [lo, hi] deg from ref (+ FP_M margin)"""
    c = S @ axis / r; hmax = (w / 2 + FP_M) / 20.0
    pre = (c <= math.cos(max(g - hmax, 0.0))) & (c >= math.cos(min(g + hmax, math.pi)))
    if not pre.any(): return -np.inf
    S, r, c = S[pre], r[pre], c[pre]
    col = np.arccos(np.clip(c, -1, 1)); half = (w / 2 + FP_M) / np.maximum(r, 20)
    m = np.abs(col - g) <= half
    if hi - lo < 360 - 1e-6 and m.any():
        side = np.cross(axis, ref); az = np.arctan2(S @ side, S @ ref) / D2R
        ext = (FP_M / np.maximum(r * np.sin(np.maximum(col, 0.05)), 5)) / D2R
        rel = (az - lo + ext) % 360.0; m &= rel <= (hi - lo) + 2 * ext
    return float(r[m].max()) if m.any() else -np.inf


def env_strap(S, e1, e2, e3, phis, width):
    """max in-plane radius of skin samples under a strap station grid phis (rad) on the great circle e1 -> e2"""
    z = S @ e3; m = np.abs(z) <= width / 2 + FP_M
    S = S[m]; x = S @ e1; y = S @ e2; rho = np.hypot(x, y)
    m = (rho < T_CAP) & (rho > 1)
    phi = np.arctan2(y[m], x[m]); rho = rho[m]
    out = np.full(len(phis), -np.inf)
    if not len(phi): return out
    dphi = phis[1] - phis[0]; b = np.round((phi - phis[0]) / dphi).astype(int)
    inr = (b >= -50) & (b < len(phis) + 50); b, rho = b[inr], rho[inr]
    if not len(b): return out
    halo = np.ceil((SP / 2 + FP_M) / np.maximum(rho, 30) / dphi).astype(int)
    for h in range(0, int(halo.max()) + 1):
        for sgn in ((0,) if h == 0 else (-1, 1)):
            bb = b + sgn * h; mm = (bb >= 0) & (bb < len(phis)) & (halo >= h)
            np.maximum.at(out, bb[mm], rho[mm])
    return out


def env_ring(S, d, href, hside, t0, t1, psi_lo, psi_hi):
    t = S @ d; m = (t >= t0) & (t <= t1)
    if not m.any(): return -np.inf
    P = S[m] - t[m, None] * d; rr = np.linalg.norm(P, axis=1)
    ps = np.arctan2(P @ hside, P @ href) / D2R
    rel = (ps - psi_lo) % 360.0; mm = (rel <= (psi_hi - psi_lo)) & (rr < 120)
    return float(rr[mm].max()) if mm.any() else -np.inf


def agg(vals, q):
    v = np.asarray(vals, float)
    if v.ndim == 1: v = v[np.isfinite(v)]
    else: v = np.where(np.isfinite(v), v, 0.0)
    if not v.size: return -np.inf if v.ndim == 1 else np.zeros(v.shape[1:])
    if q >= 1.0: return np.max(v, axis=0)
    return np.quantile(v, q, axis=0)


# ---------------------------------------------------------------- part primitives
def _grid(a, b, step):
    n = max(2, int(math.ceil((b - a) / step)) + 1)
    return np.linspace(a, b, n)


class Part:
    def __init__(self, face, other, inside):
        self.face = face; self.other = other; self.inside = inside

    @property
    def all(self):
        return np.r_[self.face, self.other]


def _band(axis, ref, g, w, lo, hi, r0, thick, face=True):
    """spherical band about axis: colatitude g (rad) +- w/2 mm, azimuth [lo, hi] deg from ref, radii [r0, r0 + thick].
    face=True: the underside faces the skin (sampled as face)"""
    side = np.cross(axis, ref); rm = r0 + thick / 2
    cols = _grid(g - w / 2 / rm, g + w / 2 / rm, SP / rm)
    full = hi - lo >= 360 - 1e-6
    span = 360.0 if full else hi - lo
    circ = max(rm * math.sin(max(g, 0.05)), 3.0)
    azs = (lo + np.linspace(0, span, max(2, int(math.ceil(span * D2R * circ / SP)) + 1), endpoint=not full)) * D2R
    C, A = np.meshgrid(cols, azs); C, A = C.ravel(), A.ravel()
    dirs = np.cos(C)[:, None] * axis + np.sin(C)[:, None] * (np.cos(A)[:, None] * ref + np.sin(A)[:, None] * side)
    under = r0 * dirs; top = (r0 + thick) * dirs
    edges = [rr * dirs[np.isin(C, (cols[0], cols[-1]))] for rr in _grid(r0, r0 + thick, SP_O)]
    if not full:
        e = np.isin(A, (azs[0], azs[-1])); edges += [rr * dirs[e] for rr in _grid(r0, r0 + thick, SP_O)]
    other = np.concatenate([top] + edges)

    def inside(P, m):
        col, az, r = _sph(P, axis, ref)
        ok = (np.abs(col - g) <= (w / 2 + m) / np.maximum(r, 1)) & (r >= r0 - m) & (r <= r0 + thick + m)
        if not full:
            ext = m / np.maximum(r * np.sin(np.maximum(col, 0.05)), 1) / D2R
            ok &= ((az - lo + ext) % 360.0) <= span + 2 * ext
        return ok
    if face: return Part(under, other, inside)
    return Part(np.zeros((0, 3)), np.r_[under, other], inside)


def _union(parts):
    face = np.concatenate([p.face for p in parts]); other = np.concatenate([p.other for p in parts])
    fns = [p.inside for p in parts]
    return Part(face, other, lambda P, m: np.logical_or.reduce([f(P, m) for f in fns]))


def _strap(e1, e2, e3, phis, r, s0, s1, width, thick=SH_T):
    if s1 <= s0: s1 = s0 + 1e-3
    rm = float(np.interp(0.5 * (s0 + s1), phis, r)); ph = _grid(s0, s1, SP / max(rm, 30))
    rr = np.interp(ph, phis, r); w = np.arange(-width / 2 + SP / 2, width / 2, SP)
    g = np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2
    face = (rr[:, None, None] * g[:, None, :] + w[None, :, None] * e3).reshape(-1, 3)
    top = ((rr + thick)[:, None, None] * g[:, None, :] + w[None, :, None] * e3).reshape(-1, 3)
    side = np.r_[((rr + thick / 2)[:, None] * g + width / 2 * e3), ((rr + thick / 2)[:, None] * g - width / 2 * e3)]

    def inside(P, m):
        x = P @ e1; y = P @ e2; z = P @ e3; rho = np.hypot(x, y); ph_ = np.arctan2(y, x)
        rp = np.interp(ph_, phis, r)
        return (ph_ >= s0 - m / np.maximum(rho, 1)) & (ph_ <= s1 + m / np.maximum(rho, 1)) & (np.abs(z) <= width / 2 + m) & (rho >= rp - m) & (rho <= rp + thick + m)
    return Part(face, np.r_[top, side], inside)


def _ring(d, href, hside, t0, t1, R0, R1, ps0, ps1, car=None):
    """ring sector about d: axial [t0, t1], radial [R0, R1], angle [ps0, ps1] deg (humerus frame). car = (ta, tb): a
    carriage straddling the track over [ta, tb]: only its overhangs face the skin. (as seed-2r-cring)"""
    ps = _grid(ps0 * D2R, ps1 * D2R, SP / R0); tt = _grid(t0, t1, SP)
    rad = lambda R, P, T: T[..., None] * d + R * (np.cos(P)[..., None] * href + np.sin(P)[..., None] * hside)
    PP, TT = np.meshgrid(ps, tt); PP, TT = PP.ravel(), TT.ravel()
    inner = rad(R0, PP, TT); outer = rad(R1, PP, TT)
    rr = _grid(R0, R1, SP_O); P2, R2 = np.meshgrid(ps, rr); P2, R2 = P2.ravel(), R2.ravel()
    ends = np.r_[t0 * d + R2[:, None] * (np.cos(P2)[:, None] * href + np.sin(P2)[:, None] * hside),
                 t1 * d + R2[:, None] * (np.cos(P2)[:, None] * href + np.sin(P2)[:, None] * hside)]
    T3, R3 = np.meshgrid(tt, rr); T3, R3 = T3.ravel(), R3.ravel()
    cends = np.r_[T3[:, None] * d + R3[:, None] * (math.cos(ps0 * D2R) * href + math.sin(ps0 * D2R) * hside),
                  T3[:, None] * d + R3[:, None] * (math.cos(ps1 * D2R) * href + math.sin(ps1 * D2R) * hside)]
    if car is not None:
        over = (TT < car[0]) | (TT > car[1]); face = inner[over]; other = np.r_[inner[~over], outer, ends, cends]
    else:
        face = inner; other = np.r_[outer, ends, cends]
    span = (ps1 - ps0)

    def inside(P, m):
        t = P @ d; Q = P - t[:, None] * d; r = np.linalg.norm(Q, axis=1)
        a = np.arctan2(Q @ hside, Q @ href) / D2R; rel = (a - ps0 + m / np.maximum(r, 1) / D2R) % 360.0
        return (t >= t0 - m) & (t <= t1 + m) & (r >= R0 - m) & (r <= R1 + m) & (rel <= span + 2 * m / np.maximum(r, 1) / D2R)
    return Part(face, other, inside)


def _profile(phis, env, s0, h0, s1, h1, rho_min=40.0):
    """web underside radius: skin envelope, >= h0 up to s0 (the band it leaves) and >= h1 from s1 (the band it lands
    on), joined by <= 60 deg ramps"""
    r = env.copy(); rho = np.maximum(env, rho_min)
    a = np.maximum(0, phis - s0) * rho; b = np.maximum(0, s1 - phis) * rho
    r = np.maximum(r, h0 - RAMP * a); r = np.maximum(r, h1 - RAMP * b)
    return r


# ---------------------------------------------------------------- design (fitted to the fit poses)
def _floor_profile(phis, base, floors, rho_ref):
    """web underside radius per station: max(base, every floor level minus a <= 60 deg ramp from its stations).
    floors = [(station mask, level mm)]"""
    r = base.copy(); s_mm = phis * rho_ref
    for mask, level in floors:
        if not mask.any(): continue
        dist = np.abs(s_mm[:, None] - s_mm[mask][None, :]).min(1)
        r = np.maximum(r, level - RAMP * dist)
    return r


class Design:
    """Joint J (radius rho_J = the slider underside): slider S (distal shell, inner member) [rho, rho+2], liner, guide
    G (proximal shell, outer member, slotted along its centreline) [rho+3, rho+5]; the slider's stud runs in the slot
    and the distal shell's web leaves it ABOVE the guide [rho+6, rho+8] (1 mm running gap)."""
    def __init__(self, p, fit):
        self.p = p = dict(PARAMS, **p)
        C = chain(fit.SR, fit.HR, p); ok = C["ok"]; self.fit_ok = float(ok.mean())
        g1, g2 = p["g1"] * D2R, p["g2"] * D2R; a1, a2 = p["a1"] * D2R, p["a2"] * D2R
        w, Ls, ww, L = p["band_w"], p["slider_len"], p["web_w"], p["ring_L"]
        vk = np.nonzero(ok)[0]
        # joint travels -> guide arcs (slider centre azimuths over the valid fit poses, cov quantiles)
        self.t1 = arc_range(C["th1"][vk], p["cov"]); self.t2 = arc_range(C["th2"][vk], p["cov"])
        rg = 62.0
        self.h1 = (Ls / 2) / max(rg * math.sin(g1), 3) / D2R; self.h2 = (Ls / 2) / max(rg * math.sin(g2), 3) / D2R
        self.G1 = (self.t1[0] - self.h1 - 1, self.t1[1] + self.h1 + 1); self.G2 = (self.t2[0] - self.h2 - 1, self.t2[1] + self.h2 + 1)
        if self.G1[1] - self.G1[0] >= 360: self.G1 = (self.G1[0], self.G1[0] + 360.0)
        if self.G2[1] - self.G2[0] >= 360: self.G2 = (self.G2[0], self.G2[0] + 360.0)
        # shell 1 frame F1 = (u1, e1 = u2 perp u1, n1): u2 = cos a1 u1 + sin a1 e1; G2 azimuth reference r2 (toward u1).
        # Web 1: great circle from the S1 stud P1 = (cos g1, sin g1, 0) to the inner edge of the G2 arc at mid travel Q2.
        u2_1 = np.array([math.cos(a1), math.sin(a1), 0.0]); r2_1 = unit(np.array([1.0, 0, 0]) - math.cos(a1) * u2_1)
        s2_1 = np.cross(u2_1, r2_1); mid2 = 0.5 * (self.t2[0] + self.t2[1]) * D2R
        P1 = np.array([math.cos(g1), math.sin(g1), 0.0]); gq = max(g2 - (w / 2) / 62.0, 0.02)
        Q2 = math.cos(gq) * u2_1 + math.sin(gq) * (math.cos(mid2) * r2_1 + math.sin(mid2) * s2_1)
        self.w1_e1 = P1; self.w1_e2 = unit(Q2 - (Q2 @ P1) * P1); self.w1_e3 = np.cross(P1, self.w1_e2)
        self.w1_ang = math.acos(np.clip(P1 @ Q2, -1, 1))
        self.u2_1, self.r2_1 = u2_1, r2_1
        self.phi1 = np.linspace(0, max(self.w1_ang, 1e-3), max(8, int(self.w1_ang * 70)))
        self.phi2 = np.linspace(0, a2, max(8, int(a2 * 110)))
        D1 = np.cos(self.phi1)[:, None] * P1 + np.sin(self.phi1)[:, None] * self.w1_e2          # web-1 stations (F1)
        col_u1 = np.arccos(np.clip(D1[:, 0], -1, 1)); col_u2 = np.arccos(np.clip(D1 @ u2_1, -1, 1))
        half_open = p["open_w"] / 2; ps_lo = p["open_dir"] + half_open - 4; ps_hi = p["open_dir"] + 360 - half_open + 4
        mid = p["open_dir"] + 180.0
        EG1, ES1, EG2, ES2, EW1, EW2, RI, RS = [], [], [], [], [], [], [], []
        b0, r0 = C["b0"], C["r0"]
        for k in vk[::max(1, int(p.get("fit_stride", 1)))]:
            S, r, armm = fit.samples(k)
            u1, u2, d = C["u1"][k], C["u2"][k], C["d"][k]
            X0 = S @ fit.SR[k].astype(np.float32)                           # scapula coordinates
            EG1.append(env_band(X0, r, b0, r0, g1, w, *self.G1))
            e1 = unit(u2 - (u2 @ u1) * u1); n1 = np.cross(u1, e1)
            M1 = np.c_[u1, e1, n1].astype(np.float32); X1 = S @ M1          # shell 1 coordinates
            ES1.append(env_band(X1, r, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), g1, w, -self.h1, self.h1))
            EG2.append(env_band(X1, r, u2_1, r2_1, g2, w, *self.G2))
            EW1.append(env_strap(X1, self.w1_e1, self.w1_e2, self.w1_e3, self.phi1, ww))
            f = unit(d - (d @ u2) * u2); m2 = np.cross(u2, f)
            M2 = np.c_[u2, f, m2].astype(np.float32); X2 = S @ M2           # shell 2 coordinates
            ES2.append(env_band(X2, r, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), g2, w, -self.h2, self.h2))
            EW2.append(env_strap(X2, np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), np.array([0, 0, 1.0]), self.phi2, ww))
            Sa = S[armm]
            RI.append(env_ring(Sa, d, C["href"][k], C["hside"][k], L - TR_AX / 2 - FP_M, L + TR_AX / 2 + FP_M, ps_lo, ps_hi))
            dw = (SL_W / 2 + FP_M) / 55.0 / D2R
            RS.append(env_ring(Sa, d, C["href"][k], C["hside"][k], L + TR_AX / 2 - FP_M, L + TR_AX / 2 + SL_LEN + FP_M, mid - dw, mid + dw))
        self.E = dict(G1=np.array(EG1), S1=np.array(ES1), G2=np.array(EG2), S2=np.array(ES2), W1=np.array(EW1), W2=np.array(EW2), RI=np.array(RI))
        q = p["q"]; c = p["clear"]
        eG1, eS1, eG2, eS2 = agg(EG1, q), agg(ES1, q), agg(EG2, q), agg(ES2, q)
        ew1, ew2 = agg(np.array(EW1), q), agg(np.array(EW2), q)
        self.env = dict(G1=eG1, S1=eS1, G2=eG2, S2=eS2, W1=float(np.max(ew1)), W2=float(np.max(ew2)))
        self.Rin = float(agg(RI, p["q"])) + p["ring_clear"]; self.Rs = float(agg(RS, p["q"])) + p["ring_clear"]
        Rc = self.Rin + TR_RAD + CAR_RAD; self.cpt = (L, Rc); hc = math.hypot(L, Rc)
        self.phic = a2 - math.atan2(Rc, L)
        up = SH_T + LINER                                                   # 3 mm: slider -> guide, guide -> web above
        on_g1 = np.abs(col_u1 - g1) <= (w / 2 + 1) / 62.0                   # web-1 stations over the G1 band
        on_g2 = (np.abs(col_u2 - g2) <= (w / 2 + 1) / 62.0) & (self.phi1 < self.w1_ang - 4.0 / 62.0)
        end1 = self.phi1 >= self.w1_ang - 1.0 / 62.0
        pe = g2 + (w / 2 + 1.0) / 62.0; on2 = self.phi2 <= pe; endc = self.phi2 >= self.phic - 1e-9
        if p["web"] == "sphere":
            Rw2 = float(np.max(ew2[self.phi2 <= self.phic])) if (self.phi2 <= self.phic).any() else -np.inf
            R = max(eS1 + c, eG1 + c - up, float(np.max(ew1)) + c - 2 * up, eG2 + c - 2 * up, eS2 + c - up, Rw2 + c - 3 * up)
            self.rho1 = R; self.rho2 = R + up
            self.w1 = np.full_like(self.phi1, R + 2 * up)
            sph = self.phi2 <= self.phic
            self.w2 = np.where(sph, R + 3 * up, 0.0)
            self.w2 = _floor_profile(self.phi2, self.w2, [(sph, R + 3 * up), (endc, hc)], 62.0)
        else:
            self.rho1 = max(eS1 + c, eG1 + c - up); self.rho2 = max(eS2 + c, eG2 + c - up)
            self.w1 = _floor_profile(self.phi1, ew1 + c, [(on_g1, self.rho1 + 2 * up), (on_g2, self.rho2 + 3 * up), (end1, self.rho2 + up)], 62.0)
            self.w2 = _floor_profile(self.phi2, ew2 + c, [(on2, self.rho2 + 2 * up), (endc, hc)], 62.0)
        self.ok_geom = self.phic > pe + 3.0 / 62.0 and self.w1_ang > (w / 2 + 3) / 62.0
        self.car_half = (CAR_ARC / 2) / (self.Rin + TR_RAD) / D2R

    # ---- parts in thorax coordinates for one pose
    def parts(self, C, k, SR):
        p = self.p; L = p["ring_L"]; g1, g2 = p["g1"] * D2R, p["g2"] * D2R; w, Ls = p["band_w"], p["slider_len"]
        u1, u2, d, href, hside = C["u1"][k], C["u2"][k], C["d"][k], C["href"][k], C["hside"][k]
        b0w, r0w = SR @ C["b0"], SR @ C["r0"]
        e1 = unit(u2 - (u2 @ u1) * u1); n1 = np.cross(u1, e1); M1 = np.c_[u1, e1, n1]          # shell 1 -> thorax
        f = unit(d - (d @ u2) * u2); m2 = np.cross(u2, f)                                       # shell 2 frame
        up = SH_T + LINER; out = {}
        out["S1"] = _band(u1, e1, g1, w, -self.h1, self.h1, self.rho1, SH_T)                    # shell 1's slider (inner)
        out["G1"] = _band(b0w, r0w, g1, w, *self.G1, self.rho1 + up, SH_T)                    # base guide (outer, slotted)
        out["W1"] = _strap(M1 @ self.w1_e1, M1 @ self.w1_e2, M1 @ self.w1_e3, self.phi1, self.w1, 0.0, self.w1_ang, p["web_w"])
        out["S2"] = _band(u2, f, g2, w, -self.h2, self.h2, self.rho2, SH_T)                     # shell 2's slider (inner)
        out["G2"] = _band(u2, M1 @ self.r2_1, g2, w, *self.G2, self.rho2 + up, SH_T)          # shell 1's guide (outer)
        out["W2"] = _strap(u2, f, m2, self.phi2, self.w2, g2, self.phic, p["web_w"])
        hw = p["open_w"] / 2
        out["track"] = _ring(d, href, hside, L - TR_AX / 2, L + TR_AX / 2, self.Rin, self.Rin + TR_RAD, p["open_dir"] + hw, p["open_dir"] + 360 - hw)
        midd = p["open_dir"] + 180; dw = (SL_W / 2) / self.Rs / D2R
        out["slide"] = _ring(d, href, hside, L + TR_AX / 2, L + TR_AX / 2 + SL_LEN, self.Rs, self.Rs + SL_RAD, midd - dw, midd + dw)
        ch = self.car_half; R0 = self.Rin + TR_RAD; psi = float(C["psi"][k])
        out["car"] = _ring(d, href, hside, L - CAR_AX / 2, L + CAR_AX / 2, R0, R0 + CAR_RAD, psi - ch, psi + ch, car=(L - TR_AX / 2, L + TR_AX / 2))
        return out


GROUP = dict(G1="base", S1="sh1", W1="sh1", G2="sh1", S2="sh2", W2="sh2", car="sh2", track="arm", slide="arm")
NONADJ_G = {("base", "sh2"), ("base", "arm"), ("sh1", "arm")}
ADJ_EXEMPT = {("G1", "S1"), ("G2", "S2"), ("car", "track")}       # the sliding pairs themselves


def interfere(parts):
    """first interfering pair or None: non-adjacent groups >= 1 mm apart; adjacent groups >= 0.15 mm apart outside
    their sliding pair"""
    names = list(parts)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ga, gb = GROUP[a], GROUP[b]
            if ga == gb: continue
            key = tuple(sorted((ga, gb)))
            if key in NONADJ_G or (key[1], key[0]) in NONADJ_G: m = 1.0
            elif (a, b) in ADJ_EXEMPT or (b, a) in ADJ_EXEMPT: continue
            else: m = 0.15
            A, B = parts[a], parts[b]
            if B.inside(A.all, m).any() or A.inside(B.all, m).any(): return f"{a}/{b}"
    return None


# ---------------------------------------------------------------- model on the bench
class Model:
    def __init__(self, p, fit, bench):
        self.D = Design(p, fit); self.p = self.D.p; self.B = bench
        self._prep_clips()

    def _taken_kin(self, C, k):
        D = self.D
        if not C["ok"][k]: return "closure"
        if not on_arc(C["th1"][k], D.G1[0], D.G1[1], D.h1 + 0.5): return "J1 limit"
        if not on_arc(C["th2"][k], D.G2[0], D.G2[1], D.h2 + 0.5): return "J2 limit"
        if not in_span(C["psi"][k:k + 1], self.p, D.car_half + 1.0)[0]: return "carriage off track"
        return ""

    def _prep_clips(self):
        """continuity on every frame of every fit clip (10 fps): followed iff closure, sliders on their guides, carriage
        on the track, and no joint jump > FLIP since the last followed frame"""
        import concept_bench as CB
        Zp = CB._poses_all(); names = list(Zp["NAMES"]); cid = Zp["CID"]; P = Zp["POSE"]
        self.status = {}
        for n in CB.FIT:
            ix = np.nonzero(cid == names.index(n))[0]
            fr = [frames_of(dict(plane=float(q[0]), elev=float(q[1]), axial=float(q[2]), flex=float(q[3]), pron=float(q[4]))) for q in P[ix]]
            C = chain(np.stack([f["S"][0] for f in fr]), np.stack([f["H"][0] for f in fr]), self.p)
            last = None
            for k, j in enumerate(ix):
                why = self._taken_kin(C, k)
                if why: self.status[int(j)] = (False, why); continue
                qv = np.array([C["th1"][k], C["th2"][k], C["psi"][k]])
                if last is not None and np.abs(wrap(qv - last)).max() > FLIP: self.status[int(j)] = (False, "flip"); last = qv; continue
                self.status[int(j)] = (True, ""); last = qv

    def metal(self, i, all_points=False):
        B = self.B; j = int(B.idx[i]); fr = B.frames(i); p = self.p
        C = chain(fr["S"][0][None], fr["H"][0][None], p)
        if not self.D.ok_geom: return None, "geometry"
        if B.kind[i] == "clip":
            ok, why = self.status.get(j, (False, "missing"))
            if not ok: return None, why
        else:
            why = self._taken_kin(C, 0)
            if why: return None, why
        parts = self.D.parts(C, 0, fr["S"][0])
        why = interfere(parts)
        if why: return None, "interference " + why
        face = np.concatenate([parts[k].face for k in parts]); other = np.concatenate([parts[k].other for k in parts])
        if all_points: return (face, other, parts), ""
        do = B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        return face, ""

    def run(self):
        B = self.B; B.reset(); why = {}
        for i in range(len(B.poses)):
            P, w = self.metal(i)
            if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None)
            else:
                d = B.record(i, P)
                if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        r = B.report(); r["why"] = why; return r


def metal(pose, frames, params, _cache={}):
    """public hook (task API): metal sample points (k, 3) for one bench pose, or None. The model is fitted per params
    and needs the bench (params['_bench']) to look the pose up (clip continuity is per clip)."""
    B = params["_bench"]; key = json.dumps({k: v for k, v in params.items() if not k.startswith("_")}, sort_keys=True)
    if key not in _cache: _cache.clear(); _cache[key] = Model({k: v for k, v in params.items() if not k.startswith("_")}, FitSkin(), B)
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


# ---------------------------------------------------------------- sweep
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def evaluate(p, fit, B):
    t = time.time(); M = Model(p, fit, B); r = M.run(); D = M.D
    r.update(rho1=round(D.rho1, 1), rho2=round(D.rho2, 1), Rin=round(D.Rin, 1), G1=round(D.G1[1] - D.G1[0]), G2=round(D.G2[1] - D.G2[0]),
             fit_ok=round(D.fit_ok, 3), secs=round(time.time() - t, 1))
    return r


KEYS = ('u1_az', 'u1_el', 'a1', 'a2', 'branch', 'g1', 'g2', 'band_w', 'slider_len', 'web_w', 'web', 'cov', 'ring_L', 'open_dir', 'open_w', 'clear', 'ring_clear', 'q')


def sweep(configs, B, fit, out=SWEEP_OUT, tag=""):
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r = evaluate(p, fit, B)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"],
                   shape=dict(rho1=r["rho1"], rho2=r["rho2"], Rin=r["Rin"], G1=r["G1"], G2=r["G2"], fit_ok=r["fit_ok"]), mode=r["mode"], stage=tag)
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | rho {r['rho1']}/{r['rho2']} Rin {r['Rin']} G {r['G1']}/{r['G2']} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in KEYS), flush=True)
    return rows


if __name__ == "__main__":
    import concept_bench as CB
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40); fit = FitSkin()
        print(evaluate(dict(PARAMS), fit, B))
