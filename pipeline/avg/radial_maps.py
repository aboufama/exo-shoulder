"""Radial skin maps around the right shoulder centre (average body): for every direction w from the GH centre, the
outermost radius at which the skin lies (r_skin) and the outermost radius of the skin offset outward by C mm (r_clear:
a point on that ray is >= C mm off the skin if it is beyond r_clear). Exact geometry: the posed skin mesh is sampled
densely (spacing ~0.2 mm near the shoulder, growing with distance) and splatted into an equirectangular map, keeping
the maximum radius per pixel ("farthest depth" render from the GH centre).

  trunk maps: skin not driven by the right arm, per arm elevation bin (scapula rhythm + girdle elevation), thorax frame
  arm map:    right-arm skin at pose 0, canonical humerus frame (same layout as the collision grids)
Lookup: lon = atan2(z, x), lat = asin(y); 0.25 deg pixels.

    python3 radial_maps.py      -> radial_maps.npz
"""
import base64, json, math, time
import numpy as np

RES = 0.25; NW, NH = int(360 / RES), int(180 / RES)
CLEARS = (0.0, 3.0)
J = json.load(open("body_mesh.json")); L = J["landmarks"]; S = J["scale"]
dec = lambda s, t: np.frombuffer(base64.b64decode(s), dtype=t)
sk = [p for p in J["parts"] if p["cls"] == "skin"][0]
V = dec(sk["pos"], np.int16).reshape(-1, 3) / 10.0
Fc = dec(sk["idx"], np.uint32 if sk["i32"] else np.uint16).reshape(-1, 3).astype(int)
wi = dec(sk["wi"], np.uint8).reshape(-1, 2).astype(int); ww = dec(sk["ww"], np.uint8) / 255.0
D2R = math.pi / 180
def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def scap(elev):
    n = [math.cos(30 * D2R), 0, -math.sin(30 * D2R)]
    return rot([0, 0, 1], 0.12 * elev * D2R) @ rot(n, -0.36 * max(0, elev - 20) * D2R)
def segs(pose):
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
    sg = segs(pose); Ra = np.stack([sg[k][0] for k in range(5)]); ta = np.stack([sg[k][1] for k in range(5)])
    A = np.einsum("nij,nj->ni", Ra[wi[:, 0]], V) + ta[wi[:, 0]]; B = np.einsum("nij,nj->ni", Ra[wi[:, 1]], V) + ta[wi[:, 1]]
    return ww[:, None] * A + (1 - ww[:, None]) * B
def vnormals(P):
    fn = np.cross(P[Fc[:, 1]] - P[Fc[:, 0]], P[Fc[:, 2]] - P[Fc[:, 0]]); n = np.zeros_like(P)
    for k in range(3): np.add.at(n, Fc[:, k], fn)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    # orient outward: majority of normals should point away from the body centroid region (skin mesh orientation)
    return n
armw = np.where(wi[:, 0] >= 2, ww, 0) + np.where(wi[:, 1] >= 2, 1 - ww, 0)
ARMV = armw > 0.5; ARMF = ARMV[Fc].sum(1) >= 2

def outward_sign(P, n):
    """+1 if the vertex normals point out of the body (checked against the body centre line), else -1"""
    c = np.array([-30.0, -300.0, -170.0])                    # roughly inside the torso (thorax frame, mm)
    return 1.0 if np.mean(((P - c) * n).sum(1) > 0) > 0.5 else -1.0

def samples(P, faces, R_MAX=480.0, seed=0):
    """dense points on the triangles (spacing ~0.2 mm near the shoulder, growing with range)"""
    A, B, C = P[faces[:, 0]], P[faces[:, 1]], P[faces[:, 2]]
    rc = np.linalg.norm((A + B + C) / 3, axis=1); keep = rc < R_MAX
    A, B, C, rc = A[keep], B[keep], C[keep], rc[keep]
    area = 0.5 * np.linalg.norm(np.cross(B - A, C - A), axis=1)
    spacing = np.maximum(0.25, rc * math.radians(RES) * 0.6)
    n = np.clip(np.ceil(area / spacing ** 2 * 2.0), 1, 4000).astype(int)
    out = []
    for lo in range(0, len(A), 20000):
        sl = slice(lo, lo + 20000); nn = n[sl]; idx = np.repeat(np.arange(len(nn)), nn)
        u = np.random.default_rng(seed + lo).random((len(idx), 2)); flip = u.sum(1) > 1; u[flip] = 1 - u[flip]
        out.append(A[sl][idx] + u[:, :1] * (B[sl][idx] - A[sl][idx]) + u[:, 1:] * (C[sl][idx] - A[sl][idx]))
        out.append(A[sl]); out.append(B[sl]); out.append(C[sl])
    return np.concatenate(out)

LAT_LO, LAT_HI = -75.0, 90.0                                   # rows we need (links live above / beside the shoulder)
def pix(Q):
    r = np.linalg.norm(Q, axis=1); lon = np.arctan2(Q[:, 2], Q[:, 0]); lat = np.arcsin(np.clip(Q[:, 1] / r, -1, 1))
    j = np.clip(((lon + math.pi) / math.radians(RES)).astype(int), 0, NW - 1); i = np.clip(((lat + math.pi / 2) / math.radians(RES)).astype(int), 0, NH - 1)
    return r, i, j

def ray_maps(P, faces, c):
    """r1: first skin crossing (exit) from the GH centre, r2: next crossing (re-entry, inf if none); r1c / r2c: the
    band [r1c, r2c] of radii that are >= c mm from every skin point (exact distance to the sampled skin)"""
    from scipy.spatial import cKDTree
    Q = samples(P, faces); r, i, j = pix(Q)
    r1 = np.full((NH, NW), np.inf, np.float32); np.minimum.at(r1, (i, j), r.astype(np.float32))
    # pinholes in r1: fill from the 3x3 min where most neighbours exist
    from scipy.ndimage import minimum_filter, uniform_filter
    fin = np.isfinite(r1); mn = minimum_filter(np.where(fin, r1, 1e9), size=3, mode="wrap")
    hole = ~fin & (uniform_filter(fin.astype(float), size=3, mode="wrap") > 0.5); r1[hole] = mn[hole]
    beyond = r > r1[i, j] + 4.0
    r2 = np.full((NH, NW), np.inf, np.float32); np.minimum.at(r2, (i[beyond], j[beyond]), r[beyond].astype(np.float32))
    tree = cKDTree(Q)
    rows = np.arange(int((LAT_LO + 90) / RES), int((LAT_HI + 90) / RES))
    lat = (rows + 0.5) * math.radians(RES) - math.pi / 2; lon = (np.arange(NW) + 0.5) * math.radians(RES) - math.pi
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    U = np.stack([np.cos(LA) * np.cos(LO), np.sin(LA), np.cos(LA) * np.sin(LO)], -1).reshape(-1, 3)
    R1 = r1[rows].ravel(); R2 = r2[rows].ravel(); has = np.isfinite(R1)
    r1c = np.zeros_like(R1); r2c = np.full_like(R2, np.inf)
    steps = np.arange(0.0, 14.01, 0.25)
    # outward from r1: first radius with distance >= c
    idx = np.nonzero(has)[0]; done = np.zeros(len(idx), bool); res1 = R1[idx] + 14.0
    for s in steps:
        todo = ~done
        if not todo.any(): break
        pts = U[idx[todo]] * (R1[idx[todo]] + s)[:, None]; d, _ = tree.query(pts, workers=-1)
        hit = d >= c; k = np.nonzero(todo)[0][hit]; res1[k] = R1[idx[k]] + s; done[k] = True
    r1c[idx] = res1
    # inward from r2: first radius with distance >= c
    idx = np.nonzero(np.isfinite(R2))[0]; done = np.zeros(len(idx), bool); res2 = R2[idx] - 14.0
    for s in steps:
        todo = ~done
        if not todo.any(): break
        pts = U[idx[todo]] * (R2[idx[todo]] - s)[:, None]; d, _ = tree.query(pts, workers=-1)
        hit = d >= c; k = np.nonzero(todo)[0][hit]; res2[k] = R2[idx[k]] - s; done[k] = True
    r2c[idx] = res2
    full1 = np.zeros((NH, NW), np.float32); full2 = np.full((NH, NW), np.inf, np.float32)
    full1[rows] = r1c.reshape(len(rows), NW); full2[rows] = r2c.reshape(len(rows), NW)
    return r1, r2, full1, full2

if __name__ == "__main__":
    C = 3.0; t0 = time.time(); elevs = list(range(0, 181, 15)); out = {k: [] for k in ("t_r1", "t_r2", "t_r1c", "t_r2c")}
    for e in elevs:
        P = posed(dict(plane=30, elev=e, axial=0, flex=30, pron=0)); m = ray_maps(P, Fc[~ARMF], C)
        for k, v in zip(("t_r1", "t_r2", "t_r1c", "t_r2c"), m): out[k].append(v)
        print(f"trunk elev {e}: {time.time() - t0:.0f}s", flush=True)
    out = {k: np.stack(v) for k, v in out.items()}
    P = posed(dict(plane=0, elev=0, axial=0, flex=30, pron=0)); m = ray_maps(P, Fc[ARMF], C)
    for k, v in zip(("a_r1", "a_r2", "a_r1c", "a_r2c"), m): out[k] = v
    np.savez_compressed("radial_maps.npz", res=RES, elevs=np.array(elevs), clear=C, **out)
    print("saved", {k: v.shape for k, v in out.items()}, f"{time.time() - t0:.0f}s")
