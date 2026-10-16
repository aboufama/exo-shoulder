# EXO shoulder

A shoulder exoskeleton whose whole mechanism rides **within ~1 cm of the skin** over the full range of motion
(overhead most of all), never touches the skin, has **at most 4 degrees of freedom**, and is built to the user's CAD
standard. Elbow, forearm link and forearm cuff are the user's existing design (`data/user_cad/`).

This repo is organised the way a field-leading wearable-robotics engineer would run the problem, not around the
scripts that happened to get written:

| question | where |
|---|---|
| What exactly must be true, as numbers? | [`REQUIREMENTS.md`](REQUIREMENTS.md) - 19 requirements (R1-R17 plus R1-aim and R5-aim), each with a pass/fail threshold |
| What would an expert do that the brief doesn't ask for, from what raw material, with which tools? | [`docs/PLAN.md`](docs/PLAN.md) - the depth reframing and phases P0-P6 |
| How do we work? | [`docs/METHOD.md`](docs/METHOD.md) - altitude, depth, range (Felix Rieseberg's essay, applied) |
| What, other than the designer, shows it's right? | [`judge/`](judge/) - geometry judges + scorecard; ultimately a printed prototype on real bodies (R15) |
| What has been learned so far? | [`docs/FINDINGS.md`](docs/FINDINGS.md) |
| How do I run it? | [`docs/PIPELINE.md`](docs/PIPELINE.md), [`CLAUDE.md`](CLAUDE.md) for agents |

## Status (2026-10-16, 20:30 UTC by git commit time)

**New here, with no context?** The work lives on branch `claude/trusting-pasteur-6czobp` (`main` stopped on
2026-10-14). Read, in this order: [`CLAUDE.md`](CLAUDE.md) (the user's goal and rules, binding),
[`docs/METHOD.md`](docs/METHOD.md), [`docs/HANDOFF.md`](docs/HANDOFF.md) (the full state, what was running, the open
questions, the next steps), [`docs/OPERATIONS.md`](docs/OPERATIONS.md) (how to run everything), then this file,
REQUIREMENTS, PLAN, FINDINGS and [`docs/concepts/ROUNDS.md`](docs/concepts/ROUNDS.md). The working method
comes from Felix Rieseberg's essay
[How to be more ambitious: A tutorial for humans with models](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)
([`docs/METHOD.md`](docs/METHOD.md)).

- **Scoring.** Score = 100 (1 - gap / 275) on the verification bench: Bench(110,360) exact, frozen shape, fold margin 5,
  O20 hubs. A number counts only after an independent verifier re-measures it. The golden target is score >= 95 at
  complexity ~0, and nothing has reached it yet.
- **Best verified overall:** minarc-stop-knuckle-4r pick1, **18.40 (score 93.31)**, held out 21.31. It has 4 revolutes,
  and the knuckle K is spring-held and sensed.
- **Best verified with 3 active joints:** sidecar-longdyad-knuckle-3r (round 8, verified 2026-10-16, commit 63167c0),
  **18.91 (93.12)**, held out 22.67. Its K is slaved to J2 by a strap-level "sidecar" drive. Its sibling
  sidecar-parallelogram is verified at 19.13 (93.04). The previous 3-active lead was 22.82. The simplest class, a plain 3R at complexity 0, tops out at 31-34.
- **What limits every leader: reach.** The J2 fold costs ~86 of 360 workspace poses and 20 of 28 overhead poses.
  In-band (~0.89) and follow (~1.0) are close to target.
- **Built CAD.** The best builds pass 7-8 of the 19 requirements:
  - user_pinknee_h1b passes 8 (3 DOF);
  - user_minarc_pick1 and l1_geneva-rod pass 7 each;
  - proximity R1 tops out at 81 % against 90, overhead R4 at ~73 % against 80, and workspace R16 at 74 % against 90.
  - The gen-5 full CAD (user_geneva_rod) is in progress.
- **Design history:** [`docs/EVOLUTION.md`](docs/EVOLUTION.md) has every judged design, and
  [`docs/concepts/ROUNDS.md`](docs/concepts/ROUNDS.md) has every discovery round.

## Quickstart

```bash
bash tools/setup.sh                                   # python deps (cadquery 2.5 / OCP 7.7, trimesh, scipy, torch)
bash tools/judge_all.sh cad_r13_n4_s1343_1 fast       # every judge + the scorecard for the reference design
cd pipeline/full-exo && python3 -m http.server 4198   # index.html?d=cad_r13_n4_s1343_1 (motion), parts.html (each part, zebra)
```

Rebuilding CAD, searching new kinematics and rendering: docs/PIPELINE.md. Searches run on the RunPod CPU farm
(`tools/cloud_run.py`, docs/CLOUD_RUN.md) and renders on RunPod GPUs; the key comes from `~/.runpod_key` or
`RUNPOD_API_KEY` (docs/OPERATIONS.md section 5; never print it); state the cost before running.

## Layout

```
REQUIREMENTS.md   numbered requirements, thresholds, judges
docs/             HANDOFF (state), OPERATIONS (runbook), METHOD, PLAN (depth reframing, phases), FINDINGS,
                  CAD_STANDARD, HARDWARE, PIPELINE, EVOLUTION; concepts/ (rounds, rows, models, verifiers)
judge/            body_contact, part_contact, part_validity, scorecard, requirements.json
data/user_cad/    the user's STEP (source of truth, read-only except BOTTOM)
data/raw/         protocol for the raw inputs still to collect (scans, OpenCap, OpenSim, AMASS/SMPL-X)
tools/            setup, benches (concept_bench, env_bench), judge_all, cloud_run (farm), runpod_guard, dashboards
                  (dash_build, dash_refresh.sh), agent_tail; workflows/ (the swarm's scripts + templates)
pipeline/         the working code: human rig (avg, arm-rom), scorer + viewers (full-exo), search + CAD + FEA
                  (conformal), G2 helpers (shoulder-d4), renders (joint-render)
```

History before this restructure: github.com/aboufama/exo-arm (archive).
