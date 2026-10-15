"""band_eval DETAIL result -> band_cad/inputs/<key>.json, the input of fair_cad/fair_pipeline.sh.

    python3 make_input.py <band_eval json> <result index> <key> --ramp-deg 60 --poses band_poses_ws.b64 [--hw 7]

The evaluator stores t_link / hub_r / stack per result but not the job keys the CAD must match: ramp_deg (the steepest
ribbon ramp out of a hub plane), hw (link half-width, if the job set it) and the pose payload the eval ran on (replan.py
and band_to_design.py index the result's per-pose feasibility by it). They are written into the result here; fair_build
reads t_link / hw / ramp_deg, fair_pipeline.sh reads poses_file. The payload must start with band_poses.b64's clip
frames (envelope.py / hold_bad.py index the dense skin maps by band_poses.b64): band_poses_ws.b64 / band_poses_wsf.b64
do, the *_fit_* payloads (6 fit clips, no Wave / Walking) do not - re-run the detail eval on a full payload first.
"""
import argparse, base64, gzip, io, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, "..")
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("idx", type=int); ap.add_argument("key")
ap.add_argument("--ramp-deg", type=float, required=True, help="the job's ramp_deg (35 = evaluator default)")
ap.add_argument("--poses", required=True, help="payload file in pipeline/conformal the detail eval ran on")
ap.add_argument("--hw", type=float, default=None, help="the job's hw (link half-width), if it set one")
a = ap.parse_args()
D = json.load(open(a.src)); R = dict(D["results"][a.idx])
if R.get("err"): sys.exit(f"result {a.idx} was rejected by the evaluator: {R['err']}")
for k in ("feas_all", "share_all", "h", "dirs_local", "faces", "lower", "PC"):
    if k not in R: sys.exit(f"result {a.idx} has no '{k}': not a DETAIL eval (run band_eval with detail=1)")
load = lambda f: np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, f)).read()))))
Z, Z0 = load(a.poses), load("band_poses.b64"); n0 = len(Z0["POSE"])
if len(Z["POSE"]) != R["PC"][0]: sys.exit(f"{a.poses} has {len(Z['POSE'])} poses, the result was evaluated on {R['PC'][0]}: wrong payload")
if len(Z["POSE"]) < n0 or np.abs(Z["POSE"][:n0] - Z0["POSE"]).max() > 1e-6 or (Z["CID"][:n0] != Z0["CID"]).any():
    sys.exit(f"{a.poses} does not start with band_poses.b64's 8 clips: the CAD's skin envelope / hold_bad would index the wrong poses")
R.update(ramp_deg=a.ramp_deg, poses_file=a.poses, _eval_src=f"{os.path.relpath(a.src, CONF)} #{a.idx}")
if a.hw is not None: R["hw"] = a.hw
out = os.path.join(HERE, "inputs", f"{a.key}.json")
json.dump(dict(results=[R], secs=D.get("secs"), device=D.get("device"), version=D.get("version")), open(out, "w"))
print(f"wrote {out}: n {R['n']}, t_link {R.get('t_link')}, hub_r {R.get('hub_r')}, stack {R.get('stack')}, ramp {a.ramp_deg}, poses {a.poses}, "
      f"cuff {R.get('cuff')}, eval score {R.get('score', 0):.3f} follow {R.get('follow', 0):.3f}")
