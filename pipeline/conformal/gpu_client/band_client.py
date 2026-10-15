"""Driver for the band evaluator on RunPod (endpoint exo-band, conformal/gpu/band_impl.py).

    python band_client.py eval designs.json [tag]           -> band_eval_<tag>.json
    python band_client.py search '<[cfg, ...] json>' tag     -> band_search_<tag>.json   (one job per cfg, in parallel)
cfg keys: n (joints), seed, pop, gens, elite, max_secs, q_step, free_w, arc_range, init [designs], stride,
          min_arc (deg, default 35: smallest link arc), min_arm_mm (mm, default 10: clear gap between a link's hub seats)
Run with the Flash tool python (~/.local/share/uv/tools/runpod-flash/bin/python) and RUNPOD_API_KEY set.
"""
import asyncio, json, os, sys, time
from runpod_flash import Endpoint
EP = Endpoint(id=os.environ.get("BAND_EP", "ijltcmvytav2jx"))
HERE = os.path.dirname(os.path.abspath(__file__))
POSES = open(os.path.join(HERE, "..", os.environ.get("POSES_FILE", "band_poses.b64"))).read()      # POSES_FILE=band_poses_fit.b64: the fitting clips only (data/raw/split.json)

async def run(job, timeout=7200):
    j = await EP.run({"job": job})
    try: await j.wait(timeout=timeout)
    except TypeError: await j.wait()
    return j.output

async def main():
    mode = sys.argv[1]
    if mode == "eval":
        D = json.load(open(sys.argv[2])); tag = sys.argv[3] if len(sys.argv) > 3 else "x"
        designs = D if isinstance(D, list) else D["designs"]
        extra = json.loads(os.environ.get("JOB_EXTRA", "{}"))                # e.g. {"stack": 4.5, "t_link": 4.0, "hub_r": 13, "G": 12}
        t = time.time(); out = await run(dict(dict(mode="band_eval", poses=POSES, designs=designs, detail=os.environ.get("DETAIL") == "1",
                                              q_step=float(os.environ.get("Q_STEP", 6)), stride=int(os.environ.get("STRIDE", 0)) or None), **extra))
        if not isinstance(out, dict) or "results" not in out: print("worker returned:", str(out)[:3000]); return
        print(f"{time.time() - t:.0f}s round trip, worker {out['secs']:.0f}s on {out['device']}; code {out.get('version', 'UNVERSIONED (stale worker!)')}")
        for r in out["results"]:
            if r.get("err"): print(f"n{r['n']} REJECTED: {r['err']}"); continue
            print(f"n{r['n']} score {100 * r['score']:5.1f}% (unweighted {100 * r['score_unweighted']:5.1f}%) follow {100 * r['follow']:5.1f}% in-band {100 * r['in_band']:5.1f}%  zj4 {r['zj4']:.1f}")
            for n, c in r["clips"].items(): print(f"     {n:24s} {100 * c['score']:5.1f}%  follow {100 * c['follow']:5.1f}%")
        json.dump(out, open(os.path.join(HERE, f"band_eval_{tag}.json"), "w"))
    elif mode == "search":
        cfgs = json.loads(sys.argv[2]); tag = sys.argv[3]
        jobs = [run(dict(cfg, mode="band_search", poses=POSES)) for cfg in cfgs]
        t = time.time(); outs = await asyncio.gather(*jobs, return_exceptions=True); res = []
        for cfg, o in zip(cfgs, outs):
            if isinstance(o, Exception) or not isinstance(o, dict) or "best" not in o: print("job failed", cfg, str(o)[:2000]); continue
            b = o["best"][0]; print("  code:", o.get("version", "UNVERSIONED (stale worker!)"))
            print(f"n{cfg['n']} seed {cfg.get('seed')}: {o['evals']} evals {o['secs']:.0f}s on {o['device']}: best {100 * b['score']:.1f}% follow {100 * b['follow']:.1f}% in-band {100 * b['in_band']:.1f}%")
            res.append(dict(cfg=cfg, **o))
        json.dump(res, open(os.path.join(HERE, f"band_search_{tag}.json"), "w")); print(f"total {time.time() - t:.0f}s")

asyncio.run(main())
