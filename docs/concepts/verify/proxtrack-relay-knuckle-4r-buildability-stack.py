"""Buildability lens, pin-a stack check for proxtrack-relay-knuckle-4r: the claim bumps the pin-a boss (member 3) and
the knee link (member 6) by independent per-point amounts. The knee link rides ABOVE the boss on pin a (skin-normal
pin; knee underside at tr + off_k, boss underside at tr, boss top at tr + tp). After the bump, does the boss top rise
into the knee link's eye? Measured at every fit-bench pose (the poses the bump is sized on): for knee-link underside
points within the boss radius of pin a's axis, height along the pin axis minus the bumped boss top (>= 0 = buildable).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability-stack.py out.json
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("proxtrack_for_stack_v", os.path.join(REPO, "docs", "concepts", "models", "proxtrack-relay-knuckle-4r.py"))
PT = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PT)
AA, CB, CC = PT.AA, PT.CB, PT.CC
CLAIM = dict(PHI=35.0, ds=19.538, rt_extra=1.5, pre=10.41, bump=1.002, band=9.272, ramp=6.0, tilt=12, taz=235, sgn=1, flood=1, hw=1, hwv="plain")


def bumped(M, j, m, X, a, ax):
    w = M.world(m, j, X)
    if a is None or not np.any(a > 0): return w
    RS, Q = M.RS[j], M.Q[j]; h = (w @ RS) @ Q; r = AA._rad(h, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
    h = h + a[:, None] * r / n; return (h @ Q.T) @ RS.T


def main(outp):
    os.environ.pop("CB_EXACT", None)
    P = CC._clamp(dict(CC.PARAMS, **AA.LEAD)); B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); M1.run()
    rp = dict(PT.DEF); rp.update(CLAIM); ax = AA.raxis(rp["tilt"], rp["taz"])
    G = PT.geometry(M1, B1, ax, rp); bumps = PT.bump_amounts(M1, G, ax)
    mb, Xb = M1.rigid["boss"]; mk, Xk = M1.rigid["knee"]; ab = bumps.get(("rigid", "boss")); ak = bumps.get(("rigid", "knee"))
    A0 = M1.fr["A0"]; sn = np.asarray(M1.D.sn, float); tp = float(M1.D.p["tp"])
    R_boss = float(np.max(np.linalg.norm((Xb - A0) - ((Xb - A0) @ sn)[:, None] * sn[None], axis=1)))
    rows = []
    for j in np.nonzero(M1.kin_ok)[0]:
        c = M1.world(mb, j, A0[None])[0]; u = M1.world(mb, j, (A0 + sn)[None])[0] - c; u /= np.linalg.norm(u)
        out = {}
        for tag, aB, aK in (("lead", None, None), ("claim", ab, ak)):
            wb = bumped(M1, j, mb, Xb, aB, ax); wk = bumped(M1, j, mk, Xk, aK, ax)
            hb = (wb - c) @ u; hk = (wk - c) @ u; rk = np.linalg.norm((wk - c) - hk[:, None] * u[None], axis=1)
            sel = rk <= R_boss + 0.5
            out[tag] = float((hk[sel].min() if sel.any() else np.inf) - (hb.max() + tp))
        rows.append((out["claim"], out["lead"], int(j)))
    rows.sort()
    res = dict(n=len(rows), boss_amount_mm=[round(float(ab.min()), 2), round(float(ab.max()), 2)] if ab is not None else None,
               knee_amount_mm=[round(float(ak.min()), 2), round(float(ak.max()), 2)] if ak is not None else None, R_boss=round(R_boss, 2), tp=tp,
               lead_gap_mm=[round(min(r[1] for r in rows), 3), round(max(r[1] for r in rows), 3)],
               claim_gap_min_mm=round(rows[0][0], 3), claim_poses_interfering=int(sum(1 for r in rows if r[0] < 0)),
               claim_interf_p50_mm=round(float(np.median([r[0] for r in rows])), 3),
               worst=[dict(gap_claim=round(r[0], 2), gap_lead=round(r[1], 2), j=r[2], kind=B1.kind[r[2]], pose=[B1.poses[r[2]][k] for k in ("plane", "elev", "axial")]) for r in rows[:6]])
    print(json.dumps(res)); json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1])
