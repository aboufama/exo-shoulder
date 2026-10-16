"""In-place fix-up of a user_style_pinknee.py export made before two export fixes (2026-10-16): (1) the knee link (its
name mentions its clip counterbores) was classed as hardware - no STEP, stainless density, and check_frames left its mesh
out; the iglidur sleeves were classed as bearing steel; (2) link 2's mesh was not closed in the judges' units (weld
tolerance 0.05 mm too small for its glued bent-bar seams). Rebuilds the two solids with the same builder functions on the
same frozen shape (the link fits come from the cache), replaces link 2's mesh in exo.glb (same node), exports the knee
link's STEP, corrects parts_full.json / build.json and re-runs the kinematic check. The geometry of every other part is
untouched (same file).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/fixup_pinknee_export.py <design id> <shape.pkl>
"""
import json, os, sys
ID, SHAPE = sys.argv[1], sys.argv[2]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import user_style_pinknee as UP                                                           # noqa: E402
import numpy as np, trimesh, cadquery as cq                                               # noqa: E402
dd = os.path.join(UP.FULL, "designs", ID)
M, shape = UP.PS.wear(SHAPE)
lk, _ = UP.links(M)
link2 = next(s for g, mem, n, s in lk if n.startswith("D8-03"))
knee = UP.knee_link(M)[3]
pf = json.load(open(os.path.join(dd, "parts_full.json")))
src = trimesh.load(os.path.join(dd, "exo.glb"))
fixed = {}
for p in pf["parts"]:
    n = p["name"]
    if n.startswith("D8-03"):
        rep = {}; m = UP.tess(link2, report=rep)
        node = f"{p['group']}|{n}|{p['k']}"; assert node in src.geometry, (node, list(src.geometry)[:5]); src.geometry[node] = m
        p["watertight_judge_units"] = rep.get("watertight_judge_units"); fixed["link 2 watertight_judge_units"] = p["watertight_judge_units"]
    if n.startswith("D8-05"):
        f = os.path.join(dd, "step", f"{p['k']:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step")
        cq.exporters.export(cq.Workplane().add(knee), f)
        vol = float(knee.Volume()); p.update(material="Ti-6Al-4V", mass_g=round(vol / 1000 * UP.TI, 2), vol_cm3=round(vol / 1000, 3), valid=bool(knee.isValid()),
                                             solids=len(knee.Solids()), faces=len(knee.Faces()))
        fixed["knee link"] = dict(step=os.path.basename(f), mass_g=p["mass_g"])
    if "iglidur" in n and p["material"] != "iglidur":
        p.update(material="iglidur", mass_g=round(p["vol_cm3"] * UP.IGL, 3)); fixed.setdefault("iglidur relabelled", []).append(n[:40])
tmp = os.path.join(dd, "exo.tmp.glb"); src.export(tmp); os.replace(tmp, os.path.join(dd, "exo.glb"))
json.dump(pf, open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
b = json.load(open(os.path.join(dd, "build.json")))
ours = [p for p in pf["parts"] if p["material"] != "user part"]
b["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                   bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
b["parts"] = pf["parts"]
# the kinematic check again (the knee link's mesh is now in its group)
names = {"base": 0, "l1": 1, "l2": 2, "l3": 3, "l4": 6, "H": 5}
parts = [(p["group"], names[p["group"]], p["name"], None) for p in pf["parts"] if p["group"] in names and p["material"] != "user part"
         and not p["name"].startswith(("UPPER ARM CUFF", "M4x6"))]                     # as the build: our parts, not the user's / the cuff
b["check"] = UP.check_frames(M, dd, parts)
b["kinematics_exact"] = dict(poses=len(b["check"]), all_within_0p5=all(r["within_0p5"] for r in b["check"]),
                             max_frame_dev_mm=max(r["frame_dev_mm"] for r in b["check"]),
                             max_joint_feature_mm=max(r["joint_features_max_mm"] for r in b["check"]),
                             max_rigid_incl_knee_link_mm=max(r["rigid_incl_knee_link_max_mm"] for r in b["check"]))
b["fixup"] = fixed
json.dump(b, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
print("fixup", fixed, "mass", b["mass_g"], "kinematics", b["kinematics_exact"], flush=True)
