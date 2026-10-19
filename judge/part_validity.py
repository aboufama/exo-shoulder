"""JUDGE R7: is every custom part a single valid, closed solid? OCC BRepCheck on the exported STEP (re-imported, as a
supplier would read it), solid count, face count, closed-mesh volume, bounding box.
    python3 judge/part_validity.py <design dir|id>  -> <design>/judge/part_validity.json"""
import json, os, sys
import numpy as np, cadquery as cq, trimesh
from OCP.BRepCheck import BRepCheck_Analyzer
from common import design_dir
dd = design_dir(sys.argv[1]); sd = os.path.join(dd, "step"); rows = []
# The arm-fixed groups H / F hold the user's own parts AND this project's arm-side parts (arm pad, pad mount, pin b retainer,
# the cut BOTTOM, the project's upper-arm cuff). Only the user's own UNMODIFIED parts (names as they come from the user's
# model) and catalogue screws are skipped; everything this project made or cut is judged (until 2026-10-16 the L1 branch
# skipped every H / F part, so the arm pad, pad mount and pin b retainer were never judged).
USER_UNMODIFIED = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
def user_or_catalogue(g, n):
    return g in ("H", "F") and (n.startswith(USER_UNMODIFIED) or "ISO 10642" in n or "screw" in n.lower())
if not os.path.isdir(sd):                                             # L1 keep-out design (meshes only): one closed mesh per part
    from common import load_parts
    for g, n, V, F in load_parts(dd):
        if user_or_catalogue(g, n): continue                           # the user's own unmodified parts + catalogue screws only
        m = trimesh.Trimesh(V, F, process=True); bb = m.bounds[1] - m.bounds[0]
        rows.append(dict(file=f"{g}|{n}", valid=bool(m.is_watertight and m.is_volume), solids=int(len(m.split(only_watertight=False))), faces=len(m.faces), bad_faces=0,
                         watertight=bool(m.is_watertight), volume_cm3=round(abs(m.volume) / 1000, 3), bbox_mm=[round(float(v), 1) for v in bb], level="L1 mesh"))
        r = rows[-1]; print(f"{r['file'][:40]:40s} L1 mesh closed volume {r['valid']!s:5s} pieces {r['solids']} {r['volume_cm3']:7.2f} cm3 {r['bbox_mm']}")
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True)
    print(f"judged {len(rows)} parts ({sum(1 for r in rows if r['file'][0] in 'HF')} arm-fixed custom parts)")
    json.dump(dict(parts=rows, level="L1", all_ok=all(r["valid"] and r["solids"] == 1 for r in rows)), open(os.path.join(dd, "judge", "part_validity.json"), "w"), indent=1)
    sys.exit(0)
for f in sorted(os.listdir(sd)):
    if not f.lower().endswith(".step"): continue
    s = cq.importers.importStep(os.path.join(sd, f)).val(); vs, tr = s.tessellate(0.02, 0.1)
    m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr); m.merge_vertices(); bb = s.BoundingBox()
    bad = sum(1 for fc in s.Faces() if not BRepCheck_Analyzer(fc.wrapped).IsValid())
    rows.append(dict(file=f, valid=bool(s.isValid()), solids=len(s.Solids()), faces=len(s.Faces()), bad_faces=bad, watertight=bool(m.is_watertight),
                     volume_cm3=round(abs(m.volume) / 1000, 3), bbox_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]))
    r = rows[-1]; print(f"{f:14s} valid {r['valid']!s:5s} solids {r['solids']} faces {r['faces']:4d} bad {bad} watertight {r['watertight']!s:5s} {r['volume_cm3']:7.2f} cm3 {r['bbox_mm']}")
cov = None; pfj = os.path.join(dd, "parts_full.json")
if os.path.exists(pfj):                                               # coverage: every custom part (incl. the arm-fixed H / F ones) has a STEP here
    fs = [f for f in os.listdir(sd) if f.lower().endswith(".step")]
    pf = json.load(open(pfj))["parts"]
    custom = [p for p in pf if p.get("material") != "user part" and not user_or_catalogue(p.get("group", ""), p["name"])
              and not (not p["name"].startswith("D8-") and "clip" in p["name"].lower())]          # catalogue E-clips: no STEP
    miss = [p["name"][:80] for p in custom if not any(f.startswith(f"{int(p['k']):02d}_") for f in fs)]
    cov = dict(custom_parts=len(custom), arm_fixed_custom=sum(1 for p in custom if p.get("group") in ("H", "F")), missing_step=miss)
    print(f"coverage: {len(custom)} custom parts ({cov['arm_fixed_custom']} arm-fixed), missing STEP: {miss or 'none'}")
os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(dict(parts=rows, coverage=cov, all_ok=all(r["valid"] and r["solids"] == 1 and r["bad_faces"] == 0 for r in rows)
                                                                 and not (cov and cov["missing_step"])),
                                                                 open(os.path.join(dd, "judge", "part_validity.json"), "w"), indent=1)
