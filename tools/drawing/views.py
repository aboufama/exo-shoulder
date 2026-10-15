"""Exact hidden-line-removed views of a B-rep (OCP HLRBRep_Algo + HLRBRep_HLRToShape), sections and detail crops.

A View maps model space to sheet millimetres: the model axes `mx`, `my` (orthonormal, the view looks along -(mx x my),
i.e. mx x my points at the viewer) are drawn along the sheet directions at `rot` degrees, scaled by `scale`, with the
model point `anchor` placed at sheet point `at`. Third-angle helpers build the top / right / auxiliary views of a
front view so that projection lines align.

Output primitives (sheet mm, exact): ("line", p0, p1) ("circle", c, r) ("arc", c, r, a0, a1) [deg, ccw]
("ellipse", c, major_vec, ratio, t0, t1) [ccw params] ("spline", degree, ctrl, knots, weights) ("poly", pts).
Each primitive carries a layer: VISIBLE, HIDDEN, TANGENT (smooth edges: the boundaries of rounds).
"""
import math
import numpy as np
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pln
from OCP.BRepLib import BRepLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_BSplineCurve, GeomAbs_BezierCurve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

from brep import unit


class View:
    def __init__(self, name, mx, my, scale, at, anchor=(0, 0, 0), rot=0.0, label=None):
        self.name, self.scale, self.rot = name, float(scale), float(rot)
        self.mx, self.my = unit(mx), unit(my); assert abs(self.mx @ self.my) < 1e-9
        self.mz = np.cross(self.mx, self.my)                                                # toward the viewer
        self.at, self.anchor = np.asarray(at, float), np.asarray(anchor, float)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot)); self.U, self.V = np.array([c, s]), np.array([-s, c])
        self.label = label

    def to_sheet(self, p):
        """model point(s) -> sheet mm"""
        p = np.asarray(p, float) - self.anchor
        u, v = p @ self.mx, p @ self.my
        return self.at + self.scale * (np.multiply.outer(u, self.U) + np.multiply.outer(v, self.V))

    def dir_sheet(self, d):
        """model direction -> sheet unit direction (the projected direction; None if along the view)"""
        d = np.asarray(d, float); q = (d @ self.mx) * self.U + (d @ self.my) * self.V; n = np.linalg.norm(q)
        return q / n if n > 1e-9 else None

    def from_local(self, xy):
        """projector-plane coordinates (x along mx, y along my, model mm, origin at the model origin) -> sheet"""
        xy = np.asarray(xy, float); a = self.anchor @ self.mx, self.anchor @ self.my
        return self.at + self.scale * (np.multiply.outer(xy[..., 0] - a[0], self.U) + np.multiply.outer(xy[..., 1] - a[1], self.V))

    # third-angle neighbours: the projection lines stay aligned with this view
    def top(self, gap, name="TOP"):
        """view from above (the +my side), placed gap mm above"""
        return View(name, self.mx, -self.mz, self.scale, self.at + gap * self.V, self.anchor, self.rot)

    def right(self, gap, name="RIGHT"):
        return View(name, -self.mz, self.my, self.scale, self.at + gap * self.U, self.anchor, self.rot)

    def aux(self, d_model, gap, name="AUX"):
        """auxiliary view looking back along the in-view direction d_model (the viewer stands on +d), placed gap mm
        along d's sheet direction; its projection lines stay parallel to d on the sheet"""
        d = unit(np.asarray(d_model, float) - (np.asarray(d_model, float) @ self.mz) * self.mz)
        ds = self.dir_sheet(d); ang = math.degrees(math.atan2(ds[1], ds[0]))
        # sheet U of the new view = d's sheet direction; the model axis drawn along it is the depth (-mz: away from the
        # parent's viewer); V = the in-plane perpendicular kept as in the parent
        my = np.cross(d, -self.mz)                                                           # mx x my must be +d
        return View(name, -self.mz, -my if np.cross(-self.mz, -my) @ d > 0 else my, self.scale,
                    self.at + gap * ds, self.anchor, ang)


# ---------------------------------------------------------------- HLR
def _projector(view):
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*map(float, view.mz)), gp_Dir(*map(float, view.mx)))
    return HLRAlgo_Projector(ax)


def _edges(shape):
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    while ex.More():
        yield TopoDS.Edge_s(ex.Current()); ex.Next()


def hlr(shape, view, hidden=True, tangent=True, outline=True):
    """exact HLR of a cq.Shape/TopoDS_Shape in the view -> [(layer, prim)] in sheet mm"""
    sh = shape.wrapped if hasattr(shape, "wrapped") else shape
    algo = HLRBRep_Algo(); algo.Add(sh); algo.Projector(_projector(view)); algo.Update(); algo.Hide()
    h = HLRBRep_HLRToShape(algo)
    sets = [("VISIBLE", h.VCompound())]
    if outline: sets.append(("VISIBLE", h.OutLineVCompound()))
    if tangent: sets.append(("TANGENT", h.Rg1LineVCompound()))
    if hidden:
        sets.append(("HIDDEN", h.HCompound()))
        if outline: sets.append(("HIDDEN", h.OutLineHCompound()))
    out = []
    for layer, comp in sets:
        if comp is None or comp.IsNull(): continue
        BRepLib.BuildCurves3d_s(comp)
        for e in _edges(comp):
            pr = edge_prim(e, view)
            if pr is not None: out.append((layer, pr))
    return out


def edge_prim(e, view, plane_xy=True):
    """one projected edge (z = 0 in the projector frame) -> a sheet primitive, exact where the curve is analytic"""
    try: c = BRepAdaptor_Curve(e)
    except Exception: return None
    t0, t1 = c.FirstParameter(), c.LastParameter()
    if abs(t1 - t0) < 1e-12: return None
    T = c.GetType()
    xy = lambda p: view.from_local(np.array([p.X(), p.Y()]))
    sc = view.scale
    if T == GeomAbs_Line:
        a, b = xy(c.Value(t0)), xy(c.Value(t1))
        return ("line", a, b) if np.linalg.norm(b - a) > 1e-6 else None
    if T == GeomAbs_Circle:
        ci = c.Circle(); ctr = xy(ci.Location()); r = ci.Radius() * sc; zsign = ci.Axis().Direction().Z()
        if t1 - t0 >= 2 * math.pi - 1e-9: return ("circle", ctr, r)
        p0, p1 = xy(c.Value(t0)), xy(c.Value(t1))
        a0 = math.degrees(math.atan2(*(p0 - ctr)[::-1])); a1 = math.degrees(math.atan2(*(p1 - ctr)[::-1]))
        if zsign < 0: a0, a1 = a1, a0                                                   # clockwise in the projector -> swap
        return ("arc", ctr, r, a0 % 360, a1 % 360)
    if T == GeomAbs_Ellipse:
        el = c.Ellipse(); ctr = xy(el.Location()); a, b = el.MajorRadius(), el.MinorRadius()
        X = el.XAxis().Direction(); Xs = view.from_local(np.array([el.Location().X() + X.X(), el.Location().Y() + X.Y()])) - ctr
        maj = unit(Xs) * a * sc; ratio = b / a; zsign = el.Axis().Direction().Z()
        if abs(ratio - 1) < 1e-7:                                                       # a circle seen face-on: keep it a circle
            if t1 - t0 >= 2 * math.pi - 1e-9: return ("circle", ctr, a * sc)
            p0, p1 = xy(c.Value(t0)), xy(c.Value(t1))
            a0 = math.degrees(math.atan2(*(p0 - ctr)[::-1])); a1 = math.degrees(math.atan2(*(p1 - ctr)[::-1]))
            if zsign < 0: a0, a1 = a1, a0
            return ("arc", ctr, a * sc, a0 % 360, a1 % 360)
        if t1 - t0 >= 2 * math.pi - 1e-9: return ("ellipse", ctr, maj, ratio, 0.0, 2 * math.pi)
        if zsign < 0: t0, t1 = -t1, -t0
        return ("ellipse", ctr, maj, ratio, t0 % (2 * math.pi), t1 % (2 * math.pi))
    if T in (GeomAbs_BSplineCurve, GeomAbs_BezierCurve):
        if T == GeomAbs_BSplineCurve:
            bs = c.BSpline()
        else:
            from OCP.GeomConvert import GeomConvert
            bs = GeomConvert.CurveToBSplineCurve_s(c.Bezier())
        bs = bs.Copy(); from OCP.Geom import Geom_BSplineCurve
        bs = Geom_BSplineCurve.DownCast(bs) if not isinstance(bs, Geom_BSplineCurve) else bs
        if t0 > bs.FirstParameter() + 1e-9 or t1 < bs.LastParameter() - 1e-9:
            try: bs.Segment(t0, t1)
            except Exception: pass
        n = bs.NbPoles(); ctrl = np.array([xy(bs.Pole(i)) for i in range(1, n + 1)])
        wts = [bs.Weight(i) for i in range(1, n + 1)]
        knots = []
        for i in range(1, bs.NbKnots() + 1): knots += [bs.Knot(i)] * bs.Multiplicity(i)
        if bs.IsPeriodic():                                                             # periodic -> sample
            return ("poly", sample_edge(e, view))
        return ("spline", bs.Degree(), ctrl, knots, wts if bs.IsRational() else None)
    return ("poly", sample_edge(e, view))


def sample_edge(e, view, defl=0.002):
    c = BRepAdaptor_Curve(e); g = GCPnts_QuasiUniformDeflection(c, defl)
    return np.array([view.from_local(np.array([g.Value(i).X(), g.Value(i).Y()])) for i in range(1, g.NbPoints() + 1)])


# ---------------------------------------------------------------- sections
def half_space_cut(shape, p0, n, size=2000.0):
    """remove the part of the shape on the +n side of the plane (p0, n): the side toward the section viewer"""
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace
    pl = gp_Pln(gp_Pnt(*map(float, p0)), gp_Dir(*map(float, n)))
    face = BRepBuilderAPI_MakeFace(pl, -size, size, -size, size).Face()
    ref = np.asarray(p0, float) + 10.0 * unit(n)
    hs = BRepPrimAPI_MakeHalfSpace(face, gp_Pnt(*map(float, ref))).Solid()
    cut = BRepAlgoAPI_Cut(shape.wrapped if hasattr(shape, "wrapped") else shape, hs); cut.Build()
    return cq.Shape.cast(cut.Shape())


def section_faces(shape, p0, n, size=2000.0):
    """the planar faces where the plane (p0, n) cuts the solid"""
    pl = gp_Pln(gp_Pnt(*map(float, p0)), gp_Dir(*map(float, n)))
    face = BRepBuilderAPI_MakeFace(pl, -size, size, -size, size).Face()
    com = BRepAlgoAPI_Common(shape.wrapped if hasattr(shape, "wrapped") else shape, face); com.Build()
    res = com.Shape(); out = []
    ex = TopExp_Explorer(res, TopAbs_FACE)
    while ex.More(): out.append(TopoDS.Face_s(ex.Current())); ex.Next()
    return out


def face_loops(face, view, defl=0.002):
    """boundary loops of a planar face as sheet polylines with bulges [(x, y, bulge)] (arcs exact as bulges, splines
    sampled) - the form a DXF HATCH polyline path takes"""
    loops = []
    wex = TopExp_Explorer(face, TopAbs_WIRE)
    while wex.More():
        w = TopoDS.Wire_s(wex.Current()); we = BRepTools_WireExplorer(w, face); pts = []
        while we.More():
            e = we.Current(); rev = e.Orientation() == 1                               # TopAbs_REVERSED
            c = BRepAdaptor_Curve(e); t0, t1 = c.FirstParameter(), c.LastParameter()
            if rev: t0, t1 = t1, t0
            T = c.GetType(); p3 = lambda t: np.array(c.Value(t).Coord())
            if T == GeomAbs_Line:
                pts.append((*view.to_sheet(p3(t0)), 0.0))
            elif T == GeomAbs_Circle:
                a, m, b = view.to_sheet(p3(t0)), view.to_sheet(p3((t0 + t1) / 2)), view.to_sheet(p3(t1))
                sweep = abs(t1 - t0)
                if sweep > math.pi * 1.999:                                             # full circle: two halves
                    tm = (t0 + t1) / 2; mm = view.to_sheet(p3((t0 + tm) / 2))
                    cr = np.cross(m - a, mm - a) if False else (mm - a)[0] * (m - a)[1] - (mm - a)[1] * (m - a)[0]
                    pts.append((*a, -1.0 if cr > 0 else 1.0)); pts.append((*m, -1.0 if cr > 0 else 1.0))
                else:
                    cr = (m - a)[0] * (b - a)[1] - (m - a)[1] * (b - a)[0]
                    bul = math.tan(sweep / 4) * (-1 if cr > 0 else 1)
                    pts.append((*a, bul))
            else:
                g = GCPnts_QuasiUniformDeflection(c, defl); q = [view.to_sheet(np.array(g.Value(i).Coord())) for i in range(1, g.NbPoints() + 1)]
                if rev: q = q[::-1]
                for x in q[:-1]: pts.append((*x, 0.0))
            we.Next()
        loops.append(pts); wex.Next()
    return loops


# ---------------------------------------------------------------- detail crop
def clip_circle(prims, c, r, n_poly=720):
    """crop sheet primitives to the circle (c, r): lines and arcs/circles exactly, the rest as polylines"""
    c = np.asarray(c, float); out = []
    inside = lambda p: np.linalg.norm(np.asarray(p) - c) <= r + 1e-9
    for layer, pr in prims:
        k = pr[0]
        if k == "line":
            a, b = pr[1], pr[2]; d = b - a; f = a - c
            A, B, C = d @ d, 2 * f @ d, f @ f - r * r; disc = B * B - 4 * A * C
            if disc <= 0: continue
            s = math.sqrt(disc); t0, t1 = max(0.0, (-B - s) / (2 * A)), min(1.0, (-B + s) / (2 * A))
            if t1 > t0 + 1e-9: out.append((layer, ("line", a + t0 * d, a + t1 * d)))
        elif k in ("circle", "arc"):
            cc, rr = pr[1], pr[2]; a0, a1 = (0.0, 360.0) if k == "circle" else (pr[3], pr[4])
            if a1 <= a0: a1 += 360.0
            L = np.linalg.norm(cc - c)
            if L + rr <= r: out.append((layer, pr)); continue
            if L >= r + rr or L + r <= rr: continue
            # intersections of the two circles -> angles on (cc, rr)
            x = (L * L + rr * rr - r * r) / (2 * L); base = math.degrees(math.atan2(*(c - cc)[::-1])); h = math.degrees(math.acos(np.clip(x / rr, -1, 1)))
            i0, i1 = base - h, base + h                                                   # the in-circle span is [i0, i1]
            for off in (-360.0, 0.0, 360.0):
                s0, s1 = max(a0, i0 + off), min(a1, i1 + off)
                if s1 > s0 + 1e-6: out.append((layer, ("arc", cc, rr, s0 % 360, s1 % 360)))
        else:
            pts = prim_points(pr)
            run = []
            for p in pts:
                if inside(p): run.append(p)
                else:
                    if len(run) > 1: out.append((layer, ("poly", np.array(run))))
                    run = []
            if len(run) > 1: out.append((layer, ("poly", np.array(run))))
    return out


def prim_points(pr, n=200):
    k = pr[0]
    if k == "poly": return pr[1]
    if k == "line": return np.array([pr[1], pr[2]])
    if k in ("circle", "arc"):
        a0, a1 = (0.0, 360.0) if k == "circle" else (pr[3], pr[4] if pr[4] > pr[3] else pr[4] + 360)
        t = np.radians(np.linspace(a0, a1, n)); return pr[1] + pr[2] * np.stack([np.cos(t), np.sin(t)], 1)
    if k == "ellipse":
        c, M, ratio, t0, t1 = pr[1:]; t1 = t1 if t1 > t0 else t1 + 2 * math.pi; t = np.linspace(t0, t1, n)
        m = np.array([-M[1], M[0]]) * ratio; return c + np.outer(np.cos(t), M) + np.outer(np.sin(t), m)
    if k == "spline":
        from scipy.interpolate import BSpline
        deg, ctrl, knots, w = pr[1:]; ctrl = np.asarray(ctrl); kn = np.asarray(knots, float)
        t = np.linspace(kn[deg], kn[-deg - 1], n)
        if w is None: return BSpline(kn, ctrl, deg)(t)
        w = np.asarray(w); num = BSpline(kn, ctrl * w[:, None], deg)(t); den = BSpline(kn, w, deg)(t); return num / den[:, None]
    raise KeyError(k)


def prims_bbox(prims):
    pts = np.concatenate([prim_points(pr, 60) for _, pr in prims]); return pts.min(0), pts.max(0)
