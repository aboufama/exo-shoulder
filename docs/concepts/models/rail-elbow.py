"""rail-elbow: a spherical 3R whose middle joint J2 is a curved RAIL on link 1, so link 2 shrinks to a carriage beside the
arm-end hub (3 ACTIVE DOF, 0 passive). Spec: docs/concepts/catalogue.json entry "rail-elbow"; write-up
docs/concepts/rail-elbow.md. Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    base (scapula handler) -- J1 O20 hub, axis b fixed in the scapula (lower member: base, upper: link 1)
    -> link 1 = strap 1 (12 x 3) from the J1 hub to the END of a circular rail (8 wide x 5 radial), fixed on link 1:
       the circle at polar angle alpha = a2 + d_off about the J2 axis p2 (p2 is fixed in link 1 at a1 from b), at ONE
       constant distance from GH (a rigid carriage rolling on a rail about p2 can only run on such a circle).
       There is no hub and no metal at p2's pole.
    -- J2: a rolling carriage (20 long x 16 wide, 9 radial, underside at the rail's underside) on the rail; its azimuth
       psi about p2 is the J2 joint value; the rail spans the carriage travel + half a carriage + a 3 mm end stop at
       both ends + a 12 mm fixing tab at the end strap 1 holds.
    -> link 2 = carriage + a bridge strap (12 x 3) from the carriage's side to the J3 upper plate
    -- J3 O20 hub, axis W fixed in the humerus (deltoid cap); lower member = the arm-end plate
    -> arm-end plate + neck (14 x 6) to BOTTOM's bar (K7).
DOF: q1 (about b), psi (about p2), q3 (about W): a spherical 3R. All three follow from the two-circle closure of b and
W on branch sigma, with no spare coordinate: 3 active, 0 passive.

Spec changes (measured / argued in docs/concepts/rail-elbow.md):
  * strap 1 joins the rail at its END (beyond the carriage travel), not at its mid-point: a carriage that grips both
    rail edges cannot pass a mid-span support;
  * rail extent = carriage travel over the closing bench poses (quantile `cov`, + `tmarg` deg), + half a carriage
    + 3 mm end stop (+ 12 mm tab at the strap end), instead of +-15 deg;
  * humerus axes in the band frame (F.HG), as the kit and the champion (KIT.md: the spec's RH is 12 deg off).
Members (every part at real size, kit sampling): hub1, strap1, rail (+ the carriage's two 4 mm overhang strips beside
the rail: one constant radius = max over all their samples and fit poses, the spec's rho_T - 5), bridge, hub3, neck.
K6 exemptions beyond the kit's shared-joint rule, all of them parts of ONE rigid body or the rail joint itself:
  * bridge vs rail member: the bridge is bolted to the carriage (in the rail member) and only meets the rail AT the
    carriage (the rail joint); it runs across the rail, away from the rest of it;
  * strap 1 vs rail: exempt only within 12 mm of the rail end it is fixed to (the tab, pseudo-joint L1r; the
    carriage never comes within 13 mm of it); everywhere else checked.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/rail-elbow.py [check|sweep STAGE|redteam]
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "rail-elbow"
NAME = "Rail elbow: J2 is a curved rail on link 1, link 2 a carriage beside the arm-end hub"
D2R = math.pi / 180
RAIL_W, RAIL_T = 8.0, 5.0                                    # rail section (spec)
CAR_L, CAR_W, CAR_T = 20.0, 16.0, 9.0                        # carriage block: [R, R + 9] radially, 16 wide over an 8 rail
END_STOP, TAB = 3.0, 12.0
R_REF = 70.0                                                 # layout radius of angular samples (kit convention)

SEED_C = dict(az=2.4305, el=80.6763, a1=76.9018, a2=66.7492, wd=86.3277, wa=21.8297, sigma=-1)   # champion r20 s1414 #4
SEED_A = dict(az=32.55, el=80.56, a1=77.41, a2=81.45, wd=71.38, wa=4.78, sigma=-1)                 # r18 s1392 #1 (spec)
SEED_B = dict(SEED_A, wd=112.0, wa=-15.0)                                                          # spec seed B
PARAMS = dict(SEED_C, margin=10.0, d_off=-40.0, q=1.0, cov=1.0, tmarg=5.0, tele=1, r_lay=142.5)   # best (sweep k64, gap 71.15)
# the spec's rigid rail: dict(PARAMS, tele=0, r_lay=70.0); the cam-track rail: dict(PARAMS, tele=0, cam=1, q_rail=0.95, cam_climb=45.0)
SWEEP = dict(d_off=[-25.0, -20.0, 20.0, 25.0], q=[0.95, 1.0], cov=[0.9, 1.0])


def kin(F, p):
    """the 3R chain: J1 axis p1, J2 axis p2, J3 axis p3, closure ok / margin, the link-1 frame (p2, ref, tt) about p2
    (ref = b projected normal to p2: azimuth 0 = towards J1) and the carriage azimuth psi (deg) = the J2 joint value"""
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"]); p2 = K.unit(p2)
    ref = K.unit(p1 - (p1 * p2).sum(-1, keepdims=True) * p2); tt = np.cross(p2, ref)
    psi = K.axis_angle(p2, ref, p3)
    return p1, p2, p3, ok, margin, ref, tt, psi


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


def on_cone(p2, ref, tt, pol, az):
    """directions at polar angle pol (rad, (P,) or (P, m)) and azimuth az (rad) about p2 in the link-1 frame"""
    pol, az = np.broadcast_arrays(np.asarray(pol, float), np.asarray(az, float))
    ex = lambda v: v.reshape(v.shape[:1] + (1,) * (pol.ndim - 1) + (3,))
    return K.unit(np.cos(pol)[..., None] * ex(p2) + np.sin(pol)[..., None] * (np.cos(az)[..., None] * ex(ref) + np.sin(az)[..., None] * ex(tt)))


def travel(B, F, p):
    """design step (outside build, so build stays pose-local): the carriage travel from the closing bench poses ->
    psi_c (centre), psi_lo / psi_hi (relative, deg), central share `cov`, widened by `tmarg`"""
    *_, ok, _, _, _, psi = kin(F, p)
    if ok.sum() < 5: return dict(psi_c=0.0, psi_lo=0.0, psi_hi=0.0)
    s = psi[ok]; c = float(np.degrees(np.arctan2(np.sin(s * D2R).mean(), np.cos(s * D2R).mean()))); r = wrap(s - c)
    lo, hi = (np.quantile(r, [(1 - p["cov"]) / 2, 1 - (1 - p["cov"]) / 2]) if p["cov"] < 1 else (r.min(), r.max()))
    return dict(psi_c=round(c, 3), psi_lo=round(float(lo) - p["tmarg"], 3), psi_hi=round(float(hi) + p["tmarg"], 3))


def rail_layout(p):
    """rail stations (azimuth rad about p2, relative to the J1 meridian) and which end holds the tab"""
    alpha = (p["a2"] + p["d_off"]) * D2R; rr = p.get("r_lay", R_REF) * math.sin(alpha)
    e_stop = (CAR_L / 2 + END_STOP) / rr; e_tab = e_stop + TAB / rr
    lo, hi = (p["psi_c"] + p["psi_lo"]) * D2R, (p["psi_c"] + p["psi_hi"]) * D2R
    rb = wrap(-p["psi_c"]) * D2R                              # J1's meridian relative to the travel centre
    tab_lo = abs(wrap((rb - p["psi_lo"] * D2R) / D2R)) <= abs(wrap((rb - p["psi_hi"] * D2R) / D2R))
    a0 = lo - (e_tab if tab_lo else e_stop); a1 = hi + (e_stop if tab_lo else e_tab)
    n = max(3, int(math.ceil((a1 - a0) * rr / 2.0)) + 1)
    return alpha, rr, np.linspace(a0, a1, n), (a0 if tab_lo else a1)


def build(B, F, p):
    p1, p2, p3, ok, margin, ref, tt, psi = kin(F, p)
    RL = p.get("r_lay", R_REF)                                # layout radius of the rail parts (2 mm samples there)
    rel = wrap(psi - p["psi_c"]); ok = ok & (rel >= p["psi_lo"]) & (rel <= p["psi_hi"])       # J2 range = the rail
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), psi, K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    alpha, rr, st, s_tab = rail_layout(p); P = len(p1); sg = 1.0 if p["d_off"] >= 0 else -1.0   # sg: the hub lies at -sg (polar)
    xs = np.arange(-CAR_L / 2, CAR_L / 2 + 1e-6, 2.0) / rr
    cam = None
    if p.get("cam"):               # variant: ONE rail whose radius follows the skin per station (a cam track, slope <= cam_climb);
        # the carriage rolls on it, its radial position (and pitch) set by the track; link 2 takes the radius change in a
        # radial guide (6 x 6 foot beside the carriage, reaching down to the carriage's lowest radius): determined by the
        # track, no free coordinate. Rail section kept rigid (max across its width per station).
        ac = np.arange(-RAIL_W / 2, RAIL_W / 2 + 1e-6, 2.0) / RL
        pol = np.broadcast_to((alpha + ac)[None, :], (len(st), len(ac))).ravel(); az = np.repeat(st, len(ac))
        Dr = on_cone(p2, ref, tt, np.broadcast_to(pol, (P, len(pol))), np.broadcast_to(az, (P, len(az))))
        ys = np.array([-8.0, -6.0, 6.0, 8.0]) / RL; X, Y = np.meshgrid(xs, ys, indexing="ij")
        caz = psi[:, None] * D2R + X.ravel()[None, :]
        Dc = on_cone(p2, ref, tt, alpha + Y.ravel()[None, :] + 0 * psi[:, None], caz)
        dst = (st[-1] - st[0]) / (len(st) - 1)
        rail_m = K.Member("rail", Dr, kind="free", r_ref=RL, t=RAIL_T, width=RAIL_W, joints=("L1r", "J2car"), grid=(len(st), len(ac)),
                          climb_deg=p.get("cam_climb", 25.0), step_mm=dst * RL)
        car_m = K.Member("car", Dc, kind="free", r_ref=RL, t=CAR_T, width=CAR_W, joints=("J2car",))
        car_m.idx = np.clip(np.round((M_wrap_rad(caz - st[0])) / dst).astype(int), 0, len(st) - 1)
        gx, gy = np.meshgrid(np.array([-2.0, 0.0, 2.0]) / rr, np.array([1.0, 3.0, 5.0]) / RL, indexing="ij")
        Dg = on_cone(p2, ref, tt, alpha - sg * (CAR_W / 2) / RL - sg * gy.ravel()[None, :] + 0 * psi[:, None], psi[:, None] * D2R + gx.ravel()[None, :])
        guide = K.Member("guide", Dg, kind="free", r_ref=RL, t=CAR_T, width=6.0, joints=("J2car",))
        rails = [rail_m, car_m, guide]; car_w = CAR_W / 2 + 6.0
        cam = dict(tab_station=0 if s_tab == st[0] else len(st) - 1)
    elif not p.get("tele"):        # spec: ONE rigid rail over the whole travel; carriage 16 wide = 8 rail + 4 mm overhang each side
        ac = np.arange(-RAIL_W / 2, RAIL_W / 2 + 1e-6, 2.0) / RL
        pol = np.broadcast_to((alpha + ac)[None, :], (len(st), len(ac))).ravel(); az = np.repeat(st, len(ac))
        Dr = on_cone(p2, ref, tt, np.broadcast_to(pol, (P, len(pol))), np.broadcast_to(az, (P, len(az))))
        ys = np.array([-8.0, -6.0, 6.0, 8.0]) / RL; X, Y = np.meshgrid(xs, ys, indexing="ij")
        Dc = on_cone(p2, ref, tt, alpha + Y.ravel()[None, :] + 0 * psi[:, None], psi[:, None] * D2R + X.ravel()[None, :])
        rails = [K.Member("rail", np.concatenate([Dr, Dc], 1), kind="cap", r_ref=RL, t=CAR_T, width=RAIL_W, joints=("L1r", "J2car"))]
        car_w = CAR_W / 2
    else:                          # variant: 2-stage geared (2:1) telescopic rail, stages side by side (8 + 8 wide):
        # stage 1 fixed on link 1 from the anchor (tab) end over half the travel; stage 2 rides beside it, driven at half
        # the carriage travel (cable loop: determined, no free coordinate); the carriage (8 + 4 mm overhang on the hub
        # side) rides stage 2. Metal exists only from the anchor to just past the carriage.
        lo, hi = (p["psi_c"] + p["psi_lo"]) * D2R, (p["psi_c"] + p["psi_hi"]) * D2R; T = hi - lo
        e_stop = (CAR_L / 2 + END_STOP) / rr; e_tab = e_stop + TAB / rr
        g = -1.0 if s_tab == st[-1] else 1.0                  # direction from the anchor along the rail
        xcar = np.clip(g * (wrap(psi - p["psi_c"]) * D2R - (hi - p["psi_c"] * D2R if g < 0 else lo - p["psi_c"] * D2R)), 0, T)
        n1 = max(3, int(math.ceil((e_tab + T / 2 + e_stop) * rr / 2.0)) + 1); n2 = max(3, int(math.ceil((T / 2 + 2 * e_stop) * rr / 2.0)) + 1)
        s1 = s_tab + g * np.linspace(0, e_tab + T / 2 + e_stop, n1)
        s2 = s_tab + g * (e_tab - e_stop + xcar[:, None] / 2 + np.linspace(0, T / 2 + 2 * e_stop, n2)[None, :])
        ac = np.arange(-RAIL_W / 2, RAIL_W / 2 + 1e-6, 2.0) / RL; h = -sg
        o1, o2 = alpha - h * (RAIL_W / 2) / RL, alpha + h * (RAIL_W / 2) / RL
        D1 = on_cone(p2, ref, tt, np.broadcast_to(np.tile(o1 + ac, n1), (P, n1 * len(ac))), np.broadcast_to(np.repeat(s1, len(ac)), (P, n1 * len(ac))))
        D2 = on_cone(p2, ref, tt, np.broadcast_to(np.tile(o2 + ac, n2)[None], (P, n2 * len(ac))), np.repeat(s2, len(ac), axis=1))
        ys = (o2 - alpha) + h * np.array([6.0, 8.0]) / RL; X, Y = np.meshgrid(xs, ys, indexing="ij")
        Dc = on_cone(p2, ref, tt, alpha + Y.ravel()[None, :] + 0 * psi[:, None], psi[:, None] * D2R + X.ravel()[None, :])
        rails = [K.Member("rail", D1, kind="cap", r_ref=RL, t=RAIL_T, width=RAIL_W, joints=("L1r",)),
                 K.Member("stage2", np.concatenate([D2, Dc], 1), kind="cap", r_ref=RL, t=CAR_T, width=RAIL_W, joints=("J2car",))]
        car_w = RAIL_W / 2 + 4.0; alpha = o2
    x_tab = on_cone(p2, ref, tt, np.full(P, (p["a2"] + p["d_off"]) * D2R + (sg * RAIL_W / 2 / RL if p.get("tele") else 0)), np.full(P, s_tab))
    car_c = on_cone(p2, ref, tt, np.full(P, alpha), psi * D2R)
    b_from = on_cone(p2, ref, tt, np.full(P, alpha - sg * car_w / RL), psi * D2R)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub3", p3, "J3")]
    strap1 = K.strap_member("strap1", p1, x_tab, ("J1", "L1r"), ramp_to=(("hub1", K.STACK), (None if cam else "rail", 0.0)))
    bridge = K.strap_member("bridge", b_from, p3, ("J3", "J2car"), ramp_to=((None, 0.0), ("hub3", K.STACK)),
                            over=[("neck", 1.0)])
    ns, nc = bridge.grid
    if not cam: bridge.ramps.append((np.repeat(np.arange(ns), nc) < 1, rails[-1].name, -K.STACK))   # on the carriage side face
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    res = K.closure_residual(p1, p3, p2, p["a1"], p["a2"])
    info = dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                rail_span_deg=round(float((st[-1] - st[0]) / D2R), 1), rail_len_mm_at_ref=round(float((st[-1] - st[0]) * rr), 1),
                same_body=([["bridge", "guide"], ["car", "guide"], ["rail", "car"]] if cam else
                           [["bridge", rails[-1].name]] + ([["rail", "stage2"]] if p.get("tele") else [])), cam=cam)
    for m in rails: m.q = p.get("q_rail")                     # per-member underside quantiles (None = the global q)
    hubs[1].q = p.get("q_hub3"); bridge.q = p.get("q_bridge")
    return K.Chain(members=hubs + [strap1] + rails + [bridge, neck], ok=ok, q=q, info=info,
                   joints=dict(J1=p1, J2=p2, J3=p3, L1r=x_tab, J2car=car_c), hubless=("J2", "L1r", "J2car"))


# ---- K6 with same-body pairs: the kit's own pair test, skipping pairs listed in Chain.info['same_body'] -------------
_KIT_COLL = K.collisions


def collisions_same_body(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    skip = {frozenset(x) for x in chain.info.get("same_body", [])}
    if not skip: return _KIT_COLL(chain, pts, ok, clear, overlap, chunk)
    hit = np.zeros(len(ok), bool); M = chain.members
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            if frozenset((M[a].name, M[b].name)) in skip: continue
            hit |= _KIT_COLL(K.Chain(members=[M[a], M[b]], ok=chain.ok, joints=chain.joints), pts, ok, clear, overlap, chunk)
    return hit


K.collisions = collisions_same_body


def M_wrap_rad(x): return (np.asarray(x) + math.pi) % (2 * math.pi) - math.pi


# ---- cam variant: the rail profile is per station (max across the section); the carriage sits on it per pose ----------
_KIT_FIT, _KIT_PTS = K.fit_profiles, K.member_points


def fit_profiles_cam(B, chain, fit, q=1.0, mode="march"):
    prof = _KIT_FIT(B, chain, fit, q, mode); cam = chain.info.get("cam")
    if not cam: return prof
    M = {m.name: m for m in chain.members}; ns, nc = M["rail"].grid; Pi = np.nonzero(fit)[0]
    row = prof["rail"].reshape(ns, nc).max(1); prof["rail"] = np.repeat(row, nc)          # rigid section
    car = M["car"]; car._rpp = row[car.idx]                                               # (P, m): on the track
    cr = car._rpp[Pi] if len(Pi) else row[None]
    prof["car"] = cr[0]
    prof["guide"] = np.full(len(prof["guide"]), float(cr.min())); M["guide"].t = float(cr.max() - cr.min() + CAR_T)
    s1 = M["strap1"]; n1, c1 = s1.grid; r = prof["strap1"].reshape(n1, c1).copy(); ne = int(math.ceil((K.HUB_R + 2) / 2)) + 1
    r[-ne:] = np.maximum(r[-ne:], row[cam["tab_station"]]); x = np.arange(n1) * s1.step_mm; sl = math.tan(60 * D2R)
    prof["strap1"] = (r[None] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1).ravel()   # butt onto the tab, K5 again
    return prof


def member_points_cam(m, rho):
    if getattr(m, "_rpp", None) is not None: return K.unit(m.D) * m._rpp[..., None]
    return _KIT_PTS(m, rho)


K.fit_profiles = fit_profiles_cam; K.member_points = member_points_cam


def full(B, p):
    p = dict(PARAMS, **p); F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    p.update(travel(B, F, p)); return p


def evaluate(B, p, **kw):
    p = full(B, p); r = K.evaluate(B, build, p, **kw); return p, r


def metal(pose, frames, params):
    """task API: metal points (k, 3) of bench pose index `pose` after an evaluate() on the same bench (frames = B)"""
    L = frames._kit_last
    if not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


def configs(stage):
    seeds = dict(C=SEED_C, A=SEED_A, B=SEED_B)
    if stage == "rigid":           # the spec: one rigid rail over the whole travel (slow: far rail stations run into the body)
        return [dict(PARAMS, **seeds[s], d_off=d, q=0.93, tele=0) for s, d in (("C", -25.0), ("C", 20.0))]
    if stage == "coarse":          # the 2-stage telescopic rail (the variant that removes the measured limiter)
        return [dict(PARAMS, **seeds[s], d_off=d, q=q, cov=c, tele=1)
                for s, d, q, c in itertools.product("CAB", (-35.0, -25.0, -15.0, 20.0), (0.9, 0.95, 1.0), (0.9, 1.0))]
    if stage == "tele2":           # telescopic rail, per-member quantile on the rail stages only
        return [dict(PARAMS, **seeds[s], d_off=d, q=1.0, q_rail=qr, cov=1.0, tele=1)
                for s, d, qr in itertools.product("CAB", (-45.0, -35.0, -25.0), (0.95, 0.98, 1.0))]
    if stage == "cam":             # cam-track rail (rigid section), per-station radius, rail quantile below 1
        return [dict(PARAMS, **SEED_C, d_off=d, q=1.0, q_rail=qr, cam=1, cam_climb=45.0) for d, qr in ((-35.0, 0.95),)]
    if stage.startswith("refine:"):  # refine:<json of a base config>
        b = json.loads(stage[7:]); out = []
        for k, dv in (("q_hub3", (-0.03,)), ("d_off", (-5, 5)), ("wd", (-8, 8)), ("a2", (-6, 6))):
            for d in dv:
                c = dict(b); c[k] = round((c.get(k) if c.get(k) is not None else 1.0) + d, 4)
                if k.startswith("q") and not 0.8 <= c[k] <= 1.0: continue
                if k == "cov" and not 0.8 <= c[k] <= 1.0: continue
                out.append(c)
        return out
    raise ValueError(stage)


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160) if "--small" not in a else K.bench(20, 40)
    if a[0] == "check":
        ov = {k: (float(v) if k != "sigma" else int(v)) for k, v in (x.split("=") for x in a[1:] if "=" in x)}
        p, r = evaluate(B, dict(PARAMS, **ov), verbose=False)
        print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                 "inband_member", "mass_g", "honest", "audit", "rail_span_deg", "rail_len_mm_at_ref", "residual_deg")})
        L = B._kit_last; print({m: round(float(np.linalg.norm(v[L["take"]], axis=-1).min()), 1) if L["take"].any() else None for m, v in L["pts"].items()})
    elif a[0] == "sweep":
        out = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
        rows = json.load(open(out)) if os.path.exists(out) else []
        stage = a[1]
        if stage == "refine":      # around the best entry so far (its design params, travel recomputed)
            b = min(rows, key=lambda e: e["gap"])["params"]; stage = "refine:" + json.dumps({k: v for k, v in b.items() if not k.startswith("psi_")})
        for c in configs(stage):
            p, r = evaluate(B, c)
            e = dict(k=len(rows), t=K.now(), params={k: v for k, v in p.items()}, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                     closure=r["closure"], collide=r["collide"], flips=r["flips"], mass_g=r["mass_g"], honest=r["honest"],
                     kmode=r["kmode"], inband_member=r["inband_member"], stage=a[1])
            rows.append(e); json.dump(rows, open(out + ".tmp", "w"), indent=1); os.replace(out + ".tmp", out)
            print(f"[{e['k']}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ct {e['contact']} "
                  f"coll {e['collide']} {r['inband_member']} | {c['az']:.0f} {c['wd']:.0f} d_off {c['d_off']} q {c['q']} qr {c.get('q_rail')} cov {c['cov']}", flush=True)
            best = min(rows, key=lambda x: x["gap"])
            if e["gap"] <= best["gap"] and e["k"] == best["k"] and len(rows) > 1 and e["gap"] < min(x["gap"] for x in rows[:-1]):
                K.log_event(f"rail-elbow new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, inband14 {e['inband14']}, "
                            f"contact {e['contact']}) at sweep k{e['k']}, {'telescopic' if c.get('tele') else 'cam' if c.get('cam') else 'rigid'} rail")
