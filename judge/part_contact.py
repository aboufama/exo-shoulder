"""JUDGE R6: do parts that move relative to each other interpenetrate? For every pair of parts in different motion groups,
every step-th frame: the deepest point of A inside B, both ways (A in B and B in A), by the winding number + exact depth to
B's welded, closed tessellation (judge/sdist.py, validated in judge/test_sdist.py). Geometry only - does not use the
pipeline's member fields. Designed coaxial fits at a shared joint (pin in sleeve, washer on seat) sit within tol.

OPEN parts are containers too (2026-10-16; until then pair_ok() dropped every B that was not watertight, so a pin fully
embedded in a link with a tessellation crack was never seen - the verifier found param_r20's base and link 2 3.49 mm inside
its open link 1, judge/VERIFY_part_contact.md). close_open() makes their oriented 2-chain closed, exactly:
  - edges shared by 4 faces (two bodies meeting on an edge, the RSR3 rails) already form a closed chain: no change;
  - otherwise the boundary of the chain (every directed edge without its reverse: the crack's two lips, T-junctions) is
    split into loops and each loop is capped by ear clipping on the shortest diagonal (the cap zips the crack shut along
    its lips); the cap's own edges cancel the boundary, so the integer winding number of judge/sdist.py applies unchanged,
    and the depth is the exact distance to the capped tessellation. part_contact.json lists every open part and its cap
    (triangles, area, cap_max_dev_mm = the farthest cap point from the open tessellation: ~0 for a crack or T-junction,
    about half the width of a real hole), so a cap that is more than a crack is visible. Measured 2026-10-16: on D5-02,
    D6-03 and D7-03 the capped integer winding number agrees with libigl's generalized winding number of the open
    tessellation on every one of ~35000 random points deeper than 0.15 mm (box + near-surface);
  - a part whose chain still does not close (a non-orientable tessellation) falls back to libigl's exact generalized
    winding number |w| > 0.5 on the open tessellation (igl.winding_number, no grid, no reject mask) - listed as such.
judge/test_part_contact.py: a pin fully embedded in a cracked slab must be caught (exact depth) both ways.

A's points are DENSE SURFACE SAMPLES, not only its vertices (2026-10-16: the vertex-only test, every other vertex at step
12, scored 0.0 mm on the first build of l1_offset-skin-normal-3r while link 2 sat 1.12 mm inside the J3 plate - two thin
plates whose edges cross put no vertex inside each other; judge/test_part_contact.py). Per part, in its own frame, cached:
  - every vertex of the tessellation (the old test, kept),
  - points along every sharp edge (dihedral > SHARP_DEG, and open boundaries) at <= h/2 spacing: where a crossing plate
    pokes through first,
  - every face, refined by longest-edge bisection until no edge is longer than h (default 1.0 mm): the midpoints are the
    samples, so every point of every face lies within h / sqrt(3) of a sample and the count is ~ area / h^2 (area
    weighted, deterministic, no n^2 blow-up on long thin facets).
Speed (the measurement is unchanged by any of it - judge/test_part_contact.py checks the fast path point by point against
sdist's Mesh.max_depth):
  - per frame each part's box is posed (8 corners) and only ordered pairs whose world boxes overlap are tested;
  - A's samples are culled in A's own frame (kd-tree ball around B's box), then to B's box shrunk by tol;
  - an exact reject mask on B's winding grid drops samples well clear of B and outside it (build_B);
  - depth = libigl's AABB closest point (exact); inside = sdist's integer winding number (grid node, plus the segment
    crossings only where the surface is nearer than the node); samples within tol of B's surface are skipped first, so a
    coaxial fit (a whole face seated on B) costs one distance query per sample;
  - a pair seen before in the same relative pose (held frames, a joint that does not move) reuses its answer;
  - samples are cached on disk per part content (.cache/part_contact, git-ignored): the user's parts repeat across designs.
B's grids are built only for parts that are ever B in an overlapping pair.
    python3 judge/part_contact.py <design dir|id> [--step 3] [--tol 0.15] [--h 1.0] [--jobs N]  -> <design>/judge/part_contact.json
--jobs splits the frames over N processes (same measurement, merged in frame order; default min(4, cores)).
Step: default 3 (10 frames per second of the 30 fps clips: a crossing that lasts >= 3 frames, 0.1 s, is always sampled);
tools/judge_all.sh runs every frame (step 1) and step 3 when fast. Measured on the 06b5a59 build of
l1_offset-skin-normal-3r at step 1: link 2 sits 1.07 mm inside the J3 plate at EVERY frame (a fixed overlap at the
joint); link 1 / link 2 cross by up to 0.66 mm for 9 frames (Wave 71-79 and 95-103) and 0.59 mm over Raise overhead 35-145.
"""
import argparse, contextlib, json, multiprocessing as mp, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import design_dir, load_parts, frames
from scipy.spatial import cKDTree
from sdist import Mesh

SHARP_DEG = 30.0
KINDS = ("vertex", "sharp edge", "face")


def weld(V, F):
    """welded tessellation (glb faces are split at B-rep seams): (V, F, watertight, trimesh). A closed tessellation whose
    winding is inconsistent or whose bodies face inward (the band_* D4 member proxies: 3 bodies, all negative volume) is
    re-oriented body by body - outward, consistent - since the grid winding number takes its sign from the face normals
    (2026-10-16: an inverted l1 proxy scored a vertex 3.44 mm 'inside' where the generalized winding number is 0.07).
    The geometry is unchanged; m.metadata["reoriented"] says it happened."""
    import trimesh
    m = trimesh.Trimesh(V, F, process=False); m.merge_vertices(digits_vertex=4); m.update_faces(m.nondegenerate_faces())
    if m.is_watertight and (not m.is_winding_consistent or m.volume < 0 or
                            any(b.volume < 0 for b in m.split(only_watertight=False)) if len(m.faces) else False):
        bodies = []
        for b in m.split(only_watertight=False):
            trimesh.repair.fix_winding(b)
            if b.volume < 0: b.invert()
            bodies.append(b)
        m = trimesh.util.concatenate(bodies); m.metadata["reoriented"] = True
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
                       + np.array([h, sharp_deg, 3.0]).tobytes()).hexdigest()
    f = os.path.join(CACHE, key + ".npz")
    try:
        z = np.load(f); return z["S"], z["kind"]
    except Exception: pass
    S, kind = surface_samples(V, F, h, sharp_deg, m)
    try:
        os.makedirs(CACHE, exist_ok=True); tmp = f"{f}.{os.getpid()}.npz"; np.savez(tmp, S=S, kind=kind); os.replace(tmp, f)
    except Exception: pass
    return S, kind


def prepare(parts, h=1.0, sharp_deg=SHARP_DEG, build=None, open_mode="cap"):
    """per part: group, name, samples (local frame) + kind, local box, open-part info, Mesh of the welded (open: closed by
    close_open) tessellation (B side; grids built for the indices in build, or for every part when build is None)"""
    info = []
    for g, n, V, F in parts:
        Vw, Fw, closed, m = weld(V, F); S, kind = cached_samples(V, F, h, sharp_deg, m); op = None
        if not closed: Vw, Fw, closed, op = close_open(m, open_mode)                # A side keeps the original surface
        lo, hi = S.min(0), S.max(0)
        info.append(dict(g=g, n=n, S=S, kind=kind, closed=closed, open=op, reoriented=bool(m.metadata.get("reoriented")), M=Mesh(Vw, Fw), lo=lo, hi=hi,
                         C=np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])))
    for i, x in enumerate(info):
        if build is None or i in build: build_B(x)
    return info


def _directed_boundary(F, nv):
    """the boundary of an oriented 2-chain: directed edges (a, b) with multiplicity #(a->b) - #(b->a) > 0, repeated"""
    d = np.asarray(F)[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2).astype(np.int64)
    k, c = np.unique(d[:, 0] * nv + d[:, 1], return_counts=True); cnt = dict(zip(k.tolist(), c.tolist()))
    out = []
    for key, c in cnt.items():
        a, b = divmod(key, nv); net = c - cnt.get(b * nv + a, 0)
        out += [(a, b)] * max(net, 0)
    return out


def close_open(m, mode="cap"):
    """(V, F, container?, info) for a welded tessellation trimesh does not call watertight (see the module doc). mode "cap":
    orient consistently (trimesh fix_winding), cap every boundary loop of the oriented chain by ear clipping on the shortest
    diagonal, check the chain closes and points outward; "gwn" (or a chain that does not close): the open tessellation, as is,
    tested with the generalized winding number. info: what was done, for part_contact.json"""
    import trimesh, igl
    w = m.copy(); V = np.asarray(w.vertices, float)
    e = np.sort(np.asarray(w.faces)[:, [0, 1, 1, 2, 2, 0]].reshape(-1, 2), 1); _, ec = np.unique(e, axis=0, return_counts=True)
    info = dict(open_edges=int((ec == 1).sum()), nonmanifold_edges=int((ec > 2).sum()), faces=int(len(w.faces)))
    if not w.is_winding_consistent: trimesh.repair.fix_winding(w); info["winding_fixed"] = True
    F = np.asarray(w.faces); bd = _directed_boundary(F, len(V))
    info["boundary_edges"] = len(bd); info["boundary_length_mm"] = round(float(sum(np.linalg.norm(V[a] - V[b]) for a, b in bd)), 2)
    cap = []
    if mode == "cap" and bd:
        out = {}
        for a, b in bd: out.setdefault(a, []).append(b)
        loops = []
        while out:                                                                    # Euler: in = out at every vertex of a chain boundary
            a0 = next(iter(out)); L = [a0]; a = a0
            while True:
                b = out[a].pop()
                if not out[a]: del out[a]
                if b == a0: break
                L.append(b); a = b
                if a not in out: L = None; break                                      # unbalanced: not an oriented chain
            if L is None: loops = None; break
            loops.append(L)
        if loops is not None:
            for L in loops:                                                           # the cap runs the loop backwards: its edges cancel the lips
                P = list(L[::-1])
                while len(P) > 3:
                    n_ = len(P); i = int(np.argmin([np.linalg.norm(V[P[(j - 1) % n_]] - V[P[(j + 1) % n_]]) for j in range(n_)]))
                    cap.append((P[(i - 1) % n_], P[i], P[(i + 1) % n_])); del P[i]
                if len(P) == 3: cap.append(tuple(P))
            info["loops"] = len(loops)
    Fc = np.r_[F, np.asarray(cap, int).reshape(-1, 3)]
    closed = not _directed_boundary(Fc, len(V))
    if mode == "cap" and closed:
        vol = trimesh.Trimesh(V, Fc, process=False).volume
        if vol < 0: Fc = Fc[:, ::-1]; info["inverted"] = True
        info.update(how="closed chain: " + (f"{len(cap)} cap triangles over {info.get('loops', 0)} boundary loops (ear clipping, shortest diagonal), "
                                             "integer winding number + exact depth to the capped tessellation" if cap else
                                             "no boundary (non-manifold edges only), integer winding number + exact depth as is"))
        if cap:
            C = trimesh.Trimesh(V, np.asarray(cap, int), process=False); info["cap_triangles"] = len(cap); info["cap_area_mm2"] = round(float(C.area), 4)
            S, _ = surface_samples(V, np.asarray(cap, int), 0.05, 180.0, C)
            info["cap_max_dev_mm"] = round(float(np.sqrt(igl.point_mesh_squared_distance(S, V, np.ascontiguousarray(F, np.int64))[0].max())), 4)
        return V, Fc, True, info
    info["how"] = "generalized winding number |w| > 0.5 (libigl, exact) + exact depth to the open tessellation (no grid)"
    return V, F, True, dict(info, gwn=True)


def build_B(x):
    """B side of a part: the winding-number grid (judge/sdist.py) plus a reject mask on its nodes, OUT = winding 0 and no
    surface within the segment to any point that rounds to the node. Bound: a node with no Mesh sample marked within k
    nodes (chessboard) is farther than k g - g sqrt(3)/2 - M.h from the surface (each sample lies within g sqrt(3)/2 of
    its node; Mesh.S covers the surface within M.h); with k g > M.h + g sqrt(3) that exceeds |P - node| <= g sqrt(3)/2,
    so the segment node -> P crosses nothing and P is outside like the node. Exact, never a guess: it only spares the
    kd-tree and the segment crossings for A's samples well clear of B."""
    from scipy.ndimage import maximum_filter
    import igl
    M = x["M"]; x["gwn"] = bool((x.get("open") or {}).get("gwn"))
    if x["gwn"]:                                                                      # open fallback: no grid, no reject mask
        x["F64"] = np.ascontiguousarray(M.F, np.int64); M.V = np.ascontiguousarray(M.V, float)
        x["AABB"] = igl.AABB(); x["AABB"].init(M.V, x["F64"]); return x
    if not hasattr(M, "W"): M.build_grid()
    n = np.asarray(M.W.shape); idx = np.clip(np.rint((M.S - M.glo) / M.g).astype(int), 0, n - 1)
    mark = np.zeros(M.W.shape, np.uint8); mark[idx[:, 0], idx[:, 1], idx[:, 2]] = 1
    k = int(np.floor((M.h + M.g * np.sqrt(3)) / M.g)) + 1
    x["OUT"] = (maximum_filter(mark, size=2 * k + 1, mode="constant") == 0) & (M.W == 0)
    x["F64"] = np.ascontiguousarray(M.F, np.int64); M.V = np.ascontiguousarray(M.V, float)
    x["AABB"] = igl.AABB(); x["AABB"].init(M.V, x["F64"])
    return x


def pair_ok(info):
    """(n, n) bool: ordered pairs (A, B) that are tested - different motion groups (every B is a container: close_open)"""
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
    M = B["M"]
    if not B.get("gwn"):
        i = np.clip(np.rint((P - M.glo) / M.g).astype(int), 0, np.asarray(M.W.shape) - 1)
        k = ~B["OUT"][i[:, 0], i[:, 1], i[:, 2]]; m, P = m[k], P[k]                   # exact reject: well clear of B, outside
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
    Pk, dk = P[keep], d[keep]
    if B.get("gwn"):                                                                  # open tessellation: generalized winding number
        import igl
        ins = np.where(np.abs(igl.winding_number(M.V, B["F64"], np.ascontiguousarray(Pk, float))) > 0.5)[0]
    else:
        i = np.clip(np.rint((Pk - M.glo) / M.g).astype(int), 0, np.asarray(M.W.shape) - 1)
        W = M.W[i[:, 0], i[:, 1], i[:, 2]].astype(int); dn = np.linalg.norm(Pk - (M.glo + M.g * i), axis=1)
        amb = np.where(dk <= dn + 1e-9)[0]
        if len(amb): W[amb] = M.winding_at(Pk[amb], dk[amb])
        ins = np.where(W >= 1)[0]
    if not len(ins): return 0.0, None
    j = ins[np.argmax(dk[ins])]
    return (float(dk[j]), int(keep[j])) if dk[j] > tol else (0.0, None)


def frame_depths(info, ok, W, tol, memo=None):
    """{"A  IN  B": (depth, kind)} for one frame (W = {group: (R, t)}). A pair whose relative pose (B's frame seen from A's,
    to 1e-5) was already measured reuses that answer - the same two rigid shapes in the same relative pose: held frames,
    and parts whose relative joint does not move over a stretch of a clip (the elbow between the cuffs)"""
    out = {}
    for i, j in candidates(info, W, ok, tol):
        A, B = info[i], info[j]; (Ra, ta), (Rb, tb) = W[A["g"]], W[B["g"]]
        key = (int(i), int(j), np.round(np.r_[(Ra.T @ Rb).ravel(), (tb - ta) @ Ra], 5).tobytes())
        if memo is None: dep, kind = depth_in(A, B, W[A["g"]], W[B["g"]], tol)
        else:
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
    clip, fi, W = item; c0 = time.process_time(); out = frame_depths(_G["info"], _G["ok"], W, _G["tol"], _G["memo"])
    return clip, fi, out, time.process_time() - c0


def run(dd, step=3, tol=0.15, h=1.0, jobs=1, select=None, log=print, open_mode="cap"):
    """the judge on a design dir: returns the part_contact.json dict (select(clip, fi) -> bool limits the frames)"""
    t0 = time.time(); c0 = time.process_time(); parts = load_parts(dd)
    todo = [(c, fi, xforms(fr)) for c, fi, fr in frames(dd, step) if select is None or select(c, fi)]
    probe = prepare(parts, h, build=set(), open_mode=open_mode)                      # samples + boxes, no grids yet
    ok = pair_ok(probe); need = set()
    for _, _, W in todo: need |= {int(j) for _, j in candidates(probe, W, ok, tol)}
    for j in need: build_B(probe[j])                                                  # grids only where a part is ever B
    info = probe; t1 = time.time(); cpu = cs = time.process_time() - c0; res = {}; nf = 0
    _G.update(info=info, ok=ok, tol=tol, memo={})                                    # the memo is per run (keys are part indices)
    with (mp.get_context("fork").Pool(jobs) if jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap(_work, todo, chunksize=2) if pool else map(_work, todo)
        for clip, fi, out, c in it:                                                  # frame order: same tie-breaking as one process
            nf += 1; cpu += c
            for k, (dep, kind) in out.items():
                r = res.setdefault(k, dict(max_depth=0.0, frames=0, worst=None, worst_point=None, per_frame={}))
                r["frames"] += 1; r["per_frame"][f"{clip}|{fi}"] = round(dep, 2)
                if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi]; r["worst_point"] = kind
    for r in res.values():                                                           # keep the series short: the worst 12 frames
        r["per_frame"] = dict(sorted(r["per_frame"].items(), key=lambda kv: -kv[1])[:12])
    OPEN = [f"{x['g']}|{x['n']}" for x in info if not x["closed"]]                  # none since close_open (kept for readers)
    ns = {f"{x['g']}|{x['n']}": int(len(x["S"])) for x in info}
    return dict(step=step, tol_mm=tol, frames_checked=nf, pairs=int(ok.sum()), seconds=round(time.time() - t0), setup_seconds=round(t1 - t0), jobs=jobs,
                cpu_seconds=round(cpu), cpu_s_per_frame=round((cpu - cs) / max(nf, 1), 3),
                violations=res, open_parts_not_tested_as_container=OPEN,
                open_parts={f"{x['g']}|{x['n']}": x["open"] for x in info if x["open"]},
                reoriented_parts=[f"{x['g']}|{x['n']}" for x in info if x.get("reoriented")],
                samples=dict(h_mm=h, sharp_deg=SHARP_DEG, total=int(sum(ns.values())), per_part=ns,
                             rule="every vertex + sharp/boundary edges at <= h/2 + longest-edge bisection of every face to edges <= h (midpoints)"),
                inside="dense surface samples of A (vertices, sharp edges, faces), both ways; integer winding number on welded tessellations (judge/sdist.py grid + segment crossings), depth = exact distance to B's closest point (libigl AABB)",
                max_depth=max([r["max_depth"] for r in res.values()], default=0.0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=3); ap.add_argument("--tol", type=float, default=0.15)
    ap.add_argument("--h", type=float, default=1.0); ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    a = ap.parse_args(); dd = design_dir(a.design)
    out = run(dd, a.step, a.tol, a.h, a.jobs); res = out["violations"]
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "part_contact.json"), "w"), indent=1)
    print(f"part contact: {out['frames_checked']} frames x {out['pairs']} ordered pairs, {out['samples']['total']} surface samples (h {a.h} mm), "
          f"{len(res)} interpenetrating by > {a.tol} mm (worst {out['max_depth']} mm); {len(out['open_parts'])} open parts closed as containers "
          f"({len(out['open_parts_not_tested_as_container'])} not usable); {out['seconds']} s")
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["max_depth"])[:15]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames  {k[:110]}  worst {v['worst']} ({v['worst_point']})")
