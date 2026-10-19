# Alignment audit: cam-coupled-4r (groove-slaved 4th hinge)

Audit 2026-10-19 03:02-03:20 UTC (hourly backlog; no earlier ledger entry). The tool is tools/alignment_audit.py
VERSION 2026-10-19.1.
- Checks: docs/alignment/cam-coupled-4r.json. Findings: docs/alignment/cam-coupled-4r.findings.json.
- Re-measures use the model unchanged, through a new adapter, tools/alignment_cam_coupled_probe.py. Neither the audit's
  remeasure nor tools/alignment_kit_rewear.py can wrap this model (no pin-knee audit(), no snap(), no fixed_prof hook).
- Output files:
  - docs/alignment/remeasure/cam-coupled-4r_fast.json (the claim bench)
  - docs/alignment/remeasure/cam-coupled-4r_bench.json (the model's own frozen() worn on Bench(110,360) exact)
  - docs/alignment/remeasure/cam-coupled-4r_k2432_housing.json
- The ledger holds two entries from this audit, 03:12 and 03:20. The second adds the exact wear; it is the one that
  stands.

## Verdict: GAMED (ledger). Claim: gap 50.67, Bench(60,160) fast, status screened

The ledger computes the verdict as the worst of the checks and the findings. The tool's checks alone give **watch**:
- no verified or held-out gap
- no continuity flood or th margin on file
- the idle parser's names do not fit this design
- out-of-band parts (hub 2 0.00, tail 0.00, link 1 0.02)

Two judgement findings are **gamed**:
- **T3: the fold margin is read on another angle.** The J1-J2-J3 dyad sits at its fold on 92 % of the taken poses.
- **S5: static islands.** The claimed reach is a static count. Connected reach is 0.806 against 0.9125 static on the
  claim bench, and 0.719 against 0.797 on the frozen exact wear.

Neither changes the row; the design was already "screened, NOT a contender". The flag means 50.67 is not evidence of a
better exo, and the design cannot be called verified, a winner or a leader until both are resolved.

**The frozen exact wear: 50.67 becomes 65.73** (score 81.6 becomes 76.1):

| | fast (claim bench) | frozen exact |
|---|---|---|
| gap | 50.67 | 65.73 |
| reach | 0.900 | 0.7833 |
| follow | 0.950 | 0.9182 |
| in-band14 | 0.4032 | 0.4041 |
| contact | 0.0099 | 0.0129 |

**Instrument note: T5 (contact depth) reads the same as before.** The 2026-10-19.1 change type-guarded the paired-file
reader. `contact_depth` still reads "not measured" for this design: it reads paired, dump or wear-probe files, and none
exists, before or after this audit. The depths are in this adapter's probe block and are reported below under T5.

## What the wearer gets (measured; frozen Bench(110,360) exact unless stated)

- **Overhead reach (workspace, elev >= 140).**
  - Taken without contact: 6 of 28 (0.214). With contact: 8 of 28.
  - Connected from the rest region: 7 of 28, contact poses included.
  - Overhead clips: 4 of 10.
  - On the claim bench: 4 of 12, connected 4 of 12.
- **Raised arm (elev >= 120).** 21 of 62 workspace poses taken without contact (120-140: 15 of 34; 140-160: 4 of 13;
  160-200: 2 of 15).
- **Metal near the skin.**
  - Taken poses with metal < 1 mm: 9. Under 2 mm: 33. Under 3 mm: 95 (of 383).
  - Overhead: 3 of 6 are under 1 mm, 4 of 6 under 2 mm and 6 of 6 under 3 mm. The minimum metal over all poses is
    0.06 mm.
  - Near-touch is report-only. Counting metal under 1 / 2 / 3 mm as contact gives gaps of 70.55, 86.59 and 135.05.
    Reading the band as 3-14 mm gives 65.93.
- **Deepest contact.**
  - 82.02 mm into the skin at plane 0 / elev 165 / axial 15 (overhead).
  - 29.96 mm at plane 150 / elev 120 / axial -180.
  - Then 2.35, 1.42 and 1.09 mm: 116.8 mm in all over 5 poses. The lead sums 6.23 mm.
- **Workspace in-band (unscored).**
  - Workspace: 0.380 in-band14 (0.202 in-band10). The median metal distance is 18.8 mm, and 62 % of samples sit above
    14 mm.
  - Overhead: 0.638 on the 6 taken poses.
  - By part: hub 1 1.00, neck 0.77, hub 4 0.67, groove flange 0.63, hub 3 0.14, link 3 0.09, link 2 0.03, link 1 0.02,
    hub 2 0.00, tail 0.00.
  - Hubs 2 and 3 ride at 87.8 and 114 mm against hub 1's 49 mm, and every strap stacked on them inherits those levels.
- **Springs.** None.
- **Stops.** None on J2: it is slaved by the groove.
- **Cuff twist.** Not modelled: rigid cuff chain, no spring-held coordinate.
- **Singular postures.**
  - The slaved map's singular distance is 7.27 deg at minimum (p05 27.66).
  - The J1-J2-J3 dyad's th margin is 0.00 deg at minimum and 0.18 deg at the median. J2 runs within about 2-7 deg of
    straight and passes through straight.
  - The J2-J3-J4 dyad margin is 0.97 deg at minimum (the model's clamp is m3 = 0.5).
  - The cam pressure angle is up to 54.5 deg (pa min 0.58), and 48.7 deg at p05.
- **Roller post (checked, no finding).**
  - The post's axis clears link 1's centreline by at least 11.6 deg, which is 15.4 mm at link 1's level (75.7 mm).
    After link 1's 6 mm half-width and the roller's 3 mm radius, at least 6 mm is left.
  - Bending of the 29.8 mm M3 cantilever: an estimate of 0.02-0.06 mm at 5 N (3-4 mm steel shank). That is not a
    feel or tracking problem for the unpowered MVP1.

**Not obtained.**
- **Held-out wear.** The design has no verifier, so there is no held_bench() of its own. Borrowing another family's
  split was not done.
- **Per-part sample counts.** The kit reports fractions only.

## Findings

1. **T3: the fold margin is read on another angle (gamed).**
   - **What the model does.** The row says margin 5. The model never checks th, the J1-J2-J3 dyad's distance from its
     fold, which is the one metric the rule names (tools/concept_kit.py lines 25-30, CLAUDE.md "The fold margin is
     read in ONE metric"). It places J2 by the slot law and clamps the J2-J3-J4 dyad at 0.5 deg. It applies the 5 deg
     to the slaved map's singular distance instead.
   - **Measured.** Fast: 186 of 203 taken poses under 5 deg (min 0.00, median 0.19). Exact: 359 of 388 (min 0.00,
     median 0.18). So 17 and 29 poses survive the rule as written.
   - **Why the exo is not shown better.** The model's own reading may be the right singularity measure for a
     cam-slaved J2. Its minimum is 7.27-8.04 deg, so no wearer-side harm is measured here. But CLAUDE.md rules that a
     different reading is the user's call, not the model's. The same pattern was ruled gamed on
     dipped-law-groove-knuckle-3r.
   - **Action.** Ask the user, as a question, whether a cam-slaved J2's margin may be read on the slaved map. If yes,
     this resolves to ok, and the J3 dyad's 0.5 deg clamp needs its own ruling.
2. **S5: static islands (gamed).**
   - **The rule.** The continuity rule requires a flood for every design with a slaved, sprung or redundant
     coordinate. None is on file.
   - **The flood run here.** kNN-8 edges among the taken workspace poses, a 2 deg slerp, and the model's own build()
     at every step. It accepts a step only if the chain closes, the cam transmits, the map stays non-singular and the
     pin stays in the slot, and no joint value or axis jumps more than 10 deg.
   - **Measured.**
     - Claim bench: 129 of 146 connect. Connected reach is 0.806 against 0.9125 static, about +9.4 to +10.6 gap.
     - Exact: 259 of 287 connect. Connected reach is 0.719 against 0.797 static, +7.8 gap, so the connected exact gap
       is about 73.5.
     - The results are identical at the kit's 25 deg jump.
   - **Why the exo is not better.** The wearer cannot reach 17-28 of the poses the score counts without resetting the
     mechanism by hand. The pose-local choice among several pin-in-slot roots on two J3-dyad branches is what makes the
     islands.
3. **T5: deep contact (watch).** One overhead pose has metal 82 mm into the arm, and the sum over 5 poses is 116.8 mm.
   The contact term counts them as 1.29 % of poses whatever the depth. A verifier should attribute the 82 mm pose to a
   member.
4. **G1: metal hugging the skin (watch, report-only).** Every taken overhead pose has metal under 3 mm, and 20.86
   points live in the 1-2 mm shell. On a real, bulging arm, this overhead reach is skin contact.
5. **NEW-hinge: the number is parked on the hinges (watch).**
   - **Measured.** All 25 best honest CMA configurations sit at reach 0.900 and follow 0.950 exactly. The frozen exact
     wear's +15.06 is 14.85 points of hinge: reach falls to 0.783 (+11.67) and follow to 0.918 (+3.18). In-band does
     not move (0.4032 to 0.4041).
   - **Why.** The score gives nothing above the targets, and in-band reads only the taken clip frames. So the search
     drops exactly the poses that cost in-band and keeps no slack.
   - **Proposed catalogue entry T6 "Parked on the hinge".**
     - Looks like: a claim at reach = 0.90 and / or follow = 0.95 to the third decimal across the top of its search.
     - Why not better: the dropped poses are motions the exo cannot follow, and any new bench costs full points.
     - Detect: report each claim's slack above the reach and follow targets, and its fast-to-frozen drop split by
       term.
     - Here: cam-coupled-4r, top 25 of cma2. 14.85 of its 15.06 drop is hinge.
6. **NEW-cam-pressure: the cam may bind (watch).**
   - **Measured.** The model accepts pressure angles up to 75.5 deg (pa_min 0.25). On taken poses the angle reaches
     54.5 deg, and is above 45 deg on at least 5 %.
   - **Why the exo is not better.** In the unpowered MVP1 the arm pushes J2 through the groove, and the bench prices
     neither friction nor stick at those angles.
   - **Proposed catalogue entry G7 "Cam / groove pressure angle".**
     - Detect: the taken poses' pressure-angle distribution against 45 deg.
7. **R2: the dashboard shows a refuted configuration (watch).**
   - **What it shows.** The dashboard's sweep_* fields for this row (reach 0.79, follow 1.0, in-band14 0.51) come from
     k 2432. That configuration ties 50.67 and was measured earlier, but it belongs to the CMA stage without the
     housing rule: its groove's inner edge is -3.7 mm from J1's axis.
   - **Measured.** Re-run under the housing rule (model unchanged): 196.65. The gap shown is the same and no rank
     moves; the components are wrong.
8. **P1: in-sample only (watch).** 50.67 is the search bench's best of 4116 honest tries (top 20 span 50.67-50.94).
   Frozen exact it is 65.73 (+15.06); there is no held-out wear.
9. **G6: '3 active' on a 4-joint chain (watch).** The mobility is 3 with J2 slaved, but the metal is 4 O20 hub stacks
   plus a closed loop. The complexity count (11.75) prices this; the active_dof column groups the design with the
   3-joint designs.

**Instrument note: the tool's idle check misreads the declarations.** It lists "K" and "crank" as declared moving.
This design has neither, so the declared-drive parser read names from another family (proposal 3 below).

## Proposals (measurement or reporting changes; not inputs to the verdict)

1. **th, or a ruled substitute, for slaved 4R chains.** Every chain with a J1-J2-J3 dyad reports the th margin over
   its taken poses, or cites the user's ruling for a substitute (here: the slaved map's singular distance).
   - Effect on the verified rows: none. They are knuckle and 3R chains that already report th: 5.006-5.181 on the
     leaders.
   - Effect here: 17 of 203 (fast) and 29 of 388 (exact) poses survive th >= 5.
2. **Refuted sweep stages do not count as a best.** tools/dash_build.py ignores a sweep stage that a red team refuted
   (a row field such as refuted_stages) when it picks the sweep best.
   - Effect: this row's sweep_* fields change to k 9706 (reach 0.90, follow 0.95, in-band14 0.403). No verified row
     changes: their numbers come from v_* fields.
3. **The idle check reads declared drives from the row's own mechanism record** (passive_rot, sliding_pairs), not from
   family names. Effect: removes this row's spurious "K / crank" watch; no verified row changes.
4. **A pressure-angle cutoff for cam and groove couplings.** Taken poses keep pa >= 0.707 (45 deg).
   - Effect: not measured on the verified rows. Groove designs such as dipped-law-groove need their own re-run.
5. **contact_depth reads remeasure files that reproduce their own gap.** It would also read a remeasure file's
   `probe.contact_poses` when that file's `fit_fast` reproduces the claim. Effect here: T5 would read 116.8 mm sum /
   82.0 mm max (exact). The effect on verified rows is not measured; their dumps already take priority.

## Next

The design stays not a contender. A re-claim reports 65.73 frozen exact, the connected reach and a held-out wear, and
needs the user's ruling on T3.

## Skeptic (2026-10-19 04:07 UTC): final verdict GAMED

The skeptic re-measured the claim, with the model unchanged, on Bench(60,160) fast, the row's claim bench (50.67
reproduced: reach 0.90, follow 0.95, in-band14 0.4032, contact 0.0099, honest). It added three controls to the flood:
kNN-16, every edge allowed, and no jump test. It also counted the samples on each part, re-scored k 2432, and read the
auditor's frozen exact files. Raw output: `docs/alignment/remeasure/cam-coupled-4r_skeptic_fast.json`. Rulings:
`docs/alignment/cam-coupled-4r.rulings.json`. Ledger: `python3 tools/alignment_ledger.py get cam-coupled-4r`.

**Refuted (1):**

- **idle**: a parser false positive. `_declared_joints` (tools/alignment_audit.py line 575) declares a K and a crank
  when the name matches 'cam'. This design has neither. Its one slaved coordinate, J2, moves:
  - over the 203 taken poses (mod 360) it runs from 159.7 to 289.4 deg, a span of 129.8 deg (p05-p95: 99.5 deg);
  - J1 spans 324.6 deg;
  - TH idle_deg is 2.0.

  The probe's J2_span 359.6 is a wrap artefact.

**Upheld (13):**

- **held_out**: nothing is on file.
- **continuity**, **fold_margin**: the measurements are now on file, and they are worse than the missing record (see
  S5 and T3).
- **sampling**: the missing counts are now measured.
  - Samples per part: hubs 81 each, slot 776, link1 140, tail 161, link2 245, link3 203, neck 224.
  - Sample-weighted in-band is 0.403 against 0.334 part-weighted: +6.93 points, over TH part_weight_watch 3 and under
    gamed 8.
- **T3**, independent re-measure. th margin is min 0.000 and median 0.193, with 186 of 203 taken poses under 5.
  - J2 sits a median 7.0 deg from straight and passes through it (min 0.015).
  - The J2-J3-J4 dyad has min 0.796, with 3 poses under 5, so neither dyad keeps the 5 deg.
  - The verified 4R reads every dyad (freek-oracle polish-verify member_margins, 5.59 on file).
  - The model's own reading holds (sing min 8.04). With J2 cam-held, the J1-J2-J3 fold is not a singularity of the
    actuated map, so no cost to the wearer is shown. The reading is still the user's call (CLAUDE.md).
- **S5**: kNN-8 and kNN-16 both connect 129 of 146 poses.
  - It is not a graph artefact: with every edge allowed, 146 of 146 connect; with no jump test, 145.
  - The loss is branch switches. Example: (-15,45,15) to (0,30,0), where in one 2 deg step J1 jumps 99.5 deg, the
    passive J2 jumps 58.8 deg and the J3-dyad branch changes.
  - The lost island at elev 90-105, planes 0-75, is smooth inside (jumps <= 3.5 deg) but cut off from the seeds.
  - Connected ws reach is 0.806 against 0.9125 static: +9.4 to +10.6, over conn_gamed 3.
- **T5**, with a correction. 6.23 mm is sidecar-longdyad's depth (RULINGS_DEPTH_REF), not the lead's.
  - The current lead, conecut-knee-knuckle-3r, reads 20.24 mm over 4 poses on the same bench (tool 2026-10-19.1).
  - Corrected: 116.84 against 20.24 mm, x5.77 and +96.6 mm. That is still a watch.
  - Instrument: at 2026-10-19.1 this row's contact_depth still reads "not measured", so T5 reads the same here. Only
    the reference's reading changed (it is no longer vacuous).
- **G1**: the numbers reproduce. Near-touch is report-only, so it stays a watch.
- **NEW-hinge**: 24 of the 26 lowest honest gaps sit at exactly reach 0.900 / follow 0.950 (2 at reach 0.906). Of the
  38 verified / cad rows, 0 sit on both hinges, so the pattern belongs to this row. It overlaps P1.
- **NEW-cam-pressure**: the pressure angle reaches 54.1 deg at most, and its 95th percentile is 47.9 deg. The 45 deg
  limit is not in TH, so this is a watch and a proposal, not a gate.
- **R2**: re-scored k 2432 under the unchanged model: 196.65 (groove inner edge -3.7 mm).
- **P1**: the frozen exact wear adds +15.06, over ff_watch 14.
- **G6**: the facts hold: 4 O20 hubs, and track K1 counts a slaved spherical 4R as 4 joints.
  - Context: the 3-joint lead is also active_dof 3, with a slaved knuckle (8 joints, 3 loops, complexity 18.5).
  - Which count applies to a slaved, GH-centred serial joint is the user's call.

**Missed by the audit** (for the next audit; it does not change this verdict):

1. **The S-fixed groove flange carries the in-band.** The slot plate is 776 of 2073 samples (37 %), at 0.63 in band.
   - Without it, the design's in-band14 is 0.266, not 0.403: the plate buys 13.7 points of the claim.
   - The moving chain sits 0.00-0.15 in band: hubs 2-3, links 1-3 and the tail (911 samples, 44 %). The arm-side
     links ride mostly over 14 mm.
   - The plate is real metal, so this is not dishonest. But the headline in-band describes the scapula flange, not the
     linkage the wearer moves. Proposal: report in-band split into the moving chain and the S-fixed parts.
2. **The T5 reference was mis-cited** (6.23 mm is sidecar-longdyad's). The corrected comparison is above.
3. **The model docstring overstates its continuity guard.** It says K2 dense continuity "drops any frame where this rule
   would switch roots". That holds for clip frames only. The workspace poses, which carry reach, have no guard, and
   that is where S5's ~100 deg root switches sit.

**Final verdict (ledger): GAMED** (T3, S5 upheld).
