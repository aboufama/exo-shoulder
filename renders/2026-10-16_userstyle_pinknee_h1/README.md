# Generation-3 winner (polished H1): skin-normal-3r-pin-knee, full CAD in the user's style

**Design:** `pipeline/full-exo/designs/user_pinknee_h1`, built by `pipeline/conformal/param_cad/user_style_pinknee.py`
from the verified H1 parameter dict. The judged scorecard (8 of 19) is `judge/scorecard.md`; the design is described in
`docs/concepts/skin-normal-3r-pin-knee.md`, section "Full user-style CAD of the polished H1".

- **Joints:** 3 pins on v5 O20 hub stacks. J1 and J2 sit on GH rays; J3 sits on its offset line, tilted toward the skin normal.
- **Cuff closure:** a flat two-pin knee instead of gen 2's crossed rails.
  - Member 3 carries the E strap and an O12 boss with an integral O4 pin a.
  - The knee plate is 40.2 x 10 x 2.59 mm Ti.
  - Pin b is integral to the BOTTOM + pad mount part (7075).
  - Each pin has an iglidur GSM-0405-03 sleeve, a 4 x 8 x 0.5 iglidur thrust washer and a DIN 6799-3.2 clip.
- **Passive translations:** 0.
- **Verified H1 number:** Bench(110,360) exact gap 26.45 (score 90.4) at fold margin 10, and 24.48 (score 91.1) at the user's margin 5.

All images are 1920 x 1080, Cycles at 192 spp (adaptive, OptiX denoise), rendered on exo-blender-cycles (RunPod ADA_24,
RTX 4090) and saved as JPG quality 92.
- **Scenes:** made with `pipeline/full-exo/shots_plan.py` at `GRID=0.01`. That is a 0.01 mm vertex weld; the default 0.2 mm collapsed the dome caps' fine triangles.
- **Cameras and clearance:** `shots.json` lists every camera and the per-pose skin clearance.
- **Rendering:** `pipeline/joint-render/film_client.py stills ... --spp 192`.

## Look

- **Mannequin:** the rig skin with the smooth, faceless display head, in matte charcoal-black.
  - Material: base 0.028, roughness 0.9, specular 0.2, no coat, no sheen. This is the gen-2 default in `render_stills.py`.
  - Back, deltoid and arm muscles read under the key and rim lights.
- **Exo metal:** bead-blasted for the Ti, 7075 and AlSi10Mg parts: metallic satin with a fine blast-grain bump, **roughness 0.5**.
  - It is set by the new `blast_rough` key in motion.json. The default stays 0.38 for other designs.
  - At 0.38, a dome cap facing the camera mirrored the dark studio world and read near-black (first pass, J2 cap in the overhead chain view).
- **Hardware:**
  - Screws and the DIN 6799 E-clips are polished stainless. The clips are newly mapped: they had fallen through to blasted metal.
  - Bearings are ground bearing steel.
  - The iglidur sleeves and thrust washers are orange.
- **No black parts.** The polished clips mirror the dark studio and read dark grey in the knee macros; they are bright stainless at other angles.
- **Shading fix in `render_stills.py`:** exo parts are now smooth-shaded by angle (30 deg).
  - With plain smooth shading, the welded vertices on creases averaged across them.
  - That drew radial streaks on the dome caps and wavy highlights on flat plates.
  - The first-pass parts stills (kept out of this folder) showed it, and so do the gen-2 stills.
- **Where the iglidur shows:** each sleeve is pressed into the knee plate bore under its clip, so the orange shows as a crescent in the clip's gap at each pin. The thrust washers are hidden under the 10 mm wide plate.
  - `parts_knee_rest_macro.jpg` and `parts_knee_macro.jpg` are the shots where the crescents read.

## Images

The pose is given as (plane of elevation, elevation, axial rotation, elbow flexion, pronation) in degrees. All three
poses are frames the design follows: every frame of Raise overhead and of Reach a high shelf is followed, with no held
frames.

| file | pose | camera |
|---|---|---|
| `parts_shoulder_top.jpg` | Raise overhead frame 36: (30, 65.9, -42.8, 12, 0); knee 105.4 deg | Along the chain's plane normal, from above: base (J1), link 1, J2, link 2, J3 + member 3, knee, BOTTOM |
| `parts_shoulder_lateral.jpg` | same | Lateral, from above |
| `parts_shoulder_posterior.jpg` | same | Posterior-lateral, from above: all three hubs, both links and the knee in one frame |
| `parts_knee_top.jpg` | same | Close on member 3 + knee, along their plane normal |
| `parts_knee_lateral.jpg` | same | Close on J3, the E strap and the knee, lateral |
| `parts_knee_macro.jpg` | same | Knee macro: plate, both pins and clips, iglidur crescents, pad mount |
| `parts_knee_rest_macro.jpg` | Rest: Raise overhead frame 0, (30, 3, -30, 12, 0); knee 101.6 deg | Knee macro from the lateral side: E strap down to pin a, knee plate, pin b on the arm pad, pad mount + riser on BOTTOM |
| `hero_overhead_back.jpg` | Raise overhead peak, frame 78: (30, 150, -60, 12, 0); knee 144.1 deg | Back-lateral three-quarter view, whole exo |
| `hero_overhead_back_mid.jpg` | same | Back-lateral, mid shot on the shoulder |
| `hero_overhead_chain.jpg` | same | Close on the chain along its plane normal |
| `hero_shelf_front.jpg` | Reach a high shelf peak, frame 78: (82, 132, -82, 6, 0); knee 135.2 deg | Front-lateral three-quarter view |
| `hero_shelf_back.jpg` | same | Back-lateral three-quarter view |
| `hero_shelf_chain.jpg` | same | Close on the chain, posterior-lateral |
| `rest_back_lateral.jpg` | Rest (as above) | Behind-lateral, whole exo |
| `rest_back_chain.jpg` | same | Behind-lateral, from above, close on the chain |
| `rest_lateral_chain.jpg` | same | Lateral, close on the chain |

At the overhead peak the knee sits at 144.1 deg, 5.4 deg inside its 149.54 stop. That is this followed clip frame; the
149.2 deg edge in the concept doc is the bench's worst Raise overhead pose at margin 10, not this frame.

## Measured gaps per pose

The gap is from the exo to this mannequin's skin, measured with libigl (fast winding number and point-mesh distance)
over the posed scene, in `shots.json`. Negative means inside the skin.

| pose | base: J1 member + bearings | l1: link 1 + nuts | l2: link 2 + J2 / J3 bearings and caps | l3: member 3 + E strap + boss | l4: knee plate + sleeves | contact by our parts |
|---|---|---|---|---|---|---|
| rest | 12.3 mm | 8.9 mm | 8.4 mm | 4.5 mm | 8.0 mm | none |
| Raise overhead frame 36 | 10.1 mm | 3.1 mm | 5.9 mm | 7.4 mm | 10.8 mm | none |
| overhead peak | 4.7 mm | **1.8 mm** | 3.0 mm | 7.8 mm | 11.3 mm | none |
| shelf peak | 9.1 mm | 6.1 mm | 6.6 mm | 4.8 mm | 8.5 mm | none |

- **No exo part of ours enters the body in any image.**
  - The BOTTOM + pad mount part reaches 1.5-1.7 mm inside the skin. All of those vertices are 243-261 mm from pin b, at the elbow end of the user's BOTTOM bar: the known R2 liner contact.
  - Within 30 mm of pin b, the mount, the riser and the pad clear the skin by at least 4.6 mm (rest), 6.8 mm (overhead peak) and 5.9 mm (shelf peak).
- **The dark notch at the forearm cuff's rim is the mannequin's forearm.** It shows in `hero_shelf_back.jpg` and `hero_overhead_back.jpg`.
  - The user's forearm cuff (F|FOREARM CUFF) sits 8.8 mm inside the display mannequin's forearm in every pose, because the mannequin's forearm is thicker than the user's.
  - This is the known R2 overlap on a user part, the same as in the gen-2 stills. It is not exo geometry.
- **Jagged skin around the axilla in `hero_overhead_chain.jpg`** is the rig skin folding at 150 deg elevation (skinning), not exo geometry.
- **Link 1 (l1) at 1.8 mm** in the overhead peak is the closest metal in these images. It is above the 1 mm near-touch line.

## Cost

GPU job time was 137.6 s on one RTX 4090 at $0.00031/s, which is **about $0.04**. With two cold starts and the idle tails, the total is at most about $0.10. It covered 13 stills jobs:

- **First pass:** 4 scenes, 14 frames.
  - The overhead front view was hidden by the arm.
  - The parts stills showed streaked dome caps.
- **Second pass:** smooth-by-angle and the 0.01 mm weld; all 4 scenes again, plus 2 grazing knee views.
  - The grazing views were blocked by the BOTTOM bar and were dropped.
- **Third pass:** satin roughness 0.5, every scene again, plus the knee macros.
  - The rest-pose grazing view was dropped.

No endpoint settings were changed.
