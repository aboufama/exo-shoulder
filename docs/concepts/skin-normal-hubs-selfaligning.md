# skin-normal-hubs-selfaligning - skin-normal hubs + passive cuff translation stage (non-concurrent 3R)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Make the morphology a continuous
   family that CONTAINS the verified state of the art, so the sweep can only lose to it by measurement, never by
   construction: each hub line goes through its skin seat with direction nlerp(seat ray, skin normal, beta), beta 0 =
   the line through GH (the spherical 3R), beta 1 = the hub square on its seat. Seat the champion's own axes first
   (J1 bvec(2.4, 80.7), J2 at its rest-pose axis bvec(30.6, 4.9), J3 wdir(86.3, 21.8)) and only then wander to the
   spec's acromion / supraspinous seats. Reuse the verifier-checked closure (seed-offset-3r-slides: orientation = the
   spherical IK of the axis DIRECTIONS, the line offsets become a drift of member 3 that 3 passive slides absorb
   exactly), and close the verifier's open hole in it (the member-3 bridge strap between the neck and the
   across-carriage, +1.7 gap there) instead of inheriting it. Price the stage: the drift grows with the line
   offsets (2 d sin(q/2)), so cap each slide (S_max) and let the bench see the metal.
2. **Rawest material.** The posed render skin of the rest pose (seat points and mean face normals within 10 mm, libigl
   exact distance - not the grid), the posed skin of every bench pose through the bench's signed distance, the fit
   clips at their full 10 fps for continuity (pipeline/conformal/band_poses_wsf.b64), and the skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) / proximity atlas for where the hubs can sit.
3. **Methods and tools.** Paden-Kahan spherical IK on the axis directions + exact line-offset drift (screw
   composition X_k), Grubler-Kutzbach mobility of the loop scapula -> chain -> stage -> humerus -> GH, sphere tracing
   on the signed-distance grid for every underside, exact cylinder / box signed distances for part-part clearance,
   CMA-ES (pycma) on the cloud CPU farm from the top of a 239-configuration coarse design of experiments.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, same metrics as the
   baseline 68.93 and the verified leaders), the in-model references run in the same sweep (the champion seats at
   beta 0 = the seed-offset family's spherical control; slides 0 = no stage), the adversarial verifier, and the
   red-team list below (the pose that jams, the point that pinches, the optimistic number).

## Spec corrections (measured)

* **The passive stage needs all 3 translations** (as the spec says, and as seed-offset-3r-slides measured): the arm has
  3 rotational DOF, the chain's orientation is the spherical IK of the 3 axis directions, and the line offsets leave a
  3-D drift of member 3; with 3 slides the loop has mobility 3 + 3 + 3 - 6 = 3 = the arm's. 3 ACTIVE, 3 PASSIVE, each
  slide set by closure (residual 0: the slides take s = Q^T t3 exactly), none undetermined (R17).
* **"Hub square on its seat" (beta 1) costs 62 / 46 / 36 mm of slide travel** at the champion seats (line offsets
  23 / 19 / 15 mm from GH: the seats sit 50-90 mm from GH with 20-29 deg tilt, so d = r sin(tilt)). Travel grows
  about linearly with beta (table below), so beta 1 is out of the spec's +-25 mm and its 145 mm rail lands on the arm
  (gap 150, rail median 28 mm). The model therefore sweeps beta in [0, 1] per hub (0 = through GH).
* **Centre the slide ranges.** The drift is one-sided (along-slide -23..+1 mm at the first optimum): an arm-fixed rail
  centred on the mid travel halves its length. Every reported number from k 291 on uses `centre=1`.
* **Missing part closed**: the member-3 bridge strap between the neck and the across-carriage (the verifier's finding on
  seed-offset-3r-slides, +1.7 gap there) is in this model, scored, and checked against the rail and carriage A.
  Added a static hub 1 / hub 2 cylinder clearance (both are fixed in member 1; the seed never needed it at a1 77 deg,
  here a1 is 36-38 deg; 16.6 mm at the best).

| beta (all hubs, champion seats) | line offsets mm | slide travel max mm (along, across, radial) |
|---|---|---|
| 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| 0.2 | 4.7 / 4.2 / 3.1 | 9.4 / 7.9 / 5.5 |
| 0.3 | 7.2 / 6.3 / 4.7 | 16.7 / 11.9 / 8.3 |
| 0.5 | 12.0 / 10.4 / 7.8 | 29.6 / 20.2 / 14.0 |
| 1.0 | 23.2 / 19.3 / 14.7 | 62.3 / 45.8 / 36.3 |

(fit clips + workspace of the pose file, closing poses; J3-only beta 1 needs no radial slide: the R3-only drift stays
in the slide plane.)

## Model (docs/concepts/models/skin-normal-hubs-selfaligning.py)

Subclass of the verified seed-offset-3r-slides model (imported, unchanged): same hubs (O20 x 12.25, upper member
from F + 3.15), 8 x 3 mm links with skin-fitted undersides (<= 60 deg ramps), remote slide stage (arm rail 8 x 4 x
(20 + 2 S_a), along-carriage 20 x (20 + 2 S_t) x 4, across-carriage 20 x 20 x 4 on a radial slide of +-R_r, 0.5 mm
running gaps), hub 3 + ramped neck + bridge = member 3, S_auto ranges (needed travel + 0.5 mm, capped at S_max),
10 fps continuity on the full clips, 1 mm part-part clearance (cylinders / boxes exact), jam_contact, greedy skin-pose
dropping recorded as contact. What is new: the axis LINES come from skin seats on the rest pose (lowest-elevation
non-held-out pose of the pose file, plane -90, elev 0: bench-independent), mapped to the closure's home frame by the
spherical IK at that pose; `centre`; bridge; hub 1 / hub 2 check. Parameters: J1 seat (az1, el1, b1), J2 rest seat
(az2, el2, b2), J3 seat on the arm (wd, wa, b3: band humerus frame), S_max, centre.
