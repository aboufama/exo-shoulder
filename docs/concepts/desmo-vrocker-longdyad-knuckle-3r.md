# desmo-vrocker-longdyad-knuckle-3r (round 12, pick 4)

Desmo V-rocker long dyad. The pinned-horn slot (nose on link 1a, swept slot in the crank tip) drives a lengthened 32/48
K dyad on a steep linear law (kK 2.5). Stage 1 is a desmodromic conjugate cam: two open rim lobes stacked on hub 2's cap
ring ride two crowned pins on a V short arm of the crank. There is no spring, roller, rod or ball link. 3 active DOF
(J1, J2, J3), K slaved and never read, 0 passive translations.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Kill the row cheaply before drawing the
   drive. Every reach gain on this row comes from the long dyad opening K further on the stretched poses. The round-12
   judge and the spiral-lobe row measured where that opening goes on the same chain (34/48): hub 2 and link 2 swing
   into the bunched posterior deltoid. So the first job is the chain's own ceiling on 32/48 with no drive metal at all,
   the judge's gate 3, run on the claim bench (frozen, exact). The conjugate lobes, the V arm and the slotted plate can
   only add metal. A designer would also treat the stroke cap (kcap) as a free cut: the conjugate pair's stroke is a
   stop-B position, and a lower cap turns K-open contact poses into plain fold losses. They would read the per-pose
   table, not a sum: which poses each extra degree of K buys, and which part enters the skin there.
2. **The rawest material.** The posed skin, through concept_bench's exact signed distance per pose (CB_EXACT=1,
   Bench(110,360)), and each part's metal (M.rigid, M.contact, M.link_pts) placed in that pose's frame. Also the
   workspace pose list (plane / elev / axial) and the clip frames. The per-pose dump (g0_<tag>.json: K, th, taken /
   contact / slide / fold, part and depth) is the data the cap and onset are chosen from. The digested counts (fold 64,
   contact 14) are not.
3. **The methods and tools.** The real chain model: spiral-lobe-longdyad-knuckle-3r.py, loaded unchanged (it loads
   inband-rssr-knuckle-3r.py unchanged), switched to 32/48, stop B 74.5 and kK 2.5. The RSSR does not exist in this
   morphology, so its metal is deleted and its range limiter is replaced by the V-rocker's stroke,
   dK_lim = min(kcap, 78.5). The frozen protocol: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360)
   exact. A per-pose attribution harness: signed distance per part per pose. The farm is at its budget line ($24.19
   against $24.40 at 16:22 UTC), so everything runs locally, with at most 2 niced processes.
4. **What, other than me, shows the number is right.** The bench's exact path on the frozen shape. The judge's own
   control cells: spiral-lobe's 34/48 ghost (18.84 seed, 17.86 best) and pick3's ghost (18.32), run through the same
   harness. The judge's law-only count at 32/48 (278-282 workspace poses taken by the law alone; envsel 276-278). Then
   the adversarial verifier and the alignment auditor, and the red-team pose list: contact poses by part and depth,
   the K-open takes, and the overhead cone (elev >= 140).
