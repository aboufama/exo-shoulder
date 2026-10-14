import numpy as np, json, collections
from load_arm import load
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Torus, GeomAbs_BSplineSurface, GeomAbs_Cone, GeomAbs_SurfaceOfExtrusion
parts = load(); CU = [p for p in parts if p[0] == "FOREARM CUFF"][0][2]; MID = [p for p in parts if p[0] == "MIDDLE"][0][2]
E = json.load(open("../arm-rom/arm_rom.json"))["elbow"]; C = np.array(E["centre"]); ax = np.array(E["axis"]); fd = np.array(E["forearm_dir"])
T = collections.Counter(); cyls = []
for f in CU.Faces():
    a = BRepAdaptor_Surface(f.wrapped); t = a.GetType(); T[str(t).split('.')[-1]] += 1
    if t == GeomAbs_Cylinder:
        cy = a.Cylinder(); d = cy.Axis().Direction(); o = cy.Location()
        cyls.append((round(cy.Radius(), 2), np.round([d.X(), d.Y(), d.Z()], 3).tolist(), np.round([o.X(), o.Y(), o.Z()], 1).tolist(), round(f.Area(), 1)))
print(dict(T)); print("faces", len(CU.Faces()), "vol", round(CU.Volume()))
for c in sorted(cyls, key=lambda t: -t[3])[:12]: print("  cyl", c)
print("forearm dir", fd.round(3), "elbow axis", ax.round(3))
o = np.array([-488.6, 123.1, 225.7]); a = fd / np.linalg.norm(fd)
e1 = ax - (ax @ a) * a; e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)        # e1: toward the link (elbow-axis side)
vs, _ = CU.tessellate(0.05, 0.05); P = np.array([[v.x, v.y, v.z] for v in vs]) - o
z = P @ a; x = P @ e1; y = P @ e2; r = np.hypot(x, y); ph = np.degrees(np.arctan2(y, x))
print("axial span", z.min().round(1), z.max().round(1), " r span", r.min().round(2), r.max().round(2))
mid = np.abs(z - (z.min() + z.max()) / 2) < 1.0
print("mid-section: phi span", ph[mid].min().round(1), ph[mid].max().round(1))
for p0 in range(-180, 181, 15):
    m = mid & (np.abs(ph - p0) < 3)
    if m.any(): print(f"   phi {p0:4d}: r {r[m].min():.2f}..{r[m].max():.2f}")
# axial profile at the top (phi ~ 0, under the link) and at the side (phi ~ 90)
for p0 in (0, 60, 120):
    m = np.abs(ph - p0) < 2
    zz = np.round(z[m], 0)
    print(f"phi {p0}: z {z[m].min():.1f}..{z[m].max():.1f}; r_max by z:", [ (int(q), round(r[m][zz == q].max(), 2)) for q in np.unique(zz)[::8]])
# holes in cuff frame
for c in cyls:
    if abs(c[0] - 2.15) < 0.01:
        q = np.array(c[2]) - o; print("   hole z", round(q @ a, 1), "lateral", round(q @ e2, 2))
