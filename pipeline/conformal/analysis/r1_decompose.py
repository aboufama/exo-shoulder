"""Where is R1 lost on a built design? The R1 judge (full-exo/score_design.py, same skin samples, same metal samples,
same 'covered skin' rule, same clip weighting) with every covered skin point tagged by the part its nearest metal
belongs to, its gap class (too close < 2 mm, in band, too far > HI), the clip, the elevation, trunk vs arm skin, and -
for links - hub vs ribbon. Then a split of the too-far gaps into
  slack  = how far that metal point could come down toward the skin and still clear it by 2 mm in EVERY followed frame
           (min over frames of its distance to the posed skin, minus 2): a shape choice;
  motion = the rest: the skin under a rigid part moves away from it in this frame relative to its closest frame
           (rigid metal over moving skin, on this joint path).
"lowered" = R1 if every metal point sat at its own worst-frame 2 mm (a CAD-side analogue of inband_ceiling.py; an
upper bound for ANY reshaping of these parts on this path).

    OMP_NUM_THREADS=2 python3 r1_decompose.py <design dir> [step=3] [HI=14]   -> <design dir>/r1_decompose_<HI>_s<step>[_ws<WS_STEP>].json
"""
import json, os, sys, time
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); FX = os.path.join(HERE, "..", "..", "full-exo")
sys.path.insert(0, os.path.join(FX, "..", "avg")); import body_pose as BP
DD = sys.argv[1]; STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 3; HI = float(sys.argv[3]) if len(sys.argv) > 3 else 14.0
LO, REACH, ARM_NEAR, WK = 2.0, 60.0, 110.0, int(os.environ.get("WORKERS", 2))
C = json.load(open(os.path.join(DD, "clips.json"))); sc = trimesh.load(os.path.join(DD, "exo.glb"))
HRm = np.array(json.load(open(os.path.join(FX, "..", "avg", "body_mesh.json")))["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HRm); HRm = _U @ _Vt
# ---- metal: exactly score_design.py's samples (same node order, same seed), plus a label per sample
MET, LAB = {}, {}
labels = []
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; g = node.split("|")[0]
    if not (g == "base" or (g[0] == "l" and g[1:].isdigit()) or g in ("H", "cuff")): continue
    m = sc.geometry[gname].copy(); m.apply_transform(T_)
    n = int(np.clip(m.area / 1.5, 500, 60000)); p, _ = trimesh.sample.sample_surface(m, n, seed=3)
    if g == "H":
        p = p[np.linalg.norm(p @ HRm, axis=1) < ARM_NEAR]
        if not len(p): continue
    lab = node.rsplit("|", 1)[0]
    if lab not in labels: labels.append(lab)
    MET.setdefault(g, []).append(p); LAB.setdefault(g, []).append(np.full(len(p), labels.index(lab)))
MET = {g: np.concatenate(v) for g, v in MET.items()}; LAB = {g: np.concatenate(v) for g, v in LAB.items()}
GORD = [g for g in MET if g != "H"] + (["H"] if "H" in MET else [])            # score_design's concatenation order
LABA = np.concatenate([LAB[g] for g in GORD]); GRPA = np.concatenate([np.full(len(MET[g]), k) for k, g in enumerate(GORD)])
NM = len(LABA)
LSEG = json.load(open(os.path.join(FX, "..", "avg", "body_mesh.json"))); L_, S_ = LSEG["landmarks"], LSEG["scale"]
# ---- skin: exactly score_design.py's samples
F = BP.F; V0 = BP.V0
near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < 180)[0]
A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
rng = np.random.default_rng(1); NS = int(A0.sum() / 0.25)
fi = near[rng.choice(len(near), NS, p=A0 / A0.sum())]; uv = rng.random((NS, 2)); flip = uv.sum(1) > 1; uv[flip] = 1 - uv[flip]
ARM_SKIN = BP.ARMV[F[fi]].sum(1) >= 2                                            # skin driven by the arm (else trunk / scapula)
def skin(P):
    a, b, c = P[F[fi, 0]], P[F[fi, 1]], P[F[fi, 2]]
    pts = a + uv[:, :1] * (b - a) + uv[:, 1:] * (c - a); nr = np.cross(b - a, c - a); nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-12
    return pts, nr
def metal(fr, pose):
    parts = [MET[g] @ np.array(fr["G"][g]).reshape(3, 3).T for g in GORD if g != "H"]
    if "H" in MET:
        sg, _ = BP.segs(L_, S_, pose); parts.append(MET["H"] @ sg[2][0].T + sg[2][1])
    return np.concatenate(parts)
# ---- joint axes in each link's own frame (from the relative rotations), to split links into hub / ribbon samples
def rel_axis(A, B, frames):
    Rs = []
    for fr in frames:
        GA = np.array(fr["G"][A]).reshape(3, 3)
        if B == "H":
            sg, _ = BP.segs(L_, S_, dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))); GB = sg[2][0]
        else: GB = np.array(fr["G"][B]).reshape(3, 3)
        Rs.append(GA.T @ GB)
    best = None; R0 = Rs[0]
    for i in range(0, len(Rs), max(1, len(Rs) // 12)):
        for j in range(i + 1, len(Rs), max(1, len(Rs) // 12)):
            M = Rs[j] @ Rs[i].T; ang = np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1))
            if best is None or ang > best[0]:
                ax = np.array([M[2, 1] - M[1, 2], M[0, 2] - M[2, 0], M[1, 0] - M[0, 1]]); best = (ang, ax / (np.linalg.norm(ax) + 1e-12))
    return best[1], R0.T @ best[1]                                               # the axis in A's frame and in B's frame
allf = [f for c in C["clips"] for f in c["frames"] if not f["held"]]
chain = [g for g in ("base", "l1", "l2", "l3") if g in MET] + ["H"]
AX = {}                                                                          # group -> list of (joint name, axis in the group frame)
for k in range(len(chain) - 1):
    A, B = chain[k], chain[k + 1]
    try: uA, uB = rel_axis(A, B, allf[::7])
    except Exception as e: print("axis", A, B, e); continue
    AX.setdefault(A, []).append((f"J{k + 1}", uA)); AX.setdefault(B, []).append((f"J{k + 1}", uB))
HUBZONE = 11.5 + 3.0                                                             # mm from a joint axis: hub / stack region
sub = np.array(["-"] * NM, dtype=object)
off = 0
for g in GORD:
    P = MET[g]; n = len(P)                                                       # group frame (H: posed by the humerus rotation, as its axis)
    if g in AX:
        best = np.full(n, np.inf); bj = np.array([""] * n, dtype=object)
        for jn, u in AX[g]:
            u = u * np.sign(np.mean(P @ u) + 1e-9); dax = np.linalg.norm(P - (P @ u)[:, None] * u[None], axis=1)
            dax = np.where(P @ u > 0, dax, np.inf); upd = dax < best; best[upd] = dax[upd]; bj[upd] = jn
        sub[off:off + n] = np.where(best < HUBZONE, "hub " + bj.astype(str), "ribbon" if g != "H" else "neck / bar")
    off += n
SUBS = sorted(set(sub.tolist())); SUBI = np.array([SUBS.index(s) for s in sub])
# ---- pass 1: covered skin per followed frame (score_design's rule), metal clearance per frame
t0 = time.time()
rec = dict(f=[], s=[], m=[], g=[]); fmeta = []
dmin = np.full(NM, np.inf); dmin_f = np.full(NM, -1)
for ci, c in enumerate(C["clips"]):
    fs = c["frames"]; idx = list(range(0, len(fs), STEP)); wclip = len(fs) / len(idx)
    for k in idx:
        fr = fs[k]; pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))
        fmeta.append(dict(clip=ci, k=k, held=bool(fr["held"]), elev=float(fr["p"][1]), w=wclip))
        if fr["held"]: continue
        X = BP.posed(pose); sp, ns = skin(X); E = metal(fr, pose)
        d, ii = cKDTree(E).query(sp, workers=WK, distance_upper_bound=REACH)
        hit = np.isfinite(d); u = (E[ii[hit]] - sp[hit]) / d[hit, None]; cov = np.zeros(len(sp), bool); cov[np.nonzero(hit)[0][(u * ns[hit]).sum(1) > 0.8]] = True
        fid = len(fmeta) - 1; si = np.nonzero(cov)[0]
        rec["f"].append(np.full(len(si), fid, np.int32)); rec["s"].append(si.astype(np.int32)); rec["m"].append(ii[si].astype(np.int32)); rec["g"].append(d[si].astype(np.float32))
        dm, _ = cKDTree(sp).query(E, workers=WK)                                 # each metal point's clearance to the posed skin
        upd = dm < dmin; dmin[upd] = dm[upd]; dmin_f[upd] = fid
    print(f"{c['name']:24s} done {time.time() - t0:.0f}s", flush=True)
# ---- optional: the functional-workspace poses the design follows (workspace.json, evaluator-feasible and closing): the
# clearance the parts also need there if the design keeps its range (R16)
WS_STEP = int(os.environ.get("WS_STEP", 0)); dmin_ws = np.full(NM, np.inf); n_ws = 0
if WS_STEP and os.path.exists(os.path.join(DD, "workspace.json")):
    for fr in json.load(open(os.path.join(DD, "workspace.json")))["poses"][::WS_STEP]:
        if not (fr.get("closes") and fr.get("eval_feasible", True)): continue
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); sp, _ = skin(BP.posed(pose)); E = metal(fr, pose)
        dm, _ = cKDTree(sp).query(E, workers=WK); dmin_ws = np.minimum(dmin_ws, dm); n_ws += 1
    print(f"workspace: {n_ws} followed poses {time.time() - t0:.0f}s", flush=True)
R = {k: np.concatenate(v) for k, v in rec.items()}
FM_clip = np.array([x["clip"] for x in fmeta]); FM_el = np.array([x["elev"] for x in fmeta]); FM_w = np.array([x["w"] for x in fmeta])
ncov = np.bincount(R["f"], minlength=len(fmeta)).astype(float)
W = FM_w[R["f"]] / ncov[R["f"]]                                                  # each followed frame weighs N_c / n_sampled_c, split over its covered skin
Wt = W.sum(); g = R["g"].astype(float); m = R["m"]
inb = (g >= LO) & (g <= HI); close = g < LO; far = g > HI
slack = np.clip(dmin[m] - LO, 0, None); gl = g - slack                           # lowered: every metal point at its own worst-frame 2 mm
inb_l = (gl >= LO - 1e-6) & (gl <= HI)
slack_w = np.clip(np.minimum(dmin, dmin_ws)[m] - LO, 0, None); inb_lw = (g - slack_w >= LO - 1e-6) & (g - slack_w <= HI)   # lowered, keeping the workspace clear
far_x = np.clip(g - HI, 0, None); far_slack = np.minimum(far_x, slack); far_motion = far_x - far_slack
def tab(sel):
    w = W[sel]; ws = w.sum()
    if ws <= 0: return None
    return dict(area=round(float(ws / Wt), 4), in_band=round(float((w * inb[sel]).sum() / ws), 4), too_close=round(float((w * close[sel]).sum() / ws), 4),
                too_far=round(float((w * far[sel]).sum() / ws), 4), lowered_in_band=round(float((w * inb_l[sel]).sum() / ws), 4),
                lowered_keep_ws_in_band=round(float((w * inb_lw[sel]).sum() / ws), 4) if n_ws else None,
                gap_median=round(float(np.median(g[sel])), 2), too_far_excess_median=round(float(np.median(g[sel][far[sel]] - HI)), 2) if far[sel].any() else 0.0,
                slack_median=round(float(np.median(slack[sel])), 2),
                too_far_mm_from_slack=round(float((w * far_slack[sel]).sum() / max(1e-12, (w * far[sel]).sum())), 2),
                too_far_mm_from_motion=round(float((w * far_motion[sel]).sum() / max(1e-12, (w * far[sel]).sum())), 2),
                lost_share=round(float((w * ~inb[sel]).sum() / Wt), 4))
out = dict(design=os.path.basename(os.path.normpath(DD)), band=[LO, HI], step=STEP, R1=round(float((W * inb).sum() / Wt), 4),
           lowered_R1=round(float((W * inb_l).sum() / Wt), 4), lowered_keep_ws_R1=round(float((W * inb_lw).sum() / Wt), 4) if n_ws else None, ws_poses=n_ws,
           all=tab(np.ones(len(g), bool)))
lab_s = LABA[m]; sub_s = SUBI[m]
out["by_part"] = {labels[k]: tab(lab_s == k) for k in range(len(labels)) if (lab_s == k).any()}
out["by_part"] = dict(sorted(out["by_part"].items(), key=lambda kv: -kv[1]["area"]))
out["by_region"] = {f"{labels[k]} / {SUBS[j]}": tab((lab_s == k) & (sub_s == j)) for k in range(len(labels)) for j in range(len(SUBS)) if ((lab_s == k) & (sub_s == j)).sum() > 50}
out["by_region"] = dict(sorted(out["by_region"].items(), key=lambda kv: -kv[1]["area"]))
cl = FM_clip[R["f"]]; out["by_clip"] = {c["name"]: tab(cl == ci) for ci, c in enumerate(C["clips"]) if (cl == ci).any()}
el = FM_el[R["f"]]; out["by_elevation"] = {f"{a}-{b}": tab((el >= a) & (el < b)) for a, b in ((0, 30), (30, 60), (60, 90), (90, 120), (120, 200)) if ((el >= a) & (el < b)).any()}
arm = ARM_SKIN[R["s"]]; out["by_skin"] = dict(arm=tab(arm), trunk_scapula=tab(~arm))
# which frames set each metal point's clearance (the poses that hold the shape up), weighted by the too-far skin it covers
bf = dmin_f[m]; bclip = np.where(bf >= 0, FM_clip[np.clip(bf, 0, None)], -1)
wf = W * far; out["too_far_binding_clip"] = {c["name"]: round(float(wf[bclip == ci].sum() / wf.sum()), 4) for ci, c in enumerate(C["clips"])}
# gap histogram of the covered skin (weighted)
edges = [0, 2, 4, 6, 8, 10, 12, 14, 18, 22, 26, 30, 40, 60]
out["gap_hist"] = {f"{a}-{b}": round(float(W[(g >= a) & (g < b)].sum() / Wt), 4) for a, b in zip(edges[:-1], edges[1:])}
out["axes"] = {gg: [(jn, [round(float(x), 4) for x in u]) for jn, u in v] for gg, v in AX.items()}
json.dump(out, open(os.path.join(DD, f"r1_decompose_{HI:g}_s{STEP}" + (f"_ws{WS_STEP}" if n_ws else "") + ".json"), "w"), indent=1)
print(f"R1 {100 * out['R1']:.1f}% (2-{HI:g} mm)   if every metal point sat at its worst-frame 2 mm: {100 * out['lowered_R1']:.1f}%"
      + (f" (keeping {n_ws} workspace poses clear too: {100 * out['lowered_keep_ws_R1']:.1f}%)" if n_ws else "") + f"   {time.time() - t0:.0f}s")
for k, v in list(out["by_region"].items())[:14]:
    print(f"  {k[:62]:62s} area {100 * v['area']:5.1f}%  in {100 * v['in_band']:5.1f}%  close {100 * v['too_close']:4.1f}%  far {100 * v['too_far']:5.1f}%"
          f" (excess med {v['too_far_excess_median']:5.1f}: slack {v['too_far_mm_from_slack']:5.1f} + motion {v['too_far_mm_from_motion']:5.1f} mm)  lowered {100 * v['lowered_in_band']:5.1f}%")
