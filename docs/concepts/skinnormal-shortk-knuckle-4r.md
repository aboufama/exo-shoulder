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

### Step 3 - the sweep inside the morphology (Bench(60,160) fast, priced, near-touch gap; local, one process)

The CPU farm batch and sweep were refused by this session's permission policy (paid compute), so every number below ran
on this box (4 shared cores, load 12-15), one configuration at a time (~25 s each incl. the law-only Bench(110,360) reach).
`docs/concepts/sweeps/skinnormal-shortk-knuckle-4r.json`, in order: 3 seeds, a 60-point Latin hypercube over the
catalogue's 12-coordinate box (half global, half +-25 % around a seed), a 16-point targeted family on the measured
stretched wall (stopb80's seats; bk1 32 / 35, bk2 52 / 56, dK_B 80 / 82, a2 58.5 / 60.5), then CMA-ES (popsize 8, unit box,
sigma 0.12) from the best. Every entry also carries `kin360` (the law-only reach on Bench(110,360), the frozen ceiling).

Frozen exact claims of sweep picks (same protocol as Step 1):

| config | what | fast gap | law-only 360 | frozen gap | score | near1 | reach | overhead | follow | ib14 | contact | lost fold / slide / contact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8 | LHS, long bk1 36 / short bk2 40, a1 40.7 | 15.53 | 0.822 | 18.88 | 93.13 | 23.69 | 0.744 | 8/28 | 1.0 | 0.904 | 0.033 | 64 / 15 / 13 |
| k20 | LHS, its neighbour | 16.04 | 0.825 | 21.05 | 92.35 | 25.40 | 0.739 | 7/28 | 1.0 | 0.894 | 0.043 | 63 / 14 / 17 |
| k33 | wall family: stopb80 + dK_B 82 + a2 58.5 | 12.18 | 0.847 | **18.61** | 93.23 | 23.36 | **0.769** | 6/28 | 0.9455 | 0.897 | 0.0475 | 55 / 15 / 19 |
| k56 | wall family: bk1 35 / bk2 56, dK_B 82, a2 58.5 | 13.57 | 0.861 | 19.72 | 92.83 | 26.76 | 0.767 | 6/28 | 0.9455 | 0.901 | 0.059 | 50 / 16 / 24 |

(k22, an LHS point with law-only reach 0.803, was dropped from the claim queue as dominated on the ceiling.)

**Hybrid check** (the variant that should remove the limiter: skinnormal's low-contact seats + the wall family's long
knuckle bk2 52 / dK_B 82): fast 14.89-18.15 (in-band 0.861-0.893, contact 0.037-0.042, follow 0.95), and two of the four
lose the chain (gap 68.6 / 375): the long knuckle does not transplant onto the lead's J1 seat (hub K leaves the skin it
parks on). Not claimed.

### Convergence gate (binding; score = 100 (1 - gap / 275), Bench(60,160) fast, 123 configurations in order)

Best 12.18 (score 95.57, k33). Gain over the second half 0.00, over the last third 0.00, top-5 spread 0.16 points: the
gate PASSES on the protocol's objective. The CMA-ES stream (40 tries from k33, sigma 0.12 -> 0.093) found nothing better
than 12.40. Caveat measured above: the fast objective no longer ranks this class - the six frozen claims span fast 12.18-16.14
but land at frozen 18.58-21.05 with no order kept (k33 fast-best -> 18.61; skinnormal fast 12.49 -> 18.58; k8 fast 15.53 ->
18.88). A sweep on the frozen objective (~6 min per config here, ~1 min on the farm) is what would settle the class; it
did not fit the time box without the farm.

### The measured limiter: a 1:1 fold-for-contact exchange in the K-open states

On the frozen 360-pose bench every pose the knuckle wins back from the stretched wall is paid in contact (and the
stopb80 seats also pay follow): skinnormal 74 fold / 8 contact (reach 0.742) -> stopb80 59 / 19 (0.761) -> k33 55 / 19
(0.769) -> k56 50 / 24 (0.767). Reach rises 0.742 -> 0.769 (+10 poses, +2.8 points) while contact rises 0.021 -> 0.048
(+2.7 points) and follow drops under 0.95 (+0.45): the net is flat at 18.6 +- 0.03. The forced (K-open) states put metal
into the skin on the extreme envelope poses the fit never saw; skinnormal's short knuckle buys margin (near1 20.20, the
best near-touch of the class: pick1 23.36) by never opening far enough to reach them.
Overhead (elev >= 140, frozen): 6-8 of 28 for every config - the knuckle does not open the overhead set.

### Red team of the best frozen config (skinnormal, repaired)

- **The near-touch pose**: metal 0.002 mm from the skin at workspace (plane 135, elev 30, axial -150) - across the body,
  arm low, full external rotation - and 0.66 mm at (150, 30, -150), 0.87 mm at (60, 75, -120): plain counts them taken,
  near1 counts them contact (near1 20.20 vs plain 18.58). The Raise-overhead peak clip frames (30, 150, -60) sit at
  1.02 mm - one more 0.1 mm of fit error and the daily clip loses follow, as stopb80 does.
- **The forced J1 swing**: 126 of 377 taken poses are in the stretched state (K open up to 73.3 deg of 75.4); the
  lowest own-state J1-J3 margin is 5.895 deg at (150, 90, -90) - 0.4 deg above the 5.5 priced reading.
- **The jam**: the folded state is never taken (0 poses) - the folded-side J2 stop is a hard wall, so a clip that drives
  th under 30.2 deg stops the arm instead of opening K (22 workspace poses on the 360 bench).
- **Clearances**: hub K's cap (18.25 mm stack) clears the skin by 1.82 mm minimum; nearest part pair 1.76 mm
  (link 1b vs the K cap); q2 slot 99.8 deg, used -5.23 .. 93.20, nothing forced off a stop.
- **Optimistic numbers in this record**: every fast number (in-sample on the 160 fit poses). The held-out wear and the
  per-part contact attribution (docs/concepts/verify/minarc-pick1-redteam.py attr, 1154 poses exact) are listed below
  only where they finished inside the time box.

### Held out (1154 poses never used: fit Bench(60,160) fast, worn exact, same harness)

| config | held gap | score | near1 | reach | overhead | follow | ib14 | ib10 | contact | lost fold / slide / contact | min own margin |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pick1 (control, verified) | 22.69 | 91.75 | 26.73 | 0.720 | - | 1.0 | 0.892 | 0.563 | 0.038 | 209 / 23 / 35 | - |
| skinnormal (repaired) | **22.43** | 91.84 | **25.45** | 0.711 | 18/71 | 1.0 | 0.891 | 0.568 | **0.027** | 221 / 30 / 24 | 5.589 |

skinnormal ties pick1: +0.18 on the bench, -0.26 held out, near-touch -3.16 / -1.28, contact poses 8 / 24 vs 11 / 35. It
does what it was picked for (margin) and nothing more: the fold losses it adds (+4 bench, +12 held) eat the contact it saves.

## Verdict

**Killed by the lead's rule (every seed and every sweep pick >= pick1's 18.40 frozen); the sweep's gate passed.** Best
frozen: the repaired skinnormal seed, **18.58 on Bench(110,360) exact frozen (score 93.24), held out 22.43, near1 20.20**,
reach 0.742 (overhead 8/28), follow 1.0, ib14 0.893, ib10 0.570, contact 0.021, min th margin 5.90 (bench) / 5.59 (held),
0 islands in the continuity flood. Best frozen reach: k33 0.769 (= the 95-point reach target) at contact 0.048 and follow
0.9455 -> 18.61. It is a 4-joint design (4 active, cx 32.5 vs the lead's 24.25), level with pick1 within 0.3 points, so it
cannot earn its 4th joint; it is never the 3-joint lead (roller-longdyad 18.67 with 3 active).

## New knowledge (predicts beyond this morphology)

1. **The fast bench has stopped ranking the 4R class.** Six frozen claims: fast 12.18-16.14 -> frozen 18.58-21.05 with
   the order scrambled. The law-only reach on Bench(110,360) (1.5 s per config) bounds frozen reach from above (frozen =
   law-only - 19..28 poses); the leak grows with how far K opens. Any further 4R search must score frozen or use a
   K-open-aware contact proxy; CMA on Bench(60,160) will polish noise.
2. **Fold-for-contact is 1:1 in the K-open (stretched) states**: each extra pose the knuckle reaches past the 3R wall
   costs ~one contact pose on the envelope (skinnormal -> stopb80 -> k33 -> k56). The knuckle moves the stretched wall to
   th = a1max + a2 - 5.5 (measured on every config) but the metal it swings there is in the skin.
3. **The folded state never takes a workspace pose** in this layout (all seeds, pick1, a two-way centred K spring
   included): the folded-side wall th_lo = |a1 - a2| + smlo is a 3R wall the knuckle cannot move.
4. **A K stop B within 5.5 deg of the K dyad's stretch (a1max > bk1 + bk2 - 5.5) refuses every pose at the verifier's
   reading** while it scores normally at the default 5.0 - fast reproductions at margin 5.0 miss it. The model caps it.

## Files

- model `docs/concepts/models/skinnormal-shortk-knuckle-4r.py` (`python3 ... '<json>'`, `... viz '<json>'`)
- sweep `docs/concepts/sweeps/skinnormal-shortk-knuckle-4r.json` (123 configs, in order, with kin360)
- frozen claims `docs/concepts/verify/skinnormal-shortk-knuckle-4r/c_*_fit60_{bench,held}.json` (+ `_params.json` = the
  priced design worn, `_conn.json` = the continuity flood), nominal inputs `seed_*.json`, `cand_k*.json`
- preview `docs/concepts/viz/concepts/skinnormal-shortk-knuckle-4r.js` (the repaired skinnormal seed; test.mjs: 239 / 239
  frames close, 207 in range, residual 0.0004 mm)

Not run inside the time box (the CPU farm batch was refused by the permission policy; everything ran locally): the
independent verifier docs/concepts/verify/minarc-final-polish-verify.py (contact-aware continuity, knee window) and the
per-part held-out contact attribution (minarc-pick1-redteam.py attr); the R17 hold with the thorax tilted; the
workspace in-band at elev 90-140.

## Audit (2026-10-17 ~06:05 UTC, independent re-measure): the death STANDS

The design is level with pick1 and with the 3-joint lead, and far ahead of the 3R champion (68.93). It gets there only by
adding a 4th active joint, so it is not a lead.

- **Convergence gate** (re-computed from the sweep file, 123 configurations in order, Bench(60,160) fast): the best
  gained 0.00 score points over the second half and 0.00 over the last third; the top-5 spread is 0.16. It has converged on
  the fast objective. The agent's caveat holds: fast does not rank this class. The 7 frozen claims run 18.58-21.05 and the
  order is scrambled. The 5 lowest-contact frozen picks sit within 0.57 of each other (18.58-19.15).
- **Ranges**: a1 35-42, a2 56-61, bk1 28-37.7, bk2 37.4-56, dK_B 56-82, smhi 7-16, smlo 5.1-8.9, az1 94-106,
  el1 65-69. The box is tight around the lead's seats by design, because the lens moves only the knuckle. The fast-best
  k33 sits on dK_B 82 (the upper bound), but the frozen claims at longer K opening (stopb80, k56) only trade fold for
  contact. The only missed direction is long bk2; the fold probe below covers it.
- **Modelling check (fold probe, `verify/skinnormal-shortk-knuckle-4r/audit_kwin.py`, kinematic only)**: the claim that
  the folded state takes 0 poses is correct, and the reason is exact. With J2 locked on its folded q2 stop, the forced
  sub-chain J1-K-J3 sits at its own fold. The smallest J1-J3 angle K can reach with every kit margin >= 5.5 is
  |bk1 - cK| + 5.5, where cK is the arc from K to J3 through the locked J2. For the seed that is 32.8 deg against
  th_lo 29.7, turning either way, so a two-way spring cannot help. It falls below th_lo only for long bk2 (bk1 29.65 /
  bk2 56: 23.1 deg; stretched one-way 123.5). That is the same direction that swings the K metal into the skin
  (k56: contact 0.059, near1 26.76). This is geometry, not a bug. No convention error was found either: the model
  imports pick1's verified kitrule harness unchanged, and the stop-B repair (a1max <= bk1 + bk2 - 5.5) is the verifier's
  own rule.
- **Re-measured** (claim harness `tools/env_polish.py claim fit60 bench`, CB_EXACT=1, CB_FOLD_MARGIN 5.5, local, one
  process; log `verify/skinnormal-shortk-knuckle-4r/audit_skinnormal_r_fit60_bench.json`):

| config | frozen gap (score) | near-touch 1 mm | reach | follow | ib14 | ib10 | contact | min metal | active / cx |
|---|---|---|---|---|---|---|---|---|---|
| skinnormal (repaired), audit | **18.58** (93.24) | 20.20 | 0.742 | 1.000 | 0.893 | 0.570 | 0.021 | 0.002 mm | 4 / 32.5 |
| skinnormal (repaired), agent | 18.58 | 20.20 | 0.742 | 1.000 | 0.893 | 0.570 | 0.021 | 0.002 mm | 4 / 32.5 |
| pick1 (same harness, cited, not re-run) | 18.40 | 23.36 | 0.750 | - | - | - | - | - | 4 / - |
| 3-joint lead roller-longdyad (cited) | 18.67 | 20.30 | 0.725 | 1.000 | 0.894 | 0.513 | 0.005 | 0.07 mm | 3 / 24.25 |

States taken: A 251, stretched 126, folded 0. Islands 0, minimum own-state th margin 5.90. Held out (agent's, not re-run):
22.43 (pick1 22.69, lead 23.73).

Measured reason in one line: reproduced at 18.58 frozen, level within 0.3 with pick1 (18.40) and the 3-joint lead
(18.67) but at 4 active joints. Every stretched pose K wins costs about one contact pose, and the folded wall is the
K sub-chain's own fold |bk1 - cK| + 5.5, so a 4th joint buys nothing here. Next, if anyone reopens the folded wall:
the probe says K must sit where cK ~ bk1 at the folded stop without a long bk2. That is
a different morphology and is not measured here.
