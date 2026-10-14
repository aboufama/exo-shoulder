"""last resort after the replan loop: frames whose (10 fps) pose still collides are marked held and keep the previous
good frame's exo configuration (the exo stops, the arm moves on: honest 'not following')"""
import sys, json, os, numpy as np
KEY = sys.argv[1]; HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "..", "..", "full-exo"); CP = os.path.join(FX, "designs", f"cad_{KEY}", "clips.json")
bad = set(np.load(os.path.join(HERE, f"out_{KEY}", "verify_bad_frames.npy")).tolist()) if os.path.exists(os.path.join(HERE, f"out_{KEY}", "verify_bad_frames.npy")) else set()
import io, gzip, base64
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(HERE, "..", "band_poses.b64")).read())))); P = Z["POSE"]
C = json.load(open(CP)); n_hold = 0
for cl in C["clips"]:
    last = None
    for k, f in enumerate(cl["frames"]):
        p = int(np.argmin(np.abs(P - np.array(f["p"])).sum(1)))
        if p in bad and not f["held"]:
            if last is not None: f["G"] = dict(last)
            f["held"] = True; n_hold += 1
        elif not f["held"]: last = dict(f["G"])
json.dump(C, open(CP, "w"), separators=(",", ":")); print(f"held {n_hold} frames with residual collisions ({len(bad)} poses)")
