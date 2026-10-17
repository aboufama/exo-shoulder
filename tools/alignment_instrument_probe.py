"""Outside check of a change to the alignment auditor's own instrument (tools/alignment_audit.py). READ-ONLY: it loads the
tool, the rows, the models' SOURCE text and the skeptics' rulings, runs the tool's checks in memory, and writes one JSON.
It never edits a row, a model, a ruling or the tool.

Written for VERSION 2026-10-17.3 (commit 19cfa4a): (1) the idle check's rigid-knee assertion matches only the literal
assignment r["knee_moved"] = True; (2) the self-test counts an upheld ruling on a RECORD check (complexity) that now reads
ok as 'resolved'. Questions it measures:
  idle   - does the narrower regex miss a real rigid-knee assertion written another way in any model under
           docs/concepts/models/? Which rows changed reading old -> new, and is any pin knee left unchecked?
  record - which upheld rulings sit on record-type checks (complexity / reporting / rules), what does each read now, is
           the complexity check still sensitive at the instrument's quantum (0.25) and on its hard-rule branches
           (active DOF > 4, passive translations > 2), which those branches share with the 'resolvable' record branch?

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_instrument_probe.py [out.json]
"""
import copy, glob, importlib.util, json, os, re, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_sp = importlib.util.spec_from_file_location("aa_probe", os.path.join(REPO, "tools", "alignment_audit.py"))
AA = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AA)

NEW = re.compile(r"""\[["']knee_moved["']\]\s*=\s*True""")           # the tool's 2026-10-17.3 pattern (copied, compared below)
OLD = re.compile(r"knee_moved")                                        # the 2026-10-17.2 pattern
BROAD = re.compile(r"""(\[["']knee_moved["']\]\s*\|?=\s*(?!=)|\bknee_moved\s*=\s*(?!=)|["']knee_moved["']\s*:|setattr\([^)]*["']knee_moved["']"""
                   r"""|\[["'](knee|bracket|rigid)_\w*(moved|drift|broke)\w*["']\]\s*=(?!=))""")
FORMS = ['r["knee_moved"] = True', "r['knee_moved']=True", 'r.update(knee_moved=True)', 'r = dict(r, knee_moved=True)',
         'out = {"knee_moved": True}', 'setattr(r, "knee_moved", True)', 'r["knee_moved"] = not kc["ok"]',
         'r["knee_moved"] = bool(ptp > 0.5)', 'r["knee_moved"] = 1', 'r["knee_moved"] |= bad', 'r["bracket_moved"] = True',
         'if r.get("knee_moved"): r["honest"] = False', '# r["knee_moved"] = True  (a comment)']


def idle_probe():
    tool_pat = re.search(r'knee_assert = re\.search\(r"""(.+?)""", src\)', open(os.path.join(REPO, "tools", "alignment_audit.py")).read())
    out = dict(tool_pattern=tool_pat.group(1) if tool_pat else None, same_as_probe=bool(tool_pat and tool_pat.group(1) == NEW.pattern))
    models = {}
    for f in sorted(glob.glob(os.path.join(REPO, "docs", "concepts", "models", "*.py"))):
        s = open(f).read(); b = sorted({m.group(0).strip() for m in BROAD.finditer(s)})
        loads = sorted(set(re.findall(r"""os\.path\.join\(HERE,\s*["']([\w\-]+)\.py["']\)""", s)))
        if OLD.search(s) or b: models[os.path.basename(f)] = dict(new=bool(NEW.search(s)), old=bool(OLD.search(s)), broad_forms=b, loads_parents=loads)
    out["models"] = models
    out["missed_by_new"] = [m for m, d in models.items() if d["broad_forms"] and not d["new"]]
    out["forms"] = {x: dict(new=bool(NEW.search(x)), broad=bool(BROAD.search(x))) for x in FORMS}
    rows, orig = [], AA._declared_joints

    def with_cuff_knee(row):                                           # PROPOSAL reading, in memory only
        mv, rg = orig(row); ck = (row.get("mechanism") or {}).get("cuff_knee")
        if isinstance(ck, dict) and (ck.get("joints") or 0) > 0 and "knee" not in rg and "knee" not in mv:
            mv["knee"] = "PROPOSAL: mechanism.cuff_knee (joints > 0), no rigid assertion"
        return mv, rg
    for f in sorted(glob.glob(os.path.join(REPO, "docs", "concepts", "rows", "*.json"))):
        try:
            row = json.load(open(f))
        except Exception:
            continue
        src = AA._model_src(row)
        if not src or bool(OLD.search(src)) == bool(NEW.search(src)) and not (row.get("mechanism") or {}).get("cuff_knee"): continue
        rid = row["id"]; V = AA._verifier_outputs(rid); rb = AA._remeasured(rid, "bench")
        a = AA.c_idle(row, V, rb); AA._declared_joints = with_cuff_knee
        try:
            b = AA.c_idle(row, V, rb)
        finally:
            AA._declared_joints = orig
        ck = (row.get("mechanism") or {}).get("cuff_knee")
        rows.append(dict(id=rid, status=row.get("status"), reading_changed_old_to_new=bool(OLD.search(src)) != bool(NEW.search(src)),
                         cuff_knee_joints=ck.get("joints") if isinstance(ck, dict) else None, declared=a.get("declared"), rigid=a.get("rigid"),
                         knee_checked="knee" in (a.get("declared") or []) or "knee" in (a.get("rigid") or []),
                         level_now=a["level"], level_proposal=b["level"], reason_proposal=b["reason"][-220:]))
    out["rows"] = rows
    out["pin_knee_unchecked"] = [r["id"] for r in rows if r["cuff_knee_joints"] and not r["knee_checked"]]
    return out


def record_probe():
    out = dict(record_checks=sorted(getattr(AA, "RECORD_CHECKS", set())), rulings=[], mutations=[])
    for f in sorted(glob.glob(os.path.join(REPO, "docs", "alignment", "*.rulings.json"))):
        rid = os.path.basename(f)[:-len(".rulings.json")]
        if not os.path.exists(os.path.join(AA.ROWS, rid + ".json")): continue
        row = AA._row(rid)
        for r in AA._rulings(rid):
            k = str(r.get("key", ""))
            if k not in ("complexity", "reporting", "rules"): continue
            c = AA.c_complexity(row) if k == "complexity" else AA.c_rules(row) if k == "rules" else AA.c_reporting(row, AA._verifier_outputs(rid))
            ev = str(r.get("evidence", ""))
            out["rulings"].append(dict(id=rid, key=k, refuted=bool(r.get("refuted")), now=c["level"], reason_now=c["reason"][:160],
                                       counted_resolved=(not r.get("refuted")) and c["level"] == "ok" and k in out["record_checks"],
                                       hard_rule_in_evidence=bool(re.search(r"active dof|dof cap|> ?cap|passive translations? ?>", ev, re.I)),
                                       ruled_numbers_on_file=bool(re.search(r"\d", ev))))
    for rid in [x for x in ("roller-longdyad-knuckle-3r", "slipper-nose-knuckle-3r", "minarc-stop-knuckle-4r") if os.path.exists(os.path.join(AA.ROWS, x + ".json"))]:
        base = AA._row(rid)
        for name, fn in (("field +0.25", lambda r: r.__setitem__("complexity", float(r["complexity"]) + 0.25)),
                         ("field +4 (the tool's own mutation)", lambda r: r.__setitem__("complexity", float(r["complexity"]) + 4.0)),
                         ("active_dof 5", lambda r: r["mechanism"].__setitem__("active_dof", 5)),
                         ("passive_trans 3", lambda r: r["mechanism"].__setitem__("passive_trans", 3))):
            row = copy.deepcopy(base); fn(row); out["mutations"].append(dict(id=rid, mutation=name, level=AA.c_complexity(row)["level"]))
    return out


if __name__ == "__main__":
    t = time.time()
    res = dict(tool_version=AA.VERSION, git=AA._git("rev-parse", "--short", "HEAD"), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               idle=idle_probe(), record=record_probe())
    res["secs"] = round(time.time() - t, 1)
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AA.REM, f"instrument_{AA.VERSION}_probe.json")
    json.dump(res, open(path, "w"), indent=1, default=str)
    I, R = res["idle"], res["record"]
    print(f"tool {AA.VERSION}: pattern same as probe {I['same_as_probe']}; models with any knee_moved text {len(I['models'])}, "
          f"assertions the new pattern misses {I['missed_by_new']}; rows changed old->new {sum(r['reading_changed_old_to_new'] for r in I['rows'])}; "
          f"pin knees left unchecked {I['pin_knee_unchecked']}; record rulings {len(R['rulings'])} "
          f"(resolved {sum(r['counted_resolved'] for r in R['rulings'])}, hard-rule evidence {sum(r['hard_rule_in_evidence'] for r in R['rulings'])}); "
          f"mutations {[(m['mutation'], m['level']) for m in R['mutations'][:4]]} -> {path}")
