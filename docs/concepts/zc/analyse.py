"""Merge the zc-frontier-3r global sweep (docs/concepts/zc/sweep/out_*.json) and CMA runs (docs/concepts/zc/cma/*.json),
print the frontier (best gap, reach at in-band >= 0.88 / 0.85 / 0.80), the distinct basins and the per-region bests.

    python3 docs/concepts/zc/analyse.py [--basins 8] [--json docs/concepts/zc/summary.json]
"""
import glob, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load(pattern):
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, pattern))):
        try:
            for r in json.load(open(f)):
                r["_src"] = os.path.basename(f); rows.append(r)
        except Exception as e:                                            # noqa: BLE001
            print("skip", f, e)
    return rows


def dist(p, q):
    """distance between two configs in scaled parameter units (directions by angle)"""
    import math
    def b(az, el): az, el = math.radians(az), math.radians(el); return np.array([-math.cos(el) * math.cos(az), math.sin(el), math.cos(el) * math.sin(az)])
    def w(d, a): d, a = math.radians(d), math.radians(a); return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])
    ang = lambda x, y: math.degrees(math.acos(max(-1, min(1, float(x @ y)))))
    return max(ang(b(p["az"], p["el"]), b(q["az"], q["el"])) / 10, ang(w(p["wd"], p["wa"]), w(q["wd"], q["wa"])) / 10,
               abs(p["a1"] - q["a1"]) / 8, abs(p["a2"] - q["a2"]) / 8, 9 * (p["sigma"] != q["sigma"]), 9 * (p["inv2"] != q["inv2"]),
               9 * (p["inv3"] != q["inv3"]))


def main():
    nb = int(sys.argv[sys.argv.index("--basins") + 1]) if "--basins" in sys.argv else 8
    sw = load("sweep/out_*.json"); cm = load("cma/*.json"); allr = sw + cm
    ok = [r for r in allr if r.get("honest") and r.get("gap", 999) < 200]
    print(f"rows: sweep {len(sw)}, cma {len(cm)}, honest {len(ok)}; prescreened out {sum(1 for r in allr if r.get('gap') == 300.0)}; "
          f"seat-rejected {sum(1 for r in allr if r.get('gap') == 200.0)}; errors {sum(1 for r in allr if r.get('error'))}")
    if not ok: return
    ok.sort(key=lambda r: r["gap"])
    out = dict(n_sweep=len(sw), n_cma=len(cm), n_honest=len(ok))
    for lab, rows in (("sweep", [r for r in ok if r in sw]), ("all", ok)):
        if not rows: continue
        g = np.array([r["gap"] for r in rows]); rc = np.array([r["reach"] for r in rows]); ib = np.array([r["inband14"] for r in rows])
        fr = {}
        for t in (0.90, 0.88, 0.85, 0.80, 0.70):
            m = ib >= t; fr[str(t)] = round(float(rc[m].max()), 4) if m.any() else None
        out[lab] = dict(best_gap=float(g.min()), p1=float(np.percentile(g, 1)), frontier_reach_at_inband=fr,
                        top=[dict(gap=r["gap"], near=r.get("near"), reach=r["reach"], follow=r["follow"], inband14=r["inband14"],
                                  contact=r["contact"], params={k: r["params"][k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "inv2", "inv3", "q", "end_extra")},
                                  member=r.get("inband_member"), tag=r.get("tag"), src=r["_src"]) for r in rows[:5]])
        print(f"[{lab}] best {g.min():.2f}; reach at in-band >= t: {fr}")
    basins = []
    for r in ok:
        if all(dist(r["params"], b["params"]) > 1.0 for b in basins): basins.append(r)
        if len(basins) >= nb: break
    out["basins"] = [dict(gap=b["gap"], near=b.get("near"), reach=b["reach"], follow=b["follow"], inband14=b["inband14"], contact=b["contact"],
                          params={k: b["params"][k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "inv2", "inv3", "q", "end_extra")},
                          member=b.get("inband_member"), src=b["_src"]) for b in basins]
    for b in out["basins"]:
        p = b["params"]
        print(f"  {b['gap']:7.2f} near {b['near']} reach {b['reach']:.3f} fol {b['follow']:.3f} ib {b['inband14']:.3f} ct {b['contact']:.3f} | "
              f"J1 ({p['az']:.0f},{p['el']:.0f}) a {p['a1']:.0f}/{p['a2']:.0f} J3 ({p['wd']:.0f},{p['wa']:.0f}) s{p['sigma']} inv{p['inv2']}{p['inv3']} | {b['member']}")
    if "--json" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
