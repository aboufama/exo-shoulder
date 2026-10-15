"""Which way may the base's mounting tab (J1 hub -> the user's scapula handler) point without the skin entering it over
the clip frames? For a band design (CAD input band_cad/inputs/<key>.json), the evaluator on CPU (why_held.py's hooked
band_impl, the DETAIL result's own shape imposed), the tab's aux samples for mount directions all round the J1 axis:
per direction the worst skin intrusion (mm above the tab's fitted underside) and the clip frames it blocks.
The deployed default mount_dir [0, 0.6, -0.8] (scapula frame) is the reference.
    python3 tab_dirs.py <key>"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("FIT", "wsf")
import why_held as WH, torch
key = sys.argv[1]; CONF = WH.CONF
R = json.load(open(os.path.join(CONF, "band_cad", "inputs", f"{key}.json")))["results"][0]
import band_impl as BI0
b = np.array(BI0.bvec(R["az"], R["el"])); e1 = np.cross(b, [0, 1.0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(b, e1)
ref = np.array([0.0, 0.6, -0.8]); ref = ref - (ref @ b) * b; ref /= np.linalg.norm(ref); a_ref = math.degrees(math.atan2(ref @ e2, ref @ e1))
BI = WH.hooked_band_impl()
cfg = json.load(open(os.path.join(CONF, "gpu_client", "r18_cfgs.json")))[1]
geo = {k: cfg[k] for k in ("hub_r", "hub_relief", "hub_margin", "stack", "t_w", "t_link", "neck", "b_ant_max", "t_lo", "hub_up", "cap_up", "rail_d", "min_arc", "min_arm_mm", "G", "ramp_deg", "hw") if k in cfg}
for k in ("hub_r", "stack", "t_link", "ramp_deg", "hw"):
    if R.get(k) is not None: geo[k] = R[k]
for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
    if g.lower() in geo: setattr(BI, g, float(geo[g.lower()]))
poses = open(os.path.join(CONF, "band_poses.b64")).read(); rows = []
h_w = torch.tensor(R["h"], dtype=torch.float32); bu_w = torch.tensor(R["bot_under"], dtype=torch.float32)
faces_w = {int(k) if k.isdigit() else k: float(v) for k, v in R["faces"].items()}
for da in [None] + list(range(0, 360, 30)):
    md = ref if da is None else math.cos(math.radians(a_ref + da)) * e1 + math.sin(math.radians(a_ref + da)) * e2
    job = dict(geo, mode="band_eval", poses=poses, maps_cache=os.path.join(WH.REPO, ".cache", "maps_s1.pt"), q_step=12, fit_clips=R.get("fit_clips"), mount_dir=[float(x) for x in md])
    B = BI.Band(job, torch.device("cpu")); orig = B.fit_shape
    def fit_fixed(*a, **kw):
        h, S, sc, zj4 = orig(*a, **kw); ff = dict(B._faces_full); ff.update({k: torch.tensor(v) for k, v in faces_w.items()}); ff["bot_under"] = bu_w
        B._faces_full = ff; B._bot_under = bu_w; B._faces = dict(faces_w); return h_w.clone(), S, sc, faces_w["zj4"]
    B.fit_shape = fit_fixed
    d = {k: R[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm") if k in R}; d["zj4_fixed"] = faces_w["zj4"]
    r = B.evaluate(dict(d)); S_ = next(x for x in B._iters if x["it"] == B._best_it)
    tab = [(ax_, u_) for ax_, u_ in zip(B._aux, S_["faces_full"]["aux_under"]) if ax_["name"] == "tab"]
    if not tab: print("no tab (base not the lower member at J1)"); break
    ax_, u_ = tab[0]; dep = (ax_["LO"] - u_[None]).clamp(min=0).max(1).values.numpy()
    blocked = int((dep > 1e-3).sum()); worst = float(dep.max())
    lab = "default [0, 0.6, -0.8]" if da is None else f"default {da:+4d} deg"
    rows.append(dict(dir=lab, mount_dir=[round(float(x), 3) for x in md], frames_blocked_by_tab=blocked, worst_mm=round(worst, 1), follow=round(r["follow"], 3),
                     clips={k: round(v["follow"], 3) for k, v in r["clips"].items()}))
    print(f"{lab:24s} mount_dir {np.round(md, 2)}: tab blocks {blocked:3d} clip frames, worst {worst:5.1f} mm; follow {r['follow']:.3f}  overhead {r['clips']['Raise overhead']['follow']:.2f}", flush=True)
json.dump(rows, open(os.path.join(HERE, f"tab_dirs_{key}.json"), "w"), indent=1)
