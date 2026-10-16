#!/usr/bin/env python3
"""Hub-1 band map of a scapula-fixed GH-ray hub (companion of tools/fold_frontier.py).

A hub whose axis is a GH ray (J1 and J2 of offset-skin-normal-3r: the 2-slide closure theorem; J1 of every spherical
3R) is a 20 mm disc on that ray, at ONE height for all poses. Per pose, the height it needs is where every line of the
disc (axis + 4 rim lines at 10 mm) is >= 2 mm off the skin; the deltoid / arm moving under a scapula-fixed hub makes
that height vary. A hub at height F is in band (2-14 mm) in the poses whose need lies in [F - 12, F] and is in the skin
in those above F. This scans J1 = bvec(az, el) on fold_frontier's grid (az 6 deg, el 16-88 / 4) against the 220 poses
of Bench(60,160) (fast grid; radii 20-200 mm every 2 mm) and reports per direction: the rest-pose need, the spread of
the need (p50 / p90 / max lift above rest), the BEST 12 mm window share (the most poses a single hub height keeps in
band) and the share kept at F = max need (no pose given up). Writes docs/research/fold/rayblock.json and joins it to
frontier.json rows (fold-free share next to hub-1 band share).

    OMP_NUM_THREADS=1 python3 tools/fold_rayblock.py
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_bench as CB, concept_kit as K

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    t0 = time.time(); B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); RS = Z["RS"][B.idx].astype(float)
    H1 = [(az, el) for az in range(-180, 180, 6) for el in range(16, 91, 4)]
    u1 = np.array([K.bvec(az, el) for az, el in H1]); r = np.arange(30.0, 121.0, 2.0)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    e1 = np.cross(u1, [0.0, 0.0, 1.0]); e1 /= np.linalg.norm(e1, axis=1, keepdims=True); e2 = np.cross(u1, e1)
    off = np.stack([np.zeros_like(u1), 10 * e1, -10 * e1, 10 * e2, -10 * e2], 1)              # (dirs, 5 lines, 3)
    r = np.arange(20.0, 201.0, 2.0); need = np.zeros((len(H1), len(B.idx)))
    for i in range(len(B.idx)):
        P = (off[:, :, None, :] + u1[:, None, None, :] * r[None, None, :, None]) @ RS[i].T      # (dirs, 5, radii, 3) world
        d = B.dist(i, P.reshape(-1, 3)).reshape(len(H1), 5, len(r))
        bad = d < 2.0; last = np.where(bad.any(2), len(r) - 1 - np.argmax(bad[:, :, ::-1], 2), -1)  # last radius index too close
        nd = np.where(last >= len(r) - 1, 999.0, r[np.clip(last + 1, 0, len(r) - 1)])
        need[:, i] = nd.max(1)
    rest = int(np.argmin(el)); over = el >= 120
    def window(nd):
        v = np.sort(nd[nd < 900]);
        if not len(v): return 0.0, None
        j = np.searchsorted(v, v + 12.0, side="right"); k = int(np.argmax(j - np.arange(len(v))))
        return float((j[k] - k) / len(nd)), float(v[min(j[k], len(v)) - 1])
    stats = []
    for k in range(len(H1)):
        nd = need[k]; w, F = window(nd); ok = nd < 900; mx = nd[ok].max() if ok.any() else 999.0
        stats.append(dict(rest=float(nd[rest]), lift_p50=float(np.median(nd[ok]) - nd[rest]) if ok.any() else None,
                          lift_p90=float(np.percentile(nd[ok], 90) - nd[rest]) if ok.any() else None, lift_max=float(mx - nd[rest]),
                          blocked=int((~ok).sum()), window12=round(w, 4), window12_overhead=round(float(((nd[over] <= F) & (nd[over] >= F - 12)).mean()), 4) if F else 0.0,
                          at_max=round(float((nd >= mx - 12).mean()), 4)))
    free_all = np.array([s_["window12"] for s_ in stats]); free_over = np.array([s_["window12_overhead"] for s_ in stats]); free_ws = np.array([s_["at_max"] for s_ in stats])
    F = json.load(open(os.path.join(REPO, "docs", "research", "fold", "frontier.json")))
    key = {h: k for k, h in enumerate(H1)}
    for row in F["rows"]:
        k = key.get((row["az1"], row["el1"]))
        if k is not None:
            row["j1_ray_free"] = round(float(free_all[k]), 4); row["j1_ray_free_overhead"] = round(float(free_over[k]), 4); row["j1_lift_p90"] = round(stats[k]["lift_p90"] or 999, 1)
    out = dict(note=__doc__.split("\n\n")[1], n_poses=len(B.idx), n_overhead=int(over.sum()),
               grid=[dict(az=a, el=e, **{k_: (round(v, 2) if isinstance(v, float) else v) for k_, v in stats[k].items()}) for k, (a, e) in enumerate(H1)],
               frontier_rows=[{k: v for k, v in row.items() if k in ("a1", "a2", "az1", "el1", "wd", "wa", "ws_share", "clip_share", "j1_ray_free", "j1_ray_free_overhead", "j1_lift_p90")} for row in F["rows"]])
    json.dump(out, open(os.path.join(REPO, "docs", "research", "fold", "rayblock.json"), "w"), indent=1)
    print(f"{len(H1)} J1 directions x {len(B.idx)} poses in {time.time() - t0:.0f} s -> docs/research/fold/rayblock.json")
    for az, e in ((95.9, 65.2), (132, 16), (138, 16), (108, 20), (108, 32), (126, 32), (120, 28), (114, 24), (126, 52), (-48, 20), (-180, 16)):
        k = int(np.argmin([(a - az) ** 2 + (b - e) ** 2 for a, b in H1]))
        st_ = stats[k]; print(f"J1 bvec({H1[k][0]:4d}, {H1[k][1]:2d}): rest need {st_['rest']:.0f} mm, lift p50 {st_['lift_p50']:.1f} p90 {st_['lift_p90']:.1f} max {st_['lift_max']:.1f}, blocked {st_['blocked']}; best 12 mm window keeps {free_all[k]:.3f} (overhead {free_over[k]:.3f}); at F = max need {free_ws[k]:.3f}")
    rows = [r_ for r_ in F["rows"] if "j1_ray_free" in r_ and 85 <= r_["a1"] + r_["a2"] <= 130]
    both = sorted(rows, key=lambda r_: -min(r_["ws_share"], r_["j1_ray_free"]))[:8]
    print("frontier rows (a1+a2 85-130) best on min(fold-free ws share, hub-1 band share):")
    for r_ in both:
        print(f"  a {r_['a1']}/{r_['a2']} J1 bvec({r_['az1']}, {r_['el1']}) J3 wdir({r_['wd']}, {r_['wa']}): fold-free ws {r_['ws_share']} | hub-1 band (12 mm window) {r_['j1_ray_free']} overhead {r_['j1_ray_free_overhead']} lift p90 {r_['j1_lift_p90']}")
    for thr in (0.95, 0.9, 0.8):
        good = free_all >= thr
        print(f"J1 directions whose best 12 mm window keeps >= {thr:.0%} of poses: {int(good.sum())} / {len(H1)}")


if __name__ == "__main__":
    main()
