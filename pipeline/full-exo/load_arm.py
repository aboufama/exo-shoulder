import os
"""Located, named solids of the user's RIGHT ARM SUBASSY.step (read-only)."""
import cadquery as cq, numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_ChildIterator, TDF_Label
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
SRC = os.environ.get("USER_CAD", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "user_cad", "RIGHT ARM SUBASSY.step"))   # the user's CAD (source of truth, read-only)
def load(path=SRC):
    doc = TDocStd_Document(TCollection_ExtendedString("d")); r = STEPCAFControl_Reader(); r.SetNameMode(True)
    r.ReadFile(path); r.Transfer(doc); st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    nm = lambda L: (lambda n: n.Get().ToExtString() if L.FindAttribute(TDataStd_Name.GetID_s(), n) else "?")(TDataStd_Name())
    out = []
    def walk(L, loc):
        if st.IsReference_s(L):
            R = TDF_Label(); st.GetReferredShape_s(L, R); loc = loc.Multiplied(st.GetLocation_s(L)); return walk_ref(R, loc, nm(L))
        it = TDF_ChildIterator(L)
        while it.More(): walk(it.Value(), loc); it.Next()
    def walk_ref(R, loc, inst):
        if st.IsAssembly_s(R):
            it = TDF_ChildIterator(R)
            while it.More(): walk(it.Value(), loc); it.Next()
        else:
            s = cq.Shape.cast(st.GetShape_s(R).Moved(loc)); out.append((nm(R), inst, s))
    labs = TDF_LabelSequence(); st.GetFreeShapes(labs)
    for i in range(1, labs.Length() + 1):
        L = labs.Value(i)
        if st.IsAssembly_s(L):
            it = TDF_ChildIterator(L)
            while it.More(): walk(it.Value(), TopLoc_Location()); it.Next()
        else: out.append((nm(L), nm(L), cq.Shape.cast(st.GetShape_s(L))))
    return out
if __name__ == "__main__":
    for name, inst, s in load():
        if s.Volume() < 50: continue
        bb = s.BoundingBox(); c = bb.center
        print(f"{name[:48]:48s} vol {s.Volume():8.0f} centre ({c.x:7.1f},{c.y:7.1f},{c.z:7.1f}) size ({bb.xlen:5.1f},{bb.ylen:5.1f},{bb.zlen:5.1f})")
