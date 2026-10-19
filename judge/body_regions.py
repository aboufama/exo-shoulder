"""R2 attribution on a self-intersecting body: how much of a part's depth inside the posed rig is the part's own doing,
and how much is the rig's limb already lying inside another body region (the rig has no soft-tissue contact model: its
upper arm passes ~90 mm into the chest in "Wash opposite shoulder", its forearm into the biceps at deep flexion).

The rig's render skin is split into three regions by its skinning weights (trunk = thorax + scapula, upper arm =
humerus, forearm = forearm + hand). A part that rides on a limb (group H: upper arm, F: forearm) is judged against
  - its OWN limb: any depth inside it counts in full (the part enters the limb it is strapped to; the plain depth);
  - every OTHER region: only the depth beyond the depth of its own limb's skin under it,
        attributable(P) = d_other(P) - d_other(Q),   Q = the nearest point of the own limb's skin to P,
    where d_other = exact distance to the other regions' surface, and d_other(Q) counts only where Q is buried (the
    point just outside the own skin at Q is inside the body). Where the own skin under the part is on the visible
    surface (not buried) the full depth counts, so in a pose where the rig does not self-intersect nothing changes.
Triangle inequality: d_other(P) - d_other(Q) <= |P - Q|, so attributable <= the plain depth (judge/sdist.py) always:
the attribution can only take away depth that lies inside the rig's own self-intersection.
Where Q lies on the edge of the own region's patch (the region boundary, where the sign of the open patch is not
defined) the plain depth counts (conservative). Parts that ride no limb (base, links) are judged with the plain depth.
Validated on synthetic self-intersecting bodies in judge/test_body_contact.py."""
import numpy as np
from scipy.spatial import cKDTree
from sdist import Mesh

REGIONS = ("trunk", "upper arm", "forearm")
OWN = {"H": 1, "F": 2}                                                  # motion group -> the limb region it rides on


def vertex_regions(W):
    """W (n, 5) skinning weights per segment [thorax, scapula, humerus, forearm, pronation] -> region per vertex"""
    return np.argmax(np.c_[W[:, 0] + W[:, 1], W[:, 2], W[:, 3] + W[:, 4]], axis=1)


def face_regions(F, vreg):
    """majority region of each face's three vertices (ties: the first vertex's)"""
    r = vreg[F]; out = r[:, 0].copy()
    out[r[:, 1] == r[:, 2]] = r[r[:, 1] == r[:, 2], 1]
    return out


def submesh(V, F, sel):
    """compacted (V, F) of the faces sel, and the patch's boundary vertices (edges with one face) in the compacted index"""
    Fs = F[sel]; u, inv = np.unique(Fs, return_inverse=True); Fc = inv.reshape(-1, 3)
    E = np.sort(np.r_[Fc[:, [0, 1]], Fc[:, [1, 2]], Fc[:, [2, 0]]], axis=1); ue, cnt = np.unique(E, axis=0, return_counts=True)
    bnd = np.unique(ue[cnt == 1].ravel())
    return V[u], Fc, bnd


class Regions:
    """per posed body: lazily built Mesh of each region (own) and of everything but each region (other)"""
    def __init__(self, V, F, freg, h=2.0):
        self.V, self.F, self.freg, self.h = V, F, freg, h; self._own = {}; self._oth = {}

    def own(self, k):
        if k not in self._own:
            Vs, Fs, bnd = submesh(self.V, self.F, self.freg == k); M = Mesh(Vs, Fs, self.h)
            # boundary samples (edges of the patch) to flag closest points that sit on the patch edge
            B = Vs[bnd] if len(bnd) else np.zeros((1, 3)) + 1e9
            self._own[k] = (M, cKDTree(B))
        return self._own[k]

    def other(self, k):
        if k not in self._oth:
            Vs, Fs, _ = submesh(self.V, self.F, self.freg != k); self._oth[k] = Mesh(Vs, Fs, self.h)
        return self._oth[k]


def attributable_depth(M, R, own, P, d, tol=0.5, eps=0.3, edge_mm=3.0, batch=256):
    """deepest attributable point of one part: M = the full body Mesh with a winding grid (sdist), R = Regions of the same
    posed body, own = the part's own region (None: plain depth), P = its points inside the body, d = their plain depth.
    Inside its own limb a point counts with its plain depth (the depth below the own skin is not used: near the
    elbow and armpit folds the open patch's sign is not reliable, and the attribution must never exceed the plain judge).
    Returns (depth mm, index into P, kind) with kind 'own limb' | 'other region, own skin visible' | 'other region,
    beyond the buried own skin' | 'region edge (plain depth)' | 'plain' (no own limb)."""
    P = np.asarray(P, float); d = np.asarray(d, float)
    if not len(P): return 0.0, None, None
    if own is None:
        j = int(np.argmax(d)); return (float(d[j]), j, "plain") if d[j] > tol else (0.0, None, None)
    Mo, Bt = R.own(own); s_own = Mo.signed(P); best, bi, bk = 0.0, None, None
    ins = np.where(s_own < 0)[0]
    if len(ins):                                                                # inside the limb it rides on: counts in full
        j = int(np.argmax(d[ins]))                                              # (plain depth: never more than the plain judge)
        if d[ins][j] > best: best, bi, bk = float(d[ins][j]), int(ins[j]), "own limb"
    out = np.where(s_own >= 0)[0]; out = out[np.argsort(-d[out])]; Mt = None
    for i0 in range(0, len(out), batch):                                        # elsewhere: attributable <= plain depth
        idx = out[i0:i0 + batch]
        if d[idx[0]] <= max(best, tol): break
        Mt = Mt or R.other(own); Pc = P[idx]
        _, _, _, Q = Mo.closest(Pc); n = Pc - Q; n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
        edge = Bt.query(Q)[0] < edge_mm; buried = M.winding_at(Q + eps * n) >= 1
        dP = Mt.closest(Pc)[0]; dQ = np.where(buried, Mt.closest(Q)[0], 0.0)
        att = np.where(edge | ~buried, d[idx], np.minimum(d[idx], np.maximum(0.0, dP - dQ)))
        kind = np.where(edge, "region edge (plain depth)", np.where(buried, "other region, beyond the buried own skin", "other region, own skin visible"))
        j = int(np.argmax(att))
        if att[j] > best: best, bi, bk = float(att[j]), int(idx[j]), str(kind[j])
    return (best, bi, bk) if bi is not None and best > tol else (0.0, None, None)
