# proxtrack-relay-knuckle-4r - arm-fixed relay shell 16 mm proximal of the pad, zero lift, counted 4th R

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Price the relay's hardware where it costs
   - in the band. The ideal relay path never measured in-band (every dump carries the lead's 0.9012), so the first number
   is the frozen exact wear with the bump and the shell ON at the pre-registered config, read on the LOWER of pooled and
   chain-only in-band, before any tuning. Make the bump RIGID (one amount per sampled point of member 3 / knee link,
   the max over every fit pose and every relay angle the track can take under it), not a per-pose lift, and make the
   track's pre-arc obey its physical floor (carriage half-arc + stop dowel). Split the result into the bump's in-band
   cost (chain metal at every pose) and the relay's reach gain, so the lever that pays is visible.
2. **Rawest material.** The posed skin itself at every bench pose (the bench's signed distance on the exact path), the
   motion clips (fit-clip frames at 10 fps for the rigid bump and the skin radius profile about a_r), the lead's
   verified frozen shape (fit on Bench(60,160) at phi 0, frozen), the per-pose relay angle solved from the lead's own
   kinematic gates; not the step-0 window tables (they are re-derived inside the model).
3. **Methods and tools.** tools/concept_bench.py exact path, the armarc relay model (relay solve, flood continuity,
   gravity check) re-used by import, the kit's honesty checks through the lead's CCModel, tools/alignment_paired.py for
   the per-pose dump, an in-process hardware sweep (one fit + one relay solve per PHI, hardware re-recorded per config).
4. **Outside judge.** Bench(110,360) exact frozen read once at the pre-registered config (no selection on it), the
   adversarial verifier, the alignment auditor's T5 depth check on the per-pose dump, and a red-team list (the 4
   elevation-0 aliases at the anterior end, folded-side relays 262 / 206, the E strap over the moving carriage).

## Mechanism

The verified lead conecut-knee-knuckle-3r unchanged (3 O20 hubs on GH rays, knuckle K + its drive, two-pin knee, J3
dowel stop), plus a one-sided relay at the cuff: a slotted circular Ti shell (1.5 mm, 12 wide) about an ARM-FIXED axis
a_r through GH (tilt 12 deg from the humeral long axis toward az 235), strapped to the arm liner 16-20 mm PROXIMAL of
BOTTOM's pad (station s0 = s_pad + ds, s_pad = -111 mm along a_r). A T-nut carriage (24 x 14, iglidur strip, h_c 1.7)
runs in the slot; a constant-force spring holds it on its zero dowel, an end dowel caps it at PHI (both on the relay's
own angle). The pad hangs from the carriage on a 2 mm x 10 Ti bracket at the lead's own radius (rpad 73.2: ZERO lift).
The E strap (member 3), the pin-a boss and the knee link take a rigid local bump over the track band. 4 counted DOF
(J1, J2, J3, relay), 0 passive translations, complexity 52.5 (tools/simplicity.py v2.2; lead 18.5).

Model: docs/concepts/models/proxtrack-relay-knuckle-4r.py (imports the armarc relay model: the relay solve on the
lead's own gates, the continuity flood, the gravity check; replaces the hardware: geometry, rigid bump, shell /
carriage / bracket sampling, analytic shell / carriage clearance, jam rule). Spec corrections, each stated:

* **Bump shape.** The spec's bump lifts every member-3 / knee point in the band to R_t + h_c + 1 (the carriage top + 1).
  Over the shell away from the carriage only R_t + 1 is needed (1 mm non-adjacent rule over the shell top); + h_c only
  over the carriage footprint, which is fixed in the carriage frame. Both are measured below; the refined bump is the
  model's default. The bump is RIGID: one amount per sampled point (max over every fit-bench pose of the lead), applied
  radially about a_r at every pose; contact-only sets take the nearest sampled point's amount.
* **Clearance reading.** Shell and carriage are annular sectors about a_r: their clearance to the chain is computed
  exactly in (r, s, arc), not as nearest-sample - 1 mm (that reading flagged a true 1.0 mm clearance as a jam on 170 of
  220 fast poses). The bracket keeps the nearest-sample - 1 mm reading.
* **Jam vs contact.** A pose whose parts jam AND whose metal is in the skin stays a CONTACT (the armarc rerecord made it
  a lost pose, which removes a contact from the contact share).
* **Bracket.** At ds 16 the pad's proximal edge (s -105.6) sits 3.6 mm from the carriage's distal edge (s -102): the
  bracket drops 8.5-9 mm over 3.6 mm (68.6 deg), over the 60-deg bent-bar ruling: machined from solid at ds 16; at
  ds >= 20 it is a legal bent bar (~50 deg).
* **Pre-arc floor** = (carriage half-length 12 + dowel 2 mm) / R_t = 9.96 deg at R_t 80.6 (a < floor is clamped).

