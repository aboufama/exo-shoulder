# Alignment audit: conecut-l2jog-knuckle-3r

Auditor run 2026-10-18 ~16:25-16:45 UTC. Discovery round 15, slice r15-B. Reference: the lead conecut-knee-knuckle-3r.
Tool: tools/alignment_audit.py 2026-10-18.1. Checks: docs/alignment/conecut-l2jog-knuckle-3r.json. Findings:
docs/alignment/conecut-l2jog-knuckle-3r.findings.json. Ledger: `python3 tools/alignment_ledger.py get conecut-l2jog-knuckle-3r`.

## Verdict and claim

**Ledger verdict: GAMED.** The tool alone gives watch. The 'gamed' comes from one judgement finding, NEW-hidden-lift. The
other 13 findings are watch.

The claim is v_gap **18.28** (score 93.35) on exact Bench(110,360), frozen shape. Held out it reads 22.45.

- **What the design is:** the lead's chain, unchanged, plus a planform "waist" on link 2. The row says link 2's edge moves
  1.6 mm in the bar plane over 20 mm at pose 139's binder, as a profile cut before bending (cx +0).
- **Against the lead, plain gap:** an exact tie on the bench (the same 262 takes and the same 4 contacts). Held out it is
  0.07 worse (22.45 vs 22.38), all of it in-band.
- **What the row claims beyond the tie:** it hardens the lead's only +0.1 / +0.2 mm probe flip (pose 139 0.072 -> 0.602 mm,
  +0.2 mm probe 18.83 -> 18.28).
- **Is the exo better?** No. Built the way the row says (a cut), it is the lead pose for pose, with a 27 % weaker link 2 at
  the waist.
- **What is gamed:** the probe number. Round 15 ranks claims at the +0.2 mm probe (docs/concepts/ROUNDS.md line 4604).
  - At that metric the row's recorded 18.28 puts the design 0.54 ahead of the lead (18.83).
  - Held out, under the same harness, it is 0.06 behind at every probe level.
  - As the stated cut, it reads exactly the lead's numbers.
- **What is not gamed:** the plain v_gap 18.28. It is right, and it stands either way.

Until the probe numbers are corrected, the ledger blocks calling this design a winner or a leader at the probe.

**Re-measured in this audit (the models unchanged; every number reproduces the claim):**

| wear | gap | reach | in-band14 | contacts | near1 | near2 | near3 | band 3-14 | file |
|---|---|---|---|---|---|---|---|---|---|
| bench re-wear (model's own frozen()) | 18.28 | 0.7278 | 0.9005 | 4 | 19.92 | 34.84 | 86.16 | 18.41 (lead 18.34) | remeasure/conecut-l2jog-knuckle-3r_bench.json |
| held re-wear | 22.45 | 0.6922 | 0.8993 | 14 | 25.30 (lead 25.23) | 37.10 | 83.12 | 22.62 (lead 22.55) | remeasure/conecut-l2jog-knuckle-3r_held.json |
| bench, lead verifier harness + flood | 18.28; static 18.28, full 18.28, knn 19.97, bench-graph 50.13 (= the lead) | | | | | | | | remeasure/conecut-l2jog-knuckle-3r_flood_bench.json |
| held, lead verifier harness + flood (first held flood on this chain) | 22.45; static 22.45, full 22.45, knn 30.69, bench-graph 23.62 | | | | | | | | remeasure/conecut-l2jog-knuckle-3r_flood_held.json |
| bench wear probe | 18.28 | | | | | | | | remeasure/conecut-l2jog-knuckle-3r_probe_bench.json |

I recomputed the probes myself from the per-pose dumps, using tools/alignment_paired.py gap_parts. "Lowest metal" counts
the contact-only walls.

| per-pose dump | plain | +0.1 | +0.2 | +0.35 | near1 | near2 |
|---|---|---|---|---|---|---|
| bench, lead | 18.29 | 18.83 | 18.83 | 19.37 | 19.92 | 34.84 |
| bench, waist as modelled | 18.29 | **18.29** | **18.29** | 18.83 | 19.92 | 34.84 |
| bench, waist as a true cut (verifier) | 18.29 | 18.83 | 18.83 | 19.37 | 19.92 | 34.84 |
| held, lead | 22.38 | 22.38 | 22.38 | 22.60 | 25.23 | 37.11 |
| held, waist as modelled | 22.44 | 22.44 | 22.44 | 22.66 | 25.29 | 37.18 |
| held, waist as a true cut | 22.38 | 22.38 | 22.38 | 22.60 | 25.23 | 37.11 |

The chain's coordinate spans in the bench re-wear are bit-identical to the lead's:
- dK -0.796..0 rad;
- K.ang 59.27..105.94 deg;
- q3' -109.20..116.10 deg;
- msub 10.81..99.0 deg;
- a1e 37.55..54.26 deg.

## What the wearer gets (measured)

Every number below equals the lead's unless stated.

- **Overhead reach (elevation >= 140):**
  - Bench: 8 of 28 poses taken. The 20 lost: fold 14, contact 3, J3 stop 3.
  - Held: 18 of 71 taken.
- **Raised-arm reach (elevation 90-140):** 39 of 85 bench poses taken (0.46).
  - By band: 90-120 27/51, 120-140 12/34, 140-160 5/13, 160-200 3/15.
- **Taken poses with metal < 2 mm:**
  - Bench: 33 of 372 (3 under 1 mm, 105 under 3 mm).
  - Held: 71 of 861 (13 under 1 mm, 218 under 3 mm).
  - The lowest metal over the bench takes is 0.263 mm, pose 203 (hub 2's skin-side ring; lead 0.072 at 139). Held: 0.325 mm.
  - As the stated cut, the bench lowest is 0.073 mm at 139, the lead's.
- **Deepest contact:**
  - Bench: 4 contact poses, summed depth 20.24 mm. The deepest is 8.93 mm at ws plane 15 / elevation 165 / axial -60
    (overhead). 3 are deeper than 3 mm. All equal the lead's.
  - Held: 14 contact poses, deepest 9.86 mm at ws 45 / 165 / -30. Summed depth: 58.09 mm modelled, 60.09 mm true cut,
    60.97 mm lead. Most of the modelled 2.9 mm is the hidden lift.
- **Workspace in-band (unscored, bench):** slightly worse than the lead on every slice.

  | slice | in-band | lead |
  |---|---|---|
  | all taken workspace poses (262) | 0.8665 | 0.8676 |
  | elevation 90-140 | 0.8309 | 0.8315 |
  | overhead (8 taken) | 0.9341 | 0.9359 |
  | scored clip frames | 0.9005 | 0.9012 |

  Link 2, the edited part, is the worst-banded body: 0.726 bench and 0.723 held (lead 0.731 / 0.728).
- **Fold margin (th, own state):**
  - Bench: 5.181 deg, 372 taken, 0 under 5.
  - Held: 5.006 deg, 861 taken, 0 under 5.
  - J3 dowel held margin: 0.74 deg low, 3.3 deg high; 19 held poses are stopped.
- **Springs, stops, cuff twist:** the lead's K clock spring, sliding-nose drive and J3 dowel stop. Cuff twist and R17 have
  never been measured on this chain. The knee spans 59.27..107.07 deg with a margin of 34-48 deg. The waist removes 27 %
  of link 2's out-of-plane section modulus at the station that carries the J3 stop reaction. Nobody checked it.
- **Continuity:**
  - The rule's flood is clean on both wears.
  - Held, without envelope stepping stones (knn), 77 of 332 forced taken poses are cut off: 30.69 vs 22.45.

## Checks (tools/alignment_audit.py)

After the re-wear, ok: held_out, fast_frozen, near_touch, contact_depth, dominance, idle, sampling, density,
judge_change, rules.

| check | level | reason |
|---|---|---|
| held_out | ok | +4.17 |
| near_touch | ok | plain 18.28, near1 19.92, near2 34.84, near3 86.16; 16.56 points in the 1-2 mm shell |
| dominance | ok | vs the lead: plain +0.00, 2 mm +0.00 |
| sampling | ok | sample-weighted 0.900 vs part-weighted 0.924 |
| continuity | watch | the tool reads floods only from verifier files and the row, so it cannot see this audit's flood files (measured clean above) |
| fold_margin | watch | the same reason (measured 5.181 / 5.006 above) |
| complexity | watch | recomputed 0.0 vs row 18.5 |
| reporting | watch | a screen's verdict on a verified row; dashboard sweep 12.5 (95.45) |

## Findings

Each finding has its full numbers and files in the findings JSON.

1. **NEW-hidden-lift: the hardening is a part the stated build does not make (GAMED).**
   - **Pattern:** the model moves link 2's samples in the plate plane and keeps each row's height (jog_disp). Link 2's
     skin-fitted underside at the binder is not flat: rows 0-3 sit at r 69.55 / 68.43 / 68.86 / 69.20 mm from GH. So the
     moved edge rides up to 0.95 mm above the real underside, an unstated radial lift.
   - **Evidence:** the verifier's true cut places each moved sample on the original section. It reads exactly the lead:
     - bench probes 18.83 / 18.83 / 19.37;
     - pose 139 at 0.073 mm;
     - ib14 0.9013;
     - held 22.38.

     The modelled waist reads +0.2 mm probe 18.29 on the bench but 22.44 vs 22.38 held. I re-read all six dumps myself
     (table above).
   - **Why the exo is not better:**
     - A laser-cut waist changes nothing for the wearer, except that it weakens link 2.
     - The modelled benefit belongs to a different part: a machined raised edge zone that nobody priced.
     - Even modelled, 139 stays at 0.6 mm, metal on skin for a real arm, and held loses through in-band.
   - **Why gamed:**
     - The round ranks at the +0.2 mm probe, and there the recorded number puts the design 0.54 ahead of a lead that is
       at least as good for the wearer.
     - Under the same harness held out, the design is behind at every probe level.
     - As stated, it is identical to the lead.
   - **Action:**
     - Record the probes as the true cut's (18.83 / 18.83 / 19.37) and mark the hardening refuted.
     - If the lift is the idea, model it as an explicit machined edge-zone lift on the kit's underside rule, with its
       in-band cost.
     - The plain v_gap 18.28 needs no change.
2. **R2: refuted records still shown (watch).**
   - The refuted numbers are still on file:
     - frozen_exact still carries p139 0.602 and probe01 / probe02 18.28;
     - the verdict on the row and on morphs.json still opens "removes the lead's only +0.1 / +0.2 mm probe flip";
     - the doc keeps lessons (3) and (4), which the verifier showed are mis-attributed.
   - "Far edge kept" is also wrong. The far row moves +0.18-0.26 mm, and the narrowing is about 1.33 mm, not 1.6.
     Held overhead pose 898 moves 1.67 -> 1.528 mm.
3. **R1: screen strings on a verified row (watch).**
   - The verdict opens "SCREENED".
   - morphs.json shows gap / sweep_gap 12.5 (score 95.45, above the board's 95 line). That number is the lead's own fit
     number, not this design's measurement.
   - The alignment fields are empty.
4. **G5: complexity 0 on the board, 18.5 real (watch).**
   - The row's delta mechanism record recomputes to the anchor, 0.
   - On the score-vs-simplicity view the design therefore Pareto-dominates the lead it copies: 93.35 at 0 against 93.35
     at 18.5.
   - Measured dominance on the board's 37 verified rows: 33 of 36 at the shown 0, 12 at the true 18.5.
5. **P1: placed on the claim bench (watch).**
   - The binder pose, the pre-registered filter (139 >= 0.4 mm) and the guard poses all come from exact Bench(110,360).
   - The search bench can move only one pose (envh 150), so the gate is flat and dl sits at its box edge, 1.6.
   - Held, never tuned on, loses 0.07.
6. **T1: a sub-millimetre lever under the 1 mm line (watch).**
   - 139 stays at 0.60 mm, so near1 is unchanged.
   - 16.56 points live in the 1-2 mm shell, carried from the lead.
7. **G1: overhead metal moves toward the skin (watch).**
   - Held 898 (elevation 165): 1.67 -> 1.528 mm.
   - Held overhead lowest-metal p10: 1.50 -> 1.42 mm.
   - Bench overhead in-band: 0.9359 -> 0.9341.
8. **S5: the held reach rests on stepping stones (watch).**
   - The first held flood of this chain: the rule's flood is full, 22.45.
   - The knn flood drops 77 of 332 forced taken poses (30.69, +8.24). The connected set exists only through the 526
     envelope stepping-stone poses.
   - This is the lead chain's property, not the waist's.
9. **Carried from the lead's chain, all watch:**
   - NEW-ws-inband: workspace in-band 0.8665, 0.8309 at elevation 90-140; slightly worse than the lead.
   - NEW-strap-dilution: equal-strap gap 18.74 bench (lead 18.67) and 22.97 held; held ib14 0.8993 sits under the hinge.
   - T3: th 5.181 / 5.006; J3 dowel held margin 0.74 deg.
   - M5: spring, R17 and cuff twist never measured. New: the waist cuts link 2's section modulus by 27 % at the J3-stop
     load path, and it was never checked.
   - G4: m_sub at rest, not re-measured.
   - P2: a held leak in form from the lead's knee re-centring, with zero measured effect.

Patterns walked and found absent:
- **T2:** clip in-band histogram equal to the 4th decimal; band 3-14 mm gap 18.41 vs 18.34.
- **T4:** no singular bound moved. The dl box edge is a planform size, not a singularity margin.
- **T5:** depth equal on the bench and lower held, mostly through the lift.
- **S1:** held +4.17 is the lead's own drop, plus 0.07.
- **S2 / S6:** link 2 keeps 124 samples (kit density 0.919x); the roller is 4.55x over-dense, as on the lead.
- **S3:** the strap and the top contact set move with the underside (asserted in apply_jog).
- **S4:** none.
- **M1 / M2:** O20 untouched; the waist is real metal (its realism is finding 1).
- **M3:** part pairs re-checked in the frozen run (parts 0 on both wears).
- **M4:** the knee spans 46.7 deg and dK 45.6 deg.
- **P3:** two wears, each reproduced exactly; 540 configs with the spread reported.
- **P4:** no measurement file in the row's 4 commits.
- **R3:** 540 configs; the top-5 spread is given.
- **R4:** v_gap on the board equals the verifier's.
- **G2 / G3:** see M5.
- **G6:** 3 active DOF.

## Proposals (proposals only; none feeds this verdict)

1. **Catalogue entry M6, "a sample move the stated manufacturing operation cannot make".**
   - **Looks like:** a profile change that claims cx +0 as a cut, but whose samples keep a coordinate the cut cannot keep.
     Here, an in-plane move that keeps each row's height over a curved, skin-fitted underside.
   - **Detect:** re-derive every moved sample from the stated operation, then re-wear:
     - a cut lies on the original surface;
     - a bend preserves the section;
     - a joggle respects the 5 t radius.
   - Give 'gamed' when the stated-operation re-wear removes the claimed ranking gain.
   - **Measured effect:** measured on this row only, where the probes return to the lead's (18.83 / 18.83 / 19.37) and
     the plain v_gap is unchanged (18.28). Of the other round-15 profile edits, conecut-h2facet's chamfer is a solid cut
     sampled as one, so it would be unaffected. I did not survey every verified row for post-fit sample transforms in the
     time box.
2. **Read auditor flood and fold-margin files in the audit tool.**
   - The continuity and fold_margin checks read only verifier files and the row. This audit's flood and th readings
     (remeasure/*_flood_bench.json, *_flood_held.json, written through the lead verifier harness unchanged) are therefore
     invisible to it, and both checks stay at "none on file".
   - Proposal: read `remeasure/<id>_flood_*.json` when its frozen gap reproduces the claim (+-0.05).
   - **Measured effect here:** continuity becomes ok on the bench. On held it becomes watch through the knn line
     (+8.24 > 3). fold_margin becomes ok (5.006).
3. **Rank-at-probe hygiene.** Round 15 ranks at the +0.2 mm probe. Proposal: any claim whose probe gain comes from moved
   samples must also report the stated-operation re-wear (proposal 1) before the probe ranks it.
   - **Measured effect:** this row's probe edge (0.54) goes to 0. The other verified rows were not re-measured for this
     proposal.
4. **Dashboard complexity for delta records.** Have tools/dash_build.py follow a delta record's `source` and add the
   `record_delta`, so conecut-h2facet, conecut-l2jog and lowarm-kphase-notch show the lead's 18.5 and not 0.
   - **Measured effect here:** this row dominates 12 of 36 verified rows, not 33.
