"""seed-2r-cring: 2R spherical shoulder + open C-ring axial bearing on the upper arm (3 ACTIVE DOF, 1 passive slide).

Topology (scapula handler -> user's upper-arm cuff):
    base (scapula handler) --R1 (O20 hub, axis u1 through GH, fixed in the scapula frame S)--> link 1 (strap on the
    great circle u1 -> u2) --R2 (O20 hub, axis u2 through GH)--> link 2 (strap on the great circle u2 -> d, down over
    the deltoid) -> carriage riding an open C-track (axis = humerus long axis d, the 3rd joint) -> C-track fixed to the
    user's cuff through a passive slide along the humerus (absorbs GH translation along the arm; the bench rig's GH is
    fixed, so the slide sits at its nominal position here).
DOF: R1 and R2 set the humerus direction d (2-circle closure: |u1.u2| = cos a1, u2.d = cos a2, two branches, the
design keeps one: sign det[u1, u2, d]); the C-ring takes the arm's axial rotation (carriage angle psi on the track) ->
3 active rotations, all axes through GH. The slide is set by the closure with the cuff (passive, not counted).

Geometry (idealised, every part at its real size; 1 sample / 4 mm2 = 2 mm grid on every surface):
  * hubs: O20 x 12.25 (docs/HARDWARE.md v5 joint): flat skin face F_J (lower member plate), upper member at F_J + 3.15,
    crown at F_J + 12.25. F_J = envelope of the skin under the O20 disc (+2 mm margin) over the fit poses + clear.
  * links: 8 x 3 mm straps on their great circle, underside at in-plane radius r(phi) = max(skin envelope under the
    strap (+2 mm margin each side) over the fit poses + clear, the hub / carriage level they leave from minus a 60 deg
    ramp). Link 1 leaves R1 at F1 + 3.15 (upper member) and lands on R2 at F2 (lower member); link 2 leaves R2 at
    F2 + 3.15 and lands on the carriage top.
  * C-track: 6 mm radial x 8 mm axial ring section, axis d, at ring_L mm from GH, circular, inner radius = envelope of
    the upper-arm skin under it (over its angular span and the fit poses) + ring_clear; open over open_w deg centred
    on open_dir (humerus frame: 0 = lateral at rest, 180 = medial, +90 = posterior).
  * carriage (on link 2): 25 mm arc x 12 mm axial x 6 mm radial block straddling the track's outer face (V-wheels).
  * passive slide (humerus-fixed side): 30 x 10 mm block, 6 mm radial, distal of the track at the track's mid angle,
    inner radius = arm-skin envelope under it + ring_clear.
Taken (bench rules): closure solved on the design branch with the evaluator's 10 deg fold/stretch singularity margin,
carriage inside the C span, along each clip (all its frames at 10 fps) no joint jumps > FLIP deg between consecutive
frames, no part pair interference (non-adjacent >= 1 mm, adjacent members outside their shared joint >= 0.15 mm).
In-band samples: every skin-facing surface (strap undersides, hub flat faces, track inner face, carriage overhangs,
slide inner face); contact: every surface (tops, sides, hub walls, ring end faces too) - a non-facing sample inside
the body is appended so the bench counts the pose as contact.
Envelopes are fitted on fit-clip frames + a workspace subsample (_seed2r_skin.py; held-out clips never posed).

    python3 docs/concepts/models/seed-2r-cring.py check          # a few poses, numbers + reasons
    python3 docs/concepts/models/seed-2r-cring.py sweep          # coarse -> refine sweep on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, HERE)
import body_pose as BP                                                     # noqa: E402
import _seed2r_skin as SK                                                  # noqa: E402

ID = "seed-2r-cring"
D2R = math.pi / 180
HUB_R, HUB_H, STACK = 10.0, 12.25, 3.15             # O20 v5 joint
STRAP_W, STRAP_T = 8.0, 3.0                         # link strap section (spec)
TR_RAD, TR_AX = 6.0, 8.0                            # C-track section
CAR_ARC, CAR_AX, CAR_RAD = 25.0, 12.0, 6.0          # carriage
SL_LEN, SL_W, SL_RAD = 30.0, 10.0, 5.0              # passive slide block (under the carriage overhang path)
SP = 2.0                                            # sample grid (1 point / 4 mm2)
RAMP = math.tan(60 * D2R)                           # strap may leave a hub / carriage level at <= 60 deg
SING = 10.0                                         # deg, fold / stretch singularity margin (band evaluator default)
FLIP = 30.0                                         # deg per 10 fps frame: larger joint jump = branch flip / not followed
FP_M = 2.0                                          # footprint margin (mm) around every part for the envelope fit
T_CAP = 200.0                                       # skin farther than this from GH never pushes a part up
OBS_CLR = 1.0                                       # link 2 fitted >= 1 mm over link 1 / R1 hub / C-track where it can pass over them

PARAMS = dict(u1_az=45.0, u1_el=0.0, a1=90.0, a2=90.0, branch=-1, ring_L=140.0, track_c=-40.0, cov=0.97,
              clear=3.0, ring_clear=3.0, q=0.9, q_ring=1.0)
# derived in Design (written back into the params): car_off (deg, carriage turned round the arm from link 2's plane),
# open_dir / open_w (deg, the C opening, humerus frame)
SWEEP = dict(u1_az=(20, 100), u1_el=(20, 75), a1=(60, 110), a2=(60, 110), branch=(-1, 1), ring_L=(60, 140),
             track_c=(-150, 30), cov=(0.9, 1.0), clear=(2, 6), ring_clear=(2, 4), q=(0.6, 1.0), q_ring=(0.9, 1.0))


def bvec(az, el):                                    # unit vector in the scapula frame: az from anterior (+x) to lateral (+z)
    a, e = az * D2R, el * D2R
    return np.array([math.cos(e) * math.cos(a), math.sin(e), math.cos(e) * math.sin(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


# ---------------------------------------------------------------- rig constants
_R = BP._rig()
D_LOC = np.array(_R.L["elbow"], float); D_LOC /= np.linalg.norm(D_LOC)          # humerus long axis (GH -> elbow), local
_H0 = BP.segs(_R.L, _R.s, dict(plane=0, elev=0, axial=0, flex=12, pron=0))[0][2][0]
REF_LOC = _H0.T @ np.array([0.0, 0.0, 1.0]); REF_LOC = unit(REF_LOC - (REF_LOC @ D_LOC) * D_LOC)   # lateral at rest


def frames_of(pose):
    (T, S, H, Fa, Pr), lift = BP.segs(_R.L, _R.s, pose)
    return dict(S=S, H=H, lift=lift)


def chain(SR, HR, p):
    """IK of the 2R + ring for scapula rotations SR (n,3,3) and humerus rotations HR (n,3,3), the design branch.
    -> dict(u1, u2, d, ok, th1, th2, psi (deg, carriage angle on the track in the humerus frame), href, hside)"""
    SR = np.asarray(SR).reshape(-1, 3, 3); HR = np.asarray(HR).reshape(-1, 3, 3)
    u1 = SR @ bvec(p["u1_az"], p["u1_el"]); d = HR @ D_LOC
    a1, a2 = p["a1"] * D2R, p["a2"] * D2R
    c = np.clip((u1 * d).sum(-1), -1, 1); s2 = 1 - c * c + 1e-12
    al = (math.cos(a1) - c * math.cos(a2)) / s2; be = (math.cos(a2) - c * math.cos(a1)) / s2
    pp = al[:, None] * u1 + be[:, None] * d; h2 = 1 - (pp * pp).sum(-1)
    n = unit(np.cross(u1, d)); u2 = pp + p["branch"] * np.sqrt(np.clip(h2, 0, None))[:, None] * n
    ang = np.arccos(c) / D2R
    lo = abs(p["a1"] - p["a2"]) + SING; hi = min(p["a1"] + p["a2"], 360 - p["a1"] - p["a2"]) - SING
    ok = (h2 > 0) & (ang >= lo) & (ang <= hi)
    # joint angles: R1 = u2 about u1 from a scapula-fixed reference; R2 = d about u2 from link 1's plane
    b0 = bvec(p["u1_az"], p["u1_el"]); r0 = np.cross(b0, [0.0, 1.0, 0.0]) if abs(b0[1]) < 0.95 else np.cross(b0, [1.0, 0.0, 0.0])
    r1 = SR @ unit(r0)
    th1 = np.arctan2((np.cross(u1, r1) * u2).sum(-1), (r1 * u2).sum(-1)) / D2R
    r2 = unit(u1 - (u1 * u2).sum(-1, keepdims=True) * u2)
    th2 = np.arctan2((np.cross(u2, r2) * d).sum(-1), (r2 * d).sum(-1)) / D2R
    href = HR @ REF_LOC; hside = np.cross(d, href)
    ea = unit(u2 - (u2 * d).sum(-1, keepdims=True) * d)                   # carriage direction (toward u2, perp. to d)
    psi = np.arctan2((hside * ea).sum(-1), (href * ea).sum(-1)) / D2R
    return dict(u1=u1, u2=u2, d=d, ok=ok, th1=th1, th2=th2, psi=psi, href=href, hside=hside, ea=ea)


def wrap(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def in_span(psi, p, half_arc_deg):
    """carriage (centre psi, half arc) fully on the C track (open over open_w around open_dir)"""
    off = np.abs(wrap(psi - p["open_dir"]))
    return off >= p["open_w"] / 2 + half_arc_deg


# ---------------------------------------------------------------- fit-pose skin (dense samples)
class FitSkin:
    """skin samples of the fit poses: region vertices + unique edge midpoints (~2.5 mm spacing). stride: use every
    stride-th fit pose (the bench's own poses are always kept)."""
    def __init__(self, stride=1, bench=None):
        if not os.path.exists(SK.OUT): SK.build()
        Z = np.load(SK.OUT); sel = np.arange(len(Z["idx"]))
        if stride > 1:
            keep = (sel % stride) == 0
            if bench is not None: keep |= np.isin(Z["idx"], bench.idx)
            sel = sel[keep]
        self.idx = Z["idx"][sel]; self.vid = Z["vid"]; self.V = Z["V"][sel]; self.POSE = Z["POSE"][sel]; self.CID = Z["CID"][sel]
        F = BP.F; m = np.zeros(len(BP.V0), bool); m[self.vid] = True; loc = -np.ones(len(BP.V0), int); loc[self.vid] = np.arange(len(self.vid))
        Fl = loc[F[m[F].all(1)]]
        E = np.unique(np.sort(np.r_[Fl[:, [0, 1]], Fl[:, [1, 2]], Fl[:, [0, 2]]], axis=1), axis=0); self.E = E
        V0 = BP.V0[self.vid]; arm = np.asarray(BP.ARMV)[self.vid]; fore = arm & (V0[:, 1] < -300.0)
        self.s_fore = np.r_[fore, fore[E].any(1)]; self.s_arm = np.r_[arm & ~fore, arm[E].all(1) & ~fore[E].any(1)]
        self.SR, self.HR = frames_arr(self.POSE)
        self.n = len(self.idx)

    def samples(self, k):
        V = self.V[k].astype(float)
        return np.r_[V, 0.5 * (V[self.E[:, 0]] + V[self.E[:, 1]])]


def frames_arr(POSE):
    fr = [frames_of(dict(plane=float(q[0]), elev=float(q[1]), axial=float(q[2]), flex=float(q[3]), pron=float(q[4]))) for q in POSE]
    return np.stack([f["S"][0] for f in fr]), np.stack([f["H"][0] for f in fr])


# ---------------------------------------------------------------- envelope fitting
def _env_strap(S, e1, e2, e3, phis, keep):
    """max in-plane radius of skin samples under a strap station grid phis (rad) on the great circle e1 -> e2."""
    x = S @ e1; y = S @ e2; z = S @ e3; rho = np.hypot(x, y)
    m = keep & (np.abs(z) <= STRAP_W / 2 + FP_M) & (rho < T_CAP) & (rho > 1)
    phi = np.arctan2(y[m], x[m]); rho = rho[m]
    out = np.full(len(phis), -np.inf)
    if not len(phi): return out
    dphi = phis[1] - phis[0]; b = np.round((phi - phis[0]) / dphi).astype(int)
    halo = np.ceil((SP / 2 + FP_M) / np.maximum(rho, 30) / dphi).astype(int)
    for h in range(0, int(halo.max()) + 1):
        for sgn in ((0,) if h == 0 else (-1, 1)):
            bb = b + sgn * h; mm = (bb >= 0) & (bb < len(phis)) & (halo >= h)
            np.maximum.at(out, bb[mm], rho[mm])
    return out


def _env_hub(S, u, keep):
    t = S @ u; r = np.linalg.norm(S - t[:, None] * u, axis=1)
    m = keep & (r <= HUB_R + FP_M) & (t > 0) & (t < T_CAP)
    return float(t[m].max()) if m.any() else -np.inf


def _env_ring(S, d, href, hside, t0, t1, psi_lo, psi_hi, keep):
    """max radial distance from the d axis of arm skin samples with axial t in [t0, t1] and angle within [psi_lo, psi_hi]
    (deg, psi_hi may exceed 180: handled by wrapping relative to psi_lo)"""
    t = S @ d; m = keep & (t >= t0) & (t <= t1)
    if not m.any(): return -np.inf
    P = S[m] - t[m, None] * d; rr = np.linalg.norm(P, axis=1)
    ps = np.arctan2(P @ hside, P @ href) / D2R
    rel = (ps - psi_lo) % 360.0; mm = (rel <= (psi_hi - psi_lo)) & (rr < 120)
    return float(rr[mm].max()) if mm.any() else -np.inf


NSEC = 72                                                                    # 5 deg sectors round the humerus axis


def _env_ring_sec(S, d, href, hside, t0, t1, keep):
    """per 5-deg sector (psi from href toward hside, sector 0 = [0, 5) deg): max radial distance from the d axis of arm
    skin samples with axial t in [t0, t1] (-inf where none)"""
    out = np.full(NSEC, -np.inf); t = S @ d; m = keep & (t >= t0) & (t <= t1)
    if not m.any(): return out
    P = S[m] - t[m, None] * d; rr = np.linalg.norm(P, axis=1); ok = rr < 120
    ps = np.arctan2(P @ hside, P @ href) / D2R
    b = (np.floor((ps % 360.0) / (360.0 / NSEC)).astype(int)) % NSEC
    np.maximum.at(out, b[ok], rr[ok]); return out


def sec_mask(c, half):
    """sectors overlapping the arc [c - half, c + half] deg"""
    lo = (np.arange(NSEC) * 360.0 / NSEC); hi = lo + 360.0 / NSEC; mid = 0.5 * (lo + hi)
    return np.abs(wrap(mid - c)) <= half + 180.0 / NSEC


def cover(ps, frac):
    """smallest circular arc (deg) holding frac of the angles ps -> (width, centre)"""
    a = np.sort(np.asarray(ps) % 360.0); n = len(a); k = max(1, int(np.ceil(frac * n)))
    a2 = np.r_[a, a + 360.0]; w = a2[k - 1:k - 1 + n] - a2[:n]; j = int(np.argmin(w)); return float(w[j]), float((a2[j] + w[j] / 2) % 360.0)


def agg(vals, q):
    v = np.asarray(vals, float); v = v[np.isfinite(v)] if v.ndim == 1 else v
    if q >= 1.0: return np.max(v, axis=0)
    return np.quantile(v, q, axis=0)


def rot_about(axis, v, ang):
    """rotate v (n,3) about unit axis (n,3) by ang (rad, scalar or (n,))"""
    ang = np.broadcast_to(np.asarray(ang, float), v.shape[:1])[:, None]
    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * (axis * v).sum(-1, keepdims=True) * (1 - np.cos(ang))


class Design:
    """fitted shape of one parameter set: hub faces F1, F2, strap profiles r1(phi), r2(phi), track / slide radii."""
    def __init__(self, p, fit):
        self.p = p = dict(PARAMS, **p)
        C = chain(fit.SR, fit.HR, p); ok = C["ok"]; self.fit_ok = float(ok.mean()); self.n_fit = int(ok.sum())
        L = p["ring_L"]; q = p["q"]; c = p["clear"]
        self.n1 = max(8, int(round(p["a1"] * D2R * 70 / 1.0))); self.phi1 = np.linspace(0, p["a1"] * D2R, self.n1)
        ks = np.nonzero(ok)[0]
        H1, H2, E1, RI, RS = [], [], [], [], []
        for k in ks:                                                         # pass 1: hubs, link 1, arm skin round the track / slide
            S = fit.samples(k); keep = ~fit.s_fore; arm = fit.s_arm
            u1, u2, d = C["u1"][k], C["u2"][k], C["d"][k]
            H1.append(_env_hub(S, u1, keep)); H2.append(_env_hub(S, u2, keep))
            e2 = unit(u2 - (u2 @ u1) * u1); E1.append(_env_strap(S, u1, e2, np.cross(u1, e2), self.phi1, keep))
            RI.append(_env_ring_sec(S, d, C["href"][k], C["hside"][k], L - TR_AX / 2 - FP_M, L + TR_AX / 2 + FP_M, arm))
            RS.append(_env_ring_sec(S, d, C["href"][k], C["hside"][k], L + TR_AX / 2 - FP_M, L + TR_AX / 2 + SL_LEN + FP_M, arm))
        self.F1 = float(agg(H1, q)) + c; self.F2 = float(agg(H2, q)) + c
        # C-track window: centred on track_c (humerus frame); it holds the carriage over a share cov of the fit poses;
        # car_off turns the carriage round the arm so its angle range is centred on the track (link 2 lands there)
        w_cov, c_cov = cover(C["psi"][ok], p["cov"]); p["car_off"] = float(wrap(p["track_c"] - c_cov))
        RI = np.where(np.isfinite(np.array(RI)), np.array(RI), 0.0); RS = np.where(np.isfinite(np.array(RS)), np.array(RS), 0.0)
        Rin = 70.0
        for _ in range(3):
            car_half = (CAR_ARC / 2) / (Rin + TR_RAD) / D2R; span = min(358.0, w_cov + 2 * car_half + 2.0)
            Rin = float(agg(RI[:, sec_mask(p["track_c"], span / 2 + 4.0)].max(1), p["q_ring"])) + p["ring_clear"]
        self.Rin = Rin; self.w_cov = w_cov; p["open_dir"] = float(wrap(p["track_c"] + 180.0)); p["open_w"] = 360.0 - span
        self.Rs = float(agg(RS[:, sec_mask(p["track_c"], (SL_W / 2 + FP_M) / Rin / D2R)].max(1), p["q_ring"])) + p["ring_clear"]
        # carriage: on the track's outer face at psi(e_a) + car_off; link 2 = strap on the great circle u2 -> carriage top
        self.Rc = self.Rin + TR_RAD + CAR_RAD
        a2 = p["a2"] * D2R; dl = p["car_off"] * D2R
        cu = L * math.cos(a2) + self.Rc * math.sin(a2) * math.cos(dl); self.hc = math.hypot(L, self.Rc)
        self.phic = math.acos(max(-1.0, min(1.0, cu / self.hc)))
        self.n2 = max(8, int(round(self.phic * 110 / 1.0))); self.phi2 = np.linspace(0, self.phic, self.n2)
        E1 = np.array(E1); env1 = agg(np.where(np.isfinite(E1), E1, 0), q) + c
        s0 = math.asin(min(1, HUB_R / self.F1)); s1 = p["a1"] * D2R - math.asin(min(1, HUB_R / self.F2))
        self.r1 = self._profile(self.phi1, env1, s0, self.F1 + STACK, s1, self.F2); self.lim1 = (s0, s1)
        self.car_half = (CAR_ARC / 2) / (self.Rin + TR_RAD) / D2R
        # pass 2: link 2 over the skin (+ clear) AND over what it can sweep across (+ OBS_CLR): link 1 and the R1 hub
        # (they turn under it about u2 / u1), the C-track (a full ring: the arm turns inside link 2's frame)
        E2 = []; th = np.linspace(0, 2 * np.pi, int(2 * np.pi * (self.Rin + TR_RAD) / SP), endpoint=False)
        tt = _grid(L - TR_AX / 2, L + TR_AX / 2, SP); TH, TT = np.meshgrid(th, tt); TH, TT = TH.ravel(), TT.ravel()
        for k in ks:
            S = fit.samples(k); keep = ~fit.s_fore
            u1, u2, d, cd = C["u1"][k], C["u2"][k], C["d"][k], self.cdir(C, k)
            f2 = unit(cd - (cd @ u2) * u2); f3 = np.cross(u2, f2)
            e_sk = _env_strap(S, u2, f2, f3, self.phi2, keep) + c
            e2 = unit(u2 - (u2 @ u1) * u1); st1 = _strap(u1, e2, np.cross(u1, e2), self.phi1, self.r1, *self.lim1); h1 = _hub(u1, self.F1)
            ring = TT[:, None] * d + (self.Rin + TR_RAD) * (np.cos(TH)[:, None] * C["href"][k] + np.sin(TH)[:, None] * C["hside"][k])
            O = np.r_[st1.other, st1.face, h1.other]
            e_ob = _env_strap(O, u2, f2, f3, self.phi2, np.ones(len(O), bool)) + OBS_CLR
            e_rg = _env_strap(ring, u2, f2, f3, self.phi2, np.ones(len(ring), bool)) + OBS_CLR
            e_rg[self.phi2 > self.phic - 4.0 / max(self.hc, 1)] = -np.inf          # the strap lands on the carriage there
            E2.append(np.maximum(np.maximum(e_sk, e_ob), e_rg))
        E2 = np.array(E2); env2 = agg(np.where(np.isfinite(E2), E2, 0), q)
        s0 = math.asin(min(1, HUB_R / self.F2))
        self.r2 = self._profile(self.phi2, env2, s0, self.F2 + STACK, self.phic, self.hc); self.lim2 = (s0, self.phic)
        self.ok_geom = bool(self.phic > s0 + 5 * D2R and s1 > s0 + 3 * D2R)

    def cdir(self, C, k):
        """unit direction GH -> carriage top centre for chain solution k"""
        e = rot_about(C["d"][k][None], C["ea"][k][None], self.p["car_off"] * D2R)[0]
        return unit(self.p["ring_L"] * C["d"][k] + self.Rc * e)

    @staticmethod
    def _profile(phis, env, s0, h0, s1, h1):
        r = env.copy(); rho = np.maximum(env, 40)
        a = np.maximum(0, phis - s0) * rho; b = np.maximum(0, s1 - phis) * rho
        r = np.maximum(r, h0 - RAMP * a); r = np.maximum(r, h1 - RAMP * b)
        return r                                                            # (a strap landing above the carriage top keeps a riser)

    # ---- parts in world coordinates for one pose (C: chain() of that pose, index 0)
    def parts(self, C):
        p = self.p; L = p["ring_L"]; out = {}
        u1, u2, d, href, hside = C["u1"][0], C["u2"][0], C["d"][0], C["href"][0], C["hside"][0]
        psi = float(C["psi"][0]) + p["car_off"]
        out["hub1"] = _hub(u1, self.F1); out["hub2"] = _hub(u2, self.F2)
        e2 = unit(u2 - (u2 @ u1) * u1); out["strap1"] = _strap(u1, e2, np.cross(u1, e2), self.phi1, self.r1, *self.lim1)
        cd = self.cdir(C, 0); f2 = unit(cd - (cd @ u2) * u2); self._f2 = f2
        out["strap2"] = _strap(u2, f2, np.cross(u2, f2), self.phi2, self.r2, *self.lim2)
        hw = p["open_w"] / 2
        out["track"] = _ring(d, href, hside, L - TR_AX / 2, L + TR_AX / 2, self.Rin, self.Rin + TR_RAD, p["open_dir"] + hw, p["open_dir"] + 360 - hw)
        mid = p["open_dir"] + 180; dws = (SL_W / 2) / self.Rs / D2R
        out["slide"] = _ring(d, href, hside, L + TR_AX / 2, L + TR_AX / 2 + SL_LEN, self.Rs, self.Rs + SL_RAD, mid - dws, mid + dws)
        ch = self.car_half; R0 = self.Rin + TR_RAD
        out["carriage"] = _ring(d, href, hside, L - CAR_AX / 2, L + CAR_AX / 2, R0, R0 + CAR_RAD, psi - ch, psi + ch, car=(L - TR_AX / 2, L + TR_AX / 2))
        return out


# ---------------------------------------------------------------- part primitives: samples (face, other) + inside test
def _grid(a, b, step):
    n = max(2, int(math.ceil((b - a) / step)) + 1)
    return np.linspace(a, b, n)


class Part:
    def __init__(self, face, other, inside):
        self.face = face; self.other = other; self.inside = inside

    @property
    def all(self):
        return np.r_[self.face, self.other]


def _hub(u, F):
    tmp = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    a = unit(np.cross(u, tmp)); b = np.cross(u, a)
    g = _grid(-HUB_R, HUB_R, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= HUB_R ** 2; X, Y = X[m], Y[m]
    face = F * u + X[:, None] * a + Y[:, None] * b
    top = (F + HUB_H) * u + X[:, None] * a + Y[:, None] * b
    th = np.linspace(0, 2 * np.pi, int(2 * np.pi * HUB_R / SP), endpoint=False); hh = _grid(F, F + HUB_H, SP)
    TH, HH = np.meshgrid(th, hh); TH, HH = TH.ravel(), HH.ravel()
    wall = HH[:, None] * u + HUB_R * (np.cos(TH)[:, None] * a + np.sin(TH)[:, None] * b)

    def inside(P, m):
        t = P @ u; r = np.linalg.norm(P - t[:, None] * u, axis=1)
        return (t >= F - m) & (t <= F + HUB_H + m) & (r <= HUB_R + m)
    return Part(face, np.r_[top, wall], inside)


def _strap(e1, e2, e3, phis, r, s0, s1):
    if s1 <= s0: s1 = s0 + 1e-3
    rm = float(np.interp(0.5 * (s0 + s1), phis, r)); ph = _grid(s0, s1, SP / max(rm, 30))
    rr = np.interp(ph, phis, r); w = np.arange(-STRAP_W / 2 + SP / 2, STRAP_W / 2, SP)
    g = np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2
    face = (rr[:, None, None] * g[:, None, :] + w[None, :, None] * e3).reshape(-1, 3)
    top = ((rr + STRAP_T)[:, None, None] * g[:, None, :] + w[None, :, None] * e3).reshape(-1, 3)
    side = np.r_[((rr + STRAP_T / 2)[:, None] * g + STRAP_W / 2 * e3), ((rr + STRAP_T / 2)[:, None] * g - STRAP_W / 2 * e3)]

    def inside(P, m):
        x = P @ e1; y = P @ e2; z = P @ e3; rho = np.hypot(x, y); ph_ = np.arctan2(y, x)
        rp = np.interp(ph_, phis, r)
        return (ph_ >= s0 - m / np.maximum(rho, 1)) & (ph_ <= s1 + m / np.maximum(rho, 1)) & (np.abs(z) <= STRAP_W / 2 + m) & (rho >= rp - m) & (rho <= rp + STRAP_T + m)
    pt = Part(face, np.r_[top, side], inside); pt.phi = ph; pt.e = (e1, e2, e3); pt.n_w = len(w)
    return pt


def _ring(d, href, hside, t0, t1, R0, R1, ps0, ps1, car=None):
    """ring sector about d: axial [t0, t1], radial [R0, R1], angle [ps0, ps1] deg (humerus frame). car = (ta, tb): a
    carriage straddling the track over [ta, tb]: only its overhangs face the skin."""
    ps = _grid(ps0 * D2R, ps1 * D2R, SP / R0); tt = _grid(t0, t1, SP)
    rad = lambda R, P, T: T[..., None] * d + R * (np.cos(P)[..., None] * href + np.sin(P)[..., None] * hside)
    PP, TT = np.meshgrid(ps, tt); PP, TT = PP.ravel(), TT.ravel()
    inner = rad(R0, PP, TT); outer = rad(R1, PP, TT)
    rr = _grid(R0, R1, SP); P2, R2 = np.meshgrid(ps, rr); P2, R2 = P2.ravel(), R2.ravel()
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


# ---------------------------------------------------------------- interference
NONADJ = [("hub1", "hub2"), ("hub1", "strap2"), ("hub1", "carriage"), ("hub1", "track"), ("hub1", "slide"),
          ("strap1", "track"), ("strap1", "slide"), ("hub2", "track"), ("hub2", "slide"), ("strap1", "carriage")]
ADJ = [("strap1", "strap2"), ("hub2", "carriage"), ("strap2", "track"), ("strap2", "slide"), ("carriage", "slide")]


def interfere(parts, u2, f2, phic):
    """first interfering pair or None. Adjacent members (sharing a joint) are exempt inside the joint: strap1 / strap2
    within the R2 hub radius + 1 mm, strap2 within 3 mm of the carriage it lands on."""
    for a, b in NONADJ:
        A, B = parts[a], parts[b]
        if B.inside(A.all, 1.0).any() or A.inside(B.all, 1.0).any(): return f"{a}/{b}"
    for a, b in ADJ:
        A, B = parts[a].all, parts[b].all
        if a == "strap1" and b == "strap2":
            ra = np.linalg.norm(A - (A @ u2)[:, None] * u2, axis=1); rb = np.linalg.norm(B - (B @ u2)[:, None] * u2, axis=1)
            A = A[ra > HUB_R + 1.0]; B = B[rb > HUB_R + 1.0]
        if a == "strap2":
            A = A[np.arctan2(A @ f2, A @ u2) < phic - 3.0 / 120.0]
        if parts[b].inside(A, 0.15).any() or parts[a].inside(B, 0.15).any(): return f"{a}/{b}"
    return None


# ---------------------------------------------------------------- model on the bench
PART_ORDER = ("hub1", "hub2", "strap1", "strap2", "track", "carriage", "slide")
_CLIPS = []


def clip_frames():
    """every frame of every fit clip in time order: [(name, dataset indices, SR, HR)] (cached)"""
    if not _CLIPS:
        import concept_bench as CB
        Zp = CB._poses_all(); names = list(Zp["NAMES"]); cid = Zp["CID"]; P = Zp["POSE"]
        for n in CB.FIT:
            ix = np.nonzero(cid == names.index(n))[0]; SR, HR = frames_arr(P[ix]); _CLIPS.append((n, ix, SR, HR))
    return _CLIPS


class Model:
    def __init__(self, p, fit, bench):
        self.D = Design(p, fit); self.p = self.D.p; self.B = bench
        self._prep_clips()

    def _prep_clips(self):
        """continuity on every frame of every fit clip (10 fps), design branch: frame followed iff closure ok, carriage on
        the track, and no joint jumps > FLIP since the last followed frame. -> {dataset index: (ok, reason)}"""
        self.status = {}; self.max_step = 0.0
        for n, ix, SR, HR in clip_frames():
            C = chain(SR, HR, self.p); psc = C["psi"] + self.p["car_off"]
            spn = in_span(psc, self.p, self.D.car_half + 1.0)
            last = None
            for k, j in enumerate(ix):
                if not C["ok"][k]: self.status[int(j)] = (False, "closure"); continue
                if not spn[k]: self.status[int(j)] = (False, "carriage off track"); continue
                q = np.array([C["th1"][k], C["th2"][k], psc[k]])
                if last is not None:
                    st = float(np.abs(wrap(q - last)).max())
                    if st > FLIP: self.status[int(j)] = (False, "flip"); last = q; continue
                    self.max_step = max(self.max_step, st)
                self.status[int(j)] = (True, ""); last = q

    def metal(self, i, parts_out=None):
        """skin-facing samples of pose i (bench index), + the worst non-facing sample when it is inside the body; None
        and the reason when the pose is not taken"""
        B = self.B; j = int(B.idx[i]); fr = B.frames(i); p = self.p
        C = chain(fr["S"][0][None], fr["H"][0][None], p)
        if B.kind[i] == "clip":
            ok, why = self.status.get(j, (False, "missing"))
            if not ok: return None, why
        else:
            if not C["ok"][0]: return None, "closure"
            if not in_span(C["psi"] + p["car_off"], p, self.D.car_half + 1.0)[0]: return None, "carriage off track"
        if not self.D.ok_geom: return None, "geometry"
        parts = self.D.parts(C)
        why = interfere(parts, C["u2"][0], self.D._f2, self.D.phic)
        if why: return None, "interference " + why
        face = np.concatenate([parts[k].face for k in PART_ORDER])
        other = np.concatenate([parts[k].other for k in PART_ORDER])
        lab = np.concatenate([np.full(len(parts[k].face), n) for n, k in enumerate(PART_ORDER)])
        labo = np.concatenate([np.full(len(parts[k].other), n) for n, k in enumerate(PART_ORDER)])
        do = B.dist(i, other); self._last_lab = lab; self._worst_other = None
        if do.min() < 0:
            face = np.r_[face, other[np.argmin(do)][None]]; self._last_lab = np.r_[lab, labo[np.argmin(do)]]
        if parts_out is not None: parts_out.update(parts)
        return face, ""

    def run(self):
        B = self.B; B.reset(); why = {}; per = {k: [0, 0, 0] for k in PART_ORDER}; cpart = {}
        for i in range(len(B.poses)):
            P, w = self.metal(i)
            if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
            d = B.record(i, P); lab = self._last_lab
            if d.min() < 0:
                why["contact"] = why.get("contact", 0) + 1
                for n in np.unique(lab[d < 0]): cpart[PART_ORDER[n]] = cpart.get(PART_ORDER[n], 0) + 1
            elif B.kind[i] == "clip":
                for n, k in enumerate(PART_ORDER):
                    m = lab == n; per[k][0] += int(m.sum()); per[k][1] += int(((d >= 2) & (d <= 14) & m).sum()); per[k][2] += int(((d >= 2) & (d <= 10) & m).sum())
        r = B.report(); r["why"] = why; r["contact_parts"] = cpart
        tot = sum(v[0] for v in per.values()) or 1
        r["parts"] = {k: dict(share=round(v[0] / tot, 3), ib14=round(v[1] / max(1, v[0]), 3), ib10=round(v[2] / max(1, v[0]), 3)) for k, v in per.items()}
        r["max_step"] = round(self.max_step, 1)
        return r


def metal(pose, frames, params, _cache={}):
    """public hook (task API): metal sample points (k, 3) of the concept for one bench pose, or None. Needs the bench
    index, so it looks the pose up in the bench it was built for (pass params['_bench'])."""
    B = params["_bench"]; key = json.dumps({k: v for k, v in params.items() if not k.startswith("_")}, sort_keys=True)
    if key not in _cache: _cache.clear(); _cache[key] = Model({k: v for k, v in params.items() if not k.startswith("_")}, FitSkin(), B)
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


# ---------------------------------------------------------------- sweep
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def evaluate(p, fit, B):
    t = time.time(); M = Model(p, fit, B); r = M.run()
    D = M.D
    r.update(F1=round(D.F1, 1), F2=round(D.F2, 1), Rin=round(D.Rin, 1), Rs=round(D.Rs, 1), fit_ok=round(D.fit_ok, 3), secs=round(time.time() - t, 1),
             phic=round(D.phic / D2R, 1), w_cov=round(D.w_cov, 1), derived=dict(car_off=round(D.p["car_off"], 1), open_dir=round(D.p["open_dir"], 1), open_w=round(D.p["open_w"], 1)))
    return r


def sweep(configs, B, fit, out=SWEEP_OUT, tag=""):
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r = evaluate(p, fit, B)
        except Exception as e: print("ERR", p, e, flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=dict(F1=r["F1"], F2=r["F2"], Rin=r["Rin"], Rs=r["Rs"]),
                   mode=r["mode"], stage=tag)
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | F1 {r['F1']} F2 {r['F2']} Rin {r['Rin']} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in ('u1_az', 'u1_el', 'a1', 'a2', 'branch', 'ring_L', 'track_c', 'cov', 'clear', 'ring_clear', 'q', 'q_ring')), flush=True)
    return rows


if __name__ == "__main__":
    import concept_bench as CB
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40); fit = FitSkin()
        print(evaluate(dict(PARAMS), fit, B))
