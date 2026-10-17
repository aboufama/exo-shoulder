"""acromion-pointer-arm-ctrack: a 2-hub gimbal at the shoulder (J1 scapula-fixed, J2 on the humeral 'equator') + the
humeral twist as a carriage on an ARM-FIXED, skin-shaped C-track (the third active coordinate = the carriage's place on
the track). Shared kit (tools/concept_kit.py, docs/concepts/KIT.md) + one add-on: the carriage rides the fitted track,
so its skin face sits at the TRACK's height under it in every pose (a per-pose height the kit's members do not have) -
the carriage samples are added to the kit's report after the kit's fit (`evaluate` below), contact- and band-checked
like every other sample.

Kinematics (bench frame, GH = origin):
  d   = the humeral axis (GH -> elbow, body_pose humerus frame E), a1 = F.S(bvec(az, el)) (J1, scapula-fixed)
  u2  = K.closure(a1, d, al12, al23, sigma)  (J2; 90/90 = the orthogonal gimbal, u2 = sigma unit(a1 x d))
  pointing frame (L2): r_ref = unit(u2 - (u2.d) d), t_ref = d x r_ref; the carriage sits at angle thc about d from r_ref
  th_arm = its angle on the arm (0 lateral, +90 posterior) = q3; taken only if the carriage (+-car mm) stays on the track
  [tc - tw/2, tc + tw/2] (arm frame).
Members: hub1 (O20 on a1), link1 (a1 -> u2), hub2 (O20 on u2), yoke (L2: u2 -> the yoke tip over the carriage at
station s_t, passes over the track + carriage + 1 mm by construction), track (arm-fixed 8 x 3 mm, skin-fitted per sample
= the spec's 'shaped to the arm's own skin'; it is the arm end, BOTTOM cut and merged into it), carriage (24 x 16 mm skin
face at the track's height under it, per pose). The carriage <-> yoke-tip column is the spec's passive radial slide
(+ swivel); its travel = the spread of (yoke tip - carriage top) over the taken poses, reported (rail stands travel +
block above the carriage, outward).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acromion-pointer-arm-ctrack.py [eval|kin|sweep N|cma N]
"""
import itertools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "acromion-pointer-arm-ctrack"
NAME = "Acromion gimbal + arm-fixed skin-shaped C-track (2 DOF at the shoulder, axial rotation lower on the arm)"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
# arm frame (body_pose humerus frame, spec 'COMMON'): E = GH -> elbow, LAT lateral, POST = E x LAT posterior
E = K.unit(np.array([-0.02273058, -0.98614607, 0.16431446]))
LAT = np.array([0.004, 0.164, 0.986]); LAT = K.unit(LAT - (LAT @ E) * E); POST = np.cross(E, LAT)
PARAMS = dict(az=0.0, el=0.0, sigma=1, al12=90.0, al23=90.0, s_t=90.0, R0=50.0, tc=-10.0, tw=200.0, thc=0.0,
              car=24.0, gap_c=5.0, margin=K.FOLD_MARGIN, width=12.0, t_link=3.0, q=0.9, qt=0.7)


def arm_dirs(s, th_deg, R0):
    """arm-frame GH-ray directions through s E + R0 n(th) (n(th) = cos th LAT + sin th POST); s, th broadcast"""
    s = np.asarray(s, float); t = np.radians(np.asarray(th_deg, float))
    P = s[..., None] * E + R0 * (np.cos(t)[..., None] * LAT + np.sin(t)[..., None] * POST)
    return K.unit(P)


def kin(F, p):
    d = F.H(E); a1 = F.S(K.bvec(p["az"], p["el"]))
    u2, ok, margin = K.closure(a1, d, p["al12"], p["al23"], p["sigma"], margin_deg=p["margin"])
    rr = K.unit(u2 - (u2 * d).sum(-1, keepdims=True) * d); tt = np.cross(d, rr)
    c = math.cos(math.radians(p["thc"])) * rr + math.sin(math.radians(p["thc"])) * tt
    th_arm = K.axis_angle(d, F.H(LAT), c)
    return d, a1, u2, c, th_arm, ok, margin


def track_grid(p):
    """arm-frame track samples: rows across (8 mm, 2 mm step) x columns along the arc (2 mm at R0)"""
    dth = math.degrees(2.0 / p["R0"]); th = np.arange(p["tc"] - p["tw"] / 2, p["tc"] + p["tw"] / 2 + 1e-6, dth)
    ds = np.arange(-4.0, 4.0 + 1e-6, 2.0)
    S, T = np.meshgrid(p["s_t"] + ds, th, indexing="ij")
    return S, T, th


def build(B, F, p):
    d, a1, u2, c, th_arm, ok, margin = kin(F, p)
    half_car = math.degrees(p["car"] / 2 / p["R0"])
    lo, hi = p["tc"] - p["tw"] / 2 + half_car, p["tc"] + p["tw"] / 2 - half_car
    ok = ok & (th_arm >= lo) & (th_arm <= hi)
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), u2), K.axis_angle(u2, a1, d), th_arm], -1)
    yt = K.unit(p["s_t"] * d + p["R0"] * c)                  # yoke tip direction (pointing frame)
    S, T, _ = track_grid(p); Dt = arm_dirs(S.ravel(), T.ravel(), p["R0"])
    rref = float(np.hypot(p["s_t"], p["R0"]))
    track = K.Member("track", F.H(Dt), kind="free", t=3.0, width=8.0, joints=("J3",), cell=4.0, r_ref=rref, q=p["qt"])
    # the track is ARM-fixed: its underside is the qt-quantile of its own GH-ray requirement over the fit poses (the arm's
    # skin; a pose where the torso reaches the track is a CONTACT pose, not a reason to lift an arm-fixed part)
    w, t = p["width"], p["t_link"]
    members = [K.hub_member("hub1", a1, "J1"), K.hub_member("hub2", u2, "J2"),
               K.strap_member("link1", a1, u2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),
               K.strap_member("yoke", u2, yt, ("J2",), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                              over=[("track", p["gap_c"]), ("link1", 1.0)]),
               track]
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=a1, J2=u2, J3=d), hubless=("J3",),
                   info=dict(residual_deg=round(float(K.closure_residual(a1, d, u2, p["al12"], p["al23"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def carriage_points(p, F, prof_track, th_arm, idx):
    """carriage skin face (24 along the track x 16 along the arm, 2 mm) at the track's radial height under it"""
    S, T, th = track_grid(p); Dt = arm_dirs(S.ravel(), T.ravel(), p["R0"])
    Pa = Dt * prof_track[:, None]                             # arm-frame track points
    sA = Pa @ E; Rad = np.linalg.norm(Pa - sA[:, None] * E, axis=1)
    Rcol = Rad.reshape(S.shape).max(0); scol = sA.reshape(S.shape).mean(0)   # per column: radial height, station
    off = np.arange(-p["car"] / 2, p["car"] / 2 + 1e-6, 2.0) / p["R0"] * 180 / math.pi; ds = np.arange(-8.0, 8.0 + 1e-6, 2.0)
    out = []
    for i in idx:
        tq = th_arm[i] + off; R = np.interp(tq, th, Rcol); s = np.interp(tq, th, scol)
        tr = np.radians(tq); n = np.cos(tr)[:, None] * LAT + np.sin(tr)[:, None] * POST
        P = (s[:, None, None] + ds[None, :, None]) * E + R[:, None, None] * n[:, None, :]
        out.append(P.reshape(-1, 3) @ F.RH[i].T)
    return np.stack(out) if out else np.zeros((0, len(off) * len(ds), 3))


def evaluate(B, p, verbose=False):
    rep = K.evaluate(B, build, p)
    L = B._kit_last; ch, prof, pts, take = L["chain"], L["prof"], L["pts"], L["take"]
    F = B._kitF; _, _, _, _, th_arm, _, _ = kin(F, p); Pi = np.nonzero(take)[0]
    Cp = carriage_points(p, F, prof["track"], th_arm, Pi)
    dc = K.dist_many(B, np.repeat(Pi, Cp.shape[1]), Cp.reshape(-1, 3)).reshape(len(Pi), -1) if len(Pi) else np.zeros((0, 0))
    allk = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    dk = K.dist_many(B, np.repeat(Pi, allk.shape[1]), allk.reshape(-1, 3)).reshape(len(Pi), allk.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = np.r_[dk[j], dc[j]]
    r = B.report()
    clip = np.array([B.kind[i] == "clip" for i in Pi], bool); good = np.r_[[min(dk[j].min(), dc[j].min()) >= 0 for j in range(len(Pi))]].astype(bool) if len(Pi) else np.zeros(0, bool)
    per = dict(rep["inband_member"])
    o = 0
    for m in ch.members:
        s = pts[m.name].shape[1]; dm = dk[clip & good, o:o + s]; o += s
        per[m.name] = round(float(((dm >= 2) & (dm <= 14)).mean()), 4) if dm.size else 0.0
    cmem = {}; o = 0
    for m in ch.members:
        s_ = pts[m.name].shape[1]; cmem[m.name] = round(float((dk[:, o:o + s_].min(1) < 0).mean()), 3) if len(Pi) else 0.0; o += s_
    cmem["carriage"] = round(float((dc.min(1) < 0).mean()), 3) if len(Pi) else 0.0
    hmem = {m.name: round(float(np.median(prof[m.name])), 1) for m in ch.members}
    dm = dc[clip & good]; per["carriage"] = round(float(((dm >= 2) & (dm <= 14)).mean()), 4) if dm.size else 0.0
    # radial slide: yoke tip underside (last strap row, centre) vs the carriage top under it
    yk = ch.members[3]; ns, nc = yk.grid; tip = prof["yoke"].reshape(ns, nc)[-1].max()
    ctop = np.linalg.norm(Cp, axis=-1).mean(1) + 4.0 if len(Pi) else np.zeros(0)   # carriage top (GH ray metric)
    col = tip - ctop
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    ws = np.array(B.kind) == "ws"; ov = np.array([B.poses[i]["elev"] >= 140 for i in range(len(B.poses))])
    rep.update({k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")})
    rep.update(inband_member=per, contact_member=cmem, rho_member=hmem, slide_travel=round(float(col.max() - col.min()), 1) if len(col) else None,
               slide_min_col=round(float(col.min()), 1) if len(col) else None,
               overhead=f"{int((taken & ws & ov).sum())}/{int((ws & ov).sum())}",
               min_metal=round(float(min(dk.min(), dc.min())), 2) if len(Pi) else None,
               near1=round(float(np.mean([np.min(B.res[i]) < 1 for i in Pi])) if len(Pi) else 0, 4))
    if verbose: print({k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "inband_member", "contact_member", "rho_member", "slide_travel", "slide_min_col", "overhead", "min_metal", "closure", "flips", "collide", "min_margin", "honest", "audit")})
    return rep


def log_sweep(entry):
    rows = json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) else []
    entry = dict(k=len(rows), t=K.now(), **entry); rows.append(entry)
    json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON); return entry


def run(B, p, tag=""):
    t0 = time.time(); r = evaluate(B, p)
    e = log_sweep(dict(params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")}, closure=r["closure"],
                       honest=r["honest"], kmode=r["kmode"], overhead=r["overhead"], slide_travel=r["slide_travel"],
                       inband_member=r["inband_member"], tag=tag))
    print(f"[{e['k']}] {tag} gap {r['gap']} reach {r['reach']} follow {r['follow']} ib14 {r['inband14']} c {r['contact']} "
          f"ov {r['overhead']} slide {r['slide_travel']} {r['inband_member']} {time.time() - t0:.1f}s", flush=True)
    return r


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "eval"
    nb = (110, 360) if "--big" in a else (60, 160)
    B = K.bench(*nb)
    if mode == "eval":
        p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}))
        evaluate(B, p, verbose=True)
