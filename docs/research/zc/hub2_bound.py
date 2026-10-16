"""Hub parking bound for the zero-complexity 3R (zc-frontier-3r): a complexity-0 hub is ONE disc at ONE level on its
axis line through GH, so it is in band (2-14 mm) only at poses whose skin exit along that line lies within 12 mm below
its level. For every Sobol config of docs/concepts/zc/sobol_kin.json (fold-law reach on Bench(110,360)) this measures,
on Bench(60,160) fast, the K3 march requirement of the hub CENTRE ray of hubs 1-3 at every pose the chain closes in and
the best in-band share any single level can give each hub ("hub band", the max over levels L of the share of poses
with requirement in [L - 12, L]) - an UPPER bound on the hub's in-band share (the disc's rim samples only add spread).

    OMP_NUM_THREADS=1 python3 docs/research/zc/hub2_bound.py OUT.json [--min-kin 0.6]
"""
import importlib.util, json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("zc_model", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
M = importlib.util.module_from_spec(spec); sys.modules["zc_model"] = M; spec.loader.exec_module(M); K = M.K


def band(r):
    """max over levels of the share of values within [L - 12, L] (sliding window on the sorted requirements)"""
    r = np.sort(r[np.isfinite(r)]); n = len(r)
    if n == 0: return 0.0, None
    j = np.searchsorted(r, r - 12.0, side="left"); k = np.arange(n) - j + 1; i = int(np.argmax(k))
    return float(k[i]) / n, float(r[i])


def main():
    out = sys.argv[1]; mk = float(sys.argv[sys.argv.index("--min-kin") + 1]) if "--min-kin" in sys.argv else 0.6
    S = [s for s in json.load(open(os.path.join(REPO, "docs", "concepts", "zc", "sobol_kin.json"))) if s["kin"] >= mk]
    B = K.bench(60, 160); F = K.frames(B); rows = []; t = time.time()
    for n, s in enumerate(S):
        p = M.snap(s["params"]); p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
        p2, ok, _ = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
        I = np.nonzero(ok)[0]; row = dict(params=s["params"], kin=s["kin"], kin_over=s["kin_over"], closes60=float(ok.mean()))
        if len(I) >= 3:
            for name, ax in (("hub1", p1), ("hub2", p2), ("hub3", p3)):
                R = K.requirement(B, I, K.unit(ax[I])); R = np.where(np.isfinite(R) & (R < 399), R, np.nan)
                b, L = band(R); row[name] = dict(band=round(b, 3), level=L, p10=float(np.nanpercentile(R, 10)) if np.isfinite(R).any() else None,
                                                   p90=float(np.nanpercentile(R, 90)) if np.isfinite(R).any() else None, none=float(np.isnan(R).mean()))
        rows.append(row)
        if n % 200 == 0:
            json.dump(rows, open(out, "w")); print(n, len(S), round(time.time() - t), flush=True)
    json.dump(rows, open(out, "w"))


if __name__ == "__main__":
    main()
