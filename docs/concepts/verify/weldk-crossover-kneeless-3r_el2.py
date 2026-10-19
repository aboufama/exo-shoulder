"""weldk-crossover-kneeless-3r verifier, part 2: an EXACT E-leg vs link-2 solid test on every taken pose.

The V7 kd test of weldk-crossover-kneeless-3r.py (H1's: mid-surface samples as 1.5 mm spheres) reads low for two 3 mm
plates that cross at an angle (two parallel plates stacked 0.15 apart and tilted by t read 1.65 cos t - 1.5, e.g. 0.13
at 10 deg), so its 13 removals are re-tested here against the true solids:

  E leg (member 3, home frame of member 3, E coordinates x along eE, y along nE, z along sn from the hub-3 centre) =
  the extrusion over |y| <= W/2 of the x-z polygon between the fitted underside polyline (x_s, rE) and the top
  (x_s, rE + T_LINK), from the hub-3 rim (x = r3, at the rim height F3 + UP) to the last station; plus the boss cylinder
  (radius BOSS_R about pin a, z in [zb, zb + tp]).  Distance from a point = exact (segment distance in x-z, combined
  with the y overshoot; interior points negative).
  Link 2 (member 2) = its fitted shell: rows of underside samples r * dv at lateral -3, -1, 1, 3 mm, extended by 1 mm
  to its true edges (+-4), bilinearly densified to 0.1 mm along x 0.2 mm across, top surface r + 3 and underside r,
  side faces at 0.25 mm through the thickness.

A pose clashes if the exact E / boss to link-2 clearance < 0.15 mm - 1e-3 (the running gap: adjacent members of J3; the
tolerance absorbs float equality at the model's binding stacked rule). Red-team bound: where the E / boss meets link 2
more than 10 mm past the hub-3 rim the two plates are no longer a bearing's running pair, so that clearance is also
read against the non-adjacent 1 mm (gap_far_bound).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/weldk-crossover-kneeless-3r_el2.py bench|held out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402
sp = importlib.util.spec_from_file_location("weldk_kl_v2", os.path.join(REPO, "docs", "concepts", "models", "weldk-crossover-kneeless-3r.py"))
MD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MD)
S, PK = MD.S, MD.PK
TOL, FAR = 1e-3, 10.0      # numeric tolerance on the binding 0.15 rule; the 'far' red team starts 10 mm past the hub-3 rim
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "weldk-crossover-kneeless-3r.json")))


def seg_dist(px, pz, ax, az, bx, bz):
    """distance from points (px, pz) (n,) to segments a-b (m,) -> (n,)"""
    dx, dz = bx - ax, bz - az; L2 = dx * dx + dz * dz
    t = np.clip(((px[:, None] - ax[None]) * dx[None] + (pz[:, None] - az[None]) * dz[None]) / np.maximum(L2, 1e-12)[None], 0, 1)
    qx = ax[None] + t * dx[None]; qz = az[None] + t * dz[None]
    return np.sqrt((px[:, None] - qx) ** 2 + (pz[:, None] - qz) ** 2).min(1)


def l2_dense(M):
    """link-2 surface points in member-2 home coordinates (top, underside, side faces)"""
    lk = M.geo.links[1]; m2, P2 = M.link_pts["L2"]; rows = lk["rows"]; sizes = [int(k.sum()) for _, k, _ in rows]; cut = np.cumsum([0] + sizes)
    nst = len(rows[0][0]); R = np.full((len(rows), nst), np.nan); DV = np.zeros((len(rows), nst, 3))
    for k, (dv, keep, sarc) in enumerate(rows):
        idx = np.nonzero(keep)[0]; pk = P2[cut[k]:cut[k + 1]]
        R[k, idx] = np.linalg.norm(pk, axis=1); DV[k] = dv
    # lateral extension to the true edges: outer row + 0.5 (outer - inner) in direction and radius
    DVe = np.concatenate([DV[:1] + 0.5 * (DV[:1] - DV[1:2]), DV, DV[-1:] + 0.5 * (DV[-1:] - DV[-2:-1])])
    Re = np.concatenate([R[:1] + 0.5 * (R[:1] - R[1:2]), R, R[-1:] + 0.5 * (R[-1:] - R[-2:-1])])
    DVe = DVe / np.linalg.norm(DVe, axis=2)[..., None]
    top, und, side = [], [], []
    ua = np.linspace(0, 1, 11)[:, None]; va = np.linspace(0, 1, 11)
    for a in range(Re.shape[0] - 1):
        for j in range(nst - 1):
            rr = Re[a:a + 2, j:j + 2]
            if not np.isfinite(rr).all(): continue
            d = DVe[a:a + 2, j:j + 2]
            for dz, out in ((0.0, und), (S.T_LINK, top)):
                P00, P01, P10, P11 = (d[0, 0] * (rr[0, 0] + dz), d[0, 1] * (rr[0, 1] + dz), d[1, 0] * (rr[1, 0] + dz), d[1, 1] * (rr[1, 1] + dz))
                # u across (rows), v along (stations): 11 x 21
                vv = np.linspace(0, 1, 21)[None, :, None]; uu = ua[:, :, None]
                X = (1 - uu) * ((1 - vv) * P00 + vv * P01) + uu * ((1 - vv) * P10 + vv * P11)
                out.append(X.reshape(-1, 3))
            if a in (0, Re.shape[0] - 2):          # side face at the outer edge
                e = 0 if a == 0 else 1
                for t in np.linspace(0, S.T_LINK, 13):
                    vv = np.linspace(0, 1, 21)[:, None]
                    side.append((1 - vv) * d[e, 0] * (rr[e, 0] + t) + vv * d[e, 1] * (rr[e, 1] + t))
    return np.concatenate(top + und + side)


def main():
    wear = sys.argv[1]; outp = sys.argv[2]; P = dict(ROW["best_params"]); t0 = time.time()
    if wear == "held":
        import types
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_kl2", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py"))
        PV = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PV)
        sys.modules["osn_polish"] = types.SimpleNamespace(held_bench=lambda *a, **k: PV.held_bench())   # the verifiers' held set
        res, M, B = MD.frozen(P, -1, -1)
    else:
        res, M, B = MD.frozen(P)
    D = M.D; fr = M.fr; c3 = D.c[2]; xs, rE = np.asarray(M._xsE, float), np.asarray(M._rE, float)
    r3 = float(M.hr[2]); rim = float(M.f[2] + S.UP)
    px_ = np.r_[r3, xs]; pu = np.r_[rim, rE]; pt = pu + S.T_LINK
    # closed polygon: underside forward, end cap, top backward, start cap
    poly_x = np.r_[px_, px_[::-1], px_[0]]; poly_z = np.r_[pu, pt[::-1], pu[0]]
    ax, az, bx, bz = poly_x[:-1], poly_z[:-1], poly_x[1:], poly_z[1:]
    x0, x1 = float(px_[0]), float(px_[-1]); W2 = S.W_LINK / 2
    A0 = fr["A0"] - c3; ax0, ay0 = float(A0 @ fr["eE"]), float(A0 @ fr["nE"]); zb, tp = float(M.zb), float(M.p["tp"])
    L2h = l2_dense(M)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    out = []
    for i in taken:
        R2, t2 = M.T(2, i); R3, t3 = M.T(3, i)
        X = (L2h @ R2.T + t2 - t3) @ R3 - c3
        x, y, z = X @ fr["eE"], X @ fr["nE"], X @ D.sn
        best = 1e9; arg = None; far = 1e9
        m = (x > x0 - 3) & (x < x1 + 3) & (np.abs(y) < W2 + 3) & (z > pu.min() - 3) & (z < pt.max() + 3)
        if m.any():
            xm, ym, zm = x[m], y[m], z[m]
            dxz = seg_dist(xm, zm, ax, az, bx, bz)
            inside = (xm >= x0) & (xm <= x1) & (zm >= np.interp(xm, px_, pu)) & (zm <= np.interp(xm, px_, pt))
            dy = np.abs(ym) - W2
            d = np.where(inside & (dy <= 0), -np.minimum(dxz, -dy), np.where(inside, dy, np.sqrt(dxz ** 2 + np.maximum(dy, 0) ** 2)))
            k = int(np.argmin(d)); best = float(d[k]); arg = ("E", round(float(xm[k]), 2), round(float(ym[k]), 2), round(float(zm[k]), 2))
            fm = xm > r3 + FAR
            if fm.any(): far = float(d[fm].min())
        rr = np.hypot(x - ax0, y - ay0) - PK.BOSS_R; dz = np.maximum(np.maximum(zb - z, z - (zb + tp)), 0)
        db = np.where((rr <= 0) & (dz <= 0), -np.minimum(-rr, np.minimum(z - zb, zb + tp - z)), np.sqrt(np.maximum(rr, 0) ** 2 + dz ** 2))
        kb = int(np.argmin(db))
        if float(db[kb]) < best: best = float(db[kb]); arg = ("boss", round(float(x[kb]), 2), round(float(y[kb]), 2), round(float(z[kb]), 2))
        far = min(far, float(db[kb]))
        out.append((best, i, arg, far))
    out.sort(key=lambda t: t[0])
    faro = sorted([(f, i) for _, i, _, f in out])
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    rmv = [i for d, i, _, _ in out if d < 0.15 - TOL]
    keep_res = list(B.res)
    for i in rmv: B.res[i] = None
    r = B.report()
    # red-team bound: E / boss vs link 2 further than FAR mm beyond the hub-3 rim treated as NON-adjacent parts (>= 1 mm)
    rf = [i for f, i in faro if f < S.PART_CLEAR]
    for i in rf: B.res[i] = None
    r_far = B.report(); B.res = keep_res
    o = dict(model_frozen=res["frozen"], n_taken=len(taken), l2_points=int(len(L2h)),
             low=[dict(gap_mm=round(d, 4), where=a, far_mm=round(f, 3), **lab(i)) for d, i, a, f in out[:20]],
             all={int(i): [round(d, 4), a, round(f, 3)] for d, i, a, f in out if d < 3.0},
             far_low=[dict(far_mm=round(f, 3), **lab(i)) for f, i in faro[:12]], tol=TOL, far_from_rim_mm=FAR,
             far_lt1mm=[lab(i) for i in rf],
             gap_far_bound={k: r_far[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
             clash=[lab(i) for i in rmv], n_clash=len(rmv),
             gap_after_sharp={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
             E_poly=dict(x0=x0, x1=x1, rim=rim, W2=W2, boss=[round(ax0, 2), round(ay0, 2), zb, tp]), secs=round(time.time() - t0, 1),
             note="exact clearance from link 2's densified shell (top, underside, side faces) to the E leg extrusion and the boss cylinder; < 0.15 = clash")
    json.dump(o, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: o[k] for k in ("model_frozen", "n_clash", "gap_after_sharp", "gap_far_bound", "far_low", "secs")}, default=float))


if __name__ == "__main__":
    main()
