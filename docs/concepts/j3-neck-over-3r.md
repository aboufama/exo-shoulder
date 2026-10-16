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
