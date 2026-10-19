"""K-placement atlas: in-band potential of a flat O20 GH-ray hub fixed in link 2a (moves with q1, q2) vs fixed in link 1."""
import json, sys, math, importlib.util, numpy as np, time
sys.path.insert(0, "tools")
sp = importlib.util.spec_from_file_location("cu", "docs/concepts/models/cam-unfold-4th.py"); cu = importlib.util.module_from_spec(sp); sp.loader.exec_module(cu)
import concept_bench as CB
S = cu.S; unit = S.unit
par = json.loads(sys.argv[1])
B = CB.Bench(n_clip=60, n_ws=160); r, M = cu._report(B, par)
D = M.D; poses = np.nonzero(M.kin_ok)[0]
u2 = D.u[1]; e, f = S.frame_of(u2); d = S.disc(10.0)
cands = []
for mem in (7, 1):
    for b in (22, 30, 40, 50, 60):
        for az in range(0, 360, 30):
            dirn = unit(math.cos(math.radians(b)) * u2 + math.sin(math.radians(b)) * (math.cos(math.radians(az)) * e + math.sin(math.radians(az)) * f))
            ee, ff = S.frame_of(dirn); pts = d[:, :1] * ee + d[:, 1:] * ff
            cands.append((mem, b, az, (mem, pts, np.broadcast_to(dirn, pts.shape).copy(), 140.0)))
t = time.time(); res = M.needed([c[3] for c in cands], poses); print("needed", round(time.time() - t, 1), "s", len(poses), "poses")
out = []
for (mem, b, az, _), h in zip(cands, res):
    pm = h.max(1); ok = pm < 1e5
    if ok.sum() < 10: out.append((mem, b, az, None, None)); continue
    F = np.percentile(pm[ok], 95); ib = float(((F - h[ok]) <= 12.0).mean())
    out.append((mem, b, az, round(ib, 3), round(float(np.percentile(pm[ok], 95) - np.percentile(pm[ok], 5)), 1)))
for mem in (7, 1):
    print("member", mem, "(7 = link 2a: moves with q1,q2; 1 = link 1: moves with q1)")
    for b in (22, 30, 40, 50, 60):
        print("  arc from J2", b, " ".join(f"{az}:{ib}/{sp_}" for m_, bb, az, ib, sp_ in out if m_ == mem and bb == b))
json.dump(out, open(sys.argv[2], "w"))
