"""Independent hold check at stop A for pick1 (docs/research/pick1_k_hold.md section 2): the judge's own simulation with
gravity scaled AND re-pointed (the claim only scales it along the upright thorax -y).

  dirs: "up2g"   2 g along thorax -y (the claim's case)
        "fwd1g"  1 g along thorax +x (wearer bent forward 90 deg: the chest faces the floor)
        "back1g" 1 g along thorax -x (lying supine)
        "side1g" 1 g along thorax +z / "side1gn" -z (lying on a side)
Per clip: largest K opening from stop A where the plan has K on stop A (plan < 0.2 deg), and the share of those samples
lifted > 0.5 deg; plus the drift. Judge imported unchanged; only option_xml's gravity string is replaced.

    OMP_NUM_THREADS=1 python3 docs/research/pick1_k_hold_check/hold_check.py <design> <preload> <dir,dir,...> <out.json>
"""
import json, math, os, sys
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
for p in ("judge", os.path.join("pipeline", "avg"), os.path.join("pipeline", "full-exo")): sys.path.insert(0, os.path.join(REPO, p))
import dynamics as D

G = {"up2g": (0, -2 * 9.81, 0), "up1g": (0, -9.81, 0), "fwd1g": (9.81, 0, 0), "back1g": (-9.81, 0, 0), "side1g": (0, 0, 9.81), "side1gn": (0, 0, -9.81),
     "fwd2g": (2 * 9.81, 0, 0), "back2g": (-2 * 9.81, 0, 0)}
_OPT = D.option_xml
def set_g(v):
    s = 'gravity="0 -9.81 0"'
    def opt(dt=D.DT, gravity=True):
        x = _OPT(dt, gravity); assert s in x; return x.replace(s, 'gravity="%.6g %.6g %.6g"' % v)
    D.option_xml = opt

dd, preload, dirs, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3].split(","), sys.argv[4]
des = D.GenDesign(dd); des.k_preload = preload; des.spring = des.springs(des.k_rate)
iK, qA, sg = des.spring_def
out = dict(design=des.id, preload=preload, runs={})
for dn in dirs:
    set_g(G[dn]); res = {}
    for ci, c in enumerate(des.clips):
        summ, R = D.run(des, ci, record=True, speed=1.0, case="passive", mu_eff=0.005, tau0=D.TAU0_ROLL, tilt="hub")
        w = R["warm"]; xs = np.degrees(sg * (qA - R["q"][w][:, iK])); xp = np.degrees(sg * (qA - R["qp"][w][:, iK]))
        onA = xp < 0.2
        res[c["name"]] = dict(drift=summ.get("spare_drift_deg"), lift_max_deg=round(float(xs[onA].max()), 3) if onA.any() else None,
                              lift_share_gt0p5=round(float((xs[onA] > 0.5).mean()), 4) if onA.any() else None, twist=summ["tracking_deg"]["twist_peak"])
        print(dn, c["name"], res[c["name"]], flush=True)
    out["runs"][dn] = res
D.option_xml = _OPT
json.dump(out, open(outp, "w"), indent=1)
