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
