# fivebar-roll: spherical five-bar pointer plus an active arm roll

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the two elbows as the only metal
   that has to cross the cap and choose the two base axes so that each elbow's circle (cone a_k about u_k) lies over
   the LOW skin of the cap for the poses it is used in, instead of one fixed nominal; check the parallel singularity
   along the actual clips (dense continuity), not only at the frames; and make the two couplers short so that the
   rigid links never have to clear the highest skin they pass over. Also check the coaxial (rhombus) variant: one
   base hub instead of two removes a 12 mm crown over the scapula.
2. **Rawest material.** The posed skin of every bench pose (the signed-distance grid of the rig's render skin), the
   fit motion clips densely interpolated between bench frames, and pipeline/conformal/analysis/skin_motion_map_14.json
   (where on the arm skin moves least: W* = wdir(112,-15)) - not the screen numbers in the catalogue.
3. **Methods and tools.** Spherical kinematics (two-cone closure K1 per leg, Gruebler count), the shared kit
   (tools/concept_kit.py: K3 march skin-fitted undersides, K4 flat O20 hubs, K5 straps, K6 collisions, K2 dense
   continuity), a vectorised coarse-then-refined sweep over the base axes, arcs, W and branches.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, Bench(60,160) on the fast
   grid cache, K3 march mode), the kit's audit (honest flag), the adversarial verifier on the exact path, and a
   red-team pose list (rest, overhead, across-body, behind-back, the pose with the least clearance on the best config).

## Result (Bench(60,160), fast grid cache, K3 march, K2 dense, K6 on)

**Dead: best gap 89.13** against the champion 3R's 68.93. Reach 0.631, follow 0.883, in-band 14 0.344, in-band 10
0.185, contact 0. Sweep entry k=13: a coaxial base at bvec(94.7, 83.7) (top of the shoulder, one double-row hub),
cranks 75 / 90, couplers 60 / 45, W = wdir(90, 0), branches -1 / -1, leg margin 5 deg, parallel margin 8 deg, q 1.0.
With the spec's margins (8 / 12 deg) the same design scores 90.30 (k=6). The model uses 231 g of Ti. Closure residual
is 0, there are 0 flips along the clips, and 8.9 % of the closing poses collide.

The 20 bench configurations are in `sweeps/fivebar-roll.json`. They were chosen by a skin-aware prefilter
(`prefilter` in the model) over about 17 000 random configurations, after a 6 000-configuration kinematic-only screen.

## What I changed from the spec, and why

- **The spec's base pair cannot be built.** Its preferred bases, bvec(-60,40) and bvec(-40,40), are 15 deg apart.
  At about 60 mm that puts two O20 hubs 16 mm apart, so K6 rejects every pose. The sweep therefore keeps the bases at
  least 22 deg apart, or makes them coaxial. The coaxial variant won.
- **The spec's arcs (crank 60 / coupler 120) are not wearable.** A 120 deg coupler passes over the neck or the torso in
  some closing pose, so its rigid level goes to 400 mm (the seed config scored gap 313). Without skin, kinematics is a
  bad guide here. The kinematic-only screen preferred bases on the anterior-inferior chest, which are buried under
  the skin. That is why the prefilter is built on the posed skin itself: a 3-deg scapula-frame map of the K3
  requirement in all 220 poses.
- The arm hub at W has two bearing rows (r 11.9, crown 16.3). The arm plate is at F, coupler 1 at F + 3.15 and
  coupler 2 at F + 6.3. The elbows are P14 pins (r 7, crown 8, one MR126 each), declared hubless. The couplers pass
  over the cranks, the neck and each other by construction, and K6 still checks every pair.

## Measured limiter (red team on the best config)

- **Proximity.** Coupler 1 sits at 82-137 mm and coupler 2 at 99-141 mm, with pins at 129 and 99 mm. Each of these
  is 0-1 % in band. When the arm goes overhead the elbows climb over the cap, and a rigid arc must clear the highest
  skin it ever passes over. Only the coaxial base hub (100 %), the W hub (56 %), the neck (68 %) and the cranks'
  near-base halves (24-42 %) are in band.
- **Reach dies overhead.** Workspace poses taken: 0.88 at elevation 0-60, 0.48 at 60-100, 0.38 at 100-140, 0.17 above
  140. Of the 160 workspace poses, 32 are lost to leg singularities (W leaves the annulus |a-c| .. a+c), 9 to the
  loop's parallel singularity and 15 to part-part collisions.
- **Pinch.** Crank 1 comes to 2.0 mm at plane 0, elevation 60, axial -60. That is the clearance rule exactly, not a
  contact.
- **The trade-off is structural.** On the prefilter front, the configurations with in-band >= 0.6 reach only 0.25-0.4
  of the workspace, and those that reach >= 0.8 put a coupler or an elbow at 120-400 mm. The W cloud in the scapula
  frame has a cone radius of 82-118 deg, so each leg's annulus must be at least that wide. That forces
  a + c >= ~120 deg per leg: four long rigid arcs over the moving cap, against the 3R's two.

## Verdict

Not worth a GPU sweep. Spreading the J2 load onto two two-force couplers does not remove the 3R's limiter, which is
rigid links clearing the highest skin they pass over. It doubles the problem. New knowledge: a 2-DOF spherical
pointer that must cover this W cloud (cone radius >= 82 deg about any base) needs arcs totalling at least ~120 deg per
leg. This holds for any parallel spherical pointer with rigid links (SPM legs included), so those families inherit
the same front unless their links move with the skin.

## Audit

An independent auditor re-ran the claimed best configuration (sweep k=13) on Bench(60,160) with the kit's honest checks (K3 march, dense K2, K6). It looked for a modelling bug, a convention that differs from the baseline's, or a check that is stricter than it needs to be.

- **Reproduced exactly:** gap 89.13, reach 0.631, follow 0.883, inband14 0.344, inband10 0.185, contact 0. Closure 0.768, 0 flips, and 8.9 % of closing poses collide.
- **Conventions:** the model uses the shared kit. The kit reproduces the baseline row exactly in `outer` mode. With the honest checks it puts the champion at 70.27, so the fair kit-to-kit gap is about 19.
- **Ablations on the same configuration** (none of them physical; they only bound how much a check costs):
  - K6 collisions off: 79.75. Reach rises to 0.725, in-band is unchanged.
  - Stacking off (`over` = []) with K6 on: 275. Every pose collides, so the stacking is necessary.
  - Each `over` pair dropped one at a time: coupler over neck changes nothing. Dropping coupler over crank 1, crank 2 or coupler 1 gives 148 to 275, so each of those pairs is needed.
  - Stacking and K6 both off: 66.64. This is the dishonest upper bound. Couplers reach only 20-22 % in band even there, and the elbow pins stay at 99 / 129 mm with 0 % in band.
- **Verdict: the death stands.** The measured reason: even with zero part-part clearance this configuration only ties the champion (66.6 against 68.9). Once the couplers stack honestly over the cranks and each other they lose all in-band (0 %), and the elbow pins climb to 99-129 mm over the cap. This is the proximity limiter of the morphology, not a modelling bug or an over-strict check. The prefilter covered about 17 k configurations, so the region tested was not the problem.
