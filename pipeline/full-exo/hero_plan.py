"""Hero stills of a whole design on the display mannequin: every exo part (the shoulder chain and the user's arm parts)
posed at one clip frame, the matte-black mannequin (mannequin.py: rig skin + featureless head), three cameras framing
the shoulder and the arm. Same look and renderer as the film (joint-render/render_stills.py on exo-blender-cycles).

    python3 hero_plan.py <design dir> <clip name> <frame fraction 0..1> <out dir>     -> out/scene.glb + out/motion.json
The fraction is moved to the nearest followed (not held) frame of that clip. GRID (mm, default 0.25) clusters vertices
to keep the payload under RunPod's 10 MB request limit.
"""
import json, math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
import scene_export as SE, body_pose as BP, mannequin as MQ

DD, clipname, frac, OUT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]; os.makedirs(OUT, exist_ok=True)
C = json.load(open(os.path.join(DD, "clips.json"))); ci = [c["name"] for c in C["clips"]].index(clipname); fr = C["clips"][ci]["frames"]
fi = int(frac * (len(fr) - 1)); ok = [k for k, f in enumerate(fr) if not f.get("held")]
if ok: fi = min(ok, key=lambda k: abs(k - fi))
GRID = float(os.environ.get("GRID", 0.25))
sc = SE.posed_scene(DD, ci, fi, body=False); out = trimesh.Scene()
for n in sc.graph.nodes_geometry:                                                    # vertex clustering per part
    g = sc.graph[n][1]; m = sc.geometry[g]; v = m.vertices
    q = np.round(v / GRID).astype(np.int64); u, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()
    fa = inv[m.faces]; fa = fa[(fa[:, 0] != fa[:, 1]) & (fa[:, 1] != fa[:, 2]) & (fa[:, 0] != fa[:, 2])]
    vv = np.zeros((len(u), 3)); np.add.at(vv, inv, v); vv /= np.bincount(inv, minlength=len(u))[:, None]
    out.add_geometry(trimesh.Trimesh(vv.astype(np.float32), fa, process=False), node_name=n, geom_name=n)
pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr[fi]["p"]))
if not os.path.exists(MQ.OUT): json.dump(MQ.build(), open(MQ.OUT, "w"), separators=(",", ":"))
MQM = MQ.Mannequin(); Vb = MQM.verts(BP.posed(pose))
out.add_geometry(trimesh.Trimesh(Vb.astype(np.float32), MQM.F, process=False), node_name="BODY|mannequin|0", geom_name="BODY|mannequin|0")
out.export(os.path.join(OUT, "scene.glb"))
# cameras: rig frame x anterior, y up, z right (lateral); GH = origin. Frame the shoulder + upper arm + elbow.
P = np.concatenate([out.geometry[g].vertices for n in out.graph.nodes_geometry for g in [out.graph[n][1]] if not n.startswith("BODY")])
lo, hi = np.percentile(P, 2, 0), np.percentile(P, 98, 0); c = 0.5 * (lo + hi); r = 0.5 * np.linalg.norm(hi - lo)
def cam(dirv, fov, tight=1.0, tgt=None):
    d = np.array(dirv, float); d /= np.linalg.norm(d); t = c if tgt is None else np.array(tgt, float)
    dist = tight * r / math.tan(math.radians(fov) / 2) * 1.1
    return dict(pos=(t + d * dist).tolist(), target=t.tolist(), fov=fov, focus=float(dist), fstop=8.0)
frames = [dict(cam=cam((0.55, 0.25, 0.80), 30)),                                      # front-lateral three-quarter, whole assembly
          dict(cam=cam((-0.60, 0.35, 0.72), 30)),                                     # back-lateral three-quarter
          dict(cam=cam((0.10, 0.55, 0.83), 22, tight=0.55, tgt=[0.0, 20.0, 30.0]))]   # the shoulder joints from above-lateral
json.dump(dict(fps=1, body=True, frames=frames, lights_centre=c.tolist(), light_scale=max(0.8, r / 90.0), exposure=-0.1),
          open(os.path.join(OUT, "motion.json"), "w"), indent=1)
print("wrote", OUT, f"clip {clipname} frame {fi} pose {pose}", "centre", np.round(c, 1), "radius", round(r, 1),
      f"{os.path.getsize(os.path.join(OUT, 'scene.glb')) / 1e6:.1f} MB")
