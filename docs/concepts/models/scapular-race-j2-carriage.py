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

Members (every part at real size, kit sampling): race = rail arc (2 mm grid, 10 wide) + carriage footprint (26 x 22,
2 mm grid) at ONE radius R (kind cap, t 8 = the carriage height, conservative for the 4 mm rail), hub2 (O20 flat disc,
ramped to R + 5), L2, hub3, neck. Variant stem=1: the rail is a T: its 10 mm head (running surface, with the rollers and
the carriage) stays at R, a 4 mm stem under it reaches down to its own skin-fitted level per station (scapula-fixed,
milled to the skin like the base) - the rail head edge rows stay at R.

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
STEM_W = 6.0                                                 # stem rows: the middle 3 of the 5 rail rows

# spec seed: a1 = sdir(0, 20) = bvec(70, 0), gamma 50, alpha23 80, J3 ~20 deg off the arm axis, posterolateral
PARAMS = dict(az1=70.0, el1=0.0, gamma=50.0, a23=80.0, wd=86.3, wa=21.8, sigma=1, margin=8.0, q=0.95, rmax=70.0, tmarg=3.0,
              r_lay=55.0, stem=0, q_l2=None)


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
    """scapula-frame directions of the rail samples (m, 3) and a mask of the head-edge rows (stem=1 keeps those at R)"""
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
    Ds, edge, grid, span, _ = rail_dirs(p); Dr = F.S(Ds)                                      # (P, mr, 3) scapula-fixed
    tdir = K.unit(np.cross(A1, u2)); pdir = np.cross(u2, tdir)                                 # carriage frame
    cx = np.arange(-CAR_L / 2 + 1, CAR_L / 2, 2.0) / RL; cy = np.arange(-CAR_W / 2 + 1, CAR_W / 2, 2.0) / RL
    X, Y = np.meshgrid(cx, cy, indexing="ij"); X, Y = X.ravel(), Y.ravel()
    Dc = K.unit(u2[:, None] + X[None, :, None] * tdir[:, None] + Y[None, :, None] * pdir[:, None])
    if p.get("stem"):
        race = K.Member("race", np.concatenate([Dr[:, edge], Dc], 1), kind="cap", t=CAR_T, width=CAR_W, joints=("J1", "J2"),
                        r_ref=RL, cell=4.0)
        stem = K.Member("stem", Dr[:, ~edge], kind="free", t=RAIL_T, width=STEM_W, joints=("J1",), r_ref=RL, cell=4.0)
        rails = [race, stem]
    else:
        rails = [K.Member("race", np.concatenate([Dr, Dc], 1), kind="cap", t=CAR_T, width=CAR_W, joints=("J1", "J2"), r_ref=RL, cell=4.0)]
    hub2 = K.hub_member("hub2", u2, "J2"); hub2.ramps = [(np.ones(len(hub2.xy), bool), "race", J2_F)]
    hub3 = K.hub_member("hub3", p3, "J3")
    l2 = K.strap_member("link2", u2, p3, ("J2", "J3"), ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                        over=[("race", 1.0), ("neck", 1.0)] + ([("stem", 1.0)] if p.get("stem") else []), q=p.get("q_l2"))
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    res = K.closure_residual(A1, p3, u2, p["gamma"], p["a23"])
    return K.Chain(members=rails + [hub2, l2, hub3, neck], ok=ok, q=q, joints=dict(J1=A1, J2=u2, J3=p3), hubless=("J1",),
                   info=dict(residual_deg=round(float(res[ok].max()), 6) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             rail_span_deg=round(span, 1)))


def full(B, p):
    p = dict(PARAMS, **p); F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    p.update(travel(B, F, p)); return p


def bench_eval(B, params):
    """farm hook: design step + kit evaluate; if the fitted race radius is below the layout radius (the rail would be
    narrower than 10 mm), re-lay it out at the fitted radius (parts only ever grow)"""
    p = full(B, params)
    if p["phi_hi"] - p["phi_lo"] < 2.0:                       # no quiet rail run holds any closing pose
        B.reset(); r = B.report(); r.update(race_R=None, r_lay=p["r_lay"], phi_c=p["phi_c"], phi_lo=p["phi_lo"], phi_hi=p["phi_hi"],
                                            rail_req=p.get("rail_req"), honest=True, note="no quiet rail run"); return r
    r = K.evaluate(B, build, p)
    R = race_radius(B)
    if R is not None and R < p["r_lay"] - 0.5:
        p["r_lay"] = math.floor(R); p.update(travel(B, B._kitF, p)); r = K.evaluate(B, build, p); R = race_radius(B)
    r = {k: v for k, v in r.items() if _jsonable(v)}
    L = B._kit_last
    if "stem" in L["prof"]:                                   # the stem hangs under the head: it may never sit above R
        ex = float(L["prof"]["stem"].max() - L["prof"]["race"].max()); r["stem_excess"] = round(ex, 2)
        if ex > 0.5: r["honest"] = False; r["audit"] = list(r.get("audit", [])) + [f"stem above the rail head by {ex:.1f} mm"]
    r.update(race_R=R, r_lay=p["r_lay"], phi_c=p["phi_c"], phi_lo=p["phi_lo"], phi_hi=p["phi_hi"], rail_req=p.get("rail_req"),
             levels=levels(B))
    return r


def _jsonable(v):
    try: json.dumps(v); return True
    except (TypeError, ValueError): return False


def race_radius(B):
    L = B._kit_last; return round(float(L["prof"]["race"].max()), 2) if "race" in L["prof"] else None


def levels(B):
    L = B._kit_last; out = {}
    for name, pr in L["prof"].items(): out[name] = [round(float(np.min(pr)), 1), round(float(np.median(pr)), 1), round(float(np.max(pr)), 1)]
    return out


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160)
    if a[0] == "check":
        ov = {k: (int(v) if k in ("sigma", "stem") else float(v)) for k, v in (x.split("=") for x in a[1:] if "=" in x)}
        r = bench_eval(B, dict(PARAMS, **ov))
        print(json.dumps({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                                "inband_member", "mass_g", "honest", "audit", "rail_span_deg", "race_R", "r_lay",
                                                "phi_lo", "phi_hi", "rail_req", "residual_deg", "levels", "stem_excess")}))
