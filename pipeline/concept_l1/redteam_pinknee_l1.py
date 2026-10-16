"""Red team of the built L1 CAD of skin-normal-3r-pin-knee (pipeline/full-exo/designs/<id>, build_pinknee_l1.py): the
point that pinches and the pose that jams, measured on the BUILT meshes (exo.glb posed by the clips.json frames = the
judges' path, exact posed skin):

  * per part: the lowest skin distance over every followed clip frame (step), with the frame; the share of frames where
    the part is < 1 mm and < 2 mm from the skin; the body region under that lowest point (trunk / upper arm / forearm by
    the rig's skin weights) and whether it is the POSTERIOR AXILLARY FOLD (trunk skin within 30 mm of the upper-arm
    region, behind the coronal plane through GH and below it; anterior = where elbow flexion takes the forearm);
  * the posterior axillary fold itself: per part, the lowest distance to that skin patch over the followed frames;
  * the knee near hub 3: min mesh distance (exact, both ways) of the knee link to hub 3's link-2 half, to the E strap, to
    link 2, and of the E strap / E boss / arm pad / pad mount to their neighbours, over the followed frames;
  * the verifier's near-touch neighbourhood (Bench(110,360): 0.02 mm at the arm-at-side poses, plane -15 / 75, elevation 0)
    posed through the design's own chain (closes? knee in its window? which built part is lowest?);
  * held frames by reason (the pose that jams), from build.json.

    OMP_NUM_THREADS=1 python3 pipeline/concept_l1/redteam_pinknee_l1.py <id> [--step 3] [--jobs 1] -> <dd>/redteam.json
"""
import argparse, json, os, sys, time
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo")); sys.path.insert(0, os.path.join(REPO, "judge"))
import concept_bench as CB, scene_export as SE                                   # noqa: E402
import body_regions as BR                                                       # noqa: E402
BP = BPJ = CB.BP                                                                # pipeline/avg/body_pose.py (the judges' rig)
POSE_KEYS = ("plane", "elev", "axial", "flex", "pron")


def load(dd):
    own = {(p["group"], p["name"]): p["material"] != "user part" for p in json.load(open(os.path.join(dd, "parts_full.json")))["parts"]}
    src = trimesh.load(os.path.join(dd, "exo.glb")); parts = []
    for node in src.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if not own.get((g, n), False): continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        X = np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 800, seed=2)[0]]
        parts.append((g, n, m, X))
    return parts


def fold_patch():
    """rest-pose skin vertex ids of the posterior axillary fold, + region per vertex"""
    sk = BPJ._rig().skin; W = np.zeros((sk["n"], 5)); np.add.at(W, (np.repeat(np.arange(sk["n"]), 4), sk["wi"].ravel()), sk["ww"].ravel())
    reg = BR.vertex_regions(W)
    rest = dict(plane=0.0, elev=0.0, axial=0.0, flex=0.0, pron=0.0)
    V0 = np.asarray(BP.posed(rest)); V9 = np.asarray(BP.posed(dict(rest, flex=90.0)))
    up = np.array([0.0, 1.0, 0.0]); fa = reg == 2
    ant = (V9[fa] - V0[fa]).mean(0); ant -= (ant @ up) * up; ant /= np.linalg.norm(ant)
    trunk, arm = np.nonzero(reg == 0)[0], np.nonzero(reg == 1)[0]
    d, _ = cKDTree(V0[arm]).query(V0[trunk]); junction = trunk[d < 30.0]
    post = junction[(V0[junction] @ ant < 0) & (V0[junction] @ up < -10.0)]
    return post, reg, ant


def pose_eval(item):
    fr, parts, patch, reg = item
    X, pose = SE.frame_xforms(fr); V = np.asarray(BP.posed(pose)); ex = CB._Exact(V); res = {}; low = {}
    W = [Xs @ np.asarray(X[g][0]).T + X[g][1] for g, n, m, Xs in parts]; d = ex(np.concatenate(W)); cut = np.cumsum([0] + [len(w) for w in W])
    tP = cKDTree(V[patch]); tV = cKDTree(V)
    for k, (g, n, m, Xs) in enumerate(parts):
        dk = d[cut[k]:cut[k + 1]]; j = int(np.argmin(dk)); vi = int(tV.query(W[k][j])[1])
        res[n] = float(dk.min()); low[n] = (BR.REGIONS[reg[vi]], bool(vi in set(patch.tolist())), float(tP.query(W[k])[0].min()))
    return res, low


def adjacent(fr, parts, pairs):
    import igl
    X, _ = SE.frame_xforms(fr); posed = {}
    for g, n, m, Xs in parts:
        R, t = X[g]; posed[n] = (np.asarray(m.vertices) @ np.asarray(R).T + t, np.asarray(m.faces), Xs @ np.asarray(R).T + t)
    out = {}
    for a, b in pairs:
        Va, Fa, Sa = posed[a]; Vb, Fb, Sb = posed[b]
        d1 = igl.signed_distance(np.ascontiguousarray(Sa), np.ascontiguousarray(Vb), np.ascontiguousarray(Fb, np.int64))[0]
        d2 = igl.signed_distance(np.ascontiguousarray(Sb), np.ascontiguousarray(Va), np.ascontiguousarray(Fa, np.int64))[0]
        out[f"{a.split(' (')[0][:30]} / {b.split(' (')[0][:30]}"] = float(min(d1.min(), d2.min()))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("id"); ap.add_argument("--step", type=int, default=3); ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(); t0 = time.time()
    dd = os.path.join(REPO, "pipeline", "full-exo", "designs", a.id); parts = load(dd); patch, reg, ant = fold_patch()
    print(f"{len(parts)} built parts; posterior axillary fold patch {len(patch)} skin vertices", flush=True)
    C = json.load(open(os.path.join(dd, "clips.json"))); items = []; tags = []
    for c in C["clips"]:
        for fi in range(0, len(c["frames"]), a.step):
            fr = c["frames"][fi]
            if fr["held"]: continue
            items.append((fr, parts, patch, reg)); tags.append((c["name"], fi, fr["p"][:3]))
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.jobs) as pool: R = pool.map(pose_eval, items, chunksize=4)
    else: R = list(map(pose_eval, items))
    per = {}
    for n in R[0][0]:
        v = np.array([r[0][n] for r in R]); k = int(np.argmin(v)); fold = np.array([r[1][n][2] for r in R]); kf = int(np.argmin(fold))
        per[n] = dict(min_mm=round(float(v.min()), 2), at=dict(clip=tags[k][0], frame=tags[k][1], pose=[round(x, 1) for x in tags[k][2]]),
                      region_at_min=R[k][1][n][0], at_posterior_axillary_fold=R[k][1][n][1],
                      share_lt1=round(float((v < 1).mean()), 4), share_lt2=round(float((v < 2).mean()), 4), median_mm=round(float(np.median(v)), 2),
                      posterior_axillary_fold_min_mm=round(float(fold.min()), 2),
                      fold_at=dict(clip=tags[kf][0], frame=tags[kf][1], pose=[round(x, 1) for x in tags[kf][2]]))
    print(f"{len(items)} followed frames (step {a.step}) in {time.time() - t0:.0f} s")
    for n, v in sorted(per.items(), key=lambda x: x[1]["min_mm"]):
        print(f"  {v['min_mm']:6.2f} mm  <1mm {v['share_lt1']:.3f}  <2mm {v['share_lt2']:.3f}  {v['region_at_min']:9s} fold {v['posterior_axillary_fold_min_mm']:6.1f}  {n[:60]:60s} {v['at']}")
    find = lambda s: next((n for g, n, m, X in parts if s in n), None)
    pairs = [("knee link", "J3 upper boss"), ("knee link", "E strap"), ("knee link", "link 2 strap"), ("knee link", "E boss"), ("knee link", "arm pad"),
             ("knee link", "pad mount"), ("E strap", "link 2 strap"), ("E strap", "J3 upper boss"), ("E boss", "pad mount"), ("E boss", "arm pad"),
             ("E strap", "pad mount"), ("E strap", "arm pad"), ("link 2 strap", "J3 lower plate"), ("link 1 strap", "link 2 strap"),
             ("link 1 strap", "J2 upper boss"), ("link 2 strap", "J2 lower plate"), ("link 2 strap", "pad mount"), ("link 2 strap", "arm pad")]
    pairs = [(find(x), find(y)) for x, y in pairs if find(x) and find(y)]; adj = {}
    for (fr, _, _, _), tg in list(zip(items, tags))[::2]:
        for k, v in adjacent(fr, parts, pairs).items():
            if k not in adj or v < adj[k][0]: adj[k] = (round(v, 3), tg[0], tg[1], [round(x, 1) for x in tg[2]])
    print("knee / adjacent pairs, min mesh distance over the followed frames (every 2nd; < 0 = inside):")
    for k, v in sorted(adj.items(), key=lambda x: x[1][0]): print(f"  {v[0]:7.3f} mm  {k}  {v[1:]}")
    # the verifier's near-touch neighbourhood (arm at the side), through the design's own chain
    sys.argv = [sys.argv[0]]; sys.path.insert(0, HERE)
    import build_pinknee_l1 as O
    bj = json.load(open(os.path.join(dd, "build.json"))); M, rep = O.fit(bj["fit"]["params"])
    near = [[pl, el, ax, 0.0, 0.0] for pl in (-30, -15, 0, 30, 60, 75, 90) for el in (0.0, 5.0, 10.0) for ax in (-60, -30, 0, 30, 60, 90)]
    K = O.chain(M, np.array(near, float)); kin, clear, adjm, _, worst = O.feasibility(M, K, np.array(near, float), [], skin=False); nt = []
    for j, p in enumerate(near):
        if not (kin[j] and clear[j] >= 1.0 and adjm[j] >= O.ADJ):
            nt.append(dict(pose=p[:3], closes=bool(K["ok"][j]), knee_ok=bool(K["kok"][j]), clear=None if np.isnan(clear[j]) else round(float(clear[j]), 2))); continue
        fr = O.frame_dict(K, j, p, p, False); r, low = pose_eval((fr, parts, patch, reg)); k = min(r, key=r.get)
        nt.append(dict(pose=p[:3], closes=True, lowest_part=k.split(" (")[0], lowest_mm=round(r[k], 2), region=low[k][0], fold=low[k][1],
                       knee_angle=round(float(K["Kn"]["ang"][j]), 1)))
    ok = [x for x in nt if x.get("lowest_mm") is not None]
    print(f"arm-at-side neighbourhood: {len(ok)}/{len(nt)} poses taken; lowest:")
    for x in sorted(ok, key=lambda x: x["lowest_mm"])[:8]: print("  ", x)
    held = {c: v["reasons"] for c, v in bj.get("clips", {}).items()}
    json.dump(dict(id=a.id, step=a.step, frames=len(items), fold_patch_vertices=int(len(patch)), per_part=per, adjacent=adj,
                   arm_at_side_neighbourhood=nt, held_reasons=held, secs=round(time.time() - t0, 1)),
              open(os.path.join(dd, "redteam.json"), "w"), indent=1, default=float)
    print(f"done {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
