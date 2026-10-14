"""ATTACK 1 - where does each chain jam? Jacobian conditioning of the reference 4R and the lead's two 3-DOF candidates along
every clip frame and over the whole everyday workspace (not just the 8 clips).

Spherical chains: angular velocity = sum_i qdot_i * axis_i, so the orientation Jacobian is the 3xN matrix of unit joint axes.
  sigma = its smallest singular value (0 = singular; the worst-direction joint rate is |omega| / sigma)
  margin = the lead's angle measure (girdle.Chain3.kin): deg from the inner joint's straight/folded configuration
  4R: sigma of [J1 J2 J3 J4] at the best spare angle q (4 deg grid) among closing configurations; also with J1 locked
      (sigma of [J2 J3 J4]) since the clip DP limits the spare joint to 6 deg/frame
Workspace: plane -90..150, elev 0..170, r = axial + plane (humeral rotation about the twist-free neutral) -90..90, 5 deg
grid; 'plausible' = rt_common.plausible() (rough active ROM). Reference 4R evaluated scapula-fixed (as the pipeline
models it) and thorax-fixed (the physical back plate).
    python3 rt_jam.py  -> results/jam.json
"""
import math, time
import numpy as np
import rt_common as RC
from rt_common import GD, BP, D2R

t0 = time.time(); FR = RC.clips(); names = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float)
P = np.array([f[3] for f in FR], float); HELD = np.array([f[4] for f in FR]); QF = np.radians([f[6] for f in FR])
ref = RC.Ref4R(); CANDS = RC.load_candidates(); OUT = dict(candidates={k: dict(params=v["prm"], x_source=v["x_source"], key=v["key"]) for k, v in CANDS.items()})
QS = np.radians(np.arange(0, 360, 4.0))


def best_over_q(Hg):
    """per pose: best sigma (closing), best sigma (valid at SING), closes, valid, best min-margin"""
    o = ref.configs(Hg, QS); mm = np.minimum(o["m2"], o["m3"])
    s_cl = np.where(o["closes"], o["sv"], -1).max(1); s_va = np.where(o["valid"], o["sv"], -1).max(1)
    s3 = np.where(o["closes"], o["sv3"], -1).max(1); mg = np.where(o["closes"], mm, -90).max(1)
    return dict(sv=s_cl, sv_valid=s_va, sv3=s3, closes=o["closes"].any(1), valid=o["valid"].any(1), margin=mg)


# ------------------------------------------------------------------ 1. clip frames
Hg_p = np.array([BP.scap(p[1]).T @ GD.Rh_of(*p[:3]) for p in P])
act = [ref.configs(Hg_p[i:i + 1], QF[i:i + 1]) for i in range(len(P))]
a_sv = np.array([o["sv"][0, 0] for o in act]); a_sv3 = np.array([o["sv3"][0, 0] for o in act]); a_mg = np.array([min(o["m2"][0, 0], o["m3"][0, 0]) for o in act])
SING_USED = float(np.floor(a_mg[~HELD].min())); ref.SING = SING_USED          # the margin the clip generator actually allowed
Hg_w = np.array([BP.scap(w[1]).T @ GD.Rh_of(*w[:3]) for w in WANT]); Hth_w = np.array([GD.Rh_of(*w[:3]) for w in WANT])
bw = best_over_q(Hg_w); bt = best_over_q(Hth_w)
clipres = {}
for n in dict.fromkeys(names):
    m = names == n; k_act = np.flatnonzero(m)[np.argmin(a_sv[m])]; k_w = np.flatnonzero(m)[np.argmin(bw["sv"][m])]
    clipres[n] = dict(ref4R_actual_q=dict(sigma_min=round(float(a_sv[m].min()), 3), sigma_J1locked_min=round(float(a_sv3[m].min()), 3),
                                          inner_margin_min_deg=round(float(a_mg[m].min()), 1), at=[int(FR[k_act][1]), [round(v) for v in P[k_act][:3]]]),
                      ref4R_best_q_want=dict(sigma_min=round(float(bw["sv"][m].min()), 3), no_valid_closure_frames=int((~bw["valid"][m]).sum()),
                                             at=[int(FR[k_w][1]), [round(v) for v in WANT[k_w][:3]]]),
                      ref4R_thorax_best_q_want=dict(sigma_min=round(float(bt["sv"][m].min()), 3), no_valid_closure_frames=int((~bt["valid"][m]).sum()), no_closure_frames=int((~bt["closes"][m]).sum())))
M_all = GD.Motion(WANT)
for tag, c in CANDS.items():
    ch = GD.Chain3(c["prm"]); r = RC.chain3_metrics(ch, M_all)
    for n in clipres:
        m = names == n; k = np.flatnonzero(m)[np.argmin(r["margin"][m])]
        clipres[n][tag] = dict(margin_min_deg=round(float(r["margin"][m].min()), 1), sigma_min=round(float(r["sv"][m].min()), 3), closes=round(float(r["ok"][m].mean()), 3),
                               at=[int(FR[k][1]), [round(v) for v in WANT[k][:3]]])
    fit = ~np.isin(names, RC.HOLD_OUT)
    OUT.setdefault("clip_summary", {})[tag] = dict(margin_fit_min=round(float(r["margin"][fit].min()), 1), margin_heldout_min=round(float(r["margin"][~fit].min()), 1),
                                                   sigma_fit_min=round(float(r["sv"][fit].min()), 3), sigma_heldout_min=round(float(r["sv"][~fit].min()), 3))
OUT["clip_summary"]["ref4R"] = dict(sing_margin_used_by_clip_generator_deg=SING_USED, sigma_min_actual_followed=round(float(a_sv[~HELD].min()), 3),
                                    sigma_J1locked_min_followed=round(float(a_sv3[~HELD].min()), 3), inner_margin_min_followed=round(float(a_mg[~HELD].min()), 1),
                                    want_frames_without_valid_closure_scapula_base=int((~bw["valid"]).sum()), want_frames_without_valid_closure_thorax_base=int((~bt["valid"]).sum()),
                                    want_frames_without_any_closure_thorax_base=int((~bt["closes"]).sum()), frames=len(FR))
OUT["clips"] = clipres
print("clip frames done", f"{time.time() - t0:.0f}s", flush=True)

# ------------------------------------------------------------------ 2. workspace
pl_g = np.arange(-90, 151, 5.0); el_g = np.arange(0, 171, 5.0); r_g = np.arange(-90, 91, 5.0)
PL, EL, RR = np.meshgrid(pl_g, el_g, r_g, indexing="ij"); PL, EL, RR = PL.ravel(), EL.ravel(), RR.ravel(); AX = RR - PL
PLAUS = RC.plausible(PL, EL); G = np.c_[PL, EL, AX]; NG = len(G)
RH = np.array([GD.Rh_of(*g) for g in G]); print(NG, "workspace poses,", int(PLAUS.sum()), "plausible", flush=True)
WS = {}
for tag, c in CANDS.items():
    ch = GD.Chain3(c["prm"]); r = ch.kin(type("M", (), dict(RH=RH))())                 # kin only needs M.RH
    W = RH @ ch.w; J = np.stack([np.broadcast_to(ch.b, W.shape), ch.c, W], -1)
    sv = np.sqrt(np.clip(np.linalg.eigvalsh(J @ np.swapaxes(J, -1, -2))[:, 0], 0, None))
    WS[tag] = dict(margin=r[1], sv=np.where(r[2], sv, 0.0), closes=r[2])
for base, Rs_of in (("ref4R_scapula", lambda e: BP.scap(e)), ("ref4R_thorax", lambda e: np.eye(3))):
    sv = np.zeros(NG); sv3 = np.zeros(NG); cl = np.zeros(NG, bool); va = np.zeros(NG, bool); mg = np.zeros(NG)
    for e in el_g:
        m = EL == e; Hg = np.einsum("ji,pjk->pik", Rs_of(e), RH[m]); o = best_over_q(Hg)
        sv[m], sv3[m], cl[m], va[m], mg[m] = np.maximum(o["sv"], 0), np.maximum(o["sv3"], 0), o["closes"], o["valid"], o["margin"]
    WS[base] = dict(sv=sv, sv3=sv3, closes=cl, valid=va, margin=mg)
print("workspace done", f"{time.time() - t0:.0f}s", flush=True)


def worst_poses(score, mask, k=6, sep=25.0):
    """k lowest-score poses inside mask, at least sep deg apart in (plane, elev, r)"""
    idx = np.flatnonzero(mask); idx = idx[np.argsort(score[idx])]; picked = []
    for i in idx:
        if all(np.abs(np.r_[PL[i], EL[i], RR[i]] - np.r_[PL[j], EL[j], RR[j]]).max() >= sep for j in picked): picked.append(i)
        if len(picked) >= k: break
    return [dict(plane=float(PL[i]), elev=float(EL[i]), axial=float(AX[i]), r_rel=float(RR[i]), score=round(float(score[i]), 3),
                 hand_mm=[round(v) for v in RC.hand_pos(PL[i], EL[i], AX[i])], task=RC.task_label(PL[i], EL[i], AX[i])) for i in picked]


wsout = {}
for tag, d in WS.items():
    sv = d["sv"]; o = dict()
    for lab, msk in (("plausible", PLAUS), ("full_box", np.ones(NG, bool))):
        o[lab] = dict(share_no_closure=round(float((~d["closes"][msk]).mean()), 4), share_sigma_below_0p1=round(float((sv[msk] < 0.1).mean()), 4),
                      share_sigma_below_0p2=round(float((sv[msk] < 0.2).mean()), 4), sigma_min=round(float(sv[msk].min()), 3))
        if "valid" in d: o[lab]["share_no_valid_closure_at_clip_margin"] = round(float((~d["valid"][msk]).mean()), 4)
        if not tag.startswith("ref"): o[lab]["share_margin_below_5deg"] = round(float((d["margin"][msk] < 5).mean()), 4); o[lab]["share_margin_below_10deg"] = round(float((d["margin"][msk] < 10).mean()), 4)
    o["worst_plausible_by_sigma"] = worst_poses(sv, PLAUS)
    if not tag.startswith("ref"): o["worst_plausible_by_margin"] = worst_poses(d["margin"], PLAUS)
    else:
        o["worst_plausible_by_margin"] = worst_poses(d["margin"], PLAUS)
        nc = PLAUS & ~d["closes"]
        if nc.any():                                                      # where the 4R cannot close at all: elevation / plane extent
            o["no_closure_region"] = dict(elev_range=[float(EL[nc].min()), float(EL[nc].max())], plane_range=[float(PL[nc].min()), float(PL[nc].max())],
                                          share_of_plausible_with_elev_ge_120=round(float((~d["closes"][PLAUS & (EL >= 120)]).mean()), 3),
                                          examples=worst_poses(-np.ones(NG), nc, k=6, sep=30))
    # per elevation band: share of plausible poses with no closure / sigma < 0.1
    o["by_elevation"] = {f"{a}-{b}": dict(no_closure=round(float((~d["closes"][PLAUS & (EL >= a) & (EL < b)]).mean()), 3),
                                          sigma_lt_0p1=round(float((sv[PLAUS & (EL >= a) & (EL < b)] < 0.1).mean()), 3))
                         for a, b in ((0, 30), (30, 60), (60, 90), (90, 120), (120, 150), (150, 171))}
    wsout[tag] = o
# connected regions of the plausible workspace where each chain cannot close or is near-singular (sigma < 0.15), and the
# orientation distance from the clips to the nearest such pose
from scipy import ndimage
shape = (len(pl_g), len(el_g), len(r_g)); RW = np.array(RH)
def rot_dist(Ra, Rb): return np.degrees(np.arccos(np.clip((np.einsum("pij,qij->pq", Ra, Rb) - 1) / 2, -1, 1)))
RHW = np.array([GD.Rh_of(*w[:3]) for w in WANT]); clipnames = list(dict.fromkeys(names))
for tag, d in WS.items():
    bad = PLAUS & (~d["closes"] | (d["sv"] < 0.15)); lab, nlab = ndimage.label(bad.reshape(shape)); lab = lab.ravel(); comps = []
    for cidx in range(1, nlab + 1):
        m = lab == cidx
        if m.sum() < 0.002 * PLAUS.sum(): continue
        k = np.flatnonzero(m)[np.argmin(d["sv"][m] + 0.001 * d["closes"][m])]
        comps.append(dict(share_of_plausible=round(float(m.sum() / PLAUS.sum()), 4), no_closure_share=round(float((~d["closes"][m]).mean()), 3),
                          plane=[float(PL[m].min()), float(PL[m].max())], elev=[float(EL[m].min()), float(EL[m].max())], r_rel=[float(RR[m].min()), float(RR[m].max())],
                          deepest=dict(plane=float(PL[k]), elev=float(EL[k]), axial=float(AX[k]), r_rel=float(RR[k]), sigma=round(float(d["sv"][k]), 3)),
                          task=RC.task_label(PL[k], EL[k], AX[k])))
    comps.sort(key=lambda c_: -c_["share_of_plausible"]); wsout[tag]["bad_regions"] = comps[:8]
    sing = np.flatnonzero(PLAUS & (d["sv"] < 0.05))                                 # singular or unreachable
    if len(sing):
        Dm = np.full(len(WANT), 999.0); arg = np.zeros(len(WANT), int)
        for a0 in range(0, len(sing), 4000):
            Dd = rot_dist(RHW, RW[sing[a0:a0 + 4000]]); j = Dd.argmin(1); v = Dd[np.arange(len(WANT)), j]; upd = v < Dm; Dm[upd] = v[upd]; arg[upd] = sing[a0:a0 + 4000][j[upd]]
        per = {}
        for cn in clipnames:
            m = names == cn; kk = np.flatnonzero(m)[np.argmin(Dm[m])]; g = arg[kk]
            per[cn] = dict(deg=round(float(Dm[m].min()), 1), clip_frame=int(FR[kk][1]), clip_pose=[round(v) for v in WANT[kk][:3]],
                           singular_pose=[float(PL[g]), float(EL[g]), float(AX[g])], singular_task=RC.task_label(PL[g], EL[g], AX[g]))
        wsout[tag]["clip_to_nearest_singular_deg"] = per
OUT["workspace"] = wsout; OUT["grid"] = dict(plane=[-90, 150, 5], elev=[0, 170, 5], r_rel=[-90, 90, 5], poses=int(NG), plausible=int(PLAUS.sum()))
OUT["joint_rate_note"] = "worst-direction joint rate = arm angular speed / sigma: at 100 deg/s, sigma 0.1 -> 1000 deg/s, 0.05 -> 2000 deg/s"
np.savez_compressed(RC.OUT + "/jam_ws.npz", PL=PL, EL=EL, AX=AX, RR=RR, PLAUS=PLAUS, **{f"{t}_{k}": v for t, d in WS.items() for k, v in d.items()})
RC.jdump(OUT, "jam.json"); print("->", RC.OUT + "/jam.json", f"{time.time() - t0:.0f}s")
for tag, o in wsout.items():
    print(tag, o["plausible"]); [print("   ", w) for w in o["worst_plausible_by_sigma"][:4]]
for tag in CANDS: print(tag, "clip", OUT["clip_summary"][tag])
print("ref4R clips", OUT["clip_summary"]["ref4R"])
