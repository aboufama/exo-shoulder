"""Wrapper: run tools/alignment_msub_rest_probe_model.py (UNCHANGED) on a row whose best_params is a JSON STRING.

Written 2026-10-18 by the skeptic of the lowarm-halfring-knuckle-3r audit (finding G4: the near-singular sub-dyad at K rest
was carried from the parent desmo-conecut, never measured on this row). The probe's run() reads
`P = dict(row.get("best_params") or {})`, which fails on a string; this wrapper re-binds run() in memory only, so that P is
the row's decoded params laid over the model module's dict NAME (CELL_B for this row), exactly as the row's verifier does
(docs/concepts/verify/lowarm-halfring-knuckle-3r.py lines 38-41). Nothing on disk is edited.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_msub_strparams.py <id> <bench|held> <out.json> [--cell-dict NAME]
"""
import inspect, json, os, sys, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import alignment_msub_rest_probe_model as MS  # noqa: E402
from alignment_strparams_adapter import _params  # noqa: E402


def main(argv):
    rid, wear, outp = argv[1], argv[2], argv[3]
    name = argv[argv.index("--cell-dict") + 1] if "--cell-dict" in argv else None
    src = textwrap.dedent(inspect.getsource(MS.run)); old = 'P = dict(row.get("best_params") or {})'
    assert src.count(old) == 1, "alignment_msub_rest_probe_model.run changed; update the wrapper"
    ns = {}
    exec(compile(src.replace(old, "P = _params(rid, _name)"), "amsub_run_strparams", "exec"),
         dict(MS.__dict__, _params=_params, _name=name), ns)
    t = time.time(); r = ns["run"](rid, wear); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    r["params_source"] = f"row best_params (decoded from a JSON string){' over the model dict ' + name if name else ''}"
    r["params"] = _params(rid, name)
    json.dump(r, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in r.items() if k not in ("rows", "lowest_rest")}, default=float))


if __name__ == "__main__":
    main(sys.argv)
