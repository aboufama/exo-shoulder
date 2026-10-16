"""Gen-5 CAD fix (docs/research/geneva-rod-gen5_fix.md): user_geneva_rod -> user_geneva_rod_v2. Rebuilds ONLY the drive parts
(lobe ring, bell crank set, pushrod set, horn set) and repairs link 1a's solid; every other part, STEP and frame is copied
unchanged from the source build (the full builder takes ~20 min to hours with OCC hangs; nothing else changes).

The changes (each closes an item of the independent check, pipeline/full-exo/designs/user_geneva_rod/VERIFY.md):
  igubal     the rod-end eyes at the real igus KGLM-03 width: O13 x 6 eyes, O10 x 6 housings, balls truncated at +-3.0
             (was O13 x 4 / 3.9 mm). At the crank the builder's own rule lowers the tube top under the wider eye; at the horn
             the rod line rises by 1.0 mm (eye 0.5 mm over the plate again) + the horn hub growth below; the RSSR, the
             crank-pin tilt and the lobe are RE-SOLVED by the red team's drive.py with the new rod-end height (hB).
  horn       the horn hub grows from 1.2 to HUB_H 3.8 mm above the crown counterbore floor so the 2x M1.6 screws (now
             ISO 7046 M1.6 x 5) engage 3.6 mm of thread (2.25 d; was 1.2 mm = 0.75 d); plate O13 x 1.4 on top.
  clips      DIN 6799 RS 2.3 on the O3 crank and horn pins sit in a cut groove (O2.3 x 0.64) with a 1.0 mm land past it
             (was: no groove, 0.5-0.6 mm land).
  bell crank retained on its post: the post runs 2.05 mm past the top MR85ZZ, a 0.3 mm shim washer on the inner ring, a
             DIN 6799 RS 4 clip in an O4 x 0.74 groove, 1.0 mm land (the wave-washer preload now has its reaction); the
             tube top drops 2.1 mm under the crank eye to make the room.
  roller     the MR63ZZ inner race is pressed on the O3 m6 roller pin (+ retaining compound), the pin pressed in the follower
             arm: the roller cannot walk off (stated, no geometry change).
  lobe       the lobe fix chosen in the judge (docs/research/geneva_rod_drive/lobe_skin.py): --a-f / --a-c / --rr / --dz.
  link 1a    the source STEP repaired by OCC ShapeFix (one valid solid, R7) and its name corrected (no magnet pocket: K is
             slaved, never read; the arbor ends in the DD O3 tip for the horn hub).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_geneva_fix.py [--src user_geneva_rod] [--out user_geneva_rod_v2]
        [--a-f 9.0] [--a-c 9.0] [--rr 3.0] [--dz 0.0] [--hub-h 3.8] [--eye-h 6.0]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import user_style_geneva as USG                                                          # noqa: E402 (the gen-5 builder, its functions reused)
import numpy as np, cadquery as cq, trimesh                                              # noqa: E402
DV, GL1, USP, US = USG.DV, USG.GL1, USG.USP, USG.US
FULL, disc, rev, unit, prism = USG.FULL, USG.disc, USG.rev, USG.unit, USG.prism
PIN_R = USG.PIN_R
CLIP23 = dict(groove_r=1.15, groove_w=0.64, s=0.6, outer_r=3.15, gap=0.15, land=1.0)      # DIN 6799 RS 2.3 (shaft 3-4)
CLIP4 = dict(groove_r=2.0, groove_w=0.74, s=0.7, outer_r=4.5, shim=0.3, land=1.0)          # DIN 6799 RS 4 (shaft 5-7) + 0.3 shim O5.1/O6.5


def grooved_pin(c, e, z0, face):
    """O3 pin along e from z0 to face + gap + groove + land, with the DIN 6799 RS 2.3 groove; + its clip in the groove"""
    k = CLIP23; g0 = face + k["gap"]; g1 = g0 + k["groove_w"]; end = g1 + k["land"]
    pin = disc(c, e, PIN_R, z0, end).cut(rev([(k["groove_r"], 0), (PIN_R + 0.5, 0), (PIN_R + 0.5, k["groove_w"]), (k["groove_r"], k["groove_w"])], np.asarray(c) + g0 * unit(e), e))
    clip = rev([(k["groove_r"] + 0.01, 0), (k["outer_r"], 0), (k["outer_r"], k["s"]), (k["groove_r"] + 0.01, k["s"])], np.asarray(c) + (g0 + 0.02) * unit(e), e)
    return pin, clip, dict(groove=[round(g0, 3), round(g1, 3)], land_mm=k["land"], pin_end=round(end, 3))


def bell_crank_fix(dv):
    """USG.bell_crank with the tube top lowered for the post clip, the post retained (shim + RS 4 clip in a groove), grooved crank pin"""
    u2, ax = dv["u2"], dv["axis"]; hb = float(dv["Pb"] @ u2); f2 = dv["f2"]; pa = lambda h: ax + h * u2
    EYE_H, EYE_R, TUBE_R, TUBE_BORE, MR85_R, POST_R = USG.EYE_H, USG.EYE_R, USG.TUBE_R, USG.TUBE_BORE, USG.MR85_R, USG.POST_R
    ARM_F_Z, ROLLER_Z = USG.ARM_F_Z, USG.ROLLER_Z
    eA, A0 = dv["eA"], dv["A0"]; e1 = unit(np.cross(eA, u2)); e2 = np.cross(eA, e1)
    ring = [A0 - 0.5 * EYE_H * eA + EYE_R * (math.cos(t) * e1 + math.sin(t) * e2) for t in np.linspace(0, 2 * math.pi, 361)]
    ring += [A0 - 0.5 * EYE_H * eA + rr_ * (math.cos(t) * e1 + math.sin(t) * e2) for rr_ in (2.0, 4.0) for t in np.linspace(0, 2 * math.pi, 73)]
    ring = np.array(ring); w = ring - ax; rad = np.linalg.norm(w - np.outer(w @ u2, u2), axis=1)
    over = ring[rad < CLIP4["outer_r"] + 0.6] @ u2; over_t = ring[rad < TUBE_R + 0.6] @ u2
    k4 = CLIP4; room = k4["shim"] + k4["groove_w"] + k4["land"]                              # post past the tube top: shim, groove, land
    t_top = min(hb + 20.0, float(over.min()) - 0.5 - room, float(over_t.min()) - 0.5)
    boss_bot, boss_top = f2 + 0.5, f2 + 4.0; t_bot = boss_top + 0.3
    post_end = t_top + room
    post = disc(ax, u2, POST_R, f2 + 0.3, post_end).cut(rev([(k4["groove_r"], 0), (POST_R + 0.5, 0), (POST_R + 0.5, k4["groove_w"]), (k4["groove_r"], k4["groove_w"])], pa(t_top + k4["shim"]), u2))
    shim = rev([(POST_R + 0.05, 0), (3.25, 0), (3.25, k4["shim"] - 0.02), (POST_R + 0.05, k4["shim"] - 0.02)], pa(t_top + 0.01), u2)
    pclip = rev([(k4["groove_r"] + 0.01, 0), (k4["outer_r"], 0), (k4["outer_r"], k4["s"]), (k4["groove_r"] + 0.01, k4["s"])], pa(t_top + k4["shim"] + 0.02), u2)
    boss = disc(ax, u2, 4.5, boss_bot, boss_top)
    tube = rev([(TUBE_BORE, 0), (TUBE_R, 0), (TUBE_R, t_top - t_bot), (TUBE_BORE, t_top - t_bot)], pa(t_bot), u2)
    for z0, z1 in ((0.0, 2.5), (t_top - t_bot - 2.5, t_top - t_bot)): tube = tube.cut(rev([(0, z0 - 0.01), (MR85_R, z0 - 0.01), (MR85_R, z1 + 0.01), (0, z1 + 0.01)], pa(t_bot), u2))
    C0 = dv["C0"]; cr = C0 - ax - (C0 @ u2) * u2; Lf = float(np.linalg.norm(cr)); xf = unit(cr); yf = np.cross(u2, xf)
    armf = USP.stadium(pa(f2 + ARM_F_Z[0]), xf, yf, Lf, 2.5, ARM_F_Z[1] - ARM_F_Z[0])
    bore = disc(ax, u2, TUBE_BORE, t_bot - 1.0, t_top + 1.0); armf = armf.cut(bore)
    armf_hub = rev([(TUBE_BORE, 0), (TUBE_R, 0), (TUBE_R, ARM_F_Z[1] - ARM_F_Z[0]), (TUBE_BORE, ARM_F_Z[1] - ARM_F_Z[0])], pa(f2 + ARM_F_Z[0]), u2)
    ca = A0 - ax - (A0 @ u2) * u2; Lc = float(np.linalg.norm(ca)); xc = unit(ca); yc = np.cross(u2, xc)
    arm_c = USP.stadium(pa(t_top - 2.0), xc, yc, Lc, 3.0, 2.0).cut(bore)
    s_lo = None
    for s_ in np.linspace(-14, 0, 281):
        if (A0 + s_ * eA) @ u2 >= t_top: s_lo = s_; break
    s_lo = (s_lo if s_lo is not None else -6.0) - 1.0
    pboss = disc(A0, eA, 2.6, s_lo, -0.5 * EYE_H - 0.3)
    crank = US.glue(US.glue(US.glue(tube, armf_hub), armf), arm_c); crank = US.glue(crank, pboss)
    crank = crank.cut(disc(C0, u2, PIN_R, f2 + ARM_F_Z[0] - 0.1, f2 + ARM_F_Z[1] + 0.1)).cut(disc(A0, eA, PIN_R, s_lo - 0.1, -0.5 * EYE_H - 0.29))
    crank = crank.clean() if crank.clean().isValid() else crank
    brg = [rev([(POST_R, 0), (MR85_R, 0), (MR85_R, 2.5), (POST_R, 2.5)], pa(z0), u2) for z0 in (t_bot, t_top - 2.5)]
    roller = rev([(PIN_R, 0), (3.0, 0), (3.0, ROLLER_Z[1] - ROLLER_Z[0]), (PIN_R, ROLLER_Z[1] - ROLLER_Z[0])], C0 - (C0 @ u2) * u2 + (f2 + ROLLER_Z[0]) * u2, u2)
    rpin = disc(C0 - (C0 @ u2) * u2, u2, PIN_R, f2 + ROLLER_Z[0], f2 + ARM_F_Z[1])
    cpin, clipA, cinfo = grooved_pin(A0, eA, s_lo + 0.5, 0.5 * EYE_H)
    info = dict(post=[round(f2 + 0.3, 2), round(post_end, 2)], post_length_mm=round(post_end - hb, 2), post_free_mm=round(post_end - boss_top, 2),
                boss=[round(boss_bot, 2), round(boss_top, 2)], model_rocker_base_h=round(hb, 2), tube=[round(t_bot, 2), round(t_top, 2)],
                eye_low_over_post_clip_zone=round(float(over.min()), 2), post_end_below_eye_mm=round(float(over.min()) - post_end, 2),
                follower_arm_mm=round(Lf, 3), crank_arm_mm=round(Lc, 3),
                crank_pin_tilt_deg=round(math.degrees(math.acos(float(np.clip(dv["pin"] @ u2, -1, 1)))), 2), rocker_axis_to_u2_mm=round(float(np.linalg.norm(ax)), 3),
                post_retention="0.3 shim O5.1/O6.5 on the top MR85ZZ inner ring + DIN 6799 RS 4 in an O4 x 0.74 groove, 1.0 mm land",
                crank_pin=cinfo, roller_retention="MR63ZZ inner race pressed on the O3 m6 pin (+ retaining compound); pin pressed in the follower arm",
                valid=dict(crank=crank.isValid(), crank_solids=len(crank.Solids()), post=post.isValid()))
    return dict(post=post, boss=boss, crank=crank, brg=brg, roller=roller, rpin=rpin, cpin=cpin, clipA=clipA, shim=shim, pclip=pclip), info


def horn_parts_fix(dv, M):
    """USG.horn_parts with the taller hub (HUB_H), M1.6 x 5 screws (2.25 d of thread), grooved horn pin"""
    h = USG.HORN; uK = dv["uK"]; F = float(M.fK); e = unit(dv["B0"] - (dv["B0"] @ uK) * uK); f = np.cross(uK, e)
    hub = disc(np.zeros(3), uK, h["hub_r"], F + h["hub_z"][0], F + h["hub_z"][1])
    dd = disc(np.zeros(3), uK, h["tip_r"] + 0.005, F + h["hub_z"][0] - 0.1, F + h["hub_z"][1] + 0.1).intersect(
        prism((F + h["hub_z"][0] - 0.2) * uK, e, f, [(-h["tip_flat"], -3), (h["tip_flat"], -3), (h["tip_flat"], 3), (-h["tip_flat"], 3)], [0] * 4, h["hub_z"][1] - h["hub_z"][0] + 0.4))
    hub = hub.cut(dd)
    plate = disc(np.zeros(3), uK, h["plate_r"], F + h["plate_z"][0], F + h["plate_z"][1]); pinP = USG.R_HORN * e
    plate = plate.cut(disc(pinP, uK, PIN_R, F + h["plate_z"][0] - 0.1, F + h["plate_z"][1] + 0.1)); screws = []; L = 5.0
    for s_ in (+1, -1):
        a = s_ * math.pi / 2; cs = h["screw_r"] * (math.cos(a) * e + math.sin(a) * f)
        plate = plate.cut(USG.trim_slot(uK, e, f, a - math.radians(h["screw_half_deg"]), a + math.radians(h["screw_half_deg"]), F + h["plate_z"][0] - 0.1, F + h["plate_z"][1] + 0.1, h["screw_r"], h["slot_w"]))
        plate = plate.cut(rev([(0, -1.6), (0.95, -1.6), (0.95, -0.6), (1.55, 0.0), (1.55, 0.2), (0, 0.2)], cs + (F + h["plate_z"][1]) * uK, uK))
        hub = hub.cut(disc(cs, uK, 0.65, F + h["hub_z"][0] + 0.15, F + h["hub_z"][1] + 0.1))         # M1.6 tapped blind (minor O1.3), 0.15 floor
        screws.append(rev([(0, -L), (0.75, -L), (0.75, -0.75), (1.45, -0.05), (0, -0.05)], cs + (F + h["plate_z"][1]) * uK, uK))
    face = float(dv["B0"] @ uK) - 0.0                                                             # pin along uK; eB = uK
    pin, clipB, pinfo = grooved_pin(pinP, uK, F + h["plate_z"][0], face + 0.5 * USG.EYE_H)
    eng = (F + h["hub_z"][1]) - (F + h["plate_z"][1] - L)
    info = dict(pin_r_mm=USG.R_HORN, plate=f"O{2 * h['plate_r']:g} x {h['plate_z'][1] - h['plate_z'][0]:.1f} at F+{h['plate_z'][0]:.2f}..F+{h['plate_z'][1]:.2f}",
                hub=f"O{2 * h['hub_r']:g} x {h['hub_z'][1] - h['hub_z'][0]:.1f}, DD bore", trim_deg=h["screw_half_deg"], screws="2x M1.6 x 5 ISO 7046",
                thread_engagement_mm=round(eng, 2), thread_engagement_d=round(eng / 1.6, 2), horn_pin=pinfo,
                eye_B_bottom_over_plate_mm=round(float((dv["B0"] - 0.5 * USG.EYE_H * dv["eB"]) @ uK - (F + h["plate_z"][1])), 3),
                valid=dict(hub=hub.isValid(), plate=plate.isValid(), pin=pin.isValid()))
    return dict(hub=hub, plate=plate, pin=pin, screws=screws, clipB=clipB), info


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--src", default="user_geneva_rod"); ap.add_argument("--out", default="user_geneva_rod_v2"); ap.add_argument("--l1", default="l1_geneva-rod")
    ap.add_argument("--a-f", type=float, default=9.0); ap.add_argument("--a-c", type=float, default=9.0); ap.add_argument("--rr", type=float, default=3.0)
    ap.add_argument("--dz", type=float, default=0.0); ap.add_argument("--hub-h", type=float, default=3.8); ap.add_argument("--eye-h", type=float, default=6.0)
    a = ap.parse_args(MY_ARGV); t0 = time.time()
    src = os.path.join(FULL, "designs", a.src); dd = os.path.join(FULL, "designs", a.out)
    if os.path.exists(dd): shutil.rmtree(dd)
    os.makedirs(os.path.join(dd, "step")); os.makedirs(os.path.join(dd, "judge"))
    # ---- the drive's new constants (module globals the builder's functions read at call time)
    USG.EYE_H = a.eye_h; USG.A_F, USG.A_C, USG.RR = a.a_f, a.a_c, a.rr
    USG.LOBE_Z = tuple(z + a.dz for z in USG.LOBE_Z); USG.ROLLER_Z = tuple(z + a.dz for z in USG.ROLLER_Z); USG.ARM_F_Z = tuple(z + a.dz for z in USG.ARM_F_Z)
    hub0 = USG.HORN["hub_z"][0]; USG.HORN["hub_z"] = (hub0, hub0 + a.hub_h); USG.HORN["plate_z"] = (hub0 + a.hub_h, hub0 + a.hub_h + 1.4)
    rise = (a.eye_h - 4.0) / 2 + (a.hub_h - 1.2)                                                  # rod-end centre over the old one (eye 0.5 over the plate kept)
    DV.hB = DV.hB + rise; DV.hL = DV.hL + a.dz
    M, rep0 = GL1.fit(); lg = GL1.law_geom(M); M._lg = lg
    dv = USG.drive_solution(M)
    print(f"drive: L {dv['L']:.3f} mm, rod end B +{rise:.2f} mm; {json.dumps({k: v for k, v in dv['rep'].items() if k in ('rocker_turn_deg', 'lift_mm', 'lobe_r_onset', 'lobe_r_end', 'pa_deg', 'rod_cap_clear_min')})}", flush=True)
    lobe, lobe_info = USG.lobe_ring(dv)
    bc, bc_info = bell_crank_fix(dv); rp, rod_info = USG.rod_parts(dv); hp, horn_info = horn_parts_fix(dv, M)
    # link 1a: the source STEP, ShapeFix'ed
    sd0 = os.path.join(src, "step"); f1a = next(f for f in os.listdir(sd0) if "D8-02a" in f)
    l1a = cq.importers.importStep(os.path.join(sd0, f1a)).val(); v0 = l1a.isValid(); l1a_fix = l1a.fix(); l1a_info = dict(source_valid=v0, fixed_valid=l1a_fix.isValid(), solids=len(l1a_fix.Solids()))
    if not l1a_fix.isValid():
        try:
            from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
            u = ShapeUpgrade_UnifySameDomain(l1a_fix.wrapped, True, True, True); u.Build(); l1a_fix = cq.Shape.cast(u.Shape()).fix(); l1a_info["unify"] = l1a_fix.isValid()
        except Exception as e: l1a_info["unify_error"] = str(e)
    print(f"link 1a: {l1a_info}", flush=True)
    rn = lambda n: n.replace("(0.4 mm slit, O3 magnet pocket)", "(0.4 mm slit, DD O3 tip for the horn hub; no magnet: K is slaved, never read)")
    lb = lobe_info
    new = [("l2", f"D9-01 drive lobe ring: 17-4PH H900, wire-EDM, the exact RSSR profile r {lb['profile_r'][0]:.2f} -> {lb['profile_r'][1]:.2f} mm "
                  f"({lb['arcs']} 3-point arcs), R{a.rr:g} concave into the O20.2 dwell, bore O18 on link 2's turned ring, keyed by an O1 dowel at the onset q2 "
                  f"{lg['law']['q2hi_deg']:.3f} deg, F+{USG.LOBE_Z[0]:.2f}..F+{USG.LOBE_Z[1]:.2f}", lobe),
           ("l1b", f"drive rocker post: O5 x {bc_info['post'][1] - bc_info['post'][0]:.1f} 17-4PH H900, pressed through link 1b's J2 pad + boss, axis || J2, "
                   f"DIN 6799 RS 4 groove at the top", bc["post"]),
           ("l1b", "drive rocker post bush: Ti-6Al-4V O9 x 3.5, in link 1b's J2 pad (bonded; the post is pressed through bush and pad)", bc["boss"]),
           ("dk", f"D9-02 drive bell crank (Ti-6Al-4V): tube O10 on the post, follower arm {bc_info['follower_arm_mm']:.2f} mm, crank arm {bc_info['crank_arm_mm']:.2f} mm "
                  f"+ crank-pin boss tilted {bc_info['crank_pin_tilt_deg']:.1f} deg (square to the rod)", bc["crank"]),
           ("dk", "drive bell crank bearing 1 MR85ZZ 5x8x2.5", bc["brg"][0]), ("dk", "drive bell crank bearing 2 MR85ZZ 5x8x2.5 (wave-washer preloaded against the post clip)", bc["brg"][1]),
           ("l1b", "drive post shim washer O5.1/O6.5 x 0.3 stainless (polished)", bc["shim"]), ("l1b", "drive post clip DIN 6799 RS 4 (polished)", bc["pclip"]),
           ("dk", f"drive follower roller MR63ZZ 3x6x2.5, inner race pressed on the pin (polished)", bc["roller"]), ("dk", "drive roller pin O3 m6 hardened, pressed (polished)", bc["rpin"]),
           ("dk", "drive crank pin O3 h6 hardened, DIN 6799 groove (polished)", bc["cpin"]), ("dk", "drive crank pin clip DIN 6799 RS 2.3 (polished)", bc["clipA"]),
           ("dk", "drive igubal ball at the crank (iglidur, igus KGLM-03, 6 wide)", rp["ballA"]),
           ("dr", f"D9-03 drive pushrod: Ti-6Al-4V dog-bone, O3 shank, centres {dv['L']:.2f} +- 0.02 mm, two O13 x {USG.EYE_H:g} eyes", rp["rod"]),
           ("dr", "drive igubal housing at the crank (iglidur, pressed, igus KGLM-03 O10 x 6)", rp["hsgA"]),
           ("dr", "drive igubal housing at the horn (iglidur, pressed, igus KGLM-03 O10 x 6)", rp["hsgB"]),
           ("l1a", "drive igubal ball at the horn (iglidur, igus KGLM-03, 6 wide)", rp["ballB"]),
           ("l1a", f"D9-04 drive horn hub: Ti-6Al-4V O9.4 x {a.hub_h:.1f}, DD bore pressed on link 1a's arbor tip, 2x M1.6 tapped blind", hp["hub"]),
           ("l1a", f"D9-05 drive horn plate: Ti-6Al-4V O13 x 1.4, horn pin at r {USG.R_HORN} mm, 2x +-5 deg trim slots for M1.6 countersunk", hp["plate"]),
           ("l1a", "drive horn pin O3 h6 hardened, pressed + staked, DIN 6799 groove (polished)", hp["pin"]),
           ("l1a", "drive horn screw 1 M1.6x5 ISO 7046 countersunk (polished)", hp["screws"][0]), ("l1a", "drive horn screw 2 M1.6x5 ISO 7046 countersunk (polished)", hp["screws"][1]),
           ("l1a", "drive horn pin clip DIN 6799 RS 2.3 (polished)", hp["clipB"])]
    # ---- splice: every source part except the drive set and link 1a, then link 1a (fixed) + the new drive set
    P0 = json.load(open(os.path.join(src, "parts_full.json"))); pf_src = P0["parts"]
    drive_like = lambda n: n.startswith("D9-") or n.startswith("drive ")
    keep = [p for p in pf_src if not drive_like(p["name"]) and not p["name"].startswith("D8-02a")]
    old_1a = next(p for p in pf_src if p["name"].startswith("D8-02a"))
    sc0 = trimesh.load(os.path.join(src, "exo.glb")); by_k = {}
    for node in sc0.graph.nodes_geometry:
        T_, gn = sc0.graph[node]; m = sc0.geometry[gn].copy(); m.apply_transform(T_); by_k[int(node.split("|")[-1])] = (node, m)
    sc = trimesh.Scene(); pf = []
    for p in keep:
        node, m = by_k[p["k"]]; sc.add_geometry(m, node_name=node, geom_name=node); pf.append(p)
        for f in os.listdir(sd0):
            if f.startswith(f"{int(p['k']):02d}_"): shutil.copy(os.path.join(sd0, f), os.path.join(dd, "step", f))
    k_next = max(p["k"] for p in pf_src) + 1
    adds = [(old_1a["group"], rn(old_1a["name"]), l1a_fix)] + new
    for i, (g, n, s) in enumerate(adds):
        k = old_1a["k"] if i == 0 else k_next + i - 1
        nl = n.lower(); hwr = not n.startswith(("D8-", "D9-")) and any(w in nl for w in ("screw", "clip", "shim"))
        if not hwr or "horn screw" in n:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{k:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        trep = {}; m = USG.tess_safe(s, fine=True, report=trep); node = f"{g}|{n}|{k}"; sc.add_geometry(m, node_name=node, geom_name=node)
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        if "iglidur" in nl or "igubal" in nl: mat, rho = "iglidur", USP.IGL
        elif "bearing" in nl or "mr63zz" in nl or "mr85zz" in nl: mat, rho = "bearing steel", 7.8
        elif "17-4ph" in nl: mat, rho = "17-4PH", 7.8
        elif "pin o3" in nl and "drive" in nl: mat, rho = "hardened steel (polished)", 7.85
        elif hwr: mat, rho = "stainless (polished)", 7.9
        else: mat, rho = "Ti-6Al-4V", USP.TI
        pf.append(dict(k=k, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=round(vol / 1000 * rho, 2), valid=bool(s.isValid()), faces=len(s.Faces()),
                       solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(P0, key=a.out, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    # ---- frames: the L1's + the drive groups re-posed by the new RSSR
    posing = dict(clips=USG.pose_groups(dv, os.path.join(FULL, "designs", a.l1, "clips.json"), os.path.join(dd, "clips.json"), "clips"),
                  workspace=USG.pose_groups(dv, os.path.join(FULL, "designs", a.l1, "workspace.json"), os.path.join(dd, "workspace.json"), "workspace"))
    D = json.load(open(os.path.join(src, "design.json"))); D.update(id=a.out, label=D["label"] + " - gen-5 fix (real igubal width, retained drive, lobe fix, link 1a repaired)",
                                                                     built_with="pipeline/conformal/param_cad/user_style_geneva_fix.py on " + a.src + " (drive parts rebuilt, link 1a repaired, every other part copied)")
    D["drive_build"] = dict(D.get("drive_build", {}), rod_centres_mm=round(dv["L"], 3), post_mm=bc_info["post_length_mm"], igubal="igus KGLM-03 at 6 mm", horn_hub_mm=a.hub_h,
                            lobe_fix=dict(a_f=a.a_f, a_c=a.a_c, rr=a.rr, dz=a.dz))
    json.dump(D, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    B = json.load(open(os.path.join(src, "build.json")))
    B.update(lobe=lobe_info, rod=rod_info, horn=horn_info, posing=posing, parts=pf, link_1a_fix=dict(l1a_info, name="renamed: no magnet pocket"))
    B["bell crank"] = bc_info
    B["invalid_or_multi_solid"] = [p["name"] for p in pf if p["material"] != "user part" and (not p["valid"] or p["solids"] != 1)]
    B["drive_kin"] = USG.drive_kin_check(dv, lobe_info)
    json.dump(B, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    B["drive_posed"] = USG.posed_drive_check(dd, dv, n=400)
    spec = importlib_spec(os.path.join(USG.REPO, "docs", "research", "geneva_rod_drive", "declare_slaved.py")); B["slaved"] = [spec.declaration(B)]
    B["gen5_fix"] = dict(src=a.src, rise_rod_end_B_mm=rise, eye_h=a.eye_h, hub_h=a.hub_h, lobe_fix=dict(a_f=a.a_f, a_c=a.a_c, rr=a.rr, dz=a.dz), drive_rep=dv["rep"], seconds=round(time.time() - t0))
    json.dump(B, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done -> {dd}: invalid {B['invalid_or_multi_solid'] or 'none'}; drive_kin max roller dev {B['drive_kin']['max_roller_dev_mm']} closure {B['drive_kin']['max_closure_mm']}; "
          f"posed {B['drive_posed']} ({time.time() - t0:.0f} s)", flush=True)


def importlib_spec(path):
    import importlib.util
    sp = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


if __name__ == "__main__":
    main()
