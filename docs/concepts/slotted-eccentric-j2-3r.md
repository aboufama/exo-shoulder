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

## The spec was wrong in one place: the slot cannot sit on link 2b with the roller on link 1

Measured first, before any bench run (`python3 docs/concepts/models/slotted-eccentric-j2-3r.py gate`, synthetic poses
over the J1-J3 angle th, Amin 60 / Amax 90 / b 25 / c 72 / a1 38.09 / margin 5):

- Over the window the law opens (th 27-123 deg), the crank angle q2 (crank vs link 1 about J2) spans **200.8 deg**:
  the J2 interior angle runs 0 -> 180 deg across any wide fold window, and the knee offset does not cancel it.
- With the roller F fixed on link 1 and the slot in a lever on 2b (the spec), the cam is **singular whenever F, K and J2
  lie on one great circle**: there d/dq2 and d/dpsi move the roller along the same direction in 2b's frame, so the slot
  cannot hold the knee. That happens whenever the crank's azimuth about J2 passes the roller seat's (or its antipode):
  with a 200 deg crank sweep, for EVERY seat. Fine-sampled (0.02 deg in th): seat (38, -7.5) lock angle 2.46 deg at
  th 75.92 where q2 = -7.49 = the seat azimuth; seat (20, 0) 0.024 deg at q2 = -0.02. (A 0.5 deg sampling misses the
  dip and reads 37 deg - the gate now also tests the alignment angle directly.)
- **Inverted** (roller G on link 2b at polar (dG, gG) about K, the slot a curved track fixed to link 1 around hub 2) the
  singular set is G-K-J2 alignment, which depends on the knee angle alone (psi spans 57-134 deg here), so it can be
  placed out of the way. This is the model. Same parts, same mobility, same complexity.
- The inverted cam's lock angle (angle between the roller's velocity in the internal four-bar mode at a fixed arm pose
  and the slot tangent; >= 50 deg = pressure angle <= 40 deg, the spec's number) falls toward the fold edges: the
  internal mode of the J1-J2-K-J3 loop IS the fold mode, it changes the knee angle only in proportion to sin(J2 interior
  angle). Best seat at the default law: 41 deg over the whole window, >= 50 deg only over th 27-117.75 (the track
  ends there: a hard stop, poses beyond are not taken). The slot lock is a fold margin in disguise.
- The track is long: 106 mm of slot, 152 deg around J2 at 25-45 deg (27-49 mm) from its axis, i.e. a crescent of
  link 1 plate around hub 2 that reaches the trapezius / neck skin.

