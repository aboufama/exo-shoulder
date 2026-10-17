# Alignment audit: groove-desmo-knuckle-3r

Auditor run `audit:groove-desmo-knuckle-3r`, 2026-10-17 (discovery round 10, slice r10-B verified this design this
round). Reference: roller-longdyad-knuckle-3r, the verified 3-active lead (18.67). Tool VERSION 2026-10-17.2.

## Verdict and claim

- **Claim:** v_gap **22.64** (score 91.77), Bench(110,360) exact, frozen shape, the verifier's corrected number
  (`docs/concepts/rows/groove-desmo-knuckle-3r.json` verification; the claim's own 19.29 did not survive).
- **Ledger verdict: WATCH** (`docs/alignment/ledger.jsonl`, entry by auditor, run `audit:groove-desmo-knuckle-3r`). The tool's
  own verdict is watch (held_out, idle, reporting); the judgement pass adds 10 watch findings and no gamed one.
- **In one line:** the verified number is honest and reproduces to the digit; the design is not ranked above a better
  one. It is a complexity / hold trade against the lead, worse on every bench number (plain +3.97, 2 mm +1.96, held out
  +5.04), and its complexity edge is smaller than the count says.

## What the wearer gets (measured)

Re-worn here through the verifier's own `--truewin` protocol (the one that produced 22.64), models and verifier
unchanged, only `PK.audit` wrapped (`tools/alignment_wear_truewin_groove.py`, new). Bench: 22.64 reproduced (per-pose
dump recomputes 22.65), 0 failing poses, 179 s. Held out: 28.77 (the verifier's dropped-pose estimate was 28.90),
0 failing poses, 336 s. Raised arm held out: 103 / 300 (lead 114 / 300); reach held out 595 / 952 (0.625; lead 0.682). Files: `docs/alignment/remeasure/groove-desmo-knuckle-3r_{bench,held}{,_perpose,_probe}.json`.

| | groove-desmo (this audit) | lead roller-longdyad (its audit) |
|---|---|---|
| reach, workspace | 245 / 360 (0.681) | 261 / 360 (0.725) |
| overhead (elev >= 140) taken / total | 8 / 28 (held 18 / 71) | 8 / 28 (held 18 / 71) |
| raised arm (elev >= 90) | 43 / 113 | 46 / 113 |
| taken poses with metal < 1 / 2 / 3 mm, bench | 2 / 25 / 130 | 3 / 30 / 133 |
| taken poses with metal < 2 mm, held out | 40 (clip 8, workspace 32); < 1 mm 6 | 66 |
| contact poses, bench | 2: 10.97 mm at (15, 165, -60), 6.03 mm at (30, 165, -60); sum 17.0 mm | 2: deepest 10.55 mm at (15, 165, -60); sum 16.46 mm |
| contact poses, held out | 8, sum 44.81 mm, deepest 9.93 mm at (30, 165, -45); 3 below elev 150: 3.49 / 1.60 mm at elev 60, 1.22 mm at (15, 105, 15) | 10, sum 49.88 mm, deepest 9.54 mm |
| workspace in-band 2-14 (unscored), all / elev 90-140 / overhead | 0.849 / 0.781 / 0.937 | 0.854 / 0.798 / - |
| overhead p10 lowest metal | 1.82 mm | - |
| fold margin in th, min over taken | 5.389 deg (held 5.406) | 5.181 deg (5.031 held) |

- **Clip metal histogram (scored frames):** 0.02 % of samples under 2 mm, 0.17 % at 2-3 mm, 10.1 % over 14 mm.
  Reading the band as 3-14 mm costs 0.18 points (22.82): the band edge is not exploited (T2 clean).
- **Near-touch (report-only, user ruling 2026-10-17):** 1 mm 23.76, 2 mm 35.06, 3 mm 112.9; 12.42 points live in the
  1-2 mm shell (lead 14.43). The lowest metal, 0.07 mm at (-60, 60, 105), is the lead's pose and part, not the drive.
- **Springs:** none. K's clock spring and stop A are gone; K is held both ways by the groove and the slot.
- **Stops:** the groove ends are stops A and B. Stop B sits at K 32.25 deg (the true 3-D crest meets the groove
  window), against the lead's 46.2: 12 bench taken poses and 37 held-out poses of the claim protocol needed more and are
  lost. The arm meets that stop through an O1.5 dowel in a 1.5-deep groove (stop load not measured).
- **Cuff twist / K slop:** K slop is +-1.6-2.0 deg with the groove that a straight dowel needs (verifier), not the
  claimed +-0.54; the lead's spring drifted 4-8 deg. Not on the bench.
- **Near-singular / near-lock:** fold margin 5.389 deg (ok). Horn pressure angle 39.0 deg at the cut stroke (gate 43;
  the lead runs at 43.0). Groove pressure angle in 3-D 36.17 deg against its 37.29 gate (claim: 30.5). Knee to
  151.92 deg (window ends 154.78).
- **Continuity:** static 22.64 = full flood 22.64; knn flood 24.04 (+1.40; the lead +1.67).

Not measured, and why: cuff twist and K-slop effect on metal (the models have no slop state); the stop-B load on the
dowel (no dynamics judge for this drive); the CAD judge (no CAD for this design).

## Findings

Each finding is in `docs/alignment/groove-desmo-knuckle-3r.findings.json` with its evidence. All are watch. None is
gamed: no measurement shows the number ranking this design above a design that is better for the wearer, and no hard
rule is broken (3 active DOF, 0 passive translations, O20 hubs, fold margin 5.389 deg).

1. **S1, held out (+6.13).** Worn held out through the verifier's own protocol it scores 28.77 against 22.64 on the
   bench, just above the +6 watch line. Before this re-wear the tool read the claim's refuted 24.96 from the row and
   called it ok. The cause is not in-sample tuning: only the drive was searched, on the lead's seats. Stop B at
   32.25 deg cuts more held-out poses (37) than bench poses (12) because the held-out set reaches deeper K. Against the
   lead it is +3.97 behind on the bench and +5.04 behind held out. Against frontload (22.82) it is 0.18 ahead on the
   bench, inside this family's paired SD of about 1.35, and 2.12 behind held out: a tie. **Action:** quote the held-out
   28.77 next to the 22.64 wherever the design is ranked.
2. **NEW-planar-gate, the claim was bought by a planar gate on a 3-D drive.** The claim's groove-fit gate was planar
   and linear (crest 8.24 at 41.25 deg). The crank turns about an axis tilted 14.78 deg from hub 2's, and the dowel
   drifts 15.6 deg, so the true crest was 8.93 against the 8.44 window: a 0.31-mm outer wall instead of 0.8. That was
   worth 3.35 points (19.29 -> 22.64). The same shortcut put the groove pressure angle at 30.5; in 3-D it is 36.17.
   The verifier corrected the number, so the 22.64 does not depend on it. **Why not better:** the claimed stroke does
   not fit in the part. **Action:** proposal M6 below, and a check of the lead's own rim lobe, which turns about the
   same tilted crank axis.
3. **R1, refuted numbers still shown.** The row's top-level verdict and the doc's Verdict section still say "19.29,
   +0.62 vs the lead, held out 24.96 (+1.23), K slop +-0.54 deg". The verifier measured +3.97, 28.90 and +-1.6-2.0 deg.
   The 06:58 dashboard refresh shows status verified and v_gap 22.64, but still displays that verdict text and the sweep
   best 17.21 (score 93.74), 5.43 better than the verified number. **Action:** the row owner rewrites the headline
   fields from the verification block (a reporting change; no number moves).
4. **M2, the catalogue dowel binds at the size the number assumes.** The 22.64 is worn with a 1.52-wide groove and a
   straight ISO 8734 O1.5 dowel. The dowel tilts 4.2 deg (3.3 deg at the cut stroke), so it binds (verifier). Fix 1,
   the 1.61 groove, was measured here (`tools/alignment_groove_width_probe.py`, new; model constants patched in memory
   only). The window becomes [7.105, 8.395], stop B moves to 30.75 deg, and the gap is **23.77** (reach 0.6694,
   4 more lost workspace poses). That puts the design behind frontload (22.82) on the plain gap.
   - Fix 2, a crowned dowel, keeps the 1.52 window and so 22.64 by construction (not re-worn), at +0.25 complexity
     (a made part instead of a bought one).
   - **Action:** the row states which fix it claims: 23.77 with the catalogue dowel, or 22.64 with a crowned one.
5. **G5, the complexity edge is half what the count says.** The record counts the closed two-walled roller slot as a
   rolling pair, which scores 0 points. `tools/simplicity.py` lists "slot" as a track pair, and the project's other
   roller-in-slot rows count it as sliding (cam-coupled-4r, slotted-eccentric-j2-3r: sliding_pairs 1). A single roller
   in a closed slot with clearance also reverses spin at each wall change, so it skids.
   - Counted as a track pair: 19.25 against the lead's 20.25, an edge of 1.0, not 2.0.
   - A crowned dowel adds 0.25; the true bought count of 14 (the record rounds up to 15) takes 0.25 off.
   - It is still the simpler design. **Action:** recount sliding_pairs = 2.
6. **M5, K is scored on its law but held only to +-1.6-2.0 deg.** This is the groove width a straight dowel needs.
   K is never read, so the slop is also an unread error of up to 2 deg in the hub-only pose estimate. It is milder than
   the lead's spring drift of 4-8 deg, so on hold this design is better than the lead. Its effect on metal distance is
   not measured.
7. **G4, the groove drive sits near friction lock.** The 3-D groove pressure angle is 36.17 deg against
   43 - atan(0.1) = 37.29. The gate holds only for a friction coefficient of 0.12 or less. Dry hardened steel at 0.15
   gives a 34.5-deg gate, which fails. A drive that stiffens when the grease goes is something the wearer feels. The
   horn side, at 39.0 deg, is better than the lead's 43.0.
8. **M3, unchecked interfaces.** Two features are not modelled: the pocket in link 1b that the short arm needs inside
   hub 2's footprint (the parent has the same), and the blended onset of the groove's lin-law corner.
9. **T5, carried from the lead: metal in the arm overhead.** On the bench, 2 contact poses at elevation 165 go 10.97 and
   6.03 mm deep (sum 17.0 mm; the lead's sum is 16.46 mm). Held out: 8 poses, sum 44.81 mm, deepest 9.93 mm (the lead:
   10 poses, 49.88 mm). This is no worse than the lead. The contact term is blind to depth.
10. **NEW-ws-inband, carried and slightly worse.** Unscored workspace in-band at elevation 90-140 is 0.781 against the
    lead's 0.798, with 21.8 % of samples over 14 mm. Held out it is 0.807.

**Checked and not present.**
- T1/T2/G1: near-touch is report-only, and the 1-2 mm shell is 12.42 points against the lead's 14.43. The band edge is
  clean (3-14 mm read costs 0.18).
- T3: the fold margin is 5.389 deg in th (held 5.406), measured on th.
- T4: the drive box bounds are interior (beta -170 in [-215, -120], r_c 16 in [13, 22], g 2.47 in [1.6, 3.2], s_arm 4.05
  in [3.0, 4.6]). r_lobe sits at the groove's physical floor R_LO, not at a search edge. ang_min is the lead's verified
  25.22.
- S2/S3: part-weighted in-band is 0.923 against 0.899 sample-weighted. The dowel and short arm are sampled as crank
  metal. The slot wall's lost first row was restored by the verifier's envelope, giving 22.50 with no new contact.
- S5: the full flood loses 0. The knn flood loses 1.40, against the lead's 1.67.
- M1: no virtual part.
- M4: K moves 32.02 deg and the pin knee 86.21-151.92 deg.
- P2: no search script reads held-out poses. The search hooks take the caller's fast bench, and the CMA scripts
  themselves are not in the repo.
- P3/R3: the CMA plateaued (top-5 spread 0.00 over 2,595 evaluations). The fast-to-verified rise is +7.97, within the
  family's 4.6-14.
- P4: no bench, judge or metric file changed in the row's 4 commits.

**A tool false positive the skeptic should refute.** The tool's `idle` check reads the knee as "asserted rigid by design
but moves 65.71 deg". This row wears the LEAD cell (`best_params.cell` "lead"), which has a working pin knee
(mechanism `cuff_knee.pins` 2). The pin knee moves 86.21-151.92 deg as designed. The "rigid" assertion comes from the
model file's other cell (GD_CELL=kneeless, `knee_moved`) and from the word "kneeless" in the row's family text. The
ledger verdict does not depend on it, because it is watch either way.

## Proposals (measurement or reporting changes; none is an input to the verdict)

- **A. held_out reads the verified held-out number.** Order: this audit's re-wear, then the verifier's
  `verification.corrected.held_out`, then the row's claim `held_out`. Effect on the verified rows that have both:
  - groove-desmo: +2.32 ok -> +6.26 watch (+6.13 with the re-wear);
  - frontload: +3.83 -> +3.93, ok, unchanged;
  - no other verified row has a corrected held-out number on file.
- **B. idle reads the cell the row wears.** A multi-cell model's `knee_moved` assertion, or the word "kneeless" in the
  family text, should not mark a pin knee rigid when `best_params.cell` is "lead" or `mechanism.cuff_knee.pins` > 0.
  Effect: groove-desmo idle watch -> ok. kneeless-roller and kneeless-sidecar are unchanged, because their ids and
  mechanisms say kneeless. Other rows were not measured.
- **C. New catalogue entry M6: a closed-form gate in a simplified geometry.**
  - Looks like: a drive limiter (fit window, pressure angle, clearance) evaluated by a planar or linear formula on a
    mechanism whose axes are tilted or whose follower drifts.
  - Why not better: the claimed stroke or pressure angle does not exist in the part.
  - Detect: the verifier re-derives each closed-form gate from the worn 3-D frames, as this verifier did. Flag a claim
    whose `why_lim` is a closed-form gate on a non-parallel axis pair.
  - Here: groove-desmo, 19.29 -> 22.64 (+3.35).
  - Not yet measured: the lead's rim-lobe crest and pressure angle about the same 14.78-deg-tilted crank axis.
- **D. Count a roller captured in a closed slot as a track pair** (`tools/simplicity.py` "slot"). Effect:
  groove-desmo 18.25 -> 19.25. cam-coupled-4r and slotted-eccentric-j2-3r already count it this way, so they are
  unchanged.
- **E. A claim names its buildable part set.** When a verifier finds a catalogue part that cannot work at the modelled
  size (here the straight dowel), the claim column carries the number with the stated fix. Effect: groove-desmo
  22.64 -> 23.77 (1.61 groove) or 22.64 at complexity 18.5 (crowned dowel). Other rows were not measured.
- **F. Report the friction margin of every sliding cam pair** as the friction coefficient at which its pressure angle
  meets the gate. Effect: groove-desmo 0.12. The lead and other rows have no sliding cam pair and are unchanged.
