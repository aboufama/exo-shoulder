"""JUDGE R10: the base bolts to a thorax back plate. How far is the arm's GH centre from where the chain carries it, and
does the base part stay out of the body, when the base is THORAX-fixed (whatever frame the design pipeline assumed)?

Girdle motion: the body rig's law (avg/body_pose.py segs(): GH lift; scap(): the skin over the scapula moves) - a model,
to be replaced by OpenSim Seth 2016 / OpenCap trajectories (data/raw) when they exist. Frames: every step-th frame of
every clip, the person's motion ("want" poses: the girdle moves whether or not the exo follows).
Chain model from design.json "base" (default for designs without one: a spherical chain centred on the GH centre at
rest, i.e. every axis through the GH centre):
    {"mount": "thorax", "chain": "spherical", "centre_mm": [x, y, z]}
    {"mount": "thorax", "chain": "offset3", "prm": {b, a1, a2, branch, w}, "axis_points_mm": [o1, o2, o3]}  (girdle.Chain3)
    python3 judge/base_mount.py <design dir|id> [--step 3]  -> <design>/judge/base_mount.json"""
import argparse, json, os, sys
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts, frames, PIPE
from sdist import signed_distance
sys.path.insert(0, os.path.join(PIPE, "girdle")); import girdle as GD
from girdle import BP
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=3)
a = ap.parse_args(); dd = design_dir(a.design)
D = json.load(open(os.path.join(dd, "design.json"))); base = D.get("base", {"mount": "thorax", "chain": "spherical", "centre_mm": [0, 0, 0]})
FR = list(frames(dd, a.step)); W = np.array([fr["want"] for _, _, fr in FR], float); M = GD.Motion(W)
if base.get("chain") == "offset3":
    pr = dict(base["prm"]); pr["b"] = tuple(pr["b"]); pr["w"] = None if pr.get("w") is None else tuple(pr["w"])
    ch = GD.Chain3(pr); A, mg, ok, *_ = ch.kin(M); x = np.concatenate([np.asarray(o, float) for o in base["axis_points_mm"]])
    mis = GD.residual(A, x, M.lift); extra = dict(singular_margin_deg_min=round(float(mg.min()), 1), closes=round(float(ok.mean()), 3))
else:
    mis = np.linalg.norm(M.lift - np.asarray(base.get("centre_mm", [0, 0, 0]), float), axis=1); extra = {}
# the base part on a thorax-fixed plate vs the exact posed skin (its pose at rest, carried by the trunk)
parts = [(n, P) for g, n, P, _ in load_parts(dd) if g == "base"]; depth = 0.0; worst = None
if parts:
    C0 = json.load(open(os.path.join(dd, "clips.json")))["clips"][0]["frames"][0]
    G0 = BP.scap(C0["p"][1]).T @ np.array(C0["G"]["base"]).reshape(3, 3)          # base group frame -> rest (thorax) frame
    B = np.concatenate([P[:: max(1, len(P) // 3000)] for _, P in parts]) @ G0.T
    for (clip, fi, fr), lf in zip(FR[::2], M.lift[::2]):
        V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["want"]))); sd = signed_distance(B - lf, V, BP.F, tree=cKDTree(V[BP.F].mean(1)))
        if -sd.min() > depth: depth = float(-sd.min()); worst = [clip, fi, [round(v) for v in fr["want"][:3]]]
names = [f[0] for f in FR]
out = dict(girdle_law="avg/body_pose.py (rig) - not yet OpenSim/OpenCap", base=base, frames_checked=len(FR), step=a.step,
           max_mm=round(float(mis.max()), 2), p95_mm=round(float(np.percentile(mis, 95)), 2), share_over_4mm=round(float((mis > 4).mean()), 3),
           per_clip={n: round(float(mis[[k for k, m in enumerate(names) if m == n]].max()), 2) for n in dict.fromkeys(names)},
           base_part_enters_body_mm=round(depth, 2), base_part_worst=worst, **extra)
os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "base_mount.json"), "w"), indent=1)
print(f"base mount (thorax-fixed, {base.get('chain', 'spherical')} chain): GH misalignment max {out['max_mm']} mm, p95 {out['p95_mm']} mm, "
      f"{100 * out['share_over_4mm']:.0f}% of frames > 4 mm; base part enters the body by {out['base_part_enters_body_mm']} mm (worst {worst})")
