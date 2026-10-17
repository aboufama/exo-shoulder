# Alignment audit: conecut-knee-knuckle-3r

This audit ran on 2026-10-17 from 17:27 to about 17:55 UTC. It was due because discovery round 12 (slice r12-B) screened
the design and its verifier verified it (commit d943974, 17:20).
- Ledger entry: 2026-10-17T17:48:48Z, by auditor, run `audit:conecut-knee-knuckle-3r`. Verdict **watch**. Tool
  reasons: dominance (+0.21 plain, -1.82 at 2 mm against the lead) and reporting (the row's verdict text still reads
  "SCREENED"; dashboard sweep best 12.5 sits 5.78 under the verified number). Plus 9 judgement findings, all watch.
- Checks: `docs/alignment/conecut-knee-knuckle-3r.json` (13 checks, tool 2026-10-17.4), with reference
  slipper-nose-knuckle-3r.
- Findings: `docs/alignment/conecut-knee-knuckle-3r.findings.json` (9, all watch).
- Re-wears, new in this audit. The models ran unchanged, locally, on 2 niced processes. The farm is past its budget
  line (CLAUDE.md (7)), so nothing went there.
  - `docs/alignment/remeasure/conecut-knee-knuckle-3r_bench.json` reproduces 18.28 exactly (247 s).
  - `docs/alignment/remeasure/conecut-knee-knuckle-3r_held.json` reproduces 22.38 exactly (552 s).
  - `docs/alignment/remeasure/conecut-knee-knuckle-3r_probe_bench.json` and `_probe_held.json` come from
    `tools/alignment_wear_probe_model.py`, on the unscored workspace.
- The verifier's knee and cuff placement check C5 (`docs/concepts/verify/conecut-knee-knuckle-3r.py place`) had never
  run. It ran here and is read-only.

## Verdict: WATCH (ledger verdict; the tool's checks alone also give watch)

- **The claim:** v_gap 18.28 (score 93.35), frozen exact Bench(110,360), verified 17:20 UTC. Held out it is 22.38.
  - Both numbers were reproduced to the digit by this audit's own re-wear.
  - Both per-pose dumps reproduce the claim.
- **No gamed reason, and no hard rule broken.**
  - 3 active DOF, 0 passive translations, O20 hubs, MR63ZZ knee pairs (stk 6.0).
  - The stop is on J3's own angle (verifier C1).
  - The `th` margin is 5.181 deg on the bench and 5.006 held out.
  - The continuity flood reads full 18.28 / knn 19.97.
- **What the number does not say:** this is a tie with the lead slipper-nose-knuckle-3r (18.49), not a better exo.
  - The 0.21 bench edge is the longer E strap's in-band dilution plus one pose with metal 0.26 mm off the skin. At
    equal strap the bench reads 18.67, behind the lead.
  - The 1.07 held-out edge is real in the plain score. It is built on 11 poses whose metal sits 0.76-3.68 mm off the
    skin, and it is gone at the 2 mm reading: 37.10 against 36.95.
  - Contact is deeper than the lead's, and the knee group now touches the hanging, rotated arm.
  - What is genuinely better: the knee never binds (window margin 11.4 mm against 0.33), and the knee link carries
    12 N per N m of J3 moment against 31.6.
- **Board risk (NEW-tie-headline):** the dashboard headline will show this row as the best 3-joint design at 93.35
  unless the lead writes the tie ruling. See finding 5.

## What the wearer gets (measured)

| | this row | lead slipper-nose | file |
|---|---|---|---|
| overhead reach (ws elev >= 140), bench / held | 8 / 28, 18 / 71 | 8 / 28, 18 / 71 | `remeasure/*_probe_bench.json`, row `frozen.held.overhead` |
| why overhead is lost (bench) | fold 14, J3 stop 3, contact 3 | fold 14, knee slide 4, contact 2 | probe `ws_overhead_why_not` |
| raised arm, ws elev 90-140 taken, bench / held | 39 / 85, 105 / 229 | 38 / 85, 96 / 229 | per-pose dumps |
| all ws taken, bench / held | 262 / 360, 659 / 952 | 261 / 360, 650 / 952 | per-pose dumps |
| taken poses with metal < 1 / 2 / 3 mm, bench | 3 / 33 / 105 | 3 / 30 / 100 | `remeasure/*_bench.json` deep |
| the same, held out | 13 / 71 / 218 | 14 / 67 / 200 | `remeasure/*_held.json` deep |
| min metal on taken poses, bench / held | 0.07 / 0.33 mm | 0.07 / 0.33 mm | deep |
| overhead p10 of per-pose min metal, bench / held | 1.83 / 1.50 mm | 1.82 / 1.50 mm | deep |
| contact poses, bench (summed depth, deepest) | 4 (20.24 mm, 8.93 mm at ws 15/165/-60) | 2 (14.75 mm, 9.01 mm) | `conecut-knee-knuckle-3r.json` contact_depth |
| contact poses, held | 14 (60.97 mm, 9.86 mm at ws 45/165/-30; 9 deeper than 3 mm) | 10 (46.12 mm, 9.05 mm) | same |
| clip in-band 2-14 (scored) / chain only | 0.9012 / 0.859 | 0.8955 / 0.869 | row `frozen.dilution`, verifier C4 |
| ws in-band, unscored, all / elev 90-140 (bench) | 0.868 / 0.832 (16.8 % > 14 mm, max 30.7 mm) | 0.856 / 0.800 (19.9 %) | probe |
| the same, held out | 0.871 / 0.848 (14.9 % > 14 mm, max 31.5 mm) | 0.861 / 0.822 (17.6 %) | probe |
| why overhead is lost, held | fold 36, J3 stop 10, contact 7 | - | `_probe_held.json` |
| knee angle over taken poses (window 25.2-154.8) | 59.3-107.1 deg | 86.2-152.2 deg | deep `K.ang` |
| knee-link force per N m about J3 | 12.0 N | 31.6 N | row `frozen.knee` |
| J3 stop | 2 mm 440C dowel; held margin 0.74 deg; 19 held poses stopped | none (knee slides: 9 bench, 32 held) | verifier C2 / C3 |
| springs | the lead's K clock spring, unchanged; R17 not run for this knee | R17 forward bound fails by 0.0008 deg at mu 0.15 | lead ledger M5 |
| fold margin `th`, bench / held | 5.181 / 5.006 deg | 5.181 / 5.006 deg | verifier extra.th_margin |
| m_sub with K at rest | not re-measured (same chain) | under 1 deg on 50 of 204 rest poses | `remeasure/slipper-nose-knuckle-3r_msub_rest_bench.json` |
| cuff twist | not measured (no CAD, no dynamics) | R17 nominal 4.04 deg | - |
| knee pad down the humerus at rest (C5, fast bench) | 96.0 mm (pin a 96.7, hub 3 13.4) | 78.8 mm (pin a 68.1) | `verify/conecut-knee-knuckle-3r.py place`, run here |

Paired near-touch gaps, from the two re-wears (this row against the lead):

| wear | plain | < 1 mm | < 2 mm | < 3 mm | band read 3-14 mm |
|---|---|---|---|---|---|
| bench | 18.28 / 18.49 (-0.21) | 19.92 / 20.12 (-0.20) | 34.84 / 33.02 (+1.82) | 86.16 / 83.15 (+3.01) | 18.34 / 18.64 |
| held | 22.38 / 23.45 (-1.07) | 25.23 / 26.54 (-1.31) | 37.10 / 36.95 (+0.15) | 83.12 / 79.25 (+3.87) | 22.55 / 23.60 |

## Findings

1. **T1, metal parked just past the contact line (watch, report-only).**
   - **Evidence, bench.** The only bench pose taken here and not by the lead is 203 (ws 0, 90, 45). Its lowest metal
     is 0.26 mm (wall / crown; 0.72 mm on the sampled metal). In the verifier's no-stop control it was a -0.03 mm
     contact. That one pose is worth 0.55 points, more than the whole 0.21 bench edge.
   - **Evidence, held out.** All 11 held poses taken here and not by the lead have metal at 0.76-3.68 mm, 6 of them
     under 2 mm. They are side and front raises at elev 75-90 with external rotation 45-90, plus pose 1099.
   - **Why it is not better.** At 2 mm the bench ranking flips (+1.82) and the held edge disappears (+0.15). At 3 mm
     this row is behind on both wears.
   - **Action.** Report the 2 mm column next to the claim. Under the user's ruling it is not a gate.
2. **NEW-strap-dilution (watch; proposed catalogue entry S6).**
   - **Evidence.** The longer E strap carries 164 samples per pose against 104. The equal-strap bench reads 18.67
     (0.18 behind the lead). Chain-only in-band is 0.859 against 0.869, hub 2 0.912 against 0.953, and the crank 0.801
     against 0.818.
   - **Why it is not better.** The share of metal above 14 mm barely moves (9.88 % against 10.44 %). The in-band share
     rises because new, well-placed strap metal was added, not because any out-of-band part moved into the band.
   - **Mitigation.** The held edge survives at equal strap (22.90 against 23.45).
   - **Action.** Rank ties at equal strap. See proposal C2.
3. **NEW-stop-relabel (watch; proposed T6).**
   - **How the score treats it.** A contact pose costs reach plus 100 / N_evaluated. A stopped pose costs reach only.
   - **Evidence.** The upper stop is inert on the exact bench. It cuts 3 overhead held poses (752 / 897 / 965) whose
     metal would be 2.0-3.4 mm in the skin. That is worth 0.34 held points: held would read 22.72, not 22.38, and the
     edge would shrink from 1.07 to about 0.73.
   - **Why it is only watch.** The dowel stands in for an E-strap-on-link-2 clash the chain already has (verifier C3),
     and the wearer is blocked either way. So it is honest hardware, but the score prefers it to touching by a margin
     the wearer does not get.
   - **Action.** Proposal C3.
4. **T5, deeper contact (watch).**
   - **Evidence, bench.** 20.24 mm over 4 poses against the lead's 14.75 mm over 2. That is x1.37, under the tool's
     margin against the lead, but x3.25 / +14.01 mm against sidecar-longdyad, the tool's default reference.
   - **Evidence, held out.** 60.97 mm over 14 poses, against 46.12 mm over 10.
   - **New contacts.** Hub 2 at -4.28 mm (205, elev 105) and link 2 at -1.23 mm (316). Held out, 835 (90, 15, -150) at
     -3.55 mm and 978 (120, 15, -165) at -1.33 mm: the arm pad and the knee link on the hanging, rotated arm, poses
     the lead takes clear at 0.81 / 0.62 mm.
   - **Action.** Size the knee on the held low-elevation, extreme-rotation poses, as the proposer's own next step 1
     says.
5. **NEW-tie-headline (watch).**
   - **Evidence.** The board headline ("Best 3-joint design so far", `docs/dashboard/simple/index.html` 234-236) is
     the first verified row with 3 or fewer joints that has no `tie` ruling. `docs/dashboard/data/morphs.json`
     (17:28) carries this row as verified 18.28 with no ruling. So the headline moves to it at 93.35 against 93.28.
   - **Why it is not better.** The proposer and the verifier both measured a tie: CI90 [-1.05, +0.80], P(better)
     0.60.
   - **Action, for the lead.** After the skeptic rules, set the row's `leader_ruling` to
     `tie: slipper-nose-knuckle-3r | ledger <skeptic time> | ...` (docs/OPERATIONS.md section 4). Do not report a new
     leader to the user.
6. **M5, spring and cuff (watch, carried).** The K spring and the drive are the lead's, unchanged; the re-wear's dK,
   a1e and m_sub spans equal the lead's. The lead's R17 forward bound fails by 0.0008 deg at mu 0.15. The new knee's
   cuff twist is unmeasured.
7. **G4, near-singular K at rest (watch, carried).** This is the lead's m_sub at rest (under 1 deg on 50 rest poses).
   The chain is identical.
8. **T3, fold margin (watch, inherited).**
   - **Clean.** The stop is on J3's own angle (C1 residual 0.015 deg).
   - **Inherited.** The held `th` margin is 5.006 deg, 0.006 above the line, on the lead's K law. A +-0.3 deg K-phase
     build error crosses it.
9. **NEW-ws-inband (watch, carried, slightly better than the lead).** On raised-arm workspace poses (elev 90-140),
   16.8 % of the metal is above 14 mm (max 30.7 mm), against 19.9 % for the lead. The scored in-band does not see it.

### Patterns walked and found absent

- **T2.** The band edge costs 0.06 points (lead 0.15).
- **T4.**
  - The knee window minimum is held at the rule's 25.22 deg by clamp, and the taken knee angle stays 34 deg or more
    inside it.
  - lE 97.14 sits 0.86 mm under the coarse LHS box edge (98). The CMA searched past it to 101, and the clamp is 110,
    so it is not a box edge.
  - The stop's 0.74 deg held margin is a robustness note: a 3 mm GH error moves phi by about 2 deg (proposer), which
    can only cost reach, never add contact.
- **S1.** Held minus bench is +4.10.
- **S2.** Part-weighted in-band is 0.925, above the sample-weighted 0.901. L1a carries 8 samples, the same as the lead.
- **S3.** The dowel sits inside the hub-3 stack, with no skin-facing metal.
- **S5.** The full flood equals static; knn costs 1.69 (lead 1.67).
- **M1, M2.** None; this is the catalogue dowel ISO 8734 2 m6, at O20.
- **M3.** The knee against E is checked by the model's parts check (329 poses fail at stk 4.85, 0 at 6.0).
  - The groove at r 6.45-8.55 leaves a 0.95 mm wall to the MR117 seat (r 5.5) over the seat's first 0.5 mm (LV L1
    3.65 to the groove floor 4.15, `pipeline/conformal/param_cad/param_build.py` line 35). This is a CAD-stage note,
    not a score issue.
- **M4.** The knee moves 46.7 deg and the drive 45.6 deg.
- **P1, P2.** The search used the fast bench only. The row best is the two-sided CMA's objective argmin, and it was
  picked over the one-sided CMA's by the fast plain gap (12.50 against 13.44).
- **P3, R3.** It is the best of 3 worn configurations (bench 18.28 / 18.36 / 18.84, held 22.38 / 22.79 / 23.90). The
  spread is on file in the concept doc's column table.
- **P4.** No bench or judge file changed in the row's 4 commits.
- **R2, R4.** The dashboard v_gap equals the verifier's.
- **G5, G6.** Complexity recomputes to 18.5, and the stop adds no DOF.

## Numbers I could not get, and why

- The cuff twist and R17 for the re-centred knee: there is no CAD and no dynamics run for this row.
- m_sub at rest for this row: the lead's script was not re-run, because the chain is identical (same spans).
- Per-pose q3' near the stops: the re-wear records only the range ([-109.20, 116.10] bench, [-111.16, 119.44] held).
  So I cannot count how many taken poses sit within 2 deg of a stop.
- The 2 mm and 3 mm readings of the one-sided CMA column (18.84 / 23.90): it was not re-worn.
- The farm was not used. It is past its budget line, so everything ran on 2 local niced processes.

## Proposals (measurement or reporting changes; not applied, none feeds the verdict)

- **C1. Tool defect: near-touch and dominance read a control file.** Before this audit's re-wear existed,
  `_near_numbers` in `tools/alignment_audit.py` read the newest non-held verifier file with an audit block. That was
  the no-stop control (`_v_bench_nostop.json`, plain 19.38), not the claim (18.28).
  - Effect: near_touch reported a 10.02-point shell instead of 16.56, and dominance reported ok (-0.89 plain) instead
    of watch (+0.21 plain, -1.82 at 2 mm).
  - Proposal: apply `contact_depth`'s guard, which uses a file only if its own gap reproduces the claim to 0.05.
  - Effect on rows: any row whose verifier folder holds a control column. This one moves ok to watch on dominance.
- **C2. Catalogue entry S6, in-band dilution.**
  - Looks like: in-band rises when a member is lengthened or added in band, with the out-of-band parts unchanged.
  - Detect: the chain-only in-band and the equal-sample-count reweighting (verifier C4) next to every claim that
    changes a member's length. A tie is ranked at equal strap.
  - Effect on this row: bench 18.28 -> 18.67, which ranks it behind the lead. Held is 22.90 against 23.45. Other rows
    are not measured.
- **C3. Catalogue entry T6, stop relabel.**
  - Looks like: a hard stop, or any "not taken" label, removes a would-be contact pose from both the contact numerator
    and denominator. It then costs reach only, while a contact costs reach plus contact.
  - Detect: re-evaluate the stopped poses without the stop, on the worn shape (verifier C3), and report the gap with
    those contacts counted.
  - Effect on this row: held 22.38 -> 22.72 (3 upper-stop poses). Bench: no change (its stopped poses are parts
    clashes). Rows with knee windows or J2 stops are not measured.
- **C4. Headline needs a ruling when the paired CI spans 0.** The board takes the headline only when the paired
  bench CI90 excludes 0, or after a lead ruling. Effect: this row stays off the headline until the ruling. The lead's
  headline is unchanged.

## Skeptic (2026-10-17, 17:50-17:58 UTC)

Ledger entry 2026-10-17T17:57:13Z, by skeptic, run `skeptic:conecut-knee-knuckle-3r`.

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence. 10 of 11
reasons are upheld and 1 is refuted. Rulings: `docs/alignment/conecut-knee-knuckle-3r.rulings.json`.

**How I checked.**
- I re-derived every number from the raw per-pose dumps with my own scripts. I did not import the audit tool.
- New tool: `tools/alignment_skeptic_why_labels.py`. It leaves the models unchanged and reads kinematic labels only,
  under the frozen protocol. Its fit gaps, 13.0 and 12.5, reproduce both fast claims.
- New evidence: `docs/alignment/remeasure/conecut-knee-knuckle-3r_skeptic_why_held.json`.
- Local only: niced, OMP_NUM_THREADS=1, 2 processes, about 15 s each. The farm was not used.

### Rulings

1. **dominance: upheld.**
   - Re-derived from the dumps: plain 18.28 against 18.49, and at 2 mm 34.84 against 33.02.
   - Both sides use the same harness: exact, frozen protocol, Bench(110,360).
   - The c_dominance rule gives watch, capped (A1 is retired). This is report-only.
2. **reporting: upheld.**
   - The row's verdict begins "SCREENED" while its status is verified.
   - morphs.json (17:43) has sweep_gap 12.5 against v_gap 18.28, 5.78 apart. 12.5 reads as score 95.45.
3. **T1: upheld.**
   - Pose 203: cmin 0.263 mm, min_mm 0.716 mm. The lead does not evaluate it.
   - Against the lead, 203 is worth 0.29, not 0.55 (0.55 is the value against the no-stop control). Without it the
     bench reads 18.57, behind the lead's 18.49, so the conclusion stands.
   - Held out: the 11 new poses sit at 0.758-3.68 mm, 6 of them under 2 mm.
   - Correction: the held 3 mm column recomputes to 82.52 / 79.04 (+3.48), not 83.12 / 79.25 (+3.87).
4. **NEW-strap-dilution: upheld.**
   - With the strap reweighted to the lead's count (verifier C4 rule), the bench reads 18.67 and the held wear 22.90.
   - Chain-only in-band (no E, boss, pad or knee) is 0.859 against 0.869.
   - Excluding only E, it is 0.8855 against 0.8864. The knee group gained in band, and hub 2 and the crank lost.
5. **NEW-stop-relabel: REFUTED, on apples to apples and wearer cost.**
   - Under the frozen protocol the lead labels held 752, 897 and 965 'slide'. The same goes for the lower-stop poses
     392 and 530. 'Slide' is the lead's knee-window stop (CLAUDE.md (5)). The lead's slide count is 32, equal to its
     verifier's.
   - The lead's dump has ev false at all five poses, so its 23.45 also charges them as reach only.
   - Charging them as contacts here (22.72) but not on the lead is a one-sided adjustment. Like for like, the held edge
     at these poses is 0.
   - The wearer meets a hard stop at these poses in both designs.
   - Correction to the count: J3MIN also cuts 392 and 530 (q3' -112.49 / -114.49). Both pass the parts check
     (clearance 1.31 mm, equal to the taken minimum 1.3146) and would be contacts at -1.11 / -9.68 mm. A one-sided T6
     count is therefore 5 poses (+0.56), not 3.
6. **T5: upheld.**
   - Bench: 4 contact poses, 20.24 mm summed. Against DEPTH_REF sidecar-longdyad (6.23 mm) that is x3.25 and +14.01 mm,
     past both the 2x and the 5 mm lines.
   - Held out: 14 poses, 60.97 mm, against the lead's 10 and 46.12 mm.
   - New contacts on the hanging, rotated arm: 835 (-3.55 mm) and 978 (-1.33 mm), where the lead's metal clears the
     skin by 0.81 / 0.62 mm.
7. **NEW-tie-headline: upheld, and live now.**
   - My copy of the page's headline rule, run on morphs.json at HEAD, picks this row (18.28, no ruling).
   - Citation fix: "NOT a leader" is in the row's `note`. `verification.verdict` does not exist.
8. **M5: upheld.** No judge or pipeline file mentions conecut. The knee's K.psi and K.ang spans are new, so the cuff
   path is unmeasured.
9. **G4: upheld.** The coordinate spans of dK, a1e and msub equal the lead's. The lead's m_sub at rest is under 1 deg
   on 50 of 204 rest poses.
10. **T3: upheld.** The held th_margin minimum is 5.006 deg with 0 poses under 5. The C1 residual is 0.015 deg.
11. **NEW-ws-inband: upheld.** At elevation 90-140, 16.8 % of the metal is above 14 mm on the bench and 14.9 % held
    out, with a maximum of 31.46 mm.

### Missed by the auditor (for the next audit; not in this verdict)

- **The stop count is short.** The held relabel count is 5, not 3. 392 and 530 are lower-stop poses that pass the
  parts check and would be contacts, at -1.11 and -9.68 mm. The audit called every lower-stop pose a parts clash, but
  that holds on the bench only.
- **Proposal C3 (T6) has to be symmetric.** Every 'not evaluated' kinematic label removes a pose from the contact
  denominator in the same way: fold, the knee-window 'slide' and 'j3stop'. Applying T6 to one row's dowel and not to
  the reference's knee window penalises only one side. Its measured effect therefore needs the reference's slide poses
  re-evaluated without the stop too (32 held on the lead).
- **Two corrections.** The held 3 mm near-touch reads +3.48, not +3.87. Pose 203 is worth 0.29 against the lead, not
  0.55. Neither changes a conclusion.

**Final verdict: WATCH.**
