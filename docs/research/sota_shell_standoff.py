# Used by docs/research/state_of_the_art.md section 3 (concentric-shell yardstick). Run: python3 docs/research/sota_shell_standoff.py
# (exact libigl path when no Bench(110,360) fast cache exists: a few minutes). r_skin = last exit radius of the skin along a ray from GH.
# Radial skin distance from the GH centre over the shoulder cap, and the stand-off of a concentric spherical shell
# of radius R (the geometry of a remote-centre spherical shoulder mechanism, e.g. CXD R = 60 mm) on the bench body.
import sys, os, numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); sys.path.insert(0, os.path.join(REPO, "tools")); os.chdir(REPO)
import concept_bench as CB
B = CB.Bench(110, 360)
print("mode", B.mode, "poses", len(B.poses))
# directions over the lateral/superior/posterior cap in the scapula-ish thorax frame (x ant, y up, z lat)
az = np.radians(np.arange(-90, 181, 6)); el = np.radians(np.arange(-30, 91, 6))
U = np.array([[np.cos(e) * np.sin(a), np.sin(e), np.cos(e) * np.cos(a)] for a in az for e in el])  # az 0 = lateral, 90 = anterior, -90 = posterior
rs = np.arange(10, 200, 1.0)
def rskin(i):
    T = B.frames(i); gh = np.asarray(T["H"][1], float)
    P = gh[None, None, :] + U[:, None, :] * rs[None, :, None]
    d = B.dist(i, P.reshape(-1, 3)).reshape(len(U), len(rs))
    out = np.full(len(U), np.nan)
    for k in range(len(U)):
        inside = d[k] < 0
        # first radius beyond which the ray is outside for good (last inside sample + 1)
        idx = np.nonzero(inside)[0]
        out[k] = rs[idx[-1] + 1] if len(idx) and idx[-1] + 1 < len(rs) else (rs[0] if not len(idx) else np.nan)
    return out
sel = {"rest-ish (lowest elevation clip pose)": int(np.argmin([p["elev"] for p, k in zip(B.poses, B.kind) if k == "clip"]))}
ws = [j for j, k in enumerate(B.kind) if k == "ws"]
oh = [j for j in ws if B.poses[j]["elev"] >= 140]
for name, j in list(sel.items()) + [("overhead ws pose elev>=140 #%d" % n, j) for n, j in enumerate(oh[:3])]:
    r = rskin(j); p = B.poses[j]
    cap = np.isfinite(r)
    print(name, {k: round(v, 1) for k, v in p.items()}, "r_skin p10/50/90:", np.nanpercentile(r, [10, 50, 90]).round(1))
    for R in (60, 80, 100, 150, 200):
        g = R - r[cap]
        print(f"   shell R={R}: stand-off over cap dirs p10/50/90 = {np.percentile(g,[10,50,90]).round(1)}; share 2-14 mm = {np.mean((g>=2)&(g<=14)):.2f}; share inside skin = {np.mean(g<0):.2f}")
