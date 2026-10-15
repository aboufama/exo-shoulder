# Posterior max-margin Cardan (posterior-max-margin-cardan)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the singularity margin as a
   *constraint* (enough margin for dense continuity, ~15-20 deg), not the objective, and spend the rest on proximity:
   a spherical 3R's in-band is set by how high each rigid arc must ride over the highest skin it ever sweeps, and a
   Cardan has the longest arcs (90 + 90 deg). So: (a) lay every part out at its real radius (a 12 mm strap at 130 mm
   is 12 mm wide, not 22), (b) fit the hub seats to the oblique skin (wedge) instead of flat discs that stand 10+ mm
   off one side, (c) test the shorter-arc variant (a1, a2 < 90) that trades margin for link length - the variant that
   removes the measured limiter if the limiter is arc length.
2. **Rawest material.** The posed skin itself (signed distance per bench pose, `Bench.dist` / grid cache), the six fit
   clips walked frame by frame and interpolated (`K.continuity_dense`), and the per-direction skin motion of
   `pipeline/conformal/analysis/skin_motion_map_14.json` to place poles over still skin - not the catalogue's summary.
3. **Methods and tools.** `tools/concept_kit.py` (K1 closed-form Cardan closure, K3 per-ray skin march, K4 O20 hubs,
   K5 straps, K6 collisions, K2 dense continuity), the singularity-margin landscape over the bench poses (Fibonacci
   grid over b and W), numpy-vectorised sweeps coarse then refined, a two-pass layout so every sample sits at the
   real radius of its part.
4. **What other than me shows the number is right.** The bench (`concept_bench`, same scoring as the 68.93 baseline
   row), the in-model control (the kit template = the champion 3R on the same kit conventions, 70.19), the
   adversarial verifier re-running on the exact path / full bench, and a red-team pose list (behind-back plane
   -60..-90, overhead elevation >= 150, across-body, back-pocket) reported per pose with the part that pinches.

