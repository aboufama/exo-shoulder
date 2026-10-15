"""Where in the arm's range does a built design work? From <design>/judge/workspace.json (R16): share of poses passing
per (plane of elevation, elevation) cell, over all humeral rotations in that cell. For the dashboard heatmap.
    python3 tools/coverage_map.py <design id> [...] > coverage.json"""
import json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); rows = []
for des in sys.argv[1:]:
    W = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", des, "judge", "workspace.json")))
    for r in W["per_pose"]:
        pl, el = r["p"][0], r["p"][1]; ok = bool(r["closes"] and r["body_mm"] is not None and r["body_mm"] <= W["tol_body_mm"] and r["parts_mm"] <= W["tol_parts_mm"])
        why = "passes" if ok else ("chain can't close" if not r["closes"] else ("body contact" if r["body_mm"] > W["tol_body_mm"] else "links collide"))
        rows.append(dict(design=des, plane=float(pl), elev=float(el), ok=ok, why=why))
cells = {}
for r in rows:
    k = (r["design"], 30 * round(r["plane"] / 30), 30 * round(r["elev"] / 30)); c = cells.setdefault(k, [0, 0]); c[0] += r["ok"]; c[1] += 1
out = [dict(design=d, plane=p, elev=e, share=round(a / n, 3), poses=n) for (d, p, e), (a, n) in sorted(cells.items())]
json.dump(out, sys.stdout, indent=1)
