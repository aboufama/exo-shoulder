"""Concept model: CUFF-SLAVED ELBOW at the cap pole (id cuff-slaved-elbow-fourbar-3r) - round 102 lens 1 (virtual J2),
pick 2; the base-tethered variant (scapula-tether-elbow-3r) is merged as cell B (mode 'tether').

A 4R path J1 -(d0)- A0 -(L)- A1 -(d1)- J3 with no metal on a J2 axis: the elbow (A0, A1) is SLAVED by a crank B.
  cell A, mode 'arm':    scapula -J1- link 1 -A0- crank A (ternary A0, A1, B0') -A1- coupler (A1, J3) -J3- arm end
                         (J3, B1, K7 neck); loop: crank A -B0'- crank B -B1- arm end. In the ARM frame this loop is a
                         spherical four-bar (ground J3-B1, input = the coupler about J3, output = crank B about B1,
                         floating link = crank A), and crank A's third pin A0 must meet link 1 (the 2R J1-A0-A1).
  cell B, mode 'tether': scapula -J1- link 1 -A0- crank A -A1- coupler (B1, A1, J3) -J3- arm; loop: scapula -B0-
                         tether -B1- coupler (spherical five-bar).
Mobility (spherical Grubler): 6 bodies, 6 revolutes: M = 3 x 5 - 2 x 6 = 3. ACTIVE J1, A0, J3; PASSIVE A1, B0, B1, set
per pose by ONE root in the coupler spin sigma about J3 (the loop equation angle(B0, B1) = rho), then the closed-form
2R closure J1-A0-A1: no undetermined coordinate (R17), 0 passive translations, no gears / pulleys / cables (MVP1).

Per pose: sigma on a 2-deg grid, the sign changes of f(sigma) = angle(B0, B1) - rho with slope sign `sgn` (the loop's
assembly branch), the one nearest `home` (circular), bisected to < 0.01 deg. Determinacy margins (all enforced in ok):
2R closure margin >= K.FOLD_MARGIN (the dyad J1-A0-A1's fold, read like th: angle(J1, A1) vs |d0 - L|, d0 + L),
|df/dsigma| >= sin 8 deg (the whole loop's singularity), the four-bar transmission angles at A1 (coupler vs crank A)
and B0 (crank A vs crank B) in [MU, 180 - MU] (arm mode; tether: at B1 and B0), pins >= PINSEP apart in every body.
Every pin an O20 v5 stack (Keep O20 only), 3 x 12 Ti straps, kit K2 dense / K3 march / K6 / audit.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cuff-slaved-elbow-fourbar-3r.py check '<json params>'
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "cuff-slaved-elbow-fourbar-3r"
NAME = "Cuff-slaved elbow: 4R path J1-A0-A1-J3 at the cap pole, elbow slaved by a crank to an arm-cuff pin (tether cell B)"
D2R = math.pi / 180
MU, PINSEP, CROSS = 30.0, 22.0, math.sin(8 * D2R)
END = K.HUB_R + 8.0      # stack-ramp zone round every pin (mm at r_ref; kit default HUB_R + 2): measured on arm seed 1,
                         # the upper member left its stack 12 mm from A0 and met the lower one 0.5 mm apart (K6)
SEAT = dict(az=43.15, el=59.93, wd=92.03, wa=-9.03)              # cap pole J1 / J3 (round-102 planner)
NM = ["d0", "L", "d1", "sb", "db", "rho", "bx", "by", "home"]
ARM1 = dict(d0=31.6, L=29.5, d1=71.0, sb=36.3, db=43.6, rho=53.7, bx=-168.1, by=22.2, home=27.3, s2=-1, sgn=-1)
ARM2 = dict(d0=32.7, L=42.4, d1=46.0, sb=49.3, db=32.6, rho=30.2, bx=-121.1, by=23.2, home=69.4, s2=-1, sgn=-1)
TET1 = dict(d0=27.2, L=44.3, d1=45.8, sb=-19.1, db=62.0, rho=48.4, bx=100.5, by=72.8, home=29.1, s2=1, sgn=1)
TET2 = dict(d0=23.7, L=26.4, d1=61.4, sb=61.7, db=63.5, rho=59.3, bx=48.7, by=36.8, home=-165.8, s2=1, sgn=1)
PARAMS = dict(SEAT, mode="arm", **ARM1, width=12.0, t_link=3.0, q=1.0)
LO = dict(arm=[18, 25, 45, -180, 22, 22, -180, 22, -180], tether=[18, 25, 45, -180, 25, 22, -40, 30, -180])
HI = dict(arm=[35, 50, 75, 180, 45, 70, 180, 45, 180], tether=[35, 50, 75, 180, 75, 75, 140, 85, 180])


def U(x): return K.unit(x)
def ang(a, b): return np.degrees(np.arccos(np.clip((U(a) * U(b)).sum(-1), -1, 1)))
def vang(c, u, v):
    """angle (deg) at vertex c between the great-circle arcs c -> u and c -> v"""
    tu = U(u - (u * c).sum(-1, keepdims=True) * c); tv = U(v - (v * c).sum(-1, keepdims=True) * c)
    return np.degrees(np.arccos(np.clip((tu * tv).sum(-1), -1, 1)))
def gcv(c, ref, psi, d):
    """point at arc d (deg) from c leaving at angle psi (deg, broadcast) from the arc c -> ref"""
    t0 = U(ref - (ref * c).sum(-1, keepdims=True) * c); t1 = np.cross(c, t0); psi = np.asarray(psi, float)[..., None] * D2R
    return math.cos(d * D2R) * c + math.sin(d * D2R) * U(np.cos(psi) * t0 + np.sin(psi) * t1)


def geom(F, p, sig):
    """sig (P, n) deg -> every pin (P, n, 3), the loop residual f (deg), the 2R closure ok and margin"""
    P, n = sig.shape
    J1 = np.broadcast_to(F.S(K.bvec(p["az"], p["el"]))[:, None], (P, n, 3))
    w = np.broadcast_to(F.HG(K.wdir(p["wd"], p["wa"]))[:, None], (P, n, 3))
    dn = np.broadcast_to(F.HG(np.array([0.0, -1.0, 0.0]))[:, None], (P, n, 3))
    A1 = gcv(w, dn, sig, p["d1"])
    A0, okc, mg = K.closure(J1, A1, p["d0"], p["L"], p["s2"], margin_deg=K.FOLD_MARGIN)
    if p["mode"] == "arm":
        B0 = gcv(A0, A1, p["sb"], p["db"]); B1 = np.broadcast_to(gcv(w[:, :1], dn[:, :1], p["bx"], p["by"]), (P, n, 3))
    else:
        B1 = gcv(w, dn, sig + p["sb"], p["db"]); B0 = np.broadcast_to(F.S(K.bvec(p["bx"], p["by"]))[:, None], (P, n, 3))
    f = ang(B0, B1) - p["rho"]
    return dict(J1=J1, A0=A0, A1=A1, B0=B0, B1=B1, J3=w, dn=dn, f=np.where(okc, f, np.nan), okc=okc, mg=mg)


def solve(F, p):
    """per pose: the loop root sigma on branch sgn nearest home -> pins (P, 3), ok, margins"""
    P = len(F.RS); SG = np.arange(-180.0, 180.0, 2.0); n = len(SG)
    g = geom(F, p, np.broadcast_to(SG, (P, n)).copy()); f = g["f"]; f2 = np.roll(f, -1, 1)
    sc = np.isfinite(f) & np.isfinite(f2) & (np.sign(f) != np.sign(f2)) & (np.sign(f2 - f) == p["sgn"]) & (np.abs(f2 - f) < 90)
    dist = np.abs((SG[None, :] + 1.0 - p["home"] + 180.0) % 360.0 - 180.0)
    cost = np.where(sc, dist, np.inf); k = np.argmin(cost, 1); ok = np.isfinite(cost[np.arange(P), k])
    lo = SG[k].astype(float); hi = lo + 2.0; flo = f[np.arange(P), k]
    for _ in range(9):                                               # bisection to 2 / 512 deg
        mid = 0.5 * (lo + hi); fm = geom(F, p, mid[:, None])["f"][:, 0]
        left = np.isfinite(fm) & (np.sign(fm) == np.sign(flo))
        lo = np.where(left, mid, lo); flo = np.where(left, fm, flo); hi = np.where(left, hi, mid)
    s = 0.5 * (lo + hi); g = geom(F, p, s[:, None]); pin = {k_: g[k_][:, 0] for k_ in ("J1", "A0", "A1", "B0", "B1", "J3", "dn")}
    res = np.abs(np.nan_to_num(g["f"][:, 0], nan=99.0)); ok &= g["okc"][:, 0] & (res < 0.5)
    e = 0.5; gp, gm = geom(F, p, (s + e)[:, None])["f"][:, 0], geom(F, p, (s - e)[:, None])["f"][:, 0]
    dfd = np.abs(np.nan_to_num((gp - gm) / (2 * e))); ok &= dfd >= CROSS
    A0, A1, B0, B1, J1, J3 = (pin[x] for x in ("A0", "A1", "B0", "B1", "J1", "J3"))
    if p["mode"] == "arm":
        tr = np.minimum(vang(A1, J3, B0), vang(B0, A1, B1))           # four-bar transmissions in the arm frame
        sep = np.minimum.reduce([ang(J1, A0), ang(A0, A1), ang(A0, B0), ang(A1, B0), ang(A1, J3), ang(B1, J3), ang(B0, B1)])
    else:
        tr = np.minimum(vang(B1, A1, B0), vang(B0, J1, B1))
        sep = np.minimum.reduce([ang(J1, A0), ang(A0, A1), ang(A1, J3), ang(B1, A1), ang(B1, J3), ang(B0, J1), ang(B0, B1)])
    tr = np.minimum(tr, 180 - tr); ok &= (tr >= MU) & (sep >= PINSEP - 1e-6)
    return dict(pin, ok=ok, sigma=s, res=res, dfd=dfd, tr=tr, mg=g["mg"][:, 0])


def strap(name, u, v, joints, p, ramps, over=()):
    return K.strap_member(name, u, v, joints, width=p["width"], t=p["t_link"], ramp_to=ramps, end_mm=END, over=list(over))


def polystrap(name, pts, joints, p, ramps, over=()):
    """one rigid body along a polyline of pins (each leg a K5 strap, same width): one Member, a stack ramp at every pin"""
    legs = [K.strap_member(f"{name}_{i}", pts[i], pts[i + 1], joints, width=p["width"], t=p["t_link"]) for i in range(len(pts) - 1)]
    nc = legs[0].grid[1]; D = np.concatenate([L_.D for L_ in legs], 1); ns = [L_.grid[0] for L_ in legs]; S = sum(ns)
    s = np.repeat(np.arange(S), nc); ne = int(math.ceil(END / 2.0)) + 1; cuts = np.cumsum([0] + ns); out = []
    for v, (h, dz) in enumerate(ramps):
        if not h: continue
        c = cuts[v] if v < len(cuts) - 1 else S
        m = (s >= c - ne) & (s < c + ne) if 0 < v < len(pts) - 1 else ((s < ne) if v == 0 else (s >= S - ne))
        out.append((m, h, dz))
    return K.Member(name, D, t=p["t_link"], width=p["width"], joints=tuple(joints), grid=(S, nc), climb_deg=60.0, ramps=out,
                    strap=True, over=list(over))


def build(B, F, p):
    p = dict(PARAMS, **p); s = solve(F, p); ok = s["ok"]
    J1, A0, A1, B0, B1, J3, dn = (s[x] for x in ("J1", "A0", "A1", "B0", "B1", "J3", "dn"))
    joints = dict(J1=J1, A0=A0, A1=A1, B0=B0, B1=B1, J3=J3)
    q = np.stack([K.axis_angle(J1, F.S(np.array([1.0, 0, 0])), A0), K.axis_angle(A0, J1, A1), s["sigma"],
                  K.axis_angle(B0, A1 if p["mode"] == "arm" else J1, B1), K.axis_angle(B1, J3 if p["mode"] == "arm" else A1, B0)], -1)
    mem = [K.hub_member(f"hub{n_}", v, n_) for n_, v in joints.items()]
    S_ = K.STACK
    if p["mode"] == "arm":
        # layers (K6 by construction, `over` processed in list order): link 1, crank B, the arm-end tab B1 -> J3 and the
        # neck low (crank B is the lower member at B0 and B1, the arm end lower at J3, link 1 lower at A0); crank A over
        # link 1 / crank B / the J1 stack (upper at A0, B0); the coupler on top (upper at A1 and J3) over everything it
        # crosses, incl. hub B1's stack next to J3. Measured on arm seed 1 without it: crank A vs link 1 137/154,
        # hub B1 vs coupler 105/154 closing poses collide.
        mem += [strap("crankB", B0, B1, ("B0", "B1"), p, (("hubB0", 0.0), ("hubB1", 0.0)), over=[("hubJ1", 1.0)]),
                strap("tab", B1, J3, ("B1", "J3"), p, (("hubB1", S_), ("hubJ3", 0.0))),
                K.neck_member(F, J3, joints=("J3",), ramps=(("hubJ3", 0.0), (None, 0))),
                strap("link1", J1, A0, ("J1", "A0"), p, (("hubJ1", S_), ("hubA0", 0.0))),
                polystrap("crankA", [A1, A0, B0], ("A1", "A0", "B0"), p, [("hubA1", 0.0), ("hubA0", S_), ("hubB0", S_)],
                          over=[("hubJ1", 1.0), ("link1", 1.0), ("crankB", 1.0)]),
                strap("coupler", A1, J3, ("A1", "J3"), p, (("hubA1", S_), ("hubJ3", S_)),
                      over=[("neck", 1.0), ("tab", 1.0), ("crankB", 1.0), ("crankA", 1.0), ("link1", 1.0), ("hubB1", 1.0)])]
    else:
        mem += [strap("tether", B0, B1, ("B0", "B1"), p, (("hubB0", S_), ("hubB1", 0.0)), over=[("hubJ1", 1.0)]),
                K.neck_member(F, J3, joints=("J3",), ramps=(("hubJ3", 0.0), (None, 0))),
                strap("link1", J1, A0, ("J1", "A0"), p, (("hubJ1", S_), ("hubA0", 0.0))),
                strap("crankA", A0, A1, ("A0", "A1"), p, (("hubA0", S_), ("hubA1", 0.0)),
                      over=[("hubJ1", 1.0), ("link1", 1.0), ("tether", 1.0)]),
                polystrap("coupler", [B1, A1, J3], ("B1", "A1", "J3"), p, [("hubB1", S_), ("hubA1", S_), ("hubJ3", S_)],
                          over=[("neck", 1.0), ("tether", 1.0), ("crankA", 1.0), ("link1", 1.0)])]
    info = dict(residual_deg=round(float(s["res"][ok].max()), 5) if ok.any() else None,
                min_2R_margin=round(float(s["mg"][ok].min()), 3) if ok.any() else None,
                min_transmission=round(float(s["tr"][ok].min()), 1) if ok.any() else None,
                min_dfdsigma=round(float(s["dfd"][ok].min()), 3) if ok.any() else None,
                closure_ws=round(float(ok[F.ws].mean()), 4) if F.ws.any() else None)
    return K.Chain(members=mem, ok=ok, q=q, joints=joints, info=info)


def near_touch(B, thr=1.0):
    """the bench report with metal < thr mm counted as contact (the search objective, CLAUDE.md)"""
    ws = [j for j, k in enumerate(B.kind) if k == "ws"]; cl = [j for j, k in enumerate(B.kind) if k == "clip"]
    ok = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= thr
    tk = [j for j in cl if ok(j)]; d = np.concatenate([B.res[j] for j in tk]) if tk else np.zeros(0)
    nz = [j for j in range(len(B.kind)) if B.res[j] is not None]
    reach = float(np.mean([ok(j) for j in ws])); follow = float(np.mean([ok(j) for j in cl]))
    ib = float(np.mean((d >= 2) & (d <= 14))) if len(d) else 0.0
    con = float(np.mean([float(np.min(B.res[j])) < thr for j in nz])) if nz else 0.0
    from concept_bench import gap_of
    return dict(gap_nt=gap_of(ib, follow, reach, con), reach_nt=round(reach, 4), contact_nt=round(con, 4),
                min_metal_mm=round(min(float(np.min(B.res[j])) for j in nz), 2) if nz else None)


def vec(x, mode="arm"):
    lo, hi = np.array(LO[mode], float), np.array(HI[mode], float); x = np.asarray(x, float)
    x = x.copy(); x[[3, 6, 8]] = (x[[3, 6, 8]] + 180) % 360 - 180; return dict(zip(NM, np.clip(x, lo, hi).tolist()))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    nc, nw = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (60, 160)
    B = K.bench(nc, nw); t0 = time.time(); rep = K.evaluate(B, build, dict(PARAMS, **par)); nt = near_touch(B)
    print({k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "closure_ws", "flips",
                                    "collide", "honest", "audit", "residual_deg", "min_2R_margin", "min_transmission",
                                    "min_dfdsigma", "mass_g")}, nt, round(time.time() - t0, 1), "s")
    print(rep["inband_member"])
