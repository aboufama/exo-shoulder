"""signed distance of points to a closed triangle mesh (no rtree): exact closest point on the k nearest triangles
(centroid kd-tree), sign from that triangle's normal (outward). Negative = inside."""
import numpy as np
from scipy.spatial import cKDTree
def closest_on_tri(P, A, B, C):
    """Ericson's closest point on triangle, vectorised: P, A, B, C (n, 3)"""
    ab, ac, ap = B - A, C - A, P - A
    d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
    bp = P - B; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
    cp = P - C; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    den = va + vb + vc; den = np.where(np.abs(den) < 1e-18, 1e-18, den); v = vb / den; w = vc / den
    Q = A + ab * v[:, None] + ac * w[:, None]                                                    # interior
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); t = (d4 - d3) / np.maximum((d4 - d3) + (d5 - d6), 1e-18); Q[m] = (B + (C - B) * t[:, None])[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.maximum(d2 - d6, 1e-18); Q[m] = (A + ac * t[:, None])[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.maximum(d1 - d3, 1e-18); Q[m] = (A + ab * t[:, None])[m]
    m = (d6 >= 0) & (d5 <= d6); Q[m] = C[m]
    m = (d3 >= 0) & (d4 <= d3); Q[m] = B[m]
    m = (d1 <= 0) & (d2 <= 0); Q[m] = A[m]
    return Q
def signed_distance(P, V, F, k=10, tree=None):
    T = V[F]; cen = T.mean(1); tree = tree or cKDTree(cen); _, J = tree.query(P, k=k)
    n = len(P); best = np.full(n, np.inf); sgn = np.ones(n)
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-18
    for c in range(k):
        j = J[:, c]; Q = closest_on_tri(P, T[j, 0], T[j, 1], T[j, 2]); d = np.linalg.norm(P - Q, axis=1)
        better = d < best - 1e-9; best = np.where(better, d, best)
        s = np.sign(((P - Q) * N[j]).sum(1)); s[s == 0] = 1; sgn = np.where(better, s, sgn)
    return sgn * best
