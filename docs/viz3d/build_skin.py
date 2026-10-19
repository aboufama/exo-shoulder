"""Mannequin for the 3D mechanism viewer (docs/viz3d/index.html): the body rig's posed render skin
(pipeline/avg/body_pose.py, the skin the judges measure against), cropped to a faceless bust (cut at the neck and
below the ribs; the right arm whole), decimated, and keyframed for every clip of a design.

Out, in docs/viz3d/skin/:
  mesh.txt      rest bust: float32 xyz per vertex, then uint32 faces (counts in mesh.json); base64, like every .txt here
  mesh.json     {nv, nf, moving: [vertex ids that leave the rigid trunk], step}
  <hash>.txt    one clip: int16 xyz (0.05 mm) of the moving vertices per keyframe (every `step` clip frames);
                the other vertices ride the trunk (rest - lift). Named by a hash of the clip's poses, so designs
                that share a clip share its file.
And docs/viz3d/<design>/motion.json gains clips[i].skin = "<hash>.bin".

    python3 docs/viz3d/build_skin.py user_conecut_knee user_pinknee_h1b
"""
import base64, hashlib, json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import body_pose as BP
import igl

OUT = os.path.join(REPO, "docs", "viz3d", "skin"); os.makedirs(OUT, exist_ok=True)
STEP, Q = 3, 0.05                                   # keyframe every 3rd frame (10 fps), int16 at 0.05 mm
NECK_Y, WAIST_Y, FACES = 118.0, -560.0, 36000      # crop (thorax frame, GH origin) and decimation target
b64 = lambda path, raw: open(path, "w").write(base64.b64encode(raw).decode())     # artifacts serve no binary types
pose_of = lambda p: dict(plane=p[0], elev=p[1], axial=p[2], flex=p[3], pron=p[4])


def bust():
    V, F = BP.V0, BP.F
    arm = np.zeros(len(V), bool); arm[np.flatnonzero(BP.ARMV) if BP.ARMV.dtype == bool else BP.ARMV] = True
    keepv = arm | ((V[:, 1] < NECK_Y) & (V[:, 1] > WAIST_Y))
    F = F[keepv[F].all(1)]
    U, G, J, I = igl.qslim(np.asfortranarray(V, float), np.asfortranarray(F, np.int32), FACES)   # I: birth vertex of each U
    used = np.unique(G); remap = -np.ones(len(U), int); remap[used] = np.arange(len(used))
    return remap[G].astype(np.uint32), I[used]


def main(designs):
    G, src = bust()
    rest = BP.V0[src]
    # vertices that leave the rigid trunk (rest - lift) in any pose of any clip
    clips = {dd: json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", dd, "clips.json")))["clips"] for dd in designs}
    S = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))["scale"]
    lift = lambda p: np.array([0, 0.2 * max(0, p[1] - 30) * S, 0])
    probe = [f["p"] for cl in next(iter(clips.values())) for f in cl["frames"][::12]]
    dev = np.zeros(len(src))
    for p in probe:
        dev = np.maximum(dev, np.linalg.norm(BP.posed(pose_of(p))[src] - (rest - lift(p)), axis=1))
    moving = np.flatnonzero(dev > 0.25)
    b64(os.path.join(OUT, "mesh.txt"), rest.astype(np.float32).tobytes() + G.tobytes())
    json.dump({"nv": len(src), "nf": len(G), "moving": moving.tolist(), "step": STEP, "q": Q},
              open(os.path.join(OUT, "mesh.json"), "w"), separators=(",", ":"))
    print(f"bust {len(src)} v / {len(G)} f, moving {len(moving)}, max probe dev {dev.max():.0f} mm")
    total, used = 0, set()
    for dd in designs:
        mp = os.path.join(REPO, "docs", "viz3d", dd, "motion.json"); M = json.load(open(mp))
        for cl, mc in zip(clips[dd], M["clips"]):
            P = [f["p"] for f in cl["frames"]]
            name = hashlib.sha1(json.dumps([[round(x, 3) for x in p] for p in P]).encode()).hexdigest()[:12] + ".txt"
            fp = os.path.join(OUT, name)
            if not os.path.exists(fp):
                keys = list(range(0, len(P), STEP)) + ([len(P) - 1] if (len(P) - 1) % STEP else [])
                X = np.stack([BP.posed(pose_of(P[k]))[src][moving] for k in keys])
                assert np.abs(X).max() < 32767 * Q, "skin outside the int16 range"
                b64(fp, np.round(X / Q).astype(np.int16).tobytes())
            used.add(name); mc["skin"] = name; mc["skinN"] = len(range(0, len(P), STEP)) + (1 if (len(P) - 1) % STEP else 0); total += os.path.getsize(fp)
        json.dump(M, open(mp, "w"), separators=(",", ":"))
        print(dd, "skin files", [c["skin"] for c in M["clips"]])
    for f in os.listdir(OUT):                                                   # drop clips no design uses any more
        if f.endswith(".txt") and f != "mesh.txt" and f not in used: os.remove(os.path.join(OUT, f))
    print("skin keyframes", total // 1024, "KB (all files incl. shared)")


if __name__ == "__main__":
    main(sys.argv[1:] or ["user_conecut_knee"])
