"""Adapter (new file, alignment skeptic of dogring-draglink-knuckle-3r, 2026-10-17): the workspace continuity flood
(CLAUDE.md continuity rule 2026-10-16; connected_report() of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py,
the same function the claim's own LS.frozen_flood calls) run on the VERIFIER's corrected wear of
dogring-draglink-knuckle-3r - the number on record (v_gap 97.83) - and on the claim wear (22.64) for comparison.

Nothing is edited: the verifier harness (docs/concepts/verify/dogring-draglink-knuckle-3r.py wear(..., ring=True)) and the
claim's model run unchanged; only PK.audit is wrapped. The harness calls PK.audit twice after its per-pose checks: first
on the corrected bench (failing poses set to None), then on the restored claim bench. At each call this adapter runs
connected_report(M, B) on the bench as it stands, then the original audit. connected_report restores B.res itself.
The minarc mechanism module is loaded lazily at the first call (after the wear and the checks), the order the claim's
own LS.frozen_flood uses. Its 'static' gap must reproduce the verifier's corrected / claim gap or the run is void.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_flood_dogring_verifier.py <out.json>
"""
import importlib.util, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))


def main():
    path = sys.argv[1]
    sp = importlib.util.spec_from_file_location("dogring_v_flood", os.path.join(REPO, "docs", "concepts", "verify", "dogring-draglink-knuckle-3r.py"))
    V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
    calls = []; orig = V.PK.audit; MECH = {}

    def wrapped(M, B):
        if "m" not in MECH:
            s2 = importlib.util.spec_from_file_location("minarc_mech_for_dogring_flood",
                                                        os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
            m = importlib.util.module_from_spec(s2); s2.loader.exec_module(m); MECH["m"] = m
        n_none = int(sum(1 for r in B.res if r is None)); t = time.time()
        rep = MECH["m"].connected_report(M, B); rep["secs"] = round(time.time() - t, 1)
        calls.append(dict(n_none=n_none, connected=rep))
        return orig(M, B)
    V.PK.audit = wrapped
    t = time.time()
    out = V.wear(dict(V.BEST), "bench", True)
    V.PK.audit = orig
    lab = {}
    if len(calls) >= 2:
        a, b = calls[-2], calls[-1]
        lab = {"corrected": a, "claim": b} if a["n_none"] >= b["n_none"] else {"corrected": b, "claim": a}
    res = dict(design="dogring-draglink-knuckle-3r", wear="bench", harness="docs/concepts/verify/dogring-draglink-knuckle-3r.py wear --ring",
               verifier={k: out.get(k) for k in ("frozen", "corrected", "corrected_overhead", "poses_failing", "why_failing")},
               flood=lab, n_audit_calls=len(calls), secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=V.BEST)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("verifier", "n_audit_calls", "secs")}, default=float))
    for k, v in lab.items():
        print(k, json.dumps({kk: vv for kk, vv in v["connected"].items()}, default=float)[:1500])


if __name__ == "__main__":
    main()
