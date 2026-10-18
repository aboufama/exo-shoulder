"""cap-nullspace-4r: a redundant spherical 4R over the shoulder cap (Keemink 2018 TNSRE 26(4) class) whose 1-D null-space
is set by two preloaded torsion springs (J0 and J3) inside own-angle stops - the unpowered MVP1 cell - with the
clearance-chosen ghost as its bound and the plain cap-pole 3R as the like-for-like control.

Chain (all axes through GH, every hub an O20 v5 stack, 12 x 3 Ti straps, K7 neck):
  scapula handler -> J0 (counted R, scapula-fixed axis c, a0 from the cap pole b toward bearing beta; torsion spring to
  the base) -> link 0 (a0) -> J1 (ACTIVE R; rest at the cap pole b = bvec(b_az, b_el); dowel stop on the J0-J1-J2 fold)
  -> link 1 (a1) -> J2 (ACTIVE R; dowel stop on the J1-J2-J3 fold) -> link 2 (a2) -> J3 (ACTIVE R, humerus-fixed
  wdir(wd, wa); torsion spring to the arm-end plate) -> K7 neck -> BOTTOM.  4 joints counted, 0 passive translations.

Null-space: with c (scapula) and u3 (arm) fixed per pose, c-J1-J2-u3 is a spherical four-bar (ground angle(c, u3),
cranks a0 and a2, coupler a1). State = q0 (J1 about c, from b) on a nq grid, ASSEMBLY MODE FIXED: sigma = side of J2
from the J1-u3 plane (the q2 stop keeps it), sB = side of J1 from the c-J2 plane (the q1 stop keeps it). sig = 0 lets
the pose-local state take either sigma (the proposer's psi-grid setup; a branch the real metal cannot change into).
A state is feasible iff th = angle(J1, u3) is >= m from the J1-J2-J3 folds, angle(c, J2) is >= m from the J0-J1-J2
folds, the J1 axis sits on the legal seat (az -110..135, el >= -20, x <= 0.2 in the scapula frame) and |q0| <= T.

Policies:
  ctrl   : the plain cap 3R (J1 locked at b; hubs 1-3 only) = the like-for-like control.
  spring : E = sum k_i wrap(q_i - r_i)^2 (q0 = J0 own angle, q1 / q2 = J1 / J2 own angles, q3 = J3 own angle vs the
           arm-end plate); the POSE-LOCAL state is the global minimum over the feasible set; the full-grid flood
           (connect=1) path-tracks the local minimum (descent from the previous state, a stop push <= 10 deg, no snap)
           over the 1432-node envelope grid on 2-deg HG slerps with symmetric neighbour edges; a ws pose counts only if
           the flood reaches its node in a state within 2 deg (same sigma) of its pose-local state.
  band   : the GHOST (bound only): per pose the state minimising every moving member's excess over its target level
           (reads the skin: an oracle no unpowered mechanism has; the kit audit flags it not pose-local).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cap-nullspace-4r.py check ['<json params>']
    big:  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cap-nullspace-4r.py frozen '<json>' --out R.json
"""
import collections, functools, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                       # noqa: E402
import spare_flood as SF                                      # noqa: E402
_spec = importlib.util.spec_from_file_location("srr_for_cn4", os.path.join(HERE, "stop-relay-rocker-3r.py"))
SR = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SR)
SPM = SR.SPM

ID = "cap-nullspace-4r"
NAME = "Cap-pole redundant 4R: spare J1 on a back-seat J0, null-space set by J0 + J3 torsion springs and own-angle stops"
# the proposer's sprung cell (sfit.json (0, 3): k0 0.189 / k3 0.261, q0 rest +8, q3 rest -115) at a0 30 / beta 330, sB +1
PARAMS = dict(b_az=43.2, b_el=59.9, a0=30.0, beta=330.0, a1=50.2, a2=60.3, wd=92.0, wa=-9.0, sB=1, sig=0, m=5.0, T=180.0,
              nq=360, policy="spring", k=[0.189, 0.0, 0.0, 0.261], r=[8.0, 0.0, 0.0, -115.0], q=0.98, connect=1,
              L1=60.0, L2=62.0, Ll0=66.0, Ll1=66.0, Ll2=72.0, q1min=40.0, sigma3=-1)


def wrap(x): return (np.asarray(x) + 180.0) % 360.0 - 180.0


def ang(u, v): return np.degrees(np.arccos(np.clip((u * v).sum(-1), -1, 1)))


def marg(th, a, b): return np.minimum.reduce([th - abs(a - b), a + b - th, 360 - a - b - th])


def seat_ok(uS):
    el = np.degrees(np.arcsin(np.clip(uS[..., 1], -1, 1))); az = np.degrees(np.arctan2(uS[..., 2], -uS[..., 0]))
    return (az >= -110) & (az <= 135) & (el >= -20) & (uS[..., 0] <= 0.20)


def rotv(k, v, a_deg):
    a = np.radians(a_deg)[..., None]; k = K.unit(k)
    return v * np.cos(a) + np.cross(k, v) * np.sin(a) + k * (k * v).sum(-1, keepdims=True) * (1 - np.cos(a))


def geom(p):
    """b (J1 rest, cap pole) and c (J0 axis) in the scapula frame"""
    b = np.asarray(K.bvec(p["b_az"], p["b_el"]), float); t1 = K.unit(np.cross(b, [0, 1.0, 0])); t2 = np.cross(b, t1)
    d = math.cos(math.radians(p["beta"])) * t1 + math.sin(math.radians(p["beta"])) * t2
    return b, math.cos(math.radians(p["a0"])) * b + math.sin(math.radians(p["a0"])) * d


class NS:
    """the null-space states of one configuration, all in the scapula frame (works for any batch of arm poses)"""

    def __init__(s, p):
        s.p = p; s.b, s.c = geom(p); s.QG = np.arange(int(p["nq"])) * 360.0 / int(p["nq"]) - 180.0
        s.U1 = rotv(np.broadcast_to(s.c, (len(s.QG), 3)), np.broadcast_to(s.b, (len(s.QG), 3)), s.QG)     # (n, 3)
        s.seat = seat_ok(s.U1) & (np.abs(s.QG) <= p["T"] + 1e-9)
        s.sigs = (1, -1) if int(p["sig"]) == 0 else (int(p["sig"]),)
        s.k = np.asarray(p["k"], float); s.r = np.asarray(p["r"], float)

    def states(s, u3, ref3):
        """u3, ref3 (P, 3) scapula frame -> dict of (P, ns, n) arrays: J2, ok, Q (P, ns, n, 4), E"""
        p = s.p; P = len(u3); n = len(s.QG); ns = len(s.sigs)
        U1 = np.broadcast_to(s.U1[None], (P, n, 3)); W = np.broadcast_to(u3[:, None, :], (P, n, 3))
        J2s, oks, Qs = [], [], []
        th = ang(U1, W); okth = marg(th, p["a1"], p["a2"]) >= p["m"]
        for sg in s.sigs:
            J2, okc, _ = K.closure(U1.reshape(-1, 3), W.reshape(-1, 3), p["a1"], p["a2"], sg, margin_deg=p["m"] - 1e-6)
            J2 = J2.reshape(P, n, 3); okc = okc.reshape(P, n)
            cc = np.broadcast_to(s.c, (P, n, 3))
            m1 = marg(ang(cc, J2), p["a0"], p["a1"])                                         # J0-J1-J2 fold margin
            sB = np.sign((np.cross(cc, J2) * U1).sum(-1))             # K.closure(c, J2, a0, a1, sB) convention
            ok = okc & okth & (m1 >= p["m"]) & (sB == p["sB"]) & s.seat[None, :]
            q1 = K.axis_angle(U1, cc, J2); q2 = K.axis_angle(J2, U1, W)
            q3 = K.axis_angle(W, np.broadcast_to(ref3[:, None, :], (P, n, 3)), J2)
            J2s.append(J2); oks.append(ok); Qs.append(np.stack([np.broadcast_to(s.QG, (P, n)), q1, q2, q3], -1))
        J2 = np.stack(J2s, 1); ok = np.stack(oks, 1); Q = np.stack(Qs, 1)
        E = (s.k * np.radians(wrap(Q - s.r)) ** 2).sum(-1)
        return dict(J2=J2, ok=ok, Q=Q, E=np.where(ok, E, np.inf))

    # ---- path-tracked flood on the full envelope grid ------------------------------------------------------------
    def step(s, st, sg_i, iq, jump=10.0):
        """one 2-deg slerp step: new state index of the spring's local minimum, or None (jam / snap)"""
        ok = st["ok"][0, sg_i]; E = st["E"][0, sg_i]; n = len(ok); step_deg = 360.0 / n
        if not ok.any(): return None
        if not ok[iq]:                                                   # a stop pushes: nearest feasible state
            idx = np.nonzero(ok)[0]; dd = np.abs(wrap((idx - iq) * step_deg)); k = int(np.argmin(dd))
            if dd[k] > jump: return None
            iq = int(idx[k])
        i0 = iq
        while True:                                                      # descent inside the feasible window
            a, b_ = (iq - 1) % n, (iq + 1) % n; j = a if E[a] < E[b_] else b_
            if E[j] < E[iq]: iq = j
            else: break
            if abs(wrap((iq - i0) * step_deg)) > jump: return None       # a snap through the basin = not followed
        return iq


def frames_S(F, p):
    w = K.wdir(p["wd"], p["wa"])
    u3 = np.einsum("pji,pj->pi", F.RS, F.HG(w)); ref3 = np.einsum("pji,pj->pi", F.RS, F.HG([0.0, -1.0, 0.0]))
    return u3, ref3


def choose(s, st, p, B=None, F=None):
    """pose-local state per pose: (sigma index, q index), okp"""
    ok, E = st["ok"], st["E"]; P, ns, n = ok.shape
    if p["policy"] == "spring":
        flat = E.reshape(P, -1)
    elif p["policy"] == "band":                       # ghost (bound only): every moving member vs its target level
        flat = np.full((P, ns * n), np.inf); I = np.broadcast_to(np.arange(P)[:, None, None], (P, ns, n))[ok]
        RS = F.RS; J1w = np.einsum("pij,nj->pni", RS, s.U1); J1w = np.broadcast_to(J1w[:, None], (P, ns, n, 3))[ok]
        J2w = np.einsum("pij,psnj->psni", RS, st["J2"])[ok]; cw = np.broadcast_to(F.S(s.c)[:, None, None], (P, ns, n, 3))[ok]
        u3w = np.broadcast_to(F.HG(K.wdir(p["wd"], p["wa"]))[:, None, None], (P, ns, n, 3))[ok]
        xy = K.disc_xy(K.HUB_R, 2.5); pen = np.zeros(len(I))

        def penal(R, L):
            R = np.where(np.isfinite(R), R, 400.0); return 20 * np.maximum(0, R - L) + np.maximum(0, L - 12 - R)
        for kk, L in ((J1w, p["L1"]), (J2w, p["L2"])):
            kv = K.unit(kk); a, b2 = K.plane_frame(kv); m_ = len(xy)
            O = xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b2[:, None]
            R = K.requirement(B, np.repeat(I, m_), np.repeat(kv, m_, 0), O=O.reshape(-1, 3)).reshape(-1, m_)
            pen += penal(R, L).max(1) + penal(R, L).mean(1)
        for (U, V, L) in ((cw, J1w, p["Ll0"]), (J1w, J2w, p["Ll1"]), (J2w, u3w, p["Ll2"])):
            ts = np.linspace(0.2, 0.8, 4); D = K.unit(U[:, None, :] * (1 - ts)[None, :, None] + V[:, None, :] * ts[None, :, None])
            R = K.requirement(B, np.repeat(I, 4), D.reshape(-1, 3)).reshape(-1, 4)
            pen += penal(R, L).max(1) + penal(R, L).mean(1)
        q1 = np.abs(wrap(st["Q"][..., 1][ok])); pen += 5 * np.maximum(0, p["q1min"] - np.minimum(q1, 360 - q1))
        F_ = np.full((P, ns, n), np.inf); F_[ok] = pen + 0.001 * np.abs(st["Q"][..., 0][ok]); flat = F_.reshape(P, -1)
    else:
        raise ValueError(p["policy"])
    j = flat.argmin(1); okp = np.isfinite(flat[np.arange(P), j])
    return j // n, j % n, okp


def build(B, F, p):
    w = K.wdir(p["wd"], p["wa"]); p3 = F.HG(w); end = K.HUB_R + 2.0
    if p["policy"] == "ctrl":                                                  # plain cap 3R: J1 locked at b
        b, _ = geom(p); u1 = F.S(b); p2, ok, mg = K.closure(u1, p3, p["a1"], p["a2"], p["sigma3"], margin_deg=p["m"])
        q = np.stack([K.axis_angle(u1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, u1, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
        m = [K.hub_member("hub1", u1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3"),
             K.strap_member("link1", u1, p2, ("J1", "J2"), ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)), over=[("link1", 1.0), ("neck", 1.0)], end_mm=end),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
        ok = ok & np.isfinite(q).all(-1)
        return K.Chain(members=m, ok=ok, q=np.where(np.isfinite(q), q, 0.0), joints=dict(J1=u1, J2=p2, J3=p3), info=dict(q0_range=None))
    s = NS(p); u3S, ref3S = frames_S(F, p); st = s.states(u3S, ref3S); si, qi, okp = choose(s, st, p, B, F)
    P = len(u3S); r_ = np.arange(P)
    u1 = np.einsum("pij,pj->pi", F.RS, s.U1[qi]); p2 = np.einsum("pij,pj->pi", F.RS, st["J2"][r_, si, qi]); c = F.S(s.c)
    if c.ndim == 1: c = np.broadcast_to(c, u1.shape).copy()
    q = st["Q"][r_, si, qi]
    hubs = [K.hub_member("hub0", c, "J0"), K.hub_member("hub1", u1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    links = [K.strap_member("link0", c, u1, ("J0", "J1"), width=12.0, t=3.0, ramp_to=(("hub0", K.STACK), ("hub1", 0.0)), end_mm=end),
             K.strap_member("link1", u1, p2, ("J1", "J2"), width=12.0, t=3.0, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)),
                            over=[("link0", 1.0), ("hub0", 1.0)], end_mm=end),
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=12.0, t=3.0, ramp_to=(("hub2", K.STACK), ("hub3", K.STACK)),
                            over=[("link1", 1.0), ("neck", 1.0), ("link0", 1.0), ("hub0", 1.0)], end_mm=end),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    ok = okp & np.isfinite(q).all(-1)
    sgn = np.array(s.sigs)[si]
    th = ang(np.einsum("pij,pj->pi", F.RS, s.U1[qi]), p3)
    info = dict(q0_range=[float(q[ok, 0].min()), float(q[ok, 0].max())] if ok.any() else None,
                th_fold_margin_min=round(float(marg(th, p["a1"], p["a2"])[ok].min()), 2) if ok.any() else None,
                sub_margin_min=round(float(marg(ang(c, p2), p["a0"], p["a1"])[ok].min()), 2) if ok.any() else None,
                sigma_used=dict(zip(*[x.tolist() for x in np.unique(sgn[ok], return_counts=True)])) if ok.any() else None)
    ch = K.Chain(members=hubs + links, ok=ok, q=np.where(np.isfinite(q), q, 0.0), joints=dict(J0=c, J1=u1, J2=p2, J3=p3), info=info)
    ch._state = (si, qi); ch._s = s
    return ch


def flood(p, seed_elev=30.0, max_states=4, jump=10.0):
    """BFS over (node, sigma, q) on the 1432-node envelope grid (spare_flood.GP / nbrs, symmetric edges), states
    path-tracked by the spring's local descent on 2-deg HG slerps; seeds = nodes of elevation <= seed_elev in their
    pose-local (global-minimum) state. -> states {node: set((sigma index, q index))}"""
    s = NS(p); w = np.asarray(K.wdir(p["wd"], p["wa"]), float); r3 = np.array([0.0, -1.0, 0.0])
    U3 = SF.HGrel @ w; R3 = SF.HGrel @ r3; n = len(s.QG); dq = 360.0 / n
    st_all = s.states(U3, R3); E = st_all["E"].reshape(len(U3), -1)
    states = collections.defaultdict(set); front = []
    for j in range(len(SF.GP)):
        if SF.GP[j, 1] > seed_elev or not np.isfinite(E[j]).any(): continue
        k = int(E[j].argmin()); sk = (k // n, k % n); states[j].add(sk); front.append((j, sk))
    while front:
        nxt = []
        for j, (si, iq) in front:
            for t in SF.nbrs(j):
                if len(states[t]) >= max_states: continue
                M = SF.slerp_u3(j, t, w)[1:]; MR = SF.slerp_u3(j, t, r3)[1:]; st = s.states(M, MR); ok = True; q = iq
                for a in range(len(M)):
                    sub = dict(ok=st["ok"][a:a + 1], E=st["E"][a:a + 1]); q = s.step(sub, si, q, jump)
                    if q is None: ok = False; break
                if not ok: continue
                if any(x[0] == si and abs(wrap((x[1] - q) * dq)) < 2.0 for x in states[t]): continue
                states[t].add((si, q)); nxt.append((t, (si, q)))
        front = nxt
    return states


def connected(B, p, ch):
    """(P,) bool: ws poses whose node the flood reaches in the pose-local state (+- 2 deg, same sigma); clips True
    (their continuity is K2 along the interpolated motion)"""
    states = flood(p); si, qi = ch._state; n = int(p["nq"]); dq = 360.0 / n
    out = np.ones(len(B.kind), bool); miss = 0
    for i in range(len(B.kind)):
        if B.kind[i] != "ws": continue
        j = SF.node_of(B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"])
        if j is None: out[i] = False; miss += 1; continue
        out[i] = any(x[0] == si[i] and abs(wrap((x[1] - qi[i]) * dq)) <= 2.0 for x in states.get(j, ()))
    grid = sum(1 for j in range(len(SF.GP)) if states.get(j))
    return out, dict(grid_conn=round(grid / len(SF.GP), 3), off_grid=miss)


def seat_legal(p):
    """J0's axis (on the scapula handler) and J1's rest both on the legal seat (back of the shoulder / acromion top)"""
    b, c = geom(p); return bool(seat_ok(b)) and (p["policy"] == "ctrl" or bool(seat_ok(c)))


def snap(params):
    """search-safe params: scalar spring entries k0..k3 / r0..r3 (CMA) folded into k / r, bounds on the rest"""
    p = dict(PARAMS, **params); p["k"] = [float(x) for x in p["k"]]; p["r"] = [float(x) for x in p["r"]]
    for i in range(4):
        if f"k{i}" in p: p["k"][i] = max(0.0, float(p[f"k{i}"]))
        if f"r{i}" in p: p["r"][i] = float(p[f"r{i}"])
    p["m"] = max(K.FOLD_MARGIN, float(p["m"])); p["q"] = min(1.0, max(0.9, float(p["q"]))); p["a0"] = min(45.0, max(20.0, float(p["a0"])))
    for k_ in ("sB", "sig", "sigma3", "nq"): p[k_] = int(round(float(p[k_])))
    return p


def evaluate(B, params, near=False):
    p = snap(params)
    if not seat_legal(p):
        return p, dict(gap=275.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, honest=False,
                       audit=["J0 / J1 seat outside the seat rule"], inband_member={})
    r = K.evaluate(B, build, p, cont=p.get("cont", True)); r = SR.declared_audit(r, p); ch = B._kit_last["chain"]
    if p["policy"] == "spring" and p.get("connect", 1):
        take = np.array([SR._taken(B, j) for j in range(len(B.res))]); conn, fi = connected(B, p, ch)
        drop = [j for j in range(len(B.res)) if take[j] and not conn[j]]
        for j in drop: B.res[j] = None
        B._kit_last["take"] = B._kit_last["take"].copy(); B._kit_last["take"][drop] = False
        r["islands_dropped"] = len(drop); r["flood"] = fi
    r = SR.extras(B, r, p)
    r.update({k: ch.info.get(k) for k in ("th_fold_margin_min", "sub_margin_min", "q0_range", "sigma_used")})
    ws = np.array([k == "ws" for k in B.kind]); r["ws_taken"] = int((B._kit_last["take"] & ws).sum())
    return p, r


KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "gap_near1", "min_metal_skin", "overhead",
        "inband_member", "islands_dropped", "flood", "ws_taken", "th_fold_margin_min", "sub_margin_min", "q0_range", "sigma_used", "collide")


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm radial; the flood
    re-run on the big bench's ws poses"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    keep = lambda r: {k: r.get(k) for k in KEYS}
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, json.dumps({k: rf.get(k) for k in ("gap", "reach", "follow", "inband14", "contact", "honest", "ws_taken", "islands_dropped")}), flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        _, r = evaluate(Bb, pf)
    finally:
        K.fit_profiles = fp; K.collisions = coll
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, json.dumps(keep(r), default=float), flush=True)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(dict(PARAMS, **par), o); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print(json.dumps({k: r.get(k) for k in KEYS}, default=float), round(time.time() - t, 1), "s", flush=True)
