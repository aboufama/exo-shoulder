# lead-relay-j0-4r: a spring-centred J0 relay under the lead, with a real O20 hub 0 (4 counted joints)

Round 103 (J3, track jump), lens 1 "relay under the lead", pick 1. Model: `docs/concepts/models/lead-relay-j0-4r.py`;
sweep: `docs/concepts/sweeps/lead-relay-j0-4r.json`; row: `docs/concepts/rows/lead-relay-j0-4r.json`; motion preview:
`docs/concepts/viz/concepts/lead-relay-j0-4r.js`. **4 counted joints. The user prefers 3.** Every comparison below is
with the 3-joint lead conecut-knee-knuckle-3r (verified 18.28, Bench(110,360) exact, frozen).

## 0. The deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Price the metal first and the kinematics second. The ghost (a zero-size J0) answers "how many poses can a relay
     buy". The real question is "what does it cost to carry the relay". Hub 0 is grounded and axisymmetric about c, so
     its distance to the skin never changes with the arm. It is either always in band or never. At the ghost's seat it
     is never in band, and that sets the price before any pose is relayed.
   - Route link 0 as a machinist would. The spec draws link 0 as a bar descending the 20-deg arc. That bar crosses the
     annulus that hub K sweeps around J1 (hub K turns with J1, 15-33 mm off J1's axis, crown about 67 mm from GH). The
     first build clashed with hub K on 47 of 160 fit poses. The buildable link 0 is a turned standoff post that stands
     inside hub 1's own footprint, then a flat bar under hub 0's rotor plate. The model builds that. Hub 0 then has to
     ride higher still: r0 78.5 mm, not 76.5.
   - Scan the seat as well as the window. A cheap fit-bench scan (about 15 s per seat) over a0 x azu with real metal
     shows whether any seat brings hub 0 into band. None can: at every legal seat the chain's sweep sets r0 at 74-104 mm.
   - Not pursued, recorded for the planner: a J0 built as a thin-section ring or arc guide around hub 1 (a ring slide
     centred on c), so that J0's metal sits at hub 1's level instead of above the sweep. It breaks the user's "O20 only"
     hub ruling, and the smallest catalogue ring slides (about 90 mm OD) do not fit inside a 1 cm band.
2. **Rawest material.**
   - The posed skin itself, through the bench's signed distance: `B.dist` on every pose for hub 0's disc, rim, walls
     and crown, and for link 0.
   - The lead's frozen metal samples (981 per pose) and its per-pose dump
     (`docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json`).
   - The humerus rotations HG of every bench pose, which the relay rotates.
   - Skin height along c (the judge's `skinray.py` probe): median 45-48 mm, max 51-57 mm.
3. **Methods and tools.**
   - The lead's own model, unchanged (`conecut-knee-knuckle-3r.py`, SN_CELL=lead), frozen on Bench(60,160) fast.
   - The relay as a rotation of the arm seen by the chain: Q' = Rc(q0)^T Q, then every member turned by Rc(q0).
   - Policy (ii) by grid search over q0 in 1-deg steps: the lead's IK, knee window, closure, J3 stop, |dK| <= dK_lim and
     the J0-J1-J3 sub-chain margin >= 5 deg.
   - The kit's bench report, recomposed per stop window from per-pose records.
   - Hub 0's r0 derived on the fit bench (skin >= 2 mm on every pose, chain >= 1 mm on every pose the lead takes).
   - Stop window picked on the fit bench. Claim on exact Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench (exact path) and the same composition run as a ghost: the ghost reproduces the judge's 15.78-15.90 class
     on the claim bench.
   - The lead's 18.28 reproduced by the q0 = 0 column with hub 0 stripped.
   - The alignment auditor's checks: in-sample window, contacts kept as contacts, near-touch shell.
   - The red-team pose list in section 4.

## 1. The mechanism as built (honest metal)

`scapula handler -> post -> J0 (O20 v5 hub 0, counted, spring-centred, own-angle dowel stops) -> link 0 (flat 12 x 3 Ti
bar under hub 0's rotor plate + turned standoff post on J1's housing crown) -> J1 -> L1a -> K -> L1b -> J2 -> L2 -> J3 ->
member 3 / E strap -> knee pins a / b (MR63ZZ pairs) -> arm pad / BOTTOM`. From J1 to the cuff it is the lead's frozen
record, untouched: stk 6.0, lE 97.14, lc 24.35, phiE 0.75, phib -91.80, J3 window [-111.90, 122.74].

- **Hub 0.** Axis c through GH, a0 20 deg from J1's axis at azimuth 45 (c = (-0.186, 0.780, 0.598) in the scapula
  frame). Underside at **r0 = 78.5 mm**, crown 90.75 mm.
  - r0 is derived, not free: it is the lowest underside at which hub 0 clears the skin by 2 mm on every fit-bench pose
    AND hub 0 + link 0 clear every chain sample by 1 mm on every fit-bench pose the lead takes.
  - That puts hub 0 about 30 mm over the skin along c (judge: median skin 45-48 mm on c). It is **0 % in band**.
- **Link 0.**
  - A 14.3 mm turned standoff post (r 6) stands on J1's housing crown, inside hub 1's footprint, which is the only
    place hub K's sweep never reaches.
  - From the post top a flat 12 x 3 Ti bar (26.7 mm to hub 0's axis, then a pad under the whole rotor plate) runs under
    hub 0.
  - Skin-facing samples: 76 for the bar and 25 for the exposed rest of hub 0's underside. That is 101 extra samples per
    pose, all 26-32 mm over the skin.
  - The descending bar the spec drew clashed with hub K on 47 of the 160 fit poses (measured in this model's first
    build).
- **J0 stops and spring.**
  - ISO 8734 2 m6 440C dowel in an arc groove of hub 0's lower plate (own angle), window [lo, hi].
  - Double-leg torsion spring, 1.4310 wire 0.95, D 22, 6 coils: rate E d^4 / (64 D n) ~ 0.019 N m/rad. With a
    0.08 N m preload the torque is about 0.10 N m at the window end (-59 deg). That is about 0.7 N at the cuff on a
    ~150 mm lever, and about 13 N at the lead's J3 dowel / slipper nose (155 N per N m), well inside the M5 WATCH
    range.

## 2. Results

See the row file for the full per-pose dump. Section 3 holds the claim numbers.

### Fit bench, Bench(60,160) fast (window picked here, never on the claim bench)

| state | gap | reach | ib14 | contacts |
|---|---|---|---|---|
| lead alone (frozen fit) | 12.50 | 0.775 | 0.9007 | 0 |
| hub 0 + link 0 worn, q0 = 0 | 20.83 | 0.775 | 0.8167 | 0 |
| **real, best window [-59, +18]** | **17.37** | 0.825 | 0.8167 | 3 |
| ghost (zero-size J0), same window | 9.54 | 0.825 | 0.9007 | 3 |

The relay buys 3.5 points, and carrying it costs 8.3. On the fit bench the window enumeration is exhaustive (99
(lo, hi) pairs, every breakpoint of the per-pose q0 set), so the sweep over the window is converged by construction.

### Seat scan with real metal, fit bench (best window per seat, picked there)

All fit-bench numbers. Lead alone: 12.50. Hub 0's r0 is derived per seat.

| seat a0 / azu | r0 (mm) | window | real gap | ghost | ib14 | note |
|---|---|---|---|---|---|---|
| 5 / 30-60 | 87.5-88.5 | [0, 0] | 16.96-17.13 | 12.50 | 0.854 | no relay closes the chain: J0 is too close to J1 to help |
| 7.5 / 30 | **65.5** | [-56, +9] | 14.22 | 9.37 | 0.858 | the lowest hub of the scan (~17-20 mm over the skin) |
| **10 / 45** | 88.0 | [-60, +42] | **14.03** | 8.02 | 0.840 | best real seat on the fit bench |
| 10 / 330 | 74.5 | [-56, +57] | 14.86 | 9.90 | 0.850 | |
| 20 / 45 (the ghost's seat) | 78.5 | [-59, +18] | 17.37 | 9.54 | 0.817 | |
| 30 / 0-90, 270-330 | 81-120.5 | - | 22.4-25.4 | 9.8-11.2 | 0.74-0.79 | link 0 grows with a0 |
| 40 / 0-45 | 92-98.5 | - | 24.6-27.6 | 8.4-11.3 | 0.74 | |
| 15-30 / 120-240 | - | - | - | - | - | J0 seat rule fails |

The full table is the sweep file. On top of the 11 x 6 grid there is a 14-seat refinement around a0 10 and a 48-seat
random sample in a0 5-15 (45 legal). The random sample's best is 14.13 at a0 7.2 / azu 355, with r0 65.5 again. **Hub 0 never comes into band**: r0 is 65.5-120.5 mm over every legal seat, against a skin
on c at 45-57 mm. The reason is structural:

- J1 turns the whole distal chain about u1, so hub K (15-33 mm off u1, crown about 67 mm from GH), hub 2 (31-46 mm off
  u1), L1b and the crank sweep an annulus around J1.
- Any grounded hub whose axis is 7-40 deg off J1's sits in that annulus. It can only ride above it.
- Below a0 ~5 the relay stops helping: no relayed pose closes.

## 3. The claim: exact Bench(110,360), frozen lead, window from the fit bench

| seat | window (fit bench) | REAL gap | reach (ws/360) | ib14 | contacts | ghost | hub 0 over the skin |
|---|---|---|---|---|---|---|---|
| lead alone, 3 joints (verified) | - | **18.28** | 0.7278 (262) | 0.9012 | 4 | - | - |
| 20 / 45 (the ghost's seat) | [-59, +18] | **24.92** | 0.7639 (275) | 0.8171 | 12 | 16.07 | median 28.8 mm, min 18.1 |
| 10 / 45 (best fit seat) | [-60, +42] | **22.18** | 0.7583 (273) | 0.8404 | 8 | 16.22 | median 40.5 mm, min 30.4 |
| 7.5 / 30 (lowest hub) | [-56, +9] | **22.95** | 0.7306 (263) | 0.8583 | 7 | 18.22 | median 19.3 mm, min 12.8 (1.7 % in band) |

Overhead stays 8/28 at every seat: no overhead pose is relayed. Follow stays 1.0.

**Ghost check.** The zero-size J0 composed from the same records gives 16.07 at a0 20 / azu 45, inside the judge's
15.78-15.90 class. The 0.17 difference is the window: the judge's [-29, +18] was fitted on the claim bench, and this one
was picked on the fit bench. At q0 = 0 with hub 0 stripped, the composition returns the lead's 18.28 exactly.

**Where the points go (a0 20 / azu 45).**

- **Relays.** 30 ws poses the lead loses have a feasible q0. 23 fall inside the window, 7 are on the stops.
  - 15 are taken:
    - 11 across the body (plane 60-150, internal rotation, axial -75 to -120): the stretched class at the K drive's
      stroke wall, q0 -3 to -58;
    - 3 behind the scapular plane (plane -90 to -30, axial +120 to +135), q0 -21 to -25;
    - 1 folded-class pose (plane 30, elev 105, axial 0) at q0 +18. It is taken at 0.05 mm from the skin.
  - 8 are skin contacts: the relayed chain drives L2 / E into the skin, with metal 0.6-5.7 mm deep.
  - Net: +13 ws, +8 contacts, -2.2 points from the relay.
- **Metal.** Hub 0 and link 0 add 101 skin-facing samples per pose, all 18-40 mm over the skin. They are 0 % in band
  and take ib14 from 0.9012 to 0.8171: **+8.4 points.**
- **Jams.** Hub 0 / link 0 clash with the lead's chain on 2 claim-bench poses that the lead takes at q0 = 0 (hub K
  1.9 mm into hub 0's keep-out, link 0 1.6 mm). r0 was derived on the fit bench, so clearing these would lift hub 0
  further.

## 4. Red team of my own best configuration (a0 10 / azu 45, 22.18)

- **The pose that jams.** At the ghost's seat, 2 clip / ws poses the lead takes are lost to hub K entering hub 0 /
  link 0's keep-out: the fit-bench r0 is not enough on the claim bench. At a0 10 / azu 45 hub 0 clears by 14.5 mm and
  link 0 by 7.0 mm, but only because the hub floats 40 mm over the skin.
- **The point that pinches.**
  - The near-touch minimum over taken poses is 0.054-0.072 mm. That is the lead's own pose-203 class (T1 WATCH),
    unchanged.
  - The relays add 4 taken poses within 1 mm of the skin at a0 20: pose 259 at 0.05 mm (plane 30, elev 105, axial 0),
    340 at 0.44, 369 at 0.45, 446 at 0.93.
  - Under the near-touch rule the relay's gain shrinks further.
- **The optimistic number.**
  - Both "real" numbers are optimistic, because:
    1. policy (ii) assumes the spring finds the least-|q0| closing state quasi-statically;
    2. the continuity flood (no J0 jump > 10 deg per 2-deg edge) was not run, and connected reach can only be <=
       static;
    3. the K-drive's stroke wall now carries the arm's push into J0. At the window end that is about 0.10 N m of
       spring torque, or ~13 N at the slipper nose: small, but a new load path through the lead's M5 WATCH.
  - None of these can bring 22.18 under the 17.5 bar.
- **Gaming check (auditor's eye).** The window was never picked on the claim bench. Relayed skin hits stay contacts.
  Parts clashes caused by hub 0 lose the pose; they are not dropped. Hub 0's samples are counted in in-band with the
  same 1 / 4 mm2 density as the lead's hubs (25 exposed underside samples + the bar's 46-76).

## 5. Verdict

**DEAD.** Gate 0: every real-metal wear is worse than 17.5 frozen exact, and every one is worse than the 3-joint lead.

| claim | REAL | ghost |
|---|---|---|
| best seat, a0 10 / azu 45 | **22.18** | 16.22 |
| the ghost's own seat, a0 20 / azu 45 | 24.92 | 16.07 |
| lowest hub, a0 7.5 / azu 30 | 22.95 | 18.22 |
| 3-joint lead (reference) | 18.28 | - |

Lens 1 closes with this number, and the binding part is **hub 0**.

- Hub 0 is grounded, so it sits at a fixed height over the skin. That height is 65.5-120.5 mm from GH at every one of
  the 108 legal seats tried, 17-55 mm over the skin and 0-2 % in band.
- Its 50-101 skin-facing samples per pose (hub underside + link 0) cost 4.2-8.4 points of in-band.
- The relay itself buys at most 2.2 points (ghost 16.07-16.22 vs the lead's 18.28), because it adds 4-8 skin contacts
  on the poses it relays.

**Even the oracle cannot pass.** At the ghost's seat, the judge's policy-(i) bound (any feasible q0, 13.35) plus the
measured dilution there (+8.4) is 21.8, still over 17.5.

**Convergence gate** (Bench(60,160) fast, 207 configurations in evaluation order: the a0 20 window enumeration, the
seat grid, the refinement and the random sample):

| check | measured | gate |
|---|---|---|
| best gain over the second half | 0.0 score points | < 1 |
| best gain over the last third | 0.0 | < 0.5 |
| top-5 spread | 0.27 | < 3 |

Every stop window is enumerated exhaustively per seat.

**Not run:** the continuity flood. Connected reach can only be <= static reach, so it cannot rescue a number already
over the bar.

## 6. New knowledge (predicts beyond this morphology)

1. **A grounded relay hub cannot sit in band beside a hub that turns its own neighbours.**
   - J1 sweeps hub K (15-33 mm off J1's axis, crown about 67 mm from GH), hub 2 (31-46 mm off), L1b and the crank around
     J1's axis.
   - Any grounded O20 hub whose axis is 7-40 deg from J1's lies in that annulus and must ride above it: r0 >= 65.5 mm,
     >= 17 mm over the skin. Below a0 ~5 no relay closes the chain at all.
   - So a base relay under a knuckle host (or any host whose first link carries a hub within ~35 mm of J1) is either
     stacked inside J1's footprint (lead-relay-wobble-4r: lifts hub 1 out of band), outside the annulus (a0 >= ~45:
     lead-relay-backbridge-4r), or floating (this cell, >= 4 points of dilution).
2. **The link from a floating relay hub to J1 cannot be a bent bar.**
   - The spec's 20-deg descending bar clashed with hub K on 47 of 160 fit poses.
   - The only clear route is a turned standoff post inside J1's own footprint (1.3-23.8 mm tall), then a flat bar
     under the relay hub.
3. **A spring-centred relay at the K drive's stroke wall takes the stretched poses at the cost of skin contacts.**
   - Of 23 relayed poses at a0 20, 15 are taken and 8 drive L2 / E into the skin (0.6-5.7 mm). Of 15 at a0 10, 11 are
     taken and 4 go into the skin.
   - 4 of the relayed takes sit within 1 mm of the skin.
   - A relay must be judged on its contacts, not on its takes.
4. **Ghost vs metal is a trade along a0.** A lower hub (small a0) means fewer relays: at a0 7.5 there are 8 candidates
   and 3 takes, so the ghost is 18.22, no gain. A larger a0 means a longer link 0 and more dilution: ib14 0.74 at a0 30-40.
   The best real seat (a0 10) still sits 3.9 over the lead.

## Audit (2026-10-18, independent auditor): the death STANDS

The audit tried to refute the death in four ways. None worked. The measured reason in one line: **at every seat this
cell covers (a0 <= 40), a grounded O20 hub 0 on its own costs at least 6.27 fit-bench points, even with link 0 deleted
and r0 left free (jams counted as lost poses instead of lifting the hub). The largest relay gain measured anywhere is
4.48, so the best this cell can reach is 14.29 on the fit bench, against the lead's 12.50 there.**

1. **Convergence gate (recomputed from the sweep file, 210 entries in order).**
   - Best fit-bench gap 14.03 (k 101).
   - Gain over the second half: 0.0 score points. Gain over the last third: 0.0.
   - Top-5 spread: 0.73 gap points (14.03-14.76), which is 0.27 score points.
   - Converged. Stop windows are enumerated exhaustively per seat, so no CMA run is needed.
2. **Is r0 over-strict?** The model derives r0 as the lowest underside that clears every chain sample by 1 mm on every
   fit pose. The bench only loses a clashing pose, so lowering the hub and accepting a few jams could in principle pay.
   - Probe: `docs/concepts/verify/lead-relay-j0-4r-audit-bound.py`, 3324 placements (a0 10-60, azu every 15 deg,
     seat-legal only, r0 44-90 in 2 mm steps).
   - Each placement wears hub 0 ALONE (link 0 omitted, which is optimistic). Its underside disc is sampled at
     1 / 4 mm2, a pose where hub 0 comes within 1 mm of the chain is lost, and hub 0 into the skin is a contact.
   - Best per a0 on the fit bench (lead alone: 12.50):

     | a0 | best placement (azu / r0) | gap, hub 0 alone | ib14 |
     |---|---|---|---|
     | 10 | 0 / 76 | 19.30 | 0.832 |
     | 20 | 90 / 78 | 19.19 | 0.833 |
     | 30 | 270 / 88 | 19.01 | 0.835 |
     | 35 | 300 / 78 | 18.77 | 0.837 |
     | 40 | 315 / 78 | 18.78 | 0.837 |
     | 45 | 315 / 78 | 17.26 | 0.852 |
     | 50 | 315 / 82 | 16.13 | 0.864 |
     | 55 | 330 / 70 | 13.75 | 0.907 |
     | 60 | 330 / 74 | 12.50 | 0.905 |

   - Lowering r0 into the band (r0 52-68) loses 15-85 of the lead's fit poses to hub K / hub 2 / L1 at every a0 <= 50.
     Lifting is cheaper than jamming, so the model's derived r0 is the right choice. It is not over-strict.
   - The only placements where hub 0 is in band and jam-free are a0 55-60 / azu 330. They lie outside J1's annulus, and
     that is the sibling cell lead-relay-backbridge-4r. Its bridge (link 0 across the annulus) measured 32.13 frozen
     exact. **No region of this cell's range was missed.**
3. **Is the J0-J1-J3 5-deg sub-chain margin over-strict?** Probe: `docs/concepts/verify/lead-relay-j0-4r-audit-sub.py`
   (fit bench).
   - Relaxing the margin to 0, or dropping it entirely, adds 2 relay candidates at a0 10 and 1 at a0 20.
   - It makes the best real gap WORSE: 14.03 -> 14.66 at a0 10 / 45, and 17.37 -> 17.87 at a0 20 / 45. The ghost goes
     8.02 -> 8.65. The least-|q0| choice then lands on a worse q0.
   - The margin is the user's 5-deg fold rule applied to the J0-J1 dyad. It is not over-strict.
4. **Conventions and modelling (code read of `docs/concepts/models/lead-relay-j0-4r.py`).**
   - The relay kinematics are right: the chain sees Rc^T Q and every member, the arm side included, is turned by Rc, so
     the arm lands back on Q. The skin is the real pose's skin.
   - Hub 0's and link 0's samples are at the bench density (disc_xy 2 mm, bar 2 x 2 mm). Hidden samples are dropped
     only where hub 1's crown statically covers them.
   - Ghost mode strips exactly the n_x extra samples. Relayed skin hits stay contacts, and hub-0 clashes lose the pose.
   - The lead reproduces: fit 12.50, and at q0 = 0 with hub 0 stripped the claim reproduces 18.28.
   - No bug was found that moves the number by more than rounding.

**Re-measured claim** (the model's own claim mode, re-run by the auditor, CB_EXACT=1, Bench(110,360) exact, frozen lead,
a0 10 / azu 45, window [-60, +42] from the fit bench): **gap 22.18**, reach 0.7583 (273/360), follow 1.0, ib14 0.8404,
ib10 0.5352, contact 0.0205 (8 poses: 4 lead + 4 relayed), overhead 8/28, near-touch min 0.072 mm, ghost 16.22, q0 = 0
with hub 0 worn 24.24 (217 s). This reproduces the agent's claim to the digit.

**Template note.** The task template's refutation bar ("within 10 of the champion's 68.93 on Bench(60,160)") is from
round 3, and this row passes it trivially: 22.18 is far better than 68.93. The round-103 bar that killed the row is the
17.5 frozen-exact kill line and the 3-joint lead's 18.28. Against that bar the death stands. Even the optimistic
hub-alone bound plus the largest relay gain (14.29 fit bench) does not reach the lead's own fit-bench 12.50.

**Next (for the planner).** The base relay under the knuckle host is closed at all three cells (beside, stacked,
backbridge). The one placement family where a grounded hub 0 is in band and jam-free (a0 55-60 / azu 330) is
blocked only by link 0's route across J1's annulus. The ask for any future relay is a host whose first link carries no
hub within ~35 mm of J1, so the annulus is empty. A 4th DOF there still costs +25 complexity.
