"""Family X - the elbow-post shoulder: three pivots, all axes through the shoulder centre.

  J1  scapula pivot (axis b)  -L1-  J2 (axis c, over the shoulder)  -L2-  J3 at the ELBOW, axis u aimed back at the
  shoulder centre, only DELTA off the humerus axis. Because a pivot may sit anywhere along its axis, J3 is placed
  ~400 mm out (beside the lateral epicondyle) where its axis, nearly the humerus axis, is outside the arm. Humeral
  axial rotation then happens almost entirely in J3: L2 becomes an upper-arm bar and J1/J2 barely move.
Rules as the routed searches: BodyParts3D skin (extended grids to the elbow), links routed in their own frames
(L1 in the shoulder shell, L2 in the shell plus a corridor along the arm), pins at free radii, J3 travel limited by
contact (POST_HALF), singularity margins, one branch.

    WORKERS=4 python3 family_X.py [RMAX] [GENS]
"""
import json, math, os, sys, random
import concurrent.futures as cf
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
import design_search as D
import design_search_families as F
import design_search_anat as A
from design_search_pivots import w_dir

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "skin_grids_ext.json"))); SHP = tuple(M["shape"]); LO = np.array(M["lo"]); GST = M["STEP"]
GR = np.fromfile(os.path.join(HERE, "skin_grids_ext.bin"), dtype=np.float32).reshape((-1,) + SHP)
TRUNK, ARM = GR[:-1], GR[-1]
CLEAR, STEP, RMIN, POST_FREE = 11.0, 8.0, 70.0, 30.0
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 and __name__ == "__main__" else 150.0
POST_HALF = float(os.environ.get("POST_HALF", 180))
SUB = slice(None)


def look(G, P):
    c = ((P - LO) / GST).T
    return map_coordinates(G, c, order=1, mode="constant", cval=100.0)


def graph(I):
    idx = {tuple(k): i for i, k in enumerate(I)}; rows, cols = [], []
    for i, k in enumerate(I):
        for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            j = idx.get((k[0] + d[0], k[1] + d[1], k[2] + d[2]))
            if j is not None: rows.append(i); cols.append(j)
    return np.array(rows, int), np.array(cols, int)


def domain(axis=None, rmax_arm=450.0, cone=30.0):
    m = int(math.ceil((rmax_arm if axis is not None else RMAX) / STEP)); gi = np.arange(-m, m + 1)
    I = np.stack(np.meshgrid(gi, gi, gi, indexing="ij"), -1).reshape(-1, 3); X = I * STEP
    r = np.linalg.norm(X, axis=1); keep = (r >= RMIN) & (r <= RMAX)
    if axis is not None:
        ca = (X @ axis) / (r + 1e-9); keep |= (r >= RMIN) & (r <= rmax_arm) & (ca >= math.cos(cone * D.D2R))
    I, X = I[keep], X[keep].astype(float); er, ec = graph(I)
    return X, er, ec


def frame(a, b):
    n = b - (a * b).sum(-1, keepdims=True) * a; n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
    return np.stack([a, n, np.cross(a, n)], -1)


def blocked(X, Rk, split=False):
    """bool (N, M) per pose: trunk/girdle contact, and upper-arm contact (separately if split)."""
    hf, rs, eb = A.HF_ALL[SUB], A.RS_ALL[SUB], A.EBIN_ALL[SUB]
    bt = np.zeros((len(Rk), len(X)), bool); ba = np.zeros_like(bt)
    for n in range(len(Rk)):
        P = X @ Rk[n].T
        bt[n] = look(TRUNK[eb[n]], P @ rs[n].T) < CLEAR
        ba[n] = look(ARM, P @ hf[n]) < CLEAR
    return (bt, ba) if split else (bt | ba)


def route(X, er, ec, Bs, a, b, alive):
    cnt = Bs[alive].sum(0).astype(float); w = 1.0 + 1000.0 * (cnt[er] + cnt[ec]) / 2
    G = coo_matrix((w, (er, ec)), shape=(len(X), len(X))).tocsr()
    dist, pred = dijkstra(G, directed=False, indices=a, return_predecessors=True)
    if not np.isfinite(dist[b]): return None, None
    path = [b]
    while path[-1] != a: path.append(pred[path[-1]])
    return path, Bs[:, path].any(1) & alive


def nearest(X, x): return int(np.argmin(np.linalg.norm(X - x, axis=1)))


def evaluate(d, full=False):
    hf, h = A.HF_ALL[SUB], A.HG_ALL[SUB]
    b = np.broadcast_to(np.asarray(d["b"], float), h.shape); u = hf @ w_dir(d["delta"], d["waz"])
    a1, a2 = d["a1"] * D.D2R, d["a2"] * D.D2R
    c, ok = F.circ_int(b, a1, u, a2, d["branch"])
    ok &= F.triangle_ok(b, u, a1, a2) & (np.abs((b * u).sum(-1)) <= math.cos(A.SING))
    post = A.about(c, h, u); best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((post - cc + 180) % 360 - 180) <= POST_HALF)).sum()
        if k > best[0]: best = (k, cc)
    alive = ok & (np.abs((post - best[1] + 180) % 360 - 180) <= POST_HALF); kin = alive.mean()
    if full is None or kin < 0.6: return dict(d, cov=0.0, kin=float(kin))
    i0 = int(np.argmax(alive)); R1, R2 = frame(b, c), frame(u, c)
    X1, e1r, e1c = domain(); X2, e2r, e2c = domain(axis=R2[i0].T @ h[i0])
    b1, c1 = R1[i0].T @ b[i0], R1[i0].T @ c[i0]; c2, u2 = R2[i0].T @ c[i0], R2[i0].T @ u[i0]
    B1 = blocked(X1, R1)
    rr = np.arange(RMIN + STEP, RMAX - 2, STEP)
    rb = rr[int(np.argmin([B1[:, nearest(X1, b1 * r)][alive].sum() for r in rr]))]
    B2t, B2a = blocked(X2, R2, split=True); best_u = None
    for ru in np.arange(150, 446, 16):                     # the cuff bracket meets the arm within POST_FREE of J3
        near = np.linalg.norm(X2 - u2 * ru, axis=1) < POST_FREE
        B2 = B2t | (B2a & ~near[None])
        cu = B2[:, nearest(X2, u2 * ru)][alive].sum()
        if best_u is None or cu < best_u[0]: best_u = (cu, ru, B2)
    _, ru, B2 = best_u
    rc = rr[int(np.argmin([(B1[:, nearest(X1, c1 * r)] | B2[:, nearest(X2, c2 * r)])[alive].sum() for r in rr]))]
    links = [(X1, e1r, e1c, B1, nearest(X1, b1 * rb), nearest(X1, c1 * rc)), (X2, e2r, e2c, B2, nearest(X2, c2 * rc), nearest(X2, u2 * ru))]
    paths = [None, None]
    for _ in range(6):
        changed = False
        for k, (X, er, ec, Bs, va, vb) in enumerate(links):
            alive &= ~(Bs[:, va] | Bs[:, vb])
            path, blk = route(X, er, ec, Bs, va, vb, alive)
            if path is None: return dict(d, cov=0.0, kin=float(kin))
            paths[k] = path
            if blk.any(): alive &= ~blk; changed = True
        if not changed: break
    out = dict(d, cov=float(alive.mean()), kin=float(kin), post_centre=best[1], r_pins=[float(rb), float(rc), float(ru)])
    if full:
        out["paths"] = [links[k][0][paths[k]].tolist() for k in range(2)]; out["frames0"] = [R1[i0].tolist(), R2[i0].tolist()]; out["alive"] = alive.tolist()
    return out


# ---------------------------------------------------------------- evolutionary search
def bvec(az, el): return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
def design(g):
    az, el, a1, a2, de, wz, br = g
    return dict(b=bvec(az, el), az=round(az, 1), el=round(el, 1), a1=round(a1, 1), a2=round(a2, 1), delta=round(de, 1), waz=round(wz, 1), branch=int(br))
def feasible(g):
    az, el, a1, a2, de, wz, br = g
    return -20 <= el <= 90 and 30 <= a1 <= 140 and 30 <= a2 <= 140 and 7 <= de <= 18 and D.base_ok(np.array(bvec(az, el)))
def init(k):
    global SUB, RMAX
    SUB = slice(None, None, k)
def score(g):
    try: return evaluate(design(g))["cov"]
    except Exception: return 0.0
def kinscore(g):
    try: return evaluate(design(g), None)["kin"]
    except Exception: return 0.0
def mutate(g, s):
    for _ in range(60):
        az, el, a1, a2, de, wz, br = g
        n = [(az + random.gauss(0, 25 * s)) % 360, el + random.gauss(0, 12 * s), a1 + random.gauss(0, 12 * s), a2 + random.gauss(0, 12 * s),
             de + random.gauss(0, 4 * s), ((wz + random.gauss(0, 35 * s) + 180) % 360) - 180, br if random.random() > 0.1 else -br]
        if feasible(n): return n
    return g


if __name__ == "__main__":
    GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 10; W = int(os.environ.get("WORKERS", 4)); random.seed(11)
    # kinematic seeding (cheap): sample widely, keep the best 24
    pool = []
    while len(pool) < 1500:
        g = [random.uniform(0, 360), random.uniform(-10, 88), random.uniform(40, 130), random.uniform(40, 130), random.uniform(7, 18), random.uniform(-180, 180), random.choice([1, -1])]
        if feasible(g): pool.append(g)
    log = open(f"family_X_{int(RMAX)}.log", "w")
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(4,)) as ex:
        ks = list(ex.map(kinscore, pool, chunksize=32))
    seeds = [g for _, g in sorted(zip(ks, pool), key=lambda t: -t[0])[:24]]
    print("kinematic seeds", [round(100 * k, 1) for k in sorted(ks, reverse=True)[:8]], file=log, flush=True)
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(8,)) as ex:
        sc = list(ex.map(score, seeds, chunksize=1))
        pop = sorted(zip(sc, seeds), key=lambda t: -t[0])[:6]; sig = 1.0
        print("gen 0", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
        for gen in range(1, GENS + 1):
            kids = [mutate(random.choice(pop)[1], sig) for _ in range(12)]
            ks2 = list(ex.map(score, kids, chunksize=1)); prev = pop[0][0]
            pop = sorted(pop + list(zip(ks2, kids)), key=lambda t: -t[0])[:6]
            sig = max(0.3, sig * (0.85 if pop[0][0] <= prev else 1.0))
            print(f"gen {gen}", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
    json.dump([dict(design(g), screen=s) for s, g in pop], open(f"family_X_{int(RMAX)}_pop.json", "w"))
