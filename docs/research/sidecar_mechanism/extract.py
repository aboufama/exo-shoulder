"""Sidecar drive red team: wear the VERIFIED sidecar-longdyad-knuckle-3r config (or a variant) with the claim's own model and
frozen protocol (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact or held out), run the verifier's added
checks, and dump the drive geometry + per-pose state for drive.py / loads.py.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/sidecar_mechanism/extract.py <out.npz> ['{"r_h": 15.5}'] [bench|held]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("sidecar_verify_x", os.path.join(REPO, "docs/concepts/verify/sidecar-longdyad-knuckle-3r.py"))
SC, S, PK = V.SC, V.S, V.PK
over = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
wear = sys.argv[3] if len(sys.argv) > 3 else "bench"
P = SC._clamp(dict(SC.PARAMS, **dict(V.BEST, **over)))
t0 = time.time()
old = os.environ.pop("CB_EXACT", None)
B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = SC.SCModel(B1, dict(P)); r1 = M1.run()
fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
print("fit", fit, round(time.time() - t0), flush=True)
os.environ["CB_EXACT"] = "1"
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]


class Frozen(SC.SCModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))
        self._sc = None
        self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        self._truncate()


if wear == "held":
    PVm = _load("pk_polish_v_sidecar_x", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py")); B = PVm.held_bench()
else:
    B = CB.Bench(n_clip=110, n_ws=360)
M = Frozen(B, P2); r = M.run()
rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
aud = PK.audit(M, B); ex = V.extra_checks(M, B)
print("frozen", rep, round(time.time() - t0), flush=True)
D = M.D; L = D.law(); g = M._scg
n = len(B.idx)
taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(n)])
T = {m: [M.T(m, i) for i in range(n)] for m in (1, 2, 7, 8, 9)}
# per-pose part-pair clearances (the model's own collide, the drive pairs it added)
keys = ["ROD-hubK", "ROD-hub2", "ROD-L1b", "CRK-hub1", "CRK-hubK", "CRK-hub3", "CRK-hub2", "CRK-L1a", "CRK-L2", "HORN-L1b", "HORN-hub2", "HORN-L2",
        "knee-CRK", "pad-CRK", "knee-HORN", "pad-HORN", "E-CRK", "E-HORN"]
CL = np.full((n, len(keys)), np.nan)
for i in np.nonzero(taken)[0]:
    M.last_clear = {}; M.collide(i)
    for j, k in enumerate(keys): CL[i, j] = M.last_clear.get(k, np.nan)
# arm points for gravity (thorax frame)
import body_pose as BP
rig = BP._rig(); Lr = rig.L
Eb, Wb = [], []
for i in range(n):
    fr = B.frames(i); H = fr["H"]; F = fr["F"]
    E = H[0] @ np.array(Lr["elbow"]) + H[1]
    rh = F[0] @ np.array(Lr["radial_head"]) + F[1]; uh = F[0] @ np.array(Lr["ulnar_head"]) + F[1]
    Eb.append(E); Wb.append(0.5 * (rh + uh))
D.ik(M.Q)
out = dict(u1=D.u[0], u2=D.u[1], u3=D.u[2], uK=D.uK, f=np.array(M.f, float), fK=float(M.fK), psiA=float(D.psiA),
           law_ts=np.asarray(L["ts"]), law_dK=np.asarray(L["dK"]), law_th=np.asarray(L["th"]), law_q2t=np.asarray(L["q2t"]),
           q2hi=float(L["q2hi"]), s_q=float(L["s_q"]), q2stops=np.array(D.q2_stops, float), a1=float(D.a1), a2=float(D.a2),
           kin_ok=np.asarray(M.kin_ok), kstate=np.asarray(M.kstate), dK=np.asarray(M.dK, float), q2now=np.asarray(D._q2now, float),
           camt=np.asarray(D._camt, float), msub=np.asarray(D._msub, float), m3e=np.asarray(D._m3e, float), a1e=np.asarray(D._a1e, float),
           taken=taken, kind=np.array([k == "clip" for k in B.kind]),
           R1=np.array([x[0] for x in T[1]]), t1=np.array([x[1] for x in T[1]]), R2=np.array([x[0] for x in T[2]]), t2=np.array([x[1] for x in T[2]]),
           R7=np.array([x[0] for x in T[7]]), t7=np.array([x[1] for x in T[7]]), R8=np.array([x[0] for x in T[8]]), t8=np.array([x[1] for x in T[8]]),
           R9=np.array([x[0] for x in T[9]]), t9=np.array([x[1] for x in T[9]]), E=np.array(Eb), W=np.array(Wb),
           PV=g["PV"], dR=g["dR"], tip0=g["tip0"], H0=g["H0"], kgrid=g["kgrid"], phig=g["phig"], sp=float(g["sp"]), dK_lim=float(g["dK_lim"]),
           crank=M.rigid["crank"][1], horn=M.rigid["horn"][1], rod=M.rigid["rod"][1], rodends=M.rigid["rodends"][1],
           L1b=M.link_pts["L1b"][1], L1a=M.link_pts["L1a"][1], L2=M.link_pts["L2"][1],
           strapL1b=M.strap["L1b"][1], strapL1a=M.strap["L1a"][1], strapL2=M.strap["L2"][1],
           CL=CL, CLkeys=np.array(keys),
           consts=np.array([S.HUB_R, S.UP, S.T_LINK, S.CROWN, S.RUN, S.W_LINK, float(P["bk1"]), float(P["bk2"]), float(P["a1max"]),
                            float(P["kK"]), float(P["r_h"]), float(P["La"]), float(P["s_arm"]), float(P["r_lobe"]), float(P["hl"]), float(P["beta"])]))
for k in ("hub1", "hubK", "hub2", "hub3"):
    if k in M.cyl:
        m, cen, ax = M.cyl[k]; out["cyl_" + k] = np.r_[m, cen, ax, M.cyl_r[k]]
np.savez(sys.argv[1], **out)
summ = dict(over=over, wear=wear, fit=fit, frozen=rep, near1=aud.get("gap_near1"), near2=aud.get("gap_near2"), minmetal=aud.get("near_touch_min_mm"),
            ovh=aud.get("overhead140"), why=r.get("why"), parts_pairs=r.get("parts_pairs"), extra=ex, sidecar=getattr(M1, "_sc_info", None),
            min_clear_taken={k: round(float(np.nanmin(CL[:, j])), 3) for j, k in enumerate(keys) if np.isfinite(CL[:, j]).any()},
            m3e_min_taken=round(float(np.asarray(D._m3e)[taken & (np.asarray(M.kstate) == 1)].min()), 3) if (taken & (np.asarray(M.kstate) == 1)).any() else None,
            msub_min_taken=round(float(np.asarray(D._msub)[taken].min()), 3),
            consts=dict(HUB_R=S.HUB_R, UP=S.UP, T_LINK=S.T_LINK, CROWN=S.CROWN, RUN=S.RUN, W_LINK=S.W_LINK), f=list(map(float, M.f)), fK=float(M.fK),
            secs=round(time.time() - t0))
json.dump(summ, open(sys.argv[1].replace(".npz", ".json"), "w"), indent=1, default=float)
print(json.dumps(summ, default=float))
