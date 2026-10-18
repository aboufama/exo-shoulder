# armarc-relay-knuckle-4r - the lead plus a one-sided arm-arc relay at the cuff

Round 104 (J4, track jump), pick 1 of lens A. A 4-joint design (the relay is a counted 4th joint).

## Deeper-version answers (written first)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Price the relay's *height*, not only its kinematics. A circular track about a GH-through axis can only sit at
     the highest skin it passes over. The pad, knee and E strap then have to climb onto the carriage, and that climb
     costs in-band on a third of the lead's metal (E 164 + knee 90 + pad 32 + boss 32 of 981 samples).
   - Choose the relay axis to make the arm look round over the arc. Do not take the humeral long axis by default:
     the GH-elbow line runs near the medial skin, so a circle about it floats 16-29 mm over the lateral arc.
   - Build the lowest-profile real guide: a slotted circular Ti shell with a T-nut carriage on an iglidur strip
     (shell 1.5 + 0.2 running gap + plate 1.5). Compare it with the spec's V-roller carriage (+5.5 over the track).
   - Model a jam as a jam: track or carriage metal within 1 mm of a non-adjacent moving body loses the pose.
2. **Rawest material.**
   - The posed skin meshes of every bench pose (concept_bench exact or fast signed distance).
   - The skin radius about each candidate relay axis, ray-cast from the axis on the 60 fit-bench clip poses (p90 per
     azimuth and station).
   - The lead's per-pose metal (its own fitted parts, unchanged).
   - The workspace and fit clips through the lead's own kinematic gates at every phi.
   - No digested summary is used as a number. ring2_out.json (the kit) is the claim being tested.
3. **Specific methods and tools.**
   - The lead's own model (conecut-knee-knuckle-3r.py), loaded unchanged and frozen.
   - A physical relay solve: the least phi in [0, PHI] that passes every gate of the lead (closure, knee window,
     R_tol, J3 dowel stop, residual, drive range dK_lim). The scan is 1 deg, then bisection.
   - Frames are patched in CB._poses_all, so every arm-side member rides HG' = HG R(a_r, phi) and the skin stays the
     pose's own.
   - The relay hardware is a set of explicit sampled parts. Poses are re-recorded after the lead's run: chain metal
     with the arm-side lift, plus the track and shell, plus the carriage.
   - A geometric axis scan (tilt x azimuth x sense) for the track's circularity defect.
   - A local sweep on Bench(60,160) fast (the farm is closed), then a frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench.
   - The PHI = 0 control, which must reproduce the lead's 12.50 fast exactly (it does).
   - The ideal-relay column (no relay metal, no lift). It must reproduce the earlier partial model's 5.39 (it does),
     and it bounds the design from above.
   - The frozen exact wear on Bench(110,360) against the lead's verified 18.28 and the pre-registered kill at 17.5.
   - A red-team pose list (relayed contacts, jams and their depths).
   - Next, the adversarial verifier (tools/workflows/exo-screen.js verify template; the bar is 18.28, stated by hand).
