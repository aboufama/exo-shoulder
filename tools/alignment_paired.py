"""Paired per-pose comparison of two designs on the same bench (docs/ALIGNMENT.md, S1 / P1 / P3: is a small gap lead a
real gain or a bench artifact?).

New audit instrument (2026-10-17). It never edits a bench, a judge, a model or a row: the models run UNCHANGED through
their own frozen() / frozen_held(); only their pin-knee-style audit(M, B) is wrapped (as tools/alignment_audit.py
remeasure does) to dump, per pose, what the bench report averages over.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_paired.py dump <id> bench|held [--out PATH]
        -> docs/alignment/remeasure/<id>_<wear>_perpose.json: per pose kind, plane / elev / axial, evaluated, min metal
           (incl. the model's extra walls M.cmin), taken, contact, and for clip poses the number of metal samples and how
           many sit in band 2-14 mm. Its own gap is recomputed from the dump and must equal the model's report.
    python3 tools/alignment_paired.py compare <id A> <id B> [--n-boot 4000] [--out PATH]
        paired comparison on every wear both have (bench, held, and the pooled bench+held set): gap A - B, its split into
        reach / in-band / contact, the discordant poses (taken by one design only, contact in one only), and a paired
        bootstrap over poses (resampled within kind) -> the 90 % interval of the gap difference and P(A better).
"""
import json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA  # noqa: E402

REM = AA.REM


def _dump_bench(M, B):
    n = len(B.idx); cmin = getattr(M, "cmin", {}) or {}; out = []
    for i in range(n):
        p = B.poses[i]; r = B.res[i]; e = r is not None
        mm = float(np.min(r)) if e and len(r) else None
        row = dict(i=i, kind=B.kind[i], plane=p.get("plane"), elev=p.get("elev"), axial=p.get("axial"), ev=bool(e),
                   min_mm=None if mm is None else round(mm, 3), cmin=None if i not in cmin else round(float(cmin[i]), 3),
                   taken=bool(e and mm is not None and mm >= 0), contact=bool(e and mm is not None and mm < 0))
        if B.kind[i] == "clip" and row["taken"]:
            d = np.asarray(r, float); row["ns"] = int(len(d)); row["nib"] = int(((d >= 2) & (d <= 14)).sum())
        out.append(row)
    return out


def dump(rid, wear, out=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = AA._load("ap_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(f"{rid}: model has no pin-knee-style audit to wrap")
    orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B); box["poses"] = _dump_bench(M, B); box["report"] = B.report(); return a
    pk.audit = wrapped; t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig
    res = dict(id=rid, wear=wear, params=P, frozen=r.get("frozen"), report=box.get("report"), poses=box.get("poses"),
               recomputed=gap_parts(box.get("poses") or []), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    path = out or os.path.join(REM, f"{rid}_{wear}_perpose.json"); os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(res, open(path, "w"), default=float)
    print(json.dumps(dict(id=rid, wear=wear, frozen=res["frozen"], recomputed=res["recomputed"], secs=res["secs"], out=path)))
    return res


def _arrays(poses):
    k = np.array([p["kind"] for p in poses]); tk = np.array([p["taken"] for p in poses], float)
    ct = np.array([p["contact"] for p in poses], float); ev = np.array([p["ev"] for p in poses], float)
    ns = np.array([p.get("ns", 0) for p in poses], float); nib = np.array([p.get("nib", 0) for p in poses], float)
    return k, tk, ct, ev, ns, nib


def _gap(k, tk, ct, ev, ns, nib, w=None):
    w = np.ones(len(k)) if w is None else w
    ws = (k == "ws"); cl = (k == "clip")
    reach = (w * tk * ws).sum() / max((w * ws).sum(), 1e-9); follow = (w * tk * cl).sum() / max((w * cl).sum(), 1e-9)
    ib = (w * nib * tk * cl).sum() / max((w * ns * tk * cl).sum(), 1e-9); con = (w * ct).sum() / max((w * ev).sum(), 1e-9)
    parts = dict(reach=100 * max(0.0, .90 - reach), follow=100 * max(0.0, .95 - follow), inband=100 * max(0.0, .90 - ib), contact=100 * con)
    return sum(parts.values()), parts, dict(reach=reach, follow=follow, inband14=ib, contact=con)


def gap_parts(poses):
    if not poses: return None
    g, parts, raw = _gap(*_arrays(poses))
    return dict(gap=round(g, 2), **{k: round(v, 4) for k, v in raw.items()}, n_ws=int(sum(p["kind"] == "ws" for p in poses)),
                n_clip=int(sum(p["kind"] == "clip" for p in poses)), ws_taken=int(sum(p["taken"] for p in poses if p["kind"] == "ws")),
                contact_poses=int(sum(p["contact"] for p in poses)))


def _load_dump(rid, wear):
    p = os.path.join(REM, f"{rid}_{wear}_perpose.json")
    return json.load(open(p)) if os.path.exists(p) else None


def compare_sets(PA, PB, n_boot=4000, seed=0):
    key = lambda p: (p["kind"], p["plane"], p["elev"], p["axial"], p["i"])
    if [key(p) for p in PA] != [key(p) for p in PB]: raise SystemExit("pose sets differ: not a paired comparison")
    A = _arrays(PA); B = _arrays(PB)
    gA, pA, rA = _gap(*A); gB, pB, rB = _gap(*B)
    k = A[0]; ws = np.where(k == "ws")[0]; cl = np.where(k == "clip")[0]
    disc = dict(ws_taken_A_only=int(((A[1] == 1) & (B[1] == 0))[ws].sum()), ws_taken_B_only=int(((A[1] == 0) & (B[1] == 1))[ws].sum()),
                contact_A_only=int(((A[2] == 1) & (B[2] == 0)).sum()), contact_B_only=int(((A[2] == 0) & (B[2] == 1)).sum()),
                contact_both=int(((A[2] == 1) & (B[2] == 1)).sum()))
    rng = np.random.default_rng(seed); d = np.empty(n_boot)
    for b in range(n_boot):
        w = np.zeros(len(k))
        np.add.at(w, rng.choice(ws, len(ws)), 1.0); np.add.at(w, rng.choice(cl, len(cl)), 1.0)
        d[b] = _gap(*A, w=w)[0] - _gap(*B, w=w)[0]
    lo, hi = np.percentile(d, [5, 95])
    return dict(gap_A=round(gA, 2), gap_B=round(gB, 2), diff=round(gA - gB, 2),
                split={c: round(pA[c] - pB[c], 2) for c in pA}, discordant=disc,
                boot=dict(n=n_boot, ci90=[round(float(lo), 2), round(float(hi), 2)], sd=round(float(d.std()), 2),
                          p_A_better=round(float((d < 0).mean()), 3)))


def compare(a, b, n_boot=4000, out=None):
    res = dict(A=a, B=b, note="diff = gap A - gap B (negative: A better); split per gap term; paired bootstrap over poses within kind")
    pooled_A, pooled_B = [], []
    for wear in ("bench", "held"):
        da, db = _load_dump(a, wear), _load_dump(b, wear)
        if not da or not db: res[wear] = "missing dump"; continue
        res[wear] = compare_sets(da["poses"], db["poses"], n_boot)
        res[wear]["model_frozen"] = dict(A=(da.get("frozen") or {}).get("gap"), B=(db.get("frozen") or {}).get("gap"))
        tag = lambda P, w: [dict(p, i=f"{w}:{p['i']}") for p in P]
        pooled_A += tag(da["poses"], wear); pooled_B += tag(db["poses"], wear)
    if pooled_A and len(pooled_A) == len(pooled_B): res["pooled_bench_plus_held"] = compare_sets(pooled_A, pooled_B, n_boot)
    path = out or os.path.join(REM, f"{a}_vs_{b}_paired.json"); json.dump(res, open(path, "w"), indent=1)
    print(json.dumps(res, indent=1)); return res


def main(argv):
    if not argv: print(__doc__); return
    get = lambda f, d=None: argv[argv.index(f) + 1] if f in argv else d
    if argv[0] == "dump": dump(argv[1], argv[2], get("--out"))
    elif argv[0] == "compare": compare(argv[1], argv[2], int(get("--n-boot", 4000)), get("--out"))
    else: print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
