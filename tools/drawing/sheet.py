"""ASME-style A3 landscape sheet in ezdxf: border + zones, title block, tolerance block, notes, revision block,
third-angle symbol; view geometry (exact primitives) on layers; export to DXF R2018 + vector PDF (true A3) + PNG.

Layers and line weights (mm): VISIBLE 0.50, HIDDEN 0.25 (dashed), CENTER 0.25 (chain), TANGENT 0.18 (rounds'
boundaries, thin), DIM 0.18, HATCH 0.18, TEXT 0.25, BORDER 0.70, TITLE 0.35, CUTPLANE 0.70 (phantom).
"""
import math, os, subprocess
import numpy as np
import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment

W, H = 420.0, 297.0
MARGIN = 10.0
LAYERS = {  # name: (lineweight 1/100 mm, linetype, color)
    "VISIBLE": (50, "CONTINUOUS", 7), "HIDDEN": (25, "HIDDEN_MM", 7), "CENTER": (25, "CENTER_MM", 7),
    "TANGENT": (18, "CONTINUOUS", 8), "DIM": (18, "CONTINUOUS", 7), "HATCH": (18, "CONTINUOUS", 7),
    "TEXT": (25, "CONTINUOUS", 7), "BORDER": (70, "CONTINUOUS", 7), "TITLE": (35, "CONTINUOUS", 7),
    "TITLE_THIN": (18, "CONTINUOUS", 7), "CUTPLANE": (70, "PHANTOM_MM", 7), "SKETCH": (25, "CONTINUOUS", 7),
    "CONSTRUCTION": (18, "PHANTOM_MM", 7), "VIEWLABEL": (35, "CONTINUOUS", 7),
}
FONT = "LiberationSans-Regular.ttf"


def new_doc():
    doc = ezdxf.new("R2018", setup=True, units=4)                                         # mm
    doc.header["$MEASUREMENT"] = 1; doc.header["$LTSCALE"] = 1.0; doc.header["$PSLTSCALE"] = 0
    lt = doc.linetypes
    if "HIDDEN_MM" not in lt: lt.add("HIDDEN_MM", pattern=[4.5, 3.0, -1.5], description="Hidden __ __ __ (3 mm dash, 1.5 gap)")
    if "CENTER_MM" not in lt: lt.add("CENTER_MM", pattern=[21.0, 15.0, -1.5, 3.0, -1.5], description="Center ____ _ ____ _")
    if "PHANTOM_MM" not in lt: lt.add("PHANTOM_MM", pattern=[22.5, 15.0, -1.5, 1.5, -1.5, 1.5, -1.5], description="Phantom ____ _ _ ____")
    for n, (lw, ltn, c) in LAYERS.items():
        doc.layers.add(n, color=c, linetype=ltn, lineweight=lw)
    st = doc.styles.get("Standard"); st.dxf.font = FONT
    if "EXO" not in doc.styles: doc.styles.add("EXO", font=FONT)
    ds = doc.dimstyles.new("EXO") if "EXO" not in doc.dimstyles else doc.dimstyles.get("EXO")
    for k, v in dict(dimtxt=3.0, dimasz=3.0, dimexe=1.5, dimexo=1.0, dimgap=1.0, dimdec=2, dimadec=1, dimtdec=2,
                     dimdsep=ord("."), dimzin=0, dimazin=0, dimtih=1, dimtoh=1, dimtad=0, dimjust=0, dimclrd=0,
                     dimclre=0, dimclrt=0, dimlwd=18, dimlwe=18, dimtxsty="EXO", dimtofl=1, dimatfit=3, dimtmove=0,
                     dimlunit=2, dimaunit=0, dimcen=0, dimscale=1.0, dimlfac=1.0, dimblk="", dimsah=0).items():
        ds.set_dxf_attrib(k, v)
    return doc


class Sheet:
    """one drawing sheet (one DXF modelspace in paper millimetres, origin at the sheet's lower left corner)"""

    def __init__(self, info, n, of):
        self.doc = new_doc(); self.msp = self.doc.modelspace(); self.info = dict(info); self.n, self.of = n, of
        self.dims = []                                                                      # registry for validate.py
        self.notes_y = None
        self.frame()

    # ------------------------------------------------------------ primitives
    def line(self, a, b, layer="VISIBLE", **kw):
        return self.msp.add_line(tuple(map(float, a)), tuple(map(float, b)), dxfattribs=dict(layer=layer, **kw))

    def polyline(self, pts, layer="VISIBLE", closed=False):
        return self.msp.add_lwpolyline([tuple(map(float, p[:2])) for p in pts], close=closed, dxfattribs=dict(layer=layer))

    def circle(self, c, r, layer="VISIBLE"):
        return self.msp.add_circle(tuple(map(float, c)), float(r), dxfattribs=dict(layer=layer))

    def arc(self, c, r, a0, a1, layer="VISIBLE"):
        return self.msp.add_arc(tuple(map(float, c)), float(r), float(a0), float(a1), dxfattribs=dict(layer=layer))

    def text(self, s, p, h=3.0, align="LEFT", layer="TEXT", rot=0.0, bold=False):
        al = {"LEFT": TextEntityAlignment.BOTTOM_LEFT, "CENTER": TextEntityAlignment.BOTTOM_CENTER,
              "RIGHT": TextEntityAlignment.BOTTOM_RIGHT, "MIDDLE": TextEntityAlignment.MIDDLE_CENTER,
              "ML": TextEntityAlignment.MIDDLE_LEFT, "MR": TextEntityAlignment.MIDDLE_RIGHT,
              "TL": TextEntityAlignment.TOP_LEFT, "TC": TextEntityAlignment.TOP_CENTER}[align]
        t = self.msp.add_text(s, height=h, rotation=rot, dxfattribs=dict(layer=layer, style="EXO"))
        t.set_placement(tuple(map(float, p)), align=al); return t

    def text_width(self, s, h=3.0):
        from ezdxf.fonts import fonts
        try: return fonts.make_font(FONT, h).text_width(s)
        except Exception: return 0.6 * h * len(s)

    def add_prims(self, prims):
        """exact view primitives (views.py) -> DXF entities. Visible after hidden so a visible edge wins on top"""
        order = {"HIDDEN": 0, "TANGENT": 1, "CENTER": 2, "VISIBLE": 3}
        for layer, pr in sorted(prims, key=lambda q: order.get(q[0], 4)):
            k = pr[0]; a = dict(layer=layer)
            if k == "line": self.msp.add_line(tuple(pr[1]), tuple(pr[2]), dxfattribs=a)
            elif k == "circle": self.msp.add_circle(tuple(pr[1]), pr[2], dxfattribs=a)
            elif k == "arc": self.msp.add_arc(tuple(pr[1]), pr[2], pr[3], pr[4], dxfattribs=a)
            elif k == "ellipse":
                c, M, ratio, t0, t1 = pr[1:]
                self.msp.add_ellipse((*c, 0), (*M, 0), ratio, t0, t1, dxfattribs=a)
            elif k == "spline":
                deg, ctrl, knots, w = pr[1:]
                sp = self.msp.add_open_spline([(*p, 0) for p in ctrl], degree=deg, knots=knots, dxfattribs=a)
                if w is not None: sp.weights = list(w); sp.dxf.flags = sp.dxf.flags | 4    # rational
            elif k == "poly":
                self.msp.add_lwpolyline([tuple(p) for p in pr[1]], dxfattribs=a)

    def hatch(self, loops, scale=1.0, angle=0.0, pattern="ANSI31"):
        h = self.msp.add_hatch(dxfattribs=dict(layer="HATCH"))
        h.set_pattern_fill(pattern, scale=scale, angle=angle)
        for i, lp in enumerate(loops):
            h.paths.add_polyline_path([(x, y, b) for x, y, b in lp], is_closed=True, flags=1 if i == 0 else 0)
        return h

    # ------------------------------------------------------------ centre lines / marks
    def centre_mark(self, c, r, ext=3.0, small=1.5, angle=0.0):
        """ASME centre mark: a small cross at the centre + centre lines extending ext beyond the circle"""
        c = np.asarray(c, float)
        for a in (angle, angle + 90):
            u = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
            self.line(c - small * u, c + small * u, "CENTER" if False else "DIM")
            if r + ext > small + 2:
                self.line(c + (small + 1.5) * u, c + (r + ext) * u, "CENTER"); self.line(c - (small + 1.5) * u, c - (r + ext) * u, "CENTER")

    def centre_line(self, a, b, layer="CENTER"):
        return self.line(a, b, layer)

    # ------------------------------------------------------------ frame
    def frame(self):
        m = MARGIN; msp = self.msp
        msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs=dict(layer="TITLE_THIN"))    # trim line
        msp.add_lwpolyline([(m, m), (W - m, m), (W - m, H - m), (m, H - m)], close=True, dxfattribs=dict(layer="BORDER"))
        # zones: 8 columns numbered right to left, 6 rows lettered bottom to top (ASME Y14.1)
        nc, nr = 8, 6; cw, rh = (W - 2 * m) / nc, (H - 2 * m) / nr
        for i in range(1, nc):
            x = m + i * cw; self.line((x, m - 5), (x, m), "TITLE_THIN"); self.line((x, H - m), (x, H - m + 5), "TITLE_THIN")
        for j in range(1, nr):
            y = m + j * rh; self.line((m - 5, y), (m, y), "TITLE_THIN"); self.line((W - m, y), (W - m + 5, y), "TITLE_THIN")
        for i in range(nc):
            x = W - m - (i + 0.5) * cw
            self.text(str(i + 1), (x, m / 2), 3.0, "MIDDLE"); self.text(str(i + 1), (x, H - m / 2), 3.0, "MIDDLE")
        for j in range(nr):
            y = m + (j + 0.5) * rh; L = "ABCDEF"[j]
            self.text(L, (m / 2, y), 3.0, "MIDDLE"); self.text(L, (W - m / 2, y), 3.0, "MIDDLE")
        for x, y in ((W / 2, m), (W / 2, H - m), (m, H / 2), (W - m, H / 2)):                       # centring marks
            d = np.array([0, 1]) if y in (m, H - m) else np.array([1, 0]); s = 1 if (y == m or x == m) else -1
            self.line((x, y), np.array([x, y]) - s * 5 * d, "BORDER")
        self.title_block(); self.revision_block()

    def zone_of(self, p):
        m = MARGIN; nc, nr = 8, 6; cw, rh = (W - 2 * m) / nc, (H - 2 * m) / nr
        col = int((W - m - p[0]) // cw) + 1; row = "ABCDEF"[min(nr - 1, max(0, int((p[1] - m) // rh)))]
        return f"{row}{min(nc, max(1, col))}"

    def _cell(self, x0, y0, x1, y1, label, value, hv=3.5, layer="TITLE"):
        self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs=dict(layer="TITLE_THIN"))
        if label: self.text(label, (x0 + 1.0, y1 - 1.0), 1.8, "TL")
        if value is not None:
            hv = min(hv, (y1 - y0) - 3.2)
            while hv > 1.8 and self.text_width(value, hv) > (x1 - x0) - 2.5: hv -= 0.1
            self.text(value, (x0 + 1.5, y0 + 1.0), hv, "LEFT")

    def title_block(self):
        """ASME Y14.1-like title block, lower right: 180 x 62 mm"""
        I = self.info; x1, y0 = W - MARGIN, MARGIN; x0 = x1 - 180.0; y1 = y0 + 62.0
        self.msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs=dict(layer="TITLE"))
        # left column (68 wide): tolerance block + projection
        xa = x0 + 68.0
        self.msp.add_lwpolyline([(x0, y0 + 22), (xa, y0 + 22), (xa, y1), (x0, y1)], close=True, dxfattribs=dict(layer="TITLE_THIN"))
        tol = ["UNLESS OTHERWISE SPECIFIED:", "DIMENSIONS ARE IN MILLIMETERS", "TOLERANCES:", "  LINEAR  X  ±0.5   .X  ±0.2   .XX  ±0.05",
               "  ANGULAR  ±0.5°", "  BREAK EDGES 0.2 MAX UNLESS NOTED", "INTERPRET PER ASME Y14.5-2018", "SURFACE ROUGHNESS Ra 1.6 µm MAX"]
        for i, s in enumerate(tol): self.text(s, (x0 + 1.5, y1 - 2.0 - i * 4.75), 2.3 if i else 2.4, "TL")
        self._cell(x0, y0 + 11, xa, y0 + 22, "THIRD ANGLE PROJECTION", None)
        self.third_angle_symbol((x0 + 46, y0 + 15.5), 1.0)
        self._cell(x0, y0, x0 + 34, y0 + 11, "DRAWN", I.get("drawn", "Claude (agent)"), 2.6)
        self._cell(x0 + 34, y0, xa, y0 + 11, "DATE", I.get("date", "2026-10-15"), 2.6)
        # right part (112 wide)
        self._cell(xa, y1 - 12, x1, y1, "COMPANY", I.get("company", "exo-shoulder"), 5.0)
        self._cell(xa, y1 - 26, x1, y1 - 12, "TITLE", I["title"], 3.6)
        self._cell(xa, y1 - 36, xa + 56, y1 - 26, "MATERIAL", I["material"], 3.0)
        self._cell(xa + 56, y1 - 36, x1, y1 - 26, "FINISH", I["finish"], 2.5)
        self._cell(xa, y0 + 11, xa + 16, y1 - 36, "SIZE", "A3", 3.5)
        self._cell(xa + 16, y0 + 11, xa + 76, y1 - 36, "DWG NO / PART NO", I["part_no"], 5.0)
        self._cell(xa + 76, y0 + 11, x1, y1 - 36, "REV", I.get("rev", "A"), 5.0)
        self._cell(xa, y0, xa + 30, y0 + 11, "SCALE", I.get("scale", "1:1"), 3.0)
        self._cell(xa + 30, y0, xa + 58, y0 + 11, "MASS", I["mass"], 3.0)
        self._cell(xa + 58, y0, xa + 80, y0 + 11, "UNITS", "mm", 3.0)
        self._cell(xa + 80, y0, x1, y0 + 11, "SHEET", f"{self.n} OF {self.of}", 3.0)
        self.tb_top = y1

    def third_angle_symbol(self, c, s=1.0):
        """ISO 128 / ASME third-angle symbol: truncated cone side view (left) + end view circles (right)"""
        cx, cy = c; d1, d2, L = 10 * s, 5 * s, 10 * s
        x0 = cx - 13 * s
        self.polyline([(x0, cy - d2 / 2), (x0 + L, cy - d1 / 2), (x0 + L, cy + d1 / 2), (x0, cy + d2 / 2)], "TITLE", closed=True)
        self.line((x0 - 2 * s, cy), (x0 + L + 2 * s, cy), "CENTER")
        xc = cx + 6 * s
        self.circle((xc, cy), d1 / 2, "TITLE"); self.circle((xc, cy), d2 / 2, "TITLE")
        self.line((xc - d1 / 2 - 1.5 * s, cy), (xc + d1 / 2 + 1.5 * s, cy), "CENTER"); self.line((xc, cy - d1 / 2 - 1.5 * s), (xc, cy + d1 / 2 + 1.5 * s), "CENTER")

    def revision_block(self):
        I = self.info; x1, y1 = W - MARGIN, H - MARGIN; x0 = x1 - 160.0; hh = 6.0
        cols = [(x0, 12, "REV"), (x0 + 12, 98, "DESCRIPTION"), (x0 + 110, 25, "DATE"), (x0 + 135, 25, "APPROVED")]
        self.msp.add_lwpolyline([(x0, y1), (x1, y1), (x1, y1 - 3 * hh), (x0, y1 - 3 * hh)], close=True, dxfattribs=dict(layer="TITLE"))
        self.text("REVISIONS", ((x0 + x1) / 2, y1 - hh / 2), 3.0, "MIDDLE")
        self.line((x0, y1 - hh), (x1, y1 - hh), "TITLE_THIN"); self.line((x0, y1 - 2 * hh), (x1, y1 - 2 * hh), "TITLE_THIN")
        for x, w, t in cols:
            if x > x0: self.line((x, y1 - hh), (x, y1 - 3 * hh), "TITLE_THIN")
            self.text(t, (x + w / 2, y1 - 1.5 * hh), 2.5, "MIDDLE")
        row = I.get("revisions", [("A", "INITIAL RELEASE", I.get("date", "2026-10-15"), "-")])
        for i, r in enumerate(row[:1]):
            for (x, w, _), s in zip(cols, r):
                h = 2.5
                while h > 1.6 and self.text_width(s, h) > w - 2: h -= 0.1
                self.text(s, (x + w / 2, y1 - 2.5 * hh), h, "MIDDLE")
        self.rev_bottom = y1 - 3 * hh

    def notes(self, lines, x, y_top, h=2.6, width=None, title="NOTES:"):
        """numbered notes block; lines are strings (wrapped at width mm)"""
        self.text(title, (x, y_top), 3.0, "TL"); y = y_top - 5.0
        for i, s in enumerate(lines):
            pre = f"{i + 1}." if not s.startswith("  ") else ""
            words = s.strip().split(); cur = ""; first = True
            wrapped = []
            for w_ in words:
                t = (cur + " " + w_).strip()
                if width and self.text_width(t, h) > width - 6: wrapped.append(cur); cur = w_
                else: cur = t
            wrapped.append(cur)
            for j, s2 in enumerate(wrapped):
                if j == 0 and pre: self.text(pre, (x, y), h, "TL")
                self.text(s2, (x + 5.0, y), h, "TL"); y -= h * 1.55
            y -= 0.6
        return y

    def view_label(self, name, p, scale=None, h=3.5):
        self.text(name, p, h, "TC", layer="VIEWLABEL")
        if scale: self.text(f"SCALE {scale}", (p[0], p[1] - h - 1.5), 2.6, "TC")

    # ------------------------------------------------------------ export
    def save(self, base, png_dpi=200):
        """base.dxf + base.svg (intermediate) -> base.pdf (vector, true A3) + base.png"""
        os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
        self.doc.set_modelspace_vport(height=H, center=(W / 2, H / 2))
        self.doc.saveas(base + ".dxf")
        svg = render_svg(self.doc)
        with open(base + ".svg", "w") as f: f.write(svg)
        import cairosvg
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=base + ".pdf")
        cairosvg.svg2png(bytestring=svg.encode(), write_to=base + ".png", output_width=int(W / 25.4 * png_dpi),
                         output_height=int(H / 25.4 * png_dpi), background_color="white")
        os.remove(base + ".svg")
        return base


def render_svg(doc):
    from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config
    ctx = RenderContext(doc)
    cfg = config.Configuration(lineweight_policy=config.LineweightPolicy.ABSOLUTE, lineweight_scaling=1.0,
                               color_policy=config.ColorPolicy.BLACK, background_policy=config.BackgroundPolicy.WHITE,
                               hatch_policy=config.HatchPolicy.NORMAL, line_policy=config.LinePolicy.ACCURATE,
                               max_flattening_distance=0.005, min_lineweight=0.13, text_policy=config.TextPolicy.FILLING)
    be = svg.SVGBackend()
    Frontend(ctx, be, config=cfg).draw_layout(doc.modelspace(), finalize=True)
    page = layout.Page(W, H, layout.Units.mm, margins=layout.Margins.all(0))
    st = layout.Settings(fit_page=False, scale=1.0, page_alignment=layout.PageAlignment.BOTTOM_LEFT, max_stroke_width=0.01,
                         min_stroke_width=0.0001, fixed_stroke_width=0.15)
    from ezdxf.math import BoundingBox2d
    return be.get_string(page, settings=st, render_box=BoundingBox2d([(0, 0), (W, H)]))


def concat_pdfs(paths, out):
    """merge per-sheet PDFs into one document (pypdf if present, else ghostscript / pdfunite)"""
    try:
        from pypdf import PdfWriter
        w = PdfWriter()
        for p in paths: w.append(p)
        with open(out, "wb") as f: w.write(f)
        return out
    except ImportError: pass
    for cmd in (["pdfunite", *paths, out], ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", f"-sOutputFile={out}", *paths]):
        try: subprocess.run(cmd, check=True, capture_output=True); return out
        except Exception: continue
    raise RuntimeError("no PDF merger (pypdf, pdfunite or gs)")
