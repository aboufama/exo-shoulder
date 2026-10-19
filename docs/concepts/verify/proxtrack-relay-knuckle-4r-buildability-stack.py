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


def coil(outp, Ds=(8.0, 5.0), L=8.0):
    """the constant-force spring's coil (OD D, width L, axis along a_r) arm-fixed beyond the zero dowel at the shell's
    station s0: centre radius R_t + D/2, arm azimuth lo - (D/2 + 1)/R_t. Fit-bench poses (phi 0, the poses the bump is
    sized on): chain metal of members 2 / 3 / 6 (claim's bump) within 1 mm of the coil = jam; 'any phi' sweeps the coil
    over the relay's [0, PHI] in the HG' frame (a bound for relayed poses)."""
    os.environ.pop("CB_EXACT", None)
    P = CC._clamp(dict(CC.PARAMS, **AA.LEAD)); B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); M1.run()
    rp = dict(PT.DEF); rp.update(CLAIM); ax = AA.raxis(rp["tilt"], rp["taz"])
    G = PT.geometry(M1, B1, ax, rp); bumps = PT.bump_amounts(M1, G, ax); Rt = G["R_t"]; e, f = G["e"], G["f"]
    res = dict(R_t=round(Rt, 2), s0=round(G["s0"], 2), arc=[round(G["lo"], 1), round(G["hi"], 1)])
    for D in Ds:
        tc0 = G["lo"] - math.degrees((0.5 * D + 1.0) / Rt); n0 = 0; nany = 0; best0 = 1e9; bestany = 1e9; parts = {}
        for j in np.nonzero(M1.kin_ok)[0]:
            RS, Q = M1.RS[j], M1.Q[j]; H = []; names = []
            for nm, (m, X) in list(M1.rigid.items()) + list(M1.link_pts.items()):
                if m not in (2, 3, 6): continue
                a = bumps.get(("rigid", nm), bumps.get(("link", nm)))
                h = (M1.world(m, j, X) @ RS) @ Q
                if a is not None and np.any(a > 0):
                    r = AA._rad(h, ax); nn = np.linalg.norm(r, axis=1, keepdims=True); nn[nn < 1e-9] = 1.0; h = h + a[:, None] * r / nn
                H.append(h); names += [nm] * len(h)
            H = np.concatenate(H); names = np.array(names); dmin_any = 1e9; d0 = None
            for ph in np.arange(0.0, float(rp["PHI"]) + 1e-9, 2.5):
                tc = tc0 - ph; cdir = math.cos(math.radians(tc)) * e + math.sin(math.radians(tc)) * f; cen = G["s0"] * ax + (Rt + 0.5 * D) * cdir
                rel = H - cen; sv = rel @ ax; rr = np.linalg.norm(rel - sv[:, None] * ax[None], axis=1)
                dd = np.sqrt(np.maximum(0, rr - 0.5 * D) ** 2 + np.maximum(0, np.abs(sv) - 0.5 * L) ** 2)
                k = int(np.argmin(dd)); dmin_any = min(dmin_any, float(dd[k]))
                if ph == 0.0: d0 = float(dd[k]); p0 = str(names[k])
            n0 += d0 < 1.0; nany += dmin_any < 1.0; best0 = min(best0, d0); bestany = min(bestany, dmin_any)
            if d0 < 1.0: parts[p0] = parts.get(p0, 0) + 1
        res[f"D{D:g}"] = dict(coil_az=round(tc0, 1), fit_poses=int(M1.kin_ok.sum()), jam_phi0=int(n0), jam_any_phi=int(nany),
                              min_mm_phi0=round(best0, 2), min_mm_any_phi=round(bestany, 2), jam_parts_phi0=parts)
    print(json.dumps(res)); json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "coil": coil(sys.argv[2])
    else: main(sys.argv[1])
