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
