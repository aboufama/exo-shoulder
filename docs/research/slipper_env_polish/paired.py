"""paired per-pose comparison (tools/alignment_paired.compare_sets: paired bootstrap within kind) of the polish claims'
dumps against the verified config's dumps on the SAME protocol and reading:
  * claim_<cfg>_<fit>_<wear>_<r>_perpose.json vs claim_BEST_<fit>_<wear>_<r>_perpose.json (farm/ or local/);
  * unpriced fit60 claims also vs the lead's own remeasure dumps (docs/alignment/remeasure/slipper-nose-knuckle-3r_<wear>_perpose.json).
    python3 docs/research/slipper_env_polish/paired.py [out.json]"""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP                                 # noqa: E402

D = {}
for d in ("farm", "local"):
    for f in glob.glob(os.path.join(HERE, d, "claim_*_perpose.json")):
        nm = os.path.basename(f)[6:-13]
        D.setdefault(nm, f)
out = {}
for nm, f in sorted(D.items()):
    cfg, rest = nm.split("_", 1)
    if cfg == "BEST": continue
    A = json.load(open(f))["poses"]
    if "BEST_" + rest in D:
        B = json.load(open(D["BEST_" + rest]))["poses"]
        r = AP.compare_sets(A, B, 4000); out[f"{nm}__vs__BEST_{rest}"] = r
        print(f"{nm} vs BEST_{rest}: diff {r['diff']} (A {r['gap_A']} B {r['gap_B']}) CI90 {r['boot']['ci90']} P(A better) {r['boot']['p_A_better']} disc {r['discordant']}")
    fit, wear, rd = rest.split("_")
    if fit == "fit60" and rd == "u":
        ref = os.path.join(AP.REM, f"slipper-nose-knuckle-3r_{wear}_perpose.json")
        if os.path.exists(ref):
            B = json.load(open(ref))["poses"]
            try:
                r = AP.compare_sets(A, B, 4000); out[f"{nm}__vs__lead_remeasure_{wear}"] = r
                print(f"{nm} vs lead remeasure {wear}: diff {r['diff']} (A {r['gap_A']} B {r['gap_B']}) CI90 {r['boot']['ci90']} P(A better) {r['boot']['p_A_better']}")
            except SystemExit as e: print(nm, "vs lead remeasure:", e)
if len(sys.argv) > 1: json.dump(out, open(sys.argv[1], "w"), indent=1)
