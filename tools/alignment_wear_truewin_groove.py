"""Adapter (alignment audit, read-only on every claim): wear groove-desmo-knuckle-3r through its OWN independent verifier
(docs/concepts/verify/groove-desmo-knuckle-3r.py, unchanged) in the protocol that produced the VERIFIED number
(--truewin: stop B where the true 3-D groove crest meets the claim's own window), and record what the score does not see.

The claim's model and the verifier run UNCHANGED; only PK.audit is wrapped to capture the worn (M, B). From that one wear:
  * tools/alignment_audit.py deep_audit (near-touch 1 / 2 / 3 mm, clip metal histogram, band 3-14, joint spans);
  * tools/alignment_wear_probe.py analyse (workspace in-band, overhead floor, poses with metal < 1 / 2 / 3 mm, contact
    poses with their depth);
  * tools/alignment_wear_probe_model.py extras (own-state th margin, knee angle span, dK span);
  * tools/alignment_paired.py per-pose dump (for the contact_depth check; its recomputed gap must equal the report).
Outputs (same shapes as the tool's remeasure / dump outputs, with harness named):
  docs/alignment/remeasure/groove-desmo-knuckle-3r_<wear>.json, ..._<wear>_perpose.json, ..._<wear>_probe.json

    GD_CELL=lead CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_truewin_groove.py bench|held
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GD_CELL", "lead")
import alignment_audit as AA                                  # noqa: E402
import alignment_paired as AP                                 # noqa: E402
import alignment_wear_probe as W                              # noqa: E402
import alignment_wear_probe_model as WM                       # noqa: E402

RID = "groove-desmo-knuckle-3r"


def main(wear):
    V = AA._load("al_v_groove_truewin", os.path.join(AA.VERIFY, RID + ".py"))
    cap = W._capture(V.PK)
    t = time.time()
    out = V.wear(dict(V.BEST), wear, False, False, True)
    M, B = cap[-1]
    deep = AA.deep_audit(M, B); probe = W.analyse(M, B); ext = WM.extras(M, B)
    poses = AP._dump_bench(M, B); rep = B.report()
    secs = round(time.time() - t, 1); git = AA._git("rev-parse", "--short", "HEAD"); exact = os.environ.get("CB_EXACT") == "1"
    harness = "docs/concepts/verify/groove-desmo-knuckle-3r.py wear --truewin (the verified protocol), models unchanged, PK.audit wrapped"
    os.makedirs(AA.REM, exist_ok=True)
    rem = dict(id=RID, wear=wear, harness=harness, params=V.BEST, frozen=out["frozen"], corrected=out["corrected"], poses_failing=out["poses_failing"],
               fit_fast=out.get("fit_fast"), why=out.get("why"), parts_ib14=out.get("parts_ib14"), audit=out.get("audit"), deep=deep,
               mode=out.get("mode"), th_margin=out.get("th_margin"), groove=out.get("groove"), roller=out.get("roller"), sc_info=out.get("sc_info"),
               corrected_overhead=out.get("corrected_overhead"), extras=ext, secs=secs, exact=exact, git=git)
    json.dump(rem, open(os.path.join(AA.REM, f"{RID}_{wear}.json"), "w"), indent=1, default=float)
    pp = dict(id=RID, wear=wear, harness=harness, params=V.BEST, frozen=out["frozen"], report={k: v for k, v in rep.items() if k != "poses"},
              poses=poses, recomputed=AP.gap_parts(poses), secs=secs, exact=exact, git=git)
    json.dump(pp, open(os.path.join(AA.REM, f"{RID}_{wear}_perpose.json"), "w"), default=float)
    pr = dict(design=RID, wear=wear, harness=harness, verifier_frozen=out["frozen"], verifier_corrected=out["corrected"],
              verifier_audit_near=out.get("audit"), probe=probe, extras=ext, secs=secs, exact=exact, git=git)
    json.dump(pr, open(os.path.join(AA.REM, f"{RID}_{wear}_probe.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(wear=wear, frozen=out["frozen"], corrected=out["corrected"], failing=out["poses_failing"],
                          deep={k: v for k, v in deep.items() if k != "coord_spans"}, recomputed=pp["recomputed"], secs=secs), default=float))


if __name__ == "__main__":
    main(sys.argv[1])
