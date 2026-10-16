"""Re-cut the user's BOTTOM of an existing L1 design with the fixed slicer (build_pinknee_l1.slice_capped), in place.

The L1 builders (build_pinknee_l1 -> build_minarc_l1) cut BOTTOM square to the arm where the knee's swept parts would meet
it. Until 2026-10-16 the cut mesh was 7 open pieces (R7 FAIL): the inherited BOTTOM tessellation (from
l1_seed-offset-3r-slides) carries 6 zero-area slivers, the slicer worked on the unmerged mesh and each cut loop was capped
by a centroid fan (overlapping itself on the channel's non-convex section). This tool takes the SAME source BOTTOM and the
SAME cut plane (recovered from the design's own cut mesh: its new vertices all lie on the plane), re-cuts it with the
fixed slicer and swaps only that mesh in exo.glb (every other node unchanged, same node names and order). An uncut BOTTOM
(the same inherited mesh) is only cleaned: vertices merged and the zero-area slivers dropped, geometry unchanged.

    python3 pipeline/concept_l1/repair_cut_bottom.py <design id> [--dry]
"""
import json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_pinknee_l1 as PK                                                       # noqa: E402

def _write(sc, nodes, bn, new, glb):
    out = trimesh.Scene()
    for node in nodes:                                                                       # same names, same order; meshes baked in the node frame
        T_, gn = sc.graph[node]; m = sc.geometry[gn].copy(); m.apply_transform(T_)
        if node == bn: m = new
        out.add_geometry(m, node_name=node, geom_name=node)
    out.export(glb)


def main():
    did = sys.argv[1]; dry = "--dry" in sys.argv
    dd = os.path.join(PK.FULL, "designs", did); glb = os.path.join(dd, "exo.glb")
    sc = trimesh.load(glb); nodes = list(sc.graph.nodes_geometry)
    bn = [n for n in nodes if n.startswith("H|BOTTOM")]
    assert len(bn) == 1, f"{did}: expected one H|BOTTOM node, got {bn}"
    bn = bn[0]
    T_, gn = sc.graph[bn]; cur = sc.geometry[gn].copy(); cur.apply_transform(T_)
    if "cut square to the arm" not in bn:                                                    # uncut: the same mesh, cleaned (merged, the 6 zero-area slivers dropped)
        new = trimesh.Trimesh(np.asarray(cur.vertices, float), np.asarray(cur.faces), process=False); new.merge_vertices()
        new.update_faces(new.nondegenerate_faces()); new.remove_unreferenced_vertices()
        old_m = trimesh.Trimesh(np.asarray(cur.vertices), np.asarray(cur.faces), process=True)
        rep = dict(design=did, mode="uncut: cleaned only (geometry unchanged: zero-area faces dropped, vertices merged)",
                   before=dict(watertight=bool(old_m.is_watertight), pieces=int(len(old_m.split(only_watertight=False)))),
                   after=dict(watertight=bool(new.is_watertight), is_volume=bool(new.is_volume), pieces=int(len(new.split(only_watertight=False))), volume_cm3=round(float(new.volume) / 1000, 3)))
        print(json.dumps(rep)); assert new.is_watertight and new.is_volume and rep["after"]["pieces"] == 1
        if not dry: _write(sc, nodes, bn, new, glb); print(f"{did}: BOTTOM cleaned in exo.glb")
        return
    src = [m for g, n, m in PK.user_parts() if n.startswith("BOTTOM")][0]                  # the builders' source (rest frame H)
    Vc = np.asarray(cur.vertices, float); d = cKDTree(np.asarray(src.vertices, float)).query(Vc)[0]
    on = Vc[d > 1e-3]                                                                        # cut points + old fan centroids: on the plane
    o = on.mean(0); _, sv, vt = np.linalg.svd(on - o); n = vt[2]
    flat = float(np.abs((on - o) @ n).max())
    if ((Vc[d <= 1e-3] - o) @ n).mean() < 0: n = -n                                          # the kept (distal) side is +n
    new = PK.slice_capped(src, o, n)
    old_m = trimesh.Trimesh(Vc, np.asarray(cur.faces), process=True)
    rep = dict(design=did, plane_fit_points=int(len(on)), plane_flatness_mm=round(flat, 6), plane_normal_rest=np.round(n, 6).tolist(),
               before=dict(watertight=bool(old_m.is_watertight), pieces=int(len(old_m.split(only_watertight=False))), volume_cm3=round(abs(old_m.volume) / 1000, 3)),
               after=dict(watertight=bool(new.is_watertight), is_volume=bool(new.is_volume), pieces=int(len(new.split(only_watertight=False))),
                          volume_cm3=round(float(new.volume) / 1000, 3), faces=int(len(new.faces))))
    print(json.dumps(rep, indent=1))
    assert new.is_watertight and new.is_volume and rep["after"]["pieces"] == 1, "re-cut BOTTOM is not one closed solid"
    assert flat < 1e-3, f"cut vertices are not planar ({flat} mm)"
    if dry: return
    _write(sc, nodes, bn, new, glb)
    bj = os.path.join(dd, "build.json")
    if os.path.exists(bj):
        B = json.load(open(bj)); b = B.get("mount", {}).get("bottom")
        if b is not None:
            b["bottom_watertight_after_cut"] = True
            b["recut_2026_10_16"] = dict(tool="pipeline/concept_l1/repair_cut_bottom.py (slice_capped)", **rep)
            json.dump(B, open(bj, "w"), indent=1, default=float)
    print(f"{did}: BOTTOM re-cut in exo.glb ({len(nodes)} nodes kept)")

if __name__ == "__main__":
    main()
