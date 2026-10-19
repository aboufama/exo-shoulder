"""Extract the corrected geneva rod-drive geometry + per-pose drive state (fit fast, worn on Bench(110,360) exact)."""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("geneva_verify_x", os.path.join(REPO, "docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py"))
G, S, PK = V.G, V.S, V.PK
P = dict(G.PARAMS, **V.BEST)
t0 = time.time()
old = os.environ.pop("CB_EXACT", None)
B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = V.CorrModel(B1, dict(P)); r1 = M1.run()
print("fit", r1["gap"], round(time.time() - t0), flush=True)
os.environ["CB_EXACT"] = "1"
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]


class Frozen(V.CorrModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))
        self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)


B = CB.Bench(n_clip=110, n_ws=360)
M = Frozen(B, P2); r = M.run()
print("frozen", r["gap"], round(time.time() - t0), flush=True)
D = M.D; L = D.law()
u1, u2, u3 = D.u; uK = D.uK
taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 if B.res[i] is not None else False for i in range(len(B.idx))])
n = len(B.idx)
R1 = np.array([M.T(1, i)[0] for i in range(n)]); R7 = np.array([M.T(7, i)[0] for i in range(n)]); R2 = np.array([M.T(2, i)[0] for i in range(n)])
t1 = np.array([M.T(1, i)[1] for i in range(n)]); t7 = np.array([M.T(7, i)[1] for i in range(n)])
# arm segments (thorax frame) for gravity
import body_pose as BP
rig = BP._rig(); Lr = rig.L
Eb, Wb = [], []
for i in range(n):
    fr = B.frames(i); H = fr["H"]; F = fr["F"]
    E = H[0] @ np.array(Lr["elbow"]) + H[1]
    rh = F[0] @ np.array(Lr["radial_head"]) + F[1]; uh = F[0] @ np.array(Lr["ulnar_head"]) + F[1]
    Eb.append(E); Wb.append(0.5 * (rh + uh))
qq_, okk_, *_ = D.ik(M.Q); assert len(D._msub) == n, (len(D._msub), n)
out = dict(ikok=okk_, u1=u1, u2=u2, u3=u3, uK=uK, f=np.array(M.f), fK=float(M.fK), psiA=float(D.psiA), th_hi=float(D.th_hi), th_lo=float(D.th_lo),
           law_ts=L["ts"], law_dK=L["dK"], law_th=L["th"], law_q2t=L["q2t"], q2hi=float(L["q2hi"]), s_q=float(L["s_q"]),
           kin_ok=M.kin_ok, kstate=M.kstate, dK=M.dK, q2now=D._q2now, camt=D._camt, msub=D._msub, m3e=D._m3e, a1e=D._a1e, q2stops=np.array(D.q2_stops), a1=float(D.a1), a2=float(D.a2), q2sgn=float(D.q2sgn), resdeg=getattr(M,'res_deg',np.zeros(1)), taken=taken, kind=np.array([k == "clip" for k in B.kind]),
           R1=R1, R7=R7, R2=R2, t1=t1, t7=t7, E=np.array(Eb), W=np.array(Wb),
           rocker=M.rigid["rocker"][1], rod=M.rigid["rod"][1], rodends=M.rigid["rodends"][1], rodK=M.strap["RODK"][1], RODall=M.strap["ROD"][1],
           L1b=M.link_pts["L1b"][1], L1a=M.link_pts["L1a"][1], L2=M.link_pts["L2"][1],
           consts=np.array([S.HUB_R, S.UP, S.T_LINK, S.CROWN, S.RUN, float(P["capK"]), float(P["bk1"]), float(P["bk2"]), float(P["a1max"])]))
for k in ("hub1", "hubK", "hub2", "hub3"):
    if k in M.cyl:
        m, cen, ax = M.cyl[k]; out["cyl_" + k] = np.r_[m, cen, ax, M.cyl_r[k]]
np.savez(sys.argv[1], **out)
print(json.dumps(dict(rod=M._rod_info, why=r.get("why"), gap=r["gap"], lawend=L.get("why_end"), dKmax=L.get("dK_max"), tmax=L.get("t_max"),
                      consts=dict(HUB_R=S.HUB_R, UP=S.UP, T_LINK=S.T_LINK, CROWN=S.CROWN, RUN=S.RUN), f=list(map(float, M.f)), fK=float(M.fK),
                      last_clear=M.last_clear if hasattr(M, "last_clear") else None, secs=round(time.time() - t0)), default=float))
