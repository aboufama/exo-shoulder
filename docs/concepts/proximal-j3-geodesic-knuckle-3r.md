# proximal-j3-geodesic-knuckle-3r - J3's seat up the lateral deltoid on the 32/48 long-dyad knuckle chain

Round 13 (main track), screened 2026-10-17. A GHOST row (gate 1): the K drive's metal is not sampled.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the seat move as a change of the
   link-2 *geodesic*, not of a number: the binder (poses 117 / 127 / 129 / 139 / 316) is link 2's mid-span posterior edge
   riding over the lateral-deltoid bulge, so the right question is which J3 seat makes the J2-J3 great-circle arc pass
   *over* the bulge's crest for every binder pose while keeping hub 3 inside the band - and then re-fit what depends on
   the seat (the cuff knee, whose geometry was fit to the old hub-3 position, and the K law, whose stretched wall moves
   with a2). Also: refuse the cheap relabel - a pose moved from contact to a knee slide or the J3 stop is reported as a
   relabel, not a gain; and search on the 1 mm near-touch gap so the takes are not knife-edge (139 sat at 0.18 mm).
2. **The rawest material.** The posed skin itself (concept_bench's signed-distance field on the scanned body, exact path
   for Bench(110,360)), the motion clips and workspace poses as the bench samples them, the per-pose metal-skin minima of
   every member (binder table: which member, how deep, on which pose), the envsel independent draw (360 fresh workspace
   poses) - not the digested round summaries.
3. **Methods and tools.** The real long-dyad model (desmo-vrocker-longdyad-knuckle-3r.py, loaded unchanged, IB_GHOST=all)
   with wd / wa / knee / K-law free; a coarse seeded scan then CMA-ES on Bench(60,160) fast on the 1 mm near-touch
   objective; frozen-shape wear on Bench(110,360) exact (the claim protocol) and on envsel; the continuity flood
   (K slaved, no jump > 10 deg) and the th-margin read (>= 5 deg in th).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py) is the judge; the frozen exact
   wear on Bench(110,360) and the independent envsel draw are out-of-sample checks; the red-team pose list (binder
   117 / 127 / 129 / 139 / 316 / 264 / 237, overhead >= 140, every new loss) with per-pose depths; the round's adversarial
   verifier and the alignment auditor re-measure. Nothing here is a claim until gate 2 places drive metal on 32/48.

## The morphology

scapula handler (base at the J1 hub ring, outside the count) -> **J1** ACTIVE (O20, pick3's acromion-top seat bvec(95.3,
67.7)) -> link 1a (bk1 32) -> **K** PASSIVE (O20 knuckle, slaved to th by the K drive) -> link 1b (bk2 48) -> **J2** ACTIVE
(O20, posterolateral cap bvec(46.4, 41.6)) -> link 2 (3 mm Ti bar, 8 mm wide) -> **J3** ACTIVE (O20, seat wd ~72 deg from the
humeral shaft, wa ~ -9.7) -> member 3 / E strap -> two-pin knee (MR63ZZ pairs at stk 6.0, outside the count) -> arm pad on
BOTTOM. 3 ACTIVE DOF, 0 passive translations, passive rotations: K (slaved) + 2 knee pins (+ the drive's pivot in gate 2).

Change vs the round-12 best long-dyad ghost (desmo-vrocker g0_s14c56k24, frozen exact 17.23): J3's seat moves up the J1-J3
geodesic's arm end (wd 66.07 -> 71.9-73), hub 3 sits higher on the lateral deltoid and link 2 shortens (a2 58.3 -> ~55),
lifting link 2's mid-span posterior edge off the lateral-deltoid bulge (the round-12 binder 117 / 127 / 129 / 139 / 316).

## Model (docs/concepts/models/proximal-j3-geodesic-knuckle-3r.py)

* Loads desmo-vrocker-longdyad-knuckle-3r.py UNCHANGED (-> spiral-lobe -> inband-rssr -> longstroke-slipper ...), every
  member's metal, closure, knee, J2 stops, slaved K law and the claim protocol (`frozen`: fit Bench(60,160) fast, shape
  frozen, worn on Bench(110,360) exact) are the parents'. IB_GHOST=all: **the K drive's metal is not sampled** (a GHOST).
* Free: wd, wa, b3 (J3 seat / tilt); lE, lc, phiE, phib, ang_min (the knee) at **stk 6.0** (MR63ZZ build rule; the round-12
  seed had pick3's 4.85); smhi, kK, kcap (the K law, allowed because the seats moved); l2v = link 2's 8 mm bar offset
  across its great circle (+-2 mm on the O20 hub faces; the posterior-edge column).
* Search objective: the 1 mm near-touch gap (LS_OBJ=near1), dishonest +100.
* Reproduction: the base cell reads fit 12.17 (dump 12.17) - the parent loads exactly.

## Search (Bench(60,160) fast, local, 2 niced processes; the farm window had closed)

| phase | configs | best near1 (fit) | where |
|---|---|---|---|
| unrefit seats (wd 69-77 x wa -22..-6, knee at stk 6.0) | 20 | 13.39 (wd 75) | wd 73 unrefit: plain 11.69, near1 14.00 (min metal 0.32 mm) |
| knee re-fit at wd 73 (LHS 36) | 36 | **11.44** (lE 89.8, lc 28.5, phib -62.1, ang_min 22.3) | knee re-fit buys 2.6 near-touch points |
| wrap region wd 74-78 / wa -22..-12 + K-law re-tune (LHS 32) | 32 | 13.87 (wd 74.9, wa -12.3) | the wrap seat stays worse even with the law free |
| full 12-D box (LHS 32) | 32 | 13.92 | |
| CMA-ES (pop 14, 18 generations, 12 params) from the best | 252 | **9.31** (k266) | converged: wd 71.5-72.5, wa -9.7, lE 84-90, lc 22-26, phib -56..-61, ang_min 22.3-23, smhi ~14, kK 2.2-2.36, kcap ~57, l2v ~0 |

Convergence gate (372 tries, score points): gain over the 2nd half 0.40 (< 1), over the last third 0.33 (< 0.5), top-5
spread 0.40 (< 3) -> **converged**. The bar offset l2v never moved off 0 (+-0.3): the posterior-edge column is closed.
