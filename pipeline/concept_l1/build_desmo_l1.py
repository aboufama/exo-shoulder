"""L1 keep-out CAD of the generation-9 winner desmo-conecut-knuckle-3r (round 13's verified winner, not the lead: frozen exact
Bench(110,360) 18.98 / score 93.10 with the built groove's blended law in the IK, claim 19.04 linear-IK reproduced, held out 23.19,
complexity 16.5, ledger WATCH: docs/alignment/desmo-conecut-knuckle-3r.md) -> pipeline/full-exo/designs/<out>/ (exo.glb, clips.json,
workspace.json, design.json, parts_full.json, build.json).

desmo-conecut = the gen-8 lead conecut-knee-knuckle-3r (knee lE 97.1443 / lc 24.3508 / phiE 0.7526 / phib -91.8041, MR63ZZ pairs stk
6.0, J3 dowel stop [-111.9036, 122.7417]) with ONLY the K drive changed to desmo-slipper's spring-free, roller-free drive, stage 2
inverted (cell B):
  * NO clock spring (capK 0: a plain O20 cap on hub K); K slaved both ways, never read;
  * stage 1: a crowned O1.5 440C pin pressed in the crank's short arm (a_s 9.529, psi 149.71) runs in a 1.52 x 1.5 groove cut in
    the underside of a link-2 cap-ring sector on hub 2 (the groove centreline = the model's own blended law, built exactly as the
    model synthesises it: dwell + C1 blend over 10 deg of q2 + rise, cut at the slot's end);
  * stage 2 (inverted): an ISO 8734 O1.5 m6 440C nose dowel pressed radially in an O5 x 3 Ti boss on link 1a at the drive's seat C0
    (r_c 16.176 / beta -177.169), the boss rooted to hub K's rim; the 1.52-wide slot (the nose's path in the crank frame, 3.72 mm,
    closed end = stop A, far end = stop B at dK 46.5) wire-EDM'd through a 2.5 mm Ti tip plate on the crank's long arm
    (walls 0.9, plate 7.04 x 3.32 on the arm-tip layer R0 + 1.65);
  * the gen-7/8 flank lug band, the crank-borne nose, the hub-2 rim lobe and its follower are DELETED.

HOW: build_conecut_l1.py (gen 8) is IMPORTED unchanged (it imports build_slipper_l1.py unchanged and adds the J3 stop, the D1-D3 /
O3 / O4 fixes and the gen-8 check poses). The model is the VERIFIER's: docs/concepts/verify/desmo-conecut-knuckle-3r.py loaded with
--blend (BlendDesign IK + the linear-part groove calibration = the verified 18.98 wear), its DCModel on the row's best_params, fit on
Bench(60,160) FAST (= DS._frozen_model's hand-over). Every gen-7/8 part is built by the gen-7 builder from THIS model's fitted shape;
this file swaps the drive (drive_parts), relabels hub K's cap, adds the drive's own checks (groove / slot vs the posed members, K
play into th, the cap-ring sector vs hub 2's O20 and its stack layer) and writes the slaved law (blended, form closure) for R17.

    OMP_NUM_THREADS=1 nice -n 15 python3 pipeline/concept_l1/build_desmo_l1.py [--out l1_desmo-conecut] [--jobs 1] [--no-clips]
    ... --post-only     (re-run the post-processing on an existing build)
"""
import json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
os.environ["SN_CELL"] = "lead"
os.environ.pop("CB_EXACT", None)                                                # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_conecut_l1 as CCL                                                  # noqa: E402  (gen-8 L1 builder, imported unchanged)
SL, MIN, BASE = CCL.SL, CCL.MIN, CCL.BASE; CB, REF = BASE.CB, BASE.REF
_argv = list(sys.argv); sys.argv = _argv + ["--blend"]                          # the verifier's B1: the blended law in the IK
try: V = MIN._load("desmoconecut_verify_for_l1", os.path.join(REPO, "docs", "concepts", "verify", "desmo-conecut-knuckle-3r.py"))
finally: sys.argv = _argv
assert V.BLEND, "the verifier's blended IK did not load"
DC = V.DC; DS = DC.DS; RF = DS.RF; S = DC.S; unit = S.unit
UP, CROWN, T_LINK, RUNG = S.UP, S.CROWN, S.T_LINK, SL.RUNG

ID = "desmo-conecut-knuckle-3r"
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
PFULL = DC._clamp(dict(DC.PARAMS, **BEST))                                     # the verified config (the verifier's: PARAMS + BEST)
CFG = dict(BEST); CFG["ang_min"] = float(PFULL["ang_min"])
J3MIN, J3MAX = float(PFULL["J3MIN"]), float(PFULL["J3MAX"])
GW, RW, PIN_D, ARM_W = DS.GROOVE_W, DS.RING_WALL, DS.PIN_D, DS.ARM_W            # groove 1.52, ring wall 0.8, pin O1.5, short arm 3 wide
GD, ROOF = 1.5, 0.8                                                             # groove depth, the ring's roof over it
S1_T = 1.5                                                                      # short arm thickness (Ti), top RUNG under the ring
PLATE_T = 2.5                                                                   # tip plate radial thickness (the model's plate_edge + 2.5)
NOSE_LO, NOSE_TIP_CLR = -1.0, 0.15                                              # nose dowel: from C0 - 1.0 (2.5 mm in the boss) to the plate top - 0.15
VERIFIED = dict(bench=dict(gap=18.98, score=93.10, reach=0.7278, follow=1.0, inband14=0.8930, inband10=0.5629, contact=0.0106, overhead="8/28"),
                claim_linear_ik=dict(gap=19.04, score=93.08), held=dict(gap=23.19, score=91.57, reach=0.6922, inband14=0.8919, contact=0.016, overhead="18/71"),
                th_margin=dict(bench_min=5.181, held_min=5.006, dth_dK_at_min=0.403, k_play_nominal_deg=0.227, k_play_worst_tol_deg=0.281,
                               held_min_with_play=[round(5.006 - 0.403 * 0.227, 3), round(5.006 - 0.403 * 0.281, 3)]),
                groove_scan=dict(crank_free_worst_deg=0.187, at_K=44.0, held_slot_slop_deg=0.04), mu_claim="0.15 nominal only (a_s +0.07 mm binds stage 1 at K 44.75)",
                complexity=16.5, ledger="WATCH (docs/alignment/desmo-conecut-knuckle-3r.md)", harness="docs/concepts/verify/desmo-conecut-knuckle-3r.py --blend",
                dumps=["docs/concepts/verify/desmo-conecut-knuckle-3r_v_bench_frozen_blend.json", "docs/concepts/verify/desmo-conecut-knuckle-3r_v_held_frozen_blend.json"])

# --- the fits table: gen-8's (D1-D3, J3 stop, knee stop) minus the slipper-nose / lobe / clock-spring lines, plus the desmo drive's
_DROP = ("nose dowel in the crank arm", "conjugate flank on link 1a", "lobe follower", "slipper nose / DLC flank wear test", "K-phase band")
FITS = [dict(f) for f in CCL.FITS if not f["where"].startswith(_DROP)]
FITS += [
    dict(where="stage-1 pin in the crank's short arm", fit="ISO 8734 1.5 m6 440C (58 HRC), pressed H7/m6 through the 1.5 mm Ti short arm along u2 (the dwell "
         "pose), protruding 1.40 into the groove, tip 0.10 off the groove roof; crowned (the pin tilts up to 4.76 deg across the groove): crown radius >= 8 mm "
         "on the running band, Ra <= 0.1, true position of the pin to the crank bore 0.01 (a_s 9.529 +-0.02: +0.07 mm binds stage 1 at K 44.75 at mu 0.15 - "
         "the verifier's cliff)"),
    dict(where="stage-1 groove in hub 2's cap-ring sector (link 2)", fit="1.52 +0.01/0 wide x 1.50 +0.05/0 deep (pin play 0.01 per side nominal, 0.015 worst) in a "
         "pressed 440C ring insert (Hertz ~1.5 GPa at 25 N on the 0.25 mm ridge at the onset blend: Ti alone yields), walls 0.8; centreline = the model's "
         "blended law (C1 quadratic over 10 deg of q2), profile +-0.005 to the J2 bore; 5-axis milled with an O1.5 ball/flat end mill, then lapped"),
    dict(where="stage-2 nose dowel in link 1a's boss", fit="ISO 8734 1.5 x 5 m6 440C, pressed H7/m6 radially in the O5 x 3 Ti boss (2.5 mm engagement), true "
         "position 0.01 to hub K's bore and link 1a's angular datum (seat r_c 16.176: r_c 15.95-16.05 flat on the fast bench), Ra <= 0.1"),
    dict(where="stage-2 slot in the crank's tip plate", fit="wire-EDM through the 2.5 mm Ti plate, width 1.52 +0.01/0 (nose play 0.01 per side), the nose's path "
         "Z = Rc^T Rk^T C0 to +-0.005, closed end = stop A (the relative pole, 0.525 mm/rad), far end = stop B at dK 46.5 +-0.25 (the slot's end; held "
         "stroke 46.27); walls 0.9; plate-to-hub-K clearance >= 1.0 (model 1.23: a 0.25 mm pivot error toward the K axis takes it to 1.0)"),
    dict(where="desmo drive wear test", fit="pass line: stage-1 forward PA bind not before K 46.5 at the measured mu after a wear run (nominal claim mu 0.15; the drive's "
         "own PA gate 43 - atan(mu) = 34.47); re-run the groove scan and R17 at mu 0.087 / 0.12 / 0.15 / 0.17"),
    dict(where="K free play (no spring preload)", fit="slot slop with the crank held 0.04 deg + stage-1 crank-free play 0.187 deg (dense scan, K 44) = 0.227 deg "
         "nominal / 0.281 at the worst groove tolerance; carried into the fold margin th at dth/dK 0.403: held-out min 5.006 -> 4.915 / 4.893 (WATCH: "
         "below the 5.0 rule by 0.09-0.11 deg at 2 held poses' worst case); bench min 5.181 -> 5.09 (holds)"),
]
GROUPS = SL.GROUPS


# ---------------------------------------------------------------------------------------------------- the verified model
class L1Model(DC.DCModel):
    """the verifier's DCModel (blended IK, J3 stop applied before fit / run); once fitted (self._l1), the crank (9) frame comes from the K
    opening read off the CURRENT member frames X[1], X[7] through the model's own law (gen-7/8 L1Model's hook, copied)"""
    def T(self, m, i):
        if m in (8, 9) and getattr(self, "_l1", False):
            X7 = self.X[7][0]; c = getattr(self, "_l1c", None)
            if c is None or c[0] is not X7: self._l1c = (X7, self._drive_frames(self.X[1][0], X7))
            Rb, tb = self._l1c[1][m]; R7, t7 = self.X[7][0][i], self.X[7][1][i]
            return R7 @ Rb[i], R7 @ tb[i] + t7
        return super().T(m, i)

    def dK_of(self, X1, X7):
        from scipy.spatial.transform import Rotation as Rot
        RK = np.einsum("nji,njk->nik", X1, X7); bad = ~np.isfinite(RK).all(axis=(1, 2)); RK[bad] = np.eye(3)
        return Rot.from_matrix(RK).as_rotvec() @ self._scg["uK"]

    def _drive_frames(self, X1, X7):
        save = (self.dK, self._sc); self.dK = self.dK_of(X1, X7); self._sc = None
        try: self._sc_pose(); X = self._sc["X"]
        finally: self.dK, self._sc = save
        return X


def fit():
    """the verifier's model on the verified config, fit on Bench(60,160) FAST = DS._frozen_model's hand-over"""
    B = CB.Bench(60, 160); P = DC._clamp(dict(DC.PARAMS, **BEST)); M = L1Model(B, P); r = M.run()
    a = DC.PK.audit(M, B); r["gap_near1"] = a.get("gap_near1"); r["gap_near2"] = a.get("gap_near2"); r["near_touch_min_mm"] = a.get("near_touch_min_mm")
    r["desmo_fail"] = list(getattr(M, "_desmo_fail", []) or []); r["blend_ik"] = dict(V._BL)
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q); M._l1 = True; M._l1c = None
    return M, r


# ---------------------------------------------------------------------------------------------------- the desmo drive geometry (the model's own)
def desmo_geom(M):
    """stage-1 groove centreline in link 2's home frame and stage-2 slot path in the crank's home frame, re-derived from the fitted model
    exactly as DCModel._desmo_build_B builds them (same calibration, blend, law, cut at dK_lim)"""
    D = M.D; P = D.p; g = M._scg; ds = M._desmo; s2 = M._s2B
    dR, uK, sp, sig, gg, cc = g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0); kgrid = g["kgrid"]; lim = float(g["dK_lim"])
    u2 = D.u[1]; F0, hmid, s_th, q_on = ds["F0"], ds["hmid"], ds["s_th"], ds["q_on"]; bx, by = ds["bx"], ds["by"]
    s_th_, q_on_, q_lo, q_hi, rms, nmv = M._calib()
    assert abs(s_th_ - s_th) < 1e-9 and abs(q_on_ - q_on) < 1e-9, (s_th_, s_th, q_on_, q_on)
    bw = math.radians(float(P["blend"])); sa = max(abs(s_th), 1e-6)
    x_lo = min((q_lo - q_on) / s_th, (q_hi - q_on) / s_th, 0.0) - math.radians(5.0) / sa
    x = np.arange(x_lo, lim + 1e-9, math.radians(0.05) / sa); qs = q_on + s_th * x
    hb = bw / abs(s_th) / 2.0 if bw > 0 else 0.0
    Kb = np.where(x <= -hb, 0.0, np.where(x >= hb, x, (x + hb) ** 2 / (4 * hb))) if hb > 0 else np.maximum(x, 0.0)
    Kb = np.minimum(Kb, lim)
    Cq = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)), F0)
    G2m = np.einsum("nij,nj->ni", S.rotm(u2, -(qs - q_on)), Cq)                  # the model's ring frame (azimuth origin at the onset)
    G2 = np.einsum("nij,nj->ni", S.rotm(u2, -qs), Cq)                              # link 2's TRUE member-local frame (q2 = R_L1b^T R_L2 about u2)
    bx = unit(G2[0] - (G2[0] @ u2) * u2); by = np.cross(u2, bx)
    az = np.unwrap(np.arctan2(G2 @ by, G2 @ bx)); rho = np.linalg.norm(G2 - np.outer(G2 @ u2, u2), axis=1); z = G2 @ u2 - hmid
    # stage 2: the nose (link 1a, C0) path in the crank frame
    C0, R0 = s2["C0"], s2["R0"]; kp = np.radians(np.arange(0.0, math.degrees(lim) + 1e-9, 0.05))
    Xp = np.einsum("nji,j->ni", S.rotm(uK, sp * kp), C0); Z = np.einsum("nji,nj->ni", S.rotm(dR, sig * RF.phi_of(kp, gg, cc)), Xp)
    nr2, cs2, wl2 = float(P["nose_r2"]), float(P["c_slot2"]), float(P["wall2"])
    U, C, F4, hr = MIN.joints4(M); H2 = float((C[2] + F4[2] * U[2]) @ u2)
    return dict(G2_model=G2m, q_on_deg=math.degrees(q_on), u2=u2, bx=bx, by=by, hmid=hmid, F0=F0, s0=ds["s0"], dR=dR, uK=uK, x=x, Kb=Kb, qs=qs, G2=G2, az=az, rho=rho, z=z, lim=lim, r_out=ds["r_out"],
                C0=C0, R0=R0, rL=s2["rL"], rb=s2["rb"], rK0=s2["rK0"], kp=kp, Z=Z, nr2=nr2, cs2=cs2, wl2=wl2, hw_in=nr2 + cs2, hw_out=nr2 + cs2 + wl2,
                rPu=R0 + 1.5 + RUNG, H2=H2, lvK=float(M.fK) + float(P["hl"]), q_lo=q_lo, q_hi=q_hi, s_th=s_th, q_on=q_on, hb=hb)


def _quads_to_tris(nI, nJ, keep):
    """triangles of a structured (nI x nJ) node grid, cell (i, j) kept where keep[i, j]"""
    F = []
    for i in range(nI - 1):
        for j in range(nJ - 1):
            if not keep[i, j]: continue
            a, b, c, d = i * nJ + j, (i + 1) * nJ + j, (i + 1) * nJ + j + 1, i * nJ + j + 1
            F += [[a, b, c], [a, c, d]]
    return np.array(F, int)


def extrude_map(V2, F2, to_bot, to_top):
    """closed solid from a 2D triangle mesh (holes allowed): bottom = to_bot(V2), top = to_top(V2) (per-vertex maps), side walls on the
    boundary edges (MIN.extrude2d generalised to a radial / any per-vertex extrusion)"""
    V2 = np.asarray(V2, float); F2 = np.asarray(F2, int).copy()
    d1, d2 = V2[F2[:, 1]] - V2[F2[:, 0]], V2[F2[:, 2]] - V2[F2[:, 0]]; ar = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]; F2[ar < 0] = F2[ar < 0][:, ::-1]
    n = len(V2); V = np.r_[to_bot(V2), to_top(V2)]; F = [F2[:, ::-1], F2 + n]
    E = np.r_[F2[:, [0, 1]], F2[:, [1, 2]], F2[:, [2, 0]]]; key = np.sort(E, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True); Eb = E[cnt[inv.ravel()] == 1]
    a, b = Eb[:, 0], Eb[:, 1]; F += [np.c_[a, b, b + n], np.c_[a, b + n, a + n]]
    m = trimesh.Trimesh(V, np.concatenate(F), process=True)
    if m.is_watertight and m.volume < 0: m.invert()
    return m


def ring_parts(M, G):
    """the link-2 cap-ring sector on hub 2 (member-2 home frame): groove layer (hmid -0.75 .. +0.75, the groove cut through it) + roof
    (to hub 2's upper boss F+UP+0.5, so the sector is one with link 2's upper boss); planform in polar (r, az) about u2: inner wall
    rho - GW/2 - RW .. outer r_out (the model's), az over the used groove +- 3 deg (the model's sector)"""
    from scipy.spatial import cKDTree
    u2, bx, by = G["u2"], G["bx"], G["by"]; used = G["Kb"] <= G["lim"] + 1e-12
    az, rho = G["az"][used], G["rho"][used]
    mono = bool(np.all(np.diff(az) * np.sign(az[-1] - az[0]) > -1e-9))
    P2 = np.c_[rho * np.cos(az), rho * np.sin(az)]; Tp = cKDTree(P2)                    # the groove centreline (link 2 local, polar plane)
    # the sector: the model samples the used groove azimuths +- 3 deg; a buildable ring closes the groove's round ends with the ring wall RW, i.e.
    # asin((GW/2 + RW) / rho_end) + 0.5 deg past each end (the +-3 deg sector would cut the groove's end discs through: two pieces)
    i0, i1 = int(np.argmin(az)), int(np.argmax(az)); hw = GW / 2
    m0 = math.asin(min(1.0, (hw + RW) / float(rho[i0]))) + math.radians(0.5); m1 = math.asin(min(1.0, (hw + RW) / float(rho[i1]))) + math.radians(0.5)
    a0, a1 = float(az.min()) - max(m0, math.radians(3)), float(az.max()) + max(m1, math.radians(3)); nA = max(80, int(math.degrees(a1 - a0) * 4))
    A = np.linspace(a0, a1, nA); r_out = float(G["r_out"]); hw = GW / 2; rr = np.arange(DS.BORE_R - 1.0, r_out, 0.005)
    glo, ghi, has = np.zeros(nA), np.zeros(nA), np.zeros(nA, bool)
    for j, a in enumerate(A):                                                           # the groove's radial extent at this azimuth: points within hw of the path
        d, _ = Tp.query(np.c_[rr * math.cos(a), rr * math.sin(a)]); inn = d < hw
        if inn.any(): has[j] = True; glo[j], ghi[j] = rr[inn].min(), rr[inn].max()
    jj = np.nonzero(has)[0]; glo[: jj[0]] = glo[jj[0]]; ghi[: jj[0]] = ghi[jj[0]]; glo[jj[-1] + 1:] = glo[jj[-1]]; ghi[jj[-1] + 1:] = ghi[jj[-1]]
    rin = np.minimum(DS.BORE_R, glo - 0.15)
    nodes = np.stack([rin, glo, ghi, np.full(nA, r_out)], 1)                           # (nA, 4)
    V2 = np.array([[r * math.cos(a), r * math.sin(a)] for a, row in zip(A, nodes) for r in row])
    keep_g = np.ones((nA - 1, 3), bool); keep_g[:, 1] = ~(has[:-1] & has[1:])          # groove layer: the groove cell cut where the groove runs
    keep_r = np.ones((nA - 1, 3), bool); rc = 0.5 * (glo + ghi)
    to3 = lambda h: (lambda P2: P2[:, :1] * bx + P2[:, 1:] * by + h * u2)
    lv = G["hmid"] - GD / 2; top = G["H2"] + UP + 0.5
    groove = extrude_map(V2, _quads_to_tris(nA, 4, keep_g), to3(lv), to3(lv + GD))
    roof = extrude_map(V2, _quads_to_tris(nA, 4, keep_r), to3(lv + GD), to3(max(top, lv + GD + ROOF)))
    info = dict(level_from_hub2_face_mm=[round(lv - G["H2"], 3), round(lv + GD - G["H2"], 3), round(max(top, lv + GD + ROOF) - G["H2"], 3)],
                groove_mid_from_hub2_face_mm=round(G["hmid"] - G["H2"], 3), pitch_mm=[round(float(rho.min()), 3), round(float(rho.max()), 3)],
                inner_wall_r_mm=round(float(rin.min()), 3), groove_r_mm=[round(float(glo[has].min()), 3), round(float(ghi[has].max()), 3)], r_out_mm=round(r_out, 3), past_O20_mm=round(r_out - S.HUB_R, 3),
                sector_deg=round(math.degrees(a1 - a0), 2), model_sector_deg=round(math.degrees(float(az.max() - az.min())) + 6.0, 2),
                end_margins_deg=[round(math.degrees(max(m0, math.radians(3))), 2), round(math.degrees(max(m1, math.radians(3))), 2)], groove_az_deg=round(math.degrees(float(az[-1] - az[0])), 2), az_monotone=mono,
                drift_mm=round(float(np.abs(G["z"][used]).max()), 3), azimuth_deg=[round(math.degrees(a0), 2), round(math.degrees(a1), 2)],
                note=("the groove's mid-plane sits at the crank pivot's level + 3.15 + glev along u2 (the model's rule); the pivot is "
                      f"{G['H2'] - float(M._scg['PV'] @ u2):.2f} mm below hub 2's face, so the groove layer lands at F+{lv - G['H2']:.2f}..F+{lv + GD - G['H2']:.2f}: "
                      "INSIDE link 1b's J2 lower-plate layer (F+0..F+3, O20) - the stack conflict this L1 reports (R6)"))
    return groove, roof, info


def stage1_parts(M, G):
    """the crank's short arm (3 x 1.5 Ti, from the crank axis to the pin, top RUNG under the ring) and the crowned O1.5 pin (crank frame)"""
    u2, F0, dR = G["u2"], G["F0"], G["dR"]; A0 = G["s0"] * dR
    lv_ring = G["hmid"] - GD / 2; top = lv_ring - RUNG; bot = top - S1_T
    al = F0 - A0; al = unit(al - (al @ u2) * u2); ac = np.cross(u2, al)
    L = float(np.linalg.norm((F0 - A0) - ((F0 - A0) @ u2) * u2))
    c = A0 + ((bot + top) / 2 - float(A0 @ u2)) * u2 + ((L + 1.5) - 1.0) / 2 * al
    c = A0 + ((bot + top) / 2 - float(A0 @ u2)) * u2 + (SL.ARM_ROOT + L + 1.5) / 2 * al   # from ARM_ROOT (inside the O10 boss wall, bore free) to 1.5 past the pin
    arm = REF.box(c, np.stack([al, ac, u2], 1), [L + 1.5 - SL.ARM_ROOT, ARM_W, S1_T])
    pin = REF.cyl(F0, u2, bot - float(F0 @ u2), (G["hmid"] + GD / 2 - 0.10) - float(F0 @ u2), r=PIN_D / 2)
    return arm, pin, dict(arm_len_mm=round(L + 1.5 - SL.ARM_ROOT, 2), arm_level_from_hub2_face_mm=[round(bot - G["H2"], 3), round(top - G["H2"], 3)], a_s=round(L, 3),
                          pin_from_hub2_face_mm=[round(bot - G["H2"], 3), round(G["hmid"] + GD / 2 - 0.10 - G["H2"], 3)],
                          pin_into_groove_mm=round(GD - 0.10, 2), crank_axis_at_arm_u2_level_mm=round(float(A0 @ u2) - G["H2"], 3))


def tip_plate(M, G, n_path=40, n_cap=9):
    """the crank's tip plate (crank frame): stadium annulus of half-widths hw_in (the slot) / hw_out (the walls) around the nose path Z,
    radially extruded from R0 + 1.65 to + PLATE_T (exact: every point on rays from GH, like the model's plate samples)"""
    Z = G["Z"]; jl = len(Z) - 1; zc = Z[jl // 2]; nrm = unit(zc); e = unit(Z[-1] - Z[0]); e = unit(e - (e @ nrm) * nrm); f = np.cross(nrm, e)
    P2 = np.c_[(Z - zc) @ e, (Z - zc) @ f]; L = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(P2, axis=0), axis=1))]
    s = np.linspace(0.0, L[-1], n_path); C2 = np.c_[np.interp(s, L, P2[:, 0]), np.interp(s, L, P2[:, 1])]
    T2 = np.gradient(C2, axis=0); T2 /= np.linalg.norm(T2, axis=1)[:, None]; N2 = np.c_[-T2[:, 1], T2[:, 0]]

    def contour(h):
        right = [C2[k] - h * N2[k] for k in range(n_path)]
        capE = [C2[-1] + h * (math.cos(t) * T2[-1] + math.sin(t) * N2[-1]) for t in np.linspace(-math.pi / 2, math.pi / 2, n_cap)][1:-1]
        left = [C2[k] + h * N2[k] for k in range(n_path - 1, -1, -1)]
        capS = [C2[0] + h * (math.cos(t) * (-T2[0]) + math.sin(t) * (-N2[0])) for t in np.linspace(-math.pi / 2, math.pi / 2, n_cap)][1:-1]
        return np.array(right + capE + left + capS)
    ci, co = contour(G["hw_in"]), contour(G["hw_out"]); nC = len(ci)
    V2 = np.r_[ci, co]; F2 = []
    for k in range(nC):
        k2 = (k + 1) % nC; F2 += [[k, k2, nC + k2], [k, nC + k2, nC + k]]
    to3 = lambda r: (lambda Q: unit(zc[None] + Q[:, :1] * e + Q[:, 1:] * f) * r)
    m = extrude_map(V2, np.array(F2), to3(G["rPu"]), to3(G["rPu"] + PLATE_T))
    return m, dict(slot_len_mm=round(float(L[-1]), 3), slot_w_mm=round(2 * G["hw_in"], 3), plate_w_mm=round(2 * G["hw_out"], 3),
                   plate_len_mm=round(float(L[-1]) + 2 * G["hw_out"], 3), radial_mm=[round(G["rPu"], 3), round(G["rPu"] + PLATE_T, 3)],
                   frame=dict(zc=zc, e=e, f=f, C2=C2, N2=N2))


def trim_arm(dg, G, zb, clr=0.3):
    """the gen-7 bent arm (SL.arm_mesh) with its arc ending before the slot: the last arc rows whose 6-mm section would cover the slot
    (any row point within hw_in + clr of the nose path, crank frame) are dropped, and the arm ends ON the plate (the plate's wall carries
    it). The ARM_END overrun past the old roller axis is not built (the plate is the tip)."""
    from scipy.spatial import cKDTree
    T = cKDTree(G["Z"]); arc = dg["arc"]; keep = len(arc)
    while keep > 0:
        row = arc[keep - 1]; X = np.r_[row, row + T_LINK * row / np.linalg.norm(row, axis=1)[:, None]]
        X = np.r_[X, 0.5 * (X[:-1] + X[1:])]; X = unit(X) * G["R0"]                   # on the nose path's sphere: the nose is a radial pin
        if float(T.query(X)[0].min()) > G["hw_in"] + clr: break
        keep -= 1
    psi = dg["psi"]                                                               # arc[k] <-> psi[k + 1]
    def ok(a):
        row = dg["arc_row"](a); X = np.r_[row, row + T_LINK * row / np.linalg.norm(row, axis=1)[:, None]]; X = np.r_[X, 0.5 * (X[:-1] + X[1:])]; X = unit(X) * G["R0"]
        return float(T.query(X)[0].min()) > G["hw_in"] + clr
    lo = psi[keep]; hi = psi[keep + 1] if keep + 1 < len(psi) else dg["beta"]
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if ok(mid): lo = mid
        else: hi = mid
    dg2 = dict(dg); dg2["arc"] = arc[:keep]; dg2["beta"] = lo if abs(lo - psi[keep]) > 1e-4 else psi[keep] + 1e-3 * dg["sgn_b"]
    ext_save = SL.ARM_END; SL.ARM_END = 0.0
    try: m, info = SL.arm_mesh(dg2, zb)
    finally: SL.ARM_END = ext_save
    Xs = unit(np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 6000, seed=17)[0]]) * G["R0"]
    info.update(arc_rows_kept=int(keep), arc_rows_model=int(len(arc)), arm_to_slot_path_mm=round(float(T.query(Xs)[0].min()), 3),
                ends_at_beta_deg=round(math.degrees(dg2["beta"]), 3), note="the arc ends where its section clears the slot by >= 0.3 mm; the tip plate joins it")
    return m, info


def boss_parts(M, G):
    """link 1a's nose boss (O 2 boss_r x 3, radial at C0 on the sphere R0 - 1.5) and its root strip from hub K's rim (4 x 3 Ti, the model's
    underside rule: level lvK at the rim rising to the boss underside)"""
    C0, rL, rb, uK = G["C0"], G["rL"], G["rb"], G["uK"]; cr = unit(C0)
    boss = REF.cyl(C0, cr, -1.5, 1.5, r=rb)
    db = unit(C0 - (C0 @ uK) * uK); wb = unit(np.cross(uK, db)); rK0 = G["rK0"]; lvK = G["lvK"]; rows = []
    rs = np.r_[np.arange(S.HUB_R + RUNG, rK0, 1.0), rK0]                            # starts RUNG outside hub K's O20: inside it the root (F+1.94..4.94) would cross
                                                                                    # link 1b's K upper boss (F+3.15..): -0.24 mm on the first build's drive sweep
    for r_ in rs:
        row = []
        for w_ in np.linspace(-(rb - 0.5), rb - 0.5, 5):
            x_ = uK * lvK + r_ * db + w_ * wb; t_ = min(max((r_ - S.HUB_R) / max(rK0 - S.HUB_R, 1e-6), 0.0), 1.0)
            row.append(unit(x_) * ((1 - t_) * float(np.linalg.norm(x_)) + t_ * rL))
        rows.append(row)
    Bot = np.array(rows); Off = T_LINK * Bot / np.linalg.norm(Bot, axis=2)[:, :, None]
    root = SL._outward(REF.grid_solid(Bot, Off))
    nose = REF.cyl(C0, cr, NOSE_LO, (G["rPu"] + PLATE_T - NOSE_TIP_CLR) - G["R0"], r=G["nr2"])
    return boss, root, nose, dict(boss_d_mm=2 * rb, boss_radial_mm=[round(rL, 3), round(rL + 3.0, 3)], boss_rK_mm=round(rK0, 3),
                                  boss_to_hubK_rim_mm=round(rK0 - rb - S.HUB_R, 3), root_w_mm=round(2 * (rb - 0.5), 2),
                                  nose_radial_from_C0_mm=[NOSE_LO, round((G["rPu"] + PLATE_T - NOSE_TIP_CLR) - G["R0"], 3)], nose_d_mm=2 * G["nr2"])


def drive_parts(M, lg, dg):
    """[(group, member, name, mesh, material)] of the desmo cell-B drive + its info (replaces SL.drive_parts)"""
    D = M.D; P = D.p; G = desmo_geom(M); dg["desmo"] = G; out = []; dR = dg["dR"]; zb = dg["zboss_built"]
    groove, roof, rinfo = ring_parts(M, G)
    out.append(("l2", 2, f"drive cap-ring groove layer keep-out (link 2's cap-ring sector on hub 2, {rinfo['sector_deg']:.1f} deg, r {rinfo['inner_wall_r_mm']:.2f}..{rinfo['r_out_mm']:.2f} "
                f"({rinfo['past_O20_mm']:.2f} past O20), F+{rinfo['level_from_hub2_face_mm'][0]:.2f}..F+{rinfo['level_from_hub2_face_mm'][1]:.2f}: the stage-1 groove {GW:g} x {GD:g} "
                f"cut through it on the model's blended law, pressed 440C insert)", groove, "steel"))
    out.append(("l2", 2, f"drive cap-ring roof keep-out (the sector over the groove, F+{rinfo['level_from_hub2_face_mm'][1]:.2f}..F+{rinfo['level_from_hub2_face_mm'][2]:.2f}, "
                f"one with hub 2's upper boss)", roof, "ti"))
    out.append(("dk", 9, f"drive bell crank boss keep-out (O10 x {SL.BOSS_H:g} mm, bore O{2 * SL.BORE_R:.1f} on the O3 pivot pin, two MR63ZZ 3x6x2.5 inside; "
                f"underside {zb:.2f} mm from GH = link 1b's highest top under its footprint + {RUNG:g}; the model's {dg['zboss']:.2f})", SL.tube(np.zeros(3), dR, zb, zb + SL.BOSS_H, 5.0, SL.BORE_R), "ti"))
    am, ainfo = trim_arm(dg, G, zb)
    out.append(("dk", 9, f"drive bell crank bent arm keep-out (6 x {T_LINK:g} mm Ti: straight run {dg['Lch']:.1f} mm, tangent arc r_c {dg['rc']:.2f} about hub K's axis "
                f"at radius {dg['rA']:.2f} from GH, ending on the tip plate clear of the slot)", am, "ti"))
    pl, pinfo = tip_plate(M, G)
    out.append(("dk", 9, f"drive crank tip plate keep-out ({pinfo['plate_len_mm']:.2f} x {pinfo['plate_w_mm']:.2f} x {PLATE_T:g} Ti, R0+1.65: the stage-2 slot "
                f"{pinfo['slot_w_mm']:.2f} x {pinfo['slot_len_mm']:.2f} wire-EDM'd through it on the nose's path; closed end = stop A, far end = stop B at dK {math.degrees(G['lim']):.1f})", pl, "ti"))
    arm1, pin1, sinfo = stage1_parts(M, G)
    out.append(("dk", 9, f"drive crank short arm keep-out ({sinfo['arm_len_mm']:.1f} x {ARM_W:g} x {S1_T:g} Ti, crank axis -> the stage-1 pin at a_s {sinfo['a_s']:.2f}, "
                f"top {RUNG:g} under the cap ring)", arm1, "ti"))
    out.append(("dk", 9, f"drive stage-1 pin keep-out (ISO 8734 1.5 m6 440C, crowned, pressed through the short arm along u2, {GD - 0.10:.2f} into the groove)", pin1, "steel"))
    boss, root, nose, binfo = boss_parts(M, G)
    out.append(("l1a", 1, f"drive nose boss keep-out (link 1a: O{2 * G['rb']:g} x 3 Ti radial at the seat C0, r_c {G['rK0']:.2f} from hub K's axis, {binfo['boss_to_hubK_rim_mm']:.2f} "
                f"outside hub K's O20)", boss, "ti"))
    out.append(("l1a", 1, f"drive nose boss root keep-out (link 1a: {binfo['root_w_mm']:g} x 3 Ti from hub K's rim to the boss)", root, "ti"))
    out.append(("l1a", 1, f"drive nose dowel keep-out (ISO 8734 1.5 x 5 m6 440C, pressed radially in link 1a's boss, C0{NOSE_LO:+g}..C0+{binfo['nose_radial_from_C0_mm'][1]:.2f}: "
                f"runs in the crank's slot, {NOSE_TIP_CLR:g} under the plate top)", nose, "steel"))
    lev = dg["lev"]
    out.append(("l1b", 7, f"drive crank pivot pin keep-out (O3 h6 hardened, pressed in link 1b's strap {lev:.1f}..{lev + T_LINK:.1f}, through the boss)",
                REF.cyl(np.zeros(3), dR, lev, zb + SL.BOSS_H + RUNG + SL.CLIP_H, r=SL.PIN_R), "steel"))
    out.append(("l1b", 7, f"drive crank pin clip keep-out (DIN 6799 RS 2.3, O6 x {SL.CLIP_H:g} over the boss top + {RUNG:g})",
                SL.tube(np.zeros(3), dR, zb + SL.BOSS_H + RUNG, zb + SL.BOSS_H + RUNG + SL.CLIP_H, 3.0, SL.PIN_R - 0.05), "steel"))
    info = getattr(M, "_sc_info", {}) or {}
    return out, dict(drive_cell="desmo cell B", ring=rinfo, arm=ainfo, plate={k: v for k, v in pinfo.items() if k != "frame"}, stage1=sinfo, boss=binfo,
                     boss_level_mm=round(zb, 3), seat_C0_mm=np.round(G["C0"], 3).tolist(), seat_R0_mm=round(G["R0"], 3), r_c=dg["rc"],
                     beta_deg=round(math.degrees(dg["beta"]), 3), g=dg["g"], sig=dg["sig"], dK_lim_deg=round(math.degrees(G["lim"]), 3),
                     mu=float(P.get("mu", 0.0)), cam={k: info.get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken", "pa_eff_horn", "pa_eff_crank",
                                                                               "friction_deg", "pa_kin_max")},
                     desmo=info.get("desmo"))


# ---------------------------------------------------------------------------------------------------- hooks into the gen-7/8 builder
_bp_cc = CCL.build_parts
_jt0 = CCL.j3_tolerance
CCL.j3_tolerance = lambda: dict(_jt0(), linear_deg=_jt0()["worst_out_deg"])     # CCL.build_parts prints 'linear_deg' (its table names it worst_out_deg)


def build_parts(M, lg, dg, knee_geom=None):
    parts, stack = _bp_cc(M, lg, dg, knee_geom)
    for k, p in enumerate(parts):
        if p[2].startswith("K upper boss + clock-spring cap"):
            parts[k] = (p[0], p[1], f"K upper boss + cap keep-out (O20, F+{UP:.2f}..F+{CROWN:.2f}, link 1b: NO clock spring - K is held both ways by the desmo drive, "
                                    "slaved to q2, never read)", p[3], p[4])
    return parts, stack


def set_adjacent(parts):
    CCL.set_adjacent(parts)
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None)
    pairs = [("drive crank tip plate", b) for b in ("K upper boss", "K lower plate", "drive nose boss", "link 1a strap", "J2 upper boss", "link 1b strap")] + \
            [("drive crank short arm", b) for b in ("J2 upper boss", "drive cap-ring", "link 2 strap", "J2 lower plate")] + \
            [("drive stage-1 pin", b) for b in ("J2 upper boss", "drive cap-ring roof")] + \
            [("drive cap-ring groove layer", b) for b in ("link 1b strap", "drive bell crank boss", "drive bell crank bent arm")] + \
            [("drive cap-ring roof", b) for b in ("link 1b strap", "drive bell crank boss", "drive bell crank bent arm")] + \
            [("drive nose boss", b) for b in ("drive bell crank bent arm", "link 1b strap", "K upper boss")] + \
            [("drive nose dowel", b) for b in ("drive crank tip plate", "drive bell crank bent arm")]
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1]: continue
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def law_check(M, K, idx, dg):
    """per pose from the posed member frames: K vs the blended law (the slaved declaration's table) and the two cam closures in the world:
    stage 2 = the nose (link 1a, C0) read in the crank's posed frame vs the slot path Z at that |dK| (mm); stage 1 = the pin (crank, F0) read
    in link 2's posed frame vs the groove centreline, nearest point (mm)"""
    from scipy.spatial.transform import Rotation as Rot
    from scipy.spatial import cKDTree
    D = M.D; G = dg["desmo"]; decl = dg["decl"]; out = []
    kdeg = np.degrees(G["kp"]); Tg = cKDTree(G["G2"][G["Kb"] <= G["lim"] + 1e-12])
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for i in idx:
            R1, t1 = M.T(1, i); R1b, t1b = M.T(7, i); R2, t2 = M.T(2, i); R9, t9 = M.T(9, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            want = float(np.interp(q2, decl["law_x_deg"], decl["law_y_deg"]))
            nz = R9.T @ (R1 @ G["C0"] + t1 - t9); ref = np.array([np.interp(abs(dK), kdeg, G["Z"][:, k]) for k in range(3)])
            pin = R2.T @ (R9 @ G["F0"] + t9 - t2)
            out.append(dict(pose=int(i), state=int(K["state"][i]), q2_deg=round(q2, 3), dK_deg=round(dK, 3), dK_law_deg=round(want, 3),
                            err_deg=round(abs(dK - want), 4), slot_closure_mm=round(float(np.linalg.norm(nz - ref)), 4),
                            groove_closure_mm=round(float(Tg.query(pin)[0]), 4),
                            cam_closure_mm=round(max(float(np.linalg.norm(nz - ref)), float(Tg.query(pin)[0])), 4)))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    return out


def slaved_decl(M, lg, K, kin, G):
    """the dynamics judge's slaved-K declaration on the BLENDED law (the verifier's B1 table: x = kK t, K = blend(x), q2 = q2hi + s_q t, cut at
    dK_lim), FORM closure (desmodromic: positive both ways, no spring), checked against the fit-bench chain"""
    D = M.D; P = D.p; L = D.law(); law = lg["law"]; kK = float(P.get("kA", P.get("kK"))); tb = math.radians(float(P["blend"])) / 2.0; hb = kK * tb
    tB = np.arange(-tb - math.radians(2.0), float(L["ts"][-1]) + 1e-12, math.radians(0.05)); x = kK * tB
    kab = np.where(x <= -hb, 0.0, np.where(x >= hb, x, (x + hb) ** 2 / (4 * hb))); kab = np.minimum(kab, G["lim"])
    keep = kab < G["lim"] - 1e-12; keep[np.argmax(~keep) if (~keep).any() else -1] = True
    tB, kab = tB[keep], kab[keep]
    st1 = kin & (np.abs(K["dK"]) > 1e-6); sgn = float(np.sign(np.median(K["dK"][st1]))) if st1.any() else 1.0
    X = law["q2hi_deg"] + law["s_q"] * np.degrees(tB); Y = sgn * np.degrees(kab); o = np.argsort(X); X, Y = X[o], Y[o]
    q2 = K["q"][:, 1]; err = round(float(np.abs(np.interp(q2[st1], X, Y) - np.degrees(K["dK"][st1])).max()), 4) if st1.any() else None
    return {"slaved": ["l1a", "l1b"], "driver": ["l1b", "l2"], "x_key": "q.1", "y_key": "knuckle.dK",
            "law_x_deg": [round(float(v), 4) for v in X], "law_y_deg": [round(float(v), 4) for v in Y], "rest_y_deg": 0.0, "closure": "form",
            "drive_groups": {"dk": "l1b"}, "source": "build.json law: the built groove's blended law (verifier B1: C1 quadratic over blend 10 deg of q2), cut at the slot end dK_lim 46.5",
            "check_fit_bench_max_err_deg": err, "check_fit_bench_poses": int(st1.sum()),
            "free_play_deg": dict(nominal=0.227, worst_tolerance=0.281, parts="slot slop crank held 0.04 + stage-1 crank-free 0.187 (dense scan)"),
            "note": "K = law(q2): stage 1 (pin in the cap-ring groove: dwell holds K on stop A, the rise drives it) -> bell crank -> stage 2 (link 1a's nose in the "
                    "crank's slot): form-closed both ways, no spring; the judge's equality is rigid - the 0.227 deg free play is not in the sim (stated)"}


def check_frames(M, dd, parts, stack):
    out = CCL.check_frames(M, dd, parts, stack)
    G = M._desmo_geom; dg = M._dg_l1
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    allp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    K = CCL.chain(M, allp); lc = law_check(M, K, [c["bench_pose"] for c in out], dg); byp = {x["pose"]: x for x in lc}
    for c in out:
        x = byp.get(c["bench_pose"]); c["desmo_law"] = x
        if x: print(f"  desmo {c['label']:42s} dK {x['dK_deg']:7.3f} law {x['dK_law_deg']:7.3f} err {x['err_deg']:.4f} slot closure {x['slot_closure_mm']:.4f} groove closure {x['groove_closure_mm']:.4f}", flush=True)
    return out


def ring_vs_stack(M, parts):
    """the cap-ring sector (link 2) vs link 1b's J2 lower plate and the J2 stop dowel over the J2 window (link 1b frame, q2 about u2): worst
    signed distance (mm, < 0 = metal in metal) and the overlap depth; plus the ring's radial reach past hub 2's O20"""
    import igl
    find = lambda s: next(p for p in parts if p[2].startswith(s))
    u2 = M.D.u[1]; lg = M._lg; qa, qb = [math.degrees(x) for x in lg["J2"][:2]]
    tgt = {nm: find(nm)[3] for nm in ("J2 lower plate", "link 1b strap", "drive bell crank boss")}
    res = {}
    for rn in ("drive cap-ring groove layer", "drive cap-ring roof"):
        Xr = np.r_[np.asarray(find(rn)[3].vertices), trimesh.sample.sample_surface_even(find(rn)[3], 4000, seed=29)[0]]
        for nm, m in tgt.items():
            best = (1e9, None)
            Vb, Fb = np.ascontiguousarray(m.vertices, float), np.ascontiguousarray(m.faces, np.int64)
            for q in np.arange(qa, qb + 1e-6, 4.0):
                R = S.rotm(u2, math.radians(q))[0]; v = float(igl.signed_distance(np.ascontiguousarray(Xr @ R.T, float), Vb, Fb)[0].min())
                if v < best[0]: best = (v, q)
            res[f"{rn[6:]} | {nm}"] = [round(best[0], 3), round(float(best[1]), 1)]
    return dict(rule="ring part (link 2) turned by q2 about u2 over the J2 window vs link 1b's parts (static in link 1b's frame) and the crank's at home "
                     "(the crank turns with K: the drive sweep covers the moving pairs); signed mm, < 0 = metal in metal", pairs=res)


def post(dd, M=None):
    if M is None: M, _ = fit()
    CCL.post(dd, M)                                                              # J3 relabel + j3_on_clip_frames (gen-8), then overwrite the text
    BJ = json.load(open(os.path.join(dd, "build.json"))); BJ["verified"] = VERIFIED
    json.dump(BJ, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    Dp = os.path.join(dd, "design.json"); D = json.load(open(Dp)); st = BJ.get("stops", {}).get("J3", {})
    D["source"] = (f"docs/concepts/{ID}.md (the verified config: docs/concepts/rows/{ID}.json best_params on the claim model's PARAMS, worn through the verifier "
                   f"docs/concepts/verify/{ID}.py --blend (BlendDesign IK, linear-part groove calibration)), fit on Bench(60,160) fast at fold margin 5 = the shape the "
                   f"verifier wore frozen on Bench(110,360) exact (v_gap 18.98, score 93.10; claim 19.04 linear IK; held out 23.19)")
    D["label"] = f"desmo-conecut-knuckle-3r (verified config, spring-free desmo K drive cell B, conecut knee + J3 stop [{J3MIN:.2f}, {J3MAX:.2f}], fit Bench(60,160), fold margin 5), L1 keep-out"
    D["built_with"] = ("pipeline/concept_l1/build_desmo_l1.py (imports build_conecut_l1.py -> build_slipper_l1.py unchanged: every gen-7/8 part from THIS model's fit, "
                       "J3 stop, D1-D3 fixes) with the drive swapped: cap-ring groove sector on link 2, crank short arm + stage-1 pin, trimmed bent arm + tip plate "
                       "with the wire-EDM slot, nose boss + root + O1.5 nose dowel on link 1a; no clock spring, no lobe, no flank lug")
    D["params"] = dict(PFULL); D["fits"] = FITS; D["verified"] = VERIFIED
    D.setdefault("build_fixes", {}).update(drive="desmo cell B (spring-free, roller-free)", clock_spring=False, capK=0.0)
    for j in D.get("joints", []):
        if j.get("joint") == "K":
            j["part"] = ("O20 v5 hub, MR117-2RS pair, plain cap (NO clock spring); stops A / B = an opposed pair of O3 dowels in arc slots + the desmo slot's own ends "
                         "(closed end = stop A at dK 0, far end = stop B at dK 46.5); slaved (no encoder)")
        if j.get("joint") == "J2":
            j["part"] = ("O20 x 12.25 v5 hub, MR117-2RS pair, encoder; link 2 carries the cap-ring sector with the stage-1 groove; q2 stops = O3 dowel in an arc "
                         "slot (folded stop q2lo, stop B at the drive's range)")
    dr = D.get("drive", {}); BJd = BJ.get("stack", {}).get("drive", {})
    D["drive"] = dict(kind=("desmo cell B: stage 1 = crowned O1.5 440C pin on the bell crank's short arm in a 1.52 x 1.5 groove in link 2's cap-ring sector "
                            "(dwell holds K on stop A, blended rise drives it); bell crank on link 1b (MR63ZZ pair on an O3 pin); stage 2 = ISO 8734 O1.5 440C nose "
                            "pressed in link 1a's boss at the seat C0 running in a 1.52-wide slot wire-EDM'd through the crank's 2.5 mm Ti tip plate; positive both "
                            "ways, no spring, no roller, no flank lug"),
                      components=["MR63ZZ 3x6x2.5 x 2 (crank pivot)", "ISO 8734 O3 m6 pivot pin + DIN 6799 RS 2.3", "ISO 8734 1.5 m6 440C stage-1 pin (crowned)",
                                  "440C groove insert ring in link 2's cap-ring sector", "ISO 8734 1.5 x 5 m6 440C nose dowel (link 1a)", "Ti tip plate with the wire-EDM slot"],
                      **{k: v for k, v in BJd.items() if k not in ("desmo",)})
    ps = D.get("passive", {})
    if ps: ps["kind"] = ("flat two-pin knee closing the loop at the cuff (pins a, b parallel to J3; NO encoders); K (4th revolute) is NOT a DOF: slaved to q2 both ways "
                         "by the desmo drive (form closure, no spring); the bell crank is set by the law phi = |dK| / g")
    D["j3_stop"] = st
    json.dump(D, open(Dp, "w"), indent=1, default=float)
    print("post: design.json rewritten for the desmo drive", flush=True)


# ---------------------------------------------------------------------------------------------------- retarget the gen-7 builder and run it
SL.RL, SL.RF, SL.SC, SL.S, SL.PK = DC, DC.RF, DC.SC, DC.S, DC.PK
SL.ID, SL.BEST, SL.CFG, SL.FITS = ID, BEST, CFG, FITS
SL.NOSE_R = float(PFULL["nose_r2"])
SL.L1Model, SL.fit = L1Model, fit
SL.chain = MIN.chain = BASE.chain = CCL.chain
SL.drive_parts, SL.build_parts, SL.set_adjacent, SL.check_frames = drive_parts, build_parts, set_adjacent, check_frames
CCL.ID, CCL.CFG, CCL.FITS, CCL.VERIFIED = ID, dict(PFULL), FITS, VERIFIED
_ld0, _sd0 = SL.law_check, SL.slaved_decl


def _law_check(M, K, idx, dg):
    M._dg_l1 = dg; return law_check(M, K, idx, dg)


def _slaved_decl(M, lg, K, kin):
    G = M._desmo_geom; d = slaved_decl(M, lg, K, kin, G); M._dg_l1["decl"] = d; return d


_lg0, _dgeo0 = SL.law_geom, SL.drive_geom


def _law_geom(M):
    lg = _lg0(M); M._lg = lg; return lg


def _drive_geom(M):
    dg = _dgeo0(M); G = desmo_geom(M); dg["desmo"] = G; M._desmo_geom = G; M._dg_l1 = dg; return dg


SL.law_check, SL.slaved_decl, SL.law_geom, SL.drive_geom = _law_check, _slaved_decl, _law_geom, _drive_geom


def patch_ring(dd):
    """rewrite ONLY the two cap-ring parts of an existing build (exo.glb nodes, parts_full.json, build.json stack.drive.ring) to the current
    ring_parts (the first build cut its +-3 deg sector through the groove's end discs: groove layer in two pieces)"""
    M, _ = fit(); G = desmo_geom(M); groove, roof, rinfo = ring_parts(M, G); _b, root, _n, binfo = boss_parts(M, G)
    sc = trimesh.load(os.path.join(dd, "exo.glb")); PF = json.load(open(os.path.join(dd, "parts_full.json"))); new = {}
    for key, mesh in (("drive cap-ring groove layer", groove), ("drive cap-ring roof", roof), ("drive nose boss root", root)):
        old = [g for g in sc.geometry if g.split("|")[1].startswith(key)]; assert len(old) == 1, old
        gp, nm, k = old[0].split("|")[:3]
        nm2 = nm.replace("99.9 deg", f"{rinfo['sector_deg']:.1f} deg") if "groove layer" in key else nm
        node = next(n for n in sc.graph.nodes_geometry if sc.graph[n][1] == old[0]); T_ = sc.graph[node][0]; assert np.allclose(T_, np.eye(4)), T_
        sc.delete_geometry(old[0]); nn = f"{gp}|{nm2}|{k}"; sc.add_geometry(mesh, node_name=nn, geom_name=nn); new[key] = nm2
        for p in PF["parts"]:
            if p["name"].startswith(key):
                mm = mesh.copy(); mm.merge_vertices(); vol = abs(mm.volume); rho_ = BASE.STEEL if "groove layer" in key else BASE.TI
                p.update(name=nm2, vol_cm3=round(vol / 1000, 3), mass_g=round(vol / 1000 * rho_, 2), valid=bool(mm.is_watertight and mm.is_volume),
                         pieces=int(len(mm.split(only_watertight=False))), faces=len(mesh.faces))
    sc.export(os.path.join(dd, "exo.glb")); json.dump(PF, open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    BJ = json.load(open(os.path.join(dd, "build.json"))); BJ["stack"]["drive"]["ring"] = rinfo; BJ["stack"]["drive"]["boss"] = binfo
    BJ["ring_patch"] = dict(note="cap-ring sector widened past the groove's round ends (asin((GW/2 + RW)/rho) + 0.5 deg) and the nose-boss root started RUNG outside "
                                 "hub K's O20 by --patch-ring; every other part untouched",
                            parts=new, valid={p["name"][:40]: (p["valid"], p["pieces"]) for p in PF["parts"] if p["name"].startswith(("drive cap-ring", "drive nose boss root"))})
    json.dump(BJ, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"patched ring: {BJ['ring_patch']}", flush=True)


def main():
    out = "l1_desmo-conecut"
    if "--out" in sys.argv: out = sys.argv[sys.argv.index("--out") + 1]
    else: sys.argv += ["--out", out]
    dd = os.path.join(BASE.FULL, "designs", out)
    if "--patch-ring" in sys.argv:
        patch_ring(dd); return
    if "--post-only" in sys.argv:
        sys.argv.remove("--post-only"); post(dd); return
    t0 = time.time()
    SL.main()
    post(dd)
    M, _ = fit(); lg = SL.law_geom(M); dg = SL.drive_geom(M)
    BJ = json.load(open(os.path.join(dd, "build.json")))
    sc = trimesh.load(os.path.join(dd, "exo.glb")); parts = []
    for gname in sc.geometry:
        gp, nm = gname.split("|")[:2]
        if gp in ("l1b", "l2", "dk"): parts.append((gp, None, nm, sc.geometry[gname], None))
    BJ["ring_vs_stack"] = ring_vs_stack(M, parts)
    json.dump(BJ, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"ring vs stack: {BJ['ring_vs_stack']['pairs']}", flush=True)
    print(f"desmo L1 done in {time.time() - t0:.0f} s -> {dd}", flush=True)


if __name__ == "__main__":
    main()
