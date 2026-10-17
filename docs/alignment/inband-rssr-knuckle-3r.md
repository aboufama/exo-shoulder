# Alignment audit: inband-rssr-knuckle-3r

Auditor run 2026-10-17 13:04-13:20 UTC (hourly audit 13:03). This run was due for one reason: the display and judge
change a510cfe (12:41). That commit added the lead's `leader_ruling` text to the row. It also changed
`tools/dash_build.py`: a CONFIRMED polish now reads its pick key from `polished_id` and is promoted to status
'verified'. And it changed the headline in `docs/dashboard/simple/index.html` and `public/index.html`: a row ruled
'tie: X' or 'no lead' is skipped. The row's claim did not move: polished pick3, 18.33 bench / 22.86 held, the same
number the 12:28 audit and the 12:36 skeptic judged (48be5d5).

- **Checks:** `docs/alignment/inband-rssr-knuckle-3r.json`, run with `--ref slipper-nose-knuckle-3r` as before.
- **Findings:** `docs/alignment/inband-rssr-knuckle-3r.findings.json`.
- **Ledger:** `docs/alignment/ledger.jsonl`, 13:10:58Z, `by auditor`, run `audit:inband-rssr-knuckle-3r`.
- **New tool:** `tools/alignment_headline_probe.mjs`. It re-runs the page's own `board` and `leader` calcs,
  extracted verbatim from the page, on `morphs.json` and on what-if copies held in memory. Its output is
  `docs/alignment/remeasure/inband_pick3/headline_probe_{simple,public}.json`.
- **Cost:** local only, $0 farm.

## Verdict: WATCH (the ledger's verdict). The display change hides nothing and promotes no unverified number today. Two latent defects.

- **Claim:** `polished_gap` 18.33 (pick3, priced), unchanged since the verifier's 931a8d1.
- **What the board shows now:** this row is #1, 'Verified (tie)', at 18.33 with every term filled: reach 0.7194,
  follow 1.0, in-band 0.9071, contact 0.0027. Those are the verifier's
  `docs/research/inband_env_polish/verify/claim_pick3_fit60_bench.json` numbers to the digit, and they recompute to
  18.33.
- **The headline** is slipper-nose-knuckle-3r 18.49, "tied with In-band RSSR knuckle (pick3)". Both print score 93.3.
  Gamed rows are still forced to 'Flagged': dipped-law-groove 18.64 is Flagged and sorts below every verified row.
- **Promotion:** only two rows carry a CONFIRMED polish. One is this row. The other, minarc-stop-knuckle-4r, was
  already verified and has 4 DOF, so it is outside the 3-joint headline.

| question the lead asked | measured answer |
|---|---|
| can the change hide a real leader? | **Not today.** The tie target is the headline, so the tie is named. It can when the ruling goes stale. Measured with the page's own code: if slipper-nose is flagged or refuted, the headline goes to trimlug-k165 at 18.51; with a new verified 3-joint row at 18.45, that row takes it. In every case this row (18.33, Verified) leaves the headline unnamed (`headline_probe_simple.json`, runs A / B / C). |
| can it promote an unverified number? | **Not today.** The promoted v_* match the verifier's file. But the promotion keys off free text (`polished_status` starting with 'CONFIRMED'). It checks no verifier file and no ledger entry, and it lives only on the dashboard. The row still says 'screened', so the auditor's own R1 guard never fires (finding NEW-freetext-promotion). |
| does the board show 18.33 (priced) while the ruling uses 18.32 (unpriced)? | **Yes.** The bench difference is 0.01, so the board order is unchanged. The held-out reading is where the two disagree: 22.86 priced vs 23.54 unpriced, against the leader's 23.45. The board does not show held-out numbers (finding NEW-reading-mismatch). |
| does the promotion key off a free-text status rather than the ledger? | **Yes** (finding NEW-freetext-promotion). The ledger is read only for 'gamed' -> Flagged. |

## What the wearer gets (pick3 as claimed, under the leader's protocol unless noted)

The claim is unchanged, so this is the 12:28 audit's wear. I recounted it this run from the per-pose dumps
`remeasure/inband_pick3/claim_O7nominal_unpriced_{bench,held}_perpose.json` and
`farm/claim_pick3_fit60_*_perpose.json`.

- **Overhead (elevation >= 140):** 9 of 28 workspace poses taken on the bench, 19 of 71 held out. The leader takes
  8 / 18.
- **Raised arm by band** (held, priced claim dump): elevation 90-120 takes 68 of 140, 120-140 takes 27 of 89, 140-160
  takes 11 of 35, and 160+ takes 8 of 36.
- **Workspace reach:** 260 of 360 and 646 of 952 (priced: 259 and 648). The leader takes 261 and 650.
- **Taken poses with metal under 2 mm:** 19 bench / 52 held unpriced, and 22 / 54 priced. The leader has 25 / 62.
  Counting the model's extra walls, it is 26 / 64 against 30 / 67.
- **Lowest metal on a taken pose:** 0.31 mm bench, 0.01 mm held (unpriced).
- **Deepest contact:** 8.30 mm held out. The 4 overhead contact poses sit at elevation 150.
- **Workspace in-band (unscored, priced):** 0.873 / 0.874. At elevation 90-140 it is 0.832 / 0.845, and overhead it
  is 0.935 / 0.934.
- **Springs:** 0.172 N.m at J2, which gives 1.15 / 1.44 N at the cuff. That is 17 % / 29 % of R17, static only.
- **Stops:** the drive range ends on the law (dK 65.5 deg, against 47.5 deg taken).
- **Singularity:** transmission >= 52.2 deg, with no jam in range.
- **Not measured:** cuff twist and dynamics.
- **DOF:** 3 active joints, O20 hubs, complexity 28.5 (the leader's is 22.25).

## Checks (tool, this run)

The tool's verdict is WATCH. It comes only from the two check false positives the skeptic refuted at 11:40 and
again at 12:45:

- **held_out** reads the empty top-level `v_gap`.
- **idle** reads the kneeless models' `knee_moved` flag.

The rest:

- **dominance** vs slipper-nose: plain -0.38, 2 mm -1.10, so this row is behind on both. That is the row's 18.87 pick,
  the tool's default remeasure.
- **Tool side effect:** run without `--ref`, dominance now says 'no reference'.
- **reporting** prints "dashboard status 'verified' vs row 'screened'" but stays 'ok'. That is the gap this audit
  measures in NEW-freetext-promotion.
- **near_touch, continuity and sampling** still read the default remeasure of the row's pre-polish pick (18.87), not
  the polished pick3. pick3's own near-touch and continuity are in `remeasure/inband_pick3/` and the polish verifier's
  files.

## Findings (all watch)

### NEW-stale-tie: a headline ruling that outlives its basis (new; display change a510cfe)

- **Evidence.** The headline skips any row whose `leader_ruling` matches `/^(tie|no lead)/i`. It names a tie only
  while the tie's target is the headline.
- **The probe** (`tools/alignment_headline_probe.mjs`, same result on both pages):

  | what-if | headline | this row (18.33) |
  |---|---|---|
  | as published | slipper-nose 18.49 | named |
  | slipper-nose flagged gamed | trimlug-k165 18.51 | kept out, not named |
  | slipper-nose refuted | trimlug-k165 18.51 | kept out, not named |
  | new verified 3-joint row at 18.45 | that row | kept out, not named |
  | ruling text begins with a space | **inband-rssr 18.33** | takes the headline despite the tie ruling |
  | row status 'screened' (pre-promotion) | slipper-nose 18.49 | named, shown Checking |

- **A 'no lead' ruling** is never named in the headline, and its board pill shows no mark except on hover.
- **Why the exo is not better or worse.** Nothing is hidden today. But a tie ruled against one design says nothing
  about the next headline. If the leader changes, the board's lowest verified 3-joint gap leaves the headline in
  silence, or comes back on a typo.
- **Action:** proposal P-F below. The lead re-rules or clears the tie whenever the headline changes.
- **Proposed catalogue entry, R5. A display ruling that outlives its basis.**
  - Looks like: a hand-written ruling that removes or adds a row on the headline, with no link to the comparison it
    was made on.
  - Detect: re-run the page's leader calc and list every verified 3-joint row with a lower gap than the headline that
    the headline does not name (`tools/alignment_headline_probe.mjs`).

### NEW-freetext-promotion: dashboard-only verification keyed on text (new; display change a510cfe)

- **What the code does.** `tools/dash_build.py` lines 401-413 promote any ideated, modelling or screened row whose
  `polished_status` text starts with 'CONFIRMED'. They do not check a verifier file or the ledger.
- **Today the number is the verifier's.** So this is a guard defect, not a gamed number.
- **The disagreement.** The row file still says status 'screened' with `v_gap` null, and the ledger records
  'screened'. Only the board says 'verified'.
- **The guard bypass, measured in memory.** I ran `c_reporting` (`tools/alignment_audit.py`) twice:
  - on the row as filed, it returns 'ok';
  - on the row with the dashboard's status (verified, v_gap 18.33), it returns **watch**: "status verified but no
    verifier file under docs/concepts/verify/; verdict text still reads as a self-measured screen".
  - There are 0 files for this id under `docs/concepts/verify/`. The verifier wrote to
    `docs/research/inband_env_polish/verify/`.
- **The same split** produces the `held_out` false positive the skeptic has now refuted twice.
- **The latent risk.** A polisher that writes 'CONFIRMED' into its own `polished_status` is shown Verified. If it is
  the lowest gap and has no ruling, it takes the headline, before any audit (probe run D: without the ruling, this
  row takes the headline at 18.33).
- **Action:** proposal P-G.

### R3: best of 3 shown without its spread (carried, updated for a510cfe)

- **What a510cfe fixed.** The pick1 key defect the skeptic found at 12:45 is fixed: every v_* term is now filled.
- **What remains.** The board's #1 row is pick3, chosen post hoc from 3 committed picks: bench 19.15 / 19.49 / 18.33.
  Its edge on the leader is noise: paired bench -0.16, 90 % CI [-2.13, +1.64].
- **Ranking basis.** The board ranks on the bench gap alone. Held out, where pick3 is behind the leader under the same
  protocol, is not shown.
- **Action:** proposal P-H, carried from the 12:28 audit.

### NEW-reading-mismatch: priced claim next to an unpriced leader (carried, unchanged)

- **Bench:** 18.33 priced against 18.32 unpriced, so the board shows 0.01 better than the same-protocol reading.
- **Held out:** 22.86 priced against 23.54 unpriced. The leader reads 23.45, so the sign flips.
- **The tie ruling** uses the unpriced numbers, which is right. The board shows only the bench.

### P2: post-hoc pick (carried; the skeptic's missed item now on file)

- **The env-fit held leg:** pick3 is the worst of the three, 22.43 / 23.47 / 23.57
  (`farm/claim_pick{1,2,3}_env_held.json`). Its 23.57 is behind the leader's 23.45 even priced.
- **The fit60 legs** are the only ones where pick3 is best.
- **The pre-registered pick1** reads 19.15 on the bench.

### M2: the CAD config is not buildable with the named ball link (carried, re-checked)

- **The CAD config:** `polished_params_cad.r_h` is still 15.0125.
- **With the catalogue igus KBRM-02 O9 head,** that config loses every pose (`fit_O9.json`, 275.0). It lives from
  r_h 15.65.
- **Where the fix is written:** the part and r_h 15.9 now appear only in the `leader_ruling` text.

### M5: spring hold unmeasured (carried, unchanged)

The spring is static only. There is no dynamics, R17 or CAD run for this id, and the leader shares the same gap.

## Proposals (measurement or reporting changes, not applied, not inputs to this verdict)

- **P-F: a tie ruling names its target and expires.**
  - The page names in the headline every verified 3-joint row ruled a tie whose gap is below the headline's, as
    "(tie ruling vs X, stale)" when X is not the headline. It also labels 'no lead' on the pill.
  - Match on the trimmed, lower-cased text.
  - Measured effect today: none, because the target is the headline (all 6 probe runs on both pages). In runs
    A / B / C the headline would name this row.
- **P-G: verification lives in the row, not in the display.**
  - The polish verifier writes the row's `status: verified` and `v_*` itself, and records its file paths (e.g.
    `polished_verify: [...]`).
  - `dash_build` promotes only when a recorded verifier file's `final.gap` equals `polished_gap` to within 0.05.
  - `c_reporting` treats a dashboard-promoted row as verified for its R1 check, and reads the verifier paths the row
    names.
  - Measured effect today: this row passes the file test (18.33 = `verify/claim_pick3_fit60_bench.json` final.gap).
    minarc is already verified. No verified row moves. The `held_out` false positive on this row disappears.
- **P-H (repeated): show the best-of-N spread.**
  - A polished pick on the board carries "best of 3: 18.33-19.49".
  - Effect: display only, no row moves.
- **P-D (repeated): read a claimant and its incumbent under one protocol before any leader comparison.**

## Numbers I could not get

- **No re-wear this run.** The claim did not move: a510cfe changed only `leader_ruling`. pick3 was re-worn at 12:28
  under both protocols, with the O9 head and with the ear de-duplicated (`remeasure/inband_pick3/`). The tool's
  default remeasure files (11:06) are the row's pre-polish pick and were not re-run.
- **The trimlug-k165 what-if** (it takes the headline in runs A / B) uses its current, still-unaudited verified row.
  Its audit is running in the discovery loop, and I did not duplicate it.
- **Cuff twist, dynamics and the leader read priced:** as in the 12:28 audit, out of scope and out of budget.

---

*Earlier sections below: the skeptic of the 12:28 pick3 leader-change audit (12:30-12:45 UTC) and the 11:03 audit's
skeptic, kept unchanged. The 12:03-12:35 auditor sections they answer are replaced by the run above and remain in git
history (48be5d5).*

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
