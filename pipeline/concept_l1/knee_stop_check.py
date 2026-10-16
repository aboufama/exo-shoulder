"""Knee-stop and E-strap check of a minarc L1 built with --knee-stop / --e-cap (build_minarc_l1.py, gen 4b).

The knee link (member 6) turns about pin a relative to member 3 (E strap + E boss). This poses the BUILT knee-link parts
(knee link, knee stop tooth, knee stop web: exo.glb group l4, member-local) relative to the built member-3 parts (E strap,
E boss: group l3) at knee angles across the model's range and past the stop, and reports the signed clearance (libigl,
negative = overlap) of every pair. Knee angle = the model's (pin a -> J3 vs pin a -> pin b; 180 = straight); the pose of the
knee about pin a is the rotation the builder uses (build_minarc_l1.knee_stop_geom), checked there against the model's own
member transforms to 0.0 deg.

    CB_FOLD_MARGIN=5.5 python3 pipeline/concept_l1/knee_stop_check.py <l1 design id> --params-file F --a1max A
"""
import argparse, json, math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_minarc_l1 as BM                                                    # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--params-file"); ap.add_argument("--params"); ap.add_argument("--a1max", type=float)
    a = ap.parse_args(); import igl
    dd = os.path.join(BM.FULL, "designs", a.design); des = json.load(open(os.path.join(dd, "design.json")))
    ks = des["build_fixes"]["knee_stop_deg"]
    P0, _ = BM.params_from(a); M, _ = BM.fit(P0); D = M.D; fr = M.fr; sn = D.sn; eE = fr["eE"]
    sang = lambda x, y: math.atan2(float(sn @ np.cross(x, y)), float(x @ y))
    rot = lambda t, V: V * math.cos(t) + np.cross(sn, V) * math.sin(t) + np.outer(V @ sn, sn) * (1 - math.cos(t))
    alpha_h = sang(-eE, fr["eK"])
    side = float(np.sign(alpha_h))
    src = trimesh.load(os.path.join(dd, "exo.glb")); parts = {}
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g not in ("l3", "l4"): continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        for key in ("knee link", "knee stop tooth", "knee stop web", "E strap", "E boss"):
            if n.startswith(key): parts[key] = m
    knee = {k: v for k, v in parts.items() if k.startswith("knee")}; m3 = {k: v for k, v in parts.items() if k.startswith("E ")}
    dense = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 6000, seed=4)[0]]
    angs = sorted(set([95.0, 110.0, 125.0, 135.0, 140.0, 143.6, 145.0, 147.0, 148.5, 149.0, 149.4, ks, 149.6, 150.0, 151.0, 153.0]))
    rows = []
    for ang in angs:
        beta = side * math.radians(ang); out = dict(knee_angle=ang)
        for kn, km in knee.items():
            X = dense(km); X3 = fr["A0"] + rot(beta - alpha_h, X - fr["A0m"])   # knee-local -> member-3 home at this knee angle
            for mn, mm in m3.items():
                sd = igl.signed_distance(np.ascontiguousarray(X3, float), np.ascontiguousarray(mm.vertices, float), np.ascontiguousarray(mm.faces, np.int64))[0]
                out[f"{kn} vs {mn}"] = round(float(sd.min()), 4)
        rows.append(out)
        print(json.dumps(out), flush=True)
    below = [r for r in rows if r["knee_angle"] < ks - 1e-6]
    res = dict(design=a.design, knee_stop_deg=ks, rows=rows,
               min_clear_below_stop=min(min(v for k, v in r.items() if k != "knee_angle") for r in below),
               tooth_vs_strap_at_stop=next(r["knee stop tooth vs E strap"] for r in rows if abs(r["knee_angle"] - ks) < 1e-6),
               knee_link_vs_E_strap_min_over_range=min(r["knee link vs E strap"] for r in below),
               note="signed clearance (mm, negative = overlap) of the built knee-side parts vs the built member-3 parts, the knee turned about pin a")
    json.dump(res, open(os.path.join(dd, "knee_stop_check.json"), "w"), indent=1)
    print({k: v for k, v in res.items() if k != "rows"})


if __name__ == "__main__":
    main()
