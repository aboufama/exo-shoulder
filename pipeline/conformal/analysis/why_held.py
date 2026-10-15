"""WHY is a frame held / a workspace pose lost? Per clip frame and per functional-workspace pose of a band design (the
CAD input band_cad/inputs/<key>.json = a band_eval DETAIL result), the blocking constraint, from the evaluator's own
constraints recomputed on CPU with hooks (pipeline/conformal/gpu/band_impl.py, exec'd with stash lines; the file itself
is not changed):
  kinematics : the 3R chain does not close (angle J1-J3 outside |a1-a2|..a1+a2) or J2 is within sing_deg of the fold /
               stretch singularity (tri_ok) - shape independent
  skin       : the fitted underside is below the skin (+2 mm) - which member / sample class (ribbon, hub) and how deep
  squeeze    : the member's top is above a re-entry sheet of skin (arm against trunk) - which member
  collision  : which pair (link-link, link-neck, link-tab, link-BOTTOM bar)
  neck       : the arm-fixed neck below the skin
Plus the geometry every pose has: angle J1-J3 vs the closure / singularity limits, and link N-1's azimuth about JN in the
arm frame vs the neck exit (the R16 'link 2 IN BOTTOM + neck' interference).

The CPU maps (.cache/maps_s1.pt) cover the 451 clip frames only (band_poses.b64): the shape is either re-fitted on the
clip frames (FIT=cpu) or, default, the DETAIL result's own fitted shape h / faces is imposed (FIT=wsf, the shape the CAD
was built from, fitted on the clips + 1432 workspace poses); the neck's underside is then re-derived from the kept clip
frames (the result does not store it).

    python3 why_held.py <key> [out.json]       (THREADS=2)
"""
import base64, gzip, io, json, math, os, sys, time
from collections import Counter, defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, ".."); REPO = os.path.join(CONF, "..", "..")
sys.path.insert(0, os.path.join(CONF, "gpu")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import torch
torch.set_num_threads(int(os.environ.get("THREADS", 2)))
D2R = math.pi / 180

# ---------------------------------------------------------------- the evaluator, with stash hooks (source transform)
def hooked_band_impl():
    src = open(os.path.join(CONF, "gpu", "band_impl.py")).read()
    reps = [
        # per-iteration stash of every constraint, after the collision mask is known
        ("            feas &= ~colm\n",
         "            feas &= ~colm\n"
         "            self._iters.append(dict(it=it_, VALID=VALID.clone(), LO=LO, HI=HI, CAP=CAP, hl=hl.clone(), h=h.clone(), colm=colm.clone(), pair_hits=dict(self._pair_hits), faces_full=self._faces_full, memA=memA, kindA=kindA, is_low=is_low, is_bot=is_bot, offs=offs, wS=wS, path=path.clone()))\n"),
        ("        best = None\n        for it_ in range(rng_iters):\n",
         "        best = None; self._iters = []\n        for it_ in range(rng_iters):\n"),
        ("                best = dict(sel=sel, score=score,", "                self._best_it = it_; best = dict(sel=sel, score=score,"),
        # per-pair collision bookkeeping
        ("        t = self.t; R = self.R_REF; out = []; F = self._faces_full\n",
         "        t = self.t; R = self.R_REF; out = []; F = self._faces_full; self._pair_hits = {}\n"
         "        def _rec(key, m):\n"
         "            self._pair_hits.setdefault(key, []).append(m.clone())\n"),
        ("                    over = (ang < (rads[i][:, None] + rads[j][None, :] - 1.0)) & (ivo > 0)[None, None] & ok_pair[None, None]\n                    hit |= over.reshape(Pn, C, -1).any(-1)\n",
         "                    over = (ang < (rads[i][:, None] + rads[j][None, :] - 1.0)) & (ivo > 0)[None, None] & ok_pair[None, None]\n                    hit |= over.reshape(Pn, C, -1).any(-1); _rec(f'm{i}-m{j}', over.reshape(Pn, C, -1).any(-1))\n"),
        ("                    over = (ang < rr) & (ivo > 0)[None, None] & ok_pair[None, None]\n                    hit |= over.reshape(Pn, C, -1).any(-1)\n",
         "                    over = (ang < rr) & (ivo > 0)[None, None] & ok_pair[None, None]\n                    hit |= over.reshape(Pn, C, -1).any(-1); _rec(f'm{i}-' + ax_['name'], over.reshape(Pn, C, -1).any(-1))\n"),
        ("                hit |= over.any(-1)\n            out.append(hit)\n",
         "                hit |= over.any(-1); _rec(f'm{i}-bar', over.any(-1))\n            out.append(hit)\n"),
    ]
    if os.environ.get("JN_LOW") == "link":                                           # proposed evaluator change (jn_flip_patch.py)
        sys.path.insert(0, HERE); import jn_flip_patch as JP; src = JP.patch(src, v2=os.environ.get("JP_V2", "1") == "1")
    for a, b in reps:
        assert src.count(a) == 1, f"band_impl changed: hook anchor not unique / missing:\n{a}"
        src = src.replace(a, b)
    import types
    mod = types.ModuleType("band_impl_hooked"); mod.__file__ = os.path.join(CONF, "gpu", "band_impl.py")
    exec(compile(src, "band_impl_hooked", "exec"), mod.__dict__)
    return mod


def geometry_of(R, POSE):
    """per pose: angle J1-J3 (deg) and link N-1's azimuth about JN in the arm frame (0 = toward the bar), pure kinematics"""
    import design_search as DS
    import band_impl as BI
    b = np.array(BI.bvec(R["az"], R["el"])); W = np.array(BI.w_dir(*R["w"])); A = [x * D2R for x in R["a"]]
    nk = json.load(open(os.path.join(CONF, "gpu_client", "neck_cfg.json")))
    pb = np.array(nk["p_bar"], float); dh = pb - (pb @ W) * W; dh /= np.linalg.norm(dh); lat = np.cross(W, dh)
    out = []
    for pl, el, ax, *_ in POSE:
        H = DS.Ry(pl * D2R) @ DS.Rx(-el * D2R) @ DS.Ry(ax * D2R); Rs = DS.scapula(el); HG = Rs.T @ H
        pz = HG @ W; d = float(np.clip(b @ pz, -1, 1)); th = math.degrees(math.acos(d))
        n_ = np.cross(b, pz); n_ /= np.linalg.norm(n_) + 1e-12; den = 1 - d * d + 1e-12
        a_ = (math.cos(A[0]) - d * math.cos(A[1])) / den; b_ = (math.cos(A[1]) - d * math.cos(A[0])) / den
        p = a_ * b + b_ * pz; h2 = 1 - p @ p
        az = None
        if h2 > -2e-3:
            p2 = p + R["branch"] * math.sqrt(max(h2, 0)) * n_
            v = HG.T @ p2; v = v - (v @ W) * W                                        # J2 seen from JN, arm frame
            az = math.degrees(math.atan2(v @ lat, v @ dh))
        out.append(dict(th=th, az=az))
    return out


def main():
    key = sys.argv[1]; outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, f"why_held_{key}.json")
    if key.endswith(".json"):                                                          # any band_eval DETAIL json: <file>.json[:index]
        INP = json.load(open(key)); R = INP["results"][int(os.environ.get("IDX", 0))]; key = os.path.basename(key)[:-5] + f"_{os.environ.get('IDX', 0)}"
        outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, f"why_held_{key}.json")
    else: INP = json.load(open(os.path.join(CONF, "band_cad", "inputs", f"{key}.json"))); R = INP["results"][0]
    pf = R.get("poses_file", "band_poses_wsf.b64")
    Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, pf)).read()))))
    NAMES = [str(x) for x in Z["NAMES"]]; ENV = set(str(x) for x in Z["ENVELOPE"]) if "ENVELOPE" in Z.files else set()
    POSE, CID, FI = Z["POSE"], Z["CID"], Z["FI"]
    P_, C_ = R["PC"]; FEAS = np.unpackbits(np.frombuffer(base64.b64decode(R["feas_all"]), np.uint8))[:P_ * C_].reshape(P_, C_).astype(bool)[:, 0]
    a1, a2 = R["a"]; sing = float(R.get("sing_deg", 10.0))
    lim = dict(close=(abs(a1 - a2), min(a1 + a2, 360 - a1 - a2)), sing=(abs(a1 - a2) + sing, min(a1 + a2, 360 - a1 - a2) - sing))
    geo = geometry_of(R, POSE)
    # ---- the evaluator on CPU over the clip frames, hooked
    BI = hooked_band_impl()
    clip_ids = [k for k, n in enumerate(NAMES) if n not in ENV]
    poses_cpu = open(os.path.join(CONF, "band_poses.b64")).read()
    Zc = np.load(io.BytesIO(gzip.decompress(base64.b64decode(poses_cpu))))
    assert len(Zc["POSE"]) == int(sum((CID == k).sum() for k in clip_ids)) and np.allclose(Zc["POSE"], POSE[:len(Zc["POSE"])]), "clip frames differ between payloads"
    cfg = json.load(open(os.path.join(CONF, "gpu_client", os.environ.get("CFG", "r18_cfgs.json"))))[int(os.environ.get("CFG_I", 1))]
    geo_job = {k: cfg[k] for k in ("hub_r", "hub_relief", "hub_margin", "stack", "t_w", "t_link", "neck", "b_ant_max", "mount_dir", "t_lo", "hub_up", "cap_up", "rail_d", "min_arc", "min_arm_mm", "G", "ramp_deg", "hw") if k in cfg}
    for k in ("hub_r", "stack", "t_link", "ramp_deg", "hw"):
        if k in R and R[k] is not None: geo_job[k] = R[k]
    for k in ("hub_relief", "hub_up", "cap_up"):                                       # job keys the DETAIL eval ran with (env overrides)
        if os.environ.get(k.upper()): geo_job[k] = float(os.environ[k.upper()])
    if os.environ.get("FILL_HOLES") == "1": geo_job["fill_holes"] = True               # band-2026-10-15m measurement (skin-map pole holes)
    job = dict(geo_job, mode="band_eval", poses=poses_cpu, maps_cache=os.path.join(REPO, ".cache", "maps_s1.pt"), q_step=R.get("q_step", 12),
               fit_clips=R.get("fit_clips"), env_target=0.9, env_weight=4.0, jn_low=os.environ.get("JN_LOW", "arm"))
    for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
        if g.lower() in job: setattr(BI, g, float(job[g.lower()]))
    B = BI.Band(job, torch.device("cpu"))
    d = {k: R[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm") if k in R}
    mode = os.environ.get("FIT", "wsf")
    if mode == "wsf":                                                                 # impose the DETAIL result's shape
        h_w = torch.tensor(R["h"], dtype=torch.float32); bu_w = torch.tensor(R["bot_under"], dtype=torch.float32)
        faces_w = {int(k) if k.isdigit() else k: float(v) for k, v in R["faces"].items()}
        orig_fit = B.fit_shape
        def fit_fixed(*a, **kw):
            h, S, sc, zj4 = orig_fit(*a, **kw)                                         # sets _faces_full (neck under from kept clip frames)
            ff = dict(B._faces_full); ff.update({k: torch.tensor(v) for k, v in faces_w.items()}); ff["bot_under"] = bu_w
            B._faces_full = ff; B._bot_under = bu_w; B._faces = dict(faces_w)
            return h_w.clone(), S, sc, faces_w["zj4"]
        B.fit_shape = fit_fixed; d["zj4_fixed"] = faces_w["zj4"]
    t0 = time.time(); r = B.evaluate(dict(d), detail=False); print(f"CPU eval ({mode} shape, JN lower member: {os.environ.get('JN_LOW', 'arm')}): score {r['score']:.3f} in-band {r['in_band']:.3f} (G {job.get('G')}) zj4 {r['zj4']:.1f} faces {B._faces} follow {r['follow']:.3f}, clips " +
                                                                     ", ".join(f"{k} {v['follow']:.2f}" for k, v in r["clips"].items()) + f"  ({time.time() - t0:.0f}s)", flush=True)
    S = next(x for x in B._iters if x["it"] == B._best_it); t = torch
    VALID = S["VALID"][:, 0]; LO = S["LO"][:, 0]; HI = S["HI"][:, 0]; hl = S["hl"]; h = S["h"]; memA, kindA = S["memA"], S["kindA"]
    lo_def = (LO - hl[None]).clamp(min=0); hi_def = (h[None] - HI).clamp(min=0)
    ff = S["faces_full"]; aux_lo = []
    for ax_, u_ in zip(B._aux, ff.get("aux_under", [])): aux_lo.append((ax_["name"], (ax_["LO"] - u_[None]).clamp(min=0)))
    cls = lambda i: ("ribbon" if int(kindA[i]) == 0 else ("JN hub (BOTTOM)" if bool(S["is_bot"][i]) else ("lower hub" if bool(S["is_low"][i]) else "upper hub")))
    pairs = {k: t.cat(v, 0)[:, 0] for k, v in S["pair_hits"].items()}
    nm_m = lambda s: s.replace("m0", "base").replace("m1", "link 1").replace("m2", "link 2").replace("m3", "link 3")
    rows = []; cnt = defaultdict(Counter)
    for f in range(len(Zc["POSE"])):
        ci = int(CID[f]); g = geo[f]; why = []
        if g["az"] is None or not (lim["close"][0] <= g["th"] <= lim["close"][1]): why.append(f"chain does not close (J1-J3 {g['th']:.1f} deg, closes {lim['close'][0]:.1f}..{lim['close'][1]:.1f})")
        elif not bool(VALID[f]): why.append(f"J2 singularity margin (J1-J3 {g['th']:.1f} deg, allowed {lim['sing'][0]:.1f}..{lim['sing'][1]:.1f})")
        if bool(VALID[f]):
            ld = lo_def[f]
            if bool((ld > 1e-3).any()):
                for mi in sorted(set(memA[ld > 1e-3].tolist())):
                    m_ = (memA == mi) & (ld > 1e-3); i = int(t.nonzero(m_)[0][0]); worst = int(t.argmax(t.where(m_, ld, t.zeros_like(ld))))
                    why.append(f"skin above {('base' if mi == 0 else f'link {mi}')} {cls(worst)} by {float(ld[worst]):.1f} mm ({int(m_.sum())} samples)")
            hd = hi_def[f]
            if bool((hd > 1e-3).any()):
                for mi in sorted(set(memA[hd > 1e-3].tolist())):
                    m_ = (memA == mi) & (hd > 1e-3); worst = int(t.argmax(t.where(m_, hd, t.zeros_like(hd))))
                    why.append(f"squeeze: {('base' if mi == 0 else f'link {mi}')} {cls(worst)} {float(hd[worst]):.1f} mm over a re-entry sheet ({int(m_.sum())} samples)")
            for k, v in pairs.items():
                if bool(v[f]): why.append(f"collision {nm_m(k)}")
            for nm, dd in aux_lo:
                if bool((dd[f] > 1e-3).any()): why.append(f"skin above the {nm} by {float(dd[f].max()):.1f} mm")
        cpu_feas = bool(VALID[f]) and not any(w_.startswith(("skin", "squeeze", "collision")) for w_ in why)
        rows.append(dict(f=f, clip=NAMES[ci], fi=int(FI[f]), pose=[round(float(x), 1) for x in POSE[f][:3]], th=round(g["th"], 1), az_l2=None if g["az"] is None else round(g["az"], 1),
                         feas_gpu=bool(FEAS[f]), feas_cpu=cpu_feas, why=why))
        if not FEAS[f]:
            import re
            for w_ in why: cnt[NAMES[ci]][re.sub(r" [-0-9.]+ mm.*| by .*| \(.*", "", w_)] += 1
            if not why: cnt[NAMES[ci]]["(cpu: no blocker - wsf-only constraint)"] += 1
    # workspace poses: kinematics + azimuth only (no CPU maps for them)
    ws = [dict(pose=[round(float(x), 1) for x in POSE[f][:3]], th=round(geo[f]["th"], 1), az_l2=None if geo[f]["az"] is None else round(geo[f]["az"], 1), feas_gpu=bool(FEAS[f]))
          for f in range(len(POSE)) if NAMES[int(CID[f])] in ENV]
    print("\nheld (evaluator-infeasible) clip frames, by blocker:")
    for c in [NAMES[k] for k in clip_ids]:
        n_inf = sum(1 for r_ in rows if r_["clip"] == c and not r_["feas_gpu"]); n_all = sum(1 for r_ in rows if r_["clip"] == c)
        if n_inf: print(f"  {c:24s} {n_inf:3d} of {n_all}: " + "; ".join(f"{k} x{v}" for k, v in cnt[c].most_common()))
    agree = np.mean([r_["feas_gpu"] == r_["feas_cpu"] for r_ in rows]); print(f"CPU vs GPU feasibility agree on {100 * agree:.1f}% of clip frames")
    az = np.array([w["az_l2"] for w in ws if w["az_l2"] is not None]); azc = np.array([r_["az_l2"] for r_ in rows if r_["az_l2"] is not None])
    hist = lambda a: np.histogram(a, bins=np.arange(-180, 181, 30))[0].tolist()
    print(f"link {R['n'] - 1} azimuth about JN (0 = toward the bar), 30 deg bins from -180: clips {hist(azc)}, workspace {hist(az)}")
    json.dump(dict(key=key, fit=mode, jn_low=os.environ.get("JN_LOW", "arm"), limits=lim, cpu_eval=dict(score=r["score"], in_band=r["in_band"], follow=r["follow"], clips=r["clips"], faces=B._faces), summary={k: dict(v) for k, v in cnt.items()}, frames=rows, workspace=ws),
              open(outp, "w"), indent=0)
    print("wrote", outp)

if __name__ == "__main__":
    main()
