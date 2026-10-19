"""Alignment probe (read-only): the J1-K-J3 sub-chain fold margin m_sub on EVERY taken pose of a frozen claim, K at rest
included, for ANY model whose frozen() / frozen_held() ends in a pin-knee-style PK.audit(M, B) (the knuckle / sidecar /
roller-flank / slipper families). The generic twin of tools/alignment_msub_rest_probe.py (which is wired to the
dipped-law verifier): the family's fold reading (tools/alignment_wear_probe_model.py th_margin, the lead verifier's)
reads min(m_sub, m_eff) only where K is off its rest and m_plain where K rests on stop A; this probe reports m_sub on
the rest poses too, so a design can be compared pose by pose with its parent on the same reading.

The model runs UNCHANGED (row best_params, its own frozen protocol: fit Bench(60,160) fast, shape frozen, worn on
Bench(110,360) exact with CB_EXACT=1, or on the held-out set); only PK.audit is wrapped to capture the worn (M, B).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_msub_rest_probe_model.py <id> <bench|held> <out.json>
"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_wear_probe as W                              # noqa: E402
from alignment_wear_probe_model import _ang, _dm               # noqa: E402  (the family reading's own formulas)


def msub_rows(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2
    dK = np.asarray(M.dK, float)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        rows.append(dict(i=i, kind=B.kind[i], th=round(th, 3), dK_deg=round(math.degrees(float(dK[i])), 4),
                         rest=bool(abs(float(dK[i])) <= 1e-6), m_plain=round(_dm(th, a1, a2), 3), m_eff=round(_dm(th, a1e, a2e), 3),
                         m_sub=round(_dm(th, b1, c), 3), min_mm=round(float(np.min(B.res[i])), 3),
                         **{k: float(B.poses[i][k]) for k in ("plane", "elev", "axial")}))
    return rows


def stats(rs, key):
    if not rs: return dict(n=0)
    m = np.array([r[key] for r in rs])
    return dict(n=len(rs), min=round(float(m.min()), 3), p10=round(float(np.percentile(m, 10)), 3), p50=round(float(np.median(m)), 3),
                lt5=int((m < 5 - 1e-6).sum()), lt2=int((m < 2).sum()), lt1=int((m < 1).sum()))


def run(rid, wear):
    row = json.load(open(os.path.join(W.REPO, "docs", "concepts", "rows", rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = W._load("amsub_" + rid.replace("-", "_"), os.path.join(W.REPO, "docs", "concepts", "models", rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(rid + ": no pin-knee-style audit to capture")
    cap = W._capture(pk)
    out = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    M, B = cap[-1]
    rows = msub_rows(M, B); rest = [r for r in rows if r["rest"]]; moved = [r for r in rows if not r["rest"]]
    fam = [min(r["m_sub"], r["m_eff"]) if not r["rest"] else r["m_plain"] for r in rows]
    return dict(design=rid, wear=wear, model_frozen=out.get("frozen"),
                family_reading=dict(min=round(float(min(fam)), 3) if fam else None, lt5=int(sum(1 for x in fam if x < 5 - 1e-6))),
                m_sub_rest=stats(rest, "m_sub"), m_sub_moved=stats(moved, "m_sub"), m_eff_moved=stats(moved, "m_eff"),
                m_plain_rest=stats(rest, "m_plain"), lowest_rest=sorted(rest, key=lambda r: r["m_sub"])[:8], rows=rows)


if __name__ == "__main__":
    t = time.time(); r = run(sys.argv[1], sys.argv[2]); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(sys.argv[3], "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in r.items() if k not in ("rows", "lowest_rest")}, default=float))
