"""Adapter (new file, alignment audit 2026-10-19, round 501 slice r501-A): one exact wear of
docs/concepts/models/isoceles-shortdyad-pinknee-3r.py feeds BOTH tools/alignment_audit.py remeasure (near-touch 1 / 2 / 3 mm,
clip metal histogram, band 3-14, coordinate spans) and tools/alignment_wear_probe.py analyse() (unscored workspace in-band,
overhead reach, clearance floor < 1 / 2 / 3 mm).

The model runs UNCHANGED. Its frozen() takes bench='held' (the verifier's disjoint held bench, crest-knee verifier's
held_bench()) instead of a frozen_held(); this adapter gives the loaded module frozen_held(P) = frozen(P, bench='held'),
exactly the call the model's own `held` mode makes. PK.audit is wrapped only to capture the worn (M, B); AA.remeasure wraps
it again to record the deep audit. Parameters: the row's best_params (the verified claim).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_isoceles_adapter.py bench|held
        -> docs/alignment/remeasure/isoceles-shortdyad-pinknee-3r_<wear>.json (remeasure) + ..._<wear>_probe.json (probe)
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                   # noqa: E402
import alignment_wear_probe as W                               # noqa: E402

RID = "isoceles-shortdyad-pinknee-3r"
CAP = []
_orig_load = AA._load


def _load(name, path):
    m = _orig_load(name, path)
    if os.path.basename(path) == RID + ".py":
        m.frozen_held = lambda P: m.frozen(P, bench="held")
        pk = m.PK; inner = pk.audit

        def cap(M, B):
            CAP.append((M, B)); return inner(M, B)
        pk.audit = cap
    return m


AA._load = _load

if __name__ == "__main__":
    wear = sys.argv[1]
    assert wear in ("bench", "held")
    t = time.time()
    rem = AA.remeasure(RID, wear)
    M, B = CAP[-1]
    out = dict(design=RID, wear=wear, model_class=type(M).__name__, model_frozen=rem.get("frozen"), probe=W.analyse(M, B),
               n=len(B.idx), mode=B.mode, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1",
               git=AA._git("rev-parse", "--short", "HEAD"),
               note="tools/alignment_isoceles_adapter.py: same worn (M, B) as the remeasure file; row best_params")
    path = os.path.join(AA.REM, f"{RID}_{wear}_probe.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "probe"}, default=float))
