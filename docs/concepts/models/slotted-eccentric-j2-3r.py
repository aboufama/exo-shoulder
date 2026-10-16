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
TH_NEED = (26.0, 141.0)        # deg: the J1-J3 angle the workspace needs at 5-95 % (docs/research/reach_attribution.md)
R_NOM = 62.0                    # mm: nominal radius of hub 2 / knee / lever (mm <-> deg for the slot gate only)
PARAMS = dict(az=97.7506, el=65.294, a1=38.0901, wd=90.0506, wa=-9.2038, sigma=-1, margin=5.0, width=12.0, t_link=3.0,
              q=0.97, rad1=10.0, rad2=10.0, rad3=10.0, end_extra=0.0,
              Amin=60.0, Amax=90.0, w=3.0, sl=1.0, b=25.0, c=72.0, sk=1, psi_lo=15.0,
              dG=None, gG=None, seg_mm=12.0, rpin=5.0, pin_t=6.5, t_lev=2.0, lock_min=50.0, g_min=0.2,
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
    if p.get("lock"):                                         # control: link 2 straight (K on the J2 -> J3 arc at b), the plain 3R
        Kw = math.cos(p["b"] * D2R) * p2 + math.sin(p["b"] * D2R) * tangent(p2, p3); psi = np.full(th.shape, 90.0)
        ok = ok2 & (mg >= p["margin"])
        return dict(th=th, a2e=a2e, p2=p2, K=Kw, psi=psi, ok=ok, mg=mg)
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
GKEYS = ("a1", "sigma", "margin", "Amin", "Amax", "w", "sl", "b", "c", "sk", "psi_lo", "dG", "gG", "rad2", "rpin", "lock",
         "lock_min", "g_min", "a2", "seg_mm")


def _turn(ax, v, deg):
    c, si = math.cos(deg * D2R), math.sin(deg * D2R)
    return v * c + np.cross(ax, v) * si + ax * (ax * v).sum(-1, keepdims=True) * (1 - c)


def _lock(e, eta, ea, etaa, eb, etab, ths, dn):
    """lock angle (deg) between the internal four-bar mode velocity of the roller and the slot tangent, and the normal
    component of that velocity (deg / deg); polar coords (radius e, azimuth eta) of the roller in the slot body's frame"""
    se = np.sin(e * D2R)
    vi = np.stack([(ea - eb) / (2 * dn), se * (((etaa - etab + 180) % 360) - 180) / (2 * dn)], -1)
    tl = np.stack([np.gradient(e, ths), se * np.gradient(np.unwrap(eta * D2R) / D2R, ths)], -1)
    tln = tl / np.maximum(np.linalg.norm(tl, axis=-1, keepdims=True), 1e-9)
    cr = np.abs(vi[:, 0] * tln[:, 1] - vi[:, 1] * tln[:, 0]); nv = np.linalg.norm(vi, axis=-1)
    return np.degrees(np.arcsin(np.clip(cr / np.maximum(nv, 1e-9), 0, 1))), cr


def _synthetic(p):
    th = np.arange(1.0, 179.0, 0.25); z = np.array([0.0, 0, 1])
    p1 = np.broadcast_to(z, (len(th), 3)); p3 = np.stack([np.sin(th * D2R), 0 * th, np.cos(th * D2R)], -1)
    return th, p1, p3, geom(p1, p3, p)


def _run(ok):
    runs, cur = [], []
    for i in range(len(ok)):
        if ok[i]: cur.append(i)
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    return np.array(max(runs, key=len)) if runs else None


def gate_spec_orientation(p, dn=0.2):
    """the SPEC's orientation (roller F fixed on link 1, slot in a lever on link 2b): the best worst-case lock angle over
    a grid of roller seats (fF 10-40, phiF -180..180). Singular whenever F, K and J2 share a great circle, i.e. whenever
    the crank sweeps through the seat's azimuth seen from J2 - unavoidable once q2 spans >= ~180 deg"""
    th, p1, p3, G = _synthetic(p); run = _run(G["ok"])
    if run is None: return dict(best_lock=None)
    s = run[::2]; P1, P3, P2, KK, ths = p1[s], p3[s], G["p2"][s], G["K"][s], th[s]
    p2a = _turn(P1, P2, dn); p2b = _turn(P1, P2, -dn); n = len(ths); bc = (np.full(n, float(p["b"])), np.full(n, float(p["c"])))
    ka = closure_v(p2a, P3, *bc, p["sk"])[0]; kb = closure_v(p2b, P3, *bc, p["sk"])[0]; best = (-1, None)
    for fF in np.arange(10.0, 41.0, 2.0):
        for ph in np.arange(-180.0, 180.0, 7.5):
            d, g = polar_K(KK, P3, seat_F(P1, P2, fF, ph)); da, ga = polar_K(ka, P3, seat_F(P1, p2a, fF, ph))
            db, gb = polar_K(kb, P3, seat_F(P1, p2b, fF, ph)); lk, _ = _lock(d, g, da, ga, db, gb, ths, dn)
            if lk.min() > best[0]: best = (float(lk.min()), (float(fF), float(ph)))
    q2 = K.axis_angle(P2, P1, KK)
    return dict(best_lock=round(best[0], 2), seat=best[1], q2_span=round(float(np.ptp(np.unwrap(q2 * D2R) / D2R)), 1), n_seats=16 * 48)


def slot_design(p):
    """INVERTED slot (the spec's orientation is singular, see gate_spec_orientation): the roller G is fixed in link 2b
    (polar dG, gG about K from the K -> J3 arc), the slot is a track fixed to link 1 around hub 2 (the curve G traces in
    link 1's polar frame about J2: radius e, azimuth eta from the J2 -> J1 arc). Gate + roller seat (grid-solved unless
    dG / gG given) + the track polyline (link 1's frame)."""
    key = tuple((k, None if p.get(k) is None else round(float(p[k]), 6)) for k in GKEYS)
    if key in _CACHE: return _CACHE[key]
    th, p1, p3, G = _synthetic(p); run = _run(G["ok"])
    out = dict(ok=False, lo=0.0, hi=-1.0, passed=False, gate=dict(why="no valid th run"))
    if run is None: _CACHE[key] = out; return out
    lo, hi = float(th[run[0]]), float(th[run[-1]]); out.update(lo=lo, hi=hi, ok=True)
    if p.get("lock"):
        out.update(passed=True, gate=dict(lock=True)); _CACHE[key] = out; return out
    s = run; P1, P3, P2, KK, ths = p1[s], p3[s], G["p2"][s], G["K"][s], th[s]; n = len(ths)
    q2 = np.unwrap(K.axis_angle(P2, P1, KK) * D2R) / D2R; dq2 = np.diff(q2)
    q2mono = bool(np.all(dq2 > 1e-3) or np.all(dq2 < -1e-3))
    dn = 0.05; p2a = _turn(P1, P2, dn); p2b = _turn(P1, P2, -dn); bc = (np.full(n, float(p["b"])), np.full(n, float(p["c"])))
    ka = closure_v(p2a, P3, *bc, p["sk"])[0]; kb = closure_v(p2b, P3, *bc, p["sk"])[0]
    rmm = lambda mm: mm / R_NOM / D2R
    e_min = rmm(p["rad2"] + 1.0 + 3.25); dG_min = rmm(p["rpin"] + 3.5 + 1.0)
    if p.get("dG") is not None: cands = [(float(p["dG"]), float(p["gG"]))]
    else: cands = [(dg, gg) for dg in np.arange(math.ceil(dG_min), 34.0, 2.0) for gg in np.arange(-180.0, 180.0, 7.5)]
    stats = dict(n=len(cands), e_min=0, lock=0, self=0); best = None
    pol = lambda P2_, P1_, X: (ang(P2_, X), K.axis_angle(P2_, P1_, X))
    need = (ths >= TH_NEED[0]) & (ths <= TH_NEED[1])
    for dG, gG in cands:
        Gw = from_polar(KK, P3, np.full(n, dG), np.full(n, gG)); e, eta = pol(P2, P1, Gw)
        ea, etaa = pol(p2a, P1, from_polar(ka, P3, np.full(n, dG), np.full(n, gG)))
        eb, etab = pol(p2b, P1, from_polar(kb, P3, np.full(n, dG), np.full(n, gG)))
        lk, cr = _lock(e, eta, ea, etaa, eb, etab, ths, dn)
        al = ang(tangent(KK, P2), tangent(KK, Gw)); al = np.minimum(al, 180 - al)     # G-K-J2 alignment = singular
        good = (lk >= p["lock_min"]) & (cr >= p["g_min"]) & (al >= 10.0) & (e >= e_min)
        sub = _run(good)                                       # the track ends where the lock is lost: a hard stop
        if sub is None or len(sub) < 20: continue
        stats["lock"] += 1
        cov = float((need[sub]).sum()) / max(1, need.sum())
        e2, et2 = e[sub], np.unwrap(eta[sub] * D2R) / D2R; S = _xy(e2, et2)        # slot centreline (mm, planar about J2)
        L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=-1))])
        far = np.abs(L[:, None] - L[None, :]) > 3 * 6.5
        dd = np.linalg.norm(S[:, None] - S[None, :], axis=-1)
        if (dd[far] < 6.5 + 1.0).any(): continue                          # the track would overlap itself
        stats["self"] += 1
        nseg = int(min(10, max(2, math.ceil(L[-1] / float(p.get("seg_mm", 12.0))))))
        ext = 2.5 + 1.95
        Ln = np.linspace(-ext, L[-1] + ext, nseg + 1)
        ne = np.interp(np.clip(Ln, 0, L[-1]), L, e2); nh = np.interp(np.clip(Ln, 0, L[-1]), L, et2)
        XY = _xy(ne, nh); dev = np.min(np.stack([_seg_dist(S, XY[i], XY[i + 1]) for i in range(nseg)], 0), 0).max()
        width = max(6.5, 6.5 + 2 * dev)
        score = cov - 0.01 * max(0.0, width - 7.5) - 0.0005 * L[-1]
        if best is None or score > best[0]:
            ispoke = int(np.argmin(np.abs(((nh + 180) % 360) - 180)))
            best = (score, dG, gG, dict(nodes_e=ne.tolist(), nodes_eta=nh.tolist(), width=round(width, 2), dev_mm=round(float(dev), 2),
                                        lock_min=round(float(lk[sub].min()), 1), g_min=round(float(cr[sub].min()), 3),
                                        lock_full_run=round(float(lk.min()), 1), e=[round(float(e2.min()), 1), round(float(e2.max()), 1)],
                                        slot_len_mm=round(float(L[-1]), 1), eta_span=round(float(np.ptp(et2)), 1), spoke_node=ispoke,
                                        th_track=[float(ths[sub[0]]), float(ths[sub[-1]])], need_cover=round(cov, 3)))
    if best is not None:
        lo, hi = best[3]["th_track"]; out.update(lo=lo, hi=hi)
    gate = dict(q2_monotone=q2mono, q2_span=round(float(np.ptp(q2)), 1), stats=stats)
    if best is not None and q2mono:
        gate.update(best[3]); out.update(passed=True, dG=best[1], gG=best[2], track=best[3], gate=gate)
    else:
        gate["why"] = "q2 not monotone" if not q2mono else "no roller seat passes (e_min / lock / self-overlap)"
        out.update(gate=gate, dG=float(p.get("dG") or 15.0), gG=float(p.get("gG") or 90.0),
                   track=dict(nodes_e=[20.0, 25.0, 30.0], nodes_eta=[-40.0, 0.0, 40.0], width=6.5, spoke_node=1))
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
    q = [K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, Kw), K.axis_angle(p3, F.HG([0.0, -1, 0]), Kw)] + ([] if lock else [knee])
    if lock:
        mem = hubs + [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end), neck,
                      K.strap_member("L2a", p2, Kw, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0)), over=[("link1", 1.0)], end_mm=end),
                      K.strap_member("L2b", Kw, p3, ("J2", "J3"), width=w, t=t, ramp_to=((None, 0), ("hub3", K.STACK)), over=[("link1", 1.0)], end_mm=end)]
        joints = dict(J1=p1, J2=p2, J3=p3); bodies = [("L2a", "L2b")]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN))
    else:
        rp, tp, tt = float(p["rpin"]), float(p["pin_t"]), float(p["t_lev"])
        n = len(th); Gw = from_polar(Kw, p3, np.full(n, sd["dG"]), np.full(n, sd["gG"]))
        eG, etaG = ang(p2, Gw), K.axis_angle(p2, p1, Gw); q += [eG, etaG]
        tr = sd["track"]; e1 = tangent(p2, p1); n1 = np.cross(p2, e1)
        def L1(e, eta):                                        # a point fixed in link 1's polar frame about J2
            e, eta = e * D2R, eta * D2R
            return math.cos(e) * p2 + math.sin(e) * (math.cos(eta) * e1 + math.sin(eta) * n1)
        N = [L1(a, b) for a, b in zip(tr["nodes_e"], tr["nodes_eta"])]
        t_stud = tt + 1.0 + t
        pins = [K.hub_member("pinK", Kw, "K", t=tp, rad=rp, step=1.25), K.hub_member("studG", Gw, "G", t=t_stud, rad=3.5, step=0.5)]
        l1 = [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end),
              K.strap_member("spoke", p2, N[tr["spoke_node"]], ("J2",), width=8.0, t=t, ramp_to=(("hub2", 0.0), (None, 0)), end_mm=end)]
        trk = [K.strap_member(f"trk{i + 1}", N[i], N[i + 1], ("J2", "G"), width=tr["width"], t=tt, end_mm=6.0) for i in range(len(N) - 1)]
        under1 = [(m.name, 1.0) for m in l1 + trk]
        crank = K.strap_member("crank", p2, Kw, ("J2", "K"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("pinK", 0.0)), over=list(under1), end_mm=end)
        nk = [("neck", 1.0)] if int(p.get("ov", 1)) >= 2 else []
        l2b = K.strap_member("L2b", Kw, p3, ("K", "J3"), width=w, t=t, ramp_to=(("pinK", K.STACK), ("hub3", K.STACK)),
                             over=under1 + [("crank", 1.0)] + nk, end_mm=end)
        arm = K.strap_member("armG", Kw, Gw, ("K", "G"), width=8.0, t=t, ramp_to=(("pinK", K.STACK), ("studG", tt + 1.0)),
                             over=under1 + [("crank", 1.0)], end_mm=min(end, 6.0))
        mem = hubs + pins + l1 + trk + [neck, crank, l2b, arm]
        joints = dict(J1=p1, J2=p2, J3=p3, K=Kw, G=Gw)
        b1 = ["link1", "spoke"] + [m.name for m in trk]
        b2 = ["L2b", "armG", "studG"]                     # the stud is pressed into link 2b's arm: one body
        bodies = [(b1[i], b1[j]) for i in range(len(b1)) for j in range(i + 1, len(b1))] + [(b2[i], b2[j]) for i in range(3) for j in range(i + 1, 3)]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN), pinK=(rp, tp), studG=(3.5, t_stud))
    okw = ok if ok.any() else np.ones(len(ok), bool)
    res = np.maximum(np.abs(ang(p2, p1) - p["a1"]), np.abs(ang(p2, p3) - G["a2e"]))
    if not lock: res = np.maximum(res, np.maximum(np.abs(ang(Kw, p2) - p["b"]), np.abs(ang(Kw, p3) - p["c"])))
    info = dict(residual_deg=round(float(res[okw].max()), 5), window=[round(sd["lo"], 2), round(sd["hi"], 2)],
                a2eff_range=[round(float(G["a2e"][okw].min()), 1), round(float(G["a2e"][okw].max()), 1)],
                knee_range=[round(float(knee[okw].min()), 1), round(float(knee[okw].max()), 1)],
                psi_min=round(float(np.minimum(G["psi"], 180 - G["psi"])[okw].min()), 1),
                slot_gate=sd.get("gate"), slot_passed=bool(sd.get("passed")), dG=sd.get("dG"), gG=sd.get("gG"),
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
    for k in ("slot_gate", "slot_passed", "dG", "gG", "window", "a2eff_range", "knee_range", "psi_min", "residual_deg"):
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
        sd = slot_design(_clean(par)); print({k: v for k, v in sd.items()}); print("spec orientation:", gate_spec_orientation(_clean(par))); sys.exit()
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r.get("inband_member"), "mass", r.get("mass_g"), "res", r.get("residual_deg"), "declared", r.get("declared_hubs"))
    print({k: r.get(k) for k in ("window", "a2eff_range", "knee_range", "psi_min", "dG", "gG", "slot_gate", "post_lift", "gap_near1",
                                 "min_metal_skin", "overhead", "th_need", "stack_mismatch")})
    if mode == "redteam": DW.redteam(B, p, r)
