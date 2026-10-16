export const meta = {
  name: 'generation-winner-cad',
  description: 'Generation winner CAD (CLAUDE.md "Every generation ends in a full CAD + render of its winner"): L1 keep-out CAD + judges (with a red team of any new mechanism in parallel), full user-style CAD, muscled-mannequin stills with a look audit, independent verifier',
  phases: [
    { title: 'L1', detail: 'L1 keep-out CAD + judges; red team of the new mechanism in parallel' },
    { title: 'CAD', detail: 'full user-style CAD' },
    { title: 'Render', detail: 'look audit + stills on the muscled mannequin' },
    { title: 'Verify', detail: 'independent check' },
  ],
}
// WHAT: builds the verified winner of a discovery generation (round) at the user's CAD standard and judges it.
//   Generalised from the gen-4 (minarc BDp) and gen-5 (geneva-tail rod) runs of 2026-10-16.
// WHEN: after a round's winner is VERIFIED (and, if a final polish ran, after its verifier confirmed or rejected the
//   polished config - CLAUDE.md: a polished config replaces the CAD's config only on a confirmed gain >= 1 gap point).
// ARGS (all strings unless noted):
//   gen          generation number (e.g. 6)
//   id           design id (docs/concepts/rows/<id>.json)
//   winner       one dense paragraph: what the mechanism is (joints, active / passive, complexity), the VERIFIED numbers
//                (v_gap, score, held out), the exact config / params file, and the files: row, doc, model, verify harness
//   short        short slug for new files, e.g. 'geneva' -> pipeline/concept_l1/build_<short>_l1.py,
//                pipeline/conformal/param_cad/user_style_<short>.py, designs l1_<slug> / user_<slug>
//   slug         design dir slug, e.g. 'geneva-rod' (L1 = l1_<slug>, full CAD = user_<slug with - -> _>)
//   prior_art    the closest built generation: its builders and design dirs to import / copy from (read-only)
//   new_mechanism  optional: the mechanism nothing before has built (e.g. a lobe -> rocker -> pushrod drive); gets a
//                red team + build spec in parallel with the L1
//   do_not_edit  optional: files other running workflows are editing right now
//   spend_usd    number, farm + render spend cap for this workflow (default 0.6)
//   date         YYYY-MM-DD for the render folder (no Date() in workflow scripts)
//   repo, branch, trailer   session settings (see tools/workflows/README.md)
// LESSONS BUILT IN: the full CAD must not lose R1 / R6 / R16 against its own L1 (gen-3: bars 4-11 mm above the model's
//   straps cost R1 80 -> 71 %); judges are outside judges - never edit a judge to pass; the look audit exists because the
//   user said the detailed renders "look bad" (2026-10-16).
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
const BRANCH = (args && args.branch) || 'claude/trusting-pasteur-6czobp'
const TRAILER = (args && args.trailer) || 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_014NJ3o5nJ9b1u4LXnQRjmMh'
const A = args || {}
const SHORT = A.short || A.id, SLUG = A.slug || A.short || A.id
const L1ID = `l1_${SLUG}`, CADID = `user_${SLUG.replace(/-/g, '_')}`
const L1B = `pipeline/concept_l1/build_${SHORT}_l1.py`, CADB = `pipeline/conformal/param_cad/user_style_${SHORT}.py`
const RDIR = `renders/${A.date || 'YYYY-MM-DD'}_userstyle_${SHORT}`
const SPEND = A.spend_usd || 0.6
const COMMON = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - especially "Every generation ends in a full CAD + render of its winner", "No lofts, ever", "Manufacturable joints only", "CAD has two levels", "User parts: only BOTTOM may be modified", the render look (mannequin MATTE black, faceless, muscles OK; parts bead blasted metal, polished screws, iglidur orange, NO black parts), "CAD rulings for built designs" (base DIRECTLY at the J1 hub ring, no base tab; ramps <= 60 deg with tangent bend arcs of inner radius >= 15 mm on 3 mm bent Ti, tighter only where 5-axis machined from solid and stated), O20 hubs only, "The fold margin is read in ONE metric, and stops must be buildable".
THE WINNER of generation ${A.gen}: ${A.id}. ${A.winner}
PRIOR ART (read-only; import or copy, never edit): ${A.prior_art || 'the newest builders in pipeline/concept_l1/ and pipeline/conformal/param_cad/ (user_style*.py) and their design dirs in pipeline/full-exo/designs/; docs/EVOLUTION.md lists every built generation'}. Write NEW files: ${L1B}, ${CADB}.${A.do_not_edit ? ' DO NOT EDIT (running workflows use them): ' + A.do_not_edit + '.' : ''} Use the current judges (tools/judge_all.sh <design id> [fast]; docs/research/judge_fixes_check.md lists today's judge fixes).
FARM / RENDER: CPU farm python3 tools/cloud_run.py (judge <id> [fast]); stills on the exo-blender-cycles endpoint (workersMax 1; ~$0.05 per still set) via pipeline/joint-render/film_client.py stills ... --spp 192 (docs/RENDER_RUNBOOK.md); never change that endpoint's settings, never touch pods named crl-*. Spend cap for this workflow $${SPEND} (check python3 tools/runpod_guard.py audit before a batch). Key only as RUNPOD_API_KEY="$(cat ~/.runpod_key)", never echo it. Local: niced, <= 2 processes; never pkill -f. Never message other agents. Write results incrementally.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const L1 = { type: 'object', properties: { design_id: { type: 'string' }, builder: { type: 'string' }, kin_check: { type: 'string' }, scorecard: { type: 'string' }, passing: { type: 'integer' }, issues: { type: 'string' } }, required: ['design_id', 'builder', 'kin_check', 'scorecard', 'passing', 'issues'] }
const MECH = { type: 'object', properties: { findings: { type: 'string' }, parts_list: { type: 'string' }, build_spec: { type: 'string' }, blockers: { type: 'string' } }, required: ['findings', 'parts_list', 'build_spec', 'blockers'] }
const CAD = { type: 'object', properties: { design_id: { type: 'string' }, design_dir: { type: 'string' }, builder: { type: 'string' }, parts: { type: 'string' }, kin_check: { type: 'string' }, validity: { type: 'string' }, scorecard: { type: 'string' }, vs_l1: { type: 'string' }, issues: { type: 'string' } }, required: ['design_id', 'design_dir', 'builder', 'parts', 'kin_check', 'validity', 'scorecard', 'vs_l1', 'issues'] }
const REN = { type: 'object', properties: { render_dir: { type: 'string' }, images: { type: 'array', items: { type: 'string' } }, look_audit: { type: 'string' }, cost: { type: 'string' }, notes: { type: 'string' } }, required: ['render_dir', 'images', 'look_audit', 'cost', 'notes'] }
const VER = { type: 'object', properties: { refuted: { type: 'boolean' }, issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['refuted', 'issues', 'summary'] }

phase('L1')
const [l1, mech] = await parallel([
  () => agent(`${COMMON}

YOUR TASK (time box 100 min, commit as you go): the L1 keep-out CAD of the generation-${A.gen} winner as pipeline/full-exo/designs/${L1ID}/ with a NEW builder ${L1B} derived from the prior art: member frames + clips.json with G/T per group from the VERIFIED model's exact kinematics (the verified config; every passive / slaved coordinate from the model's own law, never free); joint keep-outs = hub diameter x real stack (caps, springs, plates included); links as constant-thickness slabs at their real height; every other part (knee links, straps, bosses, pins, drives) at its real envelope; one valid solid per part (judge/part_validity.py). Check the posed L1 against the model's metal at >= 7 poses incl. the overhead peak, across-body, behind-back and the pose that exercises the mechanism's extreme. Then the judges (tools/judge_all.sh ${L1ID} or the farm judge) - report R1 / R1-aim / R4 / R6 / R16 / R17 first and compare with the previous generations' L1s (docs/EVOLUTION.md). Add the docs/EVOLUTION.md row + pipeline/evolution/ snapshot (tools/evolution_snapshot.py); events line in docs/concepts/events.jsonl.`, { label: `l1:${SLUG}`, phase: 'L1', schema: L1 }),
  () => A.new_mechanism ? agent(`${COMMON}

YOUR TASK (time box 60 min): RED TEAM + BUILD SPEC of the new mechanism in this generation: ${A.new_mechanism}. From the verified model and its doc's open items: the exact geometry (export curves / profiles the CAD needs), real catalogue parts at real size (name existing part numbers, their play), what keeps contact / preload (a real spring part), the play stack-up and what it does to the cuff and to the 5-deg fold margin, the torques and stresses in the worst pose (run real numbers in python, no hand-waving), a short parts list and a build spec the CAD agent can follow. Write docs/research/${SHORT}_mechanism_redteam.md + an events line; commit. Say plainly if anything is unbuildable at this size, and the cheapest fix.`, { label: 'redteam:mechanism', phase: 'L1', schema: MECH }) : null,
])
if (mech) log(`mechanism red team: ${mech.blockers.slice(0, 200)}`)
if (!l1) return { l1: null, mech }
log(`L1 ${L1ID}: ${l1.passing}/19 | ${l1.scorecard.slice(0, 160)}`)

phase('CAD')
const cad = await agent(`${COMMON}

THE L1 RESULT: ${JSON.stringify(l1)}. MECHANISM RED TEAM + BUILD SPEC: ${JSON.stringify(mech || {}).slice(0, 6000)}.
YOUR TASK (time box 150 min, commit as you go): the FULL user-style CAD of the generation-${A.gen} winner as pipeline/full-exo/designs/${CADID}/ with a NEW builder ${CADB} (param dict in; reuse the prior-art user_style*.py builders by import or copy - do not edit them; kinematics EXACTLY the verified model's via the L1 frames / clips - posed parts vs the model's metal within 0.5 mm at >= 5 poses; the bars must follow the model's strap height). Parts at real size, each one valid solid, line / tangent-arc sketches, extrudes, revolves, single-section sweeps along line/arc paths, fillets - NO lofts: every joint as the v5 O20 hub stack (pipeline/conformal/param_cad/user_style.py), links as bent or machined bars along the verified strap paths, stops as dowels in arc slots on the joint's own angle, pins with iglidur sleeves + DIN 6799 clips on a real groove land, base directly at the J1 hub ring, the arm side (BOTTOM cut + pad mount, cuff). Then judge/part_validity.py, the scorecard, a line-by-line comparison with the L1 (the full CAD must not lose R1 / R6 / R16 against its own L1 - if it does, find and fix the cause before rendering), docs/EVOLUTION.md + pipeline/evolution/ snapshot, events line.`, { label: `cad:${CADID}`, phase: 'CAD', schema: CAD })
if (!cad) return { l1, mech, cad: null }
log(`${CADID}: ${cad.scorecard.slice(0, 160)}`)

phase('Render')
const ren = await agent(`${COMMON}

THE BUILT DESIGN: ${JSON.stringify(cad)}.
YOUR TASK (time box 70 min): (A) LOOK AUDIT FIRST: open the previous generation's stills (renders/*_userstyle_*/, newest first) and list concretely what makes them look bad (faceting / tessellation, shading seams, floating or intersecting parts, clutter, scale cues, lighting, framing, camera, background, materials); fix what is in the render's or the CAD's control for THIS set and say what only a CAD change would fix. (B) Stills (pipeline/full-exo/shots_plan.py GRID=0.01, pipeline/joint-render/render_stills.py, film_client.py stills --spp 192) into ${RDIR}/: the new mechanism close-up, the hubs at the shoulder, the knee / pin macro with the iglidur orange, hero "Raise overhead" peak, hero "Reach a high shelf", the mechanism's extreme pose, rest from behind-lateral. LOOK at every image yourself; re-shoot anything with black-looking parts, gloss on the mannequin, or a part through the skin. README with the per-pose skin clearance and the look-audit list; commit.`, { label: `render:${SHORT}`, phase: 'Render', schema: REN })

phase('Verify')
const v = await agent(`${COMMON}

You are an independent VERIFIER (a skeptic) of the generation-${A.gen} winner's CAD and renders. L1: ${JSON.stringify(l1)}. MECHANISM: ${JSON.stringify(mech || {}).slice(0, 3000)}. CAD: ${JSON.stringify(cad)}. Renders: ${JSON.stringify(ren || {})}. Time box 45 min. Refute it if you can: (1) posed parts reproduce the verified model (model metal at >= 6 poses incl. overhead, behind the back and the mechanism's extreme, within 0.5 mm; bars vs model straps; every slaved coordinate equals the model's law); (2) every part real size and a real component; (3) NO lofts reachable from the builder; (4) re-run R1 / R1-aim / R4 / R6 / R16 / R7 / R17 yourself and compare with the scorecard; (5) look at every still: matte faceless mannequin, no black parts, no part through the skin, the design shown is this CAD, the look-audit fixes really applied. Write pipeline/full-exo/designs/${CADID}/VERIFY.md + an events line; commit.`, { label: `verify:gen${A.gen}`, phase: 'Verify', schema: VER })
return { l1, mech, cad, ren, v }
