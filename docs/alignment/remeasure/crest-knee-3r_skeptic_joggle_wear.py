"""Skeptic re-wear of the crest-knee-3r JOGGLE claim (row best_params_joggle, kj=1) through the joggle verifier's own
fit_fast / worn / extra_checks / joggle_checks (docs/concepts/verify/crest-knee-3r-joggle.py, imported, unchanged; NO
dump written). Independent of tools/alignment_crest_knee_joggle_adapter.py. Records: the corrected report; near-touch
gaps at 1 / 2 / 3 mm (lowest metal incl. M.cmin, as deep_audit); ws / clip in-band 2-14, over-14 share, max; overhead
floors (ws and clip, elev >= 140); ws elev >= 90; per taken pose the knee-to-E-strap clearance (every joggle slice) and
the gap when a strap-level error d jams (a) the rule reading clearance < 0.15 + d and (b) true metal touch clearance < d.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/alignment/remeasure/crest-knee-3r_skeptic_joggle_wear.py bench|held <out.json>
    JOG_MAX=2.78 ... (same; the bent-bar build: the model's own jog_max caps the step at what a 3 mm bar bent at R15 can rise
    in the ramp run, the levels re-solved by the model's LP on the fit bench, then frozen and worn)
"""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("ckjv_sk", os.path.join(REPO, "docs/concepts/verify/crest-knee-3r-joggle.py"))
J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
V, CB, CK, PK, PV, S = J.V, J.CB, J.CK, J.PK, J.PV, J.S
t0 = time.time(); which = sys.argv[1]
P = dict(J.P_JOG)
if os.environ.get("JOG_MAX"): P["jog_max"] = float(os.environ["JOG_MAX"])   # bent-bar build: step capped (model's own jog_max)
M1, P2, fit, ji = V.fit_fast(P)
B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
M = V.worn(M1, P2, B); r = M.run(); assert type(M).__mro__[1] is CK.JogModel
ex, bad1 = PV.extra_checks(M, B); cc, marg = V.crest_checks(M, B, P2); jg, bad2 = J.joggle_checks(M, B)
bad = set(bad1) | set(bad2)
for i in bad: B.res[i] = None
rep = B.report(); res0 = list(B.res)
cmin = getattr(M, "cmin", {}) or {}
tk = [i for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0]
fl = {i: min(float(np.min(B.res[i])), float(cmin.get(i, 1e9))) for i in tk}
near = {}
for thr in (1.0, 2.0, 3.0):
    for i in tk:
        if fl[i] < thr: B.res[i] = np.r_[B.res[i], -1e-3]
    near[f"{thr:g}"] = dict(gap=B.report()["gap"], poses=int(sum(fl[i] < thr for i in tk))); B.res = list(res0)
el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
def stats(ids):
    d = np.concatenate([np.asarray(B.res[i], float) for i in ids]) if ids else np.zeros(0)
    f = sorted(fl[i] for i in ids)
    return dict(n_taken=len(ids), ib14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                over14=round(float((d > 14).mean()), 4) if len(d) else None, over20=round(float((d > 20).mean()), 4) if len(d) else None,
                dmax=round(float(d.max()), 2) if len(d) else None, floor_lt1=int(sum(x < 1 for x in f)), floor_lt2=int(sum(x < 2 for x in f)),
                floors_sorted=[round(x, 2) for x in f][:12])
# knee-to-E-strap clearance per taken pose (same geometry as joggle_checks)
h = S.T_LINK / 2; sl = M._knee_slices(); kE = {}
for i in tk:
    R6, t6 = M.T(6, i); Rm, tm = M.T(M.Emid[0], i); Em = M.Emid[1] @ Rm.T + tm
    kE[i] = min(float(M.sd_box(Em, R6 @ cen + t6, R6 @ Rk, half).min()) - h for cen, Rk, half in sl)
tol = []
for d in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3):
    row = dict(err_mm=d)
    for lab, lim in (("rule", M.ADJ + d), ("touch", d)):
        jam = [i for i in tk if kE[i] < lim]
        for i in jam: B.res[i] = None
        g = B.report(); B.res = list(res0)
        row[lab] = dict(jam=len(jam), gap=g["gap"], reach=g["reach"], follow=g["follow"])
    tol.append(row)
kv = np.array(sorted(kE.values()))
out = dict(wear=which, jog_max=P.get("jog_max"), mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit,
           report={k: rep[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, removed=len(bad), ADJ=M.ADJ, near=near,
           ws=stats([i for i in tk if kind[i] == "ws"]), clip=stats([i for i in tk if kind[i] == "clip"]),
           ws_over140=dict(total=int(((kind == "ws") & (el >= 140)).sum()), **stats([i for i in tk if kind[i] == "ws" and el[i] >= 140])),
           clip_over140=dict(total=int(((kind == "clip") & (el >= 140)).sum()), **stats([i for i in tk if kind[i] == "clip" and el[i] >= 140])),
           ws_over90=dict(total=int(((kind == "ws") & (el >= 90)).sum()), n_taken=int(sum(1 for i in tk if kind[i] == "ws" and el[i] >= 90))),
           kneeE=dict(n=len(kv), min=round(float(kv[0]), 4), lt_0_25=int((kv < 0.25).sum()), lt_0_35=int((kv < 0.35).sum()),
                      lt_0_45=int((kv < 0.45).sum()), p10=round(float(np.percentile(kv, 10)), 3)),
           tolerance=tol, joggle=dict((k, jg[k]) for k in ("tr_a", "tr_b", "step_mm", "ramp_run_mm", "ramp_deg", "bent_bar_R15_max_rise_mm", "bent_bar_ok")),
           secs=round(time.time() - t0, 1))
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float); print(json.dumps(out, default=float))
