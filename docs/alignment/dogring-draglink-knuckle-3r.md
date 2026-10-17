# Alignment audit: dogring-draglink-knuckle-3r

Auditor run, 2026-10-17 12:23-12:40 UTC. The audit was due because discovery round 11 slice r11-A screened and verified
this design this round.

Files:
- Checks: `docs/alignment/dogring-draglink-knuckle-3r.json` (`--ref slipper-nose-knuckle-3r`, tool VERSION 2026-10-17.2).
- Findings: `docs/alignment/dogring-draglink-knuckle-3r.findings.json`.
- Ledger: `docs/alignment/ledger.jsonl`, by `auditor`, run `audit:dogring-draglink-knuckle-3r`, 2026-10-17T12:36:22Z.

Re-wears, all exact Bench(110,360) and the held-out set, frozen protocol, models and verifier unchanged. Local, nice,
OMP_NUM_THREADS=1, at most 2 processes, $0 farm.
- `remeasure/dogring-draglink-knuckle-3r_{bench,held}.json`: `tools/alignment_audit.py remeasure`, the claim through
  the model's own `frozen()` / `frozen_held()`.
- `remeasure/dogring-draglink-knuckle-3r_vprobe_{bench,held}.json`: a new adapter,
  `tools/alignment_wear_probe_dogring_verifier.py`. It runs the wear probe's `analyse()` inside the verifier's own
  harness and records both the corrected wear and the claim wear.
- `remeasure/dogring-draglink-knuckle-3r_vprobe_bench_EYE_R4.5.json`: the same, with the drag-link eye radius set to
  the stated O9 in memory only.

## Verdict: WATCH (claim on record: v_gap 97.83, status refuted)

- **The number on record is honest, and it is a bad number.** The verifier refuted the screen's claim at 11:39 UTC:
  - Claimed: frozen exact 22.64, held 25.36, fast 17.19.
  - Corrected: 97.83 (score 64.43), held 101.1.
  - Reason: member 9, the dog sector plus its Ti arm, overlaps link 1b's root ramp by 0.18 mm on every K-open pose.
- **Both numbers reproduce to the digit here.** Through the verifier harness I get 22.64 -> 97.83 and 25.36 -> 101.1.
  Through the model alone I get 22.64 and 25.36.
- **The 97.83 is the lenient reading.** The verifier held the arm-link 1b pair to 0.15 mm. The model holds the other
  adjacent pair through K (horn-link 1b) to 1 mm. Read at 1 mm, all 374 taken bench poses fail (`strict_1mm` in the
  row's verification).
- **No surface ranks the old numbers.** The dashboard's live headlines and leader list drop refuted rows
  (`docs/dashboard/core.js` line 9, `leader.js` line 4). The row's top-level `gap` 17.19 and `sweep_gap` 17.19 still
  sit in this row's own columns; the tool's `reporting` check flags that.
- **Why nothing is gamed.** No number on record ranks this design above a better one, and no hard rule is broken by
  the number on record: 3 active DOF, 0 passive translations, O20 hubs, fold margin >= 5.
- **Why watch.** The tool gives 6 watch checks, and the judgement pass adds 7 watch findings: M3, NEW-silent-check,
  G1, M2, M5, R3 and G5.

## What the wearer gets (measured)

Columns:
- **corrected** is the number on record: the verifier's wear, with the poses that fail its per-pose checks dropped.
- **claim** is the refuted 22.64 wear.
- **lead** is slipper-nose-knuckle-3r, verified 18.49 / 23.45 (`remeasure/slipper-nose-knuckle-3r_{bench,held}.json`
  and `_probe_{bench,held}.json`).

Each cell gives bench / held out.

| | corrected | claim | lead |
|---|---|---|---|
| gap | 97.83 / 101.1 | 22.64 / 25.36 | 18.49 / 23.45 |
| overhead reach (workspace, elev >= 140), taken / total | **4 / 28**, 13 / 71 | 8 / 28, 19 / 71 | 8 / 28, 18 / 71 |
| raised-arm reach (workspace, elev 90-140) | **21 / 85**, 62 / 229 | 40 / 85, 98 / 229 | 38 / 85, 96 / 229 |
| all workspace reach | 125 / 360, 312 / 952 | 264 / 360, 670 / 952 | 261 / 360, 650 / 952 |
| taken poses with metal < 2 mm (< 1 mm) | 33 of 191 (17), 73 of 430 (35) | 52 of 374 (20), 122 of 872 (50) | 30 of 371 (3), 67 of 852 (14) |
| overhead workspace poses taken with metal < 2 mm | 4 of 4, 12 of 13 | 7 of 8, 17 of 19 | 4 of 8, 10 of 18 |
| contact poses, summed / deepest depth | 9, 26.11 / 10.92 mm; 17, 51.48 / 10.67 mm | the same poses | 2, 14.75 / 9.0 mm; 10, 46.12 / 9.06 mm |
| in-band 2-14 on the scored clip frames | 0.8695 / 0.8651 | 0.8638 / 0.8617 | 0.8955 / 0.8943 |
| in-band on the taken workspace poses (unscored) | 0.793 / 0.802 | 0.843 / 0.846 | 0.856 / 0.861 |
| in-band at the raised arm (workspace, elev 90-140, unscored) | 0.725 / 0.783 | 0.810 / 0.824 | 0.800 / 0.822 |

Sources: `remeasure/dogring-draglink-knuckle-3r_vprobe_{bench,held}.json` (probes.corrected / probes.claim) and
`remeasure/dogring-draglink-knuckle-3r_{bench,held}.json`.

**Where the contacts are.**
- The deepest press is 10.92 mm at plane 15, elev 165, axial -60 (overhead). The lead presses 9.0 mm at the same pose.
- The design also presses where the lead does not, behind the back at mid elevation:
  - 7.18 mm at (-75, 60, 120) and 3.32 mm at (-60, 60, 105) on the bench;
  - 9.4 mm at (-90, 60, 120) and 6.54 mm at (-90, 60, 105) held out.
- The screen's own split puts the sector and arm in 5 of the 9 bench contacts.
- Against the lead, the summed depth is x1.77 and +11.36 mm on the bench, and x1.12 held out. That is under the T5
  margin (x2 AND +5 mm), so it is reported, not flagged.

**The mechanism the wearer feels.**
- Springs: one, K's spiral spring (the lead's).
- Stops:
  - stop A for K at rest;
  - stop B at a1max 74.5 deg, which is bk1 + bk2 - 5.5: 5.5 deg off the K dyad's stretch, a stated rule (the lead
    sits 5.27 deg off).
- The drive:
  - It works one way: link 2's flank pushes the sector. On the way back the spring must back-drive the 4R.
  - Transmission angle down to 54.5 deg: `pa_max_taken` 35.5 deg on the fit bench; the 4R table ends at PA 42.
  - The ring turns up to 32 deg, and K moves 0-44.0 deg on the bench.
- Cuff twist and spring lag: **not measured**. No R17 / dynamics run and no CAD exist for this design.
- Singular postures: the own-state fold margin in `th` is at least 5.389 deg on the bench and 5.189 held out (forced
  pose), with none under 5. Clean.
- DOF and complexity: 3 active, K slaved, 0 passive translations. The estimated complexity is 25.25-27.25, against the
  lead's 22.25 (finding G5).

## The 12 checks (tool)

| check | level | reading |
|---|---|---|
| held_out | ok | 25.36 vs 97.83. This pairs the claim's held out with the corrected bench (proposal B). Like with like: +2.72 claim, +3.27 corrected; both ok. |
| fast_frozen | watch | fast 17.19 against verified 97.83 (+80.64) |
| near_touch | ok (report only) | plain 22.64; < 1 mm 31.89; < 2 mm 53.61; < 3 mm 160.21; band read as 3-14 mm 23.2 (re-measured claim) |
| contact_depth | ok | "not measured": the tool does not read the verifier's `corrected_contact_depth`, which reproduces 97.83 (proposal C). Read by hand above: under the margin. |
| dominance | ok | vs the lead: plain -4.15, 2 mm -20.59 (behind on both) |
| continuity | watch | no flood on file |
| fold_margin | ok | 5.189 deg minimum (held) |
| idle | watch | **instrument false positive.** The "rigid knee" that moves 65.47 deg is K.qa, the pin knee's designed motion (86-152 deg, the same as the lead's 86.21-151.92). Its skeptics refuted the same reading on slipper-nose and inband-rssr. The drive is not idle: K moves 44.04 deg and the ring 32 deg (proposal D). |
| sampling | watch | horn 0.23 in band, median 16.8 mm, 3.4 % of samples; part-weighted in-band 0.852 against sample-weighted 0.864 |
| complexity | watch | no mechanism record (measured as G5 below) |
| reporting | watch | the dashboard's sweep column shows 17.19 (score 93.75) for this refuted row |
| judge_change | ok | no bench, judge or metric file in the row's 2 commits |
| rules | ok | O20, fold margin >= 5, passive translations <= 2 |

## Findings (judgement pass)

### M3 (watch): the claimed 22.64 was bought by a clash nobody checked

**Evidence.**
- The family's per-pose `collide()` exempts the crank-link 1b pair as adjacent. In the lead that is safe, because the
  crank only pivots on link 1b.
- Here the same slot (member 9) is a 24.4 mm Ti arm that turns up to 32 deg about J2's axis, over link 1b's root ramp.
- Its "stacked over link 1b" level is read once, at phi 0, at the link-1b point nearest the arm's centreline (model
  line 238). The up-joggled root is set on line 244.
- The verifier measured the arm 0.18 mm inside link 1b at r 15.2 mm from J2's axis on 183 of 374 taken bench poses
  (every pose with K 3.2-44.0 deg), and on 442 of 872 held out. At rest it clears link 1b by only 0.5 mm.
- Re-worn here: corrected 97.83 / 101.1, claim 22.64 / 25.36 (`_vprobe_{bench,held}.json`).

**Why the exo is not better.** Metal that interpenetrates cannot be built. The 22.64 described a mechanism whose arm
and link occupy the same space on half of the taken poses.

**Action.**
- Already refuted.
- Any repaired re-claim (the verifier's repair: lift the arm at least 1 mm over link 1b's root ramp, or route it beside
  link 1b) must add every member-9 and member-8 versus link pair to the per-pose `collide()`, at the family's 1 mm rule.
- The in-band cost of the lifted arm is not yet measured. Its verifier must re-wear the claim with this harness.

### NEW-silent-check (watch): the model's own sector-link 2 check never ran on a claim bench

**Evidence.**
- `DRModel.collide()` (model line 355) returns early when `_dogg` / `_L2ring` are missing.
- The frozen protocol `LS._frozen_model` copies a fixed attribute list from the fit model
  (`longstroke-slipper-knuckle-3r.py` lines 224-229), and these two attributes are not on it.
- So the RING-L2 check guarded only the fit Bench(60,160). It never ran on Bench(110,360) or on the held-out set.
- The verifier re-instated it and lost 0 poses. 0 points depend on it here.
- The same whitelist is copied in 9 other model files. Among the models that load the longstroke parent, only
  dogring's `collide()` guards on an attribute the list leaves out.

**Why it matters.** A check written into the model looks like protection in review, but the claim protocol skipped it.
Here it happened to cost nothing. It is a new pattern, so a catalogue entry is proposed (proposal A).

**Action.** A repaired re-claim should copy every attribute its `collide()` reads, or assert on the claim bench that
each of its per-pose checks ran.

### G1 (watch): metal hugs the skin, overhead most of all

**Evidence.**
- Claim wear, bench: 52 of 374 taken poses have metal under 2 mm, and 20 under 1 mm. The lead has 30 and 3.
- The 10th-percentile overhead pose has metal at 0.06 mm (the lead: 1.82 mm).
- 6 of the 10 overhead clip frames are under 1 mm (the lead: 0).
- Held out: 122 poses under 2 mm and 50 under 1 mm, against the lead's 67 and 14.
- The corrected wear keeps the pattern: every overhead workspace pose it still takes has metal under 2 mm (4 of 4
  bench, 12 of 13 held).

**Why the exo is not better.** Metal at 0.06 mm on the model is metal on a real, bulging arm, and this happens on the
overhead poses that matter most.

**Action.** Report only (the user's near-touch ruling, tool 2026-10-17.2). This is not gamed: the design is already
behind the lead on the plain gap.

### M2 (watch): drag-link eyes modelled at O8 against the stated O9

**Evidence.**
- The model's docstring (line 13) and the row say "O9 eyes on 2 x MR63ZZ".
- `EYE_R = 4.0` (line 51) samples O8 discs and sets the horn's reach.
- The arm tip's eye at c1 is not sampled as a disc at all.
- With `EYE_R = 4.5` in memory only, the claim moves 22.64 -> 22.76 and the corrected wear 97.83 -> 97.95 (+0.12;
  in-band 0.8638 -> 0.8626; `_vprobe_bench_EYE_R4.5.json`).

**Why the exo is not better.** The stated part is bigger than the modelled one, and the 0.12 points belong to a part
that does not exist at that size.

**Action.** A re-claim models the eyes at the part it names. This does not move any ranking.

### M5 (watch): the spring return through the 4R is unmeasured

**Evidence.**
- The dog only pushes. On return, K's spiral spring must back-drive horn -> drag link -> arm -> sector.
- It works against the sector's turn on hub 2's housing and 4 MR63ZZ, at transmission angles down to 54.5 deg.
- The row's "R17 ok" is static determinacy only.
- No dynamics, preload or lift-off-on-return number exists for this design. The lead has the same gap: its skeptic
  upheld M5 as missing.

**Why it matters.** A lagging return means K lags q2. The wearer gets cuff twist (G3) or a bind at the onset of the
lost-motion dwell.

**Action.** Measure it with judge/dynamics.py R17 before any CAD of a repaired version.

### R3 (watch): best of several frozen-exact wears, no spread

**Evidence.**
- The red team says "Selection was by frozen".
- The doc names at least 4 frozen wears: 22.64 (the pick), 24.34, 29.84 and 26.07.
- The sweep file keeps only fast numbers.
- The held-out drop shows no in-sample gain: +2.72 claim and +3.27 corrected, against the lead's +4.96.

**Action.** Record every frozen candidate and its spread with the claim.

### G5 (watch): more complex than the lead, with no record

**Evidence.**
- The row has no structured mechanism record, so the dashboard shows complexity null.
- From the row note's counts (prot 6, bodies 6, joints 9, loops 3, sliding 0, rolling 0, springs 1, the lead's
  unsensed cuff knee), `tools/simplicity.py` v2.2 gives 25.25-27.25 for 12-14 made and 15-19 bought parts.
- The lead scores 22.25, so this design is 3-5 points more complex.

**Action.** Add the mechanism record to the row; that is the row owner's file, not this audit's.

## Patterns walked and found absent or below threshold

- **T2 (band edge):** clean. Reading the band as 3-14 mm costs 0.56 (23.2 against 22.64). Of the clip samples,
  0.06 % sit under 1 mm and 0.16 % at 1-2 mm (`remeasure/dogring-draglink-knuckle-3r_bench.json`).
- **T3 (fold margin on another angle):** clean. The margin is read in `th`, at least 5.389 / 5.189 deg.
- **T4 (search bound walking to a singular posture):** clean.
  - a1max = bk1 + bk2 - 5.5 is a stated rule, 0.5 deg stricter than the family's 5.
  - dr_zr = 0 and dl_lift = 0 sit at their lower bounds. That is the lowest profile, not a singular posture.
- **T5 (depth-blind contact):** below the margin (x1.77 / x1.12, see above).
- **S1 (skewed sample):** clean. The held-out drop is +2.72 / +3.27.
- **S2 (sparse bad metal):** the tool's watch. The horn is 0.23 in band.
- **S3 (unsampled bodies):** clean. Sector + arm (77 samples), drag link and eyes (52) and horn (32) are all sampled.
- **S4 (contact on the skin sample, not the body):** not applicable.
- **S5 (static islands):** not measured (see below). K is set by the arm (stop A or the dog through the 4R), and the
  pin knee is the lead's.
- **M1 (virtual or zero-size parts):** clean. 0 passive translations.
- **M4 (idle mechanism):** clean on the design. The tool's idle watch is the known false positive.
- **P1, P2 (in-sample tuning, held-out leakage):** clean on the files. The fit is fast, the claim is exact plus held
  out, and the sweep holds no held-out field.
- **P3 (re-measuring until lucky):** see R3.
- **P4 (judge changed with the design):** clean.
- **R1 (self-measured shown as verified):** clean. The status is refuted.
- **R2 (refuted record still displayed):** the tool's watch. The row's sweep column shows 17.19.
- **R4 (pipeline recomputes the number):** the dashboard's v_gap is 97.83, equal to the verifier's.
- **G2 (stiff spring):** the lead's single spring.
- **G3 (cuff twist):** unmeasured, see M5.
- **G4 (singular postures):** clean.
- **G6 (4th sensed joint):** not applicable.

A reporting note, not a finding. The row's verdict reads "v_gap 97.83 vs champion 75.94 (score)", which compares a gap
with a score. Like with like it reads:
- score 64.43 against 75.94;
- gap 97.83 against 66.17.

The conclusion is the same.

## Numbers I could not get, and why

- **Continuity flood.** Not run. The model's `frozen_flood` would flood the refuted 22.64 wear, which is not the number
  on record. The verifier harness has no flood of the corrected wear, and building one did not fit the time box.
- **Spring return, R17 lift-off and cuff twist.** No dynamics model or CAD exists for this design.
- **The repaired design's in-band cost** (arm lifted at least 1 mm over link 1b's root). This is the row owner's
  re-claim, not an audit re-wear.
- **Contact depth through the tool.** It is not read by the tool (proposal C). I read it by hand from the verifier
  files and the probes.

## Proposals (proposals only; none is an input to this verdict)

**A. A catalogue entry for M6, a check silently skipped by the claim protocol.**
- Looks like: a model's per-pose check that runs on the fit bench but returns early on the frozen benches.
- Detect: record the set of `last_clear` keys (or `collide()` pair labels) that fire on the fit bench and on each claim
  bench. A key that fires on fit and never on a claim bench is flagged watch.
- Effect: 0 points on this row (RING-L2 re-instated, 0 poses lost). Not measured on the verified rows.

**B. The tool's held_out check should pair like with like.**
- The change: claim held against claim bench, and corrected held against corrected bench.
- Effect here: -72.47 "ok" becomes +3.27 (corrected) / +2.72 (claim), both ok. No verdict moves on this row.
- Not measured on the other rows: only rows whose verifier files carry both `frozen` and `corrected` are affected.

**C. The tool's contact_depth check should read a verifier's `corrected_contact_depth` when its corrected gap
reproduces v_gap.**
- Effect here: bench 26.11 mm against 14.75 (x1.77), held 51.48 against 46.12 (x1.12): ok, no verdict change.
- Not measured on the other rows.

**D. The tool's idle check should read the K drive's `th_margin.dK_taken_max` (here 44.04 / 45.73 deg) as the declared
moving drive, and skip `K.qa` when the row's mechanism has a two-pin cuff knee.**
- Effect: this row's idle watch goes to ok. The same false positive disappears on slipper-nose and inband-rssr, where
  their skeptics refuted it.
- This is a measurement change of the tool. Bump VERSION and run the self-test.

**E. A tightening, stated as a measurement change.** A body exempted from per-pose clash checks as "adjacent" (it
shares a hub with the other body) but reaching more than the hub radius + 2 mm from the shared axis should be checked
per pose against that body at the family's 1 mm rule.
- Effect on this row: under the 1 mm reading every taken pose fails (verifier `strict_1mm`: 374 of 374), so v_gap
  97.83 -> 275.
- Effect on the verified rows: **not measured.** In the lead family the crank only pivots on link 1b, so the expected
  effect is 0, but this audit did not wear them with the added pair.

## Skeptic (2026-10-17 12:46 UTC)

Run `skeptic:dogring-draglink-knuckle-3r`. Rulings: `docs/alignment/dogring-draglink-knuckle-3r.rulings.json`.
Ledger entry by `skeptic`, 2026-10-17T12:46:25Z. Local, nice, OMP_NUM_THREADS=1, 1 process, $0 farm. Models,
verifier, benches and judges unchanged.

New raw material:
- `tools/alignment_flood_dogring_verifier.py` (new adapter). It runs the continuity flood (`connected_report()`, the
  function the claim's own `LS.frozen_flood` calls) inside the verifier harness (`wear --ring`, exact Bench(110,360),
  frozen) on the corrected wear and on the claim wear.
- Its output: `remeasure/dogring-draglink-knuckle-3r_vflood_bench.json`. Its static gaps reproduce 97.83 and 22.64 to
  the digit.

### Final verdict: WATCH

5 reasons refuted with evidence, 8 upheld. Nothing reaches gamed, and the number on record (v_gap 97.83, refuted)
stands.

### Rulings

| key | ruling | evidence (short; full text in the rulings file) |
|---|---|---|
| fast_frozen | **refuted** | The detector is for P3 / R3 search inflation, and that inflation is small here. The claimed config goes from fit_fast 17.19 to frozen 22.64: +5.45, inside the verified rows' 4.6-14, under ff_watch 14, and equal to the lead's +5.49. 17.19 is not a best of many: the sweep best is 16.57. The other +75.19 is the M3 clash, ruled under M3. The display is ruled under `reporting`. |
| continuity | **refuted** | Measured here (`_vflood_bench.json`). Corrected wear: static 97.83, connected_full 97.83 (0 dropped; envelope 1062 ok, 607 / 607 forced connected), knn 97.83 (0 dropped). Loss 0 <= conn_watch 1. For the record: the literal bench-grid reading is 99.03 (4 dropped), and the claim wear reads full 22.64, knn 25.47 (+2.83), bench-grid 59.37. |
| idle | **refuted** | Instrument false positive. `knee_moved` is set only in the two kneeless models; dogring line 392 only reads it. K.ang 86.20-151.67 is the pin knee's designed range. K moves 44.04 deg on the claim wear and 2.8 / 2.5 deg (bench / held) on the wear on record, both above idle_deg 2.0. See missed 1. |
| sampling | upheld | horn [0.227, 16.8 mm, 32]. It is sampled on the family's 2 mm grid (nn 2.0), so it is not thin. But 77 % of its metal is beyond 14 mm. The part-weighted delta is +1.23, under 3. |
| complexity | upheld | There is no `mechanism` record on the row, and the dashboard shows null. The only number on file is prose (events line 582). |
| reporting | upheld | The bench table shows 17.19 (score 93.75) in 'Sweep best gap' and 'Claimed gap' next to 'refuted'. The column is also mislabelled: the sweep best is 16.57. |
| judgement:M3 | upheld | -0.18 mm on 183 of 374 taken poses (held 442 of 872); arm_L1b_pass_K_max_deg 2.8; lt1 374 / 374. Re-worn to the digit. |
| judgement:NEW-silent-check | **refuted** | It costs 0 on this claim, measured on both benches. With RING-L2 skipped (model frozen()) the wear gives 22.64 / 25.36, why.parts 0 / 0. With it re-instated (verifier ring_fix true) it gives 22.64 / 25.36, why.parts 0 / 0. Proposal A (M6) stays a proposal for future claims. |
| judgement:G1 | **refuted** (level) | The counts are confirmed: bench 20 / 52 of 374, held 50 / 122 of 872, against the lead's 3 / 30 and 14 / 67; p10 0.06 mm. Near-touch is report-only, as documented (ALIGNMENT.md 2026-10-17.2, c_near_touch lvl ok, CLAUDE.md decisions 3 and 6). Scored contact depth is x1.77 the lead's, under T5. Same ruling as inband-rssr G1. |
| judgement:M2 | upheld | EYE_R 4.0 (O8) against the stated O9 on MR63ZZ (O6 OD). Worn at 4.5: 22.76 / 97.95, +0.12. |
| judgement:M5 | upheld | Missing. No dynamics / R17 / CAD file for this design; the doc's 'R17 ok' is static determinacy only. |
| judgement:R3 | upheld | Missing spread. The sweep file has no frozen field, and no frozen records are in the cloud-sweep cache. Held +2.72 / +3.27 is a mitigation, not the spread. |
| judgement:G5 | upheld | Re-derived with simplicity.py v2.2: 25.25-27.25 against the lead's 22.25. |

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **The number on record is worn with its drive parked.**
   - Every pose that survives the verifier's clash check has K <= 2.8 deg on the bench and 2.5 deg held
     (`verify _v_*_frozen.json checks.arm_L1b_pass_K_max_deg`). Every K-open pose from 3.2 / 3.1 deg up is dropped.
   - So 97.83 is the lead's chain with K essentially on stop A. The drive is 0.8 / 0.5 deg above `idle_deg` 2.0.
   - The audit's "the drive: ring up to 32 deg, K 0-44 deg" and proposal D's `dK_taken_max` 44.04 / 45.73 describe the
     refuted claim wear, not the wear the 97.83 belongs to.
   - Proposal: the tool's idle reading, and every "what the wearer gets" span, should be read on the pose set of the
     number on record (the corrected taken set) whenever a verifier drops poses.
   - Not gaming: it makes the number worse. It does mean the drive contributes no tracking to the record.
2. **The refuted claim leaned on envelope stepping stones.**
   - Claim-wear flood: knn 25.47, which loses 2.83, just under the 3-point escalation (`conn_gamed`).
   - Bench-grid 59.37, with 128 forced poses dropped and 22 of them without a taken neighbour.
   - The full-envelope reading (the rule) keeps 22.64.
   - It is moot for this refuted row. Record it for a repaired re-claim, whose arm lift will move the forced poses.

### Proposals (measurement changes; none is an input to this verdict)

- **Read idle and spans on the corrected set.** As in missed 1. Effect on this row: idle reads K 2.8 / 2.5 deg, still
  ok at 2.0. Effect on the other rows: only rows whose verifier drops K-open poses; not measured.
- **Store the flood next to the verifier's corrected wear.** When a verifier drops poses, the flood should run on the
  corrected wear in the same harness, so the continuity check reads the number on record.
  `tools/alignment_flood_dogring_verifier.py` is the pattern, and it costs about 2 s on top of the wear.
