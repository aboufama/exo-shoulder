"""pick1 K hold: what the K lag costs (proximity on the SIMULATED K) and which buildable hold passes R17.

Harness only: imports judge/dynamics.py unchanged. The K law is the judge's clock spring (K_PRELOAD at stop A, the
nominal rate) plus, for the candidate holds, an extra torque on K added through MuJoCo's passive-force callback:
    helper  T(x) = H * max(0, 1 - x / x1)          (a short-stroke helper leaf: H at stop A, unloaded after x1)
    detent  T(x) = H * clip(1 - (x - x0) / (x1 - x0), 0, 1) for x >= x0, H for x < x0   (ball / magnet detent: full hold
            over the notch flank x0, falling to 0 at x1)
with x = K's opening from stop A (deg) and T toward stop A.

modes
  sim     <design> <law json> [clips]       -> drift / lift summary per clip (judge's nominal case + rate 0.010)
  lag     <design> <law json> <out.json>    -> proximity planned vs simulated on Reach a high shelf + Wash opposite shoulder
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "judge")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
import dynamics as D
import mujoco

NOM = dict(speed=1.0, case="passive", mu_eff=0.005, tau0=0.001, tilt="hub")
LAG_CLIPS = ("Reach a high shelf", "Wash opposite shoulder")

def law_torque(law, x_deg):
    """extra torque toward stop A (N.m) at opening x_deg >= 0"""
    kind = law.get("extra")
    if not kind: return 0.0
    H = float(law["H"]); x1 = float(law["x1"]); x0 = float(law.get("x0", 0.0))
    if kind == "helper": return H * max(0.0, 1.0 - x_deg / x1)
    if kind == "detent":
        if x_deg <= x0: return H
        return H * min(1.0, max(0.0, 1.0 - (x_deg - x0) / (x1 - x0)))
    raise ValueError(kind)

def install(des, law):
    """set the judge's spring preload and the extra-torque callback for this law"""
    D.K_PRELOAD = float(law["preload"])
    if not law.get("extra"):
        mujoco.set_mjcb_passive(None); return
    iK, qA, sg = des.spring_def; jn = f"J{iK + 1}"
    def cb(m, d):
        j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
        if j < 0: return
        q = d.qpos[m.jnt_qposadr[j]]; x = math.degrees(sg * (qA - q))
        d.qfrc_passive[m.jnt_dofadr[j]] += sg * law_torque(law, max(0.0, x))
    mujoco.set_mjcb_passive(cb)

def sim_clip(des, ci, law, k_rate=None, record=True):
    install(des, law)
    try:
        summ, R = D.run(des, ci, record=record, k_rate=k_rate, **NOM)
    finally:
        mujoco.set_mjcb_passive(None)
    return summ, R

def frame_q(des, ci, R):
    """simulated joint angles at each clip frame (nearest recorded sample after the settle)"""
    nf = sum(1 for c_, _, _ in des.fr if c_ == ci); s = R["s"]; warm = R["t"] >= D.SETTLE - 1e-9
    idx = []
    for fi in range(nf):
        cand = np.where(warm)[0]; k = cand[np.argmin(np.abs(s[cand] - fi))]; idx.append(k)
    return R["q"][idx], R["qp"][idx], np.array(idx)

def fk(des, Pbase, q):
    R, t = Pbase; out = {"base": (R, t)}
    for k, h in enumerate(des.hinge):
        Rr = h["Rr0"] @ D.rot(h["u"], q[k]); x = h["x"]; tr = h["tr0"] + h["Rr0"] @ x - Rr @ x
        R, t = R @ Rr, R @ tr + t; out[h["child"]] = (R, t)
    return out

def knuckle_open(des, q):
    iK, qA, sg = des.spring_def; return np.degrees(sg * (qA - q[..., iK]))

def summarise_k(des, ci, summ, R):
    """drift, K-open share, unplanned lift (sim K off stop A by > 0.5 deg where the plan has it on stop A)"""
    w = R["warm"]; q, qp = R["q"][w], R["qp"][w]; xs, xp = knuckle_open(des, q), knuckle_open(des, qp)
    lift = (xp < 0.2) & (xs > 0.5)
    return dict(drift_deg=summ.get("spare_drift_deg"), K_open_plan_max_deg=round(float(xp.max()), 2), K_open_sim_max_deg=round(float(xs.max()), 2),
                lag_max_deg=round(float((xp - xs).max()), 2), lead_max_deg=round(float((xs - xp).max()), 2),
                unplanned_lift_share=round(float(lift.mean()), 4), unplanned_lift_max_deg=round(float(xs[xp < 0.2].max()) if (xp < 0.2).any() else 0.0, 2),
                twist_peak_deg=summ["tracking_deg"]["twist_peak"], moment_gh_peak_Nm=summ["moment_gh_Nm"]["peak"], force_peak_N=summ["force_N"]["peak"],
                lags_over_10deg=summ["stalls"]["lags_over_10deg"], worst_missed_deg=summ["stalls"]["worst_missed_deg"],
                on_limit_share=summ.get("on_limit_share"))

# ------------------------------------------------------------------ proximity (score_design.py's metric, re-implemented on given member poses)
class Prox:
    def __init__(self, dd):
        import trimesh, body_pose as BP, metal_groups as MG
        from scipy.spatial import cKDTree
        self.BP, self.cKDTree = BP, cKDTree
        C = json.load(open(os.path.join(dd, "clips.json"))); sc = trimesh.load(os.path.join(dd, "exo.glb"))
        SCORED, _ = MG.classify({n.split("|")[0] for n in sc.graph.nodes_geometry}, MG.clip_groups(C))
        L = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json"))); HRm = np.array(L["landmarks"]["rest_humerus"]); U_, _, Vt_ = np.linalg.svd(HRm); HRm = U_ @ Vt_
        self.L_, self.S_ = L["landmarks"], L["scale"]; MET = {}
        for node in sc.graph.nodes_geometry:                                           # identical sampling to score_design.py (seed 3)
            T_, gname = sc.graph[node]; g = node.split("|")[0]
            if g not in SCORED: continue
            m = sc.geometry[gname].copy(); m.apply_transform(T_)
            n = int(np.clip(m.area / 1.5, 500, 60000)); p, _ = trimesh.sample.sample_surface(m, n, seed=3)
            if g == "H":
                p = p[np.linalg.norm(p @ HRm, axis=1) < 110.0]
                if not len(p): continue
            MET.setdefault(g, []).append(p)
        self.MET = {g: np.concatenate(v) for g, v in MET.items()}
        F = BP.F; V0 = BP.V0; near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < 180)[0]
        A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
        rng = np.random.default_rng(1); NS = int(A0.sum() / 0.25)
        self.fi = near[rng.choice(len(near), NS, p=A0 / A0.sum())]; uv = rng.random((NS, 2)); flip = uv.sum(1) > 1; uv[flip] = 1 - uv[flip]; self.uv = uv; self.F = F
    def metal(self, fr, G=None, T=None, dH=None):
        """posed shoulder metal (thorax mm) for frame fr; G / T override the member poses; dH = (R, t) applied to H about GH (cuff deviation)"""
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); G = G or {g: np.array(v).reshape(3, 3) for g, v in fr["G"].items()}
        T = T or {g: np.asarray(v, float) for g, v in fr.get("T", {}).items()}
        parts = [self.MET[g] @ G[g].T + T.get(g, np.zeros(3)) for g in self.MET if g != "H"]
        if "H" in self.MET:
            sg, _ = self.BP.segs(self.L_, self.S_, pose); P = self.MET["H"] @ np.array(sg[2][0]).T + np.array(sg[2][1])
            if dH is not None: P = P @ dH[0].T + dH[1]
            parts.append(P)
        return np.concatenate(parts)
    def metrics(self, fr, E):
        from sdist import Mesh
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); X = self.BP.posed(pose); F = self.F
        a, b, c = X[F[self.fi, 0]], X[F[self.fi, 1]], X[F[self.fi, 2]]
        sp = a + self.uv[:, :1] * (b - a) + self.uv[:, 1:] * (c - a); ns = np.cross(b - a, c - a); ns /= np.linalg.norm(ns, axis=1, keepdims=True) + 1e-12
        d, ii = self.cKDTree(E).query(sp, workers=2, distance_upper_bound=60.0)
        hit = np.isfinite(d); u = (E[ii[hit]] - sp[hit]) / d[hit, None]; cov = np.zeros(len(sp), bool); cov[np.nonzero(hit)[0][(u * ns[hit]).sum(1) > 0.8]] = True
        g = d[cov]
        out = dict(in14=float(((g >= 2) & (g <= 14)).mean()) if len(g) else 0.0, in10=float(((g >= 2) & (g <= 10)).mean()) if len(g) else 0.0,
                   cov_min=float(g.min()) if len(g) else float("nan"), cov_med=float(np.median(g)) if len(g) else float("nan"))
        # exact metal-to-skin clearance and depth (judge/sdist.py, the R2 instrument) for metal within 12 mm of a body vertex
        vt = self.cKDTree(X); dv = vt.query(E, distance_upper_bound=12.0)[0]; Q = E[np.isfinite(dv)]
        if len(Q):
            M = Mesh(X, F, 2.0).build_grid(1.0, Q.min(0) - 15, Q.max(0) + 15)
            dep, _ = M.max_depth(Q, 0.0); cl = M.closest(Q)[0]; W = M.winding_at(Q) >= 1
            clear = float(cl[~W].min()) if (~W).any() else float("nan")
            out.update(depth=float(dep), clear_min=clear, n_inside=int(W.sum()))
        else: out.update(depth=0.0, clear_min=float("nan"), n_inside=0)
        return out

def lag(dd, law, out_path, step=1):
    des = D.GenDesign(dd); C = json.load(open(os.path.join(des.dd, "clips.json"))); P = Prox(des.dd); res = dict(design=des.id, law=law, clips={})
    for ci, c in enumerate(des.clips):
        if c["name"] not in LAG_CLIPS: continue
        t0 = time.time(); summ, R = sim_clip(des, ci, law); qs, qp, _ = frame_q(des, ci, R)
        frs = [(i, P_) for i, (c_, fi, P_) in enumerate(des.fr) if c_ == ci]
        rows = []
        for fi in range(0, len(frs), step):
            i, Pm = frs[fi]; fr = c["frames"][fi]; Rs = D.scap(fr["p"][1], 0)
            # planned: the clip's own G / T (check the FK reproduces it), simulated: FK at the simulated angles
            Fp = fk(des, Pm["base"], des.q_frames[i]); Fs = fk(des, Pm["base"], qs[fi])
            err = max(float(np.abs(Fp[g][0] - Pm[g][0]).max()) for g in des.groups)
            G = {g: Rs @ Fs[g][0] for g in des.groups}; T = {g: Rs @ Fs[g][1] for g in des.groups}
            Rd = Rs @ Fs["cuff"][0] @ Fp["cuff"][0].T @ Rs.T; td = Rs @ (Fs["cuff"][1] - Fs["cuff"][0] @ Fp["cuff"][0].T @ Fp["cuff"][1])
            mp_ = P.metrics(fr, P.metal(fr)); ms = P.metrics(fr, P.metal(fr, G, T, (Rd, td)))
            xs, xp = float(knuckle_open(des, qs[fi])), float(knuckle_open(des, des.q_frames[i]))
            # J2 margin from its stops (deg): plan vs sim
            lo2, hi2 = des.limits.get(des.spare[0] + 1, (-1e9, 1e9)); q2s, q2p = math.degrees(qs[fi][des.spare[0] + 1]), math.degrees(des.q_frames[i][des.spare[0] + 1])
            rows.append(dict(frame=fi, held=bool(fr["held"]), dK_plan=round(xp, 2), dK_sim=round(xs, 2), fk_err=err,
                             cuff_dev_deg=round(float(np.degrees(np.linalg.norm(D.rotvec(Rd)))), 2),
                             J2_margin_plan=round(min(q2p - lo2, hi2 - q2p), 2), J2_margin_sim=round(min(q2s - lo2, hi2 - q2s), 2),
                             plan={k: round(v, 4) for k, v in mp_.items()}, sim={k: round(v, 4) for k, v in ms.items()}))
        res["clips"][c["name"]] = dict(k=summarise_k(des, ci, summ, R), frames=rows, seconds=round(time.time() - t0))
        print(c["name"], "done", round(time.time() - t0), "s", flush=True)
    for name, r in res["clips"].items():
        fr = [x for x in r["frames"] if not x["held"]]; agg = {}
        for side in ("plan", "sim"):
            v = lambda k: np.array([x[side][k] for x in fr], float)
            agg[side] = dict(in14=round(float(v("in14").mean()), 4), in10=round(float(v("in10").mean()), 4), cov_min=round(float(np.nanmin(v("cov_min"))), 2),
                             clear_min=round(float(np.nanmin(v("clear_min"))), 2), depth_max=round(float(v("depth").max()), 2), frames_inside=int((v("n_inside") > 0).sum()))
        lagf = [x for x in fr if x["dK_plan"] - x["dK_sim"] > 1.0]
        agg["lag_frames"] = len(lagf)
        for side in ("plan", "sim"):
            v = lambda k: np.array([x[side][k] for x in lagf], float)
            agg[side + "_on_lag_frames"] = dict(in14=round(float(v("in14").mean()), 4), in10=round(float(v("in10").mean()), 4), cov_min=round(float(np.nanmin(v("cov_min"))), 2),
                                                clear_min=round(float(np.nanmin(v("clear_min"))), 2)) if lagf else None
        agg["fk_err_max"] = max(x["fk_err"] for x in r["frames"]); agg["cuff_dev_max_deg"] = max(x["cuff_dev_deg"] for x in r["frames"])
        agg["J2_margin_min"] = dict(plan=min(x["J2_margin_plan"] for x in r["frames"]), sim=min(x["J2_margin_sim"] for x in r["frames"]))
        r["summary"] = agg
    json.dump(res, open(out_path, "w"), indent=1); print(json.dumps({k: v["summary"] for k, v in res["clips"].items()}, indent=1))

def simmode(dd, law, clips=None, rates=(None, 0.010)):
    des = D.GenDesign(dd); out = {}
    for ci, c in enumerate(des.clips):
        if clips and c["name"] not in clips: continue
        for kr in rates:
            summ, R = sim_clip(des, ci, law, k_rate=kr)
            out.setdefault(f"rate{kr or D.K_RATES[0]:g}", {})[c["name"]] = summarise_k(des, ci, summ, R)
    return out

if __name__ == "__main__":
    mode, dd, law = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    if mode == "lag": lag(dd, law, sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 1)
    elif mode == "sim":
        clips = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None; out = simmode(dd, law, clips)
        if len(sys.argv) > 5: json.dump(dict(design=dd, law=law, runs=out), open(sys.argv[5], "w"), indent=1)
        for r, v in out.items():
            for cn, x in v.items(): print(f"{r:10s} {cn:24s} drift {x['drift_deg']:6.2f}  open plan {x['K_open_plan_max_deg']:5.1f} sim {x['K_open_sim_max_deg']:5.1f}  lift {x['unplanned_lift_share']:.3f} max {x['unplanned_lift_max_deg']:5.2f}  twist {x['twist_peak_deg']:5.2f}  Mgh {x['moment_gh_peak_Nm']:.3f}")
