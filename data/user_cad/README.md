# User CAD (source of truth, read-only)

`RIGHT ARM SUBASSY.step` - the user's arm exo (Onshape export): TOP, MIDDLE (forearm link), BOTTOM (upper-arm link,
30 x 6.5 bar), FOREARM CUFF, elbow hardware, the earlier scissor shoulder. Loaded by `pipeline/full-exo/load_arm.py`
(override with `USER_CAD=<path>`).

Rules: never modify these parts except BOTTOM (may be cut at s = 265 mm and merged with the neck into one 5-axis part).
Never edit the user's Onshape model. If the user exports a newer STEP, replace this file and re-run the fit
(`pipeline/full-exo/fit_arm.py`).
