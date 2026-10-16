# j2-arc-sector-3r - spherical 3R whose J2 is a link-1 arc-rail sector with a link-2 roller carriage

Lens "round3: J2 as a short curved rail with a real carriage, on a fold-free axis layout", family "spherical 3R
(virtual-axis J2)". Model `docs/concepts/models/j2-arc-sector-3r.py`, sweep log `docs/concepts/sweeps/j2-arc-sector-3r.json`,
row `docs/concepts/rows/j2-arc-sector-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the rail as a *surface of revolution about the J2 axis that hugs the body*, not as the spec's flat ring
     normal to p2. A carriage rolling about p2 only needs its running edges to be circles about p2. A conical V-edge
     band tangent to the sphere around GH (a lathe-turned constant section revolved about p2, no loft) keeps the whole
     8 mm width at one distance from GH. The flat ring stands up to 8 sin(beta) mm proud across its width.
   - Ask where the rail and the carriage *may* live before sweeping. A rigid rail fixed in link 1 must clear the
     highest skin it ever passes over in link 1's frame. A carriage fixed in link 2 must do the same in link 2's frame.
     So build two ceiling maps on the cone about p2 (link-1 frame for the rail, link-2 frame for the carriage and link
     2's root) and put the rail where both are low.
   - Count the rail's real length: travel + carriage + 2 end stops + the tab where link 1 laps on. This is the
     spec's risk (2), and it decides the morphology (below).
   - Run the hub control at identical axes (the rail-elbow lesson) in the same file.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance grids on Bench(60,160) (fast cache) and the exact path for
     Bench(110,360).
   - The motion clips (training split only).
   - The K3 march per ray in each frame, used for the ceiling maps (no digested atlas numbers).
   - pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas only as cross-checks.
3. **Methods and tools.**
   - tools/concept_kit.py: closure, members, K2 dense continuity, K3 march, K4 hubs, K6 collisions, audit.
   - fold-sph3r.py's crown, near-touch, overhead and frozen big-bench harness, imported rather than copied.
   - Ceiling maps in the link-1 and link-2 frames (scratch script, numbers below).
   - The farm for the sweep (tools/cloud_run.py sweep) and CMA-ES (tools/concept_cma.py), with the convergence gate.
4. **What, other than me, shows the number is right.**
   - The bench (outside judge).
   - The hub control at identical axes, which reproduces the catalogue's 73.57 to the digit.
   - The frozen shape on Bench(110,360) exact.
   - The verifier's harness, and the red-team pose list (rest, overhead, across, behind; closest metal; crowns and
     tops of the rail and carriage).
