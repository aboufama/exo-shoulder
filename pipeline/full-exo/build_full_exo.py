"""Whole right-arm exo on the average body (1.75 m, 325 mm upper arm).

  shoulder: D4 v3 (output/shoulder-d4/build_shoulder_d4.py, run with STUB=0 into ./shoulder) - J4's inner member is BOTTOM
  user's arm (RIGHT ARM SUBASSY.step), unchanged: TOP, MIDDLE, FOREARM CUFF, elbow hardware and screws
  BOTTOM (the one modified part): the user's channel bar, cut where its section is uniform, then a lofted neck (the
    channel fades out, 15 deg twist) into a flat G2 hub plate = J4's inner member (seat, Ø10 pin, DIN 509 relief, M4)
  upper-arm cuff: the user's forearm cuff, scaled x1.24 to the upper arm, re-drilled on BOTTOM's cuff pattern (built by
    build_upper_cuff.py) + 6 of the user's countersunk M4 screws
Frames: body REST pose (thorax mm, origin right GH) for the arm groups; canonical pose-0 thorax frame for the shoulder.

    python3 build_full_exo.py      -> full_exo.step, exo.glb (viewer), bottom_mod.step, report_full.txt
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "shoulder-d4")); sys.path.insert(0, HERE)
import g2cad as G
import fit_arm as FA
from load_arm import load
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCP.TopTools import TopTools_ListOfShape
from OCP.gp import gp_Trsf

DD = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
SH = os.path.join(DD, "shoulder"); DP = json.load(open(os.path.join(SH, "display_pose.json"))); ST = DP["stack"]
BJ = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); HR = np.array(BJ["landmarks"]["rest_humerus"])
FIT = json.load(open(os.path.join(HERE, "arm_fit.json"))); R_UP, R_FO = np.array(FIT["R_up"]), np.array(FIT["R_fo"])
Fr = json.load(open(os.path.join(HERE, "bottom_frame.json")))
u_c, v_c, ax_c = (np.array(Fr[k]) for k in ("u", "v", "ax"))
u, v, ax = R_UP @ u_c, R_UP @ v_c, R_UP @ ax_c; C = np.array(FA.C_b)                    # BOTTOM's frame on the body
W = HR @ np.array(DP["pins"]["u4"]); W /= np.linalg.norm(W)                              # J4 axis, rest frame
def unit(x): return np.asarray(x, float) / np.linalg.norm(x)
def V(p): return cq.Vector(*map(float, p))

def xform(shape, R, t):
    tr = gp_Trsf(); tr.SetValues(*R[0], t[0], *R[1], t[1], *R[2], t[2])
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())
def cad_to_rest(shape, grp):
    R = R_UP if grp == "up" else R_FO; Cc = np.array(FA.C_cad); return xform(shape, R, C - R @ Cc)

# ---------------------------------------------------------------- BOTTOM (modified)
parts_user = load()
B_cad = [p[2] for p in parts_user if p[0] == "BOTTOM"][0]
B = cad_to_rest(B_cad, "up")
hc = W * ST["R_I0"]                                                       # J4 axis point on the hub's skin-side plane
# choose the cut: the bar point whose in-plane distance from the J4 axis is ~NECK + hub radius, below the hub plane
def at(s): return C + s * u
def inplane(p): d = p - hc; return d - (d @ W) * W
S_CUT = None
for s in np.arange(150, 330, 1.0):
    if np.linalg.norm(inplane(at(s))) < ST["HUB_R"] + 40.0: S_CUT = float(s); break
S_CUT = min(S_CUT, 270.0)                                                 # stays in the uniform-section region (165-270)
half = cq.Solid.makeBox(600, 600, 600, pnt=V(at(S_CUT) - 300 * v - 300 * ax), dir=V(u)) if False else None
# lower bar: keep s <= S_CUT
big = cq.Workplane(cq.Plane(origin=tuple(at(S_CUT)), xDir=tuple(v), normal=tuple(-u))).rect(800, 800).extrude(800).val()
bar = B.intersect(big)
# outer outline of the bar's cut face (U: the channel opens toward the arm)
sec = cq.Shape.cast(BRepAlgoAPI_Section(bar.wrapped, cq.Face.makePlane(400, 400, basePnt=V(at(S_CUT)), dir=V(u)).wrapped).Shape())
def ordered_loop(edges, n=240):
    pts = np.concatenate([np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 40)]) for e in edges])
    # order by angle about the section centroid (outline is star-shaped about its centre)
    c = pts.mean(0); a = np.arctan2((pts - c) @ ax, (pts - c) @ v); pts = pts[np.argsort(a)]
    seg = np.linalg.norm(np.diff(np.r_[pts, pts[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(t, sl, np.r_[pts[:, k], pts[0, k]]) for k in range(3)]).T
def chain_loop(edges, n=240, ref_u=None, ref_v=None):
    """walk the section edges end to end into one closed polyline, resampled to n points (counter-clockwise about ref_u x ref_v)"""
    segs = [np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 30)]) for e in edges]
    loop = segs.pop(0)
    while segs:
        end = loop[-1]; d = [(min(np.linalg.norm(s[0] - end), np.linalg.norm(s[-1] - end)), k) for k, s in enumerate(segs)]
        _, k = min(d); s = segs.pop(k)
        if np.linalg.norm(s[-1] - end) < np.linalg.norm(s[0] - end): s = s[::-1]
        loop = np.r_[loop, s[1:]]
    if np.linalg.norm(loop[-1] - loop[0]) < 1e-3: loop = loop[:-1]
    c = loop.mean(0); x2 = (loop - c) @ ref_u; y2 = (loop - c) @ ref_v
    if 0.5 * np.sum(x2 * np.roll(y2, -1) - np.roll(x2, -1) * y2) < 0: loop = loop[::-1]
    seg = np.linalg.norm(np.diff(np.r_[loop, loop[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(t, sl, np.r_[loop[:, k], loop[0, k]]) for k in range(3)]).T
bar_loop = chain_loop(sec.Edges(), ref_u=v, ref_v=ax)
# hub plate: flat G2 plate, planform = hub disc + strip toward the bar (smooth union), skin-side plane at R_I0, top = seat
d_hat = unit(inplane(at(S_CUT))); e2 = np.cross(W, d_hat)
HUB_R, HW, K = ST["HUB_R"], 15.0, 8.0
RHO_J = HUB_R + 10.0                                                      # where the plate's strip meets the neck
def sdf2(x, y):
    d1 = np.hypot(x, y) - HUB_R; d2 = np.maximum(np.abs(y) - HW, np.maximum(x - (RHO_J + 12), -x))
    h = np.maximum(K - np.abs(d1 - d2), 0) / K; return np.minimum(d1, d2) - h ** 3 * K / 6
plate = G.flat_plate(sdf2, [0, 0, 0], d_hat, e2, ST["R_I0"], ST["SEAT_I"], 1.2, (-HUB_R - 4, RHO_J + 16, -HUB_R - 4, HUB_R + 4))
cutp = cq.Workplane(cq.Plane(origin=tuple(hc + RHO_J * d_hat), xDir=tuple(e2), normal=tuple(d_hat))).rect(400, 400).extrude(200).val()
plate = plate.cut(cutp)
psec = cq.Shape.cast(BRepAlgoAPI_Section(plate.wrapped, cq.Face.makePlane(400, 400, basePnt=V(hc + RHO_J * d_hat), dir=V(d_hat)).wrapped).Shape())
def ordered_loop2(edges, n=240, c_axes=(e2, W)):
    pts = np.concatenate([np.array([e.positionAt(t).toTuple() for t in np.linspace(0, 1, 40)]) for e in edges])
    c = pts.mean(0); a = np.arctan2((pts - c) @ c_axes[1], (pts - c) @ c_axes[0]); pts = pts[np.argsort(a)]
    seg = np.linalg.norm(np.diff(np.r_[pts, pts[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    t = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(t, sl, np.r_[pts[:, k], pts[0, k]]) for k in range(3)]).T
# the bar's width axis v must map onto the plate's width axis e2 with the same sense (no flip through the neck)
sgn = 1.0 if (v @ e2) >= 0 else -1.0
plate_loop = chain_loop(psec.Edges(), ref_u=sgn * e2, ref_v=(W if (ax @ W) >= 0 else -W))
# neck: sections along a cubic Bezier from the bar end to the plate's strip end, morphing outline + frame
P0 = bar_loop.mean(0); P3 = plate_loop.mean(0); L_ = np.linalg.norm(P3 - P0)
P1 = P0 + 0.4 * L_ * u; P2 = P3 + 0.4 * L_ * d_hat
def bez(t): return (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3
def q_from(R):
    from scipy.spatial.transform import Rotation as Rot
    return Rot.from_matrix(R)
from scipy.spatial.transform import Rotation as Rot, Slerp
F0 = np.c_[v, ax, u]; F1 = np.c_[sgn * e2, W if (ax @ W) >= 0 else -W, -d_hat]
F0 = np.c_[F0[:, 0], F0[:, 1], np.cross(F0[:, 0], F0[:, 1])]; F1 = np.c_[F1[:, 0], F1[:, 1], np.cross(F1[:, 0], F1[:, 1])]
sl = Slerp([0, 1], Rot.from_matrix([F0, F1]))
loc0 = (bar_loop - P0) @ F0; loc1 = (plate_loop - P3) @ F1                       # local 2D (+0 normal) outlines
# align the start index: the point nearest +width
i0 = int(np.argmax(loc0[:, 0])); i1 = int(np.argmax(loc1[:, 0])); loc0 = np.roll(loc0, -i0, 0); loc1 = np.roll(loc1, -i1, 0)
ts = np.r_[0.0, 0.03, np.linspace(0.12, 0.88, 6), 0.97, 1.0]
ths = BRepOffsetAPI_ThruSections(True, False, 1e-6); ths.CheckCompatibility(False)
for t in ts:
    w = 0.5 - 0.5 * math.cos(math.pi * t)                                       # ease the shape morph
    loc = (1 - w) * loc0 + w * loc1; loc[:, 2] = 0.0
    Rt = sl([t]).as_matrix()[0]; pts = bez(t) + loc @ Rt.T
    ths.AddWire(G.wire([BRepBuilderAPI_MakeEdge(G._periodic_curve(pts, G._shift())).Edge()]))
ths.Build(); neck = cq.Shape.cast(ths.Shape())
print("neck valid", neck.isValid(), "plate valid", plate.isValid(), "bar valid", bar.isValid(), "S_CUT", S_CUT)
def fuzzy_fuse(a, b, tol=0.1):
    args = TopTools_ListOfShape(); args.Append(a.wrapped); tools = TopTools_ListOfShape(); tools.Append(b.wrapped)
    f = BRepAlgoAPI_Fuse(); f.SetArguments(args); f.SetTools(tools); f.SetFuzzyValue(tol); f.Build()
    return cq.Shape.cast(f.Shape())
bottom = fuzzy_fuse(fuzzy_fuse(bar, neck), plate)
# J4 features: pin (Ø10, chamfer, M4 tap), DIN 509 relief at the root
n_ = W; zb, zt = ST["SEAT_I"] - 1.2, ST["CAP_Z0"]
pin = G.revolve_profile([("line", (0, zb), (5, zb)), ("line", (5, zb), (5, zt - 0.4)), ("line", (5, zt - 0.4), (4.6, zt)),
                         ("line", (4.6, zt), (0, zt)), ("line", (0, zt), (0, zb))], W)
pin = pin.cut(cq.Solid.makeCylinder(1.65, 8, V(W * (zt - 7)), V(W))).cut(cq.Solid.makeCone(1.65, 1.96, 0.31, V(W * (zt - 0.3)), V(W)))
bottom = fuzzy_fuse(bottom, pin).cut(cq.Solid.makeTorus(5.0, 0.4, V(W * ST["SEAT_I"]), V(W)))
bottom = cq.Shape.cast(bottom.wrapped)
print("BOTTOM (modified) valid", bottom.isValid(), "solids", len(bottom.Solids()))
cq.exporters.export(cq.Workplane().add(bottom), os.path.join(DD, "bottom_mod.step"))

# ---------------------------------------------------------------- parts list (name, group, solid in its frame)
EXO = []                                                                    # (group, name, shape)
user_screw_cs = [p for p in parts_user if p[0].startswith("Hex socket head countersunk")]
for name, inst, s in parts_user:
    if s.Volume() < 1 or name.startswith(("SHOULDER LINK", '0.245" ID')) or name in ("RETAINING CLAMP", "BOTTOM") \
       or name.startswith("DRY RUNNING") or name.startswith("M4 ULTRA LOW PROFILE SOCKET HEAD SCREW, 8mm"): continue   # old scissor shoulder
    grp = "F" if name in ("MIDDLE", "FOREARM CUFF") or name.startswith("Hex socket head countersunk") else "H"
    EXO.append((grp, name, cad_to_rest(s, "up" if grp == "H" else "fore")))
EXO.append(("H", "BOTTOM (modified for the average arm + D4 J4 hub)", bottom))
cuff = cq.importers.importStep(os.path.join(HERE, "upper_cuff_cad.step")).val()
EXO.append(("H", "UPPER ARM CUFF (forearm cuff design, x1.24)", cad_to_rest(cuff, "up")))
# the user's countersunk screw, moved from its forearm-cuff hole to each upper-cuff hole (same seat, same depth)
MID_c = [p[2] for p in parts_user if p[0] == "MIDDLE"][0]
E = json.load(open(os.path.join(HERE, "..", "arm-rom", "arm_rom.json")))["elbow"]
scr = user_screw_cs[0][2]; sc_c = np.array(scr.Center().toTuple())
# its hole on MIDDLE: nearest of the forearm-cuff holes; reference = where the hole axis meets MIDDLE's skin-side face
vm, _ = MID_c.tessellate(0.2); Pm = np.array([[q.x, q.y, q.z] for q in vm]); zface = (Pm @ ax_c).min()
off_axis = sc_c @ ax_c - zface                                              # screw centre above MIDDLE's skin face
zface_B = (C @ ax) - 2.8 if False else None
for s_ in (94.25, 124.25, 154.25):
    for y_ in (-8.75, 8.75):
        hole_B = C + s_ * u + y_ * v + (-2.8) * ax                         # on BOTTOM's skin-side face (rest frame)
        # rotation: the user's screw axis (ax_c) -> BOTTOM's ax; position its centre off_axis from the face
        Rm = R_UP; t = hole_B + off_axis * ax - Rm @ sc_c
        EXO.append(("H", "Hex socket head countersunk screw M4x0.7x8 (upper cuff)", xform(scr, Rm, t)))
# shoulder (D4) parts: CAD frame -> canonical thorax (pose 0); J4 hardware moves with the humerus -> rest frame
X0 = np.array([-119.5, 0.0, 0.0]); Mcad = np.array([[-1.0, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])
for name, inst, s in load(os.path.join(SH, "shoulder_d4.step")):
    nm = name.replace("_", " ")
    s_th = xform(s, Mcad.T, -Mcad.T @ X0)                                   # CAD -> thorax (pose 0 = scapula frame at rest)
    key = nm.split(" ")[0]
    grp = {"D4-01": "base", "D4-02": "l1", "D4-03": "l2", "D4-04": "l3", "J1": "l1", "J2": "l2", "J3": "l2", "J4": "H"}.get(key, "l2")
    if grp == "H": s_th = xform(s_th, HR, np.zeros(3))                      # canonical -> rest (H seg at pose 0 = HR^T)
    EXO.append((grp, nm, s_th))
print(len(EXO), "parts")

# ---------------------------------------------------------------- checks at the rest pose
rep = [f"BOTTOM: cut at s = {S_CUT:.0f} mm from the elbow axis (user's bar + cuff group 94-154 kept), neck + J4 hub plate; valid {bottom.isValid()}"]
KD = FA.KD
def skin_min(shape, step=1.0):
    vs, _ = shape.tessellate(step); P = np.array([[q.x, q.y, q.z] for q in vs]); return FA.skin_dist(P).min() if len(P) else 99
for nm in ("BOTTOM (modified", "UPPER ARM CUFF"):
    s = [p[2] for p in EXO if p[1].startswith(nm)][0]; rep.append(f"{nm.strip('(')}: closest skin {skin_min(s):.1f} mm (rest pose)")
# ---------------------------------------------------------------- exports
assy = cq.Assembly(name="EXO right arm, average adult")
for k, (g, nm, s) in enumerate(EXO): assy.add(s, name=(f"{k:02d}_{g}|{nm}".replace(" ", "_").replace("(", "").replace(")", "").replace(",", ""))[:120])
assy.save(os.path.join(DD, "full_exo.step"))
sc = trimesh.Scene()
for k, (g, nm, s) in enumerate(EXO):
    tol = 0.08 if ("CUFF" in nm or "BOTTOM" in nm or g in ("base", "l1", "l2", "l3")) else 0.15
    vs, tr = s.tessellate(tol, 0.15); P = np.array([[q.x, q.y, q.z] for q in vs])
    if not len(tr): continue
    m = trimesh.Trimesh(P, tr, process=False); _ = m.vertex_normals
    sc.add_geometry(m, node_name=f"{g}|{nm}|{k}", geom_name=f"{g}|{nm}|{k}")
sc.export(os.path.join(DD, "exo.glb"))
open(os.path.join(DD, "report_full.txt"), "w").write("\n".join(rep) + "\n"); print("\n".join(rep))
