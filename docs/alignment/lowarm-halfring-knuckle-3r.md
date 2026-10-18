# Alignment audit: lowarm-halfring-knuckle-3r

Third audit of this row, run 2026-10-18 08:18-08:37 UTC on the box (local only, niced, OMP_NUM_THREADS=1, at most 2 of
my processes, box load 11-15 from other agents; the farm is closed by CLAUDE.md's spent budget line, $0 spent). Why it
ran: discovery round 14, slice r14-B, and the claim moved under the ledger. Commit 786b081 (07:40:32Z) re-verified the row
on cell A and set `v_gap` 18.83, while the ledger's last entry (skeptic, 07:44:04Z) still carried findings written for
cell B's 17.96. Reference: conecut-knee-knuckle-3r, the verified lead (18.28). Tool VERSION 2026-10-18.1. The previous
auditor sections are replaced by this text; both skeptic sections are kept below the rule.

- **Checks:** `docs/alignment/lowarm-halfring-knuckle-3r.json` (12 checks + rules). Tool verdict: **watch**, on continuity alone (the held kNN flood loses 8.14); every other check is ok. Two checks read the unplayed re-wear, not the claim: `near_touch` and `dominance` compare cell A without play (18.28; plain +0.00 and 2 mm +0.00 vs the lead), and `contact_depth` finds no dump that reproduces 18.83 (the verifier's dumps recompute 18.29). The per-pose play wear below supplies those numbers by hand.
- **Re-wear (step 2):** due. The row's last commit (07:40:32) is newer than the standing re-wear (02:43, cell B). The
  tool's `remeasure` still crashes on the row's string `best_params` (`dict(str)`), so I ran it UNCHANGED through a
  scratch wrapper that points its row directory at a copy with `best_params` decoded (no repo file edited). The params
  are the row's `best_params` (cell A: no `l2_lift`, so the model's default 0.0).
  Output: `docs/alignment/remeasure/lowarm-halfring-knuckle-3r_bench.json`, `..._held.json`.
- **New measurement:** the verified play, read per pose. The verifier's own `docs/concepts/models/lowarm-halfring-knuckle-3r-kplay.py`
  ran unchanged for cell A at +0.912 and -0.912, with `tools/alignment_paired.py`'s per-pose rows stashed for both sides.
  Output: `docs/alignment/remeasure/lowarm-halfring-knuckle-3r_kplay_perpose_A.json`.
- **Housekeeping:** a mis-pathed scratch stash of that run (per-pose rows, numbers only) landed at the repo root as
  `0.912` and was swept into the watchdog commit d3aac25 (08:29). This audit's commit removes it; its content is in the
  `_kplay_perpose_A.json` above.
- **Findings:** `docs/alignment/lowarm-halfring-knuckle-3r.findings.json`, 8 in all: 1 gamed (M3) and 7 watch.
- **Ledger:** 2026-10-18T08:35:49Z, by auditor, run `audit:lowarm-halfring-knuckle-3r`, git 1a20637. **Verdict GAMED**, claim v_gap 18.83 (re-keyed from 17.96).

## Verdict: GAMED. Claim v_gap 18.83 (score 93.15), held out 22.64 (no play, unclashed)

**The claim is now behind the lead, and the gamed P1 is gone from the headline.** The row's number is cell A (pre-registered
at ideation 2026-10-17T23:25:10Z, not picked on the claim bench) with the hard stop pad at its true 6.75 mm lever and the
resulting 0.912-deg dwell K play worn as metal on one side. The dashboard shows 18.83, 8th among verified rows.

**What still keeps it gamed is M3, on the hard-rule clause.** The verified config still has stage 1's groove ring sector
and O1.5 pin inside link 1b's J2 lower plate. The verifier measured the buildable number itself (19.05 with the play, 18.65
without, `docs/concepts/verify/lowarm-halfring-knuckle-3r_vA_padplay.json`) and did not put it in `v_gap`. At 18.83 the
row ranks ahead of sidecar-longdyad-knuckle-3r (18.91); at its own buildable 19.05 it ranks behind. The margin is small
(0.14 bench, held a tie) and density-sensitive, so the rank clause alone would only be watch; the clash is the gamed fact.

**The verified play is read on its kind side.** v_gap wears the 0.912-deg play as +0.912 on every dwell pose. The
two sides hurt different poses, and the per-pose worst of the two reads **18.89** (measured this audit, reproducing the
verifier's 18.83 / 18.35 first). It is +0.06, so it changes no rank, but it is the reading the wearer gets.

Re-wear (this audit, model unchanged): bench 18.28 (262/360, 4 contacts, near-touch 19.92 / 34.84 / 86.16, band 3-14
mm 18.42), held 22.64 (657/952, near-touch 25.49 / 37.12 / 82.96). Both match the verifier's cell-A numbers, and on the
bench they match the lead pose for pose.

## What the wearer gets (measured)

Sources: the verifier's cell-A dumps `remeasure/lowarm-halfring-knuckle-3r_{bench,held}_perpose.json` (recompute 18.29 /
22.64), this audit's per-pose play wear, this audit's re-wear, and the first audit's probe (cell B) for the unscored
workspace in-band. Counts of taken poses use min(metal, contact copy) at or above 0 and under x.

| | A verified, no play, bench | A held, no play | A +0.912 (v_gap) bench | A per-pose worst of +/-0.912 | lead bench |
|---|---|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | 18 / 71 | 8 / 28 | 8 / 28 | 8 / 28 |
| raised-arm reach (elev >= 90) | 47 / 113 | 123 / 300 | 46 / 113 | 46 / 113 | 47 / 113 |
| taken poses with metal < 1 / 2 / 3 mm (contacts excluded) | 3 / 33 / 105 of 372 | 13 / 70 / 215 of 859 | 3 / 34 / 107 of 371 | 3 / 34 / 107 of 371 | 3 / 33 / 105 |
| closest taken metal | 0.072 mm (pose 139) | 0.325 mm | 0.072 mm | 0.072 mm | 0.072 mm |
| contact poses, summed depth, deepest | 4, 16.16 mm, 9.47 mm at (15, 165, -60): crank | 14, 43.84 mm | 5, 16.24 mm, 9.50 mm | 5, 18.13 mm, **10.22 mm** at (15, 165, -60) | 4, 20.24 mm, 8.93 mm |
| gap | 18.28 | 22.64 | 18.83 | **18.89** | 18.28 |
| workspace in-band, unscored (all / elev 90-140 / overhead) | cell B probe: 0.8634 / 0.8283 / 0.9279 | - | - | - | 0.8676 / 0.8315 / 0.9359 |

Beyond the table:

- **Springs:** none. The desmo K drive is spring-free.
- **Stops:** J2 / J3 dowel stops and the crank stop pad on link 1b (now measured: on link 1b's top face, clear of link 2
  by 18.46 mm and link 1a by 5.37 mm, `rows: verification_cellA.pad_true_lever.pad_block_metal`).
- **Dwell hold:** the hard pad's true lever is 6.75 mm, so the K play is 0.912 deg, 3.6x the claim's own 0.25 gate. It
  puts pose 203 (abduction 90 / external rotation 45) 0.10 mm into the skin on the +side.
- **Cuff twist and drag:** not measured; there is no CAD or R17 run for this row.
- **Near-singular postures:** the fold margin th is 5.181 bench and 5.11 held (5.088 / 5.017 with the play; 0 poses
  dropped). The K sub-dyad m_sub at K rest is under 1 deg on 50 of 205 rest bench poses (G4).
- **Continuity:** connected_full equals static (18.28 / 22.64), but the kNN flood without the envelope stepping stones
  reads 19.97 bench and 30.78 held (S5).

## Findings (`lowarm-halfring-knuckle-3r.findings.json`)

- **M3** (gamed). Re-keyed on the moved claim v_gap 18.83 (786b081, cell A with the hard pad's true-lever dwell play worn as metal). The verified number still stands on the stage-1 layer that sits inside link 1b's J2 lower member: at glev -1.0 the groove ring sector (link 2 metal) and the O1.5 pin occupy F+0.111..1.611 inside the plate F+0..3.0 (docs/alignment/remeasure/lowarm-halfring-knuckle-3r_s1level_geom_fast.json; the family's built CAD fails R6 at 1.50 mm on the same layer, desmo-conecut VERIFY.md). Two real envelopes in one volume: a hard rule (every part at its real envelope) is broken by the verified config. NEW this audit: the verifier MEASURED the buildable number and left it out of v_gap - docs/concepts/verify/lowarm-halfring-knuckle-3r_vA_padplay.json kplay_true_lever_stage1_F39: 18.65 at play 0, 19.05 at +0.912 (row verification_cellA.v_gap_rule: 'plate layer not applied; 19.05 with both'). Rank consequence on the dashboard (docs/dashboard/data/morphs.json, verified rows by v_gap): 18.83 places the row 8th, ahead of sidecar-longdyad-knuckle-3r 18.91 (ledger watch, no stage-1 clash, held 22.67); the verifier's own buildable 19.05 places it behind. Against desmo-slipper 18.95 / desmo-conecut 18.98 the order holds like-for-like (they carry the same unapplied layer, +1.43 / +1.52). Size is small and density-sensitive (the skeptic's kit-density re-weight puts cell A's layer cost at +0.00..+0.10, pending measurement change), so the rank flip over sidecar-longdyad is 0.14 bench points and held is a tie (22.64 unclashed, no play, vs 22.67); the gamed level rests on the hard rule plus the verifier's own unapplied measurement, not on a wearer-side margin. Action: publish v_gap at the buildable level (19.05) or record a lead ruling that the layer is deferred to CAD; the family (desmo-slipper, desmo-conecut, both ledgered watch on the same layer) needs one ruling. [evidence: docs/concepts/verify/lowarm-halfring-knuckle-3r_vA_padplay.json; docs/concepts/rows/lowarm-halfring-knuckle-3r.json verification_cellA.stage1_layer_auditor and v_gap_rule; docs/alignment/remeasure/lowarm-halfring-knuckle-3r_s1level3p9_A_bench.json] Why the exo is not better: a pin and a ring sector cannot occupy the plate that carries J2. The buildable placement costs in-band, and the verifier measured it. Action: publish 19.05, or record a family-wide lead ruling that defers the layer to CAD.
- **NEW-one-sided-play** (watch). The verified v_gap 18.83 wears the dwell K play as ONE uniform side on every dwell pose (+0.912: 18.83; -0.912: 18.35). A free play of 0.912 deg sits on whichever side the load pushes it, pose by pose, and the two sides hurt different poses: the +side takes the extra contact (pose 203, abduction 90 / external rotation 45, -0.102 mm) but raises in-band to 0.9021 (above the 0.90 threshold, so in-band adds 0 to the gap), while the -side drops in-band to 0.8994 and presses 237 and 264 deeper (-10.215 / -1.753 mm vs -9.504 / -0.579). MEASURED this audit: the verifier's own kplay script (docs/concepts/models/lowarm-halfring-knuckle-3r-kplay.py, unchanged, cell A) at +/-0.912 with per-pose rows stashed, reproducing 18.83 / 18.35; the per-pose worst of the two sides (taken on both, contact on either, the lower in-band fraction) reads 18.89 (reach 0.725 = 261/360, in-band 0.8994, 5 contacts, summed depth 18.13 mm, deepest 10.22 mm at pose 237 = plane 15 / elev 165 / axial -60). +0.06 over v_gap: small, but optimistic by construction, and it moves the row no rank (sidecar-longdyad 18.91 stays behind). Proposed catalogue entry T6 (play read on one side). [evidence: docs/alignment/remeasure/lowarm-halfring-knuckle-3r_kplay_perpose_A.json] Why the exo is not better: the wearer gets both sides of the play, pose by pose. Action: read a play per pose at its worst side (proposal T6).
- **M5** (watch). Now priced, still not held: the verifier corrected the pad lever (12.29 -> 6.75 mm; the claim's seat test counted arm points up to 5 mm beside link 1b as over it, 25 of 133 crank samples truly over L1b) and wore the resulting 0.912-deg dwell K play as metal (v_gap 18.83). The hard pad fails the claim's own 0.25-deg dwell gate by 3.6x; for the wearer this is an unsensed knee coordinate that floats ~0.9 deg in dwell and pushes pose 203 (abduction 90 / external rotation 45, a raised-arm posture) 0.10 mm into the skin. The fix the row names (a preloaded or adjusted pad) adds drag or a part that is neither measured nor counted (complexity stays 16.5 with the pad as 0 parts). [evidence: docs/concepts/rows/lowarm-halfring-knuckle-3r.json verification_cellA.pad_true_lever, play_as_metal_true_lever] Why the exo is not better: an unsensed coordinate floats by 3.6x its own gate. Action: round 15 lens B's adjusted rigid pad, sampled and counted.
- **P1** (watch). Resolved as the headline, record still on file: cell B's in-sample 17.96 (min of 794 frozen-exact configs on the claim bench; held 22.70, behind the lead) is no longer the row's v_gap (now 18.83, cell A, pre-registered at ideation 2026-10-17T23:25:10Z) and the dashboard shows 18.83 (morphs.json 08:15). But the row's top-level 'verification' block (t 02:20) still reads bench gap 17.96, overhead 9/28, near1 20.14 for cell B with no superseded flag; a reader of that block gets the gamed number. [evidence: docs/concepts/rows/lowarm-halfring-knuckle-3r.json verification.bench vs verification_cellA] Why it matters: the gamed cell-B number is still printed in the row. Action: mark the 02:20 verification block superseded.
- **NEW-inherited-stack** (watch). Carried: the model execs desmo-conecut's _desmo_build_B with only the half-ring line patched (docs/concepts/models/lowarm-halfring-knuckle-3r.py lines 41-48), so the unbuildable stage-1 level formula and its glev box [-1.0, 1.5] (every value inside the plate) pass to the next round: ROUNDS.md round 15 lens B (lowarm-adjpad-knuckle-3r) pre-registers its pass bar as cell A's 18.28 at cx <= 17.0, a bar set on the clashing layer (18.65 at the nearest buildable level F+3.9, 19.05 with the true-lever play). [evidence: docs/concepts/ROUNDS.md lines 3644-3660] Why it matters: the next round's bar is set on the clashing layer. Action: name the level with the bar (proposal 4).
- **T1** (watch). Report only (user decision 3). Re-worn this audit (cell A, no play, model unchanged): bench plain 18.28, near-touch 1 / 2 / 3 mm 19.92 / 34.84 / 86.16, band read 3-14 mm 18.42, min metal 0.072 mm at pose 139 - identical to the lead (19.92 / 34.84 / 86.16, band3 18.34); held 22.64, near 25.49 / 37.12 / 82.96 vs the lead's 25.23 / 37.10 / 83.12. 16.56 bench points live in the 1-2 mm shell, as on the lead. Under the verified +0.912 play near1 is 20.46 and pose 203 goes from 0.263 mm to -0.102 mm; taken poses under 2 mm rise 33 -> 34. [evidence: docs/alignment/remeasure/lowarm-halfring-knuckle-3r_bench.json, _held.json, _kplay_perpose_A.json; remeasure/conecut-knee-knuckle-3r_{bench,held}.json] Report only.
- **S5** (watch). Carried: reach is continuous only through the envelope stepping stones: cell A connected_full 18.28 / 22.64 equals static, but the kNN flood (no stepping stones) reads 19.97 bench, 30.78 held (-8.14 held). [evidence: docs/concepts/verify/lowarm-halfring-knuckle-3r_vA_bench_frozen.json, _vA_held_frozen.json] Report only; the documented flood passes.
- **G4** (watch). Carried: the K sub-dyad margin m_sub at K rest is < 1 deg on 50 of 205 rest bench poses (min 0.0, p10 0.267, < 5 deg on 107), while the documented fold margin th is >= 5.181 (dwell 5.389; with the play 5.088). The K law is the same in cells A and B (only link 2's lift differs), so it applies to the claim. A near-singular sub-dyad at rest that the fold-margin check does not read. [evidence: docs/alignment/remeasure/lowarm-halfring-knuckle-3r_msub_rest_bench.json] Why it matters: a sub-dyad near its singular posture at rest is a feel risk the fold margin does not read. Action: report m_sub with th.

Resolved since the last audit, not carried: **R3** (best-of-794 without its spread) belonged to cell B's lift scan; cell
A's parameters were pre-registered and the 114-config fast LHS was flat (13.12-13.59). **R1** (cell A self-measured) is
resolved: the verifier reproduced 18.28 and held 22.64 and published 18.83. **S3** and **T5** were refuted by the
second skeptic and stay refuted: the pad is measured, and the summed contact depth is below the lead's under every play
side (16.16 / 16.23 / 18.13 mm vs 20.24).

## Numbers I could not get, and why

- **Held out with the play and with the buildable layer:** not run in the time box. Held at 22.64 is the unplayed,
  clashing config; the kplay script has no held path, and a held wear took 15 min at this load.
- **Workspace in-band (unscored) for cell A:** the cell-A dumps carry no per-pose in-band counts for workspace poses, and
  the wear probe (`tools/alignment_strparams_adapter.py probe`) would have been a third process. The cell-B probe stands in.
- **The tool's contact_depth check on the claim:** no dump that reproduces 18.83 sits at the path the tool reads. The
  per-pose play wear has the depths (table above); I did not overwrite the verifier's cell-A dump to feed the tool.
- **Cuff twist, pad drag, R17:** no CAD of this row.
- **Per-pose worst at the buildable level (play and layer together):** not run; the verifier's uniform +0.912 there reads 19.05.

## Proposals (not applied; none feeds the verdict)

1. **T6, a new catalogue entry: play read on one side.** A free play (a stop with clearance, a slot, a groove) is worn
   pose by pose at its worst side, not as one uniform offset. Measured effect: this row 18.83 -> 18.89 (the per-pose worst of +/-0.912, `remeasure/lowarm-halfring-knuckle-3r_kplay_perpose_A.json`). Other verified
   rows: none wears a play as metal today (the lead's groove play is unworn), so no other row moves.
2. **One ruling for the stage-1 layer across the family.** The same clash is ledgered gamed here and watch on
   desmo-slipper (18.95, +1.43 at F+3.9) and desmo-conecut (18.98, +1.52). Either every verified number that carries an
   unapplied, measured clash is published at its buildable level (this row 19.05, desmo-slipper 20.38, desmo-conecut
   20.50), or the lead rules that the layer is deferred to CAD for all three. Effect on the board: this row drops behind
   sidecar-longdyad (18.91); the two desmo rows drop behind sidecar-parallelogram (19.13) and sidecar-roller-flank (20.08),
   still ahead of kneeless-roller (21.07).
3. **Superseded verification blocks get a flag.** The row's top-level `verification` block (cell B, 17.96) has no
   superseded marker next to `verification_cellA`. Effect: reporting only; no number moves.
4. **Round 15 lens B's pass bar** (cell A's 18.28 at cx <= 17.0) should name its level: 18.65 at the buildable stage-1
   level, 19.05 with the true-lever play.

Next: the lead records a ruling on M3 (publish 19.05, or defer the layer to CAD for the family); round 15 lens B
(lowarm-adjpad) carries the level and the per-pose play rule into its claim.

---

_Below: the skeptic sections of the previous audits (2026-10-18 07:37-07:46 and 02:50-03:01 UTC), kept unchanged. Their
rulings refer to the earlier findings (ledger 2026-10-18T07:34:11Z and 02:43:22Z)._

## Skeptic (2026-10-18, 08:38-08:53 UTC), third audit

This skeptic ruled on the third audit (ledger 2026-10-18T08:35:49Z, claim v_gap 18.83, cell A). Method: every number re-read from the rawest file on disk, and two re-derivations.
- Re-run, model unchanged, local, niced, 1 process: `tools/alignment_lowarm_s1level.py geom --cell A`.
- Recomputed from the per-pose rows: the play wear and the per-part in-band at the kit's density.
- Rulings: `docs/alignment/lowarm-halfring-knuckle-3r.rulings.json`. Ledger: 2026-10-18T08:52:57Z, run `skeptic:lowarm-halfring-knuckle-3r`.

**Final verdict (ledger tool): GAMED.** M3 is upheld. 3 reasons are refuted with evidence (NEW-one-sided-play, P1, T1). 6 are upheld (continuity, M3, M5, NEW-inherited-stack, S5, G4).

### Rulings

- **continuity: upheld (watch).**
  - Held (`_vA_held_frozen.json:connected`): static 22.64, full 22.64, kNN 30.78, bench 23.81.
  - Bench: full 18.28, kNN 19.97, bench graph 50.13.
  - The tool's rule (`c_continuity` lines 500-505: rule flood ok, then watch on a kNN loss > 3) reads the right numbers.
  - Context: the lead reads the same on the bench (kNN 19.97 / bench 50.13, `conecut-knee-knuckle-3r_v_bench_frozen.json`), so the pattern is shared and not row-specific.
- **M3: upheld (gamed).**
  - I re-ran the geom on cell A (4.7 s). Groove layer and pin band are at F+0.111..1.611, pin radius 9.602 mm, inside link 1b's lower member F+0..3.0 under the O20 hub (r 10, `concept_kit.py` line 24). The clash is on the claimed config itself.
  - The verifier's buildable numbers are on file (`vA_padplay.json:kplay_true_lever_stage1_F39`): recomputed 18.66 without play and 19.05 with it. v_gap stays 18.83.
  - **Attempted refutation, not sufficient.** I re-weighted the two cell-A `claim_frozen_out.parts_ib14` records to the kit's density (horn /2.519, ring2 /3.957).
    - Without play: clashing ~18.31, buildable ~18.42. The layer costs **+0.11 at kit density**, against +0.37 as sampled.
    - With play: per-part counts are not on file. Carrying the same deltas over puts buildable+play at in-band ~0.900, about 18.83, which would remove the rank flip over sidecar-longdyad (18.91, no flagged parts).
  - That is an estimate, and S6 never changes the gap. Two real envelopes in one volume in the verified config is the fact, so the finding stands.
- **NEW-one-sided-play: refuted.**
  - The measurement is right. I recomputed the per-pose worst three ways from `_kplay_perpose_A.json:sides`: the auditor's composite, the per-pose minimum in-band, and a coherent one-side-per-pose pick. All three read **18.89**, and the two sides reproduce 18.83 / 18.35.
  - But there is no documented rule. ALIGNMENT.md has no T6 and no play-reading rule, and the auditor's own .md files T6 under "Proposals (none feeds the verdict)".
  - The row's "worst side" was applied as the worse uniform side, a valid reading under the current protocol. Under the brief, a proposed tightening never feeds the verdict.
  - It moves to proposal T6 with its effect: +0.06, no rank change.
- **M5: upheld (watch).** All values are in `padcheck.P1_pad_seat`.
  - True lever 6.75 mm (25 of 133 crank samples truly over L1b); K play 0.912 deg against the row's own gate of 0.25 (3.65x, ok false).
  - The play is priced as metal at pose 203 (-0.102 mm).
  - The drag of a preloaded or adjusted fix is not on file.
- **P1: refuted.**
  - The claim is cell A, not the in-sample cell B scan pick. Held-out drop is +3.81, under the documented watch at > 6 (`checks.held_out`).
  - The row marks cell B superseded (`cells.B.note`: "moved out of the headline by the 07:40 re-verification"), and the dashboard verdict reads "Cell B stays GAMED (P1)". The tool's `reporting` check is ok.
  - What is left is an unflagged legacy block. It is a label with no wearer cost; proposal 3 (flag it) stands.
- **NEW-inherited-stack: upheld (watch).**
  - Model lines 43-48 exec desmo-conecut's `_desmo_build_B` with one line replaced, and the cell-A geom re-run confirms the layer.
  - ROUNDS.md lens B names no stage-1 level check. Its A0L reference (desmo-conecut 18.37, "inside hub 2's O20") sits on the same layer.
  - Nuance: 18.28 is also the lead's number.
- **T1: refuted.**
  - The numbers reproduce (`checks.near_touch` 19.92 / 34.84 / 86.16, shell2 16.56).
  - The documented level is report-only: user decision 3, and `c_near_touch` lines 279-281 keep it ok.
  - The row is identical to the lead (dominance +0.00 / +0.00). The play's one shift (pose 203) is already a scored contact in v_gap.
- **S5: upheld (watch).** Same records as continuity. It is shared with the lead on the bench, and nothing on file shows the kNN drops reachable.
- **G4: upheld (watch).**
  - m_sub at K rest: min 0.0, under 1 deg on 50 of 205 poses. With K moved its min is 10.8, and the documented th at rest has a min of 5.389.
  - The probe ran on cell B (`params_source` CELL_B, l2_lift 1.5). The carry to cell A is inferred from identical K parameters, not re-worn (a 9-min exact wear).

### Missed by the auditor (for the next audit; not in this verdict)

1. **The `density` check reads the old claim.** `remeasure/sample_density_lowarm-halfring-knuckle-3r.json:bench.file` is `_v_bench_frozen.json` (cell B, 17.96), so the tool's density line ("17.96 -> 18.04") describes cell B, not v_gap 18.83.
   - Cell A at kit density (this skeptic's re-weight): 18.28 -> ~18.31 without play; buildable 18.65 -> ~18.42.
   - Action: run `tools/sample_density.py measure` on cell A, with the play wears' per-part counts.
2. **The kplay script's dwell flag is unreliable.** `PLAY["dwell_idx"]` is set inside `_ik_phys` (line 70) to the indices of the last call's batch, so the named and contact records read `dwell: false` on every pose.
   - Pose 203 is one of them, yet it moves 0.263 -> -0.102 / 1.083 mm under +/-0.912 (`vA_padplay.json:kplay_true_lever.*.named.203`). The script plays only dwell poses.
   - Contact lists that say `dwell: false` therefore do not show which contacts the play caused.
3. **The M3 rank clause is density-sensitive in the other direction too.** The published 18.83 includes the over-dense horn (2.52x, in-band 0.949), which deflates the gap.
   - The rank comparison with sidecar-longdyad (no flagged parts) is not like for like at the sampled density.
   - At kit density both the clashing and the buildable cell A sit about 18.83 against 18.91 (estimate, see M3). The flip the auditor cites exists only at the sampled density.

### Proposals carried

- **T6 (from NEW-one-sided-play):** wear a free play per pose at its worst side.
  - Effect: this row 18.83 -> 18.89 (measured three ways).
  - No other verified row wears a play as metal today, so no other row moves.
- **S-2:** re-run the density instrument on every row whose claim moved after its density file was written (today: this row) before the density check is read.

Final verdict: **GAMED** (M3: the verified config puts stage 1 inside link 1b's J2 plate; the buildable 19.05 is measured and unapplied). Next: the lead rules once for the family's stage-1 layer (this row, desmo-slipper, desmo-conecut), and the density instrument is re-run on cell A.

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
