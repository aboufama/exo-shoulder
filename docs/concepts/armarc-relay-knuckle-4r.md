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

## The lead's note, tested on the lead's real metal (frozen exact Bench(110,360))

The note asked whether the kit's 27 clean relayed poses (one-sided +30 about the long axis, scratch lensa/ring2_out.json)
stay clean on the lead's real arm-side metal and hub 1. The cell was re-run here with the IDEAL relay: no relay metal
and no lift, so it is an upper bound. The model is the lead itself, frozen. The relay solve is physical: the least phi
on every lost pose, with all of the lead's gates.

| frozen exact Bench(110,360) | gap | takes /360 | contact | near-touch 1 mm gap | relayed: taken / contact |
|---|---|---|---|---|---|
| lead (PHI 0 control, this model) | 18.28 | 262 | 0.0106 | 19.92 | - |
| ideal relay, long axis, PHI 30 | **11.93** | 289 | 0.0221 | 14.02 | 27 / 5 |

Per pose, against the kit's 27 (kit min mm -> lead metal min mm):

- 21 stay taken. The relayed taken-pose median is 3.25 mm, against 7.6-8.3 mm on the kit.
- 4 become contacts:
  - 343 (75/150/-105): 2.59 -> -1.41;
  - 372 (90/165/-90): 3.48 -> -0.55;
  - 423 (120/135/-90): 8.09 -> -0.43;
  - 448 (135/135/-90): 8.33 -> -2.71.
- 2 are not reachable once every gate is applied (drive range, knee window, J3 stop): 399 and 426, overhead at elevation 165.
- 4 taken relayed poses sit under 1.2 mm: 396 at 0.60, 369 at 1.02, 446 at 1.19, and one more at 1.15. The kit's 2-9 mm
  becomes 0.6-7 mm on the real metal.
- The physical solve also relays 7 poses the kit never looked at: 6 are taken. A spring relay cannot refuse them, so the
  seventh, 262 (30/135/0), a folded-side pose, goes **-11.44 mm** into the skin.

So the judge's estimate holds. The kit's metal was generous by ~4 mm, and 5 of the 32 relayed poses become contacts.
Even with no relay hardware, the long-axis relay reads 11.93, not the 10.83 on paper.

## Continuity (the 2026-10-16 rule), best config

The flood_relay() run covers the 1432-pose 15-deg envelope grid. Edges are 2-deg HG slerps with the least-phi relay
solved at every frame. Limits: phi step <= 10, K drive / knee pins <= 10, actives <= 25. Seeds are the lead's phi = 0
state-A nodes.

- Nodes: 1123 close.
- 88 envelope nodes are relayed; **85 are connected**.
- Edges: 2840 of 2851 pass. Failures: 8 phi jumps, 2 open, 1 active jump.
- The 3 islands are folded-side relays at axial -15:
  - 0/120/-15 at phi 17.4;
  - 15/135/-15 at 18.5;
  - 45/105/-15 at 18.9.

  phi jumps there from 0 to ~18 between grid neighbours. A spring relay snaps there.
- Relay angle over the relayed nodes: p50 9.2, p90 17.5, max 19.8 deg.

## THE DECISIVE WEAR: best config frozen exact Bench(110,360) -> 18.01, over the pre-registered kill 17.5. DEAD.

Best config: slotted circular Ti shell, PHI 20, tilt 12, az 235, sgn +. The lead's shape is frozen from its phi = 0
fit on Bench(60,160). CB_EXACT=1.

| reading (frozen exact Bench(110,360)) | gap | reach | in-band 14 | contact | takes /360 | overhead /28 |
|---|---|---|---|---|---|---|
| lead (PHI 0 control) | 18.28 | 0.7278 | 0.9012 | 0.0106 (4) | 262 | 8 |
| ideal relay at this axis (no relay metal, no lift): the bound | 16.39 | - | 0.9012 | - | - | - |
| **as built (relay metal + 4.59 mm lift)** | **18.01** | 0.7639 | 0.8838 | 0.0278 (11) | 275 | **8** |
| as built, near-touch (metal < 1 mm = contact) | 21.72 | | | | | |
| as built, chain-only in-band (S6: relay metal out of in-band, 0.8466) | 21.73 | | 0.8466 | | | |
| as built, connected reach (continuity flood) | 18.01 | 0.7639 | | | 275 | |

- **The fast optimum did not survive.** Fast 8.79 became frozen 18.01, an inflation of +9.22. The lead inflates by
  +5.78 (12.50 -> 18.28). The relay's axis, arc and PHI were tuned to the 160 fast workspace poses (round-3 lesson c).
- **The relay buys 13 takes and pays 7 contacts.** 20 bench poses relay: 13 are taken and 7 go into the skin. A spring
  relay cannot refuse a pose, so every one of the 7 is a contact. Overhead stays at 8/28: the relay takes no overhead
  pose.
- **Relayed poses park the metal on the skin.**
  - Relayed taken poses: median 1.81 mm minimum metal-skin distance.
  - 6 of the 13 are under 1.25 mm: 0.46, 0.69, 0.93, 1.00, 1.18, 1.23.
  - The lead's taken-pose median is 3.5 mm.
- **The relay hardware costs 1.62 points** over the ideal relay (16.39 -> 18.01):
  - the knee stack's 4.59 mm climb onto the carriage takes the chain's own in-band from 0.9012 to 0.8466;
  - the 4 mm-liner shell, 100 % in band, hides most of that drop in the headline 0.8838 (the lead's
    NEW-strap-dilution class). The chain-only reading is 21.73.
- **Continuity costs nothing here.** All 13 relayed takes are on the connected set. The 3 islands of the envelope flood
  are not bench poses.
- **No jams.** 0 track or carriage jams on the 360 + 110 poses.

### Red team (this config, frozen exact): where it breaks

| pose (plane / elev / axial) | phi (deg) | metal min (mm) | class |
|---|---|---|---|
| 262 (30 / 135 / 0) | 11.3 | **-9.79** | folded-side relay (the spring cannot refuse it) |
| 464 (150 / 90 / -90) | 11.8 | -6.20 | stretched, across the body |
| 206 (0 / 120 / -15) | 17.4 | -6.07 | folded-side relay; also a continuity island (phi 0 -> 17 between grid neighbours) |
| 343 (75 / 150 / -105) | 8.4 | -1.73 | overhead stretched (kit 2.59 -> real metal -1.73) |
| 182 (-15 / 90 / 45) | 11.3 | -0.71 | folded-side, binder side |
| 423 (120 / 135 / -90) | 16.0 | -0.70 | stretched overhead-ish (kit 8.09) |
| 372 (90 / 165 / -90) | 19.4 | -0.07 | overhead, at the end dowel |
| 396 (105 / 135 / -90) | 9.0 | 0.46 (taken) | the pinch: taken at 0.46 mm |
| 306 (60 / 75 / -120) | 12.7 | 0.69 (taken) | the pinch: kit 2.78 -> 0.69 |

The optimistic numbers:

- **The fast number:** 8.79 fast -> 18.01 frozen.
- **The kit's metal:** relayed median 7.6-8.3 mm on the kit, 1.81 mm here.
- **The headline in-band:** 0.8838 with the shell, 0.8466 without it.
- **The jam landscape.** On the fast bench the optimum sits 1 deg of tilt (tilt 11, az 235: 68 jams) and 10 deg of
  azimuth (az 225: 103-108 jams) from a jam cliff.

### Verdict

**DEAD at the pre-registered kill.** The frozen exact wear reads 18.01 > 17.5, against the lead's 18.28:

- a gain of 0.27;
- at 4 counted DOF and complexity 52.0 against the lead's 18.5 (tools/simplicity.py v2.2: +25 for the 4th DOF, +6
  springs, +8 loops, ...);
- near-touch 21.72 against the lead's 19.92: worse.

The convergence gate passed on the fast sweep (97 model-v2 configurations with relay metal; score points): gain over the
second half 0.00, over the last third 0.00, top-5 distinct configurations within 0.41. The kill is on the frozen exact
reading, as pre-registered.

**The limiter is measured: the second wall again, reached from the arm side.**

- A relayed pose parks the chain at its stretched-wall posture, with J3's arm frame turned about a GH-through axis.
- That puts member 3, hub 3 and the neck onto the binder-side skin:
  - relayed taken poses: median 1.81 mm;
  - 7 of 20 relayed poses are contacts.

  This is the same 1:1 fold-to-contact trade that the free-K rows measured from the scapula side
  (skinnormal-shortk-knuckle-4r 74/8 -> 55/19 -> 50/24).
- Even the ideal relay at the buildable axis is bounded at 16.39 frozen.
- The long-axis ideal relay is bounded at 11.93, with 5 relayed contacts and 4 near-touches. It cannot be built: a
  circle about the GH-elbow line floats 49-68 mm out over the arc, so the knee stack would need a 16.3 mm lift (fast
  39.72).
- Where the relay is buildable (tilt 12), it relays only 20 of the lead's 98 lost bench poses.

**What would change the verdict** is a relay whose track sits under the pad with no lift (track top <= the pad's
underside), combined with metal that clears the binder-side skin by >= 2 mm at the wall posture. Neither exists at the
lead's seats: the 4 mm liner + 1.5 shell + 0.2 + 1.5 plate stack is 7.2 mm over the skin, and the pad's lowest point is
2.6-5.7 mm over it.

Run time note for verifiers: the hardware path's exact wear (rerecord of 470 poses) took ~49 min wall under load 13-25.
The ideal path took ~4 min.

### The PHI lever, checked after the kill: closed by the hardware

The fast bench cannot see PHI. The ideal relay reads 4.89 fast at both PHI 20 and PHI 25, because its 160 workspace
poses never need phi > 20. Bench(110,360) can see it. All rows below are frozen exact at tilt 12 / az 235. They are
DIAGNOSTICS: PHI read off the claim bench is not a claim (the lowarm-halfring P1 class).

| PHI | ideal relay (no metal): bound | with the slotted shell + carriage | relayed: taken / contact | note |
|---|---|---|---|---|
| 20 | 16.39 | **18.01** | 13 / 7 | the fit best |
| 30 | 13.78 | **19.86** (follow 0.9818, contact 0.0565) | 19 / 12 | the shell arc runs to -56.7 deg |
| 45 | 12.37 | - | 32 / 13 (ideal) | near-touch 16.49 even with no metal |

At PHI 30 the longer shell touches by itself:

- at arm-down poses: elevation 0, four poses at -0.09 mm;
- at 460 (150/60/-60): -2.97;
- on clip frames 83 / 87: -0.35 / -0.45.

12 of 31 relays are contacts. More relay range buys takes only in the ideal model. With the real track, every extra
degree of arc is skin-facing metal on a circle that fits the arm only near the pad. This is the arm-ctrack / cring
death again. Dead stands.

Machinery note: the exact hardware wear now makes one distance call per pose for the contact-only parts. It runs in
548 s, against ~2900 s before, and reproduces 18.01 exactly.
