"""Alignment probe adapter for geneva-tail-knuckle-pinknee-3r (read-only; a NEW file, nothing else changed).

Wears the VERIFIED (corrected) frozen claim through the design's own verifier harness, unchanged
(docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py: frozen_wear(CorrModel, BEST, wear)), captures the worn bench via
the pin-knee audit, and reports what tools/alignment_wear_probe.py analyse() reports (unscored workspace in-band, overhead
reach, poses with metal < 1 / 2 / 3 mm, contact depths) plus the J1-J3 fold margin read in th (kit rule,
tools/concept_kit.py FOLD_MARGIN; the model's m3e = dyad_margin(th, a1e, a2)) and the sub-dyad margin msub over the taken
poses, by K state.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_geneva.py bench|held <out.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def run(wear):
    P = _load("al_probe_core", os.path.join(REPO, "tools", "alignment_wear_probe.py"))
    V = _load("al_v_geneva", os.path.join(REPO, "docs", "concepts", "verify", "geneva-tail-knuckle-pinknee-3r.py"))
    cap = P._capture(V.PK)
    out = V.frozen_wear(V.CorrModel, dict(V.G.PARAMS, **V.BEST), wear, False)
    M, B = cap[-1]
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    M.D.ik(M.Q); m3 = np.asarray(M.D._m3e, float); ms = np.asarray(M.D._msub, float); st = np.asarray(M.kstate)
    def mn(a, sel): return round(float(a[sel].min()), 3) if len(sel) else None
    fold = dict(rule="m3e = dyad_margin(th, a1e, a2) over taken poses (kit FOLD_MARGIN 5)", th_margin_min=mn(m3, taken),
                lt5=int(sum(1 for i in taken if m3[i] < 5 - 1e-6)), lt6=int(sum(1 for i in taken if m3[i] < 6)), lt10=int(sum(1 for i in taken if m3[i] < 10)),
                by_state={s: mn(m3, [i for i in taken if st[i] == v]) for s, v in (("A", 0), ("stretched", 1), ("folded", -1))},
                msub_min=mn(ms, taken), n_taken=len(taken))
    return dict(design="geneva-tail-knuckle-pinknee-3r", wear=wear, verifier_frozen=out["frozen"],
                verifier_audit_near=dict(near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"),
                                         near2_poses=out["audit"].get("near2_poses"), min_mm=out["audit"].get("near_touch_min_mm")),
                drive=out.get("drive"), fold_margin=fold, probe=P.analyse(M, B))


if __name__ == "__main__":
    t = time.time(); r = run(sys.argv[1]); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(sys.argv[2], "w"), indent=1, default=float); print(json.dumps(r, default=float)[:3000])
