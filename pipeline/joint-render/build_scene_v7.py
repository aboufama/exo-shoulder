"""v7 scene: JOINT SUBASSY (1).step with an organic inside-only lattice on the forearm cuff.

Lattice: each side of the cuff's bore is one panel, inset a constant margin M from every edge (cuff ends, C tips and
the screw land). The panel is triangulated irregularly (Poisson-disc points + jittered boundary points, Delaunay),
so the triangles tile it exactly; every triangle is then inset by a constant RIB/2 with RC-rounded corners. Ribs are
therefore one constant width everywhere and the border to every edge is one constant M + RIB/2: organic, but clean.
Pockets are blind, cut radially into the bore to a constant DEPTH (never closer than SKIN to the outer surface), so
the outside of the cuff is untouched.

Also: threaded M4 screws (3 joint ultra-low heads, 6 countersunk cuff screws), the real bearing, washers, magnet and
the post's sleeve. Joint axis at the origin. Writes joint_v7.glb and cuff_lattice_v7.step.

    python3 build_scene_v7.py [--recut]
"""
import math
import os
import sys

import numpy as np
import cadquery as cq
from scipy.spatial import Delaunay
from OCP.BRepIntCurveSurface import BRepIntCurveSurface_Inter
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "joint-verification"))
RECUT = "--recut" in sys.argv
sys.argv = sys.argv[:1] + [os.path.join(HERE, "source_v6", "assembly.step")]
from features import read                                               # noqa: E402
from build_scene import mesh, write_glb, screw_head, thread             # noqa: E402

ARM_Z, R_BORE = -53.0, 49.0
X_BORE = (-320.0, -212.0)                # bore extent along x (STEP frame)
S_LAND = 13.3                            # arc from the top centre to the edge of the screw counterbores
S_TIP = R_BORE * math.acos((-76.6 - ARM_Z) / R_BORE)   # arc from the top centre to the C tip
M = 4.5                                  # constant border to every edge
RIB, RC = 2.2, 2.6                       # rib width, pocket corner radius
DEPTH, SKIN = 2.2, 1.2                   # pocket depth from the bore; minimum skin to the outer surface
SPACING = 23.0                           # target triangle edge
SEED = 7


def outer_r(C, x, phi):
    """Median of three nearby rays: a single ray grazing the band-channel step reads a false thin wall."""
    rs = sorted(r for r in (_outer_r(C, x + dx, phi) for dx in (-0.6, 0.0, 0.6)) if r is not None)
    return rs[len(rs) // 2] if rs else None


def _outer_r(C, x, phi):
    it = BRepIntCurveSurface_Inter()
    it.Init(C.wrapped, gp_Lin(gp_Pnt(x, 0, ARM_Z), gp_Dir(0, math.sin(phi), math.cos(phi))), 1e-6)
    rs = []
    while it.More():
        p = it.Pnt(); rs.append(math.hypot(p.Y(), p.Z() - ARM_Z)); it.Next()
    out = [r for r in rs if r > R_BORE + 0.3]
    return min(out) if out else None


def panel_points(x0, x1, s0, s1, rng):
    """Jittered boundary points (so triangles meet the panel edges) + Poisson-disc interior points."""
    pts = [(x0, s0), (x1, s0), (x1, s1), (x0, s1)]
    for (a0, b0), (a1, b1) in (((x0, s0), (x1, s0)), ((x1, s0), (x1, s1)), ((x1, s1), (x0, s1)), ((x0, s1), (x0, s0))):
        L = math.hypot(a1 - a0, b1 - b0); n = max(1, round(L / SPACING))
        for i in range(1, n):
            u = (i + rng.uniform(-0.22, 0.22)) / n
            pts.append((a0 + (a1 - a0) * u, b0 + (b1 - b0) * u))
    inner = []
    for _ in range(6000):                                             # dart throwing
        p = (rng.uniform(x0 + 0.55 * SPACING, x1 - 0.55 * SPACING), rng.uniform(s0 + 0.55 * SPACING, s1 - 0.55 * SPACING))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) > 0.92 * SPACING for q in pts + inner):
            inner.append(p)
    return np.array(pts + inner)


def inset(tri, d):
    """Exact constant inward offset of a CCW triangle by d (intersection of the offset edge lines)."""
    P = [np.array(p, float) for p in tri]
    lines = []
    for i in range(3):
        a, b = P[i], P[(i + 1) % 3]
        t = (b - a) / np.linalg.norm(b - a); n = np.array([-t[1], t[0]])          # inward normal (CCW)
        lines.append((a + n * d, t))
    out = []
    for i in range(3):
        (p1, t1), (p2, t2) = lines[i - 1], lines[i]
        A = np.array([t1, -t2]).T
        try:
            u = np.linalg.solve(A, p2 - p1)
        except np.linalg.LinAlgError:
            return None
        out.append(p1 + t1 * u[0])
    # degenerate if the inset flipped
    area = lambda Q: 0.5 * ((Q[1][0] - Q[0][0]) * (Q[2][1] - Q[0][1]) - (Q[2][0] - Q[0][0]) * (Q[1][1] - Q[0][1]))
    return out if area(out) > 0.5 else None


def rounded(tri, rc, step=0.6):
    """Outward offset of a (CCW) triangle by rc: straight edges + corner arcs -> dense closed polyline."""
    P = [np.array(p) for p in tri]; pts = []
    for i in range(3):
        a, b, c = P[i - 1], P[i], P[(i + 1) % 3]
        n1 = (b - a)[::-1] * np.array([1, -1]); n1 /= np.linalg.norm(n1)      # outward normals (CCW)
        n2 = (c - b)[::-1] * np.array([1, -1]); n2 /= np.linalg.norm(n2)
        a1, a2 = math.atan2(n1[1], n1[0]), math.atan2(n2[1], n2[0])
        while a2 < a1: a2 += 2 * math.pi
        k = max(2, int((a2 - a1) * rc / step))
        pts += [tuple(b + rc * np.array([math.cos(a1 + (a2 - a1) * j / k), math.sin(a1 + (a2 - a1) * j / k)])) for j in range(k + 1)]
    return pts


def pocket_solid(poly, side, depth, x_lo, x_hi):
    """Radial ruled solid through the unrolled polygon (x, s), cut to the bore band r in [R_BORE - 2, R_BORE + depth]."""
    def wire(r):
        mp = BRepBuilderAPI_MakePolygon()
        for x, s in poly:
            ph = side * s / R_BORE
            mp.Add(gp_Pnt(x, r * math.sin(ph), ARM_Z + r * math.cos(ph)))
        mp.Close(); return mp.Wire()
    ts = BRepOffsetAPI_ThruSections(True, True)
    ts.AddWire(wire(R_BORE - 4)); ts.AddWire(wire(R_BORE + 8)); ts.Build()
    prism = cq.Shape.cast(ts.Shape())
    band = cq.Solid.makeCylinder(R_BORE + depth, x_hi - x_lo + 20, cq.Vector(x_lo - 10, 0, ARM_Z), cq.Vector(1, 0, 0))
    return prism.intersect(band)


def lattice(C):
    rng = np.random.default_rng(SEED)
    x0, x1 = X_BORE[0] + M, X_BORE[1] - M
    s0, s1 = S_LAND + M, S_TIP - M
    pts = panel_points(x0, x1, s0, s1, rng)
    tri = Delaunay(pts).simplices
    pockets, kept = [], 0
    for side in (+1, -1):                                            # mirrored: one design, both sides
        for t in tri:
            P = [tuple(pts[i]) for i in t]
            ar = 0.5 * ((P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) - (P[2][0] - P[0][0]) * (P[1][1] - P[0][1]))
            if ar < 0: P = [P[0], P[2], P[1]]
            core = inset(P, RIB / 2 + RC)
            if core is None:
                continue
            poly = rounded(core, RC)
            # depth: constant, unless the wall is locally too thin for DEPTH + SKIN
            samp = poly[::max(1, len(poly) // 12)] + [tuple(np.mean(core, axis=0))]
            ro = [r for r in (outer_r(C, x, side * s / R_BORE) for x, s in samp) if r is not None]
            if not ro:
                print("    no wall reading for a pocket", flush=True); continue
            d = min(DEPTH, min(ro) - SKIN - R_BORE)
            if d < 0.6:
                print(f"    wall too thin for a pocket (d={d:.2f})", flush=True); continue
            pockets.append(pocket_solid(poly, side, d, X_BORE[0], X_BORE[1])); kept += 1
    print(f"  panel {x1 - x0:.0f} x {s1 - s0:.0f} mm per side, {len(tri)} triangles, {kept} pockets cut", flush=True)
    out = C
    for i in range(0, len(pockets), 12):
        out = out.cut(cq.Compound.makeCompound(pockets[i:i + 12]))
    return out.clean()


def countersunk_m4x8():
    rk = 3.765
    head = cq.Solid.makeCone(rk, 2.0, rk - 2.0, cq.Vector(0, 0, 0), cq.Vector(0, 0, -1))
    head = cq.Workplane().add(head).union(cq.Workplane().circle(rk).extrude(-0.12))
    head = head.faces(">Z").workplane().polygon(6, 2.5 / math.cos(math.pi / 6)).cutBlind(-1.6)
    return head.val()


if __name__ == "__main__":
    PL = read(sys.argv[1]); P = dict(PL)
    ring = P["Revolve1[1]"].BoundingBox(); AX = (ring.xmin + ring.xmax) / 2
    mv = lambda s: s.moved(cq.Location(cq.Vector(-AX, 0, 0)))
    cache = os.path.join(HERE, "cuff_lattice_v7.step")
    if os.path.exists(cache) and not RECUT:
        cuff = cq.importers.importStep(cache).val()
    else:
        cuff = lattice(P["FOREARM CUFF"])
        cq.exporters.export(cq.Workplane().add(cuff), cache)
    print(f"  cuff {P['FOREARM CUFF'].Volume() / 1000:.1f} -> {cuff.Volume() / 1000:.1f} cm3, valid {cuff.isValid()}", flush=True)

    washers = sorted([s for n, s in PL if n.startswith("IGUS THRUST WASHER")], key=lambda s: s.BoundingBox().zmin)
    solids = dict(BOTTOM=P["BOTTOM"], MIDDLE=P["MIDDLE"], TOP=P["TOP"], CUFF=cuff,
                  BEARING_OUTER=P["Revolve1[1]"], BEARING_INNER=P["Revolve3"],
                  SHIELDS=cq.Compound.makeCompound([P["Revolve1[2]"], P["Revolve1[3]"]]),
                  WASHER_LO=washers[0], WASHER_UP=washers[1], MAGNET=P["5mm D, 2.5mm H, N42 MAGNET"],
                  SLEEVE=P["DRY RUNNING FLANGED SLEEVE BEARING, 6mm ID, 4mm L, PLASTIC BLEND"])
    dens = dict(CUFF=(0.05, 0.15), BOTTOM=(0.03, 0.12), MIDDLE=(0.025, 0.1), TOP=(0.02, 0.1), SLEEVE=(0.03, 0.15),
                BEARING_OUTER=(0.02, 0.1), BEARING_INNER=(0.02, 0.1))
    out = []
    for name, s in solids.items():
        lin, ang = dens.get(name, (0.012, 0.08))
        Pm, N, T, I = mesh(mv(s), lin=lin, ang=ang)
        out.append((name, Pm, N, T, I)); print(f"{name:14s} {len(I):7d} tris", flush=True)
    hp, hn, ht, hi = mesh(screw_head(), lin=0.006, ang=0.06)
    tp, tn, tt, ti = thread(length=6.0)
    jp, jn, jt, ji = hp + tp, hn + tn, ht + tt, hi + [(a + len(hp), b + len(hp), c + len(hp)) for a, b, c in ti]
    for k, (x, y) in enumerate(((-168.04, 6.25), (-173.45, -3.13), (-162.63, -3.13))):
        out.append((f"SCREW{k}", jp, jn, jt, ji, (x - AX, y, 6.75)))
    cp, cn, ct, ci = mesh(countersunk_m4x8(), lin=0.006, ang=0.06)
    tp, tn, tt, ti = thread(length=8.0)
    flip = lambda v: (v[0], -v[1], -v[2])                              # 180 deg about x keeps the thread right-handed
    sp = [flip(v) for v in cp + tp]; sn = [flip(v) for v in cn + tn]; st = ct + tt
    si = ci + [(a + len(cp), b + len(cp), c + len(cp)) for a, b, c in ti]
    for k, (x, y) in enumerate(((-236.045, 8.745), (-236.045, -8.755), (-266.045, 8.745), (-266.045, -8.755),
                                (-296.045, 8.745), (-296.045, -8.755))):
        out.append((f"CSCREW{k}", sp, sn, st, si, (x - AX, y, -4.73)))
    write_glb(os.path.join(HERE, "joint_v7.glb"), out)
    print("wrote joint_v7.glb", os.path.getsize(os.path.join(HERE, "joint_v7.glb")) // 1024, "KB", flush=True)
