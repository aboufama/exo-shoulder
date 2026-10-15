# Back-anchored ring-ended 3R (back-anchored-ring-3r)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the two rings as *what they
   cost on curved skin*, not only what they save in stack: an O45-65 flat annulus is 3x the O20 footprint, so on a
   curved back or arm it must stand higher to clear its highest point. Test ring vs O20 hub at each end (the spec only
   offers rings), size the ring to the flattest skin patch the ray actually meets, and connect the arm ring to the
   user's BOTTOM bar honestly (a bracket when the ring sits posterior of the lateral saddle). Then attack the limiter
   the sibling posterior 3R measured (links 26-30 mm off the skin): shorter arcs (a12, a23 < 90) and a J3 placed so
   link 2 lies along the arm, not across the moving posterior deltoid.
2. **Rawest material.** The posed skin itself (signed distance per bench pose through the fast grid cache /
   `Bench.dist`), the six fit clips walked frame by frame and interpolated by the kit's dense continuity, and
   `pipeline/conformal/analysis/skin_motion_map_14.json` (per-direction radial skin motion in the scapula and humerus
   frames) to choose where the J1 ray and the J3 ray pierce still skin - not the catalogue's summary numbers.
3. **Methods and tools.** `tools/concept_kit.py` (K1 two-cone closure, K3 per-sample skin march, K4 flat O20 hub,
   K5 straps with the 60 deg climb, K6 part-part collisions, K2 dense continuity along the clips, audit), flat
   annulus members for the thin-section rings (fitted along their own axis like K4), numpy-vectorised sweeps coarse
   then refined on Bench(60, 160).
4. **What other than me shows the number is right.** The bench (`concept_bench`, the same scoring as the 68.93
   baseline row), the kit's honesty audit (`honest` flag), the in-model control (O20 hubs in place of the rings,
   same chain), the adversarial verifier on the exact path / full bench, and a red-team pose list (overhead elev >=
   150, behind-the-back, across-the-body with internal rotation, back pocket) with the part that pinches per pose.
