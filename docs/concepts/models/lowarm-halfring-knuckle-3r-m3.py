"""Red team M3 for lowarm-halfring-knuckle-3r cell B: the LIFTED link 2 (underside + top copy, outside hub 2's O20 + 1.5)
vs every crank (member 9) sample set (boss, long arm, short arm, pin, tip plate) and vs link 1b / hub K, per pose, on the
frozen shape worn on Bench(110,360) (taken flags from the verifier's per-pose dump). Clearance = nearest sample distance
minus half the crank arm width where the crank set is a mid-line (reported raw too).
usage: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-halfring-knuckle-3r-m3.py <out.json>"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
V = _load("lowarm_v_for_m3", os.path.join(REPO, "docs/concepts/verify/lowarm-halfring-knuckle-3r.py"))
LM, DS, S = V.LM, V.DS, V.S
import concept_bench as CB
unit = S.unit
t0 = time.time()
P = DS._clamp(dict(DS.PARAMS, **dict(LM.CELL_B, **V.BEST)))
old = os.environ.pop("CB_EXACT", None)
try: B1 = CB.Bench(n_clip=60, n_ws=160)
finally:
    if old is not None: os.environ["CB_EXACT"] = old
M1 = DS.DSModel(B1, dict(P)); r1 = M1.run()
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
class Frozen(DS.DSModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_desmo"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))
        self._sc = None
        self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        self._truncate()
dump = json.load(open(os.path.join(REPO, "docs/alignment/remeasure/lowarm-halfring-knuckle-3r_bench_perpose.json")))
taken = [p["i"] for p in dump["poses"] if p["taken"]]
B = CB.Bench(n_clip=110, n_ws=360)
M = Frozen(B, dict(P2))
try:
    M.fit(); mode = "fit-only"
    _ = M.T(9, taken[0])
except Exception as e:
    M = Frozen(B, dict(P2)); M.run(); mode = "run (%s)" % repr(e)[:80]
m2, X2 = M.link_pts["L2"]
c2, ax2 = M.cyl["hub2"][1], M.cyl["hub2"][2]
w = X2 - c2; rr = np.linalg.norm(w - np.outer(w @ ax2, ax2), axis=1)
lift = getattr(M1, "_l2_lift_info", None)
sets = {}
for nm, X in (("L2_out", X2[rr > S.HUB_R + 1.5]), ("L2_all", X2)):
    sets[nm] = np.concatenate([X, X + S.T_LINK * unit(X)])
crank = [X for m, X in M.contact if m == 9] + [X for k, (m, X) in M.rigid.items() if m == 9] + [X for k, (m, X) in M.strap.items() if m == 9]
C9 = np.concatenate(crank)
L1b = M.link_pts["L1b"]; L1bX = np.concatenate([L1b[1], L1b[1] + S.T_LINK * unit(L1b[1])])
res = []
for i in taken:
    R9, t9 = M.T(9, i); R2, t2 = M.T(m2, i); Rb, tb = M.T(L1b[0], i)
    Cw = C9 @ R9.T + t9; tr2 = cKDTree(sets["L2_out"] @ R2.T + t2); tr2a = cKDTree(sets["L2_all"] @ R2.T + t2)
    d_out = float(tr2.query(Cw)[0].min()); d_all = float(tr2a.query(Cw)[0].min())
    Lb = L1bX @ Rb.T + tb; d_b = float(tr2.query(Lb)[0].min())
    res.append((i, d_out, d_all, d_b, abs(math.degrees(float(M.dK[i])))))
a = np.array([r[1] for r in res]); b = np.array([r[3] for r in res])
lo = sorted(res, key=lambda r: r[1])[:6]
cl = M.l2_check(taken)
out = dict(l2_check_reproduced_min=round(float(np.min(cl)), 2), mode=mode, n_taken=len(taken), lift=lift, n_crank_samples=int(len(C9)), n_L2_out=int(len(sets["L2_out"]) // 2),
           L2out_vs_crank_min_mm=round(float(a.min()), 3), L2out_vs_crank_p5=round(float(np.percentile(a, 5)), 3),
           L2all_vs_crank_min_mm=round(min(r[2] for r in res), 3),
           L2out_vs_L1b_min_mm=round(float(b.min()), 3),
           lowest=[dict(i=r[0], kind=B.kind[r[0]], **{k: B.poses[r[0]][k] for k in ("plane", "elev", "axial")}, L2out_crank=round(r[1], 3),
                        L2all_crank=round(r[2], 3), L2out_L1b=round(r[3], 3), dK=round(r[4], 2)) for r in lo],
           note="nearest-sample distances between surface sample clouds (link 2 underside + T_LINK top copy; crank contact/rigid/strap sets); "
                "the crank arm sets are mid-lines or surfaces as the model samples them; non-adjacent rule 1 mm",
           secs=round(time.time() - t0, 1))
json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != "note"}, default=float))
