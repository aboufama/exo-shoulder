# run from the repo root: OMP_NUM_THREADS=1 python3 docs/research/crossfit/kin_closure_diag.py  (writes kin_closure_diag.json)
"""kinematic closure (fold window + knee + closure, the flood fill's node law) of configs on: Bench(110,360) ws, the pool ws,
the held-out ws, and a FRESH jittered sample of the workspace envelope (each grid cell's pose +- U(7.5 deg) per coordinate, seed 7;
no grid pose reused); plus the knee reference m from a Bench(60,160) fit (kinematics only)"""
import sys, os, json, numpy as np
sys.path.insert(0, "tools"); import crossfit_polish as X, concept_bench as CB
os.chdir("pipeline/avg"); sys.path.insert(0, "."); import design_search as D; os.chdir("../..")
Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; ws = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
b110 = set(CB._select(110, 360)[0].tolist()); used = b110 | set(CB._select(60, 160)[0].tolist())
inb = np.array([g in b110 for g in ws]); inp = np.array([g in used for g in ws])
G = X._ws_grid(); POSE = G["POSE"]
def hg(pl, el, ax):
    H = D.Ry(pl * D.D2R) @ D.Rx(-el * D.D2R) @ D.Ry(ax * D.D2R); Rs = D.scapula(el); return Rs.T @ H
err = max(np.abs(hg(*POSE[i, :3]) - G["HG"][i]).max() for i in range(0, len(POSE), 97)); print("HG rebuild max err", round(float(err), 5))
rng = np.random.default_rng(7); J = []
for rep in range(4):
    for p in POSE:
        q = p[:3] + rng.uniform(-7.5, 7.5, 3); q[1] = np.clip(q[1], 0, 170); J.append(hg(*q))
J = np.array(J)
pl = X.KneePlugin(); B = CB.Bench(60, 160); refs = json.load(open("docs/research/crossfit/refs.json"))
for lab in ("XP1", "XP2", "XP3"):
    refs[lab] = json.load(open(f"docs/research/crossfit/pick_{lab}.json"))["params"]
out = {}
for nm, p in refs.items():
    P = pl.full(p); pl.prep(P); M = pl.MK.Model(B, pl.model_params(P)); k = pl.kin(M)
    ok = k(G["HG"])[0]; okj = k(J)[0]
    out[nm] = dict(b110=round(float(ok[inb].mean()), 4), pool=round(float(ok[inp].mean()), 4), held=round(float(ok[~inp].mean()), 4), grid=round(float(ok.mean()), 4), fresh=round(float(okj.mean()), 4))
    print(nm, out[nm], flush=True)
json.dump(out, open("docs/research/crossfit/kin_closure_diag.json", "w"), indent=1)
