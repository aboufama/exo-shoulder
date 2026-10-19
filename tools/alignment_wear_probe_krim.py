"""Alignment probe adapter for k-rim-lobe-stub-knuckle-3r (read-only; a NEW file, nothing else changed).

Wears the VERIFIED (corrected) frozen claim through the design's own verifier harness, unchanged
(docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py: frozen_wear(CorrModel, PARAMS + BEST, wear, flood)), with the
pin-knee audit wrapped to capture the worn bench. Writes two files:

  docs/alignment/remeasure/k-rim-lobe-stub-knuckle-3r_<wear>.json        the re-measure record tools/alignment_audit.py
      reads (frozen, fit_fast, why, parts_ib14, audit, deep = alignment_audit.deep_audit: near-touch 1 / 2 / 3 mm, the
      clip metal histogram, in-band read as 3-14 mm, per-pose coordinate spans)
  docs/alignment/remeasure/k-rim-lobe-stub-knuckle-3r_probe_<wear>.json  tools/alignment_wear_probe.py analyse() on the
      same worn bench (unscored workspace in-band, overhead reach, poses with metal < 1 / 2 / 3 mm, contact depths) plus
      the J1-J3 fold margin read in th (kit rule, tools/concept_kit.py FOLD_MARGIN; the model's m3e = dyad_margin(th, a1e,
      a2)), the sub-dyad margin msub, the K slave angle by state, and the continuity flood of this wear

Why an adapter: tools/alignment_audit.py remeasure wears mod.frozen() = KB.frozen, whose attribute copy list predates the
stub (the verifier's note), and the model has no frozen_held(); the verified number 44.79 is the verifier's corr wear.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_krim.py bench|held [stk=6.0]

With stk=<mm> the claim is worn UNCHANGED except for the knee pin stack (5.0 = iglidur pin, 6.0 = MR63ZZ pair, the lead's
build rule 2026-10-17); the files are then tagged _stk<value> (<id>_stk6_<wear>.json, <id>_stk6_knee_<wear>.json, no
'probe' in the name), so they never stand in for the claim's own re-measure or its contact depths.
"""
import importlib.util, json, os, subprocess, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
RID = "k-rim-lobe-stub-knuckle-3r"
REM = os.path.join(REPO, "docs", "alignment", "remeasure")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def run(wear, stk=None):
    P = _load("al_probe_core_krim", os.path.join(REPO, "tools", "alignment_wear_probe.py"))
    AA = _load("al_audit_krim", os.path.join(REPO, "tools", "alignment_audit.py"))
    V = _load("al_v_krim", os.path.join(REPO, "docs", "concepts", "verify", RID + ".py"))
    orig = V.PK.audit; cap = []

    def wrapped(M, B):
        a = orig(M, B); cap.append((M, B, AA.deep_audit(M, B))); return a
    V.PK.audit = wrapped
    t = time.time()
    try:
        params = dict(V.C.PARAMS, **V.BEST)
        if stk is not None: params["stk"] = float(stk)
        out = V.frozen_wear(V.CorrModel, params, wear, True)
    finally:
        V.PK.audit = orig
    M, B, deep = cap[-1]
    secs = round(time.time() - t, 1)
    n = len(B.idx); taken = [i for i in range(n) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    M.D.ik(M.Q); m3 = np.asarray(M.D._m3e, float); ms = np.asarray(M.D._msub, float); st = np.asarray(M.kstate)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    def mn(a, sel): return round(float(a[sel].min()), 3) if len(sel) else None
    fold = dict(rule="m3e = dyad_margin(th, a1e, a2) over taken poses (kit FOLD_MARGIN 5)", th_margin_min=mn(m3, taken),
                lt5=int(sum(1 for i in taken if m3[i] < 5 - 1e-6)), lt6=int(sum(1 for i in taken if m3[i] < 6)),
                lt10=int(sum(1 for i in taken if m3[i] < 10)),
                by_state={s: mn(m3, [i for i in taken if st[i] == v]) for s, v in (("A", 0), ("stretched", 1), ("folded", -1))},
                taken_by_state={s: int(sum(1 for i in taken if st[i] == v)) for s, v in (("A", 0), ("stretched", 1), ("folded", -1))},
                msub_min=mn(ms, [i for i in taken if st[i] != 0]), n_taken=len(taken))
    dK = np.degrees(np.abs(np.asarray(M.dK, float)))
    tk1 = [i for i in taken if st[i] == 1]
    kslave = dict(dK_taken_max=round(float(dK[tk1].max()), 2) if tk1 else 0.0, n_stretched_taken=len(tk1),
                  overhead140_taken_by_state={s: int(sum(1 for i in taken if st[i] == v and el[i] >= 140 and kind[i] == "ws"))
                                              for s, v in (("A", 0), ("stretched", 1), ("folded", -1))})
    git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    exact = os.environ.get("CB_EXACT") == "1"
    harness = "docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py frozen_wear(CorrModel, PARAMS + BEST, wear, flood=True), unchanged"
    rem = dict(id=RID, wear=wear, params={k: v for k, v in V.BEST.items()}, frozen=out["frozen"], fit_fast=out["fit_fast"], why=out["why"],
               parts_ib14=out["parts_ib14"], parts_pairs=out.get("parts_pairs"), audit=out["audit"], deep=deep, mode=B.mode, n=n, secs=secs,
               exact=exact, git=git, harness=harness, drive=out.get("drive"), connected=out.get("connected"), min_clear_taken=out.get("min_clear_taken"))
    probe = dict(design=RID, wear=wear, harness=harness, verifier_frozen=out["frozen"], frozen=out["frozen"],
                 verifier_audit_near=dict(near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"),
                                          near2_poses=out["audit"].get("near2_poses"), min_mm=out["audit"].get("near_touch_min_mm")),
                 drive=out.get("drive"), fold_margin=fold, k_slave=kslave, connected=out.get("connected"), probe=P.analyse(M, B),
                 secs=secs, exact=exact, git=git)
    os.makedirs(REM, exist_ok=True)
    tag = "" if stk is None else "_stk" + ("%g" % float(stk)).replace(".", "p")
    rem["stk"] = probe["stk"] = float(params.get("stk")) if params.get("stk") is not None else None
    f1 = os.path.join(REM, f"{RID}{tag}_{wear}.json"); f2 = os.path.join(REM, f"{RID}{tag}_{'knee' if tag else 'probe'}_{wear}.json")
    json.dump(rem, open(f1, "w"), indent=1, default=float); json.dump(probe, open(f2, "w"), indent=1, default=float)
    return rem, probe


if __name__ == "__main__":
    kw = dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a)
    rem, probe = run(sys.argv[1], float(kw["stk"]) if "stk" in kw else None)
    print(json.dumps(dict(frozen=rem["frozen"], deep={k: v for k, v in rem["deep"].items() if k != "coord_spans"}, fold=probe["fold_margin"],
                          k_slave=probe["k_slave"], why=rem["why"], conn={k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk in ("gap", "reach", "dropped")})
                                                                        for k, v in (rem.get("connected") or {}).items()},
                          contact=probe["probe"].get("contact_poses"), ws=probe["probe"].get("ws_unscored"), ws_oh=probe["probe"].get("ws_overhead140"),
                          reach_by_elev=probe["probe"].get("ws_reach_by_elev"), secs=rem["secs"]), default=float))
