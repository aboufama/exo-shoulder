"""Red team for virtual-pole-4bar-j2 / -j1 (lessons a-e): the FROZEN shape (fitted on Bench(60,160)) worn on a bench,
then: why each pose is not taken (jam poses), the closest metal per member (pinch point), the gap with < 1 mm counted
as contact (near-touch), overhead (elev >= 140) separately, and the mobility rank (3 x 3 Jacobian of the arm rotation
w.r.t. the three driven coordinates) at every taken pose.

    CB_EXACT=1 OMP_NUM_THREADS=1 python3 docs/concepts/verify/virtual-pole-4bar.py <model.py> '<params json>' [--big 110,360] --out out.json
"""
import argparse, functools, importlib.util, json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                       # noqa: E402
import concept_bench as CB                                                    # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("params"); ap.add_argument("--big", default="")
ap.add_argument("--out", required=True); a = ap.parse_args()
spec = importlib.util.spec_from_file_location("concept_model", os.path.abspath(a.model)); m = importlib.util.module_from_spec(spec)
sys.modules["concept_model"] = m; spec.loader.exec_module(m)
core = getattr(m, "_core", m); p = dict(m.PARAMS, **json.loads(a.params)); out = dict(params=p, exact=os.environ.get("CB_EXACT") == "1")
coll = K.collisions; K.collisions = functools.partial(coll, overlap=1.0 - 1e-4)          # 1 mm radial part clearance (verifier)
Bf = K.bench(60, 160); rf = K.evaluate(Bf, m.build, p); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
out["fit"] = {k: rf.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "inband_member")}
B = Bf
if a.big:
    B = K.bench(*map(int, a.big.split(","))); fp = K.fit_profiles
    K.fit_profiles = lambda B_, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try: r = K.evaluate(B, m.build, p)
    finally: K.fit_profiles = fp
else:
    r = rf
L = B._kit_last; ch = L["chain"]; ok, hit, take = L["ok"], L["hit"], L["take"]
out["bench"] = dict(n=len(B.idx), **{k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "inband_member")})
F = B._kitF; raw = ch.ok
# why not taken
why = np.array([""] * len(ok), dtype=object)
why[~raw] = "closure (transmission / crossing / no root)"; why[raw & ~ok] = "K2 flip / pass through a limit along the motion"
why[ok & hit] = "part-part collision"
res = B.res; con = np.array([res[i] is not None and float(np.min(res[i])) < 0 for i in range(len(ok))])
why[take & con] = "skin contact"
el = np.array([B.poses[i]["elev"] for i in range(len(ok))]); pl = np.array([B.poses[i]["plane"] for i in range(len(ok))])
kinds = np.array(B.kind); out["why"] = {w: int((why == w).sum()) for w in set(why) if w}
out["why_ws"] = {w: int(((why == w) & (kinds == "ws")).sum()) for w in set(why) if w}
lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:20]} plane {pl[i]:.0f} elev {el[i]:.0f} axial {B.poses[i]['axial']:.0f}"
out["jam_examples"] = [f"{why[i]}: {lab(i)}" for i in np.nonzero(why != "")[0][:12]]
# pinch: closest metal per member over the taken, non-contact poses
names = [mm.name for mm in ch.members]; sizes = [L["pts"][n].shape[1] for n in names]; cut = np.cumsum([0] + sizes)
good = [i for i in range(len(ok)) if res[i] is not None and float(np.min(res[i])) >= 0]
low = []
for i in good:
    d = res[i]; j = int(np.argmin(d)); low.append((float(d[j]), i, names[int(np.searchsorted(cut, j, side="right") - 1)]))
low.sort(); out["pinch"] = [f"{dd:.2f} mm {nm} {lab(i)}" for dd, i, nm in low[:8]]
out["min_metal_skin_mm"] = round(low[0][0], 2) if low else None
# near-touch: < 1 mm counted as contact
B2 = B; saved = list(B2.res)
for i in good:
    if float(np.min(saved[i])) < 1.0: B2.res[i] = saved[i] - 1.0
r1 = B2.report(); B2.res = saved; out["near_touch_gap"] = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
out["near_touch_poses"] = int(sum(float(np.min(saved[i])) < 1.0 for i in good))
# overhead
ov = np.nonzero(el >= 140)[0]; tk = [i for i in ov if i in set(good)]
dd = np.concatenate([res[i] for i in tk]) if tk else np.array([np.nan])
out["overhead"] = dict(total=int(len(ov)), taken=len(tk), inband14=round(float(((dd >= 2) & (dd <= 14)).mean()), 3) if tk else None,
                       why={w: int((why[ov] == w).sum()) for w in set(why[ov]) if w})
# mobility rank at the taken poses (3 x 3 Jacobian of the arm rotation w.r.t. the driven coordinates, from the chain axes)
J = ch.joints; at = int(p["at"])
if at == 2:     # arm rotation rate = w1 * J1 + w_theta * (coupler instant pole) + w3 * J3; pole = crossing of crank planes
    pole = K.unit(np.cross(np.cross(J["A0"], J["A1"]), np.cross(J["B0"], J["B1"]))); ax = [J["J1"], pole, J["J3"]]
else:
    pole = K.unit(np.cross(np.cross(J["A0"], J["A1"]), np.cross(J["B0"], J["B1"]))); ax = [pole, J["J2"], J["J3"]]
M = np.stack(ax, -1); sv = np.linalg.svd(M[take], compute_uv=False) if take.any() else np.ones((1, 3))
out["rank"] = dict(min_ratio=round(float((sv[:, 2] / sv[:, 0]).min()), 4), p5=round(float(np.percentile(sv[:, 2] / sv[:, 0], 5)), 4),
                   rank3=int((sv[:, 2] / sv[:, 0] > 1e-3).sum()), taken=int(take.sum()),
                   note="columns = the three instantaneous rotation axes of the chain (J1 or the four-bar pole, the pole or J2, J3); rank 3 = mobility exactly 3 at that pose")
# pole travel: how far the virtual pole walks from its home ray (in the body that carries the ground pins)
out["pole_angle_to_home_axis_deg"] = None
json.dump(out, open(a.out, "w"), indent=1, default=float); print(json.dumps(out, indent=1, default=float)[:6000])
