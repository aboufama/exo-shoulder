# Round 4 ideation: judge and red team (2026-10-16 ~05:45 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275), tools/concept_bench.py); gap 0 is the real
target. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered with 3 active DOF (a 4th joint only as the honest comparison the brief asks for).

Reference: champion spherical 3R 75.94 (Bench(110,360) exact). Verified leaders: skin-normal-3r-pin-knee k4598
30.35 (complexity 21.5) and spine-parked-j2-3r k7008 34.29 (complexity 0).

Every top design is limited by the J2 fold: frozen reach is 0.59-0.62, worth ~29 gap points on its own.

## Red-team measurements made by the judge

All from the proposers' own result files, re-read by the judge (scratchpad `lensj2/frz_*.json`, `r4x/frozen_*.json`)
and from this round's kit results in docs/concepts/events.jsonl.

1. **j3-neck-over-3r: the whole gain is the in-band term.** Frozen exact at k7008, same protocol:

   | | gap | reach | follow | in-band14 | contact | link 2 / neck in band |
   |---|---|---|---|---|---|---|
   | k7008 as verified | 34.29 | 0.5944 | 0.9545 | 0.878 | 0.0154 | 0.795 / 0.847 |
   | neck over link 2 | 32.10 | 0.5944 | 0.9545 | 0.901 | 0.0154 | 0.884 / 0.807 |

   - The 32.10 that remains is reach 30.56 + contact 1.54. In-band is already >= 0.90.
   - So **watch-scale-spine-3r is worth 0 on top of it**. Its parts (O11 hubs, 8 x 2 straps) only buy in-band, and
     its own fast record also stops at in-band 0.9002.
   - The parts kit pays only if a retune spends in-band slack on reach. The two candidates are merged.
2. **deltoid-crest-j3-3r: the basin's closure gain does not survive the big bench.**
   - Fast closure is 0.836 against k7008's 0.764.
   - Frozen exact gives 35.90: reach 0.611, only +0.017 over k7008's 0.594.
   - Follow drops to 0.936. The overhead clips' follow falls to 0.8, so it **loses fit-clip frames**.
   - Contact is 0.044 and collide 0.084.
   - It is worse than k7008 with the same neck-over layering (32.10).
   - The base member must enter hub 1 through a 27-deg free sector, and that is unmodelled, so the number is
     optimistic.
3. **The proxy behind this round's fold levers is optimistic.** It is the axis-ray / centre-ray proxy at q 0.98:

   | design | proxy | kit, Bench(60,160) fast | proxy error |
   |---|---|---|---|
   | stop-relay-rocker-3r | 20.7 | 35.24 (coarse 37.14) | +14.5 |
   | dwell-fourbar-knee-3r | 21.8 | 26.86 | +5.1 |

   - Frozen exact sits a few points above fast for every design so far.
   - Every proxy-only claim below (the relays and the eccentrics) gets +5..+15 added.
4. **The arm-parked 4R's spring is sized against gravity only.**
   - The proposed preload of 10 N.mm is 2.3 x the 4.4 N.mm gravity moment (16 g at 28 mm, checked).
   - docs/FINDINGS.md ("Unpowered tracking") measured the 3R chain's bearing drag at 0.05-0.10 N.m about the
     shoulder. That is rolling bearings at real speed and at 2x.
   - The self-motion collects the J1-J3 friction through O(1) ratios. An honest break-away preload is ~50-100 N.mm,
     5-10 x the proposal.
   - At that preload the 0.7 mm wire gives 32M / (pi d^3) = 1490-2970 MPa and fails. It needs d 0.9-1.1 mm
     (700-770 MPa) and a ~6.6 mm coil.
   - The wearer then feels 50-150 N.mm whenever the spare is out.
   - This does not change the bench number (the kinematic policy is the same). It decides R17 and whether the 4R is
     real: judge/dynamics.py with the stop and spring modelled is a gate.
   - Frozen breakdown (r4x/frozen_A.json):

     | reach | in-band14 | contact | crown contacts | link 3 in band | spare moves on | deflection p95 / max |
     |---|---|---|---|---|---|---|
     | 0.750 | 0.864 | 0.038 | 7 | 0.51 | 20 % of poses | 56 / 86 deg |

   - Near-touch is unmeasured. It cost the leader +6.
5. **The slot law is checked against the window algebra.**
   - With a1 37.6, clip(60, 90) gives the fold-free window [|37.6 - 60| + 10, 37.6 + 90 - 10] = [32.4, 117.6],
     against the leader's [46, 101].
   - A clip law is the per-pose optimum for a given a2 range. The claimed coverage (0.750 big bench) is an upper
     bound consistent with the workspace demand (th 26-140 at 5-95 %, docs/research/reach_attribution.md).
   - The loop is determined: spherical mobility 3(3 - 1) - 2 x 2 (J2, K) - 1 (slot pair) = 1 = q2.
   - The in-band cost of link 2b and the lever is only proxy-measured.
6. **crest-knee-3r: its headline lever is the crest-seat fold reduction.** Item 2 shows that reduction is worth
   ~1.7 frozen reach points, not the 4-6 claimed.

## Verdicts

| candidate | verdict | reason |
|---|---|---|
| j3-neck-over-3r | **PICK 1** (merged with watch-scale-spine-3r) | Measured 32.10 frozen exact at complexity 0, with no retune; a pure layer-order change that every spherical 3R must adopt. It cannot cross 90 alone (item 1). |
| arm-parked-knee-4r | **PICK 2** | The only measured frozen crossing: 22.36 = score 91.9 (one-sided 25.56). On the same harness the 3R leader is 34.28. Controls show the gain is the 4th joint, not the seats. It is a 4th ACTIVE DOF (complexity 32.25, a 4th motor in MVP2, against the user's "push for 3"). The spring is undersized against drag (item 4). Claiming it as leader needs the user's word. |
| deltoid-crest-j3-3r | **PICK 3** | A new hub-2 parking basin with complexity 0. Its frozen 35.90 is worse than the neck-over leader (item 2). Kill gate: it must beat 32.10 frozen with the base stub modelled. |
| slotted-eccentric-j2-3r | **PICK 4** | The only two-sided fold lever this round, determined by a roller in a slot (mobility 1). It uses real watch-scale parts (MR63ZZ, MR52ZZ, a wire-EDM slot). Proxy-only: judge expectation 27-33 frozen (item 3). |
| slotted-eccentric-pin-knee-3r | **PICK 5** (gated) | Same lever on the verified pin-knee host. That host's gap is 100 % reach, but its in-band slack is only 0.003. At complexity 35.75 it must beat the 4R (32.25, 22.36), not just the pin knee. Start only after pick 4 passes its slot gate and gains >= 3 frozen points. |
| crest-knee-3r | **PICK 6** (low confidence, cheap kill) | The knee's short members remove the crest 3R's neck cost. The naive transfer fails (167-171 of 220 parts poses), and the seat gain is ~1.7 points frozen (item 6). Stage-1 kill test: 400 tries. |
| stop-relay-rocker-3r | REJECT: duplicate | Already in the catalogue (status screening, slice r4-A). The kit measured 35.24 fast against the proxy's 20.7. |
| dwell-fourbar-knee-3r | REJECT: duplicate | Already in the catalogue and screening: 26.86 fast (score 90.2 fast). The frozen exact run is in flight. |
| stop-relay-knee-3r | REJECT: dominated (merged into dwell-fourbar-knee-3r) | Same one-sided, folded-side knee in link 2 as the existing dwell four-bar. It adds a spring and a sensed passive and gets the same physics risks as the rocker. Its proxy (22.0) is the instrument that over-predicted the rocker by 14.5. It stays the fallback if dwell-fourbar's pin Q cannot be placed in band. |
| deltoid-arc-cuff-4r | REJECT: measured dead | 37.40 frozen, worse than the 3R leader (34.28). The R 73 arc track has no catalogue part (THK HCR-class curved rails start at about R 100), so it would be a made sliding pair. Ring 0.62 and link 3 0.36 in band. It is the measured answer to "3 joints + sliding cuff": an axial cuff joint buys closure but not band. |
| spine-sprung-base-4r | REJECT: control only | 70.11 fast (hub 3 and link 2 at 0.00 in band). It proves the 4R's spare must live at the arm end. |
| watch-scale-spine-3r | MERGED into j3-neck-over-3r | Its only lever is in-band, which the layer swap already zeroes (item 1). Its parts stay declared sweep options. Its sensitivity data (a crown stack below 12.25 buys 0; a smaller J1 is worse) goes to FINDINGS through the modeller. |

No candidate failed the joint-component test outright except the arc track (made part, no catalogue part at that
size).

- No candidate needs a passive translation.
- No candidate has an undetermined coordinate:
  - the spring-set spares (the 4R, the relays) are set by an energy minimum under stops;
  - the slot and the dwell loop are kinematically determined;
  - the pin-knee closures are closed through the wearer's GH.

## Ranking

Ranking = (expected gap reduction vs the champion's 75.94) x (confidence) x (buildability). Buildability counts
passive translations first, then springs, made sliding pairs and active DOF. Expected values are the judge's, after
the red team.

| rank | pick | expected frozen gap | reduction | confidence | buildability | product | complexity |
|---|---|---|---|---|---|---|---|
| 1 | j3-neck-over-3r | 30-32 (31.5) | 44.4 | 0.9 | 1.0 | 40.0 | 0 |
| 2 | arm-parked-knee-4r | 22-26 (23) | 52.9 | 0.8 | 0.8 | 33.9 | 32.25 |
| 3 | deltoid-crest-j3-3r | 30-34 (32) | 43.9 | 0.4 | 1.0 | 17.6 | 0 |
| 4 | slotted-eccentric-j2-3r | 27-33 (29) | 46.9 | 0.4 | 0.85 | 16.0 | 14.25 |
| 5 | slotted-eccentric-pin-knee-3r | 24-30 (26) | 49.9 | 0.25 | 0.8 | 10.0 | 35.75 |
| 6 | crest-knee-3r | 28-32 (29) | 46.9 | 0.15 | 0.9 | 6.3 | 21.5 |

- **Most likely to cross 90 on the verification bench**: arm-parked-knee-4r (measured 22.36, but 4 active DOF).
- **Best chance among the 3-active designs**: slotted-eccentric-j2-3r, then the existing dwell-fourbar-knee-3r
  (26.86 fast, frozen running).
- j3-neck-over-3r ranks first on the formula because it is a near-certain complexity-0 gain. It does not cross 90.

## What happens next (the loop)

1. **j3-neck-over-3r.** Promote the layering into the spine-parked model and run the farm CMA with in-band as a
   constraint (>= 0.90) and reach as the objective. Then run the frozen exact claim against the k7008 control in the
   same job, then the verifier.
2. **arm-parked-knee-4r.**
   - Copy r4.py into docs/concepts/models.
   - Add near-touch, top faces, the J2-stop load direction and link 3's swept path.
   - Run judge/dynamics.py with a drag-sized spring (preload >= 50 N.mm) and rad4 10.
   - Run the farm CMA on contact and in-band, then the independent verifier.
   - If it verifies <= 27.5, that is a user-level decision ("settle for 4"): report it as a big update.
3. **slotted-eccentric-j2-3r.** Run the control (must give 28.49 fast), then the slot gate, LHS 300 and CMA. Pick 5
   starts only if this one gains >= 3 frozen points.
4. **deltoid-crest-j3-3r and crest-knee-3r.** Run their kill gates first (beat 32.10 frozen; stage 1 under 100 bad
   poses in 400 tries).
5. **The fold lever on 3 active DOF.** Still open: the two-state a1 relay (0.93-0.95 kinematic ceiling,
   docs/concepts/ROUNDS.md round-5 plan) has never been modelled. It is the round-5 keemink-4r-band lens.
