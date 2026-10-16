"""spine-parked-j2-3r: zero-passive spherical 3R at the leader's seats, J2 parked over the posterior acromion / scapular
spine, slim O15 J2 / J3 hubs (catalogue id spine-parked-j2-3r, family "spherical 3R").

Chain: scapula handler -> base -> J1 (O20 hub, MR117-2RS pair, active R, axis through GH) -> link 1 (12 x 3 Ti) -> J2
(active R through GH, branch sigma -1, slim O15 hub) -> link 2 (12 x 3 Ti, over link 1 and the neck) -> J3 (active R
through GH, slim O15 hub) -> member 3 = hub 3's arm-end plate + the K7 14 x 6 neck rigid to BOTTOM's bar -> cuff.
Passive translations 0, passive rotations 0, cuff slides 0, liner compliance claimed 0 mm: on the bench the arm rotates
about a fixed GH in the scapula frame, so the spherical chain closes exactly (residual 0). R10 (GH translation) is off
this bench and is judged separately (catalogue: cuff liner, one RSR3M along the humerus, or the base follower slide).

Kinematics and members = docs/concepts/models/_template.py build() (= fold-sph3r's), with three changes:
  * per-hub radius: rad1 / rad2 / rad3 (mm). 10 = the O20 v5 hub. 7.5 = the slim O15 hub: the SAME MR117-2RS pair
    (7 x 11 x 3) in a 2.0 mm Ti wall (bore 11 H7 + 2 x 2), same 12.25 mm stack. The kit's audit asks for O20 discs;
    a slim hub is accepted here only as a DECLARED component (SLIM below, hand calc in docs/concepts/spine-parked-j2-3r.md):
    its sampled disc must cover >= 75 % of ITS declared disc and reach >= rad - 0.5 - otherwise the problem stands
    and the report is not honest. Crowns, walls and K6 use the declared radius.
  * the crown / wall skin check, near-touch and overhead split of fold-sph3r (lessons d, e): every hub is a solid
    cylinder F .. F + 12.25; a taken pose with a crown or wall sample inside the skin becomes a contact pose.
  * `vm=1`: a kit emulation of osn's VModel spherical reference conventions (8 mm straps) to settle the kit-vs-VModel
    split (docs/concepts/spine-parked-j2-3r.md "The split").

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/spine-parked-j2-3r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/spine-parked-j2-3r.py frozen '<json params>' --out R.json
"""
import functools, json, math, os, re, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "spine-parked-j2-3r"
NAME = "Zero-passive spherical 3R at the leader's seats: J2 parked over the posterior acromion, slim O15 J2/J3 hubs"
# defaults = the leader's k4216 seats as a spherical chain (osn Design at b1 = b2 = 0, b3 0.2282: u1 = bvec(95.86, 65.21),
# a1 = angle(u1, u2) 40.34, a2 = angle(u2, u3) 74.07, u3 = wdir(84.80, -11.37) in the band humerus frame, branch -1)
PARAMS = dict(az=95.8565, el=65.2093, a1=40.3436, a2=74.0692, wd=84.7998, wa=-11.3702, sigma=-1, margin=K.FOLD_MARGIN,
              width=12.0, t_link=3.0, q=0.98, rad1=10.0, rad2=10.0, rad3=10.0, vm=0, end_extra=0.0,
              near=0)   # near 1: the report's gap / reach / follow / in-band / contact count metal < 1 mm as contact (lesson d)
# declared hub components (radius mm -> component); a hub radius not in here must pass the kit's O20 audit as is
SLIM = {10.0: "v5 O20 hub: MR117-2RS pair, 12.25 mm stack (docs/HARDWARE.md)",
        8.5: "O17 hub: MR117-2RS pair in a 2.75 mm Ti wall (conservative slim), 12.25 mm stack",
        7.5: "O15 slim hub: MR117-2RS pair (O11) in a 2.0 mm Ti wall, 12.25 mm stack (hand calc in the doc)"}
ELEV_OVER = 140.0
CROWN_LEVELS = (2.0, 4.0, 6.0, 8.0, 10.0, 12.25)


def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"]))                        # J1 fixed in the scapula
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))                       # J3 fixed in the humerus (band frame)
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])   # K1 (J2), fold margin
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    r1, r2, r3 = float(p["rad1"]), float(p["rad2"]), float(p["rad3"])
    hubs = [K.hub_member("hub1", p1, "J1", rad=r1), K.hub_member("hub2", p2, "J2", rad=r2), K.hub_member("hub3", p3, "J3", rad=r3)]
    w = 8.0 if p.get("vm") else p["width"]; t = p["t_link"]
    # strap end zone held at its hub's level: HUB_R + 2 = 12 mm for EVERY hub (also the slim ones): K6 exempts joint
    # partners within HUB_R + 2 of the shared joint whatever the hub size, so a shorter ramp would leave link 1 / link 2
    # unchecked against each other between rad + 2 and 12 mm (an optimistic hole, measured: see the doc)
    end = lambda r: K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    links = [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end(max(r1, r2))),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0)], end_mm=end(max(r2, r3))),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             hub_rad=dict(J1=r1, J2=r2, J3=r3)))


def crown_points(m, rho, rad):
    """(P, k, 3) crown disc + cylinder wall samples of a flat hub member fitted at level rho[0] (F), radius rad"""
    F0 = float(rho[0]); k = m.K[:, None, :]
    crown = (F0 + K.CROWN) * k + m.xy[None, :, :1] * m.A[:, None, :] + m.xy[None, :, 1:] * m.Bv[:, None, :]
    n = max(16, int(round(2 * math.pi * rad / 2.0))); ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    c, s = rad * np.cos(ang), rad * np.sin(ang)
    wall = [(F0 + h) * k + c[None, :, None] * m.A[:, None, :] + s[None, :, None] * m.Bv[:, None, :] for h in CROWN_LEVELS]
    return np.concatenate([crown] + wall, 1)


def _taken(B, j): return B.res[j] is not None and float(np.min(B.res[j])) >= 0.0


def declared_audit(r, p):
    """drop the kit's 'smaller than O20' problem for a hub whose radius is a DECLARED component (SLIM) and whose
    sampled disc covers >= 75 % of its declared disc and reaches >= rad - 0.5; recompute `honest`"""
    keep, decl = [], {}
    for msg in r.get("audit") or []:
        m = re.match(r"(hub\d): hub of (J\d) smaller than O20 \(covers ([\d.]+) of the disc, reaches ([\d.]+) mm\)", msg)
        if m:
            rad = float(p["rad" + m.group(2)[1]]); cov = float(m.group(3)) * (K.HUB_R / rad) ** 2; reach = float(m.group(4))
            if rad in SLIM and cov >= 0.75 and reach >= rad - 0.5:
                decl[m.group(2)] = dict(rad=rad, component=SLIM[rad], cover=round(cov, 3), reach=reach); continue
        keep.append(msg)
    r["audit"] = keep; r["declared_hubs"] = decl
    c = r.get("checks") or {}
    r["honest"] = c.get("mode") == "march" and c.get("cont") in (True, "frames") and bool(c.get("collide")) and not keep
    return r


def extras(B, r, p):
    """crown / wall check (poses with a crown or wall inside the skin -> contact), near-touch, overhead >= 140"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]; rad = {"hub1": p["rad1"], "hub2": p["rad2"], "hub3": p["rad3"]}
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [crown_points(m, prof[m.name], rad[m.name])[Pi] for m in hubs]
        C = np.concatenate(parts, 1)
        dc = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        cmin[Pi] = dc.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): cwho[int(j)] = hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)].name
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report()
    allmin = sorted((min(float(np.min(B.res[j])), cmin[j]), j) for j in range(len(B.res)) if _taken(B, j))
    save = list(B.res)
    for d, j in allmin:
        if d < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    el = np.array([q["elev"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind]); cl = ~ws
    ov = np.nonzero(el >= ELEV_OVER)[0]; ovw = ov[ws[ov]]; ovc = ov[cl[ov]]
    tk = [j for j in ov if _taken(B, j)]; d = np.concatenate([B.res[j] for j in tk]) if tk else np.zeros(0)
    over = dict(n_ws=int(len(ovw)), reach=round(float(np.mean([_taken(B, j) for j in ovw])), 4) if len(ovw) else None,
                n_clip=int(len(ovc)), follow=round(float(np.mean([_taken(B, j) for j in ovc])), 4) if len(ovc) else None,
                n_taken=len(tk), inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None)
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): r[k] = rr[k]
    r.update(crown_contact_poses=int(len(bad)), crown_min=round(float(np.min(cmin[np.isfinite(cmin)])), 2) if np.isfinite(cmin).any() else None,
             min_metal_skin=round(float(allmin[0][0]), 2) if allmin else None,
             near_low=[dict(mm=round(float(dd), 2), i=int(j), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"],
                            axial=B.poses[j]["axial"], crown=cwho.get(int(j)) if cmin[j] <= float(np.min(B.res[j])) else "face")
                       for dd, j in allmin[:5]],
             gap_near1=rn["gap"], near1=dict(reach=rn["reach"], follow=rn["follow"], inband14=rn["inband14"], contact=rn["contact"]),
             overhead=over)
    return r


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"])))
    p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))   # never shorter than the K6 exempt zone
    for k in ("rad2", "rad3"):                                  # CMA steps snap to the declared components
        p[k] = K.hub_rad(p[k], SLIM)                           # O20 only (user 2026-10-16) unless CB_ALLOW_SLIM=1
    r = K.evaluate(B, build, p); r = declared_audit(r, p); r = extras(B, r, p)
    if p.get("near"):                                           # lesson (d) as the objective: metal < 1 mm = contact
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if _jsonable(v)}


def _jsonable(v):
    try:
        json.dumps(v); return True
    except (TypeError, ValueError):
        return False


def lab(B, i): return f"#{i:3d} {B.kind[i]:4s} {B.clip[i][:20]:20s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"


def redteam(B, p, r):
    L = B._kit_last; ch, prof, pts, take, ok, hit = L["chain"], L["prof"], L["pts"], L["take"], L["ok"], L["hit"]
    Pi = np.nonzero(take)[0]; el = np.array([q["elev"] for q in B.poses]); pl = np.array([q["plane"] for q in B.poses])
    print("-- per part: in band (clip), level, median / p90 distance over taken poses --")
    for m in ch.members:
        X = pts[m.name][Pi]; d = K.dist_many(B, np.repeat(Pi, X.shape[1]), X.reshape(-1, 3)).reshape(len(Pi), -1)
        lvl = f"F {prof[m.name][0]:.1f}" if m.kind == "flat" else f"level med {np.median(prof[m.name]):.1f} max {prof[m.name].max():.1f}"
        print(f"  {m.name:6s} ib14 {r['inband_member'].get(m.name)} {lvl}; dist median {np.median(d):.1f} p90 {np.percentile(d, 90):.1f}")
    # hub fitted level: which fit poses set it (the q-dropped ones are the contact poses)
    fit = np.nonzero(ok)[0]
    for m in [m for m in ch.members if m.kind == "flat"]:
        n = len(m.xy); Dm = np.broadcast_to(m.K[fit][:, None, :], (len(fit), n, 3))
        Om = m.xy[None, :, :1] * m.A[fit][:, None, :] + m.xy[None, :, 1:] * m.Bv[fit][:, None, :]
        R = K.requirement(B, np.repeat(fit, n), Dm.reshape(-1, 3), O=Om.reshape(-1, 3)).reshape(len(fit), n)
        R = np.where(np.isfinite(R), R, 400.0).max(1); o = np.argsort(-R)[:5]
        print(f"  {m.name} level set by (requirement mm): " + "; ".join(f"{R[a]:.1f} {lab(B, int(fit[a]))}" for a in o))
    print("-- poses not taken --")
    nt = [i for i in range(len(B.res)) if not _taken(B, i)]
    why = lambda i: "fold/K2" if not ok[i] else ("K6 parts" if hit[i] else "contact")
    for i in nt[:60]: print(f"  {why(i):8s} {lab(B, i)}  min {float(np.min(B.res[i])) if B.res[i] is not None else float('nan'):.1f}")
    print(f"  ... {len(nt)} not taken: fold/K2 {sum(not ok[i] for i in nt)}, K6 {sum(bool(ok[i] and hit[i]) for i in nt)}, contact {sum(bool(ok[i] and not hit[i]) for i in nt)}")
    ws = np.array([k == "ws" for k in B.kind]); nws = [i for i in nt if ws[i]]
    print(f"  reach loss over {int(ws.sum())} ws poses: noclose/fold {sum(not ok[i] for i in nws)}, K6 {sum(bool(ok[i] and hit[i]) for i in nws)}, contact {sum(bool(ok[i] and not hit[i]) for i in nws)}")
    groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= ELEV_OVER)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                  behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
    print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 --")
    for g, ii in groups.items():
        ii = list(ii); tk = [i for i in ii if _taken(B, i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
        print(f"  {g:9s} {len(tk)}/{len(ii)}  median {float(np.nanmedian(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}"
              f"  not taken: {[(int(i), why(i)) for i in ii if not _taken(B, i)][:8]}")


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every underside / hub level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if _jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); r = declared_audit(r, pf); r = extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead", "inband_member")}, flush=True)
    if "--redteam" in sys.argv: redteam(Bb, pf, r)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), "margin", r.get("min_margin"), "declared", r.get("declared_hubs"))
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("near", r["near_low"])
    if mode == "redteam": redteam(B, p, r)
