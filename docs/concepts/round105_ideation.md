# Round 105 (J5, track jump) ideation: judge and red team (2026-10-18 ~10:10 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. The plan is docs/concepts/ROUNDS.md "Round 105 plan" (commit 94950ee).

**Lead to beat:** conecut-knee-knuckle-3r, verified 18.28 (score 93.35), frozen exact Bench(110,360), held 22.38.

- Reach 0.7278 (262/360), ib14 0.9012, contact 0.0106 (4 poses).
- Complexity 18.5, ledger WATCH.
- **Every claim's bar is 18.28.**

**Candidates:** nine came in.

- Lens A (carriage relay rail): 3.
- Lens B (seat oracle at the ER wall): 3.
- Lens C (desmo drive geometry): 3.

All of them map every joint to a real part, and all have 0 passive translations.

**Outcome: four picks** (section 4).

- Two lens-A ideas are rejected as DEAD at step 0. Their proposers measured that themselves, and the judge reproduced it.
- The two lens-B oracles are merged into one instrument.
- The three lens-C desmo cells are merged into one row: cell B, plus cell A and a Ti-groove probe.
- The lead-side seat move (acroant) stays a separate design row.

**Judge's data.** Every number below comes from a saved file. The judge ran no bench (box load ~10 on 4 cores) and did
JSON re-reads only:

- Proposers' maps and dumps: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/cr/`
  (window_s95.json, plain.py, track.py) and `.../scratchpad/kf/` (p*_t*_a*_s*.json, read2.py).
- The armarc ideal and hardware dumps: `docs/concepts/verify/armarc-relay-knuckle-4r/*.json`.
- The verified per-part in-band tables: `docs/concepts/verify/desmo-{conecut,window,slipper}-knuckle-3r_v_{bench,held}_frozen*.json`.
- The judge's own scripts: `.../scratchpad/judge105/track_fix.py` and `plain_a10.py`.

## 1. Red-team checks made by the judge

### 1.1 proxtrack: the arm-fixed track's own skin hits were counted as lost poses, not contacts

`track.py` (the 2-mm reading) drops every taken pose whose track band is under 2 mm, and that includes poses where the
track is INSIDE the skin:

- (150,105,-105) at -12.1 mm, at every PHI >= 30;
- the four elevation-0 aliases of one ER orientation, (150,0,-60) = (30,0,60) = (120,0,-30) = (15,0,75), at -4.2 mm at
  PHI 35.

The track is fixed to the arm, so no stop can refuse those poses: they are contacts. `plain.py` counts them correctly.

Corrected 2-mm reading (track < 0 = contact, track 0-2 mm = lost, relayed chain < 2 mm = lost as the planner rules):

| track pre-arc a | PHI 25 | PHI 30 | PHI 35 | PHI 40 |
|---|---|---|---|---|
| 12 (proposer's map) | 15.20 | 15.74 (proposer 15.48) | 16.18 (proposer **14.92**) | 18.65 (16.61) |
| 10 | 15.20 | **14.61** | 15.17 | 15.90 |
| plain, a 10 | 15.25 | 14.31 | 13.73 | 15.59 |

**What the table means:**

- Step 0 survives only at PHI 30-35, and only with the pre-arc a <= 10 deg.
- A 10-deg pre-arc is the physical floor: the 24 mm carriage spans 17.5 deg at R 78.5, so half of it is 8.8 deg, plus
  the end dowel.
- The difference between a 10 and a 12 is one 5-deg bin at the track's anterior end. That bin holds a single
  elevation-0 orientation, which the bench counts 4 times.

So the survivor stands, on a thinner margin than proposed.

### 1.2 proxtrack: the ideal path never measured in-band

Every ideal relay dump, at every PHI and on both axes, reads ib14 0.9012 to 4 decimals. That is the lead's own value,
carried over and not re-measured on the relayed poses. The real armarc hardware wears measured two things:

- chain-only ib14 0.8466 / 0.8509 (PHI 20 / 30), against 0.9012;
- 628-726 relay-metal samples at 100 % in band, which lifted pooled ib14 by ~0.04. That is the dilution pattern behind
  the auditor's strap-dilution watch.

proxtrack has no lift, but it bumps member 3's E strap and the knee link to R >= 82.7 at every pose:

- the E strap has 164 samples, 0.979 in band, mean 6.0 mm, and it rises by 4.3-8.1 mm;
- the knee has 90 samples, mean 9.7 mm, and it rises by 1-4.3 mm.

The lead has 0.0012 of in-band slack, so the judge expects -0.01 to -0.03 of chain in-band, i.e. +1 to +3 gap: **15.3-17.3**.

**Pre-registered:** the gate is read on the lower of the pooled and chain-only ib14.

### 1.3 proxtrack: folded-side relays stay in the skin

At PHI 30 there are 13 contacts against the lead's 4. They include the one-sided spring's folded-side relays 262 (-9.79)
and 206 (-6.07). The plan's step-0 item 4 (relay two-sided, or refuse on the relay's own angle) is not met. They stay
contacts, with depth on file (T5).

### 1.4 carrail-kfree: the dead verdict reproduces

`read2.py` over the five kf dumps reproduces the proposer's table:

| axis (tilt / az) | psi2 | PHI | plain | 2-mm | contacts |
|---|---|---|---|---|---|
| 12 / 237 | -14 | 75 | 15.70 | 15.92 | 29 |
| 8 / 225 | -12 | 75 | 15.91 | 16.71 | 26 |
| 12 / 237 | -9 | 45 / 60 / 75 | 19.95 / 18.26 / 18.54 | - | - |

Only the tilt-0 long axis (10.22 plain / 10.26 2-mm) is under 15, and there the skin radius spreads 20-36 mm under the
rail's sweep. The 0-mm re-read (11.11 at t12 / psi2 -14) is not a valid reading: it counts relayed contacts as refused,
and a one-sided relay cannot refuse at phi < PHI. **Dead upheld.**

### 1.5 desmo-geom: wrong baseline, same answer, and 18.28 is a ceiling

The proposer re-weighted desmo-conecut's verified per-part in-band. That table is on the CLASHING layer: stage 1 sits
inside link 1b's plate (M3). desmo-geom uses desmo-window's buildable level (insert underside F2+3.15, window in link
1b), so the right baseline is desmo-window's verified table, which carries the out-of-rim ring that killed it (29
samples, 15 % in band, mean 16.8 mm):

| baseline (frozen parts table) | ib14 as verified | ib14, ring2 removed | gap | held |
|---|---|---|---|---|
| desmo-window (buildable level) | 0.8785 / 0.8776 | **0.9004 / 0.8994** | **18.28** | **22.44** |
| desmo-conecut (clashing layer) | 0.8929 / 0.8920 | 0.8996 / 0.8987 | 18.32 | 22.51 |
| desmo-slipper (clashing layer, cell A) | 0.8909 / 0.8897 | 0.8979 / 0.8967 | 18.25 | 23.21 |

desmo-slipper reads lower than the lead here only because it has 3 contacts, not more takes.

**18.28 is the ceiling, not a central estimate.** Takes (262) and contacts (4) are the lead's, and the in-band term
saturates at 0.90. The best possible outcome is therefore a TIE on the plain gap at complexity 16.5 (a Pareto point 2
under the lead). Whether it gets there turns on 0.0004 of in-band, about 0.4 samples of 962. The crank's 133 samples (80 %
in band) move with dR and g, a bigger lever than the ring, of unknown sign.

**Other checks on the desmo cells:**

- **Robustness, by the proposer's own sensitivities:**
  - cell B: a_s +0.02 gives rc 0.40, and delta +0.05 gives 0.15;
  - cell T: delta +0.05 gives rc 0.56.
  - So the nominal optima fail the tolerance requirement the proposers wrote themselves (rc >= 1.0, or >= 1.3 for cell T,
    at a_s +-0.05 / delta +-0.05). The fit must carry it as a hard gate.
- **Friction:** cell A holds only at mu 0.087, the family standard of the verified desmo-slipper. At mu 0.15 its flank
  binds at dK 43.25, under the 47.05 the J2-first stop order needs (desmo-conecut-knuckle-3r.md, table). Cell B is the
  claim cell at mu 0.15.
- **Cell T's Hertz check reproduces.** Line contact, O1.5 pin, 25 N over 1.5 mm, E* ~81 GPa: p0 1532 MPa at rc 1.0 and
  1165 MPa at rc 1.3. But its 0.6 mm wall is a rule change from 0.8, and its rc cliff fails the corner gate, so it is a
  probe only.

### 1.6 acroant: the in-band gain is bought in the 1-2 mm shell

On the proposer's own fast numbers, near2 rises 18.16 -> 20.48 (J1 +5) -> 24.49 (J1 +10). That is +2.3 / +6.3 points
of metal within 1-2 mm of the skin, because hub 2 and link 2 ride closer to the skin. The lead already carries the T1
watch (16.56 points in that shell).

The in-band surplus (0.9192 at +10) is worth 0 on the gap. A win needs >= 2 more takes, or the two new overhead contacts
(115 at -5.25, 152 at -1.53) cleared. The plain read is flat within +-5 deg: the lead's J1 descends from the kneeless
polish's 94.35.

**Pre-registered:** the 1-2 mm shell is reported, the +0.1 / +0.2 mm probe is the ranking reading, and the run stops
if the fit returns d_az1 < 2.5.

### 1.7 seat oracle: the proxy is optimistic and the gate cannot pass

- At the k33 control the proxy reads 117 at +0.9 mm against a measured -1.14: 2.0 mm optimistic. So S1's +2.0 is about 0
  measured, and only S2 can clear 117 / 148.
- The gate (>= 279 connected takes at <= 4 contacts) fails by arithmetic in every cell. Nine overhead state-A parking
  contacts are untouched by any seat or K.
- The proxy's in-band falls 0.883 -> 0.857 -> 0.822 with az1.
- L0's dyad is legal: |26 - 55.04| + 5.5 = 34.54 <= a1 37.55 <= 75.54.
- L0 uses the kit's metal, not the lead's crank / horn / lobe (237 / 264 are drive metal). It bounds the K law, not the
  drive.

**Expected outcome: KILL, plus four table cells.**

## 2. Verdicts

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | carrail-relay-knuckle-4r | **REJECT (dead at step 0, measured)** | The posterior free window is only 15-25 deg at s -95 / -111 / -140. Every tail that can carry PHI >= 30 reads >= 27.4. Arm-low rotated poses put the tail 8.9-13.2 mm into the flank, down to -54 at tail 75. Goes in the relay row of the take-bound table. |
| 2 | carrail-relay-kfree-4r | **REJECT (dead at step 0, reproduced)** | Buildable axes read >= 15.70 plain / >= 15.92 2-mm with 26-29 contacts before any rail metal (1.4). Tilt 0 cannot carry a rail (20-36 mm skin spread). |
| 3 | proxtrack-relay-knuckle-4r | **PICK 1** | The only candidate whose expected number is under the lead, and the only one that buys reach. Corrected step 0 is 14.61 (2-mm) / 14.31 (plain) at PHI 30, a 10 (1.1). |
| 4 | seatoracle-erwall-knuckle-3r | **PICK 4 (instrument), merged with 6** | The planner's lens B; the per-seat cells feed main round 15 lens A's take-bound table. Gate expected to fail (1.7). |
| 5 | acroant-conecut-knuckle-3r | **PICK 3** | A lead-side 3-joint design move with measured step 0 on the real lead model. Low odds (1.6). Not a duplicate: main round 15 lens C excludes seat moves. |
| 6 | leadseat-longstop-oracle-knuckle-3r | **MERGED into 4** (cells L0 / L1) | Same model, same oracle, different seats: one instrument row with at most 4 cells. |
| 7 | desmo-geom-knuckle-3r | **PICK 2, merged with 8 and 9** | The planner's lens C. The judge's re-weighting on the buildable-level parts gives 18.28 / held 22.44 (1.5): a tie at complexity 16.5. |
| 8 | desmo-geom-flank-knuckle-3r | **MERGED into 7** (cell A) | Same model with the stage-2 switch the desmo-conecut model already carries. Runs in the same fit and is reported at equal samples. Holds only at mu 0.087. |
| 9 | desmo-geom-tigroove-knuckle-3r | **MERGED into 7** (cell T, probe only) | A material / gate variant. As proposed it fails its own corner gate (delta +0.05 gives rc 0.56), and its 0.6 mm wall is a rule change. Runs only after cell B passes, with RING_WALL 0.8 unless the lead rules. |

## 3. Ranking

Score = expected gain against the lead's 18.28 (all candidates take ~57-60 off the champion's 75.94) x confidence x
buildability. All four picks have 0 passive translations, so buildability ranks on complexity and on parts that exist.

| rank | id | expected (frozen exact) | P(beats or ties 18.28) | active / cx | why this rank |
|---|---|---|---|---|---|
| 1 | proxtrack-relay-knuckle-4r | 15.3-17.3 | ~0.65 under 18.28; ~0.3 pass <= 15 | 4 / 52.0 | The only expected gain (+1 to +3 points) and the only reach lever. A 4-joint answer, so it goes to the user as an option. |
| 2 | desmo-geom-knuckle-3r | 18.28-18.45 (18.28 = ceiling) | ~0.45 tie | 3 / 16.5 (T 16.0) | No gap gain; a Pareto point 2 complexity under the lead, at its number. |
| 3 | acroant-conecut-knuckle-3r | 17.6-19.5 | ~0.25 | 3 / 18.5 | The only 3-joint lead attempt, but the lead's J1 is a measured local optimum and the in-band gain is T1-shaped. |
| 4 | seatoracle-erwall-knuckle-3r | instrument (L0 16-17.5, S1 / S2 17-20) | n/a, gate expected FAIL | 3 / n/a | Decides the 3-DOF seat cells of the take-bound table and the "longer stroke on the lead" question. |

## 4. Picks (lead notes)

1. **proxtrack-relay-knuckle-4r.**
   - Test first: model the in-band of the E-strap / knee bump and of the relayed poses (the ideal path never measured
     it).
   - Set the track pre-arc at its physical floor (~10 deg).
   - Count track-in-skin as contact.
   - Gate on the lower of pooled and chain-only ib14: pass <= 15, kill > 17.5.
2. **desmo-geom-knuckle-3r** (cells B, A, T-probe).
   - Test first: the robust rc gate (rc >= 1.0 at a_s +-0.05 / delta +-0.05) with the ring still inside O20. Kill the
     cell if no start holds it.
   - Baseline = desmo-window's buildable parts. 18.28 is the ceiling.
3. **acroant-conecut-knuckle-3r.**
   - Test first: reproduce step 0, then check whether the re-fit keeps d_az1 >= 2.5 and clears 115 / 152 without
     growing the 1-2 mm shell.
   - Rank at the +0.1 / +0.2 mm probe.
4. **seatoracle-erwall-knuckle-3r** (instrument; cells L0, S1, S2, then L1 or the lead-seat control).
   - Test first: L0, the lead's seats with stop B 76.04.
   - The proxy is 2 mm optimistic at 117, and the gate fails by arithmetic.
   - The numbers go to the take-bound table, never into a claim.

**Order.** Lens C (desmo-geom) and lens A (proxtrack) can start together, at 2 niced processes each. The oracle cells
are ~10 min each and fit between them. acroant's step 0 is 5 minutes. Its result decides whether the oracle's 4th cell
is L1.

## 5. What happens next

**The 4-joint question for the user** (unchanged from J4) gets its first realisable number from proxtrack. If gate 0
passes (<= 15), the 4-joint option is ~94.5 at complexity 52. If it lands at 15-17.5, it is a coin flip against freek's
16.20 (also 4 joints, WATCH).

**At 3 joints:**

- desmo-geom can at best tie the lead at complexity 16.5;
- acroant is the only lead attempt;
- the seat oracle closes or opens the seat lever with a number.

**95 at 3 DOF stays measured out of reach** at the legal seats until main round 15 lens A's table says otherwise.

**Machinery:** the dead carrail rows need ledger / table entries (relay row), like the J4 dead rows that still have none.
