# scapular-race-j2-carriage - J1 is a rail on the bony rim, J2 rides its carriage

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the rail as what it is: a
   scapula-fixed part that is metal in EVERY pose along its whole length. Its radius is set by the highest skin under
   any station in any pose, so the rail may only be laid over stations whose skin never rises - choose the rail extent
   from the measured per-station requirement, not from a fixed phi window (design step `travel()`: the contiguous run
   of "quiet" stations, requirement <= `rmax`, that holds the most closing poses). (b) Make the carriage honest: a
   rolling carriage about a1 can only run on a surface of revolution about a1, so the rail is one circle at ONE
   distance R; V-rollers hang beside the rail head down to R; the J2 O20 lower plate IS the carriage plate, riding
   0.5 mm over the rail top (F = R + 4.5). (c) Check that the one moving strap L2 can be in band at all - the proximity
   atlas says a closure-frame link crosses skin that moves ~40 mm under it - and if it is the limiter, look for J3
   placements that make L2 short.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (cached grid,
   K3 march per sample ray), the fit-clip frames in time order (`B.clip_order`, slerped between frames for K2), the
   everyday-workspace envelope. The skin-motion map and the atlas are digests; they only guided where to look (the
   scapula-fixed quiet zone: top cap el > ~65 deg plus a posterior lobe, docs/research/proximity_atlas.md).
3. **Methods and tools.** The shared kit (tools/concept_kit.py): exact two-circle closure (a1, p3; arcs gamma, alpha23),
   K3 march for every skin-facing sample, flat O20 hubs with the 12.25 mm stack (J2 on the carriage, J3 on the arm),
   12 x 3 strap L2 with the 60 deg climb limit and `over` the race and the neck, K7 neck to BOTTOM, dense K2
   continuity along the slerped motion, K6 collisions. Sweeps on the cloud CPU farm (tools/cloud_run.py sweep), coarse
   random then CMA-ES from the top configurations until the convergence gate passes.
4. **What, other than me, shows the number is right.** tools/concept_bench.py on Bench(60, 160) (same poses and metrics
   as every concept; champion 68.93), the kit's audit (hub size, sampling density, pose locality), the swarm's
   adversarial verifier, and the red-team list below (rest, overhead, across the body, behind the back, the pose that
   sets the rail radius, part-part clearance re-checked in true 3D).

## Morphology and model

Topology (scapula handler -> user's cuff), every joint axis through the GH centre: base + **rail** (scapula-fixed arc,
10 wide x 4, at polar angle gamma about the race axis a1, at ONE distance R from GH) -- **J1** = the carriage rolling on
the rail (V-rollers on both rail edges; its azimuth phi about a1 is the joint value; no hub and no metal at a1's pole)
-- **J2** = O20 hub whose lower plate IS the carriage plate (axis u2 = the carriage's own direction from GH, so
alpha12 = gamma) -> **L2** (12 x 3 strap, skin-fitted underside) -- **J3** O20 hub, axis wdir(wd, wa) fixed in the
humerus -> arm-end plate + neck (14 x 6) to BOTTOM's bar. phi, q2, q3 follow from the two-circle closure of a1 and p3
(arcs gamma, alpha23, branch sigma): **3 active DOF, 0 passive**, nothing undetermined.

Model: `docs/concepts/models/scapular-race-j2-carriage.py` on the shared kit (K3 march, flat O20 hubs with the
12.25 mm stack, K5 strap, K7 neck, dense K2 along the slerped motion, K6 collisions; audit clean, `honest` true).
`python3 ... check [k=v ...]` evaluates one configuration, `python3 ... bound [n]` reproduces the ceiling below.

Spec changes (each stated):
* **the rail extent is chosen from the skin, not from a phi window** (design step `travel()`, outside `build` so
  `build` stays pose-local): rail stations every 2 deg, the K3 march along each station's centre ray in every closing
  bench pose, quantile q; stations with need <= `rmax` are quiet; the rail is laid on the contiguous quiet run that
  holds the most closing-pose carriage azimuths, trimmed to the travel actually used (+ `tmarg` 3 deg) + half a
  carriage (13 mm) + a 3 mm end stop at each end. The J1 range is that travel; poses outside it are not taken.
* **carriage = rollers + the J2 lower plate.** The spec's 26 x 22 x 8 block sharing the rail's skin face cannot be
  separated from the rail in the kit's K6 (they would always "collide"), and it is not what rolls: the V-rollers hang
  beside the rail head down to R (strips 5..9 mm either side of the rail centre, +-8 mm along, in the race member at R),
  the carriage plate = the J2 O20 lower plate rides 0.5 mm over the rail top (F = R + 4.5), L2 at F + 3.15.
* **J3 = an O20 hub + K7 neck** (the spec's option), not the septum barrel: the barrel (r 7) is smaller than O20 and
  the audit flags it; the barrel's J3 position (wd ~22, wa ~-35) was tried as a seed and closes in 3-11 % of poses.
* humerus axes in the band frame (`F.HG`) as the kit and the champion; scapula axes `bvec(az1, el1)`
  (the spec's sdir(lat, lon) = bvec(90 - lon, lat)).
* `r_lay` (the layout radius of the rail and roller samples) is a fix point at the fitted R (|R - r_lay| <= 1.5 mm, at
  most 2 re-runs); a layout above the fitted R would draw a rail narrower than 10 mm and is flagged dishonest.
* link 2's hub ramps run over its first / last 16 mm (kit default 12): with 12 mm the kit's `over` (which measures at
  the pre-climb radius) left L2 0.15 mm over the rail just outside the J2 zone in 85 % of poses (found and fixed here);
  link 2 is listed first among the members so K6 measures its pairs at its own radius, as `over` builds them.

## The ceiling, from the raw skin (why the race cannot reach gap 0)

**A race carrying a GH-concentric hub must be a surface of revolution about a1.** A rigid carriage that turns about a1
sweeps surfaces of revolution; on a rail whose radius changes along its length (a "cam" rail) the carriage pitches by
atan(r' / (r sin gamma)) and tilts the J2 axis off GH, so the three axes no longer meet and L2 binds. So the rail is
one circle at one distance R, and every station of it is metal in every pose: R must clear the highest skin under ANY
station of the used arc in ANY taken pose.

`python3 docs/concepts/models/scapular-race-j2-carriage.py bound 24000` (K3 march along every scapula-fixed direction on
a 3 deg grid in all 220 bench poses, quantile 0.95; 24 000 random designs over a1, gamma 15-85, alpha23 40-120, the J3
axis, the branch and the rail radius budget `rmax`; the J2 axis must land on the best contiguous run of rail stations
whose need is <= rmax, +- half a carriage + end stop). Hubs, L2, K2 and K6 are ignored, so these are UPPER bounds:

| rail radius budget rmax (mm) | 65 | 70 | 75 | 80 | 90 | 100 | 115 | 130 |
|---|---|---|---|---|---|---|---|---|
| reach upper bound | 0.556 | 0.613 | 0.625 | 0.713 | 0.787 | 0.856 | **0.925** | 0.956 |
| best follow bound | 0.933 | 0.917 | 0.950 | 0.950 | 0.983 | 1.000 | 1.000 | 1.000 |
| rail in band at one R (the reach-best design) | 0.630 | 0.223 | 0.330 | 0.118 | 0.045 | 0.037 | **0.010** | 0.020 |
| rail underside in band if it could follow each station (ceiling) | 0.892 | 0.818 | 0.860 | 0.599 | 0.657 | 0.154 | 0.534 | 0.315 |

Reach >= 0.90 needs the rail at >= ~115 mm from GH; there the one-radius rail is 1 % in band (its stations need 46 to
115 mm: median ~68). Below 80 mm the rail can be in band but the J2 axis then cannot follow the arm: reach <= 0.71.
The deltoid, armpit and pectoral stations are the ones the arm enters (the spec's own 13-pose precheck found the same:
~45-50 % of the workspace).

## Sweep (Bench(60, 160), fast grid cache, K3 march, dense K2, K6, audit clean)

| stage | tries | best gap | where |
|---|---|---|---|
| local check, spec axis a1 = sdir(0, 20), gamma 50, alpha23 80, champion J3 | 1 | 158.84 | reach 0.31, follow 0.53 |
| coarse, farm: 12 seeds (spec, workspace-centre, champion, ...) + 276 random | 288 | 147.61 | rail laid out at 55 mm (wider than real when R > 55: conservative) |
| CMA-ES, farm (tools/concept_cma.py, 6 streams A-F from the coarse top + spec seed, popsize 8, ~150 generations each) | 7262 | 78.04 | stream E; A 81.17, D 82.95, B 92.23, C 95.06, F 105.83 (several basins) |
| red-team rescore under the strict layout rule (r_lay <= R + 0.25), top 25 distinct | 25 | **78.54** | k7562 |
CMA_STREAMS_2

**Best (k7562), honest, audit clean:** gap **78.54** (score **71.44**; champion 68.93 / 74.93): reach **0.575**, follow
**0.85**, in-band 14 **0.617**, in-band 10 **0.276**, contact **0.077**. az1 103.78, el1 71.51 (race axis a1 lateral,
up 72 deg), gamma 37.41, alpha23 106.85, J3 wdir(51.34, -23.57), branch -1, q 0.912, rmax 83.8, r_lay 62 = R 62.0.
The rail spans 209 deg of the circle at 62 mm from GH; J1 travel -5..156 deg. Per member in band: **rail + rollers
0.959**, hub2 (carriage plate) 0.317, link2 0.283, hub3 0.754, neck 0.883. Ti mass 124 g.

The race does what the spec promised - the rail on the quiet rim is the most in-band member any morphology has shown
(0.96), and the in-band total (0.62) beats the champion (0.44) - but the J2 axis cannot follow the arm: closure + rail
range take 70 % of the poses, reach 0.575.

**Convergence gate** (score points, honest tries in chronological order - coarse, then the CMA streams interleaved by
generation): best gained 0.17 over the second half, 0.06 over the last third, top 5 within 0.06 (tolerant layout rule);
the strict-rule rescore of the top 25: top 5 within 0.66. **Converged.** GATE_2

## Red team (k7562 / its twin k6367)

* **Optimistic number found and removed:** the first CMA ran with a +1.5 mm layout tolerance; it parked r_lay 1 mm
  above the fitted rail radius (rail drawn 9.84 mm wide, end stops shorter): 78.04. With r_lay <= R + 0.25 (now the
  model's rule) the same configuration reads 80.78, and the best strict configuration 78.54.
* **Pose classes** (taken / total; why not): rest (elev < 25) 56/58 (2 contact); overhead (elev >= 120) **17/41**
  (14 no closure, 4 off the rail, 6 contact); across the body (plane >= 100) 12/27 (6 no closure, 9 off the rail);
  behind the back (plane <= -40) 17/23 (3 no closure, 3 contact); abduction 60-120 deg 10/26 (15 no closure).
* **The pose that sets the rail radius:** overhead plane 45 elev 165 axial -90 - the arm itself lies on the rail
  stations (need 176 mm); the rail stays at 62 mm because those poses are inside the q = 0.91 tail: they are contact
  poses (counted, 7.7 % contact).
* **Pinch:** link 2, 23.9 mm inside the arm at overhead plane 120 elev 165 (a contact pose, counted as contact).
* **True-3D part clearances** over the taken poses (underside and top surfaces as point clouds): link 2 over the rail
  1.0 mm (the `over` rule, exact); link 2 vs neck 0.21 mm, 12-16 mm from the J3 axis - they are the upper and lower
  members of J3, so the 0.15 mm running gap applies (passes); hub2 / rail vs the arm parts >= 35 mm.
* **Not modelled, would cost more:** the rail's mounting to the scapula handler (outside the count); the rollers as
  two strips at R (real V-rollers have a 2-3 mm deeper groove); the carriage plate is the O20 lower plate (20 mm disc)
  - a carriage carrying four rollers is closer to 26 x 22 mm, so hub2's 0.32 would drop.

