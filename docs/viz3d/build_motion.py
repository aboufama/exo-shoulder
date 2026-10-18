"""Motion data for the 3D mechanism viewer (docs/viz3d/index.html): per clip frame, the rigid transform of every
moving body of a built design (pipeline/full-exo/scene_export.py frame_xforms: chain groups by their stored G / T,
the arm side and forearm by the body rig's segments), the joint axes in their carrier body's frame, the joint-angle
readouts and the part names. Also writes the design's exo.glb next to it as base64 text (exo.txt).

    python3 docs/viz3d/build_motion.py user_conecut_knee      (and user_pinknee_h1b), then build_skin.py for both
"""
import base64, json, math, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo")); sys.path.insert(0, os.path.join(REPO, "tools"))
import scene_export as SE
import eng_drawings as ED, eng_interfaces as EI

DD = sys.argv[1] if len(sys.argv) > 1 else "user_conecut_knee"
D = os.path.join(REPO, "pipeline", "full-exo", "designs", DD)
OUT = os.path.join(REPO, "docs", "viz3d", DD); os.makedirs(OUT, exist_ok=True)
C = json.load(open(os.path.join(D, "clips.json")))
L = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))["landmarks"]
BODY = {"base": "Base on the scapula handler", "l1": "Link 1", "l1a": "Link 1a", "l1b": "Link 1b", "dk": "Cam drive: bell crank", "l2": "Link 2",
        "l3": "Member 3 (J3 disc + strap)", "l4": "Knee link", "H": "Arm pad + BOTTOM + upper-arm cuff", "F": "Forearm cuff", "T": "Trunk"}
CARRIER = {"user_conecut_knee": {"J1": "base", "K": "l1a", "J2": "l1b", "J3": "l2", "crank pivot": "l1b", "pin a": "l3", "pin b": "l4"},
           "user_pinknee_h1b": {"J1": "base", "J2": "l1", "J3": "l2", "pin a": "l3", "pin b": "l4"}}
r4 = lambda a, n=4: [round(float(x), n) for x in np.ravel(a)]

clips = []
for cl in C["clips"]:
    frames = []
    for fr in cl["frames"]:
        X, pose = SE.frame_xforms(fr)
        g = {k: r4(np.r_[np.asarray(R).ravel(), np.asarray(t)], 4) for k, (R, t) in X.items()}
        lift_y = 0.2 * max(0, pose["elev"] - 30) * 1.0556638846119553          # trunk drop (pipeline/avg/body_pose.py segs)
        kn = fr.get("knuckle") or {}
        frames.append({"g": g, "lift": round(lift_y, 2), "p": r4(fr["p"], 1), "q": r4(fr["q"], 2), "knee": round(float(fr["knee"]["angle"]), 2),
                       "pa": round(float(fr["knee"]["pin_a"]), 1), "pb": round(float(fr["knee"]["pin_b"]), 1),
                       "dK": round(float(kn.get("dK", kn.get("dk", 0.0))), 2) if isinstance(kn, dict) else 0.0, "held": bool(fr.get("held"))})
    clips.append({"name": cl["name"], "fps": cl.get("fps", 30), "frames": frames})

# joint axes in their carrier body's build-pose frame (from the rest-pose joint table, mapped back through the rest transforms)
key = {"user_conecut_knee": "A", "user_pinknee_h1b": "B"}[DD]
info, parts, hub, bom = {"A": ED.set_A, "B": ED.set_B}[key]()
pose_fn = EI.rest_posing(DD)
J, pe = EI.joint_table([p for p in parts if p["pn"][:2] in ("D8", "D9")], EI.JOINTS[key], pose_fn)
X0, _ = SE.frame_xforms(C["clips"][0]["frames"][0])
carrier = CARRIER[DD]
axes = []
for j in J:
    g = carrier.get(j["name"])
    if g not in X0:
        continue
    R, t = (np.asarray(a, float) for a in X0[g])
    O, Dd = R.T @ (j["O"] - t), R.T @ j["D"]
    lo = -min(j["f"], 75.0) if j["name"] in ("J1", "K", "J2") else -8.0          # hub axes drawn down to GH, pins short
    axes.append({"name": j["name"], "g": g, "o": r4(O, 3), "d": r4(Dd, 5), "lo": round(lo, 2), "hi": round(j["h"] + 10, 2)})

# part names: GLB index -> card title (docs/blueprints/parts) or the CAD description
titles = {}
pj = os.path.join(REPO, "docs", "blueprints", "parts", DD, "parts.json")
if os.path.exists(pj):
    import importlib.util
    spec = importlib.util.spec_from_file_location("bb", os.path.join(REPO, "docs", "blueprints", "build_blueprints.py")); bb = importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
    T = bb.TITLES.get(DD)
    for p, t in zip(json.load(open(pj))["parts"], T or []):
        for k in p["ks"]:
            titles[str(k)] = [t, p["material"] or "your part"]
json.dump({"design": DD, "info": info["design"], "bodies": {k: v for k, v in BODY.items() if k in X0 or k == "T"}, "clips": clips, "axes": axes, "titles": titles,
           "landmarks": {k: L[k] for k in ("elbow", "ulnar_head", "radial_head")}},
          open(os.path.join(OUT, "motion.json"), "w"), separators=(",", ":"))
open(os.path.join(OUT, "exo.txt"), "w").write(base64.b64encode(open(os.path.join(D, "exo.glb"), "rb").read()).decode())   # the GLB, base64 (artifacts serve no binary types)
print("wrote", OUT, sum(len(c["frames"]) for c in clips), "frames,", len(axes), "axes,", len(titles), "titles,",
      os.path.getsize(os.path.join(OUT, "motion.json")) // 1024, "KB")
