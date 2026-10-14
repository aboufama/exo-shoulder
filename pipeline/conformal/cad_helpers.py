"""Shared CAD helpers for the shoulder builders (copied verbatim from build_conformal.py / build_full_conformal.py):
G2 rounded-rectangle sections, loop chaining, planform half-width, rigid transforms, revolve tools."""
import json, math, os, sys
import numpy as np
import cadquery as cq
from scipy.interpolate import UnivariateSpline
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "shoulder-d4"))
import g2cad as G
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCP.TopTools import TopTools_ListOfShape
HUB_R, HW, E_LO, E_UP = 17.0, 7.0, 1.5, 1.2
T_LO, T_UP, T_W, T_CAP = 5.0, 5.5, 1.0, 3.0
PIN_D, SLV_OD, SLV_L, WASH_ID, WASH_OD = 10.0, 12.0, 5.0, 10.0, 18.0
SCR_HEAD_D, SCR_HEAD_H = 7.1, 2.0
T_BOT = 6.5


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)

def V(p): return cq.Vector(*map(float, p))

def fuzzy_fuse(a, b, tol=0.1):
    args = TopTools_ListOfShape(); args.Append(a.wrapped); tools = TopTools_ListOfShape(); tools.Append(b.wrapped)
    f = BRepAlgoAPI_Fuse(); f.SetArguments(args); f.SetTools(tools); f.SetFuzzyValue(tol); f.Build(); return cq.Shape.cast(f.Shape())

def glue_fuse(a, b, shift=True):
    """fuse of solids that touch along coincident faces (e.g. a neck ending exactly on a cut face): OCC glue mode, then
    unify same-domain faces so the shared face disappears"""
    from OCP.BOPAlgo import BOPAlgo_GlueShift, BOPAlgo_GlueFull
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    args = TopTools_ListOfShape(); args.Append(a.wrapped); tools = TopTools_ListOfShape(); tools.Append(b.wrapped)
    f = BRepAlgoAPI_Fuse(); f.SetArguments(args); f.SetTools(tools); f.SetGlue(BOPAlgo_GlueShift if shift else BOPAlgo_GlueFull); f.Build()
    if not f.IsDone(): return None
    u = ShapeUpgrade_UnifySameDomain(f.Shape(), True, True, True); u.Build(); return cq.Shape.cast(u.Shape())

def frame_of(axis):
    n = unit(axis); x = unit(np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])); return n, x, np.cross(n, x)

def section_outline(width, t, e, n=160):
    """G2 rounded rectangle (centred), corners of size e; returns (n,2) closed outline (x = across, y = up)"""
    hw, ht = width / 2, t / 2; segs = []
    corners = [((hw, -ht + e), (0, 1.0), (hw - e, ht), (-1.0, 0)), ((-hw + e, ht), (-1.0, 0), (-hw, ht - e), (0, -1.0)),
               ((-hw, -ht + e), (0, -1.0), (-hw + e, -ht), (1.0, 0)), ((hw - e, -ht), (1.0, 0), (hw, -ht + e), (0, 1.0))]
    # walk: right wall up, top-right corner, top, top-left corner, left wall down, bottom-left, bottom, bottom-right
    pts = []
    def line(a, b, m): return [np.array(a) + (np.array(b) - np.array(a)) * t_ for t_ in np.linspace(0, 1, m, endpoint=False)]
    def corner(a, ta, b, tb, m):
        cp = G.g2_blend(np.r_[a, 0], np.r_[ta, 0], 0.0, np.r_[tb, 0], np.r_[b, 0], np.r_[tb, 0], 0.0, -np.r_[ta, 0], frac=0.3)
        cp = np.array(cp)[:, :2]; from math import comb
        ts = np.linspace(0, 1, m, endpoint=False); return [sum(comb(5, i) * (1 - u) ** (5 - i) * u ** i * cp[i] for i in range(6)) for u in ts]
    pts += line((hw, -ht + e), (hw, ht - e), 8); pts += corner((hw, ht - e), (0, 1), (hw - e, ht), (-1, 0), 14)
    pts += line((hw - e, ht), (-hw + e, ht), 20); pts += corner((-hw + e, ht), (-1, 0), (-hw, ht - e), (0, -1), 14)
    pts += line((-hw, ht - e), (-hw, -ht + e), 8); pts += corner((-hw, -ht + e), (0, -1), (-hw + e, -ht), (1, 0), 14)
    pts += line((-hw + e, -ht), (hw - e, -ht), 20); pts += corner((hw - e, -ht), (1, 0), (hw, -ht + e), (0, 1), 14)
    pts = np.array(pts); seg = np.linalg.norm(np.diff(np.r_[pts, pts[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    tt = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(tt, sl, np.r_[pts[:, k], pts[0, k]]) for k in range(2)]).T

def chain_loop(edges, n, ref_u, ref_v):
    segs = [np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 30)]) for e in edges]; loop = segs.pop(0)
    while segs:
        end = loop[-1]; k = min(range(len(segs)), key=lambda i: min(np.linalg.norm(segs[i][0] - end), np.linalg.norm(segs[i][-1] - end)))
        s = segs.pop(k); s = s[::-1] if np.linalg.norm(s[-1] - end) < np.linalg.norm(s[0] - end) else s; loop = np.r_[loop, s[1:]]
    if np.linalg.norm(loop[-1] - loop[0]) < 1e-3: loop = loop[:-1]
    c = loop.mean(0); x2, y2 = (loop - c) @ ref_u, (loop - c) @ ref_v
    if 0.5 * np.sum(x2 * np.roll(y2, -1) - np.roll(x2, -1) * y2) < 0: loop = loop[::-1]
    seg = np.linalg.norm(np.diff(np.r_[loop, loop[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    tt = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(tt, sl, np.r_[loop[:, k], loop[0, k]]) for k in range(3)]).T

def upper_spline(s, y, smooth=2.0):
    """smooth curve through y(s) that is never below the data"""
    sp = UnivariateSpline(s, y, k=3, s=smooth * len(s))
    f = sp(s); lift = max(0.0, float((y - f).max())); return lambda q: sp(q) + lift + 0.4

def planform_halfwidth(x, stub_len=60.0, k=8.0):
    """half-width of the hub planform (disc HUB_R + strip HW, cubic smooth-min waist) at distance x from the pin"""
    def sdf2(xx, yy):
        d1 = np.hypot(xx, yy) - HUB_R; d2 = np.maximum(np.abs(yy) - HW, np.maximum(xx - stub_len, -xx))
        h = np.maximum(k - np.abs(d1 - d2), 0) / k; return np.minimum(d1, d2) - h ** 3 * k / 6
    lo, hi = 0.0, HUB_R + 6
    if sdf2(x, 0.0) >= 0: return 0.0
    for _ in range(40):
        m = 0.5 * (lo + hi); lo, hi = (m, hi) if sdf2(x, m) < 0 else (lo, m)
    return lo

def xform(shape, R, t):
    tr = gp_Trsf(); tr.SetValues(*R[0], t[0], *R[1], t[1], *R[2], t[2]); return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())

def cad_to_rest(shape, grp):
    R = R_UP if grp == "up" else R_FO; return xform(shape, R, CB - R @ np.array(FA.C_cad))

def cyl(axis, z0, z1, r, off=(0.0, 0.0)):
    n, x, y = frame_of(axis); return cq.Solid.makeCylinder(r, z1 - z0, V(n * z0 + x * off[0] + y * off[1]), V(n))

def cone(axis, z0, r0, z1, r1):
    n, _, _ = frame_of(axis); return cq.Solid.makeCone(r0, r1, z1 - z0, V(n * z0), V(n))

def bore_tool(axis, z0, z1, r, ch=0.3, ext=3.0):
    """one revolved tool: through bore radius r between faces z0..z1 with 45 deg chamfers at both faces"""
    segs = [("line", (0, z0 - ext), (r + ch + ext, z0 - ext)), ("line", (r + ch + ext, z0 - ext), (r, z0 + ch)), ("line", (r, z0 + ch), (r, z1 - ch)),
            ("line", (r, z1 - ch), (r + ch + ext, z1 + ext)), ("line", (r + ch + ext, z1 + ext), (0, z1 + ext)), ("line", (0, z1 + ext), (0, z0 - ext))]
    return G.revolve_profile(segs, axis)
