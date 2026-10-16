"""Summarise the reach-attribution runs (docs/research/reach/runs/<leader>_m<m>[_refit].json, written by attribute.py on the
farm): per leader the lost workspace poses by first cause (overall, overhead, across the body, behind the back), the clip
frames lost, the per-pose CSV of the m10 run, and the fold-margin sensitivity (reach, gap and the conditioning of the
3R at the poses each margin gains). Writes docs/research/reach/summary.json and <leader>_poses.csv.

    python3 docs/research/reach/analyse.py
"""
import csv, glob, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); RUNS = os.path.join(HERE, "runs")
LEADERS = ("pin-knee", "raglan", "knuckle", "spine")


def load(tag):
    p = os.path.join(RUNS, f"{tag}.json")
    if not os.path.exists(p): return None
    d = json.load(open(p)); d["R"] = [dict(zip(d["cols"], r)) for r in d["rows"]]; return d


def pct(a, q):
    a = [x for x in a if x is not None]
    return round(float(np.percentile(a, q)), 4) if a else None


def main():
    out = {}
    for L in LEADERS:
        base = load(f"{L}_m10")
        if base is None: continue
        o = dict(model=base["model"], corrected=base["corrected"], window=base["window"], seats=base["seats"], summary=base["summary"],
                 th_ws_pct=base["th_ws_pct"], mode=base["mode"], secs=base["secs"])
        with open(os.path.join(HERE, f"{L}_poses.csv"), "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(base["cols"])
            for r in base["rows"]: w.writerow([";".join(x) if isinstance(x, list) else x for x in r])
        # conditioning over the taken poses of the base run
        tk = [r for r in base["R"] if r["taken"]]
        o["taken_conditioning"] = dict(smin_min=pct([r["smin"] for r in tk], 0), smin_p5=pct([r["smin"] for r in tk], 5),
                                       smin_med=pct([r["smin"] for r in tk], 50),
                                       mu_min=min((min(r["mu"], 180 - r["mu"]) for r in tk if r["mu"] is not None), default=None))
        sens = {}
        for tag in (f"{L}_m7", f"{L}_m5", f"{L}_m2", f"{L}_m7_refit", f"{L}_m5_refit"):
            d = load(tag)
            if d is None: continue
            gained = [r for r, b in zip(d["R"], base["R"]) if r["taken"] and not b["taken"]]
            lost = [r for r, b in zip(d["R"], base["R"]) if b["taken"] and not r["taken"]]
            gws = [r for r in gained if r["kind"] == "ws"]
            sens[tag] = dict(window=d["window"], corrected=d["corrected"], fit_fast=d["fit_fast"],
                             d_reach=round(d["corrected"]["reach"] - base["corrected"]["reach"], 4),
                             d_gap=round(d["corrected"]["gap"] - base["corrected"]["gap"], 2),
                             gained_ws=len(gws), gained_ws_overhead=sum("overhead" in r["groups"] for r in gws),
                             gained_clip=sum(r["kind"] == "clip" for r in gained), lost_ws=sum(r["kind"] == "ws" for r in lost),
                             lost_clip=sum(r["kind"] == "clip" for r in lost),
                             gained_smin=dict(min=pct([r["smin"] for r in gained], 0), med=pct([r["smin"] for r in gained], 50)),
                             gained_mu=dict(min=min((min(r["mu"], 180 - r["mu"]) for r in gained if r["mu"] is not None), default=None),
                                            med=pct([min(r["mu"], 180 - r["mu"]) for r in gained if r["mu"] is not None], 50)),
                             gained_rate_x=None if not gained else round(1 / max(1e-6, pct([r["smin"] for r in gained], 0)), 2),
                             summary_ws=d["summary"]["ws"], summary_overhead=d["summary"]["ws_overhead"])
        o["margin"] = sens
        out[L] = o
        print(L, json.dumps(dict(corrected=o["corrected"], window=o["window"], ws=o["summary"]["ws"], over=o["summary"]["ws_overhead"],
                                 across=o["summary"]["ws_across"], behind=o["summary"]["ws_behind"], clip=o["summary"]["clip"],
                                 cond=o["taken_conditioning"])), flush=True)
        for k, v in sens.items():
            print("   ", k, json.dumps({kk: v[kk] for kk in ("window", "d_reach", "d_gap", "gained_ws", "gained_ws_overhead", "lost_ws", "lost_clip", "gained_smin", "gained_mu")}))
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
