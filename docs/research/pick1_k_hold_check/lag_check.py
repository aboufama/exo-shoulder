"""Independent check of docs/research/pick1_k_hold.md section 1 (the K lag's effect on proximity), one clip.

Different path from the claim's k_hold.py on purpose:
  * member poses come from MuJoCo's own kinematics (the judge's MJCF, qpos set to the planned / simulated angles,
    xmat / xpos read back), not from a numpy FK through the fitted hinges;
  * simulated angles are linearly interpolated at each frame's path parameter (the claim takes the nearest sample);
  * proximity is score_design.py's metric at its own sampling: EVERY skin sample (the claim: every 4th) and its default
    frame step 3 (the claim: 2);
  * no passive-force callback: the preload is set on the judge's design object exactly as GenDesign does.

    OMP_NUM_THREADS=1 python3 docs/research/pick1_k_hold_check/lag_check.py <design> <preload> <clip name> <out.json> [step=3]
"""
import json, math, os, sys
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
for p in ("judge", os.path.join("pipeline", "avg"), os.path.join("pipeline", "full-exo")): sys.path.insert(0, os.path.join(REPO, p))
import dynamics as D
import mujoco, trimesh
from scipy.spatial import cKDTree
import body_pose as BP, metal_groups as MG

dd, preload, clip, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
STEP = int(sys.argv[5]) if len(sys.argv) > 5 else 3
des = D.GenDesign(dd); des.k_preload = preload; des.spring = des.springs(des.k_rate)
ci = [c["name"] for c in des.clips].index(clip)
summ, R = D.run(des, ci, record=True, speed=1.0, case="passive", mu_eff=0.005, tau0=D.TAU0_ROLL, tilt="hub")
print("drift", summ.get("spare_drift_deg"), "twist", summ["tracking_deg"]["twist_peak"], flush=True)
warm = R["t"] >= D.SETTLE - 1e-9; s_w = R["s"][warm]; q_w = R["q"][warm]
idx = [i for i, (c_, _, _) in enumerate(des.fr) if c_ == ci]
Qsim = np.stack([np.interp(np.arange(len(idx)), s_w, np.unwrap(q_w[:, j])) for j in range(des.N)], 1)
Qplan = des.q_frames[idx]

m = mujoco.MjModel.from_xml_string(D.build_xml_general(des, 0.001)); d = mujoco.MjData(m)
bq = m.jnt_qposadr[0]; qa = [m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"J{k}")] for k in range(1, des.N + 1)]
bid = {g: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, g) for g in des.groups[1:] + ["cuff"]}
def poses(Rs, q):
    d.qpos[:] = 0; d.qpos[bq:bq + 4] = D.quat(Rs)
    for k, a in enumerate(qa): d.qpos[a] = q[k]
    mujoco.mj_kinematics(m, d)
    return {g: (d.xmat[b].reshape(3, 3).copy(), 1000 * d.xpos[b].copy()) for g, b in bid.items()}

C = json.load(open(os.path.join(des.dd, "clips.json"))); sc = trimesh.load(os.path.join(des.dd, "exo.glb"))
SCORED, _ = MG.classify({n.split("|")[0] for n in sc.graph.nodes_geometry}, MG.clip_groups(C))
LM = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json"))); HRm = np.array(LM["landmarks"]["rest_humerus"]); U_, _, Vt_ = np.linalg.svd(HRm); HRm = U_ @ Vt_
MET = {}
for node in sc.graph.nodes_geometry:                                   # score_design.py's metal sampling (seed 3, 110 mm arm rule)
    T_, gname = sc.graph[node]; g = node.split("|")[0]
    if g not in SCORED: continue
    mm = sc.geometry[gname].copy(); mm.apply_transform(T_)
    n = int(np.clip(mm.area / 1.5, 500, 60000)); p, _ = trimesh.sample.sample_surface(mm, n, seed=3)
    if g == "H":
        p = p[np.linalg.norm(p @ HRm, axis=1) < 110.0]
        if not len(p): continue
    MET.setdefault(g, []).append(p)
MET = {g: np.concatenate(v) for g, v in MET.items()}
F = BP.F; V0 = BP.V0; near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < 180)[0]
A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
rng = np.random.default_rng(1); NS = int(A0.sum() / 0.25)
fi_ = near[rng.choice(len(near), NS, p=A0 / A0.sum())]; uv = rng.random((NS, 2)); flip = uv.sum(1) > 1; uv[flip] = 1 - uv[flip]
L_, S_ = LM["landmarks"], LM["scale"]

def metrics(fr, G, T, dev=None):
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); X = BP.posed(pose)
    a, b, c = X[F[fi_, 0]], X[F[fi_, 1]], X[F[fi_, 2]]
    sp = a + uv[:, :1] * (b - a) + uv[:, 1:] * (c - a); ns = np.cross(b - a, c - a); ns /= np.linalg.norm(ns, axis=1, keepdims=True) + 1e-12
    G = dict(G); T = dict(T)
    for g in MET:                                                      # scapula-fixed groups (base): the clip's own pose, the same for plan and sim
        if g != "H" and g not in G: G[g] = np.array(fr["G"][g]).reshape(3, 3); T[g] = np.asarray(fr.get("T", {}).get(g, (0.0, 0.0, 0.0)), float)
    parts = [MET[g] @ G[g].T + T[g] for g in MET if g != "H"]
    if "H" in MET:
        sg, _ = BP.segs(L_, S_, pose); P = MET["H"] @ np.array(sg[2][0]).T + np.array(sg[2][1])
        if dev is not None: P = (P - dev[1]) @ dev[0].T + dev[2]
        parts.append(P)
    E = np.concatenate(parts); tr = cKDTree(E)
    dist, ii = tr.query(sp, workers=1, distance_upper_bound=60.0)
    hit = np.isfinite(dist); u = (E[ii[hit]] - sp[hit]) / dist[hit, None]; cov = np.zeros(len(sp), bool); cov[np.nonzero(hit)[0][(u * ns[hit]).sum(1) > 0.8]] = True
    g = dist[cov]
    # crude inside test: metal points within 3 mm of a skin sample lying on the inner side of its normal
    dm, im = cKDTree(sp).query(E, distance_upper_bound=3.0); h2 = np.isfinite(dm)
    inside = int((((E[h2] - sp[im[h2]]) * ns[im[h2]]).sum(1) < -0.05).sum())
    return dict(in14=float(((g >= 2) & (g <= 14)).mean()) if len(g) else 0.0, in10=float(((g >= 2) & (g <= 10)).mean()) if len(g) else 0.0,
                cov_min=float(g.min()) if len(g) else float("nan"), skin_metal_min=float(np.nanmin(dist)), metal_inside_pts=inside)

rows = []; fk_err = 0.0
for k, i in enumerate(idx):
    fr = des.clips[ci]["frames"][k]; Rs = D.scap(fr["p"][1], 0)
    Pp = poses(Rs, Qplan[k])
    for g in des.groups[1:]:
        fk_err = max(fk_err, float(np.abs(Pp[g][0] - np.array(fr["G"][g]).reshape(3, 3)).max()),
                     1e-3 * float(np.abs(Pp[g][1] - np.asarray(fr.get("T", {}).get(g, (0, 0, 0)), float)).max()))
    if k % STEP: continue
    Ps = poses(Rs, Qsim[k])
    Rcp, tcp = Pp["cuff"]; Rcs, tcs = Ps["cuff"]; dev = (Rcs @ Rcp.T, tcp, tcs)
    gs = [g for g in des.groups[1:] if g in MET or True]
    mp_ = metrics(fr, {g: Pp[g][0] for g in Pp}, {g: Pp[g][1] for g in Pp})
    ms_ = metrics(fr, {g: Ps[g][0] for g in Ps}, {g: Ps[g][1] for g in Ps}, dev)
    iK = des.spring_def[0]
    rows.append(dict(frame=k, held=bool(fr["held"]), dK_plan=round(math.degrees(abs(Qplan[k][iK] - des.spring_def[1])), 2),
                     dK_sim=round(math.degrees(abs(Qsim[k][iK] - des.spring_def[1])), 2),
                     cuff_dev_deg=round(float(np.degrees(np.linalg.norm(D.rotvec(dev[0])))), 2), plan=mp_, sim=ms_))
    if len(rows) % 10 == 0: print(len(rows), "frames", flush=True)
fr_ = [r for r in rows if not r["held"]]
agg = {}
for side in ("plan", "sim"):
    v = lambda k: np.array([r[side][k] for r in fr_], float)
    agg[side] = dict(in14=round(float(v("in14").mean()), 4), in10=round(float(v("in10").mean()), 4), cov_min=round(float(np.nanmin(v("cov_min"))), 2),
                     skin_metal_min=round(float(v("skin_metal_min").min()), 2), frames_with_inside_pts=int((v("metal_inside_pts") > 0).sum()))
lagf = [r for r in fr_ if r["dK_plan"] - r["dK_sim"] > 1.0]
for side in ("plan", "sim"):
    v = lambda k: np.array([r[side][k] for r in lagf], float)
    agg[side + "_lag_frames"] = dict(n=len(lagf), in14=round(float(v("in14").mean()), 4), in10=round(float(v("in10").mean()), 4)) if lagf else None
out = dict(design=des.id, preload=preload, clip=clip, step=STEP, skin_samples=int(NS), drift_deg=summ.get("spare_drift_deg"),
           twist_peak_deg=summ["tracking_deg"]["twist_peak"], mujoco_fk_vs_clip_max=fk_err, cuff_dev_max_deg=max(r["cuff_dev_deg"] for r in rows),
           dK_plan_max=max(r["dK_plan"] for r in rows), dK_sim_max=max(r["dK_sim"] for r in rows), summary=agg, frames=rows)
json.dump(out, open(outp, "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "frames"}, indent=1))
