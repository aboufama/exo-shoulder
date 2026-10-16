# Handoff: the state of the project (2026-10-16 ~20:15 UTC)

Written for a reader with no context: a new session, a new model, or a person. Every number below comes from a file in
this repo (rows, verifier outputs, scorecards, ROUNDS.md, FINDINGS.md, EVOLUTION.md); the file is named next to it.

## Start here

**What this is.** A shoulder exoskeleton for the user's right shoulder (they are 185 cm tall, 6'4" wingspan). The whole
mechanism must ride within about 1 cm of the skin over the full range of motion, overhead most of all, and never touch
it. It has at most 4 degrees of freedom, and the user wants exactly 3 if possible. MVP1 is unpowered: rolling bearings
track the arm and the user adds rotation sensing. The work is a loop: invent a mechanism, score it on a body-model
bench, have an outside verifier re-measure it, build CAD of the winner and judge it against 19 requirements.

**Read in this order.**
1. `CLAUDE.md`: the user's goal, decisions and hard rules. They are binding, and the user's words outrank everything.
2. This file: where things stand.
3. `docs/OPERATIONS.md`: how to run the machinery (workflows, farm, watchdog, dashboards, git).
4. `docs/METHOD.md`: how we work.
5. `README.md`, then `REQUIREMENTS.md`: the 19 numbered requirements (R1-R17 plus R1-aim and R5-aim) and their judges.
6. `docs/PLAN.md`: the phases and the field's instruments.
7. `docs/FINDINGS.md`: everything measured so far, newest at the bottom.
8. `docs/concepts/ROUNDS.md`: the discovery rounds, each with its plan, results, lessons and next focus.

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
| **minarc-stop-knuckle-4r pick1** (envp-F7-g35-6) | **18.40 (93.31)** | 21.31 env fit / 22.69 fit-60 | 4 (K spring-held, sensed) | 33 | verified final polish; it is the CAD config | rows/minarc-stop-knuckle-4r.json, docs/research/minarc_final_polish.md, picks/pick1_priced.json, verify/minarc-final-polish-verify.py |
| minarc-stop-knuckle-4r BDp | 19.54 (92.89) | 24.18 fit-60 / 23.68 env | 4 (K sensed) | 33 | verified; superseded by pick1 for CAD | same row, verify/minarc-bdp-judge.md, docs/research/minarc-bdp-verdict.md |
| **frontload-lobe-stopb-knuckle-3r** | **22.82 (91.70)** | 26.75 | **3** (K slaved by a rod drive, never read) | 49 | verified round-7 winner (a seat re-fit of the geneva rod, below the 1-point CAD-swap rule) | rows/, docs/concepts/frontload-lobe-stopb-knuckle-3r.md, verify/frontload-*_corr_*.json |
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
- The best design overall needs a 4th, sensed joint: minarc's knuckle K.
- The best 3-active design is the knuckle family with K slaved to J2 by a lobe, rocker and rod drive (22.82).
- The simplest designs top out at 31-34.
- Every leader loses mostly REACH to the J2 fold. In-band (~0.89) and follow (~1.0) are close to their targets.

## 3. Round 8, in flight at handoff (self-measured, NOT verified)

The round-8 plan is in ROUNDS.md, its picks in `docs/concepts/round8_ideation.md`, and the timeline in
`docs/concepts/events.jsonl`. The lever is the "sidecar": the K drive moved down to strap level, so its metal sits in
band.

| design | frozen exact (score) | near-touch 1 mm / 2 mm | held out | complexity | state |
|---|---|---|---|---|---|
| sidecar-longdyad-knuckle-3r | 18.91 (93.12) | 20.00 / 34.03 | 22.67 | 49 | independent verifier running (`docs/concepts/verify/sidecar-longdyad-knuckle-3r.py`, untracked at handoff) |
| sidecar-parallelogram-knuckle-3r | 19.13 (93.04) | 20.22 / 50.14 | 22.03 | 49 | screened, awaiting the verifier |
| sidecar-roller-flank-knuckle-3r | 20.08 (92.70) | 21.17 / - | - | 45.25 | screened, awaiting the verifier |
| twist-long-a2-knuckle-3r | 24.46 frozen (16.74 fast vs the lead's 15.57) | - | - | 49 | DEAD: the J3 twist walks back in every CMA stream |

For comparison, the verified lead is 22.82, with near-touch 24.46 / 44.08 and held out 26.75.

- **If verified,** the sidecar is the first 3-active design at the 4-active pick1's level: 3.9 points better than the
  lead, held out by ~4.
- **Its gain is in-band only** (0.855 -> ~0.90). Reach is unchanged at 0.72, with overhead 8/28, so the fold still sets
  the gap.
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
| `user_geneva_rod` | L2 | in progress | - | - | - | STEP parts built (`pipeline/conformal/param_cad/user_style_geneva.py`); judges, stills, EVOLUTION entry and the independent check not yet done |

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

1. **A sensed 4th joint (minarc pick1, score 93.3, 4 active) against 3 active joints** (best verified 22.82 / 91.7;
   the sidecar is ~93 self-measured). Does a sensed passive used only at static extremes count as passive? If yes,
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
workflow scripts and templates are in `tools/workflows/` (README there).

- **Discovery loop, rounds 6-9** (`tools/workflows/discovery-loop.js`, track main).
  - Round 8 was in verification of sidecar-longdyad-knuckle-3r, and its closer had not run.
  - **Relaunch:**
    1. Read the ROUNDS.md tail and the `docs/concepts/events.jsonl` tail.
    2. If round 8 has no "Round 8 results" section, first run an independent verifier on the three sidecar rows (the
       verifier template in `tools/workflows/`; a claim counts only once verified). Then write the round-8 results and
       lessons in ROUNDS.md and FINDINGS.md, as a closer would.
    3. Start the loop at the next round: `{first_round: 9, n_rounds: 4, track: "main", focus: "<the last round's next
       focus>"}`.
  - On a 4-core box a workflow runs 2 agents at once.
  - Never SendMessage a running workflow agent: it starts a second copy (`tools/workflows/README.md`).
- **Gen-5 CAD of geneva-tail-knuckle-pinknee-3r (rod).**
  - `l1_geneva-rod` is built and judged (7/19). `user_geneva_rod` has its STEP parts but no judge.
  - **Relaunch from the CAD stage:**
    1. Check `pipeline/full-exo/designs/user_geneva_rod/` and the builder `pipeline/conformal/param_cad/user_style_geneva.py`.
    2. Run `python3 tools/cloud_run.py judge user_geneva_rod`.
    3. Then the stills on the muscled mannequin (exo-blender-cycles, workersMax 1).
    4. Then an EVOLUTION.md entry with `tools/evolution_snapshot.py`, and an independent check (the generation-winner
       CAD template).
- **Watchdog**: a session cron every 15 min. The prompt is in `docs/OPERATIONS.md`. It checks workflows, CPU load and
  `tools/runpod_guard.py audit`, refreshes the dashboards and messages the user only for big updates.
- **Dashboards.**
  - Production: https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r, a Dashboard-type artifact whose datasets live in its
    store.
  - Public mirror: https://claude.ai/artifact/5dan8agUow4XR81Pr91XhF.
  - Both are rebuilt from `python3 tools/dash_build.py`. The upload procedure is in `docs/OPERATIONS.md` and
    `docs/DASHBOARD.md`. A new session reads each dataset's version first.
- **Compute.** The CPU farm is RunPod endpoint `exo-cpu1` via `tools/cloud_run.py` (`docs/CLOUD_RUN.md`), with the key
  in `RUNPOD_API_KEY` or `~/.runpod_key`; never print it.
  - The user's `exo-blender-cycles` endpoint is for stills only.
  - Never touch pods named `crl-*`.
  - Set `workersMin` back to 0 after any search.
  - The balance was low (~$3.5 shared) when the gen-5 CAD launched (~18:00 UTC); check it with the audit.

## 9. Next steps, in priority order

1. **Verify the round-8 sidecar family.** If sidecar-longdyad (18.91) or sidecar-parallelogram (19.13) holds:
   - it is the new 3-active leader;
   - it gets the final polish (env bench, claim held out), then the gen-6 CAD (L1 + L2 + stills + EVOLUTION);
   - check its 2 mm near-touch against the lead's before any CAD swap.
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
  - locally: `nice python3 tools/concept_bench.py --build 60 160 --jobs 3` (~15 min on an idle 4-core box);
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
