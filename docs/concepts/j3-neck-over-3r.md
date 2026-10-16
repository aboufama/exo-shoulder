# j3-neck-over-3r - the inverted J3 stack, screened as the J3 side of the knuckle chain

Round-6 lens 3 (j3-side-band). Standalone, this morphology is a complexity-0 spherical 3R inside the verified zc ceiling
(31.04; the GPU search covered all four J2 / J3 stack orders), so the lead asked to screen it ONLY as the J3 side of
minarc variant A (plain spherical chain + spring knuckle K in link 1, complexity 13.5), whose in-band loss sits on the
J3 side alone: link 2 0.43, hub 3 0.70 (F 101 mm), neck 0.68.

Model: `docs/concepts/models/j3-neck-over-3r.py` (variant A kit rule `minarc-stop-knuckle-4r-a-kitrule.py` loaded
unchanged; only `build()` changes the J3 stack order, `lay` 1 = neck over link 2, `lay` 0 = variant A's order as the
control). Sweep: `docs/concepts/sweeps/j3-neck-over-3r.json`. Row: `docs/concepts/rows/j3-neck-over-3r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Ask first WHY the J3 side is out of band before choosing a stack order. A stack order only moves 3.15 mm of
     metal between link 2 and the neck where they cross; it cannot fix a hub whose plate sits tilted on the arm.
     So: decompose hub 3's level into its per-pose requirement (median vs worst pose) and measure the plate's
     obliquity on the arm skin, then decide which lever can act.
   - Run the stack order as a paired control at identical seats and metal (lay 0 vs lay 1), so the stack's gain is
     measured, not assumed (the rail-elbow lesson).
   - Search the stack order TOGETHER with the J3 seat, because the seat sets hub 3's level and link 2's path
     (the lead's lens: deltoid-crest seats, q, neck width), and keep the knuckle's reach in the same objective
     (near-touch gap) so that band is never bought by giving the fold back.
2. **Rawest material.** The posed skin itself (the bench's signed-distance grids: the fast cache on Bench(60,160),
   the exact libigl path on Bench(110,360)), the fit motion clips and the workspace pose grid; the per-pose,
   per-sample march requirement of hub 3, link 2 and the neck (`K.requirement`), not the digested in-band
   fractions. Held-out clips never loaded.
3. **Methods and tools.** The kit (K1 closure, K2 dense continuity on J1 / K / J2 / J3, K3 march, K4 flat O20 hubs,
   K5 straps with 60-deg climb, K6 collisions, K7 neck) through minarc variant A's kit-rule model (stops in the J1-J3
   metric at >= 5 deg, physical q2 stop, hub K's +6 mm clock-spring cap, near-touch objective); a Latin-hypercube
   coarse sweep and CMA-ES streams (tools/concept_cma.py) on the cloud CPU farm; the frozen protocol (fit
   Bench(60,160) fast, wear Bench(110,360) exact) with the continuity flood fill.
4. **What, other than me, shows the number is right.** The bench report (honest flag, audit), the paired lay-0 control
   at the same seats, the frozen Bench(110,360) exact wear, the red-team pose list (the poses that set hub 3's level,
   the nearest-metal poses, overhead / across-body / behind-back), and the next stage's independent verifier.

## The mechanism

- **Chain.** Scapula handler -> J1 (O20, active, axis on a GH ray; the base rides the J1 hub ring directly) -> link 1a
  (12 x 3 Ti strap) -> **K** (O20, passive, clock spring in a cap 6 mm taller than the stack, stops A / B as a dowel in
  an arc slot) -> link 1b -> J2 (O20, active, a dowel-in-slot stop on its own angle q2) -> link 2 -> J3 (O20, active,
  humerus-fixed axis through GH) -> member 3 -> BOTTOM -> cuff. All four axes pass through GH. 0 passive translations,
  1 passive rotation (K), no gear / cable / pulley.
- **The min-arc law** (variant A kit rule, unchanged): while th = angle(J1, J3) stays inside [thLo, thHi] (both stops
  >= 5 deg from the J1-J3 fold, design variables smlo / smhi) K rests on stop A and the chain is a rigid spherical 3R;
  past it J2 locks on its q2 stop and the arm opens K to the smallest J1-J2 arc that closes (<= stop B and <= K's own
  span b1 + b2 - 5). Every state keeps >= 5 deg of fold margin (effective dyad, forced sub-chain J1-K-J3, K's range).
- **The one change: the J3 stack order.** At hub 3, link 2 is the LOWER (face) member [F, F+3] and member 3 (cap plate
  + K7 neck, 14 x 6 or narrower) the UPPER member at F + 3.15; the neck bridges >= 1 mm over every place link 2 (and link
  1a / 1b) ever passes under it before dropping to BOTTOM. Variant A had the opposite order (link 2 over the neck).
  No part is added or removed: the bearing pair, shaft and housing of hub 3 are the same; only which member is pressed on
  the shaft and which is bolted to the housing swaps.
- **Complexity** (tools/simplicity.py): 13.5, identical to variant A (1 passive rotation, 1 sensed passive, 1 spring,
  +1 body, +1 joint). K is sensed: under the user's counting rule (a passive coordinate that must be read to know the
  arm pose is ACTIVE) the skeptic counts this chain as 4 active, as for minarc. A determined K (round-6 lens 1) would
  make it 3 active; the J3 side measured here does not depend on how K is determined.

## Measured (Bench(60,160) fast, kit checks, near-touch objective; plain gap in brackets)

### Why the J3 side is out of band - the raw requirement, before any search

At variant A's kit-rule best LA1 (J3 wdir(46.2, -6.2)):
- **hub 3's level is set by its median pose, not by a worst pose**: the per-pose march requirement of the hub-3 disc is
  p50 100 / p90 105 / max 108 mm, fitted level F 105 mm. Nothing a stack order does can move it.
- **The cause is obliquity.** The J3 axis passes through GH but meets the arm skin 39 deg off the local skin normal
  (p10 / p50 / p90 34.7 / 39.0 / 42.7 deg, from the signed-distance gradient under the hub). An O20 disc tilted by
  theta spans 20 tan(theta) mm of height: 16 mm at 39 deg against the 12 mm band, so a third of the disc is out of band
  whatever its level (measured 0.64). Link 2 ramps into hub 3's face at 105 mm and the neck starts at its cap: the
  whole J3 side rides at 100-112 mm from GH.
- **Obliquity law (measured on three seats):** hub 3 in band 0.64 / 0.69 / 0.82 at obliquity 39 / 30 / 16 deg
  (J3 wdir 46 / 70 / 91). On a cylindrical arm a GH ray at d deg from the shaft meets the skin ~(90 - d) deg off its
  normal; the deltoid adds ~10 deg at d 60-75. A flat O20 hub is fully in band only at obliquity <= ~25-30 deg, i.e.
  J3 wd >= ~75-80 (the deltoid crest), which is where the knuckle chain loses reach (below).
- **The annulus crossing.** Link 2 rotates about J3 relative to the arm; the neck is arm-fixed. At LA1 link 2's
  leaving azimuth (relative to the neck's) spans -177..179 deg over taken poses, largest free sector 60 deg, and 4.8 %
  of poses put link 2 within +-30 deg of the neck. A rigid neck over link 2 must clear it in every fit pose, so those
  4.8 % lift the neck's first ~30 mm; the stack order only decides which member pays.

### The paired stack control (same seats, same metal)

| seats | lay 1 (neck over link 2) | lay 0 (variant A's order) | link 2 in band (1 / 0) | neck in band (1 / 0) | in-band14 (1 / 0) |
|---|---|---|---|---|---|
| LA1 (variant A kit-rule best, wd 46) | 31.30 (29.09) | **30.03** (28.92) | 0.27 / 0.25 | 0.34 / 0.53 | 0.704 / 0.705 |
| C5 (this search's best, wd 58) | **24.99** (24.99) | 33.18 (32.04) | 0.63 / 0.41 | 0.78 / 0.85 | 0.840 / 0.784 |

- Over the 280 random LHS configurations the inverted stack lifts link 2 from 0.10 to 0.40 (median) and costs the neck
  0.78 -> 0.71: the J3-side mean rises 0.51 -> 0.56.
- **The stack order is worth -1.3 points at LA1 and +8.2 at C5.** It pays where link 2 rarely sweeps under the neck's
  exit: at C5 the crossing share falls to 1.6 % (free sector 90 deg), so the neck is lifted on few samples while link 2
  drops 18 mm at hub 3 (level max 109 -> 91 mm).

### The search (cloud CPU farm, near-touch objective, 13 coordinates: seats az / el / wd / wa, arcs a1 / a2 / b1 / b2, stop B a1max, J2 stop margins smhi / smlo, underside quantile q, neck width nw; lay fixed per stream)

- **Coarse:** 289 configurations (Latin hypercube, wd 38-100, 70 % lay 1, plus the LA1 and crest anchors), 54 s on
  the farm. Best new: lay 1 at wd 69.8 (near 39.86 / plain 30.66, in-band 0.828, reach 0.69). Binned by the J3 seat,
  reach falls and the J3-side band rises with wd: reach p50 0.766 / 0.756 / 0.756 / 0.750 / 0.725 / 0.700 and J3-side
  in-band p90 0.54 / 0.63 / 0.71 / 0.73 / 0.74 / 0.80 for wd 38-50 / 50-60 / 60-70 / 70-80 / 80-90 / 90-100.
- **CMA round 1** (6 streams, popsize 8, 900 s each, 6526 tries): C1 / C2 from LA1 (lay 1, sigma 0.3 / 0.6): 28.56 /
  27.64; C3 from the LHS wd-70 best: 26.44; **C4 = the lay-0 control** from the same start: 31.98; C5 from the LHS
  wd-48 runner-up: **24.99** (plain 24.99, reach 0.763, in-band 0.840); C6 from the best crest seat (wd 91): 26.26
  (plain 22.87, reach 0.80).
- **CMA round 2** (4 streams from the round-1 bests, sigma 0.2-0.25, 600 s, 2540 tries): D1 (from C5) no gain;
  **D2 (from C6): 23.96** (plain 22.80; reach 0.788, follow 0.95, in-band 0.821, contact 0.037); D3 (from C3) 26.32;
  **D4 = the lay-0 control CMA'd from C5's seats: 30.16** (the stack order is worth 5.2 near-touch points after both
  orders are re-optimised from the same seats).
- **Convergence gate** (score points; 1 point = 2.75 gap): every round-2 stream passes on its own (D1 0.00 / 0.00 /
  0.31, D2 0.28 / 0.00 / 0.13, D3 0.00 / 0.00 / 0.09, D4 0.12 / 0.05 / 0.01 = gain over the second half / over the last
  third / top-5 spread); the C6 -> D2 lineage read as one history (1530 tries) gains 0.84 over its second half and 0.53 over its last third
  (0.03 over the 0.5 bar, the restart at sigma 0.2 inside it); D2 alone passes. **Converged** (one more short stream
  from D2 is the cheap confirmation if this row is ever claimed).

## THE NUMBER: frozen shape worn on Bench(110,360) EXACT

Protocol (lesson c): fit on Bench(60,160) fast (plain), freeze every underside / hub level, wear on Bench(110,360) with
CB_EXACT=1, K6 at 1 mm, fold margin 5 deg in every state, four O20 hubs with hub K's +6 mm spring cap; the workspace
continuity flood fill (1432-pose grid, 2-deg slerp edges, no joint step > 10 deg) applied to reach. Farm jobs, outputs
`.cache/j3n/frozen_*.json` (summarised in the row's `exact_frozen`).

| configuration | stack | fast plain / near | **frozen exact** | score | reach | follow | in-band14 | in-band10 | contact | near-touch | min metal | overhead reach |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LA1 = variant A kit-rule best (reference, its own file) | 0 | 28.92 / 30.03 | 41.14 | 85.0 | 0.778 | 1.0 | 0.706 | 0.371 | 0.095 | 44.72 | 0.26 | 0.39 |
| LA1 | 1 | 29.09 / 31.30 | 41.82 | 84.8 | 0.775 | 1.0 | 0.704 | 0.366 | 0.097 | 45.90 | 0.26 | 0.39 |
| C2 (CMA from LA1, lay 1) | 1 | 27.64 / 27.64 | 41.20 | 85.0 | 0.758 | 0.955 | 0.725 | 0.414 | 0.096 | 43.86 | 0.53 | 0.36 |
| C4 (lay-0 control stream) | 0 | 27.35 / 31.98 | 31.51 | 88.5 | 0.694 | 1.0 | 0.843 | 0.468 | 0.053 | 39.08 | 0.24 | 0.18 |
| D4 (lay-0 control CMA'd from C5's seats) | 0 | 30.16 / 30.16 | 35.60 | 87.1 | 0.714 | 1.0 | 0.792 | 0.483 | 0.061 | 40.36 | 0.08 | 0.25 |
| C5 | 1 | 24.99 / 24.99 | 30.80 | 88.8 | 0.714 | 1.0 | 0.840 | 0.473 | 0.061 | 35.07 | 0.13 | 0.25 |
| C5's seats | 0 | 32.04 / 33.18 | 35.60 | 87.1 | 0.719 | 1.0 | 0.783 | 0.461 | 0.059 | 41.67 | 0.08 | 0.21 |
| C3 | 1 | 24.10 / 26.44 | 31.72 | 88.5 | 0.656 | 0.973 | 0.877 | 0.489 | 0.050 | 35.47 | 0.33 | 0.21 |
| D2 (fast best) | 1 | 22.80 / 23.96 | 30.49 | 88.9 | 0.719 | 0.936 | 0.827 | 0.459 | 0.037 | 35.39 | 0.21 | 0.21 |
| D2's seats | 0 | 24.91 / 27.21 | 32.44 | 88.2 | 0.719 | 0.936 | 0.810 | 0.456 | 0.040 | 37.33 | 0.09 | 0.21 |
| **C6 (frozen best)** | 1 | 22.87 / 26.26 | **28.46** | **89.65** | 0.739 | 0.964 | 0.835 | 0.472 | 0.058 | 35.44 | **0.00** | 0.18 |

For reference on the same protocol: H1 (verified pin knee) 27.20, minarc BDp (verified, complexity 33, 4 active by
the counting rule) 19.06; the zero-complexity ceiling 31.04 / 33.51.

C6 = J1 bvec(101.33, 68.95), J3 wdir(68.93, -3.17), a1 35.29, a2 63.23, b1 30.02, b2 44.21, stop B a1max 71.88, J2
stops at 8.02 / 8.90 deg of J1-J3 margin (phi 32.97 / 136.87), q 0.965, neck 13.4 x 6, lay 1. Continuity: 1140 of 1143
grid nodes connected even from the strict rest seeds (K on stop A at elevation 0), 0 taken bench poses dropped.

Reading:
- **The stack order alone, at fixed seats:** -0.7 (LA1), +4.8 (C5), +1.95 (D2) frozen exact points. It pays only where
  link 2 rarely sweeps under the neck's exit (crossing share 4.8 % at LA1, 1.6 % at C5, 0.0 % at C6 / D2 with a
  90-105 deg free sector).
- **The stack order with re-optimised seats:** best lay 1 28.46 against best lay 0 31.51 (C4): ~3 frozen points.
- **The seats carry most of the gain over variant A** (41.14 -> 31.51 with lay 0 already): variant A's LA1 was tuned
  to the 160-pose sample (fast 28.92 -> frozen 41.14, reach 0.86 -> 0.78); the wd 58-71 seats generalise better
  (fast-to-frozen +5.6 at C6).
- **What it does not buy: the overhead.** Every configuration that gets the J3 side into band (in-band >= 0.82) keeps
  overhead workspace reach at 0.18-0.25 and loses the raise-overhead clip at elevation 149-150 (C6 overhead follow 0.6
  frozen, 0.4 fast; D2 0.4); the LA1 region keeps 0.36-0.39 overhead at in-band 0.70-0.73.

## Red team (my own best, C6)

1. **The point that pinches.** Frozen exact minimum metal-skin distance 0.00 mm (fast 0.65 mm: ws plane 75 / elev 90 /
   axial -120, plane 60 / elev 120 / axial -90, plane -15 / elev 75 / axial 90, all on a strap face). Near-touch gap
   35.44 against the plain 28.46: the near-touch figure, not the plain one, is what the wearer would feel. Not
   buildable as fitted without a re-fit at a stricter quantile (q 0.965 -> ~0.95 costs band).
2. **The pose that jams.** No jam or branch flip on the clips (K2 dense on J1 / K / J2 / J3; collide 0.0 fast), but
   the raise-overhead clip frames at elevation 149-150 are LOST (contact on the fast bench; overhead follow 0.6 frozen):
   the arm would push the chain into the skin there. Not-closing workspace poses sit at th 17 (folded, J1 ~ J3) and
   129-147 deg (stretched past K's own span b1 + b2 - 5 = 69.2 deg, before stop B at 71.9).
3. **The optimistic number.** Fast 22.87 -> frozen 28.46 (+5.6): the claim is the frozen figure. D2's fast 22.80 /
   23.96 looked better and lost 7.7 frozen (30.49). Variant A's own fast optimum lost 12.2.
4. **The DOF count.** K is sensed in its stretched states (35 % of the fast closing poses at C6, 317 of 1076 grid nodes
   at D2): under the user's counting rule this is 4 active, like minarc. The J3-side finding does not depend on it.
5. **Hub 3 got worse, not better.** C6's in-band gain is link 2 (0.25 -> 0.69) and the neck (0.53 -> 0.71); hub 3 fell to
   0.49 (F 81 mm, its level set by elevation-165 workspace poses where the acromion comes under it). The J3 side is
   still the in-band limiter: hub 1 / K / hub 2 / link 1 are 0.97-1.00.

## Verdict

**Screened.** The inverted J3 stack is a real, conditional lever: zero parts, worth +2 to +5 frozen exact points on the
knuckle chain where link 2's swept annulus leaves the neck a free exit sector (and -0.7 where it does not), ~3 points
after both orders are re-optimised. Searched together with the J3 seat it takes minarc variant A from 41.14 to
**28.46 frozen exact (score 89.65; fast 22.87 plain / 26.26 near-touch)** at complexity 13.5 and 0 passive
translations. It does not cross 90 on the big bench, it does not beat H1 (27.20) or minarc BDp (19.06), and it buys the
band with the overhead (overhead reach 0.18, the raise-overhead clip lost at elevation 150, metal at 0.0 mm). Not a
contender; its value is the layering rule (every knuckle chain should put the arm member on hub 3's cap when the free
sector allows) and the two laws below.

**New knowledge (predicts beyond this morphology):**
- **Hub obliquity law.** A flat O20 hub on an axis through GH is in band only if the axis meets the skin within
  ~25-30 deg of its normal (a 20 mm disc spans 20 tan(theta) mm; 12 mm band). On the arm a GH ray at d deg from the
  shaft meets the skin ~(90 - d) deg off normal (plus ~10 deg of deltoid at d 60-75): measured hub 3 in band
  0.64 / 0.69 / 0.82 at 39 / 30 / 16 deg. Any spherical chain with J3 at wd < ~70 cannot get hub 3 into band by
  layering, quantile or link routing.
- **Annulus-crossing price.** The stack order matters in proportion to the share of poses in which link 2 sweeps
  under the arm member's exit (+-30 deg): ~5 % costs the upper member ~0.2 in band over its first 30 mm; < 2 % makes
  the neck-over order strictly better. Measure the free sector before choosing the order.
- **The J3-side / overhead conflict.** On the knuckle chain, the seats that put the J3 side in band (wd 58-71) take
  overhead reach from 0.36-0.39 to 0.18-0.25, because the elevation-150-165 poses bring the acromion under hub 3 and
  hub 2; the J3 side and the overhead cannot both be bought by seat choice. The next lever is one that changes hub 3's
  geometry, not its seat: a J3 axis that does not pass through GH (offset / skin-normal J3 as in the pin knee's
  b3 tilt), which the spherical knuckle chain cannot take without a closure (the pin knee) - i.e. variant B.

**Next:** none for this row as a standalone design. Hand the layering rule to the knuckle CAD (gen-4 BDp: check link 2
vs member 3 order at hub 3 against the free sector) and to lens 1 (cam-stop-knuckle): if a determined K lands, re-run
this J3-side search with lay 1 at the C6 / C5 seats as starts.

## Verification (skeptic, 2026-10-16)

Harness: `docs/concepts/verify/j3-neck-over-3r.py` (loads the model unchanged, runs its frozen protocol on the farm,
then audits every taken pose of the wear from the built chain's joint axes alone). Results:
`docs/concepts/verify/j3-neck-over-3r_claim_big_frozen.json`, `..._nw14_big_frozen.json`.

**Verdict: VERIFIED as a number, not a contender, and 4 ACTIVE DOF.**

| C6, frozen, Bench(110,360) exact | gap | near-touch | reach | follow | ib14 | ib10 | contact | min metal | overhead reach |
|---|---|---|---|---|---|---|---|---|---|
| claim | 28.46 | 35.44 | 0.739 | 0.964 | 0.835 | 0.472 | 0.058 | 0.00 mm | 0.18 |
| re-measured (claim metal, neck 13.41 x 6) | **28.46** | 35.44 | 0.739 | 0.964 | 0.835 | 0.472 | 0.058 | 0.00 mm | 0.18 |
| K7 neck at its 14 x 6 section | 28.86 | 35.83 | 0.739 | 0.964 | 0.831 | 0.470 | 0.058 | 0.00 mm | 0.18 |
| champion 3R, same bench, frozen margin-5 protocol | 64.93 | | | | | | | | |

Champion reference: `docs/concepts/verify/minarc-skeptic/champbig_frozen_m5.json`. It measures 75.94 on the
risley-turret checks.

What the independent audit checked (395 taken poses, 254 free / 141 stretched / 0 folded):
- **Closure.** The link arcs b1 / b2 / a2 are exact, and J1 and J3 stay fixed in the scapula / humerus frames to 1e-4 deg.
- **Fold margin.** The J1-J3 margin of the effective dyad is at least 5.28 deg, so the 5-deg rule holds.
- **K.** The J1-J2 arc stays in [a1, a1max] = [35.29, 71.88] (it reaches 64.5 at most). K sits on stop A in every
  free-state pose.
- **J2 stop.** J2's own angle q2 stays inside its physical stops. The window is the arc from -78.8 to 177.3 deg that
  contains the mid value -127.3; 0 poses fall outside it.
- **Clip continuity.** 13 consecutive-frame steps exceed 25 deg on the sparse 110-frame bench. All of them track the
  arm's own rotation between the frames: steps of 25-47 deg against arm rotations of 15-46 deg, with margins of 11 deg
  or more. The kit's dense K2 (2-deg slerp) passed, so none of them is a branch flip.
- **Continuity flood fill.** 1140 of 1143 grid nodes are connected, 0 taken poses are dropped, and connected = static.
- **Honesty.** The kit honesty audit is clean.
- **Parts and stack.** All four O20 hubs are present (hub K has its +6 mm spring cap). The neck rides on hub 3's cap
  plate and is built over link 2 / link 1a / link 1b with K6 at 1 mm radial in the wear. The inverted stack adds no part.

Issues found:
1. **4 active DOF.** The row says active_dof 3, but its own verdict concedes the point. In the stretched state (141
   of 395 taken poses) J2 sits on its stop and K is off stop A, so q1 / q2 / q3 do not fix the arm and K must be
   position-measured. Under the user's DOF rule that makes it 4 ACTIVE. The R5 cap of 4 is met; R5-aim and the
   3-active brief fail. The row now carries `v_active_dof: 4`.
2. **The neck is narrower than K7.** At K7's 14 mm section the design costs 0.40 points (28.86). That is under one
   point, so it is not material.
3. **The wearer would feel it.** Metal touches skin (0.00 mm). The near-touch gap of 35.44 is the felt figure.
   Overhead reach is 0.18, and overhead follow 0.6: the raise-overhead clip is lost at elevation 149-150.

Not refuted: 28.46 beats the champion's 64.93 on the same bench by 36 points. It stays behind H1 (27.20, same
protocol) and minarc BDp (19.06), and it does not cross score 90.
