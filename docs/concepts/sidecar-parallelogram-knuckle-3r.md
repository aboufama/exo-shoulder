# sidecar-parallelogram-knuckle-3r

Round 8, pick 1. The sidecar parallelogram K drive: a lateral horn on link 1a, a bell crank on link 1b, and an O3 rod
on two M2 ball links beside link 1b at strap level. It sits on the verified lead's chain, which is unchanged
(frontload-lobe-stopb-knuckle-3r: J1 on the acromion top, link 1a, K knuckle, link 1b, J2, link 2, J3, pin knee + cuff).
Only the K drive is rebuilt, and nothing crosses K's crown.

Model: `docs/concepts/models/sidecar-parallelogram-knuckle-3r.py`. Sweep: `docs/concepts/sweeps/sidecar-parallelogram-knuckle-3r.json`.
Row: `docs/concepts/rows/sidecar-parallelogram-knuckle-3r.json`. Preview: `docs/concepts/viz/concepts/sidecar-parallelogram-knuckle-3r.js`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Not model the drive twice. Pick 4 (sidecar-longdyad) already built this exact drive on the lead's module: the
     per-pose RSSR closure, the honest crank stack, and the drive-range truncation. It also carries pick 1's cell as its
     control D. Two hand-built copies of one four-bar would disagree on metal and nobody would know which is right. So
     this row imports that core and adds only what pick 1 owns:
     - the lead's K dyad held unchanged (bk1 30.05 / bk2 37.57 / a1max 61.72);
     - the far-socket clearance rule;
     - a real ball-link envelope, with the all-metal fallback measured as its own cell;
     - the idle-drive rule.
   - Read the pressure-angle cap before seeding. tan pa = kK r_h / (i_rock r_lobe), so the judge's seed (kK 2.0 at
     r_h 15 / La 18 / s_arm 5 / r_lobe 7.5) is infeasible at t = 0. At r_h 15.5 it is 1.15 > 1. The cap there is
     kK <= 1.74.
   - Price the ball link as a catalogue part, not a sketch.
     - The RC-class M2 ball link is a steel ball O4.8 on an M2 stud in an acetal socket ~O7 x 7.
     - The all-metal GE4E-class spherical plain bearing (4 x 12 x 5) in a 1.5 mm eye has a socket radius of 7.5. Its
       horn must then sit at r_h >= HUB_R + 7.5 + 2 = 19.5, or the eye cuts hub K.
     - That changes the drive's gain and its in-band height, so it is measured, not assumed.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance grids per pose, via `tools/concept_bench.py`.
   - The model's own per-pose K state (dK), th, m3e and msub.
   - The per-part minimum metal-to-skin distance over the taken poses.
   - The motion clips are used only through the bench's fit-clip frames. The held-out clips stay held out until the
     claim.
3. **Methods and tools.**
   - Per-pose spatial RSSR closure (phi grid + continuation). The rod and crank are separate bodies, members 8 and 9.
   - The drive-range truncation: transmission >= 30 deg, rod / crank >= 1 mm off hub 2 and link 1b.
   - A coarse LHS of 128 drive geometries on the farm at the D seats, with kK set to 0.75-1.0 of the pressure cap.
   - CMA-ES on the near-touch gap (`tools/concept_cma.py`, farm): 3 runs with the RC ends from three seeds (D's,
     the judge's and A1's), plus 1 run with the GE4E ends.
   - The frozen wear on Bench(110,360) exact, held out, and the continuity flood fill.
4. **What, other than me, shows the number is right.**
   - The bench (Bench(60,160) fast for the search, Bench(110,360) exact for the frozen claim).
   - The round's adversarial verifier, which re-runs the frozen claim.
   - A same-harness replication. Through this wrapper, pick 4's control D re-evaluates to 10.63 fast, identical to
     pick 4's own number.
   - A red-team pose list: the overhead poses, the poses with metal under 1 mm, and the drive-range end.

## Model (what this row adds to the shared sidecar core, and where the spec was wrong)

The mechanism code is pick 4's `SCModel`, imported unchanged from `sidecar-longdyad-knuckle-3r.py`. It covers:

- the per-pose RSSR closure, with the rod and crank as members 8 and 9;
- the crank boss stacked on link 1b + 0.15;
- the drive-range truncation;
- every part pair at 1 mm.

This file adds four things:

- **`chain='lead'`.** The lead's K dyad is held at bk1 30.05 / bk2 37.57 / a1max 61.72, the spec's "lead chain
  unchanged". Pick 4's control D let the dyad float (it walked to bk2 34.6).
- **Socket floor.** r_h >= HUB_R + ER + 2: 1 mm of clearance plus 1 mm of catalogue tolerance between the horn's
  ball-link socket and hub K's housing.
  - RC ends: 15.5. The measured ROD-hubK clearance is 2.0 mm in every taken pose.
  - GE4E ends: 19.5.
- **`ends`.**
  - `rc`: an RC-class M2 ball link, steel ball O4.8 on an M2 stud with an acetal socket O7 x 7. ER 3.5, ZB 3.0.
  - `ge4e`: the all-metal fallback, a GE4E spherical plain bearing 4 x 12 x 5 in a 1.5 mm eye. ER 7.5, ZB 5.0.
  - The vendor part number of the RC link is still open; the CAD step catalogues it.
- **Idle-drive rule.** A configuration that takes no stretched pose, or carries < 30 deg of K over its taken poses,
  is dishonest (+100 in the CMA).

Where the spec was wrong (measured):

1. **The judge's seed kK 2.0 is pressure-infeasible from t = 0.**
   - tan pa = kK r_h / (i_rock r_lobe) = 2.0 x 15.5 / (3.6 x 7.5) = 1.15, so the law never starts. The gate gives
     73.88, with 0 stretched poses (idle).
   - The cap at the seed is kK <= 1.74. Across the 209 CMA ties, kK is 1.22-1.67 and i_rock 3.19-4.24. At the claim
     config the transmission is >= 55.7 deg and the real ratio dphi/ddK is 0.99-1.04.
2. **r_h 14.5 has zero clearance margin, so this row floors it at 15.5.** The coarse sweep says smaller r_h is better
   (corr +0.55 with the gap), and the CMA sits on the floor (15.5) in all 209 ties.
3. **beta -125..-95 is not where the optimum sits.**
   - The coarse best is at -83. The 209 CMA ties sit at -97.4..-91.7, at or past the upper end of the judge's
     range.
   - Moving the horn toward the rising skin (-110..-125) lifts the rod off link 1b's side and costs in-band.
4. **The rod rides OVER the crank arm, so the arm joggles down to link 1b's level (zr 0) wherever it clears the
   strap.**
   - The horn sits on link 1a's own layer: hl 3.15, at the clamp in all 209 ties, and the coarse sweep's strongest
     lever (corr -0.67). zr is 0-0.59.
   - So the drive's floor is the crank stack + ball height. Crank in-band is 0.89, the rod 0.88-0.89, the ends 0.94.

## Gate (Bench(60,160) fast, near-touch gap = the search objective; the lead's frozen seats unless stated)

| cell | near-touch | plain | reach | in-band14 | min metal | note |
|---|---|---|---|---|---|---|
| judge seed (r_h 15.5, beta -110, hl 3.15, zr 1.5, La 18, s_arm 5, r_lobe 7.5, kK 2.0) | 73.88 | 63.35 | 0.425 | 0.950 | 0.42 | law infeasible at t = 0 (pressure), drive idle |
| same, kK 1.7 (cap 1.74) | **18.30** | 13.95 | 0.769 | 0.897 | 0.42 | **kill bar 14.0 near-touch: fails untuned** |
| same, kK 1.55 | 18.75 | 14.41 | 0.763 | 0.899 | 0.42 | |
| pick 4's control D, chain free (bk2 34.6), through this wrapper | 10.63 | 10.63 | 0.794 | 0.901 | 1.11 | replicates pick 4's 10.63 exactly |
| control D's drive + seats on the lead dyad | 21.88 | 10.64 | 0.794 | 0.900 | 0.34 | the lead dyad parks metal < 1 mm until re-tuned |
| control D on the lead dyad, GE4E ends (r_h 19.5, La 21.5, kK 1.8) | 89.57 | 61.58 | 0.638 | 0.895 | 0.16 | the 19.5 horn drops into the skin: contact 0.20 |

The kill gate as written fails. Untuned, the per-pose placement at the lead's seats costs 18.30 near-touch against
the proposer's 11.88. Three things make up the difference:

- the honest crank stack;
- the 15.5 socket floor;
- 0.42 mm metal at the horn's skin side.

The plain gap (13.95) passes. I went on because the near-touch loss is a placement problem the search can fix. Pick
4's control D (10.63 near = plain) already showed that. The CMA confirms it on the held lead dyad (below).

## Search (farm; Bench(60,160) fast; near-touch objective)

**Coarse LHS.** 128 drive geometries at D's seats on the lead dyad, kK at 0.75-1.0 of the pressure cap.

- Best 11.25: r_h 16.2, beta -83, La 17.4, s_arm 4.35, hl 2.73, zr 1.0, r_lobe 7.07, kK 1.32.
- Median 40.0. 13 configurations are under 20.
- Levers, by correlation with the gap: hl -0.67, r_h +0.55, r_lobe +0.19, beta -0.13. La, s_arm, zr and kK are
  ~0.
- Worn frozen, the coarse best gives 20.52 plain (near-touch 23.26 / 56.73 at 2 mm).
- With the drive-range truncation switched off, the frozen wear is identical (attribution only). The drive's own
  range (dK_lim 38.5, ROD-hub2) costs 0 poses. The law ends at the lobe skirt first.

**CMA-ES.** popsize 8, 1250 s each, 3828 configurations in all.

| run | seed | ends | evals | best fast (near = plain) | gate (gain 2nd half / last third / top-5 spread, score pts) |
|---|---|---|---|---|---|
| P1 | control D's drive + seats | rc | 841 | **10.63** | 0.00 / 0.00 / 0.00 |
| P2 | judge seed (kK 1.7) at the lead's seats | rc | 1065 | 11.25 | 0.16 / 0.05 / 0.00 |
| P3 | pick 4's A1 drive + seats | rc | 857 | **10.63** | 0.00 / 0.00 / 0.00 |
| G1 | control D, GE4E ends, r_h 19.5 | ge4e | 1065 | 17.45 | 0.85 / 0.43 / 0.18 |

The convergence gate passes on every run: < 1 point over the second half, < 0.5 over the last third, top 5 within 3.

- **The fit-bench optimum is a plateau.** 209 configurations in P1 and P3 tie at 10.63. That is reach 127/160 =
  0.794, quantised at 0.625 gap points per pose, with in-band >= 0.90, contact 0 and metal >= 1 mm. The whole fast
  gap is the reach term, i.e. the fold. The drive has nothing left to buy on this bench.
- **Claim config.** The tie-break was declared before any frozen wear: max fit in-band14. It picks P3 #626.
  - kK 1.349 (linear, per-t gated), r_h 15.5, beta -95.83, La 14.90, s_arm 4.40 (i_rock 3.39), hl 3.15, zr 0.0,
    r_lobe 7.06;
  - smhi 19.35, smlo 5.0;
  - seats az1 97.88, el1 67.01, az2 40.89, el2 44.75, wd 69.96, wa -10.53, b3 0.370;
  - ang_min 24.79, lc 28.83, phib -59.08, with the lead's dyad.
- **Drive at the claim config.**
  - transmission >= 55.7 deg over the taken range;
  - real ratio 0.99-1.04 against a small-angle ratio of 1.04;
  - exact crest 9.85 mm, inside the 11.5 skirt;
  - rod 25.4 mm, crank swing 36.3 deg;
  - dK taken <= 35.9 of the drive's own 41.0 (rod vs hub 2), so stop B goes there;
  - K slop from 0.05 mm of ball-link play: 0.05 / 15.5 rad = 0.18 deg.
- **The all-metal GE4E ends cost 6.8 fast points (17.45 vs 10.63).** The 19.5 mm horn and the 12 mm eyes sit high
  and wide. Reach 0.731 and contact 0.017 at the best.
