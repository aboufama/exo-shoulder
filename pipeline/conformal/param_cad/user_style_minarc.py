"""Full user-style CAD of minarc-stop-knuckle-4r config BDp (docs/concepts/minarc-stop-knuckle-4r.md "Kit-rule re-optimisation";
verified 19.54 / score 92.89 on Bench(110,360) exact, frozen shape, margin 5, continuity applied, buildable stops priced:
docs/concepts/verify/minarc-bdp-judge.md) - the generation-4 winner.

The kinematics are EXACTLY the verified model's: the shape is the kit-rule model's own frozen fit on Bench(60,160) fast
(pipeline/concept_l1/build_minarc_l1.fit = the claim harness' "fit60", params docs/concepts/verify/minarc-kitrule/
params_floorBD5_phys_cap6.json + the judge's K stop-B fix a1max 54.748 = dK 34.47); every part is designed in its member's
home frame (= the scapula frame at rest, GH = origin) and exported in its member's group: base (0), l1a (link 1a, 1), l1b
(link 1b, 7), l2 (2), l3 (member 3, 3), l4 (knee link, 6), H (arm-fixed, 5, exported x_H = HR x). clips.json / workspace.json
are the L1 design's (l1_minarc-bdp: "G" + "T" per group = the model's own Model.T(m, i), state A and the forced state with J2
on its q2 dowel stop and K opened). The configuration is an INPUT (--params JSON | --params-file F, --a1max); the L1 named by
--l1 must have been built from the same config (asserted: params, tr, knee centre m).

What carries over from the gen-3 CAD (user_style_pinknee.py, user_pinknee_h1b - imported, unchanged): the v5 O20 hub
hardware (MR117-2RS pair, 17-4PH outer spacer, ground inner spacer, M7x0.5 Ti ring nut), the upper ring / pads / bores /
integral O7 pins, the 5-axis machined bars that HUG the verified model's strap (sketch2d.hug_chain: line / tangent-arc
chains, <= 60 deg ramps, seats inside the model's hub footprint), member 3 + E strap + E boss, the knee link, the IGLIDUR-PIN
stacks with DIN 6799 clips on a 1.0 mm land, the arm pad + pad mount + cut BOTTOM as one part, the upper-arm cuff, the base
at the J1 hub ring (no tab). What is new here:

  chain      J1 - K - J2 - J3: link 1 splits at the passive, spring-held, sensed knuckle K into link 1a (J1 lower -> K lower,
             both axes through GH) and link 1b (K upper ring -> J2 lower pad + integral pin, both axes through GH); link 2 =
             J2 upper -> J3 upper (offset line), as the gen-3 link 2.
  hub K      the v5 O20 stack (O20 only, user ruling) with a CLOCK-SPRING CAP 6 mm taller (crown F + 18.25 = the verified capK 6):
             threaded on l1b's M18 x 0.5 spigot, a spring chamber O16 x 5.2 round an O5 arbor (the integral O7 pin of link 1a
             continued as O5 above the ring nut), a 0.7 mm slot in the chamber wall for the spring's outer hook, the arbor's
             0.4 mm slit for the inner end, an O3 x 1.5 diametric magnet in the arbor tip and an O11 x 1.1 sensor pocket in
             the crown (+ 1.6 x 0.8 flex groove) for the user's magnetic angle sensor (K is sensed: the 4th encoder). The
             spring: 0.3 x 5 mm 1.4310 +C1900 strip, 145.5 mm (9 tangent half-turns, R2.75 + 0.6 per half-turn), outer hook.
             All profiles lines + tangent arcs (the gen-3 caps' spline dome is replaced by a torispherical R63.6 / R1 dome).
  stops      dowel-in-arc-slot (the verified claim's buildable stop): ISO 8734 O3 m6 hardened dowels pressed 3 mm into the
             upper boss at r 7.75, running in 3.1 mm arc slots through the lower pad (slot ends = semicircles, the dowel
             touches 0.02 mm past the stop angle). J2: one dowel, q2 -24.98 .. 100.84 deg (drawn at the 5.0-deg J1-J3
             margin). K: an OPPOSED PAIR (stop A dK 0 = the spring's rest, stop B dK 34.47): two dowels 180 deg apart make the
             stop a couple, so K's MR117 pair carries no radial stop load (the L1 red team: one dowel -> 770 N radial at the
             6 N.m jam push, s0 0.73). The O2 dowel of the build spec fails bending at that push (SF 1.09, build.json of the
             L1): O3 everywhere. Slot angles = the L1's (member-local, dowel centre = home angle + joint angle).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_minarc.py [--out user_minarc_bdp] [--l1 l1_minarc-bdp]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]                                           # user_style_pinknee / user_style read sys.argv
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")   # the hugging machined bars (h1b)
import user_style_pinknee as USP                                                          # noqa: E402  (gen-3 full-CAD parts)
US = USP.US; REPO = USP.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_minarc_l1 as BM                                                              # noqa: E402  (the verified kit-rule model's fit, frames, stops)
import numpy as np, cadquery as cq, trimesh                                               # noqa: E402
PB, SK, LV, unit, V, xform = US.PB, US.SK, US.LV, US.unit, US.V, US.xform
T, W = US.T, US.W
FULL = USP.FULL; at = USP.at; disc = USP.disc; prism = USP.prism; plane = USP.plane
S = BM.S
DOWEL_R, SLOT_RS, SLOT_W = BM.DOWEL_R, BM.SLOT_RS, BM.DOWEL_R + BM.SLOT_CLR             # O3 dowel, r 7.75, slot half width 1.55
END_CLR = BM.END_CLR                                                                      # the dowel touches 0.02 mm past the stop angle
DOWEL_Z = BM.DOWEL_Z                                                                      # F+0.5 .. F+6.15 (3 mm pressed into the upper boss)
CAPK = dict(ch_z0=11.35, ch_z1=16.55, ch_r=8.0, arbor_r=2.5, arbor_top=16.35, pocket_r=5.5, pocket_z=17.15, mag_r=1.525, mag_h=1.6,
            slit_w=0.4, hook_slot=(7.8, 9.3, 0.8), groove=(1.6, 0.8))
SPRING = dict(t=0.3, w=5.0, r0=2.75, d=0.6, n=9, hook_r=0.5, hook_l=0.9)
GROUPS = {"base": 0, "l1a": 1, "l1b": 7, "l2": 2, "l3": 3, "l4": 6, "H": 5}
USP.HUG_N.update({"link 1a": (5,), "link 1b": (5,)})


# ---------------------------------------------------------------------------------------------------- caps (lines + tangent arcs)
def _ts_dome(r_wall, z_wall, z_crown, rk=1.0):
    """torispherical dome: knuckle arc rk tangent to the wall r_wall at z_wall, crown arc centred on the axis through
    (0, z_crown), tangent to the knuckle (replaces the gen-3 caps' spline). (knuckle mid, tangent pt, crown mid, Rc)"""
    a = z_crown - z_wall; xk = r_wall - rk
    Rc = (xk ** 2 + a ** 2 - rk ** 2) / (2 * a - 2 * rk)
    kc = np.array([xk, z_wall]); cc = np.array([0.0, z_crown - Rc]); tp = kc + rk * unit(kc - cc)
    a1 = math.atan2(tp[1] - kc[1], tp[0] - kc[0]); km = kc + rk * np.array([math.cos(a1 / 2), math.sin(a1 / 2)])
    b0 = math.atan2(tp[1] - cc[1], tp[0] - cc[0]); bm = 0.5 * (b0 + math.pi / 2); cm = cc + Rc * np.array([math.cos(bm), math.sin(bm)])
    return tuple(km), tuple(tp), tuple(cm), Rc


def cap_v5(k, F):
    """the v5 threaded O20 cap (skirt over the boss from H1 + 0.05, flange face at U1 on the upper bearing's outer ring) with a
    torispherical dome of tangent arcs to the crown at F + 12.25"""
    z0, z1, zt = LV["H1"] + 0.05 + F, LV["U1"] + F, LV["top"] + F; R = US.HUB_R
    if CAP_STYLE == "flat":                                                                # the O20 x 12.25 envelope the model / L1 carry: wall to the
        r = 0.5; q = 1 - math.sqrt(0.5)                                                    # crown, R0.5 crown corner, flat crown
        wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(R, z0).lineTo(R, zt - r).threePointArc((R - r * q, zt - r * q), (R - r, zt)).lineTo(0.0, zt)
              .lineTo(0.0, zt - 0.5).lineTo(4.5, zt - 0.5).lineTo(4.5, z1).lineTo(9.0, z1).close())
        return xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k)), None
    km, tp, cm, Rc = _ts_dome(R, z1 + 0.35, zt)
    wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(R, z0).lineTo(R, z1 + 0.35).threePointArc(km, tp).threePointArc(cm, (0.0, zt))
          .lineTo(0.0, zt - 0.5).lineTo(4.5, zt - 0.5).lineTo(4.5, z1).lineTo(9.0, z1).close())
    return xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k)), Rc


def frame2(k):
    e, f = S.frame_of(unit(k)); f = np.cross(unit(k), e); return e, f


def cap_k(k, F, crown):
    """hub K's clock-spring cap: the v5 skirt / flange, the wall to F + crown - 0.5, an R0.5 crown corner, the crown with the
    O11 x 1.1 sensor pocket; inside: the spring chamber O16 (ch_z0 .. ch_z1) round the arbor, bored O9 through the flange
    (clears the ring nut), the outer-hook slot in the chamber wall and the sensor flex groove. Lines + tangent arcs, revolved."""
    c = CAPK; R = US.HUB_R; z0, z1, zc = LV["H1"] + 0.05 + F, LV["U1"] + F, crown + F; q = 1 - math.sqrt(0.5); r = 0.5
    wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(R, z0).lineTo(R, zc - r).threePointArc((R - r * q, zc - r * q), (R - r, zc))
          .lineTo(c["pocket_r"], zc).lineTo(c["pocket_r"], c["pocket_z"] + F).lineTo(0.0, c["pocket_z"] + F).lineTo(0.0, c["ch_z1"] + F)
          .lineTo(c["ch_r"], c["ch_z1"] + F).lineTo(c["ch_r"], c["ch_z0"] + F).lineTo(4.5, c["ch_z0"] + F).lineTo(4.5, z1).lineTo(9.0, z1).close())
    cap = xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k))
    e, f = frame2(k); k = unit(k)
    r0, r1, w = c["hook_slot"]                                                             # outer-hook slot at -e (the spring ends there)
    cap = cap.cut(prism(F * k + c["ch_z0"] * k, e, f, [(-r1, -w - 0.1), (-r0, -w - 0.1), (-r0, -0.1), (-r1, -0.1)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"]))
    gw, gd = c["groove"]                                                                   # sensor flex groove, pocket -> rim, toward +f
    cap = cap.cut(prism((zc - gd) * k, f, -e, [(c["pocket_r"] - 0.5, -gw / 2), (R + 1.0, -gw / 2), (R + 1.0, gw / 2), (c["pocket_r"] - 0.5, gw / 2)], [0, 0, 0, 0], gd + 1.0))
    return cap.clean() if cap.clean().isValid() else cap


def arbor_pin(k, F):
    """link 1a's K pin: the v5 collar O8.2 + integral O7 pin (lower_pin) continued as an O5 arbor to F + arbor_top, with a 0.4 mm
    chordal slit for the spring's inner end (at +e, where the spring starts) and an O3.05 x 1.6 magnet pocket in the tip"""
    c = CAPK; k = unit(k)
    pin = PB.revolved([(0, 1.5), (4.1, 1.5), (4.1, LV["L1"]), (3.5, LV["L1"]), (3.5, LV["N1"]), (c["arbor_r"], LV["N1"]), (c["arbor_r"], c["arbor_top"]),
                       (0, c["arbor_top"])], k, F)
    e, f = frame2(k); sw = c["slit_w"] / 2
    pin = pin.cut(prism((F + c["ch_z0"] + 0.05) * k, e, f, [(1.3, -sw), (c["arbor_r"] + 0.5, -sw), (c["arbor_r"] + 0.5, sw), (1.3, sw)], [0, 0, 0, 0], c["ch_z1"] - c["ch_z0"] - 0.3))
    pin = pin.cut(disc(np.zeros(3), k, c["mag_r"], F + c["arbor_top"] - c["mag_h"], F + c["arbor_top"] + 1.0))
    return pin


def magnet(k, F):
    c = CAPK; return disc(np.zeros(3), unit(k), c["mag_r"] - 0.025, F + c["arbor_top"] - c["mag_h"] + 0.1, F + c["arbor_top"] - 0.1)


def clock_spring(k, F):
    """the clock spring's free shape: 0.3 x 5 strip swept on 9 tangent half-turns (R r0 + i d about two centres d apart:
    a two-centre spiral of lines + tangent arcs), then an R0.5 hook bend and a 0.9 mm tab into the cap's wall slot"""
    s = SPRING; k = unit(k); e, f = frame2(k)
    segs = [(1.0 / (s["r0"] + i * s["d"]), math.pi * (s["r0"] + i * s["d"])) for i in range(s["n"])]
    L = sum(l for _, l in segs)
    segs += [(-1.0 / s["hook_r"], 0.5 * math.pi * s["hook_r"]), (0.0, s["hook_l"])]
    zm = F + CAPK["ch_z0"] + 0.1 + s["w"] / 2
    sp = US.bar_swept(e, f, (s["r0"], 0.0, math.pi / 2), segs, t=s["t"], w=s["w"], origin=zm * k, r=0.1)
    return sp, L


# ---------------------------------------------------------------------------------------------------- stops
def arc_slot_cutter(cen, k, a_lo, a_hi, z0, z1, rs=SLOT_RS, w=SLOT_W):
    """arc slot of half width w at radius rs from the dowel-centre stop angle a_lo to a_hi (rad, frame2(k)): two concentric arcs
    + two semicircular ends whose centres sit (w - DOWEL_R + END_CLR) / rs beyond the stop angles (the O3 dowel touches the end
    0.02 mm past the stop); extruded z0 .. z1 along k from cen"""
    k = unit(k); e, f = frame2(k); dl = (w - DOWEL_R + END_CLR) / rs; lo, hi = a_lo - dl, a_hi + dl
    P = lambda r, a: (r * math.cos(a), r * math.sin(a)); ro, ri = rs + w, rs - w; mid = 0.5 * (lo + hi)
    c_hi, c_lo = np.array(P(rs, hi)), np.array(P(rs, lo)); t_hi = np.array([-math.sin(hi), math.cos(hi)]); t_lo = np.array([-math.sin(lo), math.cos(lo)])
    wp = (cq.Workplane(plane(np.asarray(cen) + z0 * k, e, f)).moveTo(*P(ro, lo)).threePointArc(P(ro, mid), P(ro, hi))
          .threePointArc(tuple(c_hi + w * t_hi), P(ri, hi)).threePointArc(P(ri, mid), P(ri, lo)).threePointArc(tuple(c_lo - w * t_lo), P(ro, lo)).close())
    return wp.extrude(z1 - z0).val()


def dowel_at(cen, k, th, F):
    k = unit(k); e, f = frame2(k); pd = np.asarray(cen) + SLOT_RS * (math.cos(th) * e + math.sin(th) * f)
    z0, z1 = DOWEL_Z                                                                       # pd sits on the joint face F: z from there
    dw = USP.rev([(0, z0), (DOWEL_R - 0.2, z0), (DOWEL_R, z0 + 0.2), (DOWEL_R, z1 - 0.2), (DOWEL_R - 0.2, z1), (0, z1)], pd, k)   # ISO 8734 chamfered ends
    hole = disc(pd, k, DOWEL_R, LV["U0"] - 0.3, z1 + 0.5)                                   # press hole in the upper boss (blind, 0.5 relief)
    return dw, hole


def stop_layout(M, l1_stops):
    """the stop angles (the model's: build_minarc_l1.stop_specs) and the L1's dowel home angles (member-local); K gets the
    opposed second dowel at home + 180"""
    sp = BM.stop_specs(M); out = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = sp[key]; th = math.radians(l1_stops[key]["dowel_home_angle_deg"])
        homes = [th] + ([th + math.pi] if key == "K" else [])
        out[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes)
    return out


# ---------------------------------------------------------------------------------------------------- links
def link_cols(M, lk, rows):
    """the L1 strap underside (build_minarc_l1.link_solid's columns: the model's finalize rows + the hub-rim / footprint lift)"""
    Uu, C, F4, hr = BM.joints4(M); LVL = BM.LVL
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r.copy() for _, _, r in rows]
    d_lo = unit(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
    cols_d = [d_lo] + dvs + [d_hi]; cols_r = [rs[0].copy()] + [r.copy() for r in rs] + [rs[-1].copy()]
    for kk, j in ((lk["ka"], j0), (lk["kb"], j1)):
        if j == (idx[0] if kk == lk["ka"] else idx[-1]): continue
        cen = C[kk] + F4[kk] * Uu[kk]
        for q in range(len(cols_d)):
            den = float(cols_d[q][j] @ Uu[kk])
            if den > 0.2: cols_r[q][j] = max(cols_r[q][j], (cen @ Uu[kk] + LVL[(lk["name"], kk)]) / den + 0.02)
    for kk in (lk["ka"], lk["kb"]):
        cen = C[kk] + F4[kk] * Uu[kk]; lv = LVL[(lk["name"], kk)] + 0.2
        for q in range(len(cols_d)):
            Pq = cols_d[q] * cols_r[q][:, None]; w = Pq - C[kk]
            off = np.linalg.norm(w - (w @ Uu[kk])[:, None] * Uu[kk], axis=1); den = cols_d[q] @ Uu[kk]
            sel = (off < hr[kk] + 2.5) & (den > 0.2)
            cols_r[q][sel] = np.maximum(cols_r[q][sel], (cen @ Uu[kk] + lv) / den[sel])
    J = np.arange(j0, j1 + 1)
    return np.array([cd[J] for cd in cols_d]), np.array([cr[J] for cr in cols_r])


LINK_MODE = os.environ.get("MINARC_LINK_MODE", "profile")                                 # profile (default) | hug (user_pinknee_h1b's chains)
R_CONVEX, R_REFLEX, MARGIN, CLIMB_MAX = 2.0, 0.5, 0.1, 59.5


def profile_link(label, ex, ey, start, end, Dq, Rq, axes, hr2, t=T, w=W, side=0):
    """the link as ONE side-view sketch in the bar plane (lines + tangent arcs), extruded w across it: a 2.5-D part (3+2-axis
    machined / wire-EDM from a Ti-6Al-4V plate) whose underside runs THROUGH the verified model's strap stations (the L1 strap
    underside, max over the strap's columns, in the bar plane: polar angle / radius), MARGIN mm above them outside the hub
    footprints and at the lifted hub level inside; the top is the underside offset by t along its normals (miter), so the
    section is the model's 3 mm strap. Vertices are rounded with tangent arcs: R_CONVEX where the material corner is convex
    (the round moves metal away from the skin), R_REFLEX (0.5 mm: dips <= 0.08 mm at a 60-deg turn, inside MARGIN) where it is
    reflex; the two end faces (glued to the pads' end faces) stay sharp. Returns (solid, report)."""
    th_q = np.arctan2(Dq @ ey, Dq @ ex); rho_q = Rq * np.hypot(Dq @ ex, Dq @ ey)
    th = th_q.mean(0); order = np.argsort(th); th = th[order]; need = rho_q.max(0)[order]
    def offs(U): return [np.abs((U - np.asarray(p_)[None]) @ np.array([-d_[1], d_[0]])) for p_, d_ in axes]
    foot = lambda U: np.any([o_ < r_ + 2.5 for o_, r_ in zip(offs(U), hr2)], axis=0)
    a_ax, b_ax = np.array(axes[0][1], float), np.array(axes[1][1], float)
    S_c = np.array(start[:2], float); E_c = np.array(end[:2], float)
    S_u = S_c - 0.5 * t * a_ax; E_u = E_c - 0.5 * t * b_ax                                  # undersides at the seat ends (skin side = toward GH)
    a0, a1 = math.atan2(S_u[1], S_u[0]), math.atan2(E_u[1], E_u[0])
    P = np.stack([need * np.cos(th), need * np.sin(th)], 1); fo = foot(P)
    sel = (th > a0 + math.radians(0.6)) & (th < a1 - math.radians(0.6))
    st = [(need[j] + (0.0 if fo[j] else MARGIN)) * np.array([math.cos(th[j]), math.sin(th[j])]) for j in np.nonzero(sel)[0]]
    under = [S_u] + st + [E_u]
    # drop stations the pads already cover (a station below the straight line from a seat end into the next point is kept;
    # a station within 0.3 mm of its neighbour is merged)
    U2 = [under[0]]
    for p_ in under[1:]:
        if np.linalg.norm(p_ - U2[-1]) > 0.3: U2.append(p_)
    under = U2; n = len(under)
    # the user's ramp ruling (<= 60 deg near a hub): where the model's strap steps steeper (link 2's drop after J2's lifted
    # footprint: 68 deg), the LOWER end of the segment is raised (never lowered: the underside stays >= the strap) until the
    # segment climbs <= CLIMB_MAX against the local tangential direction about GH; the pad ends stay fixed
    tanc = math.tan(math.radians(CLIMB_MAX)); raised = []
    pol = [[float(np.hypot(*p_)), math.atan2(p_[1], p_[0])] for p_ in under]
    for _ in range(4 * n):
        hit = False
        for i in range(n - 1):
            (ra, ta), (rb, tb) = pol[i], pol[i + 1]; ds = 0.5 * (ra + rb) * abs(tb - ta); lim = tanc * ds
            if abs(rb - ra) <= lim + 1e-6: continue
            lo = i if ra < rb else i + 1
            if lo in (0, n - 1): continue                                                  # a pad end: cannot move (reported as max_climb)
            pol[lo][0] = max(ra, rb) - lim; hit = True; raised.append(lo)
        if not hit: break
    under = [np.array([r_ * math.cos(a_), r_ * math.sin(a_)]) for r_, a_ in pol]
    d = [unit(under[i + 1] - under[i]) for i in range(n - 1)]; nrm = [np.array([v[1], -v[0]]) for v in d]
    top = [under[0] + t * nrm[0]]
    for i in range(1, n - 1):
        n1, n2 = nrm[i - 1], nrm[i]; top.append(under[i] + t * (n1 + n2) / (1.0 + float(n1 @ n2)))
    top.append(under[-1] + t * nrm[-1])
    # the seat-end faces must be the pads' end faces: start / end tops on the pad top (the axis direction)
    top[0] = S_u + t * a_ax; top[-1] = E_u + t * b_ax
    # remove top vertices whose offset segment runs backwards (tight concave runs)
    changed = True
    while changed and len(top) > 2:
        changed = False
        for i in range(1, len(top) - 1):
            if float((top[i] - top[i - 1]) @ (top[i + 1] - top[i])) < 0: del top[i]; changed = True; break
    pts = [tuple(p_) for p_ in under] + [tuple(p_) for p_ in reversed(top)]
    Pp = np.array(pts); area = 0.5 * float(np.sum(Pp[:, 0] * np.roll(Pp[:, 1], -1) - np.roll(Pp[:, 0], -1) * Pp[:, 1]))
    want = []
    for i in range(len(pts)):
        a_, b_, c_ = Pp[i - 1], Pp[i], Pp[(i + 1) % len(pts)]; cr = float(np.cross(b_ - a_, c_ - b_))
        convex = (cr < 0) if area < 0 else (cr > 0)
        want.append(R_CONVEX if (convex or i >= n) else R_REFLEX)
    rad = USP.safe_radii(pts, want)
    for i in (0, n - 1, n, len(pts) - 1): rad[i] = 0.0                                     # the four end-face corners stay sharp
    nP = unit(np.cross(ex, ey))
    sol = USP.prism(np.zeros(3), ex, ey, pts, rad, w, both=True) if not side else USP.prism((-w if side < 0 else 0.0) * nP, ex, ey, pts, rad, w)
    def in_end(e_):
        q = np.array(e_.positionAt(0.5).toTuple()); x, y = q @ ex, q @ ey
        if side and abs(q @ nP) < 1e-3: return True                                        # the centre plane (the other half is glued there)
        for (Pu, ax_) in ((S_u, a_ax), (E_u, b_ax)):
            sd = np.array([ax_[1], -ax_[0]])                                               # along the pad (perpendicular to the axis in the plane)
            if abs((np.array([x, y]) - Pu) @ sd) < 1e-3: return True
        return False
    try:
        r_ = US.rounded(sol, skip=in_end)
        if r_.isValid() and len(r_.Solids()) == 1: sol = r_; rounded = True
        else: rounded = False
    except Exception: rounded = False
    # report: underside vs the L1 strap (in-plane polar), climb
    seg = [(Pp[i], Pp[i + 1]) for i in range(n - 1)]
    climb = max(abs(math.degrees(math.atan2(float((b_ - a_) @ unit(0.5 * (a_ + b_))), float((b_ - a_) @ np.array([-unit(0.5 * (a_ + b_))[1], unit(0.5 * (a_ + b_))[0]]))))) for a_, b_ in seg)
    Us = np.concatenate([np.linspace(a_, b_, 12, endpoint=False) for a_, b_ in seg] + [Pp[n - 1:n]])
    cl = np.hypot(Us[:, 0], Us[:, 1]) - np.interp(np.arctan2(Us[:, 1], Us[:, 0]), th, need); out_ = ~foot(Us)
    rep = dict(stations=int(len(st)), vertices=len(pts), radii=[r for r in rad if r > 0], rounded_edges=rounded, max_climb=round(climb, 2),
               stations_raised_for_the_60deg_ramp=sorted(set(raised)),
               over_L1_min=float(cl.min()), over_L1_mean=float(cl.mean()), over_L1_max=float(cl.max()),
               over_L1_max_outside_footprints=float(cl[out_].max()) if out_.any() else None,
               process="machined from solid Ti-6Al-4V (2.5-D: ONE side-view sketch of lines + tangent arcs through the model's strap stations, "
                       f"extruded {w:g} mm; 3+2-axis or wire EDM), rounds R{R_CONVEX:g} / R{R_REFLEX:g} in the profile")
    print(f"{label} (side-view profile): {len(st)} stations, {len(pts)} vertices, underside over the L1 strap min {cl.min():.2f} mean {cl.mean():.2f} "
          f"max {cl.max():.2f} mm (outside the footprints {rep['over_L1_max_outside_footprints']}), max climb {climb:.1f} deg, edges rounded {rounded}, "
          f"valid {sol.isValid()}", flush=True)
    return sol, rep


SPLIT = os.environ.get("MINARC_SPLIT", "1") == "1"
CAP_STYLE = os.environ.get("MINARC_CAP", "dome")                                        # dome (torispherical) | flat (the O20 x 12.25 envelope)


def profile_link_split(label, ex, ey, start, end, Dq, Rq, axes, hr2, t=T, w=W):
    """the strap is tilted across its width (one edge of a flat bar 1.7-1.9 mm above it on links 1b / 2): the bar as TWO
    half-width (4 mm) side-view profiles, each through the strap stations of ITS half (max over that half's rows), extruded
    from the bar plane to either side and glued on it - a bar whose underside steps once along its centre line (two
    extrudes; 3-axis machinable). Falls back to the one-profile bar if the halves do not glue into one valid solid."""
    nP = unit(np.cross(ex, ey)); off = np.einsum("qjk,k->qj", Dq, nP).mean(1)
    lo, hi = off <= 1e-6, off >= -1e-6
    if lo.sum() < 2 or hi.sum() < 2: return profile_link(label, ex, ey, start, end, Dq, Rq, axes, hr2, t, w)
    a, ra = profile_link(label + " (half -)", ex, ey, start, end, Dq[lo], Rq[lo], axes, hr2, t, w / 2, side=-1)
    b, rb = profile_link(label + " (half +)", ex, ey, start, end, Dq[hi], Rq[hi], axes, hr2, t, w / 2, side=+1)
    try: sol = US.glue(a, b)
    except Exception as e_: sol = None; print(f"  {label}: halves do not glue ({e_}) - one profile", flush=True)
    if sol is None or not sol.isValid() or len(sol.Solids()) != 1: return profile_link(label, ex, ey, start, end, Dq, Rq, axes, hr2, t, w)
    rep = dict(split="two half-width profiles glued on the bar plane", half_minus=ra, half_plus=rb,
               over_L1_max_outside_footprints=max(ra["over_L1_max_outside_footprints"] or 0, rb["over_L1_max_outside_footprints"] or 0),
               max_climb=max(ra["max_climb"], rb["max_climb"]), process=ra["process"].replace("ONE side-view sketch", "TWO half-width side-view sketches"))
    print(f"{label}: split bar glued, valid {sol.isValid()}, solids {len(sol.Solids())}", flush=True)
    return sol, rep


def link_gh(M, prof, nm, label, ka, kb, up_a, up_b):
    """a hugging machined bar between two joints whose axes pass through GH (links 1a, 1b): plane span(U_a, U_b); seats at the
    member level (lower pad 0 / upper pad U0) of each joint; returns (body, ex, ey, start, fit, report, Ls, rf, he)"""
    Uu, C, F4, hr = BM.joints4(M)
    ex = unit(Uu[ka]); ey = unit(Uu[kb] - (Uu[kb] @ ex) * ex); phi = math.acos(np.clip(unit(Uu[kb]) @ ex, -1, 1))
    ha = F4[ka] + (LV["U0"] if up_a else 0.0) + T / 2; hb = F4[kb] + (LV["U0"] if up_b else 0.0) + T / 2
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    Ls, rf = USP.HUG_SEAT, USP.HUG_RF
    start = (ha, Ls, math.pi / 2); end = (*(B + Ls * back), math.pi / 2 + phi)
    Dq, Rq = link_cols(M, *prof[nm]); axes = [((0.0, 0.0), (1.0, 0.0)), ((0.0, 0.0), (math.cos(phi), math.sin(phi)))]
    sd_b = -(math.cos(math.pi / 2 + phi) * ex + math.sin(math.pi / 2 + phi) * ey)
    if LINK_MODE == "profile":
        body, rep = (profile_link_split if SPLIT else profile_link)(label, ex, ey, start, end, Dq, Rq, axes, [hr[ka], hr[kb]]); fit = dict(segs=None)
        rep.update(arc_deg=round(math.degrees(phi), 2), seat_mm=Ls, pad_round_mm=rf)
        return body, ex, ey, start, fit, rep, Ls, rf, sd_b
    fit, rep = USP.hug_fit(label, ex, ey, start, end, Dq, Rq, axes, [hr[ka], hr[kb]])
    body = US.bar_swept(ex, ey, start, fit["segs"])
    he = SK.end_pose(start, fit["segs"])[2]; sd_b = -(math.cos(he) * ex + math.sin(he) * ey)
    rep.update(arc_deg=round(math.degrees(phi), 2), seat_mm=Ls, pad_round_mm=rf)
    return body, ex, ey, start, fit, rep, Ls, rf, sd_b


def build_links(M, stops):
    """links 1a, 1b, 2 with their pads, rings, bores, pins, stop slots and dowel holes; the dowels and the K spring parts"""
    Uu, C, F4, hr = BM.joints4(M); prof = BM.link_rows(M); out = []; rep = {}; H = lambda j: C[j] + F4[j] * Uu[j]
    PL = BM.PLATE
    # ---- link 1a: J1 lower (0) -> K lower (1)
    body, ex, ey, start, fit, r, Ls, rf, sd_b = link_gh(M, prof, "L1a", "link 1a", 0, 1, False, False)
    body = US.glue(USP.plate_R(Uu[0], F4[0], ey, W, hr[0], L=Ls, rf=rf), body)
    body = US.glue(body, USP.plate_R(Uu[1], F4[1], sd_b, W, hr[1], L=Ls, rf=rf))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"]) if fit["segs"] else (body, 0)
    body = body.fuse(US.lower_pin(Uu[0], F4[0])).fuse(arbor_pin(Uu[1], F4[1]))
    q_lo, q_hi = stops["K"]["q"]
    for th in stops["K"]["homes"]: body = body.cut(arc_slot_cutter(H(1), Uu[1], th + q_lo, th + q_hi, -1.0, PL + 0.1))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l1a", f"D8-02a link 1a: 8x3 bar on a line/arc chain, J1 / K pads + integral O7 pins, K pin continued as the O5 spring arbor "
                       f"(0.4 mm slit, O3 magnet pocket); K's two opposed {math.degrees(q_hi - q_lo):.1f}-deg stop slots in the K pad ({r['process']})", body))
    rep["link 1a"] = dict(fit, **r, pocket=npk, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 1a: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}", flush=True)
    # ---- link 1b: K upper (1) -> J2 lower (2)
    body, ex, ey, start, fit, r, Ls, rf, sd_b = link_gh(M, prof, "L1b", "link 1b", 1, 2, True, False)
    body = US.glue(USP.plate_R(Uu[1], F4[1] + LV["U0"], ey, W, hr[1], L=Ls, upper=True, rf=rf), body)
    body = US.glue(body, USP.plate_R(Uu[2], F4[2], sd_b, W, hr[2], L=Ls, rf=rf))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"]) if fit["segs"] else (body, 0)
    body = USP.ring_root_R(US.glue(body, USP.upper_ring_R(Uu[1], F4[1], hr[1])), Uu[1], F4[1], hr[1])
    body = body.cut(USP.bore_cutter_R(Uu[1], F4[1], hr[1]))
    body = body.fuse(US.lower_pin(Uu[2], F4[2]))
    q_lo, q_hi = stops["J2"]["q"]
    for th in stops["J2"]["homes"]: body = body.cut(arc_slot_cutter(H(2), Uu[2], th + q_lo, th + q_hi, -1.0, PL + 0.1))
    dws = []
    for i, th in enumerate(stops["K"]["homes"]):
        dw, hole = dowel_at(H(1), Uu[1], th, F4[1]); body = body.cut(hole); dws.append(("l1b", f"K stop dowel {i + 1} of 2: ISO 8734 O3 x 5.65 m6 hardened (stop A dK 0 / "
                                                                                            f"stop B dK {math.degrees(stops['K']['q'][0] if abs(stops['K']['q'][0]) > 1e-9 else stops['K']['q'][1]):.2f}), "
                                                                                            "pressed 3 mm in the K upper boss, polished", dw))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l1b", f"D8-02b link 1b: 8x3 bar on a line/arc chain, K upper pad + O20 ring + M18 spigot + bore (2 dowel holes), J2 pad + integral O7 pin "
                       f"with the {math.degrees(q_hi - q_lo):.1f}-deg q2 stop slot ({r['process']})", body))
    rep["link 1b"] = dict(fit, **r, pocket=npk, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 1b: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}", flush=True)
    out += dws
    # ---- link 2: J2 upper (2) -> J3 upper (3, offset line) - user_style_pinknee.links2's geometry on this chain
    D = M.D; u, c = D.u, D.c; F = M.f
    Cj = [c[k_] + F[k_] * u[k_] for k_ in range(3)]
    ex = unit(u[1]); ey = unit(Cj[2] - (Cj[2] @ ex) * ex); nP = np.cross(ex, ey)
    u3p = unit(u[2] - (u[2] @ nP) * nP); lean = math.degrees(math.asin(abs(float(u[2] @ nP)))); phi = math.atan2(u3p @ ey, u3p @ ex)
    ha, hb = F[1] + LV["U0"] + T / 2, F[2] + LV["U0"] + T / 2
    p3 = c[2] + hb * u[2]; B = np.array([p3 @ ex, p3 @ ey]); back = np.array([math.sin(phi), -math.cos(phi)])
    Ls, rf = USP.HUG_SEAT, USP.HUG_RF; start = (ha, Ls, math.pi / 2); end = (*(B + Ls * back), math.pi / 2 + phi)
    Dq, Rq = link_cols(M, *prof["L2"])
    axes = [((0.0, 0.0), (1.0, 0.0)), (tuple(B), (math.cos(phi), math.sin(phi)))]
    if LINK_MODE == "profile": body, r = (profile_link_split if SPLIT else profile_link)("link 2", ex, ey, start, end, Dq, Rq, axes, [hr[2], hr[3]]); fit = dict(segs=None)
    else: fit, r = USP.hug_fit("link 2", ex, ey, start, end, Dq, Rq, axes, [hr[2], hr[3]]); body = US.bar_swept(ex, ey, start, fit["segs"])
    back_w = math.sin(phi) * ex - math.cos(phi) * ey
    body = US.glue(USP.plate_R(u[1], F[1] + LV["U0"], ey, W, hr[2], L=Ls, upper=True, rf=rf), body)
    body = US.glue(body, at(USP.plate_R(u[2], F[2] + LV["U0"], back_w, W, hr[3], L=Ls + 0.6, upper=True, rf=rf), c[2]))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"]) if fit["segs"] else (body, 0)
    body = USP.ring_root_R(US.glue(body, USP.upper_ring_R(u[1], F[1], hr[2])), u[1], F[1], hr[2])
    body = US.glue(body, at(USP.upper_ring_R(u[2], F[2], hr[3]), c[2]))
    body = body.cut(USP.bore_cutter_R(u[1], F[1], hr[2])).cut(at(USP.bore_cutter_R(u[2], F[2], hr[3]), c[2]))
    for th in stops["J2"]["homes"]:
        dw, hole = dowel_at(H(2), Uu[2], th, F4[2]); body = body.cut(hole)
        out.append(("l2", f"J2 stop dowel: ISO 8734 O3 x 5.65 m6 hardened (q2 stops {stops['J2']['meta']['window_deg'][0]:.2f} / "
                          f"{stops['J2']['meta']['window_deg'][1]:.2f} deg), pressed 3 mm in the J2 upper boss, polished", dw))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l2", f"D8-03 link 2: 8x3 bar on a line/arc chain + J2 / J3 O20 rings, J2 dowel hole, flies over the knee and the pad ({r['process']})", body))
    gap = float(abs((p3 - (p3 @ ex) * ex - (p3 @ ey) * ey) @ nP))
    rep["link 2"] = dict(fit, **r, seat_mm=Ls, pad_round_mm=rf, pocket=npk, u3_lean_out_of_plane_deg=lean, j3_seat_offset_mm=gap, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 2: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}; u3 leans {lean:.2f} deg, J3 seat {gap:.2f} mm off the plane", flush=True)
    return out, rep


# ---------------------------------------------------------------------------------------------------- hubs
def hubs(M):
    """the v5 O20 hardware at J1 (l1a / base), K (l1a / l1b, + the clock-spring cap, spring, magnet), J2 (l1b / l2), J3 (l3 / l2);
    the spline-dome caps replaced by torispherical line/arc caps"""
    Uu, C, F4, hr = BM.joints4(M); out = []; rep = {}
    capK = float(M.p.get("capK", 0) or 0); crown = LV["top"] + capK
    for J, j, lo, hi in (("J1", 0, "l1a", "base"), ("K", 1, "l1a", "l1b"), ("J2", 2, "l1b", "l2"), ("J3", 3, "l3", "l2")):
        for g, n, s in US.hardware(J, Uu[j], F4[j], lo, hi):
            if " cap " in n: continue
            out.append((g, n, at(s, C[j])))
        if J != "K":
            cap, Rc = cap_v5(Uu[j], F4[j]); rep["cap_style"] = CAP_STYLE; rep["dome_crown_R"] = None if Rc is None else round(Rc, 2)
            out.append((hi, (f"{J} cap O20, torispherical dome R{Rc:.1f} / R1 (tangent arcs)" if Rc else f"{J} cap O20 x crown F+12.25, flat crown, R0.5 corner")
                        + ", threaded M18x0.5 (Ti-6Al-4V)", at(cap, C[j])))
        else:
            cap = cap_k(Uu[j], F4[j], crown); sp, Lsp = clock_spring(Uu[j], F4[j])
            out.append((hi, f"K clock-spring cap O20 x crown F+{crown:.2f} ({capK:g} mm taller): spring chamber O16 x {CAPK['ch_z1'] - CAPK['ch_z0']:.1f}, "
                            f"outer-hook slot, O11 x 1.1 sensor pocket + flex groove, threaded M18x0.5 (Ti-6Al-4V)", at(cap, C[j])))
            out.append((hi, f"K clock spring: 0.3 x 5 mm 1.4310 +C1900 strip, {Lsp:.1f} mm, 9 half-turns R2.75..R7.55, outer hook in the cap slot, inner end in "
                            f"the arbor slit; <= 0.015 N.m/rad, 0.08 N.m preload on stop A (polished spring steel)", at(sp, C[j])))
            out.append(("l1a", "K encoder magnet O3 x 1.4 diametric NdFeB N35, Ni plated, in the arbor tip (the user's magnetic angle sensor sits in the cap pocket)",
                        at(magnet(Uu[j], F4[j]), C[j])))
            rep["K"] = dict(crown_mm=crown, capK=capK, spring_length_mm=round(Lsp, 1), spring=SPRING, cap=CAPK, cap_valid=cap.isValid(), spring_valid=sp.isValid(),
                            spring_solids=len(sp.Solids()))
            print(f"hub K: cap valid {cap.isValid()} ({len(cap.Solids())} solid), spring {Lsp:.1f} mm valid {sp.isValid()} ({len(sp.Solids())} solid)", flush=True)
    return out, rep


# ---------------------------------------------------------------------------------------------------- kinematic check
def check_frames(M, dd, l1_stops, stops):
    """build_minarc_l1.check_frames' poses and measures on the FULL CAD: (a) the model's metal samples (hub discs, E strap, E
    boss, arm pad, knee link, link straps) posed by the model's member transforms vs the posed exo.glb surface of their group
    (scene_export.frame_xforms on the frame dict = the judges' path); hub-disc samples over a stop slot counted apart (a real
    void); strap samples split outside / inside the lifted hub zones; (b) every exported vertex posed by the model's member
    transforms vs by frame_xforms; (c) the dowel centres inside their slots at the pose's joint angles"""
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
    forced = [i for i in kin if K["state"][i] != 0]; ft = [i for i in forced if i in set(taken)]
    if forced: pick["forced, K most open" + (" (taken)" if ft else " (closes, not taken)")] = max(ft or forced, key=lambda i: abs(K["dK"][i]))
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    grp_of = {0: "base", 1: "l1a", 7: "l1b", 2: "l2", 3: "l3", 6: "l4", 5: "H"}; out = []
    Uu, C, F4, hr = BM.joints4(M); D = M.D
    for lab, i in pick.items():
        pz = allp[i]; fr = BM.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; fdev = 0.0
        old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BM.BASE.swap_in(M, K); res = {}
        try:
            for node in src.graph.nodes_geometry:
                g, n = node.split("|")[:2]
                if g == "F" or g not in GROUPS: continue
                if g == "H" and not n.startswith("D8-06"): continue                        # the user's untouched arm parts, cuff, hardware
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
                if name in ("hubK", "hub2"):
                    k = 1 if name == "hubK" else 2; cen = C[k] + F4[k] * Uu[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ Uu[k])[:, None] * Uu[k], axis=1)
                    inslot = (rr > SLOT_RS - SLOT_W - 0.6) & (rr < SLOT_RS + SLOT_W + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]; d = d[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4)]
                if name in ("L1a", "L1b", "L2"):
                    lk = next(x for x in M.geo.links if x["name"] == name); zone = np.zeros(len(Xp), bool)
                    for kk in (lk["ka"], lk["kb"]):
                        w = Xp - C[kk]; zone |= np.linalg.norm(w - (w @ Uu[kk])[:, None] * Uu[kk], axis=1) < hr[kk] + 2.5 + 0.5
                    do = d[~zone]
                    res[name + " outside hub zones"] = [round(float(do.max()), 4) if len(do) else None, int((~zone).sum()),
                                                        round(float(np.mean(do <= 0.5)), 4) if len(do) else None, round(float(np.median(do)), 4) if len(do) else None]
                    res[name + " hub zones (lifted)"] = [round(float(d[zone].max()), 4) if zone.any() else None, int(zone.sum())]
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                q_lo, q_hi = [math.degrees(x) for x in stops[key]["q"]]
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(ang - q_lo, 3), to_stop_hi_deg=round(q_hi - ang, 3),
                                   inside=bool(q_lo - 0.01 <= ang <= q_hi + 0.01))
        finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
        rig = {k: v for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None}
        worst = max(v[0] for v in rig.values()); joint = max(res[k][0] for k in ("hub1", "hubK", "hub2", "hub3", "boss", "pad"))
        worst_o = max((res[k][0] or 0) for k in ("L1a outside hub zones", "L1b outside hub zones", "L2 outside hub zones"))
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        joint_features_max_mm=round(joint, 4), rigid_samples_max_mm=round(worst, 4), strap_samples_outside_hub_zones_max_mm=round(worst_o, 4),
                        within_0p5=bool(joint <= 0.5 and fdev <= 0.5), per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4),
                        knee_angle=round(float(K["Kn"]["ang"][i]), 1), stops=inside))
        print(f"  check {lab:30s} pose {i} {np.round(pz[:3], 1)} state {int(K['state'][i]):+d}: hubs/boss/pad vs posed glb {joint:.3f} mm (all rigid {worst:.3f}: "
              + ", ".join(f"{k} {v[0]:.2f}" for k, v in rig.items() if k not in ("hub1", "hubK", "hub2", "hub3", "boss", "pad")) + f"), straps outside zones {worst_o:.2f}; "
              f"frames {fdev:.1e} mm; dK {inside['K']['angle_deg']:.2f} q2 {inside['J2']['angle_deg']:.2f} in slot {inside['K']['inside']}/{inside['J2']['inside']}", flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_minarc_bdp"); ap.add_argument("--l1", default="l1_minarc-bdp")
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--a1max", type=float, default=BM.A1MAX_FIX)
    ap.add_argument("--skip-base-search", action="store_true", help="no ear search (the J1 upper member alone)")
    a = ap.parse_args(MY_ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    import concept_kit as KIT
    P0, src = BM.params_from(a); M, rep0 = BM.fit(P0); D = M.D
    l1d = json.load(open(os.path.join(FULL, "designs", a.l1, "design.json"))); l1b = json.load(open(os.path.join(FULL, "designs", a.l1, "build.json")))
    same = all(abs(float(l1d["params"].get(k, P0[k])) - float(P0[k])) < 1e-6 for k in P0 if isinstance(P0[k], (int, float)))
    assert same, f"the L1 design {a.l1} was built from other params"
    assert abs(float(l1b["fit"]["tr"]) - float(M.tr)) < 1e-2 and np.allclose(l1b["fit"]["m"], D.m, atol=1e-2), "the fit differs from the L1's (its frames are another shape)"
    Uu, C, F4, hr = BM.joints4(M)
    print(f"fit ({src}) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']} plain {rep0['plain']['gap']} hub levels "
          f"{np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f} m {np.round(D.m, 3).tolist()} ({time.time() - t0:.0f} s)", flush=True)
    l1_stops = l1d["stack_mm"]["stops"]; stops = stop_layout(M, l1_stops)
    rep = dict(fit=dict(params=P0, source=src, gap_near_touch=rep0["gap"], gap_plain=rep0["plain"]["gap"], hub_levels_J1_K_J2_J3=[float(x) for x in F4],
                        tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr], fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths, rounds; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"])
                      for k, v in stops.items()})
    parts = []                                                                              # (group, name, shape) member-local
    hw, rep["hubs"] = hubs(M); parts += hw
    lk, rep["links"] = build_links(M, stops); parts += lk
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = USP.knee_link(M); parts.append((g_, n_, s_))
    Cc = json.load(open(os.path.join(FULL, "designs", a.l1, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = USP.arm_side(M, l1b["mount"], cposes); parts += [(g, n, s) for g, _, n, s in arm]
    # ---- the base at the J1 ring vs the posed link 1a (every clip frame + every eval-feasible workspace pose)
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
    Mb = M; Mb_D = M.D                                                                       # base_part reads D.u[0], f[0], hr[0] = J1 (same in this chain)
    bp, rep["base"] = USP.base_part(Mb, E, l1_body, rel, frames); parts.append((bp[0], bp[2], bp[3]))
    # ---- export: member-local; H = HR x; the user's parts as they are
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")): os.remove(os.path.join(dd, "step", f))
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith("D8-") and any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        trep = {}; m = USP.tess(s, fine=not user, report=trep)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        if user: mat, rho = "user part", None
        elif "iglidur" in n: mat, rho = "iglidur", USP.IGL
        elif "bearing" in n: mat, rho = "bearing steel", 7.8
        elif "17-4PH" in n: mat, rho = "17-4PH", 7.8
        elif "dowel" in n.lower(): mat, rho = "hardened steel (polished)", 7.85
        elif "clock spring" in n: mat, rho = "1.4310 spring steel (polished)", 7.9
        elif "magnet" in n: mat, rho = "NdFeB, Ni plated", 7.5
        elif hwr: mat, rho = "stainless (polished)", 7.9
        elif "7075-T6" in n: mat, rho = "7075-T6 (BOTTOM merged with the pad mount)", 2.81
        elif n.startswith("UPPER ARM CUFF"): mat, rho = "AlSi10Mg", 2.68
        else: mat, rho = "Ti-6Al-4V", USP.TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L2 user-style", FACES={"1": round(float(F4[0]), 2), "K": round(float(F4[1]), 2), "2": round(float(F4[2]), 2),
                                                                 "3": round(float(F4[3]), 2)}, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    for f in ("clips.json", "workspace.json"): shutil.copy(os.path.join(FULL, "designs", a.l1, f), os.path.join(dd, f))
    d = dict(l1d); d.update(id=a.out, label=f"minarc-stop-knuckle-4r BDp ({src}), full CAD in the user's style", level="L2 user-style (full CAD of the generation-4 winner)",
                            l1_design=a.l1, built_with="pipeline/conformal/param_cad/user_style_minarc.py (user_style / user_style_pinknee parts: v5 O20 hubs, K clock-spring "
                            "cap, hugging machined bars 1a / 1b / 2, O3 dowel-in-arc-slot stops (K opposed pair), member 3, knee link + IGLIDUR-PIN stacks, BOTTOM fused "
                            f"with the pad mount) on the L1 design's frames and clips ({a.l1})")
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; rep["ring_root_fillet_skipped"] = USP.RING_ROOT_SKIPPED
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    rep["check"] = check_frames(M, dd, l1_stops, stops)
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), all_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]),
                                   max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                   dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] for r in rep["check"]))
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"kinematics: {rep['kinematics_exact']}; done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
