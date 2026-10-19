"""minarc-stop-knuckle-4r: a plain spherical 3R (spine-parked / pin-knee metal) whose link 1 is split by a fourth,
PASSIVE, sensed O20 hub K, held on its stop A by a preloaded clock spring; J2 carries two hard stops on its interior
angle phi (catalogue id minarc-stop-knuckle-4r, family "redundant 4R, determined spare (Keemink layout)").

Chain: scapula handler -> J1 (O20, active R through GH) -> link 1a (12 x 3 Ti strap, arc b1) -> K (O20, passive R
through GH, sensed, clock spring onto stop A, stop B caps it) -> link 1b (strap, arc b2) -> J2 (O20, active R through
GH, interior-angle stops phi_lo / phi_hi, branch sigma) -> link 2 (strap, arc a2, over link 1a / 1b and the neck) -> J3
(O20, active R, humerus-fixed axis) -> K7 neck -> BOTTOM. 0 passive translations, 1 passive rotation (K).

THE MIN-ARC LAW (one-sided spring + stops = a determined 4th coordinate, R17). The arm pose fixes J1 (scapula) and J3
(humerus); the 4R has a 1-DOF self-motion, along which the arc a1e = angle(J1, J2) = f(psi) changes. The spring drives
psi (and a1e) DOWN until a stop holds it: K's stop A (a1e = a1), or J2's interior angle phi reaching phi_hi (stretched,
th = angle(J1, J3) > what a1 can span) / phi_lo (folded). So per pose
    a1e = a1                      if the 3R (a1, a2) closes with phi in [phi_lo, phi_hi]  (state A: rigid 3R)
    a1e = smallest x >= a1 with cos th = cos x cos a2 + sin x sin a2 cos phi_stop   otherwise (J2 on its stop, K open)
and a pose is reachable only if a1e <= a1max (stop B). In the forced states the moving chain is J1-K-J3 with J2 locked:
its own fold margin (th vs b1 and c = arc(K, J3)) must keep >= K.FOLD_MARGIN (the stop-relay sub-chain fold, checked
here, not assumed). The J2 dyad never reaches its own fold: the hard stops are its guard (phi_hi <= 180 - FOLD_MARGIN);
`mstop` 1 additionally asks the J2 dyad's th-margin >= FOLD_MARGIN in state A (the conservative reading, reported).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r.py [check|redteam] ['<json params>']
    hooks: build(B, F, p) / evaluate(B, params) -> (params, report) (tools/concept_sweep.py, tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/minarc-stop-knuckle-4r.py frozen '<json params>' --out R.json [--redteam]
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("spine_parked_ref", os.path.join(os.path.dirname(os.path.abspath(__file__)), "spine-parked-j2-3r.py"))
SP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SP)   # crown / wall check, near-touch, overhead, audit

ID = "minarc-stop-knuckle-4r"
NAME = "Min-arc stop knuckle 4R: a preloaded one-sided knuckle in link 1 with J2 hard stops (plain spherical chain)"
D2R = math.pi / 180
# seeds = the judge's re-seated pin-knee seats (catalogue model_spec): J1 bvec(90.76, 65.50), J3 wdir(74.85, -10.5)
PARAMS = dict(az=90.76, el=65.50, wd=74.85, wa=-10.5, a1=44.0, a2=74.0, b1=35.0, b2=55.0, a1max=78.0, phi_lo=15.0, phi_hi=170.0,
              sigma=-1, sK=-1, margin=K.FOLD_MARGIN, mstop=0, width=12.0, t_link=3.0, q=0.98, near=0)
SEED_SP = dict(az=119.41, el=67.05, wd=72.06, wa=0.91)       # second seed set (spine-parked base re-seated +15 / 0 / -10 / +15)
ELEV_OVER = 140.0
REPORT_KEYS = ("overhead", "gap_near1", "near1", "min_metal_skin", "forced", "forced_share", "stretched", "folded", "a1e_max", "psi_range", "min_sub_margin", "crown_contact_poses")
# link 1b leaves the knuckle in its own layer: a 1.0 mm spacer over link 1a's end (0.15 running gap + 0.85) for 16 mm, so
# the two straps, which part at psi >= ~58 deg, clear K6's 0.5 mm radial rule where they still overlap laterally past
# the 12 mm exempt zone (measured: 196 of 212 poses collided at 13.1-13.3 mm from K with the bare 0.15 mm stack)
KX = 0.85


def law(p1, p3, p):
    """-> a1e (P,), state (P,) 0 A / +1 stretched (J2 on phi_hi) / -1 folded (J2 on phi_lo), th (P,) deg; a1e nan = no root"""
    a1, a2 = float(p["a1"]), float(p["a2"])
    th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1)))
    cphi = (np.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R))
    st = cphi < math.cos(float(p["phi_hi"]) * D2R); fo = cphi > math.cos(float(p["phi_lo"]) * D2R)
    a1e = np.full(len(th), a1); state = np.zeros(len(th), int)
    for m, ps, s in ((st, float(p["phi_hi"]), 1), (fo, float(p["phi_lo"]), -1)):
        if not m.any(): continue
        A, Bc = math.cos(a2 * D2R), math.sin(a2 * D2R) * math.cos(ps * D2R); R = math.hypot(A, Bc); d = math.degrees(math.atan2(Bc, A))
        c = np.cos(th[m] * D2R) / R; g = np.degrees(np.arccos(np.clip(c, -1, 1)))
        r = np.stack([d - g, d + g], -1); r = (r + 180.0) % 360.0 - 180.0            # both roots, wrapped
        r = np.where(r >= a1 - 1e-6, r, np.inf); x = r.min(-1)
        x = np.where((np.abs(c) <= 1) & np.isfinite(x), x, np.nan)
        a1e[m] = x; state[m] = s
    return a1e, state, th


def closure_v(b, w, a1, a2, sigma):
    """K.closure with per-pose a1 (deg array); -> p, h2 (closes iff h2 > 0)"""
    b, w = K.unit(b), K.unit(w); c = np.clip((b * w).sum(-1), -1, 1); n = K.unit(np.cross(b, w))
    A1, A2 = np.asarray(a1, float) * D2R, np.asarray(a2, float) * D2R
    den = 1 - c ** 2 + 1e-12; A = (np.cos(A1) - c * np.cos(A2)) / den; Bq = (np.cos(A2) - c * np.cos(A1)) / den
    p0 = A[..., None] * b + Bq[..., None] * w; h2 = 1 - (p0 * p0).sum(-1)
    return K.unit(p0 + sigma * np.sqrt(np.clip(h2, 0, None))[..., None] * n), h2


def ang(u, v): return np.degrees(np.arccos(np.clip((K.unit(u) * K.unit(v)).sum(-1), -1, 1)))


def kinematics(F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    a1e, state, th = law(p1, p3, p)
    b1, b2 = float(p["b1"]), float(p["b2"])
    m = float(p["margin"]); sg = 1 if float(p["sigma"]) >= 0 else -1; sK = 1 if float(p["sK"]) >= 0 else -1
    fin = np.isfinite(a1e); a1s = np.where(fin, a1e, float(p["a1"]))
    p2, h2 = closure_v(p1, p3, a1s, float(p["a2"]), sg)
    pK, hK = closure_v(p1, p2, np.full(len(th), b1), np.full(len(th), b2), sK)
    ok = fin & (h2 > 0) & (hK > 0) & (a1s <= float(p["a1max"]) + 1e-9)
    ok &= (float(p["phi_hi"]) <= 180.0 - m) & (float(p["phi_lo"]) >= m)              # the J2 stops are the dyad's guard
    # K's own range: psi in (m, 180 - m) (a1e within [|b1-b2| + m, b1 + b2 - m])
    ok &= (a1s >= abs(b1 - b2) + m) & (a1s <= b1 + b2 - m)
    # forced states: the moving sub-chain J1-K-J3 (J2 locked) keeps its fold margin
    c = ang(pK, p3); msub = np.minimum.reduce([th - np.abs(b1 - c), b1 + c - th, 360 - b1 - c - th])
    ok &= (state == 0) | (msub >= m)
    m3 = np.minimum.reduce([th - abs(float(p["a1"]) - float(p["a2"])), float(p["a1"]) + float(p["a2"]) - th])
    if p.get("mstop"): ok &= (state != 0) | (m3 >= m)                                    # conservative reading
    res = np.maximum(np.abs(ang(p2, p1) - a1s), np.abs(ang(p2, p3) - float(p["a2"])))
    res = np.maximum(res, np.maximum(np.abs(ang(pK, p1) - b1), np.abs(ang(pK, p2) - b2)))
    ok &= res < 0.5
    psi = K.axis_angle(pK, p1, p2)
    return dict(p1=p1, p2=p2, p3=p3, pK=pK, a1e=a1s, state=state, th=th, ok=ok, res=res, msub=msub, psi=psi, b2=b2)


def build(B, F, p):
    k = kinematics(F, p); p1, p2, p3, pK, ok = k["p1"], k["p2"], k["p3"], k["pK"], k["ok"]
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), k["psi"], K.axis_angle(p2, pK, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0))),
             K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK + KX), ("hub2", 0.0)),
                            over=[("link1a", 1.0)], end_mm=K.HUB_R + 6.0),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1a", 1.0), ("link1b", 1.0), ("neck", 1.0)]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    o = ok
    info = dict(residual_deg=round(float(k["res"][o].max()), 5) if o.any() else None,
                forced_share=round(float((k["state"][o] != 0).mean()), 4) if o.any() else None,
                stretched=int(((k["state"] == 1) & o).sum()), folded=int(((k["state"] == -1) & o).sum()),
                a1e_max=round(float(k["a1e"][o].max()), 2) if o.any() else None,
                psi_range=[round(float(np.abs(k["psi"][o]).min()), 1), round(float(np.abs(k["psi"][o]).max()), 1)] if o.any() else None,
                min_sub_margin=round(float(k["msub"][o & (k["state"] != 0)].min()), 2) if (o & (k["state"] != 0)).any() else None)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3), info=info)


def _extras(B, r, p):
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [SP.crown_points(m, prof[getattr(m, "_was", m.name)], K.HUB_R)[Pi] for m in hubs]
        C = np.concatenate(parts, 1)
        dc = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        cmin[Pi] = dc.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): cwho[int(j)] = getattr(hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)], "_was", None) or hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)].name
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report()
    allmin = sorted((min(float(np.min(B.res[j])), cmin[j]), j) for j in range(len(B.res)) if SP._taken(B, j))
    save = list(B.res)
    for d, j in allmin:
        if d < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    el = np.array([q["elev"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind]); cl = ~ws
    ov = np.nonzero(el >= ELEV_OVER)[0]; ovw = ov[ws[ov]]; ovc = ov[cl[ov]]
    tk = [j for j in ov if SP._taken(B, j)]; d = np.concatenate([B.res[j] for j in tk]) if tk else np.zeros(0)
    over = dict(n_ws=int(len(ovw)), reach=round(float(np.mean([SP._taken(B, j) for j in ovw])), 4) if len(ovw) else None,
                n_clip=int(len(ovc)), follow=round(float(np.mean([SP._taken(B, j) for j in ovc])), 4) if len(ovc) else None,
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
    # forced-state accounting (the lead note: contact on forced poses, separately)
    kin = L.get("kin")
    if kin is not None:
        st = kin["state"]; okk = L["ok"]
        def share(mask):
            ii = np.nonzero(mask)[0]
            if not len(ii): return dict(n=0)
            tkn = [SP._taken(B, j) for j in ii]; con = [B.res[j] is not None and float(np.min(B.res[j])) < 0 for j in ii]
            return dict(n=int(len(ii)), taken=int(sum(tkn)), contact=int(sum(con)))
        r["forced"] = dict(ws_stretched=share(okk & ws & (st == 1)), ws_folded=share(okk & ws & (st == -1)), ws_A=share(okk & ws & (st == 0)),
                           clip_forced=share(okk & cl & (st != 0)), clip_A=share(okk & cl & (st == 0)))
    return r


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"])))
    for s in ("sigma", "sK"): p[s] = 1 if float(p[s]) >= 0 else -1
    p["margin"] = K.FOLD_MARGIN                                   # never a search parameter
    p["phi_hi"] = min(180.0 - p["margin"], float(p["phi_hi"])); p["phi_lo"] = max(p["margin"], float(p["phi_lo"]))
    r = K.evaluate(B, build, p)
    F = B._kitF; B._kit_last["kin"] = kinematics(F, p)
    r = SP.declared_audit(r, dict(p, rad1=10.0, rad2=10.0, rad3=10.0)); r = _extras(B, r, p)
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SP._jsonable(v)}


def lab(B, i): return SP.lab(B, i)


def redteam(B, p, r):
    SP.redteam(B, p, r)
    kin = B._kit_last.get("kin"); take = B._kit_last["take"]; ok = B._kit_last["ok"]
    if kin is None: return
    st = kin["state"]; el = np.array([q["elev"] for q in B.poses]); pl = np.array([q["plane"] for q in B.poses])
    ws = np.array([k == "ws" for k in B.kind])
    print("-- knuckle law: state counts over closing poses (A / stretched / folded) and their fate --")
    for nm, s in (("A", 0), ("stretched", 1), ("folded", -1)):
        ii = np.nonzero(ok & (st == s))[0]
        tk = [i for i in ii if SP._taken(B, i)]
        print(f"  {nm:9s} closing {len(ii)} (ws {int(ws[ii].sum())}), taken {len(tk)}, a1e {np.round(np.percentile(kin['a1e'][ii], [0, 50, 100]), 1) if len(ii) else '-'}"
              f", psi {np.round(np.percentile(np.abs(kin['psi'][ii]), [0, 50, 100]), 1) if len(ii) else '-'}")
    th = kin["th"]; nc = np.nonzero(~kin["ok"])[0]
    print(f"  not closing: {len(nc)} (ws {int(ws[nc].sum())}); th of those p5/p50/p95 {np.round(np.percentile(th[nc], [5, 50, 95]), 1) if len(nc) else '-'}; a1e>a1max {int((kin['a1e'][nc] > p['a1max']).sum())}, nan {int(np.isnan(kin['a1e'][nc]).sum())}")


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
    keep = lambda r: {k: v for k, v in r.items() if SP._jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); Bb._kit_last["kin"] = kinematics(Bb._kitF, pf)
        r = SP.declared_audit(r, dict(pf, rad1=10.0, rad2=10.0, rad3=10.0)); r = _extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp; K.collisions = coll
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead", "inband_member", "forced")}, flush=True)
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
    print("per member", r["inband_member"], "mass", r["mass_g"], "info", {k: r.get(k) for k in ("residual_deg", "forced_share", "stretched", "folded", "a1e_max", "psi_range", "min_sub_margin")})
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("forced", r.get("forced"))
    print("near", r["near_low"])
    if mode == "redteam": redteam(B, p, r)
