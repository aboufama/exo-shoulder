# Crossed skin tracks with a telescoping swivel

Two tracks shaped to the skin cross at a radial swivel; there are no intermediate links. T_S is fixed to the
scapula handler (a halo around the acromion summit). T_H is fixed to the arm (over the deltoid cap, held by a neck
to BOTTOM's bar). Carriage A runs on T_S (J1, s), carriage B runs on T_H (J3, t), and a thin-section ring bearing
between them (J2, q2) turns about the radial line through the crossing. A passive radial slide inside the swivel
takes up the radius difference of the two tracks at the crossing; the closure sets it. 3 ACTIVE DOF, 1 PASSIVE
(closure-set, cannot sag).

## Deeper-version prompt (answered before modelling)

1. **What would a top mechanism designer do here that the spec does not ask for?**
   - Treat both tracks as curves in their own body frames, and draw the arm track from the crossing locus itself
     (where the J2 pole lands in the humerus frame over the clips), not from a circle chosen first.
   - Make the radial stack the design variable it is. The outer track must clear the inner one everywhere they
     pass over each other, so the outer track is lifted only where an overpass actually happens and hugs the skin
     elsewhere.
   - Take the swivel axis seriously as a line through GH that also pierces the outer rail. Carriage B must hang
     under its rail, and the slide guide sits beside the rail (the spec's 9-13 mm stack is too thin: 4 + bearing +
     4 + rail 5 = 15-19 mm).
   - Check transmission at the crossing: a near-tangent crossing is a jam. The tangent angle is the
     condition number of the 2x2 crossing Jacobian.
2. **Rawest material.**
   - The posed render skin of every bench pose, through B.dist and the K3 ray march. There are no radius
     summaries.
   - The per-cell scapula-frame motion grid in `pipeline/conformal/analysis/skin_motion_map_14.json`. The halo
     plan shape is drawn from it.
   - Every 10 fps frame of the fit clips for continuity and branch choice. The bench samples about every
     sixth frame, which would hide a crossing that jumps.
3. **Methods and tools.**
   - Exact polyline-polyline intersection on the sphere (great-circle segment pairs, vectorised) for the crossing.
   - Branch tracking by the nearest crossing to the previous 10 fps frame.
   - The K3 requirement (vectorised ray march on the fast grid cache) for skin-fitted undersides, with a quantile
     over the closing poses.
   - Slope-limited bogie radii.
   - Interval-overlap collision tests between non-adjacent parts.
   - A sweep that runs a kinematic screen first (cheap, no geometry), then the full bench on the best track
     shapes, then a refinement of stack, quantiles and halo offset, all on Bench(60,160).
4. **What, other than me, shows the number is right?**
   - The common bench: same metric code, poses and skin as the 3R baseline (gap 68.93).
   - The adversarial verifier.
   - A red-team pose list: rest, overhead (elev 160), across the body, behind the back, plus the measured worst
     poses of the best config (the crossing that goes tangent, the frame where the slide runs out, and the pinch
     point with the smallest metal-to-skin distance).

## Result (Bench(60,160), fast grid cache, 179 configurations)

| | gap | reach | follow | in-band 2-14 | in-band 2-10 | contact |
|---|---|---|---|---|---|---|
| **best (k 138)** | **108.8** | 0.456 | 0.467 | **0.759** | 0.391 | 0.019 |
| baseline spherical 3R | 68.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |

**Best configuration.**
- The halo is the scapula-frame parallel at el 35 deg, trimmed to the scapula-safe zone (a 195 deg arc).
- The arm track is a thin loop along the deltoid meridian (a -10, d 60-140; oval(100, -10, 40, 4)), trimmed to a
  95 deg arc. It is held by a 14 x 6 neck to BOTTOM's bar.
- Branch sigma -1, radial stack 11 mm, quantile 0.9 for both tracks, rmax 90 mm. Ti mass is about 86 g.
- The slide uses 0-11 mm. Track radii from GH: halo 56-72 mm, arm track 74-90 mm.
- `python3 docs/concepts/models/crossed-skin-tracks.py check` reproduces it.

**In band per part** (2-14 mm, clip frames taken):

| Part | In band | Mean distance |
|---|---|---|
| Halo T_S | 0.94 | 10.0 mm |
| Carriage A | 0.99 | — |
| Neck | 0.78 | — |
| Arm track T_H | 0.38 | 17.1 mm |
| Carriage B | 0.04 | 20.8 mm |

The in-band-first claim of the spec holds: 0.76 against the baseline's 0.44. A scapula-fixed track on the
acromion cap stays in band almost everywhere. Only the outer track and carriage B, which ride on the swivel stack,
leave the band.

## Measured limiter: kinematic coverage, and nothing taken overhead

- **No elevation above 90 deg is ever taken.** Taken share by elevation band:

  | Elevation | Taken |
  |---|---|
  | 0-30 deg | 0.93 |
  | 30-60 deg | 0.57 |
  | 60-90 deg | 0.37 |
  | 90-120 deg | 0.04 |
  | 120-180 deg | 0.00 |

  Overhead and across-the-body probes have no crossing at all. "No crossing" is 98 of the 220 bench poses.
- **Why the coverage is capped.** Every rigid member fixed to one body frame must stay inside that frame's safe zone,
  where the fitted K3 requirement is at most about 90 mm.
  - The humerus-safe zone, measured on the posed skin with q95 over 220 poses, is one patch over the lateral deltoid:
    d 60-135, a -45..+30. Anterior directions hit the chest in across-body poses, posterior directions hit the back
    in behind-back poses, and the top of the head of the humerus hits the acromion and neck overhead.
  - The spec's seed arm circle needs 200-290 deg of J3-like travel. Fitted rigidly, it sits 180-240 mm from GH
    (sweep k 0-5).
  - Two 1-D tracks of lengths L_S and L_H cross for only a limited set of relative rotations, roughly in
    proportion to L_S x L_H. The humerus patch caps L_H at about 1.6 rad.
- **The safe zones themselves are not the problem.** A per-pose check
  (`python3 docs/concepts/models/crossed-skin-tracks.py overlap`) shows that the humerus-safe patch maps into the scapula-safe zone in
  77-100 % of poses in every elevation band, overhead included: 83 % of poses at elevation 120 deg or more have at
  least 5 % overlap. The overlap region moves (scapula frame az 40-175, el 17-72), and one fixed 1-D halo crossed by
  one 1-D arm track cannot follow it.

## What was tried (the variant that removes each limiter)

| Stage | k | Change | Best gap |
|---|---|---|---|
| coarse | 0-5 | Spec as written: iso-motion halo + arm circle, untrimmed | 209.9 (arm track at 184-224 mm) |
| coarse-rmax | 6-21 | Both tracks trimmed to their safe zones | 224 (arm arc 25-60 deg, almost all poses off track) |
| oval-safe, halo-lowered | 22-56 | Arm track = deltoid oval or thin meridian loop inside the patch; halo lowered | (fit bug, see note) |
| halo-lowered-fitfix | 57-94 | Fit poses limited to on-track crossings | 175.1 |
| refine 1-3 | 95-134 | Quantile, rmax, halo offset, oval centre and size, stack 13 | 149.5 |
| halo-parallel | 135-152 | **Halo drawn from the measured zone overlap** (scapula parallel at el 35-50) | **108.8** |
| parallel-refine | 153-166 | halo el 25/30, oval centre / size / width, q, f1 tilt, stack 13 | 108.8 (stack 13: 108.82, contact 0) |
| overhead-arm | 167-178 | Full loops and a ring around the arm, aimed at overhead | 177-275 (worse: the loops leave the band and still miss overhead) |

Note: k 6-56 fitted the tracks over every kinematically closing pose, including crossings off the trimmed tracks.
That lifted the outer track to 180-230 mm, so those numbers are pessimistic. The fix applies from k 57.

## Red team of the best configuration

- **Jam.** The lowest transmission angle among taken poses is 21.4 deg, at ws pose 77 (plane -45, elev 60, axial 45).
  Below 20 deg the pose is refused as a near-tangent crossing.
- **Pinch.**
  - The halo T_S comes to 0.13 mm from the skin at ws pose 136 (plane 45, elev 75, axial 45).
  - Carriage A comes to 0.5 mm at ws pose 101 (plane 0, elev 90).
  - These are below the grid cache's 0.5-1.5 mm p99 error, so the verifier should re-check them exactly.
- **Jams and refusals.**
  - abd90: neck/swivel interference. The swivel runs into the neck root at the end of the arm track.
  - behind-the-back: off track, the crossing leaves the 95 deg arm arc.
  - across-body and overhead: no crossing.
  - flex90: taken by the kinematics, but its exact-distance probe dips 5.2 mm into the skin, so it would be refused as
    contact.
- **Slide.** 0-11 mm over taken poses. Closure-set, it never sags.

## Verdict

**Dead as a primary morphology. Not worth a GPU sweep.**
- Gap 108.8 is 40 points behind the 3R baseline.
- No overhead pose is taken (0 of 41 at elevation 120 deg or more), and the user's goal puts overhead first.
- The measured cap is structural: the arm-fixed track must stay in a single lateral-deltoid patch, and two 1-D tracks
  fixed to two frames cross for too few relative rotations.

**What survives.**
- A scapula-fixed track on the acromion cap at el about 35 deg is in band 0.94, with mean distance 10 mm.
- A carriage riding on it is in band 0.99.
- A design that needs a scapula-side guide (for example a 3R whose J1 is a track) should copy this halo.

Image: `docs/concepts/img/crossed-skin-tracks.png` (rest and overhead, skin in grey).

## Audit (independent re-check, 2026-10-15)

Verdict: **the death stands** (refuted = false). Measured reason: 98 of the 220 bench poses have no crossing of the two tracks at all, so even with every other check removed the gap stays at about 75 or more, against the baseline's 68.93.

- **Reproduced.** `python3 docs/concepts/models/crossed-skin-tracks.py check` on Bench(60, 160) (fast cache) gives the same numbers: reach 0.4562, follow 0.4667, inband14 0.7585, inband10 0.3907, contact 0.0194, gap 108.8. Refusals: no crossing 98, tangent 3, neck/swivel interference 8, off track 8, contact 2. The 10 fps clip closure share is 0.548.
- **Modelling bug?** None found. I checked the crossing finder against a brute-force minimum distance over 3000 random relative rotations. Of 422 rotations where the curves come within 0.3 deg, it missed 1 (a tangent touch) and returned 0 false crossings. The way the bench poses, frames and skin distance are taken matches the conventions of `tools/concept_baseline.py`.
- **Over-strict check?** The extra checks (transversality 20 deg, 10 fps continuity, the 1 mm interference rule, carriages on track) refuse only 19 poses. The binding refusal is the kinematic one. Suppose every crossing pose were taken in band: reach would be at most about 0.55 and follow at most about 0.55 (clip closure 0.548). That alone is about 75 gap points, before any in-band shortfall.
- **Missed parameter region?** The tracks were not trimmed to the safe zones in k 0-5 (rmax None), and the zones were widened in k 95-108 (rmax 105/120). Neither raised coverage enough: the best untrimmed result was reach 0.34 and follow 0.68, with in-band about 0.00 because the tracks sit 180-240 mm out. Coverage and closeness pull against each other in this topology. A 2-D follower would break that trade-off, and two crossing 1-D tracks cannot.
- **What to keep** (unchanged from the screen): the scapula-fixed halo at el 35 deg (in band 0.94, mean 10 mm) and carriage A (0.99). They are worth reusing as the base stage of a morphology whose second stage follows the meeting point in 2-D.

## Polish (convergence check, 2026-10-15)

**Why.** The 179-try sweep was still climbing (+26.9 points in its second half), so the death at score 60.4 could
have been bad luck in sampling rather than a property of the mechanism.

**Method.** CMA-ES (popsize 8, box-normalised) on 12 continuous parameters: halo_el, the halo's Fourier terms
f1c / f1s / f2c / f2s, the arm oval o_d / o_a / o_A / o_B, the quantiles q / qH, and rmax (80-100). Discrete choices
were fixed (sigma -1, oval arm track, stack 11 = the physical minimum, S_in). Same model, same honesty checks, same
Bench(60,160) fast cache. Round 1: sigma 0.12 from k 138, 154 and 160 (48 tries each). Round 2: sigma 0.06 from
k 309 and 261 (32 tries each). In total, 208 new configurations (k 179-386, stage "polish"). No parameter range
was widened: o_B runs to the lower edge (2 mm) but the best uses 3.

**Best so far** (score = 100 (1 - gap/275)):

| Polish try | 1 | 53 | 104 | 157 | 208 |
|---|---|---|---|---|---|
| Score | 60.4 | 61.2 | 62.7 | 64.1 | 65.6 |

**Best: k 338, gap 94.55, score 65.6.**
- Reach 0.469, follow 0.650, in band 2-14 0.703, in band 2-10 0.407, contact 0.017. Ti mass 86 g.
- Settings: halo el 31.9 with f1s -4.75; arm oval (101.7, -6.9, 54.1, 3.0), longer than before; q 0.905 / qH 0.91;
  rmax 89.3.
- Refusals: no crossing 65 (was 98), off track 24, neck/swivel 7, tangent 5, flip 3, contact 2.
- Per part, in band 2-14: T_S 0.93, carriage A 0.98, neck 0.63, T_H 0.24, carriage B 0.05.

**Convergence gate: NOT converged.**
- The second half gained +2.96 points. The gate requires < 1.
- The best came at try 160 of 208, inside the last third.
- The top 5 are within 2.0 points (94.55-100.12). This part passes.

**Limit.** Even unconverged, the bar looks out of reach.
- The kinematic screen of the best (no geometry at all) gives reach_kin 0.65 and follow_kin 0.72. That is a
  reach/follow gap of 48 before any in-band loss.
- The geometry then loses about 18 percentage points of reach and 7 of follow. These are mostly poses where the
  crossing exists but leaves the 93 deg arm track, plus the neck/swivel interference.
- Red team, with the model's own closure / contact / continuity checks on:
  - rest is taken;
  - overhead (elev 160), across-the-body, behind-the-back, abd90 and flex90 now all *have* a crossing
    (transversal, 51-77 deg) but it lies off the trimmed arm track.
- So the growth comes from a longer arm track. The arm track is capped by the humerus-safe patch (rmax ~90 mm).
  The outer track and carriage B are still out of band (0.24 / 0.05), because they ride on the 11 mm stack.

**Verdict.** Still dead (65.6 < 74.9), but not converged. The next lever is the arm-track length against rmax, not
more sampling of the halo.
