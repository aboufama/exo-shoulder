"""Hill-climb the leader on the HONEST score (local, free): perturb -> full-frame detail eval -> proxies -> score_design."""
import sys, json, os, subprocess, random, copy, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu"))
import torch; torch.set_num_threads(4); import band_impl as BI
E = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")); S = os.path.dirname(os.path.abspath(__file__)); FX = f"{E}/full-exo"; GC = f"{E}/conformal/gpu_client"
budget = float(sys.argv[1]) if len(sys.argv) > 1 else 6000; STEP = sys.argv[2] if len(sys.argv) > 2 else "6"
keys = ("n", "az", "el", "a", "w", "branch", "order", "cuff", "hm"); GEO = ("hub_r", "hub_relief", "hub_margin", "stack", "t_link", "G")
job = json.load(open(f"{GC}/band_search_r10a.json"))[0]; cfg = job["cfg"]; geo = {k: cfg[k] for k in GEO if k in cfg}
poses = open(f"{E}/conformal/band_poses.b64").read()
def honest(d, tag):
    BI.HUB_R, BI.STACK, BI.T_LINK = 17.0, 6.0, 5.5
    r = BI.run(dict(mode="band_eval", poses=poses, q_step=cfg.get("q_step", 12), chunk=12, maps_cache=f"{S}/maps_s1.pt", detail=True, designs=[d], **geo))
    jf = f"{S}/hc_{tag}.json"; json.dump(r, open(jf, "w")); name = f"band_hc_{tag}"
    subprocess.run(["python3", "-W", "ignore", f"{FX}/band_to_design.py", jf, "0", name, f"honest climb {tag}"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["python3", "-W", "ignore", f"{FX}/score_design.py", f"{FX}/designs/{name}", STEP], check=True, stdout=subprocess.DEVNULL)
    return json.load(open(f"{FX}/designs/{name}/score.json"))["overall"], name
d0 = {k: job["best"][0][k] for k in keys if k in job["best"][0]}
rng = random.Random(23); t0 = time.time()
s0, n0 = honest(d0, "base"); best = (s0, d0, n0); print(f"base honest (step {STEP}) {100 * s0:.1f}%", flush=True); k = 0
while time.time() - t0 < budget:
    k += 1; d = copy.deepcopy(best[1]); m = rng.random()
    if m < 0.35: d["cuff"]["range"] = min(45, max(10, d["cuff"]["range"] + rng.gauss(0, 1.5)))
    elif m < 0.55: d["hm"] = min(4, max(0.8, d.get("hm", 2.0) + rng.gauss(0, 0.25)))
    elif m < 0.8: i = rng.randrange(3); d["a"][i] = max(6, d["a"][i] + rng.gauss(0, 0.8))
    else: d["w"][0] += rng.gauss(0, 1.0); d["w"][1] += rng.gauss(0, 1.5); d["az"] = (d["az"] + rng.gauss(0, 1.0)) % 360; d["el"] += rng.gauss(0, 0.7)
    try: s, name = honest(d, f"{k}")
    except Exception as e: print(k, "failed", str(e)[:120], flush=True); continue
    tag = "IMPROVED" if s > best[0] else ""
    print(f"{k} {time.time() - t0:.0f}s honest {100 * s:.1f}% {tag}  cuff {d['cuff']['range']:.1f} hm {d.get('hm', 2):.2f} a {[round(x, 1) for x in d['a']]}", flush=True)
    if s > best[0]: best = (s, d, name); json.dump(dict(score=s, design=d, name=name), open(f"{S}/honest_climb_best.json", "w"))
print("best", 100 * best[0], best[2])
