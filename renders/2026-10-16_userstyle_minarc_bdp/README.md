# Generation-4 winner (minarc-stop-knuckle-4r BDp): full CAD in the user's style

**Design:** `pipeline/full-exo/designs/user_minarc_bdp`, built by `pipeline/conformal/param_cad/user_style_minarc.py`
(v2, four-strip machined links) from the verified BDp parameter dict. The judged scorecard (5 of 19) is `judge/scorecard.md`;
the design is described in `docs/concepts/minarc-stop-knuckle-4r.md`.

- **Joints:** four revolutes on v5 O20 hub stacks: J1 (base, at the J1 ring, no tab), K (the knuckle that splits link 1
  into 1a / 1b; sensed, the 4th encoder), J2 and J3. The knee is the gen-3 flat two-pin plate. 0 passive translations.
- **Hub K:** its cap is 6 mm taller (crown F+18.25) and holds a 0.3 x 5 mm 1.4310 +C1900 clock spring, 145.6 mm long,
  round the link-1a arbor; O3 diametric magnet in the arbor tip, sensor pocket in the crown.
- **Stops:** ISO 8734 O3 m6 dowels pressed in the upper boss, running in arc slots through the lower pad: one on J2
  (q2 -24.98 .. 100.84 deg, a 125.8-deg slot) and an opposed pair on K (stop A dK 0, stop B dK -34.47).
- **Verified BDp number:** Bench(110,360) exact gap 19.54 (score 92.89) at the user's fold margin 5, stops priced at 5.5.

All images are 1920 x 1080, Cycles at 192 spp (adaptive, OptiX denoise) on exo-blender-cycles (RTX 4090), saved as JPG
quality 92, made exactly as the gen-3 stills (`renders/2026-10-16_userstyle_pinknee_h1/README.md`):
- **Scenes:** `pipeline/full-exo/shots_plan.py` at `GRID=0.01` (0.01 mm vertex weld). Every camera, pose and the
  per-pose clearance are in `shots.json`.
- **Rendering:** `pipeline/joint-render/film_client.py stills ... --spp 192` with `render_stills.py` (smooth by angle 30 deg,
  `blast_rough` 0.5).
- **New in `shots_plan.py`:** an aim on named nodes (`"aim": "node:<substr>"`), a camera along a node's own axis
  (`"dir": "axis"`, `"flip"` for the skin side), `"drop"` (leave nodes out: the cap-off view), `"body": false` (hide
  the mannequin, clearance still measured) and an elbow / forearm override on clip poses.
- **New in `render_stills.py`:** the clock spring (polished spring steel) and the magnets map to polished stainless; they
  had fallen through to blasted metal.

## Look

- **Mannequin:** the rig skin with the smooth, faceless display head, matte charcoal-black (base 0.028, roughness 0.9,
  specular 0.2, no coat, no sheen), as gen 3. No gloss in any image.
- **Exo metal:** bead blasted (Ti, 7075, AlSi10Mg, 17-4PH): metallic satin with blast grain, roughness 0.5.
- **Hardware:** dowels, E-clips, screws, the clock spring and the magnet are polished stainless; bearings ground steel;
  the iglidur sleeves and thrust washers orange (the crescents in the clip gaps of `parts_knee_macro.jpg` and
  `parts_knee_rest_macro.jpg`).
- **No black parts.** The O3 stop dowels sit at the bottom of their 3.1 mm slots and read dark grey in the underside
  views (polished steel in a shadowed slot); they are not black.
- **The patchwork on the link tops and undersides is real geometry, not a render fault.** The v2 links are four 2 mm
  side-view strips side by side, each through its own strap row with its own line / arc profile; neighbouring strips
  differ by up to 0.5 mm in height and slope, so the light breaks into strip-wide facets (strongest on link 2,
  `parts_hubJ2_macro.jpg`, `parts_stop_J2_underside.jpg`). The mesh is closed and welded (0 open edges on link 1b).
  If the finished part should read as one smooth bar, a 0.5 mm blend over the strip steps would do it, at the cost of
  the strap following measured in the judge section.

## Images

Pose = (plane of elevation, elevation, axial rotation, elbow flexion, pronation) in degrees. Every clip frame used is
followed by the exo (no held frames).

| file | pose | camera |
|---|---|---|
| `parts_shoulder_top.jpg` | Raise overhead frame 36: (30, 65.9, -42.8, 12, 0) | Along the chain's plane normal: J1, link 1a, hub K (the tall spring cap), link 1b, J2, link 2, J3, member 3, knee, BOTTOM |
| `parts_shoulder_lateral.jpg` | same | Lateral, from above |
| `parts_shoulder_posterior.jpg` | same | Posterior-lateral, from above: all four hubs, three links and the knee |
| `parts_hubK_macro.jpg` | same | Along hub K's axis, tilted: the tall spring cap with its crown sensor pocket and flex groove, link 1a to J1 |
| `parts_hubJ2_macro.jpg` | same | Hub K, J1 and J2 with link 2 leaving J2 |
| `parts_hubK_capoff_spring.jpg` | same, **K cap left out** | Down hub K's axis: the clock spring's turns, its outer hook, the arbor with the magnet |
| `parts_hubK_capoff_oblique.jpg` | same, K cap left out | Oblique on the open spring chamber |
| `parts_stop_J2_underside.jpg` | same, **mannequin hidden** | From the skin side up J2's axis: link 1b's J2 pad with the 125.8-deg q2 slot and the O3 dowel |
| `parts_stop_K_underside.jpg` | same, mannequin hidden | From the skin side up K's axis: link 1a's K pad with the two opposed 34.5-deg slots and their dowels (resting on stop A), J2's slot at left |
| `parts_chain_underside.jpg` | same, mannequin hidden | The whole chain from the skin side |
| `parts_knee_top.jpg` | same | Member 3 + knee, along their plane normal |
| `parts_knee_macro.jpg` | same | Knee macro: plate, both pins and clips, iglidur crescents, pad mount |
| `hero_overhead_back.jpg` | Raise overhead peak, frame 78: (30, 150, -60, 12, 0) | Back-lateral three-quarter, whole exo |
| `hero_overhead_back_mid.jpg` | same | Back-lateral, mid shot on the shoulder |
| `hero_overhead_chain.jpg` | same | Close on the chain along its plane normal |
| `hero_shelf_front.jpg` | Reach a high shelf peak, frame 75: (82, 132, -82, 6, 0) | Front-lateral three-quarter |
| `hero_shelf_back.jpg` | same | Back-lateral three-quarter |
| `hero_shelf_chain.jpg` | same | Close on the chain, posterior-lateral |
| `kopen_chain.jpg` | Workspace pose 1134 of the verified model: (105, 120, -90, 90, 0); **K open dK -34.17 deg (0.3 deg short of stop B), q2 on its stop** | Close on the chain along its plane normal |
| `kopen_back.jpg` | same | Back-lateral three-quarter, whole exo |
| `kopen_hubK_macro.jpg` | same | Hub K, tilted along its axis |
| `rest_back_lateral.jpg` | Rest, Raise overhead frame 0: (30, 3, -30, 12, 0) | Behind-lateral, whole exo |
| `rest_back_chain.jpg` | same | Behind-lateral, from above, close on the chain |
| `rest_lateral_chain.jpg` | same | Lateral, close on the chain |
| `parts_knee_rest_macro.jpg` | same | Knee macro from the lateral side |

**Wash opposite shoulder peak: rendered, not shipped.** Frame 81, (145, 46.1, -69.4, 119.1, 0), is where the clips open
K (dK -2.19 deg, q2 on its -24.98 stop). All three views of it (back, back chain, hub K) showed a dark disc-and-rod
shape beside hub J3 that I could not attribute in the time box, and the display rig's arm sits 17-28 mm inside its own
chest at that pose (below). The images are left out. The K-open pose below stands in for it.

**Where K opens.** On the eight clips K opens only in Wash opposite shoulder (frames 70-85 and 119-127), at most
-2.19 deg, with q2 held on its -24.98 stop: the spring lets link 1b rotate a little so the chain can keep following.
That is too small to see, so the forced pose with K wide open comes from the verified model's workspace (pose 1134, one
of 133 workspace poses with dK below -10; the kin check of the build used the same pose). It is a static pose the
model reaches, not a clip frame.

## Measured gaps per pose

The gap is from each part group to this mannequin's skin, measured with libigl (fast winding number and point-mesh
distance) on the posed scene (`shots.json`, `clearance`). Minimum gap in mm; no group of our chain has a vertex inside
the skin in any pose.

| pose | base (J1) | l1a (link 1a, K pin) | l1b (link 1b, K cap, J2 pad) | l2 (link 2, J2 / J3 caps) | l3 (member 3, E strap) | l4 (knee plate) | closest chain part |
|---|---|---|---|---|---|---|---|
| rest | 9.56 | 2.42 | 3.31 | 5.74 | 3.99 | 7.80 | link 1a 2.42 |
| Raise overhead frame 36 | 7.79 | 4.68 | 6.30 | 9.61 | 6.26 | 9.65 | link 1a 4.68 |
| overhead peak | 3.85 | 0.82 | 0.23 | **0.04** | 7.29 | 10.48 | **J2 cap 0.04** |
| shelf peak | 7.63 | 4.08 | 5.49 | 2.62 | 5.89 | 8.97 | link 2 2.62 |
| wash peak (K -2.2) | 9.45 | 6.36 | 7.80 | 13.96 | 9.15 | 12.40 | link 1a 6.36 |
| K open (ws 1134) | 8.85 | 5.70 | 2.06 | 3.63 | 6.94 | 10.13 | link 1b 2.06 |

- **Overhead peak: hub 2's cap is 0.04 mm from the skin, and link 1b 0.23 mm.** This is the known weak spot of the
  verified shape (the verification found hub 2's wall within 0.05 mm at the same pose, plane 30, elev 150, axial -60);
  the full CAD carries it over unchanged from the L1. It is under the 1 mm near-touch line: in `hero_overhead_chain.jpg`
  the J2 cap sits on the skin with no visible gap. Nothing enters the skin.
- **Our arm-mounted part (D8-06: the cut BOTTOM + pad mount):** within 30 mm of pin b it clears the skin by at least
  3.86 mm (rest), 5.15 (frame 36), 5.48 (overhead peak), 4.77 (shelf), 6.41 (wash), 5.33 (K open). Its far end, 237-255 mm
  from pin b at the elbow end of the user's BOTTOM bar, is 1.6-2.0 mm inside the skin in the rest, overhead and shelf
  poses (4.0 mm in the K-open pose): the known R2 liner contact, as in gen 3.
- **The user's arm parts:** the forearm cuff sits 8.8 mm inside the display mannequin's forearm in every pose (its forearm
  is thicker than the user's: the gen-2 / gen-3 R2 overlap on a user part). The upper-arm cuff's rim shows the
  mannequin's arm through it as a dark jagged notch in `hero_overhead_back.jpg`; it is the same 1.5-1.9 mm overlap.
- **Wash peak (not shipped): the arm parts are inside the mannequin's chest** (upper-arm cuff and BOTTOM up to 17.7 mm,
  forearm cuff 28 mm). This does not depend on the elbow: at flexion 90 or 60 instead of 119 it is 18.4 / 18.9 mm, so
  it is the display rig's upper arm pressing into its own chest at plane 145 deg, not exo geometry. Our chain is
  6.4 mm or more from the skin.
- **Jagged skin round the axilla** in `hero_overhead_chain.jpg` is the rig skin folding at 150 deg elevation (skinning),
  as in gen 3.

## Checked by eye

Every shipped image was looked at full size or on a contact sheet: no part reads black, the mannequin is matte
everywhere (no gloss), and no exo part of ours shows through the skin. The two user-part overlaps above (upper-arm cuff
rim, forearm cuff) are the only places skin and metal cross on screen.

## Cost

GPU job time was 244.5 s on one RTX 4090 at $0.00031/s, about **$0.08**. With one cold start (47 s setup) and the idle
tails, at most about $0.12. It covered 8 stills jobs (one per scene, 28 frames), each rendered once. No endpoint
settings were changed.
