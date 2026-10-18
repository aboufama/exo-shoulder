"""Adapter: run tools/alignment_audit.py (UNCHANGED) on a row whose best_params is a JSON STRING, not an object.

Found 2026-10-18 by the alignment audit of lowarm-halfring-knuckle-3r: its row stores best_params as a string (the only row
in docs/concepts/rows/ that does), and the auditor's c_rules (bp.items()) and remeasure (dict(best_params)) crash on it. The
row's own verifier decodes it and lays it over the model's CELL_B dict (docs/concepts/verify/lowarm-halfring-knuckle-3r.py
lines 38-41); this adapter does the same, in memory only, so the audit reads the parameters the verifier wore. Nothing on
disk is edited: _row() and remeasure() are re-bound in this process to decode a string best_params.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_strparams_adapter.py audit <id> [--ref <id>]
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_strparams_adapter.py remeasure <id> bench|held [--cell-dict NAME]
        --cell-dict NAME: lay the row's params over the model module's dict NAME (e.g. CELL_B), as the verifier does
"""
import importlib.util, inspect, json, os, sys, tempfile, textwrap

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import alignment_audit as AA  # noqa: E402


def _decode(row):
    bp = row.get("best_params")
    if isinstance(bp, str):
        try:
            row["best_params"] = json.loads(bp)
        except Exception:
            row["best_params"] = {}
    return row


_orig_row = AA._row
AA._row = lambda rid: _decode(_orig_row(rid))

_src = textwrap.dedent(inspect.getsource(AA.remeasure))
_old = 'P = dict(row.get("best_params") or {})'
assert _src.count(_old) == 1, "alignment_audit.remeasure changed; update the adapter"
_ns = {}
exec(compile(_src.replace(_old, 'P = dict(_decode(row).get("best_params") or {})'), "aa_remeasure_strparams", "exec"),
     dict(AA.__dict__, _decode=_decode), _ns)
remeasure = _ns["remeasure"]


def main(argv):
    cmd = argv[1]
    if cmd == "audit":
        ref = argv[argv.index("--ref") + 1] if "--ref" in argv else None
        r = AA.audit(argv[2], ref=ref)
        print(json.dumps(dict(id=r["id"], verdict=r["verdict"], checks=[(c["check"], c["level"], c["reason"]) for c in r["checks"]]), indent=1, default=float))
    elif cmd == "remeasure":
        rid, wear = argv[2], argv[3]; params = None
        if "--cell-dict" in argv:
            name = argv[argv.index("--cell-dict") + 1]
            sp = importlib.util.spec_from_file_location("adp_model", os.path.join(AA.MODELS, rid + ".py"))
            m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
            row = _decode(json.load(open(os.path.join(AA.ROWS, rid + ".json"))))
            P = dict(getattr(m, name), **row["best_params"])
            fd, params = tempfile.mkstemp(suffix=".json"); json.dump(P, os.fdopen(fd, "w"), default=float)
        remeasure(rid, wear, params=params)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
