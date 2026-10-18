# lead-relay-wobble-4r: a "wobble" J0 stacked under hub 1 of the lead (4 counted joints)

Round 103 (J3, track jump), lens 1, the PASS rule's "J0 inside J1's footprint" cell. Model:
`docs/concepts/models/lead-relay-wobble-4r.py`; sweep: `docs/concepts/sweeps/lead-relay-wobble-4r.json`; row:
`docs/concepts/rows/lead-relay-wobble-4r.json`; motion preview: `docs/concepts/viz/concepts/lead-relay-wobble-4r.js`.
**4 counted joints. The user prefers 3.** Every comparison is with the 3-joint lead conecut-knee-knuckle-3r (verified
18.28 frozen exact Bench(110,360); 12.50 on the fit bench Bench(60,160) fast).

**Verdict: DEAD.** The stack jams before the in-band arithmetic matters. Hub 0 sits at hub 1's old level, and there it
hits hub K and the riser that link 1a now needs. Those clashes lose 11-170 of the lead's poses at every legal seat. The
best legal configuration scores 32.92 frozen exact (fit bench 28.10), against the lead's 18.28.

## 0. The deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - **Route the stack before pricing it.** An O20 v5 hub has a lower plate (skin face F) and a boss + cap (F + 3.15 to
     12.25). In the lead, hub 1's boss is the grounded housing and link 1a leaves from the lower plate.
     - In a stack, hub 1 sits on the wedge on hub 0's crown. So hub 1's lower plate becomes the relayed body, and link 1a
       has to ride hub 1's boss (the kit's flip3 level, F + 7.25).
     - Link 1a then has to drop 15-24 mm to hub K's lower plate (fK 55.1 mm). It must do that inside the ~4 mm gap
       between hub 1's rim (10 mm off u1) and hub K's near rim (~14 mm off u1; hub K's axis is 25.9 deg from u1).
     - The only part that fits is a 3 mm riser wall at hub 1's rim, 5-axis machined from solid.
     - The spec does not draw that riser, and the riser is the part that jams.
   - **Close the ground path.** Hub 0's boss carries the wedge, so the handler has to hold hub 0's lower plate, at skin
     level, from the side. That is a base tab under the chain's sweep, the thing the user ruled out at J1. It is NOT
     modelled (generous to the design) and is stated as a buildability gap.
   - **Scan the whole circle, and make r0 a variable.**
     - Hub 0's lobe (it reaches 10 + r0 sin a0 mm off u1) has to point into the chain's free sector, wherever that is.
     - r0 is derived (2 mm off the skin on every pose the lead takes) and is also scanned as a design variable (hub 0
       kept low, its skin hits counted as contacts).
   - **The other stack order.** Hub 0 ON TOP of hub 1 keeps hub 1 in band. That is the sibling cell lead-relay-j0-4r at
     small a0: r0 >= 65.5 and 22.18-22.95 frozen exact, measured dead. It is not re-run here.
2. **Rawest material.**
   - The posed skin through the bench's signed distance (`B.dist`) on every pose for hub 0's disc, rim, wall and crown,
     for hub 1's lifted crescent, and for the riser.
   - The lead's frozen per-part metal samples: 981 per pose, with hub 1 at 80 samples, 100 % in band, median 8.6 mm.
   - The humerus rotations HG of every bench pose, which the relay turns.
3. **Methods and tools.**
   - The lead's model, unchanged (SN_CELL=lead, frozen fit on Bench(60,160) fast).
   - The sibling's relay machinery (`relay_candidates`, `make_model` with Rc, policy (ii), the J0-J1-J3 sub-chain
     margin >= 5).
   - A REAL per-pose re-evaluation of the stack metal:
     - the lead's metal with hub 1's covered samples dropped and its exposed crescent lifted, link 1a lifted, and hub 0's
       80 underside samples added;
     - skin contact checked for hub 0's wall and crown, the riser and hub 1's own contact samples;
     - a clash census: hub 0's cylinder against every chain sample except hub 1 and link 1a, the riser against hub 0,
       and the lifted hub 1 against every non-adjacent sample, all at 1 mm.
   - The stop window is enumerated exhaustively on the fit bench. The claim is worn frozen on exact Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench, exact path.
   - The lead reproduced through the same code: 12.50 fast and 18.28 exact at q0 = 0 with the stack stripped.
   - The ghost (zero-size J0, the same records) sits in the sibling's ghost class.
   - The per-part clash census (`parts_why` in every sweep entry).
   - The red-team list in section 4.

## 1. The mechanism as built (honest metal)

`scapula handler -> (skin-level bracket, not modelled) -> hub 0 lower plate | J0 (O20 v5, counted, spring-centred,
own-angle dowel stops) | hub 0 boss + cap -> Ti wedge plate (a0, >= 1.5 mm at its thin edge) -> hub 1 lower plate | J1 |
hub 1 boss -> link 1a (on the boss, lifted) -> riser wall (3 mm, from solid) -> hub K lower plate -> ... the lead, frozen
(stk 6.0, lE 97.14, lc 24.35, phiE 0.75, phib -91.80, J3 window [-111.90, 122.74]) ... -> knee pins a / b (MR63ZZ pairs) ->
arm pad / BOTTOM`.

- 4 counted joints and 0 passive translations. K is slaved; the knee pins sit outside the count.
- Complexity is about 50.75 (the spec's figure: the lead's 18.5 + a 4th joint 25 + the relay's stop, spring and wedge).
- **Hub 0.**
  - An O20 x 12.25 cylinder on c, where c is a0 from u1 at azimuth azu in u1's frame. It is grounded and axisymmetric
    about c, so it is the same body at every q0.
  - Its underside r0 is derived as the lowest that clears the skin by 2 mm on every pose the lead takes on the fit
    bench, or is set as a variable.
  - 80 skin-facing underside samples.
- **Hub 1.** Lifted along u1 by h, the least lift that puts its lower plate >= 1.5 mm over hub 0's crown plane over the
  discs' overlap, and its centre above the crown. That gives h = 13.5 mm at the best legal seat (r0 49.5). Samples under hub 0's
  crown disc are dropped, because they are not skin-facing. The exposed crescent counts (37-53 of 80).
- **Link 1a.** Its 8 samples are lifted by h + 7.25. The riser wall runs from hub K's plate level (55.1 mm) to the lifted
  root: 3 mm thick, 8 mm wide, 10.5-13.5 mm off u1 along link 1a's azimuth, and 20-50 mm tall.
- **Relay.** Policy (ii): q0 = 0 wherever the lead closes; otherwise the least |q0| inside [lo, hi] at which the chain
  closes with the J0-J1-J3 sub-chain >= 5 deg from its fold. A pose lost to a stack clash at q0 = 0 is NOT relayed,
  because a spring-centred J0 cannot know to leave 0.

## 2. Results

### 2a. The arithmetic kill (the spec's first test), on the lead's part table

- **Spec arithmetic:** hub 1 (80) and link 1a (8) leave the band, and hub 0 (80) enters it. ib14 = (884 - 88 + 80) / 1061
  = 0.826, which costs +7.4. The best relay (23 takes, 100 % clear) is worth -6.4. Best case: 19.25 > 18.28.
- **Measured, with the covered samples dropped:**
  - Hub 1's crescent is 37-53 samples, at a median 20-27 mm over the skin, 0 % in band.
  - Link 1a: 0 % in band.
  - Hub 0: 86-100 % in band where it sits at hub 1's level (azu 160-90, the way round through 240), and 0 % where it
    has to float (azu 90-210, derived r0 76-86).
  - At the best legal stack, ib14 = 0.873 on the fit bench (0.9007 for the lead): **+2.7 points of dilution**, not 7.4,
    because covered samples are not skin-facing.
  - So the arithmetic alone does NOT kill the cell. The clashes do.

### 2b. The clash census (the decisive test), fit bench, q0 = 0

All 48 grid seats (a0 6 / 8 / 10 / 12 x azu 0-330 step 30), with r0 derived:

| hub 0 lobe azimuth | r0 (mm) | h lift | poses of the lead lost to stack clashes | what jams |
|---|---|---|---|---|
| azu 240-60 (lobe toward the chain) | 47.5-55.3 (hub 1 at 50.47) | 12.3-20.1 | 41-170 of 184 | hub 0 vs hub K (21-121), riser vs hub 0 (5-102), hub 0 vs L1b (up to 22) |
| azu 90-210 (the chain's free sector) | 76-86 | 41-52 | 1-59 | the riser (a 40-50 mm wall) |

- The best stack seat with r0 derived is a0 12 / azu 240 at 61.85. The best seat with r0 derived at all is a0 12 /
  azu 150 at 28.19, but that seat is **illegal**: hub 0's axis falls outside the J1 seat rule (back of the shoulder and
  acromion top only).
- 27 of the 88 configurations scanned at that point sat on illegal seats (a0 >= 10 at azu 150-210, a0 >= 16 at azu
  240). They are kept in the sweep under `measured_seat_illegal`, with `gap` set to null.

**Why the free sector floats hub 0.** The chain never sweeps housing azimuths ~150-180 because the skin is high there.
With hub 0 at 52 mm, a 6-8 deg lobe toward azu 150-180 enters or grazes the skin on 5-8 fit poses, all high elevation:

- ws (plane 135, elev 135, axial -45): -0.3 mm;
- (150, 120, -60): -0.3 mm;
- (45, 165, -90): 0.4 mm;
- the clip at plane 30, elev 149-150: 0.2-0.3 mm.

That is the contracted deltoid bunching against the acromion. **The sector the chain leaves free is free because the
skin is high there.**

**r0 as a design variable (lobe in the free sector, hub 0 kept low).** 36 configurations: a0 5-12 x azu 135-200 x r0
49.5-68.

| seat (legal) | r0 | gap fast | ib14 | reach | lost to clashes | contacts |
|---|---|---|---|---|---|---|
| **a0 6 / azu 180** | **51.0** | **29.11** | 0.873 | 0.675 | 20 (riser 17, hub K 3) | 1 |
| a0 8 / azu 180 | 52.0 | 33.57 | 0.853 | 0.669 | 18 | 4 |
| a0 8 / azu 195 | 52.0 | 33.77 | 0.860 | 0.681 | 20 | - |
| a0 6 / azu 150 | 51.0 | 37.24 | 0.880 | 0.588 | 34 (riser) | 1 |
| a0 6 / azu 180 (refined) | 49.5 | 28.73 | 0.877 | 0.675 | 20 | 1 |
| a0 5 / azu 180 (relays nothing: a0 <= 5) | 49.5 | 28.94 | 0.881 | 0.663 | 23 | 0 |

The refinement covered a0 5-7, azu 160-200 and r0 49.5-53 (60 configurations). The best stack is a0 6 / azu 180 /
r0 49.5, with hub 1 lifted 13.5 mm and hub 0's lobe 5.2 mm off u1. With the riser counted as clear (a
counterfactual, because the riser cannot be removed), the same stack scores 19.21 fast against the lead's 12.50: hub
0 still meets hub K on 3 poses, and ib14 is 0.863.

### 2c. The relay (policy (ii)), fit bench, the window enumerated

| seat (legal) | window | REAL gap | GHOST gap | relay candidates | relayed takes / contacts |
|---|---|---|---|---|---|
| **a0 6 / azu 180 / r0 49.5** | [0, 21] | **28.10** | 11.88 | 1 | 1 / 0 |
| a0 6 / azu 180 / r0 51 | [0, 21] | 28.48 | 11.88 | 1 | 1 / 0 |
| a0 8 / azu 180 / r0 52 | [0, 8] | 32.93 | 11.88 | 3 | 1 / 0 |
| a0 10 / azu 150 (r0 85.5) | [0, 42] | 32.78 | 11.05 | 8 | - |
| a0 12 / azu 135 (r0 86.5) | [0, 39] | 33.69 | 11.69 | 9 | - |

- At a0 6-12 the wobble relays 1-12 of the lead's 36 lost fit poses. The ghost gain is only 0.6-1.5 points (11.05-11.88
  against the lead's 12.50).
- The stack price is 16-21 points on the fit bench.

## 3. The claim: exact Bench(110,360), frozen lead, window from the fit bench

Best legal configuration: a0 6 / azu 180, r0 49.5 (hub 0 at hub 1's old level, 1.0 mm lower), h 13.5, window
[0, 21] picked on the fit bench (`CB_EXACT=1 WOB_R0=49.5 ... claim 6 180 0 21`, 351 s).

| state | gap | reach (ws/360) | follow | ib14 | ib10 | contacts | lost to stack clashes | overhead |
|---|---|---|---|---|---|---|---|---|
| 3-joint lead (reproduced through this code) | **18.28** | 0.7278 (262) | 1.0 | 0.9012 | 0.5739 | 4 | - | 8/28 |
| **REAL: stack + relay, window [0, 21]** | **32.92** | 0.6472 (233) | **0.90** | 0.8796 | 0.5608 | 2 | 42 (riser 35, hub 0 on hub K 7) | 7/28 |
| q0 = 0 (the stack's price alone) | 32.92 | 0.6472 | 0.90 | 0.8796 | 0.5608 | 2 | 42 | 7/28 |
| GHOST (zero-size J0, same window) | 18.28 | 0.7278 | 1.0 | 0.9012 | 0.5739 | 4 | - | 8/28 |

- **The relay buys nothing on the claim bench.** Of the lead's 94 lost poses, 2 have a feasible q0, and both fall
  outside the fit-bench window, so the ghost equals the lead.
- **The stack costs 14.6 points.**
  - Reach: -29 ws poses (+8.1).
  - Follow: 0.90 (+5.0). The clashes land on followed clip frames, including the scapular-plane overhead clip at plane
    30, elev 124-150.
  - ib14: 0.8796 (+2.0).
- **In band, per part, over the taken clip frames:**
  - chain (the lead minus hub 1 and L1a): 0.909, median 9.3 mm;
  - hub 1's exposed crescent (33 of 80 samples): 0 %, median 21.1, min 17.8;
  - L1a: 0 %, median 30.4;
  - hub 0 (80): **100 %**, median 9.3, min 3.4.
- Near-touch minimum over taken poses: 0.072 mm (the lead's own pose-203 class).

## 4. Red team of my own best configuration (a0 6 / azu 180 / r0 51)

- **The pose that jams.** The scapular-plane overhead clip (plane 30, elev 124.5-150, axial -55 to -60): 5 followed
  frames.
  - The riser enters hub 0 by 1.7-1.9 mm. Hub 0 clears hub K there by only 1.8-1.9 mm.
  - Worst ws pose: (-15, 75, -45). Riser -4.6 mm into hub 0, and hub 0 -0.3 mm into hub K.
  - Across the body at low elevation, (135-150, 0-30, -45 to -60): the riser clears hub 0 by only 0.4-0.8 mm, under the
    1 mm rule.
  - So the stack jams first at **overhead**, which is the requirement that matters most.
- **The point that pinches.**
  - Hub 0's lobe toward azu 180 meets the skin at ws (135, 135, -45): its wall is 0.67 mm in, a contact.
  - Three taken poses sit within 1 mm of the skin: 0.36 mm at (120, 30, -135), 0.37 at (45, 165, -90), 0.45 at
    (60, 165, -90).
  - On the clear poses, the riser's clearance to hub 0 is 1.04 mm at minimum and 2.18 mm at p10. A 0.2 mm build error
    loses more poses.
- **The optimistic numbers.**
  - Hub 0's ground bracket (a skin-level tab from its lower plate to the handler, under the chain's sweep) is not
    modelled. It would add skin-level metal and clashes.
  - The wedge is drawn at its 1.5 mm minimum.
  - The riser is the thinnest buildable wall (3 mm). Its 8 mm width matches the lead's strap.
  - Policy (ii) assumes the spring finds the least-|q0| state quasi-statically.
  - The continuity flood was not run. Connected reach can only be <= static reach.
  - Even with the riser deleted (impossible: it is the only path from hub 1's boss to hub K's plate) the fit-bench
    number is 19.21 against the lead's 12.50.
- **Gaming check (auditor's eye).**
  - The window was picked on the fit bench, never on the claim bench.
  - Stack clashes lose the pose; they are not dropped.
  - Hub 0's skin hits stay contacts.
  - Covered samples are dropped only where hub 0's crown disc lies under them.
  - Seat-illegal seats are nulled in the sweep, not ranked. 27 configurations sat on illegal seats, including the
    best-looking "floating" ones (a0 12-16 / azu 150, 26.12-28.19 fast).

## 5. Verdict

**DEAD.** The verdict rests on the clash count, which is the spec's own closing rule ("if the two do not coincide, close
on the clash count").

- The relaying azimuth and the in-band seat never coincide with a clear one.
  - With hub 0 at hub 1's level (r0 47.5-55.3), its lobe has to sit in the 4 mm gap between hub 1's rim and hub K's,
    and there it meets hub K and link 1a's riser. That loses 41-170 of the lead's 184 fit poses wherever the lobe points
    toward the chain.
  - Where the lobe points into the chain's free sector, the skin is high on overhead poses. Hub 0 then either floats
    (r0 76-86, 0 % in band, hub 1 lifted 41-52 mm) or takes contacts. Even at r0 51 the riser still loses 17 poses.
- The arithmetic kill as written (+7.4) overstates the dilution: the measured value is +2.7 with covered samples
  dropped. But the clashes alone cost more than any relay can return.
- Best legal: a0 6 / azu 180 / r0 49.5, window [0, 21]: **28.10 fast** (lead 12.50) and **32.92 frozen exact Bench(110,360)** (lead 18.28).

**Convergence gate** (Bench(60,160) fast, legal configurations in evaluation order): 122 legal configurations of 149 evaluated. The best gained 0.14 score points over the second half (< 1) and 0.14 over the last third (< 0.5); the top-5 spread is 0.31 (< 3). **Converged.**.

## 6. New knowledge (predicts beyond this morphology)

1. **Stacked O20 hubs force the output link onto the upper hub's boss.**
   - When a hub sits on another hub's crown, its lower plate is the body that sits on the wedge. Its output link must
     then leave from the boss (F + 7.25).
   - So a 2-hub stack lifts the first link by about 20 mm over the lead's, not by 12.25 mm.
   - On a knuckle host the link has to come back down inside the 4 mm gap between hub 1's and hub K's rims, as a riser
     wall. Any grounded part within ~15 mm of J1's axis at hub level jams on that riser.
   - Rule: **no relay hub can be stacked under J1 on a host whose second hub sits within one hub diameter of J1.**
2. **The chain's free sector is free because the skin is high there.**
   - Around the lead's J1, the housing azimuths the chain never visits (~150-180) are where the deltoid bunches up
     against the acromion at elev 120-165.
   - A grounded part placed "where the chain does not go" meets the skin instead. At a 6-8 deg offset, r0 jumps from
     51 to 76-86 mm.
   - Free-sector arguments for hub placement have to be checked against the high-elevation skin, not only against the
     chain's sweep.
3. **The arithmetic kill on the part table overstates the dilution of a stack.**
   - Covered samples are not skin-facing.
   - Measured: hub 1's exposed crescent is 37-53 of 80 samples, and ib14 0.873 instead of the spec's 0.826.
   - Price stacks with the cover mask.
4. **A small-angle relay (a0 6-12) under this host relays 1-12 poses.** That is a ghost gain of 0.6-1.5 fast points.
   - The proposer's bound (10-23 newly closable at a0 6-10) assumed the full +-180 travel inside the seat rule.
   - With policy (ii), the sub-chain margin and the fit-bench window, most of those poses either need |q0| beyond the
     seat-legal travel or close into contact.
   - Lens 1 ("J0 inside J1's footprint") closes with these numbers: neither stack order (this cell, or the sibling's
     hub 0 on top) and no floating relay comes within 3.9 points of the 3-joint lead.

## Audit (2026-10-18, independent auditor): the death STANDS

The audit tried to refute the death by forgiving everything the verdict rests on. It still holds. The measured reason
in one line: **with every stack clash forgiven and the riser deleted, the stack's unavoidable in-band dilution (hub 1's
exposed crescent lifted 13-15 mm onto the wedge, link 1a on hub 1's boss) costs 3.1-7.4 fit-bench points at every
seat-legal a0, and the relay returns at most 2.8 of them (1.9 at the best seat): the cell's floor is 14.92 fast against the lead's 12.50.**

1. **Convergence gate, recomputed from the sweep file** (149 entries, 122 seat-legal, in order): the best gained 0.14
   score points over the second half and 0.14 over the last third; the top-5 spread is 0.31 score points (0.84 gap).
   Converged. The stop windows are enumerated exhaustively per seat, so no CMA run is needed.
2. **Reproduced through the model's own code.**
   - Fit bench, q0 = 0, a0 6 / azu 180: 28.73 at r0 49.5 and 29.11 at r0 51 (sweep entries 116 and 68, exact match).
   - The claim, `CB_EXACT=1 WOB_R0=49.5 ... claim 6 180 0 21` (403 s): **32.92** frozen exact Bench(110,360), reach
     0.6472 (233/360), follow 0.90, ib14 0.8796, ib10 0.5608, 2 contacts, 42 poses lost to stack clashes (riser 35,
     hub 0 on hub K 7), overhead 7/28, near-touch 0.072 mm. The ghost and the lead both read 18.28. Identical to the
     row. These are the row's v_* fields.
3. **Code review.** The lift h, the cover mask, the riser's height range, the clash pairs (riser and hub 0 are not
   adjacent, so 1 mm is the right clearance), the contact sampling and the relay composition were checked. No bug that
   inflates the gap. Two small items, both generous to the design or negligible:
   - the riser bottom sits at hub K's plate height measured along u1 (55.1); hub K's near rim projects to ~54 mm along
     u1, so the drawn riser is ~1 mm SHORTER than it must be;
   - the cover mask of hub 1 is computed at q0 = 0 and reused on relayed poses (1-3 poses).
4. **The forgiven bound** (`docs/concepts/verify/lead-relay-wobble-4r-audit.py`, results in
   `docs/concepts/verify/lead-relay-wobble-4r-audit.results.json`). Could a better routing - a flipped hub K, a riser
   clocked elsewhere, a slimmer drop - remove the clashes and refute the death? The probe sets every stack clash to
   "never loses a pose" (PART_CLR -inf), deletes the riser, and keeps only what the stack cannot avoid: hub 1 on the
   wedge (exposed crescent counted), link 1a on hub 1's boss, hub 0's underside and its skin contacts. 288 placements
   on the fit bench: a0 5-20, azu every 15 deg, r0 derived or set 48.5-53; 38 sat on illegal seats.

   | a0 | best seat-legal placement (azu / r0) | q0 = 0, every clash forgiven | ib14 | + relay, window enumerated | ghost |
   |---|---|---|---|---|---|
   | 5 | 225 / 49.0 | 15.60 | 0.869 | 15.60 (relays nothing) | 12.50 |
   | 6 | 240 / 48.5 | 16.03 | 0.865 | 15.41 | 11.88 |
   | 8 | 270 / 48.0 | 16.79 | 0.857 | **14.92** (window [-51, 0], 3 relayed) | 10.63 |
   | 10 | 240 / 47.5 | 17.79 | 0.847 | 17.17 | 11.88 |
   | 12 | 240 / 48.0 | 18.44 | 0.841 | 17.19 | 11.25 |
   | 14 | 255 / 47.75 | 19.16 | 0.833 | 17.91 | 11.25 |
   | 16 | 255 / 48.0 | 19.71 | 0.828 | 18.37 | 11.16 |
   | 20 | 0 / 52.75 | 19.94 | 0.826 | 17.12 | 9.68 |

   - Lead on the same bench: 12.50, ib14 0.9007. The forgiven floor is above it at every a0, and the dilution grows
     with a0 (the lobe pushes hub 1's crescent further out) faster than the ghost gain.
   - Also dropping link 1a's lifted samples (as if it were not skin-facing at all): 14.25 at a0 8 / azu 270.
   - The original claim seat (a0 6 / azu 180 / r0 49.5) forgiven: 17.32 at q0 = 0, 16.70 with the relay.
   - The free-sector floating seats (a0 10 / azu 150, a0 12 / azu 135, r0 85-87) forgiven: 25.83 and 26.76. Hub 0 is
     0 % in band there.
   - So no routing fix can reach the lead. The clashes the verdict names are real and buildable-relevant, but the cell
     is dead even without them.
5. **Not counted (would be gaming).** A skirt hung from the wedge to pull hub 1's crescent samples into band adds metal
   only to move the in-band average; it would also have to clear hub 0's rim while turning with q0.

**Template note.** The template's round-3 refutation bar (within 10 of 68.93) is passed trivially. The death is judged
against the 3-joint lead (12.50 fast / 18.28 exact), and it stands.
