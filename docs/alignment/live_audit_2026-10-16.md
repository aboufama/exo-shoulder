# Live alignment audit, 2026-10-16 (20:17-20:55 UTC)

The question: is anything scoring higher without being a better exo? "Better" is the user's goal: every part rides
about 1 cm off the skin (2-14 mm passes, 10 mm is the aim) over the full range of motion, overhead most of all, never
touching. The arm moves freely through its whole natural range. At most 4 DOF, 3 preferred, every joint a real part.
The unpowered MVP1 genuinely tracks the arm. The score and its benches are a proxy for that goal.

This is part 2, the live audit of what is claimed right now. Part 1 is the catalogue and the automatic checks
(`docs/ALIGNMENT.md`, `tools/alignment_audit.py`, proposals A1-A9). Findings part 1 already made are cited, not
repeated.

**Method.** Nothing here changes a score, a judge, a bench or a model. One new instrument: `tools/alignment_wear_probe.py`
(new file).
- It wears a design's frozen shape through its own verifier harness, unchanged: the claim's protocol, fit on Bench(60,160)
  fast, worn on Bench(110,360) exact.
- It reproduces the verified number to the digit.
- Then it reads the worn bench for what the gap does not see.

Outputs are in `docs/alignment/live_audit_2026-10-16/probe_*.json`, about 3 min per design locally (niced, 1 process).

    CB_EXACT=1 nice python3 tools/alignment_wear_probe.py <longdyad|parallelogram|frontload> <out.json>

## Headline

1. **The dashboard's "Best design so far" card showed an unverified fast-bench number from 18:39 to 20:24 UTC, and
   since 20:33 it shows an inflated one.**
   - It read 93.7, then 96.3 and 96.1. At 20:24 it reads 95.7 for sidecar-roller-flank.
   - That is the worst of the three sidecars frozen (20.08), and it leads only because it is the one not yet verified.
   - The card sat above the user's golden 95 bar for 1 h 15 min. The verified best is 93.31.
   - Since 20:33, with all three sidecars verified, the card reads longdyad 93.51 (verified 93.12) and ranks pick1
     third. That order is wrong on exactly the 3-vs-4-active question waiting on the user.
   - **Critical (reporting).**
2. **The in-band term never looks at the workspace.** `concept_bench.report()` reads in-band 2-14 over the 110 clip
   frames only, so 70 % of the taken poses carry no in-band cost.
   - On the 260 unscored taken workspace poses, every leader is 2.3-3.5 points lower.
   - Parallelogram's edge over longdyad exists only on the scored set.
   - **High.**
3. **Overhead, the user's first priority, is 7.8 % of the reach term.**
   - Every 3-active leader takes 8 of 28 overhead workspace poses (29 %) and about 40 % of raised-arm poses (elevation
     >= 90).
   - On the overhead poses it does take, metal is < 2 mm from the skin model on 13-15 of 18.
   - The CAD's "R4 Overhead works 71 %" is an in-band number on one clip, not the share of overhead that works.
   - **High.**
4. **The golden 95 can be reached without one more overhead pose.**
   - At longdyad's contact, gap 13.75 needs reach 0.773 (+17 poses).
   - Longdyad loses 31 poses below elevation 90.
   - A search can therefore buy "95" on easy low poses while 71 % of overhead stays blocked.
   - **High (a goal question for the user).**
5. The round-8 sidecar gain over the rod-drive lead is **real**. Longdyad's in-band gain holds on the unscored workspace
   (0.874 vs 0.827), metal over 20 mm falls 8.3 % -> 2.8 %, and it has fewer near-grazing poses (26 vs 34).
   **Parallelogram's** edge over longdyad is **not** real: it has the same reach, a lower workspace in-band and 1.7x
   the grazing poses (part 1 calls it gamed on the 1-2 mm shell; this audit adds the workspace and the tie-break that
   caused it).

## Findings

| # | target | pattern | severity | action |
|---|---|---|---|---|
| L1 | dashboard leader card | unverified fast numbers ranked above verified frozen ones | critical | fix the dashboard |
| L2 | bench in-band term | clip-only in-band; workspace profile unscored | high | proposal P1 (re-measured below) |
| L3 | reach / R4 / overhead | top priority diluted to 7.8 %; R4's name says the opposite of the overhead reach | high | proposal P2, fix the R4 label |
| L4 | golden 95 / complexity switch | the bar is reachable without overhead | high | ask the user (P3) |
| L5 | sidecar-parallelogram | tie-break that selects skin-hugging; kill gate overridden by the screener | high | block a CAD swap; tie-break rule (P4) |
| L6 | contact term | depth-blind: -14.6 mm costs the same as -0.01 mm | medium | report depths; proposal P5 |
| L7 | R1-aim (10 mm) | invisible to every search; pick1's polish traded it away | medium | report + tie-break (P6) |
| L8 | continuity on the sidecars | a contact-aware flood exists (pick1) but the sidecars ran a kinematic-only one | medium | re-measure before the gen-6 CAD |
| L9 | pick1 R17 / judge preload plumbing | judge trusts a declared preload with no hold check; PASS is upright-only | medium | qualify the PASS; P7 |
| L10 | gen-5 R17 "judge gap" | a judge fix that makes the design pass, pending | medium | guard the fix (P8) |
| L11 | sidecar-roller-flank claim | config chosen by its claim-bench score (held out 22.35 now on file) | low | carry the 2 mm number in the verification |
| L12 | events / rows | hand-typed timestamps in the future, out-of-order log | low | stamp from the clock |
| L13 | sidecar rows | fold margin stated as a rule, not measured; lobe crest 0.16 mm outside hub 2's sampled envelope | low | add min `th` to the verifier output |

### L1. The dashboard leader card shows self-measured fast numbers as the best design (critical)

- **Evidence.** In `docs/dashboard/simple/index.html`, `board` uses the verified `v_gap` when there is one, else the
  row's `gap`, else the sweep best. `leader` takes the first row that is not "Dead end" or "Refuted", which includes
  "Checking" and "Sweeping".
  - A screened row's `gap` is its fast Bench(60,160) number. Parallelogram's row `gap` is 10.63, against 19.13 frozen.
  - The leader card, read from `docs/dashboard/data/morphs.json` at each refresh commit:

    | commit (UTC) | card | what it is |
    |---|---|---|
    | 18:39, 18:53 | longdyad 93.7 | sweep best, fast |
    | 19:09-20:09 | longdyad 96.3 | claim gap, fast 10.30 |
    | 20:18 | parallelogram 96.1 | claim gap, fast 10.63 |
    | 20:24 | roller-flank 95.7 | claim gap, fast 11.73; frozen 20.08, the worst sidecar |
    | 17:08 | frontload 94.3 | claim gap, fast |
    | 20:33 (after all three sidecars were verified) | longdyad 93.51 | recomputed `v_gap` 17.84; verified 18.91 = 93.12 |

- **Real vs metric.**
  - Real: the verified best is pick1 at 18.40 (93.31), and the best 3-active design is longdyad at 18.91 (93.12).
  - Metric: the card says 95.7-96.3, above the golden 95.
  - Fast to frozen loses 5.6-14 points on every row (HANDOFF lesson 7). Verifying a design moves it down the dashboard,
    so the card rewards staying unverified.
- **Action (dashboard fix).**
  - The leader card and the board rank only on a frozen exact number: verified first, then a self-measured frozen
    exact claim marked "self-measured".
  - A fast number is never a score on the card or the board. Show it only in the sweep charts, labelled "fast
    search".
  - This extends part 1's A2. The record line (part 1 R2: 97.75 from minarc's refuted 08:12 sweep) and the `v_gap`
    recomputation (part 1 R4) are the same family.
  - With the recomputation, the 20:33 refresh inverts the verified order (measured on HEAD's `morphs.json`):
    longdyad 93.51 > parallelogram 93.43 > minarc 92.89, against the real pick1 93.31 > longdyad 93.12 >
    parallelogram 93.04.
  - The minarc row's `v_*` fields are still BDp's (19.54). pick1's 18.40 sits in `polished_gap`, which the builder
    does not read. That inversion lands exactly on the user's open 3-vs-4-active question (HANDOFF section 7).

### L2. In-band is scored on the clip frames only; the workspace profile is free (high)

- **Evidence.** `tools/concept_bench.py` `report()` reads `taken = [j for j in cl if ok(j)]` and computes `inband14`
  from those clip frames. The 360 workspace poses enter only through reach and contact.
- The probe measured the frozen Bench(110,360) exact, verified shapes:

  | | longdyad 18.91 | parallelogram 19.13 | frontload 22.82 |
  |---|---|---|---|
  | in-band14, clip frames (scored) | 0.8966 | **0.9049** | 0.8546 |
  | in-band14, taken workspace (unscored) | **0.8736** | 0.8702 | 0.8266 |
  | in-band14, workspace elevation 90-140 (unscored) | 0.841 | 0.833 | 0.785 |
  | metal samples > 20 mm, workspace | 2.8 % | 2.8 % | 8.3 % |
  | gap if in-band read all taken poses (pose-weighted, approx.) | 20.53 (+1.62) | 21.08 (+1.95) | 24.79 (+1.97) |

- **Real vs metric.**
  - The sidecar profile gain over frontload is real: +4.4-4.7 points in band on the unscored workspace, and metal over
    20 mm down from 8.3 % to 2.8 %.
  - Parallelogram's 0.22-point plain lead in in-band is a metric artefact. It clears the 0.90 kink on the scored clip
    set (0.9049, 0.9001 at ZB 4.5), but on the workspace it is lower than longdyad's.
  - Any future search can trade workspace profile for clip profile at no cost.
- **Action.** Proposal P1 below.

### L3. Overhead: the user's first priority barely moves the score, and R4's name hides it (high)

- **Evidence (probe, workspace reach by elevation, taken / poses):**

  | elevation (deg) | 0-60 | 60-90 | 90-120 | 120-140 | 140-160 | 160+ | raised arm (>= 90) |
  |---|---|---|---|---|---|---|---|
  | longdyad | 161/172 | 55/75 | 25/51 | 12/34 | 5/13 | 3/15 | **45/113 (40 %)** |
  | parallelogram | 161/172 | 56/75 | 22/51 | 12/34 | 5/13 | 3/15 | 42/113 (37 %) |
  | frontload | 161/172 | 55/75 | 25/51 | 13/34 | 5/13 | 3/15 | 46/113 (41 %) |

- The workspace sample is 48 % below elevation 60, where every design takes 94 %, so reach 0.72 hides a 60 % block on
  the raised arm.
- Overhead (elevation >= 140) is 28 of 360 poses, 7.8 % of the reach term. All 3-active leaders take 8.
- On the taken overhead poses, the closest metal is under 2 mm from the skin model on:
  - longdyad: 13 of 18 (8/10 clip, 5/8 workspace);
  - parallelogram: 15 of 18;
  - frontload: 13 of 18.
- Longdyad's deepest contact is overhead too: -4.61 mm at plane 30 / elevation 165 / axial -60.
- The CAD scorecards' **R4 "Overhead works (Raise overhead clip score)" reads 71-73 %**, an in-band share on one clip.
  HANDOFF section 4 tabulates it as "R4 overhead 71.0 %". The share of overhead poses the mechanism takes is 29 %, and
  the two numbers read as opposites.
- **Real vs metric.**
  - Real: a wearer raising the arm overhead meets the J2 fold stop on 71 % of overhead directions.
  - Where the arm does get overhead, the metal rides 1-2 mm off the modelled skin. A posed LBS skin carries no deltoid
    bulge and no shirt, so "would a wearer feel it?" gets a likely yes.
  - Metric: about 5.6 gap points.
- **Action.**
  - Report overhead reach (workspace, elevation >= 140) and overhead poses under 2 mm as headline columns in every
    claim, the dashboard and HANDOFF.
  - Rename R4's row to "Overhead clip in-band", and add the overhead workspace reach next to it.
  - Proposal P2.

### L4. The golden 95 is reachable without improving overhead (high; for the user)

- gap 13.75 with follow 1.0 and in-band >= 0.90 needs reach 0.7625 at zero contact, or 0.7732 at longdyad's contact
  0.0107.
  - That is +17.4 workspace poses for longdyad.
  - Longdyad loses 31 poses below elevation 90, 11 of them below 60.
- So a search can hit the golden bar on low poses while overhead stays at 8/28 and 23 % of everyday workspace stays
  blocked.
- CLAUDE.md then switches the objective to minimum complexity at score >= 95, which would freeze reach there.
- **Action (P3, the user's call).** Ask whether "95 %" means this. A floor would keep the golden bar honest. One
  candidate is overhead reach >= R4's own 0.80, or raised-arm reach >= 0.75.
  - Measured effect: every current leader fails it (overhead 0.29, raised 0.37-0.41).

### L5. sidecar-parallelogram: a tie-break that selects skin-hugging, after an overridden kill gate (high)

- **Evidence.**
  - The claim config was "picked from 209 fit-bench ties by a rule declared before any frozen wear (max fit in-band)"
    (`docs/concepts/sidecar-parallelogram-knuckle-3r.md`, red team). All 209 ties sit past the 0.90 kink.
  - Past the kink, more in-band buys nothing on the gap and comes mostly from lowering metal, so the rule picks the
    tie that hugs the skin hardest.
  - The worn result:
    - 44 poses with metal < 2 mm, against 26 for longdyad and 34 for frontload;
    - per-pose floor histogram on clips: 19 poses at 1-2 mm, 0 above 6 mm. Longdyad has 10 at 1-2 mm and 13 at
      6-10 mm.
  - The screen's own kill gate failed (18.30 near-touch against a bar of 14.0, untuned). The agent went on with a
    stated reason; the gate belonged to the round's judge.
  - The verification event says "0.64 ahead held out" (22.03 vs 22.67). That is plain only. At 2 mm held out the
    order flips: 48.71 vs 37.24.
- **Real vs metric.** It has the same reach and fold as longdyad (88 vs 86 fold losses), the same profile on the
  workspace, and 1.7x the grazing poses. Its 0.22-point plain gap to longdyad is noise in its favour on the scored set.
  Part 1 measured the 1-2 mm shell at 31.01 points (dominance check: gamed against frontload).
- **Action.**
  - Block any CAD swap to parallelogram.
  - For the round-8 close, rank longdyad first on plain, 2 mm and held-out 2 mm.
  - Kill gates set by a round's judge may be overridden only by the lead, with the override logged as an event.
  - Proposal P4.

### L6. Contact is binary and depth-blind (medium)

- **Evidence.** `contact` is the share of poses with any metal < 0. A pose 14.6 mm inside costs the same as one at
  0.01 mm. On a chain that still closes kinematically, a contact pose is the exo pressing into the wearer, not a stop.
  - pick1's polish gained +2.37 held out with 28 raw contact poses against BDp's 9, deepest -13.0 / -14.6 mm overhead:
    hub K into the raised deltoid (row `polished_red_team`).
  - Longdyad: 4 contact poses, -4.61 / -0.77 / -0.74 / -0.11 mm, the deepest overhead (probe).
- **Real vs metric.** The bench charged pick1 1.74 points of contact, net of which it still gained. Contact depth is
  never shown next to the score. A -14.6 mm press is a felt event, and possibly a bruise, in exactly the overhead
  region the user cares about.
- **Action.**
  - Every claim and verifier prints its contact depths: the list, the max, and the count deeper than 3 mm.
  - Proposal P5.

### L7. The 10 mm aim is invisible to every search (medium)

- **Evidence.** The gap uses in-band 2-14 only.
  - Leaders sit at in-band10 0.52-0.56, and the CAD's R1-aim is 47-51 % on every build.
  - pick1's final polish lowered held-out in-band10 from 0.574 to 0.497 (env fit) while gaining 2.37 on the gap (row
    `polished_red_team`).
- **Real vs metric.** The user said "pass at 14, aim for 10". No search has any pull toward 10, and a polish may give
  it away for free.
- **Action.** Proposal P6.

### L8. Continuity: the sidecars were held to a weaker flood than pick1 (medium)

- **Evidence.** The sidecars' claimed continuity is `connected_full`, which drops 0 poses. Its intermediate nodes are
  envelope poses where the chain closes, "skin not evaluated there"
  (`docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py`, `flood`).
  - pick1's verifier also ran a contact-aware flood (nodes = poses the frozen shape takes worn exact): 0 extra drops
    (`docs/concepts/verify/minarc-final-polish-verify.py`).
  - The sidecars' knn flood drops 10-11 poses (+2.8 / +3.1). Part 1's A4 proposes claiming on knn.
- **Real vs metric.** Unknown until measured. A path through poses where the hub sits inside the deltoid is not a path
  the wearer takes.
- **Action.** Run the contact-aware flood on longdyad, parallelogram and roller-flank, on the farm (~$0.3) before the
  gen-6 CAD. If it agrees with `full`, the claims stand.

### L9. pick1's K hold: a judge that trusts a declared parameter (medium)

- **Evidence.**
  - `judge/dynamics.py` (lines 316-318) now reads `build_fixes.spring.preload` from the design, falling back to 0.08.
    A lower declared preload lowers R17 drift.
  - No judge checks that the declared preload still holds K. The hold check (2 g upright, real direction) lives in a
    research harness (`docs/research/pick1_k_hold/`).
  - pick1 at 0.04 N.m holds 0.84x the red team's 2 g any-direction envelope.
  - Its R17 drift is 3.72 deg upright but 4.1 / 5.7 / 6.1 / 7.7 deg with gravity across the thorax: it fails 3 of 4
    lying or leaning directions (`docs/research/pick1_k_hold_check.md`).
  - Both pick1 scorecards print R17 **PASS** unqualified.
- **Real vs metric.** Upright, the tracking is real. Lying or leaning, the cuff twist returns. The 7/19 includes a pass
  that holds in one posture. Part 1 lists the pattern (P4, M5). The new risk is the interface: any design can now
  declare its way to a lower drift.
- **Action.**
  - The scorecard reads "PASS (upright only)" until the user answers HANDOFF question 2.
  - Proposal P7.

### L10. gen-5 (`l1_geneva-rod`): the R17 "judge gap" is plausible; guard the fix (medium)

- **Evidence.** In `dynamics.json`, at f0.05 the slaved K drifts as a spare joint: spare_drift 22.25 deg, twist 11.37
  deg, 37 lags over 10 deg. The judge has no lobe-rod coupling, so the HANDOFF's "judge gap, not a measured jam" fits
  the data.
- **Risk.** It is the 0.08 N.m pattern again: a judge edit in the same task that makes the design pass.
- **Action (P8).** The coupling term must carry:
  - the drive's real slop: ball-link socket play, 0.18-0.6 deg of K;
  - its compliance;
  - its pressure-angle stall limit (45 deg).

  A regression case with a coupling that does stall (pressure angle > 45) must still fail. An independent check must
  pass before the re-judged R17 counts.

### L11. roller-flank: claim chosen on the claim bench (low)

- P1 (20.08) was claimed over the fast-best P1d (20.48 frozen) after both were worn on Bench(110,360). That is a
  2-candidate selection on the claim bench. The reason given (P1d is fold-tuned to the 160-pose sample) is sound, but
  the choice was still made on the bench it is scored on.
- It was verified at 20:28 (20.08 reproduced to the digit, held out 22.35), which settles the held-out question. Its
  2 mm near-touch is 46.82 (45 poses, self-measured); the verification event does not restate it.
- **Action.** Carry the 2 mm number in the row's verification block, as for the other two sidecars.

### L12. Hand-typed timestamps (low)

- Parallelogram's row has `verification.t` 20:35:00Z, but commit c7b5c53 landed at 20:20:12.
- The events line "audit twist-long-a2-knuckle-3r" is stamped 20:31:00Z and was committed before 20:22.
- 8 of 510 events lines are out of order.
- The dashboard event feed and the record chart sort on these stamps.
- **Action.** Stamp from the clock (`date -u`), never by hand.

### L13. Small evidence gaps on the sidecar rows (low)

- The rows state the fold-margin rule ("m3e >= 5 deg of th in every taken state") but carry no measured minimum `th`
  margin, which CLAUDE.md asks for.
  - The longdyad verifier computes `th` (`frozen_wear`) and drops it. Part 1 A7 covers it.
- longdyad's lobe crest is 10.16 mm against hub 2's sampled envelope of 10.0 mm, 0.16 mm unsampled. That is
  negligible.
- The RSSR transmission minimum is 38.8 deg. The model's gate is 30; common linkage practice is >= 40. It sits just
  under; flag it on the part drawing.

## What the score does not see (for every design)

- **The feel of the fold stop.** A fold-lost pose is the arm meeting a hard stop. Reach counts it, but the dashboard
  shows only the share.
- **Profile height.** Hub crowns sit 12.25 mm above the hub base (`tools/concept_kit.py` CROWN). In-band samples the
  skin-facing faces; crowns enter only the near-touch floor. The O20-only ruling makes this equal across designs today.
- **Mass, cuff twist, driving torque and pressure.** These are CAD judges only (R8, R17, R11). The bench is blind.
- **Skin-model fidelity.** A posed LBS skin with no muscle bulge and no clothing. It matters most overhead, where
  13-15 of 18 taken poses ride < 2 mm.
- **Base slip.** R10 measures 15.2 mm against a 4 mm target, design-independent (HANDOFF section 4).

## Clean (checked, nothing found)

- **Longdyad verification.**
  - The probe reproduces 18.91 / near-touch 20.00 / 34.03 (26 poses) to the digit through the verifier's own
    `frozen_wear`.
  - The added RSSR / tilt / pressure-angle checks drop 0 poses.
  - The drive is not idle on the worn bench (dK taken 37.8 deg >= 30). Its model has no idle rule, but it measures
    clean.
- **Parallelogram verification.** Reproduces 19.13. The idle check and the ZB sensitivity are reported honestly
  (in-band 0.9001 at ZB 4.5, on the edge, and said so).
- **The round-8 sidecar gain over frontload is real** (L2 table: workspace in-band +4.4 points, metal > 20 mm 8.3 % ->
  2.8 %, 26 vs 34 grazing poses for longdyad).
- **O20 only.** No sidecar model overrides `HUB_R` or `FOLD_MARGIN`. The kit's `hub_rad()` gate holds.
- **Fold margin.** The kit rule applies (m3e >= 5 of `th`; K stop B <= bk1 + bk2 - 5). No virtual stop like minarc's
  1.4-deg reading.
- **The HANDOFF leaderboard** matches the rows (18.40, 18.91, 19.13, 22.82, 23.57) and carries the parallelogram
  2 mm flag.
- **frontload's attribution is honest** ("law and stop B are noise; the gain is the seat re-fit"). The 1-point CAD-swap
  rule was applied, so gen-5 stayed on the rod.
- **twist-long-a2's death** was re-measured through the same harness (24.46 vs 22.82).
- **pick1's preload change** was stated as a measurement change and independently re-run (events 19:18). Only the
  posture caveat and the judge interface remain (L9).
- **dash_build** keeps the larger gap when a sweep file disagrees with its recomputation, which is conservative. It
  logs 27,471 warnings; the 2,000 it prints are all on arm-parked-knee-4r sweeps.
- **No claim re-measured until it passed** in the round-8 logs. The three sidecar verifiers report the claims
  reproduced to the digit (events 20:19, 20:22, 20:28), and no earlier failed verification of these rows is on file.

## Proposals (measurement or reporting changes; the lead and the user decide, nothing applied)

Effects are measured on the three probed verified rows. The other rows: run the probe or part 1's `remeasure`.

| | proposal | longdyad | parallelogram | frontload | ranking |
|---|---|---|---|---|---|
| P1 | in-band over all taken poses (clip + workspace), not clips only | 18.91 -> ~20.53 | 19.13 -> ~21.08 | 22.82 -> ~24.79 | unchanged; parallelogram's 0.22 deficit grows to ~0.55 |
| P2 | overhead workspace reach (elevation >= 140) and overhead poses < 2 mm as headline columns; R4 to include overhead workspace reach against its 0.80 target | 0.29, 13/18 | 0.29, 15/18 | 0.29, 13/18 | no design passes; separates nothing today, but shows the real deficit |
| P3 | the golden 95 needs a floor on raised-arm or overhead reach (user) | raised 0.40 | 0.37 | 0.41 | all fail a 0.75 floor |
| P4 | tie-break among search ties on the 2 mm near-touch (fewest poses < 2 mm), never on max in-band; kill-gate overrides only by the lead | 26 poses < 2 mm | 44 | 34 | parallelogram would not be the claim config chosen |
| P5 | contact depth reported; a CAD swap needs no pose deeper than 3 mm, or depth-weighted contact (user) | max -4.61 (1 pose > 3 mm) | not probed | not probed | pick1 has poses at -13 / -14.6 held out |
| P6 | in-band10 as the tie-break and a reported column in every polish; a polish that loses > 2 points of held-out in-band10 needs the lead's say | 0.534 | 0.523 | 0.558 | pick1 0.574 -> 0.497 held out would be flagged |
| P7 | R17: when a design declares its preload, the judge also runs the hold check (2 g, real direction) and the 4 lying / leaning gravity directions; the scorecard qualifies a PASS that holds in one posture | - | - | - | pick1 R17 -> "PASS (upright only)" |
| P8 | the slaved-K coupling term for R17 lands with a stall regression case and an independent check before any re-judge counts | - | - | - | process |

## Next

- **Dashboard (L1).** Fix it before the next user-facing message. The card is the first thing the user reads.
- **Round 8 closed at 20:31 with longdyad as the winner.** Longdyad stays the 3-active leader on every reading here
  (plain, 2 mm, workspace in-band), and the closer already ranks parallelogram as gamed at 2 mm. Run the
  contact-aware flood (L8) on longdyad before the gen-6 CAD.
- **State round 9's target in raised-arm terms.** The closer says 95 needs reach 0.775, +18-19 poses (L4). Unless the
  target names overhead or raised-arm reach, a search can find those poses below elevation 90 (31 lost there) and
  leave overhead at 8/28.
- **Make the probe part of every verify.** It reproduces the claim in about 3 min locally and adds the unscored
  workspace, elevation and overhead numbers. Part 1's hourly audit can call it.
- **The user's say on P3 / P5.** It belongs in the next big-update message: the golden 95 and contact depth are goal
  questions, not measurement ones.
