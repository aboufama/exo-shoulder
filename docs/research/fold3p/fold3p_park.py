"""Hub parking gate of the coupled-J1-rocker closures (fold3p.py PROX), relay_parking.py-style, Bench(110,360) EXACT skin.

Per taken pose (static closure + window + travel; workspace poses also continuity-connected) the skin requirement along
the ray each hub sits on (K3 march, 2 mm clearance, exact distance): hub 1 (J1 line Rc(rho) u1 from the moving chain
centre G'), hub 2 (J2 = two-circle closure of (Rc(rho) u1, w), branch sigma of H1, from G'), the rocker pivot hub (line c
through o, posterior end). One level per hub = quantile 0.97 of its requirements over the taken poses (the j2knee_gate
rule); in band = level - requirement <= 12 mm. Same metric for the plain H1 seats (no rocker) as the reference.
R (mm) = distance of the pivot line from GH: rho does not depend on it (k = h / R), the chain-centre shift 2 R sin(rho/2) does.

    OMP_NUM_THREADS=1 CB_EXACT=1 CB_QUIET_EXACT=1 python3 docs/research/fold3p/fold3p_park.py
"""
import json, math, os, sys, time
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault("CB_QUIET_EXACT", "1"); os.environ["CB_EXACT"] = "1"
import fold3p as f3                                           # noqa: E402
import concept_bench as CB, concept_kit as K                 # noqa: E402

D2R = math.pi / 180
CANDS = {   # from fold3p.json (search over c, chi, k, branch at the H1 seats; best connected reach per travel cap)
    "A_t30": dict(caz=6.5905, cel=11.2829, chi=28.6728, k=-0.0827, s=1, q0=-6.9265, travel=30.0),
    "B_t45": dict(caz=5.4109, cel=1.6143, chi=27.2107, k=-0.0839, s=1, q0=-7.1772, travel=45.0),
    "C_t45_other_side": dict(caz=5.0123, cel=3.4358, chi=209.6961, k=0.0809, s=-1, q0=-7.0983, travel=45.0),
}
RS_MM = (12.0, 25.0)


def rays():
    """-> list of (name, pose index, origin (3,), dir (3,)) world frame, and the take / connected masks per candidate"""
    B = CB.Bench(110, 360); F = K.frames(B); f3.ELEV = [p["elev"] for p in B.poses]; S = f3.seats(); G = f3.Graph(B, F)
    w = np.einsum("pji,pjk,k->pi", F.RS, F.RHG, S["u3"]); lo, hi = f3.window(S["a1"], S["a2"])
    th0 = f3.ang(S["u1"][None], w); ok0 = (th0 >= lo) & (th0 <= hi)
    R = []; info = {}
    p2, okc, _ = K.closure(F.S(S["u1"]), F.HG(S["u3"]), S["a1"], S["a2"], S["sigma"], margin_deg=0.0)
    take0 = ok0 & okc; info["H1_plain"] = dict(take=take0)
    for i in np.nonzero(take0)[0]:
        R.append(("H1_plain", "hub1", i, np.zeros(3), F.S(S["u1"])[i])); R.append(("H1_plain", "hub2", i, np.zeros(3), K.unit(p2[i])))
    for name, p in CANDS.items():
        ok, q, th = f3.take("prox", p, S, F.RS, F.RHG, p["travel"]); conn = G.connected("prox", p, S, p["travel"], ok[G.ws])
        tk = ok.copy(); tk[G.ws] = conn
        _, _, _, U1, ws_ = f3.prox(p, S, F.RS, F.RHG)
        U1w = np.einsum("pij,pj->pi", F.RS, U1); Ww = np.einsum("pij,pj->pi", F.RS, ws_)
        J2, okc, _ = K.closure(U1w, Ww, S["a1"], S["a2"], S["sigma"], margin_deg=0.0); tk &= okc
        c = K.bvec(p["caz"], p["cel"]); e1, e2 = f3.perp_basis(c); oh = math.cos(p["chi"] * D2R) * e1 + math.sin(p["chi"] * D2R) * e2
        rho = np.radians(q); az_el = []
        for Rm in RS_MM:
            o = Rm * oh; Gp = o - np.einsum("pij,j->pi", f3.rot(c, rho), o)        # scapula frame
            Gw = np.einsum("pij,pj->pi", F.RS, Gp); ow = F.S(o)
            for i in np.nonzero(tk)[0]:
                R.append((f"{name}_R{int(Rm)}", "hub1", i, Gw[i], K.unit(U1w[i]))); R.append((f"{name}_R{int(Rm)}", "hub2", i, Gw[i], K.unit(J2[i])))
                R.append((f"{name}_R{int(Rm)}", "pivot", i, ow[i], F.S(c)[i]))
            info[f"{name}_R{int(Rm)}"] = dict(take=tk, shift_mm_p95=float(np.percentile(np.linalg.norm(Gp[tk], axis=1), 95)),
                                             shift_mm_max=float(np.linalg.norm(Gp[tk], axis=1).max()))
        el = np.degrees(np.arcsin(np.clip(U1[tk][:, 1], -1, 1))); az = np.degrees(np.arctan2(U1[tk][:, 2], -U1[tk][:, 0]))
        info[name] = dict(take=tk, ws_connected=float(conn.mean()), static=float(ok[F.ws].mean()), clip=float(ok[F.clip].mean()),
                          rho=[float(np.percentile(q[tk], 1)), float(np.percentile(q[tk], 99))],
                          J1_az=[float(az.min()), float(az.max())], J1_el=[float(el.min()), float(el.max())],
                          c_dir=c.round(3).tolist(), o_dir=oh.round(3).tolist(),
                          overhead=float(tk[F.ws & (np.array(f3.ELEV) >= 140)].mean()))
    return R, info, F


def _work(args):
    I, R = args; B = CB.Bench(110, 360); out = []
    for i in I:
        js = [j for j, r in enumerate(R) if r[2] == i]
        if not js: continue
        req = K.requirement(B, np.full(len(js), i), np.stack([R[j][4] for j in js]), O=np.stack([R[j][3] for j in js]))
        out += list(zip(js, req.tolist()))
    return out


def main():
    t0 = time.time(); R, info, F = rays(); n = len(F.RS); print(len(R), "rays", round(time.time() - t0, 1), flush=True)
    I = list(range(n)); chunks = [I[k::4] for k in range(4)]
    with Pool(4) as P: res = P.map(_work, [(c, R) for c in chunks])
    req = np.full(len(R), np.nan)
    for part in res:
        for j, v in part: req[j] = v
    out = dict(bench=[110, 360], mode="exact", margin=f3.M, R_mm=list(RS_MM), cands=CANDS, results={})
    keys = sorted({(r[0], r[1]) for r in R})
    for d, h in keys:
        m = np.array([r[0] == d and r[1] == h for r in R]); x = np.where(np.isfinite(req[m]), req[m], 400.0)
        lvl = float(np.quantile(x, 0.97)); ib = float(((lvl - x) <= 12.0).mean())
        out["results"].setdefault(d, {})[h] = dict(n=int(m.sum()), level=round(lvl, 1), in_band=round(ib, 4),
                                                   req_p10_p50_p90=[round(float(np.percentile(x, q)), 1) for q in (10, 50, 90)])
    for k, v in info.items():
        out["results"].setdefault(k, {}).update({a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items() if a != "take"})
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "fold3p_park.json"), "w"), indent=1, default=float)
    for d, v in out["results"].items(): print(d, json.dumps(v)[:600])


if __name__ == "__main__":
    main()
