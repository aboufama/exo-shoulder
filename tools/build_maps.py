"""Build the dense per-frame skin maps (.cache/maps_s1.pt, ~860 MB) that fair_cad/envelope.py and
gpu_client/detail_local.py read. Runs one local band evaluation with maps_cache set; the evaluator builds and saves the
maps when the file is missing. CPU works (slow - minutes to an hour); a CUDA GPU is used when present.
    python3 tools/build_maps.py"""
import json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); GPU = os.path.join(ROOT, "pipeline", "conformal", "gpu")
sys.path.insert(0, GPU); os.chdir(GPU)
import torch; torch.set_num_threads(int(os.environ.get("THREADS", 4))); import band_impl as BI
MAPS = os.environ.get("MAPS", os.path.join(ROOT, ".cache", "maps_s1.pt")); os.makedirs(os.path.dirname(MAPS), exist_ok=True)
if os.path.exists(MAPS): print("already built:", MAPS); sys.exit(0)
poses = open(os.path.join(ROOT, "pipeline", "conformal", "band_poses.b64")).read()
src = json.load(open(os.path.join(ROOT, "pipeline", "conformal", "band_cad", "inputs", "r13_n4_s1343_1.json")))
d = {k: src["results"][0][k] for k in ("n", "az", "el", "a", "w", "branch", "order", "cuff", "hm") if k in src["results"][0]}
t0 = time.time(); BI.run(dict(mode="band_eval", poses=poses, q_step=12, chunk=12, maps_cache=MAPS, designs=[d]))
print(f"maps -> {MAPS} ({os.path.getsize(MAPS) / 1e6:.0f} MB, {time.time() - t0:.0f}s)")
