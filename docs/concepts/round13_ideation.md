# Round 13 ideation: judge and red team (2026-10-17 ~19:40 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75)
at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

**Lead to beat: conecut-knee-knuckle-3r, verified 18.28** (score 93.35; Bench(110,360) exact frozen), held out 22.38,
cx 18.5, ledger WATCH. The LEAD NOTE of 18:21 UTC (ROUNDS.md) withdrew the tie rule: the plain verified gap decides, so
this judge ranks against 18.28 / 22.38, not against slipper-nose's 18.49 that the candidates quote. The champion
spherical 3R reads 75.94 on the same bench; every candidate here is ~57 points under it, so that ratio does not separate
them.

Six candidates came in from the planner's two lenses: complexity on the conecut knee (3 cells) and the reach-hub2-seat
ghost (3 cells). All six have 3 active joints and 0 passive translations. Every joint maps to a catalogue or machinable
part (MR117-2RS / MR63ZZ pairs, ISO 8734 dowels, wire-EDM slots, a 5-axis groove). No candidate is rejected on hardware,
translations or determinacy, with one condition: the seat cells are ghosts with an ideal K law, so a real drive on their
32/48 dyad is their determinacy gate. After merges, **two picks**: three candidates merge into them and one is closed by
its own measurement. The workflow asks for four; the rules ask for merges, and six cells of two lenses make two picks.
Splitting them again would put two modellers on one harness. The box is local-only at load ~15 on 4 cores.

## Red-team checks made by the judge

Scripts, logs and JSON: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge13/`.
Each check runs the proposer's own harness or synthesis, imported unchanged, and reproduces its control first. The
held-out set was not touched: the out-of-sample check uses the envsel draw (tools/env_bench.py: seed 2, 360 fresh
workspace poses plus Bench(110,360)'s clip frames, exact path, disjoint from held out by construction).

### 1. Cell B's inverted stage 2 reproduces, and its slot works with straight walls

`inv_mu.log` (the proposer's inv_mu.py on docs/research/slipper_mechanism/geo_bench.npz, nose at C0, g 2.3934) and
`tilt.log`.

| mu | PA cap (43 - atan mu) | cell B stroke (pinned horn) | cell A stroke (flank, PA only) |
|---|---|---|---|
| 0.087 | 38.03 | 76.75 | 49.75 |
| 0.12 | 36.16 | 73.00 | 46.25 |
| 0.135 | 35.31 | 71.50 | 44.75 |
| 0.15 | 34.47 | **69.75** | **43.25** |
| 0.20 | 31.69 | 64.50 | 38.50 |

- Max PA over K 0-46.3: B horn 27.4, crank 29.5 (both at K 0); A horn 36.1. The proposer's numbers hold exactly. Taken K
  is 45.62 on the bench and 46.27 held out, so cell A fails the planner's mu-0.15 kill gate on stage 2, as its proposer
  says. Stage 1 is not the binder (forward PA 31.4, reproduced from s1fast.py).
- **The closed end is a relative pole.** The slot centreline's minimum radius of curvature is 0.13 mm, over the first
  0.09 mm of path (K 0-5). That is below the nose radius of 1.0 mm, so the swept slot is undercut there. The pocket must
  be built as the union of nose discs, and the PA and the slop read on that built pocket. The proposer's slop scan already
  uses a union of discs (0.037-0.055 deg); the PA does not.
- **No taper cut or crown is needed.** A radial nose on link 1a swings 2.19 deg in the crank frame, all of it ALONG the
  slot (across: +-0.01 deg). That is 0.001 mm of interference in a 2.5 mm plate against 0.01-0.02 mm of clearance, so a
  straight-walled wire-EDM slot works. Cell A's nose path in link 1a is 25.75 mm long (axis swing up to 11.6 deg). The
  slot B replaces is seven times longer.

### 2. Cell C's regear is knife-edged on the nose seat

`inv_g2.log` reproduces the proposer's stroke (best 52.75-54.0 at g 2.8). `inv_g28_rc.log` repeats it with the boss
clearance as a bound. Cell B's own spec gates an O6 boss at r_c - 3 >= 11, i.e. r_c >= 14.

| g | stroke at mu 0.15, r_c >= 13.5 | r_c >= 14.0 | r_c >= 14.5 |
|---|---|---|---|
| 2.39 | 70.25 (r_c 15.5) | 70.25 | 70.25 |
| 2.6 | 70.00 | 68.75 | 63.25 |
| 2.7 | 65.50 | 58.50 | 51.00 |
| 2.8 | 54.00 | **46.00** (PA max 34.6 > 34.47) | 35.75 |

- C's g 2.8 works only with the nose at exactly r_c 13.5: an O5 boss 1.0 mm from hub K's O20 rim. At r_c 14.0 it holds
  46.0 deg, under the held-out 46.27. g 2.6-2.7 keeps 58-69 deg with an O6 boss.
- Stage 1 pulls the other way (s1fast.log). At g 2.6 the smallest passing rings have forward PA 32.8-34.3 against the
  34.47 gate. At g 2.8 (a_s 10 / psi 150 / blend 18) the forward PA is 28.8, with r_out 10.79 and rc 1.36. The
  compromise is g ~2.7. C's extra ring gain (~0.1-0.2 beyond glev -1.0) sits inside the family's paired noise (~1.3).
- Ridge stress, as a line contact (440C on Ti-6Al-4V, E* 81 GPa; O1.5 pin r 0.75; L 1.5 mm; 25 N), both cells:
  - the 0.23 mm ridge (rc 0.99): 1.56 GPa;
  - C's 0.60 mm ridge: 1.14 GPa (1.4 GPa with the proposer's crowned L ~1.0).
  Ti-6Al-4V starts to yield at p0 ~1.67 sigma_y ~1.47 GPa, and DLC on Ti fails by the eggshell effect. So C's "no insert
  needed" has no margin. The 440C groove insert is the default until a static force analysis shows F_pin < 10 N.

### 3. Cell A's number decomposes as claimed; B's sample-weight cost

- **A's 18.87 matches conecut once the ring is removed.** 18.87 = reach 17.22 + in-band 0.59 + contact 1.06. Deleting
  the stage-1 ring's 19 samples (42.7 % in band) from the pooled in-band gives ib14 0.903, i.e. 18.28 = conecut exactly.
  Takes and contacts are identical, as the proposer measured (ring_rigid 0 -> 12.50 fast).
- **B pays a sample-weight cost on the bench.** Deleting the lug band and outer wall (60 samples at 0.95 in band) moves
  ib14 0.8941 -> 0.8907, +0.34. That is S6 dilution, not a design loss, and it is stated as such. So B reads ~19.0-19.2 on
  the bench before the boss / tip-plate refill and glev -1.0. It ties desmo-slipper (18.95 at cx 15.75) at +0.25 cx. Its
  case is held out (conecut's knee: 22.38 vs desmo's 23.90) and friction (mu 0.15 on both stages, where desmo jams at
  0.14 and cell A and the lead's flank bind at 43). It is not the bench.
- **The stage-1 gate is re-read, and the auditor must rule on it.** In the dwell the cap ring moves along the groove and
  pushes the pin only radially (90 deg): that is the dwell's back-drive lock. The cap ring is the driver, so the forward
  (pin-side) PA is the jam test. The physics is right. It is still a gate definition changed by a proposer, so it is
  flagged to the auditor as a measurement change.

### 4. The J3-seat lever holds on an independent draw (envsel), and the wrap seat needs its law re-tune

`envsel_wear.py` repeats the claim protocol: fit Bench(60,160) fast with the seatscan / frozen_full patches,
IB_GHOST=all, pick3's knee and law unrefit. It then wears the frozen shape on envsel, exact path. The binder region is
plane <= -55, elev 40-70, axial 90-150 (7 envsel poses).

| cell | fit gap | envsel gap | taken / 360 | contacts | binder region (7 poses) | ib14 | overhead | taken < 1 / < 2 mm |
|---|---|---|---|---|---|---|---|---|
| base (wd 66.07) | 12.17 | 21.31 | 260 | 12 | 6 contacts (to -8.46), 1 fold | 0.8961 | 6/26 | 6 / 18 |
| wd 71 | 12.69 | **19.20** | 267 | 7 | 3 contacts (259 -0.15, 260 -4.48, 264 -1.88), 3 folds, 265 taken 2.1 | 0.8845 | 7/26 | 10 / 31 |
| wd 73 | 11.48 | **18.62** | 265 | 7 | 3 contacts (259 -1.02, 260 -4.51, 264 -2.42), 3 folds, 265 taken 0.79 | 0.8960 | 7/26 | 13 / 37 |
| wd 76 / wa -18 (pick3's law) | 17.07 | 25.81 | 242 | 11 (+2 part) | 3 contacts, 255 / 261 / 265 taken at 0.10-0.62 | 0.9124 | 4/26 | 4 / 29 |

Frozen exact Bench(110,360) of the same cells:

| cell | gap | taken | contacts | source |
|---|---|---|---|---|
| base | 17.23 | 269 | 6 | proposer |
| wd 71 | 17.31 | 271 | 4 | proposer |
| wd 73 | **16.72** (score 93.92), ib14 0.896, overhead 8/28, 7 taken < 1 mm, 1 part collision; 117 / 127 taken at 0.88 / 1.13, 237 no longer a contact | 269 | 4 (129 -4.07, 139 -0.87, 264 -2.33, 316 -0.61) | judge, `frozen_judge_wd73.json` |

- **Out of sample the lever is real, and larger than on the claim bench.** On the claim bench wd 71 moves -0.08
  unrefit and wd 73 -0.51 (16.72: it keeps the base's in-band and 4 contacts, but still takes only 269, under the
  planner's 274); on envsel wd 71 moves -2.11 and wd 73 -2.69. On envsel, J3 up the deltoid takes 5-7 more poses and sheds 5 contacts (the overhead
  452 / 454 contacts get shallower too). In-band does not have to fall: wd 73 keeps 0.896 with pick3's knee, and its fit
  bench improves (11.48 vs 12.17).
- **It pays in near-touch.** Taken poses under 2 mm rise from 18 to 31-37. CLAUDE.md says to search on the 1 mm
  near-touch gap, which will give some of the takes back. Three of the binder "gains" are relabels to fold (255, 261,
  262).
- **The wrap region dies at pick3's law.** wd 76 / wa -18 folds 94 envsel poses (the stretched wall), so it must carry
  the K-law re-tune its proposer named, or be dropped. It is kept only as a re-tune cell.
- **It is still a ghost: no drive metal, and the knee at stk 4.85, not the 6.0 build rule.** The drive on a 32/48 dyad
  has never been built:
  - round 12 measured the lead's flank on longer dyads: it fails at rest, and its re-seated cells put the horn lug in the
    skin on 84-104 fit poses;
  - spiral-lobe with pick3's placement read 38.56, and its verifier estimated ~18.15 with >= 8 contacts even perfectly
    re-placed;
  - the pinned-horn stage 2 is PA-legal on 32/48 only at r_c 20-22 (g 2.3-2.5);
  - the verified "long-dyad" rows walked back to 26-29 / 38-39.

  So the ghost cannot be compared with 18.28 until gate 2 exists.
- **The in-band loss at wd 71 is mostly the cuff.** Weighted by samples (pib1.log, the desmo-conecut stack's per-pose
  counts), ~85 % of wd 71's -0.0116 in-band is the cuff side: knee, E and boss. The proposer's "the whole loss is the
  unrefit cuff side" is roughly right, and the knee re-fit can recover most of it.

### 5. The dog-leg closes itself

dogleg-link2-knuckle-3r's own full frozen wear reads 16.98, with 268 taken, 5 contacts and 2 new part collisions. 316 is
taken at 0.12 mm, and 117 / 127 / 129 / 139 get deeper. Stacked on wd 71 it is worse (18.15, 4 part collisions). Its
atlas shows that cells (b) and (c) together are worth at most 1 pose. That is a measured negative: it goes to FINDINGS,
not to a pick. One untested residue moves into pick 1's sweep as a column: the 117 / 127 / 139 contacts all sit on link
2's posterior 2 mm edge (a 6 mm bar, or the bar offset 1-2 mm anterior).

## Verdicts, all six

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | desmo-conecut-knuckle-3r (cell A) | **merged into pick 2 as the control** (the planner's id is kept for the merged entry) | Measured 18.87 frozen exact (93.14), cx 16.0. Its stage 2 binds at dK 43.0-43.25 at mu 0.15, short of the taken 45.62 / 46.27, so it fails the lens's kill gate. As a standalone pick it is dead by its own number; as cell A it is the reproduction anchor for B and C. |
| 2 | hornpin-desmo-conecut-knuckle-3r (cell B) | **merged into pick 2 as the claim cell** | Same chain, knee, stage 1, law and complexity; only stage 2 is inverted. Judge reproduced 69.75 deg at mu 0.15 (PA max 29.5) and found the nose swings only along the slot. The bench gives back ~0.34 by sample weight (S6); its case is held out and friction. Round 12 recommended this cell and did not build it. |
| 3 | lowring-hornpin-conecut-knuckle-3r (cell C) | **merged into pick 2 as the g column** | Its own spec starts from cell B's file and frees g, beta and r_c: a parameter extension. g 2.8 holds only at r_c 13.5 (46.0 at r_c 14.0, under the held-out 46.27). "No insert" has no Hertz margin. Gain ~0.2-0.4, inside the paired noise. |
| 4 | proximal-j3-geodesic-knuckle-3r | **PICK 1** | The only reach lever that moved the 5-pose binder in three rounds, and it holds out of sample (envsel 21.31 -> 19.20 / 18.62 at wd 71 / 73, +5-7 taken, -5 contacts). Judge's frozen exact wd 73: 16.72 with 4 contacts, but 269 taken (bar 274). It is a ghost: gate 2 must place a real drive on 32/48. |
| 5 | posterior-wrap-j3-envfit-knuckle-3r | **merged into pick 1** (wrap region + K-law re-tune cell) | The same lever (J3's seat on the same chain, same harness), overlapping sweep (wd 73-78 vs 69-74). At pick3's law it is dead on envsel (25.81, fold 94); its envelope-fit cost measure (0.63 vs 7.82) is real and goes in as the re-tune cell. |
| 6 | dogleg-link2-knuckle-3r | not picked: closed by its own measurement | 16.98 ghost with 268 taken / 5 contacts misses the bar; it deepens the binder and worsens the seat move (18.15). Its posterior-edge residue moves into pick 1's sweep. |

## Ranking (expected gap reduction vs the lead x confidence x buildability)

Both picks have 3 active joints and 0 passive translations, so buildability is decided by the parts.

| rank | id | judge's expected frozen gap | vs lead 18.28 | confidence | complexity | lead note |
|---|---|---|---|---|---|---|
| 1 | proximal-j3-geodesic-knuckle-3r | ghost 16.0-17.0 after the knee re-fit (wd 73 unrefit measured 16.72); hardware 16.5-18.0 | +0.3 to +1.8 if gate 2 holds | low-medium | the drive's (16.0 with pick 2's drive) | gate 2 = a real drive on 32/48 |
| 2 | desmo-conecut-knuckle-3r | 18.7-19.2, held 22.9-23.4 | -0.4 to -0.9 (complexity -2.5) | medium-high | 16.0 (16.5 with the groove insert) | complexity point, not a lead |

Pick 1 ranks first because reach is the user's standing priority and because it is the only lever that moves workspace
poses. Expected value: ~0.3-0.5 gap points against the lead after the probability that the drive fits. Pick 2's value is
complexity (-2.5 against the lead; +0.25, the dowel, against desmo-slipper's 15.75) plus a friction-proof drive. That is the
frontier point the user asked for ("95+ scores with low simplicity"), but not a score step. **The two picks compose.** Pick
2's pinned-horn stage 2 is the long-stroke, low-complexity drive pick 1's gate 2 needs (64-77 deg PA-legal against the
32/48 law's cap of 56). One drive model serves both.

The 95 arithmetic is unchanged: +18 workspace poses at the lead's in-band and contact. Neither pick reaches it. Pick 1's
best case is ~271-274 taken (~94.2).

## Notes for the modellers

- **Pick 1 (proximal-j3-geodesic-knuckle-3r):**
  - Reproduce first: frozen exact 17.23 / 17.31 (proposer) and envsel 21.31 / 19.20 (judge, envsel_wear.py).
  - Gate 1, the ghost (45 min):
    - seat screen wd 69-78 x wa -22..-6;
    - knee re-fit at stk 6.0;
    - in the wrap region (a2 < 52), the K-law re-tune;
    - search on the 1 mm near-touch objective and pick on envsel;
    - judge frozen exact Bench(110,360) against the planner's pre-registered bar (<= 17.5, <= 4 contacts, >= 274 taken)
      with the per-pose binder table, taken < 1 / 2 mm, th margin, flood and T5 depth (237 sat at -11.16 at wd 71).
  - Gate 2, the hardware: pick 2's pinned-horn drive re-seated on 32/48, else the in-band RSSR. Every drive part counts
    as metal.
  - Claim only with the drive. Report relabels as relabels.
- **Pick 2 (desmo-conecut-knuckle-3r):**
  - Reproduce cell A (stack.py: fast 13.18, frozen 18.87).
  - Build cell B with the in-model gates (a)-(g) of the catalogue entry, the closed end built as a union of discs, and
    the 440C groove insert as the default.
  - Run the g column (2.6 / 2.7 / 2.8) with the boss clearance as a hard bound.
  - Pre-register the claim cell on envsel.
  - Pair it against conecut (the lead) and desmo-slipper on the same poses, bench and held, at equal samples (S6).

## Recorded, not catalogued

- The dog-leg atlas (link-2 frame proximity atlas, 1215 directions, reproduces the straight link to 0.01) closes cells
  (b) and (c) of the seat lens for the gate: at most 1 pose together. A slaved K cannot serve 127 (a1e <= 53 at th 103.5)
  and 316 (a1e >= 60 at th 104.8) at once; a K slaved to q1 fails too (th 114 within +-5 deg of q1).
- The ghost family reads ~4 points worse on envsel than on Bench(110,360) (base 21.31 vs 17.23). envsel samples the
  behind-the-back binder (7 poses) and the high-elevation overhead contacts (452 / 454 at elev 167-168) more densely. A
  long-dyad claim should report envsel next to the bench number.
