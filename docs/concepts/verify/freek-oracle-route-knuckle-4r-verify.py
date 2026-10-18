"""Verifier (skeptic) of freek-oracle-route-knuckle-4r cell B: the J3 hard stop as built.

The claim's cell B puts a dowel stop on "J3's own angle" at q3max (model convention), but the model reads q3 = the angle
of the CUFF relative to link 2 about u3 (S.sub1 between R12 and Q). The two-pin knee rotates member 3 about the J3 axis by
phi, so J3's own angle (link 2 -> member 3, the two bodies the dowel sits between) is q3' = q3 + phi - the reading the
lead's verified stop uses (docs/concepts/conecut-knee-knuckle-3r.md C1: R2^T R3 equals q3 + phi to 0.0008 deg) and the
reading the kit's own clip continuity uses (minarc-stop-knuckle-4r-pinknee.py continuity()). CLAUDE.md: "A hard stop acts
on a joint's OWN angle ... never on a virtual angle between non-adjacent bodies." Link 2 and the cuff are not adjacent.

This file (1) measures how far the claim's stop wanders on J3's own angle (q3' at every taken stop-engaged pose), and
(2) re-builds cell B with the stop on q3' (K opens until q3' = q3max', same first-crossing scan, same checks), re-picks
q3max' on the fit bench (Bench(60,160) fast, near-touch gap, as the proposer did) and wears the pick frozen on
Bench(110,360) exact with the remeasure harness's kinematic flood fill (connected reading) and on the held-out bench.

    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/freek-oracle-route-knuckle-4r-verify.py diag 86 OUT.json
    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 ... fit '[80,86,92]' OUT.json            (q3' stop, fit bench)
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 ... wear 86 OUT.json [held]  (q3' stop)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sp = importlib.util.spec_from_file_location("fo_for_verify", os.path.join(REPO, "docs", "concepts", "models", "freek-oracle-route-knuckle-4r.py"))
FO = importlib.util.module_from_spec(sp); sp.loader.exec_module(FO)
KR, KB, S, PK, CB, KIT, RM = FO.KR, FO.KB, FO.S, FO.PK, FO.CB, FO.KIT, FO.RM
KEYS = FO.KEYS


def wr(a): return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


class VDesign(FO.ODesign):
    """cell B with the stop on J3's OWN angle q3' = q3 + knee phi (OWN 1), else the claim's q3 reading (OWN 0)"""
    OWN = True

    def __init__(self, params=None):
        super().__init__(params)
        if self.p.get("m_fix") is not None:                  # the knee reference is needed INSIDE ik (phi) - set it before the first ik
            self.m = np.array(self.p["m_fix"], float); self.m[2] = 0.0

    def q3own(self, q, s):
        if not VDesign.OWN: return wr(np.degrees(q[:, 2]))
        return wr(np.degrees(q[:, 2] + self.knee(s)["phi"]))

    def j3stop2(self, Q, q, ok, s):
        q3max = self.p.get("q3max")
        if q3max is None or not len(Q): return {}
        q3 = self.q3own(q, s); sel = np.nonzero(ok & (q3 > float(q3max)))[0]
        if not len(sel): return {}
        dkb = self.dKB(); grid = np.arange(0.0, dkb + 1e-9, 0.5); out = {}
        for i in sel:
            d0 = abs(float(np.degrees(self._dK[i]))); g = grid[grid >= d0 - 1e-9]
            f = self.free_solve(np.repeat(Q[i][None], len(g), 0), g); qq = self.q3own(f["q"], f["s"])
            hit = np.nonzero(f["ok"] & (qq <= float(q3max)))[0]
            if not len(hit): out[int(i)] = None; continue
            k = int(hit[0])
            if k > 0 and f["ok"][k - 1]:
                a, b = qq[k - 1], qq[k]; t = (a - float(q3max)) / max(a - b, 1e-9); out[int(i)] = float(g[k - 1] + t * (g[k] - g[k - 1]))
            else: out[int(i)] = float(g[k])
        return out

    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = KR.KRDesign._ik_phys(self, Q)
        tab_ = {}
        js = self.j3stop2(Q, q, ok, s); refuse = [i for i, v in js.items() if v is None]
        tab_.update({i: v for i, v in js.items() if v is not None})
        if refuse: ok = ok.copy(); ok[refuse] = False
        if not tab_: return q, ok, X1, X2, X3, s
        idx = np.array(sorted(tab_), int)
        f = self.free_solve(Q[idx], np.array([tab_[i] for i in idx]))
        q = q.copy(); ok = ok.copy(); s = s.copy()
        R1m, Z0 = X1; R1m = R1m.copy(); R2m = X2[0].copy(); R3m, t3m = X3[0].copy(), X3[1].copy(); X1b = self._X1b[0].copy()
        q[idx] = f["q"]; ok[idx] = f["ok"]; R1m[idx] = f["R1"]; R2m[idx] = f["R12"]; R3m[idx] = f["R123"]; t3m[idx] = f["t3"]; s[idx] = f["s"]
        X1b[idx] = f["R1b"]
        self._dK = self._dK.copy(); self._dK[idx] = f["dK"]; self._state = self._state.copy(); self._state[idx] = 2
        self._a1e = self._a1e.copy(); self._a1e[idx] = f["a1e"]; self._msub = np.asarray(self._msub, float).copy(); self._msub[idx] = 99.0
        self._m3e = self._m3e.copy(); self._m3e[idx] = f["m3e"]
        self._X1b = (X1b, self._X1b[1])
        return q, ok, (R1m, Z0), (R2m, X2[1]), (R3m, t3m), s


KB.KDesign = VDesign
FO.ODesign.SLOT55 = False                                     # cell B: J2 keeps its own priced slot in every state


def taken(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


def stop_report(M, B):
    """q3 (claim reading), phi and q3' (J3's own angle) over taken poses, split by stop-engaged (state 2) and the rest"""
    tk = taken(B); q3 = wr(np.degrees(M.q[:, 2])); phi = np.degrees(M.K["phi"]); q3p = wr(q3 + phi); st = np.asarray(M.kstate)
    e = [i for i in tk if st[i] == 2]; o = [i for i in tk if st[i] != 2]
    def rng(a, ii): return [round(float(a[ii].min()), 2), round(float(a[ii].max()), 2)] if len(ii) else None
    return dict(taken=len(tk), engaged=len(e), q3_engaged=rng(q3, e), phi_engaged=rng(phi, e), q3own_engaged=rng(q3p, e),
                q3_other_max=(round(float(q3[o].max()), 2) if o else None), q3own_other_max=(round(float(q3p[o].max()), 2) if o else None),
                q3own_all_max=(round(float(q3p[tk].max()), 2) if tk else None), phi_all=rng(phi, tk))


def flood_connected(Mk, B, tk):
    Z, Wg, POSE, HG = RM.ws_grid(); D = Mk.D; R_tol = float(Mk.p["R_tol"]); _ = D.ik(HG[:2])
    okn, qq, sgn, st, own = RM.kin_nodes(D, HG, R_tol); seeds = okn & (POSE[:, 1] == 0) & (st == 0)
    cn, stats = RM.flood(POSE, HG, okn, seeds, D, R_tol)
    ck = {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}
    res0 = list(B.res); drop = [i for i in tk if B.kind[i] == "ws" and (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])) not in ck]
    for i in drop: B.res[i] = None
    rc = B.report(); ntc = RM.near_touch(Mk, B); B.res = res0
    return dict(nodes=int(okn.sum()), connected=int(cn.sum()), islands=int((okn & ~cn).sum()), dropped=len(drop), dropped_idx=[int(i) for i in drop], **{k: rc[k] for k in KEYS},
                near=ntc["gap_near1"], ws_taken=sum(1 for i in tk if B.kind[i] == "ws") - len(drop), edges=stats)


def kin_nodes_model(D, Q, R_tol):
    """RM.kin_nodes with ONE fold reading = the model's: in state 2 (J3 on its dowel, J2 free, K free) the moving chain is the
    J1-K-J2 wrist, so the margin is the effective dyad's th margin m3e (+ the K dyad, held by stop B); the J1-K-J3 sub-chain
    margin (J2 rigid) is the state-1 reading and is kept for state 1 only"""
    u1, u2, u3 = D.u; uK = D.uK; ang, dmargin, PKm = RM.ang, RM.dmargin, PK
    q, ok, X1, X2, X3, s = D.ik(Q)
    st = D._state.copy(); K = D.knee(s); X1b = D._X1b[0]; m3e = np.asarray(D._m3e, float).copy()
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    j3 = np.einsum("nij,j->ni", X2[0], u3); j2 = np.einsum("nij,j->ni", X1b, u2); jK = np.einsum("nij,j->ni", X1[0], uK)
    th = ang(u1[None], j3); a1e = ang(u1[None], j2); a2e = ang(j2, j3); b1 = ang(u1[None], jK); cc = ang(jK, j3)
    fam = np.minimum(dmargin(th, b1, cc), dmargin(th, a1e, a2e))
    own = np.where(st == 2, dmargin(th, a1e, a2e), np.where(st != 0, fam, dmargin(th, D.a1, D.a2)))
    lo, hi = sorted(D.q2_stops); q2 = np.degrees(PKm.wrap(q[:, 1]))
    if not VDesign.STATE2_SLOT: q2ok = (q2 >= lo - 0.05) & (q2 <= hi + 0.05)
    else: q2ok = np.where(st == 2, True, (q2 >= lo - 0.05) & (q2 <= hi + 0.05))
    ok &= (own >= RM.M5 - 1e-6) & q2ok
    dKd = np.degrees(D._dK)
    qq = np.c_[np.degrees(q[:, :2]), np.degrees(q[:, 2] + K["phi"]), np.degrees(K["qa"]), np.degrees(K["qb"]), dKd]
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]; sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    return ok, qq, sgn, st, own


VDesign.STATE2_SLOT = False


def m_of_claim_fit(q3max):
    """the knee reference m of the claim's own cell-B fit (q3 reading) - used as m_fix so the q3' stop and the knee agree"""
    VDesign.OWN = False; P = FO.params({"q3max": q3max}); P.pop("_seed", None)
    M = FO.KModel(RM.PV.fast_bench(60, 160), dict(P)); M.run(); VDesign.OWN = True
    return [float(x) for x in M.D.m]


def law(B, q3max, own, fitB=None, mfix=None, conn=False):
    VDesign.OWN = own; P = FO.params({"q3max": q3max}); P.pop("_seed", None)
    if mfix is not None: P["m_fix"] = list(mfix); P["centre"] = 0
    fitB = fitB or RM.PV.fast_bench(60, 160); t0 = time.time()
    if B is fitB:
        Mk = FO.KModel(B, dict(P)); rk = Mk.run()
    else:
        Mk, fitr, M1, _ = RM.freeze(fitB, B, dict(P), FO.KModel); rk = Mk.run()
    nt = RM.near_touch(Mk, B); tk = taken(B)
    el = np.array([p_["elev"] for p_ in B.poses])
    out = dict(q3max=q3max, own=own, bench=B.mode, n=len(B.idx), **{k: rk[k] for k in KEYS}, near=nt["gap_near1"], near1_poses=nt["near1_poses"], min_mm=nt["min_mm"],
               ws_taken=sum(1 for i in tk if B.kind[i] == "ws"), why={k: int((Mk.why == k).sum()) for k in set(Mk.why.tolist()) if k},
               stop=stop_report(Mk, B), m=[round(float(x), 3) for x in Mk.D.m],
               overhead140=dict(ws=int(sum(1 for i in range(len(el)) if el[i] >= 140 and B.kind[i] == "ws")), taken=int(sum(1 for i in tk if el[i] >= 140 and B.kind[i] == "ws"))),
               binders={j: (round(min(float(np.min(B.res[j])), float(Mk.cmin.get(j, 1e9))), 2) if B.res[j] is not None else str(Mk.why[j])) for j in FO.BINDERS} if len(B.idx) == 470 else None)
    if conn:
        c = flood_connected(Mk, B, tk); out["connected"] = c
        out["overhead140"]["taken_connected"] = int(sum(1 for i in tk if el[i] >= 140 and B.kind[i] == "ws")) - sum(
            1 for i in tk if el[i] >= 140 and B.kind[i] == "ws" and B.res[i] is None)
    out["secs"] = round(time.time() - t0, 1)
    return out, Mk


if __name__ == "__main__":
    mode = sys.argv[1]; arg = json.loads(sys.argv[2]); outp = sys.argv[3]; extra = sys.argv[4] if len(sys.argv) > 4 else ""
    if mode == "diag":                                       # the claim's cell B as written (q3 reading), frozen exact Bench(110,360)
        B = CB.Bench(n_clip=110, n_ws=360); r, M = law(B, float(arg), own=False, conn=True)
    elif mode == "fit":                                      # q3' stop: fit-bench sweep (Bench(60,160) fast) like the proposer's rows 61-68
        fitB = RM.PV.fast_bench(60, 160); r = []
        for v in arg:
            mf = m_of_claim_fit(float(v))
            o, _ = law(fitB, float(v), own=True, fitB=fitB, mfix=mf); o["m_fix"] = mf; r.append(o)
            print(json.dumps({k: o[k] for k in ("q3max", "gap", "near", "reach", "contact", "ws_taken", "stop")}), flush=True)
            json.dump(r, open(outp, "w"), indent=1, default=float)
    elif mode == "dump":                                     # the claim's cell B as written (q3 reading, q3max 86): per-pose dump (lead's rule 2026-10-17)
        import alignment_paired as AP
        B = RM.PV.held_bench() if arg == "held" else CB.Bench(n_clip=110, n_ws=360)
        r, M = law(B, 86.0, own=False, conn=True); poses = AP._dump_bench(M, B)
        rp = os.path.join(REPO, "docs", "alignment", "remeasure", f"freek-oracle-route-knuckle-4r_{arg}_perpose.json")
        json.dump(dict(id="freek-oracle-route-knuckle-4r", wear=arg, params={"seed": "k33", "cell": "B", "q3max": 86}, report={k: r[k] for k in KEYS},
                       connected=r["connected"], poses=poses, recomputed=AP.gap_parts(poses), exact=os.environ.get("CB_EXACT") == "1",
                       note="cell B as claimed (stop on the model's q3 = cuff vs link 2; = J3 own angle q3' = q3 + phi, phi a function of q3 alone); "
                            "static per-pose; connected_dropped = ws poses the kinematic flood fill drops"), open(rp, "w"), default=float)
        r["dump"] = os.path.relpath(rp, REPO); r["recomputed"] = AP.gap_parts(poses)
    elif mode == "conn_model":                               # the claim's cell B, connected under ONE (the model's) fold reading
        RM.kin_nodes = kin_nodes_model
        B = RM.PV.held_bench() if arg == "held" else CB.Bench(n_clip=110, n_ws=360)
        r, M = law(B, 86.0, own=False, conn=True)
    elif mode == "wear":                                     # q3' stop, frozen on Bench(110,360) exact (or held out)
        B = RM.PV.held_bench() if extra == "held" else CB.Bench(n_clip=110, n_ws=360)
        mf = m_of_claim_fit(float(arg)); r, M = law(B, float(arg), own=True, mfix=mf, conn=True); r["m_fix"] = mf
    json.dump(r, open(outp, "w"), indent=1, default=float)
    print(json.dumps(r, default=float)[:3000])
