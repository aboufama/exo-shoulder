"""Evolution snapshot of a judged design (docs/EVOLUTION.md): the posed exo on the posed skin at the three standard poses
(rest, Raise overhead peak, Reach back pocket peak), one fixed camera, + the scorecard numbers, into
pipeline/evolution/<design id>/ (snapshot.png, scorecard.json). Cheap matplotlib preview, not a render.

    OMP_NUM_THREADS=1 python3 tools/evolution_snapshot.py <design id>
"""
import json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import body_pose as BP, scene_export as SE

ID = sys.argv[1]; DD = os.path.join(REPO, "pipeline", "full-exo", "designs", ID); OUT = os.path.join(REPO, "pipeline", "evolution", ID)
CAM = dict(elev=12, azim=-35)                 # fixed for every snapshot: from the right, slightly behind and above
BOX = 170.0


def pick_frames(C):
    """(label, clip index, frame index): rest (first frame of the first clip), the highest elevation of Raise overhead,
    the most extended frame of Reach back pocket (largest |plane| at elevation > 20, else its last frame)"""
    names = [c["name"] for c in C["clips"]]; out = [("rest", 0, 0)]
    if "Raise overhead" in names:
        ci = names.index("Raise overhead"); el = [f["want"][1] for f in C["clips"][ci]["frames"]]; out.append(("Raise overhead peak", ci, int(np.argmax(el))))
    if "Reach back pocket" in names:
        ci = names.index("Reach back pocket"); fr = C["clips"][ci]["frames"]
        sc = [abs(f["want"][2]) + abs(f["want"][0]) for f in fr]; out.append(("Reach back pocket peak", ci, int(np.argmax(sc))))
    return out


def main():
    C = json.load(open(os.path.join(DD, "clips.json"))); os.makedirs(OUT, exist_ok=True)
    fig = plt.figure(figsize=(15, 5.4), dpi=110)
    for k, (lab, ci, fi) in enumerate(pick_frames(C)):
        fr = C["clips"][ci]["frames"][fi]; sc = SE.posed_scene(DD, ci, fi)
        ax = fig.add_subplot(1, 3, k + 1, projection="3d"); ax.view_init(**CAM)
        V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))); F = BP.F
        keep = np.linalg.norm(V[F].mean(1), axis=1) < BOX * 1.2
        ax.add_collection3d(Poly3DCollection(V[F[keep]][:, :, [2, 0, 1]], facecolor=(0.12, 0.12, 0.13, 0.35), edgecolor="none"))
        for node in sc.graph.nodes_geometry:
            g = node.split("|")[0]; T_, gn = sc.graph[node]; m = sc.geometry[gn]
            if g == "F": continue
            P = (np.c_[m.vertices, np.ones(len(m.vertices))] @ T_.T)[:, :3]
            if np.linalg.norm(P, axis=1).min() > BOX * 1.2: continue
            col = (0.95, 0.55, 0.1, 0.9) if g in ("l3", "l4") or "rail" in node else ((0.55, 0.57, 0.6, 0.6) if g == "H" else (0.78, 0.80, 0.83, 0.95))
            ax.add_collection3d(Poly3DCollection(P[m.faces][:, :, [2, 0, 1]], facecolor=col, edgecolor="none"))
        ax.set_xlim(-BOX, BOX); ax.set_ylim(-BOX, BOX); ax.set_zlim(-BOX, BOX); ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()
        ax.set_title(f"{lab}{' (held)' if fr.get('held') else ''}\np = {np.round(fr['p'][:3], 0).tolist()}", fontsize=9)
    fig.suptitle(ID, fontsize=11); fig.tight_layout(); fig.savefig(os.path.join(OUT, "snapshot.png")); print("wrote", os.path.join(OUT, "snapshot.png"))
    sc_ = os.path.join(DD, "judge", "scorecard.json")
    if os.path.exists(sc_): json.dump(json.load(open(sc_)), open(os.path.join(OUT, "scorecard.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
