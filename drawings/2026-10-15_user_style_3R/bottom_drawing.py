"""Engineering drawing (A3) of D6-04: the user's BOTTOM bar (upper arm) cut short and fused with the arm end that carries
hub J3, for the user-style 3R (r20 s1414 #4). The point of the sheet: where to cut BOTTOM and how much to remove.

Frame (tools: pipeline/conformal/band_cad/arm_end.py): s = station up the bar from the ELBOW-HINGE AXIS (datum A), along
uB; v = across the bar (vB); h = normal to the bar top, away from the arm (axB). The user's original BOTTOM is loaded
from data/user_cad (load_arm.load) and drawn in phantom where it is removed. VIEW A / B at 1:2, DETAIL C / VIEW D at 1:1,
all projected (hidden-line removed) from the built STEP solids."""
import json, math, os, sys
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepAdaptor import BRepAdaptor_Curve
R_ = "/home/user/exo-shoulder"; OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, R_ + "/pipeline/conformal/band_cad"); sys.path.insert(0, R_ + "/pipeline/full-exo")
import arm_end as AE
from load_arm import load
D = R_ + "/pipeline/full-exo/designs/param2_r20_n3_s1414_4"
B = json.load(open(D + "/build.json")); INV = json.load(open(OUT + "/inventory/D6-04_BOTTOM_arm_end.json"))
AEB, CUF = B["arm end"], B["upper cuff"]
PART = cq.importers.importStep(D + "/step/03_D6-04_BOTTOM_+_arm_end,_one_5-axis_part_.step").val()
orig = [s for n, _, s in load() if n == "BOTTOM"][0]; ORIG = AE.cad_to_rest(orig, "up")
CB, uB, vB, axB = AE.CB, AE.uB, AE.vB, AE.axB
S_CUT = float(AEB["bottom_cut_s"]); F3 = float(B["faces"]["J3"])
k3 = np.array(INV["joint_axes"][0]["axis_dir"]); k3 /= np.linalg.norm(k3)
# removed piece of the original bar (s > S_CUT), for the phantom outline
big = cq.Workplane(cq.Plane(origin=tuple(map(float, CB + S_CUT * uB)), xDir=tuple(map(float, vB)), normal=tuple(map(float, uB)))).rect(900, 900).extrude(900).val()
REMOVED = ORIG.intersect(big)
def sv(p): p = np.asarray(p, float) - CB; return np.array([p @ uB, p @ vB, p @ axB])
vs, _ = ORIG.tessellate(0.3); PO = np.array([sv([q.x, q.y, q.z]) for q in vs])
vs, _ = PART.tessellate(0.3); PP = np.array([sv([q.x, q.y, q.z]) for q in vs])
S_EYE, S_END = PO[:, 0].min(), PO[:, 0].max(); S_PEND = PP[:, 0].max()
J3F = sv(F3 * k3); J3T = sv((F3 + 11.15) * k3)                      # J3 axis at the pad face and at the pin top (75.5 + 7.5)
k3l = np.array([k3 @ uB, k3 @ vB, k3 @ axB])
# ---------------------------------------------------------------- drafting helpers (ISO-style, monochrome)
K = "black"; LW_V, LW_T = 0.7, 0.25
u = lambda v: np.asarray(v, float) / np.linalg.norm(v)
def hlr(shape, n, xd):
    """2D edges in the (xd, n x xd) frame, relative to the bar datum CB"""
    algo = HLRBRep_Algo(); algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*map(float, n)), gp_Dir(*map(float, xd)))))
    algo.Update(); algo.Hide(); h = HLRBRep_HLRToShape(algo); out = {}
    yd = np.cross(n, xd); o = np.array([CB @ xd, CB @ yd])
    for nm, comp in (("vis", h.VCompound()), ("out", h.OutLineVCompound()), ("hid", h.HCompound())):
        segs = []
        if comp is not None and not comp.IsNull():
            for e in cq.Shape.cast(comp).Edges():
                try:
                    c = BRepAdaptor_Curve(e.wrapped); t0, t1 = c.FirstParameter(), c.LastParameter()
                    P = np.array([[c.Value(t).X(), c.Value(t).Y()] for t in np.linspace(t0, t1, 2 if e.geomType() == "LINE" else 32)]) - o
                    if np.isfinite(P).all(): segs.append(P)
                except Exception:
                    pass
        out[nm] = segs
    return out
def view(axv, H, hidden=True, phantom=False, sc=1.0):
    st = dict(color=K, lw=LW_T, ls=(0, (8, 1.5, 1.5, 1.5, 1.5, 1.5))) if phantom else dict(color=K, lw=LW_V, solid_capstyle="round")
    for P in H["vis"] + H["out"]: axv.plot(P[:, 0] * sc, P[:, 1] * sc, **st)
    if hidden and not phantom:
        for P in H["hid"]: axv.plot(P[:, 0] * sc, P[:, 1] * sc, color=K, lw=LW_T, ls=(0, (3, 1.5)))
def cline(axv, a, b): axv.plot(*zip(a, b), color=K, lw=LW_T, ls=(0, (12, 2, 2, 2)))
def text(axv, p, s, **kw): axv.text(*p, s, fontsize=kw.pop("fs", 7.5), color=K, family="DejaVu Sans", **kw)
def arrow(axv, tip, frm): axv.annotate("", xy=tip, xytext=frm, arrowprops=dict(arrowstyle="-|>,head_length=0.55,head_width=0.18", color=K, lw=LW_T, shrinkA=0, shrinkB=0))
def dim(axv, p, q, off, label, sc=1.0, tfrac=0.5, bold=False):
    """aligned dimension p->q (model mm), drawn at scale sc, offset perpendicular by off (paper mm)"""
    p, q = np.asarray(p, float) * sc, np.asarray(q, float) * sc; t = u(q - p); n = np.array([-t[1], t[0]]); s = np.sign(off) or 1
    P_, Q_ = p + n * off, q + n * off
    for a_, b_ in ((p, P_), (q, Q_)): axv.plot(*zip(a_ + n * s * 1.0, b_ + n * s * 1.5), color=K, lw=LW_T)
    axv.plot(*zip(P_, Q_), color=K, lw=LW_T); arrow(axv, P_, P_ + t * 3); arrow(axv, Q_, Q_ - t * 3)
    a = math.degrees(math.atan2(t[1], t[0])); a = a - 180 if a > 90 else a + 180 if a < -90 else a
    text(axv, P_ + (Q_ - P_) * tfrac + n * s * 2.2, label, ha="center", va="center", rotation=a, fs=8 if bold else 7.5,
         fontweight="bold" if bold else "normal", bbox=dict(fc="white", ec="none", pad=0.3))
def leader(axv, tip, at, label, ha="left", sc=1.0):
    tip, at = np.asarray(tip, float) * sc, np.asarray(at, float)
    axv.plot(*zip(tip, at), color=K, lw=LW_T); arrow(axv, tip, tip + u(at - tip) * 3)
    text(axv, at, " " + label + " ", ha=ha, va="center", bbox=dict(fc="white", ec="none", pad=0.2))
def angdim(axv, c, r, a0, a1, label):
    t = np.radians(np.linspace(a0, a1, 80)); axv.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=K, lw=LW_T)
    for tt, d in ((t[0], 1), (t[-1], -1)):
        tip = c + r * np.array([math.cos(tt), math.sin(tt)]); arrow(axv, tip, tip + d * 3 * np.array([-math.sin(tt), math.cos(tt)]))
    tm = math.radians((a0 + a1) / 2); text(axv, c + (r + 6) * np.array([math.cos(tm), math.sin(tm)]), label, ha="center", va="center", fs=8.5, bbox=dict(fc="white", ec="none", pad=0.3))
A3W, A3H = 420.0, 297.0
fig = plt.figure(figsize=(A3W / 25.4, A3H / 25.4)); fig.patch.set_facecolor("white")
def mm(x0, y0, w, h, xl, yl):
    a = fig.add_axes([x0 / A3W, y0 / A3H, w / A3W, h / A3H], xlim=xl, ylim=yl); a.set_aspect("equal"); a.axis("off"); return a
bd = fig.add_axes([0, 0, 1, 1], xlim=(0, A3W), ylim=(0, A3H)); bd.axis("off")
bd.add_patch(Rectangle((10, 10), A3W - 20, A3H - 20, fill=False, ec=K, lw=1.0))
bd.add_patch(Rectangle((250, 10), 160, 42, fill=False, ec=K, lw=0.8))
for yy in (24, 38): bd.plot([250, 410], [yy, yy], color=K, lw=0.4)
bd.plot([330, 330], [10, 38], color=K, lw=0.4)
tb = lambda x, y, s, **kw: bd.text(x, y, s, fontsize=kw.pop("fs", 7), color=K, family="DejaVu Sans", va="center", **kw)
tb(253, 45, "BOTTOM (cut) + ARM END   D6-04", fs=11, fontweight="bold")
tb(253, 31, f"MATERIAL  7075-T6 (one 5-axis part), {INV['summary']['mass_g_as_specified']:.0f} g"); tb(333, 31, "SCALE  1:2 (A, B)  1:1 (C, D)   UNITS mm, deg")
tb(253, 17, "exo-shoulder  user-style 3R (r20 s1414 #4)"); tb(333, 17, "THIRD ANGLE   DATE 2026-10-16   REV A")
title = lambda x, y, s: bd.text(x, y, s, fontsize=8.5, fontweight="bold", color=K, family="DejaVu Sans", va="top")
SC2 = 0.5
TOP = float(np.max(PP[(PP[:, 0] > 30) & (PP[:, 0] < 240), 2])); BOT = float(np.min(PP[(PP[:, 0] > 30) & (PP[:, 0] < 240), 2]))
# ---- VIEW A: top view onto the bar (looking at the bar top, toward the arm), 1:2. x = s, y = v
xa, ya = (-60 * SC2, 440 * SC2), (-70 * SC2, 52 * SC2)
va = mm(16, 211, xa[1] - xa[0], ya[1] - ya[0], xa, ya)
view(va, hlr(PART, axB, uB), hidden=False, sc=SC2); view(va, hlr(REMOVED, axB, uB), phantom=True, sc=SC2)
cline(va, (0, -30 * SC2), (0, 30 * SC2)); text(va, (0, 31 * SC2), "A", ha="center", va="bottom", fs=8, fontweight="bold")
text(va, (-27 * SC2, 0), "ELBOW-HINGE\nAXIS = DATUM A", ha="right", va="center", fs=6.5)
cline(va, (S_CUT * SC2, -32 * SC2), (S_CUT * SC2, 30 * SC2)); text(va, (S_CUT * SC2, 31 * SC2), "CUT", ha="center", va="bottom", fs=8, fontweight="bold")
dim(va, (0, 24), (S_CUT, 24), 4, f"{S_CUT:.1f}  datum A to cut", sc=SC2, bold=True)
dim(va, (S_CUT, 24), (S_END, 24), 4, f"REMOVE {S_END - S_CUT:.1f}", sc=SC2, bold=True)
dim(va, (S_EYE, 24), (S_CUT, 24), 12, f"{S_CUT - S_EYE:.1f}  bar kept (eye end to cut)", sc=SC2)
dim(va, (S_EYE, -40), (S_PEND, -40), -4, f"{S_PEND - S_EYE:.1f}  this part overall", sc=SC2)
dim(va, (S_EYE, -40), (S_END, -40), -11, f"{S_END - S_EYE:.1f}  your original BOTTOM (eye end to top end)", sc=SC2)
va.plot(J3F[0] * SC2, J3F[1] * SC2, "+", color=K, ms=7, mew=LW_T)
leader(va, J3F[:2], (J3F[0] * SC2 + 14, J3F[1] * SC2 - 4), f"J3 AXIS  s {J3F[0]:.1f}, {abs(J3F[1]):.1f} off centre", sc=SC2)
text(va, ((S_CUT + S_END) / 2 * SC2 + 8, 5 * SC2), "phantom = your bar, removed", ha="center", va="center", fs=6.5, bbox=dict(fc="white", ec="none", pad=0.2))
title(20, 285, "VIEW A  -  TOP VIEW ONTO THE BAR (normal to the bar top)   1:2")
# ---- VIEW B: side view (looking across the bar), 1:2. x = s, y = h (away from the arm); datum B = the bar top face
xb, yb = (-60 * SC2, 440 * SC2), (-34 * SC2, 24 * SC2)
vb = mm(16, 166, xb[1] - xb[0], yb[1] - yb[0], xb, yb)
view(vb, hlr(PART, -vB, uB), hidden=False, sc=SC2); view(vb, hlr(REMOVED, -vB, uB), phantom=True, sc=SC2)
cline(vb, (0, -20 * SC2), (0, 16 * SC2)); cline(vb, (S_CUT * SC2, -24 * SC2), (S_CUT * SC2, 18 * SC2))
vb.plot([-28 * SC2, 430 * SC2], [TOP * SC2] * 2, color=K, lw=LW_T, ls=(0, (2, 1.5)))
text(vb, (-29 * SC2, TOP * SC2), "BAR TOP = DATUM B ", ha="right", va="center", fs=6.5)
leader(vb, (120, BOT), (120 * SC2 - 6, BOT * SC2 - 10), f"bar {TOP - BOT:.1f} thick (30 wide)", ha="right", sc=SC2)
cline(vb, (J3F[0] * SC2, (J3F[2] - 8) * SC2), (J3T[0] * SC2, (J3T[2] + 6) * SC2))
dim(vb, (J3F[0] + 20, TOP), (J3F[0] + 20, J3F[2]), 6, f"{TOP - J3F[2]:.1f}", sc=SC2)
text(vb, ((J3F[0] + 20) * SC2 + 15, (TOP + J3F[2]) / 2 * SC2), "J3 pad face\nbelow datum B", ha="left", va="center", fs=6.5)
title(20, 196, "VIEW B  -  SIDE VIEW (across the bar; up = away from the arm)   1:2")
# ---- DETAIL C: the arm end, top view at 1:1 (s 228 .. 352)
xc, yc = (212.0, 352.0), (-60.0, 28.0)
vc = mm(16, 56, xc[1] - xc[0], yc[1] - yc[0], xc, yc)
view(vc, hlr(PART, axB, uB), hidden=True)
cline(vc, (S_CUT, -44), (S_CUT, 24)); text(vc, (S_CUT, 25), "CUT", ha="center", va="bottom", fs=8, fontweight="bold")
vc.plot(*J3F[:2], "+", color=K, ms=9, mew=LW_T); cline(vc, (J3F[0] - 14, J3F[1]), (J3F[0] + 14, J3F[1])); cline(vc, (J3F[0], J3F[1] - 14), (J3F[0], J3F[1] + 14))
dim(vc, (S_CUT, 18), (J3F[0], 18), 3, f"{J3F[0] - S_CUT:.1f}  cut to J3 axis")
dim(vc, (J3F[0] + 15, 0), (J3F[0] + 15, J3F[1]), 4, f"{abs(J3F[1]):.1f}")
cline(vc, (213, 0), (350, 0)); text(vc, (296, 1), "bar centre line", ha="center", va="bottom", fs=6)
leader(vc, (J3F[0] - 7.1, J3F[1] - 7.1), (J3F[0] - 26, J3F[1] - 24), "Ø20 J3 pad, Ø7 pin x 7.5 (MR117 pair)", ha="right")
off = float(AEB["tongue_offset_from_channel_centre_mm"])
dim(vc, (S_CUT - 14, 0), (S_CUT - 14, off), -5, f"{abs(off):.2f}")
text(vc, (S_CUT - 41, -21), "10.18 = tongue offset from the bar centre", ha="left", va="center", fs=6, bbox=dict(fc="white", ec="none", pad=0.2))
title(20, 150, "DETAIL C  -  ARM END, TOP VIEW   1:1")
# ---- VIEW D: end view looking down the bar from the top end (1:1): the pad plane vs the channel plane
xd, yd = (-80.0, 30.0), (-34.0, 16.0)
vd = mm(170, 76, xd[1] - xd[0], yd[1] - yd[0], xd, yd)
view(vd, hlr(PART, uB, vB), hidden=False)
vd.plot([-78, 28], [TOP] * 2, color=K, lw=LW_T, ls=(0, (2, 1.5))); text(vd, (28, TOP + 1), "bar top (datum B)", ha="right", va="bottom", fs=6)
kp = u(np.array([k3l[1], k3l[2]])); pad_dir = np.array([kp[1], -kp[0]])
cline(vd, J3F[1:] - 20 * kp, J3F[1:] + 22 * kp); text(vd, J3F[1:] + 23 * kp, "J3", ha="center", va="bottom", fs=7.5, fontweight="bold")
ang = float(B["arm end"]["planes_deg"]); c0 = J3F[1:]
pd = pad_dir if pad_dir[0] < 0 else -pad_dir; a_pad = math.degrees(math.atan2(pd[1], pd[0])) % 360
cline(vd, c0 + 44 * pd, c0 - 8 * pd); vd.plot([c0[0] - 44, c0[0] + 8], [c0[1], c0[1]], color=K, lw=LW_T, ls=(0, (2, 1.5)))
text(vd, c0 + 45 * pd, "pad plane ", ha="right", va="center", fs=6); text(vd, (c0[0] - 45, c0[1]), "parallel to bar top ", ha="right", va="center", fs=6)
angdim(vd, c0, 34, min(180.0, a_pad), max(180.0, a_pad), f"{abs(a_pad - 180):.1f}°")
title(172, 150, "VIEW D  -  END VIEW, DOWN THE BAR   1:1")
# ---- notes / table
ny = 224; nx = 262
notes = [("CUT YOUR BOTTOM BAR", True),
         (f"Cut square to the bar at s = {S_CUT:.1f} mm from the elbow-hinge axis (datum A).", False),
         (f"Remove {S_END - S_CUT:.1f} mm from the top end: original eye-to-top {S_END - S_EYE:.1f} -> kept {S_CUT - S_EYE:.1f} mm.", False),
         ("Your cuff holes (3x2 M4 at s 94.25 / 124.25 / 154.25, v +-8.75) stay as they are.", False),
         ("", False),
         ("ARM END (fused into the bar's channel, one part)", True),
         (f"J3 axis passes through GH; pad face {F3:.2f} mm from GH; at s {J3F[0]:.1f}, {abs(J3F[1]):.1f} off the bar centre,", False),
         (f"pad face {TOP - J3F[2]:.1f} below the bar top (datum B); pad plane tilted {abs(a_pad - 180):.1f}° to the bar top (VIEW D).", False),
         (f"Strap 8 x 3; pad plane vs channel plane {ang:.1f}° about a line {AEB['common_line_behind_J3_mm']:.1f} mm behind J3;", False),
         (f"crossing {AEB['crossing_mm_below_J3']:.0f} mm below J3; turns R{AEB['turn_pad_plane_R']:g} (pad plane), R{AEB['turn_channel_plane_R']:g} (channel); bend R{AEB['bend_R']:g}.", False),
         (f"Tongue {abs(off):.2f} mm off the channel centre, embedded {AEB['embedded_in_web_mm']:g} mm in the web.", False),
         ("", False),
         ("UPPER-ARM CUFF (under the bar, for reference)", True),
         (f"Straight extrusion s {CUF and 83.85:.2f} -> 164.65 = {CUF['length']:.1f} long; U: flat {CUF['flat_width']:.0f}, side arcs R{CUF['side_arc_R']},", False),
         (f"wrap {CUF['wrap_deg']:.0f}° each side, {CUF['shell']:.0f} mm wall, centred {CUF['centre_across_bar']:+.0f} mm across the bar; 2 mm liner inside.", False),
         ("", False),
         ("Hidden lines omitted in A, B, D. Phantom = material removed from your bar.", False),
         ("All edges R0.5 unless shown. Projected from the built STEP solid.", False)]
for s_, bold in notes:
    bd.text(nx, ny, s_, fontsize=6.6, color=K, family="DejaVu Sans", va="top", fontweight="bold" if bold else "normal"); ny -= 4.6 if s_ else 2.5
for ext in ("pdf", "png"):
    fig.savefig(os.path.join(OUT, f"D6-04_BOTTOM_arm_end_drawing.{ext}"), dpi=220 if ext == "png" else None)
json.dump(dict(s_eye=S_EYE, s_end_original=S_END, s_cut=S_CUT, removed=S_END - S_CUT, kept=S_CUT - S_EYE, part_overall=S_PEND - S_EYE,
               j3_face_svh=J3F.round(2).tolist(), j3_axis_svh=k3l.round(4).tolist()), open(os.path.join(OUT, "D6-04_cut.json"), "w"), indent=1)
print(f"original {S_EYE:.2f}..{S_END:.2f} ({S_END - S_EYE:.1f}); cut {S_CUT}; remove {S_END - S_CUT:.1f}; kept {S_CUT - S_EYE:.1f}; part to {S_PEND:.1f}; J3 {J3F.round(1)}")
