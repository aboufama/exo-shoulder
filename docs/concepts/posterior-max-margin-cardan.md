# Posterior max-margin Cardan (posterior-max-margin-cardan)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the singularity margin as a
   *constraint* (enough margin for dense continuity, ~15-20 deg), not the objective, and spend the rest on proximity:
   a spherical 3R's in-band is set by how high each rigid arc must ride over the highest skin it ever sweeps, and a
   Cardan has the longest arcs (90 + 90 deg). So: (a) lay every part out at its real radius (a 12 mm strap at 130 mm
   is 12 mm wide, not 22), (b) fit the hub seats to the oblique skin (wedge) instead of flat discs that stand 10+ mm
   off one side, (c) test the shorter-arc variant (a1, a2 < 90) that trades margin for link length - the variant that
   removes the measured limiter if the limiter is arc length.
2. **Rawest material.** The posed skin itself (signed distance per bench pose, `Bench.dist` / grid cache), the six fit
   clips walked frame by frame and interpolated (`K.continuity_dense`), and the per-direction skin motion of
   `pipeline/conformal/analysis/skin_motion_map_14.json` to place poles over still skin - not the catalogue's summary.
3. **Methods and tools.** `tools/concept_kit.py` (K1 closed-form Cardan closure, K3 per-ray skin march, K4 O20 hubs,
   K5 straps, K6 collisions, K2 dense continuity), the singularity-margin landscape over the bench poses (Fibonacci
   grid over b and W), numpy-vectorised sweeps coarse then refined, a two-pass layout so every sample sits at the
   real radius of its part.
4. **What other than me shows the number is right.** The bench (`concept_bench`, same scoring as the 68.93 baseline
   row), the in-model control (the kit template = the champion 3R on the same kit conventions, 70.19), the
   adversarial verifier re-running on the exact path / full bench, and a red-team pose list (behind-back plane
   -60..-90, overhead elevation >= 150, across-body, back-pocket) reported per pose with the part that pinches.

## Result (Bench(60, 160), fast grid cache, K3 `march`, K2 dense continuity, K6 on)

| | gap | reach | follow | in-band 14 | in-band 10 | contact | min margin | Ti mass |
|---|---|---|---|---|---|---|---|---|
| baseline row (champion 3R, its own conventions) | 68.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 | 13 | |
| kit template (champion 3R, kit conventions) | 70.19 | 0.763 | 1.000 | 0.448 | 0.310 | 0.112 | | 127 g |
| **Cardan, catalogue seed, best (k6: wedge, link 2 lowest, 15 poses left out of the fit)** | 80.17 | 0.906 | 1.000 | 0.162 | 0.107 | 0.064 | 27.7 | 257 g |
| Cardan seed k6 re-run with the hub-footprint fix (k15, honest) | 81.87 | 0.900 | 1.000 | 0.150 | 0.100 | 0.069 | 27.7 | |
| Cardan, the 39.8 deg max-margin placement (k12) | 103.66 | 0.863 | 0.967 | 0.006 | 0.001 | 0.105 | 39.8 | 544 g |
| shorter-arc variant a1 = a2 = 75 at the seed (k9, before the hub-footprint fix) | 72.02 | 0.894 | 1.000 | 0.237 | 0.136 | 0.051 | 9.2 | 222 g |
| **same, hub footprint fixed, kit audit honest (k14, BEST)** | **72.67** | 0.894 | 1.000 | 0.226 | 0.133 | 0.047 | 9.2 | 371 g |

Sweep: `docs/concepts/sweeps/posterior-max-margin-cardan.json` (every configuration in order). Coarse stage at the seed:
seat (wedge only measured; the flat-seat half was cut for CPU time), stack order A / B, underside quantile q 1.0 /
0.97 / 0.93, then a pose-consistent fit drop (15 / 30 / 45 poses), branch sigma, arc length (90 / 75 / 68 / 60) and the
max-margin placements of the landscape. The box was 4 cores at load 20-27 (1-3.5 min per configuration), so the
sweep is 14-15 configurations, not 50-200: a coarse map, not a converged optimum.

## What limits it (measured)

- **The Cardan's links float.** At the seed, link 1 (up the infraspinatus) and link 2 (down the posterior deltoid)
  have 1-9 % / 2-21 % of their samples in band; their median skin distance is 26-30 mm in every configuration. A
  rigid 90 deg great-circle arc at ~110 mm radius sweeps ~170 mm of back and deltoid skin as J1 / J3 turn; its
  underside must clear the highest skin under every sample over every pose it takes, and the posterior skin under
  it moves a lot (scapula winging, deltoid bulge). Shortening the arcs to 75 deg cuts that sweep and wins 8 gap
  points (80.2 -> 72.0); at 60 deg the margin collapses (closure 81 %) and it loses.
- **Margin is anti-correlated with proximity.** The global max-margin placement on this bench (b = bvec(-43, -12),
  W = wdir(38, -100), margin 39.8 deg, more than the catalogue's 34.6) puts J1 and J3 where the skin is most oblique
  and the requirement highest: in-band 14 0.6 %, 544 g. The posterior seed (27.7 deg) is already past the margin
  that matters (0 flips, closure 100 %); beyond ~10 deg the margin buys nothing on the bench.
- **Oblique end hubs.** The wedge seats J1 / J3 are 20-25 mm tall (the spec's 49 deg obliquity, confirmed); J3 sits
  at 144-191 mm from GH, 0-65 % in band. J2 on the posterior acromion is good only when the poses that cover it are
  left out of the fit: with 15 dropped its wedge is 69 mm tall (137 mm level), with 30 dropped 5 mm (71 mm level).
- **Intruding body parts set the q = 1 envelope.** At q = 1 every part is pushed to 150-250 mm by 4-6 poses where the
  forearm, head or trunk crosses the posterior chain (elev 150 plane 0-15 axial 0: forearm behind the head; across-
  body plane 105-120 axial -135..-165: trunk over J3; behind-back plane -75 axial 60): reach 0.97, in-band 1 %.
- Branch sigma = -1 wraps the chain over the front: contact 82 % (dead branch).

## Model and departures from the spec (honesty notes)

- Built on `tools/concept_kit.py` (K0-K7). The interrupted partial model was replaced.
- **Every part at its real size, laid out in true mm** (two-pass calibration: the kit lays straps out at r_ref = 70,
  which makes a 12 mm strap at 130 mm 22 mm wide and coarser than 1 pt / 4 mm2).
- **Wedge seats** as specified: the lower member's underside under each O20 disc is skin-fitted; K6 counts the wedge
  height as stack (crown = F + 12.25 + wedge).
- **Kit fix (local to this model, reported for the kit owner):** the kit applies `over` before the K5 climb limit, so
  the climb lifts samples near a hub ramp back into the member they were raised over; with a part laid out at real
  radius this rejected 67-80 poses by K6. The model re-orders it (climb, then `over` + climb until stable; raising
  only). It also keeps `x / r_ref > 1` (r_ref = 0.8 x layout radius) so the K6 shared-joint exemption does not
  depend on how high a part was raised.
- **Pose-consistent fit drop** (`drop`): the n poses whose skin stands highest above the chain's typical skin are
  left out of the FIT only; they are still scored, and metal inside the body there is contact. The per-sample
  quantile (q = 0.93) drops a different 7 % per sample and turned 19-20 % of the poses into contact poses.
- The 25 deg K2 rule runs on the dense interpolated motion (kit default), 0 flips in every Cardan configuration.
- Spec improvement: "maximise the singularity margin" is the wrong objective for this bench; ~10 deg of margin with
  dense continuity is enough, and every extra degree is paid for in obliquity and link length.

## Red team (best configuration k9, a1 = a2 = 75, 220 poses)

17 poses not taken: 12 contact, 3 K6 collisions, 2 no closure (margin < 5 deg). Every one is in the everyday
workspace; all 60 clip frames are followed (0 flips). The poses that jam or pinch:

- **Across the body with internal rotation (plane 90-120, elev 30-105, axial -120..-165): 7 contact poses.** The
  trunk and chest come over the posterior arm: hub 3, link 2 and the neck are 14-32 mm inside the body (-31.8 is the
  grid's clamp). The posterior J3 / neck is the part that pinches; it is where the arm meets the chest.
- **Behind the back (plane -75 elev 60 axial 60; plane -45 elev 60 axial 45): 2 contact poses** - hub 2 and link 1
  are 3-32 mm inside: the arm swings toward the chain, as the spec feared.
- **Overhead with the elbow flexed (plane 0 elev 150 axial 0)**: hub 2 -14.6, link 1 -10.3, link 2 -8.4 mm - the
  forearm drops behind the head onto the J2 pole.
- **Collisions** (plane 45 elev 15 axial -105; plane 75 elev 30 axial -135; plane 105 elev 45 axial -165): link 1
  over link 2 near J2 when J2 folds; **no closure** at plane 45 elev 75 axial 45 and plane 75 elev 90 axial 15 (the
  75 deg arcs give up margin: 9.2 deg minimum where the Cardan had 27.7).
- **Kit audit** on the first k9 run: "hub of J2 smaller than O20 (covers 0.72 of the disc)": the wedge's radial
  sample rays shrank where its underside is low. Fixed (the disc is laid out at the wedge's lowest underside, so the
  footprint is >= 20 mm everywhere and larger at F, conservative) and the two best configurations re-run (k14, k15).
- Kit version: the kit was updated at 18:33 UTC (K4 flat-hub level, K2 along joint axes, pose-local kit straps, audit).
  This model uses its own straps and wedge hubs; k9 re-evaluated under the new kit gives the identical 72.02.

## Verdict

Screened, not worth its own GPU sweep. The Cardan (a1 = a2 = 90) is 80-82 at best and its max-margin placement 104;
the best honest number, 72.67, comes from the shorter-arc variant (75 / 75), which gives up most of the margin that
defines the morphology and still trails the champion 3R (68.93; kit template 70.19). Rigid great-circle links riding
behind the shoulder must clear the back and posterior deltoid in every pose, so they float 26-30 mm off the skin.
That is the same proximity limit as the 3R family, made worse by longer arcs and oblique end hubs. What carries over:
(1) a singularity margin above ~10 deg buys nothing once continuity is checked on the dense motion; (2) leaving
a pose-consistent set of poses out of the fit beats a per-sample quantile (80 vs 83-93 here); (3) the kit's
over-before-climb order needs fixing for parts laid out at their real radius.

## Verification (adversarial verifier, 2026-10-15)

Verdict: **refuted.** The best configuration (k14: a1 = a2 = 75, wedge seats, stack B, drop 15) scores **87.47** on the
larger bench when its rigid geometry is held fixed and the signed distance is exact, and **73.51** on its own 220 poses
once a modelling error is corrected. Both are worse than the 68.93 baseline. No hard rule is broken. The verifier's
scripts are in its scratchpad (`vfix.py`, `vgen.py`, `pairs.py`); the model file is unchanged.

| check | what I did | result |
|---|---|---|
| (1) DOF | read `build` | 3 active revolutes (J1 fixed in the scapula, J3 fixed in the humerus, J2 from the closed-form K1 closure); 0 passive coordinates; nothing left undetermined. Holds. |
| (2) real size, sampling | read `strap` and `hub`, ran the kit audit | Straps are 12 x 3, neck 14 x 6, 2 mm grid at true radius; O20 discs are covered (audit clean); no near-skin-only sampling. Holds. **Error found:** a wedge seat's per-sample skin-fitted underside was laid out in `K.plane_frame(k)`, an azimuth referenced to the thorax. The wedge belongs to the member that carries it (the base at J1, link 2 at J2 and J3), and that member turns about the hub axis relative to the thorax frame by -11..+24 deg (J1), -122..+110 deg (J2) and -171..+166 deg (J3), p1-p99 over the bench. So each "sample" was not one material point, and the wedge was fitted as if it never turned on the skin: optimistic. Fixed by laying the disc out in the carrier's frame (ref = scapula vector, p3, p2): gap 72.67 -> **73.54** (hub 2 in band 0.237 -> 0.156; wedges 36 / 36 / 36 mm). |
| (3) honest pose-taking | dense K2, closure residual, K6 per pair | Residual 0, 0 flips. K6 with **1 mm radial clearance for non-adjacent pairs** (the rule; the kit uses 0.5 for all pairs) changes nothing: every pair that comes closer than 1 mm shares a joint (link 1 / link 2 at J2: 20 poses; link 2 / neck at J3: 34 poses, between 0.5 and 1 mm outside the 12-15 mm hub zone). Applying 1 mm to those adjacent pairs too would give 89.44. That clearance is a CAD tolerance flag, not a rule break. |
| (4) bench artefact | the same fitted geometry, exact libigl distance (CB_EXACT=1) on the same 220 poses | **73.51** exact vs 73.54 on the grid: no grid artefact. 11 contact poses, 4 collisions, 2 no closure. |
| re-measure | Bench(110, 360), 470 poses, exact path; geometry fitted on Bench(60,160) **frozen** (a rigid part does not refit to new poses; about 250 poses were never seen by the fit) | **gap 87.47**: reach 0.817, follow 1.000, in-band 14 0.223, in-band 10 0.126, contact 0.114 (52 poses), 12 collisions, 2 no closure, min margin 7.8 deg, 0 flips. |

Where the large bench breaks it: 52 workspace poses not seen by the fit put metal inside the body.
- Across the body with internal rotation (plane 60-150, elev 15-135, axial -75..-165), about 38 poses: the trunk
  comes over hub 3, link 2 and the neck, up to 49 mm inside.
- Behind the back (plane -90..-60, elev 45-60, axial 45-75), 6 poses: hub 2 and link 1 go 4-40 mm inside.
- Overhead (plane -15..15, elev 90-165), 6 poses: the forearm or head comes onto hub 2 and link 1, 0.4-38 mm inside.

Every clip frame is still followed. Caveat: a refit on the 470 poses was not run. The exact K3 march needs about 1-2
CPU hours at load 12-15, and there is no grid cache for (110, 360). A refit would trade some of this contact for even
higher links, and in-band is already 22 %. The proximity limiter the agent measured (links 26-30 mm off the skin,
link 1 2 %, link 2 5 % in band) holds under every check.
