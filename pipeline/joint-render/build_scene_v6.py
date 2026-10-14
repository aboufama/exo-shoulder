"""v6 scene for the EXO joint animation: JOINT SUBASSY (1).step (joint + forearm cuff + 6 cuff screws), with
  * the cuff skeletonized on the INSIDE only: an isogrid of blind triangular pockets in the bore whose floors follow
    the local wall (>= SKIN mm of solid skin left everywhere), so the outside stays untouched and clean;
  * all screws remodelled with real ISO M4x0.7 threads: 3x ultra-low-head (joint) and 6x countersunk M4x8 (cuff),
    each as its own node pivoting on its own axis so it can spin;
  * the real 6704 bearing (rings, shields, balls), washers, magnet and the post's flanged sleeve from the STEP.
Joint axis at the origin (CAD frame, mm). Writes joint_v6.glb and cuff_skeleton.step.

    python3 build_scene_v6.py
"""
import math
import os
import sys

import cadquery as cq
from OCP.BRepIntCurveSurface import BRepIntCurveSurface_Inter
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "joint-verification"))
sys.argv = sys.argv[:1] + [os.path.join(HERE, "source_v6", "assembly.step")]
from features import read                                               # noqa: E402
from build_scene import mesh, write_glb, screw_head, thread             # noqa: E402

ARM_Z, R_BORE = -53.0, 49.0              # cuff bore: axis along x at z = -53, radius 49
SKIN = 1.2                               # solid skin left under every pocket (mm)
TRI, RIB, RC = 12.0, 1.6, 0.9            # isogrid: triangle side, rib width, pocket corner radius
PHI = (24.0, 108.0)                      # pocketed arc each side (deg from the top): clear of the screw land and tips
X_MARGIN = 5.0                           # solid border at each end of the cuff


def outer_r(C, x, phi):
    """Distance from the arm axis to the cuff's outer skin along the ray at angle phi (rad from +z toward +y)."""
    it = BRepIntCurveSurface_Inter()
    it.Init(C.wrapped, gp_Lin(gp_Pnt(x, 0, ARM_Z), gp_Dir(0, math.sin(phi), math.cos(phi))), 1e-6)
    rs = []
    while it.More():
        p = it.Pnt(); rs.append(math.hypot(p.Y(), p.Z() - ARM_Z)); it.Next()
    out = [r for r in rs if r > R_BORE + 0.3]
    return min(out) if out else None


def skeletonize(C):
    bb = C.BoundingBox()
    x0, x1 = bb.xmin + 1.0 + X_MARGIN, bb.xmax - 1.0 - X_MARGIN
    h = TRI * math.sqrt(3) / 2
    inr = TRI / (2 * math.sqrt(3))
    k = (inr - RIB / 2 - RC) / inr                                  # inset so ribs are RIB wide after rounding
    pockets, skipped = [], 0
    for side in (+1, -1):
        u_lo, u_hi = math.radians(PHI[0]) * R_BORE, math.radians(PHI[1]) * R_BORE
        row = 0
        while u_lo + (row + 1) * h <= u_hi:
            ua, ub = u_lo + row * h, u_lo + (row + 1) * h
            j = 0
            while True:
                v = x0 + j * TRI / 2 + (row % 2) * TRI / 2
                if v + TRI > x1 + 1e-6:
                    break
                up = j % 2 == 0
                tri = [(v, ua), (v + TRI, ua), (v + TRI / 2, ub)] if up else [(v, ub), (v + TRI, ub), (v + TRI / 2, ua)]
                cx = sum(p[0] for p in tri) / 3; cu = sum(p[1] for p in tri) / 3
                tri = [(cx + (p[0] - cx) * k, cu + (p[1] - cu) * k) for p in tri]
                samples = tri + [(cx, cu)] + [((tri[i][0] + tri[i - 1][0]) / 2, (tri[i][1] + tri[i - 1][1]) / 2) for i in range(3)]
                ro = [outer_r(C, sx, side * su / R_BORE) for sx, su in samples]
                if any(r is None for r in ro) or min(ro) - SKIN - R_BORE < 0.8:
                    skipped += 1; j += 1; continue
                floor = min(ro) - SKIN
                phc = side * cu / R_BORE
                n = cq.Vector(0, math.sin(phc), math.cos(phc))
                o = cq.Vector(cx, (R_BORE - 3) * math.sin(phc), ARM_Z + (R_BORE - 3) * math.cos(phc))
                pl = cq.Plane(origin=o, xDir=cq.Vector(1, 0, 0), normal=n)
                yv = pl.yDir                                            # local +y on the tangent plane
                # local coords: x along the cuff, y = signed arc offset (tangent direction of increasing u)
                tang = cq.Vector(0, math.cos(phc), -math.sin(phc)) * side
                sgn = 1 if yv.dot(tang) > 0 else -1
                pts = [(p[0] - cx, sgn * (p[1] - cu)) for p in tri]
                prism = cq.Workplane(pl).polyline(pts).close().offset2D(RC).extrude(12.0).val()
                cyl = cq.Solid.makeCylinder(floor, bb.xlen + 10, cq.Vector(bb.xmin - 5, 0, ARM_Z), cq.Vector(1, 0, 0))
                pockets.append(prism.intersect(cyl))
                j += 1
            row += 1
    print(f"  {len(pockets)} pockets, {skipped} skipped (wall too thin)", flush=True)
    out = C
    for i in range(0, len(pockets), 25):                            # cut in batches
        out = out.cut(cq.Compound.makeCompound(pockets[i:i + 25]))
    return out.clean(), len(pockets)


def countersunk_m4x8():
    """ISO 10642-style M4x8 countersunk hex socket: head 7.5 dia, 90 deg, 2.5 socket. Head face at z = 0, shank
    toward -z (same frame as the joint screws; flipped into place by the node rotation)."""
    rk = 3.765
    head = cq.Solid.makeCone(rk, 2.0, rk - 2.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, -1))
    head = cq.Workplane().add(head).union(cq.Workplane().circle(rk).extrude(-0.12))
    head = head.faces(">Z").workplane().polygon(6, 2.5 / math.cos(math.pi / 6)).cutBlind(-1.6)
    return head.val()


if __name__ == "__main__":
    PL = read(sys.argv[1])                                      # list: several parts share a name
    P = dict(PL)
    ring = P["Revolve1[1]"].BoundingBox(); AX = (ring.xmin + ring.xmax) / 2
    mv = lambda s, dx=-AX, dy=0.0, dz=0.0: s.moved(cq.Location(cq.Vector(dx, dy, dz)))
    print("axis x =", round(AX, 3), flush=True)

    cache = os.path.join(HERE, "cuff_skeleton.step")
    if os.path.exists(cache) and "--recut" not in sys.argv:
        cuff = cq.importers.importStep(cache).val()
    else:
        cuff, npk = skeletonize(P["FOREARM CUFF"])
        cq.exporters.export(cq.Workplane().add(cuff), cache)
    print(f"  cuff {P['FOREARM CUFF'].Volume() / 1000:.1f} -> {cuff.Volume() / 1000:.1f} cm3, valid {cuff.isValid()}", flush=True)

    balls = [s for n, s in PL if n.startswith("CirPattern1") or n == "Revolve4"]
    washers = sorted([s for n, s in PL if n.startswith("IGUS THRUST WASHER")], key=lambda s: s.BoundingBox().zmin)
    solids = dict(BOTTOM=P["BOTTOM"], MIDDLE=P["MIDDLE"], TOP=P["TOP"], CUFF=cuff,
                  BEARING_OUTER=P["Revolve1[1]"], BEARING_INNER=P["Revolve3"],
                  SHIELDS=cq.Compound.makeCompound([P["Revolve1[2]"], P["Revolve1[3]"]]),
                  WASHER_LO=washers[0], WASHER_UP=washers[1],
                  MAGNET=P["5mm D, 2.5mm H, N42 MAGNET"],
                  SLEEVE=P["DRY RUNNING FLANGED SLEEVE BEARING, 6mm ID, 4mm L, PLASTIC BLEND"])
    out = []
    for name, s in solids.items():
        # balls are hidden inside the shielded bearing: left out. Mesh density per part, tuned to stay under the
        # serverless payload limit without visible faceting at 1080p.
        lin, ang = dict(CUFF=(0.06, 0.2), BOTTOM=(0.03, 0.12), MIDDLE=(0.025, 0.1), TOP=(0.02, 0.1), SLEEVE=(0.03, 0.15), BEARING_OUTER=(0.02, 0.1), BEARING_INNER=(0.02, 0.1)).get(name, (0.012, 0.08))
        Pm, N, T, I = mesh(mv(s), lin=lin, ang=ang)
        out.append((name, Pm, N, T, I)); print(f"{name:14s} {len(I):7d} tris", flush=True)

    # joint screws: threaded ultra-low heads, head underside on TOP's counterbore floor (z = 6.75)
    hp, hn, ht, hi = mesh(screw_head(), lin=0.006, ang=0.06)
    tp, tn, tt, ti = thread(length=6.0)
    jp, jn, jt, ji = hp + tp, hn + tn, ht + tt, hi + [(a + len(hp), b + len(hp), c + len(hp)) for a, b, c in ti]
    for k, (x, y) in enumerate(((-168.04, 6.25), (-173.45, -3.13), (-162.63, -3.13))):
        out.append((f"SCREW{k}", jp, jn, jt, ji, (x - AX, y, 6.75)))
    # cuff screws: countersunk M4x8, flipped (head down inside the cuff, shank up into MIDDLE), head face z = -4.73
    cp, cn, ct, ci = mesh(countersunk_m4x8(), lin=0.006, ang=0.06)
    tp, tn, tt, ti = thread(length=8.0)
    sp = cp + tp; sn = cn + tn; st = ct + tt; si = ci + [(a + len(cp), b + len(cp), c + len(cp)) for a, b, c in ti]
    flip = lambda v: (v[0], -v[1], -v[2])                              # 180 deg about x: keeps the thread right-handed
    sp = [flip(v) for v in sp]; sn = [flip(v) for v in sn]
    for k, (x, y) in enumerate(((-236.045, 8.745), (-236.045, -8.755), (-266.045, 8.745), (-266.045, -8.755),
                                (-296.045, 8.745), (-296.045, -8.755))):
        out.append((f"CSCREW{k}", sp, sn, st, si, (x - AX, y, -4.73)))
    print(f"screws: joint {len(ji)} tris, cuff {len(si)} tris each", flush=True)
    write_glb(os.path.join(HERE, "joint_v6.glb"), out)
    print("wrote joint_v6.glb", os.path.getsize(os.path.join(HERE, "joint_v6.glb")) // 1024, "KB", flush=True)
