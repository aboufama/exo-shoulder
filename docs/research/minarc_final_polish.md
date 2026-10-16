# minarc BDp final polish on a representative envelope bench (2026-10-16)

Self-measured. Every held-out number below comes from the minarc judge's own harness
(`docs/concepts/verify/minarc-bdp-remeasure.py`, imported unchanged) with the judge's built-stop pricing; only the
benches are swapped (`tools/env_polish.py claim`). A config replaces BDp's CAD config only after an independent
verifier confirms a held-out gain of at least 1 gap point (CLAUDE.md final-polish rule).

## Why

Every polish so far lost about 5 points held out. The cross-fit study (`docs/research/crossfit_polish.md`) measured
the cause: the search benches pick their workspace poses by `linspace` over the grid order, which under-samples axial
rotation (|axial| >= 150 deg is 6-7.5 % of the bench vs 11 % of the held-out set). A polish then buys closure on the
bench that turns into skin contact elsewhere. The fix is a search bench drawn from the whole workspace envelope.

## 1. The bench: `env` (tools/env_bench.py)

**The envelope.** The one the workspace grid samples (`pipeline/conformal/gpu_client/pack_envelope.py --functional`):
* plane -90..150, elevation 0..170, humeral rotation r = axial + plane -90..90;
* inside `rt_common.plausible` (elevation ceiling per plane) and the functional rotation limits.

The grid is this envelope on a 15-deg lattice (1432 poses).

**The draw** (seeded, deterministic; `python3 tools/env_bench.py make`):
* **Cells.** Every grid pose owns its 15-deg cell (plane / elevation / r +- 7.5, clipped to the box). A fresh pose is
  uniform inside a cell and must satisfy the envelope law.
* **Strata on the drawn pose's own values.** Elevation band x plane band x signed axial band (edges -150 -90 -45 0 45
  90 150). The quotas are the grid's shares (largest remainder).
  * Why not one draw per random cell: the grid is lattice-weighted. Its boundary rows (e.g. |axial| 150-180 at the
    plane / rotation limits) carry full weight, and the held-out set is a subset of that grid.
  * A plain uniform draw in the continuous envelope under-samples those rows again. Measured on the first version:
    6.7 % |axial| >= 150 vs the grid's 9.4 %.
  * Two lattice-edge strata have almost no continuous volume (e.g. elevation < 45, plane 0-60, axial +90..150 needs
    r = 90 and plane = 0 exactly). After 3000 tries they accept a draw from their own cells: 2 poses per draw.
* **The held-out set stays held out.** A draw is rejected if it lies within 2 deg of any held-out pose (the verifier's
  1154: every fit-clip frame and workspace pose outside Bench(110,360) and Bench(60,160)). The test is twice:
  * in each coordinate (Chebyshev on plane / elevation / axial, axial wrapped);
  * in humerus orientation (geodesic), which catches the low-elevation degeneracy of plane vs axial.

  Draws within 2 deg of an already drawn pose are also rejected, so env and envsel are disjoint. The lead's ruling:
  fresh draws near held-out poses are fine; reusing or near-duplicating them is not.
  * Rejected: env 5 by coordinates + 2 by orientation, envsel 10 + 4.
  * Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (orientation), envsel 2.07 / 2.03.
  * Median orientation distance to the nearest held-out pose: 7.5 deg.
* **Frames.** Each fresh pose gets the rig's frames exactly as the grid does: `design_search` Ry Rx Ry + scapula
  rhythm, elbow 90, forearm neutral (HG rebuild error on the grid 3e-8).
* **Benches.** The 110 clip frames of Bench(110,360) (never Wave / Walking) + the fresh workspace poses.
  * **env**: 420 poses (seed 1), the search bench.
  * **envsel**: 360 poses (seed 2), the pick-selection bench (fit env -> wear envsel frozen). CMA selects on the noise
    of a fixed pool, so the picks are ranked on an independent draw.
* **Installation.** `tools/env_bench.py install()` appends the draws to `concept_bench._poses_all()` under a new clip
  name. They are not a fit clip and not the grid, so every grid, held-out and clip computation is unchanged.

**The table** (workspace poses only; `docs/research/minarc_final_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead (el >= 140) | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

(The axial -90..-45 share in `crossfit_polish.md` was 33.1 % for the pool; it counted a different band.) env and
envsel match the full grid within sampling error on every band.

Note: the held-out set is the grid MINUS the linspace benches. So it is skewed the OTHER way (11.0 % vs the grid's
9.4 %): it carries the extremes the benches lack. A representative sample of the envelope predicts the grid, not that
complement exactly.

**Fast caches** (farm; `tools/env_bench.py jobs / assemble / validate / use`):
* The same grids as `concept_bench --build` (same `_grid_pose`), 14 part jobs: 530 + 470 poses, wall 9.5 min (queued
  behind other agents), $0.10.
* Validation against the exact path (12 poses, ~17k points within 20 mm of the skin):
  * env: max error 1.86 mm, p99 1.14 mm, mean 0.12 mm, sign agreement beyond 1 mm 1.0;
  * envsel: 1.94 / 1.16 / 0.12 mm, sign agreement 0.99986.
* Keys `env-72d21f5aa2e5-env`, `env-fc171830d1d7-envsel`, on the farm volume.

**Sampling noise is the size of the effect.** The kinematic closure share (fold window + knee + closure, the flood
fill's node law) per pose set:

| config | Bench(110,360) ws | env | envsel | full grid | held out ws |
|---|---|---|---|---|---|
| BDp (priced stops) | 0.733 | 0.731 | 0.706 | 0.719 | 0.704 |
| H1 | 0.689 | 0.691 | 0.667 | 0.675 | 0.658 |

(`docs/research/minarc_final_polish/kin_closure.json`, Bench(60,160) knee reference, run at CB_FOLD_MARGIN 5.5.)
* The binomial standard error of a 420-pose share is about 0.022, i.e. about 2 reach points = 2 gap points. env and
  envsel differ by 2.5 points: both are fair draws of the envelope, and their spread IS that noise.
* Bench(110,360)'s closure surplus over held out (2.9 / 3.1 points) is about 1.3 standard errors. The skew is real
  (the axial table), but a 420-pose bench cannot resolve it better than about +- 2 points.

## 2. Does `env` predict held out better than Bench(110,360)?

__PREDICT__

## 3. The polish

__POLISH__

## 4. The claim

__CLAIM__

## Cost

__COST__

## Files

* `tools/env_bench.py` - the draw, the table, the farm cache (parts / assemble / validate / use).
* `tools/env_polish.py` - the objective, the CMA driver (tools/crossfit_polish.py's, patched), the stop pricing, the
  fresh-pose continuity, the claim wrapper.
* `docs/research/minarc_final_polish/env_poses.npz` - both draws (poses, humerus / scapula frames, source cell).
  It is frozen: the fast-cache key hashes the pose indices, so a redraw needs a new cache.
* `docs/research/minarc_final_polish/env_table.json` - the distribution table.
* `docs/research/minarc_final_polish/farm/` - job files, CMA rows (`cma_envp-*.json`), re-score and claim outputs.
* `docs/research/minarc_final_polish/picks/` - the picks' nominal parameters (the claim prices them).
