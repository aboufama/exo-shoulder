export const meta = {
  name: 'verify-claim',
  description: 'Independent verification of a bench claim (CLAUDE.md "Outside judges, never self-assessment"): a re-measure lens and a buildability / red-team lens in parallel, then a judge that rules and writes the verified numbers into the row',
  phases: [{ title: 'Verify', detail: 're-measure + buildability in parallel' }, { title: 'Rule', detail: 'judge' }],
}
// WHAT: two skeptics try to refute one design's claimed number from two angles; a judge takes the WORST credible
//   re-measured number as the verified one. Generalised from verify-minarc-bdp (2026-10-16), which confirmed BDp at 19.54
//   against a claimed 19.06 (buildable stop tolerance priced) - the pattern that produced every verified leader.
// WHEN: a design's own agent claims a frozen exact Bench(110,360) number that would lead (or lead its class, e.g. best
//   3-active), or a polish / re-fit claims a gain. The discovery loop's exo-screen.js already verifies what it screens;
//   use this for claims made outside the loop (Track work, re-fits, embodiment changes).
// ARGS (strings): id (row id), claim (one dense paragraph: config + params file, model + claim harness, the claimed
//   numbers: fit protocol, frozen exact gap, near-touch, held out, min th margin, continuity, complexity, active DOF),
//   lead (the verified leader to beat, with its held-out number under the same harness), prefix (row field prefix for the
//   verified numbers, default 'v_'), extra (optional design-specific checks), repo, branch, trailer.
// THE PROTOCOL A CLAIM MUST SURVIVE (CLAUDE.md): fit Bench(60,160) fast -> wear the FROZEN shape on Bench(110,360)
//   EXACT; margin 5 deg in the th metric (tools/concept_kit.py lines 25-30); O20 hubs; near-touch reported; continuity
//   flood fill for any passive / sprung / redundant coordinate; stops on a joint's own angle and priced; held-out set
//   never used for fitting.
const REPO = (args && args.repo) || '/home/user/exo-shoulder'
if (!args || !args.branch || !args.trailer) throw new Error('args.branch and args.trailer are required: your session branch and the two commit-attribution lines your system reminder gives, joined by \\n (tools/workflows/README.md)')
const BRANCH = args.branch
const TRAILER = args.trailer
const A = args || {}
const P = A.prefix || 'v_'
const BASE = `REPO ${REPO} (branch ${BRANCH}). CLAUDE.md is binding - especially "The fold margin is read in ONE metric, and stops must be buildable", the continuity rule, the near-touch rule, "Manufacturable joints only", the golden-target rulings (margin 5, O20 only, J1 seats back + acromion top), the DOF cap (<= 4, 3 preferred).
CLAIM UNDER TEST: ${A.id}. ${A.claim}
VERIFIED LEADER TO BEAT: ${A.lead || 'read docs/HANDOFF.md and the rows with status "verified"'}. Score = 100 (1 - gap/275).
You are an INDEPENDENT VERIFIER, a skeptic: default to refuted when the evidence is not there; re-run, never trust. Write your own harness under docs/concepts/verify/${A.id}-<lens>.py and findings in docs/concepts/verify/${A.id}-<lens>.md. Use the cloud farm (python3 tools/cloud_run.py; bench cache linked; docs/CLOUD_RUN.md) for heavy runs and up to 2 local processes (nice, OMP_NUM_THREADS=1). Never print the RunPod key. Time box 45 min; report early with what you measured if a run will not finish. Never message other agents.
GIT: commit only your own files: git add <paths> && git commit -m "<msg>" -- <paths>, message ending with the two lines
${TRAILER}
then git push -u origin ${BRANCH} (on rejection: git pull --rebase --autostash, push again, up to 4 tries). No model names in commits or files.`
const V = { type: 'object', properties: {
  refuted: { type: 'boolean' }, v_gap: { type: 'number' }, v_gap_near1: { type: 'number' }, v_reach: { type: 'number' }, v_follow: { type: 'number' }, v_inband14: { type: 'number' }, v_contact: { type: 'number' },
  held_out_gap: { type: 'number' }, min_th_margin_deg: { type: 'number' },
  issues: { type: 'array', items: { type: 'string' } }, evidence: { type: 'string' },
}, required: ['refuted', 'v_gap', 'held_out_gap', 'issues', 'evidence'] }
phase('Verify')
const lenses = [
  { key: 'remeasure', brief: `LENS: RE-MEASURE. (1) Your own frozen protocol: fit Bench(60,160) fast -> wear Bench(110,360) EXACT, margin 5, O20, with the claim's params - compare to the claimed numbers (plain and near-touch: metal < 1 mm counted as contact). (2) Measure the J1-J3 margin th YOURSELF from the member frames for every taken pose in every state the mechanism has. (3) Continuity: your own flood fill from the rest region over the full grid, 2-deg slerp edges, no joint / passive step > 10 deg, no branch change (connected() in docs/concepts/models/stop-relay-rocker-3r.py), and the contact-aware version (taken poses only); reach on the CONNECTED set. (4) Held out on the disjoint held-out poses (docs/concepts/verify/skin-normal-3r-pin-knee-polish.py), with the verified leader side by side under the same harness. The claim stands only if your margin-5 frozen exact gap is within 1.0 of the claim or better, min th >= 5 on every taken pose, connected = static, and the held-out number is reported honestly.${A.extra ? ' ALSO: ' + A.extra : ''}` },
  { key: 'build', brief: `LENS: BUILDABILITY AND RED TEAM. Read the model line by line. Check: (1) every joint maps to a real component at its real envelope (tools/hardware_catalogue.json, docs/research/passive_dof_hardware.md) and is sampled as metal like tools/concept_baseline.py; (2) every stop is a real dowel-in-arc-slot on the joint's OWN angle between the two bodies it connects, priced at a buildable tolerance; (3) every passive / sprung / slaved coordinate is determined (unique state from the same arm pose approached from different directions; springs: stress and torque vs demand with real parts); (4) the active DOF count against the cap (<= 4, 3 preferred) and the complexity count (tools/simplicity.py); (5) red team: the pose that jams, the point that pinches (min metal-skin distance and where), the optimistic number (anything the claim harness did that the protocol forbids). Re-measure the frozen gap yourself only to price an issue. Refute if any issue costs > 3 gap points or the mechanism is not buildable as modelled.${A.extra ? ' ALSO: ' + A.extra : ''}` },
]
const res = await parallel(lenses.map((l) => () => agent(`${BASE}\n\n${l.brief}`, { label: `verify:${l.key}`, phase: 'Verify', schema: V })))
phase('Rule')
const rule = await agent(`${BASE}

You are the JUDGE combining two independent verifications of ${A.id}: ${JSON.stringify(res).slice(0, 30000)}.
Rule: CONFIRMED only if neither lens refutes it; the verified number is the WORST credible re-measured frozen exact Bench(110,360) gap at margin 5 with the continuity rule (and any priced mechanism issue added). Write ${P}gap, ${P}gap_near1, ${P}reach / follow / inband14 / contact, ${P}held_out, ${P}min_th and the verdict into docs/concepts/rows/${A.id}.json (merge, never rewrite the row; status "verified" if confirmed, keep "screened" + refuted_by otherwise), a docs/FINDINGS.md section, an events line (kind "milestone"), a docs/EVOLUTION.md row if confirmed; commit + push. Return the ruling with a 100-word plain-language note for the user (what was confirmed, the number, held out vs the leader, the cost in joints / complexity).`, { label: 'rule', phase: 'Rule', schema: { type: 'object', properties: { confirmed: { type: 'boolean' }, v_gap: { type: 'number' }, score: { type: 'number' }, held_out_gap: { type: 'number' }, summary: { type: 'string' }, user_note: { type: 'string' } }, required: ['confirmed', 'v_gap', 'score', 'summary', 'user_note'] } })
return { lenses: res, rule }
