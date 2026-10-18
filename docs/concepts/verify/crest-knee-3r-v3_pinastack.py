import importlib.util, json, os, sys, numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")); sys.path.insert(0, REPO + "/tools")
sp = importlib.util.spec_from_file_location("ckv", REPO + "/docs/concepts/verify/crest-knee-3r.py"); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
PK = V.PK; S = PK.S
M1, P2, fit, ji = V.fit_fast(dict(V.ROW["best_params"]))
D = M1.D; sn = D.sn; tp = M1.p["tp"]; A0 = M1.fr["A0"]
Etop = M1.rigid["E"][1] + S.T_LINK * sn
w = Etop - A0; rad = np.linalg.norm(w - (w @ sn)[:, None] * sn, axis=1)
lev_top = (Etop @ sn); knee_u = float((A0 @ sn) * 0 + M1.tr + tp + S.RUN)
# levels along sn are measured from the skin-normal origin used by rigid (g[..][1] + h*sn): use the same h basis
hx = M1.hEx; top = hx + S.T_LINK
out = {}
for lo, hi in ((0, 6.0), (6.0, 6.5), (6.5, 8.5), (8.5, 12)):
    m = (rad >= lo) & (rad < hi)
    if m.any(): out[f"{lo}-{hi}"] = dict(n=int(m.sum()), top_max=round(float(top[m].max()), 3), clearance_min=round(float(knee_u - top[m].max()), 3))
print(json.dumps(dict(fit=fit, tr=M1.tr, tp=tp, knee_underside=round(knee_u, 3), boss_top=round(M1.tr + tp, 3), by_radius_from_pin_a=out)))
