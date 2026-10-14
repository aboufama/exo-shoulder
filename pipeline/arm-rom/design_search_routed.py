"""Non-redundant shoulder morphologies with ROUTED links (the body-conforming generalisation of the shell designs).

In a spherical mechanism only the joint AXES must pass through the shoulder centre; each link is a rigid body whose
shape between its two pins is free, and each pin may sit at any radius along its axis. The shell designs so far used
great-circle arcs on one fixed radius, which is what runs them into the trapezius ridge, the scapula and the deltoid.
Here every link is grown through the space that is free of the body (anatomical skin, >= CLEAR mm) in ITS OWN frame
over all the poses it must reach:

  1. kinematics: the chain's joint directions per pose (singularity margins, one branch, 180 deg upper-arm post);
  2. for each link, voxels in the link frame (radius RMIN..RMAX from the shoulder centre) are tested against the
     body in every pose (trunk + girdle grid per elevation, upper-arm grid in the humerus frame);
  3. each pin gets the clearest radius on its axis; each link must connect its two pins through voxels that are free
     in every kept pose (6-connected path; the link is a bar along that path). Poses whose collisions block the
     cheapest connection are dropped (greedy) until every link connects.
Coverage = kept poses / all 3,993 natural poses. RMAX caps how far the exo stands off the shoulder centre (profile).

    python3 design_search_routed.py C [RMAX]
"""
import json, math, os, sys
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
CLEAR = 11.0            # voxel centre to skin (link half-thickness 6 + 3 mm gap + 2 mm voxel slack)
STEP = 8.0              # voxel size, mm
RMIN = 70.0
RMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
POST_FREE = 30.0        # the rigid upper-arm link meets the arm within this distance of the post pin
SUB = slice(None)


def set_stride(k):
    global SUB
    SUB = slice(None, None, k)


def voxels():
    m = int(math.floor(RMAX / STEP)); gi = np.arange(-m, m + 1)
    I = np.stack(np.meshgrid(gi, gi, gi, indexing="ij"), -1).reshape(-1, 3); X = I * STEP
    r = np.linalg.norm(X, axis=1); keep = (r >= RMIN) & (r <= RMAX)
    X, I = X[keep].astype(float), I[keep]
    # 6-neighbour graph between kept voxels
    idx = {tuple(k): i for i, k in enumerate(I)}
    rows, cols = [], []
    for i, k in enumerate(I):
        for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            j = idx.get((k[0] + d[0], k[1] + d[1], k[2] + d[2]))
            if j is not None: rows.append(i); cols.append(j)
    return X, np.array(rows, dtype=int), np.array(cols, dtype=int)


VX, ER, EC = voxels()


def frame(a, b):
    """Rigid frame of a link from its two pin directions (N, 3) -> (N, 3, 3), columns = local axes in the scapula frame."""
    n = b - (a * b).sum(-1, keepdims=True) * a; n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
    return np.stack([a, n, np.cross(a, n)], -1)


def blocked(Rk, post=None, arm_check=True):
    """Rk (N, 3, 3) link frames for the poses; returns bool (N, M): voxel blocked in that pose."""
    hf, rs, eb = A.HF_ALL[SUB], A.RS_ALL[SUB], A.EBIN_ALL[SUB]
    out = np.zeros((len(Rk), len(VX)), bool)
    for n in range(len(Rk)):
        P = VX @ Rk[n].T                                   # scapula frame
        dt = A.lookup(A.TRUNK[eb[n]], P @ rs[n].T)
        bad = dt < CLEAR
        if arm_check:
            da = A.lookup(A.ARM, P @ hf[n])                # humerus frame: Hf^T p  ==  p @ Hf
            near = np.zeros(len(VX), bool) if post is None else np.linalg.norm(P - post[n], axis=1) < POST_FREE
            bad |= (da < CLEAR) & ~near
        out[n] = bad
    return out


def local(Rk0, p):
    """A point given in the scapula frame for pose 0 -> link-local coordinates (constant for pins on the link)."""
    return Rk0.T @ p


def nearest_voxel(x):
    return int(np.argmin(np.linalg.norm(VX - x, axis=1)))


def route(Bs, a_vox, b_vox, alive):
    """Cheapest 6-connected path between two voxels; node cost = number of kept poses blocking it (+ length).
    Returns (path, set of kept poses that block it)."""
    cnt = Bs[alive].sum(0).astype(float)
    w = 1.0 + 1000.0 * (cnt[ER] + cnt[EC]) / 2
    G = coo_matrix((w, (ER, EC)), shape=(len(VX), len(VX))).tocsr()
    dist, pred = dijkstra(G, directed=False, indices=a_vox, return_predecessors=True)
    if not np.isfinite(dist[b_vox]): return None, None
    path = [b_vox]
    while path[-1] != a_vox: path.append(pred[path[-1]])
    blockers = Bs[:, path].any(1) & alive
    return path, blockers


def evaluate_C(d, full_output=False, kin_only=False):
    hf, h = A.HF_ALL[SUB], A.HG_ALL[SUB]; N = len(hf)
    b = np.asarray(d["b"], float); u = hf @ w_dir(d["delta"], d["waz"]); B = np.broadcast_to(b, u.shape)
    a1, a2 = d["a1"] * D.D2R, d["a2"] * D.D2R
    c, ok = F.circ_int(B, a1, u, a2, d["branch"])
    ok &= F.triangle_ok(B, u, a1, a2) & (np.abs((B * u).sum(-1)) <= math.cos(A.SING))
    post = A.about(c, h, u); HALF = float(os.environ.get("POST_HALF", 90))
    best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((post - cc + 180) % 360 - 180) <= HALF)).sum()
        if k > best[0]: best = (k, cc)
    alive = ok & (np.abs((post - best[1] + 180) % 360 - 180) <= HALF)
    kin = alive.mean()
    if kin_only: return dict(d, kin=float(kin))
    if kin < 0.6: return dict(d, cov=0.0, kin=float(kin))
    # link frames: L1 = (b, c) rotating about b; L2 = (u, c) rotating about the post
    R1 = frame(B, c); R2 = frame(u, c)
    rr = np.arange(RMIN + STEP, RMAX - 2, STEP)
    # pins: base on b (link 1 frame), mid on c (both frames), post on u (link 2 frame)
    B1 = blocked(R1, None, True)
    i0 = int(np.argmax(alive))
    B2 = blocked(R2, u * 0, True)                          # placeholder post (set per radius below)
    def pin_cost(dirs_local_list, Bsets):
        best_r, best_c = None, 1e9
        for r in rr:
            cst = sum(Bs[:, nearest_voxel(dl * r)][alive].sum() for dl, Bs in zip(dirs_local_list, Bsets))
            if cst < best_c: best_r, best_c = r, cst
        return best_r
    b_loc1 = local(R1[i0], b); c_loc1 = local(R1[i0], c[i0]); c_loc2 = local(R2[i0], c[i0]); u_loc2 = local(R2[i0], u[i0])
    rb = pin_cost([b_loc1], [B1]); rc = pin_cost([c_loc1, c_loc2], [B1, B2])
    # post: recompute link-2 blocking with the arm exemption around the chosen post radius
    best_ru, best_cost, best_B2 = None, 1e9, None
    for ru in rr[::2]:
        B2r = blocked(R2, u * ru, True)
        cst = B2r[:, nearest_voxel(u_loc2 * ru)][alive].sum() + B2r[:, nearest_voxel(c_loc2 * rc)][alive].sum()
        if cst < best_cost: best_ru, best_cost, best_B2 = ru, cst, B2r
    ru, B2 = best_ru, best_B2
    links = [(B1, nearest_voxel(b_loc1 * rb), nearest_voxel(c_loc1 * rc)), (B2, nearest_voxel(c_loc2 * rc), nearest_voxel(u_loc2 * ru))]
    paths = [None, None]
    for _ in range(6):                                     # drop poses that block the cheapest connections
        changed = False
        for k, (Bs, va, vb) in enumerate(links):
            alive &= ~(Bs[:, va] | Bs[:, vb])              # the pins themselves must be free
            path, blk = route(Bs, va, vb, alive)
            if path is None: return dict(d, cov=0.0, kin=float(kin))
            paths[k] = path
            if blk.any(): alive &= ~blk; changed = True
        if not changed: break
    out = dict(d, cov=float(alive.mean()), kin=float(kin), post_centre=best[1], r_pins=[float(rb), float(rc), float(ru)])
    if full_output:
        out["alive"] = alive.tolist()
        out["paths"] = [VX[p].tolist() for p in paths]
        out["frames0"] = [R1[i0].tolist(), R2[i0].tolist()]
    return out


if __name__ == "__main__":
    fam = sys.argv[1]
    # candidates: the best anatomical shell designs plus the best kinematic designs
    cands = []
    for r in json.load(open(os.path.join(HERE, "design_search_anat_C.json"))):
        cands.append({k: r[k] for k in ("b", "az", "el", "a1", "a2", "delta", "waz", "branch")})
    pv = json.load(open(os.path.join(HERE, "design_search_pivots.json")))[:60]
    for r in pv:
        for br in (1, -1):
            cands.append(dict(b=r["b"], az=r["az"], el=r["el"], a1=r["a1"], a2=r["a2"], delta=r["delta"], waz=r["waz"], branch=br))
    seen, uniq = set(), []
    for c in cands:
        key = (c["az"], c["el"], c["a1"], c["a2"], c["delta"], c["waz"], c["branch"])
        if key not in seen: seen.add(key); uniq.append(c)
    print(f"family {fam}: {len(uniq)} candidates, RMAX {RMAX:.0f} mm, {len(VX)} voxels per link", flush=True)
    W = int(os.environ.get("WORKERS", 4))
    with cf.ProcessPoolExecutor(max_workers=W, initializer=set_stride, initargs=(8,)) as ex:
        res = list(ex.map(evaluate_C, uniq, chunksize=1))
    res.sort(key=lambda r: -r["cov"])
    print("screened:", [round(100 * r["cov"], 1) for r in res[:8]], flush=True)
    top = [{k: v for k, v in r.items() if k in ("b", "az", "el", "a1", "a2", "delta", "waz", "branch")} for r in res[:8]]
    with cf.ProcessPoolExecutor(max_workers=W, initializer=set_stride, initargs=(2,)) as ex:
        full = list(ex.map(evaluate_C, top, [True] * len(top), chunksize=1))
    full.sort(key=lambda r: -r["cov"])
    for r in full[:5]:
        print(f"  cov {100 * r['cov']:5.1f}%  (kinematic {100 * r['kin']:.1f}%)  az {r['az']} el {r['el']} arcs {r['a1']}/{r['a2']} delta {r['delta']} waz {r['waz']} br {r['branch']} pins r {r.get('r_pins')} post c {r.get('post_centre')}", flush=True)
    json.dump(full, open(os.path.join(HERE, f"design_search_routed_{fam}_{int(RMAX)}.json"), "w"))


# ---------------------------------------------------------------- generic router (any pin-jointed spherical chain)
def route_design(pins, links, post, alive, full_output=False):
    """pins: name -> (N, 3) unit axis directions (scapula frame) per pose; links: list of pin-name tuples (one rigid
    body each; frame from its first two pins, all its pins connected in order); post: name of the upper-arm pin.
    Pin radius: the clearest radius on its axis over every link that carries it. Returns (alive, details)."""
    i0 = int(np.argmax(alive)); rr = np.arange(RMIN + STEP, RMAX - 2, STEP)
    R = [frame(pins[l[0]], pins[l[1]]) for l in links]
    loc = [{p: local(R[k][i0], pins[p][i0]) for p in l} for k, l in enumerate(links)]
    # blocking with the arm exemption near the post: use a mid radius for the post first, refine after
    rp0 = 0.5 * (RMIN + RMAX)
    Bk = [blocked(R[k], pins[post] * rp0 if post in l else None, True) for k, l in enumerate(links)]
    radius = {}
    for p in pins:
        carriers = [k for k, l in enumerate(links) if p in l]
        costs = [sum(Bk[k][:, nearest_voxel(loc[k][p] * r)][alive].sum() for k in carriers) for r in rr]
        radius[p] = float(rr[int(np.argmin(costs))])
    for k, l in enumerate(links):
        if post in l: Bk[k] = blocked(R[k], pins[post] * radius[post], True)
    paths = [[] for _ in links]
    for _ in range(6):
        changed = False
        for k, l in enumerate(links):
            vs = [nearest_voxel(loc[k][p] * radius[p]) for p in l]
            for v in vs: alive = alive & ~Bk[k][:, v]
            paths[k] = []
            for va, vb in zip(vs, vs[1:]):
                path, blk = route(Bk[k], va, vb, alive)
                if path is None: return alive & False, None
                paths[k] += path
                if blk.any(): alive = alive & ~blk; changed = True
        if not changed: break
    det = dict(radius=radius)
    if full_output: det.update(paths=[VX[p].tolist() for p in paths], frames0=[R[k][i0].tolist() for k in range(len(links))])
    return alive, det


def post_window(post, ok):
    best = (-1, 0)
    for cc in range(-180, 180, 10):
        k = (ok & (np.abs((post - cc + 180) % 360 - 180) <= 90)).sum()
        if k > best[0]: best = (k, cc)
    return ok & (np.abs((post - best[1] + 180) % 360 - 180) <= 90), best[1]


def evaluate_B(d, full_output=False, kin_only=False):
    hf, h = A.HF_ALL[SUB], A.HG_ALL[SUB]
    b = np.asarray(d["b"], float); u0 = hf @ w_dir(d["delta"], d["waz"]); B = np.broadcast_to(b, u0.shape)
    al = d["alpha"] * D.D2R; cth = np.clip((B * u0).sum(-1), -1, 1); th = np.arccos(cth)
    tq = np.tan(th / 4) / math.tan(al); ok = np.abs(tq) <= 1
    phi = np.arccos(np.clip(tq, -1, 1)); w = np.arcsin(np.clip(math.sin(al) * np.sin(phi), -1, 1))
    ok &= (np.degrees(2 * w) >= D.PIN_SEP) & (np.degrees(th) >= D.TH_MIN)
    t1 = u0 - cth[:, None] * B; t1 /= np.linalg.norm(t1, axis=1, keepdims=True) + 1e-12; side = np.cross(B, t1)
    along = lambda s: np.cos(s)[:, None] * B + np.sin(s)[:, None] * t1
    def off(c, sg):
        sd = np.cross(np.cross(c, side), c); sd /= np.linalg.norm(sd, axis=1, keepdims=True) + 1e-12
        return np.cos(w)[:, None] * c + sg * np.sin(w)[:, None] * sd
    c1, c2, d1 = along(th / 4), along(3 * th / 4), along(th / 2)
    pins = dict(b=B, B1=off(c1, 1), C1=off(c1, -1), d1=d1, B2=off(c2, 1), C2=off(c2, -1), u=u0)
    alive, pc = post_window(A.about(B, h, u0), ok); kin = alive.mean()
    if kin_only: return dict(d, kin=float(kin))
    if kin < 0.6: return dict(d, cov=0.0, kin=float(kin))
    links = [("b", "B1"), ("b", "C1"), ("B1", "d1", "C2"), ("C1", "d1", "B2"), ("B2", "u"), ("C2", "u")]
    alive, det = route_design(pins, links, "u", alive.copy(), full_output)
    if det is None: return dict(d, cov=0.0, kin=float(kin))
    return dict(d, cov=float(alive.mean()), kin=float(kin), post_centre=pc, **det)


def evaluate_E(d, full_output=False, kin_only=False):
    hf, h = A.HF_ALL[SUB], A.HG_ALL[SUB]
    b1, b2 = np.asarray(d["b1"], float), np.asarray(d["b2"], float); p, dd = d["p"] * D.D2R, d["d"] * D.D2R
    u = hf @ w_dir(d["delta"], d["waz"]); B1, B2 = np.broadcast_to(b1, u.shape), np.broadcast_to(b2, u.shape)
    e1, k1 = F.circ_int(B1, p, u, dd, d["modes"][0]); e2, k2 = F.circ_int(B2, p, u, dd, d["modes"][1])
    ok = k1 & k2 & F.triangle_ok(B1, u, p, dd) & F.triangle_ok(B2, u, p, dd)
    t1 = e1 - (e1 * u).sum(-1, keepdims=True) * u; t2 = e2 - (e2 * u).sum(-1, keepdims=True) * u
    t1 /= np.linalg.norm(t1, axis=-1, keepdims=True) + 1e-12; t2 /= np.linalg.norm(t2, axis=-1, keepdims=True) + 1e-12
    ok &= np.abs((t1 * t2).sum(-1)) <= math.cos(A.SING * 1.5)
    alive, pc = post_window(A.about(t1 + t2, h, u), ok); kin = alive.mean()
    if kin_only: return dict(d, kin=float(kin))
    if kin < 0.5: return dict(d, cov=0.0, kin=float(kin))
    pins = dict(b1=B1, b2=B2, e1=e1, e2=e2, u=u)
    alive, det = route_design(pins, [("b1", "e1"), ("b2", "e2"), ("u", "e1"), ("u", "e2")], "u", alive.copy(), full_output)
    if det is None: return dict(d, cov=0.0, kin=float(kin))
    return dict(d, cov=float(alive.mean()), kin=float(kin), post_centre=pc, **det)
