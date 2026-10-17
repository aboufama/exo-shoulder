"""Alignment skeptic instrument (new file, 2026-10-17): independent re-check of hub-only knee determinacy on a slaved-
knuckle pin-knee design, plus the GH-drift sensing error the audit did not run.

Loads the design's model and verifier UNCHANGED through tools/alignment_knee_determinacy.worn() (the verifier's frozen
protocol). At every TAKEN pose, independently of that tool's null-space normalisation:
  * K's law slope is regressed from the K angle measured in SCREW convention (rot_angle(L1a, L1b, uK)) against q2 measured
    the same way, so the slaving row's sign cannot be inherited from the model's internal dK sign;
  * determinacy as a linear solve: with K slaved, the passive block [pin a, pin b, GH rot x y z] (6 x 5) of the loop must
    have full column rank 5 and every hub-rate vector must be consistent -> report rank and sigma_min of the passive
    block (translations scaled by 1/50 mm, as the audit's screws);
  * GH drift: hubs' readings that move with NO arm rotation. Columns J1, J2(+k K), J3, pin a, pin b against a pure GH
    translation t (arm orientation held): the followable drift plane is the 2-D subspace of t the chain can absorb; for
    a unit t in it the hub readings change by dh (deg/mm) and a fixed-GH estimator reads an arm rotation
    G_rot dh (deg/mm) that did not happen. Reported per pose: max over the followable plane.

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 tools/alignment_knee_ghdrift_skeptic.py sidecar-longdyad-knuckle-3r bench <out.json>
"""
import json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_knee_determinacy as KD      # noqa: E402  (read only: worn(), scr(), rot_angle())

LC = 50.0


def analyse(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; c3 = D.c[2]; sn = D.sn; fr = M.fr
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None]
    qK, q2 = [], []
    for i in taken:
        R1, _ = M.T(1, i); R7, _ = M.T(7, i); R2, _ = M.T(2, i)
        qK.append(KD.rot_angle(R1, R7, uK)); q2.append(KD.rot_angle(R7, R2, u2))
    qK, q2 = np.array(qK), np.array(q2)
    # K on stop A = K at its extreme value (the stop); open = the rest
    kmax, kmin = qK.max(), qK.min()
    stopA = np.abs(qK - (kmax if np.sum(np.abs(qK - kmax) < 1e-4) > np.sum(np.abs(qK - kmin) < 1e-4) else kmin)) < 1e-4
    opn = ~stopA
    pf = np.polyfit(q2[opn], qK[opn], 1); k_screw = float(pf[0])
    resid = float(np.abs(np.polyval(pf, q2[opn]) - qK[opn]).max())
    out = dict(rank=[], smin_passive=[], cond_passive=[], drift_hub_max=[], drift_j3_max=[], drift_est_rot_max=[],
               drift_unfollowable_resid=[], drift_pins_max=[])
    worst = None
    for n_, i in enumerate(taken):
        R1, t1 = M.T(1, i); R7, t7 = M.T(7, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R5, t5 = M.T(5, i)
        k = k_screw if opn[n_] else 0.0
        sJ1 = KD.scr(np.zeros(3), u1, LC); sK = KD.scr(np.zeros(3), R1 @ uK, LC); sJ2 = KD.scr(np.zeros(3), R7 @ u2, LC)
        sJ3 = KD.scr(R2 @ c3 + t2, R2 @ u3, LC); sa = KD.scr(R3 @ fr["A0"] + t3, R3 @ sn, LC); sb = KD.scr(R5 @ fr["Bm"] + t5, R5 @ sn, LC)
        H = np.stack([sJ1, sJ2 + k * sK, sJ3], 1)                       # hub columns (K slaved into J2)
        P = np.stack([sa, sb], 1)
        G = np.stack([KD.scr(np.zeros(3), e, LC) for e in np.eye(3)], 1)  # GH rotation about the fixed centre
        Pass = np.c_[P, -G]                                              # 6 x 5 passive block
        sv = np.linalg.svd(Pass, compute_uv=False); r = int((sv > 1e-6 * sv[0]).sum())
        out["rank"].append(r); out["smin_passive"].append(float(sv[-1])); out["cond_passive"].append(float(sv[0] / max(sv[-1], 1e-12)))
        # consistency of hub rates: H dh + Pass dp = 0 must be solvable for every dh -> range(H) in range(Pass)
        Q, _ = np.linalg.qr(Pass); res_H = np.linalg.norm(H - Q @ (Q.T @ H), 2)
        # GH drift at fixed arm orientation: H dh + P dpin = T t  (T = pure translation screws, scaled)
        T = np.r_[np.zeros((3, 3)), np.eye(3) / LC]
        C = np.c_[H, P]                                                  # 6 x 5
        # followable translations: t with T t in range(C)
        Uc, svc, _ = np.linalg.svd(C); rc = int((svc > 1e-6 * svc[0]).sum()); Ucr = Uc[:, :rc]
        Proj = T - Ucr @ (Ucr.T @ T)                                    # residual of each unit translation
        _, s_t, Vt_t = np.linalg.svd(Proj)
        fol = Vt_t[np.argsort(s_t)[:2]].T                                # 3 x 2: the two best-followed directions (unit, mm)
        unf = float(np.sort(s_t)[-1])
        Cp = np.linalg.pinv(C)
        dq = Cp @ (T @ fol)                                              # 5 x 2: [J1, J2, J3, pa, pb] rad per mm
        dh = dq[:3]; dpin = dq[3:]
        # the fixed-GH estimator: hub rates -> GH rotation (rad per rad), from the GH-fixed loop with K slaved
        A = np.c_[H, P, -G]                                              # 6 x 8
        _, sA, VtA = np.linalg.svd(A); rA = int((sA > 1e-6 * sA[0]).sum()); N = VtA[rA:].T   # 8 x 3
        Grot = N[5:8] @ np.linalg.inv(N[0:3])
        est = Grot @ dh
        out["drift_hub_max"].append(math.degrees(np.linalg.norm(dh, 2)))
        out["drift_j3_max"].append(math.degrees(np.abs(dh[2]).max() if dh.ndim == 1 else np.linalg.norm(dh[2], 2)))
        out["drift_est_rot_max"].append(math.degrees(np.linalg.norm(est, 2)))
        out["drift_pins_max"].append(math.degrees(np.linalg.norm(dpin, 2)))
        out["drift_unfollowable_resid"].append(unf * LC)
        if worst is None or out["drift_est_rot_max"][-1] > worst["est_rot_deg_per_mm"]:
            worst = dict(pose=int(i), kind=B.kind[i], est_rot_deg_per_mm=round(out["drift_est_rot_max"][-1], 3),
                         j3_deg_per_mm=round(out["drift_j3_max"][-1], 3), knee_ang=round(float(M.K["ang"][i]), 2) if hasattr(M, "K") else None,
                         consistency_resid=float(res_H))
    st = lambda a: dict(min=round(float(np.min(a)), 4), p5=round(float(np.percentile(a, 5)), 4), median=round(float(np.median(a)), 4),
                        p95=round(float(np.percentile(a, 95)), 4), max=round(float(np.max(a)), 4))
    return dict(poses_taken=len(taken), poses_K_open=int(opn.sum()),
                law_screw=dict(k_slope=round(k_screw, 4), resid_max_deg=round(resid, 5),
                               qK_span_deg=[round(float(qK.min()), 2), round(float(qK.max()), 2)]),
                passive_block=dict(rank=sorted(set(out["rank"])), sigma_min=st(out["smin_passive"]), cond=st(out["cond_passive"])),
                gh_drift=dict(hub_reading_deg_per_mm=st(out["drift_hub_max"]), j3_reading_deg_per_mm=st(out["drift_j3_max"]),
                              estimated_arm_rotation_error_deg_per_mm=st(out["drift_est_rot_max"]),
                              knee_pin_rate_deg_per_mm=st(out["drift_pins_max"]),
                              unfollowable_direction_gain=st(out["drift_unfollowable_resid"])),
                worst=worst)


if __name__ == "__main__":
    rid, wear, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    t = time.time(); M, B, info = KD.worn(rid, wear)
    res = dict(id=rid, wear=wear, exact=os.environ.get("CB_EXACT") == "1", **info)
    res.update(analyse(M, B)); res["secs"] = round(time.time() - t, 1)
    json.dump(res, open(outp, "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
