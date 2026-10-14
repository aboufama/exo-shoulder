"""v4 encoder joint (smallest stack that carries an on-axis angle sensor), as a stand-alone demo assembly + section data.

From the lower member's skin face F, along the joint axis:
  lower plate 3.0 (FEA: 420 MPa at 25 N.m)  | washer A igus GTM-1018-005 (10x18x0.5) in a 0.35 recess, 0.15 proud
  upper hub 4.05 with igus GSM-1012-04       | washer B GTM-1018-005 on the upper hub, 0.02 float (set by the pin length)
  pin Ø10 h9 steps to an M8x0.5 stub (1.0 long): a Ti ring nut 18 x 1.0 threads on and clamps the shoulder (sets the 0.02
  float; Loctite 222, 2 spanner holes) -> clamps washer B. No screws in the stack.
  magnet Ø4x2 N52 diametric in a pocket in the stub (the Ti pin is its non-magnetic carrier); above it a Ø4.6 pocket
  the sensor IC (QFN 3x3x0.75, MT6701-class) drops into, 0.4 over the magnet
  PCB Ø16 x 0.6 bonded under the cap ceiling, IC underneath; flex tail out through a slot in the cap rim into a 0.35 groove
  in the upper member
  Ø22 Ti G2 dome cap sits on the upper hub (it turns with it, so the sensor sees the pin turn), 2x M1.6 flush
Height above F: 10.47 mm on a Ø23 hub (v3: 13.07 on Ø26, v3.2: 10.32 without the sensor).

    python3 joint_v4.py   -> out_joint_v4/joint_v4.glb, section.json, section.png
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "shoulder-d4")); sys.path.insert(0, os.path.join(HERE, ".."))
import g2cad as G
import cad_helpers as CH
HUB_R, HW = 11.5, 7.0
T_LO, REC, PROUD, T_UP, FLOAT, T_WASH = 3.0, 0.35, 0.15, 4.05, 0.02, 0.5
RET_T, RET_RO, RET_RI = 1.0, 9.0, 2.6
PCB_GAP, PCB_T, PCB_R, IC_T, IC_A = 0.15, 0.6, 8.0, 0.75, 3.0
MAG_R, MAG_H = 2.0, 2.0
CAP_R, CAP_IN, CROWN = 11.0, 9.3, 1.0

def levels(F=0.0):
    S = F + T_LO; U0 = S + PROUD; U1 = U0 + T_UP; B0 = U1 + FLOAT; z0 = B0 + T_WASH
    R1 = z0 + RET_T; P0 = R1 + PCB_GAP; P1 = P0 + PCB_T; top = P1 + CROWN; IC0 = P0 - IC_T
    return dict(F=F, S=S, rec=S - REC, U0=U0, U1=U1, B0=B0, z0=z0, R1=R1, P0=P0, P1=P1, IC0=IC0, M1=IC0 - 0.4, M0=IC0 - 0.4 - MAG_H, top=top)

def rev(pts, axis=(0, 0, 1.0)): return G.revolve_profile([("line", a, b) for a, b in zip(pts, pts[1:] + pts[:1])], np.asarray(axis, float))
def ring_pts(axis, r, n, phase=0.0):
    a = np.asarray(axis, float); n_, x_, y_ = CH.frame_of(a); return [r * (math.cos(phase + 2 * math.pi * k / n) * x_ + math.sin(phase + 2 * math.pi * k / n) * y_) for k in range(n)], n_

def pin(axis, lv):
    z0, zr, R1 = lv["z0"], lv["rec"], lv["R1"]; r = 5.0
    return rev([(0, zr - 1.5), (r + 0.5, zr - 1.5), (r + 0.5, zr), (r - 0.25, zr + 0.05), (r - 0.25, zr + 0.45), (r, zr + 0.75), (r, z0), (4.0, z0),
                (4.0, R1 - 0.2), (3.8, R1), (0, R1)], axis)
def pin_cuts(axis, lv):
    """magnet pocket (Ø4.05) and above it the sensor pocket (Ø4.6) down the pin's stub"""
    M0, M1, R1 = lv["M0"], lv["M1"], lv["R1"]
    return [rev([(0, M0 - 0.05), (MAG_R + 0.03, M0 - 0.05), (MAG_R + 0.03, M1), (2.3, M1), (2.3, R1 + 1), (0, R1 + 1)], axis)]
def washer(axis, z): e = 0.1; return rev([(5.0, z), (8.9, z), (9.0, z + e), (9.0, z + T_WASH - e), (8.9, z + T_WASH), (5.0, z + T_WASH)], axis)
def sleeve(axis, z): return rev([(5.0, z), (5.7, z), (6.0, z + 0.3), (6.0, z + 3.7), (5.7, z + 4.0), (5.0, z + 4.0)], axis)
def retainer(axis, lv):
    """M8x0.5 ring nut (thread modelled as its minor bore), clamps the pin shoulder; 2 spanner holes Ø1.0"""
    z0 = lv["z0"]; e = 0.15; ri = 3.95
    r = rev([(ri, z0), (RET_RO - e, z0), (RET_RO, z0 + e), (RET_RO, z0 + RET_T - e), (RET_RO - e, z0 + RET_T), (ri + e, z0 + RET_T), (ri, z0 + RET_T - e)], axis)
    P, n_ = ring_pts(axis, 6.8, 2, 0.0)
    for p in P: r = r.cut(cq.Solid.makeCylinder(0.5, 0.6, cq.Vector(*(p + n_ * (z0 + RET_T - 0.5))), cq.Vector(*n_)))
    return r
def m16_cs(axis, p, z_top, L=4.0):
    """M1.6 ISO 10642 countersunk (head Ø3.0, 90 deg), top flush at z_top along axis, at offset p"""
    a = np.asarray(axis, float); s = G.revolve_profile([("line", (0, 0), (1.5, 0)), ("line", (1.5, 0), (0.8, -0.7)), ("line", (0.8, -0.7), (0.8, -L + 0.2)), ("line", (0.8, -L + 0.2), (0.6, -L)),
                                                        ("line", (0.6, -L), (0, -L)), ("line", (0, -L), (0, 0))], a)
    n_, x_, y_ = CH.frame_of(a); hexw = cq.Workplane(cq.Plane(origin=cq.Vector(*(-0.55 * n_)), xDir=cq.Vector(*x_), normal=cq.Vector(*n_))).polygon(6, 0.9 / math.cos(math.pi / 6)).extrude(0.6).val()
    return s.cut(hexw).moved(cq.Location(cq.Vector(*(p + a * z_top))))
def magnet(axis, lv): return rev([(0, lv["M0"]), (MAG_R, lv["M0"]), (MAG_R, lv["M1"]), (0, lv["M1"])], axis)
def pcb(axis, lv, tail_dir):
    a = np.asarray(axis, float); P0 = lv["P0"]
    disc = cq.Solid.makeCylinder(PCB_R, PCB_T, cq.Vector(*(a * P0)), cq.Vector(*a))
    t = np.asarray(tail_dir, float); t = t - (t @ a) * a; t /= np.linalg.norm(t); l = np.cross(a, t)
    tail = cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (lv["U1"] - 0.3 + 0.05) + t * (PCB_R + 6.0))), xDir=cq.Vector(*t), normal=cq.Vector(*a))).box(14.0, 4.0, 0.12).val()
    riser = cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (0.5 * (lv["U1"] - 0.25 + P0)) + t * (PCB_R - 0.6))), xDir=cq.Vector(*t), normal=cq.Vector(*a))).box(0.12, 4.0, P0 - lv["U1"] + 0.25).val()
    return disc, tail.fuse(riser)
def ic(axis, lv):
    a = np.asarray(axis, float); n_, x_, y_ = CH.frame_of(a)
    return cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (lv["IC0"] + IC_T / 2))), xDir=cq.Vector(*x_), normal=cq.Vector(*a))).box(IC_A, IC_A, IC_T).val()
def cap(axis, lv, tail_dir):
    U1, P1, top = lv["U1"], lv["P1"], lv["top"]; up, inn, down = (0, 1.0), (-1.0, 0), (0, -1.0)
    segs = [("line", (CAP_IN, U1), (CAP_R - 0.15, U1)), ("line", (CAP_R - 0.15, U1), (CAP_R, U1 + 0.15)), ("line", (CAP_R, U1 + 0.15), (CAP_R, U1 + 0.45)),
            ("bez", G.g2_blend((CAP_R, U1 + 0.45), up, 0.0, inn, (0.0, top), inn, 0.04, down, frac=0.45)),
            ("line", (0.0, top), (0.0, P1)), ("line", (0.0, P1), (CAP_IN - 0.4, P1)), ("line", (CAP_IN - 0.4, P1), (CAP_IN, P1 - 0.4)), ("line", (CAP_IN, P1 - 0.4), (CAP_IN, U1))]
    c = G.revolve_profile(segs, np.asarray(axis, float)); a = np.asarray(axis, float)
    t = np.asarray(tail_dir, float); t = t - (t @ a) * a; t /= np.linalg.norm(t); l = np.cross(a, t)
    slot = cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (U1 + 0.2) + t * (CAP_IN + 1.0))), xDir=cq.Vector(*t), normal=cq.Vector(*a))).box(6.0, 4.6, 0.4).val()
    c = c.cut(slot)
    for s_ in (1, -1):                                                                        # 2x M1.6 countersinks in the rim
        p = l * s_ * 10.15; c = c.cut(G.revolve_profile([("line", (0, -1), (0.85, -1)), ("line", (0.85, -1), (0.85, 0.45 - 0.7)), ("line", (0.85, 0.45 - 0.7), (1.55, 0.46)),
                                                        ("line", (1.55, 0.46), (1.55, 3)), ("line", (1.55, 3), (0, 3)), ("line", (0, 3), (0, -1))], a).moved(cq.Location(cq.Vector(*(p + a * U1)))))
    return c

def cap_noslot(axis, lv):
    """the cap without the flex slot, screw countersinks on the frame's y axis (placeholder for the design builds)"""
    U1, P1, top = lv["U1"], lv["P1"], lv["top"]; up, inn, down = (0, 1.0), (-1.0, 0), (0, -1.0); a = np.asarray(axis, float)
    segs = [("line", (CAP_IN, U1), (CAP_R - 0.15, U1)), ("line", (CAP_R - 0.15, U1), (CAP_R, U1 + 0.15)), ("line", (CAP_R, U1 + 0.15), (CAP_R, U1 + 0.45)),
            ("bez", G.g2_blend((CAP_R, U1 + 0.45), up, 0.0, inn, (0.0, top), inn, 0.04, down, frac=0.45)),
            ("line", (0.0, top), (0.0, P1)), ("line", (0.0, P1), (CAP_IN - 0.4, P1)), ("line", (CAP_IN - 0.4, P1), (CAP_IN, P1 - 0.4)), ("line", (CAP_IN, P1 - 0.4), (CAP_IN, U1))]
    c = G.revolve_profile(segs, a); n_, x_, y_ = CH.frame_of(a)
    for s_ in (1, -1):
        p = y_ * s_ * 10.15; c = c.cut(G.revolve_profile([("line", (0, -1), (0.85, -1)), ("line", (0.85, -1), (0.85, 0.45 - 0.7)), ("line", (0.85, 0.45 - 0.7), (1.55, 0.46)),
                                                        ("line", (1.55, 0.46), (1.55, 3)), ("line", (1.55, 3), (0, 3)), ("line", (0, 3), (0, -1))], a).moved(cq.Location(cq.Vector(*(p + a * U1)))))
    return c

def build(axis=(0, 0, 1.0), F=0.0, dir_lo=(1.0, 0, 0), dir_up=(math.cos(2.2), math.sin(2.2), 0)):
    a = np.asarray(axis, float); lv = levels(F); parts = []
    def plate(z0, z1, d):
        d = np.asarray(d, float); d = d - (d @ a) * a; d /= np.linalg.norm(d); l = np.cross(a, d)
        def sdf2(x, y):
            d1 = np.hypot(x, y) - HUB_R; d2 = np.maximum(np.abs(y) - HW, np.maximum(x - 34.0, -x)); k = 6.0; h = np.maximum(k - np.abs(d1 - d2), 0) / k
            return np.minimum(d1, d2) - h ** 3 * k / 6
        return G.flat_plate(sdf2, [0, 0, 0], d, l, z0, z1, 1.0, (-HUB_R - 3, 40, -HUB_R - 3, HUB_R + 3))
    lo = plate(lv["F"], lv["S"], dir_lo)
    lo = lo.cut(rev([(0, lv["rec"]), (9.15, lv["rec"]), (9.15, lv["S"] - 0.1), (9.25, lv["S"]), (12.0, lv["S"] + 3), (0, lv["S"] + 3)], a))
    lo = CH.fuzzy_fuse(lo, pin(a, lv), tol=0.0)
    for tool in pin_cuts(a, lv): lo = lo.cut(tool)
    up = plate(lv["U0"], lv["U1"], dir_up)
    up = up.cut(CH.bore_tool(a, lv["U0"], lv["U1"], 6.0))
    t = np.asarray(dir_up, float); t = t - (t @ a) * a; t /= np.linalg.norm(t); l = np.cross(a, t)
    groove = cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (lv["U1"] - 0.175) + t * (9.0 + 10.0))), xDir=cq.Vector(*t), normal=cq.Vector(*a))).box(20.0, 4.6, 0.36).val()
    up = up.cut(groove)
    for s_ in (1, -1): up = up.cut(cq.Solid.makeCylinder(0.625, 3.0, cq.Vector(*(l * s_ * 10.15 + a * (lv["U1"] - 3.0))), cq.Vector(*a)))
    parts += [("lower", "lower member: 3.0 plate, integral Ø10 h9 pin with magnet pocket (Ti-6Al-4V)", lo), ("upper", "upper member: 4.05 hub, Ø12 H7 bore, flex groove (Ti-6Al-4V)", up)]
    pd, tail = pcb(a, lv, dir_up)
    parts += [("lower", "washer A (igus GTM-1018-005, recessed)", washer(a, lv["rec"])), ("upper", "sleeve (igus GSM-1012-04)", sleeve(a, lv["U0"])),
              ("lower", "washer B (igus GTM-1018-005)", washer(a, lv["B0"])), ("lower", "magnet Ø4x2 N52 diametric", magnet(a, lv)),
              ("lower", "ring nut M8x0.5, 18 x 1.0 (Ti-6Al-4V)", retainer(a, lv)),
              ("upper", "position PCB Ø16x0.6", pd), ("upper", "flex tail (polyimide)", tail), ("upper", "angle sensor IC (QFN 3x3, MT6701-class)", ic(a, lv)),
              ("upper", "cap: Ø22 G2 dome (Ti-6Al-4V)", cap(a, lv, dir_up))]
    for s_ in (1, -1): parts.append(("upper", f"M1.6x3 ISO 10642 Ti-6Al-4V, non-magnetic (cap) {'AB'[s_ < 0]}", m16_cs(a, l * s_ * 10.15, lv["U1"] + 0.46, 3.0)))
    return parts, lv

if __name__ == "__main__":
    import trimesh
    OUT = os.path.join(HERE, "out_joint_v4"); os.makedirs(OUT, exist_ok=True)
    parts, lv = build()
    sc = trimesh.Scene()
    for k, (g, nm, s) in enumerate(parts):
        print(f"{nm[:60]:60s} valid {s.isValid()}", flush=True)
        vs, tr = s.tessellate(0.02, 0.15); m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False)
        sc.add_geometry(m, node_name=f"{g}|{nm}|{k}", geom_name=f"{g}|{nm}|{k}")
    sc.export(os.path.join(OUT, "joint_v4.glb")); json.dump({k: round(v, 3) for k, v in lv.items()}, open(os.path.join(OUT, "levels.json"), "w"), indent=1)
    print("levels", {k: round(v, 2) for k, v in lv.items()}, "height above F", round(lv["top"] - lv["F"], 2))
