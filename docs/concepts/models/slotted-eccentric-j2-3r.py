"""slotted-eccentric-j2-3r: the zero-passive spherical 3R (O20 hubs at J1 / J2 / J3, user ruling 2026-10-16) with link 2
split at a passive knee K whose angle is SLAVED to q2 by a roller in a slot (catalogue id slotted-eccentric-j2-3r).

Chain: scapula handler -> base -> J1 (O20 hub, MR117-2RS pair, active) -> link 1 (12 x 3 Ti; carries the roller stud F:
hardened O2 dowel + MR52ZZ 2 x 5 x 2.5 roller in an O7 boss, on an arm link1f when F is off link 1's arc) -> J2 (active,
O20) -> crank 2a (12 x 3 Ti, arc b) -> knee K (passive pin: MR63ZZ pair in an O10 boss, 6.5 mm stack) -> link 2b
(12 x 3 Ti, arc c, K -> J3) + its slotted lever (17-4PH 2 mm plate, slot 2.6 H7 between 1.95 mm walls, a polyline
along the slot, widened by its own deviation) -> J3 (active, O20) -> member 3 = hub 3's arm-end plate + the K7 14 x 6
neck rigid to BOTTOM's bar.
Loop link 1 - crank - link 2b - roller-in-slot: spherical mobility 3 (4 - 1) - 2 * 2 (J2, K) - 2 (roller+slot: a
higher pair, 1 constraint) ... counted per body: bodies link 1, crank, 2b; J2 and K remove 2 each, the slot 1 -> the
knee angle psi is a fixed function of q2. With the human GH closing J1-J2-K-J3 (four GH-concurrent axes between two
fixed bodies: 1 internal freedom) the slot removes that freedom: every coordinate is set by the arm pose (R17).
Passive translations 0 (the roller rolls in the slot: a sliding/rolling pair, counted as 1 sliding pair).

Kinematics (per pose, everything is a function of th = angle(J1, J3) alone in link 1's frame):
  a2e(th) = soft clip of Ac + sl (th - Ac) into [Amin, Amax] (Ac = (Amin + Amax) / 2, width w): the effective J2-J3
  arc the knee makes; sl = 1 is the spec's clip(th) law (per-pose margin-optimal);
  p2 = closure(p1, p3, a1, a2e(th), sigma); fold margin min(th - |a1 - a2e|, a1 + a2e - th) >= margin;
  K = closure(p2, p3, b, c, sk), knee transmission psi in [psi_lo, 180 - psi_lo];
  F = roller seat fixed in link 1's frame at arc fF from J2, azimuth phiF from the J2 -> J1 arc (solved per config);
  the slot = the curve F traces in link 2b's polar frame about K, (d, gamma)(th).
Slot gate (per config, synthetic poses over the valid th run): q2 strictly monotone in th; d strictly monotone; d_min >=
  (rpin + 2.5 + 1) mm; the roller boss clears hub 2 (fF >= rad2 + 3.5 + 1 mm); the lever polyline clears hub 2 by
  rad2 + its half width + 1 mm; LOCK: at fixed th the four-bar's internal mode (p2 turned about p1, K re-closed) moves
  the roller ACROSS the slot - angle between that velocity and the slot tangent >= lock_min (50 deg = pressure angle
  <= 40) and its normal component >= 0.2 deg / deg. A config whose gate fails gets +100 on its gap and honest False.
lock=1 is the LOCKED CONTROL: knee rigid (a2e = a2), no pin, no stud, no lever: the plain 3R with link 2 through K.

Checks: the kit's (K3 march, K2 dense incl. every axis J1 J2 K J3 F, K6 with same-body exemption, honest post heights,
crowns + walls of every hub / pin / stud skin-checked, near-touch, overhead split) via dwell-fourbar-knee-3r.py's
helpers (imported, unchanged).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/slotted-eccentric-j2-3r.py [check|redteam|gate] ['<json>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/slotted-eccentric-j2-3r.py frozen '<json params>' --out R.json
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("dwell_fourbar_knee_3r", os.path.join(os.path.dirname(os.path.abspath(__file__)), "dwell-fourbar-knee-3r.py"))
DW = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(DW)   # patches K.collisions (same body) + K.fit_profiles (posts)
DW.PIN[3.5] = "roller stud: hardened O2 dowel + MR52ZZ (2 x 5 x 2.5) roller in an O7 Ti boss on link 1, post = link + 1 + lever 2 + 1"

ID = "slotted-eccentric-j2-3r"
NAME = "Eccentric J2 crank + slotted-lever cam: link 2's arc set by q2 (two-sided fold lever) on the zero-passive 3R, O20"
D2R = math.pi / 180
R_NOM = 62.0                    # mm: nominal radius of hub 2 / knee / lever (mm <-> deg for the slot gate only)
PARAMS = dict(az=97.7506, el=65.294, a1=38.0901, wd=90.0506, wa=-9.2038, sigma=-1, margin=5.0, width=12.0, t_link=3.0,
              q=0.97, rad1=10.0, rad2=10.0, rad3=10.0, end_extra=0.0,
              Amin=60.0, Amax=90.0, w=3.0, sl=1.0, b=25.0, c=72.0, sk=1, psi_lo=15.0,
              fF=None, phiF=None, rpin=5.0, pin_t=6.5, t_lev=2.0, lock_min=50.0, g_min=0.2,
              a2=74.2679, lock=0, near=0, ov=1)
ang, tangent, unit = DW.ang, DW.tangent, K.unit


def closure_v(b, w, a1, a2, sigma):
    """K1 with per-pose arcs a1, a2 (deg, arrays ok): p with angle(p, b) = a1, angle(p, w) = a2, branch sign p.(b x w)"""
    b, w = unit(b), unit(w); c = np.clip((b * w).sum(-1), -1, 1); n = unit(np.cross(b, w))
    A1, A2 = np.radians(a1), np.radians(a2); den = 1 - c ** 2 + 1e-12
    A = (np.cos(A1) - c * np.cos(A2)) / den; Bq = (np.cos(A2) - c * np.cos(A1)) / den
    p0 = A[..., None] * b + Bq[..., None] * w; h2 = 1 - (p0 * p0).sum(-1)
    return p0 + sigma * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 1e-9


def a2e_of(th, p):
    if p.get("lock"): return np.full(np.shape(th), float(p["a2"]))
    lo, hi = float(p["Amin"]), float(max(p["Amax"], p["Amin"] + 0.5)); w = max(0.3, float(p["w"]))
    x = 0.5 * (lo + hi) + float(p["sl"]) * (np.asarray(th, float) - 0.5 * (lo + hi))
    return lo + w * np.logaddexp(0, (x - lo) / w) - w * np.logaddexp(0, (x - hi) / w)


def geom(p1, p3, p, F=True):
    """the chain for axes p1 (J1), p3 (J3): p2, K, ok + parts (all arrays (n, 3))"""
    th = ang(p1, p3); a2e = a2e_of(th, p); a1 = float(p["a1"])
    p2, ok2 = closure_v(p1, p3, np.full(th.shape, a1), a2e, p["sigma"])
    mg = np.minimum.reduce([th - np.abs(a1 - a2e), a1 + a2e - th, 360 - a1 - a2e - th])
    Kw, okk = closure_v(p2, p3, np.full(th.shape, float(p["b"])), np.full(th.shape, float(p["c"])), p["sk"])
    psi = ang(tangent(Kw, p2), tangent(Kw, p3))
    ok = ok2 & okk & (mg >= p["margin"]) & (psi >= p["psi_lo"]) & (psi <= 180 - p["psi_lo"])
    return dict(th=th, a2e=a2e, p2=p2, K=Kw, psi=psi, ok=ok, mg=mg)


def seat_F(p1, p2, fF, phiF):
    e = tangent(p2, p1); n = np.cross(p2, e)
    return math.cos(fF * D2R) * p2 + math.sin(fF * D2R) * (math.cos(phiF * D2R) * e + math.sin(phiF * D2R) * n)


def polar_K(Kw, p3, X):
    """(d, gamma) of points X in link 2b's polar frame about K (gamma from the K -> J3 arc)"""
    return ang(Kw, X), K.axis_angle(Kw, p3, X)


def from_polar(Kw, p3, d, g):
    t = tangent(Kw, p3); n = np.cross(Kw, t); d, g = np.radians(d), np.radians(g)
    return np.cos(d)[..., None] * Kw + np.sin(d)[..., None] * (np.cos(g)[..., None] * t + np.sin(g)[..., None] * n)


def _xy(d, g): return np.stack([d * np.cos(np.radians(g)), d * np.sin(np.radians(g))], -1) * D2R * R_NOM   # mm, planar


def _seg_dist(P, A, B):
    AB = B - A; t = np.clip(((P - A) * AB).sum(-1) / np.maximum((AB * AB).sum(-1), 1e-12), 0, 1)
    return np.linalg.norm(P - (A + t[..., None] * AB), axis=-1)


_CACHE = {}
GKEYS = ("a1", "sigma", "margin", "Amin", "Amax", "w", "sl", "b", "c", "sk", "psi_lo", "fF", "phiF", "rad2", "rpin", "lock",
         "lock_min", "g_min", "a2")


def slot_design(p):
    """valid th run, slot gate, roller seat F (grid-solved unless given) and the lever polyline in 2b's polar frame"""
    key = tuple((k, None if p.get(k) is None else round(float(p[k]), 6)) for k in GKEYS)
    if key in _CACHE: return _CACHE[key]
    th = np.arange(1.0, 179.0, 0.25); z = np.array([0.0, 0, 1])
    p1 = np.broadcast_to(z, (len(th), 3)); p3 = np.stack([np.sin(th * D2R), 0 * th, np.cos(th * D2R)], -1)
    G = geom(p1, p3, p); ok = G["ok"]
    runs, cur = [], []
    for i in range(len(th)):
        if ok[i]: cur.append(i)
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    out = dict(ok=False, lo=0.0, hi=-1.0, gate=dict(why="no valid th run"))
    if not runs: _CACHE[key] = out; return out
    run = np.array(max(runs, key=len)); lo, hi = float(th[run[0]]), float(th[run[-1]])
    out.update(lo=lo, hi=hi)
    if p.get("lock"):
        out.update(ok=True, gate=dict(lock=True)); _CACHE[key] = out; return out
    s = run[::2]; P1, P3, P2, KK = p1[s], p3[s], G["p2"][s], G["K"][s]; ths = th[s]
    q2 = K.axis_angle(P2, P1, KK); dq2 = np.diff(np.unwrap(q2 * D2R) / D2R)
    q2mono = bool(np.all(dq2 > 1e-3) or np.all(dq2 < -1e-3))
    # internal four-bar mode at fixed th: p2 turned about p1 by +-dn, K re-closed with fixed (b, c)
    dn = 0.2
    def turned(sgn):
        ax = P1; v = P2; c, si = math.cos(sgn * dn * D2R), math.sin(sgn * dn * D2R)
        p2t = v * c + np.cross(ax, v) * si + ax * (ax * v).sum(-1, keepdims=True) * (1 - c)
        kt, okt = closure_v(p2t, P3, np.full(len(ths), float(p["b"])), np.full(len(ths), float(p["c"])), p["sk"])
        return p2t, kt
    p2a, ka = turned(+1); p2b, kb = turned(-1)
    rmm = lambda mm: mm / R_NOM / D2R                        # mm -> deg at R_NOM
    fF_min = rmm(p["rad2"] + 3.5 + 1.0); d_req = rmm(p["rpin"] + 2.5 + 1.0)
    if p.get("fF") is not None:
        cands = [(float(p["fF"]), float(p["phiF"]))]
    else:
        cands = [(f, ph) for f in np.arange(math.ceil(fF_min), 40.0, 2.0) for ph in np.arange(-90.0, 90.1, 7.5)]
    best = None; stats = dict(n=len(cands), mono=0, dmin=0, lock=0, lever=0)
    for fF, phF in cands:
        F0 = seat_F(P1, P2, fF, phF); d, g = polar_K(KK, P3, F0)
        dd = np.diff(d)
        if not (np.all(dd > 1e-3) or np.all(dd < -1e-3)): continue
        stats["mono"] += 1
        if d.min() < d_req or fF < fF_min - 1e-9: continue
        stats["dmin"] += 1
        da, ga = polar_K(ka, P3, seat_F(P1, p2a, fF, phF)); db, gb = polar_K(kb, P3, seat_F(P1, p2b, fF, phF))
        sd = np.sin(d * D2R)
        vi = np.stack([(da - db) / (2 * dn), sd * (((ga - gb + 180) % 360) - 180) / (2 * dn)], -1)       # deg / deg internal
        tl = np.stack([np.gradient(d, ths), sd * np.gradient(np.unwrap(g * D2R) / D2R, ths)], -1)        # slot tangent
        tln = tl / np.maximum(np.linalg.norm(tl, axis=-1, keepdims=True), 1e-9)
        cr = np.abs(vi[:, 0] * tln[:, 1] - vi[:, 1] * tln[:, 0]); nv = np.linalg.norm(vi, axis=-1)
        lockang = np.degrees(np.arcsin(np.clip(cr / np.maximum(nv, 1e-9), 0, 1)))
        if lockang.min() < p["lock_min"] or cr.min() < p["g_min"]: continue
        stats["lock"] += 1
        # lever polyline in 2b's polar frame: K -> slot start (- ext) -> mid -> slot end (+ ext)
        ext = rmm(2.5 + 1.95); o = np.argsort(d); ds, gs = d[o], np.unwrap(g[o] * D2R) / D2R
        nodes_d = np.array([0.0, max(0.0, ds[0] - ext), 0.5 * (ds[0] + ds[-1]), ds[-1] + ext])
        nodes_g = np.array([gs[0], gs[0], np.interp(nodes_d[2], ds, gs), gs[-1]])
        XY = _xy(nodes_d, nodes_g); S = _xy(ds, gs)
        dev = np.min(np.stack([_seg_dist(S, XY[i], XY[i + 1]) for i in range(1, 3)], 0), 0).max()
        width = max(6.5, 2.6 + 2 * 1.95 + 2 * dev)
        # lever clearance from hub 2 over the run
        Lw = np.stack([from_polar(KK, P3, np.full(len(ths), nd), np.full(len(ths), ng)) for nd, ng in
                       zip(np.linspace(nodes_d[1], nodes_d[3], 12), np.interp(np.linspace(nodes_d[1], nodes_d[3], 12), nodes_d[1:], nodes_g[1:]))], 1)
        clear = float((ang(P2[:, None, :], Lw).min()) * D2R * R_NOM - width / 2)
        if clear < p["rad2"] + 1.0: continue
        stats["lever"] += 1
        score = float(lockang.min()) - 5 * max(0.0, width - 8.0) + 0.2 * min(clear - p["rad2"] - 1.0, 10.0)
        if best is None or score > best[0]:
            best = (score, fF, phF, dict(nodes_d=nodes_d.tolist(), nodes_g=nodes_g.tolist(), width=round(width, 2), dev_mm=round(float(dev), 2),
                                         lock_min=round(float(lockang.min()), 1), g_min=round(float(cr.min()), 3), d=[round(float(ds[0]), 1), round(float(ds[-1]), 1)],
                                         lever_clear_hub2=round(clear, 1), slot_len_mm=round(float(np.linalg.norm(np.diff(S, axis=0), axis=-1).sum()), 1)))
    gate = dict(q2_monotone=q2mono, stats=stats, q2_range=[round(float(q2.min()), 1), round(float(q2.max()), 1)])
    if best is not None and q2mono:
        gate.update(best[3]); out.update(ok=True, fF=best[1], phiF=best[2], lever=best[3], gate=gate, passed=True)
    else:
        gate["why"] = "q2 not monotone" if not q2mono else "no roller seat passes (mono / d_min / lock / lever)"
        out.update(ok=True, passed=False, gate=gate, fF=float(p.get("fF") or 20.0), phiF=float(p.get("phiF") or 0.0),
                   lever=dict(nodes_d=[0.0, 8.0, 20.0, 32.0], nodes_g=[0.0] * 4, width=6.5))
    if len(_CACHE) > 64: _CACHE.clear()
    _CACHE[key] = out; return out


def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    sd = slot_design(p); G = geom(p1, p3, p); p2, Kw, th = G["p2"], G["K"], G["th"]
    ok = G["ok"] & (th >= sd["lo"]) & (th <= sd["hi"])
    lock = bool(p.get("lock"))
    r1, r2, r3 = float(p["rad1"]), float(p["rad2"]), float(p["rad3"]); w, t = p["width"], p["t_link"]
    end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    hubs = [K.hub_member("hub1", p1, "J1", rad=r1), K.hub_member("hub2", p2, "J2", rad=r2), K.hub_member("hub3", p3, "J3", rad=r3)]
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    knee = K.axis_angle(Kw, p2, p3)
    q = [K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, Kw), knee, K.axis_angle(p3, F.HG([0.0, -1, 0]), Kw)]
    if lock:
        mem = hubs + [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end), neck,
                      K.strap_member("L2a", p2, Kw, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0)), over=[("link1", 1.0)], end_mm=end),
                      K.strap_member("L2b", Kw, p3, ("J2", "J3"), width=w, t=t, ramp_to=((None, 0), ("hub3", K.STACK)), over=[("link1", 1.0)], end_mm=end)]
        joints = dict(J1=p1, J2=p2, J3=p3); bodies = [("L2a", "L2b")]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN)); Fw = None
    else:
        rp, tp, tl = float(p["rpin"]), float(p["pin_t"]), float(p["t_lev"])
        Fw = seat_F(p1, p2, sd["fF"], sd["phiF"]); lv = sd["lever"]; t_stud = t + 1.0 + tl + 1.0
        dF, gF = polar_K(Kw, p3, Fw); q += [dF, gF]
        N = [Kw] + [from_polar(Kw, p3, np.full(len(th), nd), np.full(len(th), ng)) for nd, ng in zip(lv["nodes_d"][1:], lv["nodes_g"][1:])]
        on1 = abs(sd["phiF"]) < 1e-6 and sd["fF"] < p["a1"] - 8
        pins = [K.hub_member("pinK", Kw, "K", t=tp, rad=rp, step=1.25), K.hub_member("studF", Fw, "F", t=t_stud, rad=3.5, step=1.0)]
        l1 = [K.strap_member("link1", p1, p2, ("J1", "J2") + (("F",) if on1 else ()), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end)]
        if not on1:
            l1.append(K.strap_member("link1f", p2, Fw, ("J2", "F"), width=8.0, t=t, ramp_to=(("hub2", 0.0), ("studF", 0.0)), end_mm=end))
        under1 = [(m.name, 1.0) for m in l1]
        crank = K.strap_member("crank", p2, Kw, ("J2", "K"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("pinK", 0.0)), over=list(under1), end_mm=end)
        nk = [("neck", 1.0)] if int(p.get("ov", 1)) >= 2 else []
        l2b = K.strap_member("L2b", Kw, p3, ("K", "J3"), width=w, t=t, ramp_to=(("pinK", K.STACK), ("hub3", K.STACK)),
                             over=under1 + [("crank", 1.0)] + nk, end_mm=end)
        lev = []
        for i in range(3):
            rmp = (("pinK", K.STACK) if i == 0 else (None, 0), ("studF", t + 1.0) if i == 2 else (None, 0))
            lev.append(K.strap_member(f"lev{i + 1}", N[i], N[i + 1], ("K", "F"), width=lv["width"], t=tl, ramp_to=rmp,
                                      over=under1 + [("crank", 1.0), ("hub2", 1.0)], end_mm=min(end, 6.0)))
        mem = hubs + pins + l1 + [neck, crank, l2b] + lev
        joints = dict(J1=p1, J2=p2, J3=p3, K=Kw, F=Fw)
        b2 = ["L2b", "lev1", "lev2", "lev3"]
        bodies = ([("link1", "link1f")] if not on1 else []) + [(b2[i], b2[j]) for i in range(4) for j in range(i + 1, 4)]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN), pinK=(rp, tp), studF=(3.5, t_stud))
    okw = ok if ok.any() else np.ones(len(ok), bool)
    res = np.maximum(np.abs(ang(p2, p1) - p["a1"]), np.abs(ang(p2, p3) - G["a2e"]))
    res = np.maximum(res, np.maximum(np.abs(ang(Kw, p2) - p["b"]), np.abs(ang(Kw, p3) - p["c"])))
    info = dict(residual_deg=round(float(res[okw].max()), 5), window=[round(sd["lo"], 2), round(sd["hi"], 2)],
                a2eff_range=[round(float(G["a2e"][okw].min()), 1), round(float(G["a2e"][okw].max()), 1)],
                knee_range=[round(float(knee[okw].min()), 1), round(float(knee[okw].max()), 1)],
                psi_min=round(float(np.minimum(G["psi"], 180 - G["psi"])[okw].min()), 1),
                slot_gate=sd.get("gate"), slot_passed=bool(sd.get("passed", lock)), fF=sd.get("fF"), phiF=sd.get("phiF"),
                bodies=bodies, flat=flat)
    return K.Chain(members=mem, ok=ok, q=np.stack(q, -1), joints=joints, info=info)


def _jsonable(v):
    try:
        json.dumps(v); return True
    except (TypeError, ValueError):
        return False


def _clean(p):
    p = dict(PARAMS, **p); p["q"] = min(1.0, max(0.8, float(p["q"])))
    for k in ("sigma", "sk", "lock", "ov"): p[k] = int(round(float(p[k]))) if k in ("lock", "ov") else (1 if float(p[k]) >= 0 else -1)
    p["Amax"] = max(float(p["Amax"]), float(p["Amin"]) + 0.5); p["w"] = max(0.3, float(p["w"]))
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    return p


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = _clean(params); sd = slot_design(p)
    if not sd["ok"] or sd["hi"] - sd["lo"] < 5:
        return p, dict(gap=400.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, honest=False,
                       audit=["no valid th run"], closure=0.0, slot_passed=False)
    r = K.evaluate(B, build, p); r = DW.declared_audit(r, B._kit_last["chain"], B._kit_last["pts"]); r = DW.extras(B, r, p)
    ch = B._kit_last["chain"]
    for k in ("slot_gate", "slot_passed", "fF", "phiF", "window", "a2eff_range", "knee_range", "psi_min", "residual_deg"):
        r[k] = ch.info.get(k)
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    if not r["slot_passed"]:
        r["gap_unpenalised"] = r["gap"]; r["gap"] = round(r["gap"] + 100.0, 2); r["honest"] = False
        r["audit"] = (r.get("audit") or []) + ["slot gate failed"]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if _jsonable(v)}


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every underside / hub level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if _jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": DW.adjust_stacks(chain, {k: v.copy() for k, v in prof.items()})
    try:
        r = K.evaluate(Bb, build, pf); r = DW.declared_audit(r, Bb._kit_last["chain"], Bb._kit_last["pts"]); r = DW.extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    if not Bb._kit_last["chain"].info.get("slot_passed"): r["honest"] = False; r["audit"] = (r.get("audit") or []) + ["slot gate failed"]
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                     "min_metal_skin", "overhead", "inband_member", "th_need")}, flush=True)
    if "--redteam" in sys.argv: DW.redteam(Bb, pf, r)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "gate":
        sd = slot_design(_clean(par)); print({k: v for k, v in sd.items()}); sys.exit()
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r.get("inband_member"), "mass", r.get("mass_g"), "res", r.get("residual_deg"), "declared", r.get("declared_hubs"))
    print({k: r.get(k) for k in ("window", "a2eff_range", "knee_range", "psi_min", "fF", "phiF", "slot_gate", "post_lift", "gap_near1",
                                 "min_metal_skin", "overhead", "th_need", "stack_mismatch")})
    if mode == "redteam": DW.redteam(B, p, r)
