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
