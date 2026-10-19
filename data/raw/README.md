# Raw data to collect (phase P1 in docs/PLAN.md)

Nothing here yet. The current human model is a stock rig with synthetic motions; these inputs replace or validate it.
**Body scans and motion of a person are personal data: keep them in `data/raw/private/` (git-ignored) unless the user
explicitly says otherwise.** The held-out split is fixed in `split.json` (committed before any search uses it).

## What is needed from the user, and which requirement each one moves (2026-10-14)

| # | input | user effort | requirement status it changes, and why |
|---|---|---|---|
| 0 | **Ruler test** (no app): mark the top of the acromion against a door frame with the arm hanging, then at 90 deg abduction and at 90 deg forward flexion; measure the rise | 1 minute | **R10**: the rig predicts a 13 mm rise at 90 deg, the published bone-pin chain ~35-38 mm (abduction / scaption) and ~25 mm (flexion). The first real number for the girdle law that every 3-DOF design is fitted to. |
| 1 | **Permission to download OpenSim 4.x + the Seth 2016 thoracoscapular model** (simtk.org) - and **your acceptance of its licence** (the 2016 data/model is CC BY-NC-SA; the 2019 thoracoscapular model is CC BY 4.0, per docs/research/gh_translation_literature.md) | a yes + the licence | **R10** goes from "a number on the rig's hand-made girdle law" to a number on a validated scapulothoracic model. P0 showed the 3-DOF designs hinge on how the GH centre moves vs the thorax (rig: purely superior, 0 below 30 deg, 25 mm at 150 deg); a design fitted to the rig law loses 1-6 mm of margin when the law changes (P0 section 6). Also tests the rig's scapula rhythm (FINDINGS: unvalidated belief). |
| 2 | **OpenCap** (opencap.ai): the 8 design tasks **3 times each**, the 5 held-out tasks, plus one shoulder shrug and one reach with ~2 kg in the hand | ~20 min, two iPhones on tripods, printed checkerboard | **R10**: the acromion/shoulder markers vs the thorax markers give *your* GH-girdle translation; the repeats measure how much of it is a repeatable function of arm angle - which is exactly what a 3-DOF offset-axis design can absorb and a shrug or load cannot. **R3/R4**: real motion replaces synthetic keyframes. **R14**: the held-out tasks become the first data the design never saw. |
| 3 | **Phone LiDAR scans** (Polycam / Scaniverse) in the 6 poses below + upper-arm length and relaxed / flexed circumference | ~10 min | **R1, R2** are computed today on a stock rig with known errors (25-30 mm biceps bulge at full flexion, arm passing through the chest / torso, FINDINGS); registering the rig to your scans (P2) turns them into numbers on your body. The circumferences size the humeral-rotation ring (radius and opening). |
| 4 | **AMASS and SMPL-X licences** (you register and accept; the agent never does) | ~10 min of sign-up | **R14**: SMPL-X body shapes (5th-95th percentile) for the robust search and held-out bodies; AMASS adds hundreds of everyday motions for held-out testing. Until then robustness is a uniform-scale proxy only. |
| 5 | Decisions, not data: R8 mass budget (300 g proposed, stretch < 150 g); R10 threshold (4 mm proposed = half the 2-10 mm band); whether a passive (unactuated) joint counts toward the 3-DOF target; the 14 mm allowance for nested links (recorded as your words, 2026-10-14; 10 mm stays the target) | a reply | turns the "proposed" thresholds into requirements |

## 1. The user's body (user action, ~10 min with a LiDAR phone)

Scan app: Polycam or Scaniverse (LiDAR mode), tight shirt or bare shoulder, arm held still for each pose. Export OBJ/PLY.

| pose | plane / elevation / axial / elbow |
|---|---|
| arm at side | 0 / 0 / 0 / 0 |
| abduction 90 | 0 / 90 / 0 / 0 |
| flexion 90 | 90 / 90 / 0 / 0 |
| overhead | 90 / 150 / 0 / 0 (as high as comfortable) |
| hand to opposite shoulder | 120 / 60 / -60 / 120 |
| hand behind back (back pocket) | -60 / 30 / 80 / 70 |

Also: a tape measure of upper-arm length (acromion to lateral epicondyle) and upper-arm circumference relaxed / flexed.

## 2. The user's motion (user action, ~15 min)

OpenCap (opencap.ai, free, Stanford): two iPhones on tripods, calibration board, follow its protocol. Record the 8
design tasks (raise overhead, drink, comb hair, high shelf, wash opposite shoulder, back pocket, wave, walking arm
swing) **and** held-out tasks that are never used for design: e.g. put on a jacket, reach into a car seat belt,
lift a box to a shelf, throw underarm, scratch the back of the neck. OpenCap returns OpenSim .mot kinematics.

## 3. Shoulder-girdle model (download needs the user's OK)

OpenSim 4.x + the Seth 2016 thoracoscapular shoulder model (simtk.org). Used in P0 for GH translation relative to the
thorax and in P2 to validate the rig's scapulohumeral rhythm.

## 4. Population (the user must register and accept the licences themselves)

- AMASS (amass.is.tue.mpg.de): motion capture as SMPL-X bodies - extra ADL motions for a held-out set.
- SMPL-X (smpl-x.is.tue.mpg.de): body shapes for 5th-95th percentile robustness.

## Held-out rule

Decide the split once, commit `data/raw/split.json` (which clips / bodies are held out) before any synthesis uses the
new data, and never optimise against the held-out set.
