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
