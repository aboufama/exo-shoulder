# rollcone-hubspot-pinknee-3r - rolling-cone J2 at H1's hub-2 spot (round 501, G1)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the rolling pair as what it is
   kinematically - a 2R (sun axis uK, planet axis v2, both through GH) with a fixed linear coupling x = rho y - and
   read its singularity in the SAME metric as every verified row: the instantaneous dyad (u1, contact line, J3) margin
   >= 5 deg, plus the segment-extremum margin. Model the metal as what a strap-held pair can be: two conical walls at
   ONE radius each (a common strap radius +- 1.5 mm), no per-direction contour, and make the links reach the walls (a
   link that cannot meet its band lifts the band). Then search where the metal, not the ghost, wins: the band
   geometry (half angles, split plane beta, rest-zero) jointly with H1's seats and knee, on the near-touch objective.
2. **Rawest material.** The posed skin itself through the bench's exact signed distance (tools/concept_bench.py, the
   per-pose sphere-traced need of every band sample), the 10 fps fit clips for continuity, the rest-pose skin for the
   seats (offset-skin-normal-3r seat()), H1's verified best_params as the start - not the judge's ray-rule digest.
3. **Methods and tools.** H1's model (skin-normal-3r-pin-knee.py: O20 hubs 1/3, kit near-touch, closure, jam rule,
   knee window) subclassed; rolling IK by tabulating th(y) on the rest segment (0.25 deg) and interpolating;
   one-level-per-part band fitting through the seed's needed()/greedy_drop() (both bands in ONE level group);
   collisions band-band (outside the contact line, adjacent 0.15 mm), band-hub, band-link, band-knee; local
   random + CMA-ES on Bench(60,160) fast, frozen exact read on Bench(110,360).
4. **What shows the number is right, other than me.** The bench's report (gap from its own distances), the frozen
   exact Bench(110,360) wear, the auditor / verifier re-run of this model file, and the red-team pose list
   (redteam mode: poses not taken with cause, closest metal per part, near-touch at 1 / 2 mm, named pose groups).

## The model (docs/concepts/models/rollcone-hubspot-pinknee-3r.py)

H1 (skin-normal-3r-pin-knee H-g107-1 seats, O20 v5 J1 / J3, flat two-pin knee on MR63ZZ pairs, stack 6.0, knee window
[ang_min, 180 - ang_min]) with hub 2 deleted. J2 is a rolling cone pair, apex GH:

- contact generator at rest c = u2 (H1's hub-2 axis, link-1 frame); split direction tb = cos(beta) t0 + sin(beta)
  (c x t0), t0 = the tangent at c pointing away from u1; sun axis uK = R(c x tb, -alpha_s) c (link 1), planet axis
  v2 = R(c x tb, +alpha_p) c (link 2);
- rolling without slip: link 2 = link 1 R(uK, rho y) R(v2, y) R(u2, q2_rest), rho = sin(alpha_p) / sin(alpha_s); the
  `kin` mode checks numerically that the relative angular velocity lies on the contact line R(uK, rho y) c (error
  0.003 deg); at rest the chain IS H1;
- IK: th(y) = angle(u1, J3 direction) tabulated at 0.25 deg; the monotone segment holding the rest is the branch; y by
  interpolation, q1 / q3 / the knee exactly as H1 (both virtual axes pass GH, so the knee closure theorem holds);
- fold: the instantaneous dyad (u1, contact line, J3) margin >= 5 deg AND th >= 5 deg from the segment extrema (the
  two are the same singularity: dth/dy is proportional to u1 . (c x w));
- metal: a sun band on link 1 and a planet band on link 2, each a 2.5 mm Ti wall + 0.15 mm strap stack, `bh` mm tall
  radially from ONE level per band (one R_lo for the whole band, never a per-direction contour), the two levels within
  1.5 mm (common strap radius), sectors = the taken roll span + 3 deg + a 4 mm clamp at each end; bottom edges scored
  (2 rows across the wall, 2 mm pitch), both faces and the top edge skin-checked (contact only); link 1 hub 1 -> sun
  band mid sector, link 2 planet band mid sector -> hub 3 (H1 straps, 60 deg ramps, the link end held >= the band
  bottom); collisions: sun-planet adjacent (0.15 mm) outside 3 mm of the contact line, bands vs hub 1 / hub 3 / the
  other link / E strap / knee / pad (1 mm), and every H1 pair; seed VModel rules (closure < 0.5 deg, 10 fps continuity
  incl. the roll and the knee, jam rule).

Spec corrections: (1) the catalogue prices the knee pins as MR63ZZ (stack 6.0) - H1's verified best used 5.68; this
model uses 6.0 throughout (the lead's build rule). (2) The judge's 25/10/30 reading "planet band in-band 0.007" (sibling
rolling-cone-3r, which zeroes the roll at the reference Q = I) does not hold with the roll zeroed at REST (the spec): at
one level both bands read 0.97-0.98 in band (Bench(60,160) fast). (3) The rollcam (non-circular) and the internal
(ring) cells are NOT modelled here (time box); the external constant-ratio cell was searched over the full spec range
(alpha_s 8-35, alpha_p 4-16, beta +-60) jointly with H1's seats +-5 deg and the knee.

## Search (local, niced, <= 2 processes; the farm is closed)

Bench(60,160) fast, objective = the near-touch gap (metal < 1 mm counted as contact), every configuration in
docs/concepts/sweeps/rollcone-hubspot-pinknee-3r.json in order. Free: alpha_s 8-35, alpha_p 4-16 (rho 0.15-1.7),
beta +-60, band height bh 6-10, H1's seats +-5 deg (az1, el1, az2, el2, wd, wa), b3 0.15-0.40, knee lE / lc / phiE /
phib; fixed: ang_min 30.46 (H1), stk 6.0 (MR63ZZ), sector margin 3 deg + 4 mm clamps. Seeds: the catalogue cell
25/10/30 (fast 25.04: follow 0.917, 10 poses dropped as skin contact, 4 sun-band / link-2 hits), the sibling's band-legal 8.73/14.23/42 (18.92),
12/12/20; random stage (1/3 uniform over the box, 2/3 Gaussian around the seed), then a (3/3, 6)-ES from the top.

### The control (the rail-elbow lesson): is the gain the rolling pair or the seats?

Same code path for every part but J2 (H1's model, today's kit, stk 6.0), Bench(60,160) fast:

| configuration | gap | near-1 gap | reach | follow | ib14 | contact | kinematic ws |
|---|---|---|---|---|---|---|---|
| H1 seats, O20 pin J2 | 23.71 | 27.29 | 0.700 | 0.950 | 0.897 | 0.034 | 119 |
| best seats + knee, O20 pin J2 | 23.73 | 27.38 | 0.669 | 1.000 | 0.914 | 0.006 | 113 |
| best seats + knee, ROLLING J2 (2-es8-98) | 13.82 | 16.17 | 0.7625 | 1.000 | 0.899 | 0.000 | 122 |

The rolling pair is worth ~10 fast gap points (11.2 near-touch) at identical seats: the seats alone buy nothing. Two
causes, measured: (1) the window opens on the stretched side (rolling segment 26.4-108.0 vs the pin's 26.6-102.4 at
these seats, 9 more kinematic ws poses) and (2) no metal losses: all 122 kinematic ws poses are taken (the pin chain
loses 6 to the O20 hub-2 disc: skin / parts), because the 6.6 mm bands at ~61 mm sit inside the hub-2 disc's footprint
without its 12.25 mm stack and 20 mm disc.

### Frozen wear (lesson c): Bench(110,360) EXACT, shape fitted on Bench(60,160) fast, no refit

| configuration | fast gap (near-1) | frozen exact gap | near-1 | reach | follow | ib14 | ib10 | contact | overhead ws |
|---|---|---|---|---|---|---|---|---|---|
| **4-es32-202 (final pick, best fast near-1)** | 13.38 (13.38) | **22.16** (score 91.94) | 22.72 | 0.6889 | 1.000 | 0.8978 | 0.6025 | 0.0083 | 8/28 |
| 2-es8-98 (intermediate best) | 13.82 (16.17) | 23.33 | 23.89 | 0.6806 | 1.000 | 0.9005 | 0.5675 | 0.0139 | 7/28 |
| control: 2-es8-98 seats + knee, O20 pin J2 | 23.73 (27.38) | 27.55 | 30.41 | 0.6333 | 1.000 | 0.9126 | 0.5840 | 0.0088 | 7/28 |

On the frozen bench the rolling pair is worth 4.2 gap (6.5 near-touch) over a pin at the same seats; fast to frozen
loses ~9 points (the search tunes the fold boundary to the 160 fast poses, lesson c). References through the same
checks: H1 verified 27.20 (cx 0); geneva-tail rod 23.57 (cx 12); desmo-slipper 18.95 (cx 15.75); the lead
conecut-knee-knuckle-3r 18.28 (cx 18.5). At cx 6.5 this is a Pareto point between H1 and geneva-tail - IF a verifier
confirms it AND the user says yes to the rule questions below.

Final pick: alpha_s 12.81, alpha_p 7.20 (rho 0.565), beta 45.2, band height 6.34 mm; seats az1 96.56 / el1 67.53, az2
30.70 / el2 46.46, wd 73.46 / wa -6.83, b3 0.320; knee lE 61.57, lc 28.23, phiE -3.26, phib -60.37, ang_min 30.46, stk
6.0. Rolling segment th 26.8-109.6 deg (H1's pin 27.3-109.3), roll y -38.5..54.3 deg (x -21.8..30.7; sun arc 11.4 mm),
band levels 60.6 / 62.1 mm (sun / planet, one level each, 1.5 mm apart), both bands 0.99 in band (frozen), no link-to-
band step (band_lift 0). Min fold margin over taken poses 5.23 deg (dyad and segment), min |u1 . (c x w)| 0.215 (H1's
0.233). Rolling check: relative angular velocity on the contact line to 0.002 deg.

## Red team (own best; `redteam` mode, Bench(60,160), and the frozen read)

- **The limiter is still the fold, not the metal.** Frozen: 97 of 360 ws poses are fold losses (68 stretched, 24
  folded, 5 dyad-margin inside the window); metal costs only 4 parts (E strap vs link 2 at J3, an H1 pair) + 3
  contacts. The rolling segment (26.8-109.6) is no wider than H1's pin window (27.3-109.3): the search moved the
  seats to where a PIN would be narrower (at the intermediate seats a pin reads 26.6-102.4, rolling 26.4-108.0) and let
  the rolling pair buy back ~6 deg of stretched window while the metal got better (no hub-2 stack; bands at 61 mm, 0.99
  in band). It did not keep the stretched window the judge's 25/10/30 cell has (117.7): that cell
  scores 25.04 fast: follow 0.917, 10 poses dropped as skin contact and 4 sun band vs link 2 part hits eat the
  kinematic gain (its kinematic ws 127 / 160 vs the pick's 126).
- **Overhead: 8/28** (0.29; H1 0.25) - NOT solved. Overhead losses are fold 14 + slide 6 (knee window / radial).
- **Across the body is the in-band hole**: 24/36 taken, ib14 0.54 there (median 13.4 mm): hub 3 (0.70 in band) and
  link 2 (0.87) ride high when the arm crosses.
- **Pinch point**: frozen near-touch min 0.15 mm (pose 257, plane 30 / elev 90 / axial 30; 1 pose < 1 mm -> near-1 gap 22.72;
  metal < 2 mm on more poses -> near-2 gap 35.23), fast min 1.07 mm (hub 1, Raise overhead clip). The planet band came within 0.26 mm in the intermediate
  best (pose 100, plane 0 / elev 75 / axial 45) - the planet band is the part to watch.
- **The pose that jams**: E strap vs link 2 at J3 (4 frozen poses, adjacent running gap < 0.15 mm), as H1.
- **Optimistic numbers**: (1) the fast numbers (13.38) are 9 points optimistic - quote the frozen 22.16; (2) the GH
  apex coincidence is held by the straps and the contact only: generator slip / band tilt under the chain's moments is
  NOT modelled (CalculiX check needed; fallback: a spherical thrust lip, +1 sliding pair, cx +1); (3) strap fatigue
  (NiTi 0.05 mm on a 7.6 mm planet pitch radius at R 61) not checked; (4) the link-to-band junction is a straight
  continuation with no clamp body modelled beyond the band's 4 mm end clamps; (5) the internal and rollcam cells were
  NOT run; (6) not held out, not envsel - the next step.
- **Rule gate (questions for the auditor and the lead, for the user) - this row cannot be called verified, a winner or
  a leader until answered**: (a) a HUBLESS rolling J2 vs "Keep O20 only" (the user's 2026-10-16 ruling was about hub
  diameters; this joint has no hub); (b) strap-held pitch cones vs MVP1's "no gears, pulleys or cables" (the straps
  carry no drive, they are the joint's flexure constraint, as in a CORE / Rolamite joint); (c) straps priced as
  flexures (2 x 3 = 6, cx 6.5 by tools/simplicity.py v2.2 --score; 3 straps would be 9.5-10); (d) the coupled-fold
  reading (instantaneous dyad of the contact line, the kit's metric applied to the contact line).

## Convergence gate (score points of the near-touch objective)

439 configurations (seeds 1-4 merged in time order): gain over the 2nd half 1.01, over the last third 0.20, top-5
spread 0.03. The final ES run alone (205 tries from the intermediate best): 0.17 / 0.08 / 0.03 -> converged locally.
Converged on Bench(60,160) fast; the frozen gap (22.16) is the number.

## Verdict and next

Screened (not verified, rule-gated): frozen exact Bench(110,360) 22.16 (score 91.94) at cx 6.5 with 0 passive
translations - 5.0 better than H1 (27.20) and 1.4 better than geneva-tail (23.57, cx 12), 3.9 behind the lead (18.28,
cx 18.5). 95 is not reached: the stretched fold still costs 68 ws poses. Next (in order): (1) the verifier re-runs this
model (docs/concepts/models/rollcone-hubspot-pinknee-3r.py frozen '<best_params>') + held-out read + T5 dumps; (2) an
envsel / jittered-envelope polish (the fast bench under-samples axial rotation; every in-sample polish lost ~5 held
out) with the band geometry free, on the near-touch objective, and with a reach term that rewards the stretched
window (alpha_s / alpha_p cells near 25/10 where the window reaches 117.7 deg, but with hub 3 / L2 re-seated so their
metal holds); (3) the rollcam dwell cell (292 kinematic) on this metal model; (4) the CalculiX check of the strap-held
pair under the chain's moments.
