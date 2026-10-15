export const meta = {
  name: 'exo-morphology-ideation',
  description: 'Swarm ideation: many lenses propose distinct 3-active-DOF shoulder-exo morphologies, then dedup, critique for gaps, and output a modelling catalogue',
  phases: [
    { title: 'Ideate', detail: 'one designer agent per lens proposes 8-12 distinct morphologies' },
    { title: 'Dedup', detail: 'merge near-duplicates into one catalogue, nothing distinct dropped' },
    { title: 'Gaps', detail: 'completeness critics name what the catalogue misses' },
    { title: 'Finalise', detail: 'merge the gap ideas and rank by payoff vs modelling cost' },
  ],
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
  { key: 'serial-topology', text: 'SYSTEMATIC ENUMERATION of 3-active-joint serial chains beyond the baseline: mixes of revolute hubs, revolute joints realised as curved rails, prismatic/arc joints; axis arrangements (all concurrent at GH, offset, skew, one axis deliberately off-centre); joint orders; base placement on the scapula frame (top, back, front of the shoulder); which link rides where; passive slides at the cuff that absorb GH translation. Think in terms of where each joint singularity falls relative to the range of motion, and where each link has to be to clear the poses.' },
  { key: 'remote-centre', text: 'REMOTE-CENTRE JOINTS so no hub stands off the skin: revolute joints realised as curved guide rails with carriages, large-diameter ring or open C-ring bearings (e.g. around the upper arm for axial rotation, or a hoop around the shoulder), nested sliding shells, telescoping arcs, rolling-contact arcs. Each rail/ring lies on the skin and its axis passes through (or near) the GH centre. Consider how the rail length, curvature and carriage size trade against the range of motion.' },
  { key: 'closed-loop', text: 'CLOSED-LOOP / PARALLEL mechanisms with exactly 3 active coordinates and passive joints set by closure: spherical parallel manipulators (3-RRR / Agile-Eye-like, but low-profile around the shoulder), remote-centre-of-motion parallelograms (as in surgical robots), double-parallelogram RCMs, hybrid serial-parallel chains, four-bar-coupled links that keep a link parallel to the skin. Watch for passive coordinates that are not fully set by closure (they would sag) and for the count of passive joints (flag it - the user may want to rule on many-passive-joint designs).' },
  { key: 'literature', text: 'THE LITERATURE of shoulder exoskeletons and arm rehabilitation robots (e.g. Harmony, ANYexo, ABLE, MGA, CAREX, SAM, Dampace, MEDARM, ArmeoPower, ALEx, NESM, BONES, RUPERT, IntelliArm, ChARMin, LIMPACT, ShoulderX, Paexo, Hand-free, BLUE SABINO, exos with shoulder-girdle mechanisms, soft exosuits with rigid elements). For each relevant idea: what it does about the GH translation, the overhead singularity and the bulk off the skin, and how it would be adapted to 3 active DOF within ~1 cm of the skin on a scapula base. Propose the adapted versions, not the originals.' },
  { key: 'distributed-dof', text: 'DISTRIBUTED DOF PLACEMENT: put each DOF where the skin moves least or where a joint can lie flattest - e.g. 2R near the shoulder plus axial rotation by a ring or rail around the upper arm lower down; 1R at the scapula plus 2 on the arm; using the upper arm itself as a link between two cuffs; axes referenced to the elbow; joints that sit in the low-bulge strips of skin (find them: which skin over the shoulder, deltoid, upper arm stretches or bulges least across poses?).' },
  { key: 'body-hugging', text: 'BODY-HUGGING SEGMENTED forms: armour-like overlapping plates (pauldron lames) that slide over each other, vertebra/snake chains whose many joints are kinematically COUPLED by linkages (not gears/cables) so the active count stays 3, scale-like shells, a second rigid "clavicle/scapula-like" bone that rides the skin, links that are skin-shaped shells rather than straps. Be strict about DOF and about what sets each coupled coordinate.' },
  { key: 'weird-compliant', text: 'WEIRD and COMPLIANT ideas: rolling-contact joints (CORE, Rolamite), flexure-based or large-deflection compliant links that bend with the skin while the 3 rotary joints carry the motion, tensegrity, sliding-band / belt-like links, magnetically or elastically preloaded shells, links whose shape changes passively with the pose, origami/kirigami. MVP1 asks for basic rolling bearings: flag anything that would need the user to accept a different joint technology, but still propose it if it could win big.' },
  { key: 'overhead-first', text: 'OVERHEAD-FIRST design: start from the hardest poses (full overhead elevation, behind the head, across the body, behind the back, the axilla closing at rest) and work backwards: where must the singularity of the chain be to stay outside the range, which skin is exposed and stable in those poses (top of the shoulder? back of the scapula?), how must links route so that the overhead pose keeps them close (the acromion and deltoid bulge, the axilla), and which morphologies keep that while still following the rest pose.' },
]

phase('Ideate')
const proposals = await parallel(LENSES.map(L => () =>
  agent(`${CTX}\n\nYOUR LENS: ${L.text}\n\nPropose 8-12 DISTINCT morphologies under this lens (distinct = different kinematic topology or a different physical realisation that changes where the metal sits relative to the skin - not parameter variants of one idea). At least two should be bold or weird. Each must be exactly 3 ACTIVE DOF per the user rule (passive elements allowed and counted separately). Do not propose the baseline itself (a spherical 3R with three hubs and strap links over the shoulder) unless your version changes something fundamental. Give honest risks. The model_spec must be precise enough to implement and measure on tools/concept_bench.py within about an hour.`,
    { label: `ideate:${L.key}`, phase: 'Ideate', schema: LIST })
    .then(r => r ? r.morphologies.map(m => ({ ...m, lens: L.key })) : [])
))
const all = proposals.filter(Boolean).flat()
log(`${all.length} proposals from ${proposals.filter(Boolean).length}/${LENSES.length} lenses`)

const CAT = {
  type: 'object',
  properties: {
    catalogue: { type: 'array', items: { type: 'object', properties: {
      ...MORPH.properties,
      lenses: { type: 'array', items: { type: 'string' } },
      merged_from: { type: 'array', items: { type: 'string' }, description: 'ids of the proposals merged into this entry' },
      priority: { type: 'string', enum: ['A', 'B', 'C'], description: 'A = highest expected payoff per modelling hour' },
      priority_reason: { type: 'string' },
    }, required: [...MORPH.required, 'lenses', 'merged_from', 'priority', 'priority_reason'] } },
    dropped: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, reason: { type: 'string' } }, required: ['id', 'reason'] }, description: 'proposals not kept as their own entry and why (merged duplicate, not 3 active DOF, physically impossible) - every proposal id must appear in a catalogue entry merged_from or here' },
  },
  required: ['catalogue', 'dropped'],
}

phase('Dedup')
const dedup = await agent(`${CTX}\n\nYou are the CATALOGUE EDITOR. Below are ${all.length} morphology proposals (JSON) from ${LENSES.length} lens designers. Build one catalogue of DISTINCT morphologies: merge near-duplicates (keep the best-specified spec, graft the best details from the others, list merged ids in merged_from), keep every genuinely distinct idea (a different topology or a different place for the metal is distinct), fix DOF counts that are wrong per the user rule (and drop with a reason anything that cannot be 3 active DOF or is physically impossible), and set a priority A/B/C by expected payoff per modelling hour against the baseline's real weakness (in-band share near the skin, workspace clearance). Every proposal id must appear in some merged_from or in dropped. Keep the model_spec of each entry complete and implementable.\n\nPROPOSALS:\n${JSON.stringify(all)}`,
  { label: 'dedup', phase: 'Dedup', schema: CAT })

const GAP = { type: 'object', properties: { missing: { type: 'array', items: MORPH } }, required: ['missing'] }
phase('Gaps')
const brief = (dedup ? dedup.catalogue : []).map(m => `${m.id}: ${m.name} - ${m.topology}`).join('\n')
const CRITICS = [
  'a kinematician: which topologies / axis arrangements / joint-type combinations of 3 active DOF are absent?',
  'a clinician and anatomist: which body regions, skin strips, bony landmarks or motion strategies (scapulohumeral rhythm, the GH translation) does no entry exploit?',
  'an inventor who distrusts the consensus: which radically different principle (not a linkage over the shoulder at all) is absent?',
]
const gaps = await parallel(CRITICS.map((c, k) => () =>
  agent(`${CTX}\n\nYou are a COMPLETENESS CRITIC - ${c}\nThe catalogue so far (id: name - topology):\n${brief}\n\nPropose 3-6 morphologies that are genuinely MISSING (not variants of entries above), each exactly 3 active DOF per the user rule, with full specs. If nothing important is missing, return an empty list.`,
    { label: `critic:${k}`, phase: 'Gaps', schema: GAP })))
const extra = gaps.filter(Boolean).flatMap(g => g.missing.map(m => ({ ...m, lens: 'critic' })))
log(`${extra.length} gap proposals`)

phase('Finalise')
const final = await agent(`${CTX}\n\nYou are the CATALOGUE EDITOR again. Merge these gap proposals into the catalogue: add the distinct ones (with priority), merge duplicates into existing entries, drop with a reason anything not 3 active DOF or impossible. Then order the whole catalogue by priority (A first) and, within a priority, by expected payoff. Return the complete catalogue (all entries, existing and new) and the complete dropped list (existing and new).\n\nCATALOGUE:\n${JSON.stringify(dedup)}\n\nGAP PROPOSALS:\n${JSON.stringify(extra)}`,
  { label: 'finalise', phase: 'Finalise', schema: CAT })

return { n_proposals: all.length, n_gap: extra.length, final: final || dedup, raw: all.map(m => ({ id: m.id, lens: m.lens, name: m.name })) }
