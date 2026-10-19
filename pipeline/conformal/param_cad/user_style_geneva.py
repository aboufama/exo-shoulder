"""Full user-style CAD of the generation-5 winner geneva-tail-knuckle-pinknee-3r, ROD embodiment (verified v_gap 23.57 /
score 91.43 on Bench(110,360) exact frozen, held out 28.12: docs/concepts/geneva-tail-knuckle-pinknee-3r.md "Verification";
the verifier's CORRECTED config, docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py CorrModel + BEST).

Kinematics are EXACTLY the verified model's: the shape is the L1's (pipeline/concept_l1/build_geneva_l1.fit = the verifier's
frozen-wear hand-over, Bench(60,160) fast), every part is designed in its member's home frame (the scapula frame at rest, GH =
origin) and the judged clips.json / workspace.json are the L1's (l1_geneva-rod: "G" + "T" per group = the model's own member
transforms, K slaved to q2 by the lobe law past the onset), asserted equal (params, tr, knee centre m, hub levels).

Reused, imported unchanged (never edited): user_style_minarc.py (gen 4 / 4b: v5 O20 hubs with torispherical caps, the K
clock spring, the 4-strip 2.5-D machined bars 1a / 1b / 2 through the model's strap stations, O3 dowel-in-arc-slot stops with
the K opposed pair placed by the L1 clear of the bar roots, the J2 single dowel with its push limit, the physical knee stop,
check_frames), user_style_pinknee.py (member 3 + E strap capped at the boss top, knee link, IGLIDUR-PIN stacks with DIN 6799
clips on a 1.0 mm land, arm pad + pad mount fused with the cut BOTTOM, upper-arm cuff, base at the J1 ring), and
build_geneva_l1.py (fit, law, stop windows). What is new here, from the drive red team's build spec
(docs/research/geneva_rod_drive_redteam.md section 5, variant V0 side +1, docs/research/geneva_rod_drive/drive.py):

  K hub      the v5 O20 stack, K cap 6 mm taller and FLAT-topped (crown F + 18.25): spring chamber O16 round link 1a's O5
             arbor (no sensor pocket, no magnet: K is slaved, never read), a crown counterbore O10 x 1.2 for the HORN HUB;
             the arbor runs up through an O5.6 crown bore to a shoulder at F + 17.15 and a DD O3 tip; the horn hub (Ti O9.4 x
             1.2, DD bore, pressed) sits on the shoulder, flush + 0.1 over the crown; the HORN PLATE (Ti O13 x 1.4, 0.1 mm over
             the crown) carries the O3 horn pin at r_horn 2.493 and is clamped to the hub by 2x M1.6 countersunk screws in
             +-5 deg arc slots (the onset trim). Plate top = the model's horn-plate top F + 19.75.
  lobe       a 17-4PH H900 lobe ring on hub 2's rotor (link 2's upper ring turned to O18 over F2+6.15..8.9): the profile is
             the red team's exact RSSR solution (lobe_polar_V0: r 10.74 -> 12.87 over profile az 48.3 -> 60.7 deg) drawn as
             a chain of 3-point arcs through the solved profile points, a concave R3 arc (the roller at the onset) into the
             O20.2 dwell circle, a straight return flank; 2.6 mm tall, wire-EDM, keyed (O1 dowel, stated) at the onset.
  rocker     a fixed O5 17-4PH post pressed in a Ti boss on link 1b at the verified rocker base, axis || u2, 20 mm (the red
             team's +1 mm for the 1 mm rod-to-cap rule); the BELL CRANK (Ti: tube O10 on 2x MR85ZZ, follower arm 9.0 mm to an
             MR63ZZ roller on an O3 pin, crank arm 9.0 mm to the O3 crank pin tilted 29.0 deg from u2, square to the rod);
  rod        a Ti-6Al-4V dog-bone, O3 shank, centres 36.94 mm, two O13 eyes with pressed igus igubal KGLM-03-class
             spherical bearings (iglidur housing O10 + ball on the pin), DIN 6799 clips on the pins.
  posing     the bell crank (group "dk") and the rod (group "dr") are POSED, not frozen on link 1b: per clip / workspace frame
             the horn pin goes where link 1a's frame puts it, the rocker angle solves the exact RSSR closure |A(beta) - B| =
             36.94, the rod takes the minimal rotation A0B0 -> AB. Two groups are added to the L1's clips.json /
             workspace.json copies; every other group's frames are the L1's, untouched.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_geneva.py [--out user_geneva_rod] [--l1 l1_geneva-rod]
"""
import argparse, importlib.util, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")
import user_style_minarc as USM                                                            # noqa: E402  (gen-4/4b full CAD, imported unchanged)
USP, US, BM, REPO = USM.USP, USM.US, USM.BM, USM.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_geneva_l1 as GL1                                                              # noqa: E402  (gen-5 L1: the verified model's fit, law, stops)
import numpy as np, cadquery as cq, trimesh                                                # noqa: E402
PB, LV, unit, xform = US.PB, US.LV, US.unit, US.xform
FULL = USP.FULL; at = USP.at; disc = USP.disc; prism = USP.prism; plane = USP.plane; rev = USP.rev
S = BM.S; HUB_R = US.HUB_R
GROUPS = dict(USM.GROUPS, dk=8, dr=9)                                                       # + the posed drive groups (bell crank, rod)

_spec = importlib.util.spec_from_file_location("geneva_drive", os.path.join(REPO, "docs", "research", "geneva_rod_drive", "drive.py"))
DV = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(DV)                   # the red team's exact RSSR drive (V0)

# ---- drive dimensions (red team build spec, V0 side +1)
R_HORN, A_F, A_C, RR = 2.493, 9.0, 9.0, 3.0
LOBE_Z = (6.15, 8.75)                      # lobe ring band over hub 2's face (the red team's 6.2..8.7 on the pad top, under the cap skirt 8.8)
ROLLER_Z = (6.2, 8.7)                      # MR63ZZ 3 x 6 x 2.5, mid-plane F2 + 7.45 (the lobe was solved there)
ARM_F_Z = (8.85, 10.35)                    # follower arm plate over the roller
POST_R, TUBE_R, TUBE_BORE, MR85_R = 2.5, 5.0, 2.8, 4.0
EYE_R, EYE_H, HSG_R, BALL_R = 6.5, 4.0, 5.0, 3.5     # rod eye O13 x 4.4, igubal housing O10, ball sphere R3.6 (KGLM-03 class)
PIN_R = 1.5
HORN = dict(hub_z=(17.15, 18.35), hub_r=4.7, cb_r=5.0, cb_z=17.05, bore_r=2.8, tip_r=1.5, tip_flat=1.2, tip_top=18.30,
            plate_z=(18.35, 19.75), plate_r=6.5, screw_r=3.6, screw_half_deg=5.0, slot_w=0.85)


# ---------------------------------------------------------------------------------------------------- drive geometry
def drive_solution(M):
    """the red team's V0 drive on THIS fit: checks the geometry DV read (geo.npz) is the L1's shape, returns the arrays + frame"""
    D = M.D; chk = dict(u2=float(np.abs(DV.u2 - D.u[1]).max()), uK=float(np.abs(DV.uK - D.uK).max()), f2=abs(DV.f2 - float(M.f[1])), fK=abs(DV.fK - float(M.fK)))
    assert max(chk.values()) < 2e-3, f"the red team's drive geometry is another shape: {chk}"
    r = DV.run(r_h=R_HORN, a_f=A_F, a_c=A_C, rr=RR, side=+1); arr = r.pop("_arrays")
    u2, uK = DV.u2, DV.uK; bx = unit(DV.axis_off); by = np.cross(u2, bx)
    PT = DV.axis_off + DV.hT * u2; PL = DV.axis_off + DV.hL * u2
    A0, B0, C0 = arr["As"][0], arr["Bs"][0], arr["Cs"][0]; L = float(np.linalg.norm(B0 - A0))
    pin = unit(u2 - (u2 @ arr["dr"][len(arr["dr"]) // 2]) * arr["dr"][len(arr["dr"]) // 2])
    if pin @ u2 < 0: pin = -pin
    d0 = unit(B0 - A0); eB = unit(uK)                                                          # rod eye axes = the pin axes at the onset (the
    eA = pin                                                                                   # eyes are machined at the misalignment angle)
    return dict(rep=r, arr=arr, u2=u2, uK=uK, bx=bx, by=by, PT=PT, PL=PL, A0=A0, B0=B0, C0=C0, L=L, pin=pin, eA=eA, eB=eB, d0=d0,
                axis=DV.axis_off, Pb=DV.Pb, hT=DV.hT, hL=DV.hL, hB=DV.hB, capTop=DV.capTop, f2=DV.f2, fK=DV.fK, chk=chk)


def solve_beta(dv, B, beta0=0.0):
    """rocker angle (rad about u2, 1b frame) with |A(beta) - B| = L (the exact RSSR closure)"""
    u2, PT, A0, L = dv["u2"], dv["PT"], dv["A0"], dv["L"]
    A_of = lambda b: PT + DV.rotm(u2, b) @ (A0 - PT)
    b = beta0
    for _ in range(40):
        F = np.linalg.norm(A_of(b) - B) - L; h = 1e-7; dF = (np.linalg.norm(A_of(b + h) - B) - L - F) / h
        if abs(dF) < 1e-12: break
        b -= F / dF
        if abs(F) < 1e-10: break
    return b, float(abs(np.linalg.norm(A_of(b) - B) - L))


def rotm(ax, a):
    return DV.rotm(ax, a)


def minrot(a, b):
    a, b = unit(a), unit(b); v = np.cross(a, b); s = np.linalg.norm(v); c = float(a @ b)
    if s < 1e-12: return np.eye(3)
    return rotm(v / s, math.atan2(s, c))


def drive_poses(dv, G1a, T1a, G1b, T1b):
    """(G, T) of the bell crank (dk) and the rod (dr) at one frame, from link 1a / 1b's frames: horn pin B = link 1a's point B0,
    beta from the RSSR closure, rod = minimal rotation A0B0 -> AB"""
    B = G1b.T @ (G1a @ dv["B0"] + T1a - T1b)                                                    # horn pin in link 1b's frame
    b, res = solve_beta(dv, B)
    Rb = rotm(dv["u2"], b); p = dv["axis"]
    A = dv["PT"] + Rb @ (dv["A0"] - dv["PT"])
    Rr = minrot(dv["B0"] - dv["A0"], B - A)
    Gk, Tk = G1b @ Rb, G1b @ (p - Rb @ p) + T1b
    Gr, Tr = G1b @ Rr, G1b @ (A - Rr @ dv["A0"]) + T1b
    return (Gk, Tk), (Gr, Tr), dict(beta_deg=math.degrees(b), closure_mm=res, horn_shift_mm=float(np.linalg.norm(B - dv["B0"])))


def pose_groups(dv, path_in, path_out, kind):
    """add groups dk / dr to every frame (clips) or every pose (workspace) of the L1's json"""
    J = json.load(open(path_in)); stats = dict(frames=0, beta_deg=[1e9, -1e9], closure_max_mm=0.0)
    frs = [f for c in J["clips"] for f in c["frames"]] if kind == "clips" else J["poses"]
    for f in frs:
        if "G" not in f or "l1b" not in f["G"]: continue
        g = lambda k: np.array(f["G"][k], float).reshape(3, 3); t = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        (Gk, Tk), (Gr, Tr), info = drive_poses(dv, g("l1a"), t("l1a"), g("l1b"), t("l1b"))
        f["G"]["dk"] = [round(float(x), 6) for x in Gk.ravel()]; f["G"]["dr"] = [round(float(x), 6) for x in Gr.ravel()]
        f.setdefault("T", {}); f["T"]["dk"] = [round(float(x), 5) for x in Tk]; f["T"]["dr"] = [round(float(x), 5) for x in Tr]
        stats["frames"] += 1; stats["beta_deg"] = [min(stats["beta_deg"][0], info["beta_deg"]), max(stats["beta_deg"][1], info["beta_deg"])]
        stats["closure_max_mm"] = max(stats["closure_max_mm"], info["closure_mm"])
    json.dump(J, open(path_out, "w"), separators=(",", ":"))
    stats["beta_deg"] = [round(x, 3) for x in stats["beta_deg"]]; return stats


# ---------------------------------------------------------------------------------------------------- drive parts
def lobe_ring(dv):
    """the lobe ring (link 2 frame): dwell circle r 10.1 -> concave R3 (the roller at the onset) -> the solved profile as 3-point
    arcs -> straight return flank -> dwell; bore O18; extruded LOBE_Z along u2 from hub 2's face"""
    u2, bx, by, f2 = dv["u2"], dv["bx"], dv["by"], dv["f2"]; arr = dv["arr"]
    P2 = np.c_[arr["prof"] @ bx, arr["prof"] @ by]; Cp0 = np.array([dv["C0"] @ bx, dv["C0"] @ by])
    # pitch point at t = 0 in LINK 2's frame (arr['pc'][0]); the roller circle there touches the dwell and the profile start
    pc0 = np.array([arr["pc"][0] @ bx, arr["pc"][0] @ by]); r_base = float(np.linalg.norm(pc0)) - RR
    az = lambda p: math.atan2(p[1], p[0]); pol = lambda r, a: np.array([r * math.cos(a), r * math.sin(a)])
    Q0 = pol(r_base, az(pc0)); P0 = P2[0]
    assert abs(np.linalg.norm(P0 - pc0) - RR) < 0.02, np.linalg.norm(P0 - pc0)
    aQ, aP = az(Q0 - pc0), az(P0 - pc0); da = (aP - aQ + math.pi) % (2 * math.pi) - math.pi; Mq = pc0 + RR * np.array([math.cos(aQ + da / 2), math.sin(aQ + da / 2)])
    n = len(P2); idx = list(range(0, n - 1, 21)) + [n - 1]
    if idx[-1] - idx[-2] < 6: idx.pop(-2)
    a_end = az(P2[-1]); a_f = a_end + math.radians(8.0); Pf = pol(r_base, a_f)
    a_q = az(Q0) + 2 * math.pi; Mb = pol(r_base, 0.5 * (a_f + a_q))
    wp = cq.Workplane(plane((f2 + LOBE_Z[0]) * u2, bx, by)).moveTo(*Pf).threePointArc(tuple(Mb), tuple(Q0)).threePointArc(tuple(Mq), tuple(P0))
    for i, j in zip(idx[:-1], idx[1:]): wp = wp.threePointArc(tuple(P2[(i + j) // 2]), tuple(P2[j]))
    ring = wp.lineTo(*Pf).close().extrude(LOBE_Z[1] - LOBE_Z[0]).val()
    ring = ring.cut(disc(np.zeros(3), u2, 9.0, f2 + LOBE_Z[0] - 1, f2 + LOBE_Z[1] + 1))
    # arc-chain fidelity: the solved profile points vs the chain (radial, in the polar frame)
    chain_r = []
    for i, j in zip(idx[:-1], idx[1:]):
        a_, m_, b_ = P2[i], P2[(i + j) // 2], P2[j]
        # circumcircle
        A_ = np.array([[2 * (m_[0] - a_[0]), 2 * (m_[1] - a_[1])], [2 * (b_[0] - a_[0]), 2 * (b_[1] - a_[1])]])
        c_ = np.linalg.solve(A_, [m_ @ m_ - a_ @ a_, b_ @ b_ - a_ @ a_]); R_ = np.linalg.norm(a_ - c_)
        chain_r += [abs(np.linalg.norm(P2[k] - c_) - R_) for k in range(i, j + 1)]
    # the roller at stop B vs the return flank
    pcE = np.array([arr["pc"][-1] @ bx, arr["pc"][-1] @ by]); s = np.linspace(0, 1, 200)[:, None]; fl = P2[-1] * (1 - s) + Pf * s
    fl_clear = float(np.linalg.norm(fl[5:] - pcE, axis=1).min() - RR)
    info = dict(base_r=round(r_base, 3), profile_r=[round(float(np.linalg.norm(P2[0])), 3), round(float(np.linalg.norm(P2[-1])), 3)],
                profile_az_deg=[round(math.degrees(az(P2[0])), 2), round(math.degrees(a_end), 2)], arcs=len(idx) - 1,
                arc_chain_dev_max_mm=round(max(chain_r), 5), flank_to_roller_at_stopB_mm=round(fl_clear, 3), flank_end_az_deg=round(math.degrees(a_f), 2),
                past_O20_skirt_max_mm=round(float(np.linalg.norm(P2, axis=1).max()) - HUB_R, 3), band_mm=list(LOBE_Z), valid=ring.isValid())
    return ring, info


def bell_crank(dv):
    """(post, boss, crank, bearings, roller, roller pin, crank pin) in link 1b's home frame (crank parts posed by group dk)"""
    u2, ax = dv["u2"], dv["axis"]; hb = float(dv["Pb"] @ u2); f2 = dv["f2"]
    pa = lambda h: ax + h * u2
    # the eye at A: lowest point of its bottom face over the tube footprint -> tube top 0.5 below it
    eA, A0 = dv["eA"], dv["A0"]; e1 = unit(np.cross(eA, u2)); e2 = np.cross(eA, e1)
    ring = [A0 - 0.5 * EYE_H * eA + EYE_R * (math.cos(t) * e1 + math.sin(t) * e2) for t in np.linspace(0, 2 * math.pi, 361)]
    ring += [A0 - 0.5 * EYE_H * eA + rr_ * (math.cos(t) * e1 + math.sin(t) * e2) for rr_ in (2.0, 4.0) for t in np.linspace(0, 2 * math.pi, 73)]
    ring = np.array(ring); w = ring - ax; rad = np.linalg.norm(w - np.outer(w @ u2, u2), axis=1)
    over = ring[rad < TUBE_R + 0.6] @ u2
    t_top = min(hb + 20.0, float(over.min()) - 0.5) if len(over) else hb + 20.0
    # the CAD's link 1b at the rocker base is its J2 lower pad lifted to the hub level (F2 + 0..3, the L1's hub-zone lift), not the
    # model's unlifted strap (hb): the boss stands in that pad and 1 mm above it, the post is pressed through it
    boss_bot, boss_top = f2 + 0.5, f2 + 4.0; t_bot = boss_top + 0.3
    post = disc(ax, u2, POST_R, f2 + 0.3, t_top)
    boss = disc(ax, u2, 4.5, boss_bot, boss_top)
    tube = rev([(TUBE_BORE, 0), (TUBE_R, 0), (TUBE_R, t_top - t_bot), (TUBE_BORE, t_top - t_bot)], pa(t_bot), u2)
    for z0, z1 in ((0.0, 2.5), (t_top - t_bot - 2.5, t_top - t_bot)): tube = tube.cut(rev([(0, z0 - 0.01), (MR85_R, z0 - 0.01), (MR85_R, z1 + 0.01), (0, z1 + 0.01)], pa(t_bot), u2))
    # follower arm: tube -> roller pin (O5 eye), plate ARM_F_Z
    C0 = dv["C0"]; cr = C0 - ax - (C0 @ u2) * u2; Lf = float(np.linalg.norm(cr)); xf = unit(cr); yf = np.cross(u2, xf)
    armf = USP.stadium(pa(f2 + ARM_F_Z[0]), xf, yf, Lf, 2.5, ARM_F_Z[1] - ARM_F_Z[0])
    bore = disc(ax, u2, TUBE_BORE, t_bot - 1.0, t_top + 1.0)                                # the post bore (R6: a solid arm hub sat on the post)
    armf = armf.cut(bore)
    armf_hub = rev([(TUBE_BORE, 0), (TUBE_R, 0), (TUBE_R, ARM_F_Z[1] - ARM_F_Z[0]), (TUBE_BORE, ARM_F_Z[1] - ARM_F_Z[0])], pa(f2 + ARM_F_Z[0]), u2)
    # crank arm at the tube top -> the crank pin boss (along the tilted pin axis) up to the eye bottom - 0.3
    ca = A0 - ax - (A0 @ u2) * u2; Lc = float(np.linalg.norm(ca)); xc = unit(ca); yc = np.cross(u2, xc)
    arm_c = USP.stadium(pa(t_top - 2.0), xc, yc, Lc, 3.0, 2.0).cut(bore)
    pinb = A0 + 0.0 * eA; s_lo = None
    for s_ in np.linspace(-12, 0, 241):                                                       # where the pin axis meets the crank arm's top plane
        if (pinb + s_ * eA) @ u2 >= t_top: s_lo = s_; break
    s_lo = (s_lo if s_lo is not None else -6.0) - 1.0
    pboss = disc(A0, eA, 2.6, s_lo, -0.5 * EYE_H - 0.3)
    crank = US.glue(US.glue(US.glue(tube, armf_hub), armf), arm_c); crank = US.glue(crank, pboss)
    crank = crank.cut(disc(C0, u2, PIN_R, f2 + ARM_F_Z[0] - 0.1, f2 + ARM_F_Z[1] + 0.1)).cut(disc(A0, eA, PIN_R, s_lo - 0.1, -0.5 * EYE_H - 0.29))
    crank = crank.clean() if crank.clean().isValid() else crank
    brg = [rev([(POST_R, 0), (MR85_R, 0), (MR85_R, 2.5), (POST_R, 2.5)], pa(z0), u2) for z0 in (t_bot, t_top - 2.5)]
    roller = rev([(PIN_R, 0), (3.0, 0), (3.0, ROLLER_Z[1] - ROLLER_Z[0]), (PIN_R, ROLLER_Z[1] - ROLLER_Z[0])], C0 - (C0 @ u2) * u2 + (f2 + ROLLER_Z[0]) * u2, u2)
    rpin = disc(C0 - (C0 @ u2) * u2, u2, PIN_R, f2 + ROLLER_Z[0], f2 + ARM_F_Z[1])
    cpin = disc(A0, eA, PIN_R, s_lo + 0.5, 0.5 * EYE_H + 1.8)
    clipA = rev([(PIN_R - 0.2, 0), (3.0, 0), (3.0, 0.6), (PIN_R - 0.2, 0.6)], A0 + (0.5 * EYE_H + 0.7) * eA, eA)
    info = dict(post=[round(f2 + 0.3, 2), round(t_top, 2)], post_length_mm=round(t_top - hb, 2), post_free_mm=round(t_top - boss_top, 2), boss=[round(boss_bot, 2), round(boss_top, 2)],
                model_rocker_base_h=round(hb, 2), tube=[round(t_bot, 2), round(t_top, 2)],
                eye_low_over_tube=round(float(over.min()), 2) if len(over) else None, follower_arm_mm=round(Lf, 3), crank_arm_mm=round(Lc, 3),
                crank_pin_tilt_deg=round(math.degrees(math.acos(float(np.clip(dv["pin"] @ u2, -1, 1)))), 2), rocker_axis_to_u2_mm=round(float(np.linalg.norm(ax)), 3),
                valid=dict(crank=crank.isValid(), crank_solids=len(crank.Solids())))
    return dict(post=post, boss=boss, crank=crank, brg=brg, roller=roller, rpin=rpin, cpin=cpin, clipA=clipA), info


def rod_parts(dv):
    """the dog-bone (Ti) with its two eyes, the igubal housings (dr) and balls (on the pins: dk at A, l1a at B)"""
    A0, B0, eA, eB, d0, L = dv["A0"], dv["B0"], dv["eA"], dv["eB"], dv["d0"], dv["L"]
    eyeA = disc(A0, eA, EYE_R, -0.5 * EYE_H, 0.5 * EYE_H); eyeB = disc(B0, eB, EYE_R, -0.5 * EYE_H, 0.5 * EYE_H)
    shank = disc(A0, d0, PIN_R, EYE_R - 1.0, L - EYE_R + 1.0)
    rod = US.glue(US.glue(eyeA, shank), eyeB)
    rod = rod.cut(disc(A0, eA, HSG_R, -EYE_H, EYE_H)).cut(disc(B0, eB, HSG_R, -EYE_H, EYE_H))
    hz = 0.5 * EYE_H; ro = math.sqrt(BALL_R ** 2 - hz ** 2)
    def housing(c, e):
        h = disc(c, e, HSG_R, -hz, hz); return h.cut(cq.Solid.makeSphere(BALL_R, US.V(c), angleDegrees1=-90, angleDegrees2=90))
    def ball(c, e):
        b = cq.Solid.makeSphere(BALL_R - 0.02, US.V(c), angleDegrees1=-90, angleDegrees2=90)
        b = b.intersect(disc(c, e, BALL_R + 1, -hz + 0.05, hz - 0.05)); return b.cut(disc(c, e, PIN_R, -hz - 1, hz + 1))
    return dict(rod=rod, hsgA=housing(A0, eA), hsgB=housing(B0, eB), ballA=ball(A0, eA), ballB=ball(B0, eB)), dict(
        centres_mm=round(L, 3), eye=f"O{2 * EYE_R:g} x {EYE_H:g}", housing_open_r_mm=round(ro, 3), rod_valid=rod.isValid(), rod_solids=len(rod.Solids()))


def trim_slot(k, e, f, lo, hi, z0, z1, rs, w):
    """arc slot (half width w at radius rs, lo..hi rad in (e, f)): two concentric arcs + two semicircular ends, extruded along k"""
    P = lambda r, a: (r * math.cos(a), r * math.sin(a)); mid = 0.5 * (lo + hi); ro, ri = rs + w, rs - w
    c_hi, c_lo = np.array(P(rs, hi)), np.array(P(rs, lo)); t_hi = np.array([-math.sin(hi), math.cos(hi)]); t_lo = np.array([-math.sin(lo), math.cos(lo)])
    wp = (cq.Workplane(plane(z0 * unit(k), e, f)).moveTo(*P(ro, lo)).threePointArc(P(ro, mid), P(ro, hi)).threePointArc(tuple(c_hi + w * t_hi), P(ri, hi))
          .threePointArc(P(ri, mid), P(ri, lo)).threePointArc(tuple(c_lo - w * t_lo), P(ro, lo)).close())
    return wp.extrude(z1 - z0).val()


def horn_parts(dv, M):
    """horn hub + plate + pin + 2 screws (link 1a), all at hub K (axis uK, face fK)"""
    uK = dv["uK"]; F = float(M.fK); h = HORN; e = unit(dv["B0"] - (dv["B0"] @ uK) * uK); f = np.cross(uK, e)
    th_pin = 0.0                                                                                   # the pin direction is e (the onset horn pin)
    hub = disc(np.zeros(3), uK, h["hub_r"], F + h["hub_z"][0], F + h["hub_z"][1])
    dd = disc(np.zeros(3), uK, h["tip_r"] + 0.005, F + h["hub_z"][0] - 0.1, F + h["hub_z"][1] + 0.1).intersect(
        prism((F + h["hub_z"][0] - 0.2) * uK, e, f, [(-h["tip_flat"], -3), (h["tip_flat"], -3), (h["tip_flat"], 3), (-h["tip_flat"], 3)], [0] * 4, 2.0))
    hub = hub.cut(dd)
    plate = disc(np.zeros(3), uK, h["plate_r"], F + h["plate_z"][0], F + h["plate_z"][1])
    pinP = R_HORN * e
    plate = plate.cut(disc(pinP, uK, PIN_R, F + h["plate_z"][0] - 0.1, F + h["plate_z"][1] + 0.1))
    screws = []
    for s_ in (+1, -1):
        a = th_pin + s_ * math.pi / 2; cs = h["screw_r"] * (math.cos(a) * e + math.sin(a) * f)
        plate = plate.cut(trim_slot(uK, e, f, a - math.radians(h["screw_half_deg"]), a + math.radians(h["screw_half_deg"]),
                                    F + h["plate_z"][0] - 0.1, F + h["plate_z"][1] + 0.1, h["screw_r"], h["slot_w"]))
        csk = rev([(0, -1.6), (0.95, -1.6), (0.95, -0.6), (1.55, 0.0), (1.55, 0.2), (0, 0.2)], cs + (F + h["plate_z"][1]) * uK, uK)
        plate = plate.cut(csk)
        hub = hub.cut(disc(cs, uK, 0.65, F + h["hub_z"][0] - 0.1, F + h["hub_z"][1] + 0.1))     # M1.6 tapped (minor O1.3)
        sc = rev([(0, -2.45), (0.75, -2.45), (0.75, -0.75), (1.45, -0.05), (0, -0.05)], cs + (F + h["plate_z"][1]) * uK, uK)
        screws.append(sc)
    pin = disc(pinP, uK, PIN_R, F + h["plate_z"][0], F + h["plate_z"][1] + 0.3 + EYE_H + 2.1)
    clipB = rev([(PIN_R - 0.2, 0), (3.0, 0), (3.0, 0.6), (PIN_R - 0.2, 0.6)], dv["B0"] + (0.5 * EYE_H + 0.7) * dv["eB"], dv["eB"])
    info = dict(pin_r_mm=R_HORN, plate=f"O{2 * h['plate_r']:g} x {h['plate_z'][1] - h['plate_z'][0]:.1f} at F+{h['plate_z'][0]}..F+{h['plate_z'][1]}",
                hub=f"O{2 * h['hub_r']:g} x {h['hub_z'][1] - h['hub_z'][0]:.1f}, DD bore", trim_deg=h["screw_half_deg"],
                eye_B_bottom_over_plate_mm=round(float((dv["B0"] - 0.5 * EYE_H * dv["eB"]) @ uK - (F + h["plate_z"][1])), 3),
                valid=dict(hub=hub.isValid(), plate=plate.isValid()))
    return dict(hub=hub, plate=plate, pin=pin, screws=screws, clipB=clipB), info


# ---------------------------------------------------------------------------------------------------- K cap / arbor
def cap_k_flat(k, F, crown):
    """hub K's flat-topped clock-spring cap: v5 skirt / flange, wall to the crown (R0.5 corner), the crown counterbore O10 for
    the horn hub and the O5.6 arbor bore, the spring chamber O16 round the arbor, the outer-hook slot. Lines + arcs, revolved."""
    c = USM.CAPK; h = HORN; R = HUB_R; z0, z1, zc = LV["H1"] + 0.05 + F, LV["U1"] + F, crown + F; q = 1 - math.sqrt(0.5); r = 0.5
    wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(R, z0).lineTo(R, zc - r).threePointArc((R - r * q, zc - r * q), (R - r, zc))
          .lineTo(h["cb_r"], zc).lineTo(h["cb_r"], h["cb_z"] + F).lineTo(h["bore_r"], h["cb_z"] + F).lineTo(h["bore_r"], c["ch_z1"] + F)
          .lineTo(c["ch_r"], c["ch_z1"] + F).lineTo(c["ch_r"], c["ch_z0"] + F).lineTo(4.5, c["ch_z0"] + F).lineTo(4.5, z1).lineTo(9.0, z1).close())
    cap = xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k))
    e, f = USM.frame2(k); k = unit(k); r0, r1, w = c["hook_slot"]
    cap = cap.cut(prism(F * k + c["ch_z0"] * k, e, f, [(-r1, -w - 0.1), (-r0, -w - 0.1), (-r0, -0.1), (-r1, -0.1)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"]))
    return cap.clean() if cap.clean().isValid() else cap


def arbor_pin_geneva(k, F):
    """link 1a's K pin: v5 collar + integral O7 pin, continued as the O5 spring arbor (0.4 mm slit for the spring's inner end)
    through the crown bore to a shoulder at F + 17.15 and an O3 DD tip (flats 2.4) for the pressed horn hub"""
    c = USM.CAPK; h = HORN; k = unit(k)
    pin = PB.revolved([(0, 1.5), (4.1, 1.5), (4.1, LV["L1"]), (3.5, LV["L1"]), (3.5, LV["N1"]), (c["arbor_r"], LV["N1"]), (c["arbor_r"], h["hub_z"][0]),
                       (0, h["hub_z"][0])], k, F)
    e, f = USM.frame2(k); sw = c["slit_w"] / 2
    tip = disc(np.zeros(3), k, h["tip_r"], F + h["hub_z"][0] - 0.3, F + h["tip_top"]).intersect(           # the DD tip (flats 2.4), glued on the shoulder
        prism((F + h["hub_z"][0] - 0.5) * k, e, f, [(-h["tip_flat"], -3), (h["tip_flat"], -3), (h["tip_flat"], 3), (-h["tip_flat"], 3)], [0] * 4, h["tip_top"] - h["hub_z"][0] + 1.0))
    pin = US.glue(pin, tip)
    pin = pin.cut(prism((F + c["ch_z0"] + 0.05) * k, e, f, [(1.3, -sw), (c["arbor_r"] + 0.5, -sw), (c["arbor_r"] + 0.5, sw), (1.3, sw)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"] - 0.3))
    return pin


def hubs_geneva(M):
    """USM.hubs with hub K's flat-topped cap (horn hub counterbore, no sensor pocket, no magnet: K is slaved, never read)"""
    Uu, C, F4, hr = BM.joints4(M); out = []; rep = {}
    capK = float(M.p.get("capK", 0) or 0); crown = LV["top"] + capK
    for J, j, lo, hi in (("J1", 0, "l1a", "base"), ("K", 1, "l1a", "l1b"), ("J2", 2, "l1b", "l2"), ("J3", 3, "l3", "l2")):
        for g, n, s in US.hardware(J, Uu[j], F4[j], lo, hi):
            if " cap " in n: continue
            out.append((g, n, at(s, C[j])))
        if J != "K":
            cap, Rc = USM.cap_v5(Uu[j], F4[j]); rep["dome_crown_R"] = None if Rc is None else round(Rc, 2)
            out.append((hi, f"{J} cap O20, torispherical dome R{Rc:.1f} / R1 (tangent arcs), threaded M18x0.5 (Ti-6Al-4V)", at(cap, C[j])))
        else:
            cap = cap_k_flat(Uu[j], F4[j], crown); sp, Lsp = USM.clock_spring(Uu[j], F4[j])
            out.append((hi, f"K clock-spring cap O20 x crown F+{crown:.2f} ({capK:g} mm taller), FLAT crown with the O10 x 1.2 horn-hub counterbore and "
                            f"an O5.6 arbor bore; spring chamber O16 x {USM.CAPK['ch_z1'] - USM.CAPK['ch_z0']:.1f}, outer-hook slot, threaded M18x0.5, pinned "
                            "to link 1b's ring at assembly (spring preload index) (Ti-6Al-4V)", at(cap, C[j])))
            sp_ = USM.SPRING; rmax = sp_["r0"] + (sp_["n"] - 1) * sp_["d"]
            out.append((hi, f"K clock spring: 0.3 x 5 mm {sp_['steel']} strip, {Lsp:.1f} mm, {sp_['n']} half-turns R{sp_['r0']:g}..R{rmax:.2f}, outer hook in the cap slot, "
                            f"inner end in the arbor slit; {sp_['rate']:g} N.m/rad, {sp_['preload']:g} N.m preload on stop A = the drive's closing spring (polished spring steel)", at(sp, C[j])))
            rmax = sp_["r0"] + (sp_["n"] - 1) * sp_["d"] + sp_["t"] / 2
            rep["K"] = dict(crown_mm=crown, capK=capK, spring_length_mm=round(Lsp, 1), spring=dict(sp_), cap_valid=cap.isValid(), spring_valid=sp.isValid(),
                            spring_outer_r_mm=round(rmax, 3), chamber_r_mm=USM.CAPK["ch_r"], cap="flat crown, horn hub counterbore, no sensor (K slaved)")
            assert rmax <= USM.CAPK["ch_r"]
    return out, rep


# ---------------------------------------------------------------------------------------------------- checks
def drive_kin_check(dv, lobe_info):
    """the drive over its whole stroke in link 1b's frame: the roller (posed by beta) vs the solved pitch curve, the RSSR closure,
    the horn pin vs the eye centre"""
    arr = dv["arr"]; u2 = dv["u2"]; out = []
    for i in range(0, len(arr["ts"]), 12):
        t = float(arr["ts"][i]); dk = DV.sp * DV.kK * t
        B = arr["Bs"][i]; b, res = solve_beta(dv, B, float(arr["betas"][i]))
        C = dv["axis"] + rotm(u2, b) @ (dv["C0"] - dv["axis"])
        out.append(dict(t_deg=round(math.degrees(t), 2), dK_deg=round(math.degrees(abs(dk)), 2), beta_deg=round(math.degrees(b), 3),
                        beta_vs_redteam_deg=round(abs(math.degrees(b - float(arr["betas"][i]))), 5), roller_vs_pitch_mm=round(float(np.linalg.norm(C - arr["Cs"][i])), 5),
                        closure_mm=round(res, 7)))
    return dict(rows=out, max_roller_dev_mm=max(r["roller_vs_pitch_mm"] for r in out), max_closure_mm=max(r["closure_mm"] for r in out))


def posed_drive_check(dd, dv, n=40):
    """posed exo.glb at clip frames: roller vs lobe, horn pin vs ball, eye vs plate, rod vs K cap (signed distances, mm)"""
    import igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); C = json.load(open(os.path.join(dd, "clips.json")))
    by = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g, nm = node.split("|")[:2]; m = src.geometry[gn].copy(); m.apply_transform(T_); by[nm] = (g, m)
    def get(sub): return next(v for k, v in by.items() if sub in k)
    pairs = [("drive follower roller", "D9-01"), ("D9-03", "K clock-spring cap"), ("D9-03", "D9-05"), ("igubal housing at the horn", "D9-05"),
             ("drive horn pin O3", "igubal housing at the horn"), ("D9-03", "drive horn pin O3"), ("D9-02", "D8-03"), ("D9-03", "D8-02b"),
             ("D9-02", "D9-01"), ("D9-03", "D8-03"), ("D9-02", "D8-02b"), ("drive follower roller", "J2 cap"), ("D9-02", "J2 cap"), ("D9-03", "D9-02"),
             ("igubal ball at the horn", "igubal housing at the horn"), ("igubal ball at the crank", "igubal housing at the crank")]
    frs = [f for c in C["clips"] for f in c["frames"]]; frs = frs[::max(1, len(frs) // n)]
    res = {}
    for a_, b_ in pairs:
        try: (ga, ma), (gb, mb) = get(a_), get(b_)
        except StopIteration: continue
        XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 3000, seed=4)[0]]; worst = (1e9, None)
        for fi, f in enumerate(frs):
            G = lambda g: np.array(f["G"][g]).reshape(3, 3) if g in f["G"] else np.eye(3); T = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xw = XA @ G(ga).T + T(ga); Xb = (Xw - T(gb)) @ G(gb)
            d = float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min())
            if d < worst[0]: worst = (round(d, 3), fi)
        res[f"{a_} | {b_}"] = worst
    return res


def tess_safe(s, fine=True, report=None):
    """USP.tess without its 0.01 / 0.015 mm retries: OCC's mesher hangs (> 20 min) at 0.01 on this design's link 1b; an open
    tessellation is capped by the judges (judge/part_contact.py close_open), R7 judges the STEP"""
    vs, fs = s.tessellate(0.02 if fine else 0.08, 0.15 if fine else 0.4)
    m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
    if not fine: return m
    m, wt = USP.judge_close(USP.weld_open(m))
    if not wt:
        for tl, ta in ((0.03, 0.2), (0.05, 0.25)):
            vs, fs = s.tessellate(tl, ta)
            m2, wt2 = USP.judge_close(USP.weld_open(trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)))
            if wt2:
                m, wt = m2, wt2
                if report is not None: report["tessellation"] = [tl, ta]
                break
    if report is not None: report["watertight_judge_units"] = wt
    return m


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_geneva_rod"); ap.add_argument("--l1", default="l1_geneva-rod")
    ap.add_argument("--skip-base-search", action="store_true")
    a = ap.parse_args(MY_ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    import concept_kit as KIT
    M, rep0 = GL1.fit(); D = M.D; lg = GL1.law_geom(M); M._lg = lg
    Bf = M.B; M._bench_K = BM.chain(M, np.array([[Bf.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(Bf.idx))]))
    l1d = json.load(open(os.path.join(FULL, "designs", a.l1, "design.json"))); l1b = json.load(open(os.path.join(FULL, "designs", a.l1, "build.json")))
    same = all(abs(float(l1d["params"][k]) - float(v)) < 1e-6 for k, v in GL1.V.BEST.items() if isinstance(v, (int, float)))
    assert same, f"the L1 design {a.l1} was built from other params"
    assert abs(float(l1b["fit"]["tr"]) - float(M.tr)) < 1e-2 and np.allclose(l1b["fit"]["m"], D.m, atol=1e-2), "the fit differs from the L1's"
    assert np.allclose(l1b["stack"]["f"], M.f, atol=1e-2) and abs(l1b["stack"]["fK"] - M.fK) < 1e-2
    Uu, C, F4, hr = BM.joints4(M)
    print(f"fit (verifier CorrModel + BEST) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']} hub levels "
          f"{np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f} ({time.time() - t0:.0f} s)", flush=True)
    dv = drive_solution(M)
    print(f"drive V0: L {dv['L']:.3f} mm, {json.dumps({k: v for k, v in dv['rep'].items() if k in ('rocker_turn_deg', 'lift_mm', 'lobe_r_onset', 'lobe_r_end', 'pa_deg', 'rod_cap_clear_min')})}", flush=True)
    # ---- stops: K from the model (pair placed by the L1), J2 = the L1's window (q2lo .. the law's end = the q2 dowel stop B)
    l1_stops = l1d["stack_mm"]["stops"]; stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1_stops[key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1_stops[key].get("pair")))
    rep = dict(fit=dict(params=dict(GL1.G.PARAMS, **GL1.V.BEST), source="docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py CorrModel + BEST", gap_near_touch=rep0["gap"],
                        hub_levels_J1_K_J2_J3=[float(x) for x in F4], tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr],
                        fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths, rounds; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"])
                      for k, v in stops.items()}, j2_push_limit=USM.j2_push_limit(), drive_redteam_check=dv["chk"])
    parts = []
    hw, rep["hubs"] = hubs_geneva(M); parts += hw
    USM.arbor_pin = arbor_pin_geneva                                                            # link 1a's K pin = the horn's axle (module global, read at call time)
    lk, rep["links"] = USM.build_links(M, stops)
    # link 2: the J2 upper ring turned to O18 under the lobe ring; link 1b: the rocker boss
    cr = BM.joints4(M)
    ring_cut = rev([(9.0, LOBE_Z[0]), (HUB_R + 0.8, LOBE_Z[0]), (HUB_R + 0.8, LV["H1"] + 0.2), (9.0, LV["H1"] + 0.2)], dv["f2"] * dv["u2"], dv["u2"])
    bc, bc_info = bell_crank(dv)
    for i, (g, n, s) in enumerate(lk):
        if n.startswith("D8-03"):
            s2 = s.cut(ring_cut); s2 = s2.clean() if s2.clean().isValid() else s2
            lk[i] = (g, n.replace("flies over", "upper ring turned to O18 over F+6.15..8.95 for the lobe ring, flies over"), s2)
        if n.startswith("D8-02b"):                                                          # the rocker boss stays a separate bush (a glued boss hung OCC's
            lk[i] = (g, n.replace("J2 pad", "J2 pad (carries the rocker post bush)"), s)        # tessellation of link 1b for 20+ min): same member, no boolean
    parts += lk
    lobe, rep["lobe"] = lobe_ring(dv)
    rp, rep["rod"] = rod_parts(dv); hp, rep["horn"] = horn_parts(dv, M); rep["bell crank"] = bc_info
    parts += [("l2", f"D9-01 drive lobe ring: 17-4PH H900, wire-EDM, the exact RSSR profile r {rep['lobe']['profile_r'][0]:.2f} -> {rep['lobe']['profile_r'][1]:.2f} mm "
                     f"({rep['lobe']['arcs']} 3-point arcs), R3 concave into the O20.2 dwell, bore O18 on link 2's turned ring, keyed by an O1 dowel at the onset q2 "
                     f"{lg['law']['q2hi_deg']:.3f} deg, F+{LOBE_Z[0]}..F+{LOBE_Z[1]}", lobe),
              ("l1b", f"drive rocker post bush: Ti-6Al-4V O9 x {bc_info['boss'][1] - bc_info['boss'][0]:.1f}, in link 1b's J2 pad (bonded; the post is pressed through bush and pad)", bc["boss"]),
              ("l1b", f"drive rocker post: O5 x {bc_info['post'][1] - bc_info['post'][0]:.1f} 17-4PH H900, pressed 3.7 mm through link 1b's J2 pad + boss, axis || J2 "
                      f"({bc_info['rocker_axis_to_u2_mm']:.2f} mm off it)", bc["post"]),
              ("dk", f"D9-02 drive bell crank (Ti-6Al-4V): tube O10 on the post, follower arm {bc_info['follower_arm_mm']:.2f} mm, crank arm {bc_info['crank_arm_mm']:.2f} mm "
                     f"+ crank-pin boss tilted {bc_info['crank_pin_tilt_deg']:.1f} deg (square to the rod)", bc["crank"]),
              ("dk", "drive bell crank bearing 1 MR85ZZ 5x8x2.5", bc["brg"][0]), ("dk", "drive bell crank bearing 2 MR85ZZ 5x8x2.5 (wave-washer preloaded)", bc["brg"][1]),
              ("dk", "drive follower roller MR63ZZ 3x6x2.5 (polished)", bc["roller"]), ("dk", "drive roller pin O3 h6 hardened (polished)", bc["rpin"]),
              ("dk", "drive crank pin O3 h6 hardened (polished)", bc["cpin"]), ("dk", "drive crank pin clip DIN 6799 RS 2.3 (polished)", bc["clipA"]),
              ("dk", "drive igubal ball at the crank (iglidur, KGLM-03 class)", rp["ballA"]),
              ("dr", f"D9-03 drive pushrod: Ti-6Al-4V dog-bone, O3 shank, centres {dv['L']:.2f} +- 0.02 mm, two O13 x {EYE_H:g} eyes", rp["rod"]),
              ("dr", "drive igubal housing at the crank (iglidur, pressed, KGLM-03 class O10)", rp["hsgA"]),
              ("dr", "drive igubal housing at the horn (iglidur, pressed, KGLM-03 class O10)", rp["hsgB"]),
              ("l1a", "drive igubal ball at the horn (iglidur, KGLM-03 class)", rp["ballB"]),
              ("l1a", "D9-04 drive horn hub: Ti-6Al-4V O9.4 x 1.2, DD bore pressed on link 1a's arbor tip, 2x M1.6 tapped", hp["hub"]),
              ("l1a", f"D9-05 drive horn plate: Ti-6Al-4V O13 x 1.4, horn pin at r {R_HORN} mm, 2x +-5 deg trim slots for M1.6 countersunk", hp["plate"]),
              ("l1a", "drive horn pin O3 h6 hardened, pressed + staked (polished)", hp["pin"]),
              ("l1a", "drive horn screw 1 M1.6x2.5 ISO 7046 countersunk (polished)", hp["screws"][0]), ("l1a", "drive horn screw 2 M1.6x2.5 ISO 7046 countersunk (polished)", hp["screws"][1]),
              ("l1a", "drive horn pin clip DIN 6799 RS 2.3 (polished)", hp["clipB"])]
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = USP.knee_link(M)
    ks_deg = (l1d.get("build_fixes") or {}).get("knee_stop_deg")
    if ks_deg is not None:
        s_, rep["knee stop"] = USM.knee_stop_on(M, s_, ks_deg, M._bench_K)
        n_ = n_.replace(" (Ti-6Al-4V)", f" + knee stop tooth behind pin a (its face meets the E strap's side at knee angle {ks_deg:g} deg) (Ti-6Al-4V)")
    parts.append((g_, n_, s_))
    Cc = json.load(open(os.path.join(FULL, "designs", a.l1, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = USP.arm_side(M, l1b["mount"], cposes); parts += [(g, n, s) for g, _, n, s in arm]
    Wj = json.load(open(os.path.join(FULL, "designs", a.l1, "workspace.json"))); frames = []; rel = []
    allf = [f for cl in Cc["clips"] for f in cl["frames"]] + [p for p in Wj["poses"] if p.get("eval_feasible")]
    for fi, f in enumerate(allf):
        g = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        Gb, Tb, G1, T1 = g("base"), t_("base"), g("l1a"), t_("l1a"); rel.append((Gb.T @ G1, Gb.T @ (T1 - Tb)))
        if fi % 3 == 0: frames.append((Gb, Tb, G1, T1))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    l1_body = next(s for g, n, s in parts if n.startswith("D8-02a"))
    if a.skip_base_search: USP.EAR_DZ = ()
    bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames); parts.append((bp[0], bp[2], bp[3]))
    # ---- export
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")): os.remove(os.path.join(dd, "step", f))
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith(("D8-", "D9-")) and any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and (not hwr or "horn screw" in n):                                     # R7 asks a STEP of the horn screws (not on its catalogue list)
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        trep = {}; m = tess_safe(s, fine=not user, report=trep)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        nl = n.lower()
        if user: mat, rho = "user part", None
        elif "iglidur" in nl or "igubal" in nl: mat, rho = "iglidur", USP.IGL
        elif "bearing" in nl or "mr63zz" in nl or "mr85zz" in nl: mat, rho = "bearing steel", 7.8
        elif "17-4ph" in nl: mat, rho = "17-4PH", 7.8
        elif "dowel" in nl or ("pin o3" in nl and "drive" in nl): mat, rho = "hardened steel (polished)", 7.85
        elif "clock spring" in nl: mat, rho = "1.4310 spring steel (polished)", 7.9
        elif hwr: mat, rho = "stainless (polished)", 7.9
        elif "7075-T6" in n: mat, rho = "7075-T6 (BOTTOM merged with the pad mount)", 2.81
        elif n.startswith("UPPER ARM CUFF"): mat, rho = "AlSi10Mg", 2.68
        else: mat, rho = "Ti-6Al-4V", USP.TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L2 user-style", FACES={"1": round(float(F4[0]), 2), "K": round(float(F4[1]), 2), "2": round(float(F4[2]), 2),
                                                                 "3": round(float(F4[3]), 2)}, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    # ---- clips / workspace: the L1's frames + the posed drive groups
    rep["posing"] = dict(clips=pose_groups(dv, os.path.join(FULL, "designs", a.l1, "clips.json"), os.path.join(dd, "clips.json"), "clips"),
                         workspace=pose_groups(dv, os.path.join(FULL, "designs", a.l1, "workspace.json"), os.path.join(dd, "workspace.json"), "workspace"),
                         rule="groups dk (bell crank) / dr (rod) added per frame from link 1a / 1b's frames (exact RSSR closure); every other group = the L1's frames")
    d = dict(l1d); d.update(id=a.out, label="geneva-tail-knuckle-pinknee-3r rod (the verifier's corrected config), full CAD in the user's style",
                            level="L2 user-style (full CAD of the generation-5 winner)", l1_design=a.l1,
                            built_with="pipeline/conformal/param_cad/user_style_geneva.py (user_style_minarc / user_style_pinknee parts: v5 O20 hubs, K flat clock-spring cap + "
                                       "horn hub / plate / pin, 4-strip machined bars 1a / 1b / 2, O3 dowel-in-arc-slot stops (K opposed pair, J2 single), member 3, knee link + "
                                       "IGLIDUR-PIN stacks, BOTTOM fused with the pad mount; the drive: lobe ring, bell crank on a post, MR63ZZ follower, dog-bone pushrod with "
                                       f"igubal spherical bearings) on the L1 design's frames ({a.l1}) + the posed drive groups dk / dr")
    d["drive_build"] = dict(kind="V0 side +1 (docs/research/geneva_rod_drive_redteam.md): lobe ring (l2) -> MR63ZZ roller on the bell crank (dk, on a post on link 1b) -> "
                                 "dog-bone pushrod with 2 igubal spherical bearings (dr) -> horn pin at r 2.493 on the horn plate (l1a, on the arbor)",
                            rod_centres_mm=round(dv["L"], 3), post_mm=bc_info["post_length_mm"], kK=GL1.V.BEST.get("kK"))
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; rep["invalid_or_multi_solid"] = bad
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'}; posing {rep['posing']} ({time.time() - t0:.0f} s)", flush=True)
    rep["drive_kin"] = drive_kin_check(dv, rep["lobe"])
    rep["drive_posed"] = posed_drive_check(dd, dv)
    _sp = importlib.util.spec_from_file_location("declare_slaved", os.path.join(REPO, "docs", "research", "geneva_rod_drive", "declare_slaved.py"))
    _ds = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_ds); rep["slaved"] = [_ds.declaration(rep)]   # the dynamics judge's slaved-K declaration
    print(f"drive: kin {rep['drive_kin']['max_roller_dev_mm']} mm / closure {rep['drive_kin']['max_closure_mm']}; posed {rep['drive_posed']}", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if ks_deg is not None: M.p["ang_min"] = round(180.0 - float(ks_deg), 4)
    rep["check"] = USM.check_frames(M, dd, l1_stops, stops)
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), all_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]),
                                   max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                   dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] for r in rep["check"]))
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"kinematics: {rep['kinematics_exact']}; done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
