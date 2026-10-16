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
  work "only as cheap as possible if it provides a big speed up": cheapest worker type that works, scale to 0, keep small jobs local.
  User 2026-10-15 ~23:15: "If anything could speed up research do it you don't need my approval just think about everything
  intelligently and understand our main goal we can't just put 3 dof eveyrhwerr lol" - speed-ups (farm redeploys, more
  slots, quota moves between our own endpoints, new tooling) need no approval; the hygiene rules here still hold, and the
  goal is a buildable minimum-DOF exo, not more passive freedom.) The key
  comes from the `RUNPOD_API_KEY` environment variable (or `~/.runpod_key` locally) - never print it, never commit it.
  After a search, set the endpoint's `workersMin` back to 0. Never touch the user's other pods (names starting `crl-`).
- **Downloads and licences**: installs approved by the user 2026-10-15 ("install whatever you want": CalculiX, gmsh,
  Blender 4.2.3 at /opt/blender are installed); licences (AMASS, SMPL-X) are still accepted by the user, not the agent.
- **Renders/films**: show a cheap motion preview and get approval before any paid render. Mannequin: matte black,
  faceless (not uncanny), muscles OK. Parts: bead blasted metal, polished screws, iglidur orange; no black parts.
- **Manufacturable joints only** (user, 2026-10-15: "I do not think I am able to make a 3 dof translating passive device
  ... two is probably the most I can make ... Make sure that all designs are thought of with manufacturability in mind, is
  there actually a component that can be designed which serves these degrees of freedom for the size they are
  presented at?" and, clarifying: "its not that there are two max, its more subtle than that, although two would be a
  good max, its just hard to actually make a 2 dof passive translation component fit in such a small space, so max 2, 1
  is better", and "like a linear rail, or some sort of passive joint that actually exists (the real component must exist
  or be plausible) for it to be there, for example a ball and socket is fine because its a 3 dof passive joint but a 3dof
  translation passive is not, its way more subtle!"): the test is PER JOINT - does a real component exist that gives
  exactly that freedom at that size? Rotations are cheap: pin / bearing pair (1 rot), miniature U-joint (2 rot), ball and
  socket / rod end / ball stud / spherical plain bearing (3 rot), rod in a linear-rotary bushing (1 rot + 1 trans).
  Translations: a single slider / linear rail / miniature guide (1 trans) is cheap ("a slider is super easy for me to
  fit") at its real length; two crossed rails
  (2 trans) are bulky and must be shown to fit; a 3-translation passive joint does not exist as a compact part - never.
  Prefer 0 passive translations, then 1; 2 is the hard maximum. Rank designs that tie on the bench by fewer passive
  translations. Every joint, active or passive, maps to a real component - a catalogue part number (bearing, miniature guide,
  bushing) or a simple machinable design - and the model carries that component's REAL envelope (assembly height,
  footprint, rail length = travel + block length, mass) as sampled metal. A radial (skin-normal) slide counts as
  standing up by its travel + block length. A few mm of radial play may go to the cuff liner's compliance, stated as
  such. No virtual slides, no zero-height stages; the verifier rejects a design whose joints have no component.
- **Every generation ends in a full CAD + render of its winner** (user, 2026-10-16: "after every new generation, make the
  full cad of the winning verified design of that generation, just so it can be displayed in higher quality and I can see
  with the humanoid with muscles"). A generation = one discovery round (ideate -> screen -> verify). Its winner = the best
  design whose number an independent verifier confirmed (ties broken by fewer passive translations). Build it at the
  user's CAD standard in the user's style (pipeline/conformal/param_cad/user_style.py: bent bars from line/arc sketches,
  real hub stacks and catalogue parts, BOTTOM cut + arm end, no lofts), judge it, render stills on the muscled mannequin
  (matte black, faceless; parts bead blasted, polished screws, iglidur orange; no black parts) and add it to
  docs/EVOLUTION.md + the dashboard. This is the user's standing choice for L2 CAD of generation winners.
  Before that CAD the winner gets a FINAL POLISH (user, 2026-10-16: "the winning designs get a big GPU run right just to
  squeeze out that last possible optimization?"): a wide multi-start optimisation of every free parameter directly on
  the verification bench (Bench(110,360), frozen-shape protocol, fast cache for the search and the exact path for the
  claim) on the farm - this bench runs on CPU (libigl / the signed-distance cache), so the farm is the instrument; a GPU
  port is worth building only if it measurably beats the farm per dollar. A polished config replaces the CAD's config
  only after an independent verifier confirms a gain >= 1 gap point.
  (User 2026-10-16 ~03:00: no film for now - "you dont need to do the film ... focus everything on solution hunting";
  the generation-winner CAD + stills still run: "generation winner cad should still run". Quota while no film renders:
  exo-blender-cycles workersMax 1 (stills), exo-cpu1 workersMax 9 - give the render endpoint its 4 back when a film or a
  big render batch is approved.)
- **Complexity is the second objective** (user, 2026-10-16: "it would be cool to have a simplicity score for each design
  impacted by degrees of freedom moving parts, etc. I think thats a pretty major part and for now shouldn't impact overall
  score but should show in the chart", then "when score start capping out around 95+ over the night, prioritize lowering
  that simplicity number"). Every design carries a complexity count (tools/simplicity.py, docs/SIMPLICITY.md: 0 = three pins
  on bearing pairs and three links with no passive freedom; each passive translation, crossed rail, passive rotation,
  extra body / joint, closed loop, sliding pair and sensed passive ADDS points; lower = simpler), shown on the dashboard
  next to the score and NOT folded into it. Once verified bench scores plateau at >= 95 (gap <= 13.75), the search
  objective switches: minimise complexity subject to score >= 95 (a constrained / Pareto search - drop a passive joint,
  merge bodies, swap a slide for a pin), and a simpler design at score >= 95 beats a more complex one at a higher score.
- **Reach is the priority now** (user, 2026-10-16 ~05:00 UTC: "i feel like the reach numbers at 60s just isn't good, it seems
  like they're plateauing near the top, lets try to max these out as much as we can"). Every verified leader sits at reach
  0.59-0.62 on Bench(110,360) (overhead 0.17-0.25) while in-band (~0.90) and follow (~1.0) are met: the gap IS reach. Push
  reach toward 0.9 with every lever inside the rules - fold levers (scheduled / relay / coupled elements), a 4th joint
  (the DOF cap allows 4; MVP1 needs every coordinate determined: spring-centred + stops, or sensed), slimmer hardware,
  re-seating - and attribute every lost pose to its cause before choosing the lever. Never relax the 1 cm rule or the
  DOF cap, and never shrink the singularity / transmission margins to buy reach without a red-team and the user's say.
- **No lofts, ever** (user, 2026-10-15: "for all the design you do, lofts look horrible and introduce geometric problems, you
  can combine arcs, but no lofts!"): every surface comes from sketches of lines and tangent arcs - extrudes, revolves,
  sweeps of ONE constant section along a line/arc path, fillets. No lofts, no surfaces fitted or shrink-wrapped to skin
  data, no twisted sweeps. Change direction with bends (an arc in the cross-section) and planform turns instead.
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
