# Cold-start check: can a new lead continue from the repo alone? (2026-10-16, wall clock 20:16-20:40 UTC)

A test of the handoff. A new lead session with no context read only the repo: `CLAUDE.md`, `docs/HANDOFF.md`,
`docs/OPERATIONS.md`, `docs/METHOD.md`, `README.md` and `tools/workflows/README.md`, plus the files they name. It then
answered the questions a new lead must answer, dry-ran the restart, and listed every gap. The base was commit 6951138
(runbook) through b6bdda8. The runbook's content was not changed. The fixes proposed for it are in section 4.

**Verdict.** The repo alone is enough to restart. The rules, the numbers, the restart procedure, the watchdog prompt,
the dashboard procedure and the farm rules are all written down, and every script parses and dry-runs. Five
judgment calls remain (section 3C). The biggest risk is work in flight that the handoff does not list (section 3A).

## 1. Answers from the repo alone

**Goal** (CLAUDE.md).
- A right-shoulder exo with at most 4 DOF, pushed to exactly 3. The whole mechanism rides within ~1 cm of the skin
  over the full range of motion, overhead most of all, and never touches it. Pass at 14 mm, aim for 10.
- MVP1 is unpowered (bearings, the user adds rotation sensing).
- The base rides the user's scapula handler.
- The fit target is the user: 185 cm, 6'4" wingspan.

**Hard rules** (CLAUDE.md).
- Never relax the 1 cm rule or the DOF cap without asking.
- Only BOTTOM of the user's parts may change.
- Personal data stays in `data/raw/private/`.
- Paid compute: state the worker type and the cost per batch, scale to 0, and never touch `crl-*` pods.
- Joints must be manufacturable, each mapped to a real component, with at most 2 passive translations (0 preferred).
- No lofts. O20 hubs only. J1 seats at the back of the shoulder or on top of the acromion only.
- Fold margin 5 deg, read on `th`. Stops act on a joint's own angle.
- Continuity flood fill for any passive or redundant coordinate.
- Search on the near-touch gap; polish on the env bench and claim held out.
- Outside verifiers only, never self-grading. Every tested design gets its motion preview.
- Every generation ends in a final polish, then a full CAD and stills.
- Complexity is shown next to the score, never folded into it.
- Commit only your own files, by path.

**Verified leader** (HANDOFF section 2, README status):
- **Overall:** minarc-stop-knuckle-4r pick1, gap 18.40 (score 93.31), held out 21.31. It has 4 revolutes, K
  spring-held and sensed, complexity 33.
- **Best 3-active:** sidecar-longdyad-knuckle-3r, 18.91 (93.12), held out 22.67, complexity 49, verified 2026-10-16.
  K is slaved by a strap-level RSSR sidecar drive.
- **Golden target:** score >= 95 (gap <= 13.75) at complexity ~0. Nothing has reached it.
- **What limits every leader:** reach (the J2 fold).

**What was running and how to restart it** (HANDOFF section 8, OPERATIONS section 2):
- **Discovery loop**, `tools/workflows/discovery-loop.js`, round 8 open. ROUNDS.md has a "Round 8 plan" but no
  results. Restart:
  1. Verify the two `status: screened` sidecar rows (parallelogram 19.13, roller-flank 20.08) with
     `templates/verify-claim.js`.
  2. Write the round-8 results and lessons.
  3. Launch the loop with `{first_round: 9, n_rounds: 4, track: "main", focus, branch, trailer}`.
- **Gen-5 CAD** (`user_geneva_rod`): judge it (`python3 tools/cloud_run.py judge user_geneva_rod`), then stills,
  then the EVOLUTION entry, then the independent check.
- **The 15-min watchdog** and **both dashboards** (below).

**Next 3 steps** (HANDOFF section 9):
1. Close round 8: verify the other two sidecar rows, final-polish the winner, then gen-6 CAD (L1, L2, stills,
   EVOLUTION). Check its 2 mm near-touch before any CAD swap.
2. Round 9 attacks fold geometry, not K's law: the a2 wall, a J1 seat toward the back, the knee window. Target: frozen
   reach >= 0.775 and overhead >= 14/28 at in-band >= 0.88, contact <= 0.01.
3. Finish gen-5, and give the dynamics judge the lobe-rod coupling. R17 on `l1_geneva-rod` is a judge gap.

**Refreshing both dashboards** (OPERATIONS section 4).
1. `tools/dash_refresh.sh`.
2. On a new session, read the store first:
   - `ArtifactData list` on production, collections `datasets` and `files`;
   - then `tools/dash_refresh.sh seed '{...}'`.
3. For each CHANGED dataset:
   - upload it as an asset;
   - `ArtifactData update` with `datasets/<id>` and `if_version`;
   - `tools/dash_refresh.sh mark <id> <v>`.
4. The page: `page-json`, then `ArtifactData update files/index.html`, then `mark-page`.
5. The public mirror: `Artifact read`, then `Artifact publish` with the PUBLIC files map, then `mark-public`.

**Watchdog** (OPERATIONS section 3): `CronCreate({cron: "7,22,37,52 * * * *", recurring: true, prompt: <the runbook's
WATCHDOG prompt>})`. It is session-only and expires after 7 days.

**The CPU farm** (OPERATIONS section 5, `docs/CLOUD_RUN.md`):
- RunPod serverless `exo-cpu1`, driven by `tools/cloud_run.py` (`sweep`, `judge`, `run`, `batch`, `ping`).
- The key is passed only as `RUNPOD_API_KEY="$(cat ~/.runpod_key)"` and never printed.
- Use the farm when it saves >= 3x wall-clock. Set `workersMin` back to 0 after a search.
- What not to touch:
  - `exo-blender-cycles` is the user's: stills only, never change its settings;
  - pods named `crl-*`;
  - the 10-worker quota split (cpu1 9, blender 1).

**What to tell the user, and when** (CLAUDE.md rule 6, OPERATIONS section 7): big updates only.
- A new verified leader.
- A verified score >= 95.
- A requirement newly passing on a built CAD.
- A blocker that needs them: money, a licence, a download, a ruling.
- A render ready.

The open questions waiting on them are in HANDOFF section 7: sensed-4th vs 3 active, the R17 posture margin, the cuff
IMU, a fold margin below 5 deg, msub for a slaved K.

**Where the method comes from.** Felix Rieseberg, *How to be more ambitious: A tutorial for humans with models*,
https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/. It is linked from `CLAUDE.md`
(top and Ambition rules), `docs/METHOD.md`, `docs/HANDOFF.md`, `docs/OPERATIONS.md` and `README.md`.

## 2. Dry run of the restart

| check | result |
|---|---|
| `node --check` on the 3 loop scripts, `check.mjs` and the 5 templates | 9 / 9 ok |
| `node tools/workflows/check.mjs` (parse as the runtime does) | 8 / 8 parse ok |
| `node tools/workflows/check.mjs --dry` (stub agents, no spend) | 8 / 8 dry ok. The loop's dry run stops after the planner, because stub child workflows return `[]`. |
| `bash -n tools/dash_refresh.sh` | ok |
| one real run, with an empty `DASH_STATE_DIR` (a cold machine) | exit 0 in 42 s. Prints NOSTATE, then CHANGED for all 6 datasets (morphs 116 rows 0.22 MB, sweeps 27149 rows 6.87 MB, cad 351, reqs 19, events 547, motion 117 rows 1.81 MB; all < 8 MB), PAGE changed and PUBLIC CHANGED (7 files). All expected for a cold start. It rewrites the tracked `docs/dashboard/data/*.json` + `manifest.json`, as the watchdog does. |
| seed read: `ArtifactData list`, production, `datasets` and `files` | works. Versions at 20:20 UTC: morphs 79, sweeps 75, events 92, reqs 20, cad 32, motion 36, `files/index.html` 11 |
| `RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/runpod_guard.py audit` | exit 0. Balance $36.64, spend $0.368/h, limit $80. Every endpoint has workersMin 0. exo-cpu1 max 9 with 1 job in progress; exo-blender-cycles max 1 with 1 idle worker (flagged, report only). Volume exo-farm-cas 20 GB EU-RO-1. The env var and the key file hold the same key (compared by hash, never printed). |
| every path named in HANDOFF, OPERATIONS, `tools/workflows/README.md`, README and CLAUDE.md | all exist, except `picks/pick1_priced.json` (wrong prefix, section 3B) and `data/raw/private/` (git-ignored by design) |
| environment | nproc 4; node v22.22.0; `import igl, numpy, scipy, trimesh, cadquery` ok; `.cache/concept_bench/` present on this machine (a new machine rebuilds it); `tools/agent_tail.py` lists 12 runs; `~/.claude/stop-hook-git-check.sh` present |
| `CronCreate` signature against the runbook's call | matches (`cron`, `prompt`, `recurring`) |
| not exercised | writes: the dataset asset upload (`/_blob/<hash>`), the store updates and the public-mirror publish. Also `cloud_run.py ping` (it starts a paid worker, outside this check's scope) and an actual Workflow launch. |

## 3. Gaps

### A. Steps that depend on session-only state

1. **Live work the handoff does not list.** At 20:20 UTC, `tools/agent_tail.py` showed two runs that neither HANDOFF
   section 8 nor OPERATIONS mentions:
   - `wf_0729deda-636`, an "Audit" workflow with agents `audit:live` and `audit:catalogue+tool`, running;
   - `wf_a20bc382-f06`, extract / write / check, whose `check:numbers` agent was interrupted.

   HANDOFF names no workflow run IDs, so a new lead cannot map a run to its track except through `agent_tail.py`,
   which works on the same machine only.
2. **In-flight files outside git, or not yet committed.**
   - The verifier `docs/concepts/verify/sidecar-parallelogram-knuckle-3r.py` is untracked, so the parallelogram
     verification HANDOFF calls "awaiting the verifier" is probably already running.
   - The gen-5 CAD agent (`wf_14bb06ea-22e`, `cad:user-geneva`) waits on a build log in the old session's scratchpad.
     If that session dies, the build state is lost.
   - The builder was recommitted at 20:15 (c23fedb), so "STEP parts built" in HANDOFF may describe an older build.
   - A new lead should read `git status` and the exo-cpu1 queue before relaunching either, or it duplicates them.
3. **Script defaults carry the old session's settings.** The defaults are branch `claude/trusting-pasteur-6czobp` and
   a trailer with the old session's `Claude-Session` URL. A new lead that forgets to pass `trailer` commits under the
   old session's attribution. It is documented, but easy to miss.
4. **Harness tools with no fallback.** The runbook assumes the Workflow tool, `CronCreate` and the
   `Artifact` / `ArtifactData` tools exist.
   - `CronCreate` jobs fire only while the session is idle, and may run up to half a period late.
   - The remote scheduled-task tool this environment offers instead normally has an hourly minimum, so it cannot be a
     15-min watchdog.
   - Nothing says what to do without the Workflow tool, for example running the template prompts as single agents.
5. **Dashboard publish state** (`.state/`) is per machine. The cold-start path (NOSTATE, then seed) works, as tested
   above.

### B. Stale or contradictory statements

1. **Time stamps run ahead of the clock.**
   - HANDOFF's header says "~20:25 UTC", but its commit dbed7ec is 20:11:21.
   - events.jsonl has entries at 20:22:00 and 20:31:00, written by commits at 20:09:52 (63167c0) and 20:13:44
     (4f9ebd1).
   - The wall clock during this check read 20:16-20:20.
   - Any "silent for N min" judgment based on these stamps is wrong. Use git commit times.
2. **RunPod balance.** HANDOFF section 8 says "~$3.5 shared" and OPERATIONS section 5 says "~$3-7". The audit shows
   $36.64.
3. **A wrong path.** HANDOFF section 2 cites `picks/pick1_priced.json` and says such paths are under `docs/concepts/`.
   It is `docs/research/minarc_final_polish/picks/pick1_priced.json`.
4. **Two restart rules for an interrupted round.**
   - OPERATIONS section 2: relaunch at `first_round: N` with an "interrupted" focus, and let the loop finish.
   - HANDOFF section 8 and the `tools/workflows/README.md` example: verify the rows, close round 8 by hand, then
     `first_round: 9`.
   - This check followed HANDOFF, the more specific of the two.
5. **Read order.** CLAUDE.md line 3 says METHOD -> README -> REQUIREMENTS -> PLAN -> FINDINGS. CLAUDE.md "Where things
   stand", HANDOFF and OPERATIONS say CLAUDE -> HANDOFF -> OPERATIONS -> METHOD -> ...
6. **"The branch HANDOFF names"** (OPERATIONS section 1, item 2). HANDOFF names no branch; it appears only in the script
   defaults. It is also unstated whether the environment's assigned branch or that branch wins.
7. **Bench-cache build:** HANDOFF section 10 says `--jobs 3`, OPERATIONS section 1 says `--jobs 2`.
8. **The RunPod key.** README says to use `RUNPOD_API_KEY` from the environment. OPERATIONS says use only the file,
   because the env var can be a stale placeholder. Here the two match.
9. **METHOD.md line 20** says "RunPod for renders only", but the CPU farm is the main search instrument.
10. **README's layout table** says "R1-R15", but there are 19 requirements.
11. **The dashboard build log.**
    - It prints "record 6.19". That is the fast-bench sweep record, not a verified number (the verified best is
      18.40), and nothing says so.
    - It prints 27,471 warnings ("file gap != recomputed; file kept (the larger)") from 8 designs' sweep logs. Nothing
      says whether they are benign.
12. **Endpoints the docs never mention.**
    - The audit lists 16 GPU endpoints, `exo-band8`-`exo-band23`, all at workersMax 0. Neither HANDOFF nor OPERATIONS
      says whether to keep or delete them.
    - The audit's flag "exo-cpu1: workersMax=9 but only 1 job" is advisory. The runbook says to keep 9.

### C. What had to be guessed

1. What `wf_0729deda-636` and `wf_a20bc382-f06` produce, and whether a new lead should relaunch them.
2. Whether the parallelogram verifier is running (the untracked file says yes) or still has to be launched.
3. The round-9 `focus` text. No closer has written one, so it would be composed from HANDOFF section 9 item 2 and
   ROUNDS.md round 7 "Next".
4. The `winner` / `claim` arguments for the round-8 polish and CAD templates. They are written by hand from the row; the
   template headers list the fields.
5. Whether the untested write steps of the dashboard procedure work as written (section 2, "not exercised").

## 4. Proposed fixes, for the lead (not applied here)

- HANDOFF section 8:
  - add a table of live runs (run ID, track, stage, what a new lead does with it), including the audit and doc runs;
  - name the branch;
  - state that `git status` and the exo-cpu1 queue are checked before any relaunch.
- Stamp HANDOFF and events.jsonl from `date -u` at write time, not an estimate.
- Correct the balance in HANDOFF section 8 and OPERATIONS section 5, or point to the audit instead of a number.
- Fix the `pick1_priced.json` path.
- Make one restart rule for an interrupted round, and make CLAUDE.md line 3's read order match HANDOFF.
- Make `trailer` (and `branch`) required arguments in the workflow scripts, failing when missing, so a new session
  cannot commit under the old session's attribution.
- Add a fallback to OPERATIONS for an environment without CronCreate or the Workflow tool.
- Explain the dashboard build's "record" line and its warnings in `docs/DASHBOARD.md`.
- Say what the exo-band8-23 endpoints are (retired GPU search endpoints, keep at 0, or delete).

## Follow-up: how each gap was closed (same day, commit 253adac at 20:30 UTC)

| gap | fix |
|---|---|
| running work missing from HANDOFF, no run ids | HANDOFF section 8: a table of every run (id, track, state at 20:24, what a new lead does), the two session crons; `tools/agent_tail.py` now prints each run's script name (= its track) and marks agents silent 30+ min without a result as STALE? |
| in-flight work outside git (verifiers, gen-5 build) | parallelogram is verified (c7b5c53) and in the tables; roller-flank's running verifier is named; a rule: an untracked `verify/<id>.py` = still running; gen-5: check `build.json` against the builder's last commit |
| scripts default to the old branch / trailer | `branch` and `trailer` are REQUIRED in all 8 scripts; `check.mjs --dry` proves each refuses to start without them |
| no fallback for Workflow / CronCreate / Artifact tools | OPERATIONS section 9 (and the cron caveats in section 3) |
| forward-dated time stamps | HANDOFF "Clock" and OPERATIONS section 1: git commit times are the clock; HANDOFF's times are commit times |
| stale balance | $36.61 at 20:24 UTC from the audit, with "read the audit, not this line" |
| wrong pick1_priced path | fixed to `docs/research/minarc_final_polish/picks/pick1_priced.json` |
| two restart rules for an interrupted round | ONE rule in OPERATIONS section 2 (finish the round by hand, then N+1; never relaunch at N), pointed to from HANDOFF and tools/workflows/README |
| no branch named | HANDOFF "Branch", OPERATIONS section 1, README, CLAUDE.md pointer: `claude/trusting-pasteur-6czobp`; an environment-assigned branch wins after merging this one in |
| read orders differ | one order everywhere: CLAUDE -> METHOD -> HANDOFF -> OPERATIONS -> README -> REQUIREMENTS -> PLAN -> FINDINGS -> ROUNDS |
| --jobs 3 / 2, key source, METHOD "renders only", README R1-R15 | --jobs 2; one key one-liner (file, else env var); OPERATIONS section 5 notes the farm supersedes "renders only"; README says 19 requirements |
| dashboard "record 6.19" and 27,471 warnings unexplained | `tools/dash_refresh.sh` prints "fast-sweep record ... not a verified claim" and one WARN summary (objective gap above the plain formula = expected; only "below by > 0.2" lines are agent errors, printed) |
| 16 exo-band endpoints, the advisory cpu1 flag | OPERATIONS section 5 "What the audit lists" |
| round-9 focus and round-8 polish / CAD args had to be guessed | HANDOFF section 8: a draft round-9 focus and the args for verify-claim (roller-flank), final-polish and generation-winner-cad (gen 6) |
| `cloud_run.py ping` untested | ran at 20:25 UTC: ok (py 3.12, 8 vCPU, ~$0.001) |

Still untested from here: the dashboard write steps and a real Workflow launch from `tools/workflows/` (no Workflow or
ArtifactData tool in the checking agent).
