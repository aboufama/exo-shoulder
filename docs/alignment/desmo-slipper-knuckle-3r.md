# Alignment audit: desmo-slipper-knuckle-3r

This is the hourly re-audit, run 2026-10-18 22:30-23:00 UTC on the box (local only, niced, OMP_NUM_THREADS=1, at most 2
processes of mine; the farm budget line is spent, so $0 was spent). What triggered it: commit ea9371b (07:42, the lead's
density audit) came after the last audit (06:26, WATCH). It wrote a new, lower number on the row, 18.81 bench / 23.77
held at the kit's sampling density, next to v_gap 18.95, and HANDOFF said the exact re-wear was still pending. Reference:
the verified lead conecut-knee-knuckle-3r (18.28). Tool VERSION 2026-10-18.1. This text replaces the 06:18 audit's
auditor sections; its measurements that still stand are carried below. The skeptic sections are kept below the rule.

## Verdict and claim

- **Claim:** v_gap **18.95** (score 93.11), unchanged. This is the verifier's frozen exact Bench(110,360) at the
  re-placed stage-1 pin (a_s 9.5, psi 150, glev -0.5), with the blended-law IK. Held out 23.90.
- **The new number on the row is now measured exact.** At the kit's density (1 sample per 4 mm2) the claim reads
  **18.85 bench / 23.81 held**. The re-weight on the row said 18.81 / 23.77, so it holds to 0.04.
  - The documented confirmation command (`tools/sample_density.py rewear`) crashes before any wear, so no exact
    reading existed before this audit.
  - I re-wore it through the verifier's own harness with a new adapter, `tools/alignment_density_rewear_desmo.py`.
- **Ledger verdict: WATCH** (entry 2026-10-18T22:54:26Z, by auditor, run `audit:desmo-slipper-knuckle-3r`). The tool
  gives watch on `density` (S6) and `reporting`. The judgement pass adds 11 findings, all watch, for 13 reason items.
  No finding is gamed.
- **In one line:** the density change is a fairer reading of the same metal, worth 0.10 here. It does not make the exo
  better and does not change the rank. It does shrink the measured cost of the unbuildable stage 1:
  - at the plate-clearing level the row reads **19.21 bench / 24.17 held** at the kit's density;
  - that is a lift of **+0.36 / +0.36**, not the +1.43 / +1.43 the 06:18 audit measured as sampled;
  - the stage 1 at the verified level still cannot be built, and no buildable stage 1 is verified.

## What was measured in this audit

### (1) The density re-weight, worn exact

The instrument is the new file `tools/alignment_density_rewear_desmo.py`.
- It loads the verifier (`docs/concepts/verify/desmo-slipper-knuckle-3r.py`, `--blend`) through the 06:18 audit's
  unchanged `tools/alignment_desmo_slipper_s1level.py`.
- It thins roller, horn and ring2 with `tools/sample_density.py`'s own `_thin` (a greedy 2 mm Poisson disc). The thin
  happens on the Frozen wear model, right after it copies the fitted shape and before any pose is scored.
- The fit itself runs unthinned. The model, verifier and bench run unchanged.

Why a new file was needed: `CB_EXACT=1 python3 tools/sample_density.py rewear desmo-slipper-knuckle-3r bench|held`
crashes before any wear, on both wears.
- The error is `TypeError: _thin() takes from 2 to 3 positional arguments but 4 were given`. `fitted()` (line 146)
  passes `thin = (names, step, wear)` through `*thin`.
- On held, its Bench patch would also fire on the polish file's `Bench(20, 20)`, not on the fit bench.

Source files: `remeasure/desmo-slipper-knuckle-3r_density_rewear_{bench,held}.json` (thin_at truncate, a_s 9.5 /
psi 150). The control is `verify/desmo-slipper-knuckle-3r_v_{bench,held}_frozen_fix.json`.

| | bench, as sampled | bench, kit density (exact) | held, as sampled | held, kit density (exact) |
|---|---|---|---|---|
| gap | 18.95 | **18.85** | 23.90 | **23.81** |
| re-weight on the row | - | 18.81 | - | 23.77 |
| in-band 2-14 (clip frames) | 0.8909 | 0.8919 | 0.8898 | 0.8907 |
| reach / follow / contact | 0.725 / 1.0 / 0.0054 | same | 0.6828 / 1.0 / 0.0116 | same |
| losses (fold / slide / contact) | 88 / 9 / 2 | same | 260 / 32 / 10 | same |
| near-touch 1 / 2 mm (gap; poses) | 20.58 / 33.45; 3 / 30 | 20.48 / 33.27; 3 / 30 | 26.99 / 37.47; 14 / 67 | 26.90 / 37.31; 14 / 67 |
| samples roller / horn / ring2 | 19 / 61 / 19 | 3 / 16 / 7 | 19 / 61 / 19 | 3 / 16 / 7 |

- The fast fit is the control's exactly (13.53).
- Every unthinned part's in-band, the contact poses (237 at -9.0 mm, 264 at -5.72 mm) and the overhead taken count
  (8 / 28) equal the control's.
- So the 0.10 comes from the weighting alone. The ring2 sector (0.54 in band) lost its 4x weight, and the well-placed
  horn and roller (0.95 / 0.94) lost their extra weight the other way.
- The 2 mm Poisson disc keeps fewer horn and roller samples (16 / 3) than the re-weight's n / ratio (27.1 / 4.3), so
  the exact reading sits 0.04 above the re-weight.

**A trap I fell into, and caught.** My first exact run took the verifier's `BEST`, which is the row's `best_params`:
the REFUTED claim placement 9.25 / 154. It read 18.77 thinned, with ring2 at 9 samples instead of 19. I caught it only
by comparing ring2 counts with the control, then discarded it and re-ran at 9.5 / 150. The adapter now defaults to
`verification.verified_config` (finding NEW-refuted-best-params).

### (2) The plate-clearing level at the kit's density

This uses the same adapter with `--glev 2.0497 --set a_s=9.8 --set psi=150`: the 06:18 audit's nearest plate-clearing
level, F+3.9, and its re-placed pin. Source files: `remeasure/desmo-slipper-knuckle-3r_density_rewear_s1level3p9_{bench,held}.json`.

| | verified level (F+1.35) | plate-clearing (F+3.9) | lift |
|---|---|---|---|
| bench, as sampled | 18.95 | 20.38 | +1.43 |
| bench, kit density (exact) | 18.85 | **19.21** | **+0.36** |
| held, as sampled | 23.90 | 25.33 | +1.43 |
| held, kit density (exact) | 23.81 | **24.17** | **+0.36** |
| ring2 samples (as sampled -> kit), in band, median | 19 -> 7, 0.54, 13.8 mm | 29 -> 8, 0.18, 16.3 mm | |
| near-touch 1 / 2 mm, bench, kit density | 20.48 / 33.27 | 20.84 / 33.65 | |

- The fit at F+3.9 equals the 06:18 control's (fast 14.94, dK_lim 49.5). Only the three thinned parts differ.
- The metal did not move between the two readings. The raised ring is still 0.18 in band at a median of 16.3 mm. As
  sampled, its 29 samples at 1 per mm2 counted 4x.
- At the kit's density the lift is +0.36. That sits inside the lead's "+0.31..0.44" for desmo-conecut.

## What the wearer gets (measured)

All figures are on the frozen verified config, as sampled, unless a column says otherwise. The pose counts are
geometric: the density change moves no pose. Sources: the per-pose dumps
`remeasure/desmo-slipper-knuckle-3r_{bench,held}_perpose.json` (re-counted this audit) and
`_s1level3p9_{bench,held}_perpose.json`, plus `remeasure/desmo-slipper-knuckle-3r_probe_bench.json`. Counts of taken
poses use 0 <= min metal < x.

| | bench, verified level | bench, F+3.9 | held, verified | held, F+3.9 |
|---|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | 8 / 28 | 18 / 71 | 18 / 71 |
| raised-arm reach (elev >= 90) | 46 / 113 | 46 / 113 | 114 / 300 | 114 / 300 |
| taken poses with metal < 1 / 2 / 3 mm | 2 / 27 / 96 | 2 / 28 / 96 | 14 / 64 / 191 | 14 / 66 / 190 |
| taken overhead poses < 2 mm | 2 | 3 | 8 | 8 |
| closest taken metal | 0.072 mm | 0.072 mm | 0.33 mm | 0.33 mm |
| contact poses, summed depth, deepest | 2, 14.72 mm, 9.01 mm at (15, 165, -60): crank / lug | same | 10, 46.14 mm, 9.05 mm at (30, 165, -45) | same |
| clip in-band 2-14, as sampled / kit density | 0.8909 / 0.8919 | 0.8766 / 0.8883 | 0.8898 / 0.8907 | 0.8755 / 0.8871 |
| workspace in-band, all taken / elev 90-140 / overhead (unscored) | 0.853 / 0.801 / 0.938 | not probed | - | - |

- **Springs:** none. K is held both ways, by the groove (stage 1) and the two-walled slot (stage 2).
- **Stops:** the drive range ends at K 49.5 (the stage-2 horn's pressure angle) at both levels. J2 fold losses are 88
  bench / 260 held.
- **Friction:** the drive jams from mu 0.136 on the linear reading at the verified level, and from mu 0.128 at F+3.9.
  The lead's rolling stage 1 keeps its drive at mu 0.15.
- **Cuff twist / K play:** crank-free play is 0.174 deg (the verifier's dense scan reads 0.188). Cuff twist and drag
  are not measured, because no CAD of this row exists (G3).
- **Near-singular postures:** the min fold margin in th is 5.181 bench and 5.006 held, with K on its law. K play costs
  about 0.1 deg of that (T3).

## Findings (all watch; `docs/alignment/desmo-slipper-knuckle-3r.findings.json`)

1. **S6, the new number.**
   - *Evidence:* section (1). The re-weight 18.81 / 23.77 is confirmed exact at 18.85 / 23.81. The documented
     confirmation command crashes.
   - *Why the exo is not better:* no metal moved. The kit-density reading weights the same metal by area instead of
     by sampler pitch.
   - *Why watch, not gamed:* v_gap stays 18.95. The change is cross-row and was not made with this design. At the
     kit's density the row stays behind:

     | row | bench | held |
     |---|---|---|
     | conecut-knee (lead) | 18.28 | 22.43 |
     | slipper-nose | 18.56 | 23.52 |
     | trimlug | 18.58 | 23.54 |
     | desmo-conecut (re-weight) | 18.68 | 22.89 |

   - *Action:* put the exact pair on the row next to v_gap. Fix `sample_density.py rewear`.
2. **M3, carried; magnitude corrected.**
   - *Still true:* stage 1 sits inside link 1b's J2 plate, and the verified pin is dead at F+3.9.
   - *Corrected:* the buildable reading is 19.21 / 24.17 at the kit's density, a lift of +0.36 / +0.36. Most of the
     06:18 audit's +1.43 was the 4x ring2 sampler.
   - *Rank at the kit's density:* 0.08 behind sidecar-parallelogram (19.13) and ahead of sidecar-roller-flank (20.15)
     on the bench; behind both held out (22.03 / 22.42). Not the leader under any reading.
   - *Why the exo is not better:* the 18.95 belongs to a drive that cannot be built.
   - *Action:* re-claim at a buildable level with the radius gate enforced, and carry the plate-clearing reading in
     both conventions.
3. **NEW-inherited-stack (proposed M6), carried.**
   - The level formula (model line 148) and the box (line 87) are this model's. desmo-conecut and lowarm-halfring
     inherit them.
   - The row's note now names the source correctly.
4. **NEW-friction-cliff, carried.** The drive jams from mu 0.136 (0.128 at F+3.9). The score reads one mu (0.087).
5. **NEW-silent-check, carried.** RC_MIN 1.5 never cuts. The 06:27 skeptic's missed[1] is added: enforced as declared,
   the gate would cut the verified claim itself (rc_min 0.90, lim_by_gate.radius 0.5 deg). The physical floor
   (0.75) passes, with a 0.14 mm ridge that has no stress number.
6. **NEW-refuted-best-params, carried; it bit this audit.** best_params is still 9.25 / 154. It is the third instrument
   that silently wears the refuted placement.
7. **R1, partly fixed.**
   - *Fixed:* the row now records the plate-clearing numbers, names the source correctly, and gives the verified
     paired reading ahead of the "HISTORICAL TEXT" (the skeptic's missed[0]).
   - *Open:* the verdict pairs 20.38 / 25.33 (as sampled) with 18.81 / 23.77 (kit density, re-weight). Subtracting
     them suggests a 1.57 cost; the like-for-like cost is +1.43 as sampled or +0.36 at the kit's density.
8. **R2 (tool reporting), carried.** The dashboard's sweep best of 12.79 (score 95.35) sits 6.16 below the verified
   number.
9. **T3, carried.** The held fold margin is 5.006 deg, with K on its law. No per-pose margin with K play is on file.
10. **NEW-ws-inband, carried.** The raised-arm workspace reads 0.801 in band (unscored). That is not a ring2 sampling
    artefact.
11. **G3, carried.** There is still no CAD, R17, cuff-twist or drag reading for this row (re-checked 22:50).

T5 is dropped. The 06:27 skeptic refuted it against the documented reference (the current lead: x0.73 bench / x0.76
held), and the tool's contact_depth check reads ok.

## Patterns walked and found clean

- **T1 / T2:** 14.4 points live in the 1-2 mm shell at the kit's density (33.27 - 18.85) and 14.5 as sampled. Both are
  under the 15-point line.
- **T4:** blend 10 sits at its box edge. It spends groove radius, not a fold margin (NEW-silent-check).
- **S1 / P1:** held is +4.96 at the kit's density and +4.95 as sampled, the family's usual gap.
- **S2:** sample-weighted 0.890 vs part-weighted 0.898. **S3:** every moving body is sampled.
- **S4:** the standard bench sample. **S5:** the full flood equals static (18.95).
- **M1 / M2:** O20 hubs, 0 passive translations, ISO 8734 pins, an MR63ZZ crank pair. **M4:** K moves 45.6 deg.
  **M5:** no spring.
- **P2:** the F+3.9 pin was picked on fast only, before any held wear. **P3 / R3:** convergence gate 0/0/0. Both
  re-wears here reproduce the control on every unthinned term. The discarded run was at the wrong placement, not a
  re-roll.
- **P4:** no bench, judge or metric file changed in the row's 7 commits. The density tool is new and cross-row, and it
  changes no v_gap.
- **R4:** the dashboard's v_gap 18.95 equals the row's and recomputes from its own terms (0.91 in-band + 17.50
  reach + 0.54 contact). The kit-density reading is not on the dashboard as a number.
- **G1 / G2:** no spring. **G4:** same seats as the lead. **G5 / G6:** complexity 15.75 recomputed, 3 active DOF.

## Re-wear rule (step 2)

The row's last commit (ea9371b, 07:42) changed only its verdict text: the density note. The claim, best_params and
verification are unchanged, so `tools/alignment_audit.py remeasure` was not re-run. The existing
`remeasure/desmo-slipper-knuckle-3r_{bench,held}.json` (19.00 / 23.95 on the model's linear IK) stand. The new number
on the row is the density reading, and that was re-worn exact, at both levels, bench and held (sections 1 and 2).

## Numbers I could not get, and why

- **The real relief that the ring sector would sweep in link 1b:** no CAD of this row exists.
- **Strap clearance:** the model has no link 1b strap samples near J2.
- **A wider pin scan above link 1b** (F+4.6 / F+6.15) and an exact wear there: time box.
- **The workspace wear probe at F+3.9 and at the kit's density:** time box.
- **Cuff twist and drag:** no CAD.
- **Exact kit-density readings of the rows this one is ranked against:** they are re-weights from
  `docs/alignment/sample_density.md`. conecut-knee's roller is 4.55x, for example. I did not wear them.

## Proposals (not applied; none feeds the verdict)

1. **Fix `tools/sample_density.py rewear` (instrument fix).**
   - Pass `(names, step)` to `_thin`. Detect the fit bench by size or call order, not as "the first Bench".
   - Thin on the Frozen model after it copies the fit, not before the fit runs.
   - Then run it on every row the table re-weights.
   - Measured effect: here, bench 18.81 -> 18.85 and held 23.77 -> 23.81 (re-weight -> exact). No rank change.
2. **One convention per sentence on rows (reporting).**
   - When a measurement change is pending, a row shows each reading in the same convention as the number it is compared
     with.
   - Here: as sampled 18.95 -> 20.38 / 23.90 -> 25.33; kit density 18.85 -> 19.21 / 23.81 -> 24.17.
3. **Family level fix (carried; a measurement change).** Measure stage 1's level from hub 2's face, re-base the glev box
   above F+3.15, and enforce the radius gate. Measured effect on this row: 18.95 -> 20.38 as sampled, or 18.85 -> 19.21
   at the kit's density. desmo-conecut's is in its own audit.
4. **best_params = the verified placement (reporting).** Keep the claim's 9.25 / 154 in a `claim_params` field.
   Measured effect: none on any number. Three instruments, this audit's adapter among them, stop landing on the refuted
   placement.

---

*Earlier skeptic section (2026-10-17), kept as written; it rules on the first audit's findings.*

## Skeptic (2026-10-17 ~17:55 UTC, skeptic:desmo-slipper-knuckle-3r)

Final verdict (tools/alignment_ledger.py skeptic): **WATCH**. 0 of 9 reasons refuted; all upheld with re-derived
numbers. Rulings: `docs/alignment/desmo-slipper-knuckle-3r.rulings.json`. New raw material:
`docs/alignment/remeasure/desmo-slipper-knuckle-3r_skeptic_mu_blend.json` (my mu re-runs and the blended-groove
probe), tool `tools/alignment_skeptic_blend_pa.py` (new file; the model is unchanged, its `_desmo_build` is re-run in
memory with one read-only block). Local only, niced, OMP_NUM_THREADS=1, at most 2 processes. No farm.

| key | ruling | evidence |
|---|---|---|
| reporting | upheld | morphs.json: sweep_gap 12.79, v_gap 18.95. The gap of 6.16 is over the documented trigger (sg < vg - 5). |
| NEW-friction-cliff | upheld | Re-run with the model unchanged at the verified placement. mu 0.135: dK_lim 44.5, plain 14.84, gate 35.31. mu 0.14: dK_lim 0 (s1-pa-cap), plain 86.71, reach 0.344, follow 0.65. Lead at mu 0.15: fit_fast 14.88. The cliff's location is a reading artifact (see missed[0]), but the exposure is wider than the audit says, not narrower. |
| NEW-silent-check | upheld | The cut list `gates` in `_desmo_build` holds pitch, pa-pin, pa-cap and drift. `radius` appears only in `lim_by_gate`. Re-run: rc_onset 0.99, lim_by_gate.radius 0.5 deg. Ridge 0.99 - 0.76 = 0.23 mm. blend 10.0 is the `_clamp` bound. |
| NEW-refuted-best-params | upheld | Row best_params is a_s 9.25 / psi 154 (gap 13.19); verified_config is 9.5 / 150. The per-pose dumps behind 18.95 carry 9.5 / 150. |
| R2 | upheld | sweep k 128: 12.79 at 9.2141 / 152.944. Only the sparse slop reading (0.22) is on file. The dense-wall convention is -0.31 (row fast.dense_wall_sweep_convention). Paired: +0.46 bench / +0.45 held, p 0.0. |
| T3 | upheld (missing measurement) | Held th min 5.006, bench 5.181. No per-pose fold margin with K offset by its play is on file; I did not measure one. |
| M3 | upheld (missing measurement) | l2_check keeps only rr > HUB_R + 1.5. No L1/L2 CAD of this design exists. |
| T5 | upheld | My own sum over the dumps: bench 9.005 + 5.718 = 14.72 mm; held 10 contacts, 46.14 mm. Against the tool's DEPTH_REF sidecar-longdyad (6.23 mm): x2.36 and +8.49, over both TH limits. The lead's skeptic made the same ruling. |
| NEW-ws-inband | upheld | probe_bench (9.5 / 150, exact 19.0): ws elev 90-140 in-band 0.8009, over14 0.1983, p95 19.98. Lead: 0.8004 / 0.1987. Clip: 0.8904. |

### Missed (for the next audit; not counted in this verdict)

0. **The stage-1 pressure-angle gate reads a groove the design does not build.**
   * What the model gates: `paC` and `paF` (`43 - atan(mu)`, per K step) are computed on the linear K law over
     `kgrid`, K >= 0.
   * What the model builds and samples: a groove whose onset is blended over 10 deg of q2 (`Kb`, half-width 10.77 deg
     of K).
   * Measured on the built groove (verified placement, mu 0.087; `tools/alignment_skeptic_blend_pa.py`):
     * The cap-side angle is 89.19 deg at K 0.003, 57.1 at K 3.8, 41.8 at K 7.2 and 29.37 at the end of the blend.
     * It stays above the claim-mu gate of 38.03 from K 0 to 8.11, and above 35.03 to K 8.58.
     * The 35.25 that the gate trips on sits at the linear law's K 0 corner, which the built groove does not have.
     * The pin-side (forward-drive) angle peaks at 30.94. That is under `43 - atan(mu)` up to mu 0.214, and up to
       0.25 on the judge's 45 rule.
   * Two readings follow, and neither leaves the claim as stated:
     * (a) The cap-side gate does not govern at a dwell exit, where a dwell locks back-drive by design. Then the audit's
       mu 0.136 cliff is an artifact, and the forward drive holds to about mu 0.21.
     * (b) The cap-side gate does govern. Then the built groove fails the model's own gate at the claim's mu 0.087,
       and the claim's dK_lim of 49.5 exists only because the gate reads the un-blended law. Enforced on the built
       geometry, the gate would cut dK_lim to about 0 at every mu.
   * Nobody has shown that the dwell exit transmits under friction on either load path: groove to pin, and horn/arm
     load through the pin to the cap.
   * Action: a static force analysis with friction through the blended onset, on both paths. The gate must be read on
     the built groove (`Kb`), not on the law.
   * This is the same class as NEW-silent-check: a declared per-step gate that is not applied to the geometry that is
     sampled and scored.

**Proposal (measurement change, not an input to this verdict):** evaluate every stage-1 gate (pressure angles and
centreline radius) on the built, blended groove. Measured effect on the one row it touches:
* Under reading (b), the cap-side gate cuts this row's dK_lim to 0 at every mu. The fast bench reads 86.71 at the
  verified placement, the same as the mu 0.14 run, where dK_lim is also 0.
* Under reading (a), the cap-side gate is dropped at the dwell exit and nothing moves.
* No other verified row has a blended stage-1 groove.

---

## Skeptic (2026-10-18 ~06:27 UTC, skeptic:desmo-slipper-knuckle-3r), on the 06:18 re-audit

Final verdict (`tools/alignment_ledger.py skeptic`, entry 2026-10-18T06:26:41Z): **WATCH**.
- Of the 12 reasons, 1 is refuted with evidence (T5) and 11 are upheld.
- Rulings: `docs/alignment/desmo-slipper-knuckle-3r.rulings.json`. They replace the 2026-10-17 file, whose rulings are
  kept in the section above.
- New raw material: `docs/alignment/remeasure/desmo-slipper-knuckle-3r_skeptic_s1level_geom.json`. It holds my re-run
  of the auditor's `geom` mode, with the model, verifier and bench unchanged, at the verified level and at F+3.9 with
  the verified pin.
- Local only, niced, OMP_NUM_THREADS=1, 2 processes, about 10 s each. No farm.

### Re-measured

| what | auditor | my re-run / re-derivation |
|---|---|---|
| pivot under hub 2's face | -1.300 | -1.2997 |
| groove layer, pin band | F+0.60..2.10 | F+0.60..2.10, pin r 9.487 |
| short arm | F-1.75..+0.35 | F-1.748..+0.35 |
| verified pin at F+3.9 | pitch 10.074, dK_lim 0, fast 101.19 | the same (s1-pitch) |
| F+3.9 bench / held | 20.38 / 25.33 | 20.38 by hand from the frozen terms; dump 25.34 |
| contact depth, this row | 14.72 / 46.14 mm | 14.72 / 46.14 (my own sum over the dumps) |
| contact depth, conecut-knee (the current lead) | - | 20.24 / 60.97 mm (4 / 14 contacts) |

- **The face definition is the CAD's.** In `build_minarc_l1.py joints4`, F[2] = M.f[1] and C[2] = D.c[1].
- **Link 1b is J2's lower member.** See `user_style_desmo.py` line 142 and `tools/concept_kit.py` line 24.

### Rulings

| key | ruling | evidence (short; the full text is in the rulings file) |
|---|---|---|
| reporting | upheld | `morphs.json`: sweep_gap 12.79 vs v_gap 18.95. The difference, 6.16, is over the documented sg < vg - 5. |
| M3 | upheld | Re-measured as in the table above, with the same harness and frozen protocol on both sides. The +1.43 is a lower bound: at F+3.9 the short arm still runs F+0.80..2.90, inside the plate, and at F+6.15 0 of 11 pins held. |
| NEW-inherited-stack | upheld | The formula (line 148) and the box (line 87) belong to this model, created in 8d483b1 at 15:28. desmo-conecut came later (171b169, 19:36) and loads this file (line 53, copied at line 182). lowarm-halfring loads desmo-conecut at glev -1.0. The row note reverses the direction. lowarm-halfring is already `gamed` in the ledger (03:00:45Z). |
| NEW-friction-cliff | upheld | pa_cap_max 35.73 at F+3.9 (9.8/150): tan(7.27) = 0.128. At the verified level, 35.25 gives 0.136. Missed[0] from the 2026-10-17 skeptic is still open (no friction force analysis through the built blended onset). |
| NEW-silent-check | upheld | The cut list (line 182) holds pitch, pa-pin, pa-cap and drift, while the radius check appears only in lim_by_gate (line 286). Re-run at the verified placement: rc_min 0.90, lim_by_gate.radius 0.5 deg against the dK_lim of 49.5 actually used. |
| NEW-refuted-best-params | upheld | best_params is 9.25/154 (13.19), but verified_config is 9.5/150. The scan's 3.9/9.25/154 row has rc 0.51. |
| R1 | upheld | The verdict reads "Unmeasured on this row", but the audit measured 20.38 / 25.33. The same field still carries the screen's self-claim ("paired TIE with the lead ... 18.63"). |
| R2 | upheld | Sweep best 12.79 rests on the dense-wall convention (-0.31) and a placement with only a sparse slop reading. Both dense scans on file nearby fail. |
| T3 | upheld (missing measurement) | Held th min 5.006 (n 852, lt5 0) against TH 5.0. No per-pose margin with K play is on file. |
| **T5** | **refuted** | The documented reference is the current lead (DEPTH_REF = conecut-knee, line 301; ALIGNMENT.md section 6, change 2026-10-17.5). Against it this row reads x0.73 bench (14.72 vs 20.24 mm) and x0.76 held (46.14 vs 60.97), with excess -5.52 / -14.83 mm. Neither TH depth_ratio 2.0 nor depth_floor 5 mm is met, and the tool's own contact_depth check reads ok. The audit's x2.36 is against sidecar-longdyad. That is RULINGS_DEPTH_REF, a selftest replay reference that the 2026-10-17.5 change retired as the live reference. |
| NEW-ws-inband | upheld | Raised-arm in-band 0.8009 (over 14 mm: 0.198, max 30.8 mm). Against the CURRENT lead (conecut-knee probe: 0.8315 raised, 0.9012 scored) the unscored deficit is 3.06 points and the scored one 1.08, so the score under-reads this design's raised-arm cost. |
| G3 | upheld (missing measurement) | No desmo-slipper entry in `pipeline/full-exo/designs`; the row has no cad, judge, r17 or cuff_twist field. |

### Missed (for the next audit; not counted in this verdict)

0. **The verdict field still advertises a refuted self-claim as a tie with a former lead.** This is R1 in its
   documented form.
   * What the text says: after the lead note, `docs/concepts/rows/desmo-slipper-knuckle-3r.json` verdict (and
     `morphs.json`) reads "paired TIE with the lead at lower complexity: frozen exact Bench(110,360) 18.63 vs the lead's
     18.49 ... held 23.59 vs 23.45".
   * Why 18.63 is wrong: it is the claim placement 9.25/154, which the verifier refuted on its own slop gate.
   * What the verified config measures: paired against the same slipper-nose, it is worse, not tied.
     `remeasure/desmo-slipper-knuckle-3r_vs_slipper-nose-knuckle-3r_paired.json` gives bench diff +0.46 (ci90 0.0..0.56,
     p_A_better 0.0) and held +0.45 (p_A_better 0.0).
   * Why "the lead" is wrong: slipper-nose is no longer the lead; conecut-knee (18.28) is.
   * Action: replace the screen text with the verified paired reading.
1. **The declared radius gate would cut the verified claim itself, not only re-placed pins.**
   * Measured at the verified placement: rc_min 0.90, and lim_by_gate.radius is 0.5 deg (my re-run). Enforced as the
     docstring states (lines 13-16), the gate cuts dK_lim to about 0.5.
   * Expected effect: on this chain a gate that cuts dK_lim to 0 reads fast 101.19 (scan row 3.9/9.5/150). So the 18.95
     exists only because the declared 1.5 floor is silent. I did not run the gate-on wear; this is an inference from
     the same chain's dK_lim-0 reading.
   * The physical floor is the pin radius 0.75, which the verified placement passes (0.90). It leaves an inner-wall
     ridge of 0.90 - 0.76 = 0.14 mm radius under the drive load.
   * Missing: no contact-stress or wear number is on file for that ridge.
   * Action: decide which floor is the rule (1.5 declared, or 0.75 + a stated ridge), enforce it in the cut list, and
     re-claim.

**Proposal (measurement change, not an input to this verdict):** none new. The audit's family level fix and the 2026-10-17
skeptic's "gate on the built groove" proposal cover the open items.
