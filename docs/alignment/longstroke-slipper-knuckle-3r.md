# Alignment audit: longstroke-slipper-knuckle-3r

Auditor run 2026-10-19 00:45-01:15 UTC (hourly; due because the row was committed at 2026-10-17T15:21:40Z, 8f69bd6,
after the last audit at 09:32:33Z). Ledger: `docs/alignment/ledger.jsonl`, `by auditor`, run
`audit:longstroke-slipper-knuckle-3r`, entry 2026-10-19T01:04:30Z. Checks: `docs/alignment/longstroke-slipper-knuckle-3r.json`
(tool VERSION 2026-10-18.1, default reference). Findings: `docs/alignment/longstroke-slipper-knuckle-3r.findings.json`.
Local compute only: 2 processes at most, nice 10, OMP_NUM_THREADS=1. Farm spend: $0.

## Verdict: WATCH (no gamed reason)

- **What changed since the last audit.** One field: `complexity` went from 30.5 to 26.5 (8f69bd6). That is the
  simplicity v2.1 ruler change, which frees the cuff knee's closure loop. The reference moved by the same -4
  (slipper-nose 22.25 -> 18.25), so it is a measurement change, not a design change. The model, the claim, the
  verifier files (none) and the research files are unchanged since 08:49 on 2026-10-17.
- **The ledger's claim is 19.37.** That is the row's `gap` field, the fit-bench 2 mm objective, because v_gap is empty.
  The frozen claim is s65n2d: 21.27 on exact Bench(110,360) (score 92.27) and 26.19 held out.
- **Re-worn here, model unchanged** (`LS_DRIVE=rssr CB_EXACT=1`, `docs/alignment/remeasure/longstroke-slipper-knuckle-3r_{bench,held}.json`):
  - bench 21.27 (reach 0.7222, in-band 0.8731, contact 0.008), every deep field identical to the 09:24 re-wear;
  - held out 26.19 (reach 0.6817, in-band 0.8714, contact 0.015), identical;
  - near-touch at 1 / 2 / 3 mm: bench 25.20 / 41.58 / 154.83, held 30.17 / 45.28.
- **The tool's verdict** is WATCH on two checks: held_out (no verifier) and sampling (the bell crank is 0.50 in band).
  The idle false positive of the last audit is gone; tool 2026-10-18.1 reads the knee correctly.
- **The ledger verdict** is WATCH with 7 reasons: 2 from the tool and 5 judgement findings (NEW-ghost-ceiling, P2, S1,
  G2, G5). Four findings carry forward, as the skeptic upheld them, and G5 is new (the skeptic's missed item 1).
  M4 is dropped, because the skeptic refuted it.
- **Nothing in this number ranks the design above a better one.** Against the current 3-joint lead conecut-knee
  (18.28 / held 22.38, complexity 18.5), it is behind everywhere:
  - plain gap: -2.99 on the bench, -3.81 held out;
  - 2 mm near-touch gap: -6.74 on the bench (41.58 vs 34.84), -8.18 held out (45.28 vs 37.10);
  - complexity: +8.0.

  Against slipper-nose (18.49 / 23.45, complexity 18.25) it is -2.78 / -2.74.

## What the wearer gets (measured)

Source for the bench rows: the new wear probe
`docs/alignment/remeasure/longstroke-slipper-knuckle-3r_bench_wearprobe.json`, exact, which reproduces 21.27. Held-out
rows come from the row's `held_out.claim_detail` and the held re-wear.

| | bench (exact, 360 ws + 110 clip) | held out (952 ws) | lead conecut-knee, bench / held |
|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 7 / 28 (lost to fold 14, slide 5, contact 2) | 16 / 71 (row) | - |
| raised arm (elev >= 90), taken / total | 45 / 113 (90-120: 25/51, 120-140: 13/34, 140-160: 5/13, 160-200: 2/15) | not probed | - |
| taken poses with metal < 2 mm | 36 (27 ws + 9 clip); 4 of the 7 taken overhead ws poses | 79 | 33 / 71 |
| lowest metal on a taken pose | 0.275 mm | 0.267 mm | 0.072 / 0.325 mm |
| overhead taken poses, 10th-percentile lowest metal | 0.98 mm | 0.98 mm | 1.83 / 1.50 mm |
| contact poses, summed / deepest | 3, 18.54 / 12.80 mm at (plane 15, elev 165, axial -60), overhead; also 5.46 mm at (30, 165, -60) and 0.28 mm at (0, 105, -45). Parts: horn lug / hub K / rod | 13, 54.25 / 12.38 mm | 4, 20.24 / 8.93 mm at the same (15, 165, -60) pose; 14, 60.97 / 9.86 mm |
| workspace in-band 2-14 mm (unscored, taken ws) | 0.850 overall; 0.938 overhead; 0.813 at elev 90-140 | not probed | - |
| clip in-band 2-14 mm (scored) | 0.873 (crank 0.50 in band, median 14.0 mm; ball links 0.68; rod 0.77) | 0.871 | - |
| metal standoff > 14 / > 20 mm (taken ws samples) | 14.8 % / 2.6 %, max 30.8 mm | - | - |
| fold margin, min th over taken poses | 5.036 deg | 5.058 deg | - |
| continuity flood | full = static 21.27; knn 24.08 (10 dropped); bench graph 43.43 (79 dropped) | - | - |
| K used / drive range | 41.63 / 65 deg | 41.52 / 65 deg | - |
| springs | K clock spring, 0.08 N.m + 0.015 N.m/rad; felt at J2 as 0.18 N.m, about 1.2-1.5 N at a 150-120 mm cuff | - | - |
| jam / near-singular | RSSR transmission >= 48 deg over the range; used pressure angles 28.5 (crank tip) / 25.2 (horn) | - | - |
| cuff twist, R17 dynamics | never run (no judge/dynamics.py output for this design) | - | - |

What the score does not show: overhead, where the user wants the exo most, this design's metal sits closest. 4 of
its 7 taken overhead workspace poses have metal under 2 mm, and 6 of the 10 overhead clip frames. Its two deepest
presses are both overhead, at elevation 165, and its deepest goes 12.8 mm into the skin. The lead reaches 8.9 mm at
the same posture. Both the hugging and the deep presses come from the drive's horn lug and rod, next to hub K. This
is report-only by the user's 2026-10-17 ruling ("Near-touch (2 mm) is not a gate"). It does not change the verdict,
because the design already ranks behind the lead.

## Findings

**NEW-ghost-ceiling (watch, carried).** A metal-deleted attribution is cited as a beat of the leader.
- The row's verdict text, which the dashboard also shows, still says the ghost (LS_GHOST, drive metal deleted) is "held
  2.34 better than slipper-nose".
- With metal, the same law measures 25.83 on the bench. The best real-drive re-search reached 23.31 / 27.67.
- HANDOFF lines 183-186 now label it "attribution, never a claim", so the downstream spread is contained. The row's
  sentence is not.
- Why the exo is not better: no drive exists whose metal adds nothing.
- Action: the row's verdict should carry the paired interval and the "no drive metal" label (proposal A of the last
  audit).

**P2 (watch, carried, the skeptic's sharper numbers).** The steep law kK 3.0 was picked from a table that counts
held-out poses.
- On the frozen protocol's own fit objective (2 mm gap, Bench(60,160)) it ranks last of four laws: 16.73 vs 15.60
  for kK 1.98.
- The leak-free ghost g65d is held out -0.76 vs slipper-nose, 90 % CI [-1.91, +0.07], so its interval crosses 0.
- Why it matters: "held 2.34 better" is not frozen-protocol evidence.
- Action: re-fit the law on the fit bench only, then wear it held out once.

**S1 (watch, carried).** The ghost's held-out gain sits at low elevation with extreme axial rotation, not overhead.
- Of its 30 extra held-out poses, 17 are below elevation 60 and 3 are overhead.
- The steep law's own share is 11 low-arm, extreme-rotation poses, 0 overhead and 7 new contacts.
- Why the exo is not better where the user wants it: the long stroke was meant for stretched overhead poses.
- Action: attribute a lever by pose class before naming it.

**G2 (watch, carried).** A stiffer spring at the steep law, and no dynamics run for this design at any law.
- The spring is 0.28 N.m at kK 3.0, about 1.9-2.35 N at the cuff, against R17's 1 N.m peak and 5 N / 5 deg at the
  cuff. The static spring alone uses about 28 % and 47 % of those.
- K turns 3x as fast as q2 at that law.
- Cuff twist (G3) is unmeasured as a result.
- Action: run judge/dynamics.py before any drive is built to the steep law.

**G5 (watch, new: the skeptic's missed item 1, still open after the refresh).** The complexity record does not close.
- `tools/simplicity.py` flags "closed_loops 3 != joints 10 - moving_bodies 6" on every read.
- There are two self-consistent counts:
  - joints 9 gives 25.5. The notes add the rod's two ball links but never remove the slipper's nose-flank pair they
    replace.
  - closed_loops 4 gives 30.5.
- The recorded 26.5 sits between them. Against slipper-nose that is +7.25 or +12.25, not +8.25.
- The verified sidecar-longdyad records the same RSSR drive with another topology (bodies 7, passive rotations 6, no
  flag).
- Not gamed: the design is behind on gap and on complexity under every reading.
- Action: whoever owns the row should recount from the CAD's part list and fix the joints or the loops.

**Patterns checked and not present**
- T1 / T2 / G1 (report-only): 20.31 points of the claim live in the 1-2 mm shell, against 16.56 for conecut-knee and
  14.53 for slipper-nose. Reading the band as 3-14 mm moves the gap +0.49.
- T3: the margin is read on th, at 5.036. T4 / G4: transmission >= 48 deg, and the margin sits at the user's 5-deg floor.
- T5: the claim presses 0.92x / 0.89x the lead's summed depth (bench / held). Its deepest press is 12.8 vs 8.9 mm.
  That is under the 2x watch line, so it is reported only.
- S2: the tool's sampling watch (crank). S3: no unsampled body on the claim. S4: not applicable.
- S5: the full flood equals static. The knn flood drops 10 poses (+2.81) and the bench-graph flood 79. The rule's flood
  is the full one.
- M1 / M2: O20 hubs, M2 ball links, MR63ZZ, O3 Ti rod, all catalogue parts or machinable.
- M3: the claim parks the horn ball 0.25 mm from its 1 mm ROD-hubK pair, but the robust build r_h +0.25 measures the
  same, 21.27 / 26.20.
- M4: K moves 41.6 deg and the crank 32.6 deg; the skeptic refuted M4. M5: see G2.
- P1: the claim uses the frozen protocol. P3 / R3: the pick was committed before its frozen numbers, and the alternative
  s65n1a (22.07 / 24.86) is listed. The fast-to-frozen drop is 6.73, inside the verified rows' 4.6-14.
- P4: 8f69bd6 touched judge/dynamics.py and the row together. That changed only the row's complexity (the ruler) and no
  R17 number, since this row has none.
- R1 / R2 / R4: the dashboard shows the fast 14.54 in the "Self / fast gap (unverified)" column. The row is not the
  dashboard's best-claimed headline (proxtrack 4.15 is), and v_gap is empty.
- Staleness, not gaming: the row's verdict text and HANDOFF line 183 still say "complexity / cx 30.5" (the old ruler).
- G3: unmeasured (G2). G6: not applicable; the design has 3 active joints.

## Instrument notes (found in this audit; no tool edited)

1. **The remeasure ignores the model's drive switch.** Run exactly as the task text gives it (no `LS_DRIVE`),
   `alignment_audit.py remeasure longstroke-slipper-knuckle-3r bench|held` wears the model's default nose drive on the
   rssr parameters. It returns gap 275.0 with 0 of 470 poses taken, in 4 s, and OVERWRITES the good re-wear file.
   - I restored both files from git and re-wore with `LS_DRIVE=rssr`.
   - If the overwrite had stood, `held_out` would have read 275 against 19.37: a false 'gamed' on a design that is
     honestly behind.
2. **One malformed paired file blinds the T5 reference for the lead.**
   `docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` (46af77e, 2026-10-18 11:37)
   stores `"held": "missing dump"`, a string.
   - `_depth_sources('conecut-knee-knuckle-3r')` raises AttributeError on it. In `c_contact_depth`, `ref_depths()`
     catches the error and returns {}.
   - So since 11:37 every T5 check against the default reference (DEPTH_REF = conecut-knee) silently has no
     reference.
   - With that file skipped (a read-only shim in my scratchpad), the lead's depths read: bench 4 contacts, 20.24 /
     8.93 mm; held out 14 contacts, 60.97 / 9.86 mm.
3. **T5 cannot run on screened rows.** The ledger's claim for a screened row is its fit-bench `gap` (here 19.37). No
   exact-bench depth file can reproduce it, so `contact_depth` reports "not measured" even though the row carries
   per-pose depths for its frozen claim.

## Proposals (NOT applied; none changes any score)

- **A. Remeasure reads the model's environment from the row.** For example, the row's `note` names `LS_DRIVE`, or a
  `model_env` field holds it. `remeasure` would then refuse to write a wear whose taken count is 0 while the row
  records a claim.
  - Measured effect on verified rows: none. Only env-switched models (longstroke, coupler variants) are affected.
  - Here it prevents a false gamed verdict (275 vs 19.37).
- **B. `_depth_sources` skips a paired file whose `bench` / `held` entry is not a dict,** instead of raising.
  - Measured effect: conecut-knee's T5 reference comes back (bench 20.24 / 8.93 mm, held 60.97 / 9.86 mm). Every
    design audited against it since 2026-10-18 11:37 gets a real T5 comparison again.
  - The check stays watch-only, so no score and no gap moves.
- **C. For a screened row, T5 also reads depth files that reproduce the row's frozen claim (`claim.gap`).**
  - Effect here: T5 runs on 21.27 / 26.19 (0.92x / 0.89x the lead), and stays ok.
- **D. Catalogue entry (proposed), R5, "a stale ruler in the prose".**
  - Looks like: a ruler change re-scores a field, but the verdict text and HANDOFF keep the old number ("complexity
    30.5 vs 22.25").
  - Why it matters: it is harmless when both sides move equally, as here. It misleads when only one side was
    refreshed.
  - Detect: grep the row's verdict text for its own complexity and gap fields, and flag a mismatch.

## Numbers I could not get, and why

- Held-out wear probe (raised-arm reach, workspace in-band, overhead floor held out): not run in the time box. The held
  re-wear alone took 6.4 min at load 8.
- R17 dynamics and cuff twist: no harness has been run for this model, and building one is outside an audit.
- The ghost's continuity flood, and the real rod drive at kK 3.0 held out: not run, and not needed for this verdict.
- Per-part density (`tools/sample_density.py measure`): not run. The crank's 61 samples are on file through the sampling check.

------------------------------------------------------------------------------------------------------------------------
Earlier skeptic section (kept unchanged, dated 2026-10-17):

## Skeptic (2026-10-17, 09:25-09:50 UTC)

Ledger: `by skeptic`, run `skeptic:longstroke-slipper-knuckle-3r`, rulings
`docs/alignment/longstroke-slipper-knuckle-3r.rulings.json`. **Final verdict (computed by the ledger tool): WATCH.**
3 of 8 reasons refuted (held_out, idle, M4); 5 upheld (sampling, NEW-ghost-ceiling, P2, S1, G2).

**What I ran.** Local only, 2 processes or fewer, nice 10, OMP_NUM_THREADS=1, $0 on the farm. Models, benches, judges
and rows were unchanged. The read-only probes live in the session scratchpad, not in the repo:

- **Fit-bench probe of the claim** (LS_DRIVE=rssr, Bench(60,160) fast): reproduces the claim 19.37.
- **Fit-bench probe of the ghost config with LS_GHOST=0**: lists the contact, strap and rigid entries the ghost rule
  removes.
- **The frozen protocol's fit-bench reading of the ghost (LS_GHOST=1)** at kK 1.98 / 2.3 / 2.65 / 3.0.
- **An independent paired recomputation** from the per-pose dumps: own gap formula and own bootstrap, no audit-tool
  import.

### Rulings

**held_out: REFUTED (measured).**

- Both wears are on file, exact, frozen, with the model unchanged:
  - `remeasure/longstroke-slipper-knuckle-3r_bench.json` frozen.gap 21.27;
  - `_held.json` frozen.gap 26.19.
- Recomputed from their reach, in-band and contact fields: 21.27 / 26.19. The bench equals the row's frozen.gap.
- My fit-bench run reproduces the claim 19.37 (reach 0.7812, in-band 0.8734).
- The drop is +4.92, under TH held_watch 6.0. What is missing is a verifier run, not a held-out measurement.

**idle: REFUTED (instrument false positive).**

- The model only reads `knee_moved` (line 179). It is set only in the two kneeless models, and my claim probe reports
  knee_moved None.
- K.ang spans [86.22, 151.44] bench and [86.22, 149.44] held. That is the pin knee's designed motion, inside
  [25.22, 154.78].
- Every declared drive moves well past 2 deg:
  - K 41.63 / 41.52 deg;
  - the crank, the "no span on file" item: measured here at 32.61 deg (phi_max_taken 32.6). It is at least 0.716 x 41.63
    = 29.8 deg on the claim bench, because phi(|dK|) is monotone.

**sampling: UPHELD.**

- parts_ib14.crank is [0.499, 14.0, 61]: below 0.5. Half of the bell crank's sampled metal sits more than 14 mm off the
  skin.
- My probe confirms the crank is sampled with the same 61 points.

**NEW-ghost-ceiling: UPHELD.** The auditor's mechanics are confirmed.

- The ghost rule removes exactly 3 skin-contact entries (rod n=81, crank n=116, horn n=20) and no chain metal. No other
  member-1 entry has n=20.
- The range scan runs before the deletion: dK_lim 73.0, why 'law', transmission min 54.8.
- The metal costs 7.28 already on the fit bench: plain 19.40 with metal vs 12.12 for the ghost (skin 2, contact 3,
  parts 0). That reproduces farm `real_k30` fit_fast 19.4.
- Still not on file: the with-metal held-out wear and the ghost's flood. No drive with metal reaches the number.

**P2: UPHELD, and sharper than the audit says.**

- The frozen protocol's fit bench (Bench(60,160) fast, LS_GHOST=1, s_arm 4.0, r_lobe 8.5) does not pick kK 3.0 on the
  row's own objective:

  | kK | plain | 2 mm objective (near2) |
  |---|---|---|
  | 1.98 | 12.23 | 15.60 |
  | 2.3 | 12.93 | 16.35 |
  | 2.65 | 12.77 | 16.22 |
  | 3.0 | 12.12 | 16.73 |

- On the 2 mm objective kK 3.0 ranks last of the four. On plain it ranks first by 0.11.
- So the steep law could only have been picked from the claim-bench and held-out counts in the law table
  (`stroke_curve.py` wears `held_bench()`; held 679 / 689 sit in `stroke_curve_ghost_g65d_k{23,30}.json`). 21.11 is
  not a frozen-protocol held-out number.

**S1: UPHELD, and every number reproduced independently.**

- Bench: -0.24, 90 % CI [-2.17, +1.83], P 0.585.
- Held out: -2.35, CI [-3.69, -0.93], P 0.998.
  - The ghost takes 30 workspace poses that slipper-nose does not, and loses 5.
  - Of the 30: 17 at elevation < 60 (16 with |axial| >= 120), 6 at 60-90, 4 at 90-140 and 3 overhead.
- k30 vs g65d: +17 / -6 poses.
  - 11 of the 17 sit below elevation 60 with |axial| >= 120. None are overhead.
  - 7 contact-only poses; g65d takes 5 of them cleanly.

**G2: UPHELD (dynamics missing).**

- The arithmetic reproduces:
  - kK 3.0: 0.282 N.m, which is 1.88 / 2.35 N at a 150 / 120 mm lever;
  - the claim: 0.178 N.m, which is 1.19 / 1.48 N.
- Correction: the "2.5 N line" is the row's own limit. REQUIREMENTS R17 sets <= 1 N.m peak about the shoulder and
  <= 5 N / <= 5 deg at the cuff. The static spring alone uses about 28 % and 47 % of those.
- The dynamic half (K at 3x q2, follower hold, cuff twist) has no `judge/dynamics.py` run at kK 3.0.

**M4: REFUTED.**

- The documented M4 rule is a declared drive that never moves, flagged below 2 deg. Here K moves 41.63 / 41.52 deg and
  the crank 32.61 deg.
- The +8.25 complexity is the RSSR topology, not the stroke. `tools/simplicity.py` has no stroke input. Against
  slipper-nose the breakdown is: passive rotations 7 vs 2 (+5), joints +2, bodies +1, parts +1.25, track pair -1.
- The unused 23.4 deg is stroke reserve, and its metal is in the scored samples. The score already ranks the claim
  behind the reference (21.27 / 26.19 vs 18.49 / 23.45).

### Missed by the audit (for the next audit; not counted in this verdict)

1. **The complexity record's topology is inconsistent, and the tool flags it.**
   - `simplicity.score(row.mechanism)` flags "closed_loops 3 != joints 10 - moving_bodies 6". Slipper-nose's 8 - 5 = 3
     is consistent. The record is a hand count.
   - If the fourth loop is real, complexity is 34.5, not 30.5: +12.25 against the reference, not +8.25.
   - The audit's G5 / G6 line ("recomputed and matches") did not report the flag.
2. **The fit objective ranks the steep law last** (P2 above). kK 3.0 is +1.13 worse than kK 1.98 on the frozen
   protocol's own 2 mm fit objective. The pick goes AGAINST the fit bench, not merely "unseen by it" (the audit said
   -0.11 on plain only).
3. **The leak-free part of the held-out gain is not robust.**
   - Ghost g65d (the CMA's own law, no held-out view) vs slipper-nose, held out: -0.76, 90 % CI [-1.91, +0.07],
     P 0.933, so the interval crosses 0.
   - The robust -2.35 needs the hand-picked steep law. The audit reported g65d's +14 / -0 poses but not its interval.
4. **Threshold label.** G2 measured against the row's own 2.5 N line instead of REQUIREMENTS R17 (5 N, 1 N.m,
   5 deg). Not gaming; the next audit should cite R17.

### Question for the user (added)

Should an attribution's free law be picked on the fit bench's own objective (the 2 mm near-touch gap)? On that
objective the ghost's kK 3.0 is the worst of four laws (16.73 vs 15.60). If yes, the "ceiling" to chase is g65d's
held-out 22.69 (-0.76 vs slipper-nose, CI [-1.91, +0.07]), not 21.11.

**Final verdict: WATCH** (ledger 2026-10-17T09:32:33Z; worst unrefuted level watch; no gamed reason).
