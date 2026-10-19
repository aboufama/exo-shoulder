"""Red team of the built L1 CAD of offset-skin-normal-3r (pipeline/full-exo/designs/<id>): the point that pinches and
the pose that jams, measured on the BUILT meshes (exo.glb posed by clips.json / workspace.json frames, exact posed skin):

  * per part: the lowest skin distance over every followed clip frame (step), with the frame; the share of frames where
    the part is < 1 mm and < 2 mm from the skin;
  * the inverted along rail's overhanging ENDS (the 6 mm at each end beyond the block's travel envelope) and the across
    rail's ends, separately; the arm-fixed cuff stack (base plate, along block, mount) separately;
  * the verifier's near-touch pose (Bench(110,360): arm-fixed block 0.64 mm at plane -75, elev 45, axial 120) and its
    neighbours, posed through the design's own chain (closes? which part is lowest?);
  * adjacent pairs that share a joint (link 1 / link 2 at J2, link 2 / J3 plate + member 3, member 3 / member 4 /
    arm-fixed stage): min clearance over the followed frames (mesh vertex samples vs the other mesh, exact);
  * held frames by reason (the pose that jams), from build.json.

    OMP_NUM_THREADS=1 python3 pipeline/concept_l1/redteam_osn_l1.py <id> [--step 3] [--jobs 4] -> <dd>/redteam.json
"""
import argparse, json, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
import concept_bench as CB, scene_export as SE                                   # noqa: E402
BP = CB.BP


def load(dd):
    src = trimesh.load(os.path.join(dd, "exo.glb")); parts = []
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g == "F" or (g == "H" and "(proxy)" not in n): continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        X = np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 600, seed=2)[0]]
        parts.append((g, n, m, X))
    return parts


def rail_ends(parts):
    """sample subsets: the along rail's outer 6 mm at each end, the across rail's outer 6 mm (in their own group frame)"""
    out = {}
    for g, n, m, X in parts:
        if "rail (RSR3M" in n:
            ax = np.linalg.svd(np.asarray(m.vertices) - np.asarray(m.vertices).mean(0))[2][0]; c = np.asarray(m.vertices).mean(0)
            t = (X - c) @ ax; L = np.ptp(t); out[n.split(" (")[0] + " ends (outer 6 mm)"] = (g, X[np.abs(t) > L / 2 - 6.0])
    return out


def pose_eval(item):
    fr, parts, extra = item
    X, pose = SE.frame_xforms(fr); ex = CB._Exact(BP.posed(pose)); res = {}
    allp = [(g, n, Xs) for g, n, m, Xs in parts] + [(g, n, Xs) for n, (g, Xs) in extra.items()]
    W = [Xs @ np.asarray(X[g][0]).T + X[g][1] for g, n, Xs in allp]; d = ex(np.concatenate(W)); cut = np.cumsum([0] + [len(w) for w in W])
    for k, (g, n, Xs) in enumerate(allp): res[n] = float(d[cut[k]:cut[k + 1]].min())
    return res


def adjacent(fr, parts, pairs):
    """min distance (mm; < 0 never reported: vertex-to-surface only, positive) between the posed meshes of the given pairs"""
    import igl
    X, _ = SE.frame_xforms(fr); posed = {}
    for g, n, m, Xs in parts:
        R, t = X[g]; posed[n] = (np.asarray(m.vertices) @ np.asarray(R).T + t, np.asarray(m.faces), Xs @ np.asarray(R).T + t)
    out = {}
    for a, b in pairs:
        if a not in posed or b not in posed: continue
        Va, Fa, Sa = posed[a]; Vb, Fb, Sb = posed[b]
        d1 = igl.signed_distance(np.ascontiguousarray(Sa), np.ascontiguousarray(Vb), np.ascontiguousarray(Fb, np.int64))[0]
        d2 = igl.signed_distance(np.ascontiguousarray(Sb), np.ascontiguousarray(Va), np.ascontiguousarray(Fa, np.int64))[0]
        out[f"{a[:28]} / {b[:28]}"] = float(min(d1.min(), d2.min()))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("id"); ap.add_argument("--step", type=int, default=3); ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(); t0 = time.time()
    dd = os.path.join(REPO, "pipeline", "full-exo", "designs", a.id); parts = load(dd); extra = rail_ends(parts)
    C = json.load(open(os.path.join(dd, "clips.json"))); items = []; tags = []
    for c in C["clips"]:
        for fi in range(0, len(c["frames"]), a.step):
            fr = c["frames"][fi]
            if fr["held"]: continue
            items.append((fr, parts, extra)); tags.append((c["name"], fi, fr["p"][:3]))
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool: R = pool.map(pose_eval, items, chunksize=4)
    else: R = list(map(pose_eval, items))
    names = list(R[0]); per = {}
    for n in names:
        v = np.array([r[n] for r in R]); k = int(np.argmin(v))
        per[n] = dict(min_mm=round(float(v.min()), 2), at=dict(clip=tags[k][0], frame=tags[k][1], pose=[round(x, 1) for x in tags[k][2]]),
                      share_lt1=round(float((v < 1).mean()), 4), share_lt2=round(float((v < 2).mean()), 4), median_mm=round(float(np.median(v)), 2))
    print(f"{len(items)} followed frames (step {a.step}) in {time.time() - t0:.0f} s")
    for n, v in sorted(per.items(), key=lambda x: x[1]["min_mm"]): print(f"  {v['min_mm']:6.2f} mm  <1mm {v['share_lt1']:.3f}  <2mm {v['share_lt2']:.3f}  {n[:70]:70s} {v['at']}")
    # adjacent pairs over the followed frames
    nm = {n: n for g, n, m, X in parts}
    def find(s): return next((n for n in nm if s in n), None)
    pairs = [(find("link 1 strap"), find("link 2 strap")), (find("link 2 strap"), find("J3 lower plate")), (find("link 2 strap"), find("member-3 neck")),
             (find("link 2 strap"), find("member-3 bridge")), (find("link 1 strap"), find("J2 upper boss")), (find("link 2 strap"), find("J2 lower plate")),
             (find("member-3 bridge"), find("across guide rail")), (find("carriage B"), find("carriage A adapter")), (find("carriage B"), find("across guide rail")),
             (find("along guide rail"), find("along guide block")), (find("carriage A adapter"), find("along guide block")), (find("along guide rail"), find("cuff mount")),
             (find("along guide rail"), find("cuff base plate")), (find("member-3 neck"), find("along guide rail")), (find("link 2 strap"), find("across guide rail")),
             (find("link 2 strap"), find("carriage A adapter")), (find("link 2 strap"), find("along guide rail"))]
    pairs = [p for p in pairs if p[0] and p[1]]; adj = {}
    for (fr, _, _), tg in list(zip(items, tags))[::2]:
        for k, v in adjacent(fr, parts, pairs).items():
            if k not in adj or v < adj[k][0]: adj[k] = (round(v, 3), tg[0], tg[1], [round(x, 1) for x in tg[2]])
    print("adjacent / stage pairs, min mesh distance over the followed frames (every 2nd):")
    for k, v in sorted(adj.items(), key=lambda x: x[1][0]): print(f"  {v[0]:7.3f} mm  {k}  {v[1:]}")
    # the verifier's near-touch pose and neighbours, through the design's own chain
    sys.path.insert(0, HERE); sys.argv = [sys.argv[0]]
    import build_osn_l1 as O
    M, rep, e = O.fit((60, 160), json.load(open(os.path.join(dd, "build.json")))["fit"]["k"])
    near = []
    for pl in (-90, -75, -60):
        for elv in (30, 45, 60):
            for ax in (105, 120, 135): near.append([pl, elv, ax, 0.0, 0.0])
    K = O.chain(M, np.array(near, float)); kin, clear, adjm, _ = O.feasibility(M, K, np.array(near, float), [], skin=False); nt = []
    for j, p in enumerate(near):
        if not (kin[j] and clear[j] >= 1.0 and adjm[j] >= O.ADJ): nt.append(dict(pose=p[:3], closes=bool(kin[j]), clear=None if np.isnan(clear[j]) else round(float(clear[j]), 2))); continue
        fr = O.REF.frame_dict(K, j, p, p, False); r = pose_eval((fr, parts, extra)); k = min(r, key=r.get)
        nt.append(dict(pose=p[:3], closes=True, lowest_part=k[:60], lowest_mm=round(r[k], 2),
                       arm_fixed_mm=round(min(v for n_, v in r.items() if "(proxy)" in n_), 2)))
    print("verifier near-touch neighbourhood:"); [print("  ", x) for x in nt]
    B = json.load(open(os.path.join(dd, "build.json"))); held = {c: v["reasons"] for c, v in B.get("clips", {}).items()}
    json.dump(dict(id=a.id, step=a.step, frames=len(items), per_part=per, adjacent=adj, near_touch_neighbourhood=nt, held_reasons=held,
                   secs=round(time.time() - t0, 1)), open(os.path.join(dd, "redteam.json"), "w"), indent=1, default=float)
    print(f"done {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
