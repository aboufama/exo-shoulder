"""Desmo K-drive red team (gen-9 winner desmo-conecut-knuckle-3r): fit the VERIFIED claim config (the model's BEST =
rows/desmo-conecut-knuckle-3r.json best_params, k57) with the claim's own model, loaded unchanged, on the fit bench
Bench(60,160) fast, and dump the drive geometry the build needs: crank axis / pivot, the stage-1 pin (F0) and its blended
groove centreline in link 2's frame, the stage-2 nose seat C0 and its slot path in the crank frame, every velocity /
normal the loads need, the metal samples, the model's own drive report (_rod_info) and the fit's per-pose K state.
Read-only on the model; local, niced.

    OMP_NUM_THREADS=1 nice -n 15 python3 docs/research/desmo_mechanism/extract.py docs/research/desmo_mechanism/geo_fit.npz
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
os.environ.pop("CB_EXACT", None)
sp_ = importlib.util.spec_from_file_location("dc_redteam_x", os.path.join(REPO, "docs/concepts/models/desmo-conecut-knuckle-3r.py"))
DC = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(DC)
DS, RF, S = DC.DS, DC.RF, DC.S
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/desmo-conecut-knuckle-3r.json")))
bp = row.get("best_params") or {}
par = dict(DC.BEST)
for k in DC.BEST:                                             # the row's best_params must equal the model's BEST (checked, reported)
    if k in bp and abs(float(bp[k]) - float(DC.BEST[k])) > 1e-6 if isinstance(DC.BEST[k], (int, float)) else False:
        print("WARN best_params differ", k, bp[k], DC.BEST[k])
t0 = time.time()
B = CB.Bench(n_clip=60, n_ws=160)
r, M = DC._report_dc(B, par)
print("fit", {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "contact")}, round(time.time() - t0), flush=True)
g = M._scg; dm = M._desmo; s2 = M._s2B; P = M.D.p; D = M.D
PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
u2 = D.u[1]; F0 = dm["F0"]; C0 = s2["C0"]
# fine K grid (0.05 deg) over the slot stroke + 2 deg
lim = float(g["dK_lim"]); kf = np.radians(np.arange(0.0, math.degrees(lim) + 2.0 + 1e-9, 0.05)); nk = len(kf)
ph = sig * RF.phi_of(kf, gg, cc); dph = sig * RF.dphi_of(kf, gg, cc)
RC = S.rotm(dR, ph); C = np.einsum("nij,j->ni", RC, F0)                 # pin centre, link 1b frame
s_th = float(dm["s_th"]); q_on = float(dm["q_on"])
vF = dph[:, None] * np.cross(np.tile(dR, (nk, 1)), C)                  # pin velocity per unit K (link 1b frame)
vcap = s_th * np.cross(np.tile(u2, (nk, 1)), C)                         # link-2 material point at C per unit K
X = np.einsum("nji,j->ni", S.rotm(uK, sp * kf), C0)                     # nose centre in link 1b frame
vN = -sp * np.cross(np.tile(uK, (nk, 1)), X)
vCx = dph[:, None] * np.cross(np.tile(dR, (nk, 1)), X)
Z = np.einsum("nji,nj->ni", RC, X)                                       # nose path in the crank frame (the slot centreline)
# blended groove centreline in link 2's frame (the model's construction)
bw = math.radians(float(P["blend"])); sa = abs(s_th); hb = bw / sa / 2.0
xg = np.arange(-hb - math.radians(5.0) / sa, lim + math.radians(2.0) + 1e-9, math.radians(0.05) / sa)
Kb = np.where(xg <= -hb, 0.0, np.where(xg >= hb, xg, (xg + hb) ** 2 / (4 * hb)))
qs = q_on + s_th * xg
Cq = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)), F0)
G2 = np.einsum("nij,ni->nj", S.rotm(u2, -(qs - q_on)), Cq) if False else np.einsum("nij,nj->ni", S.rotm(u2, -(qs - q_on)), Cq)
mL2 = M.link_pts["L2"][0]
taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
out = dict(PV=PV, dR=dR, uK=uK, sp=float(sp), sig=float(sig), gg=float(gg), cc=float(cc), u1=D.u[0], u2=u2, u3=D.u[2],
           F0=F0, s0=float(dm["s0"]), hmid=float(dm["hmid"]), bx=dm["bx"], by=dm["by"], s_th=s_th, q_on=q_on, r_out=float(dm["r_out"]),
           C0=C0, R0=float(s2["R0"]), rL=float(s2["rL"]), rb=float(s2["rb"]), rK0=float(s2["rK0"]), lim=lim,
           kf=kf, phi=ph, dphi=dph, C=C, vF=vF, vcap=vcap, X=X, vN=vN, vCx=vCx, Z=Z, xg=xg, Kb=Kb, G2=G2,
           f=np.array(M.f, float), fK=float(M.fK), kK=float(P["kK"]),
           dK=np.asarray(M.dK, float), kin_ok=np.asarray(M.kin_ok, bool), taken=taken,
           ring2=M.rigid["ring2"][1], plate=M.rigid["plate"][1], horn=M.rigid["horn"][1], crank=M.rigid["crank"][1],
           lowarm=g.get("lowarm", np.zeros((0, 3))))
for k in ("hub1", "hubK", "hub2", "hub3"):
    if k in M.cyl:
        m, cen, ax = M.cyl[k]; out["cyl_" + k] = np.r_[m, cen, ax, M.cyl_r[k]]
np.savez(sys.argv[1], **out)
info = M._rod_info
summ = dict(params=par, clamped={k: (v if isinstance(v, (int, float, str, bool)) or v is None else str(v)) for k, v in P.items()},
            fit={k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why")}, rod_info=info,
            consts=dict(HUB_R=S.HUB_R, T_LINK=S.T_LINK, PIN_D=DS.PIN_D, GROOVE_W=DS.GROOVE_W, RING_WALL=DS.RING_WALL, BORE_R=DS.BORE_R,
                        C_GROOVE=DS.C_GROOVE, ARM_W=DS.ARM_W, RUNG=RF.RUNG, SLOP_MAX=DS.SLOP_MAX),
            mL2=int(mL2), desmo_fail=getattr(M, "_desmo_fail", None), secs=round(time.time() - t0))
json.dump(summ, open(sys.argv[1].replace(".npz", ".json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
print(json.dumps(dict(fit=summ["fit"], fail=summ["desmo_fail"], secs=summ["secs"]), default=str))
