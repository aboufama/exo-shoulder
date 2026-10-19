# Skin signed distance: what the "1000x" speed-up is (measured 2026-10-15)

The user's question: "a super big efficiency was found for skin mapping, 1000x speed-up - can you confirm?"
Answer: **yes for the precomputed distance grid (~1600x vs the judge's own signed distance per pose score, ~290x vs
exact libigl), no for libigl alone (~6x, all of it in setup).** The grid's cost is ~1 mm of error and ~1 % of points
whose 2-14 mm band classification flips, so final numbers are re-checked on the exact path.

## Method
`docs/research/skin_distance_speed_measure.py` (raw numbers: `skin_distance_speed.json`). Six bench poses of
Bench(60, 160) (rest, clip frames, workspace poses), per pose the same 2000 metal-like points: skin vertices within
160 mm of GH pushed along the GH ray by U(-3, 30) mm. Three paths on identical inputs, same process, back to back:
(a) `judge/sdist.py` Mesh (exact closest point + winding grid, the reference), (b) `concept_bench._Exact` (libigl
unsigned distance on the shoulder submesh + fast winding number for the sign), (c) the bench's precomputed int8 grid
(4 mm voxels, 0.25 mm steps, trilinear). Box load ~14 on 4 cores (other agents running): times are medians, ratios
are what to read.

## Result (median of 6 poses)

| path | per-pose setup | 2000-point query | setup + query | vs sdist | error vs sdist (points within 20 mm) |
|---|---|---|---|---|---|
| judge/sdist.py | 1.46 s | 0.16 s | 1.62 s | 1x | reference |
| libigl exact | 0.008 s | 0.28 s | 0.29 s | **6x** | 0.0 mm (identical), 0 sign errors |
| grid cache | none (2.2 MB slab paged in) | 0.001 s | 0.001 s | **~1600x** (~290x vs libigl) | p99 0.5-1.5 mm, max 1.9 mm; 0.5-2 % sign errors (points within ~2 mm of skin); 0.5-1.5 % of points flip in/out of the 2-14 mm band |

## What it means
- The big gain is **amortisation**, the standard robotics move (precomputed distance fields, as in CHOMP / TrajOpt
  collision checking): the grid costs ~8 CPU-s per pose once (`concept_bench.py --build`, 10 min for 220 poses on 3
  cores), then every evaluation is a trilinear lookup. It pays for itself after ~5 scores per pose; a 200-config sweep
  is ~1000x cheaper. A full baseline evaluation (6 percentile variants) now takes 32 s.
- libigl's own contribution is exactness at low setup cost (no 1.5 s sample-tree build), but its query is slower than
  a warm sdist query because it rebuilds its AABB tree inside every call; caching the tree per pose would give another
  ~2-3x on the exact path.
- **Caveat that matters for decisions:** the grid misjudges the sign of points within ~2 mm of the skin, so a pose's
  "contact" (any point < 0) can flip, and ~1 % of points change band. Sweeps use the grid; every reported winner is
  re-measured with `CB_EXACT=1` (the screening verifiers do this).
