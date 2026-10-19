export const meta = {
  name: 'discovery-ideate',
  description: 'One discovery round: the planner-given lenses ideate buildable morphologies aimed at the measured limiters (each idea checked on the raw data), a judge dedups, red-teams, ranks and writes the top picks into the catalogue',
  phases: [
    { title: 'Ideate', detail: 'one agent per lens, 3 ideas each, every joint a real component' },
    { title: 'Judge', detail: 'dedup, red-team, rank, write catalogue entries' },
  ],
}
// WHAT: one round's ideation (child of discovery-loop.js): one agent per lens proposes 3 buildable morphologies,
//   a judge red-teams, ranks and appends the top picks to docs/concepts/catalogue.json (status "ideated").
// ARGS (passed by the loop): {round, state, lenses: [{key, brief}], top_n, exclude: [ids], repo, branch, trailer}
// WHEN: launched by discovery-loop.js; standalone only to re-run a round's ideation.
// Session settings (a NEW lead session sets these through the Workflow tool's args; the defaults are the 2026-10-16 session's):
//   args.repo    - absolute repo path            (default /home/user/exo-shoulder)
//   args.branch  - the branch every agent pushes  (REQUIRED: your session's branch; the script stops without it)
//   args.trailer - the commit attribution lines your environment's system reminder gives (two lines, '\n'-joined; REQUIRED)
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const COMMON = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding, especially the new hard rule 'Manufacturable joints only' (user 2026-10-15: every joint, active or passive, must be a real component that exists or is plausible at that size; rotations are cheap - pin / bearing pair, miniature U-joint, ball and socket / rod end / ball stud, rod in a linear-rotary bushing; ONE slider / linear rail is cheap ("a slider is super easy for me to fit"); two crossed rails are costly and must be shown to fit; a 3-translation passive joint never exists; prefer 0 passive translations, then 1, max 2; no gears, pulleys or cables; MVP1 unpowered, exactly 3 ACTIVE DOF, no undetermined passive coordinate). THE USER (just now): "continue with discovery work with the new nuance that I provided you, I'm excited to see a design cross the threshold into 90+%". 90+ = bench score >= 90, i.e. gap <= 27.5 (score = 100*(1 - gap/275); gap = 100*(max(0,.90-inband14) + max(0,.95-follow) + max(0,.90-reach)) + 100*contact, tools/concept_bench.py). Treat gap <= 27.5 as reasonable, and gap 0 as the real target.
STATE OF THE ART (read before ideating): docs/FINDINGS.md; docs/research/proximity_atlas.md (a rigid part must clear the highest skin it ever passes over; where metal can live); docs/research/passive_dof_hardware.md + tools/hardware_catalogue.json + docs/research/manufacturability_audit.md (real component envelopes; what is buildable; a radial skin-normal slide stands ~25 mm tall); docs/concepts/catalogue.json + rows/*.json + <id>.md (every morphology's verdict and MEASURED LIMITER); the dashboard data docs/dashboard/data/morphs.json. Numbers: champion spherical 3R gap 68.93 (Bench(60,160)) / 75.94 (Bench(110,360) exact); verified: rail-elbow 64.70, seed-offset-3r-slides 66.47 (its radial slide does not exist); unverified sweep records: offset-skin-normal-3r 35.65 (2 cuff slides + a <= 3 mm radial residual into the liner) and skin-normal-hubs-selfaligning 35.86 (3 slides: not buildable) - both under audit, possibly inflated by skin-contoured plates (floating-centre-3r was refuted for exactly that). The recurring limiters: hub 2 over the deltoid in 90-150 deg abduction (out of band), the J2 fold overhead (reach), metal that cannot clear the deltoid bunching under the acromion, and contact.
ROUND ${args.round} STATE (written by this round's planner from the latest measurements; it overrides any older numbers above):
${args.state}
THE USER (standing, latest first): "dont just stop on round 4 go as far as you can!"; "I'm hoping for some amazing 95+ scores with low simplicity"; "the reach numbers at 60s just isn't good ... lets try to max these out as much as we can" (CLAUDE.md "Reach is the priority now"); weird wins; think like an expert; every idea states its complexity count (tools/simplicity.py, docs/SIMPLICITY.md, lower = simpler) and must earn it in measured points; once verified scores reach 95, minimise complexity at score >= 95.`
const LENSES = args.lenses
const IDEA = { type: 'object', properties: { ideas: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, lens: { type: 'string' }, family: { type: 'string' },
  description: { type: 'string', description: 'what the metal looks like at rest, overhead, across-body, behind-back' },
  topology: { type: 'string', description: 'scapula -> joint (ACTIVE/PASSIVE, type) -> member -> ... -> arm' },
  components: { type: 'string', description: 'every joint -> real component with part number / envelope from tools/hardware_catalogue.json' },
  active_dof: { type: 'number' }, passive_dof: { type: 'number' }, passive_translations: { type: 'number' },
  why_it_beats_the_limiter: { type: 'string', description: 'mechanism-level argument with numbers from the data' },
  model_spec: { type: 'string', description: 'how to model it on tools/concept_kit.py: kinematics/IK, parts and envelopes, checks' },
  sweep_params: { type: 'string' }, main_risk: { type: 'string' }, expected_gap: { type: 'string' } },
  required: ['id', 'name', 'description', 'topology', 'components', 'active_dof', 'passive_dof', 'passive_translations', 'why_it_beats_the_limiter', 'model_spec', 'sweep_params', 'main_risk'] } } }, required: ['ideas'] }

phase('Ideate')
const ideas = (await parallel(LENSES.map((l) => () => agent(`${COMMON}\n\n${l.brief}\n\nPropose 3 morphologies (new ids, kebab-case, not already in docs/concepts/catalogue.json). For each, check the claim with a QUICK kinematic or proximity calculation of your own on the raw data (bench poses, posed skin, the proximity atlas maps) before you write it up, and give the numbers. Be specific: real part numbers, real envelopes, a model_spec another agent can build in 75 minutes on tools/concept_kit.py. Do not write to the repo.`, { label: `ideate:${l.key}`, phase: 'Ideate', schema: IDEA, effort: 'high' })))).filter(Boolean)
const all = ideas.flatMap((r) => r.ideas)
log(`${all.length} ideas from ${ideas.length} lenses`)

phase('Judge')
const judged = await agent(`${COMMON}\n\nAlready queued or screened elsewhere (do not pick again): ${(args.exclude || []).join(', ') || 'none'}.\n\nYou are the JUDGE and red team for round ${args.round}. The candidate morphologies:\n${JSON.stringify(all, null, 1)}\n\nFor each: (1) reject it if any joint has no real component at that size, if it needs more than 2 passive translations, if a passive coordinate is undetermined, or if it is a duplicate of an existing catalogue entry or of another candidate (merge duplicates); (2) red-team the 'why it beats the limiter' argument with a quick calculation on the raw data where the claim is checkable (the pose that jams, the point that pinches, the number that is optimistic); (3) rank the survivors by (expected gap reduction vs the champion) x (confidence) x (buildability: fewer passive translations first). Pick the TOP ${args.top_n || 4} and append them to docs/concepts/catalogue.json as new entries with status "ideated", t_ideated = now (ISO UTC), lens "round${args.round}:<lens>", and the fields the existing entries use (id, name, family, lens, status, description, topology, model_spec, sweep_params, main_risk, active_dof, passive_dof) plus 'components' and 'passive_translations' (python load/append/dump(indent=1); touch only your new entries). Write docs/concepts/round${args.round}_ideation.md (every candidate, the verdict and the reason, the ranking). Add one events line per new entry to docs/concepts/events.jsonl ({"time", "kind": "ideated", "id", "event"} like the existing lines). Commit only those files (git add explicit paths; git pull --rebase --autostash; push to origin ${BRANCH}). Return the picks.`, { label: 'judge', phase: 'Judge', schema: { type: 'object', properties: { picks: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' }, note: { type: 'string', description: 'one-line lead note for the modeller: the key risk to test first' } }, required: ['id', 'name', 'note'] } }, rejected: { type: 'array', items: { type: 'string' } } }, required: ['picks'] }, effort: 'high' })
return { judged, n_ideas: all.length }
