"""knife-edge check (red team): the claim config's tolerance neighbours, one at a time (+-1 deg on angles, +-0.25 mm on
lengths) and 16 random combined corners, re-synthesised by the model (the drive's own range, PA gate, metal and fit
re-run): does every neighbour still synthesise (stroke >= the claim's taken K, honest), and what does the fast gap do?
    python3 docs/research/longstroke_drive/make_tol.py '<claim params json>' out_configs.json"""
import json, sys
import numpy as np

P = json.loads(sys.argv[1]); out = sys.argv[2]
ANG = [k for k in ("beta", "gam") if k in P]; LEN = [k for k in ("La", "r_h", "s_arm", "hl", "zr", "r_lobe") if k in P]
cf = [dict(P, _tag="claim")]
for k in ANG:
    for d in (-1.0, 1.0): cf.append(dict(P, **{k: round(P[k] + d, 4)}, _tag=f"{k}{d:+.2f}"))
for k in LEN:
    for d in (-0.25, 0.25): cf.append(dict(P, **{k: round(P[k] + d, 4)}, _tag=f"{k}{d:+.2f}"))
rng = np.random.default_rng(5)
for j in range(16):
    c = dict(P, _tag=f"corner{j}")
    for k in ANG: c[k] = round(P[k] + rng.choice([-1.0, 1.0]), 4)
    for k in LEN: c[k] = round(P[k] + rng.choice([-0.25, 0.25]), 4)
    cf.append(c)
json.dump(cf, open(out, "w")); print(len(cf), "configs")
