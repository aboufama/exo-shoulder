"""virtual-j2-knee-3r: the J2 of a GH-centred 3R realised as a PLANAR TRIPLE of pins closed through the wearer
(near-zero-closure track, 2026-10-16). Gate + theory: docs/research/nzc/ (closures.md, j2knee_gate.py).

Chain: scapula -J1 (O20 hub, active, axis on a GH ray u1)- link 1 -J2 (O20 hub at P, active, axis PARALLEL to the
virtual J2 direction w but offset rho_P from the w-line)- crank -pin a (O20, passive, || w)- knee link -pin b (O20,
passive, || w)- link 2 -J3 (O20 hub, active, axis on a GH ray u3)- member 3 (hub-3 plate + K7 neck on BOTTOM's bar).

Kinematics (exact, closed form). Every joint is either on a GH line (J1, J3, the wearer's GH) or parallel to w (J2, a,
b): the w-height of GH is invariant, so the loop is the 2-pin-knee closure (offset-skin-normal-3r's theorem) applied in
the MIDDLE of the chain. Link 2 turns about the VIRTUAL w-line through GH: orientation = R(u1, q1) R(w, theta) R(u3, q3),
the spherical 3R of arcs a1 = angle(u1, w), a2 = angle(w, u3) (K1 closure, fold margin 5). The knee (P -> pin a ->
pin b) is a two-circle closure in the plane normal to w; theta = qJ2 + qa + qb. Loop mobility 3 (the arm's), no
undetermined coordinate on the bench: with q locked the loop (arm 3 + pins a, b) has 5 freedoms against 5 independent
constraints (rank checked numerically in docs/research/nzc/closures.md). Hub 2 is no longer on the w-ray, which is the
zero-complexity class's measured cap (hub 2 F 60 -> 107 mm as a1 38 -> 62, docs/concepts/zc-frontier-3r.md).

Parts: four... six O20 v5 hubs (MR117-2RS pair, 12.25 mm stack): J1, J2, pin a, pin b, J3 (+ none on the virtual line);
"Keep O20 only" applied to the passive pins too (conservative: iglidur pins would be 5 mm). Crank and knee link: flat
3 mm Ti plates normal to w, 10 mm wide, with O20 ring ends (2 mm sample grid), each at ONE level along w (fitted K4:
every sample marched along w from its true in-plane offset); stack: link 1 lower / crank upper at J2, crank lower /
knee upper at a, knee lower / link 2 upper at b. Links 1, 2: 12 x 3 straps (K5). Neck: K7 14 x 6.
Checks: kit K1-K7, dense K2 on every joint value and axis, K6 1 mm radial (the zc / verifier setting), audit.

    OMP_NUM_THREADS=1 nice python3 docs/concepts/models/virtual-j2-knee-3r.py '<json params>'
"""
import functools, json, math, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                       # noqa: E402

ID = "virtual-j2-knee-3r"
NAME = "Virtual-J2 knee 3R: J2 as a planar pin triple (1 active + 2 passive pins || w) closed through the wearer"
PARAMS = dict(az=109.36, el=65.94, wd=85.74, wa=-16.19, a1=52.0, a2=70.0, sigma=-1,
              rhoP=28.0, psiP=30.0, rhoB=24.0, psiB=30.0, la=24.0, lk=24.0, kb=1, h0=58.0, hA=58.0, hB=58.0,
              q=0.97, end_extra=0.0, margin=5.0, width=12.0, t_link=3.0, ang_min=30.0)
BOUNDS = dict(az=(-110.0, 135.0), el=(-20.0, 90.0), wd=(20.0, 175.0), wa=(-180.0, 180.0), a1=(25.0, 80.0), a2=(30.0, 120.0),
              rhoP=(0.0, 50.0), psiP=(-180.0, 180.0), rhoB=(0.0, 50.0), psiB=(-180.0, 180.0), la=(21.0, 45.0),
              lk=(21.0, 45.0), h0=(40.0, 110.0), hA=(40.0, 110.0), hB=(40.0, 110.0), q=(0.85, 1.0), end_extra=(0.0, 6.0))
PL_T, PL_W = 3.0, 10.0
RIG_MIN = 0.17                 # |sin| >= 0.17 (10 deg): the locked-q loop stays rigid (docs/research/nzc/closures.md)

if not getattr(K.collisions, "_zc_1mm", False):                               # the verifier's 1 mm radial K6
    K.collisions = functools.partial(K.collisions, overlap=1.0 - 1e-4); K.collisions._zc_1mm = True


# ---- kit extension: a 'flat' member whose plane frame has a per-pose ORIGIN O0 (P, 3) off the GH line ---------------
# (a pin || w that is not on a GH line, and the plates of the planar group). Identical to the kit's K4 otherwise: every
# sample is marched along K from its TRUE position O0 + x A + y Bv. Members without O0 are untouched.
if not getattr(K, "_vj2_O0", False):
    _lv0, _mp0 = K._levels, K.member_points

    def _levels(B, chain, fit, q, mode):
        Pi = np.nonzero(fit)[0]; segs = []; rays = []; orig = []
        for m in chain.members:
            if m.kind == "flat":
                n = len(m.xy); Dm = np.broadcast_to(m.K[Pi][:, None, :], (len(Pi), n, 3))
                Om = m.xy[None, :, :1] * m.A[Pi][:, None, :] + m.xy[None, :, 1:] * m.Bv[Pi][:, None, :]
                if getattr(m, "O0", None) is not None: Om = Om + m.O0[Pi][:, None, :]
            else:
                Dm = m.D[Pi]; Om = np.zeros_like(Dm)
            segs.append(Dm.shape[1]); rays.append(Dm.reshape(-1, 3)); orig.append(Om.reshape(-1, 3))
        I = np.concatenate([np.repeat(Pi, s) for s in segs]) if len(Pi) else np.zeros(0, int)
        cat = lambda L: np.concatenate(L) if L else np.zeros((0, 3))
        R = K.requirement(B, I, cat(rays), mode=mode, O=cat(orig))
        out = {}; o = 0
        for m, s in zip(chain.members, segs):
            Rm = R[o:o + len(Pi) * s].reshape(len(Pi), s); o += len(Pi) * s; qq = m.q if m.q is not None else q
            out[m.name] = K.quantile(Rm, qq) if len(Pi) else np.full(s, 400.0)
        return out

    def member_points(m, rho):
        p = _mp0(m, rho)
        if m.kind == "flat" and getattr(m, "O0", None) is not None: p = p + m.O0[:, None, :]
        return p

    K._levels, K.member_points, K._vj2_O0 = _levels, member_points, True


if not getattr(K.collisions, "_vj2_pins", False):
    _col0 = K.collisions

    def _collisions(chain, pts, ok, **kw):
        """K6 with the offset pins' joint rays taken through the FITTED pin-disc centres (the kit exempts joint partners
        within HUB_R + 2 mm of a joint ray through GH; an offset pin's ray must pass through its real centre)"""
        pm = getattr(chain, "_pinmap", None)
        if pm:
            J = dict(chain.joints)
            for j, mname in pm.items(): J[j] = K.unit(pts[mname].mean(1))
            chain = K.Chain(members=chain.members, ok=chain.ok, q=chain.q, joints=J, info=chain.info, hubless=chain.hubless)
        return _col0(chain, pts, ok, **kw)
    _collisions._zc_1mm = True; _collisions._vj2_pins = True
    K.collisions = _collisions


def flat_member(name, k, a, O0, xy, joints, t, h0, ramps=()):
    k = K.unit(k); b = np.cross(k, a)
    D = K.unit(h0 * k[:, None] + O0[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    m = K.Member(name, D, kind="flat", t=t, width=2 * K.HUB_R, joints=tuple(joints), K=k, A=a, Bv=b, xy=xy, cell=4.0)
    m.O0 = O0; m.ramps = list(ramps); return m


def plate_xy(L, w=PL_W, rad=K.HUB_R, ends=(True, True)):
    """a straight plate from (0,0) to (L,0), width w, with O20 ring ends (2 mm grid)"""
    xy = K.rect_xy(L, w) + np.array([L / 2, 0.0])
    parts = [xy] + [K.disc_xy(rad) + np.array([x, 0.0]) for x, e in zip((0.0, L), ends) if e]
    P = np.unique(np.round(np.concatenate(parts), 3), axis=0); return P


def seat_ok(az, el):
    u = K.bvec(az, el); return bool(-110.0 <= az <= 135.0 and -20.0 <= el <= 90.0 and u[0] <= 0.20)


def snap(p):
    p = dict(PARAMS, **p)
    for k_, (lo, hi) in BOUNDS.items():
        if k_ in ("wa", "psiP", "psiB"): p[k_] = (float(p[k_]) + 180.0) % 360.0 - 180.0
        else: p[k_] = min(hi, max(lo, float(p[k_])))
    p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1; p["kb"] = 1 if float(p["kb"]) >= 0 else -1
    for k_ in ("margin", "width", "t_link", "ang_min"): p[k_] = PARAMS[k_]
    return p


def geometry(F, p):
    """closed-form kinematics per pose -> dict (pose-local: uses F only)"""
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    w, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    e1 = K.unit(p1 - (p1 * w).sum(1, keepdims=True) * w); e2 = np.cross(w, e1)        # link-1 plane basis (normal w)
    f1 = K.unit(p3 - (p3 * w).sum(1, keepdims=True) * w); f2 = np.cross(w, f1)        # link-2 plane basis
    cP, sP = math.cos(math.radians(p["psiP"])), math.sin(math.radians(p["psiP"]))
    cB, sB = math.cos(math.radians(p["psiB"])), math.sin(math.radians(p["psiB"]))
    OP = p["rhoP"] * (cP * e1 + sP * e2); OB = p["rhoB"] * (cB * f1 + sB * f2)
    v = OB - OP; d = np.linalg.norm(v, axis=1); la, lk = p["la"], p["lk"]
    vx, vy = (v * e1).sum(1), (v * e2).sum(1); gam = np.arctan2(vy, vx)
    ca = (la ** 2 + d ** 2 - lk ** 2) / (2 * la * np.maximum(d, 1e-9)); al = np.arccos(np.clip(ca, -1, 1))
    th = gam + p["kb"] * al
    OA = OP + la * (np.cos(th)[:, None] * e1 + np.sin(th)[:, None] * e2)
    u = OP - OA; t = OB - OA
    knee = np.degrees(np.arccos(np.clip((u * t).sum(1) / (la * lk), -1, 1)))
    amin = p["ang_min"]
    # sensing / rigidity margin: with q locked the loop is rigid iff pins a, b and the virtual axis are not collinear in
    # the knee plane (their moments OA x w, OB x w independent); |sin(OA, OB)| is the conditioning of the 3-joint reading
    rig = np.linalg.norm(np.cross(OA, OB), axis=1) / (np.linalg.norm(OA, axis=1) * np.linalg.norm(OB, axis=1) + 1e-9)
    ok = ok & (np.abs(ca) <= 1) & (knee >= amin) & (knee <= 180 - amin) & (rig >= RIG_MIN)
    res = np.linalg.norm(np.linalg.norm(OB - OA, axis=1) - lk) if ok.any() else 0.0
    return dict(p1=p1, p3=p3, w=w, ok=ok, margin=margin, OP=OP, OA=OA, OB=OB, e1=e1, knee=knee, th=th, d=d, f1=f1)


def build(B, F, p):
    g = geometry(F, p); p1, p3, w, ok = g["p1"], g["p3"], g["w"], g["ok"]; h0 = p["h0"]
    OP, OA, OB = g["OP"], g["OA"], g["OB"]
    a_cr = K.unit(OA - OP); a_kn = K.unit(OB - OA)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), w), K.axis_angle(w, p1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), w),
                  np.degrees(np.arctan2((a_cr * np.cross(w, g["e1"])).sum(1), (a_cr * g["e1"]).sum(1))), g["knee"]], -1)
    # joint rays through the pin centres at their NOMINAL levels h0 / hA / hB (search parameters; K6 exempts joint
    # partners within HUB_R + 2 mm of these rays, so a level far from the fitted one only makes K6 stricter)
    hA, hB = p.get("hA", h0), p.get("hB", h0)
    dP, dA, dB = K.unit(h0 * w + OP), K.unit(hA * w + OA), K.unit(hB * w + OB)
    disc = K.disc_xy(K.HUB_R)
    hub1 = K.hub_member("hub1", p1, "J1"); hub3 = K.hub_member("hub3", p3, "J3")
    e1 = g["e1"]
    hub2 = flat_member("hub2", w, e1, OP, disc, ("J2",), K.CROWN, h0)
    crank = flat_member("crank", w, a_cr, OP, plate_xy(p["la"]), ("J2", "Ja"), PL_T, h0, ramps=[(None, "hub2", K.STACK)])
    hubA = flat_member("pin_a", w, a_cr, OA, disc, ("Ja",), K.CROWN, hA, ramps=[(None, "crank", 0.0)])
    knee = flat_member("knee", w, a_kn, OA, plate_xy(p["lk"]), ("Ja", "Jb"), PL_T, hB, ramps=[(None, "pin_a", K.STACK)])
    hubB = flat_member("pin_b", w, a_kn, OB, disc, ("Jb",), K.CROWN, hB, ramps=[(None, "knee", 0.0)])
    for m in (crank, hubA, knee, hubB):                                      # whole-plate ramps (flat parts stay flat)
        m.ramps = [(np.ones(len(m.xy), bool), o, dz) for _, o, dz in m.ramps]
    wl, tl = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    link1 = K.strap_member("link1", p1, dP, ("J1", "J2"), width=wl, t=tl, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end)
    neck = K.strap_member("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), width=14.0, t=6.0, ramp_to=(("hub3", 0.0), (None, 0)))
    link2 = K.strap_member("link2", dB, p3, ("Jb", "J3"), width=wl, t=tl, ramp_to=(("pin_b", K.STACK), ("hub3", K.STACK)),
                           end_mm=end, over=[("link1", 1.0), ("neck", 1.0)])
    members = [hub1, hub2, hub3, crank, hubA, knee, hubB, link1, neck, link2]
    info = dict(knee_min=round(float(g["knee"][ok].min()), 1) if ok.any() else None,
                knee_max=round(float(g["knee"][ok].max()), 1) if ok.any() else None,
                d_min=round(float(g["d"][ok].min()), 1) if ok.any() else None, d_max=round(float(g["d"][ok].max()), 1) if ok.any() else None,
                residual_deg=round(float(K.closure_residual(p1, p3, w, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None)
    ch = K.Chain(members=members, ok=ok, q=q, joints=dict(J1=p1, J2=dP, J3=p3, Ja=dA, Jb=dB, Jv=w), info=info,
                 hubless=("Jv", "J2", "Ja", "Jb"))
    ch._pinmap = {"J2": "hub2", "Ja": "pin_a", "Jb": "pin_b"}
    return ch
    # J2 / Ja / Jb are OFFSET pins (axis || w, not on a GH line): the kit's centring audit measures about GH lines only, so
    # they are listed as hubless for the audit; their O20 discs (disc_xy(10), 12.25 mm crown) are built by construction
    # above (hub2, pin_a, pin_b). Jv = the virtual J2 line through GH: no metal on it, by design.


def evaluate(B, p, **kw):
    p = snap(p)
    if not seat_ok(p["az"], p["el"]): return p, dict(gap=200.0, note="J1 seat outside the ruling")
    r = K.evaluate(B, build, p, **kw)
    return p, r


if __name__ == "__main__":
    import time
    p = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    nc, nw = (int(os.environ.get("NC", 60)), int(os.environ.get("NW", 160)))
    B = K.bench(nc, nw); t0 = time.time()
    p, r = evaluate(B, p)
    keep = ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide", "honest", "audit",
            "inband_member", "knee_min", "knee_max", "d_min", "d_max", "residual_deg", "mass_g")
    print(json.dumps(dict(params=p, **{k: r.get(k) for k in keep}, secs=round(time.time() - t0, 1)), indent=1, default=str))
