"""Does moving the arm-fixed joint JN (BOTTOM's hub, axis W in the humerus frame) onto low-skin-motion skin raise the
in-band share? (skin_motion_map.py: the r18 s1392 #1 W (71.4, 4.8) sits on the deltoid belly, 23 mm of radial skin
motion, flat-disc ceiling 40 %; W ~ (112, -15) sits under the acromion edge, 12 mm, disc ceiling 94 %.)
Small evolutionary local search on CPU (band evaluator, cached clip maps with the pole holes filled - map_holes.py -,
fit clips only shape the design; no workspace envelope on CPU, so the range (R16) is NOT judged here): the chain
(az, el, a, branch, order, hm) re-optimised with W held in a box, vs the same search with W free near the design's own.
Objective = the evaluator's fit-clip score (follow x in band, overhead weighted) at G; follow and in-band reported.

    THREADS=2 python3 local_w_search.py <cad input json> <geo json> <tag> [w_lo_delta w_hi_delta w_lo_az w_hi_az] [evals=240]
-> local_w_search_<tag>.json"""
import json, os, sys, random, time, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu"))
import band_impl as BI, torch, map_holes
torch.set_num_threads(int(os.environ.get("THREADS", 2)))
SRC = json.load(open(sys.argv[1]))["results"][0]; GEO = json.load(open(sys.argv[2])); TAG = sys.argv[3]
box = [float(x) for x in sys.argv[4:8]] if len(sys.argv) >= 8 else None; NEV = int(sys.argv[8]) if len(sys.argv) > 8 else 240
G = float(os.environ.get("G", 14.0)); rng = random.Random(int(os.environ.get("SEED", 1)))
for g in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):
    if g.lower() in GEO: setattr(BI, g, float(GEO[g.lower()]))
job = dict(GEO, mode="band_eval", poses=open(os.path.join(HERE, "..", "band_poses.b64")).read(), maps_cache=os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt"), G=G)
B = BI.Band(job, torch.device("cpu"))
if os.environ.get("FILL_HOLES", "1") == "1":
    key = next(iter(BI._CACHE)); Mx, Px = BI._CACHE[key]; BI._CACHE[key] = (map_holes.fill(Mx), Px); B = BI.Band(job, torch.device("cpu"))
d0 = {k: SRC[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm")}
def ev(d):
    try: r = B.evaluate(dict(d))
    except Exception as e: return dict(score=-1, err=str(e)[:120])
    return r
def obj(r): return r.get("score_fit", r.get("score", -1)) if not r.get("err") else -1
def clampw(d):
    if box: d["w"] = [min(box[1], max(box[0], d["w"][0])), min(box[3], max(box[2], d["w"][1]))]
    return d
lo, hi = BI.arc_bounds(GEO)
def mutate(d, s):
    n = copy.deepcopy(d)
    n["az"] = (n["az"] + rng.gauss(0, 12 * s)) % 360; n["el"] = min(90, max(-10, n["el"] + rng.gauss(0, 6 * s)))
    n["a"] = [min(hi, max(lo, x + rng.gauss(0, 6 * s))) for x in n["a"]]
    n["w"] = [n["w"][0] + rng.gauss(0, 5 * s), n["w"][1] + rng.gauss(0, 8 * s)]
    if rng.random() < 0.1: n["branch"] = -n["branch"]
    for k in range(3):
        if rng.random() < 0.06: n["order"][k] = 1 - n["order"][k]
    n["hm"] = min(4.0, max(0.8, n.get("hm", 2.0) + rng.gauss(0, 0.3 * s)))
    return clampw(n)
t0 = time.time(); base = ev(d0)
print(f"baseline {d0['w']}: fit score {obj(base):.3f}  follow {base.get('follow', 0):.3f}  in-band {base.get('in_band', 0):.3f}", flush=True)
start = clampw(copy.deepcopy(d0))
if box: start["w"] = [0.5 * (box[0] + box[1]), 0.5 * (box[2] + box[3])]
pop = [(obj(r), d, r) for d in [start] + [mutate(start, 2.0) for _ in range(23)] for r in [ev(d)]]
evals = len(pop)
while evals < NEV:
    pop.sort(key=lambda x: -x[0]); el = pop[:6]; s = max(0.3, 1.0 - evals / NEV)
    kids = [mutate(rng.choice(el)[1], s) for _ in range(12)]
    pop = el + [(obj(r), d, r) for d in kids for r in [ev(d)]]; evals += len(kids)
    b = pop[0] if pop[0][0] >= max(p[0] for p in pop) else max(pop, key=lambda x: x[0])
    print(f"  {evals:4d} evals {time.time() - t0:4.0f}s  best fit score {b[0]:.3f} follow {b[2].get('follow', 0):.3f} in-band {b[2].get('in_band', 0):.3f}  w {[round(x, 1) for x in b[1]['w']]}", flush=True)
pop.sort(key=lambda x: -x[0])
top = [dict(d, **{k: v for k, v in r.items() if k in ("score", "score_fit", "follow", "follow_fit", "in_band", "clips", "zj4", "arm_mm")}) for _, d, r in pop[:5]]
json.dump(dict(baseline=dict(d0, **{k: v for k, v in base.items() if k in ("score", "score_fit", "follow", "follow_fit", "in_band", "clips")}), box=box, G=G, top=top),
          open(os.path.join(HERE, f"local_w_search_{TAG}.json"), "w"), indent=1)
print("best:", json.dumps({k: top[0][k] for k in ("az", "el", "a", "w", "branch", "order", "hm", "score_fit", "follow", "in_band")}))
