# Instructions for the agent working on this repo

Read first, in order: `docs/METHOD.md` (how we work: altitude, depth, range - from Felix Rieseberg's essay), `README.md`, `REQUIREMENTS.md`, `docs/PLAN.md`, `docs/FINDINGS.md`. Then `docs/CAD_STANDARD.md`
before touching any part, `docs/PIPELINE.md` before running anything.

## The goal (the user's words outrank everything)

Shoulder exo, at most 4 DOF (3 joints + sliding cuff, or 4 joints), whose whole mechanism rides within ~1 cm of the
skin over the full range of motion - overhead most of all - without ever touching the skin, at the user's CAD standard.
Never relax the 1 cm rule or the DOF cap to buy range without asking.
User decisions 2026-10-15 (REQUIREMENTS.md): pass at 14 mm, aim for 10; the base rides the scapula on the user's own
scapula handler (a separate part, outside the DOF count); the shoulder chain should have exactly 3 DOF - "the minimum
possible solution is 3 dof" - so push for 3 before settling for 4.
Scope 2026-10-15: MVP1 is an UNPOWERED kinematic proof of concept that tracks the arm (basic rolling bearings, the
user adds rotation sensing); no gears, pulleys or cables (MVP2 powers it, remote motors on cables). Passive
self-aligning slides at the cuff (outside the count). Right shoulder; fit the user: 6'1" (185 cm), 6'4" wingspan.
The user wants the design's evolution recorded for a final time-lapse visual: add every judged design to
docs/EVOLUTION.md (and its snapshot to pipeline/evolution/) as part of the judge loop.

## Ambition rules - every agent and subagent, every task (Felix Rieseberg's essay, docs/METHOD.md; user 2026-10-15:
"make sure any findings from it are hard engrained in everything you and all subagents do")

1. **Speed is assumed.** Never wait on something that can run in parallel; start now on the tools that exist and switch
   when better ones land; keep every slot busy (agents, GPU, CPU); time-box your task tightly and report early when a
   direction is dead (with the measured reason).
2. **Altitude: the outcome, not the task.** The outcome is all 19 requirements passing on a mechanism the wearer does not
   feel. Before you finish, say what happens next and leave a loop running instead of a one-off result (idea -> bench ->
   verifier -> GPU sweep -> L1 CAD -> judges -> dashboard, unattended).
3. **Depth: a specific, hard goal stated as reasonable.** Bench: gap 0 (in-band 2-14 mm >= 90 %, follow >= 95 %, reach
   >= 90 %, zero contact); built CAD: R1-aim (2-10 mm) >= 90 %. Not "do your best". When it looks impossible, change the
   morphology and prove the impossibility from data. Use the field's instruments (libigl, CalculiX, MuJoCo, OpenSim, ...),
   start from the rawest data, and let an outside judge decide - never grade your own work (a verifier re-measures
   every claim).
4. **Range: do the work of other fields, never role-play them**, and always include a red team looking for the pose
   that jams, the point that pinches, the number that is optimistic.
5. **Produce new knowledge** and write it down (docs/FINDINGS.md, docs/concepts/): what you measured, what failed, why.
6. **Chat with the user: big updates only** (user 2026-10-15): a new leader, a requirement newly passing, a blocker that
   needs them. Everything else goes to the dashboard and the repo.

## Working method (docs/METHOD.md - start every session with its checklist)

- **Never idle (user, 2026-10-15: "the goal of this project is to iterate as quick as possible ... don't let this
  happen again").** Never hold work behind infrastructure that can be built in parallel: start agents on the current
  tools and let them switch when the faster one lands. Before launching a workflow, count its concurrency (at most
  min(16, CPUs - 2) agents run at once per workflow: 2 on a 4-core box) and split the work over several workflows so
  everything runs at once. Keep a watchdog (a session cron every ~15 min) that checks every slot - workflows, agents,
  GPU endpoints (`tools/runpod_guard.py audit`: a stuck queue or unhealthy workers -> retire the endpoint and move the
  jobs at once), local CPU - and starts the next work when anything is idle. An interrupt can stop background agents:
  after one, check what is still running and report what stopped.

- **Outside judges, never self-assessment.** After every design change run `tools/judge_all.sh <design id>` (or
  `... fast` while iterating) and report the scorecard before/after. If a number moved because the measurement changed
  (skin model, motions, metric), say so separately from design changes.
- Start from the rawest material available (`data/raw/README.md`); when the human model and real data disagree, the data
  wins and the model gets fixed.
- Use the instruments of the field (OpenSim, MuJoCo/Drake, CalculiX, constrained parametric CAD) instead of ad-hoc
  scripts where they exist (docs/PLAN.md section 3). Ask before downloading anything.
- Keep the held-out split held out.

## Hard rules

- **User parts**: only BOTTOM may be modified (cut / merged with the neck). Never edit the user's Onshape model.
- **Personal data**: body scans and motion recordings stay in `data/raw/private/` (git-ignored). The user's machine
  also has a `personal-shoulder-diagnosis` folder - never read it into this repo or commit it.
- **Paid compute**: before any RunPod job or deploy, state the GPU type and estimated cost and wait for a yes.
  (User 2026-10-15 ~12:45 UTC: "you can spend more, i permit everything" - spend approved without a fixed cap for
  this push; still state GPU type + cost per batch and keep the endpoint hygiene below. User 2026-10-15 ~15:00: RunPod may offload
  work "only as cheap as possible if it provides a big speed up": cheapest worker type that works, scale to 0, keep small jobs local.) The key
  comes from the `RUNPOD_API_KEY` environment variable (or `~/.runpod_key` locally) - never print it, never commit it.
  After a search, set the endpoint's `workersMin` back to 0. Never touch the user's other pods (names starting `crl-`).
- **Downloads and licences**: installs approved by the user 2026-10-15 ("install whatever you want": CalculiX, gmsh,
  Blender 4.2.3 at /opt/blender are installed); licences (AMASS, SMPL-X) are still accepted by the user, not the agent.
- **Renders/films**: show a cheap motion preview and get approval before any paid render. Mannequin: matte black,
  faceless (not uncanny), muscles OK. Parts: bead blasted metal, polished screws, iglidur orange; no black parts.
- **CAD has two levels** (user, 2026-10-14: "you dont need to make high quality CAD with smoothing for each iteration
  and testing ... Just a basic CAD that has the expected keep outs of the joint, expected link height"). **L1 keep-out
  CAD** for every iteration and test: joint keep-outs (hub diameter x the real stack height), links as constant-thickness
  slabs at their real height over the skin, rail/carriage envelopes; one valid solid per part (`judge/part_validity.py`)
  and the motion judges (R1-R6, R10) - no fillets, no G2, no zebra. **L2 user-standard CAD** (docs/CAD_STANDARD.md,
  zebra check in `pipeline/full-exo/parts.html`) only for a design that passed the L1 judges on held-out data and that
  the user chose (phase P4).
- **Git**: commit and push after each meaningful, judged step; never commit caches, keys or personal data. Use the
  commit attribution your environment specifies.
- Compute: use the machine's own CPUs (check `nproc`, parallelise searches across cores); GPU on RunPod only for final Blender renders, after cost approval. Keep local CPU jobs to <= 4 workers on the user's laptop (it overheats); no limit in the cloud.

## Where things stand

**Start with docs/HANDOFF.md** (2026-10-15 ~16:00 UTC: the full state of the morphology swarm, the interrupted tracks,
the RunPod/cloud-farm state and the next steps; the previous session stopped at the user's weekly limit).


See README "Status" and `pipeline/full-exo/designs/cad_r18_n3_s1392_1_f300/judge/scorecard.md` (the 3R final rendered
2026-10-15; renders/2026-10-15_final_3R). Next levers, in order: a smaller joint stack (O17 hub: ~20 points of
workspace, docs/FINDINGS.md), the arm-end neck clear of link 2 over the whole workspace (R16 part interference), links
that follow the evaluator's fitted shape (R1), then the base skin-slip judge (R10). Evaluate picks at hub_r 11.5 until
the CAD builds a smaller joint.
