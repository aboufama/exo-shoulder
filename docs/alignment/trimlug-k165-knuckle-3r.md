# Alignment audit: trimlug-k165-knuckle-3r

Hourly auditor run, 2026-10-18 21:22-21:45 UTC. It was due because the row was committed at 2026-10-17 15:21:40Z
(8f69bd6, a complexity refresh), after the last audit at 13:18:11Z.

- Ledger entry: 2026-10-18T21:36:35Z, `by auditor`, run `audit:trimlug-k165-knuckle-3r`, git 175622c.
- Checks: `docs/alignment/trimlug-k165-knuckle-3r.json` (tool VERSION 2026-10-18.1, `--ref slipper-nose-knuckle-3r`).
- Findings: `docs/alignment/trimlug-k165-knuckle-3r.findings.json` (9, all watch).
- The earlier auditor sections (2026-10-17 12:46-13:07) are replaced by this one. The 2026-10-17 Skeptic section is
  kept below the rule.

## Verdict: WATCH

No reason reaches gamed. The number is its parent's, honestly reported. Nothing here ranks the design above one that is
better for the wearer.

- **The claim:** v_gap 18.51 (score 93.27), frozen exact Bench(110,360), verified 2026-10-17 12:25 UTC. Held out 23.47.
- **What changed since the last audit:** only the row's complexity record (22.25 -> 18.25: the cuff knee's closure loop
  is now recorded under `cuff_knee`). That is the fix for the last audit's NEW-stale-complexity-ruler. The tool's
  `complexity` check now reads 18.25 = 18.25.
- **Unchanged since the 12:52 re-wear:** the model, its parent model, the kit, the bench and the verifier. `git log`
  shows no commit to any of them since 12:00 on 2026-10-17.
- **Re-worn anyway at HEAD 9028dec:** bench 18.51. 0 of 470 poses differ from the committed dump in metal floor, taken
  or contact (`remeasure/trimlug-k165-knuckle-3r_bench*.json`, 147 s, local).
- **The ranking has moved under it.** The 3-active leaders are now conecut-knee-knuckle-3r and its two siblings at
  18.28. This row is 18.51, behind its own parent slipper-nose (18.49) by 0.02 (`docs/dashboard/data/morphs.json`).
- **New this hour, measured:**
  - **(a) The stated wall.** The "1.5 mm wall" that the trim depends on holds at the lug's mid-plane only. Kept at the
    lug's top edge instead, the score does not move: 18.50 against 18.51. But a third of the bench depth gain goes away,
    and two fifths of the held-out gain (NEW-wall-plane).
  - **(b) R17 on the built CAD.** It now exists, so M5 is measured instead of open. The spring holds. The cuff twist sits
    0.44-0.96 deg under its 5-deg gate.
  - **(c) The stock O2.5 dowel.** With the stock dowel nose that the CAD builds (r 1.25 against the claim's 1.1839), the
    claim holds: 18.51, T5 13.12 mm.

## What the wearer gets

Measured on Bench(110,360) exact unless stated. "This audit" means re-worn at HEAD.

| quantity | value | file |
|---|---|---|
| reach, taken / 360 | 261 (0.725), the parent's pose for pose | `remeasure/trimlug-k165-knuckle-3r_probe_bench.json` (this audit) |
| overhead, elev >= 140 | 8 / 28 (0.286): 5/13 at 140-160, 3/15 at 160-200; held out 18 / 71 | same, `ws_reach_by_elev`; `_probe_held.json` |
| why overhead poses are lost | fold 14, knee slide 4, contact 2 | same, `ws_overhead_why_not` |
| raised arm, elev 90-140 | 38 / 85 (0.447): 26/51 at 90-120, 12/34 at 120-140 | same |
| taken poses with metal < 1 / 2 / 3 mm | 3 / 30 / 100 of 371 (min 0.072 mm); held out 14 / 67 / 200 of 852 (min 0.33) | `remeasure/..._bench.json` deep (this audit), `_held.json` |
| overhead taken poses with metal < 2 / < 3 mm | 4 of 8 / 8 of 8; held out 10 / 18 of 18 | `ws_overhead140` floor counts |
| near-touch gap, 1 / 2 / 3 mm | 20.14 / 33.02 / 83.17; held out 26.56 / 36.97 / 79.28 | same |
| contact, bench | 2 poses. 237 (15, 165, -60): 9.00 mm, the crank (the lug group 8.35, hub K 2.65). 264 (30, 165, -60): 4.18 mm, the lug top (the parent 5.74). Sum 13.18 mm | `remeasure/..._bench_perpose.json`, row t5 |
| contact, held out | the parent's same 10 poses, sum 40.59 mm (the parent with the same dense lug 46.35). Deepest 9.06 mm at (30, 165, -45), the crank. 7 deeper than 3 mm | `remeasure/..._edgewall.json` |
| contact depth with the 1.5 mm wall kept at the lug's top edge | bench 13.44 / 13.70 mm, held out 41.85 / 42.89 mm (r_trim 21.72 / 21.98), gap 18.50 | `remeasure/..._edgewall.json`, `_bench_edgewall2.21.json` |
| workspace in-band (unscored, all taken ws) | 0.8559; 14.2 % of metal above 14 mm (p95 17.8, max 30.8) | `ws_unscored` |
| raised-arm in-band (unscored, elev 90-140) | 0.8002; 19.9 % above 14 mm (p95 20.16, max 30.8); held out 0.8218 | `ws_elev90_140` |
| built CAD (user_trimlug_k165) | R1 81.3 %, R1-aim 47.6 %, R4 73.4 %, R6 0.0 mm, R16 64.2 %, R17 PASS; 8 of 19 | `pipeline/full-exo/designs/user_trimlug_k165/judge/scorecard.md` |
| springs | one clock spring on K, 0.08 N.m preload + 0.015 N.m/rad. R17 nominal: K off its law 0.136 deg, follower lift-off 0 | `.../user_trimlug_k165/judge/dynamics.json` |
| cuff twist | 4.04 deg nominal (gate 5.0); forward-stroke bound 4.56 deg at mu 0.087, 5.0008 at mu 0.15 (FAIL) | same; `user_slipper_nose/judge_m5/forward_bound_mu*.json` |
| cuff force, moment about GH | 0.58 N, 0.129 N.m nominal; plain-bearing friction (mu 0.06) is not free: 12.0 N, twist 20.4 deg | same |
| stops and knee | knee 86.2-151.9 deg in its 25.2-154.8 window (2.9 deg from the stop). K stroke taken 45.62 of 49.8 deg | probe extras |
| fold margin (th, the rule's reading) | 5.181 deg bench, 5.006 deg held out. A linear K-phase stack gives 4.996 | `verify/..._v_held_frozen.json`; CAD check D2 |
| near-singular postures | with K at rest, m_sub under 5 deg on 106 of 204 rest poses, under 1 deg on 50, min 0.000 | `remeasure/..._msub_rest_bench.json` |
| stock dowel (r 1.25, as built) | 18.51, T5 13.12 mm, dK_lim 49.5 | `remeasure/..._bench_r125.json` |
| complexity | 18.25 (recomputed = row) | `tools/simplicity.py` via the `complexity` check |

**Numbers I could not get, and why:**

- **The bench gap with the real lobe follower, lobe ring and straddle boss sampled** (S3). No bench model of those parts
  exists. Only the built CAD's judges read them.
- **The held-out gap at the top-edge wall.** I measured the 10 held contact poses only. The full held set is 852 + 302
  poses, about 12 minutes locally, and the farm is closed: its $8 budget is spent.
- **Contact depth on a real, bulging arm.** The skin model is rigid.
- **R17 with the real nose friction measured.** The pass line mu <= 0.105 rests on a wear test that has not been run.

## Findings

### NEW-wall-plane (watch, new): the "1.5 mm wall" is read at the lug's mid-plane only

- **Evidence.** The trim cuts the horn lug at r_trim = the farthest flank contact + trim_wall. The model reads that
  contact at the lug's mid-plane (`docs/concepts/models/trimlug-k165-knuckle-3r.py` lines 84-96: 19.77 + 1.5 = 21.27 mm).
  The gen-7 CAD check (`docs/research/user_slipper_nose_fix_check.md` O2) reads the same contact line at the lug's top
  edge, +1.5 mm along ez:
  - the farthest contact is 20.22 mm over [0, dK_lim 49.75], and 20.48 mm over the built 51.75-deg stroke;
  - so the wall the built part keeps is 1.08 mm, or 0.82 mm over the built stroke;
  - the verifier's trim check T1 reads 2.53 / 1.99 mm on its own construction (rings +-1.25 mm along the GH ruling).

  The two independent readings disagree.
- **Measured here** (`tools/alignment_trimlug_edgewall.py`, a new file; the model unchanged, only `trim_wall` varied):

  | trim_wall (r_trim) | what it is | bench T5 (pose 264) | held T5, 10 contacts | Bench(110,360) gap |
  |---|---|---|---|---|
  | 99 (none) | the parent, with the same dense lug | 14.74 (5.74) | 46.35 | 18.49 (verifier control) |
  | **1.5 (21.27)** | **the claim: 1.5 mm at the mid-plane** | **13.18 (4.18)** | **40.59** | **18.51** |
  | 1.95 (21.72) | 1.5 mm at the top edge, over [0, dK_lim] | 13.44 (4.44) | 41.85 | - |
  | 2.21 (21.98) | 1.5 mm at the top edge, over the built stroke | 13.70 (4.70) | 42.89 | 18.50 |

- **Why the exo is not as much better as stated.** The design exists for contact depth.
  - On the bench, 0.26-0.52 mm of its 1.56 mm gain is metal cut out of the stated wall at the lug's top edge (17-33 %).
  - Held out it is 1.26-2.30 mm of the 5.76 mm gain (22-40 %).
  - The CAD keeps 0.82 mm, not 1.5, between the nose's last contact and the cut edge.
- **Why it is only watch.**
  - The score is blind to depth. It charges the trim +0.02, and with the wall at the top edge it would read 18.50.
  - The design ranks behind its parent.
  - No wall rule exists.
  - The MVP1 nose load (5-15 N, clock spring) is trivial for 0.8 mm of Ti.
- **Action.**
  - The row, the doc and the drawing state the wall as built: >= 0.8 mm at the top edge, as the CAD check asks.
  - Otherwise move the cut to r_K 21.98 and report the depth gain that a true 1.5 mm wall leaves: 1.04 mm on the bench,
    3.46 mm held out.
  - The verifier's T1 and the CAD check's O2 should be reconciled to one construction.

### T5 (watch, carried): depth-blind contact

Reproduced at HEAD. Bench: 2 contacts, sum 13.18 mm against the parent's 14.74 (dense lug). Held out: the same 10
contacts, sum 40.59 mm against 46.35. Four of them are 0.94-1.72 mm shallower. The deepest is 9.06 mm, the crank,
unchanged. The score charges +0.02 for the improvement, and part of the improvement is the wall reading above. T5 is
never gamed (user 2026-10-17).

- **Action:** none for this design. Clearing pose 264 needs the lug to end at r_K ~18 (dK ~35, the stroke wall), a
  ~0.5 mm narrower crank tip and a ~0.3 mm flat on hub 2.

### M5 (watch, carried, now measured; G3 from the wearer's side): the spring holds, the twist is near its gate

R17 has now run on the built CAD (`pipeline/full-exo/designs/user_trimlug_k165/judge/dynamics.json`, 18:39). It passes
nominal, on rolling bearings at mu 0.005:

- cuff twist 4.04 deg against the 5.0 gate;
- cuff force 0.58 N, M_GH 0.129 N.m;
- K off its law by 0.136 deg, follower lift-off 0.

These match user_slipper_nose to 0.005 deg: the drive is shared, and the glb differs in link 1a only.

The shared drive's forward-stroke bound (`user_slipper_nose/judge_m5/forward_bound_mu*.json`) reads:

| nose mu | 0.087 (the claim's) | 0.105 | 0.12 | 0.15 |
|---|---|---|---|---|
| twist (deg) | 4.56 | 4.68 | 4.79 | 5.0008: **FAIL** under the unrounded gate (8f69bd6) |

With plain-bearing friction (mu 0.06 at the hubs) the chain does not move freely: twist 20.4 deg, force 12.0 N, follower
lift-off 25 %.

- **Why it matters:** the twist the wearer feels sits 0.44-0.96 deg under its gate. It needs rolling bearings and a
  greased nose at mu <= 0.105, an untested wear assumption.
- **Why only watch:** the gate passes as built and modelled. The drive is the parent's (its M5 was upheld at 16:27), so
  the trim neither buys this nor fixes it.
- **Action:** run the nose wear test (pass line mu <= 0.105) before any claim of "moves freely" on the slipper family.

### T3 (watch, new on this row): the held-out fold margin is 0.006 deg above the rule, and the build tolerance decides it

- **Evidence.**
  - The held-out th margin is 5.006 deg (`verify/trimlug-k165-knuckle-3r_v_held_frozen.json`); the bench reads 5.181.
  - The CAD check (lines 94-100, D2) reproduces the lead's 17:20 ruling: at the drawn K-phase low end a linear stack
    gives -0.12 deg of K and a held-out th of 4.996, which puts 1 held-out pose under 5.
  - The band holds only on an RSS stack, and the drawing does not say RSS.
- **Why only watch.** The margin is read on th, the rule's own angle, so this is not the T3 exploit. It is a claim that
  lives at the rule's edge. This was the 13:18 skeptic's "missed" item 1, and the parent's T3 was upheld.
- **Action:** the drawing states RSS, or the K lead moves up 0.02 deg.

### G4 (watch, carried): near-singular sub-chain with K at rest

Unchanged. With K at rest on stop A, m_sub is under 5 deg on 106 of 204 rest poses and under 1 deg on 50, with a
minimum of 0.000 deg at (15, 75, 15). The claim's fold reading takes m_plain at rest (min 5.389). B1 is still open with
the user (`docs/HANDOFF.md` line 309).

- **Action:** the user's ruling on B1.

### T1 (watch, carried from the parent's upheld T1; G1): metal at 1-3 mm

- 30 of 371 taken bench poses have metal under 2 mm, and 100 have it under 3 mm.
- Overhead, 4 of the 8 taken poses are under 2 mm and all 8 are under 3 mm.
- 14.51 gap points live in the 0-2 mm shell, just under the tool's 15-point line.
- This row is identical to its parent pose for pose.

Reported only (user 2026-10-17: near-touch is not a gate).

### NEW-ws-inband (watch, carried): the raised-arm standoff the score does not read

On the taken workspace poses at elev 90-140, 0.8002 of the metal is in band and 19.9 % is above 14 mm. Held out it is
0.8218. The scored clip in-band is 0.8953. The built CAD reads R1 81.3 % against its L1's 82.0. The trim does not touch
this.

- **Action:** none for this design; the proposal stands on the parent's audit.

### S3 (watch, new on this row): the real follower, lobe ring and straddle boss are not sampled

The drive red team (`docs/research/slipper_mechanism_redteam.md` lines 53-56 and 183-186) found these parts unsampled by
the claim's model:

- the modelled lobe follower (s_arm 4.0 on r 8.27) lies inside hub 2's O20;
- the real follower is an MR63ZZ on a 6.5 mm arm, with the lobe ring at r 10.79-12.77;
- the real lobe ring, the follower plate and the 10 mm straddle boss are not sampled.

The built CAD carries them and is judged as drawn: R6 0.0 mm, R1 81.3 %, R16 64.2 %. The bench gap with them sampled is
not on file. This was the 13:18 skeptic's "missed" item 2, and it applies to the whole family.

- **Action:** sample the three parts in the family's bench model, or state the CAD as their only reading.

### R1 (watch, carried): the row's text

Unchanged since the skeptic upheld it at 13:18:

- the verdict still begins "screened -" on a verified row;
- it says "5 of them the lug, each 1.2-1.7 mm shallower" (measured: 4, 0.94-1.72 mm);
- the headline gap 13.02 / reach 0.775 are Bench(60,160) fast;
- the dashboard shows those, with contact 0.0, and a sweep best of 13.02 (score 95.27, above the user's 95 line);
- n_configs reads 45 against 31 sweep entries;
- the limiter leaves out the lug at 237.

New: the name and the verdict state a "1.5 mm wall" that the part keeps at its mid-plane only. None of it moves the
verified number.

- **Action:** correct the row text. That is the writer's job, not the auditor's.

## Not carried from the last audit (measured)

- **S1** was refuted by the skeptic: the held-out drop is +4.96, under the 6-point line, and every interval includes 0.
  The leaderboard has also moved (conecut-knee 18.28 leads the family), so the pairing with sidecar-longdyad no longer
  decides a winner.
- **NEW-stale-complexity-ruler** was refuted by the skeptic, and the lead has fixed it: the row reads 18.25 and the
  `complexity` check reads ok.
- **idle** was the instrument's false positive, refuted three times. The tool now reads ok: K moves 45.61 deg, the crank
  19.3.
- **continuity** is still a tool watch: "no flood on file" in a shape it reads. The flood is on file and clean (full
  18.51, 0 dropped; `remeasure/trimlug-k165-knuckle-3r_flood_bench.json`), and the skeptic refuted it. This is
  proposal I-b, still not applied.

## Tool checks, read

| check | level | reading |
|---|---|---|
| held_out | ok | 23.47 vs 18.51 (+4.96) |
| fast_frozen | ok | 13.02 -> 18.51 (+5.49) |
| near_touch | ok | 18.51 / 20.14 / 33.02 / 83.17; shell 14.51; band 3-14 18.66 |
| contact_depth | ok | bench 13.19 vs 14.75 (x0.89), held 40.58 vs 46.12 (x0.88) |
| dominance | ok | vs the parent: plain -0.02, 2 mm +0.00 |
| density (new, VERSION 2026-10-18.1) | ok | roller 4.55x the kit's density. Re-weighted, the bench reads 18.58 and held 23.54: +0.07 each, under the 0.1 line |
| complexity | ok | 18.25 = 18.25 |
| reporting | watch | see R1 |
| continuity | watch | instrument reading (above) |
| idle, sampling, fold_margin, judge_change, rules | ok | |

## Patterns walked and found absent

- **T2:** reading the band as 3-14 mm costs +0.15 (18.66).
- **T4:** no bound moved. The knee window and the stops are the parent's.
- **S2:** part-weighted in-band is 0.924 against 0.895 sample-weighted. L1a has 8 samples, as the parent.
- **S4:** not measurable here (the rig's R2 artefact, 24.87).
- **S5:** the flood is clean (full 18.51, 0 dropped).
- **M1 / M2:** no virtual part; O20 hubs.
  - The claim's nose r 1.1839 (an O2.37 dowel) is not a stock part, but the stock O2.5 that the CAD builds holds the
    claim: 18.51, T5 13.12 mm (`remeasure/..._bench_r125.json`, this audit).
- **M3:** the verifier wore the dense lug against every member: crank 0.153 mm (the designed running gap), nose 0.424 mm.
  The CAD reads R6 0.0 mm.
- **M4:** K 45.6 deg, crank 19.3 deg.
- **P1 / P2:** the held-out set was never searched. The pick (wall 1.5) is not the best-T5 column (wall 1.0: 12.67 /
  38.71).
- **P3:** four wears of the claim are identical: verifier farm, verifier local, the 13:06 audit, and this audit at HEAD.
- **P4:** the commits since the verification touched the row's complexity only. `judge/dynamics.py` (8f69bd6, R17
  unrounded) changed in the same commit as the row's complexity refresh. It is a stricter gate, stated as a measurement
  change, and it does not touch v_gap.
- **R2 / R3 / R4:** the dashboard v_gap is the verified 18.51 and v_contact is 0.0054. The grid spread is reported
  (13.00-13.40 fast).
- **G2:** the spring is 0.08 N.m and R17 passes at 0.129 N.m about GH.
- **G5 / G6:** 3 active joints, 0 passive translations, complexity recomputed.

## New pattern (proposed catalogue entry)

**NEW-wall-plane: a margin stated on one plane of a 3-D part.** Proposed for the next free number in section 2 (T6 and M6 are
already taken by other audits' proposals); T family, the margin is read where it is largest.

- **Looks like:** a wall, clearance or edge margin is quoted as one number ("+ 1.5 mm wall", "0.3 mm rule") but read on
  one section of a part whose contact line or skin distance varies across its thickness.
- **Why not better:** the built part fails, or touches, at its worst section, not at the section the model reads.
- **Detect:** for every stated margin, the claim reports its minimum over the part's thickness (top / mid / bottom
  section, or the swept contact line at both faces), and a CAD check of the built part repeats it.
- **Here:** trimlug's 1.5 mm wall is 1.08 / 0.82 mm at the lug's top edge (CAD check O2). Honouring it there costs 0.52
  of the 1.56 mm bench depth gain and 2.30 of the 5.76 mm held-out gain, and moves the gap -0.01
  (`remeasure/trimlug-k165-knuckle-3r_edgewall.json`).

## Proposals (not applied; measurement or reporting changes for the lead or the user)

- **W-a (reporting, tightening).** State every design wall or clearance at its worst section.
  - Measured effect on every verified row: only this row carries a stated trim wall (`grep trim_wall
    docs/concepts/rows/*.json`).
  - Here: gap 18.51 -> 18.50, T5 13.18 -> 13.70 mm, held contact depth 40.59 -> 42.89 mm.
  - No other verified number moves.
- **I-b (tool reading, still open).** `continuity` should read `docs/alignment/remeasure/<id>_flood_*.json` when its
  `frozen.gap` reproduces the claim. Effect here: watch -> ok.
- **R-a (reporting, still open).** Keep fit-bench numbers (13.02 / 0.775 / contact 0) out of the headline gap and reach
  columns of verified rows and the dashboard.

## What happens next

- **The CAD drawing:** state the lug's top-edge wall (>= 0.8 mm), or move the cut to r_K 21.98 at no cost to the score.
- **The nose wear test:** mu <= 0.105 is the line between "moves freely" and a 5-deg cuff twist at the end of the
  forward stroke.
- **The user's B1 ruling** (m_sub at K's rest) still decides G4 for the whole slipper / roller family.
- **The next audit** of this row is due when its claim, its parent's model, or the wall reading changes.


## Skeptic (2026-10-18 21:47-22:02 UTC, on the 21:22-21:45 auditor run)

Ledger: `skeptic:trimlug-k165-knuckle-3r`, 2026-10-18T22:01:48Z. Rulings: `docs/alignment/trimlug-k165-knuckle-3r.rulings.json`
(this run's; the 2026-10-17 rulings it replaces are in git history). New measurement:
`docs/alignment/remeasure/trimlug-k165-knuckle-3r_topedge_skeptic.json` (the model's own `_flank()`, fit Bench(60,160)
fast, model unchanged, local, about 60 s).

**Final verdict (computed by the ledger): WATCH.** Refuted 4 (continuity, NEW-wall-plane, T5, T1); upheld 7
(reporting, M5, T3, G4, NEW-ws-inband, S3, R1).

| key | ruling | evidence |
|---|---|---|
| continuity | **refuted** | `remeasure/..._flood_bench.json` frozen.gap 18.51 = claim; connected_full 18.51, 0 dropped, 128/128 forced poses connected; knn 20.18 (+1.67 <= conn_gamed 3.0). Model and kit unchanged since that wear. The watch is the tool not reading `*_flood_*.json` (proposal I-b). |
| reporting | upheld | row status verified, verdict 'screened - ...'; morphs.json sweep_gap / gap 13.02 (score 95.27) beside v_gap 18.51. |
| NEW-wall-plane | **refuted** | Re-derived on the model's flank, 1.5 mm out along the GH ray (the lug's top face): over [0, dK_lim 49.75] contact r_K 20.249, wall 1.021 mm (the CAD check's 20.22 / 1.08 reproduced). Over the K the scored poses use: bench k <= 45.5, wall 1.587 mm; held k <= 46.25, wall 1.489 mm. The stated 1.5 mm holds at the top face on every scored pose (to 0.011 mm). The thinner walls are at K 46.3-51.75, which no taken pose reaches. So the extra metal of trim_wall 1.95 / 2.21 carries no contact on a scored pose. No wearer cost is given or measured. The verifier and the CAD check do not disagree: they read opposite faces (underside 18.74 here, verifier 18.739). The rule's text over [0, dK_lim] is wrong at the top face: carried in R1. |
| T5 | **refuted** | Depths reproduce (bench 13.19 mm / 2, held 40.58 mm / 10, max 9.06). The documented line (>= 2x and >= 5 mm, reference = the current lead since tool 2026-10-17.5) is not met: conecut-knee 20.24 / 60.97 mm, so trimlug is x0.65 / x0.67. Against the parent x0.89 / x0.88, and the tool's contact_depth reads ok. Only the retired reference (sidecar-longdyad, x2.12) met it. |
| M5 | upheld | dynamics.json nominal: twist 4.04 deg, 0.58 N, K law error 0.136 deg, lift-off 0; mu 0.06 plain: 20.37 deg, 12.0 N. Correction: the pass line is about mu 0.150, not 0.105 (forward_bound_mu0.12 reads 4.786 deg, free). It stands because the nose friction is untested and no posture sweep is on file. |
| T3 | upheld | `_v_held_frozen.json` extra.th_margin.min 5.006; linear stack 4.996 (CAD check lines 94-100). |
| G4 | upheld | `_msub_rest_bench.json`: m_sub_rest min 0.0, lt5 106, lt1 50 of 204; m_plain_rest min 5.389. B1 is the user's. |
| T1 | **refuted** | Shell 33.02 - 18.51 = 14.51 <= TH shell2_watch 15.0; near_touch reads ok; near-touch is report-only (user 2026-10-17). The counts are near-touch counts, not taken floors. The per-pose dumps give 2 / 25 / 94 of 371 on the bench and 14 / 62 / 187 of 852 held, not 3 / 30 / 100 and 14 / 67 / 200. |
| NEW-ws-inband | upheld | probe ws_elev90_140: in-band 0.8002, 19.9 % above 14 mm, max 30.8 mm; held 0.8218. |
| S3 | upheld | No bench wear that samples the real follower, lobe ring or straddle boss is on file. The params still carry s_arm 4.0 / r_lobe 8.27. |
| R1 | upheld | The row text is unchanged at HEAD a6ae26f ('5 of them the lug'; 13.02 / 0.775 / 0.0; n_configs 45 vs 31), and the stated wall rule fails at the top face (1.02 mm). |

**Missed by the auditor (for the next audit; does not change this verdict):**

1. **M5's pass line is misstated.** The reason says the pass line is mu <= 0.105, but `forward_bound_mu0.12.json` passes
   at 4.786 deg. The line sits near 0.150, so the friction margin is 1.7x the claim's 0.087, not 1.2x.
2. **T5 is read against a retired reference.** The finding does not apply the 2026-10-17.5 reference (the current lead).
   Under that reference this row is the shallowest of the three slipper / conecut rows on file, not a T5 case.
3. **T1 counts are taken from the near-touch counters.** `deep.near*_poses` is not "taken poses under N mm". The
   per-pose dumps read lower on the bench (2 / 25 / 94) and held out (62 / 187 against 67 / 200).
4. **NEW-wall-plane does not separate the stroke the poses use from the stroke the stop allows.** The thinner wall is
   real only for K beyond 46.3 deg, which no taken pose reaches. A wall finding should state which stroke it reads.
5. **Process (the lead's rule of 2026-10-17).** The verifier wrote no per-pose dump of its own and no `connected` flood
   key: `docs/concepts/verify/trimlug-k165-knuckle-3r_*.json` holds neither. Both exist only as the auditor's re-measures
   (`remeasure/..._bench_perpose.json`, `_held_perpose.json`, `_flood_bench.json`), which reproduce the claim.

No new gaming was found. The score sits behind the parent (18.51 vs 18.49) and the current lead (18.28). Every
remaining watch is shared with the family or is reporting.

---

_Below this rule: the 2026-10-17 skeptic section, kept unchanged (it rules on the 2026-10-17 12:46-13:07 auditor run, whose text the section above replaces)._

## Skeptic (2026-10-17 13:08-13:20 UTC)

Ledger entry 2026-10-17T13:18:11Z, `by skeptic`, run `skeptic:trimlug-k165-knuckle-3r`. Rulings:
`docs/alignment/trimlug-k165-knuckle-3r.rulings.json`.

**Final verdict: WATCH.** 6 of the 10 reasons are upheld: reporting, T5, M5, G4, NEW-ws-inband, R1. 4 are refuted
with evidence: continuity, idle, S1, NEW-stale-complexity-ruler. No reason reaches gamed.

What I re-measured or re-derived (models unchanged):

- **The continuity flood, re-run by me.** Same lead-module `frozen_flood`, model class TLModel, CB_EXACT=1, 144.7 s,
  output in scratch, not committed. It matches the file on record exactly: full 18.51 with 0 dropped, knn 20.18 with 6
  dropped, bench graph 50.13 with 113 dropped.
- **The paired bootstrap against sidecar-longdyad,** re-run with seeds 1-3:
  - bench -0.40, interval [-2.76, +1.69], P 0.62-0.63;
  - held out +0.81, interval [-0.65, +2.17], P 0.18-0.19.
- **Contact depth from the dumps:** bench 13.19 / 14.75 / 6.23 mm (trimlug / lead / sidecar-longdyad), held out
  40.58 / 46.12 / 35.66. Four held-out contacts get shallower, not five.
- **Against the lead, pose by pose:** 0 of 470 bench and 0 of 1154 held-out poses differ in taken or contact. The metal
  floor rises on 60 bench and 135 held-out poses and falls on none.
- **Complexity, recomputed** with `tools/simplicity.py` v2.2: 22.25 as recorded, 18.25 with the roller-longdyad
  convention.

### Rulings

| key | ruling | evidence (short; full text in the rulings file) |
|---|---|---|
| continuity | **refuted** | The flood is on file (`remeasure/..._flood_bench.json` `connected.connected_full`: 18.51, 0 dropped) and my re-run is identical. The tool's own rule reads full (loss 0.00 <= 1.0); knn +1.67 is under the 3.0 escalation line, so the check reads ok. Same as the lead (18.49 / 20.16). The watch comes from the tool not reading the file (I-b). Process gap: the verifier's files carry no `connected` key. |
| idle | **refuted** | The model only reads `knee_moved` (line 167; SN_CELL lead at line 37); only the kneeless models set it. The 65.71 deg is the pin knee's designed travel, 86.21-151.92 inside [25.22, 154.78]. K moves 45.61 deg and the crank 19.3, both far above 2.0. The third occurrence (I-c). |
| reporting | upheld | Status verified, but the verdict text starts "screened -". The dashboard shows sweep 13.02 (score 95.27) against verified 18.51, and gap 13.02 / reach 0.775 from the fit bench. |
| S1 | **refuted** | The numbers reproduce, but the watch level does not follow. The documented S1 line is the held-out drop: +4.96 against TH 6.0, and the tool reads ok. Every interval includes 0, so neither the bench win nor the held-out loss is established. Ranking on pooled bench + held out would be a rule change (proposal only). The pair's order flips with the flood reading: knn 20.18 vs 21.72, bench graph 50.13 vs 43.40. The contact-count share is T5's. 0 poses differ from the lead. |
| T5 | upheld | The documented margin is met against sidecar-longdyad on the bench: x2.12 and +6.96 mm. Both sides are claim dumps on an unchanged bench. The rank over sidecar is exactly the trade of 2 deep presses for 4 shallow ones. Correction: at 237 the 8.35 mm is the body-1 contact group; the rigid horn reads 6.75 mm. |
| M5 | upheld | No R17 or dynamics output exists. The red team (`docs/research/slipper_mechanism_redteam.md`) is quasi-static: return factor 92-158, hysteresis <= 0.020 N.m. It also measures the lag M5 is about: K lag -0.42 to -0.53 deg takes the held-out th margin to 4.950-4.966 unless a +0.75 deg K lead is built in, and the claim's model does not carry that lead. |
| G4 | upheld | Confirmed: m_sub at rest is under 5 deg on 106 of 204 poses, min 0.000. The active chain at rest passes (m_plain 5.389), but m_sub at rest is the open B1 question for the user and depends on K holding its stop (M5). |
| NEW-ws-inband | upheld | Confirmed. Raised-arm in-band 0.8002, 19.9 % of the metal above 14 mm, max 30.8 mm (held out 0.8218). The 2-14 mm band is the goal's own. |
| NEW-stale-complexity-ruler | **refuted** | The measurement is right (22.25 vs 18.25), but the error overstates this design by 4.0. It cannot raise its score or rank, and G5 is the opposite direction (complexity hidden). The tool's complexity check reads ok. The record fix stays a writer's action. |
| R1 | upheld | Confirmed, and the errors flatter the design: 5 vs 4 shallower contacts; fit-bench gap and reach as the headline; the lug left out of the limiter at 237; n_configs 45 against 31 sweep entries. |

### Missed by the audit (not counted in this verdict; for the next audit)

1. **The held-out fold margin depends on the K lag of a real build.** Applies to the whole slipper family, the lead too.
   - The claim reads min th 5.006 deg held out (`verify/trimlug-k165-knuckle-3r_v_held_frozen.json`
     `extra.th_margin.min`, at ws (135, 30, -135), a forced pose). That is 0.006 deg above the user's 5 deg rule.
   - The red team's slaved-law re-solve (`docs/research/slipper_mechanism_redteam.md`, verdict item 2 and finding 9;
     committed a3b0434 before this audit's ledger entry) predicts a systematic K lag of -0.42 to -0.53 deg, with
     +-0.24 deg random. A lag of only 0.07-0.1 deg puts a held-out pose under 5 deg, and -0.5 to -0.7 deg reads
     4.966-4.950 with 2 poses under 5.
   - The +0.75 deg K lead that fixes it is a build instruction. The claim's model does not carry it.
   - Pattern: M5 / T3. A spring-slaved coordinate scored at its planned value, on a margin that sits at the rule's edge.
2. **The modelled lobe follower is not the real part.** Pattern M1 / M2, the gen-6 drive carried by the family.
   - The red team (lines 53-56 and 185-186) finds the modelled follower (s_arm 4.0 on r 8.27) inside hub 2's O20.
   - The real part is an MR63ZZ on a 6.5 mm arm at psi 216, with the lobe ring at r 10.79-12.77.
   - The real lobe ring, the follower plate and the 10 mm straddle boss are unsampled ("the CAD sweep decides them").
   - So the claim's metal does not include parts the build must carry. The audit's M1 / M2 walk read "no new part" and
     missed this.
3. **The verifier skipped the continuity flood the 2026-10-16 rule asks of it.** No
   `docs/concepts/verify/trimlug-k165-knuckle-3r_*.json` has a `connected` block. The audit's flood (re-run here) is
   clean, so nothing is lost. It is a protocol gap, not a number.

Reported, not a finding:
- The model's `t5()` part breakdown covers only `M.rigid` / `M.contact`. At 3 of the 10 held-out contacts the deepest
  member is unnamed: 224 (-90, 60, 105) depth 3.49 with listed parts to 1.70; 252 (-75, 60, 105) depth 1.60 with none;
  820 (75, 150, -90) depth 0.18 with none.
- Two of those (224 and 252), and 225 (5.51 mm), are elevation-60 contacts at plane -90 / -75, not overhead.

### What happens next

- Fix the audit tool (I-b, I-c), then run `selftest`. This row's refuted `continuity` / `idle` rulings will hold it to ok.
- R17 on the slipper CAD at mu 0.087 / 0.12 / 0.15, as M5 asks.
- Re-measure the held-out th margin with the +0.75 deg K lead and with the worst-case lag as claim columns.
- Re-wear the claim with the real follower, lobe ring and straddle boss sampled.
- Correct the row text: 4 contacts, not 5; fit-bench numbers out of the headline; the limiter at 237; n_configs.
- Fix the complexity record (cuff_knee.closed_loops).
