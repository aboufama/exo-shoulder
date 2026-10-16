"""geneva-tail-knuckle-3r: the one-tooth Geneva drive on the PLAIN spherical chain with a spring knuckle in link 1 (minarc
variant A metal, no pin knee), with the J3-side options (inv3, end_extra, crest-basin seats) in the search.

Chain: scapula handler -> J1 (ACTIVE, O20) -> link 1a -> K (PASSIVE R, clock spring onto stop A; cap carries one tooth
flank) -> link 1b -> J2 (ACTIVE, O20; q2 dowel stops at both ends of the law) -> link 2 + rear TAIL (rigid with link 2,
an MR63ZZ roller at its tip) -> J3 (ACTIVE, O20, humerus-fixed axis) -> neck (K7) -> BOTTOM.
3 active, 1 passive rotation (K, slaved: never read), 0 passive translations, 1 closed loop (tail roller on K's tooth).

Built on docs/concepts/models/minarc-stop-knuckle-4r-a-kitrule.py (the kit's J1-J3 fold rule, near-touch objective,
hub K cap, continuity flood fill, frozen wear), loaded as its own module copy; only the law and the metal change.

THE LAW (exact, spherical; the same construction as geneva-tail-knuckle-pinknee-3r, written for the variant-A chain):
in link 1b's frame (it carries the J2 axis u2 and K's axis uK, arc b2 apart) link 1a carries u1 and turns about uK by
kappa (0 on stop A, opening sense = the one that raises a1e = angle(u1, u2)); link 2 carries u3 and the tail tip and turns
about u2 by q (0 at the onset th_hi = min(a1 + a2, 360 - a1 - a2) - smhi with K on stop A; sense s_q = the stretching
one). The roller centre p(q) = R(u2, q) p0 (angular radius rho_n = rho / r_law) touches ONE radial flank, a half-plane
through uK fixed to link 1a, ahead of the roller in its azimuthal motion about uK:
    kappa(q) = az_c(q) - az_c(0),  az_c = az(p_perp) + s_m asin(rho_n / |p_perp|),  s_m = sign(d az / dq),
and the tip side (L_t = b2 - d or b2 + d along the great circle u2 -> uK, closest approach d mm at r_law when q = psi_c)
is the one whose flank OPENS K. th_law(q) = angle(R(uK, kappa) u1, R(u2, q) u3) is pose independent; a stretched pose is
solved by inverting th_law on its valid prefix (th_law rising with dq/dth <= RATE_MAX; pressure angle <= pa_max; contact
radius on the tooth <= HUB_R (crown: the roller runs over K's cap) or lug_max (beside: a lug on link 1a); a1e <= a1max
(stop B); the dyad margin m3e >= the kit's 5 deg and the forced sub-chain J1-K-J3 margin msub >= 5; no lift-off: at
fixed th, K must not be able to sit off the roller at a smaller opening). The end of the prefix is J2's stretched dowel.
The folded side has NO tooth: J2 stops on its folded dowel at th_lo = |a1 - a2| + smlo with K on stop A, and folded poses
beyond it are not taken (`fold_tooth` 0).

THE METAL (vs the parent): hub K = O20 stack + capK (clock-spring cap) + 1 mm + the tooth blade up to the roller top;
the TAIL strap (8 x 3 Ti, member 2, from hub 2 at link 2's level to the tip) passing over link 1a, link 1b and hub K
(+1 mm, the kit's `over`); the ROLLER (O8 boss, 3 mm: MR63ZZ + washer) as a skin-fitted strap stub under the tail tip,
its underside >= hub K's cap + 1 mm (crown embodiment). Every sample skin-checked, in band and K6-checked like a link.
Options: inv3 (link 2 on hub 3's lower plate, member 3 bridging over it on the cap plate), end_extra (strap end hold).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/geneva-tail-knuckle-3r.py check '<json>'
    CB_EXACT=1 python3 docs/concepts/models/geneva-tail-knuckle-3r.py frozen '<json>' [bench|held] [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py / cloud_run), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("kitrule_a_for_geneva3r", os.path.join(HERE, "minarc-stop-knuckle-4r-a-kitrule.py"))
KR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KR)
KA = KR.KA; SP = KR.SP; D2R = math.pi / 180
ID = "geneva-tail-knuckle-3r"
RATE_MAX = 3.45
ROLLER_H, BOSS_R = 3.0, 4.0                                   # MR63ZZ 2.5 wide + washer; O8 boss

# LA1 (the proposer's seats: the kit-rule A model at its best, camlaw.py)
LA1 = {"az": 100.6785, "el": 65.4034, "wd": 46.1583, "wa": -6.1871, "a1": 43.8793, "a2": 71.1868, "b1": 30.6983, "b2": 56.392,
       "a1max": 70.3202, "sigma": -1, "sK": -1, "width": 12.0, "t_link": 3.0, "q": 0.9694, "smhi": 6.0944, "smlo": 8.9158}
PARAMS = dict(KR.PARAMS, **LA1)
PARAMS.update(near=1, phys=0, capK=6.0, cam=1, d_mm=7.0, psi_c=0.0, side=0, rho=3.0, r_law=70.0, pa_max=45.0, lug_max=22.0,
              tail=1, tail_w=8.0, inv3=0, end_extra=0.0, fold_tooth=0, flipK=1)


def _rot(k, a):
    """rotation matrices about unit axis k (3,) by angles a (n,) rad -> (n, 3, 3)"""
    a = np.atleast_1d(np.asarray(a, float)); k = K.unit(np.asarray(k, float))
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    s, c = np.sin(a)[:, None, None], np.cos(a)[:, None, None]
    return np.eye(3)[None] + s * Kx[None] + (1 - c) * (Kx @ Kx)[None]


def _ang(u, v): return np.degrees(np.arccos(np.clip((K.unit(u) * K.unit(v)).sum(-1), -1, 1)))


def _frame(k):
    k = K.unit(k); r = np.array([1.0, 0, 0]) if abs(k[0]) < 0.9 else np.array([0, 1.0, 0])
    e = K.unit(r - (r @ k) * k); return e, np.cross(k, e)


_LAW_CACHE = {}


def geneva(p):
    """the exact one-tooth contact law of design p (canonical frame) -> dict(ok, th, a1e, ...); cached per design"""
    key = tuple(round(float(p[k]), 6) for k in ("a1", "a2", "b1", "b2", "a1max", "smhi", "smlo", "d_mm", "psi_c", "rho", "r_law", "pa_max", "lug_max",
                                                 "sigma", "sK", "side"))
    if key in _LAW_CACHE: return _LAW_CACHE[key]
    a1, a2, b1, b2 = (float(p[k]) for k in ("a1", "a2", "b1", "b2")); m = K.FOLD_MARGIN
    sg = 1 if float(p["sigma"]) >= 0 else -1; sK = 1 if float(p["sK"]) >= 0 else -1
    th_hi = min(a1 + a2, 360 - a1 - a2) - max(m, float(p["smhi"]))
    out = dict(ok=False, th_hi=th_hi)
    u1 = np.array([[0.0, 0.0, 1.0]]); u3 = np.array([[math.sin(th_hi * D2R), 0.0, math.cos(th_hi * D2R)]])
    u2, h2 = KA.closure_v(u1, u3, np.array([a1]), a2, sg); uK, hK = KA.closure_v(u1, u2, np.array([b1]), np.array([b2]), sK)
    if not (h2[0] > 0 and hK[0] > 0): _LAW_CACHE[key] = out; return out
    u1, u2, u3, uK = u1[0], K.unit(u2[0]), u3[0], K.unit(uK[0])
    # opening sense of kappa (raises a1e) and stretching sense of q (raises th)
    e = 1e-3
    s_open = 1.0 if _ang(_rot(uK, e)[0] @ u1, u2) > a1 else -1.0
    s_q = 1.0 if _ang(u1, _rot(u2, e)[0] @ u3) > th_hi else -1.0
    r_law = float(p["r_law"]); rho_n = float(p["rho"]) / r_law; d_deg = math.degrees(float(p["d_mm"]) / r_law)
    eK, fK = _frame(uK); ts = np.radians(np.arange(0.0, 70.01, 0.1))
    best = None
    for side in ((-1.0, 1.0) if not p.get("side") else (float(np.sign(p["side"])),)):
        Lt = b2 + side * d_deg
        if not (5.0 < Lt < 175.0): continue
        ax = K.unit(np.cross(u2, uK)); mpt = _rot(ax, Lt * D2R)[0] @ u2       # closest-approach point on the great circle u2 -> uK
        p0 = _rot(u2, -s_q * float(p["psi_c"]) * D2R)[0] @ mpt               # the tip at the onset (q = 0)
        pt = np.einsum("nij,j->ni", _rot(u2, s_q * ts), p0)
        pp = pt - (pt @ uK)[:, None] * uK; rp = np.linalg.norm(pp, axis=1)
        if rp.min() <= rho_n + 1e-6: continue
        az = np.unwrap(np.arctan2(pp @ fK, pp @ eK)); s_m = float(np.sign(az[5] - az[0])) or 1.0
        azc = az + s_m * np.arcsin(np.clip(rho_n / rp, -1, 1)); kap = azc - azc[0]
        if np.sign(kap[5]) != s_open: continue                              # this side's flank would close K
        best = (side, Lt, p0, pt, pp, rp, az, s_m, kap); break
    if best is None: _LAW_CACHE[key] = out; return out
    side, Lt, p0, pt, pp, rp, az, s_m, kap = best
    R1 = _rot(uK, kap); R2 = _rot(u2, s_q * ts)
    u1k = np.einsum("nij,j->ni", R1, u1); u3q = np.einsum("nij,j->ni", R2, u3)
    th = _ang(u1k, u3q); a1e = _ang(u1k, u2[None])
    # pressure angle: roller velocity (about u2) vs the flank normal (azimuth azc + 90 deg about uK)
    v = np.cross(np.broadcast_to(u2, pt.shape), pt)
    nvec = -np.sin(azc_ := (az + s_m * np.arcsin(np.clip(rho_n / rp, -1, 1))))[:, None] * eK + np.cos(azc_)[:, None] * fK
    pa = np.degrees(np.arccos(np.clip(np.abs((nvec * v).sum(1)) / np.maximum(np.linalg.norm(v, axis=1), 1e-12), 0, 1)))
    r_c = np.sqrt(np.maximum(rp ** 2 - rho_n ** 2, 0)) * r_law                # contact radius from K's axis on the flank (mm)
    kabs = np.abs(kap); dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
    h = 1e-4

    def th_of(tt, kk):
        Ra = _rot(uK, s_open * kk); Rb = _rot(u2, s_q * tt)
        return _ang(np.einsum("nij,j->ni", Ra, u1), np.einsum("nij,j->ni", Rb, u3))
    a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
    sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
    lift = (sC > 1e-9) & (sC < dk - 1e-9)
    rate = 1.0 / np.maximum(np.radians(dth), 1e-12)                          # dq / dth (rad / rad)
    if float(p["d_mm"]) < K.HUB_R + float(p["rho"]) + 1.0: emb, rmax = "crown", K.HUB_R
    else: emb, rmax = "beside", float(p["lug_max"])
    m3e = np.minimum(th - np.abs(a1e - a2), np.minimum(a1e + a2, 360 - a1e - a2) - th)
    cK = _ang(np.broadcast_to(uK, u3q.shape), u3q)                            # sub-chain J1 - K - J3 (J2 driven): its margin
    msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
    good = ((dth > 0) & (rate <= RATE_MAX) & (pa <= float(p["pa_max"])) & (r_c <= rmax) & ~lift & (a1e <= float(p["a1max"]) + 1e-9)
            & (m3e >= m - 1e-6) & (msub >= m - 1e-6) & (np.sign(kap) * s_open >= 0))
    good[0] = True
    nval = int(np.argmin(good)) if not good.all() else len(good)
    why_end = None
    if nval < len(good):
        j = nval
        why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "pressure" if pa[j] > float(p["pa_max"]) else
                   "tooth" if r_c[j] > rmax else "liftoff" if lift[j] else "stopB" if a1e[j] > float(p["a1max"]) else
                   "m3e" if m3e[j] < m else "msub" if msub[j] < m else "sign")
    # the tail tip in link 2's frame: coefficients on (u2, u3, n23) at the onset
    n23 = K.unit(np.cross(u2, u3)); Mb = np.stack([u2, u3, n23], 1); coef = np.linalg.solve(Mb, K.unit(p0))
    # the flank direction at stop A in link 1a's frame: coefficients on (uK, u1, n_K1) (the beside embodiment's lug)
    azc0 = float(az[0] + s_m * math.asin(min(1.0, rho_n / rp[0]))); fl = math.cos(azc0) * eK + math.sin(azc0) * fK
    nK1 = K.unit(np.cross(uK, u1)); coefL = np.linalg.solve(np.stack([uK, u1, nK1], 1), fl)
    out = dict(ok=nval > 1, side=side, Lt=Lt, emb=emb, th=th[:nval], a1e=a1e[:nval], ts=ts[:nval], kap=kap[:nval], pa=pa[:nval],
               r_c=r_c[:nval], rate=rate[:nval], th_hi=th_hi, th_max=float(th[nval - 1]), why_end=why_end, coef=coef, coefL=coefL,
               dK_max=float(np.degrees(kabs[:nval].max())), t_max=float(np.degrees(ts[nval - 1])),
               tip_from_u2=float(_ang(u2, p0)))
    _LAW_CACHE[key] = out
    return out


def law(p1, p3, p):
    """-> a1e, state (0 A, +1 driven by the tooth), th. Folded side: no tooth (nan beyond th_lo) unless fold_tooth."""
    if not p.get("cam"): return KR.law(p1, p3, p)
    a1, a2 = float(p["a1"]), float(p["a2"]); m = K.FOLD_MARGIN
    th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1)))
    th_lo = abs(a1 - a2) + max(m, float(p["smlo"])); L = geneva(p); th_hi = L["th_hi"]
    a1e = np.full(len(th), a1); state = np.zeros(len(th), int)
    a1e[th < th_lo] = np.nan
    hi = th > th_hi
    if L.get("ok"):
        inlaw = hi & (th <= L["th_max"] + 1e-9)
        a1e[inlaw] = np.interp(th[inlaw], L["th"], L["a1e"]); state[inlaw] = 1
        a1e[hi & ~inlaw] = np.nan
    else:
        a1e[hi] = np.nan
    return a1e, state, th


KA.law = law


def _tip(p2, p3, coef):
    return K.unit(coef[0] * K.unit(p2) + coef[1] * K.unit(p3) + coef[2] * K.unit(np.cross(p2, p3)))


def build(B, F, p):
    """variant A's chain + inv3 / end_extra + the tail, the roller and hub K's tooth height"""
    k = KR.kinematics(F, p); p1, p2, p3, pK, ok = k["p1"], k["p2"], k["p3"], k["pK"], k["ok"]
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), k["psi"], K.axis_angle(p2, pK, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    capK = float(p.get("capK", 0) or 0); cam = bool(p.get("cam")) and bool(p.get("tail", 1)); L = geneva(p) if cam else {}
    tK = K.CROWN + capK                                      # the tooth blade (r_c <= HUB_R, in the roller's layer) is not extra metal
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K", t=tK), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]; end = K.HUB_R + 2.0 + float(p.get("end_extra", 0.0)); inv3 = int(float(p.get("inv3", 0)) >= 0.5)
    if int(p.get("flipK", 1)):                               # K's stack flipped: link 1a (with the tooth on K's cap) is the UPPER member at K
        l1b = K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", 0.0), ("hub2", 0.0)), end_mm=end)
        l1a = K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", K.STACK + KA.KX)),
                             over=[("link1b", 1.0)], end_mm=max(end, K.HUB_R + 6.0))
        first = [l1b, l1a]
    else:
        l1a = K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0)), end_mm=end)
        l1b = K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK + KA.KX), ("hub2", 0.0)),
                             over=[("link1a", 1.0)], end_mm=max(end, K.HUB_R + 6.0))
        first = [l1a, l1b]
    if inv3:
        l2 = K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", 0.0)),
                            over=[("link1a", 1.0), ("link1b", 1.0)], end_mm=end)
        neck = K.strap_member("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), width=14.0, t=6.0, ramp_to=(("hub3", K.STACK), (None, 0)),
                              over=[("link2", 1.0)])
        mem = hubs + first + [l2, neck]
    else:
        neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
        l2 = K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1a", 1.0), ("link1b", 1.0), ("neck", 1.0)], end_mm=end)
        mem = hubs + first + [neck, l2]
    info = {}
    if cam and L.get("ok"):
        tip = _tip(p2, p3, L["coef"]); tw = float(p.get("tail_w", 8.0))
        # the roller stub: the last 2 BOSS_R of the tail, its underside >= hub K's cap + 1 mm (crown) / link 1a + 1 (beside)
        tg = K.unit(p2 - np.einsum("ni,ni->n", p2, tip)[:, None] * tip); g = 2 * BOSS_R / 70.0
        tipA = K.unit(math.cos(g) * tip + math.sin(g) * tg)                                       # 8 mm back toward hub 2
        dz = (K.CROWN + capK + 1.2) if L["emb"] == "crown" else (K.STACK + KA.KX + t + 1.2)
        roller = K.strap_member("roller", tipA, tip, ("J2",), width=2 * BOSS_R, t=ROLLER_H, ramp_to=(("hubK", dz), ("hubK", dz)),
                                end_mm=2 * BOSS_R + 2.0, climb_deg=None)
        tail = K.strap_member("tail", p2, tipA, ("J2",), width=tw, t=t, ramp_to=(("hub2", K.STACK), ("roller", ROLLER_H)),
                              over=[("link1a", 1.0), ("link1b", 1.0), ("hubK", 1.0)], end_mm=end)
        mem = mem + [roller, tail]
        if L["emb"] == "beside":                              # the tooth lug on link 1a: K's rim -> lug_max along the flank, 6 mm wide
            fl = K.unit(L["coefL"][0] * K.unit(pK) + L["coefL"][1] * K.unit(p1) + L["coefL"][2] * K.unit(np.cross(pK, p1)))
            gl = float(p["lug_max"]) / 70.0; lugE = K.unit(math.cos(gl) * K.unit(pK) + math.sin(gl) * fl)
            mem.append(K.strap_member("lug", pK, lugE, ("K",), width=6.0, t=t, ramp_to=(("hubK", K.STACK + KA.KX), ("hubK", K.STACK + KA.KX)),
                                      end_mm=float(p["lug_max"]) + 2.0))
        info.update(tail_deg=round(float(_ang(p2, tip).mean()), 1), emb=L["emb"])
    o = ok
    info.update(residual_deg=round(float(k["res"][o].max()), 5) if o.any() else None,
                stretched=int(((k["state"] == 1) & o).sum()), a1e_max=round(float(k["a1e"][o].max()), 2) if o.any() else None)
    return K.Chain(members=mem, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3), info=info)


KA.build = build; KR.build = build


def evaluate(B, params):
    p = KR.stops(dict(PARAMS, **params))
    p["inv3"] = int(float(p.get("inv3", 0)) >= 0.5); p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    p, r = KR.evaluate(B, p)
    L = geneva(p) if p.get("cam") else {}
    r["drive"] = dict(ok=bool(L.get("ok")), emb=L.get("emb"), side=L.get("side"), L_t=round(L.get("Lt", 0.0), 2), tip_deg=round(L.get("tip_from_u2", 0.0), 1),
                      th_hi=round(L.get("th_hi", 0.0), 2), th_max=round(L.get("th_max", 0.0), 2) if L.get("ok") else None,
                      dK_max=round(L.get("dK_max", 0.0), 1), t_max=round(L.get("t_max", 0.0), 1), why_end=L.get("why_end"),
                      pa_max_used=round(float(L["pa"].max()), 1) if L.get("ok") else None, rc_max=round(float(L["r_c"].max()), 1) if L.get("ok") else None,
                      rate_max_used=round(float(L["rate"].max()), 2) if L.get("ok") else None)
    if p.get("cam") and not L.get("ok"):                     # no working drive = not this design (a plain 3R with a stuck K, no tail)
        r["gap_nodrive"] = r["gap"]; r["gap"] = float(r["gap"]) + 100.0; r["honest"] = False
        r.setdefault("audit", []).append("drive: the one-tooth law has no valid prefix (no tail built)")
    kin = B._kit_last.get("kin")
    if kin is not None:
        ok = kin["ok"]; st = kin["state"]; ws = np.array([k_ == "ws" for k_ in B.kind])
        r["drive"].update(stretched_ws=int((ok & ws & (st == 1)).sum()), A_ws=int((ok & ws & (st == 0)).sum()), closes_ws=int((ok & ws).sum()))
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SP._jsonable(v)}


def frozen(p0, wear="bench", out=None):
    """KR.frozen (fit Bench(60,160) fast, wear frozen, continuity flood fill) through this model's law and build"""
    p = KR.stops(dict(PARAMS, **p0))
    d = KR.frozen(p, wear, out)
    if out:
        o = json.load(open(out)); o["model"] = "docs/concepts/models/geneva-tail-knuckle-3r.py"; json.dump(o, open(out, "w"), indent=1, default=float)
    return d


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        frozen(par, sys.argv[3] if len(sys.argv) > 3 else "bench", sys.argv[4] if len(sys.argv) > 4 else None); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"],
                          honest=r.get("honest"), audit=r.get("audit"), drive=r.get("drive"), overhead=r.get("overhead"), min_metal=r.get("min_metal_skin"),
                          inband_member=r.get("inband_member"), secs=round(time.time() - t, 1)), default=float))
