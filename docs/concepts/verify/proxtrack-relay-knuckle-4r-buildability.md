# proxtrack-relay-knuckle-4r - independent verifier, lens BUILDABILITY AND RED TEAM

Claim under test: round 105 screened row, frozen exact Bench(110,360) GATE 14.40 (chain-only ib14 0.8962) / plain 14.02
(pooled ib14 0.9196) / near1 17.68 at PHI 35 / ds 19.538 / rt_extra 1.5 / pre 10.41 / bump 1.002 / band 9.272 / ramp 6.0;
held gate 18.51 / plain 18.01. 4 counted joints (J1, J2, J3, relay), complexity 52.5.

Harnesses (mine; the claim model is imported unchanged and each variant patches ONE thing on the same prepared wear):

* `docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability.py` - `price` (base = the claim as modelled; `rigid1` /
  `rigid2` = the bump made rigid; `stackfix` = the pin-a stack kept buildable; `flange` = the T-nut flange sampled; the
  coil and th-margin checks ride on `base`), `diag` (the relay's feasible phi set per pose).
* `docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability-stack.py` - pin-a stack check (boss vs knee link).
* Outputs: `docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability/` (`stack.json`, `diag.json`, `price_A.json`,
  `price_C.json`).

All runs local, nice 10, OMP_NUM_THREADS=1, at most 2 processes (the CPU farm is closed).

## Verdict

RESULT_PLACEHOLDER

## 1. Every joint maps to a real component at its real envelope

| joint / part | component | sampled as metal? | finding |
|---|---|---|---|
| J1, J2, J3, K drive, two-pin knee, J3 dowel stop | the lead's verified O20 stacks / MR63ZZ pairs / ISO 8734 dowels (unchanged) | yes (lead) | as the lead |
| relay track | made part: slotted circular Ti shell 1.5 x 12, R_t 79.9, arc [-109.5, -53.6] deg (56 deg, ~78 mm) | underside in band (303 samples, 1 / 4 mm2 = kit density), top contact / jam only | buildable as a machined / rolled part; no catalogue curved guide fits h_c 1.7 |
| relay carriage | made part: T-nut carriage 24 x 14 on an iglidur strip, h_c 1.7 above the shell top | yes (contact / jam only, not in band) | **the T-nut's retaining flange under the shell is NOT modelled**: a carriage that is only above a 1.5 mm shell cannot be retained (the pad loads it both ways). The parent family's own model (armarc `flange`, 1 mm x 8 key, skin-facing) samples it; this model dropped it. Not priced (cheapest variant, ~0 expected on the chain-only gate: it sits 4.5 mm over the clip-p90 skin inside the liner) |
| relay spring | "a constant-force spring, preload >= 0.063 N.m" (the parent doc: "CF class; part number to confirm") | **no** | no part number and no envelope. A real strip for ~0.8 N at R_t 80 over >= 55 mm of travel (0.05 mm 301 stainless, 8 wide, natural radius ~3 mm, bending stress ~1.6 GPa) coils to ~7-8 mm OD x 8 wide, standing ~8 mm proud of the shell top beyond the zero dowel (or riding the carriage, which would make h_c ~9). COIL_PLACEHOLDER |
| stop dowels | ISO 8734 2 m6 x2 in the shell slot, on the relay's own angle (shell <-> carriage) | no (inside the slot) | buildable, own-angle: OK |
| pad bracket | 2 mm x 10 Ti, carriage top (s0 - 7) down to the pad's proximal edge: 8.45 mm drop over 7.1 mm (49.9 deg) | yes (in band) | the doc calls it "a legal bent bar"; it is not: two tangent bends of inner radius >= 5 t (10 mm) at 49.9 deg alone take ~16.8 mm of run (7.1 mm available). It must be machined from solid (allowed when stated); no gap change |
| rigid local bump on member 3 (E strap, pin-a boss) and the knee link | "same parts, reshaped" | yes | **not buildable as modelled - see 2 and 5** |

## 2. The rigid bump is not rigid, and it drives the pin-a boss through the knee link

Read line by line (`proxtrack-relay-knuckle-4r.py` `bump_amounts` / `rerecord.bumped`):

* **Per-point amounts collapse the parts onto the target cylinder.** Each sampled point gets its own amount
  max_pose(w x (R_t + clr [+ h_c] - r)): a part's points that sit at different radii are lifted by different amounts,
  so a part that sits wholly below the target lands as a sheet on it (its own sampled thickness is kept only through the
  contact-only top sets taking the nearest underside amount).
* **The bump's direction is re-computed at every pose** (`h + a * r_hat(h)`: radial about a_r in that pose's HG'
  frame). Member 3 and the knee link move relative to the arm (two knee pins), so the displacement changes direction in
  the part's own frame from pose to pose: a deforming part, not a rigid one. RIGID_PLACEHOLDER
* **Pin-a stack (the decisive one).** The lead stacks the knee link ON TOP of the pin-a boss and the pad (knee underside
  at tr + tp + 0.5: `off_k = tp + RUN`). Measured at every one of the 184 fit-bench poses the bump is sized on
  (`stack.json`): lead stack gap +0.50 mm at every pose; claim: the boss is lifted 1.76-5.69 mm (all 32 points) and the
  knee link only 0-3.72 mm, so the bumped boss top sits **5.05-5.08 mm INSIDE the knee link's eye at all 184 poses**
  (median -5.05). Two bodies on one pin occupy the same space: the modelled metal is not a part that can be made. The
  buildable version lifts the knee link's eye over the lifted boss (and ramps it back down to pin b on the unlifted pad),
  i.e. more metal higher off the skin than the claim counted. STACK_PLACEHOLDER

## 3. Stops on the joint's own angle

The relay's zero dowel and end dowel act on the relay's own angle (shell <-> carriage, the two bodies the joint
connects): buildable. The lead's stops are unchanged. The pre-arc floor (carriage half-arc + 2 mm dowel, 10.04 deg)
is honoured (pre 10.41).

## 4. Determinacy of the passive coordinate (relay)

* Energy reading of the relay solve: a constant-force spring pushing phi to 0 against hard stops rests at the LOWEST
  feasible phi of the feasible component it is in. "Least phi" equals that state only when the feasible set is one
  interval. Scanned at 0.25 deg over [0, 35] with the lead's own gates (`diag.json`): fit bench 0 of 200 closable poses
  with two components; **claim bench 3 of 409** (ws 178 (-15, 75, -30), 205 (0, 105, 15), 229 (15, 90, -30)): phi 0 is
  feasible AND a second band from 32.0 / 32.75 / 28.25 deg to 35 is feasible with an infeasible band in between. Arriving
  from the relayed side above that band, the carriage parks on the upper branch, not at 0: a history-dependent state.
  Worst case 3 poses (<= ~0.8 gap points); 2 of them are taken at phi 0 in the claim (4.88, 3.01 mm), 205 is a contact.
* The R17 preload (0.063 N.m) is gravity only (1.5 x the max opening torque); the iglidur-on-Ti friction of the carriage
  under the pad's load and the spring's own hysteresis are not in it, so the return to the zero dowel is not shown.
* Continuity: the claim's flood (153 of 154 relayed envelope nodes connected, 21 edges cut on phi jumps > 10 deg) is
  the family's reading; 0 bench poses dropped. Not re-run here (the remeasure lens owns it).

## 5. DOF and complexity

4 counted joints (J1, J2, J3, relay): inside the cap, not the 3 the user prefers (a 4-joint answer is never the headline
lead, user 2026-10-17). `tools/simplicity.py` v2.2 reproduces 52.5 (lead 18.5, freek-oracle-route 33.25): 25 for the
4th active DOF, 2 springs x 3, 2 tracks, 1 extra body, 9 joints. The missing spring envelope and flange add made / bought
parts but no points that change the ranking.

## 6. Red team

* **The pose that jams**: the claim's 6 near-floor jams (316, 343, 372, 396, 423, 448: pin-a boss / knee 0.94-0.99 mm
  over the shell top at overhead IR poses) were computed with the knee link sitting INSIDE the boss (2). With the stack
  made buildable the knee link rides higher and these clearances move. JAM_PLACEHOLDER
* **The point that pinches**: min metal over taken poses 0.072 mm at ws 139 (-60, 60, 105) (dump `cmin` 1.70: chain
  metal, not the contact-only set); then 306 (0.69, relayed phi 12.7), 203 (0.72), 379 (0.75). Deepest contacts: 262
  -9.79 (one-sided folded relay), 237 -8.93, 466 -8.22 (phi 28), 206 -6.07, 264 -5.80 (the bumped boss at elevation 165).
  TH_PLACEHOLDER
* **The optimistic numbers**: (a) the bump - per-point, re-directed every pose, and the boss inside the knee link
  (2) - is the in-band price of the relay, and it was counted below its buildable height; (b) the spring coil and the
  T-nut flange are absent; (c) plain 14.02 reads the pooled in-band lifted by the arm-fixed shell underside (303 samples
  at kit density, 99.5 % in band, median 8.4 mm) - real metal, but the gate's chain-only 14.40 is the reading that is
  not a dilution, and 14.02 should not be quoted as the result; (d) the PHI 35 pick and the rt_extra 1.5 box edge are each
  one claim-bench reading (the fast sweep ranked PHI 25 > 30 > 35).

## 7. Paired comparison (claim numbers; this lens did not re-run the held-out)

| design | joints | frozen exact (gate / plain) | near1 | held | complexity |
|---|---|---|---|---|---|
| conecut-knee-knuckle-3r (lead) | 3 | 18.28 | - | 22.38 | 18.5 |
| freek-oracle-route-knuckle-4r | 4 | polished 15.40 (16.20 frozen) | - | 20.50 | 33.25 |
| proxtrack-relay-knuckle-4r (claim) | 4 | 14.40 / 14.02 | 17.68 | 18.51 / 18.01 | 52.5 |
| proxtrack, buildable stack (this lens) | 4 | PAIRED_PLACEHOLDER | | not run | 52.5+ |

## Next

The lever that keeps this morphology alive is to model the pin-a stack as one rigid lift of the knee stack (boss + knee
eye together, knee link joggled to pin b), give the spring a part number and an envelope and the T-nut its flange, then
re-wear frozen exact and held out. A lower boss (the knee stack moved off the track band) is the design answer; lifting
it is the cost.
