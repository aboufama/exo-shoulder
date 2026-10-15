# seed-offset-3r-slides - non-spherical offset 3R with passive self-aligning slides

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Count the loop's mobility before
   modelling (Grubler on scapula -> chain -> cuff -> humerus -> GH): the spec's 3R + 2 slides cannot close on a 3-DOF
   arm once the axes are offset, so fix the passive set first. Then use the offsets for the one thing they can buy - a
   rigid link sweeps a surface of revolution about its OWN axis line, so move each axis line until that surface matches
   the skin it passes over (scapula / acromion / deltoid are not spheres about GH) - and price the slide stack's height
   honestly, because every passive slide under hub 3 lifts the whole distal chain off the arm.
2. **Rawest material.** The posed render skin of every bench pose (signed distance per point, not a summary), the fit
   clips at their full 10 fps for continuity (pipeline/conformal/band_poses_wsf.b64: FI order, HG / RS rotations), and
   the skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) for where skin rises under a link.
3. **Methods and tools.** Closed-form spherical IK of the axis directions (Paden-Kahan subproblems) + exact offset drift
   t3(q) absorbed by the slides (s = Q^T t3); Grubler-Kutzbach mobility; sphere tracing on the bench's signed-distance
   grid to fit each rigid underside to the envelope of the skin over the poses it takes (the band evaluator's free
   underside with <= 60 deg ramps); exact cylinder / box signed distances for part-part clearance; a coarse-then-
   coordinate sweep of the 6 offsets and the slide ranges on the common bench.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, same metrics, same contact
   rule as tools/concept_baseline.py's spherical 3R: 68.93), the adversarial verifier that re-runs the model, and the
   red-team pose list below (the pose that jams, the point that pinches), plus the slide-travel histogram per pose.

## Spec correction (measured)

The catalogue entry asks for 3 revolutes + **2** passive slides (along / across the humerus). That loop cannot close:
the arm turns about GH with 3 DOF, a 3R + 2P chain has 5, and the loop scapula -> chain -> cuff -> humerus -> GH has
mobility 5 + 3 - 6 = 2, so with non-concurrent axes the cuff is reachable only on a 2-D subset of arm orientations.
Kinematics scan on Bench(60,160) (`python3 docs/concepts/models/seed-offset-3r-slides.py kin`): with the 2 slides,
5 mm of offset on R1 leaves 27 % of clip frames and 8 % of workspace poses; 5 mm on R2 13 % / 21 %. The exception:
offsets on R3 alone - the drift (R3^T - I) c3 stays in the slide plane, so the spec's 2 slides are exact there. The
model therefore uses **3 passive translations** (along the humerus, across it, normal to the carriage): the chain's
orientation is then exactly the spherical IK of the three axis directions (so q, branches and the J2 fold are the
spherical chain's), and the offsets appear as a pose-dependent drift t3(q) absorbed by the slides, s = Q^T t3.
Loop mobility 3 + 3 + 3 - 6 = 3 = the arm's: 3 ACTIVE DOF, 3 PASSIVE DOF, each slide set by closure (none sags).

## Model (docs/concepts/models/seed-offset-3r-slides.py)

* Axis directions = the champion spherical 3R (r20 s1414 #4) + sweepable deltas (`d_az, d_el` base axis, `d_a1, d_a2`
  link angles, `d_wd, d_wa` humerus axis); each axis line moved off GH by an offset (`o1a..o3c`, mm, along / across
  its link).
* Parts at real size: O20 x 12.25 hubs (HARDWARE.md v5 joint, upper member from F + 3.15); links 8 x 3 mm straps with
  a free-shaped underside fitted 2 mm off the skin over every pose taken, <= 60 deg ramps to the hub levels; slide
  stage = arm-fixed rail 8 x 4 x (20 + 2 S_a), along-carriage 20 x (20 + 2 S_t) x 4 carrying the across rail,
  across-carriage 20 x 20 x 4, radial slide +-R_r, 0.5 mm running gaps. `S_auto` sizes each range to the travel the
  fit set needs + 0.5 mm.
* Two stage layouts: **under hub 3** (the carriage IS hub 3's lower plate - the stack lifts hub 3 and link 2 by
  9 mm + R_r) and **remote** (`remote=1`: hub 3 + a `neck` strap form member 3 at their own fitted height; the stage
  sits down the arm past the neck).
* A pose is taken iff the spherical IK closes on the design branch >= 10 deg from the J2 fold, every slide is within
  range, no joint jumps > 25 deg between consecutive full-rate (10 fps) clip frames, non-adjacent parts keep >= 1 mm
  (hub cylinders and slide boxes exact, straps as mid-surfaces), and no metal is inside the skin (side walls and
  carriage edges checked for contact too). Poses whose skin would force a rigid part up are dropped greedily while
  that lowers the gap - they are recorded with their metal inside the body (= contact, not taken), the baseline's
  percentile convention.
* `slides=0` is the in-model spherical reference (the champion chain with an arm-fixed hub-3 block and a 25 mm neck):
  it isolates what the offsets and the slides add or cost on this model's fitting rules.

## Results (Bench(60,160), fast grid; sweep log docs/concepts/sweeps/seed-offset-3r-slides.json, 360 configurations)

| configuration (same model, same rules) | gap | reach | follow | in-band 2-14 | 2-10 | contact |
|---|---|---|---|---|---|---|
| bench baseline (tools/concept_baseline.py, champion spherical 3R) | 68.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |
| in-model spherical reference, champion directions (k 348) | 62.58 | 0.750 | 0.917 | 0.574 | 0.354 | 0.116 |
| in-model spherical control, best re-tuned directions (k 351) | 58.79 | 0.750 | 0.917 | 0.616 | 0.385 | 0.121 |
| slides under hub 3, best (stage 1-2, k 151, zero offsets won) | 64.04 | 0.738 | 0.917 | 0.586 | 0.404 | 0.131 |
| remote stage + ramped neck, offsets zeroed (k 350) | 65.23 | 0.719 | 0.917 | 0.604 | 0.374 | 0.141 |
| R3-only offsets = the spec's 2 slides (exact), best (k 355) | 65.41 | 0.725 | 0.917 | 0.595 | 0.365 | 0.141 |
| **best: remote stage + ramped neck + offsets (k 324)** | **57.95** | 0.769 | 0.917 | 0.595 | 0.350 | 0.110 |

Best configuration (k 324): offsets o1 (+1.6, -5.6), o2 (+1.6, -4.0), o3 (-0.3, +4.8) mm; directions d_az +1.7, d_el
-6.4, d_a1 +2.1, d_a2 -1.4, d_wd +4.1, d_wa +3.6 deg; slide travel needed 12.5 / 8.7 / 6.2 mm (ranges 13.0 / 9.2 /
6.7); stage 5 mm past hub 3's rim; faces f1 56, f2 90, f3 64 mm. In band per part: hub 1 100 %, hub 2 2 % (median
28 mm), hub 3 98 % (median 10 mm), link 1 82 %, link 2 60 %, rail 61 %, along-carriage 23 % (median 18 mm).

**Decomposition (what the morphology itself buys).** At the same directions: the slide stage alone costs +6.4 gap
(65.23 vs 58.79: its 9-13 mm stack and the 20 x 38 mm carriage stand off the arm); R1/R2 offsets buy back 7.3
(57.95), mostly by letting hub 3 sit 98 % in band and lowering the skin-dropped poses 28 -> 22. Net vs the spherical
control: -0.84, inside the noise of the greedy pose dropping. R3-only offsets (the spec's own 2-slide version) never
beat 65.4. The 11-point gain over the bench baseline is the model's free-underside fitting (62.58 at the champion's
own directions) plus a direction re-tune (58.79) - both belong to the spherical family, not to this morphology.

## Red team (best configuration)

* **The pose that jams.** 19 poses are lost to the J2 fold (>= 10 deg margin): the five top frames of *Raise
  overhead* (plane 30, elev 124-150, axial -55..-60) and behind-the-back workspace poses (plane -60..-90, elev 30-60,
  axial 105-165) - the same branch fold as the spherical chain, offsets cannot move it (the orientation IK is the
  spherical one). 22 poses are lost to the skin (metal inside): abduction / flexion 90-150 deg at small axial rotation
  (plane -15..30, axial 0..15) and elev 165 - there the elevated upper arm occupies hub 2's place (hub 2's ray starts
  inside the body: needed face height unbounded). Named groups: rest 5/5 taken, overhead 22/41, across-the-body
  31/36, behind-the-back 11/19.
* **A metric hole found and closed.** Before the fix the sweep reached gap **49.15**: link 2 jammed against the
  along-carriage in 19 overhead poses, and a jammed pose was recorded as "not taken" (costs reach only) instead of
  "contact" (costs reach + contact), although the fitted shape had already given those poses up to the skin. With
  `jam_contact=1` (a skin-dropped pose stays contact even where parts also collide) the same configuration scores
  57.95; every number in the table above is under this rule. Verifiers: check other models for the same hole.
* **The point that pinches.** Lowest metal over poses taken: link 1 at 0.43 mm (arm at the side, internal rotation
  75 deg, plane 15), link 1 at 0.52 mm (plane -30, elev 15), link 1 0.79 mm (elev 165), hub 3 rim 0.94 mm (plane 45,
  elev 75, axial 45), rail 1.44 mm - taken by the bench rule (>= 0) but inside the 2 mm target: link 1's underside is
  fitted to the envelope, so its lowest poses graze.
* **Slides.** All three passive translations are set by closure (no undetermined coordinate); the travel needed
  (12.5 / 8.7 / 6.2 mm) is inside the ranges for every pose, no flip between consecutive 10 fps clip frames. The
  member-3 riser from the neck down onto carriage B is not sampled (vertical, not skin-facing); the neck section over
  the stage is above the stage by construction (>= 4.5 mm).

## Verdict

**Screened, not worth its own GPU sweep.** The offsets do one real thing - with a free 3-axis slide stage they let
hub 3 sit over quiet skin (98 % in band) - but the stage's own height and footprint cost as much as that buys; the
net is -0.8 gap against the spherical chain with the same directions, inside the noise. The measured limiter of the
whole family is untouched by offsets: hub 2 (2 % in band, median 28 mm, set by the overhead poses where the arm
occupies its place) and the J2 fold (19 poses). Hand the direction deltas (d_el -6.4, d_wd +4.1, d_wa +3.6 deg) to
the spherical GPU sweep; a morphology that wins must move or remove hub 2 over the deltoid in abduction 90-150 deg.

## Files

* model: docs/concepts/models/seed-offset-3r-slides.py (`kin`, `check`, `sweep`, `sweep2`, `sweep3`, `sweep4`,
  `reeval`, `redteam` modes; ~3 s per configuration on the fast grid)
* sweep log: docs/concepts/sweeps/seed-offset-3r-slides.json (in order; `asked` = the parameters as given, `params`
  = with the resolved slide ranges; entries before k 324 without `jam_contact` use the old jam rule)
* sketch: docs/concepts/img/seed-offset-3r-slides.png (lowest-elevation and highest pose taken, best configuration)

## Verification (adversarial verifier, 2026-10-15)

Verdict: **verified** - the corrected gap on Bench(110, 360), exact path, is **66.47** (baseline 68.93). The
morphology stays ahead of the baseline, but by 2.5, not 11. The verifier's checks are a subclass of the model
(VModel: closure, extra clearance pairs, missing part, jam rule), run on the best configuration (k 324, `asked`
parameters, refitted on each bench by the model's own procedure).

| check | result |
|---|---|
| 3 ACTIVE DOF, no undetermined passive coordinate | holds: R1-R3 set the orientation, and the 3 slides are solved by closure (s = Q^T t3); loop mobility 3 |
| closure residual (R1 R2 R3 vs the arm, < 0.5 deg; position closes through the slides) | max 0.015 deg over the poses taken: no pose lost |
| joint / slide ranges, 10 fps branch continuity | enforced in the model (fold 10 deg, S_auto ranges, 25 deg step); no flips |
| part-part pairs the model skipped: hub 3 vs rail and carriage A, carriage B vs rail, bridge vs rail and carriage A | added: min 2.0 / 18.0 / 7.9 / 7.9 / 3.8 mm over the poses taken (rail runs under hub 3's rim with 2 mm to spare): no pose lost |
| adjacent pairs checked anyway (exempt by the rule): link 2 vs the member-3 neck, carriage B, bridge | min 10.6 / 11.8 / 15.3 mm |
| **missing part**: member 3 had no link between the neck end (hub 3 rim + neck) and carriage B's near edge (+ S_a); with `stage_c` placing carriage B S_a further, a 13 x 8 mm gap was left | added a bridge strap with its underside at carriage B's underside (the most favourable height): 24 samples, 0 % in band (median 27 mm), **+1.68 gap** (57.95 -> 59.63 on the fast grid) |
| jam rule: a skin-dropped pose with a part-part jam but no metal inside counted as taken | fixed (such a pose is not taken); 0 poses affected for this configuration |
| grid-cache artefact (CB_EXACT=1, Bench(60,160), all fixes) | exact 58.38 vs fast 59.63: no artefact in the model's favour (the exact path is 1.25 better) |
| **re-measure on Bench(110, 360), exact path, all fixes** | **gap 66.47**: reach 0.761, follow 0.918, in-band 14 0.502, in-band 10 0.259, contact 0.096 |

The larger bench costs +6.8 gap in all. On the larger bench, hub 2 must rise to f2 98 mm (90 before); it is then
0 % in band, median 37 mm. Link 2 drops to 40 % in band (median 17.5 mm). The along-slide needs 15.2 mm of travel
(13 before). 51 poses are lost to the J2 fold and 40 to the skin. In-band 14 falls from 0.595 to 0.502. The screened
57.95 came from fitting the free undersides on the 220 poses the bench also scores. With more poses, the envelope
includes more of the high-skin overhead poses. Hub 2 and link 2 absorb most of that.

Holes that remain, not quantified:
* The radial slide (+-6.7 mm, normal to the carriage) has no guide hardware in the model. Carriage B floats on a gap
  of R_r. Pins or a bushing need about 2 R_r of stroke plus their engagement length. Pins fixed in carriage A and
  poking up through carriage B do not touch the skin, and their envelope clears link 2 by 9.6 mm. They do add height
  and mass.
* The member-3 neck breaks the model's own 60 deg ramp rule. It rises from hub 3's plate (64 mm) to 80 mm at the
  hub rim, a vertical riser. The riser has to clear the rail, which slides under it. It is not skin-facing.
* The baseline's 68.93 is on Bench(60,160), fast grid. Nobody has re-run the baseline on Bench(110,360). If the
  larger bench costs the spherical chain the same ~7 points, the margin over it is larger than 2.5.
* The author's verdict stands, with a smaller margin: the in-model spherical control at the same directions
  (58.79 fast) is within noise of this morphology, so the gain comes from the fitting and the direction re-tune,
  not from the offsets and slides. This verification did not re-run that control on the large bench.

## Convergence and red team (leader stage 1, 2026-10-15)

**Objective made honest first.** The verifier's checks now live in the model (`VModel`, `bench_eval` hook for
tools/concept_sweep.py / the farm; `vfix=1`): closure residual, hub 3 / bridge vs rail and carriage A, carriage B vs
rail, the missing member-3 bridge strap, dropped-and-jammed poses never taken - plus the red team's **riser** (below).
Same configuration (k 324), Bench(60,160) fast: screening model 57.95, verifier checks 59.63 (the verifier's own number,
reproduced), verifier checks + riser **79.75**.

**Convergence gate on the screening log (360 tries; staged coordinate search, two jam rules mixed): NOT converged** -
the best gained +5.13 score points over the second half and +2.27 over the last third (top-5 within 0.34); the best,
k 324, is try 324 of 360. The 33 tries under one rule (`jam_contact`) are re-evaluations of the top, not a search.
So: **CMA-ES on the cloud farm** (scratch driver: 13 parameters = 6 offsets, 6 direction deltas, neck length; lambda 16,
sigma0 2 mm / 2 deg / 4 mm; start k 324 with neck 13; objective = VModel gap on Bench(60,160) fast; every try appended
to the sweep log with label `cma1 <population> g<gen>`). Cost: ~2 s per configuration on a worker, 18 s wall per
generation on an idle farm, 160-400 s when the other screening agents fill the 4 shared slots (queue 14 at 21:55 UTC -
the farm, not compute, sets the pace). First 48 tries: best **54.95** (k 403, score 80.02; reach 0.800, follow 0.917,
in-band 14 0.573, contact 0.090; faces 57.6 / 94.4 / 65.2; neck 17.6 mm, no riser) - gate not yet passed (+1.16 over
the second half). The loop keeps running unattended and appends its final gate numbers below.

**The pose that jams (new, measured): the member-3 riser.** Member 3 at hub 3 is the LOWER plate (F..F+3; the boss and
cap above it turn with link 2, docs/HARDWARE.md v5). The screened neck (5 mm, ramped at 60 deg down from carriage B's
top) reaches hub 3's rim 14.4 mm above that plate, so member 3 needs a 14.4 mm vertical wall at the rim (the verifier
noted it as "not skin-facing" and left it out). Modelled as a 3 x 8 mm box on member 3 and checked like every other
part: the along-slide carries the arm-fixed cuff rail under hub 3's rim (2 mm off the hub) straight into it - **24 of
220 poses jam (riser vs rail < 1 mm)**, gap 59.63 -> 79.75. Fixable by geometry: a neck >= (carriage B top - f3) /
tan 60 deg ~ 12.3 mm ramps from the plate itself (no riser): k 324 with neck 13 = **58.59** (one adjacent riser-link 2
pose left at 0.3 mm of riser). Every CMA try carries this check.

**Variants (say which and why).** (i) `flip3` - member 3 as hub 3's UPPER member, the neck leaving the boss wall (up to
F+7.25): attacks the riser. Neck 5: still a 7.2 mm riser, 19 poses jam, 76.22; neck 8: 61.97; neck 13: 58.54 vs 58.59
unflipped - nothing to gain once the neck is long enough, dropped. (ii) **`branch=+1` - the one variant aimed at the
measured limiter.** The limiter is hub 2 (0-2 % in band, median 28-37 mm; its face is set by abduction / flexion
90-150 deg where the raised arm occupies hub 2's place) plus the J2 fold. Offsets move hub 2 by millimetres (sweep 3's
+-25 mm offsets did nothing); the other IK branch puts J2 on the mirror side of the u1-w plane. At the k 324 directions
it is far worse: **218.54** (100 of 220 poses with metal in the skin, reach 0.20, follow 0.43): hub 2 then sits where
the trunk and the raised arm are in most poses. A 16-per-generation CMA population (sigma 5 deg / 5 mm) runs beside
the main one; its result is appended below.

**Optimistic numbers (named; measured where finished).** (1) Fit on the scored poses: the free undersides are fitted
to the very poses the bench scores; the frozen-shape transfer test (fit on Bench(60,160), wear on Bench(110,360), no
refit) runs on the farm, exact path. (2) The greedy pose drop makes the objective noisy (+-1.5 gap between neighbours
whose contact share differs by 1-2 poses): the CMA best is a selection maximum, so the exact large-bench re-measure, not
the fast sweep number, is the claim. (3) Still unmodelled: the radial-slide guide (pins or bushing, ~2 R_r stroke +
engagement, not skin-facing), part-part clearance of strap mid-surfaces sampled at 2 mm (not exact solids).
