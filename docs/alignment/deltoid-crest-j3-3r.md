# Alignment audit: deltoid-crest-j3-3r

Auditor pass 2026-10-18, discovery round 102 slice r102-A (the design was screened and verified this round).
Tool: `tools/alignment_audit.py` VERSION 2026-10-17.6, reference `conecut-knee-knuckle-3r` (the verified 3-active lead,
18.28). Ledger entry: `python3 tools/alignment_ledger.py get deltoid-crest-j3-3r`.

## Verdict and claim

**Verdict: WATCH** (ledger). The claim is the verified frozen gap **v_gap 47.86** (score 82.60) on Bench(110,360)
exact, frozen shape (fit Bench(60,160) fast). The row headline is the fast best, 36.63. Both the verifier's per-pose
dump and this audit's own re-wear reproduce the claim exactly: 47.86 bench, 50.05 held (see "Re-measured").
The tool's checks are all ok except `reporting` (the dashboard's sweep best). Nothing here moves the claim. The number is
honest as a plain gap. What it does not say is that every overhead pose it credits has metal on the skin, and that its
held-out check is partly in-sample. The design is dead on its own kill bar (j3-neck-over-3r 32.10 frozen) and 29.6
points behind the lead, so no ranking that matters rests on it.

## What the wearer gets (measured)

Sources: the verifier's per-pose dumps `docs/alignment/remeasure/deltoid-crest-j3-3r_{bench,held}_perpose.json`
(their gaps recompute to 47.87 / 50.05), and this audit's re-wear and flood files listed under "Re-measured".

- **Overhead reach: 4 / 28** workspace poses at elev >= 140 on the bench, 4 / 26 held. The raised-arm clip frames
  give 6 / 10. The losses are 15 / 28 to the stretched J2 fold, 4 to part-part clashes and 5 to contact.
- **Every overhead pose it takes touches.** The lowest metal on the 4 bench overhead workspace poses is 0.13, 0.84,
  1.20 and 1.34 mm. Held, it is 0.07, 0.34, 0.39 and 0.66 mm. On the 6 overhead clip frames it is 0.66-1.28 mm. No
  overhead pose has 2 mm of clearance.
- **Raised-arm reach by elevation (bench ws taken / total):** 0-60: 145 / 172; 60-90: 30 / 75; 90-120: 20 / 51;
  120-140: 8 / 34; 140-160: 4 / 13; 160-200: 0 / 15.
- **Taken poses with metal < 2 mm:** 58 of 305 on the bench (21 clip, 37 ws). Held: 55 of 303. Below 1 mm: 22 / 22.
  Below 3 mm: 101 / 95.
- **Contact:** 20 bench poses, summed depth 26.4 mm, deepest 3.26 mm at ws (15, 150, -30); 9 of the 20 are overhead.
  Held: 22 poses, summed 42.84 mm, with two deep overhead presses: **10.51 mm at (30, 165, -15)** and **9.24 mm at
  (0, 150, -30)**. The score counts poses, not depth (T5). Against the lead this stays under the tool's watch line
  (x1.3 bench, x0.7 held).
- **Workspace in-band:** the scored clip in-band14 is 0.867. Per member (row `frozen_exact.inband_member`): hub1 0.986,
  hub2 0.999, hub3 0.905, link2 0.975, **link1 0.674**, neck 0.828. Part-weighted that is 0.894 against 0.867
  sample-weighted, so sparse sampling does not inflate it (S2 ok). Every declared body is sampled (S3 ok). The unscored
  workspace in-band is **0.813** on the bench (in-band10 0.450) and 0.799 held. 17.8 % of the
  workspace metal samples sit beyond 14 mm, 1.0 % beyond 20 mm, max 28.6 mm. Overhead workspace: 0.786 bench and
  0.694 held, with 20-26 % beyond 14 mm. So the workspace the score does not read carries metal further out than the scored clips (0.870).
- **Springs / stops / cuff twist:** none. This is a plain spherical 3R with three active pins on MR117 pairs at O20,
  0 passive joints, complexity 0 (recomputed 0). There is no spring and no cuff knee, so nothing can twist the cuff.
  The only stop is the J2 fold at the 5-deg margin.
- **Near-singular postures:** the taken poses run up the stretched fold. th spans 23.2-76.3 deg on the bench against
  a stretched limit of a1 + a2 = 82.8 deg. The minimum margin is **6.46 deg** on the bench and **5.31 deg** held, both
  inside the 5-deg rule, both near it. Reproduced by `tools/alignment_kit_flood.py`: 6.462 / 5.313.
- **Continuity:** a kNN-8 flood over the TAKEN workspace poses (the verifier's own `extras()`, 2-deg slerp, 5-deg
  margin, axis step <= 10 deg) connects **207 / 207 on the bench and 207 / 207 held**: no islands
  (`docs/alignment/remeasure/deltoid-crest-j3-3r_{bench,held}_flood.json`). The row's "263 / 263" was a count of
  closing poses with no file on record. This file confirms it on the taken set.

## Re-measured (this audit)

- `tools/alignment_audit.py remeasure` and `tools/alignment_paired.py dump` cannot wrap this kit model: it has no
  pin-knee-style `audit(M, B)`. A new adapter, `tools/alignment_kit_rewear.py`, runs the model file unchanged:
  `snap()` and `evaluate()`, fit Bench(60,160) fast frozen, worn exact. It reads the worn bench with the audit's own
  `deep_audit` and `alignment_wear_probe.analyse`.
  Bench (`docs/alignment/remeasure/deltoid-crest-j3-3r_bench.json`, 323 s): **47.86**, reproduced exactly. Near-touch
  is 64.84 / 95.56 / 122.84 at 1 / 2 / 3 mm (22 / 58 / 101 poses). With the band read as 3-14 mm the gap is 49.44
  (+1.58). Clip metal histogram: 0-2 mm 0.54 %, 2-3 mm 1.58 %, > 14 mm 12.8 %.
  Held (`docs/alignment/remeasure/deltoid-crest-j3-3r_held.json`, 452 s): the fit reproduces 36.63 fast and the
  held wear gives **50.05** (reach 0.575, follow 0.873, ib14 0.870, contact 0.068). That independently reproduces the
  verifier's held 50.05. Near-touch is 66.52 / 92.72 / 120.43 at 1 / 2 / 3 mm (22 / 55 / 95 poses). With the band
  read as 3-14 mm the gap is 51.36. Clip metal histogram: 0-2 mm 0.28 %, 2-3 mm 1.31 %, > 14 mm 12.8 %.
- `tools/alignment_kit_flood.py` (new) runs the verifier's `extras()` unchanged on the per-pose dumps. The flood is
  kinematic, so no skin is re-evaluated. Results are above. It checks the pose order against the rebuilt bench and
  reproduces the th margins.
- `docs/alignment/remeasure/deltoid-crest-j3-3r_heldleak_check.json` measures how far the held set overlaps the
  search bench (finding P2).
- Near-touch from the dumps, using `deep_audit`'s rule (taken poses below the threshold count as contact):

| wear | plain | < 1 mm | < 2 mm | < 3 mm | poses < 1 / 2 / 3 mm |
|---|---|---|---|---|---|
| bench | 47.87 | 64.85 | 95.55 | 122.83 | 22 / 58 / 101 of 305 |
| held | 50.05 | 66.52 | 92.73 | 120.42 | 22 / 55 / 95 of 303 |
| lead conecut (bench) | 18.28 | 19.92 | 34.84 | 86.16 | 3 / 33 / 105 of 372 |

The < 1 mm column equals the model's own all-faces near-touch reading (64.84 / 66.52), so the dumps' `min_mm` already
includes the top faces.

## Findings

1. **T1, watch: metal parked just past the 0 mm cutoff, from a plain-gap search.** The zc-frontier family's
   `evaluate()` returns the verifier's plain gap as the objective (`docs/concepts/models/zc-frontier-3r.py` lines 128
   and 145-149). CLAUDE.md says every search objective is the near-touch gap, so the 3780-evaluation CMA optimised
   the wrong number. 17 points of the claim live in the 0-1 mm shell (22 taken poses) and 47.7 in the 0-2 mm shell.
   The lead has 1.64 and 16.56. *Why the exo is not better:* a pose taken at 0.1-1 mm on the model is metal on a real,
   bulging arm. *Action:* the next search on this family should use the near-touch objective, or report the
   difference it would make. Not gamed: near-touch is report-only (user, 2026-10-17), and no verified row sits
   between 47.86 plain and 64.85 near-touch, so no better design is outranked.
2. **G1, watch: overhead reach is all metal-on-skin.** All 10 overhead poses the bench credits (4 ws, 6 clip) have
   metal within 1.4 mm. Held, all 4 ws are within 0.7 mm. At 1 mm, overhead reach is 2 / 28 on the bench and 0 / 26
   held. The other overhead poses are lost to the fold (15), pressed into the skin (9 bench, 11 held, up to 10.5 mm
   held), or lost to clashes. *Why the exo is not better:* "overhead most of all, never touching" gets no clearance
   at all here. *Action:* report the overhead clearance floor beside "overhead taken / 28" (proposal 2).
3. **P2, watch: the held-out set is partly the search sample.** `held_bench(110,360)` excludes Bench(110,360) but not
   the Bench(60,160) poses the CMA searched on and the frozen levels were fit on. 60 of the 470 held poses are search
   poses by index (40 ws, 20 clip), and 12 more clip frames have a pose vector identical to a search frame. The frozen
   shape takes 45 of the 60 (75 %, against 57.5 % reach overall) with 0 contacts. On the poses the search never saw,
   the held gap is **51.08** (pose-vector match, 398 poses) to **53.98** (index match, 410 poses). That is +3.22 to
   +6.12 over the bench 47.86, where +2.19 is reported (50.05). The index reading crosses the held_watch line of 6.0.
   The leaders' 1154-pose held sets share only 30 poses with Bench(60,160), and removing them moves their held gaps
   by -0.64..+0.09 (`docs/alignment/remeasure/heldleak_fit60_all.json`). So this pattern matters for the small
   470-pose verifier held sets, not for the leaders. *Why the exo is not better:* the held number is partly
   in-sample and reads 1-4 points kind. *Action:* proposal 1.
4. **R2, watch: the dashboard shows a number the design does not hold.** `morphs.json` shows sweep_gap **26.78**
   (score 90.26, reach 0.70). That is the best of 3780 fast evaluations. Its own frozen exact is **40.17** (score
   85.39, `docs/concepts/verify/deltoid-crest-j3-3r_skeptic_frozen_s10.json`), 13.39 worse, with 6 static islands and
   a **23.42 mm** press at (0, 165, +15). The row headline 36.63 / reach 0.65 is fast too (+11.23 to the verified
   number). The fast-to-frozen penalty is 11-14 points at every best. *Why the exo is not better:* a reader sees a
   ~90 score for a shape that wears at 85. *Action:* proposal 3.
5. **NEW-plain3r-islands, watch: plain 3Rs are exempt from the continuity flood, but they can take islands.** The s10
   config (the dashboard's sweep number) takes 6 workspace poses at elev 90 that no continuous path from rest reaches
   at the 5-deg margin. That is 1.67 reach points that exist only statically. The claimed config is clean: 207 / 207
   on both wears. *Why the exo is not better:* the wearer cannot raise the arm into a pose the fold stop walls off.
   *Action:* proposal 4 and catalogue entry S6 below.

Patterns walked and found absent or ok, with their numbers:
- **T2 (band edge):** reading the band as 3-14 mm costs +1.58 on the bench (47.86 -> 49.44) and +1.31 held. Only
  1.3-1.6 % of clip samples sit at 2-3 mm. No crowding at the band edge.
- **T3:** th is read on the right angle; the minimum is 6.46 bench / 5.31 held.
- **T4:** no self-set window bound; the best params sit inside the crest box (a1 38.7 of 34-64, wd 103.4 of 95-120,
  el 63.1 of 48-80, q 0.94 of 0.85-1).
- **T5:** depth stays under the tool's line against the lead, but the deep held presses are listed above.
- **S1 / P1:** the bench-to-held drop is +2.19 as reported, and +3.22 to +6.12 on unseen poses (see P2).
  Fast-to-frozen is +11.23.
- **S2 / S3:** ok, see in-band above.
- **S4:** not automatic; nothing specific to this design.
- **S5:** the claim has no islands (see NEW above).
- **M1 / M2:** O20 at all three hubs, 12 x 3 Ti links, 0 passive translations.
- **M3:** part-part is checked (43 ws poses lost to it). The cap-plate binders are named in the row.
- **M4:** three active pins, all moving. th spans 23-76 deg.
- **M5 / G2 / G3:** no spring, no knee.
- **P3 / R3:** the claim is the frozen wear of the fast best. The two best configs freeze to 47.86 / 47.88, so the
  claim is not a lucky re-wear. The dashboard's sweep best has no spread (R2).
- **P4:** no bench, judge or metric file is in the row's 5 commits.
- **R1:** status "verified" matches the verifier files.
- **R4:** v_gap 47.86 shown as measured, v_contact present.
- **G4:** margin 5.31-6.46 deg on the stretched side, inside the rule.
- **G5 / G6:** complexity 0, recomputed.

## What I could not get, and why

- Per-part sample counts. The re-wear records per-member in-band fractions (`parts_ib14`), not sample counts, so the
  under-16-samples test of S2 has fractions only.
- Tool readings that miss data on file. Before this audit's re-wears landed, the audit tool reported "no held-out
  measurement on file", "no near-touch measurement on file" and "no per-part in-band record" for this row. All three
  were on file: `verification.held.gap` 50.05, `verification.near_touch_gap` / `frozen_exact.near_touch_gap` 64.84,
  and `frozen_exact.inband_member`. The checks read other spellings. The re-wear files now close all three, and the
  second audit run reads them (the checks are ok). The reading itself is proposal 5. I did not edit the tool.
- The farm is closed: the approval window ended 2026-10-17 ~17:20 UTC. Everything ran locally, niced, with at most 2
  processes.

## Proposals (measurement or reporting changes; not applied, not inputs to the verdict)

1. **Held set disjoint from the search bench.** `held_bench()` (`tools/osn_polish.py`, and the verifier copies of it)
   should also exclude `CB._select(60,160)`, by pose vector, not only by index. Measured effect here: held 50.05 ->
   51.08 to 53.98. Measured on every held per-pose dump on file (coordinate match,
   `docs/alignment/remeasure/heldleak_fit60_all.json`): the 15 other rows (the knuckle family on 1154-pose held sets)
   share 30 poses each, and their held gaps move by -0.64..+0.09. No verified ranking changes.
2. **Overhead clearance floor.** Report it beside "overhead taken / 28": overhead poses taken with metal >= 2 mm.
   Here 0 / 28 bench and 0 / 26 held, against 4 / 28 and 4 / 26 credited. Report only, no score change.
3. **Dashboard sweep lines carry their frozen number.** Show sweep_gap with a "fast, not verified" label, plus the
   frozen exact of that config when one is on file. Here 26.78 -> 40.17.
4. **Continuity for plain 3Rs.** Run the kNN-8 flood on every claim whose taken set comes within 10 deg of the fold
   margin, plain 3Rs included. Measured cost: 2-3 s per wear from the per-pose dump (`tools/alignment_kit_flood.py`).
   Effect here: 0 on the claim; -1.67 reach points on the s10 config.
5. **Audit tool readings.** `c_held_out` should read `<id>_held_perpose.json` `frozen.gap` and
   `row.verification.held.gap`. `_near_numbers` should read `row.verification.near_touch_gap` and
   `row.frozen_exact.near_touch_gap`. `c_sampling` should read `row.frozen_exact.inband_member`. That is an
   instrument change: bump VERSION and re-run the selftest.

### Proposed catalogue entry

**S6. Static islands behind the fold of a plain chain.** *Looks like:* a plain 3R (no passive coordinate) whose search
pushes it against the dyad's stretched or folded limit takes static poses beyond a band of fold losses. *Why not
better:* moving from rest, the arm reaches the fold stop before it reaches those poses, so the wearer can never hold
them. *Detect:* the kNN-8 continuity flood over the taken poses (the verifier's `extras()`; for kit models,
`tools/alignment_kit_flood.py` on the per-pose dump), whatever the passive count. *Here:* deltoid-crest-j3-3r's s10
config, 26.78 fast / 40.17 frozen: 6 islands at elev 90, connected reach 0.589 against 0.606 static.

## Skeptic (2026-10-18)

Re-measured from the per-pose dumps, the verifier files and the tool code. The models are unchanged. Everything ran
locally, niced, with at most 2 processes. Rulings: `docs/alignment/deltoid-crest-j3-3r.rulings.json`. New measurements:
`docs/alignment/remeasure/deltoid-crest-j3-3r_skeptic_checks.json`.

**Final verdict (ledger): WATCH.** 4 reasons upheld (reporting, T1, G1, R2) and 2 refuted with measurements (P2, NEW-plain3r-islands).

- **reporting: upheld.** `morphs.json` shows sweep_gap 26.78 against v_gap 47.86, a spread of 21.08. That is past the
  5-point trigger (`c_reporting`, line 715), and 26.78 reads as a score of 90.26. The minimum of the sweep file is k 3581
  (cma-s10). The page labels the number "Sweep best gap" (`bench.js:131`), so this is a label watch. Of the 20 verified
  rows with this pattern, this one has the largest spread (next: spine-parked 12.51, minarc 12.21).
- **T1: upheld.** The CMA objective is `r["gap"]` (`tools/concept_cma.py:55`), which is the verifier's plain gap
  (`zc-frontier-3r.py:145-149`). My recompute from the dumps gives bench 47.86 / 64.84 / 95.56 / 122.84 (22 / 58 / 101
  poses) and held 50.05 / 66.52 / 92.72 / 120.43. The lead's shells are 1.64 / 16.56; this design's are 16.98 / 47.70.
  The search is still running on the plain objective: the uncommitted cma-s12 / s13 rows (5666 in the sweep file now)
  have best 29.38 plain against 44.5 near-touch, and the 26.78 rows sit at 50-51 near-touch.
- **G1: upheld.** The numbers re-derive exactly: overhead ws on the bench is 0.13 / 0.84 / 1.20 / 1.34 mm, overhead
  clip 0.66-1.28 mm, held ws 0.07-0.66 mm, with 9 / 20 and 11 / 22 overhead contacts and held presses of 10.51 and
  9.24 mm. One caveat: the 5 held overhead clip readings equal the bench's to 0.01 mm because they are the same frames
  (see missed 1), so only the held ws readings are independent.
- **P2: refuted.** The watch rests on the held_watch line, and that line was applied to a reading that still contains
  in-sample frames. The index reading (53.98, 410 poses) keeps 12 frames whose 5-D pose equals a search frame. The
  pose-vector reading removes everything the search saw, which leaves 398 poses at 51.09, +3.23 over the bench and
  under the 6.0 line. If I also remove the 32 held clip frames that are identical to claim-bench frames, 383 poses
  remain at **49.40, +1.54**, which is below the reported +2.19. The overlap is real, but it does not flatter this row's
  held number.
- **R2: upheld on its main number.** Fit 26.78 fast, worn frozen exact 40.17: 13.39 worse, with a -23.42 mm press at
  (0, 165, 15). The "6 static islands" sub-claim does not stand (next ruling). Side fact: this better config wears 40.17,
  but the claim stays at the older 47.86 config. That understates the design and is not gaming.
- **NEW-plain3r-islands: refuted.** I re-ran `tools/alignment_kit_flood.py` unchanged on the s10 wear and got the same 6
  islands. They are an artifact of the flood's edge direction. `extras()` expands only from a connected node `a` to
  `knn(a)`. None of the 6 islands is in the kNN-8 of any connected node, yet each island's own kNN-8 holds 3-6
  connected nodes. Run on those pairs, the verifier's own edge test passes: closure 1.0 at every 2-degree step and a
  maximum axis step of 0.65-1.96 deg (for example (0,90,45) <-> (15,60,60), 38.2 deg apart). For each island, 30-40 of
  its 40 nearest connected poses pass. With symmetric edges the s10 config has 0 islands and loses 0 reach points.
  The claimed config re-floods at 207 / 207 on the held set, with a th margin of 5.313.

### Missed (for the next audit; not counted in this verdict)

1. **The held set overlaps the CLAIM bench by content.** `held_bench(110,360)` excludes Bench(110,360) by index only.
   32 of its 110 clip frames have 5-D pose vectors identical to Bench(110,360) clip frames: 27 taken, 2 contacts. That
   includes all 5 held overhead clip frames (0.66 x3, 0.70, 0.81 mm, the same as the bench). The held set also holds
   13 internal duplicate vectors. So the "held" overhead clip evidence, and part of the held follow, repeat the bench.
   Removing these frames moves this row's held gap by -3.81 (to 46.24). Proposal: `held_bench` should exclude by pose
   vector against both Bench(110,360) and Bench(60,160), and de-duplicate itself. Its effect on the other rows should
   be measured the way `heldleak_fit60_all.json` was.
2. **The search keeps optimising the plain gap.** In the working tree, 1886 new cma-s12 / s13 rows were written after
   the audit, on the same plain objective (best 29.38 plain against 44.5 near-touch). A new best from them would carry
   T1 forward. The next audit of this row should check the phase of the claimed config.
3. **Instrument note (not gaming; it reads harsher, not kinder):** the verifier's continuity flood (`extras()` kNN-8,
   copied into other verifiers and run by `tools/alignment_kit_flood.py`) is directed. A taken pose whose nearest
   connected neighbour has 8 closer taken poses reads as an island even when a valid 2-degree slerp edge exists.
   Island counts on other rows (S5 findings, connected-reach claims) should be re-read with symmetric edges
   (`edge(a, b)` for b in knn(a) or a in knn(b)). Measured here: 6 -> 0.

Verdict printed by `tools/alignment_ledger.py skeptic`: **watch**.
