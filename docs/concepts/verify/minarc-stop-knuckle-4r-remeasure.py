"""Independent verifier (lens: RE-MEASURE THE NUMBER) for minarc-stop-knuckle-4r VARIANT B (2026-10-16).

Variant B = docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py (imported UNCHANGED): the pin knee + a spring-held passive
knuckle K in link 1 + J2 interior-angle hard stops. This harness applies the pin knee's verified frozen protocol
(docs/concepts/verify/skin-normal-3r-pin-knee-polish.py, round-3 verifier docs/concepts/verify/skin-normal-3r-pin-knee.py) to
variant B and to H1 side by side:

  wear  <fit60|fitbig> <bench|held> <B|H1> <out.json> ['<json params>']
        shape fitted on Bench(60,160) FAST (fit60) or Bench(110,360) FAST (fitbig), frozen (heights, knuckle hub, link
        profiles, knee centre m), worn without refit on Bench(110,360) (bench) or the disjoint held-out bench of the pin
        knee's polish verifier (held: every fit-clip frame + workspace pose outside Bench(110,360) and Bench(60,160);
        Wave / Walking stay out). CB_EXACT=1 -> exact distances on the wear bench; CB_FOLD_MARGIN sets the fold margin.
        H1 runs through the pin knee's verified harness functions unchanged (frozen_on, extra_checks, audit).
        B runs through the variant-B model + this verifier's own extra checks (independent of the model's closed form):
          * per taken pose: link 1a turns about u1 only, link 1b vs 1a about uK only, link 2 vs 1b about u2 only, member 3 vs
            link 2 about u3 only, hub 3 centre carried by link 2 = by member 3, pin a member 3 = knee link, pin b knee = arm,
            both knee rotations about the skin normal (the round-3 checks); arm orientation residual (model res_deg);
          * K one-sided between its stops: dK has psiA's sign (opens away from stop A) and a1e <= a1max (stop B);
          * the J2 interior angle phi re-computed from the member frames (angle at J2's world axis between the arcs to J1's
            axis and J3's world axis) inside [phi_lo, phi_hi] (+0.05 deg);
          * the E boss vs hub 1 / hub K / hub 2 / link 1a / link 1b (>= 1 mm) and vs link 2 away from hub 3 (adjacent
            0.15 mm); the knee link vs hub 3 above its lower plate (>= 1 mm) - the round-3 checks with link 1 split;
          * reported: the J1-J3 fold margin of the plain dyad (th - |a1 - a2|, a1 + a2 - th: the pin knee's fold-margin
            metric) over the taken state-A poses, the sub-chain margin over the forced poses, K's opening.
        The verifier knocks failing poses out (corrected); near-touch (metal < 1 mm = contact) from the model's audit.
  conn  <fit60|fitbig> <B|H1> <out.json> ['<json params>']
        workspace continuity flood fill (CLAUDE.md "Reach must be reachable by moving") on the FULL 1432-pose workspace grid:
        nodes = kinematically closed poses (fold / knee window / stops / K range / sub-chain margin / radial tol / closure
        < 0.5 deg at the margin in force), shape (knee centre m) frozen from the fit bench; edges = grid neighbours,
        humerus slerped in <= 2 deg steps, every step closes, no joint among q1, q2, q3' = q3 + phi, pin a, pin b, dK
        (variant B) steps > 10 deg, the knee branch sign constant; seeds = elevation 0. Reports static vs connected on the
        grid and on the Bench(110,360) workspace poses, plus the islands (with their J2 / K state).
  wear ... --conn <conn.json>: the continuity rule on the worn bench - taken workspace poses outside the connected set
        (same design, fit and margin) are knocked out and the bench re-scored (corrected + connected = the claim's number).

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py wear fit60 bench B out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


PV = _load("pk_polish_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py"))          # pin knee verified harness (unchanged)
V, MK, S = PV.V, PV.MK, PV.S
KB = _load("minarc_b_model", os.path.join(REPO, "docs", "concepts", "models", "minarc-stop-knuckle-4r-pinknee.py"))
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "minarc-stop-knuckle-4r.json")))
H1ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-pin-knee.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
D2R = math.pi / 180
STEP, JUMP = 2.0, 10.0


def params_for(which, extra=None):
    if which == "H1": P = dict(H1ROW["v_polish_params"])
    else:
        P = {k: v for k, v in ROW["best_params"].items() if k not in ("variant", "model")}
        P = dict(KB.PARAMS, **P)
    if extra: P.update(extra)
    return P


def frozen_B(fitB, wearB, P):
    """variant B frozen hand-over (the same attribute list as the pin knee's verified frozen_on + the knuckle hub fK)"""
    M1 = KB.KModel(fitB, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = fitB.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(KB.KModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(wearB, P2)
    return M, fit, M1


def rot_axis_err(Rrel, ax):
    """deg: how far Rrel moves its supposed axis ax (0 = a pure rotation about ax)"""
    return math.degrees(math.acos(max(-1.0, min(1.0, float((Rrel @ ax) @ ax)))))


def extra_checks_B(M, B):
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = P["tp"]; h = S.T_LINK / 2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    out = {}
    _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; zz = (X - cen3) @ u[2]; H3up = X[zz >= S.UP - 1e-6]
    e, f = S.frame_of(sn); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(MK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + MK.BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)])
    clo = dict(l1a_axis=0.0, k_axis=0.0, j2_axis=0.0, hub3c=0.0, rot3_axis=0.0, pin_a=0.0, pin_b=0.0, knee_rot_axis=0.0)
    bad_close, bad_kh3, bad_boss, bad_k, bad_phi = [], [], [], [], []; low_kh3, low_boss = [], []
    a1, a2 = D.a1, D.a2; b1, b2 = float(P["bk1"]), float(P["bk2"])
    phi_lo = max(S.SING, float(P["phi_lo"])); phi_hi = min(180 - S.SING, float(P["phi_hi"]))
    cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
    dK_max = math.degrees(math.acos(max(-1, min(1, cpsiB))) - abs(D.psiA))
    phis, dks, th_m_A, msub_F, states = [], [], [], [], []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        e0 = rot_axis_err(R1, u[0]); eK = rot_axis_err(R1.T @ R1b, D.uK); eJ2 = rot_axis_err(R1b.T @ R2, u[1])
        e1 = float(np.linalg.norm((R2 @ c[2] + t2) - (R3 @ c[2] + t3))); e2 = rot_axis_err(R2.T @ R3, u[2])
        A_m3 = R3 @ fr["A0"] + t3; A_k = R6 @ fr["A0m"] + t6; e3 = float(np.linalg.norm(A_m3 - A_k))
        B_k = R6 @ fr["Bm"] + t6; B_a = R5 @ fr["Bm"] + t5; e4 = float(np.linalg.norm(B_k - B_a))
        e5 = max(rot_axis_err(R3.T @ R6, sn), rot_axis_err(R6.T @ R5, sn))
        for k, v in zip(("l1a_axis", "k_axis", "j2_axis", "hub3c", "rot3_axis", "pin_a", "pin_b", "knee_rot_axis"), (e0, eK, eJ2, e1, e2, e3, e4, e5)):
            clo[k] = max(clo[k], v)
        if max(e0, eK, eJ2, e2, e5) > 0.5 or max(e1, e3, e4) > 0.5: bad_close.append(i)
        # K: signed opening about uK (link 1a frame), one-sided, <= stop B
        Rk = R1.T @ R1b; rv = Rot.from_matrix(Rk).as_rotvec(); dk = float(np.degrees(rv @ D.uK)); dks.append(dk)
        if dk * np.sign(D.psiA) < -0.05 or abs(dk) > dK_max + 0.05: bad_k.append(i)
        # J2 interior angle from the member frames
        p2 = R1b @ u[1]; w3 = R2 @ u[2]; a_ = u[0] - (u[0] @ p2) * p2; b_ = w3 - (w3 @ p2) * p2
        phi = math.degrees(math.acos(max(-1, min(1, float(a_ @ b_) / (np.linalg.norm(a_) * np.linalg.norm(b_) + 1e-12))))); phis.append(phi)
        if phi < phi_lo - 0.05 or phi > phi_hi + 0.05: bad_phi.append(i)
        th = math.degrees(math.acos(max(-1, min(1, float(w3 @ u[0]))))); st = int(M.kstate[i]); states.append(st)
        if st == 0: th_m_A.append(min(th - abs(a1 - a2), a1 + a2 - th))
        else: msub_F.append(float(M.msub[i]))
        bx = M._boxes_at_final(i); kc, kR, kh = bx["knee"]
        d_kh3 = float(M.sd_box(H3up @ R3.T + t3, kc, kR, kh).min()); low_kh3.append((d_kh3, i))
        if d_kh3 < S.PART_CLEAR: bad_kh3.append(i)
        bw = boss @ R3.T + t3; cyl = {k: (M.T(m, i)[0] @ cc + M.T(m, i)[1], M.T(m, i)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
        stp = {k: X @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X) in M.strap.items()}
        v = {f"boss-{hb}": float(M.sd_cyl(bw, *cyl[hb], r=M.cyl_r[hb]).min()) for hb in ("hub1", "hubK", "hub2")}
        for L in ("L1a", "L1b"):
            if len(stp[L]): v[f"boss-{L}"] = float(cKDTree(stp[L]).query(bw)[0].min()) - h
        c3w, ax3 = cyl["hub3"]; w = stp["L2"] - c3w; far = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > S.HUB_R + 1
        vL2 = float(cKDTree(stp["L2"][far]).query(bw)[0].min()) - h if far.any() else 1e9
        k = min(v, key=v.get); low_boss.append((min(v[k], vL2), i, k if v[k] <= vL2 else "boss-L2"))
        if v[k] < S.PART_CLEAR or vL2 < M.ADJ: bad_boss.append(i)
    out["closure_max"] = {k: round(v, 4) for k, v in clo.items()}; out["closure_bad_poses"] = len(bad_close)
    out["res_deg_max_taken"] = round(float(M.res_deg[taken].max()), 4) if taken else None
    low_kh3.sort(); low_boss.sort()
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    out["knee_vs_hub3_upper_low"] = [dict(mm=round(d, 2), **lab(i)) for d, i in low_kh3[:5]]; out["knee_vs_hub3_upper_bad"] = len(bad_kh3)
    out["boss_low"] = [dict(mm=round(d, 2), pair=k, **lab(i)) for d, i, k in low_boss[:5]]; out["boss_bad"] = len(bad_boss)
    out["knuckle"] = dict(psiA_deg=round(math.degrees(D.psiA), 2), dK_range_taken=[round(min(dks), 2), round(max(dks), 2)] if dks else None,
                          dK_max_stopB=round(dK_max, 2), bad=len(bad_k))
    states = np.array(states)
    out["j2_phi"] = dict(stops=[round(phi_lo, 2), round(phi_hi, 2)], range_taken=[round(min(phis), 2), round(max(phis), 2)] if phis else None, bad=len(bad_phi))
    out["states_taken"] = {"A": int((states == 0).sum()), "stretched": int((states == 1).sum()), "folded": int((states == -1).sum())}
    out["fold_margin_th_stateA"] = dict(min=round(min(th_m_A), 2) if th_m_A else None, lt5=int(sum(1 for x in th_m_A if x < 5)),
                                        lt10=int(sum(1 for x in th_m_A if x < 10)), a_deg=[round(a1, 2), round(a2, 2)])
    out["sub_margin_forced"] = dict(min=round(min(msub_F), 2) if msub_F else None, n=len(msub_F))
    return out, set(bad_close) | set(bad_kh3) | set(bad_boss) | set(bad_k) | set(bad_phi)


def wear(fit, wb, which, outp, extra, conn_json=None):
    t0 = time.time(); P = params_for(which, extra)
    fitB = PV.fast_bench(60, 160) if fit == "fit60" else PV.fast_bench(110, 360)
    wearB = PV.held_bench() if wb == "held" else CB.Bench(n_clip=110, n_ws=360)
    if which == "H1":
        M, fitr, M1 = PV.frozen_on(fitB, wearB, P); r = M.run(); model = {k: r[k] for k in KEYS}
        aud0 = MK.audit(M, wearB); ex, bad = V.extra_checks(M, wearB)
    else:
        M, fitr, M1 = frozen_B(fitB, wearB, P); r = M.run(); model = {k: r[k] for k in KEYS}
        aud0 = KB.PK.audit(M, wearB); ex, bad = extra_checks_B(M, wearB)
    res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in KEYS}
    aud = (MK.audit if which == "H1" else KB.PK.audit)(M, wearB)
    taken = [bool(wearB.res[i] is not None and float(np.min(wearB.res[i])) >= 0) for i in range(len(wearB.idx))]
    cres = None
    if conn_json:                                            # continuity rule: reach on the CONNECTED set only
        Cj = json.load(open(conn_json)); assert Cj["design"] == which and Cj["fit"] == fit and Cj["fold_margin"] == KIT.FOLD_MARGIN
        assert np.allclose(np.array(Cj["m"])[:2], np.array(M.D.m)[:2], atol=1e-3), (Cj["m"], M.D.m)
        ck = {tuple(x) for x in Cj["connected_keys"]}
        drop = [i for i in range(len(wearB.idx)) if wearB.kind[i] == "ws" and taken[i]
                and (float(wearB.poses[i]["plane"]), float(wearB.poses[i]["elev"]), float(wearB.poses[i]["axial"])) not in ck]
        for i in drop: wearB.res[i] = None
        rcc = wearB.report(); audc = (MK.audit if which == "H1" else KB.PK.audit)(M, wearB)
        cres = dict(conn_file=conn_json, ws_taken=sum(1 for i in range(len(wearB.idx)) if wearB.kind[i] == "ws" and taken[i]), dropped_unconnected=len(drop),
                    dropped=[dict(plane=wearB.poses[i]["plane"], elev=wearB.poses[i]["elev"], axial=wearB.poses[i]["axial"], state=int(getattr(M, "kstate", np.zeros(len(wearB.idx), int))[i])) for i in drop[:40]],
                    **{k: rcc[k] for k in KEYS}, gap_near1=audc["gap_near1"], near1_poses=audc["near1_poses"], min_mm=audc["near_touch_min_mm"],
                    overhead140=audc["overhead140"], score=round(100 * (1 - rcc["gap"] / 275), 2))
    wearB.res = res0
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    out = dict(design=which, fit_protocol=fit, wear_bench=wb, params=P, fit_mode=fitB.mode, wear_mode=wearB.mode, n_wear=len(wearB.idx),
               exact=os.environ.get("CB_EXACT") == "1", fold_margin=KIT.FOLD_MARGIN, sing=S.SING, o20_only=KIT.O20_ONLY,
               m=[float(x) for x in M.D.m], fit=fitr, model=model, model_audit=aud0, extra=ex, bad_removed=len(bad), corrected=corrected,
               score=round(100 * (1 - corrected["gap"] / 275), 2), corrected_audit=aud, connected=cres, why=why,
               knuckle_model=r.get("knuckle"), hubs=list(M.hr), f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2),
               idx=[int(x) for x in wearB.idx], kind=list(wearB.kind), taken=taken,
               pose_key=[[float(p["plane"]), float(p["elev"]), float(p["axial"])] for p in wearB.poses], secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(design=which, fit=fit, wear=wb, mode=wearB.mode, n=len(wearB.idx), margin=KIT.FOLD_MARGIN, fit_r=fitr, model=model,
                          corrected=corrected, score=out["score"], connected=cres and {k: v for k, v in cres.items() if k != "dropped"}, near1=aud["gap_near1"], near1_poses=aud["near1_poses"], min_mm=aud["near_touch_min_mm"],
                          overhead=aud["overhead140"], bad=len(bad), extra={k: ex.get(k) for k in ("closure_max", "closure_bad_poses", "knuckle", "j2_phi",
                          "states_taken", "fold_margin_th_stateA", "sub_margin_forced", "boss_bad", "knee_vs_hub3_upper_bad")}, secs=out["secs"]), default=float), flush=True)


# ---------------- continuity ----------------
def kin_B(D, Q, R_tol):
    q, ok, X1, X2, X3, s = D.ik(Q); dK = D._dK.copy(); st = D._state.copy(); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, Q) - 1) / 2
    ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"], dK])
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    return ok, qq, sgn, st


def kin_H(D, Q, R_tol):
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, Q) - 1) / 2
    ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    return ok, qq, sgn, np.zeros(len(Q), int)


def conn(fit, which, outp, extra, taken_mode=False):
    t0 = time.time(); P = params_for(which, extra)
    Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
    W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
    fitB = PV.fast_bench(60, 160) if fit == "fit60" else PV.fast_bench(110, 360)
    Mf = (MK.Model if which == "H1" else KB.KModel)(fitB, dict(P))        # kinematics only (no run): the frozen knee centre m
    m = np.array(Mf.D.m, float)
    D = (MK.Design if which == "H1" else KB.KDesign)(dict(Mf.p)); D.m = m.copy(); D.m[2] = 0.0
    R_tol = float(Mf.p["R_tol"]); kin = kin_H if which == "H1" else kin_B
    ok, qq, sgn, st = kin(D, HG, R_tol)
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

    n_edge = [0, 0]; why = {"fold_or_window": 0, "jump": 0, "branch": 0}; jump_by = np.zeros(qq.shape[1], int)

    def edge(a, b):
        angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude())
        n = max(2, int(math.ceil(angd / STEP)) + 1)
        Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, sg, _ = kin(D, Qs, R_tol); n_edge[0] += 1
        if not o.all(): why["fold_or_window"] += 1; return False
        d = np.abs((np.diff(q, axis=0) + 180) % 360 - 180)
        if d.max() > JUMP: why["jump"] += 1; jump_by[int(np.argmax(d.max(0)))] += 1; return False
        if len(set(sg.tolist())) > 1: why["branch"] += 1; return False
        n_edge[1] += 1; return True

    elev = POSE[:, 1]; nodes = ok.copy(); nodes_from = "kinematic closure"; n_bad = None
    if taken_mode:                                           # contact-aware: the frozen shape worn EXACT on every workspace pose
        old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"
        try: Bw = CB.Bench(20, 20)
        finally:
            if old is None: os.environ.pop("CB_EXACT")
            else: os.environ["CB_EXACT"] = old
        Bw.idx = W.copy(); Bw.kind = ["ws"] * len(W); Bw.clip = ["Workspace (envelope)"] * len(W)
        Bw.poses = [dict(plane=float(x[0]), elev=float(x[1]), axial=float(x[2]), flex=float(x[3]), pron=float(x[4])) for x in POSE]
        Bw.res = [None] * len(W); Bw._skin = {}; Bw._ex = {}; Bw._frames = {}; Bw.grid = None; Bw._V = None; Bw.mode = "exact"; Bw.key = "wsall-mr"
        if which == "H1": Mw, _, _ = PV.frozen_on(fitB, Bw, P); Mw.run(); _, bad = V.extra_checks(Mw, Bw)
        else: Mw, _, _ = frozen_B(fitB, Bw, P); Mw.run(); _, bad = extra_checks_B(Mw, Bw)
        assert np.allclose(np.array(Mw.D.m)[:2], m[:2], atol=1e-6)
        for i in bad: Bw.res[i] = None
        nodes = np.array([Bw.res[i] is not None and float(np.min(Bw.res[i])) >= 0 for i in range(len(W))]); n_bad = len(bad)
        nodes_from = f"frozen shape worn exact on all {len(W)} workspace poses, verifier extra checks ({len(bad)} removed)"
        assert not (nodes & ~ok).any(), "a taken pose the kinematic check rejects"

    def flood(seed_ok):
        cn = np.zeros(len(W), bool); front = [i for i in range(len(W)) if nodes[i] and elev[i] == 0 and seed_ok(i)]; cn[front] = True
        while front:
            nxt = []
            for a in front:
                for b in nbrs(a):
                    if nodes[b] and not cn[b] and edge(a, b): cn[b] = True; nxt.append(b)
            front = nxt
        return cn
    seed_states = sorted(set(int(st[i]) for i in range(len(W)) if nodes[i] and elev[i] == 0))
    cnA = flood(lambda i: st[i] == 0)                        # strict: rest region = elevation 0 with K on stop A
    cn = flood(lambda i: True)
    isl = np.nonzero(nodes & ~cn)[0]
    bidx = np.asarray(CB._select(110, 360)[0]); Wl = W.tolist(); wpos = {g: k for k, g in enumerate(Wl)}
    bws = [wpos[int(g)] for g in bidx if int(g) in wpos]
    oh = POSE[:, 1] >= 140
    sname = {0: "A", 1: "stretched", -1: "folded"}
    out = dict(design=which, fit=fit, params=P, fold_margin=KIT.FOLD_MARGIN, m=[round(float(x), 4) for x in m], step_deg=STEP, jump_deg=JUMP,
               joints=("q1 q2 q3' pin_a pin_b" + ("" if which == "H1" else " dK")).split(), seed_states=[sname[s] for s in seed_states],
               nodes_from=nodes_from, connected_seedA=dict(grid=int(cnA.sum()), bench=int(cnA[bws].sum()), overhead140=int((cnA & oh).sum())),
               grid=dict(poses=len(W), nodes=int(nodes.sum()), connected=int(cn.sum()), islands=int(len(isl)),
                         static_reach=round(float(nodes.mean()), 4), connected_reach=round(float(cn.mean()), 4),
                         nodes_by_state={sname[s]: int((nodes & (st == s)).sum()) for s in (0, 1, -1)},
                         connected_by_state={sname[s]: int((cn & (st == s)).sum()) for s in (0, 1, -1)},
                         overhead140=dict(poses=int(oh.sum()), nodes=int((nodes & oh).sum()), connected=int((cn & oh).sum()))),
               bench110_360=dict(ws=len(bws), nodes=int(nodes[bws].sum()), connected=int(cn[bws].sum())),
               knee_branch_signs=sorted(set(sgn[nodes].tolist())),
               edges=dict(tested=n_edge[0], passed=n_edge[1], refused=why, jump_by_joint=dict(zip(out_j(which), jump_by.tolist()))),
               island_poses=[dict(plane=float(POSE[i, 0]), elev=float(POSE[i, 1]), axial=float(POSE[i, 2]), state=sname[int(st[i])]) for i in isl[:60]])
    out["connected_keys"] = [[float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])] for i in np.nonzero(cn if os.environ.get("MR_SEED_ANY") == "1" else cnA)[0]]
    out["connected_keys_seeds"] = "elevation 0 (any state)" if os.environ.get("MR_SEED_ANY") == "1" else "elevation 0, K on stop A (strict rest region)"
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in out if k not in ("params", "island_poses", "connected_keys")}, default=float)[:3000], flush=True)


def out_j(which): return ("q1 q2 q3' pin_a pin_b" + ("" if which == "H1" else " dK")).split()


if __name__ == "__main__":
    a = sys.argv[1:]; cj = None
    if "--conn" in a: k = a.index("--conn"); cj = a[k + 1]; del a[k:k + 2]
    if a[0] == "wear": wear(a[1], a[2], a[3], a[4], json.loads(a[5]) if len(a) > 5 else None, cj)
    elif a[0] in ("conn", "conn-taken"): conn(a[1], a[2], a[3], json.loads(a[4]) if len(a) > 4 else None, taken_mode=a[0] == "conn-taken")
    else: raise SystemExit(__doc__)
