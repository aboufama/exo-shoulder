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

All numbers below are fit-bench (Bench(60,160) fast) numbers unless marked; the gap counts contact as metal < 0 mm
(plain) and the near-1 objective counts metal < 1 mm as contact. Files: docs/research/posteromedial_seat/
(stage0_*.json, cma_*.json, frozen_*.json, the drivers stage0.py / stage1.sh / summarize.py).

### 1. Kinematics first: the lead's dyad gains at most 3 % of window at these seats (fit bench, 220 poses)

Share of the fit bench's 220 poses (60 clip frames + 160 workspace) whose th = angle(u1, Q u3) lies in a window, best J3
seat over wd 45-110 x all wa (ray approximation, no metal). "Lead window" = the lead family's own window [24.67, 110.99]
(a1 37.55 / a2 57.22 / a1max 58.77); "any window" = the best window of the same width 86.3 placed at any lo (a different
dyad: kin_ceiling's 0.994 is this column).

| J1 seat (az, el) | lead window, best J3 | any window of width 86.3 |
|---|---|---|
| lead (95.4, 67.9), acromion top | 0.914 | 0.927 |
| (-52.5, 17.5) | 0.932 | 1.000 |
| (-26.25, 17.5) | 0.932 | 1.000 |
| (0, 17.5) | 0.909 | 0.982 |
| (-52.5, 40) | 0.927 | 1.000 |
| (-26.25, 40) | 0.914 | 0.991 |
| (0, 40) | 0.877 | 0.964 |
| (-52.5, 0) | 0.945 | 1.000 |
| (-26.25, 0) | 0.936 | 0.995 |
| (0, 0) | 0.895 | 0.977 |

- The 0.99-1.00 that made this cell interesting (kin_ceiling.json `curves`) needs the window at lo ~87-92: J1 and J3
  ~90-170 deg apart, a dyad with a1 + a2 ~177 (e.g. arcs ~130 / ~45). That is not the lead's knuckle (a1 37.55, a2 57.22,
  a1max 58.77; this model allows +-12 deg on each arc). With the lead's dyad the posteromedial seats buy at most +0.03
  (0.914 -> 0.945) over the acromion top.
- The J3 seats that reach those shares sit on the MEDIAL upper arm (wa 140-180, wd 95-110), against the trunk and axilla.
  With J3 held to the lateral half of the arm (|wa| <= 90, as the lead's wa -10.7) and the lead's rest th, the share
  falls to 0.57-0.78 (stage-0 seeds below) against the lead's 0.855 at its own seat (same ray reading).

### 2. Seat radius: J1's skin is 1.4-4x farther from GH than on the acromion

OSN.seat (the J1 ray from GH to 2 mm off the rest skin): the lead's J1 seat is 42.0 mm from GH (J2 51.6). The cell's J1
seats: (0, 40) 59.5, (0, 17.5) 65.9, (0, 0) 75.1, (-26.25, 40) 75.4, (-26.25, 17.5) 90.9, (-26.25, 0) 98.9,
(-52.5, 40) 111.6, (-52.5, 17.5) 149.8, (-52.5, 0) 167.4 mm. The concentric knuckle puts every hub on a GH ray, so the hubs
and links ride 1.4-4x farther out over a back that is not a sphere about GH: many J2 rays at these J1 seats run into the
trunk (r2 = 260, the march limit; amendment 2 drops them).

### 3. Stage 0: every seed of every cell is dishonest (the K drive's pressure angle), 254-375 fast

One fast evaluation per seed (lead's dyad, rest th, drive, knee and stop; J3 seat from the seed). why = fold / slide / skin
/ parts / contact over the 220 fit poses. Drive: dK_lim (deg) / crank pressure angle at the taken poses (gate 38).

| cell (az, el) | seed | J3 wd / wa / branch | share | r1 / r2 (mm) | near-1 / plain | reach | ib14 | contact | why: fold / slide / skin / parts / contact | drive dK_lim / crank PA |
|---|---|---|---|---|---|---|---|---|---|---|
| (-26.25, 0) | best share | 110 / -20 / +1 | 0.5955 | 98.9 / 66.3 | invalid: rest IK 2.7 deg off-ray (hub-2 offset 3.1 mm) | - | - | - | - | - |
| (-26.25, 17.5) | best share | 100 / -180 / -1 | 0.8636 | 90.9 / 84.8 | 371.87 / 371.87 | 0.0063 | 0.0 | 0.975 | 67 / 109 / 39 / 0 / 0 | 0.0 / 80.6 |
| (-26.25, 40) | best share | 95 / -180 / -1 | 0.8909 | 75.4 / 57.8 | 366.75 / 366.75 | 0.0187 | 0.0 | 0.9362 | 53 / 119 / 43 / 1 / 1 | 0.0 / 77.6 |
| (-26.25, 40) | lateral J3 | 110 / 0 / +1 | 0.7 | 75.4 / 49.6 | 294.04 / 294.04 | 0.0063 | 0.6791 | 0.9091 | 158 / 0 / 30 / 28 / 0 | 0.0 / 80.3 |
| (-26.25, 40) | lateral J3, br -1 pick | 110 / 0 / -1 | 0.7 | 75.4 / 59.4 | 254.02 / 254.02 | 0.1187 | 0.6534 | 0.629 | 158 / 0 / 38 / 0 / 1 | 0.0 / 87.2 |
| (-52.5, 0) | best share | 110 / -50 / +1 | 0.6364 | 167.4 / 99.2 | 375.0 / 375.0 | 0.0 | 0.0 | 1.0 | 162 / 0 / 51 / 2 / 0 | 0.0 / 87.2 |
| (-52.5, 17.5) | best share | 110 / -40 / +1 | 0.6455 | 149.8 / 68.4 | 372.29 / 372.29 | 0.0063 | 0.0 | 0.9792 | 164 / 0 / 47 / 2 / 0 | 0.0 / 86.6 |
| (-52.5, 17.5) | lateral J3, br -1 pick | 110 / -40 / -1 | 0.6455 | 149.8 / 87.0 | 375.0 / 375.0 | 0.0 | 0.0 | 1.0 | 164 / 0 / 52 / 4 / 0 | 0.0 / 88.2 |
| (-52.5, 40) | best share | 100 / 150 / -1 | 0.8909 | 111.6 / 52.0 | 366.25 / 366.25 | 0.025 | 0.0 | 0.9375 | 73 / 76 / 60 / 0 / 0 | 0.0 / 82.6 |
| (-52.5, 40) | lateral J3 | 110 / -30 / +1 | 0.6409 | 111.6 / 52.3 | 367.36 / 367.36 | 0.0187 | 0.0 | 0.9423 | 165 / 0 / 49 / 3 / 0 | 0.0 / 80.3 |
| (-52.5, 40) | lateral J3, br -1 pick | 110 / -30 / -1 | 0.6409 | 111.6 / 76.2 | 335.91 / 333.47 | 0.1062 | 0.0 | 0.6909 | 165 / 0 / 38 / 0 / 0 | 0.0 / 88.0 |
| (0, 0) | best share | 110 / -160 / -1 | 0.8091 | 75.1 / 68.4 | 375.0 / 375.0 | 0.0 | 0.0 | 1.0 | 56 / 122 / 25 / 8 / 0 | 0.0 / 86.4 |
| (0, 0) | lateral J3, br -1 pick | 105 / 10 / -1 | 0.5727 | 75.1 / 69.4 | invalid: rest IK 7.4 deg off-ray (hub-2 offset 8.9 mm) | - | - | - | - | - |
| (0, 17.5) | best share | 105 / -160 / +1 | 0.8318 | 65.9 / 111.8 | 321.41 / 311.11 | 0.0688 | 0.2456 | 0.7255 | 92 / 0 / 19 / 54 / 18 | 0.0 / 87.1 |
| (0, 17.5) | lateral J3 | 110 / 10 / +1 | 0.6636 | 65.9 / 51.4 | 367.08 / 367.08 | 0.0125 | 0.0 | 0.9333 | 150 / 0 / 28 / 32 / 0 | 0.0 / 80.7 |
| (0, 17.5) | lateral J3, br -1 pick | 110 / 10 / -1 | 0.6636 | 65.9 / 64.1 | 289.35 / 262.09 | 0.0187 | 0.752 | 0.7083 | 150 / 0 / 10 / 46 / 7 | 0.0 / 86.7 |
| (0, 40) | best share | 110 / -170 / +1 | 0.8455 | 59.5 / 113.1 | 375.0 / 375.0 | 0.0 | 0.0 | 1.0 | 88 / 28 / 95 / 8 / 0 | 50.5 / 36.4 |
| (0, 40) | lateral J3 | 110 / 20 / +1 | 0.7773 | 59.5 / 47.5 | 315.18 / 315.18 | 0.0187 | 0.3007 | 0.7879 | 144 / 0 / 26 / 37 / 0 | 0.0 / 75.1 |
| (0, 40) | lateral J3, br -1 pick | 110 / 20 / -1 | 0.7773 | 59.5 / 57.9 | 300.7 / 296.84 | 0.025 | 0.334 | 0.6774 | 144 / 0 / 19 / 45 / 2 | 0.0 / 86.6 |

- **The K drive is the first wall.** 16 of the 17 valid seeds have dK_lim 0: the slipper-nose crank's pressure angle is
  75-88 deg at rest (gate 38), so K cannot open, the window collapses to state A [24.67, 89.77] and fold takes 53-165 of
  the 220 poses. The drive is built in mm on a sphere about GH (the crank pivot sits (HUB_R + 6) / f2 rad beside hub 2,
  the lug and nose on link 1b's fitted level), so the same parts at a new seat are a different spherical mechanism. The
  acromion-top re-seat already showed it: the drive fails beyond +6 deg of J1 azimuth (acroant-conecut-knuckle-3r row).
  The one seed with a working drive ((0, 40), medial J3) takes nothing: 95 of 220 poses in the skin (hub 3 / link 2 on
  the medial arm), 88 fold, 28 knee slide.
- **Metal second.** Where poses close, the arm-side metal floats: (0, 17.5) medial J3 has hub 2, hub 3, link 2, E strap,
  knee, pad and boss at 0.0 in band with medians 31-58 mm off the skin (stage0_az0_el17.5.json `parts`); skin and part
  collisions take 10-95 poses per seed.
- Two seeds are not buildable designs: the rest-pose IK lands 2.7 / 7.4 deg off J2's seat ray (hub-2 offset 3.1 / 8.9 mm,
  real, above the snap), so the knuckle base refuses them ((-26.25, 0) best share; (0, 0) lateral br -1).

### 4. Stage 1: CMA with the drive phase free (amendment 5)

STAGE1_TEXT

### 5. Stage 3: frozen exact wear

STAGE3_TEXT

## Conclusion

CONCLUSION_TEXT
