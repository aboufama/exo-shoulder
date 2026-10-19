"""A DETAIL band_eval result computed on CPU, in the format make_input.py / fair_pipeline.sh take, for designs whose
CAD is to be judged (agent D's proximity tests).

The CPU has the dense skin maps of the 8 clips only (.cache/maps_s1.pt = band_poses.b64), so the shape is fitted to the
fit clips WITHOUT the workspace envelope (the GPU detail evals on band_poses_wsf.b64 fit it to the clips + 1432
functional-workspace poses). To let band_to_design write workspace.json (R16 is judged on the CAD, independently of the
evaluator), the per-pose arrays are padded to band_poses_wsf.b64: the workspace poses are marked NOT evaluated
(feasible False, share 0; workspace.json's eval_feasible is then False everywhere - informational only, judge/workspace.py
does not use it). The maps' pole holes are filled first (map_holes.py; FILL_HOLES=0 for the raw maps).

    THREADS=2 python3 cpu_detail.py <designs json: [{n, az, el, a, w, branch, order, hm, _src}]> <geo json> <out json>
-> then: python3 ../band_cad/make_input.py <out json> <i> <key> --ramp-deg <geo ramp_deg> --poses band_poses_wsf.b64 [--hw <geo hw>]"""
import base64, gzip, io, json, os, sys, time
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, ".."); sys.path.insert(0, os.path.join(CONF, "gpu"))
import band_impl as BI, map_holes
torch.set_num_threads(int(os.environ.get("THREADS", 2)))
DES = json.load(open(sys.argv[1])); DES = DES if isinstance(DES, list) else DES["designs"]; GEO = json.load(open(sys.argv[2])); OUT = sys.argv[3]
for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
    if g.lower() in GEO: setattr(BI, g, float(GEO[g.lower()]))
job = dict(GEO, mode="band_eval", poses=open(os.path.join(CONF, "band_poses.b64")).read(), maps_cache=os.path.join(CONF, "..", "..", ".cache", "maps_s1.pt"), G=float(GEO.get("G", 14.0)))
B = BI.Band(job, torch.device("cpu")); filled = os.environ.get("FILL_HOLES", "1") == "1"
if filled:
    key = next(iter(BI._CACHE)); Mx, Px = BI._CACHE[key]; BI._CACHE[key] = (map_holes.fill(Mx), Px); B = BI.Band(job, torch.device("cpu"))
load = lambda f: np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, f)).read()))))
NW = len(load("band_poses_wsf.b64")["POSE"]); N0 = len(B.P["POSE"])
res = []; t0 = time.time()
for d in DES:
    dd = {k: d[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm", "cuff") if k in d}
    r = B.evaluate(dict(dd), detail=True)
    if r.get("err"): res.append(dict(dd, **r)); print("REJECTED", r["err"]); continue
    P_, C_ = r["PC"]; assert P_ == N0
    fa = np.unpackbits(np.frombuffer(base64.b64decode(r["feas_all"]), np.uint8))[:P_ * C_].reshape(P_, C_).astype(bool)
    sa = np.frombuffer(base64.b64decode(r["share_all"]), np.uint8).reshape(P_, C_)
    pad = NW - P_
    fa = np.r_[fa, np.zeros((pad, C_), bool)]; sa = np.r_[sa, np.zeros((pad, C_), np.uint8)]
    r["feas_all"] = base64.b64encode(np.packbits(fa, axis=None).tobytes()).decode(); r["share_all"] = base64.b64encode(sa.tobytes()).decode(); r["PC"] = [NW, C_]
    r["cfg"] = r["cfg"] + [0] * pad; r["feasible"] = r["feasible"] + [False] * pad; r["frame"] = r["frame"] + [0.0] * pad
    r["_cpu_detail"] = (f"CPU detail eval on band_poses.b64 (clips only, fit clips {GEO.get('fit_clips')}), maps {'with pole holes filled (analysis/map_holes.py)' if filled else 'raw'}; "
                        f"padded to band_poses_wsf.b64: the {pad} workspace poses were NOT evaluated (feasible False)")
    res.append(dict(dd, _src=d.get("_src", ""), **r))
    print(f"{d.get('_src', '')[:50]}: score {r['score']:.3f} follow {r['follow']:.3f} in-band {r['in_band']:.3f} zj4 {r['zj4']:.1f} faces {r['faces']}  {time.time() - t0:.0f}s", flush=True)
json.dump(dict(results=res, secs=time.time() - t0, device="cpu", version=BI.CODE_VERSION + (" + pole holes filled (analysis/map_holes.py)" if filled else "") + "; CPU clip-only detail (analysis/cpu_detail.py)"), open(OUT, "w"))
print("wrote", OUT)
