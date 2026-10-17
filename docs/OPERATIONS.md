# Operations runbook (for a new lead session with no context)

The project state and the next steps are in [`HANDOFF.md`](HANDOFF.md); the rules in [`../CLAUDE.md`](../CLAUDE.md); the
working method in [`METHOD.md`](METHOD.md), from Felix Rieseberg's essay
[How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)
(altitude, depth, range, outside judges, never idle). This page is HOW to run the machinery: what to check when you
start, how to restart what was running, the watchdog, the dashboards, the farm, git, and what to tell the user.

**What does not survive a session** (and how you get it back): running workflows and agents (relaunch: section 2);
the 15-min watchdog cron (re-create: section 3); the dashboards' published versions (`.state/`, git-ignored: re-seed,
section 4); the fast bench caches in `.cache/` (rebuild, section 1); the RunPod key `~/.runpod_key` (the user's -
ask if missing). Everything else - rules, numbers, models, rows, findings, the user's rulings - is in the repo.

## 1. Start-of-session checklist (15 min, in this order)

1. **Read** (the one order, also in HANDOFF and CLAUDE.md "Where things stand": CLAUDE.md's line-3 list with HANDOFF and
   this page inserted after METHOD): CLAUDE.md -> METHOD.md -> HANDOFF.md -> this page -> README.md -> REQUIREMENTS.md
   -> PLAN.md -> FINDINGS.md (newest sections) -> `docs/concepts/ROUNDS.md` (the last "Round N plan" / "Round N
   results") -> `docs/ALIGNMENT.md` if present. CAD_STANDARD.md before touching a part, PIPELINE.md before running.
2. **Git**: the work lives on branch `claude/trusting-pasteur-6czobp` (HANDOFF "Branch"); `main` is ~935 commits behind.
   If your environment assigned you another branch: `git fetch origin claude/trusting-pasteur-6czobp && git merge
   FETCH_HEAD`, then work on and push to YOUR branch (the environment's branch wins) and update HANDOFF "Branch". Then
   `git status --short; git pull --rebase --autostash; git log --format='%h %ci %s' -15` (agents commit all the time;
   the log is the activity feed, and its commit times are the clock: time stamps agents write inside files ran up to
   ~20 min ahead on 2026-10-16).
3. **Machine**: `nproc; uptime`. A workflow runs min(16, nproc - 2) agents at once (2 on a 4-core box). Local CPU
   work: <= 2 niced processes (`nice -n 10`, `OMP_NUM_THREADS=1`); the user's laptop overheats above 4 workers.
4. **Python / node**: `python3 -c "import igl, numpy, scipy, trimesh, cadquery; print('ok')"` (else `bash tools/setup.sh`);
   `node --version` (motion previews `docs/concepts/viz/`, dashboard thumbs). Fast bench cache:
   `ls .cache/concept_bench/` - if empty, `nice python3 tools/concept_bench.py --build 60 160 --jobs 2` (Bench(60,160);
   the farm has its own copy linked into every job). Without it the bench silently runs the slow EXACT path (it warns).
5. **RunPod** (the key one-liner, used everywhere below - the file if present, else the environment variable):
   `K="$(cat ~/.runpod_key 2>/dev/null)"; RUNPOD_API_KEY="${K:-$RUNPOD_API_KEY}" python3 tools/runpod_guard.py audit`
   (balance, spend/h, every endpoint's workersMin = 0, queues; never print the key; neither set -> ask the user, a
   blocker). Then the same prefix with `python3 tools/cloud_run.py ping` (one ~3 s job, ~$0.001: the farm answers).
6. **What happened last**: `tail -80 docs/concepts/ROUNDS.md`; `tail -20 docs/concepts/events.jsonl`; rows still being
   worked on: `grep -l '"status": "modelling"' docs/concepts/rows/*.json`; HANDOFF "What was running".
   On the SAME machine as the old session, `python3 tools/agent_tail.py` lists the last workflow runs and
   `python3 tools/agent_tail.py <runId> 6` shows what each agent was doing.
7. **Dashboards**: open both (section 4), re-seed the publish state, refresh.
8. **Start work before you finish reading the details**: relaunch the discovery loop and whatever HANDOFF lists as
   running (section 2), then create the watchdog (section 3). Never idle (CLAUDE.md "Working method").

## 2. Workflows: what runs and how to (re)start it

Scripts, args and launch syntax: [`../tools/workflows/README.md`](../tools/workflows/README.md). Check before launching:
`node tools/workflows/check.mjs --dry`. Session settings every script takes: `repo`, `branch`, `trailer` (the two commit
attribution lines from your environment's system reminder) - pass yours.

- **Discovery loop (always on).** Find the last round in `docs/concepts/ROUNDS.md`. ONE rule:
  - last round has "Round N results" -> `first_round: N+1`, `focus` = that results section's lessons / what to attack
    next (verbatim, with its numbers), plus HANDOFF's "Next steps" item for discovery;
  - last round has only "Round N plan" (interrupted) -> finish it by hand, never re-plan it: (1) every round-N row with
    `status: screened` and no `v_gap` gets `templates/verify-claim.js` (unless git shows its verifier still running:
    an untracked `docs/concepts/verify/<id>.py` on the same machine); a planned design with no row at all gets a
    standalone `exo-screen.js` slice; (2) write "Round N results" + the FINDINGS entry as the closer would (verified
    table, lessons, winner, next focus); (3) then `first_round: N+1` as above. (Relaunching the loop at N would make
    its planner write a second "Round N plan" over the first.) HANDOFF section 8 applies this to round 8 and carries a
    draft round-9 focus.
  - `Workflow({scriptPath: "<repo>/tools/workflows/discovery-loop.js", args: {first_round, n_rounds: 4, track: "main",
    focus, branch, trailer}})` - `branch` and `trailer` are REQUIRED (every script stops without them, so no agent
    commits under an old session). When it ends, start the next one at once (the user: "dont just stop ... go as far as
    you can").
- **Each round's winner** (best VERIFIED, ties: fewer passive translations, then lower complexity): `templates/final-polish.js`,
  then `templates/generation-winner-cad.js` (L1 -> full user-style CAD -> stills -> verifier) and an EVOLUTION.md entry.
  Spend for stills: exo-blender-cycles, ~$0.05 a set.
- **Alignment audit** (CLAUDE.md "Alignment auditor"): `Workflow({scriptPath: "<repo>/tools/workflows/alignment-audit.js",
  args: {targets: ["<id>", ...], context: "<why>", ref: "<verified lead id>", branch, trailer}})` after every claim,
  every verification, every new leader, every judge / metric / bench / kit change (`targets: []`, `since` = the change's
  commit time) and before a generation-winner CAD or a polish swap. The loop runs it itself (Audit phase). Verdicts:
  `python3 tools/alignment_ledger.py latest` (`get <id>` exits 3 when gamed). A design the ledger marks 'gamed' cannot be
  called verified, a winner or a leader until the finding is resolved; the auditor's own claims get a skeptic.
- **A claim made outside the loop** -> `templates/verify-claim.js`. **A built design failing a requirement** ->
  `templates/redteam-fix.js`. **A design brief for the user's outside CAD tool** -> `templates/cad-context.js`.
- Run several workflows side by side (each has its own 2-agent cap); never SendMessage a running workflow agent (it forks a
  second copy - steer through repo files or stop + relaunch with resume).

## 3. The watchdog (a session cron, re-create it every session)

`CronCreate({cron: "7,22,37,52 * * * *", recurring: true, prompt: <below>})`. Cron jobs are session-only, fire only
while the session is idle (a long turn delays them; they can run up to half a period late) and expire after 7 days;
re-create then. Also re-create the hourly alignment audit: `CronCreate({cron: "41 * * * *", recurring: true, prompt:
"ALIGNMENT AUDIT (hourly, docs/OPERATIONS.md section 2): python3 tools/alignment_ledger.py due --since <one hour ago,
ISO UTC>; if anything is due, launch tools/workflows/alignment-audit.js with targets [], since = that time, context
'hourly', branch, trailer; a new 'gamed' final verdict on a verified or leading design goes to the dashboard and the
lead (the user only if it changes the leader)"})`. The watchdog prompt:

```
WATCHDOG (exo-shoulder, every 15 min; docs/OPERATIONS.md):
1) Check the running workflows (python3 tools/agent_tail.py; agents silent > 45 min are suspect), CPU load (uptime) and
   K="$(cat ~/.runpod_key 2>/dev/null)"; RUNPOD_API_KEY="${K:-$RUNPOD_API_KEY}" python3 tools/runpod_guard.py audit
   (a stuck queue or unhealthy workers -> retire
   the endpoint, workersMin back to 0, move the jobs). Act on anything stuck or failed. If the discovery loop ended,
   relaunch it from the next round (docs/OPERATIONS.md section 2); if a round has a verified winner without its
   final polish / generation CAD, launch them.
2) Do NOT backfill agent slots by reflex (user 2026-10-15: "you don't necessarily need a ton of agents ... use agents
   effectively"): launch new agent work only when your own analysis says it is the highest-leverage next step.
3) Dashboards: tools/dash_refresh.sh. For each "CHANGED <id> ... v<V>": Artifact publish {url: production, asset: true,
   file_path: docs/dashboard/data/<id>.json} -> "/_blob/<hash>"; ArtifactData update collection "datasets", doc_id <id>,
   data {source: {kind: "file", url: "/_blob/<hash>", name: "<id>.json"}, updated: {at: <ISO now>, by: "Claude"}},
   if_version V; then tools/dash_refresh.sh mark <id> <new version>. "PAGE changed": tools/dash_refresh.sh page-json,
   ArtifactData update collection "files", doc_id "index.html", file_path <that json>, if_version; mark-page <new version>.
   "PUBLIC CHANGED": republish the public mirror with the printed files map; tools/dash_refresh.sh mark-public.
4) Git: commit + push the dashboard data and the WIP outputs of running agents by explicit path (docs/OPERATIONS.md
   section 6); nothing over 50 MB, no caches / keys / personal data.
5) Message the user only for big updates: a new VERIFIED leader, a verified score >= 95 (gap <= 13.75), a requirement
   newly passing on a built CAD, a blocker that needs them, a generation-winner render ready.
```

## 4. Dashboards (two artifacts, one dataset build)

**2026-10-17: the session now runs under the user's second account, which cannot write to the two artifacts below
(they belong to the first account's org).** The live dashboard for this account is
https://claude.ai/artifact/DjCGir1xvu6es36Lx1nwRA - the public-mirror page (`docs/dashboard/public/index.html` + its
`data/*.json` files map from the PUBLIC line), republished by the same `file_path` from this session (a new session
passes `url` after an `Artifact read`). Its headline is the best verified design with <= 3 active joints (user ruling
2026-10-17: a sensed joint is a joint). A row whose JSON carries `leader_ruling: "tie: <leader id> | why"` (or `"no lead: ..."`)
- the lead's ruling after a leader-change audit - keeps its board place at its verified number, shows "Verified (tie)"
with the ruling on hover, and does not take the headline (the headline names the tie instead). First use: inband-rssr pick3
(2026-10-17, audit 48be5d5).

| | production | public mirror |
|---|---|---|
| URL | https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r | https://claude.ai/artifact/5dan8agUow4XR81Pr91XhF |
| kind | Dashboard-type artifact: page + datasets live in its store | plain page + data files (anyone with the link, no sign-in) |
| page source | `docs/dashboard/simple/index.html` = store doc `files/index.html` `{text}` | `docs/dashboard/public/index.html` (`tools/dash_public.py` wraps the same page) |
| data | store docs `datasets/<id>` pointing at uploaded assets | `data/<id>.json` files published beside the page |

- Build: `tools/dash_refresh.sh` (runs `tools/dash_build.py`, ~45 s, writes `docs/dashboard/data/*.json` + `manifest.json`,
  prints CHANGED / PAGE / PUBLIC lines). The page reads six datasets: morphs, sweeps, events, reqs, cad, motion. Details of
  each: [`DASHBOARD.md`](DASHBOARD.md) and the `tools/dash_build.py` docstring. Its summary lines mean: "fast-sweep
  record" = the best gap any agent LOGGED on a FAST-bench sweep (6.19 on 2026-10-16), not a verified claim - verified
  numbers are the rows' `v_gap`; "WARN n sweep rows log their objective gap above the plain formula" is expected (every
  search logs its near-touch / continuity objective; the builder keeps the larger, ~27,450 rows) - only the "below it
  ... by > 0.2" count is agent error, and the lines it prints are the ones to look at.
- **8 MB per dataset**: the store refuses a bigger file. `dash_build.py` thins `sweeps` to 7.5 MB (`thin_fit`);
  `dash_refresh.sh` flags any dataset over 8 MB - do not publish it, thin it in the builder.
- **New session, first refresh**: `Artifact read` both URLs (a publish to an artifact this session has not read is
  refused); `ArtifactData list` url production, collection "datasets" and collection "files" -> each doc's `version`;
  `tools/dash_refresh.sh seed '{"morphs": V, "sweeps": V, "events": V, "reqs": V, "cad": V, "motion": V,
  "_files_index_html": V}'`. Every dataset then reports CHANGED once; publish them all (harmless). Every write is pinned
  with `if_version`; on a version conflict, re-read that doc and redo the write.
- Public mirror publish: `Artifact publish` with `url` = the mirror (a new session's first publish must pass the URL,
  after an `Artifact read`), `file_path: docs/dashboard/public/index.html`, `files` = the map in the PUBLIC line; then
  `tools/dash_refresh.sh mark-public`. Artifacts start private: the user shares them.

## 5. Compute: local box, CPU farm, RunPod rules

- **Local**: <= 2 niced processes from agents, never `pkill -f`, never kill a process you did not start.
- **CPU farm** = RunPod serverless endpoint `exo-cpu1` via `tools/cloud_run.py` ([`CLOUD_RUN.md`](CLOUD_RUN.md)): `sweep`,
  `judge <design> [fast]`, `run`, `batch`, `ping`. Identical numbers to local, ~15x faster. Use it when it saves >= 3x
  wall-clock; one job under a minute stays local. Rate $0.288/h per worker (8 vCPU), scale to 0, idle 10 s; quota 10
  workers across all endpoints (exo-cpu1 workersMax 9, exo-blender-cycles 1 while no film renders). Cost log:
  [`RUNPOD_COSTS.md`](RUNPOD_COSTS.md).
- **Key**: `K="$(cat ~/.runpod_key 2>/dev/null)"; RUNPOD_API_KEY="${K:-$RUNPOD_API_KEY}" <command>` - the file wins
  because in some containers the env var was a stale placeholder (on 2026-10-16 both held the same key); if the audit
  answers 401, try the other source, then ask the user. Never print or commit it.
- **Rules (CLAUDE.md "Paid compute")**: spend is approved without a fixed cap for this push, but state the worker type
  and cost per batch, keep the cheapest worker type that works, set `workersMin` back to 0 after a search, keep small
  jobs local. `exo-blender-cycles` is the user's render endpoint: stills only, never change its settings. Never touch
  pods named `crl-*`. Check the balance in the audit before big batches ($36.61 at 20:24 UTC 2026-10-16, spend
  $0.66/h; read the audit, not this line; when it runs low, tell the user - that is a blocker).
- **What the audit lists**: `exo-cpu1` (the farm), `exo-blender-cycles` (the user's, report only - its "idle worker /
  check idleTimeout" flag is reported, never acted on) and 16 GPU endpoints `exo-band8` ... `exo-band23`: the band
  evaluators of the 2026-10-15 GPU searches ([`RUNPOD_COSTS.md`](RUNPOD_COSTS.md),
  `pipeline/conformal/gpu_client/`), all at workersMin 0 / workersMax 0, so they cost nothing; leave them (delete only with the user's OK).
  The flag "exo-cpu1: workersMax=9 but only N job(s)" is advisory: keep 9 (the user's quota split: cpu1 9 + blender 1).
- **"RunPod for renders only"** in METHOD.md and CLAUDE.md "Compute" predates the CPU farm; the later CLAUDE.md "Paid
  compute" and FINAL POLISH rulings (2026-10-15 23:15, 2026-10-16: "the farm is the instrument") make the farm the
  search tool. Rules stay as written; read them in date order.
- **GPU**: only when it measurably beats the farm per dollar (CLAUDE.md "FINAL POLISH"); GPU pods must be terminated
  when done (`tools/gpu_pod.py`).

## 6. Git hygiene

- Commit only your own files: `git add <paths> && git commit -m "<msg>" -- <paths>`; message ends with your
  environment's attribution lines; push; on rejection `git pull --rebase --autostash` and push again (up to 4 tries).
  No model names in commit messages or files.
- **The stop hook** (`~/.claude/stop-hook-git-check.sh`) refuses to end a turn while the tree has uncommitted changes,
  untracked files or unpushed commits. Running agents always have half-finished files, so the lead commits them as
  "WIP outputs from running agents" by explicit path (`git status --short`, then `git add <their files>`), together
  with the dashboard refresh. Never `git add -A`; never commit `.cache/`, `.state/`, keys, `data/raw/private/` or
  anything from a `personal-shoulder-diagnosis` folder.
- **Big files**: GitHub warns at 50 MB and refuses 100 MB. Before committing: `find docs pipeline -size +45M`. Split a
  growing sweep log into archived parts `docs/concepts/sweeps/<id>@1.json`, `@2.json` (`dash_build.py` reads them as
  part of `<id>`); render videos stay small or go outside git.
- A file another workflow is writing: do not edit it; copy it and work on the copy.

## 7. Talking to the user

- Chat carries **big updates only** (CLAUDE.md ambition rule 6): a new verified leader, a requirement newly passing, a
  verified score >= 95, a blocker that needs them (money, a licence, a download, a ruling), a render ready. Everything
  else goes to the dashboard and the repo.
- Their rulings are binding and recorded in CLAUDE.md / REQUIREMENTS.md; open questions waiting on them are in
  HANDOFF.md. Ask before relaxing the 1 cm rule or the DOF cap, before downloads, before accepting a licence.
- Their words outrank everything, including this page.

## 8. Helpers

| tool | use |
|---|---|
| `tools/dash_refresh.sh` | dashboard build + what to publish; `mark`, `mark-page`, `mark-public`, `seed`, `page-json` |
| `tools/agent_tail.py` | list workflow runs / agents; tail an agent's transcript (same machine only) |
| `tools/workflows/check.mjs` | parse / dry-run workflow scripts before launch |
| `tools/runpod_guard.py audit / enforce` | RunPod endpoints, spend, balance; enforce workersMin 0 + idle |
| `tools/cloud_run.py` | the CPU farm |
| `tools/judge_all.sh <design> [fast]` | every outside judge on a built design (or `cloud_run.py judge`) |
| `tools/simplicity.py` | the complexity count (docs/SIMPLICITY.md) |
| `tools/evolution_snapshot.py` | the EVOLUTION.md snapshot of a judged design |

## 9. When a tool this page assumes is missing

The runbook was written in a session that had the Workflow tool, CronCreate and the Artifact / ArtifactData tools. A
new session may lack some of them; the work goes on without them.

- **No Workflow tool.** Each script in `tools/workflows/` is plain JavaScript: its `agent(...)` calls are the prompts,
  in order, with their output schemas. Run them yourself with whatever subagent tool you have (Agent / Task), one
  stage at a time, passing each stage's output into the next prompt as the script does; with no subagent tool, do the
  stages yourself in order. Keep the outside-judge rule: the verifier stage must be a different agent (or a fresh
  session) from the one that made the claim.
- **No CronCreate** (or the session will not be idle often enough for it to fire). Run the watchdog prompt by hand at
  the end of every turn that waits on agents, or use `send_later` (a one-shot message into this session, minute
  granularity) re-armed each time. The remote scheduled tasks (`create_trigger`) normally have an hourly minimum, so they
  suit the hourly alignment audit, not the 15-min watchdog; a scheduled task that starts a fresh session needs a
  complete standalone prompt (point it at this page).
- **No Artifact / ArtifactData tools.** Keep building the datasets (`tools/dash_refresh.sh`) and commit
  `docs/dashboard/data/` + `docs/dashboard/public/`; the public page runs locally beside a copy of the data (it fetches
  `data/<id>.json` next to itself): `D=$(mktemp -d); cp docs/dashboard/public/index.html "$D"/; cp -r docs/dashboard/data
  "$D"/data; (cd "$D" && python3 -m http.server 8000)`. Tell the user once that the hosted dashboards are frozen at
  their last publish until a session with those tools republishes them (section 4).
- **No RunPod key.** Everything runs locally, slower (<= 2 niced processes); the farm's speed-up is a blocker to report,
  not a reason to stop.
