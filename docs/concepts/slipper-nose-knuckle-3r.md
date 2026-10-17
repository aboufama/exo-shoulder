# slipper-nose-knuckle-3r: the drive's roller deleted, a hardened O3 nose slides on the flank

Lens: round 10, lens 3 (low complexity at the lead's reach). Family: slaved-knuckle 3R. 3 ACTIVE DOF (J1, J2, J3
encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables / rods.
Model: `docs/concepts/models/slipper-nose-knuckle-3r.py` (SN_CELL=lead | kneeless). Sweeps:
`docs/concepts/sweeps/slipper-nose-knuckle-3r.json`. Row: `docs/concepts/rows/slipper-nose-knuckle-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Put the friction where it is binding, not everywhere. The nose slides on both strokes. On the outward stroke the
     crank drives the horn; on the return the clock spring drives the crank through the horn. The friction cone adds
     atan(mu) to whichever body is being driven. The crank-side angle is 8-11 deg, so only the horn side on the outward
     stroke binds. The honest rule is therefore max(PA_horn) + atan(mu) <= 43 (45 gate, 2 deg slop). The spec's
     PA_kin = 43 - atan(mu) applied to both sides is the same rule, because the crank side never comes near it.
   - Ask whether a plain-bearing sleeve beats a bare nose. An iglidur sleeve O4 on the O3 dowel makes the flank contact
     roll and moves the slide to the journal. The effective coefficient is then mu_journal x r_pin / r_sleeve = 0.15 x
     1.5 / 2.0 = 0.11, worse than greased DLC sliding (0.05-0.087). At this size a bare hardened nose is the better slider,
     and the sweep's nose_r 1.5-2.0 covers the sleeve's geometry.
   - Check the load the nose really sees. MVP1 is unpowered (R17), so the nose carries the clock-spring force only
     (5-15 N at the contact radius 13-17 mm), and the friction drag at J2 is ~mu x N x r ~ 0.01 N.m, against R17's
     1 N.m. Under MVP2's 10 N.m (R9), part of that moment crosses K. There the O3 x 2.5 line contact on a DLC-coated Ti
     flank (p_max <= ~1.1 GPa, the substrate's limit) carries ~175 N. The MR63ZZ it replaces is rated C0r ~0.07 kN, so
     deleting the bearing raises the static capacity of the drive tip by ~2x. A hardened flank insert would carry ~640 N.
   - Re-fit the drive (g, beta, r_c, lift, nose_r) at the central friction case, mu 0.087, instead of only wearing the
     lead's mu~0 drive at a smaller pressure-angle cap. The stroke the friction takes away may come back from the
     law/flank geometry.
2. **Rawest material.** The posed skin itself: the bench's per-pose skin distance fields and the per-pose lost-pose
   list (fold / slide / contact, with plane, elevation, axial). The motion clips (the bench's clip frames) and the
   held-out clips (only in the held-out column). The skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`
   and the proximity atlas data for where hub 3 sits (`docs/research/proximity_atlas.md`). For the wedge, its own
   face-to-skin distances per taken pose and hub 3's crown height. Not the digested summaries in the round-10 text.
3. **Specific methods and tools.**
   - Spherical conjugate-cam synthesis per 0.25 deg of K: the parent's code, with the nose radius as the offset.
   - The friction cone in the pressure-angle budget.
   - Hertz line contact and Archard wear for the nose / flank pair (hand calc below).
   - The farm sweep (`tools/cloud_run.py sweep`), then CMA-ES (`tools/concept_cma.py`) as one farm job.
   - The claim protocol: fit on Bench(60,160) fast, wear the frozen shape on Bench(110,360) exact, then held-out and
     flood.
4. **What, other than me, shows the number is right.**
   - The bench (`tools/concept_bench.py`).
   - The frozen-exact Bench(110,360) claim, worn without a refit, through the same Frozen class that reproduces the
     lead at 18.67 (`kw/frz.py` harness = `SC.frozen`).
   - The held-out clips.
   - The flood (continuity) report.
   - The 2 mm / 1 mm near-touch audit (`PK.audit`).
   - The per-pose red-team list (lowest metal, contact poses by part).
   - The alignment auditor's ruling on the wedge, which gets both columns: flat and wedged, with hub 3's crown height.
