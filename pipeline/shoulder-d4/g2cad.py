"""Curvature-continuous (G2) B-rep helpers for the D4 shoulder (OCP / CadQuery).

  g2_blend(...)       quintic Bezier between two curve ends matching point, tangent and curvature (G2 both ends)
  spherical_link(...) a link on a spherical shell: C2 planform outline (cubic smooth-min SDF of hub discs + strips,
                      smoothed periodic spline), radial side walls, G2 edge rounds swept along the outline with the
                      profile held radial (auxiliary-spine pipe), exact spherical inner / outer faces, sewn to a solid
  revolve_profile(...) solid of revolution from a list of 2D (rho, z) segments: lines, arcs about the origin, G2 blends
"""
import math
import numpy as np
from scipy.interpolate import splprep, splev
from skimage import measure
import cadquery as cq
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax1, gp_Ax2, gp_Ax3, gp_Vec
from OCP.TColgp import TColgp_HArray1OfPnt, TColgp_Array1OfPnt
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.Geom import Geom_BezierCurve, Geom_SphericalSurface
from OCP.GC import GC_MakeArcOfCircle, GC_MakeSegment
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace,
                                BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid)
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.ShapeFix import ShapeFix_Face, ShapeFix_Solid, ShapeFix_Shape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL, TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.BRep import BRep_Tool
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import fea_link as FL


def P(v): return gp_Pnt(float(v[0]), float(v[1]), float(v[2]))
def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


# ------------------------------------------------------------------ G2 blend
def g2_blend(P0, T0, k0, N0, P1, T1, k1, N1, frac=0.3):
    """quintic Bezier control points from P0 (leaving along T0, curvature k0 toward N0) to P1 (arriving along T1,
    curvature k1 toward N1). Curvature at a Bezier end = (n-1)/n |d1 x d2| / |d1|^3 -> offsets c = 5 k a^2 / 4."""
    P0, T0, N0, P1, T1, N1 = (np.asarray(x, float) for x in (P0, T0, N0, P1, T1, N1))
    L = np.linalg.norm(P1 - P0); a = b = frac * L
    c0 = 5 * k0 * a * a / 4; c1 = 5 * k1 * a * a / 4
    Q1 = P0 + a * T0; Q2 = Q1 + b * T0 + c0 * N0
    Q4 = P1 - a * T1; Q3 = Q4 - b * T1 + c1 * N1
    return [P0, Q1, Q2, Q3, Q4, P1]


def bezier_edge(pts):
    arr = TColgp_Array1OfPnt(1, len(pts))
    for i, p in enumerate(pts): arr.SetValue(i + 1, P(p))
    return BRepBuilderAPI_MakeEdge(Geom_BezierCurve(arr)).Edge()


def line_edge(a, b): return BRepBuilderAPI_MakeEdge(P(a), P(b)).Edge()


def wire(edges):
    w = BRepBuilderAPI_MakeWire()
    for e in edges: w.Add(e)
    return w.Wire()


def interp_closed(pts, tol=1e-6):
    arr = TColgp_HArray1OfPnt(1, len(pts))
    for i, p in enumerate(pts): arr.SetValue(i + 1, P(p))
    it = GeomAPI_Interpolate(arr, True, tol); it.Perform(); return it.Curve()


# ------------------------------------------------------------------ planform outline
def outline_dirs(pf, chart_dirs, level, n=420, h=0.08, smooth=0.002):
    """unit directions of the planform iso-line sdf = level (mm, at pf.r), smoothed C2 periodic, n points"""
    m, ex, ey = FL.chart(chart_dirs); r = pf.r
    ext = []
    for Pc, rh in pf.hubs:
        g = Pc / (Pc @ m) * r; ext.append((g @ ex, g @ ey, rh / (Pc @ m) ** 2 + 3))
    x0 = min(e[0] - e[2] for e in ext); x1 = max(e[0] + e[2] for e in ext)
    y0 = min(e[1] - e[2] for e in ext); y1 = max(e[1] + e[2] for e in ext)
    xs = np.arange(x0, x1, h); ys = np.arange(y0, y1, h)
    GX, GY = np.meshgrid(xs, ys, indexing="ij")
    D = m * r + GX[..., None] * ex + GY[..., None] * ey; D /= np.linalg.norm(D, axis=-1, keepdims=True)
    sd = pf.sdf(D)
    cs = max(measure.find_contours(sd, level), key=len)
    x = np.interp(cs[:, 0], np.arange(len(xs)), xs); y = np.interp(cs[:, 1], np.arange(len(ys)), ys)
    if np.hypot(x[0] - x[-1], y[0] - y[-1]) < 1e-9: x, y = x[:-1], y[:-1]
    tck, _ = splprep([x, y], s=smooth * len(x), per=1, k=5)
    # resample uniformly by arc length
    uu = np.linspace(0, 1, 4000, endpoint=False); xx, yy = splev(uu, tck)
    sl = np.r_[0, np.cumsum(np.hypot(np.diff(np.r_[xx, xx[0]]), np.diff(np.r_[yy, yy[0]])))]
    us = np.interp(np.linspace(0, sl[-1], n, endpoint=False), sl, np.r_[uu, 1.0])
    xx, yy = splev(us, tck)
    D = m * r + np.outer(xx, ex) + np.outer(yy, ey); return D / np.linalg.norm(D, axis=1, keepdims=True)


def _sphere_face(edge_wire, R, axis_n, away):
    surf = Geom_SphericalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(*axis_n), gp_Dir(*away)), R)
    best = None
    for w in (edge_wire, TopoDS.Wire_s(edge_wire.Reversed())):
        f = BRepBuilderAPI_MakeFace(surf, w, True).Face()
        sf = ShapeFix_Face(f); sf.FixOrientationMode = 0
        try: sf.FixOrientationMode(0)
        except Exception: pass
        try: sf.FixAddNaturalBoundMode(0)
        except Exception: pass
        sf.Perform(); f = sf.Face(); A = cq.Face(f).Area()
        if A > 0 and (best is None or A < best[0]): best = (A, f)
    return best[1]


def _periodic_poles(Q):
    """poles of the uniform periodic cubic B-spline interpolating the closed point list Q (n,3) at its knots"""
    n = len(Q); ker = np.zeros(n); ker[0] = 4 / 6; ker[1] = ker[-1] = 1 / 6
    return np.real(np.fft.ifft(np.fft.fft(Q, axis=0) / np.fft.fft(ker)[:, None], axis=0))


def _uknots(n):
    from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
    uk = TColStd_Array1OfReal(1, n + 1); um = TColStd_Array1OfInteger(1, n + 1)
    for i in range(n + 1): uk.SetValue(i + 1, float(i)); um.SetValue(i + 1, 1)
    return uk, um


def _periodic_curve(Q, shift):
    from OCP.Geom import Geom_BSplineCurve
    Pp = np.roll(_periodic_poles(np.asarray(Q, float)), shift, 0); n = len(Pp)
    arr = TColgp_Array1OfPnt(1, n)
    for i, p in enumerate(Pp): arr.SetValue(i + 1, P(p))
    uk, um = _uknots(n); return Geom_BSplineCurve(arr, uk, um, 3, True)


_SHIFT = None
def _shift():
    """pole index offset so that the OCC periodic curve passes through Q[i] at u = i (found once numerically)"""
    global _SHIFT
    if _SHIFT is None:
        Q = np.c_[np.cos(np.linspace(0, 2 * np.pi, 12, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, 12, endpoint=False)), np.zeros(12)]
        for s in range(-3, 4):
            c = _periodic_curve(Q, s); p = c.Value(2.0)
            if abs(p.X() - Q[2, 0]) + abs(p.Y() - Q[2, 1]) < 1e-9: _SHIFT = s; break
    return _SHIFT


def _row_surface(rows, vdeg):
    """rows: list (n_v) of (n_u,3) station poles; periodic C2 cubic along u (uniform knots), Bezier degree vdeg along v"""
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
    from OCP.Geom import Geom_BSplineSurface
    nu = len(rows[0]); nv = len(rows); s = _shift()
    poles = TColgp_Array2OfPnt(1, nu, 1, nv)
    for j, R in enumerate(rows):
        Pp = np.roll(_periodic_poles(np.asarray(R, float)), s, 0)
        for i in range(nu): poles.SetValue(i + 1, j + 1, P(Pp[i]))
    uk, um = _uknots(nu)
    vk = TColStd_Array1OfReal(1, 2); vk.SetValue(1, 0.0); vk.SetValue(2, 1.0)
    vm = TColStd_Array1OfInteger(1, 2); vm.SetValue(1, vdeg + 1); vm.SetValue(2, vdeg + 1)
    return Geom_BSplineSurface(poles, uk, vk, um, vm, 3, vdeg, True, False)


def spherical_link(pf, chart_dirs, r0, r1, e, n=400):
    """solid link: planform pf (Planform at radius pf.r), shell r0..r1, G2 edge rounds of size e (lateral = radial).
    The edge band is three B-spline surfaces (G2 corner / radial wall / G2 corner) interpolated through the exact
    profile placed at n stations round the inset outline (profile plane = radial x outward-lateral)."""
    from OCP.GeomAPI import GeomAPI_Interpolate as _GI
    t = r1 - r0
    D = outline_dirs(pf, chart_dirs, -e * pf.r / r0, n)
    S = D * r0; seg = np.linalg.norm(np.roll(S, -1, 0) - S, axis=1); params = np.r_[0, np.cumsum(seg)[:-1]] / seg.sum()
    T = np.roll(S, -1, 0) - np.roll(S, 1, 0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    X = D; Y = np.cross(T, X); Y /= np.linalg.norm(Y, axis=1, keepdims=True)
    if pf.sdf(unit(S[0] + 0.3 * Y[0]))[()] < pf.sdf(unit(S[0]))[()]: Y = -Y
    C1, W, C2 = [], [], []
    for i in range(n):
        Q = lambda u, v: S[i] + u * X[i] + v * Y[i]
        C1.append(g2_blend(Q(0, 0), Y[i], 1 / r0, -X[i], Q(e, e), X[i], 0.0, -Y[i]))
        W.append([Q(e, e), Q(t - e, e)])
        C2.append(g2_blend(Q(t - e, e), X[i], 0.0, -Y[i], Q(t, 0), -Y[i], 1 / r1, -X[i]))
    C1, W, C2 = np.array(C1), np.array(W), np.array(C2)                 # (n, k, 3)
    faces = []
    for arr, deg in ((C1, 5), (W, 1), (C2, 5)):
        Sf = _row_surface([arr[:, k] for k in range(arr.shape[1])], deg)
        faces.append(BRepBuilderAPI_MakeFace(Sf, 1e-7).Face())
    # boundary loops on the spheres: the same periodic interpolation through the station points
    def loop(pts):
        return wire([BRepBuilderAPI_MakeEdge(_periodic_curve(pts, _shift())).Edge()])
    nrm = unit(np.cross(chart_dirs[0], chart_dirs[-1])) if len(chart_dirs) > 1 and np.linalg.norm(np.cross(chart_dirs[0], chart_dirs[-1])) > 1e-6 else unit(np.cross(chart_dirs[0], [0, 0, 1.0]))
    m = FL.chart(chart_dirs)[0]; away = unit(-m - (-m @ nrm) * nrm)
    fb = _sphere_face(loop(C1[:, 0]), r0, nrm, away); ft = _sphere_face(loop(C2[:, -1]), r1, nrm, away)
    sew = BRepBuilderAPI_Sewing(5e-3)
    for f in faces + [fb, ft]: sew.Add(f)
    sew.Perform(); sh = sew.SewedShape()
    ex = TopExp_Explorer(sh, TopAbs_SHELL); shell = TopoDS.Shell_s(ex.Current())
    so = BRepBuilderAPI_MakeSolid(shell).Solid(); fx = ShapeFix_Solid(so); fx.Perform(); so = fx.Solid()
    s = cq.Solid(so)
    if s.Volume() < 0: s = cq.Solid(so.Reversed())
    return s


def _radial_face(f):
    """True if the face is (close to) ruled along the radial direction (the swept closing line)"""
    ok = 0
    for (u, v) in ((0.3, 0.3), (0.6, 0.7), (0.5, 0.5)):
        p = f.positionAt(u, v); nn = f.normalAt(p)
        pv = np.array(p.toTuple()); nv = np.array(nn.toTuple())
        ok += abs(unit(pv) @ nv) < 0.05
    return ok == 3


def _edge_sdf(ed, pf):
    return float(np.mean([pf.sdf(unit(np.array(ed.positionAt(s).toTuple())))[()] for s in (0.05, 0.3, 0.55, 0.8)]))


# ------------------------------------------------------------------ revolve profiles  (rho, z) about an axis
def revolve_profile(segs, axis, ref=None):
    """segs: list of ('line', a, b) | ('arc', a, mid, b) | ('bez', [pts]) in (rho, z) mm, forming a closed loop.
    Revolved 360 deg about `axis` through the origin. Returns cq.Solid."""
    n = unit(axis); x = unit(np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0]))
    if ref is not None: x = unit(np.asarray(ref) - (np.asarray(ref) @ n) * n)
    to3 = lambda q: q[0] * x + q[1] * n
    es = []
    for s in segs:
        if s[0] == "line": es.append(line_edge(to3(s[1]), to3(s[2])))
        elif s[0] == "arc": es.append(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(P(to3(s[1])), P(to3(s[2])), P(to3(s[3]))).Value()).Edge())
        elif s[0] == "bez": es.append(bezier_edge([to3(q) for q in s[1]]))
    f = BRepBuilderAPI_MakeFace(wire(es), True).Face()
    rv = BRepPrimAPI_MakeRevol(f, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*n)), 2 * math.pi).Shape()
    s = cq.Shape.cast(rv)
    return s.Solids()[0] if hasattr(s, "Solids") and s.Solids() else s


def corner2d(a, ta, ka, na, b, tb, kb, nb, frac=0.3):
    return ("bez", g2_blend(a, ta, ka, na, b, tb, kb, nb, frac))


def valid(s): return BRepCheck_Analyzer(s.wrapped).IsValid()


# ------------------------------------------------------------------ flat G2 plate (same edge language as the links)
def flat_plate(sdf2, origin, ex, ey, z0, z1, e, extent, n=360, h=0.08):
    """plate between planes z0..z1 along n = ex x ey (from `origin`), planform sdf2(x, y) < 0 (mm, plane coords),
    G2 edge rounds of size e swept round the outline. extent = (x0, x1, y0, y1) for the contour grid."""
    from OCP.gp import gp_Pln
    origin, ex, ey = (np.asarray(v, float) for v in (origin, ex, ey)); nn = np.cross(ex, ey)
    xs = np.arange(extent[0], extent[1], h); ys = np.arange(extent[2], extent[3], h)
    GX, GY = np.meshgrid(xs, ys, indexing="ij"); sd = sdf2(GX, GY)
    cs = max(measure.find_contours(sd, -e), key=len)
    x = np.interp(cs[:, 0], np.arange(len(xs)), xs); y = np.interp(cs[:, 1], np.arange(len(ys)), ys)
    if np.hypot(x[0] - x[-1], y[0] - y[-1]) < 1e-9: x, y = x[:-1], y[:-1]
    tck, _ = splprep([x, y], s=0.002 * len(x), per=1, k=5)
    uu = np.linspace(0, 1, 4000, endpoint=False); xx, yy = splev(uu, tck)
    sl = np.r_[0, np.cumsum(np.hypot(np.diff(np.r_[xx, xx[0]]), np.diff(np.r_[yy, yy[0]])))]
    us = np.interp(np.linspace(0, sl[-1], n, endpoint=False), sl, np.r_[uu, 1.0]); xx, yy = splev(us, tck)
    S = origin + np.outer(xx, ex) + np.outer(yy, ey) + z0 * nn
    T = np.roll(S, -1, 0) - np.roll(S, 1, 0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    Y = np.cross(T, nn); Y /= np.linalg.norm(Y, axis=1, keepdims=True)
    q0 = S[0] - origin - z0 * nn
    if sdf2(q0 @ ex + 0.3 * (Y[0] @ ex), q0 @ ey + 0.3 * (Y[0] @ ey)) < sdf2(q0 @ ex, q0 @ ey): Y = -Y
    t = z1 - z0; C1, Wl, C2 = [], [], []
    for i in range(n):
        Q = lambda u, v: S[i] + u * nn + v * Y[i]
        C1.append(g2_blend(Q(0, 0), Y[i], 0.0, nn, Q(e, e), nn, 0.0, -Y[i]))
        Wl.append([Q(e, e), Q(t - e, e)])
        C2.append(g2_blend(Q(t - e, e), nn, 0.0, -Y[i], Q(t, 0), -Y[i], 0.0, -nn))
    C1, Wl, C2 = np.array(C1), np.array(Wl), np.array(C2)
    faces = [BRepBuilderAPI_MakeFace(_row_surface([arr[:, k] for k in range(arr.shape[1])], deg), 1e-7).Face() for arr, deg in ((C1, 5), (Wl, 1), (C2, 5))]
    def pface(pts, zz):
        w = wire([BRepBuilderAPI_MakeEdge(_periodic_curve(pts, _shift())).Edge()])
        pln = gp_Pln(gp_Pnt(*(origin + zz * nn)), gp_Dir(*nn))
        return BRepBuilderAPI_MakeFace(pln, w, True).Face()
    sew = BRepBuilderAPI_Sewing(5e-3)
    for f in faces + [pface(C1[:, 0], z0), pface(C2[:, -1], z1)]: sew.Add(f)
    sew.Perform(); sh = sew.SewedShape(); exs = TopExp_Explorer(sh, TopAbs_SHELL)
    so = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(exs.Current())).Solid(); fx = ShapeFix_Solid(so); fx.Perform(); so = fx.Solid()
    s = cq.Solid(so)
    if s.Volume() < 0: s = cq.Solid(so.Reversed())
    return s


def dome_cap_profile(R, H, r_lip, r_cb, d_cb, skirt=0.5, bottom_ch=0.2, r_hole=2.25):
    """(rho, z) closed profile of a joint cap whose top is one curvature-continuous dome (no flat land):
    skirt (vertical, z 0.2..skirt) -> dome (vertical tangent at the rim, horizontal tangent at the lip, curvature matched
    to the lip) -> lip round into the screw counterbore (radius r_cb, depth d_cb) -> clearance hole r_hole.
    R outer radius, H total height. Returns segment list for revolve_profile."""
    k_lip = 1.0 / max(0.4, (r_lip - r_cb))                 # lip curvature (a quarter-turn over r_lip - r_cb)
    up, out, inn, down = (0, 1.0), (1.0, 0), (-1.0, 0), (0, -1.0)
    segs = [("line", (r_hole, 0.0), (R - bottom_ch, 0.0)), ("line", (R - bottom_ch, 0.0), (R, bottom_ch)),
            ("line", (R, bottom_ch), (R, skirt)),
            # dome: leaves the skirt going up (curvature 0, G2 with the straight skirt), turns inward, arrives horizontal
            ("bez", g2_blend((R, skirt), up, 0.0, inn, (r_lip, H), inn, k_lip, down, frac=0.42)),
            # lip: from horizontal (same curvature) down into the counterbore wall (vertical, curvature 0)
            ("bez", g2_blend((r_lip, H), inn, k_lip, down, (r_cb, H - (r_lip - r_cb)), down, 0.0, out, frac=0.36)),
            ("line", (r_cb, H - (r_lip - r_cb)), (r_cb, H - d_cb)), ("line", (r_cb, H - d_cb), (r_hole, H - d_cb)),
            ("line", (r_hole, H - d_cb), (r_hole, 0.0))]
    return segs
