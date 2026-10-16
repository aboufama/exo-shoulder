"""Fold-widening >= 3-passive closures: which ones exist, where the passive rotation must sit, how much of the J2 fold
window they open, and whether the closure determines the passive coordinate (2026-10-16, docs/concepts/fold-widening-3passive.md).

Kinematic level, Bench(110,360) frames (470 poses: 110 clip + 360 workspace), fold margin K.FOLD_MARGIN (5), seats of the
polished pin knee H1 (J1 / J2 on GH rays, J3 line off GH, knee pins || J3). No skin here; hub parking is fold3p_park.py.

Two determined closures (derivation in the note, section 1):

  PROX ("coupled J1 rocker"): J1's hub sits on a rocker that turns by rho about a passive pin c (scapula-fixed axis c through
  a point o, o perp c, |o| = R from GH). The active spherical chain is then centred at G'(rho) = (I - Rc(rho)) o, not GH.
  The pin knee (2 pins || u3, arm side) absorbs the in-plane drift; the OUT-OF-PLANE equation fixes rho:
        w . (I - Rc(rho)) o = h     (w = the arm-fixed J3 direction in the scapula frame, h = knee-plane height mismatch)
  -> A cos rho + B sin rho = A - k,  A = w.o^, B = w.(c x o^), k = h / R  -> rho = phi + s_rho acos((A - k) / |A,B|).
  The fold law then reads th = angle(Rc(rho) u1, w).

  DIST ("coupled cuff roll"): the active chain is centred at G0 = e g^ (scapula-fixed, offset from GH); the knee's arm pad
  sits on a carriage that turns by c about a passive pin v through GH (arm frame). Out-of-plane equation:
        Rv(c) u3 . g_arm = -k     (g_arm = the unit offset g^ seen in the arm frame, k = h / e)
  -> th = angle(u1, Rv(c) u3 in the scapula frame).

    OMP_NUM_THREADS=1 CB_QUIET_EXACT=1 python3 docs/research/fold3p/fold3p.py [n_random]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); os.environ.setdefault("CB_QUIET_EXACT", "1")
import concept_bench as CB, concept_kit as K                 # noqa: E402

D2R = math.pi / 180
M = K.FOLD_MARGIN
H1 = dict(az1=101.1634, el1=63.8986, az2=30.153, el2=47.0108, wd=70.3931, wa=-8.1248, b3=0.2842, lE=59.5534, lc=28.2401,
          phiE=-5.8107, phib=-54.914, ang_min=30.4611, stk=5.6815, rad1=10, rad2=10, rad3=10)


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def seats(P=H1):
    PK = _load("pk_f3", os.path.join(REPO, "docs", "concepts", "models", "skin-normal-3r-pin-knee.py"))
    D = PK.Design(P)
    return dict(u1=np.array(D.u[0]), u3=np.array(D.u[2]), a1=math.degrees(D.A[0]), a2=math.degrees(D.A[1]), sigma=int(D.branch))


def rot(c, ang):
    """(..., 3, 3) rotations about unit axis c (3,) or (..., 3) by ang (...) rad"""
    c = np.broadcast_to(np.asarray(c, float), np.shape(ang) + (3,)); a = np.asarray(ang, float)[..., None, None]
    Kx = np.zeros(c.shape[:-1] + (3, 3)); Kx[..., 0, 1] = -c[..., 2]; Kx[..., 0, 2] = c[..., 1]; Kx[..., 1, 0] = c[..., 2]
    Kx[..., 1, 2] = -c[..., 0]; Kx[..., 2, 0] = -c[..., 1]; Kx[..., 2, 1] = c[..., 0]
    return np.eye(3) + np.sin(a) * Kx + (1 - np.cos(a)) * (Kx @ Kx)


def perp_basis(c):
    c = K.unit(c); t = np.array([0.0, 0.0, 1.0]) if abs(c[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = K.unit(np.cross(c, t)); return e1, np.cross(c, e1)


def window(a1, a2, m=M): return abs(a1 - a2) + m, min(a1 + a2, 360 - a1 - a2) - m


def ang(a, b): return np.degrees(np.arccos(np.clip((K.unit(a) * K.unit(b)).sum(-1), -1, 1)))


# ---- the two closures (vectorised over poses) -----------------------------------------------------------------------
def prox(p, S, RS, RHG):
    """-> rho (deg), exists, th (deg), u1 rotated (scapula frame), w (scapula frame)"""
    w = np.einsum("pji,pjk,k->pi", RS, RHG, S["u3"])                 # RS^T RHG u3
    c = K.bvec(p["caz"], p["cel"]); e1, e2 = perp_basis(c); oh = math.cos(p["chi"] * D2R) * e1 + math.sin(p["chi"] * D2R) * e2
    A = w @ oh; Bq = w @ np.cross(c, oh); r = np.hypot(A, Bq) + 1e-12; x = (A - p["k"]) / r
    ex = np.abs(x) <= 1.0; rho = np.arctan2(Bq, A) + p["s"] * np.arccos(np.clip(x, -1, 1))
    rho = (rho + math.pi) % (2 * math.pi) - math.pi
    U1 = np.einsum("pij,j->pi", rot(c, rho), S["u1"]); th = ang(U1, w)
    return np.degrees(rho), ex, th, U1, w


def dist(p, S, RS, RHG):
    """-> c (deg), exists, th, u3 rotated (scapula frame)"""
    v = K.wdir(p["vd"], p["va"]); g = K.bvec(p["gaz"], p["gel"])
    garm = np.einsum("pij,pjk,k->pi", np.transpose(RHG, (0, 2, 1)), RS, g)  # RHG^T RS g
    x = S["u3"]; xp = x - (x @ v) * v; vx = np.cross(v, x)
    A = garm @ xp; Bq = garm @ vx; C = (x @ v) * (garm @ v); r = np.hypot(A, Bq) + 1e-12; y = (-p["k"] - C) / r
    ex = np.abs(y) <= 1.0; cc = np.arctan2(Bq, A) + p["s"] * np.arccos(np.clip(y, -1, 1)); cc = (cc + math.pi) % (2 * math.pi) - math.pi
    u3a = np.einsum("pij,j->pi", rot(v, cc), x); W = np.einsum("pji,pjk,pk->pi", RS, RHG, u3a); th = ang(S["u1"][None], W)
    return np.degrees(cc), ex, th, W


def take(kind, p, S, RS, RHG, travel):
    if kind == "prox": q, ex, th, _, _ = prox(p, S, RS, RHG)
    else: q, ex, th, _ = dist(p, S, RS, RHG)
    lo, hi = window(S["a1"], S["a2"]); q0 = p.get("q0", 0.0)
    dq = (q - q0 + 180) % 360 - 180
    return ex & (th >= lo) & (th <= hi) & (np.abs(dq) <= travel), q, th


# ---- continuity: kNN graph over the workspace poses, 2-deg slerp edges ------------------------------------------------
class Graph:
    def __init__(self, B, F, knn=6, max_deg=32.0):
        ws = np.nonzero(F.ws)[0]; Rh = F.RHG[ws]
        D = np.degrees(np.arccos(np.clip((np.einsum("aij,bij->ab", Rh, Rh) - 1) / 2, -1, 1)))
        Ds = np.degrees(np.arccos(np.clip((np.einsum("aij,bij->ab", F.RS[ws], F.RS[ws]) - 1) / 2, -1, 1)))
        D = np.maximum(D, Ds); np.fill_diagonal(D, 1e9); E = set()
        for a in range(len(ws)):
            for b in np.argsort(D[a])[:knn]:
                if D[a, b] <= max_deg: E.add((min(a, b), max(a, b)))
        self.ws = ws; self.E = sorted(E); el = np.array([B.poses[i]["elev"] for i in ws]); self.seed = el <= 15.0
        subs = [K._slerp_frames(F, ws[a], ws[b], 2.0) for a, b in self.E]
        self.off = np.cumsum([0] + [len(s.RS) for s in subs]); self.RS = np.concatenate([s.RS for s in subs]); self.RHG = np.concatenate([s.RHG for s in subs])

    def connected(self, kind, p, S, travel, ok_ws, jump=10.0):
        ok, q, _ = take(kind, p, S, self.RS, self.RHG, travel); good = []
        for e, (a, b) in enumerate(self.E):
            s0, s1 = self.off[e], self.off[e + 1]; dq = np.abs((np.diff(q[s0:s1]) + 180) % 360 - 180)
            good.append(bool(ok[s0:s1].all() and (dq <= jump).all()))
        n = len(self.ws); conn = np.zeros(n, bool); adj = [[] for _ in range(n)]
        for (a, b), g in zip(self.E, good):
            if g: adj[a].append(b); adj[b].append(a)
        front = [i for i in range(n) if self.seed[i] and ok_ws[i]]
        for i in front: conn[i] = True
        while front:
            nxt = []
            for a in front:
                for b in adj[a]:
                    if not conn[b] and ok_ws[b]: conn[b] = True; nxt.append(b)
            front = nxt
        return conn


def search(kind, S, F, n, travel, rng):
    lo_hi = dict(prox=dict(caz=(-180, 180), cel=(-80, 90), chi=(0, 360), k=(-1.2, 1.2)),
                 dist=dict(vd=(0, 180), va=(-180, 180), gaz=(-180, 180), gel=(-90, 90), k=(-1.2, 1.2)))[kind]
    ws = F.ws; best = []
    for it in range(n):
        p = {k: rng.uniform(*v) for k, v in lo_hi.items()}; p["s"] = rng.choice([-1, 1])
        if kind == "prox": q, ex, th, _, _ = prox(p, S, F.RS, F.RHG)
        else: q, ex, th, _ = dist(p, S, F.RS, F.RHG)
        q0 = float(np.median(q[ws & ex & (np.array(ELEV) <= 15)])) if (ws & ex & (np.array(ELEV) <= 15)).any() else 0.0
        p["q0"] = q0; ok, _, _ = take(kind, p, S, F.RS, F.RHG, travel)
        best.append((float(ok[ws].mean()), p))
    best.sort(key=lambda t: -t[0]); return best[:40]


def refine(kind, S, F, p0, travel, rng, n=400, scale=1.0):
    keys = [k for k in p0 if k not in ("s", "q0")]; step = dict(caz=8, cel=8, chi=12, k=0.08, vd=8, va=8, gaz=8, gel=8)
    best = (take(kind, p0, S, F.RS, F.RHG, travel)[0][F.ws].mean(), dict(p0))
    for it in range(n):
        p = dict(best[1])
        for k in keys: p[k] = p[k] + rng.normal() * step[k] * scale
        p["k"] = float(np.clip(p["k"], -1.5, 1.5))
        if kind == "prox": q, ex, *_ = prox(p, S, F.RS, F.RHG)
        else: q, ex, *_ = dist(p, S, F.RS, F.RHG)
        m = F.ws & ex & (np.array(ELEV) <= 15)
        p["q0"] = float(np.median(q[m])) if m.any() else p["q0"]
        v = take(kind, p, S, F.RS, F.RHG, travel)[0][F.ws].mean()
        if v >= best[0]: best = (v, p)
    return best


def free_ceiling(S, F, axes, travel, side):
    """per-pose-free passive rotation (bound): scapula side rotates u1 about c, arm side rotates u3 about v"""
    lo, hi = window(S["a1"], S["a2"]); ph = np.radians(np.arange(-travel, travel + 0.01, 1.0)); out = []
    w = np.einsum("pji,pjk,k->pi", F.RS, F.RHG, S["u3"])[F.ws]
    for ax in axes:
        if side == "scap":
            U = np.einsum("fij,j->fi", rot(ax, ph), S["u1"]); T = np.degrees(np.arccos(np.clip(w @ U.T, -1, 1)))
        else:
            U3 = np.einsum("fij,j->fi", rot(ax, ph), S["u3"]); Wf = np.einsum("pji,pjk,fk->pfi", F.RS[F.ws], F.RHG[F.ws], U3)
            T = ang(S["u1"][None, None], Wf)
        out.append(float(((T >= lo) & (T <= hi)).any(1).mean()))
    j = int(np.argmax(out)); return out[j], axes[j]


def main():
    t0 = time.time(); n = int(sys.argv[1]) if len(sys.argv) > 1 else 6000; rng = np.random.default_rng(7)
    B = CB.Bench(110, 360); F = K.frames(B); global ELEV; ELEV = [p["elev"] for p in B.poses]
    S = seats(); lo, hi = window(S["a1"], S["a2"]); ov = F.ws & (np.array(ELEV) >= 140)
    w = np.einsum("pji,pjk,k->pi", F.RS, F.RHG, S["u3"]); th0 = ang(S["u1"][None], w); base = (th0 >= lo) & (th0 <= hi)
    out = dict(bench=[110, 360], margin=M, seats=dict(u1=S["u1"].round(4).tolist(), u3=S["u3"].round(4).tolist(), a1=round(S["a1"], 2),
               a2=round(S["a2"], 2), sigma=S["sigma"], window=[round(lo, 1), round(hi, 1)]),
               base=dict(ws=round(float(base[F.ws].mean()), 4), overhead=round(float(base[ov].mean()), 4), clip=round(float(base[F.clip].mean()), 4)))
    print("base", out["base"], flush=True)
    # bounds: per-pose-free passive rotation, scapula side vs arm side, travel 20 / 30 / 40
    Csc = [K.bvec(az, e) for az in range(-180, 180, 10) for e in range(-80, 90, 10)]
    Car = [K.wdir(d, a) for d in range(0, 181, 10) for a in range(-180, 180, 10)]
    out["free_bound"] = {}
    for tr in (20, 30, 40):
        vs, cs = free_ceiling(S, F, Csc, tr, "scap"); va, ca = free_ceiling(S, F, Car, tr, "arm")
        out["free_bound"][str(tr)] = dict(scap=round(vs, 4), scap_axis=np.round(cs, 3).tolist(), arm=round(va, 4), arm_axis=np.round(ca, 3).tolist())
        print("free", tr, out["free_bound"][str(tr)], flush=True)
    G = Graph(B, F); print("graph", len(G.E), "edges", len(G.RS), "substeps", round(time.time() - t0, 1), flush=True)
    out["graph"] = dict(edges=len(G.E), substeps=int(len(G.RS)), knn=6, max_deg=32, seeds=int(G.seed.sum()))
    # base continuity (the plain fold law, no passive): connected share
    res = {}
    for kind in ("prox", "dist"):
        for travel in (30.0, 45.0):
            top = search(kind, S, F, n, travel, rng); fin = []
            for v, p in top[:12]:
                v2, p2 = refine(kind, S, F, p, travel, rng, n=300)
                v3, p3 = refine(kind, S, F, p2, travel, rng, n=200, scale=0.3)
                ok, q, th = take(kind, p3, S, F.RS, F.RHG, travel)
                conn = G.connected(kind, p3, S, travel, ok[G.ws])
                fin.append(dict(static=round(float(ok[F.ws].mean()), 4), connected=round(float(conn.mean()), 4),
                                overhead=round(float(ok[ov].mean()), 4), clip=round(float(ok[F.clip].mean()), 4),
                                q_p5_p95=[round(float(np.percentile(q[ok], 5)), 1), round(float(np.percentile(q[ok], 95)), 1)],
                                params={k: (round(float(x), 4) if k != "s" else int(x)) for k, x in p3.items()}))
                print(kind, travel, fin[-1], flush=True)
            fin.sort(key=lambda r: -r["connected"]); res[f"{kind}_t{int(travel)}"] = fin
    out["search"] = res; out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "fold3p.json"), "w"), indent=1, default=float); print("done", out["secs"])


ELEV = []
if __name__ == "__main__":
    main()
