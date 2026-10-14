"""Arm side of a band design (imported by build_band_cad.py, stage 2).

BOTTOM: the user's bar, cut at s = S_CUT (as in the earlier conformal build), 2x M4 tapped at the cut end for a lap joint.
Non-cuff: JN hub block (Ti-6Al-4V, 5-axis): tongue in BOTTOM's channel (4x M3 countersunk through the web), neck to a Ø26 hub plate
  perpendicular to the JN axis, turned skin-side contour, integral Ø10 h9 pin, v3 stack on top.
Sliding cuff = curved guide (ring-segment arc joint):
  track   - turned ring segment (true surface of revolution about the humerus axis), 12 wide x 4 thick, 90 deg V-ridges both
            edges (through-hardened 17-4PH H900 or hard-anodised 7075, ground V), end stops at the travel limits
  carriage- Ti-6Al-4V plate over the track carrying 4 V-groove wheels (Ø12, 90 deg, MR84-2RS inside) on Ø4 studs set radially
            (2 concentric, 2 eccentric 0.4 mm for preload), JN pin + v3 stack on top
  neck    - integral with the track: a tongue in BOTTOM's channel (4x M3 countersunk through the bar's web), lofted to the track end
Frames: canonical humerus frame (pose 0 thorax frame of the arm, mm, GH origin); converted to the arm's rest frame for H.
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); FX = os.path.join(EXO, "full-exo")
sys.path.insert(0, FX)
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
_c = os.getcwd(); os.chdir(FX); import fit_arm as FA; os.chdir(_c)
from load_arm import load
FIT = json.load(open(os.path.join(FX, "arm_fit.json"))); R_UP, R_FO = np.array(FIT["R_up"]), np.array(FIT["R_fo"])
Fr = json.load(open(os.path.join(FX, "bottom_frame.json"))); uB, vB, axB = (R_UP @ np.array(Fr[k]) for k in ("u", "v", "ax")); CB = np.array(FA.C_b)
HR = np.array(json.load(open(os.path.join(EXO, "avg", "body_mesh.json")))["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HR); HR = _U @ _Vt
S_CUT = 265.0; Z_TOP_BAR, Z_SKIN_BAR = 3.7, -2.8                            # bar section: top (away from the arm) / channel side
HA = np.array([0.0, -1.0, 0.0])                                          # humerus axis (canonical frame), GH -> elbow
LAP_HOLES = [(S_CUT - 6.0, 0.06 + y_) for y_ in (-6.0, 6.0)] + [(S_CUT - 16.0, 0.06 + y_) for y_ in (-6.0, 6.0)]   # neck tongue screws (s, lateral)

def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
def V(p): return cq.Vector(*map(float, p))
def xform(shape, R, t=np.zeros(3)):
    tr = gp_Trsf(); tr.SetValues(*R[0], t[0], *R[1], t[1], *R[2], t[2]); return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())
def cad_to_rest(shape, grp):
    R = R_UP if grp == "up" else R_FO; return xform(shape, R, CB - R @ np.array(FA.C_cad))
def can_to_rest(shape): return xform(shape, HR)
def rest_to_can_pt(p): return HR.T @ np.asarray(p)
def can_to_rest_pt(p): return HR @ np.asarray(p)

def user_parts():
    """the user's arm parts in the rest frame, as the earlier full builds: [(group, name, shape)]. The old scissor shoulder
    and its hardware are left out; BOTTOM is cut at S_CUT with 2x M4 tapped for the arm-end bracket lap"""
    out = []; user = load(); ax_c = np.array(Fr["ax"])
    for name, inst, s in user:
        if name == "BOTTOM":
            r = cad_to_rest(s, "up")
            big = cq.Workplane(cq.Plane(origin=tuple(CB + S_CUT * uB), xDir=tuple(vB), normal=tuple(-uB))).rect(800, 800).extrude(800).val()
            r = r.intersect(big)
            import g2cad as G                                                          # 4x M3 countersunk through the 2 mm web
            for s_, y_ in LAP_HOLES:
                p0 = CB + s_ * uB + y_ * vB
                tool = G.revolve_profile([("line", (0, -3.0), (1.7, -3.0)), ("line", (1.7, -3.0), (1.7, 2.25)), ("line", (1.7, 2.25), (4.15, 4.7)),
                                             ("line", (4.15, 4.7), (0, 4.7)), ("line", (0, 4.7), (0, -3.0))], axB)
                r = r.cut(tool.moved(cq.Location(V(p0))))
            out.append(("H", "BOTTOM (user's bar, cut at s 265, 4x M3 countersunk for the neck tongue)", r)); continue
        if s.Volume() < 1 or name.startswith(("SHOULDER LINK", '0.245" ID')) or name == "RETAINING CLAMP" \
           or name.startswith("DRY RUNNING") or name.startswith("M4 ULTRA LOW PROFILE SOCKET HEAD SCREW, 8mm"): continue
        grp = "F" if name in ("MIDDLE", "FOREARM CUFF") or name.startswith("Hex socket head countersunk") else "H"
        out.append((grp, name, cad_to_rest(s, "up" if grp == "H" else "fore")))
    v2 = os.path.join(FX, "upper_cuff_fair.step"); FC = os.path.join(HERE, "..", "fair_cad", "out_cuff")
    if os.path.exists(v2) and not os.environ.get("CUFF_V1"):                     # conformal G2 shell (fair_cad/cuff_fair.py), rest frame
        out.append(("H", "UPPER ARM CUFF (conformal G2 shell, AlSi10Mg bead blasted)", cq.importers.importStep(v2).val()))
        for k in range(6): out.append(("H", "M4x6 ISO 10642 countersunk (upper cuff)", cq.importers.importStep(os.path.join(FC, f"screw_{k}.step")).val()))
        return out
    cuff = cq.importers.importStep(os.path.join(FX, "upper_cuff_cad.step")).val()
    out.append(("H", "UPPER ARM CUFF (forearm cuff design x1.24)", cad_to_rest(cuff, "up")))
    scr = [p for p in user if p[0].startswith("Hex socket head countersunk")][0][2]; sc_c = np.array(scr.Center().toTuple())
    MID_c = [p[2] for p in user if p[0] == "MIDDLE"][0]; vm, _ = MID_c.tessellate(0.2); Pm = np.array([[q.x, q.y, q.z] for q in vm]); zface = (Pm @ ax_c).min()
    off_axis = sc_c @ ax_c - zface
    for s_ in (94.25, 124.25, 154.25):
        for y_ in (-8.75, 8.75):
            hole = CB + s_ * uB + y_ * vB - 2.8 * axB
            out.append(("H", "Hex socket head countersunk screw M4x0.7x8 (upper cuff)", xform(scr, R_UP, hole + off_axis * axB - R_UP @ sc_c)))
    return out

def bar_lap_frame():
    """lap pad on the bar top, canonical frame: centre, along-bar (toward the shoulder), lateral, up (away from the arm)"""
    c = CB + (S_CUT - 11.0) * uB + Z_TOP_BAR * axB
    return rest_to_can_pt(c), rest_to_can_pt(uB), rest_to_can_pt(vB), rest_to_can_pt(axB)
