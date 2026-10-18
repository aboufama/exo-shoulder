# cap-plateau-knuckle-3r - Cap-pole slaved knuckle 3R (round 14, pick 2: the cap-seat lens gate 0)

The lead's slaved-knuckle chain (J1 -> link 1a -> K -> link 1b -> J2 -> link 2 -> J3) moved to the posterolateral cap
pole: J1's O20 hub on top of the shoulder over the lateral scapular spine / posterior acromion. Three cells of the K law:
A (routed U-law, a2 70), B (short stop A, one-sided plateau), C (two-sided dwell: K opens on the folded side too).
3 active DOF (J1, J2, J3), K slaved (passive R, set by the law), knee pins outside the count, 0 passive translations.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Run the CONTROL first, in the same instrument and at the same margin. The cap seat's case rests on kinematic
     counts (C 275, B 271, A 295) set against the lead's "269-271". But that ceiling is a real-model number, with the J3
     stop and metal included. The lead's seats and law have to be counted kinematically in the same instrument, at the
     same margin, before the cap's surplus is believed.
   * Count the K play inside the fold margin (m = 5 + 0.23 deg), not after it. The lead's held margin is 5.006, so
     the play is the binding item.
   * Bound before searching. Metal only removes takes, so the kinematic count over each cell's whole sweep box is a hard
     ceiling on reach. If that ceiling is below the 279-take bar everywhere in the box, no CMA on metal can rescue the
     cell, and the convergence gate is replaced by a proof by bound.
   * Red-team cell C's folded lobe for feel. As J3 passes under J1 (th 9-12), J1 has to spin at ~1/sin(th) per unit of
     arm motion.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path behind
   Bench(110,360) (tools/concept_bench.py), plus the per-pose J1 / K / J2 / J3 axes in the scapula and humerus frames
   (the model's own body transforms). The proposers' pile-up proxies (scratchpad capseat/m.py, o.py, n.py) are digests
   and are used only to read their configurations.
3. **Methods and tools.** The fold-ceiling paired kit (docs/research/fold_ceiling/kit_paired.py: O20 hubs, K3-march
   skin-fitted 3 x 12 mm straps, the neck to BOTTOM, K2 dense continuity, K6 part collisions, exact signed distance),
   with only the K law replaced per cell. The frozen protocol: fit on Bench(60,160) fast, wear Bench(110,360) EXACT. A
   vectorised kinematic box scan for the ceiling. A finite-difference J1-rate probe on the low-th poses. Compute is
   local only, niced, with <= 2 processes.
4. **What, other than me, shows the number is right.**
   * The CONTROL: the lead's seats and law in the same instrument, worn the same way. The comparison is paired: same
     omissions (no drive metal, no cuff knee), same margin.
   * The bench (fast, then exact frozen).
   * The round-102 judge's reproduced kinematic counts (A 295, C 275 at m 5).
   * The adversarial verifier.
   * The red-team list: rest, overhead (elev >= 140), across the body, behind the back, and the low-th poses of cell C's
     folded lobe.

## Measurements

(filled in as they land; see below)
