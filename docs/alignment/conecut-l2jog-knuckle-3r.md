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

## Skeptic (2026-10-18 ~16:50-17:15 UTC)

**Final ledger verdict: GAMED.** The ledger computes it (`python3 tools/alignment_ledger.py get conecut-l2jog-knuckle-3r`,
stage skeptic, 17:13:36Z). I refuted 2 of the 18 reasons with evidence (fold_margin and G1). The other 16 stand, and
NEW-hidden-lift stands as gamed.

What I measured or re-derived myself (models unchanged):
- **Probes from all six committed per-pose dumps** (tools/alignment_paired.py gap_parts; a taken pose with
  min(min_mm, cmin) < X counts as contact). Every number in the auditor's table reproduces:
  - bench +0.2: modelled 18.29 against true cut / lead 18.83;
  - held: 22.44 against 22.38 at every probe level.
- **Status:** the three dumps share their pose keys. Status (taken / contact) differs on 0 poses, model vs lead and
  true cut vs lead, on both wears.
- **m_sub-at-rest probe on this row** (new file docs/alignment/remeasure/conecut-l2jog-knuckle-3r_skeptic_msub_rest_bench.json;
  CB_EXACT=1, nice, 1 process, 136 s):
  - It reproduces the frozen claim (18.28 / reach 0.7278 / ib14 0.9005). The family th reading is 5.181, lt5 0.
  - m_sub at rest: min 0.0, p10 0.267, lt1 50 of 205.
  - Chain coordinates (th, dK, m_plain, m_eff, m_sub) equal the lead's on all 372 taken rows. Only min_mm differs, at
    139 (0.072 -> 0.602) and 345 (1.709 -> 1.606).

| key | ruling | evidence (short; full text in conecut-l2jog-knuckle-3r.rulings.json) |
|---|---|---|
| continuity | upheld (watch) | The flood is on file (remeasure/_flood_*.json). By c_continuity's rule the bench reads ok (full 0, knn +1.69) and held reads WATCH (knn 30.69 vs 22.45: +8.24 > 3; 77 of 332 forced dropped). |
| fold_margin | **refuted** | On file: _flood_bench.json:extra.th_margin.min 5.181, _flood_held.json 5.006, lt5 0. My msub probe re-measures 5.181. c_fold_margin reads ok (gamed only < 4.95). |
| complexity | upheld | tools/simplicity.py gives this id 0 and the lead 18.5; the row says 18.5; morphs.json shows 0. |
| reporting | upheld | morphs.json: gap / sweep_gap 12.5, v_gap 18.28, verdict 'SCREENED ...' on a verified row. |
| NEW-hidden-lift | upheld (**gamed**) | Probes re-derived (above). Lift on file: verify/..._v_truecut_scan_bench.json waist_truecut model_lift_mm [-0.298, 0.951]. ROUNDS.md 4603-4604 ranks at the probe; the plain gap ties and both designs have 0 passive translations, so the probe decides the tie with an artifact. **It is already being used:** lowarm-kstop-knuckle-3r.md lines 117 / 200 / 229 / 288-289 plan the combined cell on l2jog's modelled 139 readings (0.487 at dl 1.0, 0.602). Corrections, level unchanged: (a) as the stated cut the design is status-identical to the lead, not identical pose for pose (on held, 5 pose minima are 0-0.40 mm higher; summed contact depth 60.09 vs 60.97 mm); (b) the modelled field is mixed (-0.30 to +0.95 mm). |
| R2 | upheld | Also unlisted: rows:spec_jog.frozen_exact p139 0.726 / probe02 18.28 (true cut 0.059). Doc line 127 still says 'held 898 1.67 (unchanged)', but the dump reads 1.528. Lesson (3) at doc lines 173-175 is unstruck. |
| R1 | upheld | 'SCREENED' verdict; gap 12.5 = the lead's fit_fast number; alignment ''. |
| G5 | upheld | Recount from morphs.json: dominates 33 of 36 verified rows at the shown 0, 12 of 36 at 18.5. |
| P1 | upheld | JB = 13 (pose 139's binder, line 54); dl box 0..1.6 (line 63), best 1.6; pre-registered 139 >= 0.4 on the claim bench; held 22.45 vs 22.38. |
| T1 | upheld (report-only) | Shell 16.55 > 15. The tool's near_touch is report-only by the user's 2026-10-17 ruling (alignment_audit.py lines 279-282). |
| G1 | **refuted** | No in-band gain (0.9012 -> 0.9005; held 0.9000 -> 0.8993), and near2 is identical (34.84 / 37.11). The 'held overhead p10 1.50 -> 1.42' does not reproduce: per-pose p10 over the 18 taken overhead poses is 1.431 / 1.196 on both the lead and the model. Only 898 (-0.14) and 345 (-0.10) move, and both return as the stated cut (1.691 / 1.710). They belong to NEW-hidden-lift. |
| NEW-ws-inband | upheld | probe_bench.json 0.8665 / 0.8309 / 0.9341 vs the lead's 0.8676 / 0.8315 / 0.9359; L2 part 0.726 / 0.723. |
| NEW-strap-dilution | upheld | c4_inband 18.74 / 22.97, chain-only 0.8581, held ib14 0.8993. |
| T3 | upheld | th 5.181 / 5.006; held J3 dowel margin_lo 0.74, 19 stopped. |
| M5 | upheld (watch), corrected | R17 / cuff twist ARE measured on the lead's CAD: user_conecut_knee/judge/scorecard.md R17 PASS; dynamics.json twist 3.99 deg, 0.57 N, 0.126 N.m. The waisted link 2's strength is unchecked. With the measured narrowing (5.87 -> 4.54) its out-of-plane modulus drops 22.7 % (not 27 %), and its in-plane modulus 40 %. |
| G4 | upheld, now measured | m_sub at rest lt1 50 of 205, p10 0.267: identical to the lead. |
| P2 | upheld (carried) | Inherited chain; zero measured effect (lead heldleak_check). |
| S5 | upheld | Held knn 30.69, 255 of 332 forced connected. |

### Missed by the audit (for the next audit; these do not change this verdict)

1. **The artifact is propagating into another row's claim.** docs/concepts/lowarm-kstop-knuckle-3r.md does two things:
   - Line 117: '139 at the probes ... fails at +0.1: the claim needs conecut-l2jog (dl 1.0 planform: 0.487)'.
   - Lines 200, 229 and 288-289: plans the next combined cell 'kstop + conecut-h2facet + conecut-l2jog' on 'l2jog reads
     139 at 0.602'.

   docs/concepts/round15_ideation.md line 210 still calls l2jog 'a 0-cx probe hardener ... 18.83 -> ~18.28'. A combined
   cell built on the modelled waist would inherit the 0.95 mm edge lift and read the probe gain again. As a true cut,
   139 is 0.073 at dl 1.6 (and 0.059 for the spec jog), which hardens nothing.

   Action: the combined cell's claim must use the true-cut waist (verify/conecut-l2jog-knuckle-3r.py true_disp), or
   price the lift as a machined edge zone.
2. **A second refuted record on the row:** spec_jog.frozen_exact (p139 0.726, probe02 18.28). It has the same artifact
   (verification.truecut.jog_truecut_bench_p139 0.059), and R2 did not list it.
3. **'Built as stated = the lead pose for pose' is slightly overstated.** The true-cut held dump moves 5 pose minima by
   0 to +0.40 mm against the lead (the 224 / 225 / 252 contact cluster, plus 305). The summed held contact depth is
   60.09 vs 60.97 mm. Status, plain gap and probes are equal. This is a small real benefit of the true cut, not gaming.
4. **The modelled waist is not a pure lift.** The true-cut scan's model_lift_mm is [-0.298, +0.951]. Some moved samples
   sit up to 0.30 mm below the original underside, so as modelled part of the edge zone also sinks. This matters for
   the auditor's proposed M6 detector, which should flag both signs.
5. **G1 and M5 measurement slips in the audit:**
   - the held overhead p10 '1.50 -> 1.42' does not reproduce from the dumps;
   - the 27 % section-modulus cut uses the row's refuted 1.6 mm narrowing. The measured narrowing is 1.33 mm, giving
     22.7 % out of plane and 40 % in plane.

Files: docs/alignment/conecut-l2jog-knuckle-3r.rulings.json; docs/alignment/remeasure/conecut-l2jog-knuckle-3r_skeptic_msub_rest_bench.json;
ledger entry `skeptic:conecut-l2jog-knuckle-3r` (final verdict **gamed**).
