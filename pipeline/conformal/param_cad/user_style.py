"""Parametric CAD of a searched spherical 3R in the user's design style (their SHOULDER LINK OUTER / INNER parts).

The user's links are a 12 x 3 bar bent on one arc about the sphere centre, flat round pads at the pivots (axes normal to
the bar), a 1 mm pocket on the outer face and 0.5 mm edge rounds: a sketch extruded to width, a few features, nothing
lofted. Every custom part here is built the same way:

  bar    - the side view is a sketch of tangent lines and arcs with set radii (sketch2d.py) in the plane of the two joint
           axes (a great-circle plane through GH), offset to the bar thickness and extruded symmetric to the bar width.
           The arcs are fitted once to the skin clearance field (fair_cad/envelope.py: dense skin maps, 2 mm clearance,
           every followed frame of the fit clips; held-out clips never shape the CAD) with the ramp <= 35 deg (rule 4),
           then their radii are rounded and the lengths solved exactly - the field is never interpolated into a surface.
  pads   - at every joint a flat plate in the seat plane: the O20 hub circle and the bar joined by tangent R6 arcs (a
           planform sketch extruded to the seat thickness). The bar leaves the pad parallel to the seat (rule 4) and is
           glued to it on an exactly shared end face (rule 5: OCC glue fuse, then same-domain faces unified).
  hubs   - solids of revolution about the exact joint axes (all three meet at GH): lower pad + integral O7 pin, upper
           ring + M18 spigot, bore cut through it; bearings, spacers, nut, cap as in the v5 stack (param_build.py).
  pocket - 1 mm deep on the outer face of every bar, 1.5 mm rims, round ends (as the user's links).
  rounds - 0.5 mm on every sharp edge of the bars and pads; tangent edges are left alone.

Arm end: a folded plate. The J3 pad plane (normal = J3 axis) and BOTTOM's channel plane (normal = the bar's up) are 22
deg apart about a line along the arm, so the bracket is the pad plate, one bend about that line and a tongue in BOTTOM's
channel held by two flush M3 countersunk screws through the web (BOTTOM is the one user part we may cut).

    python3 user_style.py [key=r20_n3_s1414_4] [J2=<face mm>]  -> pipeline/full-exo/designs/param2_<key>[_j2<F>]/
"""
import json, math, os, sys, time
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ARGS = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a); sys.argv = sys.argv[:1] + [ARGS.get("key", "r20_n3_s1414_4")]
import param_build as PB                                                                  # noqa: E402  (v5 stack, frames, export)
import sketch2d as SK                                                                     # noqa: E402
sys.path.insert(0, os.path.join(PB.CONF)); import cad_helpers as CH                       # noqa: E402
from scipy.interpolate import RegularGridInterpolator                                    # noqa: E402
FR, AE, LV, unit, V, xform = PB.FR, PB.AE, PB.LV, PB.unit, PB.V, PB.xform
KEY = PB.KEY; HUB_R, T, W = PB.HUB_R, PB.T, PB.W
RF, L_SEAT, ROUND, CLIMB, N_ARCS = 6.0, 14.0, 0.5, 35.0, 5                               # pad fillet, flat seat length, edge round, ramp limit, arcs per bar
FIT_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".cache", "user_style_fits.json")
POCKET = dict(depth=1.0, rim=1.5, end=4.0)                                                # outer-face pocket (user's links: 1 mm, rims, round ends)
J2_FACE = float(ARGS["J2"]) if "J2" in ARGS else None
OUT = os.path.join(FR.FULL, "designs", f"param2_{KEY}" + (f"_j2{J2_FACE:g}" if J2_FACE else ""))


# ---------------------------------------------------------------- features
def plate(k, level, sdir, w, t=T, L=L_SEAT, R=HUB_R, rf=RF):
    """flat pad in the seat plane of axis k: hub circle R + a bar of width w out to L along sdir, joined by tangent rf
    arcs; occupies levels level..level+t above GH along k"""
    k = unit(k); sdir = unit(sdir - (sdir @ k) * k); h = w / 2
    xc = math.sqrt((R + rf) ** 2 - (h + rf) ** 2); assert L > xc + 0.5, (L, xc)
    def fillet_pts(sg):                                                                    # concave arc from the bar edge to the hub circle
        c = np.array([xc, sg * (h + rf)]); a = np.array([xc, sg * h]); b = R * unit(c)
        m = c + rf * unit(unit(a - c) + unit(b - c)); return a, m, b
    a1, m1, b1 = fillet_pts(+1); a2, m2, b2 = fillet_pts(-1)
    pl = cq.Plane(origin=tuple(map(float, level * k)), xDir=tuple(map(float, sdir)), normal=tuple(map(float, k)))
    wp = (cq.Workplane(pl).moveTo(L, h).lineTo(*a1).threePointArc(tuple(m1), tuple(b1)).threePointArc((-R, 0.0), tuple(b2))
          .threePointArc(tuple(m2), tuple(a2)).lineTo(L, -h).close())
    return wp.extrude(t).val()


def bar(ex, ey, start, segs, t=T, w=W, origin=(0.0, 0.0, 0.0)):
    """bent bar: the sketch chain offset to thickness t in the plane (origin, ex, ey), extruded symmetric to width w"""
    nP = unit(np.cross(ex, ey)); pl = cq.Plane(origin=tuple(map(float, origin)), xDir=tuple(map(float, ex)), normal=tuple(map(float, nP)))
    out = SK.offset_outline(start, segs, t); wp = cq.Workplane(pl).moveTo(*out[0][1])
    for s in out:
        wp = wp.lineTo(*s[2]) if s[0] == "line" else wp.threePointArc(tuple(s[2]), tuple(s[3]))
    return wp.close().extrude(w / 2, both=True).val()


def rrect(c, u, v, a, b, r=ROUND):
    """closed wire: rectangle centred c, half sizes a along u and b along v, corners rounded r"""
    c, u, v = (np.asarray(x, float) for x in (c, u, v)); r = min(r, a - 1e-3, b - 1e-3); q = r * (1 - math.sqrt(0.5))
    P = lambda x, y: V(c + x * u + y * v)
    E = [cq.Edge.makeLine(P(a, -b + r), P(a, b - r)), cq.Edge.makeThreePointArc(P(a, b - r), P(a - q, b - q), P(a - r, b)),
         cq.Edge.makeLine(P(a - r, b), P(-a + r, b)), cq.Edge.makeThreePointArc(P(-a + r, b), P(-a + q, b - q), P(-a, b - r)),
         cq.Edge.makeLine(P(-a, b - r), P(-a, -b + r)), cq.Edge.makeThreePointArc(P(-a, -b + r), P(-a + q, -b + q), P(-a + r, -b)),
         cq.Edge.makeLine(P(-a + r, -b), P(a - r, -b)), cq.Edge.makeThreePointArc(P(a - r, -b), P(a - q, -b + q), P(a, -b + r))]
    return cq.Wire.assembleEdges(E)


def bar_swept(ex, ey, start, segs, t=T, w=W, origin=(0.0, 0.0, 0.0), r=ROUND, flat=False):
    """the bar as a constant rounded-rectangle section swept along the sketch chain (lines + tangent arcs) in the plane
    (origin, ex, ey), binormal fixed to the plane normal. flat=False: thickness t in the plane (a bent bar), width w
    across; flat=True: width w in the plane, thickness t across (a planform strap)"""
    ex, ey = np.asarray(ex, float), np.asarray(ey, float); nP = unit(np.cross(ex, ey)); o = np.asarray(origin, float)
    m2 = lambda p: V(o + p[0] * ex + p[1] * ey)
    E = []; x, y, ps = start
    for k, l in segs:
        x1, y1, p1 = SK.advance(x, y, ps, k, l)
        if abs(k) < 1e-12: E.append(cq.Edge.makeLine(m2((x, y)), m2((x1, y1))))
        else:
            xm, ym, _ = SK.advance(x, y, ps, k, l / 2); E.append(cq.Edge.makeThreePointArc(m2((x, y)), m2((xm, ym)), m2((x1, y1))))
        x, y, ps = x1, y1, p1
    path = cq.Wire.assembleEdges(E); x, y, ps = start
    c0 = o + x * ex + y * ey; N0 = math.sin(ps) * ex - math.cos(ps) * ey
    sec = rrect(c0, N0, nP, t / 2, w / 2, r) if not flat else rrect(c0, N0, nP, w / 2, t / 2, r)
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
    from OCP.gp import gp_Dir
    mk = BRepOffsetAPI_MakePipeShell(path.wrapped); mk.SetMode(gp_Dir(*map(float, nP)))      # fixed binormal = the sketch plane normal
    mk.Add(sec.wrapped, False, False); mk.Build(); mk.MakeSolid()
    return cq.Shape.cast(mk.Shape())


def edges_on_plane(s, p0, n, tol=1e-3):
    n = unit(n); return [e for e in s.Edges() if abs((np.array(e.positionAt(0.5).toTuple()) - p0) @ n) < tol
                         and abs((np.array(e.positionAt(0.0).toTuple()) - p0) @ n) < tol]


def rounded(s, keep_plane=None, skip=lambda e: False, r=ROUND):
    """0.5 mm rounds on every non-tangent edge except those lying in keep_plane (p0, n) - a face another body is glued to"""
    excl = set()
    if keep_plane is not None: excl = {e.hashCode() for e in edges_on_plane(s, *keep_plane)}
    E = [e for e in tangent_edges_free(s) if e.hashCode() not in excl and not skip(e)]
    out, nr, nf = round_edges(s, r=r, edges=E)
    return out


def upper_ring_r(k, F, r=ROUND):
    """O20 ring + M18 spigot above the upper pad, outer top corners rounded in the profile (revolve about k)"""
    z0, h1, sp = LV["U0"] + T + F, LV["H1"] + F, LV["SPIG"] + F; q = 1 - math.sqrt(0.5); r2 = 0.3
    wp = (cq.Workplane("XZ").moveTo(4.0, z0).lineTo(HUB_R, z0).lineTo(HUB_R, h1 - r)
          .threePointArc((HUB_R - r * q, h1 - r * q), (HUB_R - r, h1)).lineTo(9.0, h1).lineTo(9.0, sp - r2)
          .threePointArc((9.0 - r2 * q, sp - r2 * q), (9.0 - r2, sp)).lineTo(4.0, sp).close())
    return xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(k))


def plate_r(k, level, sdir, w, t=T, L=L_SEAT, upper=False):
    """planform pad with 0.5 mm rounds, except on its end face (the bar is glued there) and, for an upper pad, the top
    edge of the hub circle (the ring continues that cylinder)"""
    s = plate(k, level, sdir, w, t, L); k = unit(k); sd = unit(sdir - (sdir @ k) * k)
    top = (level + t) * k
    def skip(e):
        if not upper or e.geomType() != "CIRCLE": return False
        p = np.array(e.positionAt(0.5).toTuple()); return abs((p - top) @ k) < 1e-3 and abs(np.linalg.norm(p - (p @ k) * k) - HUB_R) < 1e-3
    return rounded(s, keep_plane=(level * k + L * sd, sd), skip=skip)


def terminal_r(o_mid, n, sdir, w, L, t=T):
    s = terminal(o_mid, n, sdir, w, L, t); n_ = unit(n); sd = unit(sdir - (sdir @ n_) * n_)
    return rounded(s, keep_plane=(np.asarray(o_mid, float), sd))


def ring_root_fillet(s, k, F, r=1.0):
    """try a concave round where the ring rises from the pad top (strip side); returns s unchanged if the kernel refuses"""
    k = unit(k); z = F + LV["U0"] + T
    E = [e for e in s.Edges() if e.geomType() == "CIRCLE" and abs(np.array(e.positionAt(0.5).toTuple()) @ k - z) < 1e-3
         and abs(np.linalg.norm((lambda p: p - (p @ k) * k)(np.array(e.positionAt(0.5).toTuple()))) - HUB_R) < 1e-3]
    if not E: return s
    out, nr, nf = round_edges(s, r=r, edges=E); return out


def pocket_cutter(ex, ey, start, segs, s0, s1, t=T, w=W, depth=POCKET["depth"], rim=POCKET["rim"]):
    """the pocket tool: the chain between arc lengths s0..s1, a band from (t/2 - depth) to (t/2 + 1) on the outer side,
    extruded to the pocket width; its ends are rounded afterwards by filleting the solid's pocket corners"""
    sub = []; acc = 0.0; x, y, p = start; st = None
    for k, l in segs:
        a, b = max(acc, s0), min(acc + l, s1)
        if b > a:
            if st is None: st = SK.advance(x, y, p, k, a - acc)
            sub.append((k, b - a))
        x, y, p = SK.advance(x, y, p, k, l); acc += l
    off = t / 2 - depth / 2 + 0.5                                                          # band centre (outer side)
    xs, ys, ps = st; nb = np.array([math.sin(ps), -math.cos(ps)])
    st2 = (xs + off * nb[0], ys + off * nb[1], ps)                                        # the offset chain: same angles, radii + off
    segs2 = [(0.0 if abs(k) < 1e-12 else 1.0 / (1.0 / k + off), l * (1.0 + off * k)) for k, l in sub]
    tool = bar(ex, ey, st2, segs2, t=depth + 1.0, w=w - 2 * rim)
    rp = (w - 2 * rim) / 2                                                                 # round ends: a cylinder at each end, axis along the face normal
    for (x0, y0, p0) in (st, SK.end_pose(st, sub)):
        n2 = np.array([math.sin(p0), -math.cos(p0)]); c2 = np.array([x0, y0]) + (t / 2 - depth) * n2
        c3 = c2[0] * ex + c2[1] * ey; n3 = n2[0] * ex + n2[1] * ey
        tool = tool.fuse(cq.Solid.makeCylinder(rp, depth + 1.0, V(c3), V(n3)))
    return tool.clean()


def tangent_edges_free(s, angle_deg=1.0):
    """edges of s whose two faces meet at an angle (not tangent): the edges to round"""
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.BRep import BRep_Tool
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.ShapeAnalysis import ShapeAnalysis_Surface
    from OCP.gp import gp_Pnt
    M = TopTools_IndexedDataMapOfShapeListOfShape(); TopExp.MapShapesAndAncestors_s(s.wrapped, TopAbs_EDGE, TopAbs_FACE, M)
    out = []
    for e in s.Edges():
        i = M.FindIndex(e.wrapped)
        if i == 0: continue
        fl = M.FindFromIndex(i)
        if fl.Size() != 2: continue
        fs = [cq.Face(f) for f in fl]; p = e.positionAt(0.5)
        ns = []
        for f in fs:
            n = f.normalAt(p); ns.append(np.array(n.toTuple()))
        if np.degrees(np.arccos(np.clip(ns[0] @ ns[1], -1, 1))) > angle_deg: out.append(e)
    return out


def round_edges(s, r=ROUND, edges=None):
    """fillet the given (default: all non-tangent) edges; edges the kernel refuses are dropped one by one"""
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    E = tangent_edges_free(s) if edges is None else edges
    def attempt(es):
        mk = BRepFilletAPI_MakeFillet(s.wrapped)
        for e in es: mk.Add(r, e.wrapped)
        try:
            mk.Build()
            if not mk.IsDone(): return None
            out = cq.Shape.cast(mk.Shape()); return out if out.isValid() else None
        except Exception: return None
    got = attempt(E)
    if got is not None: return got, len(E), 0
    keep = []
    for e in E:
        if attempt(keep + [e]) is not None: keep.append(e)
    return (attempt(keep) if keep else s), len(keep), len(E) - len(keep)


def glue(a, b):
    """fuse of two solids that touch on shared faces: OCC glue (shift, then full), else a plain fuse; same-domain faces
    are unified when the result stays valid (unifying a hub circle face with a full ring cylinder can break it)"""
    for f in (lambda: a.fuse(b).clean(), lambda: a.fuse(b), lambda: CH.glue_fuse(a, b, shift=False), lambda: CH.glue_fuse(a, b)):
        try: g = f()
        except Exception: g = None
        if g is not None and g.isValid() and len(g.Solids()) == 1: return g
    raise RuntimeError("glue: no valid single solid")


def lower_pin(k, F):
    """collar O8.2 + integral O7 pin, embedded 1.5 mm into the lower pad (fuses transversally)"""
    return PB.revolved([(0, 1.5), (4.1, 1.5), (4.1, LV["L1"]), (3.5, LV["L1"]), (3.5, LV["N1"]), (0, LV["N1"])], k, F)


def upper_ring(k, F):
    """O20 ring + M18 spigot on top of the upper pad (glued on the pad's top face); inner wall left for the bore cut"""
    z0 = LV["U0"] + T
    return PB.revolved([(4.0, z0), (HUB_R, z0), (HUB_R, LV["H1"]), (9.0, LV["H1"]), (9.0, LV["SPIG"]), (4.0, LV["SPIG"])], k, F)


def bore_cutter(k, F):
    return PB.revolved([(0, LV["U0"] - 1.0), (4.9, LV["U0"] - 1.0), (4.9, LV["L1"]), (5.5, LV["L1"]), (5.5, LV["SPIG"] + 1.0),
                        (0, LV["SPIG"] + 1.0)], k, F)


def hardware(J, k, F, lower, upper):
    """bearings, spacers, nut, cap of the v5 stack (param_build.joint_parts without its pad and boss)"""
    return [p for p in PB.joint_parts(J, k, F, lower, upper) if not (" pad + " in p[1] or " boss " in p[1])]


# ---------------------------------------------------------------- clearance field in a great-circle plane
class PolarField:
    """clearance (mm, >= 0 = metal clear of skin + 2 mm) of points of the plane (GH, ex, ey), min over the bar width"""
    def __init__(self, E, group, Rg, ex, ey, th_lo, th_hi, w, r_lo=35.0, r_hi=150.0):
        nP = unit(np.cross(ex, ey)); self.ex, self.ey = ex, ey
        th = np.radians(np.arange(th_lo, th_hi + 0.25, 0.25)); r = np.arange(r_lo, r_hi + 1.0, 1.0)
        TH, RR = np.meshgrid(th, r, indexing="ij"); cl = np.full(TH.shape, np.inf)
        for c in np.linspace(-w / 2, w / 2, 5):
            P = (RR * np.cos(TH))[..., None] * ex + (RR * np.sin(TH))[..., None] * ey + c * nP
            D = (P.reshape(-1, 3) @ Rg); nrm = np.linalg.norm(D, axis=1)
            need = E.min_radius(group, D / nrm[:, None]).reshape(TH.shape)
            cl = np.minimum(cl, nrm.reshape(TH.shape) - need)
        self.f = RegularGridInterpolator((th, r), cl, bounds_error=False, fill_value=None)
    def __call__(self, U):
        return self.f(np.stack([np.arctan2(U[:, 1], U[:, 0]), np.hypot(U[:, 0], U[:, 1])], 1))


def link_chain(E, group, Rg, ka, ha, kb, hb, w=W, t=T, la=L_SEAT, lb=L_SEAT, label=""):
    """fit the bar between the seat of axis ka (centre-line height ha) and the seat of axis kb (height hb), in the plane
    of the two axes. Returns (ex, ey, start, segs, info)."""
    ex = unit(ka); ey = unit(kb - (kb @ ex) * ex); phi = math.acos(np.clip(unit(kb) @ ex, -1, 1))
    start = (ha, la, math.pi / 2)
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    end = (*(B + lb * back), math.pi / 2 + phi)
    key = f"v2|{label}|{group}|{np.round(ka, 5).tolist()}|{ha:.3f}|{np.round(kb, 5).tolist()}|{hb:.3f}|{w}|{t}|{la}|{lb}|{N_ARCS}|{CLIMB}"
    cache = json.load(open(FIT_CACHE)) if os.path.exists(FIT_CACHE) else {}
    if key in cache: fit = cache[key]; fit["segs"] = [tuple(x) for x in fit["segs"]]
    else:
        fld = PolarField(E, group, Rg, ex, ey, -5.0, math.degrees(phi) + 5.0, w)
        fits = {}                                                                         # parsimony: the fewest arcs within 1 mm
        for n_ in range(3, N_ARCS + 1):                                                   # of the best mean clearance
            try: fits[n_] = SK.fit_chain(start, end, fld, t, n_arcs=n_, climb_max=CLIMB)
            except RuntimeError as e: print(f"  {label}: {n_} arcs: {e}")
        bm = min(f_["mean_clear"] for f_ in fits.values())
        n_best = min(n_ for n_, f_ in fits.items() if f_["mean_clear"] <= bm + 1.0); fit = fits[n_best]
        print(f"  {label}: mean clearance by arc count {[(n_, round(f_['mean_clear'], 2)) for n_, f_ in fits.items()]} -> {n_best} arcs")
        fit = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in fit.items()}
        fit["segs"] = [(float(k), float(l)) for k, l in fit["segs"]]; fit["radii"] = [None if r is None else float(r) for r in fit["radii"]]
        cache[key] = fit; os.makedirs(os.path.dirname(FIT_CACHE), exist_ok=True); json.dump(cache, open(FIT_CACHE, "w"), indent=0)
    print(f"{label}: arc {math.degrees(phi):.1f} deg, radii {[None if r is None else round(r, 1) for r in fit['radii']]}, "
          f"lengths {[round(l, 1) for _, l in fit['segs']]}, skin-side clearance min {fit['min_clear']:.2f} mean {fit['mean_clear']:.2f} "
          f"max {fit['max_clear']:.2f} mm, max climb {fit['max_climb']:.1f} deg")
    return ex, ey, start, fit["segs"], dict(arc_deg=math.degrees(phi), **{k: v for k, v in fit.items() if k != "segs"},
                                            segs=[(float(k), float(l)) for k, l in fit["segs"]])


def with_pocket(body, ex, ey, start, segs):
    total = sum(l for _, l in segs); s0, s1 = POCKET["end"], total - POCKET["end"]
    if s1 - s0 < 10: return body, 0
    cut = pocket_cutter(ex, ey, start, segs, s0, s1)
    b2 = body.cut(cut).clean()
    return (b2, 1) if b2.isValid() and len(b2.Solids()) == 1 else (body, 0)


def with_pocket_r(body, ex, ey, start, segs, r=0.4):
    """the outer-face pocket, then rounds on the pocket's own edges only"""
    key = lambda e: tuple(np.round(np.array(e.positionAt(0.5).toTuple()), 3))
    before = {key(e) for e in body.Edges()}
    b2, npk = with_pocket(body, ex, ey, start, segs)
    if not npk: return body, 0
    new = [e for e in tangent_edges_free(b2) if key(e) not in before]
    out, nr, nf = round_edges(b2, r=r, edges=new)
    return out, (npk if nr else 0.5)


def terminal(o_mid, n, sdir, w, L, t=T):
    """flat end pad: a bar of width w continuing L along sdir from o_mid (mid-thickness), full round end; normal n"""
    n = unit(n); sdir = unit(sdir - (sdir @ n) * n)
    pl = cq.Plane(origin=tuple(map(float, o_mid - t / 2 * n)), xDir=tuple(map(float, sdir)), normal=tuple(map(float, n)))
    return (cq.Workplane(pl).moveTo(0, w / 2).lineTo(L, w / 2).threePointArc((L + w / 2, 0.0), (L, -w / 2)).lineTo(0, -w / 2).close()
            .extrude(t).val())


def chain_end(start, segs):
    x, y, p = SK.end_pose(start, segs); return np.array([x, y]), p


# ---------------------------------------------------------------- the build
def main():
    t0 = time.time(); C, ax = FR.load(PB.BAND); E = PB.Envelope(os.path.join(FR.FULL, "designs", PB.BAND))
    import body_pose as BP
    for p, G in E.frames: G["S"] = E.RS[p]                                                  # scapula frame (= BP.scap(elev))
    ci, fi, f0 = next(FR.followed(C)); X0 = FR.frame_of(f0); X0["S"] = (BP.scap(f0["p"][1]), np.zeros(3))
    R = {g: X0[g][0] for g in ("S", "l1", "l2")}
    J1w = X0["base"][0] @ ax["J1"][1]; J2w = X0["l2"][0] @ ax["J2"][1]; J3w = X0["l2"][0] @ ax["J3"][1]
    RH, tH = X0["H"]; HR = AE.HR
    fc = PB.INP["faces"]; F = {"J1": float(fc["1"]), "J2": float(fc["2"]), "J3": float(fc.get("zj4", fc["3"]))}
    F["J1"] = max(F["J1"], PB.disc_face(E, "l1", R["l1"].T @ J1w, F["J1"]))
    if J2_FACE: F["J2"] = J2_FACE
    F["J2"] = max(F["J2"], PB.disc_face(E, "l1", R["l1"].T @ J2w, F["J2"]), PB.disc_face(E, "l2", R["l2"].T @ J2w, F["J2"]))
    F["J3"] = max(F["J3"], PB.disc_face(E, "can", HR.T @ (RH.T @ J3w), F["J3"]))
    print("joint faces (mm from GH):", {j: round(v, 2) for j, v in F.items()}, "evaluator:", {k: round(v, 2) for k, v in fc.items()})
    rep = dict(faces=F, style="user (bent bars from line/arc sketches, planform pads, pocket, 0.5 mm rounds)")
    up_mid = LV["U0"] + T / 2; lo_mid = T / 2
    parts = []
    # ---- link 1 (l1): lower at J1 and J2; link 2 (l2): upper at J2 and J3
    for name, g, (ka, kb), (Fa, Fb), upper, pid in (("link 1", "l1", (J1w, J2w), (F["J1"], F["J2"]), False, "D6-02"),
                                                    ("link 2", "l2", (J2w, J3w), (F["J2"], F["J3"]), True, "D6-03")):
        z0 = LV["U0"] if upper else 0.0
        ex, ey, st, segs, info = link_chain(E, g, R[g], ka, Fa + z0 + T / 2, kb, Fb + z0 + T / 2, label=name)
        body = bar_swept(ex, ey, st, segs)
        pe, he = chain_end(st, segs)
        body = glue(plate_r(ka, Fa + z0, ey, W, upper=upper), body)
        body = glue(body, plate_r(kb, Fb + z0, -(math.cos(he) * ex + math.sin(he) * ey), W, upper=upper))
        body, npk = with_pocket_r(body, ex, ey, st, segs)
        if upper:
            for k_, F_ in ((ka, Fa), (kb, Fb)): body = ring_root_fillet(glue(body, upper_ring_r(k_, F_)), k_, F_)
            for k_, F_ in ((ka, Fa), (kb, Fb)): body = body.cut(bore_cutter(k_, F_))
        else:
            for k_, F_ in ((ka, Fa), (kb, Fb)): body = body.fuse(lower_pin(k_, F_))
        body = body.clean() if body.clean().isValid() else body
        parts.append((g, f"{pid} {name}: bent bar 8x3 + {'J2/J3 hubs' if upper else 'J1/J2 pads + integral O7 pins'} (Ti-6Al-4V)", body))
        rep[name] = dict(info, pocket=npk, valid=body.isValid(), faces=len(body.Faces()))
        print(f"  {name}: valid {body.isValid()}, solids {len(body.Solids())}, faces {len(body.Faces())}, pocket {npk}")
    # ---- scapula base (S): upper at J1 + a tab to the user's scapula handler (2x M4 counterbored). The tab heads where
    # the skin lets it sit lowest, outside link 1's sweep about J1 (computed over the followed frames)
    k1 = unit(J1w); d0 = R["S"] @ unit(np.array([0.0, 0.6, -0.8])); d0 = unit(d0 - (d0 @ k1) * k1); d1 = np.cross(k1, d0)
    th = math.radians(32); best = None
    tkey = f"tab|{np.round(k1, 5).tolist()}|{F['J1']:.3f}"; tc = json.load(open(FIT_CACHE)) if os.path.exists(FIT_CACHE) else {}
    scan = [tc[tkey]] if tkey in tc else np.arange(-130.0, 75.0, 10.0)
    for al in scan:
        td = math.cos(math.radians(al)) * d0 + math.sin(math.radians(al)) * d1
        fld = PolarField(E, "S", R["S"], k1, td, -5.0, 45.0, 16.0)
        for h in np.arange(F["J1"] + up_mid, F["J1"] + 60, 0.5):
            P0 = h * np.array([math.cos(th), math.sin(th)]); hd = np.array([-math.sin(th), math.cos(th)])
            U = np.array([P0 + s_ * hd for s_ in np.linspace(0, 26, 14)]) - (T / 2) * np.array([math.cos(th), math.sin(th)])
            if fld(U).min() >= 0.5:
                if best is None or h < best[0]: best = (h, al, td, fld)
                break
    ht, al, ey_, fld = best; ex_ = k1
    tc = json.load(open(FIT_CACHE)) if os.path.exists(FIT_CACHE) else {}; tc[tkey] = float(al); json.dump(tc, open(FIT_CACHE, "w"), indent=0)
    print(f"base tab: heading {al:.0f} deg from medial-up about J1 (link 1 sweeps 97..207), terminal height {ht:.1f} mm")
    start = (F["J1"] + up_mid, L_SEAT, math.pi / 2); end = (*(ht * np.array([math.cos(th), math.sin(th)])), th + math.pi / 2)
    fit = SK.fit_chain(start, end, fld, T, n_arcs=3, climb_max=CLIMB)
    print(f"  tab radii {[None if r is None else round(r, 1) for r in fit['radii']]}, clearance min {fit['min_clear']:.2f} mean {fit['mean_clear']:.2f}")
    body = glue(plate_r(J1w, F["J1"] + LV["U0"], ey_, 16.0, upper=True), bar_swept(ex_, ey_, start, fit["segs"], w=16.0))
    o_mid = ht * (math.cos(th) * ex_ + math.sin(th) * ey_); sd = -math.sin(th) * ex_ + math.cos(th) * ey_; nrm = unit(o_mid)
    body = glue(body, terminal_r(o_mid, nrm, sd, 16.0, 14.0))
    body = glue(body, upper_ring_r(J1w, F["J1"]))                                        # (a concave root round here segfaults OCC's filleter)
    body = body.cut(bore_cutter(J1w, F["J1"]))
    for x_ in (9.0, 17.0):                                                                 # 2x M4: O4.3 through, O7.3 x 1.2 counterbore (outer face)
        c = o_mid + x_ * sd
        body = body.cut(cq.Solid.makeCylinder(2.15, 12.0, V(c - 6 * nrm), V(nrm)))
        body = body.cut(cq.Solid.makeCylinder(3.65, 3.0, V(c + (T / 2 - 1.2) * nrm), V(nrm)))
    body = body.clean() if body.clean().isValid() else body
    parts.append(("S", "D6-01 scapula base: J1 hub + tab, 2x M4 counterbored (Ti-6Al-4V)", body))
    rep["base tab"] = dict(heading_deg=al, radii=fit["radii"], min_clear=fit["min_clear"], mean_clear=fit["mean_clear"], terminal_height=ht, valid=body.isValid())
    print(f"  base: valid {body.isValid()}, solids {len(body.Solids())}")
    # ---- arm end (H): J3 pad + planform S-strap in the pad plane + straight twist about the planes' common line + tongue
    parts_arm, rep["arm end"], holes = arm_end(E, F, J3w, X0)
    parts += parts_arm
    # ---- joint hardware (v5 stack)
    parts += hardware("J1", J1w, F["J1"], "l1", "S") + hardware("J2", J2w, F["J2"], "l1", "l2") + hardware("J3", J3w, F["J3"], "H", "l2")
    # ---- world -> group local, + the user's arm parts (BOTTOM re-cut for the tongue)
    out = []
    for g, n, s in parts:
        Rg, tg = X0[g]; out.append((g, n, xform(s, Rg.T, -Rg.T @ tg)))
    AE.S_CUT = S_CUT2; AE.LAP_HOLES = holes
    cuff_parts, rep["upper cuff"] = upper_cuff(E)
    ia = [k for k, (g, n, _) in enumerate(out) if n.startswith("D6-04")][0]
    for g, n, s in AE.user_parts():
        if n.startswith(("UPPER ARM CUFF", "M4x6 ISO 10642 countersunk (upper cuff)")): continue    # replaced by upper_cuff()
        if n.startswith("BOTTOM"):                                                        # user 2026-10-15: BOTTOM and the J3 member
            m = s.fuse(out[ia][2])                                                        # are ONE 5-axis part, not bolted
            m = m.clean() if m.clean().isValid() else m
            print(f"  BOTTOM + arm end fused: valid {m.isValid()}, solids {len(m.Solids())}, faces {len(m.Faces())}")
            out[ia] = ("H", f"D6-04 BOTTOM + arm end, one 5-axis part (user's bar cut at s {S_CUT2:g}, strap fused into its channel; 7075-T6)", m)
            continue
        out.append((g, n, s))
    out += cuff_parts
    print(f"{len(out)} parts built in {time.time() - t0:.0f} s")
    return out, rep, C


S_CUT2, NECK_W, NECK_XC, NECK_RT, NECK_RB, NECK_RHO, NECK_LIFT = 255.0, 8.0, 55.0, 12.0, 7.5, 4.5, 1.0


def arm_end(E, F, J3w, X0):
    """J3 lower member on the arm, from lines, tangent arcs and one bend only (no loft, no twist). The J3 pad plane
    (normal = the J3 axis) and BOTTOM's channel plane (normal = the bar's up) are 22 deg apart about a line d running down
    the arm. So: a flat strap in the pad plane leaves J3 straight down the arm (clear of link 2's sweep), turns 90 deg
    (R12, planform) to run posterior and crosses that common line square; one bend about it (R4.5 centreline, the
    planes' 22 deg) puts it in the channel plane; there it turns down the arm again (R7.5, planform) into a tongue in
    BOTTOM's channel, held by 2x M3 countersunk screws through BOTTOM's web. Returns ([(group, name, solid)], report,
    LAP_HOLES)."""
    RH, tH = X0["H"]; k3 = unit(J3w); F3 = F["J3"]
    up, ub = RH @ AE.axB, RH @ AE.uB
    cbar = lambda s_: RH @ (AE.CB + s_ * AE.uB) + tH                                       # bar axis point (centre plane) at station s
    d = unit(np.cross(k3, up)); d = -d if d @ ub > 0 else d                                # common line of the two planes, down the arm
    yA, yB = np.cross(k3, d), np.cross(up, d)
    OAm = F3 * k3 + T / 2 * k3                                                             # pad mid-plane at the J3 axis
    M = np.array([[1.0, k3 @ up], [k3 @ up, 1.0]]); a_, b_ = np.linalg.solve(M, [F3 + T / 2, cbar(S_CUT2) @ up + NECK_LIFT]); p0 = a_ * k3 + b_ * up
    xA = lambda p: float(d @ (p - OAm)); yf = float(yA @ (p0 - OAm))
    th = math.acos(np.clip(yA @ yB, -1, 1)); dl = NECK_RHO * math.tan(th / 2)              # bend angle, tangent length
    xc, w = NECK_XC, NECK_W
    pc = p0 + (xc - xA(p0)) * d                                                            # where the strap crosses the common line
    h1, h2 = -yA, -yB; T1 = pc - dl * h1; T2 = pc + dl * h2
    n1 = unit(h2 - (h2 @ h1) * h1)
    xcut = xA(cbar(S_CUT2))
    assert xc + NECK_RB + 2 < xcut, "neck: the channel-plane turn must sit above BOTTOM's cut end"
    # 1) pad stub (planform pad, down the arm) + strap in the pad plane: line down, R12 turn, line posterior to T1
    yT1 = float(yA @ (T1 - OAm)); L1 = (xc - NECK_RT) - L_SEAT; L3 = -NECK_RT - yT1
    assert L1 > 1 and L3 > 1, (L1, L3)
    segA = [(0.0, L1), (-1.0 / NECK_RT, NECK_RT * math.pi / 2), (0.0, L3)]
    body = glue(plate_r(k3, F3, d, w), bar_swept(d, yA, (L_SEAT, 0.0, 0.0), segA, t=T, w=w, origin=OAm, flat=True))
    pe, he = chain_end((L_SEAT, 0.0, 0.0), segA); assert abs(pe[0] - xc) < 1e-6 and abs(pe[1] - yT1) < 1e-6
    # 2) the bend about the common line: an arc in the cross-section plane, width along d
    body = glue(body, bar_swept(h1, n1, (0.0, 0.0, 0.0), [(1.0 / NECK_RHO, NECK_RHO * th)], t=T, w=w, origin=T1))
    # 3) channel plane: R7.5 turn down the arm, then the tongue with a full round end
    s_end = S_CUT2 - 19.0; xe = float(d @ (cbar(s_end) - T2))
    segB = [(1.0 / NECK_RB, NECK_RB * math.pi / 2), (0.0, xe - NECK_RB)]
    body = glue(body, bar_swept(d, yB, (0.0, 0.0, -math.pi / 2), segB, t=T, w=w, origin=T2, flat=True))
    pB, _ = chain_end((0.0, 0.0, -math.pi / 2), segB); tip = T2 + pB[0] * d + pB[1] * yB
    body = glue(body, terminal_r(tip, up, d, w, 0.001))
    body = body.fuse(lower_pin(k3, F3))
    holes = []; tline = T2 - NECK_RB * yB                                                  # the tongue's centre line
    off = float(yB @ (tline - cbar(S_CUT2)))
    assert abs(off) + w / 2 <= 14.6, f"tongue {off:+.1f} mm off the bar centre: it would stick out of BOTTOM's side"                # inside the bar's 30 mm (it fuses into web and flange)
    body = body.clean() if body.clean().isValid() else body
    rep = dict(planes_deg=math.degrees(th), common_line_behind_J3_mm=abs(yf), embedded_in_web_mm=NECK_LIFT + T / 2 - 1.5, crossing_mm_below_J3=xc, turn_pad_plane_R=NECK_RT,
               bend_R=NECK_RHO, turn_channel_plane_R=NECK_RB, tongue_offset_from_channel_centre_mm=off, bottom_cut_s=S_CUT2, holes=holes)
    print(f"arm end: planes {math.degrees(th):.1f} deg apart about a line {abs(yf):.1f} mm behind J3; strap down {xc:.0f} mm, R{NECK_RT:g} turn, "
          f"R{NECK_RHO:g} bend, R{NECK_RB:g} turn, tongue {off:+.1f} mm off the channel centre; valid {body.isValid()}")
    return [("H", "D6-04 arm end: J3 pad + pin, strap with one bend into BOTTOM's channel", body)], rep, holes


CUFF = dict(t_land=2.8, t_shell=2.0, land_hw=15.6, wrap_deg=110.0, s0=83.85, s1=164.65, round=0.8)


def upper_cuff(E, wrap_neg_deg=None):
    """Upper-arm cuff from one sketch of lines and arcs, extruded straight along BOTTOM (no loft, no fitted shell): a U
    of constant 2 mm wall - a flat top flush with BOTTOM's skin side (the bar sits on it) and two side arcs tangent to it,
    wrapping 110 deg each - whose centre, flat width and arc radius are the smallest that keep the upper-arm skin (the
    posed rig skin weighted to the humerus, every 4th followed frame of the fit clips) 2 mm (the liner) inside it.
    6x M4 countersunk from inside into BOTTOM's tapped holes. Built in the arm's rest frame (group H).
    wrap_neg_deg: the -vB side arc stops at this wrap instead (same fit, same sketch, a shorter arc), where the user's
    FOREARM CUFF folds onto the upper arm at deep elbow flexion (user_style_osn.py)."""
    from scipy.optimize import fsolve
    import body_pose as BP
    CB, uB, vB, axB = AE.CB, AE.uB, AE.vB, AE.axB; c = CUFF
    zt = AE.Z_SKIN_BAR; W_ = math.radians(c["wrap_deg"])                                    # the bar's skin-side plane (-2.8)
    Wn = W_ if wrap_neg_deg is None else math.radians(wrap_neg_deg)                        # the -vB side's wrap
    # the upper-arm skin in the arm's rest frame over every 4th followed frame of the fit clips (perpendicular distances
    # matter here, so the posed skin itself rather than the GH-radial maps)
    C_, _ = FR.load(PB.BAND); L = json.load(open(os.path.join(FR.REPO, "pipeline", "avg", "body_mesh.json"))); pts = []
    sk = BP._rig().skin; arm = ((sk["wi"] == 2) * sk["ww"]).sum(1) >= 0.6               # upper-arm skin only (skinning weight on the humerus)
    for _, _, f in FR.followed(C_, every=4):
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"])); Vw = BP.posed(pose)
        sg, _ = BP.segs(L["landmarks"], L["scale"], pose); Rh, th = np.array(sg[2][0]), np.array(sg[2][1])
        Q = (Vw[arm] - th) @ Rh - CB; sq = Q @ uB
        m = (sq > c["s0"] - 5) & (sq < c["s1"] + 5) & (np.abs(Q @ vB) < 90) & (Q @ axB < 0) & (Q @ axB > -130)
        pts.append(np.stack([Q[m] @ vB, Q[m] @ axB], 1))
    P2 = np.concatenate(pts); liner = 2.0
    T2_ = c["t_shell"]; zi = zt - T2_                                                    # constant 2 mm shell: top flush with the bar's skin side
    def fits(R, vc, hw):
        """margin (mm) of the U profile (flat top of half width hw at vc, side arcs of radius R tangent to it) over the skin + liner"""
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
    _, Rin, vc, hw = best
    print(f"cuff: {len(P2)} skin samples; U profile: flat {2 * hw:g} mm, side arcs R{Rin:g}, centred {vc:+.0f} mm across the bar, "
          f"{fits(Rin, vc, hw):.2f} mm beyond skin + 2 mm liner at the closest point")
    pl = cq.Plane(origin=tuple(map(float, CB + c["s0"] * uB)), xDir=tuple(map(float, vB)), normal=tuple(map(float, uB)))
    q = lambda xy: (float(xy[0]), float(xy[1]))
    def arcp(sg, R, a): return np.array([vc + sg * hw + sg * R * math.sin(a), zi - Rin + R * math.cos(a)])
    Ro = Rin + T2_
    # outline: outer top line -> right outer arc -> end cap -> right inner arc -> inner top line -> left inner arc -> cap -> left outer arc
    wp = (cq.Workplane(pl).moveTo(*q(arcp(-1, Ro, 0.0))).lineTo(*q(arcp(1, Ro, 0.0)))
          .threePointArc(q(arcp(1, Ro, W_ / 2)), q(arcp(1, Ro, W_))).lineTo(*q(arcp(1, Rin, W_)))
          .threePointArc(q(arcp(1, Rin, W_ / 2)), q(arcp(1, Rin, 0.0))).lineTo(*q(arcp(-1, Rin, 0.0)))
          .threePointArc(q(arcp(-1, Rin, Wn / 2)), q(arcp(-1, Rin, Wn))).lineTo(*q(arcp(-1, Ro, Wn)))
          .threePointArc(q(arcp(-1, Ro, Wn / 2)), q(arcp(-1, Ro, 0.0))).close())
    zc = zi - Rin; Ro_rep = Ro
    cuff = wp.extrude(c["s1"] - c["s0"]).val()
    cuff = rounded(cuff, r=c["round"])
    scr = []
    for s_ in (94.25, 124.25, 154.25):
        for y_ in (-8.75, 8.75):
            p = CB + s_ * uB + y_ * vB + zt * axB
            cuff = cuff.cut(cq.Solid.makeCylinder(2.25, 12.0, V(p - 10 * axB), V(axB)))
            hd = T2_                                                                            # head sits flush with the inner face
            cuff = cuff.cut(cq.Solid.makeCone(4.2, 0.0, 4.2, V(p - hd * axB), V(axB)))
            head = PB.revolved([(0, 0), (3.95, 0), (2.0, 1.95), (2.0, 6.0), (0, 6.0)], np.array([0, 0, 1.0]), 0.0)
            Rz = PB.axis_frame(axB); scr.append(("H", "M4x6 ISO 10642 countersunk (upper cuff), polished", xform(head, Rz, p - hd * axB)))
    cuff = cuff.clean() if cuff.clean().isValid() else cuff
    rep = dict(side_arc_R=Rin, flat_width=2 * hw, centre_across_bar=vc, shell=T2_, wrap_deg=c["wrap_deg"], wrap_neg_deg=None if wrap_neg_deg is None else float(wrap_neg_deg), length=c["s1"] - c["s0"], valid=cuff.isValid())
    print(f"  cuff valid {cuff.isValid()}, faces {len(cuff.Faces())}")
    return [("H", "UPPER ARM CUFF (lines and arcs: flat land + inner R arc + outer arc, extruded; AlSi10Mg bead blasted)", cuff)] + scr, rep


def export(parts, rep, C):
    import shutil, trimesh
    import body_pose as BP
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    for f in os.listdir(os.path.join(OUT, "step")): os.remove(os.path.join(OUT, "step", f))
    Cj = json.load(open(os.path.join(FR.FULL, "designs", PB.BAND, "clips.json")))
    for cl in Cj["clips"]:                                                                  # scapula-fixed group for the base
        for f in cl["frames"]: f["G"]["S"] = BP.scap(f["p"][1]).round(6).ravel().tolist()
    json.dump(Cj, open(os.path.join(OUT, "clips.json"), "w"), separators=(",", ":"))
    ws = os.path.join(FR.FULL, "designs", f"cad_{KEY}", "workspace.json")
    if os.path.exists(ws):
        W_ = json.load(open(ws))
        for p in W_["poses"]:
            if "G" in p: p["G"]["S"] = BP.scap(p["p"][1]).round(6).ravel().tolist()
        json.dump(W_, open(os.path.join(OUT, "workspace.json"), "w"), separators=(",", ":"))
    d = json.load(open(os.path.join(FR.FULL, "designs", f"cad_{KEY}", "design.json")))
    d.update(id=os.path.basename(OUT), label=f"3R champion {KEY}, parametric CAD in the user's style",
             built_with="pipeline/conformal/param_cad/user_style.py (line/arc sketches extruded, planform pads, v5 joints; base in the scapula frame S)")
    json.dump(d, open(os.path.join(OUT, "design.json"), "w"), indent=1)
    USER = ("BOTTOM", "TOP", "MIDDLE", "FOREARM", "UPPER ARM", "Hex", "M4", "IGUS", "5mm", "Revolve", "CirPattern")
    sc = trimesh.Scene(); pf = []
    for i, (g, n, s) in enumerate(parts):
        user = n.startswith(USER)
        if not user:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        fine = not user
        vs, fs = s.tessellate(0.02 if fine else 0.08, 0.15 if fine else 0.4)
        m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        if user: mat, rho = "user part", None
        elif "bearing" in n or "17-4PH" in n: mat, rho = ("bearing steel" if "bearing" in n else "17-4PH"), 7.8
        elif "7075-T6" in n: mat, rho = "7075-T6 (BOTTOM merged with the arm end)", 2.81
        else: mat, rho = "Ti-6Al-4V", 4.43
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids())))
    sc.export(os.path.join(OUT, "exo.glb"))
    json.dump(dict(key=KEY, n=3, FACES={"1": rep["faces"]["J1"], "2": rep["faces"]["J2"], "3": rep["faces"]["J3"]}, parts=pf),
              open(os.path.join(OUT, "parts_full.json"), "w"), indent=1)
    json.dump(dict(rep, parts=pf), open(os.path.join(OUT, "build.json"), "w"), indent=1, default=float)
    bad = [p["name"] for p in pf if not p["valid"] or p["solids"] != 1]
    print(f"custom-part mass {sum(p['mass_g'] or 0 for p in pf):.1f} g; exported {len(pf)} parts -> {OUT}; invalid or multi-solid: {bad or 'none'}")


if __name__ == "__main__":
    P, rep, C = main()
    export(P, rep, C)
