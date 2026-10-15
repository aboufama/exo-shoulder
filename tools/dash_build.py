"""Datasets for the progress dashboard: the morphology swarm (bench numbers, optimisation traces, verifier checks) and
the built-CAD outside-judge history. Nothing is re-measured here; this only gathers what the swarm and the judges wrote.

    python3 tools/dash_build.py [--out DIR]             # real data from the repo -> DIR/<dataset>.json
    python3 tools/dash_build.py --sample [--out DIR]    # SAMPLE data for the page's local test harness only (never publish)

Datasets (one JSON list of row objects each):
  morphs  one row per morphology: docs/concepts/catalogue.json (ideated entries) < docs/concepts/families.json (legacy
          rows incl. the baseline) < docs/concepts/rows/<id>.json (the swarm's own rows override by id)
  sweeps  docs/concepts/sweeps/<id>.json: one row per evaluated configuration, with best_gap (best gap so far)
  judged  tools/judged_history.py (built CAD, the real requirements)
  events  docs/concepts/events.jsonl + the older event history (docs/concepts/events_history.json, else --events-old)
  reqs    the 19 requirements' best status over the judged 3-DOF designs (scorecards + judged history), with the time
          the judging rules last changed for it (RULES below, or a 'measurement' event carrying "affects": [req ids])
  cov3d   the 3-D "where the arm can go" poses of built designs: tools/coverage3d.py (newest 8 designs; --cov3d copy
          only if that fails)
  meta    one row: when this build ran (built_at), the repo head, and any warnings
A dataset that comes out empty where its file already holds rows (a failed subprocess) keeps the old file, with a WARNING.
GAP (the bench's single ranking number, lower is better, 0 = every bench target met):
  gap = 100 * (max(0, 0.90 - inband14) + max(0, 0.95 - follow) + max(0, 0.90 - reach)) + 100 * contact
Missing inputs give empty lists, never a crash."""
import argparse, datetime as dt, glob, json, os, random, re, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# session scratch paths (override with DASH_SCRATCH / DASH_OUT / DASH_EVENTS_OLD / DASH_COV3D in another session)
SCRATCH = os.environ.get("DASH_SCRATCH", "/tmp/claude-0/-home-user-exo-shoulder/83445525-dbfd-5a74-afa6-eaabc370b170/scratchpad")
DEF_OUT = os.environ.get("DASH_OUT", os.path.join(SCRATCH, "dash2", "data"))
DEF_EVENTS_OLD = os.environ.get("DASH_EVENTS_OLD", os.path.join(SCRATCH, "dash", "events_1015c.json"))
DEF_COV3D = os.environ.get("DASH_COV3D", os.path.join(SCRATCH, "cov3d"))
WARN = []


def warn(msg):
    WARN.append(msg); print("WARNING:", msg, file=sys.stderr)


def truthy(v): return v is True or (isinstance(v, (int, float)) and not isinstance(v, bool) and v == 1) or str(v).strip().lower() in ("true", "1", "yes")


CONCEPTS = os.path.join(REPO, "docs", "concepts")
TARGETS = dict(inband14=0.90, follow=0.95, reach=0.90)
STATUSES = ("ideated", "modelling", "screened", "verified", "refuted", "dead", "gpu", "cad", "judged")
KINDS = ("leader", "milestone", "measurement", "infra", "method")
NUMS = ("reach", "follow", "inband14", "inband10", "contact")
BASE_ID = "baseline-3r"                                     # the one baseline row (tools/concept_baseline.py --write)


def load(p, default=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return default


def slug(s): return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "x"


def share(v):
    """a 0-1 share (accepts percent written as 0-100), or None"""
    try: v = float(v)
    except (TypeError, ValueError): return None
    if v != v: return None
    if 1.0 < v <= 100.0: v /= 100.0
    return round(max(0.0, min(1.0, v)), 4)


def gap(ib14, follow, reach, contact):
    if ib14 is None or follow is None or reach is None: return None
    g = sum(max(0.0, TARGETS[k] - v) for k, v in (("inband14", ib14), ("follow", follow), ("reach", reach)))
    return round(100.0 * (g + (contact or 0.0)), 2)


def when(s):
    """ISO time -> aware datetime (UTC if no zone), or None"""
    if not s: return None
    try: t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError: return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def iso(t): return t.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z") if t else None


def norm_time(s): return iso(when(s))


_GIT = {}


def git_times(path, needle=None, last=False):
    """commit time that first added `needle` to `path` (or the file; last=True: the newest commit touching it), else None"""
    key = (path, needle, last)
    if key not in _GIT:
        args = ["git", "-C", REPO, "log", "--format=%cI"] + (["-1"] if last else []) + (["-S", needle] if needle else [] if last else ["--diff-filter=A"]) + ["--", path]
        try: out = subprocess.run(args, capture_output=True, text=True, timeout=30).stdout.split()
        except Exception: out = []
        _GIT[key] = norm_time(out[0] if last else out[-1]) if out else None
    return _GIT[key]


def git_first(path, needle=None): return git_times(path, needle)


_DIRTY = None


def dirty(rel):
    """True when the file has uncommitted changes (or is untracked)"""
    global _DIRTY
    if _DIRTY is None:
        try: out = subprocess.run(["git", "-C", REPO, "status", "--porcelain"], capture_output=True, text=True, timeout=30).stdout
        except Exception: out = ""
        _DIRTY = {line[3:].strip() for line in out.splitlines() if len(line) > 3}
    return rel in _DIRTY or any(rel.startswith(d.rstrip("/") + "/") for d in _DIRTY if d.endswith("/"))


def mtime(p):
    try: return iso(dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc))
    except OSError: return None


def to_int(v, default=None):
    try: return int(float(v))
    except (TypeError, ValueError): return default


# ---------------------------------------------------------------- morphs
def blank(mid):
    return dict(id=mid, name=mid, lens="", family="", active_dof=3, passive_dof=0, status="ideated", is_baseline=False,
                t_ideated=None, t_screened=None, reach=None, follow=None, inband14=None, inband10=None, contact=None, gap=None,
                v_reach=None, v_follow=None, v_inband14=None, v_inband10=None, v_contact=None, v_gap=None, n_configs=None,
                verdict="", note="", doc="", source="")


def as_list(D, *keys):
    if isinstance(D, list): return D
    if isinstance(D, dict):
        for k in keys:
            if isinstance(D.get(k), list): return D[k]
        if all(isinstance(v, dict) for v in D.values()): return [dict(v, id=v.get("id", k)) for k, v in D.items()]
    return []


def empty(v): return v is None or (isinstance(v, str) and not v.strip())


def merge(m, src):
    """src fields onto m; an empty value never overwrites a filled one"""
    for k, v in src.items():
        if k == "lenses":
            v = ", ".join(str(x).strip() for x in (v if isinstance(v, list) else [v]) if str(x).strip())
            k = "lens"
        elif k == "notes": k = "note"
        elif k in ("t", "time"):
            if src.get("t_ideated"): continue
            k = "t_ideated"
        if k not in m or (empty(v) and not empty(m[k])): continue
        m[k] = v
    return m


def finish(m):
    for k in NUMS: m[k] = share(m[k]); m["v_" + k] = share(m.get("v_" + k))
    for k in ("active_dof", "passive_dof", "n_configs"): m[k] = to_int(m[k]) if m[k] is not None else None
    m["is_baseline"] = truthy(m["is_baseline"])
    m["t_ideated"], m["t_screened"] = norm_time(m["t_ideated"]), norm_time(m["t_screened"])
    st = str(m["status"] or "ideated").lower().strip()
    st = {"modeling": "modelling", "gpu sweep": "gpu", "built": "cad", "dropped": "dead", "killed": "dead"}.get(st, st)
    if st not in STATUSES: st = "screened" if m["reach"] is not None else "ideated"
    if st in ("ideated", "modelling") and m["inband14"] is not None: st = "screened"
    m["status"] = st
    m["gap"] = gap(m["inband14"], m["follow"], m["reach"], m["contact"])
    # the verifier's gap: its own numbers where it wrote them, the claim where it did not (none at all -> no v_gap)
    if any(m["v_" + k] is not None for k in ("inband14", "follow", "reach", "contact")):
        pick = lambda k: m["v_" + k] if m["v_" + k] is not None else m[k]
        m["v_gap"] = gap(pick("inband14"), pick("follow"), pick("reach"), pick("contact"))
    else: m["v_gap"] = None
    for k in ("name", "lens", "family", "verdict", "note", "doc", "source"): m[k] = "" if m[k] is None else str(m[k])
    if not m["lens"]: m["lens"] = m["source"]                       # e.g. 'ideation A' when the entry names no lens
    m.pop("source", None)
    return m


def fam_time(r, fam_rel, fam_path):
    """a families.json row's screening time: its own field, else the commit that added its variant (or family) text"""
    for k in ("t_screened", "t", "time"):
        if norm_time(r.get(k)): return norm_time(r.get(k))
    needle = json.dumps(str(r.get("variant") or r.get("family") or ""))[1:-1]
    return (git_first(fam_rel, needle) if needle else None) or mtime(fam_path)


def morphs(sweep_counts):
    by, dup = {}, []
    cat = as_list(load(os.path.join(CONCEPTS, "catalogue.json")), "morphologies", "items", "catalogue")
    for e in cat:
        if not isinstance(e, dict) or not e.get("id"): continue
        if e.get("duplicate_of"): dup.append(f"{e['id']} (= {e['duplicate_of']})"); continue
        mid = slug(e["id"]); by[mid] = merge(by.get(mid) or blank(mid), dict(e, id=mid))
    if dup: print(f"morphs: skipped {len(dup)} catalogue duplicates: {', '.join(dup)}")
    fam_path = os.path.join(CONCEPTS, "families.json"); fam_rel = os.path.relpath(fam_path, REPO)
    for r in as_list(load(fam_path), "families", "rows"):
        if not isinstance(r, dict): continue
        try:
            fam, var = str(r.get("family") or ""), str(r.get("variant") or "")
            isb = truthy(r.get("is_baseline"))
            mid = BASE_ID if isb else slug(r.get("id") or (fam + "-" + var if var else fam))
            m = merge(by.get(mid) or blank(mid), {k: v for k, v in r.items() if k not in ("variant", "id", "is_baseline")})
            nm = fam if not var else var if fam.lower() in var.lower() else f"{fam} ({var})" if fam else var
            if r.get("name") or m["name"] == mid: m["name"] = r.get("name") or (nm[:1].upper() + nm[1:])
            m["is_baseline"] = isb
            if "status" not in r:
                m["status"] = "dead" if re.match(r"\s*(dead|killed|drop)", str(r.get("verdict") or ""), re.I) else ("screened" if r.get("inband14") is not None else m["status"])
            if not norm_time(m.get("t_screened")) and r.get("inband14") is not None: m["t_screened"] = fam_time(r, fam_rel, fam_path)
            if not m.get("doc"):
                for cand in (slug(fam), fam.lower().replace(" ", "_")):
                    if os.path.exists(os.path.join(CONCEPTS, cand + ".md")): m["doc"] = f"docs/concepts/{cand}.md"; break
            by[mid] = m
        except Exception as e:
            warn(f"families.json row {r.get('family')!r}: skipped ({e})")
    for p in sorted(glob.glob(os.path.join(CONCEPTS, "rows", "*.json"))):
        try:
            r = load(p)
            if not isinstance(r, dict): warn(f"{os.path.relpath(p, REPO)}: not a JSON object, skipped"); continue
            mid = slug(r.get("id") or os.path.splitext(os.path.basename(p))[0])
            by[mid] = merge(by.get(mid) or blank(mid), dict(r, id=mid))
            if not norm_time(by[mid].get("t_screened")) and r.get("inband14") is not None: by[mid]["t_screened"] = mtime(p)
        except Exception as e:
            warn(f"{os.path.relpath(p, REPO)}: skipped ({e})")
    out = []
    for mid, m in by.items():
        try:
            if m.get("n_configs") is None and sweep_counts.get(mid): m["n_configs"] = sweep_counts[mid]
            out.append(finish(m))
        except Exception as e:
            warn(f"morphology {mid}: skipped ({e})")
    bases = [m for m in out if m["is_baseline"]]
    if len(bases) > 1:                                        # exactly one bar to beat: rows/baseline-3r.json, else the newest
        keep = next((m for m in bases if m["id"] == BASE_ID), None) or max(bases, key=lambda m: m["t_screened"] or "")
        for m in bases:
            if m is not keep: m["is_baseline"] = False
        warn(f"{len(bases)} rows claimed to be the baseline ({', '.join(m['id'] for m in bases)}); kept {keep['id']}")
    assert len([m for m in out if m["is_baseline"]]) <= 1
    nc = [m["id"] for m in out if m["gap"] is not None and m["contact"] is None and not m["is_baseline"]]
    if nc: warn(f"{len(nc)} morphologies have no contact number; their gap counts contact as 0 (optimistic): {', '.join(nc[:6])}")
    out.sort(key=lambda m: (not m["is_baseline"], m["t_screened"] or "~", m["t_ideated"] or "~", m["id"]))
    return out


# ---------------------------------------------------------------- sweeps
def sweep_rows(mid, items):
    rows, best = [], None
    items = [x for x in items if isinstance(x, dict)]
    keyed = [(to_int(x.get("k"), i + 1), i, x) for i, x in enumerate(items)]
    keyed.sort(key=lambda t: (t[0], t[1]))
    for k, _, x in keyed:
        r = dict(id=mid, k=k, t=norm_time(x.get("t") or x.get("time")))
        for f in NUMS: r[f] = share(x.get(f))
        r["gap"] = gap(r["inband14"], r["follow"], r["reach"], r["contact"])
        if r["gap"] is not None and (best is None or r["gap"] < best): best = r["gap"]
        r["best_gap"] = best
        rows.append(r)
    return rows


def sweeps():
    rows = []
    for p in sorted(glob.glob(os.path.join(CONCEPTS, "sweeps", "*.json"))):
        try:
            D = load(p)
            if D is None: warn(f"{os.path.relpath(p, REPO)}: not valid JSON, skipped"); continue
            rows += sweep_rows(slug(os.path.splitext(os.path.basename(p))[0]), as_list(D, "configs", "rows", "results"))
        except Exception as e:
            warn(f"{os.path.relpath(p, REPO)}: skipped ({e})")
    return rows


# ---------------------------------------------------------------- judged, events
def judged():
    try:
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "judged_history.py")], cwd=REPO, capture_output=True, text=True, timeout=300)
        rows = json.loads(out.stdout) if out.returncode == 0 else []
        if out.returncode != 0: warn(f"judged_history.py exited {out.returncode}: {out.stderr.strip()[-200:]}")
    except Exception as e:
        warn(f"judged_history.py failed: {e}"); rows = []
    D = os.path.join(REPO, "pipeline", "full-exo", "designs")
    for r in rows:
        # judged_history dates a design by the commit that added its score.json; a build judged hours before it was
        # committed keeps its judge time in the file's mtime (git checkouts only make mtimes later), so take the earlier
        t, dd = when(r.get("time")), os.path.join(D, str(r.get("design")))
        fs = [f for f in (f"{dd}/score.json", f"{dd}/score_14mm.json", f"{dd}/judge/workspace.json", f"{dd}/judge/part_contact.json", f"{dd}/judge/dynamics.json") if os.path.exists(f)]
        if fs:
            m = when(mtime(fs[0]))
            if m and (t is None or m < t): t = m
        r["time"] = iso(t)
    rows = [r for r in rows if r.get("time")]
    rows.sort(key=lambda r: r["time"])
    return rows


def events(old_path):
    rows = []
    hist = os.path.join(CONCEPTS, "events_history.json")
    src = hist if os.path.exists(hist) else old_path
    old = as_list(load(src), "events") if src and os.path.exists(src) else []
    if not old: warn(f"older event history not found ({hist} or {old_path}): the log starts at docs/concepts/events.jsonl")
    rows += [r for r in old if isinstance(r, dict)]
    p = os.path.join(CONCEPTS, "events.jsonl")
    if os.path.exists(p):
        for n, line in enumerate(open(p), 1):
            line = line.strip()
            if not line: continue
            try: rows.append(json.loads(line))
            except ValueError: warn(f"events.jsonl line {n}: not JSON, skipped")
    out, seen = [], set()
    for r in rows:
        if not isinstance(r, dict): continue
        t, ev = norm_time(r.get("time") or r.get("t")), str(r.get("event") or r.get("text") or "").strip()
        if not t or not ev or (t, ev) in seen: continue
        seen.add((t, ev)); k = str(r.get("kind") or "milestone").lower()
        k = {"decision": "milestone", "measurement change": "measurement"}.get(k, k)
        row = dict(time=t, kind=k if k in KINDS else "milestone", event=ev)
        aff = r.get("affects")
        if isinstance(aff, list) and aff: row["affects"] = ",".join(str(a) for a in aff)
        out.append(row)
    out.sort(key=lambda r: r["time"])
    return out


# ---------------------------------------------------------------- reqs
# id, short name, target text, direction ('hi' / 'lo' / 'bool'), pass threshold, unit, state when nothing measured it
REQS = [
    ("R1", "Skin 2-14 mm from the metal while following", ">= 90%", "hi", 0.90, "%", "not measured"),
    ("R1-aim", "Skin 2-10 mm from the metal (the 1 cm aim)", ">= 90%", "hi", 0.90, "%", "not measured"),
    ("R2", "No part enters the body", "<= 0.5 mm", "lo", 0.5, "mm", "not measured"),
    ("R3", "Follows the arm (frames tracked)", ">= 95%", "hi", 0.95, "%", "not measured"),
    ("R4", "Overhead works (Raise overhead, 14 mm band)", ">= 80%", "hi", 0.80, "%", "not measured"),
    ("R5", "Shoulder-chain DOF", "<= 4", "lo", 4, "", "not measured"),
    ("R5-aim", "Exactly 3 DOF, the minimum", "3", "lo", 3, "", "not measured"),
    ("R6", "No interference between moving parts", "<= 0.15 mm", "lo", 0.15, "mm", "not measured"),
    ("R7", "Every custom part is one valid solid", "all parts", "bool", True, "", "not measured"),
    ("R8", "Custom-part mass", "<= 500 g", "lo", 500, "g", "not measured"),
    ("R9", "Strength SF >= 1.5 (independent FEA)", "SF >= 1.5", "hi", 1.5, "", "not measured"),
    ("R10", "Base slip on the scapula (GH-centre misalignment)", "<= 4 mm", "lo", 4.0, "mm", "not measured"),
    ("R11", "Pressure the exo adds on the cuff", "<= 7.5 kPa", "lo", 7.5, "kPa", "not measured"),
    ("R12", "CAD standard: G2 surfaces, no visible screws", "your review", None, None, "", "needs the user"),
    ("R13", "Manufacturable (supplier review and quote)", "supplier yes", None, None, "", "not measured"),
    ("R14", "Holds on motions and bodies never used to design it", "held-out data", None, None, "", "not measured"),
    ("R15", "Works on real bodies (printed prototype)", "prototype on you", None, None, "", "needs the user"),
    ("R16", "Everyday arm poses reached", ">= 90%", "hi", 0.90, "%", "not measured"),
    ("R17", "Moves freely unpowered", "yes", "bool", True, "", "not measured"),
]
JUDGED_COL = {"R1": "r1_14", "R1-aim": "r1_10", "R3": "follow", "R4": "overhead_14", "R16": "range_r16", "R6": "parts_mm",
              "R17": "moves_freely", "R5": "dof", "R5-aim": "dof"}
# When the judging (or what the designs were built from) changed so that earlier numbers of a requirement are not
# comparable with later ones - the 'measurement' events of 2026-10-15 (Log). A later event can add itself with
# "affects": ["R1", ...] in docs/concepts/events.jsonl.
RULES = [
    (("R3", "R4", "R6", "R2"), "2026-10-15T02:44:38Z", "the contact-judge fix (02:44 UTC)"),
    (("R1", "R1-aim", "R4"), "2026-10-15T11:55:00Z", "the held-out-leak fix (11:55 UTC)"),
]


def rules_from(ev):
    out = {}
    for reqs_, t, why in RULES:
        for r in reqs_: out[r] = max(out.get(r, ("", "")), (t, why))
    for e in ev:
        if e.get("kind") == "measurement" and e.get("affects"):
            for r in str(e["affects"]).split(","):
                r = r.strip()
                if r: out[r] = max(out.get(r, ("", "")), (e["time"], e["event"][:90]))
    return out


def fmt_val(v, unit):
    if isinstance(v, bool): return "yes" if v else "no"
    if unit == "%": return f"{100 * v:.1f}%"
    if isinstance(v, float) and not float(v).is_integer(): return f"{v:.2f} {unit}".strip() if v < 10 else f"{v:.1f} {unit}".strip()
    return f"{int(v)} {unit}".strip() if isinstance(v, (int, float)) else str(v)


def passes(v, d, thr):
    if v is None or d is None: return None
    if d == "bool": return bool(v) is bool(thr)
    return v >= thr if d == "hi" else v <= thr


def card_time(p):
    """when a scorecard was last written: its newest commit, or its mtime while it has uncommitted changes"""
    rel = os.path.relpath(p, REPO)
    return mtime(p) if dirty(rel) else (git_times(rel, last=True) or mtime(p))


def r6_note(design):
    pc = load(os.path.join(REPO, "pipeline", "full-exo", "designs", str(design), "judge", "part_contact.json")) or {}
    if not isinstance(pc, dict) or pc.get("max_depth") not in (0, 0.0): return ""
    bits = []
    if pc.get("step") and to_int(pc["step"], 1) > 1: bits.append(f"every {to_int(pc['step'])}th frame checked")
    opn = pc.get("open_parts_not_tested_as_container") or []
    if opn: bits.append(f"{len(opn)} open part{'s' if len(opn) != 1 else ''} not tested as containers")
    return "to confirm: 0 overlap found" + (" (" + "; ".join(bits) + ")" if bits else "")


def reqs(jrows, ev):
    rules = rules_from(ev)
    cand = {r[0]: [] for r in REQS}                    # req -> [(value, status or None, design, time, judge)]
    for p in glob.glob(os.path.join(REPO, "pipeline", "full-exo", "designs", "*", "judge", "scorecard.json")):
        sc = load(p)
        if not isinstance(sc, list): continue
        by = {r.get("id"): r for r in sc if isinstance(r, dict)}
        if (by.get("R5") or {}).get("value") not in (3, 3.0): continue          # the user's goal: 3-DOF designs only
        design = p.split(os.sep)[-3]; t = card_time(p)
        for rid in cand:
            r = by.get(rid)
            if r: cand[rid].append((r.get("value"), str(r.get("status") or "").upper(), design, t, str(r.get("judge") or "")))
    for j in jrows:
        if to_int(j.get("dof"), 0) != 3: continue
        for rid, col in JUDGED_COL.items():
            if j.get(col) is not None: cand[rid].append((j[col], None, j["design"], j["time"], "judged"))
    out = []
    for rid, name, target, d, thr, unit, idle in REQS:
        cs = cand[rid]
        sc = [c for c in cs if c[4] != "judged"]
        if sc:                                          # keep only the newest judge's measurements (a judge that changed)
            newest = max(sc, key=lambda c: c[3] or "")[4]
            cs = [c for c in cs if c[4] in (newest, "judged")]
        since, why = rules.get(rid, (None, ""))
        row = dict(req=rid, name=name, target=target, best="", design="", state=idle, note="", older_best="", rules_since=since, rules_why=why)
        num = [c for c in cs if isinstance(c[0], (int, float, bool)) and c[0] is not None]
        if num and d:
            def ok(c): return c[1] == "PASS" if c[1] in ("PASS", "FAIL") else passes(c[0], d, thr)
            key = (lambda c: (bool(ok(c)), bool(c[0]))) if d == "bool" else (lambda c: (bool(ok(c)), c[0] if d == "hi" else -c[0]))
            pick = lambda xs: max(xs, key=lambda c: (key(c), c[3] or ""))
            cur = [c for c in num if not since or (c[3] or "") >= since]
            b = pick(cur or num)
            row.update(best=fmt_val(b[0], unit), design=b[2], state="pass" if ok(b) else "fail")
            if not cur: row["note"] = "measured before " + why
            else:
                o = pick(num)
                if o is not b and key(o) > key(b): row["older_best"] = f"{fmt_val(o[0], unit)} ({o[2]}, before {why})"
            if rid == "R6" and b[0] in (0, 0.0): row["note"] = r6_note(b[2])
        out.append(row)
    return out


# ---------------------------------------------------------------- cov3d
def cov3d(src, keep=8):
    rows = None
    try:
        tmp = os.path.join(SCRATCH if os.path.isdir(SCRATCH) else REPO, ".dash_cov3d.json")
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "coverage3d.py"), "-o", tmp], cwd=REPO, capture_output=True, text=True, timeout=300)
        if out.returncode == 0: rows = load(tmp)
        else: warn(f"coverage3d.py exited {out.returncode}: {out.stderr.strip()[-200:]}")
        if os.path.exists(tmp): os.remove(tmp)
    except Exception as e:
        warn(f"coverage3d.py failed: {e}")
    if not isinstance(rows, list) or not rows:
        p = src
        if src and os.path.isdir(src):
            c = sorted(glob.glob(os.path.join(src, "**", "cov3d*.json"), recursive=True), key=os.path.getmtime)
            p = c[-1] if c else None
        rows = load(p, []) if p else []
        if rows: warn(f"cov3d: copied the stale file {p} (coverage3d.py gave nothing)")
    if not isinstance(rows, list): return []
    order = list(dict.fromkeys(r.get("design") for r in rows if isinstance(r, dict)))   # judged order, newest last
    keepset = set(order[-keep:])
    return [r for r in rows if isinstance(r, dict) and r.get("design") in keepset]


# ---------------------------------------------------------------- SAMPLE (harness only)
SAMPLE_NAMES = [
    ("Scapular-plane 3R, tilted first axis", "spherical", "robotics"), ("Offset-axis 3R hugging the deltoid", "spherical", "anatomy"),
    ("Remote-centre arc + 2R", "arc rail", "robotics"), ("Curved rail over the acromion + 2R", "arc rail", "aerospace"),
    ("Double parallelogram RCM", "parallel", "surgery robots"), ("Bennett-linkage shoulder", "overconstrained", "kinematics"),
    ("Tensegrity cap with 3 struts", "tensegrity", "biology"), ("Origami waterbomb shell", "origami", "origami"),
    ("Scissor dome over the cap", "scissor", "deployables"), ("Gimbal ring around the humerus", "gimbal", "aerospace"),
    ("Back-mounted 3R, axis through GH", "spherical", "robotics"), ("Clavicle-follow 3R", "spherical", "anatomy"),
    ("Helical humeral sleeve + 2R", "sleeve", "biology"), ("Sliding-cuff 3R (passive slide)", "spherical", "robotics"),
    ("Cable-free Sarrus cap", "overconstrained", "kinematics"), ("Pantograph over the deltoid", "parallel", "drafting tools"),
    ("Two arcs crossing at the cap", "arc rail", "astronomy mounts"), ("Bowden-ready 3R, low hubs", "spherical", "bike mech"),
    ("Exo-tendon strap chain", "compliant", "biology"), ("Compliant flexure shell", "compliant", "MEMS"),
    ("Insect-wing hinge 3R", "spherical", "biology"), ("Shoulder-pad cardan", "gimbal", "sports gear"),
    ("Belt-ring on the trunk + 2R", "ring", "rehab devices"), ("Telescoping arc link", "arc rail", "deployables"),
    ("Watt-linkage drop link", "planar+R", "kinematics"), ("Armour-plate lames", "segmented", "history"),
    ("Snake spine over the cap", "segmented", "biology"), ("Delta-style 3-leg cap", "parallel", "robotics"),
    ("Hoberman ring around the arm", "scissor", "deployables"), ("Rolling-contact cap joint", "rolling", "prosthetics"),
    ("Ball-in-socket shell, 3 sensors", "shell", "anatomy"), ("Scapula-glide + 2R", "spherical", "anatomy"),
    ("Low-profile 3R with ring bearings", "spherical", "bearings"), ("Elastic cap, bistable", "compliant", "origami"),
    ("Spherical 4-bar + R", "overconstrained", "kinematics"), ("Front-side 3R, axilla clear", "spherical", "robotics"),
    ("Saddle rail behind the shoulder", "arc rail", "saddlery"), ("Pivoting epaulette", "gimbal", "tailoring"),
    ("Cam-guided cuff slide 3R", "spherical", "cams"), ("Ring-and-arc hybrid", "ring", "aerospace"),
]


def sample():
    rnd = random.Random(7)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    t0 = now - dt.timedelta(hours=9, minutes=40)
    M = [finish(merge(blank("baseline-3r"), dict(name="Spherical 3R (current champion)", family="spherical", lens="baseline", status="judged",
                                                is_baseline=True, t_ideated=iso(t0 - dt.timedelta(hours=10)), t_screened=iso(t0),
                                                reach=0.75, follow=0.97, inband14=0.40, inband10=0.19, contact=0.0, n_configs=None,
                                                verdict="the bar to beat", note="same bench, simple straps", doc="docs/concepts/README.md")))]
    S, E = [], []
    # (status, quality 0-1, fixed screening time before now or None); quality ~0.55 is about the baseline's gap
    plan = [("cad", .78, None), ("gpu", .72, None), ("verified", .88, 85), ("verified", .62, None), ("verified", .60, None), ("verified", .66, None),
            ("refuted", .72, None), ("refuted", .70, None), ("refuted", .69, None), ("dead", .15, None), ("dead", .20, None),
            ("screened", .76, 20), ("screened", .64, 50)] + [("screened", rnd.uniform(.22, .54), None) for _ in range(15)] + \
           [("modelling", 0, None)] * 4 + [("ideated", 0, None)] * 8
    order = list(range(len(SAMPLE_NAMES))); rnd.shuffle(order)
    free = [rnd.uniform(25, 9 * 60 - 60) for _ in plan]
    for n_, (st, q, ago) in enumerate(plan):
        name, fam, lens = SAMPLE_NAMES[order[n_]]; mid = slug(name)[:40]
        m = merge(blank(mid), dict(name=name, family=fam, lens=lens, status=st, active_dof=3, passive_dof=1 if "slide" in name.lower() else 0,
                                   t_ideated=iso(t0 + dt.timedelta(minutes=rnd.randint(-40, 10))), doc=f"docs/concepts/{mid}.md"))
        if st not in ("ideated", "modelling"):
            tscr = (now - dt.timedelta(minutes=ago)) if ago else (t0 + dt.timedelta(minutes=free[n_]))
            if st in ("cad", "gpu"): tscr = t0 + dt.timedelta(minutes=60 + 70 * (st == "gpu"))
            ib14 = 0.18 + 0.62 * q + rnd.uniform(-0.03, 0.03); fo = min(1, 0.80 + 0.22 * q + rnd.uniform(-0.02, 0.02))
            re_ = min(1, 0.45 + 0.45 * q + rnd.uniform(-0.04, 0.04)); co = max(0.0, rnd.uniform(-0.03, 0.03) * (1.2 - q))
            if st == "dead": co = rnd.uniform(0.15, 0.4); ib14 *= 0.5
            n = rnd.randint(10, 60) if st != "dead" else rnd.randint(4, 9)
            m.update(n_configs=n)
            tsw = when(m["t_ideated"]); dtk = (tscr - tsw) / max(n, 1)          # the sweep: noisy configurations converging on the best
            items, bestk = [], rnd.randint(int(n * 0.4), n)
            for k in range(1, n + 1):
                f = (k / n) ** 0.5; noise = rnd.uniform(0.6, 1.0)
                if k == bestk: x = dict(inband14=ib14, follow=fo, reach=re_, contact=co)
                else: x = dict(inband14=ib14 * (0.55 + 0.4 * f) * noise, follow=fo * (0.9 + 0.08 * f * noise), reach=re_ * (0.75 + 0.22 * f * noise), contact=co + rnd.uniform(0, 0.12) * (1 - f))
                x["inband10"] = x["inband14"] * rnd.uniform(0.42, 0.55)
                items.append(dict(k=k, t=iso(tsw + dtk * k), **{a: round(min(1, max(0, b)), 4) for a, b in x.items()}))
            S += sweep_rows(mid, items)
            m.update(t_screened=iso(tscr), inband14=round(ib14, 4), inband10=round(ib14 * 0.48, 4), follow=round(fo, 4), reach=round(re_, 4), contact=round(co, 4))
            if st in ("verified", "gpu", "cad", "refuted"):
                k = 0.97 if st != "refuted" else 0.72
                m.update(v_inband14=round(ib14 * k, 4), v_inband10=round(ib14 * 0.46 * k, 4), v_follow=round(fo * (0.995 if st != "refuted" else 0.93), 4),
                         v_reach=round(re_ * (0.98 if st != "refuted" else 0.8), 4))
            m["verdict"] = {"cad": "keep-out CAD being built", "gpu": "GPU sweep running", "verified": "verified: worth a GPU sweep",
                            "refuted": "refuted: the bench skipped the axilla poses", "dead": "dead: links cross the neck overhead",
                            "screened": "claimed: waiting for the verifier" if q > .6 else rnd.choice(["below baseline", "plateaued early", "needs a lower hub"])}[st]
            m["note"] = rnd.choice(["hub stack 12 mm", "links ride 6 mm over the deltoid", "overhead blocked by the acromion", "", "passive slide sets the closure"])
        M.append(finish(m))
    rec = None                                          # leader changes as events
    for m in sorted([m for m in M[1:] if m["gap"] is not None and m["status"] not in ("refuted", "dead")], key=lambda m: m["t_screened"]):
        g = m["v_gap"] if m["v_gap"] is not None else m["gap"]
        if rec is None or g < rec:
            rec = g; E.append(dict(time=m["t_screened"], kind="leader", event=f"New leader: {m['name']} (gap {g:.1f})"))
    E += [dict(time=iso(t0 - dt.timedelta(minutes=30)), kind="method", event="Swarm starts: 40 morphologies ideated across 12 lenses"),
          dict(time=iso(t0 + dt.timedelta(minutes=5)), kind="measurement", event="Baseline 3R measured on the concept bench (gap 65.0)"),
          dict(time=iso(now - dt.timedelta(hours=3)), kind="infra", event="Verifier agent online: re-measures every claimed winner"),
          dict(time=iso(now - dt.timedelta(hours=2, minutes=10)), kind="milestone", event="First verified winner sent to a GPU sweep"),
          dict(time=iso(now - dt.timedelta(minutes=50)), kind="milestone", event="Keep-out CAD build started for the old leader")]
    E.sort(key=lambda r: r["time"])
    return M, S, E


# ---------------------------------------------------------------- main
def write(out, name, rows, extra="", guard=False):
    """guard: a subprocess-built dataset that comes out empty never replaces a file that holds rows"""
    p = os.path.join(out, name + ".json")
    if guard and not rows:
        old = load(p)
        if isinstance(old, list) and old:
            warn(f"{name}: the new build is empty; kept the previous {len(old)} rows in {p}")
            print(f"{name:7s} {len(old):5d} rows  KEPT (new build empty)"); return
    with open(p, "w") as f: json.dump(rows, f, separators=(",", ":"))
    print(f"{name:7s} {len(rows):5d} rows  {extra}".rstrip())


def head_commit():
    try: return subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception: return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None)
    ap.add_argument("--sample", action="store_true", help="write SAMPLE data for the test harness (never publish)")
    ap.add_argument("--events-old", default=DEF_EVENTS_OLD)
    ap.add_argument("--cov3d", default=DEF_COV3D)
    a = ap.parse_args()
    out = a.out or (os.path.join(SCRATCH, "dash2", "sample_data") if a.sample else DEF_OUT)
    os.makedirs(out, exist_ok=True)
    if a.sample:
        M, S, E = sample()
        E = events_merge_sample(E, a.events_old)
    else:
        S = sweeps()
        counts = {}
        for r in S: counts[r["id"]] = counts.get(r["id"], 0) + 1
        M = morphs(counts); E = events(a.events_old)
    J = judged(); R = reqs(J, E); C = cov3d(a.cov3d)
    base = next((m for m in M if m["is_baseline"]), None)
    scr = [m for m in M if not m["is_baseline"] and m["gap"] is not None]
    best = min(scr, key=lambda m: m["v_gap"] if m["v_gap"] is not None else m["gap"], default=None)
    write(out, "morphs", M, f"{len(M) - (base is not None)} morphologies, {len(scr)} screened, baseline gap {base['gap'] if base else '-'}, best {best['name'] + ' ' + str(best['v_gap'] if best['v_gap'] is not None else best['gap']) if best else '-'}" + (" (SAMPLE)" if a.sample else ""))
    write(out, "sweeps", S, f"{len({r['id'] for r in S})} morphologies")
    write(out, "judged", J, f"{sum(1 for r in J if r.get('dof') == 3)} with 3 DOF, newest {J[-1]['design'] if J else '-'}", guard=True)
    write(out, "events", E, f"newest {E[-1]['time'] if E else '-'}")
    write(out, "reqs", R, f"{sum(1 for r in R if r['state'] == 'pass')} pass")
    write(out, "cov3d", C, f"{len({r.get('design') for r in C})} designs, newest {C[-1]['design'] if C else '-'}", guard=True)
    meta = [dict(built_at=iso(dt.datetime.now(dt.timezone.utc)), commit=head_commit(), sample=bool(a.sample),
                 n_warnings=len(WARN), warnings=" | ".join(WARN)[:2000])]
    write(out, "meta", meta, f"built {meta[0]['built_at']}" + (f", {len(WARN)} warning(s)" if WARN else ""))
    print("->", out)


def events_merge_sample(E, old_path):
    old = events(old_path)
    rows = old + E; rows.sort(key=lambda r: r["time"]); return rows


if __name__ == "__main__":
    main()
