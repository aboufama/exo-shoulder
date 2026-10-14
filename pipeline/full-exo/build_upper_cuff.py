"""Upper-arm cuff = the user's FOREARM CUFF, holes defeatured, scaled uniformly to the upper arm (same form, edge
language and proportions), re-drilled with the same M4 countersunk holes on BOTTOM's cuff pattern (s = 94.25 /
124.25 / 154.25 mm from the elbow axis, y = +-8.75). Scale chosen so the liner gap matches the forearm cuff."""
import json, math, numpy as np, cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Defeaturing
from OCP.TopTools import TopTools_ListOfShape
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Cone
from OCP.gp import gp_Trsf, gp_Pnt
from load_arm import load
import fit_arm as FA

parts = load(); CU = [p for p in parts if p[0] == "FOREARM CUFF"][0][2]
E = json.load(open("../arm-rom/arm_rom.json"))["elbow"]; ax = np.array(E["axis"]); fd = np.array(E["forearm_dir"]); fd /= np.linalg.norm(fd)
o = np.array([-488.6, 123.1, 225.7])
# 1. defeature the six countersunk holes (Ø4.3 bores + their cones)
rm = TopTools_ListOfShape(); nrm = 0
for f in CU.Faces():
    a = BRepAdaptor_Surface(f.wrapped)
    if (a.GetType() == GeomAbs_Cylinder and a.Cylinder().Radius() < 5.0) or (a.GetType() == GeomAbs_Cone and f.Area() < 60):
        rm.Append(f.wrapped); nrm += 1
df = BRepAlgoAPI_Defeaturing(); df.SetShape(CU.wrapped); df.AddFacesToRemove(rm); df.SetRunParallel(False); df.Build()
solid = cq.Shape.cast(df.Shape()); print("defeatured", nrm, "faces ->", len(solid.Faces()), "faces, valid", solid.isValid())
# cuff frame (CAD): axis a along the forearm, e1 toward the link (land), e2 lateral
a = fd; e1 = ax - (ax @ a) * a; e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
vs, _ = solid.tessellate(0.2); P = np.array([[v.x, v.y, v.z] for v in vs]) - o
z = P @ a; r = np.hypot(P @ e1, P @ e2); land_r = r[(np.abs(np.degrees(np.arctan2(P @ e2, P @ e1))) < 6) & (np.abs(z - 55) < 20)].max()
MID = [p for p in parts if p[0] == "MIDDLE"][0][2]; vm, _ = MID.tessellate(0.2); Pm = np.array([[q.x, q.y, q.z] for q in vm]) - o
zm = Pm @ a; mm = (zm > 5) & (zm < 105); rm_ = np.hypot(Pm[mm] @ e1, Pm[mm] @ e2)
land_r = rm_.min()
print(f"forearm cuff: inner r 49.0, MIDDLE's skin-side face at r {land_r:.2f} from the cuff axis, cuff length {z.min():.1f}..{z.max():.1f}")

def place(k):
    """scaled cuff, CAD->body upper-arm frame: axis along the bar, land on BOTTOM's skin-side face, centred at s=124.25"""
    Fr = json.load(open("bottom_frame.json")); C, u, v, axb = (np.array(Fr[x]) for x in ("C", "u", "v", "ax"))
    # target (CAD frame of the upper-arm group): cuff axis // u, land plane = BOTTOM's skin face (z = -2.8), centre s=124.25
    tgt_o = C + 124.25 * u - (2.8 + k * land_r) * axb - 55.0 * k * u      # cuff z runs 0..110k, centred at 55k
    Rsrc = np.c_[a, e1, e2]; Rdst = np.c_[u, axb, np.cross(u, axb)]        # cuff e1 (toward the land) -> +axb (toward the bar)
    Rm = Rdst @ Rsrc.T
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    t = gp_Trsf(); t.SetScale(gp_Pnt(*o), k)
    s = cq.Shape.cast(BRepBuilderAPI_Transform(solid.wrapped, t, True).Shape())
    M = gp_Trsf(); pre = tgt_o - Rm @ o
    M.SetValues(*Rm[0], pre[0], *Rm[1], pre[1], *Rm[2], pre[2])
    s = cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped, M, True).Shape())
    return s, (C, u, v, axb)

def liner_gap(s):
    vs, _ = s.tessellate(0.4); P = np.array([[q.x, q.y, q.z] for q in vs]); Pb = FA.to_body(P, "up")
    return FA.skin_dist(Pb)

best = None
for k in np.arange(1.00, 1.32, 0.02):
    s, _ = place(k)
    # inner surface points: those closest to the cuff axis (bottom 25% of radius)
    vs, _ = s.tessellate(0.4); P = np.array([[q.x, q.y, q.z] for q in vs]); Pb = FA.to_body(P, "up")
    d = FA.skin_dist(Pb)
    # inside test: a point is inside the arm if it is closer to the humerus line than the skin there -> crude: use sign by radius
    hup = FA.hup if hasattr(FA, "hup") else None
    rad = np.linalg.norm(Pb - np.outer(Pb @ FA.hup, FA.hup), axis=1); inner = rad < np.percentile(rad, 30)
    stats = (d[inner].min(), d[inner].mean())
    print(f"k {k:.2f}: inner r {49 * k:.1f}, liner gap min {stats[0]:.1f} mean {stats[1]:.1f}")
    if stats[0] >= 1.0 and (best is None or abs(stats[1] - 11.4) < abs(best[1][1] - 11.4)): best = (k, stats)
print("chosen k", best)

# 2. the user's hole: Ø4.3 through + Ø8.96 counterbore; measure its depth on the original cuff
cb = [f for f in CU.Faces() if BRepAdaptor_Surface(f.wrapped).GetType() == GeomAbs_Cylinder and abs(BRepAdaptor_Surface(f.wrapped).Cylinder().Radius() - 4.48) < 0.02]
f0 = cb[0]; vs_, _ = f0.tessellate(0.05); Q = np.array([[q.x, q.y, q.z] for q in vs_]); dep = (Q @ ax).max() - (Q @ ax).min()
print(f"user's counterbore: Ø8.96 x {dep:.2f} deep (from the inner surface)")
K = 1.24
cuff, (C, u, v, axb) = place(K)
from OCP.ShapeFix import ShapeFix_Shape
oc = C + 124.25 * u - (2.8 + K * land_r) * axb                       # a point on the cuff axis (axis // u)
r_in = 49.0 * K
for s in (94.25, 124.25, 154.25):
    for y in (-8.75, 8.75):
        p = C + s * u + y * v
        cuff = cuff.cut(cq.Solid.makeCylinder(2.15, 80, cq.Vector(*(p - 70 * axb)), cq.Vector(*axb)))
        # inner (arm-side) surface on the hole axis: |(p - t axb) - axis| = r_in, t > 0
        w = p - oc; w -= (w @ u) * u; t = (w @ axb) - math.sqrt(max(0.0, (w @ axb) ** 2 - (w @ w - r_in ** 2)))
        q_in = p - t * axb
        tool = cq.Solid.makeCylinder(4.48, dep + 15.0, cq.Vector(*(q_in - 15.0 * axb)), cq.Vector(*axb))
        c2 = cuff.cut(tool)
        if not c2.isValid():
            sf = ShapeFix_Shape(c2.wrapped); sf.Perform(); c2 = cq.Shape.cast(sf.Shape())
        cuff = c2
        print(f"  hole s {s} y {y:+.2f}: inner surface {t:.2f} mm below the bar plane, valid {cuff.isValid()}")
pass
print("upper cuff valid", cuff.isValid(), "faces", len(cuff.Faces()), "volume", round(cuff.Volume()), "mm3 (forearm", round(CU.Volume()), ")")
cq.exporters.export(cq.Workplane().add(cuff), "upper_cuff_cad.step")      # CAD frame of the upper-arm group (as BOTTOM)
