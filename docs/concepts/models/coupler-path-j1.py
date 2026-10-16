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
    return dict(A0=A0, B0=B0, A1=A1, B1=B1, p2=unit(p2), mu=mu, valid=valid, ok=ok)


def curve_roots(fb, P3, a2, X, branch, t_grid=None):
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
    good = V[i] & V[i2] & (cross >= X) & (sg == branch)
    return dict(j=j, t=t, cross=cross, sg=sg, good=good, q=q, i=i)


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
