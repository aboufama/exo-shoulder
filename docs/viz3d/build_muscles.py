"""Muscle layer for the 3D mechanism viewer (docs/viz3d/index.html): the body rig's own muscles and bones
(pipeline/avg/body_mesh.json, BodyParts3D, posed by pipeline/avg/body_pose.py exactly as its skin is), cropped like the
bust (nothing above the neck: faceless; trunk parts end below the ribs), decimated, keyframed per clip.

Out, in docs/viz3d/muscles/ (every .txt is base64: artifacts serve no binary types):
  static.json / static.txt  rigid parts merged per (segment, class): int16 xyz at 0.1 mm, then uint32 faces per group.
                            Segment 0 rides the trunk (rest - lift); 1-4 ride the rig's scapula / humerus / forearm / hand.
  dyn.json / dyn.txt        the 70 moving muscles merged: uint32 faces, then one uint8 per vertex = the segment
                            (0 trunk .. 4 hand) of its largest skinning weight (positions come from the clip files)
  <hash>.txt                one clip: int16 xyz (0.05 mm) of the moving muscles every `step` frames IN THEIR SEGMENT'S
                            FRAME (R^T (p - t)), then float32 per frame the rig's segment transforms 1-4 (R row-major,
                            t: 12 each). The page interpolates the local shape and applies each frame's exact transform,
                            so bone motion is exact at every frame and only the muscle deformation is interpolated.
And docs/viz3d/<design>/motion.json gains clips[i].musc = "<hash>.txt".

    python3 docs/viz3d/build_muscles.py user_conecut_knee user_pinknee_h1b
"""
import base64, hashlib, json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import body_pose as BP
import igl

OUT = os.path.join(REPO, "docs", "viz3d", "muscles"); os.makedirs(OUT, exist_ok=True)
STEP, Q = 15, 0.05                                  # moving muscles keyframed every 15th frame (2 fps) in their bone's frame, int16 at 0.05 mm
NECK_Y, WAIST_Y = 118.0, -560.0                     # the bust crop of build_skin.py (thorax frame, GH origin)
RATIO = {"muscle": 0.3, "bone": 0.45, "cartilage": 0.3}
DYN_H = float(os.environ.get("DYN_H", 6.0))          # grid cell (mm) for the moving muscles, whose keyframes dominate the size
b64 = lambda path, raw: open(path, "w").write(base64.b64encode(raw).decode())
dec = lambda s, t: np.frombuffer(base64.b64decode(s), dtype=t)
pose_of = lambda p: dict(plane=p[0], elev=p[1], axial=p[2], flex=p[3], pron=p[4])


def crop(V, F, trunk):
    """faceless: drop faces reaching above the neck; trunk parts also lose faces wholly below the waist"""
    y = V[F][:, :, 1]
    keep = ~(y > NECK_Y).any(1)
    if trunk: keep &= ~(y < WAIST_Y).all(1)
    return F[keep]


def decimate(V, F, ratio):
    """qslim to ratio of the faces; returns (faces into V's birth vertices, birth vertex ids) or the input on failure"""
    if len(F) < 60: return F, np.arange(len(V))
    try:
        U, G, J, I = igl.qslim(np.asfortranarray(V, float), np.asfortranarray(F, np.int32), max(24, int(len(F) * ratio)))
        if len(G) == 0: raise ValueError("empty")
        return np.asarray(I)[G], np.arange(len(V))
    except Exception:
        return F, np.arange(len(V))


def cluster(V, F, h):
    """vertex clustering on an h-mm grid (robust on non-manifold parts): each cell keeps the vertex nearest its mean;
    returns faces into V's kept (birth) vertices, degenerate faces dropped; the input if it would vanish"""
    cell = np.floor(V / h).astype(np.int64); _, inv = np.unique(cell, axis=0, return_inverse=True); inv = inv.ravel()
    k = inv.max() + 1; cnt = np.bincount(inv, minlength=k); mean = np.zeros((k, 3))
    for c in range(3): mean[:, c] = np.bincount(inv, V[:, c], minlength=k) / cnt
    d = np.linalg.norm(V - mean[inv], axis=1); rep = np.full(k, -1); best = np.full(k, np.inf)
    order = np.argsort(d)[::-1]; rep[inv[order]] = order                # the last write per cell is its nearest vertex
    G = rep[inv[F]]; G = G[(G[:, 0] != G[:, 1]) & (G[:, 1] != G[:, 2]) & (G[:, 0] != G[:, 2])]
    return (G, True) if len(G) >= 8 else (F, False)


def compact(V, F):
    used = np.unique(F); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    return V[used], remap[F], used


def main(designs):
    rig = BP._rig(); J = rig.J
    groups = {}                                                     # (seg, cls) -> [V list, F list]
    for p in J["parts"]:
        if "w4i" in p or p["cls"] not in RATIO: continue
        V = dec(p["pos"], np.int16).reshape(-1, 3).astype(float) / 10
        F = dec(p["idx"], np.uint32 if p.get("i32") else np.uint16).reshape(-1, 3).astype(int)
        seg = p.get("seg") or 0
        F = crop(V, F, seg == 0)
        if not len(F): continue
        V, F, _ = compact(V, F)
        F, _ = decimate(V, F, RATIO[p["cls"]])
        V, F, _ = compact(V, F)
        g = groups.setdefault((seg, p["cls"]), [[], [], 0])
        g[0].append(V); g[1].append(F + g[2]); g[2] += len(V)
    meta, blobs = [], []
    for (seg, cls), (Vs, Fs, n) in sorted(groups.items()):
        V = np.concatenate(Vs); F = np.concatenate(Fs)
        assert np.abs(V).max() < 3276, "static part outside the int16 range"
        blobs += [np.round(V * 10).astype(np.int16).tobytes(), F.astype(np.uint32).tobytes()]
        meta.append({"seg": int(seg), "cls": cls, "nv": len(V), "nf": len(F)})
    raw = b""
    for bl in blobs: raw += bl + b"\0" * (-len(bl) % 4)              # keep every block 4-byte aligned
    b64(os.path.join(OUT, "static.txt"), raw)
    json.dump({"groups": meta, "q": 0.1}, open(os.path.join(OUT, "static.json"), "w"))
    print("static", meta)

    # moving muscles: decimate on the rest pose, keep each decimated vertex's birth vertex
    dyn = [d for d in rig.dyn if d is not rig.skin and d["cls"] == "muscle"]
    sel, Fs, segv, n = [], [], [], 0
    for d in dyn:
        F = crop(d["rest"], d["F"], False)
        if not len(F): sel.append(None); continue
        F, _ = cluster(d["rest"], F, DYN_H)
        _, F, used = compact(d["rest"], F)
        sel.append(used); Fs.append(F + n); n += len(used)
        segv.append(d["wi"][used, np.argmax(d["ww"][used], axis=1)])
    Fd = np.concatenate(Fs); SV = np.concatenate(segv).astype(np.uint8)
    b64(os.path.join(OUT, "dyn.txt"), Fd.astype(np.uint32).tobytes() + SV.tobytes())
    json.dump({"nv": n, "nf": len(Fd), "step": STEP, "q": Q}, open(os.path.join(OUT, "dyn.json"), "w"))
    print("moving muscles", len(dyn), "->", n, "v", len(Fd), "f")

    used_files, total = set(), 0
    for dd in designs:
        clips = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", dd, "clips.json")))["clips"]
        mp = os.path.join(REPO, "docs", "viz3d", dd, "motion.json"); M = json.load(open(mp))
        for cl, mc in zip(clips, M["clips"]):
            P = [f["p"] for f in cl["frames"]]
            name = hashlib.sha1(json.dumps([[round(x, 3) for x in p] for p in P]).encode()).hexdigest()[:12] + ".txt"
            fp = os.path.join(OUT, name)
            if not os.path.exists(fp):
                keys = list(range(0, len(P), STEP)) + ([len(P) - 1] if (len(P) - 1) % STEP else [])
                X = []
                for k in keys:
                    _, mus = rig.posed(pose_of(P[k]), muscles=True)
                    W = np.concatenate([mus[d["name"]][s] for d, s in zip(dyn, sel) if s is not None])
                    sg = rig._ctx(pose_of(P[k]), None)["segs"]
                    for g in range(5):                                  # into the frame of each vertex's segment
                        m = SV == g; R, t = (np.asarray(a, float) for a in sg[g]); W[m] = (W[m] - t) @ R
                    X.append(W)
                X = np.stack(X); assert np.abs(X).max() < 32767 * Q, "muscles outside the int16 range"
                T = np.stack([np.concatenate([np.r_[np.asarray(R).ravel(), np.asarray(t)] for R, t in rig._ctx(pose_of(p), None)["segs"][1:5]]) for p in P])
                b64(fp, np.round(X / Q).astype(np.int16).tobytes() + T.astype(np.float32).tobytes())
            used_files.add(name); mc["musc"] = name; total += os.path.getsize(fp)
        json.dump(M, open(mp, "w"), separators=(",", ":"))
        print(dd, "muscle clips", [c["musc"] for c in M["clips"]])
    for f in os.listdir(OUT):                                       # drop clips no design uses any more
        if f.endswith(".txt") and f not in ("static.txt", "dyn.txt") and f not in used_files: os.remove(os.path.join(OUT, f))
    print("muscle keyframes", total // 1024, "KB base64 (all files incl. shared)")


if __name__ == "__main__":
    main(sys.argv[1:] or ["user_conecut_knee"])
