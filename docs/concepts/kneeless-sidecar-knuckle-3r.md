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

### Is the knee really idle? Yes, exactly

At b3 0 the knee angle range over every bench pose is 0.000 deg and the drift is 0.000 mm (the model refuses a pose
past 0.5 mm / 0.5 deg; none is refused). The bracket bend at the best configuration is 128.6 deg, in hub 3's plane.

### Numbers

Each score is 100 (1 - gap / 275). Frozen means: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact.

| configuration | fast plain | fast 2 mm | frozen plain | frozen 1 mm | frozen 2 mm | reach | ib14 | contact | overhead | lost (fold / parts / contact) |
|---|---|---|---|---|---|---|---|---|---|---|
| seed: lead seats, b3 0, wd 75 / wa -7 | 17.27 | 40.49 | 22.68 | 27.02 | 47.67 | 0.719 | 0.878 | 0.024 | 7/28 | 90 / 2 / 9 |
| CMA A: 8 shape vars, 745 evals | 17.38 | 20.24 | 24.24 | 27.35 | 37.61 | 0.719 | 0.859 | 0.021 | 6/28 | 88 / 5 / 8 |
| **CMA B: + J1 seats + drive, 1585 evals (best)** | **15.63** | **20.32** | **21.11 (92.32)** | **22.75** | **33.15** | 0.714 | 0.888 | 0.013 | 8/28 | 90 / 8 / 5 |
| lead sidecar-longdyad (verified, cx 49) | 10.30 | - | 18.91 (93.12) | 20.00 | 34.03 | 0.725 | 0.897 | 0.011 | 8/28 | 86 / 2+7 slide / 4 |

More checks on the best configuration (B):

- **Held out:** 25.34. Reach 0.684, overhead 17/71. Lost: fold 263, parts (E-L2) 17, contact 21. Min metal 0.02 mm.
  The lead scores 22.67 held out.
- **Continuity flood fill:** full 21.11 (0 dropped), knn 23.65 (9 dropped), bench grid 44.84. The lead's figures are
  18.91, 21.72 and 43.4.
- **Fold margin:** min th margin over the taken poses is 5.01 deg (kit rule, as the lead). a1 / a2 are 36.4 / 56.6.
- **Drive:** the RSSR's transmission is >= 45.5 deg over the taken range. The drive range ends at dK 38.5 (rod vs
  hub 2), which is the stroke wall of the lead.
- **Search:** the 161-point LHS was best at 25.91 (2 mm). CMA A converged at 20.24 and CMA B at 20.32 (2 mm objective).
- **Gate, in score points:** B gains 0.37 over the 2nd half and 0.11 over the last third, top-5 spread 0.07. A gives
  0 / 0 / 0.03. Both runs are **converged**.
- **The spec's 20-min gate is NOT met.** Fast plain is 15.63 (gate 12.5) and 2 mm is 20.32 (gate 14.5). Contact is
  0.026 (gate 0.012). Hub 3 in band is 0.551 (gate 0.60). Workspace in-band is 0.809 / 0.740 (gate 0.874 / 0.841).
  Follow (1.0) and the RSSR transmission pass.

### Where it loses (red team, Bench(60,160) at B; frozen numbers in the row)

- **Rest** (elevation < 30): 58 of 58 poses taken, min metal 2.1 mm.
- **Overhead** (elevation >= 140): 6 of 17 taken. Lost: fold 8, skin 3. The contact poses are the drive (crank, rod,
  rod ends, horn, hub K, hub 2) at plane 0-15, elevation 135-150. **The bracket never touches the skin.**
- **Across the body** (plane >= 100): 38 of 50, lost to fold 12. The lowest metal of all is here: 0.32 mm at plane 135
  / elevation 135 / axial -45.
- **Behind the back** (plane <= -20): 27 of 30, lost to fold 3.
- **Extreme axial** (|axial| >= 120): 7 of 25, lost to fold 18.
- **New parts loss: E-L2.** The bracket's E leg runs at the 0.15 mm adjacent gap to link 2 at J3. It costs 8 frozen and
  17 held-out poses, and **zero on the fit bench**, so the search could not see it. This is the fit-bench sampling
  lesson again; an envelope-bench search (tools/env_bench.py) is the fix to try next.
- **The 2 mm objective parks metal at 2.05 mm** on many taken poses, and it lowers workspace in-band (0.809 overall,
  0.740 at elevation 90-140, both unscored). This is the round's L2 gaming watch: the gap does not see it.

### GH-offset red team (the bench cannot see it)

The chain turns about its own centre and the arm about the true head centre, offset by d. The rigid bracket then
misfits the cuff by |(I - R) d|, where R is the arm's rotation from the donning pose. Taken fit-bench poses, worst of
26 directions of d (worst along scapula -x):

| \|d\| | misfit p95 / max (mm) | left after ONE slide along the humerus, p95 | what a planar knee in this hub 3's plane would leave, p95 |
|---|---|---|---|
| 3 mm | 4.8 / 5.1 | 4.7 | 4.1 |
| 5 mm | 8.1 / 8.6 | 7.9 | 6.9 |
| 10 mm | 16.1 / 17.1 | 15.8 | 13.8 |

What the table shows:

- A slide along the arm buys almost nothing (0.1-0.3 mm at p95), so the optional slide is not worth it.
- The knee would only have absorbed 15-20 %: the misfit at the cuff lies mostly along hub 3's axis, which the knee's
  plane cannot take. So the knee's off-bench job was small. A GH offset is a cost of any rigid-centre 3R, with or
  without the knee.
- At 3 mm (healthy humeral-head translation, 1-3 mm) the liner takes up to ~5 mm. That is beyond the 3 mm that
  CLAUDE.md allows as liner compliance. At a 5-10 mm scapula-handler tracking error, the cuff would fight the arm
  with or without the knee.
- The real fix is upstream: the handler's GH estimate.

### Verdict

**Screened: a Pareto point, not a lead change.**

- Frozen 21.11 (score 92.32) at complexity 28 (hand count; the catalogue estimated 27). The lead is 18.91 at 49.
- It lies between minarc pick1 (18.40, cx 33) and H1 (27.20, cx 19.5).
- At 2 mm it beats the lead (33.15 vs 34.03), but plain it is 2.20 worse, so it fails the A1 dominance gate.
- Held out it is 2.67 worse than the lead (25.34 vs 22.67).
- The prediction was "frozen ~21-24 at cx 27", and 21.11 lands at the good end.

**Next levers (measured):**

1. Search on the envelope bench, so that E-L2 is visible: about 8 frozen poses, ~2.2 points.
2. Give the E leg a 1-2 mm joggle under link 2's J3 stack (a real bent-bar feature): this goes after the same 8 poses.
3. Hub 3's obliquity at the GH-ray seat (0.555 in band) is the structural cost of the kneeless class.
4. The fold wall (drive stroke, ROD-hub2 at dK 38.5) is unchanged from the lead.
