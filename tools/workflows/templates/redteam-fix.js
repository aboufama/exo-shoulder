export const meta = {
  name: 'redteam-fix',
  description: 'Fix a failing requirement on a built design (K-hold style): measure what the failure really costs, measure candidate fixes in the same judge, re-judge before / after, builder fixes; then an independent check',
  phases: [
    { title: 'Fix', detail: 'cost of the failure + candidate fixes measured + re-judge' },
    { title: 'Check', detail: 'independent verifier' },
  ],
}
// WHAT: the pattern of pick1-k-hold (2026-10-16): the gen-4b CAD of the leader failed R17 (the knuckle K lagged its plan
//   by 9.3 deg because the spring preload outlasted the cuff tissue); the fix agent measured the lag's proximity cost
//   (none), measured four hold options in the dynamics judge, chose preload 0.04 N.m (R17 passes, 7/19), fixed builder
//   items; the checker reproduced it and red-teamed the margin (posture-dependent 4.1-7.7 deg).
// WHEN: a judge (R1-R19) or a verifier flags a failure or open items on a built design that a design / builder change
//   can fix. Not for judge bugs: a judge bug is reported and fixed only as a stated measurement change.
// ARGS (strings): id (design or row id), context (one dense paragraph: the design, its built CAD dirs, the failing
//   requirement with numbers, what is already measured, open builder items), task (the numbered task: 1 measure what the
//   failure costs; 2 candidate fixes to MEASURE (not argue), least complexity first; 3 re-judge table; 4 builder fixes),
//   out (findings doc path, default docs/research/<id>_fix.md), spend_usd (number, default 0.4), do_not_edit (optional),
//   repo, branch, trailer.
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const A = args || {}
const OUT = A.out || `docs/research/${A.id}_fix.md`
const COMMON = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - especially "Manufacturable joints only", "No lofts, ever", O20 hubs only, "The fold margin is read in ONE metric, and stops must be buildable", "Outside judges, never self-assessment", MVP1 = unpowered kinematic proof that tracks the arm.
CONTEXT: ${A.context}
Do NOT edit judge code to make a design pass; a judge bug you find is reported and fixed only as a stated measurement change.${A.do_not_edit ? ' DO NOT EDIT (running workflows use them): ' + A.do_not_edit + '.' : ''} Local: niced, <= 2 processes; never pkill -f. Farm (python3 tools/cloud_run.py) allowed, spend <= $${A.spend_usd || 0.4}; key only as RUNPOD_API_KEY="$(cat ~/.runpod_key)", never echo it. Never message other agents.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const FIX = { type: 'object', properties: { failure_cost: { type: 'string' }, options: { type: 'string', description: 'each candidate fix with its MEASURED effect in the judge' }, chosen: { type: 'string' }, rejudge: { type: 'string', description: 'before / after table' }, builder_fixes: { type: 'string' }, open: { type: 'string' } }, required: ['failure_cost', 'options', 'chosen', 'rejudge', 'builder_fixes', 'open'] }
const VER = { type: 'object', properties: { refuted: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['refuted', 'issues', 'summary'] }

phase('Fix')
const f = await agent(`${COMMON}

YOUR TASK (time box 100 min, commit as you go):
${A.task}
Prefer the fix with the least added complexity (tools/simplicity.py) and a real component. A design change is reported as one (scorecard before / after); a measurement change separately. Write ${OUT} (+ FINDINGS section, events line, EVOLUTION row if the design changed); commit.`, { label: `fix:${A.id}`, phase: 'Fix', schema: FIX })
if (!f) return { f: null }
log(`fix ${A.id}: ${f.chosen.slice(0, 160)} | ${f.rejudge.slice(0, 120)}`)

phase('Check')
const v = await agent(`${COMMON}

You are an INDEPENDENT VERIFIER (a skeptic) of this result: ${JSON.stringify(f).slice(0, 9000)}. Time box 45 min. Refute it if you can: (1) re-run the failing requirement's judge on the claimed configuration yourself (L1 and CAD if both claimed), every clip; (2) is the fix a real component at a real size, and is every curve / torque / force it relies on sourced or measured (not assumed)? (3) reproduce the failure-cost measurement on one case; (4) any gap claim: reproduce on Bench(110,360) exact frozen at margin 5 with priced stops; (5) the builder fixes really applied; no lofts reachable; (6) red team the margin: the posture, tolerance or load case where the fix stops working. Write ${OUT.replace(/\.md$/, '_check.md')} + an events line; commit.`, { label: `check:${A.id}`, phase: 'Check', schema: VER })
return { f, v }
