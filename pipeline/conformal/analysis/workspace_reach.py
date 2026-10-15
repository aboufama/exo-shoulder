"""How much of the plausible everyday workspace can a pure 3R chain reach at all (kinematics only, no skin)? A pose is
reachable iff theta = angle(b, HG w) lies in [|a1 - a2| + s, a1 + a2 - s] (s = band_impl's 10 deg J2 margin; the
J1-J3 alignment singularity is theta near 0 / 180 and is inside that rule when a1 = a2). For the r16 winners as found,
for the same axes with longer arcs, and for the best (b, w) found by random search per arc pair.
    python3 workspace_reach.py   -> workspace_reach.json"""
import json, math, os, sys
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI
P = BI.load_poses(open(os.path.join(HERE, "..", "band_poses_ws.b64")).read(), torch.device("cpu")); HG = P["HG"].numpy(); env = P["CID"].numpy() == len(P["NAMES"]) - 1
HW = HG[env]; HC = HG[~env]; S = 10.0
def cover(b, w, a1, a2, H):
    th = np.degrees(np.arccos(np.clip((H @ w) @ b, -1, 1))); lo, hi = abs(a1 - a2) + S, a1 + a2 - S
    return float(((th >= lo) & (th <= hi)).mean())
D = json.load(open(os.path.join(HERE, "..", "gpu_client", "band_search_r16.json"))); out = []
for r in D:
    b0 = r["best"][0]; b = np.array(BI.bvec(b0["az"], b0["el"])); w = np.array(BI.w_dir(*b0["w"])); a1, a2 = b0["a"]
    row = dict(seed=r["cfg"]["seed"], a=[round(a1, 1), round(a2, 1)], workspace_kin=round(cover(b, w, a1, a2, HW), 3), clips_kin=round(cover(b, w, a1, a2, HC), 3),
               evaluator_envelope_follow=round(b0["envelope"]["follow"], 3))
    for A in (80, 90):
        row[f"arcs_{A}_{A}_same_axes"] = round(cover(b, w, A, A, HW), 3)
    out.append(row); print(row, flush=True)
rng = np.random.default_rng(0); B = rng.normal(size=(3000, 3)); B /= np.linalg.norm(B, axis=1, keepdims=True); Wd = rng.normal(size=(400, 3)); Wd /= np.linalg.norm(Wd, axis=1, keepdims=True)
best = {}
for a1, a2 in ((60, 60), (65, 65), (70, 70), (75, 75), (80, 80), (90, 90)):
    lo, hi = abs(a1 - a2) + S, a1 + a2 - S; bb = (0, None)
    for w in Wd:
        D_ = HW[::3] @ w; th = np.degrees(np.arccos(np.clip(D_ @ B.T, -1, 1))); c = ((th >= lo) & (th <= hi)).mean(0); j = int(c.argmax())
        if c[j] > bb[0]: bb = (float(c[j]), (B[j], w))
    best[f"{a1}/{a2}"] = round(cover(bb[1][0], bb[1][1], a1, a2, HW), 3); print("best possible workspace reach, arcs", a1, a2, best[f"{a1}/{a2}"], flush=True)
json.dump(dict(r16=out, best_possible=best), open(os.path.join(HERE, "workspace_reach.json"), "w"), indent=1)
