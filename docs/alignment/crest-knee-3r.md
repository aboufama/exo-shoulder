# Alignment audit: crest-knee-3r

Audit 2026-10-18 (round 14, slice r14-A), tool VERSION 2026-10-17.6, reference conecut-knee-knuckle-3r (the verified
3-active lead). Ledger entry 2026-10-18T02:27:16Z (`python3 tools/alignment_ledger.py get crest-knee-3r`).

## Verdict: WATCH (claim v_gap 32.84, score 88.06)

The number is honest. The audit wore the frozen claim again through the model, unchanged, and got the same result to the
digit: Bench(110,360) exact 32.84 and held out 29.81 (`docs/alignment/remeasure/crest-knee-3r_bench.json`,
`_held.json`). Nothing in the number ranks this design above a design that is better for the wearer. It is 5.64
points behind H1 (skin-normal-3r-pin-knee, 27.20) and 14.56 behind the lead (18.28). It is also behind both of them at
the 2 mm near-touch reading (57.98 vs 46.85 and 34.84). The watch comes from four things:

- metal sits at 1-2 mm overhead (G1);
- workspace standoff the score does not read (NEW-ws-inband);
- a held set that holds 60 of the search poses (P2);
- the dashboard still shows the fast 26.34 (R2, plus the tool's `reporting` check).

The tool's `continuity` watch is a false positive: it does not find the verifier's flood record (see Proposals).

| check | level | measured |
|---|---|---|
| held_out | ok | held 29.81 vs bench 32.84 (-3.03, re-measured) |
| fast_frozen | ok | fast 26.34 -> verified 32.84 (+6.50) |
| near_touch | ok (report-only) | plain 32.84, < 1 mm 36.25, < 2 mm 57.98, < 3 mm 93.37, band 3-14 mm 35.30 |
| contact_depth | ok | bench 5 poses, sum 6.40 mm, deepest 2.77 mm; held 6 poses, sum 4.80 mm, deepest 1.63 mm; lead 20.24 / 60.97 mm |
| dominance | ok | vs the lead: plain -14.56, 2 mm -23.14 |
| continuity | watch (tool reading gap) | the verifier's flood is on file: 1432-pose grid, 959 / 959 connected, 0 islands, 0 bench / 0 held poses dropped |
| fold_margin | ok | min th 6.23 deg bench, 5.33 deg held |
| idle | ok | knee angle span 21.15 deg (80.23-101.38) |
| sampling | ok | sample-weighted in-band 0.853 vs part-weighted 0.865 |
| complexity | ok | 0.0 recomputed (simplicity v2.2, unsensed two-pin cuff knee 0) |
| reporting | watch | the row's verdict text is still the screen's; the dashboard shows 26.34 |
| judge_change | ok | no bench, judge or metric file in the row's 3 commits |
| rules | ok | O20, fold margin >= 5, 0 passive translations, 3 active DOF |

## What the wearer gets (measured, frozen claim)

Numbers are for Bench(110,360) exact, with held out in brackets. Files: `remeasure/crest-knee-3r_{bench,held}_probe.json`
and `_perpose.json`.

- **Overhead (workspace, elevation >= 140):** the claim takes 5 of 28 (held 6 of 26).
  - Lost poses: 11 to the fold, 9 to the J3 stop, 3 to contact.
  - Clearance of the taken poses: 0.59, 0.96, 1.23, 1.72 and 2.10 mm (held 0.02, 0.18, 0.59, 0.85, 1.11 and 1.45 mm).
  - All 10 Raise-overhead clip frames are taken, at 1.08-1.85 mm.
  - So overhead the wearer has no pose with 2 mm of clearance, except one pose at 2.10 mm.
- **Raised arm (workspace, elevation >= 90):** 32 of 113 (35 of 112). H1 gets the same 32 of 113; the lead gets 47.
- **Reach by elevation (bench):**

  | elevation (deg) | taken |
  |---|---|
  | 0-60 | 156 / 172 |
  | 60-90 | 40 / 75 |
  | 90-120 | 16 / 51 |
  | 120-140 | 11 / 34 |
  | 140-160 | 4 / 13 |
  | 160-200 | 1 / 15 |

- **Large axial rotation (|axial| >= 150):** 5 of 27 workspace poses (9 of 29). All 22 lost bench poses go to the fold.
- **Taken poses with metal close to the skin:** 6 under 1 mm, 34 under 2 mm (15 clip, 19 workspace), 77 under 3 mm
  (held 10, 34, 83). H1 has 8, 27 and 92; the lead has 3, 33 and 105.
- **Contact:** 5 poses (held 6). The deepest is 2.77 mm at plane 75 / elev 90 / axial 15 and 2.67 mm at 45 / 75 / 15
  (held: 1.63 mm at 135 / 135 / -45). None is deeper than 3 mm. This is shallower than the lead (deepest 8.93 mm).
- **In band, workspace (unscored):** 0.793 (0.775).
  - Of the metal on the taken workspace poses, 20.5 % sits more than 14 mm off the skin; the maximum is 27.7 mm.
  - The scored clip frames read 0.853. H1 reads 0.867 and the lead 0.868 on the workspace.
  - The knee link is the part most out of band: 0.628 in band, median 12.9 mm.
- **Springs:** none. The chain is a plain O20 3R with the two-pin MR63ZZ cuff knee. No spring, no drive, no sensed
  passive joint.
- **Stops:** one J3 own-angle stop, a dowel in an arc slot between link 2 and member 3.
  - It is fitted on Bench(60,160) and frozen. The allowed window is 239.5 deg wide.
  - It stops 30 workspace poses (9 of them overhead) and no clip frame.
  - The closest a taken pose comes to the stop is 4.62 deg (held: 1.0 deg).
  - The knee window [25.22, 154.78] never engages: the knee angle stays within 80.2-103.8 deg (bench 80.2-101.4).
- **Cuff twist:** the knee pins are closure-determined, with closure residuals of 0.015-0.023 deg. No spring-held
  coordinate lags.
- **Near-singular postures:**
  - The th fold margin is at least 6.23 deg over the taken bench poses. Held out it is 5.33 deg, and 3 taken poses sit
    under 6 deg.
  - The knee triangle stays 51 deg or more from its window edges (55 deg on the bench).
- **Continuity:** no static islands. The verifier's flood connects 959 of 959 kinematic nodes, and drops 0 claim poses
  on the bench and 0 held out.

### What the J3 stop buys (measured this audit)

Same frozen shape, worn on Bench(110,360) exact with the J3 window removed
(`remeasure/crest-knee-3r_bench_noj3win.json`).

**Without the window the gap is 33.97, against 32.83 with it.** Reach is unchanged at 0.6333. Of the 30 poses the stop
blocks:

- 26 would be part-part clashes, where link 2 runs into member 3. They are lost either way, because the bodies would
  stop each other.
- 4 would be contact poses: side raises at plane 15-60 / elevation 75-90, pressed 3.56-5.31 mm into the arm.

On the search bench the window turns 5 contacts (0.43-7.21 mm deep) and 11 clashes into stops, and costs 1 takeable
pose: 28.42 -> 26.34.

So the stop's 1.14 points are four deep presses that become a clean hard stop. It is a real part acting on J3's own
angle, frozen from the search bench, with a blocked arc of 120.5 deg. It is not a sliver band that relabels near-zero
touches. It is not a gaming pattern.

What it does mean for the wearer: a side raise at 75-90 deg at those planes ends on a stop, because no 3R state at
these seats reaches it.

## Findings (judgement pass; `docs/alignment/crest-knee-3r.findings.json`)

1. **G1 metal hugging, watch.** Overhead reach is metal at the skin: the numbers above. 25.14 gap points live in the
   1-2 mm shell (H1 19.65, the lead 16.56).
   - Why the exo is not better than its number: a 1-2 mm reading on the model is metal on a real, bulging arm.
   - Action: none on the score (the user's ruling: near-touch is report-only). Any follow-up of this morphology should
     search the overhead clearance, not the plain gap.
2. **NEW-ws-inband, watch.** Covered under "In band, workspace" above: 0.793 / 0.775 on the unscored taken workspace
   poses, against 0.853 on the scored clips.
   - Why not better: the crest seats lift member 3 and the knee link off the skin on poses the score does not read.
   - Action: report it beside the claim.
3. **P2 held set includes search poses, watch.** The verifier's `held_bench()` leaves out Bench(110,360) but keeps the
   60 Bench(60,160) poses (20 clip, 40 workspace) that the shape was fitted on.
   - Those 60 read 21.43; the 410 unseen poses read 30.88.
   - So the honest held number is 30.88, not 29.81 (`remeasure/crest-knee-3r_held_overlap.json`). It is still better
     than the bench claim.
   - The set is also drawn from the fit clips only.
4. **R2 stale display, watch.** `docs/dashboard/data/morphs.json` shows gap and sweep_gap 26.34 (score 90.42). That is
   the in-sample fast best of 531 configs, against the verified 32.84.
   - The row's verdict text still reads as the screen.
   - It has no rank effect: the leaderboard ranks by v_gap.

### Patterns walked and not present

- **T1:** the search objective was the 1 mm near-touch gap. The shell is G1 above, and it is report-only.
- **T2:** the band read as 3-14 mm costs 2.46 points (35.30). Clip metal at 2-3 mm is 2.5 %.
- **T3:** the margin is read in th itself (verifier `crest_checks`, the H1 metric).
- **T4:** ang_min sits at the rule edge (25.22) and j3stop_margin at its box floor (1.0). Neither spends a singularity
  margin: the knee stays 51 deg or more inside its window, and the J3 limit is a hard stop, not a singularity.
- **T5:** the contact is shallower than the lead's.
- **S1:** held out beats the bench, and the |axial| >= 150 share is 7.5 % bench and 8.1 % held.
- **S2:** part-weighted in-band (0.865) is above sample-weighted (0.853).
- **S3:** every declared body has metal samples: boss 32, pad 32, L1 44, every other part 80-112 (all above the 16 floor).
- **S4:** the depth check uses the same skin mesh as every other row.
- **S5:** the flood above.
- **M1 / M2:** O20 hubs and MR63ZZ knee pins at stk 6.0.
- **M3:** the verifier's extra checks (independent 3D closure, knee vs hub 3, E boss vs hubs, L1 and L2) remove 0
  poses.
- **M4:** the knee moves 21 deg (pin a 21 deg, pin b 24 deg bench / 25 deg held).
- **M5:** no spring.
- **P1:** held out is better than the bench.
- **P3 / R3:** the claim is the best of 3 frozen cells (32.84, 33.23, 37.40), and all three are on the row. It was
  picked by the fast near-touch objective, which it also leads.
- **P4:** no measurement file changed.
- **R1:** the row's status matches the verifier files. The verdict text is under R2.
- **R4:** the dashboard v_gap equals the row's.
- **G2 / G3:** no spring and no lagging coordinate.
- **G4:** see T3 and T4.
- **G5 / G6:** 3 active joints. The cuff knee scores 0 under the user's 2026-10-17 ruling. The J3 stop is a dowel and
  is not counted (stops are not counted in tools/simplicity.py for any design).

### Numbers not obtained

- The kNN continuity flood was not run. The verifier ran the full-grid flood, which is the rule's flood.
- The true held-out split (data/raw/split.json clips) was not worn. The model and the verifier have no wear path for
  it, and adding one would be a new harness, not an audit.
- No R17 dynamics judge was run (no spring to load). Cuff twist is read from the closure residuals only.

## Proposals (not applied; measurement or reporting changes for the lead to decide)

1. **The audit tool's `continuity` check should read `row.verification.continuity` and `*_v_flood_*.json`.**
   - This row has `bench_dropped 0`, `held_dropped 0` and `grid.islands 0` on file. The tool looks only at a top-level
     `continuity` key, at verifier files with a `connected` key, and at remeasure files. So it reports "no flood on
     file".
   - Effect on every verified row: it changes no number. It can only turn false watches into ok.
   - The crest family's verifier spelling (`bench.static` / `bench.connected` / `dropped`) would map directly onto the
     check's `static` / `connected_full` reading.
2. **held_bench() should leave out the search bench too** (carried from deltoid-crest-j3-3r P2, measured again here).
   - On this row the change is +1.07 on the held number (29.81 -> 30.88).
   - It would apply to every row verified through tools/osn_polish.py held_bench. Measuring it needs each row's
     held-out per-pose dump and the same 60-pose overlap mask (this audit's `remeasure/crest-knee-3r_held_overlap.json`
     shows the method).
3. **Stop accounting in the claim.** A claim with a fitted hard stop should report what the stop does:
   - how many poses it blocks;
   - what each would be without the stop (clash, contact and depth, or taken);
   - the gap without it.

   Here the answer is 26 clashes and 4 contacts, 33.97 -> 32.83: a real part buying a clean stop. Recording it makes a
   sliver-band relabel easy to tell apart from a real stop (the round-14 judge's control).

## Files

- `docs/alignment/crest-knee-3r.json`: the 13 checks.
- `docs/alignment/crest-knee-3r.findings.json`: the 4 judgement findings.
- `docs/alignment/remeasure/crest-knee-3r_{bench,held}.json`: deep re-wear (near-touch 1 / 2 / 3, histogram, spans).
- `docs/alignment/remeasure/crest-knee-3r_{bench,held}_probe.json`: wear probe, from the same worn bench.
- `docs/alignment/remeasure/crest-knee-3r_bench_noj3win.json`: the J3 window removed, same frozen shape.
- `docs/alignment/remeasure/crest-knee-3r_held_overlap.json`: the held set split into search and unseen poses.
- `tools/alignment_crest_knee_adapter.py`: a new file. It gives the model a held wear through the verifier's own
  held_bench, and captures the worn bench so the remeasure and the probe come from one run.
