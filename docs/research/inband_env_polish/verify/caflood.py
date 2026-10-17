"""verifier's contact-aware continuity: nodes = grid poses the frozen fit60 shape TAKES worn exact (held + Bench(110,360)
dumps; Bench(60,160)-only grid poses unknown -> excluded (conservative) / included (optimistic)); strict seeds = elevation-0
taken unforced poses; edges = 2-deg slerp, every step closes, passive <= 10 deg, actives <= 25 (the rule's law)"""
import os, sys, json, math, importlib.util
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
os.environ.setdefault("CB_EXACT", "1"); os.environ.setdefault("CB_FOLD_MARGIN", "5.5"); os.environ.setdefault("CB_QUIET_EXACT", "1")
sp = importlib.util.spec_from_file_location("ep_v", REPO + "/tools/inband_env_polish.py"); EP = importlib.util.module_from_spec(sp); sp.loader.exec_module(EP)
import concept_bench as CB
from scipy.spatial.transform import Rotation as Rot, Slerp
which, held_dump, bench_dump, outp = sys.argv[1:5]
P = EP.params_of(which); Pp, _ = EP.priced(P)
FIT = EP._fit_bench("fit60"); r1, M1 = EP._rep(FIT, Pp); D = M1.D; PP = M1.p
Z = CB._poses_all(); names = [str(x) for x in Z["NAMES"]]; allw = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
Qa = Z["HG"][allw].astype(float); q, oka, _, _, X3, s = D.ik(Qa); sta = D._state.copy(); Kn = D.knee(s)
c = (np.einsum("nij,nij->n", X3[0], Qa) - 1) / 2; res = np.degrees(np.arccos(np.clip(c, -1, 1)))
oka = oka & Kn["ok"] & (np.abs(s[:, 2]) <= PP["R_tol"]) & (res < 0.5)
Pz = Z["POSE"][allw].astype(float)
# taken map from the dumps (same fit60 shape)
PV = EP._load("pv_v", REPO + "/docs/concepts/verify/skin-normal-3r-pin-knee-polish.py"); Hb = PV.held_bench(); hidx = np.asarray(Hb.idx)
bidx = CB._select(110, 360)[0]
dh = json.load(open(held_dump))["poses"]; db = json.load(open(bench_dump))["poses"]
assert len(dh) == len(hidx) and len(db) == len(bidx)
tk = {}
for d, ii in ((dh, hidx), (db, bidx)):
    for p in d:
        if p["kind"] == "ws": tk[int(ii[p["i"]])] = bool(p["taken"])
pos = {int(g): k for k, g in enumerate(allw)}
known = np.array([int(g) in tk for g in allw]); tkg = np.array([tk.get(int(g), False) for g in allw])
def edge(Qa_, Qb_, step=2.0, pj=10.0, aj=25.0):
    R2 = Rot.from_matrix(np.stack([Qa_, Qb_])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
    m = max(2, int(math.ceil(ang / step)) + 1); Qs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
    q_, ok_, _, _, _, s_ = D.ik(Qs); dK_ = D._dK; K_ = D.knee(s_); ok_ = ok_ & K_["ok"] & (np.abs(s_[:, 2]) <= PP["R_tol"])
    if not ok_.all(): return False
    qq = np.degrees(np.c_[q_[:, :2], q_[:, 2] + K_["phi"], dK_, K_["qa"], K_["qb"]])
    dq = np.abs(np.degrees(EP.PK.wrap(np.radians(np.diff(qq, axis=0)))))
    return bool((dq[:, 3:] <= pj).all() and (dq[:, :3] <= aj).all())
vals = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]
def flood(node, seeds):
    key = {tuple(np.round(Pz[k, :3], 1)): k for k in range(len(allw)) if node[k]}
    con = np.zeros(len(allw), bool); front = [k for k in range(len(allw)) if node[k] and seeds[k]]
    for k in front: con[k] = True
    while front:
        nxt = []
        for a in front:
            x = tuple(np.round(Pz[a, :3], 1))
            for d in range(3):
                j = vals[d].index(x[d])
                for jj in (j - 1, j + 1):
                    if 0 <= jj < len(vals[d]):
                        y = list(x); y[d] = vals[d][jj]; b = key.get(tuple(y))
                        if b is not None and not con[b] and edge(Qa[a], Qa[b]): con[b] = True; nxt.append(b)
        front = nxt
    return con
out = dict(which=which, grid=len(allw), kin_ok=int(oka.sum()), known=int(known.sum()), taken_known=int((tkg & known).sum()))
el_lo = float(Pz[oka & tkg & (sta == 0), 1].min()); seed_strict = (sta == 0) & (Pz[:, 1] <= el_lo + 1e-6); out["seed_elev"] = el_lo; print("strict seeds: lowest taken unforced elevation row", el_lo, "elev values", sorted(set(np.round(Pz[:, 1], 1)))[:4], flush=True)
for nm, node, seeds in (("kinematic_strict", oka, seed_strict), ("contact_cons_strict", oka & tkg, seed_strict),
                        ("contact_opt_strict", oka & (tkg | ~known), seed_strict), ("contact_cons_unforced", oka & tkg, sta == 0)):
    con = flood(node, seeds)
    tak = tkg & known
    dropped = [int(allw[k]) for k in range(len(allw)) if tak[k] and not con[k]]
    out[nm] = dict(nodes=int(node.sum()), seeds=int((node & seeds).sum()), connected=int(con.sum()), taken_dropped=len(dropped),
                   taken_dropped_held=int(sum(1 for g in dropped if g in set(hidx.tolist()))), dropped_poses=[[round(float(v), 1) for v in Z["POSE"][g, :3]] for g in dropped[:30]])
    print(nm, {k: v for k, v in out[nm].items() if k != "dropped_poses"}, flush=True)
json.dump(out, open(outp, "w"), indent=1)
