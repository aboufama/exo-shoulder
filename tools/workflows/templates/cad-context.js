export const meta = {
  name: 'cad-context',
  description: 'A self-contained brief of a verified design for an outside (LLM) CAD tool: geometry exported by running the verified model, written up for a reader with no repo access, checked by a numbers checker and a cold-read red team, fixed',
  phases: [
    { title: 'Extract', detail: 'geometry export from the verified model (+ hardware standard when scope is full)' },
    { title: 'Write', detail: 'the brief + data files' },
    { title: 'Check', detail: 'numbers checker + cold-read red team' },
    { title: 'Fix', detail: 'apply the checkers findings' },
  ],
}
// WHAT: the user hands a design to an outside CAD tool. Generalised from cad-context-zc-frontier-3r (2026-10-16). The
//   user then NARROWED it: "kinematics only, no CAD rules, short" - the delivered brief was
//   docs/cad_context/zc-frontier-3r/KINEMATICS_BRIEF.md + kinematics_data.json (axes through GH, joint envelopes, travel +
//   J2 stop window, link keep-out profiles, base / BOTTOM interfaces, check poses; no hardware choices). So the DEFAULT
//   scope here is 'kinematics'; scope 'full' adds the hardware / CAD standard (the long draft is kept in
//   docs/cad_context/zc-frontier-3r/provenance/ as the example).
// WHEN: only on the user's request for a design brief.
// ARGS (strings): id (row id), design (one paragraph: what it is, the VERIFIED config + params, files), request (the
//   user's words, verbatim), scope ('kinematics' default | 'full'), out (default docs/cad_context/<id>), repo, branch, trailer.
// PRIVACY (hard rule, CLAUDE.md): no skin meshes, scans, body measurements or anything from data/raw/private or the
//   personal-shoulder-diagnosis folder in the brief - the design's own geometry and clearance rules only.
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const A = args || {}
const OUT = A.out || `docs/cad_context/${A.id}`
const FULL = A.scope === 'full'
const COMMON = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding.
THE USER'S REQUEST (verbatim): ${A.request}
THE DESIGN: ${A.id}. ${A.design} Use the VERIFIED configuration (state exactly which params file / digest it is, and that it reproduces the verified number).
OUTPUT FOLDER: ${OUT}/. Everything in it must be readable by an outside CAD tool with NO repo access: plain mm, degrees, one stated right-handed frame with GH at the origin, no repo paths needed to understand it (paths only as provenance notes). SCOPE: ${FULL ? 'FULL - kinematics AND the hardware / CAD standard (O20 hub stack part by part, link standard, base at the J1 ring, BOTTOM interface, materials, no-loft rules)' : 'KINEMATICS ONLY (the user: "kinematics only, no CAD rules, short"): axes, joint envelopes, travel + stop windows, link keep-out profiles, base / BOTTOM interfaces, check poses - no hardware choices'}. Example of the delivered kinematics brief: docs/cad_context/zc-frontier-3r/KINEMATICS_BRIEF.md.
PRIVACY (hard rule): no skin meshes, body scans, body measurements or anything from data/raw/private or a personal-shoulder-diagnosis folder. The design's own geometry and the clearance rules as numbers on that geometry only. Every part except the user's BOTTOM plate (its interface is fixed geometry to mate to, not to redesign).
Never message other agents. Local: niced, <= 2 processes; never pkill -f. No farm or GPU spend needed.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const GEO = { type: 'object', properties: { frame: { type: 'string' }, config: { type: 'string' }, files: { type: 'array', items: { type: 'string' } }, skeleton: { type: 'string' }, ranges: { type: 'string' }, caveats: { type: 'string' } }, required: ['frame', 'config', 'files', 'skeleton', 'ranges', 'caveats'] }
const HW = { type: 'object', properties: { hub_stack: { type: 'string' }, links_std: { type: 'string' }, interfaces: { type: 'string' }, rules: { type: 'string' }, files: { type: 'array', items: { type: 'string' } } }, required: ['hub_stack', 'links_std', 'interfaces', 'rules', 'files'] }
const DOC = { type: 'object', properties: { doc: { type: 'string' }, files: { type: 'array', items: { type: 'string' } }, open: { type: 'string' } }, required: ['doc', 'files', 'open'] }
const CHK = { type: 'object', properties: { verdict: { type: 'string' }, errors: { type: 'array', items: { type: 'string' } }, gaps: { type: 'array', items: { type: 'string' } } }, required: ['verdict', 'errors', 'gaps'] }

phase('Extract')
const [geo, hw] = await parallel([
  () => agent(`${COMMON}

YOUR TASK (time box 45 min): EXPORT THE SKELETON GEOMETRY of the verified configuration by RUNNING its model (do not re-derive by hand) into ${OUT}/geometry.json (+ CSVs of link centrelines / keep-out profiles, + one PNG of three orthographic skeleton views: axes, hubs as discs at real size, link centrelines - no body) and ${OUT}/scripts/. Contents: the frame (how the model defines it) and the rest pose; each joint's axis unit vector, hub centre / level and stack side, joint angle at rest; the links' centrelines (every <= 2 mm), cross-sections and levels; the arm end and the BOTTOM interface; joint ranges over the taken workspace poses and the motion clips, the 5-deg fold margin in the th metric (tools/concept_kit.py lines 25-30) = where hard stops belong; 3+ key poses (overhead peak, across the body, behind the back) with joint angles and hub centres. Self-checks: axes meet at GH within 1e-6 where the design says they do; centrelines end at the hubs; exported metal reproduces the model's metal at 3 poses to <= 0.01 mm. Commit.`, { label: 'extract:geometry', phase: 'Extract', schema: GEO }),
  () => FULL ? agent(`${COMMON}

YOUR TASK (time box 40 min): EXTRACT THE HARDWARE AND CAD STANDARD the parts must follow from the repo's own built standard (docs/CAD_STANDARD.md, docs/HARDWARE.md, pipeline/conformal/param_cad/user_style.py and the newest user_style_*.py builders, their parts lists and VERIFY.md files): the v5 O20 hub stack part by part (catalogue numbers, fits, stack height, which face hub level F measures to), the link standard (bar section, bend radii, ramps), the base at the J1 ring and its interface to the scapula handler, the BOTTOM interface, materials and finishes, the no-loft rules. Write ${OUT}/_extract_hardware.md; commit.`, { label: 'extract:hardware', phase: 'Extract', schema: HW }) : null,
])
if (!geo) return { geo, hw }

phase('Write')
const doc = await agent(`${COMMON}

GEOMETRY EXTRACT: ${JSON.stringify(geo).slice(0, 12000)}
${hw ? 'HARDWARE EXTRACT: ' + JSON.stringify(hw).slice(0, 12000) : ''}
YOUR TASK (time box 35 min): write ${OUT}/${FULL ? 'CAD_CONTEXT.md' : 'KINEMATICS_BRIEF.md'} - ONE self-contained brief the user pastes into an outside CAD tool, with the data files attached. For a capable engineer who has never seen this project: what it is (5 lines); frame and units; the kinematic skeleton that must NOT change (tables + files); ${FULL ? 'the parts to design with their interfaces, governing dimensions, materials and rules; ' : ''}deliverables; acceptance checks the user can run on the output (hub centres within 0.1 mm, axes within 0.1 deg, keep-out profiles respected, no part interference over the key poses / joint ranges). Plain language, short sentences, numbers in tables; ${FULL ? 'under ~8 pages' : 'short - a few pages'}. Move scratch extracts to ${OUT}/provenance/. Commit.`, { label: 'write:brief', phase: 'Write', schema: DOC })
if (!doc) return { geo, hw, doc: null }

phase('Check')
const [c1, c2] = await parallel([
  () => agent(`${COMMON}

You are an INDEPENDENT NUMBERS CHECKER of ${doc.doc} and its data files (time box 30 min). Re-derive the skeleton yourself from the model at the verified params with your own script (do not reuse the extractor's scripts); check every number in the brief against the repo; internal consistency; the privacy rule. Report every error with the correct value. Write ${OUT}/provenance/check_numbers.md; commit.`, { label: 'check:numbers', phase: 'Check', schema: CHK }),
  () => agent(`${COMMON}

You are a COLD-READ RED TEAM (time box 30 min): read ONLY ${doc.doc} and the files it attaches as if you were the outside CAD tool with no repo access. List every ambiguity, missing number, sign convention, undefined term, contradiction, or place where two careful engineers would build incompatible parts. PROVE BUILDABILITY: with CadQuery (installed) and only the brief + files, build one link and one hub's custom parts as STEP; report where the brief did not let you proceed. Anything personal in the files? Write ${OUT}/provenance/cold_read.md (+ your script under provenance/); commit.`, { label: 'check:cold-read', phase: 'Check', schema: CHK }),
])

phase('Fix')
const fixed = await agent(`${COMMON}

NUMBERS CHECK: ${JSON.stringify(c1 || {}).slice(0, 8000)}
COLD READ: ${JSON.stringify(c2 || {}).slice(0, 8000)}
YOUR TASK (time box 25 min): fix ${doc.doc} and its data files for every confirmed error and every gap the cold read found (verify each claimed error yourself before changing a number). Keep it self-contained and short. Add a final "Known limits" section (e.g. no skin geometry by the privacy rule). Commit; return the final file list and a 5-line summary.`, { label: 'fix:brief', phase: 'Fix', schema: DOC })
return { geo, hw, doc, c1, c2, fixed }
