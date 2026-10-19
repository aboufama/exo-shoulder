"""Adapter (new file, alignment audit 2026-10-18, round 14 slice r14-A): the crest-knee-3r claim moved from the flat-knee
cell (row best_params, verified 32.84) to the JOGGLED knee cell (row best_params_joggle, kj=1, verified 31.50; the row's
v_params_key). tools/alignment_crest_knee_adapter.py re-wears row best_params only; this file re-uses it unchanged
(its AA._load patch: PK.audit capture + frozen_held() = the model's own frozen() worn on the verifier's held bench) and
passes the joggle parameters, so the model's own frozen() builds its JogModel (kj=1) exactly as the claim did.

The model runs UNCHANGED. Outputs:
    docs/alignment/remeasure/crest-knee-3r_<wear>.json        (AA.remeasure: near-touch 1/2/3, histogram, band 3-14, spans)
    docs/alignment/remeasure/crest-knee-3r_<wear>_probe.json  (alignment_wear_probe.analyse on the same worn (M, B))
The flat-cell files these overwrite were copied first to crest-knee-3r_flatcell_<wear>{,_probe}.json.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_crest_knee_joggle_adapter.py bench|held
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_crest_knee_adapter as CKA                     # noqa: E402  (patches AA._load on import)
AA, W = CKA.AA, CKA.W

if __name__ == "__main__":
    wear = sys.argv[1]
    assert wear in ("bench", "held")
    row = json.load(open(os.path.join(AA.ROWS, CKA.RID + ".json")))
    key = row.get("v_params_key") or "best_params"
    P = row[key]
    assert P.get("kj") == 1, "the claimed cell is not the joggle cell"
    tmp = os.path.join(AA.REM, f".{CKA.RID}_{wear}_params.tmp.json"); json.dump(P, open(tmp, "w"))
    t = time.time()
    try: rem = AA.remeasure(CKA.RID, wear, params=tmp)
    finally: os.remove(tmp)
    M, B = CKA.CAP[-1]
    out = dict(design=CKA.RID, wear=wear, params_key=key, model_class=type(M).__mro__[1].__name__, model_frozen=rem.get("frozen"),
               probe=W.analyse(M, B), bench_key=getattr(B, "key", None), n=len(B.idx), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"),
               note="tools/alignment_crest_knee_joggle_adapter.py: same worn (M, B) as the remeasure file; joggle cell (kj=1)")
    path = os.path.join(AA.REM, f"{CKA.RID}_{wear}_probe.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "probe"}, default=float))
