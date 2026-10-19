"""Which joint-hardware rule costs the most in-band share? One design, the evaluator on CPU (cached skin maps), one
rule changed at a time from the baseline geometry: hub radius, BOTTOM hub thickness (T_BOT), joint stack, the ramp a
link may leave a hub plate at, the contour relief under hubs. Prints score / follow / in-band at 10 and 14 mm and the
in-band ceiling (inband_ceiling.py: the best ANY underside could do on that joint path).
    python3 hub_sensitivity.py <designs json with geo> [design index]"""
import json, os, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
os.environ["BAND_STASH"] = "1"
import inband_ceiling as IC, band_impl as BI, torch
torch.set_num_threads(int(os.environ.get("THREADS", 4)))
D = json.load(open(sys.argv[1])); k = int(sys.argv[2]) if len(sys.argv) > 2 else 0; d0 = D["designs"][k]; geo0 = D.get("geo", {})
poses = open(os.path.join(HERE, "..", "band_poses.b64")).read(); MAPS = os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt")
BASE = {g: getattr(BI, g) for g in ("HUB_R", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D")}
VARIANTS = [("baseline", {}), ("ramp 50 deg", {"ramp_deg": 50.0}), ("ramp 65 deg", {"ramp_deg": 65.0}),
            ("hub radius 9 mm", {"hub_r": 9.0}), ("BOTTOM hub 4.5 mm thick", {"t_bot": 4.5}), ("stack 2.5 mm", {"stack": 2.5}),
            ("hub relief 20 mm", {"hub_relief": 20.0}), ("hub margin 0.8 mm", {"hm": 0.8}),
            ("all of the above", {"ramp_deg": 65.0, "hub_r": 9.0, "t_bot": 4.5, "stack": 2.5, "hub_relief": 20.0, "hm": 0.8})]
if os.environ.get("V5"):                                       # rolling bearings + cable drum (user, 2026-10-15)
    VARIANTS = [("baseline (v4 plain bearings)", {}), ("v5: drum hub R13", {"hub_r": 13.0}), ("v5: 2x 6700 in the hub (hub 8.5)", {"hub_up": 8.5}),
                ("v5: drum R13 + 6700 pair", {"hub_r": 13.0, "hub_up": 8.5}), ("v5 + ramp 60", {"hub_r": 13.0, "hub_up": 8.5, "ramp_deg": 60.0})]
rows = []
print(f"design: {d0.get('_src', '')}", flush=True)
for name, ch in VARIANTS:
    r = dict(variant=name)
    for G in (10.0, 14.0):
        for g, v in BASE.items(): setattr(BI, g, v)
        job = dict(geo0, mode="band_eval", poses=poses, maps_cache=MAPS, q_step=geo0.get("q_step", 12), G=G); d = dict(d0)
        for kk, v in ch.items():
            if kk == "hm": d["hm"] = v
            else: job[kk] = v
        for g in BASE:
            if g.lower() in job: setattr(BI, g, float(job[g.lower()]))
        B = BI.Band(job, torch.device("cpu")); a = IC.analyse(B, d)
        if a.get("err"): r[f"G{G:g}"] = dict(err=a["err"]); continue
        r[f"G{G:g}"] = dict(score=round(a["score"], 3), follow=round(a["follow"], 3), in_band=round(a["achieved"], 3), ceiling=round(a["ceiling"], 3),
                            member_in_band={m: round(v["achieved"], 3) for m, v in a["members"].items()})
    rows.append(r)
    g10, g14 = r.get("G10", {}), r.get("G14", {})
    fmt = lambda x: "rejected: " + x["err"] if "err" in x else f"score {100 * x['score']:5.1f}%  follow {100 * x['follow']:5.1f}%  in-band {100 * x['in_band']:5.1f}% (ceiling {100 * x['ceiling']:5.1f}%)"
    print(f"{name:26s} 10 mm: {fmt(g10)}\n{'':26s} 14 mm: {fmt(g14)}  members {g14.get('member_in_band')}", flush=True)
json.dump(dict(design=d0, rows=rows), open(os.path.join(HERE, "hub_sensitivity.json"), "w"), indent=1)
