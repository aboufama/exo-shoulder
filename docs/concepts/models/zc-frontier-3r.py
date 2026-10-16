"""zc-frontier-3r: the ZERO-COMPLEXITY class mapped globally under the user's 2026-10-16 ~05:50 UTC rulings.

Complexity 0 (tools/simplicity.py) = three active pins whose axes meet at GH, three links, O20 hubs, nothing else. This
model is that class with EVERY designer freedom open (not only near the old leaders):

  * J1 seat ray u1 = bvec(az, el) over the allowed seat region ONLY (user ruling 4: back of the shoulder + acromion top;
    no front / clavicle). Declared region (SEAT_OK): anterior component of u1 <= 0.20 (bvec x = -cos(el) cos(az)),
    az in [-110, 135], el in [-20, 90]. Outside it the config is not evaluated (gap 200).
  * J3 seat ray u3 = wdir(wd, wa) in the band humerus frame, the WHOLE sphere (wd 20-175, wa -180..180): which END of
    the J3 axis line carries the hub is covered by the sphere.
  * arcs a1, a2 in [12, 168]: an arc > 90 is the hub on the FAR end of the J2 line (the fold band is sign-invariant:
    (u1, a1, a2, u3) == (u1, a1, 180 - a2, -u3) kinematically, with the hub and the link on the other side).
  * branch sigma +-1.
  * stack order at J2 / J3 (inv2 / inv3, the j3-neck-over-3r idea): inv3 = 1 puts link 2 on hub 3's LOWER plate and
    member 3 (arm plate + K7 neck) on the cap plate, bridging OVER link 2; inv2 = 1 puts link 2 on hub 2's lower plate
    and link 1 on its upper plate (link 1 bridges over link 2). Same O20 hub, same parts, same stack height.
  * underside quantile q (0.8-1.0) and the strap end hold end_extra (0-8 mm), as in the polish.

Fixed by the rules: O20 v5 hubs at all three joints (rad 10, 12.25 mm stack, MR117-2RS pair; ruling 2 "Keep O20
only"), fold margin 5 deg (ruling 1), 12 x 3 Ti straps on great circles, K7 14 x 6 neck to BOTTOM's bar.

Checks = docs/concepts/models/spine-parked-j2-3r.py (kit K1-K7 + dense K2, hub crown / wall skin check, near-touch,
overhead split) + docs/concepts/verify/spine-parked-j2-3r.py's top_check (top faces of every member, near-touch over
all faces, closure residual, hub-axis accessibility F <= 140 mm) with the 1 mm radial K6, all unchanged: this file only
builds the chain. The objective `gap` = the verifier's plain gap (v); `near` = its near-touch gap (metal < 1 mm =
contact).

    OMP_NUM_THREADS=1 python3 docs/concepts/models/zc-frontier-3r.py '<json params>'         one eval on Bench(60,160)
    hooks: evaluate(B, params) -> (params, report); kin(F, p) -> closure masks (the fold law only)
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                       # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


SPM = _load("zc_spm", os.path.join(REPO, "docs", "concepts", "models", "spine-parked-j2-3r.py"))
VER = _load("zc_spm_verify", os.path.join(REPO, "docs", "concepts", "verify", "spine-parked-j2-3r.py"))
if not getattr(K.collisions, "_zc_1mm", False):                               # the verifier's 1 mm radial K6
    K.collisions = functools.partial(K.collisions, overlap=1.0 - 1e-4); K.collisions._zc_1mm = True

ID = "zc-frontier-3r"
NAME = "Zero-complexity 3R frontier: three O20 pins through GH, global seats / arcs / ends / stack order, margin 5"
# start = spine-parked k7008's axes (its verified shape) at O20 / margin 5
PARAMS = dict(az=95.8565, el=65.2093, a1=37.6, a2=73.6, wd=84.8, wa=-11.37, sigma=-1, inv2=0, inv3=0, q=0.97,
              end_extra=0.0, margin=5.0, width=12.0, t_link=3.0, rad1=10.0, rad2=10.0, rad3=10.0, vm=0, near=0)
BOUNDS = dict(az=(-110.0, 135.0), el=(-20.0, 90.0), a1=(12.0, 168.0), a2=(12.0, 168.0), wd=(20.0, 175.0),
              wa=(-180.0, 180.0), q=(0.8, 1.0), end_extra=(0.0, 8.0))
ANT_MAX = 0.20


def seat_ok(az, el):
    """user ruling 4: J1 on the back of the shoulder or the acromion top (no front / clavicle seats)"""
    u = K.bvec(az, el)
    return bool(-110.0 <= az <= 135.0 and -20.0 <= el <= 90.0 and u[0] <= ANT_MAX)


def snap(p):
    p = dict(PARAMS, **p)
    for k, (lo, hi) in BOUNDS.items():
        if k == "wa": p[k] = (float(p[k]) + 180.0) % 360.0 - 180.0
        else: p[k] = min(hi, max(lo, float(p[k])))
    p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    for k in ("inv2", "inv3"): p[k] = 1 if float(p[k]) >= 0.5 else 0
    for k in ("margin", "width", "t_link", "rad1", "rad2", "rad3", "vm", "near"): p[k] = PARAMS[k]   # rules: never loosened
    return p


def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"]))
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    inv2, inv3 = int(p.get("inv2", 0)), int(p.get("inv3", 0))
    # J2 stack: normal = link 1 lower (F), link 2 upper (F + STACK); inv2 swaps them
    l1_at2, l2_at2 = (K.STACK, 0.0) if inv2 else (0.0, K.STACK)
    # J3 stack: normal = neck / arm plate lower, link 2 upper; inv3 = link 2 lower, member 3 on the cap plate
    l2_at3, nk_at3 = (0.0, K.STACK) if inv3 else (K.STACK, 0.0)
    over1 = [("link2", 1.0)] if inv2 else []
    over2 = ([] if inv2 else [("link1", 1.0)]) + ([] if inv3 else [("neck", 1.0)])
    overn = [("link2", 1.0)] if inv3 else []
    link1 = K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", l1_at2)), end_mm=end, over=over1)
    link2 = K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", l2_at2), ("hub3", l2_at3)), end_mm=end, over=over2)
    neck = K.strap_member("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), width=14.0, t=6.0, ramp_to=(("hub3", nk_at3), (None, 0)), over=overn)
    # order: a member that passes over another comes after it (fit_profiles keeps this order among `over` members)
    mem = {"link1": link1, "link2": link2, "neck": neck}; deps = {"link1": over1, "link2": over2, "neck": overn}
    order, left = [], ["link1", "neck", "link2"]
    while left:
        for n in left:
            if all(o in order for o, _ in deps[n]): order.append(n); left.remove(n); break
        else: raise ValueError("cyclic over relations")
    return K.Chain(members=hubs + [mem[n] for n in order], ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None, inv2=inv2, inv3=inv3))


def kin(F, p):
    """the fold law alone (no proximity): closure mask over the bench poses"""
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    _, ok, _ = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"]); return ok


def run(B, p, fixed_prof=None):
    """= docs/concepts/verify/spine-parked-j2-3r.py run() with this build: model checks + the verifier's top_check"""
    fp = K.fit_profiles
    if fixed_prof is not None:
        K.fit_profiles = lambda B_, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in fixed_prof.items()}
    try:
        r = K.evaluate(B, build, p); r = SPM.declared_audit(r, p); r = SPM.extras(B, r, p)
    finally:
        K.fit_profiles = fp
    keep = {k: v for k, v in r.items() if SPM._jsonable(v) and k != "checks"}
    keep["verifier"] = VER.top_check(B, r, p)
    return keep


def evaluate(B, params, fixed_prof=None):
    """-> (params, report). report['gap'] = the verifier's plain gap (v); +200 if the seat is not allowed, +100 if the
    report is not honest or a hub axis is not accessible"""
    p = snap(params)
    if not seat_ok(p["az"], p["el"]):
        return p, dict(gap=200.0, honest=False, audit=["J1 seat outside the back / acromion-top region (ruling 4)"])
    B.reset(); r = run(B, p, fixed_prof); v = r["verifier"]
    honest = bool(r.get("honest")) and v["hub_F_ok"]
    out = dict(r, model_gap=r["gap"], v=v["v"], v_near1=v["v_near1"], near=v["v_near1"]["gap"], hub_F=v["hub_F"],
               hub_F_ok=v["hub_F_ok"], min_metal_all_faces=v["min_metal_all_faces"], top_contact_poses=v["top_contact_poses"],
               top_contact_who=v["top_contact_who"], strap_levels=v["strap_levels"], mode=B.mode)
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): out[k] = v["v"][k]
    if not honest: out["gap"] = float(out["gap"]) + 100.0
    out["honest"] = honest
    return p, out


def attribute(B, p, r):
    """every lost workspace pose / clip frame by first cause (fold side, K2 jam, parts, contact by member), overhead"""
    L = B._kit_last; ch, take, ok, hit, pts = L["chain"], L["take"], L["ok"], L["hit"], L["pts"]
    F = B._kitF; okk = kin(F, p)
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1))); lo = abs(p["a1"] - p["a2"]) + p["margin"]
    el = np.array([q["elev"] for q in B.poses]); pl = np.array([q["plane"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind])
    cause = []
    for j in range(len(B.res)):
        if B.res[j] is not None and float(np.min(B.res[j])) >= 0: cause.append("taken")
        elif not okk[j]: cause.append("fold_folded" if th[j] < lo else "fold_stretched")
        elif not ok[j]: cause.append("jam_K2")
        elif hit[j]: cause.append("parts")
        else: cause.append("contact")
    cause = np.array(cause)
    # which member is inside the skin at a contact pose (underside / top / crown: the first < 0)
    who = {}
    for j in np.nonzero(cause == "contact")[0]:
        best = (np.inf, None)
        for m in ch.members:
            X = pts[m.name][j]; d0 = K.dist_many(B, np.full(len(X), j), X).min()
            n = np.linalg.norm(X, axis=-1, keepdims=True); d1 = K.dist_many(B, np.full(len(X), j), X * (n + m.t) / n).min()
            d = min(d0, d1)
            if d < best[0]: best = (d, m.name)
        who[int(j)] = best[1]
    regions = dict(overhead=el >= 140, across=(pl >= 100) & (el >= 40),
                   behind=np.array([("back" in B.clip[i].lower()) or (pl[i] < -30 and el[i] > 20) for i in range(len(B.idx))]))
    tab = {}
    for name, sel in [("ws", ws), ("clip", ~ws)] + [(k, v & ws) for k, v in regions.items()]:
        cs = cause[sel]; tab[name] = dict(n=int(sel.sum()), **{c: int((cs == c).sum()) for c in ("taken", "fold_folded", "fold_stretched", "jam_K2", "parts", "contact")})
    cw = {}
    for j, m in who.items(): cw[m] = cw.get(m, 0) + 1
    return dict(table=tab, contact_by_member=cw, kin_ws=round(float(okk[ws].mean()), 4), kin_overhead=round(float(okk[ws & regions["overhead"]].mean()), 4),
                th_ws_p5_p95=[round(float(np.percentile(th[ws], 5)), 1), round(float(np.percentile(th[ws], 95)), 1)],
                window=[round(lo, 1), round(min(p["a1"] + p["a2"], 360 - p["a1"] - p["a2"]) - p["margin"], 1)],
                inband_member=r.get("inband_member"))


if __name__ == "__main__":
    par = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].startswith("{") else {}
    nc, nw = (int(x) for x in os.environ.get("ZC_BENCH", "60,160").split(","))
    B = K.bench(nc, nw); t = time.time(); p, r = evaluate(B, par)
    print(json.dumps({k: r.get(k) for k in ("gap", "near", "model_gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                            "hub_F", "min_metal_all_faces", "top_contact_poses", "inband_member", "overhead", "mode")}, default=float),
          f"{time.time() - t:.1f}s", flush=True)
    if "--attr" in sys.argv: print(json.dumps(attribute(B, p, r), default=float))
