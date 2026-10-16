"""stop-relay-rocker-3r: the spine-parked spherical 3R (slim O15 J2 / J3) with J1 on a spring-centred passive acromial
rocker. J2 has hard stops a margin short of its fold; the rocker turns only while J2 sits on a stop.

Chain: scapula handler -> base -> R0 (PASSIVE pivot, axis c through GH, slim O15 hub = MR117-2RS pair, AS5600 sensed,
two opposed preloaded torsion springs centre it, |q0| <= qmax) -> rocker (12 x 3 Ti strap on the c -> u1 great circle,
arc beta) -> J1 (O20 hub, ACTIVE R through GH) -> link 1 -> J2 (O15, ACTIVE R, hard stops at angle(u1, u3) = lo / hi)
-> link 2 -> J3 (O15, ACTIVE R, arm-fixed axis) -> member 3 = hub 3's arm-end plate + K7 neck rigid to BOTTOM -> cuff.
Passive translations 0, passive rotations 1 (R0, sensed, spring-centred), cuff slides 0.

Relay (force closure, every coordinate determined - R17):
  th = angle(u1r, u3) with u1r = J1 at the rocker centre (q0 = 0).
  mode A  lo <= th <= hi   : q0 = 0, u1 = u1r (the spring preload T0 holds it; J2 strictly inside its stops)
  mode B  th > hi          : J2 on its high stop (angle(u1, u3) = hi); the rocker turns to the closure root of the
  mode C  th < lo          : rocker sub-chain (c, u1, u3; arcs beta, hi or lo) with the LEAST |q0|: the spring's energy
                             minimum on the boundary of the feasible arc {q0 : lo <= angle(R(c, q0) u1r, u3) <= hi}.
  lo = |a1 - a2| + m_lo, hi = a1 + a2 - m_hi (J2 fold margins = the stops); the rocker sub-chain keeps a fold margin
  >= m_sw (10 deg, not swept) so the relay never passes its own singularity; |q0| <= qmax (rocker end stops).
  Interpolated frames (dense K2) re-run the relay, and q0 / J1-J3 values and every axis are followed for jumps.

Members (kit): hub0 (pivot, S-fixed, rad0), hub1 (moves with the rocker, rad1), hub2, hub3, rocker strap (upper member
at R0, lower member at J1), link 1 (upper at J1; over the rocker by 1 mm by construction when l1_over = 1), link 2 (over
link 1, the neck and the rocker), K7 neck. Crown / wall skin check of all four hubs, near-touch, overhead split.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/stop-relay-rocker-3r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/stop-relay-rocker-3r.py frozen '<json params>' --out R.json [--redteam]
"""
import functools, importlib.util, json, math, os, re, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("spm_for_relay", os.path.join(HERE, "spine-parked-j2-3r.py"))
SPM = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SPM)

ID = "stop-relay-rocker-3r"
NAME = "Stop-relay rocker 3R: J1 on a spring-centred acromial rocker that moves only once J2 is on a hard stop"
# seats = spine-parked CMA-B (verified frozen exact 34.79) ; rocker beta 30 / phi 330 (ideation seed)
PARAMS = dict(az=102.78, el=65.35, a1=40.68, a2=73.76, wd=84.49, wa=-12.76, sigma=-1, q=0.979,
              width=12.0, t_link=3.0, rad0=7.5, rad1=10.0, rad2=7.5, rad3=7.5, end_extra=0.0, vm=0,
              beta=30.0, phi=330.0, az_c=None, el_c=None,   # pivot: u1 tilted by beta about a normal turned phi about u1
              m_lo=10.0, m_hi=10.0, m_sw=10.0, qmax=75.0, l1_over=1, relay=1, relay_lo=1, relay_hi=1, lift1=0.0, lift2=0.0, near=0)
# lift1 / lift2 (mm): the upper member's end zone at J1 (link 1) / J2 (link 2) sits lift mm above the 0.15 running gap
# (a spacer: only raises metal), so a folded link pair clears by >= 1 mm just past K6's 12-mm joint zone
# relay_lo / relay_hi 0: that side has no relay (J2's stop is then a plain joint limit: poses past it are not taken)
SLIM = SPM.SLIM
ELEV_OVER = SPM.ELEV_OVER


def rotv(k, v, a_deg):
    """rotate v (P,3) about unit k (P,3) by a (P,) deg (Rodrigues)"""
    a = np.radians(a_deg)[..., None]; k = K.unit(k)
    return v * np.cos(a) + np.cross(k, v) * np.sin(a) + k * (k * v).sum(-1, keepdims=True) * (1 - np.cos(a))


def pivot_dir(p):
    """pivot axis c in the scapula frame"""
    if p.get("az_c") is not None and p.get("el_c") is not None: return K.bvec(p["az_c"], p["el_c"])
    u = np.asarray(K.bvec(p["az"], p["el"]), float); ref = K.unit(np.cross(u, [0.0, 1.0, 0.0]))
    ax = rotv(u[None], ref[None], np.array([float(p["phi"])]))[0]
    return rotv(ax[None], u[None], np.array([float(p["beta"])]))[0]


def relay(F, p):
    """-> u1r, u1 (P,3), c (P,3), p3, q0 (P,), mode (P,) 0 A / 1 B / 2 C / -1 none, ok (P,), sw_margin (P,)"""
    u1r = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    c = F.S(pivot_dir(p)); n = len(u1r)
    if c.ndim == 1: c = np.broadcast_to(c, (n, 3)).copy()
    th = np.degrees(np.arccos(np.clip((u1r * p3).sum(-1), -1, 1)))
    lo = abs(p["a1"] - p["a2"]) + p["m_lo"]; hi = p["a1"] + p["a2"] - p["m_hi"]
    mode = np.where((th >= lo) & (th <= hi), 0, -1); u1 = u1r.copy(); q0 = np.zeros(n); swm = np.full(n, np.nan)
    if p.get("relay", 1):
        for code, ths, sel in ((1, hi, th > hi), (2, lo, th < lo)):
            if not p.get("relay_hi" if code == 1 else "relay_lo", 1): continue
            if not sel.any(): continue
            R = []
            for s in (1, -1):
                v, _, mg = K.closure(c, p3, p["beta"], ths, s, margin_deg=-1e9)
                exists = (mg > 0) & np.isfinite(v).all(-1)
                R.append((v, exists, mg, K.axis_angle(c, u1r, v)))
            a0 = np.where(R[0][1], np.abs(R[0][3]), np.inf); a1_ = np.where(R[1][1], np.abs(R[1][3]), np.inf)
            pick = a1_ < a0
            v = np.where(pick[:, None], R[1][0], R[0][0]); qq = np.where(pick, R[1][3], R[0][3]); mg = R[0][2]
            good = sel & np.isfinite(np.minimum(a0, a1_)) & (mg >= p["m_sw"]) & (np.abs(qq) <= p["qmax"])
            u1[good] = v[good]; q0[good] = qq[good]; mode[good] = code; swm[sel] = mg[sel]
    return u1r, u1, c, p3, q0, mode, mode >= 0, swm


def build(B, F, p):
    u1r, u1, c, p3, q0, mode, okr, swm = relay(F, p)
    mJ2 = min(p["m_lo"], p["m_hi"]) - 1e-3
    p2, ok2, margin = K.closure(u1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=mJ2)   # J2 inside / on its stops
    ok = okr & ok2
    ref1 = rotv(c, F.S([1.0, 0, 0]) * np.ones_like(u1), q0)                              # J1 reference carried by the rocker
    q = np.stack([q0, K.axis_angle(u1, ref1, p2), K.axis_angle(p2, u1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    r0, r1, r2, r3 = (float(p[k]) for k in ("rad0", "rad1", "rad2", "rad3"))
    l1, l2 = float(p.get("lift1", 0.0)), float(p.get("lift2", 0.0))         # a spacer adds its height to that hub's stack
    hubs = [K.hub_member("hub0", c, "R0", rad=r0), K.hub_member("hub1", u1, "J1", rad=r1, t=K.CROWN + l1),
            K.hub_member("hub2", p2, "J2", rad=r2, t=K.CROWN + l2), K.hub_member("hub3", p3, "J3", rad=r3)]
    w, t = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    l1_over = [("rocker", 1.0)] if p.get("l1_over", 1) else []
    links = [K.strap_member("rocker", c, u1, ("R0", "J1"), width=w, t=t, ramp_to=(("hub0", K.STACK), ("hub1", 0.0)), end_mm=end),
             K.strap_member("link1", u1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK + float(p.get("lift1", 0.0))), ("hub2", 0.0)),
                            over=l1_over, end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK + float(p.get("lift2", 0.0))), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0), ("rocker", 1.0)], end_mm=end),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    okk = ok & np.isfinite(q).all(-1)
    info = dict(residual_deg=round(float(K.closure_residual(u1, p3, p2, p["a1"], p["a2"])[okk].max()), 5) if okk.any() else None,
                rocker_residual_deg=round(float(np.abs(np.degrees(np.arccos(np.clip((u1 * c).sum(-1), -1, 1))) - p["beta"])[okk].max()), 5) if okk.any() else None,
                min_margin=round(float(margin[okk].min()), 2) if okk.any() else None,
                modes=dict(A=int(((mode == 0) & okk).sum()), B=int(((mode == 1) & okk).sum()), C=int(((mode == 2) & okk).sum()),
                           none=int((~okk).sum())),
                q0_range=[round(float(q0[okk].min()), 1), round(float(q0[okk].max()), 1)] if okk.any() else None,
                sw_margin_min=round(float(np.nanmin(swm[okk & (mode > 0)])), 2) if (okk & (mode > 0)).any() else None,
                hub_rad=dict(R0=r0, J1=r1, J2=r2, J3=r3))
    return K.Chain(members=hubs + links, ok=okk, q=q, joints=dict(R0=c, J1=u1, J2=p2, J3=p3), info=info)


def declared_audit(r, p):
    """the spine-parked declared-hub rule for every hub incl. the pivot (R0 -> rad0)"""
    keep, decl = [], {}
    for msg in r.get("audit") or []:
        m = re.match(r"(hub\d): hub of ([RJ]\d) smaller than O20 \(covers ([\d.]+) of the disc, reaches ([\d.]+) mm\)", msg)
        if m:
            rad = float(p["rad" + m.group(2)[1]]); cov = float(m.group(3)) * (K.HUB_R / rad) ** 2; reach = float(m.group(4))
            if rad in SLIM and cov >= 0.75 and reach >= rad - 0.5:
                decl[m.group(2)] = dict(rad=rad, component=SLIM[rad], cover=round(cov, 3), reach=reach); continue
        keep.append(msg)
    r["audit"] = keep; r["declared_hubs"] = decl
    c = r.get("checks") or {}
    r["honest"] = c.get("mode") == "march" and c.get("cont") in (True, "frames") and bool(c.get("collide")) and not keep
    return r


_taken = SPM._taken


def crown_points(m, rho, rad):
    """SPM.crown_points with the member's own stack height m.t (12.25 + a spacer) for the crown and the top wall ring"""
    F0 = float(rho[0]); k = m.K[:, None, :]
    crown = (F0 + m.t) * k + m.xy[None, :, :1] * m.A[:, None, :] + m.xy[None, :, 1:] * m.Bv[:, None, :]
    n = max(16, int(round(2 * math.pi * rad / 2.0))); ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
    c, s = rad * np.cos(ang), rad * np.sin(ang)
    lv = sorted(set(SPM.CROWN_LEVELS) | {m.t})
    wall = [(F0 + h) * k + c[None, :, None] * m.A[:, None, :] + s[None, :, None] * m.Bv[:, None, :] for h in lv if h <= m.t + 1e-9]
    return np.concatenate([crown] + wall, 1)


def extras(B, r, p):
    """crown / wall check of every hub (radius = member width / 2), near-touch, overhead >= 140, relay modes of taken poses"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [crown_points(m, prof[m.name], m.width / 2.0)[Pi] for m in hubs]
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
    q0 = np.asarray(ch.q)[:, 0]; tkn = np.array([_taken(B, j) for j in range(len(B.res))])
    mA = np.abs(q0) < 1e-9
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): r[k] = rr[k]
    r.update(crown_contact_poses=int(len(bad)), crown_min=round(float(np.min(cmin[np.isfinite(cmin)])), 2) if np.isfinite(cmin).any() else None,
             min_metal_skin=round(float(allmin[0][0]), 2) if allmin else None,
             near_low=[dict(mm=round(float(dd), 2), i=int(j), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"],
                            axial=B.poses[j]["axial"], crown=cwho.get(int(j)) if cmin[j] <= float(np.min(B.res[j])) else "face")
                       for dd, j in allmin[:5]],
             gap_near1=rn["gap"], near1=dict(reach=rn["reach"], follow=rn["follow"], inband14=rn["inband14"], contact=rn["contact"]),
             overhead=over,
             taken_relay=dict(A=int((tkn & mA).sum()), BC=int((tkn & ~mA).sum()),
                              ws_BC=int((tkn & ~mA & ws).sum()), clip_BC=int((tkn & ~mA & cl).sum()),
                              q0_p5_p95=[round(float(np.percentile(q0[tkn & ~mA], 5)), 1), round(float(np.percentile(q0[tkn & ~mA], 95)), 1)]
                              if (tkn & ~mA).any() else None))
    return r


def snap(p):
    p = dict(PARAMS, **p); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    for k in ("rad0", "rad1", "rad2", "rad3"): p[k] = min(SLIM, key=lambda x: abs(x - float(p[k])))
    p["beta"] = min(60.0, max(10.0, float(p["beta"]))); p["phi"] = float(p["phi"]) % 360.0
    p["m_lo"] = min(20.0, max(8.0, float(p["m_lo"]))); p["m_hi"] = min(20.0, max(8.0, float(p["m_hi"])))
    p["m_sw"] = max(10.0, float(p["m_sw"])); p["relay_lo"] = int(round(float(p["relay_lo"]))); p["relay_hi"] = int(round(float(p["relay_hi"]))); p["qmax"] = min(90.0, max(0.0, float(p["qmax"])))
    for k in ("lift1", "lift2"): p[k] = min(4.0, max(0.0, float(p.get(k, 0.0))))
    for k in ("width", "t_link"): p[k] = PARAMS[k]                   # never thinned by a search
    return p


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = snap(params)
    r = K.evaluate(B, build, p); r = declared_audit(r, p); r = extras(B, r, p)
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SPM._jsonable(v)}


def lab(B, i): return SPM.lab(B, i)


def redteam(B, p, r):
    SPM.redteam(B, p, r)
    L = B._kit_last; ch = L["chain"]; q0 = np.asarray(ch.q)[:, 0]
    el = np.array([x["elev"] for x in B.poses]); tk = np.array([_taken(B, j) for j in range(len(B.res))])
    print("-- relay: taken poses by mode, q0 extremes --", r.get("taken_relay"), ch.info.get("modes"), "sw margin", ch.info.get("sw_margin_min"))
    o = np.argsort(-np.abs(q0))[:8]
    for i in o: print(f"  q0 {q0[i]:6.1f} taken {bool(tk[i])} {lab(B, int(i))}")


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm radial"""
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
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf); r = declared_audit(r, pf); r = extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                     "min_metal_skin", "overhead", "inband_member", "modes", "taken_relay")}, flush=True)
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
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), r.get("rocker_residual_deg"),
          "margin", r.get("min_margin"), "declared", r.get("declared_hubs"))
    print("modes", r.get("modes"), "q0", r.get("q0_range"), "sw", r.get("sw_margin_min"), "taken", r.get("taken_relay"))
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("near", r["near_low"])
    if mode == "redteam": redteam(B, p, r)
