# Sample density of the scored metal vs the kit (S6, 2026-10-18)

**Result: the top of the verified board does not change.** The lead conecut-knee-knuckle-3r stays at 18.28 on the bench.
Held out it moves 22.38 -> 22.43. No row moves under 18.28. lowarm-halfring-knuckle-3r (17.96, verdict "no new lead")
moves up, to 18.04 / 22.77. The desmo family moves down: desmo-conecut 18.98 -> 18.68 (from 10th to 5th) and
desmo-slipper 18.95 -> 18.81. Both stay behind the lead and slipper-nose (18.56).

**Why this audit.** The desmo-window death audit (commit 14dfecc) found ring2 sampled at 1 pt / 1 mm2, 4x the kit's
1 pt / 4 mm2 (`tools/concept_kit.py` Member.cell 4.0; straps 2 x 2 mm at r_ref 70, hub discs on a 2 mm grid). In-band14
is a share of samples, so an over-sampled part weighs extra:
- out-of-band metal that is over-sampled inflates the gap;
- well-placed metal that is over-sampled deflates it.

The honesty audit (`concept_kit.audit`) flags only sparse sampling.

## Instrument

`tools/sample_density.py measure <id>`:
1. Fits the claim's frozen shape through the model's own `frozen()`: the fit on Bench(60,160), stopped when the wear
   bench is built. Per-part counts equal the verifier's `parts_ib14` n on every row; `count_mismatch` is empty.
2. Measures each scored part (`M.rigid` + `M.link_pts`, the order `part_inband()` uses):
   - cell per sample = d1 x d2 (the grid's two pitches; a one-row part gets the kit's 2 mm across);
   - area = the sum of the cells;
   - ratio = (samples / mm2) / (1 / 4 mm2).

   A second reading is the convex hull on the part's best-fit plane plus a half-pitch border. The over-dense re-weight
   uses the higher of the two.
3. Flags parts at > 2x or < 0.5x the kit's density.
4. Re-weights the verifier's saved per-part in-band, bench and held, from files whose own gap reproduces the claim:
   - each flagged part's count goes to n / ratio;
   - in-band = sum(frac n) / sum(n);
   - reach, follow and contact are unchanged.

   The re-weight is exact for the counts. It assumes that a part's in-band share is uniform over its samples, which
   is the same assumption as the desmo-window re-weight.

Output: `remeasure/sample_density_<id>.json`.

The density reading is **conservative on tiny parts**. ring2 reads 2.45x here; the death audit's area-exact sector
(19 mm2 for 19 samples) reads 4x. With that 4x, ring2 alone takes desmo-conecut to 18.49, against 18.59 here.

## Results (frozen exact Bench(110,360) and held out; gap = claim -> kit density)

Columns:
- **Over-dense at kit** is the primary reading: only the parts above 2x are re-weighted.
- **Hull** is the same re-weight using the hull density reading.
- **Flagged** also re-weights the sparse L1a. This is a sensitivity only, because L1a is a masked lattice (below).
- **All** re-weights every part, including the kit's own straps, to exactly 1 / 4 mm2 at its real radius. This is a
  sensitivity only.

| row | v_gap | flagged parts (ratio to kit; m = masked lattice) | bench: claim -> over-dense at kit [hull] (flagged; all) | held: same |
|---|---|---|---|---|
| conecut-knee-knuckle-3r | 18.28 | roller 4.55x, L1a 0.33x m | 18.28 -> 18.28 [18.28] (18.28; 18.42) | 22.38 -> 22.43 [22.44] (22.38; 22.63) |
| desmo-conecut-knuckle-3r | 18.98 | horn 2.52x, ring2 2.44x, L1a 0.33x m | 18.98 -> 18.68 [18.68] (18.54; 18.87) | 23.19 -> 22.89 [22.89] (22.75; 23.08) |
| desmo-slipper-knuckle-3r | 18.95 | roller 4.40x, horn 2.25x, ring2 2.45x, L1a 0.33x m | 18.95 -> 18.81 [18.83] (18.66; 18.96) | 23.90 -> 23.77 [23.79] (23.61; 23.91) |
| dipped-law-groove-knuckle-3r | 18.64 | roller 2.22x, L1a 0.33x m | 18.64 -> 18.72 [18.74] (18.58; 18.92) | 24.07 -> 24.15 [24.17] (24.01; 24.35) |
| inband-rssr-knuckle-3r | None | L1a 0.33x m | 18.87 -> 18.87 [18.87] (18.72; 19.07) | 23.21 -> 23.21 [23.21] (23.06; 23.41) |
| lowarm-halfring-knuckle-3r | 17.96 | horn 2.52x, ring2 3.96x, L1a 0.33x m | 17.96 -> 18.04 [18.04] (17.90; 18.29) | 22.70 -> 22.77 [22.78] (22.64; 23.03) |
| minarc-stop-knuckle-4r | 19.54 | L1a 0.42x m | no record | no record |
| roller-longdyad-knuckle-3r | 18.67 | roller 2.23x, L1a 0.33x m | 18.67 -> 18.76 [18.79] (18.61; 18.96) | 23.73 -> 23.82 [23.85] (23.67; 24.02) |
| sidecar-longdyad-knuckle-3r | 18.91 | none | 18.91 -> 18.91 [18.91] (18.91; 18.91) | 22.67 -> 22.67 [22.67] (22.67; 22.68) |
| sidecar-parallelogram-knuckle-3r | 19.13 | L1a 0.48x m | 19.13 -> 19.13 [19.13] (19.13; 19.13) | 22.03 -> 22.03 [22.03] (22.03; 22.03) |
| sidecar-roller-flank-knuckle-3r | 20.08 | roller 2.02x, L1a 0.44x m | 20.08 -> 20.15 [20.16] (20.07; 20.42) | 22.35 -> 22.42 [22.44] (22.35; 22.69) |
| slipper-nose-knuckle-3r | 18.49 | roller 4.55x, L1a 0.33x m | 18.49 -> 18.56 [18.57] (18.41; 18.76) | 23.45 -> 23.52 [23.53] (23.36; 23.72) |
| trimlug-k165-knuckle-3r | 18.51 | roller 4.55x, L1a 0.33x m | 18.51 -> 18.58 [18.59] (18.43; 18.77) | 23.47 -> 23.54 [23.55] (23.38; 23.73) |

inband-rssr-knuckle-3r is screened, not verified. Its record is the audit re-measure (18.87 / 23.21).

## Per-part attribution (bench; the gap with that part alone at the kit's density)

| part | rows | ratio | in band | effect |
|---|---|---|---|---|
| roller (slipper family) | conecut-knee, slipper-nose, trimlug, desmo-slipper | 4.4-4.55x (hull 11-12x) | 0.94 | Well placed, so the over-weight deflates the gap: +0.07 bench on slipper-nose / trimlug. 0 on the lead, whose ib14 of 0.9012 sits above the 0.90 cap (held +0.05). |
| roller (longdyad family) | roller-longdyad, dipped-law-groove, sidecar-roller-flank | 2.0-2.2x | - | +0.07..0.09 |
| ring2 (desmo stage-1 ring) | desmo-conecut, desmo-slipper, lowarm-halfring | 2.45x (area-exact 4x); lowarm 3.96x on 4 samples | 0.15-0.55 | Out of band, so the over-weight inflates the gap: -0.39 / -0.41 (desmo-conecut / desmo-slipper bench). lowarm-halfring -0.01 (only 4 samples). |
| horn (desmo / lowarm) | desmo-conecut, desmo-slipper, lowarm-halfring | 2.25-2.52x | high | +0.09 (desmo-conecut, lowarm-halfring) and +0.21 (desmo-slipper's 61-sample horn) |
| L1a | every knuckle row | 0.33-0.48x | 0.98 | Sensitivity only (see "Masked lattices"). If re-weighted, every row drops 0.06-0.15. |

**Masked lattices (L1a).** L1a is a strap stub of 4 rows x 11 samples with 8 kept (3 / 1 / 1 / 3). The other cells lie
under the hubs, whose own discs sample that metal. The kept samples sit at the kit's pitch (d1 2.35 mm at r 54), but
the cell estimate reads the gaps between them as uncovered area (d2 4.65). It is reported and not re-weighted in the
primary reading.

**The lead's in-band sits above the cap.** conecut-knee's ib14 is 0.9012, so its in-band term is 0, and only a re-weight
that pushes it below 0.90 moves its gap. Re-weighting every part to exactly 1 / 4 mm2 gives 18.42 / 22.63. That is
mostly the kit's straps, which are sampled at r_ref 70 and so at 0.72-0.84x at their real radius: a convention shared by
every row, not a design property.

## What is not exact, and the re-wear commands

- The re-weight assumes each part's in-band share is uniform over its samples. The exact confirmation thins the flagged
  parts of the fitted shape (a 2 mm Poisson-disc subsample) before the wear:
  `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/sample_density.py rewear <id> bench|held`.
  It writes `remeasure/sample_density_<id>_<wear>_rewear.json`. It was not run here: at load ~18 one exact wear takes
  ~55 min (desmo-window audit). The candidates are desmo-conecut and desmo-slipper, the two rows the audit marks watch.
- **minarc-stop-knuckle-4r** has no per-part in-band on file, so there is nothing to re-weight. Its only flag is L1a
  (0.42x, a masked lattice), and no part is over-dense, so over-density cannot move it. For the record:
  `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py` (its
  frozen() returns parts_ib14), then `tools/sample_density.py measure minarc-stop-knuckle-4r --src-bench <that file>`.

## Audit check

`tools/alignment_audit.py` VERSION 2026-10-18.1 adds `density` (S6). It gives watch when a part above 2x the kit's
density moves the gap by more than 0.1 when re-weighted to the kit's density, either alone or with the other
over-dense parts, on the bench or held out. It never gives gamed and never changes the gap.

Today it gives watch on desmo-conecut (ring2 bench -0.39, held -0.39; all over-dense -0.30) and desmo-slipper (horn
+0.21, ring2 -0.41). It gives ok on every other row.

SELFTEST PASS, with 2 new mutations:
- an over-dense part moving the gap 0.2 gives watch;
- the same part moving nothing gives ok.
