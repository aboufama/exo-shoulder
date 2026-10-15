"""v5 joint: O20 hub, a preloaded pair of MR117-2RS ball bearings, zero play, hidden fastening, sensor space.

User 2026-10-15: "We can go to 20mm hubs"; MVP1 = unpowered kinematic proof of concept on basic rolling bearings; the
current joint "has loose bearings". Matches the band evaluator's r20 geometry: hub_r 10, stack 3.15, hub_up 7.1,
cap_up 2.0 (12.25 mm from the lower plate's skin face to the cap crown).

Along the joint axis from the lower member's skin face F (mm):
  F .. S        lower plate 3.0 (S = seat). Integral O7 Ti pin with a O8.2 collar rising from the seat: the collar's top
                face (L1) is the inner-ring shoulder; DIN 509-style relief at the shoulder corner
  S .. U0       0.15 running gap (set by the bearing stack, no thrust washer)
  U0 .. U1      upper hub 7.1 (boss of the upper member): 0.5 lip (O9.8 bore) under the lower outer ring,
                bearing 1 (3.0), outer spacer 0.6 (O11 x O9.8, 17-4PH), bearing 2 (3.0); bore O11 H6
                inner rings on the pin (k5) with an inner spacer 0.6 - delta (ground to set the preload) between them,
                clamped onto the collar by a Ti ring nut M7x0.5 (O8.6 x 0.9, Loctite 222, 2 pin-spanner holes)
                -> both stacks clamped: a preloaded back-to-back pair, no axial or radial play
  H1 = U1-1.5   top of the boss proper; a O18 threaded spigot (M18x0.5) rises from it to U1
  U1 .. top     cap: one turned Ti part, O20 skirt over the spigot (its wall continues the boss wall, one hairline),
                G2 dome crown 2.0 above U1, NO screws: it threads onto the spigot and its flange clamps the upper outer
                ring (outer stack: lip -> ring -> spacer -> ring -> cap). Tightened with a soft-jaw cup, Loctite 222
  sensing space (placeholders, the user designs the sensing): O4x2 diametric magnet in the pin top, a O4.6 pocket
                above it for the sensor IC (QFN 3x3x0.75, 0.3 air gap), O9 x 0.4 PCB bonded under the cap ceiling
All parts are revolves about the axis through GH (z = distance from GH along the axis).

    python3 joint_v5.py   -> out_joint_v5/joint_v5.glb, joint_v5_cut.glb (half section), levels.json, section.png
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "shoulder-d4")); sys.path.insert(0, os.path.join(HERE, ".."))
import g2cad as G
import cad_helpers as CH

HUB_R = 10.0                                                                # O20 hub (user 2026-10-15)
T_LO, GAP, HUB_UP, CAP_UP = 3.0, 0.15, 7.1, 2.0                             # = the evaluator's t_lo, stack - t_lo, hub_up, cap_up (r20)
LIP_T, LIP_RI = 0.5, 4.9                                                    # hub lip under the lower outer ring (O9.8 bore: outer-ring face only)
BRG = dict(d=7.0, D=11.0, B=3.0, d1=8.3, D1=9.7, ch=0.15, seal_t=0.3, seal_rec=0.1, seal_gap=0.05)   # MR117-2RS (7 x 11 x 3), ring lands d1 / D1
SPC_T = 0.6                                                                 # outer / inner spacer (inner = SPC_T - preload offset, ~5 um: not modelled)
COLLAR_R = 4.1                                                              # pin collar O8.2: inner-ring shoulder (inside the d1 land)
SKIRT_H, SPIG_R = 1.5, 9.0                                                  # cap skirt depth over the boss, threaded spigot (M18x0.5)
NUT_T, NUT_RO, NUT_RI = 0.9, 4.3, 3.25                                      # M7x0.5 ring nut (bore = thread minor), O8.6
POCKET_R, CAP_T = 4.6, 0.5                                                  # cap pocket (nut + PCB), dome thickness at the crown
PCB_T, PCB_R, IC_T, IC_A, AIR = 0.4, 4.5, 0.75, 3.0, 0.3
MAG_R, MAG_H = 2.0, 2.0
FLOAT = 0.05                                                                # cap skirt over the boss shoulder (the flange clamps at U1)

def levels(F=0.0, t_lo=T_LO):
    S = F + t_lo; U0 = S + GAP; L1 = U0 + LIP_T; B1 = L1 + BRG["B"]; B2 = B1 + SPC_T; U1 = B2 + BRG["B"]
    H1 = U1 - SKIRT_H; N1 = U1 + NUT_T; top = U1 + CAP_UP; P1 = top - CAP_T; P0 = P1 - PCB_T; IC0 = P0 - IC_T; M1 = IC0 - AIR; M0 = M1 - MAG_H
    assert abs(U1 - U0 - HUB_UP) < 1e-9 and N1 < P0 - 0.15
    return dict(F=F, S=S, U0=U0, L1=L1, B1=B1, B2=B2, U1=U1, H1=H1, N1=N1, R1=N1, P0=P0, P1=P1, IC0=IC0, M0=M0, M1=M1, top=top,
                pin_top=N1, rec=S, B0=U1, z0=U1)

def rev(pts, axis=(0, 0, 1.0), ref=None): return G.revolve_profile([("line", a, b) for a, b in zip(pts, pts[1:] + pts[:1])], np.asarray(axis, float), ref=ref)

# ---------------------------------------------------------------- lower member: integral pin
def pin(axis, lv):
    """collar O8.2 from 1.2 inside the plate to L1 (inner-ring shoulder), relief, O7 k5 seat + M7x0.5 stub to the top"""
    S, L1, R1 = lv["S"], lv["L1"], lv["R1"]; r = BRG["d"] / 2
    return rev([(0, S - 1.2), (COLLAR_R, S - 1.2), (COLLAR_R, L1), (r - 0.2, L1), (r - 0.2, L1 + 0.2), (r, L1 + 0.4), (r, R1 - 0.15), (r - 0.15, R1), (0, R1)], axis)
def pin_cuts(axis, lv):
    """magnet pocket (O4.05) and above it the sensor-IC pocket (O4.6), open at the pin top"""
    return [rev([(0, lv["M0"] - 0.05), (MAG_R + 0.025, lv["M0"] - 0.05), (MAG_R + 0.025, lv["M1"]), (2.3, lv["M1"]), (2.3, lv["R1"] + 1.0), (0, lv["R1"] + 1.0)], axis)]

# ---------------------------------------------------------------- upper member: boss bore + spigot
def spigot(axis, lv):
    """threaded spigot (M18x0.5, modelled at its major diameter), 0.5 embedded in the boss below H1"""
    H1, U1 = lv["H1"], lv["U1"]
    return rev([(5.0, H1 - 0.5), (SPIG_R, H1 - 0.5), (SPIG_R, U1 - 0.2), (SPIG_R - 0.2, U1), (5.0, U1)], axis)
def bore_tool(axis, lv):
    """lip O9.8 (entry chamfer from the skin side), bearing bore O11 with a relief at the lip corner, entry chamfer on top"""
    U0, L1, U1 = lv["U0"], lv["L1"], lv["U1"]; R = BRG["D"] / 2
    return rev([(0, U0 - 1.0), (LIP_RI + 1.2, U0 - 1.0), (LIP_RI, U0 + 0.2), (LIP_RI, L1), (R + 0.1, L1), (R + 0.1, L1 + 0.15), (R, L1 + 0.25),
                (R, U1 - 0.2), (R + 0.2, U1), (R + 1.2, U1 + 1.0), (0, U1 + 1.0)], axis)

# ---------------------------------------------------------------- bought parts: MR117-2RS (rings + seals), spacers, nut
def inner_ring(axis, z):
    b = BRG; r0, r1, c = b["d"] / 2, b["d1"] / 2, b["ch"]
    return rev([(r0 + c, z), (r1, z), (r1, z + b["B"]), (r0 + c, z + b["B"]), (r0, z + b["B"] - c), (r0, z + c)], axis)
def outer_ring(axis, z):
    b = BRG; r0, r1, c = b["D1"] / 2, b["D"] / 2, b["ch"]
    return rev([(r0, z), (r1 - c, z), (r1, z + c), (r1, z + b["B"] - c), (r1 - c, z + b["B"]), (r0, z + b["B"])], axis)
def seals(axis, z):
    b = BRG; ri, ro = b["d1"] / 2 + b["seal_gap"], b["D1"] / 2 + 0.05
    return [rev([(ri, z0), (ro, z0), (ro, z0 + b["seal_t"]), (ri, z0 + b["seal_t"])], axis) for z0 in (z + b["seal_rec"], z + b["B"] - b["seal_rec"] - b["seal_t"])]
def outer_spacer(axis, lv): return rev([(LIP_RI, lv["B1"]), (BRG["D"] / 2 - 0.02, lv["B1"]), (BRG["D"] / 2 - 0.02, lv["B2"]), (LIP_RI, lv["B2"])], axis)
def inner_spacer(axis, lv): return rev([(BRG["d"] / 2, lv["B1"]), (COLLAR_R, lv["B1"]), (COLLAR_R, lv["B2"]), (BRG["d"] / 2, lv["B2"])], axis)
def ring_nut(axis, lv):
    """M7x0.5 (thread modelled at its minor bore), face on the inner ring only (relieved past O8.2), 2 pin-spanner holes"""
    U1, N1 = lv["U1"], lv["N1"]
    r = rev([(NUT_RI, U1), (COLLAR_R, U1), (NUT_RO, U1 + 0.2), (NUT_RO, N1 - 0.1), (NUT_RO - 0.1, N1), (NUT_RI + 0.1, N1), (NUT_RI, N1 - 0.1)], axis)
    a = np.asarray(axis, float); n_, x_, y_ = CH.frame_of(a)
    for s in (1, -1): r = r.cut(cq.Solid.makeCylinder(0.4, 1.0, cq.Vector(*(s * 3.8 * x_ + a * (N1 - 0.5))), cq.Vector(*a)))
    return r
def magnet(axis, lv): return rev([(0, lv["M0"]), (MAG_R, lv["M0"]), (MAG_R, lv["M1"]), (0, lv["M1"])], axis)
def pcb(axis, lv): return rev([(0, lv["P0"]), (PCB_R, lv["P0"]), (PCB_R, lv["P1"]), (0, lv["P1"])], axis)
def ic(axis, lv):
    a = np.asarray(axis, float); n_, x_, y_ = CH.frame_of(a)
    return cq.Workplane(cq.Plane(origin=cq.Vector(*(a * (lv["IC0"] + IC_T / 2))), xDir=cq.Vector(*x_), normal=cq.Vector(*a))).box(IC_A, IC_A, IC_T).val()

DOME_A0, DOME_A1, DOME_ZW = 1.1, 5.0, 0.45                                     # quintic arms at the wall / crown, wall height above U1
def dome_profile(lv):
    """outer profile of the cap above its O20 wall: quintic Bezier from the wall (vertical, zero curvature: G2 with the
    cylinder) to the crown (horizontal, zero curvature: G2 across the axis); arms sized so it never rises above the crown"""
    U1, top = lv["U1"], lv["top"]; zw = U1 + DOME_ZW; P0, P1 = np.array([HUB_R, zw]), np.array([0.0, top])
    T0, T1 = np.array([0.0, 1.0]), np.array([-1.0, 0.0])
    return [P0, P0 + 0.5 * DOME_A0 * T0, P0 + DOME_A0 * T0, P1 - DOME_A1 * T1, P1 - 0.5 * DOME_A1 * T1, P1], zw
def cap(axis, lv):
    """one turned Ti part: skirt over the spigot (internal M18x0.5 at its major diameter), flange on the upper outer ring
    and the spigot top at U1, pocket for nut + PCB, G2 dome. No screws, no drive features."""
    U1, H1, P1, top = lv["U1"], lv["H1"], lv["P1"], lv["top"]; cp, zw = dome_profile(lv); zs = H1 + FLOAT
    segs = [("line", (0.0, P1), (POCKET_R - 0.2, P1)), ("line", (POCKET_R - 0.2, P1), (POCKET_R, P1 - 0.2)), ("line", (POCKET_R, P1 - 0.2), (POCKET_R, U1)),
            ("line", (POCKET_R, U1), (SPIG_R - 0.2, U1)), ("line", (SPIG_R - 0.2, U1), (SPIG_R, U1 - 0.2)), ("line", (SPIG_R, U1 - 0.2), (SPIG_R, zs + 0.15)),
            ("line", (SPIG_R, zs + 0.15), (SPIG_R + 0.15, zs)), ("line", (SPIG_R + 0.15, zs), (HUB_R - 0.1, zs)), ("line", (HUB_R - 0.1, zs), (HUB_R, zs + 0.1)),
            ("line", (HUB_R, zs + 0.1), (HUB_R, zw)), ("bez", [tuple(p) for p in cp]), ("line", (0.0, top), (0.0, P1))]
    return G.revolve_profile(segs, np.asarray(axis, float))

def dome_check(lv):
    """min cap wall over the pocket (dome surface - pocket ceiling) and the crown height"""
    cp, zw = dome_profile(lv); cp = np.asarray(cp); u = np.linspace(0, 1, 400)[:, None]
    pts = sum(math.comb(5, i) * (1 - u) ** (5 - i) * u ** i * cp[i] for i in range(6)); m = pts[:, 0] <= POCKET_R
    return float((pts[m, 1] - lv["P1"]).min())

# ---------------------------------------------------------------- the joint's parts, grouped by the member they turn with
def joint_parts(axis, lv, J):
    """lower group (turns with the pin): inner rings, inner spacer, ring nut, magnet; upper group (turns with the hub):
    outer rings + seals, outer spacer, cap, PCB, sensor IC. Names starting 'J<n>-' are custom parts (exported as STEP)."""
    a = np.asarray(axis, float); z1, z2 = lv["L1"], lv["B2"]
    lower = [(f"J{J} MR117-2RS bearing 1 inner ring", inner_ring(a, z1)), (f"J{J} MR117-2RS bearing 2 inner ring", inner_ring(a, z2)),
             (f"J{J}-spacerI inner spacer O8.2xO7x0.6 ground to preload (17-4PH)", inner_spacer(a, lv)),
             (f"J{J}-nut ring nut M7x0.5 O8.6x0.9 (Ti-6Al-4V)", ring_nut(a, lv)), (f"J{J} magnet O4x2 N52 diametric (NdFeB)", magnet(a, lv))]
    upper = [(f"J{J} MR117-2RS bearing 1 outer ring", outer_ring(a, z1)), (f"J{J} MR117-2RS bearing 2 outer ring", outer_ring(a, z2))]
    for k, z in ((1, z1), (2, z2)):
        for i, s in enumerate(seals(a, z)): upper.append((f"J{J} MR117-2RS bearing {k} seal {'ab'[i]} (2RS)", s))
    upper += [(f"J{J}-spacerO outer spacer O11xO9.8x0.6 (17-4PH)", outer_spacer(a, lv)),
              (f"J{J}-cap O20 G2 dome, threaded M18x0.5, no screws (Ti-6Al-4V)", cap(a, lv)),
              (f"J{J} position PCB O9x0.4 (FR-4, placeholder)", pcb(a, lv)), (f"J{J} angle sensor IC QFN 3x3 (placeholder)", ic(a, lv))]
    return lower, upper

def lower_features(body, axis, lv):
    """lower member at a joint: fuse the integral pin (collar crosses the seat transversally), cut the sensor pockets"""
    a = np.asarray(axis, float); p = pin(a, lv); b = None
    for tol in (0.0, 0.02, 0.1):
        b = CH.fuzzy_fuse(body, p, tol=tol)
        if b.isValid() and len(b.Solids()) == 1: break
    for tool in pin_cuts(a, lv): b = b.cut(tool)
    return b
def upper_features(body, axis, lv):
    """upper member at a joint: fuse the threaded spigot (embedded 0.5 below the boss top H1), cut the bearing bore"""
    a = np.asarray(axis, float); b = None
    for tol in (0.0, 0.02, 0.1):
        b = CH.fuzzy_fuse(body, spigot(a, lv), tol=tol)
        if b.isValid() and len(b.Solids()) == 1: break
    return b.cut(bore_tool(a, lv))

# ---------------------------------------------------------------- stand-alone demo: two plates + the stack
def demo_member(lv, role, d, axis=(0, 0, 1.0)):
    """a turned hub + flat 8 x 3 strap stub (for the demo / section only; the design builds use members.Strap)"""
    a = np.asarray(axis, float); d = np.asarray(d, float); d = d - (d @ a) * a; d /= np.linalg.norm(d); l = np.cross(a, d)
    z0, z1 = (lv["F"], lv["S"]) if role == "lower" else (lv["U0"], lv["H1"])
    def sdf2(x, y):
        d1 = np.hypot(x, y) - HUB_R; d2 = np.maximum(np.abs(y) - 4.0, np.maximum(x - 34.0, -x)); k = 4.0; h = np.maximum(k - np.abs(d1 - d2), 0) / k
        return np.minimum(d1, d2) - h ** 3 * k / 6
    b = G.flat_plate(sdf2, [0, 0, 0], d, l, z0, z1, 0.4, (-HUB_R - 3, 40, -HUB_R - 3, HUB_R + 3))
    return lower_features(b, a, lv) if role == "lower" else upper_features(b, a, lv)

def build(axis=(0, 0, 1.0), F=0.0, dir_lo=(1.0, 0, 0), dir_up=(math.cos(2.2), math.sin(2.2), 0)):
    a = np.asarray(axis, float); lv = levels(F); lo, up = joint_parts(a, lv, 1)
    parts = [("lower", "lower member: 3.0 plate + integral O7 pin (Ti-6Al-4V)", demo_member(lv, "lower", dir_lo, a)),
             ("upper", "upper member: O20 boss 7.1 + spigot, O11 bore (Ti-6Al-4V)", demo_member(lv, "upper", dir_up, a))]
    return parts + [("lower", n, s) for n, s in lo] + [("upper", n, s) for n, s in up], lv

def section_png(parts, lv, path):
    """half section in the plane y = 0 (x >= 0), one colour per part"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig, ax = plt.subplots(figsize=(7.5, 6.5), dpi=160)
    col = lambda n: "#e8833a" if "PCB" in n or "IC" in n else ("#8a8f99" if "MR117" in n else ("#b9bcc2" if "member" in n else ("#c9a227" if "magnet" in n else "#d4d6da")))
    import trimesh
    for g, n, s in parts:
        vs, tr = s.tessellate(0.005, 0.05); m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=True)
        sec = m.section(plane_origin=[0, 0, 0], plane_normal=[0, 1.0, 0])
        if sec is None: continue
        for ent in sec.discrete:                                                     # closed loops in the x-z plane
            P = np.asarray(ent)[:, [0, 2]]
            if P[:, 0].max() <= 0.01: continue
            ax.add_patch(Polygon(P, closed=True, fc=col(n), ec="#2b2d31", lw=0.4))
    for k in ("F", "S", "U0", "L1", "B1", "B2", "U1", "H1", "N1", "P0", "P1", "top"):
        ax.axhline(lv[k], color="#9aa", lw=0.3, ls=":"); ax.text(16.2, lv[k], f"{k} {lv[k] - lv['F']:.2f}", fontsize=6, va="center")
    ax.set_xlim(0, 19); ax.set_ylim(lv["F"] - 1, lv["top"] + 1); ax.set_aspect("equal"); ax.set_xlabel("r (mm)"); ax.set_ylabel("z from F (mm)")
    ax.set_title("joint v5: O20 hub, 2x MR117-2RS preloaded, threaded G2 cap (half section)", fontsize=9)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)

if __name__ == "__main__":
    import trimesh
    OUT = os.path.join(HERE, "out_joint_v5"); os.makedirs(OUT, exist_ok=True)
    parts, lv = build(); print("dome wall over the pocket min", round(dome_check(lv), 3), "mm")
    def mesh_of(s):
        vs, tr = s.tessellate(0.01, 0.1); return trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False)
    sc, sc2 = trimesh.Scene(), trimesh.Scene(); cutbox = cq.Solid.makeBox(80, 40, 60, cq.Vector(-40, 0, -20))
    for k, (g, nm, s) in enumerate(parts):
        print(f"{nm[:66]:66s} valid {s.isValid()} solids {len(s.Solids())} faces {len(s.Faces())} vol {s.Volume():.1f}", flush=True)
        sc.add_geometry(mesh_of(s), node_name=f"{g}|{nm}|{k}", geom_name=f"{g}|{nm}|{k}")
        h = s.cut(cutbox)
        if len(h.Solids()): sc2.add_geometry(mesh_of(h), node_name=f"{g}|{nm}|{k}", geom_name=f"{g}|{nm}|{k}")
    sc.export(os.path.join(OUT, "joint_v5.glb")); sc2.export(os.path.join(OUT, "joint_v5_cut.glb"))
    json.dump({k: round(v, 3) for k, v in lv.items()}, open(os.path.join(OUT, "levels.json"), "w"), indent=1)
    section_png(parts, lv, os.path.join(OUT, "section.png"))
    print("levels", {k: round(v - lv["F"], 2) for k, v in lv.items()}, "height above F", round(lv["top"] - lv["F"], 2))
