# Crown ring 3R (crown-ring-3r)

J1 is an open thin-section ring bearing lying on the shoulder crown (axis through GH near c* = S-local
[-0.38, 0.91, 0.16] = bvec(az 22.7, el 65.5)); J2 and J3 are spherical-3R joints (O20 hubs or KAA15-type donuts) by
two-cone closure. 3 active DOF, 0 passive. Model: docs/concepts/models/crown-ring-3r.py (shared kit).

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Not trust the premise that J1 is the
   problem. Every verified 3R measurement says the limiter is J2 and the links (hub 2 at 105-161 mm, 0-2 % in band;
   links 0.2-5 %), and annular-ring-3r already measured that an open bore over the crown loses to an O20 hub at every
   size (trapezius rises into the bore medially). So: (a) carry an O20-hub J1 as the in-model control in every
   configuration family so the ring's own effect is isolated; (b) tilt the ring axis laterally off c* (away from the
   trapezius/neck rise) and measure where the flat land actually seats, per azimuth; (c) use the one real thing a big
   ring gives - the link-1 root sits on the ring rim, 37-57 mm off the J1 axis, so J2 can be placed by the rim
   azimuth and alpha12 with a short strap - and check whether that buys J2 a lower seat; (d) red-team the land
   tilt the spec flags (a flat ring on a 55 mm dome drops 6-7 mm across its section).
2. **Rawest material.** The posed skin itself (concept_bench distance grids built from the posed body, every bench
   pose), the motion clips through the bench (clip frames, interpolated densely for K2), the skin-motion map
   pipeline/conformal/analysis/skin_motion_map_14.json for the S-fixed skin under the ring, and the proximity atlas
   data (docs/research/proximity_atlas.md) for the per-direction ceilings - not the catalogue's digested numbers
   (the spec's "skin along superior stays at 47.7-48.6 mm" is re-measured here per land sample along the ring axis).
3. **Methods and tools.** tools/concept_kit.py (K1 closure, K3 march, K4 flat parts fitted along their own normal -
   the ring land is exactly a K4 flat annulus, K2 dense continuity, K6 collisions, audit); a coarse grid then CMA-ES
   (local, then the farm via tools/cloud_run.py sweep) until the convergence gate passes; per-member in-band and
   per-pose loss tables to name the limiter.
4. **What, other than me, shows the number is right.** The bench (Bench(60,160), fast grid, march, K2, K6, audit
   honest), the adversarial verifier's exact re-run on Bench(110,360), the in-model O20-hub control (must reproduce
   the template's numbers when the ring is turned off), and a red-team pose list (rest, overhead elev >= 140,
   across-the-body plane >= 120, behind-the-back plane <= -60) with the pose that jams, the point that pinches and the
   member that floats.

## Model (docs/concepts/models/crown-ring-3r.py, shared kit)

- J1: the spec's ring as a flat annulus normal to a1, land pitch +-8 mm (bearing + 1.5 mm Ti housings), stack 9,
  kind `flat` (K4: every land sample marched along a1 from its true offset; level F = max over samples and fit
  poses). The outer and bore walls stand on the land's rim samples, and the K3 march already demands dist >= 0 on the
  15 mm of axis-parallel line above every land sample, so no wall is inside the skin in a fitted pose. p1 = 0 swaps the
  ring for an O20 hub: the in-model control, which reproduces the kit template's chain.
- J2, J3: O20 hubs (annular-ring-3r measured ring/donut bores at J2 and J3 losing to O20 at every bore, so they are
  not re-swept). Links 14 (link 1) / 12 (link 2) x 3 mm Ti, K5 climb; K7 neck to BOTTOM's bar.
- **Spec correction (link-1 root).** A lug 4.5 mm outside the land edge collides with the land in every pose (K6
  exempts joint partners only within 12 mm of the axis, an O20 rule): measured 202/202 poses. Link 1 is therefore
  bolted on top of the rotor housing: it starts over the pitch circle and passes over the outer land with
  `over=[("ring1", 0.6)]` (0.6 mm above the rotor top; the real bolted joint has 0 gap, so conservative by 0.6 mm).
  Its root direction depends on the ring level, so `bench_eval` runs two passes (h1 = the first pass's fitted F).
- Swarm parking rule in the report: `park` = each joint part's level and the minimum skin distance on the 25 mm of
  axis line above it in every taken pose; `park_ok` needs level <= 140 mm and that line free. CMA fitness adds +15
  gap for a park failure and +25 for a dishonest audit (sparse links floating > 140 mm).
- Checks: K3 march, K2 dense continuity (values + axes), K6 collisions, audit; closure margin 10 deg.

## Raw measurement: how high a flat ring sits on the crown (posed skin, all 220 bench poses)

Level F (mm along the axis from GH) of a flat plate normal to an S-fixed axis through GH, by outer radius, = the K4
fit over every bench pose (scratch: disc_scan.py; the azimuth of the sample that sets F in brackets: 0 posterior,
90 lateral, -90 medial, 180 anterior):

| axis (bvec az, el) | r 10 (O20) | r 20 | r 25 | r 30 | KA020 r 36.6 | KA025 r 42.9 | KA030 r 49.3 |
|---|---|---|---|---|---|---|---|
| c* (22.8, 65.6), the spec | 54 (-5) | 57 (-27) | 59 (-31) | 67 (-49) | 83 (-70) | 92 (-82) | 97 (-78) |
| (10, 75) | 54 | 58 | 87 (-68) | 99 | 106 | 113 (-85) | 119 |
| champion J1 (2.4, 80.7) | 54 | 57 | 101 (-68) | 109 | 116 | 126 (-86) | 133 |
| lateral (50, 62) | 54 (77) | 57 | 62 (117) | 82 (162) | 82 | 82 | 84 (128) |
| lateral-low (30, 50) | 58 (84) | 61 | 63 | 67 (106) | 71 | 74 (119) | 75 (121) |

The crown is flat enough for a plate only out to ~20-25 mm radius. Beyond that the medial land runs onto the
trapezius / neck rise (azimuth -70..-88) and F jumps by 30-70 mm. Tilting the axis laterally swaps that limit for the
anterior-lateral side (clavicle / anterior deltoid, azimuth 106-162): 74-84 mm for KA025. The spec's premise ("the
skin along superior stays at 47.7-48.6 mm") holds on the one ray, but a 76-89 mm OD ring is not a ray: its land
reaches skin 30-45 deg off the axis.
