# Instructions for the agent working on this repo

Read first, in order: `docs/METHOD.md` (how we work: altitude, depth, range - from Felix Rieseberg's essay), `README.md`, `REQUIREMENTS.md`, `docs/PLAN.md`, `docs/FINDINGS.md`. Then `docs/CAD_STANDARD.md`
before touching any part, `docs/PIPELINE.md` before running anything.

## The goal (the user's words outrank everything)

Shoulder exo, at most 4 DOF (3 joints + sliding cuff, or 4 joints), whose whole mechanism rides within ~1 cm of the
skin over the full range of motion - overhead most of all - without ever touching the skin, at the user's CAD standard.
Never relax the 1 cm rule or the DOF cap to buy range without asking.

## Working method (docs/METHOD.md - start every session with its checklist)

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
- **Paid compute**: before any RunPod job or deploy, state the GPU type and estimated cost and wait for a yes. The key
  comes from the `RUNPOD_API_KEY` environment variable (or `~/.runpod_key` locally) - never print it, never commit it.
  After a search, set the endpoint's `workersMin` back to 0. Never touch the user's other pods (names starting `crl-`).
- **Downloads and licences**: ask first; licences (AMASS, SMPL-X) are accepted by the user, not the agent.
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

See README "Status" and `pipeline/full-exo/designs/cad_r13_n4_s1343_1/judge/scorecard.md`. Next step: phase P0 in
docs/PLAN.md (base-mount physics, R10) - it needs nothing from the user except permission to download OpenSim's
shoulder model; the rig in `pipeline/avg/body_pose.py` already gives a first number.
