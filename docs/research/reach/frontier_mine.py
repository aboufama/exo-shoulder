"""Reach vs in-band frontier mined from every sweep / CMA history (docs/concepts/sweeps/*.json, Bench(60,160) fast unless a
row says otherwise): per morphology, the best reach at in-band14 >= 0.88 / 0.90 with follow >= 0.95 and contact <= 0.02,
and the unconstrained reach maximum (no proximity bar). Writes docs/research/reach/frontier_mined.json.

    python3 docs/research/reach/frontier_mine.py
"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# topology class per sweep file (docs/concepts/catalogue.json families; 'passive' = what closes the chain besides 3 active R)
CLASS = {
    "fold-sph3r": "plain 3R (0 passive)", "spine-parked-j2-3r": "plain 3R (0 passive)", "raglan-routed-3r": "plain 3R (0 passive)",
    "far-end-posterior-3r": "plain 3R (0 passive)", "crown-ring-3r": "plain 3R (0 passive)", "annular-ring-3r": "plain 3R (0 passive)",
    "skin-normal-3r-pin-knee": "3R + passive planar closure (0 transl.)", "raglan-knee-3r": "3R + passive planar closure (0 transl.)",
    "skin-normal-3r-knuckle-cufflink": "3R + passive planar closure (0 transl.)",
    "offset-skin-normal-3r": "3R + 2 cuff slides", "seed-offset-3r-slides": "3R + 2 cuff slides",
    "skin-normal-hubs-selfaligning": "3R + 2 cuff slides", "offset-axis-skin-hubs": "3R + 2 cuff slides",
    "acromial-rocker-3r": "3R + rocker / relay", "j2-arc-sector-3r": "3R + J2 arc sector (coupled)",
    "dwell-fourbar-knee-3r": "3R + coupled schedule (dwell four-bar)", "closure-set-arc-knee-3r": "3R + coupled schedule (arc knee)",
    "virtual-pole-4bar-j1": "3R with a four-bar virtual pole", "virtual-pole-4bar-j2": "3R with a four-bar virtual pole",
    "scapular-race-j2-carriage": "3R with J2 on a race carriage", "rail-elbow": "3R with a rail elbow (1 transl.)",
    "twin-rail-one-hub": "rails", "crossed-skin-tracks": "rails", "seed-arc-rails": "rails", "meridian-goniometer": "rails",
    "clavicular-front-route": "plain 3R (0 passive)", "risley-turret": "turret / SPM", "coaxial-rus-turret": "turret / SPM",
    "foldfree-rus-truss": "turret / SPM", "seed-spm-3rrr": "turret / SPM",
    "4R-lens:es_park4_a": "redundant 4R (spring-centred 4th, lens, unverified)", "4R-lens:es_park4_b": "redundant 4R (spring-centred 4th, lens, unverified)",
    "4R-lens:es_park4_c": "redundant 4R (spring-centred 4th, lens, unverified)", "4R-lens:es_park1": "redundant 4R (spring-centred 4th, lens, unverified)",
    "4R-lens:es_ring": "redundant 4R (ring 4th, lens, unverified)",
}


def num(r, k):
    v = r.get(k)
    if v is None and isinstance(r.get("report"), dict): v = r["report"].get(k)
    try: return float(v)
    except (TypeError, ValueError): return None


def main():
    out = {}
    extra = [a for a in sys.argv[1:] if a.endswith(".json")]     # other histories (e.g. a lens agent's es_*.json: rows with p / reach / inband14)
    for f in sorted(glob.glob(os.path.join(REPO, "docs", "concepts", "sweeps", "*.json"))) + extra:
        mid = os.path.basename(f)[:-5] if f not in extra else "4R-lens:" + os.path.basename(f)[:-5]
        if mid.startswith("_"): continue
        try: d = json.load(open(f))
        except Exception: continue
        if not isinstance(d, list): continue
        rows = []
        for r in d:
            if not isinstance(r, dict): continue
            rc, ib, fo, ct = num(r, "reach"), num(r, "inband14"), num(r, "follow"), num(r, "contact")
            if rc is None or ib is None: continue
            if r.get("honest") is False: continue
            rows.append(dict(reach=rc, ib14=ib, follow=fo if fo is not None else 0.0, contact=ct if ct is not None else 1.0,
                             gap=num(r, "gap"), k=r.get("k"), stage=r.get("stage"), params=r.get("params", r.get("p"))))
        if not rows: continue
        ok = lambda r, t: r["ib14"] >= t and r["follow"] >= 0.95 and r["contact"] <= 0.02
        best = lambda t: max((r for r in rows if ok(r, t)), key=lambda r: r["reach"], default=None)
        b88, b90 = best(0.88), best(0.90); top = max(rows, key=lambda r: r["reach"])
        gbest = min((r for r in rows if r["gap"] is not None), key=lambda r: r["gap"], default=None)
        sl = lambda r: None if r is None else dict(reach=r["reach"], ib14=r["ib14"], follow=r["follow"], contact=r["contact"], gap=r["gap"], k=r["k"], params=r["params"])
        # Pareto frontier reach vs in-band (follow >= .95, contact <= .02)
        F = sorted((r for r in rows if r["follow"] >= 0.95 and r["contact"] <= 0.02), key=lambda r: -r["ib14"]); par = []; mr = -1
        for r in F:
            if r["reach"] > mr + 1e-9: par.append([round(r["ib14"], 4), round(r["reach"], 4)]); mr = r["reach"]
        at = {}
        for t in (0.80, 0.84, 0.86, 0.88, 0.90):
            c = [r for r in rows if r["ib14"] >= t and r["follow"] >= 0.95]
            b = max(c, key=lambda r: r["reach"], default=None)
            at[f"{t:.2f}"] = None if b is None else [round(b["reach"], 4), round(b["ib14"], 4), round(b["contact"], 4), b["gap"]]
        out[mid] = dict(cls=CLASS.get(mid, "other"), n=len(rows), reach_max_any=sl(top), reach_at_ib88=sl(b88), reach_at_ib90=sl(b90),
                        best_gap=sl(gbest), pareto_ib14_reach=par, reach_at_ib_follow95=at)
    json.dump(out, open(os.path.join(HERE, "frontier_mined.json"), "w"), indent=1, default=float)
    print(f"{'model':36s} {'class':42s} {'n':>6s} {'reachmax':>8s} {'r@.88':>6s} {'r@.90':>6s} {'bestgap':>8s}")
    for k, v in sorted(out.items(), key=lambda kv: kv[1]["cls"]):
        g = lambda x, f: "-" if x is None else f"{x[f]:.3f}"
        print(f"{k:36s} {v['cls']:42s} {v['n']:6d} {g(v['reach_max_any'], 'reach'):>8s} {g(v['reach_at_ib88'], 'reach'):>6s} "
              f"{g(v['reach_at_ib90'], 'reach'):>6s} {'-' if v['best_gap'] is None else v['best_gap']['gap']:>8}")


if __name__ == "__main__":
    main()
