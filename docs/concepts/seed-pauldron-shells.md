# seed-pauldron-shells - nested sliding shells (pauldron) + arm ring

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat each "shell on shell" slide as
   what it really is: a large-diameter revolute about an axis through GH, i.e. a ring bearing (a T-slot channel at a
   colatitude g about the axis, slider inside, iglidur liner) whose stack (7 mm) replaces the O20 hub's 12.25 mm
   crown - and only build the ARC each slider actually travels (measured on the bench), not a full shell. The webs
   between the rings follow the skin (K3 undersides) instead of one sphere about GH; the arm ring axis may be tilted
   off the humerus axis (still through GH) so a circular track sits closer to a non-round arm.
2. **Rawest material.** The posed skin of every bench pose itself (signed-distance grid of the rig's render skin per
   pose, fit-clip frames + everyday workspace; held-out clips never loaded), the slider travel measured per pose from
   the closure (not a range from a summary), and the per-sample skin requirement marched along rays from GH.
3. **Methods and tools.** tools/concept_kit.py (K1 two-circle closure, K2 dense continuity along the interpolated
   motion, K3 march undersides, K6 part-part collisions, K7 neck to BOTTOM), tools/concept_bench.py Bench(60, 160) on
   the fast grid cache, vectorised over every pose; a coarse-then-refined grid sweep written incrementally.
4. **What, other than me, shows the number is right.** The bench (the same outside judge as the 3R champion,
   gap 68.93), the adversarial verifier re-running the model on the exact path / full bench, and a red-team pose list
   (rest, overhead, across the body, behind the back, plus the measured worst poses of the best config) in this file.

## What was modelled (docs/concepts/models/seed-pauldron-shells.py, on tools/concept_kit.py)

Kinematics: a spherical 3R. u1 is fixed in the scapula, u3 in the humerus, and u2 comes from the K1 two-circle
closure (residual 0). That gives 3 active rotations. The cuff's slide along the humerus is the 1 passive coordinate:
the arm sets it through the cuff, and it is static on the fixed-GH bench rig. No coordinate is left undriven. The
model starts from the champion's axes (rows/baseline-3r.json) so the joint realisation is the only thing that
changes. The spec's own axes (u3 = the humerus long axis, so the C-ring goes round the arm) are covered by `wd ~ 0`
with `gamma` larger than the arm, and they were tried first (see the measurements below).

Joint realisation (the morphology): there is no O20 hub at any axis. Every revolute is a sliding pair concentric
with GH: a T-slot channel (floor 2 + slider 2 + lips 2 + liner 1 = 7 mm, 12 mm wide) on a band at colatitude g about
the axis. It covers only the ARC its slider travels over every closing bench pose (plus the slider length), and it
has one radius, fitted so it clears every pose it takes at quantile q. The arm joint is a C-track (6 radial x 8 axial)
plus a 25 x 12 x 6 carriage riding 1 mm above it. Shell webs are 3 mm straps on great circles. A web is WELDED to a
track on its own shell at the track's level, or it leaves a slider inside the other shell's channel and is LIFTED over
it (track top + 1 mm). Which body carries each track (`side1`, `side2`: proximal or distal) is a design choice that
hubs do not have, and the sweep covers it. The K7 neck (14 x 6) leaves the arm ring in the middle of the C's gap,
where the carriage never goes, and passes over the ring and the carriage path by 1 mm wherever it crosses them.

Spec corrections:
1. "Shell i rotates about u_i" needs a guide that holds the other two rotations and retains the shell. Here that is
   the T-slot channel and slider.
2. A shell need not be one sphere. Only the sliding bands must be surfaces of revolution about their axis. The webs
   follow the skin (K3 undersides, 60 deg climb), which is never farther from the skin than the spec's
   one-radius-per-shell lames.
3. A C-ring round the humerus long axis (the spec's ring) is impossible on this body. Rays from GH at 35 deg from the
   arm axis leave the deltoid at about 110 mm laterally and never leave the body medially (they enter the chest). The
   carriage also travels 297 deg round the arm over the bench (axial rotation plus gimbal twist). So the ring either
   floats at 400 mm or loses most poses. With `wd = 0, gamma = 35` every member sat at 400 mm (gap 359.5, contact
   0.96). The arm ring was therefore moved onto the champion's J3 axis (lateral arm, wd 86) as a small ring bearing.
4. The neck cannot weld to the ring anywhere the carriage travels: it collided in 27 % of poses. It now leaves the
   ring in the C's gap and passes over the ring.

## Measured (Bench(60, 160), fast grid cache, kit mode 'march', K2 dense continuity, K6 collisions, kit audit)

107 configurations, all in `docs/concepts/sweeps/seed-pauldron-shells.json` in the order they ran:
- k 0-33: coarse grid on the champion's axes over g1, g2, gamma, cov2, cov3 and the track sides. The g1 = 20 half
  was cut; g1 = 16 / 20 were tried later.
- k 34-56: one-at-a-time refinement (g2, cov2, q, each axis +- 6-20 deg, sigma, web width, sides, g1).
- k 57: hybrid with an O20 hub at J2.
- k 58-103: two local random searches of the axes.
- k 104-106: the neck-from-ring-centre variant.

Only configurations that pass the kit audit (`honest`) count. 25 do not: with q = 1.0, or once more overhead poses
are taken, track 2 and both webs float to 200-400 mm, so they never touch and never count as in band. The audit
flags their sparse samples. Their low gaps (down to 70.26) are rejected, and the event log carries a retraction.

| | gap | reach | follow | in-band 14 | in-band 10 | contact |
|---|---|---|---|---|---|---|
| champion 3R (rows/baseline-3r.json) | 68.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |
| **best honest, k = 88** | **79.46** | 0.750 | 1.000 | 0.272 | 0.151 | 0.016 |
| k = 39 (champion axes, g 12/14/20, q 0.98) | 79.90 | 0.738 | 0.917 | 0.314 | 0.167 | 0.017 |
| spec's C-ring round the humerus axis (wd 0, gamma 35) | 359.5 | 0 | 0.12 | 0 | 0 | 0.96 |

Best configuration (k = 88): az 2.84, el 86.1, a1 83.0, a2 64.2, wd 83.9, wa 13.9, sigma -1, g1 16, g2 14,
gamma 16, tracks 1 and 2 on the distal bodies, ring on the humerus, cov3 0.9, q 0.98. Arcs: J1 334 deg, J2 253 deg,
J3 239 deg. Closure residual 0. Minimum singularity margin 10.05 deg. 0 branch flips. Collisions in 0.5 % of closing
poses. Ti mass 251 g. Audit clean.

In-band 2-14 mm by member (best): track1 0.65 (0.85-0.94 in other configurations: one radius of 58 mm, flat over
every pose), ring 0.18, neck 0.43, web1 0.09, carriage 0.003, **track2 0.00, web2 0.00**.

## The limiter (measured) and the variants that tried to remove it

**J2, the middle axis, as in the 3R champion, and a ring makes it worse.**
- Along u2 itself the skin requirement over the taken poses is p50 61, p95 79, max 86 mm.
- A track at colatitude 14 deg round u2 spans 200-270 deg of azimuth, and its one radius must clear the worst of
  those samples. Per-sample q95 is 64-107 mm, the per-pose max reaches 132 mm, so it sits at about 120 mm.
- The worst poses are elevation 165 with axial -90, plane 15 / elevation 90, and forward-flexed reaches at
  elevation 60-75. In these the J2 ring passes over the bulging deltoid / acromion.
- Web 2 needs only 54-78 mm of its own, but it starts at the track-2 slider and is lifted over the channel, so it
  rides at track-2 level and is never in band.

Variants tried, all measured:
- g2 8 / 14 / 20 / 28 deg: no help.
- cov2 0.8-0.9 (trim the track-2 arc): loses follow, gap 101-109.
- Track 2 on shell 1 or on shell 2 (side2 0 / 1): within 3 gap points of each other.
- An O20 hub at J2 (k 57): gap 100.2. The hub also floats, and web collisions at the hub stack rise to 16 %.
- A local search of the axes: 79.9 -> 79.5.

**J3's C-gap loses the overhead.** The red team traces all 22 workspace poses lost "off arc" to the J3 ring (cov3
0.9 leaves the gap the neck exits through), every one at elevation 60-180 deg. A further 14 are lost to the closure
margin (elevation 60-180). Elevation 150-180: 11 of 13 poses lost.

Variant that removes the gap: the neck leaves from the ring's centre (a spoke at ring level that the carriage never
crosses) and passes over the ring and the carriage path, so a full ring is allowed (k 104-106). Reach rises
0.75 -> 0.86, but the extra elevated poses send track 2 to 204 mm, which fails the audit. Removing the J3 limiter
exposes J2 harder.

## Red team (best honest configuration, k = 88)

| pose | result |
|---|---|
| rest (elevation 0, any plane) | taken, minimum 2.7-2.8 mm, track 1 closest |
| overhead (elevation 165, axial -90) | lost: the carriage leaves the C's arc (planes 75-105), or the closure margin is 8 deg < 10 (plane 120) |
| across the body (plane 150) | elevation 75-90 taken at 2.4 mm; elevation 105-120 lost off the J3 arc |
| behind the back (plane -75 / -45, axial 135-165, elevation 0-30) | taken, 2.5-2.7 mm |
| reverse (plane 75-120, axial -135 / -165, elevation 30-45) | taken, but the **neck pinches to 1.0 / 1.7 mm** |
| contact poses (1.6 % of taken) | track 2 (2 poses) and the neck (1); one workspace pose sits at 0.0 mm |

Not modelled, in common with the champion's hub 1: the scapula handler's mount to J1. With track 1 on shell 1
(side1 = 1) that mount is a stud from the scapula handler down through the channel slot onto the slider. Web 1 is
welded to the track's outer edge and sweeps 334 deg round it, so the mount must reach the slider over the inside of
the ring (from the axis side) or stay below web 1's lifted zone. This is a real packaging constraint for the L1 CAD.
Also, the track arcs are design dimensions fitted to the bench (like the undersides). The build caches them per
configuration, so it is pose-local for K2 and the audit.

## Verdict

**Dead as a morphology** (best honest gap 79.46 vs 68.93; not worth a GPU sweep). The nested-shell idea does not
remove the 3R family's limiter, the middle axis J2. A revolute concentric with GH has to be a surface of revolution,
so spreading J2 over a ring makes its one radius clear the worst of a 250 deg arc instead of one direction.

**Transferable finding (worth grafting onto the champion):** a scapula-fixed ring bearing at J1 (a T-slot channel at
colatitude 12-16 deg round u1, 7 mm stack, 334-356 deg arc) sits at one radius of 58-59 mm in every pose and is
65-94 % in band. It is a low-profile replacement for the champion's hub 1 at 12.25 mm. The spec's C-ring round the
humerus axis is impossible on this body (see spec correction 3).
