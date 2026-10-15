"""r21: r20's O20 / joint v5 geometry on the corrected evaluator (band-2026-10-15m): fill_holes (the skin-map pole
holes, a measurement fix) and hub_relief 3.65 (the lower-hub contour the CAD can build). Warm starts: r20's compact
designs (zj4 < 110 on the 15-deg detail eval) + the r18/r19 compact set. Range first as before."""
import json
keys = ("n", "az", "el", "a", "w", "branch", "order", "hm")
init, seen = [], set()
def add(d):
    k = (round(d["az"], 1), round(d["el"], 1), tuple(round(v, 1) for v in d["a"]))
    if k not in seen: seen.add(k); init.append({q: d[q] for q in keys if q in d})
import glob
for f in sorted(glob.glob("band_eval_det20d*.json")):
    for x in json.load(open(f))["results"]:
        if not x.get("err") and x["zj4"] < 110: add(x)
for j in json.load(open("band_search_r20.json")):
    for b in j["best"][:8]:
        if b["zj4"] < 110: add(b)
base = {k: v for k, v in json.load(open("r20_cfgs.json"))[0].items() if k != "init"}
base.update(fill_holes=True, hub_relief=3.65, max_secs=2700)
cfgs = [dict(base, seed=s, balance=b, **({"init": init} if w else {})) for s, b, w in ((1421, 0.4, True), (1422, 0.7, True), (1423, 0.4, False), (1424, 0.55, True))]
json.dump(cfgs, open("r21_cfgs.json", "w"), indent=1); print(len(init), "warm seeds;", [(c["seed"], c["balance"], bool(c.get("init"))) for c in cfgs])
