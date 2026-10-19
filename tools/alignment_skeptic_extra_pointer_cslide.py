"""Skeptic extras for pointer-cslide (2026-10-19; usage: OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_skeptic_extra_pointer_cslide.py <out_dir>; it also re-writes pointer-cslide_saddle_counterfactual.json in out_dir) (read-only; model unchanged, row best_params, Bench(60,160) fast):
(1) saddle underside steepness vs the kit's K5 60-deg climb limit; (2) the shoe->neck step and a K5-consistent riser
(neck rows raised to the 60-deg climb line from the shoe at s+15) -> in-band14 change on taken clip frames;
(3) the saddle counterfactual re-run (the probe's own cf())."""
import importlib.util, json, math, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"
sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("pc_probe", os.path.join(REPO, "tools", "alignment_wear_probe_pointer_cslide.py"))
W = importlib.util.module_from_spec(sp); sp.loader.exec_module(W)
MOD, K, CB, P = W.MOD, W.K, W.CB, W.P
out_dir = sys.argv[1]
os.environ.pop("CB_EXACT", None)
B = CB.Bench(n_clip=60, n_ws=160); B._kitF = K.frames(B)
rep = MOD.bench_eval(B, P); D = MOD.design(B, P); L = B._kit_last
res = dict(report={k: rep[k] for k in W.KEYS}, rho=D["rho"], T=D["T"], c=D["c"])
# (1) saddle steepness
prof = np.asarray(D["prof"]); ang = np.asarray(D["ang0"])
dax = np.abs(np.diff(prof, axis=0))                                   # axial neighbours, 2 mm apart
dcol = np.abs(np.diff(prof, axis=1)); pitch = np.radians(np.diff(ang)).mean() * (D["rho"] + 2.0)
lim = math.tan(math.radians(60.0))
res["saddle_grid"] = list(prof.shape)
res["saddle_step_axial_mm"] = dict(max=round(float(dax.max()), 2), p95=round(float(np.percentile(dax, 95)), 2),
                                   share_over_60deg=round(float((dax > 2.0 * lim).mean()), 4), limit_mm=round(2.0 * lim, 2))
res["saddle_step_circ_mm"] = dict(pitch_mm=round(float(pitch), 2), max=round(float(dcol.max()), 2), p95=round(float(np.percentile(dcol, 95)), 2),
                                  share_over_60deg=round(float((dcol > pitch * lim).mean()), 4), limit_mm=round(float(pitch * lim), 2))
res["saddle_max_climb_deg"] = dict(axial=round(math.degrees(math.atan(dax.max() / 2.0)), 1), circ=round(math.degrees(math.atan(dcol.max() / pitch)), 1))
# (2) shoe -> neck step and a K5-consistent riser
s, rho = P["s"], D["rho"]
rowsN, angN = MOD.neck_layout(P, rho); RN = np.asarray(D["neck"]).reshape(len(rowsN), len(angN))
res["neck_first_row"] = dict(w=round(float(rowsN[0] - s), 2), radius_mm=dict(min=round(float(RN[0].min()), 2), max=round(float(RN[0].max()), 2)),
                             shoe_radius=round(rho, 2), step_mm=round(float(rho - RN[0].mean()), 2),
                             climb_deg_over_4mm=round(math.degrees(math.atan((rho - RN[0].mean()) / (rowsN[0] - (s + MOD.BAND_W / 2 + 2)))), 1))
RNr = np.maximum(RN, rho - lim * (rowsN - (s + MOD.BAND_W / 2 + 2))[:, None])
res["neck_rows_raised"] = int((RNr > RN + 1e-9).any(1).sum())
F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = MOD.kin(F, P)
tk = L["take"]; Pc = np.array([i for i in np.nonzero(tk)[0] if B.kind[i] == "clip"])
def neck_pts(R):
    e = np.radians(angN); E = np.cos(e)[None, :, None] * E1[Pc][:, None] + np.sin(e)[None, :, None] * E2[Pc][:, None]
    return (rowsN[None, :, None, None] * d3[Pc][:, None, None] + R[None, :, :, None] * E[:, None]).reshape(len(Pc), -1, 3)
Xo, Xr = neck_pts(RN), neck_pts(RNr)
assert np.allclose(Xo, L["pts"]["neck"][Pc], atol=1e-6), "neck points differ from the model's"
m = Xo.shape[1]; idx = np.repeat(Pc, m)
do = K.dist_many(B, idx, Xo.reshape(-1, 3)).reshape(len(Pc), m); dr = K.dist_many(B, idx, Xr.reshape(-1, 3)).reshape(len(Pc), m)
ib = lambda d: (d >= 2.0) & (d <= 14.0)
tot = sum(L["pts"][mm.name].shape[1] for mm in L["chain"].members)
lost = int((ib(do) & ~ib(dr)).sum()); gained = int((~ib(do) & ib(dr)).sum())
res["k5_riser"] = dict(clip_taken=int(len(Pc)), samples_per_pose=int(tot), neck_samples_in_to_out=lost, out_to_in=gained,
                       inband14_delta=round(-(lost - gained) / (tot * len(Pc)), 4),
                       gap_delta_est=round(100 * (lost - gained) / (tot * len(Pc)), 2),
                       neck_inband_before=round(float(ib(do).mean()), 4), neck_inband_after=round(float(ib(dr).mean()), 4))
json.dump(res, open(os.path.join(out_dir, "pointer-cslide_skeptic_extra.json"), "w"), indent=1, default=float)
print(json.dumps(res, default=float))
# (3) the counterfactual, re-run with the probe's own code
MOD._CACHE.clear()
W.counterfactual(out_dir)
