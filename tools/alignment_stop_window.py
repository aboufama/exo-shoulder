"""Alignment probe: how a claim's bench and held-out gaps move as a J3 hard stop is moved INWARD across the interval the
fit bench cannot see (auditor, 2026-10-17). Read-only: no model runs.

Inputs (all on file): the claim's per-pose dumps (docs/alignment/remeasure/<id>_{bench,held}_perpose.json, from
tools/alignment_paired.py dump) and a per-pose q3' file with the same pose indices (e.g. the red team's
docs/research/conecut_mechanism/stop_geo.json: keys bench110 / held, each [{i, q3p, ...}]).
Why this is exact inside the fit-flat interval: when no fit-bench pose and no fit-clip frame has q3' between the old and
the new stop, the fit (Bench(60,160) fast) and therefore the frozen shape are identical, so the only change on the
exact / held benches is that poses with q3' in [old stop, new stop) are stopped (not evaluated, not taken, no contact).
Moving the stop OUTWARD admits stopped poses whose metal was never measured: that needs a re-wear, not this probe.

    python3 tools/alignment_stop_window.py <id> <q3p.json> <current J3MIN> <lo> <hi> [out.json]
"""
import json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP


def main(rid, qfile, cur, lo, hi, out=None):
    g = json.load(open(qfile)); res = {}
    for w, key in (("bench", "bench110"), ("held", "held")):
        P = json.load(open(os.path.join(REPO, "docs", "alignment", "remeasure", f"{rid}_{w}_perpose.json")))["poses"]
        G = {p["i"]: p for p in g[key]}
        bad = sum(1 for p in P if p["i"] in G and G[p["i"]]["kind"] != p["kind"])
        rows = []
        for j in np.round(np.arange(lo, hi + 1e-9, 0.1), 2):
            Q = []
            for p in P:
                q = dict(p); q3 = G.get(p["i"], {}).get("q3p")
                if q3 is not None and p["ev"] and j > q3 >= cur: q.update(ev=False, taken=False, contact=False)
                Q.append(q)
            gp = AP.gap_parts(Q); rows.append(dict(J3MIN=float(j), gap=gp["gap"], ws_taken=gp["ws_taken"], contact_poses=gp["contact_poses"]))
        res[w] = dict(claim_recomputed=AP.gap_parts(P)["gap"], kind_mismatches=bad, sweep=rows)
    B = np.array([r["gap"] for r in res["bench"]["sweep"]]); H = np.array([r["gap"] for r in res["held"]["sweep"]])
    res["summary"] = dict(id=rid, current_J3MIN=cur, window=[lo, hi], bench_min=float(B.min()), bench_max=float(B.max()), bench_mean=round(float(B.mean()), 2),
                          held_min=float(H.min()), held_max=float(H.max()), held_mean=round(float(H.mean()), 2), q3p_file=os.path.relpath(qfile, REPO))
    print(json.dumps(res["summary"]))
    if out: json.dump(res, open(out, "w"), indent=1)
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], float(a[2]), float(a[3]), float(a[4]), a[5] if len(a) > 5 else None)
