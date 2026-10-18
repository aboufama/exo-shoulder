# Alignment audit: lowarm-halfring-knuckle-3r

This is a re-audit, run 2026-10-18 07:09-07:36 UTC on the box (local only, niced, OMP_NUM_THREADS=1, at most 2 of my
processes, box load 16-19 from other agents; the farm is closed, $0 spent). The hourly loop (07:04) triggered it for two
reasons. First, the re-issued screen's red team (commit f90113b) calls cell A's 18.28 "the honest tie at cx 16.5".
Second, the desmo-slipper audit (ledger 2026-10-18T06:26:41Z) found that this row loads the desmo family's stage-1 level
formula. Reference: conecut-knee-knuckle-3r, the verified lead (18.28). Tool VERSION 2026-10-17.6. The first audit of
this row (02:28-02:50) is superseded by this text; its skeptic section is kept below the rule.

- **Checks:** `docs/alignment/lowarm-halfring-knuckle-3r.json`. They ran through `tools/alignment_strparams_adapter.py`,
  because the tool still crashes on the row's string `best_params` (c_rules: 'str' object has no attribute 'items').
  Tool verdict: **watch**, on continuity alone (the held kNN flood loses 8.23). Every other check is ok.
- **New instrument:** `tools/alignment_lowarm_s1level.py`. It loads the row's verifier unchanged, re-applies glev after
  the model's clamp, and records where stage 1 sits. The previous instance of this audit wrote it before a container
  restart, and the lead's WIP commit f164440 saved it.
- **Files written:**
  - `remeasure/lowarm-halfring-knuckle-3r_s1level_geom_fast.json`: the four geometry runs.
  - `remeasure/lowarm-halfring-knuckle-3r_s1level3p9_{A,B}_bench.json`, with `_perpose` dumps: the exact re-wears.
- **Findings:** `docs/alignment/lowarm-halfring-knuckle-3r.findings.json`, 11 in all: 2 gamed (M3, P1) and 9 watch.
- **Ledger entry:** 2026-10-18T07:34:11Z, by auditor, run `audit:lowarm-halfring-knuckle-3r`, git 983ed3e.
  **Verdict GAMED**, claim v_gap 17.96.

## Verdict: GAMED. Claim v_gap 17.96 (score 93.47), held out 22.70

**Neither number stands on buildable metal.** Both the claim (cell B 17.96) and the "honest tie" (cell A 18.28) put
stage 1 inside link 1b's J2 lower plate. At the nearest level that clears the plate:

- **cell B reads 18.39**, 0.11 behind the lead;
- **cell A reads 18.65**, 0.37 behind the lead, with the same 262 takes and 4 contacts.

All of the cost is in-band; reach and contact do not move. P1 (the link-2 lift picked on the claim bench, held out
behind) is still unresolved, because the row carries no `leader_ruling`.

### Question 1: is "cell A 18.28" an honest, pre-registered config?

**Yes on selection. No on "tie".**

- **Pre-registered.** The ideation event (2026-10-17T23:25:10Z) names a_s 9.2, psi 149.5, glev -1.0 and zr 2.0 before
  modelling started (01:00).
- **Not picked on the claim bench.** The 114-config fast LHS over the whole box found cell A best (fast 13.12). The
  794-config frozen-exact scan moved only link 2's lift parameters (cell B). So P1 and P2 do not apply to cell A.
- **But the 18.28 is self-measured.** The proposer reproduced it, and the red team is the same screen agent. The
  verifier wore cell B only. Cell A's held 22.64 is "proposer, same code path" (the row's `cells.A.held_src`).
- **Held out it is behind.** 22.64 against the lead's 22.38: the tie is a bench reading only. A verifier wear of cell
  A (bench and held, `--cell A --flood --dump`) was running in another agent's slot during this audit; its result is
  not on file yet.
- **It inherits the unbuildable layer.** glev -1.0 is desmo-conecut's BEST, the lower edge of the box (question 2).

### Question 2: the inherited stage-1 layer

Measured with `tools/alignment_lowarm_s1level.py geom` on the frozen protocol's fit model (Bench(60,160), linear IK as
verified). All levels run along the J2 axis u2, over hub 2's face H2 = c2.u2 + f[1]. Stage 1 is identical in cells A
and B (same a_s / psi / glev). Source: `remeasure/lowarm-halfring-knuckle-3r_s1level_geom_fast.json`.

| part | verified level (glev -1.0, pin 9.2 / 149.5) | F+3.9 (glev 2.039, pin 9.8 / 150) |
|---|---|---|
| crank pivot PV | **F-1.289** (as desmo-conecut) | F-1.289 |
| groove ring (link 2 metal) and O1.5 pin band | **F+0.111 .. 1.611** | F+3.15 .. 4.65 |
| short arm, lower face, root to pin | F-2.146 .. -0.139 | F+0.751 .. 2.9 |
| pin radius about u2 | 9.60 mm | 9.90 mm |
| half-ring sector built | 18.9 deg (135 of 462 stations) | 18.3 deg (124 of 451) |
| groove rc_min / dK_lim / desmo_fail | 1.0 / 46 slot-end / [] | 1.02 / 46 slot-end / [] |
| dwell K play (hard pad) | 0.638 deg | 0.622 deg |
| link 1b's J2 lower member (the plate) | F+0 .. 3.0 (`tools/concept_kit.py` line 24) | same |
| link 1b samples within 12 mm of the J2 axis | 0 (no plate metal is sampled, so no clash can be read) | 0 |

What the table shows:

- **The verified groove and pin lie wholly inside the plate.** Both cells run the inherited formula hmid = PV.u2 + 3.15
  + glev (`docs/concepts/models/desmo-conecut-knuckle-3r.py` line 182). The lowarm model execs desmo-conecut's
  `_desmo_build_B` with only the half-ring line patched (model lines 41-48).
- **No value in the box is buildable.** The clamp box glev [-1.0, 1.5] (`desmo-slipper-knuckle-3r.py` line 87) keeps the
  layer bottom at F+0.11 .. 2.61, inside the plate for every value. -1.0 is the edge where the ring sector sits lowest
  and in-band reads best.
- **Cell A's own pin is dead at the plate-clearing level.** At F+3.9 (the family's criterion: the plate top F+3.0 plus
  the 0.15 running gap), pin 9.2 / 149.5 has pitch 10.304, past R_HI. The drive limit falls to 0 (s1-pitch), and the
  fast gap reads 95.51 (reach 0.344).
- **The pin I picked.** 9.8 / 150 is the family's pre-registered F+3.9 pin from the desmo-conecut CAD's level scan
  (`pipeline/full-exo/designs/user_desmo_conecut/stage1_level_scan.json`). 9.9 / 150 reads identically on fast. I picked
  on fast only, before any exact wear.
- **F+3.9 is the lenient level.** The short arm still runs F+0.75 .. 2.9 through the plate layer (a relief pocket is
  assumed, as on the family), and no CAD of this row exists.

**Exact frozen Bench(110,360) at F+3.9, pin 9.8 / 150.** These run through the row's verifier `wear()` unchanged; only
glev and the pin differ. Files: `remeasure/lowarm-halfring-knuckle-3r_s1level3p9_{A,B}_bench.json` and their `_perpose`
dumps, which recompute to 18.66 and 18.39. Each wear took 1010 s at about a third of a core.

| | cell A verified level | cell A F+3.9 | cell B verified level (claim) | cell B F+3.9 | lead conecut-knee |
|---|---|---|---|---|---|
| bench gap | 18.28 | **18.65** | 17.96 | **18.39** | 18.28 |
| reach (ws taken) | 0.7278 (262) | 0.7278 (262) | 0.7306 (263) | 0.7306 (263) | 0.7278 (262) |
| in-band 2-14 / 2-10 | 0.9006 / 0.5715 | 0.8963 / 0.5703 | 0.8978 / 0.5682 | 0.8935 / 0.5670 | 0.9012 / 0.5739 |
| contact (poses) | 0.0106 (4) | 0.0106 (4) | 0.0080 (3) | 0.0080 (3) | 0.0106 (4) |
| near-touch 1 mm | - | 20.29 | 20.14 | 20.57 | 19.92 |
| fit fast (plain) | 13.12 | 13.52 | - | 13.81 | - |

What the exact wears show:

- **The cost is in-band only:** +0.37 (A) and +0.43 (B). It is a third of the family's cost (desmo-conecut +1.52,
  desmo-slipper +1.43), because the half ring keeps only an 18-degree sector of the raised ring.
- **The rank flips.** With stage 1 out of the plate, the claim moves from ahead of the lead (-0.32) to behind it
  (+0.11). The tie becomes 0.37 behind, on identical takes and contacts: the lead keeps more metal in the 1-cm band.
- **Held out at F+3.9 was not run** (time box).

## What the wearer gets (measured)

Sources:

- the verifier's per-pose dumps at the verified level: `remeasure/lowarm-halfring-knuckle-3r_{bench,held}_perpose.json`;
- this audit's F+3.9 dumps;
- `remeasure/conecut-knee-knuckle-3r_bench_perpose.json` for the lead;
- the first audit's probe, `remeasure/lowarm-halfring-knuckle-3r_probe_bench.json`.

Counts of taken poses use min(metal, contact copy) at or above 0 and under x.

| | B verified bench | B held | A F+3.9 bench | B F+3.9 bench | lead bench |
|---|---|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 9 / 28 | 19 / 71 | 8 / 28 | 9 / 28 | 8 / 28 |
| raised-arm reach (elev >= 90) | 48 / 113 | 124 / 300 | 47 / 113 | 48 / 113 | 47 / 113 |
| taken poses with metal < 1 / 2 / 3 mm | 4 / 34 / 106 | 12 / 71 / 216 | 3 / 33 / 105 | 4 / 34 / 106 | 3 / 33 / 105 |
| taken overhead poses < 2 mm | 5 | 11 | 4 | 5 | 4 |
| closest taken metal | 0.048 mm (pose 316) | 0.325 mm | 0.072 mm | 0.048 mm | 0.072 mm |
| contact poses, summed depth, deepest | 3, 14.92 mm, **9.47 mm** at (15, 165, -60): crank | 13, 43.67 mm, **10.38 mm** at (45, 165, -30) | 4, 16.15 mm, 9.47 mm | 3, 14.92 mm, 9.47 mm | 4, 20.24 mm, 8.93 mm |
| workspace in-band, unscored (all / elev 90-140 / overhead) | 0.8634 / 0.8283 / 0.9279 | - | not probed | not probed | 0.8676 / 0.8315 / 0.9359 |

Beyond the table:

- **Springs:** none. The desmo K drive is spring-free.
- **Stops:** J2 / J3 dowel stops, and the crank stop pad on link 1b. The pad is unsampled (S3).
- **Dwell hold:** a hard pad leaves 0.638 deg of K play against the 0.25 gate (M5). Worn as metal, it closes pose 203
  from 0.263 mm to 0.008 mm (red team).
- **Cuff twist and drag:** not measured; there is no CAD or R17 run for this row.
- **Near-singular postures:**
  - The fold margin th is 5.181 bench and 5.11 held (5.088 / 5.017 with the dwell play; 0 poses dropped).
  - The K sub-dyad m_sub at K rest is under 1 deg on 50 of 205 rest bench poses (G4).

## Findings (`lowarm-halfring-knuckle-3r.findings.json`)

1. **M3, gamed: unbuildable stage-1 layer under both cells.**
   - *Evidence:* the two tables above.
   - *Why the exo is not better than its number:* the verified groove, pin and arm occupy link 1b's plate volume. Built,
     they must ride higher. There the extra ring metal leaves the band, and both cells fall behind the lead. The lead
     is a verified design already built at L2 CAD (`pipeline/full-exo/designs/user_conecut_knee`).
   - *Why gamed:* a hard rule (every part at its real envelope) is broken by the verified config, and that placement
     is what ranks the row ahead of (17.96) or level with (18.28) the lead.
   - *Action:* re-claim both cells at a level with the groove bottom at F+3.15 or above (bench and held), or record
     them as unbuildable.
2. **P1, gamed (carried, unresolved).**
   - *Evidence:* the link-2 lift is the minimum of 794 configs scanned on the claim bench. Held out it reads 22.70
     against the lead's 22.38.
   - *What is still missing:* `morphs.json` still shows 17.96 first among verified rows, with an empty `leader_ruling`.
   - *Action:* unchanged; record a `leader_ruling`.
3. **R1, watch: the "honest tie" is self-measured and bench-only.**
   - Cell A is pre-registered and clean of P1 (question 1).
   - Its 18.28 and its held 22.64 are the proposer's own numbers, and held out it is 0.26 behind the lead.
   - At the buildable level it is 0.37 behind on the bench.
   - *Action:* drop "tie" from the row and events until a verifier wears cell A at a buildable level, bench and held.
4. **NEW-inherited-stack, watch (proposed catalogue M6, carried).**
   - *Evidence:* round 15 lens B (`lowarm-adjpad-knuckle-3r`, ROUNDS.md lines 3644-3660) pre-registers its pass bar
     as "frozen exact <= 18.28 at cx <= 17.0". That bar was set by cell A on the unbuildable layer.
   - At the buildable level the same cell reads 18.65. Lens B's cell A0L (the one-part groove) is desmo-conecut, which
     reads 20.50 at F+3.9 (its audit).
   - *Action for the planner:* lens B must pre-register the stage-1 level (groove bottom >= F+3.15) before any run, or
     its pass bar is unreachable honestly.
5. **T1, watch (carried, report only).** The bench edge is pose 316 at 0.048 mm. It is unchanged at F+3.9.
6. **R3, watch (carried).** The row shows best-of-794 without its spread (p10 18.07, median 18.42).
7. **M5, watch (updated).** The hard pad still fails its own 0.25-deg gate (0.638; 0.622 at F+3.9). The red team
   measured the play as metal: the score moves -0.11 .. +0.10, but pose 203 closes to 0.008 mm. The fix (a preload or
   an adjuster) has unmeasured drag or parts.
8. **S3, watch (carried).** The pad is unsampled metal.
9. **S5, watch (carried).** Continuity holds only through the envelope stepping stones (held kNN 30.93 against 22.70).
10. **G4, watch (carried).** m_sub at K rest is under 1 deg on 50 of 205 rest poses. With the dwell play applied, the
    verifier's th row reads 0.0 at poses 283, 311 and 338.
11. **T5, watch (report only, the skeptic's missed 4, filed now).** The low arm (zr 2.0, both cells) made the deepest
    presses deeper than the lead's: bench 9.47 against 8.93 mm, held 10.38 against 9.86 mm.

**Resolved since the first audit:** M3 V5. The red team measured the lifted link 2 against the crank: at least 9.16 mm
over 373 taken poses, and at least 9.06 mm against link 1b. The skeptic refuted NEW-string-params; it is not re-raised,
although the tool still crashes on the string.

## Re-wear rule (step 2)

The row's last commit (f90113b, 06:08:37) added red-team fields and changed the note. The claim, `best_params` and
verification are unchanged, so `remeasure lowarm-halfring-knuckle-3r bench|held` was not re-run. The standing re-wear
(02:40, 17.96) and the verifier's dumps stand. The F+3.9 wears above are the new measurement.

## Numbers I could not get, and why

- **Held out at F+3.9, both cells:** the time box. Each exact wear took 17 min at the box's load; held needs about 2.5
  times that.
- **A wider pin scan at F+3.9, and levels fully above link 1b (F+4.6, F+6.15):** not run here. On desmo-slipper's
  chain, no pin kept the drive at F+6.15.
- **The relief that link 1b would need for the short arm at F+0.75 .. 2.9:** no CAD of this row exists. The strap is
  not sampled near J2.
- **Cell A's verifier wear at the verified level:** another agent's run; not on file at this writing.
- **The workspace probe at F+3.9:** the time box.
- **Cuff twist and pad drag:** no CAD.
- **The lead's own stage-1 level against its plate:** not measured here. The lead's drive is slipper-nose's (no desmo
  groove), and its L2 CAD exists.

## Proposals (not applied; none feeds the verdict)

1. **Family level fix (a measurement change, carried from the desmo-slipper audit).**
   - Change: measure the stage-1 level from hub 2's face, not from the crank pivot. Re-base glev so the groove bottom
     is at F+3.15 or above.
   - Measured effect on the verified rows at the nearest plate-clearing pin:

     | row | verified | at the buildable level |
     |---|---|---|
     | this row, cell B | 17.96 | 18.39 |
     | this row, cell A | 18.28 | 18.65 |
     | desmo-conecut | 18.98 | 20.50 |
     | desmo-slipper | 18.95 | 20.38 (held 25.33) |

   - No other verified row has a desmo stage 1.
2. **A layer check in every verifier of a stacked drive.** Sample each drive part against the members of the joint it
   sits in: link 1b's plate needs samples within 12 mm of J2 (n = 0 today). Effect: the same four rows as above.
3. **A pass bar carried into a new round names the level its source number was measured at.** This applies to round
   15 lens B: its 18.28 bar becomes 18.65 at the buildable level.

## Skeptic (2026-10-18, 07:37-07:46 UTC), second audit

The audit's skeptic ran this section. Method:
- **Raw files.** I re-derived the numbers from the raw files: the sweep rows, the verifier JSONs (cells A and B), the
  per-part in-band of every wear, the per-pose dumps (bench and held, both rows) and the family's built CAD scorecard.
- **One measurement of my own.** I ran `docs/concepts/verify/lowarm-halfring-knuckle-3r_padcheck.py` once, unchanged,
  niced: about 7 s on the fit bench. The output went to the scratchpad only.
- **Re-weighting at kit density.** I re-weighted the saved `parts_ib14` of the verified wears and of the auditor's F+3.9
  wears to the kit's sample density. The method is the one from death audit 14dfecc. The ratios come from the lead's
  cross-row density check, `remeasure/sample_density_*.json` (on disk, not yet committed).
- **Nothing edited.** No model, bench, judge, row or score was changed.

The rulings are in `docs/alignment/lowarm-halfring-knuckle-3r.rulings.json`. Ledger entry: 2026-10-18T07:44:04Z, run
`skeptic:lowarm-halfring-knuckle-3r`.

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): GAMED.** M3 and P1 are upheld. 10 reasons are upheld
and 2 are refuted (S3, T5).

**The claim moved after the audit.** Commit 786b081 (07:40:32Z, the cell-A verifier) changed the row's `v_gap` from 17.96
to **18.83**: cell A with its stop pad at the true lever. The verifier's verdict reads "NOT a lead and not a tie ... Cell
B stays GAMED (P1). NO NEW LEAD". This ledger entry still keys the audited claim, 17.96.

| key | ruling | evidence (short; full text in the rulings file) |
|---|---|---|
| continuity | upheld (watch) | held: full 22.70, kNN 30.93 (-8.23). Cell A held: kNN 30.78. Documented threshold applied to the rule's flood. |
| M3 | **upheld (gamed)** | The pin band F+0.111..1.611 at r 9.602 lies inside link 1b's lower member [F, F+3] at O20 r 10, with 0 link-1b samples within 12 mm. The parent's built CAD fails R6 at 1.50 mm on this same layer (VERIFY.md lines 43-44). The row's verifier adopted the finding. The whole cell-B cost at F+3.9 is ring2 (4 samples at 0.859 in band -> 6 at 0.176). My refutation attempt on the rank clause is below. |
| P1 | **upheld (gamed)** | 794 scan configs on the claim bench: min 17.96, p10 18.07, median 18.42. Now that cell A is verified (held 22.64), the lift scan shows as in-sample: -0.32 on the bench, +0.06 held out. At kit density, held still trails the lead: 22.64 / 23.03 vs 22.38 / 22.63. Still no `leader_ruling`. morphs.json (v119) still lists 17.96 first. |
| R1 | upheld (watch) | "Self-measured" is resolved: the verifier reproduces 18.28 and held 22.64. The conclusion is confirmed: held paired +0.26 (P(better) 0.005), "not a tie" by the verifier, 18.83 with the true-lever play. |
| NEW-inherited-stack | upheld (watch) | The model execs `_desmo_build_B` with one line swapped (lines 41-48). Lens B checks no level. The 18.28 bar is also the lead's own number ("cx-at-lead"), but a pass can still be met inside the plate. |
| T1 | upheld (watch) | Pose 316 at 0.048 mm here, -1.24 on the lead. Near-touch 20.14 / 34.84 / 86.40. Report only. |
| R3 | upheld (watch) | The spread (p10 18.07, median 18.42) is in no row or dashboard field. |
| M5 | upheld (watch), **understated** | The true pad lever is 6.75 mm, not 12.29 (I reproduced this). Play is 0.912 deg vs the 0.25 gate; worn as metal, cell A reads 18.83 with pose 203 at -0.102 mm (in the skin). Cell B at that play is not on file. |
| S3 | **refuted** | The pad is now measured: on link 1b's top face (base 59.1 = link-1b top, top 62.26 = the sampled arm top). All 4 corners are over L1b. Clear of L2 (18.46) and L1a (5.37), with no skin-facing metal. Source: `rows:verification_cellA.pad_true_lever.pad_block_metal`, reproduced by my padcheck run. |
| S5 | upheld (watch) | Same records as continuity. Cell A: kNN 19.97 bench, 30.78 held. |
| G4 | upheld (watch) | m_sub at K rest is < 1 deg on 50 of 205 (min 0.0). The "th 0.0 at 283/311/338" clause is not in the verifier file. Its J1-J3 th with play has min 5.088 and 0 drops, so the 0.0 is the sub-dyad, not the documented fold margin. |
| T5 | **refuted** | The documented threshold is summed depth >= 2x the reference's and >= 5 mm more. Measured: bench 14.92 (3 poses) vs the lead's 20.24 (4); held 43.67 (13) vs 60.97 (14), ratio 0.74 / 0.72. The deepest single press is +0.5 mm at 237 and 683, but 264 is 1.17 vs 5.80 mm and 316 clears. The wearer is pressed less in total. |

### The M3 rank clause at kit density (attempted refutation; does not refute)

Ring2 is sampled at 3.957x the kit's density (`sample_density_lowarm-halfring-knuckle-3r.json:parts.ring2.ratio`). The
lead logged this as a pending measurement change at 07:32Z, before the audit's 07:34Z entry. I re-weighted the in-band
from the saved `parts_ib14` (reach, follow and contact unchanged):

| wear | as sampled | flagged parts at kit (ring2, horn, L1a) | all parts at kit |
|---|---|---|---|
| cell B verified (glev -1.0) | 17.96 | 17.91 | 18.31 |
| cell B at F+3.9 (pin 9.8 / 150) | 18.39 | **18.02** | **18.41** |
| cell A verified | 18.28 | 18.28 | 18.53 |
| cell A at F+3.9 | 18.65 | 18.28 | 18.63 |
| lead conecut-knee | 18.28 | 18.28 | 18.42 |
| held: cell B / cell A / lead | 22.70 / 22.64 / 22.38 | 22.64 / 22.59 / 22.38 | 23.03 / 22.94 / 22.63 |

- **The cost of clearing the plate shrinks at kit density.** It is +0.00..+0.11, against +0.37 / +0.43 as sampled.
- **The bench rank does not flip at kit density.** Cell B at the buildable level stays ahead of the lead (18.02 vs 18.28)
  or level with it (18.41 vs 18.42).
- **Why this does not refute M3.** The density change is pending, not the current measurement. The clash itself
  (metal inside another part) is a hard-rule fact that no density changes.
- **Held out, the row trails the lead in every variant.** P1 stands on that, not on M3.

### Missed by the auditor (for the next audit; does not change this verdict)

1. **M5 is understated by 1.4x.** The claim's pad-seat test counts an arm point as over link 1b when it lies within 5
   mm of any link-1b sample. The true lever is 6.75 mm, which makes the dwell K play 0.912 deg, not 0.638 (gate 0.25).
   - Worn as metal on cell A: 18.83, 5 contacts, pose 203 at -0.102 mm (`rows:verification_cellA.play_as_metal_true_lever`).
   - The audit read only the claim's 0.638.
   - Cell B's 17.96 at this play is not on file. Cell B shares the pad and the dwell pose 203.
2. **The claim moved under the ledger.** The row's `v_gap` is now 18.83 (786b081, 07:40Z); the ledger still keys 17.96.
   The dashboard (morphs.json v119, 07:33) still shows 17.96 first among verified rows. The next audit must re-key on
   18.83 (cell A, true-lever play, plate layer not applied; 19.05 with both, per the verifier).
3. **The M3 magnitude ignores ring2's 3.96x over-density** (the table above). The event was on file 2 minutes before
   the audit's entry. This is a hygiene miss in the auditor's comparison, not gaming by the row: the over-density
   penalises the row at F+3.9.
4. **The P1 evidence path now holds cell-A data.** 786b081 overwrote
   `remeasure/lowarm-halfring-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` with cell A. The cell-B pairing the
   ledger cites lives only in git (8c2f2a3), so the next audit should cite it by commit.
5. **The string-params defect persists in a new tool** (instrument note). The padcheck script builds from the verifier's
   `BEST` (CELL_B defaults: l2_rfull 16.0, l2_len 9.84), not the claimed 14.0 / 9.836, and labels its output "cell A".
   The pad result does not depend on link 2 (min L2 18.46-18.9 mm), but any link-2 reading from that script is not the
   claim's.

### Proposal (not applied; it feeds no verdict)

- **S-1.** When the ring2 density measurement change lands, re-judge M3's level on the kit-density numbers.
  - The clash stays a hard-rule finding, at watch at least, until a buildable stage-1 placement is worn.
  - The rank consequence vanishes for cell B (18.02 / 18.41 vs 18.28 / 18.42).
  - Measured effect on the verified rows I re-weighted: this row B 17.96 -> 17.91 / 18.31; A 18.28 -> 18.28 / 18.53;
    the lead 18.28 -> 18.28 / 18.42 (flagged / all parts at kit).
  - The other rows' ratios are in the lead's `remeasure/sample_density_*.json`.

Next steps:
- **The lead:** record a `leader_ruling` on cell B (P1), or let the dashboard pick up the row's new 18.83.
- **The next audit:** key on 18.83. Wear cell B at the true-lever play (+0.912) and at a buildable stage-1 level at kit
  density, bench and held.


---

_Below: the first audit's skeptic section (2026-10-18 02:50-03:01 UTC), kept unchanged. Its rulings refer to the first
audit's findings (ledger 2026-10-18T02:43:22Z)._

## Skeptic (2026-10-18, 02:50-03:01 UTC)

Run by the audit's skeptic. I re-derived the numbers from the raw files: the sweep rows, the verifier JSONs, and the bench and
held per-pose dumps, where I recomputed the gaps myself (contact = contact poses / (taken + contact)). The model and every
bench, judge and row were left unchanged. One new measurement: the m_sub rest probe on this row (G4), through a new wrapper,
`tools/alignment_msub_strparams.py`. It runs the unchanged `tools/alignment_msub_rest_probe_model.py` with the row's string
params decoded over CELL_B, as the verifier does. It ran as one niced process for 540 s and reproduces 17.96. Rulings:
`docs/alignment/lowarm-halfring-knuckle-3r.rulings.json`. Ledger entry: 2026-10-18T03:00:45Z, run
`skeptic:lowarm-halfring-knuckle-3r`.

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): GAMED.** P1 is upheld. 9 reasons upheld, 1 refuted
(NEW-string-params).

| key | ruling | evidence |
|---|---|---|
| continuity (watch) | **upheld** | Held: static 22.70, connected_full 22.70 (0 dropped), kNN 30.93 (77 dropped), bench graph 23.88. Bench: kNN 19.64, bench graph 49.98. The tool reads the rule's flood (loss 0, ok), then raises it to watch because the kNN loss is over TH conn_gamed 3. That is the documented rule applied to the documented number. |
| judgement:P1 (gamed) | **upheld** | Sweep re-derived: 794 frozen-scan rows, all tagged `Bench(110,360) exact` (the claim bench); min 17.96, p10 18.07, median 18.42, max 19.30; 251 under 18.28. Held, recomputed by me from the per-pose rows: 22.70 (658/952 ws, ib14 0.8967, 13 contacts) vs the lead's 22.38 (659/952, 0.9000, 14), same 1154 poses, both exact. The bench comparison is not apples to apples, and the bias favours this row: the lead was searched on Bench(60,160) fast (its row note, 352 configs) and frozen onto the exact bench, while this row's 17.96 is the minimum of a scan on the exact bench itself. morphs.json shows this row first among status `verified`, with `leader_ruling` empty on both rows. Caveats (none refutes): the documented `held_out` threshold reads ok (+4.74 < 6), so the level is a judgement on the rank; the held difference is not significant (CI90 [-0.34, +0.68]); cell A's 22.64 has no dump (see missed 1). |
| judgement:T1 (watch) | upheld | Pose 316 is the only discordant bench pose: 0.048 mm here, -1.235 mm on the lead. Held 820: 0.941 mm here, -0.177 on the lead. The 251 beaters clear 316 by 0.014-0.197 mm; clearance >= 0.1 mm gives 18.24, >= 0.2 mm gives 18.41. Near-touch 1 / 2 / 3 mm: 20.14 / 34.84 / 86.40 vs 19.92 / 34.84 / 86.16. Taken poses under 1 / 2 / 3 mm: 4 / 34 / 106 vs 3 / 33 / 105. Report only. |
| judgement:R3 (watch) | upheld | The spread is right. The row carries n_configs 908 and B_robust 18.41 but no p10 or median; the dashboard shows only 17.96. |
| judgement:M5 (watch) | upheld | dwell_K_play 0.638 against the 0.25 gate (ok false; tight 0.292). V4 (`kplay_correct`, verifier lines 154-175) only drops poses by th margin and never moves metal by the play, so the metal shift at 316 and 139 is not on file. Neither is the pad's drag. |
| judgement:M3 (watch) | upheld, **narrowed** | V5 is in the docstring only. But the lifted bar against the crank ARM is on file. The model's own `l2_check` (desmo-slipper model lines 358-372) reads `link_pts["L2"]`, which the lift rewrites (lowarm model lines 83-92). It measures link 2's strap outside O20 + 1.5 mm (underside and top copy) against the crank's short arm and pin in every taken pose: **clear_min 12.32 mm bench (373 poses), 12.33 held (860), 0 lost** (parent 12.11 / 12.12). Still unmeasured: the tip plate, the hub-2 crown, and the root inside r < 11.5 mm. |
| judgement:S3 (watch) | upheld | `lowarm_fit.pad` holds position only (lever 12.29 mm, 7 of 28 arm points over link 1b). There is no height or skin clearance on file. `parts_ib14.pad` [1.0, 6.2, 32] is identical on the lead, so it is the cuff pad. |
| judgement:S5 (watch) | upheld | Same records as continuity: kNN 19.64 / 30.93 (6 / 77 forced poses dropped), bench graph 49.98. |
| judgement:G4 (watch) | upheld, **now measured on this row** | `remeasure/lowarm-halfring-knuckle-3r_msub_rest_bench.json`: m_sub at K rest n 205, min 0.0, p10 0.267, median 4.753, **< 1 deg on 50**, < 2 deg on 65, < 5 deg on 107, identical to the parent. Moved poses: m_sub min 10.805, m_eff min 5.181. |
| judgement:NEW-string-params (watch) | **refuted** | The format is real (the only string `best_params` among the rows). But no number on file was worn with CELL_B's defaults (l2_rfull 16). The verifier's bench and held params, the remeasure params, both per-pose dumps and this skeptic's probe all carry l2_rfull 14.0 / l2_len 9.836 / l2_lift 1.5, and four independent wears reproduce 17.96. Through the adapter every audit check ran (rules ok, reporting ok). The wearer's numbers are unchanged. It is an instrument defect, already proposal R5, not evidence about the design. |

### Missed by the audit (for the next audit; not in this verdict)

1. **Cell A's held 22.64 is unverified, yet three conclusions lean on it**: the row verdict ("does not transfer"), the
   audit's P1 sub-point ("worse than its own no-lift cell"), and the audit's suggested fallback claim (cell A at 18.28 as
   the honest tie). `rows:cells.A.held_src` = "proposer, same code path". No held dump or verifier file for cell A exists
   in `docs/concepts/verify/` or `docs/alignment/remeasure/`. Before cell A is claimed as the tie at complexity 16.5, its
   held number needs a verifier wear and a per-pose dump.
2. **The held reach loss includes two poses this design never evaluates.** Held 274 (-60 / 45 / 120) and 1054 (135 / 30 /
   -135) have `ev` false here (lost before evaluation, within held `why.fold` 262), while the lead takes them at 2.28 and
   1.23 mm. The chain is said to be unchanged, yet the held fold set differs from the lead's. The frozen re-fit for cell B
   moves which poses fold. It is small (+0.11 reach), but it shows the lift is not a pure link-2 change on the held set.
3. **The audit's held leg rests on the verifier's own dump.** Every held number in P1 and T1 comes from
   `remeasure/lowarm-halfring-knuckle-3r_held_perpose.json`, written by the row's verifier (its note), with no `git`
   field. The lead's held dump was written by the auditor (git 748862f). I recomputed it and it is consistent (22.70), but
   no third party has re-worn the held set for this row.
4. **The deepest contacts got deeper, and cell A shares the cause.** The audit tabled it but filed no finding. The low arm
   (zr 4.03 -> 2.0) brought the crank 2 mm closer: bench 237 9.47 vs 8.93 mm, held 683 10.39 vs 9.86, 610 9.82 vs 9.13.
   T5 reads ok only because it sums depth. Cell A has the same low arm, so the recommended fallback claim inherits it.

Next: the lead records a `leader_ruling` on the row, or claims the held number, to clear P1. Cell A needs a verifier held
wear (missed 1) before it is offered as a tie. V5 still needs the tip-plate, hub-2 crown and root-in-stack clearances, and
M5 needs a K-perturbed re-wear of poses 316 and 139.
