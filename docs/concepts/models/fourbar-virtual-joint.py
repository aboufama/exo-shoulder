"""fourbar-virtual-joint: polycentric 3R - the champion's J2 hub replaced by a spherical four-bar 'virtual joint'
(catalogue entry `fourbar-virtual-joint`, docs/concepts/catalogue.json; write-up docs/concepts/fourbar-virtual-joint.md).

Topology (scapula handler -> user's upper-arm cuff), every axis through the GH centre:
    S --J1 (ACTIVE, O20 hub, axis b fixed in the scapula frame)--> L1 (V frame: straps b->p1, b->p2)
      --pins p1 (ACTIVE, rocker-1 angle phi) and p2 (passive)--> rockers R1 (p1->q1), R2 (p2->q2), two-force straps
      --pins q1, q2 (passive)--> L2 = coupler (V frame: straps q1->W, q2->W)
      --J3 (ACTIVE, O20 hub, axis W fixed in the humerus)--> arm-end neck strap (baseline's 25 deg) -> cuff.
DOF: spherical Gruebler, 6 bodies (S, L1, R1, R2, L2, arm), 6 revolutes: M = 3*(6-1) - 2*6 = 3. The four-bar loop
has one DOF (sensed at p1 = the virtual J2 coordinate); p2, q1, q2 are set by the loop's closure. 3 active, 3 passive,
no spare coordinate: given the arm, the loop coordinate phi is fixed by angle(b, W) (see below), theta1 by the
azimuth of W about b, theta3 by the arm's twist about W.

Kinematics (exact, derived here; no 2-D grid search needed): with L1 at theta1 = 0, the coupler's pose is a function
of phi alone, so W_L(phi) = R_L2(phi) W_r, and rot(b, theta1) preserves angles to b, so closure <=> G(phi) := b.W_L(phi)
= b.y (y = the arm's W direction), then theta1 = the azimuth from W_L(phi) to y about b (closed form). G is tabulated on
a 0.25 deg grid; the design's branch is the piece of G around the reference configuration (phi = 0) on which the loop
assembles in its reference mode, both transmission angles (rocker vs coupler great circle at q1, q2) stay in
[tmin, 180 - tmin], pins on different bodies stay >= pin_sep apart and G is monotone. On that piece the root is unique,
so the solution is a continuous function of the pose (no branch flips by construction; still checked on the full
10 fps fit clips, jump <= 25 deg per frame on any joint). At an end of the piece that is a fold of G (b, virtual J2,
W coplanar - the 3R's straight / folded singularity) the band keeps `sing` deg away, as tools/concept_baseline.py
(tri_ok, sing_deg 10). The 3R champion is mode '3r' of the same code: G(phi) = b.rot(J2, phi) W_r.

Geometry (idealised, every part at its real size, sampled like tools/concept_baseline.py: strap undersides on a 2 mm
grid at r_ref 70 mm (~1 point / 4 mm2), discs on a 2.5 mm grid; 8 x 3 mm straps; O20 hub discs r 10 (crown 12.25 mm
above the lower member's skin face, upper member at +up); O14 pin discs r 7 (P14: crown 8 at up 3.15); `up` = 3.15
(docs/HARDWARE.md v5: upper hub underside 0.15 over the 3 mm lower plate)):
  * every sample's underside radius is fixed in its body (a rigid part): the pct-th percentile, over the kinematically
    valid bench poses, of its obstacle radius = max(outermost skin radius under it + clear, top of an earlier part of
    another body overlapping it laterally + 1 mm) - the baseline's percentile rule plus 'rides over'; joint ends sit
    on their joint (lower member at the disc level, upper member at disc + up) within the joint radius, then a 60 deg
    ramp limit along every strap; discs are flat at their max.
  * parts of adjacent bodies are exempt from the clearance check only within joint radius + 2 mm of their joint.
Taken (bench rules): closure (residual < 0.5 deg), inside the band with its margins, every pin inside its range
(= the transmission-angle piece), no two non-adjacent parts closer than 1 mm (lateral < 1 mm and radial < 1 mm),
continuity on the full fit clips; then no metal inside the body (bench). Held-out clips are never posed.

    python3 docs/concepts/models/fourbar-virtual-joint.py check [n_clip n_ws]   # kinematics + a few poses
    python3 docs/concepts/models/fourbar-virtual-joint.py calib                 # 3R mode vs tools/concept_baseline.py
    python3 docs/concepts/models/fourbar-virtual-joint.py sweep                 # coarse -> refine on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(REPO) if os.path.basename(REPO) == "docs" else REPO
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "fourbar-virtual-joint"
D2R = math.pi / 180
CACHE = os.path.join(REPO, ".cache", "concept_models", ID)
HUB_R, PIN_R = 10.0, 7.0                     # O20 hub, O14 pin
HUB_CROWN, PIN_CROWN = 12.25, 8.0            # above the lower member's skin face, at up = 3.15
T_STRAP = 3.0
R_REF, SP, DSP = 70.0, 2.0, 2.5              # baseline sampling (strap grid, disc grid)
RAMP = math.tan(60 * D2R)
FLIP = 25.0                                  # deg per 10 fps frame (K2)
GAP = 1.0                                    # mm clearance between parts of non-adjacent bodies
RESID = 0.5                                  # deg closure residual

# seed = the baseline champion (tools/concept_baseline.py CHAMP = r20 s1414 #4): J1 axis b, arm axis W, arcs a0, a1
PARAMS = dict(mode="4bar", az=2.4305071427308924, el=80.67633718429899, a0=76.90180446920043, a1=66.74921235407174,
              wd=86.32769021001913, wa=21.829657347343378, branch=-1,
              d_up=20.0, d_dn=20.0, s_up=12.0, s_dn=12.0, crossed=1, skew=0.0, shape="V", l2_over=0,
              sing=10.0, tmin=25.0, pin_sep=15.0, pct=90, clear=2.0, up=3.15, width=8.0, neck_deg=25.0)
SWEEP = dict(d_up=(10, 35), d_dn=(10, 35), s_up=(6, 20), s_dn=(6, 20), crossed=(0, 1), skew=(-6, 6), shape=("V", "T"),
             l2_over=(0, 1), az=(-13, 18), el=(66, 90), wd=(71, 101), wa=(7, 37), pct=(80, 100))


# ------------------------------------------------------------------------------------------------ small geometry
def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def bvec(az, el):                                    # scapula frame (tools/concept_baseline.py)
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):                                # humerus frame (evaluator's HG convention)
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def rot(a, t):
    """rotation(s) about unit axis a (3,) by angle(s) t (rad) -> (..., 3, 3)"""
    a = unit(np.asarray(a, float)); t = np.asarray(t, float)[..., None, None]
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(t) * K + (1 - np.cos(t)) * (K @ K)


def mv(p, t, ang_deg):
    """move point p along the unit tangent t by ang_deg on the unit sphere"""
    a = ang_deg * D2R
    return unit(math.cos(a) * p + math.sin(a) * t)


def angle(u, v):
    return np.arccos(np.clip((u * v).sum(-1), -1, 1))


def circ_int(c1, r1, c2, r2, sign):
    """tools/concept_baseline.py: intersection of the circles (c1, r1), (c2, r2) on the unit sphere, side `sign`"""
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (np.cos(r1) - dd * np.cos(r2)) / den; b = (np.cos(r2) - dd * np.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return unit(p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n), h2 > 0


def frame2(u, v):
    """orthonormal frame (columns) from u and the part of v across u -> (..., 3, 3)"""
    e1 = unit(u); e2 = unit(v - (v * e1).sum(-1, keepdims=True) * e1); e3 = np.cross(e1, e2)
    return np.stack([e1, e2, e3], -1)


def signed_angle(u, v, ax):
    """signed angle about ax from u to v (both projected across ax)"""
    return np.arctan2((ax * np.cross(u, v)).sum(-1), (u * v).sum(-1) - (u * ax).sum(-1) * (v * ax).sum(-1))


def wrap(x):
    return (x + math.pi) % (2 * math.pi) - math.pi


# ------------------------------------------------------------------------------------------------ poses
class Poses:
    """bench poses + the full fit clips (10 fps) from the evaluator's pose file (held-out clips excluded); the same
    scapula / humerus rotations (RS, HG) as tools/concept_baseline.py"""
    def __init__(self, n_clip=60, n_ws=160):
        B = CB.Bench(n_clip, n_ws); Z = CB._poses_all(); names = list(Z["NAMES"]); fit_ids = [names.index(n) for n in CB.FIT]
        self.B = B; self.idx = B.idx; self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); self.HGr = self.HG[0]                         # reference = first fit-clip frame
        self.clip_rows = {}
        for c in fit_ids:
            j = np.nonzero(Z["CID"] == c)[0]; self.clip_rows[names[c]] = j[np.argsort(Z["FI"][j])]
        self.HGall = Z["HG"].astype(float)
        f0 = B.frames(0); self.C = (self.RS[0] @ self.HG[0]).T @ f0["H"][0]          # rig humerus = RS HG C (constant)


_P = {}


def get_poses(n_clip=60, n_ws=160):
    k = (n_clip, n_ws)
    if k not in _P: _P[k] = Poses(n_clip, n_ws)
    return _P[k]


# ------------------------------------------------------------------------------------------------ kinematics
def design(p, HGr):
    """joint axes at the reference configuration (scapula frame) and the loop curve G(phi) with its design piece"""
    b = bvec(p["az"], p["el"]); W0 = w_dir(p["wd"], p["wa"]); Wr = HGr @ W0
    J2, ex = circ_int(b, p["a0"] * D2R, Wr, p["a1"] * D2R, float(p["branch"]))
    d = dict(mode=p["mode"], b=b, W0=W0, Wr=Wr, J2=J2, ok=False, why="")
    if not ex: d["why"] = "champion arcs do not close at the reference pose"; return d
    ar = HGr @ np.array([0.0, -1.0, 0.0]); d["ar"] = ar
    e0 = unit(np.cross(W0, np.array([1.0, 0.0, 0.0]))); d["e0"] = e0; d["er"] = HGr @ e0
    if p["mode"] == "3r":
        pass
    else:
        m_up = unit(b - (b @ J2) * J2); m_dn = unit(Wr - (Wr @ J2) * J2)
        s_up_hat = unit(np.cross(J2, m_up)); s_dn_hat = unit(np.cross(m_dn, J2))
        pc = mv(J2, m_up, p["d_up"]); p1 = mv(pc, s_up_hat, p["s_up"]); p2 = mv(pc, s_up_hat, -p["s_up"])
        sg = -1.0 if p["crossed"] else 1.0
        q1c = mv(J2, m_dn, p["d_dn"] + p["skew"]); q2c = mv(J2, m_dn, p["d_dn"] - p["skew"])
        q1 = mv(q1c, s_dn_hat, sg * p["s_dn"]); q2 = mv(q2c, s_dn_hat, -sg * p["s_dn"])
        d.update(p1=p1, p2=p2, q1=q1, q2=q2, lam1=float(angle(p1, q1)), lam2=float(angle(p2, q2)), c12=float(angle(q1, q2)))
        # same-body pin pairs: discs (r 7) at least 1 mm apart at r_ref; different bodies: pin_sep (checked on the curve)
        if min(angle(p1, p2), angle(q1, q2)) * R_REF < 2 * PIN_R + GAP or min(d["lam1"], d["lam2"]) < p["pin_sep"] * D2R:
            d["why"] = "pins too close"; return d
        ref = d["q2"]; d["sigma"] = None
        for sgn in (1.0, -1.0):
            q2t, okq = circ_int(p2, d["lam2"], q1, d["c12"], sgn)
            if okq and angle(q2t, ref) < 1e-6: d["sigma"] = sgn
        if d["sigma"] is None: d["why"] = "four-bar does not assemble at the reference"; return d
    ph = np.arange(-180, 180, 0.25) * D2R
    E = loop_eval(d, ph); G = E["WL"] @ b
    ok = E["ok"].copy()
    if p["mode"] != "3r":
        mu = np.stack([E["mu1"], E["mu2"]], 1) / D2R
        ok &= (mu.min(1) >= p["tmin"]) & (mu.max(1) <= 180 - p["tmin"]) & (E["sep"] >= p["pin_sep"] * D2R)
    i0 = int(np.argmin(np.abs(ph)))
    dG = np.gradient(G); s0 = np.sign(dG[i0])
    d.update(ph=ph, G=G)
    if not ok[i0] or s0 == 0: d["why"] = "reference configuration outside the transmission / separation limits"; return d
    lo = hi = i0
    while lo > 0 and ok[lo - 1] and np.sign(dG[lo - 1]) == s0: lo -= 1
    while hi < len(ph) - 1 and ok[hi + 1] and np.sign(dG[hi + 1]) == s0: hi += 1
    th = np.arccos(np.clip(G, -1, 1)) / D2R
    tlo, thi = th[lo:hi + 1].min(), th[lo:hi + 1].max()
    ends = []
    for j, nxt in ((lo, lo - 1), (hi, hi + 1)):
        fold = 0 <= nxt < len(ph) and ok[nxt] and np.sign(dG[nxt]) != s0
        ends.append("fold" if fold else "limit")
        if fold:
            if abs(th[j] - tlo) <= abs(th[j] - thi): tlo = th[j] + p["sing"]
            else: thi = th[j] - p["sing"]
    d.update(ok=thi > tlo, ia=lo, ib=hi, tlo=tlo, thi=thi, ends=ends, phi_lo=ph[lo] / D2R, phi_hi=ph[hi] / D2R)
    if not d["ok"]: d["why"] = "empty band"
    return d


def loop_eval(d, ph):
    """loop at L1 = identity for rocker-1 angles ph (rad) -> dict(R (n,3,3) coupler rotation, WL, Q1, Q2, psi2, mu1, mu2, ok)"""
    ph = np.atleast_1d(np.asarray(ph, float))
    if d["mode"] == "3r":
        R = rot(d["J2"], ph); WL = R @ d["Wr"]
        return dict(R=R, WL=WL, ok=np.ones(len(ph), bool))
    p1, p2, q1, q2 = d["p1"], d["p2"], d["q1"], d["q2"]
    Q1 = rot(p1, ph) @ q1
    Q2, ok = circ_int(np.broadcast_to(p2, Q1.shape), d["lam2"], Q1, d["c12"], d["sigma"])
    R = frame2(Q1, Q2) @ frame2(q1, q2).T
    WL = R @ d["Wr"]
    ta = unit(p1 - (Q1 @ p1)[:, None] * Q1); tb = unit(Q2 - (Q1 * Q2).sum(1)[:, None] * Q1)
    tc = unit(p2 - (Q2 @ p2)[:, None] * Q2); td = unit(Q1 - (Q1 * Q2).sum(1)[:, None] * Q2)
    mu1 = angle(ta, tb); mu2 = angle(tc, td)
    sep = np.minimum(angle(np.broadcast_to(p1, Q2.shape), Q2), angle(np.broadcast_to(p2, Q1.shape), Q1))
    psi2 = signed_angle(np.broadcast_to(q2, Q2.shape), Q2, np.broadcast_to(p2, Q2.shape))
    return dict(R=R, WL=WL, Q1=Q1, Q2=Q2, mu1=mu1, mu2=mu2, sep=sep, psi2=psi2, ok=ok)


def ik(d, HG):
    """-> dict(ok, phi, th1, th3, psi2, resid (deg), R1, RL2 (scapula-frame body rotations)) for humerus rotations HG"""
    n = len(HG); out = dict(ok=np.zeros(n, bool), resid=np.full(n, 99.0))
    if not d["ok"]: return out
    b = d["b"]; y = HG @ d["W0"]; gy = y @ b; th = np.arccos(np.clip(gy, -1, 1)) / D2R
    inb = (th >= d["tlo"]) & (th <= d["thi"])
    seg = slice(d["ia"], d["ib"] + 1); php = d["ph"][seg]; Gp = d["G"][seg]; o = np.argsort(Gp)
    phi = np.interp(gy, Gp[o], php[o])
    h = 1e-4
    for _ in range(3):                                       # Newton on the exact loop (central difference)
        g0 = loop_eval(d, phi)["WL"] @ b
        gd = (loop_eval(d, phi + h)["WL"] @ b - loop_eval(d, phi - h)["WL"] @ b) / (2 * h)
        phi = np.clip(phi - (g0 - gy) / np.where(np.abs(gd) > 1e-9, gd, 1e-9), php[0], php[-1])
    E = loop_eval(d, phi)
    th1 = signed_angle(E["WL"], y, np.broadcast_to(b, y.shape))
    R1 = rot(b, th1); RL2 = R1 @ E["R"]
    resid = angle(np.einsum("nij,j->ni", RL2, d["Wr"]), y) / D2R
    RA = HG @ d["HGr"].T if "HGr" in d else None
    v_l2 = np.einsum("nij,j->ni", RL2, d["er"]); v_arm = HG @ d["e0"]
    th3 = signed_angle(v_l2, v_arm, y)
    ok = inb & E["ok"] & (resid < RESID)
    if d["mode"] != "3r":
        ok &= (np.minimum(E["mu1"], E["mu2"]) >= d["tmin"] * D2R) & (np.maximum(E["mu1"], E["mu2"]) <= math.pi - d["tmin"] * D2R)
        ok &= E["sep"] >= d["pin_sep"] * D2R
    out.update(ok=ok, phi=phi, th1=th1, th3=th3, psi2=E.get("psi2", np.zeros(n)), resid=resid, R1=R1, RL2=RL2, th=th)
    return out


def continuity(d, P):
    """per bench pose: False if a clip frame is reached only through a joint jump > FLIP on the full 10 fps clip"""
    okc = np.ones(len(P.idx), bool); pos = {int(z): j for j, z in enumerate(P.idx)}
    for name, rows in P.clip_rows.items():
        s = ik(d, P.HGall[rows])
        if not s["ok"].any(): continue
        q = np.stack([s["th1"], s["phi"], s["psi2"], s["th3"]], 1); last = None
        for t, z in enumerate(rows):
            if not s["ok"][t]: continue
            if last is not None and np.abs(wrap(q[t] - last)).max() / D2R > FLIP and int(z) in pos: okc[pos[int(z)]] = False
            last = q[t]
    return okc


# ------------------------------------------------------------------------------------------------ part samplers
def strap_dirs(u, v, width):
    """tools/concept_baseline.py arc_dirs for one strap: great circle u -> v, 2 mm along / across at r_ref 70 -> (ns, nc, 3)"""
    ang = float(angle(u, v)); ns = max(3, int(ang * R_REF / SP) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); th = s * ang
    D = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    cs = np.arange(-width / 2, width / 2 + 1e-6, SP) / R_REF
    return unit(D[:, None, :] * np.cos(cs)[None, :, None] + nrm[None, None, :] * np.sin(cs)[None, :, None]), ang * R_REF / (ns - 1)


def disc_dirs(u, rad):
    """tools/concept_baseline.py disc_dirs for one disc (2.5 mm grid at r_ref 70)"""
    g = np.arange(-rad, rad + 1e-6, DSP); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2
    X, Y = X[keep] / R_REF, Y[keep] / R_REF
    a = unit(np.cross(u, np.array([0.0, 0.0, 1.0]) + 1e-3)); c = np.cross(u, a)
    return unit(u[None] + X[:, None] * a[None] + Y[:, None] * c[None])


def build_items(d, p):
    """parts in processing order (lowest first). item: name, body, kind, dirs (k,3) in the body's reference frame,
    shape (strap), ds, t (radial thickness: strap 3, disc = crown), sp (grid mm), joint (disc), ends (strap)"""
    up = p["up"]; hub_t = HUB_CROWN - 3.15 + up; pin_t = PIN_CROWN - 3.15 + up; W = p["width"]
    I = []

    def disc(name, body, axis, rad, joint, t):
        I.append(dict(name=name, body=body, kind="disc", dirs=disc_dirs(axis, rad), t=t, sp=DSP, joint=joint, axis=axis))

    def strap(name, body, u, v, ends):
        S, ds = strap_dirs(u, v, W)
        I.append(dict(name=name, body=body, kind="strap", dirs=S.reshape(-1, 3), shape=S.shape[:2], ds=ds, t=T_STRAP, sp=SP, ends=ends, u=u, v=v))
    b, Wr = d["b"], d["Wr"]
    ng = p["neck_deg"] * D2R; ar = d["ar"]; nk = unit(math.cos(ng) * Wr + math.sin(ng) * unit(ar - (ar @ Wr) * Wr))
    if d["mode"] == "3r":
        J2 = d["J2"]
        disc("hub1", "L1", b, HUB_R, "J1", hub_t); disc("hub2", "L1", J2, HUB_R, "J2", hub_t)
        strap("link1", "L1", b, J2, [("J1", "lo"), ("J2", "lo")])
        disc("hub3", "L2", Wr, HUB_R, "J3", hub_t)
        strap("link2", "L2", J2, Wr, [("J2", "up"), ("J3", "lo")])
        strap("neck", "ARM", Wr, nk, [("J3", "up"), None])
        joints = dict(J1=(b, HUB_R, ("S", "L1")), J2=(J2, HUB_R, ("L1", "L2")), J3=(Wr, HUB_R, ("L2", "ARM")))
        return I, joints
    p1, p2, q1, q2 = d["p1"], d["p2"], d["q1"], d["q2"]
    joints = dict(J1=(b, HUB_R, ("S", "L1")), P1=(p1, PIN_R, ("L1", "R1")), P2=(p2, PIN_R, ("L1", "R2")),
                  Q1=(q1, PIN_R, ("R1", "L2")), Q2=(q2, PIN_R, ("R2", "L2")), J3=(Wr, HUB_R, ("L2", "ARM")))
    disc("hub1", "L1", b, HUB_R, "J1", hub_t); disc("pin_p1", "L1", p1, PIN_R, "P1", pin_t); disc("pin_p2", "L1", p2, PIN_R, "P2", pin_t)
    if p["shape"] == "T":
        pm = unit(p1 + p2); strap("L1_stem", "L1", b, pm, [("J1", "lo"), None]); strap("L1_bar", "L1", p1, p2, [("P1", "lo"), ("P2", "lo")])
    else:
        strap("L1_a", "L1", b, p1, [("J1", "lo"), ("P1", "lo")]); strap("L1_b", "L1", b, p2, [("J1", "lo"), ("P2", "lo")])

    def l2_parts(qrole):
        disc("hub3", "L2", Wr, HUB_R, "J3", hub_t)
        if qrole == "lo":
            disc("pin_q1", "L2", q1, PIN_R, "Q1", pin_t); disc("pin_q2", "L2", q2, PIN_R, "Q2", pin_t)
        if p["shape"] == "T":
            qm = unit(q1 + q2); strap("L2_bar", "L2", q1, q2, [("Q1", qrole), ("Q2", qrole)]); strap("L2_stem", "L2", qm, Wr, [None, ("J3", "lo")])
        else:
            strap("L2_a", "L2", q1, Wr, [("Q1", qrole), ("J3", "lo")]); strap("L2_b", "L2", q2, Wr, [("Q2", qrole), ("J3", "lo")])
    if not p["l2_over"]:
        l2_parts("lo")
        strap("rocker1", "R1", p1, q1, [("P1", "up"), ("Q1", "up")]); strap("rocker2", "R2", p2, q2, [("P2", "up"), ("Q2", "up")])
    else:
        disc("pin_q1", "R1", q1, PIN_R, "Q1", pin_t); strap("rocker1", "R1", p1, q1, [("P1", "up"), ("Q1", "lo")])
        disc("pin_q2", "R2", q2, PIN_R, "Q2", pin_t); strap("rocker2", "R2", p2, q2, [("P2", "up"), ("Q2", "lo")])
        l2_parts("up")
    strap("neck", "ARM", Wr, nk, [("J3", "up"), None])
    return I, joints


def body_rots(d, s, P, sel):
    """thorax <- body reference frame rotations for the selected bench poses"""
    RS = P.RS[sel]; R1 = s["R1"][sel]; RL2 = s["RL2"][sel]
    out = dict(L1=RS @ R1, L2=RS @ RL2, ARM=RS @ P.HG[sel] @ P.HGr.T)
    if d["mode"] != "3r":
        out["R1"] = RS @ R1 @ rot(d["p1"], s["phi"][sel])
        out["R2"] = RS @ R1 @ rot(d["p2"], s["psi2"][sel])
    return out


# ------------------------------------------------------------------------------------------------ skin radius
def skin_radius(B, i, D, r_max=260.0):
    """tools/concept_baseline.py: outermost skin radius along unit directions D (k, 3) from GH in pose i"""
    r = np.full(len(D), r_max); act = np.ones(len(D), bool); hit = np.zeros(len(D), bool)
    for _ in range(80):
        if not act.any(): break
        dd = B.dist(i, D[act] * r[act, None]); a = np.nonzero(act)[0]
        done = dd < 0.3; hit[a[done]] = True; act[a[done]] = False
        r[a[~done]] -= np.maximum(dd[~done], 0.5)
        low = r < 15; act &= ~low
    return np.where(hit, r, 0.0)


# ------------------------------------------------------------------------------------------------ the model
class Model:
    """one configuration fitted on the bench: kinematics, part profiles, per-pose taken / metal"""
    def __init__(self, p, P, log=None):
        self.p = dict(PARAMS, **p); self.P = P; p = self.p; B = P.B; t0 = time.time()
        d = design(dict(p, HGr=P.HGr), P.HGr); d["HGr"] = P.HGr; d["tmin"] = p["tmin"]; d["pin_sep"] = p["pin_sep"]; self.d = d
        self.info = dict(kin_ok=bool(d["ok"]), why=d.get("why", ""))
        n = len(P.idx); self.n = n
        if not d["ok"]: self.valid = np.zeros(n, bool); return
        s = ik(d, P.HG); self.s = s
        cont = continuity(d, P); self.kin = s["ok"].copy(); self.cont = cont
        valid = s["ok"] & cont; self.valid = valid; vi = np.nonzero(valid)[0]; self.vi = vi
        self.info.update(kin_ws=float(s["ok"][P.kind == "ws"].mean()), kin_clip=float(s["ok"][P.kind == "clip"].mean()),
                         cont_clip=float((valid[P.kind == "clip"]).mean()), phi_range=(d["phi_lo"], d["phi_hi"]),
                         band=(round(d["tlo"], 1), round(d["thi"], 1)), ends=d["ends"])
        if len(vi) < 5: return
        items, joints = build_items(d, p); self.items = items; self.joints = joints
        k_of = np.concatenate([[m] * len(it["dirs"]) for m, it in enumerate(items)]); self.k_of = k_of
        D0 = np.concatenate([it["dirs"] for it in items]); self.D0 = D0
        body = np.array([it["body"] for it in items])[k_of]; self.body = body
        sp = np.array([it["sp"] for it in items])[k_of]; self.sp = sp
        tt = np.array([it["t"] for it in items])[k_of]; self.tt = tt
        # joint zones: sample within joint radius + 2 mm (exemption) / within the joint radius (end constraint)
        self.zone = {}; self.endz = {}
        for J, (ax, rad, bods) in joints.items():
            a = angle(D0, ax[None]) * R_REF
            self.zone[J] = (a <= rad + 2.0) & np.isin(body, bods); self.endz[J] = a <= rad
        R = body_rots(d, s, P, vi); self.R = R
        Dt = np.empty((len(vi), len(D0), 3))
        for bd in set(body): m = body == bd; Dt[:, m] = np.einsum("pij,kj->pki", R[bd], D0[m])
        self.Dt = Dt
        # outermost skin radius under every sample, every valid pose
        rs = np.stack([skin_radius(B, int(i), Dt[q]) for q, i in enumerate(vi)])
        self.rs = rs
        # lateral neighbour pairs per pose (different bodies, not exempt), earlier item first
        adj = {}
        for J, (ax, rad, bods) in joints.items(): adj[tuple(sorted(bods))] = J
        self.pairs = []
        thr_max = (2 * DSP) / (2 * R_REF) + GAP / 40.0
        for q in range(len(vi)):
            T = cKDTree(Dt[q]); pr = T.query_pairs(2 * math.sin(thr_max / 2), output_type="ndarray")
            if not len(pr): self.pairs.append(pr); continue
            a, b_ = pr[:, 0], pr[:, 1]; o = k_of[a] > k_of[b_]; a, b_ = np.where(o, b_, a), np.where(o, a, b_)
            keep = body[a] != body[b_]
            ang_ = angle(Dt[q, a], Dt[q, b_]); r_est = np.maximum(np.minimum(rs[q, a], rs[q, b_]), 40.0)
            keep &= ang_ < (sp[a] + sp[b_]) / (2 * R_REF) + GAP / r_est
            for bp, J in adj.items():
                m = keep & (((body[a] == bp[0]) & (body[b_] == bp[1])) | ((body[a] == bp[1]) & (body[b_] == bp[0])))
                keep &= ~(m & self.zone[J][a] & self.zone[J][b_])
            self.pairs.append(np.stack([a[keep], b_[keep]], 1))
        self.info["t_fit"] = round(time.time() - t0, 1)
        if log: log(f"  fitted kinematics + skin radii: {len(vi)} valid poses, {len(D0)} samples, {time.time() - t0:.0f} s")

    def profiles(self, pct):
        """per-sample underside radius (fixed in its body) at percentile pct, sequential 'rides over'"""
        p = self.p; items = self.items; rs = self.rs + p["clear"]; up = p["up"]
        rad = np.zeros(len(self.D0)); top = np.zeros(len(self.D0)); level = {}
        ob = rs.copy()
        off = np.cumsum([0] + [len(it["dirs"]) for it in items])
        for m, it in enumerate(items):
            sl = slice(off[m], off[m + 1])
            # obstacles from earlier items (pairs whose later member is in this item)
            obm = ob[:, sl].copy()
            for q, pr in enumerate(self.pairs):
                if not len(pr): continue
                sel = (self.k_of[pr[:, 1]] == m)
                if not sel.any(): continue
                a, b_ = pr[sel, 0], pr[sel, 1]
                np.maximum.at(obm[q], b_ - off[m], top_pose[q][a] + GAP if False else rad[a] + self.tt[a] + GAP)
            r = np.percentile(obm, pct, axis=0)
            if it["kind"] == "disc":
                r = np.full_like(r, r.max()); level[it["joint"]] = r[0]
            else:
                ns, nc = it["shape"]; r = r.reshape(ns, nc); cons = np.full((ns, nc), -np.inf)
                for e in it["ends"]:
                    if e is None: continue
                    J, role = e; L = level[J] + (up if role == "up" else 0.0)
                    z = self.endz[J][sl].reshape(ns, nc); cons[z] = np.maximum(cons[z], L)
                r = np.maximum(r, cons)
                s = np.arange(ns) * it["ds"]                    # 60 deg ramp limit along the strap (both ways)
                env = r.copy()
                for j in range(ns): env = np.maximum(env, r[j][None, :] - RAMP * np.abs(s - s[j])[:, None])
                r = env.reshape(-1)
            rad[sl] = r; top[sl] = r + self.tt[sl]
        return rad

    def evaluate(self, pct, B=None):
        """record every bench pose at percentile pct -> report dict"""
        B = B or self.P.B; B.reset(); n = self.n
        if not self.d["ok"] or len(getattr(self, "vi", [])) < 5:
            r = B.report(); r.update(pct=pct, n_col=0); return r
        rad = self.profiles(pct); self.rad = rad; col = np.zeros(len(self.vi), bool)
        for q, i in enumerate(self.vi):
            pr = self.pairs[q]
            if len(pr):
                a, b_ = pr[:, 0], pr[:, 1]
                gap = np.maximum(rad[b_] - (rad[a] + self.tt[a]), rad[a] - (rad[b_] + self.tt[b_]))
                col[q] = bool((gap < GAP - 1e-6).any())
            if col[q]: continue
            B.record(int(i), self.Dt[q] * rad[:, None])
        self.col = col
        r = B.report(); r.update(pct=pct, n_col=int(col.sum()))
        # per-part in-band share over the taken clip frames
        tk = [q for q, i in enumerate(self.vi) if self.P.kind[i] == "clip" and B.res[i] is not None and B.res[i].min() >= 0]
        if tk:
            dd = np.stack([B.res[self.vi[q]] for q in tk])
            r["parts"] = {it["name"]: round(float(((dd[:, self.k_of == m] >= 2) & (dd[:, self.k_of == m] <= 14)).mean()), 3) for m, it in enumerate(self.items)}
            r["n_samples"] = int(len(self.D0))
        return r


def run(p, P, pcts=(80, 90, 95, 100), log=print):
    """fit one configuration, evaluate at each percentile, return (best report, all reports)"""
    M = Model(p, P, log=log)
    rows = []
    for pc in pcts:
        r = M.evaluate(pc); rows.append(r)
    best = min(rows, key=lambda r: r["gap"]); best = dict(best, info=M.info)
    return best, rows, M


# ------------------------------------------------------------------------------------------------ metal() API
_FIT = {}


def metal(pose, frames, params=None):
    """(k, 3) metal sample points (thorax frame, mm) of the configuration `params` (fitted on Bench(60, 160) at its
    pct) for a pose with frames (B.frames(i)), or None if the mechanism cannot take it (closure / band / pin range /
    part interference)"""
    p = dict(PARAMS, **(params or {})); key = json.dumps(p, sort_keys=True)
    if key not in _FIT:
        P = get_poses(60, 160); M = Model(p, P); M.evaluate(p["pct"]); _FIT[key] = M
    M = _FIT[key]; d = M.d; P = M.P
    if not d["ok"]: return None
    RS = frames["S"][0]; HG = RS.T @ frames["H"][0] @ P.C.T
    s = ik(d, HG[None])
    if not s["ok"][0]: return None
    R = dict(L1=RS @ s["R1"][0], L2=RS @ s["RL2"][0], ARM=RS @ HG @ P.HGr.T)
    if d["mode"] != "3r":
        R["R1"] = R["L1"] @ rot(d["p1"], s["phi"][0]); R["R2"] = R["L1"] @ rot(d["p2"], s["psi2"][0])
    Dt = np.empty_like(M.D0)
    for bd in set(M.body): m = M.body == bd; Dt[m] = M.D0[m] @ R[bd].T
    rad = M.rad; T = cKDTree(Dt); pr = T.query_pairs(2 * math.sin(((2 * DSP) / (2 * R_REF) + GAP / 40.0) / 2), output_type="ndarray")
    if len(pr):
        a, b_ = pr[:, 0], pr[:, 1]; keep = M.body[a] != M.body[b_]
        keep &= angle(Dt[a], Dt[b_]) < (M.sp[a] + M.sp[b_]) / (2 * R_REF) + GAP / np.maximum(np.minimum(rad[a], rad[b_]), 40.0)
        for J, (ax, r_, bods) in M.joints.items():
            mm = keep & (((M.body[a] == bods[0]) & (M.body[b_] == bods[1])) | ((M.body[a] == bods[1]) & (M.body[b_] == bods[0])))
            keep &= ~(mm & M.zone[J][a] & M.zone[J][b_])
        a, b_ = a[keep], b_[keep]
        gap = np.maximum(rad[b_] - (rad[a] + M.tt[a]), rad[a] - (rad[b_] + M.tt[b_]))
        if (gap < GAP - 1e-6).any(): return None
    return Dt * rad[:, None]


# ------------------------------------------------------------------------------------------------ CLI
def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def check(n_clip=20, n_ws=40):
    P = get_poses(n_clip, n_ws)
    for mode in ("3r", "4bar"):
        p = dict(PARAMS, mode=mode); d = design(p, P.HGr); d["tmin"] = p["tmin"]; d["pin_sep"] = p["pin_sep"]
        if not d["ok"]: print(mode, "design fails:", d["why"]); continue
        s = ik(d, P.HG); c = continuity(d, P)
        print(f"{mode}: band {d['tlo']:.1f}-{d['thi']:.1f} deg ({d['ends']}), phi {d['phi_lo']:.1f}..{d['phi_hi']:.1f}, "
              f"kin ws {s['ok'][P.kind == 'ws'].mean():.3f} clip {s['ok'][P.kind == 'clip'].mean():.3f}, cont-ok clip {(s['ok'] & c)[P.kind == 'clip'].mean():.3f}, "
              f"max resid {s['resid'][s['ok']].max() if s['ok'].any() else 99:.4f}")
        if mode == "4bar":
            print(f"   lam1 {d['lam1'] / D2R:.1f} lam2 {d['lam2'] / D2R:.1f} c12 {d['c12'] / D2R:.1f} deg")


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    a = sys.argv[1:]
    cmd = a[0] if a else "check"
    if cmd == "check":
        check(*(int(x) for x in a[1:3])) if len(a) >= 3 else check()
