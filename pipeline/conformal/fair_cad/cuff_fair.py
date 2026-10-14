"""Upper-arm cuff v2: a conformal G2 shell instead of the scaled forearm cuff.

Built on the same sheet machinery as the links (two B-spline surfaces over one exact pcurve-trimmed planform, G2 edge
band all round, five faces sewn), but over a cylindrical chart about the humerus axis (x = R0 * theta, y = s from GH):
  inner  = smooth upper envelope of the upper-arm skin over EVERY clip frame (biceps / triceps bulge included,
           out_cuff/envelope.npz) + LINER_MIN (fully compressed 3D-spacer liner)
  outer  = inner + T_SHELL, except under BOTTOM: a flat land in BOTTOM's skin-side plane (exact plane sampled into the
           surface) T_LAND thick, blended G2 into the shell -> the shell only rises where the bar sits
  planform = 230 deg C centred on the bar (open medially, closed by the knit band), long spine under the bar (the 3 screw
           pairs), tapering wings; the anterior wing's elbow side is scalloped wherever the forearm or the forearm cuff
           comes within CLEAR_FO of the shell at deep elbow flexion
  6x M4x6 ISO 10642 from inside (heads flush with the land's inner face, under the liner) into BOTTOM's tapped holes
Frame: the arm's rest frame (group H), mm.
    python3 cuff_fair.py  -> ../../full-exo/upper_cuff_fair.step, out_cuff/cuff.glb, out_cuff/report.json
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
from scipy.ndimage import maximum_filter, gaussian_filter, distance_transform_edt, binary_closing, binary_opening
from scipy.interpolate import RectBivariateSpline
from OCP.gp import gp_Pnt
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.Geom import Geom_BSplineSurface
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sheet as SH
from sheet import G
FX = os.path.join(HERE, "..", "..", "full-exo")

LINER_MIN, T_SHELL, T_LAND = 2.0, 2.0, 2.8           # compressed liner over the swept envelope; shell; land under the bar
BAR_HW, LAND_PAD, BLEND = 15.0, 0.6, 8.0
LAM = float(os.environ.get("CUFF_LAM", 300.0))      # fairness (bending) weight of the inner surface            # bar half width; flat land beyond the bar edge; land -> shell G2 blend
CLEAR_FO = 3.0                                        # shell to forearm / forearm cuff at deep flexion
EDGE = 0.85                                           # G2 edge round
R0 = 50.0                                             # chart radius (x = R0 * theta)
S_SCREW = (94.25, 124.25, 154.25); Y_SCREW = (-8.75, 8.75)

E = np.load(os.path.join(HERE, "out_cuff", "envelope.npz"))
TH, SS = E["TH"] + 1.0, E["SS"] + 1.0                 # cell centres
a, e1, e2 = E["a"], E["e1"], E["e2"]; CB, uB, vB, axB = E["CB"], E["uB"], E["vB"], E["axB"]
def smooth(t): t = np.clip(t, 0, 1); return t * t * t * (t * (6 * t - 15) + 10)
def cyl(x, y, r):
    th = np.asarray(x) / R0; return (np.asarray(y)[..., None] * a + np.asarray(r)[..., None] * (np.cos(th)[..., None] * e1 + np.sin(th)[..., None] * e2))
def to_xy(P):
    P = np.atleast_2d(P); return np.c_[R0 * np.arctan2(P @ e2, P @ e1), P @ a]

# ---------------------------------------------------------------- swept envelope (lower bound of the inner surface)
def fill(R):
    R = np.where(np.isfinite(R), R, np.nan); m = np.isnan(R)
    if m.any():
        idx = distance_transform_edt(m, return_distances=False, return_indices=True); R = R[tuple(idx)]
    return R
Ra = maximum_filter(np.where(np.isfinite(E["R_arm"]), E["R_arm"], -1e9), size=(3, 3), mode="wrap"); Ra[Ra < 0] = np.nan; Ra = fill(Ra)
def upper_smooth(R, sig, it=8):
    """smooth surface that stays above R (removes the raster noise of the swept envelope, never cuts into it)"""
    S = R.copy()
    for _ in range(it): S = np.maximum(R, gaussian_filter(S, sig, mode="wrap"))
    S = gaussian_filter(S, sig, mode="wrap"); return S + gaussian_filter(maximum_filter(np.maximum(R - S, 0), size=(9, 9), mode="wrap"), sig, mode="wrap") * 1.8
Ras = upper_smooth(Ra, (2.5, 2.5)); print(f"swept envelope smoothed: residual under it {np.max(Ra - Ras):.2f} mm", flush=True)
f_lb = RectBivariateSpline(np.radians(TH) * R0, SS, np.maximum(Ras, Ra), kx=3, ky=3, s=0)     # swept arm skin (max over frames), smoothed upper bound
Rfo = E["R_fo"]
def X(th_deg): return R0 * math.radians(th_deg)

# ---------------------------------------------------------------- the bar's land
n_b = axB; c_b = CB @ axB - 2.8                                  # BOTTOM's skin-side plane: X . axB = c_b
def r_plane(x, y):
    th = np.asarray(x) / R0; d = np.cos(th)[..., None] * e1 + np.sin(th)[..., None] * e2
    return (c_b - np.asarray(y) * (a @ n_b)) / np.maximum(d @ n_b, 0.2)
def land_w(x, y):
    """1 on the land (bar footprint + pad), G2 down to 0 over BLEND (lateral distance on the bar plane)"""
    P = cyl(x, y, r_plane(x, y)); v = np.abs((P - CB) @ vB)
    return 1.0 - smooth((v - BAR_HW - LAND_PAD) / BLEND)

# ---------------------------------------------------------------- planform: constrained sketch (8 lines, 8 tangent arcs; chart mm)
SP = np.array([[(CB + s_ * uB + y_ * vB - 2.8 * axB) for y_ in Y_SCREW] for s_ in S_SCREW]).reshape(-1, 3)
sxy = to_xy(SP); s_c = float(sxy[:, 1].mean()); HS = 40.4                                # spine half-length (screws +-30, head 4.5, 6 margin)
print(f"screws: s {sxy[:, 1].min():.1f}..{sxy[:, 1].max():.1f} (centre {s_c:.1f}), theta {np.degrees(sxy[:, 0] / R0).min():.1f}..{np.degrees(sxy[:, 0] / R0).max():.1f} deg", flush=True)
TH_A, TH_P = -20.0, 62.0                                         # saddle: everything beyond stays >= 1 mm off the body in every frame (out_cuff/trunkmap.npz); the knit band wraps the rest
SKETCH = [  # (x, y, fillet radius): 5 lines + 5 tangent arcs; elbow side slants (posterior half) to clear the trunk at the posterior corner
    (X(TH_A), s_c + HS, 12.0), (X(TH_A), s_c - HS, 12.0), (X(TH_P), s_c - HS + 6.0, 12.0), (X(TH_P), s_c + HS - 18.0, 12.0), (X(16.0), s_c + HS, 30.0)]
def sketch_outline(V, n=440):
    """closed polyline with tangent fillet arcs at every vertex -> n points equally spaced along it (CCW)"""
    P = np.array([v[:2] for v in V], float); R = [v[2] for v in V]; m = len(P); segs = []
    if 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]) < 0: P = P[::-1]; R = R[::-1]
    T = []
    for i in range(m):
        a_, b_, c_ = P[i - 1], P[i], P[(i + 1) % m]; d1 = (b_ - a_) / np.linalg.norm(b_ - a_); d2 = (c_ - b_) / np.linalg.norm(c_ - b_)
        turn = math.acos(np.clip(d1 @ d2, -1, 1)); t = R[i] * math.tan(turn / 2); nrm = np.array([-d1[1], d1[0]]) * np.sign(d1[0] * d2[1] - d1[1] * d2[0])
        T.append((b_ - t * d1, b_ + t * d2, b_ - t * d1 + R[i] * nrm, R[i]))
    pts = []
    for i in range(m):
        p0, p1, cen, r = T[i]; a0 = math.atan2(*(p0 - cen)[::-1]); a1 = math.atan2(*(p1 - cen)[::-1])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi; k = max(4, int(abs(da) * r / 0.2))
        pts += [cen + r * np.array([math.cos(a0 + da * j / k), math.sin(a0 + da * j / k)]) for j in range(k)]
        q0 = p1; q1 = T[(i + 1) % m][0]; L = np.linalg.norm(q1 - q0); k = max(2, int(L / 0.2))
        assert (q1 - q0) @ (P[(i + 1) % m] - P[i]) > 0, f"fillets overlap on edge {i}"
        pts += [q0 + (q1 - q0) * j / k for j in range(k)]
    pts = np.array(pts); sl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(np.r_[pts, pts[:1]], axis=0), axis=1))]
    us = np.linspace(0, sl[-1], n, endpoint=False); return np.c_[np.interp(us, sl, np.r_[pts[:, 0], pts[0, 0]]), np.interp(us, sl, np.r_[pts[:, 1], pts[0, 1]])]
QS = sketch_outline(SKETCH)
from matplotlib.path import Path as _Path
_poly = _Path(QS)
def inside(x, y): return _poly.contains_points(np.c_[np.ravel(x), np.ravel(y)]).reshape(np.shape(x))
def edge_dist(x, y):
    from scipy.spatial import cKDTree
    return cKDTree(QS).query(np.c_[np.ravel(x), np.ravel(y)])[0].reshape(np.shape(x))
d_sc = edge_dist(sxy[:, 0], sxy[:, 1]); assert inside(sxy[:, 0], sxy[:, 1]).all() and d_sc.min() > 4.5 + 3.5, f"screw too close to the edge ({d_sc.min():.1f})"
print(f"sketch: perimeter {np.sum(np.linalg.norm(np.diff(np.r_[QS, QS[:1]], axis=0), axis=1)):.0f} mm, screw heads >= {d_sc.min() - 4.5:.1f} mm from the edge", flush=True)

# ---------------------------------------------------------------- fair inner surface: stiffest-smooth shrink-wrap over the envelope
HG = 1.5; gx = np.arange(QS[:, 0].min() - 9, QS[:, 0].max() + 9, HG); gy = np.arange(QS[:, 1].min() - 9, QS[:, 1].max() + 9, HG)
GX, GY = np.meshgrid(gx, gy, indexing="ij"); nx_, ny_ = GX.shape
LB = f_lb.ev(GX.ravel(), GY.ravel()).reshape(GX.shape) + LINER_MIN
WL = land_w(GX, GY); RPL = r_plane(GX, GY)
inn = inside(GX, GY) | (edge_dist(GX, GY) < EDGE + 2.0)
def fair_solve(lam=LAM, a0=0.02, iters=14):
    from scipy.sparse import diags, kron, identity, csr_matrix
    from scipy.sparse.linalg import spsolve
    def d2(n):
        D = diags([np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1]).tolil(); D[0, 0] = D[-1, -1] = -1; return D.tocsr() / HG ** 2
    Lp = kron(d2(nx_), identity(ny_)) + kron(identity(nx_), d2(ny_)); B = lam * (Lp.T @ Lp)
    land = (WL > 0.98) & inn; tgt = np.where(land, RPL - T_LAND, LB).ravel()
    wgt = np.where(inn, a0, 0.0).ravel(); wgt[land.ravel()] = 1e4; act = np.zeros(nx_ * ny_, bool)
    for k in range(iters):
        W = wgt.copy(); W[act] = 1e4; t_ = tgt.copy(); t_[act] = LB.ravel()[act] + 0.05
        u = spsolve((B + diags(W)).tocsc(), W * t_)
        viol = inn.ravel() & (u < LB.ravel() - 0.01)
        if not viol.any(): break
        act |= viol
    return u.reshape(GX.shape), k, int(act.sum())
U, it_, nact = fair_solve()
U = WL * (RPL - T_LAND) + (1 - WL) * U                                                    # the land exact
gap = (U - (LB - LINER_MIN))[inside(GX, GY)]
print(f"fair inner surface: {it_ + 1} active-set passes, {nact} contact nodes; liner gap (to the swept skin) min {gap.min():.2f}, median {np.median(gap):.1f}, p90 {np.percentile(gap, 90):.1f} mm", flush=True)
f_U = RectBivariateSpline(gx, gy, U, kx=3, ky=3, s=0)
def r_in(x, y): return f_U.ev(np.ravel(x), np.ravel(y)).reshape(np.shape(x))
def r_out(x, y): return r_in(x, y) + T_SHELL + (T_LAND - T_SHELL) * land_w(x, y)
fo = RectBivariateSpline(np.radians(TH) * R0, SS, np.where(np.isfinite(Rfo), Rfo, 999.0), kx=1, ky=1, s=0)
ins_ = inside(GX, GY); cl = fo.ev(GX.ravel(), GY.ravel()).reshape(GX.shape) - r_out(GX, GY)
print(f"clearance to the forearm / forearm cuff (any frame) under the outline: min {cl[ins_].min():.1f} mm", flush=True)

# ---------------------------------------------------------------- the shell (cylindrical-chart version of sheet_solid)
def surface(fr, x0, x1, y0, y1, h=0.8):
    xs = np.linspace(x0, x1, int(math.ceil((x1 - x0) / h)) + 1); ys = np.linspace(y0, y1, int(math.ceil((y1 - y0) / h)) + 1)
    X, Y = np.meshgrid(xs, ys, indexing="ij"); P = cyl(X, Y, fr(X, Y))
    fits = [RectBivariateSpline(xs, ys, P[..., k], kx=3, ky=3, s=0) for k in range(3)]
    tx, ty = fits[0].tck[0], fits[0].tck[1]; nx, ny = len(tx) - 4, len(ty) - 4; C = np.stack([f.tck[2].reshape(nx, ny) for f in fits], -1)
    poles = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(nx):
        for j in range(ny): poles.SetValue(i + 1, j + 1, gp_Pnt(*map(float, C[i, j])))
    uk, um = SH._knots(tx); vk, vm = SH._knots(ty)
    return Geom_BSplineSurface(poles, uk, vk, um, vm, 3, 3, False, False)

def shell_solid(e=EDGE, n=420):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    from OCP.BRepLib import BRepLib
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopoDS import TopoDS
    from OCP.ShapeFix import ShapeFix_Solid, ShapeFix_Face
    from OCP.GeomAbs import GeomAbs_C2
    Q = QS.copy(); n = len(Q)
    pad = e + 3.0; x0, x1 = Q[:, 0].min() - pad, Q[:, 0].max() + pad; y0, y1 = Q[:, 1].min() - pad, Q[:, 1].max() + pad
    SB = surface(r_in, x0, x1, y0, y1); ST = surface(r_out, x0, x1, y0, y1)
    Bp, Tp, NB, NT = [], [], [], []
    for x, y in Q:
        pb, nb, _ = SH._eval(SB, x, y); pt, nt, _ = SH._eval(ST, x, y); Bp.append(pb); Tp.append(pt); NB.append(nb); NT.append(nt)
    Bp, Tp, NB, NT = map(np.array, (Bp, Tp, NB, NT)); unit = SH.unit
    up = unit(Tp - Bp); NB = NB * np.sign((NB * up).sum(1))[:, None]; NT = NT * np.sign((NT * up).sum(1))[:, None]
    TB = unit(np.roll(Bp, -1, 0) - np.roll(Bp, 1, 0)); TT = unit(np.roll(Tp, -1, 0) - np.roll(Tp, 1, 0)); YB = unit(np.cross(TB, NB)); YT = unit(np.cross(TT, NT))
    for Y_, P_ in ((YB, Bp), (YT, Tp)):
        xo = to_xy(P_ + 0.3 * Y_); Y_ *= np.where(inside(xo[:, 0], xo[:, 1]), -1.0, 1.0)[:, None]
    Wb = Bp + e * YB + e * NB; Wt = Tp + e * YT - e * NT; th = np.linalg.norm(Wt - Wb, axis=1)
    if th.min() < 0.2: raise ValueError(f"shell too thin for the edge round: wall {th.min():.2f} mm")
    WD = unit(Wt - Wb); C1, C2 = [], []
    for i in range(n):
        C1.append(G.g2_blend(Bp[i], YB[i], 0.0, NB[i], Wb[i], WD[i], 0.0, -YB[i])); C2.append(G.g2_blend(Wt[i], WD[i], 0.0, -YT[i], Tp[i], -YT[i], 0.0, -NT[i]))
    C1, C2 = np.array(C1), np.array(C2); Wl = np.stack([Wb, Wt], 1)
    faces = [BRepBuilderAPI_MakeFace(G._row_surface([arr[:, k] for k in range(arr.shape[1])], deg), 1e-7).Face() for arr, deg in ((C1, 5), (Wl, 1), (C2, 5))]
    def trimmed(S):
        c2 = SH.pcurve(Q); ed = BRepBuilderAPI_MakeEdge(c2, S).Edge(); BRepLib.BuildCurves3d_s(ed, 1e-6, GeomAbs_C2, 9, 2 * len(Q))
        w = BRepBuilderAPI_MakeWire(ed).Wire(); f = BRepBuilderAPI_MakeFace(S, w, True).Face(); sf = ShapeFix_Face(f); sf.Perform(); return sf.Face()
    sew = BRepBuilderAPI_Sewing(5e-3)
    for f in faces + [trimmed(SB), trimmed(ST)]: sew.Add(f)
    sew.Perform(); sh = sew.SewedShape(); exs = TopExp_Explorer(sh, TopAbs_SHELL)
    so = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(exs.Current())).Solid(); fx = ShapeFix_Solid(so); fx.Perform(); so = fx.Solid()
    s = cq.Solid(so)
    if s.Volume() < 0: s = cq.Solid(so.Reversed())
    return s, Q, (float(th.min()), float(np.linalg.norm(Tp - Bp, axis=1).min()), float(np.linalg.norm(Tp - Bp, axis=1).max()))

def m4_cs(p_face, ax, L=6.0):
    """ISO 10642 M4 x L, head top flush with the land's inner face: p_face = point on BOTTOM's skin plane, ax = axB"""
    top = -T_LAND                                                                     # head top (axial, from the bar face)
    prof = [("line", (0, top), (4.48, top)), ("line", (4.48, top), (2.0, top + 2.48)), ("line", (2.0, top + 2.48), (2.0, top + L)),
            ("line", (2.0, top + L), (0, top + L)), ("line", (0, top + L), (0, top))]
    return G.revolve_profile(prof, ax).moved(cq.Location(cq.Vector(*map(float, p_face))))
def m4_seat(p_face, ax):
    """countersink + clearance through the land, opened past the inner face (tool)"""
    top = -T_LAND
    prof = [("line", (0, top - 3.0), (5.2, top - 3.0)), ("line", (5.2, top - 3.0), (5.2, top)), ("line", (5.2, top), (4.55, top)), ("line", (4.55, top), (2.15, top + 2.40)),
            ("line", (2.15, top + 2.40), (2.15, 1.0)), ("line", (2.15, 1.0), (0, 1.0)), ("line", (0, 1.0), (0, top - 3.0))]
    return G.revolve_profile(prof, ax).moved(cq.Location(cq.Vector(*map(float, p_face))))

if __name__ == "__main__":
    import time; t0 = time.time()
    body, Q, th = shell_solid(); print(f"shell: valid {body.isValid()}, faces {len(body.Faces())}, edge wall >= {th[0]:.2f}, thickness {th[1]:.2f}..{th[2]:.2f} mm, {time.time() - t0:.0f}s", flush=True)
    screws = []
    for p in SP:
        tool = m4_seat(p, axB); b2 = body.cut(tool)
        if not b2.isValid():
            from OCP.ShapeFix import ShapeFix_Shape
            sf = ShapeFix_Shape(b2.wrapped); sf.Perform(); b2 = cq.Shape.cast(sf.Shape())
        body = b2; screws.append(m4_cs(p, axB))
    print(f"cuff with 6 countersinks: valid {body.isValid()}, faces {len(body.Faces())}", flush=True)
    vs, fs = body.tessellate(0.05, 0.2); V = np.array([[v.x, v.y, v.z] for v in vs]); F = np.array(fs)
    import trimesh; m = trimesh.Trimesh(V, F); m.merge_vertices()
    vol = abs(m.volume); print(f"mesh: watertight {m.is_watertight}, volume {vol / 1000:.2f} cm3 -> {vol * 2.67e-3:.1f} g AlSi10Mg", flush=True)
    cq.exporters.export(cq.Workplane().add(body), os.path.join(FX, "upper_cuff_fair.step"))
    sc = trimesh.Scene(); sc.add_geometry(m, node_name="cuff"); sc.export(os.path.join(HERE, "out_cuff", "cuff.glb"))
    for k, s_ in enumerate(screws): cq.exporters.export(cq.Workplane().add(s_), os.path.join(HERE, "out_cuff", f"screw_{k}.step"))
    q = cyl(Q[:, 0], Q[:, 1], r_out(Q[:, 0], Q[:, 1])); ext = q @ a
    rep = dict(volume_cm3=vol / 1000, mass_g=vol * 2.67e-3, length_spine=float(2 * HS), s_range=[float(ext.min()), float(ext.max())],
               theta=[TH_A, TH_P], liner_min=LINER_MIN, shell=T_SHELL, land=T_LAND, edge=EDGE)
    json.dump(rep, open(os.path.join(HERE, "out_cuff", "report.json"), "w"), indent=1); print(json.dumps(rep), f"{time.time() - t0:.0f}s")
