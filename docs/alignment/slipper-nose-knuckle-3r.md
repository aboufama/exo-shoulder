# Alignment audit: slipper-nose-knuckle-3r

Auditor run 2026-10-17 06:50-07:10 UTC (discovery round 10, slice r10-B). Ledger entry 2026-10-17T07:07:17Z, `by auditor`,
run `audit:slipper-nose-knuckle-3r`. Checks: `docs/alignment/slipper-nose-knuckle-3r.json` (tool VERSION 2026-10-17.2,
`--ref roller-longdyad-knuckle-3r`). Findings: `docs/alignment/slipper-nose-knuckle-3r.findings.json`.

## Verdict: WATCH (no gamed reason; the number is real and the exo is a little better than the lead)

- **The claim:** v_gap 18.49 (score 93.28), frozen exact Bench(110,360), verified 2026-10-17 06:22 UTC. The design is
  the lead roller-longdyad-knuckle-3r with its MR63ZZ drive roller deleted: a hardened O2.37 nose slides on a flank
  re-fit at mu 0.087.
- **Re-worn here, with the model unchanged** (farm, CB_EXACT=1; `docs/alignment/remeasure/slipper-nose-knuckle-3r_*.json`):
  - bench 18.49 (reach 0.725, ib14 0.8955, contact 0.0054);
  - held out 23.45;
  - 1 / 2 / 3 mm near-touch 20.12 / 33.02 / 83.15.
  - The claim reproduces to the digit.
- **Against the lead, pose by pose** (claim dumps on both sides,
  `remeasure/slipper-nose-knuckle-3r_vs_roller-longdyad-knuckle-3r_paired_claim.json`):
  - Bench -0.18, all from the in-band term. The two take the same 261 workspace poses and the same 2 contact poses.
    Paired 90 % interval [-0.26, 0.00]; P(slipper better) 0.70.
  - Held out -0.28 (one extra workspace pose, plus in-band). Interval [-0.47, 0.00]; P 0.94.
- **The reasons are all watch:**
  - 2 tool checks: `idle`, a false positive explained below, and `reporting`;
  - 6 judgement findings: M5, G4, T5, NEW-ws-inband, NEW-stale-complexity-ruler and NEW-filler-metal.
  - Four of them are carried unchanged from the lead family (G4, T5, NEW-ws-inband, and M5 in part). One is a
    reporting error that understates the design (complexity). One rules on a control column that is not part of the
    claim (the wedge).

Where the plain-gap lead comes from: the 0.18 over the lead is the drive-arm re-fit (beta, r_c, lift), not the nose. The
verifier wore the lead's own roller on the same re-fit arm and measured 18.36 (`verify/..._v_roller_at_A.json`). The
row's own verdict already files the move as a simplification below the 1-point rule.

The nose does not buy points, but it does buy the wearer something the score does not see. Deleting the roller's
O4.5 x 0.8 retaining head raises the metal floor:
- on 93 of the 371 shared taken bench poses, and 224 of 851 held out;
- on no pose is the slipper's floor lower than the lead's (1 pose held out).
- Taken poses with metal under 3 mm: 100 against 133 on the bench, 198 against 273 held out.

So the dashboard places it first among the verified 3-active rows, and the wearer is no worse off for that.

## What the wearer gets (measured, Bench(110,360) exact, frozen; held out in brackets)

- **Overhead (elevation >= 140):** 8 of 28 workspace poses taken (18 of 71). Lost to the fold 14, knee slide 4,
  contact 2 (36 / 11 / 6). The same as the lead.
- **Raised arm:** reach by elevation band is 26/51 at 90-120 and 12/34 at 120-140, then 5/13 at 140-160 and 3/15 at
  160-200. Workspace reach in all is 261 / 360, or 0.725 (650 / 952, 0.683).
- **Taken poses with metal under 2 mm:** 30 of 371 (66-67 of 852). Overhead, 4 of the 8 taken workspace poses and 5 of
  the 10 clip poses have their lowest metal at 1-2 mm. Under 1 mm: 3 poses (14), the lowest 0.07 mm at plane -60,
  elevation 60, axial 105 (held out 0.33 mm). The lead has the same counts.
- **Deepest contact:** 9.01 mm into the arm at plane 15, elevation 165, axial -60 (overhead), and the second at 5.74 mm
  (plane 30, elevation 165). Summed 14.75 mm, against the lead's 16.46.
  - Held out: 10 contacts, summed 46.12 mm, deepest 9.05 mm at (30, 165, -45). The lead: 49.88 mm.
  - sidecar-longdyad presses 6.23 mm summed on the bench (deepest 4.61).
- **Workspace in-band (unscored):**
  - all taken workspace poses: 0.856 (0.861);
  - elevation 90-140: 0.800, with 0.199 of the metal above 14 mm (0.822). The lead reads 0.798, sidecar-longdyad 0.841;
  - overhead: 0.940 (0.932).
- **Clip in-band (scored):** 0.8955; 2-3 mm band-edge share 0.0015 (lead 0.0018). Reading the band as 3-14 mm gives
  18.64 (lead 18.84): **T2 clean**.
- **Springs, stops and transmission:**
  - Spring: one clock spring (0.08 N.m + 0.03 N.m/rad) force-closes the lobe follower and the sliding nose.
  - Pressure angles: horn 35.8 + 4.97 friction = 40.77 deg against 43; crank 29.5 + 4.97 = 34.47 deg (the lead's
    crank side was 8.2).
  - Stroke: dK taken 45.62 of 49.75 deg. The K dyad window `a1max` binds before the drive.
  - Knee: up to 151.92 deg (153.16 held out) of its 154.78 window.
  - Fold margin in th, as the family reads it: 5.181 (5.006). The K sub-chain m_sub at rest is lower; see G4.
  - Cuff twist: not measured (no R17 run for this design).
  - Idle mechanisms: none. K moves 45.6 deg, the crank 19.3 deg and the knee 86.2-151.9 deg.
- **DOF:** 3 active, 0 passive translations, O20 hubs.
- **Complexity:** 22.25 as recorded; 18.25 with the knee loop recorded the lead's way (the lead reads 20.25).

## Findings

Each finding gives the pattern, the evidence, why the exo is not better on that point, and the action. None is gamed:
in each one the ranking either does not move against a design that is better for the wearer, or the comparison is mixed.

1. **M5, watch: a spring that may not hold, now against sliding friction.**
   - **Evidence:** the clock spring must return the crank through a sliding contact at 34.47 deg effective. The lead
     returned it at 8.2 deg through a rolling contact.
   - **Why it matters:** the score assumes K is on its law at all 167 bench (400 held-out) poses where K moves. No
     R17 or preload number is on file; the only evidence is the claim's hand calculation (drag 0.01-0.02 N.m against a
     0.08 N.m preload). If the spring lags, K leaves the flank and the cuff twists.
   - **Friction:** mu 0.087 is assumed and the wear test is pending. The number holds to mu 0.12 (verified); at mu 0.15
     the claim's own fast table loses 3 poses (14.90).
   - **Action:** run the R17 dynamics judge on the return stroke at mu 0.087 / 0.12 / 0.15 when CAD exists, and do the
     wear test before CAD.
2. **G4, watch: a near-singular sub-chain at rest, family-wide.**
   - **Evidence:** with K resting on stop A (204 of 371 bench poses), m_sub is under 5 deg on 106 poses and under 1 deg
     on 50, with a minimum of 0.000 deg at (15, 75, 15). It is identical to the lead pose by pose (max |difference|
     0.000; new probe `tools/alignment_msub_rest_probe_model.py`, `remeasure/*_msub_rest_bench.json`).
   - **Why it matters:** the family's fold reading (5.181) does not read m_sub at rest. This is the B1 question that is
     open with the user.
   - **What changed:** the slipper neither causes nor worsens it, and it improves the drive's own margin (2.2 deg under
     the 43 cap, where the lead sat on it).
   - **Action:** none for this row until the user rules on B1.
3. **T5, watch: depth-blind contact, family-carried.**
   - **Evidence:** 2 overhead presses of 9.01 and 5.74 mm. They are shallower than the lead's.
   - **Why it matters:** the row ranks above sidecar-longdyad (18.49 against 18.91), which presses only 6.23 mm summed
     (2.37x less, 8.52 mm less, past the tool's own 2x / 5 mm margin). Held out the ratio is 1.29x.
   - **Why it is only watch:** sidecar-longdyad is worse plain, at 2 mm (34.03 against 33.02) and at 3 mm.
   - **Action:** report the summed depth next to the gap (as T5 already proposes).
4. **NEW-ws-inband, watch: unscored raised-arm standoff, family-carried.**
   - **Evidence:** at elevation 90-140 only 0.800 of the metal is in band and 0.199 is above 14 mm (p95 20.15, max
     30.8 mm). sidecar-longdyad reads 0.841 / 0.157.
   - **Why it matters:** the gap reads in-band on clip frames only, so this raised-arm standoff costs nothing in the
     score.
   - **Action:** none for this row (A3-type reporting proposal below).
5. **NEW-stale-complexity-ruler, watch: the complexity shown understates this design.**
   - **Evidence:** the row's 22.25 charges the cuff knee's closure loop (4 points), because `cuff_knee` has no
     `closed_loops` field. The lead's record puts that loop under `cuff_knee.closed_loops: 1`, which simplicity v2.1
     (ec77d25, 04:55 UTC) frees: the lead reads 20.25. Recorded the same way, the slipper is 18.25 (`tools/simplicity.py
     --score`).
   - **Why it matters:** the dashboard shows the slipper 2.0 more complex than the lead when it is 2.0 simpler. The doc
     still compares with the lead's pre-v2.1 24.25.
   - **Action:** the row's owner adds `cuff_knee.closed_loops: 1` and refreshes the complexity. This audit does not
     edit rows.
6. **NEW-filler-metal, watch: the wedge column, which the design doc hands to the auditor.**
   - **Evidence:** on the kneeless control, the hub-3 wedge gains 1.06 points purely in-band (hub 3 in band 0.505 to
     0.799) by adding 4.73 g of metal under the hub (mean 3.4 mm, max 7.61 mm deeper). The crown the wearer feels stays
     at a median 21.9 mm above the skin, and the lowest underside goes from 1.9 to 1.8 mm.
   - **Why it is not better:** the exo is not lower. It is heavier, and its metal is closer to the arm.
   - **Scope:** not part of the claimed 18.49, which has no wedge.
   - **Action:** do not claim a wedged column. See catalogue proposal C1.

**Tool reasons:**
- **`idle` (watch): an instrument false positive.** It reads the knee as "rigid by design" because the model file holds
  the kneeless control branch (`knee_moved -> dishonest`). The claim runs SN_CELL=lead, whose knee is the lead's moving
  two-pin cuff knee (K.ang 86.2-151.9 deg, inside its 25.2-154.8 window; row `mechanism.cuff_knee`, pins 2). A skeptic
  can refute it on that evidence.
- **`reporting` (watch): it stands.** The row's `verdict` field still begins "screened -" with status verified, and the
  dashboard shows the fast sweep best 13.0 (score 95.27) next to the verified 18.49.

## Patterns walked (each against this design and the goal)

| pattern | this design | evidence |
|---|---|---|
| T1 metal past the cutoff | 14.53 points in the 1-2 mm shell (lead 14.43; watch line 15); 30 poses < 2 mm = the lead | remeasure bench `deep` |
| T2 band edge | clean: 2-3 mm share 0.0015 (lead 0.0018); band 3-14 costs 0.15 | remeasure bench `deep` |
| T3 margin on another angle | th 5.181 / 5.006 on th itself; m_sub at rest -> G4 | probe extras, msub probe |
| T4 search bound at the box edge | s_arm = 4.0 = its clamp minimum (lead 4.05): a lever length, not a window; lobe pressure angle 23.5 deg. a1max 0.26 deg under bk1+bk2-5 = the fold rule, the lead's seats. Not present | rows best_params, model `_clamp` |
| T5 depth-blind contact | finding 3 | paired_claim |
| S1 skewed sample | held-out drop +4.96 (lead +5.06); held-out gain over the lead -0.28 > bench -0.18 | remeasure held |
| S2 sparse bad metal | part-weighted in-band 0.924 > sample-weighted 0.895; L1a 8 samples (lead's) | audit `sampling` |
| S3 unsampled bodies | 5 moving bodies, all sampled (nose sampled as "roller", 19 samples) | parts_ib14 |
| S4 skin sample | family-wide, nothing specific | - |
| S5 static islands | full flood 18.49 = static; knn 20.16 (+1.67 = the lead's +1.67) | verify `_v_bench_frozen` |
| M1 virtual parts | O2.37 nose; stock O2.5 / O2 dowels verified at 18.49 | verify `_r125`, `_r100` |
| M2 slim components | O20 hubs | rules |
| M3 unchecked clashes | nose-lug 2.70-3.28 mm (nose r 1.18), nose-hub K 3.92, arm-hub K 1.31, closure 0.0, no undercut (0 of 913 steps); edge-strip correction 18.44 | verify extra |
| M4 idle drive | K 45.6 deg, crank 19.3 deg | remeasure spans |
| M5 springs | finding 1 | - |
| P1 / P2 in-sample, held-out leakage | A was chosen by the CMA objective on the fit bench; A' (18.18 frozen, better) was NOT picked by its frozen number; B was rejected on frozen (19.81) AND held out (24.78), A was ahead on both | doc "Last claim columns" |
| P3 best-of-many | 3 CMA runs, 3603 evals + 160 sweep; spread reported (A 18.49, A' 18.18, C 18.55, B 19.81) | row note |
| P4 judge changed with design | none in the 4 row commits | audit `judge_change` |
| R1 / R2 / R3 / R4 | tool `reporting` watch (verdict text, sweep best 13.0); R4 fixed (dashboard keeps 18.49) | morphs.json |
| G1 hugging | the in-band gain did not come from 1-3 mm (2-3 share fell, 3 mm poses 133 -> 100) | paired floor |
| G2 / G3 stiff spring, cuff twist | not measured (M5) | - |
| G4 singular postures | finding 2 | - |
| G5 / G6 complexity hidden | inverted: overstated (finding 5); 3 active | simplicity --score |

## Instrument notes (no score changed; for the tool's owner)

1. **Before the re-wear, `near_touch` and `dominance` read the wrong file.** They read
   `verify/..._v_roller_at_A.json`, the counterfactual roller-on-A control (18.36 / 2 mm 34.66), because it was the
   newest non-held verifier file. `dominance` then reported "beats the lead by 0.31 plain, loses by 1.56 at 2 mm"
   (watch). Read on the claim, the numbers are +0.18 / +0.08 (ok). The re-wear fixed the reading on this row.
2. **`idle` false positive.** The rigid-knee assertion is taken from text in the model file, not from the cell the
   claim runs (see above).
3. **`tools/alignment_paired.py compare` read the lead's non-claim dumps.** It read
   `roller-longdyad-knuckle-3r_{bench,held}_perpose.json` (19.34 / 24.28, a re-fit) where the claim dumps are
   `_perpose_claim.json` (18.67 / 23.73). It reported a misleading -0.86 / -0.83. This audit ran the tool's own
   `compare_sets` on the claim dumps instead (`..._paired_claim.json`) and deleted the mis-paired output.

## Proposals (not applied; each a reporting or instrument change for the lead or the user)

- **B-a (instrument).** `alignment_audit._near_numbers` should take only a verifier file whose frozen gap equals the
  row's v_gap (+-0.05) and whose params equal its best_params, not the newest one.
  - Effect measured on this row: dominance watch (0.31 / -1.56) becomes ok (+0.18 / +0.08).
  - Other rows: not measured.
- **B-b (instrument).** `idle` should take "knee rigid by design" from the row's mechanism (no `cuff_knee`, or a
  `rigid` flag), or from the cell the claim runs, not from text in the model file.
  - Effect on this row: idle watch becomes ok.
  - Other rows: not measured; kneeless-roller and kneeless-sidecar should stay as they are.
- **B-c (instrument).** `alignment_paired.py compare` should prefer `*_perpose_claim.json` and refuse a dump whose gap
  is not the row's claim.
  - Effect on this pair: -0.86 becomes -0.18 on the bench.
- **B-d (reporting).** A row that claims a simplification should report the paired metal-floor count next to its gap:
  taken poses under 3 mm, own against parent.
  - Here 100 against 133 (bench) and 198 against 273 (held out). That is the nose's real gain, and the score cannot
    see it.
  - Reporting only; no score moves.
- **B-e (records).** `tools/simplicity.py --check` should flag a pin-knee record whose `cuff_knee` has no
  `closed_loops` while the main `closed_loops` still counts a knee closure.
  - Effect on this row: 22.25 becomes 18.25 when the record is fixed.
  - Other rows: not measured.

**Catalogue entries proposed:**
- **C1 (S-family), "Filler metal under an unmoved crown".**
  - Looks like: in-band rises because metal is added under a part toward the skin while the part's outer crown does not
    move.
  - Why not better: the profile the wearer feels is unchanged, the exo is heavier, and the metal is closer to the arm.
  - Detect: report the crown height and mass next to any in-band gain from added material.
  - Here: the kneeless wedge, -1.06 points, crown median 21.9 mm in both columns, +4.73 g.
- **C2 (R-family), "A complexity compared across records written to different rule versions".**
  - Here: 22.25 against the lead's 20.25 under v2.1, where the like-for-like reading is 18.25.

## Numbers not obtained, and why

- **R17 dynamics / cuff twist / preload hold at mu 0.087-0.15:** there is no CAD and no dynamics model of the sliding
  nose (judge side).
- **Frozen exact wear at mu 0.15:** not run in this time box. The claim's fast table gives 14.90 with 3 poses lost.
- **m_sub probe on the held-out set:** bench only (the bench reading is identical to the lead's).
- **Re-wear of the kneeless wedge columns:** they are not the claim. The row's frozen numbers were used.

Farm cost of this audit: 8 jobs, about 1690 worker-seconds, about $0.14 (cpu3c rate), within the $1.5 cap.
`tools/runpod_guard.py audit` before: exo-cpu1 workersMin 0.
