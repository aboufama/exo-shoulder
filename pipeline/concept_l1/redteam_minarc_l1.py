"""Red team of the built L1 CAD of minarc-stop-knuckle-4r BDp (pipeline/full-exo/designs/<id>, build_minarc_l1.py), measured on
the BUILT meshes (exo.glb) against the exact posed skin:

  * the hub-2 pinch (the verifiers' known weak spot: hub 2's wall 0.05 mm from the skin at the overhead raise peak, plane 30,
    elev 150, axial -60, state A): every built part's lowest skin distance at that pose and its neighbourhood (plane +-15,
    elev +-15, axial +-30), posed by the design's own chain (build_minarc_l1.chain = the verified model's kinematics), and along
    the followed frames of the Raise overhead clip (clips.json = the judges' path); the lift of hub 2 that would clear 1 mm;
  * the stops: the dowel hand calc (build.json dowel_check), the dowels inside their slots over every followed clip frame and
    every eval-feasible workspace pose (joint angle from the frames vs the slot window);
  * held frames by reason (the pose that jams), from build.json.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/redteam_minarc_l1.py [l1_minarc-bdp] -> <dd>/redteam.json
"""
import json, math, os, sys, time
import numpy as np, trimesh
from scipy.spatial.transform import Rotation as Rot
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_minarc_l1 as BM                                                    # noqa: E402
CB = BM.CB; BP = CB.BP; import scene_export as SE                               # noqa: E402
KEYS = ("plane", "elev", "axial", "flex", "pron")


def load(dd):
    own = {(p["group"], p["name"]): p["material"] != "user part" for p in json.load(open(os.path.join(dd, "parts_full.json")))["parts"]}
    src = trimesh.load(os.path.join(dd, "exo.glb")); parts = []
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if not own.get((g, n), False): continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        parts.append((g, n, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 1500, seed=2)[0]]))
    return parts


def per_part(parts, fr):
    X, pose = SE.frame_xforms(fr); ex = CB._Exact(BP.posed(pose)); out = {}
    for g, n, P in parts:
        R, t = X[g]; out[n] = float(ex(P @ np.asarray(R).T + t).min())
    return out


def main():
    did = sys.argv[1] if len(sys.argv) > 1 else "l1_minarc-bdp"; dd = os.path.join(BM.FULL, "designs", did); t0 = time.time()
    parts = load(dd); b = json.load(open(os.path.join(dd, "build.json"))); C = json.load(open(os.path.join(dd, "clips.json")))
    P0 = b["fit"]["params"]; M, rep = BM.fit(P0); out = dict(design=did)
    # 1. the hub-2 pinch at the overhead raise peak and its neighbourhood, through the design's chain
    B = M.B; i5 = min(range(len(B.idx)), key=lambda i: abs(B.poses[i]["plane"] - 30) + abs(B.poses[i]["elev"] - 150) + abs(B.poses[i]["axial"] + 60))
    base = [B.poses[i5][k] for k in KEYS]; grid = []
    for dp in (-15, 0, 15):
        for de in (-15, 0, 15):
            for da in (-30, 0, 30):
                grid.append([base[0] + dp, base[1] + de, base[2] + da, base[3], base[4]])
    grid = np.array(grid, float); K = BM.chain(M, grid); rows = []
    for j in range(len(grid)):
        ok = bool(K["ok"][j] and K["kok"][j] and K["res"][j] < 0.5)
        if not ok: rows.append(dict(pose=grid[j, :3].tolist(), closes=False)); continue
        fr = BM.frame_dict(K, j, grid[j], grid[j], False); d = per_part(parts, fr); lo = min(d, key=d.get)
        hub2 = {k: round(v, 3) for k, v in d.items() if k.startswith(("J2 ", "J2 stop"))}
        rows.append(dict(pose=grid[j, :3].tolist(), closes=True, state=int(K["state"][j]), lowest_part=lo[:40], lowest_mm=round(d[lo], 3), hub2_mm=hub2,
                         under_1mm=sorted(k[:40] for k, v in d.items() if v < 1.0)))
    out["overhead_peak_neighbourhood"] = dict(centre=base, poses=rows)
    pk = next(r for r in rows if r["pose"] == grid[13, :3].tolist())
    print(f"overhead peak {base[:3]}: {pk}", flush=True)
    # 2. Raise overhead clip, every followed frame (the judges' path)
    clip = next(c for c in C["clips"] if c["name"].startswith("Raise overhead")); lows = {}
    for fi, fr in enumerate(clip["frames"]):
        if fr["held"]: continue
        for n, v in per_part(parts, fr).items():
            if n not in lows or v < lows[n][0]: lows[n] = (v, fi, fr["p"][:3])
    out["raise_overhead_clip"] = {n[:48]: dict(min_mm=round(v, 3), frame=fi, pose=[round(x, 1) for x in p]) for n, (v, fi, p) in sorted(lows.items(), key=lambda x: x[1][0])}
    for n, v in list(out["raise_overhead_clip"].items())[:6]: print(f"  Raise overhead: {v['min_mm']:7.3f} mm  {n}  frame {v['frame']} {v['pose']}", flush=True)
    h2 = min(v["min_mm"] for n, v in out["raise_overhead_clip"].items() if n.startswith("J2 "))
    out["hub2_lift_to_clear_1mm"] = round(max(0.0, 1.0 - min(h2, min(r.get("hub2_mm", {}).get(k, 9) for r in rows if r.get("closes") for k in r["hub2_mm"]))), 3)
    # 3. the dowels in their slots over every followed clip frame and eval-feasible workspace pose
    st = b["stack"]["stops"]; W = json.load(open(os.path.join(dd, "workspace.json"))); rng = {"K": [9, -9], "J2": [999, -999]}; bad = {"K": 0, "J2": 0}; n = 0
    for f in [fr for c in C["clips"] for fr in c["frames"] if not fr["held"]] + [p for p in W["poses"] if p["eval_feasible"]]:
        G = {g: np.array(v).reshape(3, 3) for g, v in f["G"].items()}
        dK = float(np.degrees(Rot.from_matrix(G["l1a"].T @ G["l1b"]).as_rotvec() @ M.D.uK)); q2 = float(np.degrees(Rot.from_matrix(G["l1b"].T @ G["l2"]).as_rotvec() @ M.D.u[1]))
        n += 1
        for key, a in (("K", dK), ("J2", q2)):
            lo, hi = (st["K"]["stop_B_deg"], 0.0) if key == "K" else tuple(st["J2"]["window_deg"]); lo, hi = min(lo, hi), max(lo, hi)
            rng[key] = [min(rng[key][0], a), max(rng[key][1], a)]
            if a < lo - 0.05 or a > hi + 0.05: bad[key] += 1
    out["stops_in_slot"] = dict(frames_and_poses=n, K_range_deg=[round(x, 3) for x in rng["K"]], J2_range_deg=[round(x, 3) for x in rng["J2"]], outside=bad,
                                K_slot=[st["K"]["stop_B_deg"], 0.0], J2_slot=st["J2"]["window_deg"])
    print(f"stops: {out['stops_in_slot']}", flush=True)
    out["dowel_check"] = b.get("dowel_check"); out["held"] = {k: v.get("reasons") for k, v in b.get("clips", {}).items()}
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(dd, "redteam.json"), "w"), indent=1, default=float)
    print(f"done {out['secs']} s -> {dd}/redteam.json")


if __name__ == "__main__":
    main()
