# The posteromedial J1 seat for the lead knuckle family (posteromedial-knuckle-3r)

2026-10-18, branch claude/exciting-albattani-94w8cp. This measures the one legal-seat cell that the 3-DOF take-bound table
(docs/research/take_bound_3dof.md) left unmeasured. The skeptic's finding F1 (docs/alignment/take_bound_3dof_skeptic.md)
names it: every "Back" row sits at bvec az 95-102 / el 62-68, which is the acromion top. No knuckle has been measured with
J1 at az < 40 or el < 55. That is the posteromedial back of the shoulder, which ruling 4 allows ("J1 seats: back of the
shoulder + acromion top only"). There, kin_ceiling.json gives a 0.994 kinematic window at bvec(-52.5, 17.5).

## Pre-registration (committed before any search)

**Model.** docs/concepts/models/posteromedial-knuckle-3r.py imports the verified lead conecut-knee-knuckle-3r unchanged:
- the same chain, O20 hubs, slipper-nose K drive and its clamps / pressure-angle rules;
- the conecut knee and the J3 own-angle dowel stop;
- the same metal and sampling (no new part, so the kit density holds as the lead's: docs/alignment/sample_density.md);
- the 5 deg fold margin in th and the near-touch rules.

What changes:
- J1 sits at bvec(az1, el1) inside the cell. Convention (tools/concept_kit.py `bvec`): az 0 posterior, 90 lateral,
  -90 medial; el 0 horizontal, + up.
- Scapula-handler rule: every cell seat passes `seat_legal()`, which is cap-nullspace-4r's `seat_ok`: az -110..135,
  el >= -20, no seat anterior of the frontal plane (u_x <= 0.20), so no front or clavicle seat.
- The J3 seat (wd, wa, b3) is free.
- J2's seat ray is re-solved from J1, J3 and the dyad arcs a1 = 37.55 + d_a1, a2 = 57.22 + d_a2 on branch br, with
  |d_a1|, |d_a2| <= 12. This is the acroant-conecut-knuckle-3r resolver, generalised.

**Seat grid (9 cells).** az1 in {-52.5, -26.25, 0} x el1 in {0, 17.5, 40}. It spans the task box (az -52.5..0, el 0..45)
and includes kin_ceiling's best seat (-52.5, 17.5).

**Protocol, per cell:**
- **Stage 0, seed (kinematic, FIT bench only).** Use Bench(60,160)'s 60 clip frames and 160 workspace poses. Rank J3 seats
  (wd 45..110 step 5, wa -180..170 step 10) by the share of fit poses with th = angle(u1, Q u3) inside the lead family's
  window [24.67, 110.99]. Skip a seat whose J2 does not resolve. Evaluate the top seat fast on both branches, with every
  other parameter at the lead's. The better near-1 gap is the CMA start. This costs 2 fast evaluations per cell.
- **Stage 1, refit.**
  - Run tools/concept_cma.py: objective = the 1 mm near-touch gap (`evaluate`), dishonest + 100, popsize 8, `--jobs 1`,
    `--budget-s 360`, seed 1, sigma 0.3.
  - 11 free parameters, with their scales: wd 6, wa 12, b3 0.1, d_a1 4, d_a2 4, lE 8, lc 4, phib 10, J3MIN 6, a1max 3,
    kK 0.3.
  - Fixed: az1 / el1 (the cell), br (from stage 0), and everything else at the lead's values.
- **Stage 2, select (FIT bench only).** Rank the cells by their best honest fit-bench near-1 gap. Keep the best cell, and
  the second if its near-1 gap is within 3 points of the best.
- **Stage 3, wear.** Use the claim protocol: CC.frozen fits on Bench(60,160) fast, freezes the drive and metal, then
  wears on Bench(110,360) EXACT. Also run the continuity flood (CC.frozen_flood, `connected_report`). Report:
  - takes, ib14, contacts;
  - plain and near-1 gaps;
  - why (fold / slide / skin / contact / j3stop), the per-part contact split, and the overhead count;
  - min th margin and the connected set.

**Kill line.** The deciding number is the frozen exact plain gap on Bench(110,360): contact = metal < 0 mm, the
leaderboard's gap.
- **> 17.5: dead for this cell.** It would not beat the 3-joint lead's 18.28 by a meaningful margin.
- **<= 15: pass.** It goes to an independent verifier, and only then is held out worn (after the freeze).
- **15-17.5: screened.** It is a 3-joint improvement candidate for the lead to verify, but not a path to 95, which needs
  13.75.

**Held-out hygiene.** No search, selection or tuning uses held-out poses. Stages 0-2 use only Bench(60,160). Stage 3
wears Bench(110,360) only for the frozen picks. Held out is worn only for a pass, after the freeze.

**Budget.** Local only, because the CPU farm is closed: `nice -n 10`, `OMP_NUM_THREADS=1`, at most 2 processes on a
shared 4-core box. The plan is 9 x 6 min of CMA (2 in parallel, about 30 min wall), plus 2 x 2 fast seed evaluations
per cell, plus 1-2 frozen exact wears and floods (about 6 min each). The time box ends 2026-10-18 ~14:29 UTC. A cell the
time box does not reach is reported as "seed only", not as measured.

## Results

(to be filled after the runs)
