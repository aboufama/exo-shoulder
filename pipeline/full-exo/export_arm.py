import numpy as np, trimesh, json
from load_arm import load
parts = load(); sc = trimesh.Scene(); info = {}
for k, (name, inst, s) in enumerate(parts):
    if s.Volume() < 1: continue
    vs, tr = s.tessellate(0.05, 0.1); P = np.array([[v.x, v.y, v.z] for v in vs]) * 0.001
    m = trimesh.Trimesh(P, tr, process=False); _ = m.vertex_normals
    col = [235, 235, 232, 255] if "CUFF" in name else [30, 30, 32, 255]
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=col, metallicFactor=0.0 if "CUFF" in name else 0.6, roughnessFactor=0.5))
    sc.add_geometry(m, node_name=f"{k:02d} {name}", geom_name=f"{k:02d} {name}")
sc.export("arm_parts.glb"); print("ok")
for nm in ("FOREARM CUFF", "BOTTOM", "MIDDLE"):
    s = [p for p in parts if p[0] == nm][0][2]; sc2 = trimesh.Scene()
    vs, tr = s.tessellate(0.03, 0.08); P = np.array([[v.x, v.y, v.z] for v in vs]) * 0.001; m = trimesh.Trimesh(P, tr, process=False); m.apply_translation(-m.bounds.mean(0)); _ = m.vertex_normals
    m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[225, 225, 222, 255], metallicFactor=0.0, roughnessFactor=0.45)); sc2.add_geometry(m)
    sc2.export(nm.replace(" ", "_").lower() + ".glb")
