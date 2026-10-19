"""minarc-stop-knuckle-4r variant B - skeptic verifier (third lens: the corrected claim on the champion's bench).

Wears the claim's BD shape (frozen protocol: fit Bench(60,160) fast, wear Bench(110,360) exact) under a stop reading and
audits every taken pose INDEPENDENTLY of the model's law, from the bench's arm pose Q alone:
  * th = angle(u1, Q u3) and the J1-J3 fold margin of the 3R dyad m3 = min(th - |a1 - a2|, a1 + a2 - th) for K on stop A;
  * forward kinematics of the 4 member frames from (q1, dK, q2, q3): J3's world axis must equal Q u3 (closure);
  * K one-sided (dK has the sign of -psiA, |dK| <= stop B), and in the forced states the J1-K-J3 sub-chain margin.
    python3 minarc-stop-knuckle-4r-skeptic.py <reading: claim|stops5|stops10> out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sp = importlib.util.spec_from_file_location("mk", os.path.join(REPO, "docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py"))
MK = importlib.util.module_from_spec(sp); sp.loader.exec_module(MK)
CB, S = MK.CB, MK.S
ROW = json.load(open(os.path.join(REPO, "docs/concepts/rows/minarc-stop-knuckle-4r.json")))
BP = ROW["best_params"]; BP = json.loads(BP) if isinstance(BP, str) else BP


def phi_of_margin(a1, a2, m):
    r = math.radians
    f = lambda th: math.degrees(math.acos((math.cos(r(th)) - math.cos(r(a1)) * math.cos(r(a2))) / (math.sin(r(a1)) * math.sin(r(a2)))))
    return f(abs(a1 - a2) + m), f(min(a1 + a2, 360 - a1 - a2) - m)


def run(reading):
    P = dict(MK.PARAMS, **BP)
    D0 = MK.KDesign(P); a1, a2 = D0.a1, D0.a2
    if reading.startswith("stops"):
        m = float(reading[5:]); P["phi_lo"], P["phi_hi"] = phi_of_margin(a1, a2, m)
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = MK.KModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(MK.KModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=110, n_ws=360); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    # ---- independent audit of the taken poses
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    Q = M.Q
    q, ok, X1, X2, X3, s = D.ik(Q)
    st, dK, msub, a1e = D._state.copy(), D._dK.copy(), D._msub.copy(), D._a1e.copy()
    w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    m3 = np.minimum(th - abs(a1 - a2), a1 + a2 - th)
    R1 = S.rotm(u1, q[:, 0]); RK = S.rotm(uK, dK); v2 = RK @ u2
    R2 = MK.rotmv(v2, q[:, 1]); R3 = S.rotm(u3, q[:, 2])
    Rall = R1 @ R2 @ RK @ R3                                  # member 3's rotation from the joint values alone
    c = (np.einsum("nij,nij->n", Rall, Q) - 1) / 2; clos = np.degrees(np.arccos(np.clip(c, -1, 1)))
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ws = np.array([k == "ws" for k in B.kind]); el = np.array([p["elev"] for p in B.poses])
    A = tk & (st == 0); F = tk & (st != 0); nz = tk & (np.abs(dK) > 1e-9)
    aud = dict(a_deg=[round(a1, 3), round(a2, 3)], phi_stops=[round(float(P2["phi_lo"]), 3), round(float(P2["phi_hi"]), 3)],
               taken=int(tk.sum()), taken_ws=int((tk & ws).sum()), taken_stateA=int(A.sum()), taken_forced=int(F.sum()),
               taken_forced_ws=int((F & ws).sum()), taken_forced_clip=int((F & ~ws).sum()),
               min_m3_stateA=round(float(m3[A].min()), 3) if A.any() else None,
               n_stateA_m3_lt5=int((A & (m3 < 5 - 1e-6)).sum()), n_stateA_m3_lt10=int((A & (m3 < 10 - 1e-6)).sum()),
               n_clip_stateA_m3_lt5=int((A & ~ws & (m3 < 5 - 1e-6)).sum()),
               min_m3_forced=round(float(m3[F].min()), 3) if F.any() else None,
               min_sub_margin_forced=round(float(msub[F].min()), 3) if F.any() else None,
               max_closure_deg_taken=round(float(clos[tk].max()), 5),
               dK_deg_taken=[round(float(np.degrees(dK[tk]).min()), 2), round(float(np.degrees(dK[tk]).max()), 2)],
               dK_one_sided=bool(len(set(np.sign(dK[nz]).tolist())) <= 1),
               a1e_max_taken=round(float(a1e[tk].max()), 2), a1max=float(P2["a1max"]),
               overhead_ws=[int((tk & ws & (el >= 140)).sum()), int((ws & (el >= 140)).sum())])
    return dict(reading=reading, fit_fast=fit, frozen=rep, why=r.get("why"), audit=aud, near=MK.PK.audit(M, B), mode=B.mode)


if __name__ == "__main__":
    t = time.time(); out = run(sys.argv[1]); out["secs"] = round(time.time() - t, 1)
    s = json.dumps(out, indent=1, default=float); print(s)
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(s)
