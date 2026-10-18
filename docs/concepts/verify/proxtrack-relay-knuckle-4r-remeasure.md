# proxtrack-relay-knuckle-4r - independent RE-MEASURE verification (skeptic)

Harness: `docs/concepts/verify/proxtrack-relay-knuckle-4r-remeasure.py`. Outputs next to it:
`proxtrack-relay-knuckle-4r-remeasure_{bench,held,edges,flood,bumpcheck}.json`. Local only: nice 10,
OMP_NUM_THREADS=1, at most 2 processes. (Once, for about 15 s, a fast-bench diagnostic ran as a third process.)

The claim's model is the mechanism under test, so it is loaded UNCHANGED for the mechanism. That covers the lead fit on
Bench(60,160) fast at phi 0, shape frozen, then the least-phi relay solve, the wear (exact) and the relay hardware
re-record. Everything the score is READ from is re-derived here from the per-pose metal arrays: taken, contact, pooled
in-band and chain-only in-band (the first nC = 981 samples per pose are chain metal), plus near-touch. The claim's own
flood is switched OFF (`flood=0`), so the static wear is read before any continuity knock-out. The flood is my own. The
claim's params are the row's best_params: PHI 35, ds 19.538, rt_extra 1.5, pre 10.41, bump 1.002, band 9.272,
ramp 6.0 (raised to its 60-deg floor, 6.15), tilt 12, taz 235.

## R1 - frozen exact Bench(110,360), margin 5, O20 (reproduced to the hundredth)

| reading | claim | mine | lead conecut-knee (same harness, same fit, same bench object) |
|---|---|---|---|
| plain gap (pooled ib14) | 14.02 | **14.02** (ib14 0.9196) | 18.28 (ib14 0.9012) |
| GATE (lower in-band: chain-only 0.8962) | 14.40 | **14.40** | 18.28 |
| near-touch 1 mm, pooled / chain-only | 17.68 / - | **17.68 / 18.06** | 19.92 |
| near-touch 2 mm (report only) | 38.01 | 38.01 / 38.39 | - |
| reach (ws taken) | 0.7917 (285) | 0.7917 (285) | 0.7278 (262) |
| follow | 1.0 | 1.0 | 1.0 |
| contacts | 13 | 13 (share 0.0319) | 4 (0.0106) |
| overhead taken / 28 | 8 | 8 | 8 |
| min metal over taken | 0.072 | 0.072 mm | - |

* The fit (Bench(60,160) fast, phi 0) reads 12.50, the same as the lead's own verifier's fit_fast. The ideal relay
  (no hardware) reads 13.21 frozen exact, matching the claim's bound.
* The lead wear (the same phi-0 fit, frozen, worn on the SAME Bench(110,360) object, with no relay) reads 18.28, the
  verified number. So the harness reproduces the lead too.
* **Paired on the bench.** The claim takes all 262 ws poses the lead takes, plus 23 relayed poses. The lead takes no
  ws pose the claim loses. Exact McNemar on ws taken: p = 2.4e-7.
* **The cost is contact.** The lead's 4 contacts reappear in the claim at identical depths (-8.93, -5.80, -4.28,
  -1.23). The relay adds 9 more: (30,135,0) -9.79, (150,105,-105) -8.22, (0,120,-15) -6.07, (135,135,-90) -1.92,
  (75,150,-105) -1.73, (150,45,-105) -1.28, (-15,90,45) -0.71, (120,135,-90) -0.70 and (90,165,-90) -0.07.
  Summed depth is 50.7 mm against the lead's 20.2 mm.
* Doc error, which moves no number: the doc says pose 264 (30,165,-60) is "-1.17 on the lead". On this harness the
  lead reads -5.80 there too, so the relay does not deepen it.
* **The fast pick does not reproduce on the fast bench.** Under the current model the pick reads plain 4.25 / gate
  4.65 / near1-gate 10.29. The sweep's record is 3.75 / 4.15 / 9.80. The difference is one pose, (75,165,-90), which
  jams with metal at -1.44. The sweep (10:24-10:31) ran under the superseded jam -> lost rule, and the model now keeps
  that pose as a contact. So the PHI 35 pick was selected under a rule that flattered it by 0.5 fast points. That is
  inside fast-sweep noise, and the claim-bench number was read under the current, stricter rule.

**In-band (question 1).** Relay metal is 303 samples per pose. Almost all are the shell underside: about 2 mm arc x
2 mm s, with 7 rows over the 12 mm width, roughly 1.1-1.2x the kit density. A few are bracket samples. The carriage
samples are NOT counted in-band. 99.5 % of the relay samples are in band, which lifts pooled ib14 from 0.8962 to
0.9196. The family's rule counts every part pooled, which gives 14.02. The pre-registered gate reads chain-only and is
the more conservative number, 14.40. Both reproduce. At kit density the shell's weight in the pool would change by
< 0.002 ib14, so neither number is inflated by over-sampling. The gate does not depend on relay samples at all.

## R2 - fold margin th measured from the member frames (own state, every taken pose)

Method: th = angle(u1, R2 u3) from M.T. In a forced (K-driven) state the margin is the minimum over the K sub-dyad and
the effective dyad; otherwise it is the plain dyad. I measured it on every taken pose, clip and ws, relayed or not.

| wear | taken | min th margin | < 5 | relayed: min | phi 0: min | forced: min | state A: min |
|---|---|---|---|---|---|---|---|
| Bench(110,360) exact | 395 | **5.000** | 0 | 5.000 (23) | 5.181 | 5.000 (186) | 5.019 |
| held out exact | 933 | **5.000** | 0 | 5.000 (74) | 5.006 | - | - |

The relayed poses sit exactly at the 5-deg margin. That is expected: the least-phi relay turns only until the lead's
gates pass. It is legal under the one-metric rule (>= 5), but these poses have no margin left. The lowest poses are
forced and relayed, at th 106.68 deg. On both benches no clip frame is relayed.

## R3 - continuity (own flood, 2-deg slerp, least-phi relay at every frame)

The grid is the 15-deg workspace envelope, 1432 poses. 1189 close kinematically, 154 of them with a relay. There are
3039 grid edges and 26060 slerp frames. 3036 edges close at every frame. Edges that fail a limit: 21 with a relay step
> 10, 0 with a passive step (dK, qa, qb) > 10, 30 with an active step > 10 (18 of those > 25), and 0 with a branch
change (no stretched <-> folded state inside an edge).

| flood | seeds (phi 0, state A) | connected nodes | bench: static -> connected | held: static -> connected |
|---|---|---|---|---|
| kinematic, family limits (passive 10, active 25) | 513 | 1188 | 285 -> 285 | 731 -> 731 |
| kinematic, STRICT (every joint and passive <= 10) | 513 | 1188 | 285 -> 285 | 731 -> 731 |
| contact-aware, strict; nodes = poses TAKEN on Bench(110,360) + held (107 unmeasured feasible nodes kinematic-only) | 502 | 1123 | 285 -> 285 | 731 -> 731 |
| contact-aware, strict, unmeasured nodes BLOCKED | 461 | 1016 | 285 -> 285 | 731 -> 731 |

**Connected = static under every reading.** No taken ws pose is dropped, relayed or not. The claim's continuity
statement holds.

## R4 - held out (the lead family's disjoint held-out bench, exact, never searched)

| reading | claim | mine | lead (same harness, same held bench object) |
|---|---|---|---|
| plain | 18.01 | **18.01** (ib14 0.9187) | 22.38 (ib14 0.9000) |
| GATE (chain-only 0.8950) | 18.51 | **18.51** | 22.38 |
| near-touch 1 mm pooled / chain-only | 23.19 | **23.19 / 23.69** | 25.23 |
| reach (ws 952) | 0.7679 (731) | 0.7679 (731) | 0.6922 (659) |
| contacts | share 0.048 | 47 poses (share 0.048) | 14 poses (0.016) |
| overhead | 18 / 71 | 18 / 71 | 18 / 71 (lead verifier) |

Relayed held poses: 110. 74 are taken, 32 are in contact and 4 jam (phi max 34.9). About 29 % of relayed poses put
metal in the skin, the same rate as on the bench (9 / 33).

**Paired held out.**
* The claim takes 657 of the lead's 659 ws poses, plus 74 relayed ones. The lead takes 2 non-relayed poses the claim
  loses (to the bump or the hardware). Exact McNemar: p = 7.7e-20.
* Contacts are 47 vs 14, with summed depth 190.6 vs 61.0 mm.
* Bench -> held inflation is +4.11 for the claim and +4.10 for the lead. The gain over the lead holds out of sample
  (-3.87 gate). The relay buys no overhead: 18 / 71 for both.
* The lead side by side reproduces its verified held number, 22.38, exactly.

## Adversarial questions inside this lens

* **(2) The rigid bump.** Its amounts come only from the fit bench: `bump_amounts(S["M1"], ...)` reads the Bench(60,160)
  kin_ok poses at phi 0. They are never set from Bench(110,360) or held out (checked in code).
  - Is the bump rigid? The model displaces each bumped point radially about a_r in the carriage frame, recomputed per
    pose. Seen from the member's own frame, that direction spreads by at most 4.5 deg on the E strap, 2.9 on the boss
    and 10.5 on the knee link, over the fit poses.
  - Member 3 turns at most 8.3 deg relative to the carriage and the knee link 38 deg. The pad reads 0.0, which is the
    sanity check.
  - Result: the gap between the model's "rigid" bump and a truly rigid part is at most 0.42 mm (p90 0.21) on the E
    strap, 0.20 mm on the boss and 0.33 mm on the knee. It is real but small, and it is not measured on the claim
    bench's extreme poses.
  - The 6 boss / knee near-jams at 0.94-0.99 mm sit within that error of the 1 mm floor.
* **(3) The rule changes.** The jam -> contact precedence makes the score WORSE (15.62 -> 16.82 at the pre-registered
  config), so it is not flattering. The exact annular clearance treats the slotted shell as solid and stays
  conservative for the shell. The pre-registered config still fails: 20.59 with the spec bump and 16.82 with the
  refined bump.
* **(4) PHI 35 vs PHI 30.** The pick came from the fast-sweep winner. Bench(110,360) was read for the pick once, plus two
  diagnostic probes. Those probes were not used to replace the claimed config.

## Verdict (RE-MEASURE lens)

**Not refuted. The claimed numbers reproduce exactly.**

* Margin-5 frozen exact gate gap 14.40 (plain 14.02, near-touch 17.68 pooled / 18.06 chain-only), against the claim's
  14.40 / 14.02 / 17.68: a difference of 0.00.
* Min th margin 5.000 on every taken pose, bench and held, with 0 below 5.
* Connected = static under the strict and the contact-aware floods.
* Held out 18.51 gate / 18.01 plain, reported as is.

Against the verified 3-joint lead (conecut-knee 18.28 / held 22.38, re-measured here side by side), the bench gain is
-3.88 and the held gain -3.87 (18.51 vs 22.38; plain -4.37). It is paid in contact: 13 vs 4 contacts on the bench, and the relay puts metal in
the skin on about 29 % of relayed poses. Near-touch is 17.68 vs 19.92. Against freek-oracle-route (4 DOF, polished
15.40, held 20.50), it is -1.00 on the bench and -1.99 held, but in-sample bench differences below 1 point are noise
(freek's polish verification). This is a 4-DOF answer at complexity 52.5. Even confirmed, it is not the headline lead
(user 2026-10-17).
