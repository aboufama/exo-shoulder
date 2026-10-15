"""r18 configs: the MVP1 lever (user: unpowered kinematic proof of concept, "as thin as possible, we're using titanium"):
links 3.0 mm thick and 8-10 mm wide (hw 4-5), miniature-bearing hubs (MR105 pair, O17 -> hub_r 8.5) vs O23; range
first (functional workspace target 0.9, weight 4), arcs >= 60, ramp 60, 14 mm band; warm starts from r17's winners."""
import json
C = json.load(open("r17_cfgs.json")); S = json.load(open("band_search_r17.json"))
keys = ("n", "az", "el", "a", "w", "branch", "order", "hm")
init = [{k: b[k] for k in keys if k in b} for j in S for b in j["best"][:3]]
base = {k: v for k, v in C[0].items() if k != "init"}; base.update(t_link=3.0)
cfgs = []
for seed, warm, hw, hub_r, bal in ((1391, True, 5.0, 8.5, 0.4), (1392, True, 5.0, 11.5, 0.4), (1393, False, 5.0, 8.5, 0.7), (1394, True, 4.0, 8.5, 0.7)):
    c = dict(base, seed=seed, hw=hw, hub_r=hub_r, hub_relief=min(base.get("hub_relief", 12.0), hub_r), balance=bal)
    if warm: c["init"] = init
    cfgs.append(c)
json.dump(cfgs, open("r18_cfgs.json", "w"), indent=1)
print([(c["seed"], "warm" if c.get("init") else "fresh", c["hw"], c["hub_r"], c["t_link"], c["balance"]) for c in cfgs], len(init), "warm seeds")
