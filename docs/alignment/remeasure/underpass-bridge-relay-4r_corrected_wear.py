"""Alignment auditor (2026-10-18): what the wearer gets from the row's VERIFIED number (v_gap 20.60 bench / 24.33 held:
the corrected bridge A_up1.2, R_under 84.222, re-scored with the verifier's X1 clash check).

No model is run. It reads the verifier's per-pose dumps of the corrected wear (verifier_fix*_A_up1.2_perpose.json, which
recompute the model-rule 19.74 / 23.45) and applies the verifier's own X1 lost set (xcheck extra_jam_rows: a taken pose
with a new jam -> lost), so the derived dump reproduces 20.60 / 24.33. Writes those derived dumps in the
tools/alignment_paired.py format (so tools/alignment_audit.py contact_depth can read the claim's depths) and a summary:
overhead / raised-arm reach, near-touch gaps, poses with metal < 1 / 2 / 3 mm, contact depths, and the same numbers for
the 3-joint lead conecut-knee-knuckle-3r from its auditor dumps.

    python3 docs/alignment/remeasure/underpass-bridge-relay-4r_corrected_wear.py
"""
import json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP  # noqa: E402

V = os.path.join(REPO, "docs", "concepts", "verify", "underpass-bridge-relay-4r")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
ID = "underpass-bridge-relay-4r"; LEAD = "conecut-knee-knuckle-3r"


def lost_set(xfile):
    x = json.load(open(os.path.join(V, xfile)))["A_up1.2"]["xcheck"]
    return sorted(r["i"] for r in x["extra_jam_rows"] if r["metal_min"] >= 0 and any(j[0] != "skin" for j in r["jam"])), x["rescored"]


def near(poses, t, crown=True):
    P = []
    for p in poses:
        q = dict(p)
        if q["taken"]:
            m = q["min_mm"]
            if crown and q.get("cmin") is not None: m = min(m, q["cmin"])
            if m < t: q["taken"] = False; q["contact"] = True
        P.append(q)
    return AP.gap_parts(P)["gap"]


def stats(poses):
    tk = [p for p in poses if p["taken"]]
    mm = lambda p: min(p["min_mm"], p["cmin"]) if p.get("cmin") is not None else p["min_mm"]
    ws = [p for p in poses if p["kind"] == "ws"]
    oh = [p for p in ws if p["elev"] >= 140]; ra = [p for p in ws if p["elev"] >= 90]
    con = sorted([p for p in poses if p["contact"]], key=lambda p: p["min_mm"])
    return dict(gap=AP.gap_parts(poses), near1=near(poses, 1.0), near2=near(poses, 2.0), near2_scored_only=near(poses, 2.0, crown=False),
                overhead=[sum(p["taken"] for p in oh), len(oh)], raised=[sum(p["taken"] for p in ra), len(ra)],
                taken=len(tk), lt1=sum(mm(p) < 1 for p in tk), lt2=sum(mm(p) < 2 for p in tk), lt3=sum(mm(p) < 3 for p in tk),
                lt2_scored_only=sum(p["min_mm"] < 2 for p in tk),
                contacts=len(con), depth_sum_mm=round(-sum(p["min_mm"] for p in con), 2),
                deepest=[dict(i=p["i"], kind=p["kind"], pose=[p["plane"], p["elev"], p["axial"]], mm=p["min_mm"]) for p in con[:4]],
                deeper3=sum(p["min_mm"] < -3 for p in con))


def main():
    out = dict(id=ID, note="derived from the verifier's corrected-bridge dumps + its X1 lost set; no model run")
    for wear, dump, xf in (("bench", "verifier_fix_A_up1.2_perpose.json", "verifier_fix.json"),
                           ("held", "verifier_fixheld_A_up1.2_perpose.json", "verifier_fixheld.json")):
        d = json.load(open(os.path.join(V, dump))); lost, resc = lost_set(xf)
        P = []
        for p in d["poses"]:
            q = dict(p)
            if q["i"] in lost and q["taken"]:      # the verifier's re-score sets B.res None: lost, and out of the contact denominator
                q["taken"] = False; q["ev"] = False; q["x1_lost"] = True; q.pop("ns", None); q.pop("nib", None)
            P.append(q)
        g = AP.gap_parts(P)
        dd = dict(id=ID, wear="bench(110,360)" if wear == "bench" else "held", poses=P, recomputed=g, frozen=dict(gap=g["gap"], derived=True), derived=True,
                  source=f"docs/concepts/verify/{ID}/{dump} + {xf} A_up1.2 xcheck lost {lost}", verifier_rescored=resc["wear"]["gap"],
                  params=d.get("params"), exact=True)
        json.dump(dd, open(os.path.join(REM, f"{ID}_{wear}_perpose.json"), "w"), default=float)
        out[wear] = dict(lost=lost, recomputed_gap=g["gap"], verifier_gap=resc["wear"]["gap"], model_rule=stats(d["poses"]), x1=stats(P))
    for wear in ("bench", "held"):
        f = os.path.join(REM, f"{LEAD}_{wear}_perpose.json")
        if os.path.exists(f): out[f"lead_{wear}"] = stats(json.load(open(f))["poses"])
    json.dump(out, open(os.path.join(REM, f"{ID}_corrected_wear.json"), "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
