# Brief for the concept agents (lead: the main session)

Repo /home/user/exo-shoulder (branch claude/exo-shoulder-mechanism-wy35fx). Read first: CLAUDE.md (hard rules),
REQUIREMENTS.md (the 19 requirements, the user's decisions incl. today's ACTIVE-DOF rule), docs/FINDINGS.md (what we
learned the hard way), docs/concepts/README.md (this stage), docs/HARDWARE.md (the O20 bearing joint), README.md Status.

THE PROBLEM: a right-shoulder exoskeleton for a 185 cm man, MVP1 unpowered (the arm drives it; rolling bearings; the
user adds rotation sensing; MVP2 powers it with remote motors on cables), whose WHOLE mechanism rides within ~1 cm of the
skin (pass: >= 90 % of the covered skin 2-14 mm from the metal; aim 2-10 mm) over the full range of motion (overhead
most of all), never touching the skin, follows >= 95 % of motion frames, reaches >= 90 % of everyday arm poses, at most
4 DOF, target exactly 3 ACTIVE DOF (passive arm-driven elements such as a cuff slide whose position is set by the
chain's closure do not count), base on the user's own scapula handler (rides the scapula; a separate part), the user's
arm parts (cuffs, BOTTOM bar) stay (only BOTTOM may be modified), titanium links as thin as strength allows, mass
<= 500 g, CAD to the user's standard (docs/CAD_STANDARD.md). Fundamental difficulties found so far: rigid links over
skin that moves and bulges with the pose (deltoid, acromion, axilla); the GH centre translates relative to the thorax
(and the base slips over the scapula: ~15 mm, R10); joint hubs stack height (~12 mm) sits off the skin; links of a
spherical chain must clear every pose of the workspace, which pushes them off the skin; an undriven spare joint sags
unpowered (R17 kills redundant chains unless something sets the extra coordinate).

YOUR JOB: explore ONE assigned family (below) as a mechanism designer - reason geometrically, look for the version of
that family that best fits this body and these goals, include weird variants if they might work - then MEASURE an
idealised model with tools/concept_bench.py (read its docstring; same poses and metrics for every family; use
Bench(n_clip=60, n_ws=160) for screening, one process, OMP_NUM_THREADS=1 - 4 cores are shared by many agents; a run
takes a few minutes). Idealised = real thicknesses / hub sizes / stack heights but no CAD detail. Compare honestly with
the baseline family in docs/concepts/README.md, and run the SAME bench on a simple version of the baseline (spherical
3R: links as 8 mm x 3 mm straps riding ~6 mm over the rest-pose skin on great-circle arcs) so the numbers are
comparable. Do not touch the GPU, the CAD pipeline files or the judges. Write docs/concepts/<family>.md (idea, sketch
PNG under docs/concepts/img/, DOF count with reasoning, bench numbers, limits, unpowered behaviour, manufacturability,
and a parameterisation for a short GPU sweep: which parameters, ranges, what the evaluator would need), and append one
row to docs/concepts/families.json (create it if missing: a JSON list of {family, variant, active_dof, passive_dof,
reach, follow, inband14, inband10, contact, verdict, notes}; re-read right before writing - other agents append too).
Time box ~75 min; report early if the family is clearly dead (with the measured reason).
Git: one shared working tree - git add only your files; `git push -u origin claude/exo-shoulder-mechanism-wy35fx`
(if rejected: `git pull --rebase --autostash` then push); commit message ends with
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01HShoE3xJTcjMWRx4v2yePx
Final report: the best variant's numbers vs the baseline's on the same bench, the verdict (worth a GPU sweep or not),
and the sweep parameters.
