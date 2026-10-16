"""Concept model: COUPLER-PATH J1 (id coupler-path-j1). J1 of the 3R is replaced by a spherical four-bar grounded on the
scapula base: crank A0 -> A1 (ACTIVE at A0), rocker B0 -> B1 (passive), coupler = link 1 (passive pins A1, B1), all axes
through GH. Link 1 carries J2's axis p2 at a coupler point, so J2 runs along a COUPLER CURVE instead of the circle
angle(u1, p2) = a1: the effective a1 varies with the crank (a fold lever with no spring, no stop, no sensor).

Stage 1 (this file, `kin`): IK only on Bench(110,360)'s orientation data, no skin. For each pose the J3 axis p3 (scapula
frame, = Q @ u3) must meet the coupler curve at angle a2: roots of g(t) = angle(p2(t), p3) - a2 over the crank angle t.
  * a root is CONDITIONED iff the coupler curve crosses the circle C(p3, a2) at >= X deg (the chain is singular exactly
    when the curve is tangent to the circle: then the pole of link 1, p2 and p3 are coplanar). X is CALIBRATED on the
    leader's own circle (kr = 0, A0 = u1, alpha = a1): the X at which the circle reproduces the kit's m = 10 / m = 5 count.
  * the four-bar must assemble and keep its transmission angle (coupler-rocker, at B1) in [25, 155] deg at the root;
  * branch: the sign of d(p2.p3)/dt at the root (the 3R's sigma); one sign for the whole design (searched);
  * clips: the root is tracked frame to frame along the crank (no jump > 25 deg of t, no pass through an invalid t).
Coverage = share of the 360 workspace poses with a conditioned root (the kinematic reach ceiling), + clip follow.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/coupler-path-j1.py kin [n_random]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("CB_QUIET_EXACT", "1")
ID = "coupler-path-j1"
NAME = "Four-bar base: J2 carried along a spherical coupler curve (fold lever, 0 passive translations)"
D2R = math.pi / 180
NT = 720                                        # crank grid (0.5 deg)
TGRID = np.arange(NT) * (360.0 / NT)


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def tangent_basis(u):
    """two unit tangents at u (a fixed rule: e1 toward +y-ish 'up' projected, e2 = u x e1)"""
    u = unit(u); ref = np.array([0.0, 1.0, 0.0]) if abs(u[1]) < 0.95 else np.array([1.0, 0.0, 0.0])
    e1 = unit(ref - (ref @ u) * u); e2 = np.cross(u, e1); return e1, e2


def expmap(u, d, psi):
    """the point at arc d (deg) from u in tangent direction psi (deg, 0 = e1 'up')"""
    e1, e2 = tangent_basis(u); d, psi = d * D2R, psi * D2R
    return math.cos(d) * unit(u) + math.sin(d) * (math.cos(psi) * e1 + math.sin(psi) * e2)


def rot(axis, ang):
    """(n,3,3) rotations about unit axis by ang (rad, (n,))"""
    a = unit(axis); Kx = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    ang = np.asarray(ang, float)[:, None, None]
    return np.eye(3)[None] + np.sin(ang) * Kx[None] + (1 - np.cos(ang)) * (Kx @ Kx)[None]


def two_circle(b, w, a1, a2, sigma):
    """the point at arc a1 from b and a2 from w (deg), branch sigma (sign of p.(b x w)); b (3,), w (n,3)"""
    b = unit(b); w = unit(w); c = np.clip(w @ b, -1, 1); n = np.cross(b[None], w); nn = np.linalg.norm(n, axis=-1, keepdims=True)
    n = n / np.maximum(nn, 1e-12); A1, A2 = a1 * D2R, a2 * D2R
    den = 1 - c ** 2 + 1e-12; A = (math.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * math.cos(A1)) / den
    p0 = A[:, None] * b[None] + Bq[:, None] * w; h2 = 1 - (p0 * p0).sum(-1)
    return p0 + sigma * np.sqrt(np.clip(h2, 0, None))[:, None] * n, h2 > 0


def largest_arc(v):
    """keep the largest cyclic run of True (a crank cannot jump across an invalid angle)"""
    v = np.asarray(v, bool)
    if v.all() or not v.any(): return v
    k = int(np.argmin(v)); r = np.roll(v, -k); best = (0, 0); i = 0; n = len(r)
    while i < n:
        if r[i]:
            j = i
            while j < n and r[j]: j += 1
            if j - i > best[1] - best[0]: best = (i, j)
            i = j
        else: i += 1
    out = np.zeros(n, bool); out[best[0]:best[1]] = True; return np.roll(out, k)


def fourbar(p, t_deg=TGRID):
    """spherical four-bar in the scapula frame. p: u1 (3,) reference seat, dA, psiA (A0 rel. u1), alpha (crank arc),
    dAB, psiB (B0 rel. A0), beta (rocker arc), c (coupler arc), s4 (assembly branch), kr, kg (coupler point: arc from
    A1, angle from the A1 -> B1 direction). Returns dict of (NT,3) arrays + valid mask + transmission angle mu."""
    u1 = unit(np.asarray(p["u1"], float))
    A0 = expmap(u1, p["dA"], p["psiA"]); A1_0 = expmap(A0, p["alpha"], 0.0)
    A1 = rot(A0, np.radians(t_deg)) @ A1_0
    B0 = expmap(A0, p["dAB"], p["psiB"])
    B1, ok = two_circle(B0, A1, p["beta"], p["c"], p["s4"])
    e2 = unit(B1 - (B1 * A1).sum(-1, keepdims=True) * A1); e3 = np.cross(A1, e2)
    kr, kg = p["kr"] * D2R, p["kg"] * D2R
    p2 = math.cos(kr) * A1 + math.sin(kr) * (math.cos(kg) * e2 + math.sin(kg) * e3)
    # transmission angle at B1: between arcs B1->A1 and B1->B0 (tangent directions at B1)
    ta = unit(A1 - (A1 * B1).sum(-1, keepdims=True) * B1); tb = unit(B0[None] - (B1 @ B0)[:, None] * B1)
    mu = np.degrees(np.arccos(np.clip((ta * tb).sum(-1), -1, 1)))
    if p.get("ideal"): ok = np.ones(len(t_deg), bool)          # calibration only: the bare circle about A0 (no B side)
    valid = ok & (mu >= p.get("mu_min", 25.0)) & (mu <= 180 - p.get("mu_min", 25.0))
    valid = largest_arc(valid)                                   # the crank can only move inside one connected range
    return dict(A0=A0, B0=B0, A1=A1, B1=B1, p2=unit(p2), mu=mu, valid=valid, ok=ok)


def curve_roots(fb, P3, a2, X, branch, t_grid=None, m=None):
    """all roots of angle(p2(t), p3) = a2 on the cyclic crank grid, vectorised. Returns dict of flat arrays: j (pose),
    t (deg), cross (deg, curve vs circle C(p3, a2) crossing angle), sg (sign of d(p2.p3)/dt), good (valid four-bar,
    cross >= X, sg == branch), q (the p2 axis at the root). P3 (N,3) scapula frame."""
    p2 = fb["p2"]; V = fb["valid"]; ok = fb["ok"]; n = len(p2); tg = TGRID if t_grid is None else t_grid
    dp = np.roll(p2, -1, 0) - np.roll(p2, 1, 0)
    g = np.degrees(np.arccos(np.clip(p2 @ P3.T, -1, 1))) - a2                  # (NT, N)
    gn = np.roll(g, -1, 0); okp = ok & np.roll(ok, -1)
    i, j = np.nonzero(((np.sign(g) != np.sign(gn)) | (g == 0)) & okp[:, None])
    i2 = (i + 1) % n; den = g[i, j] - gn[i, j]
    f = np.where(den != 0, g[i, j] / np.where(den != 0, den, 1), 0.0)
    t = (tg[i] + f * (360.0 / n)) % 360
    q = unit((1 - f)[:, None] * p2[i] + f[:, None] * p2[i2]); tan = (1 - f)[:, None] * dp[i] + f[:, None] * dp[i2]
    tan = unit(tan - (tan * q).sum(-1, keepdims=True) * q)
    p3 = P3[j]; rc = unit(p3 - (p3 * q).sum(-1, keepdims=True) * q)
    cross = np.degrees(np.arcsin(np.clip(np.abs((tan * rc).sum(-1)), 0, 1)))
    sg = np.where((tan * p3).sum(-1) > 0, 1, -1)
    # osculating-circle fold rule (m given): the kit's 3R rule th in [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m] with
    # u1 -> the centre n of the curve's osculating circle at the root and a1 -> its radius rho (exact for a circle)
    ddp = np.roll(p2, -1, 0) - 2 * p2 + np.roll(p2, 1, 0)
    nv = (1 - f)[:, None] * np.cross(dp[i], ddp[i]) + f[:, None] * np.cross(dp[i2], ddp[i2])
    nv = unit(nv); nv = np.where(((nv * q).sum(-1) < 0)[:, None], -nv, nv)
    rho = np.degrees(np.arccos(np.clip((nv * q).sum(-1), -1, 1))); the = np.degrees(np.arccos(np.clip((nv * p3).sum(-1), -1, 1)))
    marg = np.minimum.reduce([the - np.abs(rho - a2), rho + a2 - the, 360 - rho - a2 - the])
    cond = (marg >= m) if m is not None else (cross >= X)
    good = V[i] & V[i2] & cond & (sg == branch)
    return dict(j=j, t=t, cross=cross, sg=sg, good=good, q=q, i=i, marg=marg, rho=rho)


def coverage(fb, P3, a2, X, branch, mask):
    R = curve_roots(fb, P3, a2, X, branch)
    good = np.zeros(len(P3), bool); np.logical_or.at(good, R["j"], R["good"])
    return float(good[mask].mean()), good, R


def calib_circle(u1, a1, sigma_branch):
    """the leader's circle as a degenerate coupler: A0 = u1, alpha = a1, kr = 0"""
    return dict(u1=u1, dA=0.0, psiA=0.0, alpha=a1, dAB=40.0, psiB=90.0, beta=40.0, c=40.0, s4=1, kr=0.0, kg=0.0, mu_min=0.0, ideal=1)


def leader():
    s = importlib.util.spec_from_file_location("pk_cp", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
    PK = importlib.util.module_from_spec(s); s.loader.exec_module(PK)
    P = json.load(open(os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee_big_frozen.json")))["params"]
    D = PK.Design(P); return np.array(D.u[0]), np.array(D.u[2]), math.degrees(D.A[0]), math.degrees(D.A[1])


def poses110():
    import concept_bench as CB
    B = CB.Bench(n_clip=110, n_ws=360); Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float)
    kind = np.array(B.kind); el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
    ws = kind == "ws"
    return B, Q, ws, ws & (el >= 140), ws & (pl >= 100) & (el >= 40)


# ---- stage 1 search: the kinematic ceiling of a coupler curve at the leader's J3 seat -------------------------------
SPACE = dict(dA=(0, 40), psiA=(0, 360), alpha=(10, 70), dAB=(10, 70), psiB=(0, 360), beta=(10, 85), c=(10, 85),
             kr=(0, 90), kg=(-180, 180))


def rand_cfg(rng):
    p = {k: float(rng.uniform(*v)) for k, v in SPACE.items()}
    p["s4"] = int(rng.choice([-1, 1])); p["branch"] = int(rng.choice([-1, 1])); return p


def kscore(p, u1, P3, a2, ws, ov, X=40.0):
    fb = fourbar(dict(p, u1=u1)); c, good, R = coverage(fb, P3, a2, X, p["branch"], ws)
    # J2 excursion: polar distance from u1 of the J2 axis at the best (max crossing) good root of each taken ws pose
    gj = R["good"] & ws[R["j"]]
    pol = np.degrees(np.arccos(np.clip(R["q"][gj] @ u1, -1, 1))) if gj.any() else np.zeros(1)
    crank = fb["valid"].mean()
    return dict(cov=round(c, 4), ov=round(float(good[ov].mean()), 4), pol95=round(float(np.percentile(pol, 95)), 1),
                pol5=round(float(np.percentile(pol, 5)), 1), crank_valid=round(float(crank), 3))


def pick_roots(R, n, prefer="cross"):
    """per pose the index (into R) of the good root with the largest crossing angle, -1 if none"""
    best = np.full(n, -1); bc = np.full(n, -1.0)
    for r in np.nonzero(R["good"])[0]:
        j = R["j"][r]
        if R["cross"][r] > bc[j]: bc[j] = R["cross"][r]; best[j] = r
    return best


class Skin60:
    """J2-hub skin proxy on Bench(60,160) (fast grid cache): the K3 march along the J2 axis in each taken pose"""
    def __init__(self):
        import concept_bench as CB, concept_kit as K
        self.K = K; self.B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all()
        self.Q = Z["HG"][self.B.idx].astype(float); self.RS = Z["RS"][self.B.idx].astype(float)
        self.ws = np.array(self.B.kind) == "ws"; self.clip = ~self.ws

    def j2(self, fb, u3, a2, X, branch):
        P3 = self.Q @ u3; R = curve_roots(fb, P3, a2, X, branch); bi = pick_roots(R, len(P3))
        tk = bi >= 0; I = np.nonzero(tk)[0]
        if not len(I): return dict(n=0, inband=0.0, h=None, spread=None)
        D = np.einsum("nij,nj->ni", self.RS[I], R["q"][bi[I]])
        r = self.K.requirement(self.B, I, D)
        fin = np.isfinite(r); h = float(r[fin].max()) if fin.any() else np.inf
        inb = float(((h - r) <= 12.0)[fin].mean()) if fin.any() else 0.0
        return dict(n=int(tk.sum()), reach60=round(float(tk[self.ws].mean()), 4), follow60=round(float(tk[self.clip].mean()), 4),
                    inband=round(inb, 4), h=round(h, 1), p10=round(float(np.percentile(r[fin], 10)), 1),
                    p50=round(float(np.percentile(r[fin], 50)), 1), clip_inband=round(float(((h - r) <= 12.0)[fin & self.clip[I]].mean()), 4) if (fin & self.clip[I]).any() else 0.0)


# ---- stage 1b: kinematics on Bench(110,360) + the J2-hub skin proxy on Bench(60,160) --------------------------------
KEYS = ["dA", "psiA", "alpha", "dAB", "psiB", "beta", "c", "kr", "kg", "a2"]
LO = np.array([0, -360, 8, 8, -360, 8, 8, 0, -360, 50.0]); HI = np.array([45, 720, 75, 75, 720, 88, 88, 90, 720, 100.0])


class Proxy:
    def __init__(self):
        self.B, self.Q, self.ws, self.ov, self.acr = poses110()
        self.clip = ~self.ws
        self.u1, self.u3, self.a1, self.a2 = leader(); self.P3 = self.Q @ self.u3; self.S = Skin60()

    def j2cost(self, fb, a2, X, branch):
        S = self.S; P3 = S.Q @ self.u3; R = curve_roots(fb, P3, a2, X, branch, m=MARGIN); bi = pick_roots(R, len(P3))
        I = np.nonzero(bi >= 0)[0]
        if len(I) < 20: return 300.0, {}
        D = np.einsum("nij,nj->ni", S.RS[I], R["q"][bi[I]]); r = S.K.requirement(S.B, I, D); r = np.where(np.isfinite(r), r, 300.0)
        rs = np.sort(r); n = len(rs); best = (1e9, None)
        for k in range(int(0.6 * n), n):                            # hub level h = rs[k]: poses above it are lost
            h = rs[k]; lost = (n - 1 - k) / n; inb = float(((h - r) <= 12.0).mean())
            cost = 100 * lost + 50 * max(0.0, 0.9 - inb)
            if cost < best[0]: best = (cost, dict(h=round(float(h), 1), lost=round(lost, 4), inb=round(inb, 4)))
        return best[0], best[1]

    def __call__(self, p, X=40.0):
        fb = fourbar(dict(p, u1=self.u1)); a2 = p.get("a2", self.a2)
        R = curve_roots(fb, self.P3, a2, X, p["branch"], m=MARGIN); good = np.zeros(len(self.P3), bool); np.logical_or.at(good, R["j"], R["good"])
        cov = float(good[self.ws].mean()); fol = float(good[self.clip].mean())
        jc, jd = (0.0, {}) if NOSKIN else self.j2cost(fb, a2, X, p["branch"])
        g = 100 * max(0, .9 - cov) + 100 * max(0, .95 - fol) + jc
        return g, dict(cov=round(cov, 4), ov=round(float(good[self.ov].mean()), 4), acr=round(float(good[self.acr].mean()), 4),
                       follow=round(fol, 4), j2=jd, crank_valid=round(float(fb["valid"].mean()), 3))


MARGIN = float(os.environ.get("CB_FOLD_MARGIN", 10.0))       # the proxy's fold margin (the bench's rule: m = 10 here)
NOSKIN = int(os.environ.get("CP_NOSKIN", 0))                  # 1: the pure kinematic ceiling (no J2 relief term)
KRMIN = float(os.environ.get("CP_KRMIN", 0.0))              # > 0: a genuine coupler (J2 off the crank)
CIRCLE = int(os.environ.get("CP_CIRCLE", 0))                 # 1: the control - J2 on a circle about a free A0 (re-seated J1)


def x2p(x, s4, branch):
    lo = LO.copy(); lo[7] = max(lo[7], KRMIN)
    x = np.clip(x, lo, HI); p = dict(zip(KEYS, map(float, x))); p["s4"] = s4; p["branch"] = branch
    if CIRCLE: p.update(kr=0.0, ideal=1, mu_min=0.0)
    p["psiA"] %= 360; p["psiB"] %= 360; p["kg"] = (p["kg"] + 180) % 360 - 180; return p


def kopt(seed, s4, branch, iters, out, x0=None, sig=0.25):
    import cma
    PX = Proxy(); rng = np.random.default_rng(seed)
    if x0 is None and seed >= 100:                                 # start ON the leader's circle (kr 0 = J2 on the crank)
        x0 = np.array([rng.uniform(0, 4), rng.uniform(0, 360), PX.a1, rng.uniform(15, 35), rng.uniform(0, 360),
                       rng.uniform(30, 50), rng.uniform(30, 50), rng.uniform(0, 8), rng.uniform(-180, 180), PX.a2])
    if x0 is None:
        x0 = np.array([rng.uniform(0, 30), rng.uniform(0, 360), rng.uniform(30, 60), rng.uniform(15, 50), rng.uniform(0, 360),
                       rng.uniform(20, 70), rng.uniform(20, 70), rng.uniform(KRMIN, max(KRMIN + 10, 60)), rng.uniform(-180, 180), PX.a2])
    scale = HI - LO; scale[[1, 4, 8]] = 360
    es = cma.CMAEvolutionStrategy(((np.asarray(x0) - LO) / scale).tolist(), sig, dict(seed=seed, popsize=14, verbose=-9, bounds=[None, None]))
    hist = []; best = (1e9, None, None)
    for it in range(iters):
        Xs = es.ask(); fs = []
        for z in Xs:
            p = x2p(LO + np.asarray(z) * scale, s4, branch); g, d = PX(p); fs.append(g); hist.append(dict(g=round(g, 2), p=p, **d))
            if g < best[0]: best = (g, p, d)
        es.tell(Xs, fs)
    json.dump(dict(best=dict(g=best[0], p=best[1], d=best[2]), hist=hist), open(out, "w"))
    return best


# ---- stage 2: the bench model - the pin-knee leader's VModel with link 1 moved by the four-bar --------------------------
# Every member, check and fit rule of docs/concepts/models/skin-normal-3r-pin-knee.py (closure, 10 fps continuity incl. the
# knee, jam rule, near-touch, part clearances) is kept; only link 1's motion changes: R1 (a rotation about the fixed J1
# axis u1) becomes the coupler's rotation Rc(t) = E(t) E(t_h)^T about GH, t = the crank angle at A0 (q1). J2's home axis
# u2 = p2(t_h) is the coupler point at the home crank t_h, the root of angle(p2(t), u3) = a2c at Q = I. kr = 0 puts J2 ON
# the crank (a circle about A0: a re-seated plain 3R - the control). BOUND: stage 2a carries the leader's hub 1 at u1
# (standing in for the base hubs A0 / B0, which sit dA from it) and link 1 as the leader's strap from u1 to J2 moved with
# the coupler; the crank, the rocker and the pins B0 / A1 / B1 are NOT yet metal - an optimistic bound on contact and
# part clearance, roughly neutral on in-band (they ride the scapula base).
_PK = None


def _pk():
    global _PK
    if _PK is None:
        sp = importlib.util.spec_from_file_location("pk_for_coupler", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
        PK = importlib.util.module_from_spec(sp); sp.loader.exec_module(PK)
        LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee_big_frozen.json")))["params"]
        S = PK.S

        class CPDesign(PK.Design):
            def __init__(self, params=None):
                P = dict(PK.PARAMS); P.update(LEAD); P.update(dict(FB_DEFAULT)); P.update(params or {})
                if float(P["kr"]) < 0: P["kr"] = -float(P["kr"]); P["kg"] = float(P["kg"]) + 180.0     # same coupler point
                super().__init__(P); P = self.p
                self.fbp = {k: float(P[k]) for k in ("dA", "psiA", "alpha", "dAB", "psiB", "beta", "c", "kr", "kg")}
                self.fbp.update(s4=int(P["s4"]), u1=np.array(self.u[0]), mu_min=float(P.get("mu_min", 25.0)))
                if P.get("circle"): self.fbp.update(ideal=1, kr=0.0, mu_min=0.0)
                self.a2c = float(P["a2c"]); self.brc = int(P["branch"]); self.X = 25.0 + 3.0 * (S.SING - 5.0)
                self.fb = fourbar(self.fbp); self.A0 = self.fb["A0"]
                self.u[0] = unit(self.A0)                                       # hub 1 = the ACTIVE crank hub at A0 (on a GH ray)
                R = curve_roots(self.fb, np.array(self.u[2])[None], self.a2c, 0.0, self.brc)
                okh = R["sg"] == self.brc
                if not okh.any(): raise ValueError("coupler: no home root at Q = I")
                r = int(np.argmax(np.where(okh, R["cross"], -1)))
                self.t_h = float(self._refine(np.array([R["i"][r]]), np.array(self.u[2])[None])[0])
                fh = fourbar(self.fbp, np.array([self.t_h])); self.E_h = self._E(fh)[0]
                u2 = unit(fh["p2"][0]); self.u[1] = u2
                self.A = [math.acos(float(np.clip(u2 @ self.u[0], -1, 1))), math.acos(float(np.clip(u2 @ self.u[2], -1, 1)))]
                Q0 = PK.OSN.rest()["Q0"]
                self.c = [np.zeros(3), np.zeros(3), np.zeros(3)]
                _, _, X1, _, _, _ = self.ik(Q0[None]); R1, tt1 = X1[0][0], X1[1][0]
                self.c[1] = PK.OSN.foot(R1.T @ (self.seats["P"][1] * 0 - tt1), self.u[1])      # J2 on a GH ray (b2 = 0)
                _, _, _, X2, _, _ = self.ik(Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
                self.c[2] = PK.OSN.foot(R12.T @ (self.seats["P"][2] - tt2), self.u[2])
                self.rest_err = 0.0

            @staticmethod
            def _E(fb):
                A1 = fb["A1"]; e2 = unit(fb["B1"] - (fb["B1"] * A1).sum(-1, keepdims=True) * A1); e3 = np.cross(A1, e2)
                return np.stack([A1, e2, e3], -1)                              # (n,3,3) columns

            def _refine(self, i0, W, it=40):
                """bisection of g(t) = angle(p2(t), w) - a2c on the bracket [t_i, t_i + step] (cyclic grid)"""
                st = 360.0 / NT; lo = TGRID[i0 % NT].astype(float); hi = lo + st
                g = lambda t: np.degrees(np.arccos(np.clip((fourbar(self.fbp, t)["p2"] * W).sum(-1), -1, 1))) - self.a2c
                glo = g(lo)
                for _ in range(it):
                    mid = 0.5 * (lo + hi); gm = g(mid); same = np.sign(gm) == np.sign(glo)
                    lo = np.where(same, mid, lo); glo = np.where(same, gm, glo); hi = np.where(same, hi, mid)
                return 0.5 * (lo + hi)

            def ik(self, Q):
                if not hasattr(self, "E_h"): return super().ik(Q)
                u1, u2, u3 = self.u; n = len(Q); w = Q @ u3
                R = curve_roots(self.fb, w, self.a2c, self.X, self.brc, m=S.SING); bi = pick_roots(R, n); ok = bi >= 0
                t = np.full(n, self.t_h)
                if ok.any(): t[ok] = self._refine(R["i"][bi[ok]], w[ok])
                fb = fourbar(self.fbp, t)
                if self.fbp["kr"] == 0: Rc = S.rotm(self.A0, np.radians(t - self.t_h))   # J2 on the crank: link 1 IS the crank
                else: Rc = self._E(fb) @ self.E_h.T
                ok &= fb["ok"]
                q1 = (np.radians(t - self.t_h) + np.pi) % (2 * np.pi) - np.pi
                z = np.einsum("nji,nj->ni", Rc, w); q2 = S.sub1(u2, np.broadcast_to(u3, z.shape), z)
                R2 = S.rotm(u2, q2); R12 = Rc @ R2; v = unit(np.cross(u3, [0.3, 0.5, 0.8]))
                q3 = S.sub1(u3, np.broadcast_to(v, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, v)); R3 = S.rotm(u3, q3)
                c1, c2, c3 = self.c
                t1 = c1 - Rc @ c1; X1 = (Rc, t1)
                t2 = np.einsum("nij,nj->ni", Rc, c2[None] - R2 @ c2 - c1[None]) + c1; X2 = (R12, t2)
                t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3) + t2; X3 = (R12 @ R3, t3)
                sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
                self.last_t = t; self.last_mu = fb["mu"]
                return np.stack([q1, q2, q3], 1), ok, X1, X2, X3, s

        PK.Design = CPDesign
        _PK = PK
    return _PK


FB_DEFAULT = dict(dA=0.0, psiA=0.0, alpha=40.12, dAB=25.0, psiB=90.0, beta=40.0, c=40.0, kr=0.0, kg=0.0, s4=1,
                  a2c=72.31, branch=1, mu_min=25.0, circle=0)
PARAMS = dict(FB_DEFAULT)


def bench_eval(B, params):
    """tools/concept_sweep.py hook (the pin-knee report: gap, reach, ..., why, knee, f, seats)"""
    PK = _pk()
    try: r, M = PK._report(B, dict(params))
    except ValueError as e:
        B.reset(); r = B.report(); r["error"] = str(e); return r
    r.pop("params", None); r["passive_trans"] = 0; r["bound"] = "2a: crank/rocker/pins not yet metal"; return r


def evaluate(B, params):
    """tools/concept_cma.py hook: (params, report); the pin-knee's honest flag (jam rule + every VModel fix)"""
    PK = _pk(); r, M = PK._report(B, dict(params))
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    r["passive_trans"] = 0; r["t_span"] = round(float(np.ptp(M.D.last_t)), 1) if hasattr(M.D, "last_t") else None
    return p, r


def frozen(params, nc=110, nw=360):
    return _pk().frozen(dict(params), nc, nw)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "kopt":
    # kopt <seed> <s4> <branch> <iters> <out.json> : one CMA stream on the stage-1b proxy
    a = sys.argv; b = kopt(int(a[2]), int(a[3]), int(a[4]), int(a[5]), a[6]); print(a[2:5], round(b[0], 2), b[2]); sys.exit()

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] in ("check", "frozen"):
    import concept_bench as CB
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if sys.argv[1] == "frozen":
        t0 = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t0, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps({k: out[k] for k in ("fit_fast", "frozen", "mode")}, default=float)); sys.exit()
    B = CB.Bench(60, 160); t0 = time.time(); r = bench_eval(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "f", "seats", "knee", "parts_ib14", "res_max", "error")}, round(time.time() - t0, 1), B.mode)
    sys.exit()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "kin"
    if mode == "kin":
        B, Q, ws, ov, acr = poses110()
        u1, u3, a1, a2 = leader(); P3 = Q @ u3
        th = np.degrees(np.arccos(np.clip(P3 @ u1, -1, 1)))
        for m in (10, 5):
            ok = (th >= abs(a1 - a2) + m) & (th <= a1 + a2 - m); print(f"circle kit rule m={m}: ws {ok[ws].mean():.4f} overhead {ok[ov].mean():.4f}")
        for br in (1, -1):
            fb = fourbar(calib_circle(u1, a1, br))
            for X in (20, 25, 30, 34, 38, 43):
                c, good, _ = coverage(fb, P3, a2, X, br, ws); print(f"circle branch {br} X={X}: ws {c:.4f} overhead {good[ov].mean():.4f}")


def append_sweep(entries, path=os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")):
    """append bench evaluations IN ORDER: {k, t, params, inband14, inband10, reach, follow, contact, gap, ...}"""
    import datetime
    old = json.load(open(path)) if os.path.exists(path) else []
    for e in entries:
        r = e["report"]
        old.append(dict(k=len(old), t=e.get("t") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        params=e["params"], **{m: r.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                        why=r.get("why"), stage=e.get("stage", ""), honest=r.get("honest"), margin=e.get("margin", 10)))
    json.dump(old, open(path + ".tmp", "w"), indent=1, default=float); os.replace(path + ".tmp", path)
    return len(old)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "local":
    # local <configs.json> <stage>: evaluate each config on Bench(60,160) and append to the sweep file
    import concept_bench as CB
    B = CB.Bench(60, 160)
    for par in json.load(open(sys.argv[2])):
        B.reset(); r = bench_eval(B, par)
        n = append_sweep([dict(params=par, report=r, stage=sys.argv[3])])
        print(n, r.get("gap"), r.get("reach"), r.get("inband14"), r.get("why"), flush=True)
