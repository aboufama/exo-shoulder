# far-end-posterior-3r - plain 3R on the fold-free posterior J1 line, hubs at either end of their axis lines

Status: **killed after the coarse sweep** (measured reason below). Model: `docs/concepts/models/far-end-posterior-3r.py`
(the raglan-routed-3r builder with the posterior layout and the end choices). Sweep: `docs/concepts/sweeps/far-end-posterior-3r.json`.

## Depth answers (before modelling)

1. **What a top pattern maker / orthotist would do here.** Pin each seam end (hub) on the most stable landmark that the
   construction allows, not on the first one drawn. For a revolute axis through GH the construction allows TWO
   landmarks: the bearing can sit at either end of the axis line (the motion only sees the line). An orthotist would
   look for the end that lands on skin that rides with the part (scapula-fixed skin for J1, arm skin for J3) and
   relieve the bony prominences; the far-end scan (2026-10-16 01:00) found a J1 line pointing straight BACK and
   horizontal from GH (bvec(-24, 4)) whose hub stays in one 12 mm band in 100 % of poses, overhead included, and that
   is fold-free over 100 % of workspace and clip poses with arcs 65 / 65 and J3 on the posterior arm (wdir(80, -90)).
2. **Rawest material.** The posed skin of every bench pose (signed-distance grid, Bench(60, 160)); the K3 requirement
   along every link ray of the moving link frame in every closing pose (the raglan map, `map` mode of
   docs/concepts/models/raglan-routed-3r.py); the far-end scan's fold and hub-1 band tables.
3. **Instrument.** The concept kit (K0-K7: closure, flat O20 hubs with the 12.25 stack, 12 x 3 straps with skin-fitted
   undersides and the 60 deg climb limit, K7 neck, K2 dense continuity, K6 collisions, honesty audit) + the fold-sph3r
   crown / wall skin check; the farm (tools/cloud_run.py sweep, 256 configurations).
4. **Outside judge.** tools/concept_bench.py through the kit (the 68.93 baseline's metrics), the kit's honesty audit
   (it flags the parked links), and the parent's independent plain-3R sweep of the same posterior layouts (1064
   configurations of docs/concepts/models/_template.py: best 73.01, at a vertical J1 line; the horizontal posterior
   lines 92.66-98.09) - same verdict from other code.

## Mechanism (every joint a real component)

| joint | component | envelope |
|---|---|---|
| J1, J2, J3 (active R) | MR117-2RS bearing pair in an O20 hub (docs/HARDWARE.md v5 joint) | O20 x 12.25 mm stack (F -> crown) |
| links 1, 2 | 12 x 3 mm Ti strap, one planform turn allowed (constant section, tangent-arc corner) | skin-fitted underside, <= 60 deg ramps |
| neck | 14 x 6 mm strap from the arm-end hub to BOTTOM's bar (K7) | |

0 passive DOF, 0 passive translations. e1, e2, e3 = +1 / -1 choose the hub END on each axis line (kinematics unchanged:
same closure, same fold band, same joint values; a far-end hub changes the link spans to 180 - a).

## Coarse sweep (farm, Bench(60, 160) fast grid, kit checks + crown check)

256 configurations: 4 fold-free posterior layouts from the far-end scan (bvec(-24, 4) 65/65 wdir(80, -90);
bvec(-18, 20) 65/65 wdir(100, -90); bvec(-30, 8) 65/75 wdir(75, -90); bvec(-24, 4) 65/85 wdir(60, -78)) x branch
+-1 x all 8 hub-end choices x route d 0 / 25 deg x q 0.90 / 0.97.

| | gap | reach | in-band 14 | contact | note |
|---|---|---|---|---|---|
| best overall | 98.03 | 0.925 | 0.030 | 0.077 | NOT honest: links parked at ~400 mm (sparse sampling) |
| best honest | 118.55 | 0.644 | 0.279 | 0.275 | q 0.90: hub 2 and hub 3 0 % in band |
| best per end choice (e1, e2, e3) | (1,1,1) 98.03; (1,1,-1) 107.17; (1,-1,1) 109.15; (1,-1,-1) 112.56; (-1,1,1) 135.30; (-1,-1,1) 125.33; (-1,-1,-1) 140.29; (-1,1,-1) 153.87 | | | | every far end is worse than the near end |
| route d 25 vs 0 | 98.03 vs 99.12 | | | | routing cannot rescue a link that passes through the body |
| honest configurations | 7 of 256 | | | | the other 249 have a link ray that never clears the body in some pose |

Control (same code): the plain 3R at rail-elbow k2221's axes, 51.33.

## Why it is dead (measured)

* **Links through the body.** The raglan map of the default layout (link frame, every closing pose): 10-20 % of the
  closing poses send link-1 and link-2 rays through the torso / neck (no 15 mm free window within 220 mm of GH, "inf"),
  at almost every cell of both links, at any route offset -50..+50 deg. A rigid link must clear those poses, so its
  q = 1 underside parks at 400 mm; q 0.90 drops those poses as contact (reach 0.64). The fold-free arcs (65 / 65,
  J1-J3 angle 10-120 deg) make J2 swing far over the neck and chest in across-the-body and overhead poses: the fold is
  avoided by sending the middle of the chain where the body is.
* **Far ends land in the body.** The far end of the posterior J1 line is the front of the shoulder (pectoral), of the
  posterior J3 line the anterior arm / chest wall, of J2 the opposite side of GH: hub 1 drops from 50-71 % to 0 % in
  band, link spans grow to 115 deg, and every end combination scores worse than the near ends. At k2221's axes a far
  J2 hub (front of the chest) scores 184.6 (q 1.0) and 237.9 (q 0.95) against 51.33.
* So the far-end lever is real kinematically (a free choice) but the body occupies the far side of every GH line we
  can use: a far-end hub is only useful where the axis line exits the body twice near the surface, which GH lines do
  not do at the shoulder (they exit once, on the near side; the far side is torso, axilla or neck).

## New knowledge

1. A fold-free spherical 3R layout on this body is a links-through-the-body layout: the fold band is avoided by large
   J2 excursions that cross the neck / chest in 10-20 % of the poses (raglan map, inf share per link cell).
2. Hub-end choice on GH lines: the near end is always better on the 8 x 4 x 2 combinations measured; the far end of
   every GH line used by the leaders lies inside the torso, axilla or neck.
3. The leader's direction stays: fold must be beaten by moving J2 METAL off the J2 ray (osn's "next lever"), not by
   choosing fold-free GH-ray layouts.

## Confirmed in the leader's family (2026-10-16 ~02:55, raglan-knee-3r coarse sweep)

The posterior J1 line was also tried in the zero-passive-translation leader family (the pin knee: J1 / J2 hubs on GH
rays, offset skin-normal J3, flat two-pin knee), 64 layouts on the farm (`docs/concepts/sweeps/raglan-knee-3r.json`,
stage `coarse-posterior-J1`: J1 bvec(-24, 4) / (-18, 20) / (-18, 24) / (-30, 8), J3 wdir(80 / 100, -90), arcs 65 / 65 and
65 / 75, b3 0 / 0.35, both branches; J2 seat = the closure's home direction, tools/osn_fold_seeds.py `layout_params`).
Best 122.45 (median 255.8) against 26.34 for the pin knee's own seats: the fold drops to 6-20 poses of 220 (from 47),
but 46-69 poses go to skin (not split per part; in the plain 3R the raglan map puts these link rays over the neck and chest), in-band 14 0.17-0.25, contact 0.23-0.29, and
23 of 64 layouts close in no pose at all. Same verdict, other code: the fold-free posterior line moves the poses from
the fold column to the skin column.
