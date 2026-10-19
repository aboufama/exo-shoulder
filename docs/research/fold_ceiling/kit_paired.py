"""fold-ceiling PAIRED KIT INSTRUMENT (not a catalogued design; was drafted as balanced-upj3-knuckle-3r). (fold-ceiling study, docs/research/fold_ceiling.md): the leaders' family re-seated where the
fold-ceiling scan says the J1-J3 window covers the workspace AND every rigid part can park: BALANCED arcs (a1 ~ a2, so the
folded wall sits at the 5-deg margin itself) and J3 pointing UP the arm toward the shoulder (wdir d ~ 105-120 instead of the
leaders' ~70-77), which shrinks the spread of th = angle(J1, J3) under internal rotation (the leaders' stretched losses).
3 ACTIVE revolutes (J1, J2, J3) through GH + a slaved knuckle K in link 1 (link 1a J1 -> K arc bk1, link 1b K -> J2 arc
bk2 = a1max + 5 - bk1): K on stop A keeps a1e = a1 while th <= a1 + a2 - 5, beyond it K opens just enough
(a1e = th - a2 + 5, the IDEAL slaved law) up to stop B (a1max). No cuff knee (every axis passes through GH: no drift).

HONESTY: the knuckle's DRIVE (the leaders' cam / roller / rod: crank, flank boss, horn) is NOT modelled - it is an ideal
slaved law. Compare only against the CONTROL (the same kit model at the verified leader's seats and arcs, `control`
mode), never against the leader's verified number; the drive metal costs the leaders ~2-5 frozen points.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/kit_paired.py fit '<json params>'
    ... frozen|held '<json>' [out.json]        (fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) / held out EXACT)
    ... control frozen|held                     (the leader's seats / arcs in this kit model)
    ... search '<json start>' n                 (local search on Bench(60,160) fast, objective = the 1 mm near-touch gap)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # docs/research/fold_ceiling -> repo
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
import concept_bench as CB                                   # noqa: E402

ID = "fold-ceiling-kit-paired"
NAME = "Balanced dyad, J3 up the arm, slaved knuckle (fold-ceiling seat)"
# the fold-ceiling local search's acromion-top design (docs/research/fold_ceiling/local_search_tau0.8.json, result 3)
PARAMS = dict(az1=96.97, el1=60.99, d3=106.91, a3=1.94, a1=46.32, a2=48.60, a1max=70.23, bk1=28.67, sK=-1.0, sigma=-1.0,
              margin=K.FOLD_MARGIN, width=12.0, t_link=3.0, q=1.0)
# the verified leader's axes in this kit model (lost_poses_roller-longdyad-knuckle-3r.json: u1 bvec(95.39, 67.90), u3 =
# wdir(77.25, -8.2) incl. its b3 tilt, a1 37.55 / a2 57.22 / a1max 58.77, bk1 26.0, branch -1)
CONTROL = dict(az1=95.39, el1=67.90, d3=77.25, a3=-8.2, a1=37.552, a2=57.218, a1max=58.768, bk1=26.0, sK=-1.0, sigma=-1.0,
               margin=K.FOLD_MARGIN, width=12.0, t_link=3.0, q=1.0)


def closure_v(b, w, a1e, a2, sigma):
    c = np.clip((b * w).sum(-1), -1, 1); n = K.unit(np.cross(b, w)); A1, A2 = np.radians(a1e), math.radians(a2)
    den = 1 - c ** 2 + 1e-12; A = (np.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * np.cos(A1)) / den
    p0 = A[:, None] * b + Bq[:, None] * w; h2 = 1 - (p0 * p0).sum(-1)
    return K.unit(p0 + sigma * np.sqrt(np.clip(h2, 0, None))[:, None] * n), h2 > 0


def build(B, F, p):
    m = float(p["margin"]); a1, a2, amax = float(p["a1"]), float(p["a2"]), float(p["a1max"])
    bk1 = float(p["bk1"]); bk2 = amax + 5.0 - bk1
    p1 = F.S(K.bvec(p["az1"], p["el1"])); p3 = F.HG(K.wdir(p["d3"], p["a3"]))
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    lo = abs(a1 - a2) + m; hi0 = min(a1 + a2, 360 - a1 - a2) - m; hi = min(amax + a2, 360 - amax - a2) - m
    a1e = np.where(th <= hi0, a1, th - a2 + m)
    ok = (th >= lo) & (th <= hi) & (abs(bk1 - bk2) + 5.0 <= a1)                 # K dyad: stop A >= 5 deg from its own fold
    p2, okc = closure_v(p1, p3, a1e, a2, float(p["sigma"])); ok &= okc
    pK, okK, mK = K.closure(p1, p2, bk1, bk2, float(p["sK"]), margin_deg=0.0); ok &= okK
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), K.axis_angle(pK, p1, p2), K.axis_angle(p2, pK, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    for j, (s_lo, s_hi) in (p.get("stops") or {}).items():      # hard stops on a joint's OWN angle (dowel in an arc slot)
        ok &= ((q[:, int(j)] - s_lo) % 360.0) <= ((s_hi - s_lo) % 360.0)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    links = [K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0))),
             K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK), ("hub2", 0.0)), over=[("link1a", 1.0)]),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1a", 1.0), ("neck", 1.0)]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    dK = np.where(ok, a1e - a1, np.nan)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3),
                   info=dict(min_margin=round(float(np.min(np.minimum(th - lo, hi - th)[ok])), 2) if ok.any() else None,
                             a1e_open_max=round(float(np.nanmax(dK)), 2) if ok.any() else None))


def clip_stops(p, delta, joints=(0, 2, 3)):
    """joint-range stops from the FIT bench's clip frames (never the wear / held poses): each joint's own angle limited to
    the arc its clip-frame values span, widened by delta deg on both sides (circular)"""
    B = K.bench(60, 160); F = K.frames(B); ch = build(B, F, dict(p, stops=None)); ok = np.asarray(ch.ok, bool) & F.clip
    st = {}
    for j in joints:
        a = np.sort(np.asarray(ch.q)[ok, j] % 360.0); gaps = np.diff(np.r_[a, a[0] + 360.0]); k = int(np.argmax(gaps))
        lo = a[(k + 1) % len(a)]; hi = a[k]                     # the arc that leaves out the largest empty gap
        st[str(j)] = [float((lo - delta) % 360.0), float((hi + delta) % 360.0)]
    return st


def held_bench():
    sp = importlib.util.spec_from_file_location("pkpol_h", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PV = importlib.util.module_from_spec(sp); sp.loader.exec_module(PV); return PV.held_bench()


def wear(params, which="bench", near=(1.0, 2.0)):
    """the frozen protocol: fit on Bench(60,160) fast (K.evaluate: K3 march, dense K2, K6), every member's underside
    FROZEN, worn on Bench(110,360) (which='bench') or the held-out set (which='held') EXACT: closure + K2 continuity along
    the clip frames + K6 part collisions + exact signed distance of every metal sample. Returns the report + per-pose dump."""
    p = dict(params); B1 = K.bench(60, 160); r1 = K.evaluate(B1, build, p); last = B1._kit_last; prof = last["prof"]
    if which == "held": B = held_bench()
    else:
        os.environ["CB_EXACT"] = "1"; B = CB.Bench(110, 360)
    F = K.frames(B); ch = build(B, F, p); ok = np.asarray(ch.ok, bool)
    ok, flips = K.continuity_dense(B, F, build, p, ok)
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = K.collisions(ch, pts, ok); take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    d = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = d[j]
    rep = B.report(); mins = {int(i): float(d[j].min()) for j, i in enumerate(Pi)}
    kind = np.array(B.kind); ws = kind == "ws"; elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))])
    nearg = {}
    for nm in near:
        bad = {i for i, v in mins.items() if v < nm}
        okn = lambda j: B.res[j] is not None and j not in bad
        R = float(np.mean([okn(j) for j in np.nonzero(ws)[0]])); Fo = float(np.mean([okn(j) for j in np.nonzero(~ws)[0]]))
        nearg[f"gap_near{nm:g}"] = CB.gap_of(rep["inband14"], Fo, R, 0.0)
    why = dict(fold=int((ws & ~np.asarray(ch.ok, bool)).sum()), flip=int(flips), parts=int((ws & ok & hit).sum()),
               contact=int(sum(1 for i, v in mins.items() if v < 0 and ws[i])))
    ov = ws & (elev >= 140)
    pp = [dict(i=int(i), kind=str(kind[i]), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
               taken=bool(i in mins and mins[i] >= 0), min_mm=round(mins[i], 3) if i in mins else None) for i in range(len(B.idx))]
    return dict(fit_fast={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, honest_fit=r1["honest"], audit=r1["audit"],
                frozen={k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, why=why, **nearg,
                min_metal_mm=round(min([v for v in mins.values()]), 3) if mins else None,
                depth_mm_max=round(-min([v for v in mins.values()] + [0.0]), 3),
                overhead=f"{int(sum(1 for i in np.nonzero(ov)[0] if pp[i]['taken']))}/{int(ov.sum())}",
                inband_member=r1["inband_member"], mass_g=r1["mass_g"], info=r1.get("a1e_open_max"), which=which, mode=B.mode, poses=pp)


def search(start, n, seed=0):
    """local search on Bench(60,160) fast; objective: the 1 mm near-touch gap of the fit (CLAUDE.md search rule)"""
    B = K.bench(60, 160); rng = np.random.default_rng(seed)
    STEP = dict(az1=3, el1=3, d3=3, a3=4, a1=2, a2=2, a1max=2, bk1=1.5)

    def obj(p):
        if not ((p["el1"] >= 50 and 60 <= p["az1"] <= 135) or (-60 <= p["az1"] <= 90 and 0 <= p["el1"] < 50)): return 1e9, None
        if p["a1max"] > 75 or p["a1max"] < p["a1"] or not 24 <= p["bk1"] <= 34: return 1e9, None
        r = K.evaluate(B, build, p); last = B._kit_last; pts = last["pts"]; take = last["take"]
        # 1 mm near-touch: a taken pose with any metal < 1 mm counts as lost
        Pi = np.nonzero(take)[0]
        if not len(Pi): return 1e9, r
        mins = np.array([min(float(np.min(B.res[i])) for _ in [0]) for i in Pi])
        kind = np.array(B.kind); ws = kind == "ws"
        good = np.zeros(len(kind), bool); good[Pi[mins >= 1.0]] = True
        g1 = CB.gap_of(r["inband14"], good[~ws].mean(), good[ws].mean(), 0.0)
        return g1, r
    p = dict(PARAMS, **start); f, r = obj(p); hist = [dict(p=p, f=f, r={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")})]
    print("start", f, hist[-1]["r"], flush=True)
    for it in range(n):
        q = dict(p)
        for k in rng.choice(list(STEP), size=rng.integers(1, 4), replace=False): q[k] = float(q[k] + rng.normal(0, STEP[k]))
        g, rr = obj(q)
        if g < f:
            p, f = q, g; hist.append(dict(p=p, f=f, r={k: rr[k] for k in ("gap", "reach", "follow", "inband14", "contact")}))
            print(it, round(f, 2), hist[-1]["r"], flush=True)
    return p, f, hist


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "fit"
    if mode == "control":
        which = a[1] if len(a) > 1 else "frozen"; t = time.time()
        out = wear(CONTROL, "held" if which == "held" else "bench"); out["params"] = CONTROL; out["secs"] = round(time.time() - t, 1)
        if len(a) > 2: json.dump(out, open(a[2], "w"), indent=0, default=float)
        print(json.dumps({k: v for k, v in out.items() if k != "poses"}, default=float)); sys.exit()
    par = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else {}))
    if "stop_delta" in par and par.get("stops") is None:
        par["stops"] = clip_stops(par, float(par["stop_delta"]))
    if mode == "fit":
        r = K.evaluate(K.bench(60, 160), build, par)
        print(json.dumps({k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest", "audit", "inband_member", "mass_g", "flips", "collide", "min_margin", "a1e_open_max")}, default=float))
    elif mode in ("frozen", "held"):
        t = time.time(); out = wear(par, "held" if mode == "held" else "bench"); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(a) > 2: json.dump(out, open(a[2], "w"), indent=0, default=float)
        print(json.dumps({k: v for k, v in out.items() if k != "poses"}, default=float))
    elif mode == "search":
        p, f, hist = search(json.loads(a[1]) if len(a) > 1 else {}, int(a[2]) if len(a) > 2 else 60)
        out = os.path.join(REPO, "docs", "research", "fold_ceiling", f"kit_search_{int(time.time())}.json")
        json.dump(dict(best=p, f=f, hist=hist), open(out, "w"), indent=1, default=float); print("BEST", f, json.dumps(p))
