# desmo-slipper-knuckle-3r - Desmo slipper (round 12, judge pick 2)

The verified lead slipper-nose-knuckle-3r (18.49 frozen exact, Bench(110,360)) with its force closure removed:
no clock spring on K, no stop-A pin and no stage-1 roller. Both drive stages are positive both ways:

* stage 1 (hub 2 -> crank): a crowned 440C O1.5 pin, pressed in the crank's short arm, runs in a 1.52 x 1.5 groove cut
  in the underside of hub 2's cap ring (link 2);
* stage 2 (crank -> link 1a, cell A): the verified O2.5 slipper nose runs in a two-walled slot. The slot is the swept
  envelope of the nose (the union of nose discs + 0.01 mm) with the convex material corners closed to R >= rho_e.

3 active DOF (J1, J2, J3). K is slaved and never read. 0 passive translations, 0 springs.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Treat the groove as a 3-D cam, not a planar one. The pin turns about dR, and dR is tilted off u2, so the pin
     drifts along u2 and tilts across the groove. Measure that drift and tilt, then decide the crown from the numbers.
   * Calibrate the cam's sense from the model's own pose transforms, not from a formula. The "with" vs "against"
     arrangement moves the groove pressure angle from about 30 deg to about 78 deg, and one sign error flips the verdict.
     Here the relative rotation of link 2 about u2 per unit K is fitted by regression on the fit bench's taken poses.
   * Measure the slop the wearer would feel: K play with the crank held, and with the crank free in its groove
     clearance. Measure both directions, including the reversal at the dwell exit.
   * Count the new metal honestly. The lead's rim lobe was never sampled past O20. The groove ring's outer wall
     (r <= 10.98) is sampled here as link-2 metal, so this design pays for metal the lead got for free.
   * Keep the lead's seats and law. The gain is complexity (15.75 vs 18.25), so the bench target is a paired tie,
     not a new gap.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path
   behind Bench(110,360). Also the pose transforms of every body on every bench pose, which give the pin's path in
   link 2's frame directly (no digested cam table). Two further sources: the skin-motion map
   pipeline/conformal/analysis/skin_motion_map_14.json for the hub-2 deltoid region, and the verified lead's geometry
   (docs/research/slipper_mechanism/geo_bench.npz) as a cross-check of the synthesis.
3. **Methods and tools.**
   * Exact spherical-cam synthesis per 0.25 deg of K on the model's own axes: both pressure angles with friction
     (43 - atan(mu)), curvature and cusp, axial drift.
   * Morphological slot check: the nose disc must stay inside the union of swept discs, with K stepped by bisection
     to 0.005 deg.
   * Built on tools/concept_bench.py and the lead's verified model chain, loaded unchanged
     (slipper-nose -> roller-longdyad -> sidecar-roller-flank -> sidecar core), with the frozen-shape claim protocol.
   * The farm (tools/cloud_run.py) for sweeps, then CMA-ES from the top configurations.
4. **What, other than me, shows the number is right.**
   * The bench itself (fast, then exact frozen).
   * A control run: this file with the desmo additions switched off must reproduce the lead's 13.0 fast.
   * The adversarial verifier (docs/concepts/verify/slipper-nose-knuckle-3r.py retargeted).
   * The red-team pose list below: rest, overhead, across the body, behind the back, the lead's two contact poses
     237 / 264, and the dwell-exit reversal.
