"""Alignment instrument (new, 2026-10-17): pose-class breakdown of two per-pose dumps on the same bench (A vs B) - where
does A's gain come from? Reads docs/alignment/remeasure/<id>_<wear>_perpose.json (tools/alignment_paired.py dump or
tools/alignment_paired_params.py), checks the two dumps list the same poses, and reports taken / contact counts by
elevation band, the discordant poses by elevation / axial / plane, overhead (elev >= 140) and raised-arm (elev >= 90)
reach, taken poses with metal < 2 mm and contact depths. Read-only.

    python3 tools/alignment_pose_classes.py <id A> <id B> [out.json]
"""
import json, os, sys
from collections import Counter, defaultdict
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "alignment", "remeasure") + os.sep
a_id, b_id = sys.argv[1], sys.argv[2]
out = {}
for w in ("bench", "held"):
    try:
        A = json.load(open(R + f"{a_id}_{w}_perpose.json")); B = json.load(open(R + f"{b_id}_{w}_perpose.json"))
    except FileNotFoundError as e:
        print(w, "missing", e); continue
    PA, PB = A["poses"], B["poses"]
    assert len(PA) == len(PB)
    for x, y in zip(PA, PB):
        assert (x["kind"], x["plane"], x["elev"], x["axial"]) == (y["kind"], y["plane"], y["elev"], y["axial"]), (x, y)
    ws = [(x, y) for x, y in zip(PA, PB) if x["kind"] == "ws"]
    def eb(e):
        e = e or 0
        return "<60" if e < 60 else "60-90" if e < 90 else "90-120" if e < 120 else "120-140" if e < 140 else ">=140"
    tab = defaultdict(lambda: Counter())
    onlyA, onlyB = [], []
    for x, y in ws:
        k = eb(x["elev"]); tab[k]["n"] += 1; tab[k]["A"] += x["taken"]; tab[k]["B"] += y["taken"]
        tab[k]["Ac"] += x["contact"]; tab[k]["Bc"] += y["contact"]
        if x["taken"] and not y["taken"]: onlyA.append(x)
        if y["taken"] and not x["taken"]: onlyB.append(y)
    def lst(L): return [dict(plane=p["plane"], elev=p["elev"], axial=p["axial"], minA=p["min_mm"]) for p in L]
    ax = lambda L: Counter(("|ax|>=120" if abs(p["axial"] or 0) >= 120 else "|ax|<120") for p in L)
    pl = lambda L: Counter((p["plane"]) for p in L)
    cA = [x for x, y in zip(PA, PB) if x["contact"]]; cB = [y for x, y in zip(PA, PB) if y["contact"]]
    nA2 = sum(1 for x in PA if x["taken"] and x["min_mm"] is not None and x["min_mm"] < 2)
    nB2 = sum(1 for y in PB if y["taken"] and y["min_mm"] is not None and y["min_mm"] < 2)
    ovA = sum(1 for x, y in ws if (x["elev"] or 0) >= 140 and x["taken"]); ovB = sum(1 for x, y in ws if (y["elev"] or 0) >= 140 and y["taken"]); ovN = sum(1 for x, y in ws if (x["elev"] or 0) >= 140)
    raised = lambda P: sum(1 for p in P if p["kind"] == "ws" and (p["elev"] or 0) >= 90 and p["taken"]); raisedN = sum(1 for x, y in ws if (x["elev"] or 0) >= 90)
    r = dict(n_ws=len(ws), taken_A=sum(x["taken"] for x, y in ws), taken_B=sum(y["taken"] for x, y in ws),
             only_A=len(onlyA), only_B=len(onlyB), only_A_by_elev=dict(Counter(eb(p["elev"]) for p in onlyA)), only_B_by_elev=dict(Counter(eb(p["elev"]) for p in onlyB)),
             only_A_axial=dict(ax(onlyA)), only_B_axial=dict(ax(onlyB)), only_A_plane=dict(pl(onlyA)), only_B_plane=dict(pl(onlyB)),
             contact_A=dict(n=len(cA), sum_mm=round(sum(-p["min_mm"] for p in cA), 2), max_mm=round(max([-p["min_mm"] for p in cA] or [0]), 2), deepest=[dict(kind=p["kind"], plane=p["plane"], elev=p["elev"], axial=p["axial"], mm=p["min_mm"]) for p in sorted(cA, key=lambda p: p["min_mm"])[:3]]),
             contact_B=dict(n=len(cB), sum_mm=round(sum(-p["min_mm"] for p in cB), 2), max_mm=round(max([-p["min_mm"] for p in cB] or [0]), 2)),
             taken_lt2mm_A=nA2, taken_lt2mm_B=nB2, overhead140=dict(n=ovN, A=ovA, B=ovB), raised90=dict(n=raisedN, A=raised(PA), B=raised(PB)),
             by_elev={k: dict(v) for k, v in sorted(tab.items())}, recomputed_A=A.get("recomputed"), recomputed_B=B.get("recomputed"),
             frozen_A=A.get("frozen"), only_A_list=lst(onlyA)[:60], only_B_list=lst(onlyB)[:60])
    out[w] = r
    print("==", w, json.dumps({k: v for k, v in r.items() if not k.endswith("_list")}, default=float))
if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
