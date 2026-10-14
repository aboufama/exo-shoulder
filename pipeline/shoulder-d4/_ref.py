import cadquery as cq, collections, sys
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_ChildIterator
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Torus, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Plane, GeomAbs_BSplineSurface, GeomAbs_Sphere
doc = TDocStd_Document(TCollection_ExtendedString("d")); r = STEPCAFControl_Reader(); r.SetNameMode(True)
r.ReadFile(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", "..", "data", "user_cad", "RIGHT ARM SUBASSY.step")); r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
T = {GeomAbs_Torus: "torus", GeomAbs_Cylinder: "cyl", GeomAbs_Cone: "cone", GeomAbs_Plane: "plane", GeomAbs_BSplineSurface: "bspline", GeomAbs_Sphere: "sphere"}
seen = set(); out = []
def walk(L, depth=0):
    n = TDataStd_Name(); nm = n.Get().ToExtString() if L.FindAttribute(TDataStd_Name.GetID_s(), n) else "?"
    if st.IsAssembly_s(L) or st.IsReference_s(L):
        ref = L
        if st.IsReference_s(L):
            from OCP.TDF import TDF_Label
            R = TDF_Label(); st.GetReferredShape_s(L, R); ref = R
            n2 = TDataStd_Name(); nm2 = n2.Get().ToExtString() if ref.FindAttribute(TDataStd_Name.GetID_s(), n2) else nm
            if not st.IsAssembly_s(ref):
                if nm2 not in seen:
                    seen.add(nm2); s = cq.Shape.cast(st.GetShape_s(ref)); out.append((nm2, s))
                return
        it = TDF_ChildIterator(ref)
        while it.More(): walk(it.Value(), depth + 1); it.Next()
labs = TDF_LabelSequence(); st.GetFreeShapes(labs)
for i in range(1, labs.Length() + 1): walk(labs.Value(i))
for nm, s in out:
    c = collections.Counter(); rads = collections.Counter()
    for f in s.Faces():
        a = BRepAdaptor_Surface(f.wrapped); t = T.get(a.GetType(), str(a.GetType())); c[t] += 1
        if t == "torus": rads[("tor", round(a.Torus().MinorRadius(), 2))] += 1
    bb = s.BoundingBox()
    print(nm[:60], round(s.Volume()), (round(bb.xlen), round(bb.ylen), round(bb.zlen)), dict(c), dict(rads.most_common(5)))
if len(sys.argv) > 1:
    for nm, s in out:
        if sys.argv[1] in nm: cq.exporters.export(cq.Workplane().add(s), "_ref_part.stl", tolerance=0.02, angularTolerance=0.1); print("exported", nm)

import numpy as np
def sphere_fit(P):
    A = np.c_[2 * P, np.ones(len(P))]; b = (P ** 2).sum(1); x = np.linalg.lstsq(A, b, rcond=None)[0]
    c = x[:3]; return c, np.sqrt(x[3] + c @ c)
for nm, s in out:
    if "LINK" in nm or "CLAMP" in nm or "SLEEVE" in nm or "PTFE" in nm or "IGUS" in nm:
        vs, _ = s.tessellate(0.2); P = np.array([[v.x, v.y, v.z] for v in vs])
        c, R = sphere_fit(P); d = np.linalg.norm(P - c, axis=1)
        print(f"{nm[:40]:40s} fitR {R:7.1f} radial span {d.min():6.1f}..{d.max():6.1f} (t={d.max()-d.min():.2f})", "bbox", [round(x,1) for x in (s.BoundingBox().xlen, s.BoundingBox().ylen, s.BoundingBox().zlen)])
print("---- plate thickness estimates (2V/A) and planar faces")
from OCP.BRepAdaptor import BRepAdaptor_Surface
for nm, s in out:
    if "LINK" in nm:
        pl = []
        for f in s.Faces():
            a = BRepAdaptor_Surface(f.wrapped)
            if a.GetType() == GeomAbs_Plane:
                n = a.Plane().Axis().Direction(); o = a.Plane().Location(); pl.append(((round(n.X(),3), round(n.Y(),3), round(n.Z(),3)), round(o.X()*n.X()+o.Y()*n.Y()+o.Z()*n.Z(), 2), round(f.Area(),1)))
        print(nm, "2V/A", round(2 * s.Volume() / s.Area(), 2)); [print("   ", p) for p in sorted(pl, key=lambda t: -t[2])[:10]]
