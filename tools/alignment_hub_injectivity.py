"""Usage: OMP_NUM_THREADS=1 nice python3 tools/<this> <id> bench|held <out.json>  (skeptic, 2026-10-17; read-only on models)
Skeptic: global (finite) hub-only determinacy over the taken set - beyond the local Jacobian. For every pair of taken
poses compare the hub readings (J1, J2, J3; K from its law) with the arm orientation difference. A pair with nearly equal
hub readings but a large arm difference = a hidden second branch the local sigma_min cannot see. Also: finite encoder-error
amplification (arm deg per hub deg) between neighbouring poses. Model loaded unchanged via the auditor's tool."""
import json, os, sys, math
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.join(REPO, "tools"))
import importlib.util
sp = importlib.util.spec_from_file_location("aks", os.path.join(REPO, "tools", "alignment_knee_sensing.py")); AK = importlib.util.module_from_spec(sp); sp.loader.exec_module(AK)
CB = AK.CB
did, wear = sys.argv[1], sys.argv[2]
Mcls, clamp, PARAMS, PK, S = AK.adapter(did)
row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", did + ".json")))
P = clamp(dict(PARAMS, **row["best_params"]))
old = os.environ.pop("CB_EXACT", None)
B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = Mcls(B1, dict(P)); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
if wear == "held":
    PV = AK._load("pkv", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
else:
    B = CB.Bench(n_clip=110, n_ws=360)
M = Mcls(B, dict(P2)); D = M.D
fp = os.path.join(REPO, "docs", "alignment", "remeasure", f"{did}_{wear}_perpose_claim.json")
taken = [p["i"] for p in json.load(open(fp))["poses"] if p.get("taken")]
Q = np.stack([M.Q[i] for i in taken])
c, ok, aerr, q3 = AK.readings(D, Q)
hub = np.degrees(c[:, :3]); kneeang = np.asarray(AK.readings.ang, float)
n = len(taken)
dh = np.abs(hub[:, None, :] - hub[None, :, :]); dh = np.minimum(dh, 360 - dh); dhub = dh.max(-1); dh2 = np.sqrt((dh**2).sum(-1))
R = np.einsum("aij,bkj->abik", Q, Q); tr = np.clip((np.einsum("abii->ab", R) - 1) / 2, -1, 1); darm = np.degrees(np.arccos(tr))
iu = np.triu_indices(n, 1)
dhv, dav, dh2v = dhub[iu], darm[iu], dh2[iu]
out = dict(id=did, wear=wear, n_taken=n, all_ok=bool(ok.all()), taken_source=os.path.relpath(fp, REPO))
for thr in (5.0, 10.0, 20.0):
    sel = dav > thr
    j = int(np.argmin(dhv[sel])); a, b = iu[0][sel][j], iu[1][sel][j]
    out[f"min_hub_diff_deg_for_arm_diff_gt_{int(thr)}"] = dict(hub_diff=round(float(dhv[sel][j]), 3), arm_diff=round(float(dav[sel][j]), 2),
        poses=[{k: round(B.poses[taken[x]][k], 1) for k in ("plane", "elev", "axial")} for x in (a, b)], knee=[round(float(kneeang[a]), 1), round(float(kneeang[b]), 1)])
# finite amplification between near neighbours (arm diff < 15 deg): arm / hub (max-norm) ratio
sel = (dav > 0.5) & (dav < 15)
ratio = dav[sel] / np.maximum(dhv[sel], 1e-9)
j = int(np.argmax(ratio)); a, b = iu[0][sel][j], iu[1][sel][j]
out["finite_amp_arm_per_hub_deg"] = dict(max=round(float(ratio.max()), 3), p99=round(float(np.percentile(ratio, 99)), 3), median=round(float(np.median(ratio)), 3), n_pairs=int(sel.sum()),
    worst=[{k: round(B.poses[taken[x]][k], 1) for k in ("plane", "elev", "axial")} for x in (a, b)], worst_arm_hub=[round(float(dav[sel][j]), 2), round(float(dhv[sel][j]), 3)])
for thr in (5.0, 10.0, 20.0):
    sel = dav > thr; j = int(np.argmin(dh2v[sel])); a, b = iu[0][sel][j], iu[1][sel][j]
    out[f"min_hub_diff2_deg_for_arm_diff_gt_{int(thr)}"] = dict(hub_diff2=round(float(dh2v[sel][j]), 3), arm_diff=round(float(dav[sel][j]), 2), poses=[{k: round(B.poses[taken[x]][k], 1) for k in ("plane", "elev", "axial")} for x in (a, b)])
sel = (dav > 0.5) & (dav < 15); r2 = dav[sel] / np.maximum(dh2v[sel], 1e-9)
out["finite_amp2_arm_per_hub_deg"] = dict(max=round(float(r2.max()), 3), p99=round(float(np.percentile(r2, 99)), 3), median=round(float(np.median(r2)), 3))
sel = dav > 0.5; r3 = dav[sel] / np.maximum(dh2v[sel], 1e-9)
out["global_amp2_arm_per_hub_deg_all_pairs"] = dict(max=round(float(r3.max()), 3), p999=round(float(np.percentile(r3, 99.9)), 3))
print(json.dumps(out))
json.dump(out, open(sys.argv[3], "w"), indent=1)
