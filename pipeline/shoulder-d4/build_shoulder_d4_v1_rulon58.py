"""EXO shoulder, design D4: four-pivot spherical shoulder (one spare DOF), 124 mm envelope, thin skin-riding Ti links.

Kinematics from the morphology search (arm-rom/opt_D.py -> opt_D_124_c4_p180.json, 86% of 3,993 natural poses against
the BodyParts3D body): every pivot axis passes through the shoulder centre; J1 on the scapula, J4 (the post) on the
upper-arm bar; links alternate inner / outer shell so consecutive links stack at their shared pivot.

Pivot standard (EXO powered-axis joint, see memory thin-joint-bearing-stack):
  inner link: Ti hub plate + integral Ø20 h6 boss (Ø10 through-bore for cables), M20x1.0 thread at the boss tip
  2x Rulon J thrust washers, McMaster 7488K15 (1" ID x 2" OD x 1/8"), riding bare Ti faces (duplex, zero lash)
  outer link: Ti hub disc with a 6704-2Z bearing (McMaster 6656K198) pressed in; inner race slip-fit on the boss,
    0.25 mm axial float each side (radial only; the washers own axial)
  17-4PH H900 flanged cap nut M20x1.0: snug to first drag, back off 3-5 deg, lock with a radial M3 nylon-tip setscrew
  tendon drum: two grooves on the outer hub rim (Ø58)

Frames: built in the thorax frame (x anterior, y up, z right, mm, origin = right shoulder centre, arm hanging, scapula
at rest), exported in the RIGHT ARM SUBASSY CAD frame (X posterior, Y lateral, Z up; shoulder centre at (-119.5, 0, 0)).

    python3 build_shoulder_d4.py      -> shoulder_d4.step, shoulder_d4.glb, report.txt
"""
import json, math, os, sys
import numpy as np
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__)); ROM = os.path.join(HERE, "..", "arm-rom")
sys.path.insert(0, ROM)
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180")
import design_search as D, design_search_families as F, design_search_anat as A
from design_search_pivots import w_dir

# ---------------------------------------------------------------- design + display pose
DES = json.load(open(os.path.join(ROM, "opt_D_124_c4_p180.json")))[0]
b = np.asarray(DES["b"], float); a1, a2, a3 = (DES[k] * D.D2R for k in ("a1", "a2", "a3")); W = w_dir(DES["delta"], DES["waz"])
e_ = np.cross(b, [0.0, 1, 0]); e_ /= np.linalg.norm(e_); f_ = np.cross(b, e_)
def pins_for(Hg, q):
    u4 = Hg @ W; c2 = math.cos(a1) * b + math.sin(a1) * (math.cos(q) * e_ + math.sin(q) * f_)
    c3, ok = F.circ_int(c2[None], a2, u4[None], a3, DES["branch"])
    ok = ok[0] and F.triangle_ok(c2[None], u4[None], a2, a3)[0] and F.triangle_ok(b[None], c3, a1, a2)[0]
    return dict(b=b, c2=c2, c3=c3[0], u4=u4), bool(ok)

R_IN = 122.0                       # centreline of the inner links (inner face 119 mm: the searched shell)
T_PLATE, T_WASH, T_DISC, T_CAPF, H_CAP = 6.0, 3.175, 6.0, 3.0, 6.0
R_OUT = R_IN + T_PLATE / 2 + T_WASH + T_DISC / 2      # centreline of the outer links
HUB_D, BOSS_D, BORE_D = 58.0, 20.0, 10.0
WASH_ID, WASH_OD, BRG_ID, BRG_OD, BRG_W = 25.4, 50.8, 20.0, 27.0, 4.0
STRIP_W, STRIP_T, RIB_W, RIB_H = 22.0, 6.0, 6.0, 6.0

pose0 = (0, 0, 0)
H0 = D.Ry(0) @ D.Rx(0) @ D.Ry(0); Rs0 = D.scapula(0); Hg0 = Rs0.T @ H0
best = None
for qd in np.arange(0, 360, 2):
    P, ok = pins_for(Hg0, math.radians(qd))
    if ok:
        best = qd if best is None else best
Q0 = None
# choose the middle of the longest run of valid spare-joint angles at the display pose (from the search's checks)
valid = []
for qd in np.arange(0, 360, 2):
    P, ok = pins_for(Hg0, math.radians(qd))
    if ok:
        pts = np.concatenate([D.slerp_pts(P["b"][None], P["c2"][None], 9)[0], D.slerp_pts(P["c2"][None], P["c3"][None], 9)[0], D.slerp_pts(P["c3"][None], P["u4"][None], 9)[0]])
        Pt = pts * (R_IN - 3); dt = A.lookup(A.TRUNK[0], Pt); da = A.lookup(A.ARM, Pt @ Hg0)
        near = np.degrees(np.arccos(np.clip(pts @ P["u4"], -1, 1))) < 15        # where the bar meets the arm (search rule)
        if dt.min() >= 4 and da[~near].min() >= 4: valid.append(qd)
runs, cur = [], [valid[0]]
for v in valid[1:]:
    if v - cur[-1] <= 2: cur.append(v)
    else: runs.append(cur); cur = [v]
runs.append(cur); run = max(runs, key=len); Q0 = run[len(run) // 2]
PINS, _ = pins_for(Hg0, math.radians(Q0))

# ---------------------------------------------------------------- geometry helpers (thorax frame)
def V(p): return cq.Vector(float(p[0]), float(p[1]), float(p[2]))
def disc(axis, z0, z1, d, d_in=0.0):
    """annulus coaxial with a pivot axis (through the origin), between radii z0..z1 along the axis"""
    n = np.asarray(axis, float); n /= np.linalg.norm(n)
    s = cq.Solid.makeCylinder(d / 2, z1 - z0, V(n * z0), V(n))
    if d_in > 0: s = s.cut(cq.Solid.makeCylinder(d_in / 2, z1 - z0 + 0.2, V(n * (z0 - 0.1)), V(n)))
    return s
def strip(A_, B_, r, w=STRIP_W, t=STRIP_T, rib=True):
    """curved link: rectangular section (t radial x w across) swept on the great circle A->B at radius r, + outer rib.
    The strip starts / ends 3 mm inside each hub disc (so it fuses with it) and never enters the boss / cap zone;
    the rib stops short of the caps and of the stacked neighbour's disc."""
    A_ = np.asarray(A_, float); B_ = np.asarray(B_, float); n = np.cross(A_, B_); n /= np.linalg.norm(n)
    tot = math.acos(np.clip(A_ @ B_, -1, 1))
    def section(r0, r1, hw, d0, d1):
        a0 = math.asin(min(0.99, d0 / r)); a1_ = math.asin(min(0.99, d1 / r))
        S = math.cos(a0) * A_ + math.sin(a0) * np.cross(n, A_)                 # start direction, rotated a0 toward B
        pts = [S * r0 + n * -hw, S * r1 + n * -hw, S * r1 + n * hw, S * r0 + n * hw]
        wire = cq.Wire.makePolygon([V(p) for p in pts], close=True); face = cq.Face.makeFromWires(wire)
        return cq.Solid.revolve(face, math.degrees(tot - a0 - a1_), cq.Vector(0, 0, 0), V(n))
    s = section(r - t / 2, r + t / 2, w / 2, HUB_D / 2 - 3, HUB_D / 2 - 3)
    if rib: s = s.fuse(section(r + t / 2 - 0.5, r + t / 2 + RIB_H, RIB_W / 2, HUB_D / 2 + 4, HUB_D / 2 + 4))
    return s
def tendon_grooves(axis, zc, d):
    n = np.asarray(axis, float); n /= np.linalg.norm(n); out = None
    for dz in (-1.6, 1.6):
        g = cq.Solid.makeTorus(d / 2, 0.9, V(n * (zc + dz)), V(n))
        out = g if out is None else out.fuse(g)
    return out

def inner_hub(axis):      # plate + boss with cable bore, M20 tip (thread modelled at major diameter, as tapped holes are)
    z0 = R_IN - T_PLATE / 2
    top = R_IN + T_PLATE / 2 + T_WASH + T_DISC + T_WASH + T_CAPF + H_CAP
    hub = disc(axis, z0, R_IN + T_PLATE / 2, HUB_D).fuse(disc(axis, R_IN + T_PLATE / 2 - 0.1, top, BOSS_D))
    return hub.cut(disc(axis, z0 - 1, top + 1, BORE_D))
def outer_hub(axis):      # disc with bearing seat + tendon drum grooves
    z0 = R_IN + T_PLATE / 2 + T_WASH
    d = disc(axis, z0, z0 + T_DISC, HUB_D, BRG_OD)
    return d.cut(tendon_grooves(axis, z0 + T_DISC / 2, HUB_D + 1.2))
def joint_hardware(axis):
    z = R_IN + T_PLATE / 2
    w1 = disc(axis, z, z + T_WASH, WASH_OD, WASH_ID)
    zd = z + T_WASH
    brg = disc(axis, zd + (T_DISC - BRG_W) / 2, zd + (T_DISC + BRG_W) / 2, BRG_OD, BRG_ID)
    w2 = disc(axis, zd + T_DISC, zd + T_DISC + T_WASH, WASH_OD, WASH_ID)
    zc = zd + T_DISC + T_WASH
    cap = disc(axis, zc, zc + T_CAPF, 52.0, BOSS_D).fuse(disc(axis, zc + T_CAPF - 0.1, zc + T_CAPF + H_CAP, 30.0, BOSS_D))
    # radial M3 setscrew hole (tap drill 2.5) through the cap body
    n = np.asarray(axis, float); n /= np.linalg.norm(n); t = np.cross(n, [0, 0, 1.0]); t = t / np.linalg.norm(t) if np.linalg.norm(t) > 1e-6 else np.array([1.0, 0, 0])
    hole = cq.Solid.makeCylinder(1.25, 20, V(n * (zc + T_CAPF + H_CAP / 2) - t * 10), V(t))
    return dict(washer_a=w1, bearing=brg, washer_b=w2, cap=cap.cut(hole))

# ---------------------------------------------------------------- parts
pb, pc2, pc3, pu4 = (PINS[k] / np.linalg.norm(PINS[k]) for k in ("b", "c2", "c3", "u4"))
parts, colors = {}, {}
# scapula base: inner hub at J1 + stand-off column to a mounting flange just off the skin (strap / back-plate interface)
r_skin = next(r for r in np.arange(40, 125, 1.0) if A.lookup(A.TRUNK[0], (pb * r)[None])[0] > 2.0)
base = inner_hub(pb).fuse(disc(pb, r_skin + 4, R_IN - T_PLATE / 2 + 0.1, 30.0, BORE_D)).fuse(disc(pb, r_skin + 4, r_skin + 8, 64.0, BORE_D))
for k in range(4):                                     # 4x M4 tapped (Ø3.3) on a Ø50 circle in the flange
    t = np.cross(pb, [0, 1.0, 0]); t /= np.linalg.norm(t); s_ = np.cross(pb, t); ang = k * math.pi / 2
    c = pb * (r_skin + 3) + 25 * (math.cos(ang) * t + math.sin(ang) * s_)
    base = base.cut(cq.Solid.makeCylinder(1.65, 7, V(c), V(pb)))
parts["D4-01 scapula base (7075-T6, hard anodised)"] = base
parts["D4-02 link 1 (7075-T6, hard anodised)"] = strip(pb, pc2, R_OUT).fuse(outer_hub(pb)).fuse(outer_hub(pc2))
parts["D4-03 link 2 (7075-T6, hard anodised)"] = strip(pc2, pc3, R_IN).fuse(inner_hub(pc2)).fuse(inner_hub(pc3))
parts["D4-04 link 3 (7075-T6, hard anodised)"] = strip(pc3, pu4, R_OUT).fuse(outer_hub(pc3)).fuse(outer_hub(pu4))
# upper-arm bar: inner hub at J4 (the post), straight 22 x 8 bar down the lateral arm to the elbow interface
L = json.load(open(os.path.join(ROM, "body_mesh.json")))["landmarks"]
elbow = np.asarray(L["elbow"]); ex = np.asarray(L["elbow_axis"]); epi = np.linalg.norm(np.asarray(L["epi_l"]) - elbow)
E_hub = elbow + ex / np.linalg.norm(ex) * (epi + 22.0)              # elbow pivot boss, lateral, on the exo elbow axis
P_hub = pu4 * R_IN
dirb = (E_hub - P_hub) / np.linalg.norm(E_hub - P_hub)
side = np.cross(dirb, pu4); side /= np.linalg.norm(side); up = np.cross(side, dirb)
def box_between(p0, p1, w, t):
    ln = np.linalg.norm(p1 - p0); dz = (p1 - p0) / ln
    pl = cq.Plane(origin=V(p0), xDir=V(side), normal=V(dz))
    return cq.Workplane(pl).rect(w, t).extrude(ln).val()
bar = box_between(P_hub, E_hub, 22.0, 8.0).fuse(inner_hub(pu4))
ehub = cq.Solid.makeCylinder(20.0, 10.0, V(E_hub - ex * 5), V(ex)).cut(cq.Solid.makeCylinder(10.0, 12.0, V(E_hub - ex * 6), V(ex)))
bar = bar.fuse(ehub)
for s_mm in (94.25, 124.25, 154.25):                               # M4 tapped pairs for the upper-arm cuff (EXO cuff standard)
    c = E_hub - dirb * s_mm
    for dy in (-8.75, 8.75):
        bar = bar.cut(cq.Solid.makeCylinder(1.65, 12, V(c + side * dy - up * 6), V(up)))
parts["D4-05 upper-arm bar (7075-T6, hard anodised)"] = bar
for j, ax in (("J1", pb), ("J2", pc2), ("J3", pc3), ("J4", pu4)):
    hw = joint_hardware(ax)
    parts[f"{j} Rulon J thrust washer A (McMaster 7488K15)"] = hw["washer_a"]
    parts[f"{j} Rulon J thrust washer B (McMaster 7488K15)"] = hw["washer_b"]
    parts[f"{j} 6704-2Z bearing (McMaster 6656K198)"] = hw["bearing"]
    parts[f"{j} cap nut M20x1.0, 17-4PH H900"] = hw["cap"]

# ---------------------------------------------------------------- checks
report = []
report.append(f"design: base az {DES['az']} el {DES['el']}, arcs {DES['a1']}/{DES['a2']}/{DES['a3']} deg, post delta {DES['delta']} az {DES['waz']} -> searched coverage {100 * DES['cov']:.1f}%")
report.append(f"display pose: arm hanging, spare joint J1 at {Q0} deg (middle of its {len(run) * 2} deg valid band)")
report.append(f"inner links at r = {R_IN} mm (inner face {R_IN - 3:.0f}), outer links at r = {R_OUT:.1f} mm; top of caps r = {R_IN + T_PLATE / 2 + 2 * T_WASH + T_DISC + T_CAPF + H_CAP + 0:.1f} mm")
# pairwise interference (volume) between parts that are not mates
names = list(parts); clash = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        try:
            v = parts[names[i]].intersect(parts[names[j]]).Volume()
            if v > 2.0: clash.append((names[i], names[j], round(v, 1)))
        except Exception: pass
report.append("interference (> 2 mm^3): " + ("none" if not clash else "; ".join(f"{a} x {b_}: {v}" for a, b_, v in clash)))
# hardware skin clearance over the motion range: transform each moving part with its link frame
def frame(a, c):
    n = c - (a @ c) * a; n /= np.linalg.norm(n); return np.c_[a, n, np.cross(a, n)]
F0 = dict(base=np.eye(3), l1=frame(pb, pc2), l2=frame(pc2, pc3), l3=frame(pc3, pu4), bar=Hg0)
group = {"D4-01": "base", "D4-02": "l1", "D4-03": "l2", "D4-04": "l3", "D4-05": "bar", "J1": "l1", "J2": "l2", "J3": "l2", "J4": "bar"}
samples = {}
for nm, s in parts.items():
    vs, _ = s.tessellate(1.5); P = np.array([[v.x, v.y, v.z] for v in vs])
    samples[nm] = P[:: max(1, len(P) // 400)]
rng = np.random.default_rng(0); idx = rng.choice(len(D.POSES), 400, replace=False)
okp = tot = 0; worst = {}
for n in idx:
    pl, el, ax, Hg, Rs = D.POSES[n]; eb = A.EBIN_ALL[n]; Hf = A.HF_ALL[n]
    best_q = None
    for qd in np.arange(0, 360, 6):
        P, ok = pins_for(Hg, math.radians(qd))
        if not ok: continue
        Fp = dict(base=np.eye(3), l1=frame(P["b"], P["c2"]), l2=frame(P["c2"], P["c3"]), l3=frame(P["c3"], P["u4"]), bar=Hg)
        mins = []
        for nm, X in samples.items():
            g = group[nm.split(" ")[0]]; Rg = Fp[g] @ F0[g].T; Xp = X @ Rg.T
            if g == "base": Xp = Xp[np.linalg.norm(Xp, axis=1) > R_IN - T_PLATE / 2 - 0.5]     # mounting column / flange excluded
            dt = A.lookup(A.TRUNK[eb], Xp @ Rs.T).min()
            if g == "bar": da = 100.0
            else:
                uu = Fp["l3"][:, 0]; far = (Xp @ uu) / (np.linalg.norm(Xp, axis=1) + 1e-9) < math.cos(math.radians(15))
                da = A.lookup(A.ARM, Xp[far] @ Hf).min() if far.any() else 100.0
            mins.append((min(dt, da), nm))
        m = min(mins)
        if best_q is None or m[0] > best_q[0]: best_q = (m[0], qd, m[1])
    if best_q is None: continue
    tot += 1
    if best_q[0] >= 2.0: okp += 1
    else: worst[best_q[2]] = worst.get(best_q[2], 0) + 1
report.append(f"hardware skin check: {okp}/{tot} kinematically valid sampled poses keep every part >= 2 mm off the skin; limiting parts otherwise: {dict(sorted(worst.items(), key=lambda t: -t[1])[:4])}")

# ---------------------------------------------------------------- export (CAD frame of RIGHT ARM SUBASSY)
X0 = np.array([-119.5, 0.0, 0.0])
Mcad = np.array([[-1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])            # thorax -> CAD axes
from OCP.gp import gp_Trsf
_t = gp_Trsf(); _t.SetValues(*Mcad[0], X0[0], *Mcad[1], X0[1], *Mcad[2], X0[2]); loc = cq.Location(_t)
def mat(c): return cq.Color(*c)
COL = {"Ti": (0.10, 0.10, 0.11), "Rulon": (0.86, 0.72, 0.30), "6704": (0.75, 0.77, 0.80), "cap": (0.62, 0.64, 0.66)}
assy = cq.Assembly(name="EXO shoulder D4")
for nm, s in parts.items():
    c = COL["Rulon"] if "Rulon" in nm else COL["6704"] if "6704" in nm else COL["cap"] if "cap" in nm else COL["Ti"]
    assy.add(s, name=nm.replace(" ", "_").replace("(", "").replace(")", "").replace(",", ""), color=mat(c), loc=loc)
assy.save(os.path.join(HERE, "shoulder_d4.step"))
try: assy.save(os.path.join(HERE, "shoulder_d4.glb"))
except Exception as ex_: report.append(f"glb export failed: {ex_}")
mass = sum(s.Volume() * (2.81e-3 if "7075" in nm else 7.8e-3 if ("cap" in nm or "6704" in nm) else 2.2e-3) for nm, s in parts.items())
report.append(f"mass estimate: {mass:.0f} g (7075-T6 2.81, steel 7.8, Rulon 2.2 g/cc)")
bom = ["BOM (per shoulder):", "  4x 6704-2Z deep-groove bearing 20x27x4 - McMaster 6656K198",
       "  8x Rulon J thrust washer 1\" ID x 2\" OD x 1/8\" - McMaster 7488K15",
       "  4x cap nut M20x1.0, 17-4PH H900 (machined, D4-06)", "  4x M3 nylon-tip set screw (cap lock)",
       "  4x M4 socket head screw (base flange to back plate); 6x M4 countersunk (cuff to bar)",
       "  7075-T6, hard anodised: D4-01 base, D4-02 link 1, D4-03 link 2, D4-04 link 3, D4-05 upper-arm bar (stub)"]
open(os.path.join(HERE, "report.txt"), "w").write("\n".join(report + [""] + bom) + "\n")
print("\n".join(report + bom))
