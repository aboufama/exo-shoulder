"""How much of R1 can a design's links reach at all? For every scored sample of the evaluator's fitted shape, along the
chosen joint path: the underside must clear the skin in every followed frame (h >= max over frames of the lower bound),
so the best it can do is sit exactly there; it is in band in a frame only if the skin there is within G of that height.
ceiling = share of (frame, sample) pairs in band with that lowest legal underside - an upper bound for ANY underside
shape on these kinematics and this path. Compared with what the fitted shape achieves, per member and per clip.
    python3 inband_ceiling.py <designs json> [G ...]      (CPU; uses .cache/maps_s1.pt and band_poses.b64)"""
import json, os, sys, time
os.environ["BAND_STASH"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(HERE, "gpu")); import band_impl as BI
import torch

def analyse(B, d):
    r = B.evaluate(dict(d), detail=False)
    if r.get("err"): return dict(err=r["err"])
    S = B._stash; t = torch; ar = t.arange(S["LO"].shape[0])
    fe = S["feas"]; LO = S["LO"][ar, S["cfg"]][fe]; CAP = S["CAP"][ar, S["cfg"]][fe]; WT = B.WT[fe]
    h = t.where(S["is_bot"], S["bot_under"], S["h"]); m = S["scored"] & (S["wS"] > 0)
    hmin = LO.max(0).values                                                   # lowest legal underside per sample
    cid = B.P["CID"][fe]; names = list(B.P["NAMES"]); w = S["wS"]
    def share(H, sel_s, sel_f=None):
        ok = (H[None] <= CAP + 1e-3).float()
        if sel_f is not None: ok = ok[sel_f]; wt = WT[sel_f]
        else: wt = WT
        ww = (w * sel_s.float())[None] * wt[:, None]
        return float((ok * ww).sum() / ww.sum()) if float(ww.sum()) > 0 else float("nan")
    out = dict(score=r["score"], follow=r["follow"], in_band=r["in_band"], achieved=share(h, m), ceiling=share(hmin, m),
               mean_lift_mm=float(((h - hmin)[m] * w[m]).sum() / w[m].sum()), members={}, clips={})
    for mi in sorted(set(S["memA"].tolist())):
        mm = m & (S["memA"] == mi); rib = mm & (S["kindA"] == 0)
        if bool(mm.any()): out["members"][f"member {mi}"] = dict(area=float(w[mm].sum() / w[m].sum()), achieved=share(h, mm), ceiling=share(hmin, mm),
                                                                  ribbon_ceiling=share(hmin, rib) if bool(rib.any()) else None)
    for k, n in enumerate(names):
        sf = cid == k
        if bool(sf.any()): out["clips"][n] = dict(achieved=share(h, m, sf), ceiling=share(hmin, m, sf))
    return out

if __name__ == "__main__":
    D = json.load(open(sys.argv[1])); Gs = [float(x) for x in sys.argv[2:]] or [10.0]
    geo = D.get("geo", {}); designs = D["designs"]; res = []
    poses = open(os.path.join(HERE, "band_poses.b64")).read()
    for G in Gs:
        job = dict(geo, mode="band_eval", poses=poses, maps_cache=os.path.join(REPO, ".cache", "maps_s1.pt"), q_step=geo.get("q_step", 12), G=G)
        for k in ("HUB_R", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
            if k.lower() in job: setattr(BI, k, float(job[k.lower()]))
        t0 = time.time(); B = BI.Band(job, torch.device("cpu"))
        for d in designs:
            a = analyse(B, d); a["G"] = G; a["_src"] = d.get("_src"); res.append(a)
            print(f"G {G:g} mm  {d.get('_src', '')[:60]}: score {a.get('score', 0):.3f}  in-band achieved {a.get('achieved', 0):.3f} / ceiling {a.get('ceiling', 0):.3f}"
                  f"  (shape sits {a.get('mean_lift_mm', 0):.1f} mm above its lowest legal underside)  {time.time() - t0:.0f}s", flush=True)
            for k, v in a.get("members", {}).items(): print(f"     {k}: area {v['area']:.2f}  achieved {v['achieved']:.3f}  ceiling {v['ceiling']:.3f}")
    json.dump(res, open(os.path.join(HERE, "inband_ceiling.json"), "w"), indent=1)
