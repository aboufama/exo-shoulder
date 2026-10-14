"""Choreography for the EXO joint exploded-view animation: one source of truth for the browser preview and the
Cycles render. Writes motion.json (per frame: each part's lift in mm and spin in degrees, the elbow angle, and the
camera in the CAD frame, mm) and checks that no part ever passes through another.

The order is the real one:
  apart:     screws back out on the thread (spin locked to the 0.7 mm pitch), lift clear -> TOP off -> upper washer
             off -> MIDDLE lifts off the boss carrying the bearing (Loctite'd in its bore) -> the bearing comes out
             of MIDDLE -> lower washer off -> magnet drops out of its pocket
  together:  magnet in -> lower washer on -> bearing into MIDDLE -> MIDDLE + bearing onto the boss -> upper washer
             -> TOP -> screws down through TOP's holes, then driven in on the thread
then the camera pulls back and the elbow flexes.

    python3 motion.py          # writes motion.json, prints the check
"""
import json
import math
import os

FPS = 30
P, ENGAGE = 0.7, 4.85                # M4 pitch; thread engaged in BOTTOM's boss (boss top 5.6 - screw tip 0.75)
SPREAD = dict(MAGNET=-15.0, WASHER_LO=13.0, MIDDLE=26.0, BEAR_REL=16.0, WASHER_UP=57.0, TOP=70.0, SCREW=88.0)

ease = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else (4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2)
smooth = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * (3 - 2 * u)


def seg(t, t0, t1, a, b, f=ease):
    """Value moving from a to b between t0 and t1 (held outside)."""
    return a + (b - a) * f((t - t0) / (t1 - t0))


# (start, end) of every move, seconds
T = dict(
    unscrew=(0.4, 2.6), screw_up=(2.6, 3.4), top_up=(2.8, 3.7), wup_up=(3.1, 3.9), mid_up=(3.4, 4.3),
    bear_out=(4.3, 4.9), wlo_up=(3.9, 4.6), mag_out=(4.3, 4.9),
    mag_in=(5.4, 5.9), wlo_down=(5.5, 6.1), bear_in=(5.6, 6.2), mid_down=(6.2, 7.0), wup_down=(6.8, 7.5),
    top_down=(7.1, 7.9), screw_down=(7.7, 8.4), screw_in=(8.4, 10.6),
    pull_back=(10.6, 12.0), flex=(12.1, 14.1),
)
SPLIT = 5.2                          # apart before, together after
LABELS = [(0.4, "unscrew (0.7 mm per turn)"), (2.6, "screws clear"), (2.8, "TOP off"), (3.1, "upper washer off"),
          (3.4, "MIDDLE + bearing off the boss"), (3.9, "lower washer off"), (4.3, "bearing out of MIDDLE, magnet out"),
          (5.4, "magnet in, lower washer on"), (5.6, "bearing into MIDDLE"), (6.2, "MIDDLE + bearing onto the boss"),
          (6.8, "upper washer on"), (7.1, "TOP on"), (7.7, "screws through TOP"), (8.4, "screw in (0.7 mm per turn)"),
          (10.6, "pull back"), (12.1, "elbow flex")]
DUR = 14.4


def state(t):
    """Lifts (mm, + up) of every part and the screw spin (deg, + = CCW from above = backing out)."""
    s = {}
    mid = seg(t, *T["mid_up"], 0, SPREAD["MIDDLE"]) if t < SPLIT else seg(t, *T["mid_down"], SPREAD["MIDDLE"], 0)
    rel = seg(t, *T["bear_out"], 0, SPREAD["BEAR_REL"]) if t < SPLIT else seg(t, *T["bear_in"], SPREAD["BEAR_REL"], 0)
    s["MIDDLE"] = mid
    s["BEARING"] = s["SHIELDS"] = mid + rel                      # rides with MIDDLE, then comes out of its bore
    s["TOP"] = seg(t, *T["top_up"], 0, SPREAD["TOP"]) if t < SPLIT else seg(t, *T["top_down"], SPREAD["TOP"], 0)
    s["WASHER_UP"] = seg(t, *T["wup_up"], 0, SPREAD["WASHER_UP"]) if t < SPLIT else seg(t, *T["wup_down"], SPREAD["WASHER_UP"], 0)
    s["WASHER_LO"] = seg(t, *T["wlo_up"], 0, SPREAD["WASHER_LO"]) if t < SPLIT else seg(t, *T["wlo_down"], SPREAD["WASHER_LO"], 0)
    s["MAGNET"] = seg(t, *T["mag_out"], 0, SPREAD["MAGNET"]) if t < SPLIT else seg(t, *T["mag_in"], SPREAD["MAGNET"], 0)
    s["BOTTOM"] = 0.0
    if t < SPLIT:
        rise = seg(t, *T["unscrew"], 0, ENGAGE, smooth) if t < T["screw_up"][0] else seg(t, *T["screw_up"], ENGAGE, SPREAD["SCREW"])
    else:
        rise = seg(t, *T["screw_down"], SPREAD["SCREW"], ENGAGE) if t < T["screw_in"][0] else seg(t, *T["screw_in"], ENGAGE, 0, smooth)
    s["SCREW"] = rise
    s["SCREW_SPIN"] = 360.0 * min(rise, ENGAGE) / P             # locked to the pitch while on the thread
    return s


def camera(t):
    """Camera position and target in the CAD frame (mm, z up). Slow orbit; rises with the explode; pulls back."""
    ex = smooth((t - 2.0) / 1.3) - smooth((t - 7.9) / 1.1)      # stay high until TOP is seated
    az = math.radians(26 + 30 * t / DUR)
    el = math.radians(25 + 7 * ex); r = 300 + 20 * ex
    tx, th = -20.0, 6.0 + 36.0 * ex
    z = ease((t - T["pull_back"][0]) / (T["pull_back"][1] - T["pull_back"][0]))
    r += (840 - r) * z; tx += (130 - tx) * z; th += (0 - th) * z; el += (math.radians(34) - el) * z
    # glTF-style orbit (x, up, z) -> CAD (x, y, z): y = -z_gltf
    gx, gup, gz = tx + r * math.cos(el) * math.sin(az), th + r * math.sin(el), r * math.cos(el) * math.cos(az)
    return dict(pos=[gx, -gz, gup], target=[tx, 0.0, th])


def flex(t):
    return 95.0 * ease(math.sin(math.pi * min(1, max(0, (t - T["flex"][0]) / (T["flex"][1] - T["flex"][0])))))


def check(frames):
    """Physical sanity over every frame. Geometry (mm): screw head underside sits on TOP's counterbore floor when
    both are seated; screw tip at 0.75, TOP top face 8.05; bearing top 4.75 vs TOP pocket floor 5.6."""
    bad = []
    for i, f in enumerate(frames):
        L, t = f["lift"], i / FPS
        def need(cond, what):
            if not cond:
                bad.append(f"t={t:5.2f}s  {what}")
        need(L["SCREW"] >= L["TOP"] - 1e-6, f"screw head below TOP's counterbore (screw {L['SCREW']:.1f} < TOP {L['TOP']:.1f})")
        if L["SCREW"] < ENGAGE + 8.05 - 0.75:                    # screw tip inside TOP's hole region or lower
            need(L["TOP"] < 1e-3 or L["SCREW"] >= L["TOP"], "screw in TOP's hole while TOP moves wrong way")
        if L["SCREW"] <= ENGAGE + 1e-6:
            need(L["TOP"] < 1e-3, f"screw on the thread before TOP is seated (TOP {L['TOP']:.2f})")
        need(L["MIDDLE"] >= L["WASHER_LO"] - 1e-6, "MIDDLE through the lower washer")
        need(L["WASHER_UP"] >= L["MIDDLE"] - 1e-6, "upper washer through MIDDLE")
        need(L["TOP"] >= L["WASHER_UP"] - 1e-6, "TOP through the upper washer")
        need(L["BEARING"] >= L["MIDDLE"] - 1e-6, "bearing below its seat in MIDDLE")
        need(L["BEARING"] <= L["TOP"] + 0.85 + 1e-6, "bearing through TOP")
        need(L["WASHER_LO"] >= -1e-6 and L["MIDDLE"] >= -1e-6 and L["MAGNET"] <= 1e-6, "part through BOTTOM")
        if f["flex"] > 0:
            need(all(abs(L[k]) < 1e-6 for k in L), "elbow flexing while not assembled")
    # spin rate (for the record): peak revolutions per second while on the thread
    return bad


if __name__ == "__main__":
    N = round(FPS * DUR)
    frames = []
    for i in range(N):
        t = i / FPS; s = state(t)
        lift = {k: v for k, v in s.items() if k != "SCREW_SPIN"}
        frames.append(dict(lift=lift, spin=s["SCREW_SPIN"], flex=flex(t), cam=camera(t)))
    bad = check(frames)
    spins = [abs(frames[i + 1]["spin"] - frames[i]["spin"]) for i in range(N - 1)]
    print(f"{N} frames, {DUR} s. Screw: {ENGAGE / P:.2f} turns each way over {T['unscrew'][1] - T['unscrew'][0]:.1f} s, "
          f"peak {max(spins) * FPS / 360:.2f} rev/s ({max(spins):.0f} deg/frame), 0.7 mm per turn.")
    print("CHECK:", "PASS - no part passes through another" if not bad else f"{len(bad)} violations")
    for b in bad[:20]:
        print("  ", b)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "motion.json"), "w") as fh:
        json.dump(dict(fps=FPS, dur=DUR, labels=LABELS, frames=frames), fh)
