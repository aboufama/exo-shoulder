# Plan: the deep version of this project

Reframed with the "depth" questions (Felix Rieseberg, *How to be more ambitious*, Oct 2026): what would a field-leading
wearable-robotics engineer do, from what raw material, with which instruments, and what outside the model and the user
shows the result is right. The full method (altitude and range too) is in docs/METHOD.md.

## 1. What a top professional would do that the brief does not ask for

- **Treat shoulder-girdle motion as the core problem.** The glenohumeral centre translates several cm relative to the
  thorax in overhead reach (scapulohumeral rhythm). A spherical chain about one fixed point cannot follow that unless its
  base moves with the scapula, but the base bolts to a back plate on the thorax. Harmony (UT Austin), ANYexo (ETH),
  ArmeoPower either add girdle DOFs or bound the misalignment. This is the most likely root cause of "overhead is the
  hardest case". (R10)
- **Write requirements as numbers before designing** (REQUIREMENTS.md), not a single blended score: range per task,
  clearance, contact pressure (ISO/TS 15066), mass, stiffness and fatigue, singularity-free workspace.
- **Design for a population**, 5th-percentile female to 95th-percentile male, with adjustment - not one averaged body.
- **Derive link shapes from load paths** (topology optimisation inside the allowed skin-offset band), then make them
  beautiful, rather than sculpting surfaces by hand.
- **Check the workspace health of the chain**: Jacobian conditioning and distance to singularity along every task; the
  4th DOF exists to keep the chain away from singular configurations.

## 2. The rawest material

| Today (digested) | Raw |
|---|---|
| one averaged BodyParts3D rig with a hand-built skin model (`pipeline/avg`, `pipeline/arm-rom`) | **the user's own body**: phone LiDAR scans in ~6 poses (Polycam / Scaniverse) |
| 8 ADL clips synthesised from keyframes (`pipeline/full-exo/clips.json`) | **OpenCap** (Stanford, free) two-phone video of the user doing the 8 tasks -> OpenSim kinematics, plus held-out tasks |
| shoulder rhythm from a fixed rotation law in the rig | **OpenSim Seth 2016** thoracoscapular model (validated scapula / clavicle kinematics) |
| one body shape | **AMASS** motion archive and **SMPL-X** shape space (5th-95th percentile), held-out split |
| a blended "overall score" invented in this project | numbered requirements + outside judges |
| tessellated user parts | the user's STEP (`data/user_cad/`, source of truth) and their Onshape model (read-only) |

The rig is known to be wrong in places: a ~25 mm biceps bulge at full flexion, and the arm passes *through* the chest
(wash shoulder) and torso (walking, internal rotation) because the mesh has no contact model (docs/FINDINGS.md). Every
skin-clearance number inherits those errors until P2.

## 3. Methods and tools

| Need | Tool |
|---|---|
| human kinematics | OpenSim (Seth 2016, MoBL-ARMS), OpenCap |
| body shape + pose-dependent soft tissue | SMPL-X (+ pose correctives), registered to the user's scans |
| human + exo coupled, misalignment forces, contact | MuJoCo or Drake (soft contact), Pinocchio for chain Jacobians |
| clearance | exact signed distance (`judge/sdist.py`), continuous collision checking (FCL / coal) over trajectories |
| synthesis | multi-objective search (NSGA-II, or BoTorch to make the GPU evaluator cheaper to search), robust across a body-shape sample, returns a Pareto front (coverage vs clearance vs mass vs DOF) |
| CAD | constrained parametric modelling (build123d or Onshape FeatureScript); swept constant-section links, turned hubs, exact seats; zebra + curvature combs to prove G2 |
| structure | CalculiX (strength, deflection, fatigue), topology optimisation in the skin-offset band |
| manufacturing | tolerance stack, GD&T only where needed (docs/CAD_STANDARD.md), supplier DFM quote |
| test | SLA/SLS print + igus hardware, OpenCap, FSR strips / pressure film on the skin |

## 4. Outside judges

1. **A printed prototype on real arms** - the user and at least one very different body. OpenCap measures reach with
   vs without the exo; FSR strips on the skin catch any contact. (R11, R15)
2. **Held-out data** - motions and body shapes the optimiser never saw. (R14)
3. **Independent kernels and solvers** - STEP files re-imported and checked (OCC BRepCheck today, Onshape import next);
   CalculiX agreeing with the in-house FEA. (R7, R9)
4. **A supplier** - DFM review and quote. (R13)
5. **A standard** - ISO/TS 15066 body-region pressure limits. (R11)

The agent never grades its own work: every change is followed by the judges in `judge/` and the scorecard is what gets
reported.

## Phases

| Phase | Work | Needs from the user | Exit (judge) |
|---|---|---|---|
| P0 | **Base-mount physics.** Quantify GH translation vs thorax in the rig and in OpenSim Seth 2016; compute the misalignment a thorax-fixed base causes for the reference design; decide: passive girdle DOF inside the 4-DOF cap, a sliding/compliant base, or a scapula-tracking plate | OpenSim model download (permission) | R10 has a number and a decision |
| P1 | **Raw data.** Capture protocol in `data/raw/README.md`; ingest scans + OpenCap; define the held-out split | scans, OpenCap videos, AMASS / SMPL-X licences | data in `data/raw`, split committed |
| P2 | **Human model validation.** Register the rig (or SMPL-X) to the user's scans in each pose; fix the bulge / overlap artifacts | - | scan registration error reported per region |
| P3 | **Synthesis.** Multi-objective, robust across bodies, constraint: every link has a real arm (arc >= ~35 deg, see FINDINGS "short link"), Jacobian conditioning as an objective | GPU spend approval (state cost first) | Pareto front; scorecard R1-R6 on held-out data |
| P4 | **CAD** at the user's standard for the chosen design(s) | user review in `parts.html` | R7, R12 |
| P5 | **Structure + DFM.** CalculiX, tolerance stack, supplier quote | supplier account / quote request (user sends) | R9, R13 |
| P6 | **Prototype test.** Print, assemble, test on two bodies | printer / print service, a second person | R11, R15 |

P0 can start immediately with what is in this repo.
