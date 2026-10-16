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
