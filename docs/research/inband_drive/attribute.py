"""Per-part, per-pose attribution of the RSSR K drive's metal cost (docs/research/inband_drive.md section 1).

One frozen wear of a config (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact or the 952 held-out
poses), then for every pose the bench evaluated: the signed skin distance of every sample point of every part (rigid
metal by name, contact-only samples split by part). From that table the bench's own score is recomputed for any set of
deleted ("ghosted") parts - the exact counterfactual of LS_GHOST for one part at a time, with the fit unchanged.

    LS_DRIVE=rssr CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/inband_drive/attribute.py \
        '<params json>' bench|held out.json [model.py]
"""
import importlib.util, itertools, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

DRIVE_PARTS = ("crank", "rod", "rodends", "horn", "ear")
ELEV_BINS = ((-1, 60), (60, 90), (90, 120), (120, 140), (140, 999))


def load(path):
    sp = importlib.util.spec_from_file_location("attr_model_" + os.path.basename(path).replace("-", "_").replace(".py", ""), path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def contact_labels(M, reg=None):
    """label every contact-only sample: the drive's member 8 (ball-link sockets first 64 pts, then the rod), member 9
    (crank boss wall + arm top), the horn lug's top (member 1, the horn's length); a model may also carry its own
    labels (M._contact_labels: list of (label, n) per contact entry)"""
    if getattr(M, "_contact_labels", None):
        out = []
        for (m, X), labs in zip(M.contact, M._contact_labels):
            out.append(labs)
        return out
    nh = len(M.rigid["horn"][1]) if "horn" in M.rigid else -1
    out = []
    for m, X in M.contact:
        n = len(X)
        if reg and id(X) in reg: out.append(list(reg[id(X)]))
        elif m == 8: out.append([("rodends", 64), ("rod", n - 64)])
        elif m == 9: out.append([("crank", n)])
        elif m == 1 and n == nh: out.append([("horn", n)])
        else: out.append([("chain:m%d" % m, n)])
    return out


def table(M, B, reg=None):
    """per pose i (valid = the bench evaluated it): {part: distances} for rigid metal (in-band) and contact-only samples"""
    labs = contact_labels(M, reg); rows = {}
    for i in range(len(B.idx)):
        if B.res[i] is None: continue                       # not kinematically valid / part clash: no metal recorded
        # ONE distance call per pose (the exact path costs per call), split back by part
        # the bench's metal_points(i) = every rigid part + every link strap (link_pts): both are skin-facing metal
        blocks = [(("R", nm), M.world(m, i, X)) for nm, (m, X) in list(M.rigid.items()) + list(M.link_pts.items()) if len(X)]
        blocks += [(("C", j), M.world(m, i, X)) for j, (m, X) in enumerate(M.contact) if len(X)]
        dd = B.dist(i, np.concatenate([X for _, X in blocks])); k = 0; rig = {}; con = {}
        for (typ, key), X in blocks:
            d = dd[k:k + len(X)]; k += len(X)
            if typ == "R": rig[key] = d; continue
            k0 = 0
            for nm, n in labs[key]:
                if n > 0: con.setdefault(nm, []).append(d[k0:k0 + n]); k0 += n
        rows[i] = (rig, {kk: np.concatenate(v) for kk, v in con.items()})
    return rows


def score(B, rows, why, ghost=()):
    """the bench's report with the parts in `ghost` deleted (rigid and contact-only); poses not in rows stay not taken"""
    ws = [j for j, k in enumerate(B.kind) if k == "ws"]; cl = [j for j, k in enumerate(B.kind) if k == "clip"]
    mn = {}; inb = []
    for i, (rig, con) in rows.items():
        ds = [d for nm, d in rig.items() if nm not in ghost]; cs = [d for nm, d in con.items() if nm not in ghost]
        m_ = min([float(d.min()) for d in ds + cs] or [1e9]); mn[i] = m_
        if B.kind[i] == "clip" and m_ >= 0: inb.append(np.concatenate(ds))
    ok = lambda j: j in mn and mn[j] >= 0
    d = np.concatenate(inb) if inb else np.zeros(0)
    r = dict(reach=float(np.mean([ok(j) for j in ws])), follow=float(np.mean([ok(j) for j in cl])),
             inband14=float(np.mean((d >= 2) & (d <= 14))) if len(d) else 0.0, contact=float(np.mean([mn[j] < 0 for j in mn])) if mn else 0.0)
    r["gap"] = CB.gap_of(r["inband14"], r["follow"], r["reach"], r["contact"])
    r["terms"] = dict(inband=round(100 * max(0, .9 - r["inband14"]), 3), reach=round(100 * max(0, .9 - r["reach"]), 3),
                      follow=round(100 * max(0, .95 - r["follow"]), 3), contact=round(100 * r["contact"], 3))
    r["n_contact"] = int(sum(mn[j] < 0 for j in mn)); r["n_inband_pts"] = int(len(d))
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}


def part_stats(B, rows):
    """per part: over the clip poses taken (the in-band pool), share 2-14 / > 14 / < 2, median, n points per pose;
    per part per elevation class the same; per part the contact poses it alone or jointly causes, and their depth"""
    out = {}; taken = {i for i, (rig, con) in rows.items() if min(min(float(d.min()) for d in rig.values()),
                                                                     min([float(d.min()) for d in con.values()] or [1e9])) >= 0}
    names = sorted({nm for rig, con in rows.values() for nm in list(rig) + list(con)})
    for nm in names:
        D = [rows[i][0][nm] for i in sorted(taken) if B.kind[i] == "clip" and nm in rows[i][0]]
        s = dict()
        if D:
            d = np.concatenate(D)
            s.update(n_per_pose=int(len(D[0])), ib14=round(float(((d >= 2) & (d <= 14)).mean()), 3), hi=round(float((d > 14).mean()), 3),
                     lo=round(float((d < 2).mean()), 3), med=round(float(np.median(d)), 2), p90=round(float(np.percentile(d, 90)), 2),
                     out_pts=int(((d < 2) | (d > 14)).sum()))
            cls = {}
            for lo_, hi_ in ELEV_BINS:
                Dc = [rows[i][0][nm] for i in sorted(taken) if B.kind[i] == "clip" and nm in rows[i][0] and lo_ <= B.poses[i]["elev"] < hi_]
                if Dc:
                    dc = np.concatenate(Dc); cls[f"e{lo_}-{hi_}"] = dict(n=len(Dc), ib14=round(float(((dc >= 2) & (dc <= 14)).mean()), 3),
                                                                         hi=round(float((dc > 14).mean()), 3), med=round(float(np.median(dc)), 1))
            s["by_elev_clip"] = cls
        # contact: poses where this part's metal (rigid or contact-only) goes under the skin
        cp = []
        for i, (rig, con) in rows.items():
            v = [float(rig[nm].min())] if nm in rig else []
            if nm in con: v.append(float(con[nm].min()))
            if v and min(v) < 0:
                others = min([float(d.min()) for k, d in rig.items() if k != nm] + [float(d.min()) for k, d in con.items() if k != nm] or [1e9])
                cp.append(dict(i=int(i), kind=B.kind[i], elev=B.poses[i]["elev"], plane=B.poses[i]["plane"], axial=B.poses[i]["axial"],
                               depth=round(-min(v), 2), alone=bool(others >= 0)))
        s["contact_poses"] = len(cp); s["contact_alone"] = int(sum(c["alone"] for c in cp)); s["contact_depth_sum"] = round(sum(c["depth"] for c in cp), 2)
        s["contact_list"] = cp
        out[nm] = s
    return out


def sub_regions(M, B, rows):
    """the crank's own samples split: boss underside vs the arm by radius along it (where along the arm it leaves the band)"""
    if "crank" not in M.rigid: return None
    X = M.rigid["crank"][1]; nb = len(X) - 4 * int(round((len(X)) / 4))
    g = getattr(M, "_scg", None)
    if g is None: return None
    PV, dR = g["PV"], g["dR"]
    w = X - PV; r = np.linalg.norm(w - (w @ dR)[:, None] * dR, axis=1)
    taken = [i for i, (rig, con) in rows.items() if B.kind[i] == "clip" and min(float(d.min()) for d in rig.values()) >= 0
             and min([float(d.min()) for d in con.values()] or [1e9]) >= 0]
    D = np.stack([rows[i][0]["crank"] for i in taken]) if taken else None
    if D is None: return None
    out = {}
    for lo, hi in ((0, 5.01), (5.01, 10), (10, 15), (15, 20), (20, 30)):
        sel = (r >= lo) & (r < hi)
        if sel.any():
            d = D[:, sel].ravel(); out[f"r{lo:.0f}-{hi:.0f}"] = dict(n=int(sel.sum()), ib14=round(float(((d >= 2) & (d <= 14)).mean()), 3),
                                                                   hi=round(float((d > 14).mean()), 3), med=round(float(np.median(d)), 1))
    out["height_over_hub_axis_mm"] = dict(boss=round(float(np.linalg.norm(PV)), 2))
    return out


def main():
    P = json.loads(sys.argv[1]); which = sys.argv[2] if len(sys.argv) > 2 else "bench"; outp = sys.argv[3] if len(sys.argv) > 3 else None
    mpath = sys.argv[4] if len(sys.argv) > 4 else os.path.join(REPO, "docs", "concepts", "models", "longstroke-slipper-knuckle-3r.py")
    t = time.time(); MOD = load(mpath)
    nc, nw = (-1, -1) if which == "held" else (60, 160) if which == "fast" else (110, 360)
    fit, M1, M, B, r = MOD._frozen_model(P, nc, nw)
    rows = table(M, B, getattr(MOD, "DRIVE_LABELS", None))
    base = score(B, rows, M.why)
    parts_present = sorted({nm for rig, con in rows.values() for nm in list(rig) + list(con) if nm in DRIVE_PARTS})
    ghosts = {"none": score(B, rows, M.why)}
    for nm in parts_present: ghosts[nm] = score(B, rows, M.why, ghost=(nm,))
    for a, b in itertools.combinations(parts_present, 2): ghosts[f"{a}+{b}"] = score(B, rows, M.why, ghost=(a, b))
    ghosts["all_drive"] = score(B, rows, M.why, ghost=tuple(parts_present))
    out = dict(model=os.path.basename(mpath), drive=os.environ.get("LS_DRIVE"), bench=which, mode=B.mode, params=P,
               reported=dict(gap=r["gap"], reach=r["reach"], inband14=r["inband14"], contact=r["contact"], why=r.get("why")),
               recomputed=base, ghost=ghosts, parts=part_stats(B, rows), crank_regions=sub_regions(M, B, rows),
               sc_info={k: v for k, v in (getattr(M1, "_sc_info", None) or {}).items() if isinstance(v, (int, float, str, bool, list))},
               secs=round(time.time() - t, 1))
    if outp: json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(reported=out["reported"], recomputed=base, ghost={k: (v["gap"], v["terms"]) for k, v in ghosts.items()},
                          parts={k: {kk: vv for kk, vv in v.items() if kk not in ("contact_list", "by_elev_clip")} for k, v in out["parts"].items()},
                          crank_regions=out["crank_regions"], secs=out["secs"]), default=float, indent=0))


if __name__ == "__main__":
    main()
