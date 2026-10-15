"""twin-rail-one-hub: a spherical 3R whose two pole joints are ARC RAILS (virtual axes through GH) and whose middle
joint is the ONLY hub. Spec: docs/concepts/catalogue.json entry "twin-rail-one-hub"; write-up
docs/concepts/twin-rail-one-hub.md. Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    base -- crown RAIL (S-fixed): a band (W1 wide x 6 radial, caged-ball wire-race C-slide, HARDWARE option A) on the
            circle about the VIRTUAL axis a1 at cone ar1; its section is ONE constant section swept along the arc
            (a surface of revolution about a1: per row across the band, one radius = the worst skin under that row
            anywhere along the rail in any pose taken).
    -- J1 = carriage 1 (Lc long shoe, 2 x 2 mm edge lips, roof 4 mm over the band) rolling on it; q1 = its azimuth.
    -> link 1 = carriage 1 + a short bridge strap (12 x 3) from the carriage's hub-side lip to the J2 hub: J2's
       axis a2 is fixed in link 1 at cone a12 from a1, on the carriage's meridian, BESIDE the rail (ar1 = a12 + d1).
    -- J2 = the only hub: O20 (K4 flat disc, 12.25 mm stack) on a2.
    -> link 2 = strap (12 x 3) from the J2 upper member to carriage 3's lip on the J2 side.
    -- J3 = carriage 3 on the ARM rail (H-fixed, W3 x 6, about the VIRTUAL axis a3 at cone ar3, constant section);
       c3 is on a2's meridian about a3; q3 = its azimuth.
    -> arm rail + K7 neck (14 x 6) from the rail END nearest BOTTOM's bar to the bar's start.
DOF: q1 (carriage 1 on the crown rail), q2 (J2 hub), q3 (carriage 3 on the arm rail): a spherical 3R (a1, a2, a3 with
link angles a12, a23), closed form (two-circle closure, K1) on branch sigma. 3 ACTIVE, 0 PASSIVE (the ball cages are
set by the carriages, not a free coordinate).

Spec changes (stated in the write-up):
  * J2 cannot be centred on the carriage's own ray "beside the rail at the same level" (an annulus centred on a ray the
    rail runs through crosses the rail): the hub sits on the carriage's meridian at cone offset d1 from the rail
    (a12 = ar1 - d1), far enough that the O20 disc clears the band + lips laterally (K6 checks it).
  * O20 hub instead of the KAA15XL0 donut (r 19-26): smaller, the swarm's honest hub (stack 12.25 vs 9 claimed).
  * The rail profile per ROW (constant section, revolve) instead of ONE radius for the whole band (the spec's variant
    a): still a rigid section swept along the arc, which is what a carriage can roll on. variant b (rail shaped per
    station, needs a radial float) is `revolve=0` and is an optimistic bound only.
  * humerus axes in the band frame (F.HG), as the kit and the champion (KIT.md).
Rail extents are a design step from the closing bench poses (central share `cov`), cached per kinematics and computed
from ALL bench frames, so build() stays pose-local (the same rails for any subset of frames).
Kit patches (transparent, scoped): K._levels revolves members that carry `rows` (per-row max = constant section);
K.collisions skips the pairs listed in Chain.info['same_body'] (one rigid body, or the rolling joint itself).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/twin-rail-one-hub.py [check k=v ...|poses|redteam]
"""
import json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "twin-rail-one-hub"
NAME = "Twin rails, one hub: virtual J1 on a crown rail, virtual J3 on an arm rail"
D2R = math.pi / 180
RAIL_T, ROOF, LIP = 6.0, 4.0, 2.0                            # band radial, shoe roof over it, lip width per edge
END_STOP, TAB = 3.0, 8.0                                     # end stop beyond the carriage travel; neck tab on the arm rail

# champion-like seed: a1 near the scapula vertical, a3 near the humerus axis (J3 = a ring segment round the arm)
PARAMS = dict(az1=2.43, el1=80.68, a12=76.9, d1=22.0, wd=10.0, wa=0.0, a23=70.0, ar3=22.0, sigma=-1, margin=10.0,
              W1=20.0, W3=20.0, Lc=40.0, cov=0.95, R1=58.0, R3=130.0, q=1.0, revolve=1, l2over=1, ref1=0.0, ref3=0.0)


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


def kin(F, p):
    a1L = K.bvec(p["az1"], p["el1"]); a3L = K.wdir(p["wd"], p["wa"])
    a1 = F.S(a1L); a3 = F.HG(a3L)
    a2, ok, margin = K.closure(a1, a3, p["a12"], p["a23"], p["sigma"], margin_deg=p["margin"]); a2 = K.unit(a2)
    r1L = K.unit(np.cross(a1L, [0.0, 0.0, 1.0]) + 1e-9); r3L = K.unit(np.cross(a3L, [1.0, 0.0, 0.0]) + 1e-9)
    q1 = K.axis_angle(a1, F.S(r1L), a2); q3 = K.axis_angle(a3, F.HG(r3L), a2); q2 = K.axis_angle(a2, a1, a3)
    return dict(a1=a1, a2=a2, a3=a3, a1L=a1L, a3L=a3L, r1L=r1L, r3L=r3L, q1=q1, q2=q2, q3=q3, ok=ok, margin=margin)


_TRAVEL = {}


def travel(B, p):
    """design step: carriage travel (deg about each virtual axis) over the closing bench poses, central share cov"""
    key = tuple(round(float(p[k]), 6) for k in ("az1", "el1", "a12", "wd", "wa", "a23", "sigma", "margin", "cov"))
    if key in _TRAVEL: return _TRAVEL[key]
    FA = getattr(B, "_kitF", None) or K.frames(B); B._kitF = FA
    k = kin(FA, p); ok = k["ok"]; out = {}
    for n in ("q1", "q3"):
        s = k[n][ok] if ok.sum() >= 5 else np.zeros(5)
        c = float(np.degrees(np.arctan2(np.sin(s * D2R).mean(), np.cos(s * D2R).mean()))); r = wrap(s - c)
        lo, hi = (np.quantile(r, [(1 - p["cov"]) / 2, 1 - (1 - p["cov"]) / 2]) if p["cov"] < 1 else (r.min(), r.max()))
        out[n] = (c, float(lo), float(hi))
    _TRAVEL[key] = out; return out


def ring_dirs(aL, rL, cone, phis, deltas):
    """local unit directions on the cone about aL: cone + delta (rad) across, azimuth phis (rad) from rL -> (n, 3)"""
    bL = np.cross(aL, rL); Ph, De = np.meshgrid(phis, deltas, indexing="ij"); c = cone + De
    v = np.cos(c)[..., None] * aL + np.sin(c)[..., None] * (np.cos(Ph)[..., None] * rL + np.sin(Ph)[..., None] * bL)
    return v.reshape(-1, 3), np.broadcast_to(np.arange(len(deltas)), Ph.shape).ravel()


def pose_dirs(a, e, cone, x, deltas):
    """per-pose directions on the cone about a (P, 3), azimuth x (rad, offsets along the arc) from e (P, 3) -> (P, m, 3)"""
    b = np.cross(a, e); X, De = np.meshgrid(x, deltas, indexing="ij"); X, De = X.ravel(), De.ravel(); c = cone + De
    v = (np.cos(c)[None, :, None] * a[:, None] + np.sin(c)[None, :, None] *
         (np.cos(X)[None, :, None] * e[:, None] + np.sin(X)[None, :, None] * b[:, None]))
    return K.unit(v), np.broadcast_to(np.arange(len(deltas)), (len(x), len(deltas))).ravel()


def rail(name, F_map, aL, rL, cone, rng, R, W, Lc, joint, extra_end=0.0):
    """a rail band: stations over the carriage travel rng (c, lo, hi deg) + half a carriage + end stop (+ extra_end mm
    at the hi end), rows across W at 2 mm, laid out at R. Returns the Member and the hi-end centre direction (local)."""
    c, lo, hi = rng; rr = R * math.sin(cone); e = (Lc / 2 + END_STOP) / rr
    a0, a1 = (c + lo) * D2R - e, (c + hi) * D2R + e + extra_end / rr
    phis = np.linspace(a0, a1, max(3, int(math.ceil((a1 - a0) * rr / 2.0)) + 1))
    deltas = np.arange(-W / 2 + 1, W / 2 - 1 + 1e-6, 2.0) / R
    dL, rows = ring_dirs(aL, rL, cone, phis, deltas)
    m = K.Member(name, K.unit(F_map(dL)), kind="free", t=RAIL_T, width=W, r_ref=R, joints=(joint,))
    m.rows = rows
    lo_end, _ = ring_dirs(aL, rL, cone, np.array([a0]), np.array([0.0])); hi_end, _ = ring_dirs(aL, rL, cone, np.array([a1]), np.array([0.0]))
    return m, lo_end[0], hi_end[0], (a0, a1)


def carriage(name, a, e, cone, R, W, Lc, joint):
    """carriage lips: 2 x LIP mm strips along both band edges over the shoe length Lc (constant section, slides on the
    rail), t = band + roof (the shoe wraps the band)"""
    rr = R * math.sin(cone); x = np.linspace(-Lc / 2, Lc / 2, int(round(Lc / 2.0)) + 1) / rr
    deltas = np.array([-(W / 2 + LIP / 2), W / 2 + LIP / 2]) / R
    D, rows = pose_dirs(a, e, cone, x, deltas)
    m = K.Member(name, D, kind="free", t=RAIL_T + ROOF, width=LIP, r_ref=R, joints=(joint,)); m.rows = rows
    return m


def build(B, F, p):
    k = kin(F, p); a1, a2, a3 = k["a1"], k["a2"], k["a3"]; ok = k["ok"].copy(); P = len(a1)
    T = travel(B, p)
    for n in ("q1", "q3"):
        c, lo, hi = T[n]; rel = wrap(k[n] - c); ok &= (rel >= lo) & (rel <= hi)               # rail = joint range
    ar1 = (p["a12"] + p["d1"]) * D2R; ar3 = p["ar3"] * D2R
    e1 = K.unit(a2 - (a2 * a1).sum(-1, keepdims=True) * a1); e3 = K.unit(a2 - (a2 * a3).sum(-1, keepdims=True) * a3)
    c1 = np.cos(ar1) * a1 + np.sin(ar1) * e1; c3 = np.cos(ar3) * a3 + np.sin(ar3) * e3
    R1, R3, W1, W3, Lc = p["R1"], p["R3"], p["W1"], p["W3"], p["Lc"]
    r1L = K.unit(np.cross(k["a1L"], [0.0, 0.0, 1.0]) + 1e-9); r3L = K.unit(np.cross(k["a3L"], [1.0, 0.0, 0.0]) + 1e-9)
    rail1, _, _, span1 = rail("rail1", F.S, k["a1L"], r1L, ar1, T["q1"], R1, W1, Lc, "C1")
    # arm rail: the neck tab at the end nearest BOTTOM's bar start
    railA, loA, hiA, span3 = rail("rail3", F.HG, k["a3L"], r3L, ar3, T["q3"], R3, W3, Lc, "C3", extra_end=TAB)
    railB, loB, hiB, _ = rail("rail3", F.HG, k["a3L"], r3L, ar3, (T["q3"][0], T["q3"][1] - TAB / (R3 * math.sin(ar3)) / D2R, T["q3"][2]), R3, W3, Lc, "C3")
    # choose the tab end by the rest-free local geometry: the end whose direction is nearer the bar start (H-local, constant)
    barG = K.unit(F.RHG[0].T @ F.RH[0] @ K.unit(K.BAR0_H))   # bar start in the band humerus frame (RH = RHG @ C, C constant)
    use_hi = float(np.dot(K.unit(hiA), barG)) >= float(np.dot(K.unit(loB), barG))
    rail3, tab_end = (railA, hiA) if use_hi else (railB, loB)
    car1 = carriage("car1", a1, e1, ar1, R1, W1, Lc, "C1"); car3 = carriage("car3", a3, e3, ar3, R3, W3, Lc, "C3")
    s1 = 1.0 if p["d1"] < 0 else -1.0                        # side of the rail the hub is on (towards a12)
    b_from = K.unit(np.cos(ar1 + s1 * (W1 / 2 + LIP + 2.0) / R1) * a1 + np.sin(ar1 + s1 * (W1 / 2 + LIP + 2.0) / R1) * e1)
    hub2 = K.hub_member("hub2", a2, "J2")
    bridge = K.strap_member("bridge1", b_from, a2, ("C1", "J2"), ramp_to=((None, 0.0), ("hub2", 0.0)))
    s3 = 1.0 if p["a23"] > p["ar3"] else -1.0
    l_end = K.unit(np.cos(ar3 + s3 * (W3 / 2 + LIP + 2.0) / R3) * a3 + np.sin(ar3 + s3 * (W3 / 2 + LIP + 2.0) / R3) * e3)
    link2 = K.strap_member("link2", a2, l_end, ("J2", "C3"), ramp_to=(("hub2", K.STACK), (None, 0.0)),
                           over=[("rail1", ROOF + 1.0)] if p.get("l2over", 1) else [])
    neck = K.neck_member(F, F.HG(tab_end), joints=("N3",))
    q = np.stack([k["q1"], k["q2"], k["q3"]], -1)
    # a rail is an OPEN arc (it needs a gap for its mount) and a shoe cannot wrap more than a quarter of its circle
    span_bad = ((span1[1] - span1[0]) / D2R > 330 or (span3[1] - span3[0]) / D2R > 330 or
                Lc / (R1 * math.sin(ar1)) / D2R > 90 or Lc / (R3 * math.sin(ar3)) / D2R > 90)
    if span_bad: ok = np.zeros_like(ok)
    res = K.closure_residual(a1, a3, a2, p["a12"], p["a23"])
    info = dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                min_margin=round(float(k["margin"][ok].min()), 2) if ok.any() else None,
                rail1_deg=round((span1[1] - span1[0]) / D2R, 1), rail1_mm=round((span1[1] - span1[0]) * R1 * math.sin(ar1), 1),
                rail3_deg=round((span3[1] - span3[0]) / D2R, 1), span_bad=bool(span_bad), rail3_mm=round((span3[1] - span3[0]) * R3 * math.sin(ar3), 1),
                same_body=[["rail1", "car1"], ["car1", "bridge1"], ["car1", "hub2"], ["bridge1", "hub2"], ["link2", "car3"],
                           ["car3", "rail3"], ["rail3", "neck"]])
    members = [rail1, car1, bridge, hub2, link2, car3, rail3, neck]
    if not p.get("revolve", 1):
        for m in (rail1, rail3): m.rows = None
    return K.Chain(members=members, ok=ok, q=q, info=info,
                   joints=dict(J1=a1, J2=a2, J3=a3, C1=c1, C3=c3, N3=F.HG(tab_end)), hubless=("J1", "J3", "C1", "C3", "N3"))


# ---- kit patches (scoped): constant-section rails, same-body K6 pairs -------------------------------------------------
_KIT_LEVELS, _KIT_COLL = K._levels, K.collisions


def _levels_revolve(B, chain, fit, q, mode):
    out = _KIT_LEVELS(B, chain, fit, q, mode)
    for m in chain.members:
        rows = getattr(m, "rows", None)
        if rows is None: continue
        r = out[m.name]; mx = np.full(rows.max() + 1, -np.inf); np.maximum.at(mx, rows, r); out[m.name] = mx[rows]
    return out


def collisions_same_body(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    skip = {frozenset(x) for x in chain.info.get("same_body", [])}
    hit = np.zeros(len(ok), bool); M = chain.members
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            if frozenset((M[a].name, M[b].name)) in skip: continue
            hit |= _KIT_COLL(K.Chain(members=[M[a], M[b]], ok=chain.ok, joints=chain.joints), pts, ok, clear, overlap, chunk)
    return hit


K._levels = _levels_revolve; K.collisions = collisions_same_body


# ---- the swarm's parking rule and per-pose diagnostics -------------------------------------------------------------
def park(B):
    """hub 2: fitted level F and the minimum skin distance on the 25 mm of axis line above it, over the taken poses"""
    L = B._kit_last; ch = L["chain"]; take = L["take"]; Pi = np.nonzero(take)[0]
    if not len(Pi): return dict(hub2=None, park_ok=False)
    h = float(L["prof"]["hub2"][0]); a2 = K.unit(ch.joints["J2"][Pi]); ts = np.arange(h + K.CROWN, h + K.CROWN + 25.01, 2.5)
    P = (a2[:, None, :] * ts[None, :, None]).reshape(-1, 3); d = K.dist_many(B, np.repeat(Pi, len(ts)), P)
    return dict(hub2=[round(h, 1), round(float(d.min()), 2)], park_ok=bool(h <= 140 and d.min() >= 0))


def evaluate(B, p, **kw):
    """-> (params, report): the kit report + the parking rule (tools/concept_cma.py contract)"""
    p = dict(PARAMS, **p); r = K.evaluate(B, build, p, **kw); r.update(park(B)); return p, r


def bench_eval(B, p):
    """tools/concept_sweep.py hook: the kit report + the parking rule"""
    return evaluate(B, p)[1]


def metal(pose, frames, params):
    L = frames._kit_last
    if not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


def _parse(a):
    ov = {}
    for x in a:
        if "=" in x: kk, v = x.split("="); ov[kk] = float(v)
    return ov


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    B = K.bench(60, 160)
    if mode == "check":
        import time; t0 = time.time(); _, r = evaluate(B, _parse(a[1:]))
        print(json.dumps({x: r.get(x) for x in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips",
                                                 "collide", "inband_member", "honest", "audit", "rail1_deg", "rail1_mm", "rail3_deg",
                                                 "rail3_mm", "hub2", "park_ok", "residual_deg", "sample_mm", "mass_g")}, indent=1), round(time.time() - t0, 1), "s")
    elif mode == "redteam":
        p, r = evaluate(B, _parse(a[1:])); L = B._kit_last; ch = L["chain"]; take, ok, hit = L["take"], L["ok"], L["hit"]
        F = B._kitF; k = kin(F, p); T = travel(B, p); P = len(take)
        close = k["ok"]; rng = np.ones(P, bool)
        for n in ("q1", "q3"):
            c, lo, hi = T[n]; rel = wrap(k[n] - c); rng &= (rel >= lo) & (rel <= hi)
        allp = np.concatenate([L["pts"][m.name] for m in ch.members], 1); names = np.concatenate([[m.name] * L["pts"][m.name].shape[1] for m in ch.members])
        dmin = np.full(P, np.nan); arg = [None] * P
        for i in range(P):
            if ok[i]:
                d = B.dist(i, allp[i]); j = int(np.argmin(d)); dmin[i] = d[j]; arg[i] = names[j]
        groups = dict(rest=lambda q: q["elev"] <= 20, overhead=lambda q: q["elev"] >= 140,
                      across=lambda q: q["plane"] >= 120 and q["elev"] >= 45, behind=lambda q: q["plane"] <= -60 or q["axial"] >= 120)
        out = dict(report={x: r.get(x) for x in ("gap", "reach", "follow", "inband14", "inband10", "contact", "inband_member", "hub2", "park_ok")})
        for g, f in groups.items():
            I = [i for i in range(P) if f(B.poses[i])]
            why = dict(closure=0, rail_range=0, continuity=0, collision=0, contact=0, taken=0)
            for i in I:
                if not close[i]: why["closure"] += 1
                elif not rng[i]: why["rail_range"] += 1
                elif not ok[i]: why["continuity"] += 1
                elif hit[i]: why["collision"] += 1
                elif dmin[i] < 0: why["contact"] += 1
                else: why["taken"] += 1
            out[g] = dict(n=len(I), **why)
        tk = [i for i in range(P) if take[i] and dmin[i] >= 0]
        pinch = sorted(tk, key=lambda i: dmin[i])[:5]
        out["pinch"] = [dict(pose={x: round(float(v), 0) for x, v in B.poses[i].items()}, kind=B.kind[i], member=arg[i], d=round(float(dmin[i]), 2)) for i in pinch]
        # the pose that sets each rail's level: per rail, the (pose, sample) whose requirement equals the fitted row level
        for m in ch.members:
            if getattr(m, "rows", None) is None or m.name not in ("rail1", "rail3"): continue
            Pi = np.nonzero(ok)[0]; D = m.D[Pi].reshape(-1, 3); I = np.repeat(Pi, m.D.shape[1])
            R = K.requirement(B, I, D).reshape(len(Pi), -1); R = np.where(np.isfinite(R), R, 400.0)
            pi, si = np.unravel_index(int(np.argmax(R)), R.shape)
            out[m.name + "_set_by"] = dict(pose={x: round(float(v), 0) for x, v in B.poses[int(Pi[pi])].items()}, kind=B.kind[int(Pi[pi])],
                                          level=float(R.max()), median_req=round(float(np.median(R)), 1), level_rows=[round(float(v), 1) for v in np.unique(L["prof"][m.name])])
        print(json.dumps(out, indent=1, default=str))

