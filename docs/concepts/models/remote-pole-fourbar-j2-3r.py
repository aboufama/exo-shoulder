"""Concept model: REMOTE-POLE SPHERICAL FOUR-BAR as J2 at the cap pole (id remote-pole-fourbar-j2-3r) - round 102 lens 1
(virtual J2), the OPEN near-isogram cell. cap-cell-fourbar-j2-3r is merged as the measured-dead cell B (judge,
docs/concepts/round102_ideation.md 1.1) and is not modelled.

Why: at the cap-pole seats (J1 bvec(43.15, 59.93), J3 wdir(92.03, -9.03)) the plain 3R's kinematic reach is 281/360
on Bench(110,360), but mode-A poses put the J2 ray's skin exit 107-116 mm from GH, so an O20 hub ON the J2 axis is never
in band (668 configs: hub 2 <= 0.12). A spherical four-bar moves the coupler about an INSTANTANEOUS pole (the crossing
of the two crank great circles) with no metal on it: the four O20 pins sit on rays the designer picks. Open (cranks
do not cross: the cruciate cell is docs/concepts/models/cruciate-knuckle-3r.py, dead at 79.77 fast), near-isogram
(the B dyad is the A dyad carried sideways by g deg, then nudged: eps along crank B, tw about A1).

  scapula (handler on J1's hub ring) -J1- link 1 (ternary: J1, A0, B0) -A0- crank A -A1- coupler (ternary: A1, B1, J3)
  -J3- arm (K7 neck to BOTTOM); loop: link 1 -B0- crank B -B1- coupler. Six O20 v5 stacks ("Keep O20 only").

Mobility: spherical Grubler, n = 6 bodies, j = 6 revolutes: M = 3 (6 - 1) - 2 x 6 = 3; loop mobility 1. ACTIVE: J1, A0
(the J2 coordinate = crank A's own angle theta), J3; PASSIVE: B0, A1, B1, set in closed form by theta (kit two-circle
closure): 0 passive translations, no undetermined coordinate (R17). Numeric 3x3 rotation Jacobian in `jac` mode.

Fold rule, read in ONE metric (CLAUDE.md, th = the J1-J3 angle, tools/concept_kit.py): the four-bar lives on the
LONGEST monotone run of th(theta) where BOTH transmission angles stay in [MU, 180 - MU] (no toggle, no dead point,
one assembly branch); its th window is that run minus K.FOLD_MARGIN at each end (the stop: a dowel in an arc groove
on crank A's OWN angle at A0, at the theta where th is 5 deg inside the run end). Per pose theta is the unique root
on the run, J1 turns phi to carry the coupler's J3 point onto the arm's J3 axis, J3 turns q3.

Measured: docs/concepts/remote-pole-fourbar-j2-3r.md.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/remote-pole-fourbar-j2-3r.py check '<json params>'
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/remote-pole-fourbar-j2-3r.py jac '<json params>'
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("vp4j2", os.path.join(REPO, "docs", "concepts", "models", "virtual-pole-4bar-j2.py"))
VP = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(VP)

ID = "remote-pole-fourbar-j2-3r"
NAME = "Remote-pole spherical four-bar J2 at the cap pole (open near-isogram, six O20 pins)"
D2R = math.pi / 180
MU, PINSEP = 30.0, 22.0                          # transmission window [MU, 180 - MU]; min pin separation (deg)
SEAT = dict(az=43.15, el=59.93, wd=92.03, wa=-9.03)                   # cap pole J1 / J3 (round-102 planner)
ISO = ["th0", "dA0", "pA0", "dA1", "pA1", "g", "gam", "eps", "tw"]   # lens 1's near-isogram vector (rp4 par.py)
LO = np.array([30, 18, -180, 30, -180, 22, -180, -15, -25.0]); HI = np.array([140, 40, 180, 80, 180, 40, 180, 15, 25.0])
S1 = [65.8, 22.4, 60.4, 47.7, 38.6, 30.2, -96.2, 2.1, 13.6]           # lens-1 seeds (proxy 33.67 / 35.72 / 34.25)
S2 = [84.4, 28.1, 135.5, 75.2, 34.2, 22.3, 77.9, -5.6, -19.3]
S3 = [31.8, 20.8, 179.0, 54.3, 90.8, 23.1, 120.9, 2.5, 15.6]
PARAMS = dict(SEAT, **dict(zip(ISO, S1)), width=12.0, t_link=3.0, q=1.0)
ang, mv, rot, gc = VP.ang, VP.mv, VP.rot, VP.gc


def layout(p):
    """-> (J1, J3 home = the coupler's J3 point, FourBar) in the link-1 frame (= scapula at phi 0). J3 home at th0 from
    J1 in the J1-y plane; A0 at dA0 from J1 at dihedral pA0 from the arc J1 -> J3; A1 at dA1 from J3 at pA1 from J3 -> J1;
    B0 = g deg from A0 at dihedral gam from the crank A0 -> A1; B1 = B0 carried by the rotation A0 -> A1 (isogram), then
    eps deg along crank B and tw deg about A1 (breaks the isogram: its parallelogram limit is a pure translation)."""
    j = K.bvec(p["az"], p["el"]); Y = np.array([0.0, 1.0, 0.0]); T0 = K.unit(Y - (Y @ j) * j)
    c = math.cos(p["th0"] * D2R) * j + math.sin(p["th0"] * D2R) * T0
    a0 = gc(j, c, p["pA0"], p["dA0"]); a1 = gc(c, j, p["pA1"], p["dA1"])
    b0 = gc(a0, a1, p["gam"], p["g"])
    ax = K.unit(np.cross(a0, a1)); b1 = rot(ax, float(ang(a0, a1))) @ b0
    if abs(p["eps"]) > 1e-6: b1 = gc(b1, b0, 180.0, p["eps"])
    b1 = rot(a1, p["tw"]) @ b1
    return j, c, VP.FourBar(a0, b0, a1, b1)


_CACHE = {}
def curve(p):
    """coupler curve on a 0.25 deg crank grid -> the longest monotone th run with both transmissions in [MU, 180 - MU]"""
    key = json.dumps({k: p[k] for k in sorted(p) if k not in ("width", "t_link", "q")}, sort_keys=True)
    if key in _CACHE: return _CACHE[key]
    j, carried, fb = layout(p)
    TH = np.arange(-180.0, 180.0, 0.25); a1, b1, Rc, mg = fb.at(TH); c = mv(Rc, carried)
    g = ang(np.broadcast_to(j, c.shape), c); good = mg >= MU; d = np.sign(np.diff(g)); n = len(TH); best = (0.0, None)
    i = 0
    while i < n:
        if not good[i]: i += 1; continue
        k = i
        while k + 1 < n and good[k + 1]: k += 1
        s = i
        while s < k:
            e = s; sg = d[s]
            while e < k and d[e] == sg: e += 1
            if abs(g[e] - g[s]) > best[0]: best = (abs(g[e] - g[s]), (s, e))
            s = e
        i = k + 1
    sep = min(ang(fb.a0, fb.b0), ang(fb.a1h, fb.b1h), ang(fb.a0, fb.a1h), ang(fb.b0, fb.b1h),
              ang(fb.a1h, carried), ang(fb.b1h, carried), ang(fb.a0, j), ang(fb.b0, j))
    out = dict(j=j, carried=carried, fb=fb, sep=float(sep), valid=False)
    if best[1] is not None:
        s, e = best[1]; th, gg = TH[s:e + 1], g[s:e + 1]
        if gg[-1] < gg[0]: th, gg = th[::-1], gg[::-1]
        lo, hi = float(gg[0]) + K.FOLD_MARGIN, float(gg[-1]) - K.FOLD_MARGIN
        out.update(th=th, g=gg, lo=lo, hi=hi, W=hi - lo, valid=bool(hi > lo and sep >= PINSEP - 0.01),
                   mgmin=float(mg[min(s, e):max(s, e) + 1].min()))
    if len(_CACHE) > 64: _CACHE.clear()
    _CACHE[key] = out; return out


def build(B, F, p):
    p = dict(PARAMS, **p); cv = curve(p); P = len(F.RS); fb = cv["fb"]
    RS = F.RS; ST = np.transpose(RS, (0, 2, 1))
    S = lambda u: mv(RS, np.broadcast_to(u, (P, 3)))
    w = mv(F.RHG, np.broadcast_to(K.wdir(p["wd"], p["wa"]), (P, 3)))           # J3 axis (thorax), fixed in the humerus
    ws = mv(ST, w); j = cv["j"]
    rho = ang(np.broadcast_to(j, (P, 3)), ws)                                  # the arm's J1-J3 angle (th)
    if cv["valid"]:
        ok = (rho >= cv["lo"]) & (rho <= cv["hi"])
        theta = np.interp(rho, cv["g"], cv["th"]); marg = np.minimum(rho - (cv["lo"] - K.FOLD_MARGIN), (cv["hi"] + K.FOLD_MARGIN) - rho)
    else:
        ok = np.zeros(P, bool); theta = np.zeros(P); marg = np.zeros(P)
    theta = np.where(ok, theta, float(cv["th"][len(cv["th"]) // 2]) if "th" in cv else 0.0)
    a1, b1, Rc, mg = fb.at(theta); c = mv(Rc, cv["carried"])
    ok &= mg >= MU
    res = np.abs(ang(c, np.broadcast_to(j, (P, 3))) - rho)
    phi = K.axis_angle(np.broadcast_to(j, (P, 3)), c, ws); R1 = rot(np.broadcast_to(j, (P, 3)), phi)
    J1 = S(j); A0, B0 = S(mv(R1, fb.a0)), S(mv(R1, fb.b0)); A1, B1 = S(mv(R1, a1)), S(mv(R1, b1)); J3 = S(mv(R1, c))
    res = np.maximum(res, ang(J3, w))
    q = np.stack([phi, theta, K.axis_angle(B0, A0, B1), K.axis_angle(A1, A0, B1), K.axis_angle(J3, A1, F.HG([0.0, -1, 0]))], -1)
    joints = dict(J1=J1, A0=A0, B0=B0, A1=A1, B1=B1, J3=J3)
    hubs = [K.hub_member(f"hub{n}", v, n) for n, v in joints.items()]        # every pin an O20 v5 stack (Keep O20 only)
    w_, t_ = p["width"], p["t_link"]
    near = "A1" if ang(fb.a1h, cv["carried"]) <= ang(fb.b1h, cv["carried"]) else "B1"
    X = dict(A1=A1, B1=B1)[near]; Y = dict(A1=B1, B1=A1)[near]; y_name = "B1" if near == "A1" else "A1"
    g_name = "A0" if ang(j, fb.a0) <= ang(j, fb.b0) else "B0"; Xg = A0 if g_name == "A0" else B0
    o_name = "B0" if g_name == "A0" else "A0"; Xo = B0 if g_name == "A0" else A0
    mem = hubs + [
        # layers: both cranks lowest (open cell: they do not meet; K6 checks) but over J1's stack where they swing across it
        # (measured: without it hubJ1 vs crank A / B rejects 56 / 78 % of s1's closing poses), link 1 over the cranks and
        # the coupler pins, the coupler over the neck, the cranks, the link-1 pins and J1 wherever they meet
        K.strap_member("crankA", A0, A1, ("A0", "A1"), width=w_, t=t_, ramp_to=(("hubA0", 0.0), ("hubA1", 0.0)),
                       over=[("hubJ1", 1.0)]),
        K.strap_member("crankB", B0, B1, ("B0", "B1"), width=w_, t=t_, ramp_to=(("hubB0", 0.0), ("hubB1", 0.0)),
                       over=[("hubJ1", 1.0)]),
        VP.polystrap("link1", [J1, Xg, Xo], ("J1", g_name, o_name), w_, t_,
                     ramps=[("hubJ1", K.STACK), (f"hub{g_name}", K.STACK), (f"hub{o_name}", K.STACK)],
                     over=[("crankA", 1.0), ("crankB", 1.0), ("hubA1", 1.0), ("hubB1", 1.0)]),
        VP.polystrap("coupler", [Y, X, J3], (y_name, near, "J3"), w_, t_,
                     ramps=[(f"hub{y_name}", K.STACK), (f"hub{near}", K.STACK), ("hubJ3", K.STACK)],
                     over=[("neck", 1.0), ("crankA", 1.0), ("crankB", 1.0), ("hubA0", 1.0), ("hubB0", 1.0), ("hubJ1", 1.0)]),
        K.neck_member(F, J3, joints=("J3",), ramps=(("hubJ3", 0.0), (None, 0)))]
    okr = ok & (res < 0.5)
    info = dict(residual_deg=round(float(res[okr].max()), 5) if okr.any() else None, pin_sep_deg=round(cv["sep"], 1),
                th_window=[round(cv["lo"], 1), round(cv["hi"], 1)] if "lo" in cv else None,
                W=round(cv.get("W", 0.0), 1), min_th_margin=round(float(marg[okr].min()), 3) if okr.any() else None,
                min_transmission=round(float(mg[okr].min()), 1) if okr.any() else None)
    return K.Chain(members=mem, ok=okr, q=q, joints=joints, info=info)


def jac(p):
    """mobility check: numeric 3x3 Jacobian of the arm's rotation w.r.t. (phi, theta, q3) over the th WINDOW (the run
    minus the 5-deg stops); sigma_min/sigma_max per sample"""
    p = dict(PARAMS, **p); cv = curve(p); fb = cv["fb"]; out = []
    if not cv["valid"]: return np.array([])
    inw = (cv["g"] >= cv["lo"]) & (cv["g"] <= cv["hi"]); tw_ = cv["th"][inw]
    for t in np.linspace(tw_[0], tw_[-1], 30):
        def R(phi, theta, q3):
            return rot(cv["j"], phi) @ fb.at(np.array([theta]))[2][0] @ rot(cv["carried"], q3)
        x0 = np.array([10.0, float(t), 5.0]); R0 = R(*x0); J = []
        for k in range(3):
            e = np.zeros(3); e[k] = 1e-3; dR = (R(*(x0 + e)) - R(*(x0 - e))) / 2e-3 @ R0.T
            J.append([dR[2, 1], dR[0, 2], dR[1, 0]])
        sv = np.linalg.svd(np.array(J).T, compute_uv=False); out.append(sv[-1] / sv[0])
    return np.array(out)


def iso(x): return dict(zip(ISO, [float(v) for v in np.clip(x, LO, HI)]))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if isinstance(par, list): par = iso(par)
    if mode == "jac":
        r = jac(par); print("sigma_min/sigma_max over the th window: min", r.min() if len(r) else None, "median", np.median(r) if len(r) else None, len(r)); sys.exit()
    B = K.bench(60, 160); t0 = time.time(); rep = K.evaluate(B, build, dict(PARAMS, **par))
    print({k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                    "honest", "audit", "residual_deg", "pin_sep_deg", "th_window", "W", "min_th_margin",
                                    "min_transmission", "mass_g")}, round(time.time() - t0, 1), "s")
    print(rep["inband_member"])
