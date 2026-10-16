"""Concept model: VIRTUAL-POLE SPHERICAL FOUR-BAR as J2 (id virtual-pole-4bar-j2) - and, with at=1, as J1
(id virtual-pole-4bar-j1, docs/concepts/models/virtual-pole-4bar-j1.py loads this file).

Field: spherical linkage kinematics. A revolute about a GH ray needs its bearing ON that ray. A spherical four-bar
(four pins, every axis through GH) moves its coupler about an INSTANTANEOUS pole = the intersection of the two crank
great circles; the pole is virtual (no metal there) and walks along the fixed centrode as the linkage moves. So the
pole can sit where the fold-free layouts want the joint axis while the four pins sit on rays the designer picks.

Chain (at=2): scapula -J1- link 1 (carries the ground pins A0, B0) -A0- crank A -A1- coupler -B1- crank B -B0- link 1;
the coupler carries J3 (O20 hub on the arm) -> arm (K7 neck to BOTTOM).
Chain (at=1): scapula base (carries A0, B0) -A0- crank A -A1- coupler = link 1 -B1- crank B -B0- base; link 1 carries
J2 (O20 hub) -> link 2 -> J3 -> arm.
Mobility (spherical Grubler, all six axes through GH): bodies n = 6 (ground, link 1 / base, 2 cranks, coupler, arm),
revolutes j = 6: M = 3 (n - 1) - 2 j = 15 - 12 = 3. The loop alone: 3 (4 - 1) - 2 * 4 = 1. Every pin is a bearing pair
(1 rotation): 0 passive translations, no slide, no undetermined coordinate (checked numerically: `jac` mode, rank of
the 3 x 3 map from (phi, theta, q3) to the arm's rotation vector = 3 on every taken pose).

Closure (per pose, exact, pose-local): the four-bar's coupler rotation R_c(theta) in its ground frame is solved in
closed form (crank A angle theta, B1 by the kit's two-circle closure). The carried axis c(theta) = R_c(theta) c_h
traces a spherical coupler curve. at=2: the arm's J3 axis w (scapula frame) must satisfy angle(j1, c(theta)) =
angle(j1, w) (a 1-D root on a 0.25 deg theta grid, then the closed-form four-bar at the root), then J1 turns phi
about j1 to carry c onto w. at=1: J2 = c(theta) must satisfy angle(c(theta), w) = a2. Branch: the root whose slope
sign is sigma, nearest theta = 0 (the home); the dense K2 check catches any jump. Ranges in ok: four-bar margin
>= M4 deg from its toggle (transmission), crossing angle between the coupler curve and the target circle >= XMIN deg
(the 3R's 10 deg fold margin is a 11-34 deg crossing angle at 65 / 65 arcs, so 12 is the same standard), pins of one
body >= PINSEP deg apart (two O20 bearings side by side). Closure residual reported (< 0.5 deg rule).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/virtual-pole-4bar-j2.py [check|jac] ['<json params>']
"""
import json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "virtual-pole-4bar-j2"
NAME = "Virtual-pole spherical four-bar as J2 (all-pin 3-DOF chain, no slide)"
D2R = math.pi / 180
M4, XMIN, PINSEP = 10.0, 12.0, 20.0
# at=2 seed: the plain-3R axes of rail-elbow k2221 (51.33 as a plain 3R) with a converging four-bar around the home J2
PARAMS = dict(at=2, az=0.65, el=76.82, a1=80.71, a2=62.93, beta=110.0, wd=93.82, wa=-4.20, zeta=0.0,
              psiA=35.0, dA0=22.0, dA1=44.0, psiB=-35.0, dB0=22.0, dB1=44.0, sigma=0,   # sigma 0 = auto (at=2 only); at=1 needs +-1
              width=12.0, t_link=3.0, q=1.0)


def unit(x): return K.unit(x)
def rot(k, ang):
    """Rodrigues: rotation matrices (..., 3, 3) about unit axes k (..., 3) by ang (...) deg"""
    k = unit(k); a = np.asarray(ang, float)[..., None, None] * D2R
    Kx = np.zeros(k.shape[:-1] + (3, 3)); Kx[..., 0, 1], Kx[..., 0, 2], Kx[..., 1, 2] = -k[..., 2], k[..., 1], -k[..., 0]
    Kx[..., 1, 0], Kx[..., 2, 0], Kx[..., 2, 1] = k[..., 2], -k[..., 1], k[..., 0]
    return np.eye(3) + np.sin(a) * Kx + (1 - np.cos(a)) * (Kx @ Kx)


def gc(c, ref, psi, d):
    """point at arc d (deg) from c on the great circle leaving c at angle psi (deg) from the arc c -> ref"""
    c = unit(c); t0 = unit(ref - (ref @ c) * c); t = math.cos(psi * D2R) * t0 + math.sin(psi * D2R) * np.cross(c, t0)
    return math.cos(d * D2R) * c + math.sin(d * D2R) * unit(t)


def ang(u, v): return np.degrees(np.arccos(np.clip((unit(u) * unit(v)).sum(-1), -1, 1)))
def frame2(x, y):
    x = unit(x); y = unit(y - (y * x).sum(-1, keepdims=True) * x); return np.stack([x, y, np.cross(x, y)], -1)
def mv(R, u): return np.einsum("...ij,...j->...i", R, u)


class FourBar:
    """spherical four-bar in its ground frame: ground pins a0, b0; coupler pins a1h, b1h at theta = 0"""
    def __init__(self, a0, b0, a1h, b1h):
        self.a0, self.b0, self.a1h, self.b1h = map(unit, (a0, b0, a1h, b1h))
        self.aB, self.g = float(ang(b0, b1h)), float(ang(a1h, b1h))
        self.s = float(np.sign(self.b1h @ np.cross(self.b0, self.a1h)) or 1.0)
        self.E0 = frame2(self.a1h, self.b1h)

    def at(self, th):
        """theta (n,) deg -> a1, b1 (n, 3), coupler rotation Rc (n, 3, 3), four-bar margin (n,) deg"""
        a1 = mv(rot(np.broadcast_to(self.a0, np.shape(th) + (3,)), th), self.a1h)
        b1, ok, mg = K.closure(np.broadcast_to(self.b0, a1.shape), a1, self.aB, self.g, self.s, margin_deg=-999)
        mg = np.where(ok, mg, -90.0)
        Rc = frame2(a1, b1) @ self.E0.T
        return a1, b1, Rc, mg


def layout(p):
    """home geometry (scapula frame for at=2: link 1 at phi = 0 coincides with it; for at=1 the base IS the scapula)"""
    j = K.bvec(p["az"], p["el"]); Y = np.array([0.0, 1.0, 0.0]) if abs(j[1]) < 0.95 else np.array([1.0, 0.0, 0.0])
    t0 = unit(Y - (Y @ j) * j); t0 = mv(rot(j, p.get("zeta", 0.0)), t0)
    j2h = math.cos(p["a1"] * D2R) * j + math.sin(p["a1"] * D2R) * t0          # J2 at home, arc a1 from J1
    if p["at"] == 2:      # pole = J2 home; the coupler carries J3 at arc a2 from it, at dihedral beta from the arc to J1
        pole, ref = j2h, j; carried = gc(j2h, j, p["beta"], p["a2"])
    else:                 # pole = J1 (virtual); the coupler (= link 1) carries J2 at arc a1 from it
        pole, ref = j, j2h; carried = j2h
    pins = [gc(pole, ref, p["psiA"], p["dA0"]), gc(pole, ref, p["psiB"], p["dB0"]),
            gc(pole, ref, p["psiA"], p["dA1"]), gc(pole, ref, p["psiB"], p["dB1"])]
    return j, j2h, pole, carried, FourBar(*pins)


_CACHE = {}
def curve(p):
    """the coupler curve of the carried axis on a 0.25 deg theta grid, restricted to the assembled interval around 0"""
    key = json.dumps({k: p[k] for k in sorted(p) if k not in ("width", "t_link", "q")}, sort_keys=True)
    if key in _CACHE: return _CACHE[key]
    j, j2h, pole, carried, fb = layout(p)
    th = np.arange(-180.0, 180.0, 0.25); a1, b1, Rc, mg = fb.at(th); c = mv(Rc, carried)
    good = mg >= M4; i0 = int(np.argmin(np.abs(th)))
    lo = hi = i0
    if good[i0]:
        while lo > 0 and good[lo - 1]: lo -= 1
        while hi < len(th) - 1 and good[hi + 1]: hi += 1
        full = bool(good.all())
    else: full = False
    sep = min(ang(fb.a0, fb.b0), ang(fb.a1h, fb.b1h), ang(fb.a0, fb.a1h), ang(fb.b0, fb.b1h))
    out = dict(th=th[lo:hi + 1], c=c[lo:hi + 1], valid=bool(good[i0]) and sep >= PINSEP, sep=float(sep), j=j, j2h=j2h,
               pole=pole, carried=carried, fb=fb, full=full)
    if len(_CACHE) > 64: _CACHE.clear()
    _CACHE[key] = out; return out


def solve(cv, z, rho, sigma):
    """per pose: theta with angle(c(theta), z_p) = rho_p, slope sign sigma (0: the sign at theta = 0), nearest theta 0.
    z (P, 3), rho (P,) deg -> theta (P,), ok (P,), crossing angle (P,) deg"""
    th, c = cv["th"], cv["c"]; P = len(z)
    if len(th) < 3: return np.zeros(P), np.zeros(P, bool), np.zeros(P)
    G = c @ z.T - np.cos(rho * D2R)[None]                                     # (n, P)
    s = np.sign(G[1:]) != np.sign(G[:-1]); slope = np.sign(G[1:] - G[:-1])
    if sigma == 0:        # at=2 home branch: slope of c(theta).z at theta 0 (z = j1 is the same in every pose: pose-local)
        i0 = int(np.argmin(np.abs(th))); a, b = max(i0 - 1, 0), min(i0 + 1, len(th) - 1)
        sigma = float(np.sign((c[b] - c[a]) @ z[0])) if len(z) else 1.0
        sigma = sigma or 1.0
    s &= slope == sigma
    mid = 0.5 * (th[1:] + th[:-1]); cost = np.where(s, np.abs(mid)[:, None], np.inf)
    k = np.argmin(cost, 0); ok = np.isfinite(cost[k, np.arange(P)])
    g0, g1 = G[k, np.arange(P)], G[k + 1, np.arange(P)]; f = g0 / np.where(np.abs(g0 - g1) > 1e-15, g0 - g1, 1e-15)
    theta = th[k] + np.clip(f, 0, 1) * (th[k + 1] - th[k])
    dc = (c[k + 1] - c[k]) / ((th[k + 1] - th[k]) * D2R)[..., None]          # d c / d theta (per rad)
    zr = unit(z - (z * c[k]).sum(-1, keepdims=True) * c[k])
    sx = np.abs((dc * zr).sum(-1)) / (np.linalg.norm(dc, axis=-1) + 1e-12)
    return theta, ok, np.degrees(np.arcsin(np.clip(sx, 0, 1)))


def build(B, F, p):
    p = dict(PARAMS, **p); cv = curve(p); P = len(F.RS); fb = cv["fb"]
    RS = F.RS; ST = np.transpose(RS, (0, 2, 1))
    S = lambda u: mv(RS, np.broadcast_to(u, (P, 3)))                           # scapula-frame direction(s) -> thorax
    w = mv(F.RHG, np.broadcast_to(K.wdir(p["wd"], p["wa"]), (P, 3)))           # J3 axis (thorax), fixed in the humerus
    ws = mv(ST, w)                                                             # ... in the scapula frame
    j = cv["j"]
    if p["at"] == 2: z, rho = np.broadcast_to(j, (P, 3)), ang(np.broadcast_to(j, (P, 3)), ws)
    else: z, rho = ws, np.full(P, p["a2"])
    theta, ok, xang = solve(cv, z, rho, p["sigma"]) if cv["valid"] else (np.zeros(P), np.zeros(P, bool), np.zeros(P))
    a1, b1, Rc, mg = fb.at(theta); c = mv(Rc, cv["carried"])
    ok &= (mg >= M4) & (xang >= XMIN)
    res = np.abs(ang(c, z) - rho)
    if p["at"] == 2:
        phi = K.axis_angle(np.broadcast_to(j, (P, 3)), c, ws); R1 = rot(np.broadcast_to(j, (P, 3)), phi)
        J1 = S(j); A0, B0 = S(mv(R1, fb.a0)), S(mv(R1, fb.b0)); A1, B1 = S(mv(R1, a1)), S(mv(R1, b1))
        J3 = S(mv(R1, c)); J2 = S(mv(R1, np.broadcast_to(cv["pole"], (P, 3))))   # (the home pole, for the record only)
        res = np.maximum(res, ang(J3, w))
        q = np.stack([phi, theta, K.axis_angle(B0, A0, B1), K.axis_angle(A1, A0, B1), K.axis_angle(J3, A1, F.HG([0.0, -1, 0]))], -1)
        joints = dict(J1=J1, A0=A0, B0=B0, A1=A1, B1=B1, J3=J3)
        near = "A1" if ang(fb.a1h, cv["carried"]) <= ang(fb.b1h, cv["carried"]) else "B1"
        X = dict(A1=A1, B1=B1)[near]; Xg = A0 if ang(j, fb.a0) <= ang(j, fb.b0) else B0; g_name = "A0" if Xg is A0 else "B0"
        hubs = [K.hub_member(f"hub{n}", v, n) for n, v in joints.items()]
        w_, t_ = p["width"], p["t_link"]
        mem = hubs + [
            K.strap_member("link1", J1, Xg, ("J1", g_name), width=w_, t=t_, ramp_to=(("hubJ1", K.STACK), (f"hub{g_name}", 0.0))),
            K.strap_member("ground", A0, B0, ("A0", "B0"), width=w_, t=t_, ramp_to=(("hubA0", 0.0), ("hubB0", 0.0))),
            K.strap_member("crankA", A0, A1, ("A0", "A1"), width=w_, t=t_, ramp_to=(("hubA0", K.STACK), ("hubA1", 0.0)),
                           over=[("link1", 1.0), ("ground", 1.0)]),
            K.strap_member("crankB", B0, B1, ("B0", "B1"), width=w_, t=t_, ramp_to=(("hubB0", K.STACK), ("hubB1", 0.0)),
                           over=[("link1", 1.0), ("ground", 1.0)]),
            K.strap_member("coupler", A1, B1, ("A1", "B1"), width=w_, t=t_, ramp_to=(("hubA1", K.STACK), ("hubB1", K.STACK))),
            K.strap_member("link2", X, J3, (near, "J3"), width=w_, t=t_, ramp_to=((f"hub{near}", K.STACK), ("hubJ3", K.STACK)),
                           over=[("neck", 1.0), ("link1", 1.0), ("ground", 1.0)]),
            K.neck_member(F, J3, joints=("J3",), ramps=(("hubJ3", 0.0), (None, 0)))]
    else:
        J2 = S(c); A0, B0 = S(np.broadcast_to(fb.a0, (P, 3))), S(np.broadcast_to(fb.b0, (P, 3))); A1, B1 = S(a1), S(b1)
        J3 = w; res = np.maximum(res, np.abs(ang(J2, J3) - p["a2"]))
        q = np.stack([theta, K.axis_angle(B0, A0, B1), K.axis_angle(A1, A0, B1), K.axis_angle(J2, A1, J3),
                      K.axis_angle(J3, J2, F.HG([0.0, -1, 0]))], -1)
        joints = dict(A0=A0, B0=B0, A1=A1, B1=B1, J2=J2, J3=J3)
        near = "A1" if ang(fb.a1h, cv["carried"]) <= ang(fb.b1h, cv["carried"]) else "B1"
        X = dict(A1=A1, B1=B1)[near]
        hubs = [K.hub_member(f"hub{n}", v, n) for n, v in joints.items()]
        w_, t_ = p["width"], p["t_link"]
        mem = hubs + [
            K.strap_member("ground", A0, B0, ("A0", "B0"), width=w_, t=t_, ramp_to=(("hubA0", 0.0), ("hubB0", 0.0))),
            K.strap_member("crankA", A0, A1, ("A0", "A1"), width=w_, t=t_, ramp_to=(("hubA0", K.STACK), ("hubA1", 0.0)),
                           over=[("ground", 1.0)]),
            K.strap_member("crankB", B0, B1, ("B0", "B1"), width=w_, t=t_, ramp_to=(("hubB0", K.STACK), ("hubB1", 0.0)),
                           over=[("ground", 1.0)]),
            K.strap_member("coupler", A1, B1, ("A1", "B1"), width=w_, t=t_, ramp_to=(("hubA1", K.STACK), ("hubB1", K.STACK))),
            K.strap_member("link1", X, J2, (near, "J2"), width=w_, t=t_, ramp_to=((f"hub{near}", K.STACK), ("hubJ2", 0.0))),
            K.strap_member("link2", J2, J3, ("J2", "J3"), width=w_, t=t_, ramp_to=(("hubJ2", K.STACK), ("hubJ3", K.STACK)),
                           over=[("neck", 1.0), ("ground", 1.0)]),
            K.neck_member(F, J3, joints=("J3",), ramps=(("hubJ3", 0.0), (None, 0)))]
    okr = ok & (res < 0.5)
    info = dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None, pin_sep_deg=round(cv["sep"], 1),
                theta_span=[round(float(cv["th"][0]), 1), round(float(cv["th"][-1]), 1)] if len(cv["th"]) else None,
                min_cross_deg=round(float(xang[ok].min()), 1) if ok.any() else None)
    return K.Chain(members=mem, ok=okr, q=q, joints=joints, info=info)


def jac(p, B=None):
    """mobility check on data: numeric Jacobian of the arm's rotation w.r.t. the 3 actuated coordinates, rank per pose"""
    p = dict(PARAMS, **p); cv = curve(p); fb = cv["fb"]; th = cv["th"]; out = []
    rng = np.random.default_rng(0)
    for t in rng.choice(th[5:-5], size=min(40, max(len(th) - 10, 0)), replace=False) if len(th) > 12 else []:
        def R(phi, theta, q3):                       # the arm's rotation in the ground (scapula) frame
            Rc = fb.at(np.array([theta]))[2][0]
            if p["at"] == 2: return rot(cv["j"], phi) @ Rc @ rot(cv["carried"], q3)
            w2 = gc(cv["j2h"], cv["j"], 90.0, p["a2"])   # J3 in link 2 (any fixed direction at arc a2 from J2)
            return Rc @ rot(cv["carried"], phi) @ rot(w2, q3)
        x0 = np.array([10.0, float(t), 5.0]); R0 = R(*x0); J = []
        for k in range(3):
            e = np.zeros(3); e[k] = 1e-3; dR = (R(*(x0 + e)) - R(*(x0 - e))) / 2e-3 @ R0.T
            J.append([dR[2, 1], dR[0, 2], dR[1, 0]])
        sv = np.linalg.svd(np.array(J).T, compute_uv=False); out.append(sv[-1] / sv[0])
    return np.array(out)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "jac":
        r = jac(par); print("min / median sigma_min/sigma_max of the 3x3 rotation Jacobian:", r.min() if len(r) else None, np.median(r) if len(r) else None, len(r)); sys.exit()
    B = K.bench(60, 160); P = dict(PARAMS, **par)
    rep = K.evaluate(B, build, P)
    print({k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                    "honest", "audit", "residual_deg", "pin_sep_deg", "theta_span", "min_cross_deg", "mass_g")})
    print(rep["inband_member"])
