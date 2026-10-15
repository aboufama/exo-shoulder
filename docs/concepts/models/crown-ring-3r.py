"""Concept model: CROWN RING 3R (id crown-ring-3r, docs/concepts/catalogue.json, ideation B), on the shared kit
(tools/concept_kit.py, docs/concepts/KIT.md). Doc: docs/concepts/crown-ring-3r.md.

A spherical 3R (every axis through GH) whose J1 is an OPEN thin-section ring lying flat on the shoulder crown:
    scapula handler -> J1 ring (axis a1 = bvec(az1, el1) fixed in the scapula, near c* = bvec(22.8, 65.6)) -> link 1
    (strap from a lug on the rotor rim to J2) -> J2 O20 hub (axis by two-cone closure: alpha12 from a1, alpha23 from a3)
    -> link 2 (strap over the deltoid, passes over link 1 and the neck) -> J3 O20 hub (axis a3 = wdir(wd, wa) fixed in
    the humerus, band frame) -> K7 neck to BOTTOM's bar.
DOF: 3 ACTIVE, 0 PASSIVE (the humerus orientation fixes the three angles; branch sigma fixed per design).

Parts at real size (honesty rule 1):
  * J1 ring, p1 > 0 = pitch radius (KA020XP0 28.6, KA025XP0 34.9, KA030XP0 41.3): the spec's land from pitch - 8 to
    pitch + 8 (bearing + 1.5 mm Ti housings) as a FLAT annulus normal to a1 (kind 'flat', K4: every land sample is
    marched along a1 from its true in-plane offset; the level F = max over samples of the q-quantile). Stack 9 mm
    (stator 0..4.5, rotor housing 4.5..9). The outer and bore walls stand on the land's rim samples; the K3 march
    already requires dist >= 0 on the 15 mm of the axis-parallel line above every land sample (the march window), so
    a wall can never be inside the skin in a fitted pose. p1 = 0 makes J1 an O20 hub (the in-model control).
  * link 1: 14 x 3 Ti strap (spec: MVP1 loads ~1 N.m) on the great circle from the ROOT direction to J2. The root is
    bolted on TOP of the rotor housing: the strap starts over the pitch circle (direction atan2(p1, h1 + 9) off a1)
    and passes over the outer half of the land with `over=[("ring1", 0.6)]` (underside >= ring top + 0.6 mm wherever
    it is above the ring, so K6 sees the attachment as clear; the real bolted joint has 0 gap: conservative by 0.6).
    (A lug outside the land edge collided with the land in every pose - K6 exempts partners only within 12 mm of the
    axis, made for O20 hubs.) h1 is the ring level F; bench_eval runs two passes (h1 = the first pass's fitted F).
  * J2, J3: O20 hubs (K4, 12.25 stack) - annular-ring-3r measured donut / ring bores at J2 and J3 lose to O20 at every
    bore (J2 105 vs 112-118 mm, J3 66 vs 68 mm), so they are not re-swept here.
  * links 12/14 x 3, K5 60 deg climb; neck = K7 (14 x 6).
Checks: K3 march, K2 dense continuity (values + axes), K6 collisions, audit; closure margin >= `margin` deg.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/crown-ring-3r.py [--params JSON] [--poses]
"""
import json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "crown-ring-3r"
NAME = "Crown ring 3R: J1 an open thin-section ring on the crown"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
D2R = math.pi / 180
RING_HW, RING_H, RING_UP, LUG = 8.0, 9.0, 4.5, 4.5         # land half width, stack, rotor housing level, lug outside the land

# seed: J1 at c* (spec), the template's closure angles / J3 (the champion's), KA025 ring, q 1.0 (never touches)
PARAMS = dict(az1=22.8, el1=65.6, p1=34.9, a12=76.9, a23=66.75, wd=86.33, wa=21.83, sigma=-1, margin=10.0,
              width=14.0, t_link=3.0, w2=12.0, q=1.0, h1=60.0, lug=0.0)


def toward(u, v, phi):
    """rotate unit u (P, 3) toward v (P, 3) by phi rad on their great circle"""
    e = K.unit(v - (u * v).sum(-1, keepdims=True) * u)
    return math.cos(phi) * u + math.sin(phi) * e


def annulus_xy(p, hw=RING_HW, step=2.0):
    ro, ri = p + hw, p - hw
    g = np.arange(-ro, ro + 1e-6, step); X, Y = np.meshgrid(g, g); r2 = X ** 2 + Y ** 2
    keep = (r2 <= ro ** 2 + 1e-9) & (r2 >= ri ** 2 - 1e-9); return np.stack([X[keep], Y[keep]], -1)


def ring_member(name, axis, joint, p):
    k = K.unit(axis); a, b = K.plane_frame(k); xy = annulus_xy(p)
    D = K.unit(70.0 * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    return K.Member(name, D, kind="flat", t=RING_H, width=2 * (p + RING_HW), joints=(joint,), K=k, A=a, Bv=b, xy=xy, cell=4.0)


def build(B, F, p):
    a1 = F.S(K.bvec(p["az1"], p["el1"]))                     # J1: scapula-fixed
    a3 = F.HG(K.wdir(p["wd"], p["wa"]))                      # J3: humerus-fixed (band frame)
    a2, ok, margin = K.closure(a1, a3, p["a12"], p["a23"], p["sigma"], margin_deg=p["margin"])   # J2 (K1)
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), a2), K.axis_angle(a2, a1, a3),
                  K.axis_angle(a3, F.HG([0.0, -1, 0]), a2)], -1)
    det = np.abs((a1 * np.cross(a2, a3)).sum(-1))
    W, T = p["width"], p["t_link"]
    hub2, hub3 = K.hub_member("hub2", a2, "J2"), K.hub_member("hub3", a3, "J3")
    if p["p1"] > 0:                                          # the crown ring and its lug root
        j1 = ring_member("ring1", a1, "J1", p["p1"])
        if p.get("lug", 0) > 0:                                  # variant: root on a lug p['lug'] mm outside the land, rotor level
            L = p["p1"] + RING_HW + p["lug"]; hr = p["h1"] + RING_UP
            root = toward(a1, a2, math.atan2(L, hr)); dz = math.hypot(L, hr) - p["h1"]
            link1 = K.strap_member("link1", root, a2, ("J1", "J2"), width=W, t=T, ramp_to=(("ring1", dz), ("hub2", 0.0)))
        else:
            root = toward(a1, a2, math.atan2(p["p1"], p["h1"] + RING_H))      # bolted on the rotor top, from the pitch circle out
            link1 = K.strap_member("link1", root, a2, ("J1", "J2"), width=W, t=T, ramp_to=((None, 0), ("hub2", 0.0)),
                                   over=[("ring1", 0.6)])
        hubless = ("J1",)
    else:                                                    # in-model control: J1 an O20 hub (template)
        j1 = K.hub_member("hub1", a1, "J1")
        link1 = K.strap_member("link1", a1, a2, ("J1", "J2"), width=W, t=T, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)))
        hubless = ()
    link2 = K.strap_member("link2", a2, a3, ("J2", "J3"), width=p["w2"], t=T, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                           over=[("link1", 1.0), ("neck", 1.0)])
    neck = K.neck_member(F, a3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    return K.Chain(members=[j1, hub2, hub3, link1, link2, neck], ok=ok, q=q, joints=dict(J1=a1, J2=a2, J3=a3), hubless=hubless,
                   info=dict(residual_deg=round(float(K.closure_residual(a1, a3, a2, p["a12"], p["a23"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             det_p5=round(float(np.percentile(det[ok], 5)), 3) if ok.any() else None))


def _level(B, name):
    lk = B._kit_last; return float(lk["prof"][name].max())


def park_check(B, lim=140.0, free=25.0):
    """the swarm's parking rule: every joint part's level <= ~140 mm from GH, and >= 25 mm free above it (dist >= 0 on
    the axis-parallel line from its level F to F + 25 through its centre - for the ring 8 points on the pitch circle)
    in every taken pose. Returns park (name: [level, min dist on the line]) and park_ok."""
    lk = B._kit_last; ch, prof, take = lk["chain"], lk["prof"], lk["take"]; Ti = np.nonzero(take)[0]; out = {}; good = True
    if not len(Ti): return dict(park={}, park_ok=False)
    for m in ch.members:
        if m.kind != "flat": continue
        F = float(prof[m.name].max()); kk = m.K[Ti]; rad = max(0.0, float(np.median(np.linalg.norm(m.xy, axis=1))) if m.name.startswith("ring") else 0.0)
        ang = np.linspace(0, 2 * np.pi, 8, endpoint=False) if rad > 0 else np.zeros(1)
        t = np.arange(F, F + free + 1e-6, 1.0); pts = []
        for g in ang:
            c = rad * (np.cos(g) * m.A[Ti] + np.sin(g) * m.Bv[Ti])
            pts.append(c[:, None, :] + t[None, :, None] * kk[:, None, :])
        X = np.concatenate(pts, 1); I = np.repeat(Ti, X.shape[1])
        d = K.dist_many(B, I, X.reshape(-1, 3)); dmin = float(d.min())
        out[m.name] = [round(F, 1), round(dmin, 2)]; good &= (F <= lim) and dmin >= 0
    return dict(park=out, park_ok=bool(good))


def bench_eval(B, params, verbose=False):
    """two passes when J1 is a ring: the lug root of link 1 is placed at the ring's FITTED level (pass 1 -> h1)"""
    p = dict(PARAMS, **params)
    r = K.evaluate(B, build, p)
    if p["p1"] > 0 and "ring1" in B._kit_last["prof"]:
        h = _level(B, "ring1")
        if abs(h - p["h1"]) > 0.5 and h < 300:
            p["h1"] = round(h, 1); r = K.evaluate(B, build, p)
        r["h1_used"] = p["h1"]; r["ring1_F"] = round(_level(B, "ring1"), 1)
    prof = B._kit_last["prof"]
    r["levels"] = {k: round(float(v.max()), 1) for k, v in prof.items()}
    r.update(park_check(B))
    r = json.loads(json.dumps(r, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    if verbose: print(json.dumps({k: r[k] for k in r if k not in ("sample_mm",)}))
    return r


if __name__ == "__main__":
    a = sys.argv[1:]
    B = K.bench(60, 160)
    p = dict(PARAMS, **(json.loads(a[a.index("--params") + 1]) if "--params" in a else {}))
    bench_eval(B, p, verbose=True)
