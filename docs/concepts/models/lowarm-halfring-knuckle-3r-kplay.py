"""Red team M5 for lowarm-halfring-knuckle-3r: what the hard pad's dwell K play does to METAL (not only to th).
Fit once (Bench(60,160) fast, nominal), freeze the shape, then wear the SAME frozen shape on Bench(110,360) exact with
K forced to law + delta on every DWELL pose (dK = 0): delta in {0, +play, -play}. Forced poses keep the law value (their
play is the parent's groove play, shared with the lead). The arm pose is the same; J1 / J2 / J3 re-solve (the wearer's arm
drives the chain; K sits wherever the play leaves it), so every body moves. Reports gap, takes, contacts, near-touch,
th margin with the play, and per-pose min metal-skin distance (named poses 139, 316, 203, 379).
usage: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-halfring-knuckle-3r-kplay.py <cellA|cellB> <play_deg> <out.json> [delta1,delta2,...]"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"
sys.path.insert(0, os.path.join(REPO, "tools"))
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
V = _load("lowarm_v_for_kplay", os.path.join(REPO, "docs/concepts/verify/lowarm-halfring-knuckle-3r.py"))
LM, DC, DS, S = V.LM, V.DC, V.DS, V.S
import concept_bench as CB
AP = _load("ap_for_kplay", os.path.join(REPO, "tools/alignment_paired.py"))
FLm = DS.FL; KRm = FLm.G.KR; Base = FLm.G.KR.KB.KDesign
unit = S.unit
PLAY = dict(delta=0.0, on=False, info={})

class PlayDesign(Base):
    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = super()._ik_phys(Q)
        P = self.p
        if not PLAY["on"] or "m_fix" not in P: return q, ok, X1, X2, X3, s
        dK0 = np.asarray(self._dK, float); n = len(Q)
        dw = np.asarray(ok, bool) & (np.abs(dK0) < 1e-9)
        PLAY["info"]["n_dwell"] = int(dw.sum())
        if not dw.any(): return q, ok, X1, X2, X3, s
        u1, u2, u3 = self.u; uK = self.uK; c3 = self.c[2]; m = V.KIT.FOLD_MARGIN
        sp = float(np.sign(self.psiA)) or 1.0
        idx = np.nonzero(dw)[0]; Qs = Q[idx]; ns = len(idx)
        w = Qs @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        dK = np.full(ns, sp * math.radians(PLAY["delta"]))
        RK = S.rotm(uK, dK)
        u1p = np.einsum("nji,j->ni", RK, u1)                 # RK^T u1
        a23 = float(u2 @ u3); c = u1p @ u2
        A = u1p @ u3 - c * a23; Bs = u1p @ np.cross(u2, u3); C = c * a23
        R = np.hypot(A, Bs); q0 = np.arctan2(Bs, A); x = (np.cos(np.radians(th)) - C) / np.maximum(R, 1e-12)
        g = np.arccos(np.clip(x, -1, 1)); q2old = q[idx, 1]
        cands = np.stack([q0 + g, q0 - g], 1)
        dd = np.abs(np.angle(np.exp(1j * (cands - q2old[:, None])))); q2s = cands[np.arange(ns), np.argmin(dd, 1)]
        q2s = q2old + np.angle(np.exp(1j * (q2s - q2old)))
        rootok = np.abs(x) <= 1 + 1e-12
        Rq = S.rotm(u2, q2s); p = Rq @ u3
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w)
        R1 = S.rotm(u1, q1); R12 = R1 @ RK @ Rq; vv = KRm.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (ns, 3)), np.einsum("nji,njk,k->ni", R12, Qs, vv))
        R3 = S.rotm(u3, q3); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        m3e = KRm.dyad_margin(th, a1e, self.a2)
        # self-check at delta = 0: the re-solve must reproduce the model's own dwell IK
        if abs(PLAY["delta"]) < 1e-12:
            PLAY["info"]["selfcheck_q_maxdiff_deg"] = float(np.degrees(np.max(np.abs(np.angle(np.exp(1j * (np.stack([q1, q2s, q3], 1) - q[idx])))))))
        okn = rootok & (m3e >= m - 1e-6)
        q = np.array(q, float); ok = np.array(ok, bool)
        q[idx] = np.stack([q1, q2s, q3], 1); ok[idx] = ok[idx] & okn
        R1m = np.array(X1[0]); R1m[idx] = R1
        R2m = np.array(X2[0]); R2m[idx] = R12
        R3m = np.array(X3[0]); t3m = np.array(X3[1]); R3m[idx] = R123; t3m[idx] = t3
        X1 = (R1m, X1[1]); X2 = (R2m, X2[1]); X3 = (R3m, t3m)
        sv = np.einsum("nji,nj->ni", Qs, t3); s = np.array(s, float); s[idx] = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        X1b0 = np.array(self._X1b[0]); X1b0[idx] = R1 @ RK; self._X1b = (X1b0, self._X1b[1])
        self._dK = np.array(self._dK, float); self._dK[idx] = dK
        self._a1e = np.array(self._a1e, float); self._a1e[idx] = a1e
        self._m3e = np.array(self._m3e, float); self._m3e[idx] = m3e
        PLAY["info"].update(n_dwell_lost_fold=int((~okn).sum()), m3e_min_dwell=round(float(m3e.min()), 3))
        PLAY["dwell_idx"] = idx
        return q, ok, X1, X2, X3, s

FLm.G.KR.KB.KDesign = PlayDesign

NAMED = [139, 316, 203, 379, 205, 237, 264]

def main():
    cell, play, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    P = dict(LM.CELL_A) if cell == "cellA" else dict(V.BEST)
    if cell == "cellB": P = dict(LM.CELL_B, **V.BEST)
    P = DS._clamp(dict(DS.PARAMS, **P))
    t0 = time.time()
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = DS.DSModel(B1, dict(P)); r1 = M1.run()
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    class Frozen(DS.DSModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_desmo"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    B = CB.Bench(n_clip=110, n_ws=360)
    lw = ((getattr(M1, "_sc_info", None) or {}).get("desmo") or {}).get("lowarm") or getattr(M1, "_lowarm", None) or {}
    out = dict(cell=cell, params=P, fit_fast={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
               dwell_K_play_model=(lw.get("dwell_K_play") or {}), mode=B.mode, runs={})
    for d in ([float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else (0.0, play, -play)):
        PLAY.update(delta=d, on=True, info={}); t = time.time()
        M = Frozen(B, dict(P2)); r = M.run()
        rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        poses = AP._dump_bench(M, B); tk = V.taken_of(B)
        try: thm = V.th_margin(M, B, tk)
        except Exception as e: thm = dict(error=repr(e)[:200])
        try: au = DS.PK.audit(M, B)
        except Exception as e: au = dict(error=repr(e)[:200])
        ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
        mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
        ov = ws & (elev >= 140)
        dwi = set(int(i) for i in PLAY.get("dwell_idx", []))
        out["runs"][f"{d:+.3f}"] = dict(delta=d, report=rep, why=r.get("why"), recomputed=AP.gap_parts(poses),
            overhead=f"{int((ov & (mins >= 0)).sum())}/{int(ov.sum())}", near1=au.get("gap_near1"), near2=au.get("gap_near2"),
            minmetal=au.get("near_touch_min_mm"), near_low=au.get("near_touch_low"), cmin_named={int(j): (None if j not in (getattr(M, "cmin", {}) or {}) else round(float(M.cmin[j]), 3)) for j in NAMED}, th=thm, play_info=dict(PLAY["info"]),
            contacts=[dict(i=int(j), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"], axial=B.poses[j]["axial"], mm=round(float(mins[j]), 3), dwell=j in dwi)
                      for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0],
            named={int(j): dict(min_mm=None if not np.isfinite(mins[j]) else round(float(mins[j]), 3), dwell=j in dwi,
                                 pose=dict(plane=B.poses[j]["plane"], elev=B.poses[j]["elev"], axial=B.poses[j]["axial"])) for j in NAMED},
            per_pose_min=[None if not np.isfinite(x) else round(float(x), 3) for x in mins], dwell_idx=sorted(dwi),
            secs=round(time.time() - t, 1))
        rr = out["runs"][f"{d:+.3f}"]
        print(json.dumps(dict(delta=d, report=rep, why=rr["why"], overhead=rr["overhead"], near1=rr["near1"], minmetal=rr["minmetal"], near_low=rr["near_low"],
                              th_min=(thm or {}).get("min"), info=rr["play_info"], ncontact=len(rr["contacts"]),
                              named={k: v["min_mm"] for k, v in rr["named"].items()}, secs=rr["secs"]), default=float), flush=True)
        json.dump(out, open(outp, "w"), indent=1, default=float)
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)

if __name__ == "__main__":
    main()
