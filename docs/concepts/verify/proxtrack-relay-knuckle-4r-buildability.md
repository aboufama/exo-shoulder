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

**REFUTED as modelled** (the claim's number needs metal that cannot be built). The claim reproduces exactly on its own
model (frozen exact Bench(110,360): gate 14.40, plain 14.02, near1 17.68, chain-only ib14 0.8962, 6 jams, 13 contacts:
`price_base.json`), but its "rigid local bump" lifts the pin-a boss THROUGH the knee link that rides on top of it:
the bumped boss top sits 5.05-5.08 mm inside the knee link's eye at all 184 fit-bench poses (lead: +0.50 mm stack gap at
every pose; `stack.json`). The minimal buildable stack (knee eye lifted over the lifted boss, 60-deg ramp back to the
link, nothing else changed) reads, on the same prepared wear:

| reading (frozen exact Bench(110,360)) | GATE (lower ib14) | plain (pooled) | near1 | ib14 chain / pooled | reach | contacts | jams |
|---|---|---|---|---|---|---|---|
| claim as modelled (reproduced) | 14.40 | 14.02 | 17.68 | 0.8962 / 0.9196 | 0.7917 (285) | 13 | 6 |
| bump made rigid (fixed member-frame vector), amounts as claimed / re-sized | 14.40 / 14.40 | 14.02 | 17.68 | 0.8962 | 0.7917 | 13 | 6 |
| **buildable pin-a stack (this lens)** | **17.46** | **14.40** | **18.06** | **0.8656 / 0.8962** | 0.7917 (285) | 13 | 5 |

The stack costs **+3.06 gate points** (> the 3-point refutation bar): the pre-registered gate moves from PASS (<= 15) to
the report band (17.46, 0.04 under the 17.5 kill). Still 0.82 under the lead's 18.28 like-for-like, but 2.06 over
freek-oracle-route's polished 15.40, at complexity 52.5. Everything else this lens checked holds or is minor: the bump's
per-pose direction (spread <= 6.4 deg) costs 0.00; the fold margin is met on every taken pose (min own-angle margin
5.000 deg, 0 of 395 below 5); the spring coil fits at the zero end without touching the chain (>= 16.7 mm at every fit
pose and relay angle); 3 bistable relay poses on the claim bench (<= ~0.8 points); the bracket is machined, not bent;
the T-nut flange and the spring envelope are unmodelled (the flange, sampled as the parent family samples it - 1 mm x 8 key under the shell, skin-facing - costs 0.00: gate 14.40, contacts 13, pooled ib14 0.9196 -> 0.9234, `price_flange.json`). Held out (the family's held bench, exact, never searched): buildable stack **gate 21.46 / plain 18.37 / near1 23.75** (chain-only
ib14 0.8644, reach 0.7689, contact 0.0479, 17 jams; `held_stackfix.json`) vs the claim's held 18.51 / 18.01 / 23.19:
+2.95 gate points out of sample too, so the stack cost is not a bench artefact. Held, it is still 0.92 under the lead's
22.38 and 0.96 over freek-oracle-route's 20.50. (The held re-wear of the claim's own base was stopped at the time box;
the claim's on-file held numbers are used for the pair.)

## 1. Every joint maps to a real component at its real envelope

| joint / part | component | sampled as metal? | finding |
|---|---|---|---|
| J1, J2, J3, K drive, two-pin knee, J3 dowel stop | the lead's verified O20 stacks / MR63ZZ pairs / ISO 8734 dowels (unchanged) | yes (lead) | as the lead |
| relay track | made part: slotted circular Ti shell 1.5 x 12, R_t 79.9, arc [-109.5, -53.6] deg (56 deg, ~78 mm) | underside in band (303 samples, 1 / 4 mm2 = kit density), top contact / jam only | buildable as a machined / rolled part; no catalogue curved guide fits h_c 1.7 |
| relay carriage | made part: T-nut carriage 24 x 14 on an iglidur strip, h_c 1.7 above the shell top | yes (contact / jam only, not in band) | **the T-nut's retaining flange under the shell is NOT modelled**: a carriage that is only above a 1.5 mm shell cannot be retained (the pad loads it both ways). The parent family's own model (armarc `flange`, 1 mm x 8 key, skin-facing) samples it; this model dropped it. Priced (`price_flange.json`): gate 14.40 unchanged, 0 new contacts, pooled ib14 0.9196 -> 0.9234 - an omission that costs nothing |
| relay spring | "a constant-force spring, preload >= 0.063 N.m" (the parent doc: "CF class; part number to confirm") | **no** | no part number and no envelope. A real strip for ~0.8 N at R_t 80 over >= 55 mm of travel (0.05 mm 301 stainless, 8 wide, natural radius ~3 mm, bending stress ~1.6 GPa) coils to ~7-8 mm OD x 8 wide, standing ~8 mm proud of the shell top beyond the zero dowel (or riding the carriage, which would make h_c ~9). Placed arm-fixed beyond the zero dowel at the shell's station (centre R_t + D/2, arm azimuth lo - (D/2 + 1)/R_t), the
coil clears every member-2 / 3 / 6 point at every fit pose at every relay angle by >= 17.1 mm (D 8) / 16.7 mm (D 5)
(`coil.json`): it fits, at the price of an unsampled ~8 mm standing body ~15 mm off the skin. Riding on the carriage
instead would raise h_c to ~9 mm and the carriage-footprint bump with it - the zero-end placement is the buildable one |
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
  the part's own frame from pose to pose: a deforming part, not a rigid one. Priced (`price_R.json`): giving each point ONE displacement vector fixed in its member's frame (the radial at the fit
pose that set its amount; `rigid1`), and re-sizing the amounts so that vector still meets the clearance target at every
fit pose (`rigid2`, cos floored at 0.3): the direction spread is 6.4 deg max (p90 4.2 deg), the re-size adds 0.00 mm and
both read gate 14.40 / plain 14.02 / near1 17.68, 6 jams - identical to the claim. This item costs nothing.
* **Pin-a stack (the decisive one).** The lead stacks the knee link ON TOP of the pin-a boss and the pad (knee underside
  at tr + tp + 0.5: `off_k = tp + RUN`). Measured at every one of the 184 fit-bench poses the bump is sized on
  (`stack.json`): lead stack gap +0.50 mm at every pose; claim: the boss is lifted 1.76-5.69 mm (all 32 points) and the
  knee link only 0-3.72 mm, so the bumped boss top sits **5.05-5.08 mm INSIDE the knee link's eye at all 184 poses**
  (median -5.05). Two bodies on one pin occupy the same space: the modelled metal is not a part that can be made. The
  buildable version lifts the knee link's eye over the lifted boss (and ramps it back down to pin b on the unlifted pad),
  i.e. more metal higher off the skin than the claim counted. Priced (`stackfix`, `price_stackfix.json`): every knee-link point within the boss radius + 0.5 mm (6.33 mm) of pin a's
axis lifted by at least the boss's max lift (5.69 mm; 35 of 90 knee samples), ramped to 0 at a 60-deg climb beyond the
eye (machined plate), contact-only sets re-derived as the claim does: **gate 17.46 / plain 14.40 / near1 18.06**,
chain-only ib14 0.8962 -> 0.8656, reach, follow and contacts unchanged, jams 6 -> 5. The lifted eye samples leave the
14 mm band (chain-only ib14 -0.031 from 35 knee samples raised 5.7 mm at every clip pose). This is the minimal buildable stack for the
boss amounts the claim itself requires (the eye turns about pin a over the whole boss disc, so it must clear the boss's
highest point); re-stacking the knee link under the boss costs the same layer (tp + 0.5) on the boss instead.

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
  made buildable the knee link rides higher and these clearances move. Re-recorded with the buildable stack: 5 jams (316, 343, 372, 396, 423 - the boss 0.94-0.99 mm over the shell top; 4
of them with chain metal in the skin, so contacts), 448 is no longer a jam. The 1 mm rule floor is where the boss sits
on 5 overhead / IR poses; a +0.15 mm bump clears them (the claim's own probe).
* **The point that pinches**: min metal over taken poses 0.072 mm at ws 139 (-60, 60, 105) (dump `cmin` 1.70: chain
  metal, not the contact-only set); then 306 (0.69, relayed phi 12.7), 203 (0.72), 379 (0.75). Deepest contacts: 262
  -9.79 (one-sided folded relay), 237 -8.93, 466 -8.22 (phi 28), 206 -6.07, 264 -5.80 (the bumped boss at elevation 165).
  Fold margin (one metric, `th` own-angle, the lead's forced / unforced reading): min 5.000 deg over all 395 taken poses
(0 below 5; the relayed poses sit ON the 5-deg boundary by construction of the least-phi solve: 340, 464, 390, 439, 330).
The relay is parked by the stops at exactly the margin, so a stop's tolerance or the carriage's friction lands
directly in the fold margin; the stops must be priced at their tolerance (an m6 dowel in a reamed slot with ~0.1 mm play is ~0.07 deg at
R_t 80 - small, but it must be stated on the part).
* **The optimistic numbers**: (a) the bump - per-point, re-directed every pose, and the boss inside the knee link
  (2) - is the in-band price of the relay, and it was counted below its buildable height; (b) the spring coil and the
  T-nut flange are absent; (c) plain 14.02 reads the pooled in-band lifted by the arm-fixed shell underside (303 samples
  at kit density, 99.5 % in band, median 8.4 mm) - real metal, but the gate's chain-only 14.40 is the reading that is
  not a dilution, and 14.02 should not be quoted as the result; (d) the PHI 35 pick and the rt_extra 1.5 box edge are each
  one claim-bench reading (the fast sweep ranked PHI 25 > 30 > 35).

## 7. Paired comparison (gate / plain; the lead and freek from their verified rows)

| design | joints | frozen exact (gate / plain) | near1 | held | complexity |
|---|---|---|---|---|---|
| conecut-knee-knuckle-3r (lead) | 3 | 18.28 | - | 22.38 | 18.5 |
| freek-oracle-route-knuckle-4r | 4 | polished 15.40 (16.20 frozen) | - | 20.50 | 33.25 |
| proxtrack-relay-knuckle-4r (claim) | 4 | 14.40 / 14.02 | 17.68 | 18.51 / 18.01 | 52.5 |
| proxtrack, buildable stack (this lens) | 4 | 17.46 / 14.40 | 18.06 | 21.46 / 18.37 | 52.5 |

## Next

The lever that keeps this morphology alive is to model the pin-a stack as one rigid lift of the knee stack (boss + knee
eye together, knee link joggled to pin b), give the spring a part number and an envelope and the T-nut its flange, then
re-wear frozen exact and held out. A lower boss (the knee stack moved off the track band) is the design answer; lifting
it is the cost.
