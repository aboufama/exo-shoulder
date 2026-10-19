# Alignment audit: minarc-stop-knuckle-4r (2026-10-19, hourly)

Auditor run `audit:minarc-stop-knuckle-4r`, 2026-10-19 01:06-01:40 UTC, git c7316ce. Why it was due: the row's last commit
(ec77d25, 2026-10-17 04:55) came after the last audit (04:44). That commit changed only the row's `complexity` field
(33.0 -> 32.5). The claim (`polished_gap` 18.40, pick1; `v_gap` 19.54, BDp), the params, the model files and every
bench / kit file are unchanged since the 02:21 re-wear that reproduced both claims to the digit.

## Verdict and claim

- **Ledger verdict: WATCH** (`tools/alignment_ledger.py`, entry 2026-10-19T01:38:06Z in `docs/alignment/ledger.jsonl`). The
  tool alone gives WATCH (contact_depth, sampling, reporting); the 12 judgement findings are all 'watch'.
- **Claim:** `polished_gap` **18.40** (score 93.31, pick1). The row's `v_gap` is 19.54 (BDp).
- **In one line:** nothing in the number is gamed, but the row now ranks 8th on the verified board, and the 3-joint
  lead conecut-knee-knuckle-3r (18.28 / held out 22.38 / complexity 18.5, 3 joints) beats it on plain gap, held out,
  complexity and joint count. Its texts still
  call it the leader. This audit adds one new measurement: the design re-worn as built under the 2026-10-17 build
  rules, with MR63ZZ knee pins (stk 6.0) and the CAD's physical knee stop (ang_min 30.5). It reads **18.2** on the
  bench (-0.2) and **22.75** held out (+0.06).

## What the wearer gets (measured)

The claim columns are the 2026-10-17 02:21 re-wear (`remeasure/minarc-stop-knuckle-4r_pick1_probe_{bench,held}.json`).
The as-built columns are new in this audit. The as-built runs were stopped at the time box during the contact-aware continuity pass, so their columns
come from the verifier's own output (`..._pick1built_probe_{bench,held}_verifier.json`, kinematic continuity, 0 dropped);
the probe-only rows read "not measured". Both use the same verifier harness (`docs/concepts/verify/minarc-final-polish-verify.py`, unchanged; fit Bench(60,160)
fast -> frozen -> wear Bench(110,360) exact or the 1154 held-out poses; built-stop pricing; kinematic and
contact-aware continuity). Only two params change: `stk` 5.791 -> 6.0 and `ang_min` 26.1449 -> 30.5
(`remeasure/minarc-stop-knuckle-4r_pick1built_params_in.json`).

| measure | pick1 claim, bench | pick1 as built, bench | pick1 claim, held out (fit-60) | pick1 as built, held out (fit-60) |
|---|---|---|---|---|
| gap (plain) | 18.4 | 18.2 | 22.69 | 22.75 |
| reach / in-band14 / follow / contact | 0.75 / 0.8941 / 1.0 / 0.0281 | 0.75 / 0.8936 / 1.0 / 0.0256 | 0.7195 / 0.8916 / 1.0 / 0.038 | 0.7153 / 0.8911 / 1.0 / 0.0339 |
| overhead workspace taken (elevation >= 140) | 7 / 28 | 7 / 28 | 12 / 71 | 12 / 71 |
| workspace poses taken | 270 | 270 | 685 | 681 |
| raised-arm reach by elevation band (taken / total) | 90-120: 28 / 51; 120-140: 13 / 34; 140-160: 5 / 13; 160-200: 2 / 15 | not measured (probe stopped) | 90-120: 79 / 140; 120-140: 28 / 89; 140-160: 8 / 35; 160-200: 4 / 36 | not measured (probe stopped) |
| taken poses with metal < 1 / 2 / 3 mm | 13 / 38 / 171 | not measured (probe stopped) | 27 / 89 / 400 | not measured (probe stopped) |
| gap at 1 / 2 / 3 mm near-touch (reported only) | 23.36 / 41.29 / 156.01 | not measured (probe stopped) | 26.73 / 47.94 / 162.57 | not measured (probe stopped) |
| gap at 1 mm near-touch / poses under 1 mm | 23.36 / 13 | 23.14 / 13 | 26.73 / 27 | 26.61 / 26 |
| contact poses (metal inside the skin) | 11; deepest -13.17 mm (ws plane 15.0 / elev 165.0 / axial -60.0) | not measured (probe stopped) | 35; deepest -14.61 mm (ws plane 45.0 / elev 165.0 / axial -30.0) | not measured (probe stopped) |
| workspace in-band 2-14 (unscored), all / overhead | 0.8581 / 0.9254 | not measured (probe stopped) | 0.8593 / 0.9259 | not measured (probe stopped) |
| K open on taken poses (count, max deg) | 86, 56.244 | not measured (probe stopped) | 209, 56.551 | not measured (probe stopped) |

- **Springs:** one clock spring at K. As built (0.04 N.m) R17 passes upright only: drift 3.72 deg, and 4.12-7.70
  deg with gravity across the thorax. At 0.08 N.m it lags 9.28 deg (`docs/research/pick1_k_hold_check.md`).
- **Stops:** J2 dowel slot at the 5-deg J1-J3 margin (+0.5 built). K stop B at dK 56.65 deg. Knee window ang_min
  26.14 in the claim; the CAD's physical knee stop is at 149.5 deg (ang_min 30.5), and it is applied in the as-built
  columns.
- **Cuff twist:** 2.00 deg upright on R17, up to 3.83 deg with the thorax tilted. That was measured on the CAD with
  iglidur plain knee pins, which the 2026-10-17 build rule replaces with MR63ZZ pairs.
- **Near-singular postures:** own-state J1-J3 margin min 5.623 (bench) / 5.586 (held out). 107 of 380 taken bench
  poses are under 10 deg. In forced poses the plain dyad is 22.8 deg past its own fold. J1 moves up to 31 deg per
  10-fps frame.
- **Overhead:** K is closed on every taken pose at elevation >= 140, so the 4th joint does nothing overhead.

## Findings

All 12 are 'watch', and each is in `docs/alignment/minarc-stop-knuckle-4r.findings.json` with its evidence. One
2026-10-17 finding is dropped: NEW-hub-only-sensing. Sensing is out of scope under the user's ruling (6) of
2026-10-17, and the count already pays for K's encoder as an active joint.

1. **G6: A 4th joint that no longer buys a lead.**
   - Evidence: The board ranks it 8th. The 3-joint lead is ahead on plain gap (-0.12), held out (-0.31), complexity (-14) and joint count.
   - Action: None on the score. Fix the texts (R2).
2. **NEW-overhead-traded: The polish traded overhead for mid-range reach.**
   - Evidence: Overhead taken: bench 7 vs 8 of 28, held out 12 vs 16 of 71 against BDp. K never opens at elevation >= 140.
   - Action: Report overhead taken with every claim (proposal B1 of 2026-10-17).
3. **T5: The contact term is blind to depth.**
   - Evidence: Bench: 11 contact poses, deepest -13.17 mm. Held out: 35, deepest -14.61 mm (hub K wall in the deltoid). sidecar-longdyad: 4 / -4.61 mm.
   - Action: Report the deepest contact with every claim (B2).
4. **M2: The knee pins are not the build rule's component.**
   - Evidence: The claim uses stk 5.791, and the CAD uses iglidur sleeves. With MR63ZZ pairs at stk 6.0 plus the CAD's knee stop, it reads bench 18.2 (-0.2) and held out 22.75 (+0.06).
   - Action: Proposal C1: state the as-built numbers next to the claim.
5. **T4: The knee window as claimed is not the knee stop as built.**
   - Evidence: ang_min is 26.14 against the CAD's 30.5, and the knee reaches 152.75 deg held out (4 poses past 149.5). With the stop applied, held out reads 22.75 (+0.06).
   - Action: Proposal C1. FINDINGS line 1847's open item now has a number.
6. **R2: Stale leader text.**
   - Evidence: README line 33 says 'Best verified overall', but 7 verified rows are ahead (one marked gamed). The row and dashboard verdicts open with 'VERIFIED LEADER'. The refuted 6.19 is still the sweep record, and mechanism.notes is stale.
   - Action: Proposal C2.
7. **NEW-mixed-protocol: Two held-out protocols side by side.**
   - Evidence: README shows 21.31 (env fit) next to 22.67 (fit-60). On one protocol the values are 22.69 and 22.67.
   - Action: Proposal B3 (2026-10-17) stands.
8. **G4: Near-singular postures.**
   - Evidence: 107 of 380 taken bench poses have a margin under 10 deg. The margin exists only because K opens.
   - Action: A MuJoCo feel check before the spring is frozen.
9. **M5: A spring with a narrow window, and cuff twist.**
   - Evidence: R17 passes upright only. Drift is 4.12-7.70 deg with the thorax tilted, and the cuff twists up to 3.83 deg.
   - Action: A posture sweep in R17, re-run with MR63ZZ pins.
10. **T1: Metal parked just outside the contact line (reported only).**
   - Evidence: 13 / 38 taken bench poses are under 1 / 2 mm, and 6 of the 7 taken overhead poses are under 2 mm.
   - Action: None (the user does not gate on it).
11. **P4: The complexity metric changed in the row's commits.**
   - Evidence: 3ceacea and ec77d25 changed tools/simplicity.py together with this row's complexity. Both are stated changes that follow the user's rulings, and v2.1 does not move this row.
   - Action: Proposal B7 (judge_change should follow complexity moves) stands.
12. **S2: Link 1a is sparsely sampled.**
   - Evidence: Link 1a has 16 samples at 0.42x the kit density, and no per-part in-band record exists. The re-weight could move the gap by -0.28 to +2.35.
   - Action: Proposal C3: the harness should export per-part counts.

## Checks of the tool (`docs/alignment/minarc-stop-knuckle-4r.json`, tool VERSION 2026-10-18.1)

`python3 tools/alignment_audit.py audit minarc-stop-knuckle-4r --ref sidecar-longdyad-knuckle-3r` gives WATCH.

- **`contact_depth`: watch.** See T5.
- **`sampling`: watch.** No per-part in-band record exists (S2).
- **`reporting`: watch.** The dashboard shows 18.4 while v_gap is 19.54, and the sweep record is 6.19. 18.40 is an
  independently confirmed polish, so the "flatters" half of this reason is a false positive; the 6.19 half is real.
- **`complexity`: ok.** It recomputes 32.5, which now matches the row (the mismatch of 2026-10-17 is fixed).
- **The other checks are ok:** `held_out` (+4.64 for BDp), `fast_frozen`, `near_touch`, `dominance` (retired),
  `continuity` (0 dropped), `fold_margin` (5.007), `idle` (K span >= 34 deg), `density` (none over-dense; L1a 0.42x
  under-dense), `judge_change` and `rules`.

## Proposals (measurement or reporting changes for the lead or the user; none applied, none used in the verdict)

- **C1. State every verified pin-knee row as built under the 2026-10-17 rules (MR63ZZ stk 6.0 and its CAD's knee
  stop) next to its claim.** This is a tightening, so it is a measurement change. Measured effect today:
  - minarc pick1: bench 18.4 -> 18.2 (-0.2), held out 22.69 -> 22.75 (+0.06);
  - roller-longdyad: +0.26 / +0.27 at stk 6.0 (its audit);
  - sidecar-longdyad: +0.30 / +0.30 (its audit).
  The other verified rows are not measured here. The sidecar-longdyad audit's P-1 already asks for this; C1 adds the
  knee stop.
- **C2. Re-word the leader texts from the board, not by hand.** This is reporting only.
  - README's "Best verified overall" should come from the verified board: today phi40-thinstack-relay-4r 14.06 (4
    joints), or the 3-joint conecut-knee-knuckle-3r 18.28.
  - The row's and the dashboard's verdict strings should drop "VERIFIED LEADER".
  - sweeps.json should mark refuted self-measured numbers as not a record.
- **C3. The minarc verifier harness should export per-part sample counts and per-part in-band**, so S2's re-weight
  can be measured instead of bounded.
- **B1, B2, B3, B5 and B7 of 2026-10-17 stand.** B5 is now measured as part of C1. B4 is done for the complexity
  field; mechanism.notes is still stale. B6 is withdrawn, because sensing is out of scope (user ruling 6).

## Not measured, and why

- **No re-wear of the unchanged claim.** The re-wear trigger (the bench file is older than the row's last commit)
  fired, but that commit changed only the complexity field. No model, param, bench or kit file has changed since the
  02:21 re-wear, which reproduced 18.40 / 22.69 / 19.54 / 24.18 to the digit. The local CPU was at load 10-15 on 4
  cores, and the farm budget line is spent (CLAUDE.md decision 7), so the two local slots went to the as-built re-wear
  instead. Farm spend: $0.
- **The two as-built changes are not separated.** stk and ang_min were changed together. On the bench the knee never
  passes 143.6 deg, so the bench change there is stk's alone; held out it is the sum of the two.
- **The as-built contact-aware continuity pass** was stopped at the time box (35 min, CPU load 10-15 on 4 cores), and
  with it the probe's near-touch 2 / 3 mm, contact depths, K spans and unscored in-band. For the claim that pass dropped
  0 extra poses, so the as-built gaps above are expected to stand; re-run with
  `CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_minarc.py docs/alignment/remeasure/minarc-stop-knuckle-4r_pick1built_params_in.json <bench|held> docs/alignment/remeasure/minarc-stop-knuckle-4r_pick1built_probe_<bench|held>.json`.
- **No per-pose `alignment_paired` dump.** That tool cannot load this model's verifier harness. The contact depths come
  from the wear probes, whose gaps reproduce the claim.
- **Per-part in-band (S2):** the harness does not export it.

---

## Skeptic (2026-10-17, 02:30-02:40 UTC, git 14dd5d1)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It re-derived every number from the verifier files (`docs/research/minarc_final_polish/verify/v_*`), the
audit's re-wear files (`docs/alignment/remeasure/minarc-stop-knuckle-4r_*`), the rows and `tools/simplicity.py`.
No re-wear was needed: every number in the reasons was on file and was reproduced. Farm $0.

**Final verdict (ledger, `stage skeptic`, 2026-10-17T02:39:15Z): WATCH.** One of the 15 reasons was refuted
(`continuity`). The other 14 stand, all at 'watch'. The claim is 18.40 (pick1).

**Rulings** (also in `docs/alignment/minarc-stop-knuckle-4r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| near_touch | no | **Numbers.** `_bench.json` (config BDp) gives 19.54 / 26.44 / 41.69 / 152.61, the same as the verifier. **Threshold.** TH shell2_watch 15 is applied to n2 - plain = 22.15, as documented. **Label correction.** 22.15 is the 0-2 mm shell; the strict 1-2 mm shell is 15.25. **Keyed to BDp, not the claim.** pick1's own numbers are 22.89 (0-2 mm) and 17.93 (1-2 mm), both in the watch band. **Wearer.** 38 taken bench poses sit under 2 mm. It is not a gate (user, 2026-10-17). |
| continuity | **yes** | **The connected numbers are on file; the tool misses them only because of its record format.** `v_pick1_fit60_bench_conn.json`: 1105 / 1105 grid nodes, 0 islands, 990 / 990 edges, bench ws 281 / 281. `_conn_taken.json`: 1056 / 1056 nodes, ws 270 / 270. `_pick1_probe_{bench,held}.json` contact_aware_verifier: 0 / 0 dropped, gap 18.40 / 22.69. BDp is likewise 0 / 0 at 19.54 / 24.18. **Result.** Connected minus static is 0.00 everywhere, under TH conn_watch 1.0. **knn flood.** Not on file, but the tool's rule only uses it to raise a watch, so 'ok' does not need it. |
| sampling | no | **Missing measurement.** `parts_ib14` is null in the remeasure files and absent from every verify file. The row has fractions only, for the older configs BD / BA (hub3 0.664, L2 0.779). There are no sample counts, and nothing for pick1 or BDp. Not measured in this time box. |
| complexity | no | **Recomputed.** `simplicity.py` on the row mechanism gives **52.0** (+25 for the 4th active DOF, +10 for 2 sensed passives). The row field says 33.0. **Shown.** The dashboard shows 52.0; HANDOFF lines 79-80 say 33. |
| reporting | no | **First half, a false positive.** After the 02:28 refresh, morphs.json has v_config 'pick1', v_gap 18.4, v_reach 0.75, v_contact 0.0281, v_inband14 0.8941: pick1's confirmed numbers. **Second half stands.** gap / sweep_gap 6.19 (score 97.75), reach 0.8438 from the sweep, and the verdict string 'VERIFIED LEADER ... BDp 19.54'. |
| G6 | no | **Numbers.** Confirmed from the files. **Correction (apples to apples).** pick1 is judge-priced: CB_FOLD_MARGIN 5.5, J2 slot +0.5. The 3-joint reference numbers are unpriced (smlo 5.0). Priced the same way, sidecar-longdyad reads 19.36 bench and 23.29 held out (`final_polish.priced`). Like-for-like, pick1 leads it by **0.96 bench and 0.60 held out**, so "held out it does not lead" is wrong against longdyad. At 1 mm pick1 still trails priced longdyad (23.36 vs 20.45 bench, 26.73 vs 26.39 held). Held out at 1 mm it beats roller (26.73 vs 26.83). **Wearer points stand.** A 4th joint at the cap, overhead 7 vs 8 of 28, contact 11 vs 4 poses. |
| NEW-overhead-traded | no | **Overhead taken.** overhead140_ws: 7 / 28 vs 8 (bench), 12 / 71 vs 16 (fit-60 held), 16 / 71 vs 17 (env held). **Lost to contact.** 5 vs 2 bench, 16 vs 7 held. **K overhead.** K is open on 0 overhead ws / clip poses. **Size.** 1 pose on the bench, 4 of 71 held out. |
| NEW-depth-blind-contact | no | **contact_raw.** 11 / -13.17 vs 4 / -6.41 bench; 35 / -14.61 vs 13 / -7.27 fit-60 held; 28 / -14.58 vs 9 / -7.27 env held. All are ws poses, no clip frame. 5 of the 11 bench contacts are at elevation >= 150. **Fold losses.** 70 vs 86 bench, 209 vs 257 held: pick1 closes more poses and loses more of them to contact. |
| G5 | no | **Stale field.** The row says 33.0; HANDOFF 79-80 say 33; simplicity.py gives 52.0. **Knee pins.** Counted active, simplicity.py gives **90.0 at 6 DOF**, over the cap. CLAUDE.md line 18 names K only. A5 keeps cuff-side passives out of the count. The question is open. |
| R2 | no | **Stale text.** The row verdict / v_verdict and the dashboard verdict open "VERIFIED LEADER ... BDp 19.54", next to v_config pick1, and the sweep shows 6.19. **Caveat.** 18.40 itself is confirmed. |
| NEW-mixed-protocol | no | **README.** Line 33 says 21.31 (env fit); line 36 says 22.67 (fit-60): confirmed. **Correction.** The finding's "tie" (22.69 vs 22.67) also mixes stop pricing. Priced, longdyad held out is 23.29, so pick1 leads by 0.60. README's implied 1.36 overstates that by 0.76. |
| T4 | no | **Knee.** ang_min 26.1449, held knee max 152.746, margin 1.109, 4 poses past H1 (BDp 1). **Correction.** "BDp 4.66" is BDp's **bench** margin; held vs held it is 1.11 vs **2.67**. **Size.** 4 / 952 held ws poses = about 0.42 points. |
| G4 | no | **Margins.** min own 5.623 / 5.586; lt10 107 of 380 (held 273 of 887); plain dyad on forced poses -22.763. **Swing.** J1 gain 3.30 / 2.29, 31 deg per frame. **Context.** BDp swings more (3.41 / 2.55 / 35 deg) with lt10 98 of 370, so this is not a polish regression. |
| M5 | no | **Hold check.** Drift 3.72 upright and 5.69 / 6.12 / 4.12 / 7.70 tilted (3 of 4 over 5); twist up to 3.83; 9.28 at 0.08 N.m. **Red team.** Demand 0.048 N.m; Reach a high shelf moves K 15.8 deg vs BDp 0.85. **Mitigating.** At 2 g upright, K lifts at most 0.47 deg. The tilted cases are a robustness sweep, not the judge's R17 posture. |
| T1 | no | **Numbers.** 18.40 / 23.36 / 41.29 / 156.01; 13 / 38 / 171 poses; the 7 overhead ws floors are 4 / 2 / 1 in the 0-1 / 1-2 / 2-3 mm bins. **Correction.** Priced against longdyad, pick1 is 0.96 ahead plain and 6.66 behind at 2 mm (not 0.51 / 7.26). Information only. |

**Correction that runs through G6, T1 and NEW-mixed-protocol** (stop pricing, not a design change):
- pick1 and BDp are read at the judge's built-stop pricing: rule 5.5, J2 slot +0.5 (`rows polished_pricing`;
  probe `fold_margin_env` 5.5).
- The 3-joint numbers they are set against (18.91, 18.67, 19.13; 22.67, 23.73, 22.03) are unpriced (smlo 5.0). The
  sidecar-longdyad skeptic's NEW-unpriced-stops finding says so.
- Like-for-like, against sidecar-longdyad's own priced reading (19.36 / 23.29 / 1 mm 20.45 / 26.39 / 2 mm 34.63),
  pick1's lead is **+0.96 bench and +0.60 held out**. That is about 3.5 and 2 workspace poses, larger than the
  audit says.
- No priced number is on file for roller-longdyad or sidecar-parallelogram.
- This favours minarc, but it does not change any level. The 4th joint, the deeper contact and the overhead count
  are wearer facts either way.
- Proposal for the next audit (a measurement change, not used here): compare a priced claim only with priced
  references, or price both.

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **K runs to within 0.1 deg of stop B, and stop B carries no build tolerance.**
   - Stop B sits at the 5-deg rule cut, dK 56.652 (`rows polished_pricing`).
   - The taken K reaches 56.244 deg on the bench and **56.551 deg held out**, 0.10 deg from the stop
     (`_pick1_probe_{bench,held}.json` K_open_deg_taken.max).
   - The J2 slot is priced +0.5 for machining; stop B is not.
   - A stop B that engages 0.5 deg early would cut every pose that needs K above 56.15 deg. The count is not
     measured, because the probe stores only the maximum.
   - This is the same pattern as roller-longdyad's dK 46.17 of 46.25: a coordinate parked at its cutoff.
   - Proposal (measurement change): re-wear pick1 with stop B at 56.15 and report the delta.
2. **The audit report contradicts itself about the slot file.**
   - "Not measured" says pick1's bench output is written to `remeasure/minarc-stop-knuckle-4r_bench.json`.
   - That file's `config` field is BDp (19.54), as the "Checks of the tool" section states correctly.
   - So the tool's `near_touch`, `held_out` and `fast_frozen` checks describe BDp, not the claim. pick1's own
     numbers put those checks at the same levels (near_touch watch 22.89; held drop 4.29; fast drop 12.21 < 14).

**Notes** (not gaming):
- No new gaming pattern was found.
- The refuted `continuity` reason is a format gap in the tool, which reads only a `connected_full` / `connected_knn`
  dict. Both floods of the verifier are on file and drop 0 poses. A tool fix (read `connected.dropped_unconnected` and
  the `_conn*.json` files) is a change to the tool and is left to its owner.

## Skeptic (2026-10-17, 04:30-04:45 UTC, simplicity v2 metric-change audit)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It re-derived each reason from the probe files, the verifier files, the rows, `tools/simplicity.py` and the
pick1 CAD parts list. It re-ran the auditor's determinacy tool on both configs. Local CPU only, at most 2 processes.
Farm spend $0.

**Final verdict (ledger, `stage skeptic`, 2026-10-17T04:44:39Z): WATCH.** None of the 16 reasons was refuted, and
all stand at 'watch'. The claim is 18.40 (pick1).

**Re-measured here:**
- `tools/alignment_knee_sensing_minarc.py` re-run on pick1 and BDp. Every summary matches the committed files to the
  digit: pick1 0.3691 / cond 2.54 on 1056 taken grid poses, 0.3902 overhead, 0.2839 on the library; BDp 0.0958 / 9.83.
- The finite-difference step was varied from 1e-3 to 1e-5. sigma_min did not change to 4 digits.
- simplicity v1 / v2 was recomputed for every row that has a v_gap, along with the (v_gap, complexity) fronts.
- New: `tools/alignment_knee_ghdrift_minarc_skeptic.py`, output
  `docs/alignment/remeasure/minarc-stop-knuckle-4r_skeptic_ghdrift_arm.json` (see missed item 1).

**Rulings** (also in `docs/alignment/minarc-stop-knuckle-4r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| contact_depth | no | **Re-derived** from the probes' `contact_poses`: bench 11 poses, 34.43 mm summed, deepest -13.17; held out 35 poses, 126.1 mm, deepest -14.61. sidecar-longdyad `_perpose_claim`: 4 poses / 6.23 mm / deepest -4.61 on the bench; 10 / 35.66 / -8.37 held out. **Threshold.** TH depth_ratio 2.0 and floor 5 mm, applied to summed depth: x5.53 (+28.2 mm) and x3.54 (+90.4 mm). **Label slip.** In the condensed reason, "6.23 mm" is the reference's summed depth; its deepest is 4.61 mm. |
| sampling | no | No per-part sample counts in any probe or verify file. Not measured. |
| complexity | no | v2 gives 32.5 against the row's 33.0. The mismatch is over the check's 0.01 tolerance. **Direction.** The stale field overstates complexity by 0.5, so it does not flatter the design. The dashboard already shows 32.5. The notes are stale. |
| reporting | no | morphs.json (04:28): the 18.4 half is the named false positive. The second half is true: sweep_gap 6.19 sits 13.35 under the verified number, and the verdict text is "VERIFIED LEADER ... BDp". |
| G6 | no | Numbers confirmed. Complexity v2: 32.5 / 29.5 / 24.25 (v1: 52 / 49 / 43.75). The earlier pricing correction still applies: pick1 leads priced longdyad by +0.96 bench and +0.60 held out. It is still a 4th joint for a few workspace poses, none of them overhead. |
| NEW-overhead-traded | no | overhead140_ws taken: 7 vs 8 of 28 (bench), 12 vs 16 of 71 (fit-60 held out), 16 vs 17 (env fit). why_not: contact 5. K is open on 0 of 7 ws and 0 of 10 clip poses at elevation >= 140. |
| NEW-depth-blind-contact | no | contact_raw: 11 vs 4 bench (-13.17 vs -6.41); 35 vs 13 fit-60 held out; 28 vs 9 env-fit held out. 5 of 11 bench and 16 of 35 held-out contacts are at elevation >= 150. |
| G5 | no | The subtraction leaves B 4, J 4, R 0, made 10, bought 10, which is exactly mechanism_A. In the CAD (parts 15-22) the knee has no encoder, no MR63ZZ and no shared plate; the template is within 1 part. The stale 33.0 and notes are confirmed. |
| R2 | no | The row's verdict / v_verdict and the dashboard verdict open "VERIFIED LEADER" (BDp). The dashboard row mixes pick1 and BDp. |
| NEW-mixed-protocol | no | README line 33 gives 21.31 (env fit, `polished_held_out.env_fit`). Line 36 gives 22.67 (fit-60). |
| T4 | no | verifier.knee held out: ang_min 26.1449, max 152.746, margin 1.109, outside_H1 4 (BDp: 2.665, 1). |
| G4 | no | th_margin_own_state: min 5.623, lt10 107, plain dyad on forced -22.763 (BDp: lt10 98, -10.867). |
| M5 | no | k_hold_check line 16: 5.69 / 6.12 / 4.12 / 7.70. Line 48: twist 3.83. CAD part 6 still names a 0.08 N.m preload (already known). |
| T1 | no | near1 / 2 / 3 poses: 13 / 38 / 171. All 7 overhead ws poses are under 3 mm (4 under 1 mm). |
| NEW-hub-only-sensing | no | **Reproduced** to the digit, stable over the FD step. **Structure.** In the null space K's row is (0, 0, 0, 1), so hub4 determinacy reduces to forward kinematics of J1-J3 at fixed K. K's encoder is required on forced poses. **R10 caveat is larger than reported:** see missed item 1. |
| P4 | no | c_judge_change compares only gap / v_gap, confirmed in the code. Every knee row moves by -19.5. The tie-break is unchanged. The v2 front is roller-longdyad, rim-lobe, geneva-tail and skin-normal (plus minarc at 18.40). There is no flip that involves minarc. |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **The R10 caveat understates the arm error that hub-only sensing makes under GH drift.**
   - What the audit reported: the knee's member-3 twist, 1.69 deg/mm (pick1) and 1.91 (BDp).
   - What a fixed-GH estimator gets wrong: it inverts the 4 hub rows and reads a GH rotation that did not happen.
     That error is the twist times the gain from J3 to the arm.
   - pick1: median 0.68, max **2.03 deg/mm** (overhead 1.84); **8.1 deg at R10's 4 mm**.
   - BDp: median 0.70, max **7.66 deg/mm** (overhead 6.19), 30.6 deg at 4 mm. Its ill-conditioned poses
     (sigma_min 0.096) amplify the drift up to 4x.
   - Assumptions: sn is parallel to u3 within 1.2e-4 deg; J1, K and J2 are held by their stop or spring.
   - This matches the sidecar-longdyad skeptic's finding: 0.73-2.41 deg/mm, up to 9.6 deg at 4 mm.
   - It does not change the v2 count. It tells the user what dropping the knee encoders costs once GH translates.
   - Tool: `tools/alignment_knee_ghdrift_minarc_skeptic.py`. Output:
     `remeasure/minarc-stop-knuckle-4r_skeptic_ghdrift_arm.json`.
2. **A label slip in the condensed contact_depth reason.**
   - It sets pick1's deepest contact (13.17 mm) against sidecar-longdyad's "6.23 mm". 6.23 is the reference's
     *summed* depth.
   - The reference's deepest contact is 4.61 mm bench and 8.37 mm held out (`_perpose_claim`). The audit's table says
     -8.31.
   - The check itself compares summed depths correctly.
3. **Carried over, still open:** K reaches 56.55 deg held out, against stop B at 56.65 deg, and stop B carries no build
   tolerance (02:40 skeptic, missed item 1). Not re-measured here.

**Questions for the user** (added to the audit's):
- Under GH drift, hub-only sensing reads up to about 2 deg of false arm rotation per mm on pick1, and up to 7.7 on BDp.
  Is that acceptable for MVP2 control? Or should "no encoders needed" be conditional on a bound on that error, for
  example under 1 deg/mm at the taken poses? That bound would be a tightening, and it would be measured per row.
