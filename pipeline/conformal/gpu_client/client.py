"""local driver for the exo-conformal endpoint: python client.py eval|search ..."""
import asyncio, base64, json, os, sys, time
from runpod_flash import Endpoint
EP = Endpoint(id="sb7im40290hyru")
HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = base64.b64encode(open(os.path.join(HERE, "..", "maps_half.npz.gz"), "rb").read()).decode()
SKIN = open(os.path.join(HERE, "..", "skin_payload.b64")).read(); POSES = open(os.path.join(HERE, "..", "poses_payload.b64")).read()
EXACT = os.environ.get("EXACT", "1") == "1"
def maps_kw(): return dict(skin=SKIN, poses=POSES, maps="") if EXACT else dict(maps=MAPS)
async def run(job, timeout=5400):
    j = await EP.run({"job": job}); await j.wait(timeout=timeout) if "timeout" in j.wait.__code__.co_varnames else await j.wait()
    return j.output
async def main():
    mode = sys.argv[1]
    T = json.load(open(os.path.join(HERE, os.environ.get("DESIGNS", "test_designs.json"))))
    if mode == "eval":
        t = time.time(); out = await run(dict(**maps_kw(), mode="eval", W=T["W"], bar_dir=T.get("bar_dir", [0, -1, 0]), collide=os.environ.get("COLLIDE", "1") == "1", z_j4=67.5, G=10.0, q_step=6, q_rest_step=6, designs=T["designs"]))
        if not isinstance(out, dict) or "results" not in out: print("worker returned:", str(out)[:3000]); return
        print(f"{time.time() - t:.0f}s round trip; worker {out.get('secs', 0):.1f}s on {out.get('device')}")
        for r in out["results"]:
            print("GPU cov %.3f p50 %.1f p90 %.1f per %s | CPU cov %.3f p50 %.1f p90 %.1f per %s" % (r["cov"], r.get("gap_p50", 0), r.get("gap_p90", 0),
                  [round(x, 1) for x in r.get("per_link_p50", [])], r["cpu"]["cov"], r["cpu"]["gap_p50"], r["cpu"]["gap_p90"], [round(x, 1) for x in r["cpu"]["per_link_p50"]]))
    elif mode == "search":
        cfgs = json.loads(sys.argv[2]); tag = sys.argv[3]
        jobs = [run(dict(**maps_kw(), mode="search", W=T["W"], bar_dir=T.get("bar_dir", [0, -1, 0]), collide=True, z_j4=67.5, G=cfg.get("G", 10.0), q_step=cfg.get("q_step", 6), q_rest_step=cfg.get("q_rest_step", 30),
                         seed=cfg.get("seed", 1), gens=cfg.get("gens", 40), hub_r=cfg.get("hub_r", 17.0), pop=cfg.get("pop", 96), elite=cfg.get("elite", 16), weights=cfg.get("weights", {}),
                         init=[{k: d[k] for k in ("az", "el", "a1", "a2", "a3", "branch", "order")} for d in (T["designs"] + T.get("extra", []))], max_secs=cfg.get("max_secs", 4800))) for cfg in cfgs]
        t = time.time(); outs = await asyncio.gather(*jobs, return_exceptions=True)
        res = []
        for cfg, o in zip(cfgs, outs):
            if isinstance(o, Exception): print("job failed", cfg, o); continue
            print(f"cfg {cfg}: {o['evals']} evals in {o['secs']:.0f}s on {o['device']}; best score {o['best'][0]['score']:.3f} cov {o['best'][0]['cov']:.3f} per-link {[round(x,1) for x in o['best'][0]['per_link_p50']]}")
            res.append(dict(cfg=cfg, **o))
        json.dump(res, open(os.path.join(HERE, f"search_{tag}.json"), "w")); print(f"total {time.time() - t:.0f}s")
asyncio.run(main())
