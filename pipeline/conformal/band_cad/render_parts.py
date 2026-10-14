"""quick shaded renders of a stage GLB (matplotlib, no GPU): one panel per member group + hardware"""
import sys, numpy as np, trimesh, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
src, png = sys.argv[1], sys.argv[2]
sc = trimesh.load(src); groups = {}
for node in sc.graph.nodes_geometry:
    T_, g = sc.graph[node]; m = sc.geometry[g].copy(); m.apply_transform(T_); groups.setdefault(node.split("|")[0], []).append((node, m))
keys = sorted(groups); fig = plt.figure(figsize=(5 * len(keys), 5))
L = np.array([0.4, -0.5, 0.75]); L /= np.linalg.norm(L)
for k_, g in enumerate(keys):
    ax = fig.add_subplot(1, len(keys), k_ + 1, projection="3d"); allv = []
    for node, m in groups[g]:
        tri = m.vertices[m.faces]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        sh = 0.35 + 0.65 * np.clip(np.abs(n @ L), 0, 1); col = np.c_[sh * 0.72, sh * 0.74, sh * 0.78, np.ones(len(sh))]
        if "washer" in node or "sleeve" in node: col[:, :3] = np.c_[sh * 0.9, sh * 0.6, sh * 0.25]
        ax.add_collection3d(Poly3DCollection(tri, facecolors=col, edgecolor="none")); allv.append(m.vertices)
    V = np.concatenate(allv); c = V.mean(0); r = (V.max(0) - V.min(0)).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r); ax.set_title(g); ax.view_init(elev=float(sys.argv[3]) if len(sys.argv) > 3 else 25, azim=float(sys.argv[4]) if len(sys.argv) > 4 else -60); ax.set_axis_off()
plt.tight_layout(); plt.savefig(png, dpi=110); print("saved", png)
