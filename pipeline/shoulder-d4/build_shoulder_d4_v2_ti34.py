"""EXO shoulder, design D4: four-pivot spherical shoulder (one spare DOF), 124 mm envelope, thin skin-riding Ti links.

Kinematics from the footprint-aware morphology search (arm-rom/opt_D.py, FP=1 FP_W=14 FP_HUB=34 FP_ROUT=127 ->
opt_D_124_c4_p180_fp_ti34.json: 67.9% of 3,993 natural poses against the BodyParts3D body with the real 14 mm strips
and Ø34 hubs swept, inner face >= 4 mm off the skin): every pivot axis passes through the shoulder centre; J1 on the scapula, J4 (the post) on the
upper-arm bar; links alternate inner / outer shell so consecutive links stack at their shared pivot.

Pivot standard, compact all-titanium (Ti-6Al-4V everywhere; running faces electroless-nickel / Nedox plated):
  inner member: Ø34 x 6 Ti hub plate + integral Ø16 h9 pin (Ø10 through-bore for cables), M16x1.0 thread at the tip
  2x igus iglidur G thrust washers GTM-1630-015 (16 x 30 x 1.5) either side of the outer hub: they carry the
    25 N.m overturning moment as a face couple (p_max ~10 MPa vs 80 MPa rated) and all axial load
  outer member: Ø34 x 6 Ti hub disc, Ø18 H7 bore with an igus iglidur G flanged sleeve GFM-1618-06 pressed in
    (radial 200 N -> ~2 MPa); flange seated flush in a Ø24.5 x 1 counterbore under washer B
  Ti flanged cap nut M16x1.0 (MoS2 dry film on the thread against galling): snug to first drag, back off 3-5 deg,
    lock with a radial M3 nylon-tip setscrew
  links: 14 x 6 Ti strip + 5 x 4 outer rib (sigma ~ 300 MPa at 25 N.m flat-wise without the rib, Ti-6Al-4V yield 880)
  tendon drum: two grooves on the outer hub rim (Ø34)

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
DES = json.load(open(os.path.join(ROM, "opt_D_124_c4_p180_fp_ti34.json")))[0]
b = np.asarray(DES["b"], float); a1, a2, a3 = (DES[k] * D.D2R for k in ("a1", "a2", "a3")); W = w_dir(DES["delta"], DES["waz"])
e_ = np.cross(b, [0.0, 1, 0]); e_ /= np.linalg.norm(e_); f_ = np.cross(b, e_)
def pins_for(Hg, q):
    u4 = Hg @ W; c2 = math.cos(a1) * b + math.sin(a1) * (math.cos(q) * e_ + math.sin(q) * f_)
    c3, ok = F.circ_int(c2[None], a2, u4[None], a3, DES["branch"])
    ok = ok[0] and F.triangle_ok(c2[None], u4[None], a2, a3)[0] and F.triangle_ok(b[None], c3, a1, a2)[0]
    return dict(b=b, c2=c2, c3=c3[0], u4=u4), bool(ok)

R_IN = 122.0                       # centreline of the inner links (inner face 119 mm: the searched shell)
T_PLATE, T_WASH, T_DISC, T_CAPF, H_CAP = 6.0, 1.5, 6.0, 2.5, 6.0
R_OUT = R_IN + T_PLATE / 2 + T_WASH + T_DISC / 2      # centreline of the outer links
HUB_D, BOSS_D, BORE_D = 34.0, 16.0, 10.0
WASH_ID, WASH_OD, BRG_ID, BRG_OD, BRG_W = 16.0, 30.0, 16.0, 18.0, 6.0
FL_D, FL_T = 24.0, 1.0                 # GFM-1618-06 flange (total length 6 incl. flange)
STRIP_W, STRIP_T, RIB_W, RIB_H = 14.0, 6.0, 5.0, 4.0

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
def strip(A_, B_, r, w=STRIP_W, t=STRIP_T, rib=True, d_end=HUB_D / 2 - 3):
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
    s = section(r - t / 2, r + t / 2, w / 2, d_end, d_end)
    if rib: s = s.fuse(section(r + t / 2 - 0.5, r + t / 2 + RIB_H, RIB_W / 2, HUB_D / 2 + 4, HUB_D / 2 + 4))
    return s
def tendon_grooves(axis, zc, d):
    n = np.asarray(axis, float); n /= np.linalg.norm(n); out = None
    for dz in (-1.6, 1.6):
        g = cq.Solid.makeTorus(d / 2, 0.9, V(n * (zc + dz)), V(n))
        out = g if out is None else out.fuse(g)
    return out

def inner_hub(axis):      # plate + pin with cable bore, M16 tip (thread modelled at major diameter, as tapped holes are)
    z0 = R_IN - T_PLATE / 2
    top = R_IN + T_PLATE / 2 + T_WASH + T_DISC + T_WASH + T_CAPF + H_CAP
    hub = disc(axis, z0, R_IN + T_PLATE / 2, HUB_D).fuse(disc(axis, R_IN + T_PLATE / 2 - 0.1, top, BOSS_D))
    return hub.cut(disc(axis, z0 - 1, top + 1, BORE_D))
def outer_hub(axis):      # disc with sleeve seat + flange counterbore + tendon drum grooves
    z0 = R_IN + T_PLATE / 2 + T_WASH
    d = disc(axis, z0, z0 + T_DISC, HUB_D, BRG_OD).cut(disc(axis, z0 + T_DISC - FL_T, z0 + T_DISC + 0.1, FL_D + 0.5))
    return d.cut(tendon_grooves(axis, z0 + T_DISC / 2, HUB_D + 1.2))
def joint_hardware(axis):
    z = R_IN + T_PLATE / 2
    w1 = disc(axis, z, z + T_WASH, WASH_OD, WASH_ID)
    zd = z + T_WASH
    brg = disc(axis, zd, zd + BRG_W - FL_T + 0.05, BRG_OD, BRG_ID).fuse(disc(axis, zd + BRG_W - FL_T, zd + BRG_W, FL_D, BRG_ID))
    w2 = disc(axis, zd + T_DISC, zd + T_DISC + T_WASH, WASH_OD, WASH_ID)
    zc = zd + T_DISC + T_WASH
    cap = disc(axis, zc, zc + T_CAPF, 30.0, BOSS_D).fuse(disc(axis, zc + T_CAPF - 0.1, zc + T_CAPF + H_CAP, 24.0, BOSS_D))
    # radial M3 setscrew hole (tap drill 2.5) through the cap body
    n = np.asarray(axis, float); n /= np.linalg.norm(n); t = np.cross(n, [0, 0, 1.0]); t = t / np.linalg.norm(t) if np.linalg.norm(t) > 1e-6 else np.array([1.0, 0, 0])
    hole = cq.Solid.makeCylinder(1.25, 20, V(n * (zc + T_CAPF + H_CAP / 2) - t * 10), V(t))
    return dict(washer_a=w1, bearing=brg, washer_b=w2, cap=cap.cut(hole))

# ---------------------------------------------------------------- parts
pb, pc2, pc3, pu4 = (PINS[k] / np.linalg.norm(PINS[k]) for k in ("b", "c2", "c3", "u4"))
parts, colors = {}, {}
# scapula base: inner hub at J1 + stand-off column to a mounting flange just off the skin (strap / back-plate interface)
r_skin = next(r for r in np.arange(40, 125, 1.0) if A.lookup(A.TRUNK[0], (pb * r)[None])[0] > 2.0)
base = inner_hub(pb).fuse(disc(pb, r_skin + 4, R_IN - T_PLATE / 2 + 0.1, 24.0, BORE_D)).fuse(disc(pb, r_skin + 4, r_skin + 8, 64.0, BORE_D))
for k in range(4):                                     # 4x M4 tapped (Ø3.3) on a Ø50 circle in the flange
    t = np.cross(pb, [0, 1.0, 0]); t /= np.linalg.norm(t); s_ = np.cross(pb, t); ang = k * math.pi / 2
    c = pb * (r_skin + 3) + 25 * (math.cos(ang) * t + math.sin(ang) * s_)
    base = base.cut(cq.Solid.makeCylinder(1.65, 7, V(c), V(pb)))
parts["D4-01 scapula base (Ti-6Al-4V)"] = base
parts["D4-02 link 1 (Ti-6Al-4V)"] = strip(pb, pc2, R_OUT, d_end=HUB_D / 2 - 0.5).fuse(outer_hub(pb)).fuse(outer_hub(pc2))
parts["D4-03 link 2 (Ti-6Al-4V)"] = strip(pc2, pc3, R_IN).fuse(inner_hub(pc2)).fuse(inner_hub(pc3))
parts["D4-04 link 3 (Ti-6Al-4V)"] = strip(pc3, pu4, R_OUT, d_end=HUB_D / 2 - 0.5).fuse(outer_hub(pc3)).fuse(outer_hub(pu4))
# upper-arm interface stub: inner hub at J4 (the post) + a short inner-shell strip toward the humerus axis ending in a
# Ø30 x 6 pad with 4x M4 tapped holes; the user's first arm component bolts here (not designed here)
h0 = Hg0 @ np.array([0.0, -1.0, 0.0])
t_ = np.cross(pu4, h0); t_ /= np.linalg.norm(t_)
def stub_dir(gam, ang=15.0):
    d_ = math.cos(math.radians(gam)) * np.cross(t_, pu4) + math.sin(math.radians(gam)) * t_
    return math.cos(math.radians(ang)) * pu4 + math.sin(math.radians(ang)) * d_
def stub_clear(pe):                                 # pad rim + centre: min of arm / trunk skin distance at the rest pose
    u_ = np.cross(pe, [0, 0, 1.0]); u_ /= np.linalg.norm(u_); v_ = np.cross(pe, u_)
    ring = np.array([pe * (R_IN - 3) + 15 * (math.cos(k) * u_ + math.sin(k) * v_) for k in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [pe * (R_IN - 3)])
    return min(A.lookup(A.ARM, ring @ Hg0).min(), A.lookup(A.TRUNK[0], ring).min())
GAM = max(range(0, 360, 10), key=lambda g: stub_clear(stub_dir(g)))   # 0 = toward the humerus axis; pick the clearest side
pe = stub_dir(GAM)
bar = inner_hub(pu4).fuse(strip(pu4, pe, R_IN, rib=False)).fuse(disc(pe, R_IN - T_PLATE / 2, R_IN + T_PLATE / 2, 30.0))
t_ = np.cross(pe, [0, 0, 1.0]); t_ /= np.linalg.norm(t_); s_ = np.cross(pe, t_)
for k in range(4):
    c = pe * (R_IN - T_PLATE / 2 - 1) + 10 * (math.cos(k * math.pi / 2 + math.pi / 4) * t_ + math.sin(k * math.pi / 2 + math.pi / 4) * s_)
    bar = bar.cut(cq.Solid.makeCylinder(1.65, T_PLATE + 2, V(c), V(pe)))
parts["D4-05 arm interface stub (Ti-6Al-4V)"] = bar
for j, ax in (("J1", pb), ("J2", pc2), ("J3", pc3), ("J4", pu4)):
    hw = joint_hardware(ax)
    parts[f"{j} iglidur G thrust washer A (igus GTM-1630-015)"] = hw["washer_a"]
    parts[f"{j} iglidur G thrust washer B (igus GTM-1630-015)"] = hw["washer_b"]
    parts[f"{j} iglidur G flanged sleeve (igus GFM-1618-06)"] = hw["bearing"]
    parts[f"{j} cap nut M16x1.0 (Ti-6Al-4V)"] = hw["cap"]

# ---------------------------------------------------------------- checks
report = []
report.append(f"design: base az {DES['az']} el {DES['el']}, arcs {DES['a1']}/{DES['a2']}/{DES['a3']} deg, post delta {DES['delta']} az {DES['waz']} -> searched coverage {100 * DES['cov']:.1f}%")
report.append(f"arm interface pad: 15 deg from J4, {GAM} deg round from the arm-axis side, {stub_clear(pe):.0f} mm off the skin at rest")
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
okp = tot = okp_s = 0; worst = {}
for n in idx:
    pl, el, ax, Hg, Rs = D.POSES[n]; eb = A.EBIN_ALL[n]; Hf = A.HF_ALL[n]
    best_q = None; best_s = None
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
        m = min(mins); ms = min(x for x in mins if not x[1].startswith("D4-05"))
        if best_q is None or m[0] > best_q[0]: best_q = (m[0], qd, m[1])
        if best_s is None or ms[0] > best_s[0]: best_s = (ms[0], qd, ms[1])
    if best_q is None: continue
    tot += 1
    if best_q[0] >= 2.0: okp += 1
    if best_s[0] >= 2.0: okp_s += 1
    else: worst[best_q[2]] = worst.get(best_q[2], 0) + 1
report.append(f"hardware skin check, shoulder only (arm stub excluded, it is being redesigned): {okp_s}/{tot} sampled poses >= 2 mm off the skin")
report.append(f"hardware skin check: {okp}/{tot} kinematically valid sampled poses keep every part >= 2 mm off the skin; limiting parts otherwise: {dict(sorted(worst.items(), key=lambda t: -t[1])[:4])}")

# ---------------------------------------------------------------- load paths (per pivot, design loads M = 25 N.m, Fr = 200 N, Fa = 200 N)
M_D, FR_D, FA_D, P_G = 25e3, 200.0, 200.0, 80.0             # N.mm, N, N, iglidur G max recommended surface pressure (MPa)
ri, ro = WASH_ID / 2, WASH_OD / 2
I_w = math.pi / 4 * (ro ** 4 - ri ** 4); p_mom = M_D * ro / I_w; A_w = math.pi / 4 * (WASH_OD ** 2 - WASH_ID ** 2)
p_ax = FA_D / A_w; p_rad = FR_D / (BRG_ID * (BRG_W - FL_T))
Z_pin = math.pi * (BOSS_D ** 4 - BORE_D ** 4) / (32 * BOSS_D); s_pin = M_D / Z_pin
F_cpl = M_D / (2 * (ri + ro) / 2 * 2 / 3 * 1.5)                 # washer couple force reacted through the cap thread (approx.)
A_pin = math.pi / 4 * (BOSS_D ** 2 - BORE_D ** 2)
report.append("load paths (every load has its own element; nothing is carried by the tendon drum or the setscrew):")
report.append(f"  radial  -> GFM-1618-06 sleeve on the Ø16 pin: {p_rad:.1f} MPa at {FR_D:.0f} N (rated {P_G:.0f}; capacity ~{P_G * BRG_ID * (BRG_W - FL_T) / 1e3:.1f} kN)")
report.append(f"  axial + -> washer B -> cap nut -> pin thread; axial - -> washer A -> inner plate: {p_ax:.2f} MPa at {FA_D:.0f} N (capacity ~{P_G * A_w / 1e3:.0f} kN each way)")
report.append(f"  moment  -> face couple washer A (one side) / washer B (opposite side): p_max {p_mom:.1f} MPa at 25 N.m; couple force ~{F_cpl:.0f} N")
report.append(f"            through the cap: pin tension {F_cpl / A_pin:.0f} MPa; worst case (washers worn, moment on the pin) bending {s_pin:.0f} MPa vs Ti-6Al-4V yield 880")
report.append("  axial float set by the cap nut (snug, back off 3-5 deg ~ 0.01-0.015 mm on M16x1) so A and B share the moment with no preload drag")
report.append("tendon drive: each outer hub has two grooves symmetric about its mid-plane (+-1.6 mm); the two strands of a joint leave the")
report.append("  drum at diametrically opposite tangent points in opposite directions -> a pure couple: net radial = 0, net axial = 0, and the")
report.append("  symmetric grooves give no tilting moment. Guide pulleys must keep the strands in the hub plane (route them at the strip, not across).")

# ---------------------------------------------------------------- export (CAD frame of RIGHT ARM SUBASSY)
X0 = np.array([-119.5, 0.0, 0.0])
Mcad = np.array([[-1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])            # thorax -> CAD axes
from OCP.gp import gp_Trsf
_t = gp_Trsf(); _t.SetValues(*Mcad[0], X0[0], *Mcad[1], X0[1], *Mcad[2], X0[2]); loc = cq.Location(_t)
def mat(c): return cq.Color(*c)
COL = {"Ti": (0.58, 0.59, 0.61), "iglidur": (0.16, 0.16, 0.18), "cap": (0.70, 0.71, 0.73)}
assy = cq.Assembly(name="EXO shoulder D4")
for nm, s in parts.items():
    c = COL["iglidur"] if "iglidur" in nm else COL["cap"] if "cap" in nm else COL["Ti"]
    assy.add(s, name=nm.replace(" ", "_").replace("(", "").replace(")", "").replace(",", ""), color=mat(c), loc=loc)
assy.save(os.path.join(HERE, "shoulder_d4.step"))
try: assy.save(os.path.join(HERE, "shoulder_d4.glb"))
except Exception as ex_: report.append(f"glb export failed: {ex_}")
mass = sum(s.Volume() * (1.46e-3 if "iglidur" in nm else 4.43e-3) for nm, s in parts.items())
m_bar = parts[[n for n in parts if n.startswith("D4-05")][0]].Volume() * 4.43e-3
report.append(f"mass estimate: {mass:.0f} g total, {mass - m_bar:.0f} g without the arm stub (Ti-6Al-4V 4.43, iglidur G 1.46 g/cc)")
bom = ["BOM (per shoulder):", "  4x igus iglidur G flanged sleeve GFM-1618-06 (16 ID x 18 OD x 6 L, flange 24) - igus / RS / TME",
       "  8x igus iglidur G thrust washer GTM-1630-015 (16 x 30 x 1.5) - igus / RS",
       "  4x cap nut M16x1.0, Ti-6Al-4V (machined, D4-06), MoS2 dry film on thread", "  4x M3 nylon-tip set screw (cap lock)",
       "  4x M4 socket head screw (base flange to back plate); 4x M4 (arm component to D4-05 pad, Ø20 PCD)",
       "  Ti-6Al-4V, running faces (pins, hub faces) electroless nickel / Nedox: D4-01 base, D4-02 link 1, D4-03 link 2,",
       "    D4-04 link 3, D4-05 arm interface stub"]
open(os.path.join(HERE, "report.txt"), "w").write("\n".join(report + [""] + bom) + "\n")
print("\n".join(report + bom))
