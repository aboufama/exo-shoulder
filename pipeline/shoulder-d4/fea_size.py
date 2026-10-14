"""size the link thickness with fea_link: real D4 link (67.5 deg arc), Ø34 hubs, 14 mm strip, G2 waist (k=10)."""
import math, sys, json, numpy as np
import fea_link as F
arc = 67.5; t_list = [float(x) for x in sys.argv[1:]] or [4.0, 4.5, 5.0]
pA = np.array([0, 0, 1.0]); pB = np.array([math.sin(math.radians(arc)), 0, math.cos(math.radians(arc))])
out = []
for t in t_list:
    r0 = 119.0; r1 = r0 + t; rm = (r0 + r1) / 2
    pf = F.Planform([(pA, 17.0), (pB, 17.0)], [(pA, pB, 7.0)], rm, k=10.0)
    for rig in (9.0,):
        res = F.analyse(pf, pA, pB, r0, r1, rig, 25e3, h=0.8, nl=6, bores=[(pB, 6.0)], excl=1.0)
        C = res["C"]; k_tilt = 1 / np.linalg.eigvalsh((C + C.T) / 2).max() / 1e3 * math.pi / 180     # N.m/deg (softest)
        print(f"t {t}: dof {res['dof']} ({res['secs']:.0f}s)  worst vm @25 N.m {res['vm_max']:.0f} MPa (p99.5 {res['vm_p99']:.0f})  "
              f"SF_yield {F.SY / res['vm_max']:.2f}  softest link stiffness {k_tilt:.1f} N.m/deg", flush=True)
        out.append(dict(t=t, vm=res["vm_max"], p99=res["vm_p99"], k=k_tilt))
        np.savez_compressed(f"fea_t{t}.npz", X=res["X"], H=res["H"], vm=res["vm"], ok=res["ok"])
json.dump(out, open("fea_size.json", "w"))
