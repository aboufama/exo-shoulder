export const meta = {
  name: 'final-polish',
  description: 'Final polish of a verified winner (CLAUDE.md final-polish rule): CMA on a representative envelope search bench (never the held-out poses), claim on the held-out set and the verified protocol, independent verifier (held-out gain >= 1 gap point)',
  phases: [{ title: 'Polish', detail: 'envelope search bench + CMA + claim' }, { title: 'Verify', detail: 'independent verifier (held-out gain >= 1)' }],
}
// WHAT: squeezes the last points out of a verified design's free parameters. Generalised from minarc-final-polish
//   (2026-10-16: pick1 confirmed 18.40, held out +2.37 / +1.49 over BDp) after two failed polish styles: in-sample
//   polishes lost ~5 points held out because Bench(110,360) under-samples axial rotation (|axial| >= 150 deg: 6 % vs
//   11 % held out); a 2-fold cross-fit did not fix it (docs/research/crossfit_polish.md). So: search on a stratified
//   envelope sample ('env', tools/env_bench.py + tools/env_polish.py), claim held out.
// WHEN: once per generation winner, BEFORE its generation-winner CAD (or in parallel, with the CAD on the verified config;
//   a polished config replaces the CAD's config only after the verifier confirms a held-out gain >= 1 gap point).
// ARGS: id (row id), winner (string: the verified config, its params file, model, claim harness, judge harness, verified
//   + held-out numbers), seeds (string: extra start configs, optional), budget_usd (number, farm cap, default 2),
//   fields (row field prefix for the confirmed config, default 'polished_'), repo, branch, trailer.
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
const BRANCH = (args && args.branch) || 'claude/trusting-pasteur-6czobp'
const TRAILER = (args && args.trailer) || 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_014NJ3o5nJ9b1u4LXnQRjmMh'
const A = args || {}
const BUDGET = A.budget_usd || 2, F = A.fields || 'polished_'
const BASE = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - especially the polish rule at the end of "The fold margin is read in ONE metric, and stops must be buildable" (search on a representative envelope sample, claim on the held-out set), the final-polish rule under "Every generation ends in a full CAD + render of its winner" (a polished config replaces the CAD's config only after an independent verifier confirms a gain >= 1 gap point), the continuity rule, near-touch objective, margin 5 in the th metric, O20, "Keep the held-out split held out".
THE WINNER: ${A.id}. ${A.winner}
TOOLS: the envelope search bench and its polish driver tools/env_bench.py, tools/env_polish.py (docs/research/minarc_final_polish.md: how the 'env' bench was built and shown to predict held out better); bench construction tools/concept_bench.py; fast caches tools/bench_cache_farm.py; the held-out set in docs/concepts/verify/skin-normal-3r-pin-knee-polish.py; the cross-fit study docs/research/crossfit_polish.md.
Use the cloud farm for heavy runs (python3 tools/cloud_run.py, docs/CLOUD_RUN.md); local <= 2 processes. FARM BUDGET for this workflow <= $${BUDGET} total (check python3 tools/runpod_guard.py audit before each batch). Never print the RunPod key. Never message other agents. Write findings to docs/research/${A.id}_final_polish.md, a docs/FINDINGS.md section, an events line.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
phase('Polish')
const p = await agent(`${BASE}

TASK (time box 120 min): (1) SEARCH BENCH: reuse the 'env' bench (tools/env_bench.py) if its cache exists, else rebuild it (stratified envelope sample matched to the full envelope's axial / elevation / plane distribution, no pose within 2 deg of a held-out pose, plus the Bench(110,360) clip frames, never Wave / Walking); print the distribution table against held out. (2) Re-score the winner on 'env' (fit env fast -> wear env exact) next to its verified and held-out numbers. (3) CMA polish on 'env' (near-touch objective, continuity, margin 5 with stops as variables >= 5.0 priced at +0.5 tolerance, O20; starts: the verified config${A.seeds ? ', ' + A.seeds : ''}; claim-fit guard on) within budget, until the convergence gate passes (best gained < 1 point over the 2nd half of the tries, < 0.5 over the last third, top-5 within 3). (4) CLAIM: the top 3 distinct picks + the verified config in ONE farm batch through the claim harness: fit env fast -> wear held-out exact, and fit Bench(60,160) fast -> wear Bench(110,360) exact (the verified protocol), with built-stop pricing. Report the held-out gain over the verified config honestly, even if it is < 1.`, { label: `polish:${A.id}`, phase: 'Polish', schema: { type: 'object', properties: { bench: { type: 'string' }, picks: { type: 'string', description: 'table: config x (env objective, verified-protocol gap, held-out gap, held-out gain over the verified config)' }, best_id: { type: 'string' }, best_params_file: { type: 'string' }, held_gain: { type: 'number' }, cost: { type: 'string' }, issues: { type: 'string' } }, required: ['bench', 'picks', 'held_gain', 'cost', 'issues'] } })
if (p) log(`polish ${A.id}: held-out gain ${p.held_gain} | ${p.cost}`)
phase('Verify')
const v = (p && p.held_gain >= 1) ? await agent(`${BASE}

You are the INDEPENDENT VERIFIER (a skeptic) of this final-polish claim: ${JSON.stringify(p).slice(0, 8000)}. Time box 45 min. Re-run the best pick and the verified config yourself through the claim harness with built-stop pricing: held out (fit env fast -> wear held-out exact) and the verified protocol (fit Bench(60,160) fast -> wear Bench(110,360) exact); th margin from member frames (>= 5 on every taken pose); continuity (kinematic + contact-aware). Check the 'env' bench never reuses or near-duplicates (< 2 deg) a held-out pose and was not tuned on held-out outcomes. CONFIRM only if the held-out gain is >= 1 gap point on your numbers. If confirmed, write the polished config into docs/concepts/rows/${A.id}.json as ${F}* fields (never replacing the verified fields), an events line; commit.`, { label: 'verify:polish', phase: 'Verify', schema: { type: 'object', properties: { confirmed: { type: 'boolean' }, held_gain: { type: 'number' }, summary: { type: 'string' } }, required: ['confirmed', 'summary'] } }) : null
if (p && p.held_gain < 1) log(`no verifier: held-out gain ${p.held_gain} < 1 - the verified config stays`)
return { p, v }
