"""local detail evals (real-geometry band_impl, CPU) of a search's best designs -> band_cad/inputs/<tag>_n<N>_<k>.json + a ranking"""
import sys, json, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu"))
import torch; torch.set_num_threads(4); import band_impl as BI
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, "..", "band_cad", "inputs")
S = json.load(open(sys.argv[1])); tag = sys.argv[2]; per = int(sys.argv[3]) if len(sys.argv) > 3 else 2
MAPS = os.environ.get("MAPS", os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt"))   # dense per-frame skin maps (tools/build_maps.py)
poses = open(os.path.join(HERE, "..", "band_poses.b64")).read()
keys = ("n", "az", "el", "a", "w", "branch", "order", "cuff", "hm"); GEO = ("hub_r", "hub_relief", "hub_margin", "stack", "t_w", "t_link", "G", "balance", "neck", "b_ant_max", "mount_dir", "min_arc", "min_arm_mm")
rows = []
for job in S:
    cfg = job["cfg"]; geo = {k: cfg[k] for k in GEO if k in cfg}
    for k, b in enumerate(job["best"][:per]):
        d = {kk: b[kk] for kk in keys if kk in b}; t0 = time.time()
        r = BI.run(dict(mode="band_eval", poses=poses, q_step=cfg.get("q_step", 12), chunk=12, maps_cache=MAPS, detail=True, designs=[d], **geo))
        name = f"{tag}_n{cfg['n']}_s{cfg['seed']}_{k}"; x = r["results"][0]
        if x.get("err"): print(f"{name:26s} REJECTED (no CAD input written): {x['err']}", flush=True); continue
        json.dump(r, open(os.path.join(IN, f"{name}.json"), "w"))
        rows.append(dict(name=name, n=cfg["n"], cuff=bool(d.get("cuff")), score=x["score"], follow=x["follow"], in_band=x["in_band"], gpu_score=b["score"]))
        print(f"{name:26s} local {100 * x['score']:5.1f}%  (search {100 * b['score']:5.1f}%)  follow {100 * x['follow']:5.1f}  in-band {100 * x['in_band']:5.1f}  {time.time() - t0:.0f}s", flush=True)
rows.sort(key=lambda r: -r["score"]); json.dump(rows, open(os.path.join(HERE, f"detail_{tag}.json"), "w"), indent=1)
