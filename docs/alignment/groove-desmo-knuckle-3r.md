# Alignment audit: groove-desmo-knuckle-3r

Auditor run `audit:groove-desmo-knuckle-3r`, 2026-10-17 (discovery round 10, slice r10-B verified this design this
round). Reference: roller-longdyad-knuckle-3r, the verified 3-active lead (18.67). Tool VERSION 2026-10-17.2.

## Verdict and claim

- **Claim:** v_gap **22.64** (score 91.77), Bench(110,360) exact, frozen shape, the verifier's corrected number
  (`docs/concepts/rows/groove-desmo-knuckle-3r.json` verification; the claim's own 19.29 did not survive).
- **Ledger verdict: LEDGER_VERDICT.** Tool checks: TOOL_VERDICT_LINE
- **In one line:** the verified number is honest and reproduces to the digit; the design is not ranked above a better
  one. It is a complexity / hold trade against the lead, worse on every bench number (plain +3.97, 2 mm +1.96, held out
  HELD_VS_LEAD), and its complexity edge is smaller than the count says.

## What the wearer gets (measured)

Re-worn here through the verifier's own `--truewin` protocol (the one that produced 22.64), models and verifier
unchanged, only `PK.audit` wrapped (`tools/alignment_wear_truewin_groove.py`, new). Bench: 22.64 reproduced (per-pose
dump recomputes 22.65), 0 failing poses, 179 s. Files: `docs/alignment/remeasure/groove-desmo-knuckle-3r_{bench,held}{,_perpose,_probe}.json`.

| | groove-desmo (this audit) | lead roller-longdyad (its audit) |
|---|---|---|
| reach, workspace | 245 / 360 (0.681) | 261 / 360 (0.725) |
| overhead (elev >= 140) taken / total | 8 / 28 (held HELD_OVH) | 8 / 28 (held 18 / 71) |
| raised arm (elev >= 90) | 43 / 113 | 46 / 113 |
| taken poses with metal < 1 / 2 / 3 mm, bench | 2 / 25 / 130 | 3 / 30 / 133 |
| taken poses with metal < 2 mm, held out | HELD_LT2 | 66 |
| contact poses, bench | 2: 10.97 mm at (15, 165, -60), 6.03 mm at (30, 165, -60); sum 17.0 mm | 2: deepest 10.55 mm at (15, 165, -60); sum 16.46 mm |
| contact poses, held out | HELD_CONTACT | 10, sum 49.88 mm, deepest 9.54 mm |
| workspace in-band 2-14 (unscored), all / elev 90-140 / overhead | 0.849 / 0.781 / 0.937 | 0.854 / 0.798 / - |
| overhead p10 lowest metal | 1.82 mm | - |
| fold margin in th, min over taken | 5.389 deg (held HELD_TH) | 5.181 deg (5.031 held) |

- **Clip metal histogram (scored frames):** 0.02 % of samples under 2 mm, 0.17 % at 2-3 mm, 10.1 % over 14 mm.
  Reading the band as 3-14 mm costs 0.18 points (22.82): the band edge is not exploited (T2 clean).
- **Near-touch (report-only, user ruling 2026-10-17):** 1 mm 23.76, 2 mm 35.06, 3 mm 112.9; 12.42 points live in the
  1-2 mm shell (lead 14.43). The lowest metal, 0.07 mm at (-60, 60, 105), is the lead's pose and part, not the drive.
- **Springs:** none. K's clock spring and stop A are gone; K is held both ways by the groove and the slot.
- **Stops:** the groove ends are stops A and B. Stop B sits at K 32.25 deg (the true 3-D crest meets the groove
  window), against the lead's 46.2: 12 bench taken poses and 37 held-out poses of the claim protocol needed more and are
  lost. The arm meets that stop through an O1.5 dowel in a 1.5-deep groove (stop load not measured).
- **Cuff twist / K slop:** K slop is +-1.6-2.0 deg with the groove that a straight dowel needs (verifier), not the
  claimed +-0.54; the lead's spring drifted 4-8 deg. Not on the bench.
- **Near-singular / near-lock:** fold margin 5.389 deg (ok). Horn pressure angle 39.0 deg at the cut stroke (gate 43;
  the lead runs at 43.0). Groove pressure angle in 3-D 36.17 deg against its 37.29 gate (claim: 30.5). Knee to
  151.92 deg (window ends 154.78).
- **Continuity:** static 22.64 = full flood 22.64; knn flood 24.04 (+1.40; the lead +1.67).

Not measured, and why: cuff twist and K-slop effect on metal (the models have no slop state); the stop-B load on the
dowel (no dynamics judge for this drive); the CAD judge (no CAD for this design).

## Findings

FINDINGS_BLOCK

## Proposals (measurement or reporting changes; none is an input to the verdict)

PROPOSALS_BLOCK
