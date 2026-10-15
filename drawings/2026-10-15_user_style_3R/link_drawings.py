"""Engineering drawings (A3, scale 1:1) of link 1 (J1-J2) and link 2 (J2-J3) of the user-style 3R.
VIEW A = true view of the link plane (the plane through GH containing both joint axes): the hub cylinders, the angle
between their axes, their offsets from GH and the bar path, projected (hidden-line removed) from the built STEP solids.
VIEW B = edge view of the link plane. Dimensions are computed from the same geometry (build.json + the CAD frames)."""
import json, math, os, sys
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepAdaptor import BRepAdaptor_Curve
R_ = "/home/user/exo-shoulder"; sys.path.insert(0, R_ + "/pipeline/conformal/param_cad"); sys.path.insert(0, R_ + "/pipeline/avg")
import param_build as PB, body_pose as BP
D = R_ + "/pipeline/full-exo/designs/param2_r20_n3_s1414_4"; OUT = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(D + "/build.json")); F = {k: float(B["faces"][k]) for k in ("J1", "J2", "J3")}
T, W, LSEAT, STACK, HUBD, U0 = PB.T, PB.W, 14.0, 12.25, 20.0, PB.LV["U0"]
u = lambda v: np.asarray(v, float) / np.linalg.norm(v)
FR = PB.FR; C, ax = FR.load(PB.BAND)
f0 = json.load(open(D + "/clips.json"))["clips"][0]["frames"][0]; X0 = FR.frame_of(f0)
Jw = {"J1": X0["base"][0] @ ax["J1"][1], "J2": X0["l2"][0] @ ax["J2"][1], "J3": X0["l2"][0] @ ax["J3"][1]}
LINKS = [dict(name="LINK 1", pid="D6-02", g="l1", a="J1", b="J2", upper=False, step="00_D6-02_link_1.step", key="link 1",
              role="lower member at J1 and J2 (pad 0-3 mm above each hub face, integral O7 pins up through the bearings)"),
         dict(name="LINK 2", pid="D6-03", g="l2", a="J2", b="J3", upper=True, step="01_D6-03_link_2.step", key="link 2",
              role="upper member at J2 and J3 (bearing rings 3.15-12.25 mm above each hub face)")]
# ---------------------------------------------------------------- drafting helpers (ISO-style, monochrome)
K = "black"; LW_V, LW_T = 0.7, 0.25          # visible / thin (pt)
def hlr(shape, n, xd):
    algo = HLRBRep_Algo(); algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*map(float, n)), gp_Dir(*map(float, xd)))))
    algo.Update(); algo.Hide(); h = HLRBRep_HLRToShape(algo); out = {}
    for nm, comp in (("vis", h.VCompound()), ("out", h.OutLineVCompound()), ("hid", h.HCompound())):
        segs = []
        if comp is not None and not comp.IsNull():
            for e in cq.Shape.cast(comp).Edges():
                try:
                    c = BRepAdaptor_Curve(e.wrapped); u0, u1 = c.FirstParameter(), c.LastParameter()
                    nps = 2 if e.geomType() == "LINE" else 32
                    P = np.array([[c.Value(t).X(), c.Value(t).Y()] for t in np.linspace(u0, u1, nps)])
                    if np.isfinite(P).all(): segs.append(P)
                except Exception:
                    pass
        out[nm] = segs
    return out
def view(axv, H, hidden=True):
    for P in H["vis"] + H["out"]: axv.plot(P[:, 0], P[:, 1], color=K, lw=LW_V, solid_capstyle="round")
    if hidden:
        for P in H["hid"]: axv.plot(P[:, 0], P[:, 1], color=K, lw=LW_T, ls=(0, (3, 1.5)))
def cline(axv, a, b): axv.plot(*zip(a, b), color=K, lw=LW_T, ls=(0, (12, 2, 2, 2)))
def text(axv, p, s, **kw): axv.text(*p, s, fontsize=kw.pop("fs", 7.5), color=K, family=kw.pop("family", "DejaVu Sans"), **kw)
def arrow(axv, tip, frm): axv.annotate("", xy=tip, xytext=frm, arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.18", color=K, lw=LW_T, shrinkA=0, shrinkB=0))
def dim(axv, p, q, off, label, tfrac=0.5, flip=False):
    """aligned dimension p->q, offset perpendicular by off (mm), extension lines from the points"""
    p, q = np.asarray(p, float), np.asarray(q, float); t = u(q - p); n = np.array([-t[1], t[0]]); s = np.sign(off) or 1
    P_, Q_ = p + n * off, q + n * off
    for a_, b_ in ((p, P_), (q, Q_)): axv.plot(*zip(a_ + n * s * 1.0, b_ + n * s * 1.5), color=K, lw=LW_T)
    axv.plot(*zip(P_, Q_), color=K, lw=LW_T); m = (P_ + Q_) / 2
    arrow(axv, P_, P_ + t * 3); arrow(axv, Q_, Q_ - t * 3)
    a = math.degrees(math.atan2(t[1], t[0])); a = a - 180 if a > 90 else a + 180 if a < -90 else a
    text(axv, P_ + (Q_ - P_) * tfrac + n * s * 2.2, label, ha="center", va="center", rotation=a, bbox=dict(fc="white", ec="none", pad=0.3))
def angdim(axv, c, r, a0, a1, label):
    t = np.radians(np.linspace(a0, a1, 80)); axv.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=K, lw=LW_T)
    for tt, d in ((t[0], 1), (t[-1], -1)):
        tip = c + r * np.array([math.cos(tt), math.sin(tt)]); arrow(axv, tip, tip + d * 3 * np.array([-math.sin(tt), math.cos(tt)]))
    tm = math.radians((a0 + a1) / 2); text(axv, c + (r + 5) * np.array([math.cos(tm), math.sin(tm)]), label, ha="center", va="center", fs=8.5,
                                          bbox=dict(fc="white", ec="none", pad=0.3))
def leader(axv, tip, at, label, ha="left"):
    axv.plot(*zip(tip, at), color=K, lw=LW_T); arrow(axv, tip, tip + u(np.asarray(at) - np.asarray(tip)) * 3)
    text(axv, at, " " + label + " ", ha=ha, va="center", bbox=dict(fc="white", ec="none", pad=0.2))
def chain_points(start, segs):
    """centre line of the bar: per segment (kind, p0, p1, centre, R)"""
    x, y, ps = start; out = []
    for k, l in segs:
        p0 = np.array([x, y])
        if abs(k) < 1e-9:
            x, y = x + l * math.cos(ps), y + l * math.sin(ps); out.append(("L", p0, np.array([x, y]), None, None, l))
        else:
            c = p0 + (1 / k) * np.array([-math.sin(ps), math.cos(ps)])
            x, y, ps = x + (math.sin(ps + k * l) - math.sin(ps)) / k, y - (math.cos(ps + k * l) - math.cos(ps)) / k, ps + k * l
            out.append(("A", p0, np.array([x, y]), c, 1 / k, l)); continue
    return out
A3W, A3H = 420.0, 297.0
def sheet(L, ka, kb, shape):
    fig = plt.figure(figsize=(A3W / 25.4, A3H / 25.4)); fig.patch.set_facecolor("white")
    mm = lambda x0, y0, w, h, xl, yl: fig.add_axes([x0 / A3W, y0 / A3H, w / A3W, h / A3H], xlim=xl, ylim=yl)
    # border + title block
    bd = fig.add_axes([0, 0, 1, 1], xlim=(0, A3W), ylim=(0, A3H)); bd.axis("off")
    bd.add_patch(Rectangle((10, 10), A3W - 20, A3H - 20, fill=False, ec=K, lw=1.0))
    tb = [(250, 10, 160, 42)]; bd.add_patch(Rectangle((250, 10), 160, 42, fill=False, ec=K, lw=0.8))
    for yy in (24, 38): bd.plot([250, 410], [yy, yy], color=K, lw=0.4)
    bd.plot([330, 330], [10, 38], color=K, lw=0.4)
    t_ = lambda x, y, s, **kw: bd.text(x, y, s, fontsize=kw.pop("fs", 7), color=K, family="DejaVu Sans", va="center", **kw)
    t_(253, 45, f"{L['name']}  ({L['a']} - {L['b']})   {L['pid']}", fs=11, fontweight="bold")
    t_(253, 31, "MATERIAL  Ti-6Al-4V, bead blasted"); t_(333, 31, "SCALE  1:1 on A3     UNITS  mm, deg")
    t_(253, 17, "exo-shoulder  user-style 3R (r20 s1414 #4)"); t_(333, 17, "THIRD ANGLE   DATE 2026-10-15   REV A")
    # geometry in the link-plane frame: x along axis a (radial from GH), y in-plane toward axis b
    ex = u(ka); ey = u(kb - (kb @ ex) * ex); n = np.cross(ex, ey); phi = math.degrees(math.acos(np.clip(u(kb) @ ex, -1, 1)))
    eb = np.array([math.cos(math.radians(phi)), math.sin(math.radians(phi))])
    z0 = U0 if L["upper"] else 0.0; ha, hb = F[L["a"]] + z0 + T / 2, F[L["b"]] + z0 + T / 2
    segs = B[L["key"]]["segs"]; start = (ha, LSEAT, math.pi / 2); ch = chain_points(start, segs)
    # ---- VIEW A: true view of the link plane
    xa, ya = (-14, 150), (-30, 140)
    va = mm(16, 104, xa[1] - xa[0], ya[1] - ya[0], xa, ya); va.set_aspect("equal"); va.axis("off")
    view(va, hlr(shape, n, ex))
    for kk, d2 in ((L["a"], np.array([1.0, 0.0])), (L["b"], eb)):          # axes (centre lines) + hub envelopes (phantom)
        cline(va, -4 * d2, (F[kk] + STACK + 30) * d2)
        nn = np.array([-d2[1], d2[0]]); c0 = F[kk] * d2
        q = [c0 + nn * HUBD / 2, c0 + nn * HUBD / 2 + d2 * STACK, c0 - nn * HUBD / 2 + d2 * STACK, c0 - nn * HUBD / 2, c0 + nn * HUBD / 2]
        va.plot(*zip(*q), color=K, lw=LW_T, ls=(0, (8, 1.5, 1.5, 1.5, 1.5, 1.5)))
        text(va, (F[kk] + STACK + 30) * d2 + 4 * np.array([-d2[1], d2[0]]), f"{kk} AXIS", ha="center", va="center", fs=8, fontweight="bold", bbox=dict(fc="white", ec="none", pad=0.3))
    va.plot(0, 0, "+", color=K, ms=9, mew=LW_T); text(va, (-3, -6), "GH (sphere centre)\nDATUM A", ha="right", va="top", fs=7)
    angdim(va, np.zeros(2), 24, 0, phi, f"{phi:.2f}°")
    dim(va, (0, 0), (F[L["a"]], 0), -16 if True else 16, f"{F[L['a']]:.2f}")
    dim(va, (0, 0), F[L["b"]] * eb, 16, f"{F[L['b']]:.2f}")
    pa, pb = F[L["a"]] * np.array([1.0, 0]), F[L["b"]] * eb
    dim(va, pa, pb, -10 if L["upper"] else 10, f"{np.linalg.norm(pb - pa):.2f}  hub face centres")
    # hub cylinder size on hub a
    c0 = np.array([F[L["a"]], 0.0]); dim(va, c0 + [0, -HUBD / 2], c0 + [0, HUBD / 2], -(STACK + 9), "Ø20 hub")
    dim(va, c0 + [0, -HUBD / 2], c0 + [STACK, -HUBD / 2], -8, f"{STACK:.2f} stack")
    # bar path: radii from their centres, bar centre-line start/end
    for i, (kind, p0, p1, c, Rr, l) in enumerate(ch):
        va.plot(*p0, marker="o", ms=1.6, color=K)
        if kind == "A" and abs(Rr) < 300:
            mid_t = None; ang0 = math.atan2(*(p0 - c)[::-1]); ang1 = math.atan2(*(p1 - c)[::-1])
            am = (ang0 + ang1) / 2 if abs(ang1 - ang0) < math.pi else (ang0 + ang1) / 2 + math.pi
            m = c + abs(Rr) * np.array([math.cos(am), math.sin(am)]); va.plot(*c, marker="+", ms=4, color=K, mew=LW_T)
            leader(va, m, m + u(m - c) * (8 + 3 * i) * (1 if Rr > 0 else -1), f"R{abs(Rr):g}")
        elif kind == "A":
            leader(va, (p0 + p1) / 2, (p0 + p1) / 2 + np.array([4, 6]), f"R{abs(Rr):g} (centre off sheet)")
    va.plot(*ch[-1][2], marker="o", ms=1.6, color=K)
    bd.text(20, 282, "VIEW A  -  TRUE VIEW OF THE LINK PLANE (through GH and both joint axes)  1:1", fontsize=8.5, fontweight="bold", color=K, family="DejaVu Sans", va="top")
    # ---- VIEW B: edge view (looking along the in-plane tangent at axis a; up = plane normal)
    xb, yb = (-14, 150), (-32, 20)
    vb = mm(16, 36, xb[1] - xb[0], yb[1] - yb[0], xb, yb); vb.set_aspect("equal"); vb.axis("off")
    view(vb, hlr(shape, -ey, ex)); cline(vb, (-4, 0), (128, 0))
    vb.plot(0, 0, "+", color=K, ms=9, mew=LW_T)
    xbar = 0.5 * (pa[0] + pb[0]) + 8                                           # bar width between the two pads
    dim(vb, (xbar, -W / 2), (xbar, W / 2), 4, f"{W:.0f} bar")
    lo, hi = (F[L["a"]] + U0, F[L["a"]] + STACK) if L["upper"] else (F[L["a"]], F[L["a"]] + T)
    dim(vb, (lo, -HUBD / 2), (hi, -HUBD / 2), -6, f"{hi - lo:.2f} {'ring' if L['upper'] else 'pad'}")
    dim(vb, (0, -HUBD / 2), (lo, -HUBD / 2), -14, f"{lo:.2f} GH to {'ring' if L['upper'] else 'pad'} underside")
    bd.text(20, 96, "VIEW B  -  EDGE VIEW OF THE LINK PLANE (the plane is the horizontal centre line)   SCALE 1:1", fontsize=8.5, fontweight="bold", color=K, family="DejaVu Sans", va="top")
    # ---- tables: segment table + notes
    tx = mm(192, 60, 214, 225, (0, 214), (0, 225)); tx.axis("off")
    rows = ["BAR CENTRE-LINE PATH IN VIEW A (from axis " + L["a"] + " to axis " + L["b"] + ")",
            "start: on the " + L["a"] + " seat, x = %.2f (radial), y = %.1f, heading +y" % (ha, LSEAT),
            "", "  #  type   radius      length   end point (x, y)"]
    for i, (kind, p0, p1, c, Rr, l) in enumerate(ch):
        rows.append(f"  {i+1}  {'arc ' if kind == 'A' else 'line'}  " + (f"R{abs(Rr):7.1f} {'L' if Rr > 0 else 'R'}" if kind == "A" else "   -     ") +
                    f"  {l:7.2f}   ({p1[0]:7.2f}, {p1[1]:7.2f})")
    rows += [f"end: on the {L['b']} seat, {LSEAT:.0f} from axis {L['b']}, at {hb:.2f} radial along {L['b']}",
             "(L / R = turning left / right walking from " + L["a"] + " to " + L["b"] + ")", "",
             "KEY DIMENSIONS",
             f"  angle between axes {L['a']} and {L['b']}           {phi:8.2f} deg",
             f"  GH to {L['a']} hub skin-side face (along {L['a']})    {F[L['a']]:8.2f}",
             f"  GH to {L['b']} hub skin-side face (along {L['b']})    {F[L['b']]:8.2f}",
             f"  {L['a']} face centre to {L['b']} face centre          {np.linalg.norm(pb - pa):8.2f}",
             f"  {L['a']} face centre in view A (x, y)       ({pa[0]:7.2f}, {pa[1]:7.2f})",
             f"  {L['b']} face centre in view A (x, y)       ({pb[0]:7.2f}, {pb[1]:7.2f})",
             f"  hub cylinder (both joints)             Ø{HUBD:.0f} x {STACK:.2f} from the face",
             f"  bar section                             {T:.0f} (in plane) x {W:.0f} (normal to plane)",
             f"  seat: flat pad, bar leaves it {LSEAT:.0f} mm from each axis", "",
             "THIS LINK IN THE JOINT STACK",
             "  " + L["role"], "",
             "NOTES",
             "1. Both joint axes pass through GH (datum A); view A is",
             "   the plane they span, so every length and angle in it is true.",
             "2. Hub faces are measured from GH along each axis; the hub",
             "   cylinder (O20 bearing stack) occupies face .. face + 12.25.",
             "3. Phantom rectangles = hub cylinder envelopes; dashed =",
             "   hidden edges; chain lines = joint axes.",
             "4. Unless noted: edges broken R0.5, pocket 1.0 deep on the",
             "   outer face with a 1.5 rim (as built)."]
    text(tx, (0, 222), "\n".join(rows), va="top", family="DejaVu Sans Mono", fs=7.2, linespacing=1.45)
    fn = OUT + f"/{L['pid']}_{L['name'].replace(' ', '_').lower()}_drawing"
    fig.savefig(fn + ".pdf"); fig.savefig(fn + ".png", dpi=200, facecolor="white"); plt.close(fig); return fn
outs = []
for L in LINKS:
    Rg = X0[L["g"]][0]; ka, kb = Rg.T @ Jw[L["a"]], Rg.T @ Jw[L["b"]]
    shape = cq.importers.importStep(D + "/step/" + L["step"]).val()
    outs.append(sheet(L, ka, kb, shape)); print("wrote", outs[-1])
