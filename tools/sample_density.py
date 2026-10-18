"""Per-part sampling density of a design's scored metal vs the kit's (docs/ALIGNMENT.md S2 / S6: in-band is a SHARE OF
SAMPLES, so a part sampled denser than the rest weighs extra in in-band14 - out-of-band metal over-sampled inflates the
gap, well-placed metal over-sampled deflates it).

The kit's density (tools/concept_kit.py: Member.cell = 4.0 mm2 per sample, straps 2 x 2 mm at r_ref, hub discs on a 2 mm
grid; tools/concept_bench.py: "~1 pt / 4 mm2"): 1 sample per 4 mm2. The death audit of desmo-window (commit 14dfecc)
found ring2 at 1 pt / 1 mm2 (4x); this tool measures every part of every row the same way.

It never edits a bench, a judge, a model or a row. Measurement only:

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/sample_density.py measure <id> [--params p.json] [--src-bench F] [--src-held F]
        fits the frozen claim's shape exactly as the verifier does (the model's own frozen(): fit on Bench(60,160) fast;
        the run is stopped when the wear bench is built, before any wear), reads every scored part's samples
        (M.rigid + M.link_pts, the same arrays and order as part_inband()), and reports per part: n, cell area per sample
        (d1 x d2: nearest-neighbour spacing x the nearest spacing at > 60 deg to it, i.e. the grid's two pitches; a one-row
        part gets the kit's 2 mm across), area = sum of cells, samples / mm2 and the ratio to the kit (1 / 4 mm2). Flags
        parts > 2x or < 0.5x. Then re-weights the verifier's saved per-part in-band (parts_ib14 [frac, median, n],
        bench and held, files whose own gap reproduces the claim) with each flagged part's count set to its kit-density
        count (n / ratio): in-band = sum frac n / sum n is exact for the counts, and assumes the part's in-band share is
        uniform over its samples (the kit-density subsample carries the part's share). Reach, follow and contact are
        unchanged (rigid in-band samples only). -> docs/alignment/remeasure/sample_density_<id>.json
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/sample_density.py rewear <id> bench|held [--params p.json]
        the exact confirmation: the same frozen claim with every flagged part thinned to the kit's density (greedy
        2 mm Poisson-disc subsample of the fitted part, before the wear) -> docs/alignment/remeasure/sample_density_<id>_<wear>_rewear.json
    python3 tools/sample_density.py table                       # markdown table of every sample_density_*.json
"""
import glob, importlib.util, json, math, os, re, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = os.path.join(REPO, "docs", "concepts", "rows")
MODELS = os.path.join(REPO, "docs", "concepts", "models")
VERIFY = os.path.join(REPO, "docs", "concepts", "verify")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
sys.path.insert(0, os.path.join(REPO, "tools"))

VERSION = "2026-10-18.1"
KIT_CELL = 4.0          # mm2 per sample (tools/concept_kit.py Member.cell; concept_bench "~1 pt / 4 mm2")
KIT_STEP = 2.0          # mm (the kit's pitch; a one-row part is credited 2 mm across)
FLAG_HI, FLAG_LO = 2.0, 0.5


class _Stop(Exception):
    pass


def _row(rid):
    return json.load(open(os.path.join(ROWS, rid + ".json")))


def _gap(ib14, follow, reach, contact):
    return 100 * (max(0.0, .90 - ib14) + max(0.0, .95 - follow) + max(0.0, .90 - reach)) + 100 * contact


def _find_parts(d, path=""):
    """(path, sub-dict) for every dict on file that carries parts_ib14 next to a frozen gap"""
    out = []
    if isinstance(d, dict):
        if isinstance(d.get("parts_ib14"), dict) and isinstance(d.get("frozen"), dict) and d["frozen"].get("gap") is not None:
            out.append((path, d))
        for k, v in d.items():
            if k != "parts_ib14": out += _find_parts(v, path + "/" + k)
    elif isinstance(d, list):
        for i, v in enumerate(d[:64]): out += _find_parts(v, path + f"[{i}]")
    return out


def sources(rid, row=None):
    """per-part in-band records on file (verifier outputs first, then audit re-measures), with their own gap and wear"""
    fs = sorted(glob.glob(os.path.join(VERIFY, rid + "_*.json")) + glob.glob(os.path.join(VERIFY, rid + "*", "*.json")))
    fs += sorted(f for f in glob.glob(os.path.join(REM, rid + "_*.json")) if "perpose" not in f and "sample_density" not in f)
    out = []
    for f in fs:
        try: d = json.load(open(f))
        except Exception: continue
        for path, sub in _find_parts(d):
            pib = sub["parts_ib14"]
            if not all(isinstance(v, list) and len(v) >= 3 for v in pib.values()): continue
            wear = sub.get("wear") if sub.get("wear") in ("bench", "held") else d.get("wear") if d.get("wear") in ("bench", "held") else ("held" if "held" in os.path.basename(f) else "bench")
            out.append(dict(file=os.path.relpath(f, REPO), path=path or "/", wear=wear, frozen=sub["frozen"], parts=pib,
                            params=sub.get("params") or d.get("params")))
    return out


def pick_sources(rid, row, src_bench=None, src_held=None):
    """the claim's bench record (own gap = the row's v_gap +- 0.05; verifier file preferred) and its held record (same
    file stem with held, else the held record whose params match the bench record's)"""
    S = sources(rid, row); vg = row.get("v_gap"); vg = float(vg) if vg is not None else None
    def by_file(f): return [s for s in S if s["file"] == f or s["file"].endswith(f)]
    b = by_file(src_bench)[0] if src_bench and by_file(src_bench) else None
    if b is None:
        cand = [s for s in S if s["wear"] == "bench" and (vg is None or abs(float(s["frozen"]["gap"]) - vg) <= 0.05)]
        cand.sort(key=lambda s: (0 if "/verify/" in "/" + s["file"] else 1, 0 if "_v_bench_frozen" in s["file"] else 1, len(s["file"])))
        b = cand[0] if cand else None
    h = by_file(src_held)[0] if src_held and by_file(src_held) else None
    if h is None and b is not None:
        stem = b["file"].replace("_bench", "_held")
        hs = [s for s in S if s["wear"] == "held" and s["file"] == stem and s["path"] == b["path"]]
        if not hs:
            hs = [s for s in S if s["wear"] == "held" and s["params"] and b["params"] and
                  all(abs(float(s["params"].get(k, 1e9)) - float(v)) < 1e-6 for k, v in b["params"].items() if isinstance(v, (int, float)) and not isinstance(v, bool))]
            hs.sort(key=lambda s: (0 if "/verify/" in "/" + s["file"] else 1, len(s["file"])))
        h = hs[0] if hs else None
    return b, h, S


# ---- the fitted shape (the verifier's own frozen(), stopped before the wear) --------------------------------------
def _load_model(rid, row, params=None):
    bp = row.get("best_params")
    if isinstance(bp, str):
        try: bp = json.loads(bp)
        except Exception: bp = None
    P = dict(bp) if isinstance(bp, dict) else {}
    if params: P.update(params)
    mf = P.get("model") or row.get("model_file") or os.path.join(MODELS, rid + ".py")
    mf = mf if os.path.isabs(mf) else os.path.join(REPO, mf)
    argv = list(sys.argv); sys.argv = [argv[0]]
    try:
        sp = importlib.util.spec_from_file_location("sd_" + re.sub(r"\W", "_", rid), mf); mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
    finally:
        sys.argv = argv
    return mod, P, os.path.relpath(mf, REPO)


def _has_parts(o):
    return hasattr(o, "rigid") and hasattr(o, "link_pts") and isinstance(getattr(o, "rigid", None), dict)


def fitted(rid, row, params=None, thin=None):
    """the fitted M1 of the claim (fit on Bench(60,160) fast). thin=None: stop at the wear bench and return M1;
    thin=(names, step): thin those parts of M1 in place when the wear bench is built, let the wear run, return (M1, result)"""
    import concept_bench as CB
    mod, P, mf = _load_model(rid, row, params)
    orig = CB.Bench.__init__; box = {}

    def patched(self, *a, **k):
        if box.get("first_done"):
            f = sys._getframe(1); M1 = None
            while f is not None and M1 is None:
                for v in list(f.f_locals.values()):
                    if _has_parts(v) and getattr(getattr(v, "B", None), "kind", None) is not None and len(v.B.kind) < 400: M1 = v; break
                f = f.f_back
            box["M1"] = M1
            if thin is None: raise _Stop()
            if M1 is not None and not box.get("thinned"): box["thin_info"] = _thin(M1, *thin); box["thinned"] = True
        else:
            box["first_done"] = True
        return orig(self, *a, **k)
    CB.Bench.__init__ = patched; t = time.time()
    try:
        fz = getattr(mod, "frozen")
        if thin is None:
            try: fz(dict(P))
            except _Stop: pass
            return box.get("M1"), P, mf, round(time.time() - t, 1)
        wear = thin[2]
        r = fz(dict(P)) if wear == "bench" else mod.frozen_held(dict(P))
        return box.get("M1"), P, mf, round(time.time() - t, 1), r, box.get("thin_info")
    finally:
        CB.Bench.__init__ = orig


def part_sets(M):
    """the scored metal per part, in part_inband()'s order: M.rigid then M.link_pts, (n, 3) in the part's own frame"""
    out = {}
    for nm, (m, X) in list(M.rigid.items()) + list(M.link_pts.items()):
        out[nm] = np.asarray(X, float).reshape(-1, 3)
    return out


def density(X):
    """cell area per sample (d1 x d2) over the unique samples; n counts duplicates (a duplicate is extra weight)"""
    n = len(X)
    if n == 0: return dict(n=0)
    U = np.unique(np.round(X, 2), axis=0)
    if len(U) == 1: return dict(n=n, n_unique=1, area_mm2=KIT_CELL, cell_median=KIT_CELL, d1=None, d2=None, ratio=round(n * KIT_CELL / KIT_CELL, 2), rows="point")
    V = U[None, :, :] - U[:, None, :]; D = np.linalg.norm(V, axis=-1); np.fill_diagonal(D, np.inf)
    j1 = D.argmin(1); d1 = D[np.arange(len(U)), j1]
    v1 = V[np.arange(len(U)), j1] / d1[:, None]
    cosang = np.abs(np.einsum("ijk,ik->ij", V, v1) / np.where(np.isfinite(D), D, 1.0))
    D2 = np.where(cosang < 0.5, D, np.inf); d2 = D2.min(1)
    one_row = ~np.isfinite(d2) | (d2 > 4 * KIT_STEP)
    d2 = np.where(one_row, KIT_STEP, d2)
    cell = d1 * d2; area = float(cell.sum())
    out = dict(n=int(n), n_unique=int(len(U)), area_mm2=round(area, 1), cell_median=round(float(np.median(cell)), 3),
               d1=round(float(np.median(d1)), 3), d2=round(float(np.median(d2)), 3), one_row_share=round(float(one_row.mean()), 3),
               ratio=round(n * KIT_CELL / max(area, 1e-9), 3))
    # second reading for small / compact parts: the convex hull of the part on its best-fit plane plus a border of half its
    # own pitch (the cell convention's (L1 + p)(L2 + p)); the cell sum over-states a tiny part's area (its border cells)
    try:
        from scipy.spatial import ConvexHull
        c = U.mean(0); _, sv, Vt = np.linalg.svd(U - c, full_matrices=False); Y = (U - c) @ Vt[:2].T
        H = ConvexHull(Y); p = float(np.median(d1)); ah = float(H.volume) + 0.5 * p * float(H.area) + p * p
        out.update(hull_area_mm2=round(ah, 1), ratio_hull=round(n * KIT_CELL / max(ah, 1e-9), 3), flatness=round(float(sv[2] / max(sv[0], 1e-9)), 3))
    except Exception:
        pass
    # a masked lattice: the part keeps only some cells of a regular grid at the kit's pitch (a strap stub whose other cells
    # sit under a hub); its cell estimate reads sparse, but each kept sample is one kit cell
    out["masked_lattice"] = bool(out["ratio"] < FLAG_LO and float(np.median(d1)) <= 1.25 * KIT_STEP * max(1.0, float(np.linalg.norm(U, axis=1).mean()) / 70.0))
    return out


def _thin(M, names, step=KIT_STEP):
    """greedy Poisson-disc subsample (min spacing `step` mm) of the named parts of a fitted model, in place"""
    info = {}
    for nm in names:
        src = M.rigid if nm in M.rigid else M.link_pts if nm in M.link_pts else None
        if src is None: continue
        m, X = src[nm]; X = np.asarray(X, float); keep = []
        for i in np.lexsort((X[:, 2], X[:, 1], X[:, 0])):
            if all(np.linalg.norm(X[i] - X[j]) >= step - 1e-6 for j in keep): keep.append(i)
        keep = np.sort(np.array(keep, int)); src[nm] = (m, X[keep]); info[nm] = [int(len(X)), int(len(keep))]
    return info


# ---- the re-weight ------------------------------------------------------------------------------------------------
def reweight(rec, ratios, flagged):
    """in-band and gap of a saved record with each flagged part's count set to its kit-density count (n / ratio)"""
    fz = rec["frozen"]; parts = rec["parts"]
    f = {k: float(v[0]) for k, v in parts.items()}; n = {k: float(v[2]) for k, v in parts.items()}
    base = sum(f[k] * n[k] for k in parts) / sum(n.values())
    def ib_with(nn): return sum(f[k] * nn[k] for k in parts) / sum(nn.values())
    out = dict(file=rec["file"], path=rec["path"], frozen=fz, recomputed_ib14=round(base, 4))
    ib0 = float(fz["inband14"]); g0 = float(fz["gap"])
    rest = g0 - 100 * max(0.0, .90 - ib0)                       # reach + follow + contact terms, unchanged
    def gap_of(ib): return round(rest + 100 * max(0.0, .90 - ib), 2)
    var = {}
    def at(parts_, rr=ratios):
        nn = dict(n); [nn.__setitem__(k, max(1.0, n[k] / rr[k])) for k in parts_ if k in nn and rr.get(k)]
        ib = ib0 + ib_with(nn) - base; return dict(ib14=round(ib, 4), gap=gap_of(ib), n={k: round(nn[k], 2) for k in parts_ if k in nn})
    over = [k for k in flagged if (ratios.get(k) or 0) > FLAG_HI]
    var["over_at_kit"] = at(over)                               # the primary reading: over-dense parts to the kit's density
    hull = ratios.get("_hull", {})
    rr_h = {k: max(ratios.get(k) or 0, hull.get(k) or 0) for k in over}
    var["over_at_kit_hull"] = at(over, rr_h)                     # same, with the higher of the two density readings
    var["flagged_at_kit"] = at(flagged)                          # over- and under-dense parts (sensitivity)
    var["per_part"] = {k: at([k])["gap"] for k in flagged}
    na = {k: (n[k] / ratios[k] if ratios.get(k) else n[k]) for k in n}
    ib = ib0 + ib_with(na) - base; var["all_parts_at_kit"] = dict(ib14=round(ib, 4), gap=gap_of(ib))
    var["as_sampled"] = dict(ib14=round(ib0, 4), gap=round(g0, 2))
    out["variants"] = var
    out["count_mismatch"] = {k: [int(n[k]), ratios.get("_n", {}).get(k)] for k in n if ratios.get("_n", {}).get(k) not in (None, int(n[k]))}
    return out


def measure(rid, params=None, src_bench=None, src_held=None, write=True):
    row = _row(rid); b, h, S = pick_sources(rid, row, src_bench, src_held)
    P = dict(params or {})
    if b and b.get("params"):                                   # the claim's own params (the record that reproduces the gap)
        P = dict({k: v for k, v in b["params"].items()}, **P)
    t = time.time(); M1, Pu, mf, secs = fitted(rid, row, P)
    if M1 is None: raise SystemExit(f"{rid}: no fitted model with rigid / link_pts found (not a pin-knee-style model)")
    sets = part_sets(M1); dens = {k: density(X) for k, X in sets.items()}
    ratios = {k: d.get("ratio") for k, d in dens.items()}; ratios["_n"] = {k: d["n"] for k, d in dens.items()}
    ratios["_hull"] = {k: d.get("ratio_hull") for k, d in dens.items()}
    flagged = [k for k, d in dens.items() if d.get("ratio") and (d["ratio"] > FLAG_HI or d["ratio"] < FLAG_LO)]
    out = dict(id=rid, tool="tools/sample_density.py", version=VERSION, kit_cell_mm2=KIT_CELL, flag=[FLAG_LO, FLAG_HI],
               model=mf, params=Pu, fit_secs=secs, row_v_gap=row.get("v_gap"), row_status=row.get("status"),
               parts=dens, flagged={k: dens[k]["ratio"] for k in flagged}, over_dense=[k for k in flagged if dens[k]["ratio"] > FLAG_HI],
               masked_lattice=[k for k in flagged if dens[k].get("masked_lattice")],
               note="ratio = samples / mm2 over the kit's 1 / 4 mm2 (cell = d1 x d2, the grid's two pitches; a one-row part is "
                    "credited 2 mm across). Re-weight: each flagged part's count set to n / ratio in the saved per-part in-band; "
                    "exact for the counts, assumes the part's in-band share is uniform over its samples.")
    for wear, rec in (("bench", b), ("held", h)):
        out[wear] = reweight(rec, ratios, flagged) if rec else None
    out["exact_rewear_cmd"] = (f"CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/sample_density.py rewear {rid} bench|held"
                               + (" --params <claim params>" if params else ""))
    out["secs"] = round(time.time() - t, 1)
    if write:
        os.makedirs(REM, exist_ok=True)
        json.dump(out, open(os.path.join(REM, f"sample_density_{rid}.json"), "w"), indent=1, default=float)
    V = lambda w: None if not out[w] else [out[w]["frozen"]["gap"]] + [out[w]["variants"][k]["gap"] for k in ("over_at_kit", "over_at_kit_hull", "flagged_at_kit", "all_parts_at_kit")]
    brief = dict(id=rid, flagged=out["flagged"], masked=[k for k in flagged if dens[k].get("masked_lattice")], bench=V("bench"), held=V("held"),
                 src=[None if not b else b["file"], None if not h else h["file"]], fit_secs=secs)
    print(json.dumps(brief, default=float)); return out


def rewear(rid, wear, params=None):
    row = _row(rid); prev = os.path.join(REM, f"sample_density_{rid}.json")
    if not os.path.exists(prev): raise SystemExit(f"run `measure {rid}` first")
    d = json.load(open(prev)); names = list(d.get("flagged") or {})
    P = dict(d.get("params") or {}); P.update(params or {})
    M1, Pu, mf, secs, r, info = fitted(rid, row, P, thin=(names, KIT_STEP, wear))
    res = dict(id=rid, wear=wear, thinned=info, frozen=r.get("frozen"), parts_ib14=r.get("parts_ib14"), params=Pu,
               exact=os.environ.get("CB_EXACT") == "1", secs=secs, version=VERSION)
    json.dump(res, open(os.path.join(REM, f"sample_density_{rid}_{wear}_rewear.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, frozen=res["frozen"], thinned=info), default=float)); return res


def table():
    lines = ["| row | v_gap | flagged parts (ratio to kit; m = masked lattice) | bench: claim -> over-dense at kit [hull reading] (flagged incl. sparse; all parts) | held: same |",
             "|---|---|---|---|---|"]
    for f in sorted(glob.glob(os.path.join(REM, "sample_density_*.json"))):
        if f.endswith("_rewear.json"): continue
        d = json.load(open(f))
        fl = ", ".join(f"{k} {v:.2f}x" + (" m" if k in (d.get("masked_lattice") or []) else "") for k, v in (d.get("flagged") or {}).items()) or "none"
        def cell(w):
            x = d.get(w)
            if not x: return "no record"
            v = x["variants"]; return (f"{x['frozen']['gap']:.2f} -> {v['over_at_kit']['gap']:.2f} [{v['over_at_kit_hull']['gap']:.2f}] "
                                       f"({v['flagged_at_kit']['gap']:.2f}; {v['all_parts_at_kit']['gap']:.2f})")
        lines.append(f"| {d['id']} | {d.get('row_v_gap')} | {fl} | {cell('bench')} | {cell('held')} |")
    print("\n".join(lines))


def main(argv):
    if not argv: print(__doc__); return
    get = lambda f, dflt=None: argv[argv.index(f) + 1] if f in argv else dflt
    params = json.load(open(get("--params"))) if get("--params") else None
    if argv[0] == "measure": measure(argv[1], params, get("--src-bench"), get("--src-held"))
    elif argv[0] == "rewear": rewear(argv[1], argv[2], params)
    elif argv[0] == "table": table()
    else: print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
