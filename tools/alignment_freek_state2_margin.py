"""Auditor tool (new file, 2026-10-18): the fold margin of freek-oracle-route-knuckle-4r cell B, read on the MOVING chain of
every state, in the one metric th (tools/concept_kit.py lines 25-30: a dyad's J1 -> J3 angle's distance from its fold).

Why: the claim's continuity flood (RM.kin_nodes, the family reading min(m_sub, m_eff)) and the model's own reading (the
effective dyad m3e) disagree in state 2 (J3 on its own-angle dowel, J2 free in its slot, K free between its stops). The
verifier's answer (verify/freek-oracle-route-knuckle-4r/verify_margins_*.json "wrist_moving_min") was produced by a script
that is not in the repo. This file re-measures it from the repo, unchanged models only, and adds the one-metric reading
of the state-2 moving dyad J1 -> K -> J2: th_K = angle(u1, J2 axis) against its link angles bk1 = angle(u1, uK) and
c = angle(uK, J2 axis) (both constant: K sits on link 1a, J2 on link 1b), i.e. dmargin(th_K, bk1, c).

Per state (0 = state A: K on stop A, J1-J2-J3 moves; 1 = stretched: J2 on its stop, J1-K-J3 moves; 2 = J3 on its dowel,
J1-K-J2 moves) over the TAKEN poses of the claim's per-pose dump (docs/alignment/remeasure/<id>_<wear>_perpose.json):
  m3e        the model's reading (effective dyad J1-J2-J3 th margin)
  msub       the family's extra term (J1-K-J3 sub-chain th margin, J2 rigid)
  kdyad      the J1-K-J2 dyad's th margin (the moving dyad of state 2)
  oop_*      out-of-plane angle of each 3-axis set (0 = coplanar = singular 3R): A = (u1, J2, J3), 1 = (u1, K, J3),
             2 = (u1, K, J2)
It never edits a model, a bench, a judge or a row.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_freek_state2_margin.py bench|held
        -> docs/alignment/remeasure/freek-oracle-route-knuckle-4r_<wear>_state_margins.json
"""
import importlib.util, json, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RID = "freek-oracle-route-knuckle-4r"


def main(wear):
    t0 = time.time(); argv = sys.argv; sys.argv = [argv[0]]
    sp = importlib.util.spec_from_file_location("vv_freek_aud", os.path.join(REPO, "docs", "concepts", "verify", RID + "-verify.py"))
    V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V); sys.argv = argv
    V.VDesign.OWN = False                                    # the claim's stop reading (q3 = cuff vs link 2; q3' = q3 + phi)
    RM, CB = V.RM, V.CB
    dump = json.load(open(os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_{wear}_perpose.json")))
    B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
    Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float)
    P = V.FO.params({"q3max": 86}); P.pop("_seed", None); D = V.VDesign(P)
    _ = D.ik(Q[:2])
    okn, qq, sg, stn, fam = RM.kin_nodes(D, Q, float(P["R_tol"]))
    q, ok, X1, X2, X3, s = D.ik(Q); st = np.asarray(D._state).copy(); m3e = np.asarray(D._m3e, float); X1b = D._X1b[0]
    u1, u2, u3 = D.u; uK = D.uK
    jK = np.einsum("nij,j->ni", X1[0], uK); j2 = np.einsum("nij,j->ni", X1b, u2); j3 = np.einsum("nij,j->ni", X2[0], u3)
    ang, dmargin = RM.ang, RM.dmargin
    U1 = np.broadcast_to(u1, jK.shape)
    th = ang(U1, j3); a1e = ang(U1, j2); a2e = ang(j2, j3); b1 = ang(U1, jK); cK3 = ang(jK, j3); cK2 = ang(jK, j2)
    msub = dmargin(th, b1, cK3); kdyad = dmargin(a1e, b1, cK2)

    def oop(a, b, c):
        n = np.cross(a, b); n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
        return np.degrees(np.arcsin(np.clip(np.abs(np.einsum("ij,ij->i", n, c)), 0, 1)))
    oA, o1, o2 = oop(U1, j2, j3), oop(U1, jK, j3), oop(U1, jK, j2)
    # state-2 statics (J1, J2 free: zero torque; K carries its spring torque tK; J3 its dowel reaction t3): the cuff moment is
    # w = lam (u1 x J2), tK = lam det(uK, u1, J2), t3 = lam det(u3, u1, J2) -> per unit spring torque the cuff carries
    # |u1 x J2| / |det(uK, u1, J2)| and the dowel |det(u3, u1, J2)| / |det(uK, u1, J2)|
    c12 = np.cross(U1, j2); dK_ = np.einsum("ij,ij->i", jK, c12); d3_ = np.einsum("ij,ij->i", j3, c12)
    cuff_per_tK = np.linalg.norm(c12, axis=1) / np.maximum(np.abs(dK_), 1e-12); dowel_per_tK = np.abs(d3_) / np.maximum(np.abs(dK_), 1e-12)
    tk = [p["i"] for p in dump["poses"] if p["taken"]]; kind = {p["i"]: p["kind"] for p in dump["poses"]}
    pose = {p["i"]: p.get("pose") for p in dump["poses"]}

    def stat(a, ii):
        if not len(ii): return None
        j = ii[int(np.argmin(a[ii]))]
        return dict(min=round(float(a[ii].min()), 2), p5=round(float(np.percentile(a[ii], 5)), 2), at=int(j), at_kind=kind[j],
                    lt5=int((a[ii] < 5.0 - 1e-6).sum()), lt55=int((a[ii] < 5.5 - 1e-6).sum()))
    out = dict(id=RID, wear=wear, reading="claim's cell B (q3max 86, model q3 reading), taken poses of the claim's per-pose dump",
               dump_gap=dump.get("recomputed"), n_taken=len(tk), states={})
    for name in (0, 1, 2):
        ii = np.array([i for i in tk if st[i] == name], int)
        if not len(ii): continue
        out["states"][str(name)] = dict(n=len(ii), clip=int(sum(kind[i] == "clip" for i in ii)), m3e=stat(m3e, ii), family_own=stat(fam, ii),
                                        msub=stat(msub, ii), kdyad=stat(kdyad, ii), oop_A=stat(oA, ii), oop_1=stat(o1, ii), oop_2=stat(o2, ii),
                                        dK_deg=[round(float(np.degrees(D._dK[ii]).min()), 2), round(float(np.degrees(D._dK[ii]).max()), 2)])
    ii = np.array([i for i in tk if st[i] == 2], int)
    out["state2_rows"] = [dict(i=int(i), kind=kind[i], m3e=round(float(m3e[i]), 2), msub=round(float(msub[i]), 2), kdyad=round(float(kdyad[i]), 2),
                               oop_2=round(float(o2[i]), 2), dK=round(float(np.degrees(D._dK[i])), 2),
                               cuff_moment_per_spring_torque=round(float(cuff_per_tK[i]), 3), dowel_torque_per_spring_torque=round(float(dowel_per_tK[i]), 3)) for i in ii]
    if len(ii):
        out["state2_statics"] = dict(cuff_moment_per_spring_torque=[round(float(cuff_per_tK[ii].min()), 3), round(float(np.median(cuff_per_tK[ii])), 3), round(float(cuff_per_tK[ii].max()), 3)],
                                     dowel_torque_per_spring_torque=[round(float(dowel_per_tK[ii].min()), 3), round(float(np.median(dowel_per_tK[ii])), 3), round(float(dowel_per_tK[ii].max()), 3)],
                                     how="[min, median, max] over taken state-2 poses; rigid links, frictionless pins, J1 / J2 unloaded")
    out["moving_chain_min_th"] = dict(
        how="state 0: dyad (J1-J2-J3) m3e; state 1: min(msub, m3e) (the model's forced-state rule); state 2: kdyad (J1-K-J2, the moving dyad) and m3e",
        min=round(float(min([m3e[i] for i in tk if st[i] == 0] + [min(msub[i], m3e[i]) for i in tk if st[i] == 1] +
                            [min(kdyad[i], m3e[i]) for i in tk if st[i] == 2])), 2))
    out["secs"] = round(time.time() - t0, 1)
    p = os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_{wear}_state_margins.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("wear", "n_taken", "states", "moving_chain_min_th", "secs")}, default=float))


if __name__ == "__main__":
    main(sys.argv[1])
