"""skeptic probe (usage: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_msub_rest_probe.py bench out.json [--d0]): the J1-K-J3 sub-chain margin m_sub on EVERY taken pose (also K at rest), dipped claim vs its D=0 control
(models and verifier loaded unchanged; only th_margin is wrapped to record more)"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sp = importlib.util.spec_from_file_location("dip_v_sk", os.path.join(REPO, "docs/concepts/verify/dipped-law-groove-knuckle-3r.py"))
V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
_orig = V.th_margin
REC = {}
def th_margin_ext(M, B):
    out = _orig(M, B)
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    dK = np.asarray(M.dK, float) * (float(M._scg["sp"]) if getattr(M, "_scg", None) else 1.0)
    rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = V._ang(u1, j3); a1e = V._ang(u1, j2); a2e = V._ang(j2, j3); b1 = V._ang(u1, jK); c = V._ang(jK, j3)
        rows.append(dict(i=i, kind=B.kind[i], th=th, dK=math.degrees(float(dK[i])), m_sub=V._dm(th, b1, c), m_eff=V._dm(th, a1e, a2e),
                         **{k: float(B.poses[i][k]) for k in ("plane", "elev", "axial")}))
    rest = [r for r in rows if abs(r["dK"]) <= 1e-4]; dip = [r for r in rows if r["dK"] < -1e-4]; law = [r for r in rows if r["dK"] > 1e-4]
    def st(rs):
        if not rs: return dict(n=0)
        m = np.array([r["m_sub"] for r in rs]); return dict(n=len(rs), m_sub_min=round(float(m.min()), 3), m_sub_p50=round(float(np.median(m)), 3),
                                                        m_sub_max=round(float(m.max()), 3), lt5=int((m < 5 - 1e-6).sum()), lt1=int((m < 1).sum()))
    out["skeptic_msub_all"] = dict(rest=st(rest), dipped=st(dip), law=st(law),
                                   dipped_edge=[dict(dK=round(r["dK"], 3), m_sub=round(r["m_sub"], 3)) for r in sorted(dip, key=lambda r: r["dK"], reverse=True)[:8]],
                                   dipped_floor=[dict(dK=round(r["dK"], 3), m_sub=round(r["m_sub"], 3)) for r in sorted(dip, key=lambda r: r["dK"])[:5]])
    out["skeptic_rows"] = rows
    return out
V.th_margin = th_margin_ext
wear, path = sys.argv[1], sys.argv[2]
P = dict(V.BEST)
if "--d0" in sys.argv: P["dipD"] = 0.0; P["dip_ref"] = 0.0
t = time.time(); out = V.H.frozen_wear(P, wear, False, False)
res = dict(wear=wear, d0="--d0" in sys.argv, frozen=out["frozen"], th_margin={k: v for k, v in out["extra"]["th_margin"].items() if k != "skeptic_rows"},
           rows=out["extra"]["th_margin"].get("skeptic_rows"), secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
json.dump(res, open(path, "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, default=float))
