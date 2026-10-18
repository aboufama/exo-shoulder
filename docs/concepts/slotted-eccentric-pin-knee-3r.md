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
