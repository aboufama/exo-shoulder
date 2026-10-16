"""JUDGE R6: do parts that move relative to each other interpenetrate? For every pair of parts in different motion groups,
every step-th frame: the deepest point of A inside B, both ways (A in B and B in A), by the winding number + exact depth to
B's welded, closed tessellation (judge/sdist.py, validated in judge/test_sdist.py; open tessellations are listed and never
used as B). Geometry only - does not use the pipeline's member fields. Designed coaxial fits at a shared joint (pin in
sleeve, washer on seat) sit within tol.

A's points are DENSE SURFACE SAMPLES, not only its vertices (2026-10-16: the vertex-only test, every other vertex at step
12, scored 0.0 mm on the first build of l1_offset-skin-normal-3r while link 2 sat 1.12 mm inside the J3 plate - two thin
plates whose edges cross put no vertex inside each other; judge/test_part_contact.py). Per part, in its own frame, cached:
  - every vertex of the tessellation (the old test, kept),
  - points along every sharp edge (dihedral > SHARP_DEG, and open boundaries) at <= h/2 spacing: where a crossing plate
    pokes through first,
  - every face, refined by longest-edge bisection until no edge is longer than h (default 1.0 mm): the midpoints are the
    samples, so every point of every face lies within h / sqrt(3) of a sample and the count is ~ area / h^2 (area
    weighted, deterministic, no n^2 blow-up on long thin facets).
Speed: per frame each part's box is posed (8 corners) and only pairs whose world boxes overlap are tested; A's samples
are then culled to B's own box before the winding number. B's grids are built only for parts that are ever B in such a
pair.
    python3 judge/part_contact.py <design dir|id> [--step 3] [--tol 0.15] [--h 1.0] [--jobs N]  -> <design>/judge/part_contact.json
--jobs splits the frames over N processes (same measurement, merged in frame order; default min(4, cores)).
Default step 3 (10 frames per second of the 30 fps clips): a crossing that lasts 3 frames (0.1 s) is always sampled; the
06b5a59 crossing of l1_offset-skin-normal-3r lasts 11 frames above 1 mm (test_part_contact.py)."""
import argparse, contextlib, json, multiprocessing as mp, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import design_dir, load_parts, frames
from scipy.spatial import cKDTree
from sdist import Mesh

SHARP_DEG = 30.0
KINDS = ("vertex", "sharp edge", "face")


def weld(V, F):
    """welded tessellation (glb faces are split at B-rep seams): (V, F, watertight, trimesh)"""
    import trimesh
    m = trimesh.Trimesh(V, F, process=False); m.merge_vertices(digits_vertex=4); m.update_faces(m.nondegenerate_faces())
    return np.asarray(m.vertices, float), np.asarray(m.faces), bool(m.is_watertight), m


def surface_samples(V, F, h=1.0, sharp_deg=SHARP_DEG, m=None):
    """(points (n, 3), kind (n,) 0 vertex / 1 sharp edge / 2 face) on the surface of one part, in its own frame"""
    V = np.asarray(V, float); F = np.asarray(F)
    if m is None: _, _, _, m = weld(V, F)
    Vw, Fw = np.asarray(m.vertices, float), np.asarray(m.faces)
    # sharp edges (dihedral > sharp_deg) and open boundary edges, sampled at <= h / 2
    E = []
    if len(m.face_adjacency):
        sharp = m.face_adjacency_angles > np.radians(sharp_deg); E.append(m.face_adjacency_edges[sharp])
    eu = np.sort(Fw[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), 1); u, cnt = np.unique(eu, axis=0, return_counts=True); E.append(u[cnt == 1])
    E = np.concatenate(E) if E else np.zeros((0, 2), int); ES = [np.zeros((0, 3))]
    if len(E):
        a, b = Vw[E[:, 0]], Vw[E[:, 1]]; n = np.maximum(1, np.ceil(np.linalg.norm(b - a, axis=1) / (0.5 * h))).astype(int)
        for nn in np.unique(n[n > 1]):
            i = np.where(n == nn)[0]; t = (np.arange(1, nn) / nn)[None, :, None]; ES.append((a[i, None] + (b[i] - a[i])[:, None] * t).reshape(-1, 3))
    ES = np.concatenate(ES)
    # faces: longest-edge bisection until every edge <= h; the midpoints are the face samples
    T = Vw[Fw]; FS = []
    for _ in range(200):
        L = np.linalg.norm(T[:, [1, 2, 0]] - T, axis=2); big = L.max(1) > h
        if not big.any(): break
        T = T[big]; k = np.argmax(L[big], 1); r = np.arange(len(T))
        A, B, C = T[r, k], T[r, (k + 1) % 3], T[r, (k + 2) % 3]; M = 0.5 * (A + B); FS.append(M)
        T = np.concatenate([np.stack([A, M, C], 1), np.stack([M, B, C], 1)])
    FS = np.concatenate(FS) if FS else np.zeros((0, 3))
    if len(FS): FS = np.unique(np.round(FS, 5), axis=0)
    P = np.concatenate([V, ES, FS]); kind = np.r_[np.zeros(len(V), np.int8), np.ones(len(ES), np.int8), np.full(len(FS), 2, np.int8)]
    return P, kind


CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "part_contact")   # git-ignored


def cached_samples(V, F, h, sharp_deg, m):
    """surface_samples, cached on disk by the part's content (the user's parts and the hubs repeat across designs)"""
    import hashlib
    key = hashlib.sha1(np.ascontiguousarray(V, np.float64).tobytes() + np.ascontiguousarray(F, np.int64).tobytes()
                       + np.array([h, sharp_deg, 2.0]).tobytes()).hexdigest()
    f = os.path.join(CACHE, key + ".npz")
    try:
        z = np.load(f); return z["S"], z["kind"]
    except Exception: pass
    S, kind = surface_samples(V, F, h, sharp_deg, m)
    try:
        os.makedirs(CACHE, exist_ok=True); tmp = f"{f}.{os.getpid()}.npz"; np.savez(tmp, S=S, kind=kind); os.replace(tmp, f)
    except Exception: pass
    return S, kind


def prepare(parts, h=1.0, sharp_deg=SHARP_DEG, build=None):
    """per part: group, name, samples (local frame) + kind, local box, closed?, Mesh of the welded tessellation (B side;
    grids built for the indices in build, or for every closed part when build is None)"""
    info = []
    for g, n, V, F in parts:
        Vw, Fw, closed, m = weld(V, F); S, kind = cached_samples(V, F, h, sharp_deg, m)
        lo, hi = S.min(0), S.max(0)
        info.append(dict(g=g, n=n, S=S, kind=kind, closed=closed, M=Mesh(Vw, Fw) if closed else None, lo=lo, hi=hi,
                         C=np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])))
    for i, x in enumerate(info):
        if x["closed"] and (build is None or i in build): build_B(x)
    return info


def build_B(x):
    """B side of a part: the winding-number grid (judge/sdist.py) plus a reject mask on its nodes, OUT = winding 0 and no
    surface within the segment to any point that rounds to the node. Bound: a node with no Mesh sample marked within k
    nodes (chessboard) is farther than k g - g sqrt(3)/2 - M.h from the surface (each sample lies within g sqrt(3)/2 of
    its node; Mesh.S covers the surface within M.h); with k g > M.h + g sqrt(3) that exceeds |P - node| <= g sqrt(3)/2,
    so the segment node -> P crosses nothing and P is outside like the node. Exact, never a guess: it only spares the
    kd-tree and the segment crossings for A's samples well clear of B."""
    from scipy.ndimage import maximum_filter
    M = x["M"]
    if not hasattr(M, "W"): M.build_grid()
    n = np.asarray(M.W.shape); idx = np.clip(np.rint((M.S - M.glo) / M.g).astype(int), 0, n - 1)
    mark = np.zeros(M.W.shape, np.uint8); mark[idx[:, 0], idx[:, 1], idx[:, 2]] = 1
    k = int(np.floor((M.h + M.g * np.sqrt(3)) / M.g)) + 1
    x["OUT"] = (maximum_filter(mark, size=2 * k + 1, mode="constant") == 0) & (M.W == 0)
    import igl
    x["F64"] = np.ascontiguousarray(M.F, np.int64); M.V = np.ascontiguousarray(M.V, float)
    x["AABB"] = igl.AABB(); x["AABB"].init(M.V, x["F64"])
    return x


def pair_ok(info):
    """(n, n) bool: ordered pairs (A, B) that are tested - different motion groups, B closed"""
    g = np.array([x["g"] for x in info]); cl = np.array([x["closed"] for x in info])
    return (g[:, None] != g[None, :]) & cl[None, :]


def world_boxes(info, W):
    """(n, 2, 3) world AABB of every part's local box in one frame (nan for a group the frame does not pose)"""
    out = np.full((len(info), 2, 3), np.nan)
    for i, x in enumerate(info):
        if x["g"] not in W: continue
        R, t = W[x["g"]]; P = x["C"] @ R.T + t; out[i, 0], out[i, 1] = P.min(0), P.max(0)
    return out


def candidates(info, W, ok, tol):
    """ordered pairs (i, j) whose posed boxes overlap (by more than tol) in this frame"""
    bx = world_boxes(info, W); lo, hi = bx[:, 0], bx[:, 1]
    with np.errstate(invalid="ignore"):
        ov = np.all((lo[:, None] < hi[None, :] - tol) & (lo[None, :] < hi[:, None] - tol), axis=2)
    return np.argwhere(ov & ok)


def _tree(A):
    if "T" not in A: A["T"] = cKDTree(A["S"])
    return A["T"]


def depth_in(A, B, Wa, Wb, tol):
    """deepest sample of A inside B (mm, > tol) and its kind, or (0.0, None). A's samples are culled in A's own frame
    first (a kd-tree ball around B's posed box, shrunk by tol), so a big part (a cuff, the BOTTOM bar) is never posed whole"""
    Ra, ta = Wa; Rb, tb = Wb; lo, hi = B["lo"] + tol, B["hi"] - tol
    if np.any(hi <= lo): return 0.0, None
    c = ((0.5 * (lo + hi)) @ Rb.T + tb - ta) @ Ra                                   # B's box centre in A's frame
    m = np.asarray(_tree(A).query_ball_point(c, 0.5 * np.linalg.norm(hi - lo) + 1e-6, return_sorted=False), int)
    if not len(m): return 0.0, None
    P = A["S"][m] @ (Ra.T @ Rb) + (ta - tb) @ Rb                                     # those samples in B's frame
    k = np.all((P > lo) & (P < hi), axis=1); m, P = m[k], P[k]                       # deeper than tol: inside the box by tol
    if not len(m): return 0.0, None
    M = B["M"]; i = np.clip(np.rint((P - M.glo) / M.g).astype(int), 0, np.asarray(M.W.shape) - 1)
    k = ~B["OUT"][i[:, 0], i[:, 1], i[:, 2]]; m, P = m[k], P[k]                       # exact reject: well clear of B, outside
    if not len(m): return 0.0, None
    dep, k = max_depth(B, P, tol)
    return (dep, KINDS[A["kind"][m[k]]]) if k is not None and dep > tol else (0.0, None)


def max_depth(B, P, tol):
    """deepest point of P (B's frame) inside B: (depth mm, index) or (0.0, None). Distance = the exact closest point on
    B's welded tessellation (libigl AABB tree, built once per part); inside = the integer winding number of
    judge/sdist.py: the grid node's own value wherever the surface is farther from P than the node is (then the segment
    node -> P crosses nothing), the exact segment crossings (Mesh.winding_at) only for the few points nearer the surface
    than their node. Points within tol of the surface are skipped first (they cannot be deeper than tol): a coaxial fit at
    a joint puts a whole face on B's surface and costs one distance query per sample, nothing more."""
    M = B["M"]; d = np.sqrt(B["AABB"].squared_distance(M.V, B["F64"], P)[0]); keep = np.where(d > tol)[0]
    if not len(keep): return 0.0, None
    Pk, dk = P[keep], d[keep]; i = np.clip(np.rint((Pk - M.glo) / M.g).astype(int), 0, np.asarray(M.W.shape) - 1)
    W = M.W[i[:, 0], i[:, 1], i[:, 2]].astype(int); dn = np.linalg.norm(Pk - (M.glo + M.g * i), axis=1)
    amb = np.where(dk <= dn + 1e-9)[0]
    if len(amb): W[amb] = M.winding_at(Pk[amb], dk[amb])
    ins = np.where(W >= 1)[0]
    if not len(ins): return 0.0, None
    j = ins[np.argmax(dk[ins])]
    return (float(dk[j]), int(keep[j])) if dk[j] > tol else (0.0, None)


_MEMO = {}
def frame_depths(info, ok, W, tol, memo=_MEMO):
    """{"A  IN  B": (depth, kind)} for one frame (W = {group: (R, t)}). A pair whose relative pose (B's frame seen from A's,
    to 1e-5) was already measured reuses that answer - the same two rigid shapes in the same relative pose: held frames,
    and parts whose relative joint does not move over a stretch of a clip (the elbow between the cuffs)"""
    out = {}
    for i, j in candidates(info, W, ok, tol):
        A, B = info[i], info[j]; (Ra, ta), (Rb, tb) = W[A["g"]], W[B["g"]]
        key = (int(i), int(j), np.round(np.r_[(Ra.T @ Rb).ravel(), (tb - ta) @ Ra], 5).tobytes())
        if key not in memo:
            if len(memo) > 200000: memo.clear()
            memo[key] = depth_in(A, B, W[A["g"]], W[B["g"]], tol)
        dep, kind = memo[key]
        if dep > tol: out[f"{A['g']}|{A['n']}  IN  {B['g']}|{B['n']}"] = (dep, kind)
    return out


def xforms(fr):
    import scene_export as SE
    X, _ = SE.frame_xforms(fr); return {g: (np.asarray(R, float), np.asarray(t, float)) for g, (R, t) in X.items()}


_G = {}
def _work(item):
    clip, fi, W = item; return clip, fi, frame_depths(_G["info"], _G["ok"], W, _G["tol"])


def run(dd, step=3, tol=0.15, h=1.0, jobs=1, select=None, log=print):
    """the judge on a design dir: returns the part_contact.json dict (select(clip, fi) -> bool limits the frames)"""
    t0 = time.time(); parts = load_parts(dd)
    todo = [(c, fi, xforms(fr)) for c, fi, fr in frames(dd, step) if select is None or select(c, fi)]
    probe = prepare(parts, h, build=set())                                          # samples + boxes, no grids yet
    ok = pair_ok(probe); need = set()
    for _, _, W in todo: need |= {int(j) for _, j in candidates(probe, W, ok, tol)}
    for j in need: build_B(probe[j])                                                  # grids only where a part is ever B
    info = probe; t1 = time.time(); res = {}; nf = 0
    _G.update(info=info, ok=ok, tol=tol)
    with (mp.get_context("fork").Pool(jobs) if jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap(_work, todo, chunksize=2) if pool else map(_work, todo)
        for clip, fi, out in it:                                                     # frame order: same tie-breaking as one process
            nf += 1
            for k, (dep, kind) in out.items():
                r = res.setdefault(k, dict(max_depth=0.0, frames=0, worst=None, worst_point=None, per_frame={}))
                r["frames"] += 1; r["per_frame"][f"{clip}|{fi}"] = round(dep, 2)
                if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi]; r["worst_point"] = kind
    for r in res.values():                                                           # keep the series short: the worst 12 frames
        r["per_frame"] = dict(sorted(r["per_frame"].items(), key=lambda kv: -kv[1])[:12])
    OPEN = [f"{x['g']}|{x['n']}" for x in info if not x["closed"]]
    ns = {f"{x['g']}|{x['n']}": int(len(x["S"])) for x in info}
    return dict(step=step, tol_mm=tol, frames_checked=nf, pairs=int(ok.sum()), seconds=round(time.time() - t0), setup_seconds=round(t1 - t0), jobs=jobs,
                violations=res, open_parts_not_tested_as_container=OPEN,
                samples=dict(h_mm=h, sharp_deg=SHARP_DEG, total=int(sum(ns.values())), per_part=ns,
                             rule="every vertex + sharp/boundary edges at <= h/2 + longest-edge bisection of every face to edges <= h (midpoints)"),
                inside="dense surface samples of A (vertices, sharp edges, faces), both ways; integer winding number on welded tessellations (grid + segment crossings), depth = exact distance (judge/sdist.py)",
                max_depth=max([r["max_depth"] for r in res.values()], default=0.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=3); ap.add_argument("--tol", type=float, default=0.15)
    ap.add_argument("--h", type=float, default=1.0); ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    a = ap.parse_args(); dd = design_dir(a.design)
    out = run(dd, a.step, a.tol, a.h, a.jobs); res = out["violations"]
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "part_contact.json"), "w"), indent=1)
    print(f"part contact: {out['frames_checked']} frames x {out['pairs']} ordered pairs, {out['samples']['total']} surface samples (h {a.h} mm), "
          f"{len(res)} interpenetrating by > {a.tol} mm (worst {out['max_depth']} mm); {len(out['open_parts_not_tested_as_container'])} open parts not usable as containers; {out['seconds']} s")
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["max_depth"])[:15]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames  {k[:110]}  worst {v['worst']} ({v['worst_point']})")
