# Alignment audit: conecut-h2facet-knuckle-3r

Auditor run 2026-10-18 ~22:04-22:20 UTC (hourly; ledger entry 2026-10-18T22:14:00Z). It was due because the row changed at 21:00:39Z (d889d5a, dashboard
v147: a `leader_ruling` 'tie' with conecut-knee was added), after the last audit (skeptic, 17:06:25Z, WATCH). The task
of this run was a check of how the leader is reported and presented. Reference: the lead conecut-knee-knuckle-3r.
Tool: tools/alignment_audit.py 2026-10-18.1 (`--ref conecut-knee-knuckle-3r`). Checks:
docs/alignment/conecut-h2facet-knuckle-3r.json. Findings: docs/alignment/conecut-h2facet-knuckle-3r.findings.json.
Ledger: `python3 tools/alignment_ledger.py get conecut-h2facet-knuckle-3r`.

## Verdict and claim

**Ledger verdict: WATCH.** No check and no finding is 'gamed'.

The claim is unchanged: v_gap **18.28** (score 93.35) on exact Bench(110,360), frozen shape; held out 22.16.

- **What changed since the last audit:** one string. `git diff 616e0c7..HEAD` on the row shows only the new
  `leader_ruling`. The model, the verifier files, tools/concept_kit.py, the audit tool and the probe adapters have
  not changed since the re-wears on file (f493a7f 16:00 bench, 0781b77 16:12 held).
- **Why I did not re-wear the claim:** the claim did not move and neither did any input to it. The bench and held
  re-wears on file (f493a7f / 0781b77) reproduce 18.28 / 22.16 bit for bit. The only new wear is the held workspace
  probe, which had never been run for this row.
- **The ruling:** it is valid. It cites the skeptic entry 2026-10-18T17:06:25Z, whose verdict is watch, and
  tools/dash_build.py checks that. It moves no number and only demotes this row. I replicated the page's board and
  leader calcs on morphs.json:
  - with the ruling, the headline is 'Re-centred cuff knee (tied with Re-centred knee, chamfered hub)', 18.28, complexity 18.5;
  - without it, the headline would be this row at complexity 0.
- **Is the exo better than the lead?** A little, and never worse. The chamfer only removes metal.
- **Is the number or its presentation selling it wrongly?** Not upward. Two things are off:
  - The tie is resolved by hand because the board's tie order is the id's alphabetical order (NEW-tie-order).
  - Every display of the row still has complexity 0 except the headline (G5).
  - The ruling's own text undersells the row: 'buys no take' is true on the bench only (R1).

## What the wearer gets (measured)

- **Overhead reach (elev >= 140):** 8 of 28 bench poses taken, the same as the lead. The 20 lost: fold 14, contact 3,
  J3 stop 3 (bench probe). Held: see the table below.
- **Raised-arm reach (elev >= 90):** 47 of 113 bench poses (0.416), equal to the lead. Held: 124 of 300 (lead 123;
  this audit's held probe: 106 + 18). The extra one is pose 447 (0/90/30), taken with metal at 0.697 mm. Its in-band
  metal pulls the held 90-140 band down slightly, 0.8478 -> 0.8469.
- **Taken poses with metal under 2 mm:** 33 bench and 71 held, both equal to the lead. Under 3 mm: 99 vs 105 bench and
  206 vs 217 held (the chamfer's real gain). Under 1 mm: 2 vs 3 bench and 14 vs 13 held (held 447 joins at 0.697 mm).
- **Lowest metal on a taken pose:** 0.072 mm at bench 139 (ws -60/60/105), on link 2, which the chamfer cannot reach.
- **Deepest contact:**
  - bench: 8.93 mm at ws 15/165/-60 (crank / horn); 4 contact poses, 19.86 mm in total (lead 20.24);
  - held: 9.86 mm at ws 45/165/-30; 13 contact poses, 60.5 mm in total (lead 14, 60.97).
- **Workspace in-band (unscored), bench:** 0.868 over all taken workspace poses, 0.832 at elevation 90-140, and 0.936
  overhead on 8 poses. Only the scored clip frames read 0.901.
- **Held workspace probe (new in this audit, 316.5 s, the model unchanged):** it reproduces held gap 22.16 (reach 0.6933, in-band 0.9).

  | held, taken workspace poses | h2facet | lead |
  |---|---|---|
  | all: taken of total | 660 of 952 | 659 of 952 |
  | all: in-band 2-14 mm | 0.871 | 0.8712 |
  | all: metal above 14 mm | 12.7 % (max 31.46 mm) | 12.6 % (max 31.46 mm) |
  | elevation 90-140: taken | 106 of 229 | 105 of 229 |
  | elevation 90-140: in-band | 0.8469 | 0.8478 |
  | overhead (elev >= 140): taken | 18 of 71 | 18 of 71 |
  | overhead: in-band | 0.932 | 0.932 |
  | overhead: why not taken | fold 36, J3 stop 10, contact 7 | fold 36, J3 stop 10, contact 7 |
  | taken poses with a floor under 1 / 2 / 3 mm | 14 / 63 / 164 | 13 / 63 / 172 |

  The clip frames, which are what the score reads, are at in-band 0.900 on 202 of 202. File:
  docs/alignment/remeasure/conecut-h2facet-knuckle-3r_probe_held.json.
- **Springs, stops, cuff twist, singular postures:** all the lead's; the chamfer adds no joint, stop or load path.
  - The lead's built CAD dynamics give 3.99 deg nominal cuff twist and 4.77 deg at the M5 forward bound, 0.23 deg under
    the 5 deg gate; with plain friction it is 11.73 deg and 5.24 N (pipeline/full-exo/designs/user_conecut_knee/judge/dynamics.json).
  - The th fold margin is 5.181 deg on the bench and 5.006 held. The J3 dowel's held number holds inside a 1.33 deg window.
  - m_sub with the knee at rest is under 1 deg on 50 of 205 poses (G4).
- **What the built exo gets today:** the lead's CAD (user_conecut_knee, 4ad3a2a) has no chamfer yet, so the wearer of
  the built design does not get this row's +0.6 mm on 45 held poses.

## Checks (tools/alignment_audit.py)

| check | level | reading |
|---|---|---|
| held_out | ok | 22.16 vs 18.28 (+3.88) |
| fast_frozen | ok | 12.5 -> 18.28 (+5.78) |
| near_touch | ok | 18.28 / 19.38 / 34.84; 16.56 points in the 1-2 mm shell (the lead's) |
| contact_depth | ok | bench 4 poses, 19.86 mm; held 13 poses, 60.5 mm |
| dominance | ok | vs the lead: +0.00 plain, +0.00 at 2 mm (needs `--ref`; without it the check reads 'no reference') |
| continuity | watch | the text says 'no flood on file', but the check cannot see the floods that are on file. On those floods: bench full 18.28 = static; held full 22.16 = static, knn 30.39 |
| fold_margin | ok | 5.006 deg |
| idle | ok | the knee moves |
| sampling | ok | sample-weighted 0.901 vs part-weighted 0.925; L1a has 8 samples (the lead's) |
| density | ok | roller 4.55x (the lead's) |
| complexity | watch | recomputed 0.0 vs the row's 18.5: the mechanism record is a delta (G5) |
| reporting | watch | the verdict reads as a screen; the sweep best 12.5 sits 5.78 below the verified number (R1) |
| judge_change | ok | no bench / judge / metric file changed in the 4 commits that touched the row |
| rules | ok | O20, margin >= 5, 0 passive translations, 3 active DOF |

## Findings

Every finding below is watch. The full numbers and file paths are in the findings JSON.

1. **NEW-tie-order (new; the reason this audit was due).**
   - **Evidence:** tools/dash_build.py line 551 sorts the rows by id. The page's board sort by gap is stable, and the
     leader calc takes the first verified <=3-joint row without a ruling. The only exact tie among verified rows is
     at 18.28: this row, the lead and the gamed conecut-l2jog. 'conecut-h2facet' sorts before 'conecut-knee'.
   - **Why the exo is not better:** without the hand-written ruling, a row whose verified gain is zero would head the
     board, at the shown complexity 0.
   - **Action:** an explicit tie-break in the builder (proposal 1).
2. **R1 (extended to the ruling text).**
   - **Evidence:** the verdict still opens 'SCREENED'. gap / sweep_gap 12.5 (score 95.45) sit beside v_gap 18.28.
     The ruling says 'buys no take', which is true on the bench; held out it buys pose 447, and 45 poses gain +0.60 mm
     with none worse.
   - **Why it matters:** nothing is inflated. The headline names the tie partner that is slightly worse at the skin,
     and the built CAD lacks the chamfer.
   - **Action:** put the verified result first in the verdict; say 'bench tie, held +1 take at 0.70 mm' in the ruling;
     add the chamfer to user_conecut_knee.
3. **G5.**
   - **Evidence:** the board shows complexity 0 for a real 18.5. On 38 verified rows it dominates 33 of 37 at 0 and 12
     at 18.5. The headline is fixed by the ruling; the simple board's chart (labelled, at (93.35, 0)) and the
     Simplicity column are not.
   - **Action:** expand the delta mechanism record.
4. **T1.** Every scored gain lands just past a cutoff: 203 at 1.122 mm and 447 at 0.697 mm. The wearer is at least as
   well off at every pose; the size of the gain is oversold.
5. **P1.** The cut was sized on claim-bench guard poses; 122 flat configs.
6. **NEW-wrong-body-frame.**
   - The flat is modelled on link 1b but cuts link 2's boss and cap.
   - It also cuts the cap skirt over the O18 spigot, leaving at most 0.4 mm.
   - It is worth 0, yet still sits in best_params and in the name.
7. **T3.** The fold margin is 5.006 held, and the J3 window is 1.33 deg (carried).
8. **M5.** The text is corrected: twist was measured, 0.23 deg under the gate at the forward bound, and 11.73 deg with
   plain friction. J3 raceway s0 0.3-0.40 (carried).
9. **G4.** m_sub at rest is under 1 deg on 50 of 205 poses (measured by the skeptic on this row).
10. **NEW-strap-dilution.** 18.67 / 22.68 at an equal strap count; held in-band 0.8999 (carried).
11. **NEW-ws-inband.** The raised arm is the worst band and is unscored; the held probe was added in this audit.
12. **P2.** Held drift-cloud use in the lead's knee, with zero effect (carried).

S5 is no longer a finding: the skeptic refuted it with the held flood (full 22.16 = static, 0 of 332 forced poses dropped).

**Walked and not present:**
- **T2:** the band read at 3-14 mm is 18.33 vs plain 18.28.
- **T4:** no joint bound changed.
- **T5:** this row's contacts are not deeper than the lead's.
- **S1 / S2 / S3 / S4:** sampling checks ok. The chamfer region is solid-sampled, and the one drop (234, -0.05 mm)
  comes from the denser sampling.
- **M1:** this is the flat, under NEW-wrong-body-frame.
- **M2 / M3:** the chamfer wall is 3.1 mm to the bore, and the cut adds no clash.
- **M4:** the knee moves.
- **P3:** held was worn once per config, and this audit did not re-wear the claim.
- **P4:** no judge change.
- **R2:** the refuted flat is under NEW-wrong-body-frame.
- **R3:** see P1.
- **R4:** the board's v_gap equals the verifier's.
- **G1:** see T1.
- **G2 / G3:** see M5.
- **G6:** 3 active DOF.

## Proposals (proposals only; none feeds this verdict)

1. **An explicit tie-break for the headline (an instrument change; no score moves).** On an exact v_gap tie among
   verified rows, the builder orders by:
   1. fewer passive translations (CLAUDE.md's winner rule);
   2. then the incumbent first (the earliest verification event), because a design replaces the lead only on a lower gap;
   3. then id.
   The headline names the tie. Measured on today's board: the only exact tie is 18.28, and the headline is unchanged
   (conecut-knee). This row's ruling then becomes unnecessary.
   - **Alternative, the user's call:** break ties on the held gap instead. That would put this row in the headline
     (22.16 vs 22.38), which is the right answer for the wearer, but only once G5 is fixed so that the headline does
     not read complexity 0.
   - Proposed catalogue entry **R5, "Headline by name order on an exact tie"**:
     - looks like: a derivative row with zero gain and an id that sorts earlier takes the headline;
     - detect: count the verified <=3-joint unflagged rows within 0.005 of the headline gap that have no ruling, and
       watch when there are two or more;
     - here: 2 rows.
2. **A record rule for delta rows** (carried from 16:31). Expand `{source, record_delta}` to the source's full record
   before tools/simplicity.py scores it. Measured effect: 3 verified rows change their shown complexity (h2facet and
   l2jog 0 -> 18.5; kphase-notch 0 -> its source's). No gap changes.
3. **A vacuous-search flag for the convergence gate** (carried). Flag a search when every config reads the same number.
   Effect: this row's 122 configs.
4. **Catalogue entry M6, "a feature modelled on a body it does not ride on"** (carried). Here it is extended with the
   wall check: report a cut's wall to every part it cuts (bore, cap skirt, thread), not just to the bore.
5. **The continuity check should read the flood files on record** (from the skeptic's Missed 3). It should also read
   `remeasure/<id>+*_flood_{bench,held}.json` `connected` blocks. Effect: this row's level stays watch (held knn), and
   only the text changes.

---
*Skeptic section below kept from 2026-10-18 17:08 UTC (dated rule).*

## Skeptic (2026-10-18, 16:50-17:08 UTC)

Ledger entry 2026-10-18T17:06:25Z, by skeptic, run `skeptic:conecut-h2facet-knuckle-3r`.

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence. I upheld 14
of the 15 reasons and refuted 1 (S5) with a new measurement. Rulings: `docs/alignment/conecut-h2facet-knuckle-3r.rulings.json`.

**How I checked.**
- I re-derived every number from the raw files with my own short scripts:
  - the per-pose dumps (chamfer-only, fd 0.6 and the lead's, bench and held);
  - the verifier JSONs;
  - the sweep files;
  - morphs.json / sweeps.json;
  - `tools/simplicity.py --json`;
  - the lead's user-standard CAD judge files.
- I made three new measurements. All ran locally with CB_EXACT=1, nice 10, OMP_NUM_THREADS=1 and at most 2 processes.
  The models were unchanged and the farm was not used.
  - `remeasure/conecut-h2facet-knuckle-3r+chamferonly_flood_held.json`: the held continuity flood, which the audit did
    not obtain. It uses the lead verifier harness with `--flood --set fd=0` and took 381.7 s.
  - `remeasure/conecut-h2facet-knuckle-3r+rowconfig_flood_bench.json`: the bench flood at the row's own best_params
    (fd 0.6). It took 167.7 s.
  - `remeasure/conecut-h2facet-knuckle-3r_msub_rest_bench.json`: m_sub with K at rest, from
    `tools/alignment_msub_rest_probe_model.py`. It took 151.7 s.

### Rulings

1. **continuity: upheld, now measured on held.**
   - Bench: both floods read static 18.28, full 18.28 (0 dropped), knn 19.97 (6 dropped) and bench-graph 50.13. That is
     ok by the coded rule.
   - Held: static 22.16, full 22.16 (0 of 332 dropped), knn **30.39 (77 dropped)**, bench-graph 23.33 (11 dropped).
     The knn loss is 8.23, above TH conn_gamed 3, so c_continuity line 505 reads watch. The desmo-conecut and
     lowarm-halfring held files read the same way, and so does the sibling l2jog's held flood (knn 30.69).
   - The check's text "no flood on file" is out of date; the watch level is not.
2. **complexity: upheld.** simplicity.py scores this row 0 (items []) and the lead 18.5. The row field says 18.5.
3. **reporting: upheld.** morphs.json shows gap / sweep_gap 12.5 beside v_gap 18.28, and the verdict starts
   "SCREENED". The lead's own morphs row has the same 12.5 / 18.28 pair.
4. **G5: upheld, recounted.** 37 verified rows. With the shown 0 this row dominates 33 of the other 36; with 18.5 it
   dominates 12. conecut-l2jog and lowarm-kphase-notch also show 0.
5. **T1: upheld, re-derived from the dumps.**
   - Bench: near1 19.37 vs 19.92, from pose 203 alone (0.263 -> 1.122 mm).
   - Held: the plain 22.16 vs 22.38 comes from one flip, pose 447 (-0.207 mm -> taken at 0.697 mm). Held near1 is
     25.23 for both.
   - Changed poses: 21 on the bench (20 up, mean +0.603 mm; pose 234 -0.050 mm) and 45 held (all up, mean +0.601 mm).
   - The fd 0.6 and chamfer-only dumps are identical on 470/470 bench and 1154/1154 held poses.
   - The held edge is metal at 0.70 mm on a taken pose.
6. **P1: upheld.** 122 configurations, all reading 12.5 / 13.66. One correction: the envh read (17.57 / 22.24)
   exists only on the 47 coarse entries; the 75 CMA entries have none. GUARD and AZ203 are exact claim-bench poses.
7. **NEW-wrong-body-frame: upheld.**
   - In docs/HARDWARE.md the boss starts at U0 3.15 and belongs to the upper member. The flat (z 3.9-12.25) is
     edited on member 7 (link 1b), and J2 turns -14.2..90.9 deg.
   - The flat is worth 0: the per-pose dumps show 0 changed poses, and my two bench floods are equal.
   - A second defect is under Missed (1).
8. **R1: upheld.** The verdict string opens "SCREENED"; the alignment field is empty; sweeps.json has 122 entries at
   12.5.
9. **S5: REFUTED by measurement.**
   - The held flood now exists: full 22.16 = static, 0 of 332 forced dropped.
   - From the dumps, the held ws taken set is the lead's 659 plus pose 447. l2jog's held set equals the lead's.
   - forced_taken is 332 both here and in l2jog's held flood. So 447 is not a forced pose, and no flood can drop it.
   - knn and bench-graph each keep exactly one more pose than the sibling, with the same drop counts (77 and 11).
   - The lead's own held flood is still not on file. That item belongs to the lead's row.
10. **T3: upheld.** The th margin is 5.006 held and 5.181 bench, and J3MIN is the lead's -111.9036. So the 1.33 deg
    held window carries over.
11. **M5: upheld on the raceway; the carried text needs a correction.**
    - R17 and cuff twist HAVE been measured on this chain: user_conecut_knee judge/dynamics.json.
      - Nominal case: 0.126 N.m, 0.57 N, twist 3.99 deg, R17 PASS.
      - krate0.01 case: twist 3.89 deg.
      - M5 forward bound: twist 4.54 / 4.67 / 4.77 deg, 0.23 deg under the 5 deg gate.
      - Plain-friction case f0.05: twist 11.73 deg and 5.24 N, both over the 5 deg / 5 N rule.
    - What stands: J3 bearing s0 0.3 at 6 N.m (build.json j3_stop dowel_calc), and s0 0.40 under a silicone liner.
12. **G4: upheld, now measured on this row.** m_sub at rest: n 205, min 0.0, lt1 50, lt5 107. Identical to the lead
    on 372/372 rows.
13. **NEW-strap-dilution: upheld.** The equal-strap gap is 18.67 on the bench and 22.68 held. Held in-band is 0.8999.
14. **NEW-ws-inband: upheld.** Workspace in-band is 0.8676 over all taken poses, 0.8315 at elevation 90-140 and 0.9359
    overhead. All equal the lead's.
15. **P2: upheld (carried).** This design's own parameters came from bench guard poses only. It inherits the lead's
    J3MIN, whose L1 build window is bounded by held-out q3'. Measured effect: zero.

### Missed (for the next audit; not counted in this verdict)

1. **The flat's wall figure is not the flat's.**
   - The model's `wall_min_mm` (line 163) is min(10 - c, 10 - fd) - 5.5, i.e. measured to the MR117 bore. The row and
     verdict cite it as 3.1 mm.
   - But the flat runs z 3.9-12.25 and, from H1 8.75 up, cuts the cap skirt over the O18 M18x0.5 spigot (HARDWARE.md:
     spigot r <= 9, skirt to r 10, about 1 mm).
   - fd 0.6 leaves at most 0.4 mm of skirt there, before thread depth. So the flat cannot be built for a second
     reason, independent of the frame error.
   - Anything that imports the flat (lowarm-kphase-notch cites its 264 table) needs both fixes.
2. **The carried M5 text was stale.**
   - The audit copied "R17 and cuff twist never measured" from the lead's 2026-10-17 ledger. The lead chain's
     user-standard CAD has measured both since then (ruling 11).
   - The real live risks are the thin 0.23 deg twist margin at the forward bound, and the 11.7 deg twist if a plain
     pin or bushing is used.
   - Carried reasons should be re-read against the files before they are copied.
3. **The continuity check cannot see the flood files on record.**
   - c_continuity reads only the row, the verifier files, and `remeasure/<id>_*bench*.json` files that hold
     contact_aware_verifier / final_verifier keys.
   - So the audit's `+chamferonly_flood_bench.json` and my held flood are both invisible to it. It will keep printing
     "no flood on file", whatever the floods read.
   - On the held flood now on file it would read watch (knn -8.23).
   - Proposal, an instrument change and not an input to this verdict: also read `<id>+*_flood_{bench,held}.json`
     `connected` blocks. Measured effect: this row's continuity level is unchanged (watch, from held knn), and only the
     check's text changes.
