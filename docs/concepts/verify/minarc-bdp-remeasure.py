"""Independent verifier (lens: RE-MEASURE) for minarc-stop-knuckle-4r BDp (2026-10-16): variant B (pin knee + spring
knuckle K in link 1), the claim's BD seats with BOTH J2 stops at the 5-deg J1-J3 kit margin, a PHYSICAL dowel-in-slot stop on
J2's own angle q2, hub K cap +6 mm (docs/concepts/rows/minarc-stop-knuckle-4r.json kitrule_*).

The claim's MODEL (docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py) is imported unchanged - it is the object under test.
Everything else here is this verifier's own: the frozen hand-over (every attribute the fit creates, found by diffing the
model's __dict__ before / after the fit - not a hand-written list), the per-pose checks from the MEMBER FRAMES, the near-touch
re-score, the continuity flood fill and the contact-aware flood fill. The claim's harness (minarc-stop-knuckle-4r-kitrule-wear.py
and the re-measure verifier it imports) is NOT imported. H1 runs through its own verified frozen hand-over (pin knee polish
harness frozen_on + extra_checks) on the same benches.

Per taken pose, from the member frames T(m, i) (m: 1 link 1a, 7 link 1b, 2 link 2, 3 member 3):
  * joint axes in the scapula frame: J1 = u1, K = R1 uK, J2 = R1b u2, J3 = R2 u3 (= R3 u3, checked);
  * th = angle(J1, J3), a1e = angle(J1, J2), a2e = angle(J2, J3), b1 = angle(J1, K), c = angle(K, J3), bk2 = angle(K, J2);
  * the kit's J1-J3 fold margin (tools/concept_kit.py lines 25-30) of the effective dyad (a1e, a2e); in its OWN state:
    state A (K on stop A) the plain dyad (a1, a2); forced (J2 on a stop, K open) the moving sub-chain J1-K-J3 (b1, c) AND
    the effective dyad; K's own dyad (b1, bk2) over a1e. A taken pose below FOLD_MARGIN in its own state is knocked out;
  * J2's own angle q2 = rotation of link 2 vs link 1b about u2 (axis error checked) inside the dowel slot; forced poses
    sit ON a stop; K's opening dK (link 1b vs 1a about uK) one-sided (psiA's sign) and within stop B;
  * spring-equilibrium red team: for each forced pose, the smallest |dK| over q2 anywhere in the slot (0.05-deg scan,
    closed form) vs the model's (J2 on the stop) - if the spring can sit lower with J2 off the stop, the model's state is
    not the mechanism's;
  * hub K's cap (r 10, F .. F + 12.25 + capK along uK, sampled here on a 1 mm x 3 deg lattice) vs the skin (exact
    B.dist) and vs every non-adjacent member's metal samples (signed distance to the finite cylinder, >= 1 mm).

Modes (CB_EXACT=1 for the exact wear benches; CB_FOLD_MARGIN sets the margin, default 5):
  wear <bench|held> <BDp|H1> <out.json>         fit Bench(60,160) FAST -> frozen -> wear Bench(110,360) (bench) or the
                                                 re-measure verifier's 1154 disjoint held-out poses (held); continuity (kinematic
                                                 flood fill, below) applied; plain + near-touch
  conn <BDp> <out.json> [taken]                  flood fill over the full 1432-pose workspace grid from the strict rest region
                                                 (elevation 0, K on stop A): 2-deg slerp edges, every step closes and keeps the
                                                 own-state margin and the slot, no q1 / q2 / q3' / pin a / pin b / dK step > 10
                                                 deg, knee branch constant along the edge and equal to the seeds' branch;
                                                 `taken` = contact-aware: nodes are the poses the frozen shape TAKES when worn
                                                 exact on all 1432 grid poses (this verifier's checks applied)

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 docs/concepts/verify/minarc-bdp-remeasure.py wear bench BDp out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KR = _load("bdp_kitrule_model", os.path.join(REPO, "docs", "concepts", "models", "minarc-stop-knuckle-4r-kitrule.py"))
PV = _load("bdp_pk_polish", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py"))      # H1's verified harness + benches
S, PK = KR.S, KR.PK
PFILE = os.path.join(HERE, "minarc-kitrule", "params_floorBD5_phys_cap6.json")
H1ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-pin-knee.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
D2R = math.pi / 180; M5 = KIT.FOLD_MARGIN; STEP, JUMP = 2.0, 10.0
PER_POSE = {"clear", "cmin", "drop", "last_clear", "last_pair", "poses_fit", "fit", "sd_cyl"}


def P_bdp(): return dict(KR.PARAMS, **json.load(open(PFILE)))


def ang(a, b): return np.degrees(np.arccos(np.clip(np.einsum("...i,...i->...", a, b), -1, 1)))


def dmargin(th, a, b):
    """the kit's J1-J3 fold margin of a spherical dyad (a, b) spanning th (deg; arrays ok)"""
    return np.minimum.reduce([th - np.abs(a - b), np.minimum(a + b, 360 - a - b) - th])


def freeze(fitB, wearB, P, Model):
    """fit on fitB, hand EVERY attribute the fit created (by __dict__ diff) to a frozen copy worn on wearB"""
    M1 = Model(fitB, dict(P)); k0 = set(M1.__dict__); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = fitB.mode
    keys = sorted(set(M1.__dict__) - k0 - PER_POSE)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in keys: setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    return Frozen(wearB, P2), fit, M1, keys


def taken_list(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


def rot_err(Rrel, ax): return float(np.degrees(np.arccos(np.clip((Rrel @ ax) @ ax, -1, 1))))


def cap_samples(M):
    """hub K's capped cylinder in link 1a's frame: lateral lattice 1 mm x 3 deg + top disc (this verifier's own sampling)"""
    mem, cen, ax = M.cyl["hubK"]; r = float(M.cyl_r["hubK"]); H = S.CROWN + float(M.p.get("capK", 0) or 0)
    e, f = S.frame_of(ax); t = np.linspace(0, 2 * np.pi, 120, endpoint=False); ring = r * (np.cos(t)[:, None] * e + np.sin(t)[:, None] * f)
    pts = [cen + z * ax + ring for z in np.arange(0, H + 1e-9, 1.0)] + [cen + H * ax + ring]
    for rr in np.arange(1.0, r, 1.5):
        pts.append(cen + H * ax + rr * (np.cos(t)[:, None] * e + np.sin(t)[:, None] * f))
    pts.append((cen + H * ax)[None])
    return mem, cen, ax, r, H, np.concatenate(pts)


def sd_fcyl(X, cen, ax, r, H):
    """signed distance of points X to the finite cylinder (base cen, axis ax, radius r, height H)"""
    w = X - cen; z = w @ ax; rad = np.linalg.norm(w - z[:, None] * ax, axis=1)
    dr = rad - r; dz = np.maximum(-z, z - H)
    out = np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)); inside = np.minimum(np.maximum(dr, dz), 0)
    return out + inside


def member_points(M):
    """metal samples per member (strap / cyl_surf / rigid / link_pts / contact) in each member's own frame"""
    pts = {}
    for src in ("strap", "cyl_surf", "rigid", "link_pts"):
        for nm, v in getattr(M, src, {}).items():
            if isinstance(v, tuple) and len(v) == 2 and np.ndim(v[1]) == 2 and len(v[1]): pts.setdefault(int(v[0]), []).append((f"{src}:{nm}", np.asarray(v[1], float)))
    return pts


def checks_B(M, B, eq_scan=True):
    """this verifier's per-pose checks for variant B under the physical stop (see the docstring); returns (report, bad set)"""
    D = M.D; P = D.p; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = D.a1, D.a2; b1p, b2p = float(P["bk1"]), float(P["bk2"])
    taken = taken_list(B); out = {}; bad = set()
    lo, hi = sorted(D.q2_stops); sp = float(np.sign(D.psiA))
    cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1p * D2R) * math.cos(b2p * D2R)) / (math.sin(b1p * D2R) * math.sin(b2p * D2R))
    dK_max = math.degrees(math.acos(max(-1, min(1, cpsiB))) - abs(D.psiA))
    mem, cen, ax, rK, HK, capX = cap_samples(M); mp = member_points(M)
    rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i); R3, _ = M.T(3, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3; j3b = R3 @ u3
        th = float(ang(u1, j3)); a1e = float(ang(u1, j2)); a2e = float(ang(j2, j3)); b1 = float(ang(u1, jK)); c = float(ang(jK, j3)); bk2 = float(ang(jK, j2))
        dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ u2))
        axe = max(rot_err(R1, u1), rot_err(R1.T @ R1b, uK), rot_err(R1b.T @ R2, u2), rot_err(R2.T @ R3, u3))
        forced = abs(dK) > 1e-6
        m_plain = float(dmargin(th, a1, a2)); m_eff = float(dmargin(th, a1e, a2e)); m_sub = float(dmargin(th, b1, c)); m_kd = float(dmargin(a1e, b1, bk2))
        own = min(m_sub, m_eff) if forced else m_plain
        stop = None
        if forced: stop = "hi" if abs(q2 - D.q2_stops[1]) < abs(q2 - D.q2_stops[0]) else "lo"
        rows.append(dict(i=i, th=th, a1e=a1e, a2e=a2e, b1=b1, c=c, dK=dK, q2=q2, axe=axe, j3d=float(ang(j3, j3b)), forced=forced, stop=stop,
                         m_plain=m_plain, m_eff=m_eff, m_sub=m_sub, m_kd=m_kd, own=own))
        r = rows[-1]
        if own < M5 - 1e-6 or m_eff < M5 - 1e-6 or (forced and m_kd < M5 - 1e-6): bad.add(i); r["why"] = "margin"
        if q2 < lo - 0.05 or q2 > hi + 0.05: bad.add(i); r["why"] = "slot"
        if forced and min(abs(q2 - lo), abs(q2 - hi)) > 0.05: bad.add(i); r["why"] = "forced off stop"
        if dK * sp < -0.05 or abs(dK) > dK_max + 0.05: bad.add(i); r["why"] = "K range"
        if axe > 0.5: bad.add(i); r["why"] = "axis"
        # hub K cap: skin (exact dist on this bench) and non-adjacent members
        Rm, tm = M.T(mem, i); r["cap_skin"] = float(np.min(B.dist(i, M.world(mem, i, capX))))      # body frame = scapula frame @ RS^T
        cw, aw = Rm @ cen + tm, Rm @ ax; pm = 1e9; pm_who = None
        for m, lst in mp.items():
            if m in (mem, 0): continue
            Rq, tq = M.T(m, i)
            for nm, X in lst:
                Y = X @ Rq.T + tq
                if m == 7:                                   # link 1b is K's other body (adjacent): only its metal away from K's axis
                    w = Y - cw; Y = Y[np.linalg.norm(w - (w @ aw)[:, None] * aw, axis=1) > rK + 1.0]
                    if not len(Y): continue
                d = float(sd_fcyl(Y, cw, aw, rK, HK).min())
                if d < pm: pm, pm_who = d, f"m{m}:{nm}"
        r["cap_part"] = pm; r["cap_part_who"] = pm_who
        if r["cap_skin"] < 0: r["cap_contact"] = True
        if pm < S.PART_CLEAR: bad.add(i); r["why"] = "cap vs part"
    # spring equilibrium red team (forced poses): min |dK| over q2 anywhere in the slot
    eq = dict(forced=0, lower_inside=0, max_gain_deg=0.0)
    if eq_scan:
        q2g = np.radians(np.arange(lo, hi + 1e-9, 0.05)); p = S.rotm(u2, q2g) @ u3
        A0 = (u1 @ uK) * (p @ uK); Bk = p @ u1 - A0; Ck = np.cross(uK, p) @ u1; Rk = np.hypot(Bk, Ck); f0 = np.arctan2(Ck, Bk)
        for r in rows:
            if not r["forced"]: continue
            eq["forced"] += 1; x = (math.cos(r["th"] * D2R) - A0) / Rk; okx = np.abs(x) <= 1; g = np.arccos(np.clip(x, -1, 1))
            best = np.inf
            for sg in (-1, 1):
                d = (f0 + sg * g + np.pi) % (2 * np.pi) - np.pi
                good = okx & (d * sp >= -1e-9) & (np.abs(np.degrees(d)) <= dK_max + 1e-6)
                if good.any(): best = min(best, float(np.degrees(np.abs(d[good])).min()))
            gain = abs(r["dK"]) - best
            r["eq_min_dK"] = best
            if gain > 0.1: eq["lower_inside"] += 1; eq["max_gain_deg"] = max(eq["max_gain_deg"], round(gain, 3))
    st = lambda f: [r for r in rows if f(r)]
    A = st(lambda r: not r["forced"]); Fh = st(lambda r: r["forced"] and r["stop"] == "hi"); Fl = st(lambda r: r["forced"] and r["stop"] == "lo")
    mn = lambda L, k: round(min(x[k] for x in L), 3) if L else None
    out["states_taken"] = dict(A=len(A), stretched=len(Fh), folded=len(Fl))
    out["th_margin_own_state"] = dict(min=mn(rows, "own"), A_plain=mn(A, "m_plain"), stretched_sub=mn(Fh, "m_sub"), stretched_eff=mn(Fh, "m_eff"),
                                      folded_sub=mn(Fl, "m_sub"), folded_eff=mn(Fl, "m_eff"), eff_all=mn(rows, "m_eff"), K_dyad_forced=mn(Fh + Fl, "m_kd"),
                                      plain_dyad_on_forced=mn(Fh + Fl, "m_plain"),
                                      lt5=sum(1 for r in rows if r["own"] < 5), lt10=sum(1 for r in rows if r["own"] < 10), rule=M5)
    out["q2_slot"] = dict(stops=[round(lo, 3), round(hi, 3)], arc=round(hi - lo, 2), range_taken=[mn(rows, "q2"), round(max(r["q2"] for r in rows), 3) if rows else None],
                          forced_off_stop_max=round(max([min(abs(r["q2"] - lo), abs(r["q2"] - hi)) for r in Fh + Fl] or [0]), 4))
    out["K"] = dict(dK_range=[mn(rows, "dK"), round(max(r["dK"] for r in rows), 3) if rows else None], dK_max_stopB=round(dK_max, 2), psiA_sign=sp)
    out["axis_err_max"] = round(max([r["axe"] for r in rows] or [0]), 4); out["j3_two_frames_max_deg"] = round(max([r["j3d"] for r in rows] or [0]), 4)
    out["spring_equilibrium"] = eq
    out["capK"] = dict(height=HK, skin_min=round(min([r["cap_skin"] for r in rows] or [1e9]), 3), skin_lt1=sum(1 for r in rows if r["cap_skin"] < 1),
                       part_min=round(min([r["cap_part"] for r in rows] or [1e9]), 3),
                       part_min_who=min(rows, key=lambda r: r["cap_part"])["cap_part_who"] if rows else None)
    out["knocked_out"] = len(bad); out["knocked_why"] = {}
    for r in rows:
        if "why" in r: out["knocked_why"][r["why"]] = out["knocked_why"].get(r["why"], 0) + 1
    low = sorted(rows, key=lambda r: r["own"])[:6]
    lab = lambda i: dict(kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    out["lowest_own_margin"] = [dict(own=round(r["own"], 3), state=("A" if not r["forced"] else r["stop"]), **lab(r["i"])) for r in low]
    return out, bad, {r["i"]: r for r in rows}


def checks_H1(M, B):
    """H1 (3R pin knee): J1-J3 margin from the member frames"""
    D = M.D; u1, u2, u3 = D.u; a1, a2 = math.degrees(D.A[0]), math.degrees(D.A[1]); rows = []
    for i in taken_list(B):
        R1, _ = M.T(1, i); R2, _ = M.T(2, i); j2 = R1 @ u2; j3 = R2 @ u3
        rows.append(float(dmargin(float(ang(u1, j3)), float(ang(u1, j2)), float(ang(j2, j3)))))
    bad = {i for i, m in zip(taken_list(B), rows) if m < M5 - 1e-6}
    return dict(th_margin_min=round(min(rows), 3) if rows else None, lt10=sum(1 for m in rows if m < 10), a_deg=[round(a1, 2), round(a2, 2)]), bad


def near_touch(M, B, extra_min=None):
    """near-touch re-score: any taken pose whose lowest metal (bench samples, contact samples, + this verifier's cap samples) is < 1 mm
    counts as contact"""
    res0 = list(B.res); tk = taken_list(B); lows = []
    for i in tk:
        d = min(float(np.min(B.res[i])), float(getattr(M, "cmin", {}).get(i, 1e9)), (extra_min or {}).get(i, 1e9)); lows.append((d, i))
    for d, i in lows:
        if d < 1.0: B.res[i] = np.r_[B.res[i], -1e-3]
    g = B.report()["gap"]; B.res = res0; lows.sort()
    return dict(gap_near1=g, near1_poses=sum(1 for d, _ in lows if d < 1), min_mm=round(lows[0][0], 3) if lows else None,
                low=[dict(mm=round(d, 3), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for d, i in lows[:5]])


# ---------------- continuity ----------------
def ws_grid():
    Z = CB._poses_all(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    return Z, W, Z["POSE"][W].astype(float), Z["HG"][W].astype(float)


def kin_nodes(D, Q, R_tol):
    """closure + every per-pose rule this verifier applies, from the model's ik outputs (frames, not the model's flags alone)"""
    u1, u2, u3 = D.u; uK = D.uK
    q, ok, X1, X2, X3, s = D.ik(Q)
    st = D._state.copy(); K = D.knee(s); X1b = D._X1b[0]
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    j3 = np.einsum("nij,j->ni", X2[0], u3); j2 = np.einsum("nij,j->ni", X1b, u2); jK = np.einsum("nij,j->ni", X1[0], uK)
    th = ang(u1[None], j3); a1e = ang(u1[None], j2); a2e = ang(j2, j3); b1 = ang(u1[None], jK); cc = ang(jK, j3)
    forced = st != 0
    own = np.where(forced, np.minimum(dmargin(th, b1, cc), dmargin(th, a1e, a2e)), dmargin(th, D.a1, D.a2))
    lo, hi = sorted(D.q2_stops); q2 = np.degrees(PK.wrap(q[:, 1]))
    ok &= (own >= M5 - 1e-6) & (q2 >= lo - 0.05) & (q2 <= hi + 0.05)
    dKd = np.degrees(D._dK)
    qq = np.c_[np.degrees(q[:, :2]), np.degrees(q[:, 2] + K["phi"]), np.degrees(K["qa"]), np.degrees(K["qb"]), dKd]
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]; sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    return ok, qq, sgn, st, own


def flood(POSE, HG, nodes, seeds, D, R_tol):
    key = {(x[0], x[1], x[2]): i for i, x in enumerate(map(tuple, POSE))}
    vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]
    _, _, sg0, _, _ = kin_nodes(D, HG, R_tol)

    def nbrs(i):
        x = list(POSE[i, :3])
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if d == 2:                                    # axial wraps at +-180
                    jj = jj % len(vals[2])
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None and t != i: yield t
        if x[2] in (180.0, -180.0):
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t
    stats = dict(tested=0, passed=0, refused_rule=0, refused_jump=0, refused_branch=0); jump_by = np.zeros(6, int)
    branch0 = sorted(set(sg0[seeds].tolist()))
    cache = {}

    def edge(a, b):
        k = (min(a, b), max(a, b))
        if k in cache: return cache[k]
        angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude()); n = max(2, int(math.ceil(angd / STEP)) + 1)
        Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, sg, _, _ = kin_nodes(D, Qs, R_tol); stats["tested"] += 1; res = True
        if not o.all(): stats["refused_rule"] += 1; res = False
        else:
            d = np.abs((np.diff(q, axis=0) + 180) % 360 - 180)
            if d.max() > JUMP: stats["refused_jump"] += 1; jump_by[int(np.argmax(d.max(0)))] += 1; res = False
            elif len(set(sg.tolist())) > 1 or sg[0] not in branch0: stats["refused_branch"] += 1; res = False
        if res: stats["passed"] += 1
        cache[k] = res; return res
    cn = np.zeros(len(POSE), bool); front = [int(i) for i in np.nonzero(seeds)[0]]; cn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if nodes[b] and not cn[b] and edge(a, b): cn[b] = True; nxt.append(b)
        front = nxt
    stats["jump_by_joint"] = dict(zip(("q1", "q2", "q3'", "pin_a", "pin_b", "dK"), jump_by.tolist())); stats["seed_branch"] = branch0
    return cn, stats


def conn(outp, taken_mode=False, P=None):
    t0 = time.time(); P = P or P_bdp(); Z, W, POSE, HG = ws_grid()
    fitB = PV.fast_bench(60, 160)
    if taken_mode:
        old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"
        try: Bw = CB.Bench(20, 20)
        finally:
            if old is None: os.environ.pop("CB_EXACT")
            else: os.environ["CB_EXACT"] = old
        Bw.idx = W.copy(); Bw.kind = ["ws"] * len(W); Bw.clip = ["Workspace (envelope)"] * len(W)
        Bw.poses = [dict(plane=float(x[0]), elev=float(x[1]), axial=float(x[2]), flex=float(x[3]), pron=float(x[4])) for x in POSE]
        Bw.res = [None] * len(W); Bw._skin = {}; Bw._ex = {}; Bw._frames = {}; Bw.grid = None; Bw._V = None; Bw.mode = "exact"; Bw.key = "bdp-wsall"
        M, fitr, M1, keys = freeze(fitB, Bw, P, KR.KModel); M.run(); ex, bad, rows = checks_B(M, Bw, eq_scan=False)
        for i in bad: Bw.res[i] = None
        D = M.D; R_tol = float(M.p["R_tol"])
        nodes_model = np.array([Bw.res[i] is not None and float(np.min(Bw.res[i])) >= 0 for i in range(len(W))])
        ok, qq, sgn, st, own = kin_nodes(D, HG, R_tol)
        nodes = nodes_model & ok; extra = dict(worn_checks=ex, taken_not_kin_ok=int((nodes_model & ~ok).sum()))
    else:
        M1 = KR.KModel(fitB, dict(P)); D = KR.KRDesign(dict(M1.p)); D.m = np.array(M1.D.m, float); D.m[2] = 0.0
        _ = D.ik(HG[:2]); R_tol = float(M1.p["R_tol"])
        ok, qq, sgn, st, own = kin_nodes(D, HG, R_tol); nodes = ok; extra = {}
    elev = POSE[:, 1]
    seeds = nodes & (elev == 0) & (st == 0)
    cn, stats = flood(POSE, HG, nodes, seeds, D, R_tol)
    bidx = np.asarray(CB._select(110, 360)[0]); wpos = {int(g): k for k, g in enumerate(W)}; bws = [wpos[int(g)] for g in bidx if int(g) in wpos]
    oh = elev >= 140; sname = {0: "A", 1: "stretched", -1: "folded"}
    out = dict(mode="contact-aware (taken)" if taken_mode else "kinematic", fold_margin=M5, m=[round(float(x), 4) for x in D.m], step_deg=STEP, jump_deg=JUMP,
               grid=dict(poses=len(W), nodes=int(nodes.sum()), seeds=int(seeds.sum()), connected=int(cn.sum()), islands=int((nodes & ~cn).sum()),
                         nodes_by_state={sname[s]: int((nodes & (st == s)).sum()) for s in (0, 1, -1)},
                         connected_by_state={sname[s]: int((cn & (st == s)).sum()) for s in (0, 1, -1)},
                         overhead140=dict(poses=int(oh.sum()), nodes=int((nodes & oh).sum()), connected=int((cn & oh).sum())),
                         min_own_margin_nodes=round(float(own[nodes].min()), 3) if nodes.any() else None),
               bench110_360=dict(ws=len(bws), nodes=int(nodes[bws].sum()), connected=int(cn[bws].sum())),
               branch_signs_nodes=sorted(set(sgn[nodes].tolist())), edges=stats,
               islands=[dict(plane=float(POSE[i, 0]), elev=float(POSE[i, 1]), axial=float(POSE[i, 2]), state=sname[int(st[i])]) for i in np.nonzero(nodes & ~cn)[0][:60]],
               connected_keys=[[float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])] for i in np.nonzero(cn)[0]], **extra)
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in out if k not in ("connected_keys", "islands", "worn_checks")}, default=float), flush=True)
    return out


def wear(wb, which, outp):
    t0 = time.time()
    fitB = PV.fast_bench(60, 160)
    wearB = PV.held_bench() if wb == "held" else (PV.fast_bench(20, 40) if os.environ.get("BDP_SMOKE") else CB.Bench(n_clip=110, n_ws=360))
    cres = None
    if which == "H1":
        P = dict(H1ROW["v_polish_params"]); M, fitr, M1 = PV.frozen_on(fitB, wearB, P); keys = None
        r = M.run(); model = {k: r[k] for k in KEYS}
        ex0, bad0 = PV.V.extra_checks(M, wearB); exm, badm = checks_H1(M, wearB); bad = set(bad0) | set(badm); ex = dict(h1_verified_checks_bad=len(bad0), **exm)
        capmin = None
    else:
        P = P_bdp(); M, fitr, M1, keys = freeze(fitB, wearB, P, KR.KModel)
        r = M.run(); model = {k: r[k] for k in KEYS}
        same = dict(f=bool(np.allclose(M.f, M1.f)), fK=bool(abs(M.fK - M1.fK) < 1e-9), tr=bool(abs(M.tr - M1.tr) < 1e-9), m=bool(np.allclose(M.D.m, M1.D.m)),
                    q2_stops=bool(np.allclose(M.D.q2_stops, M1.D.q2_stops)), capK_crown=float(getattr(M.cyl_r["hubK"], "crown", S.CROWN)))
        ex, bad, rows = checks_B(M, wearB); ex["frozen_same_as_fit"] = same; ex["handed_over"] = keys
        capmin = {i: rr["cap_skin"] for i, rr in rows.items()}
    res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in KEYS}; nt_c = near_touch(M, wearB, capmin)
    if which != "H1":                                         # continuity: this verifier's own kinematic flood fill, same fit + margin
        cj = conn(outp.replace(".json", "_conn.json"), P=P); ck = {tuple(x) for x in cj["connected_keys"]}
        assert np.allclose(np.array(cj["m"])[:2], np.array(M.D.m)[:2], atol=1e-3), (cj["m"], M.D.m)
        tk = taken_list(wearB)
        drop = [i for i in tk if wearB.kind[i] == "ws" and (float(wearB.poses[i]["plane"]), float(wearB.poses[i]["elev"]), float(wearB.poses[i]["axial"])) not in ck]
        for i in drop: wearB.res[i] = None
        rcc = wearB.report(); ntc = near_touch(M, wearB, capmin)
        cres = dict(ws_taken=sum(1 for i in tk if wearB.kind[i] == "ws"), dropped_unconnected=len(drop), **{k: rcc[k] for k in KEYS}, **ntc,
                    score=round(100 * (1 - rcc["gap"] / 275), 2))
    final = cres or dict(**corrected, **nt_c, score=round(100 * (1 - corrected["gap"] / 275), 2))
    el = np.array([p["elev"] for p in wearB.poses]); kind = np.array(wearB.kind)
    ohw = [i for i in range(len(el)) if el[i] >= 140 and kind[i] == "ws"]
    oh = dict(ws=len(ohw), taken=sum(1 for i in ohw if wearB.res[i] is not None and float(np.min(wearB.res[i])) >= 0))
    wearB.res = res0
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    out = dict(design=which, wear_bench=wb, n_wear=len(wearB.idx), wear_mode=wearB.mode, fit_mode=fitB.mode, exact=os.environ.get("CB_EXACT") == "1",
               fold_margin=M5, o20_only=KIT.O20_ONLY, params=P, fit=fitr, model=model, extra=ex, bad_removed=len(bad), corrected=corrected,
               corrected_near=nt_c, connected=cres, final=final, overhead140_ws=oh, why=why, secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(design=which, wear=wb, mode=wearB.mode, margin=M5, fit=fitr, model=model, corrected=corrected, final=final,
                          extra={k: v for k, v in ex.items() if k not in ("handed_over",)}, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "wear": wear(a[1], a[2], a[3])
    elif a[0] == "conn": conn(a[2], taken_mode=len(a) > 3 and a[3] == "taken")
    else: raise SystemExit(__doc__)
