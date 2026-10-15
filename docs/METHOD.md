# Method: how to be ambitious on this project

Source of the framework: Felix Rieseberg, *How to be more ambitious: A tutorial for humans with models* (13 Oct 2026),
https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/ - read it. What follows is our
paraphrase, applied to this project. It is the operating method for every agent and every session here.

The essay names four kinds of ambition. **Speed** (the same work, faster) is assumed. The other three decide how we work.

## Altitude: work at the outcome, not the task

The task is "design CAD for a shoulder exo". The outcome behind it is: **a person does overhead and everyday tasks
wearing it, with assistance, and does not feel the mechanism**. Behind that: a design that keeps passing as the data,
the bodies and the requirements change.

- Ask "what happens next?" before each piece of work. A design nobody can wear, quote or test is not progress.
- Build durable loops instead of one-off results, the way "fix this crash" became "keep the app crash-free":
  new raw data or a new requirement -> re-judge every candidate -> re-optimise -> scorecard -> commit. `judge/` and
  `tools/judge_all.sh` are the start of that loop; make it run unattended.
- Give the model what the loop needs to run without a human in it: the raw data in `data/`, tools it can run itself,
  outside judges it can call (`judge/`), compute it can use (the cloud machine's CPUs, RunPod for renders only).

## Depth: do it the way the best people in the field do

1. **The field's instruments, not its vocabulary.** Saying "biomechanically validated" changes nothing; running
   OpenSim's Seth 2016 shoulder model does. Likewise CalculiX instead of a home-made FEA, constrained parametric CAD
   instead of fitted surfaces, exact signed distance instead of sampled maps, OpenCap instead of synthetic keyframes.
   When a home-made tool exists, cross-check it with the professional one before trusting it.
2. **Unreasonable goals, treated as reasonable.** The user's bar is <= 10 mm. Aim for **<= 5 mm over the whole ROM,
   100 % follow including overhead, zero contact, < 150 g** - and when something looks impossible, keep going: change
   the mechanism family, the base, the attachment, the DOF assignment within the cap. "Impossible" is a finding that
   needs a proof (a counter-example from the data), not a feeling.
3. **Challenge what we know.** Write every belief down and try to break it from the raw data:
   - "The base rides the scapula." (It bolts to a thorax plate - FINDINGS.)
   - "The rig's skin is right." (25 mm biceps bulge, arm through the chest - FINDINGS.)
   - "The 8 clips represent daily life." (They were synthesised and optimised against.)
   - "A spherical chain about a fixed GH point is the right family."
   - "Overhead fails because of link geometry." (Or because of girdle motion?)
   - "The evaluator score tracks the real CAD." (It is optimistic.)
4. **Produce new knowledge.** Once deep in the data, look for what nobody knows yet: e.g. the earliest kinematic
   signal that predicts a design will fail overhead, a closed-form bound on how far a fixed-centre chain must sit from
   the skin given measured GH translation, or a design rule that holds on held-out bodies. Show it predicts on data it
   has not seen.
5. **Outside judges.** The model does not grade itself. Every claim is checked by something else: the judges in
   `judge/`, an independent solver, a supplier's DFM review, a standard (ISO/TS 15066), held-out data, and finally a
   printed prototype on two real bodies (REQUIREMENTS.md R1-R15).

The essay's depth prompt asks four things before rewriting a task: what would a top professional do that was not asked
for, what is the rawest material, which methods and tools, and what outside the model and the user shows it is right.
`docs/PLAN.md` answers them for this project; re-ask them at the start of every phase.

## Range: bring in other fields

**Nouns into verbs.** Not "a shoulder exo" but: *follow a moving, deforming, translating joint so closely the wearer
cannot feel it, while carrying load through soft tissue to a rigid frame, without ever pinching.* Each verb points at a
field that has solved part of it:

| verb | field | what to take from it (do what they do, not role-play them) |
|---|---|---|
| follow a translating joint | biomechanics; rehab robotics (Harmony, ANYexo) | girdle mechanisms, misalignment compensation, scapulohumeral rhythm data |
| hug a moving surface | tailoring / pattern making, technical sportswear | how raglan sleeves, darts and gussets follow the shoulder through overhead motion; where garments do and do not move with skin |
| carry load through soft tissue | prosthetics and orthotics (socket fitting) | pressure-tolerant vs pressure-sensitive regions, liner materials, total-contact fitting, how a prosthetist checks a fit |
| never pinch | pressure-injury medicine, ISO/TS 15066 | pressure and shear limits by body region |
| tiny, smooth, precise joints | watchmaking, surgical instruments | miniature bearings, finishing, how sub-mm stacks are toleranced |
| light, stiff, fatigue-proof | aerospace | Ti machining, fatigue design, topology optimisation |
| fold into a small envelope | deployable / origami mechanisms | spherical linkage families and singularity analysis |
| look inevitable | industrial design (Class-A surfacing) | curvature continuity, zebra analysis, constrained sketches |

**Assemble the crew, including a red team.** Bring in the methods of: a biomechanist (OpenSim), an orthotist (fit and
pressure check), a machinist (DFM, quote), a safety reviewer (ISO 13482 / IEC 80601-2-78 hazard list), a tailor
(how fabric follows the shoulder). Red team: someone paid to find the pressure point that hurts after an hour, and the
pose that jams the chain. Use parallel subagents for independent tracks - each doing the work of that field (run
the model, produce the pressure map, write the quote request), never writing a character.

## Per-session checklist

1. Altitude: what outcome does this session move? What loop does it leave running?
2. Depth: which professional instrument does the work, which raw data does it start from, which judge decides?
3. Range: which other field's method applies here, and who is the red team?
4. Close with the scorecard (`tools/judge_all.sh`), before vs after, and what was learned in docs/FINDINGS.md.

## Running agents (the essay applied to orchestration - hard rules for the lead and every subagent)

Learned the hard way on 2026-10-15: screening agents sat unlaunched while the lead waited for a faster bench, a
workflow ran 2 agents at a time without anyone counting, a GPU endpoint sat stuck for 26 minutes, and stopped agents
went unnoticed. The user: "the goal of this project is to iterate as quick as possible ... don't ever waste time like
this again". So:

- **Speed is assumed** (the essay takes it as given): every slot busy - agents, GPU, CPU. Never hold work behind
  infrastructure that can be built in parallel; agents start on the current tools and switch when the better one lands.
  Count a workflow's concurrency before launching it (min(16, CPUs - 2) per workflow) and split the work so everything
  runs at once. A 15-minute watchdog checks every workflow, agent, endpoint and core and launches the next work.
- **Altitude in every prompt**: the prompt names the outcome (all 19 requirements, a wearer who does not feel it), the
  loop the agent's result feeds (bench -> verifier -> GPU -> L1 CAD -> judges -> dashboard) and what happens next.
- **Depth in every prompt**: a specific hard numeric target stated as reasonable (gap 0; R1-aim >= 90 %), a tight
  time box (the "Fast" list: audacious goals, short deadlines), the instrument of the field to use, the rawest data to
  start from, and the outside judge that decides. No agent grades itself: every result that matters passes an
  adversarial verifier before it is reported as a win.
- **Range in the crew**: agents do the work of distinct fields (kinematician, orthotist, machinist, biomechanist,
  inventor) plus a red team; they produce artefacts (a model, a measurement, a quote request), not characters.
- **Honest reporting**: measured numbers before/after, measurement changes separate from design changes, failures said
  plainly, and every result logged on the dashboard as it lands.
- **Brief agents fully up front.** A message sent to an agent that a workflow is running can start a second copy of it
  (2026-10-15: two cloud-farm agents built the same endpoint in parallel and collided). Put every constraint in the
  first prompt; to change a running agent's brief, say which instance keeps the work and which stops.
