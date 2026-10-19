# Alignment audit: kneeless-sidecar-knuckle-3r (2026-10-17)

The round-8 lead (sidecar-longdyad) with J3 on a GH ray (b3 0) and the two-pin knee replaced by one rigid bent 3 mm Ti
bracket. 3 active (J1, J2, J3), K slaved by the RSSR sidecar and never read, 0 passive translations, 0 sensed passives,
complexity 28.

## Verdict and claim

- **Claim:** verified gap 21.11 (score 92.32), Bench(110,360) exact, frozen shape fit on Bench(60,160) fast. Held out
  25.34. It is not a lead: the round-9 winner, roller-longdyad, is at 18.67 (its lead status is under its own audit), and
  the round-8 lead is at 18.91. Under the user's
  2026-10-17 rule the plain verified gap decides, and 21.11 loses on it by 2.44 and 2.20.
- **Re-measured here, models unchanged, on the CPU farm (~$0.02):**
  - bench 21.11 and held out 25.34, both reproduced to the digit;
  - the fit reproduces the row's fast plain (15.63), so the re-wear is a valid claim reproduction, not a cache artefact;
  - files: `docs/alignment/remeasure/kneeless-sidecar-knuckle-3r_bench.json`, `_held.json`, `_probe.json` and
    `_probe_held.json`.
- **Ledger verdict: GAMED.** `tools/alignment_ledger.py` printed it; the auditor cannot lower the tool's level.
  - The only 'gamed' reason is the tool's idle check. It reads the deleted knee's constant angle (K.ang 128.5952 deg)
    as an idle drive.
  - The drive it is meant to test moves: dK spans 35.77 deg on the bench and 36.34 deg held out.
  - This is a false positive, the same one its twin kneeless-roller carries (finding 1). A skeptic should refute it,
    with the evidence below.
  - With idle refuted, every other reason is watch. **No finding shows the number ranking this design above a design
    that is better for the wearer.**
- **What the false positive changes now:** round 10 (docs/concepts/ROUNDS.md, lens 3) picks this design as a base
  over kneeless-roller because it was "not gamed". The re-wear in this audit puts both twins on the same footing.

## What the wearer gets (measured)

All figures are from the Bench(110,360) exact frozen wear unless marked as held out. The lead is sidecar-longdyad,
measured with the same probe.

| quantity | this design | lead | file |
|---|---|---|---|
| Overhead reach (workspace, elev >= 140) | **8 / 28** taken (lost: fold 13, parts 4, contact 3). Held out 17 / 71 | 8 / 28 | `_probe.json` ws_overhead_why_not; `_probe_held.json` |
| Raised-arm reach, taken / total, by elevation | 0-60: 158/172; 60-90: 57/75; 90-120: 23/51; 120-140: 11/34; 140-160: 5/13; 160-200: 3/15 | 161, 55, 25, 12, 5, 3 | `_probe.json` ws_reach_by_elev |
| Taken poses with metal under 2 mm | 22 of 367 (clip 8, workspace 14); 6 of the 8 overhead. Held out 50 of 853 (12 of 17 overhead) | 26 of 371 | `_bench.json` deep.near2_poses; probe floor_hist |
| Taken poses with metal under 1 mm (the user's contact line) | 3 (lowest 0.476 mm). Held out 14 (lowest 0.025 mm) | 2 (0.278 mm) | `_bench.json`, `_held.json` deep |
| Taken poses with metal under 3 mm | 130 of 367 (35 %). Overhead floor p10: 1.40 mm (held out 1.05) | 178 of 371 (48 %); p10 1.02 | deep.near3_poses |
| Contact (metal into the skin) | 5 poses, summed depth 27.45 mm, **deepest 17.6 mm at (plane 0, elev 165, axial -45)**. Held out 21 poses, 76.79 mm, deepest 16.47 mm | 4 poses, 6.23 mm, deepest 4.61 mm | probe contact_poses |
| Scored in-band 2-14 (clips) | 0.888; band read as 3-14: 0.883 (gap 21.65) | 0.897 | deep |
| Workspace in-band 2-14 (unscored) | 0.843 overall, **0.805** at elev 90-140, 0.944 overhead. Held out 0.847 / 0.828 / 0.949. Metal > 14 mm: 15.7 % (> 20 mm 3.7 %) | 0.874 / 0.841 / 0.926; 12.6 % (2.8 %) | `_probe.json` ws_* |
| Fold margin (th, taken poses) | min 5.293 deg on the bench, 5.106 held out; 0 poses under 5, 3 / 4 under 5.5 | - | probe extras.th_margin_own_state; verifier |
| Drive | dK taken 35.77 of 38.5 deg (stroke wall ROD-hub2). Transmission >= 45.5 deg, real lobe PA 37.1 of 45, ball-link tilt 21.4 of 30 | dK 37.8 | probe extras.sc_info; verifier |
| Springs, stops, cuff twist | One clock-spring cap holds the follower on the lobe. K rests on stop A on 62 % of taken poses (63 % held out). No spring-hold check is on file. Cuff twist: not measured (no R17) | same drive | verifier th_margin forced counts |
| Knee and cuff | No knee: bracket drift is 0.000 mm from the transforms. A 3 mm GH-centre error gives a cuff misfit of 4.83 mm p95 (knee would leave 4.14) | knee | row gh_offset_redteam |

Taken together: the same reach as the lead and less metal at 1-3 mm. The cost is more metal lifted out of band on the
workspace and deep contact at elevation 165, and both are invisible to the gap.

## Findings (docs/alignment/kneeless-sidecar-knuckle-3r.findings.json)

1. **NEW-idle-check-false-positive (watch).**
   - **Evidence:** `c_idle` takes the smallest span among dK, phi and `K.*`. `K.*` in this model family is the
     knee's dict (ang, phi, th, psi, qa, qb), and the knee is a rigid bracket by design: K.ang is constant at
     128.5952 deg, and the verifier measured 0.000 mm of bracket drift from the transforms. The slaved knuckle drive
     moves 35.77 deg (bench) and 36.34 deg (held out).
   - **Not a better or worse exo:** this is a measurement artefact.
   - **Action:** the skeptic refutes `idle` with the files above (proposal 1).
2. **NEW-free-deletion (watch).**
   - **Evidence:** the bench's GH is an exact fixed point, so a rigid closure costs nothing while complexity falls
     from 49 to 28. At a 3 mm GH-centre error, the cuff misfit is 4.83 mm p95 (max 5.14), against the 3 mm the liner
     may take. A planar knee would leave 4.14 mm. On the twin, 38.7 % of postures stay inside the liner with no knee,
     and 66.6 % with one.
   - **Why not better:** the round-9 lesson "the knee buys little reach" holds on the bench only.
   - **Action:** price the GH offset under one harness for the knee and kneeless rows (proposal 3).
3. **NEW-contact-depth (watch).**
   - **Evidence:** 5 contact poses summing 27.45 mm, deepest 17.6 mm at elevation 165, against the lead's 6.23 mm and
     4.61 mm.
   - **Why not better:** the score sees one pose either way. The wearer meets a hard block overhead that no liner
     absorbs.
   - **Action:** report depth beside count (the roller-longdyad audit's proposal B).
4. **NEW-ws-inband (watch).**
   - **Evidence:** workspace in-band is 0.843 / 0.805, against the round-9 lens floor of 0.874 / 0.841. Metal > 14 mm
     is 15.7 %, against 12.6 % for the lead.
   - **Why not better:** in-band is scored on the clips only.
   - **Action:** round 10 lens 3 inherits this base 0.03-0.04 under its own target. State it in the lens brief.
5. **T1 (watch).**
   - **Evidence:** 3 taken poses (held out 14) sit under the user's 1 mm contact line but count as taken in the plain
     gap. At 1 mm the gap is 22.75 (+1.64) and 28.41 held out (+3.07). The lead goes +1.09 and +3.08.
   - **Ranking:** unchanged.
6. **G1 (watch).**
   - **Evidence:** overhead, all 8 taken workspace poses have metal under 3 mm and 6 under 2 mm. Overall this design is
     better than the lead: 35 % against 48 % under 3 mm, and the 1-2 mm shell holds 12.04 points against 15.12.
   - **Not a gamed number:** this is a goal gap that every knuckle row shares.
7. **M5 (watch).**
   - **Evidence:** K is held on stop A by one spring on 62-63 % of taken poses, and no spring-hold check is on file.
   - **Why it matters:** the unpowered MVP1 tracking of K is unproven.
   - **Action:** run R17 or a gravity posture sweep before any CAD.
8. **S1 (watch).**
   - **Evidence:** E-L2 costs 0 fit-bench poses, 8 claim poses and 17 held-out poses. The fit bench exact is 14.00, the
     claim 21.11 and held out 25.34.
   - **Not inflated:** the claim counts these losses. The next lever (an E-leg joggle) must be searched on a bench
     that shows the clash.
9. **R1 (watch).**
   - **Evidence:** the row's verdict, note and `verification.dominance_A1` still decide on the retired A1 gate, and
     the verdict opens "SCREENED". The conclusion (not a lead) stands under the plain-gap rule.
   - **Stale "Pareto point":** the twin kneeless-roller (21.07, held out 24.59, complexity 23.75) is ahead on all
     three, although the 0.04 on the gap is noise.
   - **Dashboard:** it shows sweep_gap 20.24, CMA A's fast in-sample 2 mm objective. That run's frozen value was
     24.24.

### Walked and clean

| pattern | why it is clean |
|---|---|
| T2 | Reading the band as 3-14 costs 0.54. |
| T3 | The fold margin is measured in th: 5.293 on the bench, 5.106 held out. The tool's `fold_margin` watch is a key-lookup miss (proposal 2). |
| T4 | Every best parameter is inside its searched range: bk2 40.89 in [35.19, 42.27], r_h 15.37 in [13.0, 17.87]. The th margin is enforced and measured. |
| S2 | Part-weighted in-band (0.904) is above sample-weighted (0.889). Rod and L1a are thin (14 / 12 samples), at 0.869 / 0.97 in band. |
| S3 | The bracket is sampled (groups knee 0.971, E, boss and pad). |
| S4 | Covered by NEW-free-deletion. |
| S5 | Full flood 21.11 with 0 dropped. The knn flood costs +2.54, against the lead's +2.81. |
| M1 / M2 | O20 hubs, 3 mm plate, 0 passive translations. |
| M3 | The model switches off the parent's three adjacency pairs and re-adds two of them: E-L2 at 0.15 mm, and the bracket against hub 3 at the stricter 1 mm. The third pair (knee-E) is one body now. The collision box uses the moved bracket level. The verifier re-collided every taken pose, with a minimum of 1.58 mm. |
| M4 | The drive moves (see finding 1). |
| P1 | Held out is +4.23, under the 6-point watch level. |
| P2 | No held-out search. |
| P3 / R3 | Best of two CMA runs, both reported. A is 24.24 frozen and B 21.11. They tie on the objective (20.24 / 20.32), and B also wins fast plain in sample, so the claim bench did not pick B. |
| P4 | No bench, judge or metric change in the row's commits. |
| R2 / R4 | The dashboard v_gap is 21.11. |
| G2 / G3 | Not measured: no R17. |
| G4 | PA 37.1 of 45, transmission >= 45.5, th >= 5.1. |
| G5 / G6 | The recomputed complexity is 28, equal to the row. K is never read, so it stays 3 active under the sensed-joint ruling. This design has no sensed knee pins, which the 2026-10-17 ruling may yet count against both knee leads. |

### Numbers not obtained

- **Cuff twist and spring hold:** not measured, because no R17 / dynamics harness exists for this design.
- **The GH-offset within-liner share for this design:** not measured. The row has p95 and max only, and its `ghoff`
  mode does not report the share. Not re-run in the time box.
- **Paired bench / held-out interval against the twin:** not run.

## Proposals (not applied; measurement or reporting changes for the lead or the user)

1. **`c_idle` reads only the declared drive (dK, phi), not the knee dict `K.*`.**
   - **Measured effect on every re-wear on file:** only the two kneeless rows change, from gamed to ok:
     - kneeless-roller: dK 43.53;
     - this design: dK 35.76.
   - Geneva, roller-longdyad, sidecar-longdyad, parallelogram and roller-flank are unchanged (their smallest span is
     already dK, at 34.9-51.7).
   - It loosens a false positive; it does not change the rule.
2. **`c_fold_margin` also reads keys ending `_taken_deg`, `_held_deg` or `_deg`.**
   - **Effect on verified rows:** three go from watch to ok:
     - kneeless-roller 5.14;
     - this design 5.01 (fast; the verifier reads 5.293);
     - skin-normal-3r-pin-knee 5.03.
   - No other verified row changes.
3. **Price the GH-centre error in every claim (a tightening, so the user's call).** Report the share of taken poses
   whose cuff misfit stays within the 3 mm liner at a 3 mm offset, under one harness, for the knee and kneeless rows.
   - **Measured so far:**
     - kneeless-roller: 38.7 % without a knee, 66.6 % with a planar knee;
     - this design: p95 4.83 mm, knee 4.14 mm;
     - the lead and the other verified rows are unmeasured.

## Next

- A skeptic rules on `idle` and `fold_margin` for this design and its twin together.
- Then round 10 lens 3 picks its base on measured grounds:
  - this design has less contact than its twin (27.45 mm against 44.0 mm summed);
  - the twin has lower complexity (23.75 against 28) and a better held-out gap (24.59 against 25.34).

## Skeptic (2026-10-17, 02:31-02:45 UTC, git 14dd5d1)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and
changed no score. Local compute only (nice 15, OMP_NUM_THREADS=1, at most 2 processes); the farm was not used.

**Re-measured this session (models unchanged).**
- **Exact re-wear.** `tools/alignment_audit.py` `remeasure`, unchanged, with its output dir redirected to the
  scratchpad. CB_EXACT=1, Bench(110,360), 115 s. It reproduces frozen **21.11** / 1 mm 22.75 / 2 mm 33.15 / 3 mm
  130.78 and why = fold 90, parts 8, contact 5. Its `deep`, `frozen` and `parts_ib14` are identical to the auditor's
  `remeasure/kneeless-sidecar-knuckle-3r_bench.json`.
  - coord_spans: dK -0.6242..0 rad (**35.76 deg**). K.ang is constant at 128.5952.
- **Fast check.** `docs/concepts/models/kneeless-sidecar-knuckle-3r.py check <best_params>` reproduces row.fast:
  plain 15.63 / 1 mm 16.78 / 2 mm 20.32, min metal 0.32 mm, honest True. Bracket: knee_ptp 0.0, drift 0.0 mm, bend
  128.6 deg. Own span read: dK **36.64 deg** over 185 taken poses, with K at stop A on 110 and moved on 75.
- **GH offset for this design.** `tools/alignment_ghoff_twin.py` (new) is the twin's `redteam_gh` logic run with this
  design's hub-3 axis, with no wear. Output: `remeasure/kneeless-sidecar-knuckle-3r_ghoffset.json`.
  - At 3 mm, 38.7 % of the 470 claim-bench poses stay within the 3 mm liner with no knee, against **66.4 %** with a
    planar knee (one slide along the arm: 40.2 %).
  - At 5 mm: 17.7 % against 36.8 %.
  - This fills the audit's "not obtained" item.

**Rulings** (also in `docs/alignment/kneeless-sidecar-knuckle-3r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| fold_margin (watch) | **yes** | On file five times, all >= TH fold_min 5.0. Row `verification.added_checks.min_th_margin_deg` 5.293 / `min_th_margin_held_deg` 5.106 and `fast.min_th_margin_taken_deg` 5.01. verify `_v_bench_frozen.json` `th_margin` {min 5.293, lt5 0}, `_v_held_frozen.json` {5.106, lt5 0} and `_v_fitexact.json` {5.007, lt5 0}. The margin is in th, both sub-chains on forced poses (verifier lines 54-58). The tool's regex skips `*_deg` keys, and the dict `th_margin` gives no number. |
| idle (gamed) | **yes** | dK spans 35.76 deg on the bench (the auditor's exact file and the own exact re-wear, identical) and 36.34 held out. The own fast run gives 36.64. verify `extra.dK_taken_max_deg` is 35.77 / 36.34 and `sidecar.phi_max_taken` 34.1. All are far above TH idle_deg 2.0. K.ang belongs to the deleted knee: `KLDesign.knee` only places the pad, and K.ang is constant at 128.5952, with bracket drift 0.000 mm. No knee is a declared joint. M4 is absent. |
| reporting (watch) | no | The row's status is verified, but its verdict opens "SCREENED, a Pareto point", which is the tool's documented trigger. The record also still decides on the retired A1 gate. A stale record is not refuted by a number. |
| NEW-idle-check-false-positive (watch) | **yes** | Every fact is confirmed. It is a defect of `c_idle`, not a pattern of this design: its design-side numbers are ok (above). The base-choice concern is now moot, because the twin was cleared to watch by its skeptic (ledger, 02:18:29Z). Proposal 1 stays open as a tool action. |
| NEW-free-deletion (watch) | no | Measured for this design (above): 38.7 % within the liner without a knee, against 66.4 % with one, at 3 mm. The row's `gh_offset_redteam` (p95 4.83, knee 4.14) is confirmed. The no-knee share is design independent: it equals the twin's 0.387 because it depends only on the poses and the rest pose. **Correction:** the deletion is not free on the bench either. It needs b3 = 0, and the result is plain 21.11 against the lead's 18.91 (b3 0.345), held out 25.34 against 22.67, seed frozen 22.68. No number refutes the misfit. |
| NEW-contact-depth (watch) | no | `_probe.json` is confirmed: 5 poses, 27.45 mm summed, deepest -17.6 mm at (0,165,-45). Held out: 21 poses, 76.79 mm. **Caveat (c):** the comparison is not pose-matched. In `sidecar-longdyad-knuckle-3r_bench_perpose_claim.json` the lead does not evaluate either of this design's two deepest poses (ev false), and at (30,165,-60) the lead is in contact at -4.61 mm where this design takes the pose at 0.48 mm. Reach at elevation 165 is equal; what differs is how the arm is stopped. No number shows that the intrusion costs nothing. |
| NEW-ws-inband (watch) | no | Two independent files agree: verify `ws_inband` 0.8426 / 0.8049 (held out 0.8465 / 0.8282) and the probe. The lead on the same probe and bench is 0.8736 / 0.8409, with over14 0.1257 against 0.1566. Selection does not explain it: this design takes fewer poses at elevation 90-140 (34 against 37). The floor is in ROUNDS.md lines 1017-1020 and 1265. |
| T1 (watch) | no | The verifier's own audit confirms it: 0.48 / 0.51 / 0.67 mm taken, gap at 1 mm 22.75. Held out: 14 poses, lowest 0.025 mm, 28.41. This is the user's line (CLAUDE.md line 76: contact stays metal < 1 mm). The tool's 1-2 mm shell trigger is not met (12.04 < 15), but these are 0-1 mm poses. |
| G1 (watch) | no | Overhead floor hist {0-1: 1, 1-2: 5, 2-3: 2} of 8 taken; held out {3, 9, 5} of 17. The lead is {1, 4, 3}: one pose better at < 2 mm overhead, and worse overall (near3 178 against 130). The whole-bench shell (12.04 < 15) cannot see an 8-pose overhead subset, and the goal puts overhead first. |
| M5 (watch) | no | Missing measurement: there is no R17, dynamics or posture-sweep output for this id. The lead's static load sheet (`docs/research/sidecar_mechanism_redteam.md` row 5) covers another geometry, and its line 112 has R17 still pending. The stop-A share is confirmed from the verifier's definition (forced = abs(dK) > 1e-6): 227 / 367 and 534 / 853. The own fast run gives 110 / 185. |
| S1 (watch) | **yes** | (b) The documented S1 trigger is held out minus bench > +6 (TH held_watch). The measured value is **+4.23**; the lead on the same protocol is +3.76. (a) "The fit bench never shows the clash" is true only of fast labels. On the same 220 poses, the exact wear has E-L2 on 3 (`_v_fitexact.json`). That is 1.4 %, against 1.7 % on the claim bench and 1.5 % held out, so the sample is not skewed against the clash. Fast mode loses the same 35 poses under another label (fold 30 + skin 5, against exact fold 30 + parts 3 + contact 2, with reach 0.7812 in both), so the objective was charged for them. The claim counts every loss (8 / 17). |
| R1 (watch) | no | Row verdict, note and `verification.dominance_A1` still cite A1. The twin (21.07 / 24.59 / cx 23.75) is ahead on all three, so "Pareto point" is a stale label that flatters. The dashboard shows sweep_gap 20.24 with v_contact null. |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **The search's fast 2 mm objective cannot see the 1-2 mm shell.**
   - The CMA searched the 2 mm near-touch gap on Bench(60,160) **fast**: 20.32, min metal 0.32 mm (row `fast`, own
     check).
   - The verifier's exact wear of the **same 220 poses** (`verify/kneeless-sidecar-knuckle-3r_v_fitexact.json`) reads
     **32.75** at 2 mm (16 poses under 2 mm). That is 12.43 points the objective never saw. One taken pose sits at
     **0.00 mm**, at (135,135,-45).
   - The fast 1 mm and plain numbers are slightly pessimistic (16.78 against 15.15; 15.63 against 14.00). Only the 2 mm
     shell is blind.
   - **For the wearer:** the search optimised a 1-2 mm metric through a lens that misses most of that shell. Metal it
     "kept off" 2 mm may sit at 1-2 mm, which ALIGNMENT section 1.1 calls metal on the skin.
   - Under the 2026-10-17 ruling the 2 mm shell is not a gate, and the 1 mm objective (fast slightly pessimistic) stays.
     Measured on this design only: no other row has a fit-exact file.
   - **Reporting proposal** (no score moves): report the fit-bench exact near-touch beside any fast objective.
2. **The knee deletion's bench price is hidden in b3, and hub 3 pays it.**
   - Deleting the knee needs b3 = 0, which costs +2.20 bench and +2.67 held out against the lead.
   - Hub 3 is 0.555 in band (median 13.5 mm), against the lead's 0.599 (13.0 mm). That is under the round-9 spec gate's
     0.60.
   - The row's own `gate.spec_gate.passed` is false on five counts: fast 15.63 > 12.5, 2 mm 20.32 > 14.5, contact
     0.026 > 0.012, hub 3 0.551 < 0.60, and workspace in-band.
   - The audit reports only the workspace in-band count. ROUNDS.md line 1324 still offers this design as the round-10
     base "(cx 28, not gamed)".
3. **Two evidence gaps for proposal 3 and the contact-depth finding.**
   - The no-knee GH-offset share is design independent (0.387 for every rigid-bracket row under that harness), so it
     cannot rank one kneeless row against another. Only the knee-equivalent share moves with u3 (0.664 here, 0.666 for
     the twin).
   - Contact depth should be compared on pose-matched sets. The lead never evaluates this design's two deepest contact
     poses.

**Final verdict (ledger, skeptic entry 2026-10-17T02:39:47Z): WATCH.**
- Refuted with evidence: idle, fold_margin, NEW-idle-check-false-positive and S1.
- Upheld as watch: reporting, NEW-free-deletion, NEW-contact-depth, NEW-ws-inband, T1, G1, M5 and R1.
- The 'gamed' rested only on the tool's idle false positive. It no longer blocks the row.
- The row is still not a leader: plain 21.11 against 18.67 / 18.91, held out 25.34 against 23.73 / 22.67.
