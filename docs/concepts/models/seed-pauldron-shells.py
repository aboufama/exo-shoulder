"""seed-pauldron-shells: nested sliding shells (a pauldron) + a C-ring on the upper arm, on the shared kit
(tools/concept_kit.py, docs/concepts/KIT.md). 3 ACTIVE DOF (J1, J2, J3) + 1 passive slide (cuff along the humerus).

Topology (scapula handler -> user's upper-arm cuff):
    base shell on the scapula handler carrying TRACK 1 (a T-slot channel on a band at colatitude g1 about u1, through
    GH) --J1: shell 1's slider runs inside track 1--> shell 1 = WEB 1 (skin-fitted plate) + TRACK 2 (channel at
    colatitude g2 about u2) --J2: shell 2's slider runs inside track 2--> shell 2 = WEB 2 + the CARRIAGE --J3: the
    carriage runs on the C-RING (track about u3 = a humerus-fixed axis through GH, colatitude gamma)--> the ring is
    held on the user's cuff by a passive slide along the humerus (NECK to BOTTOM's bar, K7).
Kinematics = a spherical 3R: u1 fixed in the scapula, u3 fixed in the humerus (near its long axis: the C-ring takes the
axial rotation), u2 by the K1 two-circle closure (|u1.u2| = cos a1, u2.u3 = cos a2). The morphology's own idea is the
JOINT REALISATION: no O20 hubs at the axes; each revolute is a large-diameter sliding pair concentric with GH (iglidur
liner), a band 7 mm thick (floor 2 + slider 2 + lips 2 + liner 1) spread over the travelled ARC only, instead of a
20 mm disc with a 12.25 mm crown on the axis.

Spec corrections (said in docs/concepts/seed-pauldron-shells.md): "shell i rotates about u_i" needs a guide that holds
the other two rotations and retains the shell: modelled as the T-slot channel + slider; a shell is NOT a full sphere
cap: only the slide bands must be surfaces of revolution about their axis (one radius per band here: 'cap'), the webs
between them follow the skin (K3 'free' straps, 60 deg climb), which is strictly closer than the spec's
one-radius-per-shell lames. The C-ring as in seed-2r-cring (track 6 radial x 8 axial, carriage 25 x 12 x 6).

Parts (every one at real size, sampled 2 mm at r_ref 70 like the kit straps):
  track1  band g1 +- band_w/2 about u1, azimuth = the slider travel over every closing bench pose + the slider length
          (a full ring if that exceeds 360), 7 mm, one radius (fitted: clears every pose it takes);
  track2  same about u2 (fixed in shell 1, azimuth from u1), colatitude g2;
  ring    C-track band gamma +- 4 mm about u3, azimuth = carriage travel + carriage arc, 6 mm, one radius;
  carriage 25 x 12 x 6 on the ring at azimuth toward u2, 1 mm above the track;
  web1    strap (web_w x 3) on the great circle u1 -> u2 from the track-1 slider (lifted over the channel: track top
          + 1 mm) to track 2's outer edge (joined at its level);
  web2    strap on u2 -> u3 from the track-2 slider (over track 2 + 1 mm) to the carriage edge (at carriage level);
  neck    K7 14 x 6 strap from the ring to BOTTOM's bar; holds the passive slide (30 x 10 x 5, inside its footprint).
Rigid joins (web1-track2, web2-carriage, ring-neck) are fake joints W1..W3 so K6 exempts the weld zone (12 mm) only.
Taken = closure with margin, every slider/carriage inside its arc, dense continuity (K2), K6 collisions (>= 1 mm).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/seed-pauldron-shells.py check [key=value ...]   # PARAMS
    ... coarse                      # the coarse grid (appends to docs/concepts/sweeps/seed-pauldron-shells.json)
    ... refine <configs.jsonl>      # any list of configurations, one JSON per line (appends)
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "seed-pauldron-shells"
NAME = "Nested sliding shells (pauldron) + arm ring"
TRACK_T, RING_T, RING_W = 7.0, 6.0, 8.0                      # channel stack, C-track section (radial, axial)
CAR_L, CAR_W, CAR_T = 25.0, 12.0, 6.0                        # carriage
GAP = 1.0                                                    # running gap web over channel / carriage over track
R0 = 70.0                                                    # kit layout radius
# best honest configuration (sweep k = 88, gap 79.46 on Bench(60, 160)); the sweep started at the champion 3R's axes
# (rows/baseline-3r.json). wd ~ 0 + gamma > the arm = the spec's C-ring round the humerus axis (measured impossible).
# side1 / side2: track of J1 / J2 on the proximal (0) or distal (1) body; j2hub=1: O20 hub at J2 (hybrid);
# neck_c=1: the neck leaves from the ring's centre over the ring (no C-gap needed); cov<j>: share of the travel the arc holds.
PARAMS = dict(az=2.841, el=86.115, a1=83.025, a2=64.198, sigma=-1, margin=10.0, wd=83.944, wa=13.919,
              g1=16.0, g2=14.0, gamma=16.0, side1=1, side2=1, side3=1, band_w=12.0, slider_len=30.0, web_w=12.0,
              cov=1.0, q=0.98, cov2=1.0, cov3=0.9)
SWEEP_COARSE = dict(az=[100.0, 123.0, 145.0], el=[35.0, 50.0, 65.0], a1=[75.0, 90.0], a2=[75.0, 90.0], sigma=[-1, 1])


def band_dirs(k, ea, eb, g, w, lo, hi, step=2.0):
    """directions (P, m, 3) of a band about axis k (P, 3): colatitude g (deg) +- w/2 mm, azimuth lo..hi (deg, from ea
    toward eb), 2 mm grid at R0; full ring when hi - lo >= 360. Also returns the azimuth (deg) of each sample."""
    full = hi - lo >= 360.0
    cs, az = [], []
    for c in (g * K.D2R + np.arange(-w / 2, w / 2 + 1e-6, step) / R0):
        span = 2 * math.pi if full else (hi - lo) * K.D2R
        n = max(2, int(math.ceil(span * R0 * max(math.sin(c), 1e-3) / step)) + (0 if full else 1))
        ph = (lo * K.D2R + (np.arange(n) * span / n if full else np.linspace(0, span, n)))
        cs.append(np.full(n, c)); az.append(ph)
    c, ph = np.concatenate(cs), np.concatenate(az)
    D = (np.cos(c)[None, :, None] * k[:, None] + np.sin(c)[None, :, None] *
         (np.cos(ph)[None, :, None] * ea[:, None] + np.sin(ph)[None, :, None] * eb[:, None]))
    return K.unit(D), np.degrees(ph)


def perp(k, ref):
    a = K.unit(ref - (ref * k).sum(-1, keepdims=True) * k); return a, np.cross(k, a)


def arc(th, ok, cov, half):
    """circular range [lo, hi] (deg) holding share cov of the angles th[ok], widened by half each side"""
    v = th[ok]
    if not len(v): return 0.0, 360.0
    m = math.degrees(math.atan2(np.sin(np.radians(v)).mean(), np.cos(np.radians(v)).mean()))
    d = (v - m + 180) % 360 - 180
    lo, hi = (d.min(), d.max()) if cov >= 1 else (np.quantile(d, (1 - cov) / 2), np.quantile(d, (1 + cov) / 2))
    return m + lo - half, m + hi + half


def in_arc(th, lo, hi, half):
    if hi - lo >= 360.0: return np.ones(th.shape, bool)
    r = (th - lo) % 360.0
    return (r >= half - 1e-6) & (r <= hi - lo - half + 1e-6)


_ARCS = {}


def build(B, F, p):
    # ---- 1. kinematics: spherical 3R (u1 scapula, u3 humerus, u2 by the K1 closure) ----------------------------------
    b0 = K.bvec(p["az"], p["el"]); r0 = np.cross(b0, [0.0, 1.0, 0.0]) if abs(b0[1]) < 0.95 else np.cross(b0, [1.0, 0, 0])
    p1 = F.S(b0); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    hl = F.HG(K.wdir(90.0, 0.0))                               # a humerus-fixed reference (lateral)
    # joint j: axis k, a reference fixed in the proximal body (rp) and one in the distal body (rd); th = rp -> rd about k
    J = [(p1, F.S(r0), p2), (p2, p1, p3), (p3, p2, hl)]
    th = np.stack([K.axis_angle(k, rp, rd) for k, rp, rd in J], -1)
    g = [p["g1"], p["g2"], p["gamma"]]; side = [int(p["side1"]), int(p["side2"]), int(p["side3"])]
    wid = [p["band_w"], p["band_w"], RING_W]; mov = [p["slider_len"], p["slider_len"], CAR_L]
    hs = [math.degrees(mov[j] / 2 / (R0 * math.sin(g[j] * K.D2R))) for j in range(3)]       # half arc of the moving element
    # TRACK of joint j on the proximal body (side 0: frame of rp, the moving element at +th) or on the distal body
    # (side 1: frame of rd, the element at -th). A track on the body a web is WELDED to must reach that web's azimuth (0).
    fr = [perp(k, rd if side[j] else rp) for j, (k, rp, rd) in enumerate(J)]
    az = np.stack([-th[:, j] if side[j] else th[:, j] for j in range(3)], -1)
    key = (id(B), json.dumps(p, sort_keys=True))
    if F is getattr(B, "_kitF", None) or key not in _ARCS:    # travelled arcs measured on the full bench (every closing pose)
        _ARCS[key] = [arc(np.r_[az[ok, j], 0.0], np.ones(ok.sum() + 1, bool), p.get(f"cov{j + 1}", p["cov"]), hs[j]) for j in range(3)]
    arcs = _ARCS[key]
    hub2 = bool(p.get("j2hub", 0))                             # hybrid: J2 as an O20 hub (K4), rings at J1 and J3
    for j in range(3):
        if not (hub2 and j == 1): ok = ok & in_arc(az[:, j], *arcs[j], hs[j])
    if hub2: g = [g[0], 0.0, g[2]]
    ok &= (g[0] + g[1] + 4 < p["a1"]) & (g[1] + g[2] + 6 < p["a2"])

    # ---- 2. members -------------------------------------------------------------------------------------------------
    trk = []
    for j, nm in enumerate(("track1", "track2", "ring")):
        if hub2 and j == 1: trk.append(K.hub_member("hub2", p2, "J2")); continue
        D, _ = band_dirs(J[j][0], *fr[j], g[j], wid[j], *arcs[j])
        trk.append(K.Member(nm, D, kind="cap", t=TRACK_T if j < 2 else RING_T, width=wid[j], joints=(f"J{j + 1}",)))
    # J3's moving element = the carriage, on the body that does not carry the ring, centred at that body's azimuth
    k3, rp3, rd3 = J[2]; ca, cb = perp(k3, rp3 if side[2] else rd3)
    Dc, _ = band_dirs(k3, ca, cb, g[2], CAR_W, -hs[2], hs[2])
    car = K.Member("carriage", Dc, t=CAR_T, width=CAR_W, joints=("J3",), ramps=[(np.ones(Dc.shape[1], bool), "ring", RING_T + GAP)])
    lift = p["band_w"] / 2 + 4.0; welds = {}

    def web(name, ka, kb, ga, gb, A, end_a, end_b, **kw):
        """strap on the great circle ka -> kb from colatitude ga (from ka) to A - gb; ends 'weld' (outer edge of a
        track on the same body, at its level), 'slide' (the slider of that body inside a track: lifted over it) or
        'car' (the carriage edge, at its level)"""
        e = perp(ka, kb)[0]; s0, s1 = ga * K.D2R, A * K.D2R - gb * K.D2R; ramp = []
        for which, (kind, tname, w) in (("a", end_a), ("b", end_b)):
            if kind.startswith("hub"):                      # O20 hub: lower member at F (hub_lo), upper at F + STACK
                ramp.append((tname, 0.0 if kind == "hub_lo" else K.STACK)); continue
            off = (w / 2 + 1.0) / R0 if kind in ("weld", "car") else 0.0
            if which == "a": s0 += off
            else: s1 -= off
            ramp.append((tname, 0.0 if kind in ("weld", "car") else TRACK_T + GAP))
            if kind in ("weld", "car"): welds[f"{name}{which}"] = (tname,)
        ua = K.unit(np.cos(s0) * ka + np.sin(s0) * e); ub = K.unit(np.cos(s1) * ka + np.sin(s1) * e)
        js = tuple(f"{name}{w}" for w in "ab" if f"{name}{w}" in welds) + (("J2",) if hub2 else ())
        return K.strap_member(name, ua, ub, js, ang=s1 - s0, width=p["web_w"], t=3.0, ramp_to=tuple(ramp),
                              end_mm=max(lift, K.HUB_R + 2.0) if hub2 else lift, **kw), ua, ub

    A1, A2 = p["a1"], p["a2"]
    w1, w1a, w1b = web("web1", p1, p2, g[0], g[1], A1, ("weld" if side[0] else "slide", "track1", p["band_w"]),
                       ("hub_lo", "hub2", 0) if hub2 else ("slide" if side[1] else "weld", "track2", p["band_w"]))
    e2b = ("car", "carriage", CAR_W) if side[2] else ("weld", "ring", RING_W)
    w2over = [("web1", GAP), ("neck", GAP)] if p.get("w2over", 0) else []
    w2, w2a, w2b = web("web2", p2, p3, g[1], g[2], A2, ("hub_up", "hub2", 0) if hub2 else
                       ("weld" if side[1] else "slide", "track2", p["band_w"]), e2b, over=w2over)
    # neck (K7) from the humerus-side element of J3 (ring if side3, else the carriage) to BOTTOM's bar
    bar = F.H(K.unit(K.BAR0_H)); gr = g[2] * K.D2R
    if side[2] and p.get("neck_c", 0):   # variant: the neck starts at the ring's CENTRE (a spoke at ring level inside the
        src = "ring"; na = None          # ring, never under the carriage) and passes over the ring + carriage path: full ring OK
    elif side[2]:          # ring on the humerus: the neck leaves it in the middle of the C's gap (the carriage never goes there)
        src = "ring"; lo, hi = arcs[2]; gz = math.radians((lo + hi) / 2 + 180.0) if hi - lo < 360 else 0.0
        na = math.cos(gz) * fr[2][0] + math.sin(gz) * fr[2][1]
        if hi - lo >= 360 - 2 * math.degrees(9.0 / (R0 * math.sin(gr))): ok = ok & False   # no gap wide enough for the 14 mm neck
    else: na = perp(p3, hl)[0]; src = "carriage"
    nstart = p3 if na is None else K.unit(math.cos(gr) * p3 + math.sin(gr) * na)
    # K7 neck (14 x 6, = K.neck_member) passing OVER the ring and the carriage path wherever it crosses them (>= 1 mm)
    nover = [("ring", GAP), ("carriage", GAP)] if side[2] else []
    neck = K.strap_member("neck", nstart, bar, ("neck_a",), width=14.0, t=6.0, ramp_to=((src, 0.0), (None, 0)), over=nover)
    welds["neck_a"] = (src,)
    wpts = dict(web1a=w1a, web1b=w1b, web2a=w2a, web2b=w2b, neck_a=nstart)
    members = trk + [car, w1, neck, w2]
    by = {m.name: m for m in members}
    for wname, (other,) in welds.items(): by[other].joints = tuple(by[other].joints) + (wname,)   # weld zone: K6 exempt there only
    joints = dict(J1=p1, J2=p2, J3=p3, **{w: wpts[w] for w in welds})
    resid = K.closure_residual(p1, p3, p2, A1, A2)
    return K.Chain(members=members, ok=ok, q=th, joints=joints, hubless=tuple(j for j in joints if not (hub2 and j == "J2")),   # ring bearings + weld zones, no O20 hubs
                   info=dict(residual_deg=round(float(resid[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             arcs=[round(float(h - l), 1) for l, h in arcs]))


def grid(base, sw):
    keys = list(sw)
    return [dict(base, **dict(zip(keys, v))) for v in itertools.product(*(sw[k] for k in keys))]


SWP = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
# the k 0-33 grid ran with the champion's axes as base (az 2.4305, el 80.6763, a1 76.9018, a2 66.7492, wd 86.3277,
# wa 21.8297, sigma -1, g1/g2/gamma 12, q 0.95); every entry of the sweep file holds its full params
SWEEP = dict(g1=[12.0, 20.0], g2=[8.0, 14.0], gamma=[12.0, 20.0], cov2=[1.0, 0.9], cov3=[0.9, 0.8], sides=[(0, 0), (1, 1)])


def coarse():
    out = []
    for c in grid(dict(PARAMS, q=0.95), {k: v for k, v in SWEEP.items() if k != "sides"}):
        for s1, s2 in SWEEP["sides"]: out.append(dict(c, side1=s1, side2=s2))
    return out


def run(B, configs, best_gap=None):
    """evaluate configs in order, appending each to the sweep file as it finishes; an event at every new best gap"""
    rows = json.load(open(SWP)) if os.path.exists(SWP) else []
    best = min((r["gap"] for r in rows if r.get("honest")), default=None)   # only configurations that pass the kit audit count
    for p in configs:
        r = K.evaluate(B, build, dict(p))
        e = dict(k=len(rows), t=K.now(), params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 closure=r["closure"], collide=r["collide"], mass_g=r["mass_g"], honest=r["honest"], inband_member=r["inband_member"])
        rows.append(e); json.dump(rows, open(SWP + ".tmp", "w"), indent=1); os.replace(SWP + ".tmp", SWP)
        print(e["k"], e["gap"], e["reach"], e["follow"], e["inband14"], e["contact"], r["collide"], flush=True)
        if e["honest"] and (best is None or e["gap"] < best):
            best = e["gap"]
            K.log_event(f"seed-pauldron-shells new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, in-band 14 {e['inband14']}, contact {e['contact']}; config k={e['k']})")
    return rows


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160) if "small" not in a else K.bench(20, 40)
    if a[0] == "coarse": run(B, coarse())
    if a[0] == "refine": run(B, [json.loads(x) for x in open(a[1])])
    if a[0] == "check":
        p = dict(PARAMS)
        for kv in a[1:]:
            if "=" in kv: k_, v_ = kv.split("="); p[k_] = type(PARAMS.get(k_, 1.0))(float(v_))
        import time; t0 = time.time(); r = K.evaluate(B, build, p); print(round(time.time() - t0, 1), "s"); print(r)
