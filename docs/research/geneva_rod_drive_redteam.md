# Drive red team + build spec: geneva-tail-knuckle-pinknee-3r, rod embodiment (gen-5 winner)

2026-10-16. Subject: the lobe -> rocker -> pushrod -> horn chain that slaves K to q2 in the gen-5 winner
(docs/concepts/geneva-tail-knuckle-pinknee-3r.md, verified 23.57 frozen exact, CORRECTED config: horn on a 1.5 mm plate on
K's +6 mm cap top, rocker post 19 mm). This mechanism has not been built before; this note prices it with real parts.

Scripts and outputs: `docs/research/geneva_rod_drive/`.

- `extract.py`: fits the verified design and wears it on Bench(110,360) exact (23.57 reproduced), then dumps the axes,
  levels, law and per-pose state to `geo.npz`. The npz is derived; rebuild it with `python3 extract.py geo.npz`.
- `drive.py`: builds the exact RSSR rod linkage and the lobe for 6 variants (`variants.json`).
- `loads.py`: forces, stresses, fold margin and arm gravity (`loads.json`), and the lobe polar export
  (`lobe_polar_V0.csv`).
- `clear.py`: the sweep clearances.
- `spec_points.py`: the placement points for the CAD (`spec_points.json`).

## Verdict

**The drive is buildable for MVP1 at this size, but not as modelled.** Six changes are needed. None of them changes the
law (kK 3.18), the seats or anything sampled in band, because the rod and its heads already sit 29-30 mm over the skin
(0 % in band). The verified number should move by well under a point. The L1 judges must confirm the rod against K's cap.

| # | Finding (measured) | Fix (cheapest first) |
|---|---|---|
| 1 | **The modelled rocker cannot move.** The rod end sits on the post's own axis, so turning the post moves nothing. A real rocker is a bell crank with two arms, which puts the rod's rocker end **9.8 mm** from the modelled point. At the verified 19 mm post, the rod then clears the cap by 0.87 mm, against the 1 mm rule; +0.5 mm gives 0.99. | Use a bell crank with a 9.0 mm follower arm and a 9.0 mm crank arm (ratio 1, as modelled), and grow the post to **20 mm**, which gives **1.10 mm**. Every number below is at 20 mm. The L1 must re-check ROD-hubK. |
| 2 | **The rod-end misalignment at the rocker is 27.8-30.2 deg**, because the rod drops toward K's axis, which is 38 deg from u2. The M3 steel rod ends allow 13-23 deg; igubal allows 30-32 deg, which leaves no margin. | Tilt the crank pin 29.0 deg from u2, square to the rod at mid-stroke (axis in `spec_points.json`). The swing is then a few degrees. At the horn the misalignment is 6.1-8.4 deg, which is fine. |
| 3 | **No catalogue M3 rod-end pair fits the 36.9 mm centre distance.** igus igubal KBRM-03 / KBLM-03 have h1 18.5 mm each, so the pair needs at least 37 + a gap. Its eye is **O13**, not O10, and it is rated 50 N long-term radial against the 52 N (spring only) to 70 N (MVP1) computed here. Steel M3 rod ends are about 27 mm long each. | Use a **custom Ti-6Al-4V dog-bone rod** (O3 shank, 36.94 +- 0.02 mm centres) with **two pressed igus igubal KGLM-03** spherical bearings (3 bore, O10, 6 wide, 32 deg swing, 200-550 N static). The O10 is exactly the head the model sampled. The eye bodies are O13 x 6. |
| 4 | **The lobe is bigger than the doc says.** With a real roller (MR63ZZ, r 3) and its base on the O20 skirt, the profile runs **10.74 -> 12.87 mm**, and is 12.60 mm at the largest taken K (44 deg). That is up to **2.9 mm past the O20 skirt** over a 12.5 deg profile arc, not 0.9 mm. The doc's 10.9 mm assumed a point follower at r 9. | Accept it, and make the nose sweep away from the rocker. With the follower on the + side, the nose clears the rocker tube by 2.95 mm. The mirror layout hits the tube by 1.98 mm. Link 2 never comes within 13.2 mm of the follower in plan. |
| 5 | **r_horn 2.49 mm is machinable.** It is an eccentric O3 pin on the plate, and the O13 eye stays inside the cap (r <= 9.0). The costs are sensitivity, 1.16-1.58 deg of K per 0.05 mm, and force. | Keep it for the CAD (it is the verified config). The alternative V2 (r_horn 4.0, crank 14.4, ratio 1.6) cuts the rod force to 38-51 N and the sensitivity to 0.72-1.15 deg, but moves the rod end 13 mm. That is a new geometry and needs a re-verify. |
| 6 | **The v5 cap is a threaded G2 dome with no angular index**, but the horn plate has to know where link 1a is. | At K: a flat-topped +6 cap, dowel-indexed to link 1a (the spring's outer anchor needs this too). The horn plate is clamped by 2x M1.6 ISO 10642 in +-5 deg arc slots, which gives the onset trim. |

**What is not buildable at this size: MVP2.** If the exo carried the arm (full support), K would see the arm's gravity
moment about uK:

- up to **4.68 N.m opening** on the stretched poses;
- **6.53 N.m** in the window.

The spring gives 0.08-0.094 N.m, so the load is 50-80x larger. At r_horn 2.49 it would mean **about 2.6 kN in the rod**.
No passive knuckle can take it, sprung or sensed; this holds for minarc too. The cheapest MVP2 route is to drive K
(a 4th actuator) or to use a morphology without a passive K.

This is not an MVP1 issue. The exo only tracks the arm, and the K load is its own weight: at most 0.033 N.m, the R17
hand check in docs/research/judge_fixes_check.md.

## 1. The lobe

The CAD baseline is variant **V0, side +1** (variants.json):

- **follower:** a bell crank with its axis parallel to u2, through the verified rocker base (15.96 mm from hub 2's axis);
  follower arm a_f 9.0, crank arm a_c 9.0, roller MR63ZZ (3 x 6 x 2.5);
- **lobe base:** pitch radius 13.1 at the onset, so the base circle (dwell) sits at r 10.1, 0.1 mm clear of the O20 skirt;
- **horn:** r_horn 2.493.

The lobe is solved for the **exact** spatial linkage, not for the model's linear `dK = kK t` with a straight rod:

1. For each t, the law gives dK = kK t.
2. The horn pin goes to B(dK).
3. The rocker angle beta comes from |A(beta) - B| = L, the RSSR closure.
4. The roller centre goes to C(beta).
5. That point, expressed in link 2's frame (rotated by -q2), is the pitch curve.
6. The profile is the pitch curve offset by the roller radius.

So the crank arcs and the rod slide (2.43 mm) are inside the profile. The law stays exactly linear.

Self-check: the J2 torque computed through the contact (normal force x arm about u2) equals kK x tau_K, from virtual
work, to 0.3 % on every row of loads.json.

Polar export, `lobe_polar_V0.csv`. The columns are: t (q2 past the onset), K opening, pitch azimuth and radius, profile
azimuth and radius, pressure angle, and rocker angle. The polar frame is x = the rocker-axis direction from u2 and
y = u2 x x, with the axes in spec_points.json.

| t (deg q2) | K open (deg) | pitch r (mm) | profile az (deg) | profile r (mm) | pressure angle (deg) | rocker (deg) |
|---|---|---|---|---|---|---|
| 0.0 | 0.0 | 13.10 | 48.28 | 10.74 | 34.3 | 0.0 |
| 4.8 | 15.3 | 13.85 | 52.42 | 11.48 | 29.8 | -4.8 |
| 9.6 | 30.5 | 14.57 | 56.03 | 12.13 | 23.5 | -9.4 |
| 13.8 | 43.9 (largest taken: 44.0) | 15.15 | 58.86 | 12.60 | 16.8 | -13.1 |
| 16.8 (stop B) | 53.4 | 15.52 | 60.73 | 12.87 | 11.5 | -15.5 |

- **Pressure angle: 34.3 deg at the onset, falling to 11.5 deg, under the 45 deg gate everywhere.** The model's constant
  41.4 deg was a point follower at r 9. A roller moves the pitch radius out by 3 mm. With the model's r 9 base (V0b),
  the start is 41.4 deg, but the dwell then needs a 1 mm groove in the boss. With a sliding O3 nose instead of a roller
  (V0s), the start is 44.0 deg and the Hertz pressure is about 800-930 MPa. **Use the roller.**
- **Curvature:** the minimum profile radius of curvature is 4.3 mm (convex), against a roller radius of 3, so there is
  no undercut.
- **Dwell:** before the onset, the lobe is the O20 skirt (r 10.0) and the follower waits 0.1 mm off it. K is held on
  stop A by its spring, so stop A, not the cam, defines K in the window. The dwell has to cover J2's whole range on that
  side: q2 from 93.4 down to -5.0 deg, about 98 deg of rim.
- **Onset step:** the law starts at full rate (K moves 3.18x q2 from the first degree). Pickup is a velocity step at
  the onset, and the 0.1 mm gap makes it a small impact. The CAD may add a 1-2 deg cubic lead-in. That costs at most 6
  deg of K over that degree, so it must be re-verified if used.
- **Closing spring:** K's clock spring is the closing spring, at the kit-rule and judge spec: 0.3 x 5 mm 1.4310 +C1900
  strip, >= 145 mm, 0.015 N.m/rad, **0.08 N.m preload** at stop A, 0.094 N.m at stop B. It holds the whole train in
  compression (horn -> rod -> rocker -> roller -> lobe), so no extra spring is needed.
- **Lift-off:**
  - *Kinematic:* the model's self-motion gate holds.
  - *Static:* the MVP1 opening load is at most 0.033 N.m against 0.08-0.094 N.m, a **safety factor of 2.4-2.8**.
  - *Dynamic (estimate):* the self-motion inertia about uK is about 5e-4 kg m2 (about 150 g at about 60 mm). The spring
    loses contact at K accelerations of more than (0.08 - 0.033) / 5e-4 = 94 rad/s2, which is q2 accelerations of more
    than about 30 rad/s2. A throw would exceed that; everyday motion does not. R17 should check it on the clips with
    the drive in.

## 2. Rocker, rod and horn: real parts

| part | spec | why |
|---|---|---|
| lobe ring | 17-4PH H900 (or 440C), 2.5 mm tall, ID 18 H7 on the boss turned to O18 g6 between F2+6.2 and F2+8.7. Profile per lobe_polar_V0.csv; the base is O20.2. Wire-EDM, keyed by an O1 dowel, clamped by the cap skirt. | Hertz 635 MPa (spring) to 738 MPa (MVP1) with the roller. Not Ti: Ti galls, and the same contact on Ti-6Al-4V is about 530 MPa on a poor wear couple. |
| follower | MR63ZZ (3 x 6 x 2.5) on an O3 h6 pin in the rocker's lower arm. The arm plate sits above the roller (F2+8.85 .. 10.35). The eye is O5, so it stays 0.6 mm off the cap skirt. | Follower load 35-45 N (spring) to 61 N (MVP1). C0 is about 0.09-0.10 kN (to confirm with the supplier), a safety factor of about 1.5. If the follower arm can grow to 9.5 mm, use MR83ZZ (3 x 8 x 3, C0 about 0.18 kN). |
| rocker | Ti-6Al-4V bell crank: tube O10 x 20 on a **fixed O5 17-4PH post** pressed into link 1b at the verified rocker base, axis parallel to u2. It turns on **2x MR85ZZ (5 x 8 x 2.5)**, preloaded by a wave washer, so it has no play. Lower arm 9.0 mm to the roller; upper crank arm 9.0 mm with the rod pin **tilted 29.0 deg**. The rocker turns 15.5 deg. | Post root 97-130 MPa, tip deflection 28-38 um. A plain-bushing rocker 19 mm tall would multiply its clearance by height / bushing length at the top, about 0.2 mm, which is about 5 deg of K. |
| rod | Ti-6Al-4V dog-bone, O3 shank, **36.94 +- 0.02 mm** centres, 2x **igus igubal KGLM-03** pressed. An optional M3 RH/LH turnbuckle between two eyes gives 1 mm per turn, or 0.023 mm per 10 deg of turn, which is about 0.6 deg of K. | Rod force 33-52 N (spring) to 70 N (MVP1). The buckling load is 3.4 kN. The KGLM-03 is rated 200-550 N static with a 32 deg swing. |
| horn | Ti-6Al-4V plate 1.5 mm, O3 pin at **r 2.493**, pressed and staked. 2x M1.6 ISO 10642 in +-5 deg arc slots on K's flat cap top. The cap is indexed to link 1a. | Pin bending is 73-99 MPa, with the lever as plate + half the eye. The eye stays inside r 9.0 of K's axis at every K. |

**Horn radius and the law.** In every variant the lobe is re-solved, so kK stays 3.18. The horn radius sets four things:
the lift, the pressure angle, the force and the sensitivity. Below, sens. is the K error per 0.05 mm of rod length.

| variant | r_horn | crank | lift | pa (deg) | lobe r end | F_rod spring / MVP1 | sens. (deg) | rod cap clear | rod-end move |
|---|---|---|---|---|---|---|---|---|---|
| V0 (build) | 2.49 | 9 | 2.42 | 34 -> 11 | 12.87 | 52 / 70 N | 1.16-1.58 | 1.10 | 9.8 mm |
| V1 | 4.0 | 9 | 3.80 | **48** -> 17 | 14.66 | 33 / 44 N | 0.72-1.00 | 1.13 | 10.0 mm |
| V2 | 4.0 | 14.4 | 2.32 | 35 -> 9 | 12.70 | 38 / 51 N | 0.72-1.15 | 1.73 | 13.3 mm |
| V3 | 5.0 | 18 | 2.22 | 35 -> 8 | 12.56 | 34 / 46 N | 0.58-1.04 | 2.36 | 15.8 mm |

- Machining does not set the smallest real crank radius; the eye does. An O13 eye on a 2.49 mm crank fits.
- A larger horn without a larger crank (V1) breaks the 45 deg pressure gate and puts the nose 4.6 mm past the skirt.
- **The model ignores the horn arc and the rod slide; both are measured here:**
  - The horn pin sweeps a 2.24 mm chord, and its effective arm drops from 2.47 to 1.82 mm at the stroke ends. That is
    why the sensitivity reaches 1.58 deg.
  - The rocker end slides 2.43 mm along a 9 mm arc.
  - Both stay within 1 mm of the swept line the verifier checked, except the 9.8 mm offset of finding 1.

## 3. Play and the K error

The spring preloads the train in compression on both sides of the onset, so every clearance sits on one side. The
clearances in the rod ends, the roller, the rocker and the horn pin add up to **one constant offset**, which the horn
slot trims out at assembly. What remains is the variation:

| source | variation | K error |
|---|---|---|
| rod centre distance | +-0.02 mm (trimmed) | 0 after the trim (+-0.5-0.6 deg before it) |
| lobe form (wire-EDM) | +-0.01 mm | +-0.24-0.28 deg |
| roller radial runout (MR63ZZ, ABEC-1 / ABEC-5) | 0.010 / 0.005 mm | 0.24 / 0.12 deg |
| post compliance (spring vs spring + MVP1 load) | 10 um | 0.23-0.32 deg |
| igubal polymer compliance (33 -> 70 N, about 5 um per joint, estimate) | about 10 um | about 0.25-0.3 deg |
| **RSS / worst case** | | **about 0.55 deg / about 1.1 deg** |
| backlash if the load ever reverses past the spring (igubal clearance 0.02-0.10 mm per joint, not catalogued; E10 bore on an h6 pin 0.014-0.060) | 0.04-0.2 mm | 0.9-6 deg (prevented by the preload, safety factor 2.4) |

**What a K error does:**

- **The cuff does not feel it.** With K slaved, the 3-DOF chain still closes on the arm and just re-solves q1-q3, so
  there is no strain at the cuff.
- **The pose read from the three encoders** is off by about the K error: 0.5-1.1 deg.
- **The 5 deg fold margin barely moves.** The margin of the taken stretched poses (m3e, the one `th` metric) is 5.11 deg
  nominal:

  | K offset (deg) | min taken margin (deg) | stretched poses below 5 (of 120) |
  |---|---|---|
  | +2 | 5.25 | 0 |
  | 0 | 5.11 | 0 |
  | -1 | 5.04 | 0 |
  | -2 | 4.98 | 1 |

  At a fixed pose `th`, the chain takes up most of the K error in q2. Each degree of K moves the margin by only about
  0.06 deg (da1e/dK is 0.42 before the re-solve). The trim direction is therefore "open, not closed": set the onset
  with K at +0.5 deg rather than -0.5.

## 4. Torques and stresses (V0; the "spring" case, then the "spring + MVP1" case)

| quantity | value | limit |
|---|---|---|
| reflected J2 torque (kK x tau_K) | 0.254-0.300 N.m; **0.36-0.41 N.m** with the MVP1 load | R17: <= 1 N.m about the shoulder, <= 5 N at the cuff. At a 120-150 mm cuff lever this is 2-3 N. **Felt as a 0.25 N.m step at the onset** (a soft wall into the stretched region; the spring gives it back on the way down). A 0.05 N.m preload would make it 0.16 N.m, still a safety factor of 1.5 on the window's 0.033 N.m. |
| K load from the arm's weight (full support, MVP2) | 4.68 N.m opening (stretched), 6.53 N.m (window), 2.63 N.m closing | spring 0.08-0.094: **50-80x over** (see Verdict) |
| K load, MVP1 (exo weight) | <= 0.033 N.m | spring safety factor 2.4-2.8 |
| rod force | 33-52 N / 47-70 N | KGLM-03 200-550 N static; KBRM-03 50 N long-term (too low) |
| follower normal force | 35-45 N / 48-61 N | MR63ZZ C0 about 0.1 kN |
| Hertz, roller on lobe (line, l 2.2 mm, R_lobe >= 4.3) | 635 / 738 MPa | 17-4PH H900: Sy 1170 MPa, static contact allowable >= 1.5 GPa |
| horn pin O3 bending | 73 / 99 MPa | Ti-6Al-4V Sy 880 MPa |
| rocker post O5 root (17-4PH) | 97 / 130 MPa | Sy 1170 MPa |
| crank arm root (3 x 4 Ti) | 58 / 79 MPa | Sy 880 MPa |

## 5. Build spec for the CAD agent (L1 now, user style after)

Placement is in `spec_points.json`. Every point is in the design's reference frame (link 1b at q = 0, K on stop A, mm
from GH), the same frame as the model's `rigid` samples.

1. **Hub 2 (O20 v5):**
   - Turn the upper boss (link 2) to O18 g6 between F2+6.2 and F2+8.7 (F2 = 60.236).
   - Slip on the lobe ring (17-4PH H900, 2.5 tall). Its profile is `lobe_polar_V0.csv` in the polar frame
     lobe_polar_x / y about u2: profile r 10.74 -> 12.87 over the profile azimuth 48.28 -> 60.73 deg, with the base
     O20.2 elsewhere.
   - Key it (O1 dowel) so that the onset sits at q2 = -5.011 deg. The cap skirt clamps it.
2. **Rocker:**
   - A fixed O5 17-4PH post on link 1b at `rocker_base_on_link1b`, axis u2, 20 mm tall. That is the verified 19 mm
     plus 1 mm for the 1 mm rod-to-cap rule (1.10 mm).
   - A Ti tube O10 on 2x MR85ZZ with a wave washer.
   - Lower arm: 9.0 mm to the MR63ZZ roller, centre at `roller_centre_onset`, roller mid-plane F2+7.45, arm plate
     above the roller.
   - Upper arm: 9.0 mm to the rod pin at `crank_pin_onset`. The pin axis is `crank_pin_axis_tilted` (29.0 deg from u2).
   - The eye bottom sits >= 0.5 mm over the tube top.
3. **Rod:** a Ti dog-bone, 36.94 mm centres, 2x igubal KGLM-03 pressed into O13 x 6 eyes, O3 shank. Sample it as the
   swept line from `crank_pin_onset` -> `horn_pin_onset` to `horn_pin_end`, plus the O13 eyes.
4. **Horn and K cap:**
   - K's +6 cap is flat-topped at `cap_top` (76.269 along uK) and dowel-indexed to link 1a.
   - The horn plate is 1.5 mm thick, O16, with 2x M1.6 ISO 10642 in +-5 deg slots.
   - The O3 pin sits at r 2.493, with the rod-end centre at `horn_pin_onset` (head mid-height, 2.5 mm over the plate).
5. **Stops:**
   - the q2 dowel stop B at q2 = -21.811 deg (16.8 deg past the onset);
   - K's stop B at a1max 58.36 deg (dK 53.4);
   - stop A as in minarc. The gen-4b fixes apply: the K stop pair is rotated off the link-1a root, and J2 uses a double
     dowel.
6. **Judges:**
   - R6 / R16 at 1 mm: ROD-hubK, the lobe nose vs the rocker tube (2.95 mm here), and the follower vs L2 (13.2 mm here).
   - R17: the 0.25 N.m J2 step, and spring contact on the fastest clips.
   - R9: the post root and the horn pin.
7. **Colours (render):**
   - Ti and 17-4PH parts: bead blasted.
   - The KGLM-03 balls and housings: iglidur orange.
   - Screws and the roller: polished.
   - No black parts.

## Red team (what could still be optimistic)

- **The MVP1 load of 0.033 N.m** is the exo-gravity bound of an earlier hand check on minarc, not a dynamics run on this
  design. R17 must re-run it with the drive in. If it exceeds about 0.06 N.m, raise the preload, which also raises the
  J2 step.
- **The MR63ZZ C0** and the **igubal clearance and compliance** are not catalogued here; they are supplier checks.
- **The dynamic lift-off at about 30 rad/s2 of q2** rests on a lumped inertia estimate. R17 is the instrument for it.
- **Placing the follower beside the rocker post** puts the roller and arm at F2+6.2..10.35. This note checked them only
  in plan against link 2 (13.2 mm) and against the cap skirt (0.6 mm by construction). The L1's R6 is the real check.
