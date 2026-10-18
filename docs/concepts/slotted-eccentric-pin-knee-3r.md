# slotted-eccentric-pin-knee-3r - the eccentric slotted-lever J2 on the pin-knee chain (round 14, lens 3 cell B)

## Deeper version (answered before modelling, 2026-10-18 00:40 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Notice that the spec's own start
   condition ("START ONLY after slotted-eccentric-j2-3r passes its slot gate on the kit and shows >= 3 frozen points
   over its own control") is already measured FALSE (that row: v_gap 115.21 vs its locked control 46.60, the slot
   costs ~69 points), and ask the one question that decides whether the pin-knee chain changes that: the eccentric's
   metal (crank, knee hub K, link 2b, the slot track and the roller) sits BETWEEN J2 and J3, upstream of member 3. The
   cuff knee only changes member 3's motion relative to the arm (planar about d3), not the J1 / J3 axis directions
   per pose, so it cannot move the eccentric's metal. The decisive measurement is therefore a PAIRED one: slot vs its
   own locked control through identical code at the pin-knee's J1 / J3 directions (H1 and lens 3's crest seats), with
   the knee hub at O20 (rule) - if the eccentric loses to its own control there, no cuff closure downstream rescues it.
   (b) Keep the inverted cam (roller on 2b, track on link 1): the spec's orientation is singular at every seat (measured
   on the parent: q2 spans 200-223 deg). (c) Attribute every lost / out-of-band sample to its part (crank, K, L2b,
   track, roller) and to its pose class (overhead, across, behind) before changing the law.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (fast cache for search, exact
   path for the claim), the bench's motion clips and workspace poses (held-out clips never loaded), the per-pose J1-J3
   angle th the poses need, the skin exit radius along the K and J2 rays (the K3 march) - not the parent's summaries.
3. **Methods and tools.** tools/concept_kit.py (K3 march, K2 dense continuity incl. axes K and G, K6 with same-body
   exemption, honest post heights, crowns + walls), the parent's slot_design (lock angle of the internal four-bar mode,
   track self-overlap, G-K-J2 alignment), CMA-ES locally (farm closed: niced, <= 2 processes, OMP_NUM_THREADS=1),
   frozen-shape wear on Bench(110,360) exact for the best cell.
4. **What shows the number is right besides me.** The bench (outside judge), the paired locked control through the
   same code (the eccentric must beat ITS OWN control, not a number from another model), the frozen exact run on
   Bench(110,360), the parent's independent verifier harness (docs/concepts/verify/slotted-eccentric-j2-3r.py), and a
   red-team pose list (overhead >= 140, across the body, behind the back, near-touch, lock-angle minimum).

## Why this cell was run, and what decides it

Round 14 plan: "slotted-eccentric-pin-knee-3r: only as lens 3's cell B if lens 3's measured limiter after gate 0 is the
fold, with its knee hub at O20 (not O11) and its complexity recorded". Lens 3 (crest-knee-3r, screened 00:12 UTC)
reports the fold as its largest loss (big bench: fold 92 of the lost poses, J3 window 30), and the lead
(conecut-knee-knuckle-3r) loses 88 of its 98 bench poses to the fold, 73 of them on the STRETCHED side (th 107-176,
internal rotation across the body). So the cell runs. Its spec's own start condition is NOT met: the parent
slotted-eccentric-j2-3r was refuted (v_gap 115.21 frozen exact vs its locked control 46.60 through the same code; the
slot costs ~69 points). This screen asks whether the pin-knee chain's axis directions, or a stretched-only law, change
that.

Model: docs/concepts/models/slotted-eccentric-pin-knee-3r.py = the parent's kit model (inverted cam, every check
unchanged) at the pin-knee chain's axis directions, with the O20 rule enforced at K (rad 10, 12.25 mm stack), fold
margin >= 5.23 (5 + K play) in th, psi in [15, 165], slot lock >= 50 deg, b >= 20 deg (two O20 hubs side by side).
Member 3 is the kit neck in both arms of every paired comparison; the eccentric's metal is all upstream of member 3, so
the cuff knee cannot change it (see the deeper version, point 1).

## Gate 0: the slot does what it promises kinematically

Seat-independent slot gate (synthetic poses over th, the parent's slot_design: lock angle of the internal four-bar mode
>= 50 deg, normal component >= 0.2 deg/deg, G-K-J2 alignment >= 10 deg, track self-overlap), 432 law cells per seat
(Amin 52-68, Amax 86-102, b 20-30, c 66-82, sl 0.6 / 1.0, both knee branches), knee hub O20:

| seat (axis directions) | plain dyad window th | best lock-held window (law) | kinematic reach Bench(60,160) |
|---|---|---|---|
| H1 (a1 41.02, a2 68.26) | [32.47, 104.05] | two-sided [25.5, 121.75] (Amin 58, Amax 86, b 25, c 74, sl 0.6; track 90.9 mm, 160 deg around J2) | 0.775 -> 0.8875 |
| H1, stretched-only | [32.47, 104.05] | [32.25, 129.75] (Amin 68, Amax 94, b 25, c 74, sl 0.6; lock 50.1 over the whole run) | 0.775 -> 0.869 |
| crest (a1 40.88, a2 55.01) | [19.36, 90.66] | [24.0, 121.5] (Amin 58, Amax 86, b 25, c 74, sl 0.6) | - |

217 of 432 H1 cells pass the slot gate; q2 spans 170-235 deg in every passing cell (the J2 interior angle sweeps ~0 -> 180
across any wide window; the crank adds to it).

## Bench: the metal that implements the window collides with itself (Bench(60,160) fast, kit checks)

Paired through identical code (member 3 = kit neck in both arms; O20 at J1 / J2 / J3 / K; margin 5.23):

| configuration | gap | reach | follow | ib14 | contact | closing poses colliding | kinematic reach |
|---|---|---|---|---|---|---|---|
| locked control, H1 directions (a2 68.26) | **34.78** | 0.688 | 1.0 | 0.799 | 0.034 | 4 % | 0.775 |
| slot, H1, two-sided gate cell (58 / 86, b 25, c 74) | 228.95 | 0.088 | 0.117 | 0.381 | 0.125 | 88 % | 0.888 |
| slot, H1, stretched-only (68 / 94, b 25, c 74) | 275.00 | 0.0 | - | - | - | 199 / 199 | 0.869 |
| same two configs with the parent's O10 knee (probe, not claimable) | 275.00 / 273.75 | - | - | - | - | 132/133, 197/199 | - |
| slot, best of 915 (B-g47-2) | **153.49** | 0.400 | 0.233 | 0.631 | 0.049 | 14 % | 0.500 |
| locked control at B-g47-2's seats (a2 60 / 66 / 72 / 78) | 63.31 / **57.07** / 61.74 / 69.16 | 0.73 | 1.0 | 0.55 | 0.048 | 5 % | - |

Per-pair attribution (K6 pairs over the closing poses, `attr` mode): H1 two-sided start of stream B: hub1|pinK 90,
hub1|L2b 70, pinK|link1 67, hub1|armG 39, pinK|spoke 38, crank|L2b 36 of 138; H1 stretched-only: pinK|link1 137,
link1|crank 132, hub1|pinK 123, pinK|trk1 92, pinK|spoke 91, pinK|trk2 82 of 199. The best config avoids them (neck|L2b
10, studG|link1 3, hub1|pinK 1 of 95) only because its lock-held track shrank to th [74, 133.5]: 125 of 220 poses do not
close, overhead 0/12. Its fitted levels: hub 2 71.2 mm (in band 0.00 - the crank rides over link 1 and the track, so hub 2
carries three layers), K 61.5, crank 61.5-75.2 (0.37), L2b 62.9-81.3 (0.38), track 54-85.

**Why (geometry, not tuning).** The roller G sits on link 2b at dG >= rpin + 3.5 + 1 = 14.5 mm from K (it must clear K's
boss), and the track is the locus of G around J2, so the track occupies the annulus e in [b - dG, b + dG] around hub 2 -
the circle K itself sweeps (b >= 20 deg so the two O20 hubs J2 / K clear). Over a wide window q2 spans 170-235 deg
(the J2 interior angle runs ~0 -> 180), so the K hub, the crank and the roller arm must cross link 1's strap, the track
and, on the folded side, hub 1. The kit stacks them honestly (crank over link 1 + track, L2b over the crank), which lifts
hub 2 out of the band; the alternative is K6 collisions. The parent found the same with an O10 knee (115.21 frozen vs
control 46.60); the O10 probe here shows the O20 rule is not what kills it.

## Frozen exact (Bench(110,360), fit Bench(60,160) fast at the 1 mm radial part-part rule, every level frozen)

Best config B-g47-2: fit 188.47 (153.49 at the search's 0.5 mm) -> **201.20** (score 26.8; reach 0.181, follow 0.055, ib14
0.604, ib10 0.362, contact 0.101; closure 0.37, collide 0.55 of the closing poses; near-touch 222.88, min metal 0.09 mm;
overhead >= 140: 0/28 ws, clip follow 0.2; kinematic reach 0.41 vs th need p5-p95 24.9-144.4; post lifts hub 2 0.85,
K 3.25, hub 3 2.82 mm).

Paired controls through the same frozen protocol (locked: link 2 rigid through K, the plain 3R): at the best config's
own seats (a2 66) fit 57.07 -> frozen exact **58.53** (reach 0.703, follow 1.0, ib14 0.549, contact 0.037, overhead 6/28);
at the H1 directions (a2 68.26) 34.78 -> **36.83** (reach 0.661, ib14 0.801, contact 0.031, overhead 6/28; the real pin
knee at H1 is 27.20 verified - the kit neck costs ~10). Paired frozen deficit of the eccentric: +142.7 at its own seats.

## Red team (own best config)

- The pose that jams: every pose with th < 74 deg (rest, scapular-plane overhead, the folded side) - the slot's lock
  falls under 50 deg there (lock over the whole kinematic run 40.7 deg), so the track ends at th 74 as a hard stop;
  overhead 0/28 on the big bench.
- The point that pinches: min metal-skin 0.09 mm on the big bench (0.32 fast); near-touch gap 222.88.
- The optimistic number: the 153.49 search number uses the kit's 0.5 mm radial part-part overlap; at the verifier's
  1 mm the same shape reads 188.47 and 201.20 frozen exact.
- The paired number that matters: the eccentric at its best is 96-119 fast points WORSE than the plain 3R at the same
  seats (57.07 at its own seats, 34.78 at H1 directions); it does not buy the reach it opens kinematically.

## Convergence gate and status

Ordered history (streams A + B + C interleaved by generation, n 915; score points): gain over the 2nd half 8.51 (> 1:
fails), over the last third 0.00, top-5 spread 2.61 -> NOT converged. Status **screened**, not dead. The remaining gain
cannot plausibly close a 96-point paired deficit: every gain so far came from shrinking the lock-held slot window (stream B: 275 at the parent's best
seats with the O20 knee -> 153.49 with the track cut to th [74, 133.5], kinematic reach 0.50 vs 0.87-0.89 at the gate
cells), i.e. by turning the eccentric off.

## What next

Not a lead path. The fold lever on the pin-knee chain needs a coupling whose moving metal does NOT share hub 2's
annulus: candidates are (a) a cam track OUTSIDE K's sweep (dG > b + 10 mm: a long roller arm over the deltoid, more
in-band metal) or (b) moving the variable length to link 1 (the U-law a1 schedule, measured 295/360 kinematic) where the
coupler would ride hub 1 on the acromion top - both need their own gate 0 on metal before any CMA. Lens 3's cx-0 row
(crest-knee-3r) and the knuckle lens stay the main lines.

## Audit (death audit, 2026-10-18 01:46-02:10 UTC; an auditor who did not build this model)

Question: is the "far behind" verdict caused by a bug, a wrong convention, a missed region or an over-strict check? Bar
for refutation: an honest gap <= 78.93 on Bench(60,160) fast (within 10 of the champion's 68.93). **The verdict stands
(not refuted).** Measured reason in one line: at the O20 knee the knee hub, the crank and the track must cross link 1 /
hub 1 across the slot's window, so every honest variant reads >= 152 fast; only the O10 knee that the round-14 plan
rules out reaches the bar (70.07), and that variant is the refuted parent.

What was re-measured (the model file unchanged; probes in the auditor's scratch, numbers below):

1. **Reproduction.** B-g47-2 on Bench(60,160) fast reads 153.49 exactly (reach 0.400, follow 0.233, ib14 0.631, ib10
   0.364, contact 0.049, honest). Gate recomputed on the honest entries in file order: 8.51 / 0.00 / 2.61 (n 915), as
   claimed. The 121 dishonest stream-C entries (the raw minimum, 112.55 at C-g10-7, has honest False and ib14 0.11 with
   every eccentric part lifted out of band) are correctly excluded.
2. **The O20 rule at K is the killer at the parent's seats (this corrects the row's "it is NOT the O20 rule").** The
   parent's best config (CMA E gen 13, emax 64.23) through THIS model at margin 5.23:
   - O10 MR63ZZ knee (the SEPK_O10_PROBE attribution path): **70.07** (reach 0.725, follow 0.90, ib14 0.485, contact
     0.061, collide 0.10). That is inside the 78.93 bar.
   - O20 knee (the rule): **209.85** (collide 0.88, hub 2 0.00 in band, trk7-10 0.00-0.12 in band).

   The row's claim holds only at the H1 gate cells, where the O10 probe also collides. The 70.07 does not refute the
   death, for two reasons. The round-14 plan requires K at O20 ("knee hub at O20 (not O11)"; CLAUDE.md "Keep O20 only").
   And that O10 configuration is the parent itself, refuted at 115.21 frozen exact against its own locked control
   (46.60), so it loses to the plain 3R even with the small knee.
3. **Missed regions (three were never benched).**

   | probe (Bench(60,160) fast, O20 K, margin 5.23) | gap | honest | collide | window th |
   |---|---|---|---|---|
   | emax fixed at 40 in ALL streams; best config with emax 50 / 64 / 80 | 197.07 | no | 0.82 | [64.25, 133.5] |
   | other knee branch sk = -1 (best; best + emax 64; parent; H1 + emax 64) | 375 / 313.46 / 375 / 375 | no | 0.87-1.0 | - |
   | dG 40 (roller track outside K's sweep: the doc's open option (a)), best + emax 90 | 275 | no | 1.0 | [53.25, 129.25] |
   | parent seats with b 28 / 32 / 36 | 220.59 / 303.41 / 305.08 | yes / no / no | 0.89-0.93 | - |
   | best, b 36, emax 64 | 136.83 | no (ib14 0.25) | 0.31 | [18.25, 133.5] |
   | H1 gate cell, emax 64 | 228.95 | no | 0.88 | [25.5, 121.75] |

   Lifting the emax cap widens the lock-held window, as the parent found, but the window's added metal collides.
4. **One over-strict modelling choice found and fixed in a probe.** The parent build gives the knee hub `pinK` no `over`
   list. The crank, L2b and armG stack over link 1 + the spoke + the track, but the K hub is fitted at its own skin
   level, so K6 counts every pass of K over link 1 as a collision (pinK|link1 is the top pair). A monkeypatch gives pinK
   `over` = link 1 + spoke + track at 1 mm:
   - best: 153.86 (unchanged)
   - parent seats: **160.72** (from 209.85; honest)
   - H1 gate cell: 110.41 dishonest (pinK, crank, L2b and armG 0.00 in band; ib14 0.30)
   - best + emax 64: 152.10 dishonest

   The fix is real: about 49 points at the parent's seats. The model file should carry it if this family is ever
   reopened. It does not approach the bar, because a K stacked over link 1 leaves the band, as the limiter says.
5. **CMA continuation.** Local, 2 processes, sigma 0.5, emax freed (scale 12), seed 7, 400 s: 81 evals (69 honest), best
   unchanged at 153.49. Gate over the combined honest history (n 1014, agent + 99 audit configs): 5.97 / 0.00 / 2.49.
   The last 424 configurations gained nothing. The 2nd-half rule is still open, only because the 153.49 sits at index
   589 of the interleaved history. It would need about 165 more no-gain evals, which the box (load ~6.5) could not run
   inside the time box. Status therefore stays **screened (far behind)**, not dead, under the binding gate.

Red-team summary: no convention bug against tools/concept_baseline.py was found. The bench, the gap formula and the
fast path are the shared kit's, and the reproduction is exact. The bad number is physical: O20 knee metal in hub 2's
annulus. The one over-strict check (pinK not stacked) is worth up to ~49 points at the parent's seats but 0 at the
best config. The number that stays optimistic is the fast 153.49 itself: frozen exact reads 201.20.

Frozen exact re-run by the auditor (the model's `frozen` mode, Bench(110,360) CB_EXACT=1): fit 188.47, then frozen exact
**201.20** (reach 0.1806, follow 0.0545, ib14 0.6042, ib10 0.3623, contact 0.1013, overhead 0/28 ws, near-touch 222.88,
min metal 0.09 mm). This reproduces the claim to the digit and is now the row's v_* fields. The 99 audit configurations
are appended to the sweep as stream "AUD". The pinK-stack probe rows carry no params, because they come from a
monkeypatched build.

## Re-dispatch (2026-10-18 05:28-06:10 UTC): the gate continuation found a new basin, still far behind its control

Why it ran. After the audit, the gate's 2nd-half rule was still open: the best (B-g47-2, 153.49) sat at index 589 of 1014
tries, so about 166 more tries without gain were needed. The box was free after the container restart, so the tries ran
locally (niced, 2 processes, OMP_NUM_THREADS=1, `tools/concept_cma.py`, model file unchanged):

| stream | start | sigma | evaluations (honest) | best |
|---|---|---|---|---|
| D1 | B-g47-2, emax freed (scale 12) | 0.3 | 161 (157) | 149.91 (D1-g18-4) |
| D2 | B-g47-2, emax freed | 0.8 | 97 (63) | **115.07 (D2-g9-0)**, 115.83 (D2-g3-6) |
| D3 | D2-g3-6 | 0.35 | 17 (11) | none better (gens took 150-300 s at box load 10-14) |

**New best D2-g9-0** (az 95.00, el 61.24, a1 53.08, wd 70.98, wa -20.37, Amin 56.37, Amax 80.71, w 4.55, sl 0.915,
b 26.04, c 74.66, emax 43.19, sk 1, margin 5.23; track dG 32, gG -165, 56.9 mm long, e 30.5-42.6 deg; q2 span 201.5):

- Bench(60,160) fast: **115.07** (score 58.2; reach 0.4625, follow 0.65, ib14 0.561, ib10 0.304, contact 0.074;
  closure 0.69, collide 0.20 of the closing poses). Fit at the 1 mm part-part rule reads the same 115.07.
- Frozen exact Bench(110,360): **117.68** (score 57.2; reach 0.433, follow 0.655, ib14 0.566, ib10 0.305, contact
  0.081; near-touch 126.06, min metal 0.08 mm; overhead >= 140: 0/28 ws, clip follow 0.0; kinematic reach 0.575 against
  th need p5-p95 26.3-144.2; post lifts hub 2 0.85, K 7.01, hub 3 4.0 mm). The run took 232 s.
- Paired locked control at the same seats (lock=1, link 2 rigid through K = the plain 3R, same code, Bench(60,160) fast):

  | a2 | 64 | **68** | 72 | 76 | 80 |
  |---|---|---|---|---|---|
  | gap | 61.33 | **55.09** | 58.11 | 64.19 | 70.70 |
  | reach | 0.719 | 0.738 | 0.750 | 0.750 | 0.738 |
  | ib14 | 0.522 | 0.555 | 0.512 | 0.472 | 0.474 |
  | window th | [16.25, 111.75] | [20.25, 115.75] | [24.25, 119.75] | [28.25, 123.75] | [32.25, 127.75] |

  The paired deficit is **+60.0 fast points** (115.07 vs 55.09). It was +96.4 at B-g47-2.

**Where the 38 points came from.** Almost all of it is follow (0.23 -> 0.65). The search bought it with two moves. First,
it lifted the eccentric's metal out of the band to stop the collisions: in band, hub 2 is 0.19, the crank 0.23, L2b 0.19
and K 0.36, and collide fell from 0.55 to 0.20. Second, it moved to a lock-held track over th [66.5, 128.25]. That
track adds 12.5 deg on the stretched side over the control's plain window [20.25, 115.75]. It loses 46 deg on the folded
side, where the lock angle of the internal four-bar mode falls below 50 deg (41.8 over the whole kinematic run). Rest
poses and scapular-plane overhead do not close there. So it is the same limiter as before, met another way. In-band
(0.56) and contact (0.074) leave this basin with no route to the control.

**Red team (D2-g9-0).**
- The pose that jams: every pose with th < 66.5. The track ends there as a hard stop, so overhead takes 0/28 on the big bench.
- The point that pinches: min metal-skin 0.08 mm. The near-touch gap is 126.06.
- The optimistic number: the fast 115.07 itself. The control at the same seats, through the same code, is 55.09.
- K's housing is fitted 7 mm higher on the big bench (post lift). The frozen shape carries this lift as out-of-band metal.

**Gate (score points).** Ordered history: A + B + C + AUD in file order, then D1 / D2 / D3 in chronological order from the
generation end times. Every try counts; dishonest tries are never the best; top-5 is taken over distinct configurations.
Result: **13.97 / 13.97 / 12.63** (n 1286; best at index 1246), so the gate is NOT converged. Status stays **screened**:
far behind, and no lead path. The wide restart showed that the earlier "no gain in 424 tries" was a local plateau. A
second wide restart (sigma >= 0.8, emax free) is the cheapest next probe if anyone reopens the family, but the paired
control at every basin found so far is 55-57.

**Lesson that predicts beyond this row.** A slaved length-changing hinge inherits the swept angle of the body it rides on:
- Downstream of the active joint whose angle drives it (this row: crank + K are J2's output), it sweeps that joint's span
  relative to the parent link. Here that is q2's 170-235 deg (201.5 at D2-g9-0) around J2, so it must cross link 1, hub 1
  and the track. The search then has two exits. It can collide, or it can lift the stack out of the band.
- Upstream of that joint, it turns only by the law's span. This is the knuckle family (link 1a -> K -> link 1b -> J2; the
  lead conecut-knee-knuckle-3r is 18.28 verified, with a dK cap of 57 deg, 52.6 of it used). Link 2 keeps the plain 3R
  sweep and never crosses link 1.

So a fold lever on the pin-knee chain belongs on link 1, not link 2. This is the measured reason the knuckle family leads
and the eccentric family trails its own control in every basin found (parent 115.21 frozen vs 46.60; this row 117.68
frozen; 115.07 fast vs 55.09).

## Audit 2 (second death audit, 2026-10-18 06:22-06:47 UTC; an auditor who did not build this model)

Question: does the re-dispatch's "far behind" stand, or is the bad number a bug, a missed region or an unconverged
search? Bar for refutation: an honest gap <= 78.93 on Bench(60,160) fast. **Not refuted; status stays screened (far
behind, no lead path).** One-line reason: the new basin refines to 86.82 fast / 97.04 frozen exact, still 7.9 points
above the bar and 27.7 fast points behind its own locked control at the same seats (59.15), because the lock-held track
still ends at th 62.25 (overhead 0/28) and the crank / L2b / K stay 0.23-0.59 in band.

What was measured (model file unchanged; local, niced, OMP_NUM_THREADS=1, <= 2 processes; ~5 s per fast evaluation):

1. **Reproduction.** D2-g9-0 reads 115.07 fast exactly (reach 0.4625, follow 0.65, ib14 0.5606, contact 0.0738, honest,
   window [66.5, 128.25]). Gate recomputed from the sweep: 13.97 / 13.97 / 12.63, as claimed.
2. **The new basin had never been refined** (D3 started from D2-g3-6, not D2-g9-0). CMA from D2-g9-0:

   | stream | start | sigma | evals | best |
   |---|---|---|---|---|
   | E1 | D2-g9-0 | 0.3 | 185 | **86.82 (E1-g13-3)**, 87.03, 87.77 |
   | E2 | E1-g2-4 (88.21) | 0.2 | 105 | none better |
   | E3 / E4 | E1-g13-3 | 0.6 (wide restart) | 49 + 17 | none better (93.88) |

   E1-g13-3: az 94.00, el 58.45, a1 49.96, wd 68.38, wa -20.10, Amin 56.48, Amax 81.91, w 2.27, sl 0.929, b 24.36,
   c 73.23, emax 49.75, sk 1, margin 5.23; track dG 32, gG -180, 66.1 mm, e 32.8-48.3 deg, q2 span 203.8, lock over the
   whole run 39.6.
   - Bench(60,160) fast: **86.82** (score 68.43; reach 0.519, follow 0.717, ib14 0.685, ib10 0.346, contact 0.038,
     collide 0.16). The gain over D2-g9-0 is in-band (hub 2 0.19 -> 0.84) and contact, not reach.
   - Frozen exact Bench(110,360) (model `frozen` mode; fit at the 1 mm part-part rule 89.42): **97.04** (score 64.7;
     reach 0.461, follow 0.682, ib14 0.699, ib10 0.354, contact 0.062, near-touch 103.66, min metal 0.24 mm,
     overhead >= 140 0/28 ws and 0/10 clip; kinematic reach 0.608 against th need p5-p95 27.1-143.2; lock-held window
     [62.25, 125.75]). In band per member: crank 0.36, L2b 0.23, K 0.59, hub 3 0.55, track node 1 0.57.
3. **Paired locked control at E1-g13-3's seats** (lock=1, the plain 3R through the same code, Bench(60,160) fast):

   | a2 | 60 | 64 | 68 | **72** | 76 |
   |---|---|---|---|---|---|
   | gap | 61.13 | 61.80 | 60.60 | **59.15** | 61.99 |
   | reach | 0.719 | 0.719 | 0.725 | 0.744 | 0.738 |
   | follow | 1.0 | 1.0 | 1.0 | 1.0 | 0.95 |
   | ib14 | 0.503 | 0.496 | 0.513 | 0.502 | 0.497 |

   Paired deficit **+27.7 fast** (was +60.0 at D2-g9-0, +96.4 at B-g47-2). The eccentric now beats its control on
   in-band (0.685 vs 0.502) but loses 0.22 of reach and 0.28 of follow: the slot still gives away the folded side.
4. **Attribution of the 50 deg slot lock (ATTRIBUTION ONLY; the lock is a round-14 hard edge).** D2-g9-0 with the lock
   gate at 40 / 30 deg: the track opens to th [13.0, 128.5] / [13.75, 128.5], reach 0.56-0.59, follow 0.82, but the
   longer track lifts out of band (ib14 0.26-0.27, dishonest): 120.62 / 113.68. The lock rule is not the only killer;
   the metal that a folded-side track needs is.
5. **Gate** over the whole honest history (A + B + C + AUD + D1-D3 + this audit's AUD2 streams, n 1641; score points):
   **24.24 / 24.24 / 0.52**, best at index 1388. Not converged by the 2nd-half rule (~1135 more no-gain tries), but the
   last 253 tries, including two sigma-0.6 restarts, gained nothing and the top 5 are within 0.52 point: a local plateau
   at 86.8-88.2. The 352 audit evaluations are appended to the sweep as stream "AUD2" (start re-evaluations excluded).

Red team (E1-g13-3): the pose that jams is every pose with th < 62.25 (track end = hard stop; rest and scapular-plane
overhead). The point that pinches: min metal 0.24 mm frozen. The optimistic number: the fast 86.82 (frozen exact 97.04,
+10.2). No convention bug against tools/concept_baseline.py found (shared kit bench, gap formula, exact reproduction).
The per-pose dump (tools/alignment_paired.py) was not written: the row is far from any lead.

New knowledge: the round's lesson stands and gets a number. Refined, the downstream eccentric still trails its own
locked control by 27.7 fast points at the same seats, and its frozen exact 97.04 is 79 points behind the knuckle lead
(18.28). What it buys is in-band (0.685 vs 0.502 for the plain 3R at those seats); what it cannot buy is the folded side
of the window, because a track that holds the 50 deg lock below th ~62 has to leave the band. Next: nothing on this
family unless someone reopens it with the fold lever upstream of J2 (the knuckle family already does that).

## Audit 3 (third death audit, 2026-10-18 07:08-07:25 UTC; an auditor who did not build this model)

Question: does "far behind" stand, or does a bug, a missed region or the open gate hide a design within 10 of the
champion (an honest gap <= 78.93 on Bench(60,160) fast)? **Not refuted. Status stays screened: far behind, no lead path,
and the gate is not converged, so the row is not dead.** One-line reason: the slot opens the folded side of the window
only where its track runs 67-129 mm from GH and knee hub K crosses link 1 and hub 1. The basin that stays in the band
plateaus at 86.82, 7.9 points above the bar.

What was measured (model file unchanged; local, niced, OMP_NUM_THREADS=1, 2 processes, box load 9-18):

1. **Reproduction.** E1-g13-3 reads 86.82 fast exactly (reach 0.5188, follow 0.7167, ib14 0.6845, contact 0.0382,
   window [62.25, 125.75]). The gap formula checks by hand: 21.55 + 23.33 + 38.12 + 3.82. The gate recomputed from the
   sweep is 24.24 / 24.24 / 0.52 (n 1641, best at index 1388), as audit 2 recorded. No convention bug was found:
   shared kit bench, shared gap formula, and b >= 20 deg, e_min and dG_min match the O20 envelopes they encode.
2. **Missed region: the H1 seats.** The locked control there is 24 fast points better than at E1's seats (34.78 vs
   59.15). E1's law moved onto the H1 seats, shifted by the a1 difference, gives this:
   - The lock-held track covers th [29.75, 124.25]: the folded side is open, with kinematic reach 0.88.
   - Every one of the 201 closing poses collides. The pairs are hub1|trk2 201, pinK|link1 138, pinK|spoke 121,
     hub1|pinK 103 and pinK|trk3 81. The track needs 9 segments and runs to 129 mm from GH.
   - Result: 275.0 honest.

   Three more seat swaps read 122-284, and two of them are dishonest.
3. **Ghost attribution (ATTRIBUTION ONLY, never a claim).** The same config, with K6 told to ignore crossings:

   | exempted pairs | gap | reach | follow | ib14 | contact |
   |---|---|---|---|---|---|
   | track vs hub 1 / armG | 213.73 | 0.231 | 0.10 | 0.455 | 0.173 |
   | plus K and crank vs link 1 / spoke / hub 1 / track | **105.33** | 0.644 | 0.667 | 0.475 | 0.089 |

   Even with every crossing exempted, the folded-side track (trk6-9 in band 0.25 / 0.03 / 0.00 / 0.03), L2b (0.08) and
   hub 2 (0.17) leave the band. The folded side is not just a collision problem: the track that holds the 50 deg lock
   there cannot lie on the skin.
4. **Gate continuation: two wide restarts with emax free.** The re-dispatch's lesson was that a wide restart can break a
   plateau.

   | stream | start | sigma | evals | best |
   |---|---|---|---|---|
   | F1 | E1-g13-3 | 1.0 | 40 | 107.18 |
   | F2 | D2-g9-0 | 0.8 | 64 | 184.07 |

   Neither found a new basin. The 109 audit tries (86 honest) are appended to the sweep as stream "AUD3". The gate is
   now **24.24 / 23.91 / 0.52** (n 1750, best still at index 1388), so it is NOT converged. The 2nd-half rule needs
   n >= 2777, about 1027 more tries without gain. That is a farm-sized job, and the farm is closed.

Red team (unchanged from audit 2, E1-g13-3):
- The pose that jams: every pose with th < 62.25 (rest and scapular-plane overhead; overhead 0/28 frozen).
- The point that pinches: min metal 0.24 mm frozen.
- The optimistic number: the fast 86.82 (frozen exact 97.04).

No per-pose dump was written: the row is 79 points behind the lead.

New knowledge: the slot's lock rule and the band are incompatible on the folded side at every seat tried. At E1's seats
the lock-held track stops at th 62. At the H1 seats it reaches th 29.75, but only with a 9-segment track that climbs to
129 mm and a knee hub that crosses link 1 and hub 1. The ghost bound (105.33, with every crossing exempted) is worse
than the in-band basin (86.82), so no stacking or exemption of the crossings rescues the H1 seats. This confirms the
round's lesson from the other side: the fold lever has to sit upstream of J2 (the knuckle family).
Next: nothing on this family. If anyone reopens it, the open gate is a farm job (about 1000 tries from E1-g13-3 and from
the H1 seats); expect it to confirm the plateau.
