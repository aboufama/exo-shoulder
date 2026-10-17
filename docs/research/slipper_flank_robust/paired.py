"""paired per-pose comparison (tools/alignment_paired.compare_sets, paired bootstrap within kind) of this task's claims
against the verified lead on the SAME protocol and reading. Lead dumps: the polish's own claims of BEST
(docs/research/slipper_env_polish/{local,farm}/claim_BEST_fit60_<wear>_<r>_perpose.json) and, for held out unpriced,
the lead's remeasure dump (docs/alignment/remeasure/slipper-nose-knuckle-3r_held_perpose.json, = the row's 23.45).
gain = lead gap - candidate gap (positive = the candidate is better).
    python3 docs/research/slipper_flank_robust/paired.py [out.json]"""
import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP                                 # noqa: E402
EPD = os.path.join(REPO, "docs", "research", "slipper_env_polish")
LEAD = {"bench_u": os.path.join(EPD, "local", "claim_BEST_fit60_bench_u_perpose.json"),
        "bench_p": os.path.join(EPD, "farm", "claim_BEST_fit60_bench_p_perpose.json"),
        "held_p": os.path.join(EPD, "local", "claim_BEST_fit60_held_p_perpose.json"),
        "held_u": os.path.join(REPO, "docs", "alignment", "remeasure", "slipper-nose-knuckle-3r_held_perpose.json")}
out = {}
for f in sorted(glob.glob(os.path.join(HERE, "claim_*_perpose.json"))):
    nm = os.path.basename(f)[6:-13]; cfg, wear, rd = nm.rsplit("_", 2)
    ref = LEAD.get(f"{wear}_{rd}")
    if not ref or not os.path.exists(ref): continue
    A = json.load(open(f))["poses"]; B = json.load(open(ref))["poses"]
    r = AP.compare_sets(A, B, 4000); ci = r["boot"]["ci90"]
    row = dict(gain=round(-float(r["diff"]), 3), gap_cand=r["gap_A"], gap_lead=r["gap_B"], ci90_gain=[round(-float(ci[1]), 3), round(-float(ci[0]), 3)],
               p_cand_better=r["boot"]["p_A_better"], discordant=r["discordant"], lead_ref=os.path.relpath(ref, REPO))
    out[nm] = row
    print(f"{nm:28s} gain {row['gain']:+.3f} (cand {row['gap_cand']} lead {row['gap_lead']}) CI90 {row['ci90_gain']} P(cand better) {row['p_cand_better']} disc {row['discordant']}")
if len(sys.argv) > 1: json.dump(out, open(sys.argv[1], "w"), indent=1)
