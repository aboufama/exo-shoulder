# Alignment audit: desmo-slipper-knuckle-3r

This is a re-audit, run 2026-10-18 06:04-06:20 UTC on the box (local only, niced, OMP_NUM_THREADS=1, at most 2
processes; the farm is closed, $0 spent). The hourly loop (06:04) triggered it after the desmo-conecut CAD-triggered
audit (8edc253) flagged that this design runs the same stage-1 level formula. Reference: conecut-knee-knuckle-3r, the
verified lead (18.28). Tool VERSION 2026-10-17.6. The first audit of this row (2026-10-17 17:20-17:50) is superseded by
this text; its skeptic section is kept below the rule.

## Verdict and claim

- **Claim:** v_gap **18.95** (score 93.11). This is the verifier's frozen exact Bench(110,360) at the re-placed stage-1
  pin (a_s 9.5, psi 150, glev -0.5), with the blended-law IK. Held out 23.90.
- **Ledger verdict: WATCH.** Entry 2026-10-18T06:18:28Z, by auditor, run `audit:desmo-slipper-knuckle-3r`.
  - The tool verdict is watch, on the reporting check alone (the dashboard's sweep best 12.79 sits 6.16 below the
    verified number).
  - The judgement pass adds 11 findings, all watch: M3, NEW-inherited-stack, NEW-friction-cliff, NEW-silent-check,
    NEW-refuted-best-params, R1, R2, T3, T5, NEW-ws-inband and G3.
  - That makes 12 reason items. No finding is gamed.
- **In one line:** the 18.95 reproduces exactly, but it belongs to a stage 1 that cannot be built. The groove, the pin
  and the short arm sit inside link 1b's J2 lower plate. At the nearest level that clears the plate, the verified pin
  no longer drives at all. The nearest pin that does drive and can be cut reads **20.38 bench (+1.43) and 25.33 held
  (+1.43)**, and that costs in-band only.
- **Rank:** at that level the design falls behind sidecar-parallelogram (19.13) and sidecar-roller-flank (20.08) on the
  plain gap and on held out. It stays not-the-leader either way, and those two rows are not shown better for the wearer
  (finding M3). Hence watch, not gamed.

## The task's two measurements

### (1) Where stage 1 sits against link 1b's J2 plate and strap

Measured with the model and the verifier unchanged, using `tools/alignment_desmo_slipper_s1level.py geom` (new file).
It runs the frozen protocol's fit model on fast Bench(60,160) with the verifier's `--blend` IK at the verified config.
All levels are along the J2 axis u2, over hub 2's face. The face is H2 = c2.u2 + f[1] = 62.044 mm, the CAD's own
definition (`user_style_desmo.py` H2 via `joints4`). The J2 axis passes through GH (offset 0.0).
Source: `docs/alignment/remeasure/desmo-slipper-knuckle-3r_s1level_scan_fast.json`, `measured_at_verified_config`.

| part | level over hub 2's face (mm) | radius from the J2 axis (mm) |
|---|---|---|
| crank pivot PV | **-1.300** (desmo-conecut: -1.289) | 16.02 |
| groove layer = ring samples (link 2 metal) | **0.60 .. 2.10** (mid 1.35) | ring 10 .. 11.05 sampled (rigid), the whole ring 1.6 .. 11.05 contact |
| stage-1 pin (O1.5) | 0.60 .. 2.10 | 9.49 (inside the O20 footprint) |
| short arm samples, root to pin | -1.75 .. +0.35 | 16.0 -> 9.5 |
| link 1b's J2 lower member (the plate) | **0 .. 3.0** (tools/concept_kit.py line 24) | 0 .. 10 |
| link 2's J2 member | from 3.15 | 0 .. 10 |

What the table shows:

- The whole stage 1 lies inside link 1b's plate layer. The groove ring is link 2 metal, and link 2 turns about u2
  against link 1b by q2. So the relief that link 1b would need is not the verifier's assumed "5 x 4 x 1.5 mm pocket"
  for the pin and arm. It would be an annular cut through the plate, spanning the 99.9-deg ring sector plus the J2
  travel. That cut is not measured here; the angle is from the model's `ring_az_deg`.
- **The box excludes every buildable level.** The level formula hmid = PV.u2 + 3.15 + glev (model line 148) treats
  the pivot as if it sat on the face, so the groove mid is F + 1.85 + glev. The box glev [-1.0, 1.5] (line 87)
  therefore puts the groove bottom at F+0.10 .. 2.60, inside the plate for every value. The search could never have
  found a buildable placement.
- **Link 1b's strap** is not sampled within 12 mm of the J2 axis in the model (`l1b_samples_r_le_12` n = 0), so the
  model holds no strap metal to read there. The desmo-conecut CAD found its strap crossed by 0.79-0.87 mm at the model
  level. No CAD of this design exists.

### (2) Re-wear at the nearest buildable level

The instrument applies glev AFTER the model's clamp; the verifier's own `wear()` is unchanged.

- **Control:** glev -0.5 at the verified pin reproduces **18.95 exactly** (`remeasure/desmo-slipper-knuckle-3r_s1level_control_bench.json`).
- **The level:** F+3.9, groove layer F+3.15 .. 4.65, glev 2.050. This is the nearest level that clears the plate top
  F+3.0 by the 0.15 running gap. It is the same criterion desmo-conecut's audit used, and the most lenient one: the
  short arm still runs F+0.74 .. 2.9, and the strap is not shown clear.

**The pin pick, on the fast bench, before any exact or held-out wear.** At F+3.9 the verified pin 9.5/150 is dead: its
pitch is 10.074, past R_HI 9.94, so the s1-pitch gate cuts dK_lim to 0 and the fast gap reads 101.19. Of 9 pins tried:

- 9.8/150 and 9.9/150 keep the drive with a groove centreline radius at or above the 0.75 pin radius. They read fast
  14.94, rc 0.95 / 0.94, crank-free play 0.169 deg, desmo_fail [], dK_lim 49.5.
- 9.7/152 and 9.8/152 read 14.21, but with rc 0.64, which is under the pin radius. That is the defect the verifier
  refuted the claim placement on, so they are excluded.
- The pick is 9.8/150, the same pin as desmo-conecut's F+3.9 candidate.

**Exact frozen at F+3.9, pin 9.8/150** (`remeasure/desmo-slipper-knuckle-3r_s1level3p9_{bench,held}.json` with
per-pose dumps; the dumps recompute to 20.38 / 25.34):

| | verified level (F+1.35) | plate-clearing level (F+3.9) | delta |
|---|---|---|---|
| bench gap | 18.95 | **20.38** | +1.43 |
| reach / follow / contact | 0.725 / 1.0 / 0.0054 | 0.725 / 1.0 / 0.0054 | 0 |
| in-band 2-14 (clip frames) | 0.8909 | 0.8766 | -0.0143 |
| ring sector samples, in band, median | 19, 0.54, 13.8 mm | 29, 0.175, 16.3 mm | the larger pin needs a larger ring, and it rides higher |
| held-out gap | 23.90 | **25.33** | +1.43 |
| near-touch 1 / 2 mm, bench | 20.58 / 33.45 | 22.01 / 34.96 | +1.4 / +1.5 |
| stage-1 pa_pin / pa_cap max (gate 38.03 at mu 0.087) | 33.94 / 35.25 | 31.61 / 35.73 | |

**Levels fully above link 1b** (fast only; `_s1level_scan_fast.json`):

- At F+4.6, 2 of 6 pins tried keep a cuttable groove: 10.1/151 (rc 0.83, dK_lim 48.0, fast 15.02) and 10.3/150
  (rc 1.05, dK_lim 45.25, fast 16.28).
- At F+6.15, the CAD's "all of stage 1 above link 1b" layout (`user_style_desmo.stage1_layout`), **0 of 11** pins tried
  keep the drive with rc >= 0.75. The drive-keeping ones have rc 0.20-0.54, and 3 of them fail groove-slop.
- The scan is not exhaustive. On what was tried, a truly buildable version of this drive costs +1.4 to +2.75 fast, or
  has no feasible pin.

## What the wearer gets (measured)

All figures are on the frozen verified config unless a column says otherwise. Sources: the per-pose dumps
`remeasure/desmo-slipper-knuckle-3r_{bench,held}_perpose.json` (the verifier's, 18.94 / 23.91) and
`_s1level3p9_{bench,held}_perpose.json` (this audit), plus `remeasure/desmo-slipper-knuckle-3r_probe_bench.json`.
Counts of taken poses use 0 <= min metal < x.

| | bench, verified level | bench, F+3.9 | held, verified | held, F+3.9 |
|---|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | 8 / 28 | 18 / 71 | 18 / 71 |
| raised-arm reach (elev >= 90) | 46 / 113 | 46 / 113 | 114 / 300 | 114 / 300 |
| taken poses with metal < 1 / 2 / 3 mm | 2 / 27 / 96 | 2 / 28 / 96 | 14 / 64 / 191 | 14 / 66 / 190 |
| taken overhead poses < 2 mm | 2 | 3 | 8 | 8 |
| closest taken metal | 0.072 mm | 0.072 mm | 0.33 mm | 0.33 mm |
| contact poses, summed depth, deepest | 2, 14.72 mm, 9.01 mm at (15, 165, -60): crank / lug | same | 10, 46.14 mm, 9.05 mm at (30, 165, -45) | same |
| workspace in-band, all taken / elev 90-140 / overhead (unscored) | 0.853 / 0.801 / 0.938 | not probed | - | - |

- **Springs:** none. K is held both ways, by the groove (stage 1) and the two-walled slot (stage 2).
- **Stops:** the slot's end cap is stop A. The drive range ends at K 49.5 (stage-2 horn pressure angle) at both
  levels. J2 fold losses: 88 bench / 260 held.
- **Friction:** the drive jams from mu 0.136 on the linear reading at the verified level, and from **mu 0.128** at F+3.9
  (pa_cap 35.73). The lead's rolling stage 1 keeps its drive at mu 0.15.
- **Cuff twist / K play:** crank-free play is 0.174 deg at the verified level and 0.169 at F+3.9 (the model's scan;
  the verifier's dense scan reads 0.188). Cuff twist and drag are not measured, because no CAD exists (G3).
- **Near-singular postures:** the min fold margin in th is 5.181 bench and 5.006 held, with K on its law. K play costs
  about 0.1 deg of that (T3).

## Findings (all watch; `docs/alignment/desmo-slipper-knuckle-3r.findings.json`)

1. **M3, measured now.**
   - *Evidence:* the clash and the re-wear above. The 18.95 sits at a stage-1 level inside link 1b's plate. The
     plate-clearing re-wear costs +1.43 bench and +1.43 held, all of it in-band; above link 1b there is no or a more
     costly pin.
   - *Why the exo is not better than its number:* the built drive must ride higher. It then puts the ring sector's
     metal further off the skin (median 16.3 mm), so the 1-cm band reads worse, and the drive jams at a lower friction.
   - *Why watch:* the design is not the leader before or after. The rows it would fall behind (sidecar-parallelogram
     19.13 / 22.03, sidecar-roller-flank 20.08 / 22.23) are much worse at 2 mm near-touch (50.14 / 46.82 vs 34.96), and
     their held numbers come from older harnesses.
   - *Action:* re-claim at a buildable level before any CAD.
2. **NEW-inherited-stack (proposed catalogue M6), seen from the source.**
   - *Evidence:* the formula (line 148) and the box (line 87) are this model's. desmo-conecut and, through it,
     lowarm-halfring (17.96, the plain-gap top row) inherit them. A second chain shows the same 1.30 mm pivot offset
     and the same ~1.4-1.5 point in-band cost.
   - *Reporting error:* the lead's note on this row says it "inherits desmo-conecut's" layer. It is the reverse.
   - *Action:* one fix in the family model, then re-claim the family's rows.
3. **NEW-friction-cliff (carried):** the jam friction moves from 0.136 to 0.128 at the buildable level.
4. **NEW-silent-check (carried):** RC_MIN 1.5 still never cuts. At the buildable levels, the pins that score best pass
   the model with rc 0.28-0.64, under the pin radius. A re-placement search needs the gate enforced first.
5. **NEW-refuted-best-params (carried):** best_params is still the refuted 9.25/154. At F+3.9 that pin keeps the drive
   but has rc 0.51.
6. **R1:** the row and the dashboard still show 18.95 with "unmeasured on this row". It is measured now.
7. **R2 (tool reporting):** the sweep best is 12.79 (score 95.35) against the verified 18.95.
8. **T3 (carried):** held fold margin 5.006 with K on its law.
9. **T5 (carried, report only):** contact depth 14.72 mm bench and 46.14 mm held, unchanged at F+3.9.
10. **NEW-ws-inband (carried):** the raised-arm workspace reads in-band 0.801, unscored. The raised ring adds metal over
    14 mm.
11. **G3 (missing measurement):** no CAD, R17, cuff twist or drag for this row. The sibling's CAD twists the cuff
    11.74 deg at f 0.05.

## Patterns walked and found clean

- **T1 / T2:** 14.5 points live in the 1-2 mm shell at the verified level (the tool's reading: 2 mm near-touch minus
  plain), and 14.58 at F+3.9. Both are under the 15-point line. The band read as 3-14 mm costs 0.15.
- **T4:** blend 10 sits at its box edge. It spends groove radius, not a fold margin (NEW-silent-check).
- **S1 / P1:** held +4.95, the family's.
- **S2:** sample-weighted 0.890 vs part-weighted 0.898. **S3:** every moving body is sampled.
- **S4:** the sample is the standard bench's.
- **S5:** full flood = static 18.95.
- **M1 / M2:** O20 hubs, 0 passive translations, ISO 8734 pins, MR63ZZ crank pair. M1 is not counted under M3: the
  parts are real components; they are placed in another part's volume.
- **M4:** K moves 45.6 deg. **M5:** no spring.
- **P2:** the pin pick here was made on fast only, before the held wear.
- **P3 / R3:** convergence gate 0/0/0. This audit's control reproduced the claim; it was not re-measured until lucky.
- **P4:** no bench / judge / metric file changed in the row's 4 commits.
- **G1 / G2:** no spring. **G4:** same seats as the lead. **G5 / G6:** complexity 15.75 recomputed, 3 active DOF.

## Re-wear rule (step 2)

The row's last commit (2f4e435, 06:00:55) changed only its verdict text. The claim, best_params and verification are
unchanged, so `tools/alignment_audit.py remeasure` was not re-run. The control above re-wears the verified claim
through the same harness today, at 18.95. The existing `remeasure/desmo-slipper-knuckle-3r_{bench,held}.json` (17:31,
19.00 / 23.95 on the model's linear IK) stand.

## Numbers I could not get, and why

- **The real relief swept in link 1b by the ring sector:** the ring sector plus the J2 travel. Not computed here;
  no CAD of this row exists.
- **Strap clearance:** there are no link 1b strap samples near J2 in the model.
- **A wide pin scan at F+4.6 and F+6.15** (20 pins tried in all, time box), and an exact wear above link 1b.
- **The workspace wear probe at F+3.9:** time box.
- **Cuff twist and drag:** no CAD.

## Proposals (not applied; none feeds the verdict)

1. **Family level fix (measurement change).** Measure stage 1's level from hub 2's face, not the crank pivot. Re-base
   the glev box so that the groove bottom is >= F+3.15. Enforce RC_MIN, or a floor of pin radius + ridge.
   - Measured effect on the verified rows: this row 18.95 -> 20.38 bench / 23.90 -> 25.33 held at the nearest
     plate-clearing pin. desmo-conecut 18.98 -> 20.50 bench (its audit).
   - lowarm-halfring 17.96: not measured. It runs the same layer at glev -1.0.
   - No other verified row has a desmo stage 1.
2. **A layer check in every verifier of a stacked drive:** sample each drive part against the members of the joint
   whose layer it shares (here link 1b's J2 plate F+0..3 and its strap). This row is the first measured case where a
   verifier's "relief pocket" assumption hid a layer conflict.
3. **Reporting:** write the measured plate-clearing number on the row as a separate field next to v_gap. Do not
   replace v_gap without a verifier.

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
