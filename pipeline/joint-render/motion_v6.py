"""Choreography v6 (joint + forearm cuff): one source of truth for the browser preview and the Cycles render.
Writes motion_v6.json and checks every frame for parts passing through each other.

Real order:
  cuff off:   6 countersunk screws back out of MIDDLE (3.27 mm of thread = 4.7 turns), drop straight down through the
              cuff's bore and out of its open underside -> cuff drops away
  joint apart: 3 screws back out (4.85 mm = 6.9 turns), lift clear -> TOP -> upper washer -> MIDDLE lifts off the boss
              carrying the bearing (Loctite'd in its bore) -> bearing out of MIDDLE -> lower washer -> magnet drops out
  together:   the exact reverse: magnet, lower washer, bearing into MIDDLE, MIDDLE + bearing onto the boss, upper
              washer, TOP, joint screws through TOP and driven in; cuff up under MIDDLE, its screws up through the bore
              and driven in
then the camera pulls back and the elbow flexes (MIDDLE, cuff and cuff screws turn together about the joint axis).
Screw spin is locked to the 0.7 mm pitch while on the thread, with a constant-speed profile so the hex sockets step
< 30 deg per frame at 60 fps (no wagon-wheel illusion).

    python3 motion_v6.py
"""
import json
import math
import os

FPS = 60
P = 0.7
ENG_J, ENG_C = 4.85, 3.27            # thread engaged: joint screws in BOTTOM's boss, cuff screws in MIDDLE
SPREAD = dict(MAGNET=-15.0, WASHER_LO=13.0, MIDDLE=26.0, BEAR_REL=16.0, WASHER_UP=57.0, TOP=70.0, SCREW=88.0,
              CUFF=-45.0, CSCREW=-140.0)
FLOOR = -165.0

ease = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else (4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2)
smooth = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * (3 - 2 * u)


def trap(u, a=0.15):
    """Constant-speed move with short eased ramps (fraction of travel vs fraction of time)."""
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    v = 1 / (1 - a)
    if u < a: return v * u * u / (2 * a)
    if u > 1 - a: return 1 - v * (1 - u) ** 2 / (2 * a)
    return v * (u - a / 2)


def seg(t, t0, t1, a, b, f=ease):
    return a + (b - a) * f((t - t0) / (t1 - t0))


T = dict(
    c_unscrew=(0.6, 2.8), c_drop=(2.8, 3.7), cuff_down=(3.3, 4.1),
    unscrew=(3.6, 5.8), screw_up=(5.8, 6.6), top_up=(6.0, 6.9), wup_up=(6.3, 7.1), mid_up=(6.6, 7.5),
    bear_out=(7.5, 8.1), wlo_up=(7.1, 7.8), mag_out=(7.5, 8.1),
    mag_in=(9.0, 9.5), wlo_down=(9.1, 9.7), bear_in=(9.2, 9.8), mid_down=(9.8, 10.6), wup_down=(10.4, 11.1),
    top_down=(10.7, 11.5), screw_down=(11.3, 12.0), screw_in=(12.0, 14.2),
    cuff_up=(14.1, 14.9), c_rise=(14.7, 15.5), c_screw_in=(15.5, 17.7),
    pull_back=(17.8, 19.2), flex=(19.3, 21.3),
)
DUR = 21.7
SPLIT = 8.5
LABELS = [(0.6, "cuff screws out (0.7 mm per turn)"), (2.8, "cuff screws out through the cuff"), (3.3, "cuff off"),
          (3.6, "joint screws out"), (5.8, "screws clear"), (6.0, "TOP off"), (6.3, "upper washer off"),
          (6.6, "MIDDLE + bearing off the boss"), (7.1, "lower washer off"), (7.5, "bearing out of MIDDLE, magnet out"),
          (9.0, "magnet in, lower washer on"), (9.2, "bearing into MIDDLE"), (9.8, "MIDDLE + bearing onto the boss"),
          (10.4, "upper washer on"), (10.7, "TOP on"), (11.3, "screws through TOP"), (12.0, "joint screws in"),
          (14.1, "cuff on"), (14.7, "cuff screws up through the cuff"), (15.5, "cuff screws in"),
          (17.8, "pull back"), (19.3, "elbow flex")]


def state(t):
    s = {}
    after = t >= SPLIT
    def mv(key, up, down, a=0.0, b=None):
        b = SPREAD[key] if b is None else b
        return seg(t, *T[down], b, a) if after else seg(t, *T[up], a, b)
    mid = mv("MIDDLE", "mid_up", "mid_down")
    rel = mv("BEAR_REL", "bear_out", "bear_in")
    s["MIDDLE"] = mid; s["BEARING"] = mid + rel
    s["TOP"] = mv("TOP", "top_up", "top_down")
    s["WASHER_UP"] = mv("WASHER_UP", "wup_up", "wup_down")
    s["WASHER_LO"] = mv("WASHER_LO", "wlo_up", "wlo_down")
    s["MAGNET"] = mv("MAGNET", "mag_out", "mag_in")
    s["BOTTOM"] = s["SLEEVE"] = 0.0
    # joint screws (+ up)
    if not after:
        r = seg(t, *T["unscrew"], 0, ENG_J, trap) if t < T["screw_up"][0] else seg(t, *T["screw_up"], ENG_J, SPREAD["SCREW"])
    else:
        r = seg(t, *T["screw_down"], SPREAD["SCREW"], ENG_J) if t < T["screw_in"][0] else seg(t, *T["screw_in"], ENG_J, 0, trap)
    s["SCREW"] = r
    # cuff (+ cuff screws, - down)
    if not after:
        c = seg(t, *T["c_unscrew"], 0, -ENG_C, trap) if t < T["c_drop"][0] else seg(t, *T["c_drop"], -ENG_C, SPREAD["CSCREW"])
        cuff = seg(t, *T["cuff_down"], 0, SPREAD["CUFF"])
    else:
        cuff = seg(t, *T["cuff_up"], SPREAD["CUFF"], 0)
        c = seg(t, *T["c_rise"], SPREAD["CSCREW"], -ENG_C) if t < T["c_screw_in"][0] else seg(t, *T["c_screw_in"], -ENG_C, 0, trap)
    s["CUFF"] = cuff; s["CSCREW"] = c
    spin = dict(SCREW=360.0 * min(r, ENG_J) / P, CSCREW=360.0 * max(c, -ENG_C) / P)
    return s, spin


# camera keys: (time, target xyz mm, distance mm, elevation deg); azimuth drifts slowly over the whole clip
CAM = [(0.0, (-55, 0, -28), 440, 20), (1.2, (-92, 0, -48), 380, 13), (3.4, (-85, 0, -70), 470, 14),
       (4.4, (-20, 0, 8), 300, 25), (5.8, (-20, 0, 8), 300, 25), (7.2, (-60, 0, -32), 540, 18),
       (8.6, (-60, 0, -32), 540, 18), (9.6, (-25, 0, 30), 390, 25), (11.0, (-20, 0, 12), 310, 25),
       (13.6, (-20, 0, 8), 300, 25), (14.4, (-90, 0, -58), 420, 12), (17.6, (-90, 0, -58), 420, 12),
       (19.2, (100, 0, -30), 900, 30), (DUR, (100, 0, -30), 900, 30)]


def camera(t):
    for (t0, g0, r0, e0), (t1, g1, r1, e1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            u = smooth((t - t0) / (t1 - t0) if t1 > t0 else 1)
            g = [a + (b - a) * u for a, b in zip(g0, g1)]; r = r0 + (r1 - r0) * u; el = math.radians(e0 + (e1 - e0) * u)
            break
    az = math.radians(28 + 32 * t / DUR)
    pos = [g[0] + r * math.cos(el) * math.sin(az), g[1] - r * math.cos(el) * math.cos(az), g[2] + r * math.sin(el)]
    return dict(pos=pos, target=g)


def flex(t):
    return 95.0 * ease(math.sin(math.pi * min(1, max(0, (t - T["flex"][0]) / (T["flex"][1] - T["flex"][0])))))


def check(frames):
    bad = []
    for i, f in enumerate(frames):
        L, t = f["lift"], i / FPS
        def need(cond, what):
            if not cond: bad.append(f"t={t:5.2f}s  {what}")
        # joint
        need(L["SCREW"] >= L["TOP"] - 1e-6, "joint screw head inside TOP")
        if L["SCREW"] <= ENG_J + 1e-6: need(L["TOP"] < 1e-3, "joint screw on the thread before TOP is seated")
        need(L["MIDDLE"] >= L["WASHER_LO"] - 1e-6, "MIDDLE through the lower washer")
        need(L["WASHER_UP"] >= L["MIDDLE"] - 1e-6, "upper washer through MIDDLE")
        need(L["TOP"] >= L["WASHER_UP"] - 1e-6, "TOP through the upper washer")
        need(L["BEARING"] >= L["MIDDLE"] - 1e-6, "bearing below its seat in MIDDLE")
        need(L["BEARING"] <= L["TOP"] + 0.85 + 1e-6, "bearing through TOP")
        need(L["WASHER_LO"] >= -1e-6 and L["MIDDLE"] >= -1e-6 and L["MAGNET"] <= 1e-6, "part through BOTTOM")
        # cuff
        need(L["CSCREW"] <= L["CUFF"] + 1e-6, "cuff screw head through the cuff wall")
        need(L["CUFF"] <= L["MIDDLE"] + 1e-6, "cuff through MIDDLE")
        if L["CSCREW"] > -ENG_C - 1e-6:
            need(abs(L["CUFF"]) < 1e-3 and abs(L["MIDDLE"]) < 1e-3, "cuff screw on the thread with cuff/MIDDLE not seated")
        if abs(L["MIDDLE"]) > 1e-6:
            need(L["CSCREW"] < -ENG_C or L["CUFF"] < -1e-3, "MIDDLE moving while the cuff is still screwed on")
        if L["CSCREW"] + 3.27 < L["CUFF"] - 78.9 + 1e-6 or L["CSCREW"] > -80:
            pass                                                    # screws below the cuff, or inside its open bore
        if L["CSCREW"] - L["CUFF"] < -82.2:                         # screws fully below the cuff: cuff must stay above them
            need(L["CUFF"] - 78.9 > L["CSCREW"] + 3.27 - 1e-6, "cuff dropped onto its screws")
        if f["flex"] > 0:
            need(all(abs(L[k]) < 1e-6 for k in L), "elbow flexing while not assembled")
    return bad


if __name__ == "__main__":
    N = round(FPS * DUR)
    frames = []
    for i in range(N):
        t = i / FPS; s, sp = state(t)
        frames.append(dict(lift=s, spin=sp, flex=flex(t), cam=camera(t)))
    bad = check(frames)
    for k, eng in (("SCREW", ENG_J), ("CSCREW", ENG_C)):
        d = [abs(frames[i + 1]["spin"][k] - frames[i]["spin"][k]) for i in range(N - 1)]
        print(f"{k:6s}: {eng / P:.2f} turns each way, peak {max(d) * FPS / 360:.2f} rev/s = {max(d):.0f} deg/frame at {FPS} fps")
    print(f"{N} frames, {DUR} s")
    print("CHECK:", "PASS - no part passes through another" if not bad else f"{len(bad)} violations")
    for b in bad[:20]:
        print("  ", b)
    json.dump(dict(fps=FPS, dur=DUR, floor=FLOOR, labels=LABELS, frames=frames),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "motion_v6.json"), "w"))
