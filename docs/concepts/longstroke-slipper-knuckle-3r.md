# longstroke-slipper-knuckle-3r (2026-10-17)

**Status: screened. The lever does not pay in this family.** Research note with every table:
docs/research/longstroke_drive.md. Row: docs/concepts/rows/longstroke-slipper-knuckle-3r.json. Model:
docs/concepts/models/longstroke-slipper-knuckle-3r.py. Preview: docs/concepts/viz/concepts/longstroke-slipper-knuckle-3r.js.

## What it is

slipper-nose-knuckle-3r's chain (the verified seats, stop A a1 37.55, a2 57.22, pin knee, link 1 split by the passive
O20 knuckle K, K slaved to q2 by the hub-2 rim lobe and never read; 3 active DOF, 0 passive translations) with

- the **K sub-dyad re-seated long** (bk1 / bk2 26-34 / 38-56, stop B a1max up to bk1 + bk2 - 5), as the fold analysis
  (docs/research/fold_ceiling.md) asked, and
- a **long-stroke K drive** with every pressure angle <= 42 deg (friction included for sliding pairs), the hub-2 lobe
  stage included (the parents allowed 45 there). Three drives, one per process (LS_DRIVE):
  - `nose`: slipper-nose's hardened dowel sliding on the conjugate flank (mu 0.087: kinematic PA <= 37.03);
  - `roller`: the lead's MR63ZZ roller on the same synthesis (rolling: PA <= 42);
  - `rssr`: the sidecar's bell crank on link 1b -> O3 Ti rod with 2 M2 ball links -> horn lug of link 1a at hub K,
    closed per pose, transmission >= 48 deg at both ball ends (= PA <= 42; a two-force rod has no friction lean), the
    crank phase gam free.

Search switches (environment): `LS_STROKE_MIN` (a drive range below it scores +100), `LS_OBJ` (near2 | near1), and
`LS_GHOST=1` (ATTRIBUTION ONLY: the drive keeps its kinematics but its metal is deleted).

## Measured (frozen protocol: fit Bench(60,160) fast, shape frozen, Bench(110,360) exact and 952 held out)

| | drive range / K used | frozen exact | held out | reach | in-band | contact | complexity |
|---|---|---|---|---|---|---|---|
| slipper-nose (reference, verified) | 49.8 / 46 | 18.49 | 23.45 | 0.725 | 0.8955 | 0.0054 | 22.25 |
| control: slipper-nose's config through this model at PA <= 42 | 49.8 / 46 | 18.49 | - | 0.725 | 0.8955 | 0.0054 | 22.25 |
| **claim s65n2d (RSSR, K dyad 26.0 / 47.2)** | 65.0 / **41.6** | **21.27** | **26.19** | 0.722 | 0.873 | 0.008 | 30.5 |
| ghost g65d (drive metal deleted, attribution) | 66.8 / 42.1 | 19.50 | 22.69 | 0.731 | 0.885 | 0.011 | - |

Claim details: overhead 7 / 28; contact 3 poses (horn lug / hub K / rod, summed depth 18.5 mm, max 12.8 mm); near-touch
25.20 (1 mm) / 41.58 (2 mm); min th margin 5.036; flood static = connected full 21.27, knn 24.08. Convergence gate of the
claim's run: 0.03 / 0.01 / 0.00 (passes).

## Why it does not pay

1. One-sided contacts cap at 46.5 (nose) / 51.8 (roller) deg at PA 42; only the phased rod reaches 65-77 deg.
2. No search uses the stroke: 15 farm CMA runs settle on configs whose taken poses turn K 42-49 deg. The wall after the
   stroke is the **law**: the hub-2 lobe caps its slope at kK <= tan(42) g r_lobe / s_arm (~2.0), and at that slope the
   stretched poses past th ~109 fail the 5 deg closure.
3. The rod drive's metal sits over the band (bell crank median 14.0 mm, in band 0.50; ball links 0.67) and makes the
   contacts. Even deleted (ghost), the long-stroke chain is not a bench gain (19.50).

## Red team

- Jam: none inside the range (scan stops at transmission 48); used PA <= 28.5 / 25.2, range-end 42.0 / 40.8.
- Lift-off: the rod stage is bilateral; the lobe stage is spring-held as the lead (static factor 2.4); the spring's
  reflected J2 torque is 1.2-1.6 N at the cuff (< 2.5 N).
- Knife edge: the stroke survives +-1 deg / +-0.25 mm (61.5-66.8 deg), the parking does not: 9 / 33 neighbours lose
  every pose to the ROD-hubK 1 mm pair; r_h +0.25 is the robust build and measures identical (21.27 / 26.20).
- Alignment audit (`tools/alignment_audit.py audit longstroke-slipper-knuckle-3r --ref slipper-nose-knuckle-3r`): WATCH,
  no gamed finding (not verified; crank mostly out of band).
