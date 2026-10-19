"""audit: which member pairs make the part-part losses of deltoid-crest-j3-3r's 26.78 config (Bench(60,160) fast)"""
import importlib.util, json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("dcm", os.path.join(REPO, "docs/concepts/models/deltoid-crest-j3-3r.py"))
M = importlib.util.module_from_spec(spec); sys.modules["dcm"] = M; spec.loader.exec_module(M)
K = M.K
P = json.loads(sys.argv[1]); nb = sys.argv[2] if len(sys.argv) > 2 else "60,160"
nc, nw = (int(x) for x in nb.split(","))
B = K.bench(nc, nw)
p, r = M.evaluate(B, P)
print("gap", r["gap"], "reach", r["reach"], "follow", r["follow"], "ib14", r["inband14"], "contact", r["contact"], flush=True)
L = B._kit_last; ch, ok, hit, pts = L["chain"], L["ok"], L["hit"], L["pts"]
Mm = ch.members; Pi = np.nonzero(hit)[0]
print("part-part poses", len(Pi), "of", len(hit), flush=True)
nr = {m.name: np.linalg.norm(pts[m.name], axis=-1) for m in Mm}; dr = {m.name: pts[m.name] / nr[m.name][..., None] for m in Mm}
cnt = {}; per = {}
for a in range(len(Mm)):
    for b in range(a + 1, len(Mm)):
        A, Bm = Mm[a], Mm[b]; shared = set(A.joints) & set(Bm.joints)
        res = K._near(A, Bm, dr[A.name][Pi], dr[Bm.name][Pi], nr[A.name][Pi], nr[Bm.name][Pi], ch.joints, shared, Pi, 1.0)
        if res is None: continue
        k, nm = res; xa, xb = nr[A.name][Pi][k], nr[Bm.name][Pi][k]
        ov = (xa[:, :, None] < xb[:, None, :] + Bm.t + 0.5) & (xb[:, None, :] < xa[:, :, None] + A.t + 0.5)
        h = (nm & ov).any((1, 2))
        for j in Pi[k][h]:
            cnt[(A.name, Bm.name)] = cnt.get((A.name, Bm.name), 0) + 1; per.setdefault(int(j), []).append(f"{A.name}-{Bm.name}")
print("pairs", {f"{a}-{b}": n for (a, b), n in sorted(cnt.items(), key=lambda x: -x[1])})
for j, v in sorted(per.items()):
    q = B.poses[j]; print(j, B.kind[j], [round(float(q[k]), 1) for k in ("plane", "elev", "axial")], v)
