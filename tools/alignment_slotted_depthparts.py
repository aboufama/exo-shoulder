"""Skeptic tool for the slotted-eccentric kit models: which part makes each skin press, re-worn independently.

Read-only on every claim. Runs the model UNCHANGED through its own frozen() (fit Bench(60,160) fast at the 1 mm
part-part rule, every level frozen, worn on Bench(110,360); CB_EXACT=1 for exact), exactly as
tools/alignment_slotted_partcounts.py does, then reads the worn bench's own record (B._kit_last: chain members and
their sampled points; B.res: per-pose signed distances, members concatenated in chain order) and writes, for every
contact pose (any metal sample < 0 mm), the deepest press of each member, and the per-member minimum over the taken
poses. It also reports the frozen gap, so the run doubles as an independent reproduction of the claim.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_slotted_depthparts.py <id> [--out file.json]
"""
import importlib.util, json, os, sys, tempfile, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def run(rid, out=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    mod = _load("asd_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    SE = getattr(mod, "SE", mod); K = SE.K
    p0 = mod._clean(P) if hasattr(mod, "_clean") and mod is not SE else dict(SE.PARAMS, **P)
    kb = K.bench; cap = {}; t0 = time.time()

    def bench(n_clip=60, n_ws=160):
        B = kb(n_clip, n_ws); cap[(n_clip, n_ws)] = B; return B
    K.bench = bench
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
    try:
        SE.ID = rid; res = SE.frozen(p0, tmp)
    finally:
        K.bench = kb
        try: os.remove(tmp)
        except OSError: pass
    Bb = cap[(110, 360)]; L = Bb._kit_last; pts = L["pts"]; ch = L["chain"]; n = len(Bb.idx)
    cols = []
    for m in ch.members:
        cols.append((m.name, int(pts[m.name].shape[1])))
    tot = sum(s for _, s in cols)
    contact, taken_min = [], {nm: None for nm, _ in cols}
    for i in range(n):
        r = Bb.res[i]
        if r is None: continue
        r = np.asarray(r, float)
        if r.size != tot:
            contact.append(dict(i=i, err=f"res size {r.size} != {tot}")); continue
        per, o = {}, 0
        for nm, s in cols:
            per[nm] = round(float(np.min(r[o:o + s])), 3); o += s
        if float(np.min(r)) < 0:
            pz = Bb.poses[i]
            contact.append(dict(i=i, kind=Bb.kind[i], plane=pz["plane"], elev=pz["elev"], axial=pz["axial"],
                                depth_mm=round(-float(np.min(r)), 3),
                                pressing={k: -v for k, v in sorted(per.items(), key=lambda kv: kv[1]) if v < 0}))
        else:
            for nm, v in per.items():
                taken_min[nm] = v if taken_min[nm] is None else min(taken_min[nm], v)
    contact.sort(key=lambda c: -c.get("depth_mm", 0))
    by_part = {}
    for c in contact:
        for nm, d in (c.get("pressing") or {}).items():
            b = by_part.setdefault(nm, dict(poses=0, sum_mm=0.0, max_mm=0.0)); b["poses"] += 1; b["sum_mm"] = round(b["sum_mm"] + d, 3)
            b["max_mm"] = max(b["max_mm"], d)
    rep = res["runs"]["frozen"]
    o2 = dict(id=rid, gap=rep.get("gap"), reach=rep.get("reach"), follow=rep.get("follow"), inband14=rep.get("inband14"),
              contact=rep.get("contact"), mode=Bb.mode, exact=os.environ.get("CB_EXACT") == "1", members=cols,
              n_contact=len(contact), sum_mm=round(sum(c.get("depth_mm", 0) for c in contact), 3), contact_poses=contact,
              by_part=by_part, taken_min_mm_by_part=taken_min, secs=round(time.time() - t0, 1),
              git=AA._git("rev-parse", "--short", "HEAD"),
              source=f"tools/alignment_slotted_depthparts.py: model {rid}.py unchanged (own frozen()), worn Bench(110,360)")
    print(json.dumps({k: v for k, v in o2.items() if k != "contact_poses"}, default=float))
    if out: json.dump(o2, open(out, "w"), indent=1, default=float)
    return o2


if __name__ == "__main__":
    a = sys.argv[1:]; out = a[a.index("--out") + 1] if "--out" in a else None
    run(a[0], out)
