"""per-part GLBs of a fair-CAD design's custom parts (from out_<key>/step/*.step) -> full-exo/designs/cad_<key>/parts/ + parts.json"""
import os, sys, json
import numpy as np, cadquery as cq, trimesh
KEY = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, f"out_{KEY}", "step")
DST = os.path.join(HERE, "..", "..", "full-exo", "designs", f"cad_{KEY}", "parts"); os.makedirs(DST, exist_ok=True)
P = json.load(open(os.path.join(HERE, f"out_{KEY}", "parts.json")))["parts"]
rows = []
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".step"): continue
    s = cq.importers.importStep(os.path.join(SRC, f)).val(); vs, tr = s.tessellate(0.02, 0.06)
    V = np.array([[q.x, q.y, q.z] for q in vs]); m = trimesh.Trimesh(V, tr, process=False)
    c = V.mean(0); m.vertices = V - c; name = f[:-5]
    full = next((p for p in P if p["name"].startswith(name.replace("_", "/")) or p["name"].split(" ")[0] == name), None)
    m.export(os.path.join(DST, f"{name}.glb")); bb = s.BoundingBox()
    rows.append(dict(file=f"{name}.glb", name=full["name"] if full else name, material=full["material"] if full else "", mass_g=full["mass_g"] if full else None,
                     faces=len(s.Faces()), valid=bool(s.isValid()), size=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]))
    print(name, rows[-1]["faces"], "faces", rows[-1]["size"])
json.dump(rows, open(os.path.join(DST, "parts.json"), "w"), indent=1)
