"""R9 sizing study: what thickness / width of one load-path part brings it to SF 1.5 (judge/fea.py's loads, CalculiX).
The part's own tet10 mesh (judge/fea.py, k = 2) is mapped and re-solved, so the junctions, gussets and hub pads scale
with the member instead of a beam formula standing in for them:
  thickness x s_t: every point moves away from the skin side along its thickness vector, x -> x_s + s_t (x - x_s), x_s =
                   the nearest skin-side surface point (--tmode normal, default). --tmode radial (r -> r_in + s_t (r - r_in)
                   along rays from GH) is wrong on the ramps into a raised hub: it lengthens them instead of thickening them
  width x s_w:     every point moves along the member plane's normal n = a_prox x a_dist (both joint axes pass through
                   GH), x -> x + (s_w - 1)(x . n) n: the strap's width scales about its spine plane
The hubs keep their geometry (the joint stack is fixed by the bearings): the map fades in from the hub edge (HUB_R + 2 mm)
over 6 mm (smootherstep), as a redesign would thicken the arm, not the joint. Mass from the mapped mesh.
    python3 judge/fea_sizing.py <design id> <part> [--t 1,1.5,1.8] [--w 1,2,3]   -> <design>/judge/fea_sizing_<part>.json
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fea as F
HUB_R = 10.0                                                                            # v5 O20 hub radius (v4: 11.5)
from common import design_dir, REPO

def skin_radius(X, T):
    """r_in at every node: the smallest radius among the boundary nodes within ~1.5 mm (angular) of its ray, smoothed"""
    from scipy.spatial import cKDTree
    el, fc = F.boundary_faces(T); b = np.unique(T[el][np.arange(len(el))[:, None], F.FACES[fc]])
    r = np.linalg.norm(X, axis=1); u = X / r[:, None]; tb = cKDTree(u[b])
    rin = np.empty(len(X)); rb = r[b]
    for i0 in range(0, len(X), 20000):
        idx = np.arange(i0, min(len(X), i0 + 20000)); q = tb.query_ball_point(u[idx], 1.5 / np.maximum(r[idx], 20.0))
        rin[idx] = [rb[j].min() if len(j) else r[i] for i, j in zip(idx, q)]
    _, nb = cKDTree(u).query(u, k=12); return rin[nb].mean(1)                                 # smooth the field (no kinks -> no inverted tets)

def skin_side_offset(X, T):
    """thickness vector at every node: x - x_s, x_s = the nearest skin-side boundary node (outward normal facing GH,
    n . x_hat < -0.3), smoothed 3 x over 24 neighbours. Closest-point projection follows the true thickness direction, on the
    ramps too (a ramp climbing radially into a raised hub has its thickness across, not along, the radius)"""
    from scipy.spatial import cKDTree
    el, fc = F.boundary_faces(T); C = T[el][np.arange(len(el))[:, None], F.FACES[fc]]
    opp = T[el, [({0, 1, 2, 3} - set(F.FACES[f])).pop() for f in fc]]
    n = np.cross(X[C[:, 1]] - X[C[:, 0]], X[C[:, 2]] - X[C[:, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True)
    cen = X[C].mean(1); n *= np.sign(np.einsum("ij,ij->i", n, cen - X[opp]))[:, None]
    NN = np.zeros_like(X); np.add.at(NN, C.ravel(), np.repeat(n, 3, axis=0)); b = np.unique(C)
    nb = NN[b] / np.maximum(np.linalg.norm(NN[b], axis=1, keepdims=True), 1e-12)
    skin = b[np.einsum("ij,ij->i", nb, X[b] / np.linalg.norm(X[b], axis=1, keepdims=True)) < -0.3]
    _, j = cKDTree(X[skin]).query(X, k=1); V = X - X[skin][j]
    _, nbr = cKDTree(X).query(X, k=24)
    for _ in range(3): V = V[nbr].mean(1)                                                       # 3 smoothing passes: no kinks at the strap edges
    return V

def run(did, part, ts, ws, threads=1, tmode="normal", fade0=2.0, fade_len=6.0):
    dd = design_dir(did); pf = json.load(open(os.path.join(dd, "parts_full.json"))); mat = F.material_for(pf, part)
    kind = dict(F.PARTS)[part]; step = os.path.join(dd, "step", part + ".step"); centres = F.cuff_screw_centres(dd)
    if kind == "bottom" and centres: step, _ = F.cut_beyond_support(step, centres, os.path.join(REPO, ".cache", "fea", did, "BOTTOM_cut.step"))
    wall = F.wall_thickness(step); P0 = F.prepare_part(step, part, kind, 2, wall, centres); X0 = P0["X"].copy()
    G = F.part_setup(step, part, kind); hubs = sorted(G["hubs"], key=lambda h: -abs(h["a"][0])) if kind == "link" else G["hubs"]
    n = np.cross(hubs[0]["a"], hubs[1]["a"]) if len(hubs) >= 2 else None
    if n is not None: n /= np.linalg.norm(n)
    rin = skin_radius(X0, P0["T"]) if tmode == "radial" else None; r0 = np.linalg.norm(X0, axis=1); u0 = X0 / r0[:, None]
    V0 = skin_side_offset(X0, P0["T"]) if tmode == "normal" else None
    dh = np.min([np.where(X0 @ h["a"] > 0, np.linalg.norm(X0 - np.outer(X0 @ h["a"], h["a"]), axis=1), 1e9) for h in hubs], axis=0)   # distance from the nearest hub axis
    q = np.clip((dh - (HUB_R + fade0)) / fade_len, 0, 1); fade = q ** 3 * (q * (q * 6 - 15) + 10)       # 0 on the hub, 1 on the arm (smootherstep)
    old = json.load(open(fn)) if os.path.exists(fn := os.path.join(dd, "judge", f"fea_sizing_{part}.json")) else None
    rows = [r for r in (old or {}).get("rows", []) if "SF" in r and not any(abs(r["t_scale"] - a) < 1e-9 and abs(r["w_scale"] - b) < 1e-9 for a, b in [(t, 1.0) for t in ts] + [(1.0, w) for w in ws])]
    for st, sw in [(t, 1.0) for t in ts] + [(1.0, w) for w in ws if w != 1.0]:
        if sw != 1.0 and n is None: continue
        se = 1.0 + (st - 1.0) * fade
        X = u0 * (rin + se * (r0 - rin))[:, None] if tmode == "radial" else X0 + (se - 1.0)[:, None] * V0
        if sw != 1.0: X = X + ((sw - 1.0) * fade * (X @ n))[:, None] * n
        vol = F.tet_volumes(X, P0["T"])
        if (vol <= 0).any():
            bad = np.unique(P0["T"][vol <= 0][:, :4]); rows.append(dict(t_scale=st, w_scale=sw, error=f"{int((vol <= 0).sum())} inverted tets", bad_hub_dist_mm=np.round(np.percentile(dh[bad], [0, 50, 100]), 1).tolist()))
            F.log(f"{part} t x{st:g} w x{sw:g}: {rows[-1]}"); continue
        P = dict(P0, X=X, vol_mm3=float(vol.sum())); el_ = np.nonzero(P0["ld_sel"])[0]
        P["ld_ref"] = P0["ld_ref"] * (np.linalg.norm(X[el_], axis=1).mean() / np.linalg.norm(X0[el_], axis=1).mean())
        work = os.path.join(REPO, ".cache", "fea", did, f"sizing_{part}_t{st:g}_w{sw:g}"); t0 = time.time()
        D, sec = F.unit_data(P, mat, work, threads); p = F.post_part(part, mat, P0["info"], D)
        rows.append(dict(t_scale=st, w_scale=sw, tmode=tmode if st != 1.0 else None, fade_mm=[HUB_R + fade0, HUB_R + fade0 + fade_len], mass_g=round(p["mass_g"], 2), D1_MPa=p["cases"]["D1"]["vm_MPa"], D1F_MPa=p["cases"]["D1F"]["vm_MPa"], SF=p["cases"]["D1F"]["SF"],
                         at_mm=p["cases"]["D1F"]["at_mm"], d_GH_mm=p["deflection"]["d_GH_mm"], ccx_s=round(sec, 1)))
        F.log(f"{part} t x{st:g} w x{sw:g}: {rows[-1]['mass_g']} g, D1F {rows[-1]['D1F_MPa']} MPa, SF {rows[-1]['SF']}, d_GH {rows[-1]['d_GH_mm']} mm ({time.time() - t0:.0f} s)")
    base = next((r for r in rows if r.get("t_scale") == 1.0 and r.get("w_scale") == 1.0 and "SF" in r), None)
    fit = {}
    for key in ("t_scale", "w_scale"):
        pts = [(r[key], r["D1F_MPa"]) for r in rows if "SF" in r and r["t_scale" if key == "w_scale" else "w_scale"] == 1.0]
        if base and len(pts) >= 2:
            x, y = np.log([p[0] for p in pts]), np.log([p[1] for p in pts]); b = np.polyfit(x, y, 1)[0]
            need = (base["D1F_MPa"] / (mat["Sy"] / F.SF_MIN)) ** (-1.0 / b) if b < 0 else None
            mpts = [(r[key], r["mass_g"]) for r in rows if "SF" in r and r["t_scale" if key == "w_scale" else "w_scale"] == 1.0]
            bm = np.polyfit(np.log([p[0] for p in mpts]), np.log([p[1] for p in mpts]), 1)[0]
            fit[key] = dict(stress_exponent=round(float(b), 2), scale_for_SF_1_5=None if need is None else round(float(need), 2),
                            mass_at_SF_1_5_g=None if need is None else round(float(base["mass_g"] * need ** bm), 1), mass_exponent=round(float(bm), 2))
    out = dict(version=F.VERSION, design=did, part=part, material=F.mat_name_of(mat), base_wall_mm=dict(p10=round(wall[0], 2), median=round(wall[1], 2)), rows=rows, fit=fit,
               method=__doc__.split("\n\n")[0])
    json.dump(out, open(fn, "w"), indent=1); print(json.dumps(fit)); return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("part"); ap.add_argument("--t", default="1,1.5,1.8"); ap.add_argument("--w", default="2,3")
    ap.add_argument("--threads", type=int, default=1); ap.add_argument("--tmode", default="normal", choices=["normal", "radial"])
    ap.add_argument("--fade0", type=float, default=2.0, help="the map starts this far outside the hub radius (mm)"); ap.add_argument("--fade_len", type=float, default=6.0); A = ap.parse_args()
    run(A.design, A.part, [float(v) for v in A.t.split(",") if v], [float(v) for v in A.w.split(",") if v], A.threads, A.tmode, A.fade0, A.fade_len)
