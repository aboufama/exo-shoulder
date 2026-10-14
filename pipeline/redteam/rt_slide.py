"""Constructive counter-test for attack 2: the DOF cap allows "3 joints + a sliding cuff". A cuff that slides along the
humerus absorbs the part of the GH misalignment that lies ALONG the humerus axis, so only the perpendicular part
P_perp(t) (A(t) x - y(t)) is left. Minimax over the axis points x (same 26-direction LP as girdle.fit_minimax, on the
projected rows), fitted on the 6 fit clips, evaluated on all 8 clips and on the plausible workspace; slide travel needed
= range of the along-humerus component. Spherical 4R + slide (x = 0) for comparison. Laws: rig, the lead's literature
law; shrug +15 / depression -10 mm evaluated with the rig-law axis points.
    python3 rt_slide.py -> results/slide.json
"""
import numpy as np
from scipy.optimize import linprog
import rt_common as RC
from rt_common import GD

FR = RC.clips(); names = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float); FIT = ~np.isin(names, RC.HOLD_OUT)
S = GD.Motion(WANT[:1]).S
def rig(P): P = np.atleast_2d(P); return np.c_[np.zeros(len(P)), 0.2 * S * np.maximum(0, P[:, 1] - 30), np.zeros(len(P))]
LAWS = {"rig": rig, "literature (lead's girdle.lift_literature)": GD.lift_literature}
pl_g = np.arange(-90, 151, 10.0); el_g = np.arange(0, 171, 10.0); r_g = np.arange(-90, 91, 30.0)
PL, EL, RR = [a.ravel() for a in np.meshgrid(pl_g, el_g, r_g, indexing="ij")]; m = RC.plausible(PL, EL)
GP = np.c_[PL, EL, RR - PL, np.full(len(PL), 90.0), np.zeros(len(PL))][m]

def perp(M): h = M.hdir; return np.eye(3)[None] - h[:, :, None] * h[:, None, :]          # (T,3,3)
def fit_perp(A, y, Pp, coax):
    A2 = A[:, :, :6] if coax else A; n = A2.shape[2]; G = np.einsum("dk,tkj,tjn->tdn", GD.DIRS, Pp, A2).reshape(-1, n); h = np.einsum("dk,tkj,tj->td", GD.DIRS, Pp, y).reshape(-1)
    r = linprog(np.r_[np.zeros(n), 1.0], A_ub=np.c_[G, -np.ones(len(G))], b_ub=h, bounds=[(-60, 60)] * n + [(0, None)], method="highs")
    x = r.x[:n] if r.success else np.zeros(n); return np.r_[x, np.zeros(3)] if coax else x
def res_perp(A, x, y, Pp): e = np.einsum("tij,j->ti", A, x) - y; return np.linalg.norm(np.einsum("tij,tj->ti", Pp, e), axis=1)
def along(A, x, y, M): e = y - np.einsum("tij,j->ti", A, x); return (e * M.hdir).sum(1)

out = {}
for lab, fn in LAWS.items():
    M = GD.Motion(WANT, lift_fn=fn); MF = GD.Motion(WANT[FIT], lift_fn=fn); MW = GD.Motion(GP, lift_fn=fn); o = {}
    Pp, PpF, PpW = perp(M), perp(MF), perp(MW)
    r0 = np.linalg.norm(np.einsum("tij,tj->ti", Pp, M.lift), axis=1); o["spherical 4R + slide (x = 0)"] = dict(clips_max=round(float(r0.max()), 2), slide_range_mm=round(float(np.ptp((M.lift * M.hdir).sum(1))), 1))
    for tag, c in RC.load_candidates().items():
        ch = GD.Chain3(c["prm"]); A, *_ = ch.kin(M); AF, *_ = ch.kin(MF); AW, mgw, okw, *_ = ch.kin(MW)
        x = fit_perp(AF, MF.lift, PpF, ch.coax); rc = res_perp(A, x, M.lift, Pp); rw = res_perp(AW, x, MW.lift, PpW)[okw]
        xw = fit_perp(AW[okw], MW.lift[okw], PpW[okw], ch.coax); rww = res_perp(AW[okw], xw, MW.lift[okw], PpW[okw])
        sh = res_perp(A, x, M.lift + [0, 15.0, 0], Pp); dp = res_perp(A, x, M.lift - [0, 10.0, 0], Pp)
        o[f"{tag} + slide"] = dict(shrug15_clips_max=round(float(sh.max()), 2), depressed10_clips_max=round(float(dp.max()), 2), clips_max=round(float(rc.max()), 2), clips_heldout_max=round(float(rc[~FIT].max()), 2), workspace_max=round(float(rw.max()), 2),
                                   workspace_p95=round(float(np.percentile(rw, 95)), 2), workspace_refit_max=round(float(rww.max()), 2),
                                   slide_range_mm=round(float(np.ptp(along(A, x, M.lift, M))), 1))
    out[lab] = o; print(lab); [print("   ", k, v) for k, v in o.items()]
RC.jdump(out, "slide.json")
