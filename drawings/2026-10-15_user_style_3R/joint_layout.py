"""One-sheet joint layout of the user-style 3R (champion r20 s1414 #4): joint axes, positions, angles, separations.
Numbers come from the kinematics (tools: docs/concepts/viz/kin.js conventions, re-derived here) and are cross-checked
against the built CAD frames (pipeline/full-exo/designs/param2_r20_n3_s1414_4)."""
import json, math, os, sys
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = "/home/user/exo-shoulder"; sys.path.insert(0, R + "/pipeline/conformal/param_cad"); sys.path.insert(0, R + "/pipeline/conformal/band_cad")
sys.path.insert(0, R + "/pipeline/avg")
import param_build as PB, arm_end as AE, body_pose as BP
D = R + "/pipeline/full-exo/designs/param2_r20_n3_s1414_4"
OUT = os.path.dirname(os.path.abspath(__file__))
u = lambda v: np.asarray(v, float) / np.linalg.norm(v)
# --- kinematics at the HOME pose (arm hanging straight down, plane 0 / elev 0 / axial 0: scapula = humerus = rig frame,
#     all three joint angles 0). Frame: x anterior, y up, z lateral (right shoulder), origin = GH centre, mm.
FR = PB.FR; C, ax = FR.load(PB.BAND)
cl = json.load(open(D + "/clips.json"))["clips"]
f0 = cl[0]["frames"][0]; X0 = FR.frame_of(f0); S0 = BP.scap(f0["p"][1])
J1s = S0.T @ (X0["base"][0] @ ax["J1"][1])                       # J1 in the scapula frame (fixed)
RH = X0["H"][0]; J3h = RH.T @ (X0["l2"][0] @ ax["J3"][1])         # J3 in the arm (body-pose humerus) frame (fixed)
b, a12, a23 = u(J1s), 76.90180446920043, 66.74921235407174
# home: the band humerus frame H = I; the body-pose humerus frame Hb = H rest_humerus^T (kin.js) -> J3 world at home:
Hb0 = AE.HR.T                                                       # RH = H HR^T (checked: 0.0 error at frame 0)
w = u(Hb0 @ J3h)
import numpy.linalg as _la
wd = (86.32769021001913, 21.829657347343378)   # cross-check: the band wdir of the chain

def circ_int(c1, r1, c2, r2, sgn):                                 # unit vector at angle r1 from c1 and r2 from c2
    c1, c2 = u(c1), u(c2); c = np.cross(c1, c2); g = c1 @ c2
    A = np.array([c1, c2]); rhs = np.cos(np.radians([r1, r2]))
    x0 = np.linalg.lstsq(A, rhs, rcond=None)[0] @ A if False else None
    M = np.array([[1, g], [g, 1]]); al, be = np.linalg.solve(M, rhs); p = al * c1 + be * c2
    h2 = 1 - p @ p; return u(p + sgn * math.sqrt(max(h2, 0)) * u(c))
cands = [circ_int(b, a12, w, a23, s) for s in (1, -1)]
# pick the branch the CAD uses: J2 in the CAD at frame 0, carried back to home through the scapula rotation
J2cad = S0.T @ (X0["l2"][0] @ ax["J2"][1])
p2 = max(cands, key=lambda c: c @ u(J2cad))
F = {"J1": 53.38, "J2": 93.18, "J3": 71.85}; STACK, HUB_D = 12.25, 20.0
Bd = json.load(open(D + "/build.json"))["faces"]; F = {k: float(Bd[k]) for k in ("J1", "J2", "J3")}
axes = {"J1": b, "J2": p2, "J3": w}
P = {k: F[k] * axes[k] for k in axes}
ang = lambda x, y: math.degrees(math.acos(max(-1, min(1, x @ y))))
assert abs(ang(b, p2) - a12) < 0.05 and abs(ang(p2, w) - a23) < 0.05, (ang(b, p2), ang(p2, w))
# BOTTOM bar frame (arm-fixed, the user's part): elbow-hinge point CB, up the bar uB, across vB, normal axB (arm rest frame)
uB, CB, vB, axB = (np.asarray(x, float) for x in (AE.uB, AE.CB, AE.vB, AE.axB))
toW = lambda p_: Hb0 @ np.asarray(p_, float)                       # arm rest frame -> home world
bar = lambda s_: toW(CB + s_ * uB)
GH_bar = ((-CB) @ uB, (-CB) @ vB, (-CB) @ axB)
J3f_bar = tuple((F["J3"] * J3h - CB) @ np.array([uB, vB, axB]).T)
# joint ranges over the 8 fit clips (followed frames), from the CAD's own per-frame joint angles q
_jr = json.load(open(OUT + "/joint_ranges.json"))   # node: KIN.sph3r closed form on every followed clip frame, unwrapped
def unwrap_range(x):
    x = np.degrees(np.unwrap(np.radians(x))) if False else x
    return x.min(), x.max()
rng = [(_jr["lo"][i], _jr["hi"][i]) for i in range(3)]
azel = lambda v: (math.degrees(math.atan2(v[2], v[0])), math.degrees(math.asin(v[1])))   # azimuth from anterior toward lateral, elevation above horizontal
d12, d23, d13 = (float(np.linalg.norm(P[a_] - P[b_])) for a_, b_ in (("J1", "J2"), ("J2", "J3"), ("J1", "J3")))
# ---------------------------------------------------------------- drawing
INK, MUTE, ACC = "#1b2430", "#7b8794", "#b4441b"; J = {"J1": "#1f5fa8", "J2": "#1b2430", "J3": "#2e7d4f"}
DIM = "#b4441b"
fig = plt.figure(figsize=(16.54, 11.69)); fig.patch.set_facecolor("white")
fig.text(0.015, 0.968, "3R SHOULDER EXO - JOINT LAYOUT", fontsize=18, fontweight="bold", color=INK)
fig.text(0.015, 0.948, "Right shoulder. Origin = GH centre (centre of the humeral head); every joint axis passes through it. Frame: x anterior, y up, z lateral. "
         "Units mm / deg. Pose: HOME = arm hanging straight down, all joints at 0.", fontsize=9.5, color=INK)
def hub(axv, c, d, n, k, lab=True):                       # hub as its true section: face at c, stack 12.25 along d, O20
    d = d / np.linalg.norm(d); n = n / np.linalg.norm(n); h = HUB_D / 2
    q = [c + n * h, c + n * h + d * STACK, c - n * h + d * STACK, c - n * h, c + n * h]
    axv.fill(*zip(*q), color=J[k], alpha=0.18, lw=0); axv.plot(*zip(*q), color=J[k], lw=1.2)
def dim_line(axv, a, b, txt, off, tpos=0.5, rot=True, fs=8.5):
    a, b = np.asarray(a, float), np.asarray(b, float); d = b - a; L = np.linalg.norm(d); t = d / L; n = np.array([-t[1], t[0]]) * off
    A, B = a + n, b + n
    for p_, q_ in ((a, A), (b, B)): axv.plot(*zip(p_ + 0.15 * n, q_ + 0.25 * np.sign(off) * n / max(abs(off), 1e-9) * 2), color=DIM, lw=0.5)
    axv.annotate("", xy=B, xytext=A, arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.7, shrinkA=0, shrinkB=0, mutation_scale=8))
    m = A + (B - A) * tpos; ang_ = math.degrees(math.atan2(t[1], t[0]))
    if ang_ > 90: ang_ -= 180
    if ang_ < -90: ang_ += 180
    axv.text(*(m + n / max(abs(off), 1e-9) * 4.5 * np.sign(off)), txt, color=DIM, fontsize=fs, ha="center", va="center", rotation=ang_ if rot else 0,
             bbox=dict(fc="white", ec="none", pad=0.6))
def arc(axv, r, a0, a1, txt):
    t = np.radians(np.linspace(a0, a1, 60)); axv.plot(r * np.cos(t), r * np.sin(t), color=DIM, lw=0.8)
    for tt, s_ in ((t[0], 1), (t[-1], -1)):
        axv.annotate("", xy=(r * np.cos(tt), r * np.sin(tt)), xytext=(r * np.cos(tt + s_ * 0.06), r * np.sin(tt + s_ * 0.06)),
                     arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.7, mutation_scale=8))
    tm = np.radians((a0 + a1) / 2); axv.text((r + 9) * np.cos(tm), (r + 9) * np.sin(tm), txt, color=DIM, fontsize=10, fontweight="bold", ha="center", va="center",
                                             bbox=dict(fc="white", ec="none", pad=0.6))
# --- TRUE VIEWS of each link plane (the plane through GH containing both joint axes): true angle, true distances
def true_view(rect, ka, kb, link, extra):
    axv = fig.add_axes(rect); axv.set_aspect("equal"); axv.axis("off")
    ea = axes[ka]; nrm = np.cross(axes[ka], axes[kb]); nrm /= np.linalg.norm(nrm); eb = np.cross(nrm, ea)
    pr = lambda p_: np.array([p_ @ ea, p_ @ eb])
    A2, B2 = pr(axes[ka]), pr(axes[kb]); th = ang(axes[ka], axes[kb])
    for k, v2, Fk in ((ka, A2, F[ka]), (kb, B2, F[kb])):
        axv.plot(*zip((0, 0), v2 * (Fk + STACK + 30)), color=J[k], lw=0.8, ls=(0, (10, 3, 2, 3)))
        axv.text(*(v2 * (Fk + STACK + 24)), k, color=J[k], fontsize=13, fontweight="bold", ha="center", va="center")
        hub(axv, v2 * Fk, v2, np.array([-v2[1], v2[0]]), k)
    pa, pb = A2 * F[ka], B2 * F[kb]
    axv.plot(*zip(pa, pb), color=INK, lw=1.6); axv.text(*((pa + pb) / 2 + np.array([4, 4])), link, fontsize=9, color=INK, fontweight="bold")
    arc(axv, 30, 0, th, f"{th:.2f}°")
    dim_line(axv, (0, 0), pa, f"{F[ka]:.2f}", -14); dim_line(axv, (0, 0), pb, f"{F[kb]:.2f}", 14)
    dim_line(axv, pa, pb, f"{np.linalg.norm(pa - pb):.1f}", 12)
    axv.plot(0, 0, "o", ms=7, color=ACC); axv.text(-4, -9, "GH", color=ACC, fontsize=10, fontweight="bold", ha="right")
    axv.set_title(f"{link.upper()} - TRUE VIEW of the plane through GH containing the {ka} and {kb} axes", fontsize=10, loc="left", color=INK)
    axv.text(0.0, -0.01, extra, transform=axv.transAxes, fontsize=7.5, color=MUTE, va="top", wrap=True)
    axv.set_xlim(-35, 155); axv.set_ylim(-45, 150)
true_view([0.015, 0.47, 0.30, 0.44], "J1", "J2", "link 1", "Dims: hub skin-side face distance from GH along its axis;\nchord = hub face centre to hub face centre. Hub O20 x 12.25 stack.")
true_view([0.335, 0.47, 0.30, 0.44], "J2", "J3", "link 2", "J2 is shared: link 1 and link 2 both pivot on it\n(same axis, same 93.18 face).")
# --- orthographic placement views, zoomed on the shoulder
def ortho(rect, title, proj, labs):
    axv = fig.add_axes(rect); axv.set_aspect("equal"); axv.axis("off"); axv.set_title(title, fontsize=9.5, loc="left", color=INK)
    pr = lambda p_: np.array(proj(np.asarray(p_, float)))
    E = pr([0, -110, 0])
    if np.linalg.norm(E) > 20: axv.plot(*zip(pr([0, 0, 0]), E), color=MUTE, lw=0.9, ls=(0, (8, 3, 2, 3))); axv.text(*(E + [3, 4]), "arm axis", fontsize=7, color=MUTE)
    for k, v in axes.items():
        e = pr((F[k] + STACK + 18) * v); axv.plot(*zip(pr([0, 0, 0]), e), color=J[k], lw=0.8, ls=(0, (10, 3, 2, 3)))
        a_, b_ = pr(F[k] * v), pr((F[k] + STACK) * v); axv.plot(*zip(a_, b_), color=J[k], lw=5, solid_capstyle="butt")
        axv.text(*(e + (e - pr([0, 0, 0])) / max(np.linalg.norm(e - pr([0, 0, 0])), 1) * 7), k, fontsize=10, fontweight="bold", color=J[k], ha="center", va="center")
    for k1, k2 in (("J1", "J2"), ("J2", "J3")):
        axv.plot(*zip(pr(P[k1]), pr(P[k2])), color=INK, lw=1.1)
    axv.plot(0, 0, "o", ms=5, color=ACC)
    axv.text(0.0, 0.0, labs, transform=axv.transAxes, fontsize=7, color=MUTE)
    axv.set_xlim(-115, 115); axv.set_ylim(-115, 115)
ortho([0.015, 0.05, 0.20, 0.36], "FRONT (from in front)", lambda p_: (-p_[2], p_[1]), "lateral <-   up ^")
ortho([0.225, 0.05, 0.20, 0.36], "SIDE (from the right side)", lambda p_: (p_[0], p_[1]), "anterior ->   up ^")
ortho([0.435, 0.05, 0.20, 0.36], "TOP (from above)", lambda p_: (p_[2], p_[0]), "lateral ->   anterior ^")
# --- tables
L = []
row = L.append
row("JOINT AXES (unit vectors at HOME; all through GH)")
row(f"     {'x':>8s}{'y':>8s}{'z':>8s}  {'fixed to':9s}")
for k, fx in (("J1", "scapula"), ("J2", "links 1+2"), ("J3", "arm")):
    v = axes[k]; row(f"{k:4s}{v[0]:+8.4f}{v[1]:+8.4f}{v[2]:+8.4f}  {fx}")
row("")
row("HUB SKIN-SIDE FACE (distance from GH; hub")
row("O20, stack 12.25 outward from the face)")
for k in ("J1", "J2", "J3"):
    row(f"  {k}: {F[k]:6.2f} mm   centre ({P[k][0]:+6.1f}, {P[k][1]:+6.1f}, {P[k][2]:+6.1f})")
row("")
row("ANGLES BETWEEN AXES")
row(f"  J1-J2  {ang(b, p2):6.2f}  (link 1, fixed)")
row(f"  J2-J3  {ang(p2, w):6.2f}  (link 2, fixed)")
row(f"  J1-J3  {ang(b, w):6.2f}  (at HOME; changes with pose)")
row("")
row("SEPARATION, face centre to face centre")
row(f"  J1-J2  {d12:6.1f} mm  (link 1, fixed)")
row(f"  J2-J3  {d23:6.1f} mm  (link 2, fixed)")
row(f"  J1-J3  {d13:6.1f} mm  (at HOME)")
row("")
row("JOINT ROTATION over the 8 motion clips")
for i, k in enumerate(("J1", "J2", "J3")):
    row(f"  {k}: {rng[i][0]:+6.1f} .. {rng[i][1]:+6.1f}  (span {rng[i][1]-rng[i][0]:5.1f})")
row("")
row("J3 ON YOUR BOTTOM PART (arm-fixed)")
row("  s = up the bar from the elbow-hinge")
row("  point, across = bar width, normal = out")
row("  of the bar face")
row(f"  GH:      s {GH_bar[0]:6.1f}  across {GH_bar[1]:+5.1f}  normal {GH_bar[2]:+6.1f}")
row(f"  J3 face: s {J3f_bar[0]:6.1f}  across {J3f_bar[1]:+5.1f}  normal {J3f_bar[2]:+6.1f}")
row(f"  J3 axis to bar axis    {math.degrees(math.acos(abs(J3h @ uB))):5.1f} deg")
row(f"  J3 axis to bar normal  {math.degrees(math.acos(abs(J3h @ axB))):5.1f} deg")
row("  BOTTOM cut at s 255.0; kept bar 276.2 mm")
row("  (eye end s -21.2 to the cut)")
row("")
row("J1 ON THE SCAPULA HANDLER: its vector above")
row("is scapula-fixed (scapula frame = this frame")
row("at HOME).")
fig.text(0.655, 0.91, "\n".join(L), va="top", ha="left", family="monospace", fontsize=8.8, color=INK, linespacing=1.36)
fig.add_artist(plt.Line2D([0.648, 0.648], [0.05, 0.92], color="#d5dbe1", lw=0.8))
fig.text(0.655, 0.025, "From the kinematics, cross-checked against the built CAD frames (design param2_r20_n3_s1414_4), 2026-10-15.", fontsize=7, color=MUTE)
fig.savefig(OUT + "/joint_layout.png", dpi=150, facecolor="white"); fig.savefig(OUT + "/joint_layout.pdf", facecolor="white")
json.dump(dict(axes={k: v.tolist() for k, v in axes.items()}, faces=F, hub_face_centres={k: v.tolist() for k, v in P.items()},
               angles={"J1-J2": ang(b, p2), "J2-J3": ang(p2, w), "J1-J3_home": ang(b, w)}, separations={"J1-J2": d12, "J2-J3": d23, "J1-J3_home": d13},
               ranges_deg={k: rng[i] for i, k in enumerate(("J1", "J2", "J3"))}, GH_in_bar=GH_bar, J3_face_in_bar=J3f_bar,
               J3_vs_bar_deg=math.degrees(math.acos(abs(J3h @ uB)))), open(OUT + "/joint_layout.json", "w"), indent=1)
print("w (J3 home)", np.round(w, 4), "p2", np.round(p2, 4), "J2cad-home", np.round(u(J2cad), 4))
print(json.dumps(json.load(open(OUT + "/joint_layout.json")), indent=0)[:1500])
