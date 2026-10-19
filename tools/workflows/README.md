# Workflow scripts (the swarm's machinery)

These are the scripts the lead session runs with the **Workflow tool** (multi-agent orchestration: `agent()`,
`parallel()`, `pipeline()`, `workflow()` for child workflows; see the workflow-authoring skill). The runbook for the
whole operation is [`docs/OPERATIONS.md`](../../docs/OPERATIONS.md).

| script | what it does | when to launch |
|---|---|---|
| `discovery-loop.js` | the self-driving discovery loop: per round a planner (state + 2-3 lenses), `discovery-ideate.js`, `exo-screen.js` slices of 2 designs, `alignment-audit.js` on each slice's screened / verified designs (Audit phase), a closer that writes `docs/concepts/ROUNDS.md` + FINDINGS and the next round's focus and may not name a winner the alignment ledger marks gamed | always running (CLAUDE.md "Discovery never stops at a round") |
| `alignment-audit.js` | the alignment auditor (CLAUDE.md "Alignment auditor", docs/ALIGNMENT.md): per design an auditor (`tools/alignment_audit.py` checks + the 25-pattern judgement pass -> `docs/alignment/<id>.md/.json`), then a skeptic that tries to refute every gamed / watch verdict; `tools/alignment_ledger.py` computes and records each verdict in `docs/alignment/ledger.jsonl` | after every claim, verification, new leader, judge / metric / bench change (`since`), before a CAD / polish swap; hourly with `targets: []` (the ledger's due list); launched by the loop |
| `discovery-ideate.js` | child: one agent per lens proposes 3 buildable morphologies; a judge red-teams and appends the top picks to `docs/concepts/catalogue.json` | launched by the loop |
| `exo-screen.js` | child: model + farm sweep to the convergence gate + red team + motion preview, then an independent verifier (or an auditor of a death) | launched by the loop; standalone for one catalogue entry |
| `templates/verify-claim.js` | two skeptic lenses (re-measure, buildability) + a judge that writes the verified numbers into the row | a claim made outside the loop (re-fit, embodiment change, Track work) |
| `templates/final-polish.js` | CMA on the representative envelope bench (`tools/env_bench.py`), claim held out, verifier only if held-out gain >= 1 | once per generation winner, before / beside its CAD |
| `templates/generation-winner-cad.js` | L1 keep-out CAD + judges (+ red team of any new mechanism), full user-style CAD, look-audited stills, verifier | after each round's winner is verified (CLAUDE.md "Every generation ends in a full CAD + render") |
| `templates/redteam-fix.js` | measure what a failing requirement costs, measure candidate fixes in the judge, re-judge, builder fixes; independent check (the pick1 K-hold pattern) | a judge or verifier flags a fixable failure on a built design |
| `templates/cad-context.js` | a self-contained brief of a verified design for an outside CAD tool (default: kinematics only, the user's latest preference) | only on the user's request |
| `check.mjs` | parse every script as the runtime does; `--dry` also runs it with stub agents (no spend) | before every launch after an edit |

Each script starts with a header comment: what it does, its args, when to launch it.

## How to launch

```
Workflow({ scriptPath: "/home/user/exo-shoulder/tools/workflows/discovery-loop.js",
           args: { first_round: 9, n_rounds: 4, track: "main", focus: "<the last closer's next focus, verbatim>",
                   branch: "<your session's branch>", trailer: "<attribution line 1>\n<attribution line 2>" } })
Workflow({ scriptPath: "/home/user/exo-shoulder/tools/workflows/alignment-audit.js",
           args: { targets: ["<row id>", ...], context: "<why: new claim / verification / leader / judge change>", ref: "<verified lead id>",
                   since: "<ISO time, optional>", branch: "<your session's branch>", trailer: "<attribution line 1>\n<attribution line 2>" } })
Workflow({ scriptPath: "/home/user/exo-shoulder/tools/workflows/templates/verify-claim.js",
           args: { id: "<row id>", claim: "<config, files, claimed numbers>", lead: "<verified leader + held out>",
                   branch: "<your session's branch>", trailer: "<attribution line 1>\n<attribution line 2>" } })
```

- `args` is a JSON object (not a JSON string). Every script takes the session settings `branch` and `trailer` (the
  two commit-attribution lines your environment's system reminder gives, joined by `\n`) - **both REQUIRED**: a script
  launched without them stops at once (`check.mjs --dry` tests this), so no agent commits under an old session's
  attribution. `repo` defaults to `/home/user/exo-shoulder`. The loop passes all three to its children.
- Which round to start, and what to do with an interrupted round: ONE rule, in `docs/OPERATIONS.md` section 2 (finish an
  interrupted round by hand - verify its screened rows, write its results - then start the loop at the next round;
  never relaunch the loop at the interrupted round, its planner would write a second plan).
- No Workflow tool in your session: `docs/OPERATIONS.md` section 9 (run the stages as the script lays them out).
- The loop finds its children through `wf_dir` (default `<repo>/tools/workflows`; it needs `alignment-audit.js` there too). A loop runs for hours; if you will
  `git pull` or edit these files meanwhile, copy the three scripts to your session scratchpad and pass `wf_dir` = that
  folder, so the running loop never sees a half-edited file.
- Before launching an edited script: `node tools/workflows/check.mjs --dry <file>`.
- Resume after a kill or an edit: `Workflow({ scriptPath, resumeFromRunId: "wf_..." })` - the unchanged prefix of
  agent calls returns cached results.
- No `Date.now()` / `Math.random()` / `new Date()` in scripts (they break resume): pass dates in `args`.
- Templates take the design-specific facts as text args (`winner`, `claim`, `context`, `task`): write them dense,
  numbers and file paths from the repo only - the agents read nothing else from you.

## Concurrency (measured)

A workflow runs at most min(16, CPUs - 2) agents at once, and child workflows share their parent's cap: **2 agents at
once on a 4-core box**, however many slices the loop starts. To run more at once, launch several workflows (each has
its own cap), e.g. the discovery loop plus a generation-winner CAD plus a verifier. Agents are mostly waiting on the CPU
farm (`tools/cloud_run.py`), so the local box is rarely the limit; keep local CPU work to <= 2 niced processes.

## Do not message a running workflow agent (measured 2026-10-16)

`SendMessage` to the agentId of an agent running inside a workflow does not reach that agent. It **resumes a second
copy** from the same transcript, as a separate background agent. Both copies then run the same plan on the same files:
they wait on the same farm batch, write the same model files and race each other on the GPU pods' override driver.
This happened twice (Track A of wf_b870688f-426 and the pin-knee GPU search wf_9bce650d-b9e). The fix was to stop the
workflow and keep the informed copy, or to split the duties between the two copies. Later messages to that agentId go
to the resumed copy only. To steer workflow agents, put the facts in the repo (row / FINDINGS / a note file the
prompt tells them to read), or stop the workflow and relaunch the stage with the new facts in its prompt (resume keeps
the finished agents cached). To watch an agent without touching it: `python3 tools/agent_tail.py <runId> [N]`.

## Provenance

The three loop scripts are the ones the 2026-10-16 lead ran (rounds 5-9), with the session's scratchpad paths replaced
by `args`. The templates are generalised from that session's runs: gen5-cad-geneva-rod and gen4-cad-minarc-bdp
(generation-winner-cad), verify-minarc-bdp (verify-claim), minarc-final-polish (final-polish), pick1-k-hold
(redteam-fix), cad-context-zc-frontier-3r (cad-context). Their results are in docs/FINDINGS.md, docs/EVOLUTION.md and
the rows.
