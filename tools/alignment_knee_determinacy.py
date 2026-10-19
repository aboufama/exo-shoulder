"""Alignment audit instrument (new file, 2026-10-17): does a slaved-knuckle pin-knee design need its knee encoders?

The user's ruling of 2026-10-17 ("if no encoders are needed, it doesn't count as added complexity") was applied in
tools/simplicity.py v2 to every pin-knee row on the premise that the 3 hub encoders fix the pose. That premise was
measured only for skin-normal-3r-pin-knee (docs/research/rebase/verify_rebase_pinknee.py dof_and_sensing: null-space
Jacobian, GH fixed). This tool repeats that check on a KNUCKLE design, where a 4th revolute K sits between J1 and J2 and
is slaved to J2's angle by a drive law (never read).

The design's model and its verifier are loaded UNCHANGED; the frozen protocol is the verifier's own (fit Bench(60,160)
fast, shape frozen, worn on Bench(110,360) exact or the held-out set). At every TAKEN pose the closed loop
    scapula - J1 - link 1a - K - link 1b - J2 - link 2 - J3 - member 3 - pin a - knee link - pin b - arm pad - GH(3R)
is written as unit screws (GH = origin, the arm a ball about it). Checks:
  * frames: the axis / point of each joint read from BOTH members it joins (must agree), and the arm pad = arm-fixed;
  * mobility = 9 - rank (K free) and chain rank;
  * K KNOWN (from its law, given q2): sigma_min of the rows J1, K, J2, J3 of the orthonormal null space N (9 x mob):
    > 0 at every pose <=> the hub readings (+ K's law) fix every passive coordinate (knee pins a, b and GH);
  * K SLAVED by the law's local slope k = d(dK)/d(q2) (regressed over the taken forced poses; 0 on stop A): the slaving
    row qK' - k q2' = 0 is appended, then sigma_min of the rows J1, J2, J3 of the null space, as the pin-knee verifier;
  * gain: max over poses of |N_p N_h^-1| (deg of knee pin / GH rate per deg of hub rate) - how hard the pins are to
    infer (an encoder error amplifier), and the same with the hub rows only for K free (should be singular: mob 4).

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 tools/alignment_knee_determinacy.py sidecar-longdyad-knuckle-3r bench <out.json>
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
D2R = math.pi / 180


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def worn(rid, wear):
    """the verifier's frozen protocol, returning the worn model and bench (the verifier's frozen_wear returns a dict only)"""
    V = _load("knee_det_verifier", os.path.join(REPO, "docs", "concepts", "verify", rid + ".py"))
    SC, CB = V.SC, V.CB
    P = SC._clamp(dict(SC.PARAMS, **V.BEST))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SC.SCModel(B1, dict(P)); r1 = M1.run()
    if wear == "fit": return M1, B1, dict(fit_fast=round(float(r1["gap"]), 2), n=len(B1.idx), mode=B1.mode)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SC.SCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if wear == "held":
        PV = _load("knee_det_polish", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    return M, B, dict(fit_fast=round(float(r1["gap"]), 2), frozen=round(float(r["gap"]), 2), n=len(B.idx), mode=B.mode)


def scr(p, w, Lc=50.0):
    w = w / np.linalg.norm(w); return np.r_[w, np.cross(p, w) / Lc]


def rot_angle(Ra, Rb, u):
    """signed angle of Ra^T Rb about u (deg)"""
    Rr = Ra.T @ Rb; a = np.array([Rr[2, 1] - Rr[1, 2], Rr[0, 2] - Rr[2, 0], Rr[1, 0] - Rr[0, 1]])
    return math.degrees(math.atan2(float(a @ u) / 1.0, float(np.trace(Rr) - 1.0)))


def analyse(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; c3 = D.c[2]; sn = D.sn; fr = M.fr
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None]
    dK = np.degrees(np.asarray(M.dK, float))                 # the model keeps dK in radians
    # law slope from the taken forced poses (K open): regress dK on q2 (deg)
    q2, frame_err = [], []
    for i in taken:
        R7, t7 = M.T(7, i); R2, t2 = M.T(2, i); q2.append(rot_angle(R7, R2, u2))
    q2 = np.array(q2); dk = dK[taken]
    opn = np.abs(dk) > 1e-6
    k_slope = float(np.polyfit(q2[opn], dk[opn], 1)[0]) if opn.sum() > 3 else 0.0
    resid = float(np.abs(np.polyval(np.polyfit(q2[opn], dk[opn], 1), q2[opn]) - dk[opn]).max()) if opn.sum() > 3 else None
    rows = dict(free_mob=[], chain_rank=[], kknown_smin=[], kknown_cond=[], slaved_mob=[], slaved_smin=[], slaved_cond=[],
                slaved_gain=[], hubonly_free_smin=[], pins_gain=[])
    worst = None
    for n_, i in enumerate(taken):
        R1, t1 = M.T(1, i); R7, t7 = M.T(7, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        Q = np.asarray(B.Q[i], float) if hasattr(B, "Q") else None
        e = [np.linalg.norm(R1 @ uK - R7 @ uK), np.linalg.norm(t1 - t7), np.linalg.norm(R7 @ u2 - R2 @ u2),
             np.linalg.norm(R2 @ u3 - R3 @ u3), np.linalg.norm((R2 @ c3 + t2) - (R3 @ c3 + t3)),
             np.linalg.norm((R3 @ fr["A0"] + t3) - (R6 @ fr.get("A0m", fr["A0"]) + t6)), np.linalg.norm(R3 @ sn - R6 @ sn),
             np.linalg.norm((R6 @ fr["Bm"] + t6) - (R5 @ fr["Bm"] + t5)), np.linalg.norm(R6 @ sn - R5 @ sn)]
        frame_err.append(e)
        S = [scr(np.zeros(3), u1), scr(np.zeros(3), R1 @ uK), scr(np.zeros(3), R7 @ u2), scr(R2 @ c3 + t2, R2 @ u3),
             scr(R3 @ fr["A0"] + t3, R3 @ sn), scr(R5 @ fr["Bm"] + t5, R5 @ sn)]
        ch = np.stack(S, 1); gh = np.stack([scr(np.zeros(3), e_) for e_ in np.eye(3)], 1)
        A = np.c_[ch, -gh]                                   # 6 x 9: J1 K J2 J3 pa pb | GH x y z
        U, sv, Vt = np.linalg.svd(A); tol = max(1e-6 * sv[0], 1e-4); r = int((sv > tol).sum()); mob = 9 - r
        svc = np.linalg.svd(ch, compute_uv=False); rows["chain_rank"].append(int((svc > max(1e-6 * svc[0], 1e-4)).sum()))
        rows["free_mob"].append(mob); N = Vt[r:].T
        hs = np.linalg.svd(N[[0, 1, 2, 3]], compute_uv=False)
        rows["kknown_smin"].append(float(hs[-1]) if N.shape[1] <= 4 and len(hs) == N.shape[1] else 0.0)
        rows["kknown_cond"].append(float(hs[0] / max(hs[-1], 1e-12)))
        hf = np.linalg.svd(N[[0, 2, 3]], compute_uv=False)   # K free, hubs only: 3 rows vs mob columns
        rows["hubonly_free_smin"].append(float(hf[-1]) if N.shape[1] <= 3 else 0.0)
        # slaved: K' = k q2' (k = 0 on stop A)
        k = k_slope if abs(dK[i]) > 1e-6 else 0.0           # deg/deg = rad/rad
        C = np.zeros(9); C[1] = 1.0; C[2] = -k
        A2 = np.r_[A, C[None]]
        U2, sv2, Vt2 = np.linalg.svd(A2); r2 = int((sv2 > max(1e-6 * sv2[0], 1e-4)).sum()); mob2 = 9 - r2
        N2 = Vt2[r2:].T; rows["slaved_mob"].append(mob2)
        h2 = np.linalg.svd(N2[[0, 2, 3]], compute_uv=False)
        sm = float(h2[-1]) if N2.shape[1] == 3 else 0.0
        rows["slaved_smin"].append(sm); rows["slaved_cond"].append(float(h2[0] / max(h2[-1], 1e-12)))
        if N2.shape[1] == 3 and sm > 1e-9:
            G_ = N2[[4, 5, 6, 7, 8]] @ np.linalg.inv(N2[[0, 2, 3]])     # passive rates per hub rate
            rows["slaved_gain"].append(float(np.linalg.norm(G_, 2))); rows["pins_gain"].append(float(np.linalg.norm(G_[:2], 2)))
        else:
            rows["slaved_gain"].append(float("inf")); rows["pins_gain"].append(float("inf"))
        if worst is None or sm < worst["sigma_min"]:
            worst = dict(pose=int(i), kind=B.kind[i], sigma_min=round(sm, 4), dK=round(float(dK[i]), 2), q2=round(float(q2[n_]), 2),
                         knee_ang=round(float(M.K["ang"][i]), 2) if hasattr(M, "K") else None)
    fe = np.array(frame_err)
    st = lambda a: dict(min=round(float(np.min(a)), 4), p5=round(float(np.percentile(a, 5)), 4), median=round(float(np.median(a)), 4),
                        p95=round(float(np.percentile(a, 95)), 4), max=round(float(np.max(a)), 4))
    nopen = int(opn.sum())
    return dict(poses_taken=len(taken), poses_K_open=nopen, poses_K_on_stopA=len(taken) - nopen,
                law=dict(k_slope_deg_per_deg=round(k_slope, 4), fit_resid_max_deg=round(resid, 4) if resid is not None else None,
                         dK_span=[round(float(dk.min()), 2), round(float(dk.max()), 2)], q2_span=[round(float(q2.min()), 2), round(float(q2.max()), 2)]),
                frame_consistency_max=dict(zip(["K_axis_1a_vs_1b", "K_point", "J2_axis", "J3_axis", "J3_point_mm", "pin_a_point_mm",
                                                "pin_a_axis", "pin_b_point_mm", "pin_b_axis"], [float(f"{x:.2e}") for x in fe.max(0)])),
                K_free=dict(mobility=sorted(set(rows["free_mob"])), chain_rank=sorted(set(rows["chain_rank"])),
                            hubs_plus_K_known_sigma_min=st(rows["kknown_smin"]), hubs_plus_K_known_cond=st(rows["kknown_cond"]),
                            hubs_only_sigma_min=st(rows["hubonly_free_smin"])),
                K_slaved=dict(mobility=sorted(set(rows["slaved_mob"])), hubs_sigma_min=st(rows["slaved_smin"]),
                              hubs_cond=st(rows["slaved_cond"]), poses_sigma_lt_0_05=int((np.array(rows["slaved_smin"]) < 0.05).sum()),
                              passive_gain=st(rows["slaved_gain"]), knee_pin_gain=st(rows["pins_gain"])),
                worst_pose=worst,
                reference="skin-normal-3r-pin-knee (verified 2026-10-16): hubs_only sigma_min >= 0.39, cond <= 2.3, mobility 3")


if __name__ == "__main__":
    rid, wear, out = sys.argv[1], sys.argv[2], sys.argv[3]
    t = time.time(); M, B, info = worn(rid, wear)
    res = dict(id=rid, wear=wear, exact=os.environ.get("CB_EXACT") == "1", **info)
    res.update(analyse(M, B)); res["secs"] = round(time.time() - t, 1)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
