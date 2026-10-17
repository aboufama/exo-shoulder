# Alignment audit: conecut-knee-knuckle-3r

This is the hourly audit of 2026-10-17 19:03 UTC, run from 19:03 to about 19:20. It was due because this row became the
verified lead (commit c5d3b06, ~18:25). In the same commit the lead changed the auditor (tools/alignment_audit.py
2026-10-17.5: `DEPTH_REF` = the current lead, which is now this row). The box was saturated (load 10-18 on 4 cores) and
the farm is closed, so nothing was re-worn. The audit read files, ran the selftest and ran three read-only probes, each
for a few seconds.

- **Ledger entry:** 2026-10-17T19:13:45Z, by auditor, run `audit:conecut-knee-knuckle-3r`. Verdict **watch**,
  tool verdict watch.
- **Reasons:** 1 tool reason (reporting) and 9 judgement findings, all watch.
- **Checks:** `docs/alignment/conecut-knee-knuckle-3r.json`. 13 checks, tool 2026-10-17.5, default reference, which
  is this row itself.
- **Findings:** `docs/alignment/conecut-knee-knuckle-3r.findings.json`.
- **No new re-wear.** The claim has not moved since the verifier's commit d943974 (17:20). The model file has not
  changed since that commit either. The later row commits only added or removed ruling text. The re-wears on file
  reproduce the claim: `remeasure/conecut-knee-knuckle-3r_bench.json` (17:31) reads 18.28, `_held.json` (17:36) reads
  22.38, and the per-pose dumps recompute to 18.29 / 22.38.
- **New files from this audit:**
  - `remeasure/conecut-knee-knuckle-3r_stopwindow.json` (tool `tools/alignment_stop_window.py`, new);
  - `remeasure/conecut-knee-knuckle-3r_heldleak_check.json`;
  - `remeasure/conecut-knee-knuckle-3r_refaudit.json`;
  - `remeasure/conecut-knee-knuckle-3r_t5ref_levels.json`.

## Verdict: WATCH, claim v_gap 18.28 (score 93.35), held out 22.38

The leader change is sound. Nothing in this number is gamed, no hard rule is broken, and the lead change follows the
user's rule the same way the earlier ones did. The new findings concern the instrument (the T5 reference is now the
lead itself), held-out hygiene in the design's search (no measured effect), and how much of the held edge depends on
where the J3 dowel lands. The held edge's size depends on that; the ranking does not.

## Question 1: the leader change itself

**It is consistent with the user's rule and with every earlier lead change.** The rule (CLAUDE.md, user 2026-10-17):
"a design replaces the lead on the plain verified gap".

| lead change | bench (verified, exact) | held out | file |
|---|---|---|---|
| roller-longdyad over sidecar-longdyad (round 10) | -0.25 (18.66 vs 18.91 in the dumps) | **+1.06 worse** (23.73 vs 22.67) | `remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json` |
| slipper-nose over roller-longdyad (06:23) | -0.18 | -0.28 | `remeasure/slipper-nose-knuckle-3r_vs_roller-longdyad-knuckle-3r_paired_claim.json` |
| **this row over slipper-nose (18:25)** | **-0.21** (18.28 vs 18.49) | **-1.07** (22.38 vs 23.45) | `remeasure/conecut-knee-knuckle-3r_vs_slipper-nose-knuckle-3r_paired.json` |

This row's held edge is the largest of the three, and it beats slipper-nose's own change on both legs. Its bench
edge is 0.04 smaller than roller-longdyad's, and roller-longdyad took the lead while losing held out. The withdrawal of the lead's CI tie rule
(row field `leader_ruling_withdrawn`) resolves the 18:03 finding NEW-incumbent-tie-rule. The rule was the lead's own
and was applied to challengers only. Whether a noise or tie rule should exist is correctly put to the user, not
decided here.

**Nothing blocks it.**
- **Ledger:** no 'gamed' entry; every entry for this row is watch.
- **Hard rules:**
  - 3 active DOF, 0 passive translations, O20 hubs at every joint;
  - MR63ZZ knee pairs (stk 6.0);
  - the knee window is a physical stop that never engages (knee 59.3-107.1 deg inside [25.22, 154.78]);
  - the J3 stop acts on J3's own angle (C1 residual 0.015 deg);
  - `th` margin 5.006 deg, held out, at or above 5;
  - continuity flood full 18.28 (0 dropped), knn 19.97;
  - per-pose dumps on file that reproduce the claim (the lead's 2026-10-17 depth rule).
- **The J3 stop's knife edge does not block it (new, measured).** The fit bench has no pose and no fit-clip frame with
  q3' between -112.79 and -98.43, so any J3MIN there gives the same fit and the same frozen shape. Moving the stop
  inward across that interval reads bench 18.02-18.30 and held 22.38-23.44 (`stopwindow.json`). Both stay ahead of
  18.49 / 23.45 everywhere.
- **The 203 objection does not block it either (new).** Cutting pose 203 with a real stop also cuts contact 205. The
  bench then reads 18.30, not the skeptic's 18.57.

**What the user should know when they read "93.4".**
- **The held edge is -1.07 only at the chosen stop.** At the mean stop place of the fit-flat window it is -0.69, and at
  the shallow end -0.01.
- **The bench edge is mostly E-strap dilution.** At equal strap the bench reads 18.67, behind.
- **Contact is deeper:** 4 / 20.24 mm against 2 / 14.75 mm on the bench, and 14 / 60.97 mm against 10 / 46.12 mm held.
- **The pick is the plain-fast best, not the declared search objective's best.** The search objective was the 1 mm
  near-touch gap. Its own pick, the one-sided CMA, worn exact and held reads 18.84 / 23.90 and would not lead.

## Question 2: the DEPTH_REF change (finding NEW-self-reference)

**It is a hole, with zero measured effect today.**
- **What 2026-10-17.5 did.** It set `DEPTH_REF = "conecut-knee-knuckle-3r"` (tool line 301). For this row,
  `c_contact_depth` then returns "ok (this is the reference)" by construction (lines 419-420).
- **Dominance.** `c_dominance` reads "no reference": `audit()` passes it no default reference (line 757), and with
  section 5's `--ref <current lead>` the lead is its own reference.
- **The selftest locks the hole in.**
  - Its mutation "reference vs itself: contact_depth ok (want ok)" passes.
  - Its hard set `LEADERS` (line 793) holds neither this row nor slipper-nose. The PASS this run (5 hard rows, 0
    failures) therefore says nothing about the current lead.
- **The reference ratchets.** On this lead change it got deeper, x1.37 bench / x1.32 held. A chain of leads, each less
  than 2x deeper than the last, never fires T5.

**Measured readings for this row** (`remeasure/conecut-knee-knuckle-3r_refaudit.json`, the tool imported read-only):

| reference | T5 bench | T5 held | T5 level | dominance (plain / 2 mm) |
|---|---|---|---|---|
| itself (2026-10-17.5 default) | - | - | ok, trivially | "no reference" |
| slipper-nose (the lead it displaced) | 20.24 vs 14.75 mm, x1.37, +5.49 | 60.97 vs 46.12 mm, x1.32, +14.85 | ok | +0.21 / -1.82, watch |
| roller-longdyad (lead before that) | x1.23, +3.78 | x1.22, +11.09 | ok | +0.39 / -1.74, watch |
| sidecar-longdyad (shallowest verified) | 20.24 vs 6.23 mm, x3.25, +14.01 | x1.71, +25.31 | **watch** | +0.63 / -0.81, watch |

**Effect on every verified row** (`remeasure/conecut-knee-knuckle-3r_t5ref_levels.json`). 13 verified rows have depth
on file.
- With the reference at this row: 2 watch (minarc-stop-knuckle-4r, kneeless-roller-knuckle-3r) and 11 ok.
- With the reference at slipper-nose: the same 2 and 11. No row changes level.
- With the reference at sidecar-longdyad: 11 watch and 2 ok (sidecar-longdyad itself, and skin-normal-3r-pin-knee at
  x1.35).

The proposals are below (P-D1 to P-D3). None is applied, and none feeds this verdict.

## Question 3: the dashboard

**The headline is right by the user's rule.** `docs/dashboard/simple/index.html` lines 233-239 take the best verified
row with 3 or fewer active joints and no "tie" / "no lead" ruling: this row, 1 - 18.28/275 = 93.35, shown as 93.4. The
row's `leader_ruling` is '' in `morphs.json`, so the tie-exclusion rule no longer applies. That is correct after the
withdrawal.

**The row text is now false** (finding R1).
- **The verdict text.** The row's verdict, which the dashboard shows, still begins "SCREENED - a measured TIE with the
  lead, not a new leader". It also gives "203 at 0.72 mm", the chain's min_mm, where the dump's lowest metal at 203 is
  0.263 mm (cuff side).
- **The gap columns.** `morphs.json` still shows gap / sweep_gap 12.5 (score 95.45) against v_gap 18.28.
- **The withdrawal note.** `leader_ruling_withdrawn` never reaches the board: `tools/dash_build.py` reads
  `leader_ruling` only (lines 453-460).

## What the wearer gets (measured; the claim is unchanged since the 17:31 re-wear)

| | this row | displaced lead slipper-nose | file |
|---|---|---|---|
| overhead reach (ws elev >= 140), bench / held | 8 / 28, 18 / 71 | 8 / 28, 18 / 71 | `remeasure/*_probe_bench.json`, `_probe_held.json` ws_overhead140 |
| why overhead is lost, bench / held | fold 14, J3 stop 3, contact 3 / fold 36, J3 stop 10, contact 7 | fold 14, knee slide 4, contact 2 (bench) | probe ws_overhead_why_not |
| raised arm, ws elev 90-140 taken, bench / held | 39 / 85, 105 / 229 | 38 / 85, 96 / 229 | probe ws_elev90_140, per-pose dumps |
| all ws taken, bench / held | 262 / 360, 659 / 952 | 261 / 360, 650 / 952 | per-pose dumps |
| taken poses with metal < 1 / 2 / 3 mm, bench | 3 / 33 / 105 | 3 / 30 / 100 | `remeasure/*_bench.json` |
| the same, held out | 13 / 71 / 218 | 14 / 67 / 200 | `remeasure/*_held.json` |
| contact poses, bench (summed, deepest) | 4 (20.24 mm, 8.93 mm at ws 15/165/-60) | 2 (14.75 mm, 9.01 mm) | `refaudit.json` contact_depth |
| contact poses, held | 14 (60.97 mm, 9.86 mm at ws 45/165/-30) | 10 (46.12 mm, 9.05 mm) | same |
| scored clip in-band 2-14, sample / part-weighted | 0.901 / 0.925 | 0.896 / 0.924 | sampling check |
| ws in-band, unscored, all taken / elev 90-140, bench | 0.868 / 0.832 (max 30.74 mm) | - / 0.800 | probe |
| the same, held | 0.871 / 0.848 (max 31.46 mm) | - / 0.822 | probe |
| knee | never engages its window (34 / 48 deg margin, 11.4 / 12.8 mm); 12.0 N per N.m | 32 held slides (0.33 mm); 31.6 N per N.m | row `frozen.knee` |
| J3 stop | 2 mm 440C dowel; held margin 0.74 deg; 3 bench / 10 held overhead poses stopped | none | verifier C2 / C3, probe |
| J3 bearing at the stop | s0 2.16 at the felt line (0.84 N.m); 0.40 with a silicone liner (4.57 N.m), a felt notch | - | `docs/research/conecut_mechanism_redteam.md` |
| springs | the lead's K clock spring; R17 not run for this knee | R17 forward bound fails by 0.0008 deg at mu 0.15 | lead ledger M5 |
| fold margin `th`, bench / held | 5.181 / 5.006 deg | 5.181 / 5.006 deg | verifier extra.th_margin |
| near-singular K at rest | not re-measured (same chain) | m_sub under 1 deg on 50 of 204 rest poses | `remeasure/slipper-nose-knuckle-3r_msub_rest_bench.json` |
| cuff twist | not measured (no CAD, no dynamics) | R17 nominal 4.04 deg | - |

## Findings (all watch)

1. **NEW-self-reference (new; proposed catalogue entry P5, "the instrument's reference is the audited row").** See
   question 2.
   - **Why the exo is not shown to be better:** depth and 2 mm dominance against the row it displaced are not computed
     by the default run. They are: T5 x1.37 / x1.32 (ok), and dominance +0.21 plain / -1.82 at 2 mm (watch).
   - **Action:** proposals P-D1 to P-D3.
2. **T1 (carried, updated).** The details are in the findings file.
   - At 2 mm the bench reads +1.82 against the displaced lead, and 16.56 points live in the 1-2 mm shell.
   - The claim is the plain-fast pick. It carries 1.16 points of metal under 1 mm on the fit bench, where the
     objective's pick carries 0.
   - New: a buildable stop that cuts 203 also cuts contact 205, so the bench reads 18.30, still ahead.
   - Report only.
3. **T3 (carried, new measurement).**
   - The `th` margin is 5.006 deg, and a +-0.3 deg K-phase error crosses the 5 deg line.
   - The J3 dowel's held number needs J3MIN in (-112.49, -111.16).
   - Across the fit-flat interval the held reads 22.38-23.44. The claim is the held-best end, and the ranking holds
     everywhere.
   - **Action:** report the held edge as "-0.01 to -1.07 depending on the stop place, -0.69 at the window mean", and
     the bench as 18.02-18.30, next to the point numbers. Accept the built stop by the red team's encoder band.
4. **P2 (new).** The design's search read held-out poses: `k2.py` imports `held_bench()`, and the LHS knee prefilter
   and the knee re-centring used the drift cloud including held.
   - **Measured effect:** none. 0 of 352 prefilter verdicts flip without held, the objective's knee margin is
     fit-bench only, and the stop was not tuned on held.
   - **Action:** drift clouds for design use bench + fit-clip (+ the envelope bench) only, so the held split stays held
     out in form as well as in effect.
5. **NEW-strap-dilution (carried).**
   - Equal-strap bench 18.67 (behind), held 22.90 (ahead).
   - The held in-band is 0.89999, on the hinge.
   - The artefact is family-wide.
6. **M5 (carried, with red-team numbers).**
   - The re-centred knee has no R17 and no cuff twist on file.
   - The J3 stop dents J3's bearing above 1.81 N.m about J3, which a silicone liner can transmit (4.57 N.m).
   - **Action:** the gen-12 L1 / CAD measures R17 and cuff twist with this knee.
7. **G4 (carried).** The near-singular K at rest is the displaced lead's, on the same chain.
8. **NEW-ws-inband (carried).** Unscored workspace metal: 13 % of it is above 14 mm overall, and 16.8 % at elevation
   90-140 (max 30.7 mm on the bench). This is better than the displaced lead.
9. **R1 (updated).** The row's verdict text contradicts its lead status, and `morphs.json` shows 12.5 against 18.28. See
   question 3.

**Resolved since 18:03.**
- NEW-incumbent-tie-rule: the tie ruling was withdrawn in c5d3b06 and the question was put to the user.
- T5 against the stale sidecar reference: refuted by the 18:21 skeptic, and now read through NEW-self-reference.

**Patterns walked and found absent this hour** (claim, model and verifier unchanged).
- T2: the band read 3-14 mm gives 18.34 against 18.28.
- T4: the J3MIN search walked toward the fit bench's stopped pose 92, not toward a singular posture. The configs that
  admitted 92 were rejected (11.88).
- S1-S5: the flood is full, with 0 dropped. The dowel and groove sit inside the O20 stack, with no skin-facing metal.
  Sampling is part-weighted +2.4 points.
- M1-M4: the stk 6.0 MR63ZZ pair is real. The E strap clears link 2 by 0.63 mm at J3MIN, and the clash sits at q3'
  -115.25, 3.35 deg past the stop (`results.json` E_L2). The knee moves (span 46.7 deg).
- P1: the held drop is +4.10. P3 and R3: all three worn configs are reported. P4: no bench, judge or metric file is in
  the row's commits.
- R2 and R4: `v_gap` 18.28 on the board equals the verifier's.
- G1: 1-3 mm metal is reported under T1. G2 and G3: under M5. G5: complexity recomputes to 18.5. G6: 3 active joints.

## Numbers I could not get, and why

- **A new re-wear.** The claim, model and verifier have not changed since the 17:31 / 17:36 re-wears, the box is
  saturated, and the farm is closed.
- **The held gap with the stop moved outward past -112.49.** That admits held pose 392, whose metal was never measured
  (it was stopped), so it needs a re-wear with J3MIN about -113. The bench is exact to -112.79.
- **R17, cuff twist and m_sub at rest for this knee.** No CAD and no dynamics run exist yet.
- **The displaced lead's ws in-band over all taken poses.** Its probe file was not re-read this hour.

## Proposals (measurement, rule or reporting changes; not applied, none feeds the verdict)

- **P-D1. The lead's T5 and dominance compare with the lead it displaced** (a TIGHTENING of what the lead row is checked
  against). When `rid == DEPTH_REF`, compare with the previous lead (the README / events "NEW VERIFIED LEADER" chain),
  as a "did contact get deeper at the lead change" check.
  - **Measured effect today:** this row's T5 stays ok (x1.37 / x1.32). Its dominance reads watch (+0.21 / -1.82),
    which is the same as the 18:03 ledger. No other row is affected.
- **P-D2. Ratchet guard: the T5 reference never gets deeper on a lead change without a stated measurement change.**
  `DEPTH_REF` = the shallower (summed bench + held depth) of the new lead and the current reference.
  - **Measured effect today:** the reference stays slipper-nose (60.87 mm against 81.21 mm here). No verified row
    changes level: the same 2 watch and 11 ok as with this row.
- **P-D3. Report, never gate, the best-in-class depth.** Each audit's T5 line also prints the ratio against the
  shallowest verified row in the lead's 1-point class (today sidecar-longdyad, 6.23 / 35.66 mm), level unchanged.
  - **Effect today:** the text only. If it were a level, 11 of 13 rows would be watch, which is the pre-.5 reading the
    18:21 skeptic refuted as not separating rows. So it stays a report.
- **P-T1 (carried, now urgent).** `LEADERS` follows the board: the verified lead plus the previous lead plus the
  4-active pick. Replace the "reference vs itself: ok" mutation with "lead vs previous lead: computed, not 'this is the
  reference'".
  - **Measured effect today:** conecut (TP 1 FP 0 FN 0) and slipper-nose (TP 2 FP 0 FN 0) join the hard set, and both
    pass.
- **P-H1. Held-out hygiene for design scripts.** A design's search reads bench, fit-clip and envelope poses only, and
  never `held_bench()`. The verifier greps the design's scripts for `held_bench`.
  - **Measured effect on this row:** none (0 of 352 flips).
- **P-S1. Report stop-placement spread with the claim.** For a design with a hard stop in a fit-flat interval, report
  the bench and held range over that interval (`tools/alignment_stop_window.py`) next to the point numbers.
  - **Effect today:** this row reads bench 18.02-18.30 and held 22.38-23.44. No ranking changes.
- **Carried from 18:03:** C1, C2, C3, C5 and C6 (C5 is resolved by the withdrawal; C6 is for the user).


---

*Below this rule (2026-10-17, 19:15 UTC): the skeptic sections of the earlier audits (17:27 and 18:03), kept as written.*

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
