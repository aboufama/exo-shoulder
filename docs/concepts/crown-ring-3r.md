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

## Results (Bench(60,160), fast grid, K3 march, K2 dense, K6, audit; sweep file docs/concepts/sweeps/crown-ring-3r.json)

| what | k | gap | score | reach | follow | in-band 14 | in-band 10 | contact | ring / hub-1 in band | J1 level | hub 2 level |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spec seed: KA025 at c*, champion closure | (local) | 88.17 | 67.9 | 0.8875 | 0.9167 | 0.064 | 0.026 | 0 | 0.009 | 91 | 160 |
| same axes, O20 hub at J1 (control) | (local) | 67.62 | 75.4 | 0.90 | 0.9167 | 0.257 | 0.179 | 0 | 1.00 | 54 | 160 |
| best ring, coarse grid (KA020, a1 (10, 75)) | 28 | 83.40 | 69.7 | 0.9125 | 0.95 | 0.066 | 0.027 | 0 | 0.008 | 107 | 161 |
| best ring with every hub <= 140 mm (CMA, p1 37.5) | 154 | 82.37 | 70.0 | 0.90 | 0.9167 | 0.115 | 0.046 | 0.005 | 0.009 | 113 | 135 |
| smallest real ring (KAA10, pitch 15.1, lug root) at the best control axes | 175 | 81.91 | 70.2 | 0.8187 | 1.0 | 0.193 | 0.071 | 0.031 | 0.110 | 64.6 | 113 |
| **O20-hub control, CMA (J1 bvec(19.5, 88.3), a12 80.0, a23 60.6, J3 wdir(94.5, 12.7), q 0.985)** | 163 | **58.03** | **78.9** | 0.8438 | 0.9833 | 0.391 | 0.226 | 0.015 | 1.00 | 52 | 113 |

The ring loses to an O20 hub on the same axes by 20-24 gap points at every size and every seat tried: its land is a
large flat area (877 samples for KA025 against ~80 for a hub) that sits 25-32 mm off the domed crown, so it drags
in-band 14 down to 0.06-0.19 on its own. Even the smallest real ring (KAA10, 25.4 mm bore, outer land 23 mm) sits at
64.6 mm vs 52 mm for the hub on the same axis and is 11 % in band; link 1 then starts 12 mm higher too (5 % in band vs
41 % from the hub).

## Red team (scratch redteam.py: every bench pose classified, the reason it is lost, the pinch, per-member distances)

Best ring, k175 (KAA10 ring at the best control axes, q 0.985):
- **The point that pinches: the ring itself, across the body.** At plane 135-150, elev 105-135, axial -45..-60 the
  ring's land is 0.2-6.7 mm INSIDE the skin (4 workspace poses; worst -6.67 mm at plane 150 / elev 120 / axial -60).
  The S-fixed ring is not on S-fixed skin there: the trapezius / clavicular skin moves relative to the scapula frame
  when the scapula protracts, and q 0.985 hands those poses to contact. The same rise into the J1 bore was measured by
  annular-ring-3r (wall -0.4 mm at plane 150 / elev 120 / axial -60): two independent models, the same pose.
- **The pose that jams: J2's closure fold.** Raise overhead (plane 0..30, elev 135, axial -45) and behind the back
  (plane -60..-90, elev 60, axial 120-135): 6 overhead + 2 behind-back + 2 across poses lost to the closure margin; 2
  overhead lost to K6 (link 2 on link 1 / neck at elev >= 150).
- **The member that floats:** hub 2 at 113 mm (median skin distance >= 31.8 mm, 2.7 % in band) and link 2 (4 %), as in
  every spherical 3R; the ring is 12 % in band, link 1 from the ring 5.5 % (41 % when it leaves an O20 hub).
- **The optimistic numbers, said plainly:** the bench distance saturates at ~31.8 mm (medians at that value mean
  "farther"); the ring's K6 attachment is modelled on top of the rotor with a 0.6 mm gap or on a 7 mm lug with no
  lug samples (the lug is ~7 x 14 mm of unsampled metal at the rotor level); the land is the spec's +-8 mm for every
  ring size (a KAA10's real land is ~+-6.5: slightly pessimistic for the smallest ring); the ring walls are covered
  for contact only through the K3 march window (dist >= 0), not sampled for in-band.

O20-hub control, k163 (the best number of this sweep): rest 52/52 taken; overhead 7/17 (6 closure, 2 K6, 1 link-1
contact at plane 30 / elev 150, 1 neck contact at plane 75 / elev 165); behind the back 17/19; across 28/30. Pinch:
link 1 -1.0 mm at plane -15 / elev 105 / axial 45 (a contact pose, q 0.985). Hub 2 113 mm (2.7 % in band), link 2 4 %.

## CMA-ES and the convergence gate (236 configurations: 144 coarse on the farm, 3 CMA generations of 28 on the farm, 8 local checks)

Two CMA-ES instances per farm batch: the ring (az1, el1, a12, a23, wd, wa, p1 12-42, q) and the O20-hub control
(same without p1); fitness = gap + 15 for a parking failure + 25 for a dishonest audit. The farm queue was 19 jobs
deep (4 slots shared by the swarm), so a generation took 5-15 min; one generation was lost to the client's 30-min
background limit. Gate (score points; "park" = every joint part <= 140 mm and 25 mm free above):

| family | n | best | gain over 2nd half | over last third | top-5 spread | gate |
|---|---|---|---|---|---|---|
| ring, park rule on | 163 | 82.37 (k154, score 70.05) | 70.05 (every coarse ring has hub 2 at 161 mm: no valid config in the first half) | 70.05 | 1.16 | NOT converged |
| ring, park rule off | 163 | 78.34 (k218, score 71.51) | 1.84 | 1.84 | 1.47 | NOT converged |
| O20-hub control, park on | 73 | **56.04 (k235, score 79.62)** | 79.62 | 0.72 | 0.83 | NOT converged |

## Verdict

**Screened, not dead (the gate is not met), and not worth a GPU sweep as a ring.** Measured on the posed skin: a flat
annulus normal to a GH ray fits the crown only out to ~20-25 mm radius; the spec's KA020-KA030 rings (outer land
36.6-49.3 mm) sit 74-133 mm from GH, 20-80 mm above an O20 hub on the same axis, and the medial land runs onto the
trapezius (or, tilted laterally, onto the clavicle / anterior deltoid). The ring is then the largest metal area in the
chain at 1-12 % in band, and the best ring loses to its own O20 twin by 20-26 gap points on the same axes. The crown
ring does not remove the 3R limiter either: J2 still travels the 60-90 deg circle off J1 (hub 2 at 113-140 mm, ~3 % in
band), which the spec's main risk predicted.

**What the sweep found instead (the in-model control):** the spherical 3R with an O20 J1 almost straight up the
scapula frame (bvec(29.9, 89.0); CMA presses on the el 89 bound), a12 82.6, a23 66.8, J3 wdir(92.2, 6.8), q 0.998:
gap **56.04** (score 79.62; reach 0.90, follow 1.00, in-band 14 0.345, in-band 10 0.203, contact 0.005; hub 2 at
139.5 mm, parking rule passed; Bench(60,160) fast, march, K2 dense, K6, audit clean). Its CMA is not converged
either (best moved 3.0 points over the second half). This belongs to the spherical family: hand k235 (and k231 57.11,
k163 58.03) to the verifier for Bench(110,360) exact and to the family's farm CMA (open el1 past 89 by
re-parametrising J1 around the vertical).

## Next (the loop)

1. Verifier: re-measure k235 / k231 / k163 on Bench(110,360) exact; if they hold, they lead the 3R family.
2. Farm CMA of the O20 control from k235 with J1 parametrised around the vertical (no el bound), until the gate passes.
3. The ring: only a small ring (outer land <= 22 mm, a KAA10-class 25 mm bore) seats on the crown, and it is still
   12 mm higher than an O20 hub and contacts across the body (plane 135-150, elev 105-135); no further ring sweep.
