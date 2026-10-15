"""Per-frame data for the Blender film render, from designs/film.json (the same plan the web preview plays).

Writes film_render/: designs.glb (every design's exo parts, nodes "D<k>|<group>|<part>|i", group-local mm) and one
motion file per chunk (frames a..b): camera, which design shows and its swap scale, each group's world transform
(viewer metres), the mannequin's posed vertices (int16, 0.05 mm) and the body faces. Egg head as in film.html.

    python3 film_frames.py [chunk=12]
env FILM=<plan json> (default designs/film.json), FILM_RENDER=<out dir> (default film_render/)
"""
import base64, gzip, json, math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg")); import body_pose as BP
CH = int(sys.argv[1]) if len(sys.argv) > 1 else 12
FILM = json.load(open(os.environ.get("FILM", os.path.join(HERE, "designs", "film.json")))); OUT = os.environ.get("FILM_RENDER", os.path.join(HERE, "film_render")); os.makedirs(OUT, exist_ok=True)
J = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); L, S = J["landmarks"], J["scale"]; HD = J["head"]
# ---- designs into one GLB
sc = trimesh.Scene(); DATA = []; GRID = float(os.environ.get('GRID', 0.25))
for k, d in enumerate(FILM["designs"]):
    src = trimesh.load(os.path.join(HERE, "designs", d["id"], "exo.glb")); DATA.append(json.load(open(os.path.join(HERE, "designs", d["id"], "clips.json"))))
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g0 = src.geometry[gn]; v = np.asarray(g0.vertices, float) @ T_[:3, :3].T + T_[:3, 3]
        q = np.round(v / GRID).astype(np.int64); u, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()   # vertex clustering
        fa = inv[g0.faces]; fa = fa[(fa[:, 0] != fa[:, 1]) & (fa[:, 1] != fa[:, 2]) & (fa[:, 0] != fa[:, 2])]
        vv = np.zeros((len(u), 3)); np.add.at(vv, inv, v); vv /= np.bincount(inv, minlength=len(u))[:, None]
        m = trimesh.Trimesh(vv.astype(np.float32), fa, process=False)
        sc.add_geometry(m, node_name=f"D{k}|{node}", geom_name=f"D{k}|{node}")                              # no normals: Blender smooths
sc.export(os.path.join(OUT, "designs.glb"))
# ---- faceless mannequin head: the head keeps its proportions, its surface is Laplacian-smoothed (no nose, eyes, lips),
#      blended to the untouched neck; the same rule as film.html
F = BP.F; V0 = BP.posed(dict(plane=0, elev=0, axial=0, flex=0, pron=0)); c = np.array(HD["mid"]) * 1.0
r_ax = np.hypot(V0[:, 0] - c[0], V0[:, 2] - c[2]); yrel = V0[:, 1] - c[1]
w_head = np.clip((yrel + 95 * S) / (35 * S), 0, 1) * (r_ax < 150 * S)                    # 0 at the neck, 1 from the jaw up
w_head = w_head * w_head * (3 - 2 * w_head); hidx = np.nonzero(w_head > 0)[0]
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
H = V0[hidx]; tree = cKDTree(H); pairs = tree.query_pairs(24 * S, output_type="ndarray")
ii = np.r_[pairs[:, 0], pairs[:, 1], np.arange(len(H))]; jj = np.r_[pairs[:, 1], pairs[:, 0], np.arange(len(H))]
d2 = np.sum((H[ii] - H[jj]) ** 2, 1); Wk = csr_matrix((np.exp(-d2 / (2 * (10 * S) ** 2)), (ii, jj)), shape=(len(H), len(H)))
Wk = csr_matrix(Wk.multiply(1.0 / np.asarray(Wk.sum(1)).ravel()[:, None]))
hc = H.mean(0) + np.array([-10 * S, 10 * S, 0])                                         # head centre (for the size restore)
def egg(V):                                                                                  # (name kept) faceless head for one frame
    X = V.copy(); Hh = X[hidx]; S_ = Hh
    for _ in range(3): S_ = Wk @ S_
    r0 = np.linalg.norm(Hh - hc, axis=1); r1 = np.linalg.norm(S_ - hc, axis=1) + 1e-9; S_ = hc + (S_ - hc) * (r0 / r1)[:, None]   # keep the size
    X[hidx] = Hh + w_head[hidx][:, None] * (S_ - Hh); return X
CV = np.zeros((0, 3))
# ---- timeline
shots, T = [], 0
for s in FILM["shots"]:
    n = s["f1"] - s["f0"] + 1; shots.append(dict(s, t0=T, n=n)); T += n
NF = min(T, int(os.environ.get("FRAMES_MAX", T))); XF = FILM.get("xfade", 10); ease = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * (3 - 2 * u)
def cam_at(f):
    K = FILM["camera"]; i = 0
    while i < len(K) - 2 and K[i + 1]["f"] <= f: i += 1
    a, b, c_, d = K[max(0, i - 1)], K[i], K[min(len(K) - 1, i + 1)], K[min(len(K) - 1, i + 2)]
    u = min(1, max(0, (f - b["f"]) / max(1, c_["f"] - b["f"])))
    cr = lambda p0, p1, p2, p3: [0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in range(3)]
    return dict(pos=cr(a["pos"], b["pos"], c_["pos"], d["pos"]), target=cr(a["target"], b["target"], c_["target"], d["target"]), fov=b["fov"] + (c_["fov"] - b["fov"]) * u)
frames, verts = [], []
for f in range(NF):
    k = next(j for j, s in enumerate(shots) if s["t0"] <= f < s["t0"] + s["n"]); s = shots[k]; i = f - s["t0"]; D = DATA[s["design"]]
    clip = D["clips"][s["clip"]]["frames"]; fr = clip[min(s["f0"] + i, len(clip) - 1)]
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); sg, lift = BP.segs(L, S, pose)
    scl = 1.0
    if i < XF and k > 0 and shots[k - 1]["design"] != s["design"]: scl = ease(i / XF)
    if i >= s["n"] - XF and k < len(shots) - 1 and shots[k + 1]["design"] != s["design"]: scl = ease((s["n"] - 1 - i) / XF)
    X = {g: (np.array(G).reshape(3, 3), np.zeros(3)) for g, G in fr["G"].items()}; X["H"] = (np.array(sg[2][0]), np.array(sg[2][1])); X["F"] = (np.array(sg[3][0]), np.array(sg[3][1]))
    Xw = {g: np.c_[R * 1e-3 * scl, (t * scl + lift) * 1e-3].round(7).ravel().tolist() for g, (R, t) in X.items()}     # world (m) = 1e-3 (scl (R x + t) + lift)
    frames.append(dict(cam=cam_at(f), design=s["design"], scale=scl, X=Xw, label=FILM["designs"][s["design"]]["label"]))
    verts.append(np.round((egg(BP.posed(pose)) + lift) * 20).astype(np.int16))
    if f % 100 == 0: print("frame", f, "/", NF, flush=True)
faces = base64.b64encode(gzip.compress(F.astype(np.int32).tobytes())).decode()
for a in range(0, NF, CH):
    b = min(NF, a + CH) - 1
    vb = base64.b64encode(gzip.compress(np.stack(verts[a:b + 1]).tobytes())).decode()
    json.dump(dict(fps=FILM["fps"], n_total=NF, a=a, b=b, frames={str(f): frames[f] for f in range(a, b + 1)}, body=dict(faces=faces, nv=int(len(V0)), verts=vb, scale=0.05e-3)),
              open(os.path.join(OUT, f"motion_{a:04d}.json"), "w"), separators=(",", ":"))
json.dump(dict(fps=FILM["fps"], n=NF, chunk=CH), open(os.path.join(OUT, "index.json"), "w"))
print("wrote", NF, "frames in", len(range(0, NF, CH)), "chunks to", OUT)
