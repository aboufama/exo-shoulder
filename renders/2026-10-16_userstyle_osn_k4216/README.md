# Generation-2 winner: offset-skin-normal-3r k4216, full CAD in the user's style

Design: `pipeline/full-exo/designs/user_osn_k4216`. It has 3 pins (J1 and J2 on GH rays, J3 on its offset line tilted
toward the skin normal) and two self-aligning cuff slides (THK RSR3M / HIWIN MGN03C class guides, 10.5 mm stack).
The build is in `pipeline/conformal/param_cad/user_style_osn.py`. The judged scorecard (5 of 19) is in
`judge/scorecard.md` and `docs/concepts/offset-skin-normal-3r.md`.

All images are 1920 x 1080, Cycles at 192 spp (adaptive, OptiX denoise), rendered on exo-blender-cycles (RunPod ADA_24,
RTX 4090), JPG quality 92. Scenes come from `pipeline/full-exo/shots_plan.py`, and `shots.json` lists every camera.

## Look

- **Mannequin:** the rig's skin with the smooth, faceless display head (`mannequin.py`).
  - Matte black: base 0.028, roughness 0.9, specular 0.2, no coat, no sheen.
  - The 10-15 stills (base 0.018, rough 0.55, coat 0.15) were glossy. The first 10-16 pass (base 0.004) showed a flat silhouette with no muscles.
- **Exo parts:**
  - Bead-blasted metal for the 7075 / Ti / AlSi10Mg parts.
  - Polished stainless screws.
  - Ground bearing steel for the bearings and the miniature guides.
  - No black parts.
- **No iglidur parts are visible.** The only iglidur part in the model is the user's thrust washer in the arm assembly, and it is hidden at these angles.

## Images

The pose is given as (plane of elevation, elevation, axial rotation, elbow flexion, pronation) in degrees. The gap is
the exo's distance to this mannequin's skin, measured by `clearance.json` with libigl (fast winding number and
point-mesh distance).

| file | pose | camera |
|---|---|---|
| `parts_shoulder_top.jpg` | Raise overhead frame 36: (30, 66, -43, 12, 0), the clip's highest followed frame | Along the chain's plane normal, from above. Shows the scapula base tab (2x M4), J1 hub, link 1, J2 hub, link 2, J3 + member 3, the cuff stage and BOTTOM. |
| `parts_shoulder_lateral.jpg` | same | Lateral, from above |
| `parts_shoulder_posterior.jpg` | same | Posterior-lateral, from above |
| `parts_cuff_stage.jpg` | same | Close on member 3 and the stage: carriage B on the across rail, the plus-shaped carriage A, the along rail and the inverted block on BOTTOM |
| `hero_overhead_back.jpg` | Raise overhead peak (30, 150, -60, 12, 0), see the note below | Back-lateral three-quarter view |
| `hero_overhead_chain.jpg` | same | Close on the chain along its plane normal, from behind |
| `hero_shelf_front.jpg` | Reach a high shelf frame 84: (82, 132, -82, 6, 0), the clip's peak | Front-lateral three-quarter view |
| `hero_shelf_back.jpg` | same | Back-lateral three-quarter view |
| `hero_shelf_chain.jpg` | same | Close on the chain, posterior-lateral |
| `rest_back_lateral.jpg` | Rest: Raise overhead frame 0, (30, 3, -30, 12, 0) | Behind-lateral, whole exo |
| `rest_back_chain.jpg` | same | Behind-lateral, from above, close on the chain |
| `rest_lateral_chain.jpg` | same | Lateral, close on the chain |

**The Raise overhead hero is not a frame the clip follows.**
- In the scapular plane the chain closes only at an axial rotation of -60 deg or less once elevation passes about 70 deg.
  - The verified model's workspace grid (plane 30) closes at axial -60 and -75 from elevation 60 to 150, and at -75 only at 165.
  - At axial -45 it does not close from 75 deg up.
- The clip's path runs at -43 to -57 deg, so this design's clips.json holds every frame from elevation 66 deg to the top (frames 37-143).
- The hero shows the clip's peak pose itself. That is workspace pose 608, (30, 150, -60), which closes and is feasible in the verified model: slides -11.2 / -3.9 mm, in range; part clearance at least 1 mm. The elbow is set to the clip's 12 deg.
- A wearer reaches it with more external rotation on the way up than the clip uses.

**Measured gaps per pose (exo to skin; negative = inside the skin):**

| pose | link 1 | link 2 | member 3 | stage | base tab | contact |
|---|---|---|---|---|---|---|
| rest | 7.9 mm | 10.9 mm | 7.0 mm | 7.5 mm | 11.5 mm | none |
| Raise overhead frame 36 | 2.0 mm | 4.2 mm | 12.9 mm | 11.7 mm | 9.5 mm | none |
| overhead peak | 1.6 mm | 3.1 mm | 11.1 mm | 10.6 mm | 4.9 mm | none |
| shelf peak | 5.8 mm | 4.6 mm | 6.4 mm | 7.3 mm | **-1.64 mm** | base tab |

- **The base tab at the shelf peak is a real defect, not a render error.** The scapula base tab sits 1.64 mm inside the skin, in 177 of 6730 samples. You can see it in `hero_shelf_chain.jpg`, where the tab's free end dips into the skin above J1. The judges measured the same 1.64 mm at Reach a high shelf frame 78. It is the base-tab issue in the concept doc (fit the tab to the clip + workspace envelope).
- **The user's arm parts in the skin are the known R2 overlap, not new.** BOTTOM and the upper cuff dip up to 2.0 mm into the skin; that is liner contact. The user's forearm cuff dips 8.8 mm into the mannequin's forearm.
- **Jagged skin above the chain in `hero_overhead_chain.jpg`.** This is the rig skin folding at 150 deg elevation (skinning). It is not exo geometry.

## First pass (kept for the record)

`first_pass_flat_mannequin/` holds the first stills of this build, made with the earlier silhouette mannequin (base 0.004):
- `hero_overhead_*` is Comb hair at elevation 143, not Raise overhead.
- `hero_shelf_*`, `hero_back_*` (Reach back pocket) and `hero_drink_*`.

## Cost

The GPU work came to about 150 s of job time on one RTX 4090 at $0.00031/s:
- 120 s for the successful jobs:
  - a 4-frame material test at 960 x 540 / 64 spp
  - two passes of 4 scenes at 13 frames in total
- about 30 s for 2-3 jobs that failed on stale frames (see below)

That is about $0.05 of job time. With the cold start and the 30 s idle tails, it is at most about $0.10. No endpoint settings were changed.

## Why stills jobs failed before (fixed in the client)

The worker renders into `/tmp/job_<a>` and counts every PNG there. On a warm worker, a second stills job with `a = 0`
found the previous job's frames, so the count failed.

That is why the 10-16 notes recorded "bodyless parts scenes fail after the glTF import" and "5 sets at once fail".

`film_client.py stills` now gives every job a fresh frame offset and renames the frames back. It is a client-side fix; the endpoint is unchanged.
