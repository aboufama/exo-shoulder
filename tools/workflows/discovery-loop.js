export const meta = {
  name: 'discovery-loop',
  description: 'Self-driving discovery rounds (reach first, target 95+ at low complexity): each round a planner reads the latest measurements and sets the lenses, the ideation workflow proposes and judges ideas, the screening workflow models / sweeps / verifies them, and a closer writes the lessons that steer the next round',
  phases: [
    { title: 'Plan', detail: 'planner: state, lenses, carried-over picks' },
    { title: 'Ideate', detail: 'discovery-ideate workflow' },
    { title: 'Screen', detail: 'exo-screen workflows, 2 designs per slice' },
    { title: 'Close', detail: 'round summary, lessons, next focus' },
  ],
}
// WHAT: the self-driving discovery loop (docs/concepts/ROUNDS.md holds every round). Per round: planner -> the
//   discovery-ideate.js child workflow -> exo-screen.js child workflows (2 designs per slice, in parallel) -> closer.
//   The closer's next_focus steers the next round.
// ARGS: {first_round: N, n_rounds: K, track: 'main', focus: '<the last round closer's "next focus" text>',
//        wf_dir: '<dir holding discovery-ideate.js + exo-screen.js>' (default <repo>/tools/workflows), repo, branch, trailer}
// WHEN: always running (CLAUDE.md "Discovery never stops at a round"); relaunch from the next round when one ends.
// Session settings (a NEW lead session sets these through the Workflow tool's args; the defaults are the 2026-10-16 session's):
//   args.repo    - absolute repo path            (default /home/user/exo-shoulder)
//   args.branch  - the branch every agent pushes  (default claude/trusting-pasteur-6czobp)
//   args.trailer - the commit attribution lines your environment's system reminder gives (two lines, '\n'-joined)
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
const BRANCH = (args && args.branch) || 'claude/trusting-pasteur-6czobp'
const TRAILER = (args && args.trailer) || 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_014NJ3o5nJ9b1u4LXnQRjmMh'
const WF_DIR = args.wf_dir || `${REPO}/tools/workflows`
const IDEATE = `${WF_DIR}/discovery-ideate.js`, SCREEN = `${WF_DIR}/exo-screen.js`
const SESSION = { repo: REPO, branch: BRANCH, trailer: TRAILER }
const first = args.first_round || 5, n = args.n_rounds || 4, track = args.track || 'main'
const BASE = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - read its goal, the ambition rules, "Manufacturable joints only", "Reach is the priority now", "Complexity is the second objective", "Every tested design gets its motion preview", "Every generation ends in a full CAD + render of its winner".
THE USER (latest first): "dont just stop on round 4 go as far as you can!"; "I'm excited to see what comes out of tonight, I'm hoping for some amazing 95+ scores with low simplicity"; "the reach numbers at 60s just isn't good ... lets try to max these out as much as we can". Score = 100 (1 - gap / 275); 95 = gap 13.75 on Bench(110,360) exact, frozen shape, confirmed by an independent verifier. With follow ~1.0 and in-band ~0.90 already met by the leaders, 95 needs reach >= ~0.77 at in-band >= 0.88 and ~0 contact.
TRACK: ${track}. ${args.focus || ''}
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const PLAN = { type: 'object', properties: {
  lead_gap: { type: 'number', description: 'the best v_gap an independent verifier confirmed so far (Bench(110,360) exact frozen)' },
  state: { type: 'string', description: 'the round state for the ideators and screeners: verified leaders with numbers and complexity, the measured limiters and where poses are lost, what was tried and died (with the reason), the levers that look open - dense, numbers only from the repo' },
  lenses: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, brief: { type: 'string' } }, required: ['key', 'brief'] }, description: '2-3 lenses, each a concrete direction aimed at the measured limiter (start each brief with "LENS:")' },
  carry: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' }, note: { type: 'string' } }, required: ['id', 'name', 'note'] }, description: 'catalogue entries already ideated (status "ideated") but never screened that deserve screening this round, best first, at most 4' },
  exclude: { type: 'array', items: { type: 'string' }, description: 'ids being screened elsewhere right now (running workflows: read docs/concepts/events.jsonl tail and rows with status modelling)' },
}, required: ['lead_gap', 'state', 'lenses', 'carry', 'exclude'] }
const CLOSE = { type: 'object', properties: {
  winner: { type: 'string', description: 'best verified design of this round (id, v_gap, complexity) or "none"' },
  new_leader: { type: 'boolean', description: 'true if it beats the previous verified lead_gap' },
  lessons: { type: 'string' }, next_focus: { type: 'string', description: 'what the next round should attack, with the measured reason' },
}, required: ['winner', 'new_leader', 'lessons', 'next_focus'] }

let focus = args.focus || ''
const rounds = []
for (let k = 0; k < n; k++) {
  const R = first + k
  phase('Plan')
  const plan = await agent(`${BASE}

You are the PLANNER of discovery round ${R} (track ${track}). Previous round's closing note: ${focus || '(first round of this loop - read docs/concepts/round4_ideation.md / round3_ideation.md, docs/research/reach_attribution.md, docs/research/state_of_the_art.md)'}.
Read the latest measurements (docs/FINDINGS.md newest sections, docs/research/reach_attribution.md, docs/concepts/ROUNDS.md, rows/*.json with status verified / screened / dead and their limiters, the catalogue, the tail of docs/concepts/events.jsonl, docs/dashboard/data/morphs.json). Then: (1) write the round state (dense, numbers from the repo only); (2) choose 2-3 lenses that attack the measured limiter from DIFFERENT angles - at least one aimed at reach >= 0.77 at in-band >= 0.88 (fold levers, redundant non-orthogonal 4R within the 4-joint cap - Keemink 2018 TNSRE 26(4) -, re-seating, slimmer hardware, routing) and one aimed at LOW COMPLEXITY at the same reach (simplify the best fold lever: fewer passive joints, no spring, no sensed passive); weird wins; never relax the 1 cm rule or the DOF cap; (3) carry over any already-ideated, never-screened catalogue entries that deserve screening (round-4 picks first); (4) list ids being screened elsewhere right now. Append a "Round ${R} plan" entry to docs/concepts/ROUNDS.md (create it if missing: one section per round - plan, picks, results, lessons) and commit it. Time box 25 min.`, { label: `plan:r${R}`, phase: 'Plan', schema: PLAN })
  if (!plan) break
  log(`round ${R}: lead ${plan.lead_gap}; lenses ${plan.lenses.map((l) => l.key).join(', ')}; carry ${plan.carry.map((c) => c.id).join(', ') || '-'}`)

  phase('Ideate')
  const idea = await workflow({ scriptPath: IDEATE }, { ...SESSION, round: R, state: plan.state, lenses: plan.lenses, top_n: Math.max(2, 4 - Math.min(2, plan.carry.length)), exclude: [...plan.exclude, ...plan.carry.map((c) => c.id)] }).catch((e) => { log(`ideate r${R} failed: ${e}`); return null })
  const picks = ((idea && idea.judged && idea.judged.picks) || []).filter((p) => !plan.exclude.includes(p.id))
  const items = [...plan.carry, ...picks].slice(0, 6)
  log(`round ${R}: screening ${items.map((i) => i.id).join(', ')}`)

  phase('Screen')
  const slices = []
  for (let i = 0; i < items.length; i += 2) slices.push(items.slice(i, i + 2))
  const screened = await parallel(slices.map((sl, j) => () => workflow({ scriptPath: SCREEN }, { ...SESSION, slice: `r${R}-${'ABC'[j]}`, items: sl, round: R, state: plan.state, lead: plan.lead_gap }).catch((e) => { log(`screen r${R} slice ${j} failed: ${e}`); return null })))
  const results = screened.filter(Boolean).flat().filter(Boolean)

  phase('Close')
  const close = await agent(`${BASE}

You are the CLOSER of discovery round ${R}. Plan: ${JSON.stringify({ lead_gap: plan.lead_gap, lenses: plan.lenses.map((l) => l.key) })}. Screening + verification results: ${JSON.stringify(results).slice(0, 60000)}.
(1) Name the round's winner = the best design whose number an independent verifier confirmed (ties: fewer passive translations, then lower complexity), and whether it beats the previous verified lead ${plan.lead_gap}. (2) Write the round's results and lessons into docs/concepts/ROUNDS.md ("Round ${R} results"), a FINDINGS.md section with what was measured and what failed and why, an events line. (3) Say what the next round should attack, with the measured reason - if verified scores have reached 95 (gap <= 13.75), the next focus is lowering complexity at score >= 95. Commit + push. Time box 20 min.`, { label: `close:r${R}`, phase: 'Close', schema: CLOSE })
  rounds.push({ round: R, lenses: plan.lenses.map((l) => l.key), screened: items.map((i) => i.id), close })
  if (close) { focus = close.next_focus; log(`round ${R} closed: winner ${close.winner}${close.new_leader ? ' (NEW LEADER)' : ''}`) }
}
return { track, rounds }
