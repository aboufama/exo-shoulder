# seed-spm-3rrr - low-profile spherical parallel 3-RRR around the shoulder

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Not accept "every link at skin +
   clearance": in an SPM the nine links of three legs cross each other over the same patch of skin, so the real design
   problem is *layering* (which leg rides on which radial shell, Agile-Eye style nested spheres) and *where the legs
   live on the sphere* (keep each leg on its own patch so it never has to stack). They would also place the
   type-2 singularity surface outside the workspace by choosing the platform-axis triangle, not just check cond(J);
   and they would make the platform the *cuff itself* (axes fixed in the humerus) so no extra platform ring adds height.
2. **Rawest material.** The posed render skin of every bench pose (B.skin, ray-cast exactly from GH into a per-pose
   cube map of the first skin exit and the far side of the arm/trunk gap), the scapula and humerus rotations of every
   fit-clip frame and workspace pose (B.frames), the clip time order (B.clip_order) for continuity - not the digested
   skin-motion summaries. The skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) only matters for a
   skin-riding part; here every part is rigid and rides on hubs, so the skin is used as an obstacle field per pose.
3. **Methods and tools.** Closed-form leg IK (intersection of two cones on the unit sphere, branch fixed per leg),
   the Gosselin SPM Jacobian J = B^-1 A with cond(J) <= 50 for both singularity types, slerp sub-steps between
   consecutive clip frames for continuity, rigid parts fitted to the q-quantile of the skin under each sample over the
   kinematically valid poses (the baseline's percentile idea), KD-tree part-part clearance >= 1 mm, the bench's signed
   distance (libigl / fast grid) for every metal sample at ~1 point / 4 mm2.
4. **What other than me shows the number is right.** tools/concept_bench.py (same poses, same signed distance, same
   metrics as the baseline), the adversarial verifier of the swarm, and a red-team pose list in this file (the poses
   where the best configuration jams, collides or pinches, with the measured part and distance).

## What was built (docs/concepts/models/seed-spm-3rrr.py)

Agile-Eye-type 3-RRR, every one of the 9 joint axes through the GH centre. Base axes u_i fixed in the scapula frame
(3 spots at b_rho deg around a centre direction), platform axes v_i fixed in the humerus frame (cone p_cone about the
humerus axis, azimuths p_az +- p_spread) - the platform *is* the arm side of the cuff, so no extra ring. Closed-form
leg IK (two cones, branch fixed per leg, so joint values are continuous wherever the leg stays closed); Gosselin
Jacobian J = B^-1 A, a pose is not taken when cond(J) > 50; along each fit clip the path between consecutive bench
frames is checked on slerp sub-steps (closure + conditioning) - a failed path is a frame not followed. Grubler
(spherical): 3(8-1-9)+9 = 3 active, the 6 passive joints are set by the loops (nothing sags unpowered, R17).

Parts at real size: 9 O20 hubs (12.25 mm from the lower member's skin face to the crown; the upper member's skin face
3.15 above the lower one, docs/HARDWARE.md v5), 6 leg links + 2 base-frame straps (join the 3 base hubs to the scapula
handler) + 2 platform straps (join the 3 platform hubs) + the arm-end drop strap toward the cuff, all 8 x 3 mm straps
on great-circle arcs. Every part is rigid in its own frame; its radius at each (s, t) sample is the q-quantile over the
taken poses of the first skin exit under it (exact ray-triangle cube maps of every posed skin, ~0.8 deg cells) +
clearance; links ramp at <= 45 deg down from their hubs. Collisions: non-adjacent parts >= 1 mm (KD-tree on 2 mm
mid-surface samples, hubs as cylinders); adjacent members of one joint may overlap outside the hub with the joint's
running gap (0.1 mm modelled, v5 has 0.15) but never interpenetrate. Metal for in-band: strap undersides + hub lower
faces at 2 mm spacing (1 point / 4 mm2); every other surface (tops, hub walls, crowns) is checked for contact.

**Changes to the spec / the earlier partial model (say so to the verifier):**
- *Hub-axis accessibility* (new, makes the model stricter): a pose is taken only if each of the 9 axes points at skin
  within 140 mm of GH with >= 25 mm free above it. Without it the fit happily put middle hubs at 300-400 mm from GH
  (rays into the trunk never exit) and the bench scored those absurd configurations at gap 216-222 (sweep entries
  0-43 were measured without it; entries 44-50 re-measure the best ones with it).
- *Adjacent-member clearance* relaxed from 1 mm to the joint's running gap (the 1 mm rule is for non-adjacent parts).
- *Per-leg nested shells* (lay_leg, Agile-Eye style: leg i one shell higher) added as the variant that should remove
  the leg-leg collisions.
- The spec's "platform ring level" parameter is gone: the platform hubs sit on the deltoid at their own fitted level.

## Sweep (Bench(60,160), fast grid, 51 bench entries, ~2500 configurations screened before the bench)

| stage | what | configs |
|---|---|---|
| kinematic / accessibility screen | random + hill-climb on the share of poses closed, conditioned, continuous with every axis on skin | 500 + 600 (+ 960 hill steps) |
| quick screen | coarse fitted-part model (cube-map radial gap), hill-climb and a shape grid (q, lay_P, lay_D, w_lower) | ~450 |
| bench: screen | best quick configurations | 30 |
| bench: refine | neighbours of the running best | 10 |
| bench: nested shells | lay_leg 4 / 8 on the best | 4 (2 duplicates) |
| bench: accessibility enforced | the 5 best + 2 best high-reach ones re-measured | 7 |

Best honest configuration (sweep entry 46, accessibility enforced): **gap 193.44** - reach 0.181, follow 0.300,
inband14 0.355, inband10 0.251, contact 0.021 (baseline spherical 3R: 68.93). Best without the accessibility rule:
216.55 (entry 40, absurd hub radii). Highest kinematic reach reached: 0.92 of all poses closed and on skin
(stage A), but those configurations lose 116-190 of 220 poses to leg-leg / leg-platform collisions and put
inband14 at 0.00-0.04.

## Red team of the best (entry 46)

- rest (workspace, elevation 0): middle hub HW2 8.3 mm *inside* the body (q 0.95 fit leaves the rest pose under it).
- overhead (Raise overhead, elevation 150): proximal link P0 collides with the platform strap.
- overhead (workspace, elevation 165): leg 2 cannot close (the two cones separate).
- across the body (Wash opposite shoulder, plane 145): leg 1 cannot close.
- behind the back (Reach back pocket, plane -80): taken, closest metal 1.7 mm (platform strap PF1, under the 2 mm floor).
- over all 220 poses: 57 taken clean, 97 lost to leg closure (leg 1: 56), 7 singular, 3 path breaks, ~25 collisions
  (D0-PF, P1-BF, P0-PF), 36 with contact; the deepest pinches are at the grid clamp (>= 31.8 mm inside) under P0 in
  Comb hair (elevation 57-77) and under P2 / D1 near rest.
- part radii from GH: base hubs 55-122 mm, middle hubs 62-201 mm, platform hubs 104-152 mm, links up to 204 mm, over
  skin that is 45-70 mm from GH: the parts that move over the whole shoulder ride 50-130 mm off it.

## Limiter (measured) and verdict

Two-sided and structural. (1) Workspace: an SPM whose 9 axes all stay on reachable shoulder skin closes on at most
~0.9 of the poses, and the configurations that do (stage A) put the middle axes w_i through a sweep that crosses the
other legs and the platform - collisions then take 116-190 of 220 poses. (2) Proximity: the three middle hubs and six
links each sweep a large patch of the shoulder sphere, so each rigid part must clear the highest skin it ever passes
over - the 3R limiter, paid nine times instead of three (inband14 0.36 at best vs 0.44 for the 3R). Nested per-leg
shells (lay_leg 4 / 8 mm) cut collisions 16 -> 14 -> 10 poses but cost in-band; they do not change either limiter. Configurations
that keep the legs short and local (high in-band) lose more than half the workspace to leg closure (leg 1 cannot close
in 56 poses).

**Verdict: dead for this goal - not worth a GPU sweep.** 2.8x the baseline's gap on the same bench; adding passive
joints (6) bought no proximity, only more rigid area to keep off moving skin. What would predict beyond this
morphology: for any closed loop whose intermediate joints move over the shoulder, count the skin area each rigid link
sweeps; the in-band ceiling falls with that area, and parallel legs multiply it.

Sketch: docs/concepts/img/seed-spm-3rrr.png (rest and overhead, skin radius from GH, parts by group).
Reproduce: `python3 docs/concepts/models/seed-spm-3rrr.py redteam` (best of the sweep), `... sweep3 <budget s>`,
`... sweep2 <nA> <budget s>`, `... sketch`.
