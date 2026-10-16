"""dwell-fourbar-knee-3r: the zero-passive spherical 3R (spine-parked-j2-3r seats, slim O15 J2 / J3 hubs) with link 2
split at a passive knee K and closed by a rocker C from link 1 - a spherical Watt six-bar, every axis through GH, pins
only (catalogue id dwell-fourbar-knee-3r).

Chain: scapula handler -> base -> J1 (O20 hub, MR117-2RS pair, active) -> link 1 (12 x 3 Ti, + a plate J2 -> pin P)
-> J2 (active, slim O15 hub) -> L2a (12 x 3 Ti, arc b) -> knee K (passive pin) -> L2b (12 x 3 Ti strap K -> J3 + a tail
K -> Q) -> J3 (active, slim O15 hub) -> member 3 = hub 3's arm-end plate + the K7 14 x 6 neck rigid to BOTTOM's bar.
Loop: link 1 -> P (passive pin) -> rocker C (8 x 3 Ti strap, arc r) -> Q (passive pin) -> L2b.
P, K, Q: MR63ZZ pair (3 x 6 x 2.5) in an O10 Ti boss on two 3 mm plates, 6.5 mm stack (declared component, PIN below).
Spherical Gruebler: 6 bodies (base, link 1, L2a, L2b, C, arm), 6 revolutes, M = 3 (6 - 1) - 2 * 6 = 3: the knee angle
is a fixed function of q2 (no spring, no sensed passive, MVP2 keeps 3 motors). Passive translations 0.

Kinematics. In link 1's frame (u2 = z, u1 at arc a1 / azimuth 0) the J3 axis traces a coupler curve u3(s) as the crank
s (= q2) turns: K = Rz(s) K0, Q = the two-circle closure of (P, r) and (K, k) on the branch that holds the rest
configuration at s = sref (knee straight there: u3(sref) = Rz(sref) J30, the plain chain's), u3 = J3's fixed coordinates
in L2b's (K, K -> Q) frame. th(s) = angle(u1, u3(s)) on ONE monotone, valid arc of the curve (valid: Q closes, the
transmission angle at Q in [tq_lo, 180 - tq_lo], at K in [tk_lo, 180 - tk_lo]) is the J1-J3 axis angle the chain can
make; the window is that arc's [th_min + margin, th_max - margin]. Per pose: th = angle(p1, p3) -> s (secant-refined to
< 1e-3 deg) -> the rotation taking (u1, u3(s)) to (p1, p3) gives q1 and every axis in the world; q3 about p3.
lock=1 is the LOCKED CONTROL (the rocker removed, the knee rigid at its rest angle): the plain spherical 3R with link 2
routed through K, the same members otherwise, through the same checks.

Checks: the kit's (K3 march, K2 dense along the 10 fps motion incl. every joint axis P / K / Q, K6 at 1 mm lateral /
0.5 mm radial with only parts of the SAME rigid body exempt from each other: link 1 + its P plate, L2b's two straps),
crowns and walls of every hub and pin skin-checked, near-touch (metal < 1 mm), overhead >= 140 split, declared slim hubs
and pins (cover >= 75 % of their declared disc).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/dwell-fourbar-knee-3r.py [check|redteam|curve] ['<json>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/dwell-fourbar-knee-3r.py frozen '<json params>' --out R.json
"""
import functools, json, math, os, re, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "dwell-fourbar-knee-3r"
NAME = "Dwell four-bar knee 3R: a spherical Watt six-bar (rocker loop from link 1 to a split link 2), pins only"
D2R = math.pi / 180
# seats = spine-parked-j2-3r CMA-B (its frozen-exact best, verified family), loop = the ideation seed k21
PARAMS = dict(az=102.7793, el=65.3479, a1=40.6794, a2=73.7554, wd=84.4912, wa=-12.7631, margin=10.0, width=12.0,
              t_link=3.0, q=0.979, rad1=10.0, rad2=7.5, rad3=7.5, end_extra=0.24,
              b=40.12, chi=-0.49, gP=17.8, phP=14.48, k=15.0, alq=-152.75, sref=188.04,
              rpin=5.0, pin_t=6.5, w_rock=8.0, tq_lo=30.0, tk_lo=20.0, lock=0, near=0, ov=1)
REPORT_KEYS = ("post_lift", "window", "piece", "rocker_arc", "knee_range", "a2eff_range", "tq_min", "tk_min", "stack_mismatch",
               "gap_near1", "min_metal_skin", "crown_contact_poses", "overhead", "near1", "th_need")
SLIM = {10.0: "v5 O20 hub: MR117-2RS pair, 12.25 mm stack (docs/HARDWARE.md)",
        8.5: "O17 hub: MR117-2RS pair in a 2.75 mm Ti wall, 12.25 mm stack",
        7.5: "O15 slim hub: MR117-2RS pair (O11) in a 2.0 mm Ti wall, 12.25 mm stack (spine-parked-j2-3r hand calc)"}
PIN = {5.0: "passive pin: MR63ZZ pair (3 x 6 x 2.5) in an O10 Ti boss, two 3 mm plates, 6.5 mm stack (catalogue: passive pin)",
       6.0: "passive pin: MR74ZZ pair (4 x 7 x 2.5) in an O12 Ti boss, 6.5 mm stack"}
ELEV_OVER = 140.0
LOOPKEYS = ("a1", "a2", "b", "chi", "gP", "phP", "k", "alq", "sref", "margin", "tq_lo", "tk_lo", "lock")


# ---- spherical helpers (link 1's frame) -----------------------------------------------------------------------------
def sdir(arc, az):
    a, z = arc * D2R, az * D2R; return np.array([math.sin(a) * math.cos(z), math.sin(a) * math.sin(z), math.cos(a)])


def rotz(s):
    """(n, 3, 3) rotations about z by s (deg)"""
    c, si = np.cos(np.radians(s)), np.sin(np.radians(s)); o, z = np.ones_like(c), np.zeros_like(c)
    return np.stack([np.stack([c, -si, z], -1), np.stack([si, c, z], -1), np.stack([z, z, o], -1)], -2)


def tangent(a, b): return K.unit(b - (a * b).sum(-1, keepdims=True) * a)
def ang(a, b): return np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))


def knee_of(p2, p3, b, chi):
    """the point at arc b from p2, at azimuth chi (deg) off the p2 -> p3 great circle"""
    t = tangent(p2, p3); nn = np.cross(p2, t)
    return math.cos(b * D2R) * p2 + math.sin(b * D2R) * (math.cos(chi * D2R) * t + math.sin(chi * D2R) * nn)


def frame(a, b):
    """columns [a, unit(b - (a.b) a), a x that] (..., 3, 3)"""
    e = tangent(a, b); return np.stack([a, e, np.cross(a, e)], -1)


_CACHE = {}


def loop_consts(p):
    u2 = np.array([0.0, 0, 1]); u1 = sdir(p["a1"], 0.0); J30 = sdir(p["a2"], 0.0)
    K0 = knee_of(u2, J30, p["b"], p["chi"]); Q0 = knee_of(K0, J30, p["k"], p["alq"]); P = sdir(p["gP"], p["phP"])
    R0 = rotz(np.array([p["sref"]]))[0]; r = float(ang(P, R0 @ Q0))
    sgn = float(np.sign((R0 @ Q0) @ np.cross(P, R0 @ K0)) or 1.0)
    c3 = frame(K0, Q0).T @ J30                               # J3 in L2b's (K, K -> Q) frame
    return dict(u1=u1, u2=u2, J30=J30, K0=K0, Q0=Q0, P=P, r=r, sgn=sgn, c3=c3)


def loop_at(C, s, p):
    """the loop at crank angles s (n,) deg -> dict of (n, 3) axes in link 1's frame + validity"""
    s = np.atleast_1d(np.asarray(s, float)); Rs = rotz(s); Ks = Rs @ C["K0"]
    if p.get("lock"):
        u3 = Rs @ C["J30"]; Q = Rs @ C["Q0"]; okq = np.ones(len(s), bool); tq = np.full(len(s), 90.0); tk = tq.copy()
    else:
        PP = np.broadcast_to(C["P"], Ks.shape)
        Q, okq, _ = K.closure(PP, Ks, C["r"], p["k"], C["sgn"], margin_deg=0.0)
        u3 = frame(Ks, Q) @ C["c3"]
        tq = ang(tangent(Q, Ks), tangent(Q, PP)); tk = ang(tangent(Ks, np.broadcast_to(C["u2"], Ks.shape)), tangent(Ks, Q))
    th = ang(u3, C["u1"])
    ok = okq & (tq >= p["tq_lo"]) & (tq <= 180 - p["tq_lo"]) & (tk >= p["tk_lo"]) & (tk <= 180 - p["tk_lo"])
    return dict(s=s, K=Ks, Q=Q, u3=u3, th=th, ok=ok, tq=tq, tk=tk)


def curve(p):
    """the monotone valid arc of th(s) the chain runs on (cached per loop geometry): s grid, th, window [lo, hi]"""
    key = tuple(round(float(p[k]), 9) for k in LOOPKEYS)
    if key in _CACHE: return _CACHE[key]
    C = loop_consts(p); st = 0.25; s = np.arange(0.0, 360.0, st); L = loop_at(C, s, p); n = len(s)
    ok, th = L["ok"], L["th"]; best = None
    if p.get("lock"):
        pieces = [np.arange(int(180 / st), n)]
    else:
        start = int(np.argmax(~ok)) if not ok.all() else 0
        idx = (np.arange(n) + start) % n; runs, cur = [], []
        for j in idx:
            if ok[j]: cur.append(j)
            else:
                if len(cur) > 2: runs.append(cur)
                cur = []
        if len(cur) > 2: runs.append(cur)
        pieces = []
        for run in runs:
            d = np.sign(np.diff(th[run])); cut = [0] + [i + 1 for i in range(len(d) - 1) if d[i] != 0 and d[i + 1] != 0 and d[i] != d[i + 1]] + [len(run) - 1]
            for a, b in zip(cut[:-1], cut[1:]):
                if b - a >= 3: pieces.append(np.array(run[a:b + 1]))
    sref_i = int(round((p["sref"] % 360) / st)) % n
    for pc in pieces:                                         # the piece holding the rest posture, else the widest
        span = th[pc].max() - th[pc].min(); hold = sref_i in set(pc.tolist())
        if best is None or (hold, span) > (best[0], best[1]): best = (hold, span, pc)
    if best is None:
        out = dict(C=C, ok=False, lo=0.0, hi=-1.0)
    else:
        pc = best[2]; su = s[pc].copy()
        su = np.unwrap(su * D2R) / D2R                        # continuous crank values along the piece
        tp = th[pc]; o = np.argsort(tp); lo, hi = tp.min() + p["margin"], tp.max() - p["margin"]
        out = dict(C=C, ok=hi > lo, lo=float(lo), hi=float(hi), s_th=su[o], th_s=tp[o], s0=float(su.min()), s1=float(su.max()),
                   hold=bool(best[0]), dth=np.gradient(tp, su), su=su, tp=tp)
    if len(_CACHE) > 64: _CACHE.clear()
    _CACHE[key] = out; return out


def solve(p, th):
    """crank s per pose for the J1-J3 angle th (n,) on the chosen arc, secant-refined; -> s, loop dict, residual"""
    cv = curve(p); C = cv["C"]
    if not cv["ok"]:
        s = np.full(len(th), float(p["sref"])); return s, loop_at(C, s, p), np.full(len(th), 180.0), np.zeros(len(th), bool)
    s = np.interp(th, cv["th_s"], cv["s_th"])
    for _ in range(3):
        L = loop_at(C, s, p); g = np.interp(s, cv["su"], cv["dth"])
        g = np.where(np.abs(g) < 1e-6, 1e-6, g); s = np.clip(s - (L["th"] - th) / g, cv["s0"], cv["s1"])
    L = loop_at(C, s, p); res = np.abs(L["th"] - th)
    inwin = (th >= cv["lo"]) & (th <= cv["hi"]) & L["ok"]
    return s, L, res, inwin


# ---- the chain --------------------------------------------------------------------------------------------------------
def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"]))                        # J1 fixed in the scapula
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))                       # J3 fixed in the humerus (band frame)
    th = ang(p1, p3); cv = curve(p); C = cv["C"]
    s, L, res, ok = solve(p, th)
    R = frame(p1, p3) @ np.swapaxes(frame(np.broadcast_to(C["u1"], p1.shape), L["u3"]), -1, -2)
    W = lambda v: np.einsum("pij,pj->pi", R, np.broadcast_to(v, p1.shape))
    p2 = W(C["u2"]); Kw = W(L["K"]); Qw = W(L["Q"]); Pw = W(C["P"]); u3w = W(L["u3"])
    lock = bool(p.get("lock"))
    knee = K.axis_angle(Kw, p2, p3)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), s, knee, K.axis_angle(p3, F.HG([0.0, -1, 0]), Kw),
                  K.axis_angle(Pw, p2, Qw)], -1)
    r1, r2, r3, rp, tp_ = float(p["rad1"]), float(p["rad2"]), float(p["rad3"]), float(p["rpin"]), float(p["pin_t"])
    w, t = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0))
    hubs = [K.hub_member("hub1", p1, "J1", rad=r1), K.hub_member("hub2", p2, "J2", rad=r2), K.hub_member("hub3", p3, "J3", rad=r3)]
    neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
    if lock:                                                  # LOCKED CONTROL: link 2 rigid through K, no loop
        mem = hubs + [K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end),
                      neck,
                      K.strap_member("L2a", p2, Kw, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0)),
                                     over=[("link1", 1.0), ("neck", 1.0)], end_mm=end),
                      K.strap_member("L2bJ", Kw, p3, ("J2", "J3"), width=w, t=t, ramp_to=((None, 0), ("hub3", K.STACK)),
                                     over=[("link1", 1.0), ("neck", 1.0)], end_mm=end)]
        joints = dict(J1=p1, J2=p2, J3=p3); bodies = [("L2a", "L2bJ")]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN))
    else:
        pins = [K.hub_member("pinP", Pw, "P", t=tp_, rad=rp, step=1.25), K.hub_member("pinK", Kw, "K", t=tp_, rad=rp, step=1.25),
                K.hub_member("pinQ", Qw, "Q", t=tp_, rad=rp, step=1.25)]
        ov = int(p.get("ov", 2)); nk = [("neck", 1.0)] if ov >= 2 else []; o1 = ov >= 1
        mem = hubs + pins + [
            K.strap_member("link1", p1, p2, ("J1", "J2", "P"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end),
            K.strap_member("link1p", p2, Pw, ("J2", "P"), width=w, t=t, ramp_to=(("hub2", 0.0), ("pinP", 0.0)), end_mm=end),
            neck,
            K.strap_member("L2a", p2, Kw, ("J2", "K"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("pinK", 0.0)),
                           over=([("link1", 1.0), ("link1p", 1.0)] if o1 else []) + nk, end_mm=end),
            K.strap_member("rocker", Pw, Qw, ("P", "Q"), width=p["w_rock"], t=t, ramp_to=(("pinP", K.STACK), ("pinQ", 0.0)),
                           over=([("link1", 1.0), ("link1p", 1.0), ("L2a", 1.0), ("hub2", 1.0)] if o1 else []) + nk, end_mm=end),
            K.strap_member("L2bJ", Kw, p3, ("K", "J3", "Q"), width=w, t=t, ramp_to=(("pinK", K.STACK), ("hub3", K.STACK)),
                           over=([("link1", 1.0), ("link1p", 1.0), ("rocker", 1.0), ("L2a", 1.0)] if o1 else []) + nk, end_mm=end),
            K.strap_member("L2bQ", Kw, Qw, ("K", "Q", "J3"), width=w, t=t, ramp_to=(("pinK", K.STACK), ("pinQ", K.STACK)),
                           over=([("link1", 1.0), ("link1p", 1.0), ("rocker", 1.0), ("L2a", 1.0)] if o1 else []) + nk, end_mm=end)]
        joints = dict(J1=p1, J2=p2, J3=p3, P=Pw, K=Kw, Q=Qw); bodies = [("link1", "link1p"), ("L2bJ", "L2bQ")]
        flat = dict(hub1=(r1, K.CROWN), hub2=(r2, K.CROWN), hub3=(r3, K.CROWN), pinP=(rp, tp_), pinK=(rp, tp_), pinQ=(rp, tp_))
    res3 = ang(u3w, p3)
    oks = ok if ok.any() else None
    info = dict(residual_deg=round(float(np.max(np.maximum(res, res3)[ok])), 5) if oks is not None else None,
                window=[round(cv["lo"], 2), round(cv["hi"], 2)], piece=[round(cv.get("s0", 0), 2), round(cv.get("s1", 0), 2)],
                rocker_arc=round(C["r"], 2), knee_range=[round(float(knee[ok].min()), 1), round(float(knee[ok].max()), 1)] if oks is not None else None,
                a2eff_range=[round(float(ang(p2, p3)[ok].min()), 1), round(float(ang(p2, p3)[ok].max()), 1)] if oks is not None else None,
                tq_min=round(float(np.minimum(L["tq"], 180 - L["tq"])[ok].min()), 1) if oks is not None else None,
                tk_min=round(float(np.minimum(L["tk"], 180 - L["tk"])[ok].min()), 1) if oks is not None else None,
                bodies=bodies, flat=flat, hold_rest=cv.get("hold"))
    return K.Chain(members=mem, ok=ok, q=q, joints=joints, info=info)


# ---- K6 with same-body exemption --------------------------------------------------------------------------------------
_KIT_COLL = K.collisions


def collisions_sb(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    """the kit's K6 (same rule, same code path per pair) with one change: two members of the SAME rigid body (link 1 and
    its P plate; L2b's strap to J3 and its tail to Q) are one machined part and are not checked against each other"""
    same = {frozenset(x) for x in (chain.info.get("bodies") or [])}
    if not same: return _KIT_COLL(chain, pts, ok, clear=clear, overlap=overlap, chunk=chunk)
    hit = np.zeros(len(ok), bool); M = chain.members; Pi = np.nonzero(ok)[0]
    if not len(Pi): return hit
    nr = {m.name: np.linalg.norm(pts[m.name], axis=-1) for m in M}; dr = {m.name: pts[m.name] / nr[m.name][..., None] for m in M}
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            A, Bm = M[a], M[b]
            if frozenset((A.name, Bm.name)) in same: continue
            shared = set(A.joints) & set(Bm.joints); ra, rb = nr[A.name], nr[Bm.name]
            if ra[Pi].min() > rb[Pi].max() + Bm.t + overlap or rb[Pi].min() > ra[Pi].max() + A.t + overlap: continue
            for c0 in range(0, len(Pi), chunk):
                P = Pi[c0:c0 + chunk]; xa, xb = ra[P], rb[P]
                res = K._near(A, Bm, dr[A.name][P], dr[Bm.name][P], xa, xb, chain.joints, shared, P, clear)
                if res is None: continue
                k, nm = res; xa, xb = xa[k], xb[k]
                ov = (xa[:, :, None] < xb[:, None, :] + Bm.t + overlap) & (xb[:, None, :] < xa[:, :, None] + A.t + overlap)
                hit[P[k]] |= (nm & ov).any((1, 2))
    return hit


K.collisions = collisions_sb


# ---- honest joint stacks: a strap end lifted above its joint's stack makes that joint's post taller ----------------------
_KIT_FIT = K.fit_profiles


def adjust_stacks(chain, prof):
    """the kit only RAISES strap ends onto a joint (>= F, >= F + 3.15), so a strap lifted by `over` / its own skin fit can
    float above the hub / pin it turns on. Physically that joint's post (housing + shaft) then stands taller: its height
    t becomes t0 + the largest lift of any member ramped onto it (crown check, K6 and mass use it). Applied in the locked
    control too."""
    lv = {m.name: float(prof[m.name][0]) for m in chain.members if m.kind == "flat"}; lift = {}
    for m in chain.members:
        if m.kind == "flat" or not m.ramps: continue
        for mask, other, dz in m.ramps:
            if other in lv: lift[other] = max(lift.get(other, 0.0), float(prof[m.name][mask].max() - (lv[other] + dz)))
    flat = chain.info.get("flat", {})
    for m in chain.members:
        if m.name in flat:
            t0 = flat[m.name][1] if len(flat[m.name]) < 3 else flat[m.name][2]
            m.t = t0 + max(0.0, lift.get(m.name, 0.0)); flat[m.name] = (flat[m.name][0], m.t, t0)
    chain.info["post_lift"] = {k: round(v, 2) for k, v in lift.items() if v > 0.05}
    return prof


def fit_profiles_adj(B, chain, fit, q=1.0, mode="march"):
    """fit, make the posts honest, fit again (members passing `over` a post then clear its real height), make honest"""
    adjust_stacks(chain, _KIT_FIT(B, chain, fit, q, mode))
    return adjust_stacks(chain, _KIT_FIT(B, chain, fit, q, mode))


K.fit_profiles = fit_profiles_adj


# ---- audit, crowns, near-touch, overhead --------------------------------------------------------------------------------
def crown_points(m, rho, rad, t):
    """(P, k, 3) crown disc + wall samples of a flat hub / pin member fitted at level rho[0] (F), radius rad, height t"""
    F0 = float(rho[0]); k = m.K[:, None, :]
    crown = (F0 + t) * k + m.xy[None, :, :1] * m.A[:, None, :] + m.xy[None, :, 1:] * m.Bv[:, None, :]
    n = max(16, int(round(2 * math.pi * rad / 2.0))); a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    c, s = rad * np.cos(a), rad * np.sin(a); lv = sorted(set([x for x in (2.0, 4.0, 6.0, 8.0, 10.0) if x < t] + [t]))
    wall = [(F0 + h) * k + c[None, :, None] * m.A[:, None, :] + s[None, :, None] * m.Bv[:, None, :] for h in lv]
    return np.concatenate([crown] + wall, 1)


def _taken(B, j): return B.res[j] is not None and float(np.min(B.res[j])) >= 0.0


def declared_audit(r, ch, pts):
    """a hub / pin smaller than O20 is accepted only as a DECLARED component (SLIM / PIN): the joint's own flat member
    (the one centred on it) must cover >= 75 % of its declared disc within rad + 0.5 and reach >= rad - 0.5 (measured
    here on its samples); recompute `honest`"""
    keep, decl = [], {}; flat = ch.info["flat"]; take = np.nonzero(ch.ok)[0]; i0 = int(take[0]) if len(take) else 0
    for msg in r.get("audit") or []:
        m = re.match(r"(\w+): hub of (\w+) smaller than O20 \(covers ([\d.]+) of the disc, reaches ([\d.]+) mm\)", msg)
        own = [x for x in ch.members if m and x.kind == "flat" and m.group(2) in x.joints and x.name in flat]
        if own:
            x = own[0]; rad = flat[x.name][0]; X = np.asarray(pts[x.name][i0], float); k = K.unit(np.asarray(ch.joints[m.group(2)][i0], float))
            lat = np.linalg.norm(X - (X @ k)[:, None] * k, axis=1)
            cov = float((lat <= rad + 0.5).sum() * x.cell / (math.pi * rad ** 2)); reach = float(lat.max())
            comp = SLIM.get(rad) if x.name.startswith("hub") else PIN.get(rad)
            if comp and cov >= 0.75 and reach >= rad - 0.5:
                decl[m.group(2)] = dict(member=x.name, rad=rad, component=comp, cover=round(cov, 3), reach=round(reach, 2)); continue
        keep.append(msg)
    r["audit"] = keep; r["declared_hubs"] = decl
    c = r.get("checks") or {}
    r["honest"] = c.get("mode") == "march" and c.get("cont") in (True, "frames") and bool(c.get("collide")) and not keep
    return r


def stack_mismatch(ch, prof):
    """per joint: how far the strap ends sit above the stack their joint asks for (lower member at F, upper at F + 3.15)
    - the kit only raises strap ends (>=), so a strap lifted by `over` floats above its pin; reported, mm"""
    out = {}; lv = {m.name: float(prof[m.name][0]) for m in ch.members if m.kind == "flat"}
    for m in ch.members:
        if m.kind == "flat" or not m.ramps: continue
        for mask, other, dz in m.ramps:
            if other in lv: out[f"{m.name}@{other}"] = round(float(prof[m.name][mask].max() - (lv[other] + dz)), 2)
    return out


def extras(B, r, p):
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]; flat = ch.info["flat"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat"]
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [crown_points(m, prof[m.name], *flat[m.name][:2])[Pi] for m in hubs]
        Cc = np.concatenate(parts, 1)
        dc = K.dist_many(B, np.repeat(Pi, Cc.shape[1]), Cc.reshape(-1, 3)).reshape(len(Pi), Cc.shape[1])
        cmin[Pi] = dc.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): cwho[int(j)] = hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)].name
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report()
    allmin = sorted((min(float(np.min(B.res[j])), cmin[j]), j) for j in range(len(B.res)) if _taken(B, j))
    save = list(B.res)
    for d, j in allmin:
        if d < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    el = np.array([q["elev"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind]); cl = ~ws
    ov = np.nonzero(el >= ELEV_OVER)[0]; ovw = ov[ws[ov]]; ovc = ov[cl[ov]]
    tk = [j for j in ov if _taken(B, j)]; d = np.concatenate([B.res[j] for j in tk]) if tk else np.zeros(0)
    over = dict(n_ws=int(len(ovw)), reach=round(float(np.mean([_taken(B, j) for j in ovw])), 4) if len(ovw) else None,
                n_clip=int(len(ovc)), follow=round(float(np.mean([_taken(B, j) for j in ovc])), 4) if len(ovc) else None,
                n_taken=len(tk), inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None)
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): r[k] = rr[k]
    F = B._kitF; p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"])); th = ang(p1, p3)[ws]
    r.update(crown_contact_poses=int(len(bad)), crown_min=round(float(np.min(cmin[np.isfinite(cmin)])), 2) if np.isfinite(cmin).any() else None,
             min_metal_skin=round(float(allmin[0][0]), 2) if allmin else None,
             near_low=[dict(mm=round(float(dd), 2), i=int(j), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"],
                            axial=B.poses[j]["axial"], crown=cwho.get(int(j)) if cmin[j] <= float(np.min(B.res[j])) else "face")
                       for dd, j in allmin[:5]],
             gap_near1=rn["gap"], near1=dict(reach=rn["reach"], follow=rn["follow"], inband14=rn["inband14"], contact=rn["contact"]),
             overhead=over, stack_mismatch=stack_mismatch(ch, prof), post_lift=ch.info.get("post_lift"),
             th_need=dict(p5=round(float(np.percentile(th, 5)), 1), p95=round(float(np.percentile(th, 95)), 1),
                          kin_reach=round(float(((th >= ch.info["window"][0]) & (th <= ch.info["window"][1])).mean()), 4)))
    return r


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = dict(PARAMS, **params); p["q"] = min(1.0, max(0.8, float(p["q"])))
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    for k in ("rad2", "rad3"): p[k] = min(SLIM, key=lambda x: abs(x - float(p[k])))
    p["rpin"] = min(PIN, key=lambda x: abs(x - float(p["rpin"]))); p["lock"] = int(round(float(p.get("lock", 0))))
    p["k"] = max(13.0, float(p["k"]))                          # pin separation K-Q: two O10 bosses + 3 mm at r ~ 60
    cv = curve(p)
    if not cv["ok"]:
        return p, dict(gap=400.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, honest=False, audit=["no valid loop arc"],
                       window=[cv["lo"], cv["hi"]], closure=0.0)
    r = K.evaluate(B, build, p); r = declared_audit(r, B._kit_last["chain"], B._kit_last["pts"]); r = extras(B, r, p)
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if _jsonable(v)}


def _jsonable(v):
    try:
        json.dumps(v); return True
    except (TypeError, ValueError):
        return False


def lab(B, i): return f"#{i:3d} {B.kind[i]:4s} {B.clip[i][:20]:20s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"


def redteam(B, p, r):
    L = B._kit_last; ch, prof, pts, take, ok, hit = L["chain"], L["prof"], L["pts"], L["take"], L["ok"], L["hit"]
    Pi = np.nonzero(take)[0]; el = np.array([q["elev"] for q in B.poses]); pl = np.array([q["plane"] for q in B.poses])
    print("-- per part: in band (clip), level, median / p90 distance over taken poses --")
    for m in ch.members:
        X = pts[m.name][Pi]; d = K.dist_many(B, np.repeat(Pi, X.shape[1]), X.reshape(-1, 3)).reshape(len(Pi), -1)
        lvl = f"F {prof[m.name][0]:.1f}" if m.kind == "flat" else f"level med {np.median(prof[m.name]):.1f} max {prof[m.name].max():.1f}"
        print(f"  {m.name:7s} ib14 {r['inband_member'].get(m.name)} {lvl}; dist median {np.median(d):.1f} p90 {np.percentile(d, 90):.1f}")
    fit = np.nonzero(ok)[0]
    for m in [m for m in ch.members if m.kind == "flat"]:
        n = len(m.xy); Dm = np.broadcast_to(m.K[fit][:, None, :], (len(fit), n, 3))
        Om = m.xy[None, :, :1] * m.A[fit][:, None, :] + m.xy[None, :, 1:] * m.Bv[fit][:, None, :]
        R = K.requirement(B, np.repeat(fit, n), Dm.reshape(-1, 3), O=Om.reshape(-1, 3)).reshape(len(fit), n)
        R = np.where(np.isfinite(R), R, 400.0).max(1); o = np.argsort(-R)[:4]
        print(f"  {m.name} level set by (requirement mm): " + "; ".join(f"{R[a]:.1f} {lab(B, int(fit[a]))}" for a in o))
    print("-- poses not taken --")
    nt = [i for i in range(len(B.res)) if not _taken(B, i)]
    why = lambda i: "fold/K2" if not ok[i] else ("K6 parts" if hit[i] else "contact")
    for i in nt[:40]: print(f"  {why(i):8s} {lab(B, i)}  min {float(np.min(B.res[i])) if B.res[i] is not None else float('nan'):.1f}")
    print(f"  ... {len(nt)} not taken: fold/K2 {sum(not ok[i] for i in nt)}, K6 {sum(bool(ok[i] and hit[i]) for i in nt)}, contact {sum(bool(ok[i] and not hit[i]) for i in nt)}")
    if hit.any():                                             # which pairs collide
        M = ch.members; cnt = {}
        for i in np.nonzero(hit)[0][:40]:
            m1 = np.zeros(len(ok), bool); m1[i] = True
            for a in range(len(M)):
                for b in range(a + 1, len(M)):
                    sub = K.Chain(members=[M[a], M[b]], ok=m1, joints=ch.joints, info=ch.info)
                    if collisions_sb(sub, {M[a].name: pts[M[a].name], M[b].name: pts[M[b].name]}, m1)[i]:
                        cnt[(M[a].name, M[b].name)] = cnt.get((M[a].name, M[b].name), 0) + 1
        print("  K6 pairs (first 40 hit poses):", cnt)
    ws = np.array([k == "ws" for k in B.kind]); nws = [i for i in nt if ws[i]]
    print(f"  reach loss over {int(ws.sum())} ws poses: fold {sum(not ok[i] for i in nws)}, K6 {sum(bool(ok[i] and hit[i]) for i in nws)}, contact {sum(bool(ok[i] and not hit[i]) for i in nws)}")
    groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= ELEV_OVER)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                  behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
    print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 --")
    for g, ii in groups.items():
        ii = list(ii); tk = [i for i in ii if _taken(B, i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
        print(f"  {g:9s} {len(tk)}/{len(ii)}  median {float(np.nanmedian(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}"
              f"  not taken: {[(int(i), why(i)) for i in ii if not _taken(B, i)][:8]}")


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
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": adjust_stacks(chain, {k: v.copy() for k, v in prof.items()})
    try:
        r = K.evaluate(Bb, build, pf); r = declared_audit(r, Bb._kit_last["chain"], Bb._kit_last["pts"]); r = extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                     "min_metal_skin", "overhead", "inband_member", "th_need")}, flush=True)
    if "--redteam" in sys.argv: redteam(Bb, pf, r)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "curve":
        p = dict(PARAMS, **par); cv = curve(p)
        print({k: cv.get(k) for k in ("ok", "lo", "hi", "s0", "s1", "hold")}, "r", round(cv["C"]["r"], 2)); sys.exit()
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r.get("inband_member"), "mass", r.get("mass_g"), "res", r.get("residual_deg"), "declared", r.get("declared_hubs"))
    print({k: r.get(k) for k in REPORT_KEYS})
    print("near", r.get("near_low"))
    if mode == "redteam": redteam(B, p, r)
