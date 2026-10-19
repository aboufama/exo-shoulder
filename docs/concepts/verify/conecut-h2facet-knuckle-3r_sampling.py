import importlib.util, json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"
os.environ.pop("CB_EXACT", None)
sp = importlib.util.spec_from_file_location("h2f_i", os.path.join(REPO, "docs/concepts/models/conecut-h2facet-knuckle-3r.py")); H2 = importlib.util.module_from_spec(sp); sp.loader.exec_module(H2)
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-h2facet-knuckle-3r.json")))
P = H2._clamp(dict(H2.PARAMS, **row["best_params"]))
B = H2.CB.Bench(n_clip=60, n_ws=160)
out = {}
Ms = {}
for nm, extra in (("cut", {}), ("nocut", dict(c=0.0, fd=0.0, dense=0))):
    p = H2._clamp(dict(P, **extra)); M = H2.CC.CCModel(B, dict(p)); M.run(); Ms[nm] = M
M = Ms["cut"]; M0 = Ms["nocut"]
mem2, cen2, ax2 = M.cyl["hub2"]; u, e, f = H2.frame(ax2)
out["mem2"] = mem2
out["rigid_keys"] = {k: (int(m), len(X)) for k, (m, X) in M.rigid.items()}
out["link_pts"] = {k: (int(v[0]), len(v[1])) for k, v in getattr(M, "link_pts", {}).items()}
out["contact_groups_cut"] = [(int(m), len(X)) for m, X in M.contact]
out["contact_groups_nocut"] = [(int(m), len(X)) for m, X in M0.contact]
# azimuth of link 1b (same member) samples near hub 2 in the hub-2 frame
for L in ("L1b", "L2"):
    if L in M.link_pts:
        m, X = M.link_pts[L][0], M.link_pts[L][1]
        if m == mem2:
            r, az, z = H2.to_cyl(X, cen2, u, e, f); sel = (r > 8) & (r < 16)
            out[L + "_near_hub2"] = dict(n=int(sel.sum()), az=[round(float(np.percentile(az[sel], q)), 1) for q in (0, 5, 50, 95, 100)] if sel.any() else None,
                                         z=[round(float(z[sel].min()), 2), round(float(z[sel].max()), 2)] if sel.any() else None, r=[round(float(r[sel].min()),2), round(float(r[sel].max()),2)] if sel.any() else None)
            # az histogram 10-deg bins
            if sel.any():
                h, b = np.histogram(az[sel], bins=36, range=(0, 360)); out[L + "_az_hist"] = {int(b[i]): int(h[i]) for i in range(36) if h[i]}
        else:
            out[L + "_member"] = int(m)
# samples on member 7 other than hub2 that the cut removed: compare contact groups element-wise
diff = []
for (m0, X0), (m1, X1) in zip(M0.contact, M.contact):
    if len(X0) != len(X1): diff.append((int(m0), len(X0), len(X1)))
out["contact_group_len_changes"] = diff
# which removed points lie outside the hub's own ring samples: classify removed points by where they came from
def setkey(X): return set(map(tuple, np.round(X, 4)))
rem_all = []
for gi, ((m0, X0), (m1, X1)) in enumerate(zip(M0.contact, M.contact)):
    if m0 != mem2: continue
    s1 = setkey(X1); rm = np.array([tuple(np.round(x, 4)) not in s1 for x in X0])
    if rm.any():
        r, az, z = H2.to_cyl(X0[rm], cen2, u, e, f)
        rem_all.append(dict(group=gi, n=int(rm.sum()), of=len(X0), r=[round(float(r.min()),2), round(float(r.max()),2)], z=[round(float(z.min()),2), round(float(z.max()),2)], az=[round(float(az.min()),1), round(float(az.max()),1)]))
out["removed_by_group"] = rem_all
# group identity: which group index corresponds to which ring (z values)
gz = []
for gi, (m0, X0) in enumerate(M0.contact):
    if m0 == mem2 and len(X0):
        r, az, z = H2.to_cyl(X0, cen2, u, e, f); gz.append((gi, len(X0), round(float(np.median(r)),2), round(float(z.min()),2), round(float(z.max()),2)))
out["mem7_contact_groups"] = gz
# rigid L1b on member 7 near the chamfer
for k, (m, X) in M.rigid.items():
    if m == mem2 and k != "hub2" and len(X):
        r, az, z = H2.to_cyl(X, cen2, u, e, f); sel = (r < 12.5) & (z < 2) & (np.abs(H2.wrapd(az - 142.8)) < 46)
        out["rigid_" + k + "_in_chamfer_zone"] = int(sel.sum())
out["facet_info"] = M._facet_info
# member transform: rotation of link 2 relative to link 1b about u2 over the bench poses (J2 relative angle spread)
try:
    angs = []
    for i in range(len(B.idx)):
        if not bool(M.kin_ok[i]): continue
        R7, _ = M.T(7, i); R2, _ = M.T(2, i); Rr = R7.T @ R2
        # angle about u (member-7 local axis u)
        v = Rr @ e; a = np.degrees(np.arctan2(v @ f, v @ e)); angs.append(a)
    angs = np.array(angs); out["q2_rel_deg"] = dict(n=len(angs), min=round(float(angs.min()),1), max=round(float(angs.max()),1), p5=round(float(np.percentile(angs,5)),1), p95=round(float(np.percentile(angs,95)),1))
except Exception as ex:
    out["q2_rel_err"] = repr(ex)[:200]
print(json.dumps(out, indent=1, default=float))
