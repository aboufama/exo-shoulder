"""Rig helpers for build_body.py: harmonic skin weights, centre-of-rotation skinning data, muscle volume models.

  * harmonic(): bone-seeded weights solved exactly (sparse Laplace solve, cotangent weights), so no region keeps an
    unconverged guess (the old 700-step diffusion left the groin and belly partly on the scapula).
  * cor_centres(): per-vertex centres of rotation (Le & Hodgins 2016, "Real-time skeletal skinning with optimized
    centers of rotation"). At run time a vertex is turned by the quaternion blend of its bones about its centre, and the
    centre itself is moved by linear blending: no LBS collapse (thin "web" at the axilla, pinched elbow) and no DQS bulge.
  * fusiform(): centreline model for spindle muscles (biceps, brachialis, brachioradialis, triceps, ...). The vertex
    is stored as (arc length s along the rest centreline, offset in the centreline frame). At run time the posed
    centreline length change goes into the fleshy belly only (tendons inextensible), each slice keeps its volume, and
    the extra cross-section is put mostly into the superficial side (away from the bone): the belly shortens toward
    its origin, thickens and peaks.
  * sheet(): flat muscles (deltoid, pectoralis major, latissimus, ...) keep volume by thickening the superficial face
    with the local fibre stretch, measured on the posed mesh between two vertices along the fibre.
"""
import math
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import splu
from scipy.spatial import cKDTree


def components(F, n):
    r = np.r_[F[:, 0], F[:, 1], F[:, 2]]; c = np.r_[F[:, 1], F[:, 2], F[:, 0]]
    return connected_components(coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)), directed=False)


def outer_shell(V, F):
    """Vertex mask of the outward-facing closed shells (BodyParts3D skin is a 3 mm thick solid: outer + inner shell;
    the inner one has inward normals, i.e. negative signed volume)."""
    nc, lab = components(F, len(V))
    sv = np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])) / 6
    vol = np.zeros(nc); np.add.at(vol, lab[F[:, 0]], sv)
    return (vol > 0.2 * vol.max())[lab]


def drop_debris(V, F, min_verts=12):
    """Remove tiny closed islands left by decimation (3-6 vertex tetrahedra)."""
    nc, lab = components(F, len(V)); cnt = np.bincount(lab, minlength=nc)
    keep = cnt[lab] >= min(min_verts, cnt.max())
    fm = keep[F].all(1); idx = np.flatnonzero(keep); remap = -np.ones(len(V), int); remap[idx] = np.arange(len(idx))
    return V[idx], remap[F[fm]]


def cotan_matrix(V, F):
    I, J, X = [], [], []
    for k in range(3):
        i, j, o = F[:, k], F[:, (k + 1) % 3], F[:, (k + 2) % 3]
        u, v = V[i] - V[o], V[j] - V[o]
        cot = (u * v).sum(1) / (np.linalg.norm(np.cross(u, v), axis=1) + 1e-12)
        I.append(i); J.append(j); X.append(0.5 * cot)
    I, J, X = np.concatenate(I), np.concatenate(J), np.concatenate(X)
    M = coo_matrix((X, (I, J)), shape=(len(V), len(V))).tocsr(); M = (M + M.T).tocsr()
    M.data = np.maximum(M.data, 0.02 * np.abs(M.data).mean())         # obtuse triangles: keep weights positive
    return M


def laplacian(V, F):
    M = cotan_matrix(V, F); return diags(np.asarray(M.sum(1)).ravel()) - M, M


def harmonic(V, F, seed, seedW):
    """W with Laplace(W) = 0 off the seeds and W = seedW on them (rows sum to 1). Components without seeds -> col 0."""
    n = len(V); L, _ = laplacian(V, F); seed = seed.copy(); W = np.zeros((n, seedW.shape[1])); W[seed] = seedW[seed]
    nc, lab = components(F, n)
    for k in range(nc):
        m = lab == k
        if not seed[m].any(): W[m, 0] = 1; seed |= m
    free = ~seed
    if free.any():
        Lr = L.tocsr(); Lff = Lr[free][:, free].tocsc(); Lfs = Lr[free][:, seed]
        W[free] = splu(Lff).solve(np.asarray(-(Lfs @ W[seed])))
    W = np.clip(W, 0, None); return W / (W.sum(1, keepdims=True) + 1e-12)


def topk(W, k=4):
    """indices (n,k) uint8 and weights (n,k) uint8 summing to 255"""
    idx = np.argsort(-W, 1)[:, :k]; w = np.take_along_axis(W, idx, 1); w = w / (w.sum(1, keepdims=True) + 1e-12)
    q = np.floor(w * 255).astype(int); r = 255 - q.sum(1); q[:, 0] += r
    return idx.astype(np.uint8), q.astype(np.uint8)


def smooth_field(X, A, it, mask=None):
    for _ in range(it):
        Y = 0.5 * X + 0.5 * (A @ X)
        X = Y if mask is None else np.where(mask[:, None] if X.ndim == 2 else mask, Y, X)
    return X


def cor_centres(V, F, W, A=None, sigma=0.1, tol=0.995, nsamp=16000, seed=0, smooth_it=6):
    """Optimised centres of rotation (Le & Hodgins 2016). W: (n, nb) weights. Rigid vertices keep C = V (-> LBS)."""
    n, nb = W.shape; C = V.astype(float).copy()
    need = W.max(1) < tol
    if not need.any(): return C
    At = 0.5 * np.linalg.norm(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]), axis=1)
    Wt = W[F].mean(1); Ct = V[F].mean(1)
    ti = np.flatnonzero((Wt.max(1) < tol) & (At > 0))
    if len(ti) == 0: return C
    aw = At[ti]
    if len(ti) > nsamp:
        rng = np.random.default_rng(seed); ti = rng.choice(ti, nsamp, replace=False, p=aw / aw.sum()); aw = np.ones(len(ti))
    Wt, Ct = Wt[ti], Ct[ti]
    pairs = [(a, b) for a in range(nb) for b in range(a + 1, nb) if (Wt[:, a] * Wt[:, b]).max() > 1e-6]
    Q, inv = np.unique(np.round(W[need], 2), axis=0, return_inverse=True); inv = inv.ravel()
    out = np.zeros((len(Q), 3)); ok = np.zeros(len(Q), bool)
    for lo in range(0, len(Q), 256):
        q = Q[lo:lo + 256]; S = np.zeros((len(q), len(ti)))
        for a, b in pairs:
            qa, qb = q[:, a:a + 1], q[:, b:b + 1]
            if (qa * qb).max() < 1e-6: continue
            ta, tb = Wt[None, :, a], Wt[None, :, b]
            S += qa * qb * ta * tb * np.exp(-((qa * tb - qb * ta) ** 2) / sigma ** 2)
        S *= aw[None]; den = S.sum(1)
        out[lo:lo + 256] = (S @ Ct) / np.maximum(den, 1e-30)[:, None]; ok[lo:lo + 256] = den > 1e-9
    ids = np.flatnonzero(need)
    C[ids[ok[inv]]] = out[inv][ok[inv]]
    if A is not None and smooth_it:                       # quantised weights -> smooth the centre field on the mesh
        C = smooth_field(C, A, smooth_it, mask=need)
    return C


def vertex_normals(V, F):
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); vn = np.zeros_like(V)
    for k in range(3): np.add.at(vn, F[:, k], fn)
    return vn / (np.linalg.norm(vn, axis=1, keepdims=True) + 1e-12)


def _frames(C):
    """tangents of a polyline (central differences)"""
    T = np.gradient(C, axis=0); return T / (np.linalg.norm(T, axis=1, keepdims=True) + 1e-12)


def _interp_frame(s, sk, Ck, Tk, Ek):
    """position + orthonormal frame at arc lengths s on the node polyline (same maths as body.js)"""
    k = np.clip(np.searchsorted(sk, s) - 1, 0, len(sk) - 2); u = np.clip((s - sk[k]) / (sk[k + 1] - sk[k] + 1e-12), 0, 1)[:, None]
    P = Ck[k] * (1 - u) + Ck[k + 1] * u
    t = Tk[k] * (1 - u) + Tk[k + 1] * u; t /= np.linalg.norm(t, axis=1, keepdims=True)
    e = Ek[k] * (1 - u) + Ek[k + 1] * u; e -= (e * t).sum(1, keepdims=True) * t; e /= np.linalg.norm(e, axis=1, keepdims=True)
    return P, t, e, np.cross(t, e)


def fusiform(V, F, W, O, I, bone_tree, K=18):
    """Centreline model. O, I: origin / insertion attachment centres (rest). Returns dict for export."""
    u = I - O; t = (V - O) @ u / (u @ u)
    lo, hi = np.percentile(t, 0.5), np.percentile(t, 99.5)
    edges = np.linspace(lo, hi, K + 1); b = np.clip(np.searchsorted(edges, t) - 1, 0, K - 1)
    Ck = np.array([V[b == k].mean(0) if (b == k).any() else O + u * (edges[k] + edges[k + 1]) / 2 for k in range(K)])
    for _ in range(2): Ck[1:-1] = 0.25 * Ck[:-2] + 0.5 * Ck[1:-1] + 0.25 * Ck[2:]
    # end nodes pushed out to the extreme vertices along the axis, so the slices cover the muscle
    d0 = _frames(Ck)[0]; d1 = _frames(Ck)[-1]
    Ck[0] = Ck[0] + d0 * min(0.0, ((V - Ck[0]) @ d0).min()); Ck[-1] = Ck[-1] + d1 * max(0.0, ((V - Ck[-1]) @ d1).max())
    sk = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Ck, axis=0), axis=1))]; L0 = sk[-1]
    Tk = _frames(Ck)
    # outward (superficial) direction: away from the nearest bone
    _, bi = bone_tree.query(Ck, k=24); Bc = bone_tree.data[bi].mean(1)
    Ek = Ck - Bc; Ek -= (Ek * Tk).sum(1, keepdims=True) * Tk
    for _ in range(3): Ek[1:-1] = 0.25 * Ek[:-2] + 0.5 * Ek[1:-1] + 0.25 * Ek[2:]
    Ek -= (Ek * Tk).sum(1, keepdims=True) * Tk; Ek /= np.linalg.norm(Ek, axis=1, keepdims=True) + 1e-12
    # vertex arc length: closest point on the polyline
    best = np.full(len(V), np.inf); s = np.zeros(len(V))
    for k in range(K - 1):
        a, d = Ck[k], Ck[k + 1] - Ck[k]; tt = np.clip((V - a) @ d / (d @ d), 0, 1)
        dist = np.linalg.norm(V - (a + tt[:, None] * d), axis=1); m = dist < best; best[m] = dist[m]; s[m] = sk[k] + tt[m] * (sk[k + 1] - sk[k])
    P, tv, ev, bv = _interp_frame(s, sk, Ck, Tk, Ek)
    R = V - P; X = np.c_[(R * tv).sum(1), (R * ev).sum(1), (R * bv).sum(1)]          # (x_t, x_e, x_b)
    # cross-section area profile -> fleshy-belly density (tendons ~ 0)
    kv = np.clip(np.searchsorted(sk, s) - 1, 0, K - 2); kv = np.where(s - sk[kv] > sk[kv + 1] - s, kv + 1, kv)
    # thickness = the smaller cross-section extent (a flat or fanning tendon is wide but thin)
    thick = np.zeros(K)
    for k in range(K):
        m = kv == k
        if m.sum() >= 4:
            re = np.percentile(X[m, 1], 95) - np.percentile(X[m, 1], 5); rb = np.percentile(X[m, 2], 95) - np.percentile(X[m, 2], 5)
            thick[k] = min(re, rb)
    thick[[0, -1]] = 0                                      # end slices are attachment caps
    thick = np.convolve(np.r_[thick[0], thick, thick[-1]], [0.25, 0.5, 0.25], "valid")
    phi = np.clip((thick / (thick.max() + 1e-9) - 0.3) / 0.45, 0, 1) ** 0.75
    km = int(np.argmax(thick)); lo_, hi_ = km, km                   # keep the one contiguous belly around the thickest slice
    while lo_ > 0 and phi[lo_ - 1] > 0: lo_ -= 1
    while hi_ < K - 1 and phi[hi_ + 1] > 0: hi_ += 1
    phi[:lo_] = 0; phi[hi_ + 1:] = 0
    # node weights: mean of the slice's vertex weights (for the node frame rotation)
    NW = np.array([W[kv == k].mean(0) if (kv == k).any() else W[np.argmin(np.abs(s - sk[k]))] for k in range(K)])
    # model weight: 1 in the span, fading at the attachment caps (there the vertices follow their bones)
    cap = 0.06 * L0
    mu = np.clip(np.minimum(s, L0 - s) / cap, 0, 1); mu = mu * mu * (3 - 2 * mu)
    # radial table for the skin height field: outer radius per node and 16 angles
    ang = np.arctan2(X[:, 2], X[:, 1]); aj = ((ang + math.pi) / (2 * math.pi) * 16).astype(int) % 16
    rad = np.hypot(X[:, 1], X[:, 2]); RT = np.zeros((K, 16))
    for k in range(K):
        for j in range(16):
            m = (kv == k) & (aj == j); RT[k, j] = rad[m].max() if m.any() else 0
    for k in range(K):                                     # fill empty bins from angular neighbours
        r = RT[k]
        if (r > 0).any():
            for j in np.flatnonzero(r == 0):
                nz = np.flatnonzero(r > 0); dj = np.minimum(np.abs(nz - j), 16 - np.abs(nz - j)); RT[k, j] = r[nz[np.argmin(dj)]]
    return dict(K=K, sk=sk, Ck=Ck, Tk=Tk, Ek=Ek, phi=phi, NW=NW, L0=L0, s=s, X=X, mu=mu, RT=RT, kv=kv)


def sheet(V, F, I, bone_tree, th, belly):
    """Flat-muscle data: superficial factor, fibre probe pair per vertex (along the direction to the insertion)."""
    vn = vertex_normals(V, F)
    _, bi = bone_tree.query(V); away = V - bone_tree.data[bi]; away /= np.linalg.norm(away, axis=1, keepdims=True) + 1e-12
    c = (vn * away).sum(1); sup = np.clip((c + 0.15) / 0.55, 0, 1); sup = sup * sup * (3 - 2 * sup)
    d = I - V; d -= (d * vn).sum(1, keepdims=True) * vn; d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-12
    tree = cKDTree(V); pf = np.zeros(len(V), int); pb = np.zeros(len(V), int)
    nb = tree.query_ball_point(V, r=30.0)
    for i in range(len(V)):
        j = np.array(nb[i]);
        if len(j) < 3: pf[i] = pb[i] = i; continue
        r = V[j] - V[i]; dist = np.linalg.norm(r, axis=1) + 1e-9; al = (r @ d[i]) / dist
        ok = (dist > 8) & ((vn[j] @ vn[i]) > 0.3)
        sc_f = np.where(ok & (al > 0.75), dist * al, -1); sc_b = np.where(ok & (al < -0.75), -dist * al, -1)
        pf[i] = j[np.argmax(sc_f)] if sc_f.max() > 0 else i; pb[i] = j[np.argmax(sc_b)] if sc_b.max() > 0 else i
    l0 = np.linalg.norm(V[pf] - V[pb], axis=1)
    bad = l0 < 6; pf[bad] = pb[bad] = np.arange(len(V))[bad]; l0[bad] = 1
    return dict(nrm=vn, sup=sup, pf=pf, pb=pb, l0=l0, th=th, belly=belly)


def submesh(V, F, mask):
    """vertices / faces of the masked part; idx = original vertex ids"""
    fm = mask[F].all(1); idx = np.flatnonzero(mask); remap = -np.ones(len(V), int); remap[idx] = np.arange(len(idx))
    return V[idx], remap[F[fm]], idx


def vertex_neighbours_(F, n):
    r = np.r_[F[:, 0], F[:, 1], F[:, 2], F[:, 1], F[:, 2], F[:, 0]]; c = np.r_[F[:, 1], F[:, 2], F[:, 0], F[:, 0], F[:, 1], F[:, 2]]
    A = coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr(); A.data[:] = 1
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    return diags(1 / deg) @ A


def dual_edges(F):
    """interior edges: (face a, face b, vertex i, vertex j)"""
    nF = len(F); E = np.sort(np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], 1); fid = np.tile(np.arange(nF), 3)
    o = np.lexsort((E[:, 1], E[:, 0])); E, fid = E[o], fid[o]
    i = np.flatnonzero((E[1:] == E[:-1]).all(1)); return fid[i], fid[i + 1], E[i]


def _bilaplace_fill(V, F, free, it_fix=None):
    """solve L^2 X = 0 for the free vertices (cotangent Laplacian with area normalisation), others fixed"""
    from scipy.sparse import diags as _diags
    L, _ = laplacian(V, F); Ar = np.zeros(len(V))
    A_ = 0.5 * np.linalg.norm(np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]), axis=1)
    for k in range(3): np.add.at(Ar, F[:, k], A_ / 3)
    Ar = np.maximum(Ar, Ar[Ar > 0].mean() * 0.1 if (Ar > 0).any() else 1)
    M = (L.T @ _diags(1 / Ar) @ L).tocsr(); fr = np.flatnonzero(free); fx = np.flatnonzero(~free)
    X = V.copy()
    if len(fr): X[fr] = splu(M[fr][:, fr].tocsc()).solve(np.asarray(-(M[fr][:, fx] @ V[fx])))
    return X


def unzip_axilla(V, F, trees, H):
    """BodyParts3D's hanging right arm is fused to the chest wall below the armpit: the arm and trunk surfaces meet in
    two sharp creases (anterior / posterior junction) and the medial arm and lateral chest wall between them do not
    exist. Raising the arm stretches that seam into a membrane. Here the creases are found by a min-cut on the faces
    (cheap along concave creases), cut open below the axillary dome, and the opening is closed by a thin pocket: an
    arm half (medial arm surface) and a trunk half (lateral chest wall) meeting in a ridge at the top. At rest the
    pocket lies inside the contact, so the visible rest surface is unchanged. Returns (V2, F2, src) with src = the
    source vertex of every new vertex (-1 for pocket interior), new vertices appended after the old ones."""
    from scipy.sparse import csr_matrix as _csr
    from scipy.sparse.csgraph import maximum_flow, breadth_first_order
    nF = len(F); C = V[F].mean(1)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
    f1, f2, ed = dual_edges(F)
    Le = np.linalg.norm(V[ed[:, 0]] - V[ed[:, 1]], axis=1); d = C[f2] - C[f1]; d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-12
    th = np.arccos(np.clip((fn[f1] * fn[f2]).sum(1), -1, 1)); concave = (fn[f1] * d).sum(1) > 0
    cap = np.maximum(1, np.round(Le * np.where(concave, 0.02 + 0.98 * np.clip(1 - th / 0.35, 0, 1), 1.0) * 100)).astype(np.int32)
    h = H / 325.0                                          # thresholds tuned on the average body, scaled by humerus length
    dh = trees["H"].query(C)[0]; y, z, x = C[:, 1], C[:, 2], C[:, 0]
    src = ((y < -262 * h) & (y > -330 * h) & (z > 5 * h)) | ((z > 45 * h) & (y < -60 * h) & (y > -262 * h) & (dh < 55 * h))
    snk = ((z < -45 * h) & (y < 60 * h) & (y > -400 * h)) | ((y < -262 * h) & (y > -330 * h) & (z < -25 * h)) | \
          ((x > 75 * h) & (z < 15 * h) & (y < -30 * h)) | ((x < -95 * h) & (z < 15 * h) & (y < -30 * h))
    snk &= ~src
    S_, T_ = nF, nF + 1
    rows = np.r_[f1, f2, np.full(src.sum(), S_), np.flatnonzero(snk)]; cols = np.r_[f2, f1, np.flatnonzero(src), np.full(snk.sum(), T_)]
    G = _csr((np.r_[cap, cap, np.full(src.sum() + snk.sum(), 10 ** 6)].astype(np.int32), (rows, cols)), shape=(nF + 2, nF + 2))
    res = maximum_flow(G, S_, T_); Rg = G - res.flow; Rg.data = (Rg.data > 0).astype(np.int32); Rg.eliminate_zeros()
    A = np.zeros(nF + 2, bool); A[breadth_first_order(Rg, S_, directed=True, return_predecessors=False)] = True; A = A[:nF]
    cut = A[f1] != A[f2]
    # unzip the sharp part of the junction, below the dome
    ytop = -95 * h
    uz = cut & (V[ed[:, 0], 1] < ytop) & (V[ed[:, 1], 1] < ytop)
    ue = ed[uz]
    if len(ue) < 6: return V, F, np.arange(len(V)), None, np.zeros_like(V), np.zeros((0, 2), int)
    # order the unzip edges into one path; its two ends stay shared (the cut goes on upward from there)
    from collections import defaultdict
    adj = defaultdict(list)
    for a, b in ue: adj[a].append(b); adj[b].append(a)
    ends = [v for v, nb in adj.items() if len(nb) == 1]
    if len(ends) != 2 or any(len(nb) > 2 for nb in adj.values()): return V, F, np.arange(len(V)), None, np.zeros_like(V), np.zeros((0, 2), int)
    path = [ends[0]]
    while len(path) < len(adj):
        nxt = [v for v in adj[path[-1]] if v not in path[-2:]]; path.append(nxt[0])
    path = np.array(path)
    inner = path[1:-1]; n0 = len(V)
    dup = {v: n0 + k for k, v in enumerate(inner)}
    F2 = F.copy()
    for fi in np.flatnonzero(A):
        for k in range(3):
            if F2[fi, k] in dup: F2[fi, k] = dup[F2[fi, k]]
    Vx = [V, V[inner]]; src_ = list(range(n0)) + list(inner)
    # pocket built from horizontal-ish rungs between the anterior and posterior chains (merged by height, bottom up):
    # the arm half follows a round arc about the humerus (the uncompressed medial arm), the trunk half a gentle
    # lateral bulge (the chest wall); they meet in a ridge (the floor of the axillary dome) at the top
    iB = int(np.argmin(V[path, 1])); up_a = path[iB::-1]; up_p = path[iB:]
    rungs = [(up_a[0], up_p[0])]; ia = ip = 0
    while ia < len(up_a) - 1 or ip < len(up_p) - 1:
        if ip >= len(up_p) - 1 or (ia < len(up_a) - 1 and V[up_a[ia + 1], 1] <= V[up_p[ip + 1], 1]): ia += 1
        else: ip += 1
        rungs.append((up_a[ia], up_p[ip]))
    el = np.median(Le); chord = max(np.linalg.norm(V[a] - V[b]) for a, b in rungs)
    M = int(np.clip(round(chord / (1.3 * el)), 3, 30))
    hum = trees["H"].data; hc = hum.mean(0); hd = np.linalg.eigh(np.cov((hum - hc).T))[1][:, -1]
    def axis_at(yv):                                       # humerus axis point at height yv
        t = (yv - hc[1]) / hd[1]; return hc + t * hd
    tau = (np.arange(1, M + 1) / (M + 1))
    nxt_id = n0 + len(inner); Vx2 = []; src2 = []
    def new_ids(k):
        nonlocal nxt_id
        ids = np.arange(nxt_id, nxt_id + k); nxt_id += k; return ids
    Pa_, Pb_ = V[rungs[-1][0]], V[rungs[-1][1]]
    anchor = []
    ridge_ids = new_ids(M); ridge_pos = Pa_[None] + tau[:, None] * (Pb_ - Pa_)[None]
    Vx2.append(ridge_pos); src2 += [-1] * M
    faces = [F2]; half_int = {}
    for side in ("arm", "trunk"):
        cp = (lambda v: dup.get(v, v)) if side == "arm" else (lambda v: v)
        rows_ = []
        for r, (a, b) in enumerate(rungs):
            if r == len(rungs) - 1: rows_.append(np.r_[cp(a), ridge_ids, cp(b)]); continue
            if a == b: rows_.append(np.r_[cp(a), np.full(M, -1), cp(b)]); continue
            Pa, Pb = V[a], V[b]; lin = Pa[None] + tau[:, None] * (Pb - Pa)[None]
            yv = 0.5 * (Pa[1] + Pb[1]); top = np.clip((V[rungs[-1][0], 1] + V[rungs[-1][1], 1]) / 2 - yv, 0, None)
            fade = np.clip(top / (25 * h), 0, 1); fade = fade * fade * (3 - 2 * fade)
            if side == "arm":                              # polar arc about the humerus axis, through the medial side
                c0 = axis_at(yv); ra, rb = Pa - c0, Pb - c0; ra[1] = rb[1] = 0
                ta, tb = math.atan2(ra[0], ra[2]), math.atan2(rb[0], rb[2])
                # go the way round that passes the medial side (-z, i.e. angle near +-pi)
                d1 = (tb - ta) % (2 * math.pi); d2 = d1 - 2 * math.pi
                d_ = d1 if math.cos(ta + d1 / 2) < math.cos(ta + d2 / 2) else d2
                ang = ta + tau * d_; rr_ = np.linalg.norm(ra) + tau * (np.linalg.norm(rb) - np.linalg.norm(ra))
                arc = np.c_[c0[2] * 0 + rr_ * np.sin(ang) + c0[0], lin[:, 1], rr_ * np.cos(ang) + c0[2]][:, [0, 1, 2]]
                pos = lin + fade * (arc - lin)
            else:                                          # lateral bulge of the chest wall
                bul = 4 * tau * (1 - tau) * 0.16 * np.linalg.norm(Pb - Pa)
                pos = lin + fade * bul[:, None] * np.array([0, 0, 1.0])[None]
            ids = new_ids(M); Vx2.append(pos); src2 += [-1] * M
            # middle strip of each half, away from the folds and the ridge: anchored to its own segment group
            hgt = top / max(1e-6, (V[rungs[-1][0], 1] + V[rungs[-1][1], 1]) / 2 - V[rungs[0][0], 1])
            for j, id_ in enumerate(ids):
                if 0.3 <= tau[j] <= 0.7 and hgt > 0.25: anchor.append((id_, 2 if side == "arm" else 0))
            rows_.append(np.r_[cp(a), ids, cp(b)])
        fl = []
        for r in range(len(rows_) - 1):
            A0, A1 = rows_[r], rows_[r + 1]
            if (A0[1:-1] == -1).all():                     # bottom rung (a == b): fan onto the shared bottom vertex
                for k in range(M + 1):
                    t3 = (A0[0], A1[k + 1], A1[k])
                    if len(set(t3)) == 3: fl.append(t3)
                continue
            for k in range(M + 1):
                q = [A0[k], A0[k + 1], A1[k + 1], A1[k]]
                for t3 in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
                    if len(set(t3)) == 3: fl.append(t3)
        faces.append(np.array(fl))
    V2 = np.concatenate([V, V[inner]] + Vx2); F2 = np.concatenate(faces).astype(int)
    src_ = list(range(n0)) + list(inner) + src2
    import trimesh
    tm = trimesh.Trimesh(V2, F2, process=False); trimesh.repair.fix_winding(tm)
    F2 = np.asarray(tm.faces)
    if tm.volume < 0: F2 = F2[:, ::-1]
    # relaxed shape: once the arm leaves the side, the flesh that was pressed into the contact (the lips of the two
    # creases) and the pocket halves round out: each level of the arm is closed by a smooth polar profile about the
    # humerus, and the chest wall by a smooth profile about the trunk's centre line, both fitted to the untouched
    # surface around; body.js blends to this shape as the arm rises
    from scipy.sparse.csgraph import dijkstra
    side_f = np.r_[np.where(A, 0, 1), np.zeros(len(faces[1]), int), np.ones(len(faces[2]), int)]
    vside = np.zeros((len(V2), 2), bool)
    for k in range(3): vside[F2[side_f == 0, k], 0] = True; vside[F2[side_f == 1, k], 1] = True
    shared = vside.all(1); relax = V2.copy(); reg_all = np.zeros(len(V2), bool); fall = np.zeros(len(V2))
    armpath = np.array([dup.get(v, v) for v in path]); trkpath = path
    npk = n0 + len(inner)
    ref = np.array([1.0, 0, 0])
    def polar_fit(cen_fn, axis_fn, good, region, win=None):
        """per vertex of region: position on a Fourier (order 2) radius profile fitted at its level to `good`"""
        out = V2.copy(); G = np.flatnonzero(good)
        for i in np.flatnonzero(region):
            c, ax_ = cen_fn(V2[i]), axis_fn(V2[i]); e1 = ref - (ref @ ax_) * ax_; e1 /= np.linalg.norm(e1); e2 = np.cross(ax_, e1)
            lv = (V2[G] - c) @ ax_; sel = G[np.abs(lv) < 7 * h]
            if len(sel) < 12: continue
            R_ = V2[sel] - c; R_ -= np.outer(R_ @ ax_, ax_); th_ = np.arctan2(R_ @ e2, R_ @ e1); rr = np.linalg.norm(R_, axis=1)
            ri = V2[i] - c; ri -= (ri @ ax_) * ax_; thi = math.atan2(ri @ e2, ri @ e1)
            if win is not None:
                dth = np.angle(np.exp(1j * (th_ - thi))); keep = np.abs(dth) < win; th_, rr = th_[keep], rr[keep]
                if len(rr) < 8: continue
                Xd = np.c_[np.ones_like(dth[keep]), dth[keep], dth[keep] ** 2]; co = np.linalg.lstsq(Xd, rr, rcond=None)[0]; r_i = co[0]
            else:
                Xd = np.c_[np.ones_like(th_), np.cos(th_), np.sin(th_), np.cos(2 * th_), np.sin(2 * th_)]
                co = np.linalg.lstsq(Xd, rr, rcond=None)[0]; r_i = co @ np.r_[1, math.cos(thi), math.sin(thi), math.cos(2 * thi), math.sin(2 * thi)]
            out[i] = c + (V2[i] - c) @ ax_ * ax_ + r_i * (math.cos(thi) * e1 + math.sin(thi) * e2)
        return out
    hum = trees["H"].data; hc = hum.mean(0); hd = np.linalg.eigh(np.cov((hum - hc).T))[1][:, -1]; hd = hd if hd[1] > 0 else -hd
    trunk_v = vside[:, 1] & ~vside[:, 0]
    def trunk_centre(p):                                    # centre of the torso cross-section at that height
        sel = trunk_v & (np.abs(V2[:, 1] - p[1]) < 6 * h); c = V2[sel].mean(0) if sel.any() else p.copy(); c[1] = p[1]; return c
    for sd, seeds in ((0, armpath), (1, trkpath)):
        Fs_ = F2[side_f == sd]; e_ = np.r_[Fs_[:, [0, 1]], Fs_[:, [1, 2]], Fs_[:, [2, 0]]]
        w_ = np.linalg.norm(V2[e_[:, 0]] - V2[e_[:, 1]], axis=1)
        Gs = _csr((np.r_[w_, w_], (np.r_[e_[:, 0], e_[:, 1]], np.r_[e_[:, 1], e_[:, 0]])), shape=(len(V2), len(V2)))
        dist = dijkstra(Gs, indices=np.asarray(seeds), min_only=True, limit=55 * h)
        reg = np.isfinite(dist) & (dist < 40 * h) & ~shared & vside[:, sd]
        pocket = np.zeros(len(V2), bool); pocket[npk:] = vside[npk:, sd] & ~shared[npk:]
        reg |= pocket
        good = vside[:, sd] & ~shared & ~reg & ~pocket & np.isfinite(dist) | (vside[:, sd] & ~reg & ~pocket & (V2[:, 1] < ytop) & (V2[:, 1] > V[path, 1].min() - 30 * h))
        good &= ~pocket
        if sd == 0:
            fit = polar_fit(lambda p: hc + ((p - hc) @ hd) * hd, lambda p: hd, good & (np.linalg.norm(np.cross(V2 - hc, hd), axis=1) < 90 * h), reg)
        else:
            fit = polar_fit(trunk_centre, lambda p: np.array([0, 1.0, 0]), good, reg, win=0.9)
        f_ = np.where(pocket, 1.0, np.clip(1 - np.nan_to_num(dist, posinf=1e9) / (40 * h), 0, 1)); f_ = f_ * f_ * (3 - 2 * f_)
        relax[reg] = V2[reg] + f_[reg, None] * (fit[reg] - V2[reg]); reg_all |= reg
    # light smoothing of the correction so the falloff edge leaves no kink
    Ad = vertex_neighbours_(F2, len(V2)); D_ = relax - V2
    for _ in range(4): D_ = np.where(reg_all[:, None], 0.5 * D_ + 0.5 * (Ad @ D_), D_)
    relax = V2 + np.where(reg_all[:, None], D_, 0)
    delta = np.where(reg_all[:, None], relax - V2, 0.0)
    info = dict(n_dup=len(inner), n_new=len(V2) - n0, rungs=len(rungs), M=M, ytop=round(ytop, 1), relax=int(reg_all.sum()), anchors=len(anchor),
                relax_max=round(float(np.linalg.norm(delta, axis=1).max()), 1))
    info['path'] = np.r_[path, armpath]                    # both sides of the cut (for the weight solve)
    info['ridge'] = np.r_[path[0], ridge_ids, path[-1]]     # top of the pocket (ironed with the relaxed shape)
    return V2, F2, np.array(src_), info, delta, np.array(anchor, int).reshape(-1, 2)


def cut_plane(V, F, c, keep_below=True):
    """Clip a triangle mesh by the plane y = c (Sutherland-Hodgman per face). Returns V2 (old vertices first, then the
    new points on the plane), F2, and on_plane (bool per V2 vertex). Unused old vertices stay (callers compact)."""
    s = (V[:, 1] - c) * (1.0 if keep_below else -1.0); inside = s < 0
    newp = {}; extra = []; out = []
    def cross(a, b):
        key = (a, b) if a < b else (b, a)
        if key not in newp:
            t = s[a] / (s[a] - s[b]); newp[key] = len(V) + len(extra); extra.append(V[a] + t * (V[b] - V[a]))
        return newp[key]
    ni = inside[F].sum(1)
    out.append(F[ni == 3])
    for f in F[(ni == 1) | (ni == 2)]:
        poly = []
        for k in range(3):
            a, b = f[k], f[(k + 1) % 3]
            if inside[a]: poly.append(a)
            if inside[a] != inside[b]: poly.append(cross(a, b))
        for k in range(1, len(poly) - 1): out.append(np.array([[poly[0], poly[k], poly[k + 1]]]))
    V2 = np.concatenate([V, np.array(extra).reshape(-1, 3)]); F2 = np.concatenate(out).astype(int)
    on = np.zeros(len(V2), bool); on[len(V):] = True
    return V2, F2, on


def boundary_loops(F):
    e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]; es = np.sort(e, 1)
    u, inv, cnt = np.unique(es, axis=0, return_inverse=True, return_counts=True)
    b = e[cnt[inv.ravel()] == 1]                            # directed boundary edges (face winding)
    nxt = {a: b_ for a, b_ in b}; loops = []; seen = set()
    for a in list(nxt):
        if a in seen: continue
        lp = [a]; seen.add(a); x = nxt[a]
        while x != a and x not in seen and x in nxt: lp.append(x); seen.add(x); x = nxt[x]
        loops.append(np.array(lp))
    return loops


def zipper(A, B, PA, PB):
    """triangle strip between two closed loops (vertex id arrays A, B with positions PA, PB), opposite directions
    expected (two surfaces meeting along a seam); returns faces"""
    B = B[::-1]; PB = PB[::-1]
    k0 = int(np.argmin(np.linalg.norm(PB - PA[0], axis=1))); B = np.roll(B, -k0); PB = np.roll(PB, -k0, axis=0)
    def param(P):
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[P, P[:1]], axis=0), axis=1))]; return d / d[-1]
    ua, ub = param(PA), param(PB); i = j = 0; out = []; na, nb = len(A), len(B)
    while i < na or j < nb:
        if j >= nb or (i < na and ua[i + 1] <= ub[j + 1]):
            out.append((A[(i + 1) % na], A[i % na], B[j % nb])); i += 1
        else:
            out.append((A[i % na], B[j % nb], B[(j + 1) % nb])); j += 1
    return np.array(out, int)


def replace_head(V, F, Vh, Fh, y_cut):
    """Low-resolution skin below y = y_cut + full-resolution head above it, joined by a zipper strip on the cut.
    Returns V2, F2, src (index into V for kept body vertices, -1 for new), head mask."""
    Vb, Fb, onb = cut_plane(V, F, y_cut, keep_below=True)
    used = np.zeros(len(Vb), bool); used[Fb.ravel()] = True
    idx = np.flatnonzero(used); remap = -np.ones(len(Vb), int); remap[idx] = np.arange(len(idx))
    Vb, Fb, onb = Vb[idx], remap[Fb], onb[idx]; srcb = np.where(idx < len(V), idx, -1)
    Vt, Ft, ont = cut_plane(Vh, Fh, y_cut, keep_below=False)
    used = np.zeros(len(Vt), bool); used[Ft.ravel()] = True
    idx = np.flatnonzero(used); remap = -np.ones(len(Vt), int); remap[idx] = np.arange(len(idx)); Vt, Ft, ont = Vt[idx], remap[Ft], ont[idx]
    la = max(boundary_loops(Fb), key=lambda l: onb[l].sum()); lb = max(boundary_loops(Ft), key=lambda l: ont[l].sum())
    n0 = len(Vb); Z = zipper(la, lb + n0, Vb[la], Vt[lb])
    V2 = np.r_[Vb, Vt]; F2 = np.r_[Fb, Ft + n0, Z]
    head = np.r_[np.zeros(n0, bool), np.ones(len(Vt), bool)]
    return V2, F2, np.r_[srcb, -np.ones(len(Vt), int)], head
