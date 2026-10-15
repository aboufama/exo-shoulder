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

## Two model bugs found and fixed on the way (v1 -> v2)

1. **Bridge self-collision.** The bridge was two straps meeting at the waypoint with no shared joint, so K6 flagged
   their common end in every pose whenever both sat at one level (collide 1.0, gap 275). Fix: a lap joint, bridge_a
   passes over bridge_b (`over`, >= 1 mm).
2. **`over` near a shared joint is decided at the pre-raise radius (kit subtlety, affects any model).** `_over`
   evaluates the shared-joint exemption (HUB_R + 2 mm of arc) at the upper member's raw skin radius; at ~50 mm a link-1
   sample 12 deg from J1 is exempt, the K5 climb limit then lifts it to ~78 mm where it is not, and K6 rejects the pose
   (link 1 vs bridge in 85 % of poses at the front-top seat, measured with a pair-by-pair K6 split). Workaround in the
   model: link 1's J1 end ramps to the bridge top + 1 mm (STACK + 1) over 20 mm. Both bugs only removed poses (v1
   numbers are pessimistic, never optimistic); the v1 sweep entries stay in the sweep file tagged `model: v1`.

## Sweep (Bench(60,160), fast grid, every check on; farm)

- v1 (with the two bugs): 240 random configurations over the spec's ranges (+ 24 CMA tries): best 81.07, never
  honest (links at 150-400 mm, sparse).
- v2: 128 random configurations, half at the front-top seat (lat 55-75), half at the spec's seats (lat 30-55):
  **best honest gap 68.26 (score 75.18)**, k368: J1 sdir(66.3, -105.5), a12 83.4, a23 73.8, J3 armpt(10.2, -34.1, 76),
  sigma -1, margin 7.3, q 0.98: reach 0.875, follow 0.95, in-band 14 0.309, in-band 10 0.241, contact 0.066, Ti 201 g.
  Reproduced locally to the digit. A non-honest 67.19 (k303, links sparse at 100+ mm) is not counted.
- Where the optimum went: every top-5 config sits on the FRONT-TOP edge (lat 55-74) or needs long arcs (a12 83-94);
  the spec's AC-front seat (lat ~40) is >= 9 gap points worse at its best. The front route converges toward the
  champion's top seat - the front itself buys nothing.
- Convergence gate (v2 tries in order): gain over the 2nd half 0.00, over the last third 0.00, top-5 spread 3.81
  score points (all configs; honest-only top-5: 75.18 / 71.78 / 71.63 / 71.56 / 71.38, spread 3.80): NOT converged (spread > 3). Status screened, not dead.

## Red team of the best honest config (k368)

| pose class | poses | close | taken | what is lost |
|---|---|---|---|---|
| rest (elev < 25) | 58 | 58 | 58 | - |
| overhead (elev >= 140) | 17 | 17 | 6 | the fold drives link 1 into the head/neck: -21 mm in raise-overhead (plane 30 elev 150); 3 K6 collisions at plane 0-45 elev 135-150 |
| across the body (plane >= 110, elev >= 60) | 18 | 17 | 14 | the forearm lies over the J1 seat: hub 1 -5.2 mm (plane 135 elev 120), bridge -6.5 mm (plane 135 elev 135) |
| behind the back (plane <= -20) | 30 | 30 | 30 | - |

- The optimistic number: in-band 14 = 0.31 is the base and the neck, not the mechanism. Per member: bridge 100 / 52 %,
  neck 59 %, hub 3 20 %, hub 1 7 %, **hub 2 0 % (151 mm), link 1 1.7 %, link 2 0.7 %** (links 113-155 mm over the
  skin). The 3R proper floats exactly like the champion's (atlas: link 2 crosses skin that moves ~40 mm under it).
- q 0.98 buys the result with 6.6 % contact poses (counted as not taken).
- Other branch (sigma +1) at the front-top seat: J2 folds into the chest, hub 2 / links unclearable (400 mm), gap 240.

## Verdict

Screened, gap 68.26 honest (score 75.18) on Bench(60,160): level with the champion baseline (68.93) and the kit
template at q 0.95 (69.29), behind the verified leaders (rail-elbow, seed-offset-3r-slides). The front route as
specified (J1 on the AC front) is measured worse than the top seat: the scapula-frame skin under it rises 34 mm in the
fit clips and the forearm covers it across the body. Next lever, if anyone continues: a CMA polish from k368 to pass
the gate - but the members that matter (hub 2, links) are at 0-2 % in band in every config, so the ceiling of this
family is the 3R proximity limit, not a parameter.
