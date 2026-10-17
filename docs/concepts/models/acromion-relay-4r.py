"""acromion-relay-4r: a PLAIN O20 spherical 3R whose J1 walks the acromion-cap rim on a spring-centred J0 at the cap
pole (the plain-host control for pinknee-scapular-relay-4r and the stop-relay class re-measured under the corrected,
full-grid continuity flood tools/spare_flood.py).

Chain: scapula handler -> J0 (counted joint, R through GH, O20 hub, axis c = bvec(az_c, el_c) at the acromion / supra-
spinatus cap pole, spring-centred: preloaded double-leg torsion spring against a base dowel, own-angle stops |q0| <= T)
-> link 0 (12 x 3 Ti strap, arc a0 on the c -> u1r great circle; u1r = bvec(az_c, el_c - a0), J1 rests on the rim below
the pole on meridian az_c) -> J1 (ACTIVE R, O20) -> link 1 (a1) -> J2 (ACTIVE R, O20, own-angle stops at th margin
m_lo / m_hi from each fold) -> link 2 (a2) -> J3 (ACTIVE R, O20, humerus-fixed wdir(wd, wa)) -> K7 neck -> BOTTOM / cuff.
4 joints (DOF cap 4; the user prefers 3), 0 passive translations, no slides, no cables, no gears.

Determination (R17, every coordinate set):
  clamp (policy 0): q0 = the least-|q0| state with J2 inside [lo, hi] (the J0 spring's preload holds q0 = 0 while J2 is
          strictly inside its stops = mode A, the plain 3R; once J2 sits on a stop the arm pushes J0 the least amount);
          while J2 is on a stop the J0-J1-J3 sub-chain (arcs a0, th_stop) keeps a fold margin >= m_sw.
  twin  (policy 1): q0 = local minimum of (q0 rad)^2 + k2 (psi2(th) - psi2r)^2 by descent from 0 (J0 spring + J2
          centring spring, psi2r = the rest-pose J2 interior angle), J2 stops as a backup.
  q0 is quantised to 0.5 deg (tools/spare_flood.QG).
Continuity (CLAUDE.md rule): a ws pose with q0 != 0 counts only if the FULL-GRID flood (tools/spare_flood.py: 1432
envelope nodes, 2-deg HG slerps, q0 path-tracked, push <= 10 deg, seeds = every q0 = 0 node = the plain chain's region)
reaches its grid node in a state within 2 deg of the pose's q0. Held-out envelope poses are transit nodes only.
Seat rule: J1's whole travel stays inside az -110..135, el >= -20, x <= 0.2 (back of the shoulder / acromion top); T is
cut to the largest symmetric travel that does (a design step, reported as T_eff).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acromion-relay-4r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/acromion-relay-4r.py frozen '<json params>' --out R.json [--redteam]
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                       # noqa: E402
import spare_flood as SF                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("srr_for_ar4", os.path.join(HERE, "stop-relay-rocker-3r.py"))
SR = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SR)
SPM = SR.SPM

ID = "acromion-relay-4r"
NAME = "Acromion-pole relay 4R: plain O20 spherical 3R, J1 on a spring-centred J0 at the acromion-cap pole"
# proposer's pole60 cell (c = bvec(60, 89), a0 30, J1 rest bvec(60, 59)), dyad 40.3 / 74.1, J3 wdir(84.8, -11.37)
PARAMS = dict(az_c=60.0, el_c=89.0, a0=30.0, T=50.0, a1=40.34, a2=74.07, wd=84.8, wa=-11.37, sigma=-1, q=0.98,
              m_lo=K.FOLD_MARGIN, m_hi=K.FOLD_MARGIN, m_sw=K.FOLD_MARGIN, policy=0, k2=2.0,
              width=12.0, t_link=3.0, rad0=10.0, rad1=10.0, rad2=10.0, rad3=10.0, lift1=0.0, lift2=0.0, end_extra=0.0,
              connect=1, near=0)
ELEV_OVER = SPM.ELEV_OVER


def rotv(k, v, a_deg):
    a = np.radians(a_deg)[..., None]; k = K.unit(k)
    return v * np.cos(a) + np.cross(k, v) * np.sin(a) + k * (k * v).sum(-1, keepdims=True) * (1 - np.cos(a))


def axes_S(p):
    """J0 axis c and J1 rest u1r in the scapula frame"""
    return np.asarray(K.bvec(p["az_c"], p["el_c"]), float), np.asarray(K.bvec(p["az_c"], p["el_c"] - p["a0"]), float)


def seat_T(p):
    """largest symmetric J0 travel (<= T) that keeps J1 inside the seat rule (az -110..135, el >= -20, x <= 0.2)"""
    c, u1r = axes_S(p); qs = np.arange(0.0, float(p["T"]) + 0.01, 0.5)
    for sgn in (1, -1):
        U = rotv(np.broadcast_to(c, (len(qs), 3)), np.broadcast_to(u1r, (len(qs), 3)), sgn * qs)
        el = np.degrees(np.arcsin(np.clip(U[:, 1], -1, 1))); az = np.degrees(np.arctan2(U[:, 2], -U[:, 0]))
        good = (az >= -110) & (az <= 135) & (el >= -20) & (U[:, 0] <= 0.20)
        if not good[0]: return -1.0
        bad = np.nonzero(~good)[0]
        if len(bad): qs = qs[:bad[0]]
    return float(qs[-1])


def cfg(p):
    c, u1r = axes_S(p)
    return SF.Cfg(c, u1r, K.wdir(p["wd"], p["wa"]), p["a1"], p["a2"], T=p["T_eff"], m=min(p["m_lo"], p["m_hi"]),
                  m_lo=p["m_lo"], m_hi=p["m_hi"], m_sw=p["m_sw"], policy="energy" if p["policy"] else "clamp", k2=p["k2"])


def q0_policy(s, u3S):
    """per-pose state q0 (deg), ok, sub-chain margin, th (P,) - the pose-local state of tools/spare_flood (vectorised)"""
    TH = np.degrees(np.arccos(np.clip(u3S @ s.U1.T, -1, 1)))
    feas = (TH >= s.lo) & (TH <= s.hi) & s.trav[None, :]
    i0 = int(np.argmin(np.abs(SF.QG))); r_ = np.arange(len(TH))
    if s.policy == "energy":
        E = np.radians(SF.QG)[None, :] ** 2 + s.k2 * np.radians(s.psi(TH) - s.psir) ** 2
        E = np.where(feas, E, np.inf); j = np.full(len(TH), i0); bad = ~feas[:, i0]
        if bad.any(): j[bad] = np.where(feas[bad], np.abs(SF.QG)[None, :], np.inf).argmin(1)
        for _ in range(500):
            jl = np.clip(j - 1, 0, len(SF.QG) - 1); jr = np.clip(j + 1, 0, len(SF.QG) - 1)
            el, er, ec = E[r_, jl], E[r_, jr], E[r_, j]
            mv = np.where((el < ec) & (el <= er), -1, np.where(er < ec, 1, 0))
            if not mv.any(): break
            j = j + mv
        ok = np.isfinite(E[r_, j])
    else:
        cost = np.where(feas, np.abs(SF.QG)[None, :], np.inf); j = cost.argmin(1); ok = np.isfinite(cost.min(1))
    q0 = SF.QG[j]; th = TH[r_, j]
    ths = np.where(th > (s.lo + s.hi) / 2, s.hi, s.lo); g = np.degrees(np.arccos(np.clip(u3S @ s.c, -1, 1)))
    sm = np.minimum.reduce([g - np.abs(s.a0 - ths), s.a0 + ths - g, 360 - s.a0 - ths - g])
    onstop = (np.abs(th - s.hi) < 0.6) | (np.abs(th - s.lo) < 0.6)
    ok &= ~onstop | (np.abs(q0) < 1e-9) | (sm >= s.m_sw)
    return np.where(ok, q0, 0.0), ok, sm, th, onstop


def build(B, F, p):
    s = cfg(p); w = K.wdir(p["wd"], p["wa"])
    u3S = np.einsum("pji,pj->pi", F.RS, F.HG(w))
    q0, okr, sm, th, onstop = q0_policy(s, u3S)
    u1S = rotv(np.broadcast_to(s.c, u3S.shape), np.broadcast_to(s.u1r, u3S.shape), q0)
    c = F.S(s.c); u1 = np.einsum("pij,pj->pi", F.RS, u1S); p3 = F.HG(w)
    if c.ndim == 1: c = np.broadcast_to(c, u1.shape).copy()
    p2, ok2, margin = K.closure(u1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=min(p["m_lo"], p["m_hi"]) - 1e-3)
    ok = okr & ok2
    ref1 = rotv(c, F.S([1.0, 0, 0]) * np.ones_like(u1), q0)                   # J1's reference is carried by link 0
    q = np.stack([q0, K.axis_angle(u1, ref1, p2), K.axis_angle(p2, u1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    r0, r1, r2, r3 = (float(p[k]) for k in ("rad0", "rad1", "rad2", "rad3"))
    l1, l2 = float(p.get("lift1", 0.0)), float(p.get("lift2", 0.0))
    hubs = [K.hub_member("hub0", c, "J0", rad=r0), K.hub_member("hub1", u1, "J1", rad=r1, t=K.CROWN + l1),
            K.hub_member("hub2", p2, "J2", rad=r2, t=K.CROWN + l2), K.hub_member("hub3", p3, "J3", rad=r3)]
    wd_, t_ = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    links = [K.strap_member("link0", c, u1, ("J0", "J1"), width=wd_, t=t_, ramp_to=(("hub0", K.STACK), ("hub1", 0.0)), end_mm=end),
             K.strap_member("link1", u1, p2, ("J1", "J2"), width=wd_, t=t_, ramp_to=(("hub1", K.STACK + l1), ("hub2", 0.0)),
                            over=[("link0", 1.0)], end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=wd_, t=t_, ramp_to=(("hub2", K.STACK + l2), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0), ("link0", 1.0)], end_mm=end),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    okk = ok & np.isfinite(q).all(-1)
    thm = np.minimum(th - s.lo + min(p["m_lo"], p["m_hi"]), s.hi + min(p["m_lo"], p["m_hi"]) - th)   # J1-J3 distance from the folds
    rel = okk & (np.abs(q0) > 1e-9)
    info = dict(residual_deg=round(float(K.closure_residual(u1, p3, p2, p["a1"], p["a2"])[okk].max()), 5) if okk.any() else None,
                min_margin=round(float(margin[okk].min()), 2) if okk.any() else None,
                th_fold_margin_min=round(float(thm[okk].min()), 2) if okk.any() else None,
                sub_margin_min=round(float(sm[rel].min()), 2) if rel.any() else None,
                q0_range=[float(q0[okk].min()), float(q0[okk].max())] if okk.any() else None,
                relay=int(rel.sum()), onstop=int((okk & onstop).sum()), T_eff=p["T_eff"])
    ch = K.Chain(members=hubs + links, ok=okk, q=q, joints=dict(J0=c, J1=u1, J2=p2, J3=p3), info=info)
    ch._q0 = q0; ch._s = s
    return ch


def connected(B, p, ch):
    """(P,) bool for ws poses with q0 != 0: the full-grid flood reaches the pose's node in a state within 2 deg of its
    q0 (nodes missing from the grid count as not connected)"""
    s = ch._s; q0 = np.asarray(ch._q0); conn, states = SF.flood(s, seeds="modeA")
    n = len(B.kind); out = np.ones(n, bool); miss = 0
    for i in range(n):
        if B.kind[i] != "ws" or abs(q0[i]) < 1e-9: continue
        j = SF.node_of(B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"])
        if j is None: out[i] = False; miss += 1; continue
        out[i] = any(abs(x - q0[i]) <= 2.0 for x in states.get(j, ()))
    return out, dict(grid_conn=round(float(conn.mean()), 3), off_grid=miss)


def snap(p):
    p = dict(PARAMS, **p); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["el_c"] = min(89.5, max(80.0, float(p["el_c"]))); p["a0"] = min(45.0, max(15.0, float(p["a0"])))
    p["T"] = min(90.0, max(0.0, float(p["T"]))); p["az_c"] = float(p["az_c"])
    fm = K.FOLD_MARGIN
    for k in ("m_lo", "m_hi"): p[k] = min(20.0, max(fm, float(p[k])))
    p["m_sw"] = max(fm, float(p["m_sw"])); p["policy"] = int(round(min(1, max(0, float(p["policy"])))))
    p["k2"] = min(16.0, max(0.1, float(p["k2"])))
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    for k in ("lift1", "lift2"): p[k] = min(4.0, max(0.0, float(p.get(k, 0.0))))
    for k in ("rad0", "rad1", "rad2", "rad3"): p[k] = K.hub_rad(p[k], SPM.SLIM)   # O20 only (user 2026-10-16)
    for k in ("width", "t_link"): p[k] = PARAMS[k]
    p["T_eff"] = seat_T(p)
    return p


def evaluate(B, params):
    p = snap(params)
    if p["T_eff"] < 0:                                       # the J1 rest seat itself breaks the seat rule
        return p, dict(gap=275.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, honest=False,
                       audit=["J1 rest seat outside the J1 seat rule"], inband_member={})
    r = K.evaluate(B, build, p); r = SR.declared_audit(r, p)
    ch = B._kit_last["chain"]
    if p.get("connect", 1) and p["T_eff"] > 0:
        take = np.array([SR._taken(B, j) for j in range(len(B.res))])
        conn, fi = connected(B, p, ch)
        drop = [j for j in range(len(B.res)) if take[j] and not conn[j]]
        for j in drop: B.res[j] = None
        B._kit_last["take"] = B._kit_last["take"].copy(); B._kit_last["take"][drop] = False
        r["islands_dropped"] = len(drop); r["flood"] = fi
    r = SR.extras(B, r, p)
    r.update({k: ch.info.get(k) for k in ("th_fold_margin_min", "sub_margin_min", "q0_range", "relay", "onstop", "T_eff")})
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


REPORT_KEYS = ("gap_near1", "gap_plain", "reach_plain", "inband14_plain", "contact_plain", "islands_dropped", "overhead", "taken_relay", "min_metal_skin", "th_fold_margin_min",
               "sub_margin_min", "q0_range", "relay", "onstop", "T_eff", "flood", "crown_contact_poses")


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SPM._jsonable(v)}


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm radial; the
    full-grid flood is re-run on the big bench's ws poses"""
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
        r = K.evaluate(Bb, build, pf); r = SR.declared_audit(r, pf); ch = Bb._kit_last["chain"]
        if pf.get("connect", 1) and pf["T_eff"] > 0:
            take = np.array([SR._taken(Bb, j) for j in range(len(Bb.res))]); conn, fi = connected(Bb, pf, ch)
            drop = [j for j in range(len(Bb.res)) if take[j] and not conn[j]]
            for j in drop: Bb.res[j] = None
            Bb._kit_last["take"] = Bb._kit_last["take"].copy(); Bb._kit_last["take"][drop] = False
            r["islands_dropped"] = len(drop); r["flood"] = fi
        r = SR.extras(Bb, r, pf)
        r.update({k: ch.info.get(k) for k in ("th_fold_margin_min", "sub_margin_min", "q0_range", "relay", "onstop", "T_eff")})
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                     "min_metal_skin", "overhead", "inband_member", "taken_relay", "islands_dropped",
                                                     "th_fold_margin_min", "sub_margin_min", "q0_range")}, flush=True)
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
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r.get("inband_member"), "res", r.get("residual_deg"), "margin", r.get("min_margin"))
    print({k: r.get(k) for k in REPORT_KEYS})
    print("near", r.get("near_low"))
    if mode == "redteam": SPM.redteam(B, p, r)
