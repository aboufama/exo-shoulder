"""signed distance of points to a closed triangle mesh (numpy + scipy kd-trees). The CLOSEST POINT is exact: every
triangle is covered by surface samples (its vertices, shared, plus a barycentric grid on long triangles: no point of a
triangle is farther than h from one of its samples). With s = the distance to the nearest sample (an upper bound: the
sample is on the surface), the closest triangle has a sample within s + h, so the triangles of the samples in that ball
are a complete candidate set (one ball query; a thin shell except in concave pockets). INSIDE = the integer winding
number (Mesh.build_grid / winding_at; signed_distance, max_depth and every judge use it): it needs no closest feature,
holds where the posed body self-intersects, and on an open mesh (a hole or non-manifold edge after welding) is a
majority over rays along x, y and z with the generalized winding number where they disagree. Vertices are welded first
(a glb tessellation is split at every B-rep seam) and faces oriented consistently outward (orient: the band builds'
proxies come mixed or inside out). Mesh.signed_pseudonormal keeps the angle-weighted pseudo-normal sign
(Baerentzen & Aanaes 2005) for comparison: exact only on a closed, manifold, non-self-intersecting mesh (posed body:
~2 % of near-surface points wrong). unsigned_distance when only |d| is needed (no grid).
History (docs/FINDINGS.md "Infrastructure"): until 2026-10-15 the sign came from the nearest face's own normal over the
10 nearest centroids - wrong near edges, and wrong whenever the true closest triangle was not among those 10 (long glb
facets): false R2 / R6 penetrations up to 90 mm where ray parity and the winding number find no point inside.
judge/test_sdist.py checks it against both. Negative = inside."""
import itertools
import numpy as np
from scipy.spatial import cKDTree

_TOPO = {}                                                                   # per face array: edge -> adjacent faces
_NORM = {}                                                                   # per (vertices, faces): pseudo-normals (small LRU)
def _key(V, F):
    sub = np.ascontiguousarray(V[:: max(1, len(V) // 64)]).tobytes()          # content checksum: a reused buffer cannot alias
    return (V.ctypes.data, V.shape, F.ctypes.data, F.shape, hash(sub), hash(np.ascontiguousarray(F).tobytes()))


def closest_on_tri(P, A, B, C, region=False):
    """Ericson's closest point on triangle, vectorised: P, A, B, C (n, 3). region=True also returns the feature code:
    0 interior; 1 / 2 / 3 vertex A / B / C; 4 / 5 / 6 edge AB / AC / BC"""
    ab, ac, ap = B - A, C - A, P - A
    d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
    bp = P - B; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
    cp = P - C; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    den = va + vb + vc; den = np.where(np.abs(den) < 1e-18, 1e-18, den); v = vb / den; w = vc / den
    Q = A + ab * v[:, None] + ac * w[:, None]; reg = np.zeros(len(P), np.int8)            # interior
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); t = (d4 - d3) / np.maximum((d4 - d3) + (d5 - d6), 1e-18); Q[m] = (B + (C - B) * t[:, None])[m]; reg[m] = 6
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.maximum(d2 - d6, 1e-18); Q[m] = (A + ac * t[:, None])[m]; reg[m] = 5
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.maximum(d1 - d3, 1e-18); Q[m] = (A + ab * t[:, None])[m]; reg[m] = 4
    m = (d6 >= 0) & (d5 <= d6); Q[m] = C[m]; reg[m] = 3
    m = (d3 >= 0) & (d4 <= d3); Q[m] = B[m]; reg[m] = 2
    m = (d1 <= 0) & (d2 <= 0); Q[m] = A[m]; reg[m] = 1
    return (Q, reg) if region else Q


def weld(V, F, tol=1e-4):
    """merge vertices that coincide to tol mm (a glb tessellation is split at every B-rep face seam: unwelded, every seam
    is a boundary and the edge / vertex pseudo-normals there are one face's normal). Same faces, same order."""
    _, first, inv = np.unique(np.round(np.asarray(V, float) / tol).astype(np.int64), axis=0, return_index=True, return_inverse=True)
    return np.asarray(V, float)[first], inv.reshape(-1)[np.asarray(F)]


def orient(V, F):
    """consistent, outward faces: two faces sharing an edge must run it opposite ways (a breadth-first walk over the
    two-face edges flips the ones that do not), then every CLOSED connected piece whose signed volume is negative is
    turned inside out (an open piece has no inside to point away from: left as walked). The band builds' proxy members
    come mixed and some proxies wholly inverted; a winding number (or any normal-based sign) is meaningless on them until
    this is done. Returns the faces and the number flipped."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components, breadth_first_order
    m = len(F); E = np.stack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], 1).reshape(-1, 2)
    _, inv, cnt = np.unique(np.sort(E, 1), axis=0, return_inverse=True, return_counts=True); inv = inv.reshape(-1)
    two = np.where(cnt[inv] == 2)[0]; two = two[np.argsort(inv[two], kind="stable")]; a, b = two[0::2], two[1::2]
    fa, fb = a // 3, b // 3; same = E[a, 0] == E[b, 0]                       # both run the edge the same way: flip one
    _, first = np.unique(np.minimum(fa, fb).astype(np.int64) * m + np.maximum(fa, fb), return_index=True)
    fa, fb, same = fa[first], fb[first], same[first]                          # one link per face pair
    G = coo_matrix((np.r_[same, same].astype(np.int8) + 1, (np.r_[fa, fb], np.r_[fb, fa])), shape=(m, m)).tocsr()
    nc, lab = connected_components(G, directed=False); flip = np.zeros(m, bool)
    for c in np.unique(lab[fa[same]]):                                        # pieces with a mismatch: walk them
        order, pred = breadth_first_order(G, int(np.argmax(lab == c)), directed=False)
        rel = np.asarray(G[pred[order[1:]], order[1:]]).ravel() == 2
        for f, p, r in zip(order[1:], pred[order[1:]], rel): flip[f] = flip[p] ^ r
    F = np.where(flip[:, None], F[:, [0, 2, 1]], F); T = V[F]
    vol = np.bincount(lab, weights=np.einsum("ij,ij->i", T[:, 0], np.cross(T[:, 1], T[:, 2])), minlength=nc)
    open_piece = np.zeros(nc, bool); open_piece[lab[np.where(cnt[inv] != 2)[0] // 3]] = True
    inside_out = ((vol < 0) & ~open_piece)[lab]; F = np.where(inside_out[:, None], F[:, [0, 2, 1]], F)
    return F, int((flip ^ inside_out).sum())


def _topology(F):
    """edge id per (face, local edge AB / AC / BC), the two faces of every edge (-1 on a boundary) and the face count of
    every edge (2 on a closed manifold)"""
    key = (F.shape, hash(np.ascontiguousarray(F).tobytes()))                 # by content: a freed array's address is reused
    if key in _TOPO: return _TOPO[key]
    E = np.stack([F[:, [0, 1]], F[:, [0, 2]], F[:, [1, 2]]], 1).reshape(-1, 2); E.sort(1)
    uniq, inv = np.unique(E, axis=0, return_inverse=True); inv = inv.reshape(-1)
    face_of = np.repeat(np.arange(len(F)), 3); adj = np.full((len(uniq), 2), -1)
    order = np.argsort(inv, kind="stable"); s_inv = inv[order]; first = np.r_[True, s_inv[1:] != s_inv[:-1]]
    adj[s_inv[first], 0] = face_of[order][first]
    second = ~first; adj[s_inv[second], 1] = face_of[order][second]
    out = (inv.reshape(-1, 3), adj, np.bincount(inv, minlength=len(uniq)))
    if len(_TOPO) > 256: _TOPO.clear()
    _TOPO[key] = out; return out


def pseudo_normals(V, F):
    """face normals (unit), edge pseudo-normals (sum of the adjacent face normals), angle-weighted vertex normals"""
    key = _key(V, F)
    if key in _NORM: return _NORM[key]
    T = V[F]; Nf = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); Nf /= np.linalg.norm(Nf, axis=1, keepdims=True) + 1e-18
    eid, adj, _ = _topology(F)
    Ne = Nf[np.maximum(adj[:, 0], 0)] + np.where(adj[:, 1:] >= 0, Nf[np.maximum(adj[:, 1], 0)], 0)
    Nv = np.zeros_like(V)
    for k in range(3):
        a, b, c = T[:, k], T[:, (k + 1) % 3], T[:, (k + 2) % 3]
        u1 = b - a; u2 = c - a; ang = np.arccos(np.clip((u1 * u2).sum(1) / (np.linalg.norm(u1, axis=1) * np.linalg.norm(u2, axis=1) + 1e-18), -1, 1))
        np.add.at(Nv, F[:, k], Nf * ang[:, None])
    if len(_NORM) > 8: _NORM.clear()
    _NORM[key] = (Nf, Ne, eid, Nv); return _NORM[key]


class Mesh:
    """exact closest point and signed distance to one triangle mesh, in its own frame (build once per rigid part). The
    vertices are welded first when the mesh has boundary edges (weld: a glb tessellation; faces that collapse to a
    segment are dropped - a mesh that is already closed, like the body, is left alone: its quantised vertices can
    coincide) and the faces oriented consistently outward (orient; self.flipped counts the faces it turned);
    closed = every edge has exactly two faces, each running it the other way round"""
    def __init__(self, V, F, h=0.6):
        V, F = np.asarray(V, float), np.asarray(F)
        if (_topology(F)[2] != 2).any():
            V, F = weld(V, F); F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 2] != F[:, 0])]
        F, self.flipped = orient(V, F)
        T = V[F]; self.V, self.F, self.T, self.h = V, F, T, h
        self.Nf, self.Ne, self.eid, self.Nv = pseudo_normals(V, F)
        _, _, ecount = _topology(F); D = np.stack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], 1).reshape(-1, 2)
        self.closed = bool((ecount == 2).all() and len(np.unique(D, axis=0)) == len(D))
        self.open_tri = (ecount[self.eid] != 2).any(1)                         # faces on a hole / non-manifold edge
        # samples: every vertex (-> all its triangles), plus the interior points of a barycentric grid on long triangles
        # (sub-edge l = L / n, l / sqrt(3) <= h: the farthest point of a triangle from its nearest vertex is <= L / sqrt(3))
        L = np.max(np.linalg.norm(T[:, [1, 2, 0]] - T, axis=2), 1); n = np.maximum(1, np.ceil(L / (h * np.sqrt(3)))).astype(int)
        order = np.argsort(F.reshape(-1), kind="stable"); vt = np.repeat(np.arange(len(F)), 3)[order]
        vptr = np.r_[0, np.cumsum(np.bincount(F.reshape(-1), minlength=len(V)))]
        S, owner = [V], []
        for nn in np.unique(n[n > 1]):
            idx = np.where(n == nn)[0]; ij = np.array([(i, j) for i in range(nn + 1) for j in range(nn + 1 - i) if not ((i == 0 and j in (0, nn)) or i == nn)], float) / nn
            w = np.c_[1 - ij.sum(1), ij]; S.append(np.einsum("sk,tkd->tsd", w, T[idx]).reshape(-1, 3)); owner.append(np.repeat(idx, len(w)))
        owner = np.concatenate(owner) if owner else np.zeros(0, int)
        self.S = np.concatenate(S); self.nv = len(V); self.vptr, self.vt, self.owner = vptr, vt, owner
        self.tree = cKDTree(self.S); self.lo, self.hi = V.min(0), V.max(0)

    def _cands(self, L, base):
        """(point index, triangle) pairs, unique, for lists L of sample indices (point i0 + row)"""
        lens = np.fromiter(map(len, L), int, len(L)); flat = np.fromiter(itertools.chain.from_iterable(L), int, int(lens.sum()))
        pi = np.repeat(np.arange(base, base + len(L)), lens); isv = flat < self.nv
        fv = flat[isv]; cnt = self.vptr[fv + 1] - self.vptr[fv]; st = np.repeat(self.vptr[fv], cnt)
        tv = self.vt[st + (np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt))]
        tri = np.r_[tv, self.owner[flat[~isv] - self.nv]]; pis = np.r_[np.repeat(pi[isv], cnt), pi[~isv]]
        key = np.unique(pis.astype(np.int64) * len(self.F) + tri); return key // len(self.F), key % len(self.F)

    def closest(self, P, chunk=2048, max_pairs=300000):
        """exact closest point: (distance, triangle, feature code, point) per row of P"""
        P = np.asarray(P, float); n = len(P); s, _ = self.tree.query(P)
        best = np.full(n, np.inf); bj = np.zeros(n, int); breg = np.zeros(n, np.int8); bQ = np.zeros((n, 3))
        for i0 in range(0, n, chunk):
            Pc = P[i0:i0 + chunk]; L = self.tree.query_ball_point(Pc, s[i0:i0 + chunk] + self.h + 1e-9, return_sorted=False)
            pi, tj = self._cands(L, i0)
            for k0 in range(0, len(pi), max_pairs):
                p, t = pi[k0:k0 + max_pairs], tj[k0:k0 + max_pairs]; T = self.T[t]
                Q, reg = closest_on_tri(P[p], T[:, 0], T[:, 1], T[:, 2], region=True); d = np.linalg.norm(P[p] - Q, axis=1)
                o = np.lexsort((d, p)); first = o[np.r_[True, p[o][1:] != p[o][:-1]]]; p, d = p[first], d[first]
                b = d < best[p]; ib = p[b]; fb = first[b]
                best[ib] = d[b]; bj[ib] = t[fb]; breg[ib] = reg[fb]; bQ[ib] = Q[fb]
        return best, bj, breg, bQ

    def signed(self, P):
        """signed distance (negative = inside): exact distance, inside = integer winding number (winding_at), right where
        the mesh self-intersects (the posed body) or is open; the grid is (re)built over P's box when P leaves it"""
        P = np.asarray(P, float); best = self.closest(P)[0]
        lo = np.maximum(P.min(0) - 3.0, self.lo - 1.0); hi = np.minimum(P.max(0) + 3.0, self.hi + 1.0)
        if np.any(lo > hi): return best                                         # every point outside the mesh's box
        if not hasattr(self, "W") or np.any(lo < self.glo) or np.any(hi > self.glo + self.g * (self.gn - 1)): self.build_grid(lo=lo, hi=hi)
        return np.where(self.winding_at(P) >= 1, -best, best)

    def signed_pseudonormal(self, P):
        """signed distance, sign from the closest feature's angle-weighted pseudo-normal (exact on a closed, manifold,
        non-self-intersecting mesh only; kept for comparison - judge/test_sdist.py)"""
        P = np.asarray(P, float); best, bj, breg, bQ = self.closest(P); N = self.Nf[bj].copy()
        for code, kv in ((1, 0), (2, 1), (3, 2)):
            m = breg == code; N[m] = self.Nv[self.F[bj[m], kv]]
        for code, ke in ((4, 0), (5, 1), (6, 2)):
            m = breg == code; N[m] = self.Ne[self.eid[bj[m], ke]]
        sg = np.sign(((P - bQ) * N).sum(1)); sg[sg == 0] = 1
        return sg * best

    def build_grid(self, g=0.5, lo=None, hi=None, max_nodes=2.5e7, axes=None):
        """integer winding number at the nodes of a regular grid (over the mesh's box, or the region lo..hi): signed ray
        crossings along +x (+1 entering, -1 leaving: -sign(n_x)) on every (y, z) scanline, cumulated - exact for a closed
        mesh and still right where it self-intersects (the posed body: 2 where arm and trunk overlap). The grid is shifted
        by irrational fractions of g so no ray meets an edge or a vertex exactly.
        An OPEN mesh (a hole or a non-manifold edge left after welding, e.g. the 3R design's BOTTOM + rail) gets the same
        sweep along x, y and z (axes, default (0,) closed / (0, 1, 2) open): a scanline through a hole misses one crossing
        and is off by one from there on; the other two axes' rays to the same node almost never pass that hole, so the
        node takes the majority, and nodes where the three disagree are flagged for the generalized winding number."""
        lo0 = self.lo if lo is None else np.maximum(np.asarray(lo, float), self.lo - 1.0)
        hi0 = self.hi if hi is None else np.minimum(np.asarray(hi, float), self.hi + 1.0)
        ext = np.maximum(hi0 - lo0, 0) + 4 * g; g = float(max(g, (np.prod(ext) / max_nodes) ** (1 / 3)))
        glo = lo0 - 2 * g + g * np.array([0.1234567, 0.3141593, 0.2718282]); n = np.ceil((hi0 + 2 * g - glo) / g).astype(int) + 1
        axes = ((0,) if self.closed else (0, 1, 2)) if axes is None else tuple(axes); assert len(axes) in (1, 3)
        Ws = [self._sweep(ax, glo, g, n) for ax in axes]
        if len(Ws) == 1: self.W, self.Wbad = Ws[0], None
        else:
            Wa = np.stack(Ws); del Ws; self.W = Wa.sum(0, dtype=np.int16) - Wa.max(0) - Wa.min(0)   # median of 3 = majority
            self.Wbad = (Wa != Wa[0]).any(0); del Wa
        self.glo, self.g, self.gn, self.axes = glo, g, n, axes
        return self

    def _sweep(self, ax, glo, g, n):
        """winding grid from rays along +axis ax (cumulated signed crossings), indexed [x, y, z]"""
        p = [ax, (ax + 1) % 3, (ax + 2) % 3]; T = self.T[:, :, p]; glo = glo[p]; n = n[p]       # rotate ax to x (cyclic: same handedness)
        j0 = np.maximum(0, np.ceil((T[:, :, 1].min(1) - glo[1]) / g).astype(int)); j1 = np.minimum(n[1] - 1, np.floor((T[:, :, 1].max(1) - glo[1]) / g).astype(int))
        k0 = np.maximum(0, np.ceil((T[:, :, 2].min(1) - glo[2]) / g).astype(int)); k1 = np.minimum(n[2] - 1, np.floor((T[:, :, 2].max(1) - glo[2]) / g).astype(int))
        nj = np.maximum(0, j1 - j0 + 1); nk = np.maximum(0, k1 - k0 + 1); cnt = nj * nk; sx = -np.sign(self.Nf[:, ax]).astype(np.int16)
        D = np.zeros((n[0] + 1, n[1], n[2]), np.int16); tris = np.where(cnt > 0)[0]
        for a0 in range(0, len(tris), 100000):                                   # bounded memory on big, flat facets
            t_ = tris[a0:a0 + 100000]; ct = cnt[t_]; tri = np.repeat(t_, ct); loc = np.arange(ct.sum()) - np.repeat(np.cumsum(ct) - ct, ct)
            j = j0[tri] + loc // nk[tri]; k = k0[tri] + loc % nk[tri]; py = glo[1] + g * j; pz = glo[2] + g * k
            A, B, C = T[tri, 0], T[tri, 1], T[tri, 2]
            ef = lambda P0, P1: (P1[:, 1] - P0[:, 1]) * (pz - P0[:, 2]) - (P1[:, 2] - P0[:, 2]) * (py - P0[:, 1])
            eC, eA, eB = ef(A, B), ef(B, C), ef(C, A)                             # edge functions = weights of the opposite vertex
            hit = ((eA > 0) & (eB > 0) & (eC > 0)) | ((eA < 0) & (eB < 0) & (eC < 0)); tot = np.where(hit, eA + eB + eC, 1.0)
            x = (eA * A[:, 0] + eB * B[:, 0] + eC * C[:, 0]) / tot
            i = np.clip(np.ceil((x - glo[0]) / g).astype(int), 0, n[0]); np.add.at(D, (i[hit], j[hit], k[hit]), sx[tri[hit]])
        return np.cumsum(D, 0, dtype=np.int16)[:n[0]].transpose(np.argsort(p))

    def winding_at(self, P, s=None):
        """exact integer winding number at P: the nearest grid node's, plus the signed crossings of the segment node -> P
        (only where the surface can be that close: s - h <= |P - node|; candidates = triangles with a sample within
        |P - node| + h of P, complete by the cover bound). Points outside the grid get the brute-force winding number;
        on an open mesh so do points whose node's sweeps disagree or whose segment passes a face on a hole."""
        P = np.asarray(P, float); s = self.tree.query(P)[0] if s is None else s; W = np.zeros(len(P), int)
        idx = np.rint((P - self.glo) / self.g).astype(int); inb = np.all((idx >= 0) & (idx < self.gn), 1)
        out = np.where(~inb & np.all((P >= self.lo - 1e-6) & (P <= self.hi + 1e-6), 1))[0]
        ii = np.where(inb)[0]; node = self.glo + self.g * idx[ii]; W[ii] = self.W[idx[ii, 0], idx[ii, 1], idx[ii, 2]]
        brute = np.zeros(len(P), bool); brute[out] = True
        if self.Wbad is not None: brute[ii] = self.Wbad[idx[ii, 0], idx[ii, 1], idx[ii, 2]]
        dn = np.linalg.norm(P[ii] - node, axis=1); u = np.where(s[ii] - self.h <= dn)[0]
        for c0 in range(0, len(u), 4096):
            uc = u[c0:c0 + 4096]; Pu = P[ii[uc]]; O = node[uc]; L = self.tree.query_ball_point(Pu, dn[uc] + self.h + 1e-9, return_sorted=False)
            pi, tj = self._cands(L, 0)
            if not len(pi): continue
            Dv = Pu[pi] - O[pi]; A = self.T[tj, 0]; e1 = self.T[tj, 1] - A; e2 = self.T[tj, 2] - A
            hh = np.cross(Dv, e2); a = (e1 * hh).sum(1); ok = np.abs(a) > 1e-15; f = np.where(ok, 1 / np.where(ok, a, 1), 0)
            sv = O[pi] - A; uu = f * (sv * hh).sum(1); q = np.cross(sv, e1); vv = f * (Dv * q).sum(1); t = f * (e2 * q).sum(1)
            hit = ok & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (t > 0) & (t < 1)
            sg = -np.sign((self.Nf[tj] * Dv).sum(1)); W[ii[uc]] += np.rint(np.bincount(pi, weights=hit * sg, minlength=len(uc))).astype(int)
            if not self.closed: brute[ii[uc]] |= np.bincount(pi, weights=self.open_tri[tj], minlength=len(uc)) > 0
        b = np.where(brute)[0]
        if len(b): W[b] = np.rint(winding_number(P[b], self.V, self.F)).astype(int)
        return W

    def max_depth(self, P, tol=0.0, batch=64, confirm=None):
        """deepest point of P inside the mesh (winding number >= 1): (depth mm, index) or (0.0, None). Depth = exact
        distance to the nearest surface. Points nearer the surface than tol are skipped (they cannot be deeper). Needs a
        grid covering P (build_grid; built over the mesh's box if missing). (confirm: old signature, ignored - the inside
        test is the winding number everywhere)"""
        P = np.asarray(P, float)
        if not len(P): return 0.0, None
        if not hasattr(self, "W"): self.build_grid()
        s, _ = self.tree.query(P); keep = np.where(s > tol)[0]
        if not len(keep): return 0.0, None
        Pk, sk = P[keep], s[keep]; ins = np.where(self.winding_at(Pk, sk) >= 1)[0]; ins = ins[np.argsort(-sk[ins])]
        best, bi = 0.0, None                                                     # s >= depth: refine the deepest first
        for i0 in range(0, len(ins), batch):
            if sk[ins[i0]] <= best: break
            b = ins[i0:i0 + batch]; d = self.closest(Pk[b])[0]; j = int(np.argmax(d))
            if d[j] > best: best, bi = float(d[j]), int(b[j])
        return (best, int(keep[bi])) if bi is not None and best > tol else (0.0, None)

_MESH = {}
def mesh(V, F, h=0.6):
    """Mesh for (V, F), cached by content (a few entries)"""
    key = _key(V, F) + (h,)
    if key not in _MESH:
        if len(_MESH) > 4: _MESH.clear()
        _MESH[key] = Mesh(V, F, h)
    return _MESH[key]


def signed_distance(P, V, F, k=None, tree=None, normals=None, h=0.6):
    """exact signed distance (negative = inside; inside = winding number >= 1). k / tree / normals: accepted for the old
    call signature, ignored"""
    return mesh(V, F, h).signed(P)


def unsigned_distance(P, V, F, h=0.6):
    """exact distance to the surface (no inside test: no winding grid, any mesh - open patches too)"""
    return mesh(V, F, h).closest(P)[0]


def winding_number(P, V, F, chunk=32):
    """generalized winding number (Jacobson et al. 2013; sum of signed solid angles, Van Oosterom & Strackee 1983):
    1 inside, 0 outside a closed mesh, and still meaningful where the mesh self-intersects (> 0.5 = inside)"""
    T = V[F]; w = np.zeros(len(P))
    for i0 in range(0, len(P), chunk):
        a, b, c = (T[None, :, q] - P[i0:i0 + chunk, None] for q in range(3)); la, lb, lc = (np.linalg.norm(x, axis=-1) for x in (a, b, c))
        num = (a * np.cross(b, c)).sum(-1); den = la * lb * lc + (a * b).sum(-1) * lc + (a * c).sum(-1) * lb + (b * c).sum(-1) * la
        w[i0:i0 + chunk] = np.arctan2(num, den).sum(1) / (2 * np.pi)
    return w


def max_depth(P, V, F, tol=0.0, h=0.6, g=0.5, margin=3.0):
    """deepest point of P inside a mesh that changes every call (the posed body): Mesh + a winding grid over P's box only"""
    M = Mesh(V, F, h).build_grid(g, P.min(0) - margin, P.max(0) + margin); return M.max_depth(P, tol)
