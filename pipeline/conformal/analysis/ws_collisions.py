"""Which part pairs does the evaluator find colliding over the FUNCTIONAL WORKSPACE poses? (its envelope 'part_collision'
loss). Collisions need no skin maps: the DETAIL result's fitted shape is imposed on a CPU Band (clip payload, maps_s1),
then the evaluator's own collisions() (hooked per pair, why_held.py) runs on the workspace poses of the payload the
DETAIL eval used (band_poses_wsf.b64). Optional JN_LOW=link: the same with link N-1 under the arm hub (jn_low key).
    python3 ws_collisions.py <band_eval DETAIL json> [index]       env: CFG / CFG_I (geometry), HUB_RELIEF, JN_LOW
"""
import base64, gzip, io, json, math, os, sys
from collections import Counter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("FIT", "wsf")
import why_held as WH, torch
CONF = WH.CONF; src = sys.argv[1]; idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
R = json.load(open(src))["results"][idx]; BI = WH.hooked_band_impl()
cfg = json.load(open(os.path.join(CONF, "gpu_client", os.environ.get("CFG", "r18_cfgs.json"))))[int(os.environ.get("CFG_I", 1))]
geo = {k: cfg[k] for k in ("hub_r", "hub_relief", "hub_margin", "stack", "t_w", "t_link", "neck", "b_ant_max", "mount_dir", "t_lo", "hub_up", "cap_up", "rail_d", "min_arc", "min_arm_mm", "G", "ramp_deg", "hw") if k in cfg}
for k in ("hub_r", "stack", "t_link", "ramp_deg", "hw"):
    if R.get(k) is not None: geo[k] = R[k]
if os.environ.get("HUB_RELIEF"): geo["hub_relief"] = float(os.environ["HUB_RELIEF"])
for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
    if g.lower() in geo: setattr(BI, g, float(geo[g.lower()]))
jl = os.environ.get("JN_LOW", R.get("jn_low") or "arm")
B = BI.Band(dict(geo, mode="band_eval", poses=open(os.path.join(CONF, "band_poses.b64")).read(), maps_cache=os.path.join(WH.REPO, ".cache", "maps_s1.pt"),
                 q_step=12, fit_clips=R.get("fit_clips"), jn_low=jl), torch.device("cpu"))
h_w = torch.tensor(R["h"], dtype=torch.float32); bu_w = torch.tensor(R["bot_under"], dtype=torch.float32)
faces_w = {int(k) if k.isdigit() else k: float(v) for k, v in R["faces"].items()}; orig = B.fit_shape
def fit_fixed(*a, **kw):
    h, S, sc, zj4 = orig(*a, **kw); ff = dict(B._faces_full); ff.update({k: torch.tensor(v) for k, v in faces_w.items()}); ff["bot_under"] = bu_w
    B._faces_full = ff; B._bot_under = bu_w; B._faces = dict(faces_w); return h_w.clone(), S, sc, faces_w["zj4"]
B.fit_shape = fit_fixed
d = {k: R[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm") if k in R}; d["zj4_fixed"] = faces_w["zj4"]; d["jn_low"] = jl
B.evaluate(dict(d))
# workspace poses of the DETAIL payload
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, R.get("poses_file", "band_poses_wsf.b64"))).read()))))
NAMES = [str(x) for x in Z["NAMES"]]; ENV = set(str(x) for x in Z["ENVELOPE"]); env_ids = [k for k, n in enumerate(NAMES) if n in ENV]
wsel = np.nonzero(np.isin(Z["CID"], env_ids))[0]; HG = torch.tensor(Z["HG"][wsel], dtype=torch.float32)
P_, C_ = R["PC"]; FEAS = np.unpackbits(np.frombuffer(base64.b64decode(R["feas_all"]), np.uint8))[:P_ * C_].reshape(P_, C_).astype(bool)[:, 0]
N = d["n"]; A = [x * math.pi / 180 for x in d["a"]]; order = d.get("order", [1] * N)
FP = [B.footprint(0.0, hubs=(False, True), ribbon=False)] + [B.footprint(A[k], (True, True)) for k in range(N - 1)]
offs = np.r_[0, np.cumsum([fp["dirs"].shape[0] for fp in FP])]; lower = {J: (J - 1 if order[J - 1] == 1 else J) for J in range(1, N)}
COLD = []; VAL = []
for c0 in range(0, len(HG), 48):
    hg = HG[c0:c0 + 48]; pins, ok, Q = B.chain(d, hg); VAL.append(ok[:, 0]); cold = []
    for mi, fp in enumerate(FP):
        if mi == 0: a_ = pins[:, :, 0]; ref = pins[:, :, 1]
        else: a_ = pins[:, :, mi - 1]; ref = pins[:, :, mi]
        n_ = B._unit(ref - (a_ * ref).sum(-1, keepdim=True) * a_); Fm = torch.stack([a_, n_, torch.cross(a_, n_, dim=-1)], -1)
        cold.append(torch.einsum("pcij,mj->pcmi", Fm, fp["dirs"])[:, :, fp["col"]].half())
    COLD.append(dict(w=cold, hg=hg))
VAL = torch.cat(VAL).numpy()
hit = B.collisions(COLD, FP, h_w, offs, N, lower, Q, d)[:, 0].numpy()
pairs = {k: torch.cat(v, 0)[:, 0].numpy() for k, v in B._pair_hits.items()}
nm = lambda s: s.replace("m0", "base").replace("m1", "link 1").replace("m2", "link 2").replace("m3", "link 3")
fe = FEAS[wsel]; n = len(wsel)
print(f"{os.path.basename(src)} #{idx} ({R.get('_src', '')[:50]}), jn_low {jl}: {n} workspace poses, chain valid {VAL.mean():.3f}, GPU-feasible {fe.mean():.3f}")
print(f"  evaluator collisions (imposed shape) in {100 * (hit & VAL).mean():.1f} % of the poses (valid chain); per pair:")
for k, v in sorted(pairs.items(), key=lambda kv: -(kv[1] & VAL).sum()):
    if (v & VAL).any(): print(f"    {nm(k):22s} {100 * (v & VAL).mean():5.1f} %   only this pair: {100 * (v & VAL & (sum(vv for kk, vv in pairs.items() if kk != k) == 0)).mean():5.1f} %")
json.dump(dict(src=src, idx=idx, jn_low=jl, n=n, valid=float(VAL.mean()), collide=float((hit & VAL).mean()),
               pairs={nm(k): float((v & VAL).mean()) for k, v in pairs.items()}), open(os.path.join(HERE, f"ws_collisions_{os.path.basename(src)[:-5]}_{idx}_{jl}.json"), "w"), indent=1)
