# fourbar-longdyad-knuckle-3r - toggle four-bar knuckle (strap cell), LISTED FOR THE USER'S B1 RULING

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the four-bar as a *stacking* problem
   before a *law* problem: a spherical four-bar on ground link 1b puts a third layer (the coupler) on top of link 1b and
   two eye columns beside two O20 housings. The designer would (a) check that each eye boss (O9 for an MR63ZZ eye, not
   just the O3 pin) clears the hub housings below the crown, (b) give the coupler the 1 mm non-adjacent clearance to
   link 1b (it is not jointed to link 1b; the spec's +3.15 is a running gap), and (c) price the stack height as in-band
   loss before trusting any law-only count. Second: read B1 as a *sub-chain singularity* question - m_sub < 5 means the
   J1-K-J3 sub-chain is near its own fold, so even a positively slaved K sees th become insensitive to K there; the
   coupled reading is physically defensible only if the four-bar's own transmission at the horn holds through those
   poses (mu_h is gated at 48-132 here for exactly that reason).
2. **Rawest material.** The bench's posed skin itself (tools/concept_bench.py exact path and its grid cache), the motion
   clips through the bench's clip frames, the fit / held-out split; not the parking estimates or the proposer's law-only
   counts (those were synthesised against Bench(110,360) workspace poses - the verification sample - so they are not an
   independent check; held-out is).
3. **Methods and tools.** Closed-form spherical four-bar (crank cone about u2, horn azimuth from A cos b + B sin b = C),
   the generic slaved-K inverse (th -> tau -> q2, K, q1, q3), the lead's verified chain model (longstroke-slipper ->
   roller-longdyad -> sidecar -> frontload -> geneva-pinknee -> minarc kit-rule classes) with its skin, in-band,
   near-touch and part-pair checks, per-pose bodies for the coupler (member 8, its rotation about GH from the pin pair),
   the farm sweep (tools/cloud_run.py) and the frozen claim protocol.
4. **What shows the number is right, other than me.** The bench (Bench(60,160) fast, then the frozen shape on
   Bench(110,360) exact and held out), the verifier harness pattern (frozen + audit near-touch + th_margin), the B1 count
   by |K| band, and a red-team pose list (overhead cone, across-the-body, behind-the-back, the toggle frames).

(Results, limiter and red team below are filled in as measured.)

## What was built (docs/concepts/models/fourbar-longdyad-knuckle-3r.py)

The lead's chain on the 28/50 (or 30-32/48) K dyad at the verified seats, loaded unchanged from
longstroke-slipper-knuckle-3r.py and its parents (skin, in band, near-touch audit, part pairs, knee, O20 stacks). The K
drive (hub-2 lobe, bell crank, nose / roller, flank, clock spring) is deleted. In its place:

* **law**: the closed-form spherical four-bar on ground link 1b (crank cone about u2, horn azimuth from
  A cos b + B sin b = cos c - cos rh (pc . uK), branch br), tabulated per 0.25 deg of q2 travel; the usable window is
  the longest run with real closure, horn transmission 48-132 deg (PA <= 42 where the coupler drives K), K inside its
  stops (-1.5 deg .. stop B at a1max <= bk1 + bk2 - 5.5), kit dyad margin m3e >= 5 and th(q2) monotone with rate <= 3.45.
  The seed reproduces the proposer's numbers exactly (window th 6.22-122.67, K -1.12..79.15, mu_h 59.5-129.0);
* **IK**: th -> tau on the window -> q2, K, q1, q3 in closed form; every pose is forced (K is never parked on a stop);
* **B1 switch** `b1read`: `family` (default, today's reading, the row's numbers: min(m_sub, m_eff) >= 5 on every forced
  pose) or `coupled` (m3e >= 5 only; LISTED FOR B1, never claimed);
* **metal, per pose, real size**: crank lug (3 mm Ti, 6 wide, formed to the sphere, integral with link 2 at link 2's
  layer at hub 2, O9 eye boss = MR63ZZ + 1.5 wall; turns with q2), horn lug (same, link 1a at hub K, + hl), coupler (3 x 4
  mm Ti arc, member 8, its own per-pose rotation about GH mapping the reference pin pair onto the pose's pin pair; a
  linear joggle between two pin-end floors = max(lug top + 0.15, link 1b's top + 1.0) + zcp; O9 eye columns from lug to
  coupler top sampled as the coupler's metal). Part pairs: coupler vs all four hub housings, L1a / L1b / L2 (1 mm; 0.15
  only within the eye of its own pin), both lugs, knee / pad / E; lugs vs the hubs and straps they are not part of.
  `clay=1` (coupler in link 1b's own layer, beside it) was added and measured: it collides with link 1b (121 of 160
  poses on the family best) - the coupler of a useful four-bar runs along link 1b, so it must be stacked over it.

### Spec corrections (measured, not assumed)

1. **The strap seed is not buildable as specified.** Its horn pin sits 11.3 mm off hub K's axis, so the O9 eye boss of an
   MR63ZZ eye reaches 0.7 mm INTO hub K's O20 housing below its crown (CPL-hubK -0.7 mm): every pose is lost (gap 375
   under both readings, 114-187 of 160+60 poses binding on CPL-hubK). A horn eye beside an O20 housing needs >= 15.5 mm
   lateral; rh was swept 15.5-24 deg and the four-bar re-synthesised (the proposer's law-only numbers do not transfer).
2. **The coupler is not jointed to link 1b**, so it gets the 1 mm non-adjacent clearance over link 1b, not the spec's
   0.15 running gap (+0.85 mm of stack).
3. **The judge's knee re-fit for the strap cell (lE 74.3, lc 15.7, phiE 18.4, phib -77.8) hits pad-E on 109 poses** of
   the fit bench; the lead's knee (ang_min raised to 26.88) and swept knees are used instead.
4. The proposer's four-bar seeds were synthesised by counting law-only poses ON Bench(110,360) - the verification
   sample (lesson c). Here every search runs on Bench(60,160); Bench(110,360) frozen and the held-out bench are the checks.

## Search (all on Bench(60,160) fast, farm; sweeps/fourbar-longdyad-knuckle-3r.json, 2520 configurations in order)

* coarse: 300 random four-bars (rc 10-24, gc +-180, rh 15.5-24, c 20-65, br +-1, k0 -1..32, hl, zcp, bk1 28-32 / bk2 48-50,
  a1max = bk1 + bk2 - 5.5, lead knee or swept knee) pre-filtered on the law window alone (th window covering <= 22 .. >= 100),
  under both readings; then 120 coupled four-bars with the TOGGLE constraint (|K| <= 1.5 deg on th 41-44.5) and 100 local
  perturbations of the top configurations;
* CMA-ES (tools/concept_cma.py, popsize 8, 600 s, one 8-vCPU farm job each) from the top 2 of each reading, 11 dims
  (rc, gc, rh, c, k0, hl, zcp, lE, lc, phiE, phib).

| run | evals | best gap | gain 2nd half (score pts) | gain last third | top-5 spread | gate |
|---|---|---|---|---|---|---|
| CMA family-0 (from 55.94) | 457 | 53.26 | 0.073 | 0.036 | 0.022 | passed |
| CMA family-1 (from 58.05) | 369 | 53.35 | 0.196 | 0.156 | 0.025 | passed |
| CMA coupled-0 (from 45.24) | 793 | 34.56 | 0.000 | 0.000 | 0.182 | passed |
| CMA coupled-1 (from 60.07) | 377 | 45.69 | 0.818 | 0.113 | 0.076 | passed |

The two family runs land within 0.09 gap of each other from different starts; the coupled runs end in two basins (34.56,
45.69) - the coupled landscape is multi-modal (the toggle basin vs an open-K basin).

## Results (Bench(60,160) fast; near-touch 2 mm objective, round-9 rule)

| reading | gap | score | reach | follow | ib14 | ib10 | contact | K range used | notes |
|---|---|---|---|---|---|---|---|---|---|
| family (today's B1 reading; THE ROW) | 53.26 | 80.63 | 0.650 | 1.000 | 0.690 | - | 0.024 | 27.6-53.8 deg | hub 2 in band 0.10 |
| coupled (LISTED FOR B1, not claimable) | 34.56 | 87.43 | 0.806 | 1.000 | 0.712 | - | 0.041 | 2.0-65.9 deg | toggle: K <= 0.8 deg on the elev-150 clip |

Lead (slipper-nose-knuckle-3r) on the same fit bench is ~16-17 fast and 18.49 verified - neither reading of this
morphology is near it.

### B1 count (law-only = law window + knee + slide, Bench(110,360) workspace, fails = min(m_sub, m_eff) < 5)

| config | law-only coupled | law-only family | 0-1 | 1-3 | 3-6 | 6-10 | 10-20 | >= 20 | m_sub < 1 | overhead coupled / family |
|---|---|---|---|---|---|---|---|---|---|---|
| proposer's strap seed (kinematics only; its metal fails) | 313 | 180 | 27/27 | 19/19 | 15/15 | 20/20 | 38/38 | 14/194 | 75 | 22/28 / 8/28 |
| coupled coarse best k444 | 280 | 158 | 23/23 | 21/21 | 15/15 | 18/18 | 45/51 | 0/152 | 53 | 12/28 / 5/28 |
| coupled CMA best (34.56) | 286 | 170 | 0/0 | 27/27 | 21/21 | 19/19 | 41/41 | 8/178 | 62 | 15/28 / 7/28 |
| family CMA best (53.26) | 250 | 234 | - | - | - | - | - | 16/250 | 7 | 12/28 / 9/28 |

Every taken pose under |K| 20 deg fails today's reading in every configuration measured (the judge saw "every pose under
|K| 10"; on these four-bars it is every pose under 20 except 6 of 51 at 10-20 on k444). So the family-optimal four-bar keeps
K open 27-54 deg on EVERY pose, i.e. it never uses the toggle.

## Claim protocol (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) EXACT and on the held-out bench; farm)

Plain gap (the lead's v_gap convention, 18.49 / held 23.45); near2 = the 2 mm near-touch reading.

| config | fit (fast, plain) | frozen Bench(110,360) exact | reach | ib14 | ib10 | contact | overhead | near2 | min metal | contact depth | held out |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupled coarse toggle best k444 (LISTED FOR B1) | 28.99 | 34.52 | 0.706 | 0.773 | 0.474 | 0.024 | 9/28 | 49.68 | 0.43 mm | 9 poses, 32.2 mm (max 9.8) | 37.25 (reach 0.682, ib14 0.772) |
| **family CMA best (THE ROW)** | 48.43 | **51.75** | 0.617 | 0.689 | 0.461 | 0.024 | 8/28 | 71.48 | 1.31 mm | 8 poses, 49.7 mm (max 16.2) | 55.30 (reach 0.586, ib14 0.689) |
| coupled CMA best (LISTED FOR B1) | 32.21 | 36.46 | 0.753 | 0.713 | 0.475 | 0.031 | 10/28 | 49.22 | 0.03 mm | 12 poses, 61.6 mm (max 10.9) | 39.80 (reach 0.726, ib14 0.712) |
| family coarse best k344 | 49.83 | 52.89 | 0.619 | 0.675 | 0.445 | 0.024 | 9/28 | 73.84 | 0.62 mm | 8 poses, 52.1 mm (max 16.6) | 56.86 (reach 0.587, ib14 0.675) |

Fold reading on the worn frozen shape (the lead verifier's th_margin, own state): family best min 5.017, 0 of 332 taken
poses under 5 (it passes today's reading by construction); coupled best min 0.0, 151 of 381 under 5 - the B1 count again.
The fit-to-frozen drop is small (family 48.43 -> 51.75, coupled 32.21 -> 36.46; held 55.30 / 39.80): the numbers are not
tuned to the sample, they are simply far from the lead's 18.49 / 23.45.

## Measured limiters

1. **Family reading (the row): B1 -> hub 2 off the skin.** With K held >= 27 deg on every pose, hub 2 never returns to the
   lead's rest seat: on the raise-overhead clip frames (elev 150, th 43) it needs 80.6 mm from GH (the proposer predicted
   71-79 at a1e 40), so its fitted level is ~80 vs ~62 and hub 2 is in band on 0.10 of the clip frames (median 24 mm off
   the skin). The chain ALONE (four-bar metal deleted, attribution only, FB_GHOST=1) scores 43.95 (plain 39.38): B1 costs
   this morphology ~25 points before any drive metal; the four-bar metal adds 9.3 (crank lug in band 0.08, coupler 0.02).
2. **Coupled reading: the four-bar's own metal + hub 2.** Ghost attribution on the coupled CMA best: 34.56 -> 26.26 (plain
   32.21 -> 23.97; ib14 0.712 -> 0.795): the drive costs 8.3 points. On the coarse toggle best k444 (hub 2 in band 0.81) it
   cost 21.2 (45.24 -> 24.06; ib14 0.773 -> 0.868). The crank lug of link 2 sweeps a ~16-20 mm circle round hub 2 with q2
   (in band 0.03, median 19-24 mm off the skin: it must clear the highest skin it ever passes over - the Geneva-tail lesson)
   and the coupler, stacked over link 1b (link 1b top + 1 mm), is in band 0.18-0.20. CMA then traded hub 2's in-band
   (0.81 -> 0.12) for reach (0.769 -> 0.806): with K swinging 2-66 deg hub 2 covers more skin than the lead's parked hub 2.
3. **Near-touch**: min metal 1.77-1.82 mm on both bests (near2 vs plain +2.3 coupled, +4.8 family).

## Red team (own best configurations)

* **The seed as specified jams on hub K** (above): every pose, both readings.
* **Toggle frames** (coupled best): the 7 fit-bench poses with th 41-44.5 sit at K 2.0-2.3 deg (not within 0.75 of stop A
  as specified: CMA moved the dead point to th 44.3, K 1.96, mu_c 179.9, mu_h 88.7). At the dead point the coupler force
  passes through the crank axis, so a K load puts no torque on J2 and the horn (mu_h 88.7) holds K both ways - positive,
  as claimed. Pin play 0.02 mm at the horn eye (r 16.2 mm) reads as 0.07 deg of K (the compact cell's r 3-4.4 would be
  0.26-0.38 deg). Gain dK/dq2 spans -1.21..+1.43 (K reverses through the dead point).
* **Pose classes** (coupled best, Bench(60,160) workspace): across the body (plane <= -45) 14/18 taken (2 skin, 2 fold);
  behind the back (plane >= 90 or axial >= 90) 42/52 (9 fold, 1 skin); overhead elev >= 140 3/12 (5 fold, 3 knee slide,
  1 skin); contacts on 8 poses, hub 2 on 5 of them (the CMA lifted it), crank / coupler / horn on 1 each.
* **Optimistic numbers flagged**: the coupled numbers need the user's B1 ruling; the proposer's law-only 289-291 were tuned
  on Bench(110,360) itself; the parking estimate (R_est 0.747) counted no drive metal and no contacts - the bench says the
  drive metal alone costs 8-21 points.

## Verdict

**Dead as a lead and as a complexity Pareto point, under both readings; the B1 count is the reason under today's.**

* Today's reading (family, the row): 53.26 fast on Bench(60,160) (score 80.63; reach 0.650, ib14 0.690). B1 fails every
  four-bar pose under |K| 20, so the best four-bar keeps K open 27-54 deg everywhere and hub 2 rides 80 mm from GH on
  the raise-overhead frames. The chain alone without any drive metal scores 43.95 - no cell of this law family can reach
  the lead's 18.49 under this reading.
* Coupled reading (LISTED FOR B1, never claimed): 34.56 fast (score 87.43; reach 0.806, ib14 0.712); the same chain
  without its four-bar metal 26.26. Even a free drive under the user's most favourable ruling stays ~8 points behind the
  lead's verified 18.49 on the fit bench, and at cx 14 it is dominated on the complexity front by spine-parked-j2-3r
  (cx 0, 34.29 verified on Bench(110,360) exact).
* Convergence gate passed on all 4 CMA runs (gains <= 0.82 / 0.16 score points, top-5 spread <= 0.18).
* Not built: the compact cell (crank pin on hub 2's cap, horn pin on hub K's cap, coupler at crown level). Its coupler
  and eyes sit at crown level (>= 12.25 mm above the hub bases), i.e. higher than the strap cell's stacked coupler, and its
  law family has the same B1 count (judge: 122 / 289), so the strap cell's ghost bound applies.

What predicts beyond this morphology: (1) a positively slaved K that is never parked on a stop is judged pose by pose
under the family reading, and on a 28-32 / 48-50 K dyad every pose under |K| ~20 deg fails m_sub - a toggle (dead point)
does not help, because the toggle's whole value is K near rest; (2) a third mechanism layer (coupler over link 1b) and a
lug that turns with q2 around hub 2 cost 8-21 gap points of in-band on this chain, about the same as the lead's whole
drive; (3) an O9 eye boss needs >= 15.5 mm lateral beside an O20 housing below its crown - law-only seeds that place a pin
inside that ring are not buildable.

## Audit (2026-10-17, outside auditor): the death stands

**Measured reason (one line):** under today's (strict) B1 reading, every four-bar pose under |K| 20 deg fails m_sub. The
family-optimal four-bar therefore holds K at 27.6-53.8 deg and hub 2 rides off the skin (in band 0.10). The chain alone,
with every piece of drive metal deleted, scores 43.95 fast. Under the coupled reading the chain alone scores 26.26. Both
are above the lead's verified 18.49, so no drive, law or knee re-tune of this morphology can reach the lead.

* **Reproduced exactly** (local, Bench(60,160) fast): family best 53.26 near2 / 48.43 plain (reach 0.650, ib14 0.6895,
  contact 0.0238; losses fold 40, slide 12, skin 4, parts 0). Ghost 43.95. Coupled best 34.56 / 32.21, ghost 26.26.
  **Frozen family best on Bench(110,360) EXACT** (local, 133 s; the row's v_* re-measured, not copied): plain 51.75
  (score 81.18; reach 0.6167, follow 1.0, ib14 0.6893, ib10 0.4606, contact 0.0235), near2 71.48, min metal 1.31 mm,
  overhead 8/28, 8 contact poses with 49.7 mm total depth (max 16.2), th_margin min 5.017 (0 of 332 under 5).
  Losses: fold 104, slide 22, parts 4, contact 8. All of these match the row.
* **Convergence gate, re-applied to the whole sweep file** (2520 entries, split by reading, running best in file order;
  score points): family 1088 entries, best 53.26, gain over the second half 0.036, over the last third 0.000, top-5
  53.26-53.32 (0.02 points). Coupled 1432 entries, best 34.56, 0.000 / 0.000, top-5 34.56-35.06 (0.18 points).
  **Passed**, consistent with the agent's per-run numbers.
* **Code read, no bug found.**
  * The law is the closed-form spherical four-bar: crank cone about u2, horn azimuth from A cos b + B sin b = C.
  * In the IK, m_sub = min(th - |bk1 - cK|, bk1 + cK - th, 360 - bk1 - cK - th) with cK = angle(uK, R(u2,q2) u3). That is
    term for term the lead verifier's `_dm(th, b1, c)` in `th_margin`. The frozen th_margin agrees: 0 of 332 under 5.
  * The family gate applies min(m_sub, m_eff) >= 5 to every pose. ROUNDS.md's Round 11 plan, lens 2, requires exactly
    that ("a positively slaved K is never at rest, so the strict reading ... must hold on every taken pose").
  * The bench, the gap formula and the score are tools/concept_bench.py's, so there is no convention drift against
    tools/concept_baseline.py.
* **Parameter range: the obvious region was covered.** The search held the K dyad at the plan's 28-32 / 48-50, so I
  probed outside it: bk1 24 / 28 / 32 / 36 x bk2 38 / 44 / 50 / 56 on both bests, family reading, four-bar not re-tuned,
  a1max = bk1 + bk2 - 5.5 (32 configs). The best family four-bar reached 53.85 (36 / 38) and 54.63 (32 / 44), against
  53.26. Worn under the family reading, the toggle (coupled-best) four-bar scores 104-160 on every dyad, with 58-107 fold
  losses: B1 kills the toggle on every K dyad tried, not only on 28-32 / 48-50.
* **One over-strict check found; it costs the bests nothing.** CRKL-L1b (link 2's crank lug against link 1b, outside hub
  2's zone) is held to PART_CLEAR 1.0 mm. Link 2 and link 1b are the two members of J2, and the honesty rule gives
  adjacent members of one joint the 0.15 mm running gap. The pair binds on 0 poses of either best (both lose 0 poses to
  parts). It did shape the landscape:
  * the family four-bar worn under the coupled reading loses 112 poses on it (gap 195.03);
  * dyad variants lose 110-171 poses to parts.

  Any relaxation of drive-metal pairs is bounded below by the ghost numbers above (43.95 / 26.26), so it cannot change
  the verdict.
* **Criterion note.** The audit template's numeric bar (within 10 of the round-3 champion's 68.93 score on Bench(60,160),
  i.e. gap 85.44) is met by this design's own 53.26 (score 80.63), as it is by every round-11 design. The claim under
  audit is "dead as a lead (18.49 verified) and as a complexity Pareto point", and that claim stands. The Pareto part is
  firm under the family reading (51.75 frozen against spine-parked-j2-3r's 34.29 at cx 0). Under the coupled reading
  (36.46 frozen) the margin is only 2.2 points, against a round-4 number measured with older checks.
* The dyad probe and the part-pair readout were one-off scratch scripts and are not committed. Champion on the same bench: 68.93 (from its row, not re-run).
