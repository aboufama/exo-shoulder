# Handoff: the state of the project (2026-10-17, last edit ~13:00 UTC by git commit time)

Written for a reader with no context: a new session, a new model, or a person. Every number below comes from a file in
this repo (rows, verifier outputs, scorecards, ROUNDS.md, FINDINGS.md, EVOLUTION.md, the alignment ledger); the file
is named next to it. The one exception is the live RunPod balance, read from `tools/runpod_guard.py audit` (named where
it appears).

**Branch.** All of this lives on branch `claude/exciting-albattani-94w8cp` of github.com/aboufama/exo-shoulder. It was
fast-forwarded from `claude/trusting-pasteur-6czobp`, which is no longer pushed to: its last commit is 40dea1a
(2026-10-16 23:13 UTC), and at 12:49 UTC the new branch is 243 commits ahead of it. `main` stopped on 2026-10-14 and is
1243 commits behind. If you find no `docs/OPERATIONS.md`, you are on an old branch:
`git fetch origin && git checkout claude/exciting-albattani-94w8cp`. If your environment assigned you another branch,
merge this one into it first (`git fetch origin claude/exciting-albattani-94w8cp && git merge FETCH_HEAD`), then commit
and push to YOUR assigned branch (the environment's branch wins: it is the one your session may push) and pass it as
`branch` to every workflow script. Then write its name here. CLAUDE.md "Where things stand" and OPERATIONS section 1
still name `claude/trusting-pasteur-6czobp`: read them as this paragraph.

**Accounts.** The user cycles accounts when credits run out. Since 2026-10-17 the session runs under the second
account, which cannot write the first account's two dashboard artifacts. This account's live dashboard is
https://claude.ai/artifact/DjCGir1xvu6es36Lx1nwRA (OPERATIONS section 4). Anything else an account switch loses (the
RunPod key file, session crons, scratchpad copies of the workflow scripts) is listed in section 8.

**Clock.** Use git commit times (`git log --format='%h %ci %s'`) as the clock. Times agents wrote inside files
(`docs/concepts/events.jsonl` `time`, "verified at hh:mm" in prose, a row's `leader_ruling` text) can run ahead of the
wall clock (up to ~20 min on 2026-10-16: events stamped 20:22 and 20:31 sit in commits made at 20:09 and 20:13); never
compute "silent for N min" from them. The times in this file are commit times unless marked otherwise.

## Start here

**What this is.** A shoulder exoskeleton for the user's right shoulder (they are 185 cm tall, 6'4" wingspan). The whole
mechanism must ride within about 1 cm of the skin over the full range of motion, overhead most of all, and never touch
it. It has at most 4 degrees of freedom, and the user wants exactly 3 if possible. MVP1 is unpowered: rolling bearings
track the arm and the user adds rotation sensing. The work is a loop: invent a mechanism, score it on a body-model
bench, have an outside verifier re-measure it, build CAD of the winner and judge it against 19 requirements.

**Read in this order** (the one order; CLAUDE.md "Where things stand", OPERATIONS.md and README.md use it too: it is
CLAUDE.md's line-3 list with this file and OPERATIONS.md inserted after METHOD.md).
1. `CLAUDE.md`: the user's goal, decisions and hard rules. They are binding, and the user's words outrank everything.
   The 2026-10-17 decisions (1)-(7) and the farm budget line are new since the last handoff.
2. `docs/METHOD.md`: how we work (Felix Rieseberg's essay, applied; link below).
3. This file: where things stand.
4. `docs/OPERATIONS.md`: how to run the machinery (workflows, farm, watchdog, dashboards, git).
5. `README.md`, then `REQUIREMENTS.md`: the 19 numbered requirements (R1-R17 plus R1-aim and R5-aim) and their judges.
6. `docs/PLAN.md`: the phases and the field's instruments.
7. `docs/FINDINGS.md`: everything measured so far, newest at the bottom.
8. `docs/concepts/ROUNDS.md`: the discovery rounds, each with its plan, results, lessons and next focus.
9. `docs/ALIGNMENT.md`: the misalignment auditor's catalogue - ways a score rises while the exo does not get better.
   Then `docs/CAD_STANDARD.md` before touching any part, `docs/PIPELINE.md` before running anything.

**How we work, and why.** The method comes from Felix Rieseberg's essay *How to be more ambitious: A tutorial for humans
with models*: https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/ (read it).
- Speed is assumed: never idle.
- Altitude: work at the outcome (a wearer who does not feel the mechanism), not the task, and leave loops running.
- Depth: use the field's instruments, chase a specific hard number, and let an outside judge decide.
- Range: do other fields' work for real, with a red team.

`docs/METHOD.md` applies the essay here, and `CLAUDE.md` "Ambition rules" makes it binding. It matters on this project
because the problem looks impossible on the first try: rigid metal within 1 cm of moving skin, overhead included. Every
real gain came from a hard numeric target, verifiers that refuted self-measured claims (several were refuted), and a
search loop that kept going.

## 1. How a design is scored

- **The bench** (`tools/concept_bench.py`): `Bench(n_clip, n_ws)` poses the body model on fit-clip frames and on
  everyday-workspace poses. The skin is exact signed distance via libigl (`CB_EXACT=1`) or a fast grid cache.
  - **reach**: share of workspace poses the mechanism takes without entering the body.
  - **follow**: share of clip frames taken.
  - **in-band14 / in-band10**: share of metal samples 2-14 / 2-10 mm from the skin.
  - **contact**: share of poses with metal inside the body.
- **gap** = 100 (max(0, .90 - in-band14) + max(0, .95 - follow) + max(0, .90 - reach)) + 100 contact. Lower is better,
  and 0 meets every bench target.
- **score** = 100 (1 - gap / 275).
- **The claim protocol** (ROUNDS.md header): fit the shape on Bench(60,160) fast, freeze it, then wear it on
  Bench(110,360) exact. The rules: fold margin 5 deg on the J1-J3 angle `th` (`tools/concept_kit.py`), O20 hubs only,
  and the continuity flood fill for any passive or redundant coordinate.
  - A number counts only after an independent verifier re-measures it.
  - **Held out**: the verifier's 1154 poses outside both benches (`tools/env_bench.py` header). They are never used to fit.
  - **Near-touch**: metal < 1 mm counts as contact. The 1 mm reading stays the search objective (a robustness
    technique). Corrected 2026-10-17 (CLAUDE.md decision (3) and "Alignment auditor"): near-touch at 1 mm and 2 mm is
    report-only, the 2 mm A1 dominance gate is retired, and a design replaces the lead on the plain verified gap, whose
    contact is metal past 0 mm as the verifiers compute it.
  - Added 2026-10-17 (CLAUDE.md, lead's rule): a verifier also writes a per-pose dump
    (`python3 tools/alignment_paired.py dump`, bench and held out, reproducing the claim to +-0.05), so contact depth
    (T5) is on file.
- **Complexity** (`tools/simplicity.py`, `docs/SIMPLICITY.md`): 0 is three pins and three links. It is shown next to the
  score and never folded into it. MEASUREMENT changes on 2026-10-17, no design changed (SIMPLICITY.md change log):
  v2, the unsensed two-pin cuff knee scores 0 (user decision (5)); v2.1, its closure loop is free too; v2.2, the sensed
  weight is 0 (decision (6): sensing is out of scope). Rows moved by the ruler alone: H1 19.5 -> 0, roller-longdyad
  43.75 -> 20.25, sidecar-longdyad 49 -> 25.5.
- **The alignment auditor** (`tools/alignment_audit.py`, ledger `docs/alignment/ledger.jsonl`). MEASUREMENT changes on
  2026-10-17: VERSION 2026-10-17.1 (86cc9f4) added the T5 contact-depth watch check, idle reads declared joints and
  fold_margin reads every spelling; VERSION 2026-10-17.2 (ded811f) made near-touch report-only and capped dominance at
  watch. A design the ledger marks 'gamed' cannot be called verified, a winner or a leader.
- **The golden target** (user, 2026-10-16): verified score >= 95 (gap <= 13.75) at complexity ~0. Nothing has reached it.
- **Built CAD** is judged separately on the 19 requirements by `tools/judge_all.sh <design id>`, or on the farm by
  `python3 tools/cloud_run.py judge <id>`. The results go to `pipeline/full-exo/designs/<id>/judge/scorecard.md`.

## 2. Verified leaderboard (Bench(110,360) exact, frozen shape, margin 5, O20)

Ledger = `python3 tools/alignment_ledger.py get <id>` (latest verdict, read 12:45-12:49 UTC). Complexity is
tools/simplicity.py v2.2 as recorded on the row. Paths are under `docs/concepts/` unless they start with `docs/` or
`tools/`.

| design | verified gap (score) | held out | active DOF | complexity | ledger | status | key files |
|---|---|---|---|---|---|---|---|
| **slipper-nose-knuckle-3r** (round 10) | **18.49 (93.28)** | 23.45 | 3 (K slaved by the hub-2 lobe and a drive crank whose hardened O2.37 440C nose slides on a DLC flank; never read) | 22.25 on the record (18.25 like-for-like, ROUNDS round 10) | watch (M5, G4, T5, ws-inband, reporting) | **VERIFIED LEAD** (a6c23c0, 06:23); final polish and gen-7 CAD running (section 8) | rows/slipper-nose-knuckle-3r.json, slipper-nose-knuckle-3r.md, verify/slipper-nose-knuckle-3r.py + `_v_bench_frozen.json` / `_v_held_frozen.json`, docs/alignment/slipper-nose-knuckle-3r.md |
| trimlug-k165-knuckle-3r (round 11) | 18.51 (93.27) | 23.47 | 3 | 22.25 | no entry yet (audit running at 12:49) | verified (03a333f, 12:26): the lead with its horn lug trimmed; +0.02, not a lead change; contact depth T5 14.74 -> 13.18 mm bench, 46.35 -> 40.59 mm held | rows/, trimlug-k165-knuckle-3r.md, verify/trimlug-k165-knuckle-3r.py |
| inband-rssr-knuckle-3r **pick3** (lead's track, docs/research/inband_drive.md) | polished 18.33 priced; **18.32 on the leader's protocol** (unpriced, margin 5) | 22.86 priced (fit-60); **23.54** on the leader's protocol | 3 (K slaved by an RSSR rod drive with the crank in link 1b's own layer) | 28.5 | watch (final, 48be5d5) | polish CONFIRMED (931a8d1); lead ruling **TIE** with slipper-nose (a510cfe, row field `leader_ruling`, dashboard "Verified (tie)"): ahead on the bench, behind held out, paired held CI [-0.83, +1.31]; the screened pick reads 18.87 (93.14) / 23.21 | rows/inband-rssr-knuckle-3r.json (`polished_*`, `leader_ruling`), docs/research/inband-rssr-knuckle-3r_final_polish.md, docs/alignment/inband-rssr-knuckle-3r.md, docs/alignment/remeasure/inband_pick3/ |
| roller-longdyad-knuckle-3r (round 9) | 18.67 (93.21) | 23.73 | 3 (K slaved by a roller flank) | 20.25 | watch | verified; built as gen 6 (section 4); its farm polish replaced nothing (held-out gain +0.73 < 1) | rows/, verify/roller-longdyad-knuckle-3r.py, docs/research/roller-longdyad-knuckle-3r_final_polish.md |
| dipped-law-groove-knuckle-3r (round 10) | 18.64 (93.22) | 24.07 | 3 | 24.25 | **gamed** (fold margin 0.184 deg, m_sub waiver, in-sample gain) | cannot be called verified or a leader until the user rules on B1 (section 7) | rows/, ROUNDS round 10 results |
| sidecar-longdyad-knuckle-3r (round 8) | 18.91 (93.12) | 22.67 | 3 (K slaved by a strap-level RSSR) | 25.5 | watch | verified; shallowest contacts on file (6.23 mm summed); its polish replaced nothing | rows/, verify/sidecar-longdyad-knuckle-3r.py |
| sidecar-parallelogram-knuckle-3r (round 8) | 19.13 (93.04) | 22.03 | 3 | 25.5 | watch (knn flood 22.21) | verified | rows/, verify/sidecar-parallelogram-knuckle-3r.py |
| sidecar-roller-flank-knuckle-3r (round 8) | 20.08 (92.70) | 22.35 | 3 | 21.75 | watch | verified (a97c86f, 2026-10-16 20:28) | rows/ (`v_held_gap`) |
| kneeless-roller / kneeless-sidecar (round 9) | 21.07 (92.34) / 21.11 (92.32) | 24.59 / 25.34 | 3 | 23.75 / 28.0 | watch / watch | verified; knee replaced by a rigid bracket; GH-offset liner share 38.7 % vs 66.6 % with the knee (ROUNDS round 9) | rows/ |
| groove-desmo-knuckle-3r (round 10) | 22.64 (91.77); claim 19.29 refuted | 28.77-28.90 | 3 (spring-free K) | 18.25 | watch | verified at the corrected stop B | rows/, verify/groove-desmo-knuckle-3r.py |
| frontload-lobe-stopb-knuckle-3r (round 7) | 22.82 (91.70) | 26.75 (ROUNDS round 7) | 3 | 25.5 | watch | verified | rows/, verify/frontload-*_corr_*.json |
| geneva-tail-knuckle-pinknee-3r rod (round 6) | 23.57 (91.43) | 28.12 | 3 | 12.0 | watch | verified; built as gen 5 | rows/, verify/geneva-*_corr_*.json |
| minarc-stop-knuckle-4r pick1 | 18.40 (93.31) | 21.31 env fit / 22.69 fit-60 | **4** (K sensed: a joint, user decision (1)) | 32.5 | watch (contact depth 34.43 mm bench) | verified polish; **not a 3-joint leader**; built as gen 4b | rows/minarc-stop-knuckle-4r.json (`polished_*`), docs/research/minarc_final_polish.md |
| skinnormal-shortk-knuckle-4r (round 10) | 18.58 (93.24) | 22.43 | 4 | 32.5 | no entry | verified, dead by the kill rule (>= pick1) | rows/, verify/skinnormal-shortk-knuckle-4r/ |
| skin-normal-3r-pin-knee **H1** | 27.20 (90.11) | 31.39 (minarc harness) | 3 | **0** (v2: the free cuff knee) | watch | verified gen-3 winner; built (user_pinknee_h1b) | rows/skin-normal-3r-pin-knee.json, skin-normal-3r-pin-knee.md |
| zc-frontier-3r (plain spherical 3R) | 33.51 (87.81) on the verifier protocol; 31.04 (88.71) fit on Bench(110,360) | - | 3 | 0 | watch | verified ceiling of the plain 3R | rows/, docs/research/golden/README.md, docs/cad_context/zc-frontier-3r/KINEMATICS_BRIEF.md |

Also verified, not contenders: cam-unfold-4th 26.70 (cx 14.25) and arm-parked-knee-4r 26.71 (4 active). For reference,
the old champion spherical 3R scores 75.94 on the same bench, and the first concept-bench baseline was 68.93
(`rows/baseline-3r.json`). Held-out numbers come from slightly different harnesses, so compare them within a row's
references, not across rows.

**Reading it.**
- **The verified lead is slipper-nose-knuckle-3r at 18.49 (score 93.28), ledger WATCH.** It took the lead from
  roller-longdyad (18.67) by 0.18, all of it in-band, below the 1-point rule (ROUNDS round 10 results). The lead rule:
  best plain verified gap, not gamed; ties by fewer passive translations, then complexity; a lead's tie ruling is
  recorded on the row (`leader_ruling`, OPERATIONS section 4).
- **Four 3-joint designs sit within 0.35 of each other** (slipper-nose 18.49, trimlug 18.51, inband pick3 18.32 on the
  leader's protocol, roller-longdyad 18.67). They take the same workspace: reach 0.725 (261/360), overhead 8/28 on
  slipper-nose, roller-longdyad and trimlug. The lead's gap is reach 17.50 + in-band 0.45 + contact 0.54 (ROUNDS
  round 10 results): **the gap is reach**.
- The 4-joint rows (minarc pick1 18.40, skinnormal-shortk 18.58) are 4 DOF under the user's ruling and are not leaders.
- The simplest verified design is H1 at complexity 0 and 27.20; the plain 3R's ceiling is 31.04 at 0.

## 3. Round 11, in flight at handoff

The round-11 plan is in ROUNDS.md ("Round 11 plan", a012c17, 07:27, lead 18.49), the judge's four picks and red team in
`docs/concepts/round11_ideation.md` (05da2af, 10:01), the timeline in `docs/concepts/events.jsonl`. Its lenses:
coupler-longstroke (the stretched wall, a ~75 deg slaved K on a 28-32 / 48-50 K dyad), a lobe-free four-bar (complexity)
and the overhead cone (the other wall). At 12:49 UTC ROUNDS.md has no "Round 11 results": the loop is in its audit
phase (section 8).

| design | pick | frozen exact (score) | held out | cx | ledger | state |
|---|---|---|---|---|---|---|
| dogring-draglink-knuckle-3r | 1 (lens 1: dog sector on hub 2 driven by link 2's root flank, drag link to a link-1a horn) | claim 22.64 (91.77; fast 17.19); **verified 97.83** | 25.36 -> 101.1 | - | watch (skeptic final, 137d572) | **REFUTED** (645823e): the dog arm overlaps link 1b's root ramp by 0.18 mm on all 183 K-open bench poses, a pair the model never checked per pose |
| fourbar-longdyad-knuckle-3r | 2 (lens 2, listed for B1) | family 51.75; coupled reading (B1) 36.46 | 55.30 / 39.80 | 14.0 | no entry | **DEAD** (f769d8e; death audited, stands: e64589c): B1 fails every pose under abs K 20; the four-bar metal costs ~21 points (events.jsonl 10:42) |
| trimlug-k165-knuckle-3r | 3 (lens 3, lever c) | **18.51 (93.27) VERIFIED** | 23.47 | 22.25 | audit RUNNING | verified (03a333f); pose 264 not cleared: clearing it needs the flank to stop at dK ~35 vs the drive's 49.8 (row `limiter`) |
| coupler-longdyad-knuckle-3r | 4 (lens 1 control, hard kill) | 23.87 (91.32) | 29.73 (the CMA best) | - | death audited, stands (9a9c996) | **DEAD** by the hard kill (d3e0391): 1540 configs, none with drive in-band >= 0.755 and <= 2 K-open drive contacts |

Measured dead by the round-11 judge and not catalogued (round11_ideation.md): openhalf-fourbar (parts in band 0.47, hub 2
at 81 mm vs 62), arcspan-knee (0 of 9 frozen), conehub (0 cone poses; the b2 tilt breaks the closure).

Alongside the round (the lead's own tracks, FINDINGS):
- **longstroke-slipper-knuckle-3r** (docs/research/longstroke_drive.md): screened 21.27 (92.27) / held 26.19, cx 30.5,
  ledger watch. An RSSR rod turns K 77.2 deg at every pressure angle <= 42, but no search uses the stroke. The next
  stretched wall is the K LAW: the hub-2 lobe at PA <= 42 caps the slope at kK ~2.0, and the 5 deg margin goes at th ~114
  even at kK 3.0. With the drive metal deleted (attribution, never a claim) the long dyad measures 18.25 / 21.11.
- **inband-rssr-knuckle-3r** (docs/research/inband_drive.md): the RSSR drive's metal made nearly free (7.57 -> 0.29
  points) by two zero-complexity moves; the leak-free pick is at parity (18.87 / 23.21). Its envelope polish pick3 is the
  tie in section 2.

**What round 11 measured, so far** (from the rows above and FINDINGS):
- Reach did not move. trimlug takes the lead's 261 poses; coupler takes 266 but pays contact 0.033 and in-band 0.856
  (row `frozen_exact`); dogring's 264 rested on an unchecked part pair.
- Drives that swing beside link 1b over the deltoid do not park: the coupler's PA-legal crank arm swings 25-37 deg
  sideways over skin up to ~33 mm higher (coupler row `limiter`).
- The K drive's metal is no longer the cost (inband 0.29 points). The long K dyad loses on the representative envelope
  bench too, through its overhead press: a report-only long-dyad row regains 20 held-out fold poses and gives them back
  in contact depth (29.3 vs 10.8 mm summed) and in-band (FINDINGS, inband polish).

**Its winner, by the rule** (best VERIFIED gap of the round, not gamed): trimlug-k165-knuckle-3r 18.51 is the round's
only verified row, a contact-depth polish of the lead. The overall verified lead stays slipper-nose 18.49 (trimlug is
+0.02, below the 1-point rule). The closer decides; check the ledger first.

## 4. Built CAD and the 19 requirements

L1 is keep-out CAD and L2 is the user's standard (CLAUDE.md "CAD has two levels"). Each scorecard is in
`pipeline/full-exo/designs/<id>/judge/scorecard.md`; EVOLUTION.md has the full story of each build.

| design | level | passes | R1 2-14 / R1-aim 2-10 | R4 overhead | R16 workspace | notes |
|---|---|---|---|---|---|---|
| **`user_roller_longdyad`** (gen 6) | L2 | **8/19** | 80.9 / 47.6 % | 72.9 % | 64.2 % (step 12) | roller-longdyad 18.67, 3 DOF. Fix rebuild 10:14 UTC (ef087c4, docs/research/roller-longdyad-gen6_fix.md): R7 FAIL -> PASS (strip-glue slivers); R17 PASS, 2x twist 5.16 -> 4.10 deg (an open link-2 mesh: MEASUREMENT); R8 212.5 g (materials: MEASUREMENT). R1 -1.0 vs its L1 is not fixed (the real lobe ring rides F2 + 9.8..12.8 mm on the J2 cap). Independent check NOT REFUTED (af8f788, docs/research/roller-longdyad-gen6_fix_check.md): at step 1 R16 is 70.3 % of 1432 poses (the 64.2 % is step-12 sampling) with **10 body-contact poses** (link 1a 6.4-10.44 mm deep at elevation 150-165, link 2 5.93 mm at pose k 35, dK 43.1); attribution queued on the farm. No stills (GPU needs the user's yes) |
| `l1_roller-longdyad` (gen 6) | L1 | **8/19** | 82.0 / 48.6 % | 74.5 % | 64.2 % | best L1 R1 yet; R6 0.98 FAIL -> 0.0 PASS once link 1a was drawn as the CAD's line/arc chain (5a3c8e4); R17 PASS slaved |
| `user_roller_longdyad_arm` | L2 option | 7/19 (R7 not run) | 81.2 / 47.6 % | 73.5 % | 64.2 % | arm-through-stations option; not adopted |
| `user_geneva_rod_v2` (gen-5 fix) | L2 | 8/19 | 80.2 / 49.8 % | 74.1 % | 68.3 % (120 poses) | lobe dwell r 10.1 -> 9.6: the ring clears the skin by +0.41 mm on all 1337 clip frames; real igubal KGLM-03; R7 PASS; R11 + R17 PASS on the farm (ec77d25) |
| `l1_geneva-rod` | L1 | 8/19 | 81.1 / 51.1 % | 73.0 % | 72.6 % | corrected 2026-10-17: 7 -> 8 when the dynamics judge got the slaved-K coupling (MEASUREMENT, 333caa9): R17 PASS |
| `user_geneva_rod` | L2 | 7/19 | 80.3 / 49.8 % | 73.8 % | 72.6 % | corrected 2026-10-17: 5 -> 7 (R17 + R11 now run, PASS; 333caa9); R7 FAIL (link 1a); superseded by v2 |
| `user_minarc_pick1` | L2 | 7/19 | 80.5 / 47.2 % | 71.0 % | 74.0 % | 4 DOF (R5-aim fails); K preload 0.04 N.m makes R17 pass (drift 3.72 deg); R8 203.8 g |
| `l1_minarc-pick1` | L1 | 7/19 | 80.8 / 48.7 % | 71.8 % | 74.0 % | same preload change (R17 drift 3.68) |
| `user_minarc_bdp` | L2 | 7/19 | 80.0 / 51.0 % | 72.0 % | 73.5 % | 4 DOF |
| `user_pinknee_h1b` | L2 | 8/19 | 76.7 / 35.8 % | 71.2 % | 61.7 % | H1, 3 DOF (R5-aim passes); R8 178.0 g |

- **Every build passes** R3 (follow, 98.7-100 %), R5 (<= 4 DOF), R6 (no part interference), R8 (mass) and R11 (cuff
  pressure). R17 now passes on every build (scorecards re-read 12:50 UTC); R7 fails only on `user_geneva_rod` (v1). The
  3-DOF builds also pass R5-aim, so 8/19 is the best count (five builds).
- **Every build fails** these:
  - R1 / R1-aim: proximity, best 82.0 % (L1) and 80.9 % (adopted full CAD) against the 90 % target;
  - R4: overhead, 71.0-74.5 % against 80;
  - R16: workspace, 61.7-74.0 % against 90 at the judge's sampling step;
  - R2: 24.87 mm on every build, from the fused BOTTOM and the rig's self-intersection (EVOLUTION.md).
- **Not run or not done:**
  - R9 FEA was not run on the latest builds;
  - R10 base slip measured 15.2 mm against the 4 mm target, design-independent for a spherical chain (FINDINGS "R10 on
    the scapula handler");
  - R12-R15 (CAD standard, manufacturing quote, held-out bodies, real bodies).
- **Gen 7** (slipper-nose-knuckle-3r, the round-10 winner) is being built (section 8). No design is built from round 11.
- The zc-frontier-3r kinematics brief for an outside CAD tool is in `docs/cad_context/zc-frontier-3r/` (the user asked
  for kinematics only).
- Renders are in `renders/2026-10-16_userstyle_*`. Gen 6 and gen 7 have no stills: GPU stills need the user's yes
  (section 7). Films are made only when the user asks (CLAUDE.md, 2026-10-16 ~03:00: "focus everything on solution
  hunting").

## 5. What is dead, and why (do not screen again)

- **Rails, rings, shells, tracks, telescopes, SPMs and pointers** (rounds 1-2). One radius cannot follow moving skin:
  crown-ring 82.37, seed-arc-rails 73.0, rail-elbow 64.7, seed-spm-3rrr 193.44 (ROUNDS.md "Rounds 1-2").
- **The plain 3R at complexity 0.** Its ceiling is 31.04 frozen: hub 2 caps the fold window (FINDINGS "The
  zero-complexity class, searched near-exhaustively on GPUs").
- **1-, 2- and 3-passive closures as fold wideners.** None widens the fold. Only a moving chain centre does, and hub 2
  caps it anyway (FINDINGS "No 1- or 2-passive closure widens the fold" and "A 3-passive closure widens the fold only
  through a moving chain centre").
- **Slim hubs (O15 / O17 / O12).** The user ruled "Keep O20 only", so O15 crest basins and slim-hub numbers do not stand.
- **stop-relay-rocker-3r** (refuted 50.36). Its reach came from static islands no continuous motion reaches; this is the
  origin of the continuity rule.
- **slotted-eccentric-j2-3r** (refuted 115.21), **closure-set-arc-knee-3r** (refuted 75.28) and
  **short-a2-arc-slide-3r** (refuted 55.3). Each lost to its own locked control.
- **coupler-path-j1** (dead 28.98). Every CMA stream collapses the four-bar onto a plain J1.
- **cam-coupled-4r** (50.67 fast with the J1-housing rule).
- **The Geneva TAIL** and any follower rigid with link 2, at any radius (the k-rim-lobe stub scored 44.79). Its sweep
  cone about u2 costs 10-42 points.
- **Direct cam pairs between O20 stacks** (rim-lobe-arm 26.21). They carry only ~26 deg of K against the rod's 36,
  which is 2.8 frozen points worse.
- **Folded-side hubs and lobes** (split-knuckle 34.18, two-rise lobe). The metal costs more than the prize.
- **Front-load and stop-B laws.** K's law shape is worth <= 0.2 frozen (FINDINGS "Round 7").
- **Hubs on link 2** (cam-unfold-4th's K is in band only within ~21-30 deg of J2), **K = c(q1)**, and
  **groove / dwell flanges** (95.51).
- **twist-long-a2-knuckle-3r** (round 8). It converged at 16.74 fast against 15.57.
- **In-sample polishes.** Every one lost ~5 points held out. P5 was refuted, and the 2-fold cross-fit was refuted as a
  fix (FINDINGS "A 2-fold cross-fit polish does not travel either").
- **Added 2026-10-17 (rounds 9-11; ROUNDS.md round 10 / 11 "Closed with measured reasons", round11_ideation.md):**
  - twin-k2-sidecar-knuckle-3r (67.32 frozen): a second knuckle hub cannot sit close to the skin;
  - J1 re-seats (back 20.29 / 61.21 / 73.21 vs control 10.30 fast; eave 27.92; crown-lateral 25.29) and a2
    re-placement (a2 60: 20.84, held 24.17);
  - the long-stroke flank (its dK 55-57.5 boss sits on the deltoid, 88-94 contact poses) and stroke beyond the a1max
    window without a longer dyad (dK_lim 46.5 -> 60 bought 0 poses);
  - the dip below stop A (one budget with the stroke; dipped-law-groove is gamed) and the planar groove gate (the 3-D
    crest is +0.69 mm, worth 3.35 points);
  - a spring-held spare 4R that acts only past the 3R wall (skinnormal family: fold traded for contact ~1:1) and stop B
    within 5.5 deg of the K dyad's stretch (keep a1max <= bk1 + bk2 - 5.5);
  - fourbar-longdyad (51.75), coupler-longdyad (23.87), dogring-draglink (refuted 97.83), openhalf-fourbar,
    arcspan-knee, conehub (section 3).

## 6. Measured lessons that steer the search

1. **The fold is the limiter.**
   - The J1-J3 window is 2 min(a1, a2) - 10 wide, and wider arcs push hub 2 onto skin it cannot clear.
   - Frozen fold losses are 84-86 of 360 workspace poses on every rod-drive variant.
   - Raising reach (0.72 -> ~0.77 at in-band >= 0.88) is the half of 95 nobody has bought yet.
   - See FINDINGS "Reach is the fold" and ROUNDS.md round 7 "Next".
   - Corrected 2026-10-17 for the knuckle family (FINDINGS "The fold is two walls", docs/research/fold_ceiling.md): the
     window is [a2 - a1 + 5, a1e(dK_max) + a2 - 5], the stretched wall is the K drive's stroke (not hub 2), and the
     folded wall is hub 2's clearance. The lead loses 88: 73 stretched (th >= 106.6) and 15 folded (th 7.7-22).
2. **Search on the near-touch gap.** Plain-gap optima put metal within 1 mm of the skin and lose 8-27 points when worn
   frozen. Also report the 2 mm near-touch: a 1 mm optimum can sit at 1-2 mm. (Corrected 2026-10-17: the 2 mm reading is
   optional and report-only; CLAUDE.md decision (3).)
3. **Polish on a representative sample, claim held out.**
   - The search benches under-sample axial rotation (|axial| >= 150 deg: 6 % against 11 % held out).
   - Final polishes therefore use `tools/env_bench.py` / `tools/env_polish.py` and claim on the held-out set.
   - A polish replaces a CAD config only on a verified gain >= 1 point.
   - Added 2026-10-17: the first env polish to pass is inband-rssr pick3 (held-out gain +1.52 fit-60 / +1.18 env fit,
     confirmed); the sidecar-longdyad and roller-longdyad polishes replaced nothing. Its audit (48be5d5) adds two rules:
     pre-register the pick (pick3 was chosen best of 3 after the claims were known), and claim both the priced and the
     leader's unpriced reading (pricing helped pick3 held out by 0.68).
4. **The continuity rule.** Any passive, sprung, relayed or redundant coordinate is scored on the set connected to the
   rest region only: 2-deg slerp edges and no jump > 10 deg (`connected()` in
   `docs/concepts/models/stop-relay-rocker-3r.py`).
5. **Stops act on a joint's own angle**, as a dowel in an arc slot between the two bodies that joint connects. Read the
   fold margin in ONE metric, `th`. minarc's virtual stops scored 15.42 but are 18.45 at the true 5 deg.
6. **The K-hold posture finding** (`docs/research/pick1_k_hold_check.md`).
   - pick1's K preload 0.04 N.m passes R17 upright (drift 3.68-3.72 deg).
   - With gravity across the thorax, Reach a high shelf drifts 4.1-7.7 deg, so the margin is upright-only.
   - The fix is to plan K on the spring's own trajectory. Otherwise state "upright use" as an MVP1 limit.
   - The lag costs no proximity.
7. **Fast to frozen loses 5.6-14 points.** Only frozen exact numbers are claims.
8. **The drive's height is half the distance to 95** for the 3-active knuckle. That is what the sidecar bought. The
   other half is fold geometry (ROUNDS.md round-8 plan "Sample arithmetic").
9. **Metal rules belong in the shared kit:** K's spring-cap cylinder, the rod-over-crown clearance and the plate-height
   cap (ROUNDS.md round 7, lesson 6).
10. **Added 2026-10-17 (rounds 9-11):**
    - K's law and the drive's form are worked out: they move the gap by <= 0.3 (ROUNDS round 9); the drive's metal can
      be made nearly free (inband 0.29 points). What is left is the chain's fold.
    - Every pose a K-open design wins has cost about one contact pose (round 10 lens 1, round 11 coupler). Select on a
      frozen or K-open-aware objective, never on fast alone.
    - Check every part pair per pose: dogring's 22.64 rested on one unchecked pair (0.18 mm).

## 7. Open questions waiting on the user (unanswered at handoff)

1. **The farm budget.** $8 per 12 h was approved at ~05:20 UTC until ~17:20 UTC; it is spent when the balance reaches
   $24.40 (CLAUDE.md decision (7)). Balance $25.44 at 12:07 (CLAUDE.md), $25.19 at 12:46 (`tools/runpod_guard.py
   audit`): about $0.8 left. After the line, or after 17:20, agents run locally (<= 2 niced processes) unless the user
   renews or raises it. Ask before then if the polish or gen-7 CAD still needs the farm.
2. **GPU stills** (exo-blender-cycles, ~$0.05 a set, OPERATIONS section 2) for gen 6 (`user_roller_longdyad`) and gen 7
   (slipper-nose): now, or wait for the next winner? GPU renders need a separate yes (CLAUDE.md decision (7)).
3. **B1** (ROUNDS.md round 11 "Needs the user's say"): does m_sub at K's rest, or the coupled reading, decide the fold
   rule? It decides G4 for the whole knuckle family, the lead included, keeps dipped-law-groove gamed, and decides
   whether a positively slaved K must pass m_sub (fourbar-longdyad's coupled reading is 36.46).
4. Still listed and never answered (ROUNDS round 9): a fold margin below 5 deg; a per-pose worst-point cap (ALIGNMENT
   A3); for the 4-DOF pick1 only, "upright use" as an MVP1 limit of K's hold (section 6, item 6).

Answered since the last handoff (CLAUDE.md, 2026-10-17): a sensed joint is a joint (1); the powered product is
context only (2); near-touch is not a gate (3); the cuff knee carries no encoders and sits outside the DOF count (5);
sensing is out of scope (6); farm spending (7).

Ask in chat for big updates only (CLAUDE.md rule 6).

## 8. What is running at handoff, and how to relaunch it

Everything below runs inside the lead session and dies with it. The procedures are in `docs/OPERATIONS.md`, and the
workflow scripts and templates are in `tools/workflows/` (README there). Every script REQUIRES `branch` and `trailer`
in its args (your session's branch and the two commit-attribution lines your system reminder gives); it stops without
them.

**The effort wrapper and `no_render` (not in the repo).** This session launched every workflow from scratchpad copies of
`tools/workflows/*.js` (and `templates/`). Each copy adds, under the comment "session 2026-10-17: the user asked for
extra-high reasoning on every subagent", the line
`const agentX = (p, o) => agent(p, Object.assign({}, o || {}, { effort: 'xhigh' }))` and calls `agentX` in place of
`agent` for its main stages. The copy of `templates/generation-winner-cad.js` also takes `no_render: true`, which skips
the paid stills stage. The repo copies have neither. A new session copies the scripts to its own scratchpad and
re-applies both before launching, or launches the repo copies and stops the gen-7 CAD before its stills stage.

**The runs at 12:49 UTC** (`python3 tools/agent_tail.py` on the same machine; `python3 tools/agent_tail.py <runId> 2`
shows what each agent was doing). On a new machine all of them are gone; their committed outputs are in git.

| run id | track | state at 12:49 UTC | what a new lead does |
|---|---|---|---|
| wf_9b682834-6df | discovery loop, rounds 10-13 (scratchpad copy of `discovery-loop.js` with the effort wrapper) | round 10 closed (f8ed6a6, 07:19); round 11: all 4 picks measured (trimlug verified, dogring refuted, fourbar and coupler dead with their deaths audited); Audit phase: audit:trimlug-k165-knuckle-3r RUNNING (dogring's skeptic final 12:46); closer not run | the round-11 steps below |
| wf_ecb7b6f8-d22 | gen-7 generation-winner CAD of slipper-nose-knuckle-3r (scratchpad copy of `templates/generation-winner-cad.js`, `no_render`) | L1 phase: l1:slipper-nose and redteam:mechanism RUNNING | if it died: the gen-7 steps below |
| wf_f38de10b-cb2 | slipper-nose final polish (`templates/final-polish.js`; the inband tie's lessons in its args) | Polish RUNNING (`tools/slipper_env_polish.py`, `docs/research/slipper_env_polish/` were WIP at 12:49) | if it died: the polish steps below |
| wf_5aa58ca8-689 | inband-rssr pick3 leader-change audit | DONE: final WATCH (48be5d5); lead ruling TIE (a510cfe) | nothing |
| wf_d261725f-27c | inband-rssr envelope polish + verifier | DONE: pick3 confirmed (931a8d1) | nothing |
| session crons | the 15-min watchdog and the hourly alignment audit | live in the old session only | re-create both (OPERATIONS section 3) |

Older runs listed by agent_tail (wf_c45ea322-bbf, wf_94030a1e-9bd gen-6 fix, wf_f9e9b785-e61, wf_c984e233-060 gen-6
CAD, wf_60efaa9e-d91 roller polish, wf_7b555b78-fca, wf_0e734f62-035 gen-5 fix) are finished; their results are in
FINDINGS / EVOLUTION / the ledger. Before relaunching anything, check git for its outputs (a verifier that finished
commits a `verify/<id>.py` and the row's `v_gap`; an untracked file means one was still running when the session ended).

**Round 11 (discovery loop).** One rule for an interrupted round (OPERATIONS section 2):
1. `tail -120 docs/concepts/ROUNDS.md`, `tail -20 docs/concepts/events.jsonl`, `python3 tools/alignment_ledger.py latest`,
   and each round-11 row's `status` / `v_gap` (`docs/concepts/rows/{dogring-draglink,fourbar-longdyad,trimlug-k165,coupler-longdyad}-knuckle-3r.json`).
2. If "Round 11 results" exists, skip to step 5. If `python3 tools/alignment_ledger.py get trimlug-k165-knuckle-3r`
   prints `null`, audit it: `Workflow({scriptPath: "<repo>/tools/workflows/alignment-audit.js", args: {targets:
   ["trimlug-k165-knuckle-3r"], context: "round-11 verified row", ref: "slipper-nose-knuckle-3r", branch, trailer}})`.
3. Write "## Round 11 results" in ROUNDS.md and the FINDINGS entry as a closer would: the section 3 table, the lessons
   (section 3 "What round 11 measured"), the winner by the rule, and the next focus.
4. The winner: section 3 ("Its winner, by the rule"); a gamed verdict on trimlug would void it.
5. Start the loop at round 12: `Workflow({scriptPath: "<your scratchpad copy of>/discovery-loop.js", args:
   {first_round: 12, n_rounds: 4, track: "main", focus, branch, trailer}})`. Use the closer's "Next focus (round 12)"
   if one was written; otherwise this draft (written from the files: ROUNDS round 10 / 11, FINDINGS "The fold is two
   walls", the round-11 rows):

   > Round 12 (track main). Lead: slipper-nose-knuckle-3r VERIFIED 18.49 (score 93.28, held out 23.45, cx 22.25,
   > 3 active, ledger watch); trimlug 18.51, inband-rssr pick3 18.32 (tie ruling) and roller-longdyad 18.67 sit level.
   > The gap is reach: 17.50 of 18.49; score 95 (gap 13.75) needs +18 workspace poses at the lead's in-band and contact.
   > The lead loses 88 to the fold: 73 stretched (th >= 106.6; 64 of them internal rotation >= 90 across the body), set by the K
   > drive's stroke, then K's window (a1max), the K law (the hub-2 lobe at PA <= 42 caps kK ~2.0) and the long dyad's
   > overhead press; and 15 folded (th 7.7-22, scapular-plane overhead), set by hub 2's clearance (median need 71 mm vs
   > 62). In-family long strokes did not pay: longstroke 21.27, coupler-longdyad 23.87, the long-dyad report row
   > 23.72 / 20.44; drives beside link 1b over the deltoid do not park. Reach >= 0.80 needs BOTH walls moved
   > (docs/research/fold_ceiling.md "Next" 3): a 4th joint or a new seat pair. A spring-held 4th joint acting only past
   > the 3R wall traded fold for contact 1:1 and took 0 folded poses (its sub-chain fold 32.8 vs th_lo 29.7), so a
   > 4-joint lens must move the folded wall too and is reported as the 4-joint route, never as a 3-joint lead. Report
   > plain gap fast and frozen exact, held out, the per-pose dump, contact depth (T5), overhead x/28, the min th margin,
   > per-part and raised-arm workspace in-band, tools/simplicity.py v2.2. Pre-register every pick. Rules: O20 hubs only,
   > fold margin 5 deg on th, stops on a joint's own angle, continuity flood fill, every part pair checked per pose.
   > Dead directions: HANDOFF section 5 - do not screen them again.
6. On a 4-core box a workflow runs 2 agents at once. Never SendMessage a running workflow agent: it starts a second copy
   (`tools/workflows/README.md`).

**slipper-nose final polish** (if wf_f38de10b-cb2 died): first check git for its picks file under
`docs/research/slipper_env_polish/`. If picks were committed, claim them as committed (never re-pick); else relaunch
`templates/final-polish.js` with `{id: "slipper-nose-knuckle-3r", winner: "<one paragraph: the verified config in
docs/concepts/rows/slipper-nose-knuckle-3r.json, model docs/concepts/models/slipper-nose-knuckle-3r.py, judge harness
docs/concepts/verify/slipper-nose-knuckle-3r.py, verified 18.49 (score 93.28), held out 23.45, flood full / knn 18.49 /
20.16; build with the stock O2.5 m6 dowel nose (18.49); the inband audit's lessons: commit the picks and ONE pick rule
before any claim, and claim both the priced reading and the leader's unpriced margin-5 reading>", budget_usd: <what is
left inside the farm line>, branch, trailer}`. A polish replaces the CAD config only on a verified held-out gain >= 1.

**Gen-7 CAD of slipper-nose** (if wf_ecb7b6f8-d22 died): `templates/generation-winner-cad.js` with `{gen: 7, id:
"slipper-nose-knuckle-3r", winner: <the polish paragraph, or the polished config if its verifier confirmed a held-out
gain >= 1>, short: "slipper", slug: "slipper-nose", prior_art: "gen-6 roller-longdyad:
pipeline/conformal/param_cad/user_style_roller.py, pipeline/concept_l1/build_roller_l1.py, designs l1_roller-longdyad /
user_roller_longdyad (read-only)", new_mechanism: "the hardened nose (stock O2.5 m6 dowel) on the drive crank, sliding on a DLC flank in
place of the MR63ZZ roller, spring-closed", do_not_edit: <files other running workflows edit>, date, no_render: true,
branch, trailer}`. Then the slipper's M5 action: R17 on the return stroke at mu 0.087 / 0.12 / 0.15 once the CAD
exists, and the wear test (ROUNDS round 11 "Lead bookkeeping"). Consider trimlug's lug trim in the built horn lug if its
audit passes (T5 depth). An EVOLUTION.md entry with `tools/evolution_snapshot.py` for every judged build.

**Gen-6 leftovers** (docs/research/roller-longdyad-gen6_fix_check.md section 8): attribute the 10 step-1 body-contact
poses (`judge/workspace.py --step 1` on 8e60d0e and on l1_roller-longdyad, then judge/body_regions.py); the R1 -1.0 vs
the L1 (lower the crank boss or move the follower beside it); the crank pivot pin fit and the crank-link 1a tolerance
(0.108 mm). Stills wait on the user (section 7).

**Slipper-nose record fixes** (ROUNDS round 11 "Lead bookkeeping", still open at 12:49): the row's verdict text still
starts "screened -", it has no `v_contact` (0.0054), and its complexity shows 22.25 against 18.25 like-for-like.

**The alignment auditor.** Wired since 2026-10-16 ~20:50 UTC (CLAUDE.md "Alignment auditor", user decision (4): keep it
running at all times): `tools/workflows/alignment-audit.js` audits every claim, verification, new leader and metric
change, a skeptic tries to refute each watch / gamed verdict, and the verdicts go to the append-only ledger
`docs/alignment/ledger.jsonl` (`python3 tools/alignment_ledger.py latest`; `get <id>` exits 3 when gamed; `due` lists
what needs an audit). The loop runs it in an Audit phase between Screen and Close. At 12:49 the ledger has two gamed
designs (dipped-law-groove-knuckle-3r, seed-offset-3r-slides); every leader is watch.

**Watchdog, dashboards, compute.**
- Watchdog: a session cron every 15 min (prompt in `docs/OPERATIONS.md` section 3), plus the hourly alignment audit.
  Both are session-only: re-create them every session.
- Dashboard: https://claude.ai/artifact/DjCGir1xvu6es36Lx1nwRA is this account's live dashboard, the public-mirror page
  (`docs/dashboard/public/index.html` + its `data/*.json`) republished by `file_path` from this session; a new session
  `Artifact read`s it first and publishes with `url` (OPERATIONS section 4). Its headline is the best verified design
  with <= 3 active joints; a row with `leader_ruling` shows "Verified (tie)". Build the data with `tools/dash_refresh.sh`.
  The first account's production dashboard (AMhjuE83FBhGXxu8vQBN7r) and public mirror (5dan8agUow4XR81Pr91XhF) belong
  to that account's org and cannot be written from this one.
- The CPU farm is RunPod endpoint `exo-cpu1` via `tools/cloud_run.py` (`docs/CLOUD_RUN.md`). Key: OPERATIONS section 5
  (never print it). Budget: section 7, item 1; `tools/runpod_guard.py audit` before and after each batch, `workersMin`
  0 after it. At 12:46 the audit read exo-cpu1 workersMin 0 / workersMax 9 and exo-blender-cycles 0 / 1. The user's
  `exo-blender-cycles` is for stills only; never touch pods named `crl-*`.

## 9. Next steps, in priority order

1. **Keep the loop running and close round 11** (section 8): trimlug's audit, the closer, then round 12 at once.
   - *Lead, 13:30 UTC (commit time):* round 11 closed with trimlug-k165 as its winner (18.51 / 23.47, WATCH, not a lead
     change). trimlug IS slipper-nose plus one cut on link 1a (the horn lug trimmed at the flank's farthest contact + 1.5
     mm wall: T5 contact depth bench 14.74 -> 13.18 mm, held 46.35 -> 40.59 mm, same params and complexity). So its
     generation CAD is the gen-7 slipper-nose CAD (wf_ecb7b6f8-d22) with that cut applied - a judged design change on
     user_slipper_nose, not a third builder - and its final polish is slipper-nose's (wf_f38de10b-cb2, same params).
   - *Lead, 14:30 UTC:* the slipper-nose polish adopted nothing (pre-registered pick1 -0.59 held out unpriced,
     docs/research/slipper-nose-knuckle-3r_final_polish.md). Its 'crank-side cliff' is a design-space artefact, not a
     buildability problem (docs/research/slipper_flank_robust.md: as built, crank PA reaches its 38.03 cap only at r_c
     -0.4..-0.5 mm). Carry into the gen-7 full CAD (and its drawing notes) if its builder has not: keep the verified flank
     (beta -176.684, no beta step), build the +0.75 deg K lead (lobe-ring dowel +0.35 deg of q2, stop B at q2 -15.47),
     nose hole / crank pivot / lobe profile +-0.02 mm true position, r_c +-0.1 mm, assembly note "K phase at onset
     +0.75 +-0.3 deg, shim the dowel". Held-out th stays 5.068 with the lead (5.5 is not reachable by a lead). R17's
     forward-stroke twist is 4.97 of 5.0 deg at mu 0.15 (audit 14:03, rate + preload de-rated) - the thinnest margin.
   - *Lead, 15:23 UTC (audit 15:17, ledger WATCH):* the full CAD user_slipper_nose is 8/19; its mu 0.15 forward bound is
     5.00081 deg raw = FAIL (judge/dynamics.py now gates unrounded). The drive's horn rule caps mu at 0.108-0.113, so the
     wear-test pass line is mu <= 0.105 (forward twist < 4.78 there) and the drawing should say so. The drawing's K-phase
     tolerance "+0.75 +-0.3 deg" is wider than the red team's stack covers (+0.45 nets 1 held-out pose under th 5; the
     high end pushes the horn PA past 43 at mu 0.12): tighten it (about +0.75 +0.15/-0.1) in the next CAD fix pass.
   - *Lead, 15:55 UTC:* gen-7 CAD workflow wf_ecb7b6f8-d22 DONE: user_slipper_nose 8/19, verifier NOT REFUTED with
     open items (pipeline/full-exo/designs/user_slipper_nose/VERIFY.md: R1 -0.94 vs its L1 from metal riding high,
     running-gap tolerances, knee-stop tolerance, r 1.25 nose has no held-out wear, drawing names). Fix pass running
     LOCALLY as wf_788f3848-0a6 (template redteam-fix.js, $0): those items + the 15:23 items + the round-11 winner's CAD
     user_trimlug_k165 (same builder with the lug cut). Stills still wait for the user's yes.
   - *Lead, 17:20 UTC (audit 17:15):* the drawn K-phase band +0.75 +0.15/-0.10 deg holds held-out th >= 5 only on an
     RSS stack; on the red team's worst-case linear stack it nets -0.12 deg (~4.996 held out, 1 pose under 5). The
     drawing must state RSS, or the low end becomes -0.02 deg. Close T3 only after the fix pass re-judges the 16:29 build.
   - *Lead, 18:12 UTC:* round 12 closed; its winner conecut-knee-knuckle-3r (verified 18.28 / 22.38) is ruled a TIE
     (leader_ruling, ledger 17:57:13Z). Its final polish is SKIPPED on purpose: four env polishes of this family moved
     nothing and the family's ceiling is measured (ghost 17.86). Its generation CAD = the gen-7 builder with conecut's
     re-centred never-binding knee (lE 97.1 / lc 24.4) + the J3 dowel stop, queued for when the gen-7 fix pass
     (wf_788f3848-0a6) finishes its check - the box is saturated (load ~17) and the jump track has priority.
   - *Lead, 18:35 UTC:* conecut-knee became the verified lead (18.28 / 22.38, user's plain-gap rule; the lead's CI tie
     rule withdrawn and put to the user). Gen-7 fix pass DONE (R1 81.18 slipper / 81.30 trimlug, verifier NOT refuted;
     its last judges run as scratchpad/fix/judge_rest.sh). Gen-8 CAD of conecut-knee launched (wf_5f217f1a-14b, local,
     no render) from the gen-7 builders, closing the verifier's D1 / D2 / D3 / O3 items. Lead ruling O4: link 2 is
     machined from solid (3+2-axis), so CLAUDE.md CAD ruling (2) allows its up-to-70-deg drop at J2, stated on the part.
   - *Lead, 20:25 UTC (audit 20:15):* the gen-8 L1 builder (pipeline/concept_l1/build_conecut_l1.py line ~86) sets the
     J3 stop's acceptance window (-112.40 <= J3MIN <= -111.25) from HELD-OUT q3' values - a held-out leak into a part
     spec. The window must come from the fit / envelope benches (fit evidence allows -112.79 to -98.43; the exact bench
     prefers -110.9) and the held margin is then reported, not designed to. Fix in the gen-8 CAD's fix pass.
   - *Lead, 21:35 UTC:* main loop rounds 10-13 (wf_9b682834-6df) DONE. Round 13 winner desmo-conecut-knuckle-3r
     (verified 18.98 / held 23.19, cx 16.5, spring-free, WATCH) - not a lead (lead conecut 18.28). Measured: the knuckle
     family caps at 269-271 takes; the plain 3R's kinematic bound at the back seat is 250; only the cap pole shows a
     kinematic path to 95 (281 / 360) = the jump track's J2. Main loop relaunched as rounds 14-16 (wf_f06588fd-4d1) with
     the closer's focus (complexity on desmo-conecut; the 4 shared overhead contacts). Desmo-conecut's polish is skipped
     (family ceiling); its generation CAD (gen-8 builder + the desmo drive) waits behind the gen-8 conecut CAD.
   - *Lead, 22:27 UTC:* gen-8 full CAD user_conecut_knee built + judged: 8/19 = its L1 (R1 81.6 vs L1 81.9, R16 66.7,
     R17 PASS; M5 forward bound 4.54 / 4.67 / 4.77 deg at mu 0.087 / 0.105 / 0.12 - the margin is back vs slipper's
     5.0008 fail at 0.15); D1 / D2 / D3 / O3 / O4 closed. NEW defect found and fixed in user_style_conecut.py: the slot
     cutter shared since gen 4 put slot-end centres beyond the stop angles, so built K / J2 stops engaged 0.88 deg late
     and J3 0.76 deg late (outside the held margin). Every earlier full CAD (gen 4-7) carries it; any rebuild of those
     must use the gen-8 cutter. Its independent verifier is running.
   - *Lead, 23:10 UTC:* gen-8 workflow wf_5f217f1a-14b DONE - user_conecut_knee NOT REFUTED (VERIFY.md: every re-run
     judge matched to the digit; R17 nominal twist 3.99 deg; knee 47.7 deg under its stop vs gen-7's 1.6). Open small
     items: E strap rides 1.33 mm over the model (gen 7: 0.52); hub K / hub 2 slot-band 1.42 mm missing from the
     builder's summary; spacer O4.5 vs the 683ZZ / MR63ZZ inner-ring abutment diameter unchecked; wave washer has no part
     number; L1 Walking-arm-swing R1 97.6 -> 81.4 unattributed; verify the slot-cutter claim on user_slipper_nose with
     stops_cc.py. Desmo-conecut's generation CAD (round 13 winner, not a lead) is DEFERRED while both discovery loops
     need the 4 local cores (farm closed); start it when a loop ends or the farm reopens. Stills wait for the user.
   - *Lead, 00:58 UTC 10-18:* the box went idle (load ~4: both loops planning), so the desmo-conecut generation CAD
     (gen 9, spring-free desmodromic K on the gen-8 conecut builders) started as wf_1cb39fa0-d38, niced, local, no render.
     Round J2 (jump) closed: virtual J2 at the cap pole dead (86.95-108.22 fast vs the plain cap 3R 63.18), deltoid-crest
     47.86 dead; J3 = 4-joint ghost gates. Round 14: cap-plateau-knuckle-3r dead at gate 0 (32.08 frozen, 247 takes) -
     the cap-pole seat is closed on both tracks.
   - *Lead, 03:13 UTC 10-18:* round 14 closed: winner crest-knee-3r 32.84 (not competitive, 14.6 behind the lead) - its
     polish and generation CAD are SKIPPED on purpose (the CAD rule is for showing the best designs; this one is far off
     the lead). lowarm-halfring-knuckle-3r 17.96 is GAMED (final, skeptic 03:00: the link-2 lift was picked from 794
     configs on the claim bench; held 22.70 behind the lead). Measured: the 3-joint seat question is closed - back seat
     269-271 takes (ghost), cap 247 (metal), crest 228; even 271 takes at 0 contact floors the gap at 14.72 (score
     ~94.65), so 95 (279 takes) may be out of reach for 3 DOF at the allowed seats. Round 15 builds the 3-DOF take-bound
     table; if it stays < 275 that is a USER decision (accept 4 DOF, or accept < 95) - the jump track's 4-DOF relays so
     far all lose in-band (lead-relay-j0 24.92, backbridge 32.13, wobble dead, cap-nullspace 70.64).
   - *Lead, 03:55 UTC 10-18:* jump round J3 (round 103) closed with no lead change: both 4-joint levers died on metal,
     not kinematics. The relays scored lead-relay-j0 22.18, backbridge 32.13 and wobble 32.92; the cap null-space scored
     57.70 (all frozen exact, all audited and upheld). Jump track relaunched as rounds 104-106 (wf_6c42dda0-f91), focused
     on J3's lessons:
     - a price-first gate (added metal priced at the measured +0.2 points per mm before any ghost);
     - lens a, a length-changing link: one real catalogue miniature guide inside link 2, or the counted cuff slide. It
       targets the 73 stretched-fold losses and adds no hub and no ring crossing;
     - lens b, one outside-field mechanism, only if it passes the pricing;
     - machinery fixes: the verify bar is the lead's 18.28, near-touch objective everywhere, and a ledger entry for
       each round winner.
   - *Lead, 05:20 UTC 10-18:* the gen-9 CAD of desmo-conecut-knuckle-3r (wf_1cb39fa0-d38) is done: L1
     l1_desmo-conecut and full user_desmo_conecut, judged, with EVOLUTION row, snapshot and VERIFY.md. No render; stills
     still wait on the user's yes.
     - The full CAD scores R1 81.8 / R1-aim 52.3 / R4 74.8; gen 8 scored 81.6 / 52.7 / 74.1. R7 PASS.
     - **R6 FAILS at 1.50 mm.** The model puts the stage-1 groove layer inside link 1b's J2 lower plate (F+0.11..F+1.61),
       and no feasible pin exists above link 1b (stage1_level_scan.json). So the verified stage 1 cannot be built in
       the v5 stack.
     - The model's ring2 samples sit +7.28 deg off link 2's true frame. That sector carries +0.67 of the claim's in-band.
     - The K play (0.16-0.28 deg, no spring) puts the held-out th margin at 4.915 / 4.893.
     - The independent check: not refuted as a record of the verified model, and not buildable as the CAD itself says.
     - These may make the verified 18.98 optimistic, so a targeted alignment audit is running (wf_bd60ecda-9e0; the
       lead is the reference). The lead conecut-knee is not affected: it has a different K drive, and its gen-8 CAD
       passes R6.
     - Open drive items from the CAD's red team: the stage-1 ridge reaches 3.8 GPa against 440C's ~3.0 GPa limit, and
       a +0.25 deg K lead with kslot 46.9 needs a verified re-wear.
   - *Lead, 05:29 UTC 10-18:* the container restarted at ~05:25 and stopped every background workflow. All three were
     resumed with resumeFromRunId and the same args; completed agents replay from cache:
     - main loop wf_f06588fd-4d1 (round 15);
     - jump loop wf_6c42dda0-f91 (round 104; its ideation was cached, and screening started);
     - the desmo-conecut audit wf_bd60ecda-9e0.

     The session crons were re-created: watchdog 6a968e7b at 7,22,37,52, hourly audit c3bb6ae3 at :41. The agents'
     uncommitted outputs were saved first (a813bce).
   - *Lead, 06:00 UTC 10-18:* the desmo-conecut audit is final WATCH (8edc253). The 18.98 stands as the model's number,
     not as a buildable drive. Stage 1 sits inside link 1b's J2 plate for every glev in the search box. Re-worn at the
     only plate-clearing level with a feasible pin (F+3.9), the bench gives 20.50 (+1.52). No buildable stage-1 placement
     is on file. The ring2 offset is worth +0.09.
     - desmo-slipper (18.95) inherits the same layer. Its row is flagged, and the next hourly audit picks it up.
     - Both row verdicts now say this.
     - Round 104's desmo-window-knuckle-3r (stage 1 raised into link 2) is the fix attempt.
     - *06:31:* the desmo-slipper audit is also final WATCH. Its stage 1 sits in the same plate, and its model is the SOURCE
       of the level formula. Re-worn at F+3.9: 20.38 / 25.33 (+1.43, a lower bound). Its old 'paired TIE' was at a refuted
       placement. desmo-window is DEAD at 20.43. **No desmo-family stage 1 is buildable on file.** The family's
       simplicity edge (cx 15.75-16.5) has no buildable number below ~20. Row texts were corrected by the lead.
   - *Lead, 07:10 UTC 10-18:* a second container restart at ~07:06. Recovered as before: WIP saved (f164440); the main
     loop wf_f06588fd-4d1, the jump loop wf_6c42dda0-f91 and the hourly audit wf_b8e85540-23f (freek-oracle-route +
     lowarm-halfring) were resumed from cache; crons re-created (watchdog d07fc9f7, hourly audit ca2ab295). The recovery
     steps are now written in OPERATIONS section 3, 'After a container restart'.
   - *Lead, 07:45 UTC 10-18:* this was a measurement change, not a design change. The desmo-window death audit (14dfecc)
     found the desmo ring2 sampler is ~4x the kit's density. The lead's cross-row density audit (0696192;
     tools/sample_density.py; alignment_audit 2026-10-18.1 adds a 'density' check, SELFTEST PASS;
     docs/alignment/sample_density.md) re-weighted every verified row under 20.5 at the kit's 1 pt / 4 mm2.
     **The top order is unchanged.** The lead conecut-knee reads 18.28 / 22.43 (held was 22.38), and no row moves under
     it. Moves on the rows:
     - desmo-conecut 18.98 -> 18.68 (18.49 at 4x);
     - desmo-slipper 18.95 -> 18.81;
     - slipper-nose / trimlug +0.07 (their roller is 4.55x and well placed);
     - lowarm-halfring 17.96 -> 18.04.
     The desmo stage-1 lift costs +0.31..0.44, not ~1.45. Exact re-wears still to run, ~55 min each at load 18:
     desmo-conecut and desmo-slipper (`CB_EXACT=1 python3 tools/sample_density.py rewear <id> bench|held`).
   - *07:45:* two final verdicts.
     - freek-oracle-route-knuckle-4r is GAMED (P1). Its 17.35 bench lead is a coin flip that reverses held out, and its
       stop was placed from claim-bench binders. The row stays screened with 4 DOF.
     - lowarm-halfring-knuckle-3r is GAMED (M3 + P1): its stage 1 sits inside the plate. Cell A was re-verified at 18.83
       (pad play), and at the plate-clearing level it reads 18.65.

     No lead change; the lead is conecut-knee 18.28.
   - *07:55:* the skeptic's reporting findings on freek-oracle-route are fixed.
     - dash_build.py now reads a row's top-level frozen_gap; the page had shown the fast 9.56.
     - The row's part counts now include the J3 dowel, so complexity is 32.5 -> 33.25 on the page.

     Open for the auditor:
     - FOLD_KEY in tools/alignment_audit.py matches none of the fold readings on file (m3e_min / family_own_min /
       fold_margin_th.*.min_margin_th). Adding them would make the family reading (0.32 deg on a taken held clip frame)
       fire gamed, which depends on the open T3 question (which th reading holds with J2 free in state 2). Decide T3 first.
     - The row's v_* fields hold the STATIC reading (16.20). The continuity rule makes the connected 17.35 the claim, and
       the row is flagged GAMED either way.
   - *Lead, 09:05 UTC 10-18:* jump round 104 (J4) closed (3c2edef).
     - The re-audit keyed on the verified claim lowered freek-oracle-route-knuckle-4r to WATCH (auditor 08:29, skeptic
       08:43). T3 was measured: the model's one fold reading is the right one.
     - The lead flipped the row to VERIFIED: 16.20 frozen exact (score 94.11), held 21.89. This is **the best verified
       number on file**, but it has 4 counted joints (cx 33.25), so it is NOT the headline lead (user 2026-10-17; the
       dashboard's headline takes <= 3 active DOF).
     - Against the lead it is a coin flip: -2.08 bench (P 0.745), -0.49 held (P 0.622). Its contact depth is 3.9x.
     - Its final polish (templates/final-polish.js, local, farm closed) was launched because its q3max search was a 1-D
       8-point sweep. It is also the measured answer to how far 4 DOF goes, for the user's 3-DOF vs 95 decision.
     - The generation CAD comes after the polish and the open items: J3 dowel force, K-spring hold R17, cuff twist.
   - Round 104's other rows: armarc 18.01, kfree-armarc 26.42 and desmo-window 18.80-19.01 at kit density are dead, all
     audited. The jump loop wf_6c42dda0-f91 runs on to rounds 105-106 on the closer's next focus (carriage-borne relay
     rail, psi2, ER binders).
   - *Lead, 11:05 UTC 10-18:* freek-oracle-route's final polish was CONFIRMED by its independent verifier
     (wf_1d92c2e0-413; d196fc2; row polished_* fields; docs/research/freek-oracle-route-knuckle-4r_final_polish.md).
     - pick1: 15.40 bench (score 94.40, +0.81, noise).
     - Held out env-fit +2.06 (P 0.97); CAD-shape +1.38 (CI crosses 0).
     - Contacts halve: bench 15 -> 7, 78.55 -> 39.47 mm.
     - It is still 4 DOF (cx 33.25), so not the headline lead. No config reaches 95; 4 DOF tops out at ~15.4 here.

     **OPEN for the user (proposal B):** do poses the J3 stop REFUSES, which would be skin contacts without it, count
     as contacts? On that reading pick1's CAD-shape held gain is +0.76 (< 1) and its bench gain 0. Until the user
     rules, the current metric stands (a refused pose = lost reach) and both readings are reported. The polished claim's
     alignment audit is running (wf_555370a5-90c). The dashboard promotes it only on a non-gamed skeptic ruling.
   - *11:15 correction:* proxtrack's screen closed (fd3cff8). Its claim is 14.02 plain frozen exact (score 94.90; gate
     reading 14.40) at PHI 35 / ds 19.5 / rt 1.5 after a converged 219-config sweep. The pre-registered PHI 30 config
     reads 16.82 with the refined bump and 20.59 with the spec bump. The 13.39 below was an earlier reading that the
     screen superseded. It is unverified, 4 DOF, cx 52.5, and awaits round 105's verifier and auditor.
   - *11:05:* round 105 (jump J5) is screening. proxtrack-relay-knuckle-4r self-measures 13.39 frozen exact with its
     'refined bump' (17.31 with the spec bump). That is the first number on file under 95's 13.75, but it is UNVERIFIED
     and 4 DOF: the bump amount is the max over the lead's fit-bench poses (legal), and a ~4-point move from a bump
     reshape needs the verifier and auditor. desmo-geom is DEAD (no stage-1 pin inside O20 passes the PA gate), which
     closes the buildable desmo drive.
   - *Lead, 11:40 UTC 10-18:* the polished claim of freek-oracle-route is final WATCH, not gamed (skeptic
     11:24:30Z, 94e94e9). The dashboard now shows it as verified 15.40 (score 94.40), 4 joints. Fixes from that audit:
     - the row's polished_bench now carries pick1's own reach / follow / in-band / contact, so the board no longer shows
       the verified config's components;
     - the row's verdict states the like-for-like held number (20.50; the env-fit protocol gives 20.24);
     - dash_build.py reads a flat polished_bench;
     - the board marks 4-joint designs ('N joints, not ranked for the lead'), and the legacy core.js leader KPI filters
       to <= 3 joints;
     - dead / refuted rows now rank below live ones on the board. Two dead ghosts (proximal-j3-geodesic 16.91,
       desmo-vrocker 17.23) had ranked above the verified lead.

     The headline was verified headless: the 3-joint lead conecut-knee 93.4.
2. **Reach is the gap.**
   - The lead's gap is reach 17.50 of 18.49 (ROUNDS round 10 results). **Score 95 is gap <= 13.75**: +18 workspace
     poses at the lead's in-band and contact, 0.278 points each (ROUNDS round 11 plan).
   - The stretched fold wall (73 bench / 211 held-out poses) is the K drive's stroke (FINDINGS "The fold is two
     walls"). Behind it sit K's window (a1max), the K law (lobe PA 42, docs/research/longstroke_drive.md) and the long
     dyad's overhead press (inband polish). The in-family estimate for 95 is a ~75 deg stroke on a 28-32 / 48-50 K dyad
     (0.775-0.778 before the drive's metal); no measured config has reached it.
   - **Reach >= 0.80 needs both walls moved** (docs/research/fold_ceiling.md "Next" 3): a 4th joint or a new seat pair.
     The folded wall is hub 2's clearance (15 bench / 50 held-out poses; median need 71 mm vs 62). The measured 4th
     joint (spring-held, acting only past the 3R wall) traded 1:1 and took 0 folded poses, and the J1 re-seats measured
     dead, so the next morphology has to move the folded wall too.
3. **Finish the round-10 winner:** the slipper-nose polish (wf_f38de10b-cb2), then the gen-7 CAD (wf_ecb7b6f8-d22): L1,
   L2, judges, independent check, EVOLUTION, and stills on the user's yes. Then its M5 R17 check and the record fixes
   (section 8).
4. **Gen-6 leftovers** (section 8): the 10 step-1 body contacts, the R1 -1.0 against the L1.
5. **Complexity.**
   - The 3-joint knuckle class sits at 18.25-28.5 like-for-like; H1 sits at 0 at 27.20 (simplicity v2).
   - Once a verified 3-active design reaches score >= 95, switch the objective to minimum complexity at score >= 95
     (CLAUDE.md).
6. **Requirements no build has touched:**
   - R9 FEA (`judge/fea.py`, CalculiX, wired into judge_all.sh but skipped on recent builds);
   - R10 base slip (15.2 mm against 4; a passive fix is unknown);
   - R2 on the user's body;
   - R12-R15.
7. **Mind the farm line** (section 7): after it, local only, and the env fast caches live only on the farm volume
   (section 10).

## 10. Infrastructure facts that still hold

- **Python deps:** `bash tools/setup.sh` (installs libigl too). On a Python 3.13 cloud container it builds a uv 3.12 venv at
  `/opt/exo-venv` and puts `python3` / `python` wrappers in `~/.local/bin` (2026-10-17: the pinned scipy 1.13 and
  cadquery-ocp 7.7 have no 3.13 wheels, and scipy's Fortran build fails). Added 2026-10-17: `mujoco` is in
  `requirements.txt` (9ee8247); without it judge/dynamics.py skips R11 and R17.
- **The bench cache** (`.cache/`) is git-ignored, so a new machine rebuilds it:
  - locally: `nice python3 tools/concept_bench.py --build 60 160 --jobs 2` (~20 min on an idle 4-core box; 2 jobs = the
    local process cap);
  - on the farm: `tools/bench_cache_farm.py` for Bench(110,360).
  - Then `python3 tools/concept_baseline.py --n-clip 60 --n-ws 160` should reproduce ~68.9.
  - Added 2026-10-17: the envelope bench's (`env`) fast caches live only on the farm volume; rebuilding them locally
    took an estimated ~2 h at high load (FINDINGS, roller-longdyad final polish).
- **Local limits:** keep local jobs niced and at <= 4 workers on the user's laptop. Here the lead kept itself to 2
  processes (this container: 4 cores).
- **Farm facts:**
  - flash CPU serverless runs in EU-RO-1 only, with the content-addressed volume `exo-farm-cas`;
  - the worker image is Python 3.12 (`flash deploy --python-version 3.12`);
  - cadquery-ocp 7.7.2 is installed at runtime;
  - a stuck endpoint (unhealthy workers, queue not moving) is retired at once.
- **Agents:** an interrupt of the lead stops its background agents, so check what still runs after one. Commit only
  your own files: `git commit -- <paths>`.

## History

The previous handoffs: 2026-10-16 20:30 UTC (round 8, sidecar-longdyad verified at 18.91, the auditor being wired) and
2026-10-15 ~16:00 UTC (the morphology swarm and the 3R final `cad_r18_n3_s1392_1_f300`). Their state is in git
(`git log -- docs/HANDOFF.md`), and the older workflow copies are in `docs/handoff/`. The design-by-design story is in
`docs/EVOLUTION.md`, and the round-by-round story in `docs/concepts/ROUNDS.md`. Earlier history is in the archive at
github.com/aboufama/exo-arm.
