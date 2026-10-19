#!/usr/bin/env python3
"""Alignment re-wear adapter for lowarm-kphase-notch-knuckle-3r (new file; the model, its parent, the verifier harness and
the bench run UNCHANGED).

Why: like lowarm-kstop (tools/alignment_remeasure_kstop.py), this model builds its module chain fresh inside _harness() on
every call, and its claim is not mod.frozen(): it is the parent's `wear()` at the claim's config (beta -157, the hub-K
notch n 2.45 / az 46-98 / F_K+6.0 to the crown, J2 dowel at K-eq 45.75 - which CUTS taken poses, so mod.frozen() alone
would not reproduce the claim). This adapter therefore loads the INDEPENDENT VERIFIER's harness
(docs/concepts/verify/lowarm-kphase-notch-knuckle-3r.py) with its corrections OFF (the claim's own metal; the verifier
found V-OWN / V-ARM change 0.00), calls its setup() and the parent's wear(delta, which) exactly as the verifier did, and
AFTER the wear (dowel cut applied) records alignment_audit.deep_audit(M, B), alignment_paired._dump_bench(M, B), the fold
margin (the verifier's th_margin_sided, metric th of tools/concept_kit.py) and, with --flood, the continuity flood
(minarc mechanism connected_report, the verifier's flood()). `merge` is the kstop adapter's merge (the claim's own per-pose
worst rule) with the id switched.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_remeasure_kphase.py side <bench|held> <delta> <out.json> [--flood] [--set mu=0.17]
        (--set: a RED-TEAM reading of a model parameter, e.g. the family's friction mu 0.17; never the claim's number)
    python3 tools/alignment_remeasure_kphase.py merge <bench|held> <side_plus.json> <side_minus.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RID = "lowarm-kphase-notch-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def side(wear, delta, outp, flood=False, extra=None):
    AA = _load("aa_for_kphase_rem", os.path.join(REPO, "tools", "alignment_audit.py"))
    AP = _load("ap_for_kphase_rem", os.path.join(REPO, "tools", "alignment_paired.py"))
    VK = _load("kphase_verifier_for_rem", os.path.join(REPO, "docs", "concepts", "verify", RID + ".py"))
    VK.OPT.update(own=False, arm_t=0.0)                     # the claim's own metal (verifier: corrections change 0.00)
    VK.setup()
    t = time.time()
    sets = dict(VK.BEST, **(extra or {}))
    o = VK.KS.wear(float(delta), wear, None, sets)
    V = VK.INFO.pop("_V"); fit, M1, M, B, r = V.CAP["res"]
    deep = AA.deep_audit(M, B); poses = AP._dump_bench(M, B)
    tk = [i for i in range(len(B.idx)) if AA._taken(B, i)]
    dK = np.degrees(np.abs(np.asarray(getattr(M, "dK", []), float)))
    thm = VK.th_margin_sided(V, float(delta))
    out = dict(id=RID, wear=wear, delta=float(delta), params=dict(sets, notch=dict(VK.K.NOTCH), dowel_K=VK.KS.DOWEL_K), red_team_sets=extra or None,
               frozen=o.get("frozen"), fit_fast=(o.get("verifier") or {}).get("fit_fast"), why=(o.get("verifier") or {}).get("why"),
               parts_ib14=(r or {}).get("parts_ib14") if isinstance(r, dict) else None, audit=None, deep=deep, mode=B.mode, poses=poses,
               recomputed=AP.gap_parts(poses), dK_taken_max=round(float(max([dK[i] for i in tk] or [0])), 3) if len(dK) == len(B.idx) else None,
               dowel_would_cut=0, dowel=o.get("dowel"), th_margin=dict(min_th_dwell=thm.get("min_th_dwell"), min_own_forced=thm.get("min_own_forced"),
                                                                      lt5_dwell=thm.get("lt5_dwell"), lt5_forced=thm.get("lt5_forced"),
                                                                      msub_lt1_dwell=thm.get("msub_lt1_dwell"), n=thm.get("n")),
               notch_info=getattr(M1, "_kph_notch", None), pk="verifier harness + KS.wear", secs=None, exact=os.environ.get("CB_EXACT") == "1")
    if not out["parts_ib14"]:
        vr = o.get("verifier") or {}
        out["parts_ib14"] = (vr.get("frozen") or {}).get("parts_ib14") if isinstance(vr.get("frozen"), dict) else None
    if flood:
        try: out["connected"] = VK.flood(V)
        except Exception as ex: out["connected_error"] = repr(ex)
    out["secs"] = round(time.time() - t, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("wear", "delta", "frozen", "recomputed", "dK_taken_max", "th_margin", "secs")}
                     | {"dowel": {k: v for k, v in (out["dowel"] or {}).items() if k != "cut"}, "connected": out.get("connected"),
                        "deep": {k: v for k, v in (out["deep"] or {}).items() if k != "coord_spans"}}, default=float))


def merge(wear, paths):
    KA = _load("kstop_adapter_for_kphase", os.path.join(REPO, "tools", "alignment_remeasure_kstop.py"))
    KA.RID = RID
    KA.merge(wear, paths)
    p = os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_{wear}.json")
    D = [json.load(open(x)) for x in paths]; out = json.load(open(p))
    out["note"] = ("per-pose worst of the sided dwell wears (+0.264 / -0.210 deg K), re-worn by tools/alignment_remeasure_kphase.py through "
                   "the verifier's harness (corrections off) and the parent's wear(): model unchanged, J2 dowel 45.75 cut applied")
    out["th_margin"] = {str(d["delta"]): d.get("th_margin") for d in D}
    out["dowel"] = {str(d["delta"]): {k: v for k, v in (d.get("dowel") or {}).items()} for d in D}
    for d in D:
        if isinstance(d.get("connected"), dict): out["connected_side"] = dict(delta=d["delta"], connected=d["connected"])
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(json.dumps(dict(path=p, frozen=out["frozen"], th_margin=out["th_margin"]), default=float))


if __name__ == "__main__":
    if sys.argv[1] == "side":
        ex = {}
        for i_, a_ in enumerate(sys.argv):
            if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); ex[k_] = float(v_)
        side(sys.argv[2], float(sys.argv[3]), sys.argv[4], "--flood" in sys.argv, ex)
    elif sys.argv[1] == "merge":
        merge(sys.argv[2], sys.argv[3:])
