# P3 search plan: multi-objective, robust, thorax-mounted, held out

Written 2026-10-14 after P0 (docs/P0_BASE_MOUNT.md). Nothing here has run yet; this is the plan and the reasons.

## 1. What changes after P0

| belief the r13 search relied on | what P0 measured on the rig | consequence for P3 |
|---|---|---|
| the base rides the scapula | the base bolts to the thorax; the scapula frame turns up to 58 deg and the GH centre rises up to 25 mm vs the thorax | every candidate is evaluated with a **thorax-fixed base**; the base part is checked against the moving scapular skin |
| all joint axes meet at the GH centre (spherical chain) | a thorax-fixed spherical chain misaligns the GH centre by 25 mm (12.7 mm with the best fixed centre) - wider than the whole 2-10 mm band, so no surface shaping can rescue it | axes may be **offset from the GH centre**; for given axis directions the best axis points are a closed-form minimax LP (`pipeline/girdle/girdle.py`) - the search only explores directions |
| 4 DOF (4R or 3R + cuff) | 3-DOF chains with offset axes leave ~5-7 mm worst-case misalignment on the rig law (P0 section 4) | **3 DOF is the primary family** (user, 2026-10-14): (a) 2R shoulder + humeral-rotation open ring on the upper arm, (b) 3R with offset axes; the 4R reference stays as the comparison |
| any link arc is fine (r13 used 6-90 deg) | link 1 of the reference has no arm (24 deg, 1.7 mm between seats) | hard constraint `min_arc` 35 deg (search code, P3 agent change) |

## 2. Families searched

| family | DOF | decision variables | fixed by construction |
|---|---|---|---|
| A. 2R pointing shoulder (offset axes) + humeral-rotation ring | 3 | J1 direction (2), arcs a1, a2, branch; ring radius, ring arc position about the arm, ring axial station s along the humerus | J3 = humerus axis; axis points = minimax LP; links may nest (link 2 over link 1, shells concentric about J2) |
| B. 3R, offset axes | 3 | J1 direction (2), J3 arm-fixed direction (2), a1, a2, branch, link orders | axis points = minimax LP |
| C. 4R spherical (r13 family) on a thorax base | 4 | as r13 | reference only |

Stack and hardware per family come from `docs/research/ring_and_shell_hardware.md` (ring rail section, carriage length, shell-on-shell liner) and docs/HARDWARE.md (v4 hub).

## 3. Objectives (Pareto, not one blended score)

1. **R1 proximity**: share of covered skin 2-10 mm from the metal while following (also report 2-14 mm: the user allows up to 14 mm "if you really need to", for nested links; 10 mm stays the target).
2. **R3/R4 follow**, overall and on "Raise overhead".
3. **R10 GH misalignment** on the thorax-fixed base (worst frame, from the LP).
4. **Mass** of custom parts (R8; stretch goal < 150 g).
5. **Singular margin**: angle from the J1-J2-J3 coplanar configuration, worst frame, on the fitting AND held-out clips (P0 saw the 3R margin drop from 20 deg on the fitting clips to 14 deg on the held-out ones - a jamming pose the fit never saw).

Hard constraints: no body contact (R2 <= 0.5 mm, including the base on the moving scapular skin), no part contact (R6), every link arc >= 35 deg, ring travel <= what the chosen ring hardware allows, offsets |o| <= 60 mm.

Method: NSGA-II-style non-dominated sorting + crowding inside the existing evolutionary loop of `band_impl.run` (no new dependency; pymoo or BoTorch would need a download - ask first). Seeds: the P0 optima for families A and B and the r13 elite for C.

## 4. Robust across body shapes

Until SMPL-X is licensed (user action, `data/raw/README.md`): the rig at three uniform scales S x {0.92, 1.00, 1.08} (roughly 5th-percentile female to 95th-percentile male stature) and two girdle laws - the rig's and the literature law from `docs/research/gh_translation_literature.md`. A design's objective value is its **worst** over the training bodies (minimax robustness), not the mean. After the licence: 8 SMPL-X shapes spanning the first 3 shape components (+-2 SD), registered to the rig's skeleton, same rule.

## 5. Held-out split (decided before any search runs; to be committed as `data/raw/split.json`)

- Motions: fit on Raise overhead, Drink, Comb hair, High shelf, Wash opposite shoulder, Back pocket; **held out: Wave, Walking arm swing** (as in P0). When OpenCap clips exist: all of the "held-out tasks" in data/raw/README.md (jacket, seat belt, box to shelf, underarm throw, scratch neck) are held out; the user's own recordings of the 8 design tasks replace the synthetic ones for fitting.
- Bodies: S = 0.96 is held out from the rig scales; later, 2 of the SMPL-X shapes.
- Rule: no objective, constraint, seed or hyper-parameter is tuned on held-out data; held-out numbers are reported next to the fitting numbers in every scorecard.

## 6. Evaluator work needed (before the search)

The band evaluator (`pipeline/conformal/gpu/band_impl.py`) is direction-only: every member sample is a direction from the GH centre and clearance is read off radial skin maps. Offset axes make members rigid bodies with a translation, so:
1. Members as 3-D sample points in their own frame; per frame pose (R, t) from `girdle.Chain3` + the LP axis points.
2. Clearance: the same per-frame radial maps, looked up at each posed point's direction and radius (as `make_clips_full.map_clear` already does) - valid where the skin is star-shaped from the GH centre, which the maps' re-entry sheets (r2c) already guard.
3. Zero spare DOF (families A, B): no spare-angle grid, so one 3-DOF evaluation is ~1/30 of a 4R evaluation (r13 scanned 30 spare angles) - CPU search becomes realistic.
4. Base part: evaluated thorax-fixed against the moving scapular skin (judge/base_mount.py logic).
5. Cross-check every Pareto design with the honest scorer and the judges on built CAD (`tools/judge_all.sh`), since the evaluator has been optimistic before (FINDINGS).

## 7. Compute (this machine's CPUs, no paid compute)

- `nproc` = 4 here: 4 worker processes, one per family/body pair; torch threads 1 each.
- Estimate (to be measured before launch): family A/B evaluation without spare grid ~1-3 s per design per body on CPU -> 3 bodies x 2 laws x 64 pop x 60 gens ~ 1-4 h per family on 4 cores.
- The 4R comparison (family C) costs ~30x more per evaluation; run it only on the r13 elite, re-evaluated thorax-fixed (no new search).

## 8. The loop it leaves running

`new raw data or requirement -> tools/judge_all.sh on every design in designs/index.json -> P3 search warm-started from the last Pareto front -> scorecards -> commit`. The entry point is a script (`tools/loop.sh`, to be written with the evaluator) that runs unattended on the cloud machine's CPUs and writes `pipeline/full-exo/designs/pareto.json` + a scorecard table.

## 9. Exit (judge)

Pareto front with, for each design, R1-R6, R8, R10 on fitting AND held-out data; at least one 3-DOF design with R10 <= 4 mm, zero contact (R2, R6) and R4 >= 80 % on held-out clips, or a counter-example from the data showing which requirement blocks it and by how much.
