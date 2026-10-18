# Alignment audit: underpass-bridge-relay-4r (2026-10-18 ~21:40 UTC, re-audit after the refutation)

## Verdict

The ledger verdict is **watch** (tool alone: watch). The claim the ledger now records is the row's verified
number, **v_gap 20.60** on frozen exact Bench(110,360) (score 92.51), held out 24.33. The row's status is refuted.

The previous audit (20:53 UTC, ledger 'gamed', finding M3) caught the self-measured 13.74 (score 95.00): it needed the
3 mm E strap to pass through the 2.5 mm bridge shell. The verifier then committed the refutation (5598374, 20:59 UTC).
The row's v_gap is now the corrected bridge: the shell underside placed by the design's own rule (up_clr 1.2) over every
chain set, the strap's top face included (R_under 84.222), and re-scored with the verifier's X1 clash check. That
number is honest about the clash that bought the 13.74. It ranks the design where it belongs: 2.32 behind the 3-joint
lead conecut-knee-knuckle-3r (18.28) and 5.84 behind its parent offset-shortcar-relay-4r (14.76). It is 4 joints, so it
is never a lead. The M3 finding is resolved in the row, so it stays on file as a watch with its residuals.

What is left is a set of watches. The new one: the loaded-bridge check, which the verifier called moot at the
corrected height, read the strap's skin-facing underside again rather than its top face (below).

## What the wearer gets (measured, on the verified corrected config)

Source: `docs/alignment/remeasure/underpass-bridge-relay-4r_corrected_wear.json`. That file comes from the verifier's
corrected-bridge per-pose dumps plus the verifier's own X1 lost set. The derived dumps
(`remeasure/underpass-bridge-relay-4r_bench_perpose.json`, `_held_perpose.json`) recompute **20.60 and 24.33 exactly**.

| | bench Bench(110,360) | held out | lead conecut-knee bench / held |
|---|---|---|---|
| gap (plain = the gate here) | 20.60 | 24.33 | 18.29 / 22.38 |
| reach (ws taken) | 0.7889 (284 / 360) | 0.7689 (732 / 952) | 0.7278 / 0.6922 |
| overhead reach (elev >= 140) | **7 / 28** | 17 / 71 | 8 / 28, 18 / 71 |
| raised-arm reach (elev >= 90) | 61 / 113 | 160 / 300 | 47 / 113, 123 / 300 |
| in-band 2-14 mm, pooled (chain only) | **0.8347** (0.9012) | 0.8318 (0.9000) | 0.9012 / 0.9000 |
| taken poses with metal < 1 / 2 / 3 mm | 8 / 56 / 138 of 394 | 24 / 130 / 292 of 934 | 3 / 33 / 105 of 372; 13 / 71 / 217 of 861 |
| near-touch gap at 1 mm / 2 mm (report only) | 24.79 / 53.16 | 29.30 / 55.19 | 19.92 / 34.84; 25.23 / 37.11 |
| contact poses, summed depth | 12, 43.23 mm | 43, 173.02 mm | 4, 20.24 mm; 14, 60.97 mm |
| deepest contact | 9.79 mm at (30, 135, 0) | 12.24 mm at (15, 135, -15) | 8.93 mm; 9.86 mm |

- **Where the gap goes (bench):** in-band 6.53, reach 11.11, contact 2.96. The raised shell's skin-facing metal is
  only 66 % in band (relay in-band 0.6626).
- **Workspace in-band (unscored): not measured.** The dumps carry sample counts on clip frames only, and
  `tools/alignment_wear_probe.py` has no adapter for this OS.wear / hwsweep model family.
- **Springs:** the relay coordinate is held by a constant-force coil on the carriage lug against the zero and PHI
  dowels. No R17 dynamics run is on file.
- **Stops and fold margin:** min `th` 5.000 deg over the claim's taken poses (verifier_claim.json / verifier_held.json
  pick.th_margin). The bridge does not change the chain, so this carries over.
- **Relay range:** the relay moves 0 to 32.9 deg over the bench takes and up to 34.94 deg held (PHI 35), so it is not
  idle.
- **Continuity:** on the corrected wear, static equals connected (19.74 by the model rule). The flood drops 0 relayed
  takes, and 153 of 154 relayed envelope frames are connected (`remeasure/underpass-bridge-relay-4r_loaded_bench.json`
  continuity).
- **Cuff twist:** not measured.
- **Near-singular postures:** none below the 5 deg margin.
- **What is physically there:** a 2.5 mm Ti cantilever shell, 1.29 mm over the strap's top face at its closest taken
  pose. Its root needs an arm-band anchor that nothing models (249.6 N.mm root moment), and it deflects 0.336 mm at 4 N.

## Checks (tools/alignment_audit.py, docs/alignment/underpass-bridge-relay-4r.json)

The tool's verdict is watch. Its readings:

- **held_out: ok, but on the wrong pair.** The tool reads `held_out_gap` 16.64, which is the refuted claim's held
  number, against v_gap 20.60 (-3.96). The right pair is v_held_gap 24.33 against 20.60, which gives +3.73. That is
  still under the +6 watch line. Proposal 2 covers the reading.
- **fast_frozen: ok.** Self-measured 13.74 against verified 20.60 is +6.86, under the 14 watch line.
- **near_touch, dominance: watch.** These are reading gaps: the tool finds no near-touch file in its formats. The
  numbers are measured above, and the design is behind the lead on the plain gap and at 2 mm, so dominance cannot fire.
- **contact_depth: ok (report only), but blinded.** With this audit's derived dumps on file the tool now reads the
  claim's depths: bench 12 poses, 43.23 mm; held 43 poses, 173.02 mm. It reports "no bench depth of
  conecut-knee-knuckle-3r on file". That is false: the reference read crashes and the crash is swallowed (finding
  NEW-blind-reference). With the one bad file skipped, the same check gives **watch**.
- **continuity: watch** (no flood in the tool's format), **idle: watch** (no K / crank / knee spans in its format),
  **sampling: watch** (no per-part record). All three are reading gaps; the measured readings are above.
- **reporting: watch.** The dashboard row shows no verified number and status 'screened' (R2 below).
- **Ok:** fold_margin 5.0, complexity 53.0 recomputes, judge_change (no bench or judge file in the row's 4 commits),
  rules (O20, margin 5, 0 passive translations, 4 DOF).

**Re-wear.** `tools/alignment_audit.py remeasure` does not support this model: its `frozen()` does not call a
pin-knee-style `audit(M, B)`; it is an OS.wear / hwsweep model. So there is no `remeasure/<id>_bench.json`. This audit
instead:

1. derived the verified config's per-pose dumps from the verifier's files (no model run), reproducing 20.60 / 24.33;
2. re-wore the corrected bridge on exact Bench(110,360) through the model and the verifier's `xcheck`, both unchanged,
   with the shell lowered by its own 4 N deflection (`remeasure/underpass-bridge-relay-4r_loaded.py` ->
   `_loaded_bench.json`).

The held-out loaded read was not run: about 15 min of CPU on a box at load 12-15, past the time box. The farm is off
(budget spent, CLAUDE.md 15:49 UTC).

## Findings (docs/alignment/underpass-bridge-relay-4r.findings.json)

### NEW-skin-only-thickness (watch): it recurred in the verifier's loaded-bridge diagnostic

- The verifier's note ("Other checks" 3, and the row note) calls the loaded bridge moot at the corrected height,
  because E's underside clears the shell by >= 4.19 mm.
- That table, `E_under_shell_taken`, reads `per["E"]`: the rigid, skin-facing set only. The loaded X1 itself was run
  only at the claimed height. At the corrected height the binding body is the strap's top face (contact set c23:m3),
  which clears the shell by just 1.292 mm (pose 149).
- This audit re-wore the corrected bridge (R_under 84.222) on exact Bench(110,360), with the model and the verifier's
  `xcheck` unchanged (`remeasure/underpass-bridge-relay-4r_loaded.py`, 468 s):

| shell state | extra jams | taken poses lost | rescored gap | ws taken | overhead |
|---|---|---|---|---|---|
| unloaded (drop 0; reproduces the verified number) | 9 | 3 | **20.60** | 284 | 7 / 28 |
| loaded: 4 N tip deflection, 0.336 mm, uniform (an upper bound) | 14 | 8 | **22.02** (+1.42) | 279 | 7 / 28 |

- The five new jams are all the strap top against the shell, read against the verifier's 1.0 mm non-adjacent rule:
  149 at 0.962 mm, 139 at 0.963, 200 at 0.967, 257 at 0.996 and 118 at 0.997.
- **Why it is only a watch:** the loaded clearance stays >= 0.96 mm, so no metal touches metal. The uniform drop
  overstates the deflection near the foot. And the verified number does not rank the design above a better one either
  way.
- **Action:** if the family is re-claimed, read the loaded check over every set (Proposal 1). A shell stiff enough to
  keep 1 mm under load, or the 1.5 mm thinned strap the verifier suggests, needs its own loaded read.

### NEW-blind-reference (watch): the tool's T5 alarm has been off since 11:37 UTC

This is a fault in the instrument, not in the design.

- `docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` (commit 46af77e,
  11:37 UTC) stores `held: "missing dump"`, a string where a dict is expected.
- `tools/alignment_audit.py` `_depth_sources()` loops over the paired files with `(d.get(w) or {}).get(...)` outside its
  `try`. For the reference conecut-knee-knuckle-3r it raises AttributeError.
- `c_contact_depth` swallows the error and prints "no bench depth of conecut-knee-knuckle-3r on file". In fact
  `remeasure/conecut-knee-knuckle-3r_bench_perpose.json` reproduces the lead (18.28 / held 22.38).

A read-only simulation with that one file skipped (nothing was edited) gives:

| audit (committed with the blind reading) | contact_depth as committed | with the file skipped |
|---|---|---|
| underpass-bridge-relay-4r (this row) | ok | **watch**: bench 43.23 vs 20.24 mm (x2.14), held 173.02 vs 60.97 (x2.84) |
| freek-oracle-route-knuckle-4r | ok | **watch**: x3.88 bench, x3.81 held |
| offset-shortcar-relay-4r | ok | **watch**: x2.28 bench |
| phi40-thinstack-relay-4r | ok | **watch**: x3.70 bench, x3.24 held |
| conecut-h2facet-knuckle-3r | ok | ok (x0.98 / x0.99) |
| conecut-l2jog-knuckle-3r | ok | ok (x1.00 / x0.95) |
| lowarm-kphase-notch-knuckle-3r | ok | ok (x0.77 / x0.66) |
| lowarm-kstop-knuckle-3r | ok | ok (x0.82 / x0.74) |

- **Why it matters:** depth is never in the score, so no number moved. But the tool's T5 alarm was off for every design
  audited against the lead since 11:37. The relay rows are exactly the ones it should have flagged; where their
  auditors judged T5 by hand (offset-shortcar did), the verdict stands.
- **Action:** Proposal 3. This audit may not edit the tool or another audit's file.

### M3 (watch): resolved in the row, residuals only

- The row is refuted, and v_gap is the corrected bridge with X1. The derived dumps reproduce it exactly.
- X1's 3 bench losses (345, 396, 446) and 8 held losses are all the knee link's top face (c29:m6) against the pad
  bracket. They read 0.014-0.092 mm by nearest 2 mm sample minus 1 mm, against the 0.15 mm running gap, so they are
  resolution-limited both ways.
- Six bench contact poses also jam the knee top on the bracket: 237 at 0.014 mm, and 316, 343, 372, 423 and 448 at
  0.20-0.48 mm into it. They are kept as contacts (0.25 points each) instead of lost (0.28 each). Read as lost, they
  would add 0.19 gap points.
- **Why it matters:** it does not change the ranking. The design is already behind the lead and the parent.
- **Action:** none for the ranking. Any re-claim of this family should sample the bracket at 1 mm.

### T5 (watch): depth-blind contact, on the verified config

- Bench: 12 contacts, 43.23 mm summed. The deepest are 9.79 mm at (30, 135, 0) and 8.93 mm at (15, 165, -60). Five
  are deeper than 3 mm.
- Held: 43 contacts, 173.02 mm summed, deepest 12.24 mm at (15, 135, -15). 21 are deeper than 3 mm.
- Against the lead (4 / 20.24 mm bench, 14 / 60.97 mm held) that is x2.14 and +23.0 mm on the bench, and x2.84 and
  +112.1 mm held. Both are past the 2x / 5 mm watch line.
- Three held contacts also put the pad bracket into the arm: 0.26, 0.44 and 3.45 mm at poses 225, 977 and 1134.
- **Why the exo is not better:** the score charges these poses, so it does not reward them. But the wearer gets J2's
  hub 10-12 mm into the arm on plain raises to 135 deg, more often than on the lead.
- **Action:** none on the number. Report the depth next to the gap on the board.

### G1 (watch, report only): metal hugging

- 56 of 394 taken bench poses (14.2 %) have metal under 2 mm, against 8.9 % on the lead. Held: 13.9 % against 8.2 %.
- Near2 is 53.16, against plain 20.60.
- No plain gain is bought by it: the design is behind the lead both plain and at 2 mm.
- T1 instances: the posterior foot rides 0.59 mm off the arm at 466 (150, 105, -105). The inherited bracket rides
  0.44 mm off at 139 (-60, 60, 105).

### S3 (watch): bodies the bridge needs that nothing samples

- The cantilever anchor (249.6 N.mm root moment): its metal is unsampled and its parts are not counted.
- The constant-force strip has no guide surface. The verifier's chord diagnostic keeps it >= 8.9 mm from the chain and
  >= 1 mm from the skin, but it is not scored metal.

### M5 (watch): spring-held relay, flexing bridge

- No R17 run is on file.
- The verified number is read on the unloaded shell. See the first finding for the loaded reading.

### R2 (watch): the refuted pass is still on the board

- `docs/dashboard/data/morphs.json` (v147, d889d5a, built 52 s after the refutation commit) still shows status
  'screened', gap 13.74 (score 95.00), no v_gap, and "4-JOINT PASS BY 0.01 (claim, unverified)".
- `sweeps.json` has best_gap 13.74.
- Because the status there is 'screened', the board keeps the row live at the golden 95 line, 6.86 points better than
  the design holds.
- It is not in the headline today: the headline claim and sweep slots are proxtrack-relay-knuckle-4r 4.15 / 4.25, and
  the leader is conecut-h2facet-knuckle-3r 18.28.
- **Action:** rebuild the dashboard from the row (tools/dash_build.py). That is the lead's step; this audit does not
  touch the board.

### Patterns checked and not found

- **T2:** the claim-era knife edges (0.01 under the pass line, in-band 0.0012 over 0.90) are gone. The verified number
  is 6.85 over the line, and its pooled in-band fails outright (0.8347), so no band edge is bought. The 3-14 mm band
  reading cannot be taken from these dumps.
- **T3:** the margin is read on `th`, min 5.000. **T4:** R_under comes from the design's rule (up_clr 1.2, the larger of
  the two placements, A over B); no search bound walks.
- **S1:** held +3.73 over bench. **S2:** the shell is sampled on a 2 mm grid (1 pt / 4 mm2, the kit's density), so its
  out-of-band metal weighs in at its area. **S4:** the skin is unchanged. **S5:** see continuity.
- **M1, M2:** O20 hubs, 0 passive translations, catalogue T-nut, dowels and coil. The anchor is under S3. **M4:** the
  relay moves 0-35 deg.
- **P1:** no polish. **P2:** the corrected placement was taken by the design's own rule on the bench, before the held
  read, and held was read once. **P3:** the claim and the correction were each read once. **P4:** no bench or judge
  file in the row's commits.
- **R1:** status refuted, v_gap verified. **R3:** pre-registered grid, top-5 spread 0.00. **R4:** the board shows no
  v_gap at all (R2), so it recomputes nothing.
- **G2:** no stiff preload declared. **G3:** cuff twist not measured. **G5:** complexity recomputes to 53.0, with the
  4th joint at 25 points. The unmodelled anchor is not counted (S3). **G6:** "4 joints, never a lead" on the row and
  the board.

## Proposals (measurement or reporting changes; not applied, not inputs to the verdict)

### Proposal 1 (repeats the 20:53 proposal, now with a second instance): every clearance or jam read covers the contact sets

The pattern (proposed catalogue entry M6, "a part's thickness lives only in a skin-check set") has now appeared twice
on this one design:

- in the model's `need_scan`, which set the claim's bridge height;
- in the verifier's loaded-bridge note, which tabulates E's underside (`E_under_shell_taken` reads `per["E"]`).

Proposed rule: any clearance table, placement or loaded check must report the minimum over the rigid, link AND
contact-only sets, and must name the set that binds.

Measured effect: this row only, 20.60 -> 22.02 if the loaded 1.0 mm rule entered the claim (as a diagnostic it does not). offset-shortcar-relay-4r: its verifier's X1 includes
the contact sets (verify line 57), so 14.76 is unchanged. The 3-joint rows have no bridge.

### Proposal 2: the held_out check should prefer `v_held_gap` when the row has one

Today the tool pairs `held_out_gap` (the claim's held number) with `v_gap`. Over every row on file, only this one has
`held_out_gap` != `v_held_gap`: the tool reads -3.96 where the true reading is +3.73. Both are ok, so no level changes.

### Proposal 3: make the T5 reference read robust, and read the verifier's dumps

Two changes:

1. In `_depth_sources()`, skip a paired file whose wear entry is not a dict, instead of letting one malformed record
   blind every comparison against the lead.
2. Also read `docs/concepts/verify/<id>/*_perpose.json` when a dump's recomputed gap reproduces the claim. This audit
   had to derive dumps into remeasure/ for the tool to see this row's depths.

Measured effect (read-only simulation, table under NEW-blind-reference): contact_depth goes from ok to watch on 4 of
the 8 audits committed since 11:37 (freek-oracle-route, offset-shortcar, phi40-thinstack, this row). It stays ok on 4.
No score or gap changes, since T5 never gives gamed.

## Skeptic (2026-10-18 ~21:32 UTC)

**Final verdict (ledger): watch.** I refuted 6 of the 14 reasons and upheld 8. The worst level among the upheld
reasons is watch.

How I checked. I re-derived everything from the verifier's raw corrected-bridge dumps
(`verify/underpass-bridge-relay-4r/verifier_fix*_A_up1.2_perpose.json`) and its X1 jam rows, independently of the
auditor's derived dumps, and ran no model:
`docs/alignment/remeasure/underpass-bridge-relay-4r_skeptic.py` -> `_skeptic.json`. It recomputes **20.60 / 24.33**
exactly. The lead's dumps recompute 18.29 / 22.38 on the same harness (frozen exact Bench(110,360) and the held split).
The rulings are in `docs/alignment/underpass-bridge-relay-4r.rulings.json`.

### Refuted (with evidence)

- **near_touch.** The numbers are measured and on file: plain 20.60, near1 24.79, near2 53.16 (held 24.33 / 29.30 /
  55.19). They are in `_skeptic.json` bench.x1 and in `_corrected_wear.json` bench.x1. When numbers are present,
  `c_near_touch` reads ok (report-only since 2026-10-17). The watch was a reader gap.
- **dominance.** Both 2 mm readings are on file on one harness: this row 20.60 / 53.16, the lead 18.29 / 34.84.
  `c_dominance` gives dp = -2.31, which is its ok branch. There is no plain gain for 1-2 mm metal to buy.
- **continuity.** `loaded_bench.json` continuity holds a flood on the corrected bridge:
  - dropped_relayed 0 and phi0_taken_not_connected 0;
  - 153 of 154 relayed envelope frames connected;
  - `claim.json` continuity.dropped_relayed is 0.

  The connected loss is 0, under the 1.0 line. The flood was run at the model rule, so see missed item 1.
- **idle.** The declared drive is the relay coordinate phi. It spans 0 to 32.9 deg over the taken bench poses
  (`claim.json` relayed_poses: 24 taken at phi 0.8-32.9; `loaded_bench.json` relayed.phi_max 32.94 on the corrected
  wear). That is past the 2 deg line. The knee has no span on file for this row, and `c_idle` does not raise a level on
  that.
- **judgement:G1.** The readings are right: 56 of 394 taken poses under 2 mm (14.2 %), 130 of 934 held (13.9 %),
  against the lead's 8.9 % and 8.2 %. The pattern is not there. G1 is an in-band gain bought by moving metal toward the
  skin, and nothing was gained: plain is -2.31 behind the lead, pooled in-band is 0.8347 against 0.9012, and dominance
  reads ok. The 1-2 mm metal stays reported under near_touch.
- **judgement:R2.** The finding was stale at the audit's own git. Dashboard v148 (c33420e, 21:21:29, an ancestor of
  81bf405) shows the row as status 'refuted', v_gap 20.6, with a verdict that begins "REFUTED AS CLAIMED". The
  "PASS BY 0.01" text is gone. Refuted rows are not live: `core.js:9` and `leader.js:4` drop them, and `bench.js:4`
  draws their line dashed. The leftover sweep_gap 13.74 is the upheld reporting watch.

### Upheld

- **sampling.** There is no per-part record. The two-group split on file stays watch even once measured:
  - chain 0.9012, relay metal 0.6626, pooled 0.8347, so the relay is 27.9 % of the samples;
  - the part-weighted figure is 0.7819, which is +5.28 points against the 3-point line;
  - 6 moving bodies are declared but only 2 groups are sampled.
- **reporting.** I re-ran `c_reporting` on the current board. It still fires: sweep best 13.74 sits 6.86 below
  v_gap 20.6. Its other two parts (no v_gap, status 'screened') are stale since v148.
- **judgement:M3.** Upheld on the unmeasured 2 mm sample resolution of the knee-top / bracket check.
  **Correction:** the "+0.19 if read as lost" has the wrong sign. The 6 bench contact-jam poses already carry
  taken = False. Reading them as lost takes them out of the contact denominator, as X1 does with a lost pose. That gives
  **19.14 (-1.46)** on the bench and **22.73 (-1.60)** held, with 16 contact-jams there. The verifier's
  kept-as-contact reading is the harsher one, so it does not flatter the design.
- **judgement:NEW-skin-only-thickness.** Confirmed from the verifier's own xcheck:
  - E's underside clears the shell by at least 4.192 mm, while the strap top (c23:m3) clears it by only 1.292 mm (pose 149);
  - 5 taken poses sit under 1.336 mm: 118, 139, 149, 200 and 257;
  - losing them as well recomputes **22.02** exactly.
- **judgement:NEW-blind-reference.** Reproduced read-only:
  - `_depth_sources('conecut-knee-knuckle-3r')` raises AttributeError;
  - with the bad paired file skipped, this row reads watch: x2.14 bench, x2.84 held;
  - freek-oracle-route (x3.88), offset-shortcar (x2.28) and phi40-thinstack (x3.70) also flip to watch;
  - the four 3-joint rows stay ok.
- **judgement:T5.** Confirmed:
  - bench: 12 contacts, 43.23 mm summed, deepest 9.79 mm;
  - held: 43 contacts, 173.02 mm summed, deepest 12.23 mm;
  - against the lead's 4 / 20.24 mm and 14 / 60.97 mm, that is x2.14 (+22.99 mm) and x2.84 (+112.05 mm), past both
    lines.
- **judgement:S3.** The design's own doc (lines 126-128) says the root anchor is unmodelled metal. The model computes
  the 249.6 N.mm root moment but samples no anchor.
- **judgement:M5.** No R17, friction or hysteresis run is on file. The doc (line 134) lists them as inherited and
  unpriced.

### Missed (for the next audit; not in this verdict)

1. **The continuity flood does not see the X1 clash.** `loaded_bench.json` continuity is read at the model rule
   (static.gap 19.74), not at the verified X1 set (20.60). The verifier's `xcheck` (verify.py lines 53-57) runs only on
   the bench poses (`S["M"]`, `S["B"]`). So the 1432 envelope frames are flooded without the knee-top / pad-bracket
   clash, which jams 9 of the 397 bench poses. Two of those 9 are relayed poses (396 at phi 9.0, 446 at phi 0.8). So
   "connected = static" has not been measured under the verified clash rule. Action: apply the X1 jam test to the
   envelope frames, then re-flood.
2. **An auditor error, not design gaming.** The M3 residual sign (+0.19, measured -1.46, see above) came from treating
   contact poses as taken. Any future "read as lost" estimate should use the dump's taken flag.

No new gaming by the design was found beyond these. The verified 20.60 stands as the honest number on the dumps.
