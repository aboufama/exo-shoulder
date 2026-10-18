"""Alignment probe (read-only): does the dashboard's per-design "sweep best gap" come from a configuration its own model
flagged dishonest? (proposed catalogue entry R5, docs/alignment/slotted-eccentric-pin-knee-3r.md)

tools/dash_build.py sweeps() rebuilds every sweep configuration's gap from its shares (or keeps the file gap when that is
larger) and takes the per-design minimum over the configurations not passed over by the claim. It never reads the
configuration's own `honest` flag nor its `obj` (a model's penalised objective, e.g. +100 when the slot gate fails or a
part leaves its declared stack), so a configuration the model itself rejected - parts lifted out of band, a failed gate,
an un-stacked collision - can become the design's "Sweep best gap" on the dashboard (and the all-time sweep record).

This tool re-reads docs/concepts/sweeps/*.json with dash_build's own parser and claim rule, and reports per design:
the dashboard's sweep best, the best over configurations not flagged honest=False, the best with each configuration read
at max(gap, obj), and the configuration that sets the dashboard number. It changes nothing.

    python3 tools/alignment_sweep_honesty.py [--ids a,b] [--out path.json]
"""
import glob, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import dash_build as DB                                          # noqa: E402  (main() is guarded)


def run(ids=None):
    C = DB.claims(); out = {}
    for p in sorted(glob.glob(os.path.join(DB.CONCEPTS, "sweeps", "*.json"))):
        mid = DB.slug(os.path.splitext(os.path.basename(p))[0].split("@")[0])
        if ids and mid not in ids: continue
        D = DB.load(p)
        if D is None: continue
        items = [x for x in DB.as_list(D, "configs", "rows", "results") if isinstance(x, dict)]
        items = [x for x in items if DB.norm_time(x.get("t") or x.get("time"))]
        rows = DB.sweep_file_rows(mid, items, os.path.relpath(p, REPO))
        if len(rows) != len(items): continue                       # parser skipped something: do not guess the pairing
        c = C.get(mid); best = {}
        for r, x in zip(rows, items):
            if r["gap"] is None: continue
            if c and r["t"] <= c[1] and r["gap"] < c[0] - 0.005: continue          # passed over (dash_build rule)
            honest = x.get("honest"); obj = DB.num(x.get("obj"))
            for key, ok, g in (("dash", True, r["gap"]), ("honest", honest is not False, r["gap"]),
                               ("obj", True, max(r["gap"], obj) if obj is not None else r["gap"])):
                if ok and (key not in best or g < best[key][0]):
                    best[key] = (g, dict(k=r["k"], t=r["t"], tag=x.get("tag"), stream=x.get("stream"), honest=honest, obj=obj,
                                         inband14=r["inband14"], reach=r["reach"], follow=r["follow"], contact=r["contact"]))
        if "dash" not in best: continue
        d = best["dash"]; h = best.get("honest"); o = best.get("obj")
        out.setdefault(mid, {}).update(dash=d[0], dash_cfg=d[1], honest_best=h[0] if h else None, obj_best=o[0] if o else None,
                                      n_dishonest=sum(1 for x in items if x.get("honest") is False), n=len(items))
    flagged = {k: v for k, v in out.items() if v["dash_cfg"]["honest"] is False}
    return dict(n_designs=len(out), flagged=flagged,
                summary=[dict(id=k, dash=v["dash"], honest_best=v["honest_best"], delta=None if v["honest_best"] is None else round(v["honest_best"] - v["dash"], 2),
                              tag=v["dash_cfg"]["tag"]) for k, v in sorted(flagged.items(), key=lambda kv: kv[1]["dash"])])


if __name__ == "__main__":
    a = sys.argv[1:]
    ids = set(a[a.index("--ids") + 1].split(",")) if "--ids" in a else None
    r = run(ids)
    if "--out" in a: json.dump(r, open(a[a.index("--out") + 1], "w"), indent=1, default=float)
    print(json.dumps(dict(n_designs=r["n_designs"], n_flagged=len(r["flagged"]), summary=r["summary"]), indent=1, default=float))
