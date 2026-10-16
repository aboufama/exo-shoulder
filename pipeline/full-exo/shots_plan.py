"""Generation-winner stills, shot by shot: one posed scene (scene.glb + motion.json for joint-render/render_stills.py on
exo-blender-cycles) per pose, with cameras aimed at the shoulder chain or at the whole exo. Unlike hero_plan.py (clip
frames only, three fixed cameras), a pose can come from the design's workspace.json (a pose the verified model reaches
but a clip does not follow), with the body pose (elbow, pronation) overridden: the shoulder chain depends only on the
humerus, the arm groups H / F are recomputed from the body pose.

    python3 shots_plan.py <design dir> <out dir> '<spec json>'
spec: {"pose": {"clip": "<name>", "frame": k} | {"workspace": i, "p": [plane, elev, axial, flex, pron]},
       "cams": [{"dir": [x, y, z] | "auto" (normal of the aimed parts' plane, away from the body; + "bias": [x, y, z])
                 | "axis" (the aimed node's own axis - its least principal direction, e.g. a hub cap's - pointing away from the
                   nearest skin; "flip": true looks from the skin side, for a bodyless underside view),
                 "fov": deg, "aim": "chain" | "all" | "l3+l4" (groups) | "node:<substr>;<substr>" (nodes whose name holds one),
                 "tight": 1.0, "shift": [dx, dy, dz], "fstop": 8}],
       "drop": [<substr>, ...] (optional: leave out the nodes whose name holds one, e.g. a cap for a cap-off view),
       "body": true (false hides the mannequin in the render; clearance is still measured),
       "skin": {...optional mannequin material override, see render_stills.py}}
Rig frame: x anterior, y up, z lateral (right), GH at the origin, mm. Chain = the shoulder groups (base, l1..l4).
Also writes clearance.json: the deepest exo vertex inside the posed mannequin (winding number) per part group.
"""
import json, math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
import scene_export as SE, body_pose as BP, mannequin as MQ

DD, OUT, SPEC = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]); os.makedirs(OUT, exist_ok=True)
GRID = float(os.environ.get("GRID", 0.2)); CHAIN = ("base", "l1", "l1a", "l1b", "l2", "l3", "l4")   # l1a / l1b: a chain split at a knuckle (minarc)
ps = SPEC["pose"]
if "clip" in ps:
    C = json.load(open(os.path.join(DD, "clips.json"))); fr = [c for c in C["clips"] if c["name"] == ps["clip"]][0]["frames"][ps["frame"]]
    assert not fr.get("held"), "held frame: the exo does not follow this clip frame"
else:
    W = json.load(open(os.path.join(DD, "workspace.json"))); fr = dict(W["poses"][ps["workspace"]])
    assert fr["closes"] and fr.get("eval_feasible"), "workspace pose not feasible in the verified model"
    if "p" in ps:
        assert np.allclose(ps["p"][:3], fr["p"][:3]), "only the elbow / forearm may be overridden"
        fr["p"] = ps["p"]
X, pose = SE.frame_xforms(fr); src = trimesh.load(os.path.join(DD, "exo.glb")); out = trimesh.Scene(); parts = {}; nodes = {}
for node in src.graph.nodes_geometry:
    T_, gn = src.graph[node]; g = node.split("|")[0]
    if g not in X or any(k in node for k in SPEC.get("drop", [])): continue
    m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]; v = m.vertices @ R.T + t
    q = np.round(v / GRID).astype(np.int64); u, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()   # vertex clustering (payload)
    fa = inv[m.faces]; fa = fa[(fa[:, 0] != fa[:, 1]) & (fa[:, 1] != fa[:, 2]) & (fa[:, 0] != fa[:, 2])]
    vv = np.zeros((len(u), 3)); np.add.at(vv, inv, v); vv /= np.bincount(inv, minlength=len(u))[:, None]
    out.add_geometry(trimesh.Trimesh(vv.astype(np.float32), fa, process=False), node_name=node, geom_name=node)
    parts.setdefault(g, []).append(vv); nodes[node] = vv
if not os.path.exists(MQ.OUT): json.dump(MQ.build(), open(MQ.OUT, "w"), separators=(",", ":"))
MQM = MQ.Mannequin(); Vb = MQM.verts(BP.posed(pose))
out.add_geometry(trimesh.Trimesh(Vb.astype(np.float32), MQM.F, process=False), node_name="BODY|mannequin|0", geom_name="BODY|mannequin|0")
out.export(os.path.join(OUT, "scene.glb"))
# clearance vs the display mannequin: winding number of each exo vertex (inside > 0.5), depth = distance to the surface
try:
    import igl
    Fb = np.asarray(MQM.F, np.int64); clr = {}
    for g, vs in parts.items():
        P = np.concatenate(vs); P = P[:: max(1, len(P) // 6000)]
        wn = igl.fast_winding_number(np.ascontiguousarray(Vb, np.float64), Fb, np.ascontiguousarray(P, np.float64))
        d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(P, np.float64), np.ascontiguousarray(Vb, np.float64), Fb)[0])
        ins = wn > 0.5; clr[g] = dict(inside_n=int(ins.sum()), n=int(len(P)), deepest_mm=round(float(d[ins].max()), 2) if ins.any() else 0.0,
                                      min_gap_mm=round(float(d[~ins].min()), 2) if (~ins).any() else None)
except Exception as e:                                                               # noqa: BLE001
    clr = dict(error=repr(e))
json.dump(dict(pose=fr["p"], clearance=clr), open(os.path.join(OUT, "clearance.json"), "w"), indent=1)
def pts(a):                                                                         # "chain", "all", groups "l3+l4" or "node:<substr>;<substr>"
    if a.startswith("node:"):
        P = [v for n, v in nodes.items() if any(k in n for k in a[5:].split(";"))]; assert P, f"no node matches {a}"; return np.concatenate(P)
    keys = CHAIN if a == "chain" else list(parts) if a == "all" else a.split("+")
    return np.concatenate([np.concatenate(parts[g]) for g in keys if g in parts])
def bound(a):
    P = pts(a); lo, hi = np.percentile(P, 1, 0), np.percentile(P, 99, 0)
    return 0.5 * (lo + hi), 0.5 * float(np.linalg.norm(hi - lo))
B = dict(chain=bound("chain"), all=bound("all"))
frames = []
for cs in SPEC["cams"]:
    a = cs.get("aim", "all"); c, r = B[a] if a in B else bound(a)
    c = c + np.array(cs.get("shift", (0, 0, 0)), float); fov = cs.get("fov", 30)
    if cs["dir"] == "axis":                                                         # the aimed node's own axis, away from the nearest skin
        P = pts(a); P = P - P.mean(0); nrm = np.linalg.svd(P[:: max(1, len(P) // 20000)], full_matrices=False)[2][2]
        near = Vb[np.argmin(((Vb - c) ** 2).sum(1))]
        if nrm @ (c - near) < 0: nrm = -nrm
        if cs.get("flip"): nrm = -nrm
        d = nrm + np.array(cs.get("bias", (0, 0, 0)), float)
    elif cs["dir"] == "auto":                                                       # along the normal of the aimed parts' best-fit plane,
        P = pts("chain" if a in ("chain", "all") or a.startswith("node:") else a)
        P = P[:: max(1, len(P) // 20000)]; nrm = np.linalg.svd(P - P.mean(0), full_matrices=False)[2][2]
        if nrm @ (P.mean(0) - Vb.mean(0)) < 0: nrm = -nrm                                # on the side away from the body
        d = nrm + np.array(cs.get("bias", (0, 0, 0)), float)
    else: d = np.array(cs["dir"], float)
    d /= np.linalg.norm(d); dist = cs.get("tight", 1.0) * r / math.tan(math.radians(fov) / 2) * 1.1
    frames.append(dict(cam=dict(pos=(c + d * dist).tolist(), target=c.tolist(), fov=fov, focus=float(dist), fstop=cs.get("fstop", 8.0))))
ca, ra = B["all"]
mo = dict(fps=1, body=bool(SPEC.get("body", True)), frames=frames, lights_centre=ca.tolist(), light_scale=max(0.8, ra / 90.0), exposure=SPEC.get("exposure", -0.1))
if "skin" in SPEC: mo["skin"] = SPEC["skin"]
json.dump(mo, open(os.path.join(OUT, "motion.json"), "w"), indent=1)
print("wrote", OUT, "pose", np.round(fr["p"], 1).tolist(), "chain c/r", np.round(B["chain"][0], 1).tolist(), round(B["chain"][1], 1),
      "all r", round(ra, 1), f"{os.path.getsize(os.path.join(OUT, 'scene.glb')) / 1e6:.1f} MB", "clearance", json.dumps(clr))
