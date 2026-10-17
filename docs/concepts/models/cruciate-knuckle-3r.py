"""Concept model: CRUCIATE KNUCKLE as J2 (id cruciate-knuckle-3r) - lens virtual-j2's CROSSED cell at the cap pole.

The catalogue spec replaced all three revolutes by rolling crossed four-bars on hubless O6-8 pins. Under the user's
"Keep O20 only" ruling (2026-10-16) and the round-102 plan, that is wrong twice over: hubless pins are out, and J1 / J3
are not the limiter. The measured limiter at the cap-pole seats is J2: mode-A poses put the J2 ray's skin exit
107-116 mm from GH, so metal ON the J2 axis cannot be in band (668 cap configs: hub 2 <= 0.12 in band). So this model
keeps J1 and J3 as plain O20 hubs and replaces ONLY J2 by a spherical CROSSED four-bar (the knee's cruciate ligaments,
O'Connor / Zavatsky), all four pins O20 stacks:

  scapula -J1- link 1 (carries the ground pins A0, B0) -A0- crank A -A1- coupler (link 2) -B1- crank B -B0- link 1;
  the coupler carries J3 (O20 hub on the arm) -> arm (K7 neck to BOTTOM).

Crossed = each crank's two pins lie on OPPOSITE sides of the home pole along its great circle (sign(dA0) != sign(dA1),
sign(dB0) != sign(dB1)), so the two cranks cross in an X and the instantaneous J2 axis is their crossing point: it
rolls along both cranks as the knuckle turns (the moving centrode). Link 1 sits on J1's side of the pole, the coupler
on J3's side, so the only metal on the J2 ray is the two crossing 3 mm cranks (crank B passes 1 mm over crank A)
instead of a 12.25 mm O20 stack. That is the bet this screen measures.

Kinematics (shared with docs/concepts/models/virtual-pole-4bar-j2.py: FourBar, layout, closure in closed form): the
carried J3 axis c(theta) traces the coupler curve; th(theta) = angle(J1, c(theta)) is the dyad's J1-J3 angle. Branch
and fold rule, read in ONE metric (CLAUDE.md, the 5-deg margin in th): the knuckle lives on the LONGEST monotone run of
th(theta) inside the assembled interval where both transmission angles stay in [30, 150] deg (no toggle, no dead
point, one assembly branch); its th window is that run's span minus K.FOLD_MARGIN at each end (the physical stop: a
dowel in an arc slot on crank A's OWN angle at A0, at the theta where th is 5 deg inside the run's end). Per pose th
is the arm's J1-J3 angle; theta is the unique root on the run (monotone), then J1 turns phi to carry c onto the arm's
J3 axis, then J3 turns q3. Mobility: spherical Grubler n = 6, j = 6: M = 3 (5) - 12 = 3; loop mobility 1; passives
(B0, A1, B1) set by theta in closed form: 0 passive translations, no undetermined coordinate (R17). Pins of one body
>= 22 deg apart (two O20 discs side by side at a ~52 mm level), each crank >= 22 deg long.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cruciate-knuckle-3r.py [check '<json>' | coarse N seed | cma ...]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("vp4j2", os.path.join(REPO, "docs", "concepts", "models", "virtual-pole-4bar-j2.py"))
VP = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(VP)

ID = "cruciate-knuckle-3r"
NAME = "Cruciate knuckle J2: crossed spherical four-bar (O20 pins) at the cap pole, J1 / J3 plain O20"
D2R = math.pi / 180
MU, PINSEP = 30.0, 22.0                          # transmission window [MU, 180 - MU]; min pin separation (deg)
SEAT = dict(az=43.15, el=59.93, wd=92.03, wa=-9.03, zeta=0.0, at=2)   # cap pole J1 / J3 (round-102 planner, rp4 SEAT)
PARAMS = dict(SEAT, a1=60.0, a2=60.0, beta=70.0, psiA=30.0, psiB=-30.0, dA0=24.0, dA1=-30.0, dB0=24.0, dB1=-30.0,
              width=12.0, t_link=3.0, q=1.0)
ang, mv, rot = VP.ang, VP.mv, VP.rot


ANCH = ["th0", "dA0", "pA0", "dB0", "pB0", "dA1", "pA1", "dB1", "pB1"]
def layout(p):
    """-> (J1, home pole, J3 home = the carried axis, FourBar) in the link-1 (scapula at phi 0) frame. Two
    parametrisations: pole-centred (a1, a2, beta, psi*, d*: virtual-pole-4bar-j2's) or ANCHORED (lens 1's search,
    scratchpad rp4/opt.py: J3 home at th0 from J1 in the J1-y plane; link-1 pins A0 / B0 at dA0 / dB0 from J1 at
    dihedral pA0 / pB0 from the arc J1 -> J3; coupler pins A1 / B1 at dA1 / dB1 from J3 at pA1 / pB1 from J3 -> J1)."""
    if "th0" not in p:
        j, j2h, pole, carried, fb = VP.layout(p); return j, pole, carried, fb
    j = K.bvec(p["az"], p["el"]); Y = np.array([0.0, 1.0, 0.0]); T0 = K.unit(Y - (Y @ j) * j)
    c = math.cos(p["th0"] * D2R) * j + math.sin(p["th0"] * D2R) * T0
    a0, b0 = VP.gc(j, c, p["pA0"], p["dA0"]), VP.gc(j, c, p["pB0"], p["dB0"])
    a1, b1 = VP.gc(c, j, p["pA1"], p["dA1"]), VP.gc(c, j, p["pB1"], p["dB1"])
    pole = K.unit(np.cross(np.cross(a0, a1), np.cross(b0, b1))); pole = pole if pole @ (j + c) > 0 else -pole
    return j, pole, c, VP.FourBar(a0, b0, a1, b1)


def arcs_cross(u0, u1, v0, v1):
    """do the great-circle arcs u0 -> u1 and v0 -> v1 cross (the cruciate X)?"""
    n1, n2 = np.cross(u0, u1), np.cross(v0, v1); x = np.cross(n1, n2)
    if np.linalg.norm(x) < 1e-9: return False
    x = x / np.linalg.norm(x)
    return any(abs(ang(u0, s) + ang(s, u1) - ang(u0, u1)) < 1e-3 and abs(ang(v0, s) + ang(s, v1) - ang(v0, v1)) < 1e-3
               for s in (x, -x))


_CACHE = {}
def curve(p):
    """coupler curve on a 0.25 deg crank grid -> the longest monotone th run with transmission in [MU, 180 - MU]"""
    key = json.dumps({k: p[k] for k in sorted(p) if k not in ("width", "t_link", "q")}, sort_keys=True)
    if key in _CACHE: return _CACHE[key]
    j, pole, carried, fb = layout(p)
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
            span = abs(g[e] - g[s])
            if span > best[0]: best = (span, (s, e))
            s = e
        i = k + 1
    sep = min(ang(fb.a0, fb.b0), ang(fb.a1h, fb.b1h), ang(fb.a0, fb.a1h), ang(fb.b0, fb.b1h),
              ang(fb.a1h, carried), ang(fb.b1h, carried), ang(fb.a0, j), ang(fb.b0, j))
    out = dict(j=j, pole=pole, carried=carried, fb=fb, sep=float(sep), crossed=False, valid=False)
    if best[1] is not None:
        s, e = best[1]; th, gg, cc = TH[s:e + 1], g[s:e + 1], c[s:e + 1]
        xs = [arcs_cross(fb.a0, a1[i], fb.b0, b1[i]) for i in np.linspace(min(s, e), max(s, e), 9).round().astype(int)]
        crossed = bool(all(xs))                         # the cranks cross (X) over the WHOLE run: a cruciate cell
        if gg[-1] < gg[0]: th, gg, cc = th[::-1], gg[::-1], cc[::-1]          # th ascending along the run
        lo, hi = float(gg[0]) + K.FOLD_MARGIN, float(gg[-1]) - K.FOLD_MARGIN
        out.update(th=th, g=gg, c=cc, lo=lo, hi=hi, W=hi - lo, crossed=crossed, valid=bool(hi > lo and sep >= PINSEP and crossed),
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
        # cruciate layers: crank A lowest, crank B crosses 1 mm over it (the X on the pole); link 1 (J1 side) and the
        # coupler (J3 side) pass over both cranks and the other body's pins wherever they meet; K6 checks the rest
        K.strap_member("crankA", A0, A1, ("A0", "A1"), width=w_, t=t_, ramp_to=(("hubA0", 0.0), ("hubA1", 0.0))),
        K.strap_member("crankB", B0, B1, ("B0", "B1"), width=w_, t=t_, ramp_to=(("hubB0", 0.0), ("hubB1", 0.0)),
                       over=[("crankA", 1.0)]),
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
                min_transmission=round(float(mg[okr].min()), 1) if okr.any() else None, crossed=cv["crossed"])
    return K.Chain(members=mem, ok=okr, q=q, joints=joints, info=info)


# ---- search -------------------------------------------------------------------------------------------------------
KEYS = ["a1", "a2", "beta", "psiA", "psiB", "dA0", "dA1", "dB0", "dB1"]
def kin_reach(p, rho_ws):
    cv = curve(dict(PARAMS, **p))
    if not cv["valid"]: return 0.0, cv
    return float(((rho_ws >= cv["lo"]) & (rho_ws <= cv["hi"])).mean()), cv


def rand_cfg(rng):
    sA, sB = rng.choice([-1, 1]), rng.choice([-1, 1])
    return dict(a1=rng.uniform(40, 80), a2=rng.uniform(40, 85), beta=rng.uniform(40, 140), psiA=rng.uniform(-90, 90),
                psiB=rng.uniform(-90, 90), dA0=sA * rng.uniform(12, 55), dA1=-sA * rng.uniform(12, 55),
                dB0=sB * rng.uniform(12, 55), dB1=-sB * rng.uniform(12, 55))


def rho_of(B, p):
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    j = K.bvec(p["az"], p["el"]); w = mv(F.RHG, np.broadcast_to(K.wdir(p["wd"], p["wa"]), (len(F.RS), 3)))
    ws = mv(np.transpose(F.RS, (0, 2, 1)), w); return ang(np.broadcast_to(j, ws.shape), ws), F


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "check":
        par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        B = K.bench(60, 160); t0 = time.time(); rep = K.evaluate(B, build, dict(PARAMS, **par))
        print({k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                        "honest", "audit", "residual_deg", "pin_sep_deg", "th_window", "W", "min_th_margin",
                                        "min_transmission", "mass_g")}, round(time.time() - t0, 1), "s")
        print(rep["inband_member"])
