# offset-arc-selfalign: skin-shaped offset arc + self-aligning cuff

## Deeper-version answers (written before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Size the stage from the measured
   offset error instead of guessing it. The J1/J3 offsets are chosen by a minimax LP that minimises the radial slide
   travel (the slide that squeezes the liner), in the spirit of the P0 offset-axis LP. The designer would also ask
   whether the arc's radius is even the limiter. If the 3R family loses on how high the rigid band has to sit over the
   skin it passes, a circle that is not centred at GH only helps where the skin envelope really is a circle with a
   different centre. Measure that before sweeping.
2. **Rawest material.** The posed skin itself per bench pose (the signed distance of every band sample to the posed
   render skin, B.dist), the full-rate fit clips (continuity and the arc's guide-azimuth range at 10 fps, not the 60
   sampled frames), and the skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`. On that map the W axis
   (BOTTOM hub) moves 23.4 mm relative to the skin under it, and the b axis (base) only 1.8 mm. That is the size of
   the problem the stage must absorb at J3 and the reason the stage sits on the arm side.
3. **Methods and tools.** Exact composed-rotation kinematics (orientations do not depend on where the axes sit,
   only the end translation t_E does). Sphere tracing on the skin SDF for the lowest rigid height of each member over
   the poses it takes (the concept_baseline convention: the p-th percentile, poses above it count as contact). A
   minimax LP (scipy HiGHS) for the axis offsets. Box, annulus and cylinder SDFs for >= 1 mm part-part clearance. All of
   it runs on tools/concept_bench.py (fast SDF cache).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, the same poses and metrics
   as the 3R baseline at gap 68.93), the adversarial verifier that re-implements the chain, and the red-team pose list
   below (the poses that set each rigid height, the poses where a slide hits its stop, the worst part-part clearance).

## Result (bench fast, 60 clip + 160 workspace poses, 47 configurations)

| | gap | reach | follow | in-band 2-14 | in-band 2-10 | contact |
|---|---|---|---|---|---|---|
| spherical 3R baseline (rows/baseline-3r.json) | **68.93** | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |
| this morphology, spherical reference (no offsets, no stage; k 8) | 144.47 | 0.594 | 0.717 | 0.228 | 0.134 | 0.233 |
| **this morphology, best (k 38)** | **133.12** | 0.606 | 0.733 | 0.296 | 0.159 | 0.217 |

Best configuration: champion trombone axes (b az 32.55 / el 80.56, W 71.38 / 4.78, A1 77.41, A2 81.45, branch -1),
J2 line offset 6 mm toward -W's azimuth (o2w -6), arc shifted 6 mm along the J2 line (dza +6), J1 / J3 offsets from
the minimax LP (o1 = (-0.12, -0.16), o3 = (1.16, -0.64) mm), stage limits +-25 / +-10 / +-5 mm (used: 2.9 / 4.0 / 3.9),
rigid heights at the 94th percentile of the poses that can clear the skin. Band radius 114 mm from the J2 line (the
GH sphere would be ~57), J1 ring underside 55 mm along b, rail underside 70 mm along the stage normal.

**Verdict: dead as specified, so it is not worth a GPU sweep.** It is 64 gap points worse than the spherical 3R. The axis
offsets and the self-aligning stage buy 11 points over its own spherical version (144.5 -> 133.1), and the slides
stay small (<= 4 mm). Neither part is the problem. The rigid circular band is.

## The measured limiter (red team)

- **The trombone tail goes into the neck overhead, at any radius.** Each band azimuth was traced separately over the
  180 kinematically valid fit poses (`limiter` run). The hub side of the arc (22-58 deg from W) needs 45-64 mm (p90),
  which would sit in band. Past the guide (azimuth 98 deg), the tail at 106-126 deg cannot clear the skin at any height
  in 13-25 poses: the whole "Raise overhead" clip (plane 30, elevation 66-150, axial -43..-60). As a group, the band
  cannot clear in 30 / 180 poses. Its p50 need is 62 mm, but a circle has a single radius. Any percentile that keeps
  the overhead clip pushes it to 114-150 mm, where the band and guide sit > 31 mm off the skin (band in-band 0.7 %,
  guide 0 %). The red-team "closest" list is five Raise-overhead frames with metal >= 31.75 mm inside the body.
- **Offsets large enough to reshape the arc break the stage.** With J2 offsets >= 6-12 mm off the best direction
  (o2w +-12, o2n +-10), the radial slide needs more than +-5 mm in 48-169 / 220 poses. That is the liner-squeeze limit.
  The LP cannot compensate, because a 100 deg J2 swing times a 10 mm offset is ~15 mm of translation. So the offset
  range that keeps the stage honest (<= 6 mm) is too small to turn a 57 mm circle into a skin-shaped one.
- **Workspace coverage costs more than it gains.** 38 workspace poses (behind-back / internal rotation, plane -90..-75)
  put the guide off the arc. Lengthening the arc to cover them (arc_ws 0.5-0.95) lengthens the tail and adds contact:
  gap 171-196.
- Named poses: rest is taken (min 2.8 mm, median 20 mm, slides 0.7 / -0.6 / -3.5 mm). Across-body is taken (min 2.3 mm).
  Overhead (pl 30 el 150) has the guide off the arc. Behind-back (pl 0 el 45 ax -30) has the band 22 mm inside the body.
  The minimum part-part clearance over taken poses is 3.15 mm (the hub's lower plate vs the along-carriage): no jam.
- The in-band share that is there comes from the parts riding on the arm and scapula: rail 67 %, J1 ring 61 %,
  carriage 42 %. Over the taken poses, the band, guide and connector are > 31 mm off the skin.

## New knowledge (predicts beyond this morphology)

1. **A rigid arc that slides through a guide has to clear every pose with every part of its length.** The part past
   the guide is the worst: overhead, it lies where the neck and trapezius are, and no single radius clears it. This
   kills any trombone / curved-rail concept with a free tail (trombone-arc, magrace-arc-chain if its tail is rigid)
   unless the tail is stowed. It predicts trombone-arc's own number: gap >= 144 on this bench (the spherical reference
   above is that design with real-size parts).
2. **The fix is to stow the tail, not to reshape the circle.** The band only has to be circular where it passes the
   guide. A tail that coils onto a drum in L1 past the guide (a steel tape / zipper-mast band), or flexes away
   from the neck, removes the limiter. With the tail gone, the per-azimuth needs (45-64 mm p90) say that the
   remaining arc can ride ~55-65 mm from the J2 line, in band. That is a new morphology to ideate: a coil-stowed arc.
3. **A self-aligning 3-slide stage on the arm costs little.** With LP-chosen axis offsets, the slides use <= 4 mm
   over the bench, and the stage's own metal is 42-67 % in band. Other concepts can borrow it (for example to absorb
   GH translation and handler slip, R10). The bench cannot see that benefit, because its GH is fixed.

## Model notes (changes from the interrupted session's draft, and spec corrections)

- Fixed: guide axes were read from the wrong object (crash). The fit is now batched over all poses: one distance
  call per sphere-tracing iteration instead of one per pose, ~5 s per configuration instead of > 10 min. Traces are
  clamped (-60..160/200 mm), so a ray that never leaves the body stops at the clamp instead of walking out of the
  SDF box into the slow exact path.
- Fixed: a rigid height is now the percentile over the poses where the part can clear the skin at some height. A pose
  where it cannot (trace at the clamp) is scored as contact and does not set the height. Before this fix, the band
  radius ran to the 200 mm clamp. A first 63-configuration pass with that bug was discarded; it is not in the sweep
  file.
- Spec correction: the spec's "fit (o2, z_a, rho) by least squares to skin + 6 mm" cannot be honoured. A circle that
  slides through a guide must clear the skin under its whole length in every pose, so rho is set by clearance (the
  rigid-height rule), not by a least-squares fit. o2 and z_a are swept.
- Honesty: all three slides are set by closure. Orientation is exact, because composed rotations do not depend on
  axis placement, and the slides take the end translation. J2 has a +-12 deg arc-end margin. Full-rate continuity is
  checked on the fit clips (max joint step 25 deg). Part-part clearance is >= 1 mm across non-adjacent parts. The O20
  hub is at real size (r 10, 12.25 stack), the KAA-class ring is 19-26 x 6 mm, and the guide is 30 x 22 x 10.
  Skin-facing undersides are sampled on a 2 mm grid. Held-out clips are never used.

Files: `docs/concepts/models/offset-arc-selfalign.py` (`python3 ... sweep N`), `docs/concepts/sweeps/offset-arc-selfalign.json`,
`docs/concepts/rows/offset-arc-selfalign.json`.
