# twist-long-a2-knuckle-3r - J3 re-seat for reach on the lead's knuckle drive

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the J3 seat as a *window-centring*
   problem, not a parameter: the fold window is `[|a1A - a2| + 5, a1max + a2 - 5]` and the overhead th set is
   `angle(J1, humerus) +- wd_eff`; so solve for the J3 axis that puts the overhead th set inside the window *first*
   (closed form per pose), then check whether hub 3 / L2 can park there. Re-parametrise the search in the designer's
   variables (effective J3 axis, a2, a1A at stop A) instead of the seat angles, so CMA moves along the lever and not
   across it (az2 / el2 are derived from `circ_int(u1, a1A, d3_rest, a2)`). Count the folded wall a longer a2 raises
   (|a1A - a2| + 5) as a cost from the start, and attribute every lost pose to its wall.
2. **Rawest material.** The posed skin itself through the bench's signed distance (grid cache / exact libigl), the
   motion clips and workspace poses of `tools/concept_bench.py` (Bench(60,160) fit, Bench(110,360) exact for the claim,
   held-out clips never touched), the rest-pose skin normal at each seat (`seat()` on the posed mesh), the proposer's
   proxy rows (scratchpad r8wg ev3_*.jsonl) only as the hypothesis to refute.
3. **Methods / tools.** The verified lead's model module (frontload-lobe-stopb-knuckle-3r.py: knuckle K, seg law,
   rod drive with the verifier's corrected cap metal, pin knee, O20 stacks, kit fold rule 5 deg, near-touch objective)
   with a seat transform; the law-only kill gate (drive metal off) through the model's own IK on Bench(110,360);
   farm LHS + CMA-ES (tools/cloud_run.py) on Bench(60,160) fast near-touch; frozen exact wear on Bench(110,360) with
   the per-cause and per-part attribution; flood fill on the worn model.
4. **What, other than me, shows the number is right.** The bench (outside judge), the frozen exact wear on
   Bench(110,360) (not the fit bench), the round's adversarial verifier re-running the claim from the row's params, and a
   red-team pose list (overhead axial -135 / 0 families, across-the-body, behind-the-back, the knee window extremes).
