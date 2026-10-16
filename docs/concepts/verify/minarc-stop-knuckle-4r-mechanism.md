# minarc-stop-knuckle-4r, variant B: independent verifier, lens mechanism / manufacturability / red team

Claim under test: `docs/concepts/rows/minarc-stop-knuckle-4r.json`, variant B, best_params (CMA stream BD), model
`docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py`: frozen shape worn on Bench(110,360) exact, gap 15.42
(score 94.4; reach 0.769, follow 1.0, in-band14 0.899, contact 0.023; near-touch 22.17; min metal 0.05 mm),
complexity 33. Verified leader it would beat: pin knee H1, 24.48 (margin 5, polish protocol) / 27.20 (round-3 protocol).

Harness: `docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py` (imports the model unchanged, swaps only what it
tests). Raw outputs: `.cache/minarc_verify_mech/*.json` (git-ignored).

RESULTS_PLACEHOLDER
