"""Adapter (new file, alignment audit 2026-10-18): one exact wear of docs/concepts/models/crest-knee-3r.py feeds BOTH
tools/alignment_audit.py remeasure (near-touch 1 / 2 / 3 mm, clip metal histogram, band 3-14, coordinate spans) and
tools/alignment_wear_probe.py analyse() (unscored workspace in-band, overhead reach, clearance floor < 1 / 2 / 3 mm).

The model runs UNCHANGED. The model file has no frozen_held(); this adapter gives the loaded module one that is its own
frozen() with the wear bench swapped for the verifier's disjoint held bench (docs/concepts/verify/crest-knee-3r.py
held_bench(), imported, not copied), exactly as the verifier's 'wear held' does. PK.audit is wrapped only to capture the
worn (M, B); AA.remeasure wraps it again to record the deep audit.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_crest_knee_adapter.py both bench|held
        -> docs/alignment/remeasure/crest-knee-3r_<wear>.json (remeasure) + crest-knee-3r_<wear>_probe.json (probe)
"""
import importlib.util, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                   # noqa: E402
import alignment_wear_probe as W                               # noqa: E402

RID = "crest-knee-3r"
CAP = []
_orig_load = AA._load


def _verifier():
    p = os.path.join(AA.VERIFY, RID + ".py")
    sp = importlib.util.spec_from_file_location("crest_knee_verifier_for_audit", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


class _HeldCB:
    """the model's CB with Bench(110, 360) answered by the verifier's held bench (the fit bench Bench(60,160) unchanged)"""
    def __init__(self, cb, held): self._cb, self._held = cb, held
    def __getattr__(self, k): return getattr(self._cb, k)
    def Bench(self, n_clip=None, n_ws=None, *a, **kw):
        if (n_clip, n_ws) == (110, 360): return self._held()
        return self._cb.Bench(n_clip=n_clip, n_ws=n_ws, *a, **kw)


def _load(name, path):
    m = _orig_load(name, path)
    if os.path.basename(path) == RID + ".py" and hasattr(m, "PK"):
        pk = m.PK; orig = pk.audit

        def cap(M, B):
            CAP.append((M, B)); return orig(M, B)
        pk.audit = cap
        if not hasattr(m, "frozen_held"):
            V = _verifier()

            def frozen_held(P, keep=False):
                real = m.CB; m.CB = _HeldCB(real, V.held_bench)
                try: return m.frozen(P, keep=keep)
                finally: m.CB = real
            m.frozen_held = frozen_held
    return m


AA._load = _load

if __name__ == "__main__":
    cmd, wear = sys.argv[1], sys.argv[2]
    assert cmd == "both" and wear in ("bench", "held")
    t = time.time(); rem = AA.remeasure(RID, wear)
    M, B = CAP[-1]
    out = dict(design=RID, wear=wear, model_frozen=rem.get("frozen"), probe=W.analyse(M, B), bench_key=getattr(B, "key", None),
               n=len(B.idx), secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"),
               note="tools/alignment_crest_knee_adapter.py: same worn (M, B) as the remeasure file")
    path = os.path.join(AA.REM, f"{RID}_{wear}_probe.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "probe"}, default=float))
