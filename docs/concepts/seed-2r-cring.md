# seed-2r-cring: 2R spherical shoulder + C-ring axial bearing on the upper arm

## Deeper-version prompt, answered before the work

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the ring as what it is: the third
   joint of a spherical 3R whose last axis is the humerus long axis. So (a) choose u1 from the measured cloud of arm
   directions in the scapula frame so that d never comes near u1 or -u1 (the 2R's gimbal lock is the only singularity;
   it decides reach before any proximity question); (b) let the ring axis tilt a few degrees off the GH-elbow line so
   the circle is centred on the real arm cross-section at its level (the track must be a circle about an axis through
   GH, the arm is an oval that is not centred on that line); (c) put the C opening where the carriage never goes AND the
   torso is (measure both, do not assume "medial"); (d) hang the passive slide on BOTTOM's bar (it already runs down
   the arm, parallel to the slide) instead of adding a new body; (e) check the ring's outer face against the torso,
   not only its inner face against the arm.
2. **Rawest material.** The posed render skin of every bench pose through the signed-distance grid (not a digested
   radius table): the ring radius is fitted per azimuth and level directly on it; the fit-clip frames in time order for
   continuity; the arm-direction and carriage-azimuth clouds computed from the pose frames themselves.
3. **Methods and tools.** Spherical-linkage closure (two-cone intersection, branch kept by sign), singularity margin
   on the cone angles, K3 skin march for straps, a Lipschitz march on the signed distance for the ring radius, dense
   continuity along the slerped motion (K2), part-part clearance (K6) plus by-construction clearances for the
   ring / carriage / slide that the shell model of K6 cannot represent; the shared kit (tools/concept_kit.py) for all
   of it except the fixed-geometry ring.
4. **What shows the number is right, other than me.** tools/concept_bench.py (fast grid, Bench(60,160)), the
   adversarial verifier re-running on the exact path, and a red-team pose list (rest, overhead, across the body,
   hand behind the back, full axial rotation at 90 deg abduction) with the pose that jams and the point that pinches.

## Verdict: dead (best gap 129.98 vs 68.93 for the spherical 3R champion, same bench)

Bench(60, 160), fast grid cache, kit conventions (K3 `march`, K2 dense continuity, K6 collisions, kit O20 hubs).
Best of 25 configurations (sweep entry 8, `docs/concepts/sweeps/seed-2r-cring.json`):

| reach | follow | in-band 14 | in-band 10 | contact | gap | closure | flips | Ti mass |
|---|---|---|---|---|---|---|---|---|
| 0.4437 | 0.7333 | 0.3886 | 0.2552 | 0.1154 | **129.98** | 0.61 | 0 | 148 g |

Params: u1 = bvec(125, 45) in the scapula frame, a1 = a2 = 90, branch sigma -1, track at L = 100 mm along an axis
tilted 18 deg (toward azimuth -30) from the GH-elbow line, inner radius 57.2 mm (q_ring 0.9), C span 122.5 deg centred
lateral (opening 237.5 deg, carriage offset 65 deg from p2's plane), 10 x 3 mm straps, q 0.95. Closure residual 0.0 deg,
min singularity margin 22 deg, audit clean (`honest` true). Per member in-band 14: hub1 0.06, hub2 0.11, link1 0.50,
link2 0.73, track 0.13, carriage 0.00, slide 1.00.

## What was built (spec corrections, said plainly)

* Rebuilt on the shared kit; the interrupted session's 535-line model (own frames, closure, fitting, a 30 deg
  per-frame flip rule) was replaced.
* **Spec was wrong: "C-ring axis = humerus long axis".** On this body the GH-elbow line runs only 3-8 mm under the
  skin at 110-140 mm from GH at rest and leaves the skin overhead (elev 165: +4.5 mm outside at 110-140 mm). A circle
  about it cannot hug the arm. The track axis is a humerus-fixed axis through GH tilted 6-18 deg (swept).
* **Spec was wrong: the opening is not free to put "medial".** The carriage's azimuth round the arm is p2's azimuth,
  which turns 1:1 with axial rotation: the carriage has to travel 222 deg of the arm's circumference for 95 % of the
  closing poses. The opening is derived from that cloud (smallest arc holding a share `cov` of the poses) and the
  carriage offset centres the C laterally, opening toward the torso.
* Passive slide (40 x 10 x 6 mm rail + block on the cuff side) at the C's end, determined by the loop (= GH translation
  along d3, zero on the fixed-GH rig): counts as metal, never undetermined.
* The track and the carriage are fixed geometry (a rotary track is a surface of revolution); their radius is fitted on
  the posed skin by a Lipschitz march on the signed distance, not by the kit's per-sample K3. Outer faces (track R + 6,
  carriage top) are checked for torso contact. Part pairs that ride the arm axis (track / carriage / slide / link 2's
  end) are clear by construction; every other pair goes through K6.

## Limiter (measured)

1. **Axial travel vs a circular track (dominant).** A circle about any GH-through humerus-fixed axis fits the arm only
   over about +-60 deg of its lateral side: required inner radius (median pose / 90th percentile) 49 / 57 mm at
   L = 100 for a +-60 deg span vs 73 / 87 mm for the +-110 deg span the carriage needs (37 / 43 vs 70 / 94 at L = 160).
   So either the C is short (cov 0.6: closure 0.61, 75 of the 89 workspace poses lost and 11 of 16 clip frames lost
   are "carriage outside the C") or it covers the travel and floats 25-45 mm off the arm (cov 0.95: R 86.5, contact
   0.80, gap 283). Track in-band 14 never exceeds 0.20; the carriage, riding on the track's outer face, never in band.
2. **2R pointing of the humerus needs long links.** Keeping the arm-direction cloud inside the closure annulus needs
   a1 + a2 ~ 180 deg (best margin to both u1 and -u1: 33 deg at u1 = bvec(125, 45)); the 90 deg arcs sweep over the arm
   on branch +1 (links never in band: their K3 rays run along the arm, 400 mm placeholders); branch -1 keeps link 1 / 2 at
   0.50 / 0.73 in band. Asymmetric arcs (100 / 80) or u1 = bvec(95, 25) are worse (156-158).
3. **Variants tried to remove limiter 1:** full-coverage C (gap 283); a non-circular cam track fitted per azimuth with
   the carriage on a radial slide (track in-band 14 0.88 on its own, but the per-azimuth envelopes over poses leave
   some column in contact in almost every pose - the skin moves round the humerus by more than the clearance; one
   evaluation, its outer-face check still used the mean circle, so it is reported as indicative only, not in the sweep).

## Red team (best config)

| pose | result |
|---|---|
| rest (clip, elev 4) | taken, min 2.7 mm |
| overhead (clip, plane 30 elev 150 axial -60) | **contact: hub 1 6.0 mm inside the skin** |
| abduction 75 + external rotation 90 (ws) | **jams: carriage at psi -106 outside the C (+-61)** |
| abduction 75 + internal rotation 90 (ws) | **jams: carriage at psi +61, at the C's end** |
| across the body (plane 135 elev 90) | taken, min 5.5 mm |
| hand behind the back (plane -90 elev 15 axial 90) | taken, min 1.3 mm (link pinch) |

Pinch points in taken poses (closest metal to skin): link 2 0.26 mm (plane 120, elev 0, axial -75), track 0.31 mm
(plane 120, elev 30, axial -135), link 1 0.27 mm (plane 60, elev 135), slide 1.6 mm, hub 1 1.8 mm. Not taken: ws 75
carriage outside C, 12 contact, 2 part-part; clip 11 / 3 / 2.

## New knowledge (predicts beyond this morphology)

* Any humerus-fixed, arm-encircling rotary track on this body is limited by the arm's cross-section about axes through
  GH, not by the torso: lateral +-60 deg fits within 49 / 57 mm (median / p90) at 100 mm, the full +-110 deg needs
  73 / 87 mm. A J3 that encircles the arm must therefore cover at most ~120 deg of travel, i.e. the axial rotation
  must be shared with another joint (or the track must move with the skin).
* The rig's GH-elbow line is eccentric in the arm (3-8 mm under the skin at mid-arm at rest, outside it overhead):
  any concept that assumes "the humerus axis is the arm's centre line" will misplace parts by 30-40 mm; check with the
  posed skin before using it.
* For 2R / 3R chains on this body the closure branch decides proximity (sigma -1 vs +1: link in-band 0.50-0.73 vs 0.00
  at the same axes); sweep the branch first.

Model: `docs/concepts/models/seed-2r-cring.py` (`check`, `sweep2`, `refine`, `refine2`); sweep:
`docs/concepts/sweeps/seed-2r-cring.json`; row: `docs/concepts/rows/seed-2r-cring.json`.

## Audit (2026-10-15T19:25:00Z)

Verdict: **the death stands** (not refuted). Re-measured on Bench(60,160), fast grid, PARAMS = sweep entry 8.

* Reproduced exactly: gap 129.98 (reach 0.4437, follow 0.7333, in-band 14 0.3886, in-band 10 0.2552, contact 0.1154),
  closure 0.61, 0 flips, part-part 0.03. Per member in-band 14: link 2 0.73, link 1 0.50, track 0.13, hubs 0.06 / 0.11,
  carriage 0.00.
* Code checked against tools/concept_baseline.py and the kit: two-cone closure and residual are the kit's; the
  carriage azimuth = p2's azimuth round d3 + a constant is correct kinematics (link 2 carries both p2 and the carriage);
  the track-radius march stops at the first clear radius (does not punch through the torso), so it does not inflate R;
  the carriage counted as skin-facing metal follows the baseline's convention for stacked members; the outer-face torso
  check is a real-size check, not an over-strict one. No bug found.
* Ablation that isolates the limiter: the same config with the C covering all of the travel (cov 1.0) needs track
  R 94.7 mm and gives gap 325.24 (reach 0.12, follow 0.07, contact 0.85, track in band 0.01). Short C loses ~40% of
  closing poses to "carriage outside the C"; long C floats far from the arm and runs into the torso. No point of the
  cov axis comes near 79.
* One-line reason: a circular, humerus-fixed track round GH must cover ~222 deg of carriage travel but fits the arm
  only over its lateral +-60 deg, so coverage and proximity cannot both be met (measured: cov 0.6 -> 129.98,
  cov 1.0 -> 325.24).
