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
| posterior J1 line (far-end scan lead: bvec(-24, 4), (-18, 20 / 24), (-30, 8); J3 wdir(80 / 100, -90); arcs 65 / 65, 65 / 75; b3 0 / 0.35; both branches) | 64 | 122.45 | 255.8 | dead: fold 6-20 poses only, but 46-69 skin poses of 220 (hub 2 / link 2 into the neck and chest), in-band 0.17-0.25, contact 0.23-0.29; 23 of 64 close no pose at all |

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
