"""Dimensions, callouts, datum symbols and feature control frames, every value measured from the B-rep.

Each call takes model-space reference points (from brep.ref / brep.evaluate), projects them through the View, adds a
real ezdxf DIMENSION (value = the projected geometry x DIMLFAC = 1/view scale, so it is computed by the CAD kernel's
geometry, never typed) and records a registry entry {handle, spec, dec} that validate.py re-measures on a freshly
loaded STEP. Text that carries a measured number (callouts, table cells) is registered the same way.

Conventions (ASME Y14.5): unidirectional text, decimals carry the general tolerance (.X +-0.2, .XX +-0.05),
basic dimensions framed, R / Ø prefixes, nX for repeated features.
"""
import math
import numpy as np
from brep import evaluate, unit


def fmt(v, dec):
    s = f"{v:.{dec}f}"
    return "0" if s in ("-0", "-0.0") else s


class Dims:
    def __init__(self, sheet, part):
        self.sh, self.part, self.msp = sheet, part, sheet.msp

    # ------------------------------------------------------------ registry
    def _reg(self, ent, spec, dec, kind="dim", text=None, scale=1.0, angular=False, extra=None):
        v = evaluate(self.part, spec)
        e = dict(handle=ent.dxf.handle, kind=kind, spec=spec, dec=dec, value=v, scale=scale, angular=angular)
        if text is not None: e["text"] = text
        if extra: e.update(extra)
        self.sh.dims.append(e); return v

    def _ov(self, view, dec, basic=False, extra=None):
        o = dict(dimlfac=1.0 / view.scale if view is not None else 1.0, dimdec=dec, dimadec=dec)
        if basic: o["dimgap"] = -1.0                                                       # framed text = basic
        if extra: o.update(extra)
        return o

    def _check(self, measured, spec, what):
        v = evaluate(self.part, spec)
        if abs(measured - v) > 2e-3:
            raise AssertionError(f"{what}: drawn geometry gives {measured:.4f}, the solid {v:.4f} ({spec})")
        return v

    # ------------------------------------------------------------ linear family
    def linear(self, view, pa, pb, spec, at, angle=None, dec=2, text="<>", basic=False, ov=None):
        """distance between model points pa, pb measured along the sheet direction `angle` (deg; default: the
        direction of pb - pa snapped to horizontal/vertical); `at` = a sheet point the dimension line passes through"""
        a, b = view.to_sheet(pa), view.to_sheet(pb)
        if angle is None:
            d = b - a; angle = 0.0 if abs(d[0]) >= abs(d[1]) else 90.0
        u = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
        self._check(abs((b - a) @ u) / view.scale, spec, f"linear {spec.get('kind')}")
        d = self.msp.add_linear_dim(base=tuple(map(float, at)), p1=tuple(map(float, a)), p2=tuple(map(float, b)), angle=angle,
                                    text=text, dimstyle="EXO", override=self._ov(view, dec, basic, ov), dxfattribs=dict(layer="DIM"))
        d.render(); self._reg(d.dimension, spec, dec, scale=view.scale, extra=dict(text_tpl=text)); return d.dimension

    def aligned(self, view, pa, pb, spec, offset, dec=2, text="<>", basic=False, ov=None):
        a, b = view.to_sheet(pa), view.to_sheet(pb)
        self._check(np.linalg.norm(b - a) / view.scale, spec, "aligned")
        d = self.msp.add_aligned_dim(p1=tuple(map(float, a)), p2=tuple(map(float, b)), distance=float(offset), text=text, dimstyle="EXO",
                                     override=self._ov(view, dec, basic, ov), dxfattribs=dict(layer="DIM"))
        d.render(); self._reg(d.dimension, spec, dec, scale=view.scale, extra=dict(text_tpl=text)); return d.dimension

    def radius(self, view, centre, r_model, angle, spec, dec=1, text="<>", location=None, ov=None):
        """radius dimension of an arc seen true size (centre in model space, r_model mm, leader at sheet angle)"""
        c = view.to_sheet(centre); self._check(r_model, spec, "radius")
        kw = dict(location=tuple(map(float, location))) if location is not None else {}
        d = self.msp.add_radius_dim(center=tuple(map(float, c)), radius=float(r_model * view.scale), angle=float(angle), text=text,
                                    dimstyle="EXO", override=self._ov(view, dec, False, dict(dimtmove=0, **(ov or {}))), dxfattribs=dict(layer="DIM"), **kw)
        d.render(); self._reg(d.dimension, spec, dec, scale=view.scale, extra=dict(text_tpl=text)); return d.dimension

    def diameter(self, view, centre, r_model, angle, spec, dec=2, text="<>", location=None, ov=None):
        c = view.to_sheet(centre); self._check(2 * r_model, spec, "diameter")
        kw = dict(location=tuple(map(float, location))) if location is not None else {}
        d = self.msp.add_diameter_dim(center=tuple(map(float, c)), radius=float(r_model * view.scale), angle=float(angle), text=text,
                                      dimstyle="EXO", override=self._ov(view, dec, False, ov), dxfattribs=dict(layer="DIM"), **kw)
        d.render(); self._reg(d.dimension, spec, dec, scale=view.scale, extra=dict(text_tpl=text)); return d.dimension

    def angular(self, view, centre, pa, pb, spec, radius_sheet, dec=1, text="<>", basic=False, ov=None):
        """angle at model point `centre` between the rays to pa and pb (counter-clockwise from pa to pb on the sheet)"""
        c, a, b = view.to_sheet(centre), view.to_sheet(pa), view.to_sheet(pb)
        ang = math.degrees(math.acos(np.clip(unit(a - c) @ unit(b - c), -1, 1))); self._check(ang, spec, "angular")
        mid = unit(unit(a - c) + unit(b - c)); base = c + radius_sheet * mid
        d = self.msp.add_angular_dim_3p(base=tuple(map(float, base)), center=tuple(map(float, c)), p1=tuple(map(float, a)), p2=tuple(map(float, b)),
                                        text=text, dimstyle="EXO", override=self._ov(None, dec, basic, ov), dxfattribs=dict(layer="DIM"))
        d.render(); self._reg(d.dimension, spec, dec, angular=True, extra=dict(text_tpl=text)); return d.dimension

    def ordinate(self, view, p, origin, axis, spec, offset, dec=2, ov=None):
        """ordinate dimension of model point p from datum `origin` along the sheet axis 'x' or 'y'; offset = sheet
        vector from the feature to the leader end"""
        f, o = view.to_sheet(p), view.to_sheet(origin)
        self._check(abs((f - o)[0 if axis == "x" else 1]) / view.scale, spec, "ordinate")
        add = self.msp.add_ordinate_x_dim if axis == "x" else self.msp.add_ordinate_y_dim
        d = add(feature_location=tuple(map(float, f)), offset=tuple(map(float, offset)), origin=tuple(map(float, o)), dimstyle="EXO",
                override=self._ov(view, dec, False, ov), dxfattribs=dict(layer="DIM"))
        d.render(); self._reg(d.dimension, spec, dec, scale=view.scale, extra=dict(signed=False)); return d.dimension

    # ------------------------------------------------------------ text carrying measured values
    def measured_text(self, template, specs, decs, p, h=3.0, align="LEFT", layer="TEXT"):
        """a text whose {} fields are measured values: template.format(*formatted values); registered"""
        vals = [evaluate(self.part, s) for s in specs]; s = template.format(*[fmt(v, d) for v, d in zip(vals, decs)])
        t = self.sh.text(s, p, h, align, layer)
        self.sh.dims.append(dict(handle=t.dxf.handle, kind="text", specs=specs, decs=decs, values=vals, text=s))
        return t, s

    def leader(self, tip, knee, lines, specs=(), decs=(), h=3.0, side=None):
        """leader with an arrow at `tip` (sheet), a knee, a short shoulder and one or more callout lines; any {} in
        the lines takes the next measured value"""
        tip, knee = np.asarray(tip, float), np.asarray(knee, float)
        side = side or (1 if knee[0] >= tip[0] else -1)
        sh_end = knee + np.array([side * 3.0, 0.0])
        self.sh.line(tip, knee, "DIM"); self.sh.line(knee, sh_end, "DIM"); self.arrow(tip, knee - tip)
        vals = [evaluate(self.part, s) for s in specs]; it = iter([fmt(v, d) for v, d in zip(vals, decs)])
        y = sh_end[1] + (len(lines) - 1) * h * 0.8; handles = []; out = []
        for ln in lines:
            s = ln.format(*[next(it) for _ in range(ln.count("{}"))])
            t = self.sh.text(s, (sh_end[0] + side * 1.0, y), h, "ML" if side > 0 else "MR", "DIM"); handles.append(t.dxf.handle); out.append(s)
            y -= h * 1.6
        if specs: self.sh.dims.append(dict(handle=handles, kind="text", specs=list(specs), decs=list(decs), values=vals, text=" | ".join(out)))
        return out

    def arrow(self, tip, direction, size=3.0, width=1.0):
        d = unit(np.asarray(direction, float)); n = np.array([-d[1], d[0]]); tip = np.asarray(tip, float)
        b = tip + size * d
        self.msp.add_solid([tuple(tip), tuple(b + width / 2 * n), tuple(b - width / 2 * n)], dxfattribs=dict(layer="DIM"))

    # ------------------------------------------------------------ GD&T
    def datum(self, letter, foot, direction, length=8.0, size=5.0):
        """datum feature symbol: a filled triangle on the feature at `foot`, a stem along `direction` (sheet) and the
        framed letter"""
        d = unit(np.asarray(direction, float)); n = np.array([-d[1], d[0]]); foot = np.asarray(foot, float)
        self.msp.add_solid([tuple(foot - 1.5 * n), tuple(foot + 1.5 * n), tuple(foot + 2.6 * d)], dxfattribs=dict(layer="DIM"))
        top = foot + length * d; self.sh.line(foot + 2.6 * d, top, "DIM")
        c = top + size / 2 * d
        sq = [c + size / 2 * np.array(v) for v in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.sh.polyline(sq, "DIM", closed=True); self.sh.text(letter, c, 3.5, "MIDDLE", "DIM")

    def fcf(self, at, cells, h=3.0, leader_to=None):
        """feature control frame at sheet point `at` (lower left): cells = [symbol, "0.02", "A", "B"]; symbol is one of
        perp, pos, prof, flat, par, circ, runout, or plain text"""
        x, y = at; H = h + 3.0; xs = x
        for i, c in enumerate(cells):
            w = H if i == 0 else max(H, self.sh.text_width(c, h) + 3.0)
            self.sh.polyline([(xs, y), (xs + w, y), (xs + w, y + H), (xs, y + H)], "DIM", closed=True)
            cc = np.array([xs + w / 2, y + H / 2])
            if i == 0: self.gdt_symbol(c, cc, h)
            else: self.sh.text(c, cc, h, "MIDDLE", "DIM")
            xs += w
        if leader_to is not None:
            self.sh.line((x, y + H / 2), leader_to, "DIM"); self.arrow(leader_to, np.array([x, y + H / 2]) - np.asarray(leader_to))
        return xs, y + H

    def gdt_symbol(self, kind, c, h):
        c = np.asarray(c, float); s = h * 0.5; L = self.sh.line
        if kind == "perp":
            L(c + (-s, -s), c + (s, -s), "DIM"); L(c + (0, -s), c + (0, s), "DIM")
        elif kind == "par":
            L(c + (-s * 0.8, -s), c + (-s * 0.2, s), "DIM"); L(c + (s * 0.2, -s), c + (s * 0.8, s), "DIM")
        elif kind == "flat":
            L(c + (-s * 0.6, -s * 0.7), c + (s * 1.0, -s * 0.7), "DIM"); L(c + (-s * 1.0, s * 0.7), c + (s * 0.6, s * 0.7), "DIM")
            L(c + (-s * 0.6, -s * 0.7), c + (-s * 1.0, s * 0.7), "DIM"); L(c + (s * 1.0, -s * 0.7), c + (s * 0.6, s * 0.7), "DIM")
        elif kind == "pos":
            self.sh.circle(c, s * 0.7, "DIM"); L(c + (-s, 0), c + (s, 0), "DIM"); L(c + (0, -s), c + (0, s), "DIM")
        elif kind == "prof":
            self.sh.arc(c + (0, -s * 0.6), s, 0, 180, "DIM"); L(c + (-s, -s * 0.6), c + (s, -s * 0.6), "DIM")
        elif kind == "circ":
            self.sh.circle(c, s * 0.8, "DIM")
        elif kind == "cyl":
            self.sh.circle(c, s * 0.6, "DIM"); L(c + (-s * 0.9, -s), c + (-s * 0.1, s), "DIM"); L(c + (s * 0.1, -s), c + (s * 0.9, s), "DIM")
        else:
            self.sh.text(kind, c, h, "MIDDLE", "DIM")
