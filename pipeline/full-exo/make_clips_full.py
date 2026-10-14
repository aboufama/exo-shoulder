"""Everyday-motion clips for the whole exo on the average body (index.html). Keyframes from clip_keys.json (ISB
shoulder angles + elbow flexion, twist-free axial, hand targets solved by IK: hand-to-mouth, combing, high reach,
washing the opposite shoulder, back pocket, waving, walking swing, overhead raise), minimum-jerk timing. Per frame: the
4R chain is solved; the spare joint J1 is chosen smoothly along the clip (dynamic programming over its valid set,
preferring the configuration that rides closest to the skin); valid = every shoulder part >= 2 mm off the skin, links
1 / 3 never touch, no shoulder link touches BOTTOM (the J4 inner member, rigid with the arm). Where nothing works the
arm is held at its last reachable pose. Also reported: how far the exo stands off the back (skin facing
backwards), the projection the user wants under 10 mm.

    python3 make_clips_full.py <design dir>      -> <design dir>/clips.json
"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); DD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else HERE)
AVG = os.path.join(HERE, "..", "avg"); sys.path.insert(0, AVG)
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
import design_search as D, design_search_families as F, design_search_anat as A
from design_search_pivots import w_dir

SHD = json.load(open(os.path.join(DD, "shoulder", "display_pose.json"))); DES = SHD["DES"]
b = np.asarray(DES["b"], float); a1, a2, a3 = (DES[k] * D.D2R for k in ("a1", "a2", "a3")); Wd = w_dir(DES["delta"], DES["waz"])
e_ = np.cross(b, [0.0, 1, 0]); e_ /= np.linalg.norm(e_); f_ = np.cross(b, e_)
def pins_for(Hg, q):
    u4 = Hg @ Wd; c2 = math.cos(a1) * b + math.sin(a1) * (math.cos(q) * e_ + math.sin(q) * f_)
    c3, ok = F.circ_int(c2[None], a2, u4[None], a3, DES["branch"])
    ok = ok[0] and F.triangle_ok(c2[None], u4[None], a2, a3)[0] and F.triangle_ok(b[None], c3, a1, a2)[0]
    return dict(b=b, c2=c2, c3=c3[0], u4=u4), bool(ok)
def frame(a, c):
    n = c - (a @ c) * a; n /= np.linalg.norm(n); return np.c_[a, n, np.cross(a, n)]
P0 = {k: np.array(v) for k, v in SHD["pins"].items()}
F0 = dict(base=np.eye(3), l1=frame(P0["b"], P0["c2"]), l2=frame(P0["c2"], P0["c3"]), l3=frame(P0["c3"], P0["u4"]))
BJ = json.load(open(os.path.join(AVG, "body_mesh.json"))); HR = np.array(BJ["landmarks"]["rest_humerus"])

# samples per group in the canonical (pose-0) scapula frame; H parts (rest frame) -> canonical with HR^T
sc = trimesh.load(os.path.join(DD, "exo.glb"))
S = {}; LINK = {}
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; m = sc.geometry[gname]; P = trimesh.transform_points(m.vertices, T_)
    g, nm = node.split("|")[0], node.split("|")[1]
    if g == "F": continue
    if g == "H":
        if not (nm.startswith("BOTTOM") or nm.startswith("J4")): continue       # arm parts below are static w.r.t. the arm
        P = P @ HR                                                              # rest -> canonical (H seg at pose 0 = HR^T)
    S.setdefault(g, []).append(P[:: max(1, len(P) // 500)])
    if nm.startswith(("D4-02", "D4-03", "D4-04")) or nm.startswith("BOTTOM"): LINK[nm[:5]] = P[:: max(1, len(P) // 2500)]
S = {k: np.concatenate(v) for k, v in S.items()}
BOT = LINK["BOTTO"]; BOT_far = BOT[np.linalg.norm(BOT - (BOT @ (Wd)) [:, None] * Wd[None], axis=1) > SHD["stack"]["HUB_R"] + 1.0]  # off the J4 stack

def back_proj(Xp, Rs, eb):
    """mm the exo's outer points stand off skin that faces backwards (trunk grid; outward normal n_x < -0.5)"""
    Pt = Xp @ Rs.T; g = A.TRUNK[int(round(eb))]; d = A.lookup(g, Pt); gr = []
    for k in range(3):
        e = np.zeros(3); e[k] = 3.0; gr.append((A.lookup(g, Pt + e) - A.lookup(g, Pt - e)) / 6.0)
    gx = gr[0] / (np.sqrt(gr[0] ** 2 + gr[1] ** 2 + gr[2] ** 2) + 1e-9)
    m = (gx < -0.5) & (d < 40.0)
    return float(d[m].max()) if m.any() else 0.0

BACK_MAX = float(os.environ.get("CLIP_BACK_MAX", 0)) or None
import conformal as CF                                    # radial skin maps (exact skin, fat layer included)
def _tmap(M, eb, it):
    """trunk map value at pixels it, linearly interpolated between the elevation bins around the fractional bin eb
    (nearest bin where a re-entry appears / vanishes between them)"""
    e0 = int(math.floor(eb)); e1 = min(e0 + 1, M.shape[0] - 1); t = eb - e0
    v0, v1 = M[e0].ravel()[it], M[e1].ravel()[it]; both = np.isfinite(v0) & np.isfinite(v1)
    return np.where(both, (1 - t) * np.where(both, v0, 0) + t * np.where(both, v1, 0), v0 if t < 0.5 else v1)
def map_clear(Xp, Rs, Hg, eb):
    """per point: (ok >= 2 mm off the skin and below any re-entry, normal gap mm); eb = fractional elevation bin"""
    r = np.linalg.norm(Xp, axis=1); w = Xp / r[:, None]
    it = CF.pix(w @ Rs.T); ia = CF.pix(w @ Hg)
    lo = np.maximum(_tmap(CF.T_R1C, eb, it), CF.A_R1C.ravel()[ia]); hi = np.minimum(_tmap(CF.T_R2C, eb, it), CF.A_R2C.ravel()[ia])
    skt, ska = _tmap(CF.T_R1, eb, it), CF.A_R1.ravel()[ia]; sk = np.maximum(skt, ska)
    cs = np.where(skt >= ska, _tmap(CF.T_COS, eb, it), CF.A_COS.ravel()[ia])
    ok = (r >= lo - 1.0) & (r <= hi + 0.5)
    return ok, (r - sk) * cs
def check(Hg, Rs, eb, q):
    Pq, ok = pins_for(Hg, q)
    if not ok: return False, -99.0, None, 0.0
    Fp = dict(base=np.eye(3), l1=frame(Pq["b"], Pq["c2"]), l2=frame(Pq["c2"], Pq["c3"]), l3=frame(Pq["c3"], Pq["u4"]))
    Rg = {g: Fp[g] @ F0[g].T for g in Fp}; Rg["H"] = Hg
    clr = 99.0; back = 0.0; gaps_all = []
    for g, X in S.items():
        Xp = X @ Rg[g].T
        if g == "base": Xp = Xp[np.linalg.norm(Xp, axis=1) > SHD["stack"]["R_I0"] - 0.5]
        if g == "H": continue                                                   # rides on the arm: not on the back, skin checked at rest
        back = max(back, back_proj(Xp, Rs, eb))
        okm, gap = map_clear(Xp, Rs, Hg, eb)
        if not okm.all(): return False, float(gap.min()), Rg, back
        clr = min(clr, float(gap.min()))
        if g in ("l1", "l2", "l3"): gaps_all.append(gap[gap < 60])
    Rg["_med"] = float(np.median(np.concatenate(gaps_all))) if gaps_all else None
    tl = {k: cKDTree(LINK[k] @ Rg[g].T) for k, g in (("D4-02", "l1"), ("D4-03", "l2"), ("D4-04", "l3"))}
    if tl["D4-02"].query(LINK["D4-04"] @ Rg["l3"].T)[0].min() < 1.0: return False, clr, Rg, back
    Bp = BOT_far @ Hg.T
    for k in ("D4-02", "D4-03", "D4-04"):
        if tl[k].query(Bp)[0].min() < (0.3 if k == "D4-04" else 1.0): return False, clr, Rg, back   # l3 rides 1 mm over BOTTOM's flat top by design
    if BACK_MAX and back > BACK_MAX: return False, clr, Rg, back                 # the design's low-profile rule
    return True, clr, Rg, back                        # clearance already enforced by the exact maps (>= 2 mm)

def minjerk(t): return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5
# natural keyframes (clip_keys.py): twist-free axial, hand-target keyframes solved by IK on the body rig
CLIPS = [(n, [(tuple(p), d) for p, d in ks]) for n, ks in json.load(open(os.path.join(HERE, os.environ.get("CLIP_KEYS", "clip_keys.json"))))]   # CLIP_KEYS=clip_keys_legacy.json: the old (twisted) keyframes
FAST = os.environ.get("FAST") == "1"
FPS = 10 if FAST else 30; QS = np.radians(np.arange(0, 360, 18 if FAST else 6))
if FAST: CLIPS = CLIPS[:2]
def frames_of(keys):
    out = []
    for (k0, dt), (k1, _) in zip(keys[:-1], keys[1:]):
        n = max(2, int(round(dt * FPS)))
        for i in range(n): s = minjerk(i / n); out.append(tuple(a + (b_ - a) * s for a, b_ in zip(k0, k1)))
    out.append(keys[-1][0]); return out
def pose_mats(plane, elev, axial):
    H = D.Ry(plane * D.D2R) @ D.Rx(-elev * D.D2R) @ D.Ry(axial * D.D2R); Rs = D.scapula(elev)
    return Rs.T @ H, Rs, float(np.interp(elev, CF.ELEVS, np.arange(len(CF.ELEVS))))

ONLY = [int(x) for x in os.environ["CLIPS_ONLY"].split(",")] if os.environ.get("CLIPS_ONLY") else list(range(len(CLIPS)))
DQ_MAX = int(os.environ.get("DQ_MAX", 1))            # spare-joint steps (of 6 deg) per frame: 6 deg/frame = 180 deg/s
ROT_MAX = math.radians(float(os.environ.get("ROT_MAX", 6.0)))   # any link may turn at most this much per frame
RESUME = float(os.environ.get("RESUME", 2.5))         # deg: a held arm resumes when the motion passes back this close

def rot_angle(Ra, Rb):
    c = (np.trace(Ra.T @ Rb) - 1) / 2; return math.acos(max(-1.0, min(1.0, c)))

result = []
for ci, (name, keys) in enumerate(CLIPS):
    if ci not in ONLY: continue
    fr = frames_of(keys); nF, nQ = len(fr), len(QS)
    OK = np.zeros((nF, nQ), bool); CL = np.full((nF, nQ), -99.0); RG = [[None] * nQ for _ in range(nF)]; BK = np.zeros((nF, nQ)); MD = np.full((nF, nQ), 60.0)
    for i, (pl, el, ax, fx, pr) in enumerate(fr):
        Hg, Rs, eb = pose_mats(pl, el, ax)
        for j, q in enumerate(QS):
            ok, c, Rg, bk = check(Hg, Rs, eb, q); OK[i, j] = ok; CL[i, j] = c; RG[i][j] = Rg; BK[i, j] = bk
            if ok and Rg.get("_med") is not None: MD[i, j] = Rg["_med"]
    sh = np.array([f[:3] for f in fr])                                        # shoulder angles per frame
    def smooth_ok(i0, j0, i1, j1):
        """transition (i0,j0)->(i1,j1): spare joint within DQ_MAX steps and every link turns < ROT_MAX"""
        dq = abs(((j1 - j0) + nQ // 2) % nQ - nQ // 2)
        if dq > DQ_MAX: return False
        Ra_, Rb_ = RG[i0][j0], RG[i1][j1]
        return all(rot_angle(Ra_[g], Rb_[g]) < ROT_MAX for g in ("l1", "l2", "l3"))
    # DP over (frame, q). A state is 'following' frame i with q j. From the state at frame i the arm either follows the
    # next frame (smooth transition) or, if it cannot, it is HELD: it waits until a later frame k whose shoulder pose is
    # within RESUME deg of frame i's pose (the motion came back) and continues from there.
    NEG = -1e9; val = np.full((nF, nQ), NEG); prev = {}
    for j in range(nQ):
        if OK[0, j]: val[0, j] = -0.05 * MD[0, j]
    if not OK[0].any():                                                       # clip starts outside the range: start at its first reachable frame
        k0 = next((i for i in range(nF) if OK[i].any()), None)
        if k0 is None: k0 = 0
        for j in range(nQ):
            if OK[k0, j]: val[k0, j] = -0.05 * MD[k0, j]
    for i in range(nF - 1):
        js = np.nonzero(val[i] > NEG / 2)[0]
        for j in js:
            moved = False
            for dj in range(-DQ_MAX, DQ_MAX + 1):
                j1 = (j + dj) % nQ
                if OK[i + 1, j1] and smooth_ok(i, j, i + 1, j1):
                    v = val[i, j] + 1000 - 0.05 * MD[i + 1, j1] - 2.0 * abs(dj)
                    if v > val[i + 1, j1]: val[i + 1, j1] = v; prev[(i + 1, j1)] = (i, j, "follow")
                    moved = True
            if not moved:                                                     # held at frame i until the motion returns
                for k in range(i + 2, nF):
                    if np.abs(sh[k] - sh[i]).max() <= RESUME:
                        for dj in range(-DQ_MAX, DQ_MAX + 1):
                            j1 = (j + dj) % nQ
                            if OK[k, j1] and smooth_ok(i, j, k, j1):                # resuming must not flick either
                                v = val[i, j] + 1000 * 0.2 - 0.05 * MD[k, j1]
                                if v > val[k, j1]: val[k, j1] = v; prev[(k, j1)] = (i, j, "hold")
                        break
    # best end state, then walk back
    flat = np.argmax(val[nF - 1]); end = (nF - 1, int(flat))
    if val[end] < NEG / 2:
        cand = [(val[i].max(), i) for i in range(nF) if val[i].max() > NEG / 2]; _, ie = max(cand); end = (ie, int(np.argmax(val[ie])))
    path = {}; cur = end
    while True:
        path[cur[0]] = (cur[1], "follow")
        if cur not in prev: break
        i0, j0, how = prev[cur]
        if how == "hold":
            for t in range(i0 + 1, cur[0]): path[t] = (j0, "held", i0)
        cur = (i0, j0)
    frames = []
    for i in range(nF):
        if i in path and path[i][1] == "follow":
            j = path[i][0]; p = fr[i]; held = False; Rg = RG[i][j]; qd = float(np.degrees(QS[j])); c = CL[i, j]; bk = BK[i, j]
        else:
            if i in path: j, _, i0 = path[i]
            else:                                                             # before the first / after the last reachable frame
                ks = sorted(path); i0 = min(ks, key=lambda t: abs(t - i)); j = path[i0][0]
                if path[i0][1] != "follow": i0 = path[i0][2]
            p = tuple(fr[i0][:3]) + tuple(fr[i][3:]); held = True; Rg = RG[i0][j]; qd = float(np.degrees(QS[j])); c = CL[i0, j]; bk = BK[i0, j]
        Rs = D.scapula(p[1]); G = {g: (Rs @ Rg[g]).round(6).ravel().tolist() for g in ("base", "l1", "l2", "l3")}
        med = Rg.get("_med") if isinstance(Rg, dict) else None
        frames.append(dict(p=[round(float(x), 2) for x in p], want=[round(float(x), 2) for x in fr[i]], held=bool(held), q=round(float(qd), 1),
                           clr=round(float(c), 1), back=round(float(bk), 1), med=None if med is None else round(med, 1), G=G))
    # flick audit: the biggest per-frame link rotation and pose step in the final clip
    worst_rot = 0.0; worst_pose = 0.0
    for i in range(1, nF):
        Ga = [np.array(frames[i - 1]["G"][g]).reshape(3, 3) for g in ("l1", "l2", "l3")]; Gb = [np.array(frames[i]["G"][g]).reshape(3, 3) for g in ("l1", "l2", "l3")]
        worst_rot = max(worst_rot, max(rot_angle(a_, b_) for a_, b_ in zip(Ga, Gb)))
        worst_pose = max(worst_pose, float(np.abs(np.array(frames[i]["p"][:3]) - np.array(frames[i - 1]["p"][:3])).max()))
    nh = sum(f["held"] for f in frames)
    print(f"{name:26s} {nF:4d} frames, follows {100 * (1 - nh / nF):5.1f}%, min skin gap {min(f['clr'] for f in frames):.1f} mm, "
          f"max link turn/frame {math.degrees(worst_rot):.1f} deg, max arm step {worst_pose:.1f} deg", flush=True)
    result.append(dict(name=name, fps=FPS, frames=frames))
sub = sys.argv[2] if len(sys.argv) > 2 else "average adult · 1.75 m"
out = "clips.json" if not os.environ.get("CLIPS_ONLY") else f"clips_part_{os.environ['CLIPS_ONLY'].replace(',', '_')}.json"
json.dump(dict(subtitle=sub, pins={k: v for k, v in SHD["pins"].items()}, clips=result), open(os.path.join(DD, out), "w"), separators=(",", ":"), default=float)
