# Red team report (2026-10-14)

Written by the red-team subagent (pipeline/redteam/ scripts, results/ JSON); saved here by the lead because the agent's
environment blocked writing it. Mission: find the pose that jams each candidate chain and the pressure point that hurts
after an hour, and attack the lead's P0 claims. One process at a time, rig girdle law or synthetic / literature laws -
none of it is OpenSim data.

## Candidates

| tag | design | parameters / source |
|---|---|---|
| ref4R | reference `cad_r13_n4_s1343_1` | design.json |
| ring | P0 2R + ring | b (38.6, -4.6), a1 88.7, a2 99.8, branch +1; published axis points |
| 3R | P0 3R | b (163.5, 61.0), a1 106.9, a2 107.1, w (121.5, 93.4); published axis points |
| ring_mt | least-travel ring (`ring_travel.json`) | b (79.0, -0.5), a1 110, a2 89.1; axis points refit by the same LP |

sigma = smallest singular value of the unit joint-axis matrix (worst-direction joint rate = arm angular rate / sigma).
r = axial + plane (humeral rotation from the twist-free neutral). "Plausible workspace" = plane -90..150, elevation
0..170, r -90..90 with a rough ROM cap: 49,543 poses on a 5 deg grid.

## Findings

| # | what fails | number | pose / frame | threatens | fix (number to hit) |
|---|---|---|---|---|---|
| 1 | P0's "3 DOF absorbs the GH lift to 5-7 mm" holds only on the rig law over the 8 clips | rig law over the workspace: ring 13.7 / 3R 18.1 / ring_mt 12.3 mm worst (9.5-9.6 % of poses > 10 mm); axis points fitted to the workspace 9.5-10.3; literature law 47.1 / 47.0 / 49.7, refit 24.7 / 27.4 / 34.5, re-searched directions ring 30.3, 3R 24.7; plane-dependent lift +-30 %: 11-14; shrug +15 mm: 19.5-21.9 (best frame 10.8); load -10 mm: 13.5-14.3; + a humeral sliding cuff: rig 4.3 but literature 23-34, shrug 18-22 | 3R worst: hand behind the head (55, 170, r -90); ring worst: across the body (150, 115) | R10, R1, R2, R14 | judge R10 over the whole workspace, under the literature law and with a +-15 mm shrug, target <= 4 mm. Orientation-only chains cannot (shrug lower bound 12.5 mm for a -10..+15 mm girdle range); needs a translational girdle element (~65 mm superior, 35 medial, 25 posterior per the literature law) - ask the user whether passive DOFs count against the cap |
| 2 | thorax-fixed base D4-01 goes into the acromion | within 2 mm from 44.4 deg elevation, inside from 52.4 deg; depth 8 / 18 / 26 / 34 / 44 mm at 50-70 / 70-90 / 90-110 / 110-130 / 130-150 deg; 97 % of penetrating base vertices in the acromion region; deepest point at rest (-9, 40, 33) mm from GH | acromion / shoulder top | R2, R10 | thorax-fixed rigid parts over the acromion / scapula need >= 20 mm stand-off (skin rises up to 19.5 / 17.8 mm): breaks the band. Plate footprint at z <= -180 mm (medial of the scapula), or carry J1 on an element that tracks the scapula |
| 3 | ref4R cannot close | 19.1 % of the plausible workspace (13.1 % thorax base); 32.3 % at the 10 deg margin; 25-34 % above 60 deg elevation; overhead with external rotation r -60 / -90: 34 / 53 %; Wash: 54 of 193 wanted frames; clips pass within 12 (Wash), 16 (Wave), 19 (Shelf) deg of a singular pose | cross-body planes 120-150 deg: 47-49 % | R3, R4, R14 | P3: closure with >= 10 deg margin and sigma >= 0.15 on >= 98 % of the plausible workspace |
| 4 | 3R gimbal lock | a1 ~ a2 (106.9 / 107.1) -> J1 and J3 align within 0.03 deg; sigma < 0.15 on 1.8 % of the workspace (elev 20-70); held-out walking: margin 12.4 deg, sigma 0.155 (645 deg/s at a joint for 100 deg/s of arm) | (98, 31, r -9): arm forward to a table, carrying, walking swing | R3, R14 | abs(a1 - a2) >= 20 deg and the arm-fixed axis >= 20 deg inside its band around b over the whole workspace (sigma >= 0.3) |
| 5 | ring jam / packaging | ring: no closure within 8.5 deg of (128.6, 94.6) - across the body at shoulder height (2.1 % of the workspace), and within 11 deg of (-51, 85) - reaching to a car back seat; ring_mt: no closure within 20.9 deg of (-11, 89.5) = T-pose (4.2 %), Wave passes 5.2 deg away; a ring track on link 2 (188 deg arc): best placement still 1.2 mm from the chest wall (walking); ring_mt track (111 deg) clears >= 50 mm except Wash (-13.9 mm) | | R3, R2 | ring travel <= 90 deg AND both singular cones >= 20 deg outside the workspace; cross-body clearance needs the P2 contact model |
| 6 | assist load path | saddle 67.8 cm2 skin-facing, lever 203 mm: 25 N.m -> 123 N -> 18.1 kPa mean (136 mmHg); 10 N.m -> 7.3 kPa. The arm's underside the elevation assist must push on faces theta 98-141 deg in all 681 frames above 45 deg; 0 % lands on the rigid saddle (theta -21..62) - the knit band carries all the lift load | | R11 | an underside load-spreading pad sized for ~4.3 kPa (32 mmHg capillary reference): >= 115 cm2 at 10 N.m, >= 290 cm2 at 25 N.m |
| 7 | upper-arm cuff edge vs chest | -0.07 mm; 21 sampled frames within 2 mm | Wash; anterior wing theta -20, s 197 mm | R2, R11 | >= 5 mm clearance at cross-body poses; trim the wing for s > 180; re-check after P2 |
| 8 | elbow | BOTTOM's original elbow end (s >= 250) 1.9 mm into the forearm skin at rest, 7.7 at 120 deg flexion (our neck / hub >= 3.4 mm clear); the user's forearm cuff 9.1 mm inside at rest (17-22 in some poses) | | R2, P2 | most likely a rig artifact (the user's parts fit their real arm): fix the rig's elbow / forearm before trusting R2 there |

Not a pressure point as modelled (scapula-fixed base): no shoulder part within 2 mm of the skin (base 2.63 mm from the
acromion, link 2 2.78 mm from the back over the scapula).

## Method (scripts in this directory)

| script | output | method |
|---|---|---|
| rt_common.py | - | clips, 4R closure, candidate loader, task labels, body regions by nearest named muscle / bone |
| rt_jam.py | results/jam.json (+ jam_ws.npz cache, not committed) | sigma and margins along clips and over the 5 deg workspace grid; no-closure and sigma < 0.15 regions; distance from each clip to the nearest singular pose |
| rt_girdle.py | girdle.json | workspace residual; plane spread; shrug / load; synthetic + literature laws; refit and robust fits |
| rt_girdle_lit.py | girdle_lit.json | short re-search of axis directions under the literature law (6 starts x 500 iterations) |
| rt_slide.py | slide.json | the same chains + a humeral sliding cuff |
| rt_pressure.py | pressure.json | exact signed distance, every 6th frame (223), parts and thorax-fixed base, by body region |
| rt_skinmotion.py | skinmotion.json | trunk skin displacement / outward rise vs the thorax |
| rt_bottom.py | bottom.json | BOTTOM's depth: our neck / hub vs the user's original end |
| rt_cuffload.py | cuffload.json | cuff area, mean pressure, where the assist load lands |
| rt_ring.py | ring.json | rigid link-2 vs arm-fixed ring tracks against trunk and forearm, every 5th frame |

Caveats: girdle motion from the rig or synthetic laws (no OpenSim data); the plausible-ROM cap is rough; the rig has no
contact model (inflates the Wash depths).
