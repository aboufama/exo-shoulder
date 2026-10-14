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
    for tol in ("glue", "glue_full", 0.0, 0.005, 0.02):
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

def build_saddle(info):
    """dovetail saddle: G2 plate (26 x 18, R8 corners, inside the Ø26 footprint) whose lips wrap the rail's flanks on 0.5
    iglidur liners; one flank liner is a tapered gib set by 2 flush M2 set screws in the lip. JN pin integral, v3.1 stack,
    stop pin from below."""
    Z_top = info["Z_top"]; L_t, L_m = 13.0, DT_TOP + LINER + LIP; ex, ey = TAU, E_M
    if np.cross(ex, ey) @ W0 < 0: ex = -ex
    def sdf2(x, y):
        qx, qy = np.abs(x) - (L_t - 8.0), np.abs(y) - (L_m - 8.0)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - 8.0
    sad = BB.G.flat_plate(sdf2, [0, 0, 0], ex, ey, Z_top - DT_H, ZJ4 + T_BOT, 1.2, (-L_t - 3, L_t + 3, -L_m - 3, L_m + 3))
    # the dovetail channel (+ liner) cut from below as an exact revolve over the saddle's arc
    rho_c = info["rho"]; half = (L_t + 2.0) / rho_c; m_in = info["m_in"]
    ch = BB.revolve_about_HA([(Z_top - DT_H - 3.0, -(m_in + LINER) - 3.0 / math.tan(DT_ANG * D2R)), (Z_top - DT_H - 3.0, (m_in + LINER) + 3.0 / math.tan(DT_ANG * D2R)),
                              (Z_top + LINER, DT_TOP + LINER), (Z_top + LINER, -(DT_TOP + LINER))], -half, half)
    sad = sad.cut(ch)
    lv = MB.stack_levels(ZJ4, T_BOT); sad = HWR.v4_lower_features(sad, W0, lv)
    dp = info["stop_dp"]; Wsp = Rot(dp) @ W0; csp = Rot(dp) @ (W0 * (ZJ4 - 1.0))
    sad = sad.cut(cq.Solid.makeCylinder(1.0, 5.0, V(csp - 0.5 * Wsp), V(Wsp)))
    parts = [("cuff", "stop pin Ø2 x 5 dowel (A2): rides in the rail slot = travel stops", cq.Solid.makeCylinder(1.0, 5.0, V(csp), V(Wsp)))]
    # liners: top + two flanks (iglidur J, 0.5), as thin revolved strips
    for nm, prof in (("top liner (iglidur J 0.5)", [(Z_top, -DT_TOP + 0.3), (Z_top, DT_TOP - 0.3), (Z_top + LINER, DT_TOP - 0.3), (Z_top + LINER, -DT_TOP + 0.3)]),):
        parts.append(("cuff", nm, BB.revolve_about_HA(prof, -(L_t - 1.0) / rho_c, (L_t - 1.0) / rho_c)))
    for s_, nm in ((1, "flank liner (iglidur J 0.5)"), (-1, "tapered gib (iglidur J, 0.5 -> 0.8): preload by 2 flush M2 set screws in the lip")):
        o = LINER / math.sin(DT_ANG * D2R)
        prof = [(Z_top - DT_H + 0.3, s_ * (m_in + 0.17)), (Z_top - 0.3, s_ * (DT_TOP - 0.17)), (Z_top - 0.3, s_ * (DT_TOP - 0.17 + o)), (Z_top - DT_H + 0.3, s_ * (m_in + 0.17 + o))]
        parts.append(("cuff", nm, BB.revolve_about_HA(prof, -(L_t - 1.0) / rho_c, (L_t - 1.0) / rho_c)))
    sad = BB.solid_ok(sad); print("  saddle valid", sad.isValid(), flush=True)
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


def build_hub_neck_v2(E):
    """non-cuff arm end, built like a machined part: the JN hub is one turned revolve (exact seat plane on top, flat skin
    face, R0.8 edge rounds), the neck a constant 14 x 6.5 section swept along the skin-hugging path from inside the hub
    (embedded 4 mm, so the union is a clean intersection) and tapering into BOTTOM's outline over its last part"""
    import cad_helpers as CH
    P_bar = BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0); hub_c = W0 * ZJ4
    dh = unit((P_bar - hub_c) - ((P_bar - hub_c) @ W0) * W0); lat = unit(np.cross(W0, dh))
    lv = MB.stack_levels(ZJ4, T_BOT); F_, S_ = lv["F"], lv["S"]; r0, e_ = MB.HUB_R, 0.8
    prof = [("line", (0.0, F_), (r0 - e_, F_)), ("arc", (r0 - e_, F_), (r0 - e_ + e_ * math.sin(math.pi / 4), F_ + e_ - e_ * math.cos(math.pi / 4)), (r0, F_ + e_)),
            ("line", (r0, F_ + e_), (r0, S_ - e_)), ("arc", (r0, S_ - e_), (r0 - e_ + e_ * math.sin(math.pi / 4), S_ - e_ + e_ * math.cos(math.pi / 4)), (r0 - e_, S_)),
            ("line", (r0 - e_, S_), (0.0, S_)), ("line", (0.0, S_), (0.0, F_))]
    hub = BB.G.revolve_profile(prof, W0, ref=dh); print("  JN hub (turned): valid", hub.isValid(), round(hub.Volume() / 1000, 2), "cm3", flush=True)
    al = math.atan((MB.HUB_R + 3.0) / 65.0); tw = unit(unit(P_bar) - (unit(P_bar) @ W0) * W0)
    P0 = W0 * (ZJ4 + T_BOT / 2) + (MB.HUB_R - 4.0) * dh; prof0 = BB.rr_prof(2 * BB.HW, T_BOT); acr0 = unit(np.cross(W0, dh))
    secs = hugging_neck(E, P0, dh, W0, prof0, math.cos(al) * W0 + math.sin(al) * tw, ZJ4, n_end_blend=0.4)
    secs = [BB.sec3d(P0 - 2.0 * dh, acr0, W0, prof0), BB.sec3d(P0, acr0, W0, prof0)] + secs                 # starts 6 mm inside the hub
    neck = BB.loft(secs); print("  neck sweep: valid", neck.isValid(), flush=True)
    body = None
    for tol in (0.0, 0.01, 0.05):
        b = CH.fuzzy_fuse(hub, neck, tol=tol)
        if b.isValid() and len(b.Solids()) == 1: body = b; break
    if body is None: body = BB.solid_ok(CH.fuzzy_fuse(hub, neck, tol=0.0))
    print("  hub + neck: valid", body.isValid(), "faces", len(body.Faces()), flush=True)
    b3 = HWR.v4_lower_features(body, W0, lv); print("  after v4 features: valid", b3.isValid(), "faces", len(b3.Faces()), flush=True)
    return BB.solid_ok(b3), [("H", n_, s_) for n_, s_ in HWR.v4_joint_parts(W0, lv, BB.N)[0]]


# ================================================================ v5 neck: the evaluator's neck, built (skin-hugging)
def hugging_neck(E, P0, T0, up0, prof0, start_dir, h_start, n_end_blend=0.3):
    """sections from a part's last section (centre P0, travel T0, up0, profile prof0) to BOTTOM's cut face, along the band
    evaluator's neck: great circle from start_dir to the bar end direction; underside = dense skin envelope (all followed
    frames) + hub margin, ramped <= 35 deg out of its start height and into the bar's skin side; 14 x 6.5 G2 section"""
    from scipy.ndimage import gaussian_filter1d
    nk = json.load(open(os.path.join(HERE, "..", "gpu_client", "neck_cfg.json"))); hm = float(BB.R.get("hm", 2.0)); RAMP = math.tan(35 * D2R)
    P3 = BB.bar_pt(BB.S_CUT, BB.BAR_Y0, BB.BAR_Z0); T3 = -BB.uBc; eb = unit(P3)
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
    k0 = int(np.clip(np.searchsorted(dA, 14.0), 1, n - 3)); k1 = int(np.clip(np.searchsorted(dA, L - 22.0), k0 + 2, n - 1))
    def bez(Pa, Ta, Pb, Tb, m):
        Ln = np.linalg.norm(Pb - Pa); A1 = Pa + Ta * Ln / 3; B1 = Pb - Tb * Ln / 3; t = np.linspace(0, 1, m)[:, None]
        return (1 - t) ** 3 * Pa + 3 * (1 - t) ** 2 * t * A1 + 3 * (1 - t) * t ** 2 * B1 + t ** 3 * Pb
    Ta = unit(C[min(k0 + 1, n)] - C[max(k0 - 1, 0)]); Tb = unit(C[min(k1 + 1, n)] - C[max(k1 - 1, 0)])
    path = np.concatenate([bez(P0, unit(T0), C[k0], Ta, 6)[1:], C[k0 + 1:k1], bez(C[k1], Tb, P3, T3, 7)])
    ups = np.concatenate([[slerp_(up0, D[k0], (j + 1) / 5) for j in range(5)], D[k0 + 1:k1], [slerp_(D[k1], BB.aBc, j / 6) for j in range(7)]])
    acr3 = unit(np.cross(BB.aBc, T3)); profB = BB.bar_prof(acr3, BB.aBc, P3); profN = BB.rr_prof(2 * BB.HW, T_BOT); secs = []; m = len(path)
    for k in range(m):
        w = k / (m - 1); tan = unit(path[min(k + 1, m - 1)] - path[max(k - 1, 0)]) if k < m - 1 else T3
        up = unit(ups[k] - (ups[k] @ tan) * tan); acr = unit(np.cross(up, tan))
        a0 = BB.smooth(1 - w / 0.15); a1 = BB.smooth((w - (1 - n_end_blend)) / n_end_blend)
        P2 = (1 - a1) * ((a0) * prof0 + (1 - a0) * profN) + a1 * profB
        secs.append(BB.sec3d(path[k], acr, up, P2))
    print(f"  hugging neck: {L:.0f} mm, underside {u_.min():.1f}..{u_.max():.1f} from GH (skin env + {hm:.1f})", flush=True)
    return secs
def slerp_(a_, b_, w): return BB.slerp(a_, b_, w)
