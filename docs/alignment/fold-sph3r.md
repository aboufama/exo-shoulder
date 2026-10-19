# Alignment audit: fold-sph3r (plain spherical 3R on fold-frontier axes)

Auditor pass 2026-10-19, about 02:45-03:20 UTC, tool VERSION 2026-10-19.1.

Why it was due: the row is a screened row with no ledger entry, and it had the lowest claimed gap among the due rows.
- It was added on 2026-10-16 at 01:33 (d3a6dcd).
- Its last commit was 03:12 that day (ff5e51e, the mechanism census).
- Its claim has not moved since.

## Verdict: WATCH (claim gap 44.72, Bench(60,160) fast, CMA F, q 0.9805; no frozen or held-out number exists)

The ledger verdict is WATCH, with no gamed reason (`python3 tools/alignment_ledger.py get fold-sph3r`).

- **Checks:** 4 watch, from `docs/alignment/fold-sph3r.json`: held_out, near_touch, fold_margin and sampling. In each
  case the tool found nothing on file in the form it reads:
  - the row has no v_gap and no verifier file;
  - the row's own `gap_near1` is skipped by the tool (see proposal 3).
- **Judgement findings:** 4 watch: T1, NEW-fitq, NEW-stale-pending and NEW-oob-standoff.

The short version:
- The 44.72 is not the design's honest number. The whole of it beyond 50.72 comes from the fitter's tolerance q
  (0.9805 instead of 1.0). That tolerance parks metal at 0.004-0.99 mm on 8 taken poses and under 2 mm on 24.
- The row's own near-touch-clean config, G at q 1.0, scores 49.03. It is the better exo by every metal reading on the
  same harness.
- Nothing is out-ranked by the difference. The board sinks fast-basis rows below every verified row
  (`docs/dashboard/simple/index.html` line 238). Even at 49.03, fold-sph3r stays ahead of the next screened row,
  cam-coupled-4r at 50.67.
- So this is watch, not gamed. The user's 2026-10-17 ruling also makes near-touch report-only (CLAUDE.md decisions 3
  and 6).

| check | level | measured |
|---|---|---|
| held_out | watch | no verified bench gap on the row; no held-out wear on file. This pass's exact frozen and held-out wears did not finish (see "Re-wear") |
| fast_frozen | ok | no verified pair. The neighbouring controls in the same model lost 6.66 (k2221, 51.33 -> 57.99) and 8.06 (k1530, 51.97 -> 60.03) when worn frozen exact |
| near_touch | watch (report only) | the tool found no record it reads. Measured this pass on the claim bench: F 44.72 plain, 53.66 / 76.53 / 134.34 at < 1 / 2 / 3 mm; G 49.03, 49.03 / 50.14 / 275.17 (`remeasure/fold-sph3r_claim.json`) |
| contact_depth | ok | 1 contact pose, sum 1.38 mm, deepest 1.38 mm at ws plane 105, elevation 45, axial -165, none deeper than 3 mm; vs the lead conecut-knee-knuckle-3r at 20.24 mm over 4 poses. Note: claim bench Bench(60,160) fast against the lead's Bench(110,360) exact |
| dominance | ok | no reference given |
| continuity | ok | no passive coordinate; flood not required |
| fold_margin | watch | the tool found no reading. Measured this pass: min th margin over taken poses 10.05 deg (F) and 10.54 deg (G); 0 taken poses within 10 deg of the fold (`remeasure/fold-sph3r_claim.json` th_margin) |
| idle | ok | 3 closure-set joints; a spherical 3R that follows a 3-DOF arm moves all three |
| sampling | watch | the tool found no per-part record it reads. Measured: hub1 1.00, hub2 0.00, hub3 0.87, link1 0.39, link2 0.10, neck 0.78 (81 / 81 / 81 / 364 / 273 / 256 samples). Part-weighted 0.523 vs sample-weighted 0.458, so the sample weighting charges this design rather than flatters it. Every declared body is sampled |
| density | ok | not measured (`tools/sample_density.py` needs a pin-knee model); the kit samples by construction |
| complexity | ok | recomputed 0.0: three pins on MR117 pairs, three links, nothing passive |
| reporting | ok | no verifier files; the board status (screened) matches the row |
| judge_change | ok | no bench / judge / metric file in the 2 commits that touched the row |
| rules | ok | O20 hubs (kit audit `[]`, honest True), margin 10 >= 5 in th, 0 passive translations, 3 DOF |

**The T5 instrument change (702373b, VERSION 2026-10-19.1).** Did T5 read this design differently? Yes, in its
reference only, and the verdict did not change. I re-ran the previous version (`git show 702373b^:tools/alignment_audit.py`,
2026-10-18.1) on the same files:
- Old version: "1 contact pose, sum 1.38 mm ... (no bench depth of conecut-knee-knuckle-3r on file)". The comparison was
  vacuous.
- New version: it compares with the lead's 20.24 mm over 4 poses.
- fold-sph3r has no paired file, so its own reading is the same under both versions.
- Before this pass the design had no depth record at all. The per-pose dump written here
  (`remeasure/fold-sph3r_claim_bench_perpose.json`, which reproduces 44.72 exactly) is what makes T5 readable.

## What the wearer gets (measured, files named)

Bench and protocol:
- All numbers are from Bench(60,160) fast, the screen's own claim bench. That is 60 clip frames and 160 workspace
  poses; the model ran unchanged.
- The source is `docs/alignment/remeasure/fold-sph3r_claim.json`, unless stated.
- F = the row's claim (k5170, q 0.9805). G = the row's near-touch-clean best (k5244, q 1.0).
- The project's overhead count over 28 poses needs Bench(110,360). That wear did not finish this pass. The row's frozen
  controls at neighbouring axes took 11 / 28 (k2221) and 13 / 28 (k1530).

| | F (claim, q 0.98) | G (q 1.0) |
|---|---|---|
| gap (score) | 44.72 (83.7) | 49.03 (82.2) |
| overhead reach, workspace elevation >= 140 | 6 / 12, but 4 of the 6 have metal at 0.004-0.40 mm and 5 are under 2 mm | 5 / 12, 4 of them at >= 2 mm |
| raised arm, workspace elevation 90-140 | 32 / 38 | 31 / 38 |
| taken poses with metal < 1 / < 2 / < 3 mm | 8 / 24 / 67 | 0 / 1 / 170 |
| deepest contact | 1.38 mm into the skin, a skin face, at ws plane 105, elevation 45, axial -165 | none |
| clip in-band 2-14 (scored) | 0.458 | 0.410 |
| workspace in-band 2-14 / 2-10 (unscored) | 0.380 / 0.288 | 0.345 / 0.243 |
| overhead workspace in-band 2-14 (unscored) | 0.38 | 0.46 |
| min th margin over taken poses | 10.05 deg | 10.54 deg |
| hub levels F1 / F2 / F3 from GH | 53 / 154 / 67 mm | 52 / 154 / 67 mm |

- **The < 3 mm count for G** (170 of 204 taken poses) is the kit's march fit. A rigid underside is set to its worst
  pose's 2 mm requirement, so most poses have one sample near 2-3 mm. The number is kit-wide, not a choice of this
  design.
- **Profile:** hub 2 is never in band.
  - It stands 154 mm from GH, posterolateral and horizontal. Its metal is a median >= 31.75 mm off the skin; 31.75 mm
    is the fast grid's cap. The design doc's exact red team at k2221 says a median 73 mm.
  - Link 2 is 0.10 in band.
- **Springs:** none.
- **Stops:** none. The J2 fold band is a jam, not a stop: 18 of 220 poses are not taken, and the design doc puts 15-17
  of them on the fold or K2.
- **Cuff twist:** none. The cuff is rigid on BOTTOM, with no knee and no slide.
- **Near-singular postures:** none within 10 deg of th's fold.
- **GH translation** is not on the bench. The row leaves it to cuff slides or the liner, outside the model. This is
  project-wide (R10 is design-independent for a spherical chain, and the user's K1 track accepts rigid-cuff spherical
  chains), so it is not filed as a finding.

## Findings (each in `fold-sph3r.findings.json`)

**T1, watch: the headline is metal parked at 0-2 mm.**

Measured, same bench, model unchanged:
- F: 44.72 plain, 53.66 at < 1 mm (8 poses), 76.53 at < 2 mm (24 poses). 31.81 points of the gap live in the 0-2 mm
  shell. The tool's pre-2026-10-17 gamed level was 25.
- G: 49.03, 49.03 at < 1 mm, 50.14 at < 2 mm (1 pose).
- F leads G by 4.31 plain. It trails by 4.63 at 1 mm and by 26.39 at 2 mm.
- F also has one real contact pose, 1.38 mm into the skin.
- F's extra overhead pose is metal on skin: its overhead taken poses sit at 0.004, 0.144, 0.324 and 0.399 mm, all at
  elevation 150-165.

Why the exo is not better: a pose taken at 0.004 mm is metal on a real, bulging arm.

Why watch and not gamed:
- near-touch is report-only by the user's 2026-10-17 ruling;
- F and G are the same design;
- no other design is out-ranked (see the verdict).

Action:
- Show G's 49.03 as the row's number, or the 53.66 at < 1 mm beside the 44.72.
- Any polish or verification uses q 1.0 and the near-touch objective.

**NEW-fitq, watch: the fitter's tolerance as a search coordinate.** This is a new pattern; the proposed catalogue entry
is below. CMA stream F searched q, the kit's underside quantile (`concept_kit.fit_profiles`, clipped to [0.8, 1.0] in
`fold-sph3r.py evaluate`).

The swap test (`remeasure/fold-sph3r_claim_qswap.json`), same bench:

| config | q | gap | < 1 mm | < 2 mm | lowest metal | overhead taken |
|---|---|---|---|---|---|---|
| F's axes (the claim) | 0.9805 | 44.72 | 53.66 | 76.53 | 0.004 mm | 6 / 12 |
| F's axes | 1.0 | 50.72 | 50.72 | 51.84 | 1.15 mm | 5 / 12 |
| G's axes | 1.0 | 49.03 | 49.03 | 50.14 | 1.37 mm | 5 / 12 |
| G's axes | 0.9805 | 52.26 | 56.74 | 80.26 | 0.13 mm | 2 / 12 |

So 6.00 points of F's headline, and its extra overhead pose, are the quantile alone. At q 1.0 the design's best is G.
q is not a universal gain: G's axes get worse at 0.9805. Stream F found the axes where the cheap cutoff pays. The
cutoff is cheap because contact costs 100 x the share of contact poses, while metal at 0.004 mm costs nothing. The
design doc says so: "With q < 1, the score buys in-band with contact poses".

Why the exo is not better: the gain is metal moved toward the skin, not a better mechanism.

Why watch: the shape is a real rigid shape, and the bench measures it honestly under the plain-gap rule.

Action: any polish or verification of this row runs at q 1.0. G at 49.03 is the shape to carry forward. Across the
project, a q < 1 number is shown beside its q 1.0 twin at the same axes (proposal 1). In fold-sph3r the dropped poses
land in the 0-2 mm shell, with 1 contact pose 1.38 mm deep. In three verified rows the same knob holds 41-73 fast points
(proposal 1), and there the dropped poses are scored contact.

**NEW-stale-pending, watch: a promised re-measurement that never landed.** This is a new pattern; the proposed
catalogue entry is below. The row verdict, the board row and the design doc say "CMA bests pending on the farm".
- `frozen_pending` points to `.cache/fsph3r/big_cmaF.json` and `big_cmaG.json`. Neither exists.
- No commit since 2026-10-16 03:12 has added a frozen number.
- For three days the board has carried a fast, in-sample best of 4790 tries with no frozen or held-out wear behind it.
- The neighbouring controls lost 6.66 and 8.06 points when worn frozen exact.
- This audit's own exact frozen wear did not finish in its time box. Only local CPU was available: the farm budget is
  spent and workersMax is 0 (CLAUDE.md decision 7).

Why watch: the row is labelled screened and sunk below every verified row, so the stale line ranks it nowhere. But it
reads as a number about to be confirmed, and nothing is running to confirm it.

Action: run `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_fsph3r_rewear.py bench F`, then `held F`
and `bench G`, to completion. Store the result, or strike "pending".

**NEW-oob-standoff, watch: out-of-band depth blindness.** This is the raglan-routed-3r audit's proposed catalogue entry
S7, present here as well.
- Hub 2 is 0.00 in band at 154 mm from GH, with metal a median >= 31.75 mm off the skin (73 mm exact at k2221 per the
  design doc).
- Link 2 is 0.10 in band.
- The gap would be the same with hub 2 at 16 mm.

The design does not buy points with this: no CMA start brought hub 2 down. But the number hides a hub that stands
several cm off the back of the shoulder, against the ~1 cm goal.

Action: report a per-part exact standoff (median and p90) beside in-band.

**Patterns walked and not present:**
- **T2:** the band read as 3-14 mm moves F by +1.06 (45.78) and G by +0.71 (49.74).
- **T3:** the margin is read on th itself: 10 deg searched, 10.05 measured.
- **T4:** no singular bound. q 0.9805 sits inside its [0.8, 1.0] box, and the fold margin is fixed at 10. The q knob is
  covered under NEW-fitq.
- **T5:** 1 shallow contact pose (1.38 mm). Frozen depths are not measured; the controls had crown contacts 27 and
  60 mm deep in unseen poses (row `frozen_controls`).
- **S1 / P1:** no held-out number exists to compare. This is the gap NEW-stale-pending names.
- **S2:** not flattering. Part-weighted in-band (0.523) is above sample-weighted (0.458).
- **S3:** all 3 moving bodies are sampled: link 1, link 2, and the arm-end (hub 3 plate + neck).
- **S4:** project-wide.
- **S5:** no passive coordinate; the J2 branch is fixed by sigma.
- **M1 / M2:** O20 at every hub (kit audit clean), 12 x 3 Ti straps, 0 passive translations.
- **M3:** K6 on every member pair, plus the model's own crown and wall skin check.
- **M4:** three closure-set joints.
- **M5, G2, G3:** no spring and no cuff joint.
- **P2:** the search used `K.bench`, and `K.evaluate` refuses held-out clips.
- **P3 / R3:** the spread is on the row: streams 44.72 / 49.03 / 50.30 / 59.33 / 59.64 / 170.35, top-5 spread 0.01.
- **P4:** no judge change.
- **R1 / R2 / R4:** labelled screened; the board number equals the row number; nothing was refuted.
- **G4:** 10 deg from the fold.
- **G5:** the count of 0 is honest for the mechanism as modelled.
- **G6:** 3 joints.

## Re-wear (what ran, what did not, and why)

- **Adapter:** `tools/alignment_fsph3r_rewear.py`, a new file. The audit's `remeasure` cannot wrap this model: it has no
  pin-knee audit. `alignment_kit_rewear.py` cannot call it either: it has no `snap()` or `fixed_prof`. The adapter runs
  the model's own `evaluate()` / `frozen()` unchanged and wraps only its `extras()` to record more.
- **Claim bench, Bench(60,160) fast. Done.** It reproduces 44.72 (F) and 49.03 (G) exactly. Output:
  `remeasure/fold-sph3r_claim.json`, the per-pose dumps `fold-sph3r_claim_bench_perpose.json` (F) and
  `fold-sph3r_claimG_bench_perpose.json`, and the q swap `fold-sph3r_claim_qswap.json`.
- **Frozen Bench(110,360) exact, and held out. Not done.**
  - The adapter fits on the claim's own fast shape (it reproduced 44.72 and 49.03 at the fit step) and wears exact.
  - Bench(110,360) has no fast cache, so the 470 poses go through libigl exact distances.
  - The machine ran at load 25 on 4 cores, and my two processes got 25-35 % of a core each.
  - The design doc's 21 minutes on 2 vCPU becomes well over an hour here. I stopped the G wear after 1 minute, to free
    a slot for the q-swap test. I stopped the F wear after 7 minutes (2.5 CPU-minutes, still inside the exact wear),
    once it was clear it could not finish in the time box. Neither left a file.
  - The farm was not used: CLAUDE.md decision 7 says the budget is spent, with workersMax 0 until the user renews.
- **Numbers I could not get:**
  - the frozen and held-out gap of F and G;
  - the overhead count over 28 for the claim;
  - frozen contact depth and frozen near-touch;
  - hub 2's exact standoff for F.

## Proposals (not applied; each is a measurement or reporting change for the lead or the user)

1. **Report every q < 1 claim beside its q 1.0 twin at the same axes, plus the contact depth of the poses the quantile
   drops.** Fixing q at 1.0 outright would be a far larger change, and it is the user's call; the measurement below
   shows why. Either form is a measurement change.
   - 3 of the 37 verified rows carry q < 1 in `best_params`: arm-parked-knee-4r (q 0.9801, v_gap 26.71),
     j3-neck-over-3r (0.9647, 28.46) and zc-frontier-3r (0.978, 33.51).
   - Measured at each row's own axes on Bench(60,160) fast, model unchanged
     (`remeasure/fold-sph3r_proposal_q1_rows.json`):

     | row | at its q | at q 1.0 | change |
     |---|---|---|---|
     | arm-parked-knee-4r | 19.32 | 92.19 | +72.87 (in-band 0.81 -> 0.21) |
     | j3-neck-over-3r | 26.26 | 67.37 | +41.11 (in-band 0.84 -> 0.30) |
     | zc-frontier-3r | 30.04 | 90.23 | +60.19 (in-band 0.89 -> 0.28) |

   - In those models the quantile is what keeps rigid parts low. Without it, a few poses whose rays run inside the body
     lift a rigid part by tens of mm. Those poses are scored as contact instead (contact 0.026 / 0.081 / 0.019 fast).
   - So for them q < 1 is the T5 trade: a few contact poses, of unknown depth here, against in-band everywhere else. A
     re-optimisation at q 1.0 would recover part of the loss; that is not measured.
   - The other 34 verified rows have no q in their parameters: effect 0.
   - This is not a finding against those three rows (they were not audited here). It is a pointer for their next T5
     audit: the dropped poses are where deep contact would sit.
2. **Catalogue entries.**
   - **T6, the fitter's tolerance as a search coordinate:** a search walks a fit tolerance (quantile, offset, clearance)
     that lets metal sit below its worst pose's requirement. Detect: a q < 1 claim without its q 1.0 twin.
   - **R5, a promised re-measurement that never lands:** a row or board line says "pending" for more than 24 h with no
     job or file behind it. Detect: `frozen_pending` paths that do not exist, or "pending" in a verdict older than 24 h.
3. **Instrument (not a tightening).** In `alignment_audit._near_numbers`, a screened row's own `gap_near1` is skipped:
   the record is matched against `v_gap`, which is null, so the error is the full gap. Match it against the ledger's
   claim (`claim_of`) instead. Likewise, let `c_fold_margin` read a re-measured `th_margin` from
   `remeasure/<id>_*.json`. Effect on verified rows: none, because they have v_gap.

## Skeptic (2026-10-19, about 03:45-04:12 UTC)

Run label `skeptic:fold-sph3r`. My rulings are in `docs/alignment/fold-sph3r.rulings.json`. Final verdict, as computed
by `tools/alignment_ledger.py skeptic`: **WATCH (2 of 8 reasons refuted, near_touch and fold_margin; 6 upheld, all at watch)**.

**What I re-measured, and how.**
- I wrote my own re-wear, `tools/alignment_fsph3r_skeptic.py`, a new file. It does not import the auditor's adapter.
  - It runs the model's `evaluate()` unchanged on Bench(60,160) fast.
  - It reads near-touch, th margin, per-part in-band, overhead and contact straight from `B.res` and `B._kit_last`.
- Output: `docs/alignment/remeasure/fold-sph3r_skeptic.json`. Every number the auditor gave on the claim bench
  reproduces to the hundredth:

  | config | gap | < 1 / < 2 mm poses | near1 / near2 | min th taken |
  |---|---|---|---|---|
  | F (claim) | 44.72 | 8 / 24 | 53.66 / 76.53 | 10.052 deg |
  | G | 49.03 | 0 / 1 | 49.03 / 50.14 | 10.536 deg |
  | F's axes at q 1.0 | 50.72 | 0 / 1 | 50.72 / 51.84 | 10.052 deg |
  | G's axes at q 0.9805 | 52.26 | 4 / 21 | 56.74 / 80.26 | 10.536 deg |

- **Exact re-read of F's near-skin poses (new).** I took the same frozen shape and the same pose index on a
  `CB_EXACT=1` bench, and measured F's 25 near-skin poses (the 24 taken poses under 2 mm, plus the contact pose) with
  the exact libigl distance. The result is in `fold-sph3r_skeptic.json` `F_exact_near`:
  - Pose 152 (ws plane 60, elevation 165, axial -90): 0.004 mm fast, **-0.281 mm exact**.
  - Pose 104 (ws plane 0, elevation 150, axial 0): 0.144 mm fast, **-0.059 mm exact**.
  - Pose 180 (the known contact): -1.384 mm fast, -1.452 mm exact.
  - Fast minus exact over the 25 poses: mean -0.073 mm, worst -0.285 mm.
- **Frozen Bench(110,360) exact and held-out wears of F.** I ran them with the auditor's adapter, model unchanged and
  output redirected to my scratch. Both reproduced the fit, 44.72, and then got 33-34 % of a core each at load 24-27 on 4 cores: 1.5 CPU-minutes each in 4.5 minutes wall. The design doc times one such wear at 21 minutes on 2 vCPU, so at this share it would need about an hour. I stopped both, and neither left a file. The farm was not used, because the budget is spent (CLAUDE.md decision 7).

**Rulings, by key.**

| key | ruling | evidence (short; full text in the rulings file) |
|---|---|---|
| held_out | upheld | Missing measurement, not on file: `v_gap`, `frozen_big` and every `v_*` are null, `.cache/fsph3r` is missing, and there is no `remeasure/fold-sph3r_bench.json` or `_held.json`. My own frozen and held wears of F could not finish in the time box |
| near_touch | **refuted** | The record is on file: row `gap_near1` 53.66, in the same top-level record as `gap` 44.72, and `remeasure/fold-sph3r_claim.json` `F.deep` (53.66 / 76.53). I re-measured the same numbers. The tool misses it only because `_near_numbers` matches against the null `v_gap`. Since 2026-10-17 `c_near_touch` reads any on-file record as ok (report-only). The substance stays under T1 |
| fold_margin | **refuted** | Measured on th = angle(J1, J3) with the kit's closure formula: min over taken poses 10.052 deg (F) and 10.536 deg (G), 0 poses under 5. This holds by construction: `K.closure` keeps only margin >= `margin_deg` (10.0) |
| sampling | upheld | With the record read, it is still watch. hub2 is 0.00 in band, link1 0.389 and link2 0.096, all under 0.5, which is `c_sampling`'s "mostly out-of-band parts" rule. Every body is sampled, and the weighting is not flattering (-6.52 points) |
| judgement:T1 | upheld | Reproduced. On the exact path 2 of F's 6 taken overhead poses are metal inside the skin |
| judgement:NEW-fitq | upheld | The swap reproduces: 50.72 and 52.26, and hub 2 sits at 159 mm at q 1.0 against 154 mm at q 0.9805. On exact, the extra overhead pose that q buys is contact |
| judgement:NEW-stale-pending | upheld | "pending" is at char 731 of both the row verdict and the board verdict, and on design-doc lines 150-151 and 226-227. `.cache/fsph3r` is missing, `frozen_big` is null, and the row's last commits are d3a6dcd and ff5e51e (2026-10-16) |
| judgement:NEW-oob-standoff | upheld | hub2 is 0.00 in band, with median and p90 both at the 31.75 mm clamp (a floor), fitted 154 mm from GH. The design doc puts it at 73 mm exact at k2221 |

**The T5 instrument change (702373b).** I confirm the auditor's reading:
- The reference side is no longer vacuous: conecut-knee-knuckle-3r reads 20.24 mm over 4 poses.
- fold-sph3r's own side is unchanged: 1 pose, 1.38 mm.
- With my exact re-read, F's claim-bench depth would be 3 poses summing 1.79 mm (1.452 + 0.281 + 0.059). That is still
  far under 2x the reference and under the 5 mm floor, so T5 stays ok either way.
- The comparison is still not apples to apples: this row's fast Bench(60,160) dump against the lead's Bench(110,360)
  exact.

**Missed by the auditor (for the next audit; not counted in this verdict).**
1. **The fast grid's error at the 0 mm cutoff is part of what the q knob buys (proposed catalogue entry T7, "the search
   instrument's error at the cutoff").**
   - The search and the claim both run on the fast grid: 4 mm voxels, int8 at 0.25 mm, trilinear.
   - With q < 1 the search parks metal at the fast grid's 0 mm line, and that line is up to 0.29 mm inside the skin on
     the exact path.
   - On the claim's own poses and shape, F's 0.004 and 0.144 mm read as contact on exact (-0.281 and -0.059 mm).
   - Reading those two poses exact moves the claim-bench gap from 44.72 to about 46.96:
     - contact 3 / 203: +0.99;
     - workspace reach 142 / 160: +1.25;
     - clip in-band was not re-read, but every clip pose under 2 mm stays at 1.52 mm or more on exact, so no clip pose
       turns into contact.
   - F's lead over G falls from 4.31 to at most 2.07.
   - F's overhead count falls to 4 of 12, below G's 5 of 12. G's lowest metal is 1.368 mm fast; at the worst error I
     measured that stays clear of the skin, though I did not measure G exact.
   - Detect: re-read exact every taken pose under 0.5 mm fast in a claim. This is a measurement step, not a threshold.
2. **Checked, not gaming: follow slack.**
   - F drops 2 "Raise overhead" clip frames (bench idx 3 and 7, th margin 9.7 deg under its own 10 deg margin). They cost
     0 points, because follow is 0.9667 against the 0.95 limit, and they leave the in-band denominator. G takes all 60.
   - At the user's 5 deg rule both frames would be taken. So the design is stricter than the rule here, not gaming it.

**What happens next.**
- Run `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_fsph3r_rewear.py bench F`, `held F` and
  `bench G` when the box is quieter, or on the farm when the budget is renewed. That gives the row a frozen and
  held-out number and closes NEW-stale-pending.
- Carry G (q 1.0) forward as the row's number.
