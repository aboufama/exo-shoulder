"""Where can a thorax-fixed joint sit? For every direction u from the GH centre (thorax frame, 2 deg grid) and every
clip frame (posed exact skin, hug.skin_frames): r1(t) = where the ray first leaves the skin. A base site needs skin that
(a) barely moves relative to the thorax (girdle, scapular skin) and (b) the arm never covers (r1 jumps when it does).
Prints the stable patches and writes base_sites.json (per direction: r1 at rest, motion max-min, fitting/held-out).
    python3 base_sites.py"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import girdle as GD, hug as HG
REPO = os.path.dirname(os.path.dirname(HERE))
C = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = np.array([c["name"] for c in C["clips"] for f in c["frames"]]); W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
sel = np.arange(0, len(W), 3); P = HG.skin_frames(W[sel], spacing=2.5, r_max=300.0); T = len(sel)
lat = np.radians(np.arange(-80, 81, 2.0)); lon = np.radians(np.arange(-180, 180, 2.0)); LA, LO = np.meshgrid(lat, lon, indexing="ij")
U = np.stack([np.cos(LA) * np.cos(LO), np.sin(LA), np.cos(LA) * np.sin(LO)], -1).reshape(-1, 3)      # x anterior, y up, z right
I = np.repeat(np.eye(3)[None], T, 0); Z = np.zeros((T, 3)); r1 = np.full((T, len(U)), np.inf)
for k0 in range(0, len(U), 1500):                                         # chunks keep the cone filter tight
    sl = slice(k0, k0 + 1500); a, _, _ = HG.ray_bounds(U[sl], I, Z, P, np.arange(T), rho_max=290.0); r1[:, sl] = a
fin = np.isfinite(r1).all(0); rest = r1[0]; mot = np.where(fin, r1.max(0) - r1.min(0), np.inf)
fit = ~np.isin(names[sel], ["Wave", "Walking arm swing"])
mot_fit = np.where(fin, r1[fit].max(0) - r1[fit].min(0), np.inf)
grid = mot.reshape(LA.shape)
print("stable skin (motion over all clip frames) - directions from the GH centre, thorax frame:")
for thr in (2, 4, 6, 10):
    m = (mot <= thr) & (rest < 280)
    print(f"  <= {thr:2d} mm: {m.sum():5d} directions ({100 * m.mean():.1f} % of the sphere)", end="")
    if m.any():
        uc = GD.unit(U[m].mean(0)); print(f"; mean direction {uc.round(2)}, rest radius {np.median(rest[m]):.0f} mm (range {rest[m].min():.0f}-{rest[m].max():.0f})")
    else: print()
# describe patches: by region (anterior/posterior, superior/inferior, medial/lateral)
def region(u):
    return ("anterior" if u[0] > 0.3 else "posterior" if u[0] < -0.3 else "mid") + "-" + ("superior" if u[1] > 0.3 else "inferior" if u[1] < -0.3 else "level") + "-" + ("lateral" if u[2] > 0.3 else "medial" if u[2] < -0.3 else "centre")
reg = {}
for k in np.nonzero((mot <= 4) & (rest < 280))[0]: reg.setdefault(region(U[k]), []).append(k)
print("patches with <= 4 mm motion:")
for rg, ks in sorted(reg.items(), key=lambda kv: -len(kv[1])):
    ks = np.array(ks); print(f"  {rg:32s} {len(ks):4d} dirs  radius {np.median(rest[ks]):5.0f} mm  motion median {np.median(mot[ks]):.1f} mm")
json.dump(dict(grid_deg=2, lat=np.degrees(lat).tolist(), lon=np.degrees(lon).tolist(), rest_r1=np.where(np.isfinite(rest), rest, -1).reshape(LA.shape).round(1).tolist(),
               motion=np.where(np.isfinite(mot), mot, -1).reshape(LA.shape).round(1).tolist(), frames=int(T),
               note="motion = max - min over clip frames of the first skin exit radius along each direction from the GH centre (thorax frame); -1 = no skin within 160 mm in some frame"),
          open(os.path.join(HERE, "base_sites.json"), "w"))
