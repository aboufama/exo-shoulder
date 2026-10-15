"""Does the chain actually move when the arm drives it? (user, 2026-10-15: "if there's some slight friction perhaps it
will be hard for a linkage to pass over another because it's pressing from a bad action angle ... It needs to
actually work"). Quasi-static, rigid links, every joint axis through the GH centre (the band designs' model).
In the scapula frame the humerus turns at w = U qdot, U = [u1 u2 u3] (joint axis directions). Coulomb friction tau_f
in every joint; the arm drives the chain through the cuff with a moment M; virtual work gives U^T M = tau_f sgn(qdot),
so per N.m of joint friction the arm must apply |M| / tau_f = |U^-T sgn(qdot)| (the FRICTION AMPLIFICATION; 1.0-1.7
for orthogonal axes, unbounded as the axes become coplanar - the jam the user describes). Also the joint speed ratio
max|qdot| / |w| (how fast a link whips round per deg/s of arm motion) and the action angle (the worst angle between
the arm's moment and the plane a joint can resist in). For a redundant chain the joint path is the one the evaluator
chose (band_eval detail cfg). Frames: band_poses.b64, 10 fps.
    python3 transmission.py <designs json (list or {"designs": [...]}), each optionally with "_eval": [file, index]>"""
import json, math, os, sys
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI

def poses():
    P = BI.load_poses(open(os.path.join(HERE, "..", "band_poses.b64")).read(), torch.device("cpu"))
    return {k: (v.numpy() if hasattr(v, "numpy") else v) for k, v in P.items()}

def axes(P, d, cfg=None):
    B = BI.Band.__new__(BI.Band); B.t = torch; B.dev = torch.device("cpu"); B.f32 = torch.float32; B.q_step = float(d.get("q_step", 12.0)); B.SING = 10.0 * BI.D2R
    pins, ok, Q = B.chain(dict(d), torch.tensor(P["HG"], dtype=torch.float32)); pins = pins.numpy(); ok = ok.numpy()
    c = np.zeros(len(pins), int) if cfg is None else np.asarray(cfg)
    return pins[np.arange(len(pins)), c], ok[np.arange(len(pins)), c]            # (F, N, 3) unit axis directions

def omega(HG, fps):
    """humerus angular velocity in the scapula frame, central differences (rad/s)"""
    dR = (np.roll(HG, -1, 0) - np.roll(HG, 1, 0)) * fps / 2; W = dR @ np.transpose(HG, (0, 2, 1))
    return np.stack([W[:, 2, 1] - W[:, 1, 2], W[:, 0, 2] - W[:, 2, 0], W[:, 1, 0] - W[:, 0, 1]], 1) / 2

def analyse(P, d, cfg=None, fps=10.0):
    U, ok = axes(P, d, cfg); names = [str(x) for x in P["NAMES"]]; cid = P["CID"]; fi = P["FI"]; N = U.shape[1]
    amp = np.full(len(U), np.nan); spd = np.full(len(U), np.nan); act = np.full(len(U), np.nan); cond = np.full(len(U), np.nan)
    for k in range(len(names)):
        idx = np.nonzero(cid == k)[0]; idx = idx[np.argsort(fi[idx])]
        if len(idx) < 3: continue
        w = omega(P["HG"][idx], fps); w[0], w[-1] = w[1], w[-2]
        for j, f in enumerate(idx):
            A = U[f].T                                                          # 3 x N
            qd = np.linalg.lstsq(A, w[j], rcond=None)[0]                         # minimum-norm joint rates (N = 3: exact)
            s = np.sign(qd); s[np.abs(qd) < 1e-6] = 0
            M = np.linalg.lstsq(A.T, s, rcond=None)[0]                           # U^T M = sgn(qdot): moment per N.m of friction
            amp[f] = np.linalg.norm(M); wn = np.linalg.norm(w[j])
            spd[f] = np.abs(qd).max() / wn if wn > 1e-3 else np.nan
            sv = np.linalg.svd(A, compute_uv=False); cond[f] = sv[0] / max(sv[-1], 1e-9)
            Mu = M / (np.linalg.norm(M) + 1e-12); act[f] = np.degrees(np.arcsin(np.clip(np.abs(A.T @ Mu).max(), 0, 1)))
    out = dict(src=d.get("_src", ""), n=N, clips={})
    for k, n in enumerate(names):
        m = (cid == k) & ok & np.isfinite(amp)
        if not m.any(): continue
        out["clips"][n] = dict(amp_p95=round(float(np.percentile(amp[m], 95)), 2), amp_max=round(float(amp[m].max()), 1),
                               speed_ratio_p95=round(float(np.nanpercentile(spd[m], 95)), 2), speed_ratio_max=round(float(np.nanmax(spd[m])), 1),
                               cond_max=round(float(cond[m].max()), 1), frames_over_amp5=round(float((amp[m] > 5).mean()), 3))
    m = ok & np.isfinite(amp)
    out["all"] = dict(amp_p95=round(float(np.percentile(amp[m], 95)), 2), amp_max=round(float(amp[m].max()), 1), speed_ratio_max=round(float(np.nanmax(spd[m])), 1),
                      frames_over_amp5=round(float((amp[m] > 5).mean()), 3), worst=[names[cid[np.nanargmax(np.where(m, amp, np.nan))]], int(fi[np.nanargmax(np.where(m, amp, np.nan))])])
    return out

if __name__ == "__main__":
    D = json.load(open(sys.argv[1])); D = D["designs"] if isinstance(D, dict) else D; P = poses(); res = []
    for d in D:
        cfg = None
        if d.get("_eval"):
            f, i = d["_eval"]; cfg = json.load(open(f))["results"][i]["cfg"]
        r = analyse(P, d, cfg); res.append(r); a = r["all"]
        print(f"{r['src'][:60]:60s} n{r['n']}: friction amplification p95 {a['amp_p95']:5.2f}, max {a['amp_max']:6.1f} (worst {a['worst']}); "
              f"joint speed up to {a['speed_ratio_max']:.1f}x the arm's; {100 * a['frames_over_amp5']:.1f}% of frames > 5x")
        for n, c in r["clips"].items():
            print(f"     {n:24s} amp p95 {c['amp_p95']:5.2f} max {c['amp_max']:6.1f}   speed p95 {c['speed_ratio_p95']:4.2f}x max {c['speed_ratio_max']:5.1f}x   cond max {c['cond_max']:6.1f}")
    json.dump(res, open(os.path.join(HERE, "transmission.json"), "w"), indent=1)
