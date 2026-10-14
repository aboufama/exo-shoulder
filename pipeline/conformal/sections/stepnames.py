"""load a STEP with part names (XCAF): [(name, cq.Shape)]"""
import cadquery as cq
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDF import TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
def load(path):
    doc = TDocStd_Document(TCollection_ExtendedString("doc")); rd = STEPCAFControl_Reader(); rd.SetNameMode(True)
    rd.ReadFile(path); rd.Transfer(doc); st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    out = []
    def name_of(lab):
        a = TDataStd_Name()
        return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else "?"
    def walk(lab, loc):
        if st.IsAssembly_s(lab):
            seq = TDF_LabelSequence(); st.GetComponents_s(lab, seq)
            for i in range(1, seq.Length() + 1):
                c = seq.Value(i); ref = c
                from OCP.TDF import TDF_Label
                r = TDF_Label()
                if st.GetReferredShape_s(c, r): ref = r
                l2 = loc.Multiplied(st.GetLocation_s(c)); 
                if st.IsAssembly_s(ref): walk(ref, l2)
                else: out.append((name_of(c) if name_of(c) != "?" else name_of(ref), cq.Shape.cast(st.GetShape_s(ref).Moved(l2))))
        else: out.append((name_of(lab), cq.Shape.cast(st.GetShape_s(lab).Moved(loc))))
    roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1): walk(roots.Value(i), TopLoc_Location())
    return out
if __name__ == "__main__":
    import sys
    for n, s in load(sys.argv[1])[:80]: print(n, round(s.Volume(), 1))
