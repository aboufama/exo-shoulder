"""Tolerance probe for the isoceles-shortdyad-pinknee-3r joggle claim (verifier red team, 2026-10-19): the joggled knee
link rides over the E strap near pin a (adjacent rule 0.15 mm; the verified bench minimum is 0.25 mm). Count the taken
poses whose knee-vs-E-strap clearance (every joggle slice, no exemption) is below 0.15 + d for strap-level errors d, and
the frozen gap if those poses jam. Same harness and claimed parameters as docs/concepts/verify/isoceles-shortdyad-pinknee-3r.py.
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/isoceles-shortdyad-pinknee-3r_tolprobe.py <bench|held> <out.json>"""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("iso_v", os.path.join(HERE, "isoceles-shortdyad-pinknee-3r.py")); I = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(I)
V, CB, S = I.V, I.CB, I.S
which, outp = sys.argv[1], sys.argv[2]
M1, P2, fit, ji = V.fit_fast(dict(I.P))
B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
M = V.worn(M1, P2, B); M.run()
tk = V.taken_list(B); h = S.T_LINK / 2; clr = {}
sl = M._knee_slices()
for i in tk:
    R3, t3 = M.T(M.Emid[0], i)
    Em = M.Emid[1] @ R3.T + t3; R6, t6 = M.T(6, i)
    clr[i] = min(float(M.sd_box(Em, R6 @ c + t6, R6 @ Rk, hf).min()) - h for c, Rk, hf in sl)
res0 = list(B.res); out = dict(wear=which, cell="joggle", taken=len(tk), min_mm=round(min(clr.values()), 3), rows=[])
for d in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0):
    jam = [i for i, v in clr.items() if v < M.ADJ + d]
    B.res = list(res0)
    for i in jam: B.res[i] = None
    r = B.report(); out["rows"].append(dict(strap_level_error_mm=d, jam_poses=len(jam), gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"]))
B.res = res0
json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out))
