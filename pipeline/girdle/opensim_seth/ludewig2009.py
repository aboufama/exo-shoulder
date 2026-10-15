"""Published mean shoulder-rhythm angles (summary values only; no subject data).

Ludewig PM, Phadke V, Braman JP, Hassett DR, Cieminski CJ, LaPrade RF (2009). Motion of the shoulder complex during
multiplanar humeral elevation. J Bone Joint Surg Am 91(2):378-389 (transcortical bone pins, n = 12; clavicle n = 11).
Means of raising, read off Fig. 5-A / 5-C (+-1 deg) by the teammate for docs/research/gh_translation_literature.md
(tag [F]); the same numbers as that note's chain (scratch scripts gh_lit.py / compare.py), copied here unchanged so the
OpenSim run and the rigid chain use identical inputs. Relaxed standing = Table I.

Angles, deg, vs the ISB thorax, Ludewig's reporting signs: ret = clavicle retraction (+), elev = clavicle elevation (+),
IR = scapular internal rotation (+), UR = scapular upward rotation (+), PT = scapular posterior tilt (+, negative = anterior).
Planes (ISB plane of elevation): abduction = 0, scaption = 40, flexion = 90.
"""
import numpy as np

E = np.array([15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120])
LUD = {
    "scaption": dict(ret=[23.5, 23.2, 25, 26.5, 27.5, 29, 30, 31, 32, 33, 34, 36.5], elev=[10.5, 10.5, 12, 13, 14, 14.5, 15, 15.5, 15.5, 15.8, 15.8, 17],
                     IR=[37, 38, 38.5, 38.8, 39, 39, 39, 39, 39, 39, 39, 37], UR=[10.5, 12, 15, 18.5, 22, 25, 28, 31, 34, 37, 40, 43],
                     PT=[-13, -12, -10.5, -9, -7.5, -6, -4.5, -3, -1.5, -0.5, 0.5, 2.5]),
    "abduction": dict(ret=[27, 28.5, 31, 33.5, 35.5, 37, 38.5, 40, 41, 42, 43, 44], elev=[12.5, 13, 14, 15, 16, 17, 17.5, 18, 18.5, 19, 19.3, 19.5],
                      IR=[31.5, 31, 31, 31, 30.8, 30.5, 30.5, 30.5, 30.5, 30.5, 30.8, 30.8], UR=[10.5, 12, 15, 18.5, 22, 25, 28, 31, 34.5, 38, 42, 46],
                      PT=[-12.5, -11.5, -10.5, -9, -7.5, -6, -4.5, -3, -1.5, 0, 1.5, 4]),
    "flexion": dict(ret=[19, 20, 21, 21.5, 22, 23, 24, 25, 25.5, 26.5, 28, 32], elev=[10.5, 10, 10, 11, 12, 12.5, 13.5, 14, 14, 14.5, 15, 14.5],
                    IR=[43, 43.5, 44.5, 45.5, 46, 46.5, 47, 47.5, 48, 48, 47.5, 43.5], UR=[10.5, 12, 15, 18.5, 21.5, 24.5, 27.5, 30.5, 33.5, 36.5, 39.5, 42],
                    PT=[-12.5, -12, -10, -8.5, -7, -5.5, -4, -2.5, -0.5, 1, 3, 5]),
}
ENDROM = {"scaption": (138, dict(ret=39, elev=17.5, IR=36, UR=51, PT=8)), "abduction": (135, dict(ret=45, elev=19.5, IR=30.5, UR=52, PT=7)),
          "flexion": (132, dict(ret=34.5, elev=15.5, IR=40, UR=47.5, PT=8.5))}
REST = dict(ret=19.2, elev=5.9, IR=41.1, UR=5.4, PT=-13.5)              # Table I, relaxed standing (means)
PLANE = {"abduction": 0, "scaption": 40, "flexion": 90}
KEYS = ["ret", "elev", "IR", "UR", "PT"]
# +-1 SD used for the sensitivity runs: scapula = McClure et al. 2001 (bone pins, n = 8, scaption range): upward rotation
# 4.8, posterior tilt 13, external rotation 12.8 (applied to IR); clavicle: no SD in the note (only Table I SEs) -> 5 deg.
SD = dict(ret=5.0, elev=5.0, IR=12.8, UR=4.8, PT=13.0)
SD_SOURCE = dict(ret="none given -> 5 deg", elev="none given -> 5 deg", IR="McClure 2001 ER SD 12.8", UR="McClure 2001 SD 4.8", PT="McClure 2001 SD 13")


def angles(plane, th):
    """(dict of the 5 angles, flag) at humerothoracic elevation th (deg); flag = None inside the data, 'below_15' when the
    15-30 deg slope is extrapolated below the first point, 'above_end_rom' beyond the plane's last point (132-138 deg)"""
    d = LUD[plane]; e_end, a_end = ENDROM[plane]; xs = list(E) + [e_end]; out = {}
    for k in KEYS:
        ys = list(d[k]) + [a_end[k]]
        if th < xs[0]: v = ys[0] + (ys[2] - ys[0]) / (xs[2] - xs[0]) * (th - xs[0])
        elif th > xs[-1]: v = ys[-1] + (ys[-1] - ys[-3]) / (xs[-1] - xs[-3]) * (th - xs[-1])
        else: v = float(np.interp(th, xs, ys))
        out[k] = float(v)
    flag = "below_15" if th < xs[0] else ("above_end_rom" if th > xs[-1] else None)
    return out, flag
