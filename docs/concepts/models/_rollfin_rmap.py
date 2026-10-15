"""Skin radius maps for docs/concepts/models/rolling-fin-j2.py: per bench pose, a cube map (6 faces x N x N, ~1 deg
cells, padded so bilinear lookups never cross a face) of the FIRST skin exit radius from the GH centre along each
direction of the thorax frame (min radius of the posed render-skin's surface samples in the cell, skin beyond T_CAP
ignored), then a 3 x 3 max filter (conservative over +-1 cell, fills raster holes). Used only to FIT the idealised
parts' radial profiles (like tools/concept_baseline.py's sphere-traced skin radius); every score comes from
concept_bench's own signed distance of the final metal points."""
import os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import body_pose as BP                                                     # noqa: E402
import concept_bench as CB                                                 # noqa: E402
N, PAD, T_CAP, R_REG, STEP = 120, 0.05, 200.0, 215.0, 1.25
EMPTY = 999.0
AX = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]     # (major axis, u axis, v axis) per face pair
FACES = [(m, s, u, v) for (m, u, v) in [(0, 1, 2), (1, 2, 0), (2, 0, 1)] for s in (1, -1)]


def cache_path(key):
    return os.path.join(REPO, ".cache", "concept_models", "rolling-fin-j2", f"rmap_{key}.npy")


def _tri_samples(V, F):
    E = np.stack([V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 1]], V[F[:, 0]] - V[F[:, 2]]], 1)
    n = np.ceil(np.linalg.norm(E, axis=2).max(1) / STEP).astype(int).clip(1, 60)
    out = []
    for k in np.unique(n):
        f = F[n == k]; i, j = np.meshgrid(np.arange(k + 1), np.arange(k + 1), indexing="ij"); m = i + j <= k
        a = (i[m] / k)[None, :, None]; b = (j[m] / k)[None, :, None]
        A, Bv, C = V[f[:, 0]][:, None], V[f[:, 1]][:, None], V[f[:, 2]][:, None]
        out.append((A + a * (Bv - A) + b * (C - A)).reshape(-1, 3))
    return np.concatenate(out)


def face_uv(D, face):
    m, s, u, v = face
    dm = D[..., m] * s
    with np.errstate(divide="ignore", invalid="ignore"):
        return dm, D[..., u] / dm, D[..., v] / dm


def build_map(V):
    keep = np.linalg.norm(V, axis=1) < R_REG; F = BP.F[keep[BP.F].any(1)]
    P = _tri_samples(V, F); r = np.linalg.norm(P, axis=1); P = P[r < T_CAP]; r = r[r < T_CAP]; D = P / r[:, None]
    Mp = np.full((6, N, N), np.inf)
    for fi, face in enumerate(FACES):
        dm, a, b = face_uv(D, face); ok = (dm > 0.05) & (np.abs(a) <= 1 + PAD) & (np.abs(b) <= 1 + PAD)
        ia = np.clip(((a[ok] + 1 + PAD) / (2 + 2 * PAD) * N).astype(int), 0, N - 1); ib = np.clip(((b[ok] + 1 + PAD) / (2 + 2 * PAD) * N).astype(int), 0, N - 1)
        rr = r[ok]; o = np.argsort(-rr); lin = (ia * N + ib)[o]
        flat = Mp[fi].reshape(-1); cur = flat[lin]; flat[lin] = np.minimum(cur, rr[o])   # duplicates: last (smallest) write wins
        Mp[fi] = flat.reshape(N, N)
    # 3x3 max filter over filled cells (conservative, fills holes); cells still empty -> EMPTY
    Fm = np.where(np.isinf(Mp), -np.inf, Mp); Pd = np.pad(Fm, ((0, 0), (1, 1), (1, 1)), constant_values=-np.inf)
    out = np.full_like(Fm, -np.inf)
    for di in range(3):
        for dj in range(3): out = np.maximum(out, Pd[:, di:di + N, dj:dj + N])
    out[np.isinf(out)] = EMPTY
    return out.astype(np.float32)


def lookup(M, D):
    """first-exit skin radius along unit directions D (..., 3) from one map M (6, N, N): bilinear in the best face"""
    D = np.asarray(D, float); shp = D.shape[:-1]; D = D.reshape(-1, 3)
    m = np.argmax(np.abs(D), 1); s = np.sign(D[np.arange(len(D)), m])
    out = np.empty(len(D))
    for fi, face in enumerate(FACES):
        sel = (m == face[0]) & (s == face[1])
        if not sel.any(): continue
        _, a, b = face_uv(D[sel], face)
        x = (a + 1 + PAD) / (2 + 2 * PAD) * N - 0.5; y = (b + 1 + PAD) / (2 + 2 * PAD) * N - 0.5
        x0 = np.clip(np.floor(x).astype(int), 0, N - 2); y0 = np.clip(np.floor(y).astype(int), 0, N - 2)
        fx = np.clip(x - x0, 0, 1); fy = np.clip(y - y0, 0, 1); G = M[fi]
        v00, v10, v01, v11 = G[x0, y0], G[x0 + 1, y0], G[x0, y0 + 1], G[x0 + 1, y0 + 1]
        val = v00 * (1 - fx) * (1 - fy) + v10 * fx * (1 - fy) + v01 * (1 - fx) * fy + v11 * fx * fy
        big = np.maximum.reduce([v00, v10, v01, v11]) >= EMPTY      # any empty neighbour -> unusable direction
        out[sel] = np.where(big, EMPTY, val)
    return out.reshape(shp)


def build(n_clip=60, n_ws=160):
    B = CB.Bench(n_clip, n_ws); path = cache_path(B.key)
    if os.path.exists(path): print("exists", path); return path
    os.makedirs(os.path.dirname(path), exist_ok=True); t = time.time()
    Ms = np.zeros((len(B.poses), 6, N, N), np.float32)
    for i in range(len(B.poses)):
        Ms[i] = build_map(B._verts(i))
        if i % 20 == 0: print(i, len(B.poses), round(time.time() - t), flush=True)
    np.save(path + ".tmp.npy", Ms); os.replace(path + ".tmp.npy", path); print("saved", path, round(time.time() - t)); return path


if __name__ == "__main__":
    a = sys.argv[1:]
    build(int(a[0]) if a else 60, int(a[1]) if len(a) > 1 else 160)
