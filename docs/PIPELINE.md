# Pipeline map

All code lives in `pipeline/` with its original directory names (the scripts reference each other by relative path).
Run Python from the directory of the script unless noted. Use the Python that has cadquery 2.5 / OCP 7.7
(`tools/setup.sh`).

| dir | what |
|---|---|
| `avg/` | the human: average body rig (`body_pose.py`: posed skin for plane/elev/axial/flex/pron, numpy port of `arm-rom/body.js`), `body_mesh.json`, `body_rig.npz`, design search on radial skin maps |
| `arm-rom/` | the anatomy build (BodyParts3D, muscles, skin), browser rig `body.js`, early ROM studies |
| `full-exo/` | the arm side and the judge of record: `score_design.py` (honest score), clips (`clip_keys.py`, `make_clips_full.py`), user CAD loader (`load_arm.py`), viewers (`index.html`, `parts.html`, `joint.html`, `film.html`), report / film / stills planning |
| `conformal/gpu/` | GPU band evaluator (`band_impl.py`, RunPod Flash `worker.py`) |
| `conformal/gpu_client/` | search clients (`band_client.py` on RunPod, `local_search.py` / `detail_local.py` on CPU), search configs and results |
| `conformal/band_cad/` | search result -> design dir (`make_cad_design.py`), BOTTOM / arm frames (`arm_end.py`), older loft CAD |
| `conformal/fair_cad/` | **current CAD**: `fair_pipeline.sh` (band design -> replan -> members -> verify -> assemble), `members.py` (swept-band links), `sheet.py` (G2 sheet bodies), `armend_fair.py` (turned JN hub + neck + BOTTOM merge), `joint_v4.py` + `hardware.py` (joint stack), `cuff_*.py` (upper-arm saddle), `parts_export.py` |
| `conformal/thin_study/` | in-house FEA (hex8) of links / rails / joint hardware |
| `shoulder-d4/` | G2 CAD helpers (`g2cad.py`) and the earlier D4 shoulder |
| `joint-render/` | Blender Cycles stills / film on RunPod (`flash_app/`, `render_stills.py`, `render_film.py`, `film_client.py`) |

## Common tasks

```bash
# setup (once): python deps + the dense skin-map cache
bash tools/setup.sh
python3 tools/build_maps.py            # -> .cache/maps_s1.pt (~860 MB; CPU, slow) - needed by fair_cad/envelope.py and detail_local.py

# re-assemble the reference design from its committed member fields (no search, no maps needed)
cd pipeline/conformal/fair_cad && python3 fair_build.py r13_n4_s1343_1 assemble && cd -
bash tools/publish_design.sh r13_n4_s1343_1   # exo.glb + step/ + parts into pipeline/full-exo/designs/cad_<key>/

# judge it (see README)
bash tools/judge_all.sh cad_r13_n4_s1343_1

# full CAD build of a searched design (needs .cache/maps_s1.pt and band_cad/inputs/<key>.json)
cd pipeline/conformal/fair_cad && bash fair_pipeline.sh <key> "<label>"

# upper-arm cuff saddle
cd pipeline/conformal/fair_cad && python3 cuff_envelope.py 1 && python3 cuff_trunkmap.py && python3 cuff_fair.py

# viewers
cd pipeline/full-exo && python3 -m http.server 4198   # index.html?d=<id>, parts.html?d=<id>, joint.html
```

## GPU search (paid - state GPU type and cost before running)

`conformal/gpu_client/band_client.py search <cfg json>` against the Flash endpoint (`BAND_EP`, default `exo-band10`).
Needs `RUNPOD_API_KEY` in the environment (never commit it, never print it). Deploy code changes under a new endpoint
name (warm workers keep old code). r13 cost ~5 jobs x ~35 min on RTX PRO 6000 MIG slices.
