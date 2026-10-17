"""Alignment skeptic probe: per-part sampling density (samples per mm2 of each rigid part's point set, PCA plane +
convex hull) and, for an RSSR drive model, the crank angle phi along the model's own K grid. Model unchanged; fit
bench Bench(60,160) fast; read-only (prints JSON). A part sampled denser than the others weighs more in the
sample-weighted in-band share (docs/ALIGNMENT.md S-class).

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_part_density.py <row id> [K_deg ...]
"""
import importlib.util, json, math, os, sys
import numpy as np
from scipy.spatial import ConvexHull

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))


def main():
    rid = sys.argv[1]; ks = [float(x) for x in sys.argv[2:]]
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", rid + ".json")))
    sp = importlib.util.spec_from_file_location("pd_" + rid.replace("-", "_"), os.path.join(REPO, "docs", "concepts", "models", rid + ".py"))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    B = mod.CB.Bench(n_clip=60, n_ws=160); r, M = mod._report(B, dict(row["best_params"]))
    dens = {}
    for k, v in M.rigid.items():
        X = np.asarray(v[1], float)
        if len(X) < 4: dens[k] = dict(n=len(X)); continue
        C = X - X.mean(0); _, s, vt = np.linalg.svd(C, full_matrices=False); Y = C @ vt[:2].T
        try: a = float(ConvexHull(Y).volume)
        except Exception: a = float("nan")
        dens[k] = dict(n=len(X), area_mm2=round(a, 1), per_mm2=round(len(X) / a, 3) if a > 0 else None)
    out = dict(id=rid, fit_gap=r.get("gap"), density=dens)
    g = getattr(M, "_scg", None)
    if g and "phig" in g:
        kg = np.degrees(g["kgrid"]); ph = np.degrees(g["phig"])
        out["crank_phi_deg_at_K"] = {f"{k:g}": round(float(np.interp(k, kg, np.abs(ph))), 2) for k in (ks or [10, 20, 30])}
        out["dK_lim_deg"] = round(math.degrees(g.get("dK_lim", float("nan"))), 2); out["why_lim"] = g.get("why_lim")
    print(json.dumps(out, default=float))


if __name__ == "__main__":
    main()
