"""Measured feature inventory of the user-style 3R custom parts, read from the exported STEP B-reps (read-only: no CAD is
built or changed here). One JSON per part in this folder + the plain-words README is written by hand from them.

    python3 measure_inventory.py            # D6-01..D6-04 (+ the upper-arm cuff if its STEP is in ../step/)

Every number comes from the B-rep (OCP surface adaptors, GProp, BRepAlgoAPI_Section, BRepClass3d); build.json values
appear only in the `build_json_check` blocks, next to the measured value they are compared with.
Coordinates: each STEP is in its group's local frame (rig frame when that group is at identity: x anterior, y up,
z lateral, origin GH centre, mm). Angles in degrees.
"""
import json, math, os, sys, collections
import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere, GeomAbs_Torus, GeomAbs_BSplineSurface, GeomAbs_BezierSurface, GeomAbs_SurfaceOfRevolution, GeomAbs_SurfaceOfExtrusion, GeomAbs_OffsetSurface
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_OUT, TopAbs_IN, TopAbs_ON, TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED
from OCP.gp import gp_Pnt, gp_Dir, gp_Pln, gp_Ax3
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line, GeomAbs_Circle

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
DES = os.path.join(REPO, "pipeline", "full-exo", "designs", "param2_r20_n3_s1414_4")
OUTD = os.path.dirname(os.path.abspath(__file__))
STEPD = os.path.join(DES, "step"); DRAW_STEP = os.path.join(OUTD, "..", "step")
BUILD = json.load(open(os.path.join(DES, "build.json")))
RHO = {"Ti-6Al-4V": 4.43, "7075-T6": 2.81, "AlSi10Mg": 2.67}
T_BAR, U0 = 3.0, 3.15                                                     # bar thickness, upper-pad level (param_build LV) - for the build.json cross-check only
FACES = BUILD["faces"]


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def P3(p): return np.array([p.X(), p.Y(), p.Z()])
def D3(d): return np.array([d.X(), d.Y(), d.Z()])
def r4(x, n=4):
    if isinstance(x, (list, tuple, np.ndarray)): return [r4(v, n) for v in x]
    if x is None or isinstance(x, (str, bool)): return x
    return round(float(x), n)


def canon(d):
    """direction with a fixed sign (largest |component| positive) for grouping and reporting"""
    d = unit(d); i = int(np.argmax(np.abs(d))); return d if d[i] > 0 else -d


def foot(p, d):
    """point of the line (p, d) closest to the origin (GH)"""
    d = unit(d); return p - (p @ d) * d


def perp_basis(n):
    n = unit(n); a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    x = unit(np.cross(a, n)); return x, np.cross(n, x)


# ---------------------------------------------------------------- faces
def face_record(i, f):
    ad = BRepAdaptor_Surface(f.wrapped); t = ad.GetType()
    g = GProp_GProps(); BRepGProp.SurfaceProperties_s(f.wrapped, g); area = g.Mass(); c = P3(g.CentreOfMass())
    bb = f.BoundingBox()
    u0, u1, v0, v1 = ad.FirstUParameter(), ad.LastUParameter(), ad.FirstVParameter(), ad.LastVParameter()
    ps = P3(ad.Value((u0 + u1) / 2, (v0 + v1) / 2))                        # a point on the surface (the area centroid of a full ring is on its axis)
    try: n_out = np.array(f.normalAt(cq.Vector(*ps)).toTuple())
    except Exception: n_out = None
    rec = dict(id=i, area_mm2=area, centroid=c, bbox=[bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax])
    if t == GeomAbs_Plane:
        pl = ad.Plane(); n = D3(pl.Axis().Direction())
        if f.wrapped.Orientation() == TopAbs_REVERSED: n = -n
        rec.update(type="plane", normal=n, offset_from_GH=float(n @ c), point=c)
    elif t == GeomAbs_Cylinder:
        cy = ad.Cylinder(); ax3 = cy.Position(); d = D3(ax3.Direction()); p = P3(ax3.Location()); X, Y = D3(ax3.XDirection()), D3(ax3.YDirection())
        r = cy.Radius(); pa = p + ((ps - p) @ d) * d; radial = unit(ps - pa)
        convex = None if n_out is None else bool(n_out @ radial > 0)
        rec.update(type="cylinder", radius=r, axis_dir=d, axis_point=p, axis_foot_GH=foot(p, d), u_span_deg=math.degrees(u1 - u0),
                   v_range=[v0, v1], start_dir=math.cos(u0) * X + math.sin(u0) * Y, end_dir=math.cos(u1) * X + math.sin(u1) * Y,
                   u_ccw_about=unit(np.cross(X, Y)), convex=convex)
    elif t == GeomAbs_Cone:
        co = ad.Cone(); ax3 = co.Position(); d = D3(ax3.Direction()); apex = P3(co.Apex())
        rec.update(type="cone", semi_angle_deg=math.degrees(co.SemiAngle()), ref_radius=co.RefRadius(), axis_dir=d, axis_point=P3(ax3.Location()),
                   apex=apex, axis_foot_GH=foot(apex, d), u_span_deg=math.degrees(u1 - u0), v_range=[v0, v1])
        pa = apex + ((ps - apex) @ d) * d; radial = unit(ps - pa); rec["convex"] = None if n_out is None else bool(n_out @ radial > 0)
    elif t == GeomAbs_Torus:
        to = ad.Torus(); ax3 = to.Position(); d = D3(ax3.Direction()); p = P3(ax3.Location())
        rec.update(type="torus", centre=p, axis_dir=d, major_radius=to.MajorRadius(), minor_radius=to.MinorRadius(),
                   u_span_deg=math.degrees(u1 - u0), v_span_deg=math.degrees(v1 - v0))
        # convex (a round on an outside edge) when the outward normal points away from the tube's centre circle
        pr = ps - p - ((ps - p) @ d) * d; q = p + to.MajorRadius() * unit(pr)
        rec["convex"] = None if n_out is None else bool(n_out @ unit(ps - q) > 0)
    elif t == GeomAbs_Sphere:
        sp = ad.Sphere(); rec.update(type="sphere", centre=P3(sp.Location()), radius=sp.Radius())
    elif t in (GeomAbs_BSplineSurface, GeomAbs_BezierSurface):
        bs = ad.BSpline() if t == GeomAbs_BSplineSurface else None
        rec.update(type="B-spline", degree_uv=[bs.UDegree(), bs.VDegree()] if bs else None, poles_uv=[bs.NbUPoles(), bs.NbVPoles()] if bs else None)
    else:
        rec.update(type={GeomAbs_SurfaceOfRevolution: "revolution", GeomAbs_SurfaceOfExtrusion: "extrusion", GeomAbs_OffsetSurface: "offset"}.get(t, str(t)))
    rec["surface_point"] = ps; rec["outward_normal_at_surface_point"] = n_out
    return rec


def neighbours(s):
    fm = TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(s.wrapped, TopAbs_FACE, fm)
    M = TopTools_IndexedDataMapOfShapeListOfShape(); TopExp.MapShapesAndAncestors_s(s.wrapped, TopAbs_EDGE, TopAbs_FACE, M)
    nb = collections.defaultdict(set)
    for i in range(1, M.Extent() + 1):
        ids = [fm.FindIndex(f) - 1 for f in M.FindFromIndex(i)]
        for a in ids:
            for b in ids:
                if a != b: nb[a].add(b)
    return {k: sorted(v) for k, v in nb.items()}


def classify(s, p):
    c = BRepClass3d_SolidClassifier(s.wrapped, gp_Pnt(*map(float, p)), 1e-6); st = c.State()
    return "out" if st == TopAbs_OUT else ("in" if st == TopAbs_IN else "on")


# ---------------------------------------------------------------- axes, revolved features, holes
def coaxial_groups(F, tol_ang=1e-4, tol_d=2e-3):
    """faces of revolution (cylinder, cone, torus, sphere centre on the axis) grouped by their axis line"""
    G = []
    for f in F:
        if f["type"] not in ("cylinder", "cone", "torus"): continue
        d = canon(f["axis_dir"]); p = foot(f["axis_point"] if f["type"] != "cone" else f["apex"], d) if f["type"] != "torus" else foot(f["centre"], d)
        for g in G:
            if np.linalg.norm(np.cross(g["d"], d)) < tol_ang and np.linalg.norm(np.cross(p - g["p"], g["d"])) < tol_d:
                g["faces"].append(f["id"]); break
        else: G.append(dict(d=d, p=p, faces=[f["id"]]))
    return G


def z_on(f, d, p0):
    """axial extent [z0, z1] of a face of revolution along the axis (d, p0): from the face's bbox corners is too crude, so
    use its v range when the surface's own axis is +-d, else sample the boundary"""
    if f["type"] == "cylinder":
        sd = 1.0 if f["axis_dir"] @ d > 0 else -1.0; zp = (f["axis_point"] - p0) @ d
        a, b = zp + sd * f["v_range"][0], zp + sd * f["v_range"][1]; return sorted([a, b])
    return None


def face_axial_range(face, d, p0, n=24):
    pts = []
    for e in face.Edges():
        for t in np.linspace(0, 1, n): pts.append(np.array(e.positionAt(t).toTuple()))
    z = (np.array(pts) - p0) @ d; rr = np.linalg.norm(np.cross(np.array(pts) - p0, d), axis=1)
    return [float(z.min()), float(z.max())], [float(rr.min()), float(rr.max())]


def revolved_profile(s, F, faces, g):
    """the turned profile of one coaxial group: rings of cylinders/cones/tori + the planes square to the axis that touch it"""
    d, p0 = g["d"], g["p"]; items = []; rmax = 0.0
    for i in g["faces"]:
        f = F[i]; (z0, z1), (ra, rb) = face_axial_range(faces[i], d, p0)
        it = dict(face=i, type=f["type"], z=[z0, z1], convex=f.get("convex"), span_deg=f.get("u_span_deg"))
        if f["type"] == "cylinder": it["diameter"] = 2 * f["radius"]; rmax = max(rmax, f["radius"])
        elif f["type"] == "cone":
            it["diameter_range"] = [2 * ra, 2 * rb]; it["included_angle_deg"] = 2 * f["semi_angle_deg"]; rmax = max(rmax, rb)
        elif f["type"] == "torus": it["major_radius"] = f["major_radius"]; it["minor_radius"] = f["minor_radius"]; it["radius_range"] = [ra, rb]
        items.append(it)
    planes = []
    for f in F:
        if f["type"] != "plane" or abs(abs(f["normal"] @ d) - 1) > 1e-6: continue
        fz = (f["point"] - p0) @ d
        (z0, z1), (ra, rb) = face_axial_range(faces[f["id"]], d, p0)
        if ra <= rmax + 0.01: planes.append(dict(face=f["id"], z=fz, faces_toward=("+axis" if f["normal"] @ d > 0 else "-axis"), boundary_radius_range=[ra, rb]))
    return sorted(items, key=lambda x: (x["z"][0], -(x.get("diameter") or 0))), sorted(planes, key=lambda x: x["z"])


def merge_rings(items):
    """join faces of one cylinder split at seams: (diameter, z0, z1, convex) -> total span"""
    out = {}
    for it in items:
        if it["type"] != "cylinder": continue
        k = (round(it["diameter"], 4), round(it["z"][0], 3), round(it["z"][1], 3), it["convex"])
        out.setdefault(k, dict(diameter=it["diameter"], z=it["z"], convex=it["convex"], span_deg=0.0, faces=[]))
        out[k]["span_deg"] += it["span_deg"]; out[k]["faces"].append(it["face"])
    return sorted(out.values(), key=lambda x: x["z"][0])


def holes_of(s, F, faces, groups):
    """concave full-circle cylinders (+ coaxial concave cones) along one axis = a hole; THRU/blind by classifying points on
    the axis just past each end; counterbore / countersink from the larger concave rings at the open end"""
    H = []
    for gi, g in enumerate(groups):
        items, planes = revolved_profile(s, F, faces, g)
        rings = [r for r in merge_rings(items) if r["convex"] is False and r["span_deg"] > 359.0]
        cones = [it for it in items if it["type"] == "cone" and it["convex"] is False]
        if not rings: continue
        d, p0 = g["d"], g["p"]
        z0 = min([r["z"][0] for r in rings] + [c["z"][0] for c in cones]); z1 = max([r["z"][1] for r in rings] + [c["z"][1] for c in cones])
        lo, hi = classify(s, p0 + (z0 - 0.3) * d), classify(s, p0 + (z1 + 0.3) * d)
        thru = lo == "out" and hi == "out"
        dmin = min(r["diameter"] for r in rings)
        open_end = "both" if thru else ("-axis" if lo == "out" else ("+axis" if hi == "out" else "none"))
        steps = [dict(diameter=r["diameter"], z_from=r["z"][0], z_to=r["z"][1], length=r["z"][1] - r["z"][0], faces=r["faces"]) for r in rings]
        cs = [dict(diameter_from=c["diameter_range"][0], diameter_to=c["diameter_range"][1], included_angle_deg=c["included_angle_deg"], z=c["z"], face=c["face"]) for c in cones]
        h = dict(axis_dir=d, axis_point_nearest_GH=p0, axis_passes_GH_within_mm=float(np.linalg.norm(p0)), z_measured_from="axis_point_nearest_GH along axis_dir",
                 z_range=[z0, z1], length=z1 - z0, thru=thru, open_end=open_end, min_diameter=dmin, steps=steps, countersinks=cs,
                 entry_points={"-axis": p0 + z0 * d, "+axis": p0 + z1 * d},
                 floor_planes=[p for p in planes if z0 - 1e-3 <= p["z"] <= z1 + 1e-3])
        if len(rings) > 1:
            big = max(rings, key=lambda r: r["diameter"])
            at_end = "+axis" if abs(big["z"][1] - z1) < 1e-3 else ("-axis" if abs(big["z"][0] - z0) < 1e-3 else "inside")
            h["counterbore"] = dict(diameter=big["diameter"], depth=big["z"][1] - big["z"][0], at_end=at_end)
        H.append(h)
    return H


# ---------------------------------------------------------------- sections (ordered lines/arcs)
def section_2d(s, origin, n, xdir):
    """section of the solid by the plane (origin, n), as closed loops of ordered lines / arcs in (x = xdir, y = n x xdir)"""
    origin = np.asarray(origin, float); n = unit(n); xdir = unit(np.asarray(xdir) - (np.asarray(xdir) @ n) * n); ydir = np.cross(n, xdir)
    sec = BRepAlgoAPI_Section(s.wrapped, gp_Pln(gp_Ax3(gp_Pnt(*origin), gp_Dir(*n), gp_Dir(*xdir))), False)
    sec.Build(); edges = cq.Shape.cast(sec.Shape()).Edges()
    if not edges: return []
    wires = cq.Wire.combine(edges, tol=1e-4)
    to2 = lambda p: [float((p - origin) @ xdir), float((p - origin) @ ydir)]
    loops = []
    for w in wires:
        ex = BRepTools_WireExplorer(w.wrapped); segs = []
        while ex.More():
            e = cq.Edge(ex.Current()); rev = ex.Current().Orientation() == TopAbs_REVERSED
            a, b = np.array(e.startPoint().toTuple()), np.array(e.endPoint().toTuple())
            if rev: a, b = b, a
            L = e.Length(); gt = e.geomType()
            if gt == "LINE": segs.append(dict(kind="line", start=to2(a), end=to2(b), length=L))
            elif gt == "CIRCLE":
                c = np.array(BRepAdaptor_Curve(e.wrapped).Circle().Location().Coord()); r = e.radius()
                m = np.array(e.positionAt(0.5).toTuple())
                va, vm = to2(a), to2(m); cc = to2(c)
                cr = (va[0] - cc[0]) * (vm[1] - cc[1]) - (va[1] - cc[1]) * (vm[0] - cc[0])
                sw = math.degrees(L / r) * (1 if cr > 0 else -1)
                segs.append(dict(kind="arc", centre=cc, radius=r, start=to2(a), end=to2(b), sweep_deg=sw, length=L))
            else: segs.append(dict(kind=gt.lower(), start=to2(a), end=to2(b), length=L))
            ex.Next()
        loops.append(merge_segs(segs))
    loops.sort(key=lambda l: -sum(x["length"] for x in l))
    return [dict(closed=bool(np.allclose(l[0]["start"], l[-1]["end"], atol=1e-3)) if l else False, n_segments=len(l), perimeter=sum(x["length"] for x in l), segments=l) for l in loops]


def merge_segs(segs):
    out = []
    for sg in segs:
        if out:
            pv = out[-1]
            if pv["kind"] == sg["kind"] == "arc" and np.allclose(pv["centre"], sg["centre"], atol=2e-3) and abs(pv["radius"] - sg["radius"]) < 2e-3 and np.sign(pv["sweep_deg"]) == np.sign(sg["sweep_deg"]):
                pv["end"] = sg["end"]; pv["sweep_deg"] += sg["sweep_deg"]; pv["length"] += sg["length"]; continue
            if pv["kind"] == sg["kind"] == "line":
                u1 = unit(np.subtract(pv["end"], pv["start"])); u2 = unit(np.subtract(sg["end"], sg["start"]))
                if abs(u1 @ u2 - 1) < 1e-7: pv["end"] = sg["end"]; pv["length"] += sg["length"]; continue
        out.append(dict(sg))
    return out


# ---------------------------------------------------------------- bent bar: arcs from coaxial cylinders square to the sketch plane
def bar_chain(F, nP, ex, origin2=np.zeros(3), t=T_BAR, start_pt=None, rmin=1.4, skip_faces=()):
    """the bar's centre line in its sketch plane (origin2, ex, ey = nP x ex) as an ordered list of tangent arcs / lines,
    recovered from the cylinders whose axes are normal to the plane: inner and outer faces of one arc are coaxial cylinders
    t apart in radius, centre-line radius = their mean. Pocket floors (same centre, other radius) reported separately."""
    nP = unit(nP); ex = unit(ex - (ex @ nP) * nP); ey = np.cross(nP, ex)
    to2 = lambda p: np.array([(p - origin2) @ ex, (p - origin2) @ ey])
    cyl = [f for f in F if f["type"] == "cylinder" and abs(abs(f["axis_dir"] @ nP) - 1) < 1e-6 and f["radius"] > rmin and f["id"] not in skip_faces]
    groups = []
    for f in cyl:
        c = to2(f["axis_point"])
        for g in groups:
            if np.linalg.norm(g["c"] - c) < 5e-3: g["f"].append(f); break
        else: groups.append(dict(c=c, f=[f]))
    arcs = []
    for g in groups:
        radii = sorted({round(f["radius"], 4) for f in g["f"]})
        pair = [(a, b) for a in radii for b in radii if abs(b - a - t) < 2e-3]
        if not pair: continue
        ri, ro = pair[0]; Rc = (ri + ro) / 2
        # angular span of the centre line = union of the spans of the inner (skin-side or not) faces at ri and ro
        angs = []
        for f in g["f"]:
            if abs(f["radius"] - ri) > 2e-3 and abs(f["radius"] - ro) > 2e-3: continue
            sdir, edir = f["start_dir"], f["end_dir"]
            ccw = 1.0 if f["u_ccw_about"] @ nP > 0 else -1.0
            th0 = math.atan2(sdir @ ey, sdir @ ex); sw = math.radians(f["u_span_deg"]) * ccw
            lo, hi = (th0, th0 + sw) if sw > 0 else (th0 + sw, th0)
            angs.append((lo, hi))
        # union on the circle: unwrap relative to the first interval
        ref = angs[0][0]; iv = []
        for lo, hi in angs:
            k = round((lo - ref) / (2 * math.pi)); iv.append((lo - 2 * math.pi * k, hi - 2 * math.pi * k))
        lo, hi = min(i[0] for i in iv), max(i[1] for i in iv)
        others = sorted({round(f["radius"], 4) for f in g["f"]} - {ri, ro})
        arcs.append(dict(centre_2d=g["c"], radius=Rc, inner_face_radius=ri, outer_face_radius=ro, th=(lo, hi), faces=sorted(f["id"] for f in g["f"]),
                         other_coaxial_radii=others))
    pt = lambda a, th: a["centre_2d"] + a["radius"] * np.array([math.cos(th), math.sin(th)])
    # order the arcs along the chain, starting at the arc end nearest start_pt
    cur = np.asarray(start_pt, float) if start_pt is not None else None; chain = []; left = list(range(len(arcs)))
    if cur is None:
        ends = [(pt(arcs[i], arcs[i]["th"][e]), i, e) for i in left for e in (0, 1)]
        cur = min(ends, key=lambda x: np.linalg.norm(x[0]))[0]                       # nearest to GH (fallback)
    while left:
        best = min(((np.linalg.norm(pt(arcs[i], arcs[i]["th"][e]) - cur), i, e) for i in left for e in (0, 1)))
        _, i, e = best; a = arcs[i]; left.remove(i)
        th_s, th_e = (a["th"][0], a["th"][1]) if e == 0 else (a["th"][1], a["th"][0])
        ps, pe = pt(a, th_s), pt(a, th_e); sweep = math.degrees(th_e - th_s)
        if chain or start_pt is not None:
            gap = np.linalg.norm(ps - cur)
            if gap > 1e-3: chain.append(dict(kind="line", start=cur.copy(), end=ps, length=gap, direction_deg=math.degrees(math.atan2(*(ps - cur)[::-1]))))
        chain.append(dict(kind="arc", turn="left (CCW, centre on the GH side when heading out)" if sweep > 0 else "right (CW)", radius=a["radius"],
                          signed_radius=a["radius"] * (1 if sweep > 0 else -1), curvature_per_mm=(1 if sweep > 0 else -1) / a["radius"],
                          centre=a["centre_2d"], start=ps, end=pe, sweep_deg=sweep, length=a["radius"] * abs(math.radians(sweep)),
                          inner_outer_face_radii=[a["inner_face_radius"], a["outer_face_radius"]], other_coaxial_face_radii=a["other_coaxial_radii"], faces=a["faces"]))
        cur = pe
    return chain, dict(origin=origin2, x_axis=ex, y_axis=ey, normal=nP)


def chain_from_build(start, segs):
    """the same chain from build.json (curvature, length) segments: sketch2d.advance()"""
    x, y, p = start; out = []
    for k, l in segs:
        if abs(k) < 1e-9: x1, y1, p1 = x + l * math.cos(p), y + l * math.sin(p), p; c = None
        else:
            x1, y1, p1 = x + (math.sin(p + k * l) - math.sin(p)) / k, y - (math.cos(p + k * l) - math.cos(p)) / k, p + k * l
            c = [x - math.sin(p) / k, y + math.cos(p) / k]
        out.append(dict(curvature=k, radius=None if abs(k) < 1e-9 else 1 / k, length=l, start=[x, y], end=[x1, y1], centre=c, sweep_deg=math.degrees(k * l)))
        x, y, p = x1, y1, p1
    return out


def compare_chain(meas, built):
    arcs = [m for m in meas if m["kind"] == "arc"]; rows = []
    for i, b in enumerate(built):
        if b["centre"] is None: rows.append(dict(seg=i, build="line", length=b["length"])); continue
        best = min(arcs, key=lambda a: np.linalg.norm(np.subtract(a["centre"], b["centre"])) + abs(a["signed_radius"] - b["radius"])) if arcs else None
        rows.append(dict(seg=i, build_radius=b["radius"], build_length=b["length"], build_sweep_deg=b["sweep_deg"], build_centre=b["centre"],
                         measured_radius=best["signed_radius"], measured_length=best["length"], measured_sweep_deg=best["sweep_deg"], measured_centre=best["centre"],
                         d_centre_mm=float(np.linalg.norm(np.subtract(best["centre"], b["centre"]))), d_radius_mm=best["signed_radius"] - b["radius"],
                         d_length_mm=best["length"] - b["length"]))
    return rows


# ---------------------------------------------------------------- generic part summary
def summary(s, F, material, extra_rho=True):
    vol = s.Volume(); g = GProp_GProps(); BRepGProp.VolumeProperties_s(s.wrapped, g); com = P3(g.CentreOfMass())
    I = g.MatrixOfInertia(); Im = np.array([[I.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])
    w, Vv = np.linalg.eigh(Im)
    vs, _ = s.tessellate(0.05, 0.2); P = np.array([[v.x, v.y, v.z] for v in vs])
    ext = [float((P @ Vv[:, k]).max() - (P @ Vv[:, k]).min()) for k in range(3)]
    bb = s.BoundingBox()
    cnt = collections.Counter(f["type"] for f in F)
    out = dict(valid=bool(s.isValid()), solids=len(s.Solids()), faces=len(F), edges=len(s.Edges()), face_types=dict(cnt),
               volume_mm3=vol, volume_cm3=vol / 1000, surface_area_mm2=s.Area(), centre_of_volume=com,
               bbox_part_frame=dict(min=[bb.xmin, bb.ymin, bb.zmin], max=[bb.xmax, bb.ymax, bb.zmax], size=[bb.xlen, bb.ylen, bb.zlen]),
               principal_axes_extents=dict(note="extents of the part along its principal axes of inertia (density-free)", axes=[Vv[:, k] for k in range(3)], extents=ext),
               material=material, mass_g={m: vol / 1000 * r for m, r in RHO.items()},
               mass_g_as_specified=vol / 1000 * RHO[material.split(" ")[0]] if material.split(" ")[0] in RHO else None)
    return out


def edge_rounds(F, rmax=1.01):
    """blend faces: tori and cylinders with radius <= 1 mm (convex = round on an outside edge, concave = fillet)"""
    R = collections.defaultdict(lambda: dict(convex=[], concave=[]))
    for f in F:
        r = f.get("minor_radius") if f["type"] == "torus" else (f.get("radius") if f["type"] == "cylinder" else None)
        if r is None or r > rmax: continue
        R[round(r, 3)]["convex" if f.get("convex") else "concave"].append(f["id"])
    return {f"R{k:g}": dict(radius=k, convex_rounds=len(v["convex"]), concave_fillets=len(v["concave"]), faces_convex=v["convex"], faces_concave=v["concave"]) for k, v in sorted(R.items())}


def joint_axes(F, faces, s, groups, levels):
    """coaxial groups whose axis passes through GH (< 0.05 mm): the joint axes; named by the nearest build face level"""
    J = []
    for g in groups:
        if np.linalg.norm(g["p"]) > 0.05: continue
        items, planes = revolved_profile(s, F, faces, g)
        # orient the axis outward (toward the part)
        zs = [z for it in items for z in it["z"]]
        d = g["d"] if np.mean(zs) > 0 else -g["d"]
        items, planes = revolved_profile(s, F, faces, dict(g, d=d))
        zmin = min(z for it in items for z in it["z"]); name = min(levels, key=lambda k: abs(levels[k] - zmin) if zmin > levels[k] - 1 else 1e9)
        J.append(dict(joint=name, axis_dir=d, passes_GH_within_mm=float(np.linalg.norm(g["p"])), z_measured_from="GH along axis_dir",
                      build_face_level=levels[name], rings=merge_rings(items), other_revolved_faces=[it for it in items if it["type"] != "cylinder"],
                      planes_square_to_axis=planes))
    return J


def planform(F, faces, k, p_axis, level_lo, level_hi, seat=None, rmax=30.0):
    """the pad's planform sketch (in the plane square to axis k): every cylinder with axis parallel to k but not on it
    (planform arcs) and every plane parallel to k (planform lines) within rmax of the axis, in 2D (x = seat direction,
    y = k x seat), restricted to faces lying between levels level_lo..level_hi along k"""
    k = unit(k)
    arcs = []; lines = []
    for f in F:
        if f["type"] == "cylinder" and abs(abs(f["axis_dir"] @ k) - 1) < 1e-6:
            c = f["axis_point"] - (f["axis_point"] @ k) * k
            if np.linalg.norm(c) < 1e-3 or np.linalg.norm(c) > rmax: continue
            (z0, z1), _ = face_axial_range(faces[f["id"]], k, np.zeros(3))
            if z1 < level_lo - 1e-3 or z0 > level_hi + 1e-3: continue
            arcs.append((f, c, (z0, z1)))
        if f["type"] == "plane" and abs(f["normal"] @ k) < 1e-6:
            (z0, z1), (ra, rb) = face_axial_range(faces[f["id"]], k, np.zeros(3))
            if z1 < level_lo - 1e-3 or z0 > level_hi + 1e-3 or ra > rmax: continue
            lines.append((f, (z0, z1)))
    if seat is None:
        cs = [c for f, c, _ in arcs if f["convex"] is False and f["radius"] > 2]
        seat = unit(sum(cs)) if cs else perp_basis(k)[0]
    seat = unit(seat - (seat @ k) * k); yv = np.cross(k, seat)
    t2 = lambda p: [float(p @ seat), float(p @ yv)]
    A = [dict(face=f["id"], radius=f["radius"], centre=t2(c), convex=f["convex"], span_deg=f["u_span_deg"], z=list(z)) for f, c, z in arcs]
    Ls = []
    for f, z in lines:
        n = f["normal"] - (f["normal"] @ k) * k
        vs = []
        for e in faces[f["id"]].Edges():
            for tt in (0, 0.5, 1): vs.append(np.array(e.positionAt(tt).toTuple()))
        P2 = np.array([t2(v) for v in vs])
        Ls.append(dict(face=f["id"], normal_2d=t2(n), offset=float(f["point"] @ unit(n)), x_range=[float(P2[:, 0].min()), float(P2[:, 0].max())],
                       y_range=[float(P2[:, 1].min()), float(P2[:, 1].max())], z=list(z)))
    if Ls:
        mx = max(abs(l["normal_2d"][1]) > 0.99 and abs(l["y_range"][0]) for l in Ls)
        for l in Ls:
            l["role"] = ("straight side of pad/bar (half width %.3g)" % abs(l["y_range"][0]) if abs(l["normal_2d"][1]) > 0.99 and abs(abs(l["y_range"][0]) - mx) < 1e-3
                         else ("pocket wall (inside the bar width)" if abs(l["normal_2d"][1]) > 0.99 else "other line"))
    return dict(plane_x_axis_seat_dir=seat, plane_y_axis=yv, arcs=A, lines=Ls)


# ---------------------------------------------------------------- per part
def jload(path): return cq.importers.importStep(path).val()


def base_inventory(path, pid, material, title):
    s = jload(path); faces = s.Faces(); F = [face_record(i, f) for i, f in enumerate(faces)]
    nb = neighbours(s)
    for f in F: f["neighbours"] = nb.get(f["id"], [])
    G = coaxial_groups(F)
    inv = dict(part=pid, title=title, step_file=os.path.relpath(path, REPO), units="mm, degrees, g",
               frame="STEP coordinates = the part's group-local frame (equal to the rig frame when the group is at identity: x anterior, y up, z lateral, origin = GH centre)",
               summary=summary(s, F, material), holes=holes_of(s, F, faces, G), edge_rounds=edge_rounds(F))
    return s, faces, F, G, inv


def link_inventory(path, pid, name, ja, jb, upper):
    s, faces, F, G, inv = base_inventory(path, pid, "Ti-6Al-4V", BUILD["parts"][0 if pid == "D6-02" else 1]["name"])
    J = joint_axes(F, faces, s, G, {k: v for k, v in FACES.items() if k in (ja, jb)})
    inv["joint_axes"] = J
    ka = [j for j in J if j["joint"] == ja][0]["axis_dir"]; kb = [j for j in J if j["joint"] == jb][0]["axis_dir"]
    nP = unit(np.cross(ka, kb)); ex = unit(ka)
    inv["angle_between_joint_axes_deg"] = math.degrees(math.acos(np.clip(ka @ kb, -1, 1)))
    inv["build_json_check_arc_deg"] = BUILD[name]["arc_deg"]
    z0 = U0 if upper else 0.0; ha = FACES[ja] + z0 + T_BAR / 2
    chain, fr = bar_chain(F, nP, ex, start_pt=np.array([ha, 14.0]))
    built = chain_from_build((ha, 14.0, math.pi / 2), BUILD[name]["segs"])
    # side planes of the bar (normal = +-nP) -> width; pocket walls
    side = sorted({round(f["offset_from_GH"], 4) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ nP) - 1) < 1e-6 and True})
    sidep = [dict(face=f["id"], offset_along_plane_normal=float(f["point"] @ nP), area=f["area_mm2"]) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ nP) - 1) < 1e-6]
    tot = sum(c["length"] for c in chain)
    inv["bar"] = dict(
        sketch_plane=dict(note="the plane of the two joint axes through GH; 2D x = joint " + ja + " axis, y = in-plane toward joint " + jb + "; the bar is this outline extruded symmetric to its width (both sides of the plane)",
                          origin=[0, 0, 0], x_axis=fr["x_axis"], y_axis=fr["y_axis"], normal=fr["normal"]),
        centre_line_chain=chain, centre_line_length=tot,
        chain_start=chain[0]["start"] if chain else None, chain_end=chain[-1]["end"] if chain else None,
        build_json_check=dict(start=[ha, 14.0, "heading +y"], segs_curvature_length=BUILD[name]["segs"], radii=BUILD[name]["radii"], compare=compare_chain(chain, built),
                              build_total_length=sum(l for _, l in BUILD[name]["segs"])),
        planes_parallel_to_sketch_plane=sidep)
    # cross-section of the bar at the middle of the longest arc (plane square to the centre line)
    arcs = [c for c in chain if c["kind"] == "arc"]
    if arcs:
        a = max(arcs, key=lambda c: c["length"]); c2 = np.asarray(a["centre"]); th = math.atan2(*(np.asarray(a["start"]) - c2)[::-1]) + math.radians(a["sweep_deg"]) / 2
        p2 = c2 + a["radius"] * np.array([math.cos(th), math.sin(th)]); P = p2[0] * fr["x_axis"] + p2[1] * fr["y_axis"]
        tng = -math.sin(th) * fr["x_axis"] + math.cos(th) * fr["y_axis"]; radial = math.cos(th) * fr["x_axis"] + math.sin(th) * fr["y_axis"]
        inv["bar"]["cross_section_mid_longest_arc"] = dict(note="section square to the centre line at the middle of the longest arc; x = radial (away from that arc's centre), y = along the sketch-plane normal (bar width)",
                                                          at_point=P, loops=section_2d(s, P, tng, radial))
    # side-view outline: section by a plane parallel to the sketch plane, inside the pocket rim (|z| = 3.2) -> the full outer and inner arcs
    inv["bar"]["side_view_outline_z3.2"] = dict(note="section by the plane parallel to the sketch plane at +3.2 mm (inside the 1.5 mm pocket rim, clear of the 0.5 rounds): the drawn side-view outline, 2D in the sketch-plane axes",
                                               loops=section_2d(s, 3.2 * nP, nP, fr["x_axis"]))
    inv["bar"]["side_view_mid_plane_z0"] = dict(note="section by the sketch plane itself (through the pocket)", loops=section_2d(s, 0 * nP, nP, fr["x_axis"]))
    # pads
    pads = []
    for j in J:
        k = j["axis_dir"]; lv = j["build_face_level"] + (U0 if upper else 0.0)
        pads.append(dict(joint=j["joint"], axis_dir=k, pad_levels_expected=[lv, lv + T_BAR],
                         planes_square_to_axis_within_pad=[p for p in j["planes_square_to_axis"] if lv - 0.01 <= p["z"] <= lv + T_BAR + 0.01],
                         planform=planform(F, faces, k, None, lv - 0.01, lv + T_BAR + 0.01)))
    inv["pads"] = pads
    inv["pocket"] = pocket_info(F, faces, chain, fr, nP)
    inv["faces"] = F
    return inv


def pocket_info(F, faces, chain, fr, nP):
    """pocket walls (planes parallel to the sketch plane, inside the bar width), floor (cylinders coaxial with a bar arc at a
    radius between the inner and outer faces), round ends (cylinders with axis in the plane)"""
    walls = [dict(face=f["id"], offset=float(f["point"] @ nP), area=f["area_mm2"]) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ nP) - 1) < 1e-6 and abs(f["point"] @ nP) < 3.9]
    floors = []
    for c in chain:
        if c["kind"] != "arc": continue
        for r in c["other_coaxial_face_radii"]:
            out = c["inner_outer_face_radii"]; depth = min(abs(r - out[0]), abs(r - out[1]))
            side = "outer (away from GH)" if abs(r - max(out)) < abs(r - min(out)) else "inner"
            if c["signed_radius"] < 0: side = "outer (away from GH)" if abs(r - min(out)) < abs(r - max(out)) else "inner"
            floors.append(dict(arc_radius=c["signed_radius"], floor_face_radius=r, depth_below_face=depth, on_side=side))
    ends = [dict(face=f["id"], radius=f["radius"], axis_dir=f["axis_dir"], axis_point=f["axis_point"], span_deg=f["u_span_deg"])
            for f in F if f["type"] == "cylinder" and abs(f["axis_dir"] @ nP) < 1e-6 and 1.5 < f["radius"] < 4 and f["convex"] is False]
    for e in ends:
        p = e["axis_point"]; q = np.array([p @ fr["x_axis"], p @ fr["y_axis"]]); e["axis_point_2d"] = q
        # arc-length station of the pocket end along the centre line
        best = None; acc = 0.0
        for c in chain:
            if c["kind"] == "arc":
                cc = np.asarray(c["centre"]); th = math.atan2(*(q - cc)[::-1]); th0 = math.atan2(*(np.asarray(c["start"]) - cc)[::-1])
                dth = (th - th0) * (1 if c["sweep_deg"] > 0 else -1); dth = (dth + 2 * math.pi) % (2 * math.pi)
                if dth <= abs(math.radians(c["sweep_deg"])) + 1e-6:
                    st = acc + c["radius"] * dth; dist = abs(np.linalg.norm(q - cc) - c["radius"])
                    if best is None or dist < best[1]: best = (st, dist)
            acc += c["length"]
        e["station_along_centre_line"] = None if best is None else best[0]
    widths = sorted({round(abs(w["offset"]), 4) for w in walls})
    return dict(walls=walls, wall_half_offsets=widths, floors=floors, round_ends=ends,
                note="pocket width = 2 x wall offset; rim = bar half-width - wall offset; end radius = pocket half-width")


def base_part_inventory():
    path = os.path.join(STEPD, "02_D6-01_scapula_base.step")
    s, faces, F, G, inv = base_inventory(path, "D6-01", "Ti-6Al-4V", BUILD["parts"][2]["name"])
    J = joint_axes(F, faces, s, G, {"J1": FACES["J1"]}); inv["joint_axes"] = J
    k1 = J[0]["axis_dir"]
    # tab bar plane: the dominant direction of the cylinders (r > 2) square to k1, weighted by area, excluding holes/round end axes (normal to the terminal)
    cand = collections.defaultdict(float); dirs = {}
    for f in F:
        if f["type"] == "cylinder" and f["radius"] > 9 and abs(f["axis_dir"] @ k1) < 1e-6:
            key = tuple(np.round(canon(f["axis_dir"]), 4)); cand[key] += f["area_mm2"]; dirs[key] = canon(f["axis_dir"])
    nP = dirs[max(cand, key=cand.get)]
    ha = FACES["J1"] + U0 + T_BAR / 2
    chain, fr = bar_chain(F, nP, k1, start_pt=np.array([ha, 14.0]), t=T_BAR)
    arcs0 = [c for c in chain if c["kind"] == "arc"]
    if arcs0 and arcs0[0]["start"][1] < 0:                                         # make y point along the tab
        chain, fr = bar_chain(F, -nP, k1, start_pt=np.array([ha, 14.0]), t=T_BAR); nP = -nP
    inv["tab_bar"] = dict(sketch_plane=dict(note="plane through GH containing the J1 axis and the tab heading; 2D x = J1 axis, y = tab heading", x_axis=fr["x_axis"], y_axis=fr["y_axis"], normal=fr["normal"]),
                          centre_line_chain=chain, centre_line_length=sum(c["length"] for c in chain),
                          build_json_check=dict(radii=BUILD["base tab"]["radii"], heading_deg=BUILD["base tab"]["heading_deg"], terminal_height=BUILD["base tab"]["terminal_height"],
                                                start=[ha, 14.0, "heading +y"]),
                          side_view_outline_z5=dict(note="section parallel to the tab sketch plane at +5 mm", loops=section_2d(s, 5 * nP, nP, fr["x_axis"])),
                          planes_parallel_to_sketch_plane=[dict(face=f["id"], offset=float(f["point"] @ nP), area=f["area_mm2"]) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ nP) - 1) < 1e-6])
    arcs = [c for c in chain if c["kind"] == "arc"]
    if arcs:
        a = max(arcs, key=lambda c: c["length"]); c2 = np.asarray(a["centre"]); th = math.atan2(*(np.asarray(a["start"]) - c2)[::-1]) + math.radians(a["sweep_deg"]) / 2
        p2 = c2 + a["radius"] * np.array([math.cos(th), math.sin(th)]); P = p2[0] * fr["x_axis"] + p2[1] * fr["y_axis"]
        tng = -math.sin(th) * fr["x_axis"] + math.cos(th) * fr["y_axis"]; radial = math.cos(th) * fr["x_axis"] + math.sin(th) * fr["y_axis"]
        inv["tab_bar"]["cross_section_mid_longest_arc"] = dict(at_point=P, loops=section_2d(s, P, tng, radial))
    # terminal pad: planes whose normal is in the tab plane and square to the last chain direction
    lv = FACES["J1"] + U0
    inv["pads"] = [dict(joint="J1", note="upper pad of J1 (level F+3.15..F+6.15) + O20 ring to F+8.75 + O18 spigot to F+10.22, bore through",
                        planes_square_to_axis_within_pad=[p for p in J[0]["planes_square_to_axis"] if lv - 0.01 <= p["z"] <= lv + T_BAR + 0.01],
                        planform=planform(F, faces, k1, None, lv - 0.01, lv + T_BAR + 0.01))]
    end = np.asarray(chain[-1]["end"]); endp = end[0] * fr["x_axis"] + end[1] * fr["y_axis"]
    nrm = unit(endp)
    term = [dict(face=f["id"], offset_along_terminal_normal=float(f["point"] @ nrm), area=f["area_mm2"]) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ nrm) - 1) < 1e-6]
    inv["terminal_pad"] = dict(note="flat end of the tab, normal = radial from GH at the chain end; carries the 2x M4 counterbored holes to the scapula handler",
                               chain_end_point=endp, normal=nrm, distance_from_GH=float(np.linalg.norm(endp)), planes_square_to_normal=term,
                               planform=planform(F, faces, nrm, None, float(endp @ nrm) - 2, float(endp @ nrm) + 2, seat=None, rmax=60))
    inv["faces"] = F
    return inv


def arm_end_inventory():
    sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "band_cad")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
    _c = os.getcwd(); os.chdir(os.path.join(REPO, "pipeline", "conformal", "band_cad")); import arm_end as AE; os.chdir(_c)
    path = os.path.join(STEPD, "03_D6-04_BOTTOM_+_arm_end,_one_5-axis_part_.step")
    s, faces, F, G, inv = base_inventory(path, "D6-04", "7075-T6", BUILD["parts"][3]["name"])
    CB, uB, vB, axB = (np.asarray(x, float) for x in (AE.CB, AE.uB, AE.vB, AE.axB))
    sv = lambda p: float((np.asarray(p) - CB) @ uB)
    J = joint_axes(F, faces, s, G, {"J3": FACES["J3"]}); inv["joint_axes"] = J
    k3 = J[0]["axis_dir"]; F3 = FACES["J3"]
    vs, _ = s.tessellate(0.05, 0.2); Pv = np.array([[v.x, v.y, v.z] for v in vs]); S = (Pv - CB) @ uB
    # BOTTOM original in the arm rest frame (as AE.user_parts() does before the cut)
    from load_arm import load
    orig = [x for x in load() if x[0] == "BOTTOM"][0][2]; ob = AE.cad_to_rest(orig, "up")
    vo, _ = ob.tessellate(0.05, 0.2); Po = np.array([[v.x, v.y, v.z] for v in vo]); So = (Po - CB) @ uB
    # the cut face: plane with normal +-uB
    cutp = [dict(face=f["id"], s_from_elbow_hinge=sv(f["point"]), area=f["area_mm2"]) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ uB) - 1) < 1e-6]
    # which points of the part belong to the strap: beyond the cut, or outside BOTTOM's original solid
    fr = dict(CB_elbow_hinge_point=CB, uB_up_the_bar=uB, vB_across_the_bar=vB, axB_bar_normal_away_from_arm=axB,
              note="arm_end.py frame of the user's BOTTOM bar (arm rest frame = this STEP's frame): s = (p - CB).uB is the station up the bar from the elbow-hinge axis")
    bott = dict(frame=fr,
                eye_end_s=float(S.min()), cut_planes_square_to_uB=cutp,
                kept_bottom_bar_length_eye_end_to_cut=255.0 - float(S.min()) if cutp else None,
                measured_cut_s=[c["s_from_elbow_hinge"] for c in cutp],
                original_bottom_s_range=[float(So.min()), float(So.max())], original_bottom_length_along_uB=float(So.max() - So.min()),
                part_s_range=[float(S.min()), float(S.max())], overall_length_along_uB=float(S.max() - S.min()),
                overall_extent_v=[float(((Pv - CB) @ vB).min()), float(((Pv - CB) @ vB).max())], overall_extent_ax=[float(((Pv - CB) @ axB).min()), float(((Pv - CB) @ axB).max())])
    # cut s = the cut plane nearest 255 among planes facing +uB
    cut_s = min((c["s_from_elbow_hinge"] for c in cutp), key=lambda x: abs(x - 255.0)) if cutp else None
    bott["cut_s_from_elbow_hinge_axis"] = cut_s; bott["kept_bottom_bar_length_eye_end_to_cut"] = cut_s - float(S.min())
    bott["bar_sections"] = {f"s{st:g}": section_2d(s, CB + st * uB, uB, vB) for st in (60.0, 150.0, 200.0, 225.0, 245.0, 254.0)}
    bott["bar_sections_note"] = "sections square to the bar at station s (2D x = vB across the bar, y = axB away from the arm, origin = CB + s uB); s 225..254 cut through the fused tongue"
    bott["original_bar_sections"] = {f"s{st:g}": section_2d(ob, CB + st * uB, uB, vB) for st in (150.0, 200.0)}
    # face-by-face comparison with the user's original BOTTOM
    Fo = [face_record(i, f) for i, f in enumerate(ob.Faces())]
    def sig_match(a, b):
        if a["type"] != b["type"]: return False
        t = a["type"]
        if t == "plane": return abs(abs(a["normal"] @ b["normal"]) - 1) < 1e-6 and abs(a["normal"] @ (b["point"] - a["point"])) < 1e-3
        if t == "cylinder": return abs(a["radius"] - b["radius"]) < 1e-3 and abs(abs(a["axis_dir"] @ b["axis_dir"]) - 1) < 1e-6 and np.linalg.norm(np.cross(b["axis_point"] - a["axis_point"], a["axis_dir"])) < 1e-3
        if t == "cone": return abs(a["semi_angle_deg"] - b["semi_angle_deg"]) < 1e-3 and np.linalg.norm(a["apex"] - b["apex"]) < 1e-3
        if t == "torus": return abs(a["major_radius"] - b["major_radius"]) < 1e-3 and abs(a["minor_radius"] - b["minor_radius"]) < 1e-3 and np.linalg.norm(a["centre"] - b["centre"]) < 1e-3
        if t == "sphere": return abs(a["radius"] - b["radius"]) < 1e-3 and np.linalg.norm(a["centre"] - b["centre"]) < 1e-3
        return np.allclose(a["bbox"], b["bbox"], atol=1e-2) or np.linalg.norm(a["centroid"] - b["centroid"]) < 1e-2
    cmp = []; used = set()
    for a in Fo:
        ms = [b for b in F if sig_match(a, b)]
        smin, smax = sv(a["bbox"][:3]), sv(a["bbox"][3:])
        if not ms: st = "removed (beyond the cut)" if sv(a["centroid"]) > (cut_s or 255) - 1e-3 else "removed / replaced (merged with the strap)"
        else:
            same = [b for b in ms if abs(b["area_mm2"] - a["area_mm2"]) < 1e-3 * max(1, a["area_mm2"]) and np.linalg.norm(b["centroid"] - a["centroid"]) < 1e-3]
            ar = sum(b["area_mm2"] for b in ms)
            st = "unchanged" if same else ("trimmed by the cut" if ar < a["area_mm2"] - 1e-3 and max(sv(b["bbox"][3:]) for b in ms) >= (cut_s or 255) - 0.5 else
                                            ("trimmed / merged with the strap" if ar < a["area_mm2"] - 1e-3 else "kept surface, re-split (area within part)"))
            used |= {b["id"] for b in ms}
        rec = dict(orig_face=a["id"], type=a["type"], area_orig=a["area_mm2"], s_centroid=sv(a["centroid"]), status=st, d6_04_faces=[b["id"] for b in ms])
        for kk in ("radius", "minor_radius", "major_radius", "semi_angle_deg"):
            if kk in a: rec[kk] = a[kk]
        if a["type"] in ("cylinder", "cone"): rec["axis_dir"] = a["axis_dir"]
        if a["type"] == "plane": rec["normal"] = a["normal"]
        cmp.append(rec)
    new = [f["id"] for f in F if f["id"] not in used]
    Go = coaxial_groups(Fo); Ho = holes_of(ob, Fo, ob.Faces(), Go)
    bott["original_bottom"] = dict(volume_mm3=ob.Volume(), faces=len(Fo), face_types=dict(collections.Counter(f["type"] for f in Fo)), holes=Ho)
    bott["face_comparison_with_original"] = cmp
    bott["face_status_counts"] = dict(collections.Counter(c["status"] for c in cmp))
    bott["d6_04_faces_not_from_bottom_strap_and_pad"] = new
    # holes of D6-04 tagged by whether the original BOTTOM had them
    for h in inv["holes"]:
        h["s_from_elbow_hinge_of_entries"] = {k: sv(v) for k, v in h["entry_points"].items()}
        h["from_original_bottom"] = any(np.linalg.norm(np.cross(h["axis_point_nearest_GH"] - ho["axis_point_nearest_GH"], ho["axis_dir"])) < 1e-3 and abs(abs(ho["axis_dir"] @ h["axis_dir"]) - 1) < 1e-6
                                        and abs(ho["min_diameter"] - h["min_diameter"]) < 1e-3 for ho in Ho)
    inv["bottom"] = bott
    # ---- strap (the arm end): planform turns, bend, tongue
    up = axB; d = unit(np.cross(k3, up)); d = -d if d @ uB > 0 else d
    yA, yB = np.cross(k3, d), np.cross(up, d)
    OAm = (F3 + T_BAR / 2) * k3
    th_pl = math.degrees(math.acos(np.clip(yA @ yB, -1, 1)))
    def cyl_about(dirv, rmin=2.0, rmax=40.0):
        return [f for f in F if f["type"] == "cylinder" and abs(abs(f["axis_dir"] @ dirv) - 1) < 1e-6 and rmin < f["radius"] < rmax and np.linalg.norm(f["axis_foot_GH"]) > 0.05]
    tA = [dict(face=f["id"], radius=f["radius"], convex=f["convex"], span_deg=f["u_span_deg"], centre_in_pad_plane_2d=[float((f["axis_point"] - OAm) @ d), float((f["axis_point"] - OAm) @ yA)],
               level_along_k3=float(f["axis_point"] @ k3)) for f in cyl_about(k3)]
    tB = [dict(face=f["id"], radius=f["radius"], convex=f["convex"], span_deg=f["u_span_deg"], axis_point=f["axis_point"],
               s_from_elbow_hinge=sv(f["axis_point"]), across_bar_v=float((f["axis_point"] - CB) @ vB)) for f in cyl_about(up)]
    tD = [dict(face=f["id"], radius=f["radius"], convex=f["convex"], span_deg=f["u_span_deg"], axis_point=f["axis_point"], axis_dir=f["axis_dir"],
               distance_of_bend_axis_from_J3_axis=float(np.linalg.norm(np.cross(f["axis_point"], k3))),
               offset_behind_J3_in_pad_plane_yA=float((f["axis_point"] - OAm) @ yA), height_along_k3=float(f["axis_point"] @ k3)) for f in cyl_about(d, 1.0, 20.0)]
    # strap mid-planes: pad-plane faces (normal k3) and channel-plane faces (normal axB) of the strap
    plA = sorted({round(float(f["point"] @ k3), 4) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ k3) - 1) < 1e-6})
    plB = sorted({round(float((f["point"] - CB) @ up), 4) for f in F if f["type"] == "plane" and abs(abs(f["normal"] @ up) - 1) < 1e-6})
    # common line of the strap mid-planes (pad mid-plane k3.p = F3 + 1.5; channel-strap mid-plane = mean of its two faces nearest the bend)
    strap = dict(frame=dict(J3_axis_k3=k3, common_line_dir_d_down_the_arm=d, pad_plane_y_axis_yA=yA, channel_plane_y_axis_yB=yB, pad_mid_plane_origin_OAm=OAm,
                            note="pad-plane sketch: origin OAm on the J3 axis at the pad mid-plane (F3 + 1.5), x = d (down the arm), y = yA = k3 x d; channel-plane sketch: x = d, y = yB = axB x d"),
                 angle_between_pad_and_channel_planes_deg=th_pl, build_json_check=BUILD["arm end"],
                 pad_plane_planform_arcs_axis_parallel_k3=tA, channel_plane_planform_arcs_axis_parallel_axB=tB, bend_cylinders_axis_parallel_d=tD,
                 planes_normal_k3_levels=plA, planes_normal_axB_offsets_from_CB=plB)
    # centre lines of the turns and the bend from coaxial pairs (radius difference = strap width 8 for planform turns, 3 for the bend)
    def pairs(lst, key, dr):
        out = []
        for i, a in enumerate(lst):
            for b in lst[i + 1:]:
                if abs(abs(a["radius"] - b["radius"]) - dr) < 2e-3 and np.allclose(a[key], b[key], atol=2e-3):
                    out.append(dict(centre_line_radius=(a["radius"] + b["radius"]) / 2, faces=[a["face"], b["face"]], centre=a[key], face_radii=sorted([a["radius"], b["radius"]]),
                                    span_deg=max(a["span_deg"], b["span_deg"])))
        return out
    strap["turn_in_pad_plane"] = pairs(tA, "centre_in_pad_plane_2d", 8.0)
    for t_ in tB: t_["c2"] = [t_["s_from_elbow_hinge"], t_["across_bar_v"]]
    strap["turn_in_channel_plane"] = pairs(tB, "c2", 8.0)
    for t_ in tD: t_["c2"] = [t_["offset_behind_J3_in_pad_plane_yA"], t_["height_along_k3"]]
    strap["bend_about_common_line"] = pairs(tD, "c2", 3.0)
    # common line of the two mid-planes, measured: pad mid plane n=k3 (F3+1.5); channel strap mid-plane from the bend's outer/inner tangent
    if strap["bend_about_common_line"]:
        b = strap["bend_about_common_line"][0]; Rb = b["centre_line_radius"]
        f0 = [x for x in tD if x["face"] == b["faces"][0]][0]; C = np.asarray(f0["axis_point"])
        # mid-plane of the pad side is tangent to the centre-line circle: its offset from C along k3 is +-Rb
        strap["bend_axis_point"] = C; strap["bend_axis_distance_from_pad_mid_plane"] = float(abs(C @ k3 - (F3 + T_BAR / 2)))
        # the two mid-planes meet on the line through the bend's tangent construction: p0 = C + Rb/cos(th/2) * bisector
        n1 = k3 if (C @ k3 - (F3 + T_BAR / 2)) < 0 else -k3
        sign_up = 1.0 if ((C - CB) @ up) < (np.mean([x for x in plB if x > 0]) if any(x > 0 for x in plB) else 0) else -1.0
        strap["common_line_note"] = "the planes' common line is where the strap's pad mid-plane and channel mid-plane meet; the bend R is tangent to both, so the line lies Rb / cos(th/2) from the bend axis, on the bisector"
        bis = unit(-n1 * 0 + 0 * up)
    # tongue: where the strap leaves the channel-plane turn and runs down the arm; offset of its centre line from the channel centre (vB = 0)
    tong = []
    for f in F:
        if f["type"] == "plane" and abs(f["normal"] @ vB) > 1 - 1e-6 and abs(f["normal"] @ d) < 1e-3:
            pass
    strap["tongue_note"] = "tongue = the 8 mm strap in the channel plane after the R7.5 turn, running down the arm to a full-round end; it is fused into BOTTOM's web (embedded 1 mm) so its faces inside the channel are merged; see channel-plane turn centre and bar sections s225..s254"
    # J3 pad + pin
    lv = F3
    strap["J3_pad"] = dict(planes_square_to_axis_within_pad=[p for p in J[0]["planes_square_to_axis"] if lv - 0.01 <= p["z"] <= lv + T_BAR + 0.01],
                           planform=planform(F, faces, k3, None, lv - 0.01, lv + T_BAR + 0.01))
    inv["strap"] = strap
    inv["faces"] = F
    return inv


def cuff_inventory(path):
    sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "band_cad")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
    _c = os.getcwd(); os.chdir(os.path.join(REPO, "pipeline", "conformal", "band_cad")); import arm_end as AE; os.chdir(_c)
    s, faces, F, G, inv = base_inventory(path, "UPPER-ARM-CUFF", "AlSi10Mg", "UPPER ARM CUFF (lines and arcs: flat land + side arcs, extruded along BOTTOM)")
    CB, uB, vB, axB = (np.asarray(x, float) for x in (AE.CB, AE.uB, AE.vB, AE.axB))
    vs, _ = s.tessellate(0.05, 0.2); Pv = np.array([[v.x, v.y, v.z] for v in vs]); S = (Pv - CB) @ uB
    mid = (S.min() + S.max()) / 2
    inv["cuff"] = dict(frame=dict(CB=CB, uB=uB, vB=vB, axB=axB), s_range=[float(S.min()), float(S.max())], length_along_uB=float(S.max() - S.min()),
                       profile_section_mid=dict(note="section square to uB at mid-length; 2D x = vB across the bar, y = axB (away from the arm)", s=float(mid), loops=section_2d(s, CB + mid * uB, uB, vB)),
                       build_json_check=BUILD["upper cuff"])
    for h in inv["holes"]: h["s_from_elbow_hinge_of_entries"] = {k: float((np.asarray(v) - CB) @ uB) for k, v in h["entry_points"].items()}
    inv["faces"] = F
    return inv


def dump(inv, name):
    def conv(o):
        if isinstance(o, dict): return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)): return [conv(v) for v in o]
        if isinstance(o, np.ndarray): return [conv(v) for v in o.tolist()]
        if isinstance(o, (np.floating, float)): return round(float(o), 4)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, np.bool_): return bool(o)
        return o
    json.dump(conv(inv), open(os.path.join(OUTD, name), "w"), indent=1)
    print("wrote", name)


if __name__ == "__main__":
    want = sys.argv[1:] or ["D6-01", "D6-02", "D6-03", "D6-04", "cuff"]
    if "D6-02" in want: dump(link_inventory(os.path.join(STEPD, "00_D6-02_link_1.step"), "D6-02", "link 1", "J1", "J2", False), "D6-02_link_1.json")
    if "D6-03" in want: dump(link_inventory(os.path.join(STEPD, "01_D6-03_link_2.step"), "D6-03", "link 2", "J2", "J3", True), "D6-03_link_2.json")
    if "D6-01" in want: dump(base_part_inventory(), "D6-01_scapula_base.json")
    if "D6-04" in want: dump(arm_end_inventory(), "D6-04_BOTTOM_arm_end.json")
    if "cuff" in want:
        c = [f for f in (os.listdir(DRAW_STEP) if os.path.isdir(DRAW_STEP) else []) if "cuff" in f.lower() and f.lower().endswith((".step", ".stp"))]
        if c: dump(cuff_inventory(os.path.join(DRAW_STEP, c[0])), "upper_arm_cuff.json")
        else: print("no cuff STEP in", DRAW_STEP)
