"""Independent verifier (skeptic) of dipped-law-groove-knuckle-3r (the lead's slaved roller-flank knuckle with kneewin's
centred knee and a DIPPED K law: the lobe lets the clock spring close K below the old stop A in the mid-folded band,
the bent arm is built at the dip floor, the flank is synthesised over [dK_neg, dK_lim]).

The claim's model (docs/concepts/models/dipped-law-groove-knuckle-3r.py, on roller-longdyad-knuckle-3r.py) is loaded
UNCHANGED. The protocol is the round's roller-flank verifier (docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py:
fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out; continuity flood), retargeted at the
claim's DipModel. The parent's per-pose drive checks read |dK| and build the crank at K = 0; the dip runs K NEGATIVE and
builds the crank at kref = the dip floor, so they are REWRITTEN here on the SIGNED opening (otherwise every dipped pose
would read as wrong-sense / off-flank). Checks on every TAKEN pose of the worn bench:

  1. CAM CLOSURE IN THE WORLD (signed): roller centre carried by the crank (member 9) on link 1a's flank path at the
     pose's signed K within 0.5 mm; roller vs lug >= ROLL_R; K inside [dK_neg, dK_lim]; crank / horn pressure angles at
     the pose's signed K <= 43 (and re-read at 45).
  2. FRAME CONSISTENCY (new, not in any parent verifier): J2's axis carried by link 1b and by link 2 agree, J3's axis
     carried by link 2 and by member 3 agree (< 0.05 deg), K's angle read from the frames (R1^T R1b about uK) equals the
     model's dK (< 0.05 deg), and the effective first link a1e read from the frames equals a1 - dip(th) on dipped poses.
     Catches a state-A closure that built hub 2 / link 2 at the undipped K while the drive was posed at the dipped K.
  3. LOBE CAM CLOSURE (new): the lobe reads q2. Every taken state-A pose must sit on the cam curve: q2 read from the
     frames (R1b^T R2 about u2) equals q2(th) of the dipped closure at the pose's th (< 0.1 deg), and K equals k(th).
     The cam is single-valued over the WHOLE dwell (q2(th) strictly monotone on [th_lo, th_hi] with the dip inside it,
     not only over the band), and the coupled rate dq2/dth at each dipped taken pose <= RATE_MAX.
  4. FOLD MARGIN (copied from docs/concepts/verify/roller-longdyad-knuckle-3r.py th_margin) plus the coupled reading
     for dipped poses (where J2 moves and K follows q2, the singularity is dth/dq2 = 0, i.e. rate -> inf; the J1-K-J3
     sub-chain margin msub is not a singularity of this chain).
  5. LOBE TOLERANCE: K error per 10 um of lobe profile error, against the dip floor.
  6. CONTINUITY FLOOD (connected_report, unchanged).
 --head: the lug's flank-edge strip that the claim's sampling deletes, rebuilt on the SIGNED flank path [dK_neg, dK_lim]
         (the claim already samples the stub head).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/dipped-law-groove-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--head] [--d0]
    (--d0: the same harness on the claim's D = 0 control, kneewin's centred knee)
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


DL = _load("dipped_law_claim_v", os.path.join(REPO, "docs", "concepts", "models", "dipped-law-groove-knuckle-3r.py"))
H = _load("roller_flank_verifier_for_dip", os.path.join(HERE, "sidecar-roller-flank-knuckle-3r.py"))
H.RF = types.SimpleNamespace(phi_of=DL.RF.phi_of, dphi_of=DL.RF.dphi_of, ROLL_R=DL.RF.ROLL_R, _ring=DL.RF._ring,
                             RFModel=DL.DipModel, _clamp=DL._clamp, PARAMS=DL.PARAMS)
H.SC, H.S, H.PK = DL.SC, DL.S, DL.PK
S = DL.S; unit = S.unit; D2R = math.pi / 180
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "dipped-law-groove-knuckle-3r.json")))["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
PA_MAX, CLOSE_TOL, ROLL_R = 43.0, 0.5, DL.RF.ROLL_R
phi_of, dphi_of = DL.RF.phi_of, DL.RF.dphi_of


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(unit(a), unit(b))), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def _rot_angle(R, u):
    """signed angle of R about u (R assumed a rotation about u); also the axis deviation |R u - u| in deg"""
    e = unit(np.cross(u, [0.3, 0.5, 0.8])); Re = R @ e
    return math.atan2(float(np.cross(e, Re) @ u), float(e @ Re)), _ang(R @ u, u)


def flank_path_signed(M):
    """roller-centre path in link 1a's frame over the drive's own SIGNED range [dK_neg, dK_lim], crank built at kref"""
    g = M._scg; PV, dR, uK, sp, sig, gg, cc, kref = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0), g.get("kref", 0.0)
    C0 = np.asarray(M._viz_rod["roller"], float); kg = np.arange(float(g.get("dK_neg", 0.0)), g["dK_lim"] + 1e-9, math.radians(0.25))
    Rc = S.rotm(dR, sig * phi_of(kg - kref, gg, cc)); Cb = np.einsum("nij,j->ni", Rc, C0 - PV) + PV
    return np.einsum("nij,nj->ni", S.rotm(uK, sp * kg), Cb)


H.flank_path = flank_path_signed            # --head envelope on the signed path


def cam_curve(D, th):
    """the dipped closure at polar angles th (deg): a1e, signed K opening (rad), dK (rad), q2 on the design's half-turn"""
    u1, u2, u3 = D.u; uK = D.uK; sp = float(np.sign(D.psiA)) or 1.0
    th = np.asarray(th, float); a1e = D.a1 - D.dip_of(th); k = np.asarray(D.kopen_of(a1e), float)
    k = np.where(D.dip_of(th) > 1e-9, k, 0.0); dK = sp * k
    RK = S.rotm(uK, dK); u1b = np.einsum("nji,j->ni", RK, u1)
    A = (u1b @ u2) * float(u2 @ u3); Bc = u1b @ u3 - A; Cs = u1b @ np.cross(u2, u3)
    R = np.hypot(Bc, Cs); q0 = np.arctan2(Cs, Bc)
    q2 = q0 + D.q2sgn * np.arccos(np.clip((np.cos(th * D2R) - A) / R, -1, 1))
    return a1e, k, dK, q2


def th_margin(M, B):
    """docs/concepts/verify/roller-longdyad-knuckle-3r.py th_margin, copied; dK read as the SIGNED opening so that the dipped
    (closing, < 0) poses are told apart from the stretched rise (> 0)"""
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float) * (float(M._scg["sp"]) if getattr(M, "_scg", None) else 1.0)   # SIGNED opening (+ = drive's sense)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m_plain = _dm(th, a1, a2); m_eff = _dm(th, a1e, a2e); m_sub = _dm(th, b1, c)
        rows.append((min(m_sub, m_eff) if forced else m_plain, forced, m_plain, m_eff, m_sub, i, th, float(dK[i])))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]; lo = min(rows)
    neg = [r for r in rows if r[7] < -1e-6]
    # coupled reading: dipped poses use m_eff (the 3R J1-J2-J3 with a1e) only; stretched poses keep the lead's own rule
    own_c = [(r[3] if r[7] < -1e-6 else r[0]) for r in rows]
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)),
                forced=int(sum(r[1] for r in rows)), th_max_taken=round(max(r[6] for r in rows), 2),
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), dK=round(math.degrees(lo[7]), 2), kind=B.kind[lo[5]],
                            **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}),
                dipped=dict(n=len(neg), m_sub_min=round(min(r[4] for r in neg), 3) if neg else None,
                            m_eff_min=round(min(r[3] for r in neg), 3) if neg else None),
                coupled=dict(min=round(min(own_c), 3), lt5=int(sum(1 for x in own_c if x < 5 - 1e-6))))


def extra_checks(M, Mfit, B, pa_max=None):
    pa_max = PA_MAX if pa_max is None else pa_max
    g = M._scg; tab = Mfit._cam_table; D = M.D; P = D.p
    PV, dR, uK, sp, sig, gg, cc, kref = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0), g.get("kref", 0.0)
    kneg, klim = float(g.get("dK_neg", 0.0)), float(g["dK_lim"])
    u1, u2, u3 = D.u
    C0 = np.asarray(M._viz_rod["roller"], float); lugM = g["lugM"]
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    dK = np.asarray(M.dK, float); st = np.asarray(M.kstate)
    ec, dl, pac, pah, bad, why = [], [], [], [], [], {}
    fr = dict(j2_axis=0.0, j3_axis=0.0, k_from_frames=0.0, a1e_dip=0.0, q2_cam=0.0, k_cam=0.0, q2_axis=0.0)
    ndip, rate_pose = 0, []
    for i in taken:
        ks = sp * float(dK[i]); ph = sig * float(phi_of(ks - kref, gg, cc))
        R1, t1 = M.T(1, i); R9, t9 = M.T(9, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i); R3, _ = M.T(3, i)
        Cw = R9 @ C0 + t9
        Cb = S.rotm(dR, ph)[0] @ (C0 - PV) + PV
        Ca = S.rotm(uK, float(dK[i]))[0] @ Cb
        Cexp = R1 @ Ca + t1
        e = float(np.linalg.norm(Cw - Cexp)); ec.append(e)
        Lw = lugM @ R1.T + t1; d = float(cKDTree(Lw).query(Cw)[0]); dl.append(d)
        a = float(np.interp(math.degrees(ks), tab["k"], tab["pa_crank"])); h = float(np.interp(math.degrees(ks), tab["k"], tab["pa_horn"]))
        pac.append(a); pah.append(h)
        # 2. frame consistency
        e2 = _ang(R1b @ u2, R2 @ u2); e3 = _ang(R2 @ u3, R3 @ u3)
        kf, kax = _rot_angle(R1.T @ R1b, uK); ekf = abs(math.degrees(kf - float(dK[i])))
        q2f, q2ax = _rot_angle(R1b.T @ R2, u2)
        th = _ang(u1, R2 @ u3); a1e_f = _ang(u1, R1b @ u2)
        fr["j2_axis"] = max(fr["j2_axis"], e2); fr["j3_axis"] = max(fr["j3_axis"], e3); fr["k_from_frames"] = max(fr["k_from_frames"], ekf, kax)
        fr["q2_axis"] = max(fr["q2_axis"], q2ax)
        rs = []
        # 3. lobe cam closure on state-A poses (dipped or dwell)
        if st[i] == 0:
            a1e_c, k_c, dK_c, q2_c = cam_curve(D, np.array([th]))
            eq = abs(math.degrees(float(DL.PK.wrap(q2f - float(q2_c[0])))))
            ek = abs(math.degrees(float(dK[i]) - float(dK_c[0])))
            fr["q2_cam"] = max(fr["q2_cam"], eq); fr["k_cam"] = max(fr["k_cam"], ek)
            if D.dip_of(np.array([th]))[0] > 1e-9:
                ndip += 1; fr["a1e_dip"] = max(fr["a1e_dip"], abs(a1e_f - float(a1e_c[0])))
                _, _, _, q2a = cam_curve(D, np.array([th - 0.25, th + 0.25]))
                rate_pose.append(abs(float(DL.PK.wrap(q2a[1] - q2a[0]))) / (0.5 * D2R))
            if eq > 0.1 or ek > 0.1: rs.append("lobe_cam")
        if e2 > 0.05 or e3 > 0.05 or ekf > 0.05: rs.append("frames")
        if e > CLOSE_TOL: rs.append("closure")
        if d < ROLL_R - 1e-6: rs.append("roller_in_lug")
        if ks > klim + 1e-9 or ks < kneg - 1e-9: rs.append("beyond_flank")
        if a > pa_max or h > pa_max: rs.append("pressure")
        if rs:
            bad.append(i)
            for r_ in rs: why[r_] = why.get(r_, 0) + 1
    tk = np.array(taken, int)
    # the cam must be single-valued over the WHOLE dwell (q2(th) monotone on [th_lo, th_hi] with the dip inside it)
    thg = np.arange(float(D.th_lo), float(D.th_hi) + 1e-9, 0.25); _, _, _, q2g = cam_curve(D, thg)
    dq = np.diff(np.unwrap(q2g)); mono_all = bool(np.all(np.sign(dq) == np.sign(dq[0]))) if len(dq) else True
    rate_all = float(np.max(np.abs(dq) / (0.25 * D2R))) if len(dq) else None
    # real lobe pressure angle over the taken STRETCHED range (parent rule) - the dip's own lobe pa is the claim's dip table
    kpos = np.abs(dK[tk][sp * dK[tk] > 0]) if len(tk) else np.zeros(0)
    kmax = float(kpos.max()) if len(kpos) else 0.0
    kg = np.linspace(0.0, kmax, 200); kK = float(P.get("kA", P.get("kK", 0.0))); s_arm = float(P["s_arm"]); rl0 = float(P["r_lobe"])
    r_t = rl0 + s_arm * phi_of(kg, gg, cc); pa_l = np.degrees(np.arctan(s_arm * dphi_of(kg, gg, cc) * kK / r_t))
    T = D.dip_table() if D._D() > 0 else {}
    out = dict(n_taken=len(taken), closure_max_mm=round(max(ec), 4) if ec else None, roller_lug_min_mm=round(min(dl), 3) if dl else None,
               pa_crank_max=round(max(pac), 1) if pac else None, pa_horn_max=round(max(pah), 1) if pah else None, pa_rule=pa_max,
               dK_sign_counts=dict(pos=int(np.sum(sp * dK[tk] > 1e-6)), neg=int(np.sum(sp * dK[tk] < -1e-6)), zero=int(np.sum(np.abs(dK[tk]) <= 1e-6))),
               dK_taken_min_deg=round(math.degrees(float((sp * dK[tk]).min())), 2) if len(tk) else None,
               dK_taken_max_deg=round(math.degrees(kmax), 2), dK_lim_deg=round(math.degrees(klim), 2), dK_neg_deg=round(math.degrees(kneg), 2),
               why_lim=g.get("why_lim"), kref_deg=round(math.degrees(kref), 2), drive_idle=bool(math.degrees(kmax) < 30.0),
               pa_lobe_real_max=round(float(pa_l.max()), 2),
               frames_max_deg={k: round(v, 4) for k, v in fr.items()}, n_dipped_taken=ndip,
               rate_dipped_taken_max=round(max(rate_pose), 3) if rate_pose else None, rate_max_rule=DL.RATE_MAX,
               cam_whole_dwell=dict(mono=mono_all, rate_max=round(rate_all, 3) if rate_all is not None else None, th=[float(D.th_lo), float(D.th_hi)]),
               dip_table=T,
               lobe_tol=dict(K_deg_per_10um=round(math.degrees(0.01 * float(gg) / s_arm), 3),
                             dip_floor_deg=round(math.degrees(D.dip_floor()), 2) if D._D() > 0 else 0.0),
               poses_failing=len(bad), why_failing=why, poses_failing_ids=bad[:50])
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    out["corrected"] = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    B.res = res0
    try: out["th_margin"] = th_margin(M, B)
    except Exception as ex: out["th_margin"] = dict(error=repr(ex)[:300])
    return out


_extra = extra_checks


def extra_checks_both(M, Mfit, B):
    out = _extra(M, Mfit, B, PA_MAX)
    o45 = _extra(M, Mfit, B, 45.0); out["at_pa45"] = {k: o45[k] for k in ("poses_failing", "why_failing", "corrected")}
    return out


H.extra_checks = extra_checks_both
H.PA_MAX = PA_MAX


def overhead_split(M, B):
    """reach / in-band at elev >= 140 and the why of the lost overhead ws poses (the claim's audit already has it; re-read)"""
    ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws" and B.poses[i]["elev"] >= 140]
    tk = [i for i in ws if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    return dict(ws=len(ws), taken=len(tk))


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        P = dict(BEST)
        if "--d0" in sys.argv: P["dipD"] = 0.0; P["dip_ref"] = 0.0
        t = time.time(); out = H.frozen_wear(P, wear, "--flood" in sys.argv, "--head" in sys.argv)
        out.update(wear=wear, d0="--d0" in sys.argv, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, d0=out["d0"], head=out["head"], fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"),
                              why=out["why"], extra=out["extra"], conn=out.get("connected"), secs=out["secs"]), default=float))
