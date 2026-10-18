# Alignment audit: slotted-eccentric-pin-knee-3r (round 14, slice r14-B)

Auditor run 2026-10-18 02:20-02:40 UTC. Tool `tools/alignment_audit.py` VERSION 2026-10-17.6, reference
conecut-knee-knuckle-3r. Ledger entry 2026-10-18T02:36:31Z, by auditor, run `audit:slotted-eccentric-pin-knee-3r`.

## Verdict: WATCH (claim 201.20)

- The claim is the row's v_gap: 201.20 on Bench(110,360) exact, frozen shape (score 26.8). The fast search number is
  153.49.
- This audit re-wore the claim and reproduced it to the digit:
  - fit Bench(60,160) fast at the 1 mm part-part rule: 188.47;
  - Bench(110,360) exact: 201.20;
  - held out (poses disjoint from Bench(110,360)): 194.02, which is 7.18 better than the bench.
- Nothing in this design's number is bought by gaming. It is a far-behind, honestly scored design: 201.20 against the
  plain-3R control at its own seats, 58.53 through the same code and protocol.
- Every pattern found is a watch. None of them ranks the design above a design that is better for the wearer, and no
  hard rule is broken.
- One finding is new and reaches beyond this design: the dashboard's per-design "Sweep best gap" counts configurations
  the model itself flagged dishonest. This design shows 97.45 there.

## What the wearer gets (measured, re-wear on Bench(110,360) exact; held out in brackets)

Files: `docs/alignment/remeasure/slotted-eccentric-pin-knee-3r_bench.json` and `_held.json`, with per-pose dumps in
`_bench_perpose.json` and `_held_perpose.json`.

**Reach and follow**
- Overhead reach (workspace, elevation >= 140): 0 / 28 taken (0 / 26). Only 10 / 28 (9 / 26) even close
  kinematically inside the slot window; the rest are lost to collisions and contact.
- Raised arm (elevation 90-140): 14 / 85 taken. Overall reach 0.181 (0.192).
- Follow: 0.055 (0.064). 82 of 110 clip frames have th < 74.0 deg, below the lock-held slot track's end. The track end
  is a hard stop that sits where the wearer's arm rests and moves every day.

**Clearance and contact**
- Taken poses with metal < 2 mm: 20 of 71 (15 of 76). Under 1 mm: 7 (3). Under 3 mm: 31 (21). Minimum 0.089 mm.
- Near-touch gaps: 222.88 at 1 mm, 242.94 at 2 mm, 259.92 at 3 mm (held out: 200.31 / 233.00 / 241.72). These are
  reported only; 2 mm is not a gate.
- Contact: 8 poses press into the skin (9 held out), summed 27.78 mm (33.13 mm). The deepest is 9.92 mm, in a
  workspace side raise (plane -15, elevation 90, axial 105). Held out, the deepest is 9.94 mm at plane 0, elevation 75,
  axial 75. Four poses are deeper than 3 mm (five held out).
- The T5 contact-depth check reads x1.37 of the reference's summed depth on the bench and x0.54 held out, so it gives
  no watch. The depths are still real: a 1 cm press is a bruise.

**In-band**
- Clip frames: 0.604 in-band 2-14 mm (0.660), 0.362 in-band 2-10 mm.
- Workspace, unscored: 0.652 (0.627) over the 65 (69) taken workspace poses.
- Per part:
  - hub 2: 0.00 (fitted level 71.2 mm: link 1, track and crank stacked);
  - crank: 0.36;
  - L2b: 0.27 (0.43 held out);
  - hub 3: 0.51;
  - spoke: 0.53.
- These per-part readings are fractions only. The kit records no per-part sample counts.

**Springs, stops, transmission, cuff twist**
- Springs: none. K is slaved by the roller in the slot, one determined loop.
- Stops: the slot track's ends at th 74.0 and 133.5 deg are the physical stops. Taken th spans 74.83-123.04
  (74.01-121.52).
- Fold margin in th, at the effective a2 the model reads (its own `geom()` mg): minimum over taken poses 15.80 deg
  (17.30 held out). The rule is 5.23.
- Knee transmission psi: minimum 72.68 deg (71.31 held out). The rule is 15. No near-singular posture is taken.
- Cuff twist: not measurable here. The pin-knee cuff is not in the model; member 3 is the kit neck.

**Moving coordinates over taken poses (idle check)**
- K: 72.68-100.06 deg, a span of 27.38 deg.
- Effective a2: 74.48-87.38 deg.
- Crank (link 2a about J2), q1: -60.0 to 18.6 deg.
- Roller on the track: e 27.1-38.4 deg, eta 7.5-71.9 deg.
- Nothing is idle.

## The 12 checks (`docs/alignment/slotted-eccentric-pin-knee-3r.json`, after the re-wear)

| check | level | measured reason |
|---|---|---|
| held_out | ok | held out 194.02 vs bench 201.20 (-7.18; re-measured) |
| fast_frozen | watch | fast 153.49 -> frozen exact 201.20 (+47.71): the row's headline gap is a number the design does not hold (the row and doc say so) |
| near_touch | ok | 201.20 / 222.88 / 242.94 / 259.92 at 0 / 1 / 2 / 3 mm; band read 3-14 mm 202.96 |
| contact_depth | ok | bench 8 poses, 27.78 mm, deepest 9.92 mm, vs ref 20.24 mm (x1.37); held 33.13 vs 60.97 mm (x0.54) |
| dominance | ok | vs conecut-knee-knuckle-3r: -182.92 plain, -208.10 at 2 mm |
| continuity | watch | no continuity flood on file |
| fold_margin | watch | the tool reads only the row and verifier files; this audit measured 15.80 / 17.30 deg (above) but cannot place it where the check reads |
| idle | ok | K moves 27.38 deg (re-measured); crank and knee have no span key the check reads (measured above) |
| sampling | watch | fractions only; hub2 0.00, crank 0.36, L2b 0.27 |
| complexity | ok | recomputed 5.0 = row 5.0 (closed loop 4 + track pair 1; slaved K and cuff knee 0) |
| reporting | watch | dashboard sweep best 97.45 (score 64.56) sits 103.75 below the claim |
| judge_change | ok | no bench, judge or metric file in the row's 3 commits |
| rules | ok | O20 at J1-J3 and K (forced in `_clean`), margin 5.23, 0 passive translations, 3 active |

## Findings (`docs/alignment/slotted-eccentric-pin-knee-3r.findings.json`)

### 1. NEW-dishonest-sweep-best (watch): the dashboard's sweep best is a configuration the model rejected

**Evidence.**
- `docs/dashboard/data/morphs.json` shows sweep_gap 97.45 for this design (sweep_inband14 0.2095).
- That number comes from AUD-g9-2 (`docs/concepts/sweeps/slotted-eccentric-pin-knee-3r.json` k 1013, 01:58 UTC). It is
  a CMA probe the death auditor appended to the design's own sweep file.
- The model flagged it `honest: false`: ib14 0.21, collide 0.12, eccentric parts out of band.
- `tools/dash_build.py` `sweep_file_rows()` and `sweeps()` (lines 188-250) read only the shares and the file `gap`.
  They never read `honest` nor the penalised `obj`. Stream C, for example, logs gap 112.55 with obj 212.55.
- The same file also holds the locked control's configurations: lock=1, the plain 3R, stream `paired`, best 30.24 at
  01:13:30. They are kept out of the sweep best only because they were logged 7 minutes before the 01:20 claim (the
  passed_over rule). Logged after it, the eccentric would show the plain 3R's 30.24 (score 89.0).

**Repo-wide** (`python3 tools/alignment_sweep_honesty.py`, new in this audit): 10 of 98 designs have a dishonest
sweep best.

| design | dashboard sweep best | best honest | difference |
|---|---|---|---|
| virtual-pole-4bar-j1 | 152.69 | 237.75 | +85.06 |
| slotted-eccentric-pin-knee-3r | 97.45 | 153.49 | +56.04 |
| virtual-pole-4bar-j2 | 104.57 | 145.94 | +41.37 |
| meridian-goniometer | 86.81 | 94.31 | +7.50 |
| virtual-j2-knee-3r | 84.34 | 86.01 | +1.67 |
| fivebar-roll | 89.13 | 90.30 | +1.17 |
| cuff-slaved-elbow-fourbar-3r | 107.61 | 108.36 | +0.75 |
| clavicular-front-route | 65.53 | 65.71 | +0.18 |
| twin-k2-sidecar-knuckle-3r | 58.31 | 58.44 | +0.13 |
| split-knuckle-twosided-3r | 26.62 | 26.62 | 0.00 |

None of the 10 is the sweep record (minarc 6.19) or near the top of the board.

**Why this is not a better exo.** A configuration the model rejected (parts lifted out of band, collisions, a failed
gate) is shown as the design's best evidence. That configuration is not wearable.

**Why watch, not gamed.** For this design the dashboard's best-evidence order is verified, then claimed, then sweep.
That order reads 201.20 / 153.49 first, so the 97.45 ranks it above no better design.

**Action.**
- Proposal R5-a below.
- Auditors' probe configurations belong in a separate file (for example `docs/alignment/remeasure/<id>_probes.json`),
  not in the design's sweep file.
- Controls belong under their own id, or carry `control: true`.

**Proposed catalogue entry R5.** A sweep best read from configurations the model rejected, or from another mechanism
logged under the design's id. Detect: `tools/alignment_sweep_honesty.py` (dashboard sweep best against the best honest
configuration, obj-aware).

### 2. S3 (watch): the cuff pin knee in the name is not in the model

**Evidence.** The row's name and `mechanism.cuff_knee` declare the cuff: pins a and b, a knee link and an arm pad.
The model builds member 3 as the kit neck instead (model lines 9-15). The re-wear samples 16 metal groups, and none of
them is the cuff knee.

**Why it does not flatter.** The doc's own paired controls show the kit neck costs about 7.6 points against the real
pin knee: kit-neck control at H1 34.78 fast / 36.83 frozen, against the pin knee's 27.20 verified under its own
harness.

**Action.** No pin-knee number may be quoted from this row until the knee is built and sampled. Renaming the row's
headline to "eccentric J2 on the pin-knee seats (kit neck)" would say what was measured.

### 3. S2 (watch): out-of-band parts hidden by sample weighting

**Evidence.**
- Hub 2 is 0.00 in band: it sits at 71.2 mm, a three-layer stack.
- The crank is at 0.36 and L2b at 0.27.
- The headline in-band is still 0.604.

**Why this is not a better exo.** A hub standing several centimetres above the band is felt at every pose.

**Action.** None for the ranking (201.20). Kit models should record per-part sample counts (proposal S2-a).

### 4. G1 (watch): metal hugging the skin

**Evidence.** 20 of 71 taken poses have metal < 2 mm, so 28 % of what the bench counts as taken is metal on a real arm.
The near-touch gap rises by 41.74 points at 2 mm.

**Action.** None: report only (user ruling 2026-10-17).

### 5. S5 (watch): no continuity flood

**What was measured.**
- K never nears its branch point: psi is at least 71 deg over the taken poses.
- The slot track's lower end, th 74.0, sits on the rest region: 72 of 128 bench workspace poses at elevation <= 30 and
  82 of 110 clip frames are below it.

**What it means.** The 18 % static reach is a set of islands above a blocked rest. A flood can only lower the reach,
not lift the rank.

**Action.** A flood is owed before any connected-reach claim.

### 6. R1 (watch): a self-measured number in the verified column

**Evidence.** v_gap 201.20 is the screener's own frozen exact. There is no verifier file for this design, and its status
is screened.

**Why it does not flatter.** The number is pessimistic, and it reproduced in two independent re-wears: the 02:08 death
audit and this one.

**Action.** Labelling only.

### Patterns checked and not present

- **T1, T2:** the plain gap is not near any cutoff that matters; the design is 182 points behind.
- **T3:** the fold margin is read in th, at the effective a2 the model itself uses. It measures 15.80 deg (17.30 held
  out), above the rule's 5.23.
- **T4:** the box edges are the rules' floors (margin 5.23, psi_lo 15, lock 50). The best config sits far from them:
  psi 71.3, margin 15.8. The emax cap of 40 was freed by the death audit, and the result got worse (197.07 dishonest).
- **T5:** see contact_depth above (x1.37 / x0.54).
- **S1, P1:** held out 7.18 better than the bench.
- **S4:** no instance.
- **M1, M2:** O20 is enforced at K. The roller is a real MR52ZZ on an O2 dowel. The track is a 2 mm plate.
- **M3:** pinK has no `over` list. That makes the model over-strict, not optimistic (death audit: stacking it moves the
  best 153.49 -> 153.86).
- **M4:** K moves 27.4 deg and a2e moves 12.9 deg; nothing is idle.
- **M5, G2, G3:** no springs. Cuff twist is not modelled (S3).
- **P2:** the search ran on Bench(60,160) only. Held out was first touched by this audit.
- **P3, R3:** 915 configs, top-5 spread 2.61, reported with the convergence gate.
- **P4:** no judge change.
- **R2:** no refuted number displayed. R4: the dashboard v_gap 201.2 equals the row.
- **G4:** no taken pose is near-singular.
- **G5:** complexity recomputes to 5.0.
- **G6:** 3 active joints.

## Proposals (measurement or reporting changes; not applied, not inputs to the verdict)

- **R5-a (dashboard sweep best).** `tools/dash_build.py` would skip configurations with `honest: false`, read each
  configuration at max(gap, obj), and skip configurations tagged as controls (stream `paired`, or params lock=1, or
  `control: true`).
  - Measured effect (`tools/alignment_sweep_honesty.py`): 10 of 98 sweep bests rise. The four large moves are +85.06,
    +56.04, +41.37 and +7.50 points; the full list is in finding 1.
  - The sweep record (6.19), every verified row and every claimed row are unchanged.
- **F-a (fold-margin reader).** `c_fold_margin` would also read a re-measure file's `kin.fold_margin_th_min_taken`
  (written by `tools/alignment_slotted_rewear.py`). For this row that turns the watch into ok at 15.80 deg. No other
  row has the key today.
- **S2-a (per-part counts in the kit).** `concept_kit` `inband_member` would carry `[share, median mm, samples]`, as the
  pin-knee audit does, so `sampling` can weigh parts. This is a model-side change and needs no metric change.

## What I could not measure, and why

- **Continuity flood:** this model has no verifier with an `extras()` flood, and `tools/alignment_kit_flood.py` needs
  one. It is not run. The measured context is in finding 5.
- **Per-part sample counts:** the kit records fractions only.
- **Cuff twist and the cuff knee's clearance:** the knee is not in the model.
- **R17 dynamics:** no CAD, no dynamics judge run (none required for a screened row).

## Instruments added by this audit (new files only)

- `tools/alignment_slotted_rewear.py` re-wears slotted-eccentric kit models through their own `frozen()`, unchanged.
  It wraps only `K.bench` (to swap in the held bench) and `build()` (pass-through record of th, effective a2, mg, psi
  and K). It reads the worn bench with `deep_audit`, `wear_probe.analyse` and a per-pose dump. Run time: 85 s bench,
  92 s held, local, niced, 2 processes.
- `tools/alignment_sweep_honesty.py` measures the dashboard sweep best against the best honest configuration for every
  design.

The next loop step is unchanged. This design stays screened and far behind; nothing here moves it, and no new leader is
involved.
