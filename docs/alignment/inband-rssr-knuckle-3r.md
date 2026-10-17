# Alignment audit: inband-rssr-knuckle-3r

Auditor run 2026-10-17 11:03-11:35 UTC (hourly audit, new screened row). Checks: `docs/alignment/inband-rssr-knuckle-3r.json`
(tool VERSION 2026-10-17.2, `--ref slipper-nose-knuckle-3r`). Findings: `docs/alignment/inband-rssr-knuckle-3r.findings.json`.
Ledger: `docs/alignment/ledger.jsonl`, `by auditor`, run `audit:inband-rssr-knuckle-3r`.

## Verdict: WATCH (no gamed reason; the number is real, the claimed tie holds, the record overstates two things)

- **The claim.** Status screened. The leak-free pick cma3 p, frozen exact Bench(110,360), is **18.87** (score 93.14),
  held out **23.21**. The robust build is 18.83 / 23.16. The row's verdict calls this parity with the leader
  slipper-nose (18.49 / 23.45; paired pooled -0.06, 90 % CI [-0.44, +0.39], P 0.55), not a lead. The ledger's claim field
  is the row's top-level `gap`, which is **16.47**: the fit-bench 2 mm objective, an in-sample number (finding R4).
- **Re-worn here, model unchanged** (local, CB_EXACT=1, 1 core each; `docs/alignment/remeasure/inband-rssr-knuckle-3r_{bench,held}.json`):
  - bench **18.87**, held **23.21**: both reproduce to the digit;
  - near-touch 1 / 2 / 3 mm: 19.96 / 34.12 / 81.99 on the bench, 26.53 / 36.97 / 80.26 held out;
  - band read as 3-14 mm: 19.01 / 23.35.
- **Reasons.** The tool gave 2 watch checks and 0 gamed:
  - `held_out`: the row is not verified, so there is no verified gap to compare with.
  - `idle`: the same instrument false positive the skeptic refuted on slipper-nose. The 66.82 deg "knee" span is
    `K.qa`, the pin knee's designed motion. This row runs the lead cell (pin knee, `mechanism.cuff_knee.pins` 2), and
    K moves 45.83 deg.

  The judgement pass adds 5 watch findings: M2, NEW-pair-knife-edge, NEW-inband-padding, R4 and M5.
- **Why nothing is gamed.** The design does not rank above a design that is better for the wearer under the same
  harness:
  - it is 0.38 behind the leader plain and 1.10 behind at 2 mm (dominance check);
  - the pose-by-pose wearer numbers below are the leader's to within a pose;
  - the catalogue-part re-wear (M2) keeps the robust build's 18.83.

## The five questions this audit was sent with

1. **Was the pick rule committed before results, and did any held-out number leak into the selection? No leak found.**
   - The rule (lowest fit-bench 2 mm objective among the law-free cma3 runs) is in commit `b6cfa9b` at 09:36:11 UTC. The
     file stamps itself "09:40Z", 4 minutes after the commit that contains it, which is a clerical slip; the git time is
     the proof.
   - The first cma3 output was committed at 10:12:05 (`a0a457d`). The pick (`f8fd767`, 10:10:20) holds fit-bench numbers
     only.
   - The claim-bench and held-out files come after: `farm/claimA/p_bench.json`, `p_held.json` at 10:17,
     `claimB/rob_held.json` at 10:19.
   - The robust build was defined by a fit-bench tolerance scan (`out/tol_rob.jsonl`, 10:14:40) before any held-out
     number.
   - The seeds (the long-stroke row's fit-bench CMA bests g65d / s65n2d / r75a) carry no held-out number. Their law
     floor is not used: the pick's kK is 1.79 against the leaky table's 3.0.
   - Four configurations were worn held out (pick, robust, secondary cma1 f, post-hoc cma3 o), and the pick did not
     move.
2. **The radial crank stud at 25.5 deg against a 30 deg cone: buildable with a catalogue part?**
   - **The cone, yes.** The repo's catalogue M2 link (igus KBRM-02, `docs/research/sidecar_mechanism_redteam.md` lines
     24 and 87) tilts 30 deg.
   - **The row's red team has the binding place wrong.** The 25.5 deg peak is at the drive's rest (K = 0), not at the
     top of the taken range. Fit-bench scan, model unchanged, CONE overridden in memory:
     - the pick keeps dK_lim 65.8 down to a 25.5 deg cone;
     - the robust build (25.9) dies at 25.5 (dK_lim 0.0, fit 108.88);
     - the pick at a 25 deg cone, frozen exact: **96.44** (dK_lim 0.0, why `cone`;
       `remeasure/inband-rssr-knuckle-3r_bench_CONE25.json`).

     So any link under ~26 deg cannot assemble the drive at all.
   - **The head, not as modelled.** The sockets are sampled at O7. The catalogue head is O9 x 4. With the catalogue
     head (SC.ER 4.5) the pick and the robust build lose every pose to the ROD-hubK pair (275.0, frozen exact). The
     red team's own fix (horn radius r_h 15.9) restores the design: **18.83** bench (`remeasure/..._cat-rh15.9_bench_SC.ER4.5.json`),
     held out **23.17** (`..._cat-rh15.9_held_SC.ER4.5.json`). Finding M2.
3. **Knife edge: is the robust build's 18.83 / 23.16 the honest number? Yes, and it is also the catalogue-head
   number on the bench.**
   - The pick holds its closest part pair at 1.062-1.181 mm on every taken pose (leader 1.31-5.11).
   - 11 of its 34 tolerance neighbours lose every pose, and 5 more cost +6.5 to +7.4.
   - The robust build passes all 34 neighbours (fast plain 12.50-13.05). It costs nothing (0.04 / 0.05 better).
   - The headline should be the robust build's (finding NEW-pair-knife-edge).
4. **Contact depth.** The tool's check could not run: it reads the claim as 16.47 and the dumps reproduce 18.87 /
   23.21. I copied the dumps into `docs/alignment/remeasure/` and measured the depths by hand from those files:

   | wear | this row | leader slipper-nose |
   |---|---|---|
   | bench | 3 contact poses, summed 9.86 mm; deepest 9.72 mm at plane 15, elevation 165, axial -60. The other two are 0.09 (pose 264) and 0.04 mm (pose 139). | 2 poses, 14.75 mm; deepest 9.01 at the same pose 237, and 5.74 at pose 264 |
   | held out | 9 poses, 23.20 mm; deepest 8.71 at (30, 165, -45), then 5.50 at (-90, 60, 120) and 3.85 at (-90, 60, 105) | 10 poses, 46.12 mm; deepest 9.05 at the same pose; 7 poses deeper than 3 mm against 3 here |

   T5 is clean: the row presses half as deep as the leader held out.
5. **The envelope-bench polish of this row (final-polish workflow wf_d261725f-27c), running now.** See "What the polish
   must not exploit" below.

## What the wearer gets (measured, Bench(110,360) exact, frozen; held out in brackets)

Probe: `remeasure/inband-rssr-knuckle-3r_probe_bench.json` (`..._probe_held.json`). Re-wear:
`remeasure/inband-rssr-knuckle-3r_{bench,held}.json`.

- **Overhead (elevation >= 140):** 8 of 28 workspace poses taken (19 of 71 held out). Lost to the fold 14, knee slide 4,
  contact 2 (36 / 11 / 5). The bench is identical to the leader; held out it takes one overhead pose more (the
  leader takes 18 of 71).
- **Raised arm:** reach by elevation band:

  | elevation | 90-120 | 120-140 | 140-160 | 160-200 |
  |---|---|---|---|---|
  | poses taken | 26 / 51 | 12 / 34 | 5 / 13 | 3 / 15 |

  Workspace reach in all is 260 / 360 = 0.722 (0.683). The leader takes 261; the missing pose is in the 60-90 band.
- **Taken poses with metal under 2 mm:** 31 of 370 (68 of 852); the leader has 30 (67).
  - Under 1 mm: 2 poses (15). The lowest is 0.65 mm on the bench and 0.03 mm held out.
  - Overhead: 4 of the 8 taken workspace poses and 5 of the 10 clip poses have their lowest metal at 1-2 mm.
  - Overhead p10 of the lowest metal: 1.82 mm (1.22).
- **Deepest contact:** 9.72 mm at plane 15, elevation 165, axial -60 (overhead). Hub K, the horn and the rod press
  together there, and they stay with the drive metal deleted. Held out: 8.71 mm at (30, 165, -45).
- **Workspace in-band (unscored):**
  - all taken workspace poses: 0.865 (0.867; leader 0.856 / 0.861);
  - elevation 90-140: 0.812 (0.833; leader 0.800 / 0.822), with 0.187 of the metal above 14 mm (0.165);
  - overhead: 0.950 (0.937; leader 0.940 / 0.932).
- **Clip in-band (scored):** 0.8971. The 2-3 mm band-edge share is 0.0014. Reading the band as 3-14 mm gives 19.01: T2
  is clean.
- **Springs, stops, cuff twist, singular postures:**
  - K's clock spring is 0.08 N.m + 0.015 N.m/rad. It reflects 0.165 N.m at J2, 1.10-1.37 N at the cuff; this is
    static, and the dynamics are unmeasured (finding M5).
  - The RSSR's minimum transmission over taken K is 52.0 deg (gate 48); with the catalogue head and r_h 15.9 it is
    49.8.
  - Minimum fold margin in th: 5.231 deg on the bench and 5.045 held out, against the 5 deg rule.
  - Continuity: static 18.87 = connected (full flood) 18.87, 0 poses dropped. knn 21.39, bench graph 51.74 (leader
    18.49 / 20.16 / 50.11).
  - Cuff twist: not measured (no dynamics run).
- **DOF and complexity:** 3 active DOF, 0 passive translations, O20 hubs. Complexity 28.5 (tools/simplicity.py
  recomputed = row) against the leader's 22.25: +6.25 for a tie.

## Findings (all watch)

### M2: the ball-link sockets are modelled smaller than the catalogue part

- **Evidence.**
  - The model samples both M2 ball-link sockets at O7 (SC.ER 3.5; the radial socket as O7 x 7). The row calls them
    catalogue parts.
  - The catalogue link the repo names is igus KBRM-02, head O9 x 4.
  - Worn with SC.ER 4.5 (override in memory; `tools/alignment_const_probe.py`), frozen exact:
    - pick **275.0** (parts 373 of 470, all ROD-hubK);
    - robust build **275.0**;
    - on the fit bench, an O8 head already loses every pose for both.
  - With r_h 15.9 (the sidecar red team's own fix for this pair) the catalogue-headed design scores **18.83** bench,
    23.17 held out.
  - Fit-bench scans: SC.ER 3.5 / 4.0 / 4.5 gives 16.47 / 275 / 275 (pick) and 16.47 / 275 / 275 (robust). At SC.ER
    4.5, r_h 15.4 / 15.9 / 16.4 gives 275 / 17.64 / 17.64 on the 2 mm objective (plain 12.75 / 12.74).
- **Why it is not a better exo as recorded.** The tie is claimed for a horn-end socket 2 mm smaller in diameter than
  the part the repo would buy. With that part the claimed shape cannot be assembled: the socket sits on hub K's
  stack. The number survives, but at a different horn radius, which the row does not record.
- **Action.**
  - Name the ball link (part number, head size) in the row.
  - Re-wear the claim with the catalogue head and r_h >= 15.9, or justify an O7 catalogue part.
  - Correct the red team's "binds at the top of the taken range": the stud's tilt peaks at rest.

### NEW-pair-knife-edge: metal parked just past a part-pair cutoff

- **Evidence.**
  - The re-worn coordinate span `clear` over taken poses is [1.062, 1.181] mm, against the 1 mm pair rule. The leader's
    is [1.315, 5.109].
  - Tolerance scan, `docs/research/inband_drive/out/tol_p.jsonl`: 11 / 34 neighbours score 275.0, and 5 cost +6.5 to
    +7.4.
  - The robust build has 0 / 34 failures and measures 18.83 / 23.16.
- **Why it is not better.**
  - A shape that a 0.25 mm build error kills is not the exo that gets built. The edge bought no points: the robust
    build is 0.04 better.
  - Both shapes sit under 0.5 mm from the cutoff, inside the gap between the modelled and the catalogue socket.
- **Action.** Use the robust build (or the catalogue-head variant) as the headline. This pattern should be in the
  catalogue (proposal P-A below).

### NEW-inband-padding: the ear's in-band samples dilute the drive's cost

- **Evidence.**
  - Frozen-exact attribution (`farm/claimA/p_attr_bench.json`): ear deleted 19.39 (+0.52), crank deleted 18.58 (-0.29),
    all drive metal deleted 18.58.
  - The ear has 44 samples per pose, 1.00 in band at a median 9.5 mm, on a 2 mm areal grid (model lines 203-207).
    Link 1b's whole strap has 36.
- **Why the exo is not better by that amount.** The headline "drive metal 7.57 -> 0.29" nets about 0.81 points of drive
  metal against 0.52 of dilution:
  - the crank still sits 0.71 in band at a median 13.2 mm;
  - the ear is good, real metal, but it does not bring the crank any closer.
- **Action.** Report the drive's cost with and without the ear. The polish must not grow the ear or other in-band
  metal to buy in-band.

### R4: the dashboard shows the in-sample best, not the frozen claim

- **Evidence.**
  - The morphs.json row shows gap 12.79 (fit-bench fast plain of the CMA's best of 11576 configurations) and
    frozen_gap null. `tools/dash_build.py` line 409 reads only `frozen_exact` / `frozen_exact_gap`, and this row stores
    its claim under `claim` / `frozen`.
  - The row's top-level `gap` is 16.47 (the fit-bench 2 mm objective). The ledger takes it as the claim, and the audit's
    contact-depth check cannot match it.
- **Why it misleads.** On the dashboard's self-measured column the row reads ahead of the leader (12.79 vs 13.00). The
  frozen 18.87 and held-out 23.21, which show parity, are not on the page. The fast-to-frozen drop is 6.08 points
  (R3).
- **Action** (not mine to apply). Write `frozen_exact_gap` 18.83 (robust) on the row, or make dash_build read
  `claim.gap`. Have the audit tool's claim reader use `claim.gap` for screened rows (proposal P-B).

### M5: the spring-held follower's dynamic hold is unmeasured

- **Evidence.** The lobe follower is force-closed by K's clock spring (0.08 N.m preload). It reflects 0.165 N.m at J2,
  static. There is no R17 / dynamics run and no CAD. pick1 at the same preload lagged 9.28 deg on R17.
- **Why it matters.** "The unpowered MVP1 genuinely tracks the arm" is the goal's last line. It is shared with the
  leader, so it changes no ranking.
- **Action.** Run judge/dynamics.py on the first CAD of this family.

## What the polish must not exploit (envelope-bench polish of this row, workflow wf_d261725f-27c)

1. **The cone gate.** The model passes any socket tilt up to 30.0 deg (CONE). A search can walk the tilt to 29.9 with
   no margin for the catalogue part's tolerance, and the tilt already peaks at rest. Require a margin (for example
   tilt <= 27 deg), or report the tilt at rest and the peak.
2. **The ROD-hubK pair.** With O7 sockets the search parks the pair at 1.06 mm. Polish with the catalogue O9 head
   (SC.ER 4.5) or claim the robust or catalogue variant; a polished 1.0x mm pair is the knife edge again.
3. **The fold margin.** Held out it is 5.045 deg against the 5 deg rule; the bound must not be walked (T3 / T4).
4. **In-band padding.** Growing the ear (or any in-band part) lowers the gap without moving any out-of-band metal.
5. **Depth-blind contact.** The score counts contact poses, not depth. Trading pose 264's 0.09 mm press for a deep
   one would score the same. Report the per-pose depth dumps.
6. **The held-out set.** The envelope bench must be built and searched without `held_bench()`. Wear the held-out set
   once, after the pick is committed (as this row did).
7. **The 1-2 mm shell.** 15.25 points of the plain gap live in the 1-2 mm shell (report-only since 2026-10-17). A polish
   that moves metal from 3 mm to 1.1 mm gains in-band and loses nothing on the score.

## Proposals (measurement or reporting changes for the lead / user; not applied, not inputs to this verdict)

- **P-A: a catalogue entry T6, "metal parked past a part-pair cutoff"**, with a check.
  - **Looks like:** the closest part pair sits within 0.25 mm of the 1 mm pair rule on every taken pose, and +-0.25 mm
    tolerance neighbours lose every pose.
  - **Detect:** the re-wear's `clear` span (deep_audit already records it), plus the row's tolerance scan.
  - **Measured effect on rows:**

    | row | clear min (mm) |
    |---|---|
    | this pick | 1.062 |
    | long-stroke claim | 1.042 |
    | slipper-nose | 1.315 |

    The rule would watch this pick and the long-stroke claim, and not slipper-nose.
- **P-B: claim reader for screened rows.** When `claim.gap` exists, the ledger and `contact_depth` should read it, not
  the top-level `gap` (here the in-sample fit objective 16.47). Effect: this row's contact-depth check would run on the
  dumps (bench 9.86 mm against the leader's 14.75, held 23.20 against 46.12: ok), and the ledger's claim would read
  18.87.
- **P-C: catalogue sizes as named constants per row.** The ball-link head (O9 x 4) and cone (30 deg) should come from
  one catalogue file, so a model cannot sample a smaller socket than the part list buys. Effect measured here: the
  pick and the robust build go 18.87 / 18.83 -> 275 until r_h >= 15.9, and at r_h 15.9 the bench is 18.83 again.
