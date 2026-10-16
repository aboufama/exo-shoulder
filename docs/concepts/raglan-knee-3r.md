# raglan-knee-3r - the zero-passive-translation leader (pin knee on the k4216 seats) with raglan-routed links

Model: `docs/concepts/models/raglan-knee-3r.py` (`check | map | frozen`; imports a private copy of
`skin-normal-3r-pin-knee.py`, so every pin-knee rule and check is inherited, not re-implemented).
Sweep: `docs/concepts/sweeps/raglan-knee-3r.json` (coarse farm sweep + every CMA try, in order).
Sister morphologies: `docs/concepts/raglan-routed-3r.md` (routing on the plain 3R), `docs/concepts/far-end-posterior-3r.md`
(far-end hubs, killed).

## Depth answers (before modelling)

1. **What a top pattern maker / orthotic fitter would do here.** Fit the garment to the body in MOTION, not at rest:
   cast in the positions of use, then place every seam on the line that does not move against the body under it
   (raglan seam, Iberall's lines of non-extension), and every hard landmark (hinge, rivet) on skin that rides with the
   piece it carries. Here the "garment pieces" are the two rigid links of the best buildable design (the pin knee:
   0 passive translations, 26.34 fast / 33.84 frozen exact) and the seams are the link centrelines. So: measure, in
   each link's OWN moving frame, which directions keep one height within 2-14 mm over every pose the chain takes (the
   raglan map), and bend the link along the best line with one planform turn (two straight legs and a tangent arc, a
   constant 8 x 3 section: the user's bent-bar style, no loft). Then let the optimiser move the seats WITH the routes
   (a seat that was bad only because its straight link crossed moving skin becomes reachable), and try the posterior
   J1 line (fold-free on 100 % of poses, the far-end scan's lead) in this family.
2. **Rawest material.** The posed skin of every bench pose (signed-distance grid, Bench(60, 160) fast; the verdict on
   Bench(110, 360) exact); the sphere-traced need (2 mm clearance) of every direction of the link's own frame in every
   pose the chain takes, with link 2 flying over the knee and pad boxes, exactly as the pin knee fits its links.
3. **Instrument.** The pin-knee model (closed-form spherical IK, knee closure in [30, 150] deg, 10 fps continuity, jam
   rule, every part pair, hub walls / crowns / strap tops skin-checked, greedy pose drop recorded as contact), the
   raglan map (`map` mode), the farm (`tools/cloud_run.py sweep`), CMA-ES on the farm (`tools/concept_cma.py`), the
   frozen large-bench protocol (fit on Bench(60, 160) fast, freeze, wear on Bench(110, 360) exact).
4. **Outside judge.** `tools/concept_bench.py` through the pin knee's own scoring (same poses, metrics, contact rule as
   every row); parity with the pin knee at d = 0 (k10: 26.34, every metric to 4 decimals); the frozen Bench(110, 360)
   exact wear; the adversarial verifier.

## Mechanism (every joint a real component)

| element | component | envelope in the model |
|---|---|---|
| J1, J2 (active R) | MR117-2RS bearing pair in an O20 hub on a GH ray | O20 disc at the fitted face, 12.25 mm stack, walls + crown skin-checked |
| J3 (active R) | same, offset skin-normal hub on the deltoid (tilt b3) | as above |
| knee (2 passive R) | two pins: integral O4 Ti pin, iglidur GSM sleeve + 2 GTM washers (tools/hardware_catalogue.json IGLIDUR-PIN) | 5 mm pin stack, O12 bosses, 10 mm knee link, E strap, arm pad |
| link 1, link 2 | 8 x 3 Ti bent bar: two straight legs + one tangent arc (planform radius rc, 10 mm default) | skin-fitted underside per sample, <= 60 deg ramps, link 2 over the knee / pad |
| neck / cuff | the pin knee's E strap, boss, pad on BOTTOM's cuff | as the pin knee |

Passive translations 0. Every coordinate is set by the 3 actuators and the closure (the knee is a closed planar RRR).

## Results (Bench(60, 160) fast grid, every pin-knee rule on)

**Parity.** d = 0 reproduces the pin knee's k10 exactly: gap 26.34, reach 0.7063, follow 0.9667, in-band 14 0.8419,
in-band 10 0.4001, contact 0.0116 (5 s). Per part (clip poses taken, in-band 2-14 / median mm / samples): hub 1 1.00 /
9.5 / 80, hub 2 0.996 / 10.5 / 80, hub 3 0.748 / 12.0 / 80, E 0.881 / 8.9 / 28, boss 0.816 / 9.4 / 32, pad 0.80 / 11.5 / 32,
knee link 0.64 / 12.8 / 90, link 1 0.925 / 7.3 / 36, link 2 0.834 / 10.7 / 141. Not taken: 47 fold, 2 skin (of 220).

**Raglan map at k10** (the measurement, 11 s; `map` mode; 19 t x 21 d cells per link, d -50..+50 deg off the great
circle, need sphere-traced to 2 mm in each link's own frame over the 173 poses the chain closes in; `ceiling` = the best
12 mm window share, i.e. what one height can keep in 2-14 mm):

| link | span | great circle (d = 0) ceiling along t | best d per t | what it says |
|---|---|---|---|---|
| link 1 (hub 1 -> hub 2) | 40.3 deg | 0.99-1.00 at every t | -20..+10 all within 0.01 of the best | already a raglan line: the whole band d -20..+10 is equally good; no route can add |
| link 2 (hub 2 -> hub 3) | 77.8 deg | 0.99 (t <= 0.3) falling to 0.80-0.87 (t >= 0.7) | 0 at every t (+-5 at the ends) | the great circle IS the argmax: off it the ceiling falls on both sides (d -20: 0.50-0.83; d +20: 0.67-0.98 near hub 2 only) |

So the leader's CMA (9869 tries on the osn seats) already put both links on their lines of least skin motion; the
straight bar is the raglan seam here. That differs from the plain 3R (raglan-routed-3r), whose straight link 1 crossed
the posterior acromion edge and gained 8.6 gap points from one 38 deg turn.

**One routed check** (link 1 t 0.5 d -10, link 2 t 0.7 d +10): gap 28.87 - link 1 0.925 -> 0.949, link 2 0.834 -> 0.768,
as the map predicts.


**Coarse farm sweep** (177 configurations, 23 farm jobs, $0.23; stages in the sweep log):

| stage | n | best gap | median | what it says |
|---|---|---|---|---|
| k10 control (d = 0) | 1 | 26.34 | | parity on the farm |
| link 1 routes (t 0.3 / 0.5 / 0.7, d -20 / -10 / +10 / +20) | 12 | **25.36** (t 0.7, d -20) | 45.13 | d -20 at any t: 25.36-25.56 (in-band 0.842 -> 0.850-0.852); d +-10 / +20 worse (link 1 meets hub 3 / link 2 or rises) |
| link 2 routes (t 0.3-0.85, d -20..+20) | 24 | 31.77 (t 0.3, d -5) | 43.39 | every link-2 turn loses: parts collisions (knee / pad / hub 1) and the deltoid end of link 2 |
| both links | 8 | 27.22 | 53.48 | link 2's loss dominates |
| tangent arc r 20 instead of 10 | 4 | 26.03 | | a gentler corner keeps less of the gain |
| seat jitter (+-4 deg, b3 +-0.06) + random routes | 64 | 33.84 | 56.19 | no seat near k10 is better with routes: the fold rises 47 -> 53-59 poses |
| posterior J1 line (far-end scan lead: bvec(-24, 4), (-18, 20 / 24), (-30, 8); J3 wdir(80 / 100, -90); arcs 65 / 65, 65 / 75; b3 0 / 0.35; both branches) | 64 | 122.45 | 255.8 | dead: fold 6-20 poses only, but 46-69 skin poses of 220 (not split per part), in-band 0.17-0.25, contact 0.23-0.29; 23 of 64 close no pose at all |

Best coarse (k for `r1t 0.7, r1d -20`): gap **25.36** (score 90.78), reach 0.7063, follow 0.9667, in-band 14 0.8517,
in-band 10 0.40, contact 0.0116 - the same 47 fold + 2 skin poses as k10; the whole gain is in band.

**Steeper link-1 turns** (local, Bench(60, 160) fast, every rule on):

| link 1 route | gap | in-band 14 | link 1 in band / samples | turn | gap with link 1 at its great-circle sample count (`gap_fixed_n`) |
|---|---|---|---|---|---|
| great circle (k10) | 26.34 | 0.8419 | 0.925 / 36 | 0 | 26.32 |
| t 0.7, d -20 | 25.36 | 0.8517 | 0.993 / 64 | 90 deg | |
| t 0.7, d -25 | 25.06 | 0.8547 | 0.996 / 72 | 101 deg | |
| t 0.7, d -30 | 24.90 | 0.8563 | 0.994 / 80 | 110 deg | |
| t 0.5, d -30 | 24.96 | 0.8557 | 0.990 / 80 | 107 deg | |
| **t 0.85, d -30** | **24.79** (score 90.99) | 0.8574 | 0.997 / 84 | 114 deg (arc r 8.7) | **25.89** |
| t 0.7, d -40 | 27.28 | 0.8325 | 0.81 / 104 | 122 deg | |
| t 0.7, d -20, arc r 6 | 25.27 | 0.8526 | 0.993 / 64 | 90 deg | |

## Red team: the number that is optimistic (dilution)

In-band 14 is a SHARE of metal samples. The steep turns do not move any out-of-band part closer: link 1 grows from
36 to 84 samples (43 -> 64 mm, +~9 g Ti) and every new sample sits in band, so the share rises by DILUTING hub 3,
the knee link and link 2. Weighting link 1 at its great-circle sample count (`gap_fixed_n`, now in every report of
this model) gives 25.89 for the best route: **the real gain of routing on the leader is 0.45 gap points** (link 1
0.925 -> 0.997 in band); the other 1.1 points are dilution. A 114 deg hairpin in a 64 mm bar is buildable (a bent
8 x 3 bar) but no designer would add it for its function - it is the annular-ring skirt artefact
(docs/concepts/annular-ring-3r.md) in another form. The CMA streams on this model optimise the bench gap, so they will
chase the same artefact; their bests are re-scored with `gap_fixed_n` below.

The same check on the plain 3R (raglan-routed-3r k3484): link 1 has 340 samples routed vs 245 straight at the same
axes; at the straight count the gap is 43.97 instead of 42.72, against 49.89 for the straight links at those axes:
there routing is mostly real (link 1 0.36 -> 0.60 in band, +5.9 points), dilution 1.25 points.

## Frozen on Bench(110, 360) exact (lesson c) and red team

Shape fitted on Bench(60, 160), frozen (hub faces, stack level, knee centre m, every link sample height), worn without
refit on Bench(110, 360) exact (the pin knee's own `frozen`, `.cache/rknee/big_*.json`). These two jobs ran without
the grid-cache link, so the FIT ran on the exact path too (fit gap 26.46 / 25.48 instead of 26.34 / 25.36 fast): the
conservative side, and the same for the control and the routed shape.

| shape | fit (60 / 160) | **frozen big exact** | score | reach | follow | in-band 14 | contact | `gap_fixed_n` (link 1 at 36 samples) | metal < 1 mm as contact | < 2 mm |
|---|---|---|---|---|---|---|---|---|---|---|
| k10 control (great circle) | 26.46 | 34.06 | 87.6 | 0.619 | 0.964 | 0.843 | 0.003 | 34.06 | 35.80 | 57.94 |
| link 1 t 0.7, d -20 | 25.48 | **33.10** | 87.96 | 0.619 | 0.964 | 0.853 | 0.003 | **33.67** | 34.84 | 56.99 |
| **link 1 t 0.85, d -30** (best fast; fit on the fast grid) | 24.79 | **32.33** | 88.24 | 0.619 | 0.964 | 0.860 | 0.003 | **33.41** | 34.07 | 56.88 |

| **CMA A2: seats + link 1 t 0.80 d -30.6** (best fast; fit on the fast grid) | 23.00 | **31.52** | 88.54 | 0.600 | 0.973 | **0.902** | 0.015 | **32.11** | 35.02 | 65.38 |

A2 on the big bench: 139 fold + 3 E / link 2 jams + 5 contact of 470; in-band 0.90 passes its target, so reach (0.600) is
now 30 of the 31.5 points; overhead reach 0.25 (19 of 28 fold), in-band 0.94; nearest metal 0.12 mm (plane 45, elevation
75, axial -105) and 0.19 mm (plane -75, elevation 45, axial 120); metal < 2 mm in many more poses (65.38 counted as
contact): the lower hub 3 / knee stack pays in margin. Knee angle 72-121 deg.

(The pin knee's own frozen run of k10, fit on the fast grid: 33.84 - the like-for-like control for the d -30 row:
-1.51 on the bench gap, -0.43 at fixed part sizes.)

Red team (frozen big bench, link 1 d -20; the d -30 best is the same pose for pose: 136 fold, 4 E / link 2 jams, 1 contact,
nearest metal 0.20 mm, 34.07 with metal < 1 mm as contact, overhead reach 0.29 / in-band 0.91):
* **The pose that jams**: 136 of 470 poses fold (J2 fold, identical to the control: routing does not touch it), 4 jam
  on the adjacent E strap / link 2 pair at J3, 1 contact. Overhead (elevation >= 140): 19 of 28 workspace poses fold,
  reach 0.29, in-band 0.90.
* **The point that pinches**: 0.12 mm at plane 30, elevation 165, axial -60 (ws #264) and 0.14 mm at plane -60,
  elevation 60, axial 105 (#139) - both on the contact-only walls / crowns, the same poses as the control; 3 taken
  poses under 1 mm (34.84 counted as contact); under 2 mm the gap is 56.99 (many crowns ride at 1-2 mm).
* **The number that is optimistic**: (1) dilution - 0.57 of the 0.96-point frozen gain is extra in-band metal
  (33.67 at the great-circle sample count vs 34.06); (2) the fast-to-exact transfer costs 7.6 points, all of it reach
  (0.706 -> 0.619: the fold band on the denser bench).
* Knee angle over the taken poses 73-116 deg (window 30-150): no knee singularity is approached.

## Verdict

**Routing is a small lever on the leader; the seat move it came with is the bigger one.** The raglan map says the leader's links are already on their lines of least
skin motion; the coarse sweep and the steeper turns confirm it: the real gain is 0.4-0.45 gap points (link 1
0.925 -> 0.99 in band) at the k10 seats, everything above that is dilution, and every link-2 turn loses. Routes only:
24.79 fast (score 90.99; 25.89 at fixed part sizes), 32.33 frozen big exact (score 88.24; 33.41 at fixed sizes)
against the pin knee's 26.34 / 33.84. Seats + routes (CMA A2): **23.00 fast (score 91.64; 23.62 at fixed sizes)**, of
which the seat move alone (straight links) is 24.49; worn frozen on Bench(110,360) exact **31.52** (score 88.54; 32.11 at fixed
sizes) - the best large-bench number of any design so far (unverified), still 4 points short of 90 because of the fold. The 90+ bar on the large bench needs
about +0.28 reach, i.e. the J2 fold - nothing a link's route can move.
The posterior-J1 seats that remove the fold lose 46-69 poses to skin instead (best 122.45).

**CMA round 2** (farm, grid cache linked, popsize 8, 2 processes per stream; objective = the bench gap, every report
also carrying `gap_fixed_n`):

| stream | free | tries | best gap | at fixed part sizes | reach | in-band 14 | where it ended |
|---|---|---|---|---|---|---|---|
| C2 | routes only (k10 seats) | 513 | 24.50 | 25.84 | 0.706 | 0.860 | link 1 t 0.85, d -34 (L1 96 samples): more dilution, no new real gain |
| **A2** | seats + routes | 1009 | **23.00** (score 91.64) | **23.62** | 0.688 | **0.901** | J1 bvec(96.9, 66.2), J2 bvec(13.0, 54.7), J3 wdir(75.9, -14.0), b3 0.239; link 1 t 0.80, d -30.6; link 2 straight (-1.3) |
| D2 | seats + routes + knee (phiE, lE, lc) | 1065 | 23.54 | 24.04 | 0.688 | 0.895 | J3 wdir(78.5, -14.6), lE 35.9, lc 25.8, link 1 d -20.8, link 2 d +5.4 |

Attribution at A2's seats (local, fast): the same seats with straight links score **24.49** at fixed sizes (24.51 bench):
the seat move (J3 3.3 deg more proximal: hub 3 0.748 -> 0.838, knee link 0.64 -> 0.79, boss / pad / E 0.81-0.88 ->
0.89-0.91 in band; one more fold pose and contact 0.0116 -> 0.0175) gives 1.8 points, the route 0.9 real + 0.6
dilution. The seat move is a pin-knee freedom the leader's seats were tuned without (osn's 2-slide stage has other
parts at hub 3); it belongs to the pin knee as much as to this morphology.

Gate (per stream, chronological; score = 100 (1 - gap / 275)): C2 gained 0.0 over the second half / 0.0 over the last
third, top 5 within 0.01; A2 0.10 / 0.0 / 0.0; D2 0.03 / 0.03 / 0.01: **converged** (sigma collapsed in each). The
first CMA round (27 tries) ran on the exact path (missing cache link) and is logged as not comparable.

## New knowledge

1. On the leader (pin knee / osn k4216 seats) the straight links ARE the raglan lines: the map's argmax is d = 0 on
   link 2 and a flat plateau d -20..+10 on link 1. The 9869-try osn CMA already solved the routing problem implicitly.
2. In-band dilution is the dominant way a route "gains" on a good design; a fixed-part-size in-band (`gap_fixed_n`)
   is needed to judge any shape change that also changes part size.
3. The posterior J1 line is dead in the knee family too (skin, not fold, takes the poses).
4. With routes free, CMA moves the pin knee's J3 seat 3.3 deg proximal (wdir(75.9, -14.0)): hub 3, the knee link, boss
   and pad come into band (hub 3 0.75 -> 0.84, knee 0.64 -> 0.80) and the in-band target (0.90) is met on the large
   bench (31.52 frozen exact, 0 passive translations). From here only reach moves the score: the J2 fold, 139 of 470.

## Next (the loop)

* Independent verifier on A2 (`best_params` in the row): re-measure fast + frozen exact with the pin-knee verifier
  harness, and re-score at fixed part sizes; check the 0.12 / 0.19 mm near-touch poses and the 2 mm margin (65.38).
* Hand A2's J3 seat to the pin-knee track (a pin-knee freedom), and the bent link 1 (t 0.80, d -30.6, arc r 10) to the
  L1 CAD as a bent bar if the verifier confirms >= 1 point at fixed part sizes.
* The fold is the only lever left on this family: J2 metal off the J2 ray (arc guide / carriage families).
