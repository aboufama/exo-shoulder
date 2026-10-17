"""paired per-pose comparison of this row's dumps (docs/research/inband_drive/farm/claimA/*_perpose.json, written by
tools/alignment_paired.py dump --out) against a reference's dumps on file (docs/alignment/remeasure/<ref>_<wear>_perpose.json,
read only), with tools/alignment_paired.compare_sets (paired bootstrap within kind) + a pose-class split of the
discordant poses (low arm elev < 60 with |axial| >= 120, elev 60-140, overhead >= 140).
    python3 docs/research/inband_drive/paired.py <dir with our dumps> [ref id] [out.json]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP                                 # noqa: E402

d = sys.argv[1]; ref = sys.argv[2] if len(sys.argv) > 2 else "slipper-nose-knuckle-3r"; outp = sys.argv[3] if len(sys.argv) > 3 else None
ID = "inband-rssr-knuckle-3r"; res = dict(A=ID, B=ref, note="diff = gap A - gap B (negative: A better)")


def cls(p):
    e, a = p["elev"], abs(p["axial"])
    return "low_arm_rot" if e < 60 and a >= 120 else "low_arm" if e < 60 else "mid_60_140" if e < 140 else "overhead_140"


PA_all, PB_all = [], []
for wear in ("bench", "held"):
    A = json.load(open(os.path.join(d, f"{ID}_{wear}_perpose.json")))["poses"]
    B = json.load(open(os.path.join(AP.REM, f"{ref}_{wear}_perpose.json")))["poses"]
    r = AP.compare_sets(A, B, 4000); split = {}
    for pa, pb in zip(A, B):
        c = cls(pa); s = split.setdefault(c, dict(A_only_taken=0, B_only_taken=0, A_contact=0, B_contact=0, A_contact_depth=0.0, B_contact_depth=0.0))
        if pa["kind"] == "ws" and pa["taken"] and not pb["taken"]: s["A_only_taken"] += 1
        if pb["kind"] == "ws" and pb["taken"] and not pa["taken"]: s["B_only_taken"] += 1
        for k_, p in (("A", pa), ("B", pb)):
            if p["contact"]:
                s[f"{k_}_contact"] += 1; s[f"{k_}_contact_depth"] = round(s[f"{k_}_contact_depth"] - min(p["min_mm"], p["cmin"] if p["cmin"] is not None else 1e9), 3)
    r["by_class"] = split; res[wear] = r
    tag = lambda P, w: [dict(p, i=f"{w}:{p['i']}") for p in P]
    PA_all += tag(A, wear); PB_all += tag(B, wear)
res["pooled_bench_plus_held"] = AP.compare_sets(PA_all, PB_all, 4000)
if outp: json.dump(res, open(outp, "w"), indent=1)
print(json.dumps(res, indent=1))
