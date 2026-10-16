# Handoff: the state of the project (2026-10-16, last edit 20:30 UTC by git commit time)

Written for a reader with no context: a new session, a new model, or a person. Every number below comes from a file in
this repo (rows, verifier outputs, scorecards, ROUNDS.md, FINDINGS.md, EVOLUTION.md); the file is named next to it.

**Branch.** All of this lives on branch `claude/trusting-pasteur-6czobp` of github.com/aboufama/exo-shoulder. `main`
stopped on 2026-10-14 and is ~935 commits behind it: if you find no `docs/OPERATIONS.md`, you are on an old branch -
`git fetch origin && git checkout claude/trusting-pasteur-6czobp`. If your environment assigned you another branch, merge
this one into it first (`git fetch origin claude/trusting-pasteur-6czobp && git merge FETCH_HEAD`), then commit and push
to YOUR assigned branch (the environment's branch wins: it is the one your session may push) and pass it as `branch` to
every workflow script. Then write its name here.

**Clock.** Use git commit times (`git log --format='%h %ci %s'`) as the clock. Times agents wrote inside files
(`docs/concepts/events.jsonl` `time`, "verified at hh:mm" in prose) ran up to ~20 min AHEAD of the wall clock on
2026-10-16 (events stamped 20:22 and 20:31 sit in commits made at 20:09 and 20:13); never compute "silent for N min"
from them. The times in this file are commit times.

## Start here

**What this is.** A shoulder exoskeleton for the user's right shoulder (they are 185 cm tall, 6'4" wingspan). The whole
mechanism must ride within about 1 cm of the skin over the full range of motion, overhead most of all, and never touch
it. It has at most 4 degrees of freedom, and the user wants exactly 3 if possible. MVP1 is unpowered: rolling bearings
track the arm and the user adds rotation sensing. The work is a loop: invent a mechanism, score it on a body-model
bench, have an outside verifier re-measure it, build CAD of the winner and judge it against 19 requirements.

**Read in this order** (the one order; CLAUDE.md "Where things stand", OPERATIONS.md and README.md use it too: it is
CLAUDE.md's line-3 list with this file and OPERATIONS.md inserted after METHOD.md).
1. `CLAUDE.md`: the user's goal, decisions and hard rules. They are binding, and the user's words outrank everything.
2. `docs/METHOD.md`: how we work (Felix Rieseberg's essay, applied; link below).
3. This file: where things stand.
4. `docs/OPERATIONS.md`: how to run the machinery (workflows, farm, watchdog, dashboards, git).
5. `README.md`, then `REQUIREMENTS.md`: the 19 numbered requirements (R1-R17 plus R1-aim and R5-aim) and their judges.
6. `docs/PLAN.md`: the phases and the field's instruments.
7. `docs/FINDINGS.md`: everything measured so far, newest at the bottom.
8. `docs/concepts/ROUNDS.md`: the discovery rounds, each with its plan, results, lessons and next focus.
9. `docs/ALIGNMENT.md` (if present): the misalignment auditor's catalogue - ways a score rises while the exo does not
   get better. Then `docs/CAD_STANDARD.md` before touching any part, `docs/PIPELINE.md` before running anything.

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
  - **Near-touch**: metal < 1 mm counts as contact. It is the search objective, and claims report both plain and
    near-touch.
- **Complexity** (`tools/simplicity.py`, `docs/SIMPLICITY.md`): 0 is three pins and three links. It is shown next to the
  score and never folded into it.
- **The golden target** (user, 2026-10-16): verified score >= 95 (gap <= 13.75) at complexity ~0. Nothing has reached it.
- **Built CAD** is judged separately on the 19 requirements by `tools/judge_all.sh <design id>`, or on the farm by
  `python3 tools/cloud_run.py judge <id>`. The results go to `pipeline/full-exo/designs/<id>/judge/scorecard.md`.

## 2. Verified leaderboard (Bench(110,360) exact, frozen shape, margin 5, O20)

| design | verified gap (score) | held out | active DOF | complexity | status | key files |
|---|---|---|---|---|---|---|
| **minarc-stop-knuckle-4r pick1** (envp-F7-g35-6) | **18.40 (93.31)** | 21.31 env fit / 22.69 fit-60 | 4 (K spring-held, sensed) | 33 | verified final polish; it is the CAD config | rows/minarc-stop-knuckle-4r.json, docs/research/minarc_final_polish.md, docs/research/minarc_final_polish/picks/pick1_priced.json, verify/minarc-final-polish-verify.py |
| minarc-stop-knuckle-4r BDp | 19.54 (92.89) | 24.18 fit-60 / 23.68 env | 4 (K sensed) | 33 | verified; superseded by pick1 for CAD | same row, verify/minarc-bdp-judge.md, docs/research/minarc-bdp-verdict.md |
| **sidecar-longdyad-knuckle-3r** (round 8) | **18.91 (93.12)** | 22.67 | **3** (K slaved by a strap-level RSSR sidecar drive, never read) | 49 | **verified (commit 63167c0, 20:09 UTC): best 3-active design**; round 8 not yet closed (no polish, no CAD) | rows/, docs/concepts/sidecar-longdyad-knuckle-3r.md, verify/sidecar-longdyad-knuckle-3r.py |
| sidecar-parallelogram-knuckle-3r (round 8) | 19.13 (93.04) | 22.03 | 3 (K slaved by a strap-level sidecar drive) | 49 | verified (commit c7b5c53, 20:20 UTC); red-team flag: 2 mm near-touch 50.14 against longdyad's 34.03 | rows/, docs/concepts/sidecar-parallelogram-knuckle-3r.md, verify/sidecar-parallelogram-knuckle-3r.py |
| frontload-lobe-stopb-knuckle-3r | 22.82 (91.70) | 26.75 | 3 (K slaved by a rod drive, never read) | 49 | verified round-7 winner (a seat re-fit of the geneva rod, below the 1-point CAD-swap rule) | rows/, docs/concepts/frontload-lobe-stopb-knuckle-3r.md, verify/frontload-*_corr_*.json |
| geneva-tail-knuckle-pinknee-3r (rod) | 23.57 (91.43) | 28.12 | 3 (K slaved) | 42.5 (46.75 full record) | verified round-6 winner; gen-5 CAD in progress | rows/, docs/concepts/geneva-tail-knuckle-pinknee-3r.md, verify/geneva-*_corr_*.json, docs/research/geneva_rod_drive_redteam.md |
| cam-unfold-4th | 26.70 (90.29) | - | 3 | 33.75 | verified, not a contender | rows/, verify/cam-unfold-4th.py |
| arm-parked-knee-4r | 26.71 (90.29) | - | 4 | 32.25 | verified, not a contender | rows/, verify/arm-parked-knee-4r.py |
| skin-normal-3r-pin-knee **H1** | 27.20 (90.11) | 31.39 (minarc harness) | 3 | 19.5 | verified gen-3 winner; built (user_pinknee_h1b) | rows/skin-normal-3r-pin-knee.json, docs/concepts/skin-normal-3r-pin-knee.md |
| zc-frontier-3r (plain spherical 3R) | 33.51 (87.81) on the verifier protocol; 31.04 (88.71) fit on Bench(110,360) | - | 3 | **0** | verified ceiling of the zero-complexity class | rows/, docs/research/golden/README.md, docs/cad_context/zc-frontier-3r/KINEMATICS_BRIEF.md |

Paths are under `docs/concepts/` unless they start with `docs/research` or `docs/cad_context`. For reference, the old
champion spherical 3R scores 75.94 on the same bench (66.97 under the round-3 check set), and the first concept-bench
baseline was 68.93 (`rows/baseline-3r.json`). Held-out numbers come from slightly different harnesses, so compare them
within a row's references, not across rows.

**Reading it.**
- The best design overall needs a 4th, sensed joint: minarc's knuckle K (18.40).
- The best 3-active design is now within 0.51 of it: sidecar-longdyad (18.91), with sidecar-parallelogram verified
  next to it (19.13). They are the knuckle family with K slaved to J2, the drive moved down to strap level. Before them,
  the 3-active lead was the rod drive at 22.82.
- The simplest designs top out at 31-34.
- Every leader loses mostly REACH to the J2 fold. In-band (~0.89) and follow (~1.0) are close to their targets.

## 3. Round 8, in flight at handoff

The round-8 plan is in ROUNDS.md, its picks in `docs/concepts/round8_ideation.md`, and the timeline in
`docs/concepts/events.jsonl`. The lever is the "sidecar": the K drive moved down to strap level, so its metal sits in
band.

| design | frozen exact (score) | near-touch 1 mm / 2 mm | held out | complexity | state |
|---|---|---|---|---|---|
| sidecar-longdyad-knuckle-3r | 18.91 (93.12) | 20.00 / 34.03 | 22.67 | 49 | **VERIFIED** (`docs/concepts/verify/sidecar-longdyad-knuckle-3r.py`): reproduces to the digit; its added RSSR closure, ball-link tilt and real pressure-angle checks drop 0 poses; min metal 0.28 mm; continuity full 18.91 / knn 21.72 |
| sidecar-parallelogram-knuckle-3r | 19.13 (93.04) | 20.22 / 50.14 | 22.03 | 49 | **VERIFIED** (commit c7b5c53, `docs/concepts/verify/sidecar-parallelogram-knuckle-3r.py`): reproduces 19.13; added RSSR closure / ball-link tilt / lobe pressure angle / worn idle checks drop 0 poses; in-band14 sits at the 0.90 edge |
| sidecar-roller-flank-knuckle-3r | 20.08 (92.70) | 21.17 / - | - | 45.25 | screened (self-measured, converged, commit 0d48a62); its verifier was RUNNING at 20:24 UTC (agent verify:sidecar-roller-flank-knuckle-3r in wf_ee162f5e-871; untracked `docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py`) |
| twist-long-a2-knuckle-3r | 24.46 frozen (16.74 fast vs the lead's 15.57) | - | - | 49 | DEAD: the J3 twist walks back in every CMA stream |

For comparison, the previous verified 3-active lead (frontload) is 22.82, with near-touch 24.46 / 44.08 and held out
26.75.

- **Verified,** the sidecar is the first 3-active design at the 4-active pick1's level: 3.91 points better than the
  rod-drive lead, and 4.08 better held out.
- **Its gain is in-band only** (0.855 -> 0.897). Reach is unchanged at 0.725, with overhead 8/28 and fold losses 86 of
  360, so the fold still sets the gap.
- **Red-team flag:** parallelogram's 2 mm near-touch is 50.14 against the lead's 44.08. The 1 mm objective lets metal
  sit 1-2 mm off the skin on 44 frozen poses.

## 4. Built CAD and the 19 requirements

L1 is keep-out CAD and L2 is the user's standard (CLAUDE.md "CAD has two levels"). Each scorecard is in
`pipeline/full-exo/designs/<id>/judge/scorecard.md`; EVOLUTION.md has the full story of each build.

| design | level | passes | R1 2-14 / R1-aim 2-10 | R4 overhead | R16 workspace | notes |
|---|---|---|---|---|---|---|
| `user_minarc_pick1` | L2 | **7/19** | 80.5 / 47.2 % | 71.0 % | 74.0 % | K preload 0.04 N.m makes R17 pass (drift 3.72 deg, CAD); R8 203.8 g; R5-aim fails (4 DOF) |
| `l1_minarc-pick1` | L1 | 7/19 | 80.8 / 48.7 % | 71.8 % | 74.0 % | same preload change (R17 drift 3.68) |
| `user_minarc_bdp` | L2 | 7/19 | 80.0 / 51.0 % | 72.0 % | 73.5 % | re-judged after the judge fixes (5/19 when first built) |
| `user_pinknee_h1b` | L2 | **8/19** | 76.7 / 35.8 % | 71.2 % | 61.7 % | 3 DOF (R5-aim passes); R8 178.0 g |
| `l1_geneva-rod` | L1 | 7/19 | 81.1 / 51.1 % | 73.0 % | 72.6 % | 3 DOF; R17 fails only because the dynamics judge has no lobe-rod coupling term (a judge gap, not a measured jam) |
| `user_geneva_rod` | L2 | in progress | - | - | - | rebuilt 20:23 UTC (build.json, step/, exo.glb) from builder commit c23fedb (20:15, `pipeline/conformal/param_cad/user_style_geneva.py`); judges, stills, EVOLUTION entry and the independent check not yet done; the CAD agent (cad:user-geneva, wf_14bb06ea-22e) was still running |

- **Every build passes** R3 (follow, 99-100 %), R5 (<= 4 DOF), R6 (no part interference), R7 (valid solids), R8 (mass)
  and R11 (cuff pressure).
- **Every build fails** these:
  - R1 / R1-aim: proximity, best 81 % against the 90 % target;
  - R4: overhead, ~71-73 % against 80;
  - R16: workspace, 62-74 % against 90;
  - R2: 24.87 mm on every build, from the fused BOTTOM and the rig's self-intersection (EVOLUTION.md).
- **Not run or not done:**
  - R9 FEA was not run on the latest builds;
  - R10 base slip measured 15.2 mm against the 4 mm target, design-independent for a spherical chain (FINDINGS "R10 on
    the scapula handler");
  - R12-R15 (CAD standard, manufacturing quote, held-out bodies, real bodies).
- The zc-frontier-3r kinematics brief for an outside CAD tool is in `docs/cad_context/zc-frontier-3r/` (the user asked
  for kinematics only).
- Renders are in `renders/2026-10-16_userstyle_*`. Films are made only when the user asks (CLAUDE.md, 2026-10-16
  ~03:00: "focus everything on solution hunting"). Generation-winner CAD and stills still run.

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

## 6. Measured lessons that steer the search

1. **The fold is the limiter.**
   - The J1-J3 window is 2 min(a1, a2) - 10 wide, and wider arcs push hub 2 onto skin it cannot clear.
   - Frozen fold losses are 84-86 of 360 workspace poses on every rod-drive variant.
   - Raising reach (0.72 -> ~0.77 at in-band >= 0.88) is the half of 95 nobody has bought yet.
   - See FINDINGS "Reach is the fold" and ROUNDS.md round 7 "Next".
2. **Search on the near-touch gap.** Plain-gap optima put metal within 1 mm of the skin and lose 8-27 points when worn
   frozen. Also report the 2 mm near-touch: a 1 mm optimum can sit at 1-2 mm.
3. **Polish on a representative sample, claim held out.**
   - The search benches under-sample axial rotation (|axial| >= 150 deg: 6 % against 11 % held out).
   - Final polishes therefore use `tools/env_bench.py` / `tools/env_polish.py` and claim on the held-out set.
   - A polish replaces a CAD config only on a verified gain >= 1 point.
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

## 7. Open questions waiting on the user (unanswered at handoff)

1. **A sensed 4th joint (minarc pick1, score 93.31, 4 active) against 3 active joints** (sidecar-longdyad, verified
   93.12 in commit 63167c0 at 20:09 UTC, so the gap between them is now 0.51 gap points). Does a sensed passive used only at static extremes count as passive? If yes,
   pick1 counts as 3 active.
2. **The R17 posture margin.** Accept "upright use" as an MVP1 limit for pick1's K, or require the posture-free fix
   (section 6, item 6).
3. **Listed in ROUNDS.md "Needs the user's say":**
   - a cuff IMU instead of the two knee-pin encoders (complexity: pin knee 19.5 -> ~11.5, frontload 49 -> ~41);
   - a fold margin below 5 deg;
   - whether msub applies to a cam- or four-bar-slaved K.

Ask in chat for big updates only (CLAUDE.md rule 6).

## 8. What was running at handoff, and how to relaunch it

Everything below ran inside the lead session and dies with it. The procedures are in `docs/OPERATIONS.md`, and the
workflow scripts and templates are in `tools/workflows/` (README there). Every script REQUIRES `branch` and `trailer`
in its args (your session's branch and the two commit-attribution lines your system reminder gives); it stops without
them.

**The runs at 20:24 UTC** (`python3 tools/agent_tail.py` on the same machine; the run id maps to the track through the
script name it prints). On a new machine all of them are gone; their committed outputs are in git.

| run id | track | state at 20:24 UTC | what a new lead does |
|---|---|---|---|
| wf_ee162f5e-871 | discovery loop rounds 6-9 (launched from the old session's scratchpad copy of `discovery-loop.js`) | round 8: longdyad + parallelogram VERIFIED; roller-flank verifier RUNNING; closer not run | the round-8 steps below |
| wf_14bb06ea-22e | gen-5 CAD of geneva-tail-knuckle-pinknee-3r (rod) | L1 + drive red team done; `cad:user-geneva` RUNNING (build at 20:23) | the gen-5 steps below |
| wf_0729deda-636 | alignment auditor (the user's request, quoted below) | Audit phase RUNNING (audit:live, audit:catalogue+tool); `docs/ALIGNMENT.md`, `tools/alignment_audit.py`, `tools/alignment_wear_probe.py` being written (check git for what landed); its Wire-in phase (an audit phase in `discovery-loop.js`, `tools/workflows/alignment-audit.js`, a CLAUDE.md rule) and its skeptic review had not run | the auditor steps below |
| wf_a20bc382-f06 | cad-context zc-frontier-3r (the user's kinematics brief) | DELIVERED (`docs/cad_context/zc-frontier-3r/KINEMATICS_BRIEF.md`); the lead stopped it before its checkers on purpose (the user narrowed the brief); agent_tail still lists check:numbers / check:cold-read as RUNNING / STALE | nothing: do not relaunch |
| wf_33b5f96b-7b1 | this cold-start handoff (OPERATIONS.md, tools/workflows/, this file) | finishing | nothing |
| session crons | the 15-min WATCHDOG and the hourly alignment audit (cron ab52224e) | live in the old session only | re-create both (OPERATIONS section 3) |

Older runs listed by agent_tail (pick1-k-hold, judges-fix-and-gen4b, films, polishes) are finished; their results are in
FINDINGS / EVOLUTION. Before relaunching anything, check git for its outputs (a verifier that finished commits a
`verify/<id>.py` and the row's `v_gap`; an untracked `verify/<id>.py` means one was still running when the session ended).

**Round 8 (discovery loop).** One rule for an interrupted round (OPERATIONS section 2):
1. `tail -80 docs/concepts/ROUNDS.md`, `tail -20 docs/concepts/events.jsonl`, and every round-8 row's `status` / `v_gap`
   (`docs/concepts/rows/sidecar-*.json`, `twist-long-a2-knuckle-3r.json`).
2. If sidecar-roller-flank-knuckle-3r still has `status: screened` and no `v_gap`, verify it:
   `Workflow({scriptPath: "<repo>/tools/workflows/templates/verify-claim.js", args: {id: "sidecar-roller-flank-knuckle-3r",
   claim: "P1 config (docs/concepts/rows/sidecar-roller-flank-knuckle-3r.json, model docs/concepts/models/sidecar-roller-flank-knuckle-3r.py):
   frozen exact Bench(110,360) 20.08 (score 92.70), near-touch 1 mm 21.17, complexity 45.25, 3 active (K slaved); converged
   (3043-try P1 lineage, gate 0.17/0.17/0.03); P1d fast 11.25 wears to 20.48", lead: "sidecar-longdyad-knuckle-3r VERIFIED 18.91
   (score 93.12), held out 22.67", branch, trailer}})`.
3. Write "## Round 8 results" in ROUNDS.md (and the FINDINGS entry) as a closer would: the verified table above, the
   lessons (section 3 bullets), the winner and the next focus.
4. Round 8's winner by the rule (best VERIFIED gap, ties by fewer passive translations, then complexity) is
   **sidecar-longdyad-knuckle-3r 18.91** unless the roller-flank verifier confirms below it, or the alignment auditor
   flags it (a flagged claim cannot win; read `docs/ALIGNMENT.md`).
5. Start the loop at round 9: `Workflow({scriptPath: "<repo>/tools/workflows/discovery-loop.js", args: {first_round: 9,
   n_rounds: 4, track: "main", focus, branch, trailer}})`. Use the closer's next focus if one was written; otherwise this
   draft (written from round 7 "Next", the round-8 numbers and section 9):

   > Round 9 (track main). Leads: sidecar-longdyad-knuckle-3r VERIFIED 18.91 (score 93.12, held out 22.67, complexity 49,
   > 3 active, K slaved by a strap-level RSSR sidecar); sidecar-parallelogram 19.13 verified but its 2 mm near-touch is
   > 50.14 against 34.03; 4-active minarc pick1 18.40. Round 8 bought in-band only (0.855 -> 0.897, at the 0.90 edge);
   > reach stayed 0.725, overhead 8/28, fold losses 86 of 360: the gap is reach at the J2 fold. Attack the fold geometry,
   > not K's law (worth <= 0.2 frozen): (a) the a2 wall - poses past th ~132 need a1e 76-100 at a2 62; (b) the J1 seat
   > toward the back of the shoulder, inside the allowed seats (back of the shoulder + acromion top only); (c) the knee
   > window for the overhead slide losses. Keep the sidecar drive at strap level. Target: frozen reach >= 0.775 and
   > overhead >= 14/28 at in-band14 >= 0.88, contact <= 0.01; report near-touch at 1 mm AND 2 mm. Rules: O20 hubs only,
   > fold margin 5 deg on th, stops on a joint's own angle, continuity flood fill, near-touch search objective. Dead
   > directions: HANDOFF section 5 - do not screen them again.
6. On a 4-core box a workflow runs 2 agents at once. Never SendMessage a running workflow agent: it starts a second copy
   (`tools/workflows/README.md`).

**Round 8's winner: polish, then gen-6 CAD** (CLAUDE.md "Every generation ends in a full CAD"):
- `templates/final-polish.js` args: `{id: "sidecar-longdyad-knuckle-3r", winner: "<one paragraph: the verified config in
  docs/concepts/rows/sidecar-longdyad-knuckle-3r.json, model docs/concepts/models/sidecar-longdyad-knuckle-3r.py, claim
  harness = the row's frozen protocol, judge harness docs/concepts/verify/sidecar-longdyad-knuckle-3r.py, verified 18.91
  (score 93.12), near-touch 20.00 / 34.03, held out 22.67, continuity full 18.91 / knn 21.72>", budget_usd: 2, branch, trailer}`.
- `templates/generation-winner-cad.js` args: `{gen: 6, id: "sidecar-longdyad-knuckle-3r", winner: <the same paragraph, or
  the polished config if its verifier confirmed a held-out gain >= 1>, short: "sidecar", slug: "sidecar-longdyad",
  prior_art: "gen-5 geneva rod: pipeline/conformal/param_cad/user_style_geneva.py, pipeline/concept_l1/build_geneva_l1.py,
  designs l1_geneva-rod / user_geneva_rod (read-only)", new_mechanism: "the strap-level RSSR sidecar drive slaving K to J2",
  do_not_edit: <files other running workflows edit>, spend_usd: 0.6, date: "<YYYY-MM-DD>", branch, trailer}`.
- Check its 2 mm near-touch against the lead's before any CAD swap.

**Gen-5 CAD of geneva-tail-knuckle-pinknee-3r (rod).** `l1_geneva-rod` is built and judged (7/19). `user_geneva_rod` was
rebuilt at 20:23 UTC from builder commit c23fedb; it has no judge yet.
1. Check that `pipeline/full-exo/designs/user_geneva_rod/build.json` is newer than the builder's last commit
   (`git log -1 --format=%ci -- pipeline/conformal/param_cad/user_style_geneva.py`); if not, rebuild with the builder.
2. `python3 tools/cloud_run.py judge user_geneva_rod`.
3. Stills on the muscled mannequin (exo-blender-cycles, workersMax 1, ~$0.05 a set).
4. An EVOLUTION.md entry with `tools/evolution_snapshot.py`, and an independent check (the verifier stage of
   `templates/generation-winner-cad.js`).

**The alignment auditor.** The user, 2026-10-16 ~20:10 UTC (verbatim): "at the same time as all the research is
happening, please require an agent on the side that is a superfan that targets misalgnment. It should understand the
goal of the project, to make a super low profile and free range shoulder joint, and see if models are cheating the
system or gaming the system in some way to scro ehigher witout actually being beter. This coudl be done in many ways,
but it needs to be a crucial aprt of our loop". If `tools/workflows/alignment-audit.js` and a CLAUDE.md rule exist, the
auditor finished its wiring: run that workflow hourly (a session cron, like the watchdog) and before any claim is called
a round's winner. If they do not, the auditor was cut short: commit its files (`docs/ALIGNMENT.md`,
`tools/alignment_audit.py`, `tools/alignment_wear_probe.py`, `docs/alignment/`), then launch a workflow that finishes
the wiring (an audit phase in `discovery-loop.js` so a flagged claim cannot win, a standalone `alignment-audit.js`, the
CLAUDE.md rule) and a skeptic review of the auditor.
Wiring DONE (2026-10-16 ~20:50 UTC; CLAUDE.md "Alignment auditor"): every claim, verification, new leader and judge /
metric change gets an audit (`tools/workflows/alignment-audit.js`: an auditor per design runs `tools/alignment_audit.py`
plus the docs/ALIGNMENT.md judgement pass, then a skeptic tries to refute every gamed / watch verdict); verdicts live in
the append-only ledger `docs/alignment/ledger.jsonl` (`python3 tools/alignment_ledger.py latest`; `get <id>` exits 3
when gamed; `due` lists what needs an audit). A design the ledger marks 'gamed' cannot be called verified, a winner or a
leader until the finding is resolved; the auditor's own claims get a skeptic. The repo `discovery-loop.js` runs it in an
Audit phase between Screen and Close, and its closer may not name a gamed winner. The loop copy already running from
the old session's scratchpad has NO Audit phase: run `alignment-audit.js` on its round's screened / verified designs
before naming that round's winner, and relaunch later rounds from the repo copy. The ledger was seeded with the tool's
19 verdicts (stage 'audit', skeptic pending: gamed = sidecar-parallelogram, sidecar-roller-flank, k-rim-lobe-stub,
seed-offset-3r-slides): run the workflow on the leaders first (minarc, sidecar-longdyad, sidecar-parallelogram).
The dashboard's morphs dataset carries `alignment` (+ `_stage`, `_reasons`, `_t`, `_claim`, `_stale`) per design; the
page does not show it yet.

**Watchdog, dashboards, compute.**
- Watchdog: a session cron every 15 min (prompt in `docs/OPERATIONS.md` section 3), plus the hourly alignment audit.
- Production dashboard: https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r, a Dashboard-type artifact whose datasets
  live in its store. Public mirror: https://claude.ai/artifact/5dan8agUow4XR81Pr91XhF. Both are rebuilt with
  `tools/dash_refresh.sh`; the publish procedure is in `docs/OPERATIONS.md` section 4. A new session reads each dataset's
  version first and seeds the state. The old session published with its own state file (a scratchpad copy of
  `.state/dash_pub/state.json`); the `if_version` pins catch any drift as a conflict: re-read the doc and redo the write.
- The CPU farm is RunPod endpoint `exo-cpu1` via `tools/cloud_run.py` (`docs/CLOUD_RUN.md`). Key: OPERATIONS section 5
  (never print it). The user's `exo-blender-cycles` is for stills only; never touch pods named `crl-*`; `workersMin`
  back to 0 after any search. Balance at 20:24 UTC: **$36.61**, spend $0.66/h (`tools/runpod_guard.py audit`; it
  changes, read it, never this line). `python3 tools/cloud_run.py ping` answered at 20:25 UTC (py 3.12, 8 vCPU).

## 9. Next steps, in priority order

1. **Take the verified sidecar-longdyad (18.91, 3 active) forward.**
   - Verify roller-flank (20.08; parallelogram 19.13 is verified) and close round 8 (section 8).
   - Give the round's winner its final polish (env bench, claim held out).
   - Then the gen-6 CAD: L1, L2, stills and EVOLUTION. Check its 2 mm near-touch against the lead's before any CAD
     swap.
   - With pick1 only 0.51 ahead, a polished 3-active design can lead outright. Report that to the user as a big
     update.
2. **Buy reach, the other half of 95.**
   - Round 9 should attack the fold geometry, not K's law.
   - The levers left:
     - the a2 wall: the stretched poses past th ~132 need a1e 76-100 at a2 62;
     - the J1 seat toward the back of the shoulder, inside the user's allowed seats;
     - the knee window for the overhead slide losses.
   - Target: frozen reach >= 0.775 and overhead >= 14/28 at in-band >= 0.88, contact <= 0.01 (ROUNDS.md round 7 "Next").
3. **Finish gen-5** (`user_geneva_rod`): judges, stills, EVOLUTION, independent check. Also fix the dynamics judge so it
   models the slaved K (lobe-rod coupling); R17 on `l1_geneva-rod` is a judge gap.
4. **pick1's K posture margin.** Plan K on the spring's trajectory and re-judge R17 and proximity, unless the user
   accepts upright-only (section 7).
5. **Complexity.**
   - The 3-active knuckle class sits at 42.5-49 and the golden target needs ~0.
   - Once a verified 3-active design reaches score >= 95, switch the objective to minimum complexity at score >= 95
     (CLAUDE.md).
   - Cheap wins wait on the user (the cuff IMU).
6. **Requirements no build has touched:**
   - R9 FEA (`judge/fea.py`, CalculiX, wired into judge_all.sh but skipped on recent builds);
   - R10 base slip (15.2 mm against 4; a passive fix is unknown);
   - R2 on the user's body;
   - R12-R15.

## 10. Infrastructure facts that still hold

- **Python deps:** `bash tools/setup.sh`, then `python3 -m pip install libigl`.
- **The bench cache** (`.cache/`) is git-ignored, so a new machine rebuilds it:
  - locally: `nice python3 tools/concept_bench.py --build 60 160 --jobs 2` (~20 min on an idle 4-core box; 2 jobs = the
    local process cap);
  - on the farm: `tools/bench_cache_farm.py` for Bench(110,360).
  - Then `python3 tools/concept_baseline.py --n-clip 60 --n-ws 160` should reproduce ~68.9.
- **Local limits:** keep local jobs niced and at <= 4 workers on the user's laptop. Here the lead kept itself to 2
  processes.
- **Farm facts:**
  - flash CPU serverless runs in EU-RO-1 only, with the content-addressed volume `exo-farm-cas`;
  - the worker image is Python 3.12 (`flash deploy --python-version 3.12`);
  - cadquery-ocp 7.7.2 is installed at runtime;
  - a stuck endpoint (unhealthy workers, queue not moving) is retired at once.
- **Agents:** an interrupt of the lead stops its background agents, so check what still runs after one. Commit only
  your own files: `git commit -- <paths>`.

## History

The previous handoff (2026-10-15 ~16:00 UTC) covered the morphology swarm and the 3R final
(`cad_r18_n3_s1392_1_f300`). Its state is in git (`git log -- docs/HANDOFF.md`), and its workflow copies are in
`docs/handoff/`. The design-by-design story is in `docs/EVOLUTION.md`, and the round-by-round story in
`docs/concepts/ROUNDS.md`. Earlier history is in the archive at github.com/aboufama/exo-arm.
