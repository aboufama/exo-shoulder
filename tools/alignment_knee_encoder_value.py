"""Usage: OMP_NUM_THREADS=1 nice python3 tools/<this> <id> bench|held <out.json>  (skeptic, 2026-10-17; read-only on models)
Skeptic: does reading the 2 knee pins (v1) improve the arm estimate over hubs only (v2)? Raw sigma_min of
d(readings)/d(GH rotation) with readings = hubs (J1, J2, J3) vs hubs + pins (J1, J2, J3, qa, qb), and with K read too.
Model unchanged, the auditor's tool's readings(); claim-protocol taken set."""
import json, os, sys
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")); sys.path.insert(0, os.path.join(REPO, "tools"))
import importlib.util
sp = importlib.util.spec_from_file_location("aks", os.path.join(REPO, "tools", "alignment_knee_sensing.py")); AK = importlib.util.module_from_spec(sp); sp.loader.exec_module(AK)
CB = AK.CB; did, wear = sys.argv[1], sys.argv[2]
Mcls, clamp, PARAMS, PK, S = AK.adapter(did)
row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", did + ".json")))
P = clamp(dict(PARAMS, **row["best_params"])); os.environ.pop("CB_EXACT", None)
M1 = Mcls(CB.Bench(n_clip=60, n_ws=160), dict(P)); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
if wear == "held":
    PV = AK._load("pkv", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
else: B = CB.Bench(n_clip=110, n_ws=360)
M = Mcls(B, dict(P2)); D = M.D
fp = os.path.join(REPO, "docs", "alignment", "remeasure", f"{did}_{wear}_perpose_claim.json")
taken = [p["i"] for p in json.load(open(fp))["poses"] if p.get("taken")] if os.path.exists(fp) else [int(i) for i in np.nonzero(M.kin_ok)[0]]
h = 1e-4; E = np.eye(3); res = {k: [] for k in ("hubs", "hubs_pins", "hubs_K", "hubs_K_pins")}; dks = []
kK = float(P2.get("kK", np.nan))
for i in taken:
    Q0 = M.Q[i]; Qs = [Q0] + [AK.rotv(sg * h * E[k]) @ Q0 for k in range(3) for sg in (1, -1)]
    c, ok, aerr, q3 = AK.readings(D, np.stack(Qs)); Zc = np.zeros((6, 3))
    for k in range(3): Zc[:, k] = AK.wrap(c[1 + 2 * k] - c[2 + 2 * k]) / (2 * h)
    for nm, sel in (("hubs", [0, 1, 2]), ("hubs_pins", [0, 1, 2, 4, 5]), ("hubs_K", [0, 1, 2, 3]), ("hubs_K_pins", [0, 1, 2, 3, 4, 5])):
        res[nm].append(float(np.linalg.svd(Zc[sel], compute_uv=False)[-1]))
    dks.append(abs(float(c[0, 3])) > 1e-9)
dks = np.array(dks); out = dict(id=did, wear=wear, n=len(taken), taken_source=os.path.relpath(fp, REPO) if os.path.exists(fp) else "kin_ok", kK=kK,
    one_over_1_plus_kK=round(1 / (1 + kK), 4) if kK == kK else None, forced=int(dks.sum()))
for nm, v in res.items():
    v = np.array(v); out[nm] = dict(min=round(float(v.min()), 4), amp_max=round(float(1 / v.min()), 3), median=round(float(np.median(v)), 4),
        forced_min=round(float(v[dks].min()), 4) if dks.any() else None, unforced_min=round(float(v[~dks].min()), 4) if (~dks).any() else None)
print(json.dumps(out)); json.dump(out, open(sys.argv[3], "w"), indent=1)
