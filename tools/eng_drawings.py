"""Engineering drawing sheets (ISO A3 landscape, third-angle projection) from a design's built STEP files.

Per made part: front / top / right views with hidden lines (OpenCascade HLR of the real solid), an isometric view,
overall dimensions, every full bore and pin tagged and listed in a hole table (size + fit from the design's fit list,
length, centre and axis in the part's datum frame), title block, material / finish / mass, general tolerances and
notes. Per set: a general-arrangement sheet (assembly views, balloons, parts list) and a hub-stack section sheet.
Output: docs/drawings/<set>/<set>_drawings.pdf + one PNG per sheet + sheets.json.

    OMP_NUM_THREADS=1 nice python3 tools/eng_drawings.py B        (sets: A, B; add a part number to draw one sheet)
"""
import glob, json, math, os, sys
import numpy as np
import cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Circle, Rectangle
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf
from OCP.BRepLib import BRepLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
from OCP.BRepTools import BRepTools
from OCP.BRepLProp import BRepLProp_SLProps
from OCP.Bnd import Bnd_OBB, Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 420.0, 297.0                                   # A3 landscape, mm
PT = 72 / 25.4                                        # points per mm
INK = "#000000"
FS = lambda h: h * PT / 0.72                          # font size (pt) for a capital height h (mm)
LW = {"vis": 0.5, "hid": 0.25, "cen": 0.18, "dim": 0.18, "frame": 0.7, "thin": 0.25}
SCALES = [10, 5, 2, 1, 0.5, 0.2, 0.1]                 # ISO 5455
DATE = "2026-10-18"


# ------------------------------------------------------------------ geometry
def load(path):
    w = cq.importers.importStep(path)
    vals = w.vals()
    return vals[0].wrapped if len(vals) == 1 else cq.Compound.makeCompound(vals).wrapped


def compound(shapes):
    return cq.Compound.makeCompound([cq.Shape.cast(s) for s in shapes]).wrapped


def transformed(shape, R, O):
    """world -> local: p' = R (p - O), rows of R are the local axes in world coordinates"""
    t = gp_Trsf(); tr = -R @ O
    t.SetValues(*R[0], tr[0], *R[1], tr[1], *R[2], tr[2])
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def to_world(shape, R, O):
    """local -> world: p = R^T p' + O (the inverse of transformed)"""
    t = gp_Trsf(); Rt = R.T
    t.SetValues(*Rt[0], O[0], *Rt[1], O[1], *Rt[2], O[2])
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def polyhedral(shape, defl=0.02):
    """the solid rebuilt from its tessellation (sewn triangles): a fallback for STEP solids whose booleans come back empty"""
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    BRepMesh_IncrementalMesh(shape, defl, False, 0.2, True)
    sew = BRepBuilderAPI_Sewing(1e-4)
    e = TopExp_Explorer(shape, TopAbs_FACE)
    while e.More():
        f = TopoDS.Face_s(e.Current()); e.Next(); loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is None:
            continue
        tr = loc.Transformation(); rev = f.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            if rev:
                b, c = c, b
            P = [tri.Node(k).Transformed(tr) for k in (a, b, c)]
            mf = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(P[0], P[1], P[2], True).Wire(), True)
            if mf.IsDone():
                sew.Add(mf.Face())
    sew.Perform()
    ex = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL); ms = BRepBuilderAPI_MakeSolid()
    while ex.More():
        ms.Add(TopoDS.Shell_s(ex.Current())); ex.Next()
    return ms.Solid()


def part_frame(shape):
    """principal frame of a part: X longest, Z thinnest pointing away from the shoulder centre (GH = world origin),
    X pointing down the arm (world -Y) where it can, else lateral; centred on the oriented bounding box"""
    obb = Bnd_OBB(); BRepBndLib.AddOBB_s(shape, obb, True, True, True)
    ax = [obb.XDirection(), obb.YDirection(), obb.ZDirection()]; hs = [obb.XHSize(), obb.YHSize(), obb.ZHSize()]
    V = [np.array([ax[i].X(), ax[i].Y(), ax[i].Z()]) for i in np.argsort(hs)[::-1]]
    c = obb.Center(); C = np.array([c.X(), c.Y(), c.Z()])
    X, _, Z = V
    if np.dot(Z, C) < 0:
        Z = -Z
    if abs(X[1]) > 0.2:
        X = X if X[1] < 0 else -X
    elif X[2] < 0:
        X = -X
    Y = np.cross(Z, X)
    return np.array([X, Y, Z]), C


def bbox(shape):
    b = Bnd_Box(); BRepBndLib.Add_s(shape, b, True)
    x0, y0, z0, x1, y1, z1 = b.Get()
    return np.array([x0, y0, z0]), np.array([x1, y1, z1])


def volume(shape):
    p = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, p)
    c = p.CentreOfMass()
    return p.Mass(), np.array([c.X(), c.Y(), c.Z()])


def features(shape):
    """full cylindrical bores and pins: radius, centre, axis, axial length, hole / boss"""
    raw = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face_s(exp.Current()); exp.Next()
        s = BRepAdaptor_Surface(f)
        if s.GetType() != GeomAbs_Cylinder:
            continue
        cyl = s.Cylinder(); a = cyl.Axis()
        P0 = np.array([a.Location().X(), a.Location().Y(), a.Location().Z()]); D = np.array([a.Direction().X(), a.Direction().Y(), a.Direction().Z()])
        u0, u1, v0, v1 = BRepTools.UVBounds_s(f)
        pr = BRepLProp_SLProps(s, (u0 + u1) / 2, (v0 + v1) / 2, 1, 1e-6)
        if not pr.IsNormalDefined():
            continue
        P = np.array([pr.Value().X(), pr.Value().Y(), pr.Value().Z()]); N = np.array([pr.Normal().X(), pr.Normal().Y(), pr.Normal().Z()])
        if f.Orientation() == TopAbs_REVERSED:
            N = -N
        rad = P - (P0 + D * np.dot(P - P0, D)); rn = np.linalg.norm(rad)
        if rn < 1e-9:
            continue
        raw.append(dict(r=cyl.Radius(), P0=P0, D=D, v0=v0, v1=v1, us=u1 - u0, hole=bool(np.dot(N, rad / rn) < 0)))
    feats = []
    for f in raw:
        for g in feats:
            if g["hole"] == f["hole"] and abs(g["r"] - f["r"]) < 2e-3 and abs(abs(np.dot(g["D"], f["D"])) - 1) < 1e-6:
                d = f["P0"] - g["P0"]
                if np.linalg.norm(d - g["D"] * np.dot(d, g["D"])) < 2e-3:
                    s0 = np.dot(d, g["D"]); sg = np.sign(np.dot(f["D"], g["D"]))
                    g["segs"].append(tuple(sorted([s0 + sg * f["v0"], s0 + sg * f["v1"]]))); g["us"] += f["us"]
                    break
        else:
            feats.append(dict(f, segs=[(f["v0"], f["v1"])]))
    out = []
    for g in feats:
        if g["us"] < 1.9 * math.pi:
            continue
        lo = min(s[0] for s in g["segs"]); hi = max(s[1] for s in g["segs"])
        d = 2 * g["r"]
        if g["hole"] and d > 25:
            continue
        if not g["hole"] and not any(abs(d - k) < 0.05 for k in (3, 4, 7, 9, 12, 18, 20)):
            continue
        out.append(dict(d=d, hole=g["hole"], c=g["P0"] + g["D"] * (lo + hi) / 2, D=g["D"], L=hi - lo))
    return out


def callout(f):
    """size + fit and function (fits from pipeline/full-exo/designs/*/design.json 'fits' and docs/HARDWARE.md)"""
    d = f["d"]; near = lambda x: abs(d - x) < 0.04
    if f["hole"]:
        for x, s, fn in ((11, "Ø11 J6", "MR117-2RS housing"), (6, "Ø6 J6", "MR63ZZ housing"), (3, "Ø3 H7", "press, ISO 8734 m6 pin"),
                         (2, "Ø2 −0.005/0", "reamed, stop dowel press"), (2.5, "Ø2.5 −0.005/0", "reamed, nose dowel press"),
                         (5.5, "Ø5.5 H7", "iglidur GSM-0405-03 press"), (20, "Ø20 H7", "on the cap skirt"), (7, "Ø7 H7", "bore"),
                         (4, "Ø4 H8", "pin clearance"), (1, "Ø1 H7", "key dowel"), (3.3, "M4 tapped", "tap drill Ø3.3, thread M4×0.7"),
                         (4.5, "Ø4.5 + CSK 90°", "M4 countersunk clearance (ISO 10642)"), (8, "Ø8", "clip counterbore")):
            if near(x):
                return s, fn
        return f"Ø{d:.2f}", "hole"
    for x, s, fn in ((7, "Ø7 j5", "MR117-2RS seat (integral pin)"), (4, "Ø4 h9", "pin (integral, hard anodise)"), (18, "M18×0.5-6g", "thread (cap / handler)"),
                     (20, "Ø20", "hub ring OD"), (12, "Ø12", "boss"), (9, "Ø9", "bearing boss"), (3, "Ø3 h5", "pin")):
        if near(x):
            return s, fn
    return f"Ø{d:.2f}", "boss"


def hlr(shape, N, Vx, defl=0.02):
    a = HLRBRep_Algo(); a.Add(shape)
    a.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*N), gp_Dir(*Vx)))); a.Update(); a.Hide()
    h = HLRBRep_HLRToShape(a)
    def polys(c):
        out = []
        if c is None or c.IsNull():
            return out
        BRepLib.BuildCurves3d_s(c, 1e-4)
        e = TopExp_Explorer(c, TopAbs_EDGE)
        while e.More():
            try:
                ad = BRepAdaptor_Curve(TopoDS.Edge_s(e.Current())); d = GCPnts_QuasiUniformDeflection(ad, defl)
                if d.IsDone() and d.NbPoints() > 1:
                    out.append(np.array([(d.Value(i).X(), d.Value(i).Y()) for i in range(1, d.NbPoints() + 1)]))
            except Exception:
                pass
            e.Next()
        return out
    def safe(name):
        try:
            return polys(getattr(h, name)())
        except Exception:                                    # a degenerate projected curve: skip that edge set
            return []
    vis = safe("VCompound") + safe("OutLineVCompound")
    hid = safe("HCompound") + safe("OutLineHCompound")
    return vis, hid


VIEWS = {"front": ((0, 0, 1), (1, 0, 0)), "top": ((0, 1, 0), (1, 0, 0)), "right": ((1, 0, 0), (0, 0, -1))}
ISO_N = np.array([1.0, 1.0, 1.0]) / math.sqrt(3); ISO_X = np.array([1.0, 0, -1.0]) / math.sqrt(2)


def view_xy(p, view):
    N, Vx = (np.array(v, float) for v in VIEWS[view]) if view != "iso" else (ISO_N, ISO_X)
    Vy = np.cross(N, Vx)
    return np.array([np.dot(p, Vx), np.dot(p, Vy)])


def ext(polys):
    a = np.concatenate(polys)
    return a.min(0), a.max(0)


# ------------------------------------------------------------------ sheet furniture
class Sheet:
    def __init__(self):
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, W); self.ax.set_ylim(0, H); self.ax.axis("off")

    def line(self, xs, ys, kind="vis", **kw):
        st = {"vis": "-", "hid": (0, (3.0 * PT / LW["hid"] / PT * 0.9, 1.2)), "cen": (0, (12, 3, 2, 3)), "dim": "-", "frame": "-", "thin": "-"}[kind]
        if kind == "hid":
            st = (0, (4, 2))
        self.ax.plot(xs, ys, color=INK, lw=LW[kind] * PT, linestyle=st, solid_capstyle="round", **kw)

    def text(self, x, y, s, h=3.5, ha="left", va="baseline", rot=0, weight="normal", color=INK):
        self.ax.text(x, y, s, fontsize=FS(h), ha=ha, va=va, rotation=rot, fontweight=weight, color=color, family="DejaVu Sans")

    def rect(self, x0, y0, x1, y1, kind="thin"):
        self.line([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], kind)

    def arrow(self, x, y, dx, dy, L=3.0):
        n = math.hypot(dx, dy); ux, uy = dx / n, dy / n; w = L * math.tan(math.radians(9))
        self.ax.add_patch(Polygon([(x, y), (x - ux * L - uy * w, y - uy * L + ux * w), (x - ux * L + uy * w, y - uy * L - ux * w)],
                                  closed=True, facecolor=INK, edgecolor=INK, lw=0.1))

    def dim(self, p1, p2, side, off, txt, h=2.5):
        """horizontal (side 'below'/'above') or vertical (side 'left'/'right') dimension between paper points p1, p2"""
        (x1, y1), (x2, y2) = p1, p2
        if side in ("below", "above"):
            sg = -1 if side == "below" else 1
            y = (min(y1, y2) if sg < 0 else max(y1, y2)) + sg * off
            for (x, yy) in ((x1, y1), (x2, y2)):
                self.line([x, x], [yy + sg * 1.0, y + sg * 1.5], "dim")
            self.line([x1, x2], [y, y], "dim"); self.arrow(x1, y, x1 - x2, 0); self.arrow(x2, y, x2 - x1, 0)
            self.text((x1 + x2) / 2, y + 0.9, txt, h, ha="center")
        else:
            sg = -1 if side == "left" else 1
            x = (min(x1, x2) if sg < 0 else max(x1, x2)) + sg * off
            for (xx, y) in ((x1, y1), (x2, y2)):
                self.line([xx + sg * 1.0, x + sg * 1.5], [y, y], "dim")
            self.line([x, x], [y1, y2], "dim"); self.arrow(x, y1, 0, y1 - y2); self.arrow(x, y2, 0, y2 - y1)
            self.text(x - 0.9, (y1 + y2) / 2, txt, h, ha="center", va="bottom", rot=90)

    def border(self):
        self.rect(20, 10, W - 10, H - 10, "frame"); self.rect(5, 5, W - 5, H - 5, "thin")
        for i in range(1, 8):                                     # zone ticks
            x = 20 + (W - 30) * i / 8
            self.line([x, x], [H - 10, H - 5], "thin"); self.line([x, x], [5, 10], "thin")
        for i, ch in enumerate("ABCDEFGH"):
            self.text(20 + (W - 30) * (i + 0.5) / 8, H - 8.6, str(i + 1), 2.5, ha="center")
        for i, ch in enumerate("FEDCBA"):
            y = 10 + (H - 20) * (i + 0.5) / 6
            self.text(12.5, y, ch, 2.5, ha="center", va="center")

    def proj_symbol(self, x, y):
        """third-angle projection symbol (ISO 5456-2), at lower-left corner (x, y), ~16 x 7 mm"""
        self.ax.add_patch(Polygon([(x, y + 1.5), (x + 6, y), (x + 6, y + 7), (x, y + 5.5)], closed=True, fill=False, lw=LW["vis"] * PT, edgecolor=INK))
        self.ax.add_patch(Circle((x + 12, y + 3.5), 3.5, fill=False, lw=LW["vis"] * PT, edgecolor=INK))
        self.ax.add_patch(Circle((x + 12, y + 3.5), 2.0, fill=False, lw=LW["vis"] * PT, edgecolor=INK))
        self.line([x - 1, x + 17], [y + 3.5, y + 3.5], "cen")

    def title_block(self, f):
        x0, y0, x1, y1 = W - 10 - 180, 10, W - 10, 56
        self.rect(x0, y0, x1, y1, "frame")
        rows = [y0, y0 + 9, y0 + 18, y0 + 27, y0 + 36, y1]
        for y in rows[1:-1]:
            self.line([x0, x1], [y, y], "thin")
        cols = [x0, x0 + 45, x0 + 90, x0 + 135, x1]
        def cell(c0, c1, r, label, value, h=3.0, weight="normal"):
            xa, xb = cols[c0], cols[c1]; ya = rows[r]
            if c0 > 0:
                self.line([xa, xa], [ya, rows[r + 1]], "thin")
            self.text(xa + 1.2, ya + 6.3, label, 1.8, color="#444444")
            self.text(xa + 1.2, ya + 1.6, value, h, weight=weight)
        cell(0, 3, 4, "TITLE", f["title"], 4.2 if len(f["title"]) <= 30 else 3.0, "bold"); cell(3, 4, 4, "DRAWING NO.", f["dwg"], 3.2, "bold")
        cell(0, 2, 3, "DESIGN", f["design"], 2.6); cell(2, 3, 3, "PART NO.", f["pn"], 3.2, "bold"); cell(3, 4, 3, "REV / STATUS", f.get("rev", "A · for review"), 2.6)
        cell(0, 2, 2, "MATERIAL", f["material"], 2.6); cell(2, 3, 2, "MASS", f["mass"], 3.0); cell(3, 4, 2, "QTY PER ASSEMBLY", str(f["qty"]), 3.0)
        cell(0, 2, 1, "FINISH", f["finish"], 2.6); cell(2, 3, 1, "SCALE", f["scale"], 3.0); cell(3, 4, 1, "SHEET", f["sheet"], 3.0)
        cell(0, 2, 0, "GENERAL TOLERANCES", "ISO 2768-mK · mm · Ra 3.2", 2.6); cell(2, 3, 0, "DATE", DATE, 2.6); cell(3, 4, 0, "SOURCE", f["src"][:38], 1.9)
        self.proj_symbol(x0 - 22, y0 + 2); self.text(x0 - 22, y0 + 11, "THIRD ANGLE", 1.8)

    def notes(self, x, y, items, h=2.5, width=118):
        self.text(x, y, "NOTES", 3.0, weight="bold"); y -= 5.5
        import textwrap
        for i, t in enumerate(items, 1):
            lines = textwrap.wrap(t, int(width / (h / 0.72 * 0.56)))
            for j, ln in enumerate(lines):
                self.text(x + (0 if j == 0 else 5), y, (f"{i}. " if j == 0 else "") + ln, h); y -= h * 1.55
            y -= 0.6
        return y

    def table(self, x, ytop, cols, rows, h=2.3, rowh=4.6, head=True):
        widths = [c[1] for c in cols]; xs = np.cumsum([x] + widths)
        y = ytop
        if head:
            self.line([xs[0], xs[-1]], [y, y], "vis")
            for (name, w), xa in zip(cols, xs[:-1]):
                self.text(xa + 1, y - rowh + 1.3, name, h * 0.85, weight="bold")
            y -= rowh; self.line([xs[0], xs[-1]], [y, y], "vis")
        for r in rows:
            for v, xa, (name, w) in zip(r, xs[:-1], cols):
                self.text(xa + 1, y - rowh + 1.3, str(v), h)
            y -= rowh; self.line([xs[0], xs[-1]], [y, y], "thin")
        for xa in xs:
            self.line([xa, xa], [ytop, y], "thin")
        return y

    def save(self, pdf, png):
        pdf.savefig(self.fig); self.fig.savefig(png, dpi=150, facecolor="white"); plt.close(self.fig)


def draw_polys(sh, polys, s, ox, oy, kind):
    for p in polys:
        sh.line(ox + s * p[:, 0], oy + s * p[:, 1], kind)


def pick_scale(need_w, need_h, room_w, room_h):
    for s in SCALES:
        if need_w * s <= room_w and need_h * s <= room_h:
            return s
    return SCALES[-1]


def scale_txt(s):
    return f"{int(s)}:1" if s >= 1 else f"1:{int(round(1 / s))}"


# ------------------------------------------------------------------ detail sheet
def detail_sheet(spec, set_info, sheet_no, n_sheets, pdf, png):
    shape_w = load(spec["step"])
    R, C = part_frame(shape_w)
    sh0 = transformed(shape_w, R, C)
    F = features(sh0)
    groups = []
    for f in F:
        for g in groups:
            if abs(abs(np.dot(f["D"], g["D"])) - 1) < 1e-4 and np.linalg.norm(np.cross(f["c"] - g["c"], g["D"])) < 0.05:
                g["f"].append(f); break
        else:
            groups.append({"D": f["D"], "c": f["c"], "f": [f]})
    def prio(g):
        ds = [(f["hole"], round(f["d"], 1)) for f in g["f"]]
        for i, k in enumerate([(True, 11.0), (False, 7.0), (False, 4.0), (False, 20.0), (False, 18.0), (False, 12.0)]):
            if k in ds:
                return i
        return 99
    best = min((prio(g) for g in groups), default=99)
    for g in groups:
        g["c"] = np.mean([f["c"] for f in g["f"]], axis=0)
    cand = [g for g in groups if prio(g) == best]
    datum = min(cand, key=lambda g: g["c"][0]) if cand and best < 99 else None
    if datum:
        df = next(f for f in datum["f"] if prio({"f": [f]}) == best)
        O = df["c"].copy()
    else:
        O = np.zeros(3)
    shape = transformed(shape_w, R, C + R.T @ O)
    for g in groups:
        g["c"] = g["c"] - O
        for f in g["f"]:
            f["c"] = f["c"] - O
        g["f"].sort(key=lambda f: (not f["hole"], f["d"]))
    groups.sort(key=lambda g: (g is not datum, round(g["c"][0], 1), g["c"][1]))
    for i, g in enumerate(groups):
        g["tag"] = chr(65 + i) if i < 26 else f"Z{i - 25}"
        for j, f in enumerate(g["f"]):
            f["tag"] = g["tag"] + (str(j + 1) if len(g["f"]) > 1 else "")
    F = [f for g in groups for f in g["f"]]
    joints = [g for g in groups if prio(g) < 3]
    vol, _ = volume(shape)
    V = {k: hlr(shape, *VIEWS[k]) for k in VIEWS}
    E = {k: ext(V[k][0] + V[k][1]) for k in V}
    sz = {k: E[k][1] - E[k][0] for k in E}
    sh = Sheet(); sh.border()
    # layout: top view above front, right view right of front; dims need ~14 mm per side
    room_w, room_h = 290.0, 285.0 - 112.0
    s = pick_scale(sz["front"][0] + sz["right"][0], sz["front"][1] + sz["top"][1], room_w - 26, room_h - 34)
    gx = gy = 12.0
    fw, fh = sz["front"] * s; tw, th = sz["top"] * s; rw, rh = sz["right"] * s
    tot_w = fw + gx + rw; tot_h = fh + gy + th
    x_left = 22 + 14 + max(0.0, (room_w - 16 - tot_w) / 2); y_bot = 112 + 14 + max(0.0, (room_h - 30 - tot_h) / 2)
    org = {"front": (x_left - E["front"][0][0] * s, y_bot - E["front"][0][1] * s),
           "top": (x_left - E["top"][0][0] * s, y_bot + fh + gy - E["top"][0][1] * s),
           "right": (x_left + fw + gx - E["right"][0][0] * s, y_bot - E["right"][0][1] * s)}
    names = {"front": "FRONT (looking at the outer face)", "top": "TOP", "right": "RIGHT"}
    for k in VIEWS:
        ox, oy = org[k]
        draw_polys(sh, V[k][1], s, ox, oy, "hid"); draw_polys(sh, V[k][0], s, ox, oy, "vis")
        lo, hi = E[k]
        sh.text(ox + (lo[0] + hi[0]) / 2 * s, oy + hi[1] * s + (9 if k != "front" else 4), names[k], 2.5, ha="center")
    # overall dimensions
    ox, oy = org["front"]; lo, hi = E["front"]
    sh.dim((ox + lo[0] * s, oy + lo[1] * s), (ox + hi[0] * s, oy + lo[1] * s), "below", 7, f"{hi[0] - lo[0]:.1f}")
    sh.dim((ox + lo[0] * s, oy + lo[1] * s), (ox + lo[0] * s, oy + hi[1] * s), "left", 7, f"{hi[1] - lo[1]:.1f}")
    ox, oy = org["top"]; lo, hi = E["top"]
    sh.dim((ox + lo[0] * s, oy + lo[1] * s), (ox + lo[0] * s, oy + hi[1] * s), "left", 7, f"{hi[1] - lo[1]:.1f}")
    # datum triad + feature tags (in the first view where the axis is end-on)
    ox, oy = org["front"]
    sh.line([ox, ox + 8], [oy, oy], "dim"); sh.arrow(ox + 8, oy, 1, 0, 2.2); sh.text(ox + 9, oy - 1, "X", 2.2)
    sh.line([ox, ox], [oy, oy + 8], "dim"); sh.arrow(ox, oy + 8, 0, 1, 2.2); sh.text(ox - 1, oy + 9, "Y", 2.2, ha="right")
    sh.ax.add_patch(Circle((ox, oy), 0.9, fill=False, lw=LW["dim"] * PT, edgecolor=INK)); sh.text(ox - 2, oy - 3.2, "Z (out)", 1.8, ha="right")
    placed = []
    for g in groups:
        best = None
        for k, (N, Vx) in VIEWS.items():
            if abs(np.dot(g["D"], N)) > 0.985:
                best = k; break
        k = best or "front"
        c2 = view_xy(g["c"], k); px, py = org[k][0] + c2[0] * s, org[k][1] + c2[1] * s
        if best:
            r = max(f["d"] for f in g["f"]) / 2 * s + 1.5
            sh.line([px - r, px + r], [py, py], "cen"); sh.line([px, px], [py - r, py + r], "cen")
        dx, dy = 7.0, 6.0
        while any(abs(qx - (px + dx)) < 5.5 and abs(qy - (py + dy)) < 5.5 for qx, qy in placed):
            dy += 5.5
        placed.append((px + dx, py + dy))
        sh.line([px, px + dx - 1.8], [py, py + dy - 1.4], "dim")
        sh.ax.add_patch(Circle((px + dx, py + dy), 2.4, facecolor="white", edgecolor=INK, lw=LW["dim"] * PT, zorder=5))
        sh.ax.text(px + dx, py + dy, g["tag"], fontsize=FS(2.1), ha="center", va="center", zorder=6)
    # isometric view (own scale)
    Vi = hlr(shape, ISO_N, ISO_X)
    lo, hi = ext(Vi[0]); szi = hi - lo
    si = pick_scale(szi[0], szi[1], 88, 80)
    ix = 318 + (90 - szi[0] * si) / 2 - lo[0] * si; iy = 196 + (84 - szi[1] * si) / 2 - lo[1] * si
    draw_polys(sh, Vi[0], si, ix, iy, "vis")
    sh.text(363, 191, f"ISOMETRIC ({scale_txt(si)})", 2.5, ha="center")
    # hole table
    cols = [("TAG", 9), ("SIZE / FIT", 26), ("FUNCTION", 47), ("TYPE", 11), ("LEN", 11), ("X", 15), ("Y", 15), ("Z", 15), ("AXIS i, j, k", 39)]
    rows = []
    for f in F[:17]:
        sz_, fn = callout(f)
        rows.append([f["tag"], sz_, fn, "bore" if f["hole"] else "pin", f"{f['L']:.2f}", f"{f['c'][0]:.2f}", f"{f['c'][1]:.2f}", f"{f['c'][2]:.2f}",
                     f"{f['D'][0]:+.3f} {f['D'][1]:+.3f} {f['D'][2]:+.3f}"])
    if not rows:
        rows = [["–", "no full bores or pins", "", "", "", "", "", "", ""]]
    sh.text(24, 106, "HOLE AND PIN TABLE", 3.0, weight="bold")
    sh.text(24, 101.5, "Origin: tag A axis, mid-length (datum A). X, Y, Z: part axes as drawn. Centres in mm.", 2.0)
    yend = sh.table(24, 99, cols, rows, h=2.1, rowh=4.2)
    if len(F) > 17:
        sh.text(24, yend - 4, f"+{len(F) - 17} more features: see STEP", 2.0)
    # notes
    n = ["Master geometry: STEP file " + os.path.basename(spec["step"]) + ". Dimensions not shown: take from the model.",
         "Bores and pins: the hole table. Fits from the design fit list (hub: Ø7 j5 shaft / Ø11 J6 housing for MR117-2RS pairs).",
         "Position of tagged features: Ø0.02 to datum A for hub and pin features, Ø0.05 for others (proposed; review before release).",
         "Surface: Ra 0.8 on bearing seats and pins, Ra 1.6 on mating faces, Ra 3.2 elsewhere. Break sharp edges 0.2 max."]
    n += spec.get("notes", [])
    if joints and len(joints) > 1:
        jr = []
        for g1, g2 in zip(joints, joints[1:]):
            ang = math.degrees(math.acos(min(1.0, abs(np.dot(g1["D"], g2["D"])))))
            w = np.cross(g1["D"], g2["D"]); dd = g2["c"] - g1["c"]
            md = abs(np.dot(dd, w / np.linalg.norm(w))) if np.linalg.norm(w) > 1e-9 else np.linalg.norm(np.cross(dd, g1["D"]))
            jr.append([f"{g1['tag']}–{g2['tag']}", f"{ang:.2f}°", f"{np.linalg.norm(dd):.2f}", f"{md:.2f}"])
        sh.text(318, 186 - 6, "JOINT AXES", 2.8, weight="bold")
        ye = sh.table(318, 178, [("AXES", 16), ("ANGLE", 20), ("CENTRES", 24), ("AXIS GAP", 24)], jr, h=2.1, rowh=4.2)
        sh.text(318, ye - 3.5, "centres: distance between tagged centres; axis gap: closest", 1.7); sh.text(318, ye - 6.2, "approach of the two axis lines (0 = they intersect).", 1.7)
        ny = ye - 11
    else:
        ny = 182
    sh.notes(318, ny, n, h=2.1, width=88)
    sh.title_block({"title": spec["title"], "dwg": f"EXO-{set_info['key']}-{spec['pn']}", "design": set_info["design"], "pn": spec["pn"],
                    "material": spec["material"], "mass": f"{vol * spec['rho'] / 1000:.2f} g", "qty": spec["qty"], "finish": spec["finish"],
                    "scale": scale_txt(s), "sheet": f"{sheet_no} / {n_sheets}", "src": os.path.basename(spec["step"])[:44]})
    sh.save(pdf, png)
    return {"pn": spec["pn"], "title": spec["title"], "scale": scale_txt(s), "features": len(F), "mass_g": round(vol * spec["rho"] / 1000, 2)}


# ------------------------------------------------------------------ general arrangement
def ga_sheet(set_info, bom, sheet_no, n_sheets, pdf, png):
    shapes, items = [], []
    for it in bom:
        for st in it.get("steps", []):
            shp = load(st); shapes.append(shp); items.append((it["item"], shp))
    asm = compound(shapes)
    sh = Sheet(); sh.border()
    views = {"behind": ((-1, 0, 0), (0, 0, 1)), "side": ((0, 0, 1), (1, 0, 0))}
    Vs = {k: hlr(asm, *v, defl=0.05) for k, v in views.items()}
    Es = {k: ext(Vs[k][0]) for k in Vs}
    room = (24, 60, 300, 286)                                 # x0, y0, x1, y1 for the two views side by side
    need_w = sum((Es[k][1] - Es[k][0])[0] for k in Vs); need_h = max((Es[k][1] - Es[k][0])[1] for k in Vs)
    s = pick_scale(need_w, need_h, room[2] - room[0] - 70, room[3] - room[1] - 14)
    gap = max(30.0, (room[2] - room[0] - 40 - need_w * s) / 2)
    x = room[0] + 20
    org = {}
    for k in ("behind", "side"):
        lo, hi = Es[k]
        org[k] = (x - lo[0] * s, room[1] + 4 + ((room[3] - room[1] - 14) - (hi[1] - lo[1]) * s) / 2 - lo[1] * s)
        draw_polys(sh, Vs[k][0], s, *org[k], "vis")
        sh.text(x + (hi[0] - lo[0]) * s / 2, org[k][1] + hi[1] * s + 5, {"behind": "VIEW FROM BEHIND", "side": "VIEW FROM THE RIGHT SIDE"}[k], 2.8, ha="center")
        x += (hi[0] - lo[0]) * s + gap
    # balloons on the view from behind
    k = "behind"; N, Vx = (np.array(v, float) for v in views[k]); Vy = np.cross(N, Vx)
    lo, hi = Es[k]; cx = org[k][0] + (lo[0] + hi[0]) / 2 * s; cy = org[k][1] + (lo[1] + hi[1]) / 2 * s
    pts = {}
    for item, shp in items:
        if item in pts:
            continue
        _, c = volume(shp)
        pts[item] = (org[k][0] + np.dot(c, Vx) * s, org[k][1] + np.dot(c, Vy) * s)
    left = sorted([(p[1], i, p) for i, p in pts.items() if p[0] <= cx], reverse=True)
    right = sorted([(p[1], i, p) for i, p in pts.items() if p[0] > cx], reverse=True)
    for side, lst in (("L", left), ("R", right)):
        if not lst:
            continue
        bx = org[k][0] + lo[0] * s - 12 if side == "L" else org[k][0] + hi[0] * s + 12
        top_ = org[k][1] + hi[1] * s; bot_ = org[k][1] + lo[1] * s
        ys = np.linspace(min(278, top_ + 4), max(70, bot_ - 4), len(lst)) if len(lst) > 1 else [lst[0][2][1]]
        for (yy, item, p), by in zip(lst, ys):
            sh.line([p[0], bx + (3.2 if side == "L" else -3.2)], [p[1], by], "dim")
            sh.ax.add_patch(Circle(p, 0.6, facecolor=INK, edgecolor=INK))
            sh.ax.add_patch(Circle((bx, by), 3.2, facecolor="white", edgecolor=INK, lw=LW["dim"] * PT, zorder=5))
            sh.ax.text(bx, by, str(item), fontsize=FS(2.4), ha="center", va="center", zorder=6)
    # parts list
    cols = [("ITEM", 8), ("PART NO.", 23), ("DESCRIPTION", 63), ("QTY", 12)]
    rows = [[b["item"], b["pn"], b["desc"], b["qty"]] for b in bom]
    sh.text(303, 282, "PARTS LIST", 3.0, weight="bold")
    yend = sh.table(303, 279, cols, rows, h=1.75, rowh=3.8)
    sh.text(303, yend - 3, "Materials and finishes: on each part sheet.", 1.8)
    sh.notes(303, yend - 9, set_info["ga_notes"], h=1.9, width=104)
    sh.title_block({"title": set_info["ga_title"], "dwg": f"EXO-{set_info['key']}-GA", "design": set_info["design"], "pn": f"{set_info['key']}-ASSY",
                    "material": "see parts list", "mass": set_info["mass"], "qty": 1, "finish": "see part drawings", "scale": scale_txt(s),
                    "sheet": f"{sheet_no} / {n_sheets}", "src": set_info["step_dir"][-58:]})
    sh.save(pdf, png)


# ------------------------------------------------------------------ hub stack section
def hub_sheet(set_info, hub, sheet_no, n_sheets, pdf, png):
    """section through one Ø20 hub (bearings, spacers, ring nut, cap, the two members' local rings), plane through the
    hub axis, clipped to a 30 mm box around the hub"""
    brg = load(hub["bearing"])
    F = [f for f in features(brg) if abs(f["d"] - 11) < 0.05 or abs(f["d"] - 7) < 0.05]
    axis = F[0]["D"]; _, c0 = volume(brg)
    if np.dot(axis, c0) < 0:
        axis = -axis                                         # +Z points away from the skin (out of the body)
    Z = axis / np.linalg.norm(axis); X = np.cross([0, 1.0, 0], Z); X /= np.linalg.norm(X); Y = np.cross(Z, X)
    R = np.array([X, Y, Z]); O = F[0]["c"]
    parts = []
    from OCP.gp import gp_Ax2 as _Ax2, gp_Dir as _Dir
    p0 = O - 15 * X - 15 * Y - 14 * Z
    box = BRepPrimAPI_MakeBox(_Ax2(gp_Pnt(*p0), _Dir(*Z), _Dir(*X)), 30, 15, 30).Shape()
    poly = set()
    for label, path in hub["parts"]:
        w = load(path)
        cw = BRepAlgoAPI_Common(w, box).Shape()
        if volume(cw)[0] < 1e-6:                             # some STEP solids defeat the boolean: clip their tessellation instead
            cw = BRepAlgoAPI_Common(polyhedral(w), box).Shape()
            if volume(cw)[0] > 1e-6:
                poly.add(label)
        cut = transformed(cw, R, O)
        try:
            lo, hi = bbox(cut)
        except Exception:                                    # nothing of this part inside the clip box
            continue
        if np.any(hi - lo < 1e-6):
            continue
        parts.append((label, cut))
    sh = Sheet(); sh.border()
    s = 5.0
    N, Vx = (0, 1.0, 0), (1.0, 0, 0)                        # view from +Y onto the cut plane y = 0: x right, z up
    ox, oy = 125, 150
    hatches = ["////", "\\\\\\\\", "xxxx", "----", "||||", "++++", "....", "oo"]
    for i, (label, cut) in enumerate(parts):
        vis, _ = hlr(cut, N, Vx, defl=0.01)
        exp = TopExp_Explorer(cut, TopAbs_FACE)
        while exp.More():
            f = TopoDS.Face_s(exp.Current()); exp.Next()
            sa = BRepAdaptor_Surface(f)
            if sa.GetType() != GeomAbs_Plane:
                continue
            pl = sa.Plane(); n = pl.Axis().Direction(); p = pl.Location()
            if abs(abs(n.Y()) - 1) > 1e-6 or abs(p.Y()) > 1e-4:
                continue
            ve, _ = hlr(f, N, Vx, defl=0.01)
            pts = np.concatenate(ve) if ve else None
            if pts is None:
                continue
            # order the boundary into a polygon via the face's wire discretization (hlr returns edge pieces)
            from OCP.BRepTools import BRepTools_WireExplorer
            from OCP.BRepTools import BRepTools as BT
            w = BT.OuterWire_s(f); we = BRepTools_WireExplorer(w); ring = []
            while we.More():
                ad = BRepAdaptor_Curve(we.Current()); d = GCPnts_QuasiUniformDeflection(ad, 0.01)
                seg = [(d.Value(j).X(), d.Value(j).Z()) for j in range(1, d.NbPoints() + 1)]
                if we.Current().Orientation() == TopAbs_REVERSED:
                    seg = seg[::-1]
                ring += seg; we.Next()
            if len(ring) > 2:
                ring = np.array(ring)
                sh.ax.add_patch(Polygon(np.c_[ox + s * ring[:, 0], oy + s * ring[:, 1]], closed=True, facecolor="white", edgecolor=INK,
                                        hatch=hatches[i % len(hatches)], lw=LW["thin"] * PT))
        if label in poly:                                    # tessellated: draw only its silhouette and cut face, not the triangle edges
            vis = hlr(cut, N, Vx, defl=0.01)[0] if False else []
        draw_polys(sh, vis, s, ox, oy, "vis")
    sh.line([ox, ox], [oy - 15 * s, oy + 16.5 * s], "cen")
    sh.text(ox, oy + 17.5 * s, "SECTION THROUGH THE HUB AXIS (5:1)", 3.0, ha="center")
    # balloons
    cents = []
    for i, (label, cut) in enumerate(parts):
        _, c = volume(cut); cents.append((c[2], i, c))
    order = sorted(cents, reverse=True)
    for n_, (_, i, c) in enumerate(order):
        label = parts[i][0]
        px, py = ox + s * c[0], oy + s * c[2]
        bx = ox + 100; by = oy + 72 - n_ * 15
        sh.line([px, bx - 4], [py, by], "dim"); sh.ax.add_patch(Circle((px, py), 0.6, facecolor=INK))
        sh.ax.add_patch(Circle((bx, by), 4, facecolor="white", edgecolor=INK, lw=LW["dim"] * PT, zorder=5))
        sh.ax.text(bx, by, str(i + 1), fontsize=FS(2.6), ha="center", va="center", zorder=6)
        sh.text(bx + 6, by - 1.2, label, 2.4)
    zs = []
    for _, cut in parts:
        lo_, hi_ = bbox(cut); zs += [lo_[2], hi_[2]]
    zmin, zmax = min(zs), max(zs)
    sh.dim((ox - 16 * s, oy + zmin * s), (ox - 16 * s, oy + zmax * s), "left", 8, f"{zmax - zmin:.2f}  overall stack")
    n = hub["notes"]
    sh.notes(250, 280, n, h=2.4, width=150)
    sh.title_block({"title": "Ø20 hub stack (v5), section", "dwg": f"EXO-{set_info['key']}-HUB", "design": set_info["design"], "pn": "HUB-v5",
                    "material": "see part list", "mass": "see parts list", "qty": hub["qty"], "finish": "bearing seats unblasted",
                    "scale": "5:1", "sheet": f"{sheet_no} / {n_sheets}", "src": os.path.dirname(os.path.relpath(hub["bearing"], REPO))[-58:]})
    sh.save(pdf, png)


# ------------------------------------------------------------------ sets
TI = ("Ti-6Al-4V (Grade 5)", 4.43)
FIN_TI = "bead blast; mask bores, pins, threads"


def step(dd, pat):
    m = sorted(glob.glob(os.path.join(REPO, "pipeline", "full-exo", "designs", dd, "step", pat)))
    if not m:
        raise SystemExit(f"no STEP matching {pat} in {dd}")
    return m[0]


def set_B():
    dd = "user_pinknee_h1b"; st = lambda p: step(dd, p)
    parts = [
        dict(pn="D8-01", title="Scapula base (J1 upper member)", step=st("29_D8-01*"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Your scapula handler's bracket threads onto the M18×0.5 spigot in place of the dome cap; no tab, no ears.", "5-axis machined."]),
        dict(pn="D8-02", title="Link 1 (J1 to J2)", step=st("18_D8-02*"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["8 × 3 bar section on a line/arc chain, 5-axis machined from solid (bends tighter than the 15 mm bent-bar rule).", "Integral Ø7 pins carry the J1 and J2 bearing pairs."]),
        dict(pn="D8-03", title="Link 2 (J2 to J3)", step=st("19_D8-03*"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["8 × 3 bar section, 5-axis machined to hug the model strap; flies over the knee and the pad.", "J2 and J3 rings carry the bearing housings."]),
        dict(pn="D8-04", title="Member 3 (J3 disc + E strap)", step=st("20_D8-04*"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["E strap 8 × 3 from one side-view sketch of lines and tangent arcs; E boss Ø12 carries integral pin a (Ø4 h9)."]),
        dict(pn="D8-05", title="Knee link", step=st("24_D8-05*"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Flat plate from lines + R1 arcs; Ø5.5 bores take the iglidur sleeves; clip counterbores Ø8 × 0.7.",
                    "Rule since 2026-10-17: rebuild the knee on MR63ZZ pairs (Ø6 J6 housings) with a physical knee stop."]),
        dict(pn="D8-06", title="Arm pad + pad mount + BOTTOM (one part)", step=st("25_D8-06*"), material="7075-T6", rho=2.81,
             finish="clear anodise (never black); pin b hard anodise", qty=1,
             notes=["Your BOTTOM bar, cut square to the arm 3.7 mm distal of pin b and merged with the pad mount; the only one of your parts that is modified.",
                    "Pin b is integral (Ø4 h9)."]),
        dict(pn="D8-07", title="Upper-arm cuff plate", step=st("67_UPPER*"), material="AlSi10Mg (DMLS)", rho=2.67, finish="bead blast", qty=1,
             notes=["One sketch (flat land + inner / outer arcs, both side arcs trimmed clear of the trunk), extruded.", "Fixed to BOTTOM with 6 × M4×6 ISO 10642."]),
    ]
    hubp = [("Base ring (D8-01)", st("29_D8-01*")), ("Link 1 pin (D8-02)", st("18_D8-02*")), ("Bearing MR117-2RS", st("00_J1_bearing_1*")),
            ("Bearing MR117-2RS", st("01_J1_bearing_2*")), ("Outer spacer (17-4PH)", st("02_J1_outer*")), ("Inner spacer (ground)", st("03_J1_inner*")),
            ("Ring nut M7×0.5 (Ti)", st("04_J1_ring*")), ("Dome cap Ø20 (Ti)", st("05_J1_cap*"))]
    hub = dict(bearing=st("00_J1_bearing_1*"), parts=hubp, qty=3, notes=[
        "Same stack at J1, J2 and J3: MR117-2RS pair back to back, shaft Ø7 j5 / housing Ø11 J6, preloaded through the ground inner spacer by the M7×0.5 ring nut.",
        "12.25 mm from the skin-side face to the crown (v5 standard, docs/HARDWARE.md).",
        "Dome cap threads M18×0.5 onto the ring; at J1 your scapula handler's bracket replaces the cap.",
        "Bearings: catalogue MR117-2RS 7 × 11 × 3 (P5 recommended: ring width 0/−40 µm).",
        "Drawn from the J1 hub of the built CAD; section plane through the axis, clipped 15 mm around it."])
    bom = [
        dict(item=1, pn="D8-01", desc="Scapula base (J1 upper member)", qty=1, material="Ti-6Al-4V", source="made", steps=[st("29_D8-01*")]),
        dict(item=2, pn="D8-02", desc="Link 1 (J1 to J2)", qty=1, material="Ti-6Al-4V", source="made", steps=[st("18_D8-02*")]),
        dict(item=3, pn="D8-03", desc="Link 2 (J2 to J3)", qty=1, material="Ti-6Al-4V", source="made", steps=[st("19_D8-03*")]),
        dict(item=4, pn="D8-04", desc="Member 3 (J3 disc + E strap)", qty=1, material="Ti-6Al-4V", source="made", steps=[st("20_D8-04*")]),
        dict(item=5, pn="D8-05", desc="Knee link", qty=1, material="Ti-6Al-4V", source="made", steps=[st("24_D8-05*")]),
        dict(item=6, pn="D8-06", desc="Arm pad + pad mount + BOTTOM", qty=1, material="7075-T6", source="made (your BOTTOM)", steps=[st("25_D8-06*")]),
        dict(item=7, pn="D8-07", desc="Upper-arm cuff plate", qty=1, material="AlSi10Mg", source="made (DMLS)", steps=[st("67_UPPER*")]),
        dict(item=8, pn="H-01", desc="Dome cap Ø20, M18×0.5", qty=3, material="Ti-6Al-4V", source="made (turned)", steps=[st("05_J1_cap*"), st("11_J2_cap*"), st("17_J3_cap*")]),
        dict(item=9, pn="H-02", desc="Hub outer spacer", qty=3, material="17-4PH", source="made (turned)", steps=[st("02_J1_outer*"), st("08_J2_outer*"), st("14_J3_outer*")]),
        dict(item=10, pn="H-03", desc="Hub inner spacer, ground (preload)", qty=3, material="Ti-6Al-4V", source="made (ground)", steps=[st("03_J1_inner*"), st("09_J2_inner*"), st("15_J3_inner*")]),
        dict(item=11, pn="H-04", desc="Hub ring nut M7×0.5", qty=3, material="Ti-6Al-4V", source="made (turned)", steps=[st("04_J1_ring*"), st("10_J2_ring*"), st("16_J3_ring*")]),
        dict(item=12, pn="MR117-2RS", desc="Ball bearing 7 × 11 × 3", qty=6, material="bearing steel", source="catalogue",
             steps=[st("00_*"), st("01_*"), st("06_*"), st("07_*"), st("12_*"), st("13_*")]),
        dict(item=13, pn="GSM-0405-03", desc="iglidur G sleeve 4 × 5.5, faced to 1.89", qty=2, material="iglidur G", source="igus", steps=[]),
        dict(item=14, pn="GTM-0408-005", desc="iglidur thrust washer 4 × 8 × 0.5", qty=2, material="iglidur", source="igus", steps=[]),
        dict(item=15, pn="DIN 6799-3.2", desc="Retaining E-clip (knee pins)", qty=2, material="A2 stainless", source="catalogue", steps=[]),
        dict(item=16, pn="ISO 10642 M4×6", desc="Countersunk screw (cuff plate to BOTTOM)", qty=6, material="A2 stainless", source="catalogue", steps=[]),
    ]
    info = dict(key="B", design="skin-normal-3r-pin-knee H1b", ga_title="Pin knee H1b, general arrangement", mass="178.0 g",
                step_dir=os.path.relpath(os.path.join(REPO, "pipeline/full-exo/designs", dd, "step"), REPO),
                ga_notes=["Right shoulder, rest pose. J1, J2, J3 are the three counted joints (Ø20 hubs, sheet HUB). The two knee pins align the cuff and are not counted; the arm pose sets their angles.",
                          "J1 seats on your scapula handler at the acromion top (bracket on the J1 M18×0.5 spigot).",
                          "UPGRADE 1 (rule 2026-10-17): knee pins on MR63ZZ pairs instead of iglidur: Ø6 J6 housings, pins ISO 8734 Ø3 m6 pressed in Ø3 H7 seats, bearing seats Ø3 j5, e-clip DIN 6799 RS 2.3 (the lead's knee: bosses Ø9 × 5.5, pin stack 9.75). Keep the pin centres: J3 to pin a 59.55, pin a to pin b 28.24 (sheets D8-04, D8-05).",
                          "UPGRADE 2: physical knee stop, knee angle 30.46° to 149.54° (used 103.0° to 147.3°): a tooth on the knee link against the E strap.",
                          "UPGRADE 3: physical J2 stop keeping the J1-J3 axis angle in 32.2° to 104.3° (5° inside the dyad limits 27.24° / 109.28° set by the link angles 41.02° and 68.26°): J2 turned 21.6° to 149.7° from its folded position (J1, J2, J3 axes coplanar, J3 nearest J1), on the branch drawn. At rest the J1-J3 angle is 76.4°. Use a dowel in an arc slot on J2's own angle.",
                          "Verified score 90.11 (gap 27.20), held-out gap 29.12; complexity 0. Bought parts (items 12-16) are listed, not drawn. Generated from the STEP files of the built CAD; status FOR REVIEW."])
    return info, parts, hub, bom


def set_A():
    dd = "user_conecut_knee"; st = lambda p: step(dd, p)
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, "pipeline/full-exo/designs", dd, "step", "*.step")))
    pick = lambda key: st(next(n for n in names if key in n))
    parts = [
        dict(pn="D8-01", title="Scapula base (J1 upper member)", step=pick("D8-01"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Your scapula handler's bracket threads onto the M18×0.5 spigot in place of the dome cap; no tab.", "5-axis machined."]),
        dict(pn="D8-02a", title="Link 1a (J1 to K, flank lug)", step=pick("D8-02a"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["5-axis machined from solid; R2 centre-line bends (tighter than the 15 mm bent-bar rule).", "Flank lug: 4-axis UV wire EDM, profile ±0.02, a-C:H DLC 2-3 µm.",
                    "K pad: two opposed 62.8° stop slots, width 3.10, centre radius 7.75."]),
        dict(pn="D8-02b", title="Link 1b (K to J2, crank pin)", step=pick("D8-02b"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Machined from solid (3+2 axis).", "Crank pivot bore Ø3 H7 for the O3 h5/m6 17-4PH pin; J2 pin carries the 118° q2 stop slot."]),
        dict(pn="D8-03", title="Link 2 (J2 to J3, J3 stop groove)", step=pick("D8-03"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["5-axis / 3+2 machined from solid; 68° drop at J2 (limit 70° on parts machined from solid).",
                    "J3 stop groove under the J3 ring: 2.10 +0.02/0 wide × 1.00 +0.05/0 deep, centre radius 7.500, 250° arc, full R1.05 ends; concentric to the J3 bore within 0.02."]),
        dict(pn="D8-04", title="Member 3 (J3 disc + E strap)", step=pick("D8-04"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["J3 stop dowel through hole Ø2.000 −0.005/0 reamed at r 7.5 (ISO 8734 2 m6 × 5, ground to 3.90).", "E boss Ø12 × 2.75 with the Ø3 H7 seat of knee pin a."]),
        dict(pn="D8-05", title="Knee link (with stop tooth)", step=pick("D8-05"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Two Ø9 × 5.5 bosses, each 2 × MR63ZZ in Ø6 J6 housings with a 0.5 mm shoulder.", "Stop tooth face ±0.02: meets the E strap at knee angle 154.78°."]),
        dict(pn="D8-06", title="Arm pad + pad mount + BOTTOM (one part)", step=pick("D8-06"), material="7075-T6", rho=2.81, finish="clear anodise (never black)", qty=1,
             notes=["Your BOTTOM bar, cut square to the arm 19.8 mm distal of pin b and merged with the pad mount; the only one of your parts that is modified.", "Ø3 H7 seat of knee pin b."]),
        dict(pn="D9-01", title="Drive bell crank", step=pick("D9-01"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["5-axis machined from solid; all bores in one setup ±5 µm.", "Straddle boss Ø10 × 10 with 683ZZ seats Ø7 J6 at both ends; Ø6 tip boss reamed Ø2.495-2.500 for the nose dowel (Loctite 648)."]),
        dict(pn="D9-02", title="Drive lobe ring (cam)", step=pick("D9-02"), material="17-4PH H900", rho=7.8, finish="as wire-EDM, passivate", qty=1,
             notes=["Wire EDM, taper 14.7° along the follower axis; profile r 10.65 → 12.62 (6 three-point arcs), dwell r 10.20.", "Bore Ø20 H7 on the J2 cap skirt (Ø20 g6), keyed by a Ø1 dowel at the onset phase + 0.35° of q2."]),
        dict(pn="H-05", title="K hub cap with spring chamber", step=pick("K_clock-spring_cap"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Crown F+18.25 (6 mm taller than the v5 cap), spring chamber Ø16 × 5.2 with the outer-hook slot, M18×0.5.", "Pinned to link 1b's ring at the spring's preload index."]),
        dict(pn="H-06", title="J2 cap (lobe ring seat)", step=pick("J2_cap"), material=TI[0], rho=TI[1], finish=FIN_TI, qty=1,
             notes=["Crown F+12.25, flat, R0.5 corner; skirt Ø20 g6 carries the lobe ring (D9-02). M18×0.5."]),
        dict(pn="D8-07", title="Upper-arm cuff plate", step=pick("UPPER_ARM_CUFF"), material="AlSi10Mg (DMLS)", rho=2.67, finish="bead blast", qty=1,
             notes=["Fixed to BOTTOM with 6 × M4×6 ISO 10642."]),
    ]
    hubp = [("Base ring (D8-01)", pick("D8-01")), ("Link 1a pin (D8-02a)", pick("D8-02a")), ("Bearing MR117-2RS", pick("00_J1_bearing_1")),
            ("Bearing MR117-2RS", pick("01_J1_bearing_2")), ("Outer spacer (17-4PH)", pick("02_J1_outer")), ("Inner spacer (ground)", pick("03_J1_inner")),
            ("Ring nut M7×0.5 (Ti)", pick("04_J1_ring")), ("Dome cap Ø20 (Ti)", pick("05_J1_cap"))]
    hub = dict(bearing=pick("00_J1_bearing_1"), parts=hubp, qty=4, notes=[
        "Same stack at J1, K, J2 and J3 (K and J2 use their own caps H-05 / H-06): MR117-2RS pair back to back, shaft Ø7 j5 / housing Ø11 J6, preloaded through the ground inner spacer by the M7×0.5 ring nut.",
        "12.25 mm from the skin-side face to the crown (v5 standard, docs/HARDWARE.md).",
        "At J1 your scapula handler's bracket threads onto M18×0.5 in place of the dome cap.",
        "Drawn from the J1 hub of the built CAD; section plane through the axis, clipped 15 mm around it."])
    sel = lambda *keys: [pick(k) for k in keys]
    bom = [
        dict(item=1, pn="D8-01", desc="Scapula base (J1 upper member)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-01")),
        dict(item=2, pn="D8-02a", desc="Link 1a (J1 to K, flank lug)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-02a")),
        dict(item=3, pn="D8-02b", desc="Link 1b (K to J2, crank pin)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-02b")),
        dict(item=4, pn="D8-03", desc="Link 2 (J2 to J3)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-03")),
        dict(item=5, pn="D8-04", desc="Member 3 (J3 disc + E strap)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-04")),
        dict(item=6, pn="D8-05", desc="Knee link with stop tooth", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D8-05")),
        dict(item=7, pn="D8-06", desc="Arm pad + pad mount + BOTTOM", qty=1, material="7075-T6", source="made (your BOTTOM)", steps=sel("D8-06")),
        dict(item=8, pn="D9-01", desc="Drive bell crank", qty=1, material="Ti-6Al-4V", source="made", steps=sel("D9-01")),
        dict(item=9, pn="D9-02", desc="Drive lobe ring (cam)", qty=1, material="17-4PH H900", source="made (wire EDM)", steps=sel("D9-02")),
        dict(item=10, pn="H-05", desc="K hub cap with spring chamber", qty=1, material="Ti-6Al-4V", source="made", steps=sel("K_clock-spring_cap")),
        dict(item=11, pn="H-06", desc="J2 cap (lobe ring seat)", qty=1, material="Ti-6Al-4V", source="made", steps=sel("J2_cap")),
        dict(item=12, pn="H-01..04", desc="Hub cap / spacers / ring nut (sheet HUB)", qty="2+4+4+4", material="Ti / 17-4PH", source="made (turned)",
             steps=[pick(k) for k in ("05_J1_cap", "24_J3_cap", "02_J1_outer", "03_J1_inner", "04_J1_ring")]),
        dict(item=13, pn="D8-07", desc="Upper-arm cuff plate", qty=1, material="AlSi10Mg", source="made (DMLS)", steps=sel("UPPER_ARM_CUFF")),
        dict(item=14, pn="MR117-2RS", desc="Ball bearing 7 × 11 × 3 (hubs)", qty=8, material="bearing steel", source="catalogue", steps=sel("00_J1_bearing_1")),
        dict(item=15, pn="MR63ZZ", desc="Ball bearing 3 × 6 × 2.5 (knee 4, follower 1)", qty=5, material="bearing steel", source="catalogue", steps=[]),
        dict(item=16, pn="683ZZ", desc="Ball bearing 3 × 7 × 3 (crank pivot)", qty=2, material="bearing steel", source="catalogue", steps=[]),
        dict(item=17, pn="ISO 8734", desc="Dowels: knee pins 3×10, stops 3×6 (3), J3 stop 2×5, nose 2.5×6", qty=7, material="440C / hardened", source="catalogue", steps=[]),
        dict(item=18, pn="K spring", desc="Clock spring 0.3 × 5 × 145.6, 1.4310", qty=1, material="spring steel", source="made / spring maker", steps=[]),
        dict(item=19, pn="misc", desc="Pins, shims, e-clips DIN 6799 RS 2.3, wave washer, M4×6 ISO 10642 (6)", qty="–", material="stainless", source="catalogue", steps=[]),
    ]
    info = dict(key="A", design="conecut-knee-knuckle-3r (A chain)", ga_title="Cone-cut pin knee chain, general arrangement", mass="216.1 g",
                step_dir=os.path.relpath(os.path.join(REPO, "pipeline/full-exo/designs", dd, "step"), REPO),
                ga_notes=["Right shoulder, rest pose. This is design A's 3-joint chain (the current 3-joint lead, verified 93.35). J1, J2, J3 are counted joints; K is slaved by the cam drive (D9-01/02) and not counted.",
                          "Design A adds a 4th joint, a cuff relay (Ti shell R80.6 strapped 31 mm above the pad, 14 × 14 T-nut carriage, 0-35°, constant-force coil). The relay is NOT modelled in CAD yet: no drawing exists for it.",
                          "J1 seats on your scapula handler at the acromion top (bracket on the J1 M18×0.5 spigot).",
                          "Bought parts (items 14-19) are listed, not drawn. Status FOR REVIEW."])
    return info, parts, hub, bom


def main():
    key = sys.argv[1].upper() if len(sys.argv) > 1 else "B"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    info, parts, hub, bom = {"A": set_A, "B": set_B}[key]()
    out = os.path.join(REPO, "docs", "drawings", key); os.makedirs(out, exist_ok=True)
    n = len(parts) + 2
    sheets = []
    pdf_path = os.path.join(out, f"{key}_drawings.pdf" if not only else f"{key}_{only}.pdf")
    with PdfPages(pdf_path) as pdf:
        if not only:
            ga_sheet(info, bom, 1, n, pdf, os.path.join(out, "01_GA.png")); sheets.append({"file": "01_GA.png", "title": info["ga_title"]})
            print("GA done", flush=True)
            hub_sheet(info, hub, 2, n, pdf, os.path.join(out, "02_HUB.png")); sheets.append({"file": "02_HUB.png", "title": "Ø20 hub stack, section"})
            print("HUB done", flush=True)
        for i, p in enumerate(parts, 3):
            if only and p["pn"] != only:
                continue
            fn = f"{i:02d}_{p['pn']}.png"
            r = detail_sheet(p, info, i, n, pdf, os.path.join(out, fn)); r["file"] = fn; sheets.append(r)
            print(p["pn"], r, flush=True)
    if not only:
        json.dump({"set": key, "design": info["design"], "pdf": os.path.basename(pdf_path), "sheets": sheets}, open(os.path.join(out, "sheets.json"), "w"), indent=1)
    print("->", pdf_path)


if __name__ == "__main__":
    main()
