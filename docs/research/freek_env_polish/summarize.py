"""summary of the freek-oracle-route-knuckle-4r envh polish: claims table + paired comparisons (alignment_paired.compare_sets)"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP
L = os.path.join(REPO, "docs", "research", "freek_env_polish", "local")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
out = dict(claims={}, paired={})
for f in sorted(os.listdir(L)):
    if f.startswith("claim_") and f.endswith(".json") and not f.endswith("_perpose.json"):
        d = json.load(open(os.path.join(L, f))); s = d["static"]; c = d["connected"]
        out["claims"][f[6:-5]] = dict(gap=d["gap"], near=d["near"], static=s["gap"], reach=c["reach"], follow=c["follow"], ib14=c["inband14"], contact=c["contact"],
                                      contact_poses=d["contact_poses"], depth=d["contact_depth_mm"], overhead=d["overhead140_ws"], dropped=c["dropped"], islands=c["islands"],
                                      th_one=d["margins"]["one_reading_min"], th_one_lt5=d["margins"]["one_lt5"], th_fam=d["margins"]["family_min"], th_fam_lt5=d["margins"]["family_lt5"],
                                      states=d["margins"]["state_counts"], refused=d["stop_refusal"]["refused"], refused_kit_contacts=d["stop_refusal"]["kit_contacts"],
                                      gap_refusals_as_contacts=d["stop_refusal"]["gap_refusals_as_contacts"], q3own_engaged=d["j3stop"].get("q3own_engaged"),
                                      priced={k: round(v, 3) for k, v in d["priced"].items()}, secs=d["secs"])
def CS(a, b):
    try: return AP.compare_sets(a, b)
    except SystemExit as e: return dict(error=str(e), gap_A=None, gap_B=None, diff=None, boot=dict(ci90=None, p_A_better=None), discordant=None)
def pp(name):
    p = os.path.join(L, f"claim_{name}_perpose.json")
    return json.load(open(p))["poses"] if os.path.exists(p) else None
ver_bench = json.load(open(os.path.join(REM, "freek-oracle-route-knuckle-4r_bench_perpose.json")))["poses"]
ver_held60 = json.load(open(os.path.join(REM, "freek-oracle-route-knuckle-4r_held_perpose.json")))["poses"]
lead_bench = json.load(open(os.path.join(REM, "conecut-knee-knuckle-3r_bench_perpose.json")))["poses"]
lead_held = json.load(open(os.path.join(REM, "conecut-knee-knuckle-3r_held_perpose.json")))["poses"]
for k in ("pick1", "pick2", "pick3"):
    a = pp(f"{k}_fit60_bench")
    if a: out["paired"][f"{k}_fit60_bench_vs_VER_verified_bench"] = CS(a, ver_bench); out["paired"][f"{k}_fit60_bench_vs_lead_bench"] = CS(a, lead_bench)
    a = pp(f"{k}_env_held"); b = pp("VER_env_held")
    if a and b: out["paired"][f"{k}_env_held_vs_VER_env_held"] = CS(a, b)
    if a: out["paired"][f"{k}_env_held_vs_VER_fit60_held(cross-protocol)"] = CS(a, ver_held60); out["paired"][f"{k}_env_held_vs_lead_held"] = CS(a, lead_held)
for k in ("pick1", "pick2", "pick3"):
    a = pp(f"{k}_fit60_held"); b = pp("VER_fit60_held") or ver_held60
    if a: out["paired"][f"{k}_fit60_held_vs_VER_fit60_held"] = CS(a, b); out["paired"][f"{k}_fit60_held_vs_lead_held"] = CS(a, lead_held)
b = pp("VER_env_held")
if b: out["paired"]["VER_env_held_vs_VER_fit60_held"] = CS(b, ver_held60)
json.dump(out, open(os.path.join(REPO, "docs", "research", "freek_env_polish", "summary.json"), "w"), indent=1)
for k, v in out["claims"].items(): print(k, json.dumps({kk: v[kk] for kk in ("gap", "near", "static", "contact_poses", "depth", "overhead", "dropped", "th_one", "th_fam", "th_fam_lt5", "refused", "refused_kit_contacts", "gap_refusals_as_contacts", "q3own_engaged")}))
for k, v in out["paired"].items(): print(k, v["gap_A"], v["gap_B"], v["diff"], v["boot"]["ci90"], v["boot"]["p_A_better"], v["discordant"])
