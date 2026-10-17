# Alignment audit: inband-rssr-knuckle-3r

Auditor run 2026-10-17 12:03-12:35 UTC (hourly audit: CANDIDATE LEADER CHANGE from the envelope-bench final polish,
workflow wf_d261725f-27c). Checks: `docs/alignment/inband-rssr-knuckle-3r.json` (`--ref slipper-nose-knuckle-3r`).
Findings: `docs/alignment/inband-rssr-knuckle-3r.findings.json`. Ledger: `docs/alignment/ledger.jsonl`, `by auditor`,
run `audit:inband-rssr-knuckle-3r`. All re-wears are new files in `docs/alignment/remeasure/inband_pick3/`, made by the
new tool `tools/alignment_inband_rescore.py`. That tool imports the polish's claim harness (`tools/inband_env_polish.py
claim`) unchanged and overrides only in memory. Local, nice, OMP_NUM_THREADS=1, at most 2 processes, $0 farm.

## Verdict: WATCH. No leader change: under the leader's own protocol the polished shape does not beat 23.45 held out

- **The claim.** pick3 (`ibp-s2-g6-4`, `docs/research/inband_env_polish/picks/pick3.json`), priced: frozen exact
  Bench(110,360) **18.33**, held out **22.86** (fit60) and 23.57 (env fit). An independent verifier confirmed it at
  12:06 against the row's own pick (`polished_*` fields). The dashboard now shows it as v_gap 18.33, ranked #1 above
  the leader slipper-nose-knuckle-3r (18.49 / 23.45).
- **The honest numbers.** The leader's 18.49 / 23.45 are read unpriced, at fold margin 5. pick3's are read priced:
  smlo +0.5, a1max -0.5, fold reading 5.5. Here pick3 is worn on the same claim harness under the leader's protocol
  (ENVP_NOPRICE=1, CB_FOLD_MARGIN=5; this harness reproduces the row's 18.87 / 23.21 to the digit):

  | pick3 variant (frozen exact, fit Bench(60,160)) | bench | held | 1 mm bench / held | 2 mm bench / held | file |
  |---|---|---|---|---|---|
  | as claimed (O7 sockets), priced | 18.33 | 22.86 | 20.52 / 26.19 | 33.38 / 36.65 | polish farm `claim_pick3_fit60_*` |
  | **as claimed, the leader's protocol** | **18.32** | **23.54** | 21.05 / 25.31 | 32.58 / 38.56 | `claim_O7nominal_unpriced_*` |
  | catalogue O9 head, r_h 15.9, the leader's protocol | 18.32 (with ear de-dup) | 23.54 | 22.69 / 27.52 | 33.66 / 39.44 | `claim_O9rh15.9_dedup_unpriced_bench`, `claim_O9rh15.9_unpriced_held` |
  | catalogue O9 head, r_h 15.9, ear de-duplicated, the leader's protocol | 18.32 | **23.62** | 22.69 / 27.60 | 33.66 / 39.44 | `claim_O9rh15.9_dedup_unpriced_*` |
  | catalogue O9 head, r_h 15.9, ear de-duplicated, priced | 18.33 | 22.86 | 22.16 / 28.41 | 33.93 / 37.54 | `claim_O9rh15.9_dedup_*` |
  | leader slipper-nose (verified protocol) | 18.49 | 23.45 | 20.12 / 26.54 | 33.02 / 36.95 | `remeasure/slipper-nose-knuckle-3r_*` |

  On the bench pick3 stays ahead: 18.32 against 18.49. Held out it is behind: 23.54 (23.62 buildable and
  de-duplicated) against 23.45. **The leader-change condition, that the honest numbers still beat 18.49 / 23.45, fails
  held out.**
- **Why WATCH and not GAMED.** Under the same harness the held-out gap is behind by only 0.09, and the wearer counts are
  mixed. Held out, pick3 has:
  - 646 of 952 workspace poses against the leader's 650;
  - 12 contact poses against 10;
  - 33.3 mm summed depth against 46.1 mm;
  - 52 taken poses under 2 mm against 62.

  So the leader is not shown to be better for the wearer. It is a tie that the claim reads as a lead.
- **Tool checks: 2 watch, 0 gamed.** The tool's checks are the same as last hour: held_out (no verified bench gap on
  the row) and idle (the K.qa false positive that the skeptic refuted).
- **The judgement pass adds 7 watch findings:** NEW-reading-mismatch, M2, P2, R3, NEW-inband-padding, G1 and M5.

## The questions this audit was sent with

1. **Sampling artefact (the ear). The polish did not exploit it, and de-duplicating it does not move the priced
   claim.**
   - The ear has 44 samples on the row's pick and on pick3. clay is fixed at 1 by the polish, and zc moved 0.80 -> 0.89
     mm. Nothing grew.
   - De-duplicated in memory (`--dedup-ear`, 1.42 mm thinning), the ear drops from 44 to 30 samples, the skeptic's
     estimate. Fit-bench in-band moves 0.9063 -> 0.9048 (`fit_base.json`, `fit_dedup.json`).
   - Frozen exact, priced, with the O9 head: bench in-band 0.9057 and held 0.9041. The gap stays 18.33 / 22.86,
     because pick3 sits above the 0.90 in-band target.
   - Unpriced, held out, it is 0.9007 -> 0.8992: 23.54 -> 23.62.
   - pick3's +0.0100 in-band over the row's pick is not the ear: the de-dup costs both about 0.0015.
2. **Buildability with the catalogue igus KBRM-02 (O9 x 4) head. Buildable, but not as recorded.**
   - The row's CAD config `polished_params_cad` (r_h 15.0125) and pick3 (r_h 14.76) lose every pose to the ROD-hubK pair
     with SC.ER 4.5: fit 275.0, parts 183 (`fit_O9.json`).
   - r_h 15.4 also loses every pose. The design lives from r_h 15.65 (`fit_O9_rh*.json`).
   - At r_h 15.9:
     - transmission min 52.2 deg (gate 48);
     - crank socket tilt 21.5 deg taken, 22.4 range, against the 30 deg cone (25 deg short-neck link: fits);
     - 18 of 18 knife-edge neighbours pass, worst +1.17 at 1 mm (`knife_O9rh15.9.txt`).
   - **The head rim against the horn lug top** (hand calculation 3 - 2 cos t - 4.5 sin t, ball centre 3.0 mm over the
     lug): -0.22 mm at the horn's taken tilt of 16.9 deg, -0.49 mm at its range maximum of 21.1 deg. A ~0.6 mm spacer
     is needed. Worn with ZB 3.6, the bench is unchanged at 18.33 (`claim_O9rh15.9_dedup_zb3.6_bench.json`).
   - The bigger head costs near-touch, not plain gap: 1 mm 20.52 -> 22.16 bench and 26.19 -> 28.41 held (priced).
3. **Paired against slipper-nose held out: not robust.**
   - pick3 as claimed: held -0.59, 90 % CI [-1.59, +0.32], P 0.82; bench -0.16, CI [-2.13, +1.64]; pooled -0.46, CI
     [-1.46, +0.44] (`inband-rssr-knuckle-3r-pick3_vs_slipper-nose-knuckle-3r_paired.json`).
   - Buildable and de-duplicated: held -0.59, CI [-1.45, +0.32] (`..._pick3cat_vs_...`).
   - The CI includes 0 every time.
   - The edge is all in-band (-0.45 bench / -0.57 held) and contact (-0.27 / -0.23). Reach is behind (+0.56 /
     +0.21).
   - These pairs are priced pick3 against the unpriced leader. At the same reading the held-out sign flips (table
     above).
4. **Contact depth.**
   - Priced pick3: bench 1 pose at 0.22 mm; held 8 poses, 21.2 mm, deepest 6.09 mm at (-90, 60, 120).
   - Under the leader's protocol: bench 2 poses, 8.59 mm (deepest 5.85); held 12 poses, 33.27 mm (deepest 8.30, 4
     overhead).
   - Leader held: 10 poses, 46.1 mm.
   - Bench pose 237 (elevation 165, 9.7 mm press on the row's pick) is lost, not cleared. The polish says so itself.
5. **Fold margin.**
   - Priced: min th 5.589 bench / 5.524 held, with 0 poses under the 5.5 reading.
   - The leader's protocol: 5.021 bench / 5.346 held, with 0 under 5. That minimum is set by the reading, so no bound
     is walked.
6. **Knife edge.**
   - pick3 nominal fails r_h -0.25 (polish `robust_picks.json`).
   - The O7 CAD build (r_h +0.25) passes 18 / 18, and so does the O9 build at r_h 15.9.
   - beta / gam / eta +-1 deg are all clean.
7. **Picks before held-out numbers.** Yes: `pick3.json` was committed in 28b9bb4 at 11:27:29 and has been unchanged
   since. The first claim files were committed in 482d4a1 at 11:50:28. The search touches the held-out set only in
   `_wear_bench`. The report-only long-dyad row (fdc74d6, 11:28:26) is not the claim. **But** pick3 was the envsel
   rule's last of 3 and was chosen after the claim (finding P2).

## What the wearer gets (measured, frozen exact; bench / held; pick3 as claimed under the leader's protocol unless noted)

- **Overhead (elevation >= 140):** 9 of 28 workspace poses taken / 19 of 71 (leader 8 / 18). Raised arm by band (held,
  priced claim dump): 90-120 68 / 140, 120-140 27 / 89, 140-160 11 / 35, 160+ 8 / 36.
- **Workspace reach:** 260 / 360 and 646 / 952 (leader 261 / 650).
- **Taken poses with metal under 2 mm:** 19 / 52 (leader 25 / 62). Under 1 mm: 4 / 8. With the catalogue O9 head
  this rises to 7 / 18 (unpriced) and 6 / 25 (priced; leader 2 / 14). The lowest metal is 0.01 mm held.
- **Deepest contact:** 8.30 mm held out. The 4 overhead contact poses sit at elevation 150, (30, -45) and (15, -60).
  The deepest priced one is 6.09 mm at plane -90, elevation 60, axial 120.
- **Workspace in-band (unscored, priced claim):** all 0.873 / 0.874, elevation 90-140 0.832 / 0.845, overhead 0.935 /
  0.934.
- **Springs:** 0.172 N.m at J2, 1.15 / 1.44 N at the cuff (17 % / 29 % of R17), static only.
- **Stops:** the drive range ends on the law (dK 65.5 against 47.5 taken).
- **Not measured:** cuff twist and dynamics. Near-singular postures: transmission >= 52.2 deg, no jam in range.
- **DOF:** 3 active DOF, O20 hubs, complexity 28.5 (the leader's is 22.25).

## Findings (all watch)

### NEW-reading-mismatch: the claim and the incumbent are read under different rules

- **Evidence.**
  - The polish compares priced pick3 (smlo +0.5, a1max -0.5, fold reading 5.5) with the leader read unpriced at margin
    5, and calls that conservative.
  - That holds for the row's own pick: pricing costs it +0.56 / +1.17.
  - For pick3 it is false held out. The same shape on the same harness reads 23.54 unpriced and 22.86 priced. The 5.5
    reading turns 4 held-out contact poses into fold losses: contact 12 -> 8, depth 33.3 -> 21.2 mm, fold 260 -> 263.
  - Under the leader's protocol, pick3 is 18.32 / 23.54 against 18.49 / 23.45.
- **Why it is not a better exo.** The metal did not move off the skin at those 4 poses. A stricter reading stopped
  counting them as taken, and the 5 deg rule is the project's rule. The held-out "lead" of 0.59 is a 0.09 deficit
  under one harness.
- **Action.**
  - Compare at one reading: re-read the leader priced, or quote pick3 unpriced (18.32 / 23.54).
  - Do not announce a leader change on 22.86.
  - Proposal P-D below.

### M2: the polished CAD config is not buildable with the named ball link

- **Evidence.** See question 2: O9 at r_h <= 15.4 gives 275. r_h >= 15.65 is needed (15.9 checked), plus a ~0.6 mm
  stud spacer at the horn.
- **Why it matters.** `polished_params_cad` (r_h 15.0125) is the shape a CAD build would take. With the part the repo
  names, it cannot assemble. The previous audit's M2 action (name the part, re-wear with the O9 head) was not taken up
  by the polish or the verifier.
- **Action.**
  - Record KBRM-02, r_h 15.9 and the spacer on the row.
  - The plain gap survives (18.33 / 22.86 priced, 18.32 / 23.54 unpriced). The 1 mm shell gets worse (finding G1).

### P2: best of 3 picks, chosen after the claim

- **Evidence.**
  - The committed envsel ranking was pick1 25.91, pick2 26.23, pick3 26.30, with pick3 last.
  - The earlier polishes' rule (best robust held-out gain) gives pick1: +1.26 against +1.18.
  - pick3 is best of 3 on both claim sets: bench 19.15 / 19.49 / 18.33, held 23.12 / 23.39 / 22.86.
  - The pre-registered #1 (pick1) is 19.15 on the bench, behind 18.49. The mean of the three committed picks is 18.99 /
    23.12.
- **Why it matters.** The post-hoc reasons are wearer-relevant (pick1 fails 2 of 18 neighbours and is 1.37 worse at
  1 mm), so this is not a leak. But a bench lead of 0.16 that only the third pick has is inside the pick-to-pick
  spread (1.16).
- **Action.** State the selection rule for choosing among the claimed picks before the claim runs, and report all
  three.

### R3: best-of-many shown without its spread, ranked #1 before the audit

- **Evidence.**
  - `morphs.json` (1e22296, 12:12:45) carries v_gap 18.33. `leader.js` ranks it #1 "verified" above slipper-nose's
    18.49.
  - The paired CI crosses 0 (question 3).
  - The ledger still takes the in-sample 16.47 as the row's base gap (proposal P-B of the previous audit, not applied).
- **Action** (not mine to apply). Show the picks' spread and the paired interval next to v_gap. Do not rank above the
  leader until the comparison is at one reading.

### NEW-inband-padding: the ear's double sampling (re-measured)

- **Evidence.** See question 1.
- **Status.** No score effect on the priced claim, because in-band is above the 0.90 target. It costs 0.08 on the
  unpriced held-out reading (23.54 -> 23.62).
- **Action.** Proposal P-E below.

### G1: the catalogue head moves metal into the under-1 mm shell

- **Evidence.**
  - Priced, taken poses under 1 mm: 6 bench / 25 held, against the O7 claim's 3 / 15 and the leader's 2 / 14.
  - Under 2 mm: 23 / 58, against the leader's 25 / 62.
  - The minimum is 0.17 mm (0.01 mm unpriced held).
- **Why it matters.** A real arm bulges, and metal under 1 mm on the model touches it.
- **Action.** Re-optimise the socket stack height with the O9 head before CAD.

### M5: the spring's dynamic hold is unmeasured

- **Evidence.** Static only: 0.172 N.m at J2. No dynamics, R17 or CAD run exists for this id.
- **Note.** This is shared with the leader and changes no ranking.

## Proposals (measurement or reporting changes, not applied, not inputs to this verdict)

- **P-D: one reading per comparison** (catalogue entry T6, "claim and incumbent read under different rules").
  - A leader-change claim must quote both designs at the same fold reading and stop pricing.
  - **Detect:** the claim harness run with ENVP_NOPRICE=1, CB_FOLD_MARGIN=5 on the claimant (one bench and one held
    wear, about 8 min local).
  - Measured effect here: pick3 18.33 / 22.86 -> 18.32 / 23.54, and the held-out sign against the leader flips. Other
    verified rows were not read priced, so they do not change.
- **P-E: de-duplicated plate sampling.**
  - Sample every rigid plate on one 2 mm grid. As a stand-in, drop samples within 1.42 mm of an earlier sample of the
    same part.
  - Measured on this row: ear 44 -> 30 samples, gap unchanged priced and +0.08 unpriced held. Other verified rows were
    not measured (the leader has no ear; its plate densities were not measured).
- **P-C (repeated): catalogue sizes as named constants.**
  - Measured effect: pick3 and its CAD build -> 275 until r_h >= 15.65; at 15.9 the gap is unchanged and the 1 mm shell
    +1.6 / +2.2.

## Numbers I could not get

- **The leader read priced.** Its model is not this harness, and it is out of time and scope. So the comparison at the
  priced reading is unknown.
- **The env-fit held-out leg under the leader's protocol.** The env fast cache lives only on the farm volume, and the
  farm budget is spent.
- **pick3's 2-3 mm band-edge share (T2).** The dumps carry in-band counts, not distances.
- **Cuff twist and dynamics:** no CAD.
- **The default remeasure** (`alignment_audit.py remeasure`, best_params) was not re-run. best_params is unchanged
  since 11:06 (the row moved only in `polished_*`), and the moved claim was re-worn through its own harness instead.


## Skeptic (2026-10-17 12:30-12:45 UTC, pick3 leader-change audit): final verdict WATCH

Rulings: `docs/alignment/inband-rssr-knuckle-3r.rulings.json`, which replaces the 11:30 rulings; those stay in git
history. Ledger: `by skeptic`, run `skeptic:inband-rssr-knuckle-3r`. Of the 9 reasons, 4 are refuted with evidence and
5 are upheld. The ledger computes the worst upheld level: **watch**. **No leader change:** the honest held-out number
(23.54 as claimed, 23.62 buildable and de-duplicated) does not beat 23.45.

**What I re-measured.** No new runs of the models: everything was re-derived from the per-pose dumps already on file,
with my own gap and paired-bootstrap code (scratch, not committed). That code does not import `tools/alignment_paired.py`
or the audit tool. It uses 4000 draws, seed 1, with poses resampled within kind. Local only, $0 farm.

- **pick3 as claimed, priced:** `farm/claim_pick3_fit60_*` gives 18.33 / 22.87.
- **Under the leader's protocol (unpriced, margin 5):** `remeasure/inband_pick3/claim_O7nominal_unpriced_*` gives
  18.32 / 23.54.
- **Catalogue O9 head, ear de-duplicated, unpriced:** 18.32 / 23.62.
- **The leader:** `remeasure/slipper-nose-knuckle-3r_*` gives 18.48 / 23.45.
- **The claim harness is the row's protocol.** `farm/claim_PICKnominal_fit60_held_perpose.json` matches the row's own
  claim dump (`inband_drive/farm/claimA/`) pose by pose: 0 of 1154 poses differ.
- **Paired against the leader (gap A - B, negative means pick3 is better):**

| reading | bench | held |
|---|---|---|
| priced | -0.16, 90 % CI [-2.10, +1.66] | -0.59, CI [-1.60, +0.32], P(better) 0.84 |
| unpriced | -0.17, CI [-1.95, +1.72] | **+0.08**, CI [-0.83, +1.31], P(better) 0.38 |
| O9, ear de-duplicated, unpriced | -0.17 | +0.16, CI [-0.70, +1.32] |

### Rulings

- **held_out: REFUTED.** The check reads only the empty top-level `v_gap`. The verified numbers are on file:
  - row `polished_gap` 18.33 and `polished_held_out.fit60.pick3.gap` 22.86;
  - the verifier's re-runs `verify/claim_pick3_fit60_{bench,held}.json` `final.gap` 18.33 / 22.86.

  The drop is +4.53, and +5.22 under the leader's protocol (env fit: +5.24). All are under TH held_watch 6.0. The
  leader drops +4.96.
- **idle: REFUTED.** This is the same instrument false positive as before, re-checked on the current files.
  - The model only reads `knee_moved` (line 291). The flag is set only in the two kneeless models.
  - CELL = 'lead' is the pin knee, and the row has `cuff_knee.pins` 2.
  - K moves 49.34 deg (`claim_O7nominal_unpriced_bench.json` `dK_taken_max`).
  - The crank's "no span on file" is answered by `cam.phi_max_taken`, 34.8 / 36.1 deg. Both joints move far above
    TH idle_deg 2.
- **NEW-reading-mismatch: UPHELD.** The numbers are confirmed, and the comparison is like for like (the harness is
  the row's protocol, 0 / 1154 pose mismatches). Pricing moves 4 held-out contact poses into fold losses (contact 12
  poses / 33.27 mm -> 8 / 21.16 mm), and the held-out sign flips at the same reading.
- **M2: UPHELD.**
  - `fit_O9.json`: 275.0, parts 183. `fit_O9_rh15.4.json`: 275.0. `fit_O9_rh15.65.json` / `_rh15.9.json`: 20.62,
    parts 0.
  - The rim formula reproduces -0.22 / -0.49 mm.
  - `docs/research/sidecar_mechanism_redteam.md` row 2 independently names the KBRM-02 (O9 x 4) and the 0.6 mm
    spacer.
  - The row has no "KBRM" string, and its `polished_params_cad.r_h` 15.0125 is dead with the catalogue head.
- **P2: UPHELD, and slightly worse.**
  - The commit order is confirmed (28b9bb4 11:27:29 before 482d4a1 11:50:28).
  - The envsel rule (`sel_mean_near1` 25.905 / 26.225 / 26.295) puts pick3 last.
  - fit60 claims: bench 19.15 / 19.49 / 18.33, held 22.86 for pick3 (best).
  - **On the env-fit held leg pick3 is the worst of the three:** 22.43 / 23.46 / 23.57 (recomputed from
    `farm/claim_pick*_env_held_perpose.json`).
  - pick3 also had the deepest contact on the selection draw: `sel_depth` 14.78 mm against 3.62 / 5.64.
- **R3: UPHELD.**
  - `morphs.json` shows v_gap 18.33 for a row whose status is 'screened'. It ranks first, above minarc 18.40,
    slipper-nose 18.49 and trimlug 18.51.
  - `v_reach`, `v_follow`, `v_inband14` and `v_contact` are all null. The cause is `tools/dash_build.py` line 402,
    which reads `polished_bench['pick1']`; this row has 'pick3' and 'row_pick'.
  - The same card's verdict text still says "at PARITY with slipper-nose, not ahead".
- **NEW-inband-padding: REFUTED (below every documented threshold, no claim effect).**
  - The ear holds 44 samples, unchanged by the polish (`fit_base` / `fit_O9` `density.ear.n`).
  - De-duplicating it costs 0.0015 in-band (0.15 points), against TH part_weight_watch 3.0.
  - The tool's sampling check on this row reads ok, at -1.54 points: sampling penalises the design overall.
  - The claimed 18.33 / 22.86 is unchanged de-duplicated. The one reading it moves (unpriced held 23.54 -> 23.62)
    does not change the leader decision.
- **G1: REFUTED as a level, not as a count.** The counts are confirmed: under 1 mm, 6 / 25 against the leader's
  2 / 14, or 7 / 25 against 3 / 14 counting the model's extra walls.
  - These are near-touch readings. ALIGNMENT.md section 6 entry 2026-10-17.2 and `c_near_touch` (lvl 'ok') make them
    report-only, as do CLAUDE.md user decisions (3) and (6).
  - On the scored contact the O9 build is shallower than the leader: bench 1 pose / 0.22 mm against 2 / 14.75 mm;
    held 8 / 21.16 mm against 10 / 46.12 mm.
  - The counts stay reported, and M2 carries the O9 head.
- **M5: UPHELD.** This is a missing measurement: no dynamics, R17 or CAD run exists for this id. The static value
  reproduces: 1.8622 x (0.08 + 0.015 x 0.832) = 0.172 N.m.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **The claim's pick depends on which held leg is read.** On the env-fit held leg pick3 is the worst of the three
   committed picks (22.43 / 23.46 / 23.57), and its 23.57 is behind the leader's 23.45 even priced. The pre-registered
   pick1 has the best env-fit held number of any pick (22.43). The claim headlines fit60 (22.86), the only leg where
   pick3 is best. P2's "best of 3 on both claim sets" holds only for the fit60 legs.
2. **The dashboard card shows the polished number without its terms.** `tools/dash_build.py` line 402 hard-codes
   `polished_bench['pick1']`. For this row (keys 'pick3' and 'row_pick'), `morphs.json` carries v_gap 18.33 with every
   `v_*` term null. Its verdict text still describes the 18.87 parity row. Any future polish whose pick is not named
   pick1 will show the same way.
3. **The 2 mm counts in the "tie" argument leave out the model's extra walls (`cmin`).** Counting them, pick3
   unpriced held has 64 taken poses under 2 mm against the leader's 67 (not 52 against 62); bench is 26 against 30.
   The tie conclusion stands, but pick3's 2 mm advantage shrinks from 10 poses to 3.


---

*Earlier audit of this row (auditor 11:03-11:35 UTC, final WATCH); its skeptic section is kept below unchanged. Its auditor sections are replaced by the run above and remain in git history (commit before this one).*

## Skeptic (2026-10-17 11:30-11:40 UTC): final verdict WATCH

Rulings: `docs/alignment/inband-rssr-knuckle-3r.rulings.json`. Ledger: `by skeptic`, run `skeptic:inband-rssr-knuckle-3r`.
Two reasons are refuted with evidence and five are upheld, so the verdict is the worst upheld level: **watch**.

**What I re-measured.** Everything ran locally, nice, OMP_NUM_THREADS=1, at most 2 processes, models unchanged, no
farm spend.
- Frozen exact Bench(110,360) re-wears through `tools/alignment_const_probe.py --tag skeptic` (the constant is
  overridden in memory only):
  - `remeasure/inband-rssr-knuckle-3r_skeptic_bench_SC.ER4.5.json`;
  - `..._skeptic_bench_SC.ER4.json`;
  - `..._skeptic-cat-rh15.9_bench_SC.ER4.5.json`.
- New read-only probe `tools/alignment_part_density.py`. It reports samples per mm2 of each part and the crank angle
  along the model's own K grid.
- The gaps and contact depths, re-derived by hand from the per-pose dumps.

### Rulings

- **held_out: refuted.**
  - Both wears are measured, exact and frozen: `remeasure/_bench.json` 18.87 and `_held.json` 23.21. The drop is
    +4.34, under TH held_watch 6.0. The leader drops +4.96.
  - Re-derived from the per-pose dumps without the audit tool:
    - bench: ws 260/360, clip 110/110, in-band 0.8971, contact 3/373, giving 18.87;
    - held out: reach 0.6828, in-band 0.8956, contact 9/861, giving 23.21.
  - Timing:
    - pick rule `b6cfa9b` 09:36:11;
    - pick `f8fd767` 10:10:20;
    - `tol_rob.jsonl` first committed 10:13:10;
    - `p_held.json` first committed 10:26:59.

    No leak.
- **idle: refuted (instrument false positive).**
  - The "rigid knee" comes from the tool's regex for `knee_moved` anywhere in the model source. This model only reads
    the flag (line 291). The flag is set only by kneeless-roller and kneeless-sidecar.
  - The row runs the lead cell: longstroke `CELL = "lead"` loads roller-longdyad, and `cuff_knee.pins` is 2.
  - K moves 45.83 deg (`deep.coord_spans.dK`). The crank, measured here from the model's RSSR grid, turns 33.71 deg
    at K 45.83 and 34.15 deg at K 46.44. Both are far above the 2 deg threshold.
- **judgement:M2: upheld.** My re-wears reproduce the auditor to the digit:
  - O9 (SC.ER 4.5): 275.0, parts 373;
  - O8 (SC.ER 4.0): 275.0, parts 373;
  - O9 at r_h 15.9: 18.83, transmission 49.8 deg, contact 3 poses / 9.93 mm, fold margin 5.231.

  The arithmetic agrees: r_h - ER - HUB_R = 14.62 - 3.5 - 10 = 1.12 mm, and the O9 head leaves 0.12. The cone peaks at
  rest (the scan starts at K = 0; CONE25 gives dK_lim 0, `cone`). The number is not inflated, since the catalogue
  build measures 18.83. But the recorded `best_params` cannot be assembled from the KBRM-02 the repo names, and the row
  records neither the part nor r_h 15.9.
- **judgement:NEW-pair-knife-edge: upheld, count corrected.**
  - `tol_p.jsonl`: **10** of 34 neighbours lose every pose (the auditor said 11). All 10 sit at r_h - 0.25 = 14.3748.
    Five more cost +6.48 to +7.35 plain.
  - `tol_rob.jsonl`: 0 of 34 dead.
  - The robust build is 18.83 / 23.16 (`claims.robust_build`).
  - No points are bought, but `best_params`, which a CAD build would take, is the knife-edge shape.
- **judgement:NEW-inband-padding: upheld, sharper.** The attribution reproduces from `p_attr_bench.json`: ear deleted
  19.39, crank deleted 18.58.
  - **New measurement:** the ear is sampled at **0.50 samples/mm2** (44 on 87.6 mm2). Every other plate is at
    0.29-0.42:

    | part | samples / mm2 |
    |---|---|
    | hubs | 0.29 |
    | knee | 0.33 |
    | E | 0.34 |
    | boss, pad | 0.35 |
    | crank | 0.39 |
    | horn | 0.42 |
    | **ear** | **0.50** |

    The cause: the pivot disc `S.disc(6, 2)` and the 2 mm strip that starts at the pivot (model lines 199-206) sample
    the same area twice.
  - At the plates' median 0.342/mm2 the ear would carry about 30 samples. In-band would then be about 0.8955 on the
    bench (about 19.03) and 0.8940 held out (about 23.37). This is arithmetic, not a re-wear.
  - That is the leader's in-band (0.8955). **The row's in-band edge over the leader is the ear's excess sampling.**
  - Not refuting: per pose the row has 914 samples against the leader's 912, and fewer out-of-band samples (94.0 vs
    95.3 bench, 95.5 vs 96.4 held). The ear's size is fixed in code, not searched.
- **judgement:R4: upheld, sharper.**
  - `morphs.json` row 52: gap 12.79, frozen_gap null, v_gap null.
  - `dash_build.py` lines 408-409 read only `frozen_exact*`.
  - `leader.js` line 73 falls back to `gap` when `v_gap` is null. So the "Below the baseline now" list ranks this row
    **#1 at 12.79 ("claimed")**, ahead of every verified row (minarc 18.40, slipper-nose 18.49); trimlug-k165 13.02 is
    #2.
  - My fit-bench run gives 16.47, the row's top-level gap.
- **judgement:M5: upheld (missing measurement).** No dynamics, R17 or CAD output exists for this id in judge/,
  pipeline/ or pipeline/full-exo/designs/. The static 0.165 N.m (1.10 / 1.37 N) reproduces.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **Tolerance count.** 10 of 34 neighbours die, not 11. All 10 are the r_h -0.25 side (`tol_p.jsonl`).
2. **Ear double-sampling** (above). It is a per-part density artefact worth about 0.16 points. It is the whole of the
   row's in-band edge over the leader.
   - **Proposal (a measurement change, not applied):** sample every plate on one de-duplicated 2 mm grid. Estimated
     effect on this row: about +0.16 bench and held out. Other rows were not measured.
3. **Dashboard ranking.** The side list puts the in-sample 12.79 first among all live rows, above the verified leaders
   (R4 understated it as 12.79 vs 13.00).
4. **Catalogue head against its own horn lug (unmodelled).** This is the sidecar red team's own geometry (finding 2b):
   ball centre ZB 3.0 mm over the lug, head O9 x 4. The rim's height over the lug top is 3 - 2 cos t - 4.5 sin t; this
   formula reproduces the red team's -0.58 mm at 22.6 deg.
   - At this row's horn tilt it gives **-0.10 mm at the taken maximum 15.1 deg** and -0.38 mm at the range maximum
     19.4 deg (`probe extras.sc_info.tilt_max_taken[1]`, `tilt_max_range[1]`).
   - With the modelled O7 it is +0.16 mm.
   - So even at r_h 15.9 the catalogue-headed build needs a spacer of about 0.1-0.4 mm. This is a hand calculation, not
     re-worn.
5. **For the envelope polish (wf_d261725f-27c), in addition to the auditor's 7 items:**
   - The ear's pivot disc / strip overlap. A polish that moves `zc` / `clay` or enlarges the ear gains sample-weighted
     in-band from the double-sampled area.
   - With the catalogue head, transmission is 49.8 deg against the 48 deg gate: the bound must not be walked.

**Final verdict (ledger): WATCH.** The number is real: 18.87 / 23.21 reproduce, and the catalogue-headed robust number
18.83 is no worse. What stands against the record:
- `best_params` is not buildable with the named part and sits on a part-pair knife edge;
- the dashboard ranks the in-sample 12.79 first;
- the in-band edge over the leader is the ear's double sampling;
- the spring's dynamic hold is unmeasured.
