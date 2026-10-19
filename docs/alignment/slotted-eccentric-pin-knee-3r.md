# Alignment audit: slotted-eccentric-pin-knee-3r (round 14, slice r14-B)

Auditor run 2026-10-18 08:11-08:45 UTC. Tool `tools/alignment_audit.py` VERSION 2026-10-18.1, reference
conecut-knee-knuckle-3r. Ledger entry by auditor, run `audit:slotted-eccentric-pin-knee-3r` (git 1a20637).
This replaces the 02:37 auditor sections, which audited the old claim 201.20 (config B-g47-2). The 02:41 skeptic
section on that old claim is kept below the dated rule at the end.

## Verdict: WATCH (claim 97.04)

- The claim is the row's v_gap: 97.04 on Bench(110,360) exact, frozen shape (score 64.7), config E1-g13-3. The fast
  search number is 86.82. The claim moved from 201.20 since the last audit: two death audits and a re-dispatch ran
  more CMA (the row's commits 50c40c9, 49de388, 8d4590e).
- This audit re-wore E1-g13-3 through the model's own `frozen()`, unchanged (`tools/alignment_slotted_rewear.py`):
  - fit Bench(60,160) fast at the 1 mm part-part rule: 89.42;
  - Bench(110,360) exact: 97.04, the claim to the digit;
  - held out (poses disjoint from Bench(110,360)): 93.02, which is 4.02 better than the bench.
- Nothing in the number is bought by gaming. The design is 78.76 plain points behind the lead (18.28) and 83.27 behind
  at 2 mm, so no pattern here ranks it above a design that is better for the wearer, and no hard rule is broken.
- All findings are watch. The new one is about depth: the claim got better while its skin presses got much deeper
  (deepest 9.92 -> 34.90 mm).

## What the wearer gets (measured on the re-wear; held out in brackets)

Files: `docs/alignment/remeasure/slotted-eccentric-pin-knee-3r_bench.json` and `_held.json`, per-pose dumps in
`_bench_perpose.json` and `_held_perpose.json`.

**Reach and follow**
- Overhead reach (workspace, elevation >= 140): 0 / 28 taken (0 / 26). Only 12 / 28 (11 / 26) even close
  kinematically; the slot track ends at th 125.75. Overhead clip frames: 0 / 10.
- Raised arm (elevation 90-140): 12 / 85 taken (16 / 86).
- Overall reach 0.461 (0.494); follow 0.682 (0.700). Kinematic reach 0.608 (0.633) against th need p5-p95 27.1-143.2.
- The track's lower end at th 62.25 is a hard stop that sits above the rest region (th p5 27.1). The wearer's arm at
  rest and in scapular-plane overhead is outside the window.

**Clearance and contact**
- Taken poses with metal < 2 mm: 21 of 241 (27 of 255). Under 1 mm: 6 (11). Under 3 mm: 128 (144). Minimum 0.237 mm
  (0.146 mm).
- Per-pose clearance floors (wear probe): the closest metal sits at 2-3 mm on 43 of 75 taken clip poses and 64 of 166
  taken workspace poses.
- Near-touch gaps (report only): 103.66 at 1 mm, 118.11 at 2 mm, 218.31 at 3 mm (101.62 / 116.55 / 219.90). Band
  read as 3-14 mm: 97.72.
- Contact: 16 poses press into the skin (16 held out), summed 95.67 mm (55.50 mm), 10 deeper than 3 mm (6).
  - Deepest on the bench: 34.90 mm at workspace plane 150, elevation 120, axial -180 (across the body, raised,
    full rotation).
  - Next deepest: 10.33 mm at plane -90, elevation 60, axial 135; then 7.49 mm at plane -15, elevation 90, axial 105.
  - Deepest held out: 13.36 mm at plane 0, elevation 90, axial 90.

**In-band**
- Clip frames: 0.699 in band 2-14 mm (0.684), 0.354 in band 2-10 mm (0.347).
- Workspace, unscored: 0.725 (0.722) over 166 (178) taken workspace poses. Raised arm: 0.835 (0.802).
- Per part (fractions; `frozen.inband_member`):
  - crank 0.36 (0.35);
  - L2b 0.23 (0.20);
  - hub 3 0.55 (0.52);
  - pinK 0.59 (0.56);
  - track node 1 0.57 (0.56);
  - hub 2 0.86 (0.84), up from 0.00 at the old claim. Its post lift is 0.85 mm, K's 4.44 mm, hub 3's 4.0 mm.
- Per-part sample counts (a third wear, `tools/alignment_slotted_partcounts.py`, 97.04 reproduced; file
  `docs/alignment/remeasure/slotted-eccentric-pin-knee-3r_partcounts.json`, 75 taken clip frames not in contact):
  no part has zero samples; the thinnest are the track nodes at 35 samples per pose (2625 clip samples). The worst
  parts are the most sampled: L2b 315 per pose (0.23 in band, median 16.63 mm) and the crank 105 per pose (0.36,
  14.77 mm). Sample-weighted in-band is 0.699 and part-weighted 0.793, so the weighting does not flatter.

**Springs, stops, transmission, cuff twist**
- Springs: none. K is slaved by the roller in the slot: one determined loop, one branch.
- Stops: the track ends at th 62.25 and 125.75 deg (fit). Taken th spans 62.80-119.34 (62.43-124.59).
- Fold margin in th, at the effective a2 the model reads (its own `geom()` mg): minimum over taken poses 12.53 deg
  (7.27 held out). The rule is 5.23.
- Knee transmission psi: minimum 62.00 deg (61.15). The rule is 15. No near-singular posture is taken.
- Cuff twist: not measurable. The pin-knee cuff is not in the model; member 3 is the kit neck (finding S3).

**Moving coordinates over taken poses (idle check)**
- K: 62.0-108.0 deg, a span of 46.0 deg.
- Effective a2: 63.37-81.91 deg.
- Crank q1: -73.1 to 33.2 deg.
- Roller on the track: e 32.85-47.94 deg.
- Nothing is idle.

## The 12 checks (`docs/alignment/slotted-eccentric-pin-knee-3r.json`, after the re-wear)

| check | level | measured reason |
|---|---|---|
| held_out | ok | held out 93.02 vs bench 97.04 (-4.02; re-measured) |
| fast_frozen | ok | fast 86.82 -> frozen exact 97.04 (+10.22) |
| near_touch | ok | 97.04 / 103.66 / 118.11 / 218.31 at 0 / 1 / 2 / 3 mm; band read 3-14 mm 97.72; 21.07 points in the 0-2 mm shell |
| contact_depth | watch | bench 16 poses, 95.67 mm, deepest 34.9 mm vs the reference's 20.24 mm (x4.73, +75.43 mm); held 55.50 vs 60.97 mm (x0.91) |
| dominance | ok | vs conecut-knee-knuckle-3r: -78.76 plain, -83.27 at 2 mm |
| continuity | watch | no continuity flood on file |
| fold_margin | watch | the tool does not read the re-wear's `kin.fold_margin_th_min_taken`; measured 12.53 / 7.27 deg (above) |
| idle | ok | K moves 46.01 deg |
| sampling | watch | fractions only; crank 0.36, L2b 0.23 |
| density | ok | not measured |
| complexity | ok | recomputed 5.0 = row 5.0 |
| reporting | watch | dashboard sweep best 86.82 sits 10.22 below the claim |
| judge_change | ok | no bench, judge or metric file in the row's 6 commits |
| rules | ok | O20 at J1-J3 and K, margin 5.23, 0 passive translations, 3 active |

The fold_margin watch is a reader gap, not a margin problem: the 02:51 skeptic refuted the same reading on the old
claim. Proposal F-a below still stands.

## Findings (`docs/alignment/slotted-eccentric-pin-knee-3r.findings.json`)

### 1. T5 (watch): the claim got better and its presses got deeper

**Evidence.**
- Old claim (201.20, B-g47-2): 8 contact poses, 27.78 mm summed, deepest 9.92 mm. Held out: 9 poses, 33.13 mm,
  deepest 9.94 mm.
- New claim (97.04, E1-g13-3): 16 poses, 95.67 mm summed, deepest 34.90 mm, 10 deeper than 3 mm. Held out: 16 poses,
  55.50 mm, deepest 13.36 mm.
- The contact share fell (0.101 -> 0.062) only because many more poses close (taken 71 -> 241).
- Against the lead: x4.73 and +75.43 mm on the bench. Held out x0.91.

**Why this is not a better exo.** Metal 3.5 cm inside the arm, across the body with the arm raised, is a block or a
bruise. The contact term charges it the same as a 0.1 mm touch.

**Why watch, not gamed.** The design is 79 points behind the lead. The depth ranks it above no better design.

**Action.** Report only; the score stays as is (user ruling 2026-10-17).

### 2. T1 (watch): the whole search ran on the plain gap

**Evidence.**
- All 1763 configurations in `docs/concepts/sweeps/slotted-eccentric-pin-knee-3r.json` have `near: 0`, including the
  death auditors' AUD2 and AUD3 streams that found the claim.
- CLAUDE.md rule: "every search objective is the near-touch gap".
- Measured cost: 97.04 plain -> 103.66 at 1 mm (+6.62) on the bench, 93.02 -> 101.62 (+8.60) held out.

**Why this is not a better exo.** A plain-gap optimum can park metal at 0.1-1 mm, which is metal on a real arm.

**Action.** Any further search on this row (the open gate is a farm job of about 1000 tries) runs with `near=1`.

### 3. G1 (watch): metal hugging the skin

**Evidence.**
- 21 of 241 taken poses have metal < 2 mm, and 128 of 241 have metal < 3 mm (53 %).
- Held out: 27 / 144 of 255.
- 21.07 points of the bench gap live in the 0-2 mm shell, above the catalogue's watch line of 15.
- The lead has 33 of 372 < 2 mm and 105 of 372 < 3 mm (28 %).

**Action.** Report only (user ruling 2026-10-17: near-touch is not a gate).

### 4. S5 (watch): no continuity flood

**What was measured.** A bench-graph flood upper bound on this audit's per-pose dumps
(`tools/alignment_benchgraph_flood.py`):
- Bench: at most 121 of 166 taken workspace poses connect. Reach 0.461 -> <= 0.336, a loss of >= 12.50 points.
- Held out: at most 120 of 178. Reach 0.494 -> <= 0.333, a loss of >= 16.11 points.
- The bench graph is sparse (1.13 neighbours per cell; 52 of 360 cells have none), so part of that loss is the
  graph, not the design.
- K stays on one branch (psi at least 61 deg), so a branch flip is not the cause.

**Action.** A flood (connected_full) is owed before any connected-reach claim. It can only lower this row's reach.

### 5. S3 (watch): the cuff pin knee in the name is not in the model

**Evidence.** The row's name and `mechanism.cuff_knee` declare the cuff: pins, knee link and arm pad. The model builds
member 3 as the kit neck (model lines 9-15). The re-wear samples 17 metal groups, and none is the cuff knee.

**Why it does not flatter.** The doc's paired controls put the kit neck about 7.6-10 points behind the real pin knee.

**Action.** Label the row "eccentric J2 at the pin-knee seats (kit neck)".

### 6. R1 (watch): an auditor's self-found, self-measured number in the verified column

**Evidence.**
- The dashboard's Verified gap 97.04 is the second death auditor's frozen exact of E1-g13-3, a configuration the same
  auditor found with its own CMA (stream AUD2, 185 evaluations).
- Death auditors ran 461 of the 1763 sweep configurations (AUD2 352, AUD3 109).
- There is no verifier file for this id, and the status is screened.
- The row is internally stale: its top-level `exact_frozen` block and `limiter` still describe D2-g9-0 (117.68).

**Why it does not flatter.** This audit re-wore E1-g13-3 independently: 97.04 to the digit, held out 93.02.

**Action.** Labelling only. Refresh `exact_frozen` and `limiter` to E1-g13-3.

### Patterns checked and not present

- **T2:** the band read as 3-14 mm moves the gap only 0.68 points (97.72).
- **T3:** the fold margin is read in th at the model's own effective a2: 12.53 deg bench, 7.27 held, rule 5.23.
- **T4:** margin, psi_lo and lock_min sit at their rule floors by construction (hard box edges). The taken poses stay
  clear of them (margin 7.27, psi 61). `emax` was freed from 40 to 49.75 by a death audit; it bounds how far the track
  runs from J2 (a size bound, not a singularity margin). The track reaches e 47.94, 1.8 deg under it.
- **S1, P1:** held out 4.02 better than the bench.
- **S2:** the sampling check lists crank 0.36 and L2b 0.23, but they are the most sampled parts; part-weighted
  in-band (0.793) is above sample-weighted (0.699), the opposite of S2.
- **S4:** no instance.
- **M1, M2:** O20 is forced at J1-J3 and K in `_clean`. The roller is an MR52ZZ on an O2 dowel; the track is a 2 mm
  plate.
- **M3:** pinK still has no `over` list, which makes the model over-strict, not optimistic.
- **M4:** K moves 46.0 deg and a2e 18.5 deg; nothing is idle.
- **M5, G2, G3:** no springs. Cuff twist is not modelled (S3).
- **P2:** the search ran on Bench(60,160) only. Held out was first touched by audits.
- **P3, R3:** best of 1763 with the convergence gate reported (24.24 / 23.91 / 0.52, not converged). Fast to frozen
  +10.22, inside the verified rows' 4.6-14.
- **P4:** no judge change in the row's 6 commits.
- **R2:** the old NEW-dishonest-sweep-best finding is gone for this row. The dashboard sweep best is now 86.82,
  E1-g13-3, honest.
- **R4:** dashboard v_gap 97.04 equals the row, and its v_contact 0.0623 equals the frozen exact.
- **G4:** no taken pose is near-singular.
- **G5:** complexity recomputes to 5.0.
- **G6:** 3 active joints.
- Motion preview: `docs/concepts/viz/concepts/slotted-eccentric-pin-knee-3r.js` carries E1-g13-3's law and track, but
  draws it on the k4598 home geometry, not on E1's own seats. The file says so; it does not change a number.

## Proposals (not applied; not inputs to the verdict)

- **F-a (fold-margin reader), from the last audit, still open.** `c_fold_margin` would also read a re-measure file's
  `kin.fold_margin_th_min_taken`. For this row that turns the watch into ok at 12.53 deg (7.27 held out). No other
  row has the key today.
- **T5-b (depth trend on a moved claim).** When a claim moves, `contact_depth` would also compare the new claim's
  summed and deepest press with the previous claim's re-wear of the same design. Measured effect: only this row has two
  re-wears on file for two claims. It gives watch here (27.78 -> 95.67 mm, 9.92 -> 34.90 mm) and changes no verdict.
- **P5 (catalogue entry, proposed): the death auditor becomes the optimiser.** A refute-or-stand audit that runs its own
  CMA, and whose best becomes the row's claim and its v_* numbers, is a search plus a self-measure. It is the same
  pattern as R1. Detect: sweep streams tagged AUD* that hold the row's `best_k`. Here: 461 audit evaluations, `best_k`
  E1-g13-3 in AUD2. Proposal: such a claim is labelled "audit-found" until a verifier writes a file.

## What I could not measure, and why

- **Continuity flood (connected_full):** this kit model has no verifier `extras()` flood. Only the bench-graph upper
  bound above is on file.
- **Which part made the 34.90 mm press:** the per-pose dump records the minimum metal, not its part. A per-part
  attribution needs another wear; it was not run inside the time box.
- **Cuff twist and the cuff knee's clearance:** the knee is not in the model.
- **R17 dynamics:** no CAD, and none is required for a screened row.

The next loop step is unchanged. This design stays screened and far behind. Nothing here moves it, and no new leader
is involved.

---

*Earlier skeptic review of the 02:37 audit (old claim 201.20), kept as written. Rule dated 2026-10-18 08:45 UTC.*

## Skeptic (2026-10-18 02:41-02:51 UTC)

Run `skeptic:slotted-eccentric-pin-knee-3r`, rulings in `docs/alignment/slotted-eccentric-pin-knee-3r.rulings.json`,
ledger entry 2026-10-18T02:50:50Z. **Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.**
Refuted 4 of 11 (fold_margin, S2, G1, R1); upheld 7.

**What this skeptic measured (models unchanged):**
- A third wear of the claim, through the model's own `frozen()`, CB_EXACT=1, niced, 1 process, with a new read-only tool
  `tools/alignment_slotted_partcounts.py`. It gave fit 188.47 and frozen exact 201.20 (ib14 0.6042), the claim to the
  digit. Output: `docs/alignment/remeasure/slotted-eccentric-pin-knee-3r_partcounts.json`. Per-member fractions
  re-derived from the samples equal the kit's `inband_member` exactly.
- Per-part sample counts on Bench(110,360) exact. These are clip frames that are taken and not in contact; there are
  only 6 such frames.

  | part | clip samples | in band 2-14 | median clearance (mm) |
  |---|---|---|---|
  | hub1 | 486 | 1.00 | 7.95 |
  | hub2 | 486 | 0.00 | 18.07 |
  | hub3 | 486 | 0.51 | 13.75 |
  | pinK | 1182 | 0.78 | 13.21 |
  | studG | 894 | 0.83 | 5.88 |
  | link1 | 1344 | 0.75 | 7.94 |
  | spoke | 510 | 0.53 | 12.67 |
  | trk1 | 168 | 0.64 | 10.01 |
  | trk2 | 168 | 1.00 | 5.37 |
  | trk3 | 168 | 1.00 | 6.36 |
  | trk4 | 168 | 1.00 | 6.54 |
  | trk5 | 168 | 1.00 | 6.06 |
  | neck | 1248 | 0.67 | 10.69 |
  | crank | 756 | 0.36 | 20.16 |
  | L2b | 2100 | 0.27 | 15.89 |
  | armG | 570 | 0.79 | 11.48 |

  Sample-weighted in-band is 0.6042 and part-weighted is 0.6958 (-9.16 points). No part has fewer than 168 samples.
- Fold margin, recomputed from the per-pose th with the model's own `a2e_of()` and the kit formula at the per-pose
  J2-J3 angle a2e: 15.801 deg on the bench (71 taken) and 17.303 held out (76 taken). Both match the remeasure `kin`
  to within 0.001.
- A bench-graph flood upper bound, from the new tool `tools/alignment_benchgraph_flood.py` on the per-pose dumps. It
  uses connected()'s graph without the edge closure checks, seeded at taken ws poses with elevation <= 30.
  - Bench: at most 27 of 65 taken poses connect (reach 0.181 -> <= 0.075), a loss of >= 10.56 points.
  - Held out: at most 39 of 69 connect, a loss of >= 8.33 points.
  - The bench graph is sparse: 1.13 neighbours per ws cell, and 52 of 360 cells have none. So this is not the rule's
    envelope flood.

**Rulings**

| key | refuted | evidence (short; full text in the rulings file) |
|---|---|---|
| fast_frozen | no | +47.71 > ff_watch 14. Of it, +34.98 is the search's 0.5 mm part-part overlap vs the 1 mm rule (153.49 -> fit 188.47, same bench, doc line 107), and +12.73 is the freeze + exact wear. No other ruling covers the bulk. |
| continuity | no | No flood on file. The bench-graph upper bound loses >= 10.56 (bench) / >= 8.33 (held) points, so it cannot show <= 1. |
| fold_margin | **yes** | Measured 15.801 / 17.303 deg (>= TH fold_min 5.0). On file in remeasure `kin.fold_margin_th_min_taken`; the tool's reader only misses it. |
| sampling | no | Counts measured: no thin and no zero-sample parts, part-weighted -9.16. The documented < 0.5 trigger still fires: hub2 0.00 (18.07 mm median), crank 0.36 (20.16 mm), L2b 0.27 (15.89 mm). |
| reporting | no | morphs.json sweep_gap 97.45 vs v_gap 201.20 confirmed. |
| NEW-dishonest-sweep-best | no | Sweep file AUD-g9-2, k 1013, honest False, gap 97.45 = the best of 150 dishonest entries. 9 lock=1 entries best 30.24. dash_build.py never reads `honest`. |
| S3 | no | Model lines 9-15: member 3 is the kit neck. The 16 sampled groups contain no cuff-knee body. The 36.83 vs 27.20 comparison crosses harnesses, so "pessimistic" is not proven either. |
| S2 | **yes** | The out-of-band parts are the heavily sampled ones: 3342 of 10902 samples, with L2b the largest share at 19.3 %. Sample weighting therefore lowers in-band by 9.16 points rather than hiding them. Hub 2's 71.2 mm is its level from GH; its clearance median is 18.07 mm. |
| G1 | **yes** | Counts confirmed (7/20/31 of 71; 3/15/21 of 76). The documented level is report-only: near_touch reads ok, c_near_touch lines 277-279. Same ruling as dogring. |
| S5 | no | Confirmed: 82/110 clip frames and 72/128 ws poses at elevation <= 30 have th < 74, and psi min is 72.68. No flood on file; the bench-graph loss is >= 10.56. |
| R1 | **yes** | 201.20 reproduced to the digit by three independent wears: the death audit, the auditor's re-wear and this skeptic's run. It is pessimistic, and only the status label remains. |

**Missed by the auditor (for the next audit; this verdict does not change):**
1. **Continuity is probably worse than watch.** On connected()'s bench graph, the static reach keeps at most 27 of 65
   poses (bench) and 39 of 69 (held). That is a loss of >= 10.56 / 8.33 points, against conn_gamed 3.
   - The bench graph is sparse, so only the envelope flood (connected_full) can decide.
   - If that flood confirms a loss > 3, continuity reads `gamed`. That would not move the rank, which is already 201.
   - The flood is owed before any connected-reach claim.
2. **The headline gap is at a laxer part-part rule.** +34.98 of the fast -> frozen drop is the kit's 0.5 mm radial
   part-part overlap in the search, against the 1 mm rule that frozen() applies.
   - The dashboard's "claimed" column can therefore mix part-part rules across kit models.
   - Check other kit rows' headline gaps for the same split (fit at 1 mm vs search number).
3. **The scored in-band rests on 6 clip frames.** The inband14 0.604, and every per-part fraction, is a mean over the
   6 of 110 clip frames that are taken and contact-free. It is corroborated by the unscored workspace in-band, 0.652
   over 65 poses.
   - This is a fragility, not a flattery.
   - Proposal: report the pose count behind the in-band beside it.
4. **Auditor misreading (S2).** Hub 2's "71.2 mm ... tens of millimetres above the band" is its fitted level from GH.
   The measured clearance median is 18.07 mm.
5. **Tool reader gap (proposal, not a tightening).** `c_fold_margin` does not read
   `docs/alignment/remeasure/<id>_bench.json` `kin.fold_margin_th_min_taken`. Adding that key to the reader would turn
   this row's fold_margin ok (15.80). On every other row it changes nothing unless the row has a kit re-wear on file.
   Bump VERSION if applied.

**Final verdict: WATCH.**

---

## Skeptic on the 08:45 audit, claim 97.04 (2026-10-18 08:50-09:04 UTC)

Run `skeptic:slotted-eccentric-pin-knee-3r`, rulings in `docs/alignment/slotted-eccentric-pin-knee-3r.rulings.json`
(this replaces the 02:51 rulings on the old claim; those are in git), ledger entry 2026-10-18T09:03:52Z.
**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.** Refuted 2 of 11 (fold_margin, R1);
upheld 9.

**What this skeptic measured (models unchanged):**
- An independent exact wear with a new read-only tool, `tools/alignment_slotted_depthparts.py`. It runs the model's own
  `frozen()`, CB_EXACT=1, niced, 1 process, about 200 s. Output:
  `docs/alignment/remeasure/slotted-eccentric-pin-knee-3r_skeptic_depthparts.json`.
  - Result: 97.04, reach 0.4611, follow 0.6818, ib14 0.699, contact 0.0623. That is the claim to the digit.
  - 16 contact poses, 95.67 mm summed.
- The same tool attributes each press to a part. The model's `extras()` appends the O20 hub-crown minimum to `B.res`
  for a pose whose crown is in the skin; the tool attributes that crown to its hub.

  | press (mm) | pose (plane / elev / axial) | parts inside the skin (mm) |
  |---|---|---|
  | 34.90 | ws 150 / 120 / -180 | hub 3 crown 34.90, L2b 24.61, neck 21.45, hub 3 face 21.37, pinK 0.91 |
  | 10.33 | ws -90 / 60 / 135 | L2b 10.33, neck 0.89, hub 3 0.27 |
  | 7.49, 7.39, 6.55, 5.79, 5.32, 4.09 | ws, planes -15 to 15, elev 60-90 | hub 2 face and crown |
  | 5.02, 3.82, 1.13 | ws, planes -90 to -45, axial 120-135 | L2b |
  | 1.14, 0.65, 0.56 | 2 clip, 1 ws | roller stud G |
  | 1.00, 0.50 | ws | hub 2 |

  - Hub 2 is in 8 of the 16 presses (38.12 mm summed).
  - The J3 end (hub 3, L2b, neck) makes the 34.90 mm press: several parts are 21-35 mm inside the body at once.
- Fold margin, recomputed from the per-pose th with the model's own `a2e_of()` and the kit formula: 12.529 deg on the
  bench (241 taken) and 7.271 held out (255 taken). Both match the dump's `mg` to within 0.001.
  - The track's upper stop at th 125.75 engages at 6.115 deg of th; the lower stop at 62.25 is at 49.33.
- The old claim's dumps (git f804972), the bench-graph flood, and the lead's dumps were re-read. Figures are in the
  rulings below.

**Rulings**

| key | refuted | evidence (short; full text in the rulings file) |
|---|---|---|
| contact_depth | no | Re-derived: 16 / 95.67 mm / deepest 34.90, 10 > 3 mm; held 16 / 55.50 / 13.36. The reference is 4 / 20.24 mm on the same 470-pose bench: x4.73, +75.43, past 2x and 5 mm. Without the deepest pose it is still x3.0. The held x0.91 crosses pose sets (1154 lead vs 470); per pose it is x2.24. |
| continuity | no | No flood for this id: the verify files are the parent's, and the row has no key. The bench-graph bound reproduces (12.50 / 16.11), but it is a bound for the sparse graph only. |
| fold_margin | **yes** | On file: remeasure `kin.fold_margin_th_min_taken` 12.529 / 7.271. Recomputed to 0.001. Above 5.0, and the stops engage at >= 6.1 deg of th. |
| sampling | no | Counts are on file now (part-weighted 0.793 vs 0.699, no thin part). The documented < 0.5 trigger still fires with counts: crank 0.356 (median 14.77 mm), L2b 0.226 (most sampled part, median 16.63 mm). |
| reporting | no | morphs.json sweep_gap 86.82 vs v_gap 97.04 (10.22 > 5). No wear at the 1 mm rule reproduces 86.82; the fit there is 89.42. |
| T5 | no | Old dumps at f804972: 8 presses / 27.78 mm / deepest 9.92 (71 taken). Now 16 / 95.67 / 34.90 (241 taken). Same harness. The mean press went 3.47 -> 5.98 mm. Hub 2 (in-band 0.00 -> 0.86) now presses on 8 poses. |
| T1 | no | Sweep: near = 0 on 1746 of 1763 entries and absent on 17; none is 1. The 1 mm cost on file is 103.66 / 101.62 (6 / 11 poses). |
| G1 | no | Share of taken poses with metal < 1 / 2 / 3 mm: 2.5 / 8.7 / 53.1 % here vs 0.8 / 8.9 / 28.2 % for the lead (held 4.3 / 10.6 / 56.5 vs 1.5 / 8.2 / 25.3). That is 3x the lead at 1 mm and 2x at 3 mm, so the pattern is present. |
| S5 | no | Missing flood. psi min 62.0 / 61.15 (one branch). The size of the loss is unknown. |
| S3 | no | Docstring: member 3 is the kit neck. The 17 sampled groups contain no cuff-knee body. |
| R1 | **yes** | This skeptic's independent exact wear gives 97.04 to the digit (third reproduction; held 93.02 is better). The stale `exact_frozen` / `limiter` describe a worse config (117.68). What remains is labelling, which `reporting` carries. |

**Missed by the auditor (for the next audit; this verdict does not change):**
1. **The held contact-depth comparison crosses pose sets.**
   - The lead's held dump is 1154 poses (952 ws + 202 clip); this design's is held_bench(110,360), 470 poses.
   - Per pose: 55.50 / 470 = 0.118 mm against 60.97 / 1154 = 0.053 mm (x2.24). Scaled to 470 poses, the lead's held
     sum is 24.83 mm, so the excess is +30.67 mm.
   - So "held x0.91" understates; at equal pose counts the held wear also reads clearly deeper.
   - Proposal (a measurement change, not applied): compare depths per pose, or on matched pose sets. On this row it
     turns held from ok to watch and leaves the verdict the same.
2. **The new depth comes from hub 2, lowered into the band.**
   - Hub 2's in-band went 0.00 -> 0.86 between the claims (post lift 0.85 mm).
   - Hub 2's face or crown now presses on 8 of the 16 contact poses, 38.12 mm summed, up to 7.49 mm. These poses are
     at plane -15 to 15 and elevation 60-90 (front raise).
   - This is the T5 trade, and the score cannot see it: the in-band gain is scored and the depth is not.
3. **The 34.90 mm press is a gross intersection, not one sample.**
   - At plane 150, elevation 120, axial -180, the whole J3 end is inside the body: hub 3's crown 34.90, L2b 24.61,
     neck 21.45 and hub 3's face 21.37 mm.
   - The auditor's re-wear could not attribute it; `tools/alignment_slotted_depthparts.py` now does.
4. **The eccentric is saturated on a third of the taken poses.**
   - For th >= 88.8 deg, a2e sits at Amax 81.907 and K at 107.5-108.0 deg: 77 of 241 taken bench poses (87 of 255
     held). There the chain acts as a plain 3R with a2 81.9.
   - 6 of the 16 bench presses, 62.69 of the 95.67 mm (the 34.90 mm one included), are in that saturated range.
   - This is not score gaming. It locates the deep presses where the slot has no authority.
5. **The S5 bench-graph loss is mostly the graph on the held wear.**
   - Held has 0.672 neighbours per cell, and 160 of 360 cells have none, so ">= 16.11" says little about the design.
   - Neither number bounds connected_full. Quote them as graph bounds only.

**Final verdict: WATCH.**
