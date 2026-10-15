export const meta = {
  name: 'exo-morphology-ideation-b',
  description: 'Swarm ideation B: four more lenses propose distinct 3-active-DOF shoulder-exo morphologies (merged later into catalogue A)',
  phases: [ { title: 'Ideate', detail: 'one designer agent per lens proposes 8-12 distinct morphologies' } ],
}
const CTX = `You are a mechanism designer in a swarm exploring the design space of a shoulder exoskeleton. Repo: /home/user/exo-shoulder (read-only for you in this stage: do NOT edit, create or commit files, and do not run heavy compute - the 4 CPU cores are saturated by judges; a quick python one-liner to look up a body dimension is fine).
Read first: REQUIREMENTS.md (the 19 requirements + the user's decisions, incl. the ACTIVE-DOF rule), docs/FINDINGS.md (what failed and why - skim, it is long), docs/concepts/README.md (this stage + the baseline to beat), the docstring of tools/concept_bench.py (the common bench every concept will be measured on: it gives per pose the thorax/scapula/humerus/forearm frames T,S,H,F and the posed skin; a concept supplies the 3-D sample points of its metal per pose, or None if it cannot take the pose), docs/HARDWARE.md (the O20 bearing joint: ~20 mm hub, ~12 mm stack).
THE PROBLEM in short: right shoulder, 185 cm man. MVP1 is UNPOWERED: the arm drives the mechanism, rolling bearings, the user adds rotation sensing; no gears, pulleys or cables in MVP1 (MVP2 powers each active joint with a remote motor on a cable, so every active coordinate must be a drivable, sensable joint). Exactly 3 ACTIVE DOF (user rule: passive elements whose position is set by the chain's closure / driven by the arm, e.g. passive self-aligning cuff slides, do not count; but an undriven spare coordinate that can sag or flop when unpowered fails R17). The base rides the scapula on the user's own scapula handler (a separate part; the base frame is the scapula S, which slips ~15 mm over the bone - R10). The user's own arm parts (upper-arm cuff, forearm cuff, BOTTOM bar) stay; the chain ends on the upper-arm cuff region. The WHOLE mechanism must ride 2-14 mm from the skin (aim 2-10) over >= 90 % of the covered skin, over the full range of motion - overhead most of all - never touching the skin, follow >= 95 % of motion frames, move through >= 90 % of the everyday arm workspace with no skin contact or part collision, mass <= 500 g titanium, strong enough for ~10 N.m. Fundamental difficulties found so far: rigid links over skin that moves and bulges with the pose (deltoid, acromion, axilla); the GH centre translates relative to the scapula; joint hubs (~12 mm stack) sit off the skin; links of a spherical chain (all axes through the GH centre) must clear every pose of the workspace, which pushes them off the skin; singularities of a 3R spherical wrist inside the range; an undriven spare joint sags (R17 kills redundant chains). The current champion (baseline) is a spherical 3R with O20 hubs and strap links: built CAD ~41-58 % in band at 14 mm (target 90 %), follows 98 %, ~78 % of the workspace. Within that family the GPU search has plateaued: the user believes - and we are acting on it - that more UNIQUE morphologies beat further tuning within one type.`

const MORPH = {
  type: 'object',
  properties: {
    id: { type: 'string', description: 'short kebab-case id, unique, e.g. arc-rail-gimbal' },
    name: { type: 'string' },
    topology: { type: 'string', description: 'joint list from scapula base to the arm, with joint type (R hub, R as curved rail / ring bearing, P, passive slide, closure joints), axis placement and which are active' },
    active_dof: { type: 'integer' },
    passive_dof: { type: 'integer' },
    dof_reasoning: { type: 'string', description: 'why it is exactly 3 active per the user rule, and how every passive coordinate is set by the arm or by closure (no sagging spare coordinate)' },
    description: { type: 'string', description: 'how it looks and works, where the metal sits relative to the skin in rest, overhead, across-body and behind-back poses' },
    why_better: { type: 'string', description: 'which fundamental difficulty it beats and why it could exceed the baseline on in-band share / workspace' },
    main_risk: { type: 'string' },
    unpowered_and_mvp2: { type: 'string', description: 'unpowered behaviour (R17) and how each active joint would be driven/sensed in MVP2' },
    model_spec: { type: 'string', description: 'a modelling recipe precise enough that another agent can build an idealised Python model for tools/concept_bench.py in ~1 hour: which frames it attaches to, how joint values are solved per pose (closed-form IK, closure, optimisation), metal geometry with real dimensions (straps, hubs, rails, carriages, rings), how passive elements absorb GH translation, how to detect a pose it cannot take' },
    sweep_params: { type: 'string', description: 'the few parameters and ranges a short sweep inside this morphology should vary' },
    modelling_cost: { type: 'string', enum: ['low', 'medium', 'high'] },
    prior_art: { type: 'string', description: 'closest known device or paper, or none' },
  },
  required: ['id', 'name', 'topology', 'active_dof', 'passive_dof', 'dof_reasoning', 'description', 'why_better', 'main_risk', 'unpowered_and_mvp2', 'model_spec', 'sweep_params', 'modelling_cost', 'prior_art'],
}
const LIST = { type: 'object', properties: { morphologies: { type: 'array', items: MORPH } }, required: ['morphologies'] }
const LENSES = [
  { key: 'biomimetic-girdle', text: 'BIOMIMETIC: copy the shoulder girdle itself - an exo-clavicle and exo-scapula riding over the real ones, links that follow the lines of the deltoid / rotator-cuff muscles (the skin over a muscle line moves with it), mechanisms that reproduce the scapulohumeral rhythm so the chain moves the way the skin does, or that let the GH-centre translation happen inside the mechanism instead of fighting it.' },
  { key: 'hardware-unlocks', text: 'HARDWARE THAT UNLOCKS GEOMETRY: what joint hardware changes where metal can sit - thin-section (Kaydon Reali-Slim-like, 4-8 mm section) ring bearings of 60-200 mm bore that can wrap the arm or the shoulder at low height, crossed-roller rings, curved linear guides / arc rails with ball carriages (THK HCR-like), iglidur polymer arc slides, tiny 10-12 mm bearings, wire-race bearings, flexure pivots. For each, propose a 3-active-DOF morphology that only becomes possible with it, with real dimensions from catalogues you know.' },
  { key: 'robot-wrists', text: 'ROBOT WRIST AND CONSTANT-VELOCITY MECHANISMS as shoulder mechanisms: Rosheim Omni-Wrist, double-Hooke / CV joints, Agile Eye, spherical 3-RRR variants with legs that wrap the shoulder, the Canfield joint, cable-free hemispherical-workspace parallel wrists, gimbals with nested rings near the skin. How to place them so the shoulder sits in the remote centre, the singularities fall outside the range of motion, and the bulk is within ~1 cm of the skin.' },
  { key: 'skin-data-driven', text: 'SKIN-DATA DRIVEN: reason from how the skin of the shoulder actually moves across the poses of the rig (pipeline/avg/body_pose.py; the bench poses). You may run LIGHT python (one process, OMP_NUM_THREADS=1, under 5 min total) to find the skin regions and strips that stay at near-constant distance from the GH centre, or near-constant relative to the scapula or the humerus, across poses. Propose morphologies that put rails, hubs and links exactly on those stable regions and avoid the bulging ones (deltoid, acromion, axilla). Report the stable regions you found (coordinates in the thorax frame) in the descriptions.' },
]
phase('Ideate')
const proposals = await parallel(LENSES.map(L => () =>
  agent(`${CTX}\n\nYOUR LENS: ${L.text}\n\nPropose 8-12 DISTINCT morphologies under this lens (distinct = different kinematic topology or a different physical realisation that changes where the metal sits relative to the skin - not parameter variants of one idea). At least two should be bold or weird. Each must be exactly 3 ACTIVE DOF per the user rule (passive elements allowed and counted separately). Do not propose the baseline itself (a spherical 3R with three hubs and strap links over the shoulder) unless your version changes something fundamental. Give honest risks. The model_spec must be precise enough to implement and measure on tools/concept_bench.py within about an hour.`,
    { label: `ideate:${L.key}`, phase: 'Ideate', schema: LIST })
    .then(r => r ? r.morphologies.map(m => ({ ...m, lens: L.key })) : [])
))
const all = proposals.filter(Boolean).flat()
log(`${all.length} proposals from ${proposals.filter(Boolean).length}/${LENSES.length} lenses`)
return { proposals: all }
