"""Collision grids from the mesh body (body_mesh.json, BodyParts3D): signed distance to the skin around the right
shoulder. Trunk grids (skin not driven by the right arm) per arm elevation (scapula rhythm + girdle elevation), and
one arm grid in the humerus frame. Same layout as make_skin_grids.mjs, so design_search_anat.py and the viewer use it.

    python3 make_mesh_grids.py
"""
import base64, json, math
import numpy as np
from scipy.spatial import cKDTree

J = json.load(open("body_mesh.json")); L = J["landmarks"]; S = J["scale"]
dec = lambda s, t: np.frombuffer(base64.b64decode(s), dtype=t)
sk = [p for p in J["parts"] if p["cls"] == "skin"][0]
V = dec(sk["pos"], np.int16).reshape(-1, 3) / 10.0
F = dec(sk["idx"], np.uint32 if sk["i32"] else np.uint16).reshape(-1, 3).astype(int)
wi = dec(sk["wi"], np.uint8).reshape(-1, 2).astype(int); ww = dec(sk["ww"], np.uint8) / 255.0
D2R = math.pi / 180


def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def scap(elev):
    n = [math.cos(30 * D2R), 0, -math.sin(30 * D2R)]
    return rot([0, 0, 1], 0.12 * elev * D2R) @ rot(n, -0.36 * max(0, elev - 20) * D2R)


def segs(pose):                                           # port of body.js segmentTransforms (affine: R, t)
    lift = np.array([0, 0.2 * max(0, pose["elev"] - 30) * S, 0])
    Rh = rot([0, 1, 0], pose["plane"] * D2R) @ rot([1, 0, 0], -pose["elev"] * D2R) @ rot([0, 1, 0], pose["axial"] * D2R)
    T = (np.eye(3), -lift); Sg = (scap(pose["elev"]), np.zeros(3)); H = (Rh @ np.array(L["rest_humerus"]).T, np.zeros(3))
    ap = lambda A, p: A[0] @ p + A[1]
    E = ap(H, np.array(L["elbow"])); ax = H[0] @ np.array(L["elbow_axis"])
    Rf = rot(ax, (pose["flex"] - L["rest_flex"]) * D2R); Fs = (Rf @ H[0], Rf @ H[1] + E - Rf @ E)
    rh, uh = ap(Fs, np.array(L["radial_head"])), ap(Fs, np.array(L["ulnar_head"]))
    Rp = rot(rh - uh, (pose["pron"] + 90) * D2R); P = (Rp @ Fs[0], Rp @ Fs[1] + rh - Rp @ rh)
    return [T, Sg, H, Fs, P]


def posed(pose):
    sg = segs(pose)
    Ra = np.stack([sg[k][0] for k in range(5)]); ta = np.stack([sg[k][1] for k in range(5)])
    A = np.einsum("nij,nj->ni", Ra[wi[:, 0]], V) + ta[wi[:, 0]]; B = np.einsum("nij,nj->ni", Ra[wi[:, 1]], V) + ta[wi[:, 1]]
    return ww[:, None] * A + (1 - ww[:, None]) * B


def normals(P):
    fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    n = np.zeros_like(P)
    for k in range(3): np.add.at(n, F[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def sdf(P, Nn, keep, Q):
    """Distance to the skin subset `keep`, negative only inside the closed skin AND nearest to that subset."""
    full = cKDTree(P); dF, iF = full.query(Q); vF = P[iF]; nF = Nn[iF]
    plane = ((Q - vF) * nF).sum(1); inside = np.where(dF < 15.0, plane, ((Q - vF) * nF).sum(1)) < 0
    t = cKDTree(P[keep]); d, i = t.query(Q); v = P[keep][i]; n = Nn[keep][i]
    dist = np.where(d < 15.0, np.abs(((Q - v) * n).sum(1)), d)
    own = keep[iF]
    return np.where(inside & own, -dist, np.where(inside, dist * 0 + np.maximum(dist, 0.0), dist))


armw = np.where(wi[:, 0] >= 2, ww, 0) + np.where(wi[:, 1] >= 2, 1 - ww, 0)
ARM = armw > 0.5
STEP = 8.0; LO = np.array([-240.0, -480.0, -320.0]); HI = np.array([240.0, 200.0, 480.0]); SH = (np.round((HI - LO) / STEP).astype(int) + 1)
ax = [LO[k] + np.arange(SH[k]) * STEP for k in range(3)]; Q = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
elevs = list(range(0, 181, 15)); grids = []
for e in elevs:
    P = posed(dict(plane=30, elev=e, axial=0, flex=30, pron=0)); grids.append(sdf(P, normals(P), ~ARM, Q).reshape(*SH)); print("trunk", e, flush=True)
P = posed(dict(plane=0, elev=0, axial=0, flex=30, pron=0)); grids.append(sdf(P, normals(P), ARM, Q).reshape(*SH)); print("arm", flush=True)
G = np.stack(grids).astype(np.float32); G.tofile("skin_grids_ext.bin")
meta = dict(shape=SH.tolist(), lo=LO.tolist(), STEP=STEP, scale=S, elevs=elevs, order="trunk per elev, then arm (humerus frame)", body="BodyParts3D mesh (body_mesh.json)", frame="thorax mm: x anterior, y up, z right, origin right GH; axis order i=x j=y k=z")
json.dump(meta, open("skin_grids_ext.json", "w"))
