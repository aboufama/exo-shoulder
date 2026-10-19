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

## Skeptic (2026-10-17, 06:55-07:12 UTC, git e25c89d)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and
changed no score. Compute was local only (nice, OMP_NUM_THREADS=1, one process). The farm was not used.

**Re-derived and re-measured this session (models unchanged).**
- **Per-pose dumps.** The gap was recomputed from `remeasure/groove-desmo-knuckle-3r_{bench,held}_perpose.json` with the
  bench's own formula.
  - Bench: 22.64 (ws 245/360, in-band 0.8986, contact 2/470).
  - Held out: 28.77 (ws 595/952, in-band 0.8972, contact 0.0099).
  - Contact depths: bench sum 17.00 mm, held 44.81 mm.
  - Raised arm 43/113 and 103/300; overhead 8/28 and 18/71. Taken poses < 1 / 2 / 3 mm: 2 / 25 / 130 on the bench.
- **Fix-1 groove sized at the cut stroke.** The 1.61 groove in the audit was sized for the claim's 41.25-deg stroke
  (run-out 0.108). At the verified stroke the verifier's own number is 1.59 (`_truewin.json` groove_width_needed_mm).
  - Re-worn: `tools/alignment_groove_width_probe.py 1.59 bench` (exact, 100 s) ->
    `remeasure/groove-desmo-knuckle-3r_groove1.59_bench.json`.
  - Window [7.095, 8.405], stop B 31.0 deg, **gap 23.48** (reach 0.6722, 3 more lost ws poses).
  - At that stroke the groove needs 1.587, so 1.59 is self-consistent. Groove pressure angle 35.27.
- **Complexity.** `tools/simplicity.py` v2.2: 18.25 as recorded, 19.25 with the slot as a track pair.

**Rulings** (also in `docs/alignment/groove-desmo-knuckle-3r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| held_out (watch) | no | Recomputed from the per-pose dumps: 28.77 - 22.64 = +6.13 (+6.12 against the dump's 22.65). That is above TH held_watch 6.0, on the same harness both sides. The loss is real: stop B drops 37 held-out ws poses (reach 0.6639 -> 0.6250) and 12 on the bench (0.7139 -> 0.6806). |
| idle (watch) | **yes** | The rigid-knee assertion comes from the other cell. The row has `best_params.cell` "lead" and `mechanism.cuff_knee.pins` 2. Model line 55 defaults to the lead cell, which loads `roller-longdyad-knuckle-3r.py`. `knee_moved` is set only in `kneeless-roller-knuckle-3r.py:166` and `kneeless-sidecar-knuckle-3r.py:150`; this model only reads it (line 305), and c_idle's regex matched that string. The knee's 86.21-151.92 deg is the pin knee's designed motion, inside [25.22, 154.78]. K moves 32.02 deg, and the crank 32.02 / 2.47 = 13.0 deg (lin law); both are far above 2.0. |
| reporting (watch) | no | Row verdict opens "SCREENED" with 19.29 / 24.96 / +-0.54. morphs.json (1b9ffbd) has the same text and sweep_gap 17.21, which is 5.43 below 22.64. |
| S1 (watch) | no | All numbers reproduce: lead 18.67 / 23.73; 37 / 12 lost poses; paired SD 1.35 (`remeasure/roller-longdyad..._vs_sidecar-longdyad..._paired_claim.json`). Correction: frontload's verifier held-out is 26.75 (`verification.corrected.held_out`), so the held-out lag is 2.02, not 2.12. That is still a tie on the gap, at 6+ fewer complexity points than frontload's 25.5. |
| NEW-planar-gate (watch) | no | Confirmed: true crest 8.934 against the 8.44 window (0.31-mm wall), tilt 14.78, pressure angle 36.17 against 30.5, +3.35 points. The 22.64 is clean (pitch_r_taken max 8.421, 0 poses over the window). The gate is still live in the model file, though: its own `sc_info.groove` reads crest 8.24, pressure angle 30.5 and slop 0.54 even inside the truewin wear, and run alone it gives dK_lim 41.2. The lead family's crest gate is the same planar formula (`sidecar-roller-flank-knuckle-3r.py:256`, `sidecar-longdyad-knuckle-3r.py:229/268`) and has not been checked in 3-D. |
| M2 (watch) | no | Binding confirmed at the cut stroke: tilt 3.3 deg, run-out 0.085 mm against a 0.02 clearance, 1.59 needed. **Size corrected by measurement:** fix 1 at the cut stroke is 23.48 (1.59) to 23.77 (1.61), i.e. +0.84 to +1.13. Both are behind frontload's 22.82. |
| G5 (watch) | no | simplicity.py gives 18.25, and 19.25 with sliding_pairs 2 / rolling_pairs 0. Line 42 lists "slot" as a track pair. slotted-eccentric-j2-3r (MR52 roller in a 2.6 slot) and cam-coupled-4r carry sliding_pairs 1. The edge over the lead is 1.0. |
| M5 (watch) | no | slop_K_deg_needed is 1.62 / 1.61 at the cut stroke and 2.03-2.04 at the claim stroke. The model has no slop state, and no measurement of its effect on metal or on the pose exists, so the watch stands as a missing measurement. **Size note (derived, not measured):** the verifier divides the half-play by s_arm 4.05, the radial lever (verify script line 255). The play acts along the groove normal, where v_F.n = \|v_F\| cos(pa) = 6.6-7.6 mm/rad (pivot_d 16.02, theta_F -14.6, r 7.06-8.42, pa 36.17). That suggests about +-0.9-1.0 deg. |
| G4 (watch) | no | Pressure angle 36.17 (taken = grid) against 37.29 = 43 - atan(0.10). The friction coefficient at the gate is tan(6.83 deg) = 0.120; mu 0.15 fails (gate 34.47). With the 1.59 groove the angle is 35.27, so mu <= 0.135. Horn 39.0 against the lead's 43.0. |
| M3 (watch) | no | Missing: "pocket" has 0 hits in the model and the verifier. The doc (line 305) says "not modelled". There is no CAD. |
| T5 (watch) | no | Depths re-derived: bench 10.97 + 6.03 = 17.00 mm; held 8 poses, 44.81 mm. The tool's reading against roller-longdyad is ok (x1.03). Against the other verified 3-active leader, sidecar-longdyad (6.23 mm), it is x2.73 and +10.77 mm, past both documented triggers. The lead's own contact-depth finding was upheld on that comparison. |
| NEW-ws-inband (watch) | no | `_bench_probe.json` ws_elev90_140: in-band 0.781, 21.8 % over 14 mm (held 0.807). The lead is 0.7979 and sidecar-longdyad 0.8409. This is felt bulk that the score never reads. |
| R1 (watch) | no | The row verdict, `frozen.gap` 19.29 and `held_out.gap` 24.96 are stale against `verification.corrected` (22.64 / 28.9). morphs.json carries the stale text. |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **Two of the lead's upheld knee findings are carried but not listed.** This design wears the lead's knee with the
   same `ang_min` 25.2189 and the same kK 2.1534.
   - Its taken knee reaches 151.92 deg on the bench and 153.16 held out (`remeasure/_bench.json`, `_held.json`
     `extras.knee_ang_taken`). That is past H1's 149.54-deg window, where the lead's skeptic upheld G4: the hub-only s8
     is lowest there (0.2497 / 0.2455; `roller-longdyad-knuckle-3r.rulings.json` judgement:G4).
   - The audit read the knee only against 154.78 (180 - ang_min).
   - The lead's knee-sensing finding also carries: the hub-only floor is 1 / (1 + kK) = 0.317 from the unread slaved K.
     This design adds K's groove slop to that unread error.
2. **The planar gate is still live in the model file.**
   - Only the verifier's `--truewin` wrapper cuts stop B to 32.25.
   - Run alone, `docs/concepts/models/groove-desmo-knuckle-3r.py` gives dK_lim 41.2 (row.fast). Its own `sc_info.groove`
     still reports crest 8.24, pressure angle 30.5 and slop +-0.54.
   - Any search, polish or derivative run on this model re-buys the 3.35 points. The audit said only that "the 22.64
     no longer depends on it".
   - Proposal C (M6) should also require the model to carry the 3-D gate, not just the verifier.
3. **Stale pre-cut values inside the verified wear's output.**
   - In `remeasure/_bench.json` `extras.sc_info`, phi_max_taken 16.7 (= 41.25 / 2.47) and pa_horn_max_taken 42.9 are
     the uncut-stroke numbers. The cut stroke gives 13.0 deg and 39.0 (`roller.pa_horn_max`).
   - c_idle reads `phi_max_taken` as the crank span, and a reader could take 42.9 as the horn pressure angle.
   - This is a reporting hazard, not a score move.

**Corrections to the audit's numbers (no level changes):**
- M2's fix 1 costs 23.48-23.77, not 23.77 alone.
- Frontload's held-out figure is 26.75, not 26.65.
- The K slop is probably about +-0.9-1.0 deg, not +-1.6-2.0. This is derived, not measured; the verifier's formula
  uses the radial lever.

**Final verdict (ledger, skeptic entry 2026-10-17T07:10:36Z): WATCH.**
- Refuted with evidence: idle, a tool false positive. Proposal B stands as a tool action.
- Upheld as watch: held_out, reporting, S1, NEW-planar-gate, M2, G5, M5, G4, M3, T5, NEW-ws-inband and R1.
- The 22.64 is an honest number for the part as modelled with a 1.52 groove.
- With a catalogue dowel the design is 23.48-23.77: behind the lead by 4.8-5.1 points on the bench and 5.04 held out,
  and behind frontload's 22.82.
- It is still the simpler design: 18.25-19.25 against the lead's 20.25 and frontload's 25.5.
