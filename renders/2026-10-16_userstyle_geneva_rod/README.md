# Generation-5 winner (geneva-tail-knuckle-pinknee-3r, rod drive): full CAD stills, with a look audit

**Design:** `pipeline/full-exo/designs/user_geneva_rod`, built by `pipeline/conformal/param_cad/user_style_geneva.py`
(judged 5 of 19: `judge/scorecard.md`). Three ACTIVE revolutes J1, J2, J3 on v5 O20 hub stacks. The knuckle K is
**slaved, never read**. A constant-pressure spiral lobe on hub 2's rotor (D9-01) drives a bell crank on link 1b
(D9-02: MR63ZZ follower roller, MR85ZZ pair). The bell crank pushes an O3 Ti pushrod with igubal eyes (D9-03). The rod
turns a horn on K's flat cap (D9-04 / D9-05). Verified v_gap 23.57 (score 91.43) on Bench(110,360), exact and frozen;
held out 28.12. 0 passive translations, complexity 42.5.

**Caveat:** the CAD agent found that this full CAD loses R1 to its own L1 (80.3 % against 81.1 %; R1-aim 49.8 %
against 51.1 %), and that R7 fails on link 1a. Neither is fixed, and the agent said rendering should wait. These stills
show the CAD as it is now, at commit cae6a6e.

All 22 images are 1920 x 1080, Cycles at 192 spp (adaptive, OptiX denoise) on exo-blender-cycles (RTX 4090), saved as
JPG quality 92.
- **Scenes:** `pipeline/full-exo/shots_plan.py` at `GRID=0.01`. `shots.json` holds every scene spec, camera and pose,
  and each pose's sampled clearance.
- **Look:** `pipeline/joint-render/render_stills.py` with the new **`"look": 2`**. It is opt-in, so the gen-3 / gen-4
  look and any running render are unchanged.
- **GPU:** two passes. A 960 x 540 preview at 24 spp, then the final at 192 spp. About 2.5 min of 4090 time in all,
  roughly $0.05-0.10. That is an estimate from job times, not a billing readout.

## A. Look audit of the gen-3 / gen-4 stills, and what changed

The gen-3 stills (`renders/2026-10-16_userstyle_pinknee_h1/`) and the gen-4 stills
(`renders/2026-10-16_userstyle_minarc_bdp/`) look bad for these concrete reasons:

| # | what looks bad | where (example) | cause | fixed here? |
|---|---|---|---|---|
| 1 | Hub caps read as flat white discs, and the metal reads as grey plastic | gen-4 `parts_hubJ2_macro` (J1 cap), gen-3 `parts_shoulder_top` (domes) | AgX Medium High Contrast plus a small hard key (8 W, 0.8 x 0.5 m at 0.85 m) clips the caps. The world was a uniform grey (0.30 at 0.35), so blasted metal had nothing to reflect | **Yes (render).** Base Contrast, a key and fill about 2x larger and softer, and a studio-gradient world for reflections only (floor 0.16, horizon 0.24, ceiling 0.75; the camera still sees the seamless backdrop). Ti-grey metal at base 0.50 instead of 0.60. The caps now show a gradient and a rim |
| 2 | The mannequin is a flat black cut-out, with no muscles | most gen-4 close-ups | Medium High Contrast crushes the 0.028 skin to pure black | **Yes (render).** Base Contrast plus a second rim light. Skin base 0.02, roughness 0.9, specular 0.2, no coat or sheen: still matte black. Back, deltoid and arm muscles now read (`rest_back_chain`, `parts_four_hubs_posterior`) |
| 3 | Tile / mosaic shading on the link tops and undersides | gen-4 `parts_hubJ2_macro`, `parts_stop_J2_underside` | Two causes. (a) Render: plain vertex normals average the STEP tessellation's long thin triangles into the flat faces. (b) CAD: the v2 links are four 2 mm strips side by side, each with its own line / arc profile, differing in height and slope by up to 0.5 mm, so each flat segment catches the light differently | **(a) applied, not A/B-tested:** face-area weighted normals on every exo part (sharp edges over 30 deg kept). The tiles that remain match the strip facets. **(b) no:** the facets are real geometry and still show on link 2 (`parts_drive_lobe_macro`, `kopen_drive_lobe_macro`). Only a CAD change fixes it, below |
| 4 | A whole part could render in the wrong material | this build: the knee link's description names "sleeve bores" (iglidur rule), link 1b's names "dowel holes" (polished rule), and the MR63ZZ roller / "(polished)" pins named no rule | Materials were picked by keywords anywhere in the part description | **Yes (render).** Drawing-numbered parts (Dx-yy) are blasted metal first; igubal maps to iglidur orange; MR63 / MR85 / roller map to bearing steel; "(polished)" maps to polished stainless |
| 5 | The user's flat cuff and pad slabs fill the frame; macros have a blurred cuff in the foreground; subjects are cut at the frame edge; half-empty frames | gen-4 `parts_knee_macro` (half the frame is a blurred cuff), `parts_hubJ2_macro` (J3 cut), `parts_stop_J2_underside` | Bounds over whole groups, wide f-stops in macros | **Yes (framing).** Macros aim at named node sets (knee: pins + knee link; drive: lobe, roller, bell crank, J2 cap) at f/22, so nothing near the camera is a smear. Every hero has a mid shot aimed at the chain. One substring bug was found and fixed: "pin a" also matched "horn **pin a**t r 2.493", which framed the whole body |
| 6 | Torn / crumpled skin in the armpit and over the raised deltoid at elevation 120 deg and above, and a crease near the scapula | gen-4 `hero_overhead_chain`; here `hero_overhead_chain`, `hero_shelf_chain`, `kopen_chain` | The display rig's skinning at extreme poses. This is not the judges' skin and not a render fault | **Partly (framing).** `hero_overhead_chain_back` views the overhead peak from behind and above, where the tear is smaller. Only a rig fix removes it (corrective smoothing of the display skin, or better skinning). Smoothing the skin at render time was not done, because it would move the skin the clearance below is measured against |
| 7 | Large flat "+"-shaped pad mount + BOTTOM slabs and a sheet-like upper-arm cuff, beside a machined chain | every hero | CAD | **No:** CAD |
| 8 | Hub caps are featureless domes; there is no machining detail | all close-ups | CAD | **No:** CAD |
| 9 | No scale cue | all | Nothing in frame has a known size | Not fixed. The hubs are O20 (about a 20-cent coin); a prop was not added |
| 10 | Background / ground | n/a | The seamless light-grey backdrop is fine | Kept |

**Still needs a CAD change, in order of visual impact:**
1. **Link-2 / link-1b strip facets.** Either a 0.5 mm blend over the strip steps, or each strip profile as fewer, longer
   tangent arcs instead of short lines. Either one costs some strap following, which has to be re-judged.
2. **The pad mount + BOTTOM "+" slabs and the upper-arm cuff.** Shape them in the same bent-bar language as the chain:
   bend arcs, rounded ends, edge rounds on the cuff.
3. **Featureless caps.** Add a spanner-hole pair or a 0.3 mm chamfer ring on the crown, so they read as machined parts.
4. **The drive lobe ring is hard to see.** It sits under the J2 cap overhang (it stands only 2.87 mm past the O20
   skirt). Here it shows only as a sliver beside the roller (`parts_drive_lobe_macro`, `kopen_drive_lobe_macro`) and
   as a band in the bodyless side views. A CAD section or a cap-off view would show the lobe profile.

## B. Images

Pose = (plane of elevation, elevation, axial rotation, elbow flexion, pronation) in degrees. No clip frame used is
held. dK is the knuckle's opening, set by the drive.

| file | pose | camera |
|---|---|---|
| `parts_four_hubs_posterior.jpg` | Raise overhead frame 36: (30, 65.9, -42.8, 12, 0), dK 0 | Posterior-lateral from above: J1, K (flat cap with the horn), J2 with the bell crank, J3, the knee, the pad |
| `parts_shoulder_top.jpg` | same | Along the chain's plane normal |
| `parts_drive_closeup.jpg` | same | The drive along its own plane: horn + igubal on K's cap, the O3 pushrod, the bell crank tube on its post, the MR63ZZ roller at the lobe, the J2 cap |
| `parts_drive_oblique.jpg` | same | The drive from the side: hub-stack heights, rod over link 1b |
| `parts_drive_lobe_macro.jpg` | same | Down J2's axis, from the roller side: the roller's balls, the crank igubal, the lobe tip as a sliver past the cap |
| `parts_drive_lobe_side.jpg`, `parts_drive_lobe_side2.jpg` | same, **mannequin hidden** | Side views at hub height, tangent to the lobe / roller contact, from both sides |
| `parts_knee_macro.jpg` | same | Knee: plate, both pins with their E-clips, iglidur crescents, the knee stop tooth, the pad mount |
| `parts_knee_oblique.jpg` | same | Knee from the posterior side |
| `kopen_drive_closeup.jpg` | Workspace pose 917: (75, 120, -105, 90, 0), **dK -43.30 deg** (stop B -53.64), q = (54.5, -18.6, 97.0) | The drive with K turned 43 deg: horn rotated, rod and bell crank swung |
| `kopen_drive_lobe_macro.jpg` | same | Down J2's axis, from the roller side |
| `kopen_chain.jpg` | same | The chain along its plane normal, arm raised to the side |
| `kopen_back.jpg` | same | Back-lateral, mid shot |
| `hero_overhead_back.jpg` | Raise overhead peak, frame 78: (30, 150, -60, 12, 0), dK 0 | Back-lateral three-quarter, whole exo |
| `hero_overhead_back_mid.jpg` | same | Back-lateral, mid shot on the shoulder |
| `hero_overhead_chain.jpg` | same | Close on the chain along its plane normal (rig tear visible, row 6) |
| `hero_overhead_chain_back.jpg` | same | Close on the chain from behind and above (smaller rig tear) |
| `hero_shelf_back.jpg` | Reach a high shelf peak, frame 75: (82, 132, -82, 6, 0), **dK -15.88 deg** (the drive turns K on this clip) | Back-lateral three-quarter, whole exo |
| `hero_shelf_mid.jpg` | same | Back-lateral, mid shot |
| `hero_shelf_chain.jpg` | same | Close on the chain along its plane normal |
| `rest_back_lateral.jpg` | Rest, Raise overhead frame 0: (30, 3, -30, 12, 0), dK 0 | Behind-lateral, whole exo |
| `rest_back_chain.jpg` | same | Behind-lateral, from above, close on the chain |

**Checked in every image:**
- No part reads black. The darkest are the J2 cap in shade and the post bore: mid-grey metal.
- No gloss on the mannequin.
- No part of ours is visibly through the skin. The overhead lobe ring below is 0.23 mm deep and is not visible at any
  framing used.

In the K-open pose q2 is -18.6 deg, 3.2 deg from its -21.81 stop.

## Skin clearance per pose (display mannequin)

Every vertex of each of our parts was checked against the posed display mannequin, using the winding number for inside
and the closest-point distance for depth. The display mannequin is the rig's render skin with the smoothed head; it is
**not** the evaluator's fitted skin that the judges and the bench use. A negative value means the part is inside the
skin by that depth.

| pose | closest part of ours | min gap | next | drive groups (dk / dr) |
|---|---|---|---|---|
| Raise overhead f36 (parts) | link 1b | 4.41 mm | link 1a 4.94 | 11.83 / 21.31 |
| WS 917, K open 43.3 deg | link 2 | 2.00 mm | link 1b 2.04 | 10.78 / 25.85 |
| **Raise overhead peak f78** | **D9-01 drive lobe ring** | **-0.23 mm** (inside) | link 1a 1.13, J2 cap 2.25 | 8.11 / 5.07 |
| Reach a high shelf f75 | link 2 | 2.62 mm | link 1b 4.24 | 13.12 / 27.90 |
| Rest f0 | member 3 | 3.75 mm | link 1a 3.98 | 16.98 / 24.70 |

- **Overhead peak: the drive's lobe ring touches the display skin.** The ring stands 2.87 mm past the O20 skirt by the
  red team's spec, and it sits 0.23 mm inside the display rig's raised deltoid at frames 76-80. In the same region the
  judge saw the R1 minimum gap on Raise overhead drop from 1.1 mm (L1) to 0.2 mm (full CAD). It is a real
  proud-of-hub feature on the skin side, not a render artefact.
- **Next CAD step for the lobe ring:** move the lobe to the hub's upper half, or trim the lobe's dwell arc where it
  faces the skin. Then re-judge R1 / R6.
- **Other K-open candidates were rejected.** Workspace pose 923 (dK 44.3) put link 2 0.33 mm into the display skin, so
  pose 917 was used.
- **Arm-side parts:** D8-06 (BOTTOM + arm pad + pad mount) sits 1.9 mm (rest), 1.9 mm (overhead) and 4.0 mm (pose
  917) inside the display rig's arm.
- **The user's parts:** the elbow thrust washer is 0.8-2.5 mm inside the display rig's arm, and the forearm cuff
  8.8-11.1 mm inside. Gen 4 showed the same numbers on the same display rig (pad 1.5, forearm cuff 8.8): this is the
  rig's arm against the scanned-arm cuffs, not the shoulder chain.

## Reproduce

```
SPEC=$(python3 -c "import json;print(json.dumps(json.load(open('renders/2026-10-16_userstyle_geneva_rod/shots.json'))['scenes']['<scene>']))")
GRID=0.01 python3 pipeline/full-exo/shots_plan.py pipeline/full-exo/designs/user_geneva_rod <out> "$SPEC"
RUNPOD_API_KEY=... <flash python> pipeline/joint-render/film_client.py stills <out>/scene.glb <out>/motion.json <out>/png --spp 192
```

Each scene in `shots.json` carries a `pose_p` and a `clearance` field; `shots_plan.py` ignores both. The look keys are
`look`, `blast_rough`, `skin` and `exposure`, and `shots_plan.py` passes them through to `motion.json`.
