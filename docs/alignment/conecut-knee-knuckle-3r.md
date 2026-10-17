# Alignment audit: conecut-knee-knuckle-3r

This is the hourly audit of 2026-10-17, run from 18:06 to about 18:20 UTC. It was due for two lead decisions:
- the lead's tie ruling on this row (commit 8e50534, row field `leader_ruling`);
- the auditor tool's version 2026-10-17.4 (commit 4302b86).

The box was saturated (load 15.5 on 4 cores) and the farm is closed, so this audit only read files and ran the
1-minute selftest. No model ran.

- **Ledger entry:** 2026-10-17T18:11:38Z, by auditor, run `audit:conecut-knee-knuckle-3r`. Verdict **watch**.
- **Reasons:** two tool reasons (dominance, reporting) and 8 judgement findings, all watch.
- **Checks:** `docs/alignment/conecut-knee-knuckle-3r.json` (13 checks, tool 2026-10-17.4, reference
  slipper-nose-knuckle-3r).
- **Findings:** `docs/alignment/conecut-knee-knuckle-3r.findings.json`.
- **No new re-wear.** The claim has not moved since the verifier's commit d943974 (17:20). The 18:05 commit only added
  `leader_ruling` to the row. The re-wears on file reproduce the claim to the digit:
  - `docs/alignment/remeasure/conecut-knee-knuckle-3r_bench.json` (17:31) reads 18.28;
  - `_held.json` (17:36) reads 22.38.

## Verdict: WATCH, claim v_gap 18.28 (score 93.35), held out 22.38

The number is honest. Nothing in it is gamed and no hard rule is broken:
- 3 active DOF and 0 passive translations, with O20 hubs and MR63ZZ knee pairs;
- a J3 stop on J3's own angle;
- a `th` margin of 5.181 / 5.006 deg;
- a continuity flood of 18.28 full and 19.97 knn.

The watch reasons are the known ones:
- metal parked near the skin (T1);
- deeper contact (T5);
- the strap dilution;
- the lead's spring and near-singular K (M5, G4);
- a 0.006 deg fold margin (T3);
- unscored workspace in-band (NEW-ws-inband).

The new finding is about the ruling, not the design: NEW-incumbent-tie-rule.

## Lead decision 1: the tie ruling. Honest in outcome by the lead's own rule; not the user's rule

**Answer: the ruling is not gaming, but it does not follow the user's rule.** It applies a stricter rule the lead wrote
itself, never put to the user, and so far applied only to challengers. Its written reasons are readings the user
retired. Under the user's rule as written, this row is the leader, so the call belongs to the user.

**Measured basis, paired per pose on the frozen exact protocol:**

| lead change | bench diff (CI90, P better) | held diff (CI90, P better) | pooled diff (CI90, P better) | what the lead did | file |
|---|---|---|---|---|---|
| roller-longdyad over sidecar-longdyad | -0.25 ([-2.62, +1.73], 0.605) | **+1.06 worse** ([-0.47, +2.39], 0.135) | +0.69 worse ([-0.56, +1.83], 0.191) | made lead (round-10 plan 5329155) | `remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json` |
| slipper-nose over roller-longdyad | -0.18 ([-0.26, 0.00], 0.698), all in-band | -0.28 ([-0.47, 0.00], 0.938) | -0.25 ([-0.40, 0.00], 0.947) | made lead (a6c23c0, 06:23) | `remeasure/slipper-nose-knuckle-3r_vs_roller-longdyad-knuckle-3r_paired_claim.json` |
| **conecut over slipper-nose** | -0.20 ([-1.05, +0.80], 0.601) | **-1.08** ([-1.86, +0.06], 0.935) | **-0.82** ([-1.46, +0.09], 0.918) | **ruled a tie** (8e50534) | `remeasure/conecut-knee-knuckle-3r_vs_slipper-nose-knuckle-3r_paired.json` |
| desmo-slipper against slipper-nose (reference) | +0.46 ([0.00, 0.56], 0.0) | +0.45 ([0.00, 0.53], 0.0) | +0.45 ([0.00, 0.53], 0.0) | called "behind" | `remeasure/desmo-slipper-knuckle-3r_vs_slipper-nose-knuckle-3r_paired.json` |

**What is fair in the ruling:**
- **The tie rule was set before the design existed.** The rule is "paired pooled 90 % CI including 0 = tie". It was
  written in the round-12 plan (0c5b95b, 13:31 UTC, `docs/concepts/ROUNDS.md` 1943-1944), and this design was first
  modelled at 16:06 (a56358d). So the rule is not post hoc.
- **The pooled CI includes 0.** It is [-1.46, +0.09], so the row is a tie under that rule.
- **The documented tie-break gives the ruling's outcome.** Passive translations are equal (0 and 0). Complexity is
  18.25 for the lead and 18.5 here (`tools/simplicity.py --json`). The 0.25 difference is one more bought part, the
  440C dowel.
- **That rule reproduces the whole lead chain.** Pooled-CI ties plus the complexity tie-break give sidecar-longdyad,
  then roller-longdyad (20.25 against 25.5), then slipper-nose (18.25 against 20.25), and slipper-nose kept against
  this row (18.25 against 18.5).
- **The bench edge is mostly a sampling effect, and two readings agree.**
  - The equal-strap bench reads 18.67, behind the lead.
  - The tool's part-weighted in-band, its dilution-free reading, gives 0.925 here and 0.924 on the lead
    (`docs/alignment/{id}.json` sampling).
  - With in-band read that way, the bench is +0.25 behind: reach -0.28, contact +0.53.

**What is not fair:**
- **It is not the user's rule.** The user's rule (CLAUDE.md, written into the file at 01:39 UTC by d0778dd) says "a
  design replaces the lead on the plain verified gap". It names no significance gate. On the plain verified gap this row
  is ahead on both legs: 18.28 against 18.49, and 22.38 against 23.45.
- **The tie rule is a tightening of a user rule.** CLAUDE.md treats a tightening as a measurement change for the user,
  not something the lead adopts on its own.
- **It is applied to challengers only.**
  - The incumbent's own lead change has a pooled CI of [-0.40, 0.00]. Read literally, "including 0", that is a tie
    too.
  - The incumbent's predecessor was made lead while worse held out (+1.06, P 0.191).
  - The rule is also read loosely when convenient: desmo-slipper's [0.00, 0.53] "includes 0" in the same literal sense,
    yet it is called behind.
  - This row's held-out evidence (P 0.935) equals the incumbent's own (0.938), and its pooled effect is 3.3 times
    larger.
- **The ruling's written reasons are readings the user retired or never adopted.**
  - "11 poses 0.76-3.68 mm off the skin" and "one 0.26 mm pose" are near-touch, which the user made report-only
    (decision (3)).
  - "Contact is deeper" is T5, which is report-only by the lead's own rule.
  - "Equal strap 18.67" is a reweighting proposal (S6) that was never adopted. It was never applied to the incumbent,
    whose 0.18 lead was 100 % in-band; its part-weighted edge was 0.924 against 0.922.
  - Using these readings to decide a lead brings back the retired A1 gate.
  - The rule that actually yields the outcome, the complexity tie-break, is not cited in the ruling.
- **The held edge is real in the plain score, and it is reach.** The held split is reach -0.95, in-band -0.57 and
  contact +0.44. Taken only here: 11 held poses (2 for the lead). It survives equal strap: 22.90 against 23.45.

**What it is for the wearer** (mixed, so it is the user's call):
- **Better here:**
  - 12 poses reached only here, pooled, against 2 reached only by the lead;
  - the knee never binds (window margin 11.4 mm against 0.33; 0 held knee-window slides against 32);
  - the knee link carries 12 N per N m against 31.6;
  - the raised-arm workspace is a little more in band (0.832 against 0.800).
- **Worse here:**
  - 6 more contact poses, pooled, against 0;
  - deeper contact: 20.24 against 14.75 mm on the bench, 60.97 against 46.12 mm held out;
  - the knee group touches the hanging, rotated arm (835 at -3.55 mm, 978 at -1.33 mm);
  - 6 of the 11 extra held poses carry metal under 2 mm.

**Action (lead, not the auditor).**
- Rewrite the `leader_ruling` text to cite the rule that actually decides: the round tie rule plus the complexity
  tie-break, 18.25 against 18.5.
- Then put one question to the user as a big update:
  - Under your plain-gap rule, conecut leads (18.28 / 22.38 against 18.49 / 23.45).
  - Under the lead's pooled-CI tie rule plus the complexity tie-break, slipper-nose keeps the lead, by one dowel pin.
  - Which rule stands?
- Until the user answers, the board should show the conflict rather than a settled tie (proposal C5 below).

## Lead decision 2: tools/alignment_audit.py 2026-10-17.4 (commit 4302b86)

**Confirmed: SELFTEST PASS, exit 0.** It ran here, niced, in about 1 minute.
- The three new mutations fire:
  - roller-longdyad's stale complexity field +0.25 gives watch;
  - slipper-nose with 5 active DOF gives gamed;
  - slipper-nose with 3 passive translations gives gamed.
- The older mutations still fire: idle drive, rigid knee, pin knee, fold 4.8, stale +4, and the reference against
  itself.
- The resolution guard is in place (`selftest`, line 838). An upheld complexity ruling counts as "resolved by a record
  fix" only when its evidence does not match `DOF|cap 4|passive translation`.

**Caveats** (instrument notes, not verdict inputs; proposals P-T1 and P-T2 below):
- **The "hard goal" runs on a stale leader list.** `LEADERS` (line 790) holds roller-longdyad, sidecar-longdyad,
  kneeless-roller, kneeless-sidecar and minarc-stop-knuckle-4r. It does not hold the verified lead slipper-nose (lead
  since 06:23) or this row.
- **The PASS covers 5 of 19 ruled rows.** Six "info" rows fail the hard goal's own criteria. There are false positives
  on dogring (2), inband-rssr (1), longstroke-slipper (1), skin-normal-3r-pin-knee (3 or more) and trimlug (1), and
  2 LOST TRUE POSITIVES on sidecar-roller-flank (held_out, continuity). Slipper-nose and this row read clean (TP only).
- **The new "never resolved" guard has no test.** No mutation runs through it: the three new mutations test
  `c_complexity`'s level, not the resolution path. It matches free-text evidence, so a hard-rule ruling worded "4
  active joints" or "translations beyond 2" would still be counted as resolved.

## What the wearer gets (measured; files from the 17:27-17:58 audit and skeptic, claim unchanged since)

| | this row | lead slipper-nose | file |
|---|---|---|---|
| overhead reach (ws elev >= 140), bench / held | 8 / 28, 18 / 71 | 8 / 28, 18 / 71 | `remeasure/*_probe_bench.json`, row `frozen.held.overhead` |
| why overhead is lost (bench) | fold 14, J3 stop 3, contact 3 | fold 14, knee slide 4, contact 2 | probe `ws_overhead_why_not` |
| raised arm, ws elev 90-140 taken, bench / held | 39 / 85, 105 / 229 | 38 / 85, 96 / 229 | per-pose dumps |
| all ws taken, bench / held | 262 / 360, 659 / 952 | 261 / 360, 650 / 952 | per-pose dumps |
| taken poses with metal < 1 / 2 / 3 mm, bench | 3 / 33 / 105 | 3 / 30 / 100 | `remeasure/*_bench.json` |
| the same, held out | 13 / 71 / 218 | 14 / 67 / 200 | `remeasure/*_held.json` |
| contact poses, bench (summed depth, deepest) | 4 (20.24 mm, 8.93 mm at ws 15/165/-60) | 2 (14.75 mm, 9.01 mm) | `conecut-knee-knuckle-3r.json` contact_depth |
| contact poses, held | 14 (60.97 mm, 9.86 mm at ws 45/165/-30) | 10 (46.12 mm, 9.05 mm) | same |
| scored clip in-band 2-14 / part-weighted | 0.901 / 0.925 | 0.896 / 0.924 | sampling check |
| ws in-band, unscored, elev 90-140, bench / held | 0.832 / 0.848 (max 31.5 mm) | 0.800 / 0.822 | probe |
| knee-window slides, held | 0 (margin 11.4 / 13.2 mm) | 32 (margin 0.33 mm) | row `frozen.knee`, verifier C2 |
| knee-link force per N m about J3 | 12.0 N | 31.6 N | row `frozen.knee` |
| J3 stop | 2 mm 440C dowel, held margin 0.74 deg, 19 held poses stopped | none | verifier C2 / C3 |
| springs | the lead's K clock spring; R17 not run for this knee | R17 forward bound fails by 0.0008 deg at mu 0.15 | lead ledger M5 |
| fold margin `th`, bench / held | 5.181 / 5.006 deg | 5.181 / 5.006 deg | verifier extra.th_margin |
| near-singular K at rest | not re-measured (same chain) | m_sub under 1 deg on 50 of 204 rest poses | `remeasure/slipper-nose-knuckle-3r_msub_rest_bench.json` |
| cuff twist | not measured (no CAD, no dynamics) | R17 nominal 4.04 deg | - |

## Findings (all watch)

1. **NEW-incumbent-tie-rule (new; proposed catalogue entry R5).** This is section "Lead decision 1".
   - **Pattern:** a lead-change criterion stricter than the user's, set by the lead, applied to challengers but not to
     the incumbent's own lead change, and justified with readings the user retired.
   - **Why it matters:** it withholds a leader the user's rule names (misalignment in the other direction), and it
     hides from the user a choice that is genuinely mixed for the wearer.
   - **Action:** the lead asks the user (above).
   - **Why only watch:** the design's number is not gamed, and a 'gamed' level would block this row, the opposite of
     the finding.
2. **NEW-strap-dilution (carried, upheld).** The bench edge's in-band part is a sampling effect:
   - the equal-strap bench reads 18.67;
   - part-weighted in-band is 0.925 against 0.924.

   The same reading also erases the incumbent's own 0.18 lead change, so the artefact is family-wide, not this row's.
   The held edge survives it: 22.90 against 23.45.
3. **T1 (carried, upheld).**
   - Bench pose 203 has metal 0.263 mm off the skin and is worth 0.29.
   - 6 of the 11 extra held poses carry metal under 2 mm.
   - At 2 mm the bench reads +1.82 and the held +0.15.
   - Report only.
4. **T5 (carried, upheld).**
   - Contact is deeper: 20.24 against 14.75 mm on the bench, 60.97 against 46.12 mm held out.
   - There are new contacts on the hanging, rotated arm (835, 978).
   - Size the knee on the low-elevation, extreme-rotation held poses.
5. **M5 (carried).** The cuff twist and R17 of the new knee have never been measured. Measure them on the gen-7 CAD
   with the knee re-cut.
6. **G4 (carried).** The lead's near-singular K at rest: m_sub is under 1 deg on 50 of 204 rest poses.
7. **T3 (carried).**
   - The held `th` margin is 5.006 deg, 0.006 above the line, and a +-0.3 deg K-phase error crosses it.
   - The dowel's held margin is 0.74 deg.
8. **NEW-ws-inband (carried, better than the lead).** At elevation 90-140, 16.8 % of the metal sits above 14 mm on the
   bench (max 30.7 mm). The lead's figure is 19.9 %.

**Resolved since the last audit.** NEW-tie-headline: the row now carries `leader_ruling: tie: slipper-nose-...`, which
cites the non-gamed skeptic entry of 17:57:13Z. The page's headline rule (`docs/dashboard/simple/index.html` line 235)
excludes tie rows, so the headline no longer crowns this row.

**Still open (reporting, tool reason).**
- The row's verdict text begins "SCREENED".
- The dashboard `gap` column shows the sweep best, 12.5 (score 95.45), 5.78 under the verified number.

**Patterns walked and found absent this hour.** None of these changed, since the claim, model and verifier did not
move: T2, T4, S1-S5, M1-M4, P1-P4, R1-R4, G1-G3, G5, G6.
- P4: no bench, judge or metric file is in the row's 5 commits.
- G5: complexity recomputes to 18.5.

## Numbers I could not get, and why

- **No new re-wear.** The box was saturated (load 15.5 on 4 cores), the farm is closed, and the claim did not move.
- **The new knee's cuff twist and R17:** no CAD and no dynamics run exist for this row.
- **m_sub at rest for this row:** it was not re-run, because the chain is identical to the lead's.
- **Per-pose q3' near the stops:** the re-wear records only the range.
- **The pooled CI of each earlier lead change at equal strap:** that would need new reweighted dumps for the
  incumbents. It is not measured.

## Proposals (measurement, rule or reporting changes; not applied, none feeds the verdict)

- **C5. Board shows a rule conflict, not a settled tie.** When a challenger is ahead on the plain verified gap on both
  legs and the lead rules a tie by a rule the user did not set, the row shows "ahead by the user's plain-gap rule; lead
  ruled tie (rule: ...), user decision pending".
  - Effect today: this row only. No number changes.
- **C6 (a TIGHTENING; for the user, not the lead).** Make the round-12 tie rule a user rule, apply it to every lead
  change, and fix its boundary.
  - The boundary: "the CI90 strictly straddles 0, i.e. lower < 0 < upper". With that, [x, 0.00] and [0.00, x] are
    decided, not tied.
  - Measured effect on every lead change on file:
    - roller over sidecar: a tie, and roller wins the complexity tie-break (20.25 against 25.5), so no change;
    - slipper over roller: [-0.40, 0.00] is decided for slipper, so no change;
    - conecut over slipper: [-1.46, +0.09] is a tie, and slipper wins the complexity tie-break (18.25 against 18.5),
      so no change;
    - desmo-slipper against slipper: [0.00, 0.53] is decided against desmo, so no change.
  - With the user's plain-gap rule instead, the only change is that conecut leads.
- **P-T1. Selftest hard set.** Make `LEADERS` follow the board, not a hand list: the verified lead plus every row with
  a `tie` ruling against it, plus the 4-active pick.
  - Effect today: slipper-nose and conecut join the hard goal, and both read clean.
  - Also report the non-hard rows' false positives and lost true positives in the PASS line, so it does not read as
    a full pass: today that is 6 rows, with 2 lost true positives on sidecar-roller-flank.
- **P-T2. Test the "never resolved" guard.** Add a mutation that feeds a synthetic upheld complexity ruling (evidence
  "5 active joints", the record fixed) through the resolution path. It must count as a lost true positive, not as
  resolved.
  - Also match on the check's own hard-rule reasons (`active DOF > cap 4`, `passive translations > 2`) rather than the
    skeptic's free text.
- **Carried, from the 17:27 audit:**
  - C1: near_touch and dominance should use only files that reproduce the claim;
  - C2: S6 dilution;
  - C3: T6 stop relabel, made symmetric as the skeptic required;
  - C4: the board headline needs a ruling when the paired CI spans 0.


---

*Below this rule (2026-10-17, 18:20 UTC): the earlier skeptic section of the 17:27-17:58 audit, kept as written.*

## Skeptic (2026-10-17, 17:50-17:58 UTC)

Ledger entry 2026-10-17T17:57:13Z, by skeptic, run `skeptic:conecut-knee-knuckle-3r`.

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence. 10 of 11
reasons are upheld and 1 is refuted. Rulings: `docs/alignment/conecut-knee-knuckle-3r.rulings.json`.

**How I checked.**
- I re-derived every number from the raw per-pose dumps with my own scripts. I did not import the audit tool.
- New tool: `tools/alignment_skeptic_why_labels.py`. It leaves the models unchanged and reads kinematic labels only,
  under the frozen protocol. Its fit gaps, 13.0 and 12.5, reproduce both fast claims.
- New evidence: `docs/alignment/remeasure/conecut-knee-knuckle-3r_skeptic_why_held.json`.
- Local only: niced, OMP_NUM_THREADS=1, 2 processes, about 15 s each. The farm was not used.

### Rulings

1. **dominance: upheld.**
   - Re-derived from the dumps: plain 18.28 against 18.49, and at 2 mm 34.84 against 33.02.
   - Both sides use the same harness: exact, frozen protocol, Bench(110,360).
   - The c_dominance rule gives watch, capped (A1 is retired). This is report-only.
2. **reporting: upheld.**
   - The row's verdict begins "SCREENED" while its status is verified.
   - morphs.json (17:43) has sweep_gap 12.5 against v_gap 18.28, 5.78 apart. 12.5 reads as score 95.45.
3. **T1: upheld.**
   - Pose 203: cmin 0.263 mm, min_mm 0.716 mm. The lead does not evaluate it.
   - Against the lead, 203 is worth 0.29, not 0.55 (0.55 is the value against the no-stop control). Without it the
     bench reads 18.57, behind the lead's 18.49, so the conclusion stands.
   - Held out: the 11 new poses sit at 0.758-3.68 mm, 6 of them under 2 mm.
   - Correction: the held 3 mm column recomputes to 82.52 / 79.04 (+3.48), not 83.12 / 79.25 (+3.87).
4. **NEW-strap-dilution: upheld.**
   - With the strap reweighted to the lead's count (verifier C4 rule), the bench reads 18.67 and the held wear 22.90.
   - Chain-only in-band (no E, boss, pad or knee) is 0.859 against 0.869.
   - Excluding only E, it is 0.8855 against 0.8864. The knee group gained in band, and hub 2 and the crank lost.
5. **NEW-stop-relabel: REFUTED, on apples to apples and wearer cost.**
   - Under the frozen protocol the lead labels held 752, 897 and 965 'slide'. The same goes for the lower-stop poses
     392 and 530. 'Slide' is the lead's knee-window stop (CLAUDE.md (5)). The lead's slide count is 32, equal to its
     verifier's.
   - The lead's dump has ev false at all five poses, so its 23.45 also charges them as reach only.
   - Charging them as contacts here (22.72) but not on the lead is a one-sided adjustment. Like for like, the held edge
     at these poses is 0.
   - The wearer meets a hard stop at these poses in both designs.
   - Correction to the count: J3MIN also cuts 392 and 530 (q3' -112.49 / -114.49). Both pass the parts check
     (clearance 1.31 mm, equal to the taken minimum 1.3146) and would be contacts at -1.11 / -9.68 mm. A one-sided T6
     count is therefore 5 poses (+0.56), not 3.
6. **T5: upheld.**
   - Bench: 4 contact poses, 20.24 mm summed. Against DEPTH_REF sidecar-longdyad (6.23 mm) that is x3.25 and +14.01 mm,
     past both the 2x and the 5 mm lines.
   - Held out: 14 poses, 60.97 mm, against the lead's 10 and 46.12 mm.
   - New contacts on the hanging, rotated arm: 835 (-3.55 mm) and 978 (-1.33 mm), where the lead's metal clears the
     skin by 0.81 / 0.62 mm.
7. **NEW-tie-headline: upheld, and live now.**
   - My copy of the page's headline rule, run on morphs.json at HEAD, picks this row (18.28, no ruling).
   - Citation fix: "NOT a leader" is in the row's `note`. `verification.verdict` does not exist.
8. **M5: upheld.** No judge or pipeline file mentions conecut. The knee's K.psi and K.ang spans are new, so the cuff
   path is unmeasured.
9. **G4: upheld.** The coordinate spans of dK, a1e and msub equal the lead's. The lead's m_sub at rest is under 1 deg
   on 50 of 204 rest poses.
10. **T3: upheld.** The held th_margin minimum is 5.006 deg with 0 poses under 5. The C1 residual is 0.015 deg.
11. **NEW-ws-inband: upheld.** At elevation 90-140, 16.8 % of the metal is above 14 mm on the bench and 14.9 % held
    out, with a maximum of 31.46 mm.

### Missed by the auditor (for the next audit; not in this verdict)

- **The stop count is short.** The held relabel count is 5, not 3. 392 and 530 are lower-stop poses that pass the
  parts check and would be contacts, at -1.11 and -9.68 mm. The audit called every lower-stop pose a parts clash, but
  that holds on the bench only.
- **Proposal C3 (T6) has to be symmetric.** Every 'not evaluated' kinematic label removes a pose from the contact
  denominator in the same way: fold, the knee-window 'slide' and 'j3stop'. Applying T6 to one row's dowel and not to
  the reference's knee window penalises only one side. Its measured effect therefore needs the reference's slide poses
  re-evaluated without the stop too (32 held on the lead).
- **Two corrections.** The held 3 mm near-touch reads +3.48, not +3.87. Pose 203 is worth 0.29 against the lead, not
  0.55. Neither changes a conclusion.

**Final verdict: WATCH.**

---

*Below this rule: the skeptic of the 18:03 hourly audit.*

## Skeptic (2026-10-17, 18:14-18:22 UTC, hourly audit of 18:03)

Ledger entry 2026-10-17T18:21:12Z, by skeptic, run `skeptic:conecut-knee-knuckle-3r`.

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence. 9 of 10
reasons are upheld and 1 (T5) is refuted. Rulings: `docs/alignment/conecut-knee-knuckle-3r.rulings.json`.

**How I checked.**
- Every number was re-derived from the per-pose dumps, the probe files and the verifier files with my own scripts.
  I did not import the audit tool or `tools/alignment_paired.py`.
- My own paired bootstrap ran over bench + held pooled, with resampling within kind (seeds 1 and 2, 4000 resamples).
- Nothing new was worn and no file the running agents use was touched. Local only, niced, `OMP_NUM_THREADS=1`, one
  process, a few seconds each. The farm was not used.

### Rulings

1. **dominance: upheld.**
   - The plain gap reads 18.29 against 18.48 from the dumps (the files' rounding of 18.28 / 18.49).
   - At 2 mm: bench 34.84 against 33.02 (+1.82), held 37.11 against 36.95 (+0.16).
   - Same harness on both sides. The c_dominance rule gives watch, capped. Report-only.
   - Taken poses under 2 mm: 33 against 30 on the bench, 71 against 67 held.
2. **reporting: upheld.**
   - The row's verdict begins "SCREENED".
   - `morphs.json` at HEAD (3a4a1a0, 18:13) has gap and sweep_gap 12.5 against v_gap 18.28: 5.78 apart, which reads as
     score 95.45.
   - The lead carries the same defect (13.0 against 18.49, watch in its audit json).
3. **NEW-incumbent-tie-rule: upheld, with two corrections.**
   - **Provenance.**
     - The user's rule is CLAUDE.md line 96, added by d0778dd at 01:39.
     - The tie rule first appears in 0c5b95b at 13:31 (`git log -S` finds nothing earlier). The design dates from
       a56358d, 16:06.
   - **The ruling text.** The `leader_ruling` cites near-touch poses, the equal-strap 18.67 and deeper contact. It never
     names the CI rule or the complexity tie-break.
   - **Complexity** (`tools/simplicity.py` today): 18.25 for the lead against 18.5 here.
   - **The tie is robust under the lead's rule.** My bootstrap gives [-1.45, +0.10], P 0.92, against the file's
     [-1.46, +0.09], P 0.918.
   - **Under the user's rule as written, this row leads:** 18.28 against 18.49, and held 22.38 against 23.45.
   - **The dilution-free reading.** On the part-weighted in-band, every one of the six wears is at least 0.921, so the
     in-band term is 0. This row then reads +0.25 on the bench, -0.51 held and -0.29 pooled. The incumbent's own change
     reads 0 / -0.11 / -0.08. So the "erase" reading leaves this row's pooled edge larger than the edge the incumbent
     won the lead on.
   - **Correction 1.** The incumbent's CI upper bound of 0.00 is a hinge artefact, not a tie.
     - In 4.8 % of my resamples the difference is exactly 0, because both resampled in-band terms clip at the 0.90
       hinge.
     - That mass sits right at the 5 % tail. My seed gives [-0.398, -0.018], P 0.952.
     - So "the incumbent is a tie too, read literally" depends on the seed.
     - Retroactive application would change no past outcome either way, because of the complexity tie-break.
   - **Correction 2.** "All of it in-band" holds for the incumbent's bench edge only. Its pooled split is reach -0.08,
     in-band -0.17.
   - **What stands.** The lead's rule conflicts with the user's rule. That conflict is real and it is the user's call.
4. **NEW-strap-dilution: upheld.**
   - The strap really is longer metal: the verifier's C4 scales the sample count by sampled length.
   - At 104 samples the gap reads 18.67 on the bench and 22.91 held.
   - Part-mean in-band: 0.9249 / 0.9237 here, 0.9241 / 0.9230 on the lead, 0.9225 / 0.9214 on roller-longdyad.
   - The held in-band is 0.89999 exactly, so the claim sits on the 0.90 hinge, and the strap carries it there.
5. **T1: upheld.**
   - Pose 203 sits at cmin 0.263 mm. Given the lead's treatment (ev false), the bench reads 18.57, behind 18.49.
   - The 11 held-only poses lie at 0.758-3.68 mm, 6 of them under 2 mm.
   - At 2 mm: bench +1.82, held +0.16 (the reason's +0.15 is rounding).
6. **T5: REFUTED, on (b) and (d).**
   - **(b) The documented threshold is not met.**
     - Section 5 runs the audit with `--ref <current verified lead>`. The T5 watch needs at least 2x the reference's
       summed depth and at least 5 mm more.
     - Against slipper-nose: x1.37 on the bench (20.24 against 14.75 mm) and x1.32 held (60.97 against 46.12 mm).
     - The auditor's own run this hour (`--ref slipper-nose`) reads `contact_depth` ok.
     - It fires only against `DEPTH_REF = sidecar-longdyad` (tool line 301). That constant is labelled "the verified
       3-active lead", but that row has not been the lead since before 06:23.
     - The lead fires against it too (x2.37), so it does not separate the two rows.
   - **(d) The depth-blind trade is absent.**
     - The extra contacts are charged in the plain gap: contact split +0.53 on the bench and +0.44 held.
     - The mean depth per contact is lower here: 5.06 against 7.38 mm on the bench, 4.36 against 4.61 mm held.
     - The hanging-arm contacts 835 (-3.55 mm) and 978 (-1.33 mm) are real. They are priced as contact, not hidden by
       depth.
7. **M5: upheld (missing measurement).**
   - No conecut file exists under `judge/` or `pipeline/`, so there is no CAD, no dynamics run, no R17 and no cuff twist.
   - The lead's forward bound reads raw twist 5.00081 deg at mu 0.15 (`_m5_forward_bound_fullcad_raw.json`). Its new
     gate gives moves_freely false.
   - The knee path is new (K.ang 59.3-107.1 against 86.2-153.2), so the lead's numbers do not transfer.
8. **G4: upheld (carried).**
   - The dK, a1e and msub spans equal the lead's.
   - The lead's `_msub_rest_bench.json` shows lt1 50 of 204.
   - There is no rest file for this row.
9. **T3: upheld.**
   - The th margin is 5.006 held (lt5 0) and 5.181 on the bench.
   - The J3 stop_margin_deg is 0.74 held and 2.7 on the bench.
   - No tolerance study is on file.
10. **NEW-ws-inband: upheld.**
    - Bench, elevation 90-140: in-band 0.8315, 16.8 % of the metal above 14 mm, max 30.74 mm. Held: 0.8478, 14.9 %,
      max 31.46 mm.
    - The lead reads 0.8004 / 19.9 % on the bench and 0.8218 held.
    - Better than the lead, but it is unscored metal past the 14 mm pass line.
    - The report table's "max 31.5 mm" is the held figure.

### Missed by the auditor (for the next audit; not in this verdict)

- **The T5 default reference is stale.**
  - `DEPTH_REF = "sidecar-longdyad-knuckle-3r"` (tools/alignment_audit.py line 301) is the default `contact_depth`
    reference. The self-test also uses it to replay the T5 rulings (line 825).
  - Section 5 prescribes the current verified lead.
  - Sidecar is the shallowest verified row (6.23 mm bench), so every challenger, and the lead itself (x2.37), fires T5
    against it.
  - The 17:57 skeptic's T5 uphold on this row rested on that constant.
  - Proposal: make `DEPTH_REF` follow the board's verified lead, as P-T1 proposes for `LEADERS`. Alternatively, keep a
    fixed best-in-class depth reference and document it as that, not as "the lead".
  - Measured effect today: this row's and the lead's T5 both read ok.
- **The literal "CI includes 0" tie rule reads hinge artefacts as ties.**
  - The (0.90 - in-band)+ term clips at 0, so a pair of rows whose in-band sits near 0.90 gets an atom of exactly-0
    resamples. That atom is 4.8 % for slipper over roller, right at the 5 % tail, so the bound reads 0.00 or -0.018
    depending on the seed.
  - The same holds for desmo's [0.00, 0.53].
  - Proposal C6's strict-straddle boundary removes the seed dependence. Its measured effect is unchanged (no outcome
    moves).
- **The claim's held in-band is 0.89999.** It sits on the hinge to 5 decimals, and the longer strap carries it there.
  Any part-weighted or equal-strap reading moves it below 0.90. This is the S6 dilution seen from the held side, and it
  is not new gaming.
- **Two factual slips in the NEW-incumbent-tie-rule reason**, neither of which changes the finding:
  - "100 % / all of it in-band" is true only of the incumbent's bench edge;
  - the incumbent's [-0.40, 0.00] is seed-dependent (see above).

**Final verdict: WATCH.**
