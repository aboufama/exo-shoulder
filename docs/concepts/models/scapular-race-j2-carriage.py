"""scapular-race-j2-carriage: J1 is a scapula-fixed arc RAIL (a race about axis a1 through GH) and the J2 O20 hub rides its
carriage; one strap L2 to the arm-end J3 hub; neck to BOTTOM (3 ACTIVE DOF, 0 passive). Spec: docs/concepts/catalogue.json
entry "scapular-race-j2-carriage"; write-up docs/concepts/scapular-race-j2-carriage.md. Built on tools/concept_kit.py.

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    base (scapula handler) + RAIL (fixed): the circle at polar angle gamma about a1 (scapula-fixed), at ONE distance R from
        GH (a rigid carriage rolling about a1 can only run on a surface of revolution about a1); 10 wide x 4 radial;
        spans the J1 travel used + half a carriage + a 3 mm end stop at each end.
    -- J1: the carriage (26 long x 22 wide x 8 radial, V-rollers on both rail edges) rolls on the rail; its azimuth phi
        about a1 is the J1 joint value. No hub and no metal at a1's pole.
    -- J2: O20 hub on the carriage, axis u2 = the carriage's own direction from GH (so alpha12 = gamma); the carriage is
        its lower member (the O20 lower plate = the carriage's top 3 mm: hub F = R + 5), L2 its upper member (R + 8.15).
    -> L2 = strap (12 x 3) on the great circle u2 -> p3, skin-fitted underside (K3), over the race where it crosses it.
    -- J3: O20 hub, axis p3 = wdir(wd, wa) fixed in the humerus (band frame, as the kit); lower member = arm-end plate
    -> neck (14 x 6) to BOTTOM's bar (K7).
DOF: phi (J1), q2, q3 from the two-circle closure of a1 and p3 with arcs gamma, alpha23 on branch sigma: a spherical 3R
whose first bearing is spread along a circle. 3 active, 0 passive, nothing undetermined.

Members (every part at real size, kit sampling): race = the rail (10 wide x 4, 5 rows on a 2 mm grid, scapula-fixed)
+ the carriage's V-roller strips (5..9 mm either side of the rail centre, +-8 mm along, moving) at ONE radius R (kind cap);
hub2 = the carriage plate = the J2 O20 lower plate (flat disc, F = R + 4.5: 0.5 mm over the rail top), crown F + 12.25;
link2 = 12 x 3 strap, ramps to hub2 / hub3 + 3.15 over its first / last 16 mm, `over` the race and the neck (+1 mm);
hub3 (O20, arm); neck (K7). link2 is listed first so K6 measures its pairs at link2's radius, as `over` builds them.

Design step (outside build, so build stays pose-local): `travel()` takes the carriage azimuths of the closing bench
poses -> the J1 range [phi_lo, phi_hi] (central share cov, + tmarg) and the rail extent. Poses outside it are not taken.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/scapular-race-j2-carriage.py check [k=v ...]
"""
import json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "scapular-race-j2-carriage"
NAME = "Scapular race: J1 is a rail on the bony rim and J2 rides its carriage"
D2R = math.pi / 180
RAIL_W, RAIL_T = 10.0, 4.0
CAR_L, CAR_W, CAR_T = 26.0, 22.0, 8.0
END_STOP = 3.0
J2_F = CAR_T - 3.0                                           # O20 lower plate = the carriage's top 3 mm
STEM_W = 6.0

# spec seed: a1 = sdir(0, 20) = bvec(70, 0), gamma 50, alpha23 80, J3 ~20 deg off the arm axis, posterolateral
PARAMS = dict(az1=70.0, el1=0.0, gamma=50.0, a23=80.0, wd=86.3, wa=21.8, sigma=1, margin=8.0, q=0.95, rmax=70.0, tmarg=3.0,
              r_lay=55.0, q_l2=None)


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


def race_frame(p):
    """scapula-frame unit vectors: a1 (race axis), m (phi 0: towards scapula +y, or +x if a1 ~ vertical), n = a1 x m"""
    a1 = K.bvec(p["az1"], p["el1"]); ref = np.array([0.0, 1.0, 0.0]) if abs(a1[1]) < 0.95 else np.array([1.0, 0, 0])
    m = K.unit(ref - (ref @ a1) * a1); n = np.cross(a1, m); return a1, m, n


def kin(F, p):
    a1s, ms, ns = race_frame(p)
    A1 = F.S(a1s); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    u2, ok, margin = K.closure(A1, p3, p["gamma"], p["a23"], p["sigma"], margin_deg=p["margin"]); u2 = K.unit(u2)
    phi = np.degrees(np.arctan2((u2 * F.S(ns)).sum(-1), (u2 * F.S(ms)).sum(-1)))
    return A1, u2, p3, ok, margin, phi


def travel(B, F, p):
    """design step (uses the skin, outside build): lay the rail only over QUIET stations - those whose skin requirement
    (K3 march along the rail's centre ray, quantile q over the closing poses) is <= rmax - and pick the contiguous run of
    quiet stations that holds the most closing-pose carriage azimuths (+- half a carriage + end stop). Returns the J1 range
    (centre phi_c, relative phi_lo / phi_hi: the carriage centre's travel) and the run's measured worst requirement."""
    *_, ok, _, phi = kin(F, p)
    if ok.sum() < 5: return dict(phi_c=0.0, phi_lo=-0.5, phi_hi=0.5, rail_req=None)
    a1, m, n = race_frame(p); g = p["gamma"] * D2R; st = np.arange(-180.0, 180.0, 2.0)
    Ds = np.cos(g) * a1 + np.sin(g) * (np.cos(st * D2R)[:, None] * m + np.sin(st * D2R)[:, None] * n)
    Pi = np.nonzero(ok)[0]; D = F.S(Ds)[Pi]                                    # (n, 180, 3)
    R = K.requirement(B, np.repeat(Pi, len(st)), D.reshape(-1, 3)).reshape(len(Pi), len(st))
    need = K.quantile(R, p["q"]); quiet = need <= p["rmax"]
    e = (CAR_L / 2 + END_STOP) / (p["r_lay"] * math.sin(g)) / D2R              # deg of rail beyond the carriage centre
    ph = phi[ok]; best = None
    if quiet.all():
        runs = [(0, len(st))]
    else:
        k0 = int(np.argmin(quiet)); qq = np.roll(quiet, -k0); runs = []; i = 0                 # runs on the circle
        while i < len(st):
            if qq[i]:
                j = i
                while j < len(st) and qq[j]: j += 1
                runs.append(((i + k0) % len(st), j - i)); i = j
            else: i += 1
    for s0, L in runs:
        lo = st[s0] - 1.0; hi = lo + 2.0 * L                                      # run [lo, hi] deg (station cells)
        if hi - lo >= 360: lo, hi = -180.0, 180.0
        clo, chi = lo + e, hi - e                                                 # carriage centre travel
        if chi <= clo: continue
        c = 0.5 * (clo + chi); r = wrap(ph - c); inside = (r >= clo - c) & (r <= chi - c)
        cnt = int(inside.sum())
        if best is None or cnt > best[0]:
            if inside.any():
                tl, th = float(r[inside].min()), float(r[inside].max())          # trim to the travel actually used
                best = (cnt, c, max(tl - p["tmarg"], clo - c), min(th + p["tmarg"], chi - c), float(need[[(s0 + k) % len(st) for k in range(L)]].max()))
    if best is None: return dict(phi_c=0.0, phi_lo=-0.5, phi_hi=0.5, rail_req=None)
    return dict(phi_c=round(best[1], 3), phi_lo=round(best[2], 3), phi_hi=round(best[3], 3), rail_req=round(best[4], 1))


def rail_dirs(p):
    """scapula-frame directions of the rail samples (m, 3), a mask of the outer rows, grid, span (deg), length (mm at r_lay)"""
    a1, m, n = race_frame(p); g = p["gamma"] * D2R; RL = p["r_lay"]; rr = RL * math.sin(g)
    e = (CAR_L / 2 + END_STOP) / rr
    lo = (p["phi_c"] + p["phi_lo"]) * D2R - e; hi = (p["phi_c"] + p["phi_hi"]) * D2R + e
    if hi - lo >= 2 * math.pi: lo, hi = -math.pi, math.pi - 2.0 / rr      # full ring
    ns = max(3, int(math.ceil((hi - lo) * rr / 2.0)) + 1); st = np.linspace(lo, hi, ns)
    ac = np.arange(-RAIL_W / 2 + 1, RAIL_W / 2, 2.0)           # -4 -2 0 2 4: 5 rows over 10 mm
    pol = g + ac / RL
    PH, PO = np.meshgrid(st, pol, indexing="ij")
    D = (np.cos(PO)[..., None] * a1 + np.sin(PO)[..., None] * (np.cos(PH)[..., None] * m + np.sin(PH)[..., None] * n)).reshape(-1, 3)
    edge = np.broadcast_to(np.abs(ac) > STEM_W / 2, PH.shape).ravel()
    return K.unit(D), edge, (ns, len(ac)), (hi - lo) / D2R, (hi - lo) * rr


def build(B, F, p):
    A1, u2, p3, ok, margin, phi = kin(F, p)
    rel = wrap(phi - p["phi_c"]); ok = ok & (rel >= p["phi_lo"]) & (rel <= p["phi_hi"])        # J1 range = the rail
    q = np.stack([phi, K.axis_angle(u2, A1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), u2)], -1)
    P = len(u2); RL = p["r_lay"]
    Ds, edge, grid, span, _ = rail_dirs(p); Dr = F.S(Ds)                                      # (P, mr, 3) scapula-fixed rail
    tdir = K.unit(np.cross(A1, u2)); pdir = np.cross(u2, tdir)                                 # carriage frame (along, across)
    # V-rollers (2 per side, 5 mm OD) hang beside the rail head down to R: the strips 5..9 mm either side of the rail
    # centre, +-8 mm along (all within HUB_R + 2 of J2, the carriage is one body with the J2 lower plate)
    cx = np.arange(-8.0, 8.01, 2.0) / RL; cy = np.array([-8.0, -6.0, 6.0, 8.0]) / RL
    X, Y = np.meshgrid(cx, cy, indexing="ij"); X, Y = X.ravel(), Y.ravel()
    Dc = K.unit(u2[:, None] + X[None, :, None] * tdir[:, None] + Y[None, :, None] * pdir[:, None])
    rails = [K.Member("race", np.concatenate([Dr, Dc], 1), kind="cap", t=RAIL_T, width=RAIL_W, joints=("J1", "J2"), r_ref=RL, cell=4.0)]
    # J2 O20 hub = the carriage plate (its lower member), riding 0.5 mm over the rail top: F = R + 4.5
    hub2 = K.hub_member("hub2", u2, "J2", ref=tdir); hub2.ramps = [(np.ones(len(hub2.xy), bool), "race", RAIL_T + 0.5)]
    hub3 = K.hub_member("hub3", p3, "J3")
    l2 = K.strap_member("link2", u2, p3, ("J2", "J3"), ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)), end_mm=16.0,
                        over=[("race", 1.0), ("neck", 1.0)], q=p.get("q_l2"))
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    res = K.closure_residual(A1, p3, u2, p["gamma"], p["a23"])
    return K.Chain(members=[l2] + rails + [hub2, hub3, neck],   # l2 first: K6 then measures its pairs at l2's radius, as the kit's `over` construction does
                   ok=ok, q=q, joints=dict(J1=A1, J2=u2, J3=p3), hubless=("J1",),
                   info=dict(residual_deg=round(float(res[ok].max()), 6) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             rail_span_deg=round(span, 1)))


def full(B, p):
    p = dict(PARAMS, **p); F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    p.update(travel(B, F, p)); return p


def evaluate(B, params, **kw):
    """design step + kit evaluate -> (full params, report). r_lay (the layout radius of the rail and roller samples) is a
    fix point at the fitted race radius R: R - 1.5 <= r_lay <= R + 0.25 (at most 2 re-runs at floor(R)); r_lay > R draws
    the rail narrower than 10 mm and its end stops shorter (optimistic: the red team found the first CMA exploiting a
    +1.5 mm tolerance, 78.04 -> 80.78), r_lay << R a wider rail than the real one. tools/concept_cma.py calls this."""
    p = dict(PARAMS, **params)
    for it in range(3):
        p = full(B, p)
        if p["phi_hi"] - p["phi_lo"] < 2.0:                   # no quiet rail run holds any closing pose
            B.reset(); r = B.report(); r.update(honest=True, audit=[], note="no quiet rail run", closure=None); return p, r
        r = K.evaluate(B, build, p, **kw); R = race_radius(B)
        if R is None or (p["r_lay"] <= R + 0.25 and p["r_lay"] >= R - 1.5) or it == 2: break
        p = dict(p, r_lay=float(math.floor(R)))
    if R is not None and p["r_lay"] > R + 0.25:
        r["honest"] = False; r["audit"] = list(r.get("audit", [])) + [f"rail laid out at {p['r_lay']} > fitted R {R}"]
    L = B._kit_last
    r.update(race_R=R, r_lay=p["r_lay"], phi_c=p["phi_c"], phi_lo=p["phi_lo"], phi_hi=p["phi_hi"], rail_req=p.get("rail_req"),
             levels=levels(B))
    return p, r


def bench_eval(B, params):
    """farm hook (tools/concept_sweep.py): the report of evaluate()"""
    p, r = evaluate(B, params)
    return {k: v for k, v in r.items() if _jsonable(v)}


def _jsonable(v):
    try: json.dumps(v); return True
    except (TypeError, ValueError): return False


def race_radius(B):
    L = B._kit_last; return round(float(L["prof"]["race"].max()), 2) if "race" in L["prof"] else None


def levels(B):
    L = B._kit_last; out = {}
    for name, pr in L["prof"].items(): out[name] = [round(float(np.min(pr)), 1), round(float(np.median(pr)), 1), round(float(np.max(pr)), 1)]
    return out


def reach_bound(B, n=24000, seed=2, q=0.95, rmaxs=(65.0, 70.0, 75.0, 80.0, 90.0, 100.0, 115.0, 130.0)):
    """the morphology's ceiling from the raw skin, no part but the rail modelled: K3 march along every scapula-fixed
    direction (3 deg grid) in every bench pose -> per-direction q-quantile requirement. For n random designs (a1, gamma,
    alpha23, J3 axis, branch, rmax) the J2 axis must land on the best contiguous run of rail stations whose requirement
    is <= rmax (+- half a carriage + end stop): an UPPER bound on reach / follow (hubs, L2, K2, K6 ignored), and the
    rail's in-band ceiling at one radius R = max need over the run vs. at a per-station radius (a cam / skin-milled web)."""
    F = K.frames(B); P = len(F.RS)
    AZ, EL = np.meshgrid(np.arange(0, 360, 3.0), np.arange(-42, 90.1, 3.0), indexing="ij"); U = K.bvec(AZ.ravel(), EL.ravel())
    R = K.requirement(B, np.repeat(np.arange(P), len(U)), F.S(U).reshape(-1, 3)).reshape(P, len(U)); R[~np.isfinite(R)] = 400.0
    NEED = np.quantile(R, q, axis=0); ci = np.nonzero(F.clip)[0]

    def cell(u):
        el = np.degrees(np.arcsin(np.clip(u[..., 1], -1, 1))); az = np.degrees(np.arctan2(u[..., 2], -u[..., 0])) % 360
        return (np.round(az / 3).astype(int) % 120) * 45 + np.clip(np.round((el + 42) / 3).astype(int), 0, 44)
    rng = np.random.default_rng(seed); st = np.arange(-180, 180, 2.0) * D2R; out = []
    for _ in range(n):
        az1, el1, g, a23 = rng.uniform(0, 360), rng.uniform(-20, 90), rng.uniform(15, 85), rng.uniform(40, 120)
        wd, wa, sg, rmax = rng.uniform(10, 120), rng.uniform(-180, 180), int(rng.choice([-1, 1])), float(rng.choice(rmaxs))
        a1, m, nn = race_frame(dict(az1=az1, el1=el1)); gr = g * D2R
        Ds = math.cos(gr) * a1 + math.sin(gr) * (np.cos(st)[:, None] * m + np.sin(st)[:, None] * nn); cs = cell(Ds)
        quiet = NEED[cs] <= rmax; best = (0.0, 0.0, 0.0, 0.0, 0.0)
        if quiet.any():
            u2, ok, _ = K.closure(F.S(a1), F.HG(K.wdir(wd, wa)), g, a23, sg, margin_deg=8.0)
            u2s = np.einsum("pji,pj->pi", F.RS, u2); phi = np.degrees(np.arctan2(u2s @ nn, u2s @ m))
            e = (CAR_L / 2 + END_STOP) / (60 * math.sin(gr)) / D2R
            k0 = int(np.argmin(quiet)) if not quiet.all() else 0; qq = np.roll(quiet, -k0); runs = []; i = 0
            while i < 180:
                if qq[i]:
                    j = i
                    while j < 180 and qq[j]: j += 1
                    runs.append(((i + k0) % 180, j - i)); i = j
                else: i += 1
            for s0, L in runs:
                lo = -180 + 2 * s0 - 1 + e; span = 2 * L - 2 * e
                if span <= 0: continue
                inside = ok.copy() if L == 180 else ok & (((phi - lo) % 360) <= span)
                rw, rc = float(inside[F.ws].mean()), float(inside[F.clip].mean())
                if rw + rc > best[0] + best[1]:
                    idx = cs[[(s0 + k) % 180 for k in range(L)]]; nd = NEED[idx]; Rc = R[np.ix_(ci, idx)]
                    best = (rw, rc, float(((Rc >= nd.max() - 12) & (Rc <= nd.max())).mean()), float(((Rc >= nd - 12) & (Rc <= nd)).mean()), float(nd.max()))
        out.append(dict(reach=round(best[0], 4), follow=round(best[1], 4), band_const=round(best[2], 3), band_cam=round(best[3], 3),
                        R=round(best[4], 1), az1=round(az1, 2), el1=round(el1, 2), gamma=round(g, 2), a23=round(a23, 2), wd=round(wd, 2),
                        wa=round(wa, 2), sigma=sg, rmax=rmax))
    return out


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160)
    if a[0] == "check":
        ov = {k: (int(v) if k in ("sigma",) else float(v)) for k, v in (x.split("=") for x in a[1:] if "=" in x)}
        r = bench_eval(B, dict(PARAMS, **ov))
        print(json.dumps({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                                "inband_member", "mass_g", "honest", "audit", "rail_span_deg", "race_R", "r_lay",
                                                "phi_lo", "phi_hi", "rail_req", "residual_deg", "levels")}))
    elif a[0] == "bound":            # the ceiling from the raw skin (docs/concepts/scapular-race-j2-carriage.md)
        out = reach_bound(B, n=int(a[1]) if len(a) > 1 else 24000)
        for rm in sorted({o["rmax"] for o in out}):
            s = [o for o in out if o["rmax"] == rm]; b = max(s, key=lambda o: o["reach"])
            print(f"rmax {rm:5.0f}: n {len(s)}  reach bound {b['reach']:.3f} (follow {b['follow']:.3f}, rail R {b['R']}, rail in band at one R "
                  f"{b['band_const']:.3f}, per-station {b['band_cam']:.3f})  best follow {max(o['follow'] for o in s):.3f}")
