"""SIM-TO-REAL 1 - does the chain self-lock (wedge) when plain-bearing friction grows with the load it carries?
transmission.py (pipeline/conformal/analysis) uses a constant Coulomb torque per joint. In a plain bearing the friction
torque grows with the tilt couple the joint carries (the moment component perpendicular to its axis, reacted by the
thrust washers / sleeve):  tau_f,i = tau0 + mu_eff |M_perp,i|.  A moving joint i is then driven only if
s_i (u_i . M) >= tau0 + mu_eff |M_perp,i|, i.e. the arm's moment M makes an action angle alpha_i = asin(s_i u_i.m) with the
joint's plane and tan(alpha_i) > mu_eff (tau0 -> 0). alpha* = max over moment directions m of min_i alpha_i is the best
the arm can do; the chain self-locks (no moment, however large, moves it) iff tan(alpha*) <= mu_eff.
mu_eff ~ mu (iglidur, 0.06-0.18) when the thrust washers carry the tilt couple; ~ 2 mu r_pin / L_sleeve = 0.37 (mu 0.15,
r 5, L 4.05 mm) when the sleeve carries it (washer float grown by wear). Also reported: the component of the frictionless
driving moment along the humerus axis per N.m of joint friction - the cuff's weakest direction (~0.03 N.m/deg about the
long axis, Schiebl et al. 2025, Sensors 25:4605).  Same designs, poses and joint path as transmission.py (10 fps).
    python3 rt_wedge.py   -> results/wedge.json"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "analysis")); os.chdir(os.path.join(REPO, "pipeline", "conformal"))
import transmission as TR                                               # noqa: E402
P = TR.poses(); names = [str(x) for x in P["NAMES"]]; cid = P["CID"]; fi = P["FI"]
D = json.load(open(os.path.join(REPO, "pipeline", "conformal", "analysis", "designs_transmission.json")))
S = np.random.default_rng(0).normal(size=(4000, 3)); S /= np.linalg.norm(S, axis=1, keepdims=True)

def alpha_star(U, s):
    mv = s != 0
    if not mv.any(): return 90.0
    V = U[mv] * s[mv, None]; m0 = S[np.argmax((S @ V.T).min(1))]
    r = minimize(lambda x: -np.min(V @ (x / np.linalg.norm(x))), m0, method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-7, maxiter=400))
    return math.degrees(math.asin(np.clip(-r.fun, -1, 1)))

res = []
for d in D:
    cfg = None
    if d.get("_eval"):
        f, i = d["_eval"]; cfg = json.load(open(f))["results"][i]["cfg"]
    U, ok = TR.axes(P, d, cfg); al = np.full(len(U), np.nan); ax = np.full(len(U), np.nan)
    for k in range(len(names)):
        idx = np.nonzero(cid == k)[0]; idx = idx[np.argsort(fi[idx])]
        if len(idx) < 3: continue
        w = TR.omega(P["HG"][idx], 10.0); w[0], w[-1] = w[1], w[-2]
        for j, f_ in enumerate(idx):
            wn = np.linalg.norm(w[j])
            if not ok[f_] or wn < 1e-3: continue
            A = U[f_].T; qd = np.linalg.lstsq(A, w[j], rcond=None)[0]; s = np.sign(qd); s[np.abs(qd) < 1e-6 * wn] = 0
            al[f_] = alpha_star(U[f_], s)
            M = np.linalg.lstsq(A.T, np.sign(qd), rcond=None)[0]                     # frictionless driving moment, 1 N.m per joint
            ax[f_] = abs(M @ (P["HG"][f_] @ np.array([0.0, -1.0, 0.0])))
    m = np.isfinite(al)
    row = dict(src=d.get("_src", ""), n=int(U.shape[1]), alpha_star_min_deg=round(float(np.nanmin(al)), 1), alpha_star_p5_deg=round(float(np.nanpercentile(al, 5)), 1),
               mu_crit_min=round(math.tan(math.radians(np.nanmin(al))), 3), mu_crit_p5=round(math.tan(math.radians(np.nanpercentile(al, 5))), 3),
               share_of_frames_self_locking={str(mu): round(float((np.tan(np.radians(al[m])) <= mu).mean()), 3) for mu in (0.1, 0.15, 0.2, 0.3, 0.37)},
               humeral_axis_moment_per_Nm_joint_friction=dict(p50=round(float(np.nanmedian(ax)), 2), p95=round(float(np.nanpercentile(ax, 95)), 2), max=round(float(np.nanmax(ax)), 2)),
               clips={n: dict(alpha_star_min_deg=round(float(al[(cid == k) & m].min()), 1), mu_crit=round(math.tan(math.radians(al[(cid == k) & m].min())), 3))
                      for k, n in enumerate(names) if ((cid == k) & m).any()})
    res.append(row)
    print(f"{row['src'][:48]:48s} n{row['n']}: self-locks if mu_eff >= {row['mu_crit_min']} (worst frame), {row['mu_crit_p5']} (p5); "
          f"frames locked at mu_eff 0.37: {100 * row['share_of_frames_self_locking']['0.37']:.0f}%; humeral-axis moment p95 {row['humeral_axis_moment_per_Nm_joint_friction']['p95']} N.m per N.m")
json.dump(res, open(os.path.join(HERE, "results", "wedge.json"), "w"), indent=1)
