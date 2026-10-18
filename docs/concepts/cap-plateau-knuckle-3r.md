# cap-plateau-knuckle-3r - Cap-pole slaved knuckle 3R (round 14, pick 2: the cap-seat lens gate 0)

The lead's slaved-knuckle chain (J1 -> link 1a -> K -> link 1b -> J2 -> link 2 -> J3) moved to the posterolateral cap
pole: J1's O20 hub on top of the shoulder over the lateral scapular spine / posterior acromion. Three cells of the K law:
A (routed U-law, a2 70), B (short stop A, one-sided plateau), C (two-sided dwell: K opens on the folded side too).
3 active DOF (J1, J2, J3), K slaved (passive R, set by the law), knee pins outside the count, 0 passive translations.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Run the CONTROL first, in the same instrument and at the same margin. The cap seat's case rests on kinematic
     counts (C 275, B 271, A 295) set against the lead's "269-271". But that ceiling is a real-model number, with the J3
     stop and metal included. The lead's seats and law have to be counted kinematically in the same instrument, at the
     same margin, before the cap's surplus is believed.
   * Count the K play inside the fold margin (m = 5 + 0.23 deg), not after it. The lead's held margin is 5.006, so
     the play is the binding item.
   * Bound before searching. Metal only removes takes, so the kinematic count over each cell's whole sweep box is a hard
     ceiling on reach. If that ceiling is below the 279-take bar everywhere in the box, no CMA on metal can rescue the
     cell, and the convergence gate is replaced by a proof by bound.
   * Red-team cell C's folded lobe for feel. As J3 passes under J1 (th 9-12), J1 has to spin at ~1/sin(th) per unit of
     arm motion.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path behind
   Bench(110,360) (tools/concept_bench.py), plus the per-pose J1 / K / J2 / J3 axes in the scapula and humerus frames
   (the model's own body transforms). The proposers' pile-up proxies (scratchpad capseat/m.py, o.py, n.py) are digests
   and are used only to read their configurations.
3. **Methods and tools.** The fold-ceiling paired kit (docs/research/fold_ceiling/kit_paired.py: O20 hubs, K3-march
   skin-fitted 3 x 12 mm straps, the neck to BOTTOM, K2 dense continuity, K6 part collisions, exact signed distance),
   with only the K law replaced per cell. The frozen protocol: fit on Bench(60,160) fast, wear Bench(110,360) EXACT. A
   vectorised kinematic box scan for the ceiling. A finite-difference J1-rate probe on the low-th poses. Compute is
   local only, niced, with <= 2 processes.
4. **What, other than me, shows the number is right.**
   * The CONTROL: the lead's seats and law in the same instrument, worn the same way. The comparison is paired: same
     omissions (no drive metal, no cuff knee), same margin.
   * The bench (fast, then exact frozen).
   * The round-102 judge's reproduced kinematic counts (A 295, C 275 at m 5).
   * The adversarial verifier.
   * The red-team list: rest, overhead (elev >= 140), across the body, behind the back, and the low-th poses of cell C's
     folded lobe.

## Instrument and honesty

The fold-ceiling paired kit (docs/research/fold_ceiling/kit_paired.py) is used with only the K law replaced
(docs/concepts/models/cap-plateau-knuckle-3r.py `build`). It has:

- O20 hubs (12.25 mm stack, cap discs);
- K3-march skin-fitted 3 x 12 mm Ti straps, with link 2 over link 1a and the neck;
- the 14 x 6 neck to BOTTOM;
- K2 dense continuity and K6 part collisions;
- the exact signed distance of every metal sample;
- the fold margin read on th = angle(J1, J3) at m = 5 + 0.23 deg (K play inside the margin);
- K's own dyad with both stops >= 5 deg from its folds.

It does NOT have the K drive (all cells are ghosts, with K set by the ideal law) or the cuff knee (every axis passes
through GH). The CONTROL is the lead's seats and law in the same model. It reproduces the round-102 judge's control,
26.24 fast at q 0.97 (judge: 26.27). It is the only number this row is compared with: the kit omits the same things in
both arms, and it sits ~15 points above the lead's verified 18.28, because the real lead carries the J3 dowel, the knee
and the near-touch-tuned metal.

## Gate 0, kinematic half (fold + closure + K dyad; metal only removes takes) - Bench(110,360), m 5.23

| cell | ws taken / 360 | clips / 110 | overhead / 28 | min th margin | a1e range |
|---|---|---|---|---|---|
| A U-law (a2 70) | 294 | 98 | 17 | 5.28 | 40-62 |
| B short stop A | 270 | 110 | 16 | 5.24 | 31.2-56.0 |
| C two-sided dwell | 275 | 110 | 18 | 5.29 | 28.0-52.5 |
| CONTROL (lead seats / law) | **277** | 110 | 14 | 5.24 | 37.6-58.4 |

**New: the cap seat has no kinematic surplus over the lead's knuckle.** At the back-of-shoulder seat, the lead's own
knuckle law already takes 277/360 kinematically. That beats cells B (270) and C (275) at the cap. The cap's "surplus"
(281 plain at the cap vs 250 plain at the back seat) is the plain 3R's: the knuckle at the back seat already recovers
it. Only cell A's a2-70 U-law clears the 279-take bar (294). It pays with hub 2 and with the overhead clip (98/110
clips), as below. The "back-of-shoulder ceiling 269-271" is a REAL-MODEL number (J3 stop + metal), not a kinematic one.
So the cap proposals compared a kinematic count against a metal count.

## Real-model numbers (paired kit; fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) EXACT)

| config | fast plain | frozen exact plain | near 1 mm | ws taken | why (fold / parts / contact) | overhead | in band: hub K / hub 2 / link 1b / link 2 | depth max |
|---|---|---|---|---|---|---|---|---|
| CONTROL, q 1.0 | 74.45 | 80.98 | 80.46 | 275 | 83 / 0 / 2 | 12/28 | 0.00 / 0.00 / 0.00 / 0.01 | 7.68 |
| C proxy config, q 1.0 | 96.65 | 98.76 | 97.20 | 269 | 85 / 0 / 6 | 14/28 | 0.00 / 0.04 / 0.00 / 0.00 | 63.94 |
| **CONTROL, q 0.97** | **26.24** | **33.19** | 33.43 | 260 | 83 / 3 / 14 | 7/28 | 1.00 / 0.86 / 0.95 / 0.46 | 14.40 |
| C proxy config, q 0.97 | 39.43 | 43.77 | 43.10 | 240 | 85 / 25 / 10 | 7/28 | 0.75 / 0.98 / 0.68 / 0.30 | 16.48 |
| B proxy config, q 0.97 | 44.98 | 47.76 | 48.49 | 235 | 90 / 17 / 18 | 5/28 | 0.57 / 0.79 / 0.58 / 0.55 | 15.65 |
| A routed U-law, q 0.97 | 75.47 | 76.59 | 72.95 | 259 | 66 / 8 / 27 | 3/28 | 0.35 / **0.04** / 0.24 / 0.44 | 16.33 |
| C search best (stream 1, 61 tries) | 29.64 | 34.25 | 31.85 | 247 | 83 / 18 / 12 | 8/28 | 0.91 / 0.98 / 0.90 / 0.47 | 15.12 |

- q = 1.0 (the kit default) puts every hub at the worst fit pose's level. In the cap cell C, J3 at wdir(100, -4)
  points up the arm, and on overhead poses its ray grazes the neck. Hub 3, link 2 and the neck end up 150-250 mm out,
  and the overhead folded-lobe poses (209 / 211 / 238 / 265, elevation 150-165) go 30-64 mm into the skin: the
  1197 g, 98.76 reading. q 0.97 (the judge's control setting) lets the 3 % worst fit poses be charged as contact. It
  is the comparable setting.
- Cell A reproduces the routed kill: hub 2 is 0.04 in band, follow 0.85 and contact 0.071. The exact J2-RAY exit is
  modest (ws p50 58, p90 67.7, p95 70, 11 / 294 > 75 mm). The hub's level is set by its O20 disc samples (10 mm off
  the ray) at the q 0.97 quantile, not by the ray. A hub-2 one-level test on the ray alone reads 260 ws clear at level
  66 mm with 0.86 in band. So even the optimistic ray loses 34 kinematic takes to a single level, against the gate's
  <= 10. Cell A is dead on both halves.

## Search (cell C, the best proxy) and the equal-effort red team of the pairing

The search is a (1+1) local search inside the pre-registered box (model `search`), with every bound a hard edge, on
Bench(60,160) fast with the 1 mm near-touch objective. There are four streams, 344 tries:

- C1, 61 tries from the proxy config;
- C2 and C3, 101 each, from the running best;
- C4, 81 tries from the kinematic-best config of the box (299/360), run alongside C3.

The CONTROL got the same search, 101 tries, in a box of the same widths around the lead's seats
(docs/concepts/verify/cap-plateau-knuckle-3r_control_search.json). Without that, the pairing would compare a searched
cell against an unsearched control.

| config | tries | fast plain / near 1 | frozen exact Bench(110,360) | held out (exact) | ws taken bench / held | why bench (fold / parts / contact) | overhead bench / held | T5 contacts / depth sum bench, held |
|---|---|---|---|---|---|---|---|---|
| **C best (C2)** | 162 | 27.13 / 25.42 | **32.08** (reach 0.686, ib14 0.823, follow 0.982, contact 0.030) | **35.16** | 247 / 636 of 952 | 85 / 19 / 9 | 9/28, 23/71 | 11 / 34.8 mm, 36 / 86.3 mm |
| C3 (best fast near 25.00) | 263 | 26.38 / 25.00 | 32.73 | - | 248 | 84 / 17 / 11 | 9/28 | - |
| C4 from the 299-kin config | 81 | 29.27 / 29.47 | - | - | - | - | - | - |
| **CONTROL searched** | 101 | 22.98 / 22.99 | **30.59** (reach 0.719, ib14 0.814, follow 1.0, contact 0.039) | **34.03** | 259 / 660 of 952 | 86 / 0 / 15 | 7/28, 17/71 | 15 / 68.9 mm, 41 / 201.3 mm |

- **Paired at equal search effort, C is +1.49 frozen and +1.13 held out WORSE than the control.** Its fast number is
  worse too (25.0 vs 23.0 near-touch).
- Against the lead it is worse still: its real-model number is ~14 points above the lead's 18.28, because the kit has
  no knee re-centring, no J3 dowel and no tuned metal. The 1.1-1.5 point paired deficit stands on top of that.
- **Pre-registered gate 0 FAILS on the takes half.** C takes 247 / 360 on the real model (275 kinematic at this
  config), with ib14 0.823 and 9-11 contacts. The bar is >= 279 takes at ib14 >= 0.88 with <= 4 contacts.
- The paired clause (> 3 worse) is not triggered. The kill is the takes bar plus the drive: cell C's two-lobe K drive
  does not exist, so this is a ghost.
- **Convergence gate (C, 344 tries in time order, near-touch objective, score points):** gain over the second half
  0.07 (< 1), over the last third 0.00 (< 0.5), top-5 spread 0.00 (< 3). PASSED. The plain-gap view is 0.57 / 0.32 /
  0.33. The pick for the frozen wear was C2's best: of the three stream bests, it was the best on frozen exact (34.25 /
  32.08 / 32.73). That makes it a wear-bench selection, so 32.08 is optimistic by the pick, and held out (35.16) is
  the claim.
- **The box holds more kinematic takes than the search keeps.** A 4000-config kinematic scan of C's box reaches 299 /
  360 with 110 clips, and 1260 of the configs reach >= 279; B's box reaches 289. But the metal search walks away from
  them: the C4 stream started at 299 ended at 29.5 near-touch, at a2 45 and el1 63, back at ~275 kinematic. **The
  extra kinematic takes are bought with metal**, the proximity atlas's rule: a rigid part must clear the highest skin
  it ever passes over.
- **The limiter, measured:** fold 83-85 (the same as the control's 86), plus **link 2 x neck part collisions, 17-19 on
  the bench and 53 held out (control 0 / 3)**.
  - With J3 up the arm (d3 ~100), the neck to BOTTOM starts high on the lateral arm, and link 2 sweeps across it
    under axial rotation.
  - Per-pair K6 on the fit bench finds link 2 x neck as the ONLY colliding pair.
  - Adding hub K to link 2's `over` list changes nothing (32.08 -> 32.08).
  - On held out C has 17 FEWER fold losses than the control (231 vs 248) and 6 more overhead takes (23 vs 17 / 71).
    The link-2 sweep over the neck spends that and more.
- **Contact depth (T5, reported only):** C's contacts are shallower than the control's: bench 34.8 vs 68.9 mm summed,
  held 86.3 vs 201.3. The deepest is pose 211 (plane 0, elev 165, axial 15) at -16.1 mm on both.

## Red team

- **Feel near the fold (judge addition 1).** On cell C's folded lobe, J1 turns **9.6 deg per deg of arm rotation at
  th 9.3** (pose 256) and 6.8 at th 11.6 (pose 178), against ~1 in the bulk. Unpowered, the wearer would feel J1's
  inertia whip as J3 passes under J1 overhead. Powered, it is a near-singular joint-rate demand. The preview shows the
  same as a 27-deg joint jump between consecutive loop frames.
- **The pose that jams / pinches.** Pose 211 (plane 0, elev 165, axial +15) puts metal 16.1 mm into the skin in both
  arms of the pairing. Pose 208 (elev 135) is -4.1 mm on C and -11.7 mm on the control. The cap seat does not clear the
  scapular-plane overhead binder.
- **The optimistic numbers.**
  - The kit has no K drive metal. Cells A and B would borrow desmo-conecut's drive, which costs the leaders ~2-5
    frozen points. Cell C needs a two-lobe drive that does not exist.
  - The kit has no cuff knee: every axis goes through GH, so there is no drift.
  - So every cap number here is a lower bound on the real design's gap.
  - The proposers' proxies (C 22.54, B 26.82 vs the lead 16.76 "on the same instrument") were one-level pile-up
    estimates. On the real model the cells read 39.4 / 45.0 fast at their proxy configs, and the control reads 26.24.

## Verdict

**DEAD (gate 0, pre-registered).** The cap-pole lens is closed:

- **A** fails hub 2: 0.04 in band, follow 0.85, frozen 76.59.
- **B** fails the takes: 270 kinematic, frozen 47.76 at its proxy.
- **C** fails the takes: 247 real-model at the converged best, frozen 32.08 / held 35.16, and it is a ghost.
- C is +1.5 frozen / +1.1 held behind the lead's own seats in the same instrument at equal search effort.

The kinematic counts that motivated the lens compared the cap knuckle (kinematic) against the back-seat knuckle's
real-model ceiling. In the same instrument, the back-seat knuckle is at 277 kinematic, above B and C.

## Files

- Model: docs/concepts/models/cap-plateau-knuckle-3r.py (`kin`, `fit`, `frozen`, `held`, `j2exit`, `jrate`, `search`,
  `levels`).
- Sweep (every try in order): docs/concepts/sweeps/cap-plateau-knuckle-3r.json.
- Per-pose dumps (bench + held, both arms of the pairing): docs/concepts/verify/cap-plateau-knuckle-3r_*.json.
- Preview: docs/concepts/viz/concepts/cap-plateau-knuckle-3r.js (cell C best).

## Audit (2026-10-18, death audit; the death STANDS)

The audit tried to refute the death in three ways: the convergence gate, the model code, and the limiter attribution. It
also re-ran the claim. Everything was local, niced and single-process. Scripts are in the auditor's scratchpad; the
upper-bound per-pose dump is docs/concepts/verify/cap-plateau-knuckle-3r_audit_ub_l2neck.json.

**Reproduction.** The frozen C2 best was re-worn on Bench(110,360) EXACT through the model's own `frozen` path (fit
Bench(60,160) fast, shape frozen). It reads **32.08** to the digit: reach 0.6861 (247/360), follow 0.9818, ib14 0.8232,
ib10 0.5234, contact 0.0301, why fold 85 / parts 19 / contact 9. The kinematic count also reproduces: 275/360 ws,
110/110 clips, overhead 18/28.

**Convergence gate.** Recomputed from the sweep over the 344 search rows in time order:

- Near-touch objective: 0.073 / 0.004 / 0.004 score points (second half / last third / top-5 spread). PASSED.
- Plain gap: 0.57 / 0.32 / 0.33.

The pass is weaker than it looks. The search is a (1+1) local search, and C2 and C3 continue from the previous
stream's best, so the top-5 configs are neighbours of one point and the spread is degenerate. The only independent
start is C4, from the 299-kinematic config, and it ended worse (29.47 near-touch). Together with the box ceiling and the
metal walk-back, the evidence still says the cell has no better basin. The gate is not what carries the death.

**Model and convention checks (no bug found).**

- The fold is read on th = angle(J1, J3) at m = 5 + 0.23, the same as the control and tools/concept_kit.py.
- K's own dyad stays >= 5 deg from both of its folds by construction.
- Both arms share the same kit, q search range and omissions.
- Near-edge parameters: el1 66.59 (box edge 67) and lo 26.38 (edge 26). But 80 of the 85 fold losses sit on the
  stretched wall, th > cap + a2 - m = 95.3 deg. lo does not move that wall, and the interior a2 / cap optimum shows
  the box is not binding there.

**Lobe slack (a candidate lever, measured small).** The folded lobe's slack, lo + f - a2 - m = 6.53 deg, loses th in
[5.23, 8.50]. Kinematically that is 2 ws poses. Setting it to 0 puts every lobe pose exactly on the fold boundary,
which is numerically ill-posed. It is not a lever.

**The lobe the death calls a ghost carries real takes.** On the folded lobe there are 33 kinematic and 19 real-model
bench takes (of 247). The law without the lobe (f = None) takes 260/360 kinematic, against 275. So the buildable,
one-sided version of C is about 4-5 points WORSE than 32.08. The ghost drive flatters C; it does not hide a better
design.

**The buildable one-sided C, measured (re-dispatch 3, 2026-10-18 08:15 UTC).** The estimate above is now a number. Cell
C's best config (C2) with the one-sided law (f = None, the class desmo-conecut's drive builds), shape re-fit on
Bench(60,160) fast (29.32) and worn frozen:

| | ghost two-lobe C2 | one-sided C2 (buildable class) | lead-seat control |
|---|---|---|---|
| kinematic ws | 275/360, clips 110/110 | 260/360, clips 108/110 | 277/360 |
| frozen exact Bench(110,360) | 32.08 (247 takes) | **35.38** (241 takes, ib14 0.797, overhead 8/28) | 30.59 |
| held out | 35.16 (636/952) | **37.93** (614/952, follow 0.965, overhead 21/71) | 34.03 |
| T5 bench / held | 11 / 34.8 mm; 36 / 86.3 mm | 7 / 24.8 mm; 16 / 29.0 mm | 15 / 68.9 mm; 41 / 201.3 mm |

The lobe is worth 3.30 frozen / 2.77 held. The buildable cap knuckle sits **+4.79 / +3.90 behind** the lead's seats in
the same kit (not re-searched with the one-sided law; the take bound, 260-270 kinematic < 279, holds either way).
Per-pose dumps: docs/concepts/verify/cap-plateau-knuckle-3r_{frozen97,held}_C2onesided.json.

**The limiter attribution, corrected (new).** The worn shape was re-run with ONLY the link 2 x neck pair exempt from
K6. Everything else was unchanged: the fit, the over-lift, every other pair and the exact signed distance. The result
is an upper bound for any re-routing that removes that collision:

- Frozen exact reads **35.65** (WORSE than 32.08). Parts fall 19 -> 5 and contacts rise 9 -> 23; reach is unchanged
  at 0.6861.
- All 14 poses the exemption frees already have metal in the skin: -0.34 to -10.77 mm. Six are overhead (elevation
  150-165) and pose 238 is the deepest.
- So link 2 x neck is not what loses those poses. Skin proximity at the cap seat with J3 up the arm loses them, and
  clearing the part collision recovers 0 takes.
- The row's limiter should read: fold 85 (stretched wall, th > 95.3) plus skin proximity on the overhead /
  scapular-plane poses where link 2 crosses the neck.

**Verdict of the audit: the death STANDS.** The measured reason, in one line: at the converged best (reproduced at
32.08 frozen exact, 247/360 takes), 80 of the 85 fold losses are on the stretched wall th > 95.3. The 14 poses behind
the link 2 x neck collisions are skin contacts anyway (exempting the pair gives 35.65), and 19 takes need the two-lobe
drive that does not exist. So no fix inside this cell reaches the control (30.59), let alone the 279-take bar or the
lead (18.28).

The task's refutation bar ("within 10 of the champion's 68.93 on Bench(60,160)") is a round-3 criterion. Every row since
round 4 clears it, and so does this one (27.13 fast). It does not test this death, which is measured against the
pre-registered gate 0 and the paired control.

## Audit 2 (2026-10-18 06:55 UTC, second death audit; the death STANDS)

This was a duplicate dispatch, so the audit was kept to cheap, independent checks. Everything ran local, niced and
single-process.

- **Reproduced again.** The C2 best, worn frozen on Bench(110,360) EXACT through the model's `frozen` path, reads
  **32.08** to the digit. That is 247/360 takes (fold 85, parts 19, contact 9), overhead 9/28, min metal -16.106 mm,
  in 129 s. The fast fit reads 27.13 and the kinematic count 275/360.
- **Gate.** Recomputed from the sweep over the 344 cell-C search rows in time order:
  - near-touch: 0.073 / 0.004 / 0.004 score points. PASSED.
  - plain gap: 0.567 / 0.316 / 0.331.
- **Claim selection.** Three C configs were worn on the claim bench: k 165 at 34.25, k 167 at 32.08 and k 349 at 32.73.
  The row reports the best of the three, which flatters C. The fast-best config (C3, k 252, near-touch 25.00) wears
  worse frozen (32.73), so the pick does not hide a better design.
- **Box edges (new).** The two parameters that sit at the box edge are held there by measured cliffs, not by the box.
  Fast Bench(60,160) gap, everything else at the best:

  | el1 (best 66.59, box edge 67) | 65.0 | 66.0 | 66.59 | 67.0 | 68.0 | 69.0 | 72.0 |
  |---|---|---|---|---|---|---|---|
  | gap | 28.46 | 28.02 | **27.13** | 29.95 | 32.95 | 141.47 (follow 0.30) | 164.26 |

  | lo (best 26.38, box edge 26) | 27.5 | 26.38 | 25.5 | 24 | 22 |
  |---|---|---|---|---|---|
  | gap | 28.94 | **27.13** | 132.27 (K6 collide 0.52) | 134.06 | 131.43 |

  Kinematic takes stay at 274-276/360 across both scans. Opening the box gains nothing.
- **Robustness (new red-team item).** Two cliffs sit close to the best:
  - **lo**, the K law's floor (a drive or cam tolerance), is 0.9 deg above a part-collision cliff. At lo 25.5, K6
    collisions hit 0.52 of the poses and the gap reads 132.
  - **el1** is ~2.4 deg below a follow cliff: at 69, follow drops to 0.30.

  J1 seat errors cost points too:
  - el1 +0.4 / +1.4 deg cost 2.8 / 5.8 fast points;
  - az1 +-1.5 deg and d3 +-1.7 deg cost 0.6-2.2.

**The death stands.** The measured reason, in one line: at the converged best (32.08 frozen exact, reproduced twice,
247/360 takes) 80 of 85 fold losses are on the stretched wall th > 95.3. The box edges are pinned by collision and
follow cliffs, not by the box. The 19 lobe takes need a two-lobe drive that does not exist. So no change inside the
cell reaches the paired control (30.59), the 279-take bar or the lead (18.28).

The task's literal bar, "within 10 of 68.93 on Bench(60,160)", is met by the original claim (27.13 fast), as audit 1
noted. That bar is stale from round 3 and does not test a gate-0 death against the lead.


## Audit 3 (2026-10-18 08:50 UTC, third death audit; the death STANDS)

Audits 1 and 2 had already reproduced the ghost claim (32.08) twice, so this audit tested the two regions nobody had
searched. Everything ran locally, niced, with at most 2 processes. All 343 evaluations are appended to the sweep (rows
k 351-693: sources `audit3_*`).

- **Reproduced.** At the C2 config the fast fit reads 27.13 (ghost) and 29.32 (one-sided re-fit), both to the digit.
- **The other branches (new).** All 351 earlier tries used sigma -1 (J2's side of the J1-J3 plane) and sK -1 (K's
  elbow).
  - At C2 the other branches read:
    - sigma +1: 154.82;
    - sK +1: 143.09;
    - both +1: 157.42.
  - K6 part collisions hit 0.58-0.61 of the poses, with follow 0.28-0.32.
  - A 140-try (1+1) search on sigma +1, started from C2, reaches only 70.16 near-touch / 72.37 plain, with hub 2 out
    of band. Its gate reads 0.41 / 0.29 / 0.19.
  - The mirror J2 branch is not a hidden basin.
- **The buildable law, searched (new).**
  - Setup: cell C's one-sided law (f = None), the class desmo-conecut's drive builds. The doff box was opened to
    5.24-8 to match the control's law. 200 tries from C2 on Bench(60,160) fast, near-touch objective. Gate: 0.35 /
    0.04 / 0.04 score points.
  - Best fast: 27.70 near-touch. The worn pick, k 166, reads 27.80 near-touch / 27.02 plain.
  - **Frozen exact Bench(110,360): 33.94.** Reach 0.6806 (245/360), ib14 0.799, follow 0.991, contact 0.019; why fold
    96 / parts 12 / contact 7; overhead 7/28; min metal -16.29 mm.
  - It sits **+3.35 behind the same-kit control (30.59)** and +15.7 behind the lead (18.28).
  - The search recovers 1.44 of the un-searched one-sided 35.38. It does not close the 3-point lobe loss.
  - Held out was not worn (time box).
- **The optimum sits on a cliff (red team).**
  - The one-sided best lies at the box edges, cap 56 and el1 67. Both are 1 deg from a K6 collision cliff:
    - cap 57: 141.36 (collide 0.64);
    - el1 66: 133.37 (collide 0.57);
    - cap 58-62: >= 134.
  - Opening the cap box, which would raise the stretched wall th > cap + a2 - m, is not a lever.
  - A drive or cam tolerance of +1 deg on the K cap would collapse it.
- **Bookkeeping.**
  - The claim's n_configs (353) did not match the sweep (351). The one-sided re-fit was not appended. The row now
    reads 694, the sweep length after this audit.
  - The literal refutation bar, "within 10 of 68.93 on Bench(60,160)", is met by every row since round 4 and does not
    test this gate-0 death.

**Death stands.** The measured reason, in one line: the buildable one-sided cap knuckle, searched and worn frozen, reads
33.94 on Bench(110,360) exact. That is 245/360 takes, with the fold losing 96 on the stretched wall. It is behind the
same-kit control (30.59) and the lead (18.28). The mirror J2 / K branches collide (>= 70 fast). The cap / el1 optimum
sits 1 deg from a K6 collision cliff.
