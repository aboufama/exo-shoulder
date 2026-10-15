# Scapula halo track

The base is a closed, non-circular track fixed to the scapula handler. It is drawn on the skin that moves least
against the scapula, around the acromion summit. J1 is a bogie carriage on that track: its position s along the track
is the joint value. J2 is an O20 hub on the carriage, with its axis radial through GH. Link 2 is a strap of arc a2 to
J3, an O20 hub on the deltoid cap that is fixed to the arm. That makes 3 active DOF (s, q2, q3) and no free passive
coordinate.

## Deeper-version prompt (answered before modelling)

1. **What would a top mechanism designer do that the spec does not ask for?**
   - Treat the track as a cam surface, not a ring. Its radius from GH should follow the skin under it, so the track
     hugs the skin. The radial offset this creates at J2 is then taken up by a cam-set slide. That slide is set by s
     alone, so it is determined, not free.
   - Draw the track's plan shape from the closure itself (where the J2 crossings actually land), not only from the
     motion contour.
   - Check the transmission angle at the crossing, because a near-tangent crossing back-drives the carriage.
2. **Rawest material.**
   - The posed render skin of every bench pose: B.dist and the K3 requirement are marched on it, with no percentile
     summaries of radii.
   - The scapula-frame skin-motion grid in `pipeline/conformal/analysis/skin_motion_map_14.json` (the per-cell motion
     values, not the zone summary). The track's plan shape is drawn from it.
   - Every 10 fps frame of the fit clips, for continuity (the bench samples every ~6th frame).
3. **Methods and tools.**
   - Closure is a 1-D root search of angle(u(s), w) = a2 along the track polyline, refined on the interpolated curve.
   - The branch is set by the sign of t.w at the root (in or out of the circle about w).
   - Skin-fitted undersides use the sphere-traced K3 requirement, vectorised over samples.
   - Non-adjacent clearance is checked with KD-tree interval-overlap tests.
   - The sweep is coarse, then refined, over track threshold, shrink, W, a2, sigma and q, on Bench(60,160) with the
     fast grid cache.
4. **What shows the number is right, other than me.**
   - The common bench, which uses the same metric code as the 3R baseline (gap 68.93).
   - The adversarial verifier.
   - A red-team pose list: the jamming pose (where the crossing goes tangent), the pinch point (the smallest
     metal-to-skin distance over the taken poses), and behind-the-back and across-the-body extremes.

