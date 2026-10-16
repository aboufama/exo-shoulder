"""Full user-style CAD of skin-normal-3r-pin-knee (docs/concepts/skin-normal-3r-pin-knee.md) - the generation-3 winner.

The kinematics are EXACTLY the verified model's: the shape is the model's own fit under the frozen-shape protocol
(build_pinknee_l1.fit: Bench(60,160) fast, the shape the verifier wore on Bench(110,360) exact), every part is designed in
its member's home frame (= the scapula frame at rest, GH = origin) and exported in its member's group (base, l1, l2,
l3 = hub 3's member, l4 = the knee link, H = arm-fixed at x_H = HR x), and clips.json / workspace.json are the L1
design's (l1_skin-normal-3r-pin-knee: "G" + "T" per group = the model's own Model.T(m, i)). The configuration is an
INPUT (--params JSON | --params-file F | --k K | default: docs/concepts/rows/<id>.json best_params), so a polished config
drops in; the L1 design dir named by --l1 must have been built from the same config (its clips carry the frames).
A config whose verified shape was fitted on a bench this box does not hold (the polished H1: fit on Bench(110,360) FAST,
cache only on the farm) comes in as a FROZEN SHAPE (--shape, pipeline/concept_l1/pinknee_shape.py: the farm fits and
pickles the attributes the verifiers hand over; here it is worn without a refit, the verifiers' frozen-shape protocol).

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
  arm side  the arm pad (O12 at pin b) + the pad mount as one planform sketch (lines + tangent arcs, 12 wide, at the pad
            level) on the L1's ROUTE (build_pinknee_l1.pad_mount_sweep: the shortest straight slab >= 1 mm clear of the
            knee's swept parts over 1161 closing poses), its last 6 mm a riser 1 mm into BOTTOM's underside; BOTTOM cut as the
            L1 cut it (square to the arm, where the sweep would meet it, the distal bar kept); all fused with pin b's integral
            pin into ONE 5-axis part; the upper-arm cuff from one line/arc sketch (user_style.upper_cuff, both side arcs
            trimmed clear of the trunk over the clip poses); the user's other arm parts unchanged.
  base      the scapula base AT THE J1 HUB RING (user ruling 2026-10-16, no tab): J1 upper ring + two short ears in the J1
            upper seat plane, each one M4 tapped hole for the user's scapula handler bracket; ear headings clear of the posed
            link 1 over every clip / workspace frame and of the skin envelope.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_pinknee.py [--out user_pinknee_k4598]
        [--params JSON | --params-file F | --k K | --shape PKL] [--hubs 10,10,10] [--l1 l1_skin-normal-3r-pin-knee]
    polished H1 (gen-3 winner): --out user_pinknee_h1 --l1 l1_skin-normal-3r-pin-knee-h1 --shape .cache/pk_shapes/h1_b110_360_m5.pkl
"""
import argparse, json, math, os, shutil, sys, time
ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import user_style as US                                                                   # noqa: E402  (param_build, sketch2d, arm_end)
REPO = US.FR.REPO
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
import build_pinknee_l1 as PK                                                             # noqa: E402  (the model fit, link rows, frames)
import pinknee_shape as PS                                                                # noqa: E402  (a frozen fitted shape, worn without its fit bench)
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


def judge_close(m):
    """the mesh as the judges see it (exo.glb float32 mm -> metres, merged at 1e-7 m, degenerate faces dropped:
    judge/dynamics.py mass_props): done here, so the exported mesh IS that mesh (gen-2 lesson: closed in mm, open in the
    judges' units -> R17's convex-hull fallback). Returns (mesh mm, watertight in the judges' units)"""
    V = np.asarray(m.vertices, np.float32).astype(float) / 1000.0
    j = trimesh.Trimesh(V, np.asarray(m.faces), process=False); j.merge_vertices(digits_vertex=7)
    j.update_faces(j.nondegenerate_faces()); j.remove_unreferenced_vertices()
    out = trimesh.Trimesh(np.asarray(j.vertices) * 1000.0, np.asarray(j.faces), process=False)
    if not j.is_watertight:
        w = weld_open(out, tol=0.05)
        if w.is_watertight: out = w
    chk = trimesh.Trimesh(np.asarray(out.vertices, np.float32).astype(float) / 1000.0, np.asarray(out.faces), process=False)
    chk.merge_vertices(digits_vertex=7); chk.update_faces(chk.nondegenerate_faces())
    return out, bool(chk.is_watertight)


def tess(s, fine=True, report=None):
    vs, fs = s.tessellate(0.02 if fine else 0.08, 0.15 if fine else 0.4)
    m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
    if not fine: return m
    m, wt = judge_close(weld_open(m))
    if report is not None: report["watertight_judge_units"] = wt
    return m


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
N_ARCS = (3, 4)                                                                            # arcs per bar (5 arcs = 3125 radius snaps per fit, 10+ min; never
                                                                                           # chosen over 4 within 0.5 mm on the earlier fits) - fewer bends
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
            for n_ in N_ARCS:
                for sc_ in ((1.0,) if rm == BEND_R else (1.0, 0.5)):
                    fk = f"{label}|hug60|bent-fail|{cm:g}|{rm:g}|{n_}|{sc_}|{geo}" if rm == BEND_R else f"{key}|fail|{cm}|{rm}|{n_}|{sc_}"
                    ok_k = f"{label}|hug60|ok|{cm:g}|{rm:g}|{n_}|{sc_}|{geo}"           # per-arc-count successes (helpers fill them in parallel)
                    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
                    if ok_k in cache:
                        f_ = dict(cache[ok_k]); f_["segs"] = [tuple(x) for x in f_["segs"]]; fits[n_] = f_
                        print(f"  {label}: {n_} arcs, climb {cm}, R >= {rm}, snap x{sc_}: ok (cached)", flush=True); break
                    if fk in cache: print(f"  {label}: {n_} arcs, climb {cm}, R >= {rm}, snap x{sc_}: {cache[fk]} (cached)", flush=True); e = cache[fk]
                    else:
                        try:
                            f_ = SK.fit_chain(start, end, clear, t, n_arcs=n_, climb_max=cm, r_min=rm, l_min=2.0, snap_scale=sc_, bend=4.0, seeds=16)
                            f_.update(climb_limit=cm, r_min=rm, l_min=2.0, snap_scale=sc_, bend=4.0); fits[n_] = f_
                            cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
                            cache[ok_k] = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in f_.items()}
                            cache[ok_k]["segs"] = [(float(a_), float(b_)) for a_, b_ in f_["segs"]]
                            cache[ok_k]["radii"] = [None if r_ is None else float(r_) for r_ in f_["radii"]]
                            json.dump(cache, open(CACHE + ".tmp", "w"), indent=0); os.replace(CACHE + ".tmp", CACHE); break
                        except RuntimeError as e_:
                            e = str(e_); print(f"  {label}: {n_} arcs, climb {cm}, R >= {rm}, snap x{sc_}: {e}", flush=True)
                            cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}; cache[fk] = e
                            os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(cache, open(CACHE + ".tmp", "w"), indent=0); os.replace(CACHE + ".tmp", CACHE)
                    if "snapped" not in e: break
            if fits: break
        if not fits: raise RuntimeError(f"{label}: no chain stays above the L1 strap")
        bm = min(f_["mean_clear"] for f_ in fits.values())
        nb = min(n_ for n_, f_ in fits.items() if f_["mean_clear"] <= bm + 0.5); fit = fits[nb]
        fit = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in fit.items()}
        fit["segs"] = [(float(k), float(l)) for k, l in fit["segs"]]; fit["radii"] = [None if r is None else float(r) for r in fit["radii"]]
        cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}; cache[key] = fit
        os.makedirs(os.path.dirname(CACHE), exist_ok=True); json.dump(cache, open(CACHE + ".tmp", "w"), indent=0); os.replace(CACHE + ".tmp", CACHE)
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
    D = M.D; u, c = D.u, D.c; F = M.f; out = []; rep = {}; hr = M.hr
    prof = M._link_rows if getattr(M, "_link_rows", None) is not None else PK.link_rows(M)   # a frozen shape carries its fit's rows
    C = [c[k] + F[k] * u[k] for k in range(3)]
    only = os.environ.get("PK_LINK_ONLY", "")                                              # "2": a helper fits link 2 alone (fills the cache)
    # ---- link 1: lower at J1 and J2 (both axes through GH), plane span(u1, u2)
    if only == "2": return links2(M, out, rep)
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
    return links2(M, out, rep)


def links2(M, out, rep):
    D = M.D; u, c = D.u, D.c; F = M.f; hr = M.hr; C = [c[k] + F[k] * u[k] for k in range(3)]
    prof = M._link_rows if getattr(M, "_link_rows", None) is not None else PK.link_rows(M)
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
    hw = [(lower_grp, f"pin {name}: iglidur thrust washer 4 x 8 x 0.5 (igus GTM-0408-005 class, in the 0.5 mm running gap; confirm the size, else cut from iglidur sheet)",
           rev([(2.1, tr + tp), (4.0, tr + tp), (4.0, tr + tp + PK.RUN), (2.1, tr + tp + PK.RUN)], cen, sn)),
          (knee_grp, f"pin {name}: iglidur G sleeve bearing igus GSM-0405-03 (4 x 5.5 x 3) faced to {zc0 - zk0:.2f}, pressed in the knee link",
           rev([(r + 0.01, zk0), (SLEEVE_D / 2, zk0), (SLEEVE_D / 2, zc0), (r + 0.01, zc0)], cen, sn))]
    # DIN 6799 E-clip: a C ring O3.2 / O7.3 x 0.6 with a 3.2 mm mouth
    clip = rev([(rg + 0.01, zc0), (3.65, zc0), (3.65, zc0 + CLIP_T), (rg + 0.01, zc0 + CLIP_T)], cen, sn)
    e, f = (PB.axis_frame(sn)[:, 0], PB.axis_frame(sn)[:, 1])
    cut = prism(np.asarray(cen) + (zc0 - 0.5) * sn, e, f, [(1.2, -1.6), (4.5, -1.6), (4.5, 1.6), (1.2, 1.6)], [0, 0, 0, 0], CLIP_T + 1.0)
    clip = clip.cut(cut)
    hw.append((lower_grp, f"pin {name}: retaining E-clip DIN 6799 - 3.2 (groove O3.2 on the O4 pin, O7.3 x 0.6), A2 stainless (polished), seated in the knee link's O8 x 0.7 counterbore", clip))
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
def arm_side(M, mount_rep, clip_poses):
    """arm pad + pad mount + riser, fused with the user's BOTTOM and pin b's integral pin into ONE 5-axis part, built in the
    canonical arm frame (exported x_H = HR x). The route is the L1's (build_pinknee_l1.pad_mount_sweep, the judged envelope):
    a straight tp slab at the pad level (tr..tr+tp) from pin b along the free direction (mount_rep dir_along_across, in
    the model's (sa, st)) to BOTTOM's bar, the last 6 mm stepping up to 1 mm into the bar's underside (riser_top_rel_tr).
    BOTTOM is cut as the L1 cut it (mount_rep bottom: square to the arm, plane normal sa, cut_along_from_pad_mm distal of
    pin b, the distal bar kept - where the knee's swept parts would meet it; cutting BOTTOM is allowed). Old L1s without a
    routed mount (no riser_top_rel_tr) fall back to the nearest-end mount at BOTTOM's s 255 end."""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; Bm = fr["Bm"]; HR = PK.HR; PR = PK.PAD_R
    da = np.array(mount_rep["dir_along_across"]); ex = unit(da[0] * D.sa + da[1] * D.st); ey = np.cross(sn, ex)
    Lx = float(mount_rep["length"]); htop = float(mount_rep.get("riser_top_rel_tr", tp)); routed = "riser_top_rel_tr" in mount_rep
    AE.S_CUT = S_CUT; AE.LAP_HOLES = []
    up = AE.user_parts()
    bot = [s for g, n, s in up if n.startswith("BOTTOM")][0]
    botC = xform(bot, HR.T)                                                                # rest (H) -> canonical arm frame
    bc = mount_rep.get("bottom") or {}; cut_rep = dict(cut=False)
    if bc.get("cut"):
        xc = float(bc["cut_along_from_pad_mm"]); o = Bm + xc * D.sa; e1 = PB.axis_frame(D.sa)[:, 0]; e2 = np.cross(D.sa, e1)
        half = prism(o - 400.0 * D.sa, e1, e2, [(-400, -400), (400, -400), (400, 400), (-400, 400)], [0, 0, 0, 0], 400.0)   # proximal half-space (normal e1 x e2 = sa)
        v0 = float(botC.Volume()); botC = botC.cut(half); botC = botC.clean() if botC.clean().isValid() else botC
        cut_rep = dict(cut=True, plane="square to the arm (normal = the model's sa), the L1's cut", along_from_pin_b_mm=xc, removed_mm3=round(v0 - float(botC.Volume()), 1),
                       solids=len(botC.Solids()), valid=botC.isValid())
        print(f"  BOTTOM cut {xc:.2f} mm distal of pin b (as the L1): removed {v0 - float(botC.Volume()):.0f} mm3, solids {len(botC.Solids())}, valid {botC.isValid()}", flush=True)
    rc = 1.0; q45 = math.sqrt(0.5)
    wp = (cq.Workplane(plane(Bm + tr * sn, ex, ey)).moveTo(0.0, -PR).lineTo(Lx - rc, -PR).threePointArc(
          (Lx - rc + rc * q45, -PR + rc - rc * q45), (Lx, -PR + rc)).lineTo(Lx, PR - rc)
          .threePointArc((Lx - rc + rc * q45, PR - rc + rc * q45), (Lx - rc, PR)).lineTo(0.0, PR).threePointArc((-PR, 0.0), (0.0, -PR)).close())
    slab = wp.extrude(tp).val()
    part = slab; riser = None; rvol = 0.0
    if routed and htop > tp + 0.05:
        x0 = max(Lx - 6.0, PR + 0.5)                                                       # the L1's riser: the last 6 mm (L - 3 .. L + 3)
        riser = prism(Bm + (tr + tp - 0.2) * sn, ex, ey, [(x0, -PR), (Lx, -PR), (Lx, PR), (x0, PR)], [0.0, rc, rc, 0.0], htop - tp + 0.2)
        rvol = float(riser.Volume()); part = part.fuse(riser)
    elif not routed:                                                                        # legacy nearest-end mount: riser into BOTTOM's s-255 end
        CBc, uBc, vBc, aBc = HR.T @ AE.CB, HR.T @ AE.uB, HR.T @ AE.vB, HR.T @ AE.axB
        riser = prism(Bm + (tr + tp - 0.2) * sn, ex, ey, [(Lx - 10.0, -PR), (Lx, -PR), (Lx, PR), (Lx - 10.0, PR)], [0, 0, 0, 0], 12.0)
        box = prism(CBc + (S_CUT - 40.0) * uBc - 14.5 * vBc + (-4.9) * aBc, uBc, vBc, [(0, 0), (40.0 - 0.01, 0), (40.0 - 0.01, 29.0), (0, 29.0)], [0, 0, 0, 0], 14.2, both=True)
        riser = riser.intersect(box); rvol = float(riser.Volume()) if riser.Solids() else 0.0
        if rvol > 1.0: part = part.fuse(riser)
    ov = float(part.intersect(botC).Volume())
    pin, hw = pin_stack("b", Bm, sn, tr, tp, "H", "l4")
    part = part.fuse(pin).fuse(botC)
    part = part.clean() if part.clean().isValid() else part
    print(f"arm side: pad mount {Lx:.1f} mm at {math.degrees(math.atan2(da[1], da[0])):.0f} deg, riser to tr + {htop:.2f} ({rvol:.0f} mm3, {ov:.1f} mm3 inside BOTTOM); "
          f"BOTTOM + mount: valid {part.isValid()}, solids {len(part.Solids())}", flush=True)
    cut_s = f"cut square to the arm {cut_rep['along_from_pin_b_mm']:.1f} mm distal of pin b" if cut_rep["cut"] else f"cut at s {S_CUT:g}"
    out = [("H", 5, f"D8-06 BOTTOM + arm pad + pad mount, one 5-axis part (user's bar {cut_s}; O12 pad at pin b + integral O4 h9 pin, hard-anodised; "
                     f"{tp:.2f} mm mount {Lx:.1f} long at the pad level, riser 1 mm into BOTTOM's underside; 7075-T6)", part)]
    out += [(g, 5 if g == "H" else 6, n, s) for g, n, s in hw]
    users = []
    for g, n, s in up:
        if n.startswith(("BOTTOM", "UPPER ARM CUFF", "M4x6 ISO 10642 countersunk (upper cuff)")): continue
        users.append((g, n, s))
    cuff, crep = upper_cuff_trim(clip_poses); users += cuff
    return out, users, dict(mount_length=Lx, mount_dir_deg=round(math.degrees(math.atan2(da[1], da[0])), 1), riser_top_rel_tr=htop, riser_mm3=round(rvol, 1),
                            mount_in_bottom_mm3=round(ov, 1), fused_valid=part.isValid(), fused_solids=len(part.Solids()), bottom=cut_rep, bottom_s_end_cut=S_CUT,
                            upper_cuff=crep, route=mount_rep.get("route", "nearest-end"))


# ---------------------------------------------------------------------------------------------------- upper-arm cuff
def upper_cuff_trim(clip_poses, wrap_neg_deg=CUFF_WRAP_NEG, margin=1.0):
    """user_style.upper_cuff (one U sketch of lines and arcs, extruded along BOTTOM; the same skin fit) with BOTH side
    arcs' wraps measured: the gen-2 lesson - the +vB arc entered the trunk with the arm at the side (Walking 90). The trunk
    skin (vertices with < 5 % weight on the arm bones) is posed at every given clip pose and taken into the arm's rest
    frame; a side arc stops `margin` mm (along the arc) before the first trunk point that comes within `margin` of its
    metal radially (points inside the inner radius - 1 are the rig's own trunk-in-arm self-intersection, not ours). The
    -vB arc keeps at most wrap_neg_deg (the forearm cuff folds onto it, user_style_osn)."""
    import body_pose as BP
    CB, uB, vB, axB = AE.CB, AE.uB, AE.vB, AE.axB; c = US.CUFF
    zt = AE.Z_SKIN_BAR; W_ = math.radians(c["wrap_deg"]); T2_ = c["t_shell"]; zi = zt - T2_; liner = 2.0
    C_, _ = US.FR.load(PB.BAND); L = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json"))); pts = []
    rig = BP._rig(); sk = rig.skin; n = len(sk["wi"])
    Wb = np.zeros((n, 5)); np.add.at(Wb, (np.repeat(np.arange(n), 4), sk["wi"].ravel()), sk["ww"].ravel())
    arm = ((sk["wi"] == 2) * sk["ww"]).sum(1) >= 0.6; trunk = Wb[:, 2:].sum(1) < 0.05
    for _, _, f in US.FR.followed(C_, every=4):
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"])); Vw = BP.posed(pose)
        sg, _ = BP.segs(L["landmarks"], L["scale"], pose); Rh, th = np.array(sg[2][0]), np.array(sg[2][1])
        Q = (Vw[arm] - th) @ Rh - CB; sq = Q @ uB
        m = (sq > c["s0"] - 5) & (sq < c["s1"] + 5) & (np.abs(Q @ vB) < 90) & (Q @ axB < 0) & (Q @ axB > -130)
        pts.append(np.stack([Q[m] @ vB, Q[m] @ axB], 1))
    P2 = np.concatenate(pts)
    def fits(R, vc, hw):
        v, z = P2[:, 0] - vc, P2[:, 1]; m = np.full(len(v), 99.0)
        top = np.abs(v) <= hw; m[top] = (zi - liner) - z[top]
        for sg in (-1, 1):
            sd = (sg * v > hw); cx, cz = sg * hw, zi - R; dx, dz = v[sd] - cx, z[sd] - cz
            ang = np.arctan2(sg * dx, dz); inw = ang <= W_ + math.radians(8)
            r = np.hypot(dx, dz); mm = np.where(inw, R - liner - r, 99.0); m[sd] = mm
        return float(m.min())
    best = None
    for vc in np.arange(-14.0, 14.1, 2.0):
        for hw in np.arange(15.0, 36.0, 2.5):
            if fits(140.0, vc, hw) < 0: continue
            lo, hi = 10.0, 140.0
            for _ in range(28):
                mid = (lo + hi) / 2; lo, hi = (lo, mid) if fits(mid, vc, hw) >= 0 else (mid, hi)
            R = math.ceil(hi); score = R + 0.5 * hw
            if best is None or score < best[0]: best = (score, R, vc, hw)
    assert best, "cuff: no U profile clears the arm"
    _, Rin, vc, hw = best; Ro = Rin + T2_
    # ---- the trunk vs both side arcs at every given pose (the judged clips' own poses)
    wrap = {1: W_, -1: min(W_, math.radians(wrap_neg_deg))}; hits = {1: [], -1: []}; flat_hit = 1e9
    for pz in clip_poses:
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], pz)); Vw = rig.posed(pose)
        sg, _ = BP.segs(L["landmarks"], L["scale"], pose); Rh, th = np.array(sg[2][0]), np.array(sg[2][1])
        Q = (Vw[trunk] - th) @ Rh - CB; sq = Q @ uB
        Q = Q[(sq > c["s0"] - margin) & (sq < c["s1"] + margin)]
        if not len(Q): continue
        v, z = Q @ vB - vc, Q @ axB
        topm = (np.abs(v) <= hw) & (z > zi - liner) & (z < zt + margin)
        if topm.any(): flat_hit = min(flat_hit, float(np.min(np.abs(z[topm] - zt))))
        for sgn in (1, -1):
            sd = sgn * v > hw; dx, dz = v[sd] - sgn * hw, z[sd] - (zi - Rin); r = np.hypot(dx, dz); ang = np.arctan2(sgn * dx, dz)
            near = (r >= Rin - 1.0) & (r <= Ro + margin) & (ang >= 0) & (ang <= wrap[sgn] + margin / Ro)
            if near.any():
                a_ = float(ang[near].min()) - margin / Ro
                if a_ < wrap[sgn]: wrap[sgn] = max(a_, math.radians(10.0)); hits[sgn].append([round(float(x), 1) for x in pz[:3]])
    Wp, Wn = wrap[1], wrap[-1]
    print(f"cuff: {len(P2)} arm skin samples; U profile: flat {2 * hw:g} mm, side arcs R{Rin:g}, centred {vc:+.0f} mm across the bar, "
          f"{fits(Rin, vc, hw):.2f} mm beyond skin + 2 mm liner; trunk over {len(clip_poses)} clip poses: +vB arc wrap {math.degrees(Wp):.0f} deg "
          f"(was {c['wrap_deg']:g}; {len(hits[1])} limiting poses), -vB {math.degrees(Wn):.0f} deg; flat top vs trunk {flat_hit if flat_hit < 1e8 else None}", flush=True)
    pl = cq.Plane(origin=tuple(map(float, CB + c["s0"] * uB)), xDir=tuple(map(float, vB)), normal=tuple(map(float, uB)))
    q = lambda xy: (float(xy[0]), float(xy[1]))
    def arcp(sg, R, a): return np.array([vc + sg * hw + sg * R * math.sin(a), zi - Rin + R * math.cos(a)])
    wp = (cq.Workplane(pl).moveTo(*q(arcp(-1, Ro, 0.0))).lineTo(*q(arcp(1, Ro, 0.0)))
          .threePointArc(q(arcp(1, Ro, Wp / 2)), q(arcp(1, Ro, Wp))).lineTo(*q(arcp(1, Rin, Wp)))
          .threePointArc(q(arcp(1, Rin, Wp / 2)), q(arcp(1, Rin, 0.0))).lineTo(*q(arcp(-1, Rin, 0.0)))
          .threePointArc(q(arcp(-1, Rin, Wn / 2)), q(arcp(-1, Rin, Wn))).lineTo(*q(arcp(-1, Ro, Wn)))
          .threePointArc(q(arcp(-1, Ro, Wn / 2)), q(arcp(-1, Ro, 0.0))).close())
    cuff = US.rounded(wp.extrude(c["s1"] - c["s0"]).val(), r=c["round"]); scr = []
    for s_ in (94.25, 124.25, 154.25):
        for y_ in (-8.75, 8.75):
            p = CB + s_ * uB + y_ * vB + zt * axB
            cuff = cuff.cut(cq.Solid.makeCylinder(2.25, 12.0, V(p - 10 * axB), V(axB)))
            hd = T2_; cuff = cuff.cut(cq.Solid.makeCone(4.2, 0.0, 4.2, V(p - hd * axB), V(axB)))
            head = PB.revolved([(0, 0), (3.95, 0), (2.0, 1.95), (2.0, 6.0), (0, 6.0)], np.array([0, 0, 1.0]), 0.0)
            scr.append(("H", "M4x6 ISO 10642 hexagon socket countersunk screw (upper cuff -> BOTTOM), polished A2", xform(head, PB.axis_frame(axB), p - hd * axB)))
    cuff = cuff.clean() if cuff.clean().isValid() else cuff
    rep = dict(side_arc_R=Rin, flat_width=2 * hw, centre_across_bar=vc, shell=T2_, wrap_pos_deg=round(math.degrees(Wp), 1), wrap_neg_deg=round(math.degrees(Wn), 1),
               wrap_rule=f"each side arc stops {margin} mm before the first trunk point within {margin} mm of it over {len(clip_poses)} clip poses",
               limiting_poses_pos=hits[1][:12], limiting_poses_neg=hits[-1][:12], flat_top_vs_trunk_mm=None if flat_hit > 1e8 else flat_hit,
               length=c["s1"] - c["s0"], valid=cuff.isValid())
    print(f"  cuff valid {cuff.isValid()}, faces {len(cuff.Faces())}", flush=True)
    return [("H", "UPPER ARM CUFF (one sketch: flat land + inner/outer R arcs, both side arcs trimmed clear of the trunk, extruded; AlSi10Mg bead blasted)", cuff)] + scr, rep


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


EAR_L, EAR_W, EAR_RF, M4_TAP = 14.5, 9.0, 3.0, 3.3                                        # ear: hole centre from the J1 axis, width, root fillet, M4 tap drill


def ear_margins(M, l1_body, rel, dz=0.0, l1m=None):
    """link 1's built surface posed into the base frame over every frame (rel = [(R, t)] l1 local -> base local), kept
    near the ear level and outside the hub ring; per heading (1 deg) the min 3D distance to an ear slab (capsule axis ->
    EAR_L, half width EAR_W / 2, levels F1 + U0 .. + T): all points, and without link 1's own J1 pad (its top face is the
    stack's designed 0.15 mm running gap under the base's upper level)"""
    D = M.D; k1 = unit(D.u[0]); F1 = M.f[0]; R = M.hr[0]; lev = F1 + LV["U0"] + dz
    d0 = unit(np.array([0.0, 0.6, -0.8])); d0 = unit(d0 - (d0 @ k1) * k1); d1 = np.cross(k1, d0)
    l1m = tess(l1_body, fine=False) if l1m is None else l1m; X1 = np.r_[np.asarray(l1m.vertices), trimesh.sample.sample_surface_even(l1m, 8000, seed=4)[0]]
    keep = []
    for Rr, tr_ in rel:
        P = X1 @ Rr.T + tr_; z = P @ k1; rad = np.linalg.norm(P - np.outer(z, k1), axis=1)
        sel = (z > lev - 2.0) & (z < lev + T + 2.0) & (rad > R + 0.3) & (rad < EAR_L + EAR_W / 2 + 3.0)
        if sel.any(): keep.append(P[sel])
    P = np.concatenate(keep) if keep else np.zeros((0, 3))
    z = P @ k1; x0, y0 = P @ d0, P @ d1; pad = z <= F1 + T + 0.01
    dz = np.maximum(np.maximum(lev - z, z - (lev + T)), 0.0)
    m_all, m_np = np.full(360, 99.0), np.full(360, 99.0)
    for a in range(360):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        x = x0 * ca + y0 * sa; y = -x0 * sa + y0 * ca
        d2 = np.hypot(x - np.clip(x, 0.0, EAR_L), y) - EAR_W / 2
        d = np.where(dz > 0, np.hypot(np.maximum(d2, 0.0), dz), d2)
        if len(d): m_all[a] = float(d.min()); m_np[a] = float(d[~pad].min()) if (~pad).any() else 99.0
    return dict(d0=d0, d1=d1, m_all=m_all, m_nopad=m_np, n_pts=int(len(P)), l1m=l1m)


EAR_DZ = (0.0, 1.3, 2.6)                                                                   # ear levels above the J1 upper seat (2.6 = flush with the ring top H1)


def base_part(M, E, l1_body, rel, frames):
    """the scapula base AT THE J1 HUB RING (user ruling 2026-10-16: the scapula handler carries the base directly at the
    J1 ring, no tab out to a remote terminal): J1 upper ring + bore, the upper seat disc, and two short ears on the ring
    (planform: the hub circle + a 9 wide bar to 14.5 mm with an R4.5 end and R3 root fillets - lines + tangent arcs,
    extruded 3 mm), each with one M4 tapped hole (O3.3 tap drill) for the handler's bracket from above. Ear level: the
    upper seat plane, else raised up to flush with the ring top (EAR_DZ). Headings: link 1 (built, posed over every clip
    and workspace frame) >= 1 mm from each ear above its own pad (>= 0.15 at the pad), >= 0.5 mm over the scapula-frame
    skin envelope (2 mm clearance), the ears 90-180 deg apart, the largest worst margin. If no level has such a pair, a
    relaxed pass (link 1 >= 0.5 mm, skin envelope >= -1.5 = 0.5 mm from the skin) - stated; if none either, NO ears: the
    base is the J1 upper member alone and the handler's bracket threads onto the M18 x 0.5 spigot in place of the dome
    cap (it retains the upper outer ring) - stated, the bracket being the handler's part."""
    D = M.D; k1 = unit(D.u[0]); F1 = M.f[0]; R = M.hr[0]
    l1m = tess(l1_body, fine=False); found = None; diag = []
    for rule, need_link, need_all, need_skin in (("strict", 1.0, 0.15, 0.5), ("relaxed", 0.5, 0.15, -1.5)):
        for dz in EAR_DZ:
            lev = F1 + LV["U0"] + dz
            em = ear_margins(M, l1_body, rel, dz=dz, l1m=l1m); d0, d1 = em["d0"], em["d1"]
            hd = lambda a, d0=d0, d1=d1: math.cos(math.radians(a)) * d0 + math.sin(math.radians(a)) * d1
            ok_link = [a for a in range(0, 360, 2) if em["m_nopad"][a] >= need_link and em["m_all"][a] >= need_all]
            skin = {}
            for a in ok_link:
                fld = US.PolarField(E, "S", np.eye(3), k1, hd(a), -5.0, 75.0, EAR_W)
                Uf = np.array([(lev, x_) for x_ in np.linspace(R, EAR_L + EAR_W / 2, 12)]); skin[a] = float(fld(Uf).min())
            feas = [a for a, v in skin.items() if v >= need_skin]
            score = lambda a: min(em["m_nopad"][a], 3.0) + 0.5 * min(em["m_all"][a], 1.0) + 0.2 * min(skin[a], 3.0)
            best = None
            for i, a in enumerate(feas):
                for b_ in feas[i + 1:]:
                    sep = abs((b_ - a + 180) % 360 - 180)
                    if sep < 90: continue
                    sc = (min(score(a), score(b_)), sep)
                    if best is None or sc > best[0]: best = (sc, a, b_)
            top = sorted(skin.items(), key=lambda kv: -kv[1])[:4]
            diag.append(dict(rule=rule, dz=dz, headings_clear_of_link1=len(ok_link), skin_feasible=len(feas), best_skin=[[a, round(v, 2)] for a, v in top]))
            print(f"base at the J1 ring ({rule}, ears +{dz:g} mm): {em['n_pts']} posed link-1 samples; headings clear of link 1 {len(ok_link)}/180, "
                  f"of those clear of the skin envelope {len(feas)}; best skin {[(a, round(v, 2)) for a, v in top]}", flush=True)
            if best is not None: found = (rule, dz, lev, em, hd, skin, best); break
        if found: break
    body = None
    if found:
        rule, dz, lev, em, hd, skin, (_, a1, a2) = found
        for a in (a1, a2):
            pl = US.plate(k1, lev, hd(a), EAR_W, T, EAR_L, R=R, rf=EAR_RF)
            pl = pl.fuse(disc((EAR_L) * hd(a), k1, EAR_W / 2, lev, lev + T)).clean()
            body = pl if body is None else US.glue(body, pl)
        if dz > 0:                                                                          # the upper seat disc under raised ears
            body = US.glue(body, disc(np.zeros(3), k1, R, F1 + LV["U0"], F1 + LV["U0"] + T))
    else:
        body = disc(np.zeros(3), k1, R, F1 + LV["U0"], F1 + LV["U0"] + T)
    body = US.rounded(body, skip=lambda e: e.geomType() == "CIRCLE" and abs(np.array(e.positionAt(0.5).toTuple()) @ k1 - (F1 + LV["U0"] + T)) < 1e-3
                      and abs(np.linalg.norm((lambda p: p - (p @ k1) * k1)(np.array(e.positionAt(0.5).toTuple()))) - R) < 1e-3) if found else body
    body = US.glue(body, upper_ring_R(k1, F1, R))
    body = ring_root_R(body, k1, F1, R)
    body = body.cut(bore_cutter_R(k1, F1, R))
    if found:
        for a in (a1, a2):
            cc = EAR_L * hd(a)
            body = body.cut(cq.Solid.makeCylinder(M4_TAP / 2, T + 2.0, V(cc + (lev - 1.0) * k1), V(k1)))
    body = body.clean() if body.clean().isValid() else body
    cl = link1_posed_check(tess(body), l1m, frames)
    if found:
        print(f"base ({rule}): ears +{dz:g} mm at {a1} / {a2} deg (sep {abs((a2 - a1 + 180) % 360 - 180)}), link 1 margins {em['m_nopad'][a1]:.2f} / "
              f"{em['m_nopad'][a2]:.2f} mm (incl. its pad {em['m_all'][a1]:.2f} / {em['m_all'][a2]:.2f}), skin envelope {skin[a1]:.2f} / {skin[a2]:.2f} mm; "
              f"built base vs posed link 1 {cl:.2f} mm; valid {body.isValid()}, solids {len(body.Solids())}", flush=True)
        name = (f"D8-01 scapula base AT THE J1 RING: J1 O20 ring + seat disc + 2 ears (+{dz:g} mm), each 1x M4 tapped (O3.3 tap drill) for the user's "
                "scapula handler bracket from above - no tab (Ti-6Al-4V, 5-axis machined)")
        rep = dict(rule=f"base at the J1 hub ring, no tab (user 2026-10-16); ear rule {rule}", ears_deg=[a1, a2], ear_level_above_seat_mm=dz,
                   ear=dict(hole_from_axis=EAR_L, width=EAR_W, thread="M4 tapped, 3 mm", tap_drill=M4_TAP),
                   link1_margin_above_pad_mm=[float(em["m_nopad"][a1]), float(em["m_nopad"][a2])],
                   link1_margin_incl_pad_mm=[float(em["m_all"][a1]), float(em["m_all"][a2])], skin_envelope_mm=[skin[a1], skin[a2]])
    else:
        print(f"base: NO ear level clears link 1's sweep and the skin - the base is the J1 upper member alone (handler bracket on the M18 x 0.5 "
              f"spigot in place of the dome cap); built base vs posed link 1 {cl:.2f} mm; valid {body.isValid()}, solids {len(body.Solids())}", flush=True)
        name = ("D8-01 scapula base AT THE J1 RING: the J1 upper member alone (O20 ring + seat disc + M18 x 0.5 spigot); the user's scapula handler "
                "bracket threads onto the spigot in place of the dome cap - no ears, no tab (Ti-6Al-4V, 5-axis machined)")
        rep = dict(rule="base at the J1 hub ring, no tab (user 2026-10-16); NO ears: link 1 sweeps every ear heading (see diag)",
                   interface="the handler's bracket threads onto the J1 M18 x 0.5 spigot in place of the dome cap (retains the upper outer ring)")
    rep.update(built_vs_posed_link1_mm=cl, diag=diag, valid=body.isValid(), solids=len(body.Solids()))
    return ("base", 0, name, body), rep


# ---------------------------------------------------------------------------------------------------- kinematic check
def check_frames(M, dd, parts):
    """as build_pinknee_l1.check_frames, on the full CAD: (a) the model's metal samples posed by its own member transforms
    vs the posed exo.glb (scene_export.frame_xforms on the frame dict = the judges' path), per part: hub discs, E boss, arm
    pad must coincide (<= 0.5 mm); the E strap, knee link and link straps are shape changes (reported); (b) every built
    part's vertices posed by the model's member transforms vs by frame_xforms"""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    M_bench_K = dict(Q=M.Q, s=M.s, RS=M.RS, X=M.X, Kn=M.K, qr=M.q)
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
    items = [(lab, i, None) for lab, i in pick.items()]
    # real clip frames (gen-2 lesson: a real overhead clip frame, Raise overhead above elevation 120; and the arm at the side
    # in Walking): the L1's frame dicts as the judges read them, the model chain re-solved at that frame's pose
    C = json.load(open(os.path.join(dd, "clips.json")))
    for cname, lab, key in (("Raise overhead", "clip: Raise overhead top", lambda f: f["p"][1]), ("Walking arm swing", "clip: Walking arm at side", lambda f: -f["p"][1]),
                            ("Comb hair", "clip: Comb hair top", lambda f: f["p"][1]), ("Reach back pocket", "clip: Reach back pocket", lambda f: -f["p"][0])):
        cl = next((c_ for c_ in C["clips"] if c_["name"] == cname), None)
        if cl is None: continue
        fol = [f for f in cl["frames"] if not f["held"]]
        if fol: f = max(fol, key=key); items.append((lab + f" (frame {cl['frames'].index(f)})", None, f))
    for lab, i, fclip in items:
        if fclip is None:
            pz = [B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")]; fr = PK.frame_dict(K, i, pz, pz, False); Ki = K
            PK.swap_in(M, M_bench_K)
        else:
            pz = list(fclip["p"]); fr = fclip; Ki = PK.chain(M, np.array([pz], float)); PK.swap_in(M, Ki); i = 0
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
        rig_max = max(res[k]["max"] for k in joint + ("knee",)); clos = max(res[k]["outside_max"] for k in ("E", "boss", "pad", "knee"))
        out.append(dict(label=lab, bench_pose=None if fclip is not None else int(i), clip_frame=fclip is not None, pose=[round(float(x), 2) for x in pz[:3]],
                        joint_features_max_mm=round(worst, 4), rigid_incl_knee_link_max_mm=round(rig_max, 4), closure_parts_model_outside_built_max_mm=round(clos, 4),
                        within_0p5=bool(worst <= 0.5 and rig_max <= 0.5 and fdev <= 0.5), per_part=res, frame_dev_mm=round(fdev, 6),
                        res_deg=round(float(Ki["res"][i]), 4), knee_angle=round(float(Ki["Kn"]["ang"][i]), 1)))
        print(f"  check {lab:34s} {np.round(pz[:3], 1)}: hubs/boss/pad vs posed glb max {worst:.4f} mm, + knee link {rig_max:.4f}; "
              + ", ".join(f"{k} {v['max']:.2f}/{v['outside_max']:+.2f}" for k, v in res.items() if k not in joint)
              + f"; frames dev {fdev:.1e} mm, knee {Ki['Kn']['ang'][i]:.1f} deg", flush=True)
    PK.swap_in(M, M_bench_K)
    return out


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_pinknee_k4598")
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--k", type=int); ap.add_argument("--hubs")
    ap.add_argument("--l1", default="l1_skin-normal-3r-pin-knee")
    ap.add_argument("--shape", help="a frozen fitted shape (pipeline/concept_l1/pinknee_shape.py export, e.g. fit on Bench(110,360) on the farm): "
                                    "worn here without a refit; its params replace --params / --k")
    a = ap.parse_args(ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    if a.shape:
        M, shape = PS.wear(a.shape); P0 = dict(shape["params"]); rep0 = dict(shape["report"])
        src = f"{shape['source']}; frozen shape {os.path.relpath(a.shape, REPO)} fit on Bench{tuple(shape['fit_bench'])} {shape['mode']} at fold margin {shape['fold_margin']:g}"
        os.environ.setdefault("CB_FOLD_MARGIN", f"{shape['fold_margin']:g}")
    else:
        P0, src = PK.params_from(a); M, rep0 = PK.fit(P0)
    D = M.D; u, c, F = D.u, D.c, M.f
    l1d = json.load(open(os.path.join(FULL, "designs", a.l1, "design.json")))
    same = all(abs(float(l1d["params"].get(k, P0[k])) - float(P0[k])) < 1e-6 for k in P0 if isinstance(P0[k], (int, float)))
    assert same, f"the L1 design {a.l1} was built from other params: rebuild it first (build_pinknee_l1.py --params-file ...)"
    print(f"fit ({src}): gap {rep0['gap']} faces {np.round(F, 2)} tr {M.tr:.2f} m {np.round(D.m, 3)} hubs {M.hr} fold margin {PK.MK.S.FOLD_MARGIN if hasattr(PK.MK.S, 'FOLD_MARGIN') else '?'} "
          f"({time.time() - t0:.0f} s)", flush=True)
    l1f = json.load(open(os.path.join(FULL, "designs", a.l1, "build.json")))["fit"]
    assert abs(float(l1f["tr"]) - float(M.tr)) < 1e-2 and np.allclose(l1f["m"], D.m, atol=1e-2), \
        (f"the fit differs from the L1's (tr {l1f['tr']} m {l1f['m']}): the frames in {a.l1}/clips.json are another shape. The verified k4598 "
         "shape is the fold-margin-10 fit: run with CB_FOLD_MARGIN=10 (tools/concept_kit.py), or rebuild the L1 at the current rule first")
    rep = dict(fit=dict(params=P0, source=src, gap=rep0["gap"], faces=[float(x) for x in F], tr=float(M.tr), m=[float(x) for x in D.m], hubs=M.hr,
                        fold_margin_deg=float(os.environ.get("CB_FOLD_MARGIN", 5.0)), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths, rounds; no lofts)")
    parts = []                                                                              # (group, member, name, shape) member-local
    for J, k_, lo, hi, mlo, mhi in (("J1", 0, "l1", "base", 1, 0), ("J2", 1, "l1", "l2", 1, 2), ("J3", 2, "l3", "l2", 3, 2)):
        for g, n, s in hardware_R(J, u[k_], F[k_], lo, hi, M.hr[k_]):
            parts.append((g, mlo if g == lo else mhi, n, at(s, c[k_])))
    lk, rep["links"] = links(M); parts += lk
    m3, rep["member 3"] = member3(M); parts += m3
    parts.append(knee_link(M))
    l1b = json.load(open(os.path.join(FULL, "designs", a.l1, "build.json")))
    Cc = json.load(open(os.path.join(FULL, "designs", a.l1, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = arm_side(M, l1b["mount"], cposes); parts += arm
    # the base at the J1 ring vs the posed link 1: every clip frame + every eval-feasible workspace pose (the L1's frames =
    # the model's); the built-mesh confirmation on every 3rd clip frame
    C = json.load(open(os.path.join(FULL, "designs", a.l1, "clips.json"))); frames = []; rel = []
    Wj = json.load(open(os.path.join(FULL, "designs", a.l1, "workspace.json")))
    allf = [f for cl in C["clips"] for f in cl["frames"]] + [p for p in Wj["poses"] if p.get("eval_feasible")]
    for fi, f in enumerate(allf):
        g = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        Gb, Tb, G1, T1 = g("base"), t_("base"), g("l1"), t_("l1"); rel.append((Gb.T @ G1, Gb.T @ (T1 - Tb)))
        if fi % 3 == 0: frames.append((Gb, Tb, G1, T1))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G in E.frames: G["S"] = E.RS[p]
    l1_body = next(s for g, mem, n, s in parts if n.startswith("D8-02"))
    bp, rep["base"] = base_part(M, E, l1_body, rel, frames); parts.append(bp)
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
        trep = {}; m = tess(s, fine=not user, report=trep)
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
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
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
