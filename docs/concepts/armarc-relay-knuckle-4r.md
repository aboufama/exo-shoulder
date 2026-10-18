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

## The morphology as built

The verified lead conecut-knee-knuckle-3r is loaded unchanged and frozen from its own phi = 0 fit on Bench(60,160).
That covers J1 at the back of the shoulder / acromion top, K slaved by the slipper-nose / conecut drive, J2, J3 with
its dowel stop, the E strap and the two-pin MR63ZZ knee.

The change is at the cuff:

- The arm pad (pin b's boss) rides a **carriage**.
- The carriage runs on a **circular track of one radius** about an arm-fixed axis a_r through GH. The arc is
  concentric with a_r, so every chain axis still passes through GH and the knee pins stay parallel to J3 (judge 1.3).
- The relay is a pure rotation of the whole arm-side frame: HG' = HG R(a_r, phi).
- A constant-force spring holds the carriage on its zero dowel. An end dowel caps it at PHI.
- One-sided: phi >= 0 only.

**Topology.** handler -> J1 -> K (passive, slaved) -> J2 -> J3 (stop) -> E strap -> knee pin a -> knee link -> pin b
-> pad on the CARRIAGE -> R_relay (counted 4th joint, spring + dowels) -> circular slotted shell -> liner -> arm.

- 4 counted joints. Passive: K, the bell crank and the knee pins a and b.
- 0 passive translations.
- Every coordinate is determined (R17): the relay sits at the least phi in [0, PHI] that closes the chain within the
  lead's stops.

**Spec corrections made here (each measured):**

1. **The relay axis is not the humeral long axis.** At tilt 0 the circle about the GH-elbow line sits 49-68 mm out
   over a 58-deg arc (skin p90 per azimuth), so the knee stack would have to climb 16.3 mm onto the carriage. The
   sweep then gives:

   | config (Bench(60,160) fast) | gap | in-band 14 |
   |---|---|---|
   | PHI 30 | 39.72 | 0.590 |
   | PHI 20 | 36.82 | 0.626 |

   A tilt of 12 deg toward azimuth 235 gives:
   - a skin profile of 67.5-70.6 mm over the arc;
   - a lift of 4.59 mm.

   (The track radius is about the tilted axis. The pad sits at r 73.2 about it.)
2. **The spec's V-roller carriage is too tall.** It stands 2 mm of track plus ~5.5 mm of roller and plate over the
   shell: lift 12.54, gap 22.58 at tilt 10 / az 270 / PHI 20. The built variant is a **slotted circular Ti shell**:
   - the 1.5 mm shell is the track, at one radius about a_r;
   - a T-nut carriage plate rides on an iglidur strip (0.2 running gap + 1.5 plate), with the T-nut flange recessed
     into the 4 mm liner;
   - stack over the liner: 3.2 mm.

   This is a curved plain guide: a machinable part, rotations only, with no balls in a curved race. Friction adds
   hysteresis to the spring relay (see the feel note below).
3. **Lift and jam rule.** Parts are rigid, so the knee stack (pad, boss, knee link, distal E strap) climbs onto the
   carriage by ONE lift, dh = max(carriage top - the stack's lowest point, track top + 1 mm - any mover over the track
   band in ANY fit-bench pose).
   - The E strap ramps from no lift at s_pad + 35 to full lift at s_pad + 15, so hub 3 is not lifted.
   - The lift is radial about a_r. At the pad it is close to the pin direction, so the knee closure is kept. This is
     an approximation, stated.
   - Any bench pose where the track / shell or the carriage comes within 1 mm of a non-adjacent moving body (knee
     link, E strap, boss, hub 3, link 2) is a **JAM**: lost and listed.
   - A relayed pose with metal in the skin is a **CONTACT**: a spring relay cannot refuse it.
4. **Relay metal sampling (model v2).**
   - Skin-facing surfaces only (shell underside, carriage underside, bracket) go into in-band, at ~1 point per 4 mm2.
   - The tops are contact-only.
   - v1 (sweep entries k < 74) also counted the tops in in-band. That doubled the shell's weight, a dilution, and
     those entries are superseded.

## Measured on Bench(60,160) fast (lead shape frozen; docs/concepts/sweeps/armarc-relay-knuckle-4r.json)

| configuration | gap | reach | in-band 14 (chain only) | contact | note |
|---|---|---|---|---|---|
| PHI 0 control | 12.50 | 0.775 | 0.9007 | 0 | = the lead's fast 12.50 (reproduced) |
| ideal relay PHI 20 / tilt 12 / az 235 (no relay metal, no lift) | 4.89 | 0.8562 | 0.9007 | 0.0051 | the kinematic ceiling at this axis |
| ideal relay, long axis, PHI 30 / 45 | 5.39 / 2.87 | 0.856 / - | 0.9007 | - | earlier partial model's 5.39 reproduced |
| **best: slotted shell PHI 20 / tilt 12 / az 235 / sgn +** | **8.79** | 0.8438 | 0.8835 (**0.8462**) | 0.0152 | lift 4.59 mm, R_t 76.1, arc -111.4..-66.7 deg, near-touch 14.44 |
| same at PHI 15 | 9.11 | 0.8375 | 0.8816 (0.8462) | 0.0102 | |
| distal bracket station (ds -25, no lift) | 16.06 | 0.80 | 0.9331 (0.9076) | 0.0606 | the distal shell meets the chest at plane 145-150 |
| spec's V-roller carriage (tilt 10 / az 270 / PHI 20) | 22.58 | 0.8375 | 0.7519 (0.7003) | 0.0152 | lift 12.54 |
| long axis (tilt 0), PHI 30 | 39.72 | 0.8375 | 0.5904 | 0.0251 | lift 16.3 |

- **Chain-only reading (S6, equal samples).** Count only the lead's own metal in in-band and keep the relay metal for
  contact. The best then reads 8.79 + 100 x (0.8835 - 0.8462) = **12.52 fast**, level with the lead's 12.50.
  - The relay metal sits 100 % in band (shell on a 4 mm liner).
  - The lift costs the chain 0.055 of in-band (0.9007 -> 0.8462).
  - The headline in-band 0.8835 is therefore partly the shell's dilution: the lead's NEW-strap-dilution class, reported
    here, not hidden.
- **The axis landscape has jam cliffs next to the optimum:**

  | axis change from the optimum | reach | cause |
  |---|---|---|
  | tilt 11 at az 235 | 0.61 | jams |
  | az 225 at tilt 11-13 | 0.41-0.48 | jams |

  In both, the knee link / E strap passes over the track band. The optimum sits 1 deg / 10 deg from a cliff.
- **Gravity determinacy (judge 1.4)**, gravity_check, lead CAD masses, 184 fit-bench poses closed at phi 0 and 2 deg:
  - the generalised gravity torque along the relay opens it by at most 0.042 N.m (p95 0.035);
  - preload needed x1.5 = 0.063 N.m, i.e. ~0.83 N at the carriage radius 76 mm, a small constant-force strip (CF class;
    part number to confirm);
  - the felt resistance past the wall is about the preload plus the strip's friction.
- **Convergence gate** (v2 entries only, 97 configurations with relay metal; score points):
  - gain over the second half 0.00;
  - gain over the last third 0.00;
  - top-5 spread 0.41 (8.79 / 9.11 / 9.65 / 9.88 / 9.91 gap).

  PASSED.
