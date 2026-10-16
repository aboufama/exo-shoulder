"""arm-parked-knee-4r: spherical 4R (all four axes through GH) whose 1-D self-motion (the spare) is set quasi-statically
by a torsion spring on the arm-end joint J4 (it parks the knee hub J3 on arm-fixed skin) and by the J2 fold-margin stops
(catalogue id arm-parked-knee-4r, family "spherical 4R, spare set by a spring and stops").

Chain: scapula handler -> base -> J1 (O20 v5 hub, axis u1 = bvec(az, el) in the scapula frame) -> link 1 (12 x 3 Ti, arc
a1) -> J2 (O20, hard stops: angle(J1, J3) inside the fold window +- margin) -> link 2 (12 x 3 Ti, arc a2, over link 1) ->
J3 = the knee (O20) -> link 3 (12 x 3 Ti, arc a3, over link 1 and the neck) -> J4 (O20 with the torsion spring wrapped
round its boss; axis u4 = wdir(wd, wa) in the band humerus frame) -> arm-end plate + K7 neck rigid to BOTTOM -> cuff.
Active DOF 4 (inside the user's 4-joint cap; MVP1: four bearing pairs, all unpowered), passive translations 0, passive
rotations 0, 1 spring, 2 stops (a dowel in a slot of link 2's end plate).

The spare (closed form, pose by pose): with u1 and u4 known, the knee p3 lies on the a3 cone about u4 at azimuth d
(measured about u4 from the u1 side); the chain closes iff angle(u1, p3) is inside [lo, hi] = [|a1 - a2| + m', min(a1 +
a2, 360 - a1 - a2) - m'] (m' = margin + 0.5): cos angle(u1, p3) = cos a3 cos th + sin a3 sin th cos d gives the feasible
|d| in [dlo, dhi]. The spring's rest azimuth dp is arm-fixed (pz4 about u4 in the band humerus frame). Centred spring
(side 0): d = sign(dp) clip(|dp|, dlo, dhi) - the energy minimum (k/2)(d - dp)^2 under the stops; the stop is pushed by
construction (the unconstrained minimum is outside the window). One-sided (side +-1): link 3 rests on a hard stop at dp
and swings only toward `side`, to the nearest feasible entry. p2 = K.closure(u1, p3, a1, a2, s1, margin).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/arm-parked-knee-4r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/arm-parked-knee-4r.py frozen '<json params>' --out R.json

O20 at every joint (user 2026-10-16: "Keep O20 only"); margin 5 deg default (user ruling for MVP1), 10 reported too.
The ideation prototype ran O15 at J2-J4 (rad 7.5); its 19.18 fast / 22.36 frozen do NOT stand under the O20 rule.
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("spm_ref", os.path.join(REPO, "docs", "concepts", "models", "spine-parked-j2-3r.py"))
SPM = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SPM)

ID = "arm-parked-knee-4r"
NAME = "Arm-parked knee 4R: J4 torsion spring parks the knee hub on arm skin; J2 fold-margin stops"
D2R = math.pi / 180
# defaults = the ideation k-A seats (az .. end_extra), hubs O20 everywhere, margin 5
PARAMS = dict(az=102.7408, el=67.9854, wd=81.3566, wa=-14.6101, a1=37.6, a2=60.0, a3=22.307, pz4=98.4478, s1=-1, side=0,
              lim4=400.0, margin=5.0, inner=0.5, width=12.0, t_link=3.0, q=0.9681, rad1=10.0, rad2=10.0, rad3=10.0,
              rad4=10.0, end_extra=1.02, near=0)
REPORT_KEYS = ("over_reach", "overhead", "gap_near1", "min_metal_skin", "crown_contact_poses", "moved_share", "defl_p95",
               "defl_max", "stop_share", "gap_plain")
ELEV_OVER = 140.0


def rot(k, v, ang):  # rotate v about unit k by ang rad (arrays)
    c, s = np.cos(ang)[..., None], np.sin(ang)[..., None]
    return v * c + np.cross(k, v) * s + k * (k * v).sum(-1, keepdims=True) * (1 - c)


def spare(F, p, u1, u4):
    """the quasi-static spare: knee p3 on the a3 cone about u4, set by the J4 spring + J2 stops. -> p3, feas, defl, info"""
    a1, a2, a3 = p["a1"], p["a2"], p["a3"]; mi = p["margin"] + p["inner"]
    th = np.degrees(np.arccos(np.clip((u1 * u4).sum(-1), -1, 1)))
    lo1, hi1 = abs(a1 - a2) + mi, min(a1 + a2, 360 - a1 - a2) - mi
    u4s = K.wdir(p["wd"], p["wa"]); ref = np.array([0.0, -1.0, 0.0]) if abs(u4s[1]) < 0.9 else np.array([0.0, 0.0, -1.0])
    e1 = K.unit(np.cross(u4s, ref)); e2 = np.cross(u4s, e1)
    pp = F.HG(math.cos(a3 * D2R) * u4s + math.sin(a3 * D2R) * (math.cos(p["pz4"] * D2R) * e1 + math.sin(p["pz4"] * D2R) * e2))
    dp = np.radians(K.axis_angle(u4, u1, pp))                 # spring rest azimuth of the knee about u4 (from the u1 side)
    sa, ca = math.sin(a3 * D2R), math.cos(a3 * D2R); st, ct = np.sin(th * D2R), np.cos(th * D2R); den = sa * st + 1e-12
    cmin = (np.cos(hi1 * D2R) - ca * ct) / den; cmax = (np.cos(lo1 * D2R) - ca * ct) / den
    dlo = np.arccos(np.clip(cmax, -1, 1)); dhi = np.arccos(np.clip(cmin, -1, 1))
    feas = (cmax >= -1) & (cmin <= 1) & (dlo <= dhi)
    side = int(p.get("side", 0))
    if side == 0:
        ad = np.clip(np.abs(dp), dlo, dhi); dsel = np.where(dp >= 0, 1.0, -1.0) * ad; defl = np.degrees(np.abs(ad - np.abs(dp)))
        stop = np.abs(ad - np.abs(dp)) > 1e-6
    else:                                   # J4 preloaded against a one-sided stop: link 3 only swings toward `side`
        inside = (np.abs(dp) >= dlo) & (np.abs(dp) <= dhi)
        ent = np.stack([dlo, -dhi], -1) if side > 0 else np.stack([dhi, -dlo], -1)
        tt = ((ent - dp[:, None]) * side) % (2 * np.pi); t = np.where(inside, 0.0, tt.min(-1))
        dsel = dp + side * t; defl = np.degrees(t); stop = t > 1e-6
    w = K.unit(u1 - (u1 * u4).sum(-1, keepdims=True) * u4); p3 = rot(u4, ca * u4 + sa * w, dsel)
    return p3, feas, defl, stop


def build(B, F, p):
    u1 = F.S(K.bvec(p["az"], p["el"])); u4 = F.HG(K.wdir(p["wd"], p["wa"]))
    p3, feas, defl, stop = spare(F, p, u1, u4)
    p2, ok1, mar1 = K.closure(u1, p3, p["a1"], p["a2"], p["s1"], margin_deg=p["margin"])
    ok = feas & ok1 & (defl <= p.get("lim4", 400.0))
    q = np.stack([K.axis_angle(u1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, u1, p3), K.axis_angle(p3, p2, u4),
                  K.axis_angle(u4, F.HG([0.0, -1, 0]), p3)], -1)
    fo = feas & ok1
    info = dict(moved_share=round(float(stop[ok].mean()), 4) if ok.any() else None,
                defl_p95=round(float(np.percentile(defl[fo], 95)), 2) if fo.any() else None,
                defl_max=round(float(defl[fo].max()), 2) if fo.any() else None,
                min_margin=round(float(mar1[ok].min()), 2) if ok.any() else None,
                residual_deg=round(float(K.closure_residual(u1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None)
    r = [float(p["rad%d" % i]) for i in (1, 2, 3, 4)]
    hubs = [K.hub_member("hub1", u1, "J1", rad=r[0]), K.hub_member("hub2", p2, "J2", rad=r[1]),
            K.hub_member("hub3", p3, "J3", rad=r[2]), K.hub_member("hub4", u4, "J4", rad=r[3])]
    w = p["width"]; t = p["t_link"]; end = K.HUB_R + 2.0 + p["end_extra"]
    links = [K.strap_member("link1", u1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", 0.0)), over=[("link1", 1.0)], end_mm=end),
             K.strap_member("link3", p3, u4, ("J3", "J4"), width=w, t=t, ramp_to=(("hub3", K.STACK), ("hub4", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0)], end_mm=end),
             K.neck_member(F, u4, joints=("J4",), ramps=(("hub4", 0.0), (None, 0)))]
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=u1, J2=p2, J3=p3, J4=u4), info=info)


def extras(B, r, p):
    """SPM.extras (crowns + walls of every hub, near-touch, overhead >= 140) with the four hubs of this chain"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]; rad = {"hub%d" % i: p["rad%d" % i] for i in (1, 2, 3, 4)}
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [SPM.crown_points(m, prof[m.name], rad[m.name])[Pi] for m in hubs]
        C = np.concatenate(parts, 1)
        dc = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        cmin[Pi] = dc.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): cwho[int(j)] = hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)].name
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report()
    _taken = SPM._taken
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
             overhead=over, over_reach=over["reach"])
    ch_info = getattr(ch, "info", None) or {}
    for k in ("moved_share", "defl_p95", "defl_max", "min_margin", "residual_deg"):
        if k in ch_info: r[k] = ch_info[k]
    r["stop_share"] = r.get("moved_share")
    return r


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"])))
    p["s1"] = 1 if float(p["s1"]) >= 0 else -1
    p["side"] = int(round(float(p.get("side", 0)))); p["side"] = max(-1, min(1, p["side"]))
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))   # never shorter than the K6 exempt zone
    for k in ("a1", "a2", "a3"): p[k] = min(110.0, max(12.0, float(p[k])))
    if not p.get("slim_control"):                               # O20 only (user ruling); slim_control 1 = the ideation's O15
        for k in ("rad1", "rad2", "rad3", "rad4"): p[k] = 10.0  # control for attribution, never a claim
    r = K.evaluate(B, build, p); r = SPM.declared_audit(r, p); r = extras(B, r, p)
    if p.get("near"):                                           # lesson (d) as the objective: metal < 1 mm = contact
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SPM._jsonable(v)}


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
    keep = lambda r: {k: v for k, v in r.items() if SPM._jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest", "gap_near1", "over_reach")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); r = SPM.declared_audit(r, pf); r = extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                    "min_metal_skin", "overhead", "inband_member", "moved_share", "defl_p95", "defl_max")}, flush=True)
    if "--redteam" in sys.argv: SPM.redteam(Bb, pf, r)
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
    print("per member", r["inband_member"], "mass", r.get("mass_g"), "res", r.get("residual_deg"), "margin", r.get("min_margin"))
    print("spare: stop share", r.get("moved_share"), "defl p95", r.get("defl_p95"), "max", r.get("defl_max"))
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("near", r["near_low"])
    if mode == "redteam": SPM.redteam(B, p, r)
