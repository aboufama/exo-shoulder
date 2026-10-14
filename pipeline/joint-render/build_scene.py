"""Scene for the exploded-view render of the EXO elbow joint: the three machined parts from the v5 STEP exports plus
simple stand-ins for the bought parts (6704-2Z bearing, two iglide J thrust washers, 3x M4 low-head screws, the
encoder magnet), placed in their assembled positions with the joint axis at the origin. Writes joint.glb with exact
B-rep normals per mesh node (smooth curved faces, crisp edges) and box-projected UVs for the powder-coat grain.

    python3 build_scene.py
"""
import json
import math
import os
import struct

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepLib import BRepLib_ToolTriangulatedShape
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.TopAbs import TopAbs_REVERSED
from OCP.TopLoc import TopLoc_Location

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "joint-drawings", "source_v5")
AX = -168.04                                                   # joint axis x in the model


def ring(r_out, r_in, h, z0=0.0, ch=0.0):
    s = cq.Workplane("XY").workplane(offset=z0).circle(r_out).circle(r_in).extrude(h)
    if ch:
        s = s.edges().chamfer(ch)
    return s.val()


def bearing():
    """6704-2Z: 20 x 27 x 4. Rings and shields as separate solids so they can take different finishes."""
    outer = ring(13.5, 12.3, 4.0, ch=0.2)
    inner = ring(11.3, 10.0, 4.0, ch=0.2)
    shield = ring(12.3, 11.3, 3.6, z0=0.2)
    return outer.fuse(inner), shield


def screw_head():
    """M4 ultra-low head: 7 x 1.2, domed rim, 2.5 hex socket; underside at z = 0, axis on z."""
    head = cq.Workplane("XY").circle(3.5).extrude(1.2).faces(">Z").edges().fillet(0.5)
    head = head.faces("<Z").edges().chamfer(0.08)
    head = head.faces(">Z").workplane().polygon(6, 2.5 / math.cos(math.pi / 6)).cutBlind(-1.0)
    return head.val()


def thread(length=6.0, P=0.7, d=4.0, seg=72):
    """ISO metric external thread M4x0.7 as a helicoidal mesh: root flat P/4, flanks at 60 deg, crest flat P/8.
    Each profile segment is its own strip (crisp edges, smooth along the helix). Runs from z = +0.4 (inside the
    head) down to z = -length, with a 45 deg chamfered tip and an end cap."""
    H = 0.8660254 * P
    r_maj = d / 2; r_min = r_maj - 5 / 8 * H                    # basic minor radius of the external thread
    knots = [(0.0, r_min), (P / 8, r_min), (P / 2 - P / 16, r_maj), (P / 2 + P / 16, r_maj), (P - P / 8, r_min), (P, r_min)]
    z_tip, z_top = -length, 0.4
    cone = lambda z: (r_min - 0.15) + (z - z_tip)                # 45 deg tip chamfer starting just inside the minor dia
    turns = int(math.ceil((z_top - z_tip) / P)) + 2
    n_th = turns * seg
    P_, N_, T_, I_ = [], [], [], []
    for k in range(len(knots) - 1):
        (w0, r0), (w1, r1) = knots[k], knots[k + 1]
        sub = 1 if r0 == r1 else 3
        rows = []
        for j in range(sub + 1):
            w = w0 + (w1 - w0) * j / sub; r = r0 + (r1 - r0) * j / sub
            row = []
            for i in range(n_th + 1):
                th = 2 * math.pi * i / seg
                z = z_tip - 2 * P + P * th / (2 * math.pi) + w
                rr = min(r, max(cone(z), 0.2)); zz = max(z, z_tip)
                if zz > z_top:
                    zz = z_top
                row.append((rr * math.cos(th), rr * math.sin(th), zz))
            rows.append(row)
        base = len(P_)
        for row in rows:
            P_ += row
        nc = n_th + 1
        for j in range(sub):
            for i in range(n_th):
                a = base + j * nc + i; b = a + 1; c = a + nc; e = c + 1
                I_ += [(a, b, e), (a, e, c)]
    # vertex normals averaged within each strip (strips share no vertices, so profile corners stay sharp)
    acc = [[0.0, 0.0, 0.0] for _ in P_]
    for a, b, c in I_:
        ax_, ay, az = P_[a]; bx, by, bz = P_[b]; cx, cy, cz = P_[c]
        ux, uy, uz = bx - ax_, by - ay, bz - az; vx, vy, vz = cx - ax_, cy - ay, cz - az
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        for q in (a, b, c):
            acc[q][0] += nx; acc[q][1] += ny; acc[q][2] += nz
    for q, (x, y, z) in enumerate(P_):
        n = acc[q]; L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1
        n = [c / L for c in n]
        if n[0] * x + n[1] * y < 0 and z > z_tip + 1e-6:          # point outward
            n = [-c for c in n]
        N_.append(tuple(n)); T_.append((math.atan2(y, x) / 1.0, z / 6.0))
    # make triangle winding agree with the outward normals
    I2 = []
    for a, b, c in I_:
        ax_, ay, az = P_[a]; bx, by, bz = P_[b]; cx, cy, cz = P_[c]
        nx = (by - ay) * (cz - az) - (bz - az) * (cy - ay); ny = (bz - az) * (cx - ax_) - (bx - ax_) * (cz - az)
        mx, my = (ax_ + bx + cx) / 3, (ay + by + cy) / 3
        I2.append((a, b, c) if nx * mx + ny * my >= 0 else (a, c, b))
    # tip cap
    o = len(P_); P_.append((0.0, 0.0, z_tip)); N_.append((0, 0, -1)); T_.append((0, 0))
    rc = cone(z_tip)
    for i in range(seg + 1):
        th = 2 * math.pi * i / seg; P_.append((rc * math.cos(th), rc * math.sin(th), z_tip)); N_.append((0, 0, -1)); T_.append((0, 0))
    for i in range(seg):
        I2.append((o, o + 2 + i, o + 1 + i))
    return P_, N_, T_, I2


def mesh(shape, lin=0.012, ang=0.08, uv_scale=6.0):
    """Positions, exact normals, box-projected UVs and indices for `shape` (mm, Z up)."""
    BRepTools.Clean_s(shape.wrapped)
    BRepMesh_IncrementalMesh(shape.wrapped, lin, False, ang, True)
    P, N, T, I, off = [], [], [], [], 0
    for f in shape.Faces():
        loc = TopLoc_Location(); tri = BRep_Tool.Triangulation_s(f.wrapped, loc)
        if tri is None:
            continue
        BRepLib_ToolTriangulatedShape.ComputeNormals_s(f.wrapped, tri)
        tr = loc.Transformation(); rev = f.wrapped.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(tr); n = tri.Normal(i).Transformed(tr)
            nx, ny, nz = ((-1 if rev else 1) * c for c in (n.X(), n.Y(), n.Z()))
            P.append((p.X(), p.Y(), p.Z())); N.append((nx, ny, nz))
            a = max(range(3), key=lambda k: abs((nx, ny, nz)[k]))           # box projection on the dominant axis
            u, v = [c for k, c in enumerate((p.X(), p.Y(), p.Z())) if k != a]
            T.append((u / uv_scale, v / uv_scale))
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            I.append((off + a - 1, off + c - 1, off + b - 1) if rev else (off + a - 1, off + b - 1, off + c - 1))
        off += tri.NbNodes()
    return P, N, T, I


def write_glb(path, items):
    """items: (name, P, N, T, I). mm -> m, CAD Z-up -> glTF Y-up. One node + mesh per item, no materials (the page
    assigns them by name)."""
    blob, views, accs, meshes, nodes = bytearray(), [], [], [], []

    def add(data, comp, count, typ, target, mn=None, mx=None):
        while len(blob) % 4:
            blob.append(0)
        views.append(dict(buffer=0, byteOffset=len(blob), byteLength=len(data), target=target))
        blob.extend(data)
        a = dict(bufferView=len(views) - 1, componentType=comp, count=count, type=typ)
        if mn is not None:
            a["min"], a["max"] = mn, mx
        accs.append(a)
        return len(accs) - 1

    shared = {}                                                  # identical meshes (same lists) are written once
    for name, P, N, T, I, *tr in items:
        if id(P) in shared:
            node = dict(name=name, mesh=shared[id(P)])
            if tr and tr[0]:
                x, y, z = tr[0]; node["translation"] = [x / 1000, z / 1000, -y / 1000]
            nodes.append(node)
            continue
        Pg = [(x / 1000, z / 1000, -y / 1000) for x, y, z in P]
        Ng = [(x, z, -y) for x, y, z in N]
        mn = [min(p[k] for p in Pg) for k in range(3)]; mx = [max(p[k] for p in Pg) for k in range(3)]
        ip = add(struct.pack(f"<{3 * len(Pg)}f", *[c for p in Pg for c in p]), 5126, len(Pg), "VEC3", 34962, mn, mx)
        inn = add(struct.pack(f"<{3 * len(Ng)}f", *[c for p in Ng for c in p]), 5126, len(Ng), "VEC3", 34962)
        it = add(struct.pack(f"<{2 * len(T)}f", *[c for p in T for c in p]), 5126, len(T), "VEC2", 34962)
        ii = add(struct.pack(f"<{3 * len(I)}I", *[c for t in I for c in t]), 5125, 3 * len(I), "SCALAR", 34963)
        meshes.append(dict(name=name, primitives=[dict(attributes=dict(POSITION=ip, NORMAL=inn, TEXCOORD_0=it), indices=ii)]))
        shared[id(P)] = len(meshes) - 1
        node = dict(name=name, mesh=len(meshes) - 1)
        if tr and tr[0]:
            x, y, z = tr[0]; node["translation"] = [x / 1000, z / 1000, -y / 1000]
        nodes.append(node)
    gltf = dict(asset=dict(version="2.0"), scene=0, scenes=[dict(nodes=list(range(len(nodes))))], nodes=nodes,
                meshes=meshes, accessors=accs, bufferViews=views, buffers=[dict(byteLength=len(blob))])
    js = json.dumps(gltf).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    while len(blob) % 4:
        blob.append(0)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)


if __name__ == "__main__":
    move = lambda s, x=0.0, y=0.0, z=0.0: s.moved(cq.Location(cq.Vector(x, y, z)))
    items = []
    for n in ("BOTTOM", "MIDDLE", "TOP"):
        f = [f for f in os.listdir(SRC) if n in f][0]
        items.append((n, move(cq.importers.importStep(os.path.join(SRC, f)).val(), x=-AX)))
    rings, shields = bearing()
    items += [("BEARING", move(rings, z=0.75)), ("SHIELDS", move(shields, z=0.75)),
              ("WASHER_LO", ring(19.5, 15.0, 1.5, z0=1.0, ch=0.15)), ("WASHER_UP", ring(19.5, 15.0, 1.5, z0=4.0, ch=0.15)),
              ("MAGNET", cq.Workplane("XY").circle(2.5).extrude(2.5).edges().chamfer(0.15).val())]
    out = []
    hp, hn, ht, hi = mesh(screw_head(), lin=0.006, ang=0.06)
    tp, tn, tt, ti = thread()
    sp, sn, st, si = hp + tp, hn + tn, ht + tt, hi + [(a + len(hp), b + len(hp), c + len(hp)) for a, b, c in ti]
    for k, (x, y) in enumerate(((0.0, 6.25), (5.413, -3.125), (-5.413, -3.125))):
        out.append((f"SCREW{k}", sp, sn, st, si, (x, y, 6.75)))
        print(f"SCREW{k}    {len(si):7d} tris", flush=True)
    for name, shape in items:
        P, N, T, I = mesh(shape, lin=0.01 if name in ("BEARING", "SHIELDS", "WASHER_LO", "WASHER_UP", "MAGNET") else 0.012)
        print(f"{name:10s} {len(I):7d} tris", flush=True)
        out.insert(len(out) - 3, (name, P, N, T, I))
    write_glb(os.path.join(HERE, "joint.glb"), out)
    print("wrote joint.glb", os.path.getsize(os.path.join(HERE, "joint.glb")) // 1024, "KB")
