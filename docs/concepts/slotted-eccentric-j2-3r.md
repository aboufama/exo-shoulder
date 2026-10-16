# slotted-eccentric-j2-3r - eccentric J2 crank + slotted-lever cam on the zero-passive spherical 3R (O20)

## Deeper version (answered before modelling, 2026-10-16 06:10 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the slot as a *designed cam
   law*, not a given: the knee law a2e(th) is free, the slot is whatever curve the roller traces in link 2b's frame,
   so the real gate is not "d monotone" but the **pressure (lock) angle of the internal four-bar mode**: at a fixed arm
   pose the four GH-concurrent axes J1-J2-K-J3 form a spherical four-bar with one internal freedom, and the slot must
   cut across the roller's velocity in THAT mode (the spec's radial-only check ignores that K itself moves). I check
   that mode by finite differences on synthetic poses. (b) Solve the roller seat F1 per configuration by a grid
   (maximise the worst lock angle subject to roller-vs-knee and lever-vs-hub-2 clearance) instead of sweeping it.
   (c) Run the locked control through the identical code, at O20 (user ruling), at fold margin 5 AND 10.
   (d) Carry the lever as a real curved body: polyline along the slot, widened by its own deviation from the polyline.
2. **Rawest material.** The posed skin on the bench (signed-distance grid cache, exact path for the claim), the six
   training motion clips + workspace poses inside tools/concept_bench.py (held-out clips never loaded), the J1-J3
   angle distribution of those poses (th_need, from the poses themselves), docs/research/reach_attribution.md only as
   a cross-check.
3. **Methods and tools.** tools/concept_kit.py (K3 march, K2 dense continuity on every joint axis incl. K and the
   roller F, K6 with same-body exemption, honest post heights from dwell-fourbar-knee-3r.py), the farm
   (tools/cloud_run.py sweep), CMA-ES (tools/concept_cma.py) from the top configurations, the frozen-shape wear on
   Bench(110,360) exact.
4. **What shows the number is right besides me.** The bench (outside judge), the frozen exact run on Bench(110,360)
   (no refit), an adversarial verifier re-running the model, and a red-team pose list (overhead >= 140, across-body,
   behind-the-back, the near-touch list, the slot lock-angle minimum and where it happens).

