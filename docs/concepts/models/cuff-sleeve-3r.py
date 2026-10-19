"""cuff-sleeve-3r: a spherical 3R about GH whose third joint is a GH-aimed O5 rod turning (and floating 5 mm) in an
MR85-pair sleeve on the cuff near the distal upper arm. Shared kit (tools/concept_kit.py, docs/concepts/KIT.md) for the
hubs, link 1, link 2's deltoid-cap strap, K2 dense continuity, K6 collisions + `over`, the audit and the scoring; the
parts that are not GH-ray parts are placed by the model:

  spar     link 2's run down the arm, fixed in the POINTING frame (e3, r_ref = p2 projected off e3): stations s along
           e3 at azimuth psi_b, underside fitted RADIALLY from the e3 line (K3 march along n_b from the e3 point, 3 mm
           window = the arm's own skin; a torso there is a CONTACT pose), quantile q over the closing poses, climb
           <= 60 deg along s. Fitted once per params in a pre-pass (`fit_parts`) and handed to build() as a constant.
  crank    a 12 x 4 plate at the rod's proximal end (station s_c), from the rod out along n_b to the spar (pointing frame).
  rod      O5 along e3 from s_c to s3 + 20 (pointing frame, but a cylinder about e3: the same in every frame).
  sleeve   O11 x 30 housing (two MR85ZZ 5 x 8 x 2.5, rotation + 5 mm axial float) about e3 at s3: ARM-fixed.
  foot     the sleeve's saddle on the cuff (BOTTOM cut and merged into it): arm-fixed, skin face fitted radially from
           the humeral axis at the arm's own skin (3 mm window), quantile qf over all bench poses; e3's tilt gamma is
           SET by it: the sleeve's skin-side generator clears the foot's skin face by >= 1.5 mm over the sleeve's length.

Kinematics (bench frame, GH = origin): E = GH -> elbow (body_pose humerus frame), e3_0 = cos(gamma) E + sin(gamma)
n(psi3) (psi3 0 lateral, +90 posterior), e3 = F.H(e3_0); p1 = F.S(bvec(az, el)) (J1); p2 = K.closure(p1, e3, a1, a2,
sigma) (J2); J3 = the arm's angle about e3 from the pointing frame (unlimited: a rod turning in a sleeve). Taken only if
the dyad is >= the fold margin (5 deg in th = angle(p1, e3)) from its fold.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cuff-sleeve-3r.py eval '{json params}'
    ... run '[{...}, ...]' tag | wear '{params}' (fit Bench(60,160), frozen exact Bench(110,360))
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "cuff-sleeve-3r"
NAME = "Spherical 3R with the twist joint as a GH-aimed rod-and-sleeve near the cuff"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
E = K.unit(np.array([-0.02273058, -0.98614607, 0.16431446]))          # GH -> elbow (body_pose humerus frame)
LAT = np.array([0.004, 0.164, 0.986]); LAT = K.unit(LAT - (LAT @ E) * E); POST = np.cross(E, LAT)
PARAMS = dict(az=30.0, el=70.0, sigma=1, a1=90.0, a2=90.0, psi3=0.0, s3=230.0, psi_b=0.0, s_a=45.0,
              margin=K.FOLD_MARGIN, width=12.0, t_link=3.0, q=0.95, qf=1.0)
SLEEVE_R, SLEEVE_L, ROD_R, CRANK_T, FOOT_MIN = 5.5, 30.0, 2.5, 4.0, 1.5


def nvec(psi):
    t = np.radians(np.asarray(psi, float)); return np.cos(t)[..., None] * LAT + np.sin(t)[..., None] * POST


def foot_grid(p):
    s = np.arange(p["s3"] - SLEEVE_L / 2, p["s3"] + SLEEVE_L / 2 + 1e-6, 2.0)
    w = np.arange(-6.0, 6.0 + 1e-6, 2.0)                                       # 12 mm wide saddle (arc mm at the skin)
    return s, w


def fit_foot(B, F, p):
    """arm-fixed saddle under the sleeve: radial skin requirement from the humeral axis (3 mm window), quantile qf over
    every bench pose -> R (ns, nw) skin-face radius (mm), and the e3 tilt gamma (deg) it sets"""
    s, w = foot_grid(p); S, W = np.meshgrid(s, w, indexing="ij"); r0 = 48.0
    psi = p["psi3"] + np.degrees(W.ravel() / r0); n = nvec(psi); P = len(B.kind); I = np.arange(P)
    O = np.einsum("pij,j->pi", F.RH, E)[:, None, :] * S.ravel()[None, :, None]
    D = np.einsum("pij,mj->pmi", F.RH, n)
    R = K.requirement(B, np.repeat(I, S.size), D.reshape(-1, 3), t0=15.0, t1=120.0, win=3.0, O=O.reshape(-1, 3)).reshape(P, -1)
    R = np.where(np.isfinite(R) & (R < 110.0), R, np.nan)
    R = np.nan_to_num(np.nanquantile(R, p["qf"], axis=0), nan=110.0).reshape(S.shape)
    need = (R.max(1) + FOOT_MIN + SLEEVE_R) / s                                 # tan(gamma) so the sleeve clears the foot
    return R, float(np.degrees(np.arctan(need.max())))


def e3_of(p):
    g = math.radians(p["_gamma"]); return K.unit(math.cos(g) * E + math.sin(g) * nvec(p["psi3"]))


def kin(F, p):
    e3l = e3_of(p); e3 = F.H(e3l); p1 = F.S(K.bvec(p["az"], p["el"]))
    p2, ok, margin = K.closure(p1, e3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    rr = K.unit(p2 - (p2 * e3).sum(-1, keepdims=True) * e3); tt = np.cross(e3, rr)
    nb = math.cos(math.radians(p["psi_b"])) * rr + math.sin(math.radians(p["psi_b"])) * tt
    tb = np.cross(e3, nb)
    return e3, p1, p2, nb, tb, ok, margin


def stations(p):
    s_c = p["s3"] - SLEEVE_L / 2 - 2.0 - CRANK_T / 2                            # crank centre: 2 mm proximal of the sleeve
    return np.arange(p["s_a"], s_c + 1e-6, 2.0), s_c


def fit_spar(B, F, p, fit):
    """spar underside offset from the e3 line per (station, width) sample: K3 march along n_b from the e3 point (3 mm
    window), quantile q over `fit` poses, then climb <= 60 deg along s (raises only)"""
    e3, _, _, nb, tb, _, _ = kin(F, p); s, _ = stations(p); w = np.arange(-p["width"] / 2 + 1, p["width"] / 2, 2.0)
    Pi = np.nonzero(fit)[0]; S, W = np.meshgrid(s, w, indexing="ij")
    O = e3[Pi][:, None, :] * S.ravel()[None, :, None] + tb[Pi][:, None, :] * W.ravel()[None, :, None]
    D = np.repeat(nb[Pi][:, None, :], S.size, 1)
    R = K.requirement(B, np.repeat(Pi, S.size), D.reshape(-1, 3), t0=4.0, t1=160.0, win=3.0, O=O.reshape(-1, 3)).reshape(len(Pi), -1)
    R = np.where(np.isfinite(R) & (R < 150.0), R, np.nan)
    R = np.nan_to_num(np.nanquantile(R, p["q"], axis=0), nan=150.0).reshape(S.shape)
    R = np.maximum(R, ROD_R + 2.0)
    sl = math.tan(math.radians(60.0)); R = (R[None, :, :] - sl * np.abs(s[:, None, None] - s[None, :, None])).max(1)
    return R


def cyl(axis_pts, ax, ref, rad, s_lo, s_hi, half=True):
    """sample points of a cylinder of radius rad about the line x = s ax (s in [s_lo, s_hi]); half: only the half facing
    -ref (ref: the outward direction, i.e. sample the side facing the arm). ax, ref: (P, 3)"""
    s = np.arange(s_lo, s_hi + 1e-6, 2.0); n_ang = max(4, int(math.ceil(math.pi * rad / 2.0)) + 1)
    ang = np.linspace(math.pi / 2, 3 * math.pi / 2, n_ang) if half else np.linspace(0, 2 * math.pi, 2 * n_ang, endpoint=False)
    u = K.unit(ref - (ref * ax).sum(-1, keepdims=True) * ax); v = np.cross(ax, u)
    C = np.cos(ang)[None, :, None] * u[:, None, :] + np.sin(ang)[None, :, None] * v[:, None, :]           # (P, na, 3)
    X = s[None, :, None, None] * ax[:, None, None, :] + rad * C[:, None, :, :]
    return X.reshape(len(ax), -1, 3)


def build(B, F, p):
    e3, p1, p2, nb, tb, ok, margin = kin(F, p)
    e3l = e3_of(p); armc = F.H(E)                                               # arm axis (for the sleeve's skin side)
    s, s_c = stations(p); Rs = np.asarray(p["_Rs"], float); w = np.arange(-p["width"] / 2 + 1, p["width"] / 2, 2.0)
    # spar (pointing frame) at its fitted underside
    Psp = (s[None, :, None, None] * e3[:, None, None, :] + w[None, None, :, None] * tb[:, None, None, :]
           + Rs[None, :, :, None] * nb[:, None, None, :]).reshape(len(e3), -1, 3)
    # crank: plate at s_c from the rod (r 3) out to the spar's last underside, both faces (s_c +- CRANK_T / 2)
    rc = float(Rs[-1].max()); tcr = np.arange(ROD_R + 1.0, rc + 1e-6, 2.0); wc = np.arange(-5.0, 5.0 + 1e-6, 2.0)
    sc = np.array([s_c - CRANK_T / 2, s_c + CRANK_T / 2])
    Pcr = (sc[None, :, None, None, None] * e3[:, None, None, None, :] + tcr[None, None, :, None, None] * nb[:, None, None, None, :]
           + wc[None, None, None, :, None] * tb[:, None, None, None, :]).reshape(len(e3), -1, 3)
    # rod (cylinder about e3, skin side = toward the arm axis) from the crank to the sleeve and its distal collar
    out = K.unit(e3 * 0 + (np.einsum("pij,j->pi", F.RH, e3l) - armc))           # outward from the arm axis, normal to e3 (approx.)
    out = K.unit(out - (out * e3).sum(-1, keepdims=True) * e3)
    Prod = np.concatenate([cyl(None, e3, out, ROD_R, s_c + CRANK_T / 2, p["s3"] - SLEEVE_L / 2, True),
                           cyl(None, e3, out, ROD_R, p["s3"] + SLEEVE_L / 2, p["s3"] + SLEEVE_L / 2 + 5.0, True)], 1)
    # sleeve (arm-fixed), skin side
    Psl = cyl(None, e3, out, SLEEVE_R, p["s3"] - SLEEVE_L / 2, p["s3"] + SLEEVE_L / 2, True)
    # foot (arm-fixed) skin face at the fitted radius from the humeral axis
    Rf = np.asarray(p["_Rf"], float); fs, fw = foot_grid(p); FS, FW = np.meshgrid(fs, fw, indexing="ij")
    loc = FS.ravel()[:, None] * E + Rf.ravel()[:, None] * nvec(p["psi3"] + np.degrees(FW.ravel() / 48.0))
    Pft = np.einsum("pij,mj->pmi", F.RH, loc)
    q3 = K.axis_angle(e3, F.H(K.unit(LAT - (LAT @ e3l) * e3l)), p2)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, e3), q3], -1)
    w_, t_ = p["width"], p["t_link"]
    a_end = math.degrees(math.atan2(float(Rs[0].max()), p["s_a"]))               # the cap strap ends over the spar's start
    ce = K.unit(math.cos(math.radians(a_end)) * e3 + math.sin(math.radians(a_end)) * nb)
    mk = lambda name, P_, t, wd, jn: K.Member(name, P_, kind="free", t=t, width=wd, joints=jn, cell=4.0, r_ref=1e4)
    members = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"),
               K.strap_member("link1", p1, p2, ("J1", "J2"), width=w_, t=t_, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
               K.strap_member("cap", p2, ce, ("J2", "J3"), width=w_, t=t_, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                              over=[("link1", 1.0)]),
               mk("spar", Psp, t_, w_, ("J2", "J3")), mk("crank", Pcr, CRANK_T, 10.0, ("J2", "J3")),
               mk("rod", Prod, 2 * ROD_R, 2 * ROD_R, ("J3",)), mk("sleeve", Psl, 2 * SLEEVE_R, 2 * SLEEVE_R, ("J3",)),
               mk("foot", Pft, 3.0, 12.0, ("J3",))]
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=e3), hubless=("J3",),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, e3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None, gamma=round(p["_gamma"], 2)))


FIXED = ("spar", "crank", "rod", "sleeve", "foot")                             # placed by the model: profile 1 (D holds the points)
LINK2 = ("cap", "spar", "crank", "rod")                                         # one rigid body (link 2): no K6 among them


def collide(ch, pts, ok):
    """K6 on every member pair except within link 2 (cap, spar, crank, rod: one rigid part) and rod-sleeve (the joint)"""
    names = [m.name for m in ch.members]; hit = np.zeros(len(ok), bool)
    groups = [[n for n in names if n not in LINK2] + [l2] for l2 in LINK2]
    for g in groups:
        mem = [m for m in ch.members if m.name in g]
        if "rod" in g: mem = [m for m in mem if m.name != "sleeve"]           # the rod runs in the sleeve (the joint)
        hit |= K.collisions(K.Chain(members=mem, ok=ok, joints=ch.joints), pts, ok)
    return hit


def prepare(B, F, p):
    p = dict(p); p.pop("_Rs", None); p.pop("_Rf", None)
    key = (round(p["psi3"], 3), round(p["s3"], 3), round(p["qf"], 4), len(B.kind))
    cache = getattr(B, "_foot_cache", {}); B._foot_cache = cache
    if key not in cache: cache[key] = fit_foot(B, F, p)
    Rf, g = cache[key]; p["_Rf"] = Rf.tolist(); p["_gamma"] = g
    return p


def score(B, ch, pts, ok, hit):
    take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    dd = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = dd[j]
    rep = B.report(); clip = np.array([B.kind[i] == "clip" for i in Pi], bool); good = dd.min(1) >= 0 if len(Pi) else np.zeros(0, bool)
    per, cmem = {}, {}; o = 0
    for m in ch.members:
        s_ = pts[m.name].shape[1]; dm = dd[:, o:o + s_]; o += s_
        per[m.name] = round(float(((dm[clip & good] >= 2) & (dm[clip & good] <= 14)).mean()), 4) if (clip & good).any() else 0.0
        cmem[m.name] = int((dm.min(1) < 0).sum()) if len(Pi) else 0
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    ws = np.array(B.kind) == "ws"; ov = np.array([B.poses[i]["elev"] >= 140 for i in range(len(B.poses))])
    rep.update(inband_member=per, contact_poses_member=cmem, contact_poses=int((dd.min(1) < 0).sum()) if len(Pi) else 0,
               overhead=f"{int((taken & ws & ov).sum())}/{int((ws & ov).sum())}", taken_ws=int((taken & ws).sum()),
               min_metal=round(float(dd.min()), 2) if len(Pi) else None, near1_gap=gap_near(B))
    return rep, taken, dd


def evaluate(B, p, verbose=False, q=None):
    """K.evaluate's pipeline with the model-placed parts: K2 dense, kit fit of hubs / link 1 / cap, the cap over link 1
    (K6 by construction), K6 on every pair, bench scoring of every sample"""
    held = set(json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"])
    if held & set(B.clip): raise ValueError("held-out clips in the bench")
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F; q = p.get("q", 1.0) if q is None else q
    p = prepare(B, F, p)
    ok0 = kin(F, p)[5]
    if not ok0.any(): return dict(gap=999.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, closure=0.0, honest=False, overhead="0/0")
    p["_Rs"] = fit_spar(B, F, p, ok0).tolist()
    ch = build(B, F, p); ok, flips = K.continuity_dense(B, F, build, p, np.asarray(ch.ok, bool))
    fitm = [m for m in ch.members if m.name not in FIXED]
    prof = K.fit_profiles(B, K.Chain(members=fitm, ok=ok, joints=ch.joints), ok, q, "march")
    for m in ch.members:
        if m.name in FIXED: prof[m.name] = np.ones(m.D.shape[1])
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = collide(ch, pts, ok); rep, taken, dd = score(B, ch, pts, ok, hit)
    problems, density = K.audit(B, F, build, p, ch, pts, (ok & ~hit) if (ok & ~hit).any() else ok)
    # the cap-to-spar junction step (cap end radius vs the spar's first station, along the GH ray)
    cap_end = float(np.median(prof["cap"].reshape(ch.members[3].grid)[-1])); sp0 = float(math.hypot(p["s_a"], np.asarray(p["_Rs"])[0].max()))
    _, _, _, _, _, _, margin = kin(F, p)
    rep.update(closure=round(float(np.mean(ch.ok)), 4), flips=int(flips), collide=round(float(np.mean(hit[ok])) if ok.any() else 0.0, 4),
               q=q, kmode="march", **ch.info, checks=dict(mode="march", cont=True, collide=True, q=q), honest=not problems,
               audit=problems, sample_mm=density, hubless=list(ch.hubless), junction_step=round(cap_end - sp0, 1),
               spar_off=[round(float(np.min(p["_Rs"])), 1), round(float(np.max(p["_Rs"])), 1)],
               min_margin_taken=round(float(margin[taken].min()), 2) if taken.any() else None)
    if verbose: print(json.dumps({k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "overhead", "taken_ws", "inband_member",
                                                    "contact_poses_member", "min_metal", "near1_gap", "closure", "flips", "collide", "min_margin",
                                                    "min_margin_taken", "gamma", "junction_step", "spar_off", "honest", "audit", "mode")}))
    B._kit_last = dict(chain=ch, prof=prof, pts=pts, take=ok & ~hit, ok=ok, hit=hit, p=p, dd=dd)
    return rep


def wear(Bs, Bb, p):
    """FROZEN wear: fit on Bs (the screening bench), then put the SAME shape (foot, spar, hub levels, link 1 and cap
    undersides) on Bb's poses with no refit: K2 dense, K6, every sample's signed distance on Bb"""
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
    hit = collide(ch, pts, ok); rep, taken, dd = score(Bb, ch, pts, ok, hit)
    _, _, _, _, _, _, margin = kin(F, ps)
    rep.update(flips=int(flips), min_margin_taken=round(float(margin[taken].min()), 2) if taken.any() else None, closure=round(float(np.mean(ch.ok)), 4))
    Bb._kit_last = dict(chain=ch, prof=prof, pts=pts, take=ok & ~hit, ok=ok, hit=hit, p=ps, dd=dd, taken=taken)
    return rep


def gap_near(Bb):
    """the gap if metal < 1 mm counted as contact (near-touch, reported only)"""
    import concept_bench as CB
    ws = [j for j, k in enumerate(Bb.kind) if k == "ws"]; cl = [j for j, k in enumerate(Bb.kind) if k == "clip"]
    ok = lambda j: Bb.res[j] is not None and float(np.min(Bb.res[j])) >= 1.0
    taken = [j for j in cl if ok(j)]; d = np.concatenate([Bb.res[j] for j in taken]) if taken else np.zeros(0)
    nz = [j for j in range(len(Bb.kind)) if Bb.res[j] is not None]
    return CB.gap_of(float(np.mean((d >= 2) & (d <= 14))) if len(d) else 0.0, float(np.mean([ok(j) for j in cl])),
                     float(np.mean([ok(j) for j in ws])), float(np.mean([float(np.min(Bb.res[j])) < 1 for j in nz])) if nz else 0.0)


def log_sweep(entry):
    import fcntl
    with open(SWEEP_JSON + ".lock", "w") as lk:                # two local processes append to one ordered list
        fcntl.flock(lk, fcntl.LOCK_EX)
        rows = json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) else []
        entry = dict(k=len(rows), t=K.now(), **entry); rows.append(entry)
        json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
    return entry


def run(B, p, tag=""):
    t0 = time.time(); r = evaluate(B, p)
    e = dict(params={k: v for k, v in p.items() if not k.startswith("_")}, **{x: r.get(x) for x in ("inband14", "inband10", "reach", "follow", "contact", "gap", "closure", "honest", "overhead", "gamma", "junction_step")},
             kmode="march", bench=f"{len([k for k in B.kind if k == 'clip'])},{len([k for k in B.kind if k == 'ws'])}", mode=B.mode,
             inband_member=r.get("inband_member"), contact_poses_member=r.get("contact_poses_member"), tag=tag)
    e = log_sweep(e)
    print(f"[{e['k']}] {tag} gap {r['gap']} reach {r['reach']} follow {r['follow']} ib14 {r['inband14']} c {r['contact']} ov {r.get('overhead')} "
          f"g {r.get('gamma')} {r.get('inband_member')} cm {r.get('contact_poses_member')} {time.time() - t0:.0f}s", flush=True)
    return r


CMA_BOX = dict(az=(-30, 90), el=(20, 85), a1=(60, 120), psi3=(-60, 60), s3=(170, 270), psi_b=(-90, 90), s_a=(25, 80), q=(0.85, 1.0))


def cma(B, x0, n_eval, base, sigma0=0.2, lam=8, seed=0, tag="cma"):
    """compact CMA-ES on the box-normalised CMA_BOX parameters (a2 = 180 - a1 unless base fixes da); every evaluation
    appended to the sweep file"""
    keys = list(CMA_BOX); lo = np.array([CMA_BOX[k][0] for k in keys], float); hi = np.array([CMA_BOX[k][1] for k in keys], float)
    def to_p(z):
        v = lo + np.clip(z, 0, 1) * (hi - lo); pp = dict(PARAMS, **base, **{k: round(float(x), 2) for k, x in zip(keys, v)})
        pp["a2"] = round(180.0 - pp["a1"] + base.get("da", 0.0), 2); pp.pop("da", None); return pp
    rng = np.random.default_rng(seed); n = len(keys); m = (np.array([x0.get(k, (CMA_BOX[k][0] + CMA_BOX[k][1]) / 2) for k in keys]) - lo) / (hi - lo)
    mu = lam // 2; w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5); c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff)); ds = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); sg = sigma0; chi = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n)); done = 0; best = None
    while done < n_eval:
        Dg, Bm = np.linalg.eigh(C); Dg = np.sqrt(np.maximum(Dg, 1e-20)); Z = rng.standard_normal((lam, n)); Y = Z @ np.diag(Dg) @ Bm.T
        X = m + sg * Y; f = []
        for x in X:
            pp = to_p(x)
            try: r = run(B, pp, tag=tag)
            except Exception as ex: print("ERR", ex, flush=True); r = dict(gap=400.0)
            g = r["gap"] + 50 * float(np.sum(np.abs(x - np.clip(x, 0, 1))))
            f.append(g); done += 1
            if best is None or r["gap"] < best[0]: best = (r["gap"], pp)
        idx = np.argsort(f); yw = (Y[idx[:mu]] * w[:, None]).sum(0); m = m + sg * yw
        Ci = Bm @ np.diag(1 / Dg) @ Bm.T; ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (Ci @ yw)
        hs = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * done / lam)) < (1.4 + 2 / (n + 1)) * chi
        pc = (1 - cc) * pc + hs * math.sqrt(cc * (2 - cc) * mueff) * yw
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hs) * cc * (2 - cc) * C) + cmu * (Y[idx[:mu]].T * w) @ Y[idx[:mu]]
        sg *= math.exp((cs / ds) * (np.linalg.norm(ps) / chi - 1)); print(f"  gen: best {best[0]} sigma {sg:.3f}", flush=True)
    return best


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "eval"
    B = K.bench(110, 360) if "--big" in a else K.bench(60, 160)
    if mode == "eval":
        p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}))
        evaluate(B, p, verbose=True)
    elif mode == "run":                                   # evaluate + append to the sweep file: run '[{...}, {...}]' tag
        for pp in json.loads(a[1]):
            try: run(B, dict(PARAMS, **pp), tag=a[2] if len(a) > 2 else "")
            except Exception as ex: print("ERR", pp, ex, flush=True)
    elif mode == "wear":                                  # wear '{params}': fit on Bench(60,160), frozen on Bench(110,360)
        p = dict(PARAMS, **json.loads(a[1])); Bb = K.bench(110, 360); t0 = time.time(); r = wear(B, Bb, p)
        out = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "mode", "overhead", "taken_ws", "contact_poses",
                                     "contact_poses_member", "inband_member", "min_margin_taken", "near1_gap", "min_metal", "flips")}
        out["secs"] = round(time.time() - t0); print("WEAR", json.dumps(out), flush=True)
    elif mode == "cma":                                   # cma '{x0}' n_eval '{base}' seed sigma0
        best = cma(B, json.loads(a[1]), int(a[2]), json.loads(a[3]) if len(a) > 3 else {}, seed=int(a[4]) if len(a) > 4 else 0,
                   sigma0=float(a[5]) if len(a) > 5 else 0.2, tag=a[6] if len(a) > 6 else "cma")
        print("BEST", best)
