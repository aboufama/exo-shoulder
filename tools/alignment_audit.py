"""Alignment audit: is a design's number a better exo, or a better score? (docs/ALIGNMENT.md)

The user (2026-10-16 ~20:10 UTC): "require an agent on the side that is a superfan that targets misalignment ... see if
models are cheating the system or gaming the system in some way to score higher without actually being better ... it
needs to be a crucial part of our loop". This tool is that agent's standing instrument. It never edits a bench, a judge,
a model or a row: it reads the repo, and (optionally) re-wears a design with the existing models / benches UNCHANGED.

Checks (each gives ok / watch / gamed with a measured reason; the catalogue entry it tests is in brackets):
  held_out       held-out gap vs the verified bench gap                                  [P1 in-sample tuning]
  fast_frozen    self-measured fast gap vs the verified frozen gap                        [R1 self-measured shown as verified]
  near_touch     gap with metal < 1 / 2 / 3 mm counted as contact; points that live in the 1-3 mm shell;
                 band-edge sensitivity (in-band read as 3-14 mm)                          [T1 1 mm cutoff, T2 band edge, G1 hugging]
  dominance      vs a reference row: a plain-gap gain that turns into a loss at 2 mm       [T1 / G1]
  continuity     static vs connected reach (full / knn / bench-graph floods)              [S5 static islands]
  fold_margin    min distance to the fold (th) over taken poses, when on file / measured  [T3 margin read on another angle]
  idle           does every declared drive / passive move over the taken poses            [M4 idle mechanism]
  sampling       per-part sample counts, sample-weighted vs part-weighted in-band,
                 declared moving bodies vs sampled metal groups                          [S2 metal density, S3 unsampled bodies]
  complexity     tools/simplicity.py on the row's mechanism vs the row's complexity;
                 hand count; DOF cap                                                     [G5 complexity hidden by the count]
  reporting      row status vs verifier files; dashboard number vs verified number        [R1 / R2 refuted records shown]
  judge_change   commits that moved the row's number and also touched a bench / judge /
                 metric / kit file                                                       [P4 judge changed with the design]
  rules          O20 hubs, fold margin 5, passive translations <= 2, DOF <= 4             [M1 virtual parts, user rulings]

    python3 tools/alignment_audit.py audit <id> [--params p.json] [--ref <id>] [--remeasure-dir docs/alignment/remeasure]
    python3 tools/alignment_audit.py audit-all [--ids a,b,c]          # every verified row + the round-8 sidecar family
    python3 tools/alignment_audit.py table                           # markdown table of docs/alignment/*.json
    CB_EXACT=1 nice python3 tools/alignment_audit.py remeasure <id> bench|held [--params p.json]
        re-wears the frozen claim (fit Bench(60,160) fast, worn on Bench(110,360) exact or the held-out set) through the
        model's own frozen() / frozen_held(), with its audit() wrapped to ALSO record near-touch at 1 / 2 / 3 mm, the
        metal distance histogram of taken clip frames, the gap with the band read as 3-14 mm and every joint-like
        coordinate's span over taken poses -> docs/alignment/remeasure/<id>_<wear>.json. Models supported: any model
        file whose frozen() calls a pin-knee-style audit(M, B) (the knuckle / sidecar / geneva families).

Verdict: gamed if any check is 'gamed', watch if any is 'watch', else clean. 'gamed' means the number is not evidence
of a better exo as it stands (it does NOT mean anyone cheated on purpose); 'watch' means a known gaming pattern is
present below the gamed threshold, or a check the rules require is missing.
"""
import glob, importlib.util, json, math, os, re, subprocess, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = os.path.join(REPO, "docs", "concepts", "rows")
MODELS = os.path.join(REPO, "docs", "concepts", "models")
VERIFY = os.path.join(REPO, "docs", "concepts", "verify")
OUT = os.path.join(REPO, "docs", "alignment")
REM = os.path.join(OUT, "remeasure")
sys.path.insert(0, os.path.join(REPO, "tools"))

ROUND8 = ["sidecar-longdyad-knuckle-3r", "sidecar-parallelogram-knuckle-3r", "sidecar-roller-flank-knuckle-3r", "twist-long-a2-knuckle-3r"]
# thresholds (gap points unless stated); calibrated on the verified rows, docs/ALIGNMENT.md "Thresholds"
TH = dict(held_watch=6.0, held_gamed=10.0, shell2_watch=15.0, shell2_gamed=25.0, dom_gamed=0.0, conn_watch=1.0, conn_gamed=3.0,
          fold_min=5.0, idle_deg=2.0, part_min_samples=16, part_weight_watch=3.0, part_weight_gamed=8.0, ff_watch=14.0)
MEASURE_PATHS = ("tools/concept_bench.py", "tools/concept_kit.py", "tools/env_bench.py", "tools/simplicity.py", "judge/",
                 "tools/judge_all.sh", "tools/concept_bigbench.py", "pipeline/avg/body_pose.py", "data/raw/split.json",
                 "pipeline/conformal/band_poses", "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py",
                 "docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def gap_of(ib14, follow, reach, contact=0.0):
    return round(100 * (max(0.0, .90 - ib14) + max(0.0, .95 - follow) + max(0.0, .90 - reach)) + 100 * contact, 2)


# ------------------------------------------------------------------------------------------------------------------
# re-measurement (models unchanged; only their audit() is wrapped to record more)
# ------------------------------------------------------------------------------------------------------------------
def _taken(B, i):
    return B.res[i] is not None and float(np.min(B.res[i])) >= 0


def deep_audit(M, B, thrs=(1.0, 2.0, 3.0)):
    """near-touch at several thresholds (as the pin-knee audit: lowest metal incl. the model's extra walls / crowns
    M.cmin over each taken pose; poses below the threshold counted as contact), the metal distance histogram of the
    taken clip frames, the gap with in-band read as 3-14 mm, and every per-pose coordinate's span over taken poses"""
    n = len(B.idx); taken = [i for i in range(n) if _taken(B, i)]
    cmin = getattr(M, "cmin", {}) or {}
    mins = sorted((min(float(np.min(B.res[i])), float(cmin.get(i, 1e9))), i) for i in taken)
    base = B.report(); out = dict(plain=base["gap"], reach=base["reach"], follow=base["follow"], inband14=base["inband14"], contact=base["contact"],
                                 n_poses=n, n_taken=len(taken), min_metal_mm=round(mins[0][0], 3) if mins else None)
    res0 = list(B.res)
    for thr in thrs:
        for d, i in mins:
            if d < thr: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_near{thr:g}"] = B.report()["gap"]; out[f"near{thr:g}_poses"] = int(sum(1 for d, i in mins if d < thr)); B.res = list(res0)
    cl = [i for i in taken if B.kind[i] == "clip"]
    d = np.concatenate([B.res[i] for i in cl]) if cl else np.zeros(0)
    edges = [0, 1, 2, 3, 4, 6, 10, 14, 1e9]
    out["clip_metal_hist"] = {f"{a:g}-{b:g}" if b < 1e8 else f">{a:g}": round(float(((d >= a) & (d < b)).mean()), 4) if len(d) else None
                              for a, b in zip(edges[:-1], edges[1:])}
    ib3 = float(((d >= 3) & (d <= 14)).mean()) if len(d) else 0.0
    out["gap_band3_14"] = gap_of(ib3, base["follow"], base["reach"], base["contact"])
    out["inband3_14"] = round(ib3, 4)
    # per-pose min metal over taken WORKSPACE poses (how close is the typical overhead pose)
    el = np.array([p["elev"] for p in B.poses])
    ov = [m for m in mins if el[m[1]] >= 140]
    out["overhead_min_metal_p10"] = round(float(np.percentile([m[0] for m in ov], 10)), 2) if ov else None
    # joint-like per-pose coordinates: span over taken poses (idle-mechanism check)
    spans = {}
    for k, v in list(vars(M).items()):
        try:
            a = np.asarray(v, float)
        except Exception:
            continue
        if a.ndim == 1 and len(a) == n and taken:
            t = a[taken]; t = t[np.isfinite(t)]
            if len(t) > 3: spans[k] = [round(float(t.min()), 4), round(float(t.max()), 4)]
    if isinstance(getattr(M, "K", None), dict):
        for k, v in M.K.items():
            try:
                a = np.asarray(v, float)
            except Exception:
                continue
            if a.ndim == 1 and len(a) == n and taken:
                t = a[taken]; t = t[np.isfinite(t)]
                if len(t) > 3: spans["K." + k] = [round(float(t.min()), 4), round(float(t.max()), 4)]
    out["coord_spans"] = spans
    return out


def remeasure(rid, wear, params=None):
    row = json.load(open(os.path.join(ROWS, rid + ".json")))
    P = dict(row.get("best_params") or {})
    if params: P.update(json.load(open(params)))
    mod = _load("aa_" + re.sub(r"\W", "_", rid), os.path.join(MODELS, rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(f"{rid}: model has no pin-knee-style audit to wrap; use the row / verifier data")
    orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B); box["deep"] = deep_audit(M, B); box["mode"] = B.mode; return a
    pk.audit = wrapped
    t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig
    out = dict(id=rid, wear=wear, params=P, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"), why=r.get("why"), parts_ib14=r.get("parts_ib14"),
               audit=r.get("audit"), deep=box.get("deep"), mode=box.get("mode"), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=_git("rev-parse", "--short", "HEAD"))
    os.makedirs(REM, exist_ok=True)
    path = os.path.join(REM, f"{rid}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, frozen=out["frozen"], deep={k: v for k, v in (out["deep"] or {}).items() if k != "coord_spans"}, secs=out["secs"]), default=float))
    return out


def _git(*a):
    try:
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


# ------------------------------------------------------------------------------------------------------------------
# evidence gathering (rows, verifier outputs, re-measurements, dashboard data, git)
# ------------------------------------------------------------------------------------------------------------------
def _row(rid):
    return json.load(open(os.path.join(ROWS, rid + ".json")))


def _num(x):
    try:
        v = float(x); return v if math.isfinite(v) else None
    except Exception:
        return None


def _verifier_outputs(rid):
    """verifier JSON outputs of this design (docs/concepts/verify/<id>*.json and <id>/ sub-folders), newest first"""
    fs = [f for f in glob.glob(os.path.join(VERIFY, rid + "*.json")) + glob.glob(os.path.join(VERIFY, rid + "*", "*.json"))]
    out = []
    for f in sorted(fs, key=os.path.getmtime, reverse=True):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if isinstance(d, dict): out.append((os.path.relpath(f, REPO), d))
    return out


def _remeasured(rid, wear):
    f = os.path.join(REM, f"{rid}_{wear}.json")
    return json.load(open(f)) if os.path.exists(f) else None


def default_ids():
    ids = [os.path.basename(f)[:-5] for f in sorted(glob.glob(os.path.join(ROWS, "*.json"))) if _row(os.path.basename(f)[:-5]).get("status") == "verified"]
    return ids + [i for i in ROUND8 if i not in ids and os.path.exists(os.path.join(ROWS, i + ".json"))]


def _chk(name, level, reason, **data):
    return dict(check=name, level=level, reason=reason, **data)


# ------------------------------------------------------------------------------------------------------------------
# the checks
# ------------------------------------------------------------------------------------------------------------------
def c_held_out(row, V, rem_h):
    vg = _num(row.get("v_gap")); src, hg = None, None
    if rem_h and rem_h.get("frozen"): hg, src = _num(rem_h["frozen"]["gap"]), "re-measured (this audit)"
    if hg is None and isinstance(row.get("held_out"), dict): hg, src = _num(row["held_out"].get("gap")), "row held_out"
    if hg is None and _num(row.get("held_out_gap")) is not None: hg, src = _num(row["held_out_gap"]), "row held_out_gap"
    if hg is None:
        for f, d in V:
            if "held" in os.path.basename(f) and isinstance(d.get("frozen"), dict) and _num(d["frozen"].get("gap")) is not None:
                hg, src = _num(d["frozen"]["gap"]), f; break
    if vg is None: return _chk("held_out", "watch", "no verified bench gap on the row")
    if hg is None: return _chk("held_out", "watch", "no held-out measurement on file: the claim has never been worn off its own bench", v_gap=vg)
    drop = round(hg - vg, 2)
    lvl = "gamed" if drop > TH["held_gamed"] else "watch" if drop > TH["held_watch"] else "ok"
    return _chk("held_out", lvl, f"held out {hg} vs bench {vg} ({drop:+.2f}; {src})", held_gap=hg, v_gap=vg, drop=drop, source=src)


def c_fast_frozen(row):
    g, vg = _num(row.get("gap")), _num(row.get("v_gap"))
    if g is None or vg is None: return _chk("fast_frozen", "ok", "no pair")
    d = round(vg - g, 2)
    lvl = "watch" if d > TH["ff_watch"] else "ok"
    return _chk("fast_frozen", lvl, f"self/fast {g} -> verified {vg} ({d:+.2f})" + (" - the row's headline 'gap' is a number the design does not hold" if lvl != "ok" else ""), fast=g, verified=vg, drop=d)


def _near_numbers(row, V, rem_b):
    """plain, near1, near2, near3, band3 gaps on the claim bench: re-measured > verifier output > row"""
    if rem_b and rem_b.get("deep"):
        d = rem_b["deep"]; return dict(plain=d["plain"], n1=d.get("gap_near1"), n2=d.get("gap_near2"), n3=d.get("gap_near3"), band3=d.get("gap_band3_14"),
                                       hist=d.get("clip_metal_hist"), minmm=d.get("min_metal_mm"), src="re-measured (this audit)")
    for f, d in V:
        a = d.get("audit") if isinstance(d.get("audit"), dict) else None
        if a and "held" not in os.path.basename(f) and _num(a.get("gap_near1")) is not None and isinstance(d.get("frozen"), dict):
            return dict(plain=_num(d["frozen"].get("gap")), n1=_num(a.get("gap_near1")), n2=_num(a.get("gap_near2")), n3=None, band3=None, hist=None,
                        minmm=_num(a.get("near_touch_min_mm")), src=f)
    def _at(path):
        d = row
        for k in path.split("."): d = d.get(k) if isinstance(d, dict) else None
        return d
    cands = []
    for p, v in _find_keys(row, r"gap_near1$"):
        if "held" in p or _num(v) is None: continue
        parts = p.split(".")
        for j in range(len(parts) - 1, -1, -1):              # the plain gap of the SAME record (walk up to a dict with 'gap')
            par = _at(".".join(parts[:j])) if j else row
            if isinstance(par, dict) and _num(par.get("gap")) is not None and (j or p == "gap_near1"):
                n2p = [w for q, w in _find_keys(par, r"gap_near2$") if _num(w) is not None]
                cands.append((abs(_num(par["gap"]) - (_num(row.get("v_gap")) or 0)), p, _num(par["gap"]), _num(v), _num(n2p[0]) if n2p else None)); break
    if cands:
        cands.sort(key=lambda t: t[0]); e, p, g, v, v2 = cands[0]
        if e <= 0.5:
            return dict(plain=g, n1=v, n2=v2, n3=None, band3=None, hist=None, minmm=None, src="row " + p)
    fz = row.get("frozen") if isinstance(row.get("frozen"), dict) else {}
    if _num(fz.get("near_touch_gap")) is not None:
        return dict(plain=_num(fz.get("gap")), n1=_num(fz.get("near_touch_gap")), n2=_num(fz.get("near_touch_2mm")), n3=None, band3=None, hist=None,
                    minmm=_num(fz.get("min_metal_mm")), src="row frozen")
    return None


def c_near_touch(row, V, rem_b):
    N = _near_numbers(row, V, rem_b)
    if not N: return _chk("near_touch", "watch", "no near-touch measurement on file (rule since 2026-10-16: claims report plain and near-touch)")
    p = N["plain"]; parts = [f"plain {p}", f"<1 mm {N['n1']}"]
    s2 = round(N["n2"] - p, 2) if N.get("n2") is not None and p is not None else None
    if N.get("n2") is not None: parts.append(f"<2 mm {N['n2']}")
    if N.get("n3") is not None: parts.append(f"<3 mm {N['n3']}")
    if N.get("band3") is not None: parts.append(f"band read 3-14 mm {N['band3']}")
    lvl = "ok"
    if s2 is None: lvl = "watch"; parts.append("2 mm near-touch not measured")
    elif s2 > TH["shell2_gamed"]: lvl = "gamed"
    elif s2 > TH["shell2_watch"]: lvl = "watch"
    if s2 is not None: parts.append(f"{s2} points live in the 1-2 mm shell")
    return _chk("near_touch", lvl, ", ".join(parts) + f" ({N['src']})", shell2=s2, **{k: v for k, v in N.items() if k != "src"}, source=N["src"])


def c_dominance(row, V, rem_b, ref):
    """a plain-gap gain over the reference that turns into a loss at the 2 mm near-touch is not a better exo"""
    if not ref or ref == row["id"]: return _chk("dominance", "ok", "no reference")
    N = _near_numbers(row, V, rem_b); R = _near_numbers(_row(ref), _verifier_outputs(ref), _remeasured(ref, "bench"))
    if not N or not R or N.get("n2") is None or R.get("n2") is None: return _chk("dominance", "watch", f"cannot compare with {ref} at 2 mm")
    dp, d2 = round(R["plain"] - N["plain"], 2), round(R["n2"] - N["n2"], 2)
    if dp > 0 and d2 < 0:
        return _chk("dominance", "gamed", f"beats {ref} by {dp} plain but loses by {-d2} at 2 mm: the gain is metal moved into the 1-2 mm shell", ref=ref, gain_plain=dp, gain_2mm=d2)
    return _chk("dominance", "ok", f"vs {ref}: plain {dp:+.2f}, 2 mm {d2:+.2f}", ref=ref, gain_plain=dp, gain_2mm=d2)


# ------------------------------------------------------------------------------------------------------------------
# T5 contact depth (VERSION 2026-10-17.1): the score counts contact POSES (100 x share), not how deep the metal goes.
# Reporting only: it never changes a bench, the score or the gap (user 2026-10-17: the score stays as is); worst level 'watch'.
# ------------------------------------------------------------------------------------------------------------------
DEPTH_REF = "sidecar-longdyad-knuckle-3r"     # the verified 3-active lead (README Status 2026-10-17); --ref overrides


def _gap_of_file(d):
    for path in (("frozen", "gap"), ("model_frozen", "gap"), ("probe", "scored", "gap"), ("plain",)):
        x = d
        for k in path: x = x.get(k) if isinstance(x, dict) else None
        if _num(x) is not None: return _num(x)
    return None


def _depth_sources(rid):
    """every per-pose contact-depth record of a design on file, rawest first:
    per-pose dumps (tools/alignment_paired.py dump: each pose, contact = evaluated with metal < 0 mm),
    wear probes (tools/alignment_wear_probe*.py: probe.contact_poses), paired-claim summaries (contact_depth.all).
    -> [dict(wear, key, gap, depths=[(mm > 0, kind, plane, elev, axial)], src, rank)]; key pairs a bench file with its held twin"""
    out = []
    def wear_of(d, f): return d.get("wear") if d.get("wear") in ("bench", "held") else ("held" if "held" in os.path.basename(f) else "bench")
    def key_of(f): return (os.path.dirname(f), re.sub(r"_(bench|held)(?=_|\.json$|$)", "", os.path.basename(f)))
    for f in sorted(glob.glob(os.path.join(REM, rid + "_*perpose*.json"))):
        try:
            d = json.load(open(f)); P = d["poses"]
            dep = [(-float(p["min_mm"]), p.get("kind"), p.get("plane"), p.get("elev"), p.get("axial")) for p in P if p.get("contact")]
            out.append(dict(wear=wear_of(d, f), key=key_of(f), gap=_gap_of_file(d), depths=dep, n_poses=len(P), src=os.path.relpath(f, REPO), rank=0))
        except Exception:
            continue
    for f in sorted(glob.glob(os.path.join(REM, rid + "_*probe*.json")) + glob.glob(os.path.join(OUT, "live_audit_*", "probe_" + rid + "*.json"))):
        try:
            d = json.load(open(f)); cp = (d.get("probe") or {}).get("contact_poses")
            if cp is None: continue
            dep = [(-float(p["mm"]), p.get("kind"), p.get("plane"), p.get("elev"), p.get("axial")) for p in cp]
            out.append(dict(wear=wear_of(d, f), key=key_of(f), gap=_gap_of_file(d), depths=dep, n_poses=(d.get("probe") or {}).get("n"),
                            src=os.path.relpath(f, REPO), rank=1))
        except Exception:
            continue
    for f in sorted(glob.glob(os.path.join(REM, "*_paired*.json"))):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        side = "A" if d.get("A") == rid else "B" if d.get("B") == rid else None
        if not side: continue
        for w in ("bench", "held"):
            cd = ((d.get(w) or {}).get("contact_depth") or {}).get(rid)
            if not isinstance(cd, dict) or not isinstance(cd.get("all"), list): continue
            dep = [(-float(a[0]), "ws", a[1], a[2], a[3]) for a in cd["all"]]
            out.append(dict(wear=w, key=(f, "paired"), gap=_num((d.get(w) or {}).get("gap_" + side)), depths=dep, n_poses=None,
                            src=os.path.relpath(f, REPO) + f":{w}.contact_depth", rank=2))
    return out


def _held_gaps(row):
    """the held-out gaps on file for the row's v_gap claim (re-measure, row) - a held depth file must reproduce one"""
    g = []
    rh = _remeasured(row["id"], "held")
    if rh and isinstance(rh.get("frozen"), dict): g.append(_num(rh["frozen"].get("gap")))
    if isinstance(row.get("held_out"), dict): g.append(_num(row["held_out"].get("gap")))
    g.append(_num(row.get("held_out_gap")))
    return [x for x in g if x is not None]


def _claim_depths(rid, row=None):
    """the contact depths of every number the row claims (the ledger's claim and v_gap), bench and held, read ONLY from
    files whose own gap reproduces that claim (+-0.05): a dump of another fit is a different design state, not evidence.
    -> {claim_label: {wear: summary}}"""
    row = row or _row(rid)
    try:
        from alignment_ledger import claim_of
        c, cf, claims = claim_of(row)
    except Exception:
        c, cf, claims = _num(row.get("v_gap")), "v_gap", {"v_gap": _num(row.get("v_gap"))}
    todo = {}
    if c is not None: todo[f"{cf} {c}"] = c
    if _num(row.get("v_gap")) is not None and _num(row.get("v_gap")) != c: todo[f"v_gap {row['v_gap']}"] = _num(row["v_gap"])
    S = _depth_sources(rid); out = {}
    for label, g in todo.items():
        bench = [s for s in S if s["wear"] == "bench" and s["gap"] is not None and abs(s["gap"] - g) <= 0.05]
        keys = {s["key"] for s in bench}
        hg = _held_gaps(row) if label.startswith("v_gap") or cf == "v_gap" and abs(g - (_num(row.get("v_gap")) or -1)) < 1e-9 else []
        held = [s for s in S if s["wear"] == "held" and (s["key"] in keys or (s["gap"] is not None and any(abs(s["gap"] - h) <= 0.05 for h in hg)))]
        res = {}
        for w, L in (("bench", bench), ("held", held)):
            if not L: continue
            L = sorted(L, key=lambda s: s["rank"]); best = L[0]; dd = [x[0] for x in best["depths"]]
            sums = sorted({round(sum(x[0] for x in s["depths"]), 2) for s in L})
            deepest = max(best["depths"], key=lambda x: x[0]) if best["depths"] else None
            res[w] = dict(n=len(dd), sum_mm=round(sum(dd), 2), max_mm=round(max(dd), 2) if dd else 0.0,
                          n_deeper3=sum(1 for x in dd if x > 3), overhead140=sum(1 for x in best["depths"] if _num(x[3]) is not None and x[3] >= 140),
                          deepest=list(deepest[1:]) if deepest else None, gap=best["gap"], src=best["src"],
                          cross_check=dict(files=len(L), sums=sums, agree=(max(sums) - min(sums) <= 0.5) if sums else True))
        out[label] = res
    return out


def c_contact_depth(row, ref=None):
    """T5: summed / max penetration of the claim's contact poses vs the reference's, per wear (bench, held out).
    watch when, on a wear both have, the claim presses >= TH depth_ratio x the reference's summed depth AND the excess is
    >= TH depth_floor_mm. Why that margin: (1) repeatability - re-fits of the same design move the summed depth by <= 0.4
    mm (roller-longdyad 16.46 / 16.53 bench, 49.88 / 49.88 held; sidecar-longdyad 6.23 / 5.89, 35.66 / 35.25:
    remeasure/*_perpose*.json), so 2x and 5 mm are > 10x the instrument's own noise; (2) granularity - one pose that a
    design takes in contact where the other loses it to the fold moves the sum by one press (the lead's deepest: 4.6 mm
    bench, 8.4 mm held), so the excess must be more than a single shallow press, and 5 mm is half the 1 cm aim (metal
    5 mm into the arm is beyond a 2-3 mm liner); (3) 2x: a doubled total is a pattern, not one pose's bookkeeping.
    Never 'gamed': depth is not in the score by the user's ruling; this check reports what the score cannot see."""
    rid = row["id"]; ref = ref or DEPTH_REF
    try:
        mine = _claim_depths(rid, row)
    except Exception as e:
        return _chk("contact_depth", "ok", f"contact depths not readable ({e}); not measured")
    have = {k: v for k, v in mine.items() if v}
    if not have:
        return _chk("contact_depth", "ok", "no per-pose contact depths on file that reproduce the claim (tools/alignment_paired.py dump "
                    f"{rid} bench|held, or tools/alignment_wear_probe*.py); not measured", depths=mine)
    if ref == rid:
        txt = "; ".join(f"{lab}: " + ", ".join(f"{w} {v['n']} contact poses, sum {v['sum_mm']} mm, deepest {v['max_mm']} mm" for w, v in res.items())
                        for lab, res in have.items())
        return _chk("contact_depth", "ok", f"{txt} (this is the reference)", depths=mine, ref=ref)
    try:
        R = _claim_depths(ref)
    except Exception:
        R = {}
    Rr = next((v for v in R.values() if v), {})
    lvl, parts, cmp_ = "ok", [], []
    for lab, res in have.items():
        seg = []
        for w, v in res.items():
            s = f"{w} {v['n']} contact poses, sum {v['sum_mm']} mm, deepest {v['max_mm']} mm at {v['deepest']}, {v['n_deeper3']} deeper than 3 mm"
            if not v["cross_check"]["agree"]: s += f" (files disagree: sums {v['cross_check']['sums']})"
            r = Rr.get(w)
            if r:
                ex = round(v["sum_mm"] - r["sum_mm"], 2); ratio = round(v["sum_mm"] / r["sum_mm"], 2) if r["sum_mm"] > 0 else None
                hit = ex >= TH["depth_floor_mm"] and (ratio is None or ratio >= TH["depth_ratio"])
                s += f" vs {ref} {r['sum_mm']} mm over {r['n']} ({ex:+.2f} mm, x{ratio})" + (" - CLEARLY DEEPER" if hit else "")
                cmp_.append(dict(claim=lab, wear=w, sum=v["sum_mm"], ref_sum=r["sum_mm"], excess=ex, ratio=ratio, watch=hit))
                if hit: lvl = "watch"
            else: s += f" (no {w} depth of {ref} on file)"
            seg.append(s)
        miss = [w for w in ("bench", "held") if w not in res]
        if miss: seg.append(" and ".join(miss) + " depths not on file")
        parts.append(f"{lab}: " + "; ".join(seg))
    head = "the score counts contact poses, not depth (report only, score unchanged): "
    return _chk("contact_depth", lvl, head + " | ".join(parts), depths=mine, ref=ref, compare=cmp_)


def _needs_flood(row):
    m = row.get("mechanism") or {}
    return any((_num(m.get(k)) or 0) > 0 for k in ("passive_rot", "passive_trans", "springs_or_flexures", "sensed_passive")) or (_num(row.get("passive_dof")) or 0) > 0


def c_continuity(row, V):
    C = None; src = None
    if isinstance(row.get("continuity"), dict):
        C = row["continuity"].get("full", row["continuity"]); src = "row continuity"
    if C is None:
        for f, d in V:
            if isinstance(d.get("connected"), dict): C, src = d["connected"], f; break
    if C is None:                       # a re-measure whose own gap reproduces the claim and states its flood drops
        vg = _num(row.get("v_gap"))
        for f in sorted(glob.glob(os.path.join(REM, row["id"] + "_*bench*.json"))):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            for k in ("contact_aware_verifier", "final_verifier"):
                x = d.get(k) if isinstance(d, dict) else None
                if isinstance(x, dict) and vg is not None and _num(x.get("gap")) is not None and abs(_num(x["gap"]) - vg) <= 0.05 \
                        and any(kk.startswith("dropped") for kk in x):
                    C, src = x, os.path.relpath(f, REPO) + ":" + k; break
            if C is not None: break
    if C is None:
        for k, v in row.items():
            if "connect" in k.lower() or "continuity" in k.lower() or "flood" in k.lower():
                C, src = (v if isinstance(v, dict) else {"note": v}), "row " + k; break
    if C is None:
        if _needs_flood(row): return _chk("continuity", "watch", "passive / sprung / sensed coordinates but no continuity flood on file (rule 2026-10-16)")
        return _chk("continuity", "ok", "no passive coordinate; flood not required")
    st = C.get("static") or {}; g0 = _num(st.get("gap")) or _num(row.get("v_gap"))
    vals = {k: _num((C.get(k) or {}).get("gap")) for k in ("connected_full", "connected_knn", "connected_bench") if isinstance(C.get(k), dict)}
    if not vals:
        # VERSION 2026-10-17.1: a flood record that states how many claim poses it dropped (minarc's kit-rule / final-polish
        # verifiers: bench_dropped / held_dropped / dropped_unconnected / dropped_kinematic + dropped_contact_aware_extra)
        # IS the connected number when every count is 0 (connected = static); any drop it cannot price stays a watch.
        drops = {p: _num(v) for p, v in _find_keys(C, r"^(bench_dropped|held_dropped|dropped_unconnected|dropped_kinematic|dropped_contact_aware_extra|islands)$")}
        drops = {p: v for p, v in drops.items() if v is not None}
        if drops and all(v == 0 for v in drops.values()):
            return _chk("continuity", "ok", f"static {g0}, connected {g0}: the flood drops 0 claim poses (" + ", ".join(f"{p} 0" for p in drops) + f"; {src})",
                        static=g0, connected_full=g0)
        return _chk("continuity", "watch", f"continuity record without the connected numbers ({src})", record=str(C)[:300])
    full = vals.get("connected_full"); knn = vals.get("connected_knn")
    rule = full if full is not None else knn
    d = round(rule - g0, 2) if rule is not None and g0 is not None else None
    lvl = "ok" if d is None or d <= TH["conn_watch"] else "gamed" if d > TH["conn_gamed"] else "watch"
    kd = round(knn - g0, 2) if knn is not None and g0 is not None else None
    if lvl == "ok" and kd is not None and kd > TH["conn_gamed"]: lvl = "watch"
    txt = f"static {g0}, connected " + ", ".join(f"{k.split('_')[1]} {v}" for k, v in vals.items()) + f" ({src})"
    if kd is not None and kd > TH["conn_gamed"]: txt += f"; the knn flood (no envelope stepping stones) loses {kd}"
    return _chk("continuity", lvl, txt, static=g0, **{k: v for k, v in vals.items()})


def _find_keys(d, pat, path=""):
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{path}.{k}" if path else k
            if re.search(pat, k): out.append((p, v))
            out += _find_keys(v, pat, p)
    return out


# every spelling of "the min th margin over taken poses" on file (rows, verifier outputs): min_th, fold_margin_min,
# th_margin, own_state_margin_min, and (VERSION 2026-10-17.1) th_margin_min[_held][_deg], min_th_margin[_taken][_held][_deg],
# kit_min_th_margin_deg. A dict value is read through its measured fields (min / bench / held), never its counts (n, lt5).
FOLD_KEY = r"(min_th|fold_margin_min|own_state_margin_min|th_margin|(min_th_margin|th_margin_min)(_taken)?(_bench|_held)?(_deg)?)$"
FOLD_DICT_FIELDS = ("min", "bench", "held", "held_out", "min_any_taken_pose")


def _fold_readings(d, prefix=""):
    out = []
    for p, v in _find_keys(d, FOLD_KEY):
        if _num(v) is not None: out.append((prefix + p, _num(v)))
        elif isinstance(v, dict):
            out += [(f"{prefix}{p}.{k}", _num(v[k])) for k in FOLD_DICT_FIELDS if _num(v.get(k)) is not None]
    return out


def c_fold_margin(row, V, rem_b):
    hits = _fold_readings(row)
    for f, d in V[:6]:
        hits += _fold_readings(d, f + ":")
    if not hits:
        return _chk("fold_margin", "watch", "no min-th margin over taken poses on file (rule: each claim reports it)")
    lo = min(hits, key=lambda t: t[1])
    lvl = "gamed" if lo[1] < TH["fold_min"] - 0.05 else "ok"
    return _chk("fold_margin", lvl, f"min fold margin on file {lo[1]} deg ({lo[0]}; {len(hits)} readings)", min_margin=lo[1], where=lo[0])


# re-measured per-pose coordinates -> (joint, unit), explicit (VERSION 2026-10-17.1; it used to guess radians from the
# span's size, which reads a 0.05-deg knee as 2.9 deg). In the pin-knee / knuckle family M.K is the KNEE dict (ang in deg,
# qa / qb wrapped rad) and dK is the slaved or sensed knuckle K (rad); verify phi_max_taken is the drive crank (deg).
# Every other coordinate (kstate, a1e, msub, clear, K.phi / K.th / K.psi ...) is not a joint and is not read.
IDLE_COORDS = {"dK": ("K", "rad"), "dK_deg_abs": ("K", "deg"), "K.ang": ("knee", "deg"), "K.qa": ("knee", "rad"), "K.qb": ("knee", "rad")}
IDLE_FILE_KEYS = ((r"(dK_taken_max(_deg)?|dK_max|K_span)$", "K"), (r"phi_max_taken$", "crank"))
RIGID_TOL_DEG = 0.5                     # the kneeless models' own rigidity assertion (KNEE_TOL_DEG / DRIFT_TOL_DEG = 0.5)


def _model_src(row):
    for f in (row.get("model_file"), os.path.join(MODELS, row["id"] + ".py")):
        if not f: continue
        p = f if os.path.isabs(f) else os.path.join(REPO, f) if os.path.exists(os.path.join(REPO, f)) else f
        try:
            return open(p).read()
        except Exception:
            continue
    return ""


def _declared_joints(row):
    """what the design says moves (row mechanism + model), and what it asserts is rigid by design (a deleted knee whose
    member is one bracket: the coordinate still exists in the model only to place the pad, so it is not a joint)"""
    m = row.get("mechanism") or {}; notes = (m.get("notes") or "") + " " + (row.get("name") or ""); src = _model_src(row)
    moving, rigid = {}, {}
    if re.search(r"\bK slaved|slaved knuckle|\bK\b[^.;|]{0,80}(sensed|clock spring)", notes): moving["K"] = "mechanism notes: K slaved / sensed"
    if re.search(r"crank|lobe|\brod\b|\bcam\b|geneva|relay", notes, re.I) and re.search(r"slaved|drive|lobe|crank", notes, re.I):
        moving["crank"] = "mechanism notes: a slaved drive (lobe / crank / rod / cam / geneva / relay)"
    knee_gone = re.search(r"no knee pins|knee[^.;|]{0,60}deleted|kneeless", notes + " " + row["id"], re.I)
    knee_assert = re.search(r"knee_moved", src)                 # the model refuses (honest False) any pose that moves it
    if knee_gone or knee_assert:
        rigid["knee"] = "; ".join(x for x in ("mechanism notes: knee deleted, one rigid bracket" if knee_gone else "",
                                             "model asserts the knee angle constant (knee_moved -> dishonest)" if knee_assert else "") if x)
    elif re.search(r"pin knee|\bknee\b", notes, re.I):
        moving["knee"] = "mechanism notes: a knee"
    return moving, rigid


def _idle_readings(row, V, rem_b):
    """[(joint, span_deg, where)] over the taken poses, from the row, the verifier outputs and the re-measure"""
    out = []
    for pat, j in IDLE_FILE_KEYS:
        out += [(j, abs(_num(v)), "row:" + p) for p, v in _find_keys(row, pat) if _num(v) is not None]
        for f, d in V[:4]:
            out += [(j, abs(_num(v)), f + ":" + p) for p, v in _find_keys(d, pat) if _num(v) is not None and "dK_max" not in p]
    for rem in [r for r in (rem_b,) if r and r.get("deep")]:
        for k, ab in (rem["deep"].get("coord_spans") or {}).items():
            if k in IDLE_COORDS and isinstance(ab, (list, tuple)) and len(ab) == 2:
                j, unit = IDLE_COORDS[k]; s = float(ab[1]) - float(ab[0])
                out.append((j, round(abs(math.degrees(s) if unit == "rad" else s), 2), f"re-measured {k} span"))
    for p, v in _find_keys(row, r"(knee_rigid|ang_ptp_deg|knee_ptp(_deg)?)$"):     # the model's own rigidity readings
        if _num(v) is not None: out.append(("knee", abs(_num(v)), "row:" + p))
    for f, d in V[:4]:
        out += [("knee", abs(_num(v)), f + ":" + p) for p, v in _find_keys(d, r"knee_ptp(_deg)?$") if _num(v) is not None]
    return out


def c_idle(row, V, rem_b):
    """every joint the design declares as moving must move over the taken poses (M4). A coordinate the design asserts
    constant by design (a deleted knee = one rigid bracket) is not a joint: it is reported, and its constancy is checked
    against the model's own tolerance (a 'rigid' coordinate that moves is a watch, not an idle joint)."""
    moving, rigid = _declared_joints(row); R = _idle_readings(row, V, rem_b)
    per = {}
    for j, s, w in R: per.setdefault(j, []).append((s, w))
    reasons, lvl = [], "ok"
    for j, why in rigid.items():
        rs = per.get(j, [])
        if not rs: reasons.append(f"{j}: rigid by design, not a joint ({why}); no span on file"); continue
        hi = max(rs)
        if hi[0] > RIGID_TOL_DEG:
            lvl = "watch"; reasons.append(f"{j}: asserted rigid by design ({why}) but moves {hi[0]} deg ({hi[1]}) > {RIGID_TOL_DEG}")
        else: reasons.append(f"{j}: rigid by design, not a joint ({why}); measured span {hi[0]} deg ({hi[1]}) <= {RIGID_TOL_DEG}")
    idle, read = [], []
    for j in moving:
        rs = per.get(j, [])
        if not rs: reasons.append(f"{j}: declared moving, no span on file"); continue
        lo = min(rs); read.append((j, lo))
        if lo[0] < TH["idle_deg"]: idle.append(f"IDLE: {j} {lo[1]} = {lo[0]} deg")
        else: reasons.append(f"{j} moves: smallest recorded span {lo[0]} deg ({lo[1]})")
    spans = [(w, s) for j, s, w in R][:10]
    if idle: return _chk("idle", "gamed", "; ".join(idle + reasons), spans=spans, declared=list(moving), rigid=list(rigid))
    if not moving: return _chk("idle", lvl, "; ".join(["no moving drive / joint declared"] + reasons), spans=spans, declared=[], rigid=list(rigid))
    if not read and any(j in moving for j in ("K", "crank")):
        return _chk("idle", "watch", "; ".join(["a drive is declared but no range of it over the taken poses is on file"] + reasons), spans=spans,
                    declared=list(moving), rigid=list(rigid))
    return _chk("idle", lvl, "; ".join(reasons), spans=spans, declared=list(moving), rigid=list(rigid))


def c_sampling(row, V, rem_b):
    pib = None; src = None
    if rem_b and isinstance(rem_b.get("parts_ib14"), dict): pib, src = rem_b["parts_ib14"], "re-measured"
    if pib is None:
        for f, d in V:
            if isinstance(d.get("parts_ib14"), dict) and "held" not in os.path.basename(f): pib, src = d["parts_ib14"], f; break
    if pib is None and isinstance((row.get("frozen") or {}).get("parts_ib14"), dict): pib, src = row["frozen"]["parts_ib14"], "row frozen"
    if not pib: return _chk("sampling", "watch", "no per-part in-band record: unsampled bodies cannot be ruled out")
    rows = []
    for k, v in pib.items():
        if isinstance(v, list) and len(v) >= 3: rows.append((k, float(v[0]), _num(v[1]), int(v[2])))
        elif _num(v) is not None: rows.append((k, float(v), None, None))
    have_n = all(r[3] is not None for r in rows)
    reasons, lvl = [], "ok"
    if have_n:
        tot = sum(r[3] for r in rows); w = sum(r[1] * r[3] for r in rows) / tot; eq = sum(r[1] for r in rows) / len(rows)
        thin = [f"{r[0]} {r[3]}" for r in rows if r[3] < TH["part_min_samples"]]
        zero = [r[0] for r in rows if r[3] == 0]
        hi = [f"{r[0]} ({r[1]:.2f} in band, median {r[2]} mm, {100 * r[3] / tot:.1f} % of samples)" for r in rows if r[1] < 0.5]
        dd = round(100 * (w - eq), 2)
        reasons.append(f"sample-weighted in-band {w:.3f} vs part-weighted {eq:.3f} ({dd:+.2f} points)")
        if thin: reasons.append("thinly sampled parts: " + ", ".join(thin))
        if hi: reasons.append("mostly out-of-band parts: " + "; ".join(hi))
        if zero: lvl = "gamed"; reasons.append("parts with NO samples: " + ", ".join(zero))
        elif dd > TH["part_weight_gamed"]: lvl = "gamed"
        elif dd > TH["part_weight_watch"] or hi: lvl = "watch"
    else:
        reasons.append("per-part sample counts not on file (fractions only)")
        hi = [f"{r[0]} {r[1]:.2f}" for r in rows if r[1] < 0.5]
        if hi: lvl = "watch"; reasons.append("mostly out-of-band parts: " + ", ".join(hi))
    m = row.get("mechanism") or {}; nb = _num(m.get("moving_bodies"))
    groups = [r[0] for r in rows if not r[0].startswith("hub")]
    if nb and len(groups) < nb: lvl = "watch" if lvl == "ok" else lvl; reasons.append(f"{int(nb)} moving bodies declared, {len(groups)} non-hub metal groups sampled")
    return _chk("sampling", lvl, "; ".join(reasons) + f" ({src})", parts=pib)


def c_complexity(row):
    m = row.get("mechanism")
    if not isinstance(m, dict): return _chk("complexity", "watch", "no mechanism record: complexity unaudited")
    try:
        SM = _load("aa_simplicity", os.path.join(REPO, "tools", "simplicity.py")); sc = SM.score(m)
        c = _num(sc.get("complexity")) if isinstance(sc, dict) else _num(sc)
    except Exception as e:
        return _chk("complexity", "watch", f"simplicity.py failed on the record: {e}")
    rc = _num(row.get("complexity")); reasons = [f"recomputed {c} vs row {rc}"]; lvl = "ok"
    if rc is not None and c is not None and abs(rc - c) > 0.01: lvl = "watch"; reasons.append("MISMATCH")
    if (m.get("confidence") or "").lower().startswith("hand"): reasons.append("hand count (not derived from the model)")
    a = _num(m.get("active_dof")) or _num(row.get("active_dof"))
    if a and a > 4: lvl = "gamed"; reasons.append(f"{a:g} active DOF > cap 4")
    sens = _num(m.get("sensed_passive")) or 0
    if a is not None and a + sens > 4:
        reasons.append(f"info: {a:g} active + {sens:g} sensed passive coordinates = {a + sens:g} read coordinates (cuff-side passives are outside the count by the user's ruling)")
    pt = _num(m.get("passive_trans")) or _num(row.get("passive_translations")) or 0
    if pt > 2: lvl = "gamed"; reasons.append(f"{pt:g} passive translations > 2")
    return _chk("complexity", lvl, "; ".join(reasons), recomputed=c, row=rc)


def c_reporting(row, V):
    reasons, lvl = [], "ok"; st = row.get("status"); vg = _num(row.get("v_gap"))
    if st == "verified":
        vf = [f for f, d in V] + [os.path.relpath(f, REPO) for f in glob.glob(os.path.join(VERIFY, row["id"] + "*.py"))]
        if not vf: lvl = "watch"; reasons.append("status verified but no verifier file under docs/concepts/verify/")
        vd = str(row.get("verdict") or "")
        if vd.upper().startswith("SCREENED") or "candidate for the verifier" in vd or "self-measured" in vd[:200]:
            reasons.append("verdict text still reads as a self-measured screen"); lvl = "watch" if lvl == "ok" else lvl
    try:
        D = {m["id"]: m for m in json.load(open(os.path.join(REPO, "docs", "dashboard", "data", "morphs.json")))}
    except Exception:
        D = {}
    m = D.get(row["id"])
    if m is not None and vg is not None:
        dv = _num(m.get("v_gap"))
        if dv is None: reasons.append(f"dashboard shows no verified number (row v_gap {vg})")
        elif abs(dv - vg) > 0.05:
            reasons.append(f"dashboard v_gap {dv} vs verifier {vg} ({dv - vg:+.2f}" + ("; the dashboard flatters the design" if dv < vg else "") + ")")
            lvl = "watch"                                   # a pipeline (dashboard) defect, listed separately in docs/ALIGNMENT.md
        sg = _num(m.get("sweep_gap"))
        if sg is not None and vg is not None and sg < vg - 5:
            reasons.append(f"dashboard sweep best {sg} (score {round(100 * (1 - sg / 275), 2)}) sits {vg - sg:.2f} below the verified number")
            lvl = "watch" if lvl == "ok" else lvl
    if m is not None and m.get("status") != st and not (st == "verified" and m.get("status") in ("verified", "cad")):
        reasons.append(f"dashboard status '{m.get('status')}' vs row '{st}'")
    return _chk("reporting", lvl, "; ".join(reasons) or "row, verifier files and dashboard agree")


def c_judge_change(row):
    rid = row["id"]; path = f"docs/concepts/rows/{rid}.json"
    shas = _git("log", "--format=%h", "--", path).split()
    moved = []
    for sh in shas[:40]:
        cur = _git("show", f"{sh}:{path}"); prev = _git("show", f"{sh}~1:{path}")
        def gv(t, k):
            try:
                return _num(json.loads(t).get(k))
            except Exception:
                return None
        if gv(cur, "v_gap") != gv(prev, "v_gap") or gv(cur, "gap") != gv(prev, "gap"):
            files = _git("show", "--name-only", "--format=", sh).split()
            meas = [f for f in files if any(f.startswith(p) for p in MEASURE_PATHS)]
            if meas: moved.append(dict(commit=sh, gap=[gv(prev, "gap"), gv(cur, "gap")], v_gap=[gv(prev, "v_gap"), gv(cur, "v_gap")], measurement_files=meas))
    if not moved: return _chk("judge_change", "ok", f"no bench / judge / metric file changed in the {len(shas)} commits that touched the row")
    txt = "; ".join(f"{m['commit']} moved gap {m['gap']} v_gap {m['v_gap']} with {', '.join(m['measurement_files'][:4])}" for m in moved[:4])
    return _chk("judge_change", "watch", "measurement code changed in the same commit as the number: " + txt + " - confirm the move is stated as a measurement change", commits=moved)


def c_rules(row):
    reasons, lvl = [], "ok"; bp = row.get("best_params") or {}
    txt = json.dumps(row)
    for k, v in bp.items():
        if re.fullmatch(r"(hub_r|hr|r_hub)\d?", k) and _num(v) is not None and _num(v) < 9.99: lvl = "gamed"; reasons.append(f"slim hub {k}={v} (O20 only)")
        if k in ("margin", "m_fold", "fold_margin") and _num(v) is not None and _num(v) < 5: lvl = "gamed"; reasons.append(f"fold margin {k}={v} < 5")
    if re.search(r"\bO1[257]\b", json.dumps(bp)): lvl = "watch"; reasons.append("slim-hub name in the params")
    if re.search(r"virtual (slide|stage)|zero-height", txt, re.I): reasons.append("row mentions a virtual / zero-height stage")
    return _chk("rules", lvl, "; ".join(reasons) or "O20, margin >= 5, translations <= 2 as recorded")


# ------------------------------------------------------------------------------------------------------------------
def audit(rid, params=None, ref=None, write=True):
    row = _row(rid); V = _verifier_outputs(rid); rb, rh = _remeasured(rid, "bench"), _remeasured(rid, "held")
    if ref is None and rid.startswith("sidecar-"): ref = "frontload-lobe-stopb-knuckle-3r"
    checks = [c_held_out(row, V, rh), c_fast_frozen(row), c_near_touch(row, V, rb), c_dominance(row, V, rb, ref), c_continuity(row, V),
              c_fold_margin(row, V, rb), c_idle(row, V, rb), c_sampling(row, V, rb), c_complexity(row), c_reporting(row, V), c_judge_change(row),
              c_rules(row)]
    lv = [c["level"] for c in checks]
    verdict = "gamed" if "gamed" in lv else "watch" if "watch" in lv else "clean"
    reasons = [f"{c['check']}: {c['reason']}" for c in checks if c["level"] == verdict and verdict != "clean"]
    out = dict(id=rid, status=row.get("status"), v_gap=row.get("v_gap"), complexity=row.get("complexity"), verdict=verdict, reasons=reasons,
               checks=checks, remeasured=dict(bench=bool(rb), held=bool(rh)), verifier_files=[f for f, d in V][:12],
               git=_git("rev-parse", "--short", "HEAD"), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    if write:
        os.makedirs(OUT, exist_ok=True); json.dump(out, open(os.path.join(OUT, rid + ".json"), "w"), indent=1, default=float)
    return out


def table():
    L = ["| design | status | verified gap | held out (drop) | near-touch 1 / 2 / 3 mm (shell 1-2) | continuity static -> connected | complexity | verdict | main reasons |",
         "|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(glob.glob(os.path.join(OUT, "*.json")), key=lambda f: (_num(json.load(open(f)).get("v_gap")) or 999)):
        r = json.load(open(f)); C = {c["check"]: c for c in r["checks"]}
        h = C["held_out"]; n = C["near_touch"]; c = C["continuity"]
        hs = f"{h.get('held_gap')} ({h.get('drop'):+.2f})" if h.get("drop") is not None else "-"
        ns = f"{n.get('n1', '-')} / {n.get('n2', '-')} / {n.get('n3') if n.get('n3') is not None else '-'} ({n.get('shell2', '-')})" if n.get("source") else "-"
        cs = (f"{c.get('static')} -> " + " / ".join(str(c.get(k)) for k in ("connected_full", "connected_knn") if c.get(k) is not None)) if c.get("static") is not None else c["level"]
        why = "; ".join(x.split(":")[0] for x in r["reasons"]) if r["reasons"] else "-"
        L.append(f"| {r['id']} | {r['status']} | {r['v_gap']} | {hs} | {ns} | {cs} | {r['complexity']} | **{r['verdict']}** | {why} |")
    return "\n".join(L)


# ==================================================================================================================
# CLI
# ==================================================================================================================
def main(argv):
    if len(argv) < 2: print(__doc__); return
    cmd = argv[1]
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
    if cmd == "remeasure":
        remeasure(argv[2], argv[3], opt("--params"))
    elif cmd == "audit":
        r = audit(argv[2], params=opt("--params"), ref=opt("--ref"))
        print(f"{r['id']}: {r['verdict'].upper()} - " + "; ".join(r["reasons"]) if r["reasons"] else f"{r['id']}: CLEAN")
    elif cmd == "audit-all":
        ids = opt("--ids").split(",") if opt("--ids") else default_ids()
        for i in ids:
            r = audit(i, ref=opt("--ref"))
            print(f"{r['id']}: {r['verdict'].upper()}" + (" - " + "; ".join(r["reasons"]) if r["reasons"] else ""))
    elif cmd == "table":
        print(table())
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
