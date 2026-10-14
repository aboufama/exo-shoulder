"""v3.2 flush joint stack (FEA-sized, thin_study/REPORT.md) (same bearing internals as v3: Ø10 h9 integral pin, 2x igus GTM-1018-010, igus GSM-1012-05,
0.02 mm float; v3.2: 2x igus GTM-1018-005 (0.5), GSM-1012-04 sleeve in a 4.05 hub, 3.0 lower plate) with nothing visible but one hairline per moving seam:
  - washer A sits in a Ø18.3 x 0.85 recess in the lower member's seat (0.15 proud): the upper hub runs 0.15 above the
    lower member's seat face all round
  - washer B sits in a Ø18.3 x 0.85 recess in the cap's underside; the cap rim floats 0.17 over the upper hub
  - the Ø20 cap is one G2 dome (no drive, no screw head, no flat land), clamped onto the pin's end face by an M3 DIN 7984
    low-head screw that comes up from the SKIN side through the pin (Ø3.2 bore) into a blind M3 thread in the cap
  - stack height above the lower member's seat: 8.82 mm (v3: 9.57)
All profiles are (r, z) along the joint axis through the GH centre; z from GH."""
import math
import numpy as np
import cadquery as cq
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "shoulder-d4"))
import g2cad as G
PIN_R, WASH_R, WASH_RI, REC_R, CAP_R = 5.0, 9.0, 5.0, 9.15, 10.0

def rev(segs, axis): return G.revolve_profile(segs, np.asarray(axis, float))
def poly(pts): return [("line", a, b) for a, b in zip(pts, pts[1:] + pts[:1])]

def recess_tool(axis, lv):
    z0, z1 = lv["rec"], lv["S"] + 3.0
    return rev(poly([(0, z0), (REC_R, z0), (REC_R, lv["S"] - 0.2), (REC_R + 0.2, lv["S"]), (REC_R + 3.2, z1), (0, z1)]), axis)

def pin_body(axis, lv):
    """integral pin from inside the plate to the cap clamp face; DIN 509-style relief just above the recess floor"""
    z0, zr, zt = lv["rec"] - 1.5, lv["rec"], lv["pin_top"]
    return rev(poly([(0, z0), (PIN_R + 0.5, z0), (PIN_R + 0.5, zr), (PIN_R - 0.25, zr + 0.05), (PIN_R - 0.25, zr + 0.45),
                     (PIN_R, zr + 0.75), (PIN_R, zt - 0.35), (PIN_R - 0.35, zt), (0, zt)]), axis)

def screw_bore(axis, lv, z_skin):
    """Ø3.2 through the pin + Ø5.8 counterbore from the skin side for the M3 DIN 7984 head (2.0 high, 0.2 under flush)"""
    zc = z_skin + 2.2
    return rev(poly([(0, z_skin - 20), (2.9, z_skin - 20), (2.9, zc), (1.6, zc), (1.6, lv["pin_top"] + 0.5), (0, lv["pin_top"] + 0.5)]), axis), zc

def bore_tool(axis, z0, z1, r=6.0, ch=0.3, ext=3.0):
    return rev(poly([(0, z0 - ext), (r + ch + ext, z0 - ext), (r, z0 + ch), (r, z1 - ch), (r + ch + ext, z1 + ext), (0, z1 + ext)]), axis)

def cap(axis, lv, crown=2.6, k_top=0.035):
    z0 = lv["pin_top"]; up, inn, down = (0, 1.0), (-1.0, 0), (0, -1.0)
    rd = 0.35                                                                          # washer B recess (0.5 washer, 0.15 proud)
    segs = [("line", (1.25, z0), (REC_R, z0)), ("line", (REC_R, z0), (REC_R, z0 - rd)), ("line", (REC_R, z0 - rd), (CAP_R - 0.1, z0 - rd)),
            ("line", (CAP_R - 0.1, z0 - rd), (CAP_R, z0 - rd + 0.1)), ("line", (CAP_R, z0 - rd + 0.1), (CAP_R, z0 - 0.15)),
            ("bez", G.g2_blend((CAP_R, z0 - 0.15), up, 0.0, inn, (0.0, z0 + crown), inn, k_top, down, frac=0.45)),
            ("line", (0.0, z0 + crown), (0.0, z0 + 2.1)), ("line", (0.0, z0 + 2.1), (1.25, z0 + 1.9)), ("line", (1.25, z0 + 1.9), (1.25, z0))]
    return rev(segs, axis)

def washer(axis, z, t=0.5):
    e = 0.1; return rev(poly([(WASH_RI, z), (WASH_R - e, z), (WASH_R, z + e), (WASH_R, z + t - e), (WASH_R - e, z + t), (WASH_RI, z + t)]), axis)

def sleeve(axis, z, L=4.0):
    return rev(poly([(5.0, z), (5.7, z), (6.0, z + 0.3), (6.0, z + L - 0.3), (5.7, z + L), (5.0, z + L)]), axis)

def m3_low_head(axis, zc, lv):
    """M3 DIN 7984 (head Ø5.5 x 2.0, hex 2.0) from the skin side; length to the cap thread, standard sizes"""
    room = lv["pin_top"] + 2.0 - zc; L = max(l for l in (6, 8, 10, 12, 14, 16, 20) if l <= room)
    s = rev(poly([(0, zc - 2.0), (2.75, zc - 2.0), (2.75, zc), (1.5, zc), (1.5, zc + L - 0.3), (1.2, zc + L), (0, zc + L)]), axis)
    n_ = np.asarray(axis, float) / np.linalg.norm(axis); x_ = np.cross(n_, [0, 0, 1.0]) if abs(n_[2]) < 0.9 else np.cross(n_, [1.0, 0, 0]); x_ /= np.linalg.norm(x_)
    hexw = cq.Workplane(cq.Plane(origin=cq.Vector(*(n_ * (zc - 2.1))), xDir=cq.Vector(*x_), normal=cq.Vector(*n_))).polygon(6, 2.0 / math.cos(math.pi / 6)).extrude(1.3).val()
    return s.cut(hexw), L, zc + L - lv["pin_top"]

def joint_parts(axis, lv, z_skin, J):
    """hardware of one joint (in the lower member's frame)"""
    scr, L, eng = m3_low_head(axis, z_skin + 2.2, lv)
    return [(f"J{J} washer A (igus GTM-1018-005, recessed)", washer(axis, lv["rec"])),
            (f"J{J} sleeve (igus GSM-1012-04)", sleeve(axis, lv["U0"])),
            (f"J{J} washer B (igus GTM-1018-005, in the cap)", washer(axis, lv["B0"])),
            (f"J{J} cap (Ti-6Al-4V, G2 dome, no drive)", cap(axis, lv)),
            (f"J{J} M3x{L} DIN 7984 low-head (12.9, zinc-flake silver) from the skin side, {eng:.1f} mm in the cap", scr)]


# ---------------------------------------------------------------- v4 (encoder-ready, Ø23): delegates to joint_v4.py
def v4_lower_features(body, axis, lv):
    import joint_v4 as J4
    a = np.asarray(axis, float)
    import cad_helpers as CH
    pin = J4.pin(a, lv); nf = len(body.Faces())
    for tol in (0.0, 0.02, 0.1):                                                         # pin into the plain body first (robust order)
        b = CH.fuzzy_fuse(body, pin, tol=tol)
        if len(b.Faces()) > nf and b.isValid(): break
    ok_pin = b.isValid()
    rec = J4.rev([(0, lv["rec"]), (9.15, lv["rec"]), (9.15, lv["S"] - 0.1), (9.30, lv["S"] + 0.05), (9.30, lv["S"] + 3), (0, lv["S"] + 3)], a).cut(pin)   # chamfer crosses the seat face transversally
    b2 = b.cut(rec)
    if not b2.isValid():
        from OCP.ShapeFix import ShapeFix_Shape
        sf = ShapeFix_Shape(b2.wrapped); sf.Perform(); b2 = cq.Shape.cast(sf.Shape())
    ok_rec = b2.isValid(); b = b2
    for tool in J4.pin_cuts(a, lv): b = b.cut(tool)
    if not b.isValid():
        print(f"  v4 lower features: pin fuse valid {ok_pin}, recess valid {ok_rec}, pin cuts valid {b.isValid()}", flush=True)
        import os; os.makedirs("out_debug", exist_ok=True); body.exportBrep("out_debug/v4_body.brep"); json_lv = {k: float(v) for k, v in lv.items()}
        import json; json.dump(dict(axis=a.tolist(), lv=json_lv), open("out_debug/v4_args.json", "w"))
    return b
def _frame(a, yref):
    import cad_helpers as CH
    n_, x_, y_ = CH.frame_of(a)
    if yref is not None:                                                                   # cap screws on the line square to the arm (full disc material)
        y_ = np.asarray(yref, float) - (np.asarray(yref, float) @ n_) * n_; y_ /= np.linalg.norm(y_); x_ = np.cross(y_, n_)
    return n_, x_, y_
def v4_upper_features(body, axis, lv, yref=None):
    import joint_v4 as J4, cad_helpers as CH
    a = np.asarray(axis, float); body = body.cut(CH.bore_tool(a, lv["U0"], lv["U1"], 6.0))
    n_, x_, y_ = _frame(a, yref)
    for s_ in (1, -1): body = body.cut(cq.Solid.makeCylinder(0.625, 2.7, cq.Vector(*(y_ * s_ * 10.15 + a * (lv["U1"] - 2.7))), cq.Vector(*a)))   # 2.7 deep: the M1.6x3 goes in 2.54, clear of the lower edge round
    return body
def v4_joint_parts(axis, lv, J, yref=None):
    """lower-member group: washers, magnet, ring nut; upper-member group: sleeve, PCB + IC, cap, 2 cap screws"""
    import joint_v4 as J4, cad_helpers as CH
    a = np.asarray(axis, float); n_, x_, y_ = _frame(a, yref)
    lower = [(f"J{J} washer A (igus GTM-1018-005, recessed)", J4.washer(a, lv["rec"])), (f"J{J} washer B (igus GTM-1018-005)", J4.washer(a, lv["B0"])),
             (f"J{J} magnet Ø4x2 N52 diametric", J4.magnet(a, lv)), (f"J{J} ring nut M8x0.5 18x1 (Ti-6Al-4V)", J4.retainer(a, lv))]
    pd, _tail = J4.pcb(a, lv, x_)
    upper = [(f"J{J} sleeve (igus GSM-1012-04)", J4.sleeve(a, lv["U0"])), (f"J{J} position PCB Ø16 (placeholder)", pd), (f"J{J} angle sensor IC (placeholder)", J4.ic(a, lv)),
             (f"J{J} cap Ø22 G2 dome (Ti-6Al-4V)", J4.cap_noslot(a, lv))]
    for s_ in (1, -1): upper.append((f"J{J} M1.6x3 ISO 10642 Ti (cap)", J4.m16_cs(a, y_ * s_ * 10.15, lv["U1"] + 0.46, 3.0)))
    return lower, upper
