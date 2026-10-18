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

## Results (frozen exact Bench(110,360) unless stated; lead fit on Bench(60,160) fast at phi 0, shape frozen)

Gate (pre-registered by the judge): the LOWER of pooled ib14 and chain-only ib14 (shell / carriage / bracket out of
the share); pass <= 15, kill > 17.5. Lead conecut-knee-knuckle-3r: 18.28 (reach 0.7278, ib14 0.9012, 4 contacts).

| reading | plain | GATE | near1 | ib14 pooled / chain | reach (ws) | contacts | jams |
|---|---|---|---|---|---|---|---|
| pre-registered (PHI 30, ds 16, rt 2.5, a 10), spec's uniform bump R_t + h_c + 1 | 17.31 | **20.59 (kill)** | 21.50 | 0.8699 / 0.8371 | 0.7889 (284) | 13 | 0 |
| same hardware, refined bump, jam -> lost (superseded rule) | 13.39 | 15.62 | 17.07 | 0.9017 / 0.8777 | 0.7861 (283) | 8 | 6 |
| same hardware, refined bump, jam with metal in skin -> contact (model rule) | 14.59 | 16.82 | 18.26 | 0.9017 / 0.8777 | 0.7861 (283) | 15 | 6 |
| **CLAIM: fast-sweep pick, PHI 35, ds 19.54, rt 1.5, a 10.41, bump 1.0, band 9.27, ramp 6.15** | **14.02** | **14.40 (pass)** | 17.68 | 0.9196 / 0.8962 | 0.7917 (285) | 13 | 6 (5 in skin) |
| ideal relay at PHI 35, no hardware (bound, first on file) | 13.21 | - | - | 0.9012 | 0.7972 | share 0.0293 | - |

Claim details: follow 1.0, overhead 8 / 28 (lead 8 / 28: the relay does not buy overhead), contact 0.0319 (13 poses),
near2 38.01, min metal over taken 0.072 mm, continuity flood: connected = static (153 of 154
relayed envelope nodes connected, 0 bench poses dropped). Relayed 33 bench poses: 23 taken, 9 contact, 1 jam (phi max
32.9). Chain-only in-band cost of the bump 0.9012 -> 0.8962 (-0.005); the shell underside (303 samples, 99.5 % in band,
median 8.4 mm) lifts pooled ib14 to 0.9196 (dilution, out of the gate). Bracket ramp 49.9 deg (legal bent bar at ds 19.5).
R_t 79.9 (underside 78.4, clip-p90 skin 72.9 over the arc + 4 + 1.5), bump max 6.9 mm (E strap 78 / 164 points, boss
32 / 32, knee 50 / 90). R17: constant-force spring preload >= 0.063 N.m (gravity check, 1.5 x max opening torque).

Fast sweep (Bench(60,160) fast, objective near-touch gate gap = metal < 1 mm counted as contact, on the lower in-band):
219 configs (41 random per PHI 25 / 30 / 35, then a 96-try elitist ES at PHI 35). Best near1-gate 9.80 (plain 3.75,
gate 4.15). CONVERGENCE GATE: gain over the second half 0.08 score points, over the last third 0.06, top-5 spread 0.01:
converged. The optimum sits on two floors: rt_extra at the box edge 1.5 (spec range 2-3.5; the bench sees the shell, so
lower is allowed when it does not touch) and the ramp at its 60-deg floor. Fast PHI ranking 25 > 30 > 35 at 12.69 /
10.98 / 9.80 (the fast bench is near-blind to PHI: the PHI 35 pick was worn on the claim bench ONCE; the PHI 30
pre-registered hardware is the only other claim-bench hardware reading).

## Red team (measured)

* **The pose that jams.** The rigid bump is sized on the fit bench; on the claim bench the pin-a boss (5 poses) and the
  knee link (1) come 0.94-0.99 mm from the shell top at overhead / IR poses (316, 343, 372, 396, 423, 448: elevation
  135-165, axial -90..-105). 5 of the 6 have chain metal in the skin and stay contacts; 396 (metal 0.46 mm) is lost.
  PROBE +0.15 mm on the bump (claim bench, diagnostic only, not a claim): jams 6 -> 0, gate 14.40 -> 14.20, plain 13.74,
  reach 286, near1 17.91: the rule-floor clearance is not where the points are; the claim holds either way.
  PROBE rt_extra 2.5 (the spec's value) at the pick (claim bench, diagnostic only): plain 14.02 unchanged, gate 15.26
  (chain-only 0.8876): a higher shell needs a taller bump. The pass rests on the low shell (underside 5.5 mm over the
  clip-p90 skin), which adds no contact on the claim bench (contact share identical 0.0319); the held-out wear and the
  verifier's skin-bulge check decide it.
* **The point that pinches.** E strap over the moving carriage: 1.0 mm by construction at the fit poses (rule floor);
  the jam list shows the carriage at >= 3.5 mm on the claim bench, so the binding clearance is the boss vs the shell
  top, not the carriage.
* **The optimistic numbers.** (1) Plain 14.02 reads the pooled in-band 0.9196: 303 shell samples at 99.5 % in band lift
  it; the gate's chain-only 14.40 is the honest one. (2) The pre-registered PHI 30 hardware reads 16.82, not the
  judge's 14.61: the step-0 estimate missed the bump's contacts. (3) Contacts 13 vs the lead's 4, with depth: folded-side
  relays 262 -9.79 and 206 -6.07 (one-sided spring, item 4 of the planner's step 0 NOT met), 466 (150, 105, -105) -8.22
  at phi 28, 237 -8.93 / 264 -5.80 at elevation 165 (264 is -1.17 on the lead: the bumped boss / E strap at full
  elevation). The 1 mm near-touch reading is 17.68. (4) The fit-bench bump and the claim-bench PHI pick are both one
  reading each; held-out reading below.
* **Elevation-0 aliases** (plane + axial = 90, the anterior-end binder the judge flagged): all 4 taken at 4.84 mm at
  a 10 (pre-registered hardware), shell not touching.
* **Spec corrections that moved numbers**: the uniform bump (spec) vs the shell/carriage split (model): 20.59 vs 16.82
  gate at the same hardware; the jam -> contact precedence: 15.62 -> 16.82.

## New knowledge

* The relay's in-band price is the BUMP, and it is set by geometry, not by the relay: the E strap / boss / knee must
  clear the shell top by 1 mm and the carriage top by 1 mm only over the carriage footprint. A uniform bump to the
  carriage top + 1 over a +-10 mm band (the spec) costs chain-only ib14 0.9012 -> 0.8371 (+6.4 gap); the split bump
  costs 0.8777 at the spec's ds 16 / rt 2.5 and 0.8962 at ds 19.5 / rt 1.5 / band 9.3 / ramp 6.2. Every mm of shell
  height costs ~0.9 gap points through the bump (rt 1.5 -> 2.5: gate 14.40 -> 15.26).
* Moving the station proximal also legalises the bracket: the pad's proximal edge is at s -105.6, so ds 16 leaves 3.6 mm
  for a 9 mm drop (68.6 deg, machined) and ds 19.5 gives 49.9 deg (bent bar under the 60-deg ruling).
* Ideal relay bound at PHI 35 (tilt 12 / az 235) frozen exact: 13.21 (PHI 30: 13.78, PHI 45: 12.37). The hardware
  claim (14.02 plain) sits 0.8 above its own bound; the remaining gap to 95 (13.75) is the relayed contacts (9 of 33
  relayed poses, the second wall) and the fold beyond the relay (56 poses), not the hardware.
* A jam rule that removes a pose from the bench must not remove a contact: 5 of 6 near-floor jams had chain metal in
  the skin (15.62 vs 16.82 gate at the pre-registered hardware).

## Next

The verifier re-measures the claim (frozen exact Bench(110,360), PHI 35 / ds 19.538 / rt_extra 1.5 / pre 10.41 /
bump 1.002 / band 9.272 / ramp 6.0): `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3
docs/concepts/models/proxtrack-relay-knuckle-4r.py frozen '<params>' out.json` (writes the T5 per-pose dump next to it),
`... held '<params>' out.json` for the held-out wear, and a paired comparison against the lead and against
freekoracle-route (16.20). Red team for the verifier: the low shell vs skin bulge at the arm's widest section (rt 1.5),
the one-sided folded-side relays (262, 206), the bumped boss at elevation 165 (264 deepens -1.17 -> -5.80), and the
near-touch 17.68. The lever left inside the morphology: a two-sided relay (or an own-angle refusal) for the folded side,
and a lower carriage (h_c) since the bump over the footprint is h_c + 1.
