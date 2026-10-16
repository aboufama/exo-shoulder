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

1. **Read**: CLAUDE.md -> HANDOFF.md -> this page -> METHOD.md -> README.md -> REQUIREMENTS.md -> PLAN.md -> FINDINGS.md
   (newest sections) -> `docs/concepts/ROUNDS.md` (the last "Round N plan" / "Round N results").
2. **Git**: `git status --short; git pull --rebase --autostash; git log --oneline -15` (agents commit all the time;
   the log is the activity feed). Work on the branch HANDOFF names; push to it.
3. **Machine**: `nproc; uptime`. A workflow runs min(16, nproc - 2) agents at once (2 on a 4-core box). Local CPU
   work: <= 2 niced processes (`nice -n 10`, `OMP_NUM_THREADS=1`); the user's laptop overheats above 4 workers.
4. **Python / node**: `python3 -c "import igl, numpy, scipy, trimesh, cadquery; print('ok')"` (else `bash tools/setup.sh`);
   `node --version` (motion previews `docs/concepts/viz/`, dashboard thumbs). Fast bench cache:
   `ls .cache/concept_bench/` - if empty, `nice python3 tools/concept_bench.py --build 60 160 --jobs 2` (Bench(60,160);
   the farm has its own copy linked into every job). Without it the bench silently runs the slow EXACT path (it warns).
5. **RunPod**: `test -s ~/.runpod_key && RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/runpod_guard.py audit`
   (balance, spend/h, every endpoint's workersMin = 0, queues; never print the key). Then
   `RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py ping` (the farm answers).
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

- **Discovery loop (always on).** Find the last round in `docs/concepts/ROUNDS.md`:
  - last round has "Round N results" -> `first_round: N+1`, `focus` = that results section's lessons / what to attack
    next (verbatim, with its numbers), plus HANDOFF's "Next steps" item for discovery;
  - last round has only "Round N plan" (interrupted) -> `first_round: N`, `focus` = "Round N was interrupted at the
    handoff: its plan is in ROUNDS.md; rows <ids> are screened / verified, <ids> are not - screen only what is missing,
    then close the round".
  - `Workflow({scriptPath: "<repo>/tools/workflows/discovery-loop.js", args: {first_round, n_rounds: 4, track: "main",
    focus, branch, trailer}})`. When it ends, start the next one at once (the user: "dont just stop ... go as far as you can").
- **Each round's winner** (best VERIFIED, ties: fewer passive translations, then lower complexity): `templates/final-polish.js`,
  then `templates/generation-winner-cad.js` (L1 -> full user-style CAD -> stills -> verifier) and an EVOLUTION.md entry.
  Spend for stills: exo-blender-cycles, ~$0.05 a set.
- **A claim made outside the loop** -> `templates/verify-claim.js`. **A built design failing a requirement** ->
  `templates/redteam-fix.js`. **A design brief for the user's outside CAD tool** -> `templates/cad-context.js`.
- Run several workflows side by side (each has its own 2-agent cap); never SendMessage a running workflow agent (it forks a
  second copy - steer through repo files or stop + relaunch with resume).

## 3. The watchdog (a session cron, re-create it every session)

`CronCreate({cron: "7,22,37,52 * * * *", recurring: true, prompt: <below>})`. Cron jobs are session-only and expire
after 7 days; re-create then. The prompt:

```
WATCHDOG (exo-shoulder, every 15 min; docs/OPERATIONS.md):
1) Check the running workflows (python3 tools/agent_tail.py; agents silent > 45 min are suspect), CPU load (uptime) and
   RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/runpod_guard.py audit (a stuck queue or unhealthy workers -> retire
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

| | production | public mirror |
|---|---|---|
| URL | https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r | https://claude.ai/artifact/5dan8agUow4XR81Pr91XhF |
| kind | Dashboard-type artifact: page + datasets live in its store | plain page + data files (anyone with the link, no sign-in) |
| page source | `docs/dashboard/simple/index.html` = store doc `files/index.html` `{text}` | `docs/dashboard/public/index.html` (`tools/dash_public.py` wraps the same page) |
| data | store docs `datasets/<id>` pointing at uploaded assets | `data/<id>.json` files published beside the page |

- Build: `tools/dash_refresh.sh` (runs `tools/dash_build.py`, ~45 s, writes `docs/dashboard/data/*.json` + `manifest.json`,
  prints CHANGED / PAGE / PUBLIC lines). The page reads six datasets: morphs, sweeps, events, reqs, cad, motion. Details of
  each: [`DASHBOARD.md`](DASHBOARD.md) and the `tools/dash_build.py` docstring.
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
- **Key**: only as `RUNPOD_API_KEY="$(cat ~/.runpod_key)"` (the env var in some containers is a stale placeholder);
  never print or commit it.
- **Rules (CLAUDE.md "Paid compute")**: spend is approved without a fixed cap for this push, but state the worker type
  and cost per batch, keep the cheapest worker type that works, set `workersMin` back to 0 after a search, keep small
  jobs local. `exo-blender-cycles` is the user's render endpoint: stills only, never change its settings. Never touch
  pods named `crl-*`. Check the balance in the audit before big batches (it was ~$3-7 on 2026-10-16; when it runs low,
  tell the user - that is a blocker).
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
