# minarc-stop-knuckle-4r BDp: the judge's ruling (2026-10-16)

**Ruling: CONFIRMED. BDp is the new VERIFIED LEADER: 19.06 frozen exact on Bench(110,360) (score 93.07), held out 23.24
against H1's 31.39.**

**Claim under test.** `rows/minarc-stop-knuckle-4r.json` `kitrule_*`. Config BDp is:
- variant B: the pin knee plus a spring knuckle K in link 1;
- the BD seats;
- both J2 stops at the 5-deg J1-J3 margin, as a physical dowel in a q2 slot (-24.98 .. 100.84 deg);
- hub K's cap 6 mm taller.

**Rule.** The design is CONFIRMED only if neither lens refutes it. The verified number is the worst credible
re-measured frozen exact Bench(110,360) gap at margin 5 with the continuity rule, plus any priced mechanism issue.

**Sources.**
- Judge script: `minarc-bdp-judge.py`. It reads the lenses' raw JSON, never their prose, and recomputes every gap from
  its components with the bench's own `gap_of`.
- Its output: `minarc-bdp-judge/ruling.json`.
- The judge's own farm runs: `minarc-bdp-judge/`.

## The two lenses

| lens | harness | bench | held out | min J1-J3 margin, own state | continuity | refuted |
|---|---|---|---|---|---|---|
| re-measure (`minarc-bdp-remeasure.md`) | its own: frozen hand-over by `__dict__` diff, frame-based checks, its own flood fills | **19.06**, near-touch 26.15 | **23.24**, near-touch 28.31 | 5.015 / 5.007 | 1041/1041 kinematic, 1014/1014 contact-aware, 0 dropped | no |
| buildability + red team (`minarc-bdp-buildability.md`) | the claim's `run()` path, plus an independent K / q2 closure and spring-equilibrium scan | **19.06** | **23.24** | 5.01 | continuity file identical to the committed one | no |

**Judge cross-check** (`ruling.json` `checks`, all true):
- Each gap recomputed from (in-band14, follow, reach, contact) equals the reported one.
- The two lenses agree to the digit on the bench and held out: lens 2's raw `.cache/minarc_bdp_build/pinch_{bench,held}.json` `model_run`.
- No taken pose is under 5 deg.
- 0 poses are dropped by continuity.
- BDp beats H1 on both sets.

## Priced mechanism issues

Both lenses' issues are folded in. None changes the number.

| issue | lens | price |
|---|---|---|
| K stop B as modelled (dK 62.83) engages at an effective-dyad margin of 2.74 deg (th 122.2); move it to dK 34.5 | buildability | 0.00: every taken pose has dK <= 34.29 |
| Clock spring at 0.03 N.m/rad reaches 1505 MPa at stop B; spec <= 0.015 N.m/rad, +C1900, strip >= 145 mm | buildability | 0.00 |
| The stops sit exactly at the rule (min margin 5.007); a slot cut long breaks it | re-measure | **priced below as a build condition** |

### Stop tolerance (judge's measurement)

A stop that must engage at 5 deg or more is drawn with a unilateral tolerance: 5.0 +0.5 / -0 deg of J1-J3 margin.
- At the stop, q2 turns about 3 deg per deg of th: the slot end moves 14.6 deg of q2 between margins 5 and 10.
- So the band is about 1.5 deg of q2, or about 0.2 mm of slot-end position at the dowel's r 7.75 mm.
- That is wide for a milled slot and an h6 dowel. The worst built case has
both stops at 5.5 deg. The judge re-ran the re-measure lens' harness on the farm with `CB_FOLD_MARGIN` 5.5, and 6 for
the slope. These runs move both J2 stops and the all-state rule, and refit the shape at that margin.

TOLERANCE_TABLE

## Issues that stand (disclosed, unpriced)

1. **The pinch.** Hub 2's wall is 0.05 mm from the skin at the overhead raise peak (plane 30, elevation 150, axial -60)
   with K closed.
   - It is the same part and value as the refuted BD. The held-out set repeats the same pose, so it is no independent
     test.
   - It is disclosed in near-touch 26.15 (held out 28.31), which is still better than H1's 31.75 (34.66).
   - This is the first thing the cross-fit polish, on the near-touch objective, must remove.
2. **Near-edge feel.** 99 of 371 taken bench poses sit under 10 deg of margin (247 held out). The feel study
   (`docs/research/fold-stop-feel.md`) found, for this stop placement:
   - no jam;
   - 0.47-2.1 mJ per stop contact;
   - 0.20 N of bearing friction at the cuff.

   The margin-10 reading costs 3.34 points (22.40).
3. **K is the singularity guard.** On forced poses the plain dyad is 11.4-11.6 deg past its fold, and the margin holds
   only because K opens.
   - The re-measured spring demand is at most 0.044 N.m, against a 0.08 N.m preload.
   - A sticky K (10 mN.m seals at 2 g) would drive J2 into its stop near-singular.
4. **Untested and unscored.**
   - The folded stop never engages.
   - The contact-aware fill checks nodes only, not the 2-deg steps between them.
   - Hub K's 18.25 mm crown is not scored by in-band (the convention for every design). It is at least 4.08 mm from
     the skin overhead.
5. **Cost.**
   - Four revolutes (J1, K, J2, J3), with K sensed: 4 active DOF in the user's count, at the cap, not the preferred 3.
   - Complexity 33 against H1's 19.5 (tools/simplicity.py v1). The re-measure lens' "H1 2.75" is a misreading; the
     tool gives 19.5.
   - K adds no overhead reach: every taken pose at elevation 140 or more is in state A.
   - BDp is 5.31 gap points short of the golden 13.75.
6. **Fit-to-wear loss** is 6.8 points (fast 12.25 to frozen exact 19.06).

## Verdict

**CONFIRMED.** Neither lens refutes it, and the judge's cross-checks pass.

| | BDp | H1 (same harness) | gain |
|---|---|---|---|
| verified gap | **19.06** (score 93.07) | 27.20 | 8.14 |
| reach / follow / in-band14 / contact | 0.725 / 1.0 / 0.8951 / 0.0107 | | |
| near-touch | 26.15 | 31.75 | |
| held out | **23.24** (near-touch 28.31) | 31.39 (34.66) | 8.15 |
| min own-state J1-J3 margin | 5.015 (held out 5.007) | | |

It beats H1 under every protocol measured:
- in-sample fit-60, the same protocol as H1's 27.20;
- held out;
- the polish protocol, where H1 is 24.48.

So it becomes the **verified leader**, with the build conditions listed in the row (`v_kitrule_build_conditions`).

## Next

1. The 2-fold cross-fit final polish of BDp on the near-touch objective, with the stops as design variables at 5.0
   +0.5 / -0 deg. It must lift hub 2 off the overhead pinch.
2. The gen-4 L1 CAD and stills, with K stop B at 34.5 deg, the 0.015 N.m/rad strip and the dowel strength check.
3. The user's ruling on a sensed 4th joint (MVP1 needs a 4th encoder).
4. The round-6 cam-stop-knuckle lens, which drives K from q2 with no K sensor: the same fold relief at 3 active DOF.
