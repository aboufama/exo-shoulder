export const meta = {
  name: 'alignment-audit',
  description: 'Misalignment superfan: for each design, is its number a better exo or a better score? An auditor runs tools/alignment_audit.py plus the docs/ALIGNMENT.md judgement pass and records a verdict in docs/alignment/ledger.jsonl; a skeptic then tries to refute every gamed / watch verdict, and the ledger computes the final verdict',
  whenToUse: 'after every claim, every verification, every new leader, every judge / metric / bench change, and on a timer (hourly, targets from the ledger due list)',
  phases: [
    { title: 'Scope', detail: 'targets from args, or the ledger due list (tools/alignment_ledger.py due)' },
    { title: 'Audit', detail: 'one auditor per design: 12 automatic checks + the 25-pattern judgement pass -> docs/alignment/<id>.md/.json + a ledger entry' },
    { title: 'Skeptic', detail: 'one skeptic per gamed / watch verdict tries to refute each reason; the ledger computes the final verdict' },
  ],
}
// WHAT: the alignment auditor the user asked for (2026-10-16 ~20:10 UTC: "require an agent on the side that is a superfan
//   that targets misalgnment ... see if models are cheating the system or gaming the system in some way to scro ehigher
//   witout actually being beter ... it needs to be a crucial aprt of our loop"). Per design:
//     AUDITOR - python3 tools/alignment_audit.py audit <id> (12 checks: held_out, fast_frozen, near_touch, dominance,
//       continuity, fold_margin, idle, sampling, complexity, reporting, judge_change, rules), a re-wear of the frozen claim
//       when the claim is new or moved (remeasure bench / held, models unchanged), then the judgement pass: every pattern of
//       docs/ALIGNMENT.md section 2 (T1-T4, S1-S5, M1-M5, P1-P4, R1-R4, G1-G6) read against the goal of section 1. Writes
//       docs/alignment/<id>.json (tool), <id>.findings.json + <id>.md (judgement), and appends the ledger entry with
//       python3 tools/alignment_ledger.py append (the tool computes the verdict: worst of the checks and the findings;
//       a judgement can raise a verdict, never lower it).
//     SKEPTIC - for a 'gamed' or 'watch' verdict only: tries to refute each reason (wrong measurement, wrong threshold,
//       apples-to-oranges reference, a missing number that is in fact on file, a pattern that does not cost the wearer
//       anything). Rulings -> docs/alignment/<id>.rulings.json -> python3 tools/alignment_ledger.py skeptic, which
//       computes the final verdict (worst level among the reasons NOT refuted with evidence). The auditor's own claims
//       therefore always get a skeptic (CLAUDE.md "Outside judges, never self-assessment").
//   A 'gamed' final verdict means: the number, as it stands, is not evidence of a better exo. CLAUDE.md: such a design
//   cannot be called verified, a winner or a leader until the finding is resolved (a re-measure, a fix, or a later audit).
// ARGS: {targets: ['<row id>', ...] (optional; empty = the ledger's due list), since: '<ISO time>' (optional: also audit
//        every verified row if a bench / judge / metric / kit file changed since then), ref: '<row id>' (reference for the
//        dominance check, default: the tool's own - frontload for the sidecar family), context: '<why this audit runs:
//        "round 9 screen", "new leader X", "judge R17 default changed in <sha>">', max_targets: 6, repo, branch, trailer}
//   branch + trailer REQUIRED (tools/workflows/README.md).
// WHEN TO LAUNCH: after every claim (a row's gap / v_gap / polished_gap set or moved), after every verification, whenever a
//   design becomes the leader (dashboard card, HANDOFF, the closer's winner), after every judge / metric / bench / kit
//   change (since = the change's commit time), before any generation-winner CAD or polish swap, and on a timer (hourly,
//   no targets: the due list). discovery-loop.js runs it on every screened / verified design of each round (Audit phase).
// OUTPUT: {audits: [{id, claim, auditor_verdict, final_verdict, reasons, skeptic}], gamed: [ids], watch: [ids], dropped}
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const MAX = args.max_targets || 6
const RANK = { clean: 0, ok: 0, watch: 1, gamed: 2 }
const worst = (levels) => ['clean', 'watch', 'gamed'][Math.max(0, ...levels.map((l) => RANK[l] || 0))]
const okId = (s) => typeof s === 'string' && /^[a-z0-9][a-z0-9._-]*$/.test(s)

const BASE = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding. You serve the user's request of 2026-10-16 ~20:10 UTC (verbatim): "at the same time as all the research is happening, please require an agent on the side that is a superfan that targets misalgnment. It should understand the goal of the project, to make a super low profile and free range shoulder joint, and see if models are cheating the system or gaming the system in some way to scro ehigher witout actually being beter. This coudl be done in many ways, but it needs to be a crucial aprt of our loop".
WHAT BETTER MEANS (docs/ALIGNMENT.md section 1 - the goal; the score is only its proxy): every piece of metal rides ~1 cm off the skin (2-14 mm passes, aim 10; metal at 1-2 mm on the model is metal on a real, bulging arm) over the FULL range of motion, overhead most of all, never touching; the arm moves freely and continuously through its whole natural range (no jam, no branch flip, no reset by hand); nothing the wearer feels (no stiff spring, no cuff twist, no near-singular joint); at most 4 DOF, 3 preferred, every joint a real component at its real size (O20 hubs); the unpowered MVP1 genuinely tracks the arm.
THE PROXY: gap = 100[(0.90-inband14)+ + (0.95-follow)+ + (0.90-reach)+] + 100 contact; score = 100(1 - gap/275); Bench(60,160) fast / Bench(110,360) exact; frozen-shape protocol; held-out split; near-touch gap; continuity flood; fold margin 5 deg in th (tools/concept_kit.py lines 25-30); complexity tools/simplicity.py. Known gaming cases and their numbers: docs/ALIGNMENT.md section 2 and 3, docs/alignment/live_audit_2026-10-16.md.
WHY THIS AUDIT RUNS: ${args.context || '(not given)'}.
HARD LIMITS: never edit a bench, a judge, a kit, a model, a row, the dashboard page or CLAUDE.md, and never change a score; tools you add are new files. Never relax the 1 cm rule or the DOF cap. A proposed TIGHTENING of a metric or rule is a measurement change: write it as a proposal (with its measured effect on every verified row) in your .md, never as an input to the verdict. Never message other agents. Do not touch files running agents use. Local compute: nice, OMP_NUM_THREADS=1, <= 2 processes, never pkill -f; heavy re-wears may go to the farm (python3 tools/cloud_run.py, docs/CLOUD_RUN.md), key only as RUNPOD_API_KEY="$(cat ~/.runpod_key)", never echo it, <= $1.5 per audit.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries; docs/alignment/ledger.jsonl merges by union). No model names in commits or files.`

const SCOPE = { type: 'object', properties: {
  targets: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, why: { type: 'string' }, claim: { type: 'number' } }, required: ['id', 'why'] }, description: 'ids due for an audit, most important first (lowest claimed gap first: leaders matter most)' },
}, required: ['targets'] }
const REASON = { type: 'object', properties: { key: { type: 'string' }, level: { type: 'string', enum: ['watch', 'gamed'] }, reason: { type: 'string' } }, required: ['key', 'level', 'reason'] }
const AUDIT = { type: 'object', properties: {
  id: { type: 'string' },
  verdict: { type: 'string', enum: ['clean', 'watch', 'gamed'], description: 'the verdict the LEDGER TOOL printed for your entry (not your own reading)' },
  tool_verdict: { type: 'string', description: 'verdict of tools/alignment_audit.py alone' },
  claim: { type: 'number', description: 'the claimed number the ledger recorded (v_gap, else gap)' },
  reasons: { type: 'array', items: REASON, description: 'every non-ok reason the ledger entry holds (reason_items): the checks and your judgement findings' },
  remeasured: { type: 'string', description: 'what you re-wore and the numbers (or why not: unsupported model, unchanged claim)' },
  wearer: { type: 'string', description: 'what the wearer actually gets, measured: overhead reach taken / total, raised-arm reach, taken poses with metal < 2 mm, deepest contact (mm, where), workspace in-band, springs / stops / cuff twist / near-singular postures' },
  files: { type: 'array', items: { type: 'string' } },
}, required: ['id', 'verdict', 'claim', 'reasons', 'remeasured', 'wearer', 'files'] }
const SKEPTIC = { type: 'object', properties: {
  id: { type: 'string' },
  rulings: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, refuted: { type: 'boolean' }, evidence: { type: 'string' } }, required: ['key', 'refuted', 'evidence'] } },
  final_verdict: { type: 'string', enum: ['clean', 'watch', 'gamed'], description: 'the verdict the LEDGER TOOL printed for your skeptic entry' },
  missed: { type: 'array', items: { type: 'string' }, description: 'gaming the auditor missed, with evidence (not counted in this verdict; it is in your .md for the next audit)' },
  summary: { type: 'string' },
}, required: ['id', 'rulings', 'final_verdict', 'missed', 'summary'] }

// ---------------------------------------------------------------- Scope
phase('Scope')
let targets = (Array.isArray(args.targets) ? args.targets : (args.targets ? [args.targets] : [])).map((t) => (typeof t === 'string' ? { id: t, why: args.context || 'requested' } : t)).filter(Boolean)
if (!targets.length) {
  const sc = await agent(`${BASE}

You are the SCOPER of an alignment audit. Run: python3 tools/alignment_ledger.py due --json${args.since ? ` --since ${args.since}` : ''}
It lists the claim-bearing rows (verified / screened / cad / gpu) with no ledger entry, a claimed number that moved since their last audit, row / verifier files committed after it${args.since ? ', and every verified row when a bench / judge / metric / kit file changed since ' + args.since : ''}. Also add any design the dashboard (docs/dashboard/data/morphs.json) or docs/HANDOFF.md currently presents as the leader or best design if its latest ledger entry (python3 tools/alignment_ledger.py get <id>) is older than its row's last commit. Return them most important first: lowest claimed gap first (read v_gap, else gap, from docs/concepts/rows/<id>.json), with the due reason. Read only; write nothing; 5 min.`, { label: 'scope', phase: 'Scope', schema: SCOPE, effort: 'low' })
  targets = (sc && sc.targets) || []
}
const seen = new Set()
const bad = targets.filter((t) => !t || !okId(t.id)).map((t) => JSON.stringify(t))
targets = targets.filter((t) => t && okId(t.id) && !seen.has(t.id) && seen.add(t.id))
if (bad.length) log(`ignored malformed target ids: ${bad.join(', ')}`)
const dropped = targets.slice(MAX).map((t) => t.id)
targets = targets.slice(0, MAX)
if (dropped.length) log(`max_targets ${MAX}: NOT audited this run (relaunch with targets = these): ${dropped.join(', ')}`)
if (!targets.length) { log('nothing due'); return { audits: [], gamed: [], watch: [], dropped } }
log(`auditing ${targets.map((t) => t.id).join(', ')}${args.ref ? ` (reference ${args.ref})` : ''}`)

// ---------------------------------------------------------------- Audit -> Skeptic (pipelined per design)
const audits = await pipeline(targets,
  (t) => agent(`${BASE}

You are the ALIGNMENT AUDITOR (the user's "superfan that targets misalignment") of design ${t.id}. Due because: ${t.why}. You love this project's goal, so you hunt every way its number rises without the exo getting better. Time box 35 min; report early with what you measured.
1. CHECKS: python3 tools/alignment_audit.py audit ${t.id}${args.ref ? ` --ref ${args.ref}` : ''}  -> docs/alignment/${t.id}.json (12 checks, each ok / watch / gamed with a measured reason).
2. RE-WEAR when the claim is new or moved (docs/alignment/remeasure/${t.id}_bench.json missing, or older than the row's last commit: git log -1 --format=%cI -- docs/concepts/rows/${t.id}.json) and the model is supported (see the tool's docstring): CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_audit.py remeasure ${t.id} bench (then held), or the same on the farm; then re-run step 1. The models run UNCHANGED (only their audit() is wrapped to record more). Where tools/alignment_wear_probe.py supports the design (or a one-line adapter in a NEW file can), run it for the unscored workspace in-band, overhead reach, poses with metal < 1 / 2 / 3 mm and contact depths. Report every number you could not get and why.
3. JUDGEMENT PASS (the part no script does): read the row (docs/concepts/rows/${t.id}.json), the model (docs/concepts/models/${t.id}.py), every verifier file (docs/concepts/verify/${t.id}*), the row's git history (git log --format='%h %ci %s' -- docs/concepts/rows/${t.id}.json), its events (grep ${t.id} docs/concepts/events.jsonl), its dashboard row (docs/dashboard/data/morphs.json) and its docs/concepts/${t.id}.md. Walk EVERY pattern of docs/ALIGNMENT.md section 2 (T1-T4, S1-S5, M1-M5, P1-P4, R1-R4, G1-G6) against this design and against the goal above: is any part of its number bought by metal parked just past a cutoff, a margin read on another angle, a search bound walking toward a singular posture, a skewed or sparse sample, an unsampled body, a static island, a virtual / zero-size / slim part, an unchecked clash, an idle drive, a spring that cannot hold, in-sample tuning or held-out leakage, re-measuring until lucky, a judge changed with the design, a self-measured or refuted number shown as verified, a best-of-many without its spread, metal hugging at 1-3 mm, a stiff spring, cuff twist, a near-singular posture, or complexity hidden by the count? Also anything NEW (a new pattern goes into your .md with a proposed catalogue entry). Each pattern present = one finding {key: the pattern id (or NEW-<short>), level: watch | gamed, reason: measured numbers + file, evidence}. 'gamed' needs measured proof that the number ranks the design above a design that is better for the wearer (e.g. ahead plain, behind at 2 mm near-touch or held out under the same harness) or that a hard rule is broken; otherwise 'watch'. Write the findings to docs/alignment/${t.id}.findings.json (a JSON list; [] if none).
4. LEDGER: python3 tools/alignment_ledger.py append ${t.id} --findings docs/alignment/${t.id}.findings.json --by auditor --run audit:${t.id}  - it computes the verdict (worst of the checks and your findings) and prints the entry: return THAT verdict and its reason_items.
5. REPORT: write docs/alignment/${t.id}.md (overwrite the auditor sections, keep any earlier "Skeptic" section below a dated rule): the verdict and the claim; what the wearer gets (measured: overhead reach taken / total, raised-arm reach, taken poses with metal < 2 mm, deepest contact and where, workspace in-band, springs / stops / cuff twist / singular postures); each finding (pattern, evidence, why the exo is not actually better, action); proposals (as proposals only). Plain sentences, numbers with their file.
6. Commit docs/alignment/${t.id}.json, ${t.id}.findings.json, ${t.id}.md, docs/alignment/ledger.jsonl and any remeasure / probe output you wrote; push.`, { label: `audit:${t.id}`, phase: 'Audit', schema: AUDIT }),
  (a, t) => {
    if (!a) return { id: t.id, auditor_verdict: null, final_verdict: null, reasons: [], skeptic: null, note: 'auditor returned nothing - rerun this target' }
    if (a.verdict === 'clean') return { id: t.id, claim: a.claim, auditor_verdict: 'clean', final_verdict: 'clean', reasons: [], wearer: a.wearer, skeptic: null }
    return agent(`${BASE}

You are the SKEPTIC of an alignment audit (CLAUDE.md: the auditor's own claims get a skeptic; never trust, re-measure). Design ${t.id}; the auditor's verdict: ${a.verdict.toUpperCase()} on claim ${a.claim}. Its reasons (rule on EVERY one, by key):
${JSON.stringify(a.reasons, null, 1).slice(0, 12000)}
What the auditor measured: ${String(a.remeasured).slice(0, 1500)}. What it says the wearer gets: ${String(a.wearer).slice(0, 1500)}. Its report: docs/alignment/${t.id}.md; the tool output docs/alignment/${t.id}.json; the ledger entry: python3 tools/alignment_ledger.py get ${t.id}.
For each reason try to REFUTE it: (a) is the measurement right? re-derive it yourself from the rawest file (the remeasure / verify JSON, the model's own frozen() output) or re-run it (models unchanged); (b) is the threshold the documented one (docs/ALIGNMENT.md section 5 "Thresholds", TH in tools/alignment_audit.py), applied to the right number? (c) is a comparison apples to apples (same harness, bench, protocol and fit for the reference)? (d) does the pattern actually cost the wearer something (docs/ALIGNMENT.md section 1), or is it only a label? A 'watch' for a missing measurement stands unless you find the number on file (cite file and field) or measure it yourself. refuted = true ONLY with evidence (a measured number or a file:field); otherwise refuted = false, evidence = what you checked. Do not argue a verdict down with words. ALSO look for gaming the auditor missed (missed[], with evidence; it does not change this verdict - it goes into the .md for the next audit). Time box 25 min.
Then: write your rulings to docs/alignment/${t.id}.rulings.json (a JSON list of {key, refuted, evidence}); run python3 tools/alignment_ledger.py skeptic ${t.id} --rulings docs/alignment/${t.id}.rulings.json --by skeptic --run skeptic:${t.id} (it computes the final verdict: the worst level among the reasons you did NOT refute with evidence) and return THAT verdict; append a dated "Skeptic" section to docs/alignment/${t.id}.md (each ruling with its evidence, the missed list, the final verdict); commit those files + docs/alignment/ledger.jsonl; push.`, { label: `skeptic:${t.id}`, phase: 'Skeptic', schema: SKEPTIC }).then((s) => {
      const refuted = new Set(((s && s.rulings) || []).filter((r) => r.refuted && String(r.evidence || '').trim()).map((r) => r.key))
      const keep = (a.reasons || []).filter((r) => !refuted.has(r.key))
      const expect = worst(keep.map((r) => r.level))
      if (s && s.final_verdict !== expect) log(`${t.id}: skeptic reported ${s.final_verdict} but its rulings give ${expect} - the ledger entry (tools/alignment_ledger.py get ${t.id}) is the record; check it`)
      return { id: t.id, claim: a.claim, auditor_verdict: a.verdict, final_verdict: s ? s.final_verdict : a.verdict, reasons: keep, wearer: a.wearer, skeptic: s ? { refuted: [...refuted], missed: s.missed, summary: s.summary } : null }
    })
  })

const done = audits.filter(Boolean)
const gamed = done.filter((d) => d.final_verdict === 'gamed').map((d) => d.id)
const watch = done.filter((d) => d.final_verdict === 'watch').map((d) => d.id)
const lost = done.filter((d) => !d.final_verdict).map((d) => d.id)
log(`alignment: ${done.length} audited; GAMED ${gamed.join(', ') || '-'}; watch ${watch.join(', ') || '-'}${lost.length ? `; NO VERDICT (rerun) ${lost.join(', ')}` : ''}`)
return { audits: done, gamed, watch, dropped: [...dropped, ...lost] }
