import numpy as np, json
from load_arm import load
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane
parts = load(); B = [p for p in parts if p[0] == "BOTTOM"][0][2]
J = json.load(open("../arm-rom/arm_rom.json")); E = J["elbow"]; C = np.array(E["centre"]); ax = np.array(E["axis"]); ax /= np.linalg.norm(ax)
vs, _ = B.tessellate(0.2); P = np.array([[v.x, v.y, v.z] for v in vs])
# bar direction: principal direction of the points projected on the plane normal to the elbow axis
Q = P - C; Qp = Q - np.outer(Q @ ax, ax); w, V = np.linalg.eigh(np.cov(Qp.T)); u = V[:, -1]
if (Qp @ u).mean() < 0: u = -u                                   # from the elbow toward the shoulder
v = np.cross(ax, u)
L = np.c_[Q @ u, Q @ v, Q @ ax]
print("extent along bar", L[:, 0].min().round(1), L[:, 0].max().round(1), " across", L[:, 1].min().round(1), L[:, 1].max().round(1), " thick", L[:, 2].min().round(2), L[:, 2].max().round(2))
for s in (20, 60, 100, 150, 200, 250, 300, 350, 380, 395, 400):
    m = np.abs(L[:, 0] - s) < 0.5
    if m.any(): print(f"  s={s}: width {L[m,1].min():.1f}..{L[m,1].max():.1f}  z {L[m,2].min():.2f}..{L[m,2].max():.2f}")
holes = []
for f in B.Faces():
    a = BRepAdaptor_Surface(f.wrapped)
    if a.GetType() == GeomAbs_Cylinder:
        cy = a.Cylinder(); r = cy.Radius(); o = cy.Location(); d = cy.Axis().Direction()
        o = np.array([o.X(), o.Y(), o.Z()]) - C; dd = np.array([d.X(), d.Y(), d.Z()])
        holes.append((round(r, 2), round(o @ u, 2), round(o @ v, 2), round(abs(dd @ ax), 3)))
for h in sorted(set(holes), key=lambda t: t[1]): print("  cyl r", h[0], "at s", h[1], "y", h[2], "|axis.elbow|", h[3])
json.dump(dict(C=C.tolist(), u=u.tolist(), v=v.tolist(), ax=ax.tolist()), open("bottom_frame.json", "w"))
