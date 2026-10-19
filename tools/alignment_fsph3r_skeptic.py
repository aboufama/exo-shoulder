"""Usage: OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_fsph3r_skeptic.py <out.json> [exact]
Skeptic re-measure of fold-sph3r on its claim bench, independent of tools/alignment_fsph3r_rewear.py.
Model file runs unchanged (mod.evaluate); everything else is read from B.res / B._kit_last.
Phase 1 (fast, Bench(60,160)): F, G, F@q1, G@q0.9805 -> gap, near-touch counts, near-touch gaps, th margin over taken
poses (concept_kit closure margin formula), per-part in-band, overhead, contact depth.
Phase 2 (optional, argv 'exact'): for F, the taken poses with fast min metal < 2 mm plus the contact pose(s): the SAME
metal points (faces + hub crowns / walls) re-measured with the exact libigl distance (CB_EXACT bench, same pose idx)."""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"
sys.path.insert(0, os.path.join(REPO, "tools"))
OUT = sys.argv[1]
PHASE2 = "exact" in sys.argv


def load():
    sp = importlib.util.spec_from_file_location("sk_fsph3r", os.path.join(REPO, "docs/concepts/models/fold-sph3r.py"))
    m = importlib.util.module_from_spec(sp); sys.modules["sk_fsph3r"] = m; sp.loader.exec_module(m); return m


mod = load(); K = mod.K
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/fold-sph3r.json")))
PF = dict(row["best_params"]); PG = dict(row["best_near_touch_clean"]["params"])
cfgs = [("F", PF), ("G", PG), ("F_q1", dict(PF, q=1.0)), ("G_q09805", dict(PG, q=0.9805))]


def crown_min(B, ch, prof, idx):
    hubs = [m for m in ch.members if m.kind == "flat"]
    if not len(idx): return {}
    C = np.concatenate([mod.crown_points(m, prof[m.name])[idx] for m in hubs], 1)
    dc = K.dist_many(B, np.repeat(idx, C.shape[1]), C.reshape(-1, 3)).reshape(len(idx), C.shape[1])
    return {int(j): float(dc[k].min()) for k, j in enumerate(idx)}


def near_gap(B, thr, cm):
    save = list(B.res)
    for j in range(len(B.res)):
        if B.res[j] is not None and min(float(np.min(B.res[j])), cm.get(j, 1e9)) < thr: B.res[j] = np.append(B.res[j], -1e-3)
    r = B.report(); B.res = save; return r["gap"]


res = {}
B = K.bench(60, 160)
for lab, P in cfgs:
    t = time.time()
    p, r = mod.evaluate(B, dict(P))
    L = B._kit_last; ch, prof, pts = L["chain"], L["prof"], L["pts"]
    ev = [j for j in range(len(B.res)) if B.res[j] is not None]
    cm = crown_min(B, ch, prof, np.array(ev, int))
    tk = [j for j in ev if float(np.min(B.res[j])) >= 0]
    allmin = {j: min(float(np.min(B.res[j])), cm.get(j, 1e9)) for j in ev}
    J1, J3 = np.asarray(ch.joints["J1"], float), np.asarray(ch.joints["J3"], float)
    th = np.degrees(np.arccos(np.clip((J1 * J3).sum(-1) / np.linalg.norm(J1, axis=-1) / np.linalg.norm(J3, axis=-1), -1, 1)))
    a1, a2 = float(p["a1"]), float(p["a2"])
    marg = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    tkc = [j for j in tk if B.kind[j] == "clip"]; o = 0; parts = {}
    for m in ch.members:
        s = pts[m.name].shape[1]
        d = np.concatenate([B.res[j][o:o + s] for j in tkc]); o += s
        parts[m.name] = [round(float(((d >= 2) & (d <= 14)).mean()), 4), round(float(np.median(d)), 2), int(s), round(float(np.percentile(d, 90)), 2)]
    tot = sum(v[2] for v in parts.values()); sw = sum(v[0] * v[2] for v in parts.values()) / tot; pw = np.mean([v[0] for v in parts.values()])
    el = np.array([q["elev"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind])
    ovw = [j for j in range(len(B.res)) if ws[j] and el[j] >= 140]
    ov_taken = [j for j in ovw if j in set(tk)]
    contact = [dict(i=j, kind=B.kind[j], mm=round(allmin[j], 3), **{k: B.poses[j][k] for k in ("plane", "elev", "axial")}) for j in ev if allmin[j] < 0]
    res[lab] = dict(params=p, gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"],
                    model_min_margin=r.get("min_margin"), model_gap_near1=r.get("gap_near1"),
                    n_eval=len(ev), n_taken=len(tk), n_taken_clip=len(tkc), n_taken_ws=len([j for j in tk if B.kind[j] == "ws"]),
                    n_lt1=sum(1 for j in tk if allmin[j] < 1), n_lt2=sum(1 for j in tk if allmin[j] < 2),
                    near1=near_gap(B, 1.0, cm), near2=near_gap(B, 2.0, cm),
                    min_metal_taken=round(min(allmin[j] for j in tk), 4),
                    th_min_taken=round(float(marg[tk].min()), 3), th_min_eval=round(float(marg[ev].min()), 3), n_th_lt5=int((marg[tk] < 5).sum()),
                    parts=parts, sample_weighted=round(sw, 4), part_weighted=round(float(pw), 4),
                    overhead_ws=len(ovw), overhead_taken=len(ov_taken), overhead_taken_min_mm=sorted(round(allmin[j], 3) for j in ov_taken),
                    contact_poses=contact, hubF={m.name: round(float(prof[m.name][0]), 2) for m in ch.members if m.kind == "flat"},
                    secs=round(time.time() - t, 1))
    print(lab, json.dumps({k: v for k, v in res[lab].items() if k not in ("params", "parts")}), flush=True)
    if lab == "F":
        near = sorted([j for j in tk if allmin[j] < 2] + [c["i"] for c in contact])
        keep = dict(idx=near, fast={j: allmin[j] for j in near},
                    P={j: np.concatenate([pts[m.name][j] for m in ch.members] + [mod.crown_points(m, prof[m.name])[j] for m in ch.members if m.kind == "flat"], 0) for j in near})
    json.dump(res, open(OUT, "w"), indent=1, default=float)

if PHASE2:
    os.environ["CB_EXACT"] = "1"
    BE = K.bench(60, 160)
    assert BE.mode == "exact" and list(BE.idx) == list(B.idx)
    ex = {}
    for j in keep["idx"]:
        t = time.time(); d = BE.dist(int(j), keep["P"][j])
        ex[int(j)] = dict(fast=round(keep["fast"][j], 3), exact=round(float(np.min(d)), 3), kind=BE.kind[j], elev=BE.poses[j]["elev"], secs=round(time.time() - t, 1))
        print("exact", j, ex[int(j)], flush=True)
        res["F_exact_near"] = ex; json.dump(res, open(OUT, "w"), indent=1, default=float)
