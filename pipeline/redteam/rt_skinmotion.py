"""Where can a THORAX-fixed base sit? Skin motion relative to the thorax over the clips (the rig's girdle: scapula-
weighted skin rotates with scap(elev), the trunk is translated by -lift; adding lift back gives the thorax frame).
Per trunk skin vertex near the shoulder: max displacement and max outward-normal rise vs rest, over every STEP-th wanted
pose. Also the skin under the reference base's footprint (base vertices at rest, canonical scapula frame = thorax at rest).
    python3 rt_skinmotion.py [STEP=6] -> results/skinmotion.json
"""
import json, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
import rt_common as RC
from rt_common import BP, GD
from common import load_parts

STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 6; t0 = time.time()
R = RC.skin_regions(); reg, dom = R["region"], R["dom"]; V0 = BP._rig().V0; F = BP.F
N0 = np.zeros_like(V0); fn = np.cross(V0[F[:, 1]] - V0[F[:, 0]], V0[F[:, 2]] - V0[F[:, 0]])
for k in range(3): np.add.at(N0, F[:, k], fn)
N0 /= np.linalg.norm(N0, axis=1, keepdims=True) + 1e-12
near = np.flatnonzero((dom <= 1) & (np.linalg.norm(V0, axis=1) < 260))
FR = RC.clips(); L = json.load(open(os.path.join(RC.REPO, "pipeline", "avg", "body_mesh.json"))); LM, S = L["landmarks"], L["scale"]
dmax = np.zeros(len(near)); rise = np.zeros(len(near)); rise_el = np.zeros(len(near))
for k in range(0, len(FR), STEP):
    w = FR[k][2]; pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], w)); V = BP.posed(pose); lift = BP.segs(LM, S, pose)[1]
    D = V[near] + lift - V0[near]; dn = (D * N0[near]).sum(1); dd = np.linalg.norm(D, axis=1)
    dmax = np.maximum(dmax, dd); upd = dn > rise; rise[upd] = dn[upd]; rise_el[upd] = w[1]
print("frames done", f"{time.time() - t0:.0f}s", flush=True)
# base footprint: skin vertices within 20 mm of the base part at rest
parts = load_parts(RC.DD); C0 = FR[0]; G0 = BP.scap(C0[3][1]).T @ np.array(C0[5]["base"]).reshape(3, 3)
B = np.concatenate([P for g, n, P, _ in parts if g == "base" and n.startswith("D4-01")]) @ G0.T
d, j = cKDTree(B).query(V0[near]); foot = d < 20
out = dict(step=STEP, vertices=len(near))
out["base_footprint"] = dict(skin_vertices=int(foot.sum()), max_disp_mm=round(float(dmax[foot].max()), 1), max_rise_mm=round(float(rise[foot].max()), 1),
                             regions={r_: int(c) for r_, c in zip(*np.unique(reg[near][foot], return_counts=True))},
                             worst_vertex_rest_mm=[round(float(v)) for v in V0[near][foot][np.argmax(rise[foot])]], rise_at_elev=float(rise_el[foot][np.argmax(rise[foot])]),
                             base_extent_rest_mm=dict(min=B.min(0).round().tolist(), max=B.max(0).round().tolist()))
byreg = {}
for r_ in np.unique(reg[near]):
    m = reg[near] == r_
    byreg[str(r_)] = dict(n=int(m.sum()), share_disp_lt_3mm=round(float((dmax[m] < 3).mean()), 3), max_disp=round(float(dmax[m].max()), 1), max_rise=round(float(rise[m].max()), 1))
out["by_region"] = byreg
# quiet zone on the back / top: how far medial (z) and down (y) must a footprint go for the skin to move < 3 / < 5 mm?
Vn = V0[near]; back = Vn[:, 0] < 10                                   # posterior / top half (x < 10 mm)
qz = {}
for thr in (3.0, 5.0):
    moving = back & (dmax >= thr)
    qz[f"lt_{thr:.0f}mm"] = dict(moving_skin_extent_rest_mm=dict(z_min=round(float(Vn[moving, 2].min())), y_min=round(float(Vn[moving, 1].min())), y_max=round(float(Vn[moving, 1].max()))) if moving.any() else None)
out["back_quiet_zone"] = qz
# grid summary for the designers: max skin displacement in 20 mm cells of (z, y) on the back half
cells = {}
for zc in range(-200, 81, 20):
    for yc in range(-160, 121, 20):
        m = back & (np.abs(Vn[:, 2] - zc) < 10) & (np.abs(Vn[:, 1] - yc) < 10)
        if m.sum() >= 3: cells[f"z{zc},y{yc}"] = round(float(dmax[m].max()), 1)
out["back_disp_grid_mm"] = cells
np.savez_compressed(os.path.join(RC.OUT, "skinmotion.npz"), near=near, dmax=dmax, rise=rise, rise_el=rise_el)
RC.jdump(out, "skinmotion.json"); print(json.dumps({k: v for k, v in out.items() if k != "back_disp_grid_mm"}, indent=1)[:3000], f"\n{time.time() - t0:.0f}s")
