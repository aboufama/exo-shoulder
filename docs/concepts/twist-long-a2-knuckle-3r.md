# twist-long-a2-knuckle-3r - J3 re-seat for reach on the lead's knuckle drive

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the J3 seat as a *window-centring*
   problem, not a parameter: the fold window is `[|a1A - a2| + 5, a1max + a2 - 5]` and the overhead th set is
   `angle(J1, humerus) +- wd_eff`; so solve for the J3 axis that puts the overhead th set inside the window *first*
   (closed form per pose), then check whether hub 3 / L2 can park there. Re-parametrise the search in the designer's
   variables (effective J3 axis, a2, a1A at stop A) instead of the seat angles, so CMA moves along the lever and not
   across it (az2 / el2 are derived from `circ_int(u1, a1A, d3_rest, a2)`). Count the folded wall a longer a2 raises
   (|a1A - a2| + 5) as a cost from the start, and attribute every lost pose to its wall.
2. **Rawest material.** The posed skin itself through the bench's signed distance (grid cache / exact libigl), the
   motion clips and workspace poses of `tools/concept_bench.py` (Bench(60,160) fit, Bench(110,360) exact for the claim,
   held-out clips never touched), the rest-pose skin normal at each seat (`seat()` on the posed mesh), the proposer's
   proxy rows (scratchpad r8wg ev3_*.jsonl) only as the hypothesis to refute.
3. **Methods / tools.** The verified lead's model module (frontload-lobe-stopb-knuckle-3r.py: knuckle K, seg law,
   rod drive with the verifier's corrected cap metal, pin knee, O20 stacks, kit fold rule 5 deg, near-touch objective)
   with a seat transform; the law-only kill gate (drive metal off) through the model's own IK on Bench(110,360);
   farm LHS + CMA-ES (tools/cloud_run.py) on Bench(60,160) fast near-touch; frozen exact wear on Bench(110,360) with
   the per-cause and per-part attribution; flood fill on the worn model.
4. **What, other than me, shows the number is right.** The bench (outside judge), the frozen exact wear on
   Bench(110,360) (not the fit bench), the round's adversarial verifier re-running the claim from the row's params, and a
   red-team pose list (overhead axial -135 / 0 families, across-the-body, behind-the-back, the knee window extremes).

## Model

`docs/concepts/models/twist-long-a2-knuckle-3r.py` = the verified lead's module (frontload-lobe-stopb-knuckle-3r: knuckle K
slaved by the hub-2 rim lobe -> rocker -> O3 rod -> horn on K's cap, seg law, pin knee, O20 stacks, kit fold rule 5 deg,
near-touch objective) with a seat transform in the designer's variables:

* `e3d / e3a` = the EFFECTIVE J3 axis in the humerus frame (wdir: d from the down-the-arm axis, a 0 lateral, +90
  anterior). The lead's effective axis is wdir(76.3, -6.8) (its seat ray wdir(63.5, -10.6) tilted b3 0.38 = 34.9 deg
  toward the skin normal). With b3 > 0 the seat ray is solved on the rest skin so the tilted axis equals (e3d, e3a)
  (residual <= 0.2 deg except at wdir(76, 15): 1.8 deg).
* `a1t / a2t` = the J1-J2 angle at K stop A and a2; J2's GH ray is `circ_int(u1, a1t, d3_rest, a2t)` on the branch nearest
  the lead's J2 seat. Without `a2t` J2 keeps its own `az2 / el2` (the "J2 parked" streams).
* the K dyad bk1 / bk2 / a1max (a1max clamped <= bk1 + bk2 - 5 by the lead's code), seg law to t_end 100.

The spec's improvement (said here): the proposer's proxy put hub 3 ON the effective axis ray (b3 = 0). The real lead
tilts its J3 axis 35 deg toward the skin normal (the hub sits 13 deg further down the arm than its axis ray), so b3 is a
free variable here, and its two ends behave differently (below).

Claim harness: `docs/concepts/models/twist-long-a2-knuckle-3r_claim.py` maps the variables with the model's own prep() and
wears the frozen shape through the lead's INDEPENDENT verifier (`docs/concepts/verify/frontload-lobe-stopb-knuckle-3r.py`,
CorrModel: horn plate on K's cap top, rod clear of the 6 mm spring cap, ROD-hubK per pose), Bench(110,360) exact.

## Law-only kill gate (drive metal off, the model's own IK on Bench(110,360) workspace poses)

Kinematic reach = law + K + fold + knee + |s_n| <= R_tol on all 360 workspace poses, after a fit on Bench(60,160) fast
(the lead's own IK gives 0.742 here; the proposer's window model said 0.761 - their +0.03 target becomes >= 0.772).
"fast" = Bench(60,160) fast near-touch gap with the drive metal off (lead 11.16; 15.57 with its rod).

| config (bk1/bk2/a1max) | kin360 | overhead | lost: folded / stretched / law+m3e / knee | fast (law-only) | hub 2 / hub 3 / L2 in band |
|---|---|---|---|---|---|
| lead (30.1/37.6/61.7) | 0.742 | 10/28 | 23 / 50 / 13 / 7 | 11.16 | 0.99 / 0.60 / 0.77 |
| lead seats, wide dyad (30/44/69) | 0.772 | 11/28 | 23 / 43 / 8 / 8 | 13.14 | 0.99 / 0.58 / 0.75 |
| seed A wdir(70,15) b3 0, a2 66, wide | **0.814** | **17/28** | 27 / 25 / 15 / 0 | 30.67 | 0.68 / 0.35 / 0.62 |
| seed A b3 0.38 | 0.775 | 8/28 | 27 / 25 / 15 / 14 | 23.82 | 0.69 / 0.59 / 0.49 |
| seed A' wdir(76,15) b3 0 | 0.808 | 16/28 | 30 / 24 / 15 / 0 | knee-E collides on every pose | - |
| seed A' b3 0.38 | 0.789 | 10/28 | 31 / 24 / 14 / 7 | 66.88 | 0.73 / 0.53 / 0.52 |
| seed B wdir(82,30) b3 0, a2 58 | 0.817 | 19/28 | 26 / 30 / 10 / 0 | knee-E every pose | - |
| seed B wdir(88,30) b3 0 | **0.825** | **21/28** | 26 / 30 / 7 / 0 | knee-E every pose | - |
| seed B b3 0.38 | 0.811 | 19/28 | 28 / 30 / 10 / 0 | 83.86 | 0.89 / 0.52 / 0.80 (E 0.67) |
| twist only: A b3 0.38, a2 66, LEAD dyad | 0.747 | 8/28 | 27 / 37 / 15 / 12 | 19.85 | 0.79 / 0.61 / 0.55 |
| a2 66 only (lead axis, lead dyad) | 0.747 | 9/28 | 27 / 46 / 12 / 6 | 17.11 | 0.99 / 0.59 / 0.78 |
| J2 parked at the lead's seat, wdir(72,2) b3 0.22, wide (a2 -> 69.4) | 0.808 | 14/28 | 29 / 25 / 15 / 0 | 23.26 (contact 0.063) | 0.98 / 0.58 / 0.82 |
| J2 parked, wdir(70,15) b3 0.2, wide (a2 -> 77.2) | 0.814 | 16/28 | 44 / 11 / 12 / 0 | 37.01 | 0.97 / 0.44 / 0.66 |

Gate verdict: KINEMATICS PASS (0.81-0.83 vs >= 0.772; overhead 14-21/28 vs the lead's 10), PARKING FAIL un-refit: when J2's
seat follows the J3 twist (circ_int) hub 2 drops to 0.68-0.79 in band and L2 to 0.49-0.62; when J2 stays parked, a2 grows
to 69-77 and link 2 / hub 3 run over the deltoid (skin contact 0.06-0.07). The b3 tilt trades knee drift (knee losses
0 -> 7-14) for hub-3 height (0.35 -> 0.59). Lever attribution: the wide K dyad alone +0.030, the twist + a2 alone +0.005,
together +0.072 (b3 0): the levers only work jointly (the twist moves the overhead th set toward the stretched wall
a1max + a2 - 5, which only the wider dyad has moved out of the way).

## Search (farm, Bench(60,160) fast, near-touch objective, rod drive metal ON)

LHS 192 over the spec's ranges (e3d 66-92, e3a -8..38, b3 0-0.5, a2 56-70, a1A 33-40, bk1 28-34, bk2 38-48, a1max 62-75,
knee, law, J1 seat): best 21.77 (e3 wdir(72, 2), a2 64, bk2 44.8). Then 13 CMA-ES streams (popsize 8, 2 processes each,
4869 configurations in all, every one in docs/concepts/sweeps/twist-long-a2-knuckle-3r.json):

| stream | start | best fast | reach / ib14 / contact | where it ended (effective J3 axis, a2, bk1/bk2/a1max) | gate (gain 2nd half / last third / top-5 spread, score pts) |
|---|---|---|---|---|---|
| A1 | seed A wdir(70,15) b3 0.2 a2 66 | 17.44 | 0.794 / 0.853 / 0.021 | wdir(70.9, **+0.1**), 66.2, 28.6/41.7/64.1 | 0.99 / 0.36 / 0.20 |
| A2 | wdir(72,10) b3 0.38 a2 64 | 17.10 | 0.800 / 0.855 / 0.026 | wdir(73.6, **-6.0**), 63.0, 31.6/42.0/68.6 | 0.55 / 0.51 / 0.31 |
| A3 | seed A b3 0 | 17.94 | 0.806 / 0.846 / 0.031 | wdir(72.3, **-4.0**), 65.1, 30.0/42.1/65.2 | 0.05 / 0.02 / 0.05 |
| B1 | seed B wdir(84,28) a2 58 | 20.70 | 0.825 / 0.794 / 0.026 | wdir(73.7, **-0.0**), 58.8, 31.6/50.8/72.1 | 6.11 / 4.52 / 0.56 (walking back) |
| C0 | lead's axis, wide dyad 30/44/69 | 17.29 | 0.800 / 0.853 / 0.026 | wdir(74.4, -1.1), 61.0, 30.5/45.2/70.7 | 0.16 / 0.16 / 0.16 |
| L1-L3 | LHS top 3 | 18.17 / **16.74** / 16.99 | L2: 0.788 / 0.856 / 0.011 | L2 wdir(70.4, -1.4), 64.5, 31.9/42.8/69.5; **L3 walked back to the lead's seats** (wdir(75.6,-5.4), a2 62.1, 28.3/38.4/61.7) | all < 0.5 |
| P1, P2 | J2 parked at the lead's seat, twisted J3 | 17.99 / 17.08 | P2: 0.800 / 0.835 / 0.005 | P2 wdir(80.3, **-7.8**) from (70, +15) | 0.00 / 0.00 / 0.05-0.46 |
| R1 | restart from A2 | **16.74** | 0.800 / 0.854 / 0.021 | wdir(74.5, -3.8), 61.8, 30.6/42.2/67.8 | 0.13 / 0.13 / 0.17 |
| T8 | twist FIXED at a = +8 | 18.94 | 0.819 / 0.831 / 0.005 | wdir(70.8, 8), 62.8, 31.7/39.5/66.2 | 0.01 / 0.00 / 0.07 |
| T15 | twist FIXED at a = +15 | 24.15 | 0.800 / 0.803 / 0.011 | wdir(69.2, 15), 68.1, 28.4/40.5/63.9 | 0.00 / 0.00 / 0.36 |

Combined gate over all 4869: gain over the 2nd half 0.13, last third 0.00, top-5 spread 0.13 score points: CONVERGED at
16.74 fast (the lead: 15.57 after 9096 configurations). Every free stream that started twisted anterior (+10 to +28 deg)
walked the twist back to -8..+2 deg (the lead sits at -6.8); with the twist held fixed the converged optimum costs
+2.2 fast at +8 deg and +7.4 at +15 deg.

## Frozen exact claims (fit Bench(60,160) fast, worn on Bench(110,360) exact through the lead's verifier CorrModel)

| config | fit (corr metal) | **frozen** | near-touch 1 mm | reach | follow | ib14 | contact | overhead | lost: fold / slide / contact | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| lead (verified, same harness) | 15.57 | **22.82** | 24.46 | 0.728 | 1.000 | 0.855 | 0.011 | 8/28 | 86 / 7 / 4 | 0.30 |
| C0 (lead axis, wide dyad 30.5/45.2/70.7) | 17.38 | **24.46** | 27.70 | 0.733 | 0.955 | 0.851 | 0.029 | 8/28 | 76 / 12 / 11 | 0.03 |
| A2 (wdir(73.6,-6.0), a2 63.0) | 17.20 | 25.52 | 27.19 | 0.731 | 0.964 | 0.851 | 0.037 | 7/28 | 75 / 11 / 14 | 0.18 |
| R1 = best fast 16.74 (wdir(74.5,-3.8), a2 61.8) | 16.84 | 25.70 | 28.38 | 0.728 | 0.955 | 0.852 | 0.037 | 7/28 | 79 / 10 / 14 | 0.40 |
| L2 = best fast 16.74 (wdir(70.4,-1.4), a2 64.5) | 16.83 | 25.85 | 27.49 | 0.722 | 0.936 | 0.857 | 0.024 | 7/28 | 85 / 12 / 9 | 0.45 |
| A1 (wdir(70.9,+0.1), a2 66.2) | 17.54 | 26.16 | 27.25 | 0.722 | 0.936 | 0.854 | 0.024 | 7/28 | 84 / 11 / 9 | 0.43 |
| T8 (twist fixed +8, converged) | 19.03 | 27.54 | 30.82 | **0.742** | 0.918 | 0.828 | 0.013 | **9/28** | 82 / 14 / 5 | 0.27 |
| A3 point at +8.5 | 23.17 | 31.01 | 33.73 | 0.739 | 0.918 | 0.807 | 0.024 | 9/28 | 83 / 5 / 9 | 0.04 |
| LHS best (wdir(72,2)) | 21.86 | 28.55 | 30.71 | 0.739 | 0.936 | 0.816 | 0.026 | - | 86 / 0 / 10 | - |

Held out (A2): 28.44 frozen (the lead 26.75). Flood fill on the worn model (A2, L2): full grid 0 dropped (static = connected).
Raw outputs: .cache/claim_twist/*.json (farm) and the scratchpad *_bench_local.json (local, same code).

## Red team (own best)

* **The optimistic number** is every fast number: 16.7-17.5 fast became 24.5-26.2 frozen (+7.7 to +9.0), worse than the
  lead's own +7.25; the twisted configs lose the most in band (T8 ib14 0.828, L2 0.657 in band).
* **The point that pinches**: C0's metal comes to 0.03 mm of the skin on ws plane 60 / elev 150 / axial -105 (overhead) and
  0.12 mm at plane -75 / elev 45 / axial 120; near-touch 1 mm costs +3.24, 2 mm 37.84 (lead 44.08 - the wide dyad does not
  make it worse at 2 mm). The rod post grows from 17 to 20.5 mm to clear K's cap (rod 43 mm long, rocker 0.77 in band).
* **The pose that jams**: none jams (closure residual <= 0.015 deg, flood fill drops 0), but the law ends at lift-off with
  m3e 0.0 at its end (dK law 77 deg, taken <= 47.8) - the stretched poses beyond th 130 are not reachable by the drive.
* **What the wide dyad really buys**: 10 fold poses back (C0 fold 76 vs 86), all of them lost again to contact (11 vs 4),
  knee slide (12 vs 7) and two clip frames (follow 0.955 vs 1.000): reach 0.733 vs 0.728. The next wall behind the
  stretched fold wall is skin contact on the same overhead / stretched poses.

## Verdict: DEAD (converged, measured)

The J3 twist is refuted: every free CMA stream that started at +10..+30 deg anterior walked it back to -8..+2 deg (the
lead sits at -6.8), an LHS start converged onto the lead's own seats, and with the twist held at +8 / +15 the converged
optimum is +2.2 / +7.4 fast worse and 27.54 frozen (+4.7 over the lead) despite the highest frozen reach of the set (0.742,
overhead 9/28). The wide K dyad (bk2 42-45, a1max 68-71) is the only part the search keeps, and frozen it buys nothing
(best 24.46 vs 22.82). Converged gate over 4869 configurations: 0.13 / 0.00 / 0.13 score points.

Limiter, measured: parking, not kinematics. The law-only kill gate shows a real +0.07 kinematic reach (0.814-0.825 vs
0.742) at b3 0, but (a) a J3 twist moves J2's GH ray lateral / down (az2 57, el2 38) where hub 2 and link 2 lift out of
the band (0.68 / 0.49-0.62); (b) keeping J2 parked turns the twist into a2 69-77, i.e. link 2 / hub 3 over the deltoid
(skin contact 0.06-0.07); (c) the b3 tilt that keeps hub 3 low (0.35 -> 0.59 in band) costs 7-14 knee poses. Each
recovered fold pose is re-lost to skin contact or knee slide on the same overhead / stretched poses.

## New knowledge

* A fold-window lever measured only kinematically (window arithmetic, parking proxy) over-predicts by the parking term:
  here +0.07 kinematic reach -> +0.005 frozen reach. The proxy's hub-2 parking (0.96) did not see that the J2 seat
  follows the J3 seat through circ_int.
* The lead's J3 effective axis (wdir(76, -7), tilt 35 deg toward the skin normal) is a local optimum that independent
  CMA starts return to; the window cannot be re-centred from the J3 side within the 1 cm band.
* The wide K dyad converts ~10 stretched-fold losses into contact / knee-slide losses: the stretched wall and the
  skin-contact wall coincide on the overhead poses, so moving the fold wall alone cannot buy reach. The next lever must
  lower the metal on those poses (drive metal in band, sidecar) rather than widen the window.

## Audit (2026-10-16 ~20:30 UTC, independent re-measurement)

The death stands. The design is behind the verified lead, though well ahead of the 3R champion.

- **Convergence gate** (re-computed on the 4869 CMA entries only): the best gained 0.13 score points over the second half and 0.00 over the last third; the top-5 gaps are 16.74-17.10. Converged. The sweep's 11.16 / 13.14 entries are `seed-lawonly` (drive metal off), so they are not buildable designs.
- **Ranges**: e3d 61-92, e3a -15..+38, b3 0-0.6, a2t 52-71, bk2 35-54 and a1max 58-78 were all explored, and the best configs sit inside the bounds. No obvious region was missed.
- **Conventions**: `prep({})` returns the lead's seats (the effective J3 axis round-trips to (76.26, -6.78)). The b3 fixed-point and the circ_int branch take the branch nearest the lead's J2 seat. No modelling bug was found.
- **Re-measured** (claim harness, lead verifier CorrModel, `CB_EXACT=1`, Bench(110,360) frozen):

| config | frozen gap | reach | follow | ib14 | contact | near-touch 1 mm | min metal | why lost (fold/slide/contact/parts) |
|---|---|---|---|---|---|---|---|---|
| C0 (best frozen) | **24.46** (91.10) | 0.733 | 0.955 | 0.851 | 0.029 | 27.70 | 0.03 mm | 76 / 12 / 11 / 2 |
| lead, same harness | **22.82** (91.70) | 0.728 | 1.000 | 0.855 | 0.011 | 24.46 | 0.30 mm | 86 / 7 / 4 / 1 |

Measured reason in one line: widening the window wins back 10 fold poses, and skin contact (+7), knee slide (+5) and clip follow (-0.045) lose them again on the same overhead and stretched poses, so the design ends 1.64 behind the lead frozen. Next: lower the metal on those poses (put the drive metal in band, or lower hub 3 / L2).
