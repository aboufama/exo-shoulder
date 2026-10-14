"""one extra search job on the laptop CPU (same band_impl + job config as the GPU jobs)"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu"))
import torch; torch.set_num_threads(int(os.environ.get("THREADS", 3))); import band_impl as BI
cfg = json.loads(sys.argv[1]); tag = sys.argv[2]
cfg.update(poses=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "band_poses.b64")).read(), mode="band_search",
           maps_cache=os.environ.get("MAPS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".cache", "maps_s1.pt")))
r = BI.run(cfg); c = dict(cfg); c.pop("poses"); c.pop("maps_cache")
json.dump([dict(cfg=c, **r)], open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"band_search_{tag}.json"), "w"))
b = r["best"][0]; print(f"local n{cfg['n']} seed {cfg['seed']}: {r['evals']} evals {r['secs']:.0f}s best {100 * b['score']:.1f}% follow {100 * b['follow']:.1f}%", flush=True)
