# meridian-goniometer - J2 as an arc rail beside the arm's elevation path (no J2 hub)

Model: `docs/concepts/models/meridian-goniometer.py` (shared kit). Sweep: `docs/concepts/sweeps/meridian-goniometer.json`.
Row: `docs/concepts/rows/meridian-goniometer.json`. Bench(60, 160), fast grid cache, K3 march, K2 dense, K6 on.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Notice that the spec's rail cannot be
   skin-fitted along its length: a carriage of 30-50 deg of arc is a rigid body, so its track must be a true circle
   about the virtual axis a2 (any radius varying with phi breaks the rotation about a2). The free choice is WHERE that
   circle sits (its cone angle alpha off a2, the side, the radius fitted on the skin), not its shape. Then decouple the
   rail from the pointer: the virtual-axis rail replaces a J2 hub in ANY spherical 3R, so try it both on the spec's
   pointer + humeral C-slide (whose J3 twist window is the measured reach ceiling 0.50 of pointer-cslide) and on the
   general 3R whose third axis is an arm-fixed hub (the champion's hub 2 floats at 105 mm and is never in band - the
   rail is the lever that removes exactly that part). Let the carriage lead or lag the arm (dphi) so it sits on the
   lowest skin, and cut the rail's q2 range from the posed data (a share of the closing poses), not from a guess.
2. **Rawest material.** The posed skin of every bench pose through the bench's signed-distance grid (the rail and
   carriage radii are K3-marched per sample per pose, the max taken because the track is one circle), the scapula and
   humerus rotations of the 60 fit-clip frames and 160 workspace poses (the q2 window and the carriage's path come from
   them), and the proximity atlas per-direction ceilings (where a scapula-fixed vs a swing-frame part can be in band).
3. **Methods and tools.** tools/concept_kit.py (K1 closure, K2 dense continuity on values and axes, K3 march, K4 hubs,
   K5 straps + `over`, K6 collisions, K7 neck, audit), 'cap' members for the circular rail and carriage (one radius:
   a surface of revolution about a2), pointer-cslide's band/shoe/neck for the spec's J3, Sobol coarse sampling then
   CMA-ES (pycma) on the cloud CPU farm (tools/cloud_run.py sweep) until the convergence gate passes.
4. **What shows the number is right besides me.** The bench (it scores the metal I hand it), the kit audit (sample
   density, pose locality, honest flag), the adversarial verifier re-running the best params, and a red-team list:
   rest, overhead abduction 150-160, overhead flexion, across-body (plane >= 110), behind-the-back (extension +
   internal rotation), the pose at each end of the rail's q2 window, the rail's sweep over the head/neck at large q1,
   and the bridge crossing the rail.
