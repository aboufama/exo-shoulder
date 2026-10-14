"""numerical G2 check: curvature across every edge-round junction of a link (sphere -> corner -> wall -> corner -> sphere)"""
import math, numpy as np
import g2cad as G, fea_link as FL
from OCP.GeomLProp import GeomLProp_SLProps
from OCP.BRep import BRep_Tool
from OCP.gp import gp_Dir
arc = 64.1; pA = np.array([0, 0, 1.0]); pB = np.array([math.sin(math.radians(arc)), 0, math.cos(math.radians(arc))])
r0, r1, e = 124.57, 130.02, 1.0
pf = FL.Planform([(pA, 17.0), (pB, 17.0)], [(pA, pB, 7.0)], (r0 + r1) / 2, k=10.0)
s = G.spherical_link(pf, [pA, pB], r0, r1, e)
worst = {}
for f in s.Faces():
    if f.geomType() != "BSPLINE": continue
    S = BRep_Tool.Surface_s(f.wrapped); u0, u1, v0, v1 = S.Bounds()
    for vv, tag in ((v0, "v0"), (v1, "v1")):
        ks = []
        for uu in np.linspace(u0, u1, 97)[:-1]:
            pr = GeomLProp_SLProps(S, uu, vv, 2, 1e-9); d = gp_Dir(); pr.TangentV(d)
            ks.append(abs(pr.MaxCurvature()) if False else None)
            # normal curvature along the profile (v) direction: II(v,v)/I(v,v)
            D1v = pr.D1V(); D2v = pr.D2V(); n = pr.Normal()
            dv = np.array([D1v.X(), D1v.Y(), D1v.Z()]); d2 = np.array([D2v.X(), D2v.Y(), D2v.Z()]); nn = np.array([n.X(), n.Y(), n.Z()])
            ks[-1] = abs(d2 @ nn) / (dv @ dv)
        worst[(round(f.Area()), tag)] = (min(ks), max(ks))
for k, (a, b_) in worst.items(): print(f"face area {k[0]:5d} {k[1]}: profile-direction curvature {a:.5f} .. {b_:.5f} 1/mm")
print(f"targets: inner sphere 1/r0 = {1 / r0:.5f}, outer sphere 1/r1 = {1 / r1:.5f}, wall 0")
