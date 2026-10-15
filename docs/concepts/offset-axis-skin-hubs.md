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
