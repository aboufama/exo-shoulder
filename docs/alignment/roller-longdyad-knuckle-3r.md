# Alignment audit: roller-longdyad-knuckle-3r

Audit of 2026-10-17 04:03-04:40 UTC (ledger entry `by auditor`, run `audit:roller-longdyad-knuckle-3r`). It replaces
the auditor sections of the 01:42 UTC audit. The skeptic's section of 02:20 UTC is kept below the rule at the end.

**Why it ran: a metric change, not a new claim.** Commit 3ceacea (03:40 UTC) put the user's ruling "if no encoders are
needed, it doesn't count as added complexity" into `tools/simplicity.py` v2. The change does two things:
- it takes an unsensed two-pin cuff knee (`mechanism.cuff_knee`) out of the count before scoring: 2 passive
  rotations, 2 bodies, 2 joints, 4 made parts and 6 bought parts, the template of
  `docs/concepts/skin-normal-3r-pin-knee.md` line 584;
- it drops the 2 knee encoders (`sensed_passive` 2 -> 0).

For this row the complexity went from 43.75 to 24.25. The bench gap did not change.

This audit checks the change on three points:
1. Is the subtraction faithful to this row's own knee?
2. Do the 3 hub encoders really fix the pose without the knee encoders?
3. Does the change flip any ranking?

## Verdict: WATCH (the ruling's premise holds for this row; the subtracted counts are not this row's)

- **The claim** is unchanged: verified gap 18.67 (score 93.21), frozen exact Bench(110,360), held out 23.73. The
  `best_params` have not changed since 70c2230. The 01:34 UTC re-wear reproduced the claim to the digit, so it was not
  re-worn again.
- **The ledger verdict is watch.** It comes from 2 tool checks (contact_depth, complexity) and 8 judgement findings.
  None of them is gamed.
- **Determinacy holds.** With only J1, J2 and J3 read, and K taken from its drive law, every passive coordinate and
  the GH rotation are fixed at every taken pose: 371 on the bench and 852 held out.
  - Smallest hub-only sigma: 0.250 on the bench, 0.246 held out. Worst condition: 3.72.
  - This is the least margin of the three rows measured. sidecar-longdyad gives 0.332, and skin-normal-3r-pin-knee
    gives 0.383, which reproduces its verifier's 0.39.
  - Dropping the knee encoders is therefore not gamed for this row.
- **The subtraction is not this row's knee.** The template takes 4 made parts, 6 bought parts and 2 bodies. This row's
  own record counted its knee as 1 made part, 2 bought parts and 1 body (its kneeless twin's record says so).
  - That over-subtracts 3.5 points.
  - The knee-closure loop stays charged at 4 points.
  - The two errors happen to cancel, to within 0.5 of the kneeless twin.
  - Neither error changes the round-9 tie-break.

## What the wearer gets (measured; unchanged since the 01:42 audit because the claim did not move)

- **Reach:** 261 of 360 workspace poses (0.725), 649 of 952 held out. Overhead (elevation >= 140): 8 of 28 taken,
  18 of 71 held out. Raised arm (elevation >= 90): 46 of 113, 114 of 300 held out.
- **Metal under 2 mm on taken poses:** 30 on the bench, 66 held out. Under 1 mm: 3 and 14. Under 3 mm: 133 against
  the lead's 178. Source: `remeasure/*_perpose_claim.json`.
- **Contact:** 2 bench poses.
  - The deepest is 10.55 mm at (plane 15, elevation 165, axial -60).
  - Held out: 10 poses with a depth sum of 49.88 mm, the deepest 9.54 mm. 4 of them are below elevation 150.
  - Source: tool check `contact_depth`, `docs/alignment/roller-longdyad-knuckle-3r.json`.
- **Workspace in-band (unscored):** 0.854 overall. At elevation 90-140 it is 0.798, against the lead's 0.841.
- **Springs and stops:** one clock-spring cap on K force-closes both rolling pairs. Stops: J2 at 5.0 / 16.84, K stop B
  at a1max 58.77. The horn pressure angle reaches 43.0, which is PA_MAX.
- **Near-singular postures:**
  - The fold margin in th is at least 5.181 (5.031 held out).
  - The knee reaches 151.92 deg (153.16 held out). Its window ends at 154.78 deg.
  - **New in this audit:** the hub-only sensing is weakest at the near-straight knee. The worst pose is
    (75, 165, -75), with the knee at 150.7 deg and dK -18.2.
- **Sensing (new):** 3 hub encoders, K slaved and never read, knee pins unread.
  - A 1 deg hub-encoder error can become up to 3.2 deg of arm-orientation error (raw sigma_min 0.317 rad/rad). On
    the pin knee it is 1.8 deg.
  - In-plane GH drift moves the J3 reading by up to 1.79 deg per mm (median 0.85) with no arm motion.
- **Cuff twist and spring torque:** not measured. All checks stay kinematic.
- **Complexity:** 24.25 under v2, which the dashboard shows. The row's own `complexity` field and its name still say
  43.75.

## (1) Faithfulness of the subtracted counts

| | rot | bodies | joints | loops | made | bought | complexity |
|---|---|---|---|---|---|---|---|
| this row's record (v1, encoders counted) | 5 | 6 | 9 | 3 | 12 | 15 | 43.75 |
| v2 as committed (template subtracted) | 3 | 4 | 7 | 3 | 8 | 9 | **24.25** |
| this row's own knee subtracted, loop kept | 3 | 5 | 7 | 3 | 11 | 13 | 27.75 |
| kneeless twin (the same drive with the knee deleted; loop gone) | 3 | 5 | 7 | 2 | 11 | 13 | 23.75 |

Source: `docs/concepts/rows/kneeless-roller-knuckle-3r.json`, mechanism notes. They say "custom 15 -> 11" (the 3
round-9 merges plus the knee link folded into the bracket) and "bought 15 - 2 iglidur pins = 13".

So this row's record carried its knee as:
- 1 made part, the knee link (the Ti pins are not separate parts);
- 2 bought parts, the 2 iglidur pins (not the 2 x (GSM sleeve + 2 GTM washers) of the template);
- 1 body.

The template therefore removes 3 made parts, 4 bought parts and 1 body that belong to the shoulder mechanism. That is
1.5 + 1.0 + 1.0 = 3.5 points too many.

The knee's closure loop is still charged in this row's record ("Loops: drive, knee closure, K dyad stop", +4). The
template has no loop to subtract, because skin-normal-3r-pin-knee counts 0 loops for the same knee.

The same template error applies to sidecar-longdyad. Its kneeless twin's record goes from 16 to 14 made, 16 to 12
bought and 7 to 6 bodies, which puts it at v2 29.5, 32.0 with its own knee subtracted, and 28.0 for the twin.

## (2) Determinacy without the knee encoders

The tool is `tools/alignment_knee_sensing.py` (new). The model is loaded unchanged and built init-only, with the knee
centre fixed from the Bench(60,160) fit as in `frozen()`. The taken poses come from the 01:34 re-wear's per-pose files.

At each taken pose the tool runs the model's own `ik` and `knee`:
- at the pose's Q, and at Q turned by +-1e-4 rad about x, y and z through GH;
- it reads J1 = q1, J2 = q2, and J3 as the angle of member 3 (Q rot(sn, phi), the model's T(3)) relative to link 2
  about u3;
- the passive coordinates are dK, pin a and pin b.

The hub-only number is sigma_min of N[hub rows], with N the orthonormal null space. That is the same quantity as
`docs/research/rebase/verify_rebase_pinknee.py`.

| row (Bench(110,360) taken) | poses | sigma_min 8 rows (p5) | cond max | raw sigma_min rad/rad (cond max) | dJ3/dq3 | GH drift deg/mm max (median) |
|---|---|---|---|---|---|---|
| **roller-longdyad (this)** | 371 | **0.250** (0.303) | 3.65 | 0.317 (9.11) | 0.58-1.33 | 1.79 (0.85) |
| roller-longdyad, held out | 852 | 0.246 (0.303) | 3.72 | 0.318 (9.33) | 0.58-1.34 | 1.87 (0.85) |
| sidecar-longdyad (ref) | 371 | 0.332 (0.354) | 2.76 | 0.378 (7.91) | 0.63-1.22 | - |
| skin-normal-3r-pin-knee (calibration, kin set) | 359 | 0.383 (0.470) | 2.38 | 0.550 (7.85) | 0.66-1.23 | 1.83 (1.01) |

Files: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_knee_sensing_{bench,held}.json`, with per-pose rows.

On every pose of the table above:
- no perturbed pose leaves the valid set;
- member 3's axis stays on u3 to within 0.015 deg;
- dJ3/dq3 never changes sign, so there is one root and no hidden branch.

With K known from its law, the 9-row form (K as a row) gives 0.248. The calibration on skin-normal-3r-pin-knee
reproduces its verifier (0.39, cond 2.3), so the method measures the same quantity.

**Reading:** the premise "the 3 hub encoders fix the pose" holds for this row. It holds with about 35 % less margin
than the knee it was shown on, and the margin is smallest on forced overhead poses with the knee near straight.

Two conditions lie outside the kinematic model:
- **The clock spring (M5).** If the roller lifts off the flank, K leaves its law and the hubs no longer fix the pose.
- **GH translation (R10).** The pins absorb it, and the J3 reading then moves about 0.85-1.8 deg per mm. This is the
  same as the pin knee, so it is family-wide.

## (3) Rankings and tie-breaks

| verified row | gap | cx v1 | cx v2 |
|---|---|---|---|
| roller-longdyad (this) | 18.67 | 43.75 | 24.25 |
| sidecar-longdyad | 18.91 | 49.0 | 29.5 |
| sidecar-parallelogram | 19.13 | 49.0 | 29.5 |
| minarc-stop | 19.54 | 52.0 | 32.5 |
| sidecar-roller-flank | 20.08 | 45.25 | 25.75 |
| kneeless-roller (twin, no knee) | 21.07 | 23.75 | 23.75 |
| kneeless-sidecar (no knee) | 21.11 | 28.0 | 28.0 |

- **The round-9 tie-break against sidecar-longdyad is unchanged.** It was 5.25 points apart before and after. It
  would be 4.25 with each row's own knee subtracted, or for the twins.
- **This row now ranks simpler than kneeless-sidecar** (24.25 against 28.0, where it was 43.75 against 28.0). The
  order holds under the faithful count (27.75 against 28.0) by 0.25, and this row also has the better gap. So the
  ranking is not wrong for the wearer.
- **Its own kneeless twin is now only 0.5 simpler, where it was 20 simpler.**
  - The twin's reason to exist (no knee, the plain 3R pose read, no near-straight knee) is now nearly invisible on
    the complexity axis.
  - That is the ruling's intent. Physically, though, this row still carries 2 pins, a knee link, 2 more bodies and
    the 0.25 sensing margin.
- **Other pin-knee rows** moved by the same 19.5; skin-normal-3r-pin-knee and raglan-knee-3r now read 0, equal to the
  plain spherical 3R anchor.
  - skinnormal-shortk-knuckle-4r (42.0 -> 32.5) carries a cuff_knee record but is not among the 13 rows of 3ceacea;
    it was added after.
  - geneva-tail-knuckle-pinknee-3r (12, made 4*, bought 3) is a pin-knee row that v2 did not touch, and its record
    looks incomplete.
  - Both are out of this audit's scope and noted for their own audits.

## Findings (`docs/alignment/roller-longdyad-knuckle-3r.findings.json`)

**G5 (watch): the subtracted knee is the template's, not this row's.**
- Evidence: see section (1). v2 gives 24.25, this row's own knee subtracted with the loop kept gives 27.75, and the
  kneeless twin gives 23.75. The row's `complexity` field and name still read 43.75 (tool check `complexity`
  MISMATCH).
- Why the exo is not simpler than the count says: 3 made parts, 4 bought parts and 1 body of the shoulder drive are
  removed with the knee.
- Why this is not gamed: the knee-loop over-charge (+4) offsets it, and no ranking flips toward a worse design.
- Action (lead): give each pin-knee row a `cuff_knee` record counted from its own parts list, decide the knee loop
  (see the user questions), and refresh the row's complexity field and name.

**NEW-knee-sensing (watch): the premise holds, with the least margin measured.**
- Evidence: see section (2).
- Why it matters for the wearer: the MVP1's arm estimate is up to 3.2 deg per deg of encoder error at the worst pose,
  and it drifts about 1 deg per mm of GH translation.
- Action: keep the check in the loop for every pin-knee row (proposal B). Restoring ang_min to at least 26.88, as the
  skeptic asked, also pulls the worst poses away from the straight knee.

**Carried, unchanged claim (skeptic rulings stand):**
- **S1:** the 0.24 round-9 win is a tie. Held out it is 23.73 against 22.67, and P(this design better) is 0.135.
- **NEW-contact-depth:** fewer but deeper presses.
- **NEW-ws-inband:** the raised-arm standoff is worse.
- **S2:** a more real envelope improves the number.
- **G4:** the drive sits at its pressure-angle cap, and the knee runs to 151.92 deg.
- **M5:** one clock spring closes two rolling pairs. Under v2 that spring now also carries the sensing premise.

The old G5 (sensed pins over the cap) is superseded by v2. T4 was refuted by the skeptic and is dropped.

## Patterns walked for this change

| pattern | reading |
|---|---|
| G5 complexity hidden by the count | present (finding G5) |
| G6 4th sensed joint | resolved for this row: 0 sensed passives, and the determinacy holds (finding NEW-knee-sensing) |
| P2 / P3 judge changed with the design, reporting | the metric changed in its own commit with a change log; no bench, judge or gap file moved (tool check judge_change ok); the row's stored complexity field is stale (43.75) |
| R1-R4 re-measuring until lucky, best-of-many | n/a: no new gap claim |
| T1-T4, S1-S5, M1-M5 | unchanged from the 01:42 audit and the skeptic's rulings (claim unchanged); S1, S2, M5 carried |
| G1-G4 | G1 / G4 carried; G2 / G3 (stiff spring, cuff twist) not measurable in the kinematic scope |

## Proposals (not applied; measurement changes for the lead or the user)

- **A. A per-row knee record.** Fill `cuff_knee` from each row's own parts list, not from the skin-normal template.
  Measured effect on this audit's rows: roller 24.25 -> 27.75, sidecar-longdyad 29.5 -> 32.0. The tie-break gap goes
  from 5.25 to 4.25 and its direction is unchanged.
- **B. A sensing gate for an unsensed knee.** Require hub-only sigma_min >= 0.2 (and dJ3/dq3 without a sign change)
  on the bench and held out before `sensed: false` is accepted. Measured: roller 0.250 / 0.246, sidecar-longdyad
  0.332, skin-normal-3r-pin-knee 0.383. All three pass; the roller is the closest.
- **C. One rule for the knee loop.** Either knuckle rows stop counting "knee closure" (the GH loop that skin-normal
  does not count), which takes -4 off the roller, or v2 subtracts it with the knee. Effect on the roller: 24.25 ->
  20.25 (with A: 23.75, equal to the kneeless twin).

## Questions for the user

1. When the knee is "free", should its closure loop be free too? The knuckle rows still pay 4 points for it, and
   skin-normal-3r-pin-knee pays 0.
2. Should the free knee be counted from each row's own parts (this row: 1 made part, 2 bought parts), or as the
   standard 4 made / 6 bought template? The template makes this row 3.5 points simpler than its own parts list.
3. Is a hub-only arm estimate whose error grows by up to 3.2x the encoder error at the near-straight knee, and moves
   about 1 deg per mm of GH drift, "no encoders needed" for MVP1? Or should a cuff IMU or a sensing margin (proposal
   B) be part of the ruling?
4. The kneeless twin (no knee, 23.75) is now only 0.5 points simpler than this row with its knee. Is that the
   intended reading, given that the twin also has no near-straight knee posture?

## Numbers not obtained

- **A re-wear of the claim:** not run, because the claim is unchanged. The 01:34 re-wear reproduced it to the digit
  and `best_params` has not changed since.
- **Determinacy under GH translation (R10):** the bench has no GH translation. Only the per-mm sensitivity is
  reported.
- **Spring torque, roller lift-off under load, cuff twist:** out of the kinematic scope, and no force file exists.
- **Held-out runs for the reference rows:** the sidecar and pin-knee runs cover the bench only;
  the pin knee has no per-pose file, so its kinematic set was used.

Local compute: about 6 runs of under 15 s each, at most 2 processes. Farm: none ($0).


---

_Earlier sections below this rule: skeptic of 2026-10-17 02:20-02:30 UTC (kept unchanged)._

## Skeptic (2026-10-17 02:20-02:30 UTC, ledger entry 2026-10-17T02:29:27Z, `by skeptic`, run `skeptic:roller-longdyad-knuckle-3r`)

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.**
- 2 of the 9 reasons are refuted with measured evidence: `fold_margin` and `judgement:T4`.
- The other 7 stand at watch.
- Rulings: `docs/alignment/roller-longdyad-knuckle-3r.rulings.json`.

**New measurements.** No model, bench, row or score was changed.

The fit-bench grid cache (key 0089c747c10f, Bench(60,160)) was rebuilt locally at 01:59. That made the auditor's
"not obtained" paired comparison on the exact claim protocol possible.
- 4 farm dumps with `tools/alignment_paired.py` reproduce the claims to the digit:

  | design | bench | held out |
  |---|---|---|
  | this design | 18.67 | 23.73 |
  | the lead | 18.91 | 22.67 |

  Files: `remeasure/*_perpose_claim.json` and `remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json`.
- 2 held-out re-wears at the knee bounds ang_min 26.88 and 30.46:
  `remeasure/roller-longdyad-knuckle-3r_angmin{26.8823,30.46}_held_skeptic.json`.
- Farm cost: 6 jobs, about 860 worker-s, about $0.07.

### Rulings

**fold_margin: REFUTED.** The margin is on file 4 times, and every reading is at or above TH fold_min 5.0.
- `rows/roller-longdyad-knuckle-3r.json` `verification.th_margin_min`: bench 5.181, held 5.031, lt5 0.
- `verify/roller-longdyad-knuckle-3r_v_bench_frozen.json` `extra.th_margin`: min 5.181, n 371, lt5 0.
- `_v_held_frozen.json` `extra.th_margin`: min 5.031, n 851, lt5 0.
- The fit-fast reading is 5.011.
- Cause of the false watch: the tool's regex ends at `th_margin$`, so it skips `th_margin_min.*`. The dict
  `extra.th_margin` carries no plain number.

**judgement:S1: stands, and is now measured on the claim protocol.**
- Bench: difference -0.25, paired SD 1.35, 90 % interval [-2.62, +1.73], P(this design better) 0.605.
- Held out: +1.06. The reach term is +0.84, and the lead takes 29 workspace poses this design misses, against 21.
  The 90 % interval is [-0.47, +2.39], and P(better) is 0.135.
- Pooled: +0.69, 90 % interval [-0.56, +1.83], P(better) 0.191.
- The perturbed fit had given P 0.23 / 0.29, so it understated the lead's out-of-sample edge.
- My own bootstrap of the auditor's perturbed dumps reproduces his numbers: SD 1.39, P 0.58 on the bench and P 0.22
  held out.
- The 0.24 is noise.

**judgement:NEW-contact-depth: stands.** Per pose, on the claim protocol:

| set | design | contacts | depth sum | deepest | deeper than 3 mm |
|---|---|---|---|---|---|
| bench | this design | 2 | 16.46 mm | -10.55 mm | |
| bench | the lead | 4 | 6.23 mm | -4.61 mm | |
| held out | this design | 10 | 49.88 mm | -9.54 mm | 7 |
| held out | the lead | 10 | 35.67 mm | -8.37 mm | 5 |

One correction to the auditor: not every press is overhead. Held out, 4 of this design's 10 presses are below
elevation 150:
- -5.51, -3.49 and -1.60 mm at elevation 60 (planes -90 / -75, axial 105-120);
- -1.22 mm at elevation 105.

**judgement:NEW-ws-inband: stands.** From the probe files on the claim protocol:
- At elevation 90-140, workspace in-band is 0.7979 against 0.8409.
- The shortfall is metal standing off more than 14 mm (over14 0.2012 against 0.1565), so the raised-arm profile is
  bulkier.
- Taken poses with metal under 2 mm: 30 against 26 on the bench and 66 against 63 held out.

**judgement:S2: stands.** The envelope-corrected gap is 18.56 against 18.67 (in-band 0.8948 against 0.8937, with 9 head
points and 10 edge points). ROUNDS.md line 1208 prints 18.56 in the winner's row.

**judgement:G4: stands, and is tighter held out.**
- Held out (`_v_held_frozen.json` `extra`): pa_horn_max 43.0 = PA_MAX. dK_taken_max is 46.17 of the 46.25 limit, which
  is 0.08 deg from the cap; the bench figure was 45.62.
- At PA 45, no pose fails on either set.
- No force file exists.

**judgement:T4: REFUTED by re-wear.** The walked bounds do not buy the number.

| ang_min | bench | held out |
|---|---|---|
| 25.22 (claim) | 18.67 | 23.73 |
| 26.88 | 18.67 | 23.72 |
| 30.46 | 18.71 | 23.55 |

- K dyad: the largest a1e on a taken pose is 54.43, 9.61 deg short of stretch (bk1 + bk2 = 64.03).
- Stop B sits 0.27 inside the 5-deg guard (the lead sits at 0.00). The interior angle is 134.5 deg.
- The th margin is at least 5.031.

**judgement:M5: stands.** No spring-torque or closure-force output exists for this design. K moves on 167 of 371 taken
bench poses and 399 of 851 held out, so the cap is loaded on about 45 % of poses.

**judgement:G5: stands.** The mechanism record has 2 sensed_passive knee pins. If they count under the 2026-10-17 ruling,
the design reads 5 coordinates, over the 4-DOF cap. That is the user's question.

### Missed by the auditor (for the next audit; does not change this verdict)

1. **The pin knee runs closer to straight than the lead's, for no score.**
   - The knee window is [ang_min, 180 - ang_min] (`docs/concepts/models/skin-normal-3r-pin-knee.py` lines 14 and 55).
     Walking ang_min from 26.88 to 25.22 therefore also raised the straight-knee limit from 153.12 to 154.78 deg.
   - The taken knee reaches 151.92 deg on the bench and 153.16 held out (`remeasure/*_bench|held.json`
     `deep.coord_spans` K.ang). The lead reaches 146.14 and 150.86.
   - Held out, the claim uses 0.04 deg of window the lead does not have.
   - That walk is worth 0.00 on the bench and 0.01 held out. At H1's 30.46 window the gap is 18.71 / 23.55.
   - The auditor's "re-wear identical" was bench only.
   - Action for the polish or CAD: restore ang_min to at least 26.88 (better 30.46) at no measured cost.
2. **Below-shoulder presses held out.** 4 of the 10 held-out contacts (both designs) sit at elevation 60-105, at plane
   -90 / -75 with axial 105-120, which is the arm across the body and rotated. The "all overhead" reading hid them.
3. **The drive cap is tighter than reported.** Held out, dK reaches 46.17 of the 46.25 limit (0.08 deg from the cap),
   and the horn pressure angle reaches 43.0.
4. **The claim-protocol paired numbers** strengthen S1. Out of sample, P(this design better) is 0.135 (pooled 0.191).
   The auditor's perturbed-fit P was 0.23 / 0.29. Proposal A's held-out form ("the held-out gap under the same harness
   is not worse") blocks this lead change on the exact protocol: 23.73 against 22.67.
5. **Where the extra 1-2 mm poses come from.** On the claim protocol, taken poses with metal under 2 mm on the scored
   (in-band) samples are equal on the bench (25 against 25), and 61 against 58 held out. This design's extra
   near-touch poses (30 against 26 on the bench) come from the model's contact-only walls and crowns (`M.cmin`), which
   in-band never sees.

**Final verdict: WATCH.** The 0.24 round-9 win is a measured tie; the lead is likelier better out of sample. Not gamed.
