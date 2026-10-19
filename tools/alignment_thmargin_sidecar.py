"""Alignment adapter (read-only on every claim): the J1-J3 fold margin `th` (tools/concept_kit.py lines 25-30) over the
TAKEN poses of a sidecar-core design's frozen claim, worn through the model's own frozen() / frozen_held() UNCHANGED.

Why: the `fold_margin` check of tools/alignment_audit.py needs "the min th margin over taken poses" on file (CLAUDE.md
"The fold margin is read in ONE metric": each claim reports it). Rows on the shared sidecar core
(docs/concepts/models/sidecar-longdyad-knuckle-3r.py: sidecar-parallelogram, sidecar-longdyad, ...) do not all carry it.
The reading is the one the kneeless-sidecar verifier uses (docs/concepts/verify/kneeless-sidecar-knuckle-3r.py,
th_margin()): K on stop A -> the (a1, a2) dyad's distance of th from |a1 - a2| and min(a1 + a2, 360 - a1 - a2); K forced
open -> the smaller of the K-J2-J3 sub-dyad (b1, c) margin and the effective (a1e, a2e) dyad margin, both in th.
Only the pin-knee audit(M, B) is wrapped (to read M / B after the model's own wear); nothing is edited, no score changes.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_thmargin_sidecar.py <id> bench|held [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0]
    dK = np.asarray(M.dK, float); rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m = min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2)
        p = B.poses[i]
        rows.append(dict(i=i, kind=B.kind[i], plane=p.get("plane"), elev=p.get("elev"), axial=p.get("axial"), m=round(m, 3),
                         forced=forced))
    if not rows: return dict(min=None, n=0)
    own = [r["m"] for r in rows]; low = sorted(rows, key=lambda r: r["m"])[:8]
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)),
                lt6=int(sum(1 for x in own if x < 6 - 1e-6)), lt8=int(sum(1 for x in own if x < 8 - 1e-6)),
                forced=int(sum(r["forced"] for r in rows)),
                min_forced=round(min([r["m"] for r in rows if r["forced"]] or [float("nan")]), 3),
                min_stopA=round(min([r["m"] for r in rows if not r["forced"]] or [float("nan")]), 3), lowest=low)


def run(rid, wear):
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = _load("thm_" + rid.replace("-", "_"), os.path.join(REPO, "docs", "concepts", "models", rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    orig = pk.audit; calls = []

    def wrapped(M, B):
        a = orig(M, B)
        try: calls.append(dict(n=len(B.idx), rep=B.report(), th=th_margin(M, B)))
        except Exception as e: calls.append(dict(n=len(B.idx), err=repr(e)))
        return a
    pk.audit = wrapped; t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig
    worn = calls[-1] if calls else {}
    rep = worn.get("rep") or {}
    return dict(id=rid, wear=wear, frozen=r.get("frozen"), worn_gap=rep.get("gap"),
                reproduces=(abs(float(rep.get("gap", 1e9)) - float((r.get("frozen") or {}).get("gap", -1e9))) <= 0.05),
                th_margin=worn.get("th"), calls=[dict(n=c["n"], gap=(c.get("rep") or {}).get("gap"), th_min=(c.get("th") or {}).get("min"),
                                                     err=c.get("err")) for c in calls],
                secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")


if __name__ == "__main__":
    rid, wear = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(REPO, "docs", "alignment", "remeasure", f"{rid}_{wear}_thmargin.json")
    res = run(rid, wear); json.dump(res, open(out, "w"), indent=1, default=float)
    print(json.dumps(dict(out=out, frozen=res["frozen"], worn_gap=res["worn_gap"], reproduces=res["reproduces"],
                          th={k: v for k, v in (res["th_margin"] or {}).items() if k != "lowest"}, secs=res["secs"]), default=float))
