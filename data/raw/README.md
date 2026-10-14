# Raw data to collect (phase P1 in docs/PLAN.md)

Nothing here yet. The current human model is a stock rig with synthetic motions; these inputs replace or validate it.
**Body scans and motion of a person are personal data: keep them in `data/raw/private/` (git-ignored) unless the user
explicitly says otherwise.**

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
