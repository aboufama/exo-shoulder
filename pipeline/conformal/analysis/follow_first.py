"""Follow first vs in-band first: what does following every fit-clip frame the chain can reach cost in proximity?
The evaluator's shape fit drops the frames that push the shape up the most while that raises its score (in-band share
x follow); a wide band G makes in-band nearly free, so the fit keeps every frame it can (follow first). On CPU (clip
frames, .cache/maps_s1.pt; no workspace poses), for one design: the shape fitted at G (default 14) vs at a wide G_FIT,
both then scored at G: follow per clip, in-band, and what still blocks (why_held.py categories).
    python3 follow_first.py <key> [G_FIT ...]      (THREADS=2)"""
import json, math, os, sys
from collections import Counter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import why_held as WH, torch
key = sys.argv[1]; GF = [float(x) for x in sys.argv[2:]] or [30.0]; CONF = WH.CONF
R = json.load(open(os.path.join(CONF, "band_cad", "inputs", f"{key}.json")))["results"][0]
BI = WH.hooked_band_impl()
cfg = json.load(open(os.path.join(CONF, "gpu_client", os.environ.get("CFG", "r18_cfgs.json"))))[int(os.environ.get("CFG_I", 1))]
geo = {k: cfg[k] for k in ("hub_r", "hub_relief", "hub_margin", "stack", "t_w", "t_link", "neck", "b_ant_max", "mount_dir", "t_lo", "hub_up", "cap_up", "rail_d", "min_arc", "min_arm_mm", "G", "ramp_deg", "hw") if k in cfg}
for k in ("hub_r", "stack", "t_link", "ramp_deg", "hw"):
    if R.get(k) is not None: geo[k] = R[k]
for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
    if g.lower() in geo: setattr(BI, g, float(geo[g.lower()]))
G0 = float(os.environ.get("G", geo.get("G", 14.0))); poses = open(os.path.join(CONF, "band_poses.b64")).read()
d0 = {k: R[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm") if k in R}
def band(G, **kw): return BI.Band(dict(geo, mode="band_eval", poses=poses, maps_cache=os.path.join(WH.REPO, ".cache", "maps_s1.pt"), q_step=12, fit_clips=R.get("fit_clips"), G=G, **kw), torch.device("cpu"))
def run(G_fit):
    B = band(G_fit); r = B.evaluate(dict(d0)); S = next(x for x in B._iters if x["it"] == B._best_it)
    h = S["h"].clone(); ff = S["faces_full"]; faces = dict(B._faces); bu = B._bot_under.clone()
    B2 = band(G0); orig = B2.fit_shape                                                # the same shape scored at G0
    def fit_fixed(*a, **kw):
        h_, S_, sc, zj4 = orig(*a, **kw); f2 = dict(B2._faces_full); f2.update({k: (v if isinstance(v, list) or hasattr(v, "shape") else torch.tensor(v)) for k, v in ff.items() if k not in ("bot_under", "rail_under") and v is not None})
        f2["bot_under"] = bu; B2._faces_full = f2; B2._bot_under = bu; B2._faces = dict(faces); return h.clone(), S_, sc, faces["zj4"]
    B2.fit_shape = fit_fixed; d = dict(d0, zj4_fixed=faces["zj4"]); r2 = B2.evaluate(d)
    return r, r2, faces
out = []
for G_fit in [G0] + GF:
    r, r2, faces = run(G_fit)
    clips = {k: round(v["follow"], 3) for k, v in r2["clips"].items()}
    print(f"shape fitted at G {G_fit:g}: faces {({k: round(v, 1) for k, v in faces.items()})}\n   scored at G {G0:g}: score {r2['score']:.3f} follow {r2['follow']:.3f} (fit clips {r2.get('follow_fit', 0):.3f}) in-band {r2['in_band']:.3f}  clips {clips}", flush=True)
    out.append(dict(G_fit=G_fit, G=G0, faces=faces, score=r2["score"], follow=r2["follow"], follow_fit=r2.get("follow_fit"), in_band=r2["in_band"], clips=clips))
json.dump(out, open(os.path.join(HERE, f"follow_first_{key}.json"), "w"), indent=1)
