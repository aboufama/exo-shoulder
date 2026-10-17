"""Full user-style CAD of the generation-8 winner conecut-knee-knuckle-3r (round 12; the VERIFIED LEAD 2026-10-17 ~18:21 UTC by the
user's plain-verified-gap rule: frozen exact Bench(110,360) 18.28 / score 93.35, held out 22.38; ledger WATCH,
docs/alignment/conecut-knee-knuckle-3r.md) -> pipeline/full-exo/designs/user_conecut_knee/.

conecut = the gen-7 lead slipper-nose-knuckle-3r with exactly two changes: (a) the pin knee RE-PROPORTIONED (stk 6.0 MR63ZZ pairs, lE
97.1443, lc 24.3508, phiE 0.7526, phib -91.8041; ang_min 25.2189) and (b) a J3 HARD STOP on J3's own angle q3' = q3 + phi (the link 2 ->
member 3 angle), window [J3MIN -111.9036, J3MAX 122.7417]. So this builder is the gen-7 full-CAD builder with the knee and the J3 stop
changed and nothing else:

  * build_conecut_l1 (gen-8 L1) is imported FIRST: it retargets build_slipper_l1's module globals at the verified CCModel
    (docs/concepts/models/conecut-knee-knuckle-3r.py, SN_CELL=lead) on CC.PARAMS + the row's best_params (= the verifier's config) and
    puts the J3 stop into the chain (BM.chain). user_style_slipper (gen-7 full CAD, imported unchanged) then reads that retargeted module
    as its RL1, so every gen-7 part (v5 O20 hubs, K clock-spring cap, link 1a chain + r 1.25 flank lug, links 1b / 2, lobe ring, straddle
    bell crank + nose, member 3 + E strap, knee link with MR63ZZ-pair bosses + knee stop tooth, arm pad + pad mount fused with the cut
    BOTTOM, cuff, base at the J1 ring) is built from THIS model's fit; the knee comes out re-proportioned by the model's own lE / lc /
    phiE / phib. The judged clips.json / workspace.json are the L1's (l1_conecut-knee), asserted the same fit (params, tr, m, levels).
  * the J3 stop (the L1's / the J3 red team's build spec, docs/research/conecut_mechanism_redteam.md section 6): an ISO 8734 2 m6 x 5
    440C dowel ground to 3.90, pressed through hub 3's lower plate (member 3's J3 disc, a reamed O2.000 -0.005/0 through hole) at r 7.5,
    F+0.10..F+4.00 (skin end recessed 0.10), running 0.85 mm deep in a 2.10 x 1.00 arc groove cut into link 2's J3 pad / ring underside
    (F+3.15..4.15) with FULL R1.05 ends whose centres sit 0.382 deg past the dowel-centre stop angles (the O2 dowel touches the end
    exactly at J3MIN / J3MAX); the dowel's home angle is the L1's (build.json stops.J3, frame_of(u3) of member 3: one frame for both).
  * the gen-7 CAD verifier's open items (pipeline/full-exo/designs/user_slipper_nose/VERIFY.md, docs/research/user_slipper_nose_fix.md):
      D1  ONE running-face entry (+-0.02 profile): the inherited ISO 2768-f line is dropped here (the L1's filter missed it: its text reads
          'crank-to-link 1a / link 1b', the filter looked for 'crank-to-link 1a / 1b');
      D2  the K-phase band '+0.75 +0.15 / -0.10 deg' is stated as an RSS band (the linear low end -0.02 deg) on the drawing;
      D3  the crank's axial position is HELD: a ground stainless inner-ring spacer O3.1 x O4.5 (thickness = the built gap, checked in
          0.15-0.20) under the lower 683ZZ on link 1b's face, and real preload room over the upper 683ZZ: an inner-ring shim O3.1 x O4.5 x
          0.10 + a wave washer O3.2 x O6 (working envelope 0.20, 5-10 N) under the DIN 6799 RS 2.3 clip, the clip groove moved up 0.15 to
          ztop + 0.30 (land 0.50 to the unchanged pin end ztop + 1.40); the posed drive-pair check re-runs with the new parts;
      O3  the checks (--checks-only) write kinematics_exact with the model-metal-outside table (hub 3's groove band excluded like the
          K / J2 slot bands) and the J3 dowel-in-groove reading at every check pose;
      O4  LEAD RULING (2026-10-17): link 2 is machined from solid (3+2-axis), so CLAUDE.md CAD ruling (2) allows its tighter transition:
          its J2 drop follows the model up to 70 deg (USM.CLIMB_MAX 70 while link 2 is profiled; link 1b stays at the 60-deg rule), stated
          on the part ('5-axis / 3+2 machined from solid, drop 68-70 deg').
    plus the knee stop (+-0.02 on the drawing, the tooth at 180 - ang_min = 154.78), the wear-test pass line mu <= 0.105, and the J3
    dowel / groove fits + acceptance bands (the L1's FITS).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_conecut.py [--out user_conecut_knee] [--l1 l1_conecut-knee]
        [--link-margin 0] [--l1b-margin 0.1] [--skip-base-search] [--no-checks | --checks-only]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")
import build_conecut_l1 as CL1                                                             # noqa: E402  (gen-8 L1: retargets build_slipper_l1 at conecut)
import user_style_slipper as USS                                                           # noqa: E402  (gen-7 full CAD builder, imported unchanged)
assert USS.RL1 is CL1.SL, "user_style_slipper must read the build_slipper_l1 module build_conecut_l1 retargeted"
assert USS.RL1.ID == "conecut-knee-knuckle-3r" and USS.RL1.fit is CL1.fit and USS.BM.chain is CL1.chain
import numpy as np, cadquery as cq, trimesh                                                # noqa: E402
USM, USP, US, BM, PB = USS.USM, USS.USP, USS.US, USS.BM, USS.PB
RL1 = USS.RL1; LV = USS.LV; T = USS.T; disc, rev, plane, at, xform = USS.disc, USS.rev, USS.plane, USS.at, USS.xform
FULL = USS.FULL; GROUPS = USS.GROUPS; unit = USS.unit
ID = CL1.ID; J3MIN, J3MAX = CL1.J3MIN, CL1.J3MAX
J3_RS, J3_DR, J3_GW, J3_GD, J3_DTOP, J3_DBOT, J3_END_R = CL1.J3_RS, CL1.J3_DR, CL1.J3_GW, CL1.J3_GD, CL1.J3_DTOP, CL1.J3_DBOT, CL1.J3_END_R
UP = float(LV["U0"])                                                                       # 3.15: the upper member's underside over the joint face
L2_CLIMB = 70.0                                                                            # O4: link 2's drop at J2 up to 70 deg (machined from solid)
SPACER_RI, SPACER_RO = 1.55, 2.25                                                          # D3: inner-ring spacer / shim O3.1 x O4.5
SPACER_T, LAND_R = 0.175, 2.5                                                              # D3: spacer 0.175 (select 0.15-0.20) on an O5 land spot-faced on link 1b
SHIM_T, WAVE_T, WAVE_RO, CLIP_DZ, CLIP_T = 0.10, 0.20, 3.0, 0.30, 0.6                     # D3: shim 0.10 + wave washer 0.20 working = clip at ztop + 0.30

# ---------------------------------------------------------------------------------------------------- O4: link 2's drop up to 70 deg
_profile_link0 = USM.profile_link
CLIMB_USED = {}


def _profile_link(label, *a, **k):
    if not str(label).startswith("link 2"): return _profile_link0(label, *a, **k)
    c0 = USM.CLIMB_MAX; USM.CLIMB_MAX = L2_CLIMB
    try:
        sol, rep = _profile_link0(label, *a, **k); CLIMB_USED.setdefault(label, []).append(rep.get("max_climb")); return sol, rep
    finally: USM.CLIMB_MAX = c0


USM.profile_link = _profile_link                                                           # profile_link_split looks it up in USM at call time


# ---------------------------------------------------------------------------------------------------- link 1a (USS.link1a_body, copied)
SEAT_K_OVERLAP = 0.02                                                                      # this fit's chain ends 0.26 um short of the K pad's seat face (OCC
                                                                                           # fuses them as 2 solids): the K pad runs 0.02 mm into the bar's end


def link1a_body(M, stops, lug):
    """USS.link1a_body (copied) with the K pad's seat SEAT_K_OVERLAP longer (one solid; the bar and its centre line unchanged)"""
    Uu, C, F4, hr = BM.joints4(M); H = lambda j: C[j] + F4[j] * Uu[j]
    ex, ey, start, segs, info = USS.link1a_path(M)
    bar = US.bar_swept(ex, ey, start, segs, t=T, w=USS.W, r=0.3)
    padA = USP.plate_R(Uu[0], F4[0], ey, USS.W, hr[0], L=info["seat_J1_mm"], rf=USS.L1A["rf"])
    sd_b = info["sd_b"][0] * ex + info["sd_b"][1] * ey
    padB = USP.plate_R(Uu[1], F4[1], sd_b, USS.W, hr[1], L=info["seat_K_mm"] + SEAT_K_OVERLAP, rf=USS.L1A["rf"])
    body = US.glue(US.glue(padA, bar), padB)
    body = body.fuse(US.lower_pin(Uu[0], F4[0])).fuse(USS.arbor_pin_roller(Uu[1], F4[1]))
    if lug is not None:
        for s_ in lug: body = body.fuse(s_)
    q_lo, q_hi = stops["K"]["q"]
    for th in stops["K"]["homes"]: body = body.cut(USM.arc_slot_cutter(H(1), Uu[1], th + q_lo, th + q_hi, -1.0, BM.PLATE + 0.1))
    body = body.clean() if body.clean().isValid() else body
    info.update(vs_model=USS.link1a_vs_model(M, ex, ey, start, segs), valid=body.isValid(), solids=len(body.Solids()), seat_K_overlap_mm=SEAT_K_OVERLAP)
    info.pop("sd_b")
    return body, info


USS.link1a_body = link1a_body                                                              # USS.build_links calls it by its module-global name


# ---------------------------------------------------------------------------------------------------- drive layout (USS.drive_layout, copied)
def drive_layout(M, lg, dg, l1b_body):
    """USS.drive_layout (copied) with its red-team frame ASSERT turned into a reported reading: the gen-7 red team's export
    (docs/research/slipper_mechanism/spec_points_bench_r125.json) was made on slipper-nose's fit; conecut's fit (J2 level +0.47 mm)
    tilts the model's crank axis dR by ~0.1 deg against it, so the red team's follower centre sits ~0.14 mm off a_s 6.5 / psi 216 about
    THIS dR. The CAD follows the verified model (dR, the law, the lobe synthesised for it); the flank arcs stay the gen-7 r 1.25
    synthesis, and the posed drive check measures the nose / flank closure on this build (build.json drive_posed)."""
    D = M.D; u2 = unit(D.u[1]); dR = unit(dg["dR"]); f2 = float(M.f[1])
    top = USS.l1b_top_under(l1b_body, dR, USS.BOSS_R + 0.6, dg["zboss"] - 6.0, dg["zboss"] + 12.0)
    zb = max(dg["zboss"], (top if top is not None else -1e9) + 0.15)
    s_f = zb + USS.BOSS_H / 2
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); psi = math.radians(USS.PSI_DEG)
    v = math.cos(psi) * e1 + math.sin(psi) * e2; F0 = s_f * dR + USS.A_S * v
    Frt = np.array(USS.SPEC["follower_centre_onset"], float); s0 = float(Frt @ dR); chk = float(np.linalg.norm((Frt - s0 * dR) - USS.A_S * v))
    dR_dev = math.degrees(math.acos(float(np.clip(dR @ unit(np.array(USS.SPEC["dR_crank_axis"], float)), -1, 1))))
    print(f"drive layout: follower frame vs the gen-7 red team's export {chk:.3f} mm (crank axis dR {dR_dev:.3f} deg off the gen-7 export: conecut's fit)", flush=True)
    return dict(zb=zb, l1b_top=top, raise_mm=zb - dg["zboss"], s_f=s_f, F0=F0, v=v, F0_redteam=Frt, follower_shift_mm=s_f - s0,
                follower_hmid_over_f2=float(F0 @ u2) - f2, dR=dR, u2=u2, f2=f2, follower_check_mm=chk, dR_vs_gen7_export_deg=dR_dev)


# ---------------------------------------------------------------------------------------------------- the fits table (one entry per feature)
def fits(crank_stack=None):
    drop = ("crank-to-link 1a / link 1b running faces", "crank-to-link 1a / 1b running faces", "K phase (assembly", "K-phase band (D2)",
            "knee stop tooth (knee link)", "knee stop tooth vs E strap side", "wear-test pass line", "slipper nose / DLC flank wear test", "crank pivot axial stack (D3)",
            "crank pivot bearings (2 x 683ZZ", "crank running faces (D9-01")
    out = [dict(f) for f in USS.FITS if not f["where"].startswith(drop)]
    cs = crank_stack or {}
    out += [
        dict(where="crank pivot bearings + axial stack (2 x 683ZZ straddling the follower in the O10 x 10 boss; D3)",
             fit=("pin O3 h5 17-4PH H900 (pressed H7/m6 in link 1b), housings O7 J6 at both boss ends with 0.5 mm floors to the follower pocket. AXIAL STACK "
                  f"(the crank's height is HELD): ground stainless inner-ring spacer O3.1 x O4.5 x {cs.get('spacer_t_mm', 0.15):.2f} (select-fit 0.15-0.20, +-0.005 "
                  "ground) between link 1b's spot face and the lower 683ZZ inner ring - it sets the crank boss's running gap to link 1b; preload: inner-ring shim "
                  "O3.1 x O4.5 x 0.10 on the upper 683ZZ + wave washer O3.2 x O6 x 0.08 strip (free 0.40, working 0.20, 5-10 N; supplier part to confirm) "
                  f"under the DIN 6799 RS 2.3 clip, clip groove at the boss top + {CLIP_DZ:.2f} (land 0.50 to the pin end); re-check the posed drive pairs "
                  "(build.json drive_posed) after any change of the spacer")),
        dict(where="crank running faces (D9-01 against links 1a / 1b / 2 and the facing pads; D1)",
             fit=("profile +-0.02 mm on the crank's two boss faces + arm sides and the facing pads of links 1a / 1b / 2 (worst two-face stack 0.04 < the smallest "
                  "posed running gap, build.json drive_posed); NOT ISO 2768-f (+-0.05, stack 0.10, could close the 0.086 mm gap) - the inherited 2768-f "
                  "line is removed (one entry for these faces)")),
        dict(where="K phase (assembly; D2)",
             fit=("build the +0.75 deg K lead: lobe-ring key dowel at the onset phase + 0.35 deg of q2, J2 stop B slot end at q2 -15.47 (the CAD draws the nominal "
                  "-15.82 = the loaded state); keep the verified flank (beta -176.684, no beta step); nose hole / crank pivot / lobe profile +-0.02 mm true "
                  "position, r_c +-0.1 mm. K phase at the onset +0.75 +0.15 / -0.10 deg = an RSS band of the stack (key dowel position, lobe profile, crank "
                  "pivot, flank profile); a worst-case LINEAR stack is +-0.30 deg - read linear, the low end is -0.02 deg (onset +0.73): shim the key dowel "
                  "and accept on the measured onset")),
        dict(where="knee stop tooth (knee link) against the E strap's side face",
             fit=(f"stop at knee angle 180 - ang_min = {180.0 - RL1.CFG['ang_min']:.2f} deg (conecut's taken knee max 105.94 bench / 107.07 held out: 47.7 deg / "
                  "12.8 mm in d below it; the clips run 59.3..91.8): tooth face and the E strap's side face profile +-0.02 mm each (EDM / ground)")),
        dict(where="wear-test pass line (nose on the DLC flank)",
             fit=("PASS only if the measured nose / flank friction mu <= 0.105 over the wear test (the horn's 43-deg pressure-angle rule caps mu at 0.108-0.113); "
                  "verified at mu 0.087; the R17 forward-stroke bound on this CAD at mu 0.087 / 0.105 / 0.12: judge_m5/forward_bound_mu*.json")),
    ]
    return out


# ---------------------------------------------------------------------------------------------------- the J3 stop (dowel in member 3, groove in link 2)
def j3_geom(M, l1_stop):
    u3, H3, e, f, R3 = CL1.j3_frame(M)
    D = M.D; H3_l2 = D.c[2] + M.f[2] * unit(D.u[2])                                       # link 2's own J3 face point (build_links: at(..., c[2]) at level F[2])
    assert np.allclose(u3, unit(D.u[2]), atol=1e-6) and np.linalg.norm(H3 - H3_l2) < 1e-3, f"J3 frame differs from link 2's: {H3 - H3_l2}"
    e2, f2 = USM.frame2(u3); assert np.allclose(e2, e) and np.allclose(f2, f), "frame2 != the L1's j3_frame"
    th = math.radians(float(l1_stop["dowel_home_angle_deg"]))
    pd = H3 + J3_RS * (math.cos(th) * e + math.sin(th) * f)
    return dict(u3=u3, H3=H3, e=e, f=f, R3=R3, th=th, pd=pd)


def j3_groove_cutter(g, z0, z1):
    """the arc groove (link 2): half width w = 1.05 at r 7.5 between the dowel-centre stop angles th + J3MIN .. th + J3MAX, FULL R1.05 ends
    whose centres sit (w - r_dowel) / r = 0.382 deg beyond them (the O2 dowel touches the end exactly at the stop); two concentric arcs +
    two semicircles (threePointArc), extruded z0..z1 along u3 from the J3 face"""
    w = J3_GW / 2; rs = J3_RS; dl = (w - J3_DR) / rs; e, f, u3, H3 = g["e"], g["f"], g["u3"], g["H3"]
    lo, hi = g["th"] + math.radians(J3MIN) - dl, g["th"] + math.radians(J3MAX) + dl
    P = lambda r, a: (r * math.cos(a), r * math.sin(a)); ro, ri = rs + w, rs - w; mid = 0.5 * (lo + hi)
    c_hi, c_lo = np.array(P(rs, hi)), np.array(P(rs, lo)); t_hi = np.array([-math.sin(hi), math.cos(hi)]); t_lo = np.array([-math.sin(lo), math.cos(lo)])
    wp = (cq.Workplane(plane(H3 + z0 * u3, e, f)).moveTo(*P(ro, lo)).threePointArc(P(ro, mid), P(ro, hi))
          .threePointArc(tuple(c_hi + w * t_hi), P(ri, hi)).threePointArc(P(ri, mid), P(ri, lo)).threePointArc(tuple(c_lo - w * t_lo), P(ro, lo)).close())
    return wp.extrude(z1 - z0).val(), dict(end_centre_beyond_stop_deg=round(math.degrees(dl), 3), groove_deg=[round(math.degrees(lo), 3), round(math.degrees(hi), 3)],
                                           groove_arc_deg=round(math.degrees(hi - lo) + 2 * math.degrees(math.asin(w / rs)), 2))


def j3_dowel(g):
    """ISO 8734 2 m6 x 5 ground to 3.90 (chamfered 0.15 x 45 at both ends), F+0.10..F+4.00 at r 7.5 in member 3's home frame"""
    z0, z1, r, ch = J3_DBOT, UP + J3_DTOP, J3_DR, 0.15
    return rev([(0, z0), (r - ch, z0), (r, z0 + ch), (r, z1 - ch), (r - ch, z1), (0, z1)], g["pd"], g["u3"])


def j3_apply(M, parts, l1_stop):
    """cut the groove into link 2 (D8-03) and the dowel hole into member 3 (D8-04), add the dowel (member 3). Returns parts, report"""
    g = j3_geom(M, l1_stop); rep = dict(home_angle_deg=float(l1_stop["dowel_home_angle_deg"]), window_deg=[J3MIN, J3MAX], r_mm=J3_RS)
    cut, gi = j3_groove_cutter(g, UP - 0.5, UP + J3_GD); rep.update(gi, groove_z_mm=[UP, UP + J3_GD], groove_w_mm=J3_GW, end_R_mm=J3_GW / 2)
    i2 = next(i for i, p in enumerate(parts) if p[1].startswith("D8-03"))
    b2 = parts[i2][2].cut(cut); b2 = b2.clean() if b2.clean().isValid() else b2
    b2, sl2 = USM.sliver_free(b2, "link 2 (J3 groove)")
    rep["link2_after_groove"] = dict(valid=b2.isValid(), solids=len(b2.Solids()), slivers=sl2, removed_mm3=round(parts[i2][2].Volume() - b2.Volume(), 2))
    parts[i2] = (parts[i2][0], parts[i2][1].replace("J2 dowel hole,", f"J2 dowel hole, the J3 stop's {J3_GW:.2f} x {J3_GD:.2f} arc groove (r {J3_RS:g}, "
                                                    f"{gi['groove_arc_deg']:.1f} deg, R{J3_GW / 2:.2f} ends) under the J3 pad / ring,"), b2)
    i3 = next(i for i, p in enumerate(parts) if p[1].startswith("D8-04"))
    hole = disc(g["pd"], g["u3"], J3_DR, -0.5, BM.PLATE + 0.5)
    b3 = parts[i3][2].cut(hole); b3 = b3.clean() if b3.clean().isValid() else b3
    rep["member3_after_hole"] = dict(valid=b3.isValid(), solids=len(b3.Solids()), removed_mm3=round(parts[i3][2].Volume() - b3.Volume(), 3))
    parts[i3] = (parts[i3][0], parts[i3][1].replace("J3 disc + integral O7 pin,", f"J3 disc + integral O7 pin + the J3 stop dowel's reamed O2.000 -0.005/0 through hole "
                                                    f"(r {J3_RS:g}),"), b3)
    dw = j3_dowel(g)
    parts.append(("l3", (f"J3 stop dowel ISO 8734 2 m6 x 5, 440C grade >= 56 HRC, ground to {UP + J3_DTOP - J3_DBOT:.2f}: pressed through hub 3's lower plate (member 3) "
                         f"at r {J3_RS:g}, F+{J3_DBOT:.2f}..F+{UP + J3_DTOP:.2f} (skin end recessed {J3_DBOT:.2f}), {J3_DTOP:g} mm into link 2's groove (tip "
                         f"{J3_GD - J3_DTOP:.2f} off its floor); stops J3's own angle q3' at {J3MIN:.2f} / {J3MAX:.2f} deg (polished)"), dw))
    # where the stop sits against the two members' own metal: the web (uncut ring) centre vs link 2's bar root, the dowel vs member 3's E strap
    u3, e, f = g["u3"], g["e"], g["f"]; ang = lambda v: math.degrees(math.atan2(float(v @ f), float(v @ e)))
    eE = M.fr["eE"]; eE = eE - (eE @ u3) * u3
    D = M.D; u, c = D.u, D.c; Fm = M.f; ex = unit(u[1]); Cj2 = c[2] + Fm[2] * u[2]; ey = unit(Cj2 - (Cj2 @ ex) * ex); nP = np.cross(ex, ey)
    u3p = unit(u[2] - (u[2] @ nP) * nP); phi = math.atan2(u3p @ ey, u3p @ ex); back_w = math.sin(phi) * ex - math.cos(phi) * ey
    root = back_w - (back_w @ u3) * u3                                                     # the J3 pad runs out along its seat direction into link 2's bar
    web_c = (math.degrees(g["th"]) + 0.5 * (J3MIN + J3MAX) + 180.0)
    rep["placement"] = dict(dowel_vs_E_strap_deg=round(((math.degrees(g["th"]) - ang(eE)) + 180) % 360 - 180, 2),
                            web_centre_deg=round(web_c % 360, 2), link2_bar_root_deg=round(ang(root) % 360, 2), web_vs_bar_root_deg=round(((web_c - ang(root)) + 180) % 360 - 180, 2),
                            note="frame_of(u3) angles; the web (108.6 deg of uncut ring) sits under link 2's ring wherever it lands - the groove is inside the O20 ring "
                                 "(r 6.45..8.55, walls 0.95 to the bearing seat / 1.45 to the rim), never in the bar")
    print(f"J3 stop: groove {gi}, link 2 {rep['link2_after_groove']}, member 3 {rep['member3_after_hole']}, placement {rep['placement']}", flush=True)
    return parts, rep, g


# ---------------------------------------------------------------------------------------------------- D3: the crank's axial stack
def crank_stack(cp, cinfo, lay, l1b_body):
    """D3: link 1b's top is inclined under the crank (0.82 mm below the boss underside at the pin, 0.15 at the footprint's high side), so
    link 1b gets an O5 LAND around the pivot pin, spot-faced perpendicular to dR at zb - SPACER_T (machined with link 1b), and the ground
    spacer O3.1 x O4.5 x SPACER_T sits on it under the lower 683ZZ inner ring; over the upper 683ZZ the inner-ring shim + wave washer, the
    clip moved to ztop + 0.30 (the pin end unchanged). Returns parts, report, link 1b with the land"""
    dR = lay["dR"]; zb = float(lay["zb"]); ztop = zb + USS.BOSS_H
    top_sp = USS.l1b_top_under(l1b_body, dR, SPACER_RO + 0.05, zb - 6.0, zb + 1.0)
    top_boss = USS.l1b_top_under(l1b_body, dR, USS.BOSS_R + 0.6, zb - 6.0, zb + 1.0)
    if top_boss is None: top_boss = zb - 0.15
    if top_sp is None: top_sp = top_boss                                                   # nothing of link 1b under the O4.5 footprint in range: sit on the boss reading
    z_land = zb - SPACER_T; t_sp = SPACER_T
    land = disc(np.zeros(3), dR, LAND_R, top_sp - 1.0, z_land)
    l1b_new = l1b_body.fuse(land); l1b_new = l1b_new.clean() if l1b_new.clean().isValid() else l1b_new
    ok = l1b_new.isValid() and len(l1b_new.Solids()) == 1
    if not ok: l1b_new = l1b_body
    rep = dict(boss_underside_mm=round(zb, 4), l1b_top_under_spacer_mm_before_land=round(top_sp, 4), l1b_top_under_boss_mm=round(top_boss, 4),
               land=dict(r_mm=LAND_R, top_mm=round(z_land, 4), rise_over_l1b_mm=round(z_land - top_sp, 4), fused=ok, valid=l1b_new.isValid(), solids=len(l1b_new.Solids())),
               spacer_t_mm=round(t_sp, 4), spacer_in_0p15_0p20=bool(0.15 - 1e-3 <= t_sp <= 0.20 + 1e-3), boss_gap_to_l1b_mm=round(zb - top_boss, 4))
    spacer = rev([(SPACER_RI, z_land), (SPACER_RO, z_land), (SPACER_RO, zb), (SPACER_RI, zb)], np.zeros(3), dR)
    shim = rev([(SPACER_RI, ztop), (SPACER_RO, ztop), (SPACER_RO, ztop + SHIM_T), (SPACER_RI, ztop + SHIM_T)], np.zeros(3), dR)
    wave = rev([(1.6, ztop + SHIM_T), (WAVE_RO, ztop + SHIM_T), (WAVE_RO, ztop + SHIM_T + WAVE_T), (1.6, ztop + SHIM_T + WAVE_T)], np.zeros(3), dR)
    z_c = ztop + CLIP_DZ
    clip = rev([(1.15, z_c), (3.0, z_c), (3.0, z_c + CLIP_T), (1.15, z_c + CLIP_T)], np.zeros(3), dR)
    out = []
    for g_, n_, s_ in cp:
        if n_.startswith("drive crank pivot pin clip"):
            out.append((g_, f"drive crank pivot pin clip DIN 6799 RS 2.3 at the boss top + {CLIP_DZ:.2f} (groove O2.3 x 0.6 H13, land {ztop + 1.4 - z_c - CLIP_T:.2f} to the "
                            "pin end) over the preload stack (polished)", clip))
            continue
        if n_.startswith("drive crank pivot pin O3"):
            n_ = n_.replace("pressed in link 1b", f"pressed in link 1b, clip groove at the boss top + {CLIP_DZ:.2f}")
        if n_.startswith("drive crank bearing 2"):
            n_ = n_.replace("wave-washer preloaded 5-10 N", "preloaded 5-10 N by the wave washer through the inner-ring shim")
        out.append((g_, n_, s_))
    out += [("l1b", f"drive crank inner-ring spacer O3.1 x O4.5 x {t_sp:.3f} ground stainless 1.4310 (select-fit 0.15-0.20): on link 1b's O5 spot-faced land under the "
                    "lower 683ZZ inner ring - holds the crank's axial position (D3) (polished)", spacer),
            ("l1b", f"drive crank preload inner-ring shim O3.1 x O4.5 x {SHIM_T:.2f} stainless (polished)", shim),
            ("l1b", f"drive crank preload wave washer O3.2 x O6 (stainless spring shim: 0.08 strip, free 0.40, drawn at its {WAVE_T:.2f} working height: 5-10 N) (polished)", wave)]
    rep.update(shim_mm=[round(ztop, 3), round(ztop + SHIM_T, 3)], wave_mm=[round(ztop + SHIM_T, 3), round(ztop + SHIM_T + WAVE_T, 3)],
               clip_mm=[round(z_c, 3), round(z_c + CLIP_T, 3)], pin_end_mm=round(ztop + 1.4, 3), land_mm=round(ztop + 1.4 - z_c - CLIP_T, 3))
    print(f"crank stack (D3): {rep}", flush=True)
    return out, rep, l1b_new


# ---------------------------------------------------------------------------------------------------- checks
def posed_drive_check(dd, n=60, frames=None):
    """USS.posed_drive_check's pairs + the D3 stack parts and the J3 stop dowel (copied: same sampling, same frames)"""
    import igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); C = json.load(open(os.path.join(dd, "clips.json"))) if frames is None else dict(clips=[dict(name="given", frames=frames)])
    by = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g, nm = node.split("|")[:2]; m = src.geometry[gn].copy(); m.apply_transform(T_); by[nm] = (g, m)
    def get(sub): return next(v for k, v in by.items() if k.startswith(sub))
    pairs = [("drive lobe follower roller", "D9-02"), ("drive nose dowel", "D8-02a"), ("D9-01", "D8-02a"),
             ("D9-01", "D9-02"), ("D9-01", "D8-02b"), ("D9-01", "D8-03"), ("D9-01", "J2 cap"), ("D9-01", "K clock-spring cap"), ("drive lobe follower roller", "J2 cap"),
             ("drive lobe follower roller", "D8-03"), ("drive follower pin", "D9-02"), ("drive follower inner-ring shim", "D9-02"), ("drive nose dowel", "K clock-spring cap"),
             ("drive nose dowel", "D8-02b"), ("D8-02a", "D8-02b"), ("D8-02a", "K clock-spring cap"), ("D8-02a", "D8-01"), ("drive crank pivot pin clip", "D9-01"),
             ("D9-02", "D8-02b"), ("drive crank bearing 1", "D8-02b"),
             ("drive crank inner-ring spacer", "D9-01"), ("drive crank preload wave washer", "D9-01"), ("drive crank preload inner-ring shim", "D9-01"),
             ("drive crank pivot pin clip", "D8-03"), ("drive crank preload wave washer", "D8-03"), ("drive crank pivot pin clip", "J2 cap"),
             ("J3 stop dowel", "D8-03")]
    frs = [f for c in C["clips"] for f in c["frames"]]
    pick = (frs[::max(1, len(frs) // n)] + sorted(frs, key=lambda f: -abs(f.get("knuckle", {}).get("dK", 0.0)))[:12]) if frames is None else frs
    res = {}
    for a_, b_ in pairs:
        try: (ga, ma), (gb, mb) = get(a_), get(b_)
        except StopIteration: res[f"{a_} | {b_}"] = "missing"; continue
        XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 3000, seed=4)[0]]; worst = (1e9, None)
        for f in pick:
            G = lambda g: np.array(f["G"][g]).reshape(3, 3) if g in f["G"] else np.eye(3); T_ = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xb = ((XA @ G(ga).T + T_(ga)) - T_(gb)) @ G(gb)
            d = float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min())
            if d < worst[0]: worst = (round(d, 3), round(float(f.get("knuckle", {}).get("dK", 0.0)), 2))
        res[f"{a_} | {b_}"] = worst
    drv = sorted([f for f in frs if abs(f.get("knuckle", {}).get("dK", 0.0)) > 0.5], key=lambda f: abs(f["knuckle"]["dK"]))
    drv = drv[::max(1, len(drv) // 40)]
    for a_, b_ in (("drive lobe follower roller", "D9-02"), ("drive nose dowel", "D8-02a")):
        (ga, ma), (gb, mb) = get(a_), get(b_); XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 4000, seed=5)[0]]; ds = []
        for f in drv:
            G = lambda g: np.array(f["G"][g]).reshape(3, 3); T_ = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xb = ((XA @ G(ga).T + T_(ga)) - T_(gb)) @ G(gb)
            ds.append(float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min()))
        res[f"contact {a_} | {b_} (driven frames: min, max of the per-frame min)"] = [len(ds), round(min(ds), 3) if ds else None, round(max(ds), 3) if ds else None]
    return res


def j3_sweep_built(dd, M, g, dq=1.0):
    """the BUILT stop: the exported dowel (member 3) turned about J3 by q3' in link 2's home frame vs the exported link 2 (groove) and every
    other link-2-riding part (J3 hub hardware / cap): signed distance (mm, < 0 = metal in metal) over the window and 2 deg past each end"""
    import igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); dw = None; tg = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; gp, nm = node.split("|")[:2]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        if nm.startswith("J3 stop dowel"): dw = m
        elif gp == "l2" and (nm.startswith("D8-03") or nm.startswith("J3")): tg[nm[:40]] = m
    X = np.r_[np.asarray(dw.vertices), trimesh.sample.sample_surface_even(dw, 4000, seed=23)[0]]; u3, H3 = g["u3"], g["H3"]
    qs = sorted(set(np.r_[np.arange(J3MIN - 2.0, J3MAX + 2.0 + 1e-9, dq), J3MIN, J3MAX, J3MIN - 0.25, J3MAX + 0.25, J3MIN + 0.25, J3MAX - 0.25].round(4).tolist()))
    out = {}
    for q in qs:
        R = CL1.S.rotm(u3, math.radians(q))[0]; Xq = (X - H3) @ R.T + H3
        out[q] = {nm: float(igl.signed_distance(np.ascontiguousarray(Xq, float), np.ascontiguousarray(m.vertices, float), np.ascontiguousarray(m.faces, np.int64))[0].min())
                  for nm, m in tg.items()}
    mn = lambda q: min(out[round(q, 4)].values())
    inside = [q for q in qs if J3MIN + 1e-6 < q < J3MAX - 1e-6]; w_in = min(mn(q) for q in inside)
    l2 = next(k for k in tg if k.startswith("D8-03"))
    res = dict(rule="exported dowel (member 3) vs exported link 2 + J3 hub parts riding link 2, turned by q3' about J3 (signed mm, < 0 = metal in metal)",
               inside_window_min_mm=round(w_in, 4), at_J3MIN_mm=round(out[round(J3MIN, 4)][l2], 4), at_J3MAX_mm=round(out[round(J3MAX, 4)][l2], 4),
               past_0p25_mm=[round(mn(J3MIN - 0.25), 4), round(mn(J3MAX + 0.25), 4)], inside_0p25_mm=[round(mn(J3MIN + 0.25), 4), round(mn(J3MAX - 0.25), 4)],
               past_2deg_mm=[round(mn(qs[0]), 4), round(mn(qs[-1]), 4)], others_min_mm={k: round(min(out[q][k] for q in qs), 4) for k in tg if k != l2})
    res["verdict"] = "stop" if (res["past_0p25_mm"][0] < -0.01 and res["past_0p25_mm"][1] < -0.01 and w_in > -0.005) else "CHECK"
    return res


def check_frames(M, dd, stops, g3):
    """USS.check_frames (copied) + the L1's check poses for the J3 stop and the knee (q3' extremes, knee-angle extremes); hub 3's groove band
    excluded from the joint-feature reading like the K / J2 slot bands (the model samples solid plate where the groove is cut), and the J3
    dowel read in link 2's posed frame against the groove ends"""
    import scene_export as SE, igl
    from scipy.spatial.transform import Rotation as Rot
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    allp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    K = BM.chain(M, allp)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    kin = [i for i in range(len(B.idx)) if K["ok"][i] and K["kok"][i] and K["res"][i] < 0.5]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": next(j for j in sorted(taken, key=el)[::-1] if j != max(taken, key=el))}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    tgt = np.array([30.0, 150.0, -60.0]); pick["overhead raise peak"] = min(kin, key=lambda i: float(np.linalg.norm(allp[i, :3] - tgt)))
    st1 = [i for i in taken if K["state"][i] == 1]
    if st1: pick["K most open, taken (drive extreme)"] = max(st1, key=lambda i: abs(K["dK"][i]))
    pick["J3 q3' min, taken"] = min(taken, key=lambda i: K["q3p"][i]); pick["J3 q3' max, taken"] = max(taken, key=lambda i: K["q3p"][i])
    pick["knee angle min, taken"] = min(taken, key=lambda i: K["Kn"]["ang"][i]); pick["knee angle max, taken"] = max(taken, key=lambda i: K["Kn"]["ang"][i])
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    grp_of = {0: "base", 1: "l1a", 7: "l1b", 2: "l2", 3: "l3", 6: "l4", 5: "H", 9: "dk"}; out = []
    Uu, C, F4, hr = BM.joints4(M); D = M.D
    for lab, i in pick.items():
        pz = allp[i]; fr = BM.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; fdev = 0.0
        old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BM.BASE.swap_in(M, K); res = {}
        try:
            for node in src.graph.nodes_geometry:
                g, n = node.split("|")[:2]
                if g == "F" or g not in GROUPS: continue
                if g == "H" and not n.startswith("D8-06"): continue
                T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
                Vl = np.asarray(m.vertices); mem = GROUPS[g]; Vc = Vl @ np.asarray(R).T + t
                Vm = M.world(mem, i, Vl if mem != 5 else Vl @ BM.HR); fdev = max(fdev, float(np.abs(Vm - Vc).max()))
                m.vertices = Vc
                if not any(s_ in n.lower() for s_ in ("screw", "clip din", "e-clip")): meshes.setdefault(g, []).append(m)
            meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
            for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
                Pw = M.world(m, i, Xp); g = "l1a" if name == "hub1" else grp_of[m]
                d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                            np.ascontiguousarray(meshes[g].faces, np.int64))[0])
                win = igl.fast_winding_number(np.ascontiguousarray(meshes[g].vertices, float), np.ascontiguousarray(meshes[g].faces, np.int64), np.ascontiguousarray(Pw, float))
                dout = np.where(win > 0.5, 0.0, d)
                if name == "hub2":
                    dl = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes["l1b"].vertices, float),
                                                                 np.ascontiguousarray(meshes["l1b"].faces, np.int64))[0]); d = np.minimum(d, dl)
                if name in ("hubK", "hub2", "hub3"):
                    k = {"hubK": 1, "hub2": 2, "hub3": 3}[name]; cen = C[k] + F4[k] * Uu[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ Uu[k])[:, None] * Uu[k], axis=1)
                    rs_, hw_ = (USM.SLOT_RS, USM.SLOT_W) if k < 3 else (J3_RS, J3_GW / 2)
                    inslot = (rr > rs_ - hw_ - 0.6) & (rr < rs_ + hw_ + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]; d = d[~inslot]; dout = dout[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4), round(float(dout.max()), 4)]
                if name in ("L1a", "L1b", "L2"):
                    lk = next(x for x in M.geo.links if x["name"] == name); zone = np.zeros(len(Xp), bool)
                    for kk in (lk["ka"], lk["kb"]):
                        w = Xp - C[kk]; zone |= np.linalg.norm(w - (w @ Uu[kk])[:, None] * Uu[kk], axis=1) < hr[kk] + 2.5 + 0.5
                    do = d[~zone]
                    res[name + " outside hub zones"] = [round(float(do.max()), 4) if len(do) else None, int((~zone).sum()),
                                                        round(float(np.mean(do <= 0.5)), 4) if len(do) else None, round(float(np.median(do)), 4) if len(do) else None]
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                q_lo, q_hi = [math.degrees(x) for x in stops[key]["q"]]
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(ang - q_lo, 3), to_stop_hi_deg=round(q_hi - ang, 3), inside=bool(q_lo - 0.01 <= ang <= q_hi + 0.01))
            # J3: q3' from the posed frames (R2^T R3 about u3) vs the model's q3 + phi, and the dowel centre read in link 2's posed frame
            q3f = float(np.degrees(Rot.from_matrix(R2.T @ R3).as_rotvec() @ g3["u3"]))
            pw = R3 @ g3["pd"] + t3; p2 = R2.T @ (pw - t2) - g3["H3"]
            a2 = math.degrees(math.atan2(float(p2 @ g3["f"]), float(p2 @ g3["e"]))); rel = ((a2 - math.degrees(g3["th"])) + 180.0) % 360.0 - 180.0
            inside["J3"] = dict(angle_deg=round(q3f, 3), model_q3p_deg=round(float(K["q3p"][i]), 3), frame_vs_model_deg=round(abs(CL1.wr(q3f - float(K["q3p"][i]))), 4),
                                dowel_angle_in_link2_deg=round(rel, 3), from_stop_lo_deg=round(rel - J3MIN, 3), to_stop_hi_deg=round(J3MAX - rel, 3),
                                inside=bool(J3MIN - 0.01 <= rel <= J3MAX + 0.01), dowel_r_in_link2_mm=round(float(np.linalg.norm(p2 - (p2 @ g3["u3"]) * g3["u3"])), 4))
        finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
        joint_keys = [k for k in ("hub1", "hubK", "hub2", "hub3", "boss", "pad") if k in res]
        joint = max(res[k][0] for k in joint_keys)
        worst_o = max((res[k][0] or 0) for k in ("L1a outside hub zones", "L1b outside hub zones", "L2 outside hub zones") if k in res)
        drv = {k: res[k] for k in ("crank", "roller", "horn") if k in res}
        others = {k: v for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and k not in drv and v[0] is not None}
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        joint_features_max_mm=round(joint, 4), rigid_non_drive_max_mm=round(max(v[0] for v in others.values()), 4),
                        strap_samples_outside_hub_zones_max_mm=round(worst_o, 4), drive_samples_mm=drv,
                        within_0p5=bool(joint <= 0.5 and fdev <= 0.5), per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4),
                        knee_angle=round(float(K["Kn"]["ang"][i]), 1), q3p_deg=round(float(K["q3p"][i]), 3), stops=inside))
        print(f"  check {lab:34s} pose {i} {np.round(pz[:3], 1)} st {int(K['state'][i]):+d}: joints vs posed glb {joint:.3f} mm, other rigid {out[-1]['rigid_non_drive_max_mm']:.3f}, "
              f"drive {drv}, straps outside zones {worst_o:.2f}; frames {fdev:.1e}; dK {inside['K']['angle_deg']:.2f} q2 {inside['J2']['angle_deg']:.2f} "
              f"q3' {inside['J3']['angle_deg']:.2f} (model {inside['J3']['model_q3p_deg']:.2f}); in slot {inside['K']['inside']}/{inside['J2']['inside']}/{inside['J3']['inside']}", flush=True)
    return out


def run_checks(M, dd, stops, rep, t0, g3):
    """the post-export checks: posed drive pairs (+ the D3 stack and the J3 dowel), the built J3 stop sweep, the model's metal vs the posed
    parts at the check poses (kinematics_exact + the outside table), drive skin, working end"""
    rep.pop("checks", None); W = lambda: json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep["drive_posed"] = posed_drive_check(dd); print(f"drive posed (mm, at dK): {rep['drive_posed']}", flush=True); W()
    rep["j3_stop_built"] = j3_sweep_built(dd, M, g3); print(f"J3 stop (built): {rep['j3_stop_built']}", flush=True); W()
    rep["check"] = check_frames(M, dd, stops, g3)
    keys = sorted({k for r in rep["check"] for k in r["per_part"] if " " not in k})
    outside = {k: max(float(r["per_part"][k][2]) for r in rep["check"] if k in r["per_part"]) for k in keys}
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), joint_features_and_frames_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   model_metal_outside_built_max_mm={k: round(v, 3) for k, v in outside.items()},
                                   model_metal_within_0p5_except_crank=all(v <= 0.5 for k, v in outside.items() if k != "crank"),
                                   crank_note="the model's crank samples (arm root inside link 1b's strap) are a model artefact (gen-6 L1 7.12); the built crank is the red team's",
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]), max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                   dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] and r["stops"]["J3"]["inside"] for r in rep["check"]),
                                   q3p_frames_vs_model_max_deg=max(r["stops"]["J3"]["frame_vs_model_deg"] for r in rep["check"]))
    W(); print(f"kinematics: {rep['kinematics_exact']} ({time.time() - t0:.0f} s)", flush=True)
    rep["drive_skin"] = USS.drive_skin(dd); W()
    print(f"drive skin: { {k: v for k, v in rep['drive_skin'].items() if k != 'per_clip'} }", flush=True)
    W_ = json.load(open(os.path.join(dd, "workspace.json")))
    frs = [p for p in W_["poses"] if p.get("eval_feasible") and abs(p.get("knuckle", {}).get("dK", 0.0)) >= 29.3]
    dks = [abs(p["knuckle"]["dK"]) for p in frs]
    rep["working_end"] = dict(poses=len(frs), dK_range=[round(min(dks), 2), round(max(dks), 2)] if dks else None)
    if frs: rep["working_end"].update(pairs=posed_drive_check(dd, frames=frs), skin=USS.drive_skin(dd, frames=frs))
    W(); print(f"working end: {json.dumps(rep['working_end'], default=float)[:1500]}", flush=True)
    print(f"checks done in {time.time() - t0:.0f} s", flush=True)


# ---------------------------------------------------------------------------------------------------- main (USS.main, copied, + the knee / J3 / D3 changes)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_conecut_knee"); ap.add_argument("--l1", default="l1_conecut-knee")
    ap.add_argument("--skip-base-search", action="store_true"); ap.add_argument("--checks-only", action="store_true")
    ap.add_argument("--link-margin", type=float, default=0.0, help="links 1b / 2 underside clearance (gen-7 fix: 0)")
    ap.add_argument("--l1b-margin", type=float, default=0.1, help="link 1b's own margin (gen-7 fix: 0.1)")
    ap.add_argument("--no-checks", action="store_true")
    a = ap.parse_args(MY_ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    import concept_kit as KIT
    M, rep0 = RL1.fit(); D = M.D; lg = RL1.law_geom(M); M._lg = lg; dg = RL1.drive_geom(M)
    Bf = M.B; M._bench_K = BM.chain(M, np.array([[Bf.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(Bf.idx))]))
    L1D = os.path.join(FULL, "designs", a.l1)
    l1d = json.load(open(os.path.join(L1D, "design.json"))); l1b = json.load(open(os.path.join(L1D, "build.json")))
    same = all(abs(float(l1d["params"][k]) - float(v)) < 1e-6 for k, v in RL1.CFG.items() if isinstance(v, (int, float)))
    assert same, f"the L1 design {a.l1} was built from other params"
    assert abs(float(l1b["fit"]["tr"]) - float(M.tr)) < 1e-2 and np.allclose(l1b["fit"]["m"], D.m, atol=1e-2), "the fit differs from the L1's"
    assert np.allclose(l1b["stack"]["f"], M.f, atol=1e-2) and abs(l1b["stack"]["fK"] - M.fK) < 1e-2
    Uu, C, F4, hr = BM.joints4(M)
    print(f"fit (claim CCModel SN_CELL=lead, BEST + ang_min {RL1.CFG['ang_min']}) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']}; "
          f"hub levels {np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f}; knee lE {RL1.CFG['lE']} lc {RL1.CFG['lc']} ({time.time() - t0:.0f} s)", flush=True)
    l1_stops = l1d["stack_mm"]["stops"]; stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1_stops[key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1_stops[key].get("pair")))
    l1_j3 = l1b["stack"]["stops"]["J3"]
    if a.checks_only:
        rep = json.load(open(os.path.join(dd, "build.json"))); g3 = j3_geom(M, l1_j3); run_checks(M, dd, stops, rep, t0, g3); return
    rep = dict(fit=dict(params=dict(RL1.CFG), source=f"docs/concepts/rows/{ID}.json best_params on the claim CCModel's PARAMS (SN_CELL=lead; = {a.l1} = the verifier's config)",
                        gap_near_touch=rep0["gap"], hub_levels_J1_K_J2_J3=[float(x) for x in F4], tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr],
                        fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"]) for k, v in stops.items()},
               j2_push_limit=USM.j2_push_limit(), law=lg["law"])
    parts = []
    hw, rep["hubs"] = USS.hubs(M); parts += hw
    USS.LINK_MARGIN.update(l1b=a.l1b_margin, l2=a.link_margin)
    lug, rep["flank lug"] = USS.flank_lug(M, dg, None)
    lk, rep["links"] = USS.build_links(M, stops, lug)
    rep["links"]["link 2"]["climb_max_deg_allowed"] = L2_CLIMB; rep["links"]["link 2"]["climb_used_deg"] = CLIMB_USED
    l1b_body = next(s for g, n, s in lk if n.startswith("D8-02b"))
    lay = drive_layout(M, lg, dg, l1b_body)
    ring, rep["lobe"], lobe_g = USS.lobe_ring(M, lg, dg, lay)
    cp, rep["crank"] = USS.crank_parts(M, dg, lay, l1b_body)
    z_pp = rep["crank"]["pivot_pin_mm"]; i_1b = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-02b"))
    cp, rep["crank_stack"], l1b_land = crank_stack(cp, rep["crank"], lay, l1b_body)
    lk[i_1b] = (lk[i_1b][0], lk[i_1b][1].replace("carries the crank pivot pin", f"carries the crank pivot pin on an O{2 * LAND_R:g} land spot-faced at the boss underside "
                                                 f"- {SPACER_T:g} (D3)"), l1b_land)
    try:
        b_ = lk[i_1b][2].cut(disc(np.zeros(3), lay["dR"], USS.PIN_R, z_pp[0] - 1.0, z_pp[0] + T + 1.0))
        bad_, zero_, ns_ = USM.step_bad_faces(b_); ok_ = b_.isValid() and len(b_.Solids()) == 1 and bad_ == 0 and ns_ == 1
    except Exception as e_: ok_, bad_, zero_ = False, str(e_), None
    if ok_:
        lk[i_1b] = (lk[i_1b][0], lk[i_1b][1].replace("carries the crank pivot pin", "carries the crank pivot pin in an O3 H7 bore"), b_)
        rep["crank"]["pivot_pin"] = f"O3 h6 pressed in an O3 H7 bore through link 1b (bore cut; STEP round trip 0 bad faces, {zero_} zero-area)"
    else:
        rep["crank"]["pivot_pin"] = (f"O3 h6 pressed in link 1b: drawn as the press fit (pin overlapping its bore); the bore cut fails R7's STEP round trip ({bad_} bad faces)")
    print(f"crank pivot pin: {rep['crank']['pivot_pin']}", flush=True)
    # O4: state link 2's tighter transition on the part
    i_2 = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-03"))
    clu = [c_ for v in CLIMB_USED.values() for c_ in v if c_ is not None]
    lk[i_2] = (lk[i_2][0], lk[i_2][1].replace("D8-03 link 2:", f"D8-03 link 2 (5-axis / 3+2 machined from solid Ti-6Al-4V, drop {max(clu) if clu else 0:.1f} deg at J2 "
                                                           f"(<= {L2_CLIMB:g}: CAD ruling 2, tighter transition on a part machined from solid)):"), lk[i_2][2])
    parts += lk
    parts.append(("l2", f"D9-02 drive lobe ring: 17-4PH H900, wire-EDM (taper {rep['lobe']['e_ext_to_u2_deg']:.1f} deg along the follower axis), profile r "
                        f"{rep['lobe']['profile_r_mm'][0]:.2f} -> {rep['lobe']['profile_r_mm'][1]:.2f} mm ({rep['lobe']['arcs']} 3-point arcs), dwell r {rep['lobe']['dwell_r_mm']:.2f}, "
                        f"bore O20 on the J2 cap skirt, band F+{rep['lobe']['band_over_f2_mm'][0]:.2f}..F+{rep['lobe']['band_over_f2_mm'][1]:.2f}, keyed by an O1 dowel at the "
                        "onset phase + 0.35 deg of q2 (the +0.75 deg K lead, +0.15 / -0.10 deg K RSS; the CAD draws the nominal phase = the loaded state)", ring))
    parts += cp
    USP.pin_stack = USS.knee_pin_bb                                                            # the knee pins: MR63ZZ pairs (member3 / arm_side call pin_stack)
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = USS.knee_link_bb(M)
    ks_deg = (l1d.get("build_fixes") or {}).get("knee_stop_deg")
    if ks_deg is not None:
        s_, rep["knee stop"] = USM.knee_stop_on(M, s_, ks_deg, M._bench_K)
        n_ = n_.replace(" (Ti-6Al-4V)", f" + knee stop tooth behind pin a (its face meets the E strap's side at knee angle {ks_deg:g} deg = 180 - ang_min {RL1.CFG['ang_min']}; "
                                        "+-0.02 on the tooth and the E strap's side face) (Ti-6Al-4V)")
    parts.append((g_, n_, s_))
    parts, rep["j3_stop"], g3 = j3_apply(M, parts, l1_j3)
    rep["j3_stop"]["l1"] = {k: l1_j3.get(k) for k in ("dowel_home_angle_deg", "groove_deg", "groove_arc_deg", "web_deg", "clearance_to_link2_strap_deg", "tolerance", "dowel_calc")}
    Cc = json.load(open(os.path.join(L1D, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = USP.arm_side(M, l1b["mount"], cposes); parts += [(g, n, s) for g, _, n, s in arm]
    Wj = json.load(open(os.path.join(L1D, "workspace.json"))); frames = []; rel = []
    allf = [f for cl in Cc["clips"] for f in cl["frames"]] + [p for p in Wj["poses"] if p.get("eval_feasible")]
    for fi, f in enumerate(allf):
        gg = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        Gb, Tb, G1, T1 = gg("base"), t_("base"), gg("l1a"), t_("l1a"); rel.append((Gb.T @ G1, Gb.T @ (T1 - Tb)))
        if fi % 3 == 0: frames.append((Gb, Tb, G1, T1))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    l1_body = next(s for g, n, s in parts if n.startswith("D8-02a"))
    if a.skip_base_search: USP.EAR_DZ = ()
    try: bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames)
    except (FileNotFoundError, OSError) as e_:
        print(f"base: ear search needs {e_} - built without ears (the J1 upper member alone)", flush=True)
        USP.EAR_DZ = (); bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames); rep["base"]["ear_search"] = f"not run: {e_}"
    parts.append((bp[0], bp[2], bp[3]))
    print(f"parts built ({time.time() - t0:.0f} s)", flush=True)
    NAMEFIX = {"+ integral O4 pin a": "+ the O3 H7 seat of pin a (ISO 8734 m6 pressed; MR63ZZ-pair knee)",
               "+ integral O4 h9 pin, hard-anodised": "+ the O3 H7 seat of pin b (ISO 8734 m6 pressed; MR63ZZ-pair knee), clear anodised (never black)"}
    for i_, (g, n, s) in enumerate(parts):
        for o_, n2_ in NAMEFIX.items(): n = n.replace(o_, n2_)
        parts[i_] = (g, n, s)
    rep["step_clean"] = {}; USER0 = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    for i_, (g, n, s) in enumerate(parts):
        if n.startswith(USER0): continue
        s2, r_ = USS.step_clean(s, n[:40]); rep["step_clean"][n[:60]] = r_
        if s2 is not s: parts[i_] = (g, n, s2)
    nb_ = sum(1 for v in rep["step_clean"].values() if (v.get("after") or v).get("bad_faces_after_step", 0) or (v.get("after") or v).get("solids_after_step", 1) != 1)
    print(f"step round trip: {len(rep['step_clean'])} parts, {nb_} with bad faces / not one solid after STEP ({time.time() - t0:.0f} s)", flush=True)
    # ---- export (USS.main, copied)
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")):
        if os.path.isfile(os.path.join(dd, "step", f)): os.remove(os.path.join(dd, "step", f))
    sd_stock = os.path.join(dd, "step", "stock"); os.makedirs(sd_stock, exist_ok=True)
    for f in os.listdir(sd_stock): os.remove(os.path.join(sd_stock, f))
    USER = USER0; sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith(("D8-", "D9-")) and any(k in n.lower() for k in ("screw", "m4x6", "clip"))                # USS.main's rule (R7 custom set unchanged)
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        elif hwr and not user:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(sd_stock, f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_').replace('.', 'p')[:60]}.step"))
        trep = {}; m = USS.tess_safe(s, fine=not user, report=trep)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        mat, rho = USS.material(n, user)
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L2 user-style", FACES={"1": round(float(F4[0]), 2), "K": round(float(F4[1]), 2), "2": round(float(F4[2]), 2),
                                                                 "3": round(float(F4[3]), 2)}, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    for fn in ("clips.json", "workspace.json"):                                                # the L1's frames (group dk = member 9 by the law), unchanged
        J = json.load(open(os.path.join(L1D, fn))); frs = [f for c in J["clips"] for f in c["frames"]] if fn == "clips.json" else J["poses"]
        assert all("dk" in f["G"] for f in frs if "G" in f and "l1b" in f["G"]), f"{fn}: the L1's frames lack group dk"
        shutil.copy(os.path.join(L1D, fn), os.path.join(dd, fn))
    d = dict(l1d); d.update(id=a.out, row_id=ID, l1_design=a.l1,
                            label="conecut-knee-knuckle-3r (verified config: slipper-nose + re-proportioned knee + J3 hard stop [-111.90, 122.74]; verified 18.28 / held 22.38), "
                                  "full CAD in the user's style",
                            level="L2 user-style (full CAD of the generation-8 winner)",
                            build_fixes_2026_10_17=dict(link_margin_mm=dict(l1b=USS.LINK_MARGIN["l1b"], l2=USS.LINK_MARGIN["l2"]), link2_climb_max_deg=L2_CLIMB,
                                                        d1="one running-face entry (+-0.02)", d2="K-phase band stated RSS (linear low end -0.02)",
                                                        d3=rep["crank_stack"], o4="link 2 machined from solid: drop up to 70 deg at J2 (stated on the part)",
                                                        note="docs/research/user_slipper_nose_fix.md + docs/research/conecut_mechanism_redteam.md"),
                            built_with="pipeline/conformal/param_cad/user_style_conecut.py (imports build_conecut_l1 - the gen-8 L1, which retargets build_slipper_l1 at the "
                                       "verified CCModel - then user_style_slipper unchanged: v5 O20 hubs, K plain clock-spring cap, link 1a line/arc chain + r 1.25 flank lug, "
                                       "4-strip machined bars 1b / 2 (link 2 drop <= 70 deg, machined from solid), O3 dowel-in-arc-slot K / J2 stops, the J3 stop (O2 dowel in "
                                       "member 3, R1.05-ended arc groove under link 2's J3 ring), member 3 + E strap, the re-proportioned knee link with MR63ZZ-pair bosses + "
                                       f"knee stop, BOTTOM fused with the pad mount; the slipper-nose drive with the D3 axial stack) on the L1 design's frames ({a.l1})")
    d["fits"] = fits(rep["crank_stack"])
    d["drive_build"] = dict((l1d.get("drive_build") or {}), kind="slipper-nose (docs/research/slipper_mechanism_redteam.md section 6), unchanged from gen 7: lobe ring (l2) -> "
                            "MR63ZZ follower at a_s 6.5 / psi 216 between the two 683ZZ of the straddle bell crank (dk, O3 pin in link 1b; D3 spacer + preload stack) -> bent "
                            "arm -> ISO 8734 O2.5 nose (DLC, mu 0.087) on the r 1.25 conjugate flank (link 1a's lug)",
                            nose_r=USS.NOSE_R, mu=float(RL1.CFG.get("mu", 0.087)), wear_test_pass_mu_max=0.105, crank_stack=rep["crank_stack"],
                            crank_raise_mm=round(lay["raise_mm"], 3), follower_shift_mm=round(lay["follower_shift_mm"], 3), kK=float(RL1.CFG["kK"]), g=float(RL1.CFG["g"]))
    d["j3_stop"] = dict(l1d.get("j3_stop") or {}, built=rep["j3_stop"])
    for j in d.get("joints", []):
        if j.get("joint") == "J3":
            j["part"] = (f"O20 x 12.25 v5 hub, MR117-2RS pair, encoder; HARD STOP on J3's own angle q3' (link 2 -> member 3) at {J3MIN:.2f} / {J3MAX:.2f} deg: ISO 8734 "
                         f"2 m6 x 5 440C dowel ground to 3.90, pressed through member 3's J3 disc at r {J3_RS:g}, in a {J3_GW:.2f} x {J3_GD:.2f} arc groove "
                         f"({rep['j3_stop']['groove_arc_deg']} deg, R{J3_GW / 2:.2f} ends) under link 2's J3 ring - inside the O20 stack")
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; rep["invalid_or_multi_solid"] = bad; rep["slaved"] = l1b["slaved"]
    rep["layout"] = {k: (np.round(v, 4).tolist() if isinstance(v, np.ndarray) else v) for k, v in lay.items()}
    rep["ring_root_skipped"] = list(USP.RING_ROOT_SKIPPED)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    if a.no_checks:
        rep["checks"] = "not run in this pass (--no-checks): run --checks-only on this design"
        json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"--no-checks: stopped after the export ({time.time() - t0:.0f} s)", flush=True); return
    run_checks(M, dd, stops, rep, t0, g3)


if __name__ == "__main__":
    main()
