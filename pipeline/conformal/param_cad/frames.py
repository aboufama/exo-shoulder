"""Kinematic frames of a searched spherical 3R for the parametric CAD (param_build.py).

Every part is designed once in WORLD coordinates (thorax mm, GH = origin, x anterior, y up, z right) at one reference
frame f0 of the design's clips, around the exact joint axes, then moved into its group's local frame:
    base, l1, l2 : world = G_f x            (clips.json frames[f]["G"][group], rotation about GH)
    H, F         : world = R_f x + t_f      (body_pose.segs of the frame's pose: humerus / forearm)
so scene_export.py / the judges pose it for every frame exactly as the old pipeline's parts.
Joint axes (clips.json "axes"): J1 = base x = l1 x, J2 = l2 x, J3 = the 4th entry in l2 (each link's x is its proximal axis).
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); import body_pose as BP          # noqa: E402

FULL = os.path.join(REPO, "pipeline", "full-exo")


def load(design="band_r20_n3_s1414_4"):
    C = json.load(open(os.path.join(FULL, "designs", design, "clips.json")))
    ax = {"J1": ("base", np.array(C["axes"][0][1], float)), "J2": ("l2", np.array(C["axes"][2][1], float)),
          "J3": ("l2", np.array(C["axes"][3][1], float))}                     # each link's local x = its proximal axis
    return C, ax


def body_frames(p):
    """(R, t) of the humerus and forearm segments for pose p = [plane, elev, axial, flex, pron] (scene_export's X['H'], X['F'])"""
    L = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))
    sg, _ = BP.segs(L["landmarks"], L["scale"], dict(zip(["plane", "elev", "axial", "flex", "pron"], p)))
    return (np.array(sg[2][0]), np.array(sg[2][1])), (np.array(sg[3][0]), np.array(sg[3][1]))


def frame_of(fr):
    """world transforms {group: (R, t)} for one clips.json frame"""
    X = {g: (np.array(G).reshape(3, 3), np.zeros(3)) for g, G in fr["G"].items()}
    X["H"], X["F"] = body_frames(fr["p"])
    return X


def followed(C, every=1, skip_held_out=True):
    held = set(json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"]) if skip_held_out else set()
    for ci, cl in enumerate(C["clips"]):
        if cl["name"] in held: continue
        for k, f in enumerate(cl["frames"]):
            if k % every == 0 and not f["held"]: yield ci, k, f


def axis_in(C, ax, joint, group):
    """direction of joint's axis in `group`'s local frame, with its spread over followed frames (deg; ~0 if fixed there)"""
    g0, a0 = ax[joint]; v = []
    for _, _, f in followed(C, every=5):
        X = frame_of(f); w = X[g0][0] @ a0; v.append(X[group][0].T @ w)
    v = np.array(v); m = v.mean(0); m /= np.linalg.norm(m)
    return m, float(np.degrees(np.arccos(np.clip(v @ m, -1, 1))).max())


if __name__ == "__main__":
    C, ax = load()
    for j, (g, a) in ax.items():
        print(j, "in", g, np.round(a, 4))
    for j, g in (("J1", "l1"), ("J2", "l1"), ("J3", "H")):
        m, s = axis_in(C, ax, j, g); print(f"{j} in {g}: {np.round(m, 4)}  spread {s:.3f} deg")
