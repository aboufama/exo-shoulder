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
PLATE_T, PLATE_DROP = 1.5, 1.5              # follower plate 1.5 mm, its top 1.5 under the boss top (its plane is square to dR, the ring's to u2)
GAP = 0.6                                    # follower roller over the plate (an integral O4 step on the follower pin clears the shield)
ARM_W, ARM_T = 6.0, 3.0
ARM_UP = 1.0                                 # the straight run's underside at the boss axis, over the boss underside
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
                            "(flank on the roller, follower on the lobe) (polished spring steel)", at(sp, C[j])))
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
    vs, fs = body.tessellate(0.05, 0.3); V = np.array([[v.x, v.y, v.z] for v in vs]); m = trimesh.Trimesh(V, np.array(fs), process=False)
    P = np.r_[V, trimesh.sample.sample_surface_even(m, 60000, seed=3)[0]]; h = P @ ax; w = P - np.outer(h, ax); rr = np.linalg.norm(w, axis=1)
    sel = (rr < r) & (h > z_lo) & (h < z_hi)
    return float(h[sel].max()) if sel.any() else None


def drive_layout(M, lg, dg, l1b_body):
    """crank stack on the BUILT link 1b: boss underside zb = max(model's, link 1b's top under the O10 footprint + 0.15) (the
    L1's stack fix: the model stacks its boss on strap samples the ramp rule lifts), boss O10 x 6 (2 x 683ZZ), the follower
    plate = the boss's top 1.5 mm, the follower MR63ZZ on it (+ GAP); the follower = the red team's a_s 7.0 / psi 219 deg moved
    along dR with the boss (the crank turns about dR: the same law; the lobe is synthesised for it)"""
    D = M.D; u2 = unit(D.u[1]); dR = unit(dg["dR"]); f2 = float(M.f[1])
    top = l1b_top_under(l1b_body, dR, BOSS_R + 0.6, dg["zboss"] - 6.0, dg["zboss"] + 12.0)
    zb = max(dg["zboss"], (top if top is not None else -1e9) + 0.15)
    s_f = zb + BOSS_H + GAP + ROLL_W / 2
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); psi = math.radians(PSI_DEG)
    v = math.cos(psi) * e1 + math.sin(psi) * e2; F0 = s_f * dR + A_S * v
    # the red team's follower at the model's stack (hmid = f2 + 7.45) for the record
    s0 = (f2 + HMID - A_S * (v @ u2)) / (dR @ u2); F0_rt = s0 * dR + A_S * v
    chk = float(np.linalg.norm(F0_rt - np.array(SPEC["follower_centre_onset"])))
    assert chk < 0.02, f"follower frame differs from the red team's: {chk}"
    return dict(zb=zb, l1b_top=top, raise_mm=zb - dg["zboss"], s_f=s_f, F0=F0, v=v, F0_redteam=F0_rt, follower_shift_mm=s_f - s0,
                follower_hmid_over_f2=float(F0 @ u2) - f2, dR=dR, u2=u2, f2=f2)


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
                key="O1 dowel key at the onset phase + 0.23 deg of q2 (red team K bias +0.5 deg; drawn at the nominal = loaded phase)")
    return ring, info, dict(e_ext=e_ext, O=O, bx=bx, by=by, Cp=Cp, q2=q2, dk=dk)


def flank_lug(M, dg):
    """link 1a's flank lug (link 1a home frame): the red team's 3 tangent arcs (results_bench flank_arcs, fit within 3 um of the
    exact flank, dK 0 -> 48.25) closed by their 6 mm back offsets (concentric arcs) and two normal end lines, in flank_sketch_frame,
    extruded straight along z_c over the 3 mm lug (h0 +- 1.5); the web to the K pad: an inner tab at the pad level (fK .. fK + 3,
    r <= 10.4 of uK) + an outer riser (r >= 10.4) up into the lug, each a line sketch extruded along uK"""
    fr = SPEC["flank_sketch_frame"]; ex, ey, ez = (np.array(fr[k], float) for k in ("ex", "ey", "ez")); h0 = float(SPEC["flank_mid_plane_h"])
    arcs = RES["flank_arcs"]; Cs = [np.array(a["centre"]) for a in arcs]; Rs = [float(a["r"]) for a in arcs]
    pts = [np.array(arcs[0]["p0"])] + [np.array(a["p1"]) for a in arcs]; mids = [np.array(a["pm"]) for a in arcs]
    off = lambda c, r, p: c + (r + LUG_BACK) * unit(p - c)
    # back chain: junctions offset along the shared normal
    back = [off(Cs[0], Rs[0], pts[0])] + [0.5 * (off(Cs[i], Rs[i], pts[i + 1]) + off(Cs[min(i + 1, 2)], Rs[min(i + 1, 2)], pts[i + 1])) if i < 2 else off(Cs[2], Rs[2], pts[3]) for i in range(3)]
    bmid = [off(Cs[i], Rs[i], mids[i]) for i in range(3)]
    pl = cq.Plane(origin=tuple(map(float, (h0 - 1.5) * ez)), xDir=tuple(map(float, ex)), normal=tuple(map(float, ez)))
    wp = cq.Workplane(pl).moveTo(*pts[0])
    for i in range(3): wp = wp.threePointArc(tuple(mids[i]), tuple(pts[i + 1]))
    wp = wp.lineTo(*back[3])
    for i in (2, 1, 0): wp = wp.threePointArc(tuple(bmid[i]), tuple(back[i]))
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
    z_lug = h0
    info = dict(arcs=[dict(r=r_, dK=a["dK"]) for r_, a in zip(Rs, arcs)], built_to_dK=DK_FLANK, extrude="straight along z_c (2-axis wire-EDM); top trimmed to the sphere r h0 + 1.5 (the model's spherical lug band; the arm runs 0.17 over it)",
                lug_band_mm=[round(h0 - 1.5, 3), round(h0 + 1.5, 3)], back_mm=LUG_BACK, web_bottom_over_fK_mm=round(hl, 3),
                lug_valid=lug.isValid(), web_valid=web.isValid())
    return [lug, web], info


def arm_arc(dg, lay):
    """the arm's arc concentric with hub K: a REVOLVE about uK of its annular section (bottom on the sphere r rA, 3 mm thick
    radially from GH, 6 wide about r_c) from the tangent point (psT) to ARM_END past the roller (beta)"""
    uK, tK0, bK0 = unit(dg["uK"]), dg["tK0"], dg["bK0"]; rc, rA, h = dg["rc"], dg["rA"], dg["h_tip"]
    a0, a1 = dg["psT"], dg["beta"] + dg["sgn_b"] * 3.0 / rc; lo, hi = min(a0, a1), max(a0, a1); span = math.degrees(hi - lo)
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


def crank_parts(M, dg, lay):
    """the bell crank (member 9 home frame = link 1b at phi 0) + its hardware; the pivot pin + clip (link 1b)"""
    dR, zb, F0, s_f = lay["dR"], lay["zb"], lay["F0"], lay["s_f"]; uK = unit(dg["uK"]); C0 = np.asarray(dg["C0"], float); cr = unit(C0)
    ztop = zb + BOSS_H
    boss = rev([(BRG_R, 0.0), (BOSS_R, 0.0), (BOSS_R, BOSS_H), (BRG_R, BOSS_H)], zb * dR, dR)
    foot = F0 - (F0 @ dR) * dR; xf = unit(foot); yf = np.cross(dR, xf)
    zpt = ztop - PLATE_DROP; plate = USP.stadium((zpt - PLATE_T) * dR, xf, yf, A_S, 2.5, PLATE_T)
    # straight run: chord from the boss (on the axis, underside ARM_UP over the boss underside) to the arc's tangent point
    T3 = uK * dg["h_tip"] + dg["rc"] * (math.cos(dg["psT"]) * dg["tK0"] + math.sin(dg["psT"]) * dg["bK0"]); B = unit(T3) * (dg["rA"] + ARM_T / 2)
    A = (zb + ARM_UP + ARM_T / 2) * dR; ex = unit(B - A); up = unit(dR - (dR @ ex) * ex); L = float(np.linalg.norm(B - A)) + 1.0
    straight = US.bar_swept(ex, up, (0.0, 0.0, 0.0), [(0.0, L)], t=ARM_T, w=ARM_W, origin=A, r=0.3)
    arc, ainfo = arm_arc(dg, lay)
    crank = US.glue(boss, plate)
    for part in (straight, arc): crank = crank.fuse(part)
    crank = crank.cut(disc(np.zeros(3), dR, BRG_R, zb - 1.0, ztop + 1.0))                     # the bearing bore O7 through boss + plate
    crank = crank.cut(disc(foot, dR, PIN_R, zpt - PLATE_T - 0.5, zpt + 0.5))                   # follower pin press hole
    z_arm_top = dg["rA"] + ARM_T - dg["R0"]
    crank = crank.cut(disc(C0, cr, PIN_R, 0.0, z_arm_top + 1.0))                                # roller pin press hole in the arm tip
    # (no clean(): OCC's same-domain unify hangs on the revolve + pipe faces of this crank)
    brg = [rev([(PIN_R, 0.0), (BRG_R, 0.0), (BRG_R, BRG_W), (PIN_R, BRG_W)], (zb + z0) * dR, dR) for z0 in (0.0, BRG_W)]
    froll = rev([(PIN_R, -ROLL_W / 2), (ROLL_R, -ROLL_W / 2), (ROLL_R, ROLL_W / 2), (PIN_R, ROLL_W / 2)], F0, dR)
    zr0 = s_f - ROLL_W / 2; zr1 = s_f + ROLL_W / 2
    fpin = rev([(0.0, zpt - PLATE_T), (PIN_R, zpt - PLATE_T), (PIN_R, zpt), (2.0, zpt), (2.0, zr0), (PIN_R, zr0), (PIN_R, zr1 + 1.2), (0.0, zr1 + 1.2)], foot, dR)
    fclip = rev([(1.15, zr1 + 0.1), (3.0, zr1 + 0.1), (3.0, zr1 + 0.7), (1.15, zr1 + 0.7)], foot, dR)
    roller = rev([(PIN_R, -ROLL_W / 2), (ROLL_R, -ROLL_W / 2), (ROLL_R, ROLL_W / 2), (PIN_R, ROLL_W / 2)], C0, cr)
    z_h = -ROLL_W / 2 - STEP_T
    rpin = rev([(0.0, z_h - HEAD_T), (HEAD_R, z_h - HEAD_T), (HEAD_R, z_h), (2.0, z_h), (2.0, -ROLL_W / 2), (PIN_R, -ROLL_W / 2), (PIN_R, z_arm_top - 0.1), (0.0, z_arm_top - 0.1)], C0, cr)
    l1b_top = lay["l1b_top"] if lay["l1b_top"] is not None else dg["lev"] + T
    ppin = rev([(0.0, l1b_top - T - 0.0), (PIN_R, l1b_top - T), (PIN_R, ztop + 1.4), (0.0, ztop + 1.4)], np.zeros(3), dR)
    pclip = rev([(1.15, ztop + 0.15), (3.0, ztop + 0.15), (3.0, ztop + 0.75), (1.15, ztop + 0.75)], np.zeros(3), dR)
    info = dict(boss_mm=[round(zb, 3), round(ztop, 3)], boss_raised_over_model_mm=round(lay["raise_mm"], 3), l1b_top_under_boss_mm=None if lay["l1b_top"] is None else round(lay["l1b_top"], 3),
                follower_centre_on_dR_mm=round(s_f, 3), follower_shift_along_dR_mm=round(lay["follower_shift_mm"], 3), follower_hmid_over_f2_mm=round(lay["follower_hmid_over_f2"], 3),
                straight_run_mm=round(L, 2), arm_root_up_mm=ARM_UP, arc=ainfo, crank_valid=crank.isValid(), crank_solids=len(crank.Solids()),
                roller_centre_r_mm=round(dg["R0"], 3), arm_bottom_over_roller_top_mm=round(dg["rA"] - dg["R0"] - ROLL_W / 2, 3))
    parts = [("dk", f"D9-01 drive bell crank (Ti-6Al-4V, 5-axis machined from solid): boss O10 x {BOSS_H:g} (2 x 683ZZ), follower plate {PLATE_T:g} mm {PLATE_DROP:g} under the boss top "
                    f"to the follower pin at {A_S:g} mm, bent arm 6 x 3 (straight run {L:.1f} mm + the arc about hub K at r_c {dg['rc']:.2f}, a revolve, "
                    f"{ainfo['span_deg']:.1f} deg), roller pin bore at the tip", crank),
             ("dk", "drive crank bearing 1 683ZZ 3x7x3 (polished)", brg[0]), ("dk", "drive crank bearing 2 683ZZ 3x7x3, 0.1 mm wave-washer preloaded (polished)", brg[1]),
             ("dk", f"drive lobe follower roller MR63ZZ 3x6x2.5 at a_s {A_S:g} mm, psi {PSI_DEG:g} deg (polished)", froll),
             ("dk", f"drive follower pin O3 h6 17-4PH H900 with an integral O4 x {GAP + PLATE_DROP:g} step, pressed in the follower plate (polished)", fpin),
             ("dk", "drive follower pin clip DIN 6799 RS 2.3 (polished)", fclip),
             ("dk", "drive flank roller MR63ZZ 3x6x2.5, radial axis (polished)", roller),
             ("dk", f"drive flank roller pin ISO 2341-B 3x8 headed, head O{2 * HEAD_R:g} x {HEAD_T:g} on the skin side, {STEP_T:g} mm step, pressed in the arm tip (polished)", rpin),
             ("l1b", "drive crank pivot pin O3 h6 17-4PH H900, pressed in link 1b (polished)", ppin),
             ("l1b", "drive crank pivot pin clip DIN 6799 RS 2.3 (polished)", pclip)]
    return parts, info


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


def posed_drive_check(dd, n=60):
    """posed exo.glb at clip frames (every len/n-th frame + the frames of largest |dK|): signed distance (mm, negative = inside) of the
    moving drive pairs"""
    import igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); C = json.load(open(os.path.join(dd, "clips.json")))
    by = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g, nm = node.split("|")[:2]; m = src.geometry[gn].copy(); m.apply_transform(T_); by[nm] = (g, m)
    def get(sub): return next(v for k, v in by.items() if k.startswith(sub))
    pairs = [("drive lobe follower roller", "D9-02"), ("drive flank roller MR63ZZ", "D8-02a"), ("drive flank roller pin", "D8-02a"), ("D9-01", "D8-02a"),
             ("D9-01", "D9-02"), ("D9-01", "D8-02b"), ("D9-01", "D8-03"), ("D9-01", "J2 cap"), ("D9-01", "K clock-spring cap"), ("drive lobe follower roller", "J2 cap"),
             ("drive follower pin clip", "D9-02"), ("drive follower pin clip", "D8-03"), ("drive flank roller MR63ZZ", "K clock-spring cap"), ("D8-02a", "D8-02b"),
             ("D8-02a", "K clock-spring cap"), ("D8-02a", "D8-01"), ("drive crank pivot pin clip", "D9-01")]
    frs = [f for c in C["clips"] for f in c["frames"]]
    pick = frs[::max(1, len(frs) // n)] + sorted(frs, key=lambda f: -abs(f.get("knuckle", {}).get("dK", 0.0)))[:12]
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
    for a_, b_ in (("drive lobe follower roller", "D9-02"), ("drive flank roller MR63ZZ", "D8-02a")):
        (ga, ma), (gb, mb) = get(a_), get(b_); XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 4000, seed=5)[0]]; ds = []
        for f in drv:
            G = lambda g: np.array(f["G"][g]).reshape(3, 3); T = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xb = ((XA @ G(ga).T + T(ga)) - T(gb)) @ G(gb)
            ds.append(float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min()))
        res[f"contact {a_} | {b_} (driven frames: min, max of the per-frame min)"] = [len(ds), round(min(ds), 3) if ds else None, round(max(ds), 3) if ds else None]
    return res


def drive_skin(dd, every=1):
    """RL1.drive_skin (copied) on this build's drive parts (D9-* + drive hardware + link 1a with its flank lug): min signed skin distance per
    part over EVERY clip frame (body_pose.posed, winding-number sign)"""
    import igl
    sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); import body_pose as BP
    C = json.load(open(os.path.join(dd, "clips.json"))); src = trimesh.load(os.path.join(dd, "exo.glb")); BF = np.ascontiguousarray(BP.F, np.int64)
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
    if "iglidur" in nl or "igubal" in nl: return "iglidur", USP.IGL
    if "bearing" in nl or "mr63zz" in nl or "683zz" in nl or "mr117" in nl: return "bearing steel", 7.8
    if "17-4ph" in nl: return "17-4PH", 7.8
    if "dowel" in nl or "iso 2341" in nl: return "hardened steel (polished)", 7.85
    if "clock spring" in nl: return "1.4310 spring steel (polished)", 7.9
    if any(k in nl for k in ("screw", "m4x6", "clip")): return "stainless (polished)", 7.9
    if "7075-T6" in n: return "7075-T6 (BOTTOM merged with the pad mount)", 2.81
    if n.startswith("UPPER ARM CUFF"): return "AlSi10Mg", 2.68
    return "Ti-6Al-4V", USP.TI


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_roller_longdyad"); ap.add_argument("--l1", default="l1_roller-longdyad")
    ap.add_argument("--skip-base-search", action="store_true"); ap.add_argument("--checks-only", action="store_true")
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
    print(f"fit (claim RLModel, BEST + ang_min {RL1.CFG['ang_min']}) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']}; hub levels "
          f"{np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f}; law {lg['law']} ({time.time() - t0:.0f} s)", flush=True)
    l1_stops = l1d["stack_mm"]["stops"]; stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1_stops[key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1_stops[key].get("pair")))
    rep = dict(fit=dict(params=dict(RL1.CFG), source=f"docs/concepts/rows/{RL1.ID}.json best_params + ang_min {RL1.CFG['ang_min']} through the claim's RLModel (= {a.l1})",
                        gap_near_touch=rep0["gap"], hub_levels_J1_K_J2_J3=[float(x) for x in F4], tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr],
                        fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"]) for k, v in stops.items()},
               j2_push_limit=USM.j2_push_limit(), law=lg["law"])
    parts = []
    hw, rep["hubs"] = hubs(M); parts += hw
    lug, rep["flank lug"] = flank_lug(M, dg)
    lk, rep["links"] = build_links(M, stops, lug)
    l1b_body = next(s for g, n, s in lk if n.startswith("D8-02b"))
    lay = drive_layout(M, lg, dg, l1b_body)
    ring, rep["lobe"], lobe_g = lobe_ring(M, lg, dg, lay)
    cp, rep["crank"] = crank_parts(M, dg, lay)
    for i, (g, n, s) in enumerate(lk):                                                         # the O3 press bore for the crank pivot pin: cut only if the bar
        if n.startswith("D8-02b"):                                                              # stays one valid solid (else the pin is drawn pressed = overlapping)
            s2 = s.cut(disc(np.zeros(3), lay["dR"], PIN_R, lay["l1b_top"] - T - 1.0, lay["l1b_top"] + 0.5))
            ok = s2.isValid() and len(s2.Solids()) == 1; rep["crank"]["pivot_bore_cut_in_link_1b"] = bool(ok)
            if ok: lk[i] = (g, n.replace("carries the crank pivot pin", "carries the crank pivot pin (O3 press bore)"), s2)
    parts += lk
    parts.append(("l2", f"D9-02 drive lobe ring: 17-4PH H900, wire-EDM (taper {rep['lobe']['e_ext_to_u2_deg']:.1f} deg along the follower axis), profile r "
                        f"{rep['lobe']['profile_r_mm'][0]:.2f} -> {rep['lobe']['profile_r_mm'][1]:.2f} mm ({rep['lobe']['arcs']} 3-point arcs), dwell r {rep['lobe']['dwell_r_mm']:.2f}, "
                        f"bore O20 on the J2 cap skirt, band F+{rep['lobe']['band_over_f2_mm'][0]:.2f}..F+{rep['lobe']['band_over_f2_mm'][1]:.2f}, keyed by an O1 dowel at the "
                        "onset + 0.23 deg (K bias)", ring))
    parts += cp
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = USP.knee_link(M)
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
    # ---- export
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")): os.remove(os.path.join(dd, "step", f))
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith(("D8-", "D9-")) and any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
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
    d = dict(l1d); d.update(id=a.out, label="roller-longdyad-knuckle-3r (verified config, ang_min 26.88), full CAD in the user's style", level="L2 user-style (full CAD of the generation-6 winner)",
                            l1_design=a.l1,
                            built_with="pipeline/conformal/param_cad/user_style_roller.py (user_style_minarc / user_style_pinknee parts: v5 O20 hubs, K plain clock-spring cap, "
                                       "link 1a as one line/arc chain (60-deg ramp, machined) + the flank lug, 4-strip machined bars 1b / 2, O3 dowel-in-arc-slot stops (K opposed pair, "
                                       "J2 single at the drive's range), member 3, knee link + knee stop + IGLIDUR-PIN stacks, BOTTOM fused with the pad mount; the drive: lobe ring, bell "
                                       f"crank on 2 x 683ZZ with the real follower, MR63ZZ flank roller on an ISO 2341-B pin) on the L1 design's frames ({a.l1})")
    d["drive_build"] = dict(kind="roller-flank (docs/research/roller_mechanism_redteam.md section 6): lobe ring (l2) -> MR63ZZ follower at a_s 7.0 / psi 219 on the bell crank "
                                 "(dk, 2 x 683ZZ on an O3 pin in link 1b) -> bent arm -> MR63ZZ roller -> 3-arc flank on link 1a's lug (l1a); one clock spring in K's cap",
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
    rep["drive_posed"] = posed_drive_check(dd); print(f"drive posed (mm, at dK): {rep['drive_posed']}", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep["check"] = check_frames(M, dd, stops)
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), all_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]), max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                   dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] for r in rep["check"]))
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"kinematics: {rep['kinematics_exact']} ({time.time() - t0:.0f} s)", flush=True)
    rep["drive_skin"] = drive_skin(dd)
    print(f"drive skin: { {k: v for k, v in rep['drive_skin'].items() if k != 'per_clip'} }", flush=True)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
