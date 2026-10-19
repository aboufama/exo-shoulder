# Alignment audit: sidecar-roller-flank-knuckle-3r (verified, round 8 pick 2)

Hourly audit of 2026-10-19, 01:09-01:35 UTC. Ledger entry 2026-10-19T01:31:23Z (`by auditor`, run
`audit:sidecar-roller-flank-knuckle-3r`, git b3a9a60).

- **Why it was due:** commit ec77d25 (simplicity v2.1, 2026-10-17 04:55) touched the row after the last ledger entry
  (skeptic, 2026-10-16 20:55). That commit and 3ceacea changed only the row's complexity: 45.25 to 21.75, plus the
  cuff_knee sub-record.
- **What did not change:** the claim. The model's import chain (the sidecar core, the frontload module, the geneva
  module, the pin-knee polish, the minarc mechanism, the bench and the kit) has not changed since the 2026-10-16 20:32
  bench remeasure (last commits 2026-10-16 04:07-19:39).
- **What this audit touched:** no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and no score. It added no
  tool. It ran locally (nice, OMP_NUM_THREADS=1, at most 2 processes) on a box at load 10-15 from other agents. No farm
  was used (the CPU budget line is spent), so the cost was $0.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **20.08** (score 92.70), frozen exact Bench(110,360), held out **22.35** (score 91.87).
  Every re-wear in this audit reproduces it to the digit.
- **Rank:** 19th of 37 verified rows and 15th of the 3-joint rows on the plain gap. Held out it is second of the
  3-joint wears on file: 22.35, against sidecar-parallelogram 22.03, conecut-knee 22.38, sidecar-longdyad 22.67,
  slipper-nose 23.45 and roller-longdyad 23.73.
- **Complexity:** 21.75 (tools/simplicity.py 2.2), equal to the row.
- **Ledger reasons (12, all watch):**
  - From the tool (3): `dominance`, `fold_margin`, `reporting`.
  - From this judgement pass (9): T5, G1, M2, G4, M5, M3, S3, G5, R1.
- **Why none is gamed:** no finding shows the number ranking this design above one that is better for the wearer under
  the same harness, and no hard rule is broken:
  - The fold margin in th holds: 5.49 deg on the bench and 5.02 held out, with no pose under 5.
  - It has 3 active DOF, 0 passive translations and O20 hubs.

## What the wearer gets (measured)

| item | bench (Bench(110,360) exact) | held out | file (docs/alignment/remeasure/ unless stated) |
|---|---|---|---|
| plain gap / score | 20.08 / 92.70 | 22.35 / 91.87 | `_bench_perpose.json` (recomputed 20.08), `_probe_held.json` |
| overhead reach (elev >= 140), taken / total | 8 / 28 (0.286) | 19 / 71 (0.268) | `_probe_bench.json`, `_probe_held.json` |
| why overhead poses are lost | fold 14, slide 3, contact 3 | fold 35, slide 11, contact 6 | same |
| raised-arm reach (elev >= 90) | 46 / 113 (0.407): 90-120 25/51, 120-140 13/34, 140-160 5/13, 160+ 3/15 | 119 / 300 (0.397) | `ws_reach_by_elev` |
| taken poses with metal < 2 mm | 45 of 370 with the model's walls (41 on sampled metal), 1 < 1 mm (min 0.32 mm), 171 < 3 mm | 108 of 868 (2 mm count), 14 workspace poses < 1 mm (min 0.17 mm) | `_bench.json`, `_bench_perpose.json`, `_probe_held.json` |
| overhead floor | **all 8 taken overhead poses < 2 mm** (1 < 1 mm); 8 of 10 overhead clip frames at 1-2 mm | **all 19 < 2 mm, 7 < 1 mm**; 18 of 19 clip frames at 1-2 mm | `ws_overhead140`, `clip_overhead140` |
| contact (penetration) | 5 poses, sum 22.09 mm, 3 deeper than 3 mm; **deepest 12.57 mm at (15, 165, -60), overhead**; next 5.45 mm at (30, 165, -60) | 10 poses, sum 59.91 mm, 8 deeper than 3 mm; deepest 11.08 mm at (30, 165, -45) | `_bench_perpose.json`, `_probe_held.json` contact_poses |
| workspace in-band 2-14 (unscored) | 0.852 on taken workspace poses; overhead 0.921; elev 90-140 0.793 (20.5 % of samples over 14 mm) | 0.856; overhead 0.907; elev 90-140 0.806 | `ws_unscored`, `ws_overhead140`, `ws_elev90_140` |
| scored in-band 2-14 | 0.8903 (under the 0.90 target by 0.0097) | 0.8883 | row; `_probe_held.json` |
| fold margin in th (family reading) | min 5.49 deg, 0 < 5, 1 < 5.5 | min 5.02 deg, 0 < 5, 2 < 5.5 | `_probe_*.json` extras, `_msub_rest_bench.json` |
| J1-K-J3 sub-chain with K at rest | m_sub < 5 deg on 85 of 185 rest poses, < 1 on 39, min 0.000 at (-15, 60, 15) | not measured | `_msub_rest_bench.json` |
| springs | one clock spring holds both rolling pairs and K on its law; K is off its rest on 185 of 370 taken poses, up to 51.68 deg | 443 of 868, up to 53.37 deg | verify `_v_*_frozen.json` extra |
| stops | folded J2 stop at smlo 5.0 (the user's floor), but it binds no taken pose (m_plain at rest min 6.075); priced at 5.5 it costs 0.00. Drive range ends by the law at 56.2 deg (K taken to 51.7) | K taken to 53.4 | `_smlo55_bench.json`, `_msub_rest_bench.json` |
| knee window | [26.54, 153.46]; taken 76.87-147.27 (6.2 deg spare) | taken 76.87-151.31 (**2.15 deg spare**) | `_probe_*.json` extras |
| cam transmission | horn pressure angle max 41.5 deg, crank 6.4 deg (gate 45). The roller rolls, so its friction adds about nothing, and it stays under the later 43-deg budget | horn 41.7 deg | row frozen.cam; verify held extra |
| cuff twist / K lag | not measured: there is no CAD, so R17 has never run | | pipeline/full-exo/designs/ |

For the wearer, this is the lead's chain with a rodless strap-level drive. The drive itself is honest:
- It carries 51.7 deg of K with 0.000 mm closure error, and the roller never goes inside the lug.
- It adds no gear, pulley, cable, rod or ball link.
- Its horn pressure angle (41.5 deg) is the highest transmission load in the drive, still inside the 45-deg gate.

Overhead is still the gap:
- Only 8 of the 28 overhead workspace poses are reached, and the fold takes 14 of the 20 that are lost.
- Every overhead pose that is reached has metal under 2 mm from the arm.
- Its deepest contact, 12.57 mm at the shared overhead pose (15, 165, -60), is deeper than every knee-carrying knuckle
  row checked: lead 8.93, slipper-nose 9.01, roller-longdyad 10.55, sidecar-longdyad 4.61. Only the kneeless rows
  press deeper (kneeless-sidecar 17.6 mm, docs/ALIGNMENT.md T5).

## Checks (tools/alignment_audit.py 2026-10-18.1, re-run after the re-wears)

| check | level | reading |
|---|---|---|
| held_out | ok | 22.23 (real envelope) vs 20.08 (+2.15); 22.35 at the claim's own sampling |
| fast_frozen | ok | fast 11.73 -> verified 20.08 (+8.35) |
| near_touch | ok | 1 mm 21.17, 2 mm 46.82, 3 mm 164.78; band read as 3-14 mm 20.42; 26.74 points in the 1-2 mm shell |
| contact_depth | ok | bench 5 poses, 22.09 mm, deepest 12.57; held 10, 59.91 mm, deepest 11.08. The reference (conecut-knee) has no claim-matched depth file. Against sidecar-longdyad the same check reads **watch** (x3.55 bench, +15.86 mm) |
| dominance | **watch** | beats frontload-lobe-stopb by 2.74 plain and loses by 2.74 at 2 mm. The skeptic ruled this a trade-off, not a fake gain (rulings.json) |
| continuity | ok | static 20.08 = connected full 20.08; the knn flood drops 10 forced poses (22.90); bench grid 53.48 |
| fold_margin | **watch** | nothing on the row or the verifier files. This audit measured 5.49 / 5.02 deg, but the tool reads only row and verify files (proposal 4) |
| idle | ok | K 51.68 deg, crank 23.6 deg, knee 70.06 deg |
| sampling | ok | sample-weighted in-band 0.890 vs part-weighted 0.918; L1a has 8 samples |
| density | ok | roller sampled 2.02x the kit's density; at the kit's density 20.15 bench / 22.42 held |
| complexity | ok | 21.75 = row (hand count) |
| reporting | **watch** | the verdict text reads as a self-measured screen; the dashboard's sweep best 11.25 sits 8.83 below the verified number |
| judge_change | ok | no bench, judge or metric file in the 5 commits that touched the row |
| rules | ok | O20, margin >= 5, translations <= 2 |

## Re-wear (the remeasure file predated the row's last commit)

All of these are the model's own `frozen()` and `frozen_held()`, unchanged, with `CB_EXACT=1`.

| wear | plain | 1 mm | 2 mm | in-band14 | reach | file |
|---|---|---|---|---|---|---|
| bench, per-pose dump | **20.08** (recomputed 20.08) | | | 0.8903 | 0.7222 | `_bench_perpose.json` (249 s) |
| bench, wear probe | 20.08 | 21.17 | 46.82 | 0.8903 | 0.7222 | `_probe_bench.json` (174 s) |
| held out, wear probe | **22.35** | 25.41 | 50.38 | 0.8883 | 0.6996 | `_probe_held.json` (515 s) |
| bench, J1-K-J3 sub-chain probe | 20.08 | | | | | `_msub_rest_bench.json` (203 s) |
| bench, stk 6.0 (MR63ZZ knee) | 20.34 (**+0.26**) | 21.43 | 47.03 | 0.8877 | 0.7222 | `_stk6_bench.json` (284 s) |
| bench, smlo 5.5 (stop +0.5 deg) | 20.08 (+0.00) | 21.17 | 46.82 | 0.8903 | 0.7222 | `_smlo55_bench.json` (194 s) |

Readings not taken, and why:
- **Held-out deep remeasure:** started, then stopped to stay inside the time box. Each process had about half a core,
  and a held wear took 8-9 minutes. Its readings are on file from the verifier (`_v_held_frozen.json`: 22.35, 1 mm
  25.41, 2 mm 50.38, min 0.17), and the held probe reproduces them.
- **Held-out per-pose dump:** not run. The held probe's `contact_poses` is the depth source, and it reproduces 22.35.
- **Held out at stk 6.0:** not run (time box). On the siblings it moved +0.06 to +0.30.
- **Bench deep remeasure (2026-10-16, `_bench.json`):** not re-run. The dump and the probe re-wear the same call and
  reproduce it field for field, so that file stays as it was.
- **Which part makes the 12.57 mm overhead press:** not attributed. No tool records per-part contact.

## Findings (all watch; docs/alignment/sidecar-roller-flank-knuckle-3r.findings.json)

1. **T5, depth-blind contact.**
   - *Evidence:*
     - Bench: 5 contacts summing 22.09 mm, deepest 12.57 mm at (15, 165, -60), overhead.
     - Held out: 10 contacts summing 59.91 mm, 8 of them deeper than 3 mm.
     - The same-core rod sidecar (sidecar-longdyad, 18.91) presses 6.23 / 35.66 mm, and sidecar-parallelogram
       1.82 / 18.22 mm.
     - The lead conecut-knee totals about the same (20.24 / 60.97 mm), but its deepest bench press is 8.93 mm at the
       same pose.
   - *Why the exo is not better:* metal 1.26 cm into the arm overhead is a pose the wearer cannot reach without the
     exo blocking or bruising the arm, and the gap counts it the same as a 0.06 mm graze.
   - *Why watch:* depth blindness does not lift this design above any of those rows, because it is behind them on the
     plain gap.
   - *Action:* attribute the press to a part (proposal 5).
2. **G1, metal hugging (report only).**
   - *Evidence:* 26.74 points of the gap live in the 1-2 mm shell. Every taken overhead pose has metal under 2 mm:
     8 of 8 on the bench, and 19 of 19 held out, 7 of them under 1 mm.
   - *Status:* the skeptic refuted it as gamed on 2026-10-16, and the user ruled that near-touch is not a gate.
   - *Why it matters to the wearer:* the overhead poses this design does reach are reached with metal on the skin of
     a real, bulging arm.
3. **M2, a component smaller than the real one.**
   - *Evidence:* the knee stack stk 4.8534 is inherited, against 6.0 for the MR63ZZ pairs the lead's rule requires.
     At 6.0 the bench reads +0.26 (20.34), all of it in-band (the knee 0.935 -> 0.904 in band). The notes still say
     '2 iglidur pins'.
   - *Why not gamed:* no rank flips.
   - *Action:* proposal 2.
4. **G4, a near-singular posture (family-wide, open with the user as B1).**
   - *Evidence:* the fold reading holds (5.49 bench / 5.02 held). But with K at rest, the J1-K-J3 sub-chain is within
     1 deg of its fold on 39 of 185 rest poses, minimum 0.000.
   - *Note:* the held-out minimum of 5.02 deg is 0.02 deg over the rule. The model's truncation enforces the rule, so
     the margin there is exactly the rule.
5. **M5, a spring that may not hold.**
   - *Evidence:* one clock spring force-closes both rolling pairs and holds K on its law over 185 bench and 443
     held-out K-open poses. The 51.5 mm bent arm's deflection is not modelled, and R17 has never run.
6. **M3, a moving running gap (new to this drive).**
   - *Evidence:* the arm's arc rides 0.15 mm over the lug's spherical shell while the two move against each other.
     The verifier accepted this as a running gap. Any deflection or build error over 0.15 mm makes it an uncounted
     sliding pair with friction in the K drive.
   - *Not measured:* measuring it needs a model change. The cost is likely small, because the arm metal sits at a
     median 11.4 mm.
7. **S3, an unsampled body (family-wide).**
   - *Evidence:* the crank's short arm and its lobe follower are not separate sampled metal. The real follower on this
     core (IKO CFS2.5 on a 6.0 mm arm, lobe ring r 10.29-13.43 mm) stands up to 3.4 mm outside the O20 hub.
   - *Not measured.*
8. **G5, complexity hidden by the count.**
   - *Evidence:* with the knee counted as its twin pair measures it, the row reads 24.25, not 21.75. So the design
     with its knee reads 2.5 points simpler than the same mechanism without one.
   - *Why watch:* no decision rides on complexity below score 95.
9. **R1, stale records.**
   - *Evidence:*
     - The verdict text says 'Contender, self-measured ... Needs the adversarial verifier' on a verified row.
     - 'Complexity 45.25' appears in the verdict, the note and the design doc. The complexity is 21.75.
     - The dashboard shows the fast 11.73 and the sweep's 11.25. That 11.25 is P1d, which the designer did not claim:
       it wears to 20.48.
     - The rank text dates from 2026-10-16.
     - The fold margin, depth and knee stack are not on the row.

Checked and not present:

- **T2:** the band read as 3-14 mm moves +0.34 (20.42).
- **T3:** the margin is read in th, 5.49 / 5.02.
- **T4:**
  - smlo sits on the 5.0 floor in 4906 of 8512 sweep configs and in 42 of the top 50. But pricing it at 5.5 costs
    0.00, because no taken pose rests on it.
  - ang_min 26.54 lies inside the sweep's 24.1-33.5, not at a bound.
  - The knee stop has 2.15 deg spare held out.
- **S1 / P1:** held out is +2.27, in line with the family, and it ranks second of the 3-joint held wears.
- **S2:** part-weighted in-band (0.918) is above sample-weighted (0.890). Hub 3 at 0.604 and L2 at 0.74 are sampled at
  80 and 128 points.
- **S5:** connected full = static 20.08. The knn flood's 22.90 is the same size as the family's (sidecar-longdyad
  21.72 vs 18.91).
- **S6:** the roller is sampled 2.02x the kit's density, which is +0.07 at the kit's density.
- **M1:** 0 passive translations; every joint is a catalogue bearing (MR117-2RS O20 hubs, MR63ZZ crank and roller).
- **M4:** the drive moves 51.7 deg.
- **P2:** the search hooks (`bench_eval`, `evaluate` in the sidecar core) never load the held bench. It is loaded only
  in `frozen_held`.
- **P3 / R3:**
  - The claim P1 was set (frozen 20.08, 20:05) before the fast-best P1d existed (20:12).
  - P1d was worn and rejected (20.48).
  - The top-5 spread (0.03) is on the row.
- **P4:** no judge change.
- **R4:** the dashboard v_gap 20.08 matches the verifier (v_contact on the row).

## Proposals (measurement changes for the lead / the user; not inputs to this verdict)

1. **Contact depth on the claim** (T5). Write the claim's per-pose dump next to every verified row, as the lead's
   2026-10-17 rule already asks, and add a claim-matched dump for conecut-knee so the tool's default reference reads.
   - Measured effect if T5 used sidecar-longdyad as the reference: this row goes from ok to watch (x3.55 bench).
   - No score change.
2. **Every pin-knee claim states `stk` and claims at 6.0** (the MR63ZZ rule).
   - Measured effect: this row +0.26 bench (held not run).
   - sidecar-parallelogram +0.00 / +0.06; sidecar-longdyad +0.30 / +0.30; roller-longdyad +0.26 / +0.27.
3. **Price the cam pair's running gap.** Rerun the frozen claim with the arm's arc lifted to a 1 mm clearance over the
   lug, which needs a model parameter for RUNG over the shell. Until then, state the 0.15 mm gap and the unmodelled arm
   deflection beside the number.
   - Not measured.
4. **Instrument (no score change):** let `c_fold_margin` in tools/alignment_audit.py also read the auditor's own
   `remeasure/<id>_msub_rest_*.json` `family_reading` and `_probe_*.json` `extras.th_margin_own_state`.
   - This row's watch would then read ok at 5.02.
   - It is a tool change, so it needs a VERSION bump and a selftest run. It was not made here.
5. **Per-part contact attribution** (new instrument). Extend the per-pose dump to record which metal group sets the
   floor of each contact and near-touch pose.
   - The 12.57 mm press at (15, 165, -60) is the deepest of the knee-carrying knuckle rows checked at a pose the whole
     family presses (lead 8.93, roller-longdyad 10.55, slipper-nose 9.01).
   - Knowing the part decides whether it is a drive problem or a chain problem.

## What happens next

- The lead or the verifier writes the fold margin (5.49 / 5.02), the knee stack and the per-pose dumps onto the row or
  into a verify file, so that `fold_margin` and `contact_depth` read them without the auditor.
- The row's stale text needs fixing: the verdict, the 45.25 complexity in three places and the dashboard's fast fields.
- Before any L1 CAD of this design:
  - run the held-out stk 6.0 wear;
  - run the part attribution of the overhead contact;
  - run a 2 mm near-touch search (26.7 points sit in the 1-2 mm shell, overhead most of all);
  - run R17 for the clock-spring hold and the 0.15 mm arm-over-lug gap.
- The hourly audit loop re-audits this row when its row or verifier files change.

## Skeptic (2026-10-19, 02:07-02:30 UTC)

Ledger entry 2026-10-19T02:18:22Z (`by skeptic`, run `skeptic:sidecar-roller-flank-knuckle-3r`). Rulings:
`docs/alignment/sidecar-roller-flank-knuckle-3r.rulings.json`. This replaces the 2026-10-16 file, which is still in
git history.

How I checked:
- I re-derived every number from the raw files: the per-pose dumps, the probes, the verify JSON, and tools/simplicity.py
  score().
- I re-ran no wear. The box was at load 18 on 4 cores, and every reading I needed is on file in a file that reproduces
  the claim.
- I edited no bench, judge, kit, model, row or dashboard, and changed no score. Cost: $0.

**Final verdict (ledger): WATCH.** 3 reasons are refuted and 9 are upheld, all of them watch.

### Refuted (with evidence)

**dominance.** The numbers reproduce, but the stated cause does not.
- Frontload (`verify/frontload-lobe-stopb-knuckle-3r_corr_bench_frozen.json`) reads 22.82 plain and 44.08 at 2 mm
  (34 poses). This design reads 20.08 and 46.82 (45 poses).
- Decomposed with `gap_of`, the 2.74 gain is all in-band: +3.57 (inband14 0.8546 -> 0.8903). Reach costs -0.56 (0.7278
  -> 0.7222) and contact -0.27.
- In-band counts only metal at 2-14 mm (concept_bench.py line 191), and this design reaches fewer poses than frontload.
  So no part of the gain is metal moved into the 1-2 mm shell. The gain is a real lower profile.
- What is left, 11 more taken poses under 2 mm, is G1's cost, and G1 stands.

**fold_margin.** The margin is on file, and it passes.
- `_probe_bench.json` `extras.th_margin_own_state` reads min 5.49 (0 < 5). `_probe_held.json` reads min 5.02 (0 < 5).
  `_msub_rest_bench.json` `family_reading` reads min 5.49. All three reproduce the claim.
- Recomputed from the 370 per-pose rows: rest m_plain min 6.075, moved min(m_sub, m_eff) min 5.49.
- By c_fold_margin's own rule, that reads ok. The missing entry on the row stays under R1.

**judgement:T5.** The documented rule (>= 2x the reference's summed depth AND >= 5 mm more) is not met against the
documented reference, the current lead conecut-knee. I compared on the same 470 pose indices.

| wear | this design | lead conecut-knee | ratio | excess |
|---|---|---|---|---|
| bench | 22.09 mm (5 contacts) | 20.24 mm (4 contacts) | x1.09 | +1.85 mm |
| held out | 59.91 mm (10 contacts) | 60.97 mm (14 contacts) | x0.98 | -1.06 mm |

- Both designs lose the 3 shared overhead contact poses.
- This design presses deeper at (15,165,-60), +3.64 mm (12.57 vs 8.93). That is under the 5 mm floor.
- It presses shallower at (30,165,-60) and (60,150,-105).
- The only reference that meets the rule is sidecar-longdyad, which the tool comment marks stale since 2026-10-17 05:00.

### Upheld

- **reporting.** The verdict opens 'Contender, self-measured'. The dashboard's sweep_gap is 11.25 (score 95.91,
  above the 95 line) against the verified 20.08, a difference of 8.83 (the trigger is > 5).
- **judgement:G1.** Re-derived: 45 of 370 taken poses are under 2 mm, and all 8 taken overhead poses are under 2 mm
  (0.65-1.98). The shell holds 26.74 points (TH watch 15). Two corrections:
  - On the walls basis, 2 poses are under 1 mm (0.32 and 0.65), not 1.
  - 183 poses are under 3 mm on the walls basis. The 171 is the sampled basis.
- **judgement:M2.** The model inherits stk 4.8534, which is under even the iglidur figure of 5.0. At the MR63ZZ 6.0,
  the bench reads 20.34 (+0.26). The held-out stk 6.0 wear is still not on file.
- **judgement:G4.** Recounted: rest m_sub is under 5 on 85 of 185 poses, under 1 on 39, min 0.000. The stiffness of K's
  rest stop is unmeasured, and B1 is open with the user. Correction: 33 of the 85 are at elev >= 90, so the near-fold is
  not only in the low arm.
- **judgement:M5.** The clock spring holds K off its rest on 185 / 443 poses, up to 51.68 / 53.37 deg. There is no CAD,
  so R17 has never run.
- **judgement:M3.** The 0.15 mm gap is confirmed (model line 142, RUNG 0.15).
  - It meets the kit's written clearance for adjacent parts (>= 0.15 mm, skin-normal-3r-pin-knee.py docstring), since
    arm and lug are a cam pair.
  - The open question is whether a 51.5 mm bent cantilever under ~2.5 N holds 0.15 mm. No number is on file.
- **judgement:S3.** The crank's short arm and its follower are not separate sampled metal. No model is on file.
- **judgement:G5.** Reproduced: 21.75 on the row, 24.25 with the twin delta. cuff_knee over-subtracts bodies 1, made 2
  and bought 2.
- **judgement:R1.** Confirmed. The row also still compares against 'the verified lead 22.82' (frontload). Its mechanism
  notes say the knee is 'sensed as the lead', while `cuff_knee.sensed` is false.

### Missed by the auditor (for the next audit; not in this verdict)

1. **The T5 tool check has been silently off against the lead for every design since 46af77e (2026-10-18 11:37).**
   - *Cause:* `docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` has
     `"held": "missing dump"`, a string. `_depth_sources` (tools/alignment_audit.py line 351) calls `.get` on it and
     raises AttributeError. `ref_depths()` in `c_contact_depth` swallows the exception and returns {}.
   - *Effect:* every contact_depth check reads "no bench depth of conecut-knee-knuckle-3r on file" and ok. The lead's
     dumps are claim-matched (bench frozen 18.28 / recomputed 18.29, held 22.38 / 22.38). So this audit's text "ok only
     because the lead has no claim-matched depth file" is wrong.
   - *Scale:* 16 audit JSONs carry the false ok. 5 of them meet the documented rule against the lead and should have
     read watch from the tool:

     | design | bench sum | ratio to lead | excess |
     |---|---|---|---|
     | freek-oracle-route-knuckle-4r | 78.55 mm | x3.88 | +58.31 mm |
     | phi40-thinstack-relay-4r | 74.92 mm | x3.70 | +54.68 mm |
     | proxtrack-relay-knuckle-4r | 50.36 mm | x2.49 | +30.12 mm |
     | offset-shortcar-relay-4r | 46.18 mm | x2.28 | +25.94 mm |
     | underpass-bridge-relay-4r | 43.23 mm | x2.14 | +22.99 mm |

   - *Status:* their judgement passes caught it by hand. The tool did not.
   - *Fix:* a tool change (guard the paired loop, bump VERSION, run the selftest), for the auditor. It was not made here.
2. **G1 mixes count bases.** "45 < 2 mm" is counted with the walls. "1 < 1 mm" and "171 < 3 mm" are counted on sampled
   metal. On one basis (walls) the counts are 45 / 2 / 183.
3. **G4's "low-arm workspace" understates where the sub-chain folds.** 33 of the 85 rest poses with m_sub under 5 are
   raised-arm (elev >= 90): ws 20 at 90-140 and 3 at >= 140, clip 4 and 6.
4. **The row's verdict names a stale lead and the notes a sensed knee.** The verdict compares against 'the verified lead
   22.82' (frontload, displaced 2026-10-17). The mechanism notes say the knee is 'sensed as the lead' while `cuff_knee`
   says `sensed: false`. Both belong in the R1 clean-up.

What happens next:
- The auditor fixes the paired-file crash in `_depth_sources`, then re-runs contact_depth on the 16 affected audits.
- The lead writes the fold margin (5.49 / 5.02) and the knee stack onto this row.
- The held-out stk 6.0 wear runs when the box has CPU to spare.
