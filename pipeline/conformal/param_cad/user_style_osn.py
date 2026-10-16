"""Full user-style CAD of offset-skin-normal-3r k4216 (docs/concepts/offset-skin-normal-3r.md) - the generation-2 winner.

The kinematics are EXACTLY the verified model's: the shape is the model's own fit (build_osn_l1.fit, Bench(60,160) fast,
gap 32.61), every part is designed in the model's member-local rest frame (= the scapula frame at rest, GH = origin) and
exported in its member's group, and clips.json / workspace.json are the L1 design's (l1_offset-skin-normal-3r: "G" + "T"
per group, world = RS (R_m x + t_m); the arm-fixed parts sit in H at x_H = HR (x + m)). Only the part shapes change,
in the user's style (user_style.py, no lofts):

  hubs     J1, J2, J3: the v5 O20 stack exactly as user_style.py builds it (pads + integral O7 pins on the lower member,
           O20 ring + M18 spigot + bore on the upper member, 2x MR117-2RS, 17-4PH outer spacer, ground inner spacer,
           M7x0.5 Ti ring nut, threaded G2 dome cap); J3 is the same stack about its OFFSET line (foot point c3, 7.0 mm
           from GH, tilted b3 toward the skin normal): built about GH, then moved by c3 (c3 is perpendicular to u3).
  links    bent 8 x 3 bars, user_style.bar_swept: the side view is a chain of tangent lines and arcs in the great-circle
           plane the model's strap rides in (link 1: span(u1, u2); link 2: span(C2, C3), C = the hub face centres),
           fitted (sketch2d.fit_chain) to stay at or above the L1 strap's underside (the model's fitted rows + the L1's
           hub-rim lift) and hug it; planform pads at the hubs, the user-style pocket, 0.5 mm rounds. Link 2's J3 pad
           is the J3 seat plane; u3 leans 3.9 deg out of link 2's plane, so the bar ends 0.6 mm inside that pad.
  member 3 hub 3's lower pad + pin + the model's ramped neck (60 deg, its underside = the model's to the arcs) + the
           bridge, ONE side-view sketch of lines and tangent arcs extruded 8 mm, on the across block (carriage B).
  stage    the real catalogue guides (tools/hardware_catalogue.json THK-RSR3M = HIWIN MGN03C class: H 4, block 8 x 12,
           rail 3 x 2.6, pitch 10): along guide INVERTED (block on the cuff base, rail 26.6 riding with carriage A), a 1 mm
           plus-shaped adapter (carriage A), the across rail 29 + its block (carriage B); stack 1.5 + 4 + 1 + 4 = 10.5 mm.
  arm side the cuff base plate + arm + a tongue in BOTTOM's channel, fused with the user's BOTTOM (cut at s 255) into
           ONE 5-axis part (BOTTOM is the one user part we may modify); the upper-arm cuff from one line/arc sketch
           (user_style.upper_cuff); the user's other arm parts unchanged.
  base     the scapula base: J1 ring + a 16 mm tab with 2x M4 counterbored to the user's scapula handler, the tab heading
           chosen outside link 1's sweep about J1 over the followed clip frames.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_osn.py [--out user_osn_k4216]
"""
import argparse, json, math, os, shutil, sys, time
ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import user_style as US                                                                   # noqa: E402  (also param_build, sketch2d, arm_end)
REPO = US.FR.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_osn_l1 as L1B                                                                # noqa: E402  (the model fit, frames, catalogue sizes)
import numpy as np, cadquery as cq, trimesh                                               # noqa: E402
PB, SK, AE, LV, unit, V, xform = US.PB, US.SK, US.AE, US.LV, US.unit, US.V, US.xform
HUB_R, T, W, L_SEAT = US.HUB_R, US.T, US.W, US.L_SEAT
FULL = US.FR.FULL; SRC = "l1_offset-skin-normal-3r"
GH_, GW, GL, RW, RH, H1 = L1B.GH, L1B.GW, L1B.GL, L1B.RW, L1B.RH, L1B.H1                   # RSR3M: H 4, W 8, L 12, rail 3 x 2.6, H1 1
BASE_T, ADAPT_T, ARM_W, CH = L1B.BASE_T, L1B.ADAPT_T, L1B.ARM_W, L1B.CH
CACHE = os.path.join(REPO, ".cache", "user_style_osn_fits.json")
SCREW = "M1.6"                                                                            # [est] miniature-guide screws (not in the catalogue json)


def at(s, c): return xform(s, np.eye(3), np.asarray(c, float))


# ---------------------------------------------------------------------------------------------------- sketch helpers
def rounded_poly(pl, pts, radii):
    """closed wire on cq.Plane pl: polygon pts [(x, y)] with a tangent arc of radius radii[i] at vertex i (0 = sharp)"""
    P = [np.asarray(p, float) for p in pts]; n = len(P); segs = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]; r = radii[i]
        if r <= 0: segs.append((b, None, b)); continue
        u1, u2 = unit(a - b), unit(c - b); th = math.acos(np.clip(u1 @ u2, -1, 1))
        d = r / math.tan(th / 2); t1, t2 = b + d * u1, b + d * u2
        assert d < np.linalg.norm(a - b) + 1e-9 and d < np.linalg.norm(c - b) + 1e-9, ("arc too big", i, r)
        cen = b + (r / math.sin(th / 2)) * unit(u1 + u2); mid = cen + r * unit(b - cen)
        segs.append((t1, mid, t2))
    wp = cq.Workplane(pl).moveTo(*segs[0][2])
    for i in range(1, n + 1):
        t1, mid, t2 = segs[i % n]
        if np.linalg.norm(t1 - np.array(wp.val().endPoint().toTuple()[:2]) if False else 0) < 0: pass
        wp = wp.lineTo(*t1) if mid is None else wp.lineTo(*t1).threePointArc(tuple(mid), tuple(t2))
    return wp.close()


def plane(origin, xdir, ydir):
    xdir = unit(xdir); ydir = unit(ydir - (ydir @ xdir) * xdir)
    return cq.Plane(origin=tuple(map(float, origin)), xDir=tuple(map(float, xdir)), normal=tuple(map(float, np.cross(xdir, ydir))))


def prism(origin, xdir, ydir, pts, radii, h, both=False):
    """sketch (lines + tangent arcs) in the plane (origin, xdir, ydir), extruded h along xdir x ydir (both: +-h/2)"""
    wp = rounded_poly(plane(origin, xdir, ydir), pts, radii)
    return (wp.extrude(h / 2, both=True) if both else wp.extrude(h)).val()


def screw_csk(p, axis, d, L, name):
    """countersunk screw (ISO 10642 style, polished), head flush at p, shank along +axis (into the part)"""
    k = 1.0 if d < 2 else 1.2; dk = 2 * d
    prof = [(0, 0), (dk / 2, 0), (d / 2, (dk - d) / 2 * 1.0), (d / 2, L), (0, L)]
    return ("screw", name, xform(PB.revolved(prof, np.array([0, 0, 1.0]), 0.0), PB.axis_frame(axis), p))


def csk_hole(p, axis, d, depth):
    """countersunk through hole: cone (90 deg) from the face at p + a clearance bore along +axis"""
    s = cq.Solid.makeCylinder(d / 2 + 0.1, depth + 1, V(p - 0.5 * axis), V(axis))
    return s.fuse(cq.Solid.makeCone(d + 0.1, 0.0, d + 0.1, V(p - 0.01 * axis), V(axis)))


# ---------------------------------------------------------------------------------------------------- links
def l1_rows(M, lk, rows):
    """the L1 strap underside (build_osn_l1.link_solid's rows + hub-rim lift): directions (q, n, 3), radii (q, n), stations J"""
    D = M.D; u, c = D.u, D.c; F = M.f; UP = L1B.UP; unit_ = L1B.unit
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): UP}
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r.copy() for _, _, r in rows]
    d_lo = unit_(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit_(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
    cols_d = [d_lo] + dvs + [d_hi]; cols_r = [rs[0].copy()] + [r.copy() for r in rs] + [rs[-1].copy()]
    for kk, j in ((lk["ka"], j0), (lk["kb"], j1)):
        if j == (idx[0] if kk == lk["ka"] else idx[-1]): continue
        cen = c[kk] + F[kk] * u[kk]
        for q in range(len(cols_d)):
            den = float(cols_d[q][j] @ u[kk])
            if den > 0.2: cols_r[q][j] = max(cols_r[q][j], (cen @ u[kk] + lvl[(lk["name"], kk)]) / den + 0.02)
    for kk in (lk["ka"], lk["kb"]):
        cen = c[kk] + F[kk] * u[kk]; lv = lvl[(lk["name"], kk)] + 0.2
        for q in range(len(cols_d)):
            Pq = cols_d[q] * cols_r[q][:, None]; w = Pq - c[kk]
            off = np.linalg.norm(w - (w @ u[kk])[:, None] * u[kk], axis=1); den = cols_d[q] @ u[kk]
            sel = (off < HUB_R + 2.5) & (den > 0.2)
            cols_r[q][sel] = np.maximum(cols_r[q][sel], (cen @ u[kk] + lv) / den[sel])
    J = np.arange(j0, j1 + 1)
    return np.array([cd[J] for cd in cols_d]), np.array([cr[J] for cr in cols_r])


def link_fit(label, ex, ey, start, end, Dq, Rq, t=T):
    """bent-bar chain (start -> end poses in the plane (GH, ex, ey)) whose skin side stays >= the L1 strap underside"""
    th_q = np.arctan2(Dq @ ey, Dq @ ex); rho_q = Rq * np.hypot(Dq @ ex, Dq @ ey)       # in-plane angle / radius of each sample
    th = th_q.mean(0); order = np.argsort(th); th = th[order]; need = rho_q.max(0)[order]
    clear = lambda U: np.hypot(U[:, 0], U[:, 1]) - np.interp(np.arctan2(U[:, 1], U[:, 0]), th, need)
    key = f"{label}|{np.round(ex, 5).tolist()}|{np.round(ey, 5).tolist()}|{np.round(start, 4).tolist()}|{np.round(end, 4).tolist()}|{np.round(need, 3).tolist()}"
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    if key in cache: fit = cache[key]; fit["segs"] = [tuple(x) for x in fit["segs"]]
    else:
        fits = {}
        for n_ in range(3, 6):
            for cm in (35.0, 45.0, 60.0):
                try: fits[n_] = SK.fit_chain(start, end, clear, t, n_arcs=n_, climb_max=cm); fits[n_]["climb_limit"] = cm; break
                except RuntimeError as e: print(f"  {label}: {n_} arcs, climb {cm}: {e}", flush=True)
        if not fits: raise RuntimeError(f"{label}: no chain stays above the L1 strap")
        bm = min(f_["mean_clear"] for f_ in fits.values())
        nb = min(n_ for n_, f_ in fits.items() if f_["mean_clear"] <= bm + 1.0); fit = fits[nb]
        fit = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in fit.items()}
        fit["segs"] = [(float(k), float(l)) for k, l in fit["segs"]]; fit["radii"] = [None if r is None else float(r) for r in fit["radii"]]
        cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}; cache[key] = fit
        os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(cache, open(CACHE, "w"), indent=0)
    # the bar's skin side over the L1 strap underside, sampled along the chain
    P, H, _ = SK.sample(start, fit["segs"], 40); U = P - 0.5 * t * SK.normals(H); cl = clear(U)
    print(f"{label}: radii {[None if r is None else round(r, 1) for r in fit['radii']]}, lengths {[round(l, 1) for _, l in fit['segs']]}, "
          f"over the L1 underside min {cl.min():.2f} mean {cl.mean():.2f} max {cl.max():.2f} mm, max climb {fit['max_climb']:.1f} deg "
          f"(limit {fit.get('climb_limit', 35)})", flush=True)
    return fit, dict(over_L1_min=float(cl.min()), over_L1_mean=float(cl.mean()), over_L1_max=float(cl.max()))


def links(M):
    D = M.D; u, c = D.u, D.c; F = M.f; prof = L1B.REF.link_profiles(M); out = []; rep = {}
    C = [c[k] + F[k] * u[k] for k in range(3)]
    # ---- link 1: lower at J1 and J2 (both axes through GH), plane span(u1, u2)
    ex = unit(u[0]); ey = unit(u[1] - (u[1] @ ex) * ex); phi = math.acos(np.clip(unit(u[1]) @ ex, -1, 1))
    ha, hb = F[0] + T / 2, F[1] + T / 2
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    start = (ha, L_SEAT, math.pi / 2); end = (*(B + L_SEAT * back), math.pi / 2 + phi)
    Dq, Rq = l1_rows(M, *prof["L1"]); fit, r1 = link_fit("link 1", ex, ey, start, end, Dq, Rq)
    body = US.bar_swept(ex, ey, start, fit["segs"])
    he = SK.end_pose(start, fit["segs"])[2]; sd_b = -(math.cos(he) * ex + math.sin(he) * ey)
    body = US.glue(US.plate_r(u[0], F[0], ey, W), body)
    body = US.glue(body, US.plate_r(u[1], F[1], sd_b, W))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"])
    for k_ in (0, 1): body = body.fuse(US.lower_pin(u[k_], F[k_]))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l1", 1, "D7-02 link 1: bent bar 8x3 + J1/J2 pads + integral O7 pins (Ti-6Al-4V)", body))
    rep["link 1"] = dict(fit, **r1, pocket=npk, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 1: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}", flush=True)
    # ---- link 2: upper at J2 (through GH) and J3 (offset line), plane span(C2, C3) = the model's strap plane
    ex = unit(u[1]); ey = unit(C[2] - (C[2] @ ex) * ex); nP = np.cross(ex, ey)
    u3p = unit(u[2] - (u[2] @ nP) * nP); lean = math.degrees(math.asin(abs(float(u[2] @ nP))))
    phi = math.atan2(u3p @ ey, u3p @ ex)
    ha, hb = F[1] + LV["U0"] + T / 2, F[2] + LV["U0"] + T / 2
    p3 = c[2] + hb * u[2]; B = np.array([p3 @ ex, p3 @ ey]); back = np.array([math.sin(phi), -math.cos(phi)])
    start = (ha, L_SEAT, math.pi / 2); end = (*(B + L_SEAT * back), math.pi / 2 + phi)
    Dq, Rq = l1_rows(M, *prof["L2"]); fit, r2 = link_fit("link 2", ex, ey, start, end, Dq, Rq)
    body = US.bar_swept(ex, ey, start, fit["segs"])
    back_w = math.sin(phi) * ex - math.cos(phi) * ey                                      # in the J3 seat plane (perpendicular to u3)
    body = US.glue(US.plate_r(u[1], F[1] + LV["U0"], ey, W, upper=True), body)
    pad3 = at(US.plate_r(u[2], F[2] + LV["U0"], back_w, W, L=L_SEAT + 0.6, upper=True), c[2])
    body = US.glue(body, pad3)
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"])
    body = US.ring_root_fillet(US.glue(body, US.upper_ring_r(u[1], F[1])), u[1], F[1])
    body = US.glue(body, at(US.upper_ring_r(u[2], F[2]), c[2]))
    body = body.cut(US.bore_cutter(u[1], F[1])).cut(at(US.bore_cutter(u[2], F[2]), c[2]))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l2", 2, "D7-03 link 2: bent bar 8x3 + J2/J3 hubs (Ti-6Al-4V)", body))
    gap = float(abs((p3 - (p3 @ ex) * ex - (p3 @ ey) * ey) @ nP))
    rep["link 2"] = dict(fit, **r2, pocket=npk, u3_lean_out_of_plane_deg=lean, j3_seat_offset_mm=gap, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 2: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}; u3 leans {lean:.2f} deg out of "
          f"the bar plane, J3 seat centre {gap:.2f} mm off it", flush=True)
    return out, rep


# ---------------------------------------------------------------------------------------------------- scapula base
def base_part(M, E, l1_dirs):
    """J1 upper ring + a tab (16 wide, 3 thick: a bent bar from a 3-arc sketch) to the user's scapula handler, 2x M4
    counterbored; heading = the lowest-sitting one outside link 1's sweep about J1 (+-30 deg)"""
    D = M.D; k1 = unit(D.u[0]); F1 = M.f[0]; up_mid = LV["U0"] + T / 2
    d0 = unit(np.array([0.0, 0.6, -0.8])); d0 = unit(d0 - (d0 @ k1) * k1); d1 = np.cross(k1, d0)
    ang = np.degrees(np.arctan2(l1_dirs @ d1, l1_dirs @ d0))                              # link 1's heading about J1, every followed frame
    def dist_sector(al): return float(np.min(np.abs((ang - al + 180) % 360 - 180)))
    th = math.radians(32); best = None; Rg = np.eye(3)
    for al in np.arange(-180.0, 180.0, 10.0):
        if dist_sector(al) < 30.0: continue
        td = math.cos(math.radians(al)) * d0 + math.sin(math.radians(al)) * d1
        fld = US.PolarField(E, "S", Rg, k1, td, -5.0, 45.0, 16.0)
        for h in np.arange(F1 + up_mid, F1 + 60, 0.5):
            P0 = h * np.array([math.cos(th), math.sin(th)]); hd = np.array([-math.sin(th), math.cos(th)])
            U = np.array([P0 + s_ * hd for s_ in np.linspace(0, 26, 14)]) - (T / 2) * np.array([math.cos(th), math.sin(th)])
            if fld(U).min() >= 0.5:
                if best is None or h < best[0]: best = (h, al, td, fld)
                break
    assert best, "base tab: no heading outside link 1's sweep"
    ht, al, ey_, fld = best; ex_ = k1
    print(f"base tab: heading {al:.0f} deg about J1 (link 1 sweeps {ang.min():.0f}..{ang.max():.0f}, nearest {dist_sector(al):.0f} deg away), "
          f"terminal height {ht:.1f} mm", flush=True)
    start = (F1 + up_mid, L_SEAT, math.pi / 2); end = (*(ht * np.array([math.cos(th), math.sin(th)])), th + math.pi / 2)
    fit = SK.fit_chain(start, end, fld, T, n_arcs=3, climb_max=US.CLIMB)
    body = US.glue(US.plate_r(k1, F1 + LV["U0"], ey_, 16.0, upper=True), US.bar_swept(ex_, ey_, start, fit["segs"], w=16.0))
    o_mid = ht * (math.cos(th) * ex_ + math.sin(th) * ey_); sd = -math.sin(th) * ex_ + math.cos(th) * ey_; nrm = unit(o_mid)
    body = US.glue(body, US.terminal_r(o_mid, nrm, sd, 16.0, 14.0))
    body = US.glue(body, US.upper_ring_r(k1, F1))
    body = body.cut(US.bore_cutter(k1, F1))
    for x_ in (9.0, 17.0):                                                                 # 2x M4: O4.3 through, O7.3 x 1.2 counterbore
        cc = o_mid + x_ * sd
        body = body.cut(cq.Solid.makeCylinder(2.15, 12.0, V(cc - 6 * nrm), V(nrm)))
        body = body.cut(cq.Solid.makeCylinder(3.65, 3.0, V(cc + (T / 2 - 1.2) * nrm), V(nrm)))
    body = body.clean() if body.clean().isValid() else body
    print(f"  base: valid {body.isValid()}, solids {len(body.Solids())}", flush=True)
    return ("base", 0, "D7-01 scapula base: J1 hub + tab, 2x M4 counterbored to the scapula handler (Ti-6Al-4V)", body), \
        dict(heading_deg=float(al), link1_sector_deg=[float(ang.min()), float(ang.max())], radii=fit["radii"], min_clear=fit["min_clear"],
             mean_clear=fit["mean_clear"], terminal_height=float(ht), valid=body.isValid())


# ---------------------------------------------------------------------------------------------------- member 3 + stage
def member3_and_stage(M):
    """[(group, member, name, shape in the member-local rest frame; member 5 before the mid offset)]"""
    D = M.D; P = D.p; u, c = D.u, D.c; F = M.f; tr = M.tr; sa, st, sn = D.sa, D.st, D.sn
    cs = D.stage_c(); c3 = c[2]; F3 = F[2]; neck = P["neck"]; Sa, St = P["S_a"], P["S_t"]
    ztop = M.zb + L1B.S.CAR_H; kr = math.tan(math.radians(L1B.S.RAMP)); xcs = float((cs - c3) @ sa)
    out = []; rep = {}
    # ---- member 3: J3 lower pad + pin, neck + bridge = ONE side-view sketch (x along sa from c3, z along sn), extruded 8
    z_blk = tr + BASE_T + GH_ + ADAPT_T + GH_                                              # across block top = tr + 10.5
    xn1, zn1 = HUB_R + neck, ztop                                                          # the model's neck end (underside)
    P1 = (xn1 - (zn1 - F3) / kr, F3); P2 = (xn1 - (zn1 - z_blk) / kr, z_blk)
    s60, c60 = math.sin(math.radians(L1B.S.RAMP)), math.cos(math.radians(L1B.S.RAMP))
    xt, zt = xn1 - T * s60, zn1 + T * c60                                                   # top ramp line (3 mm normal offset)
    z_top, z_over = z_blk + 6.0, ztop                                                      # bridge: 6 mm tall, 3 mm over the block
    P7 = (xt + (z_top - zt) / kr, z_top); P8 = (xt - (zt - (F3 + T)) / kr, F3 + T)
    x_step, x_end = xcs - L1B.S.CAR_L / 2, xcs + GW / 2
    pts = [(L_SEAT, F3), P1, P2, (x_end, z_blk), (x_end, z_over), (x_step, z_over), (x_step, z_top), P7, P8, (L_SEAT, F3 + T)]
    rad = [0.0, 3.2, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 0.2, 0.0]
    neckb = prism(c3, sa, sn, pts, rad, W, both=True)
    m3 = US.glue(at(US.plate_r(u[2], F3, sa, W), c3), neckb)
    m3 = m3.fuse(at(US.lower_pin(u[2], F3), c3))
    for y_ in (-2.5, 2.5):                                                                 # 2x M1.6 [est] into the across block
        p = c3 + xcs * sa + y_ * st + z_over * sn
        m3 = m3.cut(csk_hole(p, -sn, 1.6, 4.0))
        out.append(("l3", 3, f"{SCREW}x4 ISO 10642 countersunk, across block to member 3 (polished)", screw_csk(p, -sn, 1.6, 4.0, "")[2]))
    m3 = m3.clean() if m3.clean().isValid() else m3
    out.insert(0, ("l3", 3, "D7-04 member 3: J3 pad + integral O7 pin + ramped neck (60 deg, the model's) + bridge, one sketch (Ti-6Al-4V)", m3))
    rep["member 3"] = dict(neck_underside=[list(map(float, P1)), list(map(float, P2))], bridge=[float(x_step), float(x_end), float(z_blk), float(z_top)],
                           valid=m3.isValid(), solids=len(m3.Solids()))
    print(f"member 3: neck {neck:.1f} mm, ramp 60 deg from F3 {F3:.2f} to the block top {z_blk:.2f}; valid {m3.isValid()}, solids {len(m3.Solids())}", flush=True)
    # ---- the real stage, heights z from the fitted cuff level tr along sn, around the stage centre cs
    z_blk0 = BASE_T; z_rail0 = BASE_T + GH_ - RH; z_rail1 = BASE_T + GH_
    z_ad1 = z_rail1 + ADAPT_T; z_xr1 = z_ad1 + RH; z_xb0 = z_ad1 + H1; z_xb1 = z_ad1 + GH_
    LA, LT = GL + 2 * Sa + 2.0, GL + 2 * St + 2.0
    o = lambda z: cs + (tr + z) * sn
    w, cw, bd = GW / 2, (RW + 2 * CH) / 2, GH_ - H1                                        # block body: 8 wide, 3 tall, channel 3.4
    chd = z_rail1 - z_rail0 - H1 + CH
    def u_sec(open_up):
        y0, y1 = (0.0, bd) if open_up else (bd, 0.0)
        yc = y1 - chd if open_up else y1 + chd
        return [(-w, y0), (w, y0), (w, y1), (cw, y1), (cw, yc), (-cw, yc), (-cw, y1), (-w, y1)], [0.3, 0.3, 0.3, 0, 0, 0, 0, 0.3]
    pts, rad = u_sec(True)                                                                  # inverted along block: mount face down on the base
    blk = prism(o(z_blk0), st, sn, pts, rad, GL, both=True)
    for x_ in (-2.5, 2.5): blk = blk.cut(cq.Solid.makeCylinder(0.65, 1.5, V(o(z_blk0) + x_ * sa - 0.1 * sn), V(sn)))   # M1.6 tapped (drill 1.3)
    out.append(("H", 5, f"along guide block THK RSR3M (= HIWIN MGN03C class), INVERTED on the cuff base: W {GW} x L {GL} x H {GH_} (catalogue)", blk))
    rail = lambda L_, pitch_dir: None
    def rail_solid(origin, along, up, L_):
        """rail 3 x 2.6, 0.2 chamfers, counterbored holes at the catalogue pitch 10 (M1.6)"""
        pts_ = [(-RW / 2, 0), (RW / 2, 0), (RW / 2, RH), (-RW / 2, RH)]
        across = np.cross(up, along)
        s = prism(origin, across, up, pts_, [0.2] * 4, L_, both=True)
        for x_ in np.arange(-math.floor(L_ / 2 / 10) * 10, L_ / 2, 10.0):
            if abs(x_) > L_ / 2 - 2.5: continue
            p = origin + x_ * along
            s = s.cut(cq.Solid.makeCylinder(0.9, RH + 1, V(p - 0.5 * up), V(up))).cut(cq.Solid.makeCylinder(1.5, 1.0, V(p + (RH - 1.0) * up), V(up)))
        return s
    # along rail (rides with carriage A): base face on the adapter (up), running face down in the block's channel
    ar = rail_solid(o(z_rail1), sa, -sn, LA)
    out.append(("l4", 4, f"along guide rail THK RSR3R3 3 x 2.6 x {LA:.1f} (catalogue rail, travel +-{Sa}), rides with carriage A", ar))
    # carriage A: plus-shaped 1 mm adapter, R1 roots, R1 corners
    a_, t_, h_ = LA / 2, LT / 2, ARM_W / 2
    pp = [(a_, -h_), (a_, h_), (h_, h_), (h_, t_), (-h_, t_), (-h_, h_), (-a_, h_), (-a_, -h_), (-h_, -h_), (-h_, -t_), (h_, -t_), (h_, -h_)]
    ad = prism(o(z_rail1), sa, st, pp, [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], ADAPT_T)
    out.append(("l4", 4, f"carriage A: plus-shaped adapter {ADAPT_T} mm, arms {ARM_W} wide, under both rails (Ti-6Al-4V)", ad))
    xr = rail_solid(o(z_ad1), st, sn, LT)
    out.append(("l4", 4, f"across guide rail THK RSR3R3 3 x 2.6 x {LT:.1f} (catalogue rail, travel +-{St}), on carriage A", xr))
    pts, rad = u_sec(False)                                                                 # across block: opening down over the rail
    pts = [(x, -y) for x, y in pts]; pts = pts[::-1]; rad = rad[::-1]
    xb = prism(o(z_xb1), sa, sn, pts, rad, GL, both=True)
    out.append(("l3", 3, f"carriage B = across guide block THK RSR3M (= HIWIN MGN03C class): W {GW} x L {GL} x H {GH_} (catalogue)", xb))
    stack = dict(base=[0, BASE_T], along_block=[z_blk0, z_blk0 + bd], along_rail=[round(z_rail0, 2), z_rail1], adapter=[z_rail1, z_ad1],
                 across_rail=[z_ad1, round(z_xr1, 2)], across_block=[z_xb0, z_xb1], total=z_xb1, rails_mm=dict(along=round(LA, 1), across=round(LT, 1)))
    rep["stage"] = stack
    return out, rep


def arm_side(M):
    """the cuff base plate + arm (stage plane, 1.5 mm at the fitted cuff level, as the L1's base plate + mount) and a
    tongue in BOTTOM's channel (planform in the channel plane, 0.5 mm into BOTTOM's 2 mm web), fused with BOTTOM (cut at
    s 255) into one 5-axis part. Built in the arm's rest frame H. Returns ([(group, name, shape)], report)"""
    D = M.D; sa, st, sn = D.sa, D.st, D.sn; cs = D.stage_c(); tr = M.tr; HR = L1B.HR
    mv = D.m[0] * sa + D.m[1] * st + D.m[2] * sn
    toH = lambda p: HR @ (np.asarray(p) + mv); dH = lambda d: HR @ np.asarray(d)
    O = toH(cs + tr * sn); aH, tH, nH = dH(sa), dH(st), dH(sn)
    CB, uB, vB, axB = AE.CB, AE.uB, AE.vB, AE.axB
    sc = float((O - CB) @ uB); vc = float((O - CB) @ vB)
    # plate: base plate under the along block + the arm toward BOTTOM (the L1's mount footprint), lines + tangent arcs
    pts = [(-(GL / 2 + 1), -(GW / 2 + 1)), (37.0, -(GW / 2 + 1)), (37.0, 19.6), (6.0, 19.6), (6.0, GW / 2 + 1), (-(GL / 2 + 1), GW / 2 + 1)]
    plate_ = prism(O, aH, tH, pts, [2.0, 3.0, 3.0, 3.0, 2.0, 2.0], BASE_T)
    # tongue: s 236..252 along BOTTOM, |v| <= 11 (inside the flanges), ax -2.0 .. 2.2 (0.5 mm into the web at 1.7..3.7)
    pl = plane(CB + 244.0 * uB + 0.0 * vB - 2.0 * axB, uB, vB)
    tongue = rounded_poly(pl, [(-8, -11), (8, -11), (8, 11), (-8, 11)], [2.0] * 4).extrude(4.2).val()
    br = plate_.fuse(tongue).clean()
    for x_ in (-2.5, 2.5): br = br.cut(csk_hole(O + x_ * aH, nH, 1.6, BASE_T + 1.0))      # 2x M1.6 [est] into the along block, flush
    up = AE.user_parts()
    bot = [s for g, n, s in up if n.startswith("BOTTOM")][0]
    part = bot.fuse(br); part = part.clean() if part.clean().isValid() else part
    out = [("H", "D7-05 BOTTOM + stage base, one 5-axis part (user's bar cut at s 255; base plate 1.5 under the along block + arm + tongue fused into its channel web; 7075-T6)", part)]
    for x_ in (-2.5, 2.5):
        out.append(("H", f"{SCREW}x4 ISO 10642 countersunk, along block to the base (polished)", screw_csk(O + x_ * aH, nH, 1.6, 4.0, "")[2]))
    for g, n, s in up:
        if n.startswith(("BOTTOM", "UPPER ARM CUFF", "M4x6 ISO 10642 countersunk (upper cuff)")): continue
        out.append((g, n, s))
    cuff, crep = US.upper_cuff(None); out += cuff
    print(f"arm side: stage centre at s {sc:.1f}, v {vc:+.1f} on BOTTOM (cut at {AE.S_CUT:g}); BOTTOM + base fused: valid {part.isValid()}, "
          f"solids {len(part.Solids())}", flush=True)
    return out, dict(stage_on_bottom=dict(s=sc, v=vc), bottom_cut_s=AE.S_CUT, fused_valid=part.isValid(), fused_solids=len(part.Solids()), upper_cuff=crep)


# ---------------------------------------------------------------------------------------------------- kinematic check
def check(M, dd, poses_named):
    """posed by clips.json-style frame dicts (scene_export.frame_xforms) vs the model's own member transforms: the model's
    metal samples (hubs 1-3 faces, the neck, the bridge) vs the built parts of their member; signed: > 0 = the sample is
    outside the built metal by that much. Links: the bar vs the model's strap samples (shape change, reported apart)."""
    import scene_export as SE, igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); want = np.array([p for _, p in poses_named], float)
    K = L1B.chain(M, want); L1B.swap_in(M, K); grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 4: "l4", 5: "H"}; out = []
    for i, (nm, pz) in enumerate(poses_named):
        fr = L1B.REF.frame_dict(K, i, pz, pz, False); X, _ = SE.frame_xforms(fr); meshes = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or "screw" in node.lower(): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m)
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        res = {}
        for name, (mem, Xp) in [(k, v) for k, v in M.rigid.items() if k in ("hub1", "hub2", "hub3", "neck", "bridge")] + list(M.link_pts.items()):
            Pw = M.world(mem, i, Xp); g = "l1" if name == "hub1" else grp_of[mem]; mm = meshes[g]
            sd = igl.signed_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(mm.vertices, float), np.ascontiguousarray(mm.faces, np.int64))[0]
            res[name] = dict(outside_max=round(float(sd.max()), 4), abs_max=round(float(np.abs(sd).max()), 4))
        ok = all(v["outside_max"] <= 0.5 for k, v in res.items() if k not in ("L1", "L2"))
        out.append(dict(pose_name=nm, pose=[round(float(x), 1) for x in pz[:3]], closes=bool(K["ok"][i] and K["sok"][i]), res_deg=round(float(K["res"][i]), 4),
                        slides=[round(float(x), 2) for x in K["s"][i]], samples=res, within_0p5=ok))
        print(f"  check {nm:28s} {np.round(pz[:3], 1)} closes {out[-1]['closes']}: " + ", ".join(f"{k} {v['outside_max']:+.3f}" for k, v in res.items())
              + f" -> {'OK' if ok else 'OVER 0.5'}", flush=True)
    return out


def clip_picks(C):
    """(label, clip index, frame index) of followed frames of clips.json: rest, the peak of every clip (highest elevation,
    for Reach back pocket the most extended), the middle of Raise overhead"""
    names = [c["name"] for c in C["clips"]]; out = [("rest (first frame)", 0, 0)]
    for ci, cl in enumerate(C["clips"]):
        fr = [(fi, f) for fi, f in enumerate(cl["frames"]) if not f["held"]]
        if not fr: continue
        if cl["name"] == "Reach back pocket": fi = max(fr, key=lambda x: abs(x[1]["p"][0]) + abs(x[1]["p"][2]))[0]
        else: fi = max(fr, key=lambda x: x[1]["p"][1])[0]
        out.append((f"{cl['name']} peak", ci, fi))
        if cl["name"] == "Raise overhead": out.append(("Raise overhead middle", ci, fr[len(fr) // 2][0]))
    return out


def check_clips(M, dd, parts_local, mv):
    """the built parts posed by clips.json (scene_export.frame_xforms on the clip frame itself) vs the verified model at the
    same pose (L1B.chain on the frame's pose): (a) the model's metal samples (hubs 1-3, neck, bridge; links reported apart
    as the shape change) vs the posed built parts of their member, signed (> 0 = sample outside the built metal);
    (b) every custom part's vertices posed by the model's own member transforms vs posed by the clip frame (frame dev)"""
    import scene_export as SE, igl
    C = json.load(open(os.path.join(dd, "clips.json"))); src = trimesh.load(os.path.join(dd, "exo.glb"))
    grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 4: "l4", 5: "H"}; out = []
    loc = {}                                                                                # node -> (member, member-local vertices)
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g == "F" or n not in parts_local: continue
        T_, gn = src.graph[node]; V0 = trimesh.transform_points(src.geometry[gn].vertices, T_)
        mem = parts_local[n]
        if mem == 5: V0 = V0 @ L1B.HR - mv                                                  # x_H = HR (x + m)  ->  member-local x
        loc[node] = (mem, V0[:: max(1, len(V0) // 400)])
    for lab, ci, fi in clip_picks(C):
        f = C["clips"][ci]["frames"][fi]; pz = np.array([f["p"]], float); K = L1B.chain(M, pz); L1B.swap_in(M, K)
        X, _ = SE.frame_xforms(f); meshes = {}; fdev = 0.0
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F": continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t
            if "screw" not in node.lower() and not node.split("|")[1].startswith(("M4x6", "UPPER ARM", "TOP", "MIDDLE", "Hex", "IGUS", "5mm", "Revolve", "CirPattern")):
                meshes.setdefault(g, []).append(m)
            if node in loc:
                mem, Vl = loc[node]; Vm = M.world(mem, 0, Vl); R, t = X[g]
                Vc = (Vl if mem != 5 else (Vl + mv) @ L1B.HR.T) @ np.asarray(R).T + t
                fdev = max(fdev, float(np.abs(Vm - Vc).max()))
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}; res = {}
        for name, (mem, Xp) in [(k, v) for k, v in M.rigid.items() if k in ("hub1", "hub2", "hub3", "neck", "bridge")] + list(M.link_pts.items()):
            Pw = M.world(mem, 0, Xp); g = "l1" if name == "hub1" else grp_of[mem]; mm = meshes[g]
            sd = igl.signed_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(mm.vertices, float), np.ascontiguousarray(mm.faces, np.int64))[0]
            res[name] = dict(outside_max=round(float(sd.max()), 4), n=int(len(Pw)))
        ok = all(v["outside_max"] <= 0.5 for k, v in res.items() if k not in ("L1", "L2")) and fdev <= 0.5
        out.append(dict(label=lab, clip=C["clips"][ci]["name"], frame=fi, pose=[round(float(x), 1) for x in f["p"][:3]], closes=bool(K["ok"][0] and K["sok"][0]),
                        res_deg=round(float(K["res"][0]), 4), slides_model=[round(float(x), 3) for x in K["s"][0]], slides_clip=f["s"],
                        frame_dev_mm=round(fdev, 5), samples=res, within_0p5=ok))
        print(f"  clip check {lab:28s} {np.round(f['p'][:3], 1)} closes {out[-1]['closes']} frame dev {fdev:.1e} mm: "
              + ", ".join(f"{k} {v['outside_max']:+.3f}" for k, v in res.items()) + f" -> {'OK' if ok else 'OVER 0.5'}", flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_osn_k4216"); ap.add_argument("--k", type=int, default=4216)
    a = ap.parse_args(ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    M, rep0, e = L1B.fit((60, 160), a.k); D = M.D; u, c, F = D.u, D.c, M.f
    print(f"fit k {a.k}: gap {rep0['gap']} faces {np.round(F, 2)} tr {M.tr:.2f} ({time.time() - t0:.0f} s)", flush=True)
    AE.S_CUT = 255.0; AE.LAP_HOLES = []
    rep = dict(fit=dict(k=a.k, gap=rep0["gap"], faces=[float(x) for x in F], tr=float(M.tr)), style="user (line/arc sketches, extrudes, revolves, "
               "single-section sweeps on line/arc paths, rounds; no lofts)")
    parts = []                                                                              # (group, member, name, shape) member-local
    # hubs: v5 stack hardware (J3 about its offset line)
    for J, k_, lo, hi, mlo, mhi in (("J1", 0, "l1", "base", 1, 0), ("J2", 1, "l1", "l2", 1, 2), ("J3", 2, "l3", "l2", 3, 2)):
        for g, n, s in US.hardware(J, u[k_], F[k_], lo, hi):
            parts.append((g, mlo if g == lo else mhi, n, at(s, c[k_])))
    lk, rep["links"] = links(M); parts += lk
    m3, r3 = member3_and_stage(M); parts += m3; rep.update(r3)
    # link 1's heading about J1 in the base frame over the followed frames of the L1 clips (for the base tab)
    C = json.load(open(os.path.join(FULL, "designs", SRC, "clips.json"))); ex = unit(u[0]); ey1 = unit(u[1] - (u[1] @ ex) * ex); dirs = []
    for cl in C["clips"]:
        for f in cl["frames"]:
            if f["held"]: continue
            RS = np.array(f["G"]["base"]).reshape(3, 3); G1 = np.array(f["G"]["l1"]).reshape(3, 3); dirs.append((RS.T @ G1) @ ey1)
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    bp, rep["base"] = base_part(M, E, np.array(dirs)); parts.append(bp)
    arm, rep["arm side"] = arm_side(M)
    # ---- export: member-local (= model rest frame) for members 0-4, H = HR (x + m) for member 5, user parts as they are
    mv = D.m[0] * D.sa + D.m[1] * D.st + D.m[2] * D.sn
    allp = []
    for g, mem, n, s in parts:
        allp.append((g, n, xform(s, L1B.HR, L1B.HR @ mv) if mem == 5 else s))
    allp += arm
    for f in os.listdir(os.path.join(dd, "step")): os.remove(os.path.join(dd, "step", f))
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s) in enumerate(allp):
        user = n.startswith(USER); custom = not user and "screw" not in n.lower() and "M4x6" not in n
        if custom:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        fine = not user
        vs, fs = s.tessellate(0.02 if fine else 0.08, 0.15 if fine else 0.4)
        m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        if user: mat, rho = "user part", None
        elif "bearing" in n: mat, rho = "bearing steel", 7.8
        elif "17-4PH" in n: mat, rho = "17-4PH", 7.8
        elif "catalogue" in n: mat, rho = "steel (catalogue guide)", 7.85
        elif "screw" in n.lower() or "M4x6" in n: mat, rho = "stainless (polished)", 7.9
        elif "7075-T6" in n: mat, rho = "7075-T6 (BOTTOM merged with the stage base)", 2.81
        elif n.startswith("UPPER ARM CUFF"): mat, rho = "AlSi10Mg", 2.68
        else: mat, rho = "Ti-6Al-4V", 4.43
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids())))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L2 user-style", FACES={str(j + 1): round(float(F[j]), 2) for j in range(3)}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    for f in ("clips.json", "workspace.json"): shutil.copy(os.path.join(FULL, "designs", SRC, f), os.path.join(dd, f))
    d = json.load(open(os.path.join(FULL, "designs", SRC, "design.json")))
    d.update(id=a.out, label=f"offset-skin-normal-3r k {a.k}, full CAD in the user's style", level="L2 user-style (full CAD of the generation-2 winner)",
             built_with="pipeline/conformal/param_cad/user_style_osn.py (user_style.py parts: line/arc sketches extruded / swept, planform pads, v5 joints; "
                        "real RSR3M guides; BOTTOM fused with the stage base) on the L1 design's frames and clips (l1_offset-skin-normal-3r)",
             l1_design=SRC)
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_base=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in pf if not p["user"] if False] if False else [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass custom {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    # ---- kinematic check: >= 5 poses incl. overhead and behind the back (the model's own chain; none held)
    poses = [("rest (bench first)", [30.0, 3.0, -30.0, 0, 0]), ("forward reach", [60.0, 90.0, 0.0, 0, 0]), ("abduction 90", [0.0, 90.0, 30.0, 0, 0]),
             ("overhead (bench highest)", [45.0, 165.0, -90.0, 0, 0]), ("overhead raise elev 150", [30.0, 150.0, -60.0, 0, 0]),
             ("behind the back (pocket)", [-80.0, 39.0, 101.0, 0, 0]), ("behind the back (red-team pinch)", [-75.0, 45.0, 120.0, 0, 0])]
    rep["check"] = check(M, dd, poses)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
