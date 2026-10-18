"""Skeptic re-run of the crest-knee-3r continuity flood (verifier code unchanged, imported) with two seedings:
(a) the verifier's (every kin-ok elevation-0 node seeded connected, no edge tested among them);
(b) strict: ONE rest seed (the kin-ok elev-0 node nearest identity), every edge tested incl. the elev-0 ring.
Then which bench / held taken ws poses each drops."""
import importlib.util, json, math, os, sys
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("ckv", os.path.join(REPO, "docs/concepts/verify/crest-knee-3r.py")); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
CB = V.CB
P = dict(V.ROW["best_params"]); M1, P2, fit, ji = V.fit_fast(P)
D = V.PK.Design(dict(P2)); D.m = np.array(P2["m_fix"], float); D.m[2] = 0.0
R_tol = float(P2["R_tol"]); win = P2.get("j3win")
Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
ok, qq, sgn = V.kin(D, HG, R_tol, win)
key = {(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)}
vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]
def nbrs(i):
    x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
    for d in range(3):
        j = vals[d].index(x[d])
        for jj in (j - 1, j + 1):
            if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1
            if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
            if 0 <= jj < len(vals[d]):
                y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                if t is not None: yield t
    if x[2] in (180.0, -180.0):
        t = key.get((x[0], x[1], -x[2]))
        if t is not None: yield t
def edge(a, b):
    R0, R1 = Rot.from_matrix(HG[a]), Rot.from_matrix(HG[b]); angd = np.degrees((R0.inv() * R1).magnitude())
    n = max(2, int(math.ceil(angd / V.STEP)) + 1); Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
    o, q, sg = V.kin(D, Qs, R_tol, win)
    if not o.all(): return False
    d = np.abs((np.diff(q, axis=0) + 180) % 360 - 180)
    if d.max() > V.JUMP: return False
    if len(set(sg.tolist())) > 1: return False
    return True
def flood(seeds):
    conn = np.zeros(len(W), bool); conn[seeds] = True; front = list(seeds)
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if ok[b] and not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    return conn
elev = POSE[:, 1]
e0 = [i for i in range(len(W)) if elev[i] == 0]; s_all = [i for i in e0 if ok[i]]
ang = [Rot.from_matrix(HG[i]).magnitude() for i in s_all]; s1 = s_all[int(np.argmin(ang))]
out = dict(n_grid=len(W), kin_ok=int(ok.sum()), elev0_nodes=len(e0), elev0_ok=len(s_all), elev0_sgn=sorted(set(int(sgn[i]) for i in s_all)),
           elev0_sgn_counts={str(s): int(sum(1 for i in s_all if sgn[i] == s)) for s in set(sgn[s_all].tolist())},
           elev0_not_ok=[dict(plane=float(POSE[i,0]), axial=float(POSE[i,2])) for i in e0 if not ok[i]][:40],
           strict_seed=dict(plane=float(POSE[s1,0]), elev=float(POSE[s1,1]), axial=float(POSE[s1,2]), sgn=int(sgn[s1])))
cA = flood(s_all); cB = flood([s1])
out["verifier_seeding"] = dict(connected=int(cA.sum()), islands=int((ok & ~cA).sum()))
out["strict_one_seed"] = dict(connected=int(cB.sum()), islands=int((ok & ~cB).sum()),
                              lost=[dict(plane=float(POSE[i,0]), elev=float(POSE[i,1]), axial=float(POSE[i,2]), sgn=int(sgn[i])) for i in np.nonzero(cA & ~cB)[0]][:60])
# which taken bench / held ws poses drop under the strict seeding (per-pose dumps on file)
import alignment_paired as AP
wpos = {int(g): k for k, g in enumerate(W)}
for wear in ("bench", "held"):
    B = CB.Bench(n_clip=110, n_ws=360) if wear == "bench" else V.held_bench()
    dp = json.load(open(os.path.join(REPO, f"docs/alignment/remeasure/crest-knee-3r_{wear}_perpose.json")))
    poses = dp["poses"]; drop = []
    for row in poses:
        if row["kind"] == "ws" and row["taken"]:
            k = wpos.get(int(B.idx[row["i"]]))
            if k is None or not cB[k]: drop.append(row["i"])
    for row in poses:
        if row["i"] in drop: row.update(taken=False, ev=False, contact=False, min_mm=None)
    out[wear] = dict(static=dp["recomputed"], strict_connected=AP.gap_parts(poses), dropped=len(drop),
                     dropped_poses=[dict(plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for i in drop][:40])
json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ("elev0_not_ok",)}, default=float)[:3000])
