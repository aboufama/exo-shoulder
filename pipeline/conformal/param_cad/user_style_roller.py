"""Full user-style CAD of the generation-6 winner roller-longdyad-knuckle-3r (round 9; VERIFIED frozen exact Bench(110,360) 18.67 /
score 93.21, envelope-corrected 18.56, held out 23.73 - 23.72 at the auditor's knee fix ang_min 26.88; docs/concepts/
roller-longdyad-knuckle-3r.md, docs/alignment/roller-longdyad-knuckle-3r.md).

Kinematics are EXACTLY the verified model's: the shape is the L1's (pipeline/concept_l1/build_roller_l1.fit = the claim's RLModel
on rows best_params + ang_min 26.8823, fit on Bench(60,160) fast = the frozen protocol's hand-over), every part is designed in its
member's home frame (the scapula frame at rest, GH = origin) and the judged clips.json / workspace.json are the L1's
(l1_roller-longdyad: "G" + "T" per group = the model's own member transforms; K slaved to q2 by the lin law past the onset; the
bell crank = group dk = the model's member 9, posed by phi = |dK| / g about dR), asserted equal (params, tr, knee centre m, levels).

Reused by import, never edited: user_style_minarc.py (v5 O20 hubs + torispherical caps, the K clock spring, links 1b / 2 as
4-strip 2.5-D machined bars through the model's strap stations, O3 dowel-in-arc-slot stops, the physical knee stop),
user_style_pinknee.py (member 3 + E strap, knee link, IGLIDUR-PIN stacks with DIN 6799 clips on a 1.0 mm land, arm pad + pad
mount fused with the cut BOTTOM, upper-arm cuff, base at the J1 ring), build_roller_l1.py (fit, law, stop windows, drive geometry,
the drive skin sweep). What is new here (docs/research/roller_mechanism_redteam.md section 6, the build spec):

  link 1a    the verified K dyad is at its lower bound (bk1 26): the J1 and K O20 skirts leave ~3.6 mm for link 1a's 4.7 mm climb,
             where the gen-4 profile bar finds one station and no valid solid. Link 1a is drawn here as ONE side-view chain in
             span(u1, uK): J1 pad -> a concave bend that starts at the J1 skirt + 0.2 (the L1's R6 fault: its strap rose inside
             the base's J1 upper boss) -> a 60-deg ramp -> a convex bend onto the K pad plane -> K pad; centre-line bend radii
             2 mm (5-axis machined from solid, stated: tighter than the 15 mm bent-bar rule), swept 8 x 3 (one constant section).
  hub K      the v5 O20 stack with the 6 mm taller clock-spring cap, FLAT crown, no sensor pocket, no magnet (K is slaved, never
             read: 3 encoders J1 / J2 / J3; the two knee pins carry none); the spring is the closing spring of both rolling pairs.
  flank lug  link 1a's lateral lug at hub K: the red team's 3-arc flank section (R 6.134 / 10.403 / 13.619, its exact fit within
             3 um) re-derived here from the model's own cam synthesis on the flank_sketch_frame, extended to dK 48.25 (+2 deg
             run-out), closed by its 6 mm back offset (concentric arcs) and extruded STRAIGHT along z_c over the 3 mm lug (2-axis
             wire-EDM); its root: a web from the K pad to the lug, extruded along uK (line sketch). Fused into link 1a.
  crank      (group dk) Ti-6Al-4V, 5-axis machined from solid: boss O10 on the O3 pivot pin (2 x 683ZZ, wave-washer preloaded),
             the follower plate on the boss top, the bent arm 6 x 3 (a straight run swept on a line/arc chain at the model's
             levels + the arc concentric with hub K at r_c as a REVOLVE of its annular section), the flank roller MR63ZZ on an
             ISO 2341-B 3 x 8 headed pin (head O5 x 1.0 on the skin side); the lobe follower MR63ZZ on an O3 pin at a_s 7.0,
             psi 219 deg (the red team's real follower; the model's s_arm 4.05 one sits inside hub 2's housing).
  lobe ring  (group l2) 17-4PH H900 on link 2's upper ring turned to O18: synthesised here from the posed follower (the claim's
             law dK(q2) -> phi -> the follower centre in link 2's frame), offset by the roller radius in the plane square to the
             follower axis at mid-stroke, drawn as 3-point arcs, the onset joined by the roller's own circle into the dwell, a
             straight return flank; band F2 + 6.15..8.75 under the J2 cap skirt; keyed by an O1 dowel at the onset + 0.23 deg of
             q2 (the red team's +0.5 deg K bias, stated: drawn at the nominal phase = the loaded state).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_roller.py [--out user_roller_longdyad] [--l1 l1_roller-longdyad]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")
import user_style_minarc as USM                                                            # noqa: E402  (gen-4/4b full CAD, imported unchanged)
USP, US, BM, REPO = USM.USP, USM.US, USM.BM, USM.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_roller_l1 as RL1                                                              # noqa: E402  (gen-6 L1: the verified model's fit, law, drive geometry)
assert RL1.MIN is BM, "build_roller_l1 must patch the same build_minarc_l1 module the gen-4 CAD reads"
import numpy as np, cadquery as cq, trimesh                                                # noqa: E402
PB, SK, LV, unit, xform = US.PB, US.SK, US.LV, US.unit, US.xform
FULL = USP.FULL; at = USP.at; disc = USP.disc; prism = USP.prism; plane = USP.plane; rev = USP.rev
S = BM.S; HUB_R = US.HUB_R; T, W = US.T, US.W
GROUPS = dict(USM.GROUPS, dk=9)                                                             # + the posed bell crank (the model's member 9)
SPEC = json.load(open(os.path.join(REPO, "docs", "research", "roller_mechanism", "spec_points_bench.json")))
RES = json.load(open(os.path.join(REPO, "docs", "research", "roller_mechanism", "results_bench.json")))

# ---- link 1a (the short dyad)
L1A = dict(ramp_deg=60.0, R=2.0, clr_J1=0.2, run_K=0.2, rf=0.5)
# ---- drive dimensions (red team build spec)
ROLL_R, ROLL_W = 3.0, 2.5                    # MR63ZZ 3 x 6 x 2.5 (flank roller and lobe follower)
A_S, PSI_DEG = 7.0, 219.0                    # the real lobe follower: short arm 7.0 at psi 219 deg (red team finding 1)
LOBE_Z = (6.15, 8.75)                        # lobe ring band over hub 2's face (under the J2 cap skirt at H1 + 0.05 = 8.80)
HMID = 7.45                                  # follower mid-plane F2 + 7.45 (the red team's hmid)
DK_FLANK = 48.25                             # flank built to dK 48.25 (+2 deg run-out past dK_lim 46.25)
LUG_BACK = 6.0                               # lug depth behind the flank
BOSS_R, BOSS_H, BRG_R, BRG_W = 5.0, 6.0, 3.5, 3.0    # crank boss O10 x 6, 2 x 683ZZ (3 x 7 x 3)
PIN_R, BORE_R = 1.5, 1.6
PLATE_T = 1.5                                # follower plate (the boss top 1.5 mm, merged)
GAP = 0.35                                   # follower roller over the plate (an integral 0.35 step on the pin clears the shield)
ARM_W, ARM_T = 6.0, 3.0
HEAD_R, HEAD_T, STEP_T = 2.5, 1.0, 0.2       # ISO 2341-B 3 x 8 head O5 x 1.0, 0.2 mm step under the roller's inner ring


# ---------------------------------------------------------------------------------------------------- link 1a
def link1a_path(M):
    """the centre-line chain of link 1a in span(u1, uK) (2-D: x along u1, y across): start at the J1 seat face (J1 skirt +
    clr), concave bend R, ramp at ramp_deg, convex bend R onto the K pad plane, a short run to the K seat face; the K seat length
    is solved (>= 10.05, outside the K skirt). Returns (ex, ey, start, segs, info)"""
    Uu, C, F4, hr = BM.joints4(M); u1, uK = unit(Uu[0]), unit(Uu[1])
    ex = u1; ey = unit(uK - (uK @ ex) * ex); phi = math.acos(float(np.clip(uK @ ex, -1, 1)))
    ha, hb = F4[0] + T / 2, F4[1] + T / 2; R = L1A["R"]; Ls_a = hr[0] + L1A["clr_J1"]; a1 = L1A["run_K"]
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    start = (ha, Ls_a, math.pi / 2); best = None
    for a_deg in np.arange(L1A["ramp_deg"], 20.0, -0.5):
        a = math.radians(a_deg)
        x1, y1, p1 = SK.advance(*start, -1.0 / R, R * a); d1 = np.array([math.cos(p1), math.sin(p1)])
        x2, y2, p2 = SK.advance(0.0, 0.0, p1, 1.0 / R, R * (a + phi)); v2 = np.array([x2, y2]); d2 = np.array([math.cos(p2), math.sin(p2)])
        sol = np.linalg.solve(np.c_[d1, -back], B - np.array([x1, y1]) - v2 - a1 * d2); Lr, Ls_b = float(sol[0]), float(sol[1])
        if Lr >= 0.0 and Ls_b >= hr[1] + 0.05: best = (a, Lr, Ls_b); break
    assert best is not None, "link 1a: no ramp <= 60 deg closes the dyad"
    a, Lr, Ls_b = best
    segs = [(-1.0 / R, R * a), (0.0, Lr), (1.0 / R, R * (a + phi)), (0.0, a1)]
    end = SK.end_pose(start, segs); E = B + Ls_b * back
    assert np.allclose(end[:2], E, atol=1e-6) and abs(end[2] - (math.pi / 2 + phi)) < 1e-9, (end, E)
    return ex, ey, start, segs, dict(ramp_deg=round(math.degrees(a), 2), ramp_mm=round(Lr, 3), K_run_mm=a1, bend_R_centre_mm=R, bend_R_inner_mm=R - T / 2,
                                    seat_J1_mm=round(Ls_a, 3), seat_K_mm=round(Ls_b, 3), dyad_deg=round(math.degrees(phi), 3), sd_b=back)


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
def build_links(M, stops, lug):
    """USM.build_links' links 1b and 2 (copied: the 4-strip machined bars, pads, rings, bores, pins, slots, dowels), link 1a = link1a_body"""
    Uu, C, F4, hr = BM.joints4(M); prof = BM.link_rows(M); out = []; rep = {}; H = lambda j: C[j] + F4[j] * Uu[j]
    PL = BM.PLATE; link_gh, link_cols = USM.link_gh, USM.link_cols
    body, rep["link 1a"] = link1a_body(M, stops, lug)
    q_lo, q_hi = stops["K"]["q"]
    out.append(("l1a", f"D8-02a link 1a: 8x3 bar on ONE line/arc chain in span(u1, uK) (J1 seat at the J1 skirt + {L1A['clr_J1']:g}, "
                       f"{rep['link 1a']['ramp_deg']:.0f}-deg ramp, R{L1A['R']:g} centre-line bends: 5-axis machined from solid, tighter than the 15 mm bent-bar rule), "
                       f"J1 / K pads + integral O7 pins, K pin continued as the O5 spring arbor (0.4 mm slit, no magnet: K is slaved); K's two opposed "
                       f"{math.degrees(q_hi - q_lo):.1f}-deg stop slots in the K pad; the flank lug (3-arc flank, 2-axis wire-EDM along z_c) + its web (Ti-6Al-4V)", body))
    print(f"  link 1a: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}; {rep['link 1a']}", flush=True)
    # ---- link 1b: K upper (1) -> J2 lower (2)   (USM.build_links, copied)
    body, ex, ey, start, fit, r, Ls, rf, sd_b = link_gh(M, prof, "L1b", "link 1b", 1, 2, True, False)
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
    out.append(("l1b", f"D8-02b link 1b: 8x3 bar on a line/arc chain, K upper pad + O20 ring + M18 spigot + bore (2 dowel holes), J2 pad + integral O7 pin "
                       f"with the {math.degrees(q_hi - q_lo):.1f}-deg q2 stop slot; carries the crank pivot pin ({r['process']})", body))
    rep["link 1b"] = dict(fit, **r, pocket=npk, valid=body.isValid(), solids=len(body.Solids()))
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
    body, r = (USM.profile_link_split if USM.SPLIT else USM.profile_link)("link 2", ex, ey, start, end, Dq, Rq, axes, [hr[2], hr[3]]); fit = dict(segs=None)
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
    ring_cut = rev([(9.0, LOBE_Z[0]), (HUB_R + 0.8, LOBE_Z[0]), (HUB_R + 0.8, LV["H1"] + 0.2), (9.0, LV["H1"] + 0.2)], F[1] * unit(u[1]), unit(u[1]))
    body = body.cut(ring_cut)
    body = body.clean() if body.clean().isValid() else body
    out.append(("l2", f"D8-03 link 2: 8x3 bar on a line/arc chain + J2 / J3 O20 rings (J2 upper ring turned to O18 over F+{LOBE_Z[0]}..{LV['H1'] + 0.2:.2f} "
                      f"for the lobe ring), J2 dowel hole, flies over the knee and the pad ({r['process']})", body))
    rep["link 2"] = dict(**r, seat_mm=Ls, pad_round_mm=rf, u3_lean_out_of_plane_deg=lean, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 2: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}", flush=True)
    return out, rep
