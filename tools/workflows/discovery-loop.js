export const meta = {
  name: 'discovery-loop',
  description: 'Self-driving discovery rounds (reach first, target 95+ at low complexity): each round a planner reads the latest measurements and sets the lenses, the ideation workflow proposes and judges ideas, the screening workflow models / sweeps / verifies them, the alignment auditor checks every screened / verified number for gaming, and a closer writes the lessons that steer the next round',
  phases: [
    { title: 'Plan', detail: 'planner: state, lenses, carried-over picks' },
    { title: 'Ideate', detail: 'discovery-ideate workflow' },
    { title: 'Screen', detail: 'exo-screen workflows, 2 designs per slice; each slice hands its designs to alignment-audit as soon as it finishes' },
    { title: 'Audit', detail: 'alignment-audit (auditor + skeptic -> docs/alignment/ledger.jsonl) on every screened / verified design; re-runs any slice audit that failed' },
    { title: 'Close', detail: 'round summary, lessons, next focus; never names a winner the ledger marks gamed' },
  ],
}
// WHAT: the self-driving discovery loop (docs/concepts/ROUNDS.md holds every round). Per round: planner -> the
//   discovery-ideate.js child workflow -> exo-screen.js child workflows (2 designs per slice, in parallel) -> the
//   alignment-audit.js child on every screened / verified design (each slice's designs go to the auditor as soon as
//   that slice finishes; the Audit phase re-runs any that failed) -> closer. The closer's next_focus steers the next round.
//   ALIGNMENT GATE (user 2026-10-16, CLAUDE.md "Alignment auditor"): the closer may not name a winner whose latest
//   docs/alignment/ledger.jsonl verdict is 'gamed' (the script re-asks the closer if it does), and carries every 'watch'
//   reason into the round notes; the planner's lead is the best verified design the ledger does not mark gamed.
// ARGS: {first_round: N, n_rounds: K, track: 'main', focus: '<the last round closer's "next focus" text>',
//        wf_dir: '<dir holding discovery-ideate.js + exo-screen.js + alignment-audit.js>' (default <repo>/tools/workflows),
//        repo, branch, trailer}
// WHEN: always running (CLAUDE.md "Discovery never stops at a round"); relaunch from the next round when one ends.
// Session settings (a NEW lead session sets these through the Workflow tool's args; the defaults are the 2026-10-16 session's):
//   args.repo    - absolute repo path            (default /home/user/exo-shoulder)
//   args.branch  - the branch every agent pushes  (REQUIRED: your session's branch; the script stops without it)
//   args.trailer - the commit attribution lines your environment's system reminder gives (two lines, '\n'-joined; REQUIRED)
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const WF_DIR = args.wf_dir || `${REPO}/tools/workflows`
const IDEATE = `${WF_DIR}/discovery-ideate.js`, SCREEN = `${WF_DIR}/exo-screen.js`, AUDIT = `${WF_DIR}/alignment-audit.js`
const SESSION = { repo: REPO, branch: BRANCH, trailer: TRAILER }
const first = args.first_round || 5, n = args.n_rounds || 4, track = args.track || 'main'
const BASE = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - read its goal, the ambition rules, "Manufacturable joints only", "Reach is the priority now", "Complexity is the second objective", "Every tested design gets its motion preview", "Every generation ends in a full CAD + render of its winner".
THE USER (latest first): "dont just stop on round 4 go as far as you can!"; "I'm excited to see what comes out of tonight, I'm hoping for some amazing 95+ scores with low simplicity"; "the reach numbers at 60s just isn't good ... lets try to max these out as much as we can". Score = 100 (1 - gap / 275); 95 = gap 13.75 on Bench(110,360) exact, frozen shape, confirmed by an independent verifier. With follow ~1.0 and in-band ~0.90 already met by the leaders, 95 needs reach >= ~0.77 at in-band >= 0.88 and ~0 contact.
ALIGNMENT (user 2026-10-16, CLAUDE.md "Alignment auditor"): a design whose latest verdict in docs/alignment/ledger.jsonl is 'gamed' (python3 tools/alignment_ledger.py get <id>: exit 3) cannot be called verified, a winner or a leader until the finding is resolved; 'watch' reasons are carried into every summary that names the design.
TRACK: ${track}. ${args.focus || ''}
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const PLAN = { type: 'object', properties: {
  lead_gap: { type: 'number', description: 'the best v_gap an independent verifier confirmed so far (Bench(110,360) exact frozen) on a design the alignment ledger does not mark gamed' },
  lead_id: { type: 'string', description: 'the row id of that lead (the alignment audit uses it as the reference design)' },
  state: { type: 'string', description: 'the round state for the ideators and screeners: verified leaders with numbers and complexity, the measured limiters and where poses are lost, what was tried and died (with the reason), the levers that look open - dense, numbers only from the repo' },
  lenses: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, brief: { type: 'string' } }, required: ['key', 'brief'] }, description: '2-3 lenses, each a concrete direction aimed at the measured limiter (start each brief with "LENS:")' },
  carry: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' }, note: { type: 'string' } }, required: ['id', 'name', 'note'] }, description: 'catalogue entries already ideated (status "ideated") but never screened that deserve screening this round, best first, at most 4' },
  exclude: { type: 'array', items: { type: 'string' }, description: 'ids being screened elsewhere right now (running workflows: read docs/concepts/events.jsonl tail and rows with status modelling)' },
}, required: ['lead_gap', 'lead_id', 'state', 'lenses', 'carry', 'exclude'] }
const CLOSE = { type: 'object', properties: {
  winner: { type: 'string', description: 'best verified design of this round that the alignment ledger does not mark gamed (id, v_gap, complexity, alignment verdict) or "none"' },
  winner_id: { type: 'string', description: 'the winner row id, or "none"' },
  alignment: { type: 'string', description: 'each audited design of the round: final ledger verdict and its watch / gamed reasons in one line; designs passed over as gamed' },
  new_leader: { type: 'boolean', description: 'true if it beats the previous verified lead_gap' },
  lessons: { type: 'string' }, next_focus: { type: 'string', description: 'what the next round should attack, with the measured reason' },
}, required: ['winner', 'winner_id', 'alignment', 'new_leader', 'lessons', 'next_focus'] }
const okId = (x) => typeof x === 'string' && /^[a-z0-9][a-z0-9._-]*$/.test(x)
// designs a slice screened that carry a number to audit (deaths carry none; their auditor already ran in exo-screen)
const auditIds = (res) => [...new Set(res.filter((x) => x && x.result && okId(x.result.id) && x.result.status !== 'dead').map((x) => x.result.id))]
const runAudit = (ids, R, why, ref) => workflow({ scriptPath: AUDIT }, { ...SESSION, targets: ids, ref: okId(ref) ? ref : undefined, max_targets: Math.max(6, ids.length), context: `discovery round ${R}: ${why}` })
  .then((a) => (a && Array.isArray(a.audits) ? a.audits : [])).catch((e) => { log(`audit r${R} (${ids.join(', ')}) failed: ${e}`); return [] })

let focus = args.focus || ''
const rounds = []
for (let k = 0; k < n; k++) {
  const R = first + k
  phase('Plan')
  const plan = await agent(`${BASE}

You are the PLANNER of discovery round ${R} (track ${track}). Previous round's closing note: ${focus || '(first round of this loop - read docs/concepts/round4_ideation.md / round3_ideation.md, docs/research/reach_attribution.md, docs/research/state_of_the_art.md)'}.
Read the latest measurements (docs/FINDINGS.md newest sections, docs/research/reach_attribution.md, docs/concepts/ROUNDS.md, rows/*.json with status verified / screened / dead and their limiters, the catalogue, the tail of docs/concepts/events.jsonl, docs/dashboard/data/morphs.json) and the alignment ledger (python3 tools/alignment_ledger.py latest: the lead is the best verified design NOT marked gamed; carry the leaders' watch reasons into the state so the lenses do not buy points the same way). Then: (1) write the round state (dense, numbers from the repo only); (2) choose 2-3 lenses that attack the measured limiter from DIFFERENT angles - at least one aimed at reach >= 0.77 at in-band >= 0.88 (fold levers, redundant non-orthogonal 4R within the 4-joint cap - Keemink 2018 TNSRE 26(4) -, re-seating, slimmer hardware, routing) and one aimed at LOW COMPLEXITY at the same reach (simplify the best fold lever: fewer passive joints, no spring, no sensed passive); weird wins; never relax the 1 cm rule or the DOF cap; (3) carry over any already-ideated, never-screened catalogue entries that deserve screening (round-4 picks first); (4) list ids being screened elsewhere right now. Append a "Round ${R} plan" entry to docs/concepts/ROUNDS.md (create it if missing: one section per round - plan, picks, results, lessons) and commit it. Time box 25 min.`, { label: `plan:r${R}`, phase: 'Plan', schema: PLAN })
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
  // each slice: screen, then (pipelined, no barrier) the alignment audit of what it screened / verified
  const screened = await parallel(slices.map((sl, j) => async () => {
    const tag = `r${R}-${'ABC'[j]}`
    const res = await workflow({ scriptPath: SCREEN }, { ...SESSION, slice: tag, items: sl, round: R, state: plan.state, lead: plan.lead_gap }).catch((e) => { log(`screen r${R} slice ${j} failed: ${e}`); return null })
    const got = (Array.isArray(res) ? res : []).filter(Boolean)
    const ids = auditIds(got)
    const audits = ids.length ? await runAudit(ids, R, `slice ${tag} screened / verified these designs this round`, plan.lead_id) : []
    return { got, audits }
  }))
  const results = screened.filter(Boolean).flatMap((s) => s.got)

  phase('Audit')
  const audits = screened.filter(Boolean).flatMap((s) => s.audits).filter((a) => a && a.final_verdict)
  const missing = auditIds(results).filter((id) => !audits.some((a) => a.id === id))
  if (missing.length) {
    log(`round ${R}: re-running the alignment audit for ${missing.join(', ')} (no verdict from its slice)`)
    audits.push(...(await runAudit(missing, R, 'catch-up: the slice audit returned no verdict', plan.lead_id)).filter((a) => a && a.final_verdict))
  }
  const gamed = audits.filter((a) => a.final_verdict === 'gamed').map((a) => a.id)
  const unaudited = auditIds(results).filter((id) => !audits.some((a) => a.id === id))
  const alignTxt = JSON.stringify(audits.map((a) => ({ id: a.id, claim: a.claim, verdict: a.final_verdict, auditor: a.auditor_verdict, reasons: (a.reasons || []).map((r) => `${r.level} ${r.key}: ${String(r.reason).slice(0, 300)}`), wearer: String(a.wearer || '').slice(0, 600), skeptic: a.skeptic && a.skeptic.summary }))).slice(0, 20000)
  log(`round ${R} alignment: ${audits.map((a) => `${a.id} ${a.final_verdict}`).join('; ') || '-'}${unaudited.length ? `; UNAUDITED ${unaudited.join(', ')}` : ''}`)

  phase('Close')
  const close = await agent(`${BASE}

You are the CLOSER of discovery round ${R}. Plan: ${JSON.stringify({ lead_gap: plan.lead_gap, lead_id: plan.lead_id, lenses: plan.lenses.map((l) => l.key) })}. Screening + verification results: ${JSON.stringify(results).slice(0, 60000)}.
ALIGNMENT AUDIT of this round (auditor + skeptic, final verdicts as recorded in docs/alignment/ledger.jsonl): ${alignTxt || '[]'}${unaudited.length ? `\nUNAUDITED (no ledger verdict this round - may be named only as "winner pending audit"): ${unaudited.join(', ')}` : ''}
(1) Name the round's winner = the best design whose number an independent verifier confirmed AND whose latest ledger verdict is not 'gamed' - re-check each candidate right before naming it with python3 tools/alignment_ledger.py get <id> (exit 3 = gamed; a later audit may have changed it). Ties: fewer passive translations, then lower complexity. If the best verified number is gamed, name the best non-gamed design and say in ROUNDS.md which design was passed over and the measured reason. Say whether the winner beats the previous verified lead ${plan.lead_gap}. Carry every 'watch' reason of the round's designs into the round notes (an "Alignment" paragraph in "Round ${R} results") and the FINDINGS section, with the numbers. (2) Write the round's results and lessons into docs/concepts/ROUNDS.md ("Round ${R} results"), a FINDINGS.md section with what was measured and what failed and why, an events line. (3) Say what the next round should attack, with the measured reason - if verified scores have reached 95 (gap <= 13.75), the next focus is lowering complexity at score >= 95. Commit + push. Time box 20 min.`, { label: `close:r${R}`, phase: 'Close', schema: CLOSE })
  let closed = close
  if (closed && gamed.includes(closed.winner_id)) {
    log(`round ${R}: the closer named ${closed.winner_id}, which the alignment ledger marks GAMED - re-asking`)
    closed = (await agent(`${BASE}

You are the CLOSER of discovery round ${R}, second pass. Your first pass named ${closed.winner_id} the winner, but its alignment verdict is GAMED (${JSON.stringify(audits.find((a) => a.id === closed.winner_id) || {}).slice(0, 4000)}). CLAUDE.md: a design the ledger marks gamed cannot be called a winner or a leader until the finding is resolved. Check python3 tools/alignment_ledger.py get ${closed.winner_id} (exit 3 = still gamed). If it is still gamed: name the best verified non-gamed design instead (or "none"), correct "Round ${R} results" in docs/concepts/ROUNDS.md, the FINDINGS section and the events line you wrote (say which design was passed over and why, with the numbers), commit + push. If a newer ledger entry is not gamed, keep the winner and cite that entry. Time box 10 min.`, { label: `close2:r${R}`, phase: 'Close', schema: CLOSE })) || closed
  }
  rounds.push({ round: R, lenses: plan.lenses.map((l) => l.key), screened: items.map((i) => i.id), alignment: audits.map((a) => ({ id: a.id, verdict: a.final_verdict })), close: closed })
  if (closed) { focus = closed.next_focus; log(`round ${R} closed: winner ${closed.winner}${closed.new_leader ? ' (NEW LEADER)' : ''}${gamed.length ? `; passed over as gamed: ${gamed.join(', ')}` : ''}`) }
}
return { track, rounds }
