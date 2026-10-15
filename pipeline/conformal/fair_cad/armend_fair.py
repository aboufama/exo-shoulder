"""Arm end of a band design, fair pipeline (canonical humerus frame; H parts go to the arm's rest frame later).

Cuff design (ring-segment arc guide):
  - BOTTOM + neck + V-track = ONE 5-axis part: the user's bar (cut at s 265) continues without a joint line into a G2
    neck that flows into the track; the track's skin-side keel follows the dense skin envelope (all followed frames,
    2 mm clearance + margin), its V-head is a true surface of revolution about the humerus axis
  - travel stops are hidden: a slot in the track top (exact revolve) and a Ø2 stop pin pressed into the carriage from below
  - the free end closes in a smooth taper (no cap face)
  - carriage: G2 plate; wheel pins and eccentric bushings blind from below (nothing on top); JN pin integral; the JN
    screw comes up from the carriage's underside (v3.1 stack)
Hub design: BOTTOM + neck + JN hub plate as one part (same neck), skin side of the hub from the dense envelope.
"""
import math, os, sys, json
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); BC = os.path.join(HERE, "..", "band_cad")
sys.path.insert(0, HERE); sys.path.insert(0, BC)
KEY = sys.argv[1]; _argv = sys.argv; sys.argv = ["build_band_cad.py", KEY, "2"]; _c = os.getcwd(); os.chdir(BC)
import build_band_cad as BB
os.chdir(_c); sys.argv = _argv
import members as MB, hardware as HWR, envelope as EV
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
unit, V, Rot, W0, HA, E_M, TAU, ZJ4 = BB.unit, BB.V, BB.Rot, BB.W0, BB.HA, BB.E_M, BB.TAU, BB.ZJ4
def rows(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)
T_BOT, D2R = MB.T_BOT, math.pi / 180

def env_t(E, phis, ms, Z_top, margin=0.6):
    """skin side of the track: lowest t (along the section's W) per (phi, m) that keeps 2 mm + margin from the skin"""
    P = np.array([[Rot(ph) @ (Z_top * W0 + m * E_M) for m in ms] for ph in phis]); D = rows(P.reshape(-1, 3))
    r_env = E.min_radius("can", D).reshape(len(phis), len(ms)) + margin
    t = np.sqrt(np.maximum(r_env ** 2 - np.asarray(ms)[None] ** 2, 0.0))
    return np.where(r_env > 20, t, -np.inf)

def build_track_neck(E):
    rho_c = float(np.linalg.norm(np.cross(HA, W0 * ZJ4))); Z_top = ZJ4 - 0.5; tc = Z_top - BB.TRK_V
    Lt = BB.WHL_SP / 2 + BB.WHL_OD / 2 + 1.0; Lm = BB.TRK_HW + BB.WHL_RG + BB.WHL_OD / 2 + 1.0
    PHI_t = float(BB.CUFF["range"]) * D2R + Lt / rho_c; PHI_e = PHI_t + 2.0 / rho_c
    sgn = min((-1, 1), key=lambda s_: np.linalg.norm(Rot(s_ * PHI_e) @ (W0 * tc) - BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0)))
    phis = np.linspace(-sgn * PHI_e, sgn * PHI_e, max(12, int(2 * PHI_e / (1.5 * D2R)) + 1))
    ms = np.linspace(BB.WEB_HW, -BB.WEB_HW, 5)
    T = env_t(E, phis, ms, Z_top)                                                        # (phi, m) min t
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    T = np.where(np.isfinite(T), T, np.nanmin(np.where(np.isfinite(T), T, np.nan)))
    Ts = gaussian_filter1d(maximum_filter1d(T, 3, axis=0), 1.0, axis=0); Ts = np.maximum(Ts, T)
    def frame_s(phi):
        up = Rot(phi) @ W0; tan = -(Rot(phi) @ TAU)
        if sgn > 0: tan = -tan
        return Rot(phi) @ (W0 * tc), unit(np.cross(up, tan)), up, tan
    def prof_s(k, phi, scale=1.0):
        c, acr, up, tan = frame_s(phi); sg = float((Rot(phi) @ E_M) @ acr)
        tb = [min(Ts[k, j], Z_top - BB.TRK_H - 0.4) for j in range(len(ms))]
        tm = [(Z_top, -BB.WEB_HW), (Z_top, BB.WEB_HW), (tc, BB.TRK_HW), (Z_top - BB.TRK_H, BB.WEB_HW)] + [(tb[j], m) for j, m in enumerate(ms)] + [(Z_top - BB.TRK_H, -BB.WEB_HW), (tc, -BB.TRK_HW)]
        P2 = BB.norm_prof(BB.round_poly(np.array([(sg * m, t - tc) for t, m in tm]), 0.3))
        cen = P2.mean(0); return cen + (P2 - cen) * scale
    secs = []
    # free end: smooth taper over 3 mm beyond the travel end (quarter-ellipse in scale)
    ph0 = phis[0]; c0, acr0, up0, tan0 = frame_s(ph0)
    for s_ in (0.12, 0.45, 0.75, 0.93):
        d_ = 3.0 * math.sqrt(max(0.0, 1 - s_ ** 2)); P2 = prof_s(0, ph0, s_)
        secs.append(BB.sec3d(c0 - tan0 * d_, acr0, up0, P2))
    for k, phi in enumerate(phis):
        c, acr, up, tan = frame_s(phi); secs.append(BB.sec3d(c, acr, up, prof_s(k, phi)))
    c, acr, up, tan = frame_s(phis[-1])
    secs += BB.neck_sections(c, tan, up, prof_s(len(phis) - 1, phis[-1]), n=22)
    track = BB.loft(secs); print("  track+neck loft valid", track.isValid(), round(track.Volume() / 1000, 1), "cm3", flush=True)
    # hidden end stops: slot in the track top for the carriage's stop pin (offset 8 mm tangentially from the carriage centre)
    dp = 8.0 / rho_c; rng = float(BB.CUFF["range"]) * D2R; pr = 1.0 / rho_c
    slot = BB.revolve_about_HA([(Z_top - 1.2, -1.2), (Z_top - 1.2, 1.2), (Z_top + 1.5, 1.2), (Z_top + 1.5, -1.2)], -rng + dp - pr - 0.2 / rho_c, rng + dp + pr + 0.2 / rho_c)
    track = track.cut(slot); track = BB.solid_ok(track); print("  track valid", track.isValid(), flush=True)
    return track, dict(rho=rho_c, PHI_t=PHI_t, PHI_e=PHI_e, Z_top=Z_top, tc=tc, Lt=Lt, Lm=Lm, sgn=sgn, stop_dp=dp)

def build_carriage(info):
    Lt, Lm, tc = info["Lt"], info["Lm"], info["tc"]; ex, ey = TAU, E_M
    if np.cross(ex, ey) @ W0 < 0: ex = -ex
    def sdf2(x, y):
        qx, qy = np.abs(x) - (Lt - 4.0), np.abs(y) - (Lm - 4.0)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - 4.0
    carr = BB.G.flat_plate(sdf2, [0, 0, 0], ex, ey, ZJ4, ZJ4 + T_BOT, 1.2, (-Lt - 3, Lt + 3, -Lm - 3, Lm + 3))
    lv = MB.stack_levels(ZJ4, T_BOT); carr = HWR.v4_lower_features(carr, W0, lv)
    rho_w = float(np.linalg.norm(np.cross(HA, W0 * tc))); psi = (BB.WHL_SP / 2) / rho_w; parts = []
    top_blind = ZJ4 + T_BOT - 1.0                                                         # blind: 1 mm of plate stays over every pin
    for ps in (-psi, psi):
        for sm in (-1, 1):
            Wp = Rot(ps) @ W0; cw = Rot(ps) @ (W0 * tc + E_M * sm * (BB.TRK_HW + BB.WHL_RG)); ecc = sm < 0
            def rv(segs): return BB.G.revolve_profile([("line", a_, b_) for a_, b_ in zip(segs, segs[1:] + segs[:1])], Wp).moved(cq.Location(V(cw)))
            hz = (top_blind - (cw @ W0)) / max(Wp @ W0, 0.5)                                # pin length to the blind hole bottom
            parts.append(("cuff", "V-wheel Ø12 90° (PEEK, custom turned)", rv([(3.0, -2.0), (5.7, -2.0), (6.0, -1.7), (6.0, -1.5), (BB.WHL_RG, 0.0), (6.0, 1.5), (6.0, 1.7), (5.7, 2.0), (3.0, 2.0)])))
            parts.append(("cuff", "MR63ZZ bearing 3x6x2.5", rv([(1.5, -1.25), (3.0, -1.25), (3.0, 1.25), (1.5, 1.25)])))
            parts.append(("cuff", "spacer 3.1x4.8x1.25 (17-4PH)", rv([(1.55, 1.25), (2.4, 1.25), (2.4, 2.5), (1.55, 2.5)])))
            parts.append(("cuff", f"headed wheel pin Ø3 h6 (17-4PH H900), {'in an eccentric bushing' if ecc else 'pressed'}, blind from below",
                          rv([(0.0, -2.0), (2.4, -2.0), (2.4, -1.4), (1.5, -1.25), (1.5, hz - 0.3), (1.2, hz), (0.0, hz)])))
            if ecc:
                off_ = 0.4 * unit(Rot(ps) @ E_M) * sm
                bush = cq.Solid.makeCylinder(2.5, hz - 2.5, V(cw + off_ + 2.5 * Wp), V(Wp)).cut(cq.Solid.makeCylinder(1.5, hz + 1, V(cw), V(Wp)))
                parts.append(("cuff", "eccentric bushing Ø5/Ø3 x 0.4 mm (17-4PH), turned from below for preload", bush))
                carr = carr.cut(cq.Solid.makeCylinder(2.5, hz + 3.0, V(cw + off_ - 3.0 * Wp), V(Wp)))
            else: carr = carr.cut(cq.Solid.makeCylinder(1.5, hz + 3.0, V(cw - 3.0 * Wp), V(Wp)))
    # stop pin (Ø2 dowel) pressed from below, 8 mm ahead of the centre, rides in the track's slot
    dp = info["stop_dp"]; Wsp = Rot(dp) @ W0; csp = Rot(dp) @ (W0 * (ZJ4 - 1.0))
    carr = carr.cut(cq.Solid.makeCylinder(1.0, 5.0, V(csp - 0.5 * Wsp), V(Wsp)))
    parts.append(("cuff", "stop pin Ø2 x 5 dowel (A2), rides in the track slot = travel stops", cq.Solid.makeCylinder(1.0, 5.0, V(csp), V(Wsp))))
    carr = BB.solid_ok(carr); print("  carriage valid", carr.isValid(), round(carr.Volume() / 1000, 2), "cm3", flush=True)
    parts += [("cuff", n_, s_) for n_, s_ in HWR.v4_joint_parts(W0, lv, BB.N)[0]]
    return carr, parts

def bottom_merged(arm_part_can):
    """the user's BOTTOM (cut at s 265, nothing drilled) fused with the arm-end part (converted to the rest frame)"""
    from load_arm import load
    bot = [s for n, i, s in load() if n == "BOTTOM"][0]; r = BB.AE.cad_to_rest(bot, "up")
    big = cq.Workplane(cq.Plane(origin=tuple(BB.AE.CB + BB.S_CUT * BB.AE.uB), xDir=tuple(BB.AE.vB), normal=tuple(-BB.AE.uB))).rect(800, 800).extrude(800).val()
    r = r.intersect(big); a = BB.AE.can_to_rest(arm_part_can)
    m = None; vr, va = r.Volume(), a.Volume(); print(f"  merge: BOTTOM {vr / 1000:.1f} + arm part {va / 1000:.1f} cm3 (valid {r.isValid()}, {a.isValid()})", flush=True)
    for tol in ((0.0, "glue", "glue_full", 0.005, 0.02) if os.environ.get("NECK_END", "embed") == "embed" else ("glue", "glue_full", 0.0, 0.005, 0.02)):
        m = BB.CH.glue_fuse(r, a, shift=(tol == "glue")) if isinstance(tol, str) else BB.CH.fuzzy_fuse(r, a, tol=tol)
        if m is not None and m.isValid() and 0.97 * (vr + va) < m.Volume() < 1.01 * (vr + va) and len(m.Solids()) == 1: break
        print(f"  fuse {tol}: " + ("failed" if m is None else f"volume {m.Volume() / 1000:.1f} vs {(vr + va) / 1000:.1f}, valid {m.isValid()}, solids {len(m.Solids())}") + ", retry", flush=True)
    m = BB.solid_ok(m)
    if hasattr(m, "Solids") and len(m.Solids()) > 1:
        print("  WARNING merged BOTTOM has", len(m.Solids()), "solids", flush=True); os.makedirs("out_debug", exist_ok=True); r.exportBrep("out_debug/merge_bottom.brep"); a.exportBrep("out_debug/merge_arm.brep")
    print("  BOTTOM merged valid", m.isValid(), round(m.Volume() / 1000, 1), "cm3", flush=True)
    return m

def user_parts_rest():
    """the user's other arm parts (everything but BOTTOM, the old scissor shoulder and its hardware)"""
    return [(g, n, s) for g, n, s in BB.AE.user_parts() if not n.startswith("BOTTOM")]


# ================================================================ v2 arm ends (real-geometry search): dovetail arc slide, JN hub
DT_TOP, DT_H, DT_ANG = 6.0, 3.0, 60.0                                                     # dovetail half-width at the top, flank height, flank angle
LINER, LIP = 0.5, 2.5                                                                    # iglidur liner on the flanks/top, saddle lip wall
RAIL_MIN = 10.0                                                                          # rail total depth (thin_study: Ti keel >= 10)
def build_dovetail_track_neck(E):
    """curved dovetail rail (male, wider at the top) about the humerus axis; keel to the skin envelope; neck into BOTTOM"""
    rho_c = float(np.linalg.norm(np.cross(HA, W0 * ZJ4))); Z_top = ZJ4 - LINER; L_s = 13.0
    PHI_t = float(BB.CUFF["range"]) * D2R + L_s / rho_c; PHI_e = PHI_t + 2.0 / rho_c
    sgn = min((-1, 1), key=lambda s_: np.linalg.norm(Rot(s_ * PHI_e) @ (W0 * Z_top) - BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0)))
    phis = np.linspace(-sgn * PHI_e, sgn * PHI_e, max(12, int(2 * PHI_e / (1.5 * D2R)) + 1))
    m_in = DT_TOP - DT_H / math.tan(DT_ANG * D2R); ms = np.linspace(m_in, -m_in, 5)
    T = env_t(E, phis, ms, Z_top)
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    T = np.where(np.isfinite(T), T, np.nanmin(np.where(np.isfinite(T), T, np.nan)))
    Ts = np.maximum(gaussian_filter1d(maximum_filter1d(T, 3, axis=0), 1.0, axis=0), T)
    tc = Z_top - DT_H / 2
    def frame_s(phi):
        up = Rot(phi) @ W0; tan = -(Rot(phi) @ TAU)
        if sgn > 0: tan = -tan
        return Rot(phi) @ (W0 * tc), unit(np.cross(up, tan)), up, tan
    def prof_s(k, phi, scale=1.0):
        c, acr, up, tan = frame_s(phi); sg = float((Rot(phi) @ E_M) @ acr)
        tb = [min(Ts[k, j], Z_top - RAIL_MIN) for j in range(len(ms))]                    # FEA: >= 10 mm total depth (Ti)
        tm = [(Z_top, -DT_TOP), (Z_top, DT_TOP), (Z_top - DT_H, m_in)] + [(tb[j], m) for j, m in enumerate(ms)] + [(Z_top - DT_H, -m_in)]
        P2 = BB.norm_prof(BB.round_poly(np.array([(sg * m, t - tc) for t, m in tm]), 0.3)); cen = P2.mean(0); return cen + (P2 - cen) * scale
    secs = []; c0, acr0, up0, tan0 = frame_s(phis[0])
    for s_ in (0.12, 0.45, 0.75, 0.93):
        secs.append(BB.sec3d(c0 - tan0 * 3.0 * math.sqrt(max(0.0, 1 - s_ ** 2)), acr0, up0, prof_s(0, phis[0], s_)))
    for k, phi in enumerate(phis):
        c, acr, up, tan = frame_s(phi); secs.append(BB.sec3d(c, acr, up, prof_s(k, phi)))
    c, acr, up, tan = frame_s(phis[-1]); secs += hugging_neck(E, c, tan, up, prof_s(len(phis) - 1, phis[-1]), unit(c), Z_top - RAIL_MIN)
    track = BB.loft(secs); print("  dovetail track+neck loft valid", track.isValid(), flush=True)
    dp = 8.0 / rho_c; rng = float(BB.CUFF["range"]) * D2R; pr = 1.0 / rho_c
    slot = BB.revolve_about_HA([(Z_top - 1.2, -1.2), (Z_top - 1.2, 1.2), (Z_top + 1.5, 1.2), (Z_top + 1.5, -1.2)], -rng + dp - pr - 0.2 / rho_c, rng + dp + pr + 0.2 / rho_c)
    track = BB.solid_ok(track.cut(slot)); print("  track valid", track.isValid(), flush=True)
    return track, dict(rho=rho_c, PHI_t=PHI_t, PHI_e=PHI_e, Z_top=Z_top, tc=tc, m_in=m_in, sgn=sgn, stop_dp=dp)

def loft_polys(polys):
    """ThruSections through closed polygons with the same vertex count (straight edges, one lateral face per edge)"""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt
    ths = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    for P in polys:
        pg = BRepBuilderAPI_MakePolygon()
        for p in P: pg.Add(gp_Pnt(*map(float, p)))
        pg.Close(); ths.AddWire(pg.Wire())
    ths.Build(); s = cq.Shape.cast(ths.Shape())
    return s.Solids()[0] if hasattr(s, "Solids") and s.Solids() else s

def mesh_volume(s):
    """closed-tessellation volume (CAD_STANDARD rule 7: OCC Volume() is unreliable on lofted / sewn bodies)"""
    import trimesh
    vs, tr = s.tessellate(0.05, 0.2); return abs(trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=True).volume)

def self_x(s):
    """True if OCC's argument analyser finds a self-intersection (a folded loft breaks every later boolean)"""
    from OCP.BOPAlgo import BOPAlgo_ArgumentAnalyzer
    an = BOPAlgo_ArgumentAnalyzer(); an.SetShape1(s.wrapped); an.SelfInterMode = True; an.Perform(); return bool(an.HasFaulty())

KEEL_IN = 0.6                                                                            # keel half-width = flank-bottom half-width - this (transversal union)
def build_dovetail_rail_neck(E):
    """the 3R + sliding-cuff arm end, simplest robust construction (iteration CAD: keep-outs and heights, no polish):
      - rail head: ONE exact revolve about the humerus axis of the dovetail section (top 2 x DT_TOP, 60 deg flanks, DT_H)
      - keel: ThruSections through straight-edged quadrilaterals (one per 2 deg of arc), top embedded 1 mm in the head,
        half-width m_in - KEEL_IN, bottom = the dense skin envelope (all followed frames, 2 mm + margin) at every phi,
        so the rail hugs the skin (the evaluator's fitted rail_under) and never enters the envelope
      - neck: the hugging 14 x 6.5 neck as its own loft, starting inside the rail's neck end, beyond the saddle's travel
        (rail extended 32 mm past the travel end there), path = one smoothing spline (hugging_neck approach mode: aimed
        above BOTTOM's cut, down the bar's axis, ends 6 mm inside the bar - see hugging_neck), first approach run whose
        loft does not self-intersect. Known residual: the neck runs back beside the rail toward the bar and grazes the
        saddle's lip in the last ~2.5 deg of travel (<= 0.55 mm at the design limit)
      - hidden stop slot: exact revolve cut in the head's top
    every union crosses faces transversally (CAD_STANDARD rule 5)"""
    import cad_helpers as CH
    rho_c = float(np.linalg.norm(np.cross(HA, W0 * ZJ4))); Z_top = ZJ4 - LINER; L_s = max(13.0, MB.HUB_R + 0.8)
    rng = float(BB.CUFF["range"]) * D2R; PHI_t = rng + L_s / rho_c
    sgn = min((-1, 1), key=lambda s_: np.linalg.norm(Rot(s_ * PHI_t) @ (W0 * Z_top) - BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0)))
    ph_free, ph_neck = -sgn * (PHI_t + 2.0 / rho_c), sgn * (PHI_t + 32.0 / rho_c)                  # rail ends (free end / neck end: the neck leaves 16+ mm past the travel, it curves back toward the bar)
    lo_, hi_ = min(ph_free, ph_neck), max(ph_free, ph_neck)
    m_in = DT_TOP - DT_H / math.tan(DT_ANG * D2R); m_k = m_in - KEEL_IN
    head = BB.revolve_about_HA([(Z_top, -DT_TOP), (Z_top, DT_TOP), (Z_top - DT_H, m_in), (Z_top - DT_H, -m_in)], lo_, hi_)
    print(f"  rail head (exact revolve, {math.degrees(hi_ - lo_):.1f} deg at rho {rho_c:.1f}): valid {head.isValid()}, {mesh_volume(head) / 1000:.2f} cm3", flush=True)
    # keel bottom per phi: the shallowest t across its width that keeps the envelope, smoothed only upward (never into it)
    k0, k1 = lo_ + 0.5 / rho_c, hi_ - 0.5 / rho_c                                                  # keel ends 0.5 mm inside the head's end faces
    phis = np.linspace(k0, k1, max(8, int((k1 - k0) / (2.0 * D2R)) + 1)); ms = np.linspace(-m_k - 0.5, m_k + 0.5, 7)
    T = env_t(E, phis, ms, Z_top, margin=MB.MARGIN)
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    T = np.where(np.isfinite(T), T, np.nanmin(np.where(np.isfinite(T), T, np.nan)))
    tb = T.max(1); tb = np.maximum(gaussian_filter1d(maximum_filter1d(tb, 3), 1.0), tb)
    tb = np.minimum(tb, Z_top - DT_H - 1.5); t_top = Z_top - DT_H + 1.0
    depth = Z_top - tb
    print(f"  keel to the skin envelope: rail depth {depth.min():.1f}..{depth.max():.1f} mm (FEA wants >= {RAIL_MIN:.0f}; "
          f"{int(np.sum(depth < RAIL_MIN))} of {len(depth)} sections shallower because the skin is closer)", flush=True)
    polys = [[Rot(ph) @ (t_ * W0 + m_ * E_M) for t_, m_ in ((t_top, -m_k), (t_top, m_k), (tb[k], m_k), (tb[k], -m_k))] for k, ph in enumerate(phis)]
    keel = loft_polys(polys); print(f"  keel loft: valid {keel.isValid()}, self-intersecting {self_x(keel)}, {mesh_volume(keel) / 1000:.2f} cm3", flush=True)
    rail = None
    for tol in (0.0, 0.01, 0.05):
        b = CH.fuzzy_fuse(head, keel, tol=tol)
        if b.isValid() and len(b.Solids()) == 1: rail = b; break
    print(f"  head + keel: valid {rail is not None and rail.isValid()}", flush=True)
    # neck: own loft from inside the rail's neck end
    ph_n = ph_neck - sgn * 9.0 / rho_c; up0 = Rot(ph_n) @ W0                                 # the neck leaves the rail sideways, toward the bar
    eb = unit(BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0)); T0 = eb - (eb @ up0) * up0; T0 = unit(T0)
    x_len = float(os.environ.get("NECK_EXIT", 0.0))                                      # > 0: leave straight across the rail first (tried on r13 n3: clears the saddle but the bar-end bend folds)
    if x_len > 0: tau = unit(sgn * (Rot(ph_n) @ TAU)); T0 = unit(T0 - float(T0 @ tau) * tau)
    acr0 = unit(np.cross(up0, T0))
    # the neck start: inside the rail head + keel, beyond the travel
    zc_n = Z_top - 3.75                                                                  # top 0.5 under the rail top (a start below the saddle band, Z_top - 10, sits 5.5 mm under the skin envelope here)
    kd_ = float(np.interp(ph_n, phis, depth)) if phis[0] < phis[-1] else float(np.interp(ph_n, phis[::-1], depth[::-1]))
    print(f"  neck attaches {math.degrees(abs(ph_n) - PHI_t):.1f} deg past the travel end, centred {Z_top - zc_n:.2f} under the rail top; keel depth there {kd_:.1f} mm "
          f"(the neck needs {Z_top - zc_n + T_BOT / 2:.1f})", flush=True)
    P0 = Rot(ph_n) @ (W0 * zc_n); prof0 = BB.rr_prof(2 * BB.HW, T_BOT)
    for appr in (12.0, 16.0, 10.0, 14.0, 20.0, 8.0):                                       # first approach run whose loft does not fold
        secs = hugging_neck(E, P0, T0, up0, prof0, unit(P0 + x_len * T0), zc_n - T_BOT / 2, n_end_blend=0.4, approach=appr, exit_len=x_len)
        secs = [BB.sec3d(P0 - 2.0 * T0, acr0, up0, prof0), BB.sec3d(P0, acr0, up0, prof0)] + secs
        neck = BB.loft(secs); sx = self_x(neck)
        if not sx: break
    print(f"  neck loft (approach {appr:.0f} mm): valid {neck.isValid()}, self-intersecting {sx}, {mesh_volume(neck) / 1000:.2f} cm3", flush=True)
    body = None
    for tol in (0.0, 0.01, 0.05):
        b = CH.fuzzy_fuse(rail, neck, tol=tol)
        if b.isValid() and len(b.Solids()) == 1: body = b; break
    if body is None: body = BB.solid_ok(CH.fuzzy_fuse(rail, neck, tol=0.0))
    print(f"  rail + neck: valid {body.isValid()}, solids {len(body.Solids())}", flush=True)
    dp = 8.0 / rho_c; pr = 1.0 / rho_c
    slot = BB.revolve_about_HA([(Z_top - 1.2, -1.2), (Z_top - 1.2, 1.2), (Z_top + 1.5, 1.2), (Z_top + 1.5, -1.2)], -rng + dp - pr - 0.2 / rho_c, rng + dp + pr + 0.2 / rho_c)
    track = BB.solid_ok(body.cut(slot)); print(f"  rail valid {track.isValid()}, solids {len(track.Solids())}, {mesh_volume(track) / 1000:.2f} cm3", flush=True)
    return track, dict(rho=rho_c, PHI_t=PHI_t, PHI_e=max(abs(ph_free), abs(ph_neck)), Z_top=Z_top, tc=Z_top - DT_H / 2, m_in=m_in, sgn=sgn, stop_dp=dp, L_s=L_s,
                       depth=(float(depth.min()), float(depth.max())))

def build_saddle(info):
    """dovetail saddle: plate (2 L_t x 2 L_m, R8 corners; wide enough that the Ø23 v4 seat and its washer recess stay inside
    it) whose lips wrap the rail's flanks on 0.5 iglidur liners; one flank liner is a tapered gib set by 2 flush M2 set
    screws in the lip. JN pin integral, v4 stack, stop pin from below."""
    legacy = os.environ.get("RAIL_V1") == "1"                                              # the broken first version (reproduction only)
    Z_top = info["Z_top"]; L_m = max(DT_TOP + LINER + LIP, MB.HUB_R + 0.8); L_t = max(info.get("L_s", 13.0), L_m); ex, ey = TAU, E_M
    if legacy: L_t, L_m = 13.0, DT_TOP + LINER + LIP                                         # 26 x 18: the Ø18.3 washer recess broke out of its sides
    if np.cross(ex, ey) @ W0 < 0: ex = -ex
    def sdf2(x, y):
        qx, qy = np.abs(x) - (L_t - 8.0), np.abs(y) - (L_m - 8.0)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - 8.0
    sad = BB.G.flat_plate(sdf2, [0, 0, 0], ex, ey, Z_top - DT_H, ZJ4 + T_BOT, 1.2, (-L_t - 3, L_t + 3, -L_m - 3, L_m + 3))
    # the dovetail channel (+ liner) cut from below as an exact revolve over the saddle's arc: the rail's section offset by
    # the liner (0.5 normal to each flank), narrowing downward along the 60 deg flanks so the lips hook under the head
    rho_c = info["rho"]; half = (L_t + 2.0) / rho_c; m_in = info["m_in"]; tn = math.tan(DT_ANG * D2R); o = LINER / math.sin(DT_ANG * D2R)
    if legacy:                                                                             # (sign error: a 13 mm rectangular slot, no dovetail)
        ch = BB.revolve_about_HA([(Z_top - DT_H - 3.0, -(m_in + LINER) - 3.0 / tn), (Z_top - DT_H - 3.0, (m_in + LINER) + 3.0 / tn),
                                  (Z_top + LINER, DT_TOP + LINER), (Z_top + LINER, -(DT_TOP + LINER))], -half, half)
    else:
        w_top, w_bot = DT_TOP + LINER / tn + o, m_in + o - 3.0 / tn
        ch = BB.revolve_about_HA([(Z_top - DT_H - 3.0, -w_bot), (Z_top - DT_H - 3.0, w_bot), (Z_top + LINER, w_top), (Z_top + LINER, -w_top)], -half, half)
    sad = sad.cut(ch)
    lv = MB.stack_levels(ZJ4, T_BOT); sad = HWR.v4_lower_features(sad, W0, lv)
    dp = info["stop_dp"]; Wsp = Rot(dp) @ W0; csp = Rot(dp) @ (W0 * (ZJ4 - 1.0))
    sad = sad.cut(cq.Solid.makeCylinder(1.0, 5.0, V(csp - 0.5 * Wsp), V(Wsp)))
    parts = [("cuff", "stop pin Ø2 x 5 dowel (A2): rides in the rail slot = travel stops", cq.Solid.makeCylinder(1.0, 5.0, V(csp), V(Wsp)))]
    # liners: top + two flanks (iglidur J, 0.5), as thin revolved strips; the top liner has a hole for the stop pin
    for nm, prof in (("top liner (iglidur J 0.5)", [(Z_top, -DT_TOP + 0.3), (Z_top, DT_TOP - 0.3), (Z_top + LINER, DT_TOP - 0.3), (Z_top + LINER, -DT_TOP + 0.3)]),):
        lin = BB.revolve_about_HA(prof, -(L_t - 1.0) / rho_c, (L_t - 1.0) / rho_c)
        if not legacy: lin = lin.cut(cq.Solid.makeCylinder(1.15, 4.0, V(csp - 2.0 * Wsp), V(Wsp)))
        parts.append(("cuff", nm, lin))
    for s_, nm in ((1, "flank liner (iglidur J 0.5)"), (-1, "tapered gib (iglidur J, 0.5 -> 0.8): preload by 2 flush M2 set screws in the lip")):
        o = LINER / math.sin(DT_ANG * D2R)
        prof = [(Z_top - DT_H + 0.3, s_ * (m_in + 0.17)), (Z_top - 0.3, s_ * (DT_TOP - 0.17)), (Z_top - 0.3, s_ * (DT_TOP - 0.17 + o)), (Z_top - DT_H + 0.3, s_ * (m_in + 0.17 + o))]
        parts.append(("cuff", nm, BB.revolve_about_HA(prof, -(L_t - 1.0) / rho_c, (L_t - 1.0) / rho_c)))
    sad = BB.solid_ok(sad); print(f"  saddle valid {sad.isValid()}, solids {len(sad.Solids())}, {mesh_volume(sad) / 1000:.2f} cm3", flush=True)
    parts += [("cuff", n_, s_) for n_, s_ in HWR.v4_joint_parts(W0, lv, BB.N)[0]]
    return sad, parts

def build_hub_neck(E):
    """non-cuff arm end: JN hub plate (T_BOT, skin side from the dense envelope, flat seat) + neck, one loft"""
    P_bar = BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0); hub_c = W0 * ZJ4
    dh = unit((P_bar - hub_c) - ((P_bar - hub_c) @ W0) * W0); lat = unit(np.cross(W0, dh))
    # turned skin side: per ring radius the shallowest depth over the dense envelope (arm-fixed, all followed frames)
    rr = np.array([0.0, 4.0, 8.0, 11.0, 12.6]); depth = []
    for r_ in rr:
        ang = np.linspace(0, 2 * math.pi, 24, endpoint=False); P = np.array([W0 * ZJ4 + r_ * (math.cos(a_) * dh + math.sin(a_) * lat) for a_ in ang])
        env = E.min_radius("can", rows(P)) + 0.5; z = env * (rows(P) @ W0); depth.append(float(np.clip(ZJ4 - np.nanmax(z), 0.0, 12.0)))
    from scipy.interpolate import PchipInterpolator
    pc = PchipInterpolator(rr, depth)
    def dep(x, y):
        r_ = np.hypot(np.atleast_1d(x), np.atleast_1d(y)); return np.clip(pc(np.minimum(r_, rr[-1])), 0, 12) * np.clip((MB.HUB_R + 3.0 - r_) / 3.0, 0, 1)
    print("  JN hub turned skin-side depths", np.round(depth, 2), flush=True)
    xs = list(-MB.HUB_R + 0.04 + (2 * MB.HUB_R - 0.08) * (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, 19)))) + list(np.linspace(MB.HUB_R + 1.2, MB.HUB_R + 7.0, 4))
    secs = [BB.sec3d(W0 * (ZJ4 + T_BOT / 2) + x * dh, lat, W0, BB.rr_prof(2 * max(BB.CH.planform_halfwidth(x), 0.6), T_BOT, lambda y, x=x: dep(np.full(len(y), x), y))) for x in xs]
    al = math.atan((MB.HUB_R + 3.0) / 65.0); tw = unit(unit(P_bar) - (unit(P_bar) @ W0) * W0)
    secs += hugging_neck(E, W0 * (ZJ4 + T_BOT / 2) + (MB.HUB_R + 7.0) * dh, dh, W0, BB.rr_prof(2 * BB.HW, T_BOT), math.cos(al) * W0 + math.sin(al) * tw, ZJ4)
    body = BB.loft(secs); lv = MB.stack_levels(ZJ4, T_BOT)
    def nfaces(s): return len(s.Faces()) if s is not None else 0
    print("  hub+neck loft faces", nfaces(body), "valid", body.isValid(), flush=True)
    b3 = HWR.v4_lower_features(body, W0, lv); print("  after v4 features faces", nfaces(b3), b3.isValid(), flush=True)
    body = BB.solid_ok(b3)
    print("  hub+neck valid", body.isValid(), flush=True)
    return body, [("H", n_, s_) for n_, s_ in HWR.v4_joint_parts(W0, lv, BB.N)[0]]


# ---------------------------------------------------------------- turned skin side of the JN hub (a sketch, fitted to the envelope)
HUB_DEPTH_MAX = float(os.environ.get("HUB_DEPTH_MAX", 8.0))                              # the turned skin side drops at most this far below F
HUB_D1, HUB_D2 = 2.0, 1.0                                                                # G2 blend setbacks: centre flat -> cone, cone -> wall

def hub_need(E, dh, lat, F_, r0, margin=None, nth=120, dr=0.25):
    """per ring radius r (0..r0): the axial height (along W0) the hub's skin side must stay above = max over the ring and
    over every followed frame of the dense envelope (skin + 2 mm, envelope.py) + margin. -inf where no skin."""
    margin = MB.MARGIN if margin is None else margin
    rr = np.linspace(0.0, r0, int(round(r0 / dr)) + 1); th = np.linspace(0, 2 * math.pi, nth, endpoint=False)
    U = np.cos(th)[:, None] * dh[None] + np.sin(th)[:, None] * lat[None]; z = np.full((len(rr), nth), float(F_))
    for _ in range(3):                                                                    # the direction depends on the height: iterate
        P = W0[None, None] * z[..., None] + rr[:, None, None] * U[None]
        env = E.min_radius("can", rows(P.reshape(-1, 3))).reshape(z.shape) + margin
        z = np.where(env > 20, np.sqrt(np.maximum(env ** 2 - rr[:, None] ** 2, 0.0)), -np.inf)
        z = np.where(np.isfinite(z), z, F_ - 50.0)
    z = np.where(env > 20, z, -np.inf)
    return rr, z.max(1), z

def _bez_pts(cp, n=48):
    cp = np.asarray(cp, float); m = len(cp) - 1; u = np.linspace(0, 1, n)[:, None]
    return sum(math.comb(m, i) * (1 - u) ** (m - i) * u ** i * cp[i] for i in range(m + 1))

def underside_sketch(r1, al, zc, r0, d1=HUB_D1, d2=HUB_D2, F=None, d3=1.0):
    """skin side of the turned hub as a sketch in (r, z), axis -> wall: plane z = zc out to the corner K1 = (r1, zc), then
    a cone at slope al. Either the cone runs to the corner K2 on the wall r = r0 ("cone"), or - when F is given and the
    cone climbs back to the old flat face F before the rim - it meets the plane z = F at K3 and that annulus runs to the
    rim ("dimple": a flat-bottomed countersink in the old face). Corners: short G2 blends (setbacks d1, d3, d2).
    Returns (segments, polyline samples, the wall start point, family)."""
    x_, up = np.array([1.0, 0.0]), np.array([0.0, 1.0]); t_ = np.array([math.cos(al), math.sin(al)]); segs = []
    def bl(p, tp, q, tq): segs.append(("bez", [tuple(v) for v in BB.G.g2_blend(p, tp, 0.0, up, q, tq, 0.0, -tp)]))
    fam = "cone"
    if F is not None and al > 1e-6:
        r2 = r1 + (F - zc) / math.tan(al)
        if r2 + d3 + d2 + 0.3 <= r0: fam = "dimple"
    if abs(al) < 1e-9:
        K2 = np.array([r0, zc]); b_ = K2 - d2 * x_; segs.append(("line", (0.0, zc), tuple(b_))); bl(b_, x_, K2 + d2 * up, up)
    else:
        K1 = np.array([r1, zc]); p1, q1 = K1 - d1 * x_, K1 + d1 * t_
        if p1[0] > 1e-6: segs.append(("line", (0.0, zc), tuple(p1)))
        bl(p1, x_, q1, t_)
        if fam == "dimple":
            K3 = np.array([r2, F]); p3, q3 = K3 - d3 * t_, K3 + d3 * x_; K2 = np.array([r0, F])
            segs.append(("line", tuple(q1), tuple(p3))); bl(p3, t_, q3, x_); b_ = K2 - d2 * x_; segs.append(("line", tuple(q3), tuple(b_))); bl(b_, x_, K2 + d2 * up, up)
        else:
            K2 = np.array([r0, zc + (r0 - r1) * math.tan(al)]); p2 = K2 - d2 * t_; segs.append(("line", tuple(q1), tuple(p2))); bl(p2, t_, K2 + d2 * up, up)
    pts = np.concatenate([np.array([s_[1], s_[2]]) if s_[0] == "line" else _bez_pts(s_[1]) for s_ in segs])
    return segs, pts, tuple(K2 + d2 * up), fam

def fit_underside(rr, need, F_, r0, depth_max=HUB_DEPTH_MAX, d1=HUB_D1, d2=HUB_D2):
    """the closest turned skin side above the envelope: over the sketch family (centre flat + cone [+ the old face F as
    an outer annulus], G2 corner blends) pick (r1, slope, zc) minimising the ring-area-weighted gap to need(r), zc the
    lowest that clears need everywhere (bisection). Never above the old flat face F (the contour only removes stand-off),
    never deeper than depth_max below it. A cone that runs to the wall stays >= 0.4 mm under F, so the neck's flat
    underside (at F) crosses it transversally; the dimple keeps the old annulus at F (the v2 hub/neck junction)."""
    nc = np.where(np.isfinite(need), np.minimum(need, F_), -np.inf); w = np.maximum(rr, 0.125)
    floor = F_ - depth_max; nf = np.maximum(nc, floor); d3 = 1.0
    def prof(r1, al, zc, fam):
        segs, pts, ws, f_ = underside_sketch(r1, al, zc, r0, d1, d2, F=F_ if fam == "dimple" else None, d3=d3)
        o = np.argsort(pts[:, 0], kind="stable"); return np.interp(rr, pts[o, 0], pts[o, 1]), f_
    def solve(r1, al, fam):
        """lowest zc of this family that clears need (the profile rises monotonically with zc inside a family)"""
        ta = math.tan(al); span = r0 - r1
        if fam == "dimple":                                                             # the cone must regain F before the rim blend
            lo, hi = max(floor, F_ - (r0 - d3 - d2 - 0.3 - r1) * ta), F_ - 0.05
        elif abs(al) < 1e-9: lo, hi = floor, F_
        else: lo, hi = floor - min(0.0, span * ta), min(F_, F_ - 0.4 - max(0.0, span * ta))   # a cone into the wall: rim corner >= 0.4 under F
        if lo > hi: return None
        ok = lambda z: bool(np.all(prof(r1, al, z, fam)[0] >= nc - 1e-6))
        if not ok(hi): return None
        if ok(lo): zc = lo
        else:
            for _ in range(22):
                mid = 0.5 * (lo + hi); lo, hi = (lo, mid) if ok(mid) else (mid, hi)
            zc = hi
        if fam == "cone" and abs(al) < 1e-9 and zc > F_ - 0.4: zc = F_                    # never a flat face just under F (the neck's
        zb, f_ = prof(r1, al, zc, fam)                                                  # underside would graze the rim blend)
        if f_ != fam or zb.min() < floor - 1e-6: return None
        return float(np.sum((zb - nf) * w)), zc
    J0, z0 = solve(0.0, 0.0, "cone"); best = (J0, 0.0, 0.0, z0, "cone")
    for al in np.radians(np.arange(-35.0, 45.01, 1.0)):
        if abs(al) < 1e-9: continue
        r1max = r0 - d2 - d1 * math.cos(al) - 0.3
        for r1 in np.arange(d1, r1max + 1e-9, 0.25):
            for fam in (("cone", "dimple") if al > 0 else ("cone",)):
                ev = solve(r1, al, fam)
                if ev is not None and ev[0] < best[0] - 1e-9: best = (ev[0], r1, al, ev[1], fam)
    J, r1, al, zc, fam = best; segs, pts, ws, fam = underside_sketch(r1, al, zc, r0, d1, d2, F=F_ if fam == "dimple" else None, d3=d3)
    o = np.argsort(pts[:, 0], kind="stable"); zb = np.interp(rr, pts[o, 0], pts[o, 1])
    return dict(r1=r1, al=al, zc=zc, segs=segs, wall=ws, zb=zb, J=J, J_flat=J0, family=fam)

def hub_gap_report(E, dh, lat, zb_of_r, r0, tag, nth=72):
    """skin gap of the hub's skin side (radial, along each direction from GH) over every followed frame:
    min over all, and median over the skin side of the worst-frame gap / of all frames"""
    rr = np.linspace(0.0, r0 - 0.3, 24); th = np.linspace(0, 2 * math.pi, nth, endpoint=False)
    U = np.cos(th)[:, None] * dh[None] + np.sin(th)[:, None] * lat[None]
    P = (W0[None, None] * np.asarray(zb_of_r(rr))[:, None, None] + rr[:, None, None] * U[None]).reshape(-1, 3)
    sk = E.skin_radius("can", rows(P)); rad = np.linalg.norm(P, axis=1)[None]; gap = np.where(sk > 20, rad - sk, np.nan)
    worst = np.nanmin(gap, 0)
    print(f"  {tag}: skin gap min {np.nanmin(gap):.2f} mm, median (worst frame) {np.nanmedian(worst):.2f} mm, median (all frames) {np.nanmedian(gap):.2f} mm", flush=True)
    return dict(min=float(np.nanmin(gap)), median_worst=float(np.nanmedian(worst)), median_all=float(np.nanmedian(gap)))

def build_hub_neck_v2(E):
    """non-cuff arm end, built like a machined part: the JN hub is one turned revolve (exact seat plane on top, R0.8 round
    into the wall; its skin side a turned sketch - centre flat + cone + G2 blends - fitted over the dense skin envelope,
    HUB_FLAT=1 for the old flat face), the neck a constant 14 x 6.5 section swept along the skin-hugging path from inside
    the hub (embedded, so the union is a clean intersection) and tapering into BOTTOM's outline over its last part"""
    import cad_helpers as CH
    P_bar = BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0); hub_c = W0 * ZJ4
    dh = unit((P_bar - hub_c) - ((P_bar - hub_c) @ W0) * W0); lat = unit(np.cross(W0, dh))
    lv = MB.stack_levels(ZJ4, T_BOT); F_, S_ = lv["F"], lv["S"]; r0, e_ = MB.HUB_R, 0.8
    top = [("arc", (r0, S_ - e_), (r0 - e_ + e_ * math.sin(math.pi / 4), S_ - e_ + e_ * math.cos(math.pi / 4)), (r0 - e_, S_)),
           ("line", (r0 - e_, S_), (0.0, S_))]
    hub_gap_report(E, dh, lat, lambda r: np.full(len(r), F_), r0, "flat skin face (old hub)")
    if os.environ.get("HUB_FLAT") == "1":
        prof = [("line", (0.0, F_), (r0 - e_, F_)), ("arc", (r0 - e_, F_), (r0 - e_ + e_ * math.sin(math.pi / 4), F_ + e_ - e_ * math.cos(math.pi / 4)), (r0, F_ + e_)),
                ("line", (r0, F_ + e_), (r0, S_ - e_))] + top + [("line", (0.0, S_), (0.0, F_))]
    else:
        rr, need, _ = hub_need(E, dh, lat, F_, r0)
        fit = fit_underside(rr, need, F_, r0); zc = fit["zc"]
        print(f"  JN hub turned skin side: need below F by {np.round(F_ - need[::8], 2)} (r = {np.round(rr[::8], 1)})", flush=True)
        print(f"  fitted sketch ({fit['family']}): centre flat {F_ - zc:.2f} mm under F out to r {fit['r1']:.2f}, cone {math.degrees(fit['al']):+.0f} deg, "
              f"skin side under F by {np.round(F_ - fit['zb'][::8], 2)}; clears need by min {np.min(fit['zb'] - np.minimum(need, F_)):.2f}; "
              f"area-weighted stand-off over need {fit['J'] / np.sum(np.maximum(rr, 0.125)):.2f} mm (flat face {fit['J_flat'] / np.sum(np.maximum(rr, 0.125)):.2f})", flush=True)
        prof = fit["segs"] + [("line", fit["wall"], (r0, S_ - e_))] + top + [("line", (0.0, S_), (0.0, zc))]
        zb_ = fit["zb"]; hub_gap_report(E, dh, lat, lambda r: np.interp(r, rr, zb_), r0, "turned skin side (new hub)")
    hub = BB.G.revolve_profile(prof, W0, ref=dh); print("  JN hub (turned): valid", hub.isValid(), round(hub.Volume() / 1000, 2), "cm3", flush=True)
    al = math.atan((MB.HUB_R + 3.0) / 65.0); tw = unit(unit(P_bar) - (unit(P_bar) @ W0) * W0)
    P0 = W0 * (ZJ4 + T_BOT / 2) + (MB.HUB_R - 4.0) * dh; prof0 = BB.rr_prof(2 * BB.HW, T_BOT - 0.6); acr0 = unit(np.cross(W0, dh))
    sd = math.cos(al) * W0 + math.sin(al) * tw
    for appr in (0.0, 12.0, 16.0, 20.0):
        # 0: great circle + Bezier ends (r13 n4). A short neck (r16 3R: JN hub beside BOTTOM's cut, 44 mm chord, 55 deg
        # turn, hugging floor up to 9 mm over the chord) folds that path -> the rail neck's smoothing spline; first loft
        # that does not fold wins, else the last (20 mm: the widest bend, 11.8 mm on r16) and the BOTTOM merge + R7 decide
        secs = hugging_neck(E, P0, dh, W0, prof0, sd, ZJ4, n_end_blend=0.4, hold_mm=4.0 + 1.5, approach=appr)    # P0 is 4 mm inside the rim: thin until 1.5 mm outside
        secs = [BB.sec3d(P0 - 2.0 * dh, acr0, W0, prof0), BB.sec3d(P0, acr0, W0, prof0)] + secs             # starts 6 mm inside the hub
        neck = BB.loft(secs); sx = self_x(neck)
        print(f"  neck sweep (approach {appr:.0f} mm): valid {neck.isValid()}, self-intersecting {sx}" + ("  (WARNING: folded loft kept - check R7 / the merge)" if sx and appr == 20.0 else ""), flush=True)
        if neck.isValid() and not sx: break
    body = None
    for tol in (0.0, 0.01, 0.05):
        b = CH.fuzzy_fuse(hub, neck, tol=tol)
        if b.isValid() and len(b.Solids()) == 1: body = b; break
    if body is None: body = BB.solid_ok(CH.fuzzy_fuse(hub, neck, tol=0.0))
    print("  hub + neck: valid", body.isValid(), "faces", len(body.Faces()), flush=True)
    b3 = HWR.v4_lower_features(body, W0, lv); print("  after v4 features: valid", b3.isValid(), "faces", len(b3.Faces()), flush=True)
    return BB.solid_ok(b3), [("H", n_, s_) for n_, s_ in HWR.v4_joint_parts(W0, lv, BB.N)[0]]


# ================================================================ v5 neck: the evaluator's neck, built (skin-hugging)
def hugging_neck(E, P0, T0, up0, prof0, start_dir, h_start, n_end_blend=0.3, hold_mm=None, approach=0.0, exit_len=0.0):
    """sections from a part's last section (centre P0, travel T0, up0, profile prof0) to BOTTOM's cut face, along the band
    evaluator's neck: great circle from start_dir to the bar end direction; underside = dense skin envelope (all followed
    frames) + hub margin, ramped <= 35 deg out of its start height and into the bar's skin side; 14 x 6.5 G2 section"""
    from scipy.ndimage import gaussian_filter1d
    nk = json.load(open(os.path.join(HERE, "..", "gpu_client", "neck_cfg.json"))); hm = float(BB.R.get("hm", 2.0)); RAMP = math.tan(35 * D2R)
    P3 = BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0); T3 = -BB.uBc; eb = unit(P3 - approach * T3)       # approach > 0: aim above the cut, turn down into the bar
    s0 = unit(start_dir); om = math.acos(float(np.clip(s0 @ eb, -1, 1))); L = om * 80.0; n = max(8, int(L / 4.0))
    us = np.linspace(0, 1, n + 1); D = np.array([unit((math.sin((1 - u) * om) * s0 + math.sin(u * om) * eb) / max(math.sin(om), 1e-6)) for u in us])
    tg = np.gradient(D, axis=0); tg = rows(tg - (tg * D).sum(1)[:, None] * D); lat = rows(np.cross(D, tg))
    R3 = np.concatenate([rows(D + lat * w / 80.0) for w in (-5.0, 0.0, 5.0)])
    env = E.min_radius("can", R3).reshape(3, -1).max(0) + hm
    dA, dB = us * L, (1 - us) * L
    u_ = np.maximum.reduce([env, h_start - RAMP * np.maximum(0, dA - 6.0), float(nk["r_under"]) - RAMP * np.maximum(0, dB - 6.0)])
    u_ = np.maximum(gaussian_filter1d(u_, 1.2), u_)
    C = D * (u_ + T_BOT / 2)[:, None]
    # tangent-continuous ends: Bezier from the part (P0, T0) into the path and from the path into the bar (P3, T3)
    k0 = int(np.clip(np.searchsorted(dA, 14.0), 1, n - 3)); k1 = int(np.clip(np.searchsorted(dA, L - (22.0 if approach <= 0 else 0.6 * approach)), k0 + 2, n - 1))
    def bez(Pa, Ta, Pb, Tb, m, arm=1 / 3):
        Ln = np.linalg.norm(Pb - Pa); A1 = Pa + Ta * Ln * arm; B1 = Pb - Tb * Ln * arm; t = np.linspace(0, 1, m)[:, None]
        return (1 - t) ** 3 * Pa + 3 * (1 - t) ** 2 * t * A1 + 3 * (1 - t) * t ** 2 * B1 + t ** 3 * Pb
    Ta = unit(C[min(k0 + 1, n)] - C[max(k0 - 1, 0)]); Tb = unit(C[min(k1 + 1, n)] - C[max(k1 - 1, 0)])
    if approach > 0:
        # iteration CAD: one weighted smoothing spline through the start (inside the part), the skin-hugging great-circle
        # points and an approach run down the bar's axis into the cut, resampled every 2 mm; the bends come out as wide
        # as the smoothing allows (Bezier pieces here hooked / folded where the path meets the bar sideways)
        from scipy.interpolate import splprep, splev
        T0u = unit(T0); kk = np.arange(k0, k1 + 1)
        ex_ = [P0 + f_ * exit_len * T0u for f_ in (0.5, 1.0)] if exit_len > 0 else []         # straight exit run (clear of a sliding part)
        ctrl = np.vstack([P0 - 2.0 * T0u, P0, P0 + 3.0 * T0u] + ex_ + list(C[kk]) + [P3 - approach * T3, P3 - 0.5 * approach * T3, P3, P3 + 3.0 * T3, P3 + 6.0 * T3])
        wts = np.r_[[40.0, 40.0, 8.0], [30.0, 6.0][:len(ex_)], np.ones(len(kk)), [0.3, 0.6, 40.0, 40.0, 40.0]]   # pin both embedded ends, let the corner round
        dmin = None
        for sm in (2.0, 4.0, 8.0, 16.0):
            tck, _ = splprep(ctrl.T, w=wts, k=3, s=len(ctrl) * sm); dense = np.array(splev(np.linspace(0, 1, 3000), tck)).T
            i0 = int(np.argmin(np.linalg.norm(dense - P0, axis=1))); i3 = int(np.argmin(np.linalg.norm(dense - P3, axis=1))); seg = dense[i0:i3 + 1]
            arc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(seg, axis=0), axis=1))]; ns = max(8, int(arc[-1] / 2.0))
            path = np.array([np.interp(np.linspace(0, arc[-1], ns + 1), arc, seg[:, j]) for j in range(3)]).T[1:]
            t1 = np.gradient(path, axis=0); t1 /= np.linalg.norm(t1, axis=1)[:, None]; ds = np.linalg.norm(np.gradient(path, axis=0), axis=1)
            kap = np.linalg.norm(np.gradient(t1, axis=0), axis=1) / np.maximum(ds, 1e-6); rmin = 1.0 / max(kap[1:-1].max(), 1e-6)
            if rmin >= 10.0: break
        fr = np.linspace(0, 1, len(path)); rad = rows(path)
        ups = np.array([slerp_(up0, rad[k], min(1.0, f_ / 0.15)) if f_ < 0.15 else (slerp_(rad[k], BB.aBc, (f_ - 0.7) / 0.3) if f_ > 0.7 else rad[k]) for k, f_ in enumerate(fr)])
        print(f"  neck path: smoothing spline {arc[-1]:.0f} mm, min bend radius {rmin:.1f} mm at {100 * (int(np.argmax(kap[1:-1])) + 1) / len(path):.0f}% (section half-width {BB.HW:.0f}), end {np.linalg.norm(path[-1] - P3):.2f} mm from the cut centre", flush=True)
    else:
        path = np.concatenate([bez(P0, unit(T0), C[k0], Ta, 6)[1:], C[k0 + 1:k1], bez(C[k1], Tb, P3, T3, 7)])
        ups = np.concatenate([[slerp_(up0, D[k0], (j + 1) / 5) for j in range(5)], D[k0 + 1:k1], [slerp_(D[k1], BB.aBc, j / 6) for j in range(7)]])
    acr3 = unit(np.cross(BB.aBc, T3)); profB = BB.bar_prof(acr3, BB.aBc, P3); profN = BB.rr_prof(2 * BB.HW, T_BOT); secs = []
    if os.environ.get("NECK_END", "embed") == "embed":
        # morphing the 14 mm neck into the 30 mm bar section over the last few mm folds the loft (self-intersecting
        # lateral face -> every later boolean on the part fails). Instead the neck keeps its width, thins to 5.5 (0.5 inside
        # the bar's faces) and runs 6 mm into BOTTOM past the cut: the merge is a plain transversal union.
        profB = BB.rr_prof(2 * BB.HW, T_BOT - 1.0)
        path = np.concatenate([path, [P3 + 3.0 * T3, P3 + 6.0 * T3]]); ups = np.concatenate([ups, [BB.aBc, BB.aBc]])
    m = len(path); sarc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))] + np.linalg.norm(path[0] - P0)
    for k in range(m):
        w = k / (m - 1); tan = unit(path[min(k + 1, m - 1)] - path[max(k - 1, 0)]) if k < m - 1 else T3
        up = unit(ups[k] - (ups[k] @ tan) * tan); acr = unit(np.cross(up, tan))
        a0 = BB.smooth(1 - w / 0.15) if hold_mm is None else BB.smooth(1 - max(0.0, sarc[k] - hold_mm) / 6.0); a1 = BB.smooth((w - (1 - n_end_blend)) / n_end_blend)
        P2 = (1 - a1) * ((a0) * prof0 + (1 - a0) * profN) + a1 * profB
        secs.append(BB.sec3d(path[k], acr, up, P2))
    print(f"  hugging neck: {L:.0f} mm, underside {u_.min():.1f}..{u_.max():.1f} from GH (skin env + {hm:.1f})", flush=True)
    return secs
def slerp_(a_, b_, w): return BB.slerp(a_, b_, w)
