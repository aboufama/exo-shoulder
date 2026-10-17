# skinnormal-shortk-knuckle-4r - near-touch-robust redundant 4R (short sensed knuckle on the lead's J1 seat)

Round 10, the 4-joint route inside the DOF cap (Keemink 2018 TNSRE 26(4)): pick1's verified sensed-knuckle 4R
(minarc-stop-knuckle-4r, 18.40 frozen exact Bench(110,360)) with only the knuckle and the seats moved. 4 active (K sensed),
2 passive pins (the cuff knee), 0 passive translations, cx 32.5 (tools/simplicity.py v2). This is never the 3-joint lead.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Ask first where the 4R's points go between
   the fit and the frozen wear, before searching anything: pick1 went 11.57 fast -> 18.40 frozen, and its frozen reach
   (0.750) sits 15 poses under its own law-only (kinematic) reach on the same 360-pose bench (0.806). So the job is not
   kinematics, it is *what the frozen shape hits on poses the fit never saw*. A designer would (a) compute the law-only
   ceiling of every seed on Bench(110,360) (cheap, seconds) and the fast->frozen leak per lost pose (slide / contact /
   fold), (b) re-check every built tolerance in the verifier's own reading (CB_FOLD_MARGIN 5.5) before the expensive
   wear - a stop drawn on a singular dyad is a mechanism that locks, and (c) only then sweep, ranking candidates by the
   frozen-reach ceiling, not by the 160-pose in-sample number (round-3 lesson (c)).
2. **Rawest material.** The posed skin itself (the bench's signed-distance grids, worn exact on Bench(110,360) and the
   1154 held-out poses), the motion clips' frames (Raise-overhead peak frames are where stopb80 loses follow), the
   1432-pose workspace grid for the continuity flood, and the per-pose knock-out list of the frozen wear (fold / slide /
   contact by pose, with the metal-skin minimum) - not the round-10 judge's fast table.
3. **Methods and tools.** pick1's verified harness unchanged (docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py,
   phys 1: q2 dowel stop, closed-form K opening, kit J1-J3 margin in every state, capK 6, near-touch); the judge's built
   stop pricing (tools/env_polish.priced); the claim protocol (tools/env_polish.py claim fit60 bench|held = the
   minarc-bdp-remeasure harness: fit Bench(60,160) fast, freeze by __dict__ diff, wear exact, own-state margins, kinematic
   flood continuity); law-only reach on Bench(110,360) per configuration; a Latin-hypercube + CMA-ES over the catalogue's
   12 search coordinates with J2's seat SOLVED from the rest arcs (never searched directly).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, fast and exact), the frozen
   claim harness written by the judge (not by me), the independent verifier docs/concepts/verify/minarc-final-polish-verify.py
   (contact-aware continuity, knee window, held-out integrity asserts), pick1's verified 18.40 / held 22.69 as the
   same-harness control, and a red-team pose list (the frozen wear's contact / near-touch poses, written below).

## Measurement log

(filled as measured; numbers are Bench(60,160) fast in-sample unless marked frozen exact Bench(110,360))
