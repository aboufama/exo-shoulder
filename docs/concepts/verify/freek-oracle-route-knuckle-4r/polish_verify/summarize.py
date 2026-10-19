"""summary of the independent polish verification: claims + paired comparisons (alignment_paired.compare_sets)"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
out = dict(claims={}, paired={})
for f in sorted(os.listdir(HERE)):
    if f.endswith(".json") and not f.endswith("_perpose.json") and f != "summary.json" and f != "heldcheck.json":
        d = json.load(open(os.path.join(HERE, f))); c = d["connected"]; sr = d["stop_refusal"]; mm = d["member_margins"]
        out["claims"][f[:-5]] = dict(gap=d["gap"], static=d["static"]["gap"], recomputed=d["recomputed"]["gap"], near=d["near"], reach=c["reach"], follow=c["follow"],
                                     ib14=c["inband14"], contact=c["contact"], contact_poses=d["contact_poses"], depth=d["contact_depth_mm"], overhead=d["overhead140_ws"],
                                     kin_dropped=c["dropped"], islands=c["islands"], contact_aware=d["contact_aware"], member_margins=mm,
                                     q3own_engaged=d["j3stop"].get("q3own_engaged"), engaged=d["j3stop"].get("engaged"),
                                     refused=sr["refused"], refused_kit_contacts=sr["kit_contacts"], gap_refusals_as_contacts=sr["gap_refusals_as_contacts"],
                                     priced=d["priced"], secs=d["secs"])


def pp(name):
    p = os.path.join(HERE, f"{name}_perpose.json")
    return json.load(open(p))["poses"] if os.path.exists(p) else None


def CS(a, b):
    try: return AP.compare_sets(a, b)
    except SystemExit as e: return dict(error=str(e))


for prot in ("envh_held", "fit60_held", "fit60_bench"):
    a, b = pp(f"pick1_{prot}"), pp(f"VER_{prot}")
    if a and b: out["paired"][f"pick1_vs_VER_{prot}"] = CS(a, b)
for prot, wear in (("fit60_held", "held"), ("fit60_bench", "bench")):
    a = pp(f"VER_{prot}"); f = os.path.join(REM, f"freek-oracle-route-knuckle-4r_{wear}_perpose.json")
    if a and os.path.exists(f): out["paired"][f"VER_{prot}_vs_on_file_verified_dump"] = CS(a, json.load(open(f))["poses"])
    a = pp(f"pick1_{prot}")
    if a and os.path.exists(f): out["paired"][f"pick1_{prot}_vs_VER_verified_dump"] = CS(a, json.load(open(f))["poses"])
    for k in ("pick1",):
        a = pp(f"{k}_{prot}"); f2 = os.path.join(REPO, "docs", "research", "freek_env_polish", "local", f"claim_{k}_{prot}_perpose.json")
        if a and os.path.exists(f2): out["paired"][f"{k}_{prot}_vs_polisher_dump"] = CS(a, json.load(open(f2))["poses"])
for k in ("pick1", "VER"):
    a = pp(f"{k}_envh_held"); f2 = os.path.join(REPO, "docs", "research", "freek_env_polish", "local", f"claim_{k}_env_held_perpose.json")
    if a and os.path.exists(f2): out["paired"][f"{k}_envh_held_vs_polisher_dump"] = CS(a, json.load(open(f2))["poses"])
json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)
for k, v in out["claims"].items(): print(k, json.dumps({kk: v[kk] for kk in ("gap", "static", "recomputed", "near", "contact_poses", "depth", "overhead", "kin_dropped", "contact_aware", "member_margins", "q3own_engaged", "refused", "refused_kit_contacts", "gap_refusals_as_contacts")}, default=float))
for k, v in out["paired"].items(): print(k, json.dumps({kk: v.get(kk) for kk in ("gap_A", "gap_B", "diff", "boot", "discordant", "error")}, default=float))
