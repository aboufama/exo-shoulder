# Skeptic: take_bound_3dof ("95 at 3 DOF is measured out of reach at the legal seats")

Alignment skeptic, 2026-10-18 ~12:35-13:10 UTC, branch claude/exciting-albattani-94w8cp. Claim under test:
docs/research/take_bound_3dof.md (+ .json / .py; commits f128408, 9dbac97, 0b784e9, 66a9c1e). Read only: no bench,
judge, row or claim file changed; nothing searched, selected or tuned on held-out poses. Every number below is quoted
from a cited file or recomputed from one (no new bench runs: 4 other jobs held the 4 cores; the one quantity I needed,
the 5.0 vs 5.5 margin effect on the oracle, reads straight off the oracle's own per-pose file).

## Verdict: UPHELD-WITH-CORRECTIONS

No 3-joint design or bound on file reaches gap 13.75. The core argument for the acromion-top knuckle family holds: no
real K law has been measured above 272 workspace takes, and 272 takes cost 14.44 even with zero contact and full
in-band. But the blocker overstates its scope ("back-of-shoulder" seats were not covered by the table), misstates the
3-joint ceiling (~17.2 is not a ceiling), and calls the free-K oracle a bound on "ANY K law" and on the sensed-K 4th
joint, which it is not. All three need fixing before the user sees it. A fair blocker also lists the one option that
needs no rule change: measure the untested posteromedial J1 seats first.

## Findings

### F1 (coverage, major): the posteromedial back-of-shoulder seats are not in the table

- bvec convention (tools/concept_kit.py line 49): az 0 posterior, 90 lateral, 180 anterior. Every table row except the
  cap pole puts J1 at bvec(95-102, 62-68), which is lateral and high: the acromion top. The table's "Back of the shoulder"
  row is the lead's acromion-top seat (az 95.4 / el 67.9) under another name. The cap pole is bvec(43.2, 59.9), posterolateral
  and high. No row has J1 at az < 40 or el < 55.
- That untested region is where the kinematics are best. docs/research/fold_ceiling/kin_ceiling.json `curves`: the best
  window at W 80 (the lead's drive gives W 81.8) sits at seat1 bvec(-52.5, 17.5), posteromedial and low. It holds
  0.994 of the 360 bench poses (0.966 held out). At W 86.3 it holds 1.00 at bvec(-45, 17.5). kin_ceiling.py line 48
  counts az -90..90 / el -20..80 as "back of the shoulder", which is inside ruling 4. reach_attribution section 6
  (quoted at ROUNDS.md line 723) gives the plain 3R at J1 bvec(-5..3, 0) a headroom of 0.942.
- What has been measured there, all of it older and none of it a knuckle at az <= 0:
  - zc-frontier streams from (0, 45) / (30, 60): P0 57.92, reach 0.85 at in-band 0.42 (ROUNDS.md lines 718-719, 1056).
  - The pin-knee posterior J1 line: 122.45, in-band 0.17-0.25, contact 0.23-0.29, with no per-part split (lines 720,
    1057).
  - Knuckle re-seats at az 75 / 55 / 35 near the lead's elevation: fast 20.29 / 61.21 / 73.21 against the control's
    10.30 (round9_ideation.md line 72). These were short refits by the proposer.
  - ROUNDS.md lines 726 and 1061 say it in so many words: "A knuckle at a back seat has never been measured". The 6
    seat cells kin_ceiling picks (az -45..-67, el 10-17.5) have never had metal.
- The round-9 judge closed the lever on the grounds that "the seat only slides a window whose top is the drive stroke
  (109.5)". fold_ceiling section 2 (written later, 2026-10-17) refutes that reasoning at these seats: a window of the
  drive's width holds about 99 %.
- Plausibility that this region beats 18.28: low. It is still unmeasured. Both families measured at back seats lost
  the band (in-band 0.17-0.42), which is the same wall as the cap pole's R3. But 95 at 306 takes (the zc stream's 0.85)
  needs only in-band >= 0.81, and nothing at these seats has been worn with today's tools (60-deg ramps, corridor route,
  knuckle parking).
- **Correction:** add a row "Back of the shoulder, posteromedial (az <= 40, el <= 50), any realisation", with
  kinematic 0.94-0.99, best metal P0 57.92 (in-band 0.42), knuckle "unmeasured", 95 reachable "unmeasured (nearest
  evidence: in-band collapses)". Rename the current "Back" rows "acromion top (lead's seat)". Section 6 and the blocker
  headline must say "at the seats measured" rather than "at the back-of-shoulder and acromion-top seats".

### F2 (the bound logic, major): the free-K oracle bounds takes at fixed metal, stretched side only, at 5.5 deg

1. **It bounds takes, not the gap.** The doc says the k33 oracle (17.25 connected, 280 takes, about 21 contacts)
   "bounds every 3-joint K law at these seats (and the sensed-K 4th joint)" ([R2]). The sensed-K 4th joint at the same
   k33 seats, freek-oracle-route-knuckle-4r, verified at 16.20 with the same 280 takes (rows/freek-oracle-route-knuckle-4r.json
   `v_gap` 16.2, `v_reach` 0.7778, `v_contact` 0.0375). It beats its own "bound" by 1.05 because link routing and a J3
   dowel cut the contacts from about 21 to 15. The polish then cut them to about 7 (contact 0.0179). The oracle picks K
   per pose on one fixed kit metal, so it bounds the TAKES at that seat and dyad. At 277-280 takes the zero-contact
   floor is 13.06-12.22, BELOW 13.75. The oracle therefore does not exclude 95. What excludes it for 3 joints is the
   separate fact that no real K law closes more than 272 (law cap [d], ~40 ghost cells at 269-271 [f], and the
   lobe, RSSR, desmo, dog-ring, sidecar and roller drives all measured). That is strong evidence, not a proof. The
   doc's own [R1] has the right structure. Section 6's "free per-pose K (the ceiling of ANY K law) whose extra poses go
   into the skin" folds the two arguments into one and overstates both.
2. **Stretched side only.** freek-oracle-route-knuckle-4r.md lines 50 and 75: the oracle is offered only to stretched
   poses (th > th_hi). State-A and folded-side poses are not offered ("a fully free K could also open there - not covered
   by this bound"). In cell L0b, 19 overhead "fold" poses (plane 0-45, elev 90-165; poses 181, 202-210, 229-236,
   259-265, 287, 292) carry no oracle samples at all (cell_L0b_perpose.json `res`). fold_ceiling.md lines 141-142 bound
   this: hub 2 clears only 4 of the 15 folded poses at the lead's level. A two-sided law could add at most about 4
   takes. That does not change the verdict, but "ANY K law" must be qualified.
3. **The fold margin read is 5.5, not 5.0.** Cell L0b and the k33 oracle run with CB_FOLD_MARGIN 5.5 (cell_L0b.json
   `fold_margin` 5.5; freek md line 49). The user's rule and the lead's verified reading are 5.0 (tools/concept_kit.py
   line 30; the lead's min th margin is 5.181, `extra.th_margin`). In L0b at least one refused pose, 354 at th 127.81,
   lies inside the 5.0 window: a1max 76.044 + a2 57.218 - 5.0 = 128.26 against 127.76 at 5.5. A "bound" read under a
   stricter rule than the design it bounds is not an upper bound. The effect is about 1 pose (about 0.3 gap points),
   so the verdict stands. The freek 4-joint numbers (16.20, 15.40) are also read at 5.5, which slightly favours the
   3-joint lead in the comparison.

### F3 (the ceiling arithmetic, major for the user text): "~17.2 = the 3-joint ceiling" is wrong

- "Clearing all 4 of its contacts without a new take would give 17.22". The lead's 4 contacts are workspace poses that
  close kinematically (205, 237, 264, 316; `contacts` in conecut-knee-knuckle-3r_v_bench_frozen.json). Clearing them
  turns them into takes: 266 takes give 100 (0.90 - 266/360) = **16.11** (score 94.14), not 17.22. 17.22 is only the
  zero-contact floor at 262 takes, which would need those poses refused by a stop.
- The ceiling the evidence supports is a range, not 17.2:
  - The best idealised 3-joint measurement is 16.91 (269 takes, ghost drive; proximal-j3 `/audit/at_knee_rule`).
    desmo-vrocker's ghost is 17.23 (rows/desmo-vrocker-longdyad-knuckle-3r.json).
  - The take-count floor is **14.44** (272 takes, the law cap, at zero contact and full in-band) to 14.72 (271
    ghosts). That is score **94.65-94.75**.
- So "3 joints top out around 93.7" understates 3 joints by about 1 score point. Correct text: "even with every
  contact cleared and full in-band, the most takes any real 3-joint K law has reached (272) leaves 14.4 (score ~94.7),
  short of 95. The best idealised design measured is 16.9 (93.9)." The 3-joint upper estimate (94.7) sits above the
  4-joint verified 94.11 and the polished 94.40. That belongs in the user's comparison.

### F4 (arithmetic): correct

gap_of (tools/concept_bench.py line 53) = 100 [(0.90 - ib14)+ + (0.95 - follow)+ + (0.90 - reach)+] + 100 contact.
Contact counts over every pose with a result, so 4 contacts / 376 gives 0.0106. One take is worth 0.278; a contact
turned into a take is worth 0.278 + 0.266 = 0.54 (as stated). 13.75 needs 274.5, so 275 takes at zero contact (ib14 >=
0.90, follow >= 0.95), or 278.3, so 279 takes at the lead's 0.0106 (as stated). Lead: 262 takes, 100 x 0.1722 + 1.06 =
18.28 (verified file `/frozen`). The "takes 95 needs" column checks out: 279 metal, 281 ghost (16.91 - 15.28 = 1.63),
292 oracle (17.69 - 13.06 = 4.63), cap 3R > 360. Score = 100 - 0.3636 gap (18.28 -> 93.35).

### F5 (4-joint quotes): correct, with one framing note

The quotes match their sources:
- freek: 16.20 verified (280 takes, contact 0.0375, cx 33.25) and held 21.89 (row `held_out.cellB_q3max86.static`).
- freek pick1: 15.40 bench, held 20.50 on the CAD shape and 20.24 on the env fit (FINDINGS lines 3518-3521).
- proxtrack: 14.02 plain / 14.40 gate, held 18.01, 285 takes, 13 contacts, cx 52.5, row status "screened", ledger no
  entry. The verifier's re-measure is in flight; its uncommitted
  docs/concepts/verify/proxtrack-relay-knuckle-4r-remeasure_bench.json reproduces 14.02 / 285 / 13. That is a
  reproduction, not a verdict.

Framing:
- Compare verified with verified: 18.28 against 16.20, a gain of 2.08 gap points (0.76 score points) for the 4th
  joint. The 15.40 polish has no 3-joint counterpart: conecut was never env-polished, and the predecessor slipper-nose
  polish gained < 1 (FINDINGS line 2546).
- Say what each "4th joint" physically is:
  - freek: the knuckle angle K as a sensed joint.
  - proxtrack: an unpowered, constant-force-spring carriage on an arm-fixed circular track that the chain pushes off its
    dowel (proxtrack md lines 25-31).
  - The project counts both as joints, under the user's rulings (2026-10-17: "a joint in the shoulder chain is a joint";
    REQUIREMENTS line 63: elements that need power or position measurement count). The user should see the hardware,
    not just the word "joint".

### F6 (measurement artefacts that might hold 3 joints back): none found beyond F2.3

- The workspace set matches R16 as written: all 360 bench workspace poses lie inside pack_envelope.py's `functional()`
  limits (checked: 360 / 360).
- Contact is metal < 0 mm, as ruled. The near-touch readings are not in the gap.
- Sample density does not move the lead (docs/alignment/sample_density.md: 18.28 -> 18.28).
- The fold margin is 5.0 for the lead; F2.3 covers the oracle exception.
- The lead's 6 J3-stop losses are E-L2 part collisions with metal -1 to -12.6 mm in the skin (`c3_stopped`), so they
  are not a rule artefact.
- One protocol cost, not an artefact: the frozen-shape transfer from the fit bench is 12.50 fast (reach 0.775,
  contact 0) to 18.28 on the claim bench. It falls on every design alike, and fitting on the claim bench would be
  in-sample.

### F7 (other 3-joint families): no measured row beats 18.28; about 40 never modelled

Every 3-active row in rows/*.json and catalogue.json was checked:
- Knuckle variants in the acromion-top family: sidecar 18.91-20.08, inband-rssr 18.87, desmo-vrocker ghost 17.23
  (dead at gate 3), dogring refuted.
- Older families at 22-125: raglan, j3-neck, dwell-fourbar, split-knuckle-twosided (34.18, the two-sided K attempt),
  and the scheduled relays refuted by continuity.
- The table's family choice is fair for measured families.
- About 40 catalogue concepts sit at "ideated" or "modelling-interrupted" (rolling-cone, SPM / tripod, telescopes and
  others) and were never modelled. Nothing says they would win. The blocker should say "every family measured", not
  "every family".

### F8 (fairness of the blocker text)

- The headline "measured out of reach at the back-of-shoulder and acromion-top seats" overstates the scope (F1).
- It needs "and no 4-joint design reaches 95 either" in the first line, not in option 1's last sentence.
- The "ceiling ~17.2 / 93.7" figure is wrong (F3).
- It omits the option that needs no rule change: measure the posteromedial seats with the lead family. Because the
  user is asked to relax something, leaving out the no-relaxation option is steering.
- Costs are mostly stated. Add the final-product cost the user named: one more joint to cable-drive and track.
- Uncertainty is stated, but the oracle and the "ANY K law" wording claim more certainty than the data gives (F2).

## Corrections the lead must make before sending

1. Scope: "at the J1 seats measured (acromion top, cap pole)", not "back-of-shoulder and acromion-top". Rename the
   "Back" rows "acromion top (lead's seat)" and add the posteromedial row (F1).
2. Replace "~17.2 (93.7) = the 3-joint ceiling" with "upper estimate 14.4-14.7 (score ~94.7) from the take count; best
   idealised measurement 16.9 (93.9)". Fix "clearing the 4 contacts" to 16.11 (F3).
3. Recast the oracle as a take bound at fixed metal, stretched side only, read at 5.5. Drop "bounds the sensed-K 4th
   joint": freek verified 16.20 below its 17.25. Rest the 3-joint "no" on the law cap of 272 (F2).
4. State in the first line that no 4-joint design reaches 95 either. Compare verified with verified (2.08 gap / 0.76
   score points).
5. Add option 0, measure the posteromedial seats first (no rule change), with its low odds stated. Name the physical
   4th element in option 1.

## Corrected blocker (plain language, ~120 words)

"Needs your call. Our best 3-joint design scores 93.4 (target 95). Every 3-joint design we have measured at your
allowed J1 seats falls short. Even with perfect contact clearance, the most poses any real 3-joint chain has reached
caps it near 94.7. What stops it is metal touching skin, not geometry. One legal region is untested: J1 low on the back
of the shoulder. The odds there are low, because earlier designs could not stay within 1 cm. No 4-joint design reaches
95 either. Options: (1) test that region first, with no rule change; (2) allow a 4th joint (a tracked knuckle or a
sprung cuff carriage): best verified 94.1, polished 94.4, about double the complexity and skin-contact depth, plus one
more joint to drive; (3) allow front/clavicle J1 seats: unmeasured; (4) accept ~93-94 with 3 joints."
