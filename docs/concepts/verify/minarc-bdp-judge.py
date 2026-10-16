"""Judge for minarc-stop-knuckle-4r BDp (2026-10-16): combines the two independent lenses and prices the stop tolerance.

Reads the lenses' raw outputs (never their prose):
  remeasure lens   docs/concepts/verify/minarc-bdp/farm/wear_{bench,held}_{m5,H1_m5}.json, minarc-bdp/wear_bench_m10.json,
                   minarc-bdp/conn_taken_m5.json            (its own harness, docs/concepts/verify/minarc-bdp-remeasure.py)
  buildability     .cache/minarc_bdp_build/{pinch_bench,pinch_held,equil,demand}.json   (git-ignored; optional here -
                   its numbers are copied into the ruling when present)
and the judge's own farm runs of the remeasure harness with the stops moved by a machining tolerance:
  docs/concepts/verify/minarc-bdp-judge/wear_{bench,held}_m5p5.json, wear_bench_m6.json
  (CB_FOLD_MARGIN 5.5 / 6: both J2 stops and the all-state rule at 5.5 / 6 deg; the shape is refit at that margin).

Checks: every gap is recomputed from its components with tools/concept_bench.gap_of (the bench's own formula); the
lenses must agree on the margin-5 frozen exact bench / held-out numbers; the own-state J1-J3 margin must be >= 5 with 0
poses under 5; continuity must drop 0 taken poses. Ruling: CONFIRMED only if neither lens refutes and the checks pass.

    python3 docs/concepts/verify/minarc-bdp-judge.py      -> docs/concepts/verify/minarc-bdp-judge/ruling.json
"""
import json, os, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
from concept_bench import gap_of                                    # noqa: E402

V = os.path.join(REPO, "docs", "concepts", "verify")
J = os.path.join(V, "minarc-bdp-judge")
B2 = os.path.join(REPO, ".cache", "minarc_bdp_build")


def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None


def score(g): return round(100.0 * (1.0 - g / 275.0), 2)


def regap(r):
    """the bench's own gap from a run's components (in-band14, follow, reach, contact)"""
    return gap_of(r["inband14"], r["follow"], r["reach"], r.get("contact", 0.0))


def summary(d, tag):
    if d is None: return None
    f, ex = d.get("final") or d.get("corrected"), d.get("extra") or {}
    out = dict(tag=tag, margin=d.get("fold_margin"), fit_fast=d["fit"]["gap"], gap=f["gap"], regap=regap(f),
               score=score(f["gap"]), reach=f["reach"], follow=f["follow"], inband14=f["inband14"],
               inband10=f.get("inband10"), contact=f["contact"], gap_near1=(d.get("corrected_near") or f).get("gap_near1"),
               near1_poses=(d.get("corrected_near") or f).get("near1_poses"), min_mm=(d.get("corrected_near") or f).get("min_mm"),
               dropped_unconnected=(d.get("connected") or f).get("dropped_unconnected"))
    th = ex.get("th_margin_own_state")
    if th: out.update(min_th=th["min"], lt5=th["lt5"], lt10=th["lt10"])
    elif ex.get("th_margin_min") is not None: out.update(min_th=ex["th_margin_min"])
    if ex.get("q2_slot"): out["q2_slot"] = ex["q2_slot"].get("stops")
    if ex.get("K"): out["dK_range"] = ex["K"].get("dK_range")
    return out


def main():
    R = {}
    R["bench_m5"] = summary(load(os.path.join(V, "minarc-bdp", "farm", "wear_bench_m5.json")), "remeasure lens, bench, margin 5")
    R["held_m5"] = summary(load(os.path.join(V, "minarc-bdp", "farm", "wear_held_m5.json")), "remeasure lens, held out, margin 5")
    R["h1_bench_m5"] = summary(load(os.path.join(V, "minarc-bdp", "farm", "wear_bench_H1_m5.json")), "H1, bench, margin 5")
    R["h1_held_m5"] = summary(load(os.path.join(V, "minarc-bdp", "farm", "wear_held_H1_m5.json")), "H1, held out, margin 5")
    R["bench_m10"] = summary(load(os.path.join(V, "minarc-bdp", "wear_bench_m10.json")), "remeasure lens, bench, margin 10")
    R["bench_m5p5"] = summary(load(os.path.join(J, "wear_bench_m5p5.json")), "judge, bench, stops at 5.5 (tolerance)")
    R["held_m5p5"] = summary(load(os.path.join(J, "wear_held_m5p5.json")), "judge, held out, stops at 5.5 (tolerance)")
    R["bench_m6"] = summary(load(os.path.join(J, "wear_bench_m6.json")), "judge, bench, stops at 6")
    R["bench_m5_B34"] = summary(load(os.path.join(J, "wear_bench_m5_B34.json")), "judge, bench, J2 stops 5.0, K stop B dK 34.47")
    R["bench_m5p5_B34"] = summary(load(os.path.join(J, "wear_bench_m5p5_B34.json")), "judge, bench, J2 stops 5.5, K stop B dK 34.47")
    R["held_m5p5_B34"] = summary(load(os.path.join(J, "wear_held_m5p5_B34.json")), "judge, held out, J2 stops 5.5, K stop B dK 34.47")
    ct = load(os.path.join(V, "minarc-bdp", "conn_taken_m5.json"))
    if ct: R["conn_taken_m5"] = dict(nodes=ct["grid"]["nodes"], connected=ct["grid"]["connected"], islands=ct["grid"]["islands"],
                                     edges=f'{ct["edges"]["passed"]}/{ct["edges"]["tested"]}')
    # buildability lens (claim's own run() path) - optional, git-ignored raw
    pb, ph, eq = (load(os.path.join(B2, n + ".json")) for n in ("pinch_bench", "pinch_held", "equil"))
    if pb: R["lens2_bench"] = dict(pb["model_run"], regap=regap(pb["model_run"]))
    if ph: R["lens2_held"] = dict(ph["model_run"], regap=regap(ph["model_run"]))
    if eq: R["lens2_equil"] = dict(scan=eq["scan"], rule_cut_th=eq["stretched_end"]["rule_cut_th"],
                                   physical_lock_th=eq["stretched_end"]["physical_lock_th"], dK_stopB_deg=eq["dK_stopB_deg"])

    checks = {}
    b, h = R["bench_m5"], R["held_m5"]
    checks["bench_regap_matches"] = abs(b["regap"] - b["gap"]) <= 0.011
    checks["held_regap_matches"] = abs(h["regap"] - h["gap"]) <= 0.011
    if "lens2_bench" in R:
        checks["lenses_agree_bench"] = abs(R["lens2_bench"]["gap"] - b["gap"]) <= 0.011
        checks["lenses_agree_held"] = abs(R["lens2_held"]["gap"] - h["gap"]) <= 0.011
    checks["margin_ge_5_bench"] = b["min_th"] >= 5.0 and b["lt5"] == 0
    checks["margin_ge_5_held"] = h["min_th"] >= 5.0 and h["lt5"] == 0
    checks["continuity_0_dropped"] = b["dropped_unconnected"] == 0 and h["dropped_unconnected"] == 0
    checks["beats_h1_bench"] = b["gap"] < R["h1_bench_m5"]["gap"]
    checks["beats_h1_held"] = h["gap"] < R["h1_held_m5"]["gap"]
    lenses_refuted = {"remeasure": False, "buildability": False}

    # the priced number: margin-5 rule reading; the stop tolerance is a build condition, priced separately
    tol = {}
    if R["bench_m5p5"]:
        tol["bench_m5p5"] = R["bench_m5p5"]["gap"]; tol["bench_cost"] = round(R["bench_m5p5"]["gap"] - b["gap"], 2)
    if R["held_m5p5"]:
        tol["held_m5p5"] = R["held_m5p5"]["gap"]; tol["held_cost"] = round(R["held_m5p5"]["gap"] - h["gap"], 2)
    if R["bench_m6"]: tol["bench_m6"] = R["bench_m6"]["gap"]
    rule_bench = max([b["gap"]] + ([R["lens2_bench"]["gap"]] if "lens2_bench" in R else []))
    rule_held = max([h["gap"]] + ([R["lens2_held"]["gap"]] if "lens2_held" in R else []))
    # priced: a stop that must engage at >= 5 deg is drawn 5.0 +0.5 / -0; its worst built case is the 5.5 reading
    # and K's stop B drawn at the 5.0-deg cut (dK 34.47) - the worst built pairing is J2 at 5.5 with stop B at 34.47
    worst_bench = max([rule_bench] + [R[k]["gap"] for k in ("bench_m5p5", "bench_m5_B34", "bench_m5p5_B34") if R.get(k)])
    worst_held = max([rule_held] + [R[k]["gap"] for k in ("held_m5p5", "held_m5p5_B34") if R.get(k)])
    for k in ("bench_m5_B34", "bench_m5p5_B34", "held_m5p5_B34"):
        if R.get(k): checks[k + "_margin_ge_5"] = R[k]["min_th"] >= 5.0 and R[k]["lt5"] == 0 and R[k]["dropped_unconnected"] == 0
    if R["bench_m5p5"]:
        checks["tolerance_margin_ge_5"] = R["bench_m5p5"]["min_th"] >= 5.0 and R["bench_m5p5"]["lt5"] == 0
        checks["tolerance_continuity_0_dropped"] = R["bench_m5p5"]["dropped_unconnected"] == 0 and R["held_m5p5"]["dropped_unconnected"] == 0
    confirmed = not any(lenses_refuted.values()) and all(checks.values())
    ruling = dict(confirmed=confirmed, v_gap=worst_bench, v_score=score(worst_bench), held_out_gap=worst_held,
                  rule_reading=dict(gap=rule_bench, score=score(rule_bench), held_out_gap=rule_held,
                                    note="both J2 stops at exactly the 5.00-deg rule (both lenses, to the digit)"),
                  priced_mechanism_issues={"K stop B moved to dK 34.5 deg (buildability lens)": 0.0,
                                           "clock-spring rate <= 0.015 N.m/rad, +C1900 (buildability lens)": 0.0,
                                           "J2 stop slot drawn 5.0 +0.5 / -0 deg of J1-J3 margin with K stop B at dK 34.47 "
                                           "(judge; worst built pairing = J2 stops at 5.5, stop B at 34.47)": round(worst_bench - rule_bench, 2)},
                  stop_tolerance=tol, checks=checks, lenses_refuted=lenses_refuted, runs=R)
    os.makedirs(J, exist_ok=True)
    json.dump(ruling, open(os.path.join(J, "ruling.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in ruling.items() if k != "runs"}, indent=1, default=float))
    for k in ("bench_m5", "held_m5", "h1_bench_m5", "h1_held_m5", "bench_m10", "bench_m5p5", "held_m5p5", "bench_m6"):
        if R.get(k): print(k, {x: R[k].get(x) for x in ("gap", "regap", "reach", "inband14", "contact", "gap_near1", "min_th", "lt10", "q2_slot")})


def wear_stopb(wb, dKB, outp):
    """the re-measure lens' wear(), unchanged, with K's stop B moved to dK = dKB (a1max from K's dyad: cos a1max =
    cos bk1 cos bk2 + sin bk1 sin bk2 cos(|psiA| + dKB), psiA from K's closed dyad a1). CB_FOLD_MARGIN sets the J2 stops."""
    import importlib.util, math
    spec = importlib.util.spec_from_file_location("bdp_remeasure", os.path.join(V, "minarc-bdp-remeasure.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    P = json.load(open(mod.PFILE)); d = math.pi / 180
    b1, b2, a1max0 = P["bk1"] * d, P["bk2"] * d, P["a1max"] * d
    cb, sb = math.cos(b1) * math.cos(b2), math.sin(b1) * math.sin(b2)
    psiB0 = math.acos((math.cos(a1max0) - cb) / sb)
    eq = load(os.path.join(B2, "equil.json"))
    psiA = abs(eq["psiA_deg"]) * d if eq else psiB0 - 62.827 * d          # lens 2: psiA -57.465, dK at stop B 62.827
    a1max = math.acos(cb + sb * math.cos(psiA + dKB * d)) / d
    P["a1max"] = round(a1max, 4)
    pf = os.path.join(J, f"params_BDp_stopB{dKB:g}.json"); os.makedirs(J, exist_ok=True)
    json.dump(P, open(pf, "w"), indent=1)
    print(json.dumps(dict(dKB=dKB, a1max=P["a1max"], a1max_was=round(a1max0 / d, 4), psiA_deg=round(psiA / d, 3),
                          dK_stopB_check=round((psiB0 - psiA) / d, 3))), flush=True)
    mod.PFILE = pf
    mod.wear(wb, "BDp", outp)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "wear": wear_stopb(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    else: main()
