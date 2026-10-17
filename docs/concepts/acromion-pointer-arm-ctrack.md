# acromion-pointer-arm-ctrack - gimbal at the shoulder + arm-fixed skin-shaped C-track for the humeral twist

Model: `docs/concepts/models/acromion-pointer-arm-ctrack.py` (shared kit + a carriage add-on). Sweep:
`docs/concepts/sweeps/acromion-pointer-arm-ctrack.json`. Row: `docs/concepts/rows/acromion-pointer-arm-ctrack.json`.
Preview: `docs/concepts/viz/concepts/acromion-pointer-arm-ctrack.js`. Round J1 (round 101) GATE 0 screen.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the twist window the track
   must carry for EVERY allowed J1 seat before drawing anything (the class lives or dies on it), with the carriage
   angle in the pointing frame placed where the window is densest, on the workspace poses and the clip frames
   separately; treat J1's seat as the design's main variable (the spec's acromion seat sdir(40,0) is the WORST class
   of seat for this decomposition - measured below); refuse the spec's radial slide where it stands up (a skin-normal
   slide counts travel + block) and measure its travel instead of assuming it; fit the arm-fixed track on the arm's
   own skin only (a pose where the torso reaches an arm-fixed part is a contact pose, never a reason to lift the
   part); make the track the arm end itself (BOTTOM cut and merged), so no neck crosses the carriage's path.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (track,
   carriage, yoke and hubs all fitted and checked on it pose by pose), the scapula / humerus rotations of the 60 fit
   clip frames and the 160 (and 360) workspace poses (the twist window is computed from them, not from
   ring_travel.json or the catalogue's 311-353 deg digest), and the body_pose humerus frame (E = GH -> elbow).
3. **Methods and tools.** tools/concept_kit.py (K1 closure = the gimbal at 90/90 or skewed, K2 dense continuity, K3
   march, K4 O20 hubs, K5 straps, K6 collisions + `over`), a per-pose carriage riding the fitted track (add-on in the
   model), a circular sliding-window count for the twist window, CMA-ES / coarse grids on Bench(60, 160) fast, frozen
   wear on Bench(110, 360) exact.
4. **What shows the number is right besides me.** The bench (it scores every sample I hand it on its own skin
   distance, contact included), the kit audit (sampling, O20 hubs, pose locality), the adversarial verifier and the
   alignment auditor, and the red-team list: rest, overhead (elev >= 140), across-body, behind-the-back, the pose
   that ends the carriage's travel, the anteromedial track end against the chest, hub 1 when the arm comes nearest
   to the gimbal pole, and the radial slide's travel (the spec's hidden stand-up).
