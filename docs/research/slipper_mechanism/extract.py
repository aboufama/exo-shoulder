"""Slipper-nose drive red team: wear the VERIFIED slipper-nose-knuckle-3r config (rows/slipper-nose-knuckle-3r.json
best_params, mu 0.087, nose_r 1.1839; knee stop ang_min = the lead's 25.2189 as the claim ran it) with the claim's own model
(loaded unchanged through its verifier harness, SN_CELL=lead) and the frozen protocol (fit Bench(60,160) fast, shape frozen,
worn on Bench(110,360) exact or held out), run the verifier's added checks (N1-N3), and dump the drive geometry, the cam
table, the per-pose state and the per-part signed skin distance of every drive part for drive.py.
Copied from docs/research/roller_mechanism/extract.py (the gen-6 roller) with the model retargeted.

    SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/slipper_mechanism/extract.py <out.npz> ['{}'] [bench|held]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


os.environ.setdefault("SN_CELL", "lead")
V = _load("slipper_verify_x", os.path.join(REPO, "docs/concepts/verify/slipper-nose-knuckle-3r.py"))
SN, H = V.SN, V.H
RF, SC, S, PK = SN.RF, SN.SC, SN.S, SN.PK
over = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
wear = sys.argv[3] if len(sys.argv) > 3 else "bench"
V.retarget(dict(V.BEST, **over))
P = SN._clamp(dict(SN.PARAMS, **dict(V.BEST, **over)))
t0 = time.time()
old = os.environ.pop("CB_EXACT", None)
B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = SN.SNModel(B1, dict(P)); r1 = M1.run()
fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
print("fit", fit, round(time.time() - t0), flush=True)
os.environ["CB_EXACT"] = "1"
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]


class Frozen(SN.SNModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_cam_table", "_wedge_info"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))
        self._sc = None
        self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        self._truncate()


if wear == "held":
    PVm = _load("pk_polish_v_slipper_x", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py")); B = PVm.held_bench()
else:
    B = CB.Bench(n_clip=110, n_ws=360)
M = Frozen(B, P2); r = M.run()
rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
aud = PK.audit(M, B); ex = V.extra_checks(M, M1, B)
print("frozen", rep, round(time.time() - t0), flush=True)
D = M.D; L = D.law(); g = M._scg; ct = M._cam_table
n = len(B.idx)
taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(n)])
kin = np.asarray(M.kin_ok, bool)
# per-part signed skin distance (rigid samples by name) on every kinematically reached pose (taken + lost to contact / skin)
names = sorted(M.rigid.keys()); PD = np.full((n, len(names)), np.nan)
for i in np.nonzero(kin)[0]:
    for j, nm in enumerate(names):
        m, X = M.rigid[nm]
        if len(X): PD[i, j] = float(B.dist(i, M.world(m, i, X)).min())
T = {m: [M.T(m, i) for i in range(n)] for m in (1, 2, 7, 9)}
whys = np.array([str(M.why[i]) for i in range(n)])
poses = np.array([[float(B.poses[i].get("plane", np.nan)), float(B.poses[i].get("elev", np.nan)), float(B.poses[i].get("axial", np.nan))] for i in range(n)])
out = dict(u1=D.u[0], u2=D.u[1], u3=D.u[2], uK=D.uK, f=np.array(M.f, float), fK=float(M.fK), psiA=float(D.psiA),
           law_ts=np.asarray(L["ts"]), law_dK=np.asarray(L["dK"]), law_th=np.asarray(L["th"]), law_q2t=np.asarray(L["q2t"]),
           q2hi=float(L["q2hi"]), q2stops=np.array(D.q2_stops, float), a1=float(D.a1), a2=float(D.a2),
           kin_ok=kin, kstate=np.asarray(M.kstate), dK=np.asarray(M.dK, float), q2now=np.asarray(D._q2now, float),
           camt=np.asarray(D._camt, float), m3e=np.asarray(D._m3e, float), msub=np.asarray(D._msub, float),
           taken=taken, kind=np.array([k == "clip" for k in B.kind]), whys=whys, poses=poses,
           R1=np.array([x[0] for x in T[1]]), t1=np.array([x[1] for x in T[1]]), R2=np.array([x[0] for x in T[2]]), t2=np.array([x[1] for x in T[2]]),
           R7=np.array([x[0] for x in T[7]]), t7=np.array([x[1] for x in T[7]]), R9=np.array([x[0] for x in T[9]]), t9=np.array([x[1] for x in T[9]]),
           PV=g["PV"], dR=g["dR"], sp=float(g["sp"]), sig=float(g["sig"]), gg=float(g["g"]), cc=float(g["c"]), kgrid=g["kgrid"], dK_lim=float(g["dK_lim"]),
           C0=np.asarray(M._viz_rod["roller"], float), armPts=np.array(M._viz_rod["armPts"], float), lugPts=np.array(M._viz_rod["lugPts"], float),
           ct_pa_crank=ct["pa_crank"], ct_pa_horn=ct["pa_horn"], ct_contact_r=ct["contact_r"], ct_flank_rho=ct["flank_rho"],
           ct_clear_hubK=ct["clear_hubK"], ct_clear_roll_hubK=ct["clear_roll_hubK"], ct_clear_hub2=ct["clear_hub2"],
           crank=M.rigid["crank"][1], roller=(M.rigid["roller"][1] if "roller" in M.rigid else np.zeros((0, 3))), horn=M.rigid["horn"][1], lugM=g["lugM"], lowarm=g["lowarm"],
           L1b=M.link_pts["L1b"][1], L1a=M.link_pts["L1a"][1], L2=M.link_pts["L2"][1],
           PD=PD, PDnames=np.array(names),
           consts=np.array([S.HUB_R, S.UP, S.T_LINK, S.CROWN, S.RUN, S.W_LINK, float(P["bk1"]), float(P["bk2"]), float(P["a1max"]),
                            float(P["kK"]), float(P["r_c"]), float(P["beta"]), float(P["s_arm"]), float(P["r_lobe"]), float(P["hl"]),
                            float(P.get("lift", 0.0)), float(P["g"]), float(P["zr"]), float(P["ang_min"]), float(P["nose_r"]), float(P["mu"])]))
for k in ("hub1", "hubK", "hub2", "hub3"):
    if k in M.cyl:
        m, cen, ax = M.cyl[k]; out["cyl_" + k] = np.r_[m, cen, ax, M.cyl_r[k]]
np.savez(sys.argv[1], **out)
drv = ["crank", "roller", "horn"]
pd_t = {nm: round(float(np.nanmin(PD[taken, j])), 3) for j, nm in enumerate(names) if np.isfinite(PD[taken, j]).any()}
summ = dict(over=over, wear=wear, fit=fit, frozen=rep, near1=aud.get("gap_near1"), near2=aud.get("gap_near2"), minmetal=aud.get("near_touch_min_mm"),
            ovh=aud.get("overhead140"), why=r.get("why"), parts_pairs=r.get("parts_pairs"), extra=ex, sidecar=getattr(M1, "_sc_info", None),
            part_skin_min_taken=pd_t, n_taken=int(taken.sum()), n_kin=int(kin.sum()),
            consts=dict(HUB_R=S.HUB_R, UP=S.UP, T_LINK=S.T_LINK, CROWN=S.CROWN, RUN=S.RUN, W_LINK=S.W_LINK, RUNG=SC.RUNG, BOSS_H=SC.BOSS_H),
            f=list(map(float, M.f)), fK=float(M.fK), secs=round(time.time() - t0))
json.dump(summ, open(sys.argv[1].replace(".npz", ".json"), "w"), indent=1, default=float)
print(json.dumps(summ, default=float)[:4000])
