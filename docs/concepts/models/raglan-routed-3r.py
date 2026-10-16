"""Concept model: RAGLAN-ROUTED 3R ON FAR-END HUBS (id raglan-routed-3r).

Plain spherical 3R (3 active pins on O20 bearing hubs, 0 passive DOF, no cuff slide) with two levers taken from pattern
making / orthotic fitting:

  1. FAR-END HUBS. A revolute axis is a LINE through GH; the kinematics (closure, fold band, joint values) do not care
     which end of the line carries the bearing. e1, e2, e3 = +1 / -1 put hub k at +p_k or at -p_k. The links then span
     arccos(e1 e2 cos a1) and arccos(e2 e3 cos a2) instead of a1 and a2 (a far-end hub changes the pattern piece, not the
     motion). Default layout: the fold-free POSTERIOR J1 line (bvec(-24, 4), hub on the back of the shoulder over
     scapula-fixed skin) and J3 on the posterior arm (wdir(80, -90)).
  2. RAGLAN ROUTING. A link between two hubs need not run on the great circle. Like a raglan seam it can take a
     planform turn: link k = two great-circle legs hub -> W_k -> hub, W_k = cos(d) slerp(h_a, h_b, t) + sin(d) n_ab
     (n_ab = the link's own plane normal), FIXED IN THE LINK (the link is one rigid piece: a constant 12 x 3 section
     swept along two straight-on-the-sphere legs; the corner is a tangent arc in the planform - no loft, no twist).
     d = 0 is the great circle (reproduces _template.py exactly when e = +1). The route is chosen from the measured
     RAGLAN MAP (mode `map`): for every direction in the link's own frame, the share of closing poses that keep it
     within one 12 mm band (the "ceiling" of the skin-motion map, computed in the moving link frame instead of the
     scapula / humerus frame).

Every part as the kit's template: flat O20 hubs with the 12.25 stack (K4), 12 x 3 straps with the 60 deg climb limit
(K5), the K7 neck to BOTTOM's bar from the arm-end hub, link 2 over link 1 and the neck (K6 by construction), K3
march, K2 dense continuity, K6 collisions, the kit's honesty audit.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/raglan-routed-3r.py [check|parity|map] ['<json params>']
"""
import itertools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "raglan-routed-3r"
NAME = "Raglan-routed 3R on far-end hubs (posterior J1 line, links on the lines of least skin motion)"
PARAMS = dict(az=-24.0, el=4.0, a1=65.0, a2=65.0, wd=80.0, wa=-90.0, sigma=1, margin=10.0,
              e1=1, e2=1, e3=1,                       # hub ends on the axis lines (+1 / -1)
              r1t=0.5, r1d=0.0, r2t=0.5, r2d=0.0,     # link waypoints: fraction along, deg off the great circle (+ = n_ab side)
              width=12.0, t_link=3.0, q=1.0)


def routed_strap(name, a, b, t_w, d_w, joints, width=12.0, t=3.0, ramp_to=(), end_mm=K.HUB_R + 2.0, extra=None, **kw):
    """one rigid strap hub a -> W (-> W2) -> hub b (great-circle legs, constant section), every W fixed in the link frame:
    W = cos(d) slerp(a, b, t) + sin(d) n_ab. extra = (t2, d2): a second planform turn (t2 > t)"""
    a, b = K.unit(a), K.unit(b)
    wps = [(t_w, d_w)] + ([tuple(extra)] if extra is not None else [])
    wps = [(tt, dd) for tt, dd in sorted(wps) if abs(dd) >= 0.25]
    if not wps:
        return K.strap_member(name, a, b, joints, width=width, t=t, ramp_to=ramp_to, **kw), a + b
    ang = np.arccos(np.clip((a * b).sum(-1), -1, 1))[:, None]; n = K.unit(np.cross(a, b))
    W = []
    for tt, dd in wps:
        g = K.unit(np.sin((1 - tt) * ang) * a + np.sin(tt * ang) * b); dr = math.radians(dd)
        W.append(K.unit(math.cos(dr) * g + math.sin(dr) * n))
    nodes = [a] + W + [b]; legs = []
    for i in range(len(nodes) - 1):
        Dl = K.strap_dirs(nodes[i], nodes[i + 1], width=width); legs.append(Dl if i == 0 else Dl[:, 1:])
    D = np.concatenate(legs, 1); ns, nc = D.shape[1:3]
    n_end = int(math.ceil(end_mm / 2.0)) + 1; s = np.repeat(np.arange(ns), nc); ramps = []
    for (h, dz), m in zip(ramp_to, (s < n_end, s >= ns - n_end)):
        if h: ramps.append((m, h, dz))
    return K.Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=60.0,
                    ramps=ramps, strap=True, **kw), W[0]


def axes(F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    return p1, p2, p3, ok, margin


def build(B, F, p):
    p1, p2, p3, ok, margin = axes(F, p)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    e1, e2, e3 = (int(p.get(k, 1)) for k in ("e1", "e2", "e3"))
    h1, h2, h3 = e1 * p1, e2 * p2, e3 * p3                     # the hub ends (kinematics unchanged)
    hubs = [K.hub_member("hub1", h1, "J1"), K.hub_member("hub2", h2, "J2"), K.hub_member("hub3", h3, "J3")]
    w, t = p["width"], p["t_link"]
    x1 = (p["r1t2"], p["r1d2"]) if p.get("r1d2") is not None else None
    x2 = (p["r2t2"], p["r2d2"]) if p.get("r2d2") is not None else None
    L1, W1 = routed_strap("link1", h1, h2, p["r1t"], p["r1d"], ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), extra=x1)
    L2, W2 = routed_strap("link2", h2, h3, p["r2t"], p["r2d"], ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                          over=[("link1", 1.0), ("neck", 1.0)], extra=x2)
    neck = K.neck_member(F, h3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    for m, k in ((hubs[1], "qh2"), (L2, "ql2")):                 # per-part underside quantile (None = the global q): a part
        if p.get(k) is not None: m.q = float(p[k])               # placed lower turns the poses that lift it into contact poses
    res = K.closure_residual(p1, p3, p2, p["a1"], p["a2"])
    lk = [round(math.degrees(float(np.arccos(np.clip(np.median((x * y).sum(-1)), -1, 1)))), 1) for x, y in ((h1, h2), (h2, h3))]
    return K.Chain(members=hubs + [L1, L2, neck], ok=ok, q=q, joints=dict(J1=h1, J2=h2, J3=h3),
                   info=dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None, link_span_deg=lk))


# ---- the raglan map: which directions of each LINK's frame stay in one 12 mm band over the closing poses -------------
def window_share(R, n_all, w=12.0):
    """R (P, m) requirement per closing pose. Returns (ceiling, top, inf): ceiling = share of ALL n_all poses inside
    the best w-mm window (reachable with q < 1); top = share inside [max - w, max] (what a q = 1 underside gets: it sits
    at the max requirement); inf = share of closing poses whose ray never clears the skin (the cell then sits at 400 mm)"""
    C = np.zeros(R.shape[1]); Tp = np.zeros(R.shape[1]); Inf = (~np.isfinite(R)).mean(0)
    for j in range(R.shape[1]):
        v = np.sort(R[np.isfinite(R[:, j]), j])
        if not len(v): continue
        k = np.searchsorted(v, v + w, side="right"); C[j] = (k - np.arange(len(v))).max() / n_all
        Tp[j] = 0.0 if Inf[j] > 0 else float((v >= v[-1] - w).sum()) / n_all
    return C, Tp, Inf


def raglan_map(B, p, T=np.linspace(0.05, 0.95, 19), Dg=np.arange(-50.0, 50.1, 5.0)):
    F = K.frames(B); p1, p2, p3, ok, _ = axes(F, p)
    e1, e2, e3 = (int(p.get(k, 1)) for k in ("e1", "e2", "e3")); H = [e1 * p1, e2 * p2, e3 * p3]
    Pi = np.nonzero(ok)[0]; out = {}
    for li, (a, b) in enumerate(((H[0], H[1]), (H[1], H[2]))):
        a, b = a[Pi], b[Pi]; ang = np.arccos(np.clip((a * b).sum(-1), -1, 1))[:, None]; n = K.unit(np.cross(a, b))
        cells = []
        for tt in T:
            g = K.unit(np.sin((1 - tt) * ang) * a + np.sin(tt * ang) * b)
            for dd in Dg:
                cells.append(K.unit(math.cos(math.radians(dd)) * g + math.sin(math.radians(dd)) * n))
        Dc = np.stack(cells, 1)                                  # (P, m, 3)
        I = np.repeat(Pi, Dc.shape[1]); R = K.requirement(B, I, Dc.reshape(-1, 3)).reshape(len(Pi), -1)
        C, Tp, Inf = (x.reshape(len(T), len(Dg)) for x in window_share(R, len(B.idx)))
        med = np.median(np.where(np.isfinite(R), R, 400), 0).reshape(len(T), len(Dg))
        out[f"link{li + 1}"] = dict(t=list(map(float, T)), d=list(map(float, Dg)), ceiling=np.round(C, 3).tolist(), top=np.round(Tp, 3).tolist(),
                                    inf=np.round(Inf, 3).tolist(), median_mm=np.round(med, 1).tolist(), span_deg=round(float(np.degrees(np.median(ang))), 1))
    return out


def best_route(M, link, key="top", step_deg=2.0):
    """the waypoint (t, d) whose two legs (sampled every step_deg of arc, nearest map cell) have the highest mean `key`
    share (top: a q = 1 underside); the hub zones (first / last 8 % of the span) are left out"""
    T, Dg, C = np.array(M[link]["t"]), np.array(M[link]["d"]), np.array(M[link][key]); A = M[link]["span_deg"]
    def c_at(t, d): return float(C[int(np.clip(np.rint((t - T[0]) / (T[1] - T[0])), 0, len(T) - 1)), int(np.clip(np.rint((d - Dg[0]) / (Dg[1] - Dg[0])), 0, len(Dg) - 1))])
    def route(tw, dw):
        v = []
        for (t0, d0), (t1, d1) in (((0.0, 0.0), (tw, dw)), ((tw, dw), (1.0, 0.0))):
            L = math.hypot((t1 - t0) * A, d1 - d0); n = max(2, int(L / step_deg))
            for x in np.linspace(0, 1, n, endpoint=False):
                t = t0 + (t1 - t0) * x
                if 0.08 <= t <= 0.92: v.append(c_at(t, d0 + (d1 - d0) * x))
        return float(np.mean(v)) if v else 0.0
    best = max(((route(tw, dw), float(tw), float(dw)) for tw in T for dw in Dg), key=lambda z: z[0])
    return dict(key=key, route=round(best[0], 3), t=best[1], d=best[2], great_circle=round(route(0.5, 0.0), 3))


_FS = {}
def fs():
    """the verified fold-sph3r checks (crown / wall skin check, near-touch, overhead, red team, frozen big bench), reused"""
    if not _FS:
        import importlib.util
        sp = importlib.util.spec_from_file_location("fold_sph3r_checks", os.path.join(REPO, "docs/concepts/models/fold-sph3r.py"))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        m.build = build; m.evaluate = evaluate; m.ID = ID; m.PARAMS = PARAMS; _FS["m"] = m
    return _FS["m"]


def clean(params):
    p = dict(PARAMS); p.update(params or {})
    p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    for k in ("e1", "e2", "e3"): p[k] = 1 if float(p.get(k, 1)) >= 0 else -1
    for k in ("r1t", "r2t", "r1t2", "r2t2"):
        if p.get(k) is not None: p[k] = min(0.9, max(0.1, float(p[k])))     # the turns stay between the hubs
    for k in ("r1d", "r2d", "r1d2", "r2d2"):
        if p.get(k) is not None: p[k] = min(60.0, max(-60.0, float(p[k])))
    p["width"] = max(8.0, float(p["width"]))
    for k in ("qh2", "ql2"):
        if p.get(k) is not None: p[k] = min(1.0, max(0.8, float(p[k])))                               # 8 x 3 mm Ti strap is the narrowest used (osn)
    return p


def evaluate(B, params):
    """tools/concept_cma.py hook: (params, report); the fold-sph3r crown / wall check, near-touch and overhead included"""
    p = clean(params); r = K.evaluate(B, build, p); r = fs().extras(B, r)
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params); return {k: v for k, v in r.items() if fs()._jsonable(v)}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = dict(PARAMS); par.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    B = K.bench(60, 160); t0 = time.time()
    if mode == "parity":                                     # e = +1, d = 0 must equal the template
        import importlib.util
        sp = importlib.util.spec_from_file_location("tpl", os.path.join(REPO, "docs/concepts/models/_template.py")); T = importlib.util.module_from_spec(sp); sp.loader.exec_module(T)
        for q in (0.95, 1.0):
            a = K.evaluate(B, T.build, dict(T.PARAMS, q=q)); b = K.evaluate(B, build, dict(PARAMS, **{k: T.PARAMS[k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "margin")}, q=q))
            print(q, {k: (a[k], b[k]) for k in ("gap", "reach", "inband14", "contact")})
        sys.exit()
    if mode == "map":
        M = raglan_map(B, par); M["params"] = par
        M["routes"] = {k: [best_route(M, k, "top"), best_route(M, k, "ceiling")] for k in ("link1", "link2")}
        print(json.dumps(M["routes"]), f"{time.time() - t0:.0f}s")
        json.dump(M, open(sys.argv[3] if len(sys.argv) > 3 else "/dev/stdout", "w"))
        sys.exit()
    if mode == "frozen":                                      # CB_EXACT=1: fit on Bench(60,160), freeze, wear on Bench(110,360) exact
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        fs().frozen(clean(par), o); sys.exit()
    p, r = evaluate(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "inband_member", "link_span_deg", "mass_g",
                                 "honest", "audit", "crown_contact_poses", "crown_min", "min_metal_skin", "gap_near1", "overhead")}, f"{time.time() - t0:.0f}s")
    if mode == "redteam": fs().redteam(B, p, r)
