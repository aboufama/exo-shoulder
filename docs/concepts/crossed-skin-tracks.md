# Crossed skin tracks with a telescoping swivel

Two tracks shaped to the skin cross at a radial swivel; there are no intermediate links. T_S is fixed to the
scapula handler (a halo around the acromion summit). T_H is fixed to the arm (over the deltoid cap, held by a neck
to BOTTOM's bar). Carriage A runs on T_S (J1, s), carriage B runs on T_H (J3, t), and a thin-section ring bearing
between them (J2, q2) turns about the radial line through the crossing. A passive radial slide inside the swivel
takes up the radius difference of the two tracks at the crossing; the closure sets it. 3 ACTIVE DOF, 1 PASSIVE
(closure-set, cannot sag).

## Deeper-version prompt (answered before modelling)

1. **What would a top mechanism designer do here that the spec does not ask for?**
   - Treat both tracks as curves in their own body frames, and draw the arm track from the crossing locus itself
     (where the J2 pole lands in the humerus frame over the clips), not from a circle chosen first.
   - Make the radial stack the design variable it is. The outer track must clear the inner one everywhere they
     pass over each other, so the outer track is lifted only where an overpass actually happens and hugs the skin
     elsewhere.
   - Take the swivel axis seriously as a line through GH that also pierces the outer rail. Carriage B must hang
     under its rail, and the slide guide sits beside the rail (the spec's 9-13 mm stack is too thin: 4 + bearing +
     4 + rail 5 = 15-19 mm).
   - Check transmission at the crossing: a near-tangent crossing is a jam. The tangent angle is the
     condition number of the 2x2 crossing Jacobian.
2. **Rawest material.**
   - The posed render skin of every bench pose, through B.dist and the K3 ray march. There are no radius
     summaries.
   - The per-cell scapula-frame motion grid in `pipeline/conformal/analysis/skin_motion_map_14.json`. The halo
     plan shape is drawn from it.
   - Every 10 fps frame of the fit clips for continuity and branch choice. The bench samples about every
     sixth frame, which would hide a crossing that jumps.
3. **Methods and tools.**
   - Exact polyline-polyline intersection on the sphere (great-circle segment pairs, vectorised) for the crossing.
   - Branch tracking by the nearest crossing to the previous 10 fps frame.
   - The K3 requirement (vectorised ray march on the fast grid cache) for skin-fitted undersides, with a quantile
     over the closing poses.
   - Slope-limited bogie radii.
   - Interval-overlap collision tests between non-adjacent parts.
   - A sweep that runs a kinematic screen first (cheap, no geometry), then the full bench on the best track
     shapes, then a refinement of stack, quantiles and halo offset, all on Bench(60,160).
4. **What, other than me, shows the number is right?**
   - The common bench: same metric code, poses and skin as the 3R baseline (gap 68.93).
   - The adversarial verifier.
   - A red-team pose list: rest, overhead (elev 160), across the body, behind the back, plus the measured worst
     poses of the best config (the crossing that goes tangent, the frame where the slide runs out, and the pinch
     point with the smallest metal-to-skin distance).
