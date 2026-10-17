"""Adapter (new file, alignment audit of dogring-draglink-knuckle-3r, 2026-10-17): run tools/alignment_wear_probe.py's
analyse() on the VERIFIER's corrected wear of dogring-draglink-knuckle-3r (docs/concepts/verify/dogring-draglink-knuckle-3r.py
wear(..., ring=True): the claim's model unchanged, frozen protocol, poses failing the verifier's per-pose checks dropped).

Nothing is edited: the verifier harness and the model run unchanged; only PK.audit is wrapped to run analyse() on the worn
(M, B) at the moment the harness calls it. The harness calls audit twice after its checks: first on the corrected bench
(failing poses set to None), then on the restored claim bench. Both are recorded ('corrected', 'claim').

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_dogring_verifier.py <bench|held> <out.json> [EYE_R=4.5]
        the optional NAME=VALUE sets one module constant of the claim's model in memory only (a what-if for a proposal,
        never an input to a score)
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_wear_probe as W                              # noqa: E402


def main():
    which, path = sys.argv[1], sys.argv[2]
    sp = importlib.util.spec_from_file_location("dogring_v_probe", os.path.join(REPO, "docs", "concepts", "verify", "dogring-draglink-knuckle-3r.py"))
    V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
    override = {}
    for kv in sys.argv[3:]:
        if "=" in kv:
            k, v = kv.split("=", 1); old = getattr(V.DR, k); setattr(V.DR, k, type(old)(float(v))); override[k] = [old, float(v)]
    calls = []; orig = V.PK.audit

    def wrapped(M, B):
        n_none = int(sum(1 for r in B.res if r is None))
        calls.append(dict(n_none=n_none, probe=W.analyse(M, B)))
        return orig(M, B)
    V.PK.audit = wrapped
    t = time.time()
    out = V.wear(dict(V.BEST), which, True)
    V.PK.audit = orig
    # the last two audit calls of wear(): corrected (more None), then the restored claim
    lab = {}
    if len(calls) >= 2:
        a, b = calls[-2], calls[-1]
        lab = dict(corrected=a if a["n_none"] >= b["n_none"] else b, claim=b if a["n_none"] >= b["n_none"] else a)
    res = dict(design="dogring-draglink-knuckle-3r", wear=which, override=override, harness="docs/concepts/verify/dogring-draglink-knuckle-3r.py wear --ring",
               verifier=dict(frozen=out["frozen"], corrected=out["corrected"], corrected_overhead=out["corrected_overhead"], poses_failing=out["poses_failing"],
                             why_failing=out["why_failing"], audit=out["audit"], corrected_audit=out["corrected_audit"],
                             corrected_contact_depth=out["corrected_contact_depth"], th_margin=out["th_margin"],
                             checks={k: v for k, v in out["checks"].items() if not k.startswith("worst")}),
               n_audit_calls=len(calls), probes=lab, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=V.BEST)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(verifier=res["verifier"]["corrected"], claim=res["verifier"]["frozen"], override=override, secs=res["secs"],
                          corrected_ws=(lab.get("corrected") or {}).get("probe", {}).get("ws_unscored"),
                          corrected_ovh=(lab.get("corrected") or {}).get("probe", {}).get("ws_overhead140")), default=float))


if __name__ == "__main__":
    main()
