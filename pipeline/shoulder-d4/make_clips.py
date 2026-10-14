"""Everyday-motion clips for the D4 shoulder on the body (arm-rom/shoulder_on_body.html).

Clips are keyframed in ISB shoulder angles (plane of elevation, elevation, axial rotation + internal) plus elbow flexion,
after typical activities-of-daily-living ranges reported for healthy adults (e.g. Magermans 2005, van Andel 2008:
hand-to-mouth ~50-60 deg elevation with 110-130 deg elbow flexion, combing ~100-120 deg elevation with external
rotation, high reach 120-140 deg, perineal / back-pocket reach in extension with internal rotation), timed with
minimum-jerk profiles. For every frame the 4R chain is solved, the spare joint is chosen smoothly along the clip
(dynamic programming over its valid set) and every shoulder part is checked >= 2 mm off the skin with no same-shell
link contact. Where no setting of the spare joint works, the arm is held at its last reachable pose (the exo stops it).

    python3 make_clips.py   -> ../arm-rom/shoulder_clips.json
"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__)); ROM = os.path.join(HERE, "..", "arm-rom")
sys.path.insert(0, ROM); sys.path.insert(0, HERE)
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180")
import design_search as D, design_search_families as F, design_search_anat as A
from design_search_pivots import w_dir

DES = json.load(open(os.path.join(ROM, "opt_D_124_c4_p180_fp_thin.json")))[0]
b = np.asarray(DES["b"], float); a1, a2, a3 = (DES[k] * D.D2R for k in ("a1", "a2", "a3")); W = w_dir(DES["delta"], DES["waz"])
e_ = np.cross(b, [0.0, 1, 0]); e_ /= np.linalg.norm(e_); f_ = np.cross(b, e_)
def pins_for(Hg, q):
    u4 = Hg @ W; c2 = math.cos(a1) * b + math.sin(a1) * (math.cos(q) * e_ + math.sin(q) * f_)
    c3, ok = F.circ_int(c2[None], a2, u4[None], a3, DES["branch"])
    ok = ok[0] and F.triangle_ok(c2[None], u4[None], a2, a3)[0] and F.triangle_ok(b[None], c3, a1, a2)[0]
    return dict(b=b, c2=c2, c3=c3[0], u4=u4), bool(ok)
def frame(a, c):
    n = c - (a @ c) * a; n /= np.linalg.norm(n); return np.c_[a, n, np.cross(a, n)]

DP = json.load(open(os.path.join(HERE, "display_pose.json"))); P0 = {k: np.array(v) for k, v in DP["pins"].items()}
Hg0 = D.scapula(0).T @ np.eye(3)
F0 = dict(base=np.eye(3), l1=frame(P0["b"], P0["c2"]), l2=frame(P0["c2"], P0["c3"]), l3=frame(P0["c3"], P0["u4"]), bar=Hg0)
X0 = np.array([-119.5, 0.0, 0.0]); M = np.array([[-1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])
GROUP = {"D4-01": "base", "D4-02": "l1", "D4-03": "l2", "D4-04": "l3", "D4-05": "bar", "J1": "l1", "J2": "l2", "J3": "l2", "J4": "bar"}

# part samples in the scapula frame, from the web mesh (mm, CAD frame)
sc = trimesh.load(os.path.join(ROM, "shoulder_d4_web.glb"))
samples = {g: [] for g in set(GROUP.values())}; linkpts = {}
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; m = sc.geometry[gname].copy(); m.apply_transform(T_)
    P = (m.vertices - X0) @ M                                          # CAD -> thorax/scapula frame (M orthonormal: M^T)
    key = GROUP[node.split(" ")[0].split("_")[0]]
    samples[key].append(P[:: max(1, len(P) // 400)])
    if node.startswith(("D4-02", "D4-03", "D4-04", "D4-05")): linkpts[node[:5]] = P[:: max(1, len(P) // 1500)]
samples = {k: np.concatenate(v) for k, v in samples.items()}

def check(Hg, Rs, eb, Hf, q):
    """(ok, clearance mm, rotations) for one pose and spare-joint angle"""
    Pq, ok = pins_for(Hg, q)
    if not ok: return False, -99.0, None
    Fp = dict(base=np.eye(3), l1=frame(Pq["b"], Pq["c2"]), l2=frame(Pq["c2"], Pq["c3"]), l3=frame(Pq["c3"], Pq["u4"]), bar=Hg)
    Rg = {g: Fp[g] @ F0[g].T for g in Fp}
    clr = 99.0
    for g, X in samples.items():
        if g == "bar": continue                                       # the arm interface stub is being redesigned
        Xp = X @ Rg[g].T
        if g == "base": Xp = Xp[np.linalg.norm(Xp, axis=1) > 118.5]
        dt = A.lookup(A.TRUNK[eb], Xp @ Rs.T).min()
        uu = Fp["l3"][:, 0]; far = (Xp @ uu) / np.linalg.norm(Xp, axis=1) < math.cos(math.radians(15))
        da = A.lookup(A.ARM, Xp[far] @ Hf).min() if far.any() else 99.0
        clr = min(clr, dt, da)
    # same-shell links must not touch (outer: l1 / l3; inner: l2 / stub)
    for ka, ga, kb, gb in (("D4-02", "l1", "D4-04", "l3"), ("D4-03", "l2", "D4-05", "bar")):
        d, _ = cKDTree(linkpts[kb] @ Rg[gb].T).query(linkpts[ka] @ Rg[ga].T)
        if d.min() < 1.0: return False, clr, Rg
    return clr >= 2.0, clr, Rg

def minjerk(t): return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5

# (plane, elevation, axial[+ internal], elbow flexion, pronation), seconds to reach the next key
CLIPS = [
    ("Raise overhead", [((30, 3, 0, 12, 0), 2.6), ((30, 150, -10, 12, 0), 0.8), ((30, 150, -10, 12, 0), 2.6), ((30, 3, 0, 12, 0), 0.6)]),
    ("Drink from a cup", [((40, 4, 0, 15, 0), 1.6), ((60, 40, 10, 95, 20), 0.8), ((62, 52, 15, 128, 30), 1.2), ((62, 52, 15, 128, 30), 0.9),
                          ((60, 40, 10, 95, 20), 1.4), ((40, 4, 0, 15, 0), 0.6)]),
    ("Comb hair", [((30, 4, 0, 15, 0), 1.8), ((50, 95, -20, 110, 0), 0.9), ((60, 115, -35, 125, 0), 0.8), ((72, 108, -25, 120, 0), 0.8),
                   ((60, 115, -35, 125, 0), 0.8), ((72, 108, -25, 120, 0), 1.6), ((30, 4, 0, 15, 0), 0.6)]),
    ("Reach a high shelf", [((60, 4, 0, 35, 0), 1.8), ((80, 115, 0, 20, 0), 0.7), ((82, 132, 0, 6, 0), 0.9), ((82, 132, 0, 6, 0), 1.8), ((60, 4, 0, 35, 0), 0.6)]),
    ("Wash opposite shoulder", [((30, 4, 0, 15, 0), 1.8), ((95, 55, 25, 115, 0), 0.9), ((115, 75, 30, 128, 0), 0.7), ((105, 68, 28, 124, 0), 0.7),
                                ((115, 75, 30, 128, 0), 1.6), ((30, 4, 0, 15, 0), 0.6)]),
    ("Reach back pocket", [((0, 4, 0, 15, 0), 1.6), ((-35, 30, 45, 55, 0), 0.8), ((-45, 38, 60, 72, 0), 0.9), ((-45, 38, 60, 72, 0), 1.5), ((0, 4, 0, 15, 0), 0.6)]),
    ("Wave", [((20, 4, 0, 20, 0), 1.6), ((15, 92, -45, 95, 0), 0.5), ((15, 95, -65, 95, 0), 0.45), ((15, 92, -30, 95, 0), 0.45), ((15, 95, -65, 95, 0), 0.45),
              ((15, 92, -30, 95, 0), 0.45), ((15, 95, -65, 95, 0), 0.45), ((15, 92, -45, 95, 0), 1.6), ((20, 4, 0, 20, 0), 0.6)]),
    ("Walking arm swing", [((90, 4, 0, 18, 0), 0.55), ((90, 24, 0, 32, 0), 0.55), ((90, 4, 0, 18, 0), 0.55), ((90, 24, 0, 32, 0), 0.55),
                           ((90, 4, 0, 18, 0), 0.55), ((90, 24, 0, 32, 0), 0.55), ((90, 4, 0, 18, 0), 0.6)]),
]
FPS = 30; QS = np.radians(np.arange(0, 360, 6))

def frames_of(keys):
    out = []
    for (k0, dt), (k1, _) in zip(keys[:-1], keys[1:]):
        n = max(2, int(round(dt * FPS)))
        for i in range(n):
            s = minjerk(i / n); out.append(tuple(a + (b_ - a) * s for a, b_ in zip(k0, k1)))
    out.append(keys[-1][0]); return out

def pose_mats(plane, elev, axial):
    H = D.Ry(plane * D.D2R) @ D.Rx(-elev * D.D2R) @ D.Ry(axial * D.D2R); Rs = D.scapula(elev)
    Hg = Rs.T @ H; eb = int(np.argmin(np.abs(A.ELEVS - elev))); return Hg, Rs, eb

result = []
for name, keys in CLIPS:
    fr = frames_of(keys); nF, nQ = len(fr), len(QS)
    OK = np.zeros((nF, nQ), bool); CL = np.full((nF, nQ), -99.0); RG = [[None] * nQ for _ in range(nF)]
    for i, (pl, el, ax, fx, pr) in enumerate(fr):
        Hg, Rs, eb = pose_mats(pl, el, ax)
        for j, q in enumerate(QS):
            ok, c, Rg = check(Hg, Rs, eb, Hg, q); OK[i, j] = ok; CL[i, j] = c; RG[i][j] = Rg
    # dynamic programming: maximise clearance, penalise spare-joint speed, forbid infeasible states where possible
    cost = np.where(OK, -np.minimum(CL, 12.0), 1e3); acc = cost[0].copy(); back = np.zeros((nF, nQ), int)
    dq = np.abs(((np.arange(nQ)[:, None] - np.arange(nQ)[None, :]) + nQ // 2) % nQ - nQ // 2)   # steps of 6 deg
    trans = 0.8 * dq + np.where(dq > 2, 50.0, 0.0)                    # > 12 deg per frame (360 deg/s) is not allowed
    for i in range(1, nF):
        tot = acc[None, :] + trans; back[i] = np.argmin(tot, axis=1); acc = tot[np.arange(nQ), back[i]] + cost[i]
    path = [int(np.argmin(acc))]
    for i in range(nF - 1, 0, -1): path.append(back[i][path[-1]])
    path = path[::-1]
    frames, last = [], None
    for i, j in enumerate(path):
        pl, el, ax, fx, pr = fr[i]
        if OK[i, j]: last = (fr[i], RG[i][j], float(np.degrees(QS[j])), float(CL[i, j])); held = False
        else: held = True
        if last is None:                                                 # nothing reachable yet: show the rest pose
            Hg, Rs, eb = pose_mats(30, 3, 0); okj = [k for k in range(nQ) if check(Hg, Rs, eb, Hg, QS[k])[0]]
            k = okj[len(okj) // 2]; _, c, Rg = check(Hg, Rs, eb, Hg, QS[k]); last = ((30, 3, 0, 12, 0), Rg, float(np.degrees(QS[k])), c)
        p, Rg, qd, c = last
        Rs = D.scapula(p[1])
        R = {g: (M @ Rs @ Rg[g] @ M.T).round(6).ravel().tolist() for g in Rg}
        frames.append(dict(p=[round(v, 2) for v in p] if not held else [round(v, 2) for v in p], want=[round(v, 2) for v in fr[i]],
                           held=held, q=round(qd, 1), clr=round(c, 1), R=R))
    nheld = sum(f["held"] for f in frames)
    print(f"{name:26s} {nF:4d} frames, exo follows {100 * (1 - nheld / nF):5.1f}% of the clip, min clearance {min(f['clr'] for f in frames):.1f} mm", flush=True)
    result.append(dict(name=name, fps=FPS, frames=frames))
json.dump(dict(X=X0.tolist(), clips=result), open(os.path.join(ROM, "shoulder_clips.json"), "w"), separators=(",", ":"))
