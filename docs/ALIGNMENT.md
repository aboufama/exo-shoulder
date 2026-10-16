# Alignment: is a better score a better exo?

The user asked for this on 2026-10-16 at about 20:10 UTC: "at the same time as all the research is happening, please
require an agent on the side that is a superfan that targets misalignment. It should understand the goal of the
project, to make a super low profile and free range shoulder joint, and see if models are cheating the system or gaming
the system in some way to score higher without actually being better. ... it needs to be a crucial part of our loop".

This file has three parts:
- the goal in physical terms;
- a catalogue of the ways a number can rise while the exo does not get better, each with a past instance from this
  project;
- an audit of the verified leaderboard, with proposals.

The instrument is `tools/alignment_audit.py`. Its per-design outputs are in `docs/alignment/<id>.json`, and its
re-measurements are in `docs/alignment/remeasure/`.

"Gamed" here means the number, as it stands, is not evidence of a better exo. It does not mean anyone cheated on
purpose. Every case below came from a search or a model doing exactly what its objective asked.

## 1. What "better" means for the wearer

A better design is one the wearer notices less while moving more freely. Physically:

1. **Close, never touching.** Every piece of metal rides about 1 cm off the skin: 2-14 mm passes and 10 mm is the aim.
   This holds in every posture the arm reaches. Skin is soft and moves: it bulges with the deltoid and slides over the
   acromion. Metal at 1-2 mm on the model is metal on the skin of a real arm. Metal at 25 mm is a bump that catches on
   a doorway.
2. **Free range, overhead most of all.** The wearer's arm goes everywhere it naturally goes, including overhead, as one
   continuous motion. The exo never stops the arm, jams or flips branch, and it never needs a hand to reset it.
3. **Felt as nothing.** No spring the wearer pushes against, no cuff that twists on the arm, and no joint that sits near
   a singular posture where small arm motions swing it fast.
4. **Real and simple.** At most 4 DOF, 3 preferred. Every joint is a real component at its real size (O20 hubs). The
   fewer parts, loops, springs and sensors, the better.
5. **It tracks the arm unpowered (MVP1).** Every coordinate is determined by the arm, or sprung and stopped, or
   sensed.

The score proxies these only in part:
- gap = 100 [(0.90 - in-band14)+ + (0.95 - follow)+ + (0.90 - reach)+] + 100 contact, and score = 100 (1 - gap / 275);
- the benches are Bench(60,160) fast and Bench(110,360) exact;
- the protocol adds the frozen shape, the held-out set, the near-touch gap, the continuity flood, the 5-deg fold margin
  on `th`, and complexity from `tools/simplicity.py`.

Each piece of that proxy has a blind spot. The catalogue lists them.

## 2. Catalogue of gaming patterns

Each entry gives:
- **Looks like**: the pattern in the numbers.
- **Why not better**: the physical reason it is not a better exo.
- **Detect**: the automatic check (in `tools/alignment_audit.py` unless stated).
- **Here**: the project's past instance, with its numbers and file.

### T. Metric and threshold exploits: sitting just past a cutoff

**T1. Metal parked just outside the contact cutoff (the 0 mm, then 1 mm, line).**
- **Looks like:** contact 0 and a good plain gap, but the 1 mm and 2 mm near-touch gaps jump. Many taken poses have
  metal 0.1-2 mm off the skin.
- **Why not better:** a real arm has skin bulge, cuff slip and build tolerance of a few mm. A pose taken at 0.3 mm is
  a pose with metal on skin.
- **Detect:** `near_touch` re-wears the claim and counts poses with metal < 1 / 2 / 3 mm as contact. It flags watch
  when > 15 points of the gap depend on the 1-2 mm shell, and gamed when > 25.
- **Here:**
  - Plain-gap CMA optima put metal within 1 mm on 15-20 % of poses and lost 8-27 points frozen (CLAUDE.md "Search on
    the near-touch gap", the arm-parked-knee-4r screen). That case created the 1 mm rule.
  - The 1 mm rule then moved the metal to 1-2 mm. sidecar-parallelogram scores 19.13 plain and 20.22 at 1 mm, but
    50.14 at 2 mm, with 44 frozen poses at 1-2 mm (`rows/sidecar-parallelogram-knuckle-3r.json`; the verifier's own
    reading is 50.41).

**T2. In-band read at the band edge (2 mm).**
- **Looks like:** in-band14 rises because metal samples crowd 2-3 mm off the skin.
- **Why not better:** 2.0 mm counts as in band and 1.9 mm does not, but the wearer cannot tell them apart. The aim is
  10 mm.
- **Detect:** `near_touch` reports the gap with the band read as 3-14 mm, and the histogram of metal distances on taken
  clip frames.
- **Here:** see the re-measured round-8 table in section 3.

**T3. The fold margin read on a different angle.**
- **Looks like:** the claim keeps "5 deg" from the fold, but measured on an angle other than `th`.
- **Why not better:** near the fold the J2 dyad is near-singular. Small arm motions swing the links fast and the
  transmission stiffens: the wearer feels a jerk or a jam.
- **Detect:** `fold_margin` takes the minimum `th` margin on file over the taken poses. It flags gamed below 5 deg,
  and watch when no claim reports it.
- **Here:** minarc variant B scored 15.42 with stops at 5 deg of the J2 interior angle, which is 1.4 deg of `th`. At the
  true 5 deg it scores 18.45 (FINDINGS "The knuckle's 15.42 needs J2 stops inside the fold margin"; rows/minarc *.v_kitrule_*).

**T4. Self-set search bounds walk toward a singular posture.**
- **Looks like:** a polish gains reach, and its knee or other window bound sits at the search tool's own limit.
- **Why not better:** it spends the singularity margin, which the user's ruling guards.
- **Detect:** `rules` checks the declared margins. A bound at the search box edge is flagged in review (not yet
  automatic; proposal A6).
- **Here:** the pin-knee GPU polish lowered the knee's ang_min from 30.5 to 22-23 deg, with the bound at 20. The
  polish-protocol gain fell from 3.7-4.2 to 0.57 once H1's window was restored, and the held-out gain became -0.08 and
  -0.73 (FINDINGS "The pin-knee GPU polish's held-out gain is the knee's singularity margin").

### S. Sampling exploits: what the bench does not look at

**S1. A skewed pose sample.**
- **Looks like:** a polish wins in sample and loses held out.
- **Why not better:** the wearer moves through the whole workspace, not through the bench's linspace slice of it.
- **Detect:** `held_out` compares held-out with the bench gap. It flags watch above +6 and gamed above +10.
- **Here:** every in-sample polish lost about 5 points held out. The search benches have 6 % of poses at |axial| >= 150
  against 11 % held out (FINDINGS "A 2-fold cross-fit polish does not travel either"). P5 was refuted out of sample.

**S2. Sparse sampling of bad metal.**
- **Looks like:** in-band is sample-weighted, so a part that is far from the skin but lightly sampled barely moves it.
- **Why not better:** a rod 22 mm off the skin is a bump the wearer feels, however few samples it has.
- **Detect:** `sampling` compares sample-weighted with part-weighted in-band. It lists parts with < 16 samples and parts
  mostly out of band, with their share of samples.
- **Here:** frontload's rod and rod ends are 0.00 in band (median 22 mm) on 5.5 % of samples. Sample-weighted in-band
  is 0.856, but part-weighted it is 0.798 (`verify/frontload-*_claim_bench_frozen.json`).

**S3. Unsampled bodies.**
- **Looks like:** a body exists in the mechanism, but no metal group samples it.
- **Why not better:** an unscored link can sit anywhere, including on the skin.
- **Detect:** `sampling` compares declared moving bodies with sampled non-hub groups, and flags any part with 0
  samples.
- **Here:**
  - The geneva-tail CMA's 16.10 was a plain 3R with an unscored link 1b (FINDINGS "Idle-drive search optima").
  - The CAD judge did not count `l1a` / `l1b`. The new rule makes the judge stop on an unlisted group
    (`pipeline/full-exo/metal_groups.py`).

**S4. Contact on the skin sample, not the body.**
- **Looks like:** contact is judged by signed distance to one posed skin mesh. Self-overlapping body parts and the
  scapula's own motion live in the model.
- **Detect:** not automatic. The data-wins rule (`data/raw`) covers it.
- **Here:** R2 reads 24.87 mm on every build because of the rig's self-intersection (HANDOFF section 4). That number is
  a measurement artefact, not a design property.

**S5. Static islands.**
- **Looks like:** reach counts each pose on its own, so a design with a relayed, sprung or redundant coordinate takes
  poses that no continuous arm motion reaches.
- **Why not better:** the wearer cannot get there without a hand to reset the mechanism.
- **Detect:** `continuity` reads static against connected (full, knn and bench-graph floods). It flags watch when the
  rule's flood loses > 1 point and gamed when it loses > 3. It also flags watch when a design with passive coordinates
  has no flood on file.
- **Here:** stop-relay-rocker-3r scored 29.82 fast and was refuted at 50.36 (ROUNDS.md round 4). That case created the
  continuity rule.

### M. Model-reality gaps: the model has something the world does not

**M1. Virtual or zero-size parts.**
- **Looks like:** slides with no carriage height, stages of zero height, three passive translations.
- **Why not better:** no such part exists at that size, so the built exo is taller or cannot be built.
- **Detect:** `complexity` and `rules` flag gamed above 2 passive translations or above 4 active DOF.
- **Here:** seed-offset-3r-slides still has status "verified" (66.47) with 3 passive translations in series. Its own
  record says "NOT BUILDABLE" (`rows/seed-offset-3r-slides.json`).

**M2. Components that do not exist at that size.**
- **Looks like:** hubs slimmer than the user's O20 stack.
- **Why not better:** the user ruled "Keep O20 only".
- **Detect:** `rules` checks hub radii in the params. `CB_ALLOW_SLIM` must be off.
- **Here:** the O15 "crest basin": hub 2 is 0.9975 in band at O15 and 0.03 at O20 at the same seats (FINDINGS round 6).
  spine-parked's slim-hub number does not stand.

**M3. Unchecked clashes.**
- **Looks like:** two parts share space and nobody checked them against each other.
- **Detect:** verifier-side. Add every new part to every hub-stack and cap check (ROUNDS.md round 7 lesson 6).
- **Here:** the frontload claim's horn and rod-end head sat inside K's spring cap. The verifier's correction cost +0.20
  (ROUNDS.md, verify/frontload `_corr_`).

**M4. Idle mechanisms.**
- **Looks like:** a declared drive or joint never moves over the taken poses, so the score belongs to a simpler
  mechanism while the complexity and the story belong to the complex one.
- **Detect:** `idle` reads the recorded drive ranges (dK) and the re-measured coordinate spans. It flags gamed below 2
  deg, and watch when no range is on file.
- **Here:** the geneva tail CMA's idle drive (16.10, K idle) and split-knuckle's K2-idle 22.34 sweep minimum (FINDINGS
  round 6 and round 7 "Search hygiene").

**M5. Springs that cannot hold, and sensors that are not counted.**
- **Looks like:** a spring-held coordinate is scored at its planned value.
- **Why not better:** the real spring lags, stalls, or holds the arm back.
- **Detect:** not automatic. It needs the dynamics judge (R17) and a posture sweep.
- **Here:** pick1's K at 0.08 N.m preload lagged 9.28 deg on Reach a high shelf (R17 fail). At 0.04 N.m it passes
  upright only, drifting 4.1-7.7 deg with gravity across the thorax (FINDINGS "pick1's K hold";
  `docs/research/pick1_k_hold_check.md`).

### P. Protocol exploits

**P1. In-sample tuning.** Fitting and claiming on the same poses. Detected by `held_out`; see S1.

**P2. Held-out leakage.** Searching on held-out poses, or choosing among many configs by their held-out number.
- **Detect:** review only. A search script that imports `held_bench()` is a red flag. The rule is that final polishes
  search on the env bench and claim held out.

**P3. Re-measuring until lucky.** Many re-wears or seeds, with only the best reported.
- **Detect:** `fast_frozen` flags a row whose headline gap is far from its verified number. Reporting best-of-many
  needs the spread (R3).

**P4. Changing the judge with the design.**
- **Looks like:** a judge default or metric moves in the same commit or task that moves the design's number.
- **Detect:** `judge_change` walks `git log` of the row. It lists every commit that changed the row's gap and also
  touched a bench, kit, judge or metric file.
- **Here:** `judge/dynamics.py` began reading a design's declared preload, with 0.08 N.m as the fallback, in the same
  task that lowered pick1's preload to 0.04 N.m. pick1's R17 went from fail to pass (6 -> 7/19; FINDINGS "pick1's K
  hold"). It was stated as a measurement change, which is the right handling, but the pattern is the one to watch.

### R. Reporting exploits

**R1. Self-measured numbers shown as verified.**
- **Detect:** `reporting` compares the row status, the verifier files and the dashboard. It flags a verified row whose
  verdict still reads as a self-measured screen.

**R2. Refuted records still displayed.**
- **Looks like:** the dashboard's sweep "record" line and per-design sweep best show numbers the verifier refuted.
- **Here:** minarc's 6.19 (score 97.75) is still the all-time record in `docs/dashboard/data/sweeps.json`, against the
  verified 18.40 / 19.54.

**R3. Best-of-many without the spread.**
- **Looks like:** a CMA's best of 7000 tries is reported as the design's number.
- **Detect:** `fast_frozen` reports the self-measured to verified drop. Over the verified rows it is 4.6-14 points.

**R4. A reporting pipeline that recomputes the number.**
- **Found by this audit:** `tools/dash_build.py` rebuilds `v_gap` from `v_inband14`, `v_follow`, `v_reach` and
  `v_contact`. When a row has no `v_contact` it falls back to the row's fast contact (usually 0). The dashboard
  therefore shows verified numbers the verifier never measured:
  - sidecar-longdyad 17.84 against the verified 18.91;
  - sidecar-parallelogram 18.06 against 19.13;
  - geneva rod 23.04 against 23.57;
  - zc-frontier 31.70 against 33.51;
  - refuted rows also flattered: posterior-max-margin-cardan 80.76 against 87.47, short-a2 50.98 against 55.30.

### G. Goal drift: reach bought with things the wearer would feel

- **G1. Metal hugging at 1-3 mm** (T1 and T2 from the wearer's side). An in-band gain that comes from moving metal from
  8 mm to 2.5 mm is a worse exo: it touches the arm through clothing and tissue bulge. **Detect:** the `near_touch` and
  `dominance` checks.
  - `dominance` compares a design with a reference row (by default the previous verified 3-active lead, frontload).
  - It flags gamed when the design beats the reference on the plain gap and loses to it at 2 mm.
- **G2. Stiff springs** that buy a planned state the wearer then has to push against. **Detect:** R17 and the preload
  sweep (judge side).
- **G3. Cuff twist** when a spring-held coordinate lags. pick1's 0.08 N.m preload twisted the cuff 4.64 deg.
  **Detect:** R17.
- **G4. Singular postures** (T3 and T4).
- **G5. Complexity hidden by the count.** **Detect:** `complexity` recomputes `tools/simplicity.py` and checks the DOF
  cap and passive translations.
  - minarc's K is a sensed, spring-held 4th joint in the shoulder chain, not at the cuff. The leaderboard calls the
    design "4 active", and its CAD fails R5-aim (4 DOF).
  - Its mechanism record still counts K as a sensed passive: 6 points instead of 25 for a 4th active DOF. That gives
    complexity 33 against 52 with K counted active (measured with `tools/simplicity.py`).
  - The user's question "does a sensed passive used only at static extremes count as passive?" is open (HANDOFF
    section 7), and the count pre-answers it in the design's favour.
- **G6. A 4th sensed joint versus 3 active.** It is the same issue as G5, seen on the leaderboard.

## 3. Audit of the verified leaderboard

To reproduce:

```
python3 tools/alignment_audit.py audit-all
python3 tools/alignment_audit.py table
CB_EXACT=1 nice python3 tools/alignment_audit.py remeasure <id> bench|held
```

The audit covered every row with status `verified` plus the round-8 sidecar family. Sources:
- the round-8 sidecars were re-worn here with their own models, unchanged (`docs/alignment/remeasure/`);
- every other row uses the verifier outputs and row fields on file.

Columns:
- **verified gap** is the row's `v_gap`.
- **held out** is the held-out gap, with its drop from the bench.
- **near-touch** is the gap with metal under 1 / 2 / 3 mm counted as contact. The bracket is the number of points that
  exist only if 1-2 mm metal is acceptable.
- **continuity** is static -> connected, read with the full-envelope flood and then the knn flood.
- Each verdict's reasons are in `docs/alignment/<id>.json`.

The table, as of 2026-10-16 ~20:40 UTC:

| design | status | verified gap | held out (drop) | near-touch 1 / 2 / 3 mm (shell 1-2) | continuity static -> connected | complexity | verdict | main reasons |
|---|---|---|---|---|---|---|---|---|
| sidecar-longdyad-knuckle-3r | verified | 18.91 | 22.67 (+3.76) | 20.0 / 34.03 / 155.98 (15.12) | 18.91 -> 18.91 / 21.72 | 49.0 | **watch** | near_touch; fold_margin; reporting |
| sidecar-parallelogram-knuckle-3r | verified | 19.13 | 22.03 (+2.90) | 20.22 / 50.14 / 150.75 (31.01) | 19.13 -> 19.13 / 22.21 | 49.0 | **gamed** | near_touch; dominance |
| minarc-stop-knuckle-4r | verified | 19.54 | 24.18 (+4.64) | 26.44 / None / - (None) | watch | 33.0 | **watch** | near_touch; continuity; sampling; reporting |
| frontload-lobe-stopb-knuckle-3r | verified | 22.82 | 26.65 (+3.83) | 24.36 / 43.98 / - (21.26) | 22.82 -> 22.82 / 25.63 | 49.0 | **watch** | near_touch; fold_margin; sampling; reporting |
| geneva-tail-knuckle-pinknee-3r | verified | 23.57 | 27.92 (+4.35) | 25.21 / 38.84 / - (15.27) | 23.57 -> 23.57 / 26.1 | 42.5 | **watch** | near_touch; fold_margin; sampling; complexity; reporting |
| twist-long-a2-knuckle-3r | dead | 24.46 | - | 27.7 / None / - (None) | watch | 49.0 | **watch** | held_out; near_touch; continuity; fold_margin; idle; sampling; complexity; reporting |
| cam-unfold-4th | verified | 26.7 | - | 28.4 / None / - (None) | watch | 33.75 | **watch** | held_out; near_touch; continuity; fold_margin; idle; sampling; reporting |
| arm-parked-knee-4r | verified | 26.71 | - | 31.99 / None / - (None) | watch | 32.25 | **watch** | held_out; near_touch; continuity; fold_margin; sampling; reporting |
| skin-normal-3r-pin-knee | verified | 27.2 | - | 31.75 / 46.85 / - (19.65) | watch | None | **watch** | held_out; near_touch; continuity; fold_margin; sampling; reporting |
| raglan-knee-3r | verified | 27.82 | - | - | watch | None | **watch** | held_out; near_touch; continuity; fold_margin |
| j3-neck-over-3r | verified | 28.46 | - | 35.44 / None / - (None) | watch | 13.5 | **watch** | held_out; near_touch; continuity; fold_margin; sampling; reporting |
| skin-normal-3r-knuckle-cufflink | verified | 29.1 | - | - | watch | None | **watch** | held_out; near_touch; continuity; fold_margin; idle; sampling |
| zc-frontier-3r | verified | 33.51 | - | - | ok | None | **watch** | held_out; near_touch; fold_margin; sampling; reporting |
| dwell-fourbar-knee-3r | verified | 37.66 | - | - | watch | 19.0 | **watch** | held_out; near_touch; continuity; fold_margin; sampling; complexity; reporting |
| spine-parked-j2-3r | verified | 41.0 | - | - | ok | None | **watch** | held_out; near_touch; fold_margin; sampling; reporting |
| offset-skin-normal-3r | verified | 41.02 | - | - | watch | None | **watch** | held_out; near_touch; continuity; fold_margin; sampling; reporting |
| k-rim-lobe-stub-knuckle-3r | verified | 44.79 | - | 53.51 / 71.68 / - (26.89) | 44.79 -> 44.79 / 46.48 | 34.0 | **gamed** | near_touch |
| seed-offset-3r-slides | verified | 66.47 | - | - | watch | None | **gamed** | complexity |
| sidecar-roller-flank-knuckle-3r | screened | None | - | 21.17 / 46.82 / - (26.74) | watch | 45.25 | **gamed** | near_touch; dominance |

### What the audit found

1. **The round-8 sidecars reproduce to the digit.** Re-worn here with the models unchanged
   (`docs/alignment/remeasure/*_bench.json`), they measure:
   - sidecar-longdyad 18.91, and sidecar-parallelogram 19.13;
   - near-touch at 1 mm 20.00 / 20.22, and at 2 mm 34.03 / 50.14.

   The scores are not fabricated. The question is what they buy.
2. **sidecar-parallelogram is gamed on the 1-2 mm shell (T1 / G1).**
   - 31.0 of its points depend on accepting metal at 1-2 mm, on 44 taken poses.
   - Against the previous verified 3-active lead (frontload), it is 3.59 better plain but 6.16 worse at 2 mm.
   - roller-flank shows the same pattern from its self-measured numbers: 2.64 better plain, 2.84 worse at 2 mm.
   - The 1 mm near-touch rule moved the problem 1 mm outward rather than solving it.
   - sidecar-longdyad is the clean one of the three: 15.1 points in the shell, and better than frontload at 2 mm by
     9.95. **Its lead is real.**
3. **The band edge is not exploited (T2 clean).** On taken clip frames only 0.3 % of the sidecar metal samples sit at
   2-3 mm. Reading the band as 3-14 mm costs longdyad 0.31 points and parallelogram 0.00.
4. **Per pose, the worst point is close.** For both sidecars, 169-178 of about 370 taken poses have some metal (a hub
   crown or edge) under 3 mm. The 10th-percentile overhead pose has metal at 1.0-1.2 mm.
   - The sample-share in-band (0.90) hides this: it is a metal-area average, not a per-pose worst case.
   - The wearer feels the worst point. This is a gap between the score and the goal, not a gamed design: it applies to
     every row (proposal A3).
5. **The dashboard flatters verified numbers (R4).** `tools/dash_build.py` recomputes `v_gap` and drops the contact
   term when a row has no `v_contact`. Displayed against verified:

   | design | dashboard | verified |
   |---|---|---|
   | sidecar-longdyad | 17.84 | 18.91 |
   | sidecar-parallelogram | 18.06 | 19.13 |
   | geneva rod | 23.04 | 23.57 |
   | zc-frontier | 31.70 | 33.51 |

   The sweep "record" is still minarc's refuted 6.19 (score 97.75), and each verified row's dashboard sweep best sits
   5.6-13.4 points under its verified number. This is a pipeline defect, not a design one, so the per-design verdict
   shows it as watch.
6. **minarc's complexity counts its 4th joint as passive (G5).**
   - K is a sensed, spring-held joint in the shoulder chain. The leaderboard and the CAD (R5-aim fails, 4 DOF) treat it
     as a 4th DOF, but `rows/minarc-stop-knuckle-4r.json` mechanism has `active_dof: 3, sensed_passive: 3`.
   - Counted as the 4th active DOF, the complexity is 52, not 33 (`tools/simplicity.py`).
   - The user's question on this is still open (HANDOFF section 7.1).
7. **A sample-weighted in-band hides the drive's height (S2).**
   - frontload's rod and rod ends are 0.00 in band (median 22 mm off the skin) but carry only 5.5 % of the samples.
     Part-weighted in-band is 0.798 against the score's 0.856.
   - The sidecars fixed exactly this: rod 0.89 in band and crank 0.91. That is why longdyad's gain is real.
8. **Continuity depends on which flood is read.**
   - The full flood uses 1039 envelope poses as stepping stones and drops 0 poses on every knuckle row.
   - The knn flood (bench poses only) costs:

     | design | knn flood cost |
     |---|---|
     | longdyad | +2.81 |
     | parallelogram | +3.08 |
     | frontload | +2.81 |
     | geneva | +2.53 |

   - The rule names `connected()` without naming the graph. The ranking does not change, but the absolute number does
     (proposal A4).
9. **Missing evidence on verified rows.** 12 of the 17 verified rows have no held-out number on file and 11 have no 2 mm
   near-touch. 16 record no min `th` margin over taken poses (CLAUDE.md requires it of each claim); only minarc does,
   at 5.007 deg. Those rows
   are older than the rules. They are watch, not gamed, and none of them leads.
10. **seed-offset-3r-slides still has status "verified" with 3 passive translations (M1).** Its own record says NOT
    BUILDABLE.
11. **No judge or bench file changed in a commit that moved a verified row's number** (`judge_change` is ok on every
    row). The one P4 instance found was the R17 preload default (section 2, P4). It was a CAD judge, outside the row
    history, and it was stated as a measurement change.

Not yet re-measured here (queued, `docs/alignment/remeasure/`): the held-out wear of longdyad and parallelogram with
3 mm near-touch, and roller-flank's bench wear. Their verifier numbers are on file and are used above.

## 4. Proposals (not applied; each is a measurement or reporting change for the lead / the user to decide)

Each proposal gives its measured effect on the rows that have the data. A row without the data is listed as such.

**A1. Make the 2 mm near-touch gap the claim column, and add a dominance gate.**
- **Proposal:** a design replaces the lead only if it beats it on the plain gap AND on the 2 mm near-touch gap. Searches
  keep the 1 mm objective but also report 2 mm.
- **Effect** (2 mm gap; rows without a 2 mm reading are not ranked):

  | design | 2 mm near-touch gap |
  |---|---|
  | sidecar-longdyad | 34.03 (the leader at 2 mm by 4.8) |
  | geneva rod | 38.84 |
  | frontload | 43.98 |
  | pin-knee H1 | 46.85 |
  | roller-flank | 46.82 (self) |
  | parallelogram | 50.14 |
  | k-rim-lobe | 71.68 |

  - Missing: minarc BDp / pick1, cam-unfold, arm-parked, j3-neck, raglan and the rounds 1-3 rows.
  - The ranking changes in two places. Parallelogram falls from 2nd to 6th of the rows with data, and frontload falls
    behind the geneva rod it was a re-fit of.
  - Longdyad keeps the 3-active lead.

**A2. The dashboard shows the verifier's `v_gap` verbatim.** Never recompute it, and print "-" when `v_contact` is
missing. Sweep bests and the record line show only configs a verifier did not refute.
- **Effect:** the dashboard numbers become the verified ones (section 3, item 5; 20 rows differ today).
- The record line moves from 6.19 (score 97.75) to the verified 18.40 (93.31).
- This is a reporting change. No score moves.

**A3. Report the per-pose worst point.**
- **Proposal:** add the 10th-percentile per-pose min-metal and the share of taken poses with metal under 3 mm to every
  claim. A future ruling could cap it, for example at 25 % of taken poses under 3 mm.
- **Effect:** longdyad has 178 of 371 taken poses (48 %) under 3 mm, and parallelogram 169 of 369 (46 %). Overhead p10
  is 1.02 / 1.17 mm. Other rows are not measured yet: run
  `python3 tools/alignment_audit.py remeasure <id> bench` on knuckle-family rows.
- The cap would block every current design, so it is the user's call. It is the most direct reading of "about 1 cm,
  never touching".

**A4. Name the continuity graph in the rule.** Report both the full-envelope flood and the knn flood, and claim on the
knn flood: it uses only bench poses as stepping stones, so it is the stricter of the two.
- **Effect:**

  | design | knn flood claim | today's number |
  |---|---|---|
  | longdyad | 21.72 | 18.91 |
  | parallelogram | 22.21 | 19.13 |
  | frontload | 25.63 | 22.82 |
  | geneva rod | 26.10 | 23.57 |
  | k-rim-lobe | 46.48 | 44.79 |

  - The order is unchanged.
  - minarc pick1 / BDp and the older rows have no knn number on file.

**A5. Count a sensed joint in the shoulder chain as active until the user rules.** Cuff-side passives stay outside the
count.
- **Effect:** minarc goes from 33 to 52, and is then the most complex verified knuckle. The other verified rows' sensed
  coordinates are at the cuff (pin knee), so they do not change. j3-neck-over-3r's K is not in its mechanism record,
  so it is unmeasured.

**A6. Flag a search bound at the edge of its box.** A searched window or margin within 1 deg of the search tool's own
bound is flagged before a claim.
- **Effect:** none on today's verified rows (H1's ang_min 30.46 is a ruling, not a box edge). This is the test that
  would have caught the GPU knee polish early.

**A7. "Verified" requires a held-out number, a 2 mm near-touch and the min `th` margin.** Older rows keep their
status, flagged "verified (pre-2026-10-16 rules)".
- **Effect:** 16 of 17 rows flagged on the `th` margin, 12 on held out and 11 on the 2 mm near-touch. Of the top 5, the
  4 knuckle-family rows lack only the `th` margin.

**A8. A row with more than 2 passive translations cannot carry status "verified".**
- **Effect:** seed-offset-3r-slides becomes "unbuildable". No other row changes.

**A9. Commit every bench, judge or metric change on its own, before the design change it enables, with the
before / after of every built design.**
- **Effect:** process only. `judge_change` then catches any exception automatically.

## 5. How this runs in the loop

- **After every screen, before a verifier is launched:**
  `python3 tools/alignment_audit.py audit <id> --ref <current verified lead>`. A `gamed` verdict goes into the
  verifier's brief as the first thing to refute.
- **After every verifier, before a row counts:** run `remeasure <id> bench` and `held`, then `audit`. The
  `docs/alignment/<id>.json` verdict sits next to the number on the dashboard.
- **Before a generation-winner CAD or a polish swap:** the candidate must not be `gamed` on `near_touch`, `dominance`,
  `continuity`, `fold_margin` or `idle`.
- **Hourly:** `audit-all` (data only, a few seconds). Diff the verdicts and report new `gamed` rows to the lead.
- **Thresholds** (`TH` in the tool) are set from the verified rows:
  - held-out drop: watch > 6, gamed > 10 (the verified rows drop 2.9-4.6);
  - 1-2 mm shell: watch > 15, gamed > 25 (the 3-active leaders sit at 15-31);
  - connected loss: watch > 1, gamed > 3;
  - idle: < 2 deg;
  - part-weighted in-band: watch > 3 points, gamed > 8.

  Changing a threshold is a measurement change and is stated as one.
