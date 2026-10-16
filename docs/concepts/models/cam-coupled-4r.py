"""cam-coupled-4r: a spherical 4R whose spare coordinate is SET by a roller pin on link 2's tail running in a
scapula-fixed spherical slot (catalogue id cam-coupled-4r, family "redundant 4R, determined spare").

Chain (every joint axis through GH, every hub the v5 O20 stack):
  scapula handler -> base (+ the S-fixed slot plate) -> J1 (O20, ACTIVE) -> link 1 (12 x 3 Ti, arc a1) -> J2 (O20,
  PASSIVE, scheduled by the slot) -> link 2 (12 x 3, arc a2; a tail strap from J2 to an MR63 roller pin) -> J3 (O20,
  ACTIVE) -> link 3 (12 x 3, arc a3) -> J4 (O20, ACTIVE, humerus-fixed axis) -> K7 neck -> BOTTOM -> cuff.
The pin on link 2 (angle tr from J2's axis, azimuth tp from link 2's direction: 180 = the tail continues link 2 back past
J2) runs in the small-circle slot {x : x . n = cos beta} of an S-fixed groove plate (n = bvec(n_az, n_el) in the scapula
frame). DOF: 4 bodies x 3 - 4 x 2 (J1-J4) - 1 (a point held on a curve) = 3 = the arm. ACTIVE J1, J3, J4. PASSIVE J2,
the pin's slide along the slot and the roller's roll: all set by the closure. The pin's position depends on q1 and q2
only (it is fixed in link 2), so the slot is a law q2 = f(q1) wherever d(pin . n)/dq2 != 0 (the cam transmits): the
arm orientation is an exact function of the three active readings (no sensed passive), and nothing sags (R17).

Kinematics per pose (vectorised): scan the J1 azimuth q1 (p2 on the a1 cone about u1) over 360 x 1 deg; p3 = the
two-circle closure of p2 (arc a2) and u4 (arc a3) on branch s3 (K.closure, fold margin `margin` = K.FOLD_MARGIN);
g(q1) = pin . n - cos beta; sign changes between valid neighbours are refined by 40 bisections (residual < 1e-9
rad). Assembly mode = the sign of dg/dq1 (`mode`): a root cannot change it without a cam fold (dg/dq1 = 0), which the
hold rule rejects; with two roots of the mode, the one nearest the azimuth of u4 about u1 (+ q1_off) is taken (pose-
local; K2 dense continuity drops any frame where this rule would switch roots along a clip).
A pose is TAKEN only if (on top of the kit's K2 / K6 / skin rules):
  * a root exists on the mode, the J3 dyad (p2, p3, u4) keeps the fold margin;
  * the cam transmits: pa = |t2 . nt| / |t2| >= pa_min (t2 = pin velocity per unit J2 at fixed J1, nt = slot normal
    on the sphere; pa = cos of the pressure angle) and 70 |t2 . nt| >= hold_mm (mm of cross-slot pin travel per rad of
    J2: the roller's 0.05 mm play then costs <= 0.05 / hold_mm rad of J2);
  * the actuated map (J1 with J2 slaved, J3, J4) is not singular: the effective J1 axis w1 = u1 + f'(q1) p2 stays >=
    sing_deg out of the plane of p3 and u4;
  * the pin stays inside the cut slot [s_c - s_half, s_c + s_half] (slot coordinate = azimuth of the pin about n).
Metal: O20 hubs at J1-J4 (flat, K4), straps link 1-3 (K5; link 2 / link 3 over link 1, the neck and the slot plate;
link 1 over the slot plate), the tail (12 x 3 strap from J2 to the pin + 6 mm pad past it, link 2's body, over link 1
and the slot plate), the K7 neck, and the slot plate: an S-fixed spherical groove plate (kind 'cap': ONE radius, so the
roller runs at one radius) 14 mm wide (6.1 slot for the MR63 3 x 6 x 2.5 roller + 2 x 4 mm walls), 4 mm thick, over the
cut arc + 6 mm at both ends. The roller pin (M3 shoulder screw) reaches from the tail's underside into the groove:
its length is reported (pin_len_mm). The slot's cut arc is set by a KINEMATIC pre-pass (evaluate()): the pin's slot
coordinate over the closing poses, trimmed to the [pct_lo, pct_hi] percentiles; frozen thereafter.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cam-coupled-4r.py [check|redteam] ['<json params>']
    hooks: evaluate(B, params) -> (params, report) (tools/concept_cma.py), bench_eval (tools/concept_sweep.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/cam-coupled-4r.py frozen '<json params>' --out R.json [--redteam]
"""
import functools, importlib.util, inspect, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("spine_parked_ref", os.path.join(os.path.dirname(os.path.abspath(__file__)), "spine-parked-j2-3r.py"))
SP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SP)   # crown / wall check, near-touch, overhead, red team

ID = "cam-coupled-4r"
NAME = "Cam-coupled 4R: a roller on link 2's tail in a scapula-fixed slot schedules the spare (J2)"
D2R = math.pi / 180
# seeds: park4's frozen seats (round-4 four-dof lens: az 102.7, el 68.0, a1 37.6, a2 60, a3 22.3, J4 = wdir(81.36, -14.61))
PARAMS = dict(az=102.74, el=67.99, wd=81.36, wa=-14.61, a1=37.6, a2=60.0, a3=22.31, s3=-1, mode=1, q1_off=0.0,
              tr=25.0, tp=180.0, n_az=102.74, n_el=67.99, beta=50.0, s_c=0.0, s_half=180.0, pct_lo=0.0, pct_hi=100.0,
              pa_min=0.25, hold_mm=8.0, sing_deg=K.FOLD_MARGIN, margin=K.FOLD_MARGIN,
              width=12.0, t_link=3.0, q=0.98, slot_w=14.0, slot_t=4.0, pad=6.0, near=0)
NQ = 360
ELEV_OVER = 140.0


def _rot(k, v, ang):
    c, s = np.cos(ang)[..., None], np.sin(ang)[..., None]
    return v * c + np.cross(k, v) * s + k * (k * v).sum(-1, keepdims=True) * (1 - c)


def _slot_frame(p):
    n = K.bvec(p["n_az"], p["n_el"]); e1 = K.unit(np.cross(n, [0.0, 1.0, 0.0]) + 1e-9); e2 = np.cross(n, e1)
    return n, e1, e2


class Kin:
    """kinematics of one design on frames F (pose-local)"""
    def __init__(self, F, p):
        self.p = p; self.u1 = F.S(K.bvec(p["az"], p["el"])); self.u4 = F.HG(K.wdir(p["wd"], p["wa"]))
        n, e1, e2 = _slot_frame(p); self.n = F.S(n); self.e1 = F.S(e1); self.e2 = F.S(e2)
        ref = F.S([0.0, 1.0, 0.0]); self.a = K.unit(ref - (ref * self.u1).sum(-1, keepdims=True) * self.u1)  # q1 = 0 direction
        self.b = np.cross(self.u1, self.a); self.cb = math.cos(p["beta"] * D2R)
        self.tr, self.tp = p["tr"] * D2R, p["tp"] * D2R

    def at(self, I, q1):
        """chain at poses I (k,) and J1 azimuths q1 (k,) rad -> p2, p3, pin, ok3, margin"""
        u1, u4 = self.u1[I], self.u4[I]; A1 = self.p["a1"] * D2R
        p2 = math.cos(A1) * u1 + math.sin(A1) * (np.cos(q1)[:, None] * self.a[I] + np.sin(q1)[:, None] * self.b[I])
        p3, ok3, mar = K.closure(p2, u4, self.p["a2"], self.p["a3"], self.p["s3"], margin_deg=self.p["margin"])
        pin = self.pin(p2, p3)
        return p2, p3, pin, ok3, mar

    def pin(self, p2, p3):
        u = K.unit(p3 - (p3 * p2).sum(-1, keepdims=True) * p2); v = np.cross(p2, u)
        return math.cos(self.tr) * p2 + math.sin(self.tr) * (math.cos(self.tp) * u + math.sin(self.tp) * v)

    def g(self, I, q1):
        p2, p3, pin, ok3, _ = self.at(I, q1); return (pin * self.n[I]).sum(-1) - self.cb, ok3

    def solve(self):
        P = len(self.u1); q = np.arange(NQ) * (2 * math.pi / NQ) - math.pi
        I = np.repeat(np.arange(P), NQ); Q = np.tile(q, P)
        G, OK = self.g(I, Q); G = G.reshape(P, NQ); OK = OK.reshape(P, NQ)
        G2 = np.concatenate([G, G[:, :1]], 1); O2 = np.concatenate([OK, OK[:, :1]], 1)
        br = (np.sign(G2[:, :-1]) != np.sign(G2[:, 1:])) & O2[:, :-1] & O2[:, 1:]
        sl = np.sign(G2[:, 1:] - G2[:, :-1])
        pi_, ki = np.nonzero(br & (sl == float(self.p["mode"])))
        q1 = np.full(P, np.nan)
        if len(pi_):
            lo = q[ki].copy(); hi = lo + 2 * math.pi / NQ; glo = G[pi_, ki].copy()
            for _ in range(40):
                mid = 0.5 * (lo + hi); gm, _ = self.g(pi_, mid); same = np.sign(gm) == np.sign(glo)
                lo = np.where(same, mid, lo); glo = np.where(same, gm, glo); hi = np.where(same, hi, mid)
            r = 0.5 * (lo + hi)
            # nearest root to the azimuth of u4 about u1 (+ q1_off): pose-local assembly choice
            u4 = self.u4[pi_]; az4 = np.arctan2((u4 * self.b[pi_]).sum(-1), (u4 * self.a[pi_]).sum(-1)) + self.p["q1_off"] * D2R
            d = np.abs((r - az4 + math.pi) % (2 * math.pi) - math.pi)
            order = np.lexsort((d, pi_)); first = np.r_[True, pi_[order][1:] != pi_[order][:-1]]
            sel = order[first]; q1[pi_[sel]] = r[sel]
        return q1


def kinematics(F, p):
    """-> dict with q1 (P,) rad (nan = no root), p2, p3, pin, ok (P,), slot coord s (deg), pa, hold, sing (deg)"""
    kn = Kin(F, p); q1 = kn.solve(); P = len(q1); has = np.isfinite(q1); q1z = np.where(has, q1, 0.0); I = np.arange(P)
    p2, p3, pin, ok3, mar = kn.at(I, q1z)
    # cam transmission at fixed J1: pin velocity per unit J2 = p2 x pin
    t2 = np.cross(p2, pin); nt = kn.n - (kn.n * pin).sum(-1, keepdims=True) * pin; ntn = np.linalg.norm(nt, axis=-1) + 1e-12
    t2n = (t2 * nt).sum(-1) / ntn
    pa = np.abs(t2n) / (np.linalg.norm(t2, axis=-1) + 1e-12); hold = 70.0 * np.abs(t2n)
    # slaved law f'(q1) = -(dg/dq1 at fixed q2) / (dg/dq2): pin velocity per unit J1 at fixed J2 = u1 x pin
    t1n = (np.cross(kn.u1, pin) * nt).sum(-1) / ntn; fp = -t1n / np.where(np.abs(t2n) < 1e-9, 1e-9, t2n)
    w1 = K.unit(kn.u1 + fp[:, None] * p2); n34 = K.unit(np.cross(p3, kn.u4))
    sing = np.degrees(np.arcsin(np.clip(np.abs((w1 * n34).sum(-1)), 0, 1)))
    s = np.degrees(np.arctan2((pin * kn.e2).sum(-1), (pin * kn.e1).sum(-1)))
    ds = (s - p["s_c"] + 180.0) % 360.0 - 180.0
    ok = has & ok3 & (pa >= p["pa_min"]) & (hold >= p["hold_mm"]) & (sing >= p["sing_deg"])
    inslot = np.abs(ds) <= p["s_half"]
    return dict(kn=kn, q1=q1z, has=has, p2=p2, p3=p3, pin=pin, ok=ok, okk=ok, inslot=inslot, s=s, ds=ds, pa=pa, hold=hold, sing=sing, margin=mar, fp=fp)


def slot_dirs(p):
    """S-frame directions of the slot plate: band of width slot_w (mm at r 70) about the small circle beta, over the
    cut arc s_c +- s_half + pad (2 mm grid at r_ref 70)"""
    n, e1, e2 = _slot_frame(p); bt = p["beta"] * D2R; rr = 70.0 * max(math.sin(bt), 0.05)
    half = min(180.0, p["s_half"] + math.degrees(p["pad"] / rr))
    ns = max(3, int(2 * half * D2R * rr / 2.0) + 1); S = (p["s_c"] + np.linspace(-half, half, ns)) * D2R
    cs = np.arange(-p["slot_w"] / 2, p["slot_w"] / 2 + 1e-6, 2.0) / 70.0
    D = [math.cos(bt + c) * n + math.sin(bt + c) * (math.cos(a) * e1 + math.sin(a) * e2) for c in cs for a in S]
    return np.array(D)


def build(B, F, p):
    k = kinematics(F, p); ok = k["ok"] & k["inslot"]
    kn = k["kn"]; u1, u4, p2, p3, pin = kn.u1, kn.u4, k["p2"], k["p3"], k["pin"]
    q = np.stack([K.axis_angle(u1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, u1, p3), K.axis_angle(p3, p2, u4),
                  K.axis_angle(u4, F.HG([0.0, -1, 0]), p3), k["s"]], -1)
    w = p["width"]; t = p["t_link"]; end = K.HUB_R + 2.0
    # tail: J2 -> pin, extended by `pad` mm past the pin (the roller pad)
    ang = np.arccos(np.clip((p2 * pin).sum(-1), -1, 1)); ext = ang + p["pad"] / 70.0
    hubs = [K.hub_member("hub1", u1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3"), K.hub_member("hub4", u4, "J4")]
    slot = K.Member("slot", F.S(slot_dirs(p)), kind="cap", t=p["slot_t"], width=p["slot_w"], joints=("J1",), cell=4.0)
    links = [K.strap_member("link1", u1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), over=[("slot", 1.0)], end_mm=end),
             K.strap_member("tail", p2, pin, ("J2",), ang=ext, width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0)),
                            over=[("link1", 1.0), ("slot", 1.0)], end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", 0.0)),
                            over=[("link1", 1.0), ("neck", 1.0), ("slot", 1.0)], end_mm=end),
             K.strap_member("link3", p3, u4, ("J3", "J4"), width=w, t=t, ramp_to=(("hub3", K.STACK), ("hub4", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0), ("slot", 1.0)], end_mm=end),
             K.neck_member(F, u4, joints=("J4",), ramps=(("hub4", 0.0), (None, 0)))]
    okr = ok
    info = dict(residual_deg=round(float(K.closure_residual(p2, u4, p3, p["a2"], p["a3"])[okr].max()), 6) if okr.any() else None,
                min_margin=round(float(k["margin"][okr].min()), 2) if okr.any() else None,
                pa_min_taken=round(float(k["pa"][okr].min()), 3) if okr.any() else None,
                hold_min_taken=round(float(k["hold"][okr].min()), 2) if okr.any() else None,
                sing_min_taken=round(float(k["sing"][okr].min()), 2) if okr.any() else None,
                cut_noroot=round(float(np.mean(~k["has"])), 4), cut_cam=round(float(np.mean(k["has"] & ~k["ok"])), 4),
                cut_slot=round(float(np.mean(k["ok"] & ~k["inslot"])), 4))
    return K.Chain(members=hubs + [slot] + links, ok=ok, q=q, joints=dict(J1=u1, J2=p2, J3=p3, J4=u4, JP=pin), info=info, hubless=("JP",))


def set_slot(B, p):
    """kinematic pre-pass: cut the slot over the [pct_lo, pct_hi] percentiles of the pin's slot coordinate over the poses
    that close (circular: centred on the circular mean)"""
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    k = kinematics(F, dict(p, s_half=180.0)); s = k["s"][k["ok"]]
    if len(s) < 3: return dict(p, s_c=0.0, s_half=180.0)
    c = math.degrees(math.atan2(np.sin(np.radians(s)).mean(), np.cos(np.radians(s)).mean()))
    d = (s - c + 180.0) % 360.0 - 180.0; lo, hi = np.percentile(d, [p["pct_lo"], p["pct_hi"]])
    return dict(p, s_c=round(c + 0.5 * (lo + hi), 4), s_half=round(0.5 * (hi - lo) + 0.25, 4))


_EXTRAS_SRC = inspect.getsource(SP.extras).replace(
    'rad = {"hub1": p["rad1"], "hub2": p["rad2"], "hub3": p["rad3"]}', 'rad = {m.name: K.HUB_R for m in hubs}')
_ns = dict(SP.__dict__); exec(_EXTRAS_SRC, _ns); extras = _ns["extras"]
assert "K.HUB_R for m in hubs" in _EXTRAS_SRC


def evaluate(B, params, preset=False):
    """tools/concept_cma.py hook -> (params, report). preset: keep s_c / s_half as given (frozen protocol)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"])))
    p["s3"] = 1 if float(p["s3"]) >= 0 else -1; p["mode"] = 1 if float(p["mode"]) >= 0 else -1
    for a in ("a1", "a2", "a3"): p[a] = min(150.0, max(15.0, float(p[a])))
    p["tr"] = min(80.0, max(8.0, float(p["tr"]))); p["beta"] = min(170.0, max(5.0, float(p["beta"])))
    p["pct_lo"] = min(20.0, max(0.0, float(p["pct_lo"]))); p["pct_hi"] = min(100.0, max(80.0, float(p["pct_hi"])))
    if not preset: p = set_slot(B, p)
    r = K.evaluate(B, build, p); r = extras(B, r, p)
    L = B._kit_last; take = L["take"]; prof = L["prof"]
    r["slot_arc_deg"] = round(2 * p["s_half"], 1); r["slot_len_mm"] = round(2 * p["s_half"] * D2R * float(np.median(prof["slot"])) * math.sin(p["beta"] * D2R), 1)
    # roller pin length: tail underside over the pin minus the slot plate's groove floor (mm), over taken poses
    r["pin_len_mm"] = round(float(np.median(prof["tail"][-12:]) - float(np.median(prof["slot"]))), 1)
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for kk in ("reach", "follow", "inband14", "contact"): r[kk + "_plain"] = r[kk]; r[kk] = r["near1"][kk]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SP._jsonable(v)}


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast (slot cut there too), freeze every underside / hub level / slot arc, wear on Bench(big)"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if SP._jsonable(v) and k not in ("checks",)}
    res["params_frozen"] = pf
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        _, r = evaluate(Bb, pf, preset=True)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin", "overhead", "inband_member")}, flush=True)
    if "--redteam" in sys.argv: SP.redteam(Bb, pf, r)
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
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), "margin", r.get("min_margin"))
    print("cam", {k: r.get(k) for k in ("pa_min_taken", "hold_min_taken", "sing_min_taken", "cut_noroot", "cut_cam", "cut_slot", "slot_arc_deg", "slot_len_mm", "pin_len_mm")},
          "slot", p["s_c"], p["s_half"])
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    if mode == "redteam": SP.redteam(B, p, r)
