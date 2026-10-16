"""Full user-style CAD of skin-normal-3r-pin-knee (docs/concepts/skin-normal-3r-pin-knee.md) - the generation-3 winner.

The kinematics are EXACTLY the verified model's: the shape is the model's own fit under the frozen-shape protocol
(build_pinknee_l1.fit: Bench(60,160) fast, the shape the verifier wore on Bench(110,360) exact), every part is designed in
its member's home frame (= the scapula frame at rest, GH = origin) and exported in its member's group (base, l1, l2,
l3 = hub 3's member, l4 = the knee link, H = arm-fixed at x_H = HR x), and clips.json / workspace.json are the L1
design's (l1_skin-normal-3r-pin-knee: "G" + "T" per group = the model's own Model.T(m, i)). The configuration is an
INPUT (--params JSON | --params-file F | --k K | default: docs/concepts/rows/<id>.json best_params), so a polished config
drops in; the L1 design dir named by --l1 must have been built from the same config (its clips carry the frames).

Parts (user style, user_style.py; no lofts - line / tangent-arc sketches, extrudes, revolves, single-section sweeps along
line / arc paths, rounds):
  hubs      J1, J2, J3: the v5 O20 stack exactly as user_style.py builds it (pads + integral O7 pins on the lower member,
            O20 ring + M18 spigot + bore on the upper member, 2x MR117-2RS, 17-4PH outer spacer, ground inner spacer, M7x0.5
            Ti ring nut, threaded G2 dome cap); J3 about its OFFSET line (foot point c3, tilted b3): built about GH, moved by
            c3. Per joint (the params' rad1..rad3 / --hubs): slim O15 / O17 = the same MR117-2RS pair, spacers, ring nut and
            12.25 mm stack in a plain tube of the hub radius with a press-fit O13 cap plug + O(2R) flange (no M18 spigot).
  links     bent 8 x 3 bars (user_style.bar_swept) fitted to stay at or above the L1 strap undersides (the model's fitted
            rows + the L1's hub-rim lift) and hug them (user_style_osn's link fit: the CAD standard's 35 deg ramp first, the
            model's steeper ramps only where 35 deg has no chain); planform pads, the user-style pocket, 0.5 mm rounds.
            Link 2 flies over the knee and the pad (the model's L2 rows avoid both boxes).
  member 3  hub 3's lower disc + integral O7 pin + the E strap (ONE side-view sketch of lines and tangent arcs in the plane
            (c3; eE, sn), extruded 8 mm: its underside = the upper hull of the model's fitted E profile, 3 mm thick, the top
            stepping down to the boss top tr + tp inside the knee link's reach) + the E boss (O12 x tp at pin a, tr) +
            pin a's integral O4 Ti pin.
  knee      the knee link: a flat Ti plate, planform = 10 wide stadium (R5 ends, inside the model's (lc + 12) x 10 box), tp
            thick at tr + tp + 0.5, O5.5 bores with iglidur sleeves, O8 x 0.7 clip counterbores (pins end flush).
  pins a, b IGLIDUR-PIN stack 5.0 mm (tools/hardware_catalogue.json): integral O4 h9 Ti pin on the lower plate (E boss /
            arm pad), iglidur thrust washer O4.2 x O8 x 0.5 in the 0.5 mm running gap, iglidur sleeve O4 x O5.5 x 1.55 pressed
            in the knee link, DIN 6799 RS3.2 E-clip (A2) in a 0.7 mm counterbore - nothing stands above the 5.0 mm stack.
  arm side  the arm pad (O12 at pin b) + the pad mount (the L1's slab footprint, 12 wide, at the pad level) as one planform
            sketch, a riser under BOTTOM's cut end inside BOTTOM's own footprint, fused with the user's BOTTOM (cut at s
            255, as the L1) into ONE 5-axis part; the upper-arm cuff from one line/arc sketch (user_style.upper_cuff, the
            anterior arc stopped at 12 deg as user_style_osn); the user's other arm parts unchanged.
  base      the scapula base: J1 upper ring + a 16 wide tab with 2x M4 counterbored to the user's scapula handler. The tab
            is chosen from headings x terminal angles by (1) the skin envelope (>= 0.5 mm over the 2 mm clearance), (2) NO
            contact with the posed link 1 over every clip frame (>= 0.5 mm, built meshes: gen-2's tab hit link 1 at 0.85
            mm), (3) the lowest mean clearance (gen-2's climbing tab sat at a median 42 mm and cost R1 29.7 points).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_pinknee.py [--out user_pinknee_k4598]
        [--params JSON | --params-file F | --k K] [--hubs 10,10,10] [--l1 l1_skin-normal-3r-pin-knee]
"""
import argparse, json, math, os, shutil, sys, time
ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import user_style as US                                                                   # noqa: E402  (param_build, sketch2d, arm_end)
REPO = US.FR.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_pinknee_l1 as PK                                                             # noqa: E402  (the model fit, link rows, frames)
import numpy as np, cadquery as cq, trimesh                                               # noqa: E402
PB, SK, AE, LV, unit, V, xform = US.PB, US.SK, US.AE, US.LV, US.unit, US.V, US.xform
T, W, L_SEAT = US.T, US.W, US.L_SEAT
FULL = US.FR.FULL
CACHE = os.path.join(REPO, ".cache", "user_style_pinknee_fits.json")
CUFF_WRAP_NEG = 12.0                                                                       # deg (user_style_osn: the forearm cuff folds onto the anterior arc)
S_CUT = 255.0                                                                              # BOTTOM's cut (as the L1's user parts)
PIN_D, SLEEVE_D, CB_D, CB_H, CLIP_T, GROOVE_D = 4.0, 5.5, 8.0, 0.7, 0.6, 3.2            # pin stack hardware (mm)
KNEE_R = 5.0                                                                               # (unused since the R1-corner plate)
KNEE_CR = 1.0                                                                              # knee link planform corner radius
TI, STEEL, IGL = 4.43, 7.85, 1.46


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
        wp = wp.lineTo(*t1) if mid is None else wp.lineTo(*t1).threePointArc(tuple(mid), tuple(t2))
    return wp.close()


def safe_radii(pts, want):
    """per-vertex corner radius <= want that fits (tangent length <= 45 % of both adjacent sides); 0 for turns < 1 deg"""
    P = [np.asarray(p, float) for p in pts]; n = len(P); out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]; u1, u2 = unit(a - b), unit(c - b)
        th = math.acos(np.clip(u1 @ u2, -1, 1))
        if th > math.radians(179.0): out.append(0.0); continue
        lim = 0.45 * min(np.linalg.norm(a - b), np.linalg.norm(c - b)) * math.tan(th / 2)
        w = want[i] if isinstance(want, (list, tuple)) else want
        out.append(round(min(w, lim), 3) if min(w, lim) >= 0.05 else 0.0)
    return out


def plane(origin, xdir, ydir):
    xdir = unit(xdir); ydir = unit(ydir - (ydir @ xdir) * xdir)
    return cq.Plane(origin=tuple(map(float, origin)), xDir=tuple(map(float, xdir)), normal=tuple(map(float, np.cross(xdir, ydir))))


def prism(origin, xdir, ydir, pts, radii, h, both=False):
    """sketch (lines + tangent arcs) in the plane (origin, xdir, ydir), extruded h along xdir x ydir (both: +-h/2)"""
    wp = rounded_poly(plane(origin, xdir, ydir), pts, radii)
    return (wp.extrude(h / 2, both=True) if both else wp.extrude(h)).val()


def stadium(origin, xdir, ydir, L, r, h):
    """planform: two half circles of radius r, centres 0 and L along xdir, joined by tangent lines; extruded h"""
    wp = (cq.Workplane(plane(origin, xdir, ydir)).moveTo(0.0, -r).lineTo(L, -r).threePointArc((L + r, 0.0), (L, r))
          .lineTo(0.0, r).threePointArc((-r, 0.0), (0.0, -r)).close())
    return wp.extrude(h).val()


def disc(cen, ax, r, z0, z1):
    ax = unit(ax); return cq.Solid.makeCylinder(r, z1 - z0, V(np.asarray(cen) + z0 * ax), V(ax))


def rev(profile, cen, ax):
    """solid of revolution about the line (cen, ax); profile [(r, z)] with z along ax from cen"""
    return xform(cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(ax), np.asarray(cen, float))


def weld_open(m, tol=0.05):
    """weld vertices on open boundary edges within tol (mm) - OCC leaves 0.02 mm seams on glued bent bars (user_style_osn)"""
    from scipy.spatial import cKDTree
    from trimesh.grouping import group_rows
    w = m.copy(); w.merge_vertices(digits_vertex=6); w.update_faces(w.nondegenerate_faces()); w.remove_unreferenced_vertices()
    e = w.edges_sorted; ob = e[group_rows(e, require_count=1)]
    if not len(ob): return w
    bv = np.unique(ob); par = {int(v): int(v) for v in bv}
    def find(a_):
        while par[a_] != a_: par[a_] = par[par[a_]]; a_ = par[a_]
        return a_
    for i_, j_ in cKDTree(w.vertices[bv]).query_pairs(tol):
        ra, rb = find(int(bv[i_])), find(int(bv[j_])); par[max(ra, rb)] = min(ra, rb)
    mp = np.arange(len(w.vertices))
    for v_ in bv: mp[v_] = find(int(v_))
    F2 = mp[w.faces]; F2 = F2[(F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])]
    w2 = trimesh.Trimesh(w.vertices, F2, process=False); w2.remove_unreferenced_vertices()
    return w2 if w2.is_watertight or not m.is_watertight else m


def tess(s, fine=True):
    vs, fs = s.tessellate(0.02 if fine else 0.08, 0.15 if fine else 0.4)
    m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
    return weld_open(m) if fine else m


# ---------------------------------------------------------------------------------------------------- hubs (O20 v5 / slim)
# O20 = the v5 stack exactly as user_style.py builds it. Slim O15 / O17 (docs/concepts/spine-parked-j2-3r.md "Slim hub, hand
# calc"): the same MR117-2RS pair, spacers and M7x0.5 ring nut, the same 12.25 mm stack; the O20 M18 spigot + threaded cap do
# not fit, so the upper member is a plain tube of the hub radius up to F + 11.25 with an O13 counterbore, and the cap is a
# press-fit O13 annular plug (retains the upper outer ring, clears the ring nut) with an O(2R) x 1.0 flange to the crown.
SLIM_TOP, CAP_CB = 11.25, 6.5


def plate_R(k, level, sdir, w, R, t=T, L=L_SEAT, upper=False, rf=US.RF):
    if R == US.HUB_R and rf == US.RF: return US.plate_r(k, level, sdir, w, t=t, L=L, upper=upper)
    s = US.plate(k, level, sdir, w, t, L, R=R, rf=rf); k = unit(k); sd = unit(sdir - (sdir @ k) * k); top = (level + t) * k
    def skip(e):
        if not upper or e.geomType() != "CIRCLE": return False
        p = np.array(e.positionAt(0.5).toTuple()); return abs((p - top) @ k) < 1e-3 and abs(np.linalg.norm(p - (p @ k) * k) - R) < 1e-3
    return US.rounded(s, keep_plane=(level * k + L * sd, sd), skip=skip)


def upper_ring_R(k, F, R):
    if R == US.HUB_R: return US.upper_ring_r(k, F)
    z0, zt, r = LV["U0"] + T + F, SLIM_TOP + F, 0.5; q = 1 - math.sqrt(0.5)
    wp = (cq.Workplane("XZ").moveTo(4.0, z0).lineTo(R, z0).lineTo(R, zt - r).threePointArc((R - r * q, zt - r * q), (R - r, zt)).lineTo(4.0, zt).close())
    return xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k))


def bore_cutter_R(k, F, R):
    if R == US.HUB_R: return US.bore_cutter(k, F)
    return PB.revolved([(0, LV["U0"] - 1.0), (4.9, LV["U0"] - 1.0), (4.9, LV["L1"]), (5.5, LV["L1"]), (5.5, LV["U1"]), (CAP_CB, LV["U1"]),
                        (CAP_CB, SLIM_TOP + 1.0), (0, SLIM_TOP + 1.0)], k, F)


def ring_root_R(body, k, F, R):
    return US.ring_root_fillet(body, k, F) if R == US.HUB_R else body


def hardware_R(J, k, F, lower, upper, R):
    """the v5 stack's bearings, spacers, nut, cap (O20) - or, slim, the same minus the O20 cap plus the press-fit cap"""
    hw = US.hardware(J, k, F, lower, upper)
    if R == US.HUB_R: return hw
    hw = [h for h in hw if " cap " not in h[1]]
    cap = PB.revolved([(4.6, LV["U1"]), (CAP_CB - 0.01, LV["U1"]), (CAP_CB - 0.01, SLIM_TOP), (R - 0.5, SLIM_TOP), (R, SLIM_TOP + 0.5), (R, LV["top"] - 0.4),
                       (R - 0.4, LV["top"]), (0, LV["top"]), (0, SLIM_TOP + 0.05), (4.6, SLIM_TOP + 0.05)], k, F)
    return hw + [(upper, f"{J} cap O{2 * R:.0f} press-fit plug O13 + flange, retains the upper outer ring (Ti-6Al-4V) [slim hub]", cap)]


# ---------------------------------------------------------------------------------------------------- links
def l1_rows(M, lk, rows):
    """the L1 strap underside (build_pinknee_l1.link_solid's rows + hub-rim lift, per-joint hub radius): directions
    (q, n, 3), radii (q, n)"""
    D = M.D; u, c = D.u, D.c; F = M.f; UP = PK.UP; hr = M.hr
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): UP}
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r.copy() for _, _, r in rows]
    d_lo = unit(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
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
            sel = (off < hr[kk] + 2.5) & (den > 0.2)
            cols_r[q][sel] = np.maximum(cols_r[q][sel], (cen @ u[kk] + lv) / den[sel])
    J = np.arange(j0, j1 + 1)
    return np.array([cd[J] for cd in cols_d]), np.array([cr[J] for cr in cols_r])


BEND_R = 16.5                                                                              # centre-line R of a 3 mm bar bent to >= 15 mm inner radius (5 t)
CLIMBS = ((60.0, BEND_R), (60.0, 4.0))                                                     # user ruling 2026-10-16: ramps <= 60 deg near a hub, bends
                                                                                           # >= 15 mm inner on bent bars; tighter = 5-axis machined


def link_fit(label, ex, ey, start, end, Dq, Rq, t=T, climbs=CLIMBS):
    """bent-bar chain (start -> end poses in the plane (GH, ex, ey)) whose skin side stays >= the L1 strap underside
    (user_style_osn.link_fit: fairness weight 4, up to 5 arcs). The 2026-10-16 CAD ruling: ramps up to 60 deg; a bent
    3 mm Ti bar first (every bend >= 15 mm inner radius); only if no such chain exists, tighter transitions on a part
    5-axis machined from solid (fit['machined'] = True, stated on the part)"""
    th_q = np.arctan2(Dq @ ey, Dq @ ex); rho_q = Rq * np.hypot(Dq @ ex, Dq @ ey)
    th = th_q.mean(0); order = np.argsort(th); th = th[order]; need = rho_q.max(0)[order]
    clear = lambda U: np.hypot(U[:, 0], U[:, 1]) - np.interp(np.arctan2(U[:, 1], U[:, 0]), th, need)
    geo = f"{np.round(ex, 5).tolist()}|{np.round(ey, 5).tolist()}|{np.round(start, 4).tolist()}|{np.round(end, 4).tolist()}|{np.round(need, 3).tolist()}"
    key = f"{label}|hug60|" + "|".join(f"{cm:g},{rm:g}" for cm, rm in climbs) + "|" + geo
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    old = f"{label}|hug4|{geo}"                                                            # the previous run's (60, 4) machined fit of link 1
    if key not in cache and old in cache and cache[old].get("climb_limit") == 60.0 and cache[old].get("r_min") == 4.0 \
            and any(f"{label}|hug60|bent-fail|{cm:g}" in k_ for k_ in cache for cm, rm in climbs if rm == BEND_R):
        cache[key] = cache[old]
    if key in cache: fit = cache[key]; fit["segs"] = [tuple(x) for x in fit["segs"]]
    else:
        fits = {}
        for cm, rm in climbs:
            for n_ in (3, 4, 5):
                for sc_ in ((1.0,) if rm == BEND_R else (1.0, 0.5)):
                    fk = f"{label}|hug60|bent-fail|{cm:g}|{rm:g}|{n_}|{sc_}|{geo}" if rm == BEND_R else f"{key}|fail|{cm}|{rm}|{n_}|{sc_}"
                    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
                    if fk in cache: print(f"  {label}: {n_} arcs, climb {cm}, R >= {rm}, snap x{sc_}: {cache[fk]} (cached)", flush=True); e = cache[fk]
                    else:
                        try:
                            f_ = SK.fit_chain(start, end, clear, t, n_arcs=n_, climb_max=cm, r_min=rm, l_min=2.0, snap_scale=sc_, bend=4.0, seeds=16)
                            f_.update(climb_limit=cm, r_min=rm, l_min=2.0, snap_scale=sc_, bend=4.0); fits[n_] = f_; break
                        except RuntimeError as e_:
                            e = str(e_); print(f"  {label}: {n_} arcs, climb {cm}, R >= {rm}, snap x{sc_}: {e}", flush=True)
                            cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}; cache[fk] = e
                            os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(cache, open(CACHE, "w"), indent=0)
                    if "snapped" not in e: break
            if fits: break
        if not fits: raise RuntimeError(f"{label}: no chain stays above the L1 strap")
        bm = min(f_["mean_clear"] for f_ in fits.values())
        nb = min(n_ for n_, f_ in fits.items() if f_["mean_clear"] <= bm + 0.5); fit = fits[nb]
        fit = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in fit.items()}
        fit["segs"] = [(float(k), float(l)) for k, l in fit["segs"]]; fit["radii"] = [None if r is None else float(r) for r in fit["radii"]]
        cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}; cache[key] = fit
        os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(cache, open(CACHE, "w"), indent=0)
    P, H, _ = SK.sample(start, fit["segs"], 40); U = P - 0.5 * t * SK.normals(H); cl = clear(U)
    rr = [abs(r) for r in fit["radii"] if r is not None]; inner = min(rr) - t / 2 if rr else None
    machined = bool(inner is not None and inner < BEND_R - t / 2 - 1e-6)
    print(f"{label}: radii {[None if r is None else round(r, 1) for r in fit['radii']]}, lengths {[round(l, 1) for _, l in fit['segs']]}, "
          f"over the L1 underside min {cl.min():.2f} mean {cl.mean():.2f} max {cl.max():.2f} mm, max climb {fit['max_climb']:.1f} deg "
          f"(limit {fit.get('climb_limit', 35)}), min inner bend R {inner} -> {'5-axis machined from solid' if machined else 'bent 3 mm Ti bar'}", flush=True)
    return fit, dict(over_L1_min=float(cl.min()), over_L1_mean=float(cl.mean()), over_L1_max=float(cl.max()), min_inner_bend_mm=inner,
                     process="5-axis machined from solid Ti-6Al-4V (a bend below the 15 mm inner radius rule)" if machined
                     else "bent 3 mm Ti-6Al-4V bar (every bend >= 15 mm inner radius)")


def links(M):
    D = M.D; u, c = D.u, D.c; F = M.f; prof = PK.link_rows(M); out = []; rep = {}; hr = M.hr
    C = [c[k] + F[k] * u[k] for k in range(3)]
    # ---- link 1: lower at J1 and J2 (both axes through GH), plane span(u1, u2)
    ex = unit(u[0]); ey = unit(u[1] - (u[1] @ ex) * ex); phi = math.acos(np.clip(unit(u[1]) @ ex, -1, 1))
    ha, hb = F[0] + T / 2, F[1] + T / 2
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    Dq, Rq = l1_rows(M, *prof["L1"]); fit = None
    # seats: the standard's 14 mm pads (R6 planform rounds) first; if no chain climbs from J1's seat to J2's (k4598: J2's face
    # is 10.9 mm above J1's within 40 deg, the L1 strap needs ~55 deg near J2), 12 / 11 mm pads with R3 planform rounds
    for Ls, rf in ((L_SEAT, US.RF), (12.0, 3.0), (11.0, 2.0)):
        start = (ha, Ls, math.pi / 2); end = (*(B + Ls * back), math.pi / 2 + phi)
        try: fit, r1 = link_fit("link 1" if Ls == L_SEAT else f"link 1 (seat {Ls:g})", ex, ey, start, end, Dq, Rq); break
        except RuntimeError as e_: print(f"  link 1: seat {Ls:g}: {e_}", flush=True)
    if fit is None: raise RuntimeError("link 1: no chain at any seat length")
    body = US.bar_swept(ex, ey, start, fit["segs"])
    he = SK.end_pose(start, fit["segs"])[2]; sd_b = -(math.cos(he) * ex + math.sin(he) * ey)
    body = US.glue(plate_R(u[0], F[0], ey, W, hr[0], L=Ls, rf=rf), body)
    body = US.glue(body, plate_R(u[1], F[1], sd_b, W, hr[1], L=Ls, rf=rf))
    r1.update(seat_mm=Ls, pad_round_mm=rf)
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"])
    for k_ in (0, 1): body = body.fuse(US.lower_pin(u[k_], F[k_]))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l1", 1, f"D8-02 link 1: 8x3 bar on a line/arc chain + J1/J2 pads + integral O7 pins ({r1['process']})", body))
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
    back_w = math.sin(phi) * ex - math.cos(phi) * ey
    body = US.glue(plate_R(u[1], F[1] + LV["U0"], ey, W, hr[1], upper=True), body)
    body = US.glue(body, at(plate_R(u[2], F[2] + LV["U0"], back_w, W, hr[2], L=L_SEAT + 0.6, upper=True), c[2]))
    body, npk = US.with_pocket_r(body, ex, ey, start, fit["segs"])
    body = ring_root_R(US.glue(body, upper_ring_R(u[1], F[1], hr[1])), u[1], F[1], hr[1])
    body = US.glue(body, at(upper_ring_R(u[2], F[2], hr[2]), c[2]))
    body = body.cut(bore_cutter_R(u[1], F[1], hr[1])).cut(at(bore_cutter_R(u[2], F[2], hr[2]), c[2]))
    body = body.clean() if body.clean().isValid() else body
    out.append(("l2", 2, f"D8-03 link 2: 8x3 bar on a line/arc chain + J2/J3 hubs, flies over the knee and the pad ({r2['process']})", body))
    gap = float(abs((p3 - (p3 @ ex) * ex - (p3 @ ey) * ey) @ nP))
    rep["link 2"] = dict(fit, **r2, pocket=npk, u3_lean_out_of_plane_deg=lean, j3_seat_offset_mm=gap, valid=body.isValid(), solids=len(body.Solids()))
    print(f"  link 2: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}; u3 leans {lean:.2f} deg out of "
          f"the bar plane, J3 seat centre {gap:.2f} mm off it", flush=True)
    return out, rep


# ---------------------------------------------------------------------------------------------------- pin hardware
def pin_stack(name, cen, sn, tr, tp, lower_grp, knee_grp):
    """IGLIDUR-PIN at (cen, sn): integral O4 pin (returned as a solid to fuse into the lower plate), thrust washer, sleeve
    in the knee link, E-clip. Levels along sn: lower plate tr..tr+tp, gap ..+0.5, knee link tr+tp+0.5..tr+2tp+0.5."""
    zk0 = tr + tp + PK.RUN; zk1 = zk0 + tp; zc0 = zk1 - CB_H                               # knee link, clip seat
    r = PIN_D / 2; rg = GROOVE_D / 2
    pin = rev([(0, tr + 0.8), (r, tr + 0.8), (r, zc0), (rg, zc0), (rg, zc0 + CLIP_T), (r, zc0 + CLIP_T), (r - 0.2, zk1), (0, zk1)], cen, sn)
    hw = [(lower_grp, f"pin {name}: iglidur thrust washer O4.2 x O8 x 0.5 (GTM class, 0.5 mm running gap) [est size, confirm]",
           rev([(2.1, tr + tp), (4.0, tr + tp), (4.0, tr + tp + PK.RUN), (2.1, tr + tp + PK.RUN)], cen, sn)),
          (knee_grp, f"pin {name}: iglidur G sleeve O4 x O5.5 x {zc0 - zk0:.2f} (GSM-0405 class, cut to length) [est, confirm]",
           rev([(r + 0.01, zk0), (SLEEVE_D / 2, zk0), (SLEEVE_D / 2, zc0), (r + 0.01, zc0)], cen, sn))]
    # DIN 6799 E-clip: a C ring O3.2 / O7.3 x 0.6 with a 3.2 mm mouth
    clip = rev([(rg + 0.01, zc0), (3.65, zc0), (3.65, zc0 + CLIP_T), (rg + 0.01, zc0 + CLIP_T)], cen, sn)
    e, f = (PB.axis_frame(sn)[:, 0], PB.axis_frame(sn)[:, 1])
    cut = prism(np.asarray(cen) + (zc0 - 0.5) * sn, e, f, [(1.2, -1.6), (4.5, -1.6), (4.5, 1.6), (1.2, 1.6)], [0, 0, 0, 0], CLIP_T + 1.0)
    clip = clip.cut(cut)
    hw.append((lower_grp, f"pin {name}: DIN 6799 RS3.2 E-clip, A2 stainless (polished, screw-class hardware), seated in the knee link's O8 x 0.7 counterbore", clip))
    return pin, hw


# ---------------------------------------------------------------------------------------------------- member 3 + knee
def upper_hull(x, z):
    """the smallest concave polyline above the points (x sorted)"""
    H = []
    for p in zip(x, z):
        while len(H) >= 2 and ((H[-1][0] - H[-2][0]) * (p[1] - H[-2][1]) - (H[-1][1] - H[-2][1]) * (p[0] - H[-2][0])) >= 0: H.pop()
        H.append(p)
    return H


def member3(M):
    """hub 3's lower disc + O7 pin, the E strap (one side-view sketch), the E boss + pin a; returns parts, report"""
    D = M.D; P = D.p; u, c = D.u, D.c; F3 = M.f[2]; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; r3 = M.hr[2]
    eE = fr["eE"]; lE = float(P["lE"]); c3 = c[2]; BR = PK.BOSS_R
    assert abs(u[2] @ sn - 1) < 1e-6, "member 3 assumes J3 = the knee plane normal"
    xs_m = np.unique(np.round(M._Ex, 6)); hx_m = np.array([M.hEx[np.isclose(M._Ex, v)].max() for v in xs_m])
    x_rim = lE - BR
    X = np.r_[r3, xs_m]; Z = np.r_[F3, hx_m]
    hull = upper_hull(X, Z + 0.02)                                                         # the model's stations (2 mm), then its own
    hull = [(float(x_), float(max(z_, F3))) for x_, z_ in hull] + [(float(x_rim), float(tr))]   # <= 60 deg step to the boss level
    # top: 3 mm over the underside (vertical offset / cos(slope) >= 3 normal), capped at the boss top tr + tp (the knee link
    # rides 0.5 mm above it within its reach of pin a)
    ztop_cap = tr + tp
    xx = np.linspace(r3, x_rim, 400); zu = np.interp(xx, [h[0] for h in hull], [h[1] for h in hull])
    sl = np.gradient(zu, xx); zt = np.minimum(zu + T / np.cos(np.arctan(sl)), ztop_cap)
    # top polyline: offset of the hull vertices while below the cap, then the cap
    top = []
    for x_, z_ in hull:
        zz = min(float(np.interp(x_, xx, zu + T / np.cos(np.arctan(sl)))), ztop_cap)
        top.append((x_, zz))
    ic = np.nonzero(zu + T / np.cos(np.arctan(sl)) >= ztop_cap)[0]
    x_cap = float(xx[ic[0]]) if len(ic) else x_rim
    top = [(r3 + 0.2, F3 + T)] + [p for p in top if r3 + 1.0 < p[0] < x_cap - 0.3] + [(x_cap, ztop_cap)]   # <= the J3 pad top inside hub 3
    under = [(r3 - 2.0, F3)] + hull + [(lE, tr)]
    pts = under + [(lE, tr + tp)] + list(reversed(top)) + [(r3 - 2.0, F3 + T)]
    # drop near-duplicate vertices
    clean = [pts[0]]
    for p in pts[1:]:
        if np.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 0.05: clean.append(p)
    pts = clean
    rad = safe_radii(pts, 1.0)
    for i, p in enumerate(pts):                                                            # sharp where the sketch meets the disc / boss
        if p[0] <= r3 - 2.0 + 1e-6 or p[0] >= lE - 1e-6: rad[i] = 0.0
    side = prism(c3, eE, sn, pts, rad, W, both=True)
    m3 = disc(c3, u[2], r3, F3, F3 + T).fuse(side)
    boss = disc(fr["A0"], sn, BR, tr, tr + tp); m3 = m3.fuse(boss)
    m3 = m3.fuse(at(US.lower_pin(u[2], F3), c3))
    pin, hw = pin_stack("a", fr["A0"], sn, tr, tp, "l3", "l4")
    m3 = m3.fuse(pin)
    m3 = m3.clean() if m3.clean().isValid() else m3
    out = [("l3", 3, "D8-04 member 3: J3 disc + integral O7 pin, E strap (one side-view sketch of lines and tangent arcs, 8 x 3, its top stepping to the "
                     f"boss), E boss O12 x {tp} + integral O4 pin a (Ti-6Al-4V)", m3)]
    out += [(g, 3 if g == "l3" else 6, n, s) for g, n, s in hw]
    rep = dict(underside_hull=[[round(a, 2), round(b, 2)] for a, b in hull], top_cap_from_x=round(x_cap, 2), sketch_vertices=len(pts),
               radii=[r for r in rad if r > 0], valid=m3.isValid(), solids=len(m3.Solids()))
    print(f"member 3: E underside hull {len(hull)} vertices ({hull[0][1]:.2f} -> {hull[-1][1]:.2f}), top capped at tr + tp from x {x_cap:.2f} "
          f"(boss rim {x_rim:.2f}); valid {m3.isValid()}, solids {len(m3.Solids())}", flush=True)
    return out, rep


def knee_link(M):
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"])
    z0 = tr + tp + PK.RUN; A = fr["A0m"]; Bp = fr["Bm"]; eK, nK = fr["eK"], fr["nK"]
    assert np.linalg.norm(A + lc * eK - Bp) < 1e-6
    # planform: the model's knee box (lc + 2 BOSS_R) x KNEE_W, pins BOSS_R from its ends, corners R1 (lines + tangent arcs):
    # every model sample of the knee link lies within 0.41 mm of it (a stadium with R5 ends left the box corners 2 mm out)
    e_ = PK.BOSS_R; hw_ = PK.KNEE_W / 2
    k = prism(A + z0 * sn, eK, nK, [(-e_, -hw_), (lc + e_, -hw_), (lc + e_, hw_), (-e_, hw_)], [KNEE_CR] * 4, tp)
    for cen in (A, Bp):
        k = k.cut(disc(cen, sn, SLEEVE_D / 2, z0 - 1, z0 + tp + 1)).cut(disc(cen, sn, CB_D / 2, z0 + tp - CB_H, z0 + tp + 1))
    k = k.clean() if k.clean().isValid() else k
    Lk = lc + 2 * PK.BOSS_R
    print(f"knee link: plate {Lk:.1f} x {PK.KNEE_W:.0f} x {tp} (R{KNEE_CR:g} corners), valid {k.isValid()}, solids {len(k.Solids())}", flush=True)
    return ("l4", 6, f"D8-05 knee link: flat plate {Lk:.1f} x {PK.KNEE_W:.0f} x {tp} (lines + R{KNEE_CR:g} arcs), O5.5 sleeve bores, O8 x 0.7 clip "
                     "counterbores (Ti-6Al-4V)", k)


# ---------------------------------------------------------------------------------------------------- arm side
def arm_side(M, mount_rep):
    """arm pad + pad mount (one planform at the pad level, the L1 slab footprint) + a riser inside BOTTOM's footprint, fused
    with BOTTOM (cut at s 255) and pin b's integral pin; built in the canonical arm frame, exported x_H = HR x"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; Bm = fr["Bm"]; HR = PK.HR
    da = np.array(mount_rep["dir_along_across"]); ex = unit(da[0] * D.sa + da[1] * D.st); ey = np.cross(sn, ex)
    L = float(mount_rep["length"])
    AE.S_CUT = S_CUT; AE.LAP_HOLES = []
    up = AE.user_parts()
    bot = [s for g, n, s in up if n.startswith("BOTTOM")][0]
    botC = xform(bot, HR.T)                                                                # rest (H) -> canonical arm frame
    CBc, uBc, vBc, aBc = HR.T @ AE.CB, HR.T @ AE.uB, HR.T @ AE.vB, HR.T @ AE.axB
    best = None
    for Lx in (L, L + 3.0, L + 6.0, L + 9.0):
        wp = (cq.Workplane(plane(Bm + tr * sn, ex, ey)).moveTo(0.0, -PK.PAD_R).lineTo(Lx - 1.0, -PK.PAD_R).threePointArc(
              (Lx - 1.0 + 1.0 * math.sin(math.pi / 4), -PK.PAD_R + 1.0 - 1.0 * math.cos(math.pi / 4)), (Lx, -PK.PAD_R + 1.0)).lineTo(Lx, PK.PAD_R - 1.0)
              .threePointArc((Lx - 1.0 + 1.0 * math.sin(math.pi / 4), PK.PAD_R - 1.0 + 1.0 * math.cos(math.pi / 4)), (Lx - 1.0, PK.PAD_R))
              .lineTo(0.0, PK.PAD_R).threePointArc((-PK.PAD_R, 0.0), (0.0, -PK.PAD_R)).close())
        slab = wp.extrude(tp).val()
        # riser: the slab's last 10 mm extruded up to 0.5 mm into BOTTOM's web, trimmed to BOTTOM's own planform (s <= cut,
        # |v| <= 14.5): no metal outside BOTTOM's footprint above the slab
        riser = prism(Bm + (tr + tp - 0.2) * sn, ex, ey, [(Lx - 10.0, -PK.PAD_R), (Lx, -PK.PAD_R), (Lx, PK.PAD_R), (Lx - 10.0, PK.PAD_R)], [0, 0, 0, 0], 12.0)
        box = prism(CBc + (S_CUT - 40.0) * uBc - 14.5 * vBc + (-4.9) * aBc, uBc, vBc, [(0, 0), (40.0 - 0.01, 0), (40.0 - 0.01, 29.0), (0, 29.0)], [0, 0, 0, 0],
                    14.2, both=True)                                                       # ax -12 .. 2.2: 0.5 mm into BOTTOM's web (1.7 .. 3.7)
        riser = riser.intersect(box)
        vol = float(riser.Volume()) if riser.Solids() else 0.0
        ov = float(slab.intersect(botC).Volume())
        print(f"  pad mount {Lx:.1f} mm: slab-in-BOTTOM {ov:.1f} mm3, riser {vol:.1f} mm3", flush=True)
        if vol > 60.0 or ov > 60.0: best = (Lx, slab, riser, vol, ov); break
        best = (Lx, slab, riser, vol, ov)
    Lx, slab, riser, vol, ov = best
    pin, hw = pin_stack("b", Bm, sn, tr, tp, "H", "l4")
    part = slab
    if vol > 1.0: part = part.fuse(riser)
    part = part.fuse(pin).fuse(botC)
    part = part.clean() if part.clean().isValid() else part
    print(f"arm side: BOTTOM + pad mount: valid {part.isValid()}, solids {len(part.Solids())}", flush=True)
    out = [("H", 5, f"D8-06 BOTTOM + arm pad + pad mount, one 5-axis part (user's bar cut at s {S_CUT:g}; O12 pad at pin b + integral O4 pin, "
                     f"{tp} mm mount {Lx:.1f} long at the pad level, riser into BOTTOM's channel; 7075-T6)", part)]
    out += [(g, 5 if g == "H" else 6, n, s) for g, n, s in hw]
    users = []
    for g, n, s in up:
        if n.startswith(("BOTTOM", "UPPER ARM CUFF", "M4x6 ISO 10642 countersunk (upper cuff)")): continue
        users.append((g, n, s))
    cuff, crep = US.upper_cuff(None, wrap_neg_deg=CUFF_WRAP_NEG); users += cuff
    return out, users, dict(mount_length=Lx, slab_in_bottom_mm3=round(ov, 1), riser_mm3=round(vol, 1), fused_valid=part.isValid(),
                            fused_solids=len(part.Solids()), bottom_cut_s=S_CUT, upper_cuff=crep)


# ---------------------------------------------------------------------------------------------------- scapula base
def link1_posed_check(tab_mesh, l1_mesh, frames):
    """min clearance (mm) between the base tab and link 1 over the clip frames (both built meshes, signed: < 0 = inside)"""
    import igl
    Vt, Ft = np.ascontiguousarray(tab_mesh.vertices, float), np.ascontiguousarray(tab_mesh.faces, np.int64)
    V1, F1 = np.ascontiguousarray(l1_mesh.vertices, float), np.ascontiguousarray(l1_mesh.faces, np.int64)
    St = np.r_[Vt, trimesh.sample.sample_surface_even(tab_mesh, 1500, seed=2)[0]]
    S1 = np.r_[V1[:: max(1, len(V1) // 3000)], trimesh.sample.sample_surface_even(l1_mesh, 3000, seed=2)[0]]
    worst = 1e9
    for Gb, Tb, G1, T1 in frames:
        R = Gb.T @ G1; t = Gb.T @ (T1 - Tb)                                                 # l1 local -> base local
        A = S1 @ R.T + t
        lo, hi = Vt.min(0) - 3, Vt.max(0) + 3; sel = np.all((A > lo) & (A < hi), 1)
        if sel.any(): worst = min(worst, float(igl.signed_distance(np.ascontiguousarray(A[sel]), Vt, Ft)[0].min()))
        B = (St - t) @ R                                                                    # base local -> l1 local
        lo, hi = V1.min(0) - 3, V1.max(0) + 3; sel = np.all((B > lo) & (B < hi), 1)
        if sel.any(): worst = min(worst, float(igl.signed_distance(np.ascontiguousarray(B[sel]), V1, F1)[0].min()))
    return worst


def base_part(M, E, l1_body, frames):
    """J1 upper ring + tab (16 wide) to the user's scapula handler, 2x M4 counterbored; candidates = headings about J1 x
    terminal angles off J1 (0 = flat in the J1 upper seat plane); feasible = >= 0.5 mm over the scapula-frame skin envelope
    (2 mm clearance) and >= 0.5 mm from the posed link 1 over every clip frame; best = lowest mean envelope clearance"""
    D = M.D; k1 = unit(D.u[0]); F1 = M.f[0]; up_mid = LV["U0"] + T / 2; WT = 16.0
    d0 = unit(np.array([0.0, 0.6, -0.8])); d0 = unit(d0 - (d0 @ k1) * k1); d1 = np.cross(k1, d0)
    l1m = tess(l1_body); cands = []
    for al in np.arange(-180.0, 180.0, 10.0):
        td = math.cos(math.radians(al)) * d0 + math.sin(math.radians(al)) * d1
        fld = US.PolarField(E, "S", np.eye(3), k1, td, -5.0, 75.0, WT)
        # flat: pad (14) + terminal (14 + round end 8) in the J1 upper seat plane, underside at F1 + U0
        Uf = np.array([(F1 + LV["U0"], x_) for x_ in np.linspace(0, 36, 37)])
        cf = fld(Uf)
        if cf.min() >= 0.5: cands.append(dict(al=al, th=0.0, h=F1 + up_mid, score=float(cf.mean()), td=td, fld=fld))
        for thd in (10.0, 20.0, 30.0):
            th = math.radians(thd)
            for h in np.arange(F1 + up_mid, F1 + 40, 0.5):
                P0 = h * np.array([math.cos(th), math.sin(th)]); hd = np.array([-math.sin(th), math.cos(th)])
                U = np.array([P0 + s_ * hd for s_ in np.linspace(0, 22, 12)]) - (T / 2) * np.array([math.cos(th), math.sin(th)])
                cu = fld(U)
                if cu.min() >= 0.5:
                    cands.append(dict(al=al, th=thd, h=float(h), score=float(cu.mean()) + 0.5 * (h - F1 - up_mid), td=td, fld=fld)); break
    assert cands, "base tab: no candidate clears the skin envelope"
    cands.sort(key=lambda c_: c_["score"]); tried = []
    for cd in cands[:24]:
        al, thd, ht, ey_, fld = cd["al"], cd["th"], cd["h"], cd["td"], cd["fld"]; th = math.radians(thd)
        try:
            body = plate_R(k1, F1 + LV["U0"], ey_, WT, M.hr[0], upper=True)
            if thd == 0.0:
                o_mid = (F1 + up_mid) * k1 + L_SEAT * ey_; nrm = k1; sd = ey_; fit = None
            else:
                start = (F1 + up_mid, L_SEAT, math.pi / 2); end = (*(ht * np.array([math.cos(th), math.sin(th)])), th + math.pi / 2); fit = None
                for cm, rm in ((35.0, 12.0), (45.0, 6.0), (60.0, 4.0)):
                    for n_ in (2, 3):
                        try: fit = SK.fit_chain(start, end, fld, T, n_arcs=n_, climb_max=cm, r_min=rm, l_min=2.0, seeds=8); break
                        except RuntimeError: pass
                    if fit: break
                if not fit: tried.append((al, thd, "no chain")); continue
                body = US.glue(body, US.bar_swept(k1, ey_, start, fit["segs"], w=WT))
                o_mid = ht * (math.cos(th) * k1 + math.sin(th) * ey_); sd = -math.sin(th) * k1 + math.cos(th) * ey_; nrm = unit(o_mid)
            body = US.glue(body, US.terminal_r(o_mid, nrm, sd, WT, 14.0))
            body = US.glue(body, upper_ring_R(k1, F1, M.hr[0]))
            body = body.cut(bore_cutter_R(k1, F1, M.hr[0]))
            for x_ in (6.0, 14.0):                                                         # 2x M4: O4.3 through, O7.3 x 1.2 counterbore
                cc = o_mid + x_ * sd
                body = body.cut(cq.Solid.makeCylinder(2.15, 12.0, V(cc - 6 * nrm), V(nrm)))
                body = body.cut(cq.Solid.makeCylinder(3.65, 3.0, V(cc + (T / 2 - 1.2) * nrm), V(nrm)))
            body = body.clean() if body.clean().isValid() else body
        except Exception as e_:
            tried.append((al, thd, f"cad {e_}")); continue
        cl = link1_posed_check(tess(body), l1m, frames)
        tried.append((float(al), thd, round(cl, 2)))
        print(f"  base tab heading {al:.0f}, terminal {thd:.0f} deg off J1 at {ht:.1f}: envelope mean {cd['score']:.2f}, vs posed link 1 {cl:.2f} mm", flush=True)
        if cl >= 0.5 and body.isValid() and len(body.Solids()) == 1:
            print(f"base tab: heading {al:.0f} deg, terminal {thd:.0f} deg off J1 at {ht:.1f} mm, link 1 >= {cl:.2f} mm; valid {body.isValid()}", flush=True)
            return ("base", 0, "D8-01 scapula base: J1 hub + tab, 2x M4 counterbored to the scapula handler (Ti-6Al-4V)", body), \
                dict(heading_deg=float(al), terminal_deg=thd, terminal_height=float(ht), envelope_mean_clear=cd["score"], link1_min_mm=cl,
                     radii=None if fit is None else fit["radii"], tried=tried, valid=body.isValid())
    raise RuntimeError(f"base tab: no candidate clears link 1: {tried}")


# ---------------------------------------------------------------------------------------------------- kinematic check
def check_frames(M, dd, parts):
    """as build_pinknee_l1.check_frames, on the full CAD: (a) the model's metal samples posed by its own member transforms
    vs the posed exo.glb (scene_export.frame_xforms on the frame dict = the judges' path), per part: hub discs, E boss, arm
    pad must coincide (<= 0.5 mm); the E strap, knee link and link straps are shape changes (reported); (b) every built
    part's vertices posed by the model's member transforms vs by frame_xforms"""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": sorted(taken, key=el)[-2]}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    K = PK.chain(M, np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))]))
    grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 6: "l4", 5: "H"}; out = []
    loc = {}
    for g, mem, n, s in parts:
        loc[n] = (g, mem)
    for lab, i in pick.items():
        pz = [B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")]; fr = PK.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; fdev = 0.0
        for node in src.graph.nodes_geometry:
            g, n = node.split("|")[:2]
            if g == "F" or n not in loc: continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            Vl = np.asarray(m.vertices); mem = loc[n][1]
            Vc = Vl @ np.asarray(R).T + t
            Vm = M.world(mem, i, Vl if mem != 5 else Vl @ PK.HR)
            fdev = max(fdev, float(np.abs(Vm - Vc).max()))
            m.vertices = Vc
            if "screw" not in n.lower() and "clip" not in n.lower(): meshes.setdefault(g, []).append(m)
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        res = {}
        for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
            Pw = M.world(m, i, Xp); g = "l1" if name == "hub1" else grp_of[m]
            d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                        np.ascontiguousarray(meshes[g].faces, np.int64))[0])
            sd = igl.signed_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float), np.ascontiguousarray(meshes[g].faces, np.int64))[0]
            res[name] = dict(max=round(float(d.max()), 4), p95=round(float(np.percentile(d, 95)), 4), outside_max=round(float(sd.max()), 4), n=int(len(Pw)))
        joint = ("hub1", "hub2", "hub3", "boss", "pad")
        worst = max(res[k]["max"] for k in joint)
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], joint_features_max_mm=round(worst, 4),
                        within_0p5=bool(worst <= 0.5 and fdev <= 0.5), per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4),
                        knee_angle=round(float(K["Kn"]["ang"][i]), 1)))
        print(f"  check {lab:16s} pose {i} {np.round(pz[:3], 1)}: joint features (hubs, boss, pad) vs posed glb max {worst:.4f} mm; "
              + ", ".join(f"{k} {v['max']:.2f}/{v['outside_max']:+.2f}" for k, v in res.items() if k not in joint)
              + f"; frames dev {fdev:.1e} mm, knee {K['Kn']['ang'][i]:.1f} deg", flush=True)
    return out


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_pinknee_k4598")
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--k", type=int); ap.add_argument("--hubs")
    ap.add_argument("--l1", default="l1_skin-normal-3r-pin-knee")
    a = ap.parse_args(ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    P0, src = PK.params_from(a); M, rep0 = PK.fit(P0); D = M.D; u, c, F = D.u, D.c, M.f
    l1d = json.load(open(os.path.join(FULL, "designs", a.l1, "design.json")))
    same = all(abs(float(l1d["params"].get(k, P0[k])) - float(P0[k])) < 1e-6 for k in P0 if isinstance(P0[k], (int, float)))
    assert same, f"the L1 design {a.l1} was built from other params: rebuild it first (build_pinknee_l1.py --params-file ...)"
    print(f"fit ({src}): gap {rep0['gap']} faces {np.round(F, 2)} tr {M.tr:.2f} m {np.round(D.m, 3)} hubs {M.hr} ({time.time() - t0:.0f} s)", flush=True)
    rep = dict(fit=dict(params=P0, source=src, gap=rep0["gap"], faces=[float(x) for x in F], tr=float(M.tr), m=[float(x) for x in D.m], hubs=M.hr),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths, rounds; no lofts)")
    parts = []                                                                              # (group, member, name, shape) member-local
    for J, k_, lo, hi, mlo, mhi in (("J1", 0, "l1", "base", 1, 0), ("J2", 1, "l1", "l2", 1, 2), ("J3", 2, "l3", "l2", 3, 2)):
        for g, n, s in hardware_R(J, u[k_], F[k_], lo, hi, M.hr[k_]):
            parts.append((g, mlo if g == lo else mhi, n, at(s, c[k_])))
    lk, rep["links"] = links(M); parts += lk
    m3, rep["member 3"] = member3(M); parts += m3
    parts.append(knee_link(M))
    l1b = json.load(open(os.path.join(FULL, "designs", a.l1, "build.json")))
    arm, users, rep["arm side"] = arm_side(M, l1b["mount"]); parts += arm
    # base tab vs the posed link 1 over every 2nd frame of every clip (the L1's clips = the model's frames)
    C = json.load(open(os.path.join(FULL, "designs", a.l1, "clips.json"))); frames = []
    for cl in C["clips"]:
        for fi, f in enumerate(cl["frames"]):
            if fi % 2: continue
            g = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
            frames.append((g("base"), t_("base"), g("l1"), t_("l1")))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    l1_body = next(s for g, mem, n, s in parts if n.startswith("D8-02"))
    bp, rep["base"] = base_part(M, E, l1_body, frames); parts.append(bp)
    # ---- export: member-local for members 0-4 / 6, H = HR x for member 5, the user's parts as they are
    HR = PK.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if mem == 5 else s, mem) for g, mem, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")): os.remove(os.path.join(dd, "step", f))
    USER = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        m = tess(s, fine=not user)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        if user: mat, rho = "user part", None
        elif "bearing" in n: mat, rho = "bearing steel", 7.8
        elif "17-4PH" in n: mat, rho = "17-4PH", 7.8
        elif "iglidur" in n: mat, rho = "iglidur", IGL
        elif hwr: mat, rho = "stainless (polished)", 7.9
        elif "7075-T6" in n: mat, rho = "7075-T6 (BOTTOM merged with the pad mount)", 2.81
        elif n.startswith("UPPER ARM CUFF"): mat, rho = "AlSi10Mg", 2.68
        else: mat, rho = "Ti-6Al-4V", TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids())))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L2 user-style", FACES={str(j + 1): round(float(F[j]), 2) for j in range(3)}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    for f in ("clips.json", "workspace.json"): shutil.copy(os.path.join(FULL, "designs", a.l1, f), os.path.join(dd, f))
    d = dict(l1d); d.update(id=a.out, label=f"skin-normal-3r-pin-knee ({src}), full CAD in the user's style",
                            level="L2 user-style (full CAD of the generation-3 winner)", l1_design=a.l1,
                            built_with="pipeline/conformal/param_cad/user_style_pinknee.py (user_style.py parts: line/arc sketches extruded / swept, planform "
                                       "pads, v5 joints; member 3 one side-view sketch; knee link + IGLIDUR-PIN stacks; BOTTOM fused with the pad mount) on "
                                       f"the L1 design's frames and clips ({a.l1})")
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    rep["check"] = check_frames(M, dd, [(g, mem, n, s) for g, mem, n, s in parts])
    rep["kinematics_exact"] = dict(poses=len(rep["check"]), all_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                   max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]),
                                   max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]))
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"kinematics: {rep['kinematics_exact']}; done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
