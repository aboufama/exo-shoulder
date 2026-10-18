# Alignment audit: sidecar-longdyad-knuckle-3r (verified; round-8 winner, now 14th on the verified board)

This is the hourly audit of 2026-10-18, 22:17-22:45 UTC. Ledger entry 2026-10-18T22:37:17Z (`by auditor`, run
`audit:sidecar-longdyad-knuckle-3r`, git 9b1711c). It supersedes the 22:32:17 entry of the same run, which lacked the
G4 finding. It was due because commit ec77d25 (simplicity v2.1, 2026-10-17 04:55)
touched the row after the last audit (skeptic, 04:37). That commit changed only the row's complexity: 29.5 to 25.5,
because the knee's closure loop became free. The claim did not move. The audit edited no bench, judge, kit, model, row,
dashboard page or CLAUDE.md, and changed no score. It added no tool. It ran locally (nice, OMP_NUM_THREADS=1, at most
2 processes), with no farm, so $0. The earlier auditor sections (2026-10-17 04:15) are replaced by this one. The two
skeptic sections are kept unchanged under the dated rule at the end.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **18.91** (score 93.12), frozen exact Bench(110,360), held out 22.67. It did not move, and
  both re-wears reproduce it to the digit.
- **Complexity:** 25.5 (tools/simplicity.py 2.2). The row field matches. The 04:14 MISMATCH is gone.
- **Ledger reasons (11, all watch):**
  - From the tool (1): `reporting`.
  - From this judgement pass (10): **M2** (new: knee pin stack), **S3** (new on this ledger: unsampled drive parts),
    **G4** (new on this ledger: sub-chain margin with K at rest, B1), NEW-catalogue-drive, NEW-unpriced-stops,
    **G5** (now flatters this row by 2.5), M5, G1, S1, R1.
  - None is gamed.
- **Retired: NEW-law-dependent-sensing.** The user ruled on 2026-10-17 that sensing is out of scope ("dont wory about
  the sensor stuff"), and encoders now cost 0 (simplicity v2.2). Its mechanical half, a K that leaves its law, is
  kept under M5.
- **What changed for the wearer since the last audit:** nothing in the design. Two things in the rules apply to it.
  1. The lead's build rule says the knee pins are built as MR63ZZ pairs. This row's claim sits on a thinner knee.
     With the MR63ZZ stack it reads 19.21 on the bench and 22.97 held out (+0.30 on each).
  2. The v2.1 knee credit now makes this pin-knee row read simpler than its own kneeless twin.

## Checks (tools/alignment_audit.py 2026-10-18.1, re-run after the re-wears)

Thirteen of the 14 checks are ok and one is watch. The file is `docs/alignment/sidecar-longdyad-knuckle-3r.json`.

| check | level | reading |
|---|---|---|
| held_out | ok | 22.67 vs 18.91 (+3.76), re-measured this audit |
| fast_frozen | ok | fast 10.3 -> verified 18.91 (+8.61) |
| near_touch | ok | 1 mm 20.00, 2 mm 34.03, 3 mm 155.98; band 3-14 mm 19.22; 15.12 points live in the 1-2 mm shell |
| contact_depth | ok | bench 4 contacts, sum 6.23 mm, deepest 4.61 mm at (30, 165, -60); held out 10, sum 35.66 mm, deepest 8.37 mm at (15, 150, -60). The reference (conecut-knee) has no depth on file |
| dominance | ok | vs frontload-lobe-stopb: plain +3.91, 2 mm +10.05 |
| continuity | ok | static 18.91 = connected full 18.91; knn 21.72; bench grid 43.4 |
| fold_margin | ok | min th margin 5.232 deg |
| idle | ok | K 37.8 deg, crank 31.6 deg, knee pins 56.1 deg |
| sampling | ok | sample-weighted in-band 0.897 vs part-weighted 0.923; thin parts: rod 13, L1a 12 samples |
| density | ok | no part sampled at more than 2x the kit's density |
| complexity | ok | 25.5 recomputed = 25.5 on the row (hand count) |
| reporting | **watch** | the verdict text still reads as a self-measured screen; the dashboard's sweep best 10.3 sits 8.61 below the verified number |
| judge_change | ok | no bench, judge or metric file changed in the 6 commits that touched the row |
| rules | ok | O20, margin >= 5, translations <= 2 |

## Re-wear (by the rule: the remeasure files were older than the row's last commit)

These are the model's own `frozen()` and `frozen_held()`, unchanged, run with `CB_EXACT=1`.

| wear | plain | 1 mm | 2 mm | 3 mm | min metal | < 1 / 2 / 3 mm poses | secs |
|---|---|---|---|---|---|---|---|
| bench (fit Bench(60,160), worn Bench(110,360) exact) | **18.91** | 20.00 | 34.03 | 155.98 | 0.278 mm | 2 / 26 / 178 of 371 | 117 |
| held out | **22.67** | 25.75 | 37.24 | 163.09 | 0.141 mm | 14 / 63 / 427 of 859 | 364 |

Both reproduce the row and the 2026-10-17 re-wear to the digit. The files are
`docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_bench.json` and `_held.json`. Another agent's WIP commits
(0f605a3, 466df40) picked them up and committed them first; the content is mine. One measurement file changed since
the last audit, `judge/dynamics.py` (8f69bd6, an R17 rounding gate). It does not touch the bench.

**Knee-stack wear (new this audit).** This is the same call with one change, `{"stk": 6.0}`: the MR63ZZ-pair stack
of the kit (docs/concepts/models/skin-normal-3r-pin-knee.py lines 19 and 54), in place of the claim's 4.8534.

| wear | plain | in-band14 | knee part in band (median) | 1 mm | 2 mm | reach / contact |
|---|---|---|---|---|---|---|
| bench, stk 4.8534 (claim) | 18.91 | 0.8966 | 0.942 (10.4 mm) | 20.00 | 34.03 | 0.725 / 0.0107 |
| bench, stk 6.0 (MR63ZZ pair) | **19.21** | 0.8936 | 0.914 (11.0 mm) | 20.30 | 34.03 | 0.725 / 0.0107 |
| held, stk 4.8534 (claim) | 22.67 | 0.8947 | - | 25.75 | 37.24 | 0.690 / 0.0115 |
| held, stk 6.0 (MR63ZZ pair) | **22.97** | 0.8917 | - | 26.05 | 37.24 | 0.690 / 0.0115 |

The files are `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_mr63knee_bench.json` and `_mr63knee_held.json`.
They come from `tools/alignment_audit.py`'s `remeasure()` with a params file, with its output folder redirected so the
canonical files stay untouched. The knee kinematics are identical: knee angle 88.7-146.1 deg either way. So the whole
cost is the taller knee plates moving out of band.

## What the wearer gets (measured)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140) | **8 / 28 taken** on the bench (lost: fold 14, slide 4, contact 2); 18 / 71 held out | `remeasure/..._bench.json` audit.overhead140; row held_out |
| Raised-arm reach (taken / total) | 0-60: 161/172; 60-90: 55/75; 90-120: 25/51; 120-140: 12/34; 140-160: 5/13; 160-200: 3/15 | `remeasure/..._probe.json` |
| Taken poses with metal < 2 mm | **26 of 371** bench (2 under 1 mm, min 0.278 mm); 63 of 859 held out (14 under 1 mm, min 0.141 mm). Overhead: 5 of the 8 taken poses have their floor under 2 mm; overhead p10 floor 1.02 mm bench, 0.64 mm held out | `_bench.json`, `_held.json` (re-worn today); `_probe.json` |
| Deepest contact | **4.61 mm into the arm at plane 30 / elev 165 / axial -60** (overhead), 4 contact poses on the bench, summed 6.23 mm; held out 10 poses, summed 35.66 mm, deepest **8.37 mm** at (15, 150, -60), 5 deeper than 3 mm | audit contact_depth; `_bench_perpose_claim.json` |
| Workspace in-band (unscored) | 0.874 over 261 taken workspace poses; 0.841 at elev 90-140; overhead 0.926 | `_probe.json` |
| Drive margins | transmission min 38.8 deg (limit 30); lobe pressure angle 39.11 (limit 45); horn ball-link tilt 21.8 (limit 30); K taken to 37.8 of the model's 43.0 range (but only 35.4 with the catalogue eye, NEW-catalogue-drive) | `verify/..._v_bench_frozen.json` extra / sidecar |
| Springs / stops | one K clock spring (0.08 N.m) holds the whole drive in contact. J2 stops smlo 5.0 / smhi 16.55; K stop B 63.18 never binds. The knee window 26.88-153.12 deg is enforced by the kit (`knee()` line 110), and the knee peaks at 146.1 deg, 7.0 deg inside its stop | row; model; `_bench.json` coord_spans |
| Cuff twist, K lag, lift-off | **not measured**: R17 has never run on this design (no judged CAD) | - |
| Near-singular postures | on the claim's reading, none: fold margin >= 5.232 deg of th, drive transmission >= 38.8 deg, knee 7 deg inside its window. With K resting on stop A, the J1-K-J3 sub-chain margin is under 5 deg on **145 of 250** rest poses (under 1 deg on 67, min 0.000 at (15, 45, -15)); B1 is open with the user | row final_polish; verifier; `remeasure/..._msub_rest_bench.json` |

Numbers I could not get, and why:
- The gap with the real follower, short arm and lobe ring sampled (S3): no bench model of them exists, and building
  one does not fit a 35-minute box.
- Cuff twist and K lag (M5): R17 needs a judged CAD of this design, and none exists.
- The knee-stack wear for the other pin-knee rows: one row per audit. roller-longdyad's own concurrent audit has its
  stk 6.0 bench at 18.93 (claim 18.67).

## Findings

### M2 (watch, new): the knee is claimed on a thinner stack than the hardware the build must use

- **Evidence.** The model carries stk 4.8534 mm (model line 48, inherited from the old lead's search). The kit's
  figures are 5.0 for iglidur and 6.0 for an MR63ZZ pair. The lead's build rule of 2026-10-17 (CLAUDE.md) requires
  MR63ZZ pairs. The row notes and the built L1 still show iglidur pins: 2.18 mm plates, GTM washers and e-clips in
  `pipeline/full-exo/designs/l1_sidecar-longdyad/parts_full.json` k 24-30.
- **Measured.** With the claim otherwise unchanged at stk 6.0: bench 19.21 (+0.30), held out 22.97 (+0.30). The whole
  cost is knee-plate in-band.
- **Why the exo is not quite as good as the number.** The knee the build rule allows stands 1.15 mm taller than the
  claim's knee. The knee the claim does model, iglidur, is the one that failed R17 with about 10 deg of cuff twist on
  the lead's build.
- **Why watch and not gamed.** The only verified, unflagged row it reorders is desmo-conecut-knuckle-3r, which was
  claimed at stk 6.0.
  - Bench: this row is 0.07 ahead as recorded and 0.23 behind with the same knee.
  - Held out: it stays ahead with the same knee (22.97 vs 23.24).
  - A mixed result inside one workspace pose is not proof that the other design is better for the wearer.
- **Action.** Proposal P-1.

### S3 (watch, new on this ledger): drive parts the build must carry are not sampled

- **Evidence.** The verifier's open items (design doc lines 286-295): "The crank's short arm and its follower are not
  sampled metal". The modelled lobe works at r 7.7-10.2 mm, inside hub 2's O20 housing.
- **The real parts.** The drive red team (`docs/research/sidecar_mechanism_redteam.md` finding 3) solved the real
  follower: an IKO CFS2.5 on a 6.0 mm arm, riding a lobe ring of profile r 10.29-13.43 mm on link 2's housing. That
  ring stands up to 3.4 mm outside the hub.
- **Not measured.** It is the same family-wide gap that the trimlug-k165 audit lists. It is optimistic by an unknown
  amount, most likely on in-band rather than contact, since the ring stands sideways from the hub, not toward the skin.
- **Action.** Proposal P-2.

### G5 (watch, changed direction): the knee credit now makes the pin-knee row read simpler than its kneeless twin

- **Evidence.**
  - v2.2 reads this row 25.5 and its kneeless twin 28.0. The twin is the same mechanism with the knee link, the 2
    pins and the knee loop replaced by one rigid bracket.
  - The standard subtraction takes out 1 body, 2 made and 2 bought parts more than this row's own knee has. Since
    v2.1 it also takes out the knee loop, which the twin confirms belongs to the knee.
  - Under the ruling ("no added complexity") the two rows should read equal, at 28.0. On 2026-10-17 04:14 the error
    went against this row (+1.5). Now it favours it (-2.5).
  - roller-longdyad has the same: 20.25 against kneeless-roller 23.75.
- **Why it matters.** No ranking among verified rows flips. But "fewer joints is simpler" is now inverted on these
  two pairs, and the next complexity-minimising search would see the knee as a way to lower the count.
- **Action.** Proposal P-3.

### G4 (watch, new on this ledger): the J1-K-J3 sub-chain sits at its fold while K rests on stop A

- **Evidence.** The committed read-only probe `tools/alignment_msub_rest_probe_model.py` ran on the frozen exact bench
  (gap reproduced 18.91, 149 s); the file is `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_msub_rest_bench.json`.
- **The claim's reading holds.** The family reading gives min 5.232 deg, 0 poses under 5. It reads m_plain where K
  rests (min 6.062) and min(m_sub, m_eff) where K moves (m_sub >= 10.79).
- **With K at rest** (250 of 371 taken poses), m_sub is under 5 deg on 145, under 2 on 88 and under 1 on 67, min
  0.000 deg at (15, 45, -15).
- **Why it may matter for the wearer.** Stop A is held by one clock spring. If that stop is not rigid under the
  arm's load, the J1-K-J3 sub-chain is near-singular over most of the low-arm workspace.
- **Why watch.** It is the family's reading, and the user has not ruled on B1 (docs/HANDOFF.md section 7 item 3).
  roller-longdyad shows the same (106 of 204 under 5, min 0.000), and so does trimlug-k165.
- **Action.** None from the audit; it waits for the user's B1 ruling.

### Carried (claim unchanged; re-worn numbers identical)

- **NEW-catalogue-drive (watch).** The catalogue KBRM-02 ball link (O9 x 4 head), with the drive cap at dK 35.4, reads
  19.76 on the bench and 23.53 held out. K is taken to 37.8 deg, past what the real eye allows.
- **NEW-unpriced-stops (watch).** smlo 5.0 and a1max = bk1 + bk2 - 5 sit exactly on the rule. Priced at +0.5 deg, it
  reads 19.36 (held out 23.29).
- **M5 (watch).** One 0.08 N.m clock spring holds K on its law, and K leaves stop A on 123 of 375 bench poses. R17
  has never run. Off its law, the chain has mobility 4: a loose knuckle the model never wears. The sensing side is
  retired by the user's ruling.
- **G1 (watch, report only).** 26 bench and 63 held-out taken poses have metal under 2 mm. 5 of the 8 overhead poses
  have their floor under 2 mm. Near-touch is not a gate.
- **S1 (watch).** 13 3R verified rows sit within 0.70 points, so the plain order among them is noise. On held out
  this row is second of the 3R rows with a held-out wear on file (22.67, behind conecut-knee's 22.38). The noise does
  not flatter it.
- **R1 (watch).** These records are stale:
  - the row verdict reads "SCREENED";
  - the dashboard gap / reach fields carry the fast 10.3 / 0.80, and its alignment_reasons show the old MISMATCH;
  - design doc line 62 says "complexity 49.0";
  - ROUNDS.md lines 1228 and 1306 say the kneeless bracket "halves complexity". Under v2.2 the bracket adds 2.5.

## Patterns checked and clean (this pass)

| pattern | result |
|---|---|
| T1 / T2 | near-touch and band edge are reported only (G1); band 3-14 mm 19.22 vs 18.91 |
| T3 | fold margin read on th (the rule's angle), min 5.232 deg on the family reading (m_plain at K's rest, min(m_sub, m_eff) where K moves); the rest-pose m_sub is G4 |
| T4 | no search bound walking to a singular edge: the CMA moved ang_min from the parent's 27.86 to 26.88, but the window never binds (knee 88.7-146.1 deg, 7.0 deg inside the 153.12 stop) |
| T5 | contact depth reported (bench 6.23 mm summed; held 35.66 mm, deepest 8.37). It is the shallowest held-out sum of the 3R pin-knee rows with depth on file (roller-longdyad 49.88, slipper-nose 46.12) |
| S2, S4, S5, S6 | sampling ok (rod 13 / L1a 12 samples, in-band); continuity full = static; density ok |
| M1, M3, M4 | no virtual parts or slides; RSSR closure 0.0 mm and ball-link tilt checked by the verifier; nothing idle |
| P1-P4 | held out +3.76 (under the 6 line); no held-out leakage (the final polish searched the envelope bench and replaced nothing); one claim, no re-measure shopping; no judge change with the design |
| R2-R4 | no refuted record shown; the sweep best is flagged by the `reporting` check (R1) |
| G2, G3 | spring-held drive and cuff twist are unmeasured (M5, M2's iglidur note); drive transmission 38.8 deg and pressure angle 39.11 deg are inside their limits, not at a cap (G4's rest-pose margin is a finding above) |
| G6 | 3 active joints (J1, J2, J3); K slaved; knee pins are cuff alignment outside the count. 3 DOF |

## Proposals (not applied; measurement changes for the lead or the user)

- **P-1. Re-wear every verified pin-knee row at the build rule's knee stack (stk 6.0) and rank on that.**
  - Measured effect so far: this row +0.30 bench and +0.30 held out (19.21 / 22.97). roller-longdyad +0.26 on the
    bench (18.93, its own concurrent audit). desmo-conecut and conecut-knee are already claimed at 6.0.
  - On this row the only order change is desmo-conecut ahead on the bench, while this row stays ahead held out.
  - Rows inheriting 4.8534 that I could not measure: slipper-nose, desmo-slipper and the other frontload-descended
    rows.
- **P-2. Add the real follower, short arm and lobe ring to the drive's sampled metal** (the red team's CFS2.5 on a
  6.0 mm arm, ring r 10.29-13.43 mm), then re-wear the claim. Effect: unknown until built. It is family-wide.
- **P-3. Derive each pin-knee row's knee subtraction from its own kneeless twin (or its CAD part list).**
  - Measured effect: this row 25.5 -> 28.0 (= its twin); roller-longdyad 20.25 -> 23.75 (= its twin).
  - No verified ranking changes, and the "knee is free" ruling then holds exactly instead of paying a bonus.
- **P-4.** Fix the stale R1 records: the row verdict text, doc line 62, the dashboard's gap / reach fields, and ROUNDS
  lessons 1228 / 1306.

## Cost

- Two canonical re-wears (117 s bench, 364 s held), two knee-stack wears (172 s bench, 332 s held) and one m_sub
  rest probe (149 s).
- Local, nice, at most 2 processes at once (machine load 4-10 from other agents). No farm, $0.

---

*Auditor sections above: 2026-10-18 22:45 UTC (hourly audit, due to ec77d25). Skeptic sections below: 2026-10-17
02:24-02:40 UTC and the 2026-10-17 simplicity-v2 metric-change skeptic; kept unchanged.*

## Skeptic (2026-10-17, 02:24-02:40 UTC, git e99f42f -> 0a574f3)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It used local compute only: nice, OMP_NUM_THREADS=1, one process. A farm batch was tried, but this session's
permission policy refused it, so the farm was not used ($0).

**Final verdict (ledger, `stage skeptic`, 2026-10-17T02:32:17Z): WATCH.** None of the 9 reasons was refuted, and all
are watch. The claim is 18.91.

**Re-measured this session (model unchanged).**
- **Exact re-wear.** `tools/alignment_audit.py` `remeasure`, unchanged, with its output dir redirected to the scratchpad.
  CB_EXACT=1, HEAD e99f42f, 232 s.
  - Frozen: **18.91**, 1 mm 20.00, 2 mm 34.03, 3 mm 155.98; band 3-14 mm 19.22.
  - Poses: near1 2 (0.28 and 0.38 mm), near2 26, near3 178. Lost: fold 86, slide 7, parts 2, contact 4.
  - Overhead p10 min metal 1.02 mm; overhead lost: fold 14, slide 4, contact 2.
  - Spans: dK 0..37.80 deg; knee K.ang 88.7-146.1 deg.
  - The fit used the rebuilt fast cache (`.cache/concept_bench`, created 01:59 UTC); fit_fast 10.3 matches row.gap.
  - Every figure matches `remeasure/sidecar-longdyad-knuckle-3r_bench.json` to the digit.
- **Measurement files.** `git diff --stat 63167c0 HEAD` changes only judge/dynamics.py. The diff covered the bench,
  kit, env bench, simplicity, judge/, body_pose, split.json, the band poses, both verify helpers, this model, its
  frontload parent and the pin-knee model.

**Rulings** (also in `docs/alignment/sidecar-longdyad-knuckle-3r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| near_touch (watch) | no | **Measurement.** Re-worn: the numbers are reproduced to the digit (above). **Threshold.** TH shell2_watch 15.0 is applied to gap_near2 - plain = 15.12, the same quantity the section-5 calibration ("15-31") used. **Label correction.** 15.12 is the 0-2 mm shell. The strict 1-2 mm shell (gap_near2 - gap_near1) is **14.03**, under 15. The watch crosses the line by 0.12 only through the 2 poses under 1 mm (+1.09). Held out: 14.57 for 0-2 mm, 11.49 for 1-2 mm. Re-reading the shell is a measurement change, so it is not used. **Wearer cost.** It is real (section 1 item 1): 24 taken bench poses sit at 1-2 mm and 2 at 0.28 / 0.38 mm. |
| reporting (watch) | no | **After the 02:13 refresh (fc0f574).** morphs.json still has gap 10.3, sweep_gap 10.3, reach 0.8 and the verdict "SCREENED, a candidate for the verifier". 100 (1 - 10.3/275) = 96.25. **Row.** t_verified and v_contact are null, while verification.contact is 0.0107. |
| S1 (watch) | no | **Numbers confirmed.** v_gap 18.67 / 18.91 / 19.13. Held out, exact, n 1154: 23.73 / 22.67 / 22.03. Held 1 mm: 26.83 / 25.75 / 24.44. One pose = 100/360 = 0.278. **Paired file.** 8 / 8 discordant, CI90 [-2.62, +1.77], pooled P(roller better) 0.287. **New.** At 1 mm the bench order reverses again: this design 20.00, parallelogram 20.22, roller-longdyad 20.30. This strengthens the finding. |
| NEW-sensed-knee-pins (watch) | no | **Recomputed** with `tools/simplicity.py`, the 2 pins moved to active and out of passive_rot: 49 -> 87 at 5 DOF (89 if passive_rot is kept). roller-longdyad 81.75, parallelogram 87, roller-flank 83.25, frontload 87; kneeless 23.75 / 28.0 unchanged. **No ruling.** A grep of CLAUDE.md, REQUIREMENTS, HANDOFF and ROUNDS finds no user ruling on the knee pins, only proposals (HANDOFF 222; ROUNDS 527-528, 738). |
| NEW-catalogue-drive (watch) | no | **Confirmed.** `_rh155cap354_bench.json` 19.76 / 20.85, 368 taken. `_held.json` 23.53 / 26.63. Control `_rh155_bench.json` 18.92. **No judge.** l1_sidecar-longdyad has no judge/. **Correction.** "about 1.2 behind roller-longdyad" uses roller's envelope-corrected 18.56, which the roller audit's S2 says never to quote. Like-for-like, the gap is **1.09** (18.67). |
| NEW-unpriced-stops (watch) | no | **Stops.** smlo 5.0. a1max 63.1774 = 28.9414 + 39.236 - 5 exactly. min th 5.232. **Priced.** 19.36 / held 23.29, min th 5.513. **Roller-longdyad.** smlo 5.0, a1max 0.27 inside its rule, so the comparison is like-for-like within 0.3 deg. **Wearer.** A built stop at exactly 5 deg with +-0.5 tolerance reaches 4.5 deg of the fold. |
| G1 (watch) | no | **Probe.** clip overhead floor < 2 mm on 8/10 frames (all 10 < 3 mm); workspace overhead 5/8 (1 < 1 mm). **p10.** 1.02 bench (own re-wear), 0.64 held. **Under 3 mm.** near3 178 vs roller 133. **Correction.** The shell figures mix two definitions. Bench 15.12 is n2 - plain, but its own parenthesis "20.00 -> 34.03" is 14.03. Held 11.49 is n2 - n1. Like-for-like: 14.03 / 11.49 for 1-2 mm, or 15.12 / 14.57 for 0-2 mm. |
| M5 (watch) | no | **Missing measurement.** No R17 / dynamics output for this design or l1_sidecar-longdyad anywhere in judge/ or pipeline/. The red team doc only plans it. |
| R1 (watch) | no | **HANDOFF.** Lines 81 ("no polish, no CAD") and 97 ("within 0.51") are unchanged since 4e5b038 (22:15). The polish closed at 22:03. **Row and dashboard.** The verdict still opens "SCREENED". |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **The round-9 lead change reverses at the user's own contact line.**
   - CLAUDE.md says "contact stays metal < 1 mm". The plain v_gap counts only penetration (< 0 mm) as contact, so
     poses with metal at 0-1 mm count as clearance.
   - At 1 mm, the exact bench reads: this design **20.00**, parallelogram 20.22, roller-longdyad **20.30**
     (`remeasure/*_bench.json` deep.gap_near1). Held out at 1 mm: 25.75 / 24.44 / 26.83.
   - Roller-longdyad's plain 0.24 lead becomes a 0.30 deficit on the bench and 1.08 held out. It has 3 taken bench
     poses under 1 mm, the closest at **0.072 mm** (deep.min_metal_mm). This design has 2, at 0.28 / 0.38 mm.
   - This is T1 at the 0 mm line: the round-9 winner's gain lives where metal sits within 0.1 mm of the skin.
   - The finding bears on the lead decision, not on this design's verdict. Proposal (a rule question for the user, not
     applied): state which line the "plain verified gap" uses for contact, 0 mm as the verifier computes it or 1 mm as
     CLAUDE.md words it. Effect on the verified rows, from the files above: at 1 mm this design ranks first of the
     three on the bench (20.00 / 20.22 / 20.30); held out, parallelogram first (24.44 / 25.75 / 26.83).
2. **The ball links are not at their real size in any reading (M2 / M3).**
   - The model samples an O7 socket (`ER, ZB = 3.5, 3.0`, model line 43). The build spec uses catalogue KBRM-02 /
     KBLM-02 heads, O9 x 4, with the horn ball centre **3.6 mm** over the lug top (0.6 mm spacer;
     `docs/research/sidecar_mechanism_redteam.md` lines 166-170).
   - `tools/alignment_drive_cap_wear.py` changes only the dK cap ("Nothing else changes"), so the 19.76 catalogue
     reading still samples O7 heads at ZB 3.0.
   - The verifier's own fast ZB sensitivity is +0.39 at ZB 4.0 and +0.54 at 4.5 (row
     `verification.zb_sensitivity_fast`).
   - The real-size envelope wear (O9 heads, ZB 3.6, cap 35.4) has not been run. Neither 18.91 nor 19.76 is yet the
     built exo's number.

**Notes** (not gaming):
- **The per-pose floor peaks just above 2 mm.** In the paired exact-fit dump (`_bench_perpose.json`, gap 19.66, not the
  claim), 74 of 371 taken bench poses have their floor at 2.25-2.5 mm, against 10 at 2.0-2.25 mm.
  - Held out: 153 of 859.
  - Most are arm-low poses (median elevation 22.9 deg), and the model's crown / wall term `cmin` binds on 58 of the 74.
  - It is a fixed hub-crown standoff, not a search line: the objective was the 1 mm near-touch gap.
  - Roller-longdyad has 19 poses in the same bin.
  - It explains the 3 mm cliff (34.03 -> 155.98). A report of each hub's floor would show it (proposal A3).
- **The tool's near_touch label.** `c_near_touch` prints "points live in the 1-2 mm shell" for gap_near2 - plain, which
  is the 0-2 mm shell.
  - Proposal (reporting only; no threshold or score moves): print both shells, 0-2 mm and 1-2 mm, with their labels.
  - Effect on the verified rows on file:

    | design | 0-2 mm | 1-2 mm |
    |---|---|---|
    | this design | 15.12 | 14.03 |
    | parallelogram | 31.01 | 29.92 |
    | roller-longdyad | 14.43 | 12.80 |

**Cost:** one local exact re-wear (232 s, one process, nice), no farm, $0.

## Skeptic (2026-10-17, metric-change audit, simplicity v2)

**Final verdict (ledger tool): WATCH.** 10 of 10 reasons upheld; none refuted. Two corrections in the evidence (G5 size, and a second, unnamed condition on the sensing premise), and one new measurement: the GH-drift sensing error the audit did not run.

**What I re-measured.**

- New instrument `tools/alignment_knee_ghdrift_skeptic.py` (new file; loads the model and verifier unchanged through `tools/alignment_knee_determinacy.worn()`). Exact Bench(110,360), frozen protocol, gap 18.91 reproduced, 375 taken poses, 206.7 s, one local process (nice, OMP_NUM_THREADS=1). Output: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_skeptic_ghdrift_bench.json`. The fit bench (188 poses, 7 s) gives the same picture.
- K's law, regressed in screw convention (not from the model's own dK): slope 1.6232, residual 0.0 deg. The audit's slaving row has the right sign.
- Determinacy as a linear solve (K slaved): the passive block [pin a, pin b, GH rotation] has rank [5] at every taken pose. The hubs fix the knee pins with GH fixed. This agrees with the audit's null-space result.
- **GH drift** (arm orientation held, GH centre translated in the plane the knee can absorb): the J3 reading moves 0.8472 deg/mm (median), 1.5158 max; J1 and J2 do not move. A fixed-GH estimator reads an arm rotation that did not happen: 0.7304 deg/mm median, 1.3729 p95, 2.4102 max. Knee pins turn 3.2678-6.6445 deg/mm. At R10's 4 mm that is 2.9 deg typical and up to 9.6 deg of false arm rotation (J3 alone up to 6.1 deg). Worst pose 345 (ws, knee 146.14 deg). Skin-normal-3r-pin-knee, same question: J3 1.01 median / 1.78-1.90 max deg/mm (docs/alignment/skin-normal-3r-pin-knee.md).

**Rulings.**

- **complexity**: stands. Re-derived: docs/concepts/rows/sidecar-longdyad-knuckle-3r.json:complexity = 49.0; tools/simplicity.py score(mechanism) = 29.5 (4 prot 4, 3 loops 12, 2 bodies 2, 5 joints 5, 1 spring 3, 5 made 2.5, 4 bought 1.0, knee 0). The v1 record (cuff_knee removed, sensed_passive 2) scores 49.0 exactly, so the top-level field is the v1 number left in place. Threshold: tools/alignment_audit.py c_complexity, |row - recomputed| > 0.01 -> watch, applied to these two numbers; mechanism.confidence = 'hand count'. docs/dashboard/data/morphs.json complexity reads 29.5, so the user sees v2. No wearer cost; a records mismatch. Stands.
- **reporting**: stands. docs/dashboard/data/morphs.json for this id: gap 10.3, sweep_gap 10.3, reach 0.8, v_gap 18.91, verdict starts 'SCREENED, a candidate for the verifier'. Row gap 10.3 / reach 0.8 / verdict the same. 100(1 - 10.3/275) = 96.25; 18.91 - 10.3 = 8.61. Stands.
- **judgement:G5**: stands. Numbers reproduce (simplicity.py): v2 29.5, kneeless twin 28.0, roller-longdyad 24.25, kneeless-roller 23.75; twin delta prot 2 / joints 2 / bodies 1 / loops 1 / made 2 / bought 4. Correction to the reasoning, not the level: the template's 2 bodies / 4 made / 6 bought match the built CAD (pipeline/full-exo/designs/l1_sidecar-longdyad/parts_full.json k24 E boss, k25 knee link, k26 arm pad = pin b plate 'arm-fixed', k27-28 stop tooth/web, k29-30 retainers), and the template's 0 loops matches skin-normal's own record for the same serial knee (EXAMPLES: bodies 5, joints 5, loops 0). The row lists 7 bodies for L1a, L1b, L2, crank, rod, member 3, knee link, arm pad (8) while the twin counts the rod (6 bodies: 5 + rod, loops 2 = 8 - 6). With the rod counted, the row's own Euler count is loops 10 - 8 = 2: the 'knee closure' loop is a body-count slip, not a knee loop. Template-faithful record (bodies 8, loops 2) scores 26.5 (topology check clean), 3.0 below the recorded 29.5. So the recorded number is not the faithful one, in the unflattering direction; both rows remain hand counts. Not refuted: the mismatch the reason names exists, its size is 3.0 (not 1.5 / 2.5).
- **judgement:NEW-law-dependent-sensing**: stands. Re-measured independently with a new instrument (tools/alignment_knee_ghdrift_skeptic.py; exact Bench(110,360) frozen, gap 18.91, 375 taken poses, 206.7 s; output docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_skeptic_ghdrift_bench.json). K's law slope regressed in SCREW convention (rot_angle L1a->L1b about uK vs q2): 1.6232 deg/deg, residual 0.0 deg, so the slaving row's sign is right (the audit's 1.6232 from the model's dK). Linear-solve form: the passive block [pin a, pin b, GH rot] has rank [5] at every pose, sigma_min min 0.1125 (screw scale 1/50 mm, a different normalisation from the audit's null-space 0.310, so the two are not comparable numerically; both say determined). The condition stands as a missing measurement: K is held on its law only by the clock spring and R17 / K lag has no output on file (design.json note: R17's dynamics judge has no place for the drive members dk / dr). A second condition the reason does not name, also measured here: GH drift (see missed): J3 reading 0.8472 deg/mm median, 1.5158 max; estimated arm rotation error 0.7304 median, 2.4102 max deg/mm. Stands.
- **judgement:S1**: stands. Row v_gap 18.91; held_out.gap 22.67 (rows file); remeasure _bench.json deep.gap_near1 20.0. Trio and reversals as stated (prior skeptic re-checked the other two rows' files; unchanged since). One workspace pose = 100/360 = 0.278. Tie-break: v2 roller 24.25 vs this 29.5 (5.25); v1 43.75 vs 49.0 (5.25). With this row's template-faithful 26.5 (G5 correction) the margin is 2.25: still no flip. Stands.
- **judgement:NEW-catalogue-drive**: stands. remeasure/sidecar-longdyad-knuckle-3r_rh155cap354_bench.json frozen.gap 19.76, _held.json 23.53 (cap_deg 35.4, r_h 15.5 vs 14.87). ls pipeline/full-exo/designs/l1_sidecar-longdyad/: build.json, design.json, exo.glb, parts_full.json, no judge/. Stands.
- **judgement:NEW-unpriced-stops**: stands. rows file best_params: smlo 5.0, a1max 63.1774 = bk1 28.9414 + bk2 39.236 - 5 exactly; final_polish.min_th_margin 5.232; final_polish.priced bench_gap 19.36, held_gap 23.29, min_th_margin 5.513. Stands.
- **judgement:G1**: stands. remeasure/sidecar-longdyad-knuckle-3r_bench.json deep: n_taken 371, near2_poses 26, near1_poses 2, min_metal_mm 0.278, near3_poses 178, overhead_min_metal_p10 1.02; audit.near_touch_low 0.28 mm at ws (45, 150, -45) and 0.38 at ws (15, 90, 30). Reported, not gated (CLAUDE.md decision 3). Wearer cost real (ALIGNMENT section 1: metal at 1-2 mm on the model is metal on a real arm). Stands.
- **judgement:M5**: stands. Missing measurement: no R17 / K-lag / lift-off output for this design anywhere (grep of every json naming sidecar-longdyad; pipeline/full-exo/designs/l1_sidecar-longdyad/design.json note: 'R17's dynamics judge orders posed groups as a serial chain ... the drive's side members dk / dr have no place in it'; docs/research/sidecar_mechanism_redteam.md line 112: R17 judge fix in progress). Stands.
- **judgement:R1**: stands. Row complexity 49.0 vs v2 29.5; morphs.json gap 10.3 / reach 0.8, verdict 'SCREENED'; docs/concepts/ROUNDS.md lines 1227-1228 'halves complexity (49 -> 24-27)'. Under v2: 29.5 - 28.0 = 1.5 (sidecar), 24.25 - 23.75 = 0.5 (roller). With the G5 body-count correction the knee row (26.5) would read below its own kneeless twin (28.0), so the lesson is not merely smaller but of the wrong sign on hand counts. Stands.

**Missed by the auditor** (for the next audit; does not change this verdict):

- GH-drift sensing error not measured on this row although the v2 premise ('the 3 hub encoders fix the pose', CLAUDE.md decision 5) is shown only with GH fixed. Measured here (exact Bench(110,360) frozen, 375 taken poses, docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_skeptic_ghdrift_bench.json:gh_drift): in-plane GH drift moves the J3 reading 0.8472 deg/mm median / 1.5158 max with no arm motion, and a fixed-GH estimator reads 0.7304 deg/mm median / 2.4102 max of arm rotation that did not happen; at R10's 4 mm up to 9.6 deg. The knee's 2 encoders were in the v1 record for exactly this reason (tools/simplicity.py EXAMPLES skin-normal note: 'exact under GH translation only if all three are read'). Complexity only; never the gap.
- G5 size is wrong in the unflattering direction: the row's mechanism counts 7 moving bodies and 3 loops ('knee closure'), but its parts are L1a, L1b, L2, crank, O3 rod, member 3, knee link, arm pad = 8 bodies (rows file notes; CAD parts_full.json k25 knee link, k26 arm pad 'arm-fixed'); the kneeless twin counts the rod (6 bodies, 2 loops). With bodies 8, Euler gives loops 10 - 8 = 2 and the serial knee closes only through GH, as in skin-normal's own record (bodies 5, joints 5, loops 0). tools/simplicity.py score() on {moving_bodies: 8, closed_loops: 2} = 26.5, topology clean, vs recorded 29.5. Under that count the knee row (26.5) reads below its own kneeless twin (28.0), so ROUNDS.md round-9 lesson (1) reverses sign, and the round-9 tie-break margin is 2.25 not 5.25 (no flip).
- Stale self-contradiction in the record after 3ceacea: rows/sidecar-longdyad-knuckle-3r.json mechanism.notes still says 'pin knee (2 iglidur pins, sensed twist as the lead)' while mechanism.sensed_passive is 0 and cuff_knee.sensed is false.
- The v2 change also silences tools/alignment_audit.py c_complexity's info line 'active + sensed passive > 4 read coordinates' on all 13 pin-knee rows (sensed_passive 2 -> 0). That is consistent with CLAUDE.md decision 5 (knee outside the DOF count), but it means the audit no longer surfaces the GH-drift dependency anywhere; a record of 'sensed: false, GH drift X deg/mm' per row would keep it visible (proposal, not applied).

**Questions for the user** (unchanged in substance from the skin-normal audit, now with this row's number):

- The knee ruling rests on 'the 3 hub encoders fix the pose', shown with GH fixed. With GH drifting, this design's hub-only estimate of the arm is off by about 0.7304 deg per mm of drift (up to 2.4102). What arm-pose error per mm of GH drift is acceptable before the 2 knee encoders count again?
- K is held on its law by one 0.08 N.m clock spring, and the hub-only reading depends on it. Should R17 (K lag, lift-off) have to pass before a knuckle row may drop its knee encoders?

**Cost:** one local exact run (one process, nice) + one fit-bench run; no farm, $0.
