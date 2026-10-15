import trimesh, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = "/home/user/exo-shoulder/pipeline/full-exo/designs/param2_r20_n3_s1414_4"
src = trimesh.load(f"{D}/exo.glb")
parts = {}
for node in src.graph.nodes_geometry:
    T, gn = src.graph[node]; g, nm = node.split("|")[:2]
    if nm.startswith(("D6-0", "UPPER ARM CUFF")):
        m = src.geometry[gn].copy(); m.apply_transform(T); parts.setdefault(nm, []).append(m)
def edges2d(m, R, keep=(0, 1)):
    V = (m.vertices - m.vertices.mean(0)) @ R.T
    fa = m.face_adjacency; ang = m.face_adjacency_angles
    E = m.face_adjacency_edges[ang > np.radians(25)]
    b = trimesh.grouping.group_rows(m.edges_sorted, require_count=1)   # open boundary edges, if any
    E = np.vstack([E, m.edges_sorted[b]]) if len(b) else E
    return V, E
for nm, ms in sorted(parts.items()):
    m = trimesh.util.concatenate(ms)
    V0 = m.vertices - m.vertices.mean(0); U, S, Vt = np.linalg.svd(V0[::max(1, len(V0)//20000)], full_matrices=False)
    R = Vt.copy(); R[2] = np.cross(R[0], R[1])
    V, E = edges2d(m, R)
    ext = V.max(0) - V.min(0)
    fig, axs = plt.subplots(2, 1, figsize=(11, 8.5), gridspec_kw=dict(height_ratios=[ext[1] + 30, ext[2] + 30]))
    for ax, (i, j, title) in zip(axs, [(0, 1, "VIEW 1 - looking along the part's thinnest direction"), (0, 2, "VIEW 2 - the same part turned 90 deg about its length")]):
        segs = V[E][:, :, [i, j]]
        from matplotlib.collections import LineCollection
        ax.add_collection(LineCollection(segs, colors="#1d2530", linewidths=0.6))
        lo, hi = V[:, [i, j]].min(0), V[:, [i, j]].max(0)
        ax.set_xlim(lo[0] - 20, hi[0] + 20); ax.set_ylim(lo[1] - 22, hi[1] + 14); ax.set_aspect("equal"); ax.axis("off")
        y = lo[1] - 12; ax.annotate("", (lo[0], y), (hi[0], y), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#b4441b"))
        ax.text((lo[0] + hi[0]) / 2, y - 6, f"{hi[0]-lo[0]:.1f} mm", ha="center", va="top", fontsize=10, color="#b4441b")
        x = hi[0] + 10; ax.annotate("", (x, lo[1]), (x, hi[1]), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#b4441b"))
        ax.text(x + 3, (lo[1] + hi[1]) / 2, f"{hi[1]-lo[1]:.1f} mm", va="center", fontsize=10, color="#b4441b")
        ax.set_title(title, loc="left", fontsize=10, color="#1d2530")
        if nm.startswith("D6-04"):
            import sys; sys.path.insert(0, "/home/user/exo-shoulder/pipeline/conformal/band_cad"); import arm_end as AE
            uB, CB = np.asarray(AE.uB, float), np.asarray(AE.CB, float); c0 = m.vertices.mean(0)
            sv = (m.vertices - CB) @ uB; s0 = sv.min()
            P = lambda s_: ((CB + s_ * uB - c0) @ R.T)[[i, j]]
            a, b, cpt = P(s0), P(255.0), P(255.0)
            v1 = (i == 0 and j == 1); yy = hi[1] + 8 if v1 else lo[1] - 42
            ax.plot([b[0], b[0]], [lo[1] - 4, hi[1] + 4], color="#2a6fb0", lw=0.9, ls=(0, (6, 3)))
            ax.text(b[0] + 2, hi[1] + 5, "cut of your BOTTOM bar\n(255.0 mm above the elbow-hinge axis)", fontsize=8, color="#2a6fb0", va="bottom")
            ax.annotate("", (a[0], yy), (b[0], yy), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#2a6fb0"))
            ax.text((a[0] + b[0]) / 2, yy + 2 if v1 else yy - 3, f"BOTTOM bar kept: {255.0 - s0:.1f} mm (eye end to the cut)", ha="center", va="bottom" if v1 else "top", fontsize=9, color="#2a6fb0")
            ax.set_ylim(min(ax.get_ylim()[0], yy - 16), max(ax.get_ylim()[1], hi[1] + 22))
    fig.suptitle(nm, x=0.02, ha="left", fontsize=12, fontweight="bold")
    fig.text(0.02, 0.01, "Outline projected from the CAD solid (feature edges). Overall extents only; the full sheets give every radius, pad and hole.", fontsize=8, color="#555")
    fn = nm.split(" ")[0].replace("-", "_") if nm.startswith("D6") else "cuff"
    fig.savefig(f"{fn}.png", dpi=130, facecolor="white"); plt.close(fig); print(fn, np.round(ext, 1))
