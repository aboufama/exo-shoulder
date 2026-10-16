"""K's hold demand on pick1 with gravity in its REAL direction (thorax -y, the scapula law per pose) instead of the red
team's "any direction": the same generalized-force method as docs/concepts/verify/minarc-pick1-redteam.py mech_one (imported
unchanged: MECH.kin at dK0 and dK0 + an opening eps, buildability-lens member masses + 4 g for the cap and strip, 2 mN.m
per sealed bearing pair along the self-motion), over every eval pose of the bench pose set (clips, workspace envelope, fresh
envelope) in state A (K on stop A).

    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 python3 docs/research/pick1_k_hold/demand_real_g.py OUT.json
"""
import json, math, os, sys
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
V = os.path.join(REPO, "docs", "concepts", "verify")
sys.path.insert(0, V)
import importlib.util
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
RT = _load("rt_pick1", os.path.join(V, "minarc-pick1-redteam.py"))
sys.path.insert(0, os.path.join(REPO, "judge")); import dynamics as DY          # scap(): body_pose.scap law (scapula in the thorax)
D2R = math.pi / 180

def main(outp):
    assert RT.KIT.FOLD_MARGIN == 5.5
    R = RT._load("rt_remeasure_m", os.path.join(V, "minarc-bdp-remeasure.py")); MECH = RT._load("rt_mech", os.path.join(V, "minarc-stop-knuckle-4r-mechanism.py"))
    Pp, pinfo = RT.params(R, "pick1")
    fitB = R.PV.fast_bench(60, 160); M1 = R.KR.KModel(fitB, dict(Pp)); M1.run(); D = M1.D
    Z = RT.CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; Q = Z["HG"].astype(float); P = np.asarray(Z["POSE"], float)
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s); ok = ok & Kn["ok"]
    st = np.asarray(D._state).copy(); dK0 = np.asarray(D._dK).copy(); sp = float(np.sign(D.psiA))
    mass = MECH.member_mass_model(M1); mass[7] = (mass[7][0] + 4.0, mass[7][1]); MECH.M = R.KR.KB; eps = 0.2 * D2R
    def coms(dK):
        k = MECH.kin(D, Q, dK); Rm = {1: k["R1"], 7: k["R1"] @ k["RK"], 2: k["R12"], 3: k["R123"]}; t = {3: k["t3"]}
        return {mm: (gm, np.einsum("nij,j->ni", Rm[mm], c) + (t[mm] if mm in t else 0)) for mm, (gm, c) in mass.items() if mm in Rm}, k
    C0, k0 = coms(dK0); Cp, kp = coms(dK0 + sp * eps)
    q2err = np.degrees(np.abs(R.PK.wrap(k0["q"][:, 1] - q[:, 1])))
    grad = sum(gm * (Cp[mm][1] - C0[mm][1]) for mm, (gm, _) in Cp.items()) / eps        # d(sum m x)/d(opening), g mm / rad, scapula frame
    tau_any = np.linalg.norm(grad, axis=1) * 9.81e-6
    Rs = DY.scap(P[:, 1], 0); gdir = np.einsum("nji,j->ni", Rs, np.array([0.0, -1.0, 0.0]))   # gravity direction in the scapula frame
    tau_open = 9.81e-6 * (grad * gdir).sum(1)                                              # > 0: gravity opens K (pulls it off stop A)
    dq = np.degrees(np.abs(R.PK.wrap(kp["q"] - k0["q"]))) / math.degrees(eps); fric = 2e-3 * (1 + dq.sum(1))
    okm = ok & (kp["g2"] > 0) & (k0["g2"] > 0) & (q2err < 0.5)
    ws = np.array([str(n).startswith("Workspace") for n in names])[cid]; fresh = np.array([str(n).startswith("Envelope") for n in names])[cid]
    out = dict(config="pick1", rule="demand = max(0, gravity torque along K's opening, REAL direction) x g + 2 mN.m per sealed pair along the self-motion; "
               "the red team's state-A 0.0478 N.m is 2 g in the WORST direction + the same friction")
    for nm, sel in (("stateA_all", okm & (st == 0)), ("stateA_clip_frames", okm & (st == 0) & ~ws & ~fresh), ("stateA_workspace", okm & (st == 0) & (ws | fresh))):
        if not sel.any(): out[nm] = dict(n=0); continue
        r = dict(n=int(sel.sum()))
        for gs in (1.0, 2.0):
            dem = np.maximum(0.0, tau_open[sel]) * gs + fric[sel]
            r[f"{gs:g}g_real"] = dict(max_Nm=round(float(dem.max()), 4), p99_Nm=round(float(np.percentile(dem, 99)), 4), median_Nm=round(float(np.median(dem)), 4),
                                      share_gravity_closes=round(float((tau_open[sel] <= 0).mean()), 3),
                                      over_0p040=int((dem > 0.040).sum()), over_0p035=int((dem > 0.035).sum()), worst_pose=[round(float(x), 1) for x in P[sel][np.argmax(dem)][:3]])
            r[f"{gs:g}g_any_dir"] = dict(max_Nm=round(float((tau_any[sel] * gs + fric[sel]).max()), 4))
        out[nm] = r
    json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
