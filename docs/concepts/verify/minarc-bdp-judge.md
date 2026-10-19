# minarc-stop-knuckle-4r BDp: the judge's ruling (2026-10-16)

**Ruling: CONFIRMED. BDp is the new VERIFIED LEADER.**

The verified gap is **19.54 (score 92.89)**: frozen exact Bench(110,360), margin 5, continuity applied, buildable stops
priced in. Held out it is **24.18**, against H1's 31.39 in the same harness.
- Both lenses get **19.06 (93.07)** to the digit, held out 23.24, with the stops at exactly the rule.
- The judge priced the stops as they would be built: J2's slot drawn 5.0 +0.5 / -0 deg of J1-J3 margin, and K's stop
  B moved to dK 34.47 (the lens' fix).
- The worst built pairing, measured on the farm, adds **+0.48** on the bench (+0.94 held out).

**Claim under test.** `rows/minarc-stop-knuckle-4r.json` `kitrule_*`. Config BDp is:
- variant B: the pin knee plus a spring knuckle K in link 1;
- the BD seats;
- both J2 stops at the 5-deg J1-J3 margin, as a physical dowel in a q2 slot (-24.98 .. 100.84 deg);
- hub K's cap 6 mm taller.

**Rule.** The design is CONFIRMED only if neither lens refutes it. The verified number is the worst credible
re-measured frozen exact Bench(110,360) gap at margin 5 with the continuity rule, plus any priced mechanism issue.

**Sources.**
- Judge script: `minarc-bdp-judge.py`. Its default mode reads the lenses' raw JSON, never their prose, and recomputes
  every gap from its components with the bench's own `gap_of` (`tools/concept_bench.py`). Its output is
  `minarc-bdp-judge/ruling.json`.
- The script's `wear` mode is the re-measure lens' `wear()`, imported unchanged, with K's stop B moved.
  `CB_FOLD_MARGIN` sets the J2 stops.
- Six farm jobs on exo-cpu1 (cpu3c-8-16), about $0.10. Raw data and logs are in `minarc-bdp-judge/`.

## The two lenses

| lens | harness | bench, margin 5 | held out | min J1-J3 margin, own state | continuity | refuted |
|---|---|---|---|---|---|---|
| re-measure (`minarc-bdp-remeasure.md`) | its own: frozen hand-over by `__dict__` diff, frame-based checks, its own flood fills | **19.06**, near-touch 26.15 | **23.24**, near-touch 28.31 | 5.015 / 5.007 | 1041/1041 kinematic, 1014/1014 contact-aware, 0 dropped | no |
| buildability + red team (`minarc-bdp-buildability.md`) | the claim's `run()` path, plus an independent K / q2 closure and spring-equilibrium scan | **19.06** | **23.24** | 5.01 | continuity file identical to the committed one | no |

**Judge cross-check** (`ruling.json` `checks`, all 14 true):
- Each gap recomputed from (in-band14, follow, reach, contact) equals the reported one.
- The two lenses agree to the digit on the bench and held out: lens 2's raw `.cache/minarc_bdp_build/pinch_{bench,held}.json`
  `model_run`.
- No taken pose is under 5 deg in any run.
- 0 taken poses are dropped by continuity in any run.
- BDp beats H1 on both sets.

## Priced mechanism issues

| issue | found by | price (bench / held out) |
|---|---|---|
| K stop B as modelled (dK 62.83) engages at an effective-dyad margin of 2.74 deg (th 122.2), so the device follows the arm below the margin; move it to dK 34.47 (a1max 54.748) | buildability | **0.00 / -** at nominal J2 stops: the judge's run gives 19.06, identical |
| Clock spring at 0.03 N.m/rad reaches 1505 MPa at stop B; spec <= 0.015 N.m/rad, +C1900, strip >= 145 mm | buildability | 0.00 |
| The J2 stops sit exactly at the rule (min margin 5.007), so a slot cut long breaks it; draw it 5.0 +0.5 / -0 deg | re-measure (flagged), judge (priced) | **+0.48 / +0.94**, worst built pairing (table) |

### Stop tolerance (judge's measurement)

A stop that must engage at 5 deg or more is drawn with a unilateral tolerance: 5.0 +0.5 / -0 deg of J1-J3 margin.
- At the stop, q2 turns about 3 deg per deg of th: the slot end moves 14.6 deg of q2 between margins 5 and 10.
- So the band is about 1.5 deg of q2, or about 0.2 mm of slot-end position at the dowel's r 7.75 mm. It covers machining
  plus chain compliance.
- K's stop B must engage at or before the 5.0 cut with J2 on its 5.0 stop: dK 34.47, drawn -0.5 / +0.
- The worst built pairing is therefore J2 stops at 5.5 with stop B at 34.47. A J2 stop that engages later forces K to
  open further, and stop B then blocks it.

Every row below is the re-measure lens' harness, unchanged, run by the judge on the farm, except the first and last rows,
which are the lens' own runs. Fit is Bench(60,160) fast, refit at each setting; wear is frozen exact.

| J2 stops at | K stop B (dK) | fit | **bench** (score) | reach / in-band14 / contact | near-touch (poses < 1 mm, min) | held out (near-touch) | min own-state margin | q2 slot | continuity |
|---|---|---|---|---|---|---|---|---|---|
| 5.0 (lenses) | 62.83 (as modelled; the rule cuts at m3e 5) | 12.25 | 19.06 (93.07) | 0.725 / 0.8951 / 0.0107 | 26.15 (15, 0.05) | 23.24 (28.31) | 5.015 / held 5.007 | -24.98 .. 100.84 | 0 dropped |
| 5.0 | **34.47** | 12.25 | **19.06** (93.07) | 0.725 / 0.8951 / 0.0107 | 26.15 (15, 0.05) | - | 5.015 | -24.98 .. 100.84 | 0 dropped |
| 5.5 | 62.83 | 13.10 | 19.29 (92.99) | 0.725 / 0.8928 / 0.0107 | 26.15 (15, 0.05) | 23.36 (28.20) | 5.553 / held 5.517 | -23.29 .. 99.70 | 1041/1041, 0 islands, 0 dropped |
| **5.5** | **34.47** (worst built pairing) | 14.32 | **19.54 (92.89)** | 0.7222 / 0.8931 / 0.0107 | **26.44** (15, 0.05) | **24.18** (28.86) | 5.553 / held 5.525 | -23.29 .. 99.70 | 0 dropped (bench 260, held 650 taken) |
| 6.0 | 62.83 | 12.68 | 19.53 (92.90) | 0.725 / 0.8904 / 0.0107 | 26.15 (15, 0.05) | - | 6.000 | -21.68 .. 98.60 | 1041/1041, 0 dropped |
| 10.0 (re-measure lens) | 62.83 | 15.37 | 22.40 (91.85) | 0.714 / 0.8702 / 0.0081 | 26.21 (11, 0.14) | - | 10.017 | -10.39 .. 90.59 | 1014/1014, 0 dropped |

What the table shows:
- **Stop B at 34.47 is free at the nominal J2 stops.** The result is identical, which confirms lens 2's 0-cost fix.
- **The J2 tolerance costs in-band.** In-band goes 0.8951, then 0.8928, then 0.8904 for stops at 5.0, 5.5 and 6.0:
  about 0.47 points per degree. Reach does not move.
- **The pairing costs one more workspace pose of reach**, plus a worse refit (fit 14.32).
- **The tolerance could be cheaper.** A tighter band (0.1-0.2 deg of th, about 0.05 mm at the dowel) would recover most
  of the +0.48. That is a CAD choice that needs the L1 compliance check.
- **The spring equilibrium holds in every run:** 0 forced poses have a smaller K opening inside the slot.
- **The frozen hand-over is asserted identical** to the fit in every run.

H1's verified 27.20 carries no tolerance price. Its taken poses sit at least 5.49 deg (5.32 held out) from the fold, so
a 5.5-deg stop would cost it little. The 7.7-point lead does not depend on this.

## Issues that stand (disclosed, unpriced)

1. **The pinch.** Hub 2's wall is 0.05 mm from the skin at the overhead raise peak (plane 30, elevation 150, axial -60)
   with K closed.
   - It is the same part and value as the refuted BD. The held-out set repeats the same pose, so it is no independent
     test.
   - It is disclosed in near-touch 26.44 (held out 28.86), still better than H1's 31.75 (34.66).
   - This is the first thing the cross-fit near-touch polish must remove.
2. **Near-edge feel.** 99 of 371 taken bench poses sit under 10 deg of margin (247-249 held out). The feel study
   (`docs/research/fold-stop-feel.md`, this stop placement under the earlier phi law) found:
   - no jam;
   - 0.47-2.1 mJ per J2 stop contact;
   - 0.20 N of bearing friction at the cuff.
3. **K is the singularity guard.** On forced poses the plain dyad is 11.4-11.6 deg past its fold, and the margin holds
   only because K opens.
   - The re-measured spring demand is at most 0.044 N.m, against a 0.08 N.m preload (1.6-1.8x).
   - A sticky K (10 mN.m seals at 2 g) would drive J2 into its stop near-singular.
4. **Untested and unscored.**
   - The folded stop never engages.
   - The contact-aware fill checks nodes only, not the 2-deg steps between them.
   - Hub K's 18.25 mm crown is not scored by in-band (the convention for every design). It is at least 4.08 mm from
     the skin overhead.
   - The dowels need the L1 CAD strength check: about 770 N at 6 N.m about GH.
5. **Cost.**
   - Four revolutes (J1, K, J2, J3), with K sensed: 4 active DOF in the user's count, at the cap, not the preferred 3.
   - Complexity 33 against H1's 19.5 (tools/simplicity.py v1). The re-measure lens' "H1 2.75" is a misreading; the
     tool gives 19.5.
   - K adds no overhead reach: every taken pose at elevation 140 or more is in state A.
   - BDp is 5.79 gap points short of the golden 13.75.
6. **Fit-to-wear loss** is 5.2-6.8 points.

## Verdict

**CONFIRMED.** Neither lens refutes it, and every judge cross-check passes.

| | BDp verified (buildable stops) | BDp at the rule's nominal | H1 (same harness) | gain over H1 |
|---|---|---|---|---|
| bench gap | **19.54** (score 92.89) | 19.06 (93.07) | 27.20 | 7.66 |
| reach / follow / in-band14 / contact | 0.7222 / 1.0 / 0.8931 / 0.0107 | 0.725 / 1.0 / 0.8951 / 0.0107 | 0.658 / 0.964 / 0.895 / 0.026 | |
| near-touch | 26.44 | 26.15 | 31.75 | 5.31 |
| held out | **24.18** (near-touch 28.86) | 23.24 (28.31) | 31.39 (34.66) | 7.21 |
| min own-state J1-J3 margin | 5.0-5.5 as built (5.525 at 5.5) | 5.007 | 5.32 | |

It beats H1 under every protocol measured:
- in-sample fit-60, the same protocol as H1's 27.20;
- held out;
- the polish protocol, where H1 is 24.48.

So it becomes the **verified leader**, with the build conditions in the row (`v_kitrule_build_conditions`).

## Next

1. The 2-fold cross-fit final polish of BDp on the near-touch objective, with the stops as design variables: the J2
   slot at 5.0 +tol / -0, and stop B at the 5.0 cut. It must lift hub 2 off the overhead pinch.
2. The gen-4 L1 CAD and stills, with stop B at 34.47, the 0.015 N.m/rad strip, the dowel strength check and the stop
   tolerance from the link compliance.
3. The user's ruling on a sensed 4th joint (MVP1 needs a 4th encoder).
4. The round-6 cam-stop-knuckle lens, which drives K from q2 with no K sensor: the same fold relief at 3 active DOF.
