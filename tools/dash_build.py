"""Datasets for the progress dashboard (docs/DASHBOARD.md): every benchmark over time, gathered from what the swarm, the
judges and the GPU searches already wrote. Nothing is re-measured here.

    python3 tools/dash_build.py [--out docs/dashboard/data] [--manifest docs/dashboard/manifest.json]

Writes one JSON file per dataset (an array of row objects, sorted, so a file's sha256 changes only when its data does)
and the manifest [{id, title, description, file, sha256, rows, bytes, updated}]. After a build, the lead uploads only
the files whose sha256 changed (compare with the manifest of the last upload) and updates those datasets' url/updated.

Datasets (id: sources -> builder):
  morphs        concept bench, one row per morphology: docs/concepts/catalogue.json < families.json < rows/<id>.json,
                plus each morphology's best sweep configuration (sweeps/<id>.json)                   -> morphs()
  sweeps        concept bench, every configuration a morphology agent evaluated, with its time, its morphology's best
                gap so far and the overall record so far (all morphologies)                         -> sweeps()
  cad           built-CAD outside judges, long form: one row per (judged design, requirement) with value, threshold and
                pass: tools/judged_history.py (score.json, score_14mm.json, judge/*.json) + judge/scorecard.json,
                thresholds from judge/requirements.json                                              -> cad()
  gpu_evals     GPU band-evaluator DETAIL evaluations: tools/judged_history.py --evals (time = the commit that added
                the result file)                                                                     -> gpu_evals()
  gpu_searches  GPU band searches, one row per search job: pipeline/conformal/gpu_client/band_search_*.json (time = the
                commit that added the file)                                                          -> gpu_searches()
  reqs          requirement board: R1-R17 + R1-aim + R5-aim for the best judged 3-DOF design (most passes on its
                scorecard, then R1), with the best any 3-DOF design reached                          -> reqs()
  events        docs/concepts/events.jsonl + one milestone per judged design (its judge time) + every new built-CAD R1
                record                                                                               -> events()
  spend         GPU spend from the audit log in docs/RUNPOD_COSTS.md                                 -> spend()
  cov3d         the 3-D "where the arm can go" poses of the newest built designs: tools/coverage3d.py -> cov3d()
  motion        tiny monochrome motion previews of every concept (the leaderboard's first column): written by
                docs/concepts/viz/thumbs.mjs (node), re-run here when kin.js, thumbs.mjs or a concepts/*.js file is
                newer than motion.json or a concept was removed; the file is taken as written     -> motion()
  meta          one row: when this build ran, the repo head, warnings                                -> main()

GAP (the concept bench's single ranking number, lower is better, 0 = every bench target met):
  gap = 100 * (max(0, 0.90 - inband14) + max(0, 0.95 - follow) + max(0, 0.90 - reach)) + 100 * contact
A dataset with no rows is written as one marker row {empty: true} (the dashboard runtime refuses a file without
rows); the page drops it. Missing or malformed inputs are skipped with a WARNING (listed in meta), never a crash. A subprocess-built dataset that
comes out empty where the old file holds rows keeps the old file."""
import argparse, datetime as dt, glob, hashlib, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPTS = os.path.join(REPO, "docs", "concepts")
DESIGNS = os.path.join(REPO, "pipeline", "full-exo", "designs")
GPU = os.path.join(REPO, "pipeline", "conformal", "gpu_client")
WARN = []
TARGETS = dict(inband14=0.90, follow=0.95, reach=0.90)
NUMS = ("reach", "follow", "inband14", "inband10", "contact")
STATUSES = ("ideated", "modelling", "screened", "verified", "refuted", "dead", "duplicate", "gpu", "cad")
KINDS = ("leader", "milestone", "measurement", "infra", "method", "judged")
BASE_ID = "baseline-3r"
FAILED_GAP = 999.0          # a sweep file's gap at or above this is the agent's marker for a failed configuration


def warn(msg):
    WARN.append(msg); print("WARNING:", msg, file=sys.stderr)


def load(p, default=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return default


def truthy(v): return v is True or (isinstance(v, (int, float)) and not isinstance(v, bool) and v == 1) or str(v).strip().lower() in ("true", "1", "yes")


def slug(s): return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "x"


def num(v):
    try: v = float(v)
    except (TypeError, ValueError): return None
    return None if v != v else v


def share(v):
    """a 0-1 share (accepts percent written as 0-100), or None"""
    v = num(v)
    if v is None: return None
    if 1.0 < v <= 100.0: v /= 100.0
    return round(max(0.0, min(1.0, v)), 4)


def gap(ib14, follow, reach, contact):
    if ib14 is None or follow is None or reach is None: return None
    g = sum(max(0.0, TARGETS[k] - v) for k, v in (("inband14", ib14), ("follow", follow), ("reach", reach)))
    return round(100.0 * (g + (contact or 0.0)), 2)


def when(s):
    if not s: return None
    try: t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError: return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def iso(t): return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if t else None


def norm_time(s): return iso(when(s))


def mtime(p):
    try: return iso(dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc))
    except OSError: return None


def to_int(v, default=None):
    try: return int(float(v))
    except (TypeError, ValueError): return default


_GIT = {}


def git_time(rel, first=True):
    """commit time that first added (first=True) or last touched the path, else None"""
    key = (rel, first)
    if key not in _GIT:
        args = ["git", "-C", REPO, "log", "--format=%cI"] + (["--diff-filter=A"] if first else ["-1"]) + ["--", rel]
        try: out = subprocess.run(args, capture_output=True, text=True, timeout=30).stdout.split()
        except Exception: out = []
        _GIT[key] = norm_time(out[-1] if first else out[0]) if out else None
    return _GIT[key]


_DIRTY = None


def dirty(rel):
    global _DIRTY
    if _DIRTY is None:
        try: out = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True, timeout=30).stdout
        except Exception: out = ""
        _DIRTY = {line[3:].strip() for line in out.splitlines() if len(line) > 3}
    return rel in _DIRTY or any(rel.startswith(d.rstrip("/") + "/") for d in _DIRTY if d.endswith("/"))


def file_time(p):
    """when a result file was written: its mtime while uncommitted, else the commit that added it (mtime if earlier)"""
    rel = os.path.relpath(p, REPO)
    if dirty(rel): return mtime(p)
    g, m = git_time(rel), mtime(p)
    return min(x for x in (g, m) if x) if (g or m) else None


def as_list(D, *keys):
    if isinstance(D, list): return D
    if isinstance(D, dict):
        for k in keys:
            if isinstance(D.get(k), list): return D[k]
    return []


# ---------------------------------------------------------------- concept bench
def sweep_file_rows(mid, items, src):
    rows = []
    items = [x for x in items if isinstance(x, dict)]
    for i, x in enumerate(items):
        t = norm_time(x.get("t") or x.get("time"))
        if not t: continue
        r = dict(id=mid, t=t, k=to_int(x.get("k"), i), stage=str(x.get("stage") or x.get("mode") or ""))
        for f in NUMS: r[f] = share(x.get(f))
        r["gap"] = gap(r["inband14"], r["follow"], r["reach"], r["contact"])
        raw = num(x.get("gap"))
        if raw is not None and raw >= FAILED_GAP: r["gap"] = None          # the agent's own 'failed' sentinel (999)
        elif r["gap"] is None: r["gap"] = round(raw, 2) if raw is not None else None
        elif raw is not None and abs(raw - r["gap"]) > 0.02: warn(f"{src} k={r['k']}: file gap {raw} != recomputed {r['gap']}; recomputed kept")
        rows.append(r)
    if not rows and items: warn(f"{src}: no configuration has a time, skipped")
    return rows


def claims():
    """the agents' claimed rows: id -> (gap, claim time); see passed_over in sweeps()"""
    out = {}
    for p in glob.glob(os.path.join(CONCEPTS, "rows", "*.json")):
        r = load(p)
        if not isinstance(r, dict): continue
        g = gap(*(share(r.get(k)) for k in ("inband14", "follow", "reach")), share(r.get("contact")))
        t = norm_time(r.get("t_screened")) or (file_time(p) if g is not None else None)
        if g is not None and t: out[slug(r.get("id") or os.path.splitext(os.path.basename(p))[0])] = (g, t)
    return out


def sweeps():
    """passed_over: a configuration measured before its morphology's claimed row and better than the claim. The agent saw
    it and claimed something worse, i.e. rejected it (seed-offset-3r-slides: 80 configurations scored under a metric hole
    it then closed, best 49.15 vs the claimed 57.95). It stays in the data but counts for no best and no record."""
    rows, C = [], claims()
    for p in sorted(glob.glob(os.path.join(CONCEPTS, "sweeps", "*.json"))):
        try:
            D = load(p)
            if D is None: warn(f"{os.path.relpath(p, REPO)}: not valid JSON, skipped"); continue
            rows += sweep_file_rows(slug(os.path.splitext(os.path.basename(p))[0]), as_list(D, "configs", "rows", "results"), os.path.relpath(p, REPO))
        except Exception as e:
            warn(f"{os.path.relpath(p, REPO)}: skipped ({e})")
    rows.sort(key=lambda r: (r["t"], r["id"], r["k"]))
    for r in rows:
        c = C.get(r["id"])
        r["passed_over"] = bool(c and r["gap"] is not None and r["t"] <= c[1] and r["gap"] < c[0] - 0.005)
    n = sum(r["passed_over"] for r in rows)
    if n: print(f"{n} sweep configuration(s) passed over by their agent's claim (no best, no record)", file=sys.stderr)
    best, rec = {}, None
    for r in rows:                                   # running bests in time order
        g = None if r["passed_over"] else r["gap"]
        if g is not None and (r["id"] not in best or g < best[r["id"]]): best[r["id"]] = g
        r["best_gap"] = best.get(r["id"])
        r["is_record"] = g is not None and (rec is None or g < rec)
        if r["is_record"]: rec = g
        r["record_gap"] = rec
    return rows


def blank(mid):
    return dict(id=mid, name=mid, family="", lens="", status="ideated", is_baseline=False, active_dof=None, passive_dof=None,
                t_ideated=None, t_screened=None, reach=None, follow=None, inband14=None, inband10=None, contact=None, gap=None,
                v_reach=None, v_follow=None, v_inband14=None, v_inband10=None, v_contact=None, v_gap=None,
                n_configs=0, sweep_gap=None, sweep_t=None, sweep_reach=None, sweep_follow=None, sweep_inband14=None,
                sweep_contact=None, t_last=None, verdict="", note="", duplicate_of="", doc="", source="")


def merge(m, src):
    for k, v in src.items():
        if k == "lenses":
            v = ", ".join(str(x).strip(" '[]\"") for x in (v if isinstance(v, list) else str(v).split(",")) if str(x).strip(" '[]\""))
            k = "lens"
        elif k == "notes": k = "note"
        elif k == "limiter":
            if v: m["note"] = (m.get("note") + " | " if m.get("note") else "") + "limiter: " + str(v)
            continue
        if k not in m or v is None or (isinstance(v, str) and not v.strip() and m.get(k)): continue
        m[k] = v
    return m


def morphs(S):
    by = {}
    for e in as_list(load(os.path.join(CONCEPTS, "catalogue.json")), "morphologies", "items"):
        if isinstance(e, dict) and e.get("id"):
            mid = slug(e["id"]); by[mid] = merge(by.get(mid) or blank(mid), dict(e, id=mid))
    for r in as_list(load(os.path.join(CONCEPTS, "families.json")), "families", "rows"):
        if not isinstance(r, dict): continue
        if truthy(r.get("is_baseline")): mid = BASE_ID                    # the bar: rows/baseline-3r.json wins below
        else: mid = slug(r.get("id") or (str(r.get("family") or "") + "-" + str(r.get("variant") or "")))
        m = merge(by.get(mid) or blank(mid), {k: v for k, v in r.items() if k not in ("variant", "id", "is_baseline", "verdict")})
        if m["name"] == mid: m["name"] = " ".join(x for x in (r.get("family"), r.get("variant")) if x) or mid
        m["is_baseline"] = mid == BASE_ID
        by[mid] = m
    for p in sorted(glob.glob(os.path.join(CONCEPTS, "rows", "*.json"))):
        r = load(p)
        if not isinstance(r, dict): warn(f"{os.path.relpath(p, REPO)}: not a JSON object, skipped"); continue
        mid = slug(r.get("id") or os.path.splitext(os.path.basename(p))[0])
        by[mid] = merge(by.get(mid) or blank(mid), dict(r, id=mid))
        if not norm_time(by[mid].get("t_screened")) and r.get("inband14") is not None: by[mid]["t_screened"] = file_time(p)
    per = {}
    for s in S: per.setdefault(s["id"], []).append(s)
    out = []
    for mid, m in by.items():
        try:
            for k in NUMS: m[k] = share(m[k]); m["v_" + k] = share(m.get("v_" + k))
            m["active_dof"], m["passive_dof"] = to_int(m["active_dof"]), to_int(m["passive_dof"])
            m["is_baseline"] = truthy(m["is_baseline"])
            m["t_ideated"], m["t_screened"] = norm_time(m["t_ideated"]), norm_time(m["t_screened"])
            st = str(m["status"] or "ideated").lower().strip()
            if str(m["status"] or "").lower().strip() == "modelling-interrupted":
                m["note"] = (m["note"] + " | " if m["note"] else "") + "a partial, unverified model file exists (interrupted)"
            st = {"modelling-interrupted": "ideated", "modeling": "modelling", "dropped": "dead", "killed": "dead",
                  "gpu sweep": "gpu", "built": "cad", "judged": "cad"}.get(st, st)
            if m.get("duplicate_of"): st = "duplicate"
            if st not in STATUSES: st = "screened" if m["inband14"] is not None else "ideated"
            sw = per.get(mid, [])
            if st == "ideated" and sw: st = "modelling"                    # its agent is sweeping it
            if st in ("ideated", "modelling") and m["inband14"] is not None: st = "screened"
            m["status"] = st
            m["gap"] = gap(m["inband14"], m["follow"], m["reach"], m["contact"])
            if m["gap"] is None and num(m.get("gap")) is not None: m["gap"] = round(num(m["gap"]), 2)
            if any(m["v_" + k] is not None for k in ("inband14", "follow", "reach")):
                pick = lambda k: m["v_" + k] if m["v_" + k] is not None else m[k]
                m["v_gap"] = gap(pick("inband14"), pick("follow"), pick("reach"), pick("contact"))
            else: m["v_gap"] = None
            m["n_configs"] = len(sw) or to_int(m.get("n_configs"), 0) or 0
            scored = [s for s in sw if s["gap"] is not None and not s["passed_over"]]
            if scored:
                b = min(scored, key=lambda s: (s["gap"], s["t"]))
                m.update(sweep_gap=b["gap"], sweep_t=b["t"], sweep_reach=b["reach"], sweep_follow=b["follow"],
                         sweep_inband14=b["inband14"], sweep_contact=b["contact"])
            m["t_last"] = max([x for x in [m["t_ideated"], m["t_screened"]] + [s["t"] for s in sw] if x] or [None]) if (sw or m["t_screened"] or m["t_ideated"]) else None
            if not m["lens"]: m["lens"] = str(m.get("source") or "")
            for k in ("name", "family", "lens", "verdict", "note", "duplicate_of", "doc"): m[k] = "" if m[k] is None else str(m[k])
            out.append({k: m[k] for k in blank(mid) if k != "source"})
        except Exception as e:
            warn(f"morphology {mid}: skipped ({e})")
    bases = [m for m in out if m["is_baseline"]]
    if len(bases) > 1:
        keep = next((m for m in bases if m["id"] == BASE_ID), bases[0])
        for m in bases:
            if m is not keep: m["is_baseline"] = False
        warn(f"{len(bases)} rows claimed to be the baseline; kept {keep['id']}")
    if not any(m["is_baseline"] for m in out): warn("no baseline row (docs/concepts/rows/baseline-3r.json)")
    out.sort(key=lambda m: (not m["is_baseline"], m["id"]))
    return out


# ---------------------------------------------------------------- built CAD judges
REQ_DEF = load(os.path.join(REPO, "judge", "requirements.json"), {}) or {}
# id, short name, direction, unit shown, judged_history column
REQS = [
    ("R1", "Skin 2-14 mm from the metal while following", "hi", "%", "r1_14"),
    ("R1-aim", "Skin 2-10 mm from the metal (the 1 cm aim)", "hi", "%", "r1_10"),
    ("R2", "No part enters the body", "lo", "mm", None),
    ("R3", "Follows the arm (frames tracked)", "hi", "%", "follow"),
    ("R4", "Overhead works (Raise overhead, 14 mm band)", "hi", "%", "overhead_14"),
    ("R5", "Shoulder-chain DOF (cap 4)", "lo", "", "dof"),
    ("R5-aim", "Exactly 3 DOF, the minimum", "lo", "", "dof"),
    ("R6", "No interference between moving parts", "lo", "mm", "parts_mm"),
    ("R7", "Every custom part is one valid solid", "bool", "", None),
    ("R8", "Custom-part mass", "lo", "g", None),
    ("R9", "Strength SF (independent FEA)", "hi", "", None),
    ("R10", "Base slip on the scapula (GH-centre misalignment)", "lo", "mm", None),
    ("R11", "Pressure the exo adds on the cuff", "lo", "kPa", None),
    ("R12", "CAD standard: G2 surfaces, no visible screws", None, "", None),
    ("R13", "Manufacturable (supplier review and quote)", None, "", None),
    ("R14", "Holds on motions and bodies never used to design it", None, "", None),
    ("R15", "Works on real bodies (printed prototype)", None, "", None),
    ("R16", "Everyday arm poses reached (workspace)", "hi", "%", "range_r16"),
    ("R17", "Moves freely unpowered", "bool", "", "moves_freely"),
]
# judging-rule changes after which earlier values of a requirement are not comparable (also: a 'measurement' event in
# docs/concepts/events.jsonl with "affects": ["R1", ...])
RULES = [(("R3", "R4", "R6", "R2"), "2026-10-15T02:44:38Z", "the contact-judge fix"),
         (("R1", "R1-aim", "R4"), "2026-10-15T11:55:00Z", "the held-out-leak fix")]


def threshold(rid):
    d = REQ_DEF.get(rid) or {}
    op, v = d.get("op"), d.get("value")
    if isinstance(v, bool): v = 1.0 if v else 0.0
    return op, (float(v) if isinstance(v, (int, float)) else None), str(d.get("judge") or "")


def passes(v, op, thr):
    if v is None or thr is None or not op: return None
    return {">=": v >= thr, "<=": v <= thr, "==": abs(v - thr) < 1e-9}.get(op)


def rules_since(ev):
    out = {}
    for reqs_, t, why in RULES:
        for r in reqs_: out[r] = max(out.get(r, ("", "")), (t, why))
    for e in ev:
        if e.get("kind") == "measurement" and e.get("affects"):
            for r in str(e["affects"]).split(","):
                if r.strip(): out[r.strip()] = max(out.get(r.strip(), ("", "")), (e["time"], e["event"][:80]))
    return out


def first_mention(design):
    """the first commit whose docs (docs/*.md, README.md) mention the design id: a judged build is reported as soon as it
    is judged, while its score files may be committed hours later in a batch (7c94de2 at 13:33 carried builds judged
    from 05:52 on); taking the earlier time keeps a pre-fix result from counting as 'current rules'"""
    if not design or design == "None": return None
    key = ("mention", design)
    if key not in _GIT:
        args = ["git", "-C", REPO, "log", "--format=%cI", "-G", re.escape(design) + r"([^_a-z0-9]|$)", "--", "docs/*.md", "README.md"]
        try: out = subprocess.run(args, capture_output=True, text=True, timeout=60).stdout.split()
        except Exception: out = []
        _GIT[key] = norm_time(out[-1]) if out else None
    return _GIT[key]


def judged_history():
    try:
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "judged_history.py")], cwd=REPO, capture_output=True, text=True, timeout=300)
        if out.returncode != 0: warn(f"judged_history.py exited {out.returncode}: {out.stderr.strip()[-200:]}"); return []
        rows = json.loads(out.stdout)
    except Exception as e:
        warn(f"judged_history.py failed: {e}"); return []
    for r in rows:      # a build judged hours before its commit keeps the judge time in the files' mtime: take the earlier
        dd = os.path.join(DESIGNS, str(r.get("design")))
        ts = [when(r.get("time")), when(first_mention(str(r.get("design"))))] + [when(mtime(f)) for f in (f"{dd}/score.json", f"{dd}/score_14mm.json") if os.path.exists(f) and not dirty(os.path.relpath(f, REPO))]
        ts = [t for t in ts if t]
        r["time"] = iso(min(ts)) if ts else None
    return [r for r in rows if r.get("time")]


def cad(ev):
    J = judged_history()
    rules = rules_since(ev)
    rows, seen = [], set()
    meta = {}
    for j in J:
        meta[j["design"]] = (j["level"], to_int(j["dof"]))
        for rid, name, d, unit, col in REQS:
            if not col or j.get(col) is None: continue
            v = j[col]
            v = (1.0 if v else 0.0) if isinstance(v, bool) else float(v)
            rows.append((j["time"], j["design"], rid, v, "judged_history.py"))
            seen.add((j["design"], rid))
    for p in sorted(glob.glob(os.path.join(DESIGNS, "*", "judge", "scorecard.json"))):
        sc = load(p)
        if not isinstance(sc, list): continue
        design = p.split(os.sep)[-3]
        dj = load(os.path.join(DESIGNS, design, "design.json"), {}) or {}
        dof = to_int(dj.get("dof", dj.get("n")))
        if not dof or dof > 4: continue
        if design not in meta: meta[design] = ("Full CAD" if design.startswith("cad_") or design == "final" else "Keep-out CAD", dof)
        rel = os.path.relpath(p, REPO)
        t = mtime(p) if dirty(rel) else (git_time(rel, first=False) or mtime(p))
        for r in sc:
            if not isinstance(r, dict) or (design, r.get("id")) in seen: continue
            v = r.get("value")
            if isinstance(v, bool): v = 1.0 if v else 0.0
            if not isinstance(v, (int, float)): continue
            rows.append((t, design, r["id"], float(v), "judge/scorecard.json"))
    out = []
    by = {x[0]: x for x in REQS}
    for t, design, rid, v, src in rows:
        if rid not in by: continue
        op, thr, judge = threshold(rid)
        lvl, dof = meta[design]
        since = rules.get(rid, ("", ""))[0]
        out.append(dict(time=t, design=design, level=lvl, dof=dof, req=rid, name=by[rid][1], value=round(v, 4), op=op or "",
                        threshold=thr, unit=by[rid][3], ok=passes(v, op, thr), rules="older" if since and t < since else "current",
                        judge=judge[:120], src=src))
    out.sort(key=lambda r: (r["time"], r["design"], [x[0] for x in REQS].index(r["req"])))
    return out


def reqs(C, ev):
    rules = rules_since(ev)
    cards = {}
    for p in glob.glob(os.path.join(DESIGNS, "*", "judge", "scorecard.json")):
        sc = load(p)
        if not isinstance(sc, list): continue
        by = {r.get("id"): r for r in sc if isinstance(r, dict)}
        if (by.get("R5") or {}).get("value") not in (3, 3.0): continue          # the user's goal: 3 active DOF
        rel = os.path.relpath(p, REPO)
        cards[p.split(os.sep)[-3]] = (by, mtime(p) if dirty(rel) else (git_time(rel, first=False) or mtime(p)))
    def rank(item):
        d, (by, t) = item
        return (sum(1 for r in by.values() if str(r.get("status")).upper() == "PASS"), num((by.get("R1") or {}).get("value")) or 0, t or "")
    best = max(cards.items(), key=rank)[0] if cards else ""
    by, t = cards.get(best, ({}, None))
    out = []
    for rid, name, d, unit, col in REQS:
        r = by.get(rid) or {}
        op, thr, judge = threshold(rid)
        st = str(r.get("status") or "").upper()
        state = {"PASS": "pass", "FAIL": "fail", "PARTIAL": "partial"}.get(st, "not measured")
        if rid in ("R12", "R15") and state != "pass": state = "needs the user"
        v = r.get("value")
        v = (1.0 if v else 0.0) if isinstance(v, bool) else (float(v) if isinstance(v, (int, float)) else None)
        cs = [c for c in C if c["req"] == rid and c["dof"] == 3]
        cur = [c for c in cs if c["rules"] == "current"]
        b = None
        if cur and d in ("hi", "lo", "bool"):
            b = max(cur, key=lambda c: ((c["value"] if d != "lo" else -c["value"]), c["time"]))
        since = rules.get(rid, ("", ""))
        out.append(dict(req=rid, name=name, design=best if r else "", time=t if r else None, state=state, value=None if v is None else round(v, 4),
                        unit=unit, op=op or "", threshold=thr, target=str(r.get("target") or (f"{op} {thr:g}" if op and thr is not None else "")),
                        judge=judge[:160], best_value=b["value"] if b else None, best_design=b["design"] if b else "",
                        best_ok=b["ok"] if b else None, rules_since=since[0] or None, rules_why=since[1]))
    return out


# ---------------------------------------------------------------- GPU searches
def gpu_evals():
    try:
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "judged_history.py"), "--evals"], cwd=REPO, capture_output=True, text=True, timeout=300)
        rows = json.loads(out.stdout) if out.returncode == 0 else []
        if out.returncode != 0: warn(f"judged_history.py --evals exited {out.returncode}")
    except Exception as e:
        warn(f"judged_history.py --evals failed: {e}"); rows = []
    res = []
    for r in rows:
        res.append(dict(time=norm_time(r.get("time")), candidate=str(r.get("design") or ""), dof=to_int(r.get("dof")),
                        inband14=num(r.get("r1_14")), follow=num(r.get("follow")), workspace=num(r.get("range_r16")),
                        overhead_follow=num(r.get("overhead_follow")), hub_r=num(r.get("hub_r")), maps=str(r.get("measurement") or "")))
    res = [r for r in res if r["time"]]
    res.sort(key=lambda r: (r["time"], r["candidate"]))
    return res


def gpu_searches():
    rows = []
    for p in sorted(glob.glob(os.path.join(GPU, "band_search_*.json"))):
        D = load(p)
        if not isinstance(D, list): continue
        t = file_time(p); s = os.path.splitext(os.path.basename(p))[0].replace("band_search_", "")
        for i, job in enumerate(D):
            if not isinstance(job, dict) or not isinstance(job.get("hist"), list) or not job["hist"]: continue
            h = job["hist"][-1]; cfg = job.get("cfg") if isinstance(job.get("cfg"), dict) else {}
            rows.append(dict(time=t, search=s, job=i, dof=to_int(cfg.get("n")), seed=to_int(cfg.get("seed")), fit=num(h.get("best")),
                             follow=num(h.get("follow")), gens=to_int(h.get("gen")), evals=to_int(job.get("evals")), secs=round(num(job.get("secs")) or 0),
                             device=str(job.get("device") or "")[:60], version=str(job.get("version") or "")[:60]))
    rows = [r for r in rows if r["time"] and r["fit"] is not None]
    rows.sort(key=lambda r: (r["time"], r["search"], r["job"]))
    return rows


# ---------------------------------------------------------------- events, spend
def events(C):
    rows = []
    p = os.path.join(CONCEPTS, "events.jsonl")
    if os.path.exists(p):
        for n, line in enumerate(open(p), 1):
            if not line.strip(): continue
            try: r = json.loads(line)
            except ValueError: warn(f"events.jsonl line {n}: not JSON, skipped"); continue
            if not isinstance(r, dict): continue
            t, e = norm_time(r.get("time") or r.get("t")), str(r.get("event") or r.get("text") or "").strip()
            if not t or not e: continue
            k = str(r.get("kind") or "milestone").lower()
            k = {"decision": "milestone", "measurement change": "measurement"}.get(k, k)
            row = dict(time=t, kind=k if k in KINDS else "milestone", event=e, source="swarm")
            if isinstance(r.get("affects"), list) and r["affects"]: row["affects"] = ",".join(map(str, r["affects"]))
            rows.append(row)
    first = {}
    for c in C:
        first.setdefault(c["design"], c)
    for d, c in first.items():
        vals = {x["req"]: x for x in C if x["design"] == d and x["time"] == c["time"]}
        bits = [f"{rid} {'%.1f %%' % (100 * vals[rid]['value']) if vals[rid]['unit'] == '%' else vals[rid]['value']}" for rid in ("R1", "R3", "R16") if rid in vals]
        rows.append(dict(time=c["time"], kind="judged", event=f"Judged {d} ({c['level']}, {c['dof']} DOF)" + (": " + ", ".join(bits) if bits else ""), source="judges"))
    rec = {}                                         # one record per judging-rule epoch: older values are not compared
    for c in [x for x in C if x["req"] == "R1" and x["dof"] == 3]:
        if c["rules"] not in rec or c["value"] > rec[c["rules"]]:
            rec[c["rules"]] = c["value"]
            tail = "" if c["rules"] == "current" else "; judged before a later judging-rule change"
            rows.append(dict(time=c["time"], kind="leader", event=f"Built-CAD R1 record: {100 * c['value']:.1f} % ({c['design']}, {c['level']}{tail})", source="judges"))
    out, seen = [], set()
    for r in rows:
        key = (r["time"], r["event"])
        if key in seen: continue
        seen.add(key); r.setdefault("affects", ""); out.append(r)
    out.sort(key=lambda r: (r["time"], r["kind"], r["event"]))
    return out


def spend():
    try: txt = open(os.path.join(REPO, "docs", "RUNPOD_COSTS.md")).read()
    except OSError: return []
    rows, start = [], None
    for line in txt.splitlines():
        m = re.match(r"\| (\d\d)-(\d\d) (\d\d:\d\d)(?:-(\d\d:\d\d))? \| ([^|]*)\|", line)
        cells = line.split("|")
        bal = cells[6].strip() if len(cells) > 6 else ""          # the 'balance before -> after' column
        b = re.match(r"(\d+\.\d\d)(?: -> (\d+\.\d\d))?", bal)
        if not (m and b): continue
        before = float(b.group(1)); after = float(b.group(2)) if b.group(2) else before     # an audit row: one balance
        if start is None: start = before
        rows.append(dict(time=f"2026-{m.group(1)}-{m.group(2)}T{m.group(4) or m.group(3)}:00Z", endpoint=m.group(5).strip()[:60],
                         balance=after, spent=round(start - after, 2)))
    rows.sort(key=lambda r: r["time"])
    return rows


def cov3d(keep=8):
    tmp = os.path.join(REPO, ".cache", "dash_cov3d.json")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    try:
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "coverage3d.py"), "-o", tmp], cwd=REPO, capture_output=True, text=True, timeout=300)
        rows = load(tmp) if out.returncode == 0 else None
        if out.returncode != 0: warn(f"coverage3d.py exited {out.returncode}: {out.stderr.strip()[-200:]}")
    except Exception as e:
        warn(f"coverage3d.py failed: {e}"); rows = None
    if not isinstance(rows, list): return []
    order = list(dict.fromkeys(r.get("design") for r in rows if isinstance(r, dict)))
    keepset = set(order[-keep:])
    return [r for r in rows if isinstance(r, dict) and r.get("design") in keepset]


VIZ = os.path.join(CONCEPTS, "viz")


def motion(out_dir):
    """the motion-preview file (raw bytes, or None): docs/concepts/viz/thumbs.mjs writes <out>/motion.json from the
    concept kinematics; it is re-run (about 5 s, niced) when the file is missing, older than kin.js / thumbs.mjs / any
    concepts/*.js, or holds a concept whose file is gone. A failed run keeps the previous file (with a warning)."""
    out = os.path.join(out_dir, "motion.json")
    thumbs = os.path.join(VIZ, "thumbs.mjs")
    srcs = [os.path.join(VIZ, "kin.js"), thumbs] + sorted(glob.glob(os.path.join(VIZ, "concepts", "*.js")))
    have = {os.path.basename(f)[:-3] for f in srcs[2:]}
    stale = not os.path.exists(out)
    if not stale:
        t_out = os.path.getmtime(out)
        stale = any(os.path.getmtime(f) > t_out for f in srcs if os.path.exists(f))
        if not stale:
            mech = [r for r in (load(out, []) or []) if isinstance(r, dict) and r.get("kind") == "mechanism"]
            stale = not mech or any(r.get("id") not in have for r in mech)
    if stale and os.path.exists(thumbs):
        try:
            r = subprocess.run(["nice", "-n", "10", "node", thumbs, "--out", out], capture_output=True, text=True, timeout=600)
            if r.returncode != 0: warn(f"motion: thumbs.mjs exited {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
            skipped = [line.strip() for line in r.stdout.splitlines() if line.startswith("  ")]
            if skipped: warn("motion: thumbs.mjs skipped " + "; ".join(skipped))
        except Exception as e:
            warn(f"motion: thumbs.mjs did not run ({e}); kept the previous file")
    if not os.path.exists(out): return None
    return open(out, "rb").read()


# ---------------------------------------------------------------- main
DESC = {
    "morphs": ("Concept bench morphologies", "One row per morphology in the swarm's catalogue: status, the agent's claimed bench numbers, the verifier's re-measured numbers (v_), its best sweep configuration so far, and the 3R baseline once (is_baseline). Built from docs/concepts/catalogue.json, families.json, rows/*.json and sweeps/*.json."),
    "sweeps": ("Concept bench sweeps", "Every configuration a morphology agent evaluated on the concept bench, with its time, gap, its morphology's best gap so far (best_gap) and the record over all morphologies so far (record_gap); passed_over marks a configuration its agent measured before its claimed row and rejected (better than the claim), which counts for no best. Built from docs/concepts/sweeps/*.json."),
    "cad": ("Built CAD judge results", "One row per judged design and requirement: value, threshold and pass from the outside judges, timed by the judge output (score files: the earliest of their commit, their file time and the first commit whose docs report the design; scorecard-only values: the scorecard's commit). Built from tools/judged_history.py, judge/scorecard.json files and judge/requirements.json."),
    "gpu_evals": ("GPU evaluator detail runs", "Every GPU band-evaluator detail evaluation of a search candidate (in-band 14 mm, follow, workspace share, overhead follow). Time is the git commit that added the result file, not the run itself. Built from pipeline/conformal/gpu_client/band_eval_*.json via tools/judged_history.py --evals."),
    "gpu_searches": ("GPU band searches", "One row per GPU search job: its final best fitness, follow, generations, evaluations and seconds. Time is the git commit that added the result file. Built from pipeline/conformal/gpu_client/band_search_*.json."),
    "reqs": ("Requirement board", "Latest status of R1-R17 (with R1-aim and R5-aim) for the best judged 3-DOF design (most passes on its scorecard, then R1), with the best value any 3-DOF design reached under the current judging rules. Built from judge/scorecard.json files and judge/requirements.json."),
    "events": ("Event log", "What happened and when: the swarm's own log (docs/concepts/events.jsonl), one milestone per judged design and every new built-CAD R1 record (from the judge outputs)."),
    "spend": ("GPU spend log", "RunPod balance and cumulative spend at each logged audit. Built from docs/RUNPOD_COSTS.md (audit rows only)."),
    "cov3d": ("Arm reach in 3-D", "One row per built design and everyday arm pose of the R16 workspace judge: where the upper arm points and whether the built design reaches it, with the reason if not. Built by tools/coverage3d.py from judge/workspace.json files (newest 8 designs)."),
    "motion": ("Motion previews", "Tiny monochrome previews of each concept's mechanism moving with the arm through the gallery's motion loop (40 frames, one fixed camera for all), as SVG paths per frame; generated by docs/concepts/viz/thumbs.mjs from the concept kinematics (docs/concepts/viz/kin.js and concepts/*.js)."),
    "meta": ("Data build info", "When tools/dash_build.py last gathered the data, the repo commit, and any warnings it printed."),
}


def head_commit():
    try: return subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception: return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "dashboard", "data"))
    ap.add_argument("--manifest", default=os.path.join(REPO, "docs", "dashboard", "manifest.json"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    S = sweeps(); M = morphs(S)
    C = cad([]); E = events(C)
    C = cad(E)                                       # with any rule change the log adds
    R = reqs(C, E)
    data = dict(morphs=M, sweeps=S, cad=C, gpu_evals=gpu_evals(), gpu_searches=gpu_searches(), reqs=R, events=E, spend=spend(), cov3d=cov3d())
    data["motion"] = motion(a.out)                   # raw bytes as thumbs.mjs wrote them (not re-serialised)
    old = {d["id"]: d for d in (load(a.manifest, []) or [])}
    man = []
    built = iso(dt.datetime.now(dt.timezone.utc))
    data["meta"] = None
    for k in list(data):
        rows = data[k]
        if k == "meta": rows = [dict(built_at=built, commit=head_commit(), n_warnings=len(WARN), warnings=" | ".join(WARN)[:2000])]
        p = os.path.join(a.out, k + ".json")
        if k == "motion" and rows is not None:
            raw = rows
        elif k in ("cad", "cov3d", "gpu_evals") and not rows and isinstance(load(p), list) and load(p):
            warn(f"{k}: the new build is empty; kept the previous file"); raw = open(p, "rb").read()
        else:
            if not rows:      # the runtime refuses a file with no rows: one marker row the page skips (EXO.rows drops it)
                rows = [dict(empty=True, note="no rows yet")]
            raw = json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode()
            with open(p, "wb") as f: f.write(raw)
        h = hashlib.sha256(raw).hexdigest()
        n = sum(1 for r in json.loads(raw) if not (isinstance(r, dict) and r.get("empty") is True))
        prev = old.get(k, {})
        man.append(dict(id=k, title=DESC[k][0], description=DESC[k][1], file=os.path.relpath(p, os.path.dirname(a.manifest)),
                        sha256=h, rows=n, bytes=len(raw), updated=prev.get("updated") if prev.get("sha256") == h else built))
        flag = "" if prev.get("sha256") == h else "  CHANGED"
        print(f"{k:13s} {n:6d} rows {len(raw):9d} B{flag}")
        if len(raw) > 8 * 1024 * 1024: warn(f"{k} is over 8 MB: the dashboard refuses it")
    with open(a.manifest, "w") as f: json.dump(man, f, indent=1); f.write("\n")
    base = next((m for m in M if m["is_baseline"]), None)
    print(f"baseline gap {base['gap'] if base else '-'}; {sum(m['status'] == 'screened' for m in M)} screened; record {S[-1]['record_gap'] if S else '-'}; {len(WARN)} warning(s)")
    print("->", a.out)


if __name__ == "__main__":
    main()
