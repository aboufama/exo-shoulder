"""Alignment ledger: the loop's standing record of which numbers are evidence of a better exo (docs/ALIGNMENT.md).

The user (2026-10-16 ~20:10 UTC): "require an agent on the side that is a superfan that targets misalignment ... see if
models are cheating the system or gaming the system in some way to score higher without actually being better ... it
needs to be a crucial part of our loop". tools/alignment_audit.py measures; this file RECORDS, append-only, one JSON line
per ruling in docs/alignment/ledger.jsonl, and computes every verdict itself so no agent does the arithmetic by hand:

    python3 tools/alignment_ledger.py append <id> [--findings f.json] [--by auditor] [--run label] [--note txt]
        after `alignment_audit.py audit <id>`: reasons = every check of docs/alignment/<id>.json that is not 'ok' plus the
        auditor's judgement findings (f.json: [{"key": "T1", "level": "watch|gamed", "reason": "...", "evidence": "..."}]);
        verdict = the worst level. The judgement pass can only ADD reasons (raise a verdict), never lower the tool's.
    python3 tools/alignment_ledger.py skeptic <id> --rulings r.json [--by skeptic] [--run label]
        r.json: [{"key": "<reason key>", "refuted": true|false, "evidence": "..."}]. Final verdict = the worst level among
        the reasons of the latest 'audit' entry that the skeptic did NOT refute with evidence (an unruled reason stands).
    python3 tools/alignment_ledger.py latest [--json]       latest verdict per id (what the dashboard and the closer read)
    python3 tools/alignment_ledger.py get <id>              latest entry for one id (JSON; exit 3 if 'gamed')
    python3 tools/alignment_ledger.py due [--since ISO] [--json]
        ids that need an audit now: a claim-bearing row (verified / screened / cad / gpu) with no ledger entry, whose
        claimed number moved since its last entry, or whose row / verifier files were committed after it; and EVERY
        verified row when a bench / judge / metric / kit file changed since --since (a judge / metric change).
    python3 tools/alignment_ledger.py seed                  one 'audit' entry (by 'seed') per docs/alignment/<id>.json
                                                            that has no ledger entry yet (time = the audit file's own t)

Entry: {time, id, verdict, reasons: [str], claim, claim_field, claims: {v_gap, gap, polished_gap}, status, stage
(audit | skeptic), by, run, tool_verdict, reason_items: [{key, level, reason}], refuted: [{key, evidence}], git, note}.
'gamed' = the number, as it stands, is not evidence of a better exo (CLAUDE.md: such a design cannot be called verified,
a winner or a leader until the finding is resolved). A later entry for the same id supersedes an earlier one.
Never edits a row, a bench, a judge or a model.
"""
import fcntl, glob, json, os, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "docs", "alignment")
LEDGER = os.environ.get("ALIGN_LEDGER") or os.path.join(OUT, "ledger.jsonl")   # ALIGN_LEDGER: a scratch ledger for tests
ROWS = os.path.join(REPO, "docs", "concepts", "rows")
RANK = {"clean": 0, "ok": 0, "watch": 1, "gamed": 2}
CLAIM_STATUSES = ("verified", "screened", "cad", "gpu")
try:                                     # the audit tool's list of measurement code (bench, kit, judges, metric, split)
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from alignment_audit import MEASURE_PATHS
except Exception:
    MEASURE_PATHS = ("tools/concept_bench.py", "tools/concept_kit.py", "tools/env_bench.py", "tools/simplicity.py", "judge/",
                     "tools/judge_all.sh", "tools/concept_bigbench.py", "pipeline/avg/body_pose.py", "data/raw/split.json")


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def git(*a):
    try:
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


def num(x):
    try:
        v = float(x); return v if v == v and abs(v) != float("inf") else None
    except Exception:
        return None


def worst(levels):
    lv = max((RANK.get(str(x), 0) for x in levels), default=0)
    return {0: "clean", 1: "watch", 2: "gamed"}[lv]


def row(rid):
    try:
        return json.load(open(os.path.join(ROWS, rid + ".json")))
    except Exception:
        return {}


def claim_of(r):
    """the number the row claims: the verifier's v_gap when there is one, else the agent's gap"""
    claims = {k: num(r.get(k)) for k in ("v_gap", "gap", "polished_gap") if num(r.get(k)) is not None}
    for k in ("v_gap", "gap"):
        if claims.get(k) is not None: return claims[k], k, claims
    return None, None, claims


def entries(path=LEDGER):
    out = []
    if not os.path.exists(path): return out
    for i, line in enumerate(open(path)):
        line = line.strip()
        if not line: continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        if isinstance(e, dict) and e.get("id"): e["_n"] = i; out.append(e)
    return out


def latest_by_id(path=LEDGER):
    """{id: latest entry} - the dashboard (tools/dash_build.py) and the loop's closer read this"""
    best = {}
    for e in entries(path):
        k = (str(e.get("time") or ""), e["_n"])
        if e["id"] not in best or k >= (str(best[e["id"]].get("time") or ""), best[e["id"]]["_n"]): best[e["id"]] = e
    return best


def write(e):
    os.makedirs(OUT, exist_ok=True)
    e = {k: v for k, v in e.items() if not k.startswith("_")}
    line = json.dumps(e, separators=(",", ":"), ensure_ascii=False, default=str) + "\n"
    with open(LEDGER, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX); f.write(line); f.flush(); fcntl.flock(f, fcntl.LOCK_UN)
    return e


def opt(argv, k, d=None):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else d


def items_from_audit(a):
    return [dict(key=c["check"], level=c["level"], reason=c.get("reason", "")) for c in a.get("checks", []) if RANK.get(c.get("level"), 0) > 0]


def base_entry(rid, stage, by, run):
    r = row(rid); c, cf, claims = claim_of(r)
    return dict(time=now(), id=rid, stage=stage, by=by, run=run, status=r.get("status"), claim=c, claim_field=cf, claims=claims,
                git=git("rev-parse", "--short", "HEAD"))


def cmd_append(argv):
    rid = argv[2]; p = os.path.join(OUT, rid + ".json")
    if not os.path.exists(p): sys.exit(f"no {os.path.relpath(p, REPO)}: run python3 tools/alignment_audit.py audit {rid} first")
    a = json.load(open(p))
    it = items_from_audit(a)
    fp = opt(argv, "--findings")
    if fp:
        F = json.load(open(fp))
        for f in (F if isinstance(F, list) else F.get("findings", [])):
            lv = str(f.get("level", "watch")).lower()
            if lv not in ("watch", "gamed"): continue          # judgement findings only add reasons
            key = "judgement:" + str(f.get("key") or f.get("pattern") or "?")
            while any(i["key"] == key for i in it): key += "'"          # keys stay unique: the skeptic rules on each
            it.append(dict(key=key, level=lv,
                           reason=str(f.get("reason", "")) + (f" [evidence: {f['evidence']}]" if f.get("evidence") else "")))
    v = worst(i["level"] for i in it)
    e = base_entry(rid, "audit", opt(argv, "--by", "auditor"), opt(argv, "--run", ""))
    e.update(verdict=v, tool_verdict=a.get("verdict"), reason_items=it,
             reasons=[f"{i['key']}: {i['reason']}" for i in it if i["level"] == v and v != "clean"],
             audit_file=os.path.relpath(p, REPO), audit_t=a.get("t"), note=opt(argv, "--note", ""))
    print(json.dumps(write(e), indent=1))


def cmd_skeptic(argv):
    rid = argv[2]; rp = opt(argv, "--rulings")
    if not rp: sys.exit("--rulings r.json is required")
    aud = [e for e in entries() if e["id"] == rid and e.get("stage") == "audit"]
    if not aud: sys.exit(f"no 'audit' entry for {rid} in the ledger: run append first")
    last = aud[-1]; R = json.load(open(rp)); R = R if isinstance(R, list) else R.get("rulings", [])
    ref = {str(x.get("key")): x for x in R if x.get("refuted") is True and str(x.get("evidence") or "").strip()}
    keep = [i for i in last.get("reason_items", []) if i["key"] not in ref]
    v = worst(i["level"] for i in keep)
    e = base_entry(rid, "skeptic", opt(argv, "--by", "skeptic"), opt(argv, "--run", ""))
    e.update(verdict=v, audit_verdict=last.get("verdict"), audit_time=last.get("time"), reason_items=keep,
             reasons=[f"{i['key']}: {i['reason']}" for i in keep if i["level"] == v and v != "clean"],
             refuted=[dict(key=k, evidence=str(x.get("evidence"))[:600]) for k, x in ref.items()],
             upheld=[str(x.get("key")) for x in R if str(x.get("key")) not in ref])   # a refutation without evidence upholds
    print(json.dumps(write(e), indent=1))


def cmd_latest(argv):
    L = latest_by_id()
    if "--json" in argv:
        print(json.dumps({k: {x: v for x, v in e.items() if not x.startswith("_")} for k, e in sorted(L.items())}, indent=1)); return
    for k, e in sorted(L.items(), key=lambda kv: (-RANK.get(kv[1].get("verdict"), 0), kv[0])):
        print(f"{e.get('verdict', '?'):6s} {k:40s} claim {e.get('claim')} ({e.get('claim_field')}) {e.get('stage')} by {e.get('by')} {e.get('time')}"
              + (" - " + "; ".join(e.get("reasons", []))[:220] if e.get("reasons") else ""))


def cmd_get(argv):
    e = latest_by_id().get(argv[2])
    if not e: print("null"); sys.exit(2)
    print(json.dumps({k: v for k, v in e.items() if not k.startswith("_")}, indent=1))
    if e.get("verdict") == "gamed": sys.exit(3)


def last_commit_time(*paths):
    t = git("log", "-1", "--format=%cI", "--", *paths)
    return t.replace("+00:00", "Z") if t else ""


def to_utc(t):
    """git %cI -> comparable UTC Z string (the repo's commits are in +00:00; other offsets are converted)"""
    import datetime as dt
    try:
        return dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return t


def due(since=None):
    L = latest_by_id(); out = {}
    rows = {os.path.basename(p)[:-5]: row(os.path.basename(p)[:-5]) for p in sorted(glob.glob(os.path.join(ROWS, "*.json")))}
    for rid, r in rows.items():
        if str(r.get("status") or "").lower() not in CLAIM_STATUSES: continue
        e = L.get(rid); c, cf, _ = claim_of(r)
        if e is None: out.setdefault(rid, []).append("no ledger entry"); continue
        if c is not None and (num(e.get("claim")) is None or abs(c - num(e.get("claim"))) > 0.005):
            out.setdefault(rid, []).append(f"claim {cf} {c} != audited {e.get('claim')}")
        t = to_utc(last_commit_time(f"docs/concepts/rows/{rid}.json", *glob.glob(os.path.join(REPO, "docs", "concepts", "verify", rid + "*"))))
        if t and t > str(e.get("time") or ""): out.setdefault(rid, []).append(f"row / verifier files committed {t} after the last audit {e.get('time')}")
    if since:
        meas = git("log", f"--since={since}", "--format=%h %s", "--", *MEASURE_PATHS).splitlines()
        if meas:
            why = f"measurement code changed since {since}: " + "; ".join(m[:70] for m in meas[:3])
            for rid, r in rows.items():
                if str(r.get("status") or "").lower() == "verified": out.setdefault(rid, []).append(why)
    return out


def cmd_due(argv):
    D = due(opt(argv, "--since"))
    if "--json" in argv: print(json.dumps([dict(id=k, why=v) for k, v in D.items()], indent=1)); return
    for k, v in D.items(): print(f"{k}: " + " | ".join(v))
    if not D: print("nothing due")


def cmd_seed(argv):
    L = latest_by_id(); n = 0
    for p in sorted(glob.glob(os.path.join(OUT, "*.json"))):
        try:
            a = json.load(open(p))
        except Exception:
            continue
        rid = a.get("id")
        if not rid or rid in L or "checks" not in a: continue
        it = items_from_audit(a); v = a.get("verdict") or worst(i["level"] for i in it)
        e = base_entry(rid, "audit", "seed (alignment_audit.py audit-all)", "")
        e.update(time=a.get("t") or now(), verdict=v, tool_verdict=a.get("verdict"), reason_items=it,
                 reasons=list(a.get("reasons") or []), audit_file=os.path.relpath(p, REPO), audit_t=a.get("t"), git=a.get("git"),
                 note="seeded from the tool's audit file; no judgement pass, skeptic pending")
        write(e); n += 1
    print(f"seeded {n} entr{'y' if n == 1 else 'ies'} -> {os.path.relpath(LEDGER, REPO)}")


if __name__ == "__main__":
    cmds = dict(append=cmd_append, skeptic=cmd_skeptic, latest=cmd_latest, get=cmd_get, due=cmd_due, seed=cmd_seed)
    if len(sys.argv) < 2 or sys.argv[1] not in cmds: print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](sys.argv)
