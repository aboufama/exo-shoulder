"""Posed scene of a design for rendering: every exo part transformed to the world (body rig frame, mm) at one clip
frame, optionally with the posed body. Node names keep "<group>|<part>|k".

    python3 scene_export.py <design dir> <clip index> <frame> <out.glb> [--body]
"""
import json, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg")); import body_pose as BP
def frame_xforms(fr):
    """world transforms (R, t) per group for one clip frame"""
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))
    L = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json")))
    sg, _ = BP.segs(L["landmarks"], L["scale"], pose)
    X = {g: (np.array(G).reshape(3, 3), np.zeros(3)) for g, G in fr["G"].items()}
    X["H"] = (np.array(sg[2][0]), np.array(sg[2][1])); X["F"] = (np.array(sg[3][0]), np.array(sg[3][1]))
    return X, pose
def posed_scene(DD, ci, fi, body=False):
    C = json.load(open(os.path.join(DD, "clips.json"))); fr = C["clips"][ci]["frames"][fi]; X, pose = frame_xforms(fr)
    src = trimesh.load(os.path.join(DD, "exo.glb")); sc = trimesh.Scene()
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g = node.split("|")[0]
        if g not in X: continue
        m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]; m.vertices = m.vertices @ R.T + t
        sc.add_geometry(m, node_name=node, geom_name=node)
    if body:
        V = BP.posed(pose); sc.add_geometry(trimesh.Trimesh(V, BP.F, process=False), node_name="BODY|skin|0", geom_name="BODY|skin|0")
    return sc
if __name__ == "__main__":
    DD, ci, fi, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    posed_scene(DD, ci, fi, "--body" in sys.argv).export(out); print("wrote", out)
