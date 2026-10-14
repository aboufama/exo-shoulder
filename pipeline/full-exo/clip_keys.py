"""Natural keyframes for the everyday-motion clips (make_clips_full.py).

ISB YXY angles (plane, elevation, axial): near zero elevation plane and axial both spin the humerus about its long
axis, so a keyframe written as (plane, elev, 0) twists the whole arm by `plane`. Here every keyframe's axial is
measured from the twist-free swing in its plane (ISB axial = axial_rel - plane), and the keyframes that must put the
hand somewhere (cup at the mouth, comb on the head, hand on the opposite shoulder, hand in the back pocket) are solved
by inverse kinematics on the body rig: wrist on the target, as little twist and as close to the hint as possible.

    python3 clip_keys.py        -> clip_keys.json (read by make_clips_full.py), prints wrist errors
"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
import body_pose as BP
J = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); L = J["landmarks"]; S = J["scale"]

def wrist(pl, el, ax, flex):
    sg, _ = BP.segs(L, S, dict(plane=pl, elev=el, axial=ax, flex=flex, pron=0)); F = sg[3]
    return F[0] @ np.array(L["ulnar_head"]) + F[1]

# body targets (thorax frame, GH origin, mm): x anterior, y up, z right; midline z ~ -174
MOUTH = np.array([139.0, 144.0, -173.0])
TARGET = {
    "cup": MOUTH + [45, -65, 25],                 # wrist when the cup is at the lips
    "cup_low": MOUTH + [120, -150, 70],           # cup on its way up
    "comb_front": np.array([75.0, 305.0, -85.0]), # wrist above the right temple, comb on the crown
    "comb_back": np.array([-35.0, 295.0, -95.0]),
    "comb_up": np.array([150.0, 230.0, -20.0]),
    "wash_a": np.array([95.0, 5.0, -290.0]),      # hand on the left shoulder, scrubbing
    "wash_b": np.array([55.0, 40.0, -325.0]),
    "wash_in": np.array([210.0, -60.0, -180.0]),
    "pocket_in": np.array([-95.0, -470.0, -40.0]),  # hand in the right back pocket
    "pocket_way": np.array([-50.0, -430.0, 40.0]),
}

def solve(tgt, hint, flex_hint):
    """(plane, elev, axial_ISB, flex) with the wrist on tgt; hint = (plane, elev, axial_rel)"""
    def cost(x):
        pl, el, ar, fx = x; w = wrist(pl, el, ar - pl, fx)
        return (np.sum((w - tgt) ** 2) + 4.0 * ar ** 2 * 0.25 + 2.0 * (fx - flex_hint) ** 2
                + 0.5 * ((pl - hint[0]) ** 2 + (el - hint[1]) ** 2) + 1e4 * (max(0, -el) + max(0, el - 165) + max(0, fx - 145) + max(0, -fx)) ** 2
                + 1e3 * (max(0, abs(pl - hint[0]) - 35) + max(0, abs(el - hint[1]) - 35)) ** 2)        # stay in the hinted family
    best = None
    for d_ar in (0, -30, 30):
        x0 = np.array([hint[0], hint[1], hint[2] + d_ar, flex_hint], float)
        r = minimize(cost, x0, method="Nelder-Mead", options=dict(xatol=0.05, fatol=0.05, maxiter=4000))
        if best is None or r.fun < best.fun: best = r
    pl, el, ar, fx = best.x
    return (round(pl, 1), round(el, 1), round(ar - pl, 1), round(fx, 1)), float(np.linalg.norm(wrist(pl, el, ar - pl, fx) - tgt))

def tf(pl, el, ar, fx, pr=0):
    """twist-free keyframe: axial_rel -> ISB axial"""
    return (pl, el, ar - pl, fx, pr)

# keyframes: ("tf", plane, elev, axial_rel, flex) or ("ik", target, (plane, elev, axial_rel) hint, flex hint); + duration
SPEC = [
    ("Raise overhead", [(("tf", 30, 3, 0, 12), 2.6), (("tf", 30, 150, -30, 12), 0.8), (("tf", 30, 150, -30, 12), 2.6), (("tf", 30, 3, 0, 12), 0.6)]),
    ("Drink from a cup", [(("tf", 40, 4, 0, 15), 1.6), (("ik", "cup_low", (60, 35, 20), 95), 0.8), (("ik", "cup", (60, 50, 30), 130), 1.2), (("ik", "cup", (60, 50, 30), 130), 0.9),
                          (("ik", "cup_low", (60, 35, 20), 95), 1.4), (("tf", 40, 4, 0, 15), 0.6)]),
    ("Comb hair", [(("tf", 30, 4, 0, 15), 1.8), (("ik", "comb_up", (50, 95, 0), 110), 0.9), (("ik", "comb_front", (60, 115, -10), 125), 0.8), (("ik", "comb_back", (72, 108, 0), 120), 0.8),
                   (("ik", "comb_front", (60, 115, -10), 125), 0.8), (("ik", "comb_back", (72, 108, 0), 120), 1.6), (("tf", 30, 4, 0, 15), 0.6)]),
    ("Reach a high shelf", [(("tf", 60, 4, 0, 35), 1.8), (("tf", 80, 115, 0, 20), 0.7), (("tf", 82, 132, 0, 6), 0.9), (("tf", 82, 132, 0, 6), 1.8), (("tf", 60, 4, 0, 35), 0.6)]),
    ("Wash opposite shoulder", [(("tf", 30, 4, 0, 15), 1.8), (("ik", "wash_in", (95, 45, 20), 110), 0.9), (("ik", "wash_a", (110, 70, 25), 128), 0.7), (("ik", "wash_b", (105, 75, 25), 128), 0.7),
                                (("ik", "wash_a", (110, 70, 25), 128), 0.7), (("ik", "wash_b", (105, 75, 25), 128), 1.6), (("tf", 30, 4, 0, 15), 0.6)]),
    ("Reach back pocket", [(("tf", 0, 4, 0, 15), 1.6), (("ik", "pocket_way", (-35, 25, 40), 50), 0.8), (("ik", "pocket_in", (-45, 35, 55), 75), 0.9), (("ik", "pocket_in", (-45, 35, 55), 75), 1.5), (("tf", 0, 4, 0, 15), 0.6)]),
    ("Wave", [(("tf", 20, 4, 0, 20), 1.6), (("tf", 15, 92, -45, 95), 0.5), (("tf", 15, 95, -65, 95), 0.45), (("tf", 15, 92, -30, 95), 0.45), (("tf", 15, 95, -65, 95), 0.45),
              (("tf", 15, 92, -30, 95), 0.45), (("tf", 15, 95, -65, 95), 0.45), (("tf", 15, 92, -45, 95), 1.6), (("tf", 20, 4, 0, 20), 0.6)]),
    ("Walking arm swing", [(("tf", 90, 4, 0, 18), 0.55), (("tf", 90, 24, 0, 32), 0.55), (("tf", 90, 4, 0, 18), 0.55), (("tf", 90, 24, 0, 32), 0.55),
                           (("tf", 90, 4, 0, 18), 0.55), (("tf", 90, 24, 0, 32), 0.55), (("tf", 90, 4, 0, 18), 0.6)]),
]

if __name__ == "__main__":
    out = []; cache = {}
    for name, keys in SPEC:
        ks = []
        for k, dur in keys:
            if k[0] == "tf": ks.append([list(tf(*k[1:])), dur]); continue
            key = (k[1], k[2], k[3])
            if key not in cache: cache[key] = solve(TARGET[k[1]], k[2], k[3])
            (pl, el, ax, fx), err = cache[key]; ks.append([[pl, el, ax, fx, 0], dur])
            print(f"{name:24s} {k[1]:11s} -> plane {pl:6.1f} elev {el:6.1f} axial {ax:6.1f} (rel {ax + pl:5.1f}) flex {fx:5.1f}   wrist error {err:5.1f} mm")
        out.append([name, ks])
    json.dump(out, open(os.path.join(HERE, "clip_keys.json"), "w"), indent=1); print("saved clip_keys.json")
