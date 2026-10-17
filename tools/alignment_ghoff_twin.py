"""Alignment skeptic re-measure (2026-10-17, prints JSON; writes nothing): the twin's GH-offset harness (kneeless-roller-knuckle-3r.py redteam_gh, copied verbatim in logic)
applied to kneeless-sidecar-knuckle-3r's best_params, so the within-liner shares are apples to apples with the twin's
remeasure/kneeless-roller-knuckle-3r_ghoffset.json. Models unchanged; nothing in the repo is written."""
import importlib.util, json, os, sys
import numpy as np

REPO = "/home/user/exo-shoulder"
MD = os.path.join(REPO, "docs", "concepts", "models")
sys.path.insert(0, os.path.join(REPO, "tools"))


def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KS = load("ksk_model_skeptic", os.path.join(MD, "kneeless-sidecar-knuckle-3r.py"))
CB = KS.CB
row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "kneeless-sidecar-knuckle-3r.json")))
par = row["best_params"]
D = KS.KLDesign(KS._clamp(dict(KS.PARAMS, **par))); u3 = np.asarray(D.u[2], float)
OSN = load("osn_for_skeptic", os.path.join(MD, "offset-skin-normal-3r.py")); Q0 = OSN.rest()["Q0"]
out = {"u3": [round(float(x), 4) for x in u3]}
for nc, nw, tag in ((110, 360, "claim_bench"), (60, 160, "fit_bench")):
    Z = CB._poses_all(); B = CB.Bench(n_clip=nc, n_ws=nw); Q = Z["HG"][B.idx].astype(float)
    dirs = np.array([[x, y, z] for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)], float)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    Rr = np.einsum("nij,kj->nik", Q, Q0)
    ax_arm = np.array([0.0, -1.0, 0.0])
    res = {}
    for mg in (3.0, 5.0):
        mis = np.einsum("nij,kj->nki", np.eye(3)[None] - Rr, dirs * mg)
        mag = np.linalg.norm(mis, axis=2); worst = mag.max(1)
        armf = np.einsum("nji,nkj->nki", Q, mis)
        perp = armf - (armf @ ax_arm)[..., None] * ax_arm; wp = np.linalg.norm(perp, axis=2).max(1)
        kn = np.abs(armf @ u3).max(1)
        res[f"{mg:g}mm"] = dict(within_liner=round(float((worst <= 3.0).mean()), 3), median=round(float(np.median(worst)), 2),
                                p90=round(float(np.percentile(worst, 90)), 2), max=round(float(worst.max()), 2),
                                slide_within_liner=round(float((wp <= 3.0).mean()), 3),
                                knee_equiv_within_liner=round(float((kn <= 3.0).mean()), 3), knee_equiv_median=round(float(np.median(kn)), 2),
                                knee_equiv_max=round(float(kn.max()), 2))
    res["n_poses"] = int(len(Q)); out[tag] = res
print(json.dumps(out))
