"""EXO elbow joint + forearm cuff assembly film (v8: one continuous camera move, no cuts). Writes film_v7.json
(per frame: every part's offset in mm, each screw's spin, the elbow angle, the camera with lens/focus/aperture) and
checks every frame for parts passing through each other and for the camera entering the cuff.

  0.0- 3.0  the joint builds in the real order: magnet up into BOTTOM, lower washer, bearing into MIDDLE, MIDDLE onto
            the boss, upper washer, TOP
  3.1- 6.8  the camera glides in close: the three joint screws come down through TOP and drive in (pitch-locked)
  6.8-11.4  the camera sweeps down and under as the cuff rises into its seat; its six countersunk screws come up
            through the bore and drive in flush, seen from inside the cuff
 11.4-17.0  one pull back to a high three-quarter view; the elbow flexes and holds
Coordinates: CAD frame, mm, joint axis at the origin, z up.

    python3 film_v7.py
"""
import json
import math
import os

FPS, DUR = 60, 17.0
P = 0.7
ENG_J, ENG_C = 4.85, 3.27

ease = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else (4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2)
out_q = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else 1 - (1 - u) ** 3        # arrives softly
smooth = lambda u: 0.0 if u <= 0 else 1.0 if u >= 1 else u * u * (3 - 2 * u)


def trap(u, a=0.15):
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    v = 1 / (1 - a)
    if u < a: return v * u * u / (2 * a)
    if u > 1 - a: return 1 - v * (1 - u) ** 2 / (2 * a)
    return v * (u - a / 2)


def go(t, t0, t1, a, b, f=ease):
    return a + (b - a) * f((t - t0) / (t1 - t0))


def parts(t):
    """z offsets (mm) of every part from its assembled position, and screw spins (deg)."""
    z = dict(BOTTOM=0.0, SLEEVE=0.0)
    z["MAGNET"] = go(t, 0.3, 0.9, -45, 0, out_q)
    z["WASHER_LO"] = go(t, 0.5, 1.1, 45, 0, out_q)
    mid = go(t, 1.4, 2.2, 60, 0, ease)
    z["MIDDLE"] = mid
    z["BEARING"] = mid + go(t, 0.7, 1.4, 40, 0, out_q)                 # pressed into MIDDLE, then rides with it
    z["WASHER_UP"] = go(t, 2.0, 2.6, 85, 0, out_q)
    z["TOP"] = go(t, 2.3, 3.0, 105, 0, out_q)
    spin = {}
    for k in range(3):                                                 # joint screws: down through TOP, then driven in
        d = 0.18 * k
        r = go(t, 3.1 + d, 3.8 + d, 130, ENG_J, out_q) if t < 4.2 + d else go(t, 4.2 + d, 6.4 + d, ENG_J, 0, trap)
        z[f"SCREW{k}"] = r; spin[f"SCREW{k}"] = 360.0 * min(r, ENG_J) / P
    z["CUFF"] = go(t, 6.8, 7.8, -160, 0, out_q)                       # parked below the frame until it rises
    for k in range(6):                                                 # cuff screws: up through the bore, driven in
        d0, d1 = 0.06 * k, 0.25 * (k // 2)
        c = go(t, 7.8 + d0, 8.8 + d0, -400, -ENG_C, out_q) if t < 9.0 + d1 else go(t, 9.0 + d1, 11.0 + d1, -ENG_C, 0, trap)
        z[f"CSCREW{k}"] = c; spin[f"CSCREW{k}"] = 360.0 * max(c, -ENG_C) / P
    return z, spin


def flex(t):
    return 100.0 * ease((t - 13.6) / 2.0)


# camera keys: (time, pos mm, target mm, vertical fov deg, f-stop). One continuous move: C1 (Catmull-Rom style)
# spline through the keys, so it never stops dead or jerks between beats.
KEYS = [
    (0.0, (165, -240, 150), (-15, 0, 35), 30, 8.0),       # wide on the stack
    (2.8, (110, -250, 125), (-12, 0, 25), 30, 8.0),
    (4.0, (55, -80, 70), (-1, 0, 9), 24, 4.0),            # in close for the joint screws
    (6.4, (44, -86, 60), (-1, 0, 9), 24, 4.0),
    (7.4, (-20, -300, -60), (-85, 0, -40), 30, 8.0),      # down and out to the side as the cuff rises
    (8.1, (-50, -190, -200), (-92, 0, -40), 32, 8.0),     # dip well below the cuff first...
    (8.9, (-75, -40, -130), (-98, 0, -10), 36, 5.6),      # ...then slide in under it, looking up into the bore
    (10.9, (-82, -32, -118), (-98, 0, -8), 36, 5.6),
    (12.0, (-60, -200, -180), (-70, 0, -40), 32, 8.0),    # out from under
    (13.6, (370, -640, 250), (140, 0, -30), 30, 11.0),    # hero
    (17.0, (385, -655, 262), (140, 0, -30), 30, 11.0),
]


def _hermite(t, idx):
    ts = [k[0] for k in KEYS]; vs = [k[idx] for k in KEYS]
    vec = isinstance(vs[0], tuple)
    V = [list(v) if vec else [v] for v in vs]
    i = max(0, min(len(ts) - 2, max(j for j in range(len(ts)) if ts[j] <= t)))
    t0, t1 = ts[i], ts[i + 1]; h = t1 - t0; u = min(1.0, max(0.0, (t - t0) / h))
    def slope(j):
        if j == 0 or j == len(ts) - 1:
            return [0.0] * len(V[0])                                  # start and end at rest
        return [(V[j + 1][c] - V[j - 1][c]) / (ts[j + 1] - ts[j - 1]) for c in range(len(V[0]))]
    m0, m1 = slope(i), slope(i + 1)
    h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
    out = [h00 * V[i][c] + h10 * h * m0[c] + h01 * V[i + 1][c] + h11 * h * m1[c] for c in range(len(V[0]))]
    return out if vec else out[0]


def camera(t):
    pos, tgt = _hermite(t, 1), _hermite(t, 2)
    return dict(pos=pos, target=tgt, fov=_hermite(t, 3), fstop=max(2.8, _hermite(t, 4)), focus=math.dist(pos, tgt))


def cam_in_cuff(f):
    """True if the camera is inside the cuff's wall (or its rim) while the cuff is near its seat."""
    x, y, z = f["cam"]["pos"]; cz = -53.0 + f["z"]["CUFF"]
    if not (-158 <= x <= -38):
        return False
    r = math.hypot(y, z - cz); phi = math.degrees(math.atan2(abs(y), z - cz))
    return 47.0 <= r <= 60.0 and phi <= 122.0


def check(frames):
    bad = []
    for i, f in enumerate(frames):
        Z, t = f["z"], i / FPS
        def need(c, w):
            if not c: bad.append(f"t={t:5.2f}s  {w}")
        need(Z["MAGNET"] <= 1e-6, "magnet through BOTTOM")
        need(Z["WASHER_LO"] >= -1e-6, "lower washer through BOTTOM")
        need(Z["MIDDLE"] >= Z["WASHER_LO"] - 1e-6, "MIDDLE through the lower washer")
        need(Z["BEARING"] >= Z["MIDDLE"] - 1e-6, "bearing below its seat in MIDDLE")
        need(Z["WASHER_UP"] >= Z["MIDDLE"] - 1e-6, "upper washer through MIDDLE")
        need(Z["TOP"] >= Z["WASHER_UP"] - 1e-6, "TOP through the upper washer")
        need(Z["BEARING"] <= Z["TOP"] + 0.85 + 1e-6, "bearing through TOP")
        for k in range(3):
            s = Z[f"SCREW{k}"]
            need(s >= Z["TOP"] - 1e-6, f"screw {k} head inside TOP")
            if s < ENG_J + 7.3: need(Z["TOP"] < 1e-3, f"screw {k} in TOP's hole before TOP is seated")
        need(Z["CUFF"] <= Z["MIDDLE"] + 1e-6, "cuff through MIDDLE")
        for k in range(6):
            c = Z[f"CSCREW{k}"]
            need(c <= Z["CUFF"] + 1e-6, f"cuff screw {k} head through the cuff wall")
            if c > -ENG_C - 1e-6: need(abs(Z["CUFF"]) < 1e-3 and abs(Z["MIDDLE"]) < 1e-3, f"cuff screw {k} on the thread before cuff and MIDDLE are seated")
        if f["flex"] > 0:
            need(all(abs(v) < 1e-6 for v in Z.values()), "elbow flexing while not assembled")
        need(not cam_in_cuff(f), "camera inside the cuff wall")
    return bad


if __name__ == "__main__":
    N = round(FPS * DUR)
    frames = []
    for i in range(N):
        t = i / FPS; z, sp = parts(t)
        frames.append(dict(z=z, spin=sp, flex=flex(t), cam=camera(t), hidden=[], cut=False))
    bad = check(frames)
    for pref, eng in (("SCREW", ENG_J), ("CSCREW", ENG_C)):
        d = max(abs(frames[i + 1]["spin"][f"{pref}0"] - frames[i]["spin"][f"{pref}0"]) for i in range(N - 1))
        print(f"{pref:6s}: {eng / P:.2f} turns, peak {d:.0f} deg/frame at {FPS} fps")
    print(f"{N} frames, {DUR} s, one continuous camera move")
    print("CHECK:", "PASS - no part passes through another" if not bad else f"{len(bad)} violations")
    for b in bad[:20]:
        print("  ", b)
    json.dump(dict(fps=FPS, dur=DUR, frames=frames,
                   shots=[("joint builds", 0.0), ("joint screws", 3.1), ("cuff", 6.8), ("cuff screws", 7.8), ("pull back + flex", 11.4)]),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "film_v7.json"), "w"))
