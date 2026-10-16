"""j2-arc-sector-3r: spherical 3R whose J2 is a link-1 ARC-RAIL SECTOR with a link-2 V-roller CARRIAGE (no J2 hub, no
metal at the J2 axis point). Catalogue id j2-arc-sector-3r; write-up docs/concepts/j2-arc-sector-3r.md. Built on
tools/concept_kit.py; crown / near-touch / overhead checks and the frozen big-bench run reused from
docs/concepts/models/fold-sph3r.py.

Topology (scapula handler -> user's upper-arm cuff), every joint axis through GH:
    base -> J1 ACTIVE R: O20 hub, axis p1 = S @ bvec(az, el) (scapula-fixed)
    -> link 1 (12 x 3 Ti strap, great circle p1 -> the rail's tab) + the RAIL SECTOR (rigid with link 1)
    -> J2 ACTIVE R about the virtual axis p2 (two-circle closure, arcs a1 / a2): the rail is a conical V-edge ring
       sector about p2 at cone half-angle beta, its running edges circles about p2, its underside at ONE distance rho
       from GH (a surface of revolution about p2 - the only surface a rigid carriage rolling about p2 can ride; it is a
       lathe-turned constant section revolved about p2, no loft); 8 wide x 4 thick; the spec's flat ring (normal p2)
       is its beta-tilted special case and sits up to 8 sin(beta) mm proud across its width, so the cone is used
       (improvement, stated in the write-up). The CARRIAGE is rigid with link 2: 4 V-rollers (MR63ZZ, OD 6) beside the
       rail edges (strips 4..10 mm from the rail centre line, 16 mm long, same level as the rail underside, 4 mm tall)
       + a 20 x 16 x 4 plate at rail + 4.5 (rail top + 0.5 running gap): 8.5 mm over the rail underside in all.
       J2's value is the carriage azimuth: psi_c = theta2 + chi; travel |psi_c - pc| <= pw (end stops); the rail spans
       the travel + half a carriage + a 3 mm stop each side + an 8 mm tab where link 1 laps onto it (side s1).
    -> link 2 (12 x 3 strap, great circle carriage -> p3), bolted on the carriage plate, over the rail / link 1 / neck
    -> J3 ACTIVE R: O20 hub, axis p3 = HG @ wdir(wd, wa) (humerus-fixed) -> K7 neck (14 x 6) -> BOTTOM -> cuff.
Option over_hub1=1: the rail (and its rollers) rides over hub 1's crown (2.2 mm over the crown plane: 1 mm at the crown edge as K6 measures it) (one level for the whole rail), for
layouts whose rail passes over hub 1 (a1 - beta < ~22 deg).
Option wp=1: link 2 is two great-circle straps (carriage -> waypoint -> hub 3) with a planform turn at a waypoint
fixed in link 2's frame (azimuth w_psi from p3 about p2, w_beta off p2); the two straps are one rigid part (exempt from
each other within 12 mm of the waypoint, pseudo-joint Wl2). No loft.
K6 zones (Chain.joints, declared hubless): Wcar = the carriage centre (shared by rail, carriage plate, link 2: the
running pair and the bolted carriage-link 2 body are exempt within HUB_R + 2 = 12 mm of it, which covers the whole
20 x 16 footprint: its farthest samples are 11.4 mm out). Everywhere else every pair is checked; by construction the
plate is 0.6 mm over the rail top, link 1 1.1 mm over the rail (it laps onto the tab on a 1.1 mm shim, so the 1 mm
radial K6 of the big-bench run holds too), link 2 0.6 mm over the plate and 1 mm over the rail, link 1 and the neck.
DOF: theta1, theta2 (= the carriage on its rail), theta3; 3 active, 0 passive, 0 passive translations, nothing
undetermined (the carriage is preloaded on 2 eccentric rollers; it has no free coordinate).

Design step (evaluate(), outside build so build stays pose-local): the rail travel [pc - pw, pc + pw] is the central
`cov` share of the carriage azimuths over the poses the chain closes in on the bench it is fitted on; frozen with the
other parameters for the big bench.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/j2-arc-sector-3r.py [check|redteam|control] ['<json>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/j2-arc-sector-3r.py frozen '<json params>' --out R.json
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

_spec = importlib.util.spec_from_file_location("fold_sph3r", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fold-sph3r.py"))
FS = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(FS)   # crowns, near-touch, overhead, hub control

ID = "j2-arc-sector-3r"
NAME = "Spherical 3R with J2 as a link-1 arc-rail sector and a link-2 roller carriage (no J2 hub)"
D2R = math.pi / 180
RAIL_W, RAIL_T = 8.0, 4.0                                    # rail section (V edges ground on both sides)
CAR_L, CAR_W = 16.0, 20.0                                    # carriage footprint (along x across)
ROLL_IN, ROLL_T = 4.0, 4.0                                   # roller strips from |y| 4 to 10, 4 mm tall
PLATE_DZ, PLATE_T = 4.6, 4.0                                 # plate underside over the rail underside (rail top + 0.6), thickness
STOP, TAB = 3.0, 8.0
# spec first run (catalogue model_spec): bvec(95.86, 65.21), a1 60 / a2 80, wdir(79.15, -13.37), R 30 at 52 -> beta 30
PARAMS = dict(az=95.8565, el=65.2093, a1=60.0, a2=80.0, wd=79.148, wa=-13.3653, sigma=1, margin=10.0, beta=30.0,
              chi=90.0, cov=0.98, pc=None, pw=None, s1=-1, r_lay=60.0, width=12.0, t_link=3.0, q=0.98,
              wp=0, w_psi=0.0, w_beta=50.0, over_hub1=0)   # wp=1: link 2 turns at a waypoint (w_psi from p3's azimuth, w_beta off p2) in its own frame


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


def kin(F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], 1 if float(p["sigma"]) >= 0 else -1, margin_deg=p["margin"])
    e1 = K.unit(p1 - (p1 * p2).sum(-1, keepdims=True) * p2); e2 = np.cross(p2, e1)
    th2 = K.axis_angle(p2, p1, p3); psi_c = wrap(th2 + p["chi"])
    return p1, p2, p3, e1, e2, ok, margin, th2, psi_c


def cone_dirs(p2, e1, e2, psi_deg, b_deg):
    """unit directions at azimuth psi (P, n) about p2 and polar angle b (n,) or (P, n): (P, n, 3)"""
    ps, b = np.asarray(psi_deg, float) * D2R, np.broadcast_to(np.asarray(b_deg, float) * D2R, np.shape(psi_deg))
    return K.unit(np.cos(b)[..., None] * p2[:, None] + np.sin(b)[..., None] * (np.cos(ps)[..., None] * e1[:, None] + np.sin(ps)[..., None] * e2[:, None]))


def rail_extent(p):
    """rail sector [lo, hi] (deg about p2) and the tab centre azimuth, at the layout radius"""
    rc = p["r_lay"] * math.sin(p["beta"] * D2R); ext = (CAR_L / 2 + STOP) / rc / D2R; tab = TAB / rc / D2R
    lo, hi = p["pc"] - p["pw"] - ext, p["pc"] + p["pw"] + ext
    if p["s1"] < 0: lo -= tab; tc = lo + tab / 2
    else: hi += tab; tc = hi - tab / 2
    return lo, hi, tc, rc


def build(B, F, p):
    p1, p2, p3, e1, e2, ok, margin, th2, psi_c = kin(F, p)
    ok = ok & (np.abs(wrap(psi_c - p["pc"])) <= p["pw"])                       # J2 travel (end stops)
    n = len(p1); lo, hi, tc, rc = rail_extent(p); rl = p["r_lay"]
    # rail: rows across (polar angle) every 2 mm, columns along every 2 mm, at the layout radius
    acr = np.arange(-RAIL_W / 2, RAIL_W / 2 + 1e-6, 2.0); b_rows = p["beta"] + acr / rl / D2R
    along = np.linspace(lo, hi, max(3, int(round((hi - lo) * D2R * rc / 2.0)) + 1))
    PS, BB = np.meshgrid(along, b_rows, indexing="ij"); PS, BB = PS.ravel(), BB.ravel()
    Dr = cone_dirs(p2, e1, e2, np.broadcast_to(PS, (n, len(PS))), BB)
    # carriage: roller strips beside the rail (|y| 5, 7, 9), and the plate over the whole footprint
    xs = np.arange(-CAR_L / 2 + 1, CAR_L / 2, 2.0)
    ys_r = np.array([-9.0, -7.0, -5.0, 5.0, 7.0, 9.0]); ys_p = np.arange(-CAR_W / 2 + 1, CAR_W / 2, 2.0)
    def carr(ys):
        X, Y = np.meshgrid(xs, ys, indexing="ij"); X, Y = X.ravel(), Y.ravel()
        return cone_dirs(p2, e1, e2, psi_c[:, None] + X[None, :] / rc / D2R, p["beta"] + Y / rl / D2R)
    Dj = np.concatenate([Dr, carr(ys_r)], 1)
    j2 = K.Member("j2", Dj, kind="cap", t=RAIL_T, width=RAIL_W, joints=("J2", "Wcar"), r_ref=rl, cell=4.0,
                  ramps=[(np.ones(Dj.shape[1], bool), "hub1", K.CROWN + 2.2)] if p.get("over_hub1") else [])   # rail + rollers ride over hub 1's crown (+2.2: K6 measures the crown edge radially, sqrt(F^2 + 10^2))
    plate = K.Member("carplate", carr(ys_p), kind="cap", t=PLATE_T, width=CAR_W, joints=("J2", "Wcar"), r_ref=rl, cell=4.0,
                     ramps=[(np.ones(len(xs) * len(ys_p), bool), "j2", PLATE_DZ)])
    u_tab = cone_dirs(p2, e1, e2, np.full((n, 1), tc), np.array([p["beta"]]))[:, 0]
    u_car = cone_dirs(p2, e1, e2, psi_c[:, None], np.array([p["beta"]]))[:, 0]
    w, t = p["width"], p["t_link"]
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub3", p3, "J3")]
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    link1 = K.strap_member("link1", p1, u_tab, ("J1",), width=w, t=t, ramp_to=(("hub1", K.STACK), ("j2", RAIL_T + 1.1)),
                           over=[("j2", 1.1), ("carplate", 1.0)])   # bridges over the carriage path where it crosses it                                   # laps onto the rail tab, bolted on top
    link2 = K.strap_member("link2", u_car, p3, ("J2", "J3", "Wcar"), width=w, t=t, ramp_to=(("carplate", PLATE_T + 0.6), ("hub3", K.STACK)),
                           over=[("link1", 1.0), ("neck", 1.0), ("j2", 1.0), ("carplate", 0.6)])
    joints = dict(J1=p1, J2=p2, J3=p3, Wcar=u_car); extra = []
    if p.get("wp"):     # link 2 as two great-circle segments with a planform turn at a waypoint fixed in link 2's frame
        u_w = cone_dirs(p2, e1, e2, (th2 + p["w_psi"])[:, None], np.array([p["w_beta"]]))[:, 0]
        link2 = K.strap_member("link2", u_car, u_w, ("J2", "Wcar", "Wl2"), width=w, t=t, ramp_to=(("carplate", PLATE_T + 0.6), (None, 0)),
                               over=[("link1", 1.0), ("neck", 1.0), ("j2", 1.0), ("carplate", 0.6)])
        extra = [K.strap_member("link2b", u_w, p3, ("J3", "Wl2"), width=w, t=t, ramp_to=((None, 0), ("hub3", K.STACK)),
                                over=[("link1", 1.0), ("neck", 1.0), ("j2", 1.0), ("carplate", 0.6)])]
        joints["Wl2"] = u_w
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), th2, K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    return K.Chain(members=[hubs[0], j2, plate, hubs[1], neck, link1, link2] + extra, ok=ok, q=q, joints=joints,
                   hubless=tuple(j for j in joints if j not in ("J1", "J3")),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             rail_deg=round(hi - lo, 1), rail_mm=round((hi - lo) * D2R * rc, 1), travel=[round(p["pc"] - p["pw"], 1), round(p["pc"] + p["pw"], 1)]))


def design(B, p):
    """rail travel = the central cov share of the carriage azimuths over the closing poses (circular, about their mean)"""
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    *_, ok, margin, th2, psi = kin(F, p)
    if not ok.any(): return dict(p, pc=0.0, pw=1.0)
    s = psi[ok] * D2R; c = math.degrees(math.atan2(np.sin(s).mean(), np.cos(s).mean()))
    d = wrap(psi[ok] - c); a = (1 - p["cov"]) / 2; lo, hi = np.quantile(d, a), np.quantile(d, 1 - a)
    pw = min(150.0, (hi - lo) / 2 + 1.0)
    return dict(p, pc=float(round(c + (hi + lo) / 2, 3)), pw=float(round(pw, 3)))


def tops(B, ch, prof, take):
    """rail top (+4) and carriage plate top skin check: a top inside the skin makes the pose a contact pose"""
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    if not len(Pi): return 0, None
    M = {m.name: m for m in ch.members}; X = []
    for nm in ("j2", "carplate"):
        m = M[nm]; rho = prof[nm][0]; X.append(m.D[Pi] * (rho + m.t))
    X = np.concatenate(X, 1); d = K.dist_many(B, np.repeat(Pi, X.shape[1]), X.reshape(-1, 3)).reshape(len(Pi), -1).min(1)
    for j, dd in zip(Pi, d):
        if dd < 0: B.res[j] = np.append(B.res[j], dd)
    return int((d < 0).sum()), round(float(d.min()), 2)


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["s1"] = 1 if float(p["s1"]) >= 0 else -1; p["beta"] = float(min(60.0, max(12.0, p["beta"])))
    if p.get("pc") is None or p.get("pw") is None or params.get("redesign", False): p = design(B, p)
    p.pop("redesign", None)
    r = K.evaluate(B, build, p)
    L = B._kit_last; nt, tmin = tops(B, L["chain"], L["prof"], L["take"])
    r = FS.extras(B, r); r.update(top_contact_poses=nt, top_min=tmin, level_j2=round(float(L["prof"]["j2"][0]), 1),
                                  level_hub1=round(float(L["prof"]["hub1"][0]), 1), level_hub3=round(float(L["prof"]["hub3"][0]), 1))
    return p, r


def bench_eval(B, params):
    p, r = evaluate(B, params)
    out = {k: v for k, v in r.items() if FS._jsonable(v)}; out["params_used"] = p
    return out


def control(B, p):
    """the hub version at IDENTICAL axes (fold-sph3r build: O20 hub at J2, straps p1 -> p2 -> p3)"""
    pc = {k: p[k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "margin", "q")}
    return FS.evaluate(B, pc)


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) (incl. the rail travel), freeze every underside, wear on Bench(big) (K6 at 1 mm radial)"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    Bf = K.bench(*fit); pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if FS._jsonable(v) and k not in ("checks",)}
    res["params_frozen"] = pf; res["runs"]["fit"] = dict(keep(rf), bench=list(fit)); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        _, r = evaluate(Bb, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead")}, flush=True)
    if "--redteam" in sys.argv: FS.redteam(Bb, pf, r)
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
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), "margin", r.get("min_margin"),
          "rail", r.get("rail_deg"), r.get("rail_mm"), "travel", r.get("travel"), "levels j2/hub1/hub3", r["level_j2"], r["level_hub1"], r["level_hub3"])
    print("crowns", r["crown_contact_poses"], r["crown_min"], "tops", r["top_contact_poses"], r["top_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("params", json.dumps({k: p[k] for k in p}))
    if mode == "redteam": FS.redteam(B, p, r)
    if mode == "control":
        _, rc = control(B, p)
        print("HUB CONTROL", {k: rc[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest")}, rc["inband_member"], "overhead", rc["overhead"])
