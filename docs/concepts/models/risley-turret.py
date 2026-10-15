"""risley-turret: J1 and J2 as two overlapping flat ring bearings on top of the scapula, one strap down to an O20 hub
on the lateral deltoid (3 ACTIVE DOF, 0 passive), on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).
Catalogue entry: docs/concepts/catalogue.json id "risley-turret". Rebuilt on the kit (the interrupted session's own
620-line implementation was replaced: own envelope tracer, no dense continuity, no audit).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    S (handler) --J1: flat ring bearing about b (S-fixed)--> L1 (= J1's upper race + J2's lower race, one figure-8
    race body bolted in the overlap lens) --J2: flat ring bearing about p2 (A1 from b)--> L2 (J2's upper race + one
    strap from the rim of the ring down to W) --J3: O20 v5 hub about W (humerus-fixed)--> H (K7 neck to BOTTOM).
DOF: a spherical 3R with a short first link: b fixed in S, W fixed in H, p2 by the K1 two-circle closure
(angle(b, p2) = A1, angle(p2, W) = A2, branch sigma). 3 active, 0 passive, no spare.

Parts, every one at real size (2 mm sample grid = 1 pt / 4 mm2 on every skin-facing face):
  ring1  flat annulus about b, radii r_in..r_out, axial section ring_h (8 mm: lower race on S, upper race on L1);
         lower face fitted by the K4 march of every annulus sample along b (kind 'flat');
  ring2  same about p2. Its level h2 = max(K4 skin fit, stack): every ring-2 lower-face point over ring 1's footprint
         (lateral r_in - 1 .. r_out + 1 from b) sits >= j2_gap above ring 1's top (h1 + ring_h). Solved exactly in the
         ring pair's own frame (constant: both rings are bodies of revolution, the angle b-p2 is A1), two-pass: pass 1
         fits h1 and h2's skin level, pass 2 rebuilds with h2 (a ramp on ring1's level). The overlap lens (area of
         ring 2's lower face over ring 1's upper race) is reported; < lens_min mm2 -> no L1 joint -> config invalid.
  link2  strap width x t (14 x 3 Ti) on the great circle from the ring-2 rim point toward W (a lug on the outer wall of
         J2's upper race: underside at axial h2 + ring_h/2) to the J3 hub (upper member, F3 + 3.15); K3 underside,
         60 deg climb, passes over ring 1 and the neck (>= 1 mm, `over`). The rigid lug join ring2/link2 is the fake
         joint "L2" (K6 exempt within 12 mm of it only).
  hub3   O20 v5 hub about W (K4, 12.25 stack).  neck  K7 14 x 6 strap from W to BOTTOM's bar.
Taken: K1 closure with margin, dense K2 continuity (every joint axis), K6 collisions, no metal inside the skin.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/risley-turret.py check [key=value ...]
    ... sweep coarse|refine|red   (appends to docs/concepts/sweeps/risley-turret.json)
    ... write                     (row from the best sweep entry, re-evaluated)
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "risley-turret"
NAME = "Risley turret: J1 and J2 as two overlapping rings on top of the scapula"
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
# spec start: b = bvec(32.55, 80.56), W0 = wdir(71.38, 4.78), A1 40, A2 75, branch -1, margin 5
PARAMS = dict(az=32.55, el=80.56, wd=71.38, wa=4.78, a1=40.0, a2=75.0, sigma=-1, margin=5.0,
              r_in=15.0, r_out=24.0, ring_h=8.0, j2_gap=1.0, width=14.0, t_link=3.0, lens_min=60.0, q=1.0)


# ---- the ring pair (canonical frame: b = z, p2 = (sin A1, 0, cos A1)) ------------------------------------------------
def annulus_xy(r_in, r_out, step=2.0):
    xy = K.disc_xy(r_out, step); r = np.linalg.norm(xy, axis=1); return xy[r >= r_in - 1e-9]


def stack_level(p, h1, h2_skin, step=0.25):
    """smallest h2 >= h2_skin with every ring-2 lower-face point over ring 1's footprint >= j2_gap above ring 1's top;
    -> (h2, lens area mm2 of ring 2's lower face over ring 1's upper race)"""
    A = p["a1"] * K.D2R; pc = np.array([math.sin(A), 0, math.cos(A)]); e1 = np.array([math.cos(A), 0, -math.sin(A)])
    xy = annulus_xy(p["r_in"], p["r_out"], 0.5); top = h1 + p["ring_h"] + p["j2_gap"]
    h = max(h2_skin, 0.0)
    for _ in range(2000):
        P = h * pc + xy[:, :1] * e1 + xy[:, 1:] * np.array([0, 1.0, 0]); lat = np.hypot(P[:, 0], P[:, 1])
        over = (lat >= p["r_in"] - 1) & (lat <= p["r_out"] + 1)
        if not over.any() or P[over, 2].min() >= top: break
        h += step
    lens = float(((lat >= p["r_in"]) & (lat <= p["r_out"])).sum() * 0.25)
    return h, lens


def ring_member(name, axis, joints, p):
    k = K.unit(axis); a, bv = K.plane_frame(k); xy = annulus_xy(p["r_in"], p["r_out"])
    D = K.unit(70.0 * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * bv[:, None])
    return K.Member(name, D, kind="flat", t=p["ring_h"], width=2 * p["r_out"], joints=tuple(joints), K=k, A=a, Bv=bv,
                    xy=xy, cell=4.0)


def build(B, F, p):
    b = F.S(K.bvec(p["az"], p["el"])); W = F.HG(K.wdir(p["wd"], p["wa"])); arm = F.HG([0.0, -1.0, 0.0])
    p2, ok, margin = K.closure(b, W, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    q = np.stack([K.axis_angle(b, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, b, W), K.axis_angle(W, arm, p2)], -1)
    h2 = p.get("_h2", 62.0)                                   # pass 1: nominal (only the strap start uses it)
    # strap start: the rim of ring 2 toward W (+1 mm), a lug on the outer wall of J2's upper race (axial h2 + ring_h/2)
    ax = h2 + p["ring_h"] / 2; rr = p["r_out"] + 1.0; phi0 = math.atan2(rr, ax)
    t = K.unit(W - (W * p2).sum(-1, keepdims=True) * p2); r0 = math.cos(phi0) * p2 + math.sin(phi0) * t
    # L1: J1's upper race and J2's lower race joined by a bridge strap between the facing rims (lugs on the outer walls,
    # J1 upper race at axial h1 + 3/4 ring_h, J2 lower race at h2 + 1/4 ring_h); rings that overlap need the lens join
    h1 = p.get("_h1", 55.0); rr1 = p["r_out"] + 1.0; ax1 = h1 + 0.75 * p["ring_h"]; ax2 = h2 + 0.25 * p["ring_h"]
    phi1, phi2 = math.atan2(rr1, ax1), math.atan2(rr, ax2)
    bridge = p.get("_lens", 0.0) < p["lens_min"]             # no bolting lens over ring 1 -> a bridge strap
    tb = K.unit(p2 - (p2 * b).sum(-1, keepdims=True) * b); tp = K.unit(b - (b * p2).sum(-1, keepdims=True) * p2)
    s1 = math.cos(phi1) * b + math.sin(phi1) * tb; s2 = math.cos(phi2) * p2 + math.sin(phi2) * tp
    ring1 = ring_member("ring1", b, ("J1", "L1a") if bridge else ("J1",), p)
    ring2 = ring_member("ring2", p2, ("J2", "L2", "L1b") if bridge else ("J2", "L2"), p)
    if "_h2" in p: ring2.ramps = [(np.ones(len(ring2.xy), bool), "ring1", p["_h2"] - p["_h1"])]
    extra, jx = [], {}
    if bridge:
        extra = [K.strap_member("bridge", s1, s2, ("L1a", "L1b"), width=p["width"], t=p["t_link"],
                                ramp_to=(("ring1", math.hypot(ax1, rr1) - h1), ("ring2", math.hypot(ax2, rr) - h2)))]
        jx = dict(L1a=s1, L1b=s2)
    hub3 = K.hub_member("hub3", W, "J3")
    link2 = K.strap_member("link2", r0, W, ("J2", "J3", "L2"), width=p["width"], t=p["t_link"],
                           ramp_to=(("ring2", math.hypot(ax, rr) - h2), ("hub3", K.STACK)),
                           over=[("ring1", 1.0), ("neck", 1.0)] + ([("bridge", 1.0)] if bridge else []))
    neck = K.neck_member(F, W, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    p2arm = np.degrees(np.arccos(np.clip((p2 * arm).sum(-1), -1, 1)))
    info = dict(residual_deg=round(float(K.closure_residual(b, W, p2, p["a1"], p["a2"])[ok].max()), 6) if ok.any() else None,
                min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                min_p2_arm_deg=round(float(p2arm[ok].min()), 1) if ok.any() else None,
                h1=p.get("_h1"), h2=p.get("_h2"), lens_mm2=p.get("_lens"))
    info["bridge"] = bool(bridge)
    return K.Chain(members=[ring1, ring2, hub3, link2, neck] + extra, ok=ok, q=q,
                   joints=dict(J1=b, J2=p2, J3=W, L2=r0, **jx), hubless=("J1", "J2", "L2") + tuple(jx), info=info)


def evaluate(B, p, **kw):
    """two passes: (1) closure + dense K2 -> fit poses -> ring levels h1, h2 (skin); stack solve; (2) the kit's honest
    evaluate with ring 2 at its stack level and the strap lug at the true rim height"""
    p = {k: v for k, v in p.items() if not k.startswith("_")}
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    ch = build(B, F, p); ok, _ = K.continuity_dense(B, F, build, p, np.asarray(ch.ok, bool))
    if not ok.any():
        return K.evaluate(B, build, p, **kw)
    rings = K.Chain(members=[m for m in ch.members if m.name in ("ring1", "ring2")], ok=ok)
    prof = K.fit_profiles(B, rings, ok, p.get("q", 1.0), "march")
    h1, h2s = float(prof["ring1"][0]), float(prof["ring2"][0])
    h2, lens = stack_level(p, h1, h2s)
    return K.evaluate(B, build, dict(p, _h1=round(h1, 3), _h2=round(h2, 3), _h2skin=round(h2s, 3), _lens=round(lens, 1)), **kw)


def run_sweep(B, configs, log=print):
    rows = json.load(open(SWEEP_OUT)) if os.path.exists(SWEEP_OUT) else []
    best = min(rows, key=lambda e: e["gap"]) if rows else None
    for c in configs:
        r = evaluate(B, dict(c))
        e = dict(k=len(rows), t=K.now(), params=dict(c), **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 closure=r["closure"], mass_g=r["mass_g"], honest=r["honest"], kmode=r["kmode"],
                 h1=r.get("h1"), h2=r.get("h2"), lens_mm2=r.get("lens_mm2"), inband_member=r["inband_member"],
                 collide=r["collide"], flips=r["flips"], min_p2_arm_deg=r.get("min_p2_arm_deg"))
        rows.append(e); tmp = SWEEP_OUT + ".tmp"; json.dump(rows, open(tmp, "w"), indent=1); os.replace(tmp, SWEEP_OUT)
        if best is None or e["gap"] < best["gap"]:
            best = e; K.log_event(f"Risley turret new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, "
                                  f"in-band14 {e['inband14']}, contact {e['contact']}; baseline 68.93)")
        if log: log(f"[{e['k']}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} "
                    f"contact {e['contact']} clos {e['closure']} col {e['collide']} h {e['h1']}/{e['h2']} {e['inband_member']} {c}", flush=True)
    return best, rows


def grid(base, **ax):
    keys = list(ax); return [dict(base, **dict(zip(keys, v))) for v in itertools.product(*(ax[k] for k in keys))]


if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0] if a else "check"
    kv = {x.split("=")[0]: float(x.split("=")[1]) for x in a[1:] if "=" in x}
    nb = (20, 40) if "small" in a else (60, 160)
    B = K.bench(*nb)
    if cmd == "check":
        r = evaluate(B, dict(PARAMS, **kv)); print(json.dumps(r, default=str))
    elif cmd == "sweep":
        stage = a[1] if len(a) > 1 else "coarse"
        if stage == "coarse":
            cf = grid(PARAMS, a1=[32.0, 40.0, 48.0], a2=[70.0, 80.0, 90.0], wd=[71.38, 85.0], sigma=[-1, 1])
        else:
            cf = [json.loads(l) for l in open(stage)]
        best, rows = run_sweep(B, cf); print("BEST", best)
