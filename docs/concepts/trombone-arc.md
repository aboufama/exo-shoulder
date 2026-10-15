# Trombone arc (trombone-arc)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the band as a surface of revolution
   about p2 only where it actually passes the guide; the band end that never enters the guide is a free skin-fitted
   connector. Pick the axes (b, W, A1, A2) so the skin under the band's sweep is as uniform in radius as possible
   (a constant-radius band can only be in band where the skin under it is within 12 mm of its highest point), and let
   A1 = A2 so the band circle runs straight into the J3 hub with no separate link. Size the band ends from the guide
   positions the poses really need, and accept a few poses rather than a 90 mm tail.
2. **Rawest material.** The posed skin of every bench pose (Bench(60,160) grid SDF of the rig skin, K3 march along each
   metal ray), the fit-clip frames in time order (continuity along the interpolated motion), the everyday workspace
   poses. Not the digested baseline scorecard.
3. **Methods and tools.** tools/concept_kit.py: K1 two-circle closure (closed form), K3 march for undersides, K4 O20
   hub, K5/K7 straps and BOTTOM neck, K6 part-part collisions, K2 dense continuity; per-pose guide azimuth from the L2
   frame; sweep coarse (axes, A1/A2, arc range, band quantile) then refine around the best.
4. **What other than me shows the number is right.** The bench (B.report via K.evaluate, honest audit on), the
   adversarial verifier, and a red-team pose list (overhead, across-body, behind-back, the pose of the longest tail,
   the pose of closest band-to-skin and closest band-to-arm) reported below.
