"""SIM-TO-REAL 2 - kinematic incompatibility of an exactly-3-DOF rotation chain with a rigid cuff. If the chain's rotation
centre c' misses the arm's true GH centre c by e (donning / fitting error, GH translation in the glenoid, base slip),
every exo point carried by the arm end moves by (I - R) e relative to the arm, R = humerus rotation in the base
(scapula) frame since the pose the exo was fitted in (arm hanging). |(I - R) e| <= 2 |e| sin(theta / 2). That shift is
either taken by the skin (interaction force ~ k x shift; upper-arm interface 2.1-4.5 N/mm, Schiebl et al. 2025) or shows
up as metal moving relative to the skin it was shaped against. band_poses.b64 (all 8 clips, scapula frame).
    python3 rt_misalign.py   -> results/misalign.json"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "analysis")); os.chdir(os.path.join(REPO, "pipeline", "conformal"))
import transmission as TR                                               # noqa: E402
P = TR.poses(); names = [str(x) for x in P["NAMES"]]; cid = P["CID"]; HG = P["HG"]
k0 = int(np.argmin((HG @ np.array([0.0, -1.0, 0.0]))[:, 1]))           # fitting pose: humerus closest to hanging straight down
th = np.degrees(np.arccos(np.clip((np.einsum("fij,ij->f", HG, HG[k0]) - 1) / 2, -1, 1)))
out = dict(fit_frame=[names[cid[k0]], int(P["FI"][k0])], rotation_since_fit_deg={n: round(float(th[cid == k].max()), 1) for k, n in enumerate(names)}, cases={})
for e in (2.7, 4, 10, 15, 20, 30):
    s = 2 * e * np.sin(np.radians(th) / 2)
    out["cases"][str(e)] = dict(shift_worst_dir_max_mm=round(float(s.max()), 1), p95=round(float(np.percentile(s, 95)), 1), median=round(float(np.median(s)), 1),
                                shift_random_dir_max_mm=round(float(s.max() * math.pi / 4), 1), force_N_at_2_and_4p5_N_per_mm=[round(2 * float(s.max())), round(4.5 * float(s.max()))])
    print(f"centre error {e:4.1f} mm -> arm-end shift up to {s.max():5.1f} mm (p95 {np.percentile(s, 95):5.1f}, median {np.median(s):4.1f}); force {2 * s.max():4.0f}-{4.5 * s.max():4.0f} N if the skin takes it")
json.dump(out, open(os.path.join(HERE, "results", "misalign.json"), "w"), indent=1)
