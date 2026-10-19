# Alignment audit: conecut-knee-knuckle-3r

This is the hourly audit of 2026-10-17 20:03 UTC (20:03-20:12). It was due for the lead's commit cf106a2 (19:22), which
followed the 19:20 new-leader audit: (1) tools/alignment_audit.py 2026-10-17.6 (`PREV_LEAD` = slipper-nose; the lead's
own T5 compares with it); (2) the row's verdict text now starts "VERIFIED LEAD"; (3) the row doc's suggestion to add
held-out pose indices to a search bench is struck. The box is loaded (load 11 on 4 cores) and the farm is closed, so the
audit is lean: file reads, the audit, the selftest and two read-only probes of a few seconds each.

- **Ledger entry:** 2026-10-17T20:07:38Z, by auditor, run `audit:conecut-knee-knuckle-3r`. Verdict **watch**, tool
  verdict watch. Reasons: 1 tool reason (reporting) and 9 judgement findings, all watch.
- **Checks:** `docs/alignment/conecut-knee-knuckle-3r.json`, 13 checks, tool 2026-10-17.6, default reference.
- **Findings:** `docs/alignment/conecut-knee-knuckle-3r.findings.json`.
- **No re-wear.** The claim did not move: cf106a2 changed only the row's verdict text (v_gap 18.28, gap 12.5 unchanged).
  The re-wears on file reproduce the claim: `remeasure/conecut-knee-knuckle-3r_bench.json` 18.28 (17:31), `_held.json`
  22.38 (17:36); the per-pose dumps recompute to 18.29 / 22.38.
- **New file:** `remeasure/conecut-knee-knuckle-3r_refswap_2003.json` (where the 2026-10-17.6 swap fires; the
  dominance check against the current lead / previous lead on every verified row; proposal measurement only).

## Verdict: WATCH, claim v_gap 18.28 (score 93.35), held out 22.38

Nothing in the number is gamed and no hard rule is broken; the lead stands. Of the three changes, the T5 fix works as
intended and the verdict headline is now honest. Two things are still open. The dominance check is blind for the lead
(and, by default, for every non-sidecar row). The held-out-indices advice the lead struck in the row doc still sits,
unstruck, in docs/concepts/ROUNDS.md, the file the planner reads.

## Question 1: the 2026-10-17.6 T5 swap

**The code does exactly what the commit says.** Line 411 of tools/alignment_audit.py:
`if ref == rid and rid == DEPTH_REF and PREV_LEAD != rid: ref = PREV_LEAD`. A probe over all 87 rows, once with
ref = the row itself and once with the default reference, finds the swap firing on this row only, in both modes
(`refswap_2003.json` swap_fires_on). It cannot fire for any other row, because it needs `rid == DEPTH_REF`. An explicit
`--ref` to another row is untouched: lead vs sidecar-longdyad still reads watch, x3.25 bench / x1.71 held. This audit's
T5 reads bench 4 contact poses, summed 20.24 mm, deepest 8.93 mm vs slipper-nose 14.75 mm over 2 (x1.37, +5.49 mm), and
held 14 poses, 60.97 mm, deepest 9.86 mm vs 46.12 mm over 10 (x1.32, +14.85 mm). That is ok under the 2x / 5 mm rule,
and it matches the 19:20 skeptic's numbers. **SELFTEST PASS** (tool 2026-10-17.6, 5 hard leaders, every mutation
fires).

**Dominance still reads "no reference" for the lead. It should use PREV_LEAD too (proposal P-D1b below).** `audit()`
passes ref=None to `c_dominance` unless `--ref` is given or the id starts with "sidecar-". So "no reference" is the
default for all 84 non-sidecar rows, not only for the lead. Read in memory against PREV_LEAD, the lead is **watch**:
+0.21 plain but -1.82 at 2 mm (34.84 vs 33.02). The lead's whole plain edge over the lead it displaced is smaller than
the amount it loses at 2 mm. This is report only, because the user retired the A1 gate.

**The selftest has a stale label.** The mutation "reference vs itself: contact_depth ok (want ok)" no longer exercises
the "this is the reference" branch. After the swap it compares this row with slipper-nose and passes because x1.37 < 2.
If the lead were ever >= 2x deeper than PREV_LEAD, a TRUE T5 watch, the selftest would FAIL on a correct reading. The
branch itself still works: with PREV_LEAD patched in memory to the lead, it returns ok, "this is the reference". The
hard set `LEADERS` still holds neither this row nor slipper-nose.

## Question 2: is the verdict text honest, and does the board still contradict it?

**The headline is honest.** "VERIFIED LEAD 18.28 (score 93.35), held out 22.38 (lead since ~18:21 UTC by the user's
plain-verified-gap rule; ledger WATCH)" matches the verifier, the ledger and the user's rule. The tool's "verdict text
still reads as a self-measured screen" reason no longer fires.

**Two strings are still wrong or stale:**
- **The screen note** is kept behind "Screen note as written:". The same field therefore still says "SCREENED - a
  measured TIE with the lead, not a new leader" and "203 at 0.72 mm". As labelled history that is acceptable. But the
  203 figure understates how close the metal comes. 0.716 mm is the chain's min_mm. The lowest metal at bench pose 203
  (ws 0/90/45, taken) is 0.263 mm (cmin, on the cuff side; `remeasure/conecut-knee-knuckle-3r_bench_perpose.json`).
- **docs/dashboard/data/morphs.json** (built 19:58) carries:
  - the same verdict;
  - gap / sweep_gap 12.5 (score 95.45, the self/fast best) beside v_gap 18.28. This is the tool's one remaining
    reporting watch;
  - `frozen_gap` null on a verified row;
  - `alignment_reasons` still quoting the 19:20 entry ("verdict text still reads as a self-measured screen", "the T5
    reference is now this row itself"). These are stale until the board is rebuilt from this ledger entry.

The events and docs/HANDOFF.md carry the tie -> lead sequence with timestamps. That is history, not a contradiction. No
other board string calls this row a tie or says it is not the leader.

## Question 3: is anything still pointing a search at held-out indices?

The row doc's "What next" item 1 is struck correctly (docs/concepts/conecut-knee-knuckle-3r.md lines 261-266). Line 204
names the same indices as a description of the held contacts, not as a prescription. **Still live:**
- **docs/concepts/ROUNDS.md lines 2177-2179** (round 12 lesson 6): "poses 764 / 835 / 907 / 978 / 1047 ... those poses
  belong in the envelope search bench". This is unstruck, in the file the planner reads to steer the next round. It is
  the same leak the lead struck in the row doc.
- **docs/concepts/ROUNDS.md line 1858** (an older lesson): "searched on the envelope bench and selected held out". This
  is selection on the held-out split.
- **docs/concepts/desmo-conecut-knuckle-3r.md lines 22-25** (round 13, audited in the main loop): the drive synthesis
  input includes "the K, q2 and crank angles the drive must follow on every bench and held-out pose". This has the same
  form as this row's drift cloud (finding P2), and is passed on for that row's in-loop audit.

**No script points a search at those indices.** grep for 764 / 835 / 907 / 978 / 1047 finds only the three docs above.
Of the 32 Python files that use `held_bench` outside docs/concepts/verify:
- the 11 in docs/concepts/models call it only for their "held" wear (nc == -1);
- tools/env_bench.py excludes every fresh pose within 2 deg of a held-out pose (EXCL 2.0, asserted);
- the polish tools (knee_polish, knee_polish2, osn_polish, env_polish, inband_env_polish) wear held out for the claim
  only;
- the rest are audit or research analyses.

I did not edit any of these files. The action is the lead's: strike ROUNDS.md lesson 6's last clause and line 1858's
"selected held out", as was done in the row doc.

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

## Findings (all watch; `conecut-knee-knuckle-3r.findings.json`)

- **NEW-self-reference (updated, half fixed).** T5 now compares with PREV_LEAD: ok, x1.37 / x1.32. Three things remain:
  - dominance is blind by default; against PREV_LEAD it reads watch (+0.21 / -1.82);
  - the selftest's "reference vs itself" mutation now tests lead vs PREV_LEAD, so a true T5 watch on the lead would fail
    the selftest;
  - DEPTH_REF and PREV_LEAD are hand-set, and the hard set holds neither lead.

  Why the exo is not better: the instrument still cannot say whether this lead change moved metal closer to the arm. It
  did: 33 vs 30 taken bench poses under 2 mm, and deeper contact summed. Action: proposals P-D1b and P-T1b.
- **R1 (updated).** The headline is honest. Still open: the screen note's "203 at 0.72 mm" (true lowest metal 0.263 mm),
  morphs.json gap / sweep_gap 12.5 beside v_gap 18.28, `frozen_gap` null, and the stale alignment_reasons until the
  rebuild. Action: the lead corrects 203 to 0.26 mm (cuff) / 0.72 mm (chain), and the board shows the verified number
  first.
- **P2 (updated).** This row's own search read held-out poses, with nil measured effect (0 of 352 prefilter flips). New:
  the advice the lead struck lives on in ROUNDS.md lesson 6 (lines 2177-2179) and line 1858. desmo-conecut's drive
  synthesis takes held-out joint angles as input. Action: the lead strikes the ROUNDS.md lines, and desmo-conecut's
  in-loop audit checks its drive input.
- **T1 (carried).**
  - 16.56 points of the bench claim live in the 1-2 mm shell.
  - Against slipper-nose at 2 mm: +1.82 on the bench, +0.16 held out.
  - Bench pose 203 is taken at 0.263 mm.
  - The claim config is the plain-fast best (12.50), not the near-touch objective's pick. That pick (k 311) wears
    18.84 / 23.90.
- **T3 (carried).**
  - The fold margin is 5.006 deg held out, and a ±0.3 deg K-phase build error crosses 5 deg.
  - The held number needs J3MIN in a 1.33 deg window, (-112.49, -111.16).
  - The fit bench has no pose in q3' -112.79 to -98.43.
- **NEW-strap-dilution (carried).** At equal E-strap samples the bench reads 18.67, behind 18.49. The held edge
  survives at 22.90.
- **M5 (carried).**
  - Cuff twist and R17 for the re-centred knee have never been measured (the L1 build is running now).
  - The J3 dowel's bearing s0 is 2.16 at the felt line.
- **G4 (carried).** The lead's chain has m_sub under 1 deg on 50 of 204 rest poses (near-singular sub-dyad at rest).
- **NEW-ws-inband (carried).** Unscored workspace in-band is 0.868 bench / 0.871 held, against 0.901 scored.

## Numbers I could not get, and why

- **A new re-wear.** The claim did not move, the box is loaded and the farm is closed.
- **R17, cuff twist and m_sub at rest for this knee.** No CAD and no dynamics run exist yet. The L1 build
  (`pipeline/concept_l1/build_conecut_l1.py`, score_design on l1_conecut-knee) is running as of 20:03, so the next
  audit can read R17 from it.
- **Dominance against PREV_LEAD under the tool.** It is measured in memory only (`refswap_2003.json`), because the
  tool's default passes no reference.

## Proposals (not applied; none feeds the verdict)

- **P-D1b. Dominance default reference: the lead compares with PREV_LEAD.** This tightens what the lead row is checked
  against. Measured effect on all 27 verified / cad rows (`refswap_2003.json` dominance_proposal):
  - **lead vs PREV_LEAD only:** 1 row moves, this one, ok -> watch (+0.21 / -1.82). The verdict is unchanged (already
    watch).
  - **every row vs DEPTH_REF, as written:** 10 rows go ok -> watch only because they have no 2 mm numbers ("cannot
    compare"). That would be noise, so a "cannot compare" result must read ok (report) before this variant is
    adopted. The 2 sidecar rows go watch -> ok, because they are behind the lead plain. Recommended: lead vs PREV_LEAD
    only.
- **P-T1b (replaces P-T1).** Split the selftest mutation in two:
  - (a) "this is the reference" branch, with PREV_LEAD patched to DEPTH_REF in memory: want ok. Measured ok.
  - (b) lead vs PREV_LEAD: computed and reported as info, never pass / fail. A true finding must not fail the
    instrument's regression test.

  Also add the lead and PREV_LEAD to `LEADERS`. Effect today: none on any level. conecut (TP 1 FP 0 FN 0) and
  slipper-nose (TP 2 FP 0 FN 0) both pass.
- **P-D2 (carried).** Ratchet guard: the T5 reference never gets deeper on a lead change without a stated measurement
  change. Effect today: none (the same 2 watch / 11 ok).
- **P-H1 (carried, widened).** A design's search never reads `held_bench()` or held-out indices, and planner text
  (docs/concepts/ROUNDS.md, round ideation files) never prescribes them. The verifier greps the design's scripts, and
  the auditor greps ROUNDS.md each round. Effect today: 2 ROUNDS.md passages to strike. No number changes.
- **P-S1, P-D3 and C1-C6** are carried unchanged (19:20 audit).

---

*Below this rule (2026-10-17, 20:10 UTC): the skeptic sections of the earlier audits (17:27, 18:03 and 19:03), kept as
written.*

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

---

## Skeptic (2026-10-17, 19:14-19:21 UTC, hourly audit of 19:03)

Ledger: 2026-10-17T19:20:18Z, by skeptic, run `skeptic:conecut-knee-knuckle-3r`. **Final verdict: WATCH** (10 reasons
upheld, 0 refuted; none gamed). Rulings file: `docs/alignment/conecut-knee-knuckle-3r.rulings.json`. Re-derived from
the per-pose dumps (`remeasure/conecut-knee-knuckle-3r_{bench,held}_perpose.json`, which recompute to 18.29 / 22.38),
the tool code, the probe files and the design's scratch scripts. No model re-run (load 10-13 on 4 cores, farm closed).

### Rulings

1. **reporting - upheld.** The row's verdict still begins "SCREENED - a measured TIE"; `morphs.json` gap / sweep_gap
   12.5 against v_gap 18.28, 5.78 apart, over the documented 5-point line (`c_reporting`, line 711).
2. **NEW-self-reference - upheld.** `DEPTH_REF` = this row (line 301), `ref == rid` returns ok (lines 419-420),
   dominance reads "no reference". My own run of `c_contact_depth` over the 24 verified rows with depth on file, with
   the reference at conecut / slipper-nose / sidecar-longdyad: 2 / 2 / 11 watch, 0 rows change level between the first
   two. Against slipper-nose this row's T5 stays ok (x1.37 / x1.32), but its dominance reads watch (+0.21 plain, -1.82
   at 2 mm), a watch the default run hides. A real hole; no number moves today.
3. **T1 - upheld, with an attribution.** Bench < 2 mm 34.84 against 33.02, held 37.11 against 36.95 (my
   re-derivation: a taken pose with min(min_mm, cmin) < X becomes untaken + contact). Taken poses < 1 / 2 / 3 mm:
   bench 3 / 33 / 105 against 3 / 30 / 100; held 13 / 71 / 217 against 14 / 67 / 199 (the auditor's 218 / 200 at 3 mm
   are 1 off). Pose 203 taken, min_mm 0.716, cmin 0.263; pose 205 contact -4.28. **New:** the whole 2 mm deficit is
   cuff-side metal (cmin). Counting chain metal only (min_mm), < 2 mm reads 30.79 against 30.97 bench and 34.88
   against 36.02 held, so this row is better there. At 1 mm it is better on both wears (19.92 / 20.12, 25.23 / 26.55).
   The 1-2 mm metal is the re-centred knee / pad side. Report-only watch stands.
4. **T3 - upheld.** `th` margin 5.006 deg held (`extra.th_margin.min`, lt5 0). The fit-flat interval checks out: in
   `docs/research/conecut_mechanism/stop_geo.json` the nearest fit-bench q3' values are -112.79 and -98.43, with
   nothing strictly between them. The stop-window tool stops inward poses only (exact). Bench 18.02-18.30, held
   22.38-23.44, and the claim is the held-best end.
5. **P2 - upheld, and broader than stated.** `heldleak_check.json`: 0 of 352 flips, but held binds the margin on 218
   configs. The design's scratch scripts read held beyond the knee prefilter (see missed 1).
6. **NEW-strap-dilution - upheld.** From the sampling parts table (E 0.979 over 164 samples): sample-weighted 0.9011.
   With E at the lead's 104 samples it is 0.8961, so the bench reads 18.68 (auditor 18.67), behind 18.49.
   Part-weighted 0.9249. Paired bench split: in-band -0.45 of a -0.20 diff.
7. **M5 - upheld (missing).** No R17 or cuff twist for this knee. The L1 build exists
   (`pipeline/full-exo/designs/l1_conecut-knee/`, 18:51-18:53: design.json, build.json, exo.glb) but no judge output;
   `results.json` holds only an impact-model `knee_twist_deg_per_Nm` 0.123, not the R17 reading.
8. **G4 - upheld (missing).** Only the displaced lead's m_sub at rest is on file (lt1 50 of 204); no conecut msub file.
   Not run: the probe took 465 s on the lead, and the box is saturated.
9. **NEW-ws-inband - upheld.** Probe `ws_elev90_140` in-band 0.8315 bench / 0.8478 held, over14 0.168 / 0.149, d_max
   30.74 / 31.46; slipper-nose 0.8004.
10. **R1 - upheld.** The verdict text is unchanged on the row and the board; 203's 0.72 mm in the text is min_mm 0.716,
    and the cuff side is at 0.263 mm.

### Missed by the auditor (for the next audit; not in this verdict)

1. **P2 is wider than the knee prefilter.** In the design's scratch (`scratchpad/cone/`, 13:34-14:22):
   - `q3.py` (14:05) printed the held-out poses each candidate J3 stop excludes (-100 / -105 / -110);
   - `full_j3stop.py` with `HELD=1` wore a J3-stopped config held out: `full_kw25stop_held.json`, J3MIN -105, held
     22.79, 14:22. That was before the 16:06 sweep that set the LHS J3MIN range to -112..-100;
   - `stopc.py` printed the held cuts of a q1 stop.

   The auditor's "the J3 stop was not tuned on held" holds for the final J3MIN, which is a fit-search output. The
   stop's range, though, was scoped with held counts in view. That effect is not measured; it needs the sweep re-run
   with J3MIN bounds set blind (e.g. -120..-95).
2. **A forward held-out leak in the row doc.** "What next" item 1 (`docs/concepts/conecut-knee-knuckle-3r.md` lines
   261-263) says "Add 764 / 835 / 907 / 978 / 1047 to the envelope search bench". Those are held-out pose indices: in
   the held dump, 3 are taken at 0.51-1.13 mm and 2 are contacts. Followed, it would put held poses into the family's
   next searches. Propose: strike or rewrite the item to name the envelope region (elev 15, axial -135 to -165), never
   held indices.
3. **T1's 2 mm deficit is cuff-side, not chain.** See ruling 3. The next audit should split near-touch by part (min_mm
   chain, cmin cuff) when it compares with the reference.
4. **On file, though listed as not got:** the displaced lead's ws in-band over all taken poses.
   `remeasure/slipper-nose-knuckle-3r_probe_bench.json` probe.ws_unscored inband14 reads 0.856, against 0.868 here.
5. **M5 is runnable now.** The L1 build of this knee landed at 18:51-18:53, so "no CAD" is stale. The R17 and
   cuff-twist judges can run on `l1_conecut-knee`.

**Final verdict (ledger): WATCH.**

## Skeptic (2026-10-17, 20:09-20:17 UTC, hourly audit of 20:03)

Ledger: 2026-10-17T20:15:35Z, by skeptic, run `skeptic:conecut-knee-knuckle-3r`. **Final verdict: WATCH** (10 reasons
upheld, 0 refuted; none gamed). Rulings file: `docs/alignment/conecut-knee-knuckle-3r.rulings.json`.

What I used:
- my own re-derivation from the per-pose dumps, which recompute to 18.29 / 22.38;
- the tool's own `c_dominance` / `c_contact_depth`, run in memory (write=False);
- the stop-window, probe and sweep files, and the L1 build directory;
- the board after its 20:13:38 rebuild (9a3e0c5).

**New measurement:** m_sub at rest for THIS row. I ran `tools/alignment_msub_rest_probe_model.py` (CB_EXACT=1,
nice, 1 process, 244 s). It reproduces the frozen claim to the digit: 18.28, reach 0.7278, in-band 0.9012, contact
0.0106. Output: `remeasure/conecut-knee-knuckle-3r_msub_rest_bench.json`.

### Rulings

1. **reporting: upheld.**
   - After the rebuild, `morphs.json` still has gap / sweep_gap 12.5 against v_gap 18.28. That is 5.78 apart, over
     the 5-point line (`c_reporting` line 715; R2 class).
   - The board labels `gap` as "Claimed gap" (`docs/dashboard/bench.js` line 131). So this row shows a *claimed*
     score of 95.45, over the 95 golden line, beside a verified 93.35.
2. **NEW-self-reference: upheld.**
   - The tool's `c_dominance` with no reference reads "no reference". Against PREV_LEAD it reads watch: +0.21 plain,
     -1.82 at 2 mm. My dumps give the same (2 mm: 34.84 vs 33.02).
   - The line 411 swap needs `rid == DEPTH_REF`, so it can fire on this row only. Line 757 gives a default reference
     only to `sidecar-` ids (3 of the 89 rows now).
   - Selftest line 888 is re-routed by line 411 to slipper-nose, so the "reference vs itself" branch is no longer
     exercised.
   - `LEADERS` holds neither this row nor slipper-nose.
3. **R1: upheld in part; one sub-item is resolved.**
   - Still true: the screen note's "203 at 0.72 mm". Pose 203 has min_mm 0.716 but cmin **0.263**.
   - Still true: 12.5 beside 18.28, and `frozen_gap` null.
   - **Resolved at 20:13:38:** `alignment_reasons` now quote the 20:07:38 entry (`alignment_t` 20:07:38Z,
     `alignment_stale` false).
4. **P2: upheld, and wider than stated.**
   - ROUNDS.md (mtime 20:02:39) still carries line 1858 "selected held out" and lines 2178-2179 ("764 / 835 / 907 /
     978 / 1047 ... belong in the envelope search bench"), both unstruck.
   - desmo-conecut doc lines 22-24 take held-out joint angles as drive input. Its model file has no `held_bench` call.
   - New: the build spec reads held out too (missed 1).
   - Score effect nil: 0 of 352 flips.
5. **T1: upheld.**
   - Bench: shell 16.56 (34.84 - 18.28, over TH watch 15). Against slipper-nose: +1.82 at 2 mm bench, +0.16 held out.
   - Taken poses under 1 / 2 / 3 mm: bench 3 / 33 / 105 against 3 / 30 / 100; held out 13 / 71 / 217 against
     14 / 67 / 199. The auditor's 218 is 1 off.
   - Correction: the claim (sweep index 204) is the objective best under `stop_pen`, at fast 12.50 / 13.66 / 18.80. It
     is not the sweep's raw plain best. That is 11.88 (cma2s-g6-2), rejected by `stop_pen` (row doc lines 126-136).
6. **T3: upheld.**
   - Held-out `th` minimum 5.006 deg, lt5 0.
   - Fit-bench q3' values: -112.791 and -98.431, with nothing between them. Held-out q3' values: -112.488 and
     -111.159.
   - Held-out sweep: 22.38 down to just above -111.1, then 22.49. Bench: 18.29 there, and 18.02 at -110.9.
   - The L1 build keeps the held number only through an acceptance window, -112.40 to -111.25. The fragility is
     written into the build spec, not removed.
   - The ±0.3 deg K-phase crossing is the auditor's arithmetic; I did not re-measure it.
7. **NEW-strap-dilution: upheld.** Sample-weighted in-band is 0.90113. With E at slipper-nose's 104 samples it is
   0.89605, so the bench reads **18.67**, behind 18.49. Held-out in-band is 0.89999.
8. **M5: upheld (missing).**
   - No R17 or cuff-twist result for this knee exists. `l1_conecut-knee/` holds build files only.
   - The running `score_design.py` writes R1 `score.json`, not R17.
   - `build.json` dowel_check s0 0.73 is the inherited J2-stop hand calc, identical in all 7 L1 builds. It is not this
     knee's number.
9. **G4: upheld, now measured on this row.**
   - m_sub at rest: n 205, min 0.0, p10 0.267, under 1 / 2 / 5 deg on 50 / 65 / 107 (39 ws + 11 clip under 1 deg;
     ws 227 / 224 / 283 at 0.000-0.002 deg).
   - This is identical to the displaced lead (50 of 204). The re-centred knee and the J3 stop leave the sub-dyad's
     rest posture as it was.
   - m_plain at rest has min 5.389, and the family reading min 5.181, so the scored fold metric is clean. The
     near-singular sub-dyad at rest is real.
10. **NEW-ws-inband: upheld.**
    - Bench: unscored ws in-band 0.8676, and 0.8315 at elev 90-140 (over 14 mm 0.168, d_max 30.74).
    - Held out: 0.8712 / 0.8478 (d_max 31.46).
    - Scored in-band is 0.9012.

### Missed by the auditor (for the next audit; not in this verdict)

1. **The L1 build's J3 stop acceptance window is set from the held-out split.**
   - `pipeline/concept_l1/build_conecut_l1.py` line 86 specifies "assembled stop -112.40 <= J3MIN <= -111.25 ... (the
     windows that keep the verified bench and held numbers)".
   - The held-out q3' neighbours -112.488 / -111.159 (`stop_geo.json` held) bound the window.
   - On fit evidence, J3MIN could sit anywhere in the 14-deg fit-flat interval (-112.79 to -98.43). The exact bench
     even prefers -110.9 (18.02).
   - So the held-out split now sets a build tolerance. Score effect today: nil. It is P2's pattern moved into the part
     spec, and it hides T3's fragility as a tolerance.
   - Proposal: the build spec states the fit-evidence window, and quotes the held number as a consequence, not as an
     acceptance target.
2. **The board's "Claimed gap" column shows the fast self-measure as the claim.**
   - `bench.js` line 131 labels `gap` "Claimed gap". 10 verified rows read score >= 95 there, 95.20-97.75 (gap
     6.19-13.19), against verified 18.28-20.08.
   - `c_reporting` reads only `sweep_gap`, so a row whose `gap` and `sweep_gap` differ escapes the check
     (inband-rssr: gap 12.79, sweep null).
   - This is systemic (R3 class), not this row's doing. Proposal: `c_reporting` also compares `gap` with `v_gap` on
     verified rows, and the board labels it "self-measured (fast)".
3. **The tool's G4 note can be closed with a number.** This row's m_sub at rest is now on file (not a miss: the number did not exist at
   20:03). The next audit should quote 50 / 205, not "not re-measured".

**Final verdict (ledger): WATCH.** The claim is reproduced exactly: 18.28 / 22.38 from the dumps, and 18.28 in this
probe's frozen re-run. Every reason measured true. Nothing is gamed.
