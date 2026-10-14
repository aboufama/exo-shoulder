"""Real CAD for a band-searched shoulder design, to the user's standards.

  - v3 bearing internals at every joint, unchanged: integral Ø10 h9 pin with DIN 509 relief on the lower member, 2x igus
    GTM-1018-010 (washer A under, washer B over the upper member), igus GSM-1012-05 flush in a Ø12 H7 bore of the upper
    member, 0.02 mm float, Ø20 G2 dome cap (no flat land) clamped by an M4x6 ultra-low-profile screw.
  - thin variant of the stack (as the designs were scored): lower plate 3.5 mm under its flat washer seat, upper hub 5.05 mm
    between its seats (sleeve flush), links 4.0 mm; Ø26 hubs.
  - links: one G2 ThruSections loft tip to tip (G2 rounded-rectangle sections), Ti-6Al-4V; the skin side of every lower
    member's hub is 3D-contoured to the fitted envelope (only the washer seat on top is flat); the base (scapula-fixed) gets an
    axisymmetric (turned) contour and a mounting tab with 2x M3.
  - arm end (stage 2): BOTTOM = the user's bar (cut where it was cut before) + a bolted, machinable hub block carrying the
    tilted JN pin (or, with the sliding cuff, an arm-fixed curved guide rail and a sliding carriage).
Members are built in their own frames (the viewer's convention: x = start pin, end pin at angle theta in xy).

    python3 build_band_cad.py <key: 4c_best | 5r_thin | 4r_thin> [stage=1]
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
from scipy.interpolate import RBFInterpolator, UnivariateSpline
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, ".."); EXO = os.path.join(CONF, "..")
sys.path.insert(0, CONF); sys.path.insert(0, os.path.join(EXO, "shoulder-d4"))
import cad_helpers as CH
import g2cad as G
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax1

KEY = sys.argv[1]; STAGE = int(sys.argv[2]) if len(sys.argv) > 2 else 1
R = json.load(open(os.path.join(HERE, "inputs", f"{KEY}.json")))["results"][0]
OUT = os.path.join(HERE, f"out_{KEY}"); os.makedirs(OUT, exist_ok=True)
N = R["n"]; A = [x * math.pi / 180 for x in R["a"]]; D2R = math.pi / 180
HUB_R = float(R.get("hub_r", 13.0)); CH.HUB_R = HUB_R; HW = CH.HW
STACK = float(R.get("stack", 4.5)); T_W = 1.0; T_LO = STACK - T_W; T_LINK = float(R.get("t_link", 4.0)); T_SEAT = 5.05; T_BOT = 6.5
PIN_D, SLV_OD = 10.0, 12.0; CAP_R, CAP_H = 10.0, 2.5; R_REF = 65.0; E_EDGE = 1.2
h = np.array(R["h"]); sizes = R["sizes"]; kind = np.array(R["kind"]); off = np.r_[0, np.cumsum(sizes)]
IS_LOW = np.array(R["is_low"], bool); FACES = {int(k): v for k, v in R["faces"].items() if k.isdigit()}
LOWER = {int(k): v for k, v in R["lower"].items()}; ZJ4 = float(R["zj4"])
unit = CH.unit; V = CH.V

def member_samples(mi):
    s = slice(int(off[mi]), int(off[mi + 1]))
    return np.array(R["dirs_local"][mi]), h[s], kind[s], IS_LOW[s]

def hub_axis(mi, end):
    """axis of member mi's hub at its start (end=0) / end (end=1) pin, in the member frame"""
    if mi == 0: return np.array([1.0, 0, 0])
    th = A[mi - 1]; return np.array([1.0, 0, 0]) if end == 0 else np.array([math.cos(th), math.sin(th), 0.0])

def joint_of(mi, end): return mi if (mi > 0 and end == 0) else (mi + 1 if mi > 0 else 1)

def plate_role(mi, end):
    """(z0 = skin-side face along the hub axis, plate thickness, lower?) of member mi's hub at that end"""
    J = joint_of(mi, end)
    if J == N: return ZJ4 + T_BOT + T_W, T_SEAT, False                 # link N-1 sits on the arm-end lower member
    if LOWER[J] == mi: return FACES[J], T_LO, True
    return FACES[J] + STACK, T_SEAT, False

def contour_field(mi, end, axis, d, lat, axisym=False):
    """depth below the flat face (>= 0) of a lower hub's skin side, f(x along d, y along lat). Bounded polar interpolation of
    the fitted samples (centre, ring 0.55 R, ring R - 1.5): periodic in angle within a ring, monotone cubic in radius, held
    to the rim, faded to 0 over the first 3 mm of the stub. axisym: one depth per ring (the shallowest = safe), turned."""
    from scipy.interpolate import PchipInterpolator
    dl, hm, kd, il = member_samples(mi); kk = 1 if (mi > 0 and end == 0) else 2
    idx = np.nonzero(kd == kk)[0]; P = dl[idx] * hm[idx][:, None]; F = plate_role(mi, end)[0]
    dep = np.clip(F - P @ axis, 0.0, 12.0); X, Y = P @ d, P @ lat; rr = np.hypot(X, Y); ph = np.arctan2(Y, X)
    rings = [np.arange(0, 1), np.arange(1, 9), np.arange(9, 21)]; rv = [0.0, float(rr[rings[1]].mean()), float(rr[rings[2]].mean())]
    def ring_val(k, phi):
        ix = rings[k]
        if len(ix) == 1 or axisym: return np.full_like(phi, float(dep[ix].min()) if axisym else float(dep[ix][0]))
        o = np.argsort(ph[ix]); pp = np.r_[ph[ix][o] - 2 * np.pi, ph[ix][o], ph[ix][o] + 2 * np.pi]; dd = np.tile(dep[ix][o], 3)
        return np.interp(phi, pp, dd)
    def f(x, y):
        x = np.atleast_1d(np.asarray(x, float)); y = np.atleast_1d(np.asarray(y, float)); r_ = np.hypot(x, y); phi = np.arctan2(y, x)
        vals = np.stack([ring_val(k, phi) for k in range(3)], 1); out = np.empty(len(r_))
        for i_ in range(len(r_)):
            out[i_] = float(PchipInterpolator(rv, vals[i_])(min(r_[i_], rv[2])))
        fade = np.clip((HUB_R + 3.0 - r_) / 3.0, 0, 1) * np.where(r_ <= HUB_R, 1.0, 1.0)
        return np.clip(out, 0.0, 12.0) * fade
    return f

def section_pts(c, acr, up, wd, tp, depth_fn=None, x_plate=0.0):
    """G2 rounded-rectangle section (width wd, thickness tp) centred at c; optional contoured skin side: the bottom is
    pushed down (-up) by depth_fn(x_plate, y), faded to 0 over the edge rounds so the G2 corners survive"""
    ec = min(E_EDGE, wd / 2 - 0.1, tp / 2 - 0.1)
    prof = CH.section_outline(wd, tp, max(0.2, ec), n=120)
    if depth_fn is not None:
        y2, z2 = prof[:, 0], prof[:, 1]
        dep = np.asarray(depth_fn(np.full(len(y2), x_plate), y2)).reshape(-1)
        wy = np.clip((wd / 2 - np.abs(y2)) / max(ec * 1.5, 0.3), 0, 1); wz = np.clip((-z2) / (tp / 2), 0, 1) ** 2
        wy = wy * wy * (3 - 2 * wy)
        prof = np.c_[y2, z2 - dep * wy * wz]
    pts = c + np.outer(prof[:, 0], acr) + np.outer(prof[:, 1], up)
    q = pts - c; i0 = int(np.argmax(q @ acr + 0.3 * (q @ up))); return np.roll(pts, -i0, 0)

def loft(sections):
    ths = BRepOffsetAPI_ThruSections(True, False, 1e-6); ths.CheckCompatibility(False)
    for pts in sections: ths.AddWire(G.wire([BRepBuilderAPI_MakeEdge(G._periodic_curve(pts, G._shift())).Edge()]))
    ths.Build(); body = cq.Shape.cast(ths.Shape())
    if hasattr(body, "Solids") and body.Solids(): body = body.Solids()[0]
    return body

def plate_sections(axis, d, lat, z0, tp, depth_fn, x0, x1, stub, nx=19):
    """sections across a hub plate (flat top at z0 + tp) from x0 to x1 along d; planform = disc HUB_R + strip HW (G2 waist)"""
    u = np.linspace(0, 1, nx); xs = x0 + (x1 - x0) * (0.5 - 0.5 * np.cos(np.pi * u)); out = []
    for x in xs:
        hw_ = max(CH.planform_halfwidth(x), 0.6); c = axis * (z0 + tp / 2) + x * d             # disc + strip toward the ribbon (G2 waist)
        out.append(section_pts(c, lat, axis, 2 * hw_, tp, depth_fn, x))
    return out

def build_link_short(mi):
    """links whose two hubs overlap (arc x radius < 2 HUB_R + 8): one loft across both hubs. Inside each washer-seat zone
    (r <= 9.6 + 1 from its pin) the sections lie exactly in that hub's plane; between the zones plane, height and
    thickness blend (smoothstep); planform = union of the two discs with a G2 waist"""
    th = A[mi - 1]; a = np.array([1.0, 0, 0]); b = np.array([math.cos(th), math.sin(th), 0.0]); LAT = np.array([0, 0, 1.0])
    (zA, tA, lowA), (zB, tB, lowB) = plate_role(mi, 0), plate_role(mi, 1)
    dA = unit(b - (b @ a) * a); dB = unit(a - (a @ b) * b)
    dist = th * 0.5 * (zA + zB + 0.5 * (tA + tB))
    latA, latB = unit(LAT - (LAT @ a) * a), unit(LAT - (LAT @ b) * b)
    depA = contour_field(mi, 0, a, dA, latA) if lowA else None
    depB = contour_field(mi, 1, b, dB, latB) if lowB else None
    seat = 10.6; x0, x1 = min(seat, dist / 2 - 0.5), max(dist - seat, dist / 2 + 0.5)
    def hw(x):
        hA = math.sqrt(max(HUB_R ** 2 - x ** 2, 0)); hB = math.sqrt(max(HUB_R ** 2 - (x - dist) ** 2, 0)); hmax, hmin = max(hA, hB), min(hA, hB)
        k = 5.0; return hmax + (max(0.0, k - (hmax - hmin)) ** 3 / (6 * k * k) if hmin > 0 else 0.0)
    xs = -HUB_R + 0.04 + (dist + 2 * HUB_R - 0.08) * (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, 31)))
    secs = []
    for x in xs:
        w = float(np.clip((x - x0) / max(x1 - x0, 1e-3), 0, 1)); w = w * w * (3 - 2 * w)
        cA = a * (zA + tA / 2) + x * dA; cB = b * (zB + tB / 2) + (dist - x) * dB
        up = unit((1 - w) * a + w * b); c = (1 - w) * cA + w * cB; lat = unit((1 - w) * latA + w * latB); lat = unit(lat - (lat @ up) * up)
        tp = (1 - w) * tA + w * tB
        if depA is not None or depB is not None:
            fA = depA if depA is not None else (lambda xx, yy: np.zeros(len(np.atleast_1d(yy))))
            fB = depB if depB is not None else (lambda xx, yy: np.zeros(len(np.atleast_1d(yy))))
            dep = (lambda xx, yy, w=w, x=x: (1 - w) * np.asarray(fA(np.full(len(np.atleast_1d(yy)), x), yy)).reshape(-1) + w * np.asarray(fB(np.full(len(np.atleast_1d(yy)), dist - x), yy)).reshape(-1))
        else: dep = None
        secs.append(section_pts(c, lat, up, 2 * max(hw(x), 0.8), tp, dep, x))
    return loft(secs), dict(zA=zA, tA=tA, lowA=lowA, zB=zB, tB=tB, lowB=lowB)

def build_link(mi):
    """one loft tip to tip: plate A (start hub) -> ribbon through the fitted underside -> plate B (end hub)"""
    th = A[mi - 1]; a = np.array([1.0, 0, 0]); b = np.array([math.cos(th), math.sin(th), 0.0]); LAT = np.array([0, 0, 1.0])
    if th * 0.5 * (plate_role(mi, 0)[0] + plate_role(mi, 1)[0]) < 2 * HUB_R + 8.0: return build_link_short(mi)
    dl, hm, kd, il = member_samples(mi)
    rib = np.nonzero(kd == 0)[0]; st = rib.reshape(-1, 3)
    s_ = np.arctan2(dl[st[:, 1], 1], dl[st[:, 1], 0]) / th
    rows = {w: (s_, hm[st[:, j]]) for j, w in enumerate((-HW, 0.0, HW))}
    sp = lambda s, y: UnivariateSpline(s, y, k=min(3, len(s) - 1), s=2.0 * len(s))
    fL, fC, fR = sp(*rows[-HW]), sp(*rows[0.0]), sp(*rows[HW])
    lift = max(0.0, float(max((rows[w][1] - f(rows[w][0])).max() for w, f in ((-HW, fL), (0.0, fC), (HW, fR)))))
    def h_at(s, w):
        c, l, r_ = float(fC(s)) + lift, float(fL(s)) + lift, float(fR(s)) + lift; base = max(c, (l + r_) / 2); tilt = (r_ - l) / 2
        return base + tilt * w / HW + max(0.0, max(l - (base - tilt), r_ - (base + tilt)))
    (zA, tA, lowA), (zB, tB, lowB) = plate_role(mi, 0), plate_role(mi, 1); t = T_LINK
    dA = unit(b - (b @ a) * a); dB = unit(a - (a @ b) * b)
    xj = HUB_R + 7.0
    sA = xj / (zA + tA / 2) / th; sB = 1 - xj / (zB + tB / 2) / th
    uA = zA + (tA - t) / 2; uB = zB + (tB - t) / 2; R_m = 0.5 * (zA + zB); slope = math.tan(math.radians(32)); kk = 2.5
    def H(s, w=0.0):
        env = h_at(s, w); rA = uA - slope * max(0.0, (s - sA) * th * R_m); rB = uB - slope * max(0.0, (sB - s) * th * R_m)
        v = np.array([env, rA, rB]); m = v.max(); return float(m + kk * math.log(np.exp((v - m) / kk).sum()))
    def dir_at(s): ang = s * th; return np.array([math.cos(ang), math.sin(ang), 0.0])
    depA = contour_field(mi, 0, a, dA, unit(LAT - (LAT @ a) * a)) if lowA else None
    depB = contour_field(mi, 1, b, dB, unit(LAT - (LAT @ b) * b)) if lowB else None
    secs = plate_sections(a, dA, unit(LAT - (LAT @ a) * a), zA, tA, depA, -HUB_R + 0.04, HUB_R - 0.04, False)
    secs += [section_pts(a * (zA + tA / 2) + x * dA, unit(LAT - (LAT @ a) * a), a, 2 * max(CH.planform_halfwidth(x), 0.6), tA, depA, x) for x in np.linspace(HUB_R + 1.2, xj, 5)]
    for s in np.linspace(sA, sB, 22)[1:-1]:
        w0 = dir_at(s); C = w0 * (H(s) + t / 2); Ct = dir_at(s + 1e-3) * (H(s + 1e-3) + t / 2); T = unit(Ct - C)
        up = unit(w0 - (w0 @ T) * T); acr = np.cross(T, up); acr = acr if acr @ LAT > 0 else -acr
        tilt = math.atan2(H(s, HW) - H(s, -HW), 2 * HW); up2 = math.cos(tilt) * up - math.sin(tilt) * acr; acr2 = np.cross(T, up2)
        acr2 = acr2 if acr2 @ LAT > 0 else -acr2
        secs.append(section_pts(C, unit(acr2 - (acr2 @ up2) * up2), up2, 2 * HW, t))
    latB = unit(LAT - (LAT @ b) * b)
    secB = [section_pts(b * (zB + tB / 2) + x * dB, latB, b, 2 * max(CH.planform_halfwidth(x), 0.6), tB, depB, x) for x in np.linspace(xj, HUB_R + 1.2, 5)]
    secB += plate_sections(b, dB, latB, zB, tB, depB, HUB_R - 0.04, -HUB_R + 0.04, False)
    secs += secB
    return loft(secs), dict(zA=zA, tA=tA, lowA=lowA, zB=zB, tB=tB, lowB=lowB)

def build_base():
    """scapula-fixed hub plate + mounting tab (2x M3) pointing away from link 1; turned (axisymmetric) skin-side contour"""
    a = np.array([1.0, 0, 0]); d = np.array([0, -1.0, 0]); lat = np.array([0, 0, 1.0])     # tab along -y (link 1 leaves along +y)
    z0, tp, low = plate_role(0, 1)
    dep = contour_field(0, 1, a, -d, lat, axisym=True) if low else None
    depf = (lambda x, y: dep(-np.asarray(x), y)) if dep is not None else None
    TAB = 24.0; xe = HUB_R + TAB - HW                                                        # tab = stadium (round end, radius HW)
    def base_hw(x):
        disc = math.sqrt(max(HUB_R ** 2 - x ** 2, 0.0))
        strip = HW if 0.0 <= x <= xe else (math.sqrt(max(HW ** 2 - (x - xe) ** 2, 0.0)) if x > xe else 0.0)
        k = 6.0; hmax = max(disc, strip); hmin = min(disc, strip)
        return hmax + max(0.0, k - (hmax - hmin)) ** 3 / (6 * k * k) if strip > 0 and disc > 0 else hmax    # smooth-max waist
    secs = []
    xs = np.r_[-HUB_R + 0.04 + (2 * HUB_R) * (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, 17)))[:-1], np.linspace(HUB_R, xe, 6), xe + HW * np.sin(np.linspace(0.15, 1.45, 7))]
    for x in xs:
        hw_ = base_hw(float(x)); c = a * (z0 + tp / 2) + x * d; secs.append(section_pts(c, lat, a, 2 * max(hw_, 0.8), tp, depf, x))
    body = loft(secs)
    for x_ in (HUB_R + 8.0, HUB_R + 18.0):                                                     # 2x M3 counterbored, from the skin side
        p = a * z0 + x_ * d
        tool = G.revolve_profile([("line", (0, -6), (1.7, -6)), ("line", (1.7, -6), (1.7, tp + 2)), ("line", (1.7, tp + 2), (0, tp + 2)), ("line", (0, tp + 2), (0, -6))], a)
        body = body.cut(tool.moved(cq.Location(V(p))))
    return body, dict(z0=z0, tp=tp, low=low)

def pin_on(axis, z_seat, z_top):
    r = PIN_D / 2; z0 = z_seat - 1.2; hr, ch = 1.65, 0.3
    segs = [("line", (hr, z0), (r, z0)), ("line", (r, z0), (r, z_seat + 0.05)), ("line", (r, z_seat + 0.05), (r - 0.4, z_seat + 0.25)),
            ("line", (r - 0.4, z_seat + 0.25), (r - 0.4, z_seat + 0.65)), ("line", (r - 0.4, z_seat + 0.65), (r, z_seat + 0.85)),
            ("line", (r, z_seat + 0.85), (r, z_top - 0.4)), ("line", (r, z_top - 0.4), (r - 0.4, z_top)), ("line", (r - 0.4, z_top), (hr + ch, z_top)),
            ("line", (hr + ch, z_top), (hr, z_top - ch)), ("line", (hr, z_top - ch), (hr, z_top - 7.0)), ("line", (hr, z_top - 7.0), (0.0, z_top - 7.6)),
            ("line", (0.0, z_top - 7.6), (0.0, z0)), ("line", (0.0, z0), (hr, z0))]
    return G.revolve_profile(segs, axis)

def stack_levels(F, t_lo):
    zA = F + t_lo; zU0 = zA + T_W; zU1 = zU0 + T_SEAT; zB1 = zU1 + T_W; zc0 = zB1 + 0.02
    return dict(F=F, zA=zA, zU0=zU0, zU1=zU1, zB1=zB1, zc0=zc0, top=zc0 + CAP_H)

def joint_hw(axis, lv):
    zA, zU0, zU1, zc0 = lv["zA"], lv["zU0"], lv["zU1"], lv["zc0"]; out = {}
    wash = lambda z: G.revolve_profile([("line", (5, z), (8.85, z)), ("line", (8.85, z), (9, z + 0.15)), ("line", (9, z + 0.15), (9, z + 0.85)),
                                        ("line", (9, z + 0.85), (8.85, z + 1)), ("line", (8.85, z + 1), (5, z + 1)), ("line", (5, z + 1), (5, z))], axis)
    out["washer A (igus GTM-1018-010)"] = wash(zA)
    out["sleeve (igus GSM-1012-05)"] = G.revolve_profile([("line", (5, zU0), (5.7, zU0)), ("line", (5.7, zU0), (6, zU0 + 0.3)), ("line", (6, zU0 + 0.3), (6, zU0 + 4.7)),
                                                          ("line", (6, zU0 + 4.7), (5.7, zU0 + 5)), ("line", (5.7, zU0 + 5), (5, zU0 + 5)), ("line", (5, zU0 + 5), (5, zU0))], axis)
    out["washer B (igus GTM-1018-010)"] = wash(zU1)
    segs = G.dome_cap_profile(R=CAP_R, H=CAP_H, r_lip=5.2, r_cb=3.8, d_cb=2.05, skirt=0.35)
    out["retaining cap (Ti-6Al-4V, G2 dome)"] = G.revolve_profile([(s[0],) + tuple((q[0], q[1] + zc0) for q in s[1:]) if s[0] != "bez" else ("bez", [(q[0], q[1] + zc0) for q in s[1]]) for s in segs], axis)
    zs = zc0 + CAP_H - 2.05; zt = zs + 2.0
    scr = G.revolve_profile([("line", (0, zs - 6), (1.85, zs - 6)), ("line", (1.85, zs - 6), (2.0, zs - 5.7)), ("line", (2.0, zs - 5.7), (2.0, zs)),
                             ("line", (2.0, zs), (3.55, zs)), ("line", (3.55, zs), (3.55, zt - 0.35)), ("line", (3.55, zt - 0.35), (3.2, zt)),
                             ("line", (3.2, zt), (0, zt)), ("line", (0, zt), (0, zs - 6))], axis)
    n_, x_, y_ = CH.frame_of(axis)
    hexw = cq.Workplane(cq.Plane(origin=V(n_ * (zt - 1.3)), xDir=V(x_), normal=V(n_))).polygon(6, 2.5 / math.cos(math.pi / 6)).extrude(1.4).val()
    out["M4x6 ultra-low-profile socket screw (A2 stainless)"] = scr.cut(hexw)
    return out

def upper_features(body, axis, zU0):
    return body.cut(CH.bore_tool(axis, zU0, zU0 + T_SEAT, SLV_OD / 2))       # Ø12 H7 sleeve bore through the 5.05 hub, 0.3 chamfers

def solid_ok(s):
    if not s.isValid():
        from OCP.ShapeFix import ShapeFix_Shape
        sf = ShapeFix_Shape(s.wrapped); sf.Perform(); s = cq.Shape.cast(sf.Shape())
    return s

# ================================================================ stage 2: arm end (canonical humerus frame)
import arm_end as AE
def w_dir(d, az): d, az = d * D2R, az * D2R; return np.array([math.sin(d) * math.sin(az), -math.cos(d), math.sin(d) * math.cos(az)])
W0 = w_dir(*R["w"]); HA = np.array([0.0, -1.0, 0.0]); CUFF = R.get("cuff")
E_M = unit(HA - (HA @ W0) * W0); TAU = unit(np.cross(HA, W0))                  # meridian (along the arm) / tangential at phi = 0
S_CUT = AE.S_CUT; BAR_Y0, BAR_Z0 = 0.06, 0.445                                  # bar section centre (lateral, normal)
uBc, vBc, aBc = (AE.rest_to_can_pt(x) for x in (AE.uB, AE.vB, AE.axB))
def bar_pt(s, y, z): return AE.rest_to_can_pt(AE.CB + s * AE.uB + y * AE.vB + z * AE.axB)
def Rot(phi):
    K = np.array([[0, -HA[2], HA[1]], [HA[2], 0, -HA[0]], [-HA[1], HA[0], 0]]); return np.eye(3) + math.sin(phi) * K + (1 - math.cos(phi)) * K @ K
def smooth(w): w = min(max(float(w), 0.0), 1.0); return w * w * (3 - 2 * w)
def slerp(a_, b_, w):
    a_, b_ = unit(a_), unit(b_); om = math.acos(float(np.clip(a_ @ b_, -1, 1)))
    if om < 1e-6: return a_
    return unit((math.sin((1 - w) * om) * a_ + math.sin(w * om) * b_) / math.sin(om))
def bezier(P0, T0, P3, T3, n):
    L = np.linalg.norm(P3 - P0); P1 = P0 + T0 * L / 3; P2 = P3 - T3 * L / 3
    u = np.linspace(0, 1, n)[:, None]; return (1 - u) ** 3 * P0 + 3 * (1 - u) ** 2 * u * P1 + 3 * (1 - u) * u ** 2 * P2 + u ** 3 * P3

def round_poly(P, r):
    """closed polygon, every corner replaced by a round of size <= r"""
    P = np.asarray(P, float); out = []; n = len(P)
    for i in range(n):
        a_, b_, c_ = P[i - 1], P[i], P[(i + 1) % n]; la, lc = np.linalg.norm(a_ - b_), np.linalg.norm(c_ - b_)
        if la < 1e-6 or lc < 1e-6: out.append(b_); continue
        u1, u2 = (a_ - b_) / la, (c_ - b_) / lc; ang = math.acos(float(np.clip(u1 @ u2, -1, 1)))
        if ang > math.pi - 1e-3: out.append(b_); continue
        d = min(r / math.tan(ang / 2), 0.45 * la, 0.45 * lc); p1, p2 = b_ + u1 * d, b_ + u2 * d
        for t_ in np.linspace(0, 1, 6): out.append((1 - t_) ** 2 * p1 + 2 * (1 - t_) * t_ * b_ + t_ ** 2 * p2)
    return np.array(out)
def norm_prof(P, n=120):
    """closed 2D profile (across, up) -> CCW, starting at argmax(across + 0.3 up), n points by arc length (loft-compatible)"""
    P = np.asarray(P, float)
    if 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]) < 0: P = P[::-1]
    P = np.roll(P, -int(np.argmax(P[:, 0] + 0.3 * P[:, 1])), 0); Q = np.vstack([P, P[:1]])
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q, axis=0), axis=1))]; t_ = np.linspace(0, s[-1], n, endpoint=False)
    return np.c_[np.interp(t_, s, Q[:, 0]), np.interp(t_, s, Q[:, 1])]
def rr_prof(wd, tp, depth=None):
    """G2 rounded rectangle (as section_pts), optional turned/contoured skin side pushed down by depth(y)"""
    ec = min(E_EDGE, wd / 2 - 0.1, tp / 2 - 0.1); prof = CH.section_outline(wd, tp, max(0.2, ec), n=160)
    if depth is not None:
        y2, z2 = prof[:, 0], prof[:, 1]; dep = np.asarray(depth(y2)).reshape(-1)
        wy = np.clip((wd / 2 - np.abs(y2)) / max(ec * 1.5, 0.3), 0, 1); wy = wy * wy * (3 - 2 * wy); wz = np.clip((-z2) / (tp / 2), 0, 1) ** 2
        prof = np.c_[y2, z2 - dep * wy * wz]
    return norm_prof(prof)
def sec3d(c, acr, up, P2): return c + np.outer(P2[:, 0], acr) + np.outer(P2[:, 1], up)

def bot_ring_depths():
    """arm-end hub: axial depth of its turned skin side below the face zj4 per ring (centre, 0.55 R, R - 1.5)"""
    ib = np.nonzero(np.array(R["is_bot"], bool))[0]; bu = np.array(R["bot_under"])[ib]; ca = np.array(R["cosa"])[ib]
    dep = np.clip(ZJ4 - bu * ca, 0.0, 12.0); rings = [dep[0:1], dep[1:9], dep[9:21]]
    return [0.0, 0.55 * HUB_R, HUB_R - 1.5], [float(r_.min()) for r_ in rings]
def axisym_depth(rv, dv):
    from scipy.interpolate import PchipInterpolator
    pc = PchipInterpolator(rv, dv)
    def f(x, y):
        r_ = np.hypot(np.atleast_1d(x), np.atleast_1d(y)); v = pc(np.minimum(r_, rv[-1]))
        return np.clip(v, 0, 12) * np.clip((HUB_R + 3.0 - r_) / 3.0, 0, 1)
    return f

# ---------------------------------------------------------------- neck: bolted to BOTTOM (tongue in the bar's channel)
BAR_POLY = np.array([(-14.94, -2.81), (15.06, -2.80), (15.06, 0.70), (12.05, 3.70), (-11.95, 3.70), (-14.94, 0.68)])  # bar outline at the cut
LAP_HOLES = AE.LAP_HOLES
def bar_prof(acr, up, c):
    P3 = np.array([bar_pt(S_CUT, y, z) for y, z in round_poly(BAR_POLY, 0.3)]); return norm_prof(np.c_[(P3 - c) @ acr, (P3 - c) @ up])
def neck_sections(P0, T0, up0, prof0, n=18):
    """from a part's last section (centre P0, travel T0, up0, profile prof0) to the bar's end face at s = S_CUT: the neck
    lies in the bar's plane over most of its length and folds into the part's plane near the part; profile morphs
    into the bar's own outline so the joint line is flush"""
    P3 = bar_pt(S_CUT, BAR_Y0, BAR_Z0); T3 = -uBc; acr3 = unit(np.cross(aBc, T3)); profB = bar_prof(acr3, aBc, P3)
    path = bezier(P0, unit(T0), P3, T3, n + 1); secs = []
    for k_ in range(1, n + 1):
        w = k_ / n; p = path[k_]; tan = unit(path[min(k_ + 1, n)] - path[k_ - 1]) if k_ < n else T3
        up = slerp(up0, aBc, smooth(w / 0.45)); up = unit(up - (up @ tan) * tan); acr = unit(np.cross(up, tan))
        wp = smooth((w - 0.65) / 0.35); secs.append(sec3d(p, acr, up, (1 - wp) * prof0 + wp * profB))
    return secs
def tongue():
    """22 mm tongue filling the bar's channel (0.1 clearance), 4x M3 tapped for countersunk screws through the bar's web"""
    c = bar_pt(S_CUT - 10.6, BAR_Y0, -0.6)
    b = cq.Workplane(cq.Plane(origin=tuple(map(float, c)), xDir=tuple(map(float, uBc)), normal=tuple(map(float, aBc)))).box(22.8, 23.8, 4.4).edges().chamfer(0.3).val()
    for s_, y_ in LAP_HOLES:
        p = bar_pt(s_, y_, 1.6); b = b.cut(cq.Solid.makeCylinder(1.25, 4.1, V(p - 4.1 * aBc), V(aBc)))
    return b
def lap_screws():
    out = []
    for s_, y_ in LAP_HOLES:
        p = bar_pt(s_, y_, 3.7)
        scr = G.revolve_profile([("line", (0, 0), (3.0, 0)), ("line", (3.0, 0), (1.5, -1.5)), ("line", (1.5, -1.5), (1.5, -5.8)), ("line", (1.5, -5.8), (1.3, -6.0)),
                                 ("line", (1.3, -6.0), (0, -6.0)), ("line", (0, -6.0), (0, 0))], aBc)
        n_, x_, y2 = CH.frame_of(aBc)
        hexw = cq.Workplane(cq.Plane(origin=V(-1.2 * n_), xDir=V(x_), normal=V(n_))).polygon(6, 2.0 / math.cos(math.pi / 6)).extrude(1.4).val()
        out.append(("H", "M3x6 countersunk ISO 10642 (A2, polished) - neck lap", scr.cut(hexw).moved(cq.Location(V(p)))))
    return out

def build_hub_block():
    """non-cuff arm end: Ø26 JN hub plate (6.5, turned skin side) perpendicular to the JN axis + neck + tongue, one Ti part"""
    P_bar = bar_pt(S_CUT, BAR_Y0, BAR_Z0); hub_c = W0 * ZJ4
    dh = unit((P_bar - hub_c) - ((P_bar - hub_c) @ W0) * W0); lat = unit(np.cross(W0, dh))
    rv, dv = bot_ring_depths(); dep = axisym_depth(rv, dv); print("  hub block ring depths", np.round(dv, 2), flush=True)
    xs = list(-HUB_R + 0.04 + (2 * HUB_R - 0.08) * (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, 19)))) + list(np.linspace(HUB_R + 1.2, HUB_R + 7.0, 4))
    secs = [sec3d(W0 * (ZJ4 + T_BOT / 2) + x * dh, lat, W0, rr_prof(2 * max(CH.planform_halfwidth(x), 0.6), T_BOT, lambda y, x=x: dep(np.full(len(y), x), y))) for x in xs]
    secs += neck_sections(W0 * (ZJ4 + T_BOT / 2) + (HUB_R + 7.0) * dh, dh, W0, rr_prof(2 * HW, T_BOT))
    body = loft(secs); print("  neck loft valid", body.isValid(), round(body.Volume() / 1000, 1), "cm3", flush=True)
    return CH.fuzzy_fuse(body, tongue(), tol=0.0)

# ---------------------------------------------------------------- sliding cuff = ring-segment arc guide (V-track + 4-wheel carriage)
TRK_HW, TRK_V, TRK_H, WEB_HW = 6.0, 2.0, 4.0, 4.0                               # V-head half-width at the ridges, ridge height, head height, keel
WHL_OD, WHL_RG, WHL_B, WHL_SP = 12.0, 4.5, 4.0, 13.0                             # V-wheel OD, groove-bottom radius, width, spacing along the arc
def revolve_about_HA(profile_tm, phi0, phi1):
    """(t along W0, m along E_M) polygon in the phi = 0 meridian plane -> exact solid of revolution about the humerus axis"""
    pts = [Rot(phi0) @ (t * W0 + m * E_M) for t, m in profile_tm]; poly = BRepBuilderAPI_MakePolygon()
    for p in pts: poly.Add(gp_Pnt(*map(float, p)))
    poly.Close(); face = BRepBuilderAPI_MakeFace(poly.Wire(), True).Face()
    return cq.Shape.cast(BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(*map(float, HA))), float(phi1 - phi0), True).Shape())
def rail_rows():
    """fitted rail underside (evaluator samples) -> per row: phi (sorted), t, mean m in the meridian frame"""
    RD = np.array(R["rail_dirs"]); RU = np.array(R["rail_under"]); P = RD * RU[:, None]; ncol = len(RD) // 3; w0p = W0 - (W0 @ HA) * HA; rows = []
    for r_ in range(3):
        ph, tt, mm = [], [], []
        for k_ in range(ncol):
            p = P[r_ * ncol + k_]; pp = p - (p @ HA) * HA; phi = math.atan2(HA @ np.cross(w0p, pp), w0p @ pp); q = Rot(-phi) @ p
            ph.append(phi); tt.append(q @ W0); mm.append(q @ E_M)
        o = np.argsort(ph); rows.append((np.array(ph)[o], np.array(tt)[o], float(np.mean(mm))))
    return sorted(rows, key=lambda r: r[2])

def build_cuff():
    rho_c = float(np.linalg.norm(np.cross(HA, W0 * ZJ4)))                            # carriage plate radius about the humerus axis
    Z_top = ZJ4 - 0.5; tc = Z_top - TRK_V                                            # track top 0.5 under the carriage; ridge level
    Lt, Lm = WHL_SP / 2 + WHL_OD / 2 + 1.0, TRK_HW + WHL_RG + WHL_OD / 2 + 1.0         # carriage plate half sizes (tangential, along the arm)
    PHI_t = float(CUFF["range"]) * D2R + Lt / rho_c; STOP = 2.0 / rho_c; PHI_e = PHI_t + STOP
    rows = rail_rows(); ms = [r_[2] for r_ in rows]
    def t_bot(m, phi):
        tb = np.interp(m, ms, [np.interp(phi, r_[0], r_[1]) for r_ in rows]) + 0.2       # fitted underside (skin + margin) + 0.2
        return min(tb, Z_top - TRK_H - 0.4)
    def frame(phi):
        up = Rot(phi) @ W0; tan = -(Rot(phi) @ TAU); acr = unit(np.cross(up, tan)); return Rot(phi) @ (W0 * tc), acr, up, tan
    def _unused_prof(phi):
        c, acr, up, tan = frame(phi); sg = float((Rot(phi) @ E_M) @ acr)
        tm = [(Z_top, -WEB_HW), (Z_top, WEB_HW), (tc, TRK_HW), (Z_top - TRK_H, WEB_HW)] + [(t_bot(m, phi), m) for m in np.linspace(WEB_HW, -WEB_HW, 5)] + [(Z_top - TRK_H, -WEB_HW), (tc, -TRK_HW)]
        return norm_prof(round_poly(np.array([(sg * m, t - tc) for t, m in tm]), 0.3))
    # end nearer the bar carries the neck; the other end is free
    sgn = min((-1, 1), key=lambda s_: np.linalg.norm(Rot(s_ * PHI_e) @ (W0 * tc) - bar_pt(S_CUT, BAR_Y0, BAR_Z0)))
    phis = np.linspace(-sgn * PHI_e, sgn * PHI_e, max(12, int(2 * PHI_e / (1.5 * D2R)) + 1))
    def frame_s(phi):                                                                  # travel from the free end toward the neck end
        c, acr, up, tan = frame(phi)
        if sgn > 0: tan = -tan; acr = unit(np.cross(up, tan))
        return c, acr, up, tan
    def prof_s(phi):
        c, acr, up, tan = frame_s(phi); sg = float((Rot(phi) @ E_M) @ acr)
        tm = [(Z_top, -WEB_HW), (Z_top, WEB_HW), (tc, TRK_HW), (Z_top - TRK_H, WEB_HW)] + [(t_bot(m, phi), m) for m in np.linspace(WEB_HW, -WEB_HW, 5)] + [(Z_top - TRK_H, -WEB_HW), (tc, -TRK_HW)]
        return norm_prof(round_poly(np.array([(sg * m, t - tc) for t, m in tm]), 0.3))
    secs = []
    for phi in phis:
        c, acr, up, tan = frame_s(phi); secs.append(sec3d(c, acr, up, prof_s(phi)))
    c, acr, up, tan = frame_s(phis[-1])
    secs += neck_sections(c, tan, up, prof_s(phis[-1]), n=20)
    track = loft(secs); print("  track+neck loft valid", track.isValid(), round(track.Volume() / 1000, 1), "cm3", flush=True)
    track = CH.fuzzy_fuse(track, tongue(), tol=0.0)
    lip = [(Z_top - 1.0, -3.5), (Z_top - 1.0, 3.5), (Z_top + 2.1, 3.5), (Z_top + 2.5, 3.1), (Z_top + 2.5, -3.1), (Z_top + 2.1, -3.5)]
    PHI_l = PHI_e - 0.4 / rho_c                                                        # lips end 0.4 short of the free end (no coplanar cap)
    for a0, a1 in ((PHI_t, PHI_l), (-PHI_l, -PHI_t)):                                  # integral end stops at the travel limits
        track = CH.fuzzy_fuse(track, revolve_about_HA(lip, a0, a1), tol=0.0)
    track = solid_ok(track); print("  track valid", track.isValid(), flush=True)
    # carriage plate: G2-rounded rectangle normal to W0, underside zj4, 6.5 thick; integral JN pin; 4 wheel pins
    ex, ey = TAU, E_M
    if np.cross(ex, ey) @ W0 < 0: ex = -ex
    def sdf2(x, y):
        qx, qy = np.abs(x) - (Lt - 4.0), np.abs(y) - (Lm - 4.0)
        return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - 4.0
    carr = G.flat_plate(sdf2, [0, 0, 0], ex, ey, ZJ4, ZJ4 + T_BOT, 1.0, (-Lt - 3, Lt + 3, -Lm - 3, Lm + 3))
    rho_w = float(np.linalg.norm(np.cross(HA, W0 * tc))); psi = (WHL_SP / 2) / rho_w; hw_parts = []
    for ps in (-psi, psi):
        for sm in (-1, 1):
            Wp = Rot(ps) @ W0; cw = Rot(ps) @ (W0 * tc + E_M * sm * (TRK_HW + WHL_RG)); ecc = sm < 0
            def rv(segs): return G.revolve_profile([("line", a_, b_) for a_, b_ in zip(segs, segs[1:] + segs[:1])], Wp).moved(cq.Location(V(cw)))
            hw_parts.append(("cuff", "V-wheel Ø12 90° (PEEK, custom turned)", rv([(3.0, -2.0), (5.7, -2.0), (6.0, -1.7), (6.0, -1.5), (WHL_RG, 0.0), (6.0, 1.5), (6.0, 1.7), (5.7, 2.0), (3.0, 2.0)])))
            hw_parts.append(("cuff", "MR63ZZ bearing 3x6x2.5", rv([(1.5, -1.25), (3.0, -1.25), (3.0, 1.25), (1.5, 1.25)])))
            hw_parts.append(("cuff", "spacer 3.1x4.8x1.25 (17-4PH)", rv([(1.55, 1.25), (2.4, 1.25), (2.4, 2.5), (1.55, 2.5)])))
            ztop = 2.5 + T_BOT - 0.3
            hw_parts.append(("cuff", f"headed wheel pin Ø3 h6 (17-4PH H900){', in eccentric bushing' if ecc else ', pressed'}",
                             rv([(0.0, -2.0), (2.4, -2.0), (2.4, -1.4), (1.5, -1.25), (1.5, ztop), (0.0, ztop)])))
            if ecc:                                                                     # eccentric bushing (0.4 mm) turns for preload, set-screw locked
                off_ = 0.4 * unit(Rot(ps) @ E_M) * sm
                bush = cq.Solid.makeCylinder(2.5, ztop - 2.5, V(cw + off_ + 2.5 * Wp), V(Wp)).cut(cq.Solid.makeCylinder(1.5, ztop, V(cw), V(Wp)))
                hw_parts.append(("cuff", "eccentric bushing Ø5/Ø3, 0.4 mm (17-4PH)", bush))
                carr = carr.cut(cq.Solid.makeCylinder(2.5, 30.0, V(cw + off_ - 5 * Wp), V(Wp)))
            else: carr = carr.cut(cq.Solid.makeCylinder(1.5, 30.0, V(cw - 5 * Wp), V(Wp)))
    print(f"  cuff: rho {rho_c:.1f}  travel ±{CUFF['range']:.1f}°  track ±{PHI_e / D2R:.1f}°  carriage {2 * Lt:.0f}x{2 * Lm:.0f}", flush=True)
    return track, carr, hw_parts, dict(rho=rho_c, PHI_t=PHI_t / D2R, PHI_e=PHI_e / D2R, Z_top=Z_top, Lt=Lt, Lm=Lm, neck_end=int(sgn))

def stage1():
    import trimesh
    parts = []                                                       # (group, name, shape) in the group's own frame
    # ---- shoulder members + the joint hardware of the joints they are the lower member of
    base, bi = build_base(); ax0 = hub_axis(0, 1)
    if bi["low"]:
        lv = stack_levels(bi["z0"], T_LO); base = CH.fuzzy_fuse(base, pin_on(ax0, lv["zA"], lv["zc0"]))
        for nm, s in joint_hw(ax0, lv).items(): parts.append(("base", f"J1 {nm}", s))
    else: base = upper_features(base, ax0, bi["z0"])
    base = solid_ok(base); parts.append(("base", "D4-01 scapula base (Ti-6Al-4V)", base)); print("base valid", base.isValid(), flush=True)
    for mi in range(1, N):
        body, li = build_link(mi)
        for end, (z0, tp, low) in ((0, (li["zA"], li["tA"], li["lowA"])), (1, (li["zB"], li["tB"], li["lowB"]))):
            ax_ = hub_axis(mi, end); J = joint_of(mi, end)
            if low:
                lv = stack_levels(z0, T_LO); body = CH.fuzzy_fuse(body, pin_on(ax_, lv["zA"], lv["zc0"]))
                for nm, s in joint_hw(ax_, lv).items(): parts.append((f"l{mi}", f"J{J} {nm}", s))
            else: body = upper_features(body, ax_, z0)
        body = solid_ok(body); parts.append((f"l{mi}", f"D4-{mi + 1:02d} link {mi} (Ti-6Al-4V)", body))
        print(f"link {mi} valid {body.isValid()} volume {body.Volume() / 1000:.1f} cm3", flush=True)
    json.dump([[g, n] for g, n, _ in parts], open(os.path.join(OUT, "parts_stage1.json"), "w"))
    sc = trimesh.Scene()
    for k_, (g, nm, s) in enumerate(parts):
        vs, tr = s.tessellate(0.05, 0.12)
        if not len(tr): print("no mesh", nm); continue
        m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False); _ = m.vertex_normals
        sc.add_geometry(m, node_name=f"{g}|{nm}|{k_}", geom_name=f"{g}|{nm}|{k_}")
    sc.export(os.path.join(OUT, "shoulder_stage1.glb"))
    import pickle
    from OCP.BRepTools import BRepTools
    for k_, (g, nm, s) in enumerate(parts): BRepTools.Write_s(s.wrapped, os.path.join(OUT, f"part_{k_:02d}.brep"))
    print("stage 1 exported", len(parts), "parts")


MAT = {"Ti": ("Ti-6Al-4V", 4.43), "igus": ("iglidur G", 1.46), "A2": ("A2 stainless", 7.9), "174": ("17-4PH H900", 7.8), "PEEK": ("PEEK", 1.32),
       "52100": ("bearing steel", 7.8)}
def mat_of(name):
    n = name.lower()
    if "igus" in n: return "igus"
    if "screw" in n or "a2" in n: return "A2"
    if "17-4" in n: return "174"
    if "peek" in n: return "PEEK"
    if "bearing" in n: return "52100"
    return "Ti"

def export(parts, tag):
    import trimesh
    from OCP.BRepTools import BRepTools
    sc = trimesh.Scene()
    for k_, (g, nm, s) in enumerate(parts):
        vs, tr = s.tessellate(0.05, 0.12)
        if not len(tr): print("no mesh", nm); continue
        m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False); _ = m.vertex_normals
        sc.add_geometry(m, node_name=f"{g}|{nm}|{k_}", geom_name=f"{g}|{nm}|{k_}")
    sc.export(os.path.join(OUT, f"{tag}.glb"))

def stage2():
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    from OCP.BRep import BRep_Builder
    names = json.load(open(os.path.join(OUT, "parts_stage1.json"))); parts = []
    for k_, (g, nm) in enumerate(names):
        sh = TopoDS_Shape(); BRepTools.Read_s(sh, os.path.join(OUT, f"part_{k_:02d}.brep"), BRep_Builder()); parts.append((g, nm, cq.Shape.cast(sh)))
    lv = stack_levels(ZJ4, T_BOT); can = []                                       # arm-end parts in the canonical humerus frame
    info = {}
    if CUFF:
        track, carr, hw_parts, info = build_cuff()
        carr = solid_ok(CH.fuzzy_fuse(carr, pin_on(W0, lv["zA"], lv["zc0"]))); print("  carriage valid", carr.isValid(), flush=True)
        can += [("H", "D4-T arc guide: V-track + neck (Ti-6Al-4V, nitrided V flanks)", track), ("cuff", "D4-C cuff carriage (Ti-6Al-4V)", carr)] + hw_parts
        can += [("cuff", f"J{N} {nm}", s) for nm, s in joint_hw(W0, lv).items()]
    else:
        blk = solid_ok(CH.fuzzy_fuse(build_hub_block(), pin_on(W0, lv["zA"], lv["zc0"]))); print("  hub block valid", blk.isValid(), flush=True)
        can += [("H", f"D4-{N + 1:02d} arm-end hub block + neck (Ti-6Al-4V)", blk)] + [("H", f"J{N} {nm}", s) for nm, s in joint_hw(W0, lv).items()]
    can += lap_screws()
    for g, nm, s in can:
        if hasattr(s, "Solids") and len(s.Solids()) > 1: print("  WARNING", nm, "has", len(s.Solids()), "solids", [round(x.Volume() / 1000, 2) for x in s.Solids()], flush=True)
        parts.append((g, nm, AE.can_to_rest(s) if g == "H" else s))
    parts += [(g, nm, s) for g, nm, s in AE.user_parts()]
    export(parts, "exo")
    rows = []
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    for k_, (g, nm, s) in enumerate(parts):
        custom = not any(u in nm for u in ("BOTTOM (user", "UPPER ARM CUFF", "Hex socket head countersunk")) and g in ("base", "cuff", "H", "F") or g.startswith("l")
        user = g in ("H", "F") and not (nm.startswith(("D4-", "J")) or "M3x6" in nm)
        vol = s.Volume() / 1000.0; mk = mat_of(nm)
        rows.append(dict(k=k_, group=g, name=nm, vol_cm3=round(vol, 3), material=("user part" if user else MAT[mk][0]), mass_g=(None if user else round(vol * MAT[mk][1], 2)), valid=bool(s.isValid())))
        if not user and nm.startswith("D4-"): cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, "step", f"{nm.split(' ')[0]}.step"))
    json.dump(dict(key=KEY, n=N, info=info, stack=dict(lv), parts=rows), open(os.path.join(OUT, "parts.json"), "w"), indent=1)
    tot = sum(r["mass_g"] for r in rows if r["mass_g"]); print(f"stage 2 exported {len(parts)} parts; custom mass {tot:.0f} g", flush=True)

if __name__ == "__main__":
    stage1() if STAGE == 1 else stage2()
