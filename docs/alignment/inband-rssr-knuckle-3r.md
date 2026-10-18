# Alignment audit: inband-rssr-knuckle-3r

Auditor run 2026-10-18 21:05-21:40 UTC (hourly audit). This run was due because the row was committed at
2026-10-17T15:21:40Z (8f69bd6), after the last audit at 13:18:02Z.

**What changed since 13:18.** The row's own change is small: `complexity` went from 28.5 to 24.5. That is a change of
ruler, not of design: the cuff knee's closure loop became free under simplicity v2.1, and the lead's 3d9dc71 and
8f69bd6 apply that to every pin-knee row. The claim did not move: polished pick3 is still 18.33 bench / 22.86 held,
the number the verifier confirmed in 931a8d1. What changed around the row is bigger:

- **The headline moved.** It is now conecut-knee-knuckle-3r at 18.28 / 22.38 held (verified, skeptic 2026-10-17
  20:15:35Z), while this row's `leader_ruling` still names slipper-nose.
- **The dashboard changed twice.** `tools/dash_build.py` now promotes a CONFIRMED polish to 'verified' only while the
  latest ledger entry is a non-gamed skeptic entry on the same claim. A `leader_ruling` now counts only when it cites
  a skeptic entry.
- **The leader family has been dynamics-judged.** `user_conecut_knee` and `user_slipper_nose` each have a
  `judge/dynamics.json`.

**Files for this run:**

- **Checks:** `docs/alignment/inband-rssr-knuckle-3r.json`, tool VERSION 2026-10-18.1.
- **Findings:** `docs/alignment/inband-rssr-knuckle-3r.findings.json`.
- **Ledger:** `docs/alignment/ledger.jsonl`, `by auditor`, run `audit:inband-rssr-knuckle-3r`.
- **New measurements, all written by this run:**
  - `docs/alignment/remeasure/inband-rssr-knuckle-3r_{bench,held}.json`: the tool's re-wear of the row's screen pick.
  - `docs/alignment/remeasure/inband_pick3/pick3_vs_conecut-knee_2026-10-18.json`: the per-pose wearer counts and
    paired bootstraps of pick3 against conecut-knee, lowarm-kphase-notch and slipper-nose.
  - `docs/alignment/remeasure/inband_pick3/headline_probe_{simple,public}_2026-10-18.json`.
  - `docs/alignment/remeasure/inband_pick3/probe_pick3_unpriced_bench.json`: the unscored workspace probe of pick3.
- **Cost:** local only (nice, OMP_NUM_THREADS=1, at most 2 processes), $0 farm.

## Verdict: WATCH (the ledger's verdict). The claim stands. The row's '(tie)' label is now stale: the row is behind the new leader.

- **Claim:** `polished_gap` 18.33 (pick3, priced), unchanged.
- **The buildable config reads the same number.** That config is `polished_params_cad_catalogue`: the igus KBRM-02
  O9 head at r_h 15.9, with the ear de-duplicated. Priced, it reads 18.33 bench / 22.86 held
  (`remeasure/inband_pick3/claim_O9rh15.9_dedup_{bench,held}.json`). So no part of the board's number is bought by the
  model's non-catalogue O7 socket. The old M2 finding is resolved in substance; see "Resolved since 13:18".
- **Against today's leader** conecut-knee (unpriced, margin 5, same poses, `tools/alignment_paired.compare_sets`,
  4000 draws). Positive means this row is worse.

  | leg | difference | 90 % CI | P(this row better) |
  |---|---|---|---|
  | bench | +0.03 | [-1.95, +1.93] | 0.49 |
  | held | +1.16 | [-0.06, +2.38] | 0.064 |
  | pooled | +0.84 | | 0.10 |
  | held, catalogue build | +1.24 | [+0.02, +2.47] | 0.048 |

  This row is behind the leader on every leg. It is more complex (24.5 against 18.5), and it has no dynamics run.
  The board ranks it below the leader, which is correct.
- **What is wrong is the label.** The pill still reads 'Verified (tie)' on a ruling made against slipper-nose, which
  is no longer the headline (finding NEW-stale-tie).
- **Nothing is gamed.** No hard rule is broken: 3 active joints, O20 hubs, 0 passive translations, and an own-state
  `th` minimum of 5.52 deg (0 taken poses under 5.5). No ranking against a better design is proven at 90 %.

## What the wearer gets (pick3 as claimed, priced; leader conecut-knee in brackets, unpriced at margin 5)

All counts come from the per-pose dumps, and each dump reproduces its claim: priced 18.33 / 22.87, unpriced
18.32 / 23.54, the leader 18.29 / 22.38. The sources are `docs/research/inband_env_polish/farm/claim_pick3_fit60_{bench,held}_perpose.json`,
`remeasure/inband_pick3/claim_O7nominal_unpriced_*_perpose.json` and
`remeasure/conecut-knee-knuckle-3r_{bench,held}_perpose.json`. The summary is in
`pick3_vs_conecut-knee_2026-10-18.json` under "wear".

- **Overhead (elevation >= 140):** 9 of 28 workspace poses taken on the bench and 19 of 71 held out [8 / 28 and
  18 / 71].
- **Raised arm by band (held):**

  | elevation | this row | leader |
  |---|---|---|
  | 90-120 | 68 / 140 | 76 / 140 |
  | 120-140 | 27 / 89 | 29 / 89 |
  | 140-160 | 11 / 35 | 11 / 35 |
  | 160+ | 8 / 36 | 7 / 36 |

  The leader's held-out lead is mid-raise: it takes 18 workspace poses this row does not, and this row takes 5 the
  leader does not.
- **Workspace reach:** 259 of 360 and 648 of 952 [262 and 659].
- **Taken poses with metal under 2 mm** (own metal): 22 bench and 54 held [23 / 57]. Counting the model's extra
  walls, it is 30 / 66 [33 / 71].
  - Under 1 mm: 3 / 15 [3 / 13].
  - With the buildable O9 head (unpriced): under 1 mm rises to 7 / 18 and under 2 mm to 21 / 56. The 1 mm near-touch
    gap rises by 1.64 bench and 2.22 held (`claim_O9rh15.9_dedup_*`). This is reported only; near-touch is not a gate.
- **Lowest metal on a taken pose:** 0.31 mm bench and 0.36 mm held [0.07 / 0.33].
- **Contact and its depth.**
  - Bench: 1 contact pose, 0.22 mm deep [4 poses, sum 20.24 mm, deepest 8.93 mm].
  - Held: 8 contact poses, summed depth 21.16 mm, deepest 6.09 mm at plane -90 / elevation 60 / axial 120
    [14 poses, sum 60.97 mm, deepest 9.86 mm at elevation 165].
  - Overhead held contacts: 4 (elevation 150: 3.80 / 3.70 / 0.10 mm; elevation 165: 0.76 mm) [7, deepest 9.86 mm].
  - Unpriced, the held contacts are 12, summed 33.27 mm, deepest 8.30 mm.
  - So this row presses into the arm less often and less deeply than the leader. That is a real wearer advantage,
    smaller than the leader's reach advantage in gap points.
- **Workspace in-band (unscored), unpriced pick3 on the bench**
  (`remeasure/inband_pick3/probe_pick3_unpriced_bench.json`; it reproduces 18.32; leader in brackets from
  `remeasure/conecut-knee-knuckle-3r_probe_bench.json`):
  - All taken workspace poses: 0.874 [0.868]. 12.5 % of the metal is over 14 mm and 3.3 % over 20 mm; the farthest
    sample is 32.6 mm.
  - Elevation 90-140: 0.837 [0.832].
  - Overhead: 0.921 [0.936]. Of the 9 taken overhead poses, 5 have metal under 2 mm and 1 under 1 mm [4 of 8, and
    0]. All 9 are under 3 mm.
  - Taken workspace poses with metal under 2 mm: 18 [28].
  - The first probe call passed `picks/pick3.json`, whose params are nested, and so wore the screen pick (18.87).
    This run re-ran it with the flat `pick3_params_flat.json`.
- **Springs:** static 0.165 N.m at J2, which gives 1.1 / 1.37 N at the cuff. That is 17 % of the R17 moment and 22-28 %
  of the cuff force (row `spring_R17`).
- **Stops:** the K drive's range ends on the law (dK 65.5 deg against about 47.5 deg taken). The folded dowel sits at
  smlo 5.03 deg, at the search's 5.0 deg floor, and is priced +0.5 deg to 5.53. On every taken pose the own-state
  `th` minimum is 5.589 deg bench and 5.524 deg held, with 0 poses under 5.5 (`polished_rules`).
- **Singularity:** transmission >= 52.2 deg; the knee window is at ang_min 25.22 deg, its search floor, not widened.
- **Not measured:** dynamics and cuff twist. No CAD and no `judge/dynamics.py` run exists for this id. The leader's
  CAD reads `moves_freely_nominal` true.
- **DOF and complexity:** 3 active joints, O20 hubs, complexity 24.5 [18.5]. The 28.5 -> 24.5 change is a ruler
  change, applied the same way on the leader family. `tools/simplicity.py` recomputes 24.5.

## Checks (tool, this run)

The tool's verdict is WATCH. It comes from one check, `held_out`: "no verified bench gap on the row". This is the same
false positive the skeptic has refuted three times. The row keeps status 'screened' with `v_gap` null, while the
verifier's numbers sit under `polished_*` and `docs/research/inband_env_polish/verify/`. Measured, the drop is
22.86 - 18.33 = +4.53 priced (+5.22 unpriced), under TH held_watch 6.0. The leader drops +4.10.

- **The tool still reads the screen pick, not pick3.** `remeasure` re-wears the row's `best_params` (cma3 p).
  - This run reproduced its 18.87 bench exactly (`remeasure/inband-rssr-knuckle-3r_bench.json`, 128 s).
  - Held out it reproduced 23.21 exactly (`remeasure/inband-rssr-knuckle-3r_held.json`, 411 s): near-touch 1 mm
    26.53, 2 mm 36.97, lowest metal 0.03 mm. The screen pick's numbers are unchanged since 11:12 on 2026-10-17, and
    no bench, kit or model file has changed since.
  - So near_touch, continuity, sampling and density describe that screen pick: <2 mm 34.12, shell2 15.25, knn flood
    21.39, rod 12 and L1a 8 samples, all ok.
- **contact_depth** reports 'not measured'. The polished claim's per-pose dumps sit under
  `docs/research/inband_env_polish/farm/`, where the tool does not look. This run measured the depths from them
  (above): they are shallower than the leader's.
- **complexity:** recomputed 24.5 = row 24.5.
- **reporting:** 'ok', with the dashboard showing 'verified' against the row's 'screened'.
- **judge_change:** 'ok'. 8f69bd6 touched `judge/dynamics.py` in the same commit as the row, but it changed only the
  row's complexity, and no dynamics judge runs on this id. So it is not P4.
- **rules:** 'ok'.

## Every catalogue pattern against this design (pick3 as claimed)

| pattern | present? | measured reason |
|---|---|---|
| T1 metal parked past the cutoff | no | contact 0.0027; near-touch 1 mm 20.52 and 2 mm 33.38 bench, against the leader's 34.84 at 2 mm; under-2 mm taken poses 22 / 54 against 23 / 57 |
| T2 band edge | no | for the screen pick, reading the band as 3-14 mm moves the gap +0.14 and 0.14 % of clip metal sits at 2-3 mm; pick3's clip in-band 0.907 is in line with that |
| T3 margin read on another angle | no | own-state `th` from the member frames: min 5.589 / 5.524, 0 poses under 5.5 |
| T4 bound walking to a singular posture | no (bounds at the user's floors) | smlo 5.03 at its 5.0 floor, priced +0.5; ang_min 25.22 at its floor (the pick's own value, not widened); transmission >= 52.2 deg |
| T5 depth-blind contact | no | held depth sum 21.16 mm, deepest 6.09 mm, against the leader's 60.97 / 9.86 |
| S1 skewed sample | no | held drop +4.53 (< 6); the env search bench has 0 poses within 2 deg of the held-out set (polish verifier) |
| S2 sparse sampling of bad metal | no | part-weighted in-band is 1.5 points above the sample-weighted reading; the thin rod (12 samples) and L1a (8) sit in band (0.87 / 0.98) |
| S3 unsampled bodies | no | every declared body has a metal group: rod, rodends, crank, horn, ear, L1a, L1b, L2, knee, pad |
| S4 skin, not body | not this design's | (rig-wide) |
| S5 static islands | no | kinematic and contact-aware floods drop 0 taken poses (`verify/caflood_pick3.json`) |
| S6 over-dense sampling | no | no part above 2x the kit's density; the ear double-sampling is removed in the catalogue build at the same gap |
| M1 virtual / zero-size | no | 0 passive translations |
| M2 a part that does not exist at that size | resolved | the catalogue O9 build reads 18.33 / 22.86 priced, the same as the board; one residual build-text conflict (proposal P-J) |
| M3 unchecked clash | no | the O9 head-rim clash (-0.22 / -0.49 mm) was found by the 12:28 audit and is fixed by the r_h 15.9 + ~0.6 mm spacer build, measured above |
| M4 idle mechanism | no | K spans 45.8-47.5 deg and the crank 33.7-34.8 deg |
| M5 spring that cannot hold | **watch** | dynamics unmeasured; the leader family is now dynamics-judged |
| P1 in-sample tuning | no | see S1 |
| P2 held-out leakage / choosing by held-out | **watch** | pick3 picked best of 3 after the claims (worst on the env-fit held leg; ranked last by the pre-registered envsel rule) |
| P3 re-measuring until lucky | no | the claim harness is deterministic; one claim per pick |
| P4 judge changed with the design | no | see judge_change |
| R1 self-measured shown as verified | no | the board's v_* equal the verifier's file; the promotion is now ledger-gated |
| R2 refuted records shown | no | |
| R3 best-of-many without spread | **watch** | 19.15 / 19.49 / 18.33; that choice alone puts the row above lowarm 18.47 and slipper-nose 18.49 |
| R4 pipeline recomputes the number | no | the board's 18.33 = `polished_gap` |
| G1 hugging 1-3 mm | no | 87 / 184 taken poses under 3 mm against the leader's 97 / 199 |
| G2 stiff spring | no (static) | 17 % of R17 |
| G3 cuff twist | unmeasured | under M5 |
| G4 singular posture | no | see T3 / T4 |
| G5 complexity hidden | no | 24.5 recomputed; the knee-loop ruler is applied as on the leader family; stale `mechanism.confidence` text ("--score 28.5") |
| G6 4th sensed joint | n/a | 3 active joints |
| NEW-stale-tie | **watch** | see below |
| NEW-reading-mismatch | **watch** | see below |

## Findings (all watch)

### NEW-stale-tie: the tie ruling has outlived its basis (carried, now live)

- **What the row says:** `leader_ruling` = "tie: slipper-nose-knuckle-3r | ledger 2026-10-17T13:18:02Z | ...".
  `dash_build` accepts it, because it cites a non-gamed skeptic entry, so the pill prints 'Verified (tie)'.
- **What the board does** (`headline_probe_{simple,public}_2026-10-18.json`, 'as published'): the headline is
  conecut-knee 18.28, "tied with Re-centred knee, chamfered hub". This row is not named, and it is behind the
  headline: bench +0.03, held +1.16 (P better 0.064), catalogue build +1.24 held (CI [+0.02, +2.47]).
- **Why the exo is not what the label says:** a reader sees 'tie' next to 18.33 / 93.3 against the leader's
  18.28 / 93.4 and reads it as tied with the leader. Against the leader it is behind on every leg, more complex, and
  without a dynamics run.
- **The latent half, measured:**
  - In runs A and B (conecut-knee flagged or refuted), the headline goes to lowarm-kphase-notch at 18.47. This row
    (18.33) and conecut-h2facet (18.28) stay out of the headline unnamed.
  - For this row that exclusion rests on a ruling against slipper-nose. Against lowarm it is bench -0.15
    (CI [-2.12, +1.71]) and held +0.66 (P 0.155), so the exclusion happens to be defensible, but only by accident.
- **Action (lead):** re-rule this row against the current headline or clear the ruling (proposal P-F). Either way no
  headline changes today.

### R3: best of 3 shown without its spread (carried, updated for the new board)

- **The board order:** 18.33 sits above lowarm-kphase-notch 18.47 (complexity 0, estimated) and slipper-nose 18.49
  (18.25), and this row is the more complex one (24.5).
- **The bench edge is noise:** paired unpriced -0.15 (CI [-2.12, +1.71]) against lowarm and -0.17 (CI [-2.01, +1.69])
  against slipper-nose.
- **Held out** it is behind lowarm by +0.66 (P better 0.155) and level with slipper-nose at +0.08 (P 0.366).
- **The three picks** read 19.15 / 19.49 / 18.33 bench (`farm/claim_pick{1,2,3}_fit60_bench.json`). The
  pre-registered pick1 would sort below both simpler rows.
- **Why the exo is not better:** the place above two simpler designs comes from the selection, not from a measured
  advantage.
- **Action:** show "best of 3: 18.33-19.49" (P-H) and a held-out column.

### P2: post-hoc pick (carried, unchanged)

- **Selection:** pick3 was chosen after the claims were known. The pre-registered envsel rule ranked it last:
  25.905 / 26.225 / 26.295.
- **The picks on each leg:**

  | leg | pick1 | pick2 | pick3 |
  |---|---|---|---|
  | fit60 bench | 19.15 | 19.49 | 18.33 |
  | fit60 held | 23.12 | 23.39 | 22.86 |
  | env-fit held | 22.43 | 23.47 | 23.57 |

  On the env-fit held leg pick3 is the worst of the three.
- **No held-out search was found,** so this is watch.

### NEW-reading-mismatch: a priced claim next to unpriced neighbours (carried, updated)

- **The readings:** the board's 18.33 is priced, and its neighbours (18.28 / 18.47 / 18.49) are unpriced at margin 5.
  On the bench the order holds (18.32 unpriced).
- **Held out, the reading decides the comparison:**
  - Against the leader it is +0.49 priced (P 0.307) and +1.16 unpriced (P 0.064).
  - Against lowarm, priced is level (22.86 against 22.87) and unpriced is 0.66 behind.
- **The ruling text uses the unpriced reading,** and the board shows the priced bench only.

### M5: spring hold and cuff twist unmeasured (carried; the asymmetry grew)

- **This row:** there is no CAD and no `judge/dynamics.py` run, and no `pipeline/full-exo/designs/*inband*`.
- **The leader family:** `user_conecut_knee` and `user_slipper_nose` now have `judge/dynamics.json` with
  `moves_freely_nominal` true.
- **What is unmeasured here:** this row's drive differs from theirs. It is an RSSR rod on two ball links instead of
  the nose / flank sliding pair. So the leader's dynamics result cannot be carried over: the friction sensitivity
  (the "mu <= 0.105" wear line in HANDOFF is the slipper's) and the cuff twist are unmeasured for this design.
- **No ranking depends on it today.**

## Resolved since 13:18 (no finding this run)

- **NEW-freetext-promotion.** `tools/dash_build.py` (lines 483-490) now promotes a CONFIRMED polish only while the latest
  ledger entry is a non-gamed skeptic entry on the same claim (|claim - v_gap| <= 0.005). It also accepts a
  `leader_ruling` only when the ruling cites a non-gamed skeptic entry. A self-written 'CONFIRMED' can no longer take
  the headline before an audit. What remains is in proposal P-G.
- **M2.** The buildable catalogue config was measured at the board's number: 18.33 / 22.86 priced. The unpriced reading
  is 18.32 / 23.62, against the O7 pick3's 18.32 / 23.54. What remains is a text conflict on the row (proposal P-J).

## Proposals (measurement or reporting changes, not applied, not inputs to this verdict)

- **P-F (repeated, now live): a tie ruling expires when its target stops being the headline.** The page then shows the
  row without '(tie)' until the lead re-rules it.
  - Measured effect today, with the page's own calcs on `morphs.json`: the pill on this row loses '(tie)'. The
    headline stays conecut-knee 18.28, because 18.28 < 18.33.
  - In runs A and B, this row (18.33) would take the headline over lowarm (18.47), and it would then need its own
    leader-change audit, since it is held-out behind lowarm by 0.66.
- **P-G (repeated, partly applied by the lead): the polished claim lives in the row and in the audit tool.**
  - The polish verifier writes `status: verified`, `v_*` and its file paths on the row.
  - `tools/alignment_audit.py` then reads pick3's per-pose dumps for held_out, near_touch, contact_depth and
    continuity, instead of re-wearing the screen pick.
  - Measured effect: the held_out false positive goes, with a drop of +4.53. contact_depth reads 21.16 mm / 6.09 mm
    held, below the leader's 60.97 / 9.86, so ok. No verified row moves.
- **P-H (repeated): show the best-of-N spread** ("best of 3: 18.33-19.49") and a held-out column. Display only.
- **P-J (new): one build config per row.**
  - `polished_status` still says "build the r_h +0.25 variant (polished_params_cad)". That config (r_h 15.0125) loses
    every pose with the catalogue KBRM-02 head (275.0, `remeasure/inband_pick3/` and the 13:18 skeptic). Meanwhile
    `polished_params_cad_catalogue_note` says "BUILD THIS config" for r_h 15.9.
  - Proposal: the lead strikes the first instruction or replaces `polished_params_cad` with the catalogue config.
  - Effect: none on any number. It prevents a CAD agent from building the config that fails.
- **P-K (new): the promotion should not flicker with every audit.**
  - `dash_build` promotes only while the LATEST ledger entry for the row is a skeptic entry. Every hourly auditor
    entry, this one included, therefore drops the row from 'Verified' back to its file status 'screened' until the
    skeptic's next entry, even when the auditor's verdict is watch on the same claim.
  - Proposal: promote while the latest skeptic entry on the same claim is not gamed and no later entry is gamed.
  - Measured effect: after this run's watch entry the row stays 'Verified'. Without the change it shows as a screen
    until the skeptic rules. No other row is affected, since minarc is verified in its own file.
- **Record hygiene (no proposal needed):** `mechanism.confidence` still says "tools/simplicity.py --score 28.5". The
  row's complexity and the recompute are both 24.5.

## Numbers I could not get

- **Workspace in-band of the priced pick3 and of the catalogue build.** The workspace probe
  (`tools/alignment_wear_probe_params.py`) can override params, but not the model's socket radius SC.ER or the
  pricing. So it measured the unpriced O7 pick3 on the bench only (above, 230 s). The O9 build's workspace in-band is not
  measured; its clip in-band (0.9011 against 0.9026) suggests a difference under 0.002.
- **Dynamics, R17 and cuff twist for this id:** these need an L1 / L2 CAD, which does not exist. The task is out of
  scope for an audit.
- **A held-out workspace probe of pick3:** skipped for time. It would take about 6 min on 1 process, and the held
  per-pose counts above already give overhead reach, the clearance floor and the contact depth.

---

*Earlier sections below: the skeptics of 2026-10-17 (13:10-13:30, 12:30-12:45 and 11:30-11:40 UTC), kept unchanged. The
2026-10-17 13:04-13:20 auditor section they answer is replaced by the run above and remains in git history (e95a8aa and
earlier).*

## Skeptic (2026-10-17 13:10-13:30 UTC, hourly audit 13:03 / display change a510cfe): final verdict WATCH

Rulings: `docs/alignment/inband-rssr-knuckle-3r.rulings.json`, which replaces the 12:45 rulings; those stay in git
history. Ledger: `by skeptic`, run `skeptic:inband-rssr-knuckle-3r`. Of the 9 reasons, 2 are refuted with evidence and
7 are upheld. The ledger computes the worst upheld level: **watch**. No leader change, and nothing hidden on the
dashboard today.

**What I re-measured.** Models unchanged, local only (nice, OMP_NUM_THREADS=1, at most 2 processes), $0 farm.

- **Gaps and wearer counts:** my own gap code (not `tools/alignment_paired.py`, not the audit tool) on the per-pose
  dumps. pick3 priced 18.33 / 22.87, unpriced at margin 5.0 18.32 / 23.54, the leader 18.48 / 23.45. All the
  auditor's wearer counts reproduce.
- **Paired bootstrap against the leader** (4000 draws, seed 7, resampled within kind, poses matched by
  kind / plane / elev / axial). Negative means pick3 is better.

  | reading | bench | held |
  |---|---|---|
  | priced | -0.16, 90 % CI [-2.15, +1.65] | -0.59, CI [-1.59, +0.31], P(better) 0.84 |
  | unpriced, margin 5 | -0.17, CI [-1.99, +1.68] | +0.08, CI [-0.84, +1.31], P(better) 0.38 |

- **The CAD config with the catalogue head, measured directly.** `picks/pick3_rh025.json` (r_h 15.0125) went through
  `tools/alignment_inband_rescore.py fit60 bench --fitonly`. With `--er 4.5` (KBRM-02, O9) it reads 275.0 with
  `why.parts` 183. With the model's O7 socket it reads 19.45, the verifier's `fit_fast`.
- **The headline what-ifs, re-implemented in Python** (not the auditor's probe) on `morphs.json`. The results agree
  with the probe, and I added one case: 'no lead' written on the leader's row.

### Rulings

- **held_out: REFUTED.** This is the same tool false positive as before. The check reads the empty top-level `v_gap`.
  - The verifier's files are `verify/claim_pick3_fit60_{bench,held}.json` with `final.gap` 18.33 / 22.86, a drop of
    +4.53.
  - Under the leader's protocol the drop is +5.22, and on the env-fit leg it is +5.24. Both are under TH held_watch
    6.0. The leader drops +4.97.
- **idle: REFUTED.** The knee is the two-pin cuff knee, which moves by design.
  - The row has `mechanism.cuff_knee` pins 2 and joints 2.
  - The model only reads `knee_moved` (line 291). The flag is set only in the two kneeless models.
  - K moves 47.47 / 47.68 / 49.34 deg (`dK_taken_max`), and the crank moves 33.7-34.8 deg (`cam.phi_max_taken`).
    Both are far above TH idle 2 deg.
- **NEW-stale-tie: UPHELD.**
  - The code is the same on both pages.
  - The what-ifs reproduce. If slipper-nose is flagged or refuted, the headline goes to trimlug 18.51 and the 18.33
    row is not named. A leading space puts the 18.33 row in the headline.
  - My extra case: 'no lead' written on slipper-nose sends the headline to trimlug, and both slipper-nose and
    inband-rssr sit below it unnamed.
  - `dash_build` copies the ruling with no trim.
- **NEW-freetext-promotion: UPHELD.**
  - The promotion is a `startswith('CONFIRMED')` test on hand-written text. No workflow writes `polished_status`.
  - The page shows 'Verified' unless the ledger says gamed. In my what-if, an unaudited row at 18.0 with status
    verified takes the headline.
  - `c_reporting` tests verifier files only when the row itself says 'verified'.
  - Today the shown v_* equal the verifier's file to the digit.
- **R3: UPHELD.**
  - The row is the lowest verified-basis gap on the board.
  - It is the best of 3 committed picks: 19.15 / 19.49 / 18.33.
  - Its paired bench edge is noise: -0.16, CI [-2.15, +1.65].
  - The board shows no spread and no held-out number.
- **NEW-reading-mismatch: UPHELD.** The held-out sign flips with the reading, from P(better) 0.84 priced to 0.38
  unpriced. The tie ruling correctly uses the unpriced reading, and the board shows only the priced bench.
- **P2: UPHELD.** On the env-fit held leg the picks read 22.43 / 23.46 / 23.57, so pick3 is worst and behind the
  leader's 23.45. It is best only on the fit60 legs. No held-out search was found, so this stays at watch.
- **M2: UPHELD, now measured at the CAD r_h.** The CAD config (r_h 15.0125) reads 275.0 with the O9 head. It lives
  from r_h 15.65. The row's `polished_params_cad.r_h` is still 15.0125.
- **M5: UPHELD.** This is a missing measurement. No file under `judge/` or `pipeline/` names this id, so there is no
  dynamics, R17 or cuff-twist run.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **M2's cited file was worn at the claim's r_h, not the CAD's.**
   - `fit_O9.json` ran on `picks/pick3.json` (r_h 14.7625, `sets` {}). The CAD config is r_h 15.0125.
   - The conclusion holds: measured directly, 15.0125 with O9 reads 275.0 (parts 183).
   - The polish verifier has no bench claim for the CAD variant. `polished_bench` holds pick3 (r_h 14.7625) and
     row_pick only. Only the held leg `verify/claim_pick3rh_fit60_held.json` covers r_h 15.0125, at 22.86, identical
     to pick3.
   - So the board's 18.33 is a config the CAD does not build. Neither config is buildable with the catalogue head.
2. **Overhead contact elevations are misstated in the wearer section.** The held-out overhead contacts are 3 at
   elevation 150 and 1 at 165, both priced and unpriced (`farm/claim_pick3_fit60_held_perpose.json`,
   `remeasure/inband_pick3/claim_O7nominal_unpriced_held_perpose.json`). The section says all 4 are at 150. The
   leader has 3 at 150 and 3 at 165.
3. **The ruling field has no authority check.**
   - `leader_ruling` is copied from any row with no test of who wrote it or which ledger entry it rests on.
   - A 'no lead' (or 'tie: X') written on the true leader's row removes it from the headline. The headline gives no
     trace; the pill shows it only on hover.
   - The auditor covered stale rulings on the ruled row. This is the other direction: a competitor's row can be
     dropped.
   - Proposal (not applied): a ruling counts only when it names the time of a skeptic entry for that row in
     `docs/alignment/ledger.jsonl` (ledger entries carry `time` and the HEAD at write time in `git`, not the commit that
     recorded them).
   - Measured effect today if applied strictly: the one ruling cites commit 48be5d5 and "12:45 UTC". The ledger's
     matching entry is the 12:36:27Z skeptic, with `git` b391a5f. So a strict check drops the ruling, and the page
     puts this row in the headline at 18.33 (probe run D). The ruling text would need the entry's time, so this is a
     process change for the lead to decide, not a defect in today's ruling.

**Final verdict (ledger, skeptic): WATCH.**

---

*Earlier sections below: the skeptic of the 12:28 pick3 leader-change audit (12:30-12:45 UTC) and the 11:03 audit's
skeptic, kept unchanged. The 12:03-12:35 auditor sections they answer are replaced by the run above and remain in git
history (48be5d5).*

## Skeptic (2026-10-17 12:30-12:45 UTC, pick3 leader-change audit): final verdict WATCH

Rulings: `docs/alignment/inband-rssr-knuckle-3r.rulings.json`, which replaces the 11:30 rulings; those stay in git
history. Ledger: `by skeptic`, run `skeptic:inband-rssr-knuckle-3r`. Of the 9 reasons, 4 are refuted with evidence and
5 are upheld. The ledger computes the worst upheld level: **watch**. **No leader change:** the honest held-out number
(23.54 as claimed, 23.62 buildable and de-duplicated) does not beat 23.45.

**What I re-measured.** No new runs of the models: everything was re-derived from the per-pose dumps already on file,
with my own gap and paired-bootstrap code (scratch, not committed). That code does not import `tools/alignment_paired.py`
or the audit tool. It uses 4000 draws, seed 1, with poses resampled within kind. Local only, $0 farm.

- **pick3 as claimed, priced:** `farm/claim_pick3_fit60_*` gives 18.33 / 22.87.
- **Under the leader's protocol (unpriced, margin 5):** `remeasure/inband_pick3/claim_O7nominal_unpriced_*` gives
  18.32 / 23.54.
- **Catalogue O9 head, ear de-duplicated, unpriced:** 18.32 / 23.62.
- **The leader:** `remeasure/slipper-nose-knuckle-3r_*` gives 18.48 / 23.45.
- **The claim harness is the row's protocol.** `farm/claim_PICKnominal_fit60_held_perpose.json` matches the row's own
  claim dump (`inband_drive/farm/claimA/`) pose by pose: 0 of 1154 poses differ.
- **Paired against the leader (gap A - B, negative means pick3 is better):**

| reading | bench | held |
|---|---|---|
| priced | -0.16, 90 % CI [-2.10, +1.66] | -0.59, CI [-1.60, +0.32], P(better) 0.84 |
| unpriced | -0.17, CI [-1.95, +1.72] | **+0.08**, CI [-0.83, +1.31], P(better) 0.38 |
| O9, ear de-duplicated, unpriced | -0.17 | +0.16, CI [-0.70, +1.32] |

### Rulings

- **held_out: REFUTED.** The check reads only the empty top-level `v_gap`. The verified numbers are on file:
  - row `polished_gap` 18.33 and `polished_held_out.fit60.pick3.gap` 22.86;
  - the verifier's re-runs `verify/claim_pick3_fit60_{bench,held}.json` `final.gap` 18.33 / 22.86.

  The drop is +4.53, and +5.22 under the leader's protocol (env fit: +5.24). All are under TH held_watch 6.0. The
  leader drops +4.96.
- **idle: REFUTED.** This is the same instrument false positive as before, re-checked on the current files.
  - The model only reads `knee_moved` (line 291). The flag is set only in the two kneeless models.
  - CELL = 'lead' is the pin knee, and the row has `cuff_knee.pins` 2.
  - K moves 49.34 deg (`claim_O7nominal_unpriced_bench.json` `dK_taken_max`).
  - The crank's "no span on file" is answered by `cam.phi_max_taken`, 34.8 / 36.1 deg. Both joints move far above
    TH idle_deg 2.
- **NEW-reading-mismatch: UPHELD.** The numbers are confirmed, and the comparison is like for like (the harness is
  the row's protocol, 0 / 1154 pose mismatches). Pricing moves 4 held-out contact poses into fold losses (contact 12
  poses / 33.27 mm -> 8 / 21.16 mm), and the held-out sign flips at the same reading.
- **M2: UPHELD.**
  - `fit_O9.json`: 275.0, parts 183. `fit_O9_rh15.4.json`: 275.0. `fit_O9_rh15.65.json` / `_rh15.9.json`: 20.62,
    parts 0.
  - The rim formula reproduces -0.22 / -0.49 mm.
  - `docs/research/sidecar_mechanism_redteam.md` row 2 independently names the KBRM-02 (O9 x 4) and the 0.6 mm
    spacer.
  - The row has no "KBRM" string, and its `polished_params_cad.r_h` 15.0125 is dead with the catalogue head.
- **P2: UPHELD, and slightly worse.**
  - The commit order is confirmed (28b9bb4 11:27:29 before 482d4a1 11:50:28).
  - The envsel rule (`sel_mean_near1` 25.905 / 26.225 / 26.295) puts pick3 last.
  - fit60 claims: bench 19.15 / 19.49 / 18.33, held 22.86 for pick3 (best).
  - **On the env-fit held leg pick3 is the worst of the three:** 22.43 / 23.46 / 23.57 (recomputed from
    `farm/claim_pick*_env_held_perpose.json`).
  - pick3 also had the deepest contact on the selection draw: `sel_depth` 14.78 mm against 3.62 / 5.64.
- **R3: UPHELD.**
  - `morphs.json` shows v_gap 18.33 for a row whose status is 'screened'. It ranks first, above minarc 18.40,
    slipper-nose 18.49 and trimlug 18.51.
  - `v_reach`, `v_follow`, `v_inband14` and `v_contact` are all null. The cause is `tools/dash_build.py` line 402,
    which reads `polished_bench['pick1']`; this row has 'pick3' and 'row_pick'.
  - The same card's verdict text still says "at PARITY with slipper-nose, not ahead".
- **NEW-inband-padding: REFUTED (below every documented threshold, no claim effect).**
  - The ear holds 44 samples, unchanged by the polish (`fit_base` / `fit_O9` `density.ear.n`).
  - De-duplicating it costs 0.0015 in-band (0.15 points), against TH part_weight_watch 3.0.
  - The tool's sampling check on this row reads ok, at -1.54 points: sampling penalises the design overall.
  - The claimed 18.33 / 22.86 is unchanged de-duplicated. The one reading it moves (unpriced held 23.54 -> 23.62)
    does not change the leader decision.
- **G1: REFUTED as a level, not as a count.** The counts are confirmed: under 1 mm, 6 / 25 against the leader's
  2 / 14, or 7 / 25 against 3 / 14 counting the model's extra walls.
  - These are near-touch readings. ALIGNMENT.md section 6 entry 2026-10-17.2 and `c_near_touch` (lvl 'ok') make them
    report-only, as do CLAUDE.md user decisions (3) and (6).
  - On the scored contact the O9 build is shallower than the leader: bench 1 pose / 0.22 mm against 2 / 14.75 mm;
    held 8 / 21.16 mm against 10 / 46.12 mm.
  - The counts stay reported, and M2 carries the O9 head.
- **M5: UPHELD.** This is a missing measurement: no dynamics, R17 or CAD run exists for this id. The static value
  reproduces: 1.8622 x (0.08 + 0.015 x 0.832) = 0.172 N.m.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **The claim's pick depends on which held leg is read.** On the env-fit held leg pick3 is the worst of the three
   committed picks (22.43 / 23.46 / 23.57), and its 23.57 is behind the leader's 23.45 even priced. The pre-registered
   pick1 has the best env-fit held number of any pick (22.43). The claim headlines fit60 (22.86), the only leg where
   pick3 is best. P2's "best of 3 on both claim sets" holds only for the fit60 legs.
2. **The dashboard card shows the polished number without its terms.** `tools/dash_build.py` line 402 hard-codes
   `polished_bench['pick1']`. For this row (keys 'pick3' and 'row_pick'), `morphs.json` carries v_gap 18.33 with every
   `v_*` term null. Its verdict text still describes the 18.87 parity row. Any future polish whose pick is not named
   pick1 will show the same way.
3. **The 2 mm counts in the "tie" argument leave out the model's extra walls (`cmin`).** Counting them, pick3
   unpriced held has 64 taken poses under 2 mm against the leader's 67 (not 52 against 62); bench is 26 against 30.
   The tie conclusion stands, but pick3's 2 mm advantage shrinks from 10 poses to 3.


---

*Earlier audit of this row (auditor 11:03-11:35 UTC, final WATCH); its skeptic section is kept below unchanged. Its auditor sections are replaced by the run above and remain in git history (commit before this one).*

## Skeptic (2026-10-17 11:30-11:40 UTC): final verdict WATCH

Rulings: `docs/alignment/inband-rssr-knuckle-3r.rulings.json`. Ledger: `by skeptic`, run `skeptic:inband-rssr-knuckle-3r`.
Two reasons are refuted with evidence and five are upheld, so the verdict is the worst upheld level: **watch**.

**What I re-measured.** Everything ran locally, nice, OMP_NUM_THREADS=1, at most 2 processes, models unchanged, no
farm spend.
- Frozen exact Bench(110,360) re-wears through `tools/alignment_const_probe.py --tag skeptic` (the constant is
  overridden in memory only):
  - `remeasure/inband-rssr-knuckle-3r_skeptic_bench_SC.ER4.5.json`;
  - `..._skeptic_bench_SC.ER4.json`;
  - `..._skeptic-cat-rh15.9_bench_SC.ER4.5.json`.
- New read-only probe `tools/alignment_part_density.py`. It reports samples per mm2 of each part and the crank angle
  along the model's own K grid.
- The gaps and contact depths, re-derived by hand from the per-pose dumps.

### Rulings

- **held_out: refuted.**
  - Both wears are measured, exact and frozen: `remeasure/_bench.json` 18.87 and `_held.json` 23.21. The drop is
    +4.34, under TH held_watch 6.0. The leader drops +4.96.
  - Re-derived from the per-pose dumps without the audit tool:
    - bench: ws 260/360, clip 110/110, in-band 0.8971, contact 3/373, giving 18.87;
    - held out: reach 0.6828, in-band 0.8956, contact 9/861, giving 23.21.
  - Timing:
    - pick rule `b6cfa9b` 09:36:11;
    - pick `f8fd767` 10:10:20;
    - `tol_rob.jsonl` first committed 10:13:10;
    - `p_held.json` first committed 10:26:59.

    No leak.
- **idle: refuted (instrument false positive).**
  - The "rigid knee" comes from the tool's regex for `knee_moved` anywhere in the model source. This model only reads
    the flag (line 291). The flag is set only by kneeless-roller and kneeless-sidecar.
  - The row runs the lead cell: longstroke `CELL = "lead"` loads roller-longdyad, and `cuff_knee.pins` is 2.
  - K moves 45.83 deg (`deep.coord_spans.dK`). The crank, measured here from the model's RSSR grid, turns 33.71 deg
    at K 45.83 and 34.15 deg at K 46.44. Both are far above the 2 deg threshold.
- **judgement:M2: upheld.** My re-wears reproduce the auditor to the digit:
  - O9 (SC.ER 4.5): 275.0, parts 373;
  - O8 (SC.ER 4.0): 275.0, parts 373;
  - O9 at r_h 15.9: 18.83, transmission 49.8 deg, contact 3 poses / 9.93 mm, fold margin 5.231.

  The arithmetic agrees: r_h - ER - HUB_R = 14.62 - 3.5 - 10 = 1.12 mm, and the O9 head leaves 0.12. The cone peaks at
  rest (the scan starts at K = 0; CONE25 gives dK_lim 0, `cone`). The number is not inflated, since the catalogue
  build measures 18.83. But the recorded `best_params` cannot be assembled from the KBRM-02 the repo names, and the row
  records neither the part nor r_h 15.9.
- **judgement:NEW-pair-knife-edge: upheld, count corrected.**
  - `tol_p.jsonl`: **10** of 34 neighbours lose every pose (the auditor said 11). All 10 sit at r_h - 0.25 = 14.3748.
    Five more cost +6.48 to +7.35 plain.
  - `tol_rob.jsonl`: 0 of 34 dead.
  - The robust build is 18.83 / 23.16 (`claims.robust_build`).
  - No points are bought, but `best_params`, which a CAD build would take, is the knife-edge shape.
- **judgement:NEW-inband-padding: upheld, sharper.** The attribution reproduces from `p_attr_bench.json`: ear deleted
  19.39, crank deleted 18.58.
  - **New measurement:** the ear is sampled at **0.50 samples/mm2** (44 on 87.6 mm2). Every other plate is at
    0.29-0.42:

    | part | samples / mm2 |
    |---|---|
    | hubs | 0.29 |
    | knee | 0.33 |
    | E | 0.34 |
    | boss, pad | 0.35 |
    | crank | 0.39 |
    | horn | 0.42 |
    | **ear** | **0.50** |

    The cause: the pivot disc `S.disc(6, 2)` and the 2 mm strip that starts at the pivot (model lines 199-206) sample
    the same area twice.
  - At the plates' median 0.342/mm2 the ear would carry about 30 samples. In-band would then be about 0.8955 on the
    bench (about 19.03) and 0.8940 held out (about 23.37). This is arithmetic, not a re-wear.
  - That is the leader's in-band (0.8955). **The row's in-band edge over the leader is the ear's excess sampling.**
  - Not refuting: per pose the row has 914 samples against the leader's 912, and fewer out-of-band samples (94.0 vs
    95.3 bench, 95.5 vs 96.4 held). The ear's size is fixed in code, not searched.
- **judgement:R4: upheld, sharper.**
  - `morphs.json` row 52: gap 12.79, frozen_gap null, v_gap null.
  - `dash_build.py` lines 408-409 read only `frozen_exact*`.
  - `leader.js` line 73 falls back to `gap` when `v_gap` is null. So the "Below the baseline now" list ranks this row
    **#1 at 12.79 ("claimed")**, ahead of every verified row (minarc 18.40, slipper-nose 18.49); trimlug-k165 13.02 is
    #2.
  - My fit-bench run gives 16.47, the row's top-level gap.
- **judgement:M5: upheld (missing measurement).** No dynamics, R17 or CAD output exists for this id in judge/,
  pipeline/ or pipeline/full-exo/designs/. The static 0.165 N.m (1.10 / 1.37 N) reproduces.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **Tolerance count.** 10 of 34 neighbours die, not 11. All 10 are the r_h -0.25 side (`tol_p.jsonl`).
2. **Ear double-sampling** (above). It is a per-part density artefact worth about 0.16 points. It is the whole of the
   row's in-band edge over the leader.
   - **Proposal (a measurement change, not applied):** sample every plate on one de-duplicated 2 mm grid. Estimated
     effect on this row: about +0.16 bench and held out. Other rows were not measured.
3. **Dashboard ranking.** The side list puts the in-sample 12.79 first among all live rows, above the verified leaders
   (R4 understated it as 12.79 vs 13.00).
4. **Catalogue head against its own horn lug (unmodelled).** This is the sidecar red team's own geometry (finding 2b):
   ball centre ZB 3.0 mm over the lug, head O9 x 4. The rim's height over the lug top is 3 - 2 cos t - 4.5 sin t; this
   formula reproduces the red team's -0.58 mm at 22.6 deg.
   - At this row's horn tilt it gives **-0.10 mm at the taken maximum 15.1 deg** and -0.38 mm at the range maximum
     19.4 deg (`probe extras.sc_info.tilt_max_taken[1]`, `tilt_max_range[1]`).
   - With the modelled O7 it is +0.16 mm.
   - So even at r_h 15.9 the catalogue-headed build needs a spacer of about 0.1-0.4 mm. This is a hand calculation, not
     re-worn.
5. **For the envelope polish (wf_d261725f-27c), in addition to the auditor's 7 items:**
   - The ear's pivot disc / strip overlap. A polish that moves `zc` / `clay` or enlarges the ear gains sample-weighted
     in-band from the double-sampled area.
   - With the catalogue head, transmission is 49.8 deg against the 48 deg gate: the bound must not be walked.

**Final verdict (ledger): WATCH.** The number is real: 18.87 / 23.21 reproduce, and the catalogue-headed robust number
18.83 is no worse. What stands against the record:
- `best_params` is not buildable with the named part and sits on a part-pair knife edge;
- the dashboard ranks the in-sample 12.79 first;
- the in-band edge over the leader is the ear's double sampling;
- the spring's dynamic hold is unmeasured.
