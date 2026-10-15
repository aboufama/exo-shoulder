"""r20 configs: the v5 joint the final CAD builds (user 2026-10-15: "We can go to 20mm hubs"): O20 hub (hub_r 10),
2x MR117 (7x11x3) back-to-back in the upper hub (hub_up 7.1 above its underside: 0.5 lip + 3 + 0.6 spacer + 3),
ring nut + flush dome cap (cap_up 2.0), plate gap unchanged (stack 3.15); links 3.0 thick, hw 4. Range first
(functional workspace target 0.9, weight 4), 14 mm band, ramp 60; warm starts from the compact (zj4 < 110 mm)
winners of r17-r19 (stand-off designs excluded: docs/FINDINGS.md)."""
import json, glob
keys = ("n", "az", "el", "a", "w", "branch", "order", "hm")
init = []
for f in ("band_search_r17.json", "band_search_r18.json", "band_search_r19.json"):
    for j in json.load(open(f)):
        for b in j["best"][:8]:
            if b.get("zj4", 0) < 110: init.append({k: b[k] for k in keys if k in b})
seen, uniq = set(), []
for d in init:
    key = (round(d["az"], 1), round(d["el"], 1), tuple(round(v, 1) for v in d["a"]))
    if key not in seen: seen.add(key); uniq.append(d)
base = {k: v for k, v in json.load(open("r19_cfgs.json"))[0].items() if k != "init"}
base.update(hub_r=10.0, hub_relief=10.0, hub_up=7.1, cap_up=2.0, stack=3.15, t_link=3.0, hw=4.0, max_secs=2700)
cfgs = []
for seed, bal, warm in ((1411, 0.4, True), (1412, 0.7, True), (1413, 0.4, True), (1414, 0.4, False)):
    c = dict(base, seed=seed, balance=bal)
    if warm: c["init"] = uniq
    cfgs.append(c)
json.dump(cfgs, open("r20_cfgs.json", "w"), indent=1)
print([(c["seed"], c["balance"], "warm" if c.get("init") else "fresh") for c in cfgs], len(uniq), "warm seeds")
