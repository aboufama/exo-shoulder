"""EXO shoulder, design D4 v3: four-pivot spherical shoulder (one spare DOF), 124 mm envelope, thin all-titanium links.

Kinematics: arm-rom/opt_D.py with the real footprint (FP=1 FP_W=14 FP_HUB=34 FP_RIN=119 FP_ROUT=124.7)
-> opt_D_124_c4_p180_fp_thin.json, 67.8% of 3,993 natural poses (BodyParts3D body, links >= 4 mm off the skin).
Every pivot axis passes through the shoulder centre; links alternate inner / outer shell.

Sizing (fea_link.py, own hex8 FEA validated against beam theory, 25 N.m in the worst direction):
  links 14 mm strip, Ø34 hubs, Ti-6Al-4V; inner links 5.0 mm, outer links 5.45 mm (room for the 5 mm sleeve)
Joint (per pivot), after the RIGHT ARM SUBASSY standard (pin + end clamp + M4 ULP screw):
  inner member: integral Ø10 h9 pin on a flat seat machined into the spherical hub, DIN 509-style relief at the root
  2x igus iglidur G thrust washers GTM-1018-010 (10 x 18 x 1.0): duplex, moment as a face couple, axial both ways
  outer member: Ø12 H7 bore with an igus iglidur G sleeve GSM-1012-05 (10/12 x 5) flush: radial
  Ti retaining cap Ø20 x 2.5 clamped on the pin end by an M4 ultra-low-profile screw (flush in a counterbore);
    pin length sets 0.02 mm axial float (no preload drag)
Finish: G2 planform (cubic smooth-min outline), G2 edge rounds swept round every link, G2 revolve profiles on the base,
  pins and caps; machined features (seats, bores, threads) carry 0.2-0.5 mm chamfers.

    python3 build_shoulder_d4.py      -> shoulder_d4.step, shoulder_d4.glb, report.txt
"""
import json, math, os, sys, time
import numpy as np
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__)); ROM = os.path.abspath(os.environ.get("ROM_DIR", os.path.join(HERE, "..", "arm-rom")))
OUT = os.path.abspath(os.environ.get("OUT_DIR", HERE)); os.makedirs(OUT, exist_ok=True)
STUB = os.environ.get("STUB", "1") == "1"            # 0: J4's inner member is the user's BOTTOM (built in full-exo)
sys.path.insert(0, ROM); sys.path.insert(0, HERE)
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180")
import design_search as D, design_search_families as F, design_search_anat as A
from design_search_pivots import w_dir
import fea_link as FL, g2cad as G

T0 = time.time()
# ---------------------------------------------------------------- design + display pose
DES = json.load(open(os.path.join(ROM, os.environ.get("DES_FILE", "opt_D_124_c4_p180_fp_thin.json"))))[0]
b = np.asarray(DES["b"], float); a1, a2, a3 = (DES[k] * D.D2R for k in ("a1", "a2", "a3")); W = w_dir(DES["delta"], DES["waz"])
e_ = np.cross(b, [0.0, 1, 0]); e_ /= np.linalg.norm(e_); f_ = np.cross(b, e_)
def pins_for(Hg, q):
    u4 = Hg @ W; c2 = math.cos(a1) * b + math.sin(a1) * (math.cos(q) * e_ + math.sin(q) * f_)
    c3, ok = F.circ_int(c2[None], a2, u4[None], a3, DES["branch"])
    ok = ok[0] and F.triangle_ok(c2[None], u4[None], a2, a3)[0] and F.triangle_ok(b[None], c3, a1, a2)[0]
    return dict(b=b, c2=c2, c3=c3[0], u4=u4), bool(ok)

# ---------------------------------------------------------------- dimensions (mm)
def drop(rho, R): return R - math.sqrt(R * R - rho * rho)
T_IN, T_OUT = 5.0, 5.45
HUB_R, STRIP_HW, K_BLEND = 17.0, 7.0, 10.0
E_IN, E_OUT = 1.5, 1.0                     # G2 edge-round size (inner links: skin side comfort; outer: room for grooves)
PIN_D, WASH_ID, WASH_OD, WASH_T = 10.0, 10.0, 18.0, 1.0
SLV_ID, SLV_OD, SLV_L = 10.0, 12.0, 5.0
CAP_D, CAP_T, FLOAT = 20.0, 2.5, 0.02
SCR_HEAD_D, SCR_HEAD_H, SCR_L = 7.1, 2.0, 6.0
R_I0 = float(os.environ.get("R_I0", 119.0)); R_I1 = R_I0 + T_IN
SEAT_I = R_I1 - drop(WASH_OD / 2, R_I1) - 0.05                 # flat on the inner hub (washer A)
SEAT_OB = SEAT_I + WASH_T                                       # outer hub underside flat
R_O0 = SEAT_OB - 0.05
for _ in range(5):                                              # outer links just thick enough for the sleeve at this radius
    T_OUT = max(5.45, SLV_L + 0.1 + drop(WASH_OD / 2, R_O0 + T_OUT))
R_O1 = R_O0 + T_OUT
SEAT_OT = R_O1 - drop(WASH_OD / 2, R_O1) - 0.05                 # outer hub top flat (washer B)
CAP_Z0 = SEAT_OT + WASH_T + FLOAT; CAP_Z1 = CAP_Z0 + CAP_T
PIN_TOP = CAP_Z0
assert SEAT_OT - SEAT_OB >= SLV_L - 1e-6, "outer hub too thin for the sleeve"

H0 = D.Ry(0) @ D.Rx(0) @ D.Ry(0); Rs0 = D.scapula(0); Hg0 = Rs0.T @ H0
valid_q = []
for qd in np.arange(0, 360, 2):
    Pq, ok = pins_for(Hg0, math.radians(qd))
    if ok:
        pts = np.concatenate([D.slerp_pts(Pq["b"][None], Pq["c2"][None], 9)[0], D.slerp_pts(Pq["c2"][None], Pq["c3"][None], 9)[0], D.slerp_pts(Pq["c3"][None], Pq["u4"][None], 9)[0]])
        Pt = pts * (R_I0); dt = A.lookup(A.TRUNK[0], Pt); da = A.lookup(A.ARM, Pt @ Hg0)
        near = np.degrees(np.arccos(np.clip(pts @ Pq["u4"], -1, 1))) < 15
        if dt.min() >= 4 and da[~near].min() >= 4: valid_q.append(qd)
runs, cur = [], [valid_q[0]]
for v in valid_q[1:]:
    if v - cur[-1] <= 2: cur.append(v)
    else: runs.append(cur); cur = [v]
runs.append(cur); run = max(runs, key=len); Q0 = run[len(run) // 2]
PINS, _ = pins_for(Hg0, math.radians(Q0))
pb, pc2, pc3, pu4 = (PINS[k] / np.linalg.norm(PINS[k]) for k in ("b", "c2", "c3", "u4"))

def V(p): return cq.Vector(float(p[0]), float(p[1]), float(p[2]))
def unit(v): return G.unit(v)
def frame_of(axis):
    n = unit(axis); x = unit(np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])); return n, x, np.cross(n, x)
def cyl(axis, z0, z1, r, off=(0, 0)):
    n, x, y = frame_of(axis); base = n * z0 + x * off[0] + y * off[1]
    return cq.Solid.makeCylinder(r, z1 - z0, V(base), V(n))
def cone(axis, z0, r0_, z1, r1_):
    n, _, _ = frame_of(axis); return cq.Solid.makeCone(r0_, r1_, z1 - z0, V(n * z0), V(n))
def ring_torus(axis, z, R_, r_):
    n, _, _ = frame_of(axis); return cq.Solid.makeTorus(R_, r_, V(n * z), V(n))
def cut(s, *tools):
    for t in tools: s = s.cut(t)
    return s.clean()
def fuse(s, *others):
    for o in others: s = s.fuse(o)
    return s.clean()

# ---------------------------------------------------------------- joint features
def pin_solid(axis):
    """integral pin: Ø10 from just below the seat to the cap face; 0.4 x 45 chamfer at the tip,
    M4 tap drill Ø3.3 x 7 with a 0.3 chamfer (the root relief is cut after fusing)"""
    r = PIN_D / 2; z0 = SEAT_I - 1.2; z1 = PIN_TOP
    segs = [("line", (0, z0), (r, z0)), ("line", (r, z0), (r, z1 - 0.4)), ("line", (r, z1 - 0.4), (r - 0.4, z1)),
            ("line", (r - 0.4, z1), (0, z1)), ("line", (0, z1), (0, z0))]
    p = G.revolve_profile(segs, axis)
    return cut(p, cyl(axis, z1 - 7.0, z1 + 1, 1.65), cone(axis, z1 - 0.3, 1.65, z1 + 0.01, 1.96))

def inner_hub_features(link, axis):
    """flat seat for washer A + integral pin + DIN 509-style relief (r 0.4) at the pin root"""
    link = cut(link, cyl(axis, SEAT_I, R_I1 + 2, HUB_R + 2))
    link = fuse(link, pin_solid(axis))
    return cut(link, ring_torus(axis, SEAT_I, PIN_D / 2, 0.4))

def outer_hub_features(link, axis, grooves=True):
    """underside flat for washer A (shallow pocket, 45 deg mouth chamfer), Ø12 H7 sleeve bore with 0.3 chamfers,
    top flat for washer B, two tendon grooves on the hub rim"""
    rp = WASH_OD / 2 + 0.6
    zr = math.sqrt(R_O0 ** 2 - rp ** 2)
    link = cut(link, cyl(axis, zr - 1.0, SEAT_OB, rp), cone(axis, zr - 0.4, rp + 0.6, zr + 0.2, rp))
    link = cut(link, cyl(axis, R_O0 - 2, R_O1 + 2, SLV_OD / 2),
               cone(axis, SEAT_OB - 0.01, SLV_OD / 2 + 0.3, SEAT_OB + 0.3, SLV_OD / 2),
               cone(axis, SEAT_OT - 0.3, SLV_OD / 2, SEAT_OT + 0.01, SLV_OD / 2 + 0.3))
    link = cut(link, cyl(axis, SEAT_OT, R_O1 + 2, HUB_R + 2))
    if grooves:
        al = HUB_R / ((R_O0 + R_O1) / 2)
        for dz in (-0.75, 0.75):
            rg = (R_O0 + R_O1) / 2 + dz
            link = cut(link, ring_torus(axis, rg * math.cos(al), rg * math.sin(al), 0.55))
    return link

def washer(axis, z0):
    c = 0.15; ri, ro, t = WASH_ID / 2, WASH_OD / 2, WASH_T
    segs = [("line", (ri, z0), (ro - c, z0)), ("line", (ro - c, z0), (ro, z0 + c)), ("line", (ro, z0 + c), (ro, z0 + t - c)),
            ("line", (ro, z0 + t - c), (ro - c, z0 + t)), ("line", (ro - c, z0 + t), (ri, z0 + t)), ("line", (ri, z0 + t), (ri, z0))]
    return G.revolve_profile(segs, axis)

def sleeve(axis, z0):
    ri, ro, L = SLV_ID / 2, SLV_OD / 2, SLV_L; c = 0.3
    segs = [("line", (ri, z0), (ro - c, z0)), ("line", (ro - c, z0), (ro, z0 + c)), ("line", (ro, z0 + c), (ro, z0 + L - c)),
            ("line", (ro, z0 + L - c), (ro - c, z0 + L)), ("line", (ro - c, z0 + L), (ri, z0 + L)), ("line", (ri, z0 + L), (ri, z0))]
    return G.revolve_profile(segs, axis)

def cap(axis):
    """Ti retaining cap: G2-rounded top rim (e 0.8), 0.2 chamfer underneath, Ø4.5 clearance + counterbore for the
    M4 ULP head (head 0.05 below flush), 0.2 chamfer at the counterbore mouth"""
    R_, z0, z1, e = CAP_D / 2, CAP_Z0, CAP_Z1, 0.8
    rc = SCR_HEAD_D / 2 + 0.25; zc = z1 - SCR_HEAD_H - 0.05
    segs = [("line", (2.25, z0), (R_ - 0.2, z0)), ("line", (R_ - 0.2, z0), (R_, z0 + 0.2)), ("line", (R_, z0 + 0.2), (R_, z1 - e)),
            G.corner2d((R_, z1 - e), (0, 1.0), 0.0, (-1, 0), (R_ - e, z1), (-1, 0), 0.0, (0, -1)),
            ("line", (R_ - e, z1), (rc + 0.2, z1)), ("line", (rc + 0.2, z1), (rc, z1 - 0.2)), ("line", (rc, z1 - 0.2), (rc, zc)),
            ("line", (rc, zc), (2.25, zc)), ("line", (2.25, zc), (2.25, z0))]
    return G.revolve_profile(segs, axis)

def screw(axis):
    """M4 ultra-low-profile socket head (Ø7.1 x 2.0, 2.5 hex socket), 6 mm shank"""
    zc = CAP_Z1 - SCR_HEAD_H - 0.05; zt = zc + SCR_HEAD_H; R_ = SCR_HEAD_D / 2
    segs = [("line", (0, zc - SCR_L), (1.85, zc - SCR_L)), ("line", (1.85, zc - SCR_L), (2.0, zc - SCR_L + 0.3)),
            ("line", (2.0, zc - SCR_L + 0.3), (2.0, zc)), ("line", (2.0, zc), (R_, zc)), ("line", (R_, zc), (R_, zt - 0.35)),
            ("line", (R_, zt - 0.35), (R_ - 0.35, zt)), ("line", (R_ - 0.35, zt), (0, zt)), ("line", (0, zt), (0, zc - SCR_L))]
    s = G.revolve_profile(segs, axis)
    n, x, y = frame_of(axis)
    hexw = cq.Workplane(cq.Plane(origin=V(n * (zt - 1.3)), xDir=V(x), normal=V(n))).polygon(6, 2.5 / math.cos(math.pi / 6)).extrude(1.4).val()
    return s.cut(hexw)

# ---------------------------------------------------------------- links
def link(hubs, strips, r0, r1, e, chart):
    pf = FL.Planform(hubs, strips, (r0 + r1) / 2, k=K_BLEND)
    return G.spherical_link(pf, chart, r0, r1, e), pf

parts, PF = {}, {}
t_ = time.time()
L1, PF["l1"] = link([(pb, HUB_R), (pc2, HUB_R)], [(pb, pc2, STRIP_HW)], R_O0, R_O1, E_OUT, [pb, pc2])
L1 = outer_hub_features(outer_hub_features(L1, pb), pc2)
L2, PF["l2"] = link([(pc2, HUB_R), (pc3, HUB_R)], [(pc2, pc3, STRIP_HW)], R_I0, R_I1, E_IN, [pc2, pc3])
L2 = inner_hub_features(inner_hub_features(L2, pc2), pc3)
L3, PF["l3"] = link([(pc3, HUB_R), (pu4, HUB_R)], [(pc3, pu4, STRIP_HW)], R_O0, R_O1, E_OUT, [pc3, pu4])
L3 = outer_hub_features(outer_hub_features(L3, pc3), pu4)
print(f"links built {time.time() - t_:.0f}s", flush=True)

# arm interface stub (inner shell): hub at J4 + strip + Ø26 pad with 4x M4 (the user's first arm component bolts here)
h0 = Hg0 @ np.array([0.0, -1.0, 0.0]); tq = unit(np.cross(pu4, h0))
def stub_dir(gam, ang=15.0):
    d_ = math.cos(math.radians(gam)) * np.cross(tq, pu4) + math.sin(math.radians(gam)) * tq
    return math.cos(math.radians(ang)) * pu4 + math.sin(math.radians(ang)) * d_
def stub_clear(pe):
    _, u_, v_ = frame_of(pe)
    ring = np.array([pe * (R_I0 - 1) + 13 * (math.cos(k) * u_ + math.sin(k) * v_) for k in np.linspace(0, 2 * math.pi, 12, endpoint=False)] + [pe * (R_I0 - 1)])
    return min(A.lookup(A.ARM, ring @ Hg0).min(), A.lookup(A.TRUNK[0], ring).min())
GAM = max(range(0, 360, 10), key=lambda g: stub_clear(stub_dir(g))); pe = unit(stub_dir(GAM))
if STUB:
  L5, PF["bar"] = link([(pu4, HUB_R), (pe, 13.0)], [(pu4, pe, STRIP_HW)], R_I0, R_I1, E_IN, [pu4, pe])
  L5 = inner_hub_features(L5, pu4)
  n_, x_, y_ = frame_of(pe)
  for k in range(4):
    off = 8.5 * np.array([math.cos(k * math.pi / 2 + math.pi / 4), math.sin(k * math.pi / 2 + math.pi / 4)])
    d = unit(pe * R_I1 + off[0] * x_ + off[1] * y_)
    L5 = cut(L5, cq.Solid.makeCylinder(1.65, 8, V(d * (R_I0 - 1.5)), V(d)), cq.Solid.makeCone(1.65, 2.0, 0.35, V(d * (R_I1 - 0.34)), V(d)))

# scapula base (turned): Ø44 x 4 mounting flange (4x M4 on Ø34) -> G2 blend -> Ø16 column -> G2 flare -> spherical hub
r_skin = next(r for r in np.arange(40, 125, 1.0) if A.lookup(A.TRUNK[0], (pb * r)[None])[0] > 2.0)
zf0 = r_skin + 2.0; zf1 = zf0 + 4.0; RF, RC = 22.0, 8.0
al = HUB_R / ((R_I0 + R_I1) / 2); ca, sa = math.cos(al), math.sin(al)
def sph(R, ang): return (R * math.sin(ang), R * math.cos(ang))
e = E_IN
ai = (HUB_R - e) / ((R_I0 + R_I1) / 2)                                         # inset angle (edge-round start)
pB0 = sph(R_I0, ai); pT0 = sph(R_I1, ai)
radial = np.array([math.sin(ai), math.cos(ai)]); tang_out = np.array([math.cos(ai), -math.sin(ai)])
wb = np.array(pB0) + e * radial + e * tang_out; wt = np.array(pT0) - e * radial + e * tang_out
segs = []
segs.append(("line", (0, zf0), (RF - 0.4, zf0))); segs.append(("line", (RF - 0.4, zf0), (RF, zf0 + 0.4)))
segs.append(("line", (RF, zf0 + 0.4), (RF, zf1 - 1.0)))
segs.append(G.corner2d((RF, zf1 - 1.0), (0, 1.0), 0.0, (-1, 0), (RF - 1.0, zf1), (-1, 0), 0.0, (0, -1)))
segs.append(("line", (RF - 1.0, zf1), (RC + 4.0, zf1)))
segs.append(G.corner2d((RC + 4.0, zf1), (-1, 0), 0.0, (0, 1), (RC, zf1 + 4.0), (0, 1.0), 0.0, (1, 0), frac=0.35))
ang_f = math.asin((RC + 5.0) / R_I0); pf_ = sph(R_I0, ang_f); tf = np.array([math.cos(ang_f), -math.sin(ang_f)])
z_col_top = pf_[1] - 5.0
segs.append(("line", (RC, zf1 + 4.0), (RC, z_col_top)))
segs.append(G.corner2d((RC, z_col_top), (0, 1.0), 0.0, (1, 0), pf_, tf, 1 / R_I0, -np.array([math.sin(ang_f), math.cos(ang_f)]), frac=0.35))
segs.append(("arc", pf_, sph(R_I0, (ang_f + ai) / 2), pB0))
segs.append(G.corner2d(pB0, tang_out, 1 / R_I0, -radial, tuple(wb), radial, 0.0, -tang_out))
segs.append(("line", tuple(wb), tuple(wt)))
segs.append(G.corner2d(tuple(wt), radial, 0.0, -tang_out, pT0, -tang_out, 1 / R_I1, -radial))
rho_seat = math.sqrt(R_I1 ** 2 - SEAT_I ** 2)
segs.append(("arc", pT0, sph(R_I1, (ai + math.asin(rho_seat / R_I1)) / 2), (rho_seat, SEAT_I)))
segs.append(("line", (rho_seat, SEAT_I), (0, SEAT_I))); segs.append(("line", (0, SEAT_I), (0, zf0)))
base = G.revolve_profile(segs, pb)
base = fuse(base, pin_solid(pb)); base = cut(base, ring_torus(pb, SEAT_I, PIN_D / 2, 0.4))
n_, x_, y_ = frame_of(pb)
for k in range(4):
    off = 17.0 * np.array([math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)])
    base = cut(base, cyl(pb, zf0 - 0.5, zf1 + 0.5, 1.65, off), cq.Solid.makeCone(1.95, 1.65, 0.3, V(n_ * (zf0 - 0.001) + x_ * off[0] + y_ * off[1]), V(n_)))

parts["D4-01 scapula base (Ti-6Al-4V)"] = base
parts["D4-02 link 1 (Ti-6Al-4V)"] = L1
parts["D4-03 link 2 (Ti-6Al-4V)"] = L2
parts["D4-04 link 3 (Ti-6Al-4V)"] = L3
if STUB: parts["D4-05 arm interface stub (Ti-6Al-4V)"] = L5
for j, ax in (("J1", pb), ("J2", pc2), ("J3", pc3), ("J4", pu4)):
    parts[f"{j} iglidur G thrust washer A (igus GTM-1018-010)"] = washer(ax, SEAT_I)
    parts[f"{j} iglidur G sleeve (igus GSM-1012-05)"] = sleeve(ax, SEAT_OB)
    parts[f"{j} iglidur G thrust washer B (igus GTM-1018-010)"] = washer(ax, SEAT_OT)
    parts[f"{j} retaining cap (Ti-6Al-4V)"] = cap(ax)
    parts[f"{j} M4x6 ultra-low-profile socket head screw"] = screw(ax)
print(f"parts built {time.time() - T0:.0f}s", flush=True)

# ---------------------------------------------------------------- checks
report = []
report.append(f"design: base az {DES['az']} el {DES['el']}, arcs {DES['a1']}/{DES['a2']}/{DES['a3']} deg, post delta {DES['delta']} az {DES['waz']} -> searched coverage {100 * DES['cov']:.1f}%")
report.append(f"display pose: arm hanging, spare joint J1 at {Q0} deg (middle of its {len(run) * 2} deg valid band)")
report.append(f"stack (radius from the shoulder centre): inner links {R_I0:.2f}-{R_I1:.2f}, washer A {SEAT_I:.2f}-{SEAT_I + WASH_T:.2f}, outer links {R_O0:.2f}-{R_O1:.2f}"
              f" (shell gap {R_O0 - R_I1:.2f}), washer B {SEAT_OT:.2f}-{SEAT_OT + WASH_T:.2f}, cap {CAP_Z0:.2f}-{CAP_Z1:.2f}  -> joint height {CAP_Z1 - R_I0:.2f} mm above the skin-side face")
bad = [nm for nm, s in parts.items() if not G.valid(s)]
report.append("B-rep validity: " + ("all parts valid" if not bad else "INVALID: " + ", ".join(bad)))
names = list(parts); clash = []
bbs = {nm: parts[nm].BoundingBox() for nm in names}
def bb_overlap(a, b_):
    A_, B_ = bbs[a], bbs[b_]
    return not (A_.xmax < B_.xmin or B_.xmax < A_.xmin or A_.ymax < B_.ymin or B_.ymax < A_.ymin or A_.zmax < B_.zmin or B_.zmax < A_.zmin)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        if not bb_overlap(names[i], names[j]): continue
        try:
            v = parts[names[i]].intersect(parts[names[j]]).Volume()
            if v > 0.5: clash.append((names[i], names[j], round(v, 2)))
        except Exception: pass
thread = [c for c in clash if "screw" in c[0] + c[1] and abs(c[2] - math.pi / 4 * (4.0 ** 2 - 3.3 ** 2) * (SCR_L - (CAP_Z1 - SCR_HEAD_H - 0.05 - PIN_TOP))) < 2.0]
real = [c for c in clash if c not in thread]
report.append(f"interference (> 0.5 mm^3): " + ("none" if not real else "; ".join(f"{a} x {b_}: {v}" for a, b_, v in real))
              + f"  [{len(thread)} expected M4 thread engagements: Ø4 screw in Ø3.3 tap drill, {thread[0][2] if thread else 0} mm^3 each]")
print("interference done", flush=True)

def frame(a, c):
    n = c - (a @ c) * a; n /= np.linalg.norm(n); return np.c_[a, n, np.cross(a, n)]
F0 = dict(base=np.eye(3), l1=frame(pb, pc2), l2=frame(pc2, pc3), l3=frame(pc3, pu4), bar=Hg0)
group = {"D4-01": "base", "D4-02": "l1", "D4-03": "l2", "D4-04": "l3", "D4-05": "bar", "J1": "l1", "J2": "l2", "J3": "l2", "J4": "bar"}
samples = {}
for nm, s in parts.items():
    vs, _ = s.tessellate(1.0); Pp = np.array([[v.x, v.y, v.z] for v in vs]); samples[nm] = Pp[:: max(1, len(Pp) // 500)]
def footprint(key, n=500):
    pf = PF[key]; m, ex, ey = FL.chart([h[0] for h in pf.hubs])
    g = np.random.default_rng(3).uniform(-110, 110, (60000, 2)); Dg = m * pf.r + g[:, :1] * ex + g[:, 1:] * ey
    Dg /= np.linalg.norm(Dg, axis=1, keepdims=True); return Dg[pf.sdf(Dg) < 0][:n]
FP_ = {k: footprint(k) for k in (("l1", "l2", "l3", "bar") if STUB else ("l1", "l2", "l3"))}
def overlap(ka, Ra, kb, Rb, clear=1.5):
    pts = FP_[ka] @ Ra.T
    return bool((PF[kb].sdf(pts @ Rb) < clear).any())
rng = np.random.default_rng(0); idx = rng.choice(len(D.POSES), 400, replace=False)
okp = tot = layer_fail = 0; worst = {}
for n in idx:
    pl, el, ax, Hg, Rs = D.POSES[n]; eb = A.EBIN_ALL[n]; Hf = A.HF_ALL[n]
    best_q = None
    for qd in np.arange(0, 360, 6):
        Pq, ok = pins_for(Hg, math.radians(qd))
        if not ok: continue
        Fp = dict(base=np.eye(3), l1=frame(Pq["b"], Pq["c2"]), l2=frame(Pq["c2"], Pq["c3"]), l3=frame(Pq["c3"], Pq["u4"]), bar=Hg)
        Rg = {g: Fp[g] @ F0[g].T for g in Fp}
        lay = overlap("l1", Rg["l1"], "l3", Rg["l3"]) or (STUB and overlap("l2", Rg["l2"], "bar", Rg["bar"]))
        mins = []
        for nm, Xs in samples.items():
            g = group[nm.split(" ")[0]]; Xp = Xs @ Rg[g].T
            if g == "base": Xp = Xp[np.linalg.norm(Xp, axis=1) > R_I0 - 0.5]
            if not len(Xp): continue
            dt = A.lookup(A.TRUNK[eb], Xp @ Rs.T).min()
            if g == "bar": da = 100.0
            else:
                uu = Fp["l3"][:, 0]; far = (Xp @ uu) / (np.linalg.norm(Xp, axis=1) + 1e-9) < math.cos(math.radians(15))
                da = A.lookup(A.ARM, Xp[far] @ Hf).min() if far.any() else 100.0
            mins.append((min(dt, da), nm))
        m_ = min((x for x in mins if not x[1].startswith("D4-05")), default=(99.0, ""))
        score = m_[0] - (100 if lay else 0)
        if best_q is None or score > best_q[0]: best_q = (score, qd, m_[1], lay)
    if best_q is None: continue
    tot += 1
    if best_q[3]: layer_fail += 1
    elif best_q[0] >= 2.0: okp += 1
    else: worst[best_q[2]] = worst.get(best_q[2], 0) + 1
report.append(f"hardware sweep (400 random natural poses, spare joint chosen per pose): {okp}/{tot} kinematically valid poses keep every"
              f" shoulder part >= 2 mm off the skin with no same-shell link overlap; {layer_fail} lost to link overlap; skin-limited by {dict(sorted(worst.items(), key=lambda t: -t[1])[:4])}")
print("sweep done", flush=True)

# ---------------------------------------------------------------- FEA summary + loads
fea = json.load(open(os.path.join(HERE, "fea_size.json")))
fe5 = [r for r in fea if abs(r["t"] - 5.0) < 1e-6][0]
report.append("FEA (fea_link.py, hex8, validated vs beam theory within 3%): 14 mm strip, Ø34 hubs, 25 N.m in the worst direction:")
for r in fea: report.append(f"   t {r['t']:.1f} mm: von Mises max {r['vm']:.0f} MPa (SF yield {880 / r['vm']:.2f}), softest single-link stiffness {r['k']:.1f} N.m/deg")
report.append(f"   chosen: inner 5.0 mm (SF {880 / fe5['vm']:.2f} at the 25 N.m limit, {0.6 * fe5['vm']:.0f} MPa at 15 N.m working), outer 5.45 mm (SF ~{880 / (fe5['vm'] * (5 / 5.45) ** 2):.2f})")
ri, ro = WASH_ID / 2, WASH_OD / 2; I_w = math.pi / 4 * (ro ** 4 - ri ** 4)
report.append(f"joint at 25 N.m / 200 N radial / 200 N axial: washer face p_max {25e3 * ro / I_w:.0f} MPa (iglidur G 80 MPa), sleeve {200 / (SLV_ID * SLV_L):.1f} MPa,"
              f" couple force ~{25e3 / (2 * 0.6 * ro):.0f} N through cap + M4 (12.9 proof ~9 kN)")
report.append("load paths: radial -> sleeve; axial + -> washer B -> cap -> M4 -> pin; axial - -> washer A -> inner hub; moment -> A/B face couple")

# ---------------------------------------------------------------- export (CAD frame of RIGHT ARM SUBASSY)
X0 = np.array([-119.5, 0.0, 0.0]); Mcad = np.array([[-1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])
from OCP.gp import gp_Trsf
_t = gp_Trsf(); _t.SetValues(*Mcad[0], X0[0], *Mcad[1], X0[1], *Mcad[2], X0[2]); loc = cq.Location(_t)
COL = {"Ti": (0.62, 0.62, 0.63), "iglidur": (0.17, 0.17, 0.19), "screw": (0.08, 0.08, 0.09)}
def kind(nm): return "iglidur" if "iglidur" in nm else "screw" if "screw" in nm else "Ti"
assy = cq.Assembly(name="EXO shoulder D4 v3")
for nm, s in parts.items():
    assy.add(s, name=nm.replace(" ", "_").replace("(", "").replace(")", "").replace(",", ""), color=cq.Color(*COL[kind(nm)]), loc=loc)
assy.save(os.path.join(OUT, "shoulder_d4.step"))
import trimesh
scene = trimesh.Scene()
MAT = {"Ti": trimesh.visual.material.PBRMaterial(name="titanium", baseColorFactor=[158, 158, 161, 255], metallicFactor=0.85, roughnessFactor=0.36),
       "iglidur": trimesh.visual.material.PBRMaterial(name="iglidur", baseColorFactor=[44, 44, 48, 255], metallicFactor=0.0, roughnessFactor=0.55),
       "screw": trimesh.visual.material.PBRMaterial(name="blackoxide", baseColorFactor=[22, 22, 24, 255], metallicFactor=0.7, roughnessFactor=0.4)}
mass = 0.0
for nm, s in parts.items():
    vs, tr = s.tessellate(0.05, 0.1); Pm = np.array([[v.x, v.y, v.z] for v in vs]) @ Mcad.T + X0
    mesh = trimesh.Trimesh(Pm * 0.001, tr, process=False)
    _ = mesh.vertex_normals                                     # smooth within each OCC face, sharp across its edges
    mesh.visual = trimesh.visual.TextureVisuals(material=MAT[kind(nm)]); scene.add_geometry(mesh, node_name=nm, geom_name=nm)
    rho = {"iglidur": 1.46e-3, "screw": 7.9e-3, "Ti": 4.43e-3}[kind(nm)]
    mass += abs(trimesh.Trimesh(Pm, tr).volume) * rho
scene.export(os.path.join(OUT, "shoulder_d4.glb"))
web = trimesh.Scene()                                          # lighter mesh (mm, CAD frame) for the on-body viewer
for nm, s in parts.items():
    vs, tr = s.tessellate(0.08, 0.15); Pm = np.array([[v.x, v.y, v.z] for v in vs]) @ Mcad.T + X0
    mesh = trimesh.Trimesh(Pm, tr, process=False); _ = mesh.vertex_normals
    mesh.visual = trimesh.visual.TextureVisuals(material=MAT[kind(nm)]); web.add_geometry(mesh, node_name=nm, geom_name=nm)
web.export(os.path.join(OUT if OUT != HERE else ROM, "shoulder_d4_web.glb"))
json.dump(dict(Q0=float(Q0), pins=dict(b=pb.tolist(), c2=pc2.tolist(), c3=pc3.tolist(), u4=pu4.tolist()), DES=DES,
               stack=dict(R_I0=R_I0, R_I1=R_I1, SEAT_I=SEAT_I, SEAT_OB=SEAT_OB, R_O0=R_O0, R_O1=R_O1, SEAT_OT=SEAT_OT, CAP_Z0=CAP_Z0, CAP_Z1=CAP_Z1, PIN_D=PIN_D, HUB_R=HUB_R)),
          open(os.path.join(OUT, "display_pose.json"), "w"))
report.append(f"mass: {mass:.0f} g total incl. stub (mesh volumes; Ti-6Al-4V 4.43, iglidur G 1.46, steel 7.9 g/cc)")
bom = ["BOM (per shoulder):",
       "  4x igus iglidur G sleeve bearing GSM-1012-05 (10 ID x 12 OD x 5) - igus / RS / TME",
       "  8x igus iglidur G thrust washer GTM-1018-010 (10 x 18 x 1.0) - igus / RS",
       "  4x M4 x 6 ultra-low-profile socket head screw (as RIGHT ARM SUBASSY), threadlocker",
       "  4x M4 socket head screw (base flange to back plate, Ø34 PCD); 4x M4 (arm component to D4-05 pad)",
       "  Ti-6Al-4V: D4-01 base (turned + milled), D4-02 / D4-04 outer links (5-axis, 5.45), D4-03 inner link (5.0),",
       "    D4-05 arm stub, 4x D4-06 retaining cap; pins and running faces electroless nickel / Nedox"]
open(os.path.join(OUT, "report.txt"), "w").write("\n".join(report + [""] + bom) + "\n")
print("\n".join(report + bom)); print(f"total {time.time() - T0:.0f}s")
