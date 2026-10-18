"""kfree-armarc-relay-4r (round 104, lens A 'guide-price-close', pick 2): a PLAIN O20 spherical 3R at the verified lead's
seats (no knuckle K, no drive, link 1 one bent bar) whose arm-side member rides a ONE-SIDED circular ARM-ARC RELAY: the
cuff pad sits on a carriage that runs on a circular track of one radius about an arm-fixed axis r through GH (tilt from
the humeral long axis swept). The relay is a COUNTED 4th revolute (4 joints, cap 4), spring-preloaded onto a zero dowel
(phi = theta0) with an end dowel at theta0 + PHI.

PHYSICS (least-phi solve, the judge's amendment 1.2): the preload holds phi at its zero dowel while the plain dyad closes
in its window [|a1 - a2| + m, a1 + a2 - m] (m = K.FOLD_MARGIN, J2 own-angle dowel stops). When the arm leaves the window
(EITHER wall: stretched across the body / overhead, folded behind the back), the arm turns the carriage to the LEAST
phi in [0, PHI] (one-sided, sgn) at which the dyad closes; the chain then sits on that J2 stop with the spring pressing
it there (determinate). The relay does not choose its wall: a pose whose least-phi state ends in a part-part collision
is a JAM (metal on metal between non-adjacent bodies), counted lost and listed separately (info['jams']).

Geometry: J1 = bvec(az1, el1) (scapula), J3 = HG R(r, theta0 + phi) wdir(d3, a3) (the carriage frame), J2 by the
two-circle closure. Members (concept_kit K3-K7): hub1 / hub2 / hub3 (O20 flat discs), link1 (ONE 12 x 3 Ti strap J1 ->
J2; `hubK` = 1 keeps the kit's hub K + link 1a / 1b as metal for the proposer's reproduction), link2 (J2 -> J3, over
link 1 and the neck), neck (14 x 6 strap J3 -> the pad at BAR0_H + s_cuff Db, carriage frame, over the track by the
carriage height), carriage (a cap-kind plate +-blk/2 deg along the track, 12 wide, t carr_h, over the track), track
(ARM-FIXED, cap kind = one radius about GH, fitted at the per-sample quantile q_track over the fit poses - an
arm-fixed arc meets the torso in some poses, which the bench then counts as contact: a circle about a GH-through axis lies on a sphere about GH, arc theta0 -
blk/2 - 3 .. theta0 + PHI + blk/2 + 3 deg, 8 wide x track_t). The track is on the contact list and in ib14 with the
torso (dist_many over the whole skin).

K2: the relay angle enters q as 2.5 phi so a phi jump > 10 deg between 2-deg slerp steps (the continuity rule for
passive / redundant joints) trips the kit's 25-deg jump test; the carriage axis C is also a Chain joint (hubless).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/kfree-armarc-relay-4r.py fit '<json>'
    ... repro                              (the proposer's nok_metal +30 / +45 / +60 counts, kit CONTROL metal)
    ... frozen|held '<json>' [out.json]    (fit Bench(60,160) fast, frozen, worn Bench(110,360) / held out EXACT)
    hooks: evaluate(B, params) (tools/concept_cma.py), bench_eval(B, params)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
import concept_bench as CB                                   # noqa: E402
_sp = importlib.util.spec_from_file_location("kit_paired_kfree", os.path.join(REPO, "docs", "research", "fold_ceiling", "kit_paired.py"))
KP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KP)

ID = "kfree-armarc-relay-4r"
NAME = "Plain O20 3R at the lead's seats + one-sided arm-arc relay (counted 4th R), no knuckle or drive"
PARAMS = dict(KP.CONTROL); PARAMS.update(a1max=KP.CONTROL["a1"], PHI=60.0, sgn=1.0, tilt=0.0, taz=0.0, theta0=0.0,
                                         s_cuff=0.0, rt_off=0.0, blk=22.0, track_w=8.0, track_t=3.0, carr_h=4.0, hubK=0, phistep=1.0, q_track=0.9)


def rot(axis, deg):
    k = K.unit(np.asarray(axis, float)); a = math.radians(deg); X = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * X + (1 - math.cos(a)) * X @ X


def relay_axis(p):
    """arm-fixed relay axis in the HG frame: the humeral long axis (+y, up the arm, = the proposer's ry) tilted by `tilt`
    toward azimuth taz (wdir convention: 0 lateral, +90 anterior)"""
    return -K.wdir(float(p["tilt"]), float(p["taz"]) + 180.0) if p["tilt"] else np.array([0.0, 1.0, 0.0])


def window(p):
    m = float(p["margin"]); a1, a2 = float(p["a1"]), float(p["a2"])
    return abs(a1 - a2) + m, min(a1 + a2, 360 - a1 - a2) - m


def relay_phi(F, p, only=None):
    """least relay angle (one-sided, sgn) that brings angle(J1, J3) into the plain window; nan where none <= PHI.
    only: optional (P,) mask of poses allowed to relay (the reproduction relays only out-of-window poses: identical)"""
    r = relay_axis(p); u1 = K.bvec(p["az1"], p["el1"]); u3 = K.wdir(p["d3"], p["a3"]); lo, hi = window(p)
    p1 = F.S(u1); n = len(p1); phi = np.full(n, np.nan); th = np.full(n, np.nan)
    st = float(p.get("phistep", 1.0)); fs = np.arange(0.0, float(p["PHI"]) + 1e-6, st)
    for f in fs:
        v = F.RHG @ (rot(r, float(p["theta0"]) + float(p["sgn"]) * f) @ u3)
        t = np.degrees(np.arccos(np.clip((p1 * v).sum(-1), -1, 1)))
        new = np.isnan(phi) & (t >= lo) & (t <= hi)
        if only is not None: new &= only | (f == 0)
        phi[new] = f; th[new] = t[new]
    return phi, th


def relay_frames(F, p, phi):
    r = relay_axis(p); f0 = float(p["theta0"]); s = float(p["sgn"])
    R = np.stack([rot(r, f0 + s * (0.0 if np.isnan(f) else f)) for f in phi])
    C = np.einsum("pji,pjk->pik", F.RHG, F.RH)              # RHG^T RH per pose (constant ~12 deg)
    RHG2 = F.RHG @ R
    return K.Frames(RS=F.RS, RHG=RHG2, RH=RHG2 @ C, clip=F.clip, ws=F.ws), R


def pad_dir_HG(F, p):
    """pad centre (start of BOTTOM's bar, moved s_cuff mm down Db) in the HG frame, per pose (P, 3)"""
    C = np.einsum("pji,pjk->pik", F.RHG, F.RH)
    return K.unit(C @ K.unit(K.BAR0_H + float(p["s_cuff"]) * K.DB))


def arc_dirs(c, r, f_lo, f_hi, width, r_ref=70.0, step=2.0):
    """directions of a band of width `width` (mm at r_ref) along the circle about axis r through c (P, 3) (HG frame),
    from angle f_lo to f_hi (deg) about r: (P, m, 3)"""
    sg = np.sqrt(np.clip(1 - (c @ r) ** 2, 1e-6, 1)); df = math.degrees(step / r_ref / float(np.median(sg)))
    fs = np.linspace(f_lo, f_hi, max(3, int(math.ceil((f_hi - f_lo) / df)) + 1)); ws = np.arange(-width / 2, width / 2 + 1e-6, step) / r_ref
    out = []
    for f in fs:
        cf = c @ rot(r, f).T; mf = K.unit(r[None, :] - (cf @ r)[:, None] * cf)
        for w in ws: out.append(K.unit(np.cos(w) * cf + np.sin(w) * mf))
    return np.stack(out, 1)


def build(B, F, p):
    p = dict(PARAMS, **p); a1, a2 = float(p["a1"]), float(p["a2"]); w, t = float(p["width"]), float(p["t_link"])
    phi, _ = relay_phi(F, p); F2, R = relay_frames(F, p, phi)
    r = relay_axis(p); c = pad_dir_HG(F, p); f0 = float(p["theta0"]); s = float(p["sgn"]); PHI = float(p["PHI"]); hb = float(p["blk"]) / 2
    lo_f, hi_f = (f0 - hb - 3.0, f0 + PHI + hb + 3.0) if s > 0 else (f0 - PHI - hb - 3.0, f0 + hb + 3.0)
    track_HG = arc_dirs(c, r, lo_f, hi_f, float(p["track_w"]))
    track = K.Member("track", np.einsum("pij,pmj->pmi", F.RHG, track_HG), kind="cap", t=float(p["track_t"]), width=float(p["track_w"]),
                     off=float(p["rt_off"]), cell=4.0, q=float(p["q_track"]))
    cc = np.einsum("pij,pj->pi", R, c)                                           # carriage centre (HG), turned by theta0 + phi
    car_HG = arc_dirs(cc, r, -hb, hb, 12.0)
    carriage = K.Member("carriage", np.einsum("pij,pmj->pmi", F.RHG, car_HG), kind="cap", t=float(p["carr_h"]), width=12.0,
                        joints=("C",), over=[("track", 0.5)], cell=4.0)
    Cax = np.einsum("pij,pj->pi", F.RHG, cc)
    p1 = F2.S(K.bvec(p["az1"], p["el1"])); p3 = F2.HG(K.wdir(p["d3"], p["a3"]))
    neck = K.strap_member("neck", p3, F2.H(K.unit(K.BAR0_H + float(p["s_cuff"]) * K.DB)), ("J3", "C"), width=14.0, t=6.0,
                          ramp_to=(("hub3", 0.0), (None, 0)), over=[("track", float(p["carr_h"]))])
    ok_r = ~np.isnan(phi)
    if int(p["hubK"]):
        ch = KP.build(B, F2, dict(p, a1max=a1, bk1=float(p.get("bk1", 26.0))))
        mem = {m.name: m for m in ch.members}; mem["link2"].over = [("link1a", 1.0), ("neck", 1.0), ("track", 1.0)]
        members = [mem["hub1"], mem["hubK"], mem["hub2"], mem["hub3"], mem["link1a"], mem["link1b"], track, carriage, neck, mem["link2"]]
        ok = np.asarray(ch.ok, bool) & ok_r; q = np.c_[ch.q, 2.5 * np.nan_to_num(phi)]; joints = dict(ch.joints, C=Cax)
    else:
        p2, ok, margin = K.closure(p1, p3, a1, a2, float(p["sigma"]), margin_deg=float(p["margin"])); ok &= ok_r
        q = np.stack([K.axis_angle(p1, F2.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3), K.axis_angle(p3, F2.HG([0.0, -1, 0]), p2),
                      2.5 * np.nan_to_num(phi)], -1)
        members = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3"),
                   K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
                   track, carriage, neck,
                   K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                                  over=[("link1", 1.0), ("neck", 1.0), ("track", 1.0)])]
        joints = dict(J1=p1, J2=p2, J3=p3, C=Cax)
    rel = ok & (np.nan_to_num(phi) > 0)
    return K.Chain(members=members, ok=ok, q=q, joints=joints, hubless=("C",),
                   info=dict(relayed=int(rel.sum()), phi_max=round(float(np.nanmax(np.where(ok, phi, np.nan))), 1) if ok.any() else None,
                             _phi=phi))


def evaluate(B, params, near=1.0):
    """the kit evaluation + relay counts (jams = relayed poses ending in part collisions) + the 1 mm near-touch gap"""
    p = dict(PARAMS, **params); r = K.evaluate(B, build, p); L = B._kit_last; ch = L["chain"]; phi = ch.info.pop("_phi")
    r.pop("_phi", None)
    rel = L["ok"] & (np.nan_to_num(phi) > 0); kind = np.array(B.kind); ws = kind == "ws"
    take = L["take"]; Pi = np.nonzero(take)[0]
    mins = {int(i): float(np.min(B.res[i])) for i in Pi if B.res[i] is not None}
    bad = {i for i, v in mins.items() if v < near}
    okn = np.array([B.res[j] is not None and j not in bad for j in range(len(kind))])
    gnear = CB.gap_of(r["inband14"], okn[~ws].mean(), okn[ws].mean(), 0.0)
    r.update(relayed=int(rel.sum()), relayed_ws=int((rel & ws).sum()), jams=int((rel & L["hit"]).sum()),
             jams_ws=int((rel & L["hit"] & ws).sum()), relayed_contact=int(sum(1 for i in Pi if rel[i] and mins.get(int(i), 1) < 0)),
             relayed_taken=int(sum(1 for i in Pi if rel[i] and mins.get(int(i), -1) >= 0)), gap_near1=round(gnear, 3),
             phi_max_taken=round(float(max([phi[i] for i in Pi if mins.get(int(i), -1) >= 0] + [0.0])), 1),
             min_metal_mm=round(min(mins.values()), 3) if mins else None)
    return p, r


def bench_eval(B, params): return evaluate(B, params)[1]


def wear(params, which="bench"):
    """frozen protocol (as kit_paired.wear): fit Bench(60,160) fast, undersides frozen, worn EXACT"""
    p = dict(PARAMS, **params); B1 = K.bench(60, 160); _, r1 = evaluate(B1, p); prof = B1._kit_last["prof"]
    if which == "held": B = KP.held_bench()
    else:
        os.environ["CB_EXACT"] = "1"; B = CB.Bench(110, 360)
    F = K.frames(B); ch = build(B, F, p); phi = ch.info.pop("_phi"); ok = np.asarray(ch.ok, bool)
    ok, flips = K.continuity_dense(B, F, build, p, ok)
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = K.collisions(ch, pts, ok); take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    nm = np.concatenate([[m.name] * pts[m.name].shape[1] for m in ch.members])
    d = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = d[j]
    rep = B.report(); mins = {int(i): float(d[j].min()) for j, i in enumerate(Pi)}; part = {int(i): str(nm[int(np.argmin(d[j]))]) for j, i in enumerate(Pi)}
    kind = np.array(B.kind); ws = kind == "ws"; elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))])
    nearg = {}
    for nmm in (1.0, 2.0):
        bad = {i for i, v in mins.items() if v < nmm}
        okn = np.array([B.res[j] is not None and j not in bad for j in range(len(kind))])
        nearg[f"gap_near{nmm:g}"] = round(CB.gap_of(rep["inband14"], okn[~ws].mean(), okn[ws].mean(), 0.0), 3)
    rel = np.asarray(ch.ok, bool) & (np.nan_to_num(phi) > 0)
    why = dict(fold=int((ws & ~np.asarray(ch.ok, bool)).sum()), flip=int(flips), parts=int((ws & ok & hit).sum()),
               jams_ws=int((ws & ok & hit & rel).sum()), contact=int(sum(1 for i, v in mins.items() if v < 0 and ws[i])),
               relayed_ws=int((ws & rel).sum()), relayed_taken_ws=int(sum(1 for i, v in mins.items() if v >= 0 and ws[i] and rel[i])))
    ov = ws & (elev >= 140)
    pp = [dict(i=int(i), kind=str(kind[i]), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
               phi=None if np.isnan(phi[i]) else float(phi[i]), closes=bool(ch.ok[i]), followed=bool(ok[i]), jam=bool(ok[i] and hit[i]),
               taken=bool(i in mins and mins[i] >= 0), min_mm=round(mins[i], 3) if i in mins else None, part=part.get(int(i)))
          for i in range(len(B.idx))]
    return dict(fit_fast={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "contact", "gap_near1", "relayed", "jams")},
                honest_fit=r1["honest"], audit=r1["audit"], frozen={k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                why=why, **nearg, min_metal_mm=round(min(mins.values()), 3) if mins else None,
                overhead=f"{int(sum(1 for i in np.nonzero(ov)[0] if pp[i]['taken']))}/{int(ov.sum())}",
                inband_member=r1["inband_member"], mass_g=r1["mass_g"], which=which, mode=B.mode, poses=pp)


def repro():
    """the proposer's nok_metal: kit CONTROL (a1max = a1, hub K kept), profiles fitted WITHOUT the relay on Bench(60,160),
    worn exact on Bench(110,360); out-of-window ws poses relayed at the least phi; counts kin / collide / contact / clean"""
    P = dict(KP.CONTROL, a1max=KP.CONTROL["a1"]); B1 = K.bench(60, 160); K.evaluate(B1, KP.build, P); prof = B1._kit_last["prof"]
    os.environ["CB_EXACT"] = "1"; B = CB.Bench(110, 360); F = K.frames(B); ws = np.array(B.kind) == "ws"; out = {}
    for PHI in (30, 45, 60):
        p = dict(PARAMS, **P, PHI=PHI, hubK=1); phi, _ = relay_phi(F, p); rel = ws & (np.nan_to_num(phi) > 0)
        F2, _ = relay_frames(F, p, phi); ch = KP.build(B, F2, P); ok = np.asarray(ch.ok, bool)
        pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}; hit = K.collisions(ch, pts, ok)
        Pi = np.nonzero(rel & ok)[0]; allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
        d = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1]).min(1)
        col = hit[Pi]; out[PHI] = dict(relayed=int(len(Pi)), collide=int(col.sum()), contact=int((d < 0).sum()),
                                      clean=int(((~col) & (d >= 0)).sum()), in_window_ws=int((ws & ~np.isnan(phi)).sum()))
        print("repro +%d" % PHI, out[PHI], flush=True)
    return out



# =====================================================================================================================
# LEAD-BASED MODEL (the scored one). The kit model above (build / evaluate / wear) reproduces the proposer's nok_metal
# counts exactly (repro), but its q 1.0 metal parks hub 2 at 171 mm from GH even with no relay (kit CONTROL fast 74.45 /
# 102.98 with K welded vs the lead's own model 12.50): its in-band is meaningless, so the score comes from the LEAD'S OWN
# MODEL (conecut-knee-knuckle-3r: O20 stacks, pin knee, J3 dowel stop, fitted metal) through the relay wrapper of
# armarc-relay-knuckle-4r (relay solve, arc track + shell + carriage metal, arm-side lift onto the carriage, jams), with:
#   * K WELDED at stop A: the relay solve's gate adds |dK| <= KWELD (0.1 deg), so a pose past the plain wall
#     th > a1 + a2 - 5 is relayed (least phi) or LOST - the lead's own K law never opens (no K, no drive);
#   * poses with no welded solution in [0, PHI] are marked lost ('kfold') after the run (the wrapper would otherwise
#     wear them at phi = 0 with the lead's K open);
#   * drive metal deleted (drive = 0): the bell crank and nose (member 9) and link 1a's horn leave the rigid, contact and
#     part lists (hub K + link 1a / 1b at stop A stay as metal: the spec's first pass, as the kit did); drive = 1 keeps
#     them parked at dK = 0 (an upper bound on metal);
#   * frozen shape: the lead's parts as fitted on Bench(60,160) fast at phi = 0 (its own protocol), worn with the relay.
# =====================================================================================================================
KWELD = 0.1
DRIVE_NAMES = ("crank", "roller", "horn")
_AR = None


def _ar():
    global _AR
    if _AR is None:
        os.environ.setdefault("SN_CELL", "lead")
        sp = importlib.util.spec_from_file_location("armarc_for_kfree", os.path.join(HERE, "armarc-relay-knuckle-4r.py"))
        _AR = importlib.util.module_from_spec(sp); sp.loader.exec_module(_AR)
        g0 = _AR.gate

        def gate_weld(M, Q):                                       # the lead's gates + K welded at stop A
            ok = g0(M, Q); dk = np.degrees(np.abs(np.asarray(M.D._dK, float)))
            return ok & (dk <= KWELD)
        _AR.gate = gate_weld; _AR._gate_lead = g0
    return _AR


LPAR = dict(PHI=60.0, tilt=0.0, taz=0.0, sgn=1.0, hw=1, hwv="plain", ds=0.0, drive=0)


def _strip_drive(M):
    """delete the drive metal (crank + nose on member 9, link 1a's horn) from the rigid / contact lists"""
    horn = M.rigid.get("horn")
    for nm in DRIVE_NAMES: M.rigid.pop(nm, None)
    keep = []
    for m, Pc in M.contact:
        if m == 9: continue
        if horn is not None and m == horn[0] and len(Pc) and len(horn[1]):
            dd = np.linalg.norm(np.asarray(Pc)[:, None, :] - np.asarray(horn[1])[None, :, :], axis=-1).min(1)
            if np.median(dd) < 0.5: continue
        keep.append((m, Pc))
    M.contact = keep


def lead_eval(params, nc=60, nw=160, exact=False):
    AR = _ar(); CBm = AR.CB; t0 = time.time()
    rp = dict(LPAR); rp.update({k: params[k] for k in LPAR if k in params})
    # K welded: the lead's linear K law opens from th = a1 + a2 - smhi (16.84 deg before the plain wall); welded, the dyad
    # closes up to a1 + a2 - 5, so the law onset moves to smhi = 5 (K at stop A wherever the welded dyad closes) and the
    # gate |dK| <= KWELD then IS the welded chain's window
    xp = {k: v for k, v in params.items() if k not in LPAR and k != "psi2"}
    if float(params.get("psi2", 0.0)):                         # window re-placement (shift_a2.py): J2's rest axis turned about J1 by psi2
        L0 = dict(AR.CC.PARAMS, **AR.LEAD); u1 = K.bvec(L0["az1"], L0["el1"]); u2 = K.bvec(L0["az2"], L0["el2"]); ps = math.radians(float(params["psi2"]))
        v = K.unit(math.cos(ps) * u2 + math.sin(ps) * np.cross(u1, u2) + (1 - math.cos(ps)) * (u1 @ u2) * u1)
        xp.update(az2=math.degrees(math.atan2(v[2], -v[0])), el2=math.degrees(math.asin(float(np.clip(v[1], -1, 1)))))
    P = AR.CC._clamp(dict(AR.CC.PARAMS, **AR.LEAD, **dict(dict(smhi=5.0), **xp)))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CBm.Bench(n_clip=60, n_ws=160); M1 = AR.CC.CCModel(B1, dict(P)); r1 = M1.run()
        assert abs(float(M1.p.get("smhi", 5.0)) - float(P["smhi"])) < 1e-6, ("smhi clamped", M1.p.get("smhi"))
        ax = AR.raxis(rp["tilt"], rp["taz"])
        G = AR.relay_geometry(M1, B1, ax, rp) if int(rp["hw"]) and float(rp["PHI"]) > 0 else None
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    phi, ax = AR.solve_phi(M1, rp); phi_fill = np.where(np.isfinite(phi), phi, 0.0); Zr = AR.relayed_Z(phi_fill, ax)
    drive = int(rp["drive"])

    class Frozen(AR.CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.rigid = dict(M1.rigid); self._sc = None
            self.contact = list(M1.contact)
            if not drive: _strip_drive(self)
            self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    if exact: os.environ["CB_EXACT"] = "1"
    B = CBm.Bench(n_clip=nc, n_ws=nw); phi_b = phi[B.idx]
    with AR.patched(Zr):
        M = Frozen(B, P2); M.run()
    hwrep = AR.rerecord(M, B, G, ax, np.nan_to_num(phi_b), AR.Z0["HG"][B.idx].astype(float)) if G is not None else {}
    why = np.asarray(M.why, dtype=object).copy(); nok = ~np.isfinite(phi_b)
    for i in np.nonzero(nok)[0]:                                  # no welded solution in [0, PHI]: lost (the K is welded)
        B.res[i] = None
        if why[i] in ("", "contact", "skin"): why[i] = "kfold"
    M.why = why
    rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    kind = np.array(B.kind); ws = kind == "ws"; elev = np.array([p["elev"] for p in B.poses])
    taken = np.isfinite(mins) & (mins >= 0); rel = np.isfinite(phi_b) & (np.abs(phi_b) > 0)
    ok1 = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 1.0
    cl = np.nonzero(~ws)[0]; wl = np.nonzero(ws)[0]; nz = [j for j in range(len(kind)) if B.res[j] is not None]
    near1 = CBm.gap_of(rep["inband14"], float(np.mean([ok1(j) for j in cl])), float(np.mean([ok1(j) for j in wl])),
                       float(np.mean([float(np.min(B.res[j])) < 1.0 for j in nz])) if nz else 0.0)
    jam = (why == "parts") | (why == "jam")
    out = dict(wear=rep, near1_gap=round(float(near1), 3), smhi=float(M1.p.get("smhi")), a1a2=[round(float(M1.D.a1), 3), round(float(M1.D.a2), 3)], fit_lead_phi0={k: r1[k] for k in ("gap", "reach", "inband14", "contact")},
               bench=[nc, nw], mode=B.mode, relay=dict(rp, axis=[round(float(x), 4) for x in ax]),
               why={str(k): int((why == k).sum()) for k in set(why.tolist())}, why_ws={str(k): int(((why == k) & ws).sum()) for k in set(why.tolist())},
               ws_taken=int((ws & taken).sum()), ws=int(ws.sum()), overhead=[int((ws & taken & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())],
               relayed=dict(n_ws=int((rel & ws).sum()), taken_ws=int((rel & ws & taken).sum()), contact=int((rel & np.isfinite(mins) & (mins < 0)).sum()),
                            jam=int((rel & jam).sum()), jam_ws=int((rel & jam & ws).sum()), clip=int((rel & ~ws).sum()), clip_taken=int((rel & ~ws & taken).sum()),
                            phi_max=round(float(np.nanmax(np.abs(phi_b))), 2) if np.isfinite(phi_b).any() else 0.0,
                            phi_max_taken=round(float(np.max(np.abs(phi_b[taken]))), 2) if taken.any() else 0.0),
               min_metal_taken=round(float(np.nanmin(np.where(taken, mins, np.nan))), 3) if taken.any() else None,
               hw={k: v for k, v in hwrep.items() if k != "jams"}, n_hw_jams=len(hwrep.get("jams", [])), secs=round(time.time() - t0, 1))
    if G is not None:
        out["relay_hw"] = dict(R_t=round(G["R_t"], 1), h_c=G["h_c"], dh_lift=round(G["dh"], 2), rpad=round(G["rpad"], 1), th0=round(G["th0"], 1),
                               arc=[round(G["lo"], 1), round(G["hi"], 1)], arc_len_deg=round(G["hi"] - G["lo"], 1),
                               arc_len_mm=round((G["hi"] - G["lo"]) * math.pi / 180 * G["R_t"], 1))
        out["viz_RL"] = dict(ax=[round(float(x), 4) for x in ax], e=[round(float(x), 4) for x in G["e"]], f=[round(float(x), 4) for x in G["f"]],
                             s0=round(G["s0"], 2), Rt=round(G["R_t"], 1), lo=round(G["lo"], 2), hi=round(G["hi"], 2), th0=round(G["th0"], 2),
                             hc=G["h_c"], dh=round(G["dh"], 1), PHI=float(rp["PHI"]), sgn=float(rp["sgn"]), rpad=round(G["rpad"], 1))
    out["poses"] = [dict(i=int(j), kind=str(kind[j]), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")],
                         phi=(round(float(phi_b[j]), 1) if np.isfinite(phi_b[j]) else None), why=str(why[j]),
                         min_mm=(round(float(mins[j]), 2) if np.isfinite(mins[j]) else None)) for j in range(len(kind)) if kind[j] == "ws"]
    names = list(AR.Z0["NAMES"]); steps = []
    for nm in CBm.FIT:
        ii = np.nonzero(AR.Z0["CID"] == names.index(nm))[0]; ii = ii[np.argsort(AR.Z0["FI"][ii], kind="stable")]
        p_ = phi[ii]; good = np.isfinite(p_[1:]) & np.isfinite(p_[:-1])
        if good.any(): steps.append(float(np.abs(np.diff(p_))[good].max()))
    out["phi_clip_step_max"] = round(max(steps), 2) if steps else 0.0
    return out, M, B


def lead_bench_eval(B, params):
    out, _, _ = lead_eval(params); r = dict(out["wear"]); r["gap_near1"] = out["near1_gap"]; return r


def append_sweep(params, out, path=None):
    path = path or os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
    try: S_ = json.load(open(path))
    except Exception: S_ = []
    w = out["wear"]
    S_.append(dict(k=len(S_), t=K.now(), params=params, inband14=w["inband14"], inband10=w["inband10"], reach=w["reach"], follow=w["follow"],
                   contact=w["contact"], gap=w["gap"], gap_near1=out["near1_gap"], bench=out["bench"], mode=out["mode"],
                   relayed=out["relayed"], why_ws=out["why_ws"], overhead=out["overhead"], min_metal_taken=out["min_metal_taken"]))
    json.dump(S_, open(path, "w"), indent=0, default=float)


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "lead"
    if mode == "repro":
        print(json.dumps(repro())); sys.exit()
    if mode in ("lead", "lfrozen", "lsweep"):
        if mode == "lsweep":                                     # lsweep '<json list of param dicts>' : fast, appended to the sweep file
            for c in json.loads(a[1]):
                out, _, _ = lead_eval(c); append_sweep(c, out, a[2] if len(a) > 2 else None)
                print(json.dumps(dict(params=c, **out["wear"], near1=out["near1_gap"], rel=out["relayed"], why=out["why_ws"], ov=out["overhead"],
                                      hw=out.get("relay_hw"), secs=out["secs"]), default=float), flush=True)
            sys.exit()
        par = json.loads(a[1]) if len(a) > 1 else {}
        out, M, B = lead_eval(par, *((110, 360, True) if mode == "lfrozen" else (60, 160, False)))
        out["params"] = par; out["row"] = ID
        if len(a) > 2: json.dump(out, open(a[2], "w"), indent=0, default=float)
        print(json.dumps({k: v for k, v in out.items() if k != "poses"}, default=float)); sys.exit()
    a = sys.argv[1:]; mode = a[0] if a else "fit"
    if mode == "repro":
        print(json.dumps(repro())); sys.exit()
    par = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else {}))
    if mode == "fit":
        t = time.time(); _, r = evaluate(K.bench(60, 160), par)
        print(json.dumps({k: r[k] for k in ("gap", "gap_near1", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                           "inband_member", "mass_g", "flips", "collide", "relayed", "relayed_ws", "jams", "jams_ws",
                                           "relayed_taken", "relayed_contact", "phi_max_taken", "min_metal_mm")}, default=float), round(time.time() - t, 1))
    elif mode in ("frozen", "held"):
        t = time.time(); out = wear(par, "held" if mode == "held" else "bench"); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(a) > 2: json.dump(out, open(a[2], "w"), indent=0, default=float)
        print(json.dumps({k: v for k, v in out.items() if k != "poses"}, default=float))
