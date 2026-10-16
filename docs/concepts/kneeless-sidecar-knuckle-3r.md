# kneeless-sidecar-knuckle-3r

The verified lead (sidecar-longdyad-knuckle-3r, 18.91 frozen, complexity 49) with J3 put on a GH ray (b3 0) and the
two-pin knee replaced by one rigid bent 3 mm Ti bracket from hub 3's lower plate to the arm pad. The strap-level
sidecar drive that slaves K (hub-2 rim lobe -> bell crank on link 1b -> O3 rod with M2 ball links -> horn lug of
link 1a) is unchanged. 3 active (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, 0 sensed
passives. Complexity 27 (catalogue estimate; the knee costs ~22 of the lead's 49).

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Prove first that the knee carries nothing, and do not assume it. With every axis through GH, member 3's drift
     relative to the arm is identically zero. The model refuses any pose whose drift moves the bracket by more than
     0.5 mm or 0.5 deg, and reports the knee angle's range (it must stay under 0.5 deg).
   - Do not carry the knee's metal over as dead weight. With no pins, the knee plate drops from the pin-stack level
     (tr + tp + RUN) to the bracket level tr. Bracket and pad are both 3 mm plate (conservative: the lead's plate was
     2.35 mm).
   - Price what the knee absorbed off the bench: a GH offset (scapula-handler tracking error or humeral-head
     translation) makes the arm turn about a different centre than the chain does. Measure the cuff misfit
     |(I - R) d| at 3, 5 and 10 mm, and split it into three parts: what one slide along the humerus would take, what
     a planar knee in hub 3's plane would leave, and what the liner must take.
   - Treat hub 3's obliquity as the expected limiter. On a GH ray, hub 3's disc is perpendicular to the ray, not to
     the skin, so the seat (wd, wa) and the bracket's legs are where the search should act.
2. **The rawest material.** Two sources:
   - the posed skin itself, through the bench's signed-distance grids (fast) and exact libigl distances (frozen, on
     Bench(110,360));
   - the motion clips and workspace poses as HG rotations (`CB._poses_all`), which the GH-offset red team uses
     directly: the rotation from the donning pose (lowest elevation), with the humerus axis taken from the band frame.

   The proximity atlas law (a rigid part must clear the highest skin it passes over) is why hub 3's obliquity costs
   in-band.
3. **Methods and tools.**
   - The lead's verified model is loaded as its own module copy (docs/concepts/models/sidecar-longdyad-knuckle-3r.py,
     with its VModel checks, kit fold rule, capK, RSSR drive table, drive-range truncation and frozen()).
   - Only the knee rule, the bracket metal and the adjacency checks change (docs/concepts/models/kneeless-sidecar-knuckle-3r.py).
   - Search on the farm (tools/cloud_run.py batch): a 161-configuration Latin hypercube over the gate's 8 shape
     variables, plus CMA-ES (tools/concept_cma.py) on the 2 mm near-touch objective (round-9 rule). Run A uses the gate
     set; run B adds the J1 seats and the drive.
   - Frozen exact wear on Bench(110,360).
   - `ghoff` mode for the GH-offset red team.
4. **What, other than me, shows the number is right.**
   - The bench, at the lead's own code path (the judge's numbers reproduce: lead metal at b3 0, wd 75 / wa -7 gives
     18.86 fast).
   - The frozen exact wear, reported plain, at 1 mm and at 2 mm.
   - The round's verifier (docs/concepts/verify/sidecar-longdyad-knuckle-3r.py harness).
   - A red-team pose list: the overhead poses, the behind-the-back and across-the-body poses (the bracket at extreme
     internal rotation), and the rod at dK 38-43 against hub 2.

## Results

(filled in below as the runs land)
