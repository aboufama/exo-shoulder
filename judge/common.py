"""shared helpers for the judges: repo paths, a design's parts (exo.glb, per group, in the group's rest frame) and its frames"""
import json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PIPE = os.path.join(REPO, "pipeline")
for _p in ("avg", "full-exo"): sys.path.insert(0, os.path.join(PIPE, _p))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def design_dir(arg):
    return arg if os.path.isdir(arg) else os.path.join(PIPE, "full-exo", "designs", arg)

def load_parts(dd):
    """[(group, name, V (n,3) float64, F (m,3))] from exo.glb, vertices in the group's frame (scene_export convention)"""
    import trimesh
    src = trimesh.load(os.path.join(dd, "exo.glb")); out = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g, nm = node.split("|")[:2]; m = src.geometry[gn]
        V = (np.c_[m.vertices, np.ones(len(m.vertices))] @ T_.T)[:, :3]
        o = out.setdefault((g, nm), [[], [], 0]); o[0].append(V); o[1].append(np.asarray(m.faces) + o[2]); o[2] += len(V)
    return [(g, nm, np.concatenate(v[0]), np.concatenate(v[1])) for (g, nm), v in out.items()]

def frames(dd, step=1):
    """yield (clip name, frame index, frame dict) for every step-th frame of every clip (held frames included)"""
    C = json.load(open(os.path.join(dd, "clips.json")))
    for c in C["clips"]:
        for fi in range(0, len(c["frames"]), step): yield c["name"], fi, c["frames"][fi]

def is_hardware(name):
    n = name.lower()
    return any(k in n for k in ("screw", "washer", "sleeve", "magnet", "ring nut", "pcb", "sensor ic", "igus", "dowel", "cirpattern", "revolve"))
