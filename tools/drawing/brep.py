"""B-rep access for drawings: load a STEP solid, list its analytic features, and measure them.

Every number a drawing prints comes from here. A measurement is a *spec* (a small JSON-able dict: what to measure and
which faces/edges, found again by probe points ON them) plus its value; `evaluate(part, spec)` re-runs the spec on a
freshly loaded solid, so the validator (validate.py) can re-measure every dimension independently of the sheet code.

Feature probes: a face is selected by a point on it (the face nearest the probe, within `tol`) and its surface type,
so a spec stays valid as long as the solid is the same and fails loudly when the STEP changes under the drawing.
"""
import math
import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.GeomAbs import (GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Torus, GeomAbs_Cone, GeomAbs_Sphere,
                         GeomAbs_Circle, GeomAbs_Line)
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

DENSITY = {"Ti-6Al-4V": 4.43, "7075-T6": 2.81, "AlSi10Mg": 2.67, "17-4PH": 7.80, "bearing steel": 7.80}   # g/cm3


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)


def P(p): return np.array([p.X(), p.Y(), p.Z()])


class Part:
    """one STEP solid + its analytic faces (planes, cylinders, tori, cones)"""

    def __init__(self, path):
        self.path = path
        sh = cq.importers.importStep(path)
        sols = sh.solids().vals()
        if len(sols) != 1: raise ValueError(f"{path}: {len(sols)} solids (a drawing needs exactly one)")
        self.shape = sols[0]
        if not self.shape.isValid(): raise ValueError(f"{path}: invalid solid")
        self.faces = [self._face(i, f) for i, f in enumerate(self.shape.Faces())]

    # ------------------------------------------------------------ features
    def _face(self, i, f):
        a = BRepAdaptor_Surface(f.wrapped); t = a.GetType(); d = dict(i=i, face=f, area=f.Area(), centre=np.array(f.Center().toTuple()))
        if t == GeomAbs_Plane:
            pl = a.Plane(); n = P(pl.Axis().Direction()); p = P(pl.Location())
            d.update(kind="plane", normal=n, d=float(p @ n))
        elif t == GeomAbs_Cylinder:
            c = a.Cylinder(); ax = c.Axis(); p = P(ax.Location()); k = P(ax.Direction())
            d.update(kind="cyl", axis=k, point=p - (p @ k) * k, r=c.Radius())
        elif t == GeomAbs_Torus:
            to = a.Torus(); ax = to.Axis(); p = P(ax.Location()); k = P(ax.Direction())
            d.update(kind="torus", axis=k, point=p, R=to.MajorRadius(), r=to.MinorRadius())
        elif t == GeomAbs_Cone:
            c = a.Cone(); ax = c.Axis(); d.update(kind="cone", axis=P(ax.Direction()), point=P(ax.Location()),
                                                 r=c.RefRadius(), half_angle=math.degrees(c.SemiAngle()))
        elif t == GeomAbs_Sphere:
            s = a.Sphere(); d.update(kind="sphere", point=P(s.Location()), r=s.Radius())
        else:
            d.update(kind="other")
        return d

    def where(self, kind=None, **crit):
        """faces of a kind matching criteria: r=(value, tol), axis=vector (parallel, either sense), normal=vector,
        d=(value, tol) for planes, near=(point, max distance from the face)"""
        out = []
        for f in self.faces:
            if kind and f["kind"] != kind: continue
            ok = True
            for k, v in crit.items():
                if k in ("r", "R", "d"):
                    val, tol = v if isinstance(v, (tuple, list)) else (v, 1e-3)
                    ok &= k in f and abs(f[k] - val) <= tol
                elif k in ("axis", "normal"):
                    ok &= k in f and abs(abs(unit(v) @ f[k]) - 1) < 1e-6
                elif k == "near":
                    p, tol = v; ok &= self.dist_to_face(f, p) <= tol
            if ok: out.append(f)
        return out

    def dist_to_face(self, f, p):
        v = BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float, p))).Vertex()
        ext = BRepExtrema_DistShapeShape(v, f["face"].wrapped); ext.Perform()
        return ext.Value() if ext.IsDone() else 1e9

    def probe(self, p, kind=None, tol=0.05):
        """the face nearest point p (must be within tol, of the given kind)"""
        best = None
        for f in self.faces:
            if kind and f["kind"] != kind: continue
            if np.linalg.norm(f["centre"] - p) > 400: continue
            d = self.dist_to_face(f, p)
            if best is None or d < best[0]: best = (d, f)
        if best is None or best[0] > tol:
            raise LookupError(f"probe {np.round(p, 3).tolist()} ({kind}): no face within {tol} mm (nearest {best and round(best[0], 4)})")
        return best[1]

    def point_on(self, f):
        """a point on the face (projection of the face centre onto it), the probe a spec records"""
        from OCP.BRepExtrema import BRepExtrema_DistShapeShape
        v = BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float, f["centre"]))).Vertex()
        ext = BRepExtrema_DistShapeShape(v, f["face"].wrapped); ext.Perform()
        return P(ext.PointOnShape2(1))

    # ------------------------------------------------------------ mass properties
    def volume(self):
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(self.shape.wrapped, g); return g.Mass()

    def mass_g(self, material):
        return self.volume() / 1000.0 * DENSITY[material]

    def bbox(self):
        b = self.shape.BoundingBox(); return np.array([b.xmin, b.ymin, b.zmin]), np.array([b.xmax, b.ymax, b.zmax])


# ---------------------------------------------------------------- reference geometry from specs
def ref(part, spec):
    """resolve a reference spec to geometry. Kinds:
    {"axis": probe}            -> (point, dir) of the cylinder/torus/cone face at probe
    {"plane": probe}           -> (point, normal) of the planar face at probe
    {"cyl": probe}             -> the cylinder face dict
    {"mid": [ref, ref]}        -> the midpoint of two point refs
    {"origin": [axis, axis]}   -> the point of closest approach of two axis refs
    {"point": [x, y, z]}       -> a fixed point (only for view-placement helpers, never a measured value)
    """
    if "axis" in spec:
        f = part.probe(np.array(spec["axis"]), tol=spec.get("tol", 0.05))
        if "axis" not in f: raise LookupError(f"probe {spec['axis']}: face has no axis ({f['kind']})")
        return f["point"], f["axis"]
    if "plane" in spec:
        f = part.probe(np.array(spec["plane"]), "plane", tol=spec.get("tol", 0.05))
        return f["normal"] * f["d"], f["normal"]
    if "origin" in spec:
        (p1, d1), (p2, d2) = ref(part, spec["origin"][0]), ref(part, spec["origin"][1])
        return closest_points(p1, d1, p2, d2)[2]
    if "point" in spec: return np.array(spec["point"], float)
    raise KeyError(spec)


def closest_points(p1, d1, p2, d2):
    """closest points of two lines and their midpoint"""
    d1, d2 = unit(d1), unit(d2); w = p1 - p2; a, b, c, d, e = d1 @ d1, d1 @ d2, d2 @ d2, d1 @ w, d2 @ w
    den = a * c - b * b
    if abs(den) < 1e-12: s, t = 0.0, e / c
    else: s, t = (b * e - c * d) / den, (a * e - b * d) / den
    q1, q2 = p1 + s * d1, p2 + t * d2; return q1, q2, (q1 + q2) / 2


def probe_of(part, f):
    return [round(float(x), 6) for x in part.point_on(f)]


# ---------------------------------------------------------------- measurements (spec -> value)
def evaluate(part, m):
    """value of a measurement spec on the part. Kinds:
    radius / diameter          {"cyl": probe} or {"torus_minor": probe}
    mid_radius                 {"cyls": [probe_in, probe_out]}: the mean radius of two coaxial cylinders (a bar's path)
    plane_plane                {"planes": [p, p]}: distance between two parallel planar faces
    point_plane                {"point": pointref, "plane": probe}: distance of a point ref to a planar face
    axis_plane_point           {"origin": [axref, axref], "plane": probe}: distance from the axes' meeting point to a plane
    axis_axis_angle            {"axes": [probe, probe], "signs": [1, -1]}: angle between two axes (deg)
    coord                      {"point": pointref, "dir": [x, y, z], "origin": pointref}: (p - o) . dir
    centre_coord               {"cyl": probe, "dir": [...], "origin": pointref}: the axis' trace in the plane through o normal to (dir x ...) - see code
    distance                   {"points": [pointref, pointref], "dir": [...]|None}
    """
    k = m["kind"]
    if k in ("radius", "diameter"):
        f = part.probe(np.array(m["cyl"]), tol=m.get("tol", 0.05))
        r = f["r"] if f["kind"] in ("cyl", "torus", "sphere", "cone") else None
        if r is None: raise LookupError(f"{m}: not a round face")
        return r if k == "radius" else 2 * r
    if k == "torus_minor":
        f = part.probe(np.array(m["torus"]), "torus"); return f["r"]
    if k == "mid_radius":
        f1, f2 = (part.probe(np.array(p), "cyl") for p in m["cyls"])
        assert abs(abs(f1["axis"] @ f2["axis"]) - 1) < 1e-6 and np.linalg.norm(f1["point"] - f2["point"]) < 1e-4, "not coaxial"
        return (f1["r"] + f2["r"]) / 2
    if k == "radial_gap":
        f1, f2 = (part.probe(np.array(p), "cyl") for p in m["cyls"]); return abs(f1["r"] - f2["r"])
    if k == "plane_plane":
        f1, f2 = (part.probe(np.array(p), "plane") for p in m["planes"])
        assert abs(abs(f1["normal"] @ f2["normal"]) - 1) < 1e-6, "planes not parallel"
        return abs(f1["d"] - f2["d"] * (f1["normal"] @ f2["normal"]))
    if k == "point_plane":
        p = ref(part, m["point"]); f = part.probe(np.array(m["plane"]), "plane"); return abs(p @ f["normal"] - f["d"])
    if k == "axis_axis_angle":
        (_, d1), (_, d2) = ref(part, {"axis": m["axes"][0]}), ref(part, {"axis": m["axes"][1]})
        s = m.get("signs", [1, 1]); d1, d2 = s[0] * d1, s[1] * d2
        if m.get("acute", True) and d1 @ d2 < 0: d2 = -d2
        return math.degrees(math.acos(np.clip(d1 @ d2, -1, 1)))
    if k == "coord":
        p = ref(part, m["point"]); o = ref(part, m["origin"]) if "origin" in m else np.zeros(3)
        return float((p - o) @ unit(m["dir"]))
    if k == "distance":
        a, b = ref(part, m["points"][0]), ref(part, m["points"][1])
        return float(abs((b - a) @ unit(m["dir"]))) if m.get("dir") is not None else float(np.linalg.norm(b - a))
    if k == "axis_point_coord":
        # trace of a cylinder axis in a plane (o, n): the axis point in that plane, then its coordinate along dir
        p, d = ref(part, {"axis": m["axis"]}); o = ref(part, m["origin"]); n = unit(m["plane_n"])
        t = ((o - p) @ n) / (d @ n) if abs(d @ n) > 1e-9 else 0.0
        q = p + t * d if abs(d @ n) > 1e-9 else p - ((p - o) @ n) * n
        return float((q - o) @ unit(m["dir"]))
    if k == "path_point_coord":
        # a tangent point of a bar path: on the line of the two arc centres (circles of mid radii), coordinate along dir
        q = path_tangent_point(part, m["arcs"][0], m["arcs"][1]); o = ref(part, m["origin"]); return float((q - o) @ unit(m["dir"]))
    if k == "arc_sweep":
        a = path_arc(part, m["arc"]); q0 = path_point(part, m["p0"]); q1 = path_point(part, m["p1"])
        u, v = unit(q0 - a["c"]), unit(q1 - a["c"]); return math.degrees(math.acos(np.clip(u @ v, -1, 1)))
    if k == "arc_length":
        a = path_arc(part, m["arc"]); q0 = path_point(part, m["p0"]); q1 = path_point(part, m["p1"])
        u, v = unit(q0 - a["c"]), unit(q1 - a["c"]); return a["R"] * math.acos(np.clip(u @ v, -1, 1))
    if k == "value":                       # a constant written in the spec (only for notes; the validator flags these)
        return float(m["value"])
    raise KeyError(k)


def path_arc(part, cyls):
    """an arc of a bar path: the two coaxial cylinders (inner/outer bar faces) -> centre (axis trace in z of the
    probes' plane), axis, mid radius"""
    f1, f2 = (part.probe(np.array(p), "cyl") for p in cyls)
    k = f1["axis"]; c = f1["point"]
    pm = (np.array(cyls[0]) + np.array(cyls[1])) / 2; c = c + ((pm - c) @ k) * k                     # into the probes' plane
    return dict(c=c, k=k, R=(f1["r"] + f2["r"]) / 2)


def path_tangent_point(part, cyls_a, cyls_b):
    a, b = path_arc(part, cyls_a), path_arc(part, cyls_b); L = np.linalg.norm(b["c"] - a["c"]); d = (b["c"] - a["c"]) / L
    # tangent circles touch on their centre line: externally (S bend, L = Ra + Rb) at a + Ra d; internally
    # (same-hand bend, L = |Ra - Rb|) at a + Ra d when a is the larger circle, else a - Ra d
    ext, inn = abs(L - (a["R"] + b["R"])), abs(L - abs(a["R"] - b["R"]))
    if min(ext, inn) > 1e-3: raise ValueError(f"arcs not tangent (centre distance {L:.4f}, radii {a['R']:.3f} {b['R']:.3f})")
    if ext < inn or a["R"] > b["R"]: return a["c"] + a["R"] * d
    return a["c"] - a["R"] * d


def path_point(part, spec):
    """a path point: {"tangent": [arc, arc]} or {"end": arc, "plane": probe} (where the arc's mid circle meets the
    mid-plane between a pad's two faces given as planes [p, p]) or {"ref": pointref}"""
    if "tangent" in spec: return path_tangent_point(part, *spec["tangent"])
    if "ref" in spec: return ref(part, spec["ref"])
    if "end" in spec:
        a = path_arc(part, spec["end"]); f1, f2 = (part.probe(np.array(p), "plane") for p in spec["mid_of"])
        n = f1["normal"]; dm = (f1["d"] + f2["d"] * (f1["normal"] @ f2["normal"])) / 2
        # circle (c, R) in the plane normal to k  ∩  plane n.x = dm  -> two points; take the one nearer the hint
        k = a["k"]; u = unit(n - (n @ k) * k); h = (dm - a["c"] @ n) / (u @ n)
        if abs(h) > a["R"]: raise ValueError("path end: plane misses the arc")
        v = np.cross(k, u); s = math.sqrt(a["R"] ** 2 - h ** 2); hint = np.array(spec["hint"])
        cand = [a["c"] + h * u + s * v, a["c"] + h * u - s * v]
        return min(cand, key=lambda q: np.linalg.norm(q - hint))
    raise KeyError(spec)
