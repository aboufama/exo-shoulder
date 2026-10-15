"""CAD build -> viewer design dir: exo.glb from out_<key>/, clips copied from the band design with the base held
scapula-fixed (one fixed frame per design: its tab points away from link 1's mean direction), index.json entry.

    python3 make_cad_design.py <key> <source band design dir name> "<label>" [--allow-short-link]

Refuses (exit 2) a design with a link arc < MIN_ARC deg (35) or less than MIN_ARM_MM (10) clear between a link's hub
seats (docs/FINDINGS.md "Short link"; thresholds from band_impl, env MIN_ARC / MIN_ARM_MM override) unless
--allow-short-link or ALLOW_SHORT_LINK=1 is given.
"""
import json, math, os, shutil, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); FX = os.path.join(EXO, "full-exo")
sys.path.insert(0, os.path.join(EXO, "avg"))
ALLOW = "--allow-short-link" in sys.argv[1:] or os.environ.get("ALLOW_SHORT_LINK") == "1"
KEY, SRC, LABEL = [x for x in sys.argv[1:] if x != "--allow-short-link"][:3]; NAME = f"cad_{KEY}"; sys.argv = sys.argv[:1]
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as DS; os.chdir(_c)
C = json.load(open(os.path.join(FX, "designs", SRC, "clips.json")))
# ---- every link a real arm (docs/FINDINGS.md "Short link"): no CAD from a design whose hubs sit side by side
sys.path.insert(0, os.path.join(EXO, "conformal", "gpu")); import band_impl as BI
DSN = C.get("design") or {}
if "a" not in DSN: print(f"WARNING make_cad_design: designs/{SRC}/clips.json has no design kinematics - link arcs NOT checked", file=sys.stderr, flush=True)
else:
    _probs = BI.design_link_report(DSN, DSN.get("arm_mm"), float(os.environ.get("MIN_ARC", BI.MIN_ARC)), float(os.environ.get("MIN_ARM_MM", BI.MIN_ARM_MM)),
                                   hub_r=float(DSN.get("hub_r", 11.5)))                  # default: the fair CAD's O23 seat (fair_cad/members.py HUB_R)
    if DSN.get("arm_mm") is None:
        print(f"WARNING make_cad_design: designs/{SRC}/clips.json has no arm_mm (made before the guard?) - min_arm_mm NOT checked; re-run band_to_design.py",
              file=sys.stderr, flush=True)
    if _probs:
        _msg = "!" * 110 + f"\nmake_cad_design {SRC} -> {NAME}: a link without a real arm\n  " + "\n  ".join(_probs) + "\n"
        if not ALLOW: print(_msg + "  REFUSED: no CAD built. Override (only with the user's OK): --allow-short-link or ALLOW_SHORT_LINK=1\n" + "!" * 110, file=sys.stderr, flush=True); sys.exit(2)
        print(_msg + "  building anyway (--allow-short-link / ALLOW_SHORT_LINK=1)\n" + "!" * 110, file=sys.stderr, flush=True)
DD = os.path.join(FX, "designs", NAME); os.makedirs(DD, exist_ok=True)
_g = os.path.join(HERE, f"out_{KEY}", "exo.glb")
if os.path.exists(_g): shutil.copy(_g, os.path.join(DD, "exo.glb"))     # old pipeline build (the fair pipeline writes its own)
loc = []                                                                            # base frame in the scapula frame, per frame
for cl in C["clips"]:
    for f in cl["frames"]:
        Rs = DS.scapula(f["p"][1]); loc.append(Rs.T @ np.array(f["G"]["base"]).reshape(3, 3))
loc = np.array(loc); a = loc[0][:, 0]; print("J1 axis spread", float(np.abs(loc[:, :, 0] - a).max()))
MOUNT = {"5r_thin": [0.0, 1.0, -1.0], "4r_thin": [-1.0, 0.0, -1.0]}.get(KEY, [0.0, 0.6, -0.8])   # base tab toward the back plate (thorax: anterior, up, right)
nb0 = loc[:, :, 1].mean(0); nb0 = nb0 - (nb0 @ a) * a; nb0 /= np.linalg.norm(nb0)
d = np.array(MOUNT, float); d -= (d @ a) * a; d /= np.linalg.norm(d); nb = -d; Fb = np.c_[a, nb, np.cross(a, nb)]   # tab = local -y = d
e2 = np.cross(a, nb0); t = math.degrees(math.atan2(d @ e2, d @ nb0)); a1 = np.degrees(np.arctan2(loc[:, :, 1] @ e2, loc[:, :, 1] @ nb0))
print(f"base tab toward {MOUNT}: link 1 within +-16 deg of it in {100 * np.mean(np.abs((a1 - t + 180) % 360 - 180) < 16):.1f}% of frames")
ang = np.degrees(np.arctan2(loc[:, :, 1] @ np.cross(a, nb), loc[:, :, 1] @ nb)); print(f"link 1 swing about J1 vs the fixed base frame: {ang.min():.0f} .. {ang.max():.0f} deg")
for cl in C["clips"]:
    for f in cl["frames"]:
        Rs = DS.scapula(f["p"][1]); f["G"]["base"] = (Rs @ Fb).round(6).ravel().tolist(); f["clr"] = 0.0; f["med"] = None
C["subtitle"] = LABEL
json.dump(C, open(os.path.join(DD, "clips.json"), "w"), separators=(",", ":"))
_ws = os.path.join(FX, "designs", SRC, "workspace.json")                             # R16 poses (judge/workspace.py) with the same fixed base
if os.path.exists(_ws):
    W = json.load(open(_ws))
    for w in W["poses"]:
        if "G" in w: w["G"]["base"] = (DS.scapula(w["p"][1]) @ Fb).round(6).ravel().tolist()
    json.dump(W, open(os.path.join(DD, "workspace.json"), "w"), separators=(",", ":")); print(f"workspace.json: {len(W['poses'])} poses, base re-framed")
_inp = os.path.join(HERE, "inputs", f"{KEY}.json")                                    # design.json (R5 count, base mount, R17 kinematics)
if os.path.exists(_inp):
    Ri = json.load(open(_inp))["results"][0]; cuff = Ri.get("cuff")
    json.dump(dict(id=NAME, source=f"pipeline/conformal/band_cad/inputs/{KEY}.json" + (f" (= {Ri['_eval_src']})" if "_eval_src" in Ri else ""),
                   n_joints=Ri["n"], sliding_cuff=bool(cuff), dof=Ri["n"] + (1 if cuff else 0),
                   kinematics={k: Ri[k] for k in ("az", "el", "a", "w", "branch", "order") if k in Ri}, **({"cuff": cuff} if cuff else {}),
                   base=dict(mount="girdle", chain="spherical", note="base rides the scapula on the user's scapula handler"),
                   built_with=f"pipeline/conformal/fair_cad/fair_pipeline.sh (POSES_FILE={Ri.get('poses_file', 'band_poses.b64')}; t_link {Ri.get('t_link')}, "
                              f"ramp {Ri.get('ramp_deg', 35)} deg; v4 joint stacks)", label=LABEL),
              open(os.path.join(DD, "design.json"), "w"), indent=1)
idx = json.load(open(os.path.join(FX, "designs", "index.json"))); idx = [e for e in idx if e["id"] != NAME]
idx.insert(0, dict(id=NAME, label=LABEL)); json.dump(idx, open(os.path.join(FX, "designs", "index.json"), "w"), indent=1)
print("wrote", DD)
