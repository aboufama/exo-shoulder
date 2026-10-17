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

### The mechanism (unchanged from pick1 except the knuckle and the seats)

scapula handler -> J1 (ACTIVE R, O20, bvec(az1, el1), sensed) -> link 1a (12 x 3 Ti strap, arc bk1) -> K (O20 bearing pair,
SENSED = active under the 2026-10-17 ruling; 0.3 x 5 mm EN 1.4310 clock spring preloaded onto stop A, cap +6 mm; stop B
dowel at dK_B) -> link 1b (arc bk2) -> J2 (ACTIVE R, O20; dowel-in-slot stops on its OWN angle q2 at smhi / smlo deg of
J1-J3 margin, built +0.5) -> link 2 -> J3 (ACTIVE R, O20, wdir(wd, wa), tilt b3) -> member 3 -> pin knee (2 PASSIVE
iglidur pins, closed by the cuff, unsensed = 0 complexity) -> arm pad / cuff -> BOTTOM. 4 active, 2 passive rotations,
0 passive translations, no gears / pulleys / cables, cx 32.5 (v2). Every pose is determined: inside [th_lo, th_hi] K sits
on stop A (the chain is a rigid 3R), past th_hi J2 sits on its stretched stop and K opens to the unique smallest rotation
that closes the chain (closed form) - no coordinate is left to sag (R17 as pick1: the spring holds K on stop A upright).

Model: `docs/concepts/models/skinnormal-shortk-knuckle-4r.py` imports pick1's verified harness
(`minarc-stop-knuckle-4r-kitrule.py`, phys 1, kitrule 1, m3e 1, near 1, capK 6) UNCHANGED, and adds (a) the catalogue's
search coordinates - rest arcs a1 / a2 with J2's seat SOLVED by a 2-D Newton on the design's own arcs (residual < 1e-5 deg),
dK_B -> a1max on the K dyad - (b) the judge's built-stop pricing (tools/env_polish.priced) before every number, and (c) the
K-dyad repair below. Round-trip check: the three seeds re-entered through (a1, a2, dK_B) reproduce the judge's priced
fast numbers to the digit (12.49 / 12.83 / 16.14).

### Spec corrections (measured)

- **The skinnormal seed is dead at the verifier's reading as specified.** Its stop B (a1max 65.35, priced 64.95) lies
  inside the K dyad's margin read at CB_FOLD_MARGIN 5.5: bk1 + bk2 - 5.5 = 64.85 < 64.95, so KRDesign.k_ok is False and
  EVERY pose is refused (gap 275; the claim's fit crashes on an empty pose set). The judge reproduced 12.49 at the default
  margin 5.0, where the dyad still has 0.4 deg. Repair: stop B drawn 0.1 deg earlier (a1max 64.84, dK_B 75.84 -> 75.40);
  fast 12.49 unchanged at both margins. The model now caps a1max <= bk1 + bk2 - 5.5 for every configuration.
- **earlystop's az2 = el2 = 42.70 is not a copy slip**: KRDesign gives rest arcs 40.78 / 59.45 = the proposer's 40.8 / 59.4.
- **The near-touch hypothesis is refuted as the main fast-to-frozen leak** (below): the leak is the fold on the 360-pose bench.

### Step 1 - the seeds, frozen exact Bench(110,360) (fit Bench(60,160) fast, priced, CB_FOLD_MARGIN 5.5)

Protocol: `CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/env_polish.py claim fit60 bench <seed>.json OUT.json` (the judge's
minarc-bdp-remeasure harness: freeze by __dict__ diff, wear exact, own-state margins, kinematic flood continuity on the
1432-pose grid). Run locally, one process (the farm batch was refused by this session's permission policy).

| config | fast gap (priced) | law-only reach 360 | frozen gap | score | near1 | reach | overhead | follow | ib14 | contact | lost fold / slide / contact | min metal mm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pick1 (control, verified) | 15.94 near1 | 0.806 | **18.40** | 93.31 | 23.36 | 0.750 | - | 1.0 | 0.894 | 0.028 | 70 / 9 / 11 | 0.56 |
| skinnormal (repaired) | 12.49 | 0.794 | **18.58** | 93.24 | 20.20 | 0.742 | 8/28 | 1.0 | 0.893 | 0.021 | 74 / 11 / 8 | 0.002 |
| stopb80 | 12.83 | 0.836 | **19.10** | 93.05 | 23.93 | 0.761 | 6/28 | 0.955 | 0.896 | 0.048 | 59 / 13 / 19 | 0.34 |
| earlystop | 16.14 | 0.831 | **19.15** | 93.04 | 22.87 | 0.753 | 6/28 | 1.0 | 0.894 | 0.038 | 61 / 13 / 15 | 0.22 |

Every seed is >= pick1's 18.40: the lead's kill rule for the route fires. The judge's calibrations: near1 + 2.46 predicted
14.9 / 15.3 (wrong by 3.7-3.8), plain + 6.83 predicted 19.3 / 19.7 (right within 0.6-0.7). skinnormal does what it was
picked for - near-touch 20.20 vs pick1 23.36, contact poses 8 vs 11 - but loses 4 more poses to the fold.

### Where the frozen points go (law-only attribution on Bench(110,360), KRDesign.ik of the priced design)

- The frozen reach is the law-only reach minus a near-constant leak: pick1 0.806 -> 0.750 (-20 poses), skinnormal
  0.794 -> 0.742 (-19), stopb80 0.836 -> 0.761 (-27). The leak is knee slide (9-13) + contact (8-19), mostly envelope
  poses the 160-pose fit never shows; the law-only reach (cheap: 1.5 s) is the ceiling and the ranking key.
- **The folded side is never rescued by K**: on every seed and pick1, 0 workspace poses are taken in the folded state
  (J2 on its folded stop); 18-22 poses at th 7-30 deg are lost whatever K does (a two-way centred K spring, dKm 10-30,
  takes 0 extra poses). Only |a1 - a2| (+ smlo) moves that wall.
- **The stretched wall is a1max + a2 - 5.5** (the effective dyad with K fully open): skinnormal's 52 stretched losses
  start at th 119.1 (wall 64.84 + 58.64 - 5.5 = 117.98), stopb80's 41 at th 127.3 (wall 75.5 + 57.43 - 5.5 = 127.43);
  moving stop B to the K-dyad limit rescues
  0 / 5 poses. The poses run to th 175: the effective-dyad wall can never pass 174.5 deg.
