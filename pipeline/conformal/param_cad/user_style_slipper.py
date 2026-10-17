"""Full user-style CAD of the generation-7 winner slipper-nose-knuckle-3r (round 10; VERIFIED frozen exact Bench(110,360) 18.49 /
score 93.28, held out 23.45, min fold margin th 5.006; docs/concepts/slipper-nose-knuckle-3r.md, docs/alignment/slipper-nose-knuckle-3r.md).

Kinematics are EXACTLY the verified model's: the shape is the L1's (pipeline/concept_l1/build_slipper_l1.fit = the claim's SNModel,
SN_CELL=lead, on rows best_params (mu 0.087, ang_min 25.2189), fit on Bench(60,160) fast = the frozen protocol's hand-over), every part
is designed in its member's home frame (the scapula frame at rest, GH = origin) and the judged clips.json / workspace.json are the
L1's (l1_slipper-nose: "G" + "T" per group = the model's own member transforms; K slaved to q2 by the lin law past the onset; the bell
crank = group dk = the model's member 9, posed by phi = |dK| / g about dR), asserted equal (params, tr, knee centre m, levels).

COPIED from user_style_roller.py (gen 6, never edited: the same chain, hubs, links, lobe ring, crank arm); imported unchanged:
user_style_minarc.py (v5 O20 hubs + caps, K clock spring, links 1b / 2 as 4-strip machined bars through the model's strap stations,
O3 dowel-in-arc-slot stops, the physical knee stop, sliver_free / step_bad_faces), user_style_pinknee.py (member 3 + E strap, arm pad
+ pad mount fused with the cut BOTTOM, upper-arm cuff, base at the J1 ring), build_slipper_l1.py (fit, law, stop windows, drive
geometry). The build spec is docs/research/slipper_mechanism_redteam.md section 6. What is new against gen 6:

  nose       the MR63ZZ flank roller and its ISO 2341 pin are DELETED: the crank's bent arm ends in an O6 tip boss with a reamed
             O2.495-2.500 hole; an ISO 8734 2.5 m6 x 6 type C dowel (1.4125 = 440C grade, >= 52 HRC, a-C:H DLC) is pressed 3 mm into
             it, flush with the arm's outer face, its rounded end 0.15 mm over the lug's skin-side face (59.96 mm from GH): the STOCK
             O2.5 nose (build spec 6.1: the flank re-cut for r 1.25, *_r125 exports; the verifier's column for r 1.25 is 18.49 = the
             claim's). Loctite 648, pressed with anti-seize. No head, no retaining part.
  flank      link 1a's lug: the r 1.25 mid-plane section (4 tangent arcs R 1.688 / 4.424 / 8.606 / 11.824 within 3 um, dK 0 -> 51.75)
             closed by its 6 mm back offsets (concentric arcs), extruded straight along z_c over the 3 mm lug (one constant section,
             no loft). DRAWING: exact ruled surface by 4-axis UV wire EDM (contours flank_bench_r125.csv top / bot at +-1.5 mm,
             taper 0.14-2.74 deg), profile +-0.02, ruling parallelism to the nose axis <= 0.005 over 2.2 mm, a-C:H DLC 2-3 um on a
             Cr / Si interlayer (< 250 C), PAO grease: the straight extrude in the CAD is the mid-plane section (<= 0.072 mm off the
             ruled surface at +-1.5); a STRAIGHT-extruded flank would edge-load the nose (p0 1144 MPa, red team finding 2).
  crank      (group dk) Ti-6Al-4V, 5-axis machined from solid: STRADDLE boss O10 x 10 with 2 x 683ZZ at its two ends (wave-washer
             preload 5-10 N) and the lobe follower MR63ZZ BETWEEN them in a clevis pocket on the O3 follower pin at a_s 6.5 / psi 216
             (the red team's real follower; static factor 3.07 against 1.31 for the side-by-side O10 x 6 of gen 6); the bent arm 6 x 3
             (straight run + the arc about hub K at r_c, a revolve) ending in the O6 tip boss of the nose.
  lobe ring  (group l2) 17-4PH H900, synthesised from the posed follower (the claim's law dK(q2) -> phi -> the follower centre in
             link 2's frame), offset by the roller radius, 3-point arcs; on hub 2's O20 ring / cap skirt, keyed by an O1 dowel at
             the onset phase + 0.35 deg of q2 (the red team's +0.75 deg K lead; drawn at the nominal phase = the loaded state).
  knee       (CLAUDE.md user decision 5 + the lead's build rule) pins a, b are MR63ZZ BALL-BEARING PAIRS: ISO 8734 O3 m6 440C pins
             pressed H7/m6 in the E boss / the arm pad, 2 x MR63ZZ in an O9 x 5.5 boss on the knee link (J6 housing, 0.5 mm
             shoulder, 3.3 mm proud of the bar AWAY from the skin), 0.5 mm inner-ring spacer, DIN 6799 RS 2.3 e-clip on a 0.3 mm land
             over a 0.1 shim; the physical knee stop at 180 - ang_min = 154.78 deg.
  R7         sliver_free + the STEP round trip (USM.step_bad_faces) on EVERY custom part before export (gen-6 carry-over c).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_slipper.py [--out user_slipper_nose] [--l1 l1_slipper-nose]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")
import user_style_minarc as USM                                                            # noqa: E402  (gen-4/4b full CAD, imported unchanged)
USP, US, BM, REPO = USM.USP, USM.US, USM.BM, USM.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_slipper_l1 as RL1                                                             # noqa: E402  (gen-7 L1: the verified model's fit, law, drive geometry)
assert RL1.MIN is BM, "build_slipper_l1 must patch the same build_minarc_l1 module the gen-4 CAD reads"
import numpy as np, cadquery as cq, trimesh                                                # noqa: E402
PB, SK, LV, unit, xform = US.PB, US.SK, US.LV, US.unit, US.xform
FULL = USP.FULL; at = USP.at; disc = USP.disc; prism = USP.prism; plane = USP.plane; rev = USP.rev
S = BM.S; HUB_R = US.HUB_R; T, W = US.T, US.W
GROUPS = dict(USM.GROUPS, dk=9)                                                             # + the posed bell crank (the model's member 9)
# the stock O2.5 nose: the red team's r 1.25 exports (build spec 6.1; same frame as the claim's r 1.1839 ones)
SPEC = json.load(open(os.path.join(REPO, "docs", "research", "slipper_mechanism", "spec_points_bench_r125.json")))
RES = json.load(open(os.path.join(REPO, "docs", "research", "slipper_mechanism", "results_bench_r125.json")))

# ---- link 1a (the short dyad)
L1A = dict(RL1.L1A_PATH, rf=0.5)                 # the chain: build_roller_l1.L1A_PATH (climb from J1's skirt + 0.15, was 0.2)
# ---- drive dimensions (red team build spec, docs/research/slipper_mechanism_redteam.md sections 2 / 6)
ROLL_R, ROLL_W = 3.0, 2.5                    # MR63ZZ 3 x 6 x 2.5 (the lobe follower; the flank roller is gone)
A_S, PSI_DEG = float(RES["follower_chosen"]["a_s"]), float(RES["follower_chosen"]["psi_deg"])   # the real lobe follower: a_s 6.5 at psi 216 deg
NOSE_R = float(SPEC["nose_r_flank"])         # 1.25: stock ISO 8734 O2.5 m6 (the flank is the r 1.25 synthesis)
NOSE_L, NOSE_CH = 6.0, 0.2                   # dowel length 6, 0.2 x 45 deg end chamfers (the tip end rounded by the supplier: drawn as a chamfer)
DK_FLANK = float(RES["flank"]["built_to_dK"])    # flank built to dK 51.75 (dK_lim 49.75 + 2 deg run-out)
LUG_BACK = 6.0                               # lug depth behind the flank
BOSS_R, BOSS_H, BRG_R, BRG_W = 5.0, 10.0, 3.5, 3.0   # STRADDLE boss O10 x 10: 683ZZ (3 x 7 x 3) seats at both ends, the follower between them
POCKET_H, POCKET_R = ROLL_W + 0.5, ROLL_R + 0.5      # the follower's clevis pocket: 0.25 axial each side (0.2 shims on the inner ring), 0.5 radial
CLEVIS_R = 2.5                               # clevis lug end radius round the O3 follower pin (1.0 wall)
SHIM_T = 0.2
PIN_R, BORE_R = 1.5, 1.6
ARM_W, ARM_T = 6.0, 3.0
ARM_UP = 1.0                                 # the straight run's underside at the boss axis, over the boss underside
TIP_R = 3.0                                  # O6 tip boss round the nose hole (the arm's end)
# knee pins: MR63ZZ pairs (the L1's: build_slipper_l1 KB_R / KB_H, ISO 8734 O3 m6 pins, DIN 6799 RS 2.3)
KB_R, KB_H, KB_SHOULDER, KB_LIP_R = RL1.KB_R, RL1.KB_H, 0.5, 2.6
KCLIP_R, KCLIP_T, KCLIP_LAND, KSHIM_T, KGROOVE_R = 3.0, 0.6, 0.3, 0.1, 1.15
FITS = [dict(f) for f in RL1.FITS]           # the L1's drawing notes, amended by the red team's build spec
FITS[0] = dict(where="nose dowel in the crank arm's O6 tip boss", fit="ISO 8734 2.5 m6 x 6 type C (1.4125, >= 52 HRC cert), reamed O2.495-2.500 (2-13 um "
               "interference with m6; H7/m6 alone is a transition fit with 0 N pull-out possible), Loctite 648, pressed 3.0 mm with anti-seize, flush with "
               "the arm's outer face; a-C:H DLC with the flank batch")
FITS[1] = dict(where="conjugate flank on link 1a", fit="exact ruled surface, 4-axis UV wire EDM + skim (contours flank_bench_r125.csv top / bot at +-1.5 mm), "
               "profile +-0.02 (target +-0.01), ruling parallelism to the nose axis <= 0.005 over 2.2 mm, a-C:H DLC 2-3 um on a Cr / Si interlayer (< 250 C), "
               "PAO grease without EP additives; the CAD shows the mid-plane section extruded along z_c")
FITS[3] = dict(where="crank pivot bearings (2 x 683ZZ straddling the follower in the O10 x 10 boss)", fit="pin O3 h5 17-4PH H900 (pressed H7/m6 in link 1b), "
               "housings O7 J6 at both boss ends with 0.5 mm floors to the follower pocket, wave washer 5-10 N preload under the DIN 6799 RS 2.3 clip")
FITS[4] = dict(where="lobe follower (MR63ZZ in the crank's clevis pocket)", fit="pin O3 h5 pressed H7/m6 through both clevis prongs (flush), 2 x 0.2 mm "
               "inner-ring shims, pocket 3.0 x O7 (0.25 axial, 0.5 radial running)")
FITS[2] = dict(where="crank pivot pin in link 1b", fit="O3 17-4PH H900 pin, ground m6 over its 3 mm press length in link 1b (H7) and h5 over the 683ZZ inner rings; DIN 6799 RS 2.3 e-clip in a groove with a 0.3 mm land, wave washer under it")
FITS.append(dict(where="lobe ring on hub 2", fit="bore O20 H7 on the J2 upper ring / cap skirt O20 g6, keyed by an O1 dowel at the onset phase + 0.35 deg of q2 "
                 "(the red team's +0.75 deg K lead)"))
FITS.append(dict(where="knee pin e-clips", fit="DIN 6799 RS 2.3 in a O2.3 x 0.6 groove (H13) with a 0.3 mm land to the pin end, 0.1 mm shim under the clip"))
FITS.append(dict(where="K phase (assembly; docs/HANDOFF.md 14:30 + docs/research/slipper_flank_robust.md)", fit="build the +0.75 deg K lead: lobe-ring key dowel at the "
                 "onset phase + 0.35 deg of q2, J2 stop B slot end at q2 -15.47 (the CAD draws the nominal -15.82 = the loaded state); keep the verified flank "
                 "(beta -176.684, no beta step); nose hole / crank pivot / lobe profile +-0.02 mm true position, r_c +-0.1 mm; assembly note: K phase at the "
                 "onset +0.75 +0.15 / -0.10 deg (was +-0.3: wider than the red team's stack covers; docs/research/user_slipper_nose_fix.md), shim the key dowel"))
FITS.append(dict(where="wear-test pass line (nose on the DLC flank; docs/HANDOFF.md section 9, docs/alignment/slipper-nose-knuckle-3r.md 15:17 audit)",
                 fit="PASS only if the measured nose / flank friction mu <= 0.105 over the wear test (the horn's 43-deg pressure-angle rule caps mu at "
                     "0.108-0.113; the R17 forward bound at mu 0.15 is 5.00081 deg raw = FAIL on the unrounded gate (judge/dynamics.py 8f69bd6), "
                     "at mu 0.12 4.78 deg); verified at mu 0.087"))
FITS.append(dict(where="knee stop tooth (knee link) against the E strap's side face", fit="stop at knee angle 180 - ang_min = 154.78 deg, 1.62 deg above "
                 "the workspace's largest knee angle 153.16 (clips <= 130.6): tooth face and the E strap's side face profile +-0.02 mm each (EDM / ground) "
                 "-> +-0.04 mm stack at the 6.8 mm contact radius = +-0.34 deg, stop 154.44..155.12, >= 1.28 deg margin; ISO 2768-f (+-0.05 each) would "
                 "leave 0.78 deg"))
FITS.append(dict(where="crank running faces (D9-01 against links 1a / 1b / 2; the posed drive check's 0.086-0.123 mm running gaps)",
                 fit="the crank's two boss faces + arm sides and the facing pads of links 1a / 1b / 2: profile +-0.02 mm (worst two-face stack 0.04 "
                     "< the 0.086 mm smallest gap); ISO 2768-f (+-0.05, stack 0.10) could close the 0.086 gap - never leave these faces to the general "
                     "tolerance"))


# ---------------------------------------------------------------------------------------------------- link 1a
def link1a_path(M):
    """the centre-line chain of link 1a in span(u1, uK): build_roller_l1.link1a_path (one source for the L1 keep-out and this part:
    J1 seat face at J1's skirt + clr_J1 -> concave bend R -> <= 60-deg ramp -> convex bend R onto the K pad plane -> K run -> K seat
    face). Returns (ex, ey, start, segs, info)"""
    return RL1.link1a_path(M)


def link1a_vs_model(M, ex, ey, start, segs):
    """the built bar's underside vs the model's L1a strap stations (link_rows): signed height (mm) of the bar underside over the
    model's underside along each station's direction, inside / outside the hub zones"""
    prof = BM.link_rows(M); lk, rows = prof["L1a"]; P, H, _ = SK.sample(start, segs, m=60)
    nrm = np.c_[np.cos(H - math.pi / 2), np.sin(H - math.pi / 2)]                      # right of the heading = toward the skin (x down)
    bot = P + (T / 2) * np.where((nrm @ np.array([1.0, 0.0]))[:, None] < 0, nrm, -nrm)
    Uu, C, F4, hr = BM.joints4(M); out = []
    for dv, keep, r in rows:
        for j in np.nonzero(keep)[0]:
            d3 = dv[j]; x, y = float(d3 @ ex), float(d3 @ ey)
            if abs(float(d3 @ np.cross(ex, ey))) > 0.08: continue                        # off the bar's mid-plane strip
            ang = math.atan2(y, x); ab = np.arctan2(bot[:, 1], bot[:, 0]); k = int(np.argmin(np.abs(ab - ang)))
            if abs(ab[k] - ang) > 0.01: continue
            out.append(float(np.linalg.norm(bot[k]) - r[j]))
    out = np.array(out) if out else np.zeros(1)
    return dict(stations=int(len(out)), over_model_min_mm=round(float(out.min()), 3), over_model_mean_mm=round(float(out.mean()), 3), over_model_max_mm=round(float(out.max()), 3))


def link1a_body(M, stops, lug):
    """link 1a: J1 pad + the chain bar + K pad (glued on the seat faces), the J1 integral pin, the K arbor (no magnet pocket),
    the flank lug + its web (fused), then K's two opposed stop slots cut through pad and web"""
    Uu, C, F4, hr = BM.joints4(M); H = lambda j: C[j] + F4[j] * Uu[j]
    ex, ey, start, segs, info = link1a_path(M)
    bar = US.bar_swept(ex, ey, start, segs, t=T, w=W, r=0.3)
    padA = USP.plate_R(Uu[0], F4[0], ey, W, hr[0], L=info["seat_J1_mm"], rf=L1A["rf"])
    sd_b = info["sd_b"][0] * ex + info["sd_b"][1] * ey
    padB = USP.plate_R(Uu[1], F4[1], sd_b, W, hr[1], L=info["seat_K_mm"], rf=L1A["rf"])
    body = US.glue(US.glue(padA, bar), padB)
    body = body.fuse(US.lower_pin(Uu[0], F4[0])).fuse(arbor_pin_roller(Uu[1], F4[1]))
    if lug is not None:
        for s_ in lug: body = body.fuse(s_)
    q_lo, q_hi = stops["K"]["q"]
    for th in stops["K"]["homes"]: body = body.cut(USM.arc_slot_cutter(H(1), Uu[1], th + q_lo, th + q_hi, -1.0, BM.PLATE + 0.1))
    body = body.clean() if body.clean().isValid() else body
    info.update(vs_model=link1a_vs_model(M, ex, ey, start, segs), valid=body.isValid(), solids=len(body.Solids()))
    info.pop("sd_b")
    return body, info


def arbor_pin_roller(k, F):
    """link 1a's K pin: v5 collar + integral O7 pin continued as the O5 spring arbor with the 0.4 mm slit (no magnet pocket: K is not read)"""
    c = USM.CAPK; k = unit(k)
    pin = PB.revolved([(0, 1.5), (4.1, 1.5), (4.1, LV["L1"]), (3.5, LV["L1"]), (3.5, LV["N1"]), (c["arbor_r"], LV["N1"]), (c["arbor_r"], c["arbor_top"]),
                       (0, c["arbor_top"])], k, F)
    e, f = USM.frame2(k); sw = c["slit_w"] / 2
    return pin.cut(prism((F + c["ch_z0"] + 0.05) * k, e, f, [(1.3, -sw), (c["arbor_r"] + 0.5, -sw), (c["arbor_r"] + 0.5, sw), (1.3, sw)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"] - 0.3))


# ---------------------------------------------------------------------------------------------------- links 1b, 2 (USM.build_links, link 1a replaced)
LINK_MARGIN = dict(l1b=None, l2=None)          # set by main (--link-margin / --l1b-margin): USM.MARGIN while each bar's profile is built
def build_links(M, stops, lug):
    """USM.build_links' links 1b and 2 (copied: the 4-strip machined bars, pads, rings, bores, pins, slots, dowels), link 1a = link1a_body"""
    Uu, C, F4, hr = BM.joints4(M); prof = BM.link_rows(M); out = []; rep = {}; H = lambda j: C[j] + F4[j] * Uu[j]
    PL = BM.PLATE; link_gh, link_cols = USM.link_gh, USM.link_cols
    body, rep["link 1a"] = link1a_body(M, stops, lug)
    q_lo, q_hi = stops["K"]["q"]
    out.append(("l1a", f"D8-02a link 1a: 8x3 bar on ONE line/arc chain in span(u1, uK) (J1 seat at the J1 skirt + {L1A['clr_J1']:g}, "
                       f"{rep['link 1a']['ramp_deg']:.0f}-deg ramp, R{L1A['R']:g} centre-line bends: 5-axis machined from solid, tighter than the 15 mm bent-bar rule), "
                       f"J1 / K pads + integral O7 pins, K pin continued as the O5 spring arbor (0.4 mm slit, no magnet: K is slaved); K's two opposed "
                       f"{math.degrees(q_hi - q_lo):.1f}-deg stop slots in the K pad; the flank lug (the r 1.25 conjugate flank: 4 tangent arcs; 4-axis UV wire-EDM ruled surface, a-C:H DLC) + its web (Ti-6Al-4V)", body))
    print(f"  link 1a: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}; {rep['link 1a']}", flush=True)
    # ---- link 1b: K upper (1) -> J2 lower (2)   (USM.build_links, copied)
    m0 = USM.MARGIN; USM.MARGIN = LINK_MARGIN["l1b"] if LINK_MARGIN["l1b"] is not None else m0
    try: body, ex, ey, start, fit, r, Ls, rf, sd_b = link_gh(M, prof, "L1b", "link 1b", 1, 2, True, False)
    finally: r_m1b = USM.MARGIN; USM.MARGIN = m0
    body = US.glue(USP.plate_R(Uu[1], F4[1] + LV["U0"], ey, W, hr[1], L=Ls, upper=True, rf=rf), body)
    body = US.glue(body, USP.plate_R(Uu[2], F4[2], sd_b, W, hr[2], L=Ls, rf=rf))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"]) if fit["segs"] else (body, 0)
    body = USP.ring_root_R(US.glue(body, USP.upper_ring_R(Uu[1], F4[1], hr[1])), Uu[1], F4[1], hr[1])
    body = body.cut(USP.bore_cutter_R(Uu[1], F4[1], hr[1]))
    body = body.fuse(US.lower_pin(Uu[2], F4[2]))
    q_lo, q_hi = stops["J2"]["q"]
    for th in stops["J2"]["homes"]: body = body.cut(USM.arc_slot_cutter(H(2), Uu[2], th + q_lo, th + q_hi, -1.0, PL + 0.1))
    dws = []
    for i, th in enumerate(stops["K"]["homes"]):
        dw, hole = USM.dowel_at(H(1), Uu[1], th, F4[1]); body = body.cut(hole)
        dws.append(("l1b", f"K stop dowel {i + 1} of 2: {USM.DOWEL_STOCK} (stop A dK 0 / stop B dK {math.degrees(stops['K']['q'][0] if abs(stops['K']['q'][0]) > 1e-9 else stops['K']['q'][1]):.2f}), "
                           "pressed 3 mm in the K upper boss, polished", dw))
    body = body.clean() if body.clean().isValid() else body
    body, sl_1b = USM.sliver_free(body, "link 1b")
    out.append(("l1b", f"D8-02b link 1b: 8x3 bar on a line/arc chain, K upper pad + O20 ring + M18 spigot + bore (2 dowel holes), J2 pad + integral O7 pin "
                       f"with the {math.degrees(q_hi - q_lo):.1f}-deg q2 stop slot; carries the crank pivot pin ({r['process']})", body))
    rep["link 1b"] = dict(fit, **r, pocket=npk, valid=body.isValid(), solids=len(body.Solids()), slivers=sl_1b, margin_mm=r_m1b)
    print(f"  link 1b: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}", flush=True)
    out += dws
    # ---- link 2: J2 upper (2) -> J3 upper (3, offset line)   (USM.build_links, copied)
    D = M.D; u, c = D.u, D.c; F = M.f
    Cj = [c[k_] + F[k_] * u[k_] for k_ in range(3)]
    ex = unit(u[1]); ey = unit(Cj[2] - (Cj[2] @ ex) * ex); nP = np.cross(ex, ey)
    u3p = unit(u[2] - (u[2] @ nP) * nP); lean = math.degrees(math.asin(abs(float(u[2] @ nP)))); phi = math.atan2(u3p @ ey, u3p @ ex)
    ha, hb = F[1] + LV["U0"] + T / 2, F[2] + LV["U0"] + T / 2
    p3 = c[2] + hb * u[2]; B = np.array([p3 @ ex, p3 @ ey]); back = np.array([math.sin(phi), -math.cos(phi)])
    Ls, rf = USP.HUG_SEAT, USP.HUG_RF; start = (ha, Ls, math.pi / 2); end = (*(B + Ls * back), math.pi / 2 + phi)
    Dq, Rq = link_cols(M, *prof["L2"])
    axes = [((0.0, 0.0), (1.0, 0.0)), (tuple(B), (math.cos(phi), math.sin(phi)))]
    m0 = USM.MARGIN; USM.MARGIN = LINK_MARGIN["l2"] if LINK_MARGIN["l2"] is not None else m0
    try: body, r = (USM.profile_link_split if USM.SPLIT else USM.profile_link)("link 2", ex, ey, start, end, Dq, Rq, axes, [hr[2], hr[3]]); fit = dict(segs=None)
    finally: r_m2 = USM.MARGIN; USM.MARGIN = m0
    back_w = math.sin(phi) * ex - math.cos(phi) * ey
    body = US.glue(USP.plate_R(u[1], F[1] + LV["U0"], ey, W, hr[2], L=Ls, upper=True, rf=rf), body)
    body = US.glue(body, at(USP.plate_R(u[2], F[2] + LV["U0"], back_w, W, hr[3], L=Ls + 0.6, upper=True, rf=rf), c[2]))
    body = USP.ring_root_R(US.glue(body, USP.upper_ring_R(u[1], F[1], hr[2])), u[1], F[1], hr[2])
    body = US.glue(body, at(USP.upper_ring_R(u[2], F[2], hr[3]), c[2]))
    body = body.cut(USP.bore_cutter_R(u[1], F[1], hr[2])).cut(at(USP.bore_cutter_R(u[2], F[2], hr[3]), c[2]))
    for th in stops["J2"]["homes"]:
        dw, hole = USM.dowel_at(H(2), Uu[2], th, F4[2]); body = body.cut(hole)
        out.append(("l2", f"J2 stop dowel: {USM.DOWEL_STOCK} (q2 stops {stops['J2']['meta']['window_deg'][0]:.2f} / {stops['J2']['meta']['window_deg'][1]:.2f} deg: "
                          f"stop B = the drive's range dK 46.25), pressed 3 mm in the J2 upper boss, polished; stop push limit "
                          f"{USM.j2_push_limit()['push_limit_Nm_s0_1']:.1f} N.m (J2 MR117 pair s0 1.0)", dw))
    # (gen-6 fix) no O18 groove on the J2 upper ring any more: the lobe ring seats on the J2 cap's O20 skirt (band F2 + 9.8..12.8), so the
    # groove at LOBE_Z (the first lobe seat) was a stale cut (the verifier's finding e)
    body = body.clean() if body.clean().isValid() else body
    body, sl_2 = USM.sliver_free(body, "link 2")
    out.append(("l2", f"D8-03 link 2: 8x3 bar on a line/arc chain + J2 / J3 O20 rings, J2 dowel hole, flies over the knee and the pad ({r['process']})", body))
    rep["link 2"] = dict(**r, seat_mm=Ls, pad_round_mm=rf, u3_lean_out_of_plane_deg=lean, valid=body.isValid(), solids=len(body.Solids()), slivers=sl_2, margin_mm=r_m2)
    print(f"  link 2: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}", flush=True)
    return out, rep


# ---------------------------------------------------------------------------------------------------- hubs (K: plain clock-spring cap)
def cap_k_plain(k, F, crown):
    """hub K's clock-spring cap without the sensor pocket (K is never read): the v5 skirt / flange, the wall to the crown with an
    R0.5 corner, a FLAT crown; inside the spring chamber O16 round the arbor, the outer-hook slot. Lines + tangent arcs, revolved."""
    c = USM.CAPK; R = HUB_R; z0, z1, zc = LV["H1"] + 0.05 + F, LV["U1"] + F, crown + F; q = 1 - math.sqrt(0.5); r = 0.5
    wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(R, z0).lineTo(R, zc - r).threePointArc((R - r * q, zc - r * q), (R - r, zc))
          .lineTo(0.0, zc).lineTo(0.0, c["ch_z1"] + F).lineTo(c["ch_r"], c["ch_z1"] + F).lineTo(c["ch_r"], c["ch_z0"] + F).lineTo(4.5, c["ch_z0"] + F)
          .lineTo(4.5, z1).lineTo(9.0, z1).close())
    cap = xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k))
    e, f = USM.frame2(k); k = unit(k); r0, r1, w = c["hook_slot"]
    cap = cap.cut(prism(F * k + c["ch_z0"] * k, e, f, [(-r1, -w - 0.1), (-r0, -w - 0.1), (-r0, -0.1), (-r1, -0.1)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"]))
    return cap.clean() if cap.clean().isValid() else cap


def hubs(M):
    """USM.hubs with hub K's plain clock-spring cap (no sensor pocket, no magnet: K is slaved, never read)"""
    Uu, C, F4, hr = BM.joints4(M); out = []; rep = {}
    capK = float(M.p.get("capK", 0) or 0); crown = LV["top"] + capK
    for J, j, lo, hi in (("J1", 0, "l1a", "base"), ("K", 1, "l1a", "l1b"), ("J2", 2, "l1b", "l2"), ("J3", 3, "l3", "l2")):
        for g, n, s in US.hardware(J, Uu[j], F4[j], lo, hi):
            if " cap " in n: continue
            out.append((g, n, at(s, C[j])))
        if J != "K":
            style = USM.CAP_STYLE
            if J == "J2": USM.CAP_STYLE = "flat"                                                  # the lobe ring's seat: a cylindrical skirt to the crown
            try: cap, Rc = USM.cap_v5(Uu[j], F4[j])
            finally: USM.CAP_STYLE = style
            rep.setdefault("caps", {})[J] = "flat" if Rc is None else f"dome R{Rc:.1f}"
            out.append((hi, (f"{J} cap O20, torispherical dome R{Rc:.1f} / R1 (tangent arcs)" if Rc else f"{J} cap O20 x crown F+12.25, flat crown, R0.5 corner (the lobe ring's seat)")
                        + ", threaded M18x0.5 (Ti-6Al-4V)", at(cap, C[j])))
        else:
            cap = cap_k_plain(Uu[j], F4[j], crown); sp, Lsp = USM.clock_spring(Uu[j], F4[j]); sp_ = USM.SPRING
            out.append((hi, f"K clock-spring cap O20 x crown F+{crown:.2f} ({capK:g} mm taller), FLAT crown, no sensor pocket (K is slaved, never read): spring "
                            f"chamber O16 x {USM.CAPK['ch_z1'] - USM.CAPK['ch_z0']:.1f}, outer-hook slot, threaded M18x0.5, pinned to link 1b's ring at the spring's "
                            "preload index (Ti-6Al-4V)", at(cap, C[j])))
            rmax = sp_["r0"] + (sp_["n"] - 1) * sp_["d"]
            out.append((hi, f"K clock spring: 0.3 x 5 mm {sp_['steel']} strip, {Lsp:.1f} mm, {sp_['n']} half-turns R{sp_['r0']:g}..R{rmax:.2f}, outer hook in the cap slot, "
                            f"inner end in the arbor slit; {sp_['rate']:g} N.m/rad, {sp_['preload']:g} N.m preload on stop A = the closing spring of both rolling pairs "
                            "(the nose on the flank, the follower on the lobe) (polished spring steel)", at(sp, C[j])))
            rmax = sp_["r0"] + (sp_["n"] - 1) * sp_["d"] + sp_["t"] / 2
            rep["K"] = dict(crown_mm=crown, capK=capK, spring_length_mm=round(Lsp, 1), spring=dict(sp_), cap_valid=cap.isValid(), spring_valid=sp.isValid(),
                            spring_outer_r_mm=round(rmax, 3), chamber_r_mm=USM.CAPK["ch_r"], cap="flat crown, no sensor (K slaved)")
            assert rmax <= USM.CAPK["ch_r"]
    return out, rep


# ---------------------------------------------------------------------------------------------------- drive geometry
def rotm(ax, a):
    ax = unit(np.asarray(ax, float)); Kx = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * Kx + (1 - math.cos(a)) * Kx @ Kx


def l1b_top_under(body, ax, r, z_lo, z_hi):
    """highest point (along ax, through GH) of a solid within radius r of the axis line, between z_lo and z_hi (tessellation)"""
    vs, fs = body.copy().tessellate(0.05, 0.3); V = np.array([[v.x, v.y, v.z] for v in vs]); m = trimesh.Trimesh(V, np.array(fs), process=False)   # a copy: a triangulated part exports a STEP that fails BRepCheck
    P = np.r_[V, trimesh.sample.sample_surface_even(m, 60000, seed=3)[0]]; h = P @ ax; w = P - np.outer(h, ax); rr = np.linalg.norm(w, axis=1)
    sel = (rr < r) & (h > z_lo) & (h < z_hi)
    return float(h[sel].max()) if sel.any() else None


def drive_layout(M, lg, dg, l1b_body):
    """crank stack on the BUILT link 1b: boss underside zb = max(model's, link 1b's top under the O10 footprint + 0.15) (the L1's
    stack fix), STRADDLE boss O10 x 10 (683ZZ seats at both ends), the follower MR63ZZ centred between the two bearings at
    s_f = zb + 5 on dR, at the red team's a_s 6.5 / psi 216 deg (the crank turns about dR: the same law; the lobe is synthesised
    for it). The red team's own follower centre (spec_points follower_centre_onset) is checked against a_s / psi."""
    D = M.D; u2 = unit(D.u[1]); dR = unit(dg["dR"]); f2 = float(M.f[1])
    top = l1b_top_under(l1b_body, dR, BOSS_R + 0.6, dg["zboss"] - 6.0, dg["zboss"] + 12.0)
    zb = max(dg["zboss"], (top if top is not None else -1e9) + 0.15)
    s_f = zb + BOSS_H / 2
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); psi = math.radians(PSI_DEG)
    v = math.cos(psi) * e1 + math.sin(psi) * e2; F0 = s_f * dR + A_S * v
    Frt = np.array(SPEC["follower_centre_onset"], float); s0 = float(Frt @ dR); chk = float(np.linalg.norm((Frt - s0 * dR) - A_S * v))
    assert chk < 0.02, f"follower frame differs from the red team's: {chk}"
    return dict(zb=zb, l1b_top=top, raise_mm=zb - dg["zboss"], s_f=s_f, F0=F0, v=v, F0_redteam=Frt, follower_shift_mm=s_f - s0,
                follower_hmid_over_f2=float(F0 @ u2) - f2, dR=dR, u2=u2, f2=f2, follower_check_mm=chk)


def lobe_pitch(M, lg, dg, lay, n=97):
    """the follower centre over the stroke in link 2's HOME frame: t (q2 past the onset) 0 .. t_stop, q2 = q2hi + s_q t, dK = the
    law, phi = sig |dK| / g about dR (the model's _sc_pose), link 2 = rotm(u2, q2) in link 1b's frame (the L1's drive sweep)"""
    law = lg["law"]; ts = np.linspace(0.0, law["t_stop_deg"], n); q2 = law["q2hi_deg"] + law["s_q"] * ts
    dk = RL1.dK_of_q2(lg, q2); u2 = lay["u2"]; out = []
    for q_, k_ in zip(q2, dk):
        ph = dg["sig"] * float(RL1.RF.phi_of(math.radians(k_), dg["g"], dg["c"]))
        C1b = dg["PV"] + rotm(dg["dR"], ph) @ (lay["F0"] - dg["PV"])
        out.append(rotm(u2, math.radians(q_)).T @ C1b)
    return np.array(out), ts, q2, dk


def circ3(a, m, b):
    A_ = 2 * np.array([[m[0] - a[0], m[1] - a[1]], [b[0] - a[0], b[1] - a[1]]]); c = np.linalg.solve(A_, [m @ m - a @ a, b @ b - a @ a]); return c, float(np.linalg.norm(a - c))


def lobe_ring(M, lg, dg, lay):
    """the lobe ring (link 2's home frame). The wall is ruled along the follower axis at mid-stroke (e_ext, wire-EDM with the
    taper), the faces square to u2 (band = the follower roller +- 1.3 along u2): sketch in the plane square to e_ext through the
    follower mid-level on the u2 axis - the projected pitch curve offset by the roller radius (3-point arcs through the profile),
    the onset joined by the roller's own circle and a radial line into the dwell circle (0.1 mm under the projected dwell
    locus: the follower runs free there, K on stop A), a straight return flank 8 deg past the end; extruded, cut to the band,
    bore O20 (on the J2 cap skirt)"""
    Cp, ts, q2, dk = lobe_pitch(M, lg, dg, lay); u2 = lay["u2"]; f2 = lay["f2"]
    qm = 0.5 * (q2[0] + q2[-1]); e_ext = unit(rotm(u2, math.radians(qm)).T @ lay["dR"])
    if e_ext @ u2 < 0: e_ext = -e_ext
    hz = float(np.mean(Cp @ u2)); O = hz * u2                                                    # sketch origin: the u2 axis at the follower mid-level
    bx = unit(Cp[0] - (Cp[0] @ e_ext) * e_ext - (O - (O @ e_ext) * e_ext)); by = np.cross(e_ext, bx)
    pr = lambda X: np.c_[(X - O) @ bx, (X - O) @ by] if X.ndim == 2 else np.array([(X - O) @ bx, (X - O) @ by])
    P = pr(Cp)                                                                                   # projected pitch curve (2-D)
    T_ = np.gradient(P, axis=0); T_ = T_ / np.linalg.norm(T_, axis=1)[:, None]; N_ = np.c_[-T_[:, 1], T_[:, 0]]
    if float(np.mean(np.einsum("ij,ij->i", N_, P))) > 0: N_ = -N_                                # inward (toward the u2 axis)
    prof = P + ROLL_R * N_
    # dwell: the follower's locus with phi = 0 is the circle |C| about u2 (projected: an ellipse); the dwell circle sits 0.1 under it
    rho0 = float(np.linalg.norm(Cp[0] - (Cp[0] @ u2) * u2)); tilt = math.acos(float(abs(e_ext @ u2)))
    r_dw = rho0 * math.cos(tilt) - ROLL_R - 0.1
    az = lambda p: math.atan2(p[1], p[0]); pol = lambda r, a: np.array([r * math.cos(a), r * math.sin(a)])
    pc0 = P[0]; Qr = pc0 - ROLL_R * unit(pc0); Qd = pol(r_dw, az(pc0)); P0 = prof[0]
    aQ, aP = az(Qr - pc0), az(P0 - pc0); da = (aP - aQ + math.pi) % (2 * math.pi) - math.pi; Mq = pc0 + ROLL_R * np.array([math.cos(aQ + da / 2), math.sin(aQ + da / 2)])
    nP = len(prof); idx = list(range(0, nP - 1, 16)) + [nP - 1]
    if idx[-1] - idx[-2] < 6: idx.pop(-2)
    sgn = 1.0 if az(prof[-1]) - az(prof[0]) > 0 else -1.0
    a_f = az(prof[-1]) + sgn * math.radians(8.0); Pf = pol(r_dw, a_f)
    a_q = az(Qd); span = (sgn * (a_q - a_f)) % (2 * math.pi); Mb = pol(r_dw, a_f + sgn * span / 2)      # the long way round, past the return flank
    pl = cq.Plane(origin=tuple(map(float, O)), xDir=tuple(map(float, bx)), normal=tuple(map(float, e_ext)))
    wp = cq.Workplane(pl).moveTo(*Pf).threePointArc(tuple(Mb), tuple(Qd))
    if np.linalg.norm(Qr - Qd) > 1e-3: wp = wp.lineTo(*Qr)
    wp = wp.threePointArc(tuple(Mq), tuple(P0))
    for i, j in zip(idx[:-1], idx[1:]): wp = wp.threePointArc(tuple(prof[(i + j) // 2]), tuple(prof[j]))
    ring = wp.lineTo(*Pf).close().extrude(6.0, both=True).val()
    hlo, hhi = float((Cp @ u2).min()) - ROLL_W / 2 - 0.05, float((Cp @ u2).max()) + ROLL_W / 2 + 0.05
    ring = ring.intersect(disc(np.zeros(3), u2, 30.0, hlo, hhi)).cut(disc(np.zeros(3), u2, HUB_R, hlo - 1, hhi + 1))
    ring = ring.clean() if ring.clean().isValid() else ring
    dev = []
    for i, j in zip(idx[:-1], idx[1:]):
        c_, R_ = circ3(prof[i], prof[(i + j) // 2], prof[j]); dev += [abs(float(np.linalg.norm(prof[k] - c_)) - R_) for k in range(i, j + 1)]
    pr_r = np.linalg.norm(prof, axis=1)
    info = dict(e_ext_to_u2_deg=round(math.degrees(tilt), 2), band_over_f2_mm=[round(hlo - f2, 3), round(hhi - f2, 3)], pitch_r_mm=[round(float(np.linalg.norm(P, axis=1).min()), 3), round(float(np.linalg.norm(P, axis=1).max()), 3)],
                profile_r_mm=[round(float(pr_r.min()), 3), round(float(pr_r.max()), 3)], dwell_r_mm=round(r_dw, 3), arcs=len(idx) - 1,
                arc_chain_dev_max_mm=round(max(dev), 5), stroke_q2_deg=[round(float(q2[0]), 3), round(float(q2[-1]), 3)],
                past_O20_max_mm=round(float(pr_r.max()) - HUB_R, 3), valid=ring.isValid(), solids=len(ring.Solids()),
                key="O1 dowel key at the onset phase + 0.35 deg of q2 (red team K lead +0.75 deg; drawn at the nominal = loaded phase)")
    return ring, info, dict(e_ext=e_ext, O=O, bx=bx, by=by, Cp=Cp, q2=q2, dk=dk)


def lug_trim_radius(wall):
    """trimlug-k165-knuckle-3r's cut on the built r 1.25 flank: r_trim = the farthest flank contact from K's axis over the drive's own range
    [0, dK_lim] (flank_bench_r125.csv contact points, link 1a's frame) + wall; the model's is 19.77 + 1.5 = 21.27 at its r 1.1839 nose"""
    import csv
    uK = unit(np.array(SPEC["uK"], float)); lim = float(SPEC["dK_lim_deg"])
    rows = list(csv.DictReader(open(os.path.join(REPO, "docs", "research", "slipper_mechanism", "flank_bench_r125.csv"))))
    X = np.array([[float(r_["contact_" + a_]) for a_ in "xyz"] for r_ in rows if float(r_["dK_deg"]) <= lim + 1e-9])
    rK = np.linalg.norm(X - (X @ uK)[:, None] * uK, axis=1)
    return float(rK.max()) + float(wall), float(rK.max())


def flank_lug(M, dg, trim_wall=None):
    """link 1a's flank lug (link 1a home frame): the red team's 3 tangent arcs (results_bench flank_arcs, fit within 3 um of the
    exact flank, dK 0 -> 48.25) closed by their 6 mm back offsets (concentric arcs) and two normal end lines, in flank_sketch_frame,
    extruded straight along z_c over the 3 mm lug (h0 +- 1.5); the web to the K pad: an inner tab at the pad level (fK .. fK + 3,
    r <= 10.4 of uK) + an outer riser (r >= 10.4) up into the lug, each a line sketch extruded along uK"""
    fr = SPEC["flank_sketch_frame"]; ex, ey, ez = (np.array(fr[k], float) for k in ("ex", "ey", "ez")); h0 = float(SPEC["flank_mid_plane_h"])
    arcs = RES["flank_arcs"]; Cs = [np.array(a["centre"]) for a in arcs]; Rs = [float(a["r"]) for a in arcs]
    pts = [np.array(arcs[0]["p0"])] + [np.array(a["p1"]) for a in arcs]; mids = [np.array(a["pm"]) for a in arcs]; na = len(arcs)
    off = lambda c, r, p: c + (r + LUG_BACK) * unit(p - c)
    # back chain: junctions offset along the shared normal (concentric arcs; the flank is concave toward the nose on 100 % of the stroke)
    back = [off(Cs[0], Rs[0], pts[0])] + [0.5 * (off(Cs[i], Rs[i], pts[i + 1]) + off(Cs[i + 1], Rs[i + 1], pts[i + 1])) for i in range(na - 1)] + [off(Cs[-1], Rs[-1], pts[-1])]
    bmid = [off(Cs[i], Rs[i], mids[i]) for i in range(na)]
    pl = cq.Plane(origin=tuple(map(float, (h0 - 1.5) * ez)), xDir=tuple(map(float, ex)), normal=tuple(map(float, ez)))
    wp = cq.Workplane(pl).moveTo(*pts[0])
    for i in range(na): wp = wp.threePointArc(tuple(mids[i]), tuple(pts[i + 1]))
    wp = wp.lineTo(*back[na])
    for i in reversed(range(na)): wp = wp.threePointArc(tuple(bmid[i]), tuple(back[i]))
    lug = wp.close().extrude(3.0).val()
    ball = cq.Solid.makeSphere(h0 + 1.5, US.V(np.zeros(3)), angleDegrees1=-90, angleDegrees2=90)
    lug = lug.intersect(ball)
    # web: planform in the K pad plane (frame2(uK)), from inside the pad to 2 mm behind the flank's dK-0 end and the back corner
    Uu, C, F4, hr = BM.joints4(M); uK = unit(Uu[1]); fK = float(F4[1]); e, f = USM.frame2(uK)
    X3 = lambda p, h: p[0] * ex + p[1] * ey + h * ez
    A3 = X3(pts[0] + 2.0 * unit(pts[0] - Cs[0]), h0); B3 = X3(back[0], h0)
    p2 = lambda X: np.array([X @ e, X @ f]); a2, b2 = p2(A3), p2(B3); ang = [math.atan2(v[1], v[0]) for v in (a2, b2)]
    am = math.atan2(math.sin(ang[0]) + math.sin(ang[1]), math.cos(ang[0]) + math.cos(ang[1])); hw = math.radians(13.0)
    pol = lambda r, a: (r * math.cos(a), r * math.sin(a))
    r_in, r_tab, r_ris = 8.0, 11.0, (HUB_R + 0.5) / math.cos(hw)                              # the riser's inner chord stays >= 10.5 from uK (link 1b's K boss / cap: r 10)
    inner = prism(fK * uK, e, f, [pol(r_in, am - hw), pol(r_tab, am - hw), pol(r_tab, am + hw), pol(r_in, am + hw)], [0] * 4, 3.0)
    rel = lambda a: (a - am + math.pi) % (2 * math.pi) - math.pi
    o_lo, o_hi = sorted([tuple(a2), tuple(b2)], key=lambda q: rel(math.atan2(q[1], q[0])))
    quad = [pol(r_ris, am - hw), o_lo, o_hi, pol(r_ris, am + hw)]
    hl = float(M.p["hl"])
    riser = prism((fK + hl) * uK, e, f, quad, [0] * 4, 14.0).cut(disc(np.zeros(3), ez, 90.0, h0, h0 + 40.0))   # top = the lug's mid plane (embedded 1.5)
    web = US.glue(inner, riser.intersect(ball))
    z_lug = h0; trim = None
    if trim_wall is not None:                                                                  # trimlug-k165-knuckle-3r: ONE coaxial cylinder cut about uK
        r_trim, r_c_max = lug_trim_radius(trim_wall); assert np.allclose(uK, unit(np.array(SPEC["uK"], float)), atol=1e-6)
        cyl = disc(np.zeros(3), uK, r_trim, -120.0, 120.0); v0 = lug.Volume() + web.Volume()
        lug = lug.intersect(cyl); web = web.intersect(cyl)
        trim = dict(rule="trimlug-k165-knuckle-3r: lug band kept where r_K <= the farthest flank contact over [0, dK_lim] + wall (one cylinder about uK)",
                    wall_mm=float(trim_wall), contact_r_max_mm=round(r_c_max, 3), r_trim_mm=round(r_trim, 3), model_r_trim_mm=21.27,
                    removed_mm3=round(v0 - lug.Volume() - web.Volume(), 2), lug_solids=len(lug.Solids()), web_solids=len(web.Solids()))
        print(f"  lug trim: r_K <= {r_trim:.2f} (contact max {r_c_max:.2f} + {trim_wall:g}), removed {trim['removed_mm3']} mm3, valid {lug.isValid()} / {web.isValid()}", flush=True)
    info = dict(arcs=[dict(r=r_, dK=a["dK"]) for r_, a in zip(Rs, arcs)], built_to_dK=DK_FLANK, nose_r=NOSE_R,
                extrude="CAD: the mid-plane section extruded straight along z_c (one constant section); DRAWING: the exact ruled surface by 4-axis UV wire EDM "
                        "(taper 0.14-2.74 deg, <= 0.072 mm off the straight extrude at +-1.5); top trimmed to the sphere r h0 + 1.5 (the model's lug band)",
                lug_band_mm=[round(h0 - 1.5, 3), round(h0 + 1.5, 3)], back_mm=LUG_BACK, web_bottom_over_fK_mm=round(hl, 3),
                lug_valid=lug.isValid(), web_valid=web.isValid(), trim=trim)
    return [lug, web], info


def arm_arc(dg, lay):
    """the arm's arc concentric with hub K: a REVOLVE about uK of its annular section (bottom on the sphere r rA, 3 mm thick
    radially from GH, 6 wide about r_c) from the tangent point (psT) to ARM_END past the roller (beta)"""
    uK, tK0, bK0 = unit(dg["uK"]), dg["tK0"], dg["bK0"]; rc, rA, h = dg["rc"], dg["rA"], dg["h_tip"]
    a0, a1 = dg["psT"], dg["beta"]; lo, hi = min(a0, a1), max(a0, a1); span = math.degrees(hi - lo)   # ends on the nose axis: the O6 tip boss rounds it
    d = lambda a: math.cos(a) * tK0 + math.sin(a) * bK0
    def sect(r_):
        n = math.hypot(r_, h); return (r_ * rA / n, h * rA / n)
    pb0, pb1 = sect(rc - ARM_W / 2), sect(rc + ARM_W / 2); pbm = sect(rc)
    s_ = lambda p, f_: (p[0] * f_, p[1] * f_); ft = (rA + ARM_T) / rA
    def build(x0, ang):
        pl = cq.Plane(origin=(0.0, 0.0, 0.0), xDir=tuple(map(float, x0)), normal=tuple(map(float, np.cross(x0, uK))))
        wp = (cq.Workplane(pl).moveTo(*pb0).threePointArc(pbm, pb1).lineTo(*s_(pb1, ft)).threePointArc(s_(pbm, ft), s_(pb0, ft)).close())
        return wp.revolve(ang, (0, 0, 0), (0, 1, 0)).val()
    arc = build(d(lo), span)
    cm = np.array(arc.Center().toTuple()); cm_ang = math.atan2(float(cm @ bK0), float(cm @ tK0))
    if abs(((cm_ang - 0.5 * (lo + hi)) + math.pi) % (2 * math.pi) - math.pi) > math.radians(5):
        arc = build(d(hi), span)
        cm = np.array(arc.Center().toTuple()); cm_ang = math.atan2(float(cm @ bK0), float(cm @ tK0))
    ok = abs(((cm_ang - 0.5 * (lo + hi)) + math.pi) % (2 * math.pi) - math.pi) < math.radians(5)
    return arc, dict(span_deg=round(span, 2), from_deg=round(math.degrees(a0), 2), to_deg=round(math.degrees(a1), 2), r_c=rc, bottom_sphere_r=round(rA, 3), direction_ok=ok)


ARM_MODE = os.environ.get("SLIPPER_ARM", "profile")                                           # profile (gen-6 fix: through the model's stations) | chord (gen 6 first build)


def arm_profile(dg, lay, l1b_body):
    """the arm's straight run as ONE side-view sketch (lines + tangent arcs, 2.5-D, extruded ARM_W across) in the plane through GH
    spanned by the boss axis dR and the arc's tangent point T3: its underside runs THROUGH the model's arm stations (the L1's
    arm_mesh rule: the model's levels, the root raised to the boss underside + ARM_UP and let down on the <= 60-deg ramp, every row
    lifted to keep RUNG over link 1b's BUILT bar over the crank's whole swing), the top offset ARM_T along the normals; it ends on
    the arc's start section (bottom rA at T3). Replaces the gen-6 first build's chord, which held the run up to the boss level
    while the model's arm dips to its strap (R1: dk -15.6k skin samples in band vs the L1). Returns (solid, info)."""
    dR = unit(lay["dR"]); zb = lay["zb"]; st = dg["straight"]; Lch = dg["Lch"]; ns = dg["ns"]; d_s = np.linspace(0.0, Lch, ns)
    keep = d_s > RL1.ARM_ROOT + 1e-6; dd = np.r_[RL1.ARM_ROOT, d_s[keep]]
    rows = np.array([[np.interp(x, d_s, st[:, c, k]) for k in range(3)] for x in dd for c in range(4)]).reshape(len(dd), 4, 3)
    lv = np.linalg.norm(rows.mean(axis=1), axis=1); z0 = zb + ARM_UP
    want = np.maximum(lv, z0 - math.tan(math.radians(60.0)) * np.maximum(dd - BOSS_R, 0.0)); rows = rows * (want / lv)[:, None, None]
    vs, fs = l1b_body.tessellate(0.05, 0.3); dg2 = dict(dg, strap_L1b=trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False))
    lifted = RL1.arm_over_strap(dg2, rows)
    ex = dR; T3 = np.asarray(dg["T3"], float); ey = unit(T3 - (T3 @ ex) * ex)
    th = np.array([math.atan2(float(r.mean(0) @ ey), float(r.mean(0) @ ex)) for r in rows])
    rho = np.array([float(np.linalg.norm(r, axis=1).max()) for r in rows]) + lifted
    thB = math.atan2(float(T3 @ ey), float(T3 @ ex)); rA = float(dg["rA"])
    sel = th < thB - math.radians(0.3)
    U = [np.array([z0, 0.0])] + [r_ * np.array([math.cos(t_), math.sin(t_)]) for t_, r_ in zip(th[sel], rho[sel])] + [rA * np.array([math.cos(thB), math.sin(thB)])]
    U2 = [U[0]]
    for p_ in U[1:]:
        if np.linalg.norm(p_ - U2[-1]) > 0.3: U2.append(p_)
    U = U2; n = len(U)
    d = [unit(U[i + 1] - U[i]) for i in range(n - 1)]; nr = [np.array([-v[1], v[0]]) for v in d]
    if float(nr[0] @ unit(U[1])) < 0: nr = [-v for v in nr]                                   # normals away from GH (the top side)
    top = [U[0] + ARM_T * nr[0]]
    for i in range(1, n - 1): top.append(U[i] + ARM_T * (nr[i - 1] + nr[i]) / (1.0 + float(nr[i - 1] @ nr[i])))
    top.append(U[-1] * (rA + ARM_T) / rA)                                                       # the end face on the arc's radial start section
    changed = True
    while changed and len(top) > 2:
        changed = False
        for i in range(1, len(top) - 1):
            if float((top[i] - top[i - 1]) @ (top[i + 1] - top[i])) < 0: del top[i]; changed = True; break
    pts = [tuple(p_) for p_ in U] + [tuple(p_) for p_ in reversed(top)]
    want_r = [0.0] + [2.0] * (len(pts) - 1); rad = USP.safe_radii(pts, want_r)
    for i in (0, n - 1, n, len(pts) - 1): rad[i] = 0.0                                          # root (in the boss) and the arc joint stay sharp
    sol = USP.prism(np.zeros(3), ex, ey, pts, rad, ARM_W, both=True)
    over = [float(np.linalg.norm(p_)) - float(np.interp(math.atan2(p_[1], p_[0]), th, np.linalg.norm(rows, axis=2).max(1))) for p_ in U[1:-1]] or [0.0]
    info = dict(stations=int(len(rows)), vertices=len(pts), underside_over_model_rows_mm=[round(min(over), 3), round(max(over), 3)],
                lifted_over_built_l1b_mm=[round(float(x), 3) for x in lifted], root_level_mm=round(z0, 3), min_level_mm=round(float(min(np.linalg.norm(u_) for u_ in U)), 3),
                level_end_mm=round(rA, 3), valid=sol.isValid(),
                process="2.5-D side-view sketch (lines + R2 tangent arcs) through the model's arm stations, extruded 6 across; part of the 5-axis crank")
    print(f"arm straight run (profile through the model's stations): {len(rows)} rows, {len(pts)} vertices, levels {z0:.2f} -> min {info['min_level_mm']:.2f} -> {rA:.2f}, "
          f"lifted over link 1b {max(lifted):.2f}, valid {sol.isValid()}", flush=True)
    return sol, info


def crank_parts(M, dg, lay, l1b_body=None):
    """the bell crank (member 9 home frame = link 1b at phi 0) + its hardware; the pivot pin + clip (link 1b). STRADDLE layout (red team
    build spec 4): boss O10 x 10 from zb, 683ZZ seats O7 x 3 at both ends, a 4 mm web between them (O3.2 pin clearance); the clevis lug
    (stadium from the boss axis to the follower pin, end R2.5, the boss height) with the follower pocket O7 x 3.0 between the two bearing
    seats (0.5 mm floors); the bent arm (straight run + arc about hub K) ending in the O6 tip boss of the nose dowel"""
    dR, zb, F0, s_f = lay["dR"], lay["zb"], lay["F0"], lay["s_f"]; uK = unit(dg["uK"]); C0 = np.asarray(dg["C0"], float); cr = unit(C0)
    ztop = zb + BOSS_H
    boss = rev([(BORE_R, BRG_W), (BRG_R, BRG_W), (BRG_R, 0.0), (BOSS_R, 0.0), (BOSS_R, BOSS_H), (BRG_R, BOSS_H), (BRG_R, BOSS_H - BRG_W), (BORE_R, BOSS_H - BRG_W)],
               zb * dR, dR)
    foot = F0 - (F0 @ dR) * dR; xf = unit(foot); yf = np.cross(dR, xf)
    clevis = USP.stadium(zb * dR, xf, yf, A_S, CLEVIS_R, BOSS_H)
    # straight run: chord from the boss (on the axis, underside ARM_UP over the boss underside) to the arc's tangent point
    T3 = uK * dg["h_tip"] + dg["rc"] * (math.cos(dg["psT"]) * dg["tK0"] + math.sin(dg["psT"]) * dg["bK0"]); B = unit(T3) * (dg["rA"] + ARM_T / 2)
    A = (zb + ARM_UP + ARM_T / 2) * dR; ex = unit(B - A); up = unit(dR - (dR @ ex) * ex); L = float(np.linalg.norm(B - A)) + 1.0
    straight = US.bar_swept(ex, up, (0.0, 0.0, 0.0), [(0.0, L)], t=ARM_T, w=ARM_W, origin=A, r=0.3); arm_info = dict(mode="chord")
    if ARM_MODE == "profile" and l1b_body is not None:
        try:
            s2, i2 = arm_profile(dg, lay, l1b_body)
            if s2.isValid() and len(s2.Solids()) == 1: straight, arm_info = s2, dict(i2, mode="profile")
            else: arm_info["profile_rejected"] = f"valid {s2.isValid()}, solids {len(s2.Solids())}"
        except Exception as e_: arm_info["profile_rejected"] = repr(e_)[:200]
    arc, ainfo = arm_arc(dg, lay)
    zA0, zA1 = dg["rA"] - dg["R0"], dg["rA"] + ARM_T - dg["R0"]                                 # arm underside / top along the nose axis, from C0
    tip = disc(C0, cr, TIP_R, zA0, zA1)
    crank = US.glue(boss, clevis)
    for part in (straight, arc, tip): crank = crank.fuse(part)
    crank = crank.cut(disc(np.zeros(3), dR, BRG_R, zb - 1.0, zb + BRG_W))                      # lower 683ZZ seat O7 x 3
    crank = crank.cut(disc(np.zeros(3), dR, BRG_R, ztop - BRG_W, ztop + 1.0))                  # upper 683ZZ seat O7 x 3
    crank = crank.cut(disc(np.zeros(3), dR, BORE_R, zb - 1.0, ztop + 1.0))                     # O3.2 through the web
    crank = crank.cut(disc(foot, dR, POCKET_R, s_f - POCKET_H / 2, s_f + POCKET_H / 2))        # the follower's clevis pocket (open toward the lobe)
    crank = crank.cut(disc(foot, dR, PIN_R, zb - 0.5, ztop + 0.5))                             # follower pin press hole through both prongs
    crank = crank.cut(disc(C0, cr, NOSE_R, zA0 - 0.5, zA1 + 0.5))                               # the nose dowel's reamed hole in the tip boss
    # (no clean(): OCC's same-domain unify hangs on the revolve + pipe faces of this crank)
    brg = [rev([(PIN_R, 0.0), (BRG_R, 0.0), (BRG_R, BRG_W), (PIN_R, BRG_W)], (zb + z0) * dR, dR) for z0 in (0.0, BOSS_H - BRG_W)]
    froll = rev([(PIN_R, -ROLL_W / 2), (ROLL_R, -ROLL_W / 2), (ROLL_R, ROLL_W / 2), (PIN_R, ROLL_W / 2)], F0, dR)
    zr0 = s_f - ROLL_W / 2; zr1 = s_f + ROLL_W / 2
    shims = [rev([(PIN_R + 0.05, z0), (2.25, z0), (2.25, z0 + SHIM_T), (PIN_R + 0.05, z0 + SHIM_T)], foot, dR) for z0 in (zr0 - SHIM_T, zr1)]
    fpin = rev([(0.0, zb), (PIN_R, zb), (PIN_R, ztop), (0.0, ztop)], foot, dR)
    nose = rev([(0.0, zA1 - NOSE_L), (NOSE_R - NOSE_CH, zA1 - NOSE_L), (NOSE_R, zA1 - NOSE_L + NOSE_CH), (NOSE_R, zA1 - NOSE_CH), (NOSE_R - NOSE_CH, zA1), (0.0, zA1)], C0, cr)
    l1b_top = lay["l1b_top"] if lay["l1b_top"] is not None else dg["lev"] + T
    ppin = rev([(0.0, l1b_top - T - 0.0), (PIN_R, l1b_top - T), (PIN_R, ztop + 1.4), (0.0, ztop + 1.4)], np.zeros(3), dR)
    pclip = rev([(1.15, ztop + 0.15), (3.0, ztop + 0.15), (3.0, ztop + 0.75), (1.15, ztop + 0.75)], np.zeros(3), dR)
    ang_arm_fol = math.degrees(math.acos(float(np.clip(unit(B - (B @ dR) * dR) @ xf, -1, 1))))
    info = dict(boss_mm=[round(zb, 3), round(ztop, 3)], boss_raised_over_model_mm=round(lay["raise_mm"], 3), l1b_top_under_boss_mm=None if lay["l1b_top"] is None else round(lay["l1b_top"], 3),
                layout="straddle: 683ZZ seats zb..zb+3 and ztop-3..ztop, follower pocket s_f +- 1.5 between them (0.5 mm floors)",
                follower_centre_on_dR_mm=round(s_f, 3), follower_shift_along_dR_vs_redteam_mm=round(lay["follower_shift_mm"], 3), follower_hmid_over_f2_mm=round(lay["follower_hmid_over_f2"], 3),
                arm_vs_follower_azimuth_deg=round(ang_arm_fol, 1), straight_run_mm=round(L, 2), arm_root_up_mm=ARM_UP, arc=ainfo, straight_run=arm_info,
                crank_valid=crank.isValid(), crank_solids=len(crank.Solids()), nose_centre_r_mm=round(dg["R0"], 3),
                nose_dowel_from_GH_mm=[round(dg["R0"] + zA1 - NOSE_L, 3), round(dg["R0"] + zA1, 3)], nose_engagement_mm=round(zA1 - zA0, 3),
                lug_skin_face_r_mm=round(dg["R0"] - 1.5, 3), pivot_pin_mm=[round(l1b_top - T, 3), round(ztop + 1.4, 3)])
    parts = [("dk", f"D9-01 drive bell crank (Ti-6Al-4V, 5-axis machined from solid): STRADDLE boss O10 x {BOSS_H:g} (683ZZ seats O7 x 3 at both ends), clevis lug "
                    f"to the follower pin at a_s {A_S:g} / psi {PSI_DEG:g} with the follower pocket O7 x {POCKET_H:g} between the bearings, bent arm 6 x 3 (straight run "
                    f"{'through the model arm stations (side-view line/arc profile)' if arm_info['mode'] == 'profile' else f'{L:.1f} mm chord'} + the arc about hub K at r_c "
                    f"{dg['rc']:.2f}, a revolve, {ainfo['span_deg']:.1f} deg), O6 tip boss reamed O2.495-2.500 for the nose; all bores one setup +-5 um", crank),
             ("dk", "drive crank bearing 1 683ZZ 3x7x3 (polished)", brg[0]), ("dk", "drive crank bearing 2 683ZZ 3x7x3, wave-washer preloaded 5-10 N (polished)", brg[1]),
             ("dk", f"drive lobe follower roller MR63ZZ 3x6x2.5 at a_s {A_S:g} mm, psi {PSI_DEG:g} deg, between the crank bearings (polished)", froll),
             ("dk", "drive follower inner-ring shim 1 O3.1 x O4.5 x 0.2 (stainless, polished)", shims[0]),
             ("dk", "drive follower inner-ring shim 2 O3.1 x O4.5 x 0.2 (stainless, polished)", shims[1]),
             ("dk", f"drive follower pin O3 h5 17-4PH H900 x {BOSS_H:g}, pressed H7/m6 through both clevis prongs, flush (polished)", fpin),
             ("dk", f"drive nose dowel ISO 8734 2.5 m6 x {NOSE_L:g} type C (1.4125 = 440C grade, >= 52 HRC), a-C:H DLC, pressed 3 mm in the arm's O6 tip boss "
                    f"(reamed O2.495-2.500, Loctite 648), flush with the outer face, rounded end {dg['R0'] + zA1 - NOSE_L:.2f} mm from GH on the flank (polished)", nose),
             ("l1b", "drive crank pivot pin O3 h5 17-4PH H900, pressed in link 1b (polished)", ppin),
             ("l1b", "drive crank pivot pin clip DIN 6799 RS 2.3 (polished)", pclip)]
    return parts, info


def knee_pin_bb(name, cen, sn, tr, tp, lower_grp, knee_grp, cen_knee=None):
    """replaces user_style_pinknee.pin_stack (IGLIDUR-PIN) for the MR63ZZ-pair knee (CLAUDE.md user decision 5 + the lead's build rule):
    returns (seat, hardware). The ISO 8734 O3 m6 pin is pressed H7/m6 in the lower plate (E boss / arm pad, tr..tr+tp; drawn as the press
    fit: the pin solid overlaps its plate, same member); the 0.5 mm inner-ring spacer in the running gap; the two MR63ZZ in the knee link's
    O9 x 5.5 boss (z0 .. z0 + 5.5, a 0.5 mm housing shoulder between them); 0.1 mm shim; DIN 6799 RS 2.3 e-clip in an O2.3 x 0.6 groove,
    0.3 mm land to the pin end. Levels along sn: lower plate tr..tr+tp, gap ..+RUN, knee link z0 = tr+tp+RUN."""
    run = USP.PK.RUN; z0 = tr + tp + run; ck = cen if cen_knee is None else cen_knee; r = 1.5
    zc0 = z0 + KB_H + KSHIM_T; ztop = zc0 + KCLIP_T + KCLIP_LAND
    pin = rev([(0.0, tr), (r - 0.2, tr), (r, tr + 0.2), (r, zc0), (KGROOVE_R, zc0), (KGROOVE_R, zc0 + KCLIP_T), (r, zc0 + KCLIP_T), (r, ztop - 0.2),
               (r - 0.2, ztop), (0.0, ztop)], cen, sn)
    hw = [(lower_grp, f"knee pin {name} ISO 8734 3 m6 x 10 faced to {ztop - tr:.1f}: 440C (1.4125) pressed H7/m6 in the {'E boss' if name == 'a' else 'arm pad'} over its full "
                      f"{tp:.2f} mm, O2.3 x 0.6 e-clip groove with a {KCLIP_LAND:g} mm land (polished)", pin),
          (lower_grp, f"knee pin {name} spacer: inner-ring spacer O3.1 x O4.5 x {run:g} (stainless, polished)", rev([(r + 0.05, tr + tp), (2.25, tr + tp), (2.25, z0), (r + 0.05, z0)], cen, sn))]
    hb = (KB_H - KB_SHOULDER) / 2
    for j, zz in enumerate((z0, z0 + hb + KB_SHOULDER)):
        hw.append((knee_grp, f"knee pin {name} bearing {j + 1} MR63ZZ: knee bearing {j + 1} of 2 MR63ZZ 3x6x2.5 (J6 housing, the pin's free length j5) (polished)",
                   rev([(r, zz), (3.0, zz), (3.0, zz + hb), (r, zz + hb)], ck, sn)))
    hw.append((lower_grp, f"knee pin {name} shim: O3.1 x O4.5 x {KSHIM_T:g} under the e-clip (stainless, polished)", rev([(r + 0.05, z0 + KB_H), (2.25, z0 + KB_H), (2.25, zc0), (r + 0.05, zc0)], cen, sn)))
    clip = rev([(KGROOVE_R + 0.01, zc0), (KCLIP_R, zc0), (KCLIP_R, zc0 + KCLIP_T), (KGROOVE_R + 0.01, zc0 + KCLIP_T)], cen, sn)
    e, f = (PB.axis_frame(sn)[:, 0], PB.axis_frame(sn)[:, 1])
    clip = clip.cut(prism(np.asarray(cen) + (zc0 - 0.5) * sn, e, f, [(0.9, -1.15), (4.0, -1.15), (4.0, 1.15), (0.9, 1.15)], [0, 0, 0, 0], KCLIP_T + 1.0))
    hw.append((lower_grp, f"knee pin {name} e-clip DIN 6799 RS 2.3: retaining e-clip (A2 stainless, polished)", clip))
    seat = disc(cen, sn, 1.0, tr + 0.3, tr + tp - 0.3)                                          # inside the plate: the fuse leaves the plate as it was
    return seat, hw


def knee_link_bb(M):
    """the knee link (USP.knee_link's planform: the model's knee box, R1 corners) with the two MR63ZZ bearing bosses O9 x 5.5 standing
    up from the plate (z0 .. z0 + 5.5, AWAY from the skin), housing O6 (J6) x 2.5 for each bearing, a 0.5 mm shoulder (O5.2 lip) between"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"]); PK = USP.PK
    z0 = tr + tp + PK.RUN; A = fr["A0m"]; Bp = fr["Bm"]; eK, nK = fr["eK"], fr["nK"]
    assert np.linalg.norm(A + lc * eK - Bp) < 1e-6
    e_ = PK.BOSS_R; hw_ = PK.KNEE_W / 2
    k = prism(A + z0 * sn, eK, nK, [(-e_, -hw_), (lc + e_, -hw_), (lc + e_, hw_), (-e_, hw_)], [USP.KNEE_CR] * 4, tp)
    hb = (KB_H - KB_SHOULDER) / 2
    for cen in (A, Bp):
        k = k.fuse(disc(cen, sn, KB_R, z0, z0 + KB_H))
    for cen in (A, Bp):
        k = k.cut(disc(cen, sn, 3.0, z0 - 1.0, z0 + hb)).cut(disc(cen, sn, 3.0, z0 + hb + KB_SHOULDER, z0 + KB_H + 1.0)).cut(disc(cen, sn, KB_LIP_R, z0 - 1.0, z0 + KB_H + 1.0))
    k = k.clean() if k.clean().isValid() else k
    Lk = lc + 2 * PK.BOSS_R
    print(f"knee link (MR63ZZ pairs): plate {Lk:.1f} x {PK.KNEE_W:.0f} x {tp:.2f}, bosses O{2 * KB_R:g} x {KB_H:g}, valid {k.isValid()}, solids {len(k.Solids())}", flush=True)
    return ("l4", 6, f"D8-05 knee link: flat plate {Lk:.1f} x {PK.KNEE_W:.0f} x {tp:.2f} (lines + R{USP.KNEE_CR:g} arcs) + two O{2 * KB_R:g} x {KB_H:g} bearing bosses "
                     f"({KB_H - tp:.2f} mm proud of the plate, away from the skin), each 2 x MR63ZZ in O6 J6 housings with a {KB_SHOULDER:g} mm shoulder (Ti-6Al-4V)", k)


def step_clean(s, label):
    """carry-over (c): every custom part goes through USM.sliver_free (zero-area faces re-sewn) and R7's STEP round trip (USM.step_bad_faces)
    before export; returns (solid, report)"""
    try:
        bad, zero, ns = USM.step_bad_faces(s)
    except Exception as e_:
        return s, dict(step="round trip failed: " + repr(e_)[:120])
    out = dict(bad_faces_after_step=bad, zero_area_faces=zero, solids_after_step=ns)
    if zero or bad:
        s2, how = USM.sliver_free(s, label); out["sliver_free"] = how
        if s2 is not s:
            b2, z2, n2 = USM.step_bad_faces(s2); out.update(after=dict(bad_faces_after_step=b2, zero_area_faces=z2, solids_after_step=n2)); s = s2
    return s, out


# ---------------------------------------------------------------------------------------------------- checks
def check_frames(M, dd, stops):
    """USM.check_frames (copied) on this chain: + the crank (member 9 -> group dk) and the flank lug / horn samples (member 1); the model's
    metal samples posed by the model's member transforms vs the posed exo.glb (scene_export.frame_xforms = the judges' path), exported
    vertices posed both ways, the dowels inside their slots"""
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
                if name in ("hubK", "hub2"):
                    k = 1 if name == "hubK" else 2; cen = C[k] + F4[k] * Uu[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ Uu[k])[:, None] * Uu[k], axis=1)
                    inslot = (rr > USM.SLOT_RS - USM.SLOT_W - 0.6) & (rr < USM.SLOT_RS + USM.SLOT_W + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]; d = d[~inslot]; dout = dout[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4), round(float(dout.max()), 4)]
                if name in ("L1a", "L1b", "L2"):
                    lk = next(x for x in M.geo.links if x["name"] == name); zone = np.zeros(len(Xp), bool)
                    for kk in (lk["ka"], lk["kb"]):
                        w = Xp - C[kk]; zone |= np.linalg.norm(w - (w @ Uu[kk])[:, None] * Uu[kk], axis=1) < hr[kk] + 2.5 + 0.5
                    do = d[~zone]
                    res[name + " outside hub zones"] = [round(float(do.max()), 4) if len(do) else None, int((~zone).sum()),
                                                        round(float(np.mean(do <= 0.5)), 4) if len(do) else None, round(float(np.median(do)), 4) if len(do) else None]
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                q_lo, q_hi = [math.degrees(x) for x in stops[key]["q"]]
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(ang - q_lo, 3), to_stop_hi_deg=round(q_hi - ang, 3), inside=bool(q_lo - 0.01 <= ang <= q_hi + 0.01))
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
                        knee_angle=round(float(K["Kn"]["ang"][i]), 1), stops=inside))
        print(f"  check {lab:34s} pose {i} {np.round(pz[:3], 1)} st {int(K['state'][i]):+d}: joints vs posed glb {joint:.3f} mm, other rigid {out[-1]['rigid_non_drive_max_mm']:.3f}, "
              f"drive [max, p95, outside] {drv}, straps outside zones {worst_o:.2f}; frames {fdev:.1e}; dK {inside['K']['angle_deg']:.2f} q2 {inside['J2']['angle_deg']:.2f} "
              f"in slot {inside['K']['inside']}/{inside['J2']['inside']}", flush=True)
    return out


def posed_drive_check(dd, n=60, frames=None):
    """posed exo.glb at clip frames (every len/n-th frame + the frames of largest |dK|; or the given frames, e.g. the workspace's closing
    poses at the drive's working end): signed distance (mm, negative = inside) of the moving drive pairs"""
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
             ("D9-02", "D8-02b"), ("drive crank bearing 1", "D8-02b")]
    frs = [f for c in C["clips"] for f in c["frames"]]
    pick = (frs[::max(1, len(frs) // n)] + sorted(frs, key=lambda f: -abs(f.get("knuckle", {}).get("dK", 0.0)))[:12]) if frames is None else frs
    res = {}
    for a_, b_ in pairs:
        try: (ga, ma), (gb, mb) = get(a_), get(b_)
        except StopIteration: res[f"{a_} | {b_}"] = "missing"; continue
        XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 3000, seed=4)[0]]; worst = (1e9, None)
        for fi, f in enumerate(pick):
            G = lambda g: np.array(f["G"][g]).reshape(3, 3) if g in f["G"] else np.eye(3); T = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xw = XA @ G(ga).T + T(ga); Xb = (Xw - T(gb)) @ G(gb)
            d = float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min())
            if d < worst[0]: worst = (round(d, 3), round(float(f.get("knuckle", {}).get("dK", 0.0)), 2))
        res[f"{a_} | {b_}"] = worst
    # the two rolling pairs over the driven frames: per-frame min distance (contact = ~0; a positive max = lift-off / play in the CAD)
    drv = sorted([f for f in frs if abs(f.get("knuckle", {}).get("dK", 0.0)) > 0.5], key=lambda f: abs(f["knuckle"]["dK"]))
    drv = drv[::max(1, len(drv) // 40)]
    for a_, b_ in (("drive lobe follower roller", "D9-02"), ("drive nose dowel", "D8-02a")):
        (ga, ma), (gb, mb) = get(a_), get(b_); XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 4000, seed=5)[0]]; ds = []
        for f in drv:
            G = lambda g: np.array(f["G"][g]).reshape(3, 3); T = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xb = ((XA @ G(ga).T + T(ga)) - T(gb)) @ G(gb)
            ds.append(float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min()))
        res[f"contact {a_} | {b_} (driven frames: min, max of the per-frame min)"] = [len(ds), round(min(ds), 3) if ds else None, round(max(ds), 3) if ds else None]
    return res


def drive_skin(dd, every=1, frames=None):
    """RL1.drive_skin (copied) on this build's drive parts (D9-* + drive hardware + link 1a with its flank lug): min signed skin distance per
    part over EVERY clip frame (body_pose.posed, winding-number sign); or over the given frames (the workspace's closing poses)"""
    import igl
    sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); import body_pose as BP
    C = json.load(open(os.path.join(dd, "clips.json"))) if frames is None else dict(clips=[dict(name="workspace", frames=[dict(f, held=f.get("held", False)) for f in frames])]); src = trimesh.load(os.path.join(dd, "exo.glb")); BF = np.ascontiguousarray(BP.F, np.int64)
    parts = {}
    for node in src.graph.nodes_geometry:
        g, nm = node.split("|")[:2]
        if not (nm.startswith(("D9-", "drive", "D8-02a"))) or "pivot pin" in nm: continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        parts[nm[:40]] = (g, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 6000, seed=11)[0]])
    best = {k: (1e9, None) for k in parts}; n03 = {k: 0 for k in parts}; n2 = {k: 0 for k in parts}; nfr = 0; per_clip = {}
    for cl in C["clips"]:
        cmin = 1e9
        for k, f in enumerate(cl["frames"]):
            if k % every: continue
            nfr += 1; Vb = np.ascontiguousarray(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"]))), float)
            for nm, (g, X) in parts.items():
                Qp = np.ascontiguousarray(X @ np.array(f["G"][g]).reshape(3, 3).T + np.array(f.get("T", {}).get(g, [0, 0, 0])), float)
                d = np.sqrt(igl.point_mesh_squared_distance(Qp, Vb, BF)[0]); w = igl.fast_winding_number(Vb, BF, Qp) > 0.5; v = float(np.where(w, -d, d).min())
                if v < best[nm][0]: best[nm] = (v, f"{cl['name']} frame {k}{' (held)' if f['held'] else ''}")
                n03[nm] += v < 0.3; n2[nm] += v < 2.0; cmin = min(cmin, v)
        per_clip[cl["name"]] = round(cmin, 3)
    worst = min(best.items(), key=lambda kv: kv[1][0])
    return dict(rule=">= 0.3 mm on every frame (gen-5 lobe ring: -0.26)", frames=nfr, every=every, min_mm=round(worst[1][0], 3), where=f"{worst[0]}: {worst[1][1]}",
                passes=bool(worst[1][0] >= 0.3), per_part={k: dict(min_mm=round(v[0], 3), at=v[1], frames_lt_0p3=n03[k], frames_lt_2=n2[k]) for k, v in best.items()},
                per_clip=per_clip)


def working_end(dd, dk_min=29.3):
    """the drive's working end (the gen-6 verifier's finding d: no judged clip frame reaches |dK| > 29.3 of the 46.25 cap): the posed
    drive pairs and the drive skin over the workspace's closing, feasible poses at |dK| >= dk_min (workspace.json, the L1's frames)"""
    W = json.load(open(os.path.join(dd, "workspace.json")))
    frs = [p for p in W["poses"] if p.get("eval_feasible") and abs(p.get("knuckle", {}).get("dK", 0.0)) >= dk_min]
    dks = [abs(p["knuckle"]["dK"]) for p in frs]
    out = dict(poses=len(frs), dK_range=[round(min(dks), 2), round(max(dks), 2)] if dks else None)
    if frs: out.update(pairs=posed_drive_check(dd, frames=frs), skin=drive_skin(dd, frames=frs))
    return out


def tess_safe(s, fine=True, report=None):
    """user_style_geneva.tess_safe (copied): 0.02 / 0.15 with a coarser retry when the welded mesh is not watertight"""
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


def material(n, user):
    nl = n.lower()
    if user: return "user part", None
    import re
    if re.match(r"D\d+-\d+", n):                                                                # our numbered machined parts: by their stated alloy, never by feature
        if "17-4ph" in nl: return "17-4PH", 7.8                                                   # words (gen-6 fix: "dowel hole(s)" made links 1b / 2 hardened steel)
        if "7075-T6" in n: return "7075-T6 (BOTTOM merged with the pad mount)", 2.81
        return "Ti-6Al-4V", USP.TI
    if "iglidur" in nl or "igubal" in nl: return "iglidur", USP.IGL
    if "bearing" in nl or "mr63zz" in nl or "683zz" in nl or "mr117" in nl: return "bearing steel", 7.8
    if "17-4ph" in nl: return "17-4PH", 7.8
    if "dowel" in nl or "iso 2341" in nl: return "hardened steel (polished)", 7.85
    if "clock spring" in nl: return "1.4310 spring steel (polished)", 7.9
    if any(k in nl for k in ("screw", "m4x6", "clip", "shim", "spacer")): return "stainless (polished)", 7.9
    if "iso 8734" in nl: return "440C / 1.4125 (polished)", 7.7
    if "7075-T6" in n: return "7075-T6 (BOTTOM merged with the pad mount)", 2.81
    if n.startswith("UPPER ARM CUFF"): return "AlSi10Mg", 2.68
    return "Ti-6Al-4V", USP.TI


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_slipper_nose"); ap.add_argument("--l1", default="l1_slipper-nose")
    ap.add_argument("--skip-base-search", action="store_true"); ap.add_argument("--checks-only", action="store_true")
    ap.add_argument("--working-end-only", action="store_true", help="only the working-end check on the built design (no rebuild)")
    ap.add_argument("--link-margin", type=float, default=0.1, help="links 1b / 2: underside clearance over the model strap outside the hub "
                    "footprints (USM.MARGIN; gen-7 v1 0.1, the fix 0)")
    ap.add_argument("--l1b-margin", type=float, default=None, help="link 1b's own margin (default = --link-margin)")
    ap.add_argument("--lug-trim", type=float, default=None, help="trimlug-k165-knuckle-3r: cut the flank lug + web at r_K <= the farthest flank "
                    "contact over [0, dK_lim] + this wall (mm; the verified row: 1.5)")
    ap.add_argument("--e-hull", choices=("hull", "stations"), default="hull", help="member 3's E strap underside: the upper hull of the model's "
                    "stations (gen-7 v1) or the stations themselves (the fix: no bridge over the strap's dips)")
    ap.add_argument("--id", default="slipper-nose-knuckle-3r", help="the verified row this CAD builds (label / design.json)")
    ap.add_argument("--no-checks", action="store_true", help="stop after the export (no posed drive / kinematics / skin / working-end checks)")
    a = ap.parse_args(MY_ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    if a.working_end_only:
        r = working_end(dd); print(json.dumps(r, indent=1, default=float)); json.dump(r, open(os.path.join(dd, "judge", "working_end.json"), "w"), indent=1, default=float); return
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
    print(f"fit (claim SNModel SN_CELL=lead, BEST + ang_min {RL1.CFG['ang_min']}) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']}; hub levels "
          f"{np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f}; law {lg['law']} ({time.time() - t0:.0f} s)", flush=True)
    l1_stops = l1d["stack_mm"]["stops"]; stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1_stops[key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1_stops[key].get("pair")))
    if a.checks_only:                                                                          # the checks alone on the built design (same fit, same stops)
        rep = json.load(open(os.path.join(dd, "build.json"))); run_checks(M, dd, stops, rep, t0); return
    rep = dict(fit=dict(params=dict(RL1.CFG), source=f"docs/concepts/rows/{RL1.ID}.json best_params (mu {RL1.CFG.get('mu')}, ang_min {RL1.CFG['ang_min']}) through the claim's SNModel, SN_CELL=lead (= {a.l1})",
                        gap_near_touch=rep0["gap"], hub_levels_J1_K_J2_J3=[float(x) for x in F4], tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr],
                        fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"]) for k, v in stops.items()},
               j2_push_limit=USM.j2_push_limit(), law=lg["law"])
    parts = []
    hw, rep["hubs"] = hubs(M); parts += hw
    LINK_MARGIN.update(l1b=a.l1b_margin if a.l1b_margin is not None else a.link_margin, l2=a.link_margin)
    USP.E_UNDERSIDE = a.e_hull
    lug, rep["flank lug"] = flank_lug(M, dg, a.lug_trim)
    lk, rep["links"] = build_links(M, stops, lug)
    l1b_body = next(s for g, n, s in lk if n.startswith("D8-02b"))
    lay = drive_layout(M, lg, dg, l1b_body)
    ring, rep["lobe"], lobe_g = lobe_ring(M, lg, dg, lay)
    cp, rep["crank"] = crank_parts(M, dg, lay, l1b_body)
    z_pp = rep["crank"]["pivot_pin_mm"]; i_1b = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-02b"))
    try:
        b_ = lk[i_1b][2].cut(disc(np.zeros(3), lay["dR"], PIN_R, z_pp[0] - 1.0, z_pp[0] + T + 1.0))
        bad_, zero_, ns_ = USM.step_bad_faces(b_); ok_ = b_.isValid() and len(b_.Solids()) == 1 and bad_ == 0 and ns_ == 1
    except Exception as e_: ok_, bad_, zero_ = False, str(e_), None
    if ok_:
        lk[i_1b] = (lk[i_1b][0], lk[i_1b][1].replace("carries the crank pivot pin", "carries the crank pivot pin in an O3 H7 bore"), b_)
        rep["crank"]["pivot_pin"] = f"O3 h6 pressed in an O3 H7 bore through link 1b (bore cut; STEP round trip 0 bad faces, {zero_} zero-area)"
    else:
        rep["crank"]["pivot_pin"] = (f"O3 h6 pressed in link 1b: drawn as the press fit (pin overlapping its bore); the bore cut fails R7's STEP round trip ({bad_} bad faces)")
    print(f"crank pivot pin: {rep['crank']['pivot_pin']}", flush=True)
    parts += lk
    parts.append(("l2", f"D9-02 drive lobe ring: 17-4PH H900, wire-EDM (taper {rep['lobe']['e_ext_to_u2_deg']:.1f} deg along the follower axis), profile r "
                        f"{rep['lobe']['profile_r_mm'][0]:.2f} -> {rep['lobe']['profile_r_mm'][1]:.2f} mm ({rep['lobe']['arcs']} 3-point arcs), dwell r {rep['lobe']['dwell_r_mm']:.2f}, "
                        f"bore O20 on the J2 cap skirt, band F+{rep['lobe']['band_over_f2_mm'][0]:.2f}..F+{rep['lobe']['band_over_f2_mm'][1]:.2f}, keyed by an O1 dowel at the "
                        "onset phase + 0.35 deg of q2 (the +0.75 deg K lead, +0.15 / -0.10 deg K; the CAD draws the nominal phase = the loaded state)", ring))
    parts += cp
    USP.pin_stack = knee_pin_bb                                                                # the knee pins: MR63ZZ pairs (member3 / arm_side call pin_stack)
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = knee_link_bb(M)
    ks_deg = (l1d.get("build_fixes") or {}).get("knee_stop_deg")
    if ks_deg is not None:
        s_, rep["knee stop"] = USM.knee_stop_on(M, s_, ks_deg, M._bench_K)
        n_ = n_.replace(" (Ti-6Al-4V)", f" + knee stop tooth behind pin a (its face meets the E strap's side at knee angle {ks_deg:g} deg = 180 - ang_min {RL1.CFG['ang_min']}) (Ti-6Al-4V)")
    parts.append((g_, n_, s_))
    Cc = json.load(open(os.path.join(L1D, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = USP.arm_side(M, l1b["mount"], cposes); parts += [(g, n, s) for g, _, n, s in arm]
    Wj = json.load(open(os.path.join(L1D, "workspace.json"))); frames = []; rel = []
    allf = [f for cl in Cc["clips"] for f in cl["frames"]] + [p for p in Wj["poses"] if p.get("eval_feasible")]
    for fi, f in enumerate(allf):
        g = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        Gb, Tb, G1, T1 = g("base"), t_("base"), g("l1a"), t_("l1a"); rel.append((Gb.T @ G1, Gb.T @ (T1 - Tb)))
        if fi % 3 == 0: frames.append((Gb, Tb, G1, T1))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    l1_body = next(s for g, n, s in parts if n.startswith("D8-02a"))
    if a.skip_base_search: USP.EAR_DZ = ()
    try: bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames)
    except (FileNotFoundError, OSError) as e_:                                                 # the ear skin check reads the envelope maps (.cache/maps_s1.pt)
        print(f"base: ear search needs {e_} - built without ears (as user_geneva_rod: the J1 upper member alone)", flush=True)
        USP.EAR_DZ = (); bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames); rep["base"]["ear_search"] = f"not run: {e_}"
    parts.append((bp[0], bp[2], bp[3]))
    print(f"parts built ({time.time() - t0:.0f} s)", flush=True)
    NAMEFIX = {"+ integral O4 pin a": "+ the O3 H7 seat of pin a (ISO 8734 m6 pressed; MR63ZZ-pair knee)",
               "+ integral O4 h9 pin, hard-anodised": "+ the O3 H7 seat of pin b (ISO 8734 m6 pressed; MR63ZZ-pair knee), clear anodised (never black)"}
    for i_, (g, n, s) in enumerate(parts):
        for o_, n2_ in NAMEFIX.items(): n = n.replace(o_, n2_)
        parts[i_] = (g, n, s)
    # ---- carry-over (c): sliver_free + R7's STEP round trip on every custom part
    rep["step_clean"] = {}; USER0 = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    for i_, (g, n, s) in enumerate(parts):
        if n.startswith(USER0): continue
        s2, r_ = step_clean(s, n[:40]); rep["step_clean"][n[:60]] = r_
        if s2 is not s: parts[i_] = (g, n, s2)
    nb_ = sum(1 for v in rep["step_clean"].values() if (v.get("after") or v).get("bad_faces_after_step", 0) or (v.get("after") or v).get("solids_after_step", 1) != 1)
    print(f"step round trip: {len(rep['step_clean'])} parts, {nb_} with bad faces / not one solid after STEP ({time.time() - t0:.0f} s)", flush=True)
    # ---- export
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")):
        if os.path.isfile(os.path.join(dd, "step", f)): os.remove(os.path.join(dd, "step", f))
    sd_stock = os.path.join(dd, "step", "stock"); os.makedirs(sd_stock, exist_ok=True)                 # the verifier's item (5b): stock hardware STEPs
    for f in os.listdir(sd_stock): os.remove(os.path.join(sd_stock, f))                                # for the drawing set, OUTSIDE step/ (R7 judges custom parts)
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith(("D8-", "D9-")) and any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        elif hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(sd_stock, f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_').replace('.', 'p')[:60]}.step"))
        trep = {}; m = tess_safe(s, fine=not user, report=trep)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        mat, rho = material(n, user)
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L2 user-style", FACES={"1": round(float(F4[0]), 2), "K": round(float(F4[1]), 2), "2": round(float(F4[2]), 2),
                                                                 "3": round(float(F4[3]), 2)}, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    # ---- clips / workspace: the L1's frames (group dk = the model's member 9, posed by the law) - copied unchanged
    for fn in ("clips.json", "workspace.json"):
        J = json.load(open(os.path.join(L1D, fn))); frs = [f for c in J["clips"] for f in c["frames"]] if fn == "clips.json" else J["poses"]
        assert all("dk" in f["G"] for f in frs if "G" in f and "l1b" in f["G"]), f"{fn}: the L1's frames lack group dk"
        shutil.copy(os.path.join(L1D, fn), os.path.join(dd, fn))
    lab_ = ("slipper-nose-knuckle-3r (verified config, mu 0.087, ang_min 25.22), full CAD in the user's style" if a.lug_trim is None else
            f"{a.id} (slipper-nose-knuckle-3r + the horn lug trimmed at the farthest flank contact + {a.lug_trim:g} mm wall; verified 18.51 / 23.47), "
            "full CAD in the user's style")
    d = dict(l1d); d.update(id=a.out, label=lab_, row_id=a.id, level=("L2 user-style (full CAD of the generation-7 winner)" if a.lug_trim is None else
                                                                   "L2 user-style (full CAD of the round-11 winner)"),
                            build_fixes_2026_10_17=dict(link_margin_mm=dict(l1b=LINK_MARGIN["l1b"], l2=LINK_MARGIN["l2"]), e_underside=a.e_hull,
                                                        lug_trim_wall_mm=a.lug_trim, note="docs/research/user_slipper_nose_fix.md"),
                            l1_design=a.l1,
                            built_with="pipeline/conformal/param_cad/user_style_slipper.py (user_style_minarc / user_style_pinknee parts: v5 O20 hubs, K plain clock-spring cap, "
                                       "link 1a as one line/arc chain (60-deg ramp, machined) + the r 1.25 flank lug, 4-strip machined bars 1b / 2, O3 dowel-in-arc-slot stops (K opposed "
                                       "pair, J2 single at the drive's range), member 3, knee link with MR63ZZ-pair bosses + knee stop, BOTTOM fused with the pad mount; the drive: lobe ring, "
                                       f"STRADDLE bell crank (2 x 683ZZ around the MR63ZZ follower), ISO 8734 O2.5 nose dowel on the DLC flank) on the L1 design's frames ({a.l1})")
    d["fits"] = FITS
    d["drive_build"] = dict(kind="slipper-nose (docs/research/slipper_mechanism_redteam.md section 6): lobe ring (l2) -> MR63ZZ follower at a_s 6.5 / psi 216 between the two "
                                 "683ZZ of the straddle bell crank (dk, O3 pin in link 1b) -> bent arm -> ISO 8734 O2.5 nose (DLC, mu 0.087) sliding on the r 1.25 conjugate flank "
                                 "(4 arcs, UV wire EDM, DLC) on link 1a's lug (l1a); one clock spring in K's cap closes both pairs",
                            nose_r=NOSE_R, mu=float(RL1.CFG.get("mu", 0.087)), wear_test_pass_mu_max=0.105,
                            wear_test_note="PASS only at measured mu <= 0.105: the horn's 43-deg rule caps mu at 0.108-0.113; the R17 forward bound at mu 0.15 is "
                                           "5.00081 deg raw = FAIL on the unrounded gate (judge/dynamics.py 8f69bd6); mu 0.12 4.78",
                            lug_trim=rep["flank lug"].get("trim"),
                            crank_raise_mm=round(lay["raise_mm"], 3), follower_shift_mm=round(lay["follower_shift_mm"], 3), kK=float(RL1.CFG["kK"]), g=float(RL1.CFG["g"]))
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; rep["invalid_or_multi_solid"] = bad
    rep["slaved"] = l1b["slaved"]                                                                 # the L1's declaration (same law, same frame keys, drive group dk rides l1b)
    rep["layout"] = {k: (np.round(v, 4).tolist() if isinstance(v, np.ndarray) else v) for k, v in lay.items()}
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    if a.no_checks:
        rep["checks"] = "not run in this pass (--no-checks): run --checks-only on this design"
        json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"--no-checks: stopped after the export ({time.time() - t0:.0f} s)", flush=True); return
    run_checks(M, dd, stops, rep, t0)


def run_checks(M, dd, stops, rep, t0):
    """the post-export checks (posed drive pairs, the model's metal vs the posed parts, drive skin, working end) on the built design dd"""
    rep.pop("checks", None)
    rep["drive_posed"] = posed_drive_check(dd); print(f"drive posed (mm, at dK): {rep['drive_posed']}", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep["check"] = check_frames(M, dd, stops)
    keys = sorted({k for r in rep["check"] for k in r["per_part"] if " " not in k})
    outside = {k: max(float(r["per_part"][k][2]) for r in rep["check"] if k in r["per_part"]) for k in keys}
    # the gen-7 verifier (VERIFY.md 1 + 4): the old flag all_within_0p5 tested the joint features and frames only; renamed, and the per-part
    # table of the model's metal OUTSIDE the built solids (winding number, the verifier's measure) added - the crank's is the model artefact
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), joint_features_and_frames_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   model_metal_outside_built_max_mm={k: round(v, 3) for k, v in outside.items()},
                                   model_metal_within_0p5_except_crank=all(v <= 0.5 for k, v in outside.items() if k != "crank"),
                                   crank_note="the model's crank samples (arm root inside link 1b's strap) are a model artefact (gen-6 L1 7.12); the built crank is the red team's",
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]), max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                   dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] for r in rep["check"]))
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"kinematics: {rep['kinematics_exact']} ({time.time() - t0:.0f} s)", flush=True)
    rep["drive_skin"] = drive_skin(dd)
    print(f"drive skin: { {k: v for k, v in rep['drive_skin'].items() if k != 'per_clip'} }", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep["working_end"] = working_end(dd)
    print(f"working end (workspace |dK| >= 29.3): {json.dumps(rep['working_end'], default=float)[:1500]}", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
