"""Fair G2 sheet bodies (the new EXO CAD pipeline core).

A plate = skin-side surface + outer surface over one closed planform, edged all round by a curvature-continuous round
(G2 blend -> wall -> G2 blend). Five faces, sewn into one solid: no booleans, no filleted cuts, no end caps.
  - surfaces are spherical graphs about the GH centre, P = rho(d) d, over an azimuthal-equidistant chart (x, y in mm at
    radius R0 about a centre direction c0); the B-spline surfaces are parameterised by the chart itself, so the planform
    outline is one exact periodic 2D curve on both of them (exact trimming, nothing projected)
  - flat seats are exact planes sampled into the surface (rho = z / (d . a)); deviation from the plane < 1 um
"""
import math
import numpy as np
import cadquery as cq
from scipy.interpolate import RectBivariateSpline, splprep, splev
from skimage import measure
from OCP.gp import gp_Pnt, gp_Pnt2d
from OCP.TColgp import TColgp_Array2OfPnt, TColgp_Array1OfPnt2d
from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
from OCP.Geom import Geom_BSplineSurface
from OCP.Geom2d import Geom2d_BSplineCurve
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.BRepLib import BRepLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopoDS import TopoDS
from OCP.ShapeFix import ShapeFix_Solid, ShapeFix_Face
from OCP.GeomLProp import GeomLProp_SLProps
from OCP.GeomAbs import GeomAbs_C2
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "shoulder-d4"))
import g2cad as G

def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)

class Chart:
    """azimuthal-equidistant chart about c0: (x, y) mm at radius R0 <-> unit direction"""
    def __init__(self, c0, e1, R0):
        self.c0 = unit(c0); e1 = np.asarray(e1, float); e1 = unit(e1 - (e1 @ self.c0) * self.c0); self.e1 = e1; self.e2 = np.cross(self.c0, e1); self.R0 = float(R0)
    def dirs(self, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float); r = np.hypot(x, y) / self.R0
        s = np.where(r > 1e-12, np.sin(r) / np.maximum(r, 1e-12), 1.0) / self.R0
        return np.cos(r)[..., None] * self.c0 + (s * x)[..., None] * self.e1 + (s * y)[..., None] * self.e2
    def xy(self, d):
        d = unit(d); ang = np.arccos(np.clip(d @ self.c0, -1, 1)); p = d - (d @ self.c0)[..., None] * self.c0
        n = np.linalg.norm(p, axis=-1); f = np.where(n > 1e-12, ang / np.maximum(n, 1e-12), 1.0) * self.R0
        return np.stack([(p @ self.e1) * f, (p @ self.e2) * f], -1)

def _knots(t):
    u, m = np.unique(np.round(t, 12), return_counts=True)
    K = TColStd_Array1OfReal(1, len(u)); M = TColStd_Array1OfInteger(1, len(u))
    for i, (a, b) in enumerate(zip(u, m)): K.SetValue(i + 1, float(a)); M.SetValue(i + 1, int(b))
    return K, M

def surface(chart, rho_xy, x0, x1, y0, y1, h=0.6):
    """cubic B-spline surface P(x, y) = rho(x, y) d(x, y) interpolated on a chart grid; parameters = chart mm"""
    xs = np.linspace(x0, x1, max(6, int(math.ceil((x1 - x0) / h)) + 1)); ys = np.linspace(y0, y1, max(6, int(math.ceil((y1 - y0) / h)) + 1))
    X, Y = np.meshgrid(xs, ys, indexing="ij"); D = chart.dirs(X, Y); Rh = rho_xy(X, Y); P = D * Rh[..., None]
    fits = [RectBivariateSpline(xs, ys, P[..., k], kx=3, ky=3, s=0) for k in range(3)]
    tx, ty = fits[0].get_knots(); tx_full, ty_full = fits[0].tck[0], fits[0].tck[1]
    nx, ny = len(tx_full) - 4, len(ty_full) - 4; C = np.stack([f.tck[2].reshape(nx, ny) for f in fits], -1)
    poles = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(nx):
        for j in range(ny): poles.SetValue(i + 1, j + 1, gp_Pnt(*map(float, C[i, j])))
    uk, um = _knots(tx_full); vk, vm = _knots(ty_full)
    return Geom_BSplineSurface(poles, uk, vk, um, vm, 3, 3, False, False)

def _periodic_poles(Q):
    n = len(Q); ker = np.zeros(n); ker[0] = 4 / 6; ker[1] = ker[-1] = 1 / 6
    return np.real(np.fft.ifft(np.fft.fft(Q, axis=0) / np.fft.fft(ker)[:, None], axis=0))

def pcurve(Q2):
    """periodic uniform cubic 2D B-spline through Q2 (n,2) at u = 0..n-1 (same convention as g2cad._periodic_curve)"""
    Pp = np.roll(_periodic_poles(np.asarray(Q2, float)), G._shift(), 0); n = len(Pp)
    arr = TColgp_Array1OfPnt2d(1, n)
    for i, p in enumerate(Pp): arr.SetValue(i + 1, gp_Pnt2d(float(p[0]), float(p[1])))
    uk, um = G._uknots(n); return Geom2d_BSplineCurve(arr, uk, um, 3, True)

def outline(sdf2, extent, e, h=0.1, n=360):
    """closed G2 planform outline (chart coords) = level set sdf = -e (the round sits outside it), n points equally spaced"""
    xs = np.arange(extent[0], extent[1], h); ys = np.arange(extent[2], extent[3], h)
    GX, GY = np.meshgrid(xs, ys, indexing="ij"); sd = sdf2(GX, GY)
    cs = max(measure.find_contours(sd, -e), key=len)
    x = np.interp(cs[:, 0], np.arange(len(xs)), xs); y = np.interp(cs[:, 1], np.arange(len(ys)), ys)
    if np.hypot(x[0] - x[-1], y[0] - y[-1]) < 1e-9: x, y = x[:-1], y[:-1]
    tck, _ = splprep([x, y], s=0.002 * len(x), per=1, k=5)
    uu = np.linspace(0, 1, 6000, endpoint=False); xx, yy = splev(uu, tck)
    sl = np.r_[0, np.cumsum(np.hypot(np.diff(np.r_[xx, xx[0]]), np.diff(np.r_[yy, yy[0]])))]
    us = np.interp(np.linspace(0, sl[-1], n, endpoint=False), sl, np.r_[uu, 1.0]); xx, yy = splev(us, tck)
    Q = np.c_[xx, yy]
    if 0.5 * np.sum(Q[:, 0] * np.roll(Q[:, 1], -1) - np.roll(Q[:, 0], -1) * Q[:, 1]) < 0: Q = Q[::-1]       # CCW in the chart
    return Q

def _eval(S, x, y):
    pr = GeomLProp_SLProps(S, float(x), float(y), 1, 1e-9); p = pr.Value(); n = pr.Normal()
    return np.array([p.X(), p.Y(), p.Z()]), np.array([n.X(), n.Y(), n.Z()]), pr

def sheet_solid(chart, rho_bot, rho_top, sdf2, extent, e=1.2, n=360, h=0.6, wall_min=0.25):
    """the plate between rho_bot(x, y) (skin side) and rho_top(x, y) over planform sdf2 < 0 (chart mm), G2 rounds of size e all round"""
    Q = outline(sdf2, extent, e, n=n)
    pad = e + 3.0; x0, x1 = Q[:, 0].min() - pad, Q[:, 0].max() + pad; y0, y1 = Q[:, 1].min() - pad, Q[:, 1].max() + pad
    SB = surface(chart, rho_bot, x0, x1, y0, y1, h); ST = surface(chart, rho_top, x0, x1, y0, y1, h)
    Bp, Tp, NB, NT = [], [], [], []
    for x, y in Q:
        pb, nb, _ = _eval(SB, x, y); pt, nt, _ = _eval(ST, x, y)
        Bp.append(pb); Tp.append(pt); NB.append(nb); NT.append(nt)
    Bp, Tp, NB, NT = map(np.array, (Bp, Tp, NB, NT))
    up = unit(Tp - Bp)                                                                     # material side (skin -> outer)
    NB = NB * np.sign((NB * up).sum(1))[:, None]; NT = NT * np.sign((NT * up).sum(1))[:, None]      # both normals point outward-up
    TB = unit(np.roll(Bp, -1, 0) - np.roll(Bp, 1, 0)); TT = unit(np.roll(Tp, -1, 0) - np.roll(Tp, 1, 0))
    YB = unit(np.cross(TB, NB)); YT = unit(np.cross(TT, NT))
    # outward = away from the planform interior (test against the chart sdf)
    xyo = chart.xy(unit(Bp + 0.3 * YB)); s_out = np.sign(sdf2(xyo[:, 0], xyo[:, 1]) - sdf2(Q[:, 0], Q[:, 1])); YB *= s_out[:, None]
    xyo = chart.xy(unit(Tp + 0.3 * YT)); s_out = np.sign(sdf2(xyo[:, 0], xyo[:, 1]) - sdf2(Q[:, 0], Q[:, 1])); YT *= s_out[:, None]
    Wb = Bp + e * YB + e * NB; Wt = Tp + e * YT - e * NT
    th = np.linalg.norm(Wt - Wb, axis=1)
    if th.min() < wall_min: raise ValueError(f"sheet too thin for e={e}: wall {th.min():.2f} mm")
    WD = unit(Wt - Wb); C1, C2 = [], []
    for i in range(n):
        C1.append(G.g2_blend(Bp[i], YB[i], 0.0, NB[i], Wb[i], WD[i], 0.0, -YB[i]))
        C2.append(G.g2_blend(Wt[i], WD[i], 0.0, -YT[i], Tp[i], -YT[i], 0.0, -NT[i]))
    C1, C2 = np.array(C1), np.array(C2); Wl = np.stack([Wb, Wt], 1)
    faces = [BRepBuilderAPI_MakeFace(G._row_surface([arr[:, k] for k in range(arr.shape[1])], deg), 1e-7).Face() for arr, deg in ((C1, 5), (Wl, 1), (C2, 5))]
    def trimmed(S):
        c2 = pcurve(Q); ed = BRepBuilderAPI_MakeEdge(c2, S).Edge(); BRepLib.BuildCurves3d_s(ed, 1e-6, GeomAbs_C2, 9, 2 * len(Q))
        w = BRepBuilderAPI_MakeWire(ed).Wire(); f = BRepBuilderAPI_MakeFace(S, w, True).Face()
        sf = ShapeFix_Face(f); sf.Perform(); return sf.Face()
    tb_, tt_ = trimmed(SB), trimmed(ST)
    # sew the five faces into ONE closed shell. The edge rounds are interpolated through the outline stations while the
    # trimmed skin/outer faces carry the exact outline curve: on steep or strongly curved members the two drift apart by
    # more than 5 um between stations, the sewing then leaves free edges and several shells, and taking the first shell
    # gave an open "solid" with 3-4 faces and a meaningless (near zero) volume. Retry with a wider tolerance, then check.
    for tol in ((5e-3,) if os.environ.get("SEW_V1") == "1" else (5e-3, 2e-2, 5e-2, 0.1)):         # SEW_V1=1: the old single try (reproduction)
        sew = BRepBuilderAPI_Sewing(tol)
        for f in faces + [tb_, tt_]: sew.Add(f)
        sew.Perform(); sh = sew.SewedShape(); shells = []; exs = TopExp_Explorer(sh, TopAbs_SHELL)
        while exs.More(): shells.append(TopoDS.Shell_s(exs.Current())); exs.Next()
        if len(shells) == 1 and sew.NbFreeEdges() == 0: break
    sew_info = dict(tol=tol, shells=len(shells), free_edges=int(sew.NbFreeEdges()))
    shell = shells[0] if os.environ.get("SEW_V1") == "1" else max(shells, key=lambda s_: sum(1 for _ in _faces_of(s_)))
    so = BRepBuilderAPI_MakeSolid(shell).Solid(); fx = ShapeFix_Solid(so); fx.Perform(); so = fx.Solid()
    s = cq.Solid(so)
    if s.Volume() < 0: s = cq.Solid(so.Reversed())
    return s, dict(Q=Q, SB=SB, ST=ST, sew=sew_info, thickness=(float(np.linalg.norm(Tp - Bp, axis=1).min()), float(np.linalg.norm(Tp - Bp, axis=1).max())))

def _faces_of(shape):
    from OCP.TopAbs import TopAbs_FACE
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More(): yield ex.Current(); ex.Next()

def sheet_solid_v2(chart, rho_bot, rho_top, sdf2, extent, e_bot, e_top, wall_dir, n=480, h=0.6, wall_min=0.2):
    """sheet_solid with designed walls (strap links, members.Strap): the sketch outline sdf2 = 0 is the wall; the skin-side
    round has its own size e_bot(x, y) and the outer round e_top(x, y) (per station, smooth fields); the wall runs along
    wall_dir(P) (unit, per point: the hub axis around a hub pad -> true cylinders, the strap's in-plane normal along it ->
    a constant rectangular section) instead of radially from the GH centre. The top outline is where that wall line meets
    the top surface, moved in by e_top; both trimmed faces carry their own exact outline. The default sheet_solid is
    unchanged."""
    Q = outline(lambda x, y: sdf2(x, y) + e_bot(x, y), extent, 0.0, n=n)
    eb = np.asarray(e_bot(Q[:, 0], Q[:, 1]), float); et = np.asarray(e_top(Q[:, 0], Q[:, 1]), float)
    pad = float(max(eb.max(), et.max())) + 4.0; x0, x1 = Q[:, 0].min() - pad, Q[:, 0].max() + pad; y0, y1 = Q[:, 1].min() - pad, Q[:, 1].max() + pad
    SB = surface(chart, rho_bot, x0, x1, y0, y1, h); ST = surface(chart, rho_top, x0, x1, y0, y1, h)
    Bp, NB = [], []
    for x, y in Q:
        pb, nb, _ = _eval(SB, x, y); Bp.append(pb); NB.append(nb)
    Bp, NB = np.array(Bp), np.array(NB); WD0 = unit(wall_dir(Bp))
    NB = NB * np.sign((NB * WD0).sum(1))[:, None]                                          # bottom normal into the material
    TB = unit(np.roll(Bp, -1, 0) - np.roll(Bp, 1, 0)); YB = unit(np.cross(TB, NB))
    xyo = chart.xy(unit(Bp + 0.3 * YB)); s_out = np.sign(sdf2(xyo[:, 0], xyo[:, 1]) - sdf2(Q[:, 0], Q[:, 1])); YB *= s_out[:, None]
    Wb = Bp + eb[:, None] * YB + eb[:, None] * NB
    # the wall line from Wb along the wall direction meets the top surface at X (bisection on |L(t)| - rho_top(dir L(t)))
    def f(t):
        L = Wb + t[:, None] * WD0; xy = chart.xy(unit(L)); return np.linalg.norm(L, axis=1) - rho_top(xy[:, 0], xy[:, 1])
    lo = np.zeros(len(Q)); hi = np.full(len(Q), 40.0)
    if (f(lo) > 0).any(): raise ValueError(f"sheet_solid_v2: the wall starts above the top surface at {int((f(lo) > 0).sum())} stations")
    for _ in range(50):
        mid = 0.5 * (lo + hi); up = f(mid) > 0; hi = np.where(up, mid, hi); lo = np.where(up, lo, mid)
    X = Wb + (0.5 * (lo + hi))[:, None] * WD0
    def top_pt(P):
        xy = chart.xy(unit(P)); return np.array([_eval(ST, x, y)[0] for x, y in xy]), xy
    _, nT = zip(*[_eval(ST, *chart.xy(unit(p[None]))[0])[:2] for p in X]); NT = np.array(nT); NT = NT * np.sign((NT * WD0).sum(1))[:, None]
    TT = unit(np.roll(X, -1, 0) - np.roll(X, 1, 0)); YT = unit(np.cross(TT, NT)); YT *= np.sign((YT * YB).sum(1))[:, None]
    Tp, Qt = top_pt(X - et[:, None] * YT)                                                  # top outline: e_top in from the wall
    NT = np.array([_eval(ST, x, y)[1] for x, y in Qt]); NT = NT * np.sign((NT * WD0).sum(1))[:, None]
    TT = unit(np.roll(Tp, -1, 0) - np.roll(Tp, 1, 0)); YT = unit(np.cross(TT, NT)); YT *= np.sign((YT * YB).sum(1))[:, None]
    Wt = Tp + et[:, None] * YT - et[:, None] * NT
    th = np.linalg.norm(Wt - Wb, axis=1)
    if ((Wt - Wb) * WD0).sum(1).min() < wall_min: raise ValueError(f"sheet_solid_v2: wall {((Wt - Wb) * WD0).sum(1).min():.2f} mm (rounds too big for the thickness)")
    WD = unit(Wt - Wb); C1, C2 = [], []
    for i in range(len(Q)):
        C1.append(G.g2_blend(Bp[i], YB[i], 0.0, NB[i], Wb[i], WD[i], 0.0, -YB[i]))
        C2.append(G.g2_blend(Wt[i], WD[i], 0.0, -YT[i], Tp[i], -YT[i], 0.0, -NT[i]))
    C1, C2 = np.array(C1), np.array(C2); Wl = np.stack([Wb, Wt], 1)
    faces = [BRepBuilderAPI_MakeFace(G._row_surface([arr[:, k] for k in range(arr.shape[1])], deg), 1e-7).Face() for arr, deg in ((C1, 5), (Wl, 1), (C2, 5))]
    def trimmed(S, Q2):
        c2 = pcurve(Q2); ed = BRepBuilderAPI_MakeEdge(c2, S).Edge(); BRepLib.BuildCurves3d_s(ed, 1e-6, GeomAbs_C2, 9, 2 * len(Q2))
        w = BRepBuilderAPI_MakeWire(ed).Wire(); fc = BRepBuilderAPI_MakeFace(S, w, True).Face()
        sf = ShapeFix_Face(fc); sf.Perform(); return sf.Face()
    tb_, tt_ = trimmed(SB, Q), trimmed(ST, Qt)
    for tol in (5e-3, 2e-2, 5e-2, 0.1):
        sew = BRepBuilderAPI_Sewing(tol)
        for fc in faces + [tb_, tt_]: sew.Add(fc)
        sew.Perform(); sh = sew.SewedShape(); shells = []; exs = TopExp_Explorer(sh, TopAbs_SHELL)
        while exs.More(): shells.append(TopoDS.Shell_s(exs.Current())); exs.Next()
        if len(shells) == 1 and sew.NbFreeEdges() == 0: break
    sew_info = dict(tol=tol, shells=len(shells), free_edges=int(sew.NbFreeEdges()))
    shell = max(shells, key=lambda s_: sum(1 for _ in _faces_of(s_)))
    so = BRepBuilderAPI_MakeSolid(shell).Solid(); fx = ShapeFix_Solid(so); fx.Perform(); so = fx.Solid()
    s = cq.Solid(so)
    if s.Volume() < 0: s = cq.Solid(so.Reversed())
    return s, dict(Q=Q, Qt=Qt, SB=SB, ST=ST, sew=sew_info, thickness=(float(th.min()), float(th.max())), wall=float(((Wt - Wb) * WD0).sum(1).min()))
