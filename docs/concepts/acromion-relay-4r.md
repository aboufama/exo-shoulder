# Acromion-pole relay 4R (acromion-relay-4r)

Round 101 (J1), pick 2. A plain O20 spherical 3R whose J1 walks the acromion-cap rim on a spring-centred J0 at the cap
pole. Its role this round is threefold:

- the plain-host control for pinknee-scapular-relay-4r (it isolates what the relay is worth without the pin knee);
- the shared full-grid continuity flood (`tools/spare_flood.py`), built and validated here;
- the stop-relay class re-measured under that corrected flood, reported as an INSTRUMENT change.

acromion-twinspring-4r is merged in as the "twin" determination cell (policy 1).

## Deeper-version prompt (answered before modelling, 2026-10-17 ~17:31 UTC)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Before tuning the relay, ask whether the relay can move the binder at all. The plain 3R's binder is hub 2, and
     J2 lies on the a2-circle about the humerus-fixed J3. A base-side spare moves J1, and through J1 it only slides
     J2 along that same circle. So measure hub 2's skin requirement per pose, with and without the relay, before
     spending CMA time.
   - Treat the instrument as a design input. The stop-relay died partly on a 360-node graph (157 components), so the
     flood has to be right before any number means anything.
   - Report the relay's worth in poses (static vs connected, overhead / 28), not just in gap points.
   - State the feel: the spring torque at the extreme relay poses, as cuff force.
2. **The rawest material.**
   - The posed skin itself, through the bench's signed-distance requirement along each hub axis
     (`K.requirement`, the K3 march).
   - The full 1432-node envelope grid of the workspace clip (`concept_bench._poses_all`, HG rotations), not the
     bench's 360 subsample.
   - The motion clips (follow).
   - The lead's lost poses (`docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json`).
   - The skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`, for the 1-3 mm spread at the cap
     pole that justifies seating J0 there.
3. **Methods and tools.**
   - tools/concept_kit.py: closure, O20 hubs, straps, K1-K7, dense K2 on q0..q3.
   - stop-relay-rocker-3r's crown / wall / near-touch extras.
   - The path-tracked full-grid flood `tools/spare_flood.py`.
   - CMA-ES (`tools/concept_cma.py`) on Bench(60,160) fast with the near-touch objective, islands dropped.
   - A frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench (Bench(60,160) fast, then Bench(110,360) exact frozen).
   - The flood validated against the judge's independent `graph.py` numbers: 0.67 on the 360-node graph, 0.91 on the
     full grid for the stop-relay section-5 setup.
   - The control: the same chain with T = 0 (relay locked) through the same code.
   - The red-team pose list below (rest, overhead, across the body, behind the back, the nearest-touch poses).
   - The adversarial verifier and the alignment auditor.

## Results

(filled in below as measured)
