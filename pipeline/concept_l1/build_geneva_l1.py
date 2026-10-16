"""L1 keep-out CAD of the generation-5 winner geneva-tail-knuckle-pinknee-3r in its ROD embodiment (verified v_gap 23.57 /
score 91.43 on Bench(110,360) exact frozen, held out 28.12: docs/concepts/geneva-tail-knuckle-pinknee-3r.md "Verification")
-> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json, workspace.json, design.json,
parts_full.json, build.json).

Derived from pipeline/concept_l1/build_minarc_l1.py (the gen-4 / 4b minarc L1), which is IMPORTED, never edited: its strap,
stop (dowel in arc slot), E-strap cap, knee-stop, chain / frame / check functions run here on this design's model. What
changes:
  * the model is the VERIFIER's corrected model (docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py CorrModel, config
    BEST, emb_mode "rod"): horn on a 1.5 mm plate on K's +6 mm cap top, rod centreline at the rod-end heads' mid-height,
    rocker post grown to the 19 mm at which the rod clears hub K's cap by 1 mm. The shape is that model's own fit on
    Bench(60,160) FAST (= the verifier's frozen-wear hand-over), so the L1 carries exactly the metal the verifier wore;
  * K is SLAVED: past the onset q2hi the lobe law dK = kK (q2 - q2hi) (stretching sense) sets K's angle, K never free and
    never read (3 encoders J1, J2, J3); the member frames come from the model's exact closed-form IK (state A: K on stop A;
    state 1: q2 on the law, K = law(q2)); folded poses past q2lo are not taken (J2 on its q2lo dowel, K on stop A);
  * stops: K = an opposed O3 dowel pair (gen 4b) between stop A (0, the spring's rest) and stop B (a1max); J2 = ONE O3 dowel
    (gen 4b: its 130+ deg slot leaves no room for an opposed pair; its strength is stated as a push limit) between the folded
    stop q2lo and the stretched stop B at the end of the law's valid prefix (q2hi + t_max: the physical "q2 dowel stop B");
  * the drive's metal at its real envelope: the constant-pressure spiral LOBE on hub 2's rotor (link 2) from r_lobe 9 mm at
    the onset to r_lobe + kK r_horn t at stop B (it stands past the O20 skirt there - modelled as it is), a 3 mm sector in the
    upper boss's height band; the ROCKER (O10 post, 19 mm) on link 1b beside hub 2; the O3 PUSHROD with both M3 ROD-END
    heads (O10 x 5); the HORN PLATE (O20 x 1.5, concentric, on hub K's cap top). The cap is link 1b's (the model's stack:
    link 1a = K lower plate, link 1b = K upper boss + cap); the horn plate is clamped on link 1a's K axle, which runs up
    through the MR117 bore and the clock spring's arbor (the spring's inner end) - so the rod (link 1b) turns link 1a, the
    spring sits between 1a and 1b, and nothing in the model's frozen link levels changes. The rod, its heads and the rocker
    ride link 1b rigidly, as the verified model wears them (the horn pin's arc, <= r_horn x dK = 2.3 mm, and the rocker's
    matching swing are not modelled - stated, 29-30 mm off the skin);
  * gen-4b fixes carried over: E strap top capped at the boss top (e_cap), the physical knee stop tooth + web at the model's
    own knee-window edge 180 - ang_min (no measurement change), the K stop pair placed clear of the lower member's strap.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_geneva_l1.py [--out l1_geneva-rod] [--jobs 2] [--no-clips]
"""
import argparse, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
os.environ.pop("CB_EXACT", None)                     # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_minarc_l1 as MIN                                                   # noqa: E402  (gen-4/4b L1 builder, imported unchanged)
BASE = MIN.BASE; CB, REF = BASE.CB, BASE.REF

V = MIN._load("geneva_verify_for_l1", os.path.join(REPO, "docs", "concepts", "verify", "geneva-tail-knuckle-pinknee-3r.py"))
G = V.G; S = G.S; KB = G.KB; PK = G.PK
ID = "geneva-tail-knuckle-pinknee-3r"
CROWN, UP, T_LINK, W_LINK = S.CROWN, S.UP, S.T_LINK, S.W_LINK
PLATE = MIN.PLATE; unit = S.unit; TI, STEEL = BASE.TI, BASE.STEEL
HORN_PLATE, HEAD_H, HEAD_R, ROD_R, ROCKER_R = V.HORN_PLATE, V.HEAD_H, V.HEAD_R, 1.5, 5.0
LOBE_Z = (UP + 1.0, UP + 4.0)                         # the lobe's 3 mm band in hub 2's upper boss (>= 0.95 mm over link 1b's lifted root)
LOBE_RIN = 7.0                                        # the sector's inner radius (inside the O20 hub, below the lobe's base circle)


# ---------------------------------------------------------------------------------------------------- the verified model
def fit():
    """the verifier's corrected model on the claim's config, fit on Bench(60,160) FAST: the shape it wore frozen"""
    B = CB.Bench(60, 160); M = V.CorrModel(B, dict(G.PARAMS, **V.BEST)); r = M.run(); a = PK.audit(M, B)
    r["gap_near1"] = a.get("gap_near1"); r["near_touch_min_mm"] = a.get("near_touch_min_mm")
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q)
    return M, r


def drive_geom(M):
    """the verifier's rod metal, recomputed with its own formulas (CorrModel._rod_metal) for the meshes"""
    D = M.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = M.fK, M.f[1]; capK = float(P.get("capK", 0) or 0)
    L1b = M.link_pts["L1b"][1]
    g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0)
    ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
    near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max()) + T_LINK
    hrk = float(M._rocker_h); eK, _ = S.frame_of(uK)
    hornP = uK * (fK + CROWN + capK + HORN_PLATE) + float(P["r_horn"]) * eK
    top = dR * (lev + hrk); a = top + 0.5 * HEAD_H * dR; b = hornP + 0.5 * HEAD_H * uK
    return dict(dR=dR, lev=lev, hrk=hrk, top=top, hornP=hornP, a=a, b=b, eK=eK, capK=capK, g0=g0)


def law_geom(M):
    """the slaved K: the lobe law on its valid prefix, the J2 window (q2lo .. q2 stop B) and K's (stop A .. stop B)"""
    D = M.D; P = D.p; L = D.law(); assert L.get("ok") and L["emb"] == "rod", L.get("emb")
    q0 = math.degrees(D._q2c[2]); sg = D.q2sgn
    rel = lambda x: ((x - q0 + 180) % 360 - 180) * sg
    q2lo, q2hi = D.q2_stops; q2end = math.degrees(float(L["q2t"][-1]))
    r_lo, r_hi = sorted((rel(q2lo), rel(q2end))); assert r_lo - 1e-6 <= rel(q2hi) <= r_hi + 1e-6, (q2lo, q2hi, q2end)
    qa, qb = sorted((q0 + sg * r_lo, q0 + sg * r_hi))
    spK = MIN.stop_specs(M)["K"]
    kK, r_horn, r_lobe = float(P["kK"]), float(P["r_horn"]), float(P["r_lobe"])
    t_end = float(L["ts"][-1]); lift = kK * r_horn                                # mm of lobe rise per rad of q2 (rocker 1:1)
    return dict(J2=(math.radians(qa), math.radians(qb), dict(q2_stops_deg=[round(q2lo, 3), round(q2end, 3)], q2_onset_deg=round(q2hi, 3),
                                                             window_deg=[round(qa, 3), round(qb, 3)], stop_B="end of the law's valid prefix (" + str(L["why_end"]) + ")")),
                K=spK, law=dict(kK=kK, r_horn=r_horn, r_lobe=r_lobe, s_q=float(L["s_q"]), q2hi_deg=round(q2hi, 3), t_end_deg=round(math.degrees(t_end), 3),
                                dK_end_deg=round(float(np.degrees(np.abs(L["dK"][-1]))), 3), pressure_angle_deg=round(float(L["pa"].max()), 2),
                                lobe_lift_mm_per_rad=round(lift, 4), lobe_r_end_mm=round(r_lobe + lift * t_end, 3), why_end=L["why_end"]),
                L=L)


# ---------------------------------------------------------------------------------------------------- the drive parts
def lobe_mesh(M, lg, dg, n=60):
    """the spiral lobe sector on hub 2's rotor (link 2, member-local home frame): outer edge r(t) = r_lobe + kK r_horn t at the
    rotor angle that faces the rocker at q2 = q2hi + s_q t, t in [0, t_end]; inner arc at LOBE_RIN; band LOBE_Z over the hub
    face. Returns (mesh, info)."""
    D = M.D; u2 = D.u[1]; c2 = D.c[1]; f2 = M.f[1]; H2 = c2 + f2 * u2; law = lg["law"]
    e, f = S.frame_of(u2); f = np.cross(u2, e)
    zc = H2 + 0.5 * (LOBE_Z[0] + LOBE_Z[1]) * u2
    sR = [dg["dR"] * z for z in np.linspace(dg["lev"], dg["lev"] + dg["hrk"], 40)]                  # rocker post axis samples
    hz = [float((p - c2) @ u2) - f2 for p in sR]
    k = int(np.argmin([abs(h - 0.5 * (LOBE_Z[0] + LOBE_Z[1])) for h in hz]))
    w = sR[k] - H2; w = w - (w @ u2) * u2; phiR = math.atan2(float(w @ f), float(w @ e)); d_ax = float(np.linalg.norm(w))
    ts = np.linspace(0.0, math.radians(law["t_end_deg"]), n); s_q = law["s_q"]; q2hi = math.radians(law["q2hi_deg"])
    psi = phiR - (q2hi + s_q * ts); r = law["r_lobe"] + law["lobe_lift_mm_per_rad"] * ts
    outer = np.c_[r * np.cos(psi), r * np.sin(psi)]; inner = np.c_[LOBE_RIN * np.cos(psi), LOBE_RIN * np.sin(psi)]
    V2 = np.r_[outer, inner]; F2 = []
    for i in range(n - 1): F2 += [[i, i + 1, n + i + 1], [i, n + i + 1, n + i]]
    m = MIN.extrude2d(V2, np.array(F2), H2, e, f, u2, LOBE_Z[0], LOBE_Z[1])
    # check: the lobe point that faces the rocker, posed into link 1b's frame at q2hi + s_q t, has radius r(t) on the rocker side
    chk = []
    for t_, r_ in ((0.0, law["r_lobe"]), (ts[-1], r[-1])):
        R2 = S.rotm(u2, q2hi + s_q * t_)[0]; Vw = (np.asarray(m.vertices) - c2) @ R2.T + c2
        ww = Vw - H2; ww = ww - np.outer(ww @ u2, u2); dir_ = np.cos(phiR) * e + np.sin(phiR) * f
        rr = np.linalg.norm(ww, axis=1); ang = np.arccos(np.clip((ww @ dir_) / np.maximum(rr, 1e-9), -1, 1))
        chk.append(round(float(rr[ang < math.radians(2.0)].max()), 3))
    info = dict(r_lobe=law["r_lobe"], r_end_at_stopB=round(float(r[-1]), 3), past_O20_skirt_mm=round(float(r[-1]) - S.HUB_R, 3),
                r_at_taken_max=None, sweep_deg=round(law["t_end_deg"], 3), band_mm=list(LOBE_Z), rocker_axis_to_hub2_axis_mm=round(d_ax, 2),
                rocker_face_to_hub2_axis_mm=round(d_ax - ROCKER_R, 2), gap_lobe_end_to_rocker_face_mm=round(d_ax - ROCKER_R - float(r[-1]), 2),
                rocker_height_at_lobe_band_mm=round(hz[k], 2), facing_radius_check_mm=chk,
                note="the follower that bridges the gap from the rocker post to the lobe is part of the rocker (L2 detail): the model "
                     "samples neither the lobe (inside the O20 stack) nor a follower")
    return m, info


def drive_parts(M, dg, lg):
    """[(group, member, name, mesh, material)] of the rod drive + its info"""
    D = M.D; U = [D.u[0], D.uK, D.u[1], D.u[2]]; HK = M.fK * D.uK; dR = dg["dR"]
    out = []
    lobe, linfo = lobe_mesh(M, lg, dg)
    taken_t = math.radians(float(np.degrees(np.abs(M.dK[M.kin_ok & (M.kstate == 1)])).max()) / lg["law"]["kK"]) if (M.kin_ok & (M.kstate == 1)).any() else 0.0
    linfo["r_at_taken_max"] = round(lg["law"]["r_lobe"] + lg["law"]["lobe_lift_mm_per_rad"] * taken_t, 3)
    out.append(("l2", 2, f"drive lobe keep-out (constant-pressure spiral on hub 2's rotor rim, link 2: r {lg['law']['r_lobe']:g} -> {linfo['r_end_at_stopB']:.2f} mm over "
                f"{lg['law']['t_end_deg']:.1f} deg of q2, {LOBE_Z[1] - LOBE_Z[0]:.0f} mm band F+{LOBE_Z[0]:.2f}..F+{LOBE_Z[1]:.2f}; past the O20 skirt by "
                f"{linfo['past_O20_skirt_mm']:.2f} mm at stop B)", lobe, "steel"))
    out.append(("l1b", 7, f"drive rocker post keep-out (O{2 * ROCKER_R:.0f} x {dg['hrk']:.1f} mm on link 1b beside hub 2, base at {dg['lev']:.1f} mm from GH; "
                f"the verifier's post height: the straight rod clears hub K's cap by 1 mm)", REF.cyl(np.zeros(3), dR, dg["lev"], dg["lev"] + dg["hrk"], r=ROCKER_R), "ti"))
    out.append(("l1b", 7, f"drive rod-end head at the rocker (M3 rod end, O{2 * HEAD_R:.0f} x {HEAD_H:.0f} keep-out)", REF.cyl(dg["top"], dR, 0.0, HEAD_H, r=HEAD_R), "steel"))
    out.append(("l1b", 7, f"drive rod-end head at the horn (M3 rod end, O{2 * HEAD_R:.0f} x {HEAD_H:.0f} keep-out, on the horn pin r {float(D.p['r_horn']):.2f} mm off K's axis)",
                REF.cyl(dg["hornP"], D.uK, 0.0, HEAD_H, r=HEAD_R), "steel"))
    L_rod = float(np.linalg.norm(dg["b"] - dg["a"]))
    out.append(("l1b", 7, f"drive pushrod keep-out (O{2 * ROD_R:.0f} x {L_rod:.1f} mm steel rod, head mid to head mid)",
                REF.cyl(dg["a"], unit(dg["b"] - dg["a"]), 0.0, L_rod, r=ROD_R), "steel"))
    r_hp = float(D.p["r_horn"]) + 4.0                                         # the verifier's O8 pad about the horn pin, made concentric (K-invariant)
    out.append(("l1a", 1, f"drive horn plate keep-out (O{2 * r_hp:.1f} x {HORN_PLATE:g} mm on hub K's cap top, F+{CROWN + dg['capK']:.2f}.."
                f"F+{CROWN + dg['capK'] + HORN_PLATE:.2f}; clamped on link 1a's K axle through the bearing bore and the spring arbor; carries the horn pin)",
                REF.cyl(HK, D.uK, CROWN + dg["capK"], CROWN + dg["capK"] + HORN_PLATE, r=r_hp), "ti"))
    return out, dict(lobe=linfo, rod_len_mm=round(L_rod, 2), rocker_post_mm=dg["hrk"], rocker_base_mm=round(dg["lev"], 2),
                     horn=dict(r_horn=float(D.p["r_horn"]), plate_mm=HORN_PLATE, plate_r_mm=round(r_hp, 3), head_bottom_mm=round(CROWN + dg["capK"] + HORN_PLATE, 3),
                               arc_at_stopB_mm=round(float(D.p["r_horn"]) * math.radians(lg["law"]["dK_end_deg"]), 2),
                               arc_at_taken_max_mm=round(float(D.p["r_horn"]) * taken_t * lg["law"]["kK"], 2)),
                     model_rod_info=getattr(M, "_rod_info", None))


# ---------------------------------------------------------------------------------------------------- parts
def build_parts(M, lg, dg, knee_geom=None):
    """[(group, member, name, mesh in the MEMBER-LOCAL home frame, material)]; member 5 = arm-fixed (canonical arm frame)"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"])
    U, C, F4, hr = MIN.joints4(M); H = lambda k: C[k] + F4[k] * U[k]; out = []
    capK = float(P.get("capK", 0) or 0)
    prof = MIN.link_rows(M); straps = {}
    for nm in ("L1a", "L1b", "L2"):
        lk, rows = prof[nm]; straps[nm] = MIN.link_solid(M, lk, rows)
    out.append(("base", 0, "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member, carried directly by the scapula handler at the hub ring)",
                REF.cyl(H(0), U[0], UP, CROWN, r=hr[0]), "ti"))
    out.append(("l1a", 1, "J1 lower plate keep-out (O20 x 3, link 1a)", REF.cyl(H(0), U[0], 0.0, PLATE, r=hr[0]), "ti"))
    out.append(("l1a", 1, "link 1a strap keep-out (8 x 3 mm Ti, fitted underside, J1 -> K)", straps["L1a"], "ti"))
    info = {}
    smp = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 4000, seed=2)[0]]
    for key, k, lower_strap, glo, mlo, gup, mup, label in (("K", 1, "L1a", "l1a", 1, "l1b", 7, "K"), ("J2", 2, "L1b", "l1b", 7, "l2", 2, "J2")):
        q_lo, q_hi, meta = lg[key]
        pair = key == "K"                                                       # gen 4b: K = an opposed pair (a couple); J2 single (no room)
        spts = smp(straps[lower_strap])
        ka_ = 0 if key == "K" else 1; ex_ = unit(U[ka_]); ey_ = unit(U[k] - (U[k] @ ex_) * ex_)   # gen 4b: the full CAD's bar root pad as points
        ph_ = math.acos(float(np.clip(unit(U[k]) @ ex_, -1, 1))); sd_ = math.sin(ph_) * ex_ - math.cos(ph_) * ey_
        lat_ = np.cross(U[k], sd_); rr_ = np.linspace(MIN.SLOT_RS - MIN.DOWEL_R - MIN.SLOT_CLR, hr[k], 8); ll_ = np.linspace(-W_LINK / 2, W_LINK / 2, 9)
        spts = np.r_[spts, np.array([H(k) + r_ * sd_ + l_ * lat_ + 1.5 * U[k] for r_ in rr_ for l_ in ll_])]
        th, a_lo, a_hi, clr = MIN.slot_place(spts, H(k), U[k], q_lo, q_hi, MIN.SLOT_RS, MIN.DOWEL_R + MIN.SLOT_CLR, MIN.DOWEL_R, pair=pair)
        plate = MIN.slotted_plate(H(k), U[k], 0.0, PLATE, hr[k], MIN.SLOT_RS, MIN.DOWEL_R + MIN.SLOT_CLR, a_lo, a_hi, extra=[(a_lo + np.pi, a_hi + np.pi)] if pair else ())
        e, f = S.frame_of(U[k]); f = np.cross(U[k], e); homes = [th, th + np.pi] if pair else [th]
        pds = [H(k) + MIN.SLOT_RS * (math.cos(t_) * e + math.sin(t_) * f) for t_ in homes]
        dws = [REF.cyl(pd, U[k], MIN.DOWEL_Z[0], MIN.DOWEL_Z[1], r=MIN.DOWEL_R) for pd in pds]
        travel = math.degrees(q_hi - q_lo)
        out.append((glo, mlo, f"{label} lower plate keep-out (O20 x 3, {'link 1a' if key == 'K' else 'link 1b'}) with the {label} stop slot{'s (an opposed pair)' if pair else ''} "
                    f"(r {MIN.SLOT_RS} mm, {2 * (MIN.DOWEL_R + MIN.SLOT_CLR):.1f} wide, {travel:.1f} deg of travel + the dowel; its ends = the stops)", plate, "ti"))
        for i_, dw in enumerate(dws):
            out.append((gup, mup, f"{label} stop dowel{f' {i_ + 1} of 2' if pair else ''} (ISO 8734 O{2 * MIN.DOWEL_R:g} m6 hardened, r {MIN.SLOT_RS} mm, F+{MIN.DOWEL_Z[0]}..F+{MIN.DOWEL_Z[1]:.2f}, "
                        f"pressed in the {label} upper boss)", dw, "steel"))
        info[key] = dict(meta, travel_deg=round(travel, 3), dowel_home_angle_deg=round(math.degrees(th), 2), dowel_home_angles_deg=[round(math.degrees(t_), 2) for t_ in homes],
                         pair=pair, slot_deg=[round(math.degrees(a_lo), 2), round(math.degrees(a_hi), 2)],
                         clearance_to_lower_strap_deg=round(clr, 2), dowel_mm=[2 * MIN.DOWEL_R, MIN.DOWEL_Z[0], MIN.DOWEL_Z[1]], slot_r_mm=MIN.SLOT_RS,
                         slot_w_mm=2 * (MIN.DOWEL_R + MIN.SLOT_CLR), end_clearance_mm=MIN.END_CLR,
                         frame="angles in frame_of(axis) of the lower member: dowel centre = home angle + joint angle")
        if key == "K":
            out.append(("l1b", 7, f"K upper boss + clock-spring cap keep-out (O20, F+3.15..F+{CROWN + capK:.2f}: cap {capK:g} mm taller - 0.3 x 5 mm 1.4310 +C1900 strip, "
                        f"outer end on this cap, inner end on link 1a's K axle; holds K on stop A below the drive's onset; K SLAVED to q2 by the lobe-rod drive, never read)",
                        REF.cyl(H(1), U[1], UP, CROWN + capK, r=hr[1]), "ti"))
            out.append(("l1b", 7, "link 1b strap keep-out (8 x 3 mm Ti, fitted underside, K -> J2)", straps["L1b"], "ti"))
    out.append(("l2", 2, "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2; the rotor that carries the drive lobe)", REF.cyl(H(2), U[2], UP, CROWN, r=hr[2]), "ti"))
    out.append(("l2", 2, "link 2 strap keep-out (8 x 3 mm Ti, fitted underside, J2 -> J3)", straps["L2"], "ti"))
    out.append(("l2", 2, "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(3), U[3], UP, CROWN, r=hr[3]), "ti"))
    out.append(("l3", 3, "J3 lower plate keep-out (O20 x 3, member 3)", REF.cyl(H(3), U[3], 0.0, PLATE, r=hr[3]), "ti"))
    dparts, dinfo = drive_parts(M, dg, lg); out += dparts
    Em, Einfo = MIN.e_strap_capped(M)
    out.append(("l3", 3, f"E strap keep-out (8 x 3 mm Ti, fitted underside, hub 3 plate -> pin a, thins to {tp:.2f} at the boss, top capped at the boss top tr+tp under the knee's reach)", Em, "ti"))
    out.append(("l3", 3, f"E boss = pin a lower plate (O{2 * MIN.BOSS_R:.0f} x {tp:.2f} mm, tr..tr+tp, member 3)", REF.cyl(fr["A0"], sn, tr, tr + tp, r=MIN.BOSS_R), "ti"))
    z0 = tr + tp + S.RUN; ck = fr["A0m"] + (lc / 2) * fr["eK"] + (z0 + tp / 2) * sn
    out.append(("l4", 6, f"knee link keep-out (flat Ti bar {lc + 2 * MIN.BOSS_R:.1f} x {MIN.KNEE_W:.0f} x {tp:.2f} mm, pins a, b {MIN.BOSS_R:.0f} mm from its ends, tr+tp+0.5)",
                REF.box(ck, np.stack([fr["eK"], fr["nK"], sn], 1), [lc + 2 * MIN.BOSS_R, MIN.KNEE_W, tp]), "ti"))
    out.append(("H", 5, f"arm pad = pin b lower plate (O{2 * MIN.PAD_R:.0f} x {tp:.2f} mm, tr..tr+tp, arm-fixed on the cuff)", REF.cyl(fr["Bm"], sn, tr, tr + tp, r=MIN.PAD_R), "ti"))
    if knee_geom is not None:
        ks = knee_geom; e_, n_ = fr["eK"], fr["nK"]
        out.append(("l4", 6, f"knee stop tooth keep-out ({ks['face']['s'][1] - ks['face']['s'][0]:.1f} x 2 mm, hangs {tr + tp + S.RUN + tp - ks['tooth'][1]:.2f} mm from the knee "
                    f"link top behind pin a; its face meets the E strap's side at knee angle {ks['ang_stop']:.2f} deg)", MIN.prism_mesh(ks["tooth"][0], fr["A0m"], e_, n_, sn, *ks["tooth"][1:]), "ti"))
        out.append(("l4", 6, f"knee stop web keep-out (knee link level, {tp:.2f} mm, joins the tooth to the knee link's back edge)",
                    MIN.prism_mesh(ks["web"][0], fr["A0m"], e_, n_, sn, *ks["web"][1:]), "ti"))
    zr = z0 + tp + S.RUN; RET = BASE.RET
    out.append(("l3", 3, f"pin a retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["A0"], sn, zr, zr + RET, r=4.0), "steel"))
    out.append(("H", 5, f"pin b retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["Bm"], sn, zr, zr + RET, r=4.0), "steel"))
    stack = dict(pin_stack_mm=float(P["stk"]), plate_tp=tp, run=S.RUN, knee_level_tr=round(float(tr), 3), f=[round(float(x), 3) for x in M.f], fK=round(float(M.fK), 3),
                 capK_mm=capK, hubK_crown_mm=CROWN + capK, horn_plate_top_mm=CROWN + capK + HORN_PLATE, boss=[round(float(tr), 3), round(float(tr + tp), 3)],
                 knee=[round(float(z0), 3), round(float(z0 + tp), 3)], E=Einfo, knee_link_mm=[round(lc + 2 * MIN.BOSS_R, 2), MIN.KNEE_W, tp], hubs_r=list(hr),
                 retainer=[round(float(zr), 3), round(float(zr + RET), 3)], full_pin_stack_mm=round(float(zr + RET - tr), 3), stops=info, drive=dinfo)
    return out, stack


def set_adjacent(parts):
    """minarc's built-part pairs (BASE.ADJ_PAIRS) + the drive's: lobe vs link 1b / J2 lower plate / rocker, rocker / rod / heads
    vs link 2 and link 1a and hub 1, the horn head on the horn plate (a seated pivot: within the 0.15 mm running rule)"""
    MIN.set_adjacent(parts)
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None)
    pairs = (("drive lobe", "link 1b strap"), ("link 1b strap", "drive lobe"), ("drive lobe", "J2 lower plate"), ("drive lobe", "drive rocker post"),
             ("drive rocker post", "drive lobe"), ("drive rocker post", "link 2 strap"), ("link 2 strap", "drive rocker post"), ("drive rocker post", "J2 upper boss"),
             ("drive rod-end head at the rocker", "link 2 strap"), ("drive pushrod", "link 2 strap"), ("drive pushrod", "link 1a strap"),
             ("drive rocker post", "link 1a strap"), ("drive pushrod", "drive horn plate"), ("drive rod-end head at the horn", "drive horn plate"),
             ("drive pushrod", "J1 upper boss"), ("drive rod-end head at the horn", "J1 upper boss"), ("drive horn plate", "link 1b strap"),
             ("drive horn plate", "K upper boss"), ("link 2 strap", "drive rod-end head at the rocker"), ("J2 upper boss", "drive rocker post"))
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1]: continue
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def drive_sweep(parts, U2, UK, q2w, kw, dq=1.0, nk=55):
    """red team of the drive's relative motions, pose-independent: link 2's parts (lobe, strap, J2 upper boss, J2 dowel) vs
    link 1b's over the whole q2 window (rotation about u2 through GH: the model's member frames have no translation), and
    link 1a's (horn plate, strap, plates) vs link 1b's over K's window. Pairs with a drive part only. Signed distance of A's
    surface samples to B's mesh (negative = inside), worst over the window: {pair: (mm, angle)}"""
    import igl
    def rot(u, a):
        u = unit(u); Kx = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]]); return np.eye(3) + math.sin(a) * Kx + (1 - math.cos(a)) * Kx @ Kx
    smp = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 3000, seed=4)[0]]
    sd = lambda X, m: float(igl.signed_distance(np.ascontiguousarray(X), np.ascontiguousarray(m.vertices, float), np.ascontiguousarray(m.faces, np.int64))[0].min())
    by = lambda mem: [(n, m) for g, mm, n, m, mat in parts if mm == mem]
    out = {}
    for memA, axis, angs in ((2, U2, np.arange(q2w[0], q2w[1] + 1e-6, dq)), (1, UK, -np.linspace(min(0.0, kw), max(0.0, kw), nk))):
        for na, ma in by(memA):
            if memA == 2 and not any(s_ in na for s_ in ("drive", "link 2 strap", "J2 upper boss", "J2 stop dowel")): continue
            XA = smp(ma)
            for nb, mb in by(7):
                if not ("drive" in na or "drive" in nb): continue
                best = (1e9, None)
                for q in angs:
                    v = sd(XA @ rot(axis, math.radians(q)).T, mb)
                    if v < best[0]: best = (v, float(q))
                out[f"{na[:40]} | {nb[:40]}"] = (round(best[0], 3), round(best[1] if memA == 2 else -best[1], 1))
    return dict(sorted(out.items(), key=lambda kv: kv[1][0]))


def law_check(M, K, idx):
    """per pose: the slaved K vs the lobe law, from the member frames (K's angle and q2 read off R1^T R1b and R1b^T R2)"""
    from scipy.spatial.transform import Rotation as Rot
    D = M.D; lg = M._lg["law"]; out = []
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for i in idx:
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            t = ((q2 - lg["q2hi_deg"] + 180) % 360 - 180) * lg["s_q"]
            want = float(np.degrees(np.interp(math.radians(max(t, 0.0)), M._lg["L"]["ts"], np.abs(M._lg["L"]["dK"])))) if K["state"][i] == 1 else 0.0
            out.append(dict(pose=int(i), state=int(K["state"][i]), q2_deg=round(q2, 3), t_deg=round(t, 3), dK_deg=round(dK, 3), dK_law_deg=round(want, 3),
                            err_deg=round(abs(abs(dK) - want), 4)))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="l1_geneva-rod")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time(); fb = (60, 160); fbs = "Bench(60,160)"
    import concept_kit as KIT
    dd = os.path.join(BASE.FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    M, rep = fit(); D = M.D; P = M.p
    if M.B.mode != "fast": print(f"WARNING: the fit bench {fbs} ran {M.B.mode}, not fast", flush=True)
    lg = law_geom(M); M._lg = lg; dg = drive_geom(M)
    print(f"fit (verifier CorrModel, BEST) on {fbs} {M.B.mode} (fold margin {KIT.FOLD_MARGIN}): near-touch gap {rep['gap']} reach {rep['reach']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} near1 {rep.get('gap_near1')} | f {np.round(M.f, 3).tolist()} fK {M.fK:.3f} tr {M.tr:.2f} rod {getattr(M, '_rod_info', None)} "
          f"law {lg['law']} ({time.time() - t0:.0f} s)", flush=True)
    Bf = M.B; allp_ = np.array([[Bf.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(Bf.idx))])
    Kf = MIN.chain(M, allp_); kin_ = Kf["ok"] & Kf["kok"]
    knee_stop = round(180.0 - float(P["ang_min"]), 4)                          # the model's own knee-window edge: no measurement change
    kg = MIN.knee_stop_geom(M, knee_stop, K=Kf)
    knee_rep = dict({k_: v for k_, v in kg.items() if k_ not in ("tooth", "web")}, model_window_edge_deg=knee_stop,
                    fit_bench_knee_max_deg=round(float(Kf["Kn"]["ang"][kin_].max()), 3), fit_bench_poses_past_stop=int((Kf["Kn"]["ang"][kin_] > knee_stop).sum()))
    print(f"knee stop at {knee_stop} deg: {knee_rep}", flush=True)
    parts, stack = build_parts(M, lg, dg, kg); stack["knee_stop"] = knee_rep
    print(f"drive: {json.dumps(stack['drive'])}", flush=True)
    up = BASE.user_parts(); bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ BASE.HR
    dense = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 40000, seed=5)[0]]
    mc = trimesh.Trimesh(bottom_c, np.asarray(bot.faces), process=False)
    sweep, swrep = BASE.arm_sweep(M, parts); xc, crep = BASE.cut_bottom(M, dense(mc), sweep)
    if xc is not None:
        mc = BASE.slice_bottom(mc, M, xc)
        k = next(i for i, (g, n, m) in enumerate(up) if n.startswith("BOTTOM")); n0 = up[k][1]
        up[k] = (up[k][0], n0 + f" + cut square to the arm {xc:.1f} mm distal of pin b, clear of the knee sweep",
                 trimesh.Trimesh(np.asarray(mc.vertices) @ BASE.HR.T, mc.faces, process=False))
        crep["bottom_watertight_after_cut"] = bool(mc.is_watertight)
    bottom_c = dense(mc)
    print(f"knee sweep in the arm frame: {len(sweep)} points ({swrep}); BOTTOM {crep}", flush=True)
    mount, mrep = BASE.pad_mount_sweep(M, bottom_c, sweep)
    if mount is None: print(f"WARNING: {mrep['note']} -> the nearest-end mount (may meet the sweep)", flush=True); mount, mrep = BASE.pad_mount(M, bottom_c)
    mrep["bottom"] = crep; mrep["sweep"] = swrep
    if mount is not None: parts.append(("H", 5, f"pad mount to BOTTOM (proxy) ({P['tp']:.2f} mm slab at the pad level, arm pad -> the BOTTOM bar, routed clear of the knee sweep)", mount, "ti"))
    def export_mesh(g, mem, m):
        if mem != 5: return m
        return trimesh.Trimesh(np.asarray(m.vertices) @ BASE.HR.T, m.faces, process=False)
    sc = trimesh.Scene(); pf = []
    allp = [(g, n, export_mesh(g, mem, m), mat) for g, mem, n, m, mat in parts] + [(g, n, m, "user") for g, n, m in up]
    for i, (g, n, m, mat) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = mat == "user"; mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        rho = STEEL if mat == "steel" else TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else ("steel" if mat == "steel" else "Ti-6Al-4V"),
                       mass_g=None if user else round(vol / 1000 * rho, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)),
                       pieces=None if user else int(len(mm.split(only_watertight=False))), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L1 keep-out", FACES={"1": round(float(M.f[0]), 2), "K": round(float(M.fK), 2), "2": round(float(M.f[1]), 2), "3": round(float(M.f[2]), 2)},
                   parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    bad = [p['name'] for p in ours if not p['valid'] or p['pieces'] != 1]
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in ours):.1f} g) + {len(up)} user parts; invalid: {bad or 'none'}; mount {mrep}; "
          f"stops {json.dumps(stack['stops'])}", flush=True)
    dsw = drive_sweep(parts, D.u[1], D.uK, stack["stops"]["J2"]["window_deg"], stack["stops"]["K"]["stop_B_deg"])
    stack["drive"]["sweep_check"] = dict(rule="signed distance (mm, negative = inside), worst over the joint window; angle = q2 (link 2 pairs) or dK (link 1a pairs)",
                                         pairs=dsw, worst=next(iter(dsw.items())) if dsw else None)
    print(f"drive sweep (worst 6): {list(dsw.items())[:6]}", flush=True)
    u1, u2, u3 = D.u; w_d = math.degrees(math.acos(float(np.clip(-u3[1], -1, 1)))); w_a = math.degrees(math.atan2(u3[0], u3[2]))
    az = math.degrees(math.atan2(u1[2], -u1[0])); elv = math.degrees(math.asin(float(np.clip(u1[1], -1, 1))))
    chk = S.circ_int(S.bvec(az, elv), D.A[0], S.w_dir(w_d, w_a), D.A[1], D.branch)
    law = lg["law"]
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict((k_, P[k_]) for k_ in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")),
               knee=dict((k_, P[k_]) for k_ in ("lE", "lc", "phiE", "phib", "stk", "ang_min")), knee_mid_m_mm=np.round(D.m, 3).tolist(), hub_r_mm=list(M.hr),
               knuckle=dict(uK=np.round(D.uK, 6).tolist(), bk1=P["bk1"], bk2=P["bk2"], psiA_deg=round(math.degrees(D.psiA), 3), a1max=P["a1max"],
                            dK_stop_B_deg=stack["stops"]["K"]["stop_B_deg"], q2_stops_deg=stack["stops"]["J2"]["q2_stops_deg"], smlo=P["smlo"], smhi=P["smhi"],
                            slaved=dict(law="dK = kK (q2 - q2hi) along the stretching sense, on the law's valid prefix", kK=law["kK"], q2_onset_deg=law["q2hi_deg"],
                                        s_q=law["s_q"], r_lobe=law["r_lobe"], r_horn=law["r_horn"], pressure_angle_deg=law["pressure_angle_deg"]),
                            note="az/el/a/w = the 3R with K on stop A; past the onset q2hi K is SLAVED to q2 by the lobe -> rocker -> pushrod -> horn drive "
                                 "(3 active DOF; K never free, never read)"))
    design = dict(id=a.out, source=f"docs/concepts/{ID}.md (rod embodiment, the verifier's corrected config: docs/concepts/verify/{ID}.py CorrModel + BEST), "
                                   f"fit on {fbs} {M.B.mode} at fold margin {KIT.FOLD_MARGIN} = the shape the verifier wore frozen on Bench(110,360) exact "
                                   "(v_gap 23.57, score 91.43; held out 28.12)",
                  params={k_: v for k_, v in V.BEST.items()}, n_joints=4, sliding_cuff=False, dof=3,
                  passive=dict(count=2, translations=0, rotations=2, outside_dof_count=True,
                               kind="flat two-pin knee closing the loop at the cuff (pins a, b parallel to J3); set by loop closure, nothing sags. K (4th revolute) is "
                                    "NOT a DOF: slaved to q2 by the lobe-rod drive past the onset, spring-held on stop A below it",
                               components=[dict(pin="a", between="member 3 (E boss) / knee link", part="IGLIDUR-PIN: iglidur GSM sleeve + 2 GTM washers on an integral O4 Ti pin, DIN 6799 RS 3.2 e-clip land",
                                                stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]]),
                                           dict(pin="b", between="knee link / arm pad (cuff)", part="IGLIDUR-PIN (as pin a)", stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]])]),
                  joints=[dict(joint="J1", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][0]),
                          dict(joint="K", part=f"O20 v5 hub, MR117-2RS pair, cap {CROWN + float(P.get('capK', 0)):.2f} mm (clock spring 0.3 x 5 1.4310 +C1900) + {HORN_PLATE:g} mm horn "
                                                f"plate on link 1a's axle; stops A / B = an opposed pair of O3 dowels in two {stack['stops']['K']['travel_deg']:.1f}-deg arc slots; "
                                                "slaved (no encoder)", axis_offset_mm=0.0, passive=False, slaved=True, sensed=False),
                          dict(joint="J2", part=f"O20 x 12.25 v5 hub, MR117-2RS pair, encoder; drive lobe on its rotor; q2 stops = O3 dowel in a "
                                                 f"{stack['stops']['J2']['travel_deg']:.1f}-deg arc slot (folded stop q2lo, stretched stop B at the law's end)",
                               axis_offset_mm=kin["axis_line_offsets_mm"][1]),
                          dict(joint="J3", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][2])],
                  drive=dict(kind="constant-pressure spiral lobe (hub 2 rotor) -> rocker on link 1b -> O3 pushrod, M3 rod ends O10 -> horn on hub K's cap top",
                             components=["MR63ZZ-class follower or a polished pad on the rocker (L2)", "M3 rod-end x 2 (e.g. DIN ISO 12240-4 E-series, O10 head)",
                                         "O3 x %.1f mm steel pushrod, M3 threaded ends" % stack["drive"]["rod_len_mm"], "O%.1f x 1.5 Ti horn plate on the K axle" % (2 * (float(P["r_horn"]) + 4.0))],
                             **stack["drive"]),
                  kinematics=kin, base=dict(mount="girdle", chain="geneva_rod_knuckle", note="base rides the scapula on the user's scapula handler, carried directly at the J1 hub ring (no tab)"),
                  built_with="pipeline/concept_l1/build_geneva_l1.py (L1 keep-out meshes: O20 hub keep-outs incl. hub K's 6 mm taller cap + horn plate, fitted 8 x 3 straps "
                             "1a / 1b / 2, stop dowels + arc slots, the lobe / rocker / rod / rod-end drive, E strap + boss, knee link + knee stop, arm pad, pin retainers)",
                  label=f"geneva-tail-knuckle-pinknee-3r rod (fit {fbs}, fold margin {KIT.FOLD_MARGIN:g}), L1 keep-out", fit_bench=list(fb), fold_margin=KIT.FOLD_MARGIN,
                  build_fixes=dict(k_pair=True, j2_single_dowel_push_limit=True, e_cap=True, knee_stop_deg=knee_stop),
                  faces_mm=[round(float(x), 2) for x in M.f], fK_mm=round(float(M.fK), 2), tr=round(float(M.tr), 2), stack_mm=stack,
                  bench=dict(near_touch_gap=rep["gap"], **{k_: rep[k_] for k_ in ("reach", "follow", "inband14", "contact")}, inband10=rep["inband10"]),
                  note="R17's dynamics judge models K as a spring-held knuckle between stops A / B (kinematics.knuckle); it has no term for the lobe-rod "
                       "coupling, so its K moves where the clips put it but is not driven by q2 in MuJoCo")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    set_adjacent(parts)
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(params=dict(G.PARAMS, **V.BEST), source=f"docs/concepts/verify/{ID}.py CorrModel + BEST", bench=f"{fb[0]},{fb[1]}", mode=M.B.mode,
                            fold_margin=KIT.FOLD_MARGIN, report={k_: rep.get(k_) for k_ in ("gap", "plain", "gap_near1", "near_touch_min_mm", "reach", "follow", "inband14",
                                                                                              "inband10", "contact", "why", "min_clear_taken", "parts_ib14", "drive")},
                            m=np.round(D.m, 3).tolist(), tr=round(float(M.tr), 3), fK=round(float(M.fK), 3), rod=getattr(M, "_rod_info", None)),
                   law={k_: v for k_, v in law.items()}, stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"], dowel_check=MIN.dowel_check(),
                   j2_push_limit=dict(MIN.dowel_check()["bearing_pair_static"], rule="J2 single dowel (gen 4b): rated by the MR117 pair's static load (s0 1.0 at "
                                      f"{MIN.dowel_check()['bearing_pair_static']['C0_N_each'] * 2 * MIN.SLOT_RS / 1000:.2f} N.m)"))
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = MIN.check_frames(M, dd, parts, stack)
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench
    try: rep_out["law_check"] = law_check(M, Kf, [c["bench_pose"] for c in rep_out["check"]] + list(np.nonzero(kin_ & (Kf["state"] == 1))[0]))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    lc_ = rep_out["law_check"]; st1 = [x for x in lc_ if x["state"] == 1]
    rep_out["law_check_summary"] = dict(poses=len(lc_), stretched=len(st1), max_err_deg=max((x["err_deg"] for x in lc_), default=None),
                                        dK_max_deg=max((abs(x["dK_deg"]) for x in st1), default=None), past_40=sum(1 for x in st1 if abs(x["dK_deg"]) > 40))
    print(f"law check: {rep_out['law_check_summary']}", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        C, st = BASE.make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=max(M.hr), knuckle=True, **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        ko = {cl["name"]: dict(frames_K_open=sum(1 for f in cl["frames"] if not f["held"] and abs(f.get("knuckle", {}).get("dK", 0)) > 1e-3),
                               dK_max=round(max([abs(f.get("knuckle", {}).get("dK", 0)) for f in cl["frames"] if not f["held"]] or [0]), 2)) for cl in C["clips"]}
        for k_ in st: st[k_]["knuckle"] = ko.get(k_)
        rep_out["clips"] = st; json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"clips.json written ({time.time() - t0:.0f} s); K open on clips: { {k_: v for k_, v in ko.items() if v['frames_K_open']} }", flush=True)
        W = BASE.make_workspace(M, a.jobs); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4),
                                    driven_feasible=int(sum(1 for p in W["poses"] if p["eval_feasible"] and p["knuckle"]["state"] != 0)))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
