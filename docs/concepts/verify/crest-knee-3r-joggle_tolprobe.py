"""Tolerance probe for the crest-knee-3r joggle claim: the pin-a stack lets the knee link ride 0.20 mm over the E strap
(adjacent rule 0.15). Count the taken poses whose knee-vs-E-strap clearance (every joggle slice, no exemption) is below
0.15 + d for strap-level errors d, and the frozen gap if those poses jam.
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r-joggle_tolprobe.py <bench|held> <out.json> [flat]"""
import importlib.util, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("ckj", os.path.join(HERE, "crest-knee-3r-joggle.py")); J = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(J)
V, CB, S = J.V, J.CB, J.S
which, outp = sys.argv[1], sys.argv[2]
FLAT = len(sys.argv) > 3 and sys.argv[3] == "flat"           # control: the verified FLAT cell (row best_params, flat knee)
if FLAT: V.CK.Model = V.CK._FlatModel
M1, P2, fit, ji = V.fit_fast(dict(J.ROW["best_params"]) if FLAT else dict(J.P_JOG))
B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
M = V.worn(M1, P2, B); M.run()
tk = V.taken_list(B); h = S.T_LINK / 2; clr = {}
if FLAT:
    kc, kR, kh = M._boxes_at_final(0)["knee"]; R6, t6 = M.T(6, 0); sl = [(R6.T @ (kc - t6), R6.T @ kR, kh)]   # knee box in body-6 home frame
else: sl = M._knee_slices()
for i in tk:
    R3, t3 = M.T(M.Emid[0], i)
    Em = M.Emid[1] @ R3.T + t3; R6, t6 = M.T(6, i)
    clr[i] = min(float(M.sd_box(Em, R6 @ c + t6, R6 @ Rk, hf).min()) - h for c, Rk, hf in sl)
res0 = list(B.res); out = dict(wear=which, cell="flat" if FLAT else "joggle", taken=len(tk), min_mm=round(min(clr.values()), 3), rows=[])
for d in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5):
    jam = [i for i, v in clr.items() if v < M.ADJ + d]
    B.res = list(res0)
    for i in jam: B.res[i] = None
    r = B.report(); out["rows"].append(dict(strap_level_error_mm=d, jam_poses=len(jam), gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"]))
B.res = res0
json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out))
