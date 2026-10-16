# Alignment audit: kneeless-roller-knuckle-3r (round 9, lens 3, screened)

This is the hourly audit of 2026-10-16 at 22:45 UTC, run from git 9724c2d onward. The audit edited no bench, judge,
model, row, dashboard page or CLAUDE.md, and wrote no tool. Every re-wear ran the model file unchanged, through
`tools/alignment_audit.py remeasure`, `tools/alignment_wear_probe_model.py` and the model's own `redteam_gh` mode.

## Verdict: GAMED (ledger), but the only gamed reason is a false positive of the audit tool

**The claim.**
- The row headline is the fast Bench(60,160) plain gap **16.70**. The ledger records this as the claim, field `gap`.
- The design's own self-measured frozen exact Bench(110,360) claim is 21.07 (score 92.34), with 1 mm 23.23, 2 mm
  32.25 and held out 24.59. It is not verified.
- The row calls itself "a complexity Pareto point, not a lead change" (complexity 23.75).

**The ledger.** Verdict gamed; tool verdict gamed.
- The only gamed reason is the tool's `idle` check: "re-measured K.ang span = 0.0 deg".
- `K.ang` is the knee angle of this model family. Here the knee is deleted on purpose: the model asserts it constant
  (93.12 deg on every pose) and the mechanism record does not count it.
- The declared drive (the slaved knuckle K) moves dK 0 to 43.53 deg over the taken poses.
- So pattern M4 (an idle mechanism carrying the story and the complexity) is not present. The finding
  NEW-idle-check-false-positive records this with its evidence.
- The auditor cannot lower a tool reason. **A skeptic ruling on `idle` is requested.**
- Every other reason is watch. Without the false positive, the verdict would be **watch**.

**The number reproduces to the digit.** This audit re-wore the claim with the row's best_params and the model
unchanged (CB_EXACT=1):

| wear | plain | 1 mm | 2 mm | 3 mm |
|---|---|---|---|---|
| bench | 21.07 | 23.23 | 32.25 | 87.37 |
| held out | 24.59 | 27.20 | 36.06 | 92.23 |

Files: `docs/alignment/remeasure/kneeless-roller-knuckle-3r_bench.json` and `_held.json`.

**It is not ahead of the lead on the same harness.** Against sidecar-longdyad (18.91 / 20.00 / 34.03 / 155.98; held
out 22.67 / 25.75 / 37.24 / 163.09):
- it is worse plain (+2.16), at 1 mm (+3.23) and held out (+1.92);
- it is better at 2 mm (-1.78) and much better at 3 mm (-68.6).

The A1 dominance gate is not met, and the row does not claim the lead. Against the newly verified roller-longdyad
(same drive, with a knee: 18.67 / 20.30 / 33.10, held out 23.73), it is +2.40 plain and -0.85 at 2 mm.

## What the wearer gets (measured)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140), workspace | **7 / 28 taken** on the bench (lead 8 / 28). Lost to fold 15, contact 4, parts 2. Held out: 16 / 71 (lead 18 / 71), with 13 of the 71 lost to contact and 7 to parts | `remeasure/..._bench.json` and `_held.json` audit.overhead140 |
| Raised-arm reach by elevation (taken / total) | 0-60: 158/172; 60-90: 57/75; 90-120: 25/51; 120-140: 14/34; 140-160: 5/13; 160-200: **2/15**. Lead: 161, 55, 25, 12, 5, 3 | `remeasure/..._probe.json` ws_reach_by_elev |
| Taken poses with metal < 2 mm | 21 of 371 on the bench (lead 26), 49 of 863 held out (lead 63) | `_bench.json` / `_held.json` deep |
| Metal < 1 mm on taken poses | 4 on the bench (lead 2), 12 held out (lead 14). Min metal **0.006 mm** at (plane 90, elev 135, axial -90), hub 2's crown edge. 10th-percentile overhead min metal 1.72 mm (lead 1.02) on the bench, 1.25 (lead 0.64) held out | same |
| Metal < 3 mm on taken poses | 95 of 371 (lead 178), 228 of 863 held out (lead 427). The clear win of this design | same |
| Contact (metal into skin, penalised) | **10 workspace poses** on the bench (lead 4), summed depth **44.0 mm** (lead 6.23). Deepest -12.0 mm at (15, 165, -60). Five of the 10 are the everyday side raise: scapular-plane abduction 90-105 with axial 15-45, depths -0.7 to -5.9 mm, hub 2's crown. Held out: 26 poses (lead 10) | `_probe.json` contact_poses; `_held.json` why |
| Workspace in-band (unscored) | 2-14 mm: **0.855** over the 261 taken workspace poses (lead 0.874); elev 90-140: 0.828 (lead 0.841); overhead 0.946 (lead 0.926). Metal > 20 mm: 4.2 % (lead 2.8 %); max 33.7 mm | `_probe.json` ws_unscored, ws_elev90_140, ws_overhead140 |
| Scored clip in-band | 0.8905 (lead 0.8966). Band read 3-14 mm: 21.41 (+0.34), so the band edge is not exploited | `_bench.json` deep.gap_band3_14 |
| Per-part in-band | hub 3 **0.505**, median 13.9 mm: half of the GH-ray hub stands beyond 14 mm on the deltoid (lead 0.599 / 13.0). L2 0.71, crank 0.86, every other part >= 0.93. Part-weighted 0.912 vs sample-weighted 0.891, so the weighting does not flatter | `_bench.json` parts_ib14 |
| Fold margin (th, the one metric) | min **5.408 deg** over the 371 taken poses (0 below 5, 1 below 5.5); th max taken 108.74 | `_probe.json` extras.th_margin_own_state |
| Continuity | full flood 21.07 (0 dropped); knn flood 23.35 (8 dropped, +2.28). From the row; this audit did not re-run the flood | `rows/kneeless-roller-knuckle-3r.json` frozen.connected |
| Drive | dK 0-43.53 deg taken; horn pressure angle 42.5 against the 43 cap; arm to hub K 1.53 mm; roller to hub K 3.08 mm | `_probe.json` extras |
| Springs / stops | One K clock-spring cap closes both cam pairs. Stop A plus drive stop B on K. No R17 run, so lag, cuff twist and hold force are unmeasured | row mechanism.notes |
| Knee | none: the knee angle is constant 93.12 deg on every pose (the model's assertion holds) | `_bench.json` deep.coord_spans |
| GH-centre error | 3 mm error: rigid misfit median 3.40 / max 5.90 mm, only **38.7 %** of poses within a 3 mm liner (a planar knee would leave 66.6 %). 5 mm error: 17.7 % (36.2 %) | `remeasure/..._ghoffset.json` |

The seed config was the row headline (15.81 fast) from 22:19 to 22:57. Frozen exact it measures 21.78 / 1 mm 26.29 /
2 mm **58.90**, with 58 taken poses under 2 mm: a metal-hugging config (`_seed_bench.json`). The dashboard's 22:50
sweep best, 14.91 fast plain, measures 21.77 / 24.48 / 34.59 frozen (`_plainbest_bench.json`). Neither is the claim
now.

## Findings

**idle (tool, gamed): a false positive.** See the verdict. The probe has the evidence: `knee_ang_taken`
[93.12, 93.12] and `dK_taken_max_deg` 43.53.
- **Action:** a skeptic rules on `idle`.
- **Tool proposal T-a** (below).

**R1 (watch): the dashboard shows the fast number and ranks it among verified ones.**
- The board carries gap 16.70 and frozen_gap null (built in memory with tools/dash_build.py; nothing was written).
- `tools/dash_build.py:408-409` reads only `frozen_exact` / `frozen_exact_gap`. The row keeps its claim under
  `frozen`.
- The main board's "Below the baseline now" list (`docs/dashboard/leader.js:73-74`) sorts claimed and verified
  numbers together. It shows this row 3rd, at 16.70, above the verified minarc 18.40 and sidecar-longdyad 18.91.
- On the same harness the design is 21.07. **Why not better:** 4.37 points of the displayed number are the fit bench.
- **Action:** proposal R-a.

**NEW-free-deletion (watch): the knee is deleted for free on the bench.**
- The bench's GH is an ideal fixed point at the chain centre. A rigid closure therefore costs nothing on the score,
  and complexity falls from 43.75 to 23.75.
- At a 3 mm GH-centre error the cuff liner overflows on 61 % of postures. With a planar knee it would overflow on 33 %.
- **Why not better:** the wearer feels it as cuff pressure and twist. The doc states the cost, but the Pareto claim
  "about half the complexity" is priced on the bench only.
- **Action:** the user's misalignment budget, as the doc itself says, before any CAD. Catalogue proposal G7.

**NEW-contact-depth (watch): more and deeper contact, at an everyday posture.**
- Contact poses: 10 against the lead's 4.
- Summed depth: 44.0 mm against 6.23 mm.
- Five of the poses are at scapular-plane abduction 90-105, where hub 2's crown presses 0.7-5.9 mm into the shoulder.
- The score charges each contact pose (about 0.54 points), but not its depth or where it falls.
- **Why not better:** the 3 mm advantage is partly bought by poses where metal goes into the skin dropping out of
  the taken set.
- **Action:** the doc's own next lever (hub 2's crown), and proposal R-b.

**NEW-ws-inband (watch): the raised-arm comparison flips between benches.**
- On the fit bench the doc's comparison shows a raised-arm workspace in-band gain over the lead: 0.814 vs 0.762.
- On the claim bench it is a loss: 0.828 vs 0.841, and 0.855 vs 0.874 overall.
- **Action:** report workspace in-band on the claim bench (as the live audit's L2).

**M5 (watch): the spring-closed cam pairs are unproven.** Two rolling pairs are force-closed by one clock spring, and
no R17 has run.
- **Action:** the slaved-coordinate coupling in judge/dynamics.py before CAD.

**G4 (watch): the drive runs at its cap.** The horn pressure angle reaches 42.5 against the 43 cap at dK 43.53 (dK_lim
46.8), with 1.53 mm from the arm to hub K.
- **Action:** a force check of the roller-flank contact with K slop.

**NEW-confounded-lesson (watch): the doc's "new knowledge 2" is confounded.**
- The doc credits the deleted knee for the small fast-to-frozen penalty: +4.4 here against +8.4-9.0 for the knee
  rows.
- Those knee rows were searched on the plain or 1 mm gap. The knee row with the same drive and the same 2 mm
  objective (roller-longdyad) pays +5.48. The knee's share is about 1.1 points; the rest is the search objective.
- **Action:** correct the lesson before it reaches FINDINGS and steers the next round.

**Patterns checked and not present.** Each is checked against the files listed.
- **T1 / G1:** the 1-2 mm shell holds 9.02 points (2 mm minus 1 mm) and 11.18 from plain. That is under the 15-point
  watch line, and 3 mm is far better than the lead.
- **T2:** band 3-14 is +0.34.
- **T3:** min th 5.408 on the claim's own taken poses.
- **T4:** no best_params sits at a clamp edge (bk1 27.4 in 24-32, bk2 35.7 in 34-48, g 2.23 in 1.8-3.0, r_c 16.3 in
  14.5-19.5, beta -171 in -180..-150, lE 82.3 in 35-95, lc 29.9 in 6-45). There is no knee window to walk.
- **S1 / P1:** the held-out drop is +3.52, under 6.
- **S2:** part-weighted is above sample-weighted. L1a has 8 samples, but it is a short link at 0.96 in band.
- **S3:** every moving body has a sampled metal group (L1a, L1b, L2, crank, roller / horn, and the bracket as knee + E +
  pad). The row's red team also reports minima for the flank lug and hub 2's crown at the metal-lost poses.
- **S5:** the full flood drops 0. The knn flood drops 8 poses (+2.28), under the 3-point line.
- **M1 / M2:** O20 at all four hubs (rad 10). There are 0 passive translations and 3 active DOF.
- **M3:** the bracket keeps 0.15 mm to hub 3 (the adjacency rule) and 1 mm to everything else, as the knee did.
- **P2:** held out was read on 3 frozen candidates (claim 24.59, C2 24.89, round-1 C 25.55). The claim was picked by
  its frozen bench number, and held out ranks the same, so held out did not choose it. The search scripts were not
  read in this audit.
- **P3 / R3:** the claim is the best of 5 frozen wears. The spread (21.07-22.37) is reported in `other_frozen`, and
  held out ranks the same (24.59 < 24.89 < 25.55).
- **P4:** no bench, judge or metric file changed in the row's commits.
- **R2:** the refuted earlier numbers are passed over by the dashboard (sweep_gap 16.70, not 14.91).
- **G2 / G3:** unmeasured; see M5.
- **G5:** the complexity reproduces as 23.75. The record omits member 3 as a moving body; the anchor counts it, so it
  is +1 (24.75). The sibling roller row omits it the same way, so the comparison holds.
- **G6:** K is slaved and never read, so it is not a sensed fourth joint.

## Proposals (measurement or reporting changes; none applied, none used in the verdict)

- **T-a (tool):** make `tools/alignment_audit.py` read what is already on file.
  - Changes:
    - c_idle skips `K.*` spans when the row asserts `knee_rigid`, or when the mechanism record has no knee.
    - c_continuity reads `row.frozen.connected`.
    - c_fold_margin reads `remeasure/<id>_probe.json` extras.th_margin_own_state.
  - **Effect on this row:** idle gamed -> ok (dK 43.53); continuity watch -> ok (full 0 dropped, knn +2.28);
    fold_margin watch -> ok (5.408). The tool verdict becomes watch, because held_out still has no verified bench gap.
  - Its twin kneeless-sidecar-knuckle-3r would get the same correction. Rows with a working knee keep the
    K.ang test.
- **R-a (reporting):** dash_build reads a row's `frozen.gap` as `frozen_gap` when `frozen.bench` names the exact
  Bench(110,360) frozen protocol, and leader.js ranks by v_gap, then frozen_gap, then the fast gap, labelled.
  - **Effect on the "Below the baseline" list:**
    - this row 16.70 -> 21.07 (from 3rd to below minarc 18.40, roller-longdyad 18.67, sidecar-longdyad 18.91,
      sidecar-parallelogram 19.13 and roller-flank 20.08);
    - kneeless-sidecar 15.63 -> 21.11;
    - roller-longdyad is now verified, 18.67.
  - No score moves.
- **R-b (reporting):** every claim reports the summed contact depth, the deepest contact, and the contact poses at
  scapular-plane abduction 60-120.
  - **Effect:** this row 44.0 mm / -12.0 mm / 5 poses; the lead 6.23 mm / -4.61 mm / 0 poses.
  - A cap would be the user's call.
- **New catalogue entries proposed:**
  - **G7. A compliance deleted for free.** The bench's GH is an ideal fixed point. Deleting a passive freedom
    between the chain and the cuff therefore costs nothing on the score, and the complexity count falls.
    - **Detect:** any design that removes such a freedom reports the GH-offset misfit at 3 / 5 mm as the share of
      poses within the liner, against its parent.
    - **Here:** 38.7 % against 66.6 % at 3 mm.
  - **R5. A lesson drawn across rows that differ in protocol.** A fast-to-frozen or held-out comparison between rows
    searched on different objectives or benches.
    - **Detect:** review. Compare only with a row on the same objective and harness.
    - **Here:** +4.4 credited to the knee deletion, against +5.48 for the same-objective knee row.

## What happens next

1. The skeptic rules on `idle`. The rest stays watch.
2. The adversarial verifier re-wears A2 with this model's `frozen` / `held` / `flood` / `redteam` modes. This audit's
   re-wears are the reference.
3. R17 with the slaved coupling, and the user's GH-misalignment number, before any CAD.
4. The hub-2-crown lever for this class: 9 of its 13 metal-lost poses are there, and the side-raise contact found
   here.
