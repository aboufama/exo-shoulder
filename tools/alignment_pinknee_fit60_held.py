"""Skeptic re-measure: the skin-normal-3r-pin-knee claim worn on the DISJOINT held-out set under the claim's OWN protocol.

The verified claim (v_gap 27.20) is H1 fitted on Bench(60,160) FAST, shape frozen, worn EXACT on Bench(110,360). The
held-out numbers on file (v_p5_h1_held_gap 29.12, v_polish2_h1_held_gap 28.55) fit the shape on Bench(110,360) instead.
This tool fits exactly as the claim does (fit60) and wears that frozen shape on the polish verifier's held_bench()
(every fit-clip frame and workspace pose outside both benches; Wave / Walking stay out). It imports the polish harness
docs/concepts/verify/skin-normal-3r-pin-knee-polish.py UNCHANGED and runs its own frozen_on / extra_checks / audit /
redteam sequence, so the numbers are the same instrument as every other v_* field. Nothing is edited.

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 tools/alignment_pinknee_fit60_held.py <out.json> ['<json params>']
"""
import importlib.util, json, os, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
H1 = {"rad1": 10.0, "rad2": 10.0, "rad3": 10.0, "az1": 101.1634, "el1": 63.8986, "az2": 30.153, "el2": 47.0108, "wd": 70.3931,
      "wa": -8.1248, "b3": 0.2842, "lE": 59.5534, "lc": 28.2401, "phiE": -5.8107, "phib": -54.914, "ang_min": 30.4611, "stk": 5.6815}


def main():
    outp = sys.argv[1]; P = json.loads(sys.argv[2]) if len(sys.argv) > 2 else dict(H1)
    spec = importlib.util.spec_from_file_location("pk_polish", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py"))
    H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
    t0 = time.time()
    fitB = H.fast_bench(60, 160)                    # the claim's own fit bench
    wearB = H.held_bench()                          # disjoint from Bench(110,360) and Bench(60,160)
    M, fit, M1 = H.frozen_on(fitB, wearB, P)
    r = M.run(); model = {k: r[k] for k in H.KEYS}
    aud0 = H.MK.audit(M, wearB)
    ex, bad = H.V.extra_checks(M, wearB)
    rt0 = H.redteam(M, wearB)
    res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in H.KEYS}
    aud = H.MK.audit(M, wearB); rt = H.redteam(M, wearB)
    # per-pose closest metal / contact depth on the corrected taken set (min of skin samples and the audit's cmin)
    import numpy as np
    per = []
    for i in range(len(wearB.idx)):
        if wearB.res[i] is None: continue
        mm = min(float(np.min(wearB.res[i])), float(M.cmin.get(i, 1e9)) if hasattr(M, "cmin") else 1e9)
        p = wearB.poses[i]
        per.append(dict(i=i, kind=wearB.kind[i], plane=p["plane"], elev=round(p["elev"], 1), axial=p["axial"], mm=round(mm, 3)))
    wearB.res = res0
    out = dict(protocol="fit60->held", params=P, fit_mode=fitB.mode, wear_mode=wearB.mode, n_wear=len(wearB.idx),
               exact=os.environ.get("CB_EXACT") == "1", fold_margin=H.KIT.FOLD_MARGIN, o20_only=H.KIT.O20_ONLY, fit=fit, model=model,
               model_audit=aud0, extra=ex, bad_removed=len(bad), corrected=corrected, corrected_audit=aud, redteam=rt, redteam_model=rt0,
               per_pose_taken=per, secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(n=len(wearB.idx), fit=fit, corrected=corrected, near1=aud.get("gap_near1"), min_mm=aud.get("near_touch_min_mm"),
                          overhead=aud.get("overhead140"), bad=len(bad), fold=rt.get("fold_margin_min_taken_deg"), knee=rt.get("knee_ang_taken"),
                          secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
