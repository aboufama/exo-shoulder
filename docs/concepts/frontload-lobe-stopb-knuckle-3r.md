# frontload-lobe-stopb-knuckle-3r

Front-loaded stretched lobe + stop B at the K dyad's 5-deg margin (winner re-cut, 2:1 rocker). Round 7, pick 4.
Kill gate (round-7 judge): a re-fitted fast near-touch gap < 16.0 on Bench(60,160). The winner measures 16.53.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the rocker as a real bell crank, not a ratio. A 2:1 rocker puts the rod end on a 10 mm arm, and that arm has
     to sit at the height where the rod can reach K's horn. The rod must pass over hub K's crown: its centre has to be
     at least the crown top + 2 mm wherever it is within HUB_R + 2 of K's axis. That height fixes the arm level. The
     spec does not ask for this, and the parent model never checks rod against hub K (same body).
   - Make the arm level a design variable (`arm_lo`, the fork's underside above link 1b) and let the crown rule raise it.
     The 2:1 rocker's metal is then priced at its true height, not at a convenient one.
   - Give the law a target, not just a shape. Next to the two-segment law (`seg`), the margin-tracking law (`track`)
     opens K by the least amount that keeps the effective dyad margin m3e = a1e + a2 - th >= smt. Its gain is clipped to
     the pressure-angle cap, it never closes K, and the law ends on stop B.
   - Clamp what the catalogue clamps:
     - horn >= 2.45 mm;
     - rocker ratio 1-2.5;
     - lobe base radius 7-8.1 mm;
     - lobe crest <= HUB_R + 1.5 (the winner's crest, 11.3 mm, passed the verifier);
     - a1max <= bk1 + bk2 - 5.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance field of the posed body, metal sampled about 1 point per 4 mm2.
   - The motion clips and the workspace poses of Bench(60,160) for the fit, and Bench(110,360) exact for the frozen wear.
   - The winner's own per-part in-band numbers and lost-pose attribution, re-measured here, not copied:
     - stretched_kin;
     - why: fold / slide / contact;
     - the rocker, rod and rod-end samples.
3. **Methods and tools.**
   - The winner's verified model is loaded as its own module copy (docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py).
     Its `_ik_phys`, kit fold rule, VModel checks, capK cap, near-touch report and frozen() are reused unchanged.
   - Only `law()` and the rocker / rod metal change.
   - Searches on the farm (tools/cloud_run.py batch):
     - a 192-configuration LHS over the law, the rocker, stop B, smhi, bk1 / bk2 and the seats;
     - three CMA-ES runs (tools/concept_cma.py, popsize 16, 8 processes), one per law family: seg at i_rock about 2,
       seg at i_rock 1, and track.
   - The objective is the near-touch gap.
4. **What, other than me, shows the number is right.**
   - The bench (tools/concept_bench.py), at the same code path that reproduces the winner's 16.53 exactly with the
     control config (law_mode lin, i_rock 1).
   - The frozen exact wear on Bench(110,360), reported plain and near-touch.
   - The round's independent verifier, using the winner's harness.
   - A red-team pose list: the overhead stretched poses past the law's th_max, the rod against hub K's crown, and K's
     slop from rod-end play.

## Model

docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py. The pressure angle is a function of the law's local gain:
tan(pa) = k(t) r_horn / (i_rock r(t)), where r(t) = r_lobe + r_horn |dK| / i_rock.

Results below (filled in as they land).
