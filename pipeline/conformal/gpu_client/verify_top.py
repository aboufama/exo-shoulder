"""Top designs of a band search -> detailed GPU eval -> proxy design dirs -> honest score_design.py table.

    RUNPOD_API_KEY=... <flash python> verify_top.py band_search_<tag>.json [per_job=2]
      (writes band_top_<tag>.json, full-exo/designs/band_<tag>_<k>/, prints the honest table)
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FX = os.path.join(HERE, "..", "..", "full-exo")
src = sys.argv[1]; per = int(sys.argv[2]) if len(sys.argv) > 2 else 2; tag = os.path.basename(src).replace("band_search_", "").replace(".json", "")
S = json.load(open(src)); keys = ("n", "az", "el", "a", "w", "branch", "order", "cuff", "hm")
GEO = ("hub_r", "hub_relief", "hub_margin", "stack", "t_link", "G")
designs = []
for job in S:
    if os.environ.get("SKIP_CUFF") == "1" and job["cfg"].get("cuff_range"): continue
    for b in job["best"][:per]:
        designs.append(dict({k: b[k] for k in keys if k in b}, _q=job["cfg"].get("q_step", 6), _geo=json.dumps({g: job["cfg"][g] for g in GEO if g in job["cfg"]}, sort_keys=True),
                            _job=f"n{job['cfg']['n']} s{job['cfg'].get('seed')}", _est=b["score"]))
by_q = {}
for d in designs: by_q.setdefault((d["_q"], d["_geo"]), []).append(d)
results = []
for gi, ((q, geo), ds) in enumerate(by_q.items()):                           # one detailed eval per (grid step, geometry)
    fn = os.path.join(HERE, f"_top_{tag}_{gi}.json"); json.dump([{k: d[k] for k in keys if k in d} for d in ds], open(fn, "w"))
    env = dict(os.environ, DETAIL="1", Q_STEP=str(q), JOB_EXTRA=geo)
    subprocess.run([sys.executable, os.path.join(HERE, "band_client.py"), "eval", fn, f"top_{tag}_{gi}"], check=True, env=env)
    R = json.load(open(os.path.join(HERE, f"band_eval_top_{tag}_{gi}.json")))
    for i, (d, r) in enumerate(zip(ds, R["results"])): results.append((d, os.path.join(HERE, f"band_eval_top_{tag}_{gi}.json"), i, r))
rows = []
for k, (d, path, i, r) in enumerate(results):
    name = f"band_{tag}_{k}"
    subprocess.run(["python3", "-W", "ignore", os.path.join(FX, "band_to_design.py"), path, str(i), name, f"{d['_job']} #{k}"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["python3", "-W", "ignore", os.path.join(FX, "score_design.py"), os.path.join(FX, "designs", name), "3"], check=True, stdout=subprocess.DEVNULL)
    sc = json.load(open(os.path.join(FX, "designs", name, "score.json")))
    rows.append(dict(name=name, job=d["_job"], est=r["score"], honest=sc["overall"], follow=sc["follow"], in_band=sc["in_band"],
                     clips={c["name"]: round(c["score"], 3) for c in sc["clips"]}, design={kk: d[kk] for kk in keys if kk in d}, geo=json.loads(d["_geo"]), zj4=r["zj4"]))
    print(f"{name:18s} {d['_job']:8s} evaluator {100 * r['score']:5.1f}%  honest {100 * sc['overall']:5.1f}%  follow {100 * sc['follow']:5.1f}%  in-band {100 * sc['in_band']:5.1f}%", flush=True)
json.dump(rows, open(os.path.join(HERE, f"band_top_{tag}.json"), "w"), indent=1)
