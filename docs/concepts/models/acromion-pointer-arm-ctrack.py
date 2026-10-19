"""acromion-pointer-arm-ctrack: a 2-hub gimbal at the shoulder (J1 scapula-fixed, J2 on the humeral 'equator') + the
humeral twist as a carriage on an ARM-FIXED C-track (the third active coordinate = the carriage's place on the track).
Shared kit (tools/concept_kit.py, docs/concepts/KIT.md) for the hubs, link 1, the yoke (L2), K2 continuity, K6
collisions and `over`, the audit and the scoring; two parts are placed by the model because they are not GH-ray parts:

  track    ARM-fixed, fitted RADIALLY from the humeral axis (pointer-cslide lesson 3: a part along the arm cannot be
           fitted on GH rays - the GH ray runs inside the arm, and the march then jumps over the torso and parks it at
           400 mm). Per sample (station s, arm angle th): the K3 march from the axis point s E outward along n(th) with a
           3 mm window (the arm's own skin; a torso within 15 mm must not lift an arm-fixed part - a pose where the
           torso reaches the track is a CONTACT pose), quantile qt over the closing poses. Fitted once per params in a
           pre-pass on the closing poses (`fit_track`) and handed to build() as a constant (build stays pose-local).
  carriage on the track at the arm angle th_arm (= q3) of the pose: 24 mm along the track x 16 mm along the arm;
           circ=1: the track's top is a CIRCULAR race about the humeral axis (radius = the track's highest skin face +
           3; the body under it skin-fitted = a saddle), the carriage is rigid on L2, NO passive joint (0 passive);
           circ=0: the spec - the carriage follows the skin-shaped track on a passive radial slide + swivel (its
           travel = the spread of the track height it meets, reported; a skin-normal slide stands travel + block).

Kinematics (bench frame, GH = origin): d = humeral axis (body_pose humerus frame E), a1 = F.S(bvec(az, el)) (J1),
u2 = K.closure(a1, d, al12, al23, sigma) (J2; 90/90 = orthogonal gimbal), pointing frame r_ref = unit(u2 - (u2.d)d),
t_ref = d x r_ref; the carriage sits at angle thc about d from r_ref; th_arm = its angle on the arm (0 lateral, +90
posterior); taken only if the carriage stays on the track [tc - tw/2, tc + tw/2] (arm frame) and the gimbal is >= the
fold margin from its poles. The yoke (L2, 12 x 3 strap u2 -> the carriage) passes over link 1, the track and the
carriage (+1 mm) by construction. The track is the arm end (BOTTOM cut and merged into it).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acromion-pointer-arm-ctrack.py eval '{json params}' [--big]
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "acromion-pointer-arm-ctrack"
NAME = "Acromion gimbal + arm-fixed skin-shaped C-track (2 DOF at the shoulder, axial rotation lower on the arm)"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
E = K.unit(np.array([-0.02273058, -0.98614607, 0.16431446]))          # GH -> elbow (body_pose humerus frame)
LAT = np.array([0.004, 0.164, 0.986]); LAT = K.unit(LAT - (LAT @ E) * E); POST = np.cross(E, LAT)
PARAMS = dict(az=30.0, el=0.0, sigma=1, al12=90.0, al23=90.0, s_t=40.0, tc=-10.0, tw=200.0, thc=-5.5, car=24.0,
              circ=1, twin=70.0, fork=1, margin=K.FOLD_MARGIN, width=12.0, t_link=3.0, q=0.95, qt=0.95)
CAR_H = 7.0                                                   # carriage body: skin face -> top (mm)


def nvec(th_deg):
    t = np.radians(np.asarray(th_deg, float)); return np.cos(t)[..., None] * LAT + np.sin(t)[..., None] * POST


def kin(F, p):
    d = F.H(E); a1 = F.S(K.bvec(p["az"], p["el"]))
    u2, ok, margin = K.closure(a1, d, p["al12"], p["al23"], p["sigma"], margin_deg=p["margin"])
    rr = K.unit(u2 - (u2 * d).sum(-1, keepdims=True) * d); tt = np.cross(d, rr)
    c = math.cos(math.radians(p["thc"])) * rr + math.sin(math.radians(p["thc"])) * tt
    th_arm = K.axis_angle(d, F.H(LAT), c)
    half = math.degrees(p["car"] / 2 / 50.0); lo, hi = p["tc"] - p["tw"] / 2 + half, p["tc"] + p["tw"] / 2 - half
    inw = (th_arm >= lo) & (th_arm <= hi)
    if p.get("twin"):                                         # a second shoe on L2, `twin` deg further round the race:
        t2 = (th_arm + p["twin"] + 180) % 360 - 180           # the open race is held by whichever shoe is on it
        inw = inw | ((t2 >= lo) & (t2 <= hi))
    return d, a1, u2, th_arm, ok & inw, margin


def track_grid(p):
    th = np.arange(p["tc"] - p["tw"] / 2, p["tc"] + p["tw"] / 2 + 1e-6, math.degrees(2.0 / 50.0))
    return np.arange(-4.0, 4.0 + 1e-6, 2.0), th


def fit_track(B, F, p, fit):
    """radial skin requirement of every track sample from the humeral axis (3 mm window), quantile qt over `fit` poses
    -> R (ns, nth) radial skin-face height (mm)"""
    ds, th = track_grid(p); Pi = np.nonzero(fit)[0]
    S, T = np.meshgrid(p["s_t"] + ds, th, indexing="ij"); n = nvec(T.ravel()); s = S.ravel()
    O = np.einsum("pij,j->pi", F.RH[Pi], E)[:, None, :] * s[None, :, None]
    D = np.einsum("pij,mj->pmi", F.RH[Pi], n)
    R = K.requirement(B, np.repeat(Pi, len(s)), D.reshape(-1, 3), t0=12.0, t1=160.0, win=3.0, O=O.reshape(-1, 3))
    R = R.reshape(len(Pi), -1); R = np.where(np.isfinite(R) & (R < 130.0), R, np.nan)   # torso / forearm in the way: not the arm's skin
    return np.nan_to_num(np.nanquantile(R, p["qt"], axis=0), nan=130.0).reshape(S.shape)   # those poses become contact poses


def car_local(p, Rt):
    """carriage skin-face samples relative to its centre: (along-track angle offsets deg, along-arm offsets mm)"""
    off = np.arange(-p["car"] / 2, p["car"] / 2 + 1e-6, 2.0) / 50.0 * 180 / math.pi
    return off, np.arange(-8.0, 8.0 + 1e-6, 2.0)


def build(B, F, p):
    d, a1, u2, th_arm, ok, margin = kin(F, p)
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), u2), K.axis_angle(u2, a1, d), th_arm], -1)
    Rt = np.asarray(p["_Rt"], float); ds, th = track_grid(p)
    Rcol = Rt.max(0)                                         # per track column: highest skin face over its width
    # track (arm-fixed): skin face at Rt; circ: race radius = max(Rcol) + 3 (saddle body under it)
    Pa = ((p["s_t"] + ds)[:, None, None] * E + Rt[..., None] * nvec(th)[None]).reshape(-1, 3)
    Ptr = np.einsum("pij,mj->pmi", F.RH, Pa)
    # carriage on the track at th_arm
    off, cds = car_local(p, Rt); tq = th_arm[:, None] + off[None]                  # (P, no)
    Rf = (np.full_like(tq, Rcol.max()) if p["circ"] else np.interp(tq, th, Rcol)) + 3.6   # carriage skin face: on the race / track top (+0.6)
    sc = (p["s_t"] + cds)[None, None, :]; Rf = Rf - 3.6                       # carriage on the race: its skin face 3.6 mm
    Rf = np.sqrt((np.sqrt(sc ** 2 + Rf[:, :, None] ** 2) + 3.6) ** 2 - sc ** 2)  # above the track face ALONG the GH ray (K6's metric)
    Pc = sc[..., None] * E + Rf[..., None] * nvec(tq)[:, :, None, :]
    Pc = np.einsum("pij,pmkj->pmki", F.RH, Pc).reshape(len(tq), -1, 3)
    extra = []
    if p.get("twin") and p["circ"]:                          # shoe 2 (rigid on L2, on the race when it is over the track)
        Pc2 = sc[..., None] * E + Rf[..., None] * nvec(tq + p["twin"])[:, :, None, :]
        Pc2 = np.einsum("pij,pmkj->pmki", F.RH, Pc2).reshape(len(tq), -1, 3)
        Rb = float(np.sqrt((np.sqrt(p["s_t"] ** 2 + Rf.max() ** 2) + CAR_H + 1.0) ** 2 - p["s_t"] ** 2))   # bridge over both shoes
        tb = np.linspace(0, 1, max(3, int(abs(p["twin"]) * math.pi / 180 * Rb / 2) + 1))
        tbq = th_arm[:, None] + tb[None] * p["twin"]; sb = np.arange(-6.0, 6.0 + 1e-6, 2.0)
        Pb = (p["s_t"] + sb)[None, None, :, None] * E + Rb * nvec(tbq)[:, :, None, :]
        Pb = np.einsum("pij,pmkj->pmki", F.RH, Pb).reshape(len(tq), -1, 3)
        extra = [K.Member("carriage2", Pc2, kind="free", t=CAR_H, width=16.0, joints=("J3",), cell=4.0, r_ref=1e4)]
        if not p.get("fork"):                                # shoe 2 on a bridge along the race (over both shoes) ...
            extra.append(K.Member("bridge", Pb, kind="free", t=3.0, width=12.0, joints=("J3",), cell=4.0, r_ref=1e4))
        else:                                                # ... or on its own tine from hub 2 (a fork yoke, skin-fitted)
            c2 = np.einsum("pij,pj->pi", F.RH, p["s_t"] * E + Rcol.max() * nvec(th_arm + p["twin"]))
            fork = K.strap_member("yoke2", u2, K.unit(c2), ("J2",), width=p["width"], t=p["t_link"], ramp_to=(("hub2", K.STACK), (None, 0.0)),
                                  over=[("link1", 1.0), ("track", 1.0), ("carriage", 1.0), ("carriage2", 1.0)])
    Rcc = np.full(len(th_arm), Rcol.max()) if p["circ"] else np.interp(th_arm, th, Rcol)
    cc = np.einsum("pij,pj->pi", F.RH, p["s_t"] * E + Rcc[:, None] * nvec(th_arm))
    yt = K.unit(cc)                                          # yoke end: over the carriage centre (pointing frame)
    w, t = p["width"], p["t_link"]
    track = K.Member("track", Ptr, kind="free", t=3.0, width=8.0, joints=("J3",), cell=4.0, r_ref=1e4)
    car = K.Member("carriage", Pc, kind="free", t=CAR_H, width=16.0, joints=("J3",), cell=4.0, r_ref=1e4)
    members = [K.hub_member("hub1", a1, "J1"), K.hub_member("hub2", u2, "J2"),
               K.strap_member("link1", a1, u2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
               K.strap_member("yoke", u2, yt, ("J2",), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                              over=[("link1", 1.0), ("track", 1.0), ("carriage", 1.0)] + [(m.name, 1.0) for m in extra]),  # yoke (tine 1)
               track, car] + extra + ([fork] if p.get("twin") and p["circ"] and p.get("fork") else [])
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=a1, J2=u2, J3=d), hubless=("J3",),
                   info=dict(residual_deg=round(float(K.closure_residual(a1, d, u2, p["al12"], p["al23"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


FIXED = ("track", "carriage", "carriage2", "bridge")                                # placed by the model: profile 1 (D holds the points)


def collide(ch, pts, ok):
    """K6 on every member pair, except the two tines of the fork yoke (one rigid body, merged at hub 2): each tine is
    checked against every other member"""
    names = [m.name for m in ch.members]
    if "yoke2" not in names: return K.collisions(ch, pts, ok)
    a = K.Chain(members=[m for m in ch.members if m.name != "yoke2"], ok=ok, joints=ch.joints)
    b = K.Chain(members=[m for m in ch.members if m.name != "yoke"], ok=ok, joints=ch.joints)
    return K.collisions(a, pts, ok) | K.collisions(b, pts, ok)


def evaluate(B, p, verbose=False, q=None):
    """K.evaluate's pipeline with the two model-placed parts: K2 dense, kit fit of hubs / link 1 / yoke, the yoke
    raised over link 1 + track + carriage (K6 by construction), K6 on every pair, bench scoring of every sample"""
    held = set(json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"])
    if held & set(B.clip): raise ValueError("held-out clips in the bench")
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F; q = p.get("q", 1.0) if q is None else q
    p = dict(p); p.pop("_Rt", None)
    _, _, _, _, ok0, _ = kin(F, p)
    if not ok0.any(): return dict(gap=999.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, closure=0.0, honest=False, kmode="march", overhead="0/0")
    p["_Rt"] = fit_track(B, F, p, ok0).tolist()
    ch = build(B, F, p); ok, flips = K.continuity_dense(B, F, build, p, np.asarray(ch.ok, bool))
    fitm = [m for m in ch.members if m.name not in FIXED]
    yks = [m for m in fitm if m.name in ("yoke", "yoke2")]; overs = [m.over for m in yks]
    for m in yks: m.over = [("link1", 1.0)]
    prof = K.fit_profiles(B, K.Chain(members=fitm, ok=ok, joints=ch.joints), ok, q, "march")
    for m in ch.members:
        if m.name in FIXED: prof[m.name] = np.ones(m.D.shape[1])
    for yk, over in zip(yks, overs):                          # the yoke tines pass over the arm-fixed parts + the shoes
        yk.over = over; r = K._over(ch, yk, prof[yk.name], prof, ok)
        ns, nc = yk.grid; R2 = r.reshape(ns, nc); x = np.arange(ns) * yk.step_mm; sl = math.tan(yk.climb_deg * K.D2R)
        prof[yk.name] = (R2[None, :, :] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1).ravel()
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = collide(ch, pts, ok); take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    dd = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = dd[j]
    rep = B.report(); clip = np.array([B.kind[i] == "clip" for i in Pi], bool); good = dd.min(1) >= 0 if len(Pi) else np.zeros(0, bool)
    per, cmem, hmem = {}, {}, {}; o = 0
    for m in ch.members:
        s = pts[m.name].shape[1]; dm = dd[:, o:o + s]; o += s
        per[m.name] = round(float(((dm[clip & good] >= 2) & (dm[clip & good] <= 14)).mean()), 4) if (clip & good).any() else 0.0
        cmem[m.name] = round(float((dm.min(1) < 0).mean()), 3) if len(Pi) else 0.0
        hmem[m.name] = round(float(np.median(np.linalg.norm(pts[m.name][Pi], axis=-1))), 1) if len(Pi) else None
    problems, density = K.audit(B, F, build, p, ch, pts, take if take.any() else ok)
    Rt = np.asarray(p["_Rt"]); Rcol = Rt.max(0); _, th = track_grid(p); _, _, _, th_arm, _, _ = kin(F, p)
    used = np.interp(th_arm[take], th, Rcol) if take.any() else np.zeros(1)
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    ws = np.array(B.kind) == "ws"; ov = np.array([B.poses[i]["elev"] >= 140 for i in range(len(B.poses))])
    rep.update(inband_member=per, contact_member=cmem, rho_member=hmem, closure=round(float(np.mean(ch.ok)), 4), flips=int(flips),
               collide=round(float(np.mean(hit[ok])) if ok.any() else 0.0, 4), q=q, kmode="march", **ch.info,
               checks=dict(mode="march", cont=True, collide=True, q=q), honest=not problems, audit=problems, sample_mm=density,
               hubless=list(ch.hubless), overhead=f"{int((taken & ws & ov).sum())}/{int((ws & ov).sum())}",
               slide_travel=0.0 if p["circ"] else round(float(used.max() - used.min()), 1),
               race_float=round(float(Rcol.max() - np.median(used)), 1),
               track_R=[round(float(Rcol.min()), 1), round(float(Rcol.max()), 1)],
               min_metal=round(float(dd.min()), 2) if len(Pi) else None,
               near1=round(float(np.mean(dd.min(1) < 1)), 4) if len(Pi) else 0.0)
    if verbose: print(json.dumps({k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "overhead", "inband_member", "contact_member", "rho_member", "slide_travel", "race_float", "track_R", "min_metal", "near1", "closure", "flips", "collide", "min_margin", "honest", "audit", "mode")}))
    B._kit_last = dict(chain=ch, prof=prof, pts=pts, take=take, ok=ok, hit=hit, p=p)
    return rep


def wear(Bs, Bb, p):
    """FROZEN wear: fit on Bs (the screening bench), then put the SAME shape (track skin face, hub levels, link and yoke
    undersides) on Bb's poses with no refit: K2 dense, K6, every sample's signed distance on Bb (exact path if Bb has
    no fast cache). -> Bb report (+ overhead, per-member in-band / contact, min th margin to the gimbal poles)"""
    evaluate(Bs, p); L = Bs._kit_last; ps = L["p"]; prof_s = L["prof"]
    F = K.frames(Bb); Bb._kitF = F; ch = build(Bb, F, ps); ok, flips = K.continuity_dense(Bb, F, build, ps, np.asarray(ch.ok, bool))
    prof = {}
    for m in ch.members:
        if m.name in FIXED: prof[m.name] = np.ones(m.D.shape[1]); continue
        r = prof_s[m.name]; n = m.D.shape[1] if m.kind != "flat" else len(m.xy)
        if len(r) != n:                                       # strap sample count follows the median arc: resample along it
            ns0 = len(r) // m.grid[1]; R2 = r.reshape(ns0, m.grid[1]); x0 = np.linspace(0, 1, ns0); x1 = np.linspace(0, 1, m.grid[0])
            r = np.stack([np.interp(x1, x0, R2[:, j]) for j in range(m.grid[1])], 1).ravel()
        prof[m.name] = r
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = collide(ch, pts, ok); take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    dd = K.dist_many(Bb, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    Bb.reset()
    for j, i in enumerate(Pi): Bb.res[i] = dd[j]
    rep = Bb.report(); clip = np.array([Bb.kind[i] == "clip" for i in Pi], bool); good = dd.min(1) >= 0
    per, cmem = {}, {}; o = 0
    for m in ch.members:
        s_ = pts[m.name].shape[1]; dm = dd[:, o:o + s_]; o += s_
        per[m.name] = round(float(((dm[clip & good] >= 2) & (dm[clip & good] <= 14)).mean()), 4) if (clip & good).any() else 0.0
        cmem[m.name] = int((dm.min(1) < 0).sum())
    taken = np.array([Bb.res[i] is not None and float(np.min(Bb.res[i])) >= 0 for i in range(len(Bb.res))])
    ws = np.array(Bb.kind) == "ws"; ov = np.array([Bb.poses[i]["elev"] >= 140 for i in range(len(Bb.poses))])
    _, _, _, _, _, margin = kin(F, ps)
    rep.update(inband_member=per, contact_poses_member=cmem, contact_poses=int((dd.min(1) < 0).sum()), flips=int(flips),
               overhead=f"{int((taken & ws & ov).sum())}/{int((ws & ov).sum())}", taken_ws=int((taken & ws).sum()),
               min_margin_taken=round(float(margin[taken].min()), 2) if taken.any() else None,
               near1_gap=CB_gap_near(Bb), min_metal=round(float(dd.min()), 2) if len(Pi) else None)
    return rep


def CB_gap_near(Bb):
    """the gap if metal < 1 mm counted as contact (near-touch, reported only)"""
    import concept_bench as CB
    ws = [j for j, k in enumerate(Bb.kind) if k == "ws"]; cl = [j for j, k in enumerate(Bb.kind) if k == "clip"]
    ok = lambda j: Bb.res[j] is not None and float(np.min(Bb.res[j])) >= 1.0
    taken = [j for j in cl if ok(j)]; d = np.concatenate([Bb.res[j] for j in taken]) if taken else np.zeros(0)
    nz = [j for j in range(len(Bb.kind)) if Bb.res[j] is not None]
    return CB.gap_of(float(np.mean((d >= 2) & (d <= 14))) if len(d) else 0.0, float(np.mean([ok(j) for j in cl])),
                     float(np.mean([ok(j) for j in ws])), float(np.mean([float(np.min(Bb.res[j])) < 1 for j in nz])) if nz else 0.0)


def best_thc(F, p):
    """the carriage angle in the pointing frame that puts the most poses (ws + 0.3 x clips) inside the track window"""
    best = (-1, 0.0); _, _, _, th0, _, _ = kin(F, dict(p, thc=0.0)); _, _, _, _, okc, _ = kin(F, dict(p, thc=0.0, tw=720.0, twin=0))
    half = math.degrees(p["car"] / 2 / 50.0); lo, hi = p["tc"] - p["tw"] / 2 + half, p["tc"] + p["tw"] / 2 - half
    wrap = lambda x: (x + 180) % 360 - 180
    for c in np.arange(-180, 180, 2.0):                       # th_arm(thc) = th_arm(0) + thc (rotation about d)
        t1 = wrap(th0 + c); inw = (t1 >= lo) & (t1 <= hi)
        if p.get("twin"): t2 = wrap(t1 + p["twin"]); inw = inw | ((t2 >= lo) & (t2 <= hi))
        inw = inw & okc; sc = inw[F.ws].mean() + 0.3 * inw[F.clip].mean()
        if sc > best[0]: best = (sc, float(c))
    return round(best[1], 1)


def log_sweep(entry):
    import fcntl
    with open(SWEEP_JSON + ".lock", "w") as lk:                # two local processes append to one ordered list
        fcntl.flock(lk, fcntl.LOCK_EX)
        rows = json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) else []
        entry = dict(k=len(rows), t=K.now(), **entry); rows.append(entry)
        json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
    return entry


CMA_BOX = dict(twin=(60, 120), az=(-30, 90), el=(-20, 85), s_t=(30, 110), tc=(-40, 40), tw=(100, 200), dthc=(-60, 60), qt=(0.85, 1.0),
               q=(0.85, 1.0), al12=(70, 110), al23=(70, 110))


def cma(B, x0, n_eval, circ, sigma0=0.25, lam=10, seed=0, tag="cma"):
    """compact CMA-ES (Hansen's (mu/mu_w, lambda) with rank-1 + rank-mu updates) on the box-normalised CMA_BOX
    parameters; thc = best_thc(...) + dthc; every evaluation appended to the sweep file"""
    F = K.frames(B); keys = list(CMA_BOX); lo = np.array([CMA_BOX[k][0] for k in keys], float); hi = np.array([CMA_BOX[k][1] for k in keys], float)
    def to_p(z):
        v = lo + np.clip(z, 0, 1) * (hi - lo); pp = dict(PARAMS, circ=circ, **{k: float(x) for k, x in zip(keys, v)})
        dth = pp.pop("dthc"); pp["thc"] = round(best_thc(F, pp) + dth, 1); return pp
    rng = np.random.default_rng(seed); n = len(keys); m = (np.array([x0.get(k, (CMA_BOX[k][0] + CMA_BOX[k][1]) / 2) for k in keys]) - lo) / (hi - lo)
    mu = lam // 2; w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5); c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff)); ds = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); sg = sigma0; chi = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n)); done = 0; best = None
    while done < n_eval:
        Dg, Bm = np.linalg.eigh(C); Dg = np.sqrt(np.maximum(Dg, 1e-20)); Z = rng.standard_normal((lam, n)); Y = Z @ np.diag(Dg) @ Bm.T
        X = m + sg * Y; f = []
        for x in X:
            pp = to_p(x); r = run(B, pp, tag=f"{tag} circ{circ}"); g = r["gap"] + 50 * float(np.sum(np.abs(x - np.clip(x, 0, 1))))
            f.append(g); done += 1
            if best is None or r["gap"] < best[0]: best = (r["gap"], pp)
        idx = np.argsort(f); yw = (Y[idx[:mu]] * w[:, None]).sum(0); m = m + sg * yw
        Ci = Bm @ np.diag(1 / Dg) @ Bm.T; ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (Ci @ yw)
        hs = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * done / lam)) < (1.4 + 2 / (n + 1)) * chi
        pc = (1 - cc) * pc + hs * math.sqrt(cc * (2 - cc) * mueff) * yw
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hs) * cc * (2 - cc) * C) + cmu * (Y[idx[:mu]].T * w) @ Y[idx[:mu]]
        sg *= math.exp((cs / ds) * (np.linalg.norm(ps) / chi - 1)); print(f"  gen: best {best[0]} sigma {sg:.3f}", flush=True)
    return best


def run(B, p, tag=""):
    t0 = time.time(); r = evaluate(B, p)
    e = dict(params={k: v for k, v in p.items() if k != "_Rt"}, **{x: r.get(x) for x in ("inband14", "inband10", "reach", "follow", "contact", "gap", "closure", "honest", "overhead", "slide_travel", "race_float")},
             kmode="march", bench=f"{len([k for k in B.kind if k == 'clip'])},{len([k for k in B.kind if k == 'ws'])}", mode=B.mode,
             inband_member=r.get("inband_member"), contact_member=r.get("contact_member"), tag=tag)
    e = log_sweep(e)
    print(f"[{e['k']}] {tag} gap {r['gap']} reach {r['reach']} follow {r['follow']} ib14 {r['inband14']} c {r['contact']} ov {r.get('overhead')} "
          f"{r.get('inband_member')} cm {r.get('contact_member')} {time.time() - t0:.0f}s", flush=True)
    return r


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "eval"
    B = K.bench(110, 360) if "--big" in a else K.bench(60, 160)
    if mode == "eval":
        p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}))
        evaluate(B, p, verbose=True)
    elif mode == "coarse":                                # coarse grid; thc = the densest carriage window (ws + 0.3 clips)
        F = K.frames(B); grid = json.loads(a[1]); cfgs = []
        import itertools
        for vals in itertools.product(*grid.values()):
            pp = dict(PARAMS, **dict(zip(grid.keys(), vals)))
            if isinstance(pp.get("arc"), list): pp["tc"], pp["tw"] = (pp["arc"][0] + pp["arc"][1]) / 2, pp["arc"][1] - pp["arc"][0]
            pp.pop("arc", None); pp["thc"] = best_thc(F, pp); cfgs.append(pp)
        for pp in cfgs: run(B, pp, tag=a[2] if len(a) > 2 else "coarse")
    elif mode == "wear":                                  # wear '{params}': fit on Bench(60,160), frozen on Bench(110,360)
        p = dict(PARAMS, **json.loads(a[1])); Bb = K.bench(110, 360); t0 = time.time(); r = wear(B, Bb, p)
        out = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "mode", "overhead", "taken_ws", "contact_poses",
                                 "contact_poses_member", "inband_member", "min_margin_taken", "near1_gap", "min_metal", "flips")}
        out["secs"] = round(time.time() - t0); print("WEAR", json.dumps(out), flush=True)
    elif mode == "cma":                                   # cma '{x0}' n_eval circ seed
        x0 = json.loads(a[1]); best = cma(B, x0, int(a[2]), int(a[3]), seed=int(a[4]) if len(a) > 4 else 0, sigma0=float(a[5]) if len(a) > 5 else 0.25)
        print("BEST", best)
    elif mode == "run":                                   # evaluate + append to the sweep file: run '[{...}, {...}]' tag
        for pp in json.loads(a[1]): run(B, dict(PARAMS, **pp), tag=a[2] if len(a) > 2 else "")
