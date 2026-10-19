"""freek-oracle-route-knuckle-4r: the FREE-K ORACLE BOUND with an anterior link-2 corridor (round 104, lens B).

An INSTRUMENT, never a claim: no unpowered mechanism picks K per pose, so this is the ceiling of every K law / K spring /
J3-split determination (cells B / C of the catalogue entry) at the given seats and shape.

Chain (= skinnormal-shortk-knuckle-4r on the k33 seats, docs/concepts/models/skinnormal-shortk-knuckle-4r.py, imported
UNCHANGED with its verified minarc kitrule harness and the judge's stop pricing):
  J1 (ACTIVE R, O20) -> link 1a -> K (COUNTED R, SENSED; here: ORACLE within [5.5-deg floor, stop B]) -> link 1b -> J2 (ACTIVE R,
  O20, own-angle q2 slot) -> link 2 (planform CORRIDOR bar) -> J3 (ACTIVE R, O20) -> member 3 -> two-pin knee (2 PASSIVE R) -> cuff.
  4 counted joints, 0 passive translations, no gears / pulleys / cables.

What this file adds to the verified harness:
  * ROUTE (params rA deg, rsp deg, rsr deg): link 2's four rows (-3 / -1 / +1 / +3 mm) leave hub 2 on the great circle, bow
    sideways by v(s) = rA sin(pi/2 s / rsp) up to the peak s = rsp and return as rA cos(pi/2 (s - rsp) / (rsr - rsp)) to the
    great circle at s = rsr (s = arc from hub 2's centre, deg); the model's own needed() + ramp profile refits the bar's height
    on the routed rows (fit bench), so the corridor's in-band cost is measured, not assumed. rA > 0 = the +bn side; which side
    is anterior is printed by `side` (bn . x_anterior at rest).
  * ORACLE K (class ODesign): for a bench pose listed in ODesign.TAB {pose key: |dK| deg} the stretched kit state (J2 locked on
    its stop, K at the minimal opening) is replaced by the FREE-K self-motion at that K: K -> a1e on the K dyad (bk1, bk2) ->
    the (a1e, a2) dyad closes on the arm's J3 axis (same assembly branch as state A) -> J2's own angle q2 must sit inside its slot
    (stretched end moved to the 5.5-deg rule for the bound) and the effective dyad keeps the 5.5-deg J1-J3 margin; |dK| <= stop B.
    Everything downstream (q3, member 3, knee, slide residual, part pairs, skin, band, clip continuity incl. the dK jump rule on the
    fit clips' frames) is the model's own code.
  * oracle(): per stretched pose of a bench, NS samples of |dK| on [floor, stop B] (+ the kit's own value), exact skin distance of
    every member-1 / 1b / 2 metal sample (link_pts, cyl_surf, rigid, strap, contact rings), pick = the sample with the largest
    min(distance, CAP) (CAP 2.5 mm: beyond it clearance only costs band; ties -> nearest the kit's K); then ONE composed run of the
    frozen model with the table, so every check applies.

    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/freek-oracle-route-knuckle-4r.py fast '<json>' OUT.json
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 ... wear '<json>' OUT.json      (fit fast -> frozen exact Bench(110,360))
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


SK = _load("sk_for_freek_oracle", os.path.join(HERE, "skinnormal-shortk-knuckle-4r.py"))
KR, EP = SK.KR, SK.EP
KB, S, PK, CB, KIT = KR.KB, KR.S, KR.PK, SK.CB, SK.KIT
RM = _load("rm_for_freek_oracle", os.path.join(REPO, "docs", "concepts", "verify", "minarc-bdp-remeasure.py"))
D2R = math.pi / 180
ID = "freek-oracle-route-knuckle-4r"
K33 = os.path.join(REPO, "docs", "concepts", "verify", "skinnormal-shortk-knuckle-4r", "c_k33_fit60_bench_params.json")
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
BINDERS = (117, 127, 129, 139, 148, 316, 343, 369, 423, 119)
NS, CAP = 17, 2.5
NSR = int(os.environ.get("FO_NSR", "7"))                    # samples of the run-based oracle on the exact bench


def unit(x): x = np.asarray(x, float); return x / np.linalg.norm(x, axis=-1, keepdims=True)


def qkeys(Q): return [r.tobytes() for r in np.round(np.asarray(Q, float).reshape(len(Q), 9), 5)]


# ------------------------------------------------------------------ route (link 2 planform corridor)
def vroute(sdeg, A, sp, sr):
    s = np.asarray(sdeg, float); v = np.zeros_like(s)
    a = s <= sp; v[a] = A * np.sin(0.5 * np.pi * np.clip(s[a] / max(sp, 1e-6), 0, 1))
    b = (s > sp) & (s < sr); v[b] = A * np.cos(0.5 * np.pi * (s[b] - sp) / max(sr - sp, 1e-6))
    return v


class RouteGeo(KB.KGeo):
    def add_links(self, f1, fK, f2, f3):
        out = super().add_links(f1, fK, f2, f3); P = self.D.p; A = float(P.get("rA", 0.0) or 0.0)
        if A == 0.0: return out
        sp, sr = float(P.get("rsp", 25.0)), float(P.get("rsr", 48.0))
        D = self.D; U = [D.u[0], D.uK, D.u[1], D.u[2]]; Cc = [D.c[0], np.zeros(3), D.c[1], D.c[2]]; F = [f1, fK, f2, f3]
        hr = [self.hr[0], S.HUB_R, self.hr[1], self.hr[2]]; C = [Cc[k] + F[k] * U[k] for k in range(4)]
        for lk in out:
            if lk["name"] != "L2": continue
            ka, kb = lk["ka"], lk["kb"]; da, db = unit(C[ka]), unit(C[kb]); R = 0.5 * (np.linalg.norm(C[ka]) + np.linalg.norm(C[kb]))
            ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
            nn = max(4, int(R * ang / S.SPACING * 1.15)); ts = (np.arange(nn) + 0.5) / nn
            dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts])
            vc = vroute(ts * math.degrees(ang), A, sp, sr) * D2R
            dc = np.cos(vc)[:, None] * dirs + np.sin(vc)[:, None] * bn[None]
            # arc length along the routed centre line (the ramp profile's coordinate)
            seg = np.r_[0.0, np.arccos(np.clip(np.einsum("ij,ij->i", dc[1:], dc[:-1]), -1, 1))]
            sarc = (np.cumsum(seg) + 0.5 * ang / nn) * R
            rows = []
            for v in (-3.0, -1.0, 1.0, 3.0):
                dv = unit(dc + (v / R) * bn); pts = R * dv
                def off_axis(k): w = pts - Cc[k]; return np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                keep = (off_axis(ka) > hr[ka]) & (off_axis(kb) > hr[kb]); rows.append((dv, keep, sarc))
            lk["rows"] = rows; lk["route"] = dict(A=A, sp=sp, sr=sr, span=round(math.degrees(ang), 2), bn=[round(float(x), 4) for x in bn])
        self.links = out
        return out


KB.KGeo = RouteGeo


# ------------------------------------------------------------------ oracle K
class ODesign(KR.KRDesign):
    TAB = None                                               # {pose key: |dK| deg}
    SLOT55 = True                                            # oracle bound: J2's stretched slot end at the 5.5-deg rule; False = the design's own stop

    def dKB(self):
        P = self.p; b1, b2 = float(P["bk1"]) * D2R, float(P["bk2"]) * D2R
        c = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1) * math.cos(b2)) / (math.sin(b1) * math.sin(b2))
        return math.degrees(abs(math.acos(max(-1, min(1, c))) - abs(self.psiA)))

    def dK_of_a1e(self, a1e):
        P = self.p; b1, b2 = float(P["bk1"]) * D2R, float(P["bk2"]) * D2R
        c = (np.cos(np.asarray(a1e, float) * D2R) - math.cos(b1) * math.cos(b2)) / (math.sin(b1) * math.sin(b2))
        return np.maximum(np.degrees(np.arccos(np.clip(c, -1, 1))) - math.degrees(abs(self.psiA)), 0.0)

    def floor(self, th):
        """|dK| (deg) at the 5.5-deg rule's floor a1e = th - a2 + m (stretched side)"""
        return self.dK_of_a1e(np.asarray(th, float) - self.a2 + KIT.FOLD_MARGIN)

    def free_solve(self, Q, dKabs):
        """J2 OFF its stop, K at |dK| (deg): closed-form (a1e, a2) dyad closure, same branch as state A"""
        u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN
        w = Q @ u3; wu1 = w @ u1; th = np.degrees(np.arccos(np.clip(wu1, -1, 1)))
        dK = np.sign(self.psiA) * np.asarray(dKabs, float) * D2R
        RK = S.rotm(uK, dK); v2 = np.einsum("nij,j->ni", RK, u2); v3 = np.einsum("nij,j->ni", RK, u3)
        c12 = v2 @ u1; ca2 = math.cos(self.A[1]); det = 1 - c12 ** 2 + 1e-12
        al = (wu1 - c12 * ca2) / det; be = (ca2 - c12 * wu1) / det; cr = np.cross(np.broadcast_to(u1, v2.shape), v2)
        g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / np.maximum(np.einsum("ij,ij->i", cr, cr), 1e-12)
        best = None
        for sg in (1.0, -1.0):
            z = al[:, None] * u1 + be[:, None] * v2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
            q1 = S.sub1(u1, z, w); R1 = S.rotm(u1, q1)
            p2 = np.einsum("nij,nj->ni", R1, v2); br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
            if best is None: best = [q1.copy(), z.copy()]
            else:
                pick = br == self.branch; best[0][pick] = q1[pick]; best[1][pick] = z[pick]
        q1, z = best; R1 = S.rotm(u1, q1)
        q2 = KB.sub1v(v2, v3, z); R2p = KB.rotmv(v2, q2); R12 = R1 @ R2p @ RK
        vv = unit(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3); R123 = R12 @ R3; t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        a1e = np.degrees(np.arccos(np.clip(v2 @ u1, -1, 1))); m3e = KR.dyad_margin(th, a1e, self.a2)
        A, Rr, q0 = self._q2c; sgq = self.q2sgn or 1.0
        rel = sgq * np.degrees(PK.wrap(q2 - q0))
        rlo = math.degrees(math.acos(max(-1.0, min(1.0, (math.cos(self.th_lo * D2R) - A) / Rr))))
        th5 = (min(self.a1 + self.a2, 360 - self.a1 - self.a2) - m) if ODesign.SLOT55 else self.th_hi   # bound: slot end at the 5.5 rule; cell B: the real stop
        rhi = math.degrees(math.acos(max(-1.0, min(1.0, (math.cos(th5 * D2R) - A) / Rr))))
        ok = (g2 > 0) & (m3e >= m - 1e-6) & (np.asarray(dKabs) <= self.dKB() + 1e-6) & (rel >= rlo - 0.05) & (rel <= rhi + 0.05)
        ok &= bool(self.k_ok) & bool(self.stops_ok)
        return dict(q=np.stack([q1, q2, q3], 1), ok=ok, R1=R1, R1b=R1 @ RK, R12=R12, R123=R123, t3=t3, s=s, dK=dK, a1e=a1e, m3e=m3e, rel=rel, th=th)

    def j3stop(self, Q, q, ok):
        """CELL B (opt-in param q3max, deg, the MODEL's own J3 angle: S.sub1 about u3 from vref = unit(u3 x (0.3, 0.5, 0.8))): a dowel
        stop at q3max on J3's own angle. Where the slaved state's q3 > q3max, K opens along the free self-motion until q3 = q3max
        (first crossing on [current |dK|, stop B], 0.5-deg scan + linear refine); no crossing -> refused (the arm is stopped)."""
        q3max = self.p.get("q3max")
        if q3max is None or not len(Q): return {}
        q3 = np.degrees(PK.wrap(q[:, 2])); sel = np.nonzero(ok & (q3 > float(q3max)))[0]
        if not len(sel): return {}
        dkb = self.dKB(); grid = np.arange(0.0, dkb + 1e-9, 0.5); out = {}
        for i in sel:
            d0 = abs(float(np.degrees(self._dK[i]))); g = grid[grid >= d0 - 1e-9]
            f = self.free_solve(np.repeat(Q[i][None], len(g), 0), g); qq = np.degrees(PK.wrap(f["q"][:, 2]))
            hit = np.nonzero(f["ok"] & (qq <= float(q3max)))[0]
            if not len(hit): out[int(i)] = None; continue
            k = int(hit[0])
            if k > 0 and f["ok"][k - 1]:
                a, b = qq[k - 1], qq[k]; t = (a - float(q3max)) / max(a - b, 1e-9); out[int(i)] = float(g[k - 1] + t * (g[k] - g[k - 1]))
            else: out[int(i)] = float(g[k])
        return out

    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = super()._ik_phys(Q)
        tab_ = {}
        if ODesign.TAB and len(Q):
            ks = qkeys(Q); tab_ = {i: ODesign.TAB[k] for i, k in enumerate(ks) if k in ODesign.TAB}
        js = self.j3stop(Q, q, ok); refuse = [i for i, v in js.items() if v is None]
        tab_.update({i: v for i, v in js.items() if v is not None})
        if refuse: ok = ok.copy(); ok[refuse] = False
        if not tab_: return q, ok, X1, X2, X3, s
        idx = np.array(sorted(tab_), int)
        f = self.free_solve(Q[idx], np.array([tab_[i] for i in idx]))
        q = q.copy(); ok = ok.copy(); s = s.copy()
        R1m, Z0 = X1; R1m = R1m.copy(); R2m = X2[0].copy(); R3m, t3m = X3[0].copy(), X3[1].copy(); X1b = self._X1b[0].copy()
        q[idx] = f["q"]; ok[idx] = f["ok"]; R1m[idx] = f["R1"]; R2m[idx] = f["R12"]; R3m[idx] = f["R123"]; t3m[idx] = f["t3"]; s[idx] = f["s"]
        X1b[idx] = f["R1b"]
        self._dK = self._dK.copy(); self._dK[idx] = f["dK"]; self._state = self._state.copy(); self._state[idx] = 2
        self._a1e = self._a1e.copy(); self._a1e[idx] = f["a1e"]; self._msub = np.asarray(self._msub, float).copy(); self._msub[idx] = 99.0
        self._m3e = self._m3e.copy(); self._m3e[idx] = f["m3e"]
        self._X1b = (X1b, self._X1b[1])
        return q, ok, (R1m, Z0), (R2m, X2[1]), (R3m, t3m), s


KB.KDesign = ODesign
KModel = KR.KModel


def params(over=None):
    """the VERIFIED priced params of a skinnormal-shortk seed (k33 default; seed = k8 / k20 / k56 / skinnormal_r / stopb80 /
    earlystop) + overrides (route rA / rsp / rsr; cap = the oracle's saturation, not a design parameter)"""
    over = dict(over or {}); seed = over.pop("seed", "k33"); over.pop("cap", None)
    f = K33.replace("c_k33_", f"c_{seed}_")
    P = dict(KR.PARAMS, **{k: v for k, v in json.load(open(f)).items() if not k.startswith("_")})
    P.update(over); P["_seed"] = seed; return P


def evaluate(B, over):
    """hook: oracle bound on B (fit = wear = B); report gap = the oracle's NEAR-TOUCH gap (metal < 1 mm = contact)"""
    global CAP
    cap0 = CAP; CAP = float(over.get("cap", CAP))
    try: r = run_oracle(B, B, params(over))
    finally: CAP = cap0
    o = r["oracle"]
    rep = dict(gap=o["near"], plain=o["gap"], reach=o["reach"], follow=o["follow"], inband14=o["inband14"], inband10=o["inband10"], contact=o["contact"],
               ws_taken=o["ws_taken"], near1_poses=o["near1_poses"], min_mm=o["min_mm"], moved=o["moved"], why=o["why"],
               kit=dict(gap=r["kit"]["near"], plain=r["kit"]["gap"], reach=r["kit"]["reach"], inband14=r["kit"]["inband14"], contact=r["kit"]["contact"]))
    return dict(over), rep


def metal(M):
    """every metal sample of the members K moves (1 link 1a + hub K, 7 link 1b + hub 2, 2 link 2), in member frames"""
    out = {1: [], 7: [], 2: []}
    for mem, lst in RM.member_points(M).items():
        if mem in out: out[mem] += [np.asarray(p, float) for _, p in lst]
    for c in getattr(M, "contact", []):
        if int(c[0]) in out and np.ndim(c[1]) == 2 and len(c[1]): out[int(c[0])].append(np.asarray(c[1], float))
    return {k: np.concatenate(v) for k, v in out.items() if v}


def scan(M, B, ns=NS):
    """per stretched pose of bench B: the free-K samples, their legality and exact min skin distance (members 1, 7, 2)"""
    D = M.D; ODesign.TAB = None
    q, ok, X1, X2, X3, s = D.ik(M.Q); st = D._state.copy(); dk_kit = np.degrees(np.abs(D._dK)); okk = ok.copy()
    w = M.Q @ D.u[2]; th = np.degrees(np.arccos(np.clip(w @ D.u[0], -1, 1)))
    cand = np.nonzero(st == 1)[0]; fl = D.floor(th[cand]); dkb = D.dKB(); mt = metal(M); res = {}
    for j, i in enumerate(cand):
        samp = np.unique(np.r_[np.linspace(min(fl[j], dkb), dkb, ns), dk_kit[i] if okk[i] else []].round(3))
        f = D.free_solve(np.repeat(M.Q[i][None], len(samp), 0), samp); rows = []
        okk_ = np.nonzero(f["ok"])[0]; dd = {}
        if len(okk_):                                        # ONE batched distance call per pose (the exact path builds its tree per call)
            names = list(mt); sizes = [len(mt[mm]) for mm in names]
            X = {1: f["R1"][okk_], 7: f["R1b"][okk_], 2: f["R12"][okk_]}
            Pw = np.concatenate([np.einsum("kj,sij->ski", mt[mm], X[mm]) for mm in names], 1) @ M.RS[i].T
            dist = B.dist(i, Pw); cut = np.cumsum([0] + sizes)
            for a, k in enumerate(okk_): dd[k] = {mm: float(dist[a, cut[b]:cut[b + 1]].min()) for b, mm in enumerate(names)}
        for k, dk in enumerate(samp):
            if k not in dd: rows.append((float(dk), False, None, None)); continue
            rows.append((float(dk), True, min(dd[k].values()), dd[k]))
        res[int(i)] = dict(th=float(th[i]), kit=float(dk_kit[i]) if okk[i] else None, floor=float(fl[j]), dKB=dkb, rows=rows)
    return res


def pick(res, cap=None):
    cap = CAP if cap is None else cap; tab = {}
    for i, r in res.items():
        good = [(min(d, cap), -abs(dk - (r["kit"] if r["kit"] is not None else r["floor"])), dk) for dk, ok, d, _ in r["rows"] if ok]
        if good: tab[i] = max(good)[2]
    return tab


KIN_REFUSED = ("fold", "slide", "flip", "closure", "parts")


def _rec(M, B, i):
    """one pose's outcome in a model run: (score, taken, dmin, why)"""
    r = B.res[i]
    if r is None: return (-50.0, False, None, str(M.why[i]))
    d = min(float(np.min(r)), float(getattr(M, "cmin", {}).get(i, 1e9)))
    if d < 0: return (-100.0 + d, False, d, "contact")
    return (min(d, CAP), True, d, "")


def pick_rows(rows, ref):
    """the oracle's pick for one pose from [(dK, taken, dmin, why)] (row 0 = the kit): ONLY configurations the mechanism can
    physically be in compete (not refused for fold / slide / flip / closure / a part jam): a refused K is not a place the
    mechanism can park to dodge a contact (2026-10-18 red team: the first rule let 5 contact poses 'escape' to a refused floor
    sample and read as lost poses instead of contacts - 15.27 was optimistic). Taken-and-clear beats contact; among taken,
    the larger min(distance, CAP); ties -> nearest the kit's K. No legal row -> the kit's state stands."""
    def sc(x):
        if x[1]: return min(x[2], CAP)
        if x[3] == "contact": return -100.0 + x[2]
        return None
    legal = [x for x in rows if x[0] is not None and x[3] not in KIN_REFUSED and sc(x) is not None]
    if not legal: return None
    best = max(legal, key=lambda x: (round(sc(x), 3), -abs(x[0] - ref)))
    return None if best is rows[0] else best[0]


def sub_bench(B, sub):
    """a fresh exact bench holding only the poses `sub` of B (same poses; per-pose caches empty)"""
    W = CB.Bench(n_clip=110, n_ws=360); assert list(np.asarray(W.idx)) == list(np.asarray(B.idx)), "sub_bench expects Bench(110,360)"
    sub = list(map(int, sub)); W.idx = np.asarray(W.idx)[sub]; W.kind = [W.kind[i] for i in sub]; W.poses = [W.poses[i] for i in sub]
    W.res = [None] * len(sub); return W


def oracle_runs(Mk, B, ns=9, sub=True):
    """the FAITHFUL oracle: ns composed runs of the frozen model, each with every stretched pose at the same fraction of its
    legal K range [floor, stop B]; per pose the best of {kit, ns samples} by _rec (taken and clear > lost > contact; ties ->
    nearest the kit's K). Every check of the model (knee window, slide residual, member 3 / knee moving with K, part pairs,
    clip continuity incl. the dK jump rule) is applied in every sample run."""
    D = Mk.D; ODesign.TAB = None
    q, ok, *_ = D.ik(Mk.Q); st = D._state.copy(); dk_kit = np.degrees(np.abs(D._dK)); okk = ok.copy()
    w = Mk.Q @ D.u[2]; th = np.degrees(np.arccos(np.clip(w @ D.u[0], -1, 1)))
    cand = np.nonzero(st == 1)[0]; fl = np.minimum(D.floor(th[cand]), D.dKB()); dkb = D.dKB(); keys = qkeys(Mk.Q)
    recs = {int(i): [(float(dk_kit[i]) if okk[i] else None, _rec(Mk, B, i))] for i in cand}
    Bs = sub_bench(B, cand) if (sub and B.mode != "fast") else B; loc = (lambda k, i: k) if Bs is not B else (lambda k, i: i)
    for j in range(ns):
        fr = j / max(ns - 1, 1); dks = fl + fr * (dkb - fl)
        ODesign.TAB = {keys[i]: float(dks[k]) for k, i in enumerate(cand)}
        Mj = type(Mk)(Bs, dict(Mk.p)); Mj.run()
        for k, i in enumerate(cand): recs[int(i)].append((float(dks[k]), _rec(Mj, Bs, loc(k, i))))
        print(f"  oracle sample {j + 1}/{ns} done", flush=True)
    ODesign.TAB = None; tab = {}
    for i, rr in recs.items():
        rows = [(x[0], x[1][1], x[1][2], x[1][3]) for x in rr]
        ref = rows[0][0] if rows[0][0] is not None else float(fl[list(cand).index(i)])
        pk = pick_rows(rows, ref)
        if pk is not None: tab[i] = pk
    res = {i: dict(th=float(th[i]), kit=rr[0][0], floor=float(fl[list(cand).index(i)]), dKB=dkb,
                   rows=[(x[0], x[1][1], x[1][2], x[1][3]) for x in rr]) for i, rr in recs.items()}
    return res, tab


def run_oracle(fitB, B, P, frozen=True, how="runs", pre=None):
    """fit (kit K) on fitB, oracle on B with that shape, composed run; returns the reports"""
    t0 = time.time(); ODesign.TAB = None; P = dict(P); seed = P.pop("_seed", "k33")
    Mk, fitr, M1, keys = RM.freeze(fitB, B, dict(P), KModel)          # frozen shape on B (fitB itself for the fast sweep)
    if pre is not None:                                       # compose only: re-pick from saved per-pose sample records (same frozen shape)
        kit = dict(pre.get("kit", {})); ntk = dict(gap_near1=kit.get("near")); whyk = kit.get("why"); tk_kit = []
        res = {int(i): v for i, v in pre["res"].items()}; tab = {}
        for i, r_ in res.items():
            rows = [tuple(x) for x in r_["rows"]]; pk = pick_rows(rows, rows[0][0] if rows[0][0] is not None else r_["floor"])
            if pk is not None: tab[i] = pk
    else:
        rk = Mk.run(); kit = {k: rk[k] for k in KEYS}; ntk = RM.near_touch(Mk, B); whyk = {k: int((Mk.why == k).sum()) for k in set(Mk.why.tolist()) if k}
        tk_kit = [i for i in RM.taken_list(B)]
    if pre is not None: pass
    elif how == "runs": res, tab = oracle_runs(Mk, B, ns=NSR if B.mode != "fast" else 9)
    else: res = scan(Mk, B); tab = pick(res)
    ODesign.TAB = {qkeys(Mk.Q[[i]])[0]: v for i, v in tab.items()}
    Mo = type(Mk)(B, dict(Mk.p)); ro = Mo.run(); orc = {k: ro[k] for k in KEYS}; nto = RM.near_touch(Mo, B)
    whyo = {k: int((Mo.why == k).sum()) for k in set(Mo.why.tolist()) if k}
    tk = RM.taken_list(B); ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
    low = {i: min(float(np.min(B.res[i])), float(getattr(Mo, "cmin", {}).get(i, 1e9))) for i in tk}
    # CONNECTED bound: a taken ws pose counts only if (a) its grid node is in the seed's kinematic flood-fill set (the verifier's
    # conn json; the route changes no kinematics) and (b) when the oracle moved K, every sampled K between the kit's and the
    # pick is kinematically legal at that pose (K can be swept there without a fold / slide / closure / flip refusal)
    conn = None; cf = K33.replace("_params.json", "_conn.json").replace("c_k33_", "c_" + str(seed) + "_")
    if os.path.exists(cf) and how == "runs":
        ck = {tuple(x) for x in json.load(open(cf))["connected_keys"]}; kin_bad = ("fold", "slide", "flip", "closure")
        res0 = list(B.res); drop = []
        for i in tk:
            if B.kind[i] != "ws": continue
            key = (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"]))
            ok_c = key in ck
            if ok_c and i in tab:
                lo, hi = sorted([res[i]["kit"] if res[i]["kit"] is not None else res[i]["floor"], tab[i]])
                ok_c = all(w_ not in kin_bad for dk, tk_, dm, w_ in res[i]["rows"][1:] if dk is not None and lo - 1e-6 <= dk <= hi + 1e-6)
            if not ok_c: drop.append(i)
        for i in drop: B.res[i] = None
        rc = B.report(); ntc = RM.near_touch(Mo, B); B.res = res0
        conn = dict(file=os.path.relpath(cf, REPO), dropped=len(drop), **{k: rc[k] for k in KEYS}, near=ntc["gap_near1"],
                    ws_taken=sum(1 for i in tk if B.kind[i] == "ws") - len(drop))
    ODesign.TAB = None
    if pre is None: kit = dict(**kit, near=ntk["gap_near1"], ws_taken=sum(1 for i in tk_kit if B.kind[i] == "ws"), why=whyk)
    return dict(conn=conn, fit=fitr, kit=kit,
                oracle=dict(**orc, near=nto["gap_near1"], near1_poses=nto["near1_poses"], min_mm=nto["min_mm"], ws_taken=sum(1 for i in tk if B.kind[i] == "ws"),
                            clear02=sum(1 for i in tk if low[i] >= 0.2), clear1=sum(1 for i in tk if low[i] >= 1.0), why=whyo,
                            moved=len(tab), state_free_taken=int(sum(1 for i in tk if Mo.kstate[i] == 2))),
                res=res, tab=tab, low=low, M=Mo, Mk=Mk, secs=round(time.time() - t0, 1))


def side(P=None):
    """which side of link 2's great circle is +bn (rA > 0): bn . (x anterior, y up) at rest"""
    B = RM.PV.fast_bench(20, 40); M = KModel(B, dict(params(P))); M.run()
    L2 = [l for l in M.geo.links if l["name"] == "L2"][0]; d = M.geo.links
    U = [M.D.u[0], M.D.uK, M.D.u[1], M.D.u[2]]; bn = unit(np.cross(unit(M.D.c[1] + M.f[1] * U[2]), unit(M.D.c[2] + M.f[2] * U[3])))
    return dict(bn_scap=[round(float(x), 3) for x in bn])


if __name__ == "__main__":
    mode = sys.argv[1]; over = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}; outp = sys.argv[3] if len(sys.argv) > 3 else None
    if mode == "side": print(side(over)); sys.exit()
    if mode == "law":                                        # cell B (q3max) or the kit: fit fast -> frozen on Bench(60,160) fast or Bench(110,360) exact, no oracle
        P = params(over); P.pop("_seed", None); fitB = RM.PV.fast_bench(60, 160); ex = len(sys.argv) > 4 and sys.argv[4] == "exact"
        ODesign.SLOT55 = False                               # a real mechanism: J2 keeps its own priced slot in every state
        hd = len(sys.argv) > 4 and sys.argv[4] == "held"; ex = ex or hd
        B = (RM.PV.held_bench() if hd else CB.Bench(n_clip=110, n_ws=360)) if ex else fitB; ODesign.TAB = None
        Mk, fitr, M1, _ = RM.freeze(fitB, B, dict(P), KModel); rk = Mk.run(); nt = RM.near_touch(Mk, B); tk = RM.taken_list(B)
        out = dict(id=ID, mode="law", bench=B.mode, over=over, **{k: rk[k] for k in KEYS}, near=nt["gap_near1"], near1_poses=nt["near1_poses"], min_mm=nt["min_mm"],
                   ws_taken=sum(1 for i in tk if B.kind[i] == "ws"), why={k: int((Mk.why == k).sum()) for k in set(Mk.why.tolist()) if k},
                   j3stop_engaged_taken=int(sum(1 for i in tk if Mk.kstate[i] == 2)),
                   binders={j: (round(min(float(np.min(B.res[j])), float(Mk.cmin.get(j, 1e9))), 2) if B.res[j] is not None else str(Mk.why[j])) for j in BINDERS if ex})
        if ex:                                               # continuity: the remeasure harness's kinematic flood fill, run on THIS design (law incl.)
            t1 = time.time(); Z, Wg, POSE, HG = RM.ws_grid(); D = Mk.D; R_tol = float(Mk.p["R_tol"]); _ = D.ik(HG[:2])
            okn, qq, sgn, st, own = RM.kin_nodes(D, HG, R_tol); seeds = okn & (POSE[:, 1] == 0) & (st == 0)
            cn, stats = RM.flood(POSE, HG, okn, seeds, D, R_tol)
            ck = {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}
            res0 = list(B.res); drop = [i for i in tk if B.kind[i] == "ws" and (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])) not in ck]
            for i in drop: B.res[i] = None
            rc = B.report(); ntc = RM.near_touch(Mk, B); B.res = res0
            out["connected"] = dict(nodes=int(okn.sum()), seeds=int(seeds.sum()), connected=int(cn.sum()), islands=int((okn & ~cn).sum()), dropped=len(drop),
                                    **{k: rc[k] for k in KEYS}, near=ntc["gap_near1"], ws_taken=out["ws_taken"] - len(drop), edges=stats, secs=round(time.time() - t1, 1))
            el = np.array([p_["elev"] for p_ in B.poses]); out["overhead140_ws"] = dict(ws=int(sum(1 for i in range(len(el)) if el[i] >= 140 and B.kind[i] == "ws")),
                                                                                    taken=int(sum(1 for i in tk if el[i] >= 140 and B.kind[i] == "ws" and i not in drop)))
        if outp: json.dump(out, open(outp, "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode == "viz":                                        # geometry export for docs/concepts/viz/concepts/<id>.js (SK's exporter on this model's fit)
        def _rep(B, pr):
            ODesign.TAB = None; pp = params(pr); pp.pop("_seed", None); M = KModel(B, pp); r = M.run(); return dict(r), M
        SK._report = _rep
        print(json.dumps(SK.viz_export(over), default=float)); sys.exit()
    if mode == "sweep":                                      # configs: a JSON list in argv[2]; appends to the sweep file incrementally
        cfgs = json.loads(sys.argv[2]); sw = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json"); fitB = RM.PV.fast_bench(60, 160)
        for c in cfgs:
            t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            try: pp, rep = evaluate(fitB, c)
            except Exception as e: pp, rep = c, dict(gap=275.0, error=repr(e)[:200])
            rows = json.load(open(sw)) if os.path.exists(sw) else []
            rows.append(dict(k=len(rows), t=t, params=pp, bench="Bench(60,160) fast, oracle K (bound)", **{kk: rep.get(kk) for kk in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                             extra={kk: v for kk, v in rep.items() if kk not in ("inband14", "inband10", "reach", "follow", "contact", "gap")}))
            json.dump(rows, open(sw + ".tmp", "w"), indent=1, default=float); os.replace(sw + ".tmp", sw)
            print(json.dumps(dict(k=len(rows) - 1, params=pp, gap=rep.get("gap"), plain=rep.get("plain"), reach=rep.get("reach"), ib14=rep.get("inband14"), contact=rep.get("contact"), kit=rep.get("kit"))), flush=True)
        sys.exit()
    P = params(over); CAP = float(over.get("cap", CAP))
    fitB = RM.PV.fast_bench(60, 160)
    B = fitB if mode == "fast" else CB.Bench(n_clip=110, n_ws=360)
    pre = None
    if os.environ.get("FO_PRE"):                             # compose mode: FO_PRE=<saved OUT.json> (its _perpose.json holds the sample records)
        pre = json.load(open(os.environ["FO_PRE"].replace(".json", "_perpose.json"))); pre["kit"] = json.load(open(os.environ["FO_PRE"]))["kit"]
    r = run_oracle(fitB, B, P, how=os.environ.get("FO_HOW", "runs"), pre=pre)
    o = r["oracle"]; k = r["kit"]
    bind = {}
    if mode == "wear":
        for j in BINDERS:
            if j in r["res"]:
                rr = r["res"][j]; ch = r["tab"].get(j)
                bind[j] = dict(pose={kk: B.poses[j][kk] for kk in ("plane", "elev", "axial")}, th=round(rr["th"], 1), kit_dK=rr["kit"], pick_dK=ch,
                               samples=[(None if x[0] is None else round(x[0], 1), x[1], None if x[2] is None else round(x[2], 2), x[3]) for x in rr["rows"]],
                               final_min=round(r["low"][j], 2) if j in r["low"] else None)
    out = dict(id=ID, mode=mode, bench=B.mode, fit_mode=fitB.mode, over=over, fold_margin=KIT.FOLD_MARGIN, fit=r["fit"], kit=k,
               oracle={kk: v for kk, v in o.items()}, connected=r["conn"], binders=bind, secs=r["secs"],
               score_oracle=round(100 * (1 - o["gap"] / 275), 2), score_oracle_near=round(100 * (1 - o["near"] / 275), 2))
    if outp:
        json.dump(out, open(outp, "w"), indent=1, default=float)
        json.dump(dict(res={str(i): v for i, v in r["res"].items()}, tab={str(i): v for i, v in r["tab"].items()}, low={str(i): v for i, v in r["low"].items()}),
                  open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    print(json.dumps({kk: out[kk] for kk in ("mode", "bench", "kit", "oracle", "connected", "score_oracle", "score_oracle_near", "secs")}, default=float), flush=True)
