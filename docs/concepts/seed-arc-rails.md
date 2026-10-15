# seed-arc-rails - three concentric arc rails about the GH centre

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat each rail as what it is
   kinematically: a revolute joint with a remote axis through GH, i.e. a circle about that axis. A circle about an axis
   through GH is at ONE distance from GH everywhere, so the only freedom per rail is its polar angle rho about the axis
   (rho = 90: the spec's great circle; rho -> 0: a hub) and its radius. The designer would (a) measure first whether a
   great circle can lie on the skin at all (it cannot: a 190-250 deg great circle about GH runs through the neck, trunk
   or arm), (b) not fix the third rail on the humerus long axis (a C-ring needs ~250-300 deg of ring because the
   carriage's azimuth around the arm couples swing and twist), but put it about the axis the best spherical 3R already
   found (86 deg from the long axis), and (c) sweep rho per rail to see whether any rail between "hub" and "great
   circle" sits closer to the skin than the champion's links.
2. **Rawest material.** The posed skin of every bench pose (the rig's render skin, via the bench's signed distance), the
   fit-clip motions at their native 10 fps (closure, rail range and branch continuity are checked on EVERY frame of the
   fit clips, not only the 60 bench samples), the everyday-workspace envelope. The skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) is a digest; the bench skin is used directly.
3. **Methods and tools.** Exact two-circle closure of the spherical 3R (the band evaluator's, with its 10 deg fold
   margin); per-rail radius fitted by the baseline's percentile rule (sphere tracing on the bench's signed distance);
   every part at real size (rail 8 x 4, carriage 20 x 12 x 8, strap links 8 x 3) sampled on a 2 mm grid; part-part
   clearance by k-d tree on volume samples; the cached signed-distance grid Bench(60, 160).
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same metrics and poses as every other
   concept), the swarm's adversarial verifier, and a red-team pose list (rest, 170 deg overhead flexion/abduction,
   across-the-body adduction, hand behind the back) written below with the reason each fails or passes. The hub-like
   limit (rho ~ 12 deg) was run first as a calibration against the baseline (68.9): it lands at 80.7 at p100, the
   same family, which shows the model is not flattering itself.

## Morphology and model

Topology (scapula handler -> user's cuff): RAIL 1 fixed on the scapula handler, a circle about u1 (through GH) at polar
rho1 on the sphere R1 -> CARRIAGE 1 (20 x 12 x 8, its place on the rail = joint 1) -> LINK 1 (8 x 3 strap) -> RAIL 2, a
circle about u2 at rho2 on the sphere R2 -> CARRIAGE 2 (joint 2) -> LINK 2 -> CARRIAGE 3 -> RAIL 3 fixed on the cuff, a
circle about W (an axis fixed in the humerus through GH) at rho3 on the sphere R3 (joint 3). Every rail axis passes
through GH, so the chain is a spherical 3R: 3 ACTIVE DOF, each carriage driven along its rail. Passive DOF: 0 on the
bench (GH is fixed in the scapula frame there, so the chain closes exactly without the cuff slide the catalogue lists;
a slide would be an undetermined passive coordinate under R17 unless sprung - not modelled).

Spec changes, each measured (docs/concepts/sweeps/seed-arc-rails.json, stage tags):
* stage A, the catalogue spec (great-circle rails 1 and 2, C-ring about the humerus long axis): no finite radius
  exists - the rails' needed spans (190-270 deg) run into the trunk / neck / arm in every layout tried. Dead as specified.
* the third rail moved off the long axis to the champion's humerus-fixed axis (86.3 deg from the long axis, az 21.8);
  the C-ring needs ~300 deg of ring (swing-twist coupling of the carriage azimuth) and its medial part enters the trunk.
* the rails are crowns of polar rho1, rho2, rho3 about the champion's three axes (u1 az 2.43 el 80.68, a12 76.9, a23
  66.75, branch -1); rho -> 0 is the hub limit.

Model file: docs/concepts/models/seed-arc-rails.py (`check`, `sweep`; task API `metal(pose, frames, params)`).
Radii are refitted twice so carriage and strap footprints are at their real size at the fitted radius.

RESULTS_PLACEHOLDER
