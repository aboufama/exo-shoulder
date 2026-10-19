"""Part cards of a built design: every part of pipeline/full-exo/designs/<id>/exo.glb drawn alone on white - a
true-scale plan view (looking along the part's thinnest axis, overall dimension lines + a scale bar) beside a small iso
view - plus parts.json (title, full CAD description, quantity, body, material, mass, oriented size) for the blueprint
page. Identical parts (same geometry and material) share one card with their quantity. Cheap matplotlib drawing
(painter's order, crease + silhouette edges), not a render.

    OMP_NUM_THREADS=1 nice python3 tools/part_cards.py <design id> [out dir, default docs/blueprints/parts/<id>]
"""
import io, json, os, re, sys
import numpy as np
import trimesh
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = sys.argv[1]
DD = os.path.join(REPO, "pipeline", "full-exo", "designs", ID)
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "docs", "blueprints", "parts", ID)
INK = (0.17, 0.19, 0.22)
BODY = {"base": "base (on the scapula handler)", "l1": "link 1", "l1a": "link 1a", "l1b": "link 1b", "dk": "knuckle drive",
        "l2": "link 2", "l3": "member 3", "l4": "knee link", "H": "arm pad / cuff (BOTTOM)", "F": "forearm cuff"}


def finish(mat, name):
    """(base RGB, specular) in the user's render style: bead-blasted metal, polished steel, iglidur orange, no black"""
    m, n = mat.lower(), name.lower()
    if "iglidur" in m or "igus" in n or "iglide" in n:
        return (0.93, 0.52, 0.16), 0.05
    if "magnet" in n:
        return (0.62, 0.63, 0.66), 0.25
    if "screw" in n or "polished" in m or "bearing steel" in m or "spring" in m:
        return (0.76, 0.78, 0.81), 0.16
    if mat == "user part":
        return (0.80, 0.78, 0.74), 0.05
    return (0.67, 0.69, 0.72), 0.08          # Ti-6Al-4V, 17-4PH, 7075-T6, AlSi10Mg: bead blasted


def obb_local(m):
    """vertices in the part's oriented-bounding-box frame, axes sorted longest -> thinnest, handedness kept"""
    T, ext = trimesh.bounds.oriented_bounds(m)
    v = trimesh.transform_points(m.vertices, T)
    order = np.argsort(-np.asarray(ext)); v = v[:, order]; ext = np.asarray(ext)[order]
    if np.linalg.det(np.eye(3)[order]) < 0:
        v[:, 2] *= -1
    return v - (v.max(0) + v.min(0)) / 2, ext


def polys(v, faces, base, spec, R):
    """face + edge polygons of the mesh seen along -z after rotation R, sorted far -> near"""
    w = v @ R.T
    tri = w[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nl = np.linalg.norm(n, axis=1); ok = nl > 1e-12
    n[ok] /= nl[ok, None]
    front = n[:, 2] >= 0
    ns = n * np.where(front, 1, -1)[:, None]
    l1 = np.array([-0.45, 0.55, 1.0]); l1 /= np.linalg.norm(l1)
    l2 = np.array([0.6, -0.35, 0.5]); l2 /= np.linalg.norm(l2)
    h = l1 + np.array([0, 0, 1.0]); h /= np.linalg.norm(h)
    I = 0.40 + 0.50 * np.clip(ns @ l1, 0, 1) + 0.16 * np.clip(ns @ l2, 0, 1)
    col = np.clip(np.asarray(base)[None, :] * I[:, None] + spec * np.clip(ns @ h, 0, 1)[:, None] ** 24, 0, 1)
    depth = tri[:, :, 2].mean(1)
    items = [(depth[i], tri[i, :, :2], col[i], col[i], 0.3) for i in np.nonzero(ok)[0]]
    mesh = trimesh.Trimesh(v, faces, process=False)
    try:
        adj = mesh.face_adjacency; ang = mesh.face_adjacency_angles; edges = mesh.face_adjacency_edges
        sil = front[adj[:, 0]] != front[adj[:, 1]]
        keep = (ang > np.radians(28)) | sil
        for (a, b), (e0, e1) in zip(adj[keep], edges[keep]):
            d = max(depth[a], depth[b]) + 1e-3
            items.append((d, w[[e0, e1], :2], (0, 0, 0, 0), INK, 0.55))
    except Exception:
        pass
    items.sort(key=lambda t: t[0])
    return items


def draw(ax, items):
    pc = PolyCollection([t[1] for t in items], facecolors=[t[2] for t in items], edgecolors=[t[3] for t in items],
                        linewidths=[t[4] for t in items], closed=True, antialiased=True)
    ax.add_collection(pc)


def nice_bar(span):
    for b in (1, 2, 5, 10, 20, 50, 100, 200):
        if b >= span * 0.22:
            return b
    return 200


def dim_h(ax, x0, x1, y, txt, off):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color=INK, shrinkA=0, shrinkB=0, mutation_scale=7))
    ax.text((x0 + x1) / 2, y - off * 0.25, txt, ha="center", va="top", fontsize=8.5, color=INK)


def dim_v(ax, x, y0, y1, txt, off):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<|-|>", lw=0.7, color=INK, shrinkA=0, shrinkB=0, mutation_scale=7))
    ax.text(x + off * 0.25, (y0 + y1) / 2, txt, ha="left", va="center", fontsize=8.5, color=INK, rotation=90)


def card(v, faces, ext, base, spec, path):
    fig = plt.figure(figsize=(7.2, 3.9), dpi=110, facecolor="white")
    a1 = fig.add_axes([0.02, 0.04, 0.60, 0.92]); a2 = fig.add_axes([0.64, 0.10, 0.34, 0.80])
    plan = polys(v, faces, base, spec, np.eye(3))
    draw(a1, plan)
    L, W = ext[0], ext[1]; off = max(L, W) * 0.09 + 0.6
    dim_h(a1, -L / 2, L / 2, -W / 2 - off, f"{L:.1f} mm", off)
    dim_v(a1, L / 2 + off, -W / 2, W / 2, f"{W:.1f} mm", off)
    bar = nice_bar(L)
    bx, by = -L / 2, W / 2 + off * 1.1
    a1.plot([bx, bx + bar], [by, by], color=INK, lw=2.2, solid_capstyle="butt")
    for t in range(bar + 1) if bar <= 10 else range(0, bar + 1, bar // 5 if bar >= 5 else 1):
        a1.plot([bx + t, bx + t], [by, by - off * 0.18], color=INK, lw=0.6)
    a1.text(bx + bar + off * 0.3, by, f"{bar} mm", va="center", fontsize=8.5, color=INK)
    a1.set_xlim(-L / 2 - off * 0.8, L / 2 + off * 2.4); a1.set_ylim(-W / 2 - off * 2.0, W / 2 + off * 2.0)
    a1.set_aspect("equal"); a1.axis("off")
    az, tilt = np.radians(35), np.radians(-58)          # turn about the thin axis, then tip the plan face away
    Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(tilt), -np.sin(tilt)], [0, np.sin(tilt), np.cos(tilt)]])
    R = Rx @ Rz
    iso = polys(v, faces, base, spec, R)
    draw(a2, iso)
    P = (v @ R.T)[:, :2]; c = (P.max(0) + P.min(0)) / 2; s = (P.max(0) - P.min(0)).max() * 0.56 + 1e-6
    a2.set_xlim(c[0] - s, c[0] + s); a2.set_ylim(c[1] - s, c[1] + s); a2.set_aspect("equal"); a2.axis("off")
    a2.text(c[0], P[:, 1].min() - s * 0.08, "3D view (not to scale)", ha="center", va="top", fontsize=7.5, color=(0.45, 0.47, 0.5))
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor="white"); plt.close(fig)
    im = Image.open(buf).convert("RGB")
    box = Image.eval(im.convert("L"), lambda x: 255 if x < 250 else 0).getbbox()      # crop the white margins
    if box:
        pad = 14; im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
    im = im.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)


def title_of(desc):
    """short card title from the CAD part description: the drawing number + name of a made part, the catalogue part
    of a bought one, cut at a clause boundary (never mid-phrase); the full description stays in parts.json"""
    t = desc.strip()
    m = re.match(r"^(D\d+-\d+[a-z]?)\s+([^:(]+)", t)
    if m:
        return f"{m.group(1)} {m.group(2).strip().rstrip(',')}"
    t = re.split(r":\s| \(|, ", t, maxsplit=1)[0]
    return t.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    scene = trimesh.load(os.path.join(DD, "exo.glb"))
    meshes = scene.dump(concatenate=False)
    pf = {p["k"]: p for p in json.load(open(os.path.join(DD, "parts_full.json")))["parts"]}
    groups = {}
    for m in meshes:
        name = m.metadata.get("name", "")
        bits = name.split("|")
        grp, desc, k = bits[0], "|".join(bits[1:-1]) or name, int(bits[-1]) if bits[-1].isdigit() else -1
        p = pf.get(k, {}); mat = p.get("material", "")
        sig = (round(float(m.area), 1), len(m.faces), mat, grp in ("H", "F") and mat == "user part")
        g = groups.setdefault(sig, {"ks": [], "descs": [], "bodies": [], "mesh": m, "mat": mat, "mass": p.get("mass_g"), "k0": k, "desc0": desc})
        if k < g["k0"]:
            g.update(k0=k, desc0=desc, mesh=m)
        g["ks"].append(k); g["descs"].append(desc); g["bodies"].append(grp)
    rows = []
    for i, g in enumerate(sorted(groups.values(), key=lambda g: min(g["ks"]))):
        m = g["mesh"]; desc = g["desc0"]
        base, spec = finish(g["mat"], desc)
        v, ext = obb_local(m)
        fn = f"{i:03d}.png"
        try:
            card(v, np.asarray(m.faces), ext, base, spec, os.path.join(OUT, fn))
        except Exception as e:  # a degenerate mesh: list it without a picture
            print("skip", desc[:60], e); fn = None
        rows.append({"file": fn, "title": title_of(desc), "desc": desc, "descs": sorted(set(g["descs"])), "qty": len(g["ks"]),
                     "ks": g["ks"], "bodies": sorted(set(BODY.get(b, b) for b in g["bodies"])), "material": g["mat"],
                     "mass_g": g["mass"], "size_mm": [round(float(x), 2) for x in ext], "faces": int(len(m.faces)),
                     "user_part": g["mat"] == "user part"})
        print(f"{i:3d} x{len(g['ks'])} {rows[-1]['title'][:70]}")
    json.dump({"design": ID, "source": f"pipeline/full-exo/designs/{ID}/exo.glb + parts_full.json", "parts": rows},
              open(os.path.join(OUT, "parts.json"), "w"), indent=1)
    print(len(rows), "cards ->", OUT)


if __name__ == "__main__":
    main()
