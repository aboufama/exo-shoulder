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

### Amendments (2026-10-18 ~13:08 UTC, before any CMA; stage-0 probes only)

The first stage-0 probes, at cell (-52.5, 17.5), forced four changes. Each is stated with the measurement that forced it.

1. **The rest pose sits at the lead's rest th (83.23 +- 4 deg).**
   - Why: the seed as registered put the top window-share J3 seat (wd 80 / wa -140) at rest th 26.7. That puts the
     dyad's rest configuration at the other end of its window, so the K drive's phase is wrong. The drive went idle:
     crank pressure angle 86.8 deg at rest against the 38 gate, dK_lim 0, fast 375 dishonest.
   - With the lead's rest th, the dyad and its K drive phase are the lead's. Only where the chain sits on the body
     changes, which is what this cell measures.
2. **J2's seat lies on the shoulder's skin: r2 <= 120 mm from GH.**
   - Why: OSN.seat marches each ray in from 260 mm. At these J1 seats, many J2 rays return r2 = 260, which means the
     ray runs into the trunk and there is no buildable hub-2 seat. Each (J3 seat, branch) pair is a separate candidate.
3. **A numerical snap, not a physics change.** The knuckle base asserts |c[0]|, |c[1]| < 1e-6 mm (J1 and J2 on GH rays).
   At these seats the rest IK leaves c[1] at about 4e-6 mm. Offsets under 1e-3 mm are set to exactly 0; larger ones
   still trip the assertion.
4. **Compute.** A fast evaluation takes 30 s to over 4 min at these seats, against 4 s at the lead's seat. The box is
   shared (load 9-16) and the geometry is slow: long links and hubs deep in the skin. Nine 6-minute CMAs would get
   about 5-10 evaluations each, which is not a refit. So:
   - Stage 0 runs on all 9 cells, with one fast evaluation of each cell's best seed.
   - Stage 1 (the CMA) runs only on the best 1-2 cells by stage-0 near-1 gap, honest seeds first, with the remaining
     budget (`--budget-s` up to 900).
   - Every cell's stage-0 number and its loss attribution is reported.

5. **(~13:27 UTC, after stage 0 and before any CMA) The drive phase is free, and so is a lateral-J3 variant.**
   - Why the drive is freed: stage 0 put the K drive's crank pressure angle at 75-87 deg at rest in 9 of 10 seeds
     (gate 38). That holds even with the lead's dyad, rest th and drive parameters, so the drive is the first wall.
     With it idle, the window collapses to state A and fold takes 56-164 of the 220 fit poses.
   - So the CMA also frees the drive phase inside the lead's clamps: beta (-180..-150), g (1.8-3.0), r_c (14.5-19.5)
     and lift (0-4). Scales: beta 6, g 0.25, r_c 1.5, lift 0.8. The full free set: wd 6, wa 12, d_a1 4, d_a2 4, beta 6,
     g 0.25, r_c 1.5, lift 0.8, lE 8, lc 4, phib 10, J3MIN 6.
   - Run settings: popsize 8, sigma 0.3, `--budget-s 1200`, seed 1.
   - Lateral-J3 variant (`PM_WA_MAX=90`, tag `_lat`): the J3 seat is limited to the lateral half of the arm,
     |wa| <= 90, as the lead's is (wa -10.7). Why: the best window-share J3 seats at these J1 seats are on the medial
     upper arm (wa 140-180), against the trunk and axilla.
   - Stage-1 cells, by stage-0 near-1 (no seed was honest): (-26.25, 40)_lat 294.04 and (0, 40)_lat 315.18.

## Results

(to be filled after the runs)
