"""Independent verifier of the REBASE claim (2026-10-16): skin-normal-3r-pin-knee H1 (H-g107-1, O20 x3) re-measured at the
user's fold margin 5 deg (tools/concept_kit.py FOLD_MARGIN; CB_FOLD_MARGIN overrides) - claimed 28.21 (margin 10) -> 27.20
(margin 5) on Bench(110,360) exact, shape frozen from the Bench(60,160) fast fit made at the same margin.

Runs the round-3 verifier docs/concepts/verify/skin-normal-3r-pin-knee.py UNCHANGED (frozen_model, model audit, extra_checks:
independent 3D closure, knee vs hub 3 upper, E boss, spans, pad place) and adds the checks the round-3 harness does not:

  * DOF / determinacy: screw rank of the closed loop scapula-J1-J2-J3-pin a-knee-pin b-arm-GH(3R) at EVERY taken pose
    (mobility = 8 - rank(all 8) must be 3; rank(chain of 5) must be 5 = no undetermined passive coordinate);
  * sensing claim: with the loop's 3-dim velocity null space N (8 x 3), the arm's GH rates are a function of the THREE hub
    rates iff N[J1..J3] is non-singular (then the knee pins need no encoder when GH is known); and of the 5 chain rates
    always (rank 5). Reports the conditioning of both;
  * fold margin actually used over the taken poses (th = angle(J1, J3 image), window [|a1 - a2| + m, min(a1 + a2,
    360 - a1 - a2) - m]), knee-angle window margin, radial drift |s_n| (R_tol), closure residual - all over taken poses;
  * pose accounting: every pose is taken or carries a why (no pose dropped silently), the counts add up;
  * hub envelope as sampled: hub radius (O20 = 10), F -> crown 12.25, pin stack and plate thickness.

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 docs/research/rebase/verify_rebase_pinknee.py <out.json> ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_spec = importlib.util.spec_from_file_location("pk_verifier_r3", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee.py"))
V = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V)
MK, S, CB = V.MK, V.S, V.CB
KEYS = V.KEYS
unit = S.unit


def scr(p, w, Lc=50.0):
    w = unit(w); return np.r_[w, np.cross(p, w) / Lc]


def dof_and_sensing(M, taken):
    D = M.D; u, c = D.u, D.c; sn = D.sn; fr = M.fr
    mob, rch, smin_c, s6, hub_cond, hub_smin = [], [], [], [], [], []
    for i in taken:
        R1, t1 = M.T(1, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R5, t5 = M.T(5, i)
        ch = np.stack([scr(c[0], u[0]), scr(R1 @ c[1] + t1, R1 @ u[1]), scr(R2 @ c[2] + t2, R2 @ u[2]),
                       scr(R3 @ fr["A0"] + t3, R3 @ sn), scr(R5 @ fr["Bm"] + t5, R5 @ sn)], 1)
        gh = np.stack([scr(np.zeros(3), e) for e in np.eye(3)], 1)
        A = np.c_[ch, -gh]                                    # loop closure: chain twist = arm twist (about GH)
        U, sv, Vt = np.linalg.svd(A); tol = max(1e-6 * sv[0], 1e-4)
        r = int((sv > tol).sum()); mob.append(8 - r)
        svc = np.linalg.svd(ch, compute_uv=False); rch.append(int((svc > max(1e-6 * svc[0], 1e-4)).sum()))
        smin_c.append(float(svc[-1] / svc[0])); s6.append(float(sv[5] / sv[0]))
        N = Vt[r:].T                                          # (8, mob) null space: admissible joint-rate combinations
        if N.shape[1] == 3:
            Hs = np.linalg.svd(N[:3], compute_uv=False)       # hub rates J1..J3 -> loop motion
            hub_smin.append(float(Hs[-1])); hub_cond.append(float(Hs[0] / max(Hs[-1], 1e-12)))
    if not taken: return None
    return dict(poses=len(taken), mobility=sorted(set(mob)), chain_rank=sorted(set(rch)),
                chain_sigma_min_rel=dict(min=round(min(smin_c), 4), p5=round(float(np.percentile(smin_c, 5)), 4), median=round(float(np.median(smin_c)), 4)),
                sixth_sigma_rel_max=float(f"{max(s6):.2e}"),
                hubs_only_sensing=dict(sigma_min_min=round(min(hub_smin), 4) if hub_smin else None,
                                       sigma_min_p5=round(float(np.percentile(hub_smin, 5)), 4) if hub_smin else None,
                                       cond_max=round(max(hub_cond), 1) if hub_cond else None,
                                       cond_p95=round(float(np.percentile(hub_cond, 95)), 1) if hub_cond else None),
                note="mobility 3 + chain rank 5: the loop follows the arm with no undetermined passive coordinate; "
                     "hubs_only_sensing sigma_min > 0 on every taken pose: the 3 hub rates fix the loop motion "
                     "(knee pins need no encoder if GH is known; with GH drift they carry its in-plane part)")


def windows(M, B, taken):
    D = M.D; u1, u2, u3 = D.u; a1, a2 = math.degrees(D.A[0]), math.degrees(D.A[1])
    lo0, hi0 = abs(a1 - a2), min(a1 + a2, 360 - a1 - a2)
    w = M.Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    t = np.array(taken, int)
    fm = np.minimum(th[t] - lo0, hi0 - th[t]) if len(t) else np.array([np.nan])
    am = float(M.p["ang_min"]); ang = M.K["ang"][t]
    km = np.minimum(ang - am, (180 - am) - ang) if len(t) else np.array([np.nan])
    rad = np.abs(M.s[t, 2]) if len(t) else np.array([np.nan])
    return dict(fold_margin_rule=S.SING, fold_window_deg=[round(lo0, 2), round(hi0, 2)],
                fold_margin_min_taken=round(float(fm.min()), 3), fold_margin_lt_rule=int((fm < S.SING - 1e-6).sum()),
                fold_margin_lt_10_taken=int((fm < 10).sum()),
                knee_window=[am, 180 - am], knee_margin_min_taken=round(float(km.min()), 3), knee_out=int((km < -1e-6).sum()),
                radial_drift_max_taken_mm=round(float(rad.max()), 4), R_tol=M.p["R_tol"],
                res_deg_max_taken=round(float(M.res_deg[t].max()), 4))


def accounting(M, B):
    n = len(B.idx); taken = [i for i in range(n) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    not_taken = [i for i in range(n) if i not in set(taken)]
    silent = [int(i) for i in not_taken if not M.why[i]]
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    return dict(n_poses=n, taken=len(taken), not_taken=len(not_taken), why=why, why_sum=sum(why.values()), silent_drops=silent[:20],
                n_silent=len(silent), n_clip=int(sum(1 for k in B.kind if k == "clip")), n_ws=int(sum(1 for k in B.kind if k == "ws"))), taken


def main():
    outp = sys.argv[1]; P = json.loads(sys.argv[2]) if len(sys.argv) > 2 else dict(V.ROW["best_params"])
    t0 = time.time(); M, B, fit, M1 = V.frozen_model(P)
    r = M.run(); model = {k: r[k] for k in KEYS}
    acc, taken0 = accounting(M, B)
    aud0 = MK.audit(M, B)
    ex, bad = V.extra_checks(M, B)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = MK.audit(M, B)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    dof = dof_and_sensing(M, taken); win = windows(M, B, taken)
    B.res = res0
    env = dict(hub_r=list(M.hr), crown=S.CROWN, up=S.UP, stk=M.p["stk"], tp=round(M.p["tp"], 3), run=S.RUN, t_link=S.T_LINK,
               w_link=S.W_LINK, boss_r=MK.BOSS_R, knee_w=MK.KNEE_W, lE=M.p["lE"], lc=M.p["lc"], o20_only=S._KIT.O20_ONLY,
               fold_margin=S._KIT.FOLD_MARGIN)
    out = dict(params=P, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fold_margin=S.SING, fit_fast=fit, model=model,
               accounting=acc, model_audit=aud0, extra=ex, corrected=corrected, corrected_audit=aud, dof=dof, windows=win,
               envelope=env, verifier_removed=len(bad), secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(mode=B.mode, margin=S.SING, fit=fit, model=model, corrected=corrected, near1=aud["gap_near1"], near_min=aud["near_touch_min_mm"],
                          removed=len(bad), acc=acc, dof=dof, win=win, env=env, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
