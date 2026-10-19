#!/usr/bin/env python3
"""Near-touch, reach and closest-metal readings straight from per-pose dumps (new audit instrument, 2026-10-18; read-only).

The per-pose dumps (docs/alignment/remeasure/<id>_<wear>_perpose.json, written by verifiers / tools/alignment_paired.py)
carry, per pose: kind, plane / elev / axial, evaluated, min metal (min_mm) and the model's extra walls (cmin), taken,
contact, clip sample counts. This tool reads them for several designs on the same bench and reports, per wear:
  plain gap (recomputed with alignment_paired.gap_parts, must reproduce the dump's own number), the gap with a taken pose
  whose metal min(min_mm, cmin) < 1 / 2 / 3 mm counted as contact (the near-touch reading the audit uses), the number of
  such poses, overhead (ws elev >= 150) and raised-arm (ws elev >= 90) takes, the closest taken metal, and the poses
  where the designs differ (taken by one only, or under 1 mm in one only). It never changes a score.

    python3 tools/alignment_neartouch_dumps.py <id A> <id B> [<id C> ...] [--out PATH]
"""
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP  # noqa: E402


def eff(r):
    if r.get("min_mm") is None: return None
    return min(r["min_mm"], r["cmin"] if r.get("cmin") is not None else 9e9)


def read(rid, wear):
    p = os.path.join(REM, f"{rid}_{wear}_perpose.json")
    if not os.path.exists(p): return None
    d = json.load(open(p)); P = d["poses"]; base = AP.gap_parts(P)
    taken = [r for r in P if r["taken"]]; ws = [r for r in P if r["kind"] == "ws"]
    out = dict(src=os.path.relpath(p, REPO), gap=base["gap"], dump_gap=(d.get("recomputed") or d.get("frozen") or {}).get("gap"),
               reach=base["reach"], inband14=base["inband14"], contact=base["contact"],
               min_metal=round(min(eff(r) for r in taken), 3) if taken else None,
               overhead150=[sum(1 for r in ws if r["elev"] >= 150 and r["taken"]), sum(1 for r in ws if r["elev"] >= 150)],
               raised90=[sum(1 for r in ws if r["elev"] >= 90 and r["taken"]), sum(1 for r in ws if r["elev"] >= 90)])
    for thr in (1.0, 2.0, 3.0):
        Q = []
        for r in P:
            q = dict(r)
            if r["taken"] and eff(r) is not None and eff(r) < thr: q["taken"] = False; q["contact"] = True
            Q.append(q)
        out[f"gap_near{thr:g}"] = AP.gap_parts(Q)["gap"]; out[f"near{thr:g}_poses"] = sum(1 for r in taken if eff(r) < thr)
    ov = [eff(r) for r in taken if r["elev"] >= 140]
    out["overhead140_min_metal_p10"] = round(float(np.percentile(ov, 10)), 2) if ov else None
    out["under1"] = sorted([[r["i"], r["kind"], r["plane"], round(r["elev"], 1), round(r["axial"], 1), round(eff(r), 3)] for r in taken if eff(r) < 1.0],
                           key=lambda x: x[5])
    return out, P


def main(argv):
    ids = [a for a in argv if not a.startswith("--")]
    outp = argv[argv.index("--out") + 1] if "--out" in argv else None
    if outp in ids: ids.remove(outp)
    res = dict(ids=ids, rule="near-touch: a taken pose with min(min_mm, cmin) < N mm counted as contact (report only, user decision 3)")
    for wear in ("bench", "held"):
        R = {}; PP = {}
        for rid in ids:
            x = read(rid, wear)
            if x: R[rid], PP[rid] = x
        if not R: continue
        a = ids[0]; diffs = {}
        for b in ids[1:]:
            if a not in PP or b not in PP or len(PP[a]) != len(PP[b]): continue
            A, B = PP[a], PP[b]; dd = dict(taken_A_only=[], taken_B_only=[], under1_A_only=[], under1_B_only=[], contact_A_only=[], contact_B_only=[])
            for ra, rb in zip(A, B):
                tag = [ra["i"], ra["kind"], ra["plane"], round(ra["elev"], 1), round(ra["axial"], 1)]
                if ra["taken"] and not rb["taken"]: dd["taken_A_only"].append(tag)
                if rb["taken"] and not ra["taken"]: dd["taken_B_only"].append(tag)
                if ra["contact"] and not rb["contact"]: dd["contact_A_only"].append(tag)
                if rb["contact"] and not ra["contact"]: dd["contact_B_only"].append(tag)
                ea, eb = eff(ra), eff(rb)
                if ra["taken"] and rb["taken"] and ea is not None and eb is not None:
                    if ea < 1.0 <= eb: dd["under1_A_only"].append(tag + [round(ea, 3), round(eb, 3)])
                    if eb < 1.0 <= ea: dd["under1_B_only"].append(tag + [round(ea, 3), round(eb, 3)])
            diffs[f"{a}_vs_{b}"] = dd
        res[wear] = dict(designs=R, diffs=diffs)
    s = json.dumps(res, indent=1, default=float)
    if outp: open(outp, "w").write(s)
    print(s)


if __name__ == "__main__":
    main(sys.argv[1:])
