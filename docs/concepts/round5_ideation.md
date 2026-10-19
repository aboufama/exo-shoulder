# Round 5 ideation: judge and red team (2026-10-16 ~07:12 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275), tools/concept_bench.py); gap 0 is the real
target. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered with exactly 3 active DOF.

Reference: verified leaders skin-normal-3r-pin-knee k4598 30.35 (complexity 21.5) and spine-parked-j2-3r k7008 34.29
(complexity 0), both on Bench(110,360) exact, frozen. Their limiter is the J2 fold: the window is 42-102 deg, but the
workspace needs th = angle(J1, J3) of 26-140 deg.

## Red-team measurements made by the judge

Scripts are in the session scratchpad `judge5/`. They re-read the proposers' own raw files and the bench poses.

1. **The min-arc knuckle proxy counts penetrating poses as merely unreached. The bench also counts them as contact.**
   `rt_minarc.py` re-scores the proposer's own per-ray K3 requirements (`k4r_lens/allmem_110_360_*.npz`) on
   Bench(110,360). Levels are clip p95 + 4 mm, as the proposer used.
   - In the bench (`CB.report`), a pose that closes but penetrates the skin counts twice: it is not reached, and it adds
     to the contact share at 100 x share.
   - The proposer's proxy only drops such poses.

   | design (proxy rays) | kinematic | reach | follow | in-band | contact | gap as proposed | gap with contact |
   |---|---|---|---|---|---|---|---|
   | pin-knee 3R (verified 30.35) | 0.631 | 0.617 | 1.000 | 0.916 | 0.015 | 28.3 | **29.8** |
   | spine-parked 3R (verified 34.29) | 0.611 | 0.606 | 0.955 | 0.917 | 0.006 | 29.4 | 30.1 |
   | minarc on the leader's own seats | 0.978 | 0.814 | 0.945 | 0.853 | 0.141 | 13.8 | 27.8 |
   | **minarc, re-seated pin-knee seats** | 0.972 | 0.825 | 0.973 | 0.927 | 0.122 | 7.5 | **19.7** |
   | minarc, re-seated spine seats | 0.981 | 0.828 | 0.955 | 0.796 | 0.130 | 17.6 | 30.6 |

   - The contact-aware column reproduces the pin knee's verified 30.35, so the re-score is calibrated.
   - At the re-seated pin-knee seats, 62 workspace poses are forced (42 stretched, 20 folded). 32 of them penetrate at
     clip-fitted levels (18 stretched, 14 folded).
   - On the forced poses the hub-2 ray needs p50 58 / p90 101 mm, against a clip p95 of 57.
   - Raising the levels instead (a q-quantile over all closing poses) gives in-band 0.53 at q 0.97 on this ray proxy.
   - **Verdict:** the knuckle is real and its kinematics hold, but the honest expectation is a gap of **18-24**
     (score 91-93.5), not 10-14. That still crosses the 90 line by the widest margin of any candidate. The CMA's lever
     is stop B and the phi stops: trading the penetrating forced poses against reach.

2. **The short-a2 arc-slide kinematics reproduce exactly.** `rt_a2.py` (Bench(110,360), seed S1):

   | margin | 3R ws / clip | relay ws / clip | overhead (relay / 3R) | across-body | poses where the slide moves (ws / clip) | slide p95 |
   |---|---|---|---|---|---|---|
   | 10 | 0.664 / 0.873 | 0.764 / 0.955 | 0.50 / 0.46 | 0.31 | 36 / 9 | 13.0 deg |
   | 5 | 0.725 / 0.891 | 0.794 / 0.955 | 0.61 / 0.46 | 0.32 | 25 / 7 | 12.5 deg |

   - th at these seats has 5 / 50 / 95 % = 19.7 / 58.8 / 140.8 deg.
   - The widened window stops at 88.7 deg, so 81 workspace poses stay above it.
   - The reach term alone therefore keeps the gap at **>= ~13.6**. This design crosses 90 but cannot reach 95 by
     itself.
   - Its proxy already fits levels on every pose it takes (q 0.97) and counts contact, so it is kit-like. It is
     calibrated 3-5 points optimistic on k7008. Expected verified gap **20-23**.

3. **The two relay sides agree once contact is counted.**
   - The reseat lens found that a relay on the scapula-side arc a1 drags hub 2 off its quiet circle (hub 2 in band
     0.05-0.24).
   - The keemink lens claimed the same lever keeps in-band at 0.92.
   - Both are right about different poses. In-band is scored on clip frames, which the knuckle never moves. The cost
     lands on the forced workspace poses, as the contact in item 1.
   - So the a1 knuckle buys more reach (0.97 kinematic), and the a2 slide pays less contact on the poses it gains
     (0 by its proxy).

4. **The force-closed relay is not the stop-relay-rocker failure.**
   - stop-relay-rocker-3r was refuted because its relay entries sat at the rocker sub-chain's own fold (static islands,
     0 relay poses taken with continuity).
   - In the min-arc knuckle, J2 is locked on its stop while forced. The moving chain is then J1-K-J3, whose elbow
     angle psi stays at 58-120 deg, never near straight.
   - In the a2 slide, J2 is also locked on its stop. The slide axis n is perpendicular to the plane through J2 and J3,
     and J1 is near that plane, so turning the slide changes th about 1 deg per deg.
   - The proposer's flood fill counted 2 jams in 431 relay edges.
   - Both designs must still pass the verifier's flood fill and dense K2 before any claim.

## Verdicts

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | **minarc-stop-knuckle-4r** | **PICK 1** | Highest measured kinematic ceiling (0.972). The re-scored proxy is 19.7 against the leader's 29.8 on the same ruler. Components: O20 hubs, a clock spring and dowel stops. The spare is determined by a one-sided minimum-energy preload on stops (single-valued in the arm pose). Complexity ~14, 0 passive translations. Expected gap 18-24. |
| 2 | **short-a2-arc-slide-3r** | **PICK 2** | Its kinematic claim is reproduced exactly, and its proxy is kit-like with 0 contact on gained poses. The arc slot is a rotation about GH, built as a machined curved slot with iglidur bushings. Complexity ~13.5, 0 passive translations. Expected 20-23: the most confident 90 crosser, but the reach floor at 13.6 caps it below 95. |
| 3 | pin-knee-minarc-knuckle-4r | MERGED into pick 1 as variant B | It is the same lever on the verified pin-knee chain. Complexity 35 (3 sensed passives + a spring), and it carries the same forced-pose contact as pick 1. Run it only if variant A's in-band falls below 0.88. |
| 4 | rssr-scheduled-knuckle-4r | NOT PICKED (rank 3) | Buildable (igubal rod ends, a pins-only loop) and determined by geometry. But its ray in-band proxy is 0.79 against 0.92, because the cos-U schedule is never flat. It adds a rod layer over link 1b, and complexity is 19-25.5. It is also exposed to the same forced-pose contact as pick 1. Revisit if pick 1's spring fails the MuJoCo sag check. |
| 5 | handler-arc-track-j1-3r | NOT PICKED (rank 4) | A J1 rocker realised as a scapula-fixed arc track, so it needs no pivot hub. Its own estimate is ~27 after calibration, which lands at the 90 line at best. Hub 1 rises 5 mm on the carriage. Contact appears on 7-13 % of gained poses. Lowest expected gain of the reach levers. |
| 6 | fossa-pivot-rocker-3r | MERGED into stop-relay-rocker-3r (refuted; "do not pick again") | It re-seats the refuted rocker with a long arm and the m_sw >= 10 rule: connected 0.769, est. 22.44. That is new evidence against round 4's inert-rocker verdict, but 20 % of gained poses touch, and the round-4 continuity CMA converged to 0 relay poses. Recorded here; the verifier should reproduce the jam count before the id is reopened. |
| 7 | groove-knee-link1-3r | REJECTED (measured: metric dilution) | The proposer's own red team shows reach only +0.016 over the same-seat plain 3R. About 7.5 of its 9.6 points come from extra in-band metal (tail, roller, groove plate) diluting the sample share. The groove pressure angle sits at its 45 deg cap (p95 44.7). Its components (MR85ZZ cam follower in an iglidur groove) are real; the gain is not. |
| 8 | rod-knee-link1-3r | REJECTED (measured: worse than plain) | Proxy 41.52 against plain spine-parked at 33.62 on the same code. With honest clearances and full crank rotation it gives 0 valid of 400. The proposer files it as a control expected to be refuted. Its overconstrained spherical loop would also need a spherical bearing. |
| 9 | humeral-groove-knee-3r | REJECTED (measured: worse than plain) | Realised at 35.3 against plain 33.6. The arm-side groove plate sits on deltoid skin that bunches in the humerus frame (in band 0.63-0.70). This closes the mirror direction. |

## Ranking

Ranked by (expected gap reduction vs the pin knee's 30.35) x (confidence) x (buildability):

1. minarc-stop-knuckle-4r: about -6 to -12, medium confidence (proxy re-scored by the judge), 0 translations, complexity ~14.
2. short-a2-arc-slide-3r: about -7 to -10, medium-high confidence (kinematics reproduced, kit-like proxy), 0 translations, complexity ~13.5.
3. rssr-scheduled-knuckle-4r: about -6 to -14 kinematically, low confidence on band, complexity 19-25.5.
4. handler-arc-track-j1-3r: about -3, medium confidence, complexity 13.5.

Both picks are simpler than the pin knee (21.5). Both are force-closed relays on J2 hard stops. The rssr loop is the
geometric fallback if a spring relay fails the dynamics check.

## What happens next

- The round-5 screen models both picks on tools/concept_kit.py: fit fast, then CMA on the farm, then frozen
  Bench(110,360) exact through an independent verifier. Report margin 10 and 5, and contact on forced poses separately.
- If pick 1 lands at gap <= 27.5 verified, it becomes the generation winner and goes to the final polish and L2 CAD.
- If both stall above 24, the next lever is pick 1's seats searched with an objective that counts contact. Its
  32 penetrating forced poses are the measured gap between proxy 7.5 and contact-aware 19.7. Do not stack both relays:
  that is 2 passives on 3 active joints, outside the user's 3-DOF goal.
