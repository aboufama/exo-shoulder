"""Alignment probe (new audit instrument, 2026-10-17): the hub-2 lobe pressure angle of an rssr-drive knuckle, exact vs
the model's linearised gate. The law gate uses the small-angle stage-2 gain r_h / La (i_rock = La / s_arm); the real RSSR
map phi(dK) has a ratio dphi/ddK that varies along the stroke. Lobe lift = s_arm * phi(dK(t)); exact tan(pa) = d(lift)/dt / r(t).
Read-only: the model runs UNCHANGED (one fit on Bench(60,160) fast to build the drive tables).

    LS_DRIVE=rssr OMP_NUM_THREADS=1 nice python3 tools/alignment_lobe_exact.py '<params json>' [out.json]
"""
import importlib.util, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ["LS_DRIVE"] = "rssr"
import concept_bench as CB
sp_ = importlib.util.spec_from_file_location("ls_model_lobe_exact", os.path.join(REPO, "docs", "concepts", "models", "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(LS)
par = json.loads(sys.argv[1]); p = LS._clamp(dict(LS.PARAMS, **par))
B = CB.Bench(60, 160); r, M = LS._report(B, p); D = M.D; L = D.law(); g = M._scg
kg = np.asarray(g["kgrid"], float); ph = np.abs(np.asarray(g["phig"], float)); ratio = np.gradient(ph, kg)
dK = np.abs(np.asarray(L["dK"], float)); t = np.asarray(L["q2t"], float); t = np.abs(t - t[0])
s_arm = float(M.p["s_arm"]); rl = float(M.p["r_lobe"]); La = float(M.p["La"]); rh = float(M.p["r_h"])
phi_t = np.interp(dK, kg, ph); lift = s_arm * phi_t; r_t = rl + lift
k_t = np.gradient(dK, t); pa_lin = np.degrees(np.arctan(k_t * rh / ((La / s_arm) * (rl + rh * dK / (La / s_arm)))))
dlift = np.gradient(lift, t); pa_ex = np.degrees(np.arctan(dlift / r_t))
fs = (s_arm + 0.25) / s_arm; pa_ex_tol = np.degrees(np.arctan(dlift * fs / (rl + lift * fs)))      # s_arm +0.25 mm (one tolerance step)
pa_law_tol = np.degrees(np.arctan(np.tan(np.radians(np.asarray(L["pa"], float))) * fs))            # the model gate at s_arm +0.25 (r change ignored)
info = getattr(M, "_sc_info", {}) or {}
dkt = float(info.get("dK_lim", 0))
rows = []
for j in range(0, len(t), max(1, len(t) // 24)):
    rows.append(dict(dK=round(math.degrees(dK[j]), 2), ratio=round(float(np.interp(dK[j], kg, ratio)), 4), pa_law=round(float(L["pa"][j]), 2),
                     pa_lin=round(float(pa_lin[j]), 2), pa_exact=round(float(pa_ex[j]), 2), r=round(float(r_t[j]), 2)))
taken_max = None
try:
    taken_max = float(np.degrees(np.max(np.abs(np.asarray(M.dK, float)[np.asarray(M.kin_ok, bool)]))))
except Exception: pass
lim_t = (dK <= math.radians(taken_max) + 1e-9) if taken_max else np.ones(len(dK), bool)
out = dict(params=par, ratio_small_angle=round(rh / La, 4), ratio_at_0=round(float(ratio[0]), 4), ratio_range_law=[round(float(ratio.min()), 4), round(float(ratio.max()), 4)],
           pa_law_max=round(float(np.max(L["pa"])), 2), pa_exact_max=round(float(np.max(pa_ex)), 2), pa_exact_max_over_fit_taken=round(float(np.max(pa_ex[lim_t])), 2), pa_exact_max_sarm_p025=round(float(np.max(pa_ex_tol)), 2), pa_law_max_sarm_p025=round(float(np.max(pa_law_tol)), 2),
           dK_taken_max_fit=taken_max, n_exact_over_42=int(np.sum(pa_ex > 42 + 1e-9)), dK_first_over_42=(round(math.degrees(float(dK[np.argmax(pa_ex > 42)])), 2) if np.any(pa_ex > 42) else None),
           sc_info={k: info.get(k) for k in ("dK_lim", "why_lim", "ratio_range", "ratio_small_angle", "crest_exact", "trans_min_taken")}, rows=rows)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
for rw in rows: print(json.dumps(rw))
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"), indent=1)
