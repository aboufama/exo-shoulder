"""fit the cuff's two end ellipses (bar frame: w along BOTTOM, q across, p toward the bar) around the swept envelope"""
import numpy as np, sys, json
from scipy.optimize import minimize
sys.argv = ["x"]; exec(open("cuff_fair.py").read().split("# ---------------------------------------------------------------- the bar's land")[0])
c_bar = CB + 124.25 * uB - 2.8 * axB
Xg, Yg = np.meshgrid(np.radians(TH) * R0, SS, indexing="ij"); P = cyl(Xg, Yg, env); thg = np.broadcast_to(TH[:, None], Xg.shape)
w_ = (P - c_bar) @ uB
TH_A, TH_P = -72.0, 112.0; half_sp = 40.4; s_c = 204.8
ant = smooth((-thg - 12.0) / 70.0); post = smooth((thg - 18.0) / 85.0)
s_hi = s_c + half_sp - 54.0 * ant - (half_sp - 27.0) * post; s_lo = s_c - half_sp - 10.0 * ant + (half_sp - 27.0) * post
sel = (thg >= TH_A - 4) & (thg <= TH_P + 4) & (Yg >= s_lo - 4) & (Yg <= s_hi + 4)
P = P[sel]; w_ = w_[sel]; q_ = (P - c_bar) @ vB; p_ = (P - c_bar) @ axB
print("points", len(P), "vB.e2 (posterior)", float(vB @ e2))
W0, W1 = -45.0, 45.0; T, M = 2.0, 2.0
def params(x, w):
    t = (w - W0) / (W1 - W0); x0, x1 = x[:4], x[4:]; return [(1 - t) * x0[k] + t * x1[k] for k in range(4)]   # qc, top, A, B (top = outer top height)
def F(x):
    qc, top, A, B = params(x, w_); pc = top - T - B
    return ((q_ - qc) / (A - M)) ** 2 + ((p_ - pc) / (B - M)) ** 2
def obj(x):
    pen = np.maximum(F(x) - 1.0, 0); return x[2] * x[3] + x[6] * x[7] + 1e5 * np.sum(pen ** 2) + 50 * (x[1] ** 2 + x[5] ** 2)
x0 = np.array([5.0, 0.0, 70.0, 60.0, 5.0, 0.0, 65.0, 55.0])
bnd = [(-30, 30), (-3.0, 0.0), (40, 110), (40, 110)] * 2
r = minimize(obj, x0, method="L-BFGS-B", bounds=bnd, options=dict(maxiter=3000))
x = r.x.copy()
for _ in range(200):                                        # inflate until every point clears
    if F(x).max() <= 1.0: break
    x[[2, 3, 6, 7]] += 0.1
print("max F", F(x).max().round(4), "ends (qc, outer top, A, B):", np.round(x[:4], 2), np.round(x[4:], 2))
qc, top, A, B = params(x, w_); pc = top - T - B
gap = (np.sqrt(F(x)) ** -1 - 1)                              # crude relative clearance
th_e = np.degrees(np.arctan2((q_ - qc) / A, (p_ - pc) / B))
print("phi range of the covered envelope:", th_e.min().round(1), th_e.max().round(1))
json.dump(dict(W0=W0, W1=W1, T=T, M=M, x=x.tolist()), open("out_cuff/ellipses.json", "w"), indent=1)
d = np.hypot(q_ - qc, p_ - pc); k = 1 / np.sqrt(F(x)); gapmm = (k - 1) * d + M
for nm, m in (("elbow half", w_ < 0), ("shoulder half", w_ >= 0), ("posterior th>60", None)):
    if m is None: m = np.zeros(len(w_), bool); m[:] = False
    if m.any(): print(f"{nm}: liner gap median {np.median(gapmm[m]):.1f}, p90 {np.percentile(gapmm[m], 90):.1f}, max {gapmm[m].max():.1f} mm")
