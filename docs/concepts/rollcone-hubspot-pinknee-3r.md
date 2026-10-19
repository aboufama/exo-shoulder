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
25/10/30 (fast 25.04: follow 0.917, 12 poses dropped as contact), the sibling's band-legal 8.73/14.23/42 (18.92),
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
