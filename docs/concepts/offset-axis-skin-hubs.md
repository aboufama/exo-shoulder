# offset-axis-skin-hubs - off-sphere skin hubs + passive cuff stage (axis directions spherical, axis lines free)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Not start from zero: two verified or
   screened relatives already ARE slices of this morphology (seed-offset-3r-slides: champion directions + small
   offsets; skin-normal-hubs-selfaligning: lines through skin seats, a 1-D offset per hub tied to the skin normal,
   best screened 35.86). Parameterise each axis line as a free direction + a free 2-D perpendicular offset (up to
   30 mm) so the family strictly CONTAINS both, seed it at their best lines (reproduced to 1e-5 mm), and spend the
   search on the freedom they did not have - the offset direction not tied to the normal, J1 pinned or not, the stage
   station down the arm, the travel cap. And before trusting any inherited number, run the inherited best under the
   verifier's full checks (the seed's VModel: closure residual, hub 3 / bridge vs rail, member-3 riser), because the
   relative that scores 35.86 was built on the screening Model, not the VModel.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (every
   underside fitted per sample, not a summary radius), the rest-pose render mesh (libigl exact distance) for the line
   seats, the fit clips at full 10 fps for branch continuity (pipeline/conformal/band_poses_wsf.b64), and the
   skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) / proximity atlas for where a hub's face can
   sit; the slide travel per pose (s = Q^T t3) straight from the closure, not a travel estimate 2 e sin(q/2).
3. **Methods and tools.** Paden-Kahan spherical IK on the axis directions + exact screw composition of the offset
   lines (the drift of member 3, absorbed by 3 passive slides), Grubler-Kutzbach mobility of the loop
   scapula -> chain -> stage -> humerus -> GH, sphere tracing on the signed-distance grid for every underside, exact
   cylinder / box signed distances for part-part clearance, a 240-configuration design of experiments and then CMA-ES
   (pycma) on the cloud CPU farm (tools/cloud_run.py sweep) until the convergence gate passes.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses and metrics as the 68.93
   baseline and the verified leaders); the verifier's own check code (seed-offset-3r-slides VModel), reused unchanged;
   the in-model references in the same sweep log (k 0-1: the relative's best lines under these checks); the adversarial
   verifier on Bench(110, 360) exact; the red-team list below (the pose that jams, the point that pinches, the
   optimistic number).

## Spec corrections (measured)

* **3 passive translations, not 1 along + 2 transverse in one plane.** With non-concurrent lines the drift of member 3
  (t3(q), exact screw composition) has a component normal to the arm too; the stage is along / across / radial
  (seed-offset-3r-slides measured the same: a 3R + 2P loop has mobility 2 with offset lines). Loop mobility
  3 + 3 + 3 - 6 = 3 = the arm's: 3 ACTIVE DOF, 3 PASSIVE DOF, each slide = Q^T t3 (closure residual max 0.015 deg),
  none undetermined (R17). The spec's travel budget (along +-40, transverse +-8) is the `S_max` cap per slide; a pose
  whose drift leaves the cap is not taken ("slide").
* **"Hubs lying flat on their own skin patch" is not a free choice of the hub position**: a hub's face height along
  its line is set by the skin envelope over the poses it is taken in (fitted, 2 mm), and its line is set by the
  direction + offset. What the morphology adds is the offset; its price is travel (2 e sin(q/2) per line, measured
  per pose from the closure). Free 2-D offsets up to +-30 mm per line (`O_MAX`).
* **The neck / stage station is a riser problem first.** The verifier's member-3 riser (hub 3's lower plate must
  climb to the neck's start height at the rim) jams the centred rail at short necks: see the red team.

## Model (docs/concepts/models/offset-axis-skin-hubs.py)

`Design`: J1 line direction bvec(az1, el1), J2 line direction at rest bvec(az2, el2), J3 line direction at rest
Q0 wdir(wd, wa) (band humerus frame), each line through GH + o_k (o_kx, o_ky in frame_of(d_k), scapula frame at the
rest pose = the lowest-elevation non-held-out pose, bench independent); the rest lines are pulled back to the closure's
home frame through the spherical IK at the rest pose (as skin-normal-hubs-selfaligning). `pin1` 1: the J1 line
through GH. `Model` = MRO Model -> skin-normal-hubs-selfaligning.Model (centred stage `centre`, travel cap `S_max`,
hub 1 / hub 2 cylinder check) -> seed-offset-3r-slides.VModel (the verifier's checks: closure residual < 0.5 deg,
hub 3 / bridge vs rail and carriage A, carriage B vs rail, the member-3 bridge strap, the member-3 riser, a dropped
pose that jams is never taken) -> seed-offset-3r-slides.Model (O20 x 12.25 hubs, 8 x 3 straps with skin-fitted
undersides and <= 60 deg ramps, remote slide stage: rail 8 x 4 x (20 + 2 S_a), along-carriage 20 x (20 + 2 S_t) x 4,
across-carriage 20 x 20 x 4 on a radial slide +-R_r, 0.5 mm running gaps, 1 mm part-part clearance, 10 fps branch
continuity on the full fit clips, J2 fold margin 10 deg, greedy skin-pose dropping recorded as contact).
Conversion checks (`k722`, `k403` modes): the skin-normal-hubs-selfaligning k 722 lines are reproduced to 4e-5 mm, the
seed-offset-3r-slides k 403 lines to 4e-5 mm and its VModel number exactly (54.95 = 54.95, every metric).

## Results (Bench(60,160), fast grid, verifier checks on; sweep log docs/concepts/sweeps/offset-axis-skin-hubs.json)

| configuration (same model, same rules) | gap | score | reach | follow | in-band 2-14 | 2-10 | contact |
|---|---|---|---|---|---|---|---|
| bench baseline (champion spherical 3R) | 68.93 | 74.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |
| seed-offset-3r-slides k 403 lines (its VModel number, reproduced exactly; k 242) | 54.96 | 80.01 | 0.800 | 0.917 | 0.573 | | 0.090 |
| skin-normal-hubs-selfaligning k 722 lines, its neck 5 (screened 35.86 without the verifier checks; k 0) | 148.06 | 46.16 | 0.169 | 0.267 | 0.899 | 0.519 | 0.065 |
| same lines, spherical control (lines through GH, no stage) | 45.68 | 83.39 | 0.638 | 1.000 | 0.741 | | 0.036 |
| same directions, offsets x0 (stage at minimum size) / x0.5 | 47.01 / 42.01 | | 0.638 | 1.000 | 0.728 / 0.778 | | 0.036 |
| **best: k 722 lines, neck 13 (riser 5.3 mm) (k 1)** | **37.78** | **86.26** | 0.656 | 1.000 | 0.784 | 0.324 | 0.018 |
| same directions, offsets x1.5 / x2 / x3 / x4 | 58.92 / 94.40 / 141.97 / 123.02 | | 0.54-0.46 | | 0.72-0.38 | | |
| best of 240-config DOE (free lines up to 30 mm, J1 pinned or not, neck 10-35, travel cap 8-40) | 49.12 | 82.14 | 0.663 | | 0.749 | | 0.036 |
| best of 96-config reach-side DOE (seed-offset directions, free lines) | 54.96 (= k 403) | | | | | | |
| best of CMA-ES from k 1 (local 48 tries sigma 1.2 deg / 1.8 mm; farm 64 tries sigma 1.6 deg / 2.4 mm) | 39.89 / 40.58 | 85.49 | 0.650 | | 0.769 | | |
| fold-frontier seed a1 60 deg (fold only 9 poses), both J2 branches, zero offsets | 119.16 / 148.39 | | 0.650 / 0.588 | | 0.326 / 0.411 | | 0.20 / 0.37 |

Best configuration (k 1): J1 line bvec(108.72, 62.15) offset (-4.55, -2.32) mm; J2 rest line bvec(32.35, 53.72) offset
(-6.09, 2.38); J3 line wdir(80.79, -11.26) offset (-5.84, 4.09) (frame_of(d), scapula frame at rest); line distances
from GH 5.1 / 6.9 / 6.8 mm; link angles a1 38.9, a2 68.3 deg; neck 13 mm; centred stage, half-ranges 7.8 / 8.1 / 6.7 mm
(travel 7.3 / 7.6 / 6.2 about mid - inside the spec's +-40 / +-8 budget except 0.1 mm across); hub faces 51 / 63 / 76
mm. In band 2-14 per part: hub 1 99 %, hub 2 94 % (median 12.1 mm), hub 3 81 % (11.8), link 1 96 %, link 2 90 %,
rail 87 %, along-carriage 56 % (13.5), neck 7 % (21.5), bridge 0 % (26.6). Why not taken: fold 51, skin 3, parts 1.

**What the morphology's own freedom buys, measured.** The spec's premise - free the axis lines by up to 30 mm so each
hub lies on its own skin patch - fails on travel: at fixed directions the slide travel grows ~2.8 mm per mm of line
offset (half-ranges 4 / 8 / 12 / 15 / 22 / 30 mm at offset scale x0.5 / 1 / 1.5 / 2 / 3 / 4), the stage grows with it
(rail 20 + 2 S_a, carriage 20 + 2 S_t) and jams link 2 and the riser (parts 1 / 16 / 51 / 60 poses at x1 / 1.5 / 2 / 3).
Over the 240-config DOE the median gap rises ~10 per +5 mm of rms line offset (74 at < 6 mm, 89, 98, 110, 117 at
> 20 mm). The optimum is 5-7 mm per line - exactly where the relatives already were - and is sharp (x0.5 42.0, x1 37.8,
x1.5 58.9). Nothing in 339 tries of the extra freedom (2-D offsets not tied to the skin normal, J1 pinned, longer necks,
the spec's travel caps, the reach-side directions with free lines) beat the relative's lines; the stage + offsets are
worth 7.9 gap over the spherical chain at the same directions (45.68 -> 37.78), the rest is the J1-lateral-acromion /
J2-posterior-superior layout found by skin-normal-hubs-selfaligning.

## Convergence gate (binding)

Over all tries in order (DOE 240 + reach-side DOE 103 + CMA): best gained **0.0** score points over the second half
(limit 1), **0.0** over the last third (limit 0.5), top-5 spread **1.54** (limit 3) -> **converged** by the rule. Honest
reading: the best is the seed (k 1), a CMA optimum of the relative's search re-measured under the verifier checks; my
search (DOE + 48 local CMA tries + the fold-seed CMA below) never improved on it, so the morphology is screened at the
relative's number, not above it. The farm CMA (16 per generation, sigma 1.6 deg / 2.4 mm, 4 generations, queued 23:11,
landed 23:37-23:43 behind the shared queue) reached 40.58; the local CMA (12 per generation, 4 generations) 39.89.

## Red team (best k 1)

* **The pose that jams.** The J2 fold takes 51 of 160 workspace poses (reach 0.656 = 24.4 of the 37.8 gap): overhead
  at elev >= 90 in planes -15..15 (#101-104, #113-116), behind the back at plane -90..-45 with axial 45-165 (#64, #67,
  #73, #77), across the body at plane >= 100 / elev >= 40. One link 1 - link 2 jam (#76, plane -45 elev 45 axial 30).
  Three skin poses (#91-93, plane -15, elev 75-105). Named groups: rest 5/5, overhead 24/41, across the body 22/36,
  behind the back 14/19. The Raise-overhead clip peak (elev 150) IS taken (follow 1.00).
* **The point that pinches.** Link 2 at 0.26 mm (#152, plane 60 elev 165 axial -90); hub 1 at 0.53-0.55 mm in the
  Raise-overhead peak frames (#4-#6) and #140; link 2 0.78 mm (#63). Taken by the bench rule (>= 0) but touches in
  practice. Lowest part-part clearance over the poses taken 1.12 mm.
* **The optimistic numbers.** (1) The undersides AND the slide ranges (S_auto) are fitted on the scored poses (the
  seed lost 6.8 gap on Bench(110, 360) for exactly this). (2) These lines are a selection maximum of the relative's
  CMA on the same 220 poses. (3) The radial-slide guide (pins / bushing, ~2 R_r stroke + engagement) is still
  unmodelled (inherited, not skin-facing). (4) The riser is a 3 x 8 mm wall; a real one needs its joint to the plate.
* **A number that was optimistic and is now fixed - for the relative.** skin-normal-hubs-selfaligning's screened
  35.86 runs on the seed's screening Model, which lacks the verifier's checks. Under them (same lines, its neck 5)
  the centred rail sits 4.8 mm toward hub 3 and runs into hub 3 (3 poses) and the 20 mm member-3 riser (120 poses):
  148.06. With neck 13 the riser is 5.3 mm and nothing jams: 37.78. Its verifier should re-measure with the riser on.

## The fold-frontier lead (new knowledge, partly negative)

A spherical-direction 3R (offsets or not) takes a pose only if theta = angle(u1, Q u3) lies in
[|a1 - a2| + 10, a1 + a2 - 10]. Scanning u1 above the shoulder (el >= 25 deg) and u3 radial on the arm (40-140 deg from
the humerus axis) over the bench poses: a1 39 reaches 0.89 ws / 0.93 clip, a1 45 0.94 / 1.00, a1 50-77 0.95 / 1.00
(scratch fold2.py; best pairs e.g. a1 60, a2 50, u1 bvec(128, 39)). So the fold alone does NOT force the trade between
a small J1-J2 angle (hub 2 low) and reach. But the fold-optimal pairs put the hubs on skin the arm sweeps: the a1 60
seed takes all but 9 poses kinematically and loses 38-76 to the skin (gap 119-148, hubs 1-3 10-20 % in band). The
best layout's reach 0.656 is a fold x skin limit; a CMA from the fold seed (local, sigma 4 deg / 6 mm) runs below.
