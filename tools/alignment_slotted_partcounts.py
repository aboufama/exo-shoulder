"""Per-part sample counts for the slotted-eccentric kit models (skeptic tool, read-only on every claim).

The kit's evaluate() reports inband_member as fractions only: per[m] = share of member m's metal samples within 2-14 mm
over clip frames that are not in contact, and 0.0 when the member has NO sample there (tools/concept_kit.py
`if dm.size else 0.0`). This runs the model UNCHANGED through its own frozen() (fit Bench(60,160) fast, worn on
Bench(110,360), CB_EXACT=1 for exact), exactly as tools/alignment_slotted_rewear.py does, and then reads the worn bench's
own record (B._kit_last: chain members, sampled points, per-pose distances in B.res) to print, per member, the number of
metal samples per pose, the number of clip samples behind the fraction, the fraction re-derived from those samples and
the median clearance. Writes nothing in the repo unless --out is given.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_slotted_partcounts.py <id> [--out file.json]
"""
import importlib.util, json, os, sys, tempfile
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def run(rid, out=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    mod = _load("asp_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    SE = getattr(mod, "SE", mod); K = SE.K
    p0 = mod._clean(P) if hasattr(mod, "_clean") and mod is not SE else dict(SE.PARAMS, **P)
    kb = K.bench; cap = {}

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
    Bb = cap[(110, 360)]; L = Bb._kit_last; pts = L["pts"]; ch = L["chain"]
    n = len(Bb.idx); clip = np.array([k == "clip" for k in Bb.kind], bool)
    good = np.array([Bb.res[i] is not None and float(np.min(Bb.res[i])) >= 0 for i in range(n)], bool)
    # B.res[i] holds the per-sample distances of the poses the kit evaluated (members concatenated in chain order)
    sel = [i for i in range(n) if clip[i] and good[i]]
    D = np.array([np.asarray(Bb.res[i], float) for i in sel]) if sel else np.zeros((0, 0))
    rows, o = {}, 0
    for m in ch.members:
        s = int(pts[m.name].shape[1]); dm = D[:, o:o + s] if D.size else np.zeros((0, s)); o += s
        rows[m.name] = dict(per_pose=s, clip_samples=int(dm.size),
                            ib14=round(float(((dm >= 2) & (dm <= 14)).mean()), 4) if dm.size else None,
                            median_mm=round(float(np.median(dm)), 2) if dm.size else None)
    tot = sum(r["clip_samples"] for r in rows.values())
    w = sum(r["ib14"] * r["clip_samples"] for r in rows.values() if r["ib14"] is not None) / max(tot, 1)
    nz = [r["ib14"] for r in rows.values() if r["ib14"] is not None]
    rep = res["runs"]["frozen"]
    o2 = dict(id=rid, gap=rep.get("gap"), inband14=rep.get("inband14"), inband_member=rep.get("inband_member"), clip_good_poses=len(sel),
              samples_total_cols=o, res_cols=int(D.shape[1]) if D.size else None, parts=rows,
              sample_weighted=round(w, 4), part_weighted=round(float(np.mean(nz)), 4) if nz else None,
              zero_sample_parts=[k for k, r in rows.items() if r["clip_samples"] == 0])
    print(json.dumps(o2, indent=1))
    if out: json.dump(o2, open(out, "w"), indent=1)
    return o2


if __name__ == "__main__":
    a = sys.argv[1:]; out = a[a.index("--out") + 1] if "--out" in a else None
    run(a[0], out)
