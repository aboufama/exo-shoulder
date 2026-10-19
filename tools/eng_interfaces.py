"""End-geometry drawing sets: what you need to redesign each part from the drawing - where its end components (hub
rings, integral pins, knee bores) sit relative to each other, the angles between their axes, and every diameter and
face along each end's own axis, referenced to one datum - plus the kinematic assembly layout (every joint axis in the
body frame) and the real-CAD general arrangement and hub section (tools/eng_drawings.py).

Part frame (each part sheet): origin on END 1's axis at its skin-side face; Z = END 1's axis, pointing away from the
skin; X = toward END 2 (perpendicular to Z); Y = Z x X. Ends are ordered proximal first (highest on the body).
Body frame (assembly): origin at the shoulder (GH) centre; x anterior, y up, z lateral (right shoulder), rest pose.

    OMP_NUM_THREADS=1 nice python3 tools/eng_interfaces.py B        (sets: A, B)
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Arc
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eng_drawings as ED
from eng_drawings import Sheet, load, features, hlr, ext, draw_polys, pick_scale, scale_txt, transformed, volume, callout, LW, PT, FS, INK, REPO

GHOST = "#a7b0ba"


def rest_posing(dd):
    """pose(step_path, shape) -> the shape at the CAD's rest frame (clip 0, frame 0), as the judges pose it
    (pipeline/full-exo/scene_export.py: every group by its frame transform, the arm side by the body rig). The STEP
    files themselves are in the build pose, where the knee is not closed."""
    import trimesh
    sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
    import scene_export as SE
    D = os.path.join(REPO, "pipeline", "full-exo", "designs", dd)
    X, _ = SE.frame_xforms(json.load(open(os.path.join(D, "clips.json")))["clips"][0]["frames"][0])
    kmap = {}
    for name in trimesh.load(os.path.join(D, "exo.glb")).geometry:
        bits = name.split("|")
        if bits[-1].isdigit():
            kmap[int(bits[-1])] = bits[0]
    def pose(path, shape):
        k = int(os.path.basename(path).split("_")[0]); g = kmap.get(k)
        if g not in X:
            return shape
        R, t = X[g]
        return transformed(shape, np.asarray(R), -np.asarray(R).T @ np.asarray(t))
    return pose
JOINT_FEATS = {(True, 11.0), (True, 7.0), (True, 6.0), (True, 5.5), (True, 20.0), (False, 7.0), (False, 4.0), (False, 12.0), (False, 10.0)}
IVIEWS = {"front": ((0, -1, 0), (1, 0, 0)), "top": ((0, 0, 1), (1, 0, 0)), "right": ((1, 0, 0), (0, 1, 0))}


def unit(v):
    return v / np.linalg.norm(v)


def coaxial_groups(F):
    groups = []
    for f in F:
        for g in groups:
            if abs(abs(np.dot(f["D"], g["D"])) - 1) < 1e-4 and np.linalg.norm(np.cross(f["c"] - g["c"], g["D"])) < 0.05:
                g["f"].append(f); break
        else:
            groups.append({"D": f["D"].copy(), "c": f["c"].copy(), "f": [f]})
    for g in groups:
        g["c"] = np.mean([f["c"] for f in g["f"]], axis=0)
    return groups


def axial_faces(shape, P, D, rmax=12.5):
    """axial positions (along D from P) of planar faces square to the axis whose centroid lies within rmax of it"""
    out = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face_s(exp.Current()); exp.Next()
        sa = BRepAdaptor_Surface(f)
        if sa.GetType() != GeomAbs_Plane:
            continue
        n = sa.Plane().Axis().Direction(); n = np.array([n.X(), n.Y(), n.Z()])
        if abs(abs(np.dot(n, D)) - 1) > 1e-3:
            continue
        p = GProp_GProps(); BRepGProp.SurfaceProperties_s(f, p); c = p.CentreOfMass(); c = np.array([c.X(), c.Y(), c.Z()])
        if np.linalg.norm((c - P) - D * np.dot(c - P, D)) <= rmax:
            out.append(float(np.dot(c - P, D)))
    return out


def partial_bosses(shape, d0=12.0, min_span=150.0):
    """boss cylinders of diameter d0 that are not full turns (a pin boss merged into a strap or pad): the knee-pin axes of
    parts whose pressed pins are merged into the solid, so no seat bore is modelled"""
    from OCP.GeomAbs import GeomAbs_Cylinder
    from OCP.BRepTools import BRepTools
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.TopAbs import TopAbs_REVERSED
    out = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face_s(exp.Current()); exp.Next()
        sa = BRepAdaptor_Surface(f)
        if sa.GetType() != GeomAbs_Cylinder:
            continue
        cyl = sa.Cylinder()
        if abs(2 * cyl.Radius() - d0) > 0.05:
            continue
        u0, u1, v0, v1 = BRepTools.UVBounds_s(f)
        if math.degrees(u1 - u0) < min_span or math.degrees(u1 - u0) > 340:
            continue
        a = cyl.Axis(); P0 = np.array([a.Location().X(), a.Location().Y(), a.Location().Z()]); D = np.array([a.Direction().X(), a.Direction().Y(), a.Direction().Z()])
        pr = BRepLProp_SLProps(sa, (u0 + u1) / 2, (v0 + v1) / 2, 1, 1e-6)
        P = np.array([pr.Value().X(), pr.Value().Y(), pr.Value().Z()]); N = np.array([pr.Normal().X(), pr.Normal().Y(), pr.Normal().Z()])
        if f.Orientation() == TopAbs_REVERSED:
            N = -N
        rad = P - (P0 + D * np.dot(P - P0, D))
        if np.dot(N, rad) <= 0:
            continue                                          # a bore, not a boss
        out.append(dict(d=d0, hole=False, c=P0 + D * (v0 + v1) / 2, D=D, L=v1 - v0))
    return out


def part_ends(shape):
    """ends (joint components), clocked secondary features and other features of a part, world coordinates; every
    axis points away from GH (the world origin)"""
    F = features(shape)
    for pb in partial_bosses(shape):
        if not any(abs(abs(np.dot(pb["D"], f["D"])) - 1) < 1e-4 and np.linalg.norm(np.cross(pb["c"] - f["c"], f["D"])) < 0.05 for f in F):
            F.append(pb)
    G = coaxial_groups(F)
    for g in G:
        g["D"] = unit(g["D"])
        if np.dot(g["D"], g["c"]) < 0:
            g["D"] = -g["D"]
    ends = [g for g in G if any((f["hole"], round(f["d"], 1)) in JOINT_FEATS for f in g["f"])]
    def hosted(g, among):
        for e in among:
            if abs(np.dot(g["D"], e["D"])) > math.cos(math.radians(2)):
                rv = (g["c"] - e["c"]) - e["D"] * np.dot(g["c"] - e["c"], e["D"])
                if np.linalg.norm(rv) < 12.5:
                    return True
        return False
    _eid = {id(e) for e in ends}
    seats = [g for g in G if id(g) not in _eid and any(f["hole"] and round(f["d"], 1) in (3.0, 2.5) and f["L"] >= 2.0 for f in g["f"]) and not hosted(g, ends)]
    ends = ends + seats                                       # pressed pin seats (knee pins, crank pivot, nose dowel) are joint ends too
    eid = {id(e) for e in ends}
    rest = [g for g in G if id(g) not in eid]
    sec, other = [], []
    for g in rest:
        host = None
        for e in ends:
            if abs(np.dot(g["D"], e["D"])) > math.cos(math.radians(2)):
                rv = (g["c"] - e["c"]) - e["D"] * np.dot(g["c"] - e["c"], e["D"])
                if np.linalg.norm(rv) < 12.5:
                    host = e; break
        (sec if host else other).append((g, host))
    for e in ends:
        P, D = e["c"], e["D"]
        lv = axial_faces(shape, P, D)
        rng = []
        for f in e["f"]:
            s = float(np.dot(f["c"] - P, D)); rng.append((f, s - f["L"] / 2, s + f["L"] / 2))
        s0 = min(lv + [a for _, a, _ in rng])
        e["O"] = P + D * s0
        e["levels"] = sorted(set(round(x - s0, 2) for x in lv))
        e["ranges"] = sorted([(f, a - s0, b - s0) for f, a, b in rng], key=lambda t: (t[1], -t[0]["d"]))
        e["top"] = max(e["levels"] + [b for _, _, b in e["ranges"]])
    ends.sort(key=lambda e: -e["O"][1])
    return ends, sec, other


def frame_of(ends, shape):
    e1 = ends[0]; Z = e1["D"]
    if len(ends) > 1:
        v = ends[1]["O"] - e1["O"]
    else:
        _, c = volume(shape); v = c - e1["O"]
    X = v - Z * np.dot(v, Z)
    X = unit(X) if np.linalg.norm(X) > 1e-6 else unit(np.cross(Z, [0, 0, 1.0]))
    Y = np.cross(Z, X)
    return np.array([X, Y, Z]), e1["O"]


def end_solid(e, R, O):
    """bold stand-in of an end in the part frame: its bosses minus its bores (bore-only ends: the bores as cylinders)"""
    loc = lambda p: R @ (p - O)
    Dl = R @ e["D"]
    boss = [t for t in e["ranges"] if not t[0]["hole"]]; holes = [t for t in e["ranges"] if t[0]["hole"]]
    def cyl(f, a, b):
        base = loc(e["O"] + e["D"] * a)
        return cq.Solid.makeCylinder(f["d"] / 2, max(b - a, 0.05), cq.Vector(*base), cq.Vector(*Dl))
    if boss:
        s = None
        for t in boss:
            c = cyl(*t); s = c if s is None else s.fuse(c)
        for t in holes:
            try:
                s = s.cut(cyl(*t))
            except Exception:
                pass
        return s
    s = None
    for t in holes:
        c = cyl(*t); s = c if s is None else s.fuse(c)
    return s


def angle_arc(sh, cx, cy, r, a0, a1, label, h=2.4):
    """arc dimension between directions a0 -> a1 (degrees, paper frame) at (cx, cy)"""
    if abs(a1 - a0) < 0.3:
        sh.text(cx + r * 0.8, cy + r * 0.3, label, h); return
    lo, hi = min(a0, a1), max(a0, a1)
    sh.ax.add_patch(Arc((cx, cy), 2 * r, 2 * r, theta1=lo, theta2=hi, lw=LW["dim"] * PT, color=INK))
    for a, sg in ((lo, 1), (hi, -1)):
        x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        sh.arrow(x, y, -math.sin(math.radians(a)) * -sg, math.cos(math.radians(a)) * -sg, 2.2)
    m = math.radians((lo + hi) / 2)
    sh.text(cx + (r + 3.5) * math.cos(m), cy + (r + 3.5) * math.sin(m), label, h, ha="center", va="center")


def proj(p, view):
    N, Vx = (np.array(v, float) for v in IVIEWS[view]); Vy = np.cross(N, Vx)
    return np.array([np.dot(p, Vx), np.dot(p, Vy)])


def fmt_s(x):
    return f"{x:.2f}"


# ------------------------------------------------------------------ part sheet
def interface_sheet(spec, info, names, sheet_no, n_sheets, pdf, png, pose=None):
    shape_w = load(spec["step"])
    if pose:
        shape_w = pose(spec["step"], shape_w)                # rest pose: end order and names match the kinematic sheet
    ends, sec, other = part_ends(shape_w)
    if not ends:
        raise SystemExit(f"{spec['pn']}: no end components found")
    R, O = frame_of(ends, shape_w)
    loc = lambda p: R @ (p - O)
    ldir = lambda d: R @ d
    shape = transformed(shape_w, R, O)
    for i, e in enumerate(ends):
        e["name"] = names.get((spec["pn"], i)) or f"END {i + 1}"
        e["lO"] = loc(e["O"]); e["lD"] = ldir(e["D"])
        if i == 0:
            e["lX"] = np.array([1.0, 0, 0])
        else:
            v = ends[0]["lO"] - e["lO"]; x = v - e["lD"] * np.dot(v, e["lD"])
            e["lX"] = unit(x) if np.linalg.norm(x) > 1e-6 else unit(np.cross(e["lD"], [0, 0, 1.0]))
        e["lY"] = np.cross(e["lD"], e["lX"])
    vol, _ = volume(shape)
    ghost = {k: hlr(shape, *IVIEWS[k], defl=0.03)[0] for k in IVIEWS}
    bold_s = [end_solid(e, R, O) for e in ends]
    bold = {k: [] for k in IVIEWS}
    for s_ in bold_s:
        if s_ is None:
            continue
        for k in IVIEWS:
            v, h = hlr(s_.wrapped, *IVIEWS[k], defl=0.01); bold[k].append((v, h))
    axes = []
    for e in ends:
        a = e["lO"] - e["lD"] * 6; b = e["lO"] + e["lD"] * (e["top"] + 6); axes.append((a, b))
    E = {}
    for k in IVIEWS:
        pts = ghost[k] + [np.array([proj(a, k), proj(b, k)]) for a, b in axes]
        E[k] = ext(pts)
    sz = {k: E[k][1] - E[k][0] for k in E}
    sh = Sheet(); sh.border()
    room_w, room_h = 266.0, 285.0 - 122.0
    s = pick_scale(sz["front"][0] + sz["right"][0], sz["front"][1] + sz["top"][1], room_w - 40, room_h - 38)
    gx, gy = 18.0, 18.0
    fw, fh = sz["front"] * s; tw, th = sz["top"] * s; rw, rh = sz["right"] * s
    x_left = 24 + 18 + max(0.0, (room_w - 30 - (fw + gx + rw)) / 2); y_bot = 122 + 16 + max(0.0, (room_h - 36 - (fh + gy + th)) / 2)
    org = {"front": (x_left - E["front"][0][0] * s, y_bot - E["front"][0][1] * s),
           "top": (x_left - E["top"][0][0] * s, y_bot + fh + gy - E["top"][0][1] * s),
           "right": (x_left + fw + gx - E["right"][0][0] * s, y_bot - E["right"][0][1] * s)}
    P = lambda k, p: (org[k][0] + proj(p, k)[0] * s, org[k][1] + proj(p, k)[1] * s)
    labels = {"front": "FRONT  (X right, Z up)", "top": "TOP  (X right, Y up)", "right": "RIGHT  (Y right, Z up)"}
    for k in IVIEWS:
        for pl in ghost[k]:
            sh.ax.plot(org[k][0] + s * pl[:, 0], org[k][1] + s * pl[:, 1], color=GHOST, lw=0.25 * PT, solid_capstyle="round")
        for v, h in bold[k]:
            draw_polys(sh, h, s, *org[k], "hid"); draw_polys(sh, v, s, *org[k], "vis")
        for a, b in axes:
            (x0, y0), (x1, y1) = P(k, a), P(k, b)
            if math.hypot(x1 - x0, y1 - y0) > 1.0:
                sh.line([x0, x1], [y0, y1], "cen")
        lo, hi = E[k]
        sh.text(org[k][0] + (lo[0] + hi[0]) / 2 * s, org[k][1] + hi[1] * s + 5, labels[k], 2.5, ha="center")
    # reference points + end names
    for k in IVIEWS:
        for i, e in enumerate(ends):
            x, y = P(k, e["lO"])
            sh.ax.add_patch(Circle((x, y), 0.8, facecolor="white", edgecolor=INK, lw=LW["vis"] * PT, zorder=6))
            if k == "front":
                sh.text(x - 1.5, y - 4.2, e["name"], 2.4, ha="right", weight="bold")
    # dimensions: every other end against END 1
    x1, y1 = P("front", ends[0]["lO"])
    for j, e in enumerate(ends[1:]):
        lo, hi = E["front"]
        o = e["lO"]; d = e["lD"]
        xe, ye = P("front", o)
        ybase = org["front"][1] + lo[1] * s
        sh.dim((x1, y1), (xe, ye), "below", (min(y1, ye) - ybase) + 6 + 7 * j, f"x {o[0]:.2f}")
        if abs(o[2]) > 0.05:
            xr = org["front"][0] + hi[0] * s
            sh.dim((x1, y1), (xe, ye), "right", (xr - max(x1, xe)) + 6 + 7 * j, f"z {o[2]:.2f}")
        # projected axis angle in the front view: from Z (up) toward X
        axz = math.degrees(math.atan2(d[0], d[2]))
        sh.line([xe, xe], [ye, ye + 16], "dim")
        angle_arc(sh, xe, ye, 12, 90.0, 90.0 - axz, f"{abs(axz):.2f}°")
        # top view: y offset and azimuth
        xt, yt = P("top", o); xt1, yt1 = P("top", ends[0]["lO"])
        if abs(o[1]) > 0.05:
            sh.dim((xt1, yt1), (xt, yt), "left", 8 + 7 * j, f"y {o[1]:.2f}")
        if math.hypot(d[0], d[1]) > 0.01:
            phi = math.degrees(math.atan2(d[1], d[0]))
            sh.line([xt, xt + 16], [yt, yt], "dim")
            angle_arc(sh, xt, yt, 11, 0.0, phi, f"{phi:.2f}°")
        # right view: projected angle from Z toward Y
        xr_, yr_ = P("right", o)
        ayz = math.degrees(math.atan2(d[1], d[2]))
        sh.line([xr_, xr_], [yr_, yr_ + 16], "dim")
        angle_arc(sh, xr_, yr_, 10, 90.0, 90.0 - ayz, f"{abs(ayz):.2f}°")
    # ---------------- tables
    xr0 = 298
    sh.text(xr0, 281, "END POSITIONS (part frame)", 3.0, weight="bold")
    rows = []
    for e in ends:
        o, d = e["lO"], e["lD"]
        beta = math.degrees(math.acos(max(-1.0, min(1.0, d[2]))))
        phi = math.degrees(math.atan2(d[1], d[0])) if math.hypot(d[0], d[1]) > 1e-6 else 0.0
        rows.append([e["name"], f"{o[0]:.2f}", f"{o[1]:.2f}", f"{o[2]:.2f}", f"{beta:.2f}°", f"{phi:.2f}°",
                     f"{math.degrees(math.atan2(d[0], d[2])):.2f}°", f"{math.degrees(math.atan2(d[1], d[2])):.2f}°"])
    ye = sh.table(xr0, 278, [("END", 17), ("x", 13), ("y", 13), ("z", 13), ("TILT", 14), ("AZIM.", 14), ("∠XZ", 14), ("∠YZ", 14)], rows, h=2.0, rowh=4.2)
    lines = ["x, y, z: the end's reference point (on its axis, at its skin-side face).",
             "TILT: true angle between this end's axis and END 1's axis (Z).", "AZIM.: direction of that tilt, measured in the XY plane from X toward Y.",
             "∠XZ, ∠YZ: the axis projected in the FRONT and RIGHT views, from Z.", "All axes point away from the skin."]
    yy = ye - 3.4
    for t in lines:
        sh.text(xr0, yy, t, 1.75); yy -= 2.9
    if len(ends) > 1:
        sh.text(xr0, yy - 3, "AXIS RELATIONS", 3.0, weight="bold")
        rr = []
        for e in ends[1:]:
            p1, d1, p2, d2 = ends[0]["lO"], ends[0]["lD"], e["lO"], e["lD"]
            w = np.cross(d1, d2); dp = p2 - p1
            if np.linalg.norm(w) < 1e-9:
                gap = np.linalg.norm(np.cross(dp, d1)); rr.append([f"{ends[0]['name']}–{e['name']}", "parallel", f"{gap:.2f}", "–", "–"]); continue
            gap = abs(np.dot(dp, unit(w)))
            A = np.array([[np.dot(d1, d1), -np.dot(d1, d2)], [np.dot(d1, d2), -np.dot(d2, d2)]]); b = np.array([np.dot(dp, d1), np.dot(dp, d2)])
            t1, t2 = np.linalg.solve(A, b)
            rr.append([f"{ends[0]['name']}–{e['name']}", f"{math.degrees(math.acos(min(1, abs(np.dot(d1, d2))))):.2f}°", f"{gap:.2f}", f"{t1:.2f}", f"{t2:.2f}"])
        ye2 = sh.table(xr0, yy - 6, [("ENDS", 26), ("ANGLE", 18), ("AXIS GAP", 20), ("t1", 24), ("t2", 24)], rr, h=2.0, rowh=4.2)
        yy = ye2 - 3.4
        for t in ["AXIS GAP: closest distance between the two axis lines (0 = they meet).", "t1, t2: where that closest point lies along each axis from",
                  "the end's reference point (negative = toward the skin)."]:
            sh.text(xr0, yy, t, 1.75); yy -= 2.9
    # iso of the real part (ghost reference)
    Vi = hlr(shape, ED.ISO_N, ED.ISO_X, defl=0.03)[0]
    lo, hi = ext(Vi); szi = hi - lo
    si = pick_scale(szi[0], szi[1], 100, max(26.0, yy - 66 - 18))
    hbox = szi[1] * si
    iy = yy - 8 - hbox - lo[1] * si; ix = xr0 + (110 - szi[0] * si) / 2 - lo[0] * si
    draw_polys(sh, Vi, si, ix, iy, "vis")
    sh.text(xr0, yy - 4, f"BUILT PART, ISOMETRIC ({scale_txt(si)}), for reference", 2.2)
    # end stacks + clocked features (bottom-left)
    sh.text(24, 116, "END STACKS  (along each end's own axis, s from its skin-side face, mm)", 3.0, weight="bold")
    rows = []
    for e in ends:
        for f, a, b in e["ranges"]:
            sz_, fn = callout(f)
            rows.append([e["name"], sz_, fn, "bore" if f["hole"] else "pin / boss", fmt_s(a), fmt_s(b)])
        rows.append([e["name"], "faces at s =", ", ".join(fmt_s(v) for v in e["levels"][:9]) + (" …" if len(e["levels"]) > 9 else ""), "", "", ""])
    rows = rows[:14]
    ye = sh.table(24, 113, [("END", 16), ("SIZE / FIT", 25), ("FUNCTION / FACE LEVELS", 82), ("TYPE", 18), ("FROM s", 16), ("TO s", 16)], rows, h=2.0, rowh=4.0)
    crow = []
    for g, host in sec:
        e = host
        rv = loc(g["c"]) - e["lO"]; rv = rv - e["lD"] * np.dot(rv, e["lD"])
        ang = math.degrees(math.atan2(np.dot(rv, e["lY"]), np.dot(rv, e["lX"])))
        lev = np.dot(loc(g["c"]) - e["lO"], e["lD"])
        for f in g["f"]:
            sz_, fn = callout(f)
            crow.append([e["name"], sz_, fn, f"{np.linalg.norm(rv):.2f}", f"{ang:.1f}°", f"{lev - f['L'] / 2:.2f} – {lev + f['L'] / 2:.2f}"])
    for g, _ in other:
        for f in g["f"]:
            sz_, fn = callout(f); c = loc(f["c"])
            crow.append(["part", sz_, fn, f"at {c[0]:.1f}, {c[1]:.1f}, {c[2]:.1f}", "", f"len {f['L']:.2f}"])
    if crow and ye > 30:
        sh.text(24, ye - 5, "CLOCKED AND OTHER FEATURES  (angle about the end's axis from its X reference: toward the other end; END 1: X)", 2.3, weight="bold")
        nmax = max(0, int((ye - 9 - 12) / 4.0) - 1)
        sh.table(24, ye - 7, [("END", 16), ("SIZE / FIT", 25), ("FUNCTION", 60), ("RADIUS", 32), ("ANGLE", 14), ("LEVEL s", 26)], crow[:nmax], h=1.9, rowh=4.0)
    # notes + title block
    n = [f"Ends are the interfaces to keep: positions, angles and end stacks above. The bar between them is free: built path in STEP {os.path.basename(spec['step'])}.",
         "Keep the bar 8 × 3 mm section minimum, 2-14 mm off the skin, clear of the neighbouring parts over the range of motion.",
         "Fits: hub Ø7 j5 / Ø11 J6 (MR117-2RS pairs); knee Ø3 j5 / Ø6 J6 (MR63ZZ). General tolerances ISO 2768-mK."] + spec.get("notes", [])[:2]
    sh.notes(232, 106, n, h=2.0, width=176)
    sh.title_block({"title": spec["title"], "dwg": f"EXO-{info['key']}-{spec['pn']}", "design": info["design"], "pn": spec["pn"], "material": spec["material"],
                    "mass": f"{vol * spec['rho'] / 1000:.2f} g", "qty": spec["qty"], "finish": spec["finish"], "scale": scale_txt(s),
                    "sheet": f"{sheet_no} / {n_sheets}", "src": os.path.basename(spec["step"])[:44]})
    sh.save(pdf, png)
    return {"pn": spec["pn"], "title": spec["title"], "ends": [e["name"] for e in ends], "scale": scale_txt(s)}


# ------------------------------------------------------------------ assembly layout
BVIEWS = {"behind": ((-1, 0, 0), (0, 0, 1)), "side": ((0, 0, 1), (1, 0, 0)), "above": ((0, 1, 0), (0, 0, 1))}


def joint_table(parts, joints, pose):
    """world-frame joints at the rest pose; joints: [(name, part a, part b)] - each joint is the coaxial pair of ends
    of the two parts it connects (matched by geometry, not by order)"""
    pe = {}
    for p in parts:
        ends, _, _ = part_ends(pose(p["step"], load(p["step"]))); pe[p["pn"]] = ends
    out = []
    for name, pa_, pb_ in joints:
        if pa_ not in pe or pb_ not in pe or not pe[pa_] or not pe[pb_]:
            print(f"  {name}: cannot match ({pa_}, {pb_})", flush=True); continue
        best = None
        for i, ea in enumerate(pe[pa_]):
            for k, eb in enumerate(pe[pb_]):
                ang = math.degrees(math.acos(min(1.0, abs(np.dot(ea["D"], eb["D"]))))); v = eb["O"] - ea["O"]
                off = np.linalg.norm(v - ea["D"] * np.dot(v, ea["D"]))
                if best is None or ang + off < best[0]:
                    best = (ang + off, i, k, ang, off)
        _, i, k, ang, off = best
        print(f"  {name}: {pa_}[{i}] / {pb_}[{k}] axis angle {ang:.3f} deg, offset {off:.3f} mm", flush=True)
        members = [(pa_, i), (pb_, k)]
        es = [pe[pa_][i], pe[pb_][k]]
        if not es:
            continue
        D = unit(np.mean([e["D"] if np.dot(e["D"], es[0]["D"]) > 0 else -e["D"] for e in es], axis=0))
        P = es[0]["O"]
        s0 = min(np.dot(e["O"] - P, D) for e in es); top = max(np.dot(e["O"] - P, D) + e["top"] for e in es)
        O = P + D * s0
        f = float(np.dot(O, D)); off = float(np.linalg.norm(O - D * np.dot(O, D)))
        out.append({"name": name, "D": D, "O": O, "f": f, "off": off, "h": top - s0, "members": members})
    return out, pe


def skeleton_sheet(info, J, sheet_no, n_sheets, pdf, png):
    sh = Sheet(); sh.border()
    hubs = []
    for j in J:
        hub_d = 20.0 if j["name"].startswith(("J", "K")) else 9.0
        hubs.append(cq.Solid.makeCylinder(hub_d / 2, max(j["h"], 2.0), cq.Vector(*j["O"]), cq.Vector(*j["D"])))
    hc = cq.Compound.makeCompound(hubs).wrapped
    V = {k: hlr(hc, *BVIEWS[k], defl=0.02) for k in BVIEWS}
    cen = [j["O"] + j["D"] * j["h"] / 2 for j in J]
    def pv(p, k):
        N, Vx = (np.array(v, float) for v in BVIEWS[k]); return np.array([np.dot(p, Vx), np.dot(p, np.cross(N, Vx))])
    E = {}
    for k in BVIEWS:
        pts = V[k][0] + [np.array([pv(np.zeros(3), k)]), np.array([pv(c, k) for c in cen])]
        E[k] = ext(pts)
    sz = {k: E[k][1] - E[k][0] for k in E}
    s = pick_scale(sz["behind"][0] + sz["side"][0] + sz["above"][0] + 60, max(sz[k][1] for k in sz), 380, 140)
    x = 30.0; org = {}
    for k in ("behind", "side", "above"):
        lo, hi = E[k]
        org[k] = (x - lo[0] * s, 132 + (140 - sz[k][1] * s) / 2 - lo[1] * s)
        x += sz[k][0] * s + 30
    titles = {"behind": "FROM BEHIND (z right, y up)", "side": "FROM THE RIGHT SIDE (x right, y up)", "above": "FROM ABOVE (z right, x up)"}
    for k in BVIEWS:
        ox, oy = org[k]
        draw_polys(sh, V[k][1], s, ox, oy, "hid"); draw_polys(sh, V[k][0], s, ox, oy, "vis")
        g = pv(np.zeros(3), k); gx, gy = ox + g[0] * s, oy + g[1] * s
        sh.line([gx - 3, gx + 3], [gy, gy], "vis"); sh.line([gx, gx], [gy - 3, gy + 3], "vis"); sh.text(gx + 2, gy - 4, "GH", 2.2)
        for j, c in zip(J, cen):
            a = j["O"] - j["D"] * (j["f"] if j["name"].startswith(("J", "K")) else 4); b = j["O"] + j["D"] * (j["h"] + 6)
            pa, pb = pv(a, k), pv(b, k)
            sh.line([ox + pa[0] * s, ox + pb[0] * s], [oy + pa[1] * s, oy + pb[1] * s], "cen")
        chain = [pv(c, k) for c in cen]
        for p0, p1 in zip(chain, chain[1:]):
            sh.line([ox + p0[0] * s, ox + p1[0] * s], [oy + p0[1] * s, oy + p1[1] * s], "vis")
        for j, c in zip(J, chain):
            sh.text(ox + c[0] * s + 3, oy + c[1] * s + 2.5, j["name"], 2.4, weight="bold")
        lo, hi = E[k]
        sh.text(ox + (lo[0] + hi[0]) / 2 * s, oy + hi[1] * s + 6, titles[k], 2.6, ha="center")
    rows = []
    prev = None
    for j, c in zip(J, cen):
        d = j["D"]; el = math.degrees(math.asin(max(-1, min(1, d[1])))); az = math.degrees(math.atan2(d[2], d[0]))
        ang = gap = dist = ""
        if prev is not None:
            pd, pO = prev["D"], prev["O"]
            ang = f"{math.degrees(math.acos(min(1, abs(np.dot(pd, d))))):.2f}°"
            w = np.cross(pd, d)
            gap = f"{abs(np.dot(j['O'] - pO, unit(w))):.2f}" if np.linalg.norm(w) > 1e-9 else f"{np.linalg.norm(np.cross(j['O'] - pO, pd)):.2f}"
            dist = f"{np.linalg.norm(c - pc):.2f}"
        rows.append([j["name"], f"{d[0]:+.4f} {d[1]:+.4f} {d[2]:+.4f}", f"{el:.2f}°", f"{az:.2f}°", f"{j['O'][0]:.2f}, {j['O'][1]:.2f}, {j['O'][2]:.2f}",
                     f"{j['f']:.2f}", f"{j['off']:.2f}", f"{j['h']:.2f}", ang, gap, dist])
        prev, pc = j, c
    sh.text(24, 118, "JOINT AXES IN THE BODY FRAME  (origin: GH centre; x anterior, y up, z lateral; rest pose; mm)", 3.0, weight="bold")
    ye = sh.table(24, 114, [("JOINT", 16), ("AXIS i, j, k (outward)", 50), ("ELEV.", 15), ("AZIM.", 15), ("REF. POINT x, y, z", 46), ("FACE FROM GH", 22),
                             ("AXIS OFF GH", 20), ("HUB H", 15), ("∠ TO PREV.", 19), ("GAP TO PREV.", 22), ("HUB CTR DIST.", 23)], rows, h=2.0, rowh=4.3)
    expl = ["REF. POINT: on the axis at the joint's skin-side face (the lower member's face). FACE FROM GH: that face's distance from GH along the axis.",
            "AXIS OFF GH: closest distance from GH to the axis line (0 = the axis passes through the shoulder centre).  HUB H: skin-side face to crown.",
            "ELEV.: angle above horizontal.  AZIM.: angle in the horizontal plane from anterior (+x) toward lateral (+z).",
            "∠ / GAP TO PREV.: angle and closest distance between this axis and the previous joint's axis (the link between them).  HUB CTR DIST.: straight distance between hub mid-points."]
    yy = ye - 4
    for t in expl:
        sh.text(24, yy, t, 1.9); yy -= 3.4
    sh.notes(24, yy - 4, info["skel_notes"], h=2.1, width=200)
    sh.title_block({"title": info["skel_title"], "dwg": f"EXO-{info['key']}-KIN", "design": info["design"], "pn": f"{info['key']}-KIN", "material": "–",
                    "mass": "–", "qty": 1, "finish": "–", "scale": scale_txt(s), "sheet": f"{sheet_no} / {n_sheets}", "src": "joint axes from the part STEP files"})
    sh.save(pdf, png)


# ------------------------------------------------------------------ sets
JOINTS = {
    "B": [("J1", "D8-01", "D8-02"), ("J2", "D8-02", "D8-03"), ("J3", "D8-03", "D8-04"), ("pin a", "D8-04", "D8-05"), ("pin b", "D8-05", "D8-06")],
    "A": [("J1", "D8-01", "D8-02a"), ("K", "D8-02a", "D8-02b"), ("J2", "D8-02b", "D8-03"), ("J3", "D8-03", "D8-04"),
          ("crank pivot", "D8-02b", "D9-01"), ("pin a", "D8-04", "D8-05"), ("pin b", "D8-05", "D8-06")],
}


def main():
    key = sys.argv[1].upper() if len(sys.argv) > 1 else "B"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    info, parts, hub, bom = {"A": ED.set_A, "B": ED.set_B}[key]()
    info["skel_title"] = {"A": "Cone-cut chain, kinematic layout", "B": "Pin knee H1b, kinematic layout"}[key]
    info["skel_notes"] = ["Use this sheet with the part sheets: each part's END POSITIONS are its slice of this table, in its own frame.",
                          "J1, J2 axes pass through GH (spherical chain); J3 is offset. Knee pins are parallel to J3." if key == "B" else
                          "J1, K, J2 axes pass through GH (spherical chain); J3 is offset; K is slaved by the cam drive. Knee pins are parallel to J3.",
                          "Rest pose of the built CAD (arm at the side). Joint angles change with the arm; the part-frame geometry does not."]
    out = os.path.join(REPO, "docs", "drawings", key); os.makedirs(out, exist_ok=True)
    made = [p for p in parts if p["pn"].startswith("D") and p["pn"] != "D8-07"] + [p for p in parts if not p["pn"].startswith("D") or p["pn"] == "D8-07"]
    pose = rest_posing({"A": "user_conecut_knee", "B": "user_pinknee_h1b"}[key])
    J, pe = joint_table([p for p in parts if p["pn"][:2] in ("D8", "D9")], JOINTS[key], pose)
    for j in J:                                              # the two parts meeting at a joint must share its axis at rest
        print(f"  {j['name']}: members {j['members']}", flush=True)
    names = {}
    for j in J:
        for pn, i in j["members"]:
            names[(pn, i)] = j["name"]
    for pn, ends in pe.items():                              # ends that are not chain joints: name them by what they carry
        for i, e in enumerate(ends):
            ds = {(f["hole"], round(f["d"], 1)) for f in e["f"]}
            label = ("nose dowel" if (True, 2.5) in ds else "J2 cap seat" if (True, 20.0) in ds else
                     "follower pin" if (True, 3.0) in ds else f"END {i + 1}")
            names.setdefault((pn, i), label)
    n = 3 + len(made)
    sheets = []
    pdf_path = os.path.join(out, f"{key}_drawings.pdf" if not only else f"{key}_{only}.pdf")
    with PdfPages(pdf_path) as pdf:
        if not only:
            skeleton_sheet(info, J, 1, n, pdf, os.path.join(out, "01_KIN.png")); sheets.append({"file": "01_KIN.png", "title": info["skel_title"]})
            print("KIN done", flush=True)
            ED.ga_sheet(info, bom, 2, n, pdf, os.path.join(out, "02_GA.png"), pose=pose); sheets.append({"file": "02_GA.png", "title": info["ga_title"]})
            print("GA done", flush=True)
            ED.hub_sheet(info, hub, 3, n, pdf, os.path.join(out, "03_HUB.png")); sheets.append({"file": "03_HUB.png", "title": "Ø20 hub stack, section"})
            print("HUB done", flush=True)
        for i, p in enumerate(made, 4):
            if only and p["pn"] != only:
                continue
            fn = f"{i:02d}_{p['pn']}.png"
            ends, _, _ = part_ends(pose(p["step"], load(p["step"])))
            if ends:
                r = interface_sheet(p, info, names, i, n, pdf, os.path.join(out, fn), pose=pose)
            else:                                            # no joint ends (e.g. the cuff plate): the hole-table sheet
                r = ED.detail_sheet(p, info, i, n, pdf, os.path.join(out, fn))
            r["file"] = fn; sheets.append(r)
            print(p["pn"], r, flush=True)
    if not only:
        for f in os.listdir(out):
            if f.endswith(".png") and f not in {x["file"] for x in sheets}:
                os.remove(os.path.join(out, f))
        json.dump({"set": key, "design": info["design"], "pdf": os.path.basename(pdf_path), "sheets": sheets}, open(os.path.join(out, "sheets.json"), "w"), indent=1)
    print("->", pdf_path)


if __name__ == "__main__":
    main()
