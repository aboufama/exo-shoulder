# Alignment audit: kneeless-roller-knuckle-3r (round 9, lens 3, verified)

This audit ran on 2026-10-17 from 01:41 to about 02:00 UTC, at git b3a24be onward, in a fresh container. It replaces the
auditor sections of the 2026-10-16 23:10 audit. It edited no bench, judge, kit, model, row, dashboard page or
CLAUDE.md, wrote no tool and changed no score.

Why it ran:
- The design was verified at 23:27 UTC, after the 23:10 audit.
- That audit's ledger verdict, 'gamed', rests on one tool reason that it called a false positive. No skeptic has
  ruled on it yet.
- The user changed two rules on 2026-10-17. The 2 mm A1 dominance gate is retired (the plain verified gap decides,
  and contact stays metal < 1 mm). A sensed joint is a joint.

## Verdict: GAMED (ledger), on one tool reason that the evidence refutes. Every other reason is watch.

**The claim** is the verified v_gap **21.07** (score 92.34) on Bench(110,360) exact, with the shape frozen. Held out it
is 24.59. Complexity is 23.75. The ledger reads the claim from `v_gap` now; the 23:10 audit read the fast 16.70.

**Ledger entry 2026-10-17T01:49:03Z: verdict gamed, tool verdict gamed.**
- **gamed, `idle` (tool):** "IDLE: re-measured K.ang span = 0.0 deg". This is the knee angle of a design that has no
  knee. The declared drive K moves 0-43.53 deg (45.78 held out). See the first finding.
- **watch, `fold_margin` (tool):** "no min-th margin on file". The row does record it: 5.408 deg on the bench and
  5.091 held out, both at least 5. This is a second miss in how the tool reads the row.
- **watch, `reporting` (tool):** the row's verdict text still says "self-measured, NOT verified". That understates
  the row; it does not flatter it.
- **watch, 8 judgement findings:** listed below.

**What resolves it.** A skeptic rules on `idle`, with `python3 tools/alignment_ledger.py skeptic
kneeless-roller-knuckle-3r --rulings ...` by a separate agent. CLAUDE.md requires that the auditor's own claims get a
skeptic. This audit did not run the skeptic stage, and the auditor cannot lower a tool reason. If `idle` is
refuted, the verdict is **watch**.

**Effect on the rankings.** The 'gamed' label does not change any ranking. The design is not the leader under either
rule:

| design | plain (bench) | held out |
|---|---|---|
| roller-longdyad | 18.67 | 23.73 |
| sidecar-longdyad | 18.91 | 22.67 |
| sidecar-parallelogram | 19.13 | - |
| kneeless-roller (this design) | 21.07 | 24.59 |

Under the old A1 rule it was also not the leader. The rule change moves nothing for this design. The row and the doc
still give "fails the A1 dominance gate" as the reason it is not the lead. Under the 2026-10-17 rules the reason is
simply that it is 2.40 plain behind roller-longdyad and 2.16 behind sidecar-longdyad.

**Re-wear: not re-run, because the claim is unchanged.**
- The verifier's commit (40dea1a, 23:13 UTC) is newer than the re-wear files (23:09). But it changed only the status
  and the verification fields. The row's best_params are identical to the re-worn params (0 differences).
- The verifier's own harness reproduced the numbers to the digit: 21.07 / 1 mm 23.23 / 2 mm 32.25, and held out 24.59.
- The local bench cache is not built in this container, and scipy is missing. The farm was not needed for an
  unchanged claim.
- Every number below comes from the committed re-wears (`docs/alignment/remeasure/kneeless-roller-knuckle-3r_*.json`,
  model unchanged, CB_EXACT=1) or from the verifier files.

## What the wearer gets (measured)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140, workspace) | **7 / 28 taken** on the bench (roller-longdyad 8, lead 8). Lost to the fold 15, contact 4, parts 2. Held out 16 / 71 (both knee rows 18 / 71) | `remeasure/..._bench.json`, `_held.json` audit.overhead140 |
| Raised-arm reach by elevation (taken / total) | 0-60: 158/172; 60-90: 57/75; 90-120: 25/51; 120-140: 14/34; 140-160: 5/13; 160-200: **2/15** (lead 161, 55, 25, 12, 5, 3) | `remeasure/..._probe.json` ws_reach_by_elev |
| Taken poses with metal < 1 / 2 / 3 mm | Bench: 4 / 21 / **95** of 371 (roller-longdyad 3 / 30 / 133, lead 2 / 26 / 178). Held out: 12 / 49 / 228 of 863 (roller-longdyad 14 / 66 / 274, lead 14 / 63 / 427). This is the design's clear win | `_bench.json`, `_held.json` deep |
| Lowest metal on a taken pose | **0.01 mm** at (plane 90, elev 135, axial -90), on hub 2's crown edge. Next: 0.55, 0.78 and 0.84 mm. 10th-percentile overhead min metal is 1.72 mm (lead 1.02) | `_bench.json` audit.near_touch_low, deep |
| Contact (metal into the skin) | **10 workspace poses** on the bench (roller-longdyad 2, lead 4), summed depth 44.0 mm (lead 6.23). Deepest -12.0 mm at (15, 165, -60). Five of the 10 are at side raise 90-105 (hub 2's crown, -0.7 to -5.9 mm). Held out: 26 contact poses + 12 part clashes (knee rows 10 + 0 and 10 + 5) | `_probe.json` contact_poses; `_held.json` why |
| Workspace in-band (unscored) | 2-14 mm: 0.855 over the 261 taken workspace poses (lead 0.874). Elev 90-140: 0.828 (0.841). Overhead: 0.946 (0.926). Metal more than 20 mm off the skin: 4.2 % (lead 2.8 %) | `_probe.json`; row verification.ws_inband |
| Scored in-band | 0.8905. Hub 3 is **0.505** in band (median 13.9 mm); link 2 is 0.71; every other part is at least 0.86 | `_bench.json` parts_ib14 |
| Fold margin (th) | min 5.408 deg on the bench and 5.091 held out (0 poses below 5) | row verification.checks |
| Continuity | Full flood 21.07 (0 dropped). knn flood 23.35 (8 dropped, +2.28; lead +2.81). Bench-graph flood 49.5 (lead 43.4) | row verification.flood |
| Springs and stops | One K clock-spring cap closes both cam pairs. K rests on stop A on **499 of 863** held-out taken poses. No R17 has run, so lag, cuff twist and hold force are unmeasured | row mechanism.notes; doc verifier watch item 5 |
| Drive at its caps | Horn pressure angle 41.5 on the bench and 42.5 held out (cap 43). dK 45.78 held out (limit 46.75). Crank 1.53 mm from hub K; E 1.4 mm from L2 held out | row verification.checks |
| Knee and cuff | No knee: the knee angle is constant (93.12 deg) and the bracket drift is 0.000 mm. Under a 3 mm GH-centre error, only **38.7 %** of postures stay within a 3 mm liner. A planar knee would keep 66.6 % | `remeasure/..._ghoffset.json` |
| DOF and parts | 3 active, K slaved and never read, 0 sensed, 0 passive translations, O20 hubs. Complexity 23.75 (recomputed 23.75) | audit check complexity |

## Findings (each is watch; the ledger's 'gamed' is the tool's idle check)

**1. NEW-idle-check-false-positive: the ledger's 'gamed' is a tool false positive.**
- `tools/alignment_audit.py` c_idle takes the smallest span among dK and the `K.*` entries. In this model family,
  `K.*` is the KNEE dictionary.
- Here the knee is deleted by construction. K.ang, K.qa and K.qb are constant on every pose. The model asserts this
  (ptp 0.000 deg, |s| 0.000 mm), and the verifier checks it independently from the body transforms (bracket drift
  0.000 mm).
- The declared drive moves:
  - dK 0-43.53 deg on the bench, 45.78 held out and 45.61 on the fit bench;
  - the crank swings phi up to 20.5 deg.
- No knee is counted in the mechanism record. So M4 is absent: the score and the complexity belong to the same
  mechanism.
- The tool reports dK 43.53 in the same check that it calls idle. It also misses the row's
  `verification.checks.th_margin_min_deg` (fold_margin watch).
- **Action:** a skeptic rules on `idle`. Tool proposal T-a below.

**2. NEW-free-deletion: the knee is deleted for free on the bench, and the round-9 lesson drops its wearer price.**
- The bench's GH is an ideal fixed point, so a rigid closure costs no score. Complexity falls 43.75 -> 23.75.
- Under a 3 mm GH-centre error, the bracket-to-arm misfit is median 3.40 / max 5.90 mm, with 38.7 % of postures within
  a 3 mm liner (a planar knee: 66.6 %). At 5 mm the figures are 17.7 % and 36.2 % (`remeasure/..._ghoffset.json`).
- The design doc's lesson 1 states this price. But ROUNDS.md "Round 9 results" lesson (1) says only "costs ~2.2 gap
  points and halves complexity ... the knee buys little reach". Its round-10 focus (c) then sends planners to regain
  the 2.2 points for the knee-free class.
- **Why not better:** the wearer feels the misfit as cuff pressure and twist on about 61 % of postures at a 3 mm
  tracking or humeral-head error. The bench cannot see this.
- Measured worth of the knee, same drive, same harness: +2.40 plain on the bench, but only +0.86 held out
  (24.59 vs 23.73).
- **Action:** the round-10 brief carries the liner price next to the 2.2 points. The user's tracking-error budget comes
  before more search on the knee-free class.

**3. NEW-contact-depth: more and deeper contact, at an everyday posture.**
- 10 contact poses on the bench (roller-longdyad 2, lead 4), with summed depth 44.0 mm.
- Five of them are the side raise, scapular-plane abduction 90-105, where hub 2's crown presses 0.7-5.9 mm into the
  shoulder.
- Held out: 26 contact poses (the knee rows have 10 each).
- **Why not better:** the score charges about 0.54 points per contact pose, but not the depth or where it falls. The
  2 / 3 mm win comes partly from contact poses leaving the taken set.
- **Action:** the hub-2-crown lever (the doc's own next step); proposal R-b.

**4. T1: metal under 1 mm on taken poses, which the user's contact line calls contact.**
- 4 taken poses: 0.01, 0.55, 0.78 and 0.84 mm.
- They are worth 2.16 points on the bench (21.07 -> 23.23) and 2.61 held out (12 poses).
- They do not change this design's place: at the 1 mm line it is still behind (23.23 vs 20.30 / 20.00).
- **Action:** see the cross-row note below.

**5. M5: spring-closed cams and stop A, unproven.**
- One clock spring holds both rolling pairs.
- K sits on stop A on 58 % of held-out taken poses.
- No R17 has run, so G2 (stiff spring) and G3 (cuff twist) are unmeasured.
- **Action:** the slaved-coordinate coupling in judge/dynamics.py, before CAD.

**6. G4: the drive and the fold run at their limits held out.**
- Horn pressure angle 42.5 against the 43 cap.
- dK 45.78 against a limit of 46.75 (0.97 deg to spare).
- th margin 5.091 against the 5-deg rule.
- E to L2 1.4 mm.
- These are hard per-pose constraints, so the readings are not taken on another angle (T3 absent). But a built
  drive with tolerance has under 1 deg of stroke left.
- **Action:** a force and tolerance check of the roller-flank contact at 42.5 deg with K slop.

**7. NEW-inband-padding: in-band metal added lowers the gap.**
- This design's E strap has 132 samples (lE 82.3 mm) and its bracket 105 (lc 29.9), all in band. The roller-longdyad
  has 104 / 85.
- With the sibling's counts, in-band would be 0.8871 instead of 0.8907: up to 0.36 points (0.13 for E alone).
- The verifier's `--head` wear (more metal sampled) lowers the gap 21.07 -> 20.95. roller-longdyad's
  envelope-corrected 18.56 < 18.67 is the same effect.
- The effect is small, real metal at true size, and changes no ranking.
- **Action:** catalogue proposal S6.

**8. NEW-confounded-lesson: the design doc's "New knowledge 2" is still uncorrected.**
- The doc credits the deleted knee with the small fast-to-frozen penalty: +4.4 here against +8.4-9.0 for the knee
  rows.
- The same-objective knee row, roller-longdyad, pays +5.48 fast-to-frozen and +5.06 bench-to-held (this design +4.37
  and +3.52). So the knee's share is about 1.1-1.5 points. The rest is the search objective.
- **Action:** correct the lesson before it reaches FINDINGS.

**Resolved since the 23:10 audit.**
- R1: the dashboard now ranks this row by v_gap 21.07 (`docs/dashboard/leader.js` best(): v_gap first). Before, it
  ranked by the fast 16.70.
- NEW-ws-inband: the verifier now reports workspace in-band on the worn bench (0.855 / 0.828 below the lead), in the
  row and the doc.

**Patterns checked and absent.**
- **T2:** reading the band as 3-14 mm costs only +0.34.
- **T3:** the fold margin is read on th: 5.408, and 5.091 held out.
- **T4:** no best_params sits at its clamp edge. The nearest is bk2 35.68 in 34-48. ang_min 0 is correct for a rigid
  bracket.
- **S1 / P1:** the held-out drop is +3.52, the smallest of the three.
- **S2:** part-weighted in-band (0.912) is above sample-weighted (0.891).
- **S3:** every moving body is sampled: L1a, L1b, L2, crank, roller / horn, and the bracket as knee + E + pad.
- **S5:** the full flood drops 0 poses; the knn flood +2.28.
- **M1 / M2:** O20 hubs; 0 passive translations.
- **M3:** the verifier re-collided every taken pose; its added checks remove 0 poses.
- **P2:** the claim was picked on the frozen bench, and held out ranks the 3 candidates the same.
- **P3 / R3:** best of 5914 configs, with the frozen spread 21.07-22.37 reported.
- **P4:** judge_change is ok.
- **R2 / R4:** the dashboard v_gap equals the verified 21.07.
- **G1:** this design hugs the least of the three at 2 and 3 mm.
- **G5:** the complexity reproduces.
- **G6:** 0 sensed passives, so the 2026-10-17 rule "a sensed joint is a joint" does not change this design's count.

## Rule changes of 2026-10-17, applied to this design

- **The A1 gate is retired.** This entry's reasons do not use A1. The `dominance` check (vs sidecar-longdyad: plain
  -2.16, 2 mm +1.78) is ok, and it is not used as a gate. The row and doc text "fails the A1 dominance gate" is now
  outdated wording (the rows are not the auditor's to edit). The conclusion is the same under the plain verified gap.
- **A sensed joint is a joint.** This design has none. For context only, measured with `tools/simplicity.py`: if the
  knee rows' two sensed knee pins were counted as active joints, their complexity would be 87.0 (sidecar-longdyad) and
  81.75 (roller-longdyad), against 49 / 43.75 today, and they would have 5 active DOF.
  - ROUNDS.md and CLAUDE.md treat the knee rows as "3-joint leaders", that is, the cuff-side knee as the cuff freedom.
  - Whether the cuff knee's encoders make it a joint is the user's call.
  - The answer only widens this design's complexity lead. It cannot hurt it, so it is not a finding here.
- **ALIGNMENT.md** still describes A1 as adopted (section 4) and G5 / G6 as an open question. This audit did not edit
  it: the round-9 winner audit runs at the same time and reads it. Proposed text: "A1: RETIRED by the user 2026-10-17
  (plain verified gap decides; contact stays metal < 1 mm; 2 mm reported only). G5 / G6 / A5: ruled 2026-10-17, a
  sensed joint is a joint (minarc pick1 is 4-active)."

## Cross-row note for the round-9 winner audit (data from committed re-wears, not a finding on this design)

At the user's own contact line (metal < 1 mm counts as contact), the round-9 order of the top two flips:

| design | plain | 1 mm | held-out plain | held-out 1 mm |
|---|---|---|---|---|
| sidecar-longdyad | 18.91 | **20.00** | **22.67** | **25.75** |
| roller-longdyad | **18.67** | 20.30 | 23.73 | 26.83 |

- roller-longdyad's 0.24 plain gain rests on 3 taken poses with metal under 1 mm (the lead has 2). It is gone at the
  1 mm line and held out.
- CLAUDE.md's 2026-10-17 ruling says both "a design replaces the lead on the plain verified gap" and "contact stays
  metal < 1 mm". The plain v_gap counts contact only below 0 mm: a pose with metal at 0.01 mm is taken.
- Which reading the user meant decides the round-9 winner. Files: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench.json`,
  `_held.json`, `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_bench.json`, `_held.json` (deep.gap_near1).

## Proposals (measurement or reporting changes; none applied, none used in the verdict)

**T-a (tool).** `tools/alignment_audit.py` reads what is already on file:
- c_idle skips `K.*` spans when the model asserts `knee_rigid` or the mechanism record has no knee;
- c_fold_margin reads `row.verification.checks.th_margin_min_deg`.

Effect on this row: idle gamed -> ok (dK 43.53), fold_margin watch -> ok (5.408), and the tool verdict becomes watch.
kneeless-sidecar-knuckle-3r would get the same correction. Rows with a working knee keep the K.ang test.

**R-b (reporting).** Every claim reports:
- the summed contact depth, the deepest contact, and the contact poses at scapular-plane abduction 60-120;
- the 1 mm gap next to the plain gap, labelled as the user's contact line.

Effect: this row 44.0 mm / -12.0 mm / 5 poses / 1 mm 23.23. The lead: 6.23 mm / -4.61 mm / 0 poses / 20.00. No score
moves.

**ROUNDS wording (reporting).** Round-9 lesson (1) adds "plus a 1.5x larger cuff-liner misfit under GH-centre error
(38.7 % vs 66.6 % of postures within a 3 mm liner at 3 mm error)". Round-10 focus (c) waits for the user's
tracking-error budget.

**New catalogue entries (proposed for docs/ALIGNMENT.md section 2):**
- **S6. In-band padding.**
  - *Looks like:* the sample-weighted in-band rises when in-band metal is added or lengthened, with no out-of-band metal
    moved.
  - *Why not better:* more metal is never a lower profile.
  - *Detect:* report in-band without the parts the design added or lengthened against its parent, and the gap change
    from adding a missing envelope (`--head`).
  - *Here:* up to 0.36 points; `--head` 21.07 -> 20.95; roller-longdyad 18.67 -> 18.56.
  - *Tightening option (a measurement change, the user's call):* score in-band part-weighted. This row would go
    0.8905 -> 0.912: better, not worse, so part-weighting would not catch this case. The direct test is the
    sample-count comparison above.
- **G7. A compliance deleted for free.**
  - *Looks like:* the bench's GH is an ideal fixed point, so a passive freedom between the chain and the cuff can be
    deleted at no score cost.
  - *Detect:* report the GH-offset misfit at 3 / 5 mm (share of postures within the liner) against the parent.
  - *Here:* 38.7 % vs 66.6 %.
- **R5. A lesson drawn across rows that differ in protocol.**
  - *Detect:* review; compare only with a row searched on the same objective and harness.
  - *Here:* +4.4 credited to the knee against +5.48 for the same-objective knee row.

## Numbers not obtained, and why

- **R17 lag, cuff twist and spring hold force:** no dynamics run exists for this design. The judge needs the
  slaved-coordinate coupling, and that was out of scope for an audit.
- **A re-wear in this session:** the claim is unchanged, and the local bench cache and scipy are missing in the fresh
  container.
- **Held-out workspace in-band and reach by elevation:** the probe was run on the bench wear only.
- **A GH-offset misfit for the knee rows from their own models:** the 66.6 % comes from this model's planar-knee
  equivalent, not from a re-wear of a knee row.
