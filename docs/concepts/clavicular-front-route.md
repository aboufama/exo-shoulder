# clavicular-front-route: Front route, J1 on the bony acromio-clavicular front

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the front seat as a bone anchor
   only where the skin over it is quiet in the scapula frame in EVERY pose, including the ones where the arm, forearm
   or hand sweep across the front of the shoulder (across-the-body reach, comb hair): a scapula-fixed hub there must
   clear the arm, not just the skin under it. Pick the link arcs from the measured angle band between the J1 seat and
   the arm point over the bench poses (not round 60/60), try asymmetric arcs (short link 1 keeps J2 on the bony front,
   long link 2 reaches the arm), and check both closure branches - the fold side decides whether J2 overhead sits over
   the head/neck or over the deltoid. Count the bridge from the handler as metal (it is between the handler and the cuff).
2. **Rawest material.** The posed skin of every bench pose (the bench's signed-distance grids, `B.dist`), the fit-clip
   frames in time order, the per-pose K3 requirement of every member sample (which pose sets each member's height),
   `pipeline/conformal/analysis/skin_motion_map_14.json` and the proximity atlas field (docs/research/proximity_atlas.md).
3. **Methods and tools.** The shared kit (tools/concept_kit.py: K1 closure, K3 march, K4 flat O20 hubs with the real
   stack, K5 straps with climb limit, K7 neck, K2 dense continuity on every joint axis, K6 collisions, audit), a
   per-member/per-pose requirement diagnostic, the cloud CPU farm for every sweep (random coarse, then CMA-ES from the
   top until the convergence gate passes).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, Bench(60,160), fast grid),
   the adversarial verifier on Bench(110,360) exact, and a red-team pose list: across-the-body at elevation 120-150 /
   plane 120-150 (the forearm over the front seat), comb hair, overhead flexion 150-165 (the fold), behind the back
   (plane <= -20), and the link-1 / bridge pinch at J1.

## Model

`docs/concepts/models/clavicular-front-route.py` (kit, all honesty checks on).

Spherical 3R: J1 (O20 hub) scapula-fixed at sdir(j1lat, j1lon), J3 (O20 hub) humerus-fixed at armpt(s3, th3, 76)
(body_pose frame), J2 by the two-circle closure (arcs a12, a23, branch sigma, fold margin), 12 x 3 links, a
scapula-fixed 14 x 3 bridge from the handler side sdir(45, 90) via sdir(65, 20) to the J1 seat (two straps lapped
at the waypoint), the K7 14 x 6 neck to BOTTOM. Every honesty check on (K3 march, K2 dense continuity on every
joint axis, K6 collisions, audit clean, closure residual 0).

Departures from the spec, and why: kit flat O20 hubs instead of ray-fit caps; the K7 straight neck instead of the
dog-leg down the strip; the bridge counted as metal (it sits between the handler and the cuff); the J1 seat range
extended to the front-top (lat 55-75) once the raw skin showed the spec's seat is not quiet (below).

## Measured on the raw skin: the spec's front seat is not quiet

The K3 skin requirement of an O20 disc fixed in the scapula frame, all 220 bench poses
(scratch `seat_req.py`; same march as the bench):

| J1 seat | fit clips p10 / p50 / p90 / max (mm) | workspace p50 / p90 / max | atlas S ceiling | atlas skin motion |
|---|---|---|---|---|
| spec AC-front sdir(40,-100) | 44 / 49 / 78 / 79 | 48 / 77 / unclearable | 0.00 | 95 mm |
| clavicle-lateral sdir(30,-80) | 44 / 51 / 84 / 87 | 51 / 79 / unclearable | 0.00 | 111 mm |
| supraclavicular sdir(50,-140) | 59 / 62 / 71 / unclearable | 61 / 87 / unclearable | 0.10-0.23 | 36-47 mm |
| **front-top sdir(65,-120)** | **49 / 49 / 51 / 52** | 49 / 51 / 87 | 0.02-0.08 | 32-43 mm |
| champion top bvec(2.4, 80.7) | 53 / 53 / 54 / 54 | 53 / 54 / 54 | 1.00 | 1.7 mm |

The bony AC front is quiet only in the rig's bones: in the scapula frame the skin over it rises 34 mm in the fit
clips alone (anterior deltoid / pectoral bulge and the humeral head moving forward under arm flexion), and in
across-the-body workspace poses (plane 120-150, elevation 120-150) the forearm lies over the seat, so no radius up to
220 mm clears it ("unclearable": the hub would sit inside the arm). The spec's "8-11 mm spread" was a first-sheet,
fit-clip-only number; the arm passing over is what kills the seat. Only the front-TOP edge (lat ~65) is quiet in the
clips.
