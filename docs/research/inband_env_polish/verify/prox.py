import sys, os, json, importlib.util
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
import concept_bench as CB
Z0 = CB._poses_all(); names = [str(x) for x in Z0["NAMES"]]; cid = Z0["CID"]
# held-out set rebuilt from scratch (verifier definition)
used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
cl = [i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in used]; ws = [i for i in np.nonzero(cid == ws_id)[0] if i not in used]
hidx = np.array(cl + ws); print("held", len(hidx), "clip", len(cl), "ws", len(ws))
E = np.load(REPO + "/docs/research/minarc_final_polish/env_poses.npz")
HP = Z0["POSE"][hidx, :3].astype(float); HT = np.einsum("nij,njk->nik", Z0["RS"][hidx].astype(float), Z0["HG"][hidx].astype(float))
wrap = lambda a: (np.asarray(a) + 180) % 360 - 180
out = {}
for nm in ("env", "envsel"):
    P = E[nm + "_POSE"][:, :3].astype(float); T = np.einsum("nij,njk->nik", E[nm + "_RS"].astype(float), E[nm + "_HG"].astype(float))
    dc = np.array([np.abs(np.c_[HP[:, 0] - p[0], HP[:, 1] - p[1], wrap(HP[:, 2] - p[2])]).max(1).min() for p in P])
    tr = np.einsum("aij,bij->ab", T, HT); dg = np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1))).min(1)
    # exact reuse check: identical pose rows in the archive's held set
    exact = int(sum(1 for p in P if (np.abs(HP - p).max(1) < 1e-6).any()))
    out[nm] = dict(n=len(P), min_cheb=round(float(dc.min()), 3), n_cheb_lt2=int((dc < 2).sum()), min_geo=round(float(dg.min()), 3), n_geo_lt2=int((dg < 2).sum()),
                   median_geo=round(float(np.median(dg)), 2), exact_reuse=exact, ax_ge150=round(float(np.mean(np.abs(P[:, 2]) >= 150)), 4))
# the env bench's clip frames = Bench(110,360)'s first 110 (same as the verified bench); none held out by construction
c110 = CB._select(110, 360)[0][:110]; print("clip frames in held:", len(set(c110.tolist()) & set(hidx.tolist())))
print("held ws |axial|>=150:", round(float(np.mean(np.abs(Z0["POSE"][np.array(ws), 2]) >= 150)), 4))
print(json.dumps(out, indent=1))
