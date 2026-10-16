# roller-longdyad-knuckle-3r: the re-cut roller flank on the long K dyad

Round 9, pick 1. The judge sized the lever as the drive stroke: the lead's taken th max is 109.2, which is the RSSR
stroke wall, not stop B. A re-cut flank (dK_lim 56-64) should raise that wall to 117.5-120.2. Complexity 44.0
(lead 49). 3 active DOF, K slaved and never read, 0 passive translations.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Check that the wall is really the drive. On a slaved knuckle, three things end the stretched window: the drive's
     stroke (dK_lim), stop B (a1max), and the J1-J2-J3 dyad margin of the effective first link a1e(dK). The law
     decides that third one: where K sits as q2 grows. A longer flank is worth nothing if the law opens K too slowly to
     keep m3e >= 5. So the gate also logs m3e and the law gain kK per lost pose, not only dK_lim.
   - Treat the flank boss's height over the skin as a design variable from the start. The no-refit wear put the horn on
     the skin on 88 of 89 contact poses.
   - Size the pressure angles against the real K slop.
   - Count the roller's retaining head as metal on the skin side.
2. **The rawest material.**
   - The posed skin through the bench's exact signed distance: the Bench(110,360) poses and the clips.
   - The lead's own IK, per pose: th, dK, a1e, m3e, msub, knee state.
   - Not the judge's wall table. That table assumes a1 is held and the law keeps up, and it is re-derived here.
3. **The methods and tools.**
   - The lead's and the roller-flank model's code, loaded unchanged. The cam is synthesised per 0.25 deg of K, with
     both pressure angles, lift-off, cusp, contact on the lug, and arm / roller / lug clearances.
   - A law-only gate on Bench(110,360) via the fitted design's own IK.
   - A per-part contact split.
   - The farm for the sweep and CMA-ES on the 2 mm near-touch gap.
   - Frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench, and the frozen exact Bench(110,360) wear (plain, 1 mm and 2 mm).
   - The round's verifier harness (docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py style). It re-checks cam
     closure in the world, the roller never inside the lug, and K inside the drive's range.
   - A red-team pose list: overhead axial -135, the far flank end, and the poses at the new wall.

## Verdict (screened 2026-10-16 22:15 UTC)

The lever is **dead**, and the measurement says why. The long-stroke re-cut flank passes the law-only gate: kin360
0.7778, +13 poses. It cannot be parked. Its flank boss sits on the deltoid, and lifting the boss takes the crank out of
band. Every co-fit walks back to the lead's stroke (dK_lim 42-47).

The best co-fit (a short dyad, pressure angles <= 43, the stub head counted) is level with the lead at lower
complexity. It is not a lead change:

| frozen exact Bench(110,360), fit-60 shape | plain | 1 mm | 2 mm | held out | cx |
|---|---|---|---|---|---|
| this row, best config (F2) | **18.67** | 20.30 | **33.10** | 23.73 | 43.75 |
| lead sidecar-longdyad-knuckle-3r (verified) | 18.91 | 20.00 | 34.03 | 22.67 | 49 |

- F2 detail: reach 0.725, follow 1.0, in-band14 0.894, in-band10 0.513, contact 0.005.
- Lost 99 of 360: fold 88, slide 9, contact 2. Overhead 8/28 (fold 14, slide 4, contact 2).
- Fast Bench(60,160): plain 13.19, 1 mm 14.35, 2 mm 16.57 (lead 10.30 / 10.30 / 25.13).
- The plain gain is 0.24 (under one pose) and the 2 mm gain is 0.93. It is worse at 1 mm (+0.30) and held out (+1.06).
- So the 1-point rule is not met. A verifier is worth it only as a complexity Pareto point (cx 43.75 vs 49 at the same
  score).

## What was measured

1. **No-refit wear** (the seed flank g 2.3 / beta -168 / r_c 17.5 at bk2 44 on the lead's seats). Fast plain 154.74,
   follow 0.35, contact 0.47. Per-part split of the 89 contact poses: horn (the flank boss on link 1a) 88, crank and
   roller 8, hub K 3.
2. **Law-only gate** on Bench(110,360), through the fitted design's own IK, with the drive metal not deciding it:

   | cell | dK_lim (PA <= 43) | kin360 | th max taken | overhead |
   |---|---|---|---|---|
   | lead control: bk2 39.24, kK 1.62 | 44.5 | 0.7417 (= the judge's 0.742) | 109.2 | 10/28 |
   | bk2 44, kK 2.4, seed flank | 53.2 | 0.7667 | 115.0 | 11/28 |
   | bk2 46, kK 2.4, flank g 2.1 / beta -165 / r_c 19.5 | 57.5 | **0.7778** | 117.3 | 11/28 |
   | bk2 42, kK 2.6, same flank | 53.5 | 0.7667 | 115.0 | 11/28 |
   | bk2 39.24, kK 2.2, same flank (monotone control) | 48.2 | 0.7556 | 112.2 | 10/28 |
   | bk2 48 | cam fails at rest (PA crank 49.6) | 0.4611 | | |

   - The gate passes, but by one pose: +13 against the +12 needed.
   - The law matters as much as the flank. At kK 1.62 the J1-J2-J3 margin m3e falls under 5 at th 113.3, before any
     drive wall. kK has to rise to 2.4-2.8 so that a1e keeps up with th.
   - The 43-degree pressure-angle rule caps the re-cut flank at **dK 55-57.5**. A 7 x 9 x 6 grid over g / beta / r_c
     found nothing higher. The proposer's 64 was measured at 45 degrees.
   - The 6 workspace poses at th 117.6-123.6 need dK 60-64. No flank under 43 degrees reaches them.
3. **Co-fit, Bench(60,160), 2 mm near-touch objective, farm.** 7236 configurations: a 245-point LHS, then 15 CMA-ES
   streams in 3 rounds.

   | cell (fast 2 mm gap) | free | bk2 42 | bk2 44 | bk2 46 | control bk2 39.24 |
   |---|---|---|---|---|---|
   | lift <= 4 | **15.09** (bk2 38, at the bound) | 18.95 | 21.82 | drive idle | 22.61 |
   | lift <= 8 | 21.14 | 23.23 | 31.91 | 35.88 | |

   - Every free stream drives bk1 and bk2 to their LOWER bounds (26 / 38), and the flank to dK_lim 42-47.
   - Lifting the flank boss 5.5-8 mm clears the deltoid, but the crank arm wraps over the boss at lug level + 3 mm.
     Crank in-band falls to 0.48-0.64.
   - Convergence gate on the whole sweep: gain over the second half 0.00, over the last third 0.00, top-5 spread 0.05.
     Converged.

## Red team

- **The pose that jams: none found at the drive.** Over the taken dK the pressure angles are crank <= 8.2 and horn
  <= 43.0. The horn reaches 43.0, the cushion's edge, at the last taken step. The tightest clearances are arm to hub K
  1.14 mm and roller to hub K 2.02 mm. The low arm keeps 15.8 mm from the lug.
- **The point that pinches.** Frozen min metal is 0.07 mm at workspace pose (plane -60, elev 60, axial 105), then
  0.67 mm at (15, 90, 30). Held out, it is 0.33 mm at (150, 15, -180).
- **The optimistic number.** Fast to frozen adds 5.48. Held out adds another 5.06 (the lead adds 3.76).
- **The verified roller-flank row fails the 43-degree rule at rest.** Its crank pressure angle is 44.8, so its 20.08
  sits 1.8 degrees inside the judge's cushion.
- **Workspace in-band (unscored), fit bench, same formula.** 0.825 overall and 0.757 at elevation 90-140, against the
  lead's 0.837 / 0.762. That is slightly below the lead: gaming pattern L2 checked, no hidden gain.

## New knowledge

- **On this lobe, the K stroke is capped by the skin, not by the drive's kinematics.** The RSSR stops at dK 43 (rod
  against hub 2). The flank stops at 42-47 once worn: its boss reaches 30-33 mm off hub K's axis onto the deltoid.
- **Prediction.** Any K drive whose output lives on link 1a more than ~20 mm from K's axis meets the deltoid. The
  drive-stroke lever needs one of two things:
  - an output inside hub K's own footprint (r < ~12 mm, e.g. a cam ground into hub K's cap ring);
  - a second knuckle (twin-K2), which adds stroke without a longer flank.
- **A shorter K dyad parks better than a longer one** (bk1 26, bk2 38), the opposite of the long-dyad premise.
- **The law gain kK, not only the drive wall, sets the stretched wall.** At kK 1.62 the dyad margin m3e < 5 binds at
  th 113.3.

## Files

- Model: docs/concepts/models/roller-longdyad-knuckle-3r.py. Modes: check / split / gate / frozen / held / flood /
  viz.
- Sweep: docs/concepts/sweeps/roller-longdyad-knuckle-3r.json.
- Row: docs/concepts/rows/roller-longdyad-knuckle-3r.json.
- Preview: docs/concepts/viz/concepts/roller-longdyad-knuckle-3r.js.
