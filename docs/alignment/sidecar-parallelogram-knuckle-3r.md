# Alignment audit: sidecar-parallelogram-knuckle-3r (verified, round 8 pick 1)

Hourly audit of 2026-10-19, 00:46-01:15 UTC. Ledger entry 2026-10-19T01:09:05Z (`by auditor`, run
`audit:sidecar-parallelogram-knuckle-3r`, git c7316ce). It was due because commit ec77d25 (simplicity v2.1,
2026-10-17 04:55) touched the row after the last ledger entry (skeptic, 2026-10-16 20:55). That commit changed only the
row's complexity, 49.0 to 25.5. The claim did not move, and the model's import chain (the sidecar core, the frontload
module, the pin knee, the bench, the kit) has not changed since the verification (git log since 2026-10-16 20:27).

The audit edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed no score. It added one tool,
`tools/alignment_drive_cap_wear_sc.py` (a one-module adapter so that `tools/alignment_drive_cap_wear.py` can reach a
model that imports the sidecar core as `SC`). It ran locally (nice, OMP_NUM_THREADS=1, at most 2 processes), with no
farm, so $0.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **19.13** (score 93.04), frozen exact Bench(110,360), held out **22.03** (score 91.99).
  Both re-wears reproduce it to the digit.
- **Complexity:** 25.5 (tools/simplicity.py 2.2), equal to the row.
- **Ledger reasons (14, all watch):**
  - From the tool (4): `dominance`, `continuity`, `fold_margin`, `reporting`.
  - From this judgement pass (10): NEW-catalogue-drive, M2, NEW-unpriced-stops, G4, M5, S3, G1, G5, S1, R1.
  - None is gamed. No finding shows the number ranking this design above one that is better for the wearer under the
    same harness, and no hard rule is broken.
- **What changed since the last entry:** nothing in the design. Three rules written after the verification now apply,
  and this audit measured each:
  1. The lead's MR63ZZ knee rule: 0.00 on the bench, +0.06 held out.
  2. The catalogue ball-link cap: +1.12 on the bench, +0.63 held out.
  3. The folded stop priced at +0.5 deg: +0.28 on the bench.

## What the wearer gets (measured)

| item | bench (Bench(110,360) exact) | held out | file |
|---|---|---|---|
| plain gap / score | 19.13 / 93.04 | 22.03 / 91.99 | remeasure `_bench_perpose.json`, `_held.json` |
| overhead reach (elev >= 140), taken / total | 8 / 28 (0.286) | 19 / 71 (0.268) | row; verify `_v_held_frozen.json` |
| raised-arm reach (elev >= 90) | 42 / 113 (0.372): 90-120 22/51, 120-140 12/34, 140-160 5/13, 160+ 3/15 | not measured | `_probe.json` ws_reach_by_elev |
| why overhead poses are lost | fold 14, slide 4, contact 2 | fold 35, slide 13, contact 4 | row; verify held |
| taken poses with metal < 2 mm | 44 of 369 (2 < 1 mm, min 0.651 mm) | 96 of 859 (11 < 1 mm, min 0.275 mm) | `_bench.json`, `_held.json` |
| overhead floor | 7 of 8 taken overhead poses and 8 of 10 overhead clip frames at 1-2 mm; p10 1.17 mm | p10 0.83 mm | `_probe.json`, `_held.json` |
| contact (penetration) | 4 poses, sum 1.82 mm, deepest 0.90 mm at (60, 150, -105), overhead | 9 poses, sum 18.22 mm, deepest 4.99 mm at (-90, 60, 120); 3 deeper than 3 mm | `_bench_perpose.json`, `_held_perpose.json` (gaps reproduce 19.13 / 22.02) |
| workspace in-band 2-14 (unscored) | 0.870 (taken workspace poses), overhead 0.937 | not measured | `_probe.json` |
| scored in-band 2-14 | 0.9049 (0.0049 over the 0.90 target) | 0.9031 | row |
| fold margin in th (family reading) | min 5.011 deg, 0 poses < 5 | not measured | `_msub_rest_bench.json` |
| J1-K-J3 sub-chain with K at rest | m_sub < 5 deg on 117 of 222 rest poses, < 1 on 51, min 0.000 | not measured | `_msub_rest_bench.json` |
| springs | one clock spring keeps the K drive on its law; K leaves stop A on 147 of 369 taken poses | | `_msub_rest_bench.json` |
| stops | folded J2 stop at smlo 5.0 (on the floor); stop B at dK 41.0 (K taken to 37.31 bench, 37.06 held) | | row |
| knee window | [24.79, 155.21]; taken knee angle 93.5-149.4 (bench), 93.5-149.7 (held): 5.5 deg short of the stop | | `_bench.json`, `_held.json` coord_spans |
| cuff twist / K lag | not measured: no CAD, so no R17 | | pipeline/full-exo/designs/ |

For the wearer, this is the lead's chain with a strap-level rod drive. The drive is honest: it carries 37 deg of K, has
0.000 mm closure error, and adds no gear, pulley or cable. Overhead is still the gap. Only 8 of the 28 overhead
workspace poses are reached, all lost to the fold. The overhead poses it does reach are the ones where the metal
hugs the arm at 1-2 mm.

## Checks (tools/alignment_audit.py 2026-10-18.1, re-run after the re-wears)

| check | level | reading |
|---|---|---|
| held_out | ok | 22.03 vs 19.13 (+2.90), re-measured this audit |
| fast_frozen | ok | fast 10.63 -> verified 19.13 (+8.50) |
| near_touch | ok | 1 mm 20.22, 2 mm 50.14, 3 mm 150.75; band 3-14 mm 19.13; 31.01 points in the 1-2 mm shell |
| contact_depth | ok | bench 4 poses, sum 1.82 mm, deepest 0.90; held 9, sum 18.22, deepest 4.99. The reference (conecut-knee) has no depth on file |
| dominance | **watch** | beats frontload-lobe-stopb by 3.69 plain, loses by 6.06 at 2 mm. The skeptic ruled this a trade-off, not a fake gain (rulings.json) |
| continuity | **watch** | static 19.13 = connected full 19.13; the knn flood loses 3.08 (22.21); bench grid 45.03 |
| fold_margin | **watch** | nothing on the row or verifier files. This audit measured 5.011 deg (`_msub_rest_bench.json`), but the tool reads only row and verify files (proposal 4) |
| idle | ok | K 35.87 deg, crank 36.3 deg, knee 52.68 deg |
| sampling | ok | sample-weighted in-band 0.905 vs part-weighted 0.921; rod 12 samples |
| density | ok | no part over 2x the kit's density |
| complexity | ok | 25.5 = row (hand count) |
| reporting | **watch** | the verdict text reads as a self-measured screen; the dashboard's sweep best 10.63 sits 8.50 below the verified number |
| judge_change | ok | no bench, judge or metric file in the 4 commits that touched the row |
| rules | ok | O20, margin >= 5, translations <= 2 |

## Re-wear (the remeasure file predated the row's last commit)

All of these are the model's own `frozen()` and `frozen_held()`, unchanged, with `CB_EXACT=1`.

| wear | plain | 1 mm | 2 mm | in-band14 | reach | file |
|---|---|---|---|---|---|---|
| bench, per-pose dump | **19.13** (recomputed 19.13) | | | 0.9049 | 0.7194 | `_bench_perpose.json` (187 s) |
| held out, deep remeasure | **22.03** | 24.44 | 48.71 | 0.9031 | 0.6901 | `_held.json` (409 s) |
| held out, per-pose dump | 22.03 (recomputed 22.02) | | | 0.9031 | 0.6901 | `_held_perpose.json` |
| bench, stk 6.0 (MR63ZZ knee) | 19.13 (+0.00) | 20.22 | 50.19 | 0.9014 | 0.7194 | `_stk6_bench.json` |
| held, stk 6.0 | 22.09 (+0.06) | 24.50 | 48.71 | **0.8994** | 0.6901 | `_stk6_held.json` |
| bench, drive cap dK 35.4 (KBRM-02 eye) | 20.25 (+1.12) | 21.35 | 49.75 | 0.9049 | 0.7083 | `_cap354_bench.json` |
| held, drive cap dK 35.4 | 22.66 (+0.63) | 25.09 | 49.19 | 0.9031 | 0.6838 | `_cap354_held.json` |
| bench, smlo 5.5 (stop +0.5 deg) | 19.41 (+0.28) | 20.50 | 50.45 | 0.9049 | 0.7167 | `_smlo55_bench.json` |

The bench deep remeasure of 2026-10-16 (`_bench.json`, git c932f10) was not re-run, because the per-pose dump re-wears
the same call and reproduces it field for field (gap, reach, in-band, contact). That file stays as it was.

The three rule readings together are not measured. Applied one by one they add 1.12 + 0.28 + 0.00 = 1.40 on the bench
(about 20.5) and at least 0.63 + 0.06 = 0.69 held out (smlo 5.5 held out was not run).

## Findings (all watch)

1. **NEW-catalogue-drive.**
   - *Pattern:* a part modelled smaller than the catalogue part.
   - *Evidence:* the claim samples an O7 acetal ball-link socket and runs K to the model's stop B at 41 deg. The
     catalogued igus KBRM-02 (head O9 x 4) pinches hub 2 past dK 35.4 on this core (docs/research/sidecar_mechanism_redteam.md
     finding 2). This row takes K to 37.3 deg. With the cap at 35.4 it reads 20.25 / 22.66 (+1.12 / +0.63).
   - *Why the exo is not better by that much:* the 4 bench poses past 35.4 need a custom eye that nobody has drawn.
   - *Action:* proposal 1.
2. **M2.**
   - *Pattern:* a component smaller than the real one.
   - *Evidence:* the knee stack stk 4.8534 is inherited, against 6.0 for the MR63ZZ pairs the lead's rule requires.
     Bench +0.00, held +0.06. Held out, in-band falls below 0.90 (0.8994).
   - *Why it matters:* the bench in-band margin is now 0.0014, so any further thickening costs gap.
   - *Action:* proposal 2.
3. **NEW-unpriced-stops.**
   - *Pattern:* a stop placed exactly on the rule.
   - *Evidence:* smlo 5.0 is the user's floor. The taken poses come within 0.011 deg of it: min 5.011, three poses
     under 5.14. A +0.5 deg build tolerance costs +0.28.
   - *Why it matters:* the rule holds, but on the stop's nominal position only.
   - *Action:* proposal 3.
4. **G4.**
   - *Pattern:* a near-singular posture.
   - *Evidence:* with K at rest, the J1-K-J3 sub-chain sits at its fold on 51 of 222 rest poses (m_sub < 1 deg). This
     is the same as the family (sidecar-longdyad 145 of 250 under 5).
   - *Status:* open with the user (B1).
5. **M5.**
   - *Pattern:* a spring that may not hold.
   - *Evidence:* one clock spring holds the whole drive on its law over 147 K-open poses. No R17 has run, because no
     CAD exists.
6. **S3.**
   - *Pattern:* an unsampled body.
   - *Evidence:* the crank's short arm, the follower and the lobe ring are not sampled metal. They are family-wide and
     not measured.
7. **G1.**
   - *Pattern:* hugging.
   - *Evidence:* 31.0 points live in the 1-2 mm shell, double sidecar-longdyad's 15.1 on the same drive. 7 of 8 taken
     overhead poses have their floor at 1-2 mm.
   - *Status:* report only (user ruling). The skeptic refuted it as gamed.
8. **G5.**
   - *Pattern:* complexity hidden by the count.
   - *Evidence:* the knee subtraction reads this row at 25.5, below the kneeless twin of the same core at 28.0. No
     rank flips.
9. **S1.** The plain rank is inside noise: 14 rows sit within 0.85 points. The held-out wear is the best 3-joint wear
   on file, and the claim sits mid-spread of its worn ties (18.54 / 19.13 / 19.97).
10. **R1.** The verdict text is stale ('SCREENED ... self-measured', 'complexity 49'). The fast 10.63 shows in the gap
    fields and the sweep line. The fold margin, contact depth and knee stack are not on the row.

Checked and not present:

- T2: the band read as 3-14 mm moves 0.00.
- T4: the knee window bound does not bind (5.5 deg unused), and ang_min stayed 23.8-31.0 in the sweep, not at a
  bound.
- T5: depth is shallow on the bench (1.82 mm summed). Held out it is about half of sidecar-longdyad's 35.66 mm.
- S2: the rod is in band 0.88.
- M1 and M4: the drive moves 37 deg.
- P2: the search hooks (`bench_eval`, `evaluate`) never load the held bench. It is loaded only in `frozen_held`.
- P3 / R3: the tie-break was declared before the wear, and the claim sits mid-spread.
- P4: no judge change.
- R4: the dashboard v_gap 19.13 now matches the verifier (v_contact on the row).

## Proposals (measurement changes for the lead / the user; not inputs to this verdict)

1. **Claim on the catalogue ball link** (cap the drive at the KBRM-02's dK 35.4, or draw and price the custom O7 eye).
   - Measured effect: this row +1.12 bench / +0.63 held.
   - On file for sidecar-longdyad (with r_h 15.5): +0.85 / +0.86 (`remeasure/sidecar-longdyad-knuckle-3r_rh155cap354_*`).
   - The other sidecar-drive rows (roller-flank, twin-k2, kneeless-sidecar) are not measured.
   - Rows without a ball-link drive: 0.
2. **Every pin-knee claim states `stk` and claims at 6.0** (the MR63ZZ rule).
   - Measured effect: this row +0.00 / +0.06.
   - sidecar-longdyad: +0.30 / +0.30.
   - The other pin-knee rows are not measured here (`tools/alignment_knee_stack_probe.py <id> bench|held` does it in
     about 2 and 6 minutes per row).
3. **Price J2 stops at +0.5 deg of build tolerance** (smlo, smhi >= 5.5 in the claim).
   - Measured effect: this row +0.28 bench.
   - sidecar-longdyad: +0.45 bench (row final_polish.priced).
   - Others are not measured.
4. **Instrument (no score change):** let `c_fold_margin` in tools/alignment_audit.py also read the auditor's own
   `remeasure/<id>_msub_rest_*.json` `family_reading` (min, lt5). This row's watch would then read ok at 5.011. That
   is a tool change, so it needs a VERSION bump and a selftest run; it was not made here.

## What happens next

- The lead or the verifier writes the fold margin (5.011), the knee stack and the per-pose dumps onto the row or into a
  verify file, so that `fold_margin` and `contact_depth` read them without the auditor.
- Before any L1 CAD of this design:
  - run the catalogue-drive wear (proposal 1) and the held-out smlo 5.5 wear;
  - run a 2 mm near-touch search (31 points of the gap sit in the 1-2 mm shell, overhead most of all);
  - run R17 for the clock-spring hold.
- The hourly audit loop re-audits this row when its row or verifier files change.
