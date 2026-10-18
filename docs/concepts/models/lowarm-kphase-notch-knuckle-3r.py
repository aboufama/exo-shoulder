"""lowarm-kphase-notch-knuckle-3r (round 15, lens C pick 4): lowarm-kstop-knuckle-3r's chain (imported UNCHANGED through its
own harness: stage 1 at F+3.9, K-own set-screw stop A, pad deleted, sided dwell wears, J2 dowel at K-eq 46.35) with
  (1) the stage-2 pair phased toward hub 2: beta -177.169 -> BETA (the nose boss on link 1a and the crank's slot plate
      re-synthesised by the chain's own model at r_c 16.18, g 2.393),
  (2) a SECTOR NOTCH in hub K's O20 housing where the phased slot plate crosses it: hub K's solid = cylinder r 10 x
      F..F+12.25 MINUS the annular sector {r >= 10 - n, az in [a0, a1] about uK in the owning body's frame, z in [z0, z1]
      over F_K}, as a CSG difference max(sd_cyl, -sd_notch) (conservative outside, exact inside). Used in the PLATE-hubK
      stroke gate (desmo-conecut _desmo_build_B) AND in every per-pose collide check (ROD / CRK / HORN vs hub K).
  (3) hub-2 / ring2 flats (conecut-h2facet's planar flat) - step 2, only after gate 0.
3 ACTIVE DOF (J1, J2, J3); K slaved, never read; crank pivot + knee pins passive rotations; 0 passive translations; no
spring / gear / pulley / cable (MVP1). Complexity 16.75 (kstop's; machined cuts on existing parts add 0).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-kphase-notch-knuckle-3r.py probe '<json sets>' <out.json>
        fast fit Bench(60,160) with the PLATE-hubK gate bypassed (true value recorded) + the plate footprint in hub K's frames
    CB_EXACT=1 ... guard '<json sets>' <out.json>   fast fit, frozen, exact wear on the guard poses (per part)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
ID = "lowarm-kphase-notch-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KS = _load("kstop_for_kphase", os.path.join(HERE, "lowarm-kstop-knuckle-3r.py"))
GUARD = (139, 203, 205, 237, 264, 316)
# notch: n depth (mm), [a0, a1] az (deg) about uK in the owning body's frame (e = unit(uK x [0.3, 0.5, 0.8]), f = uK x e),
# [z0, z1] over F_K; body 'K' = hub K's own member (cyl['hubK'][0]); bypass = gate value recorded and ignored (probe only)
NOTCH = dict(on=False, n=0.0, a0=0.0, a1=0.0, z0=0.0, z1=0.0, bypass=False)
REC = dict(plateK=[], gate_calls=0, pose_calls=0)
HUB_R, CROWN = 10.0, 12.25
GRV_R, GRV_Z = (6.45, 8.55), (3.15, 4.75)                  # kstop's stop-A groove (link 1b boss)


def frame(ax):
    e = np.cross(ax, [0.3, 0.5, 0.8]); e = e / np.linalg.norm(e); return e, np.cross(ax, e)


def sd_notch(Pw, cen, ax, e):
    """signed distance to the notch volume (annular sector, open outward: r_hi = 10 + 5)"""
    f = np.cross(ax, e); w = Pw - cen; z = w @ ax; rv = w - z[:, None] * ax; rr = np.linalg.norm(rv, axis=1)
    az = np.degrees(np.arctan2(rv @ f, rv @ e))
    a0, a1 = NOTCH["a0"], NOTCH["a1"]; mid = 0.5 * (a0 + a1); hw = 0.5 * (a1 - a0)
    da = np.abs((az - mid + 180.0) % 360.0 - 180.0) - hw                          # deg outside the sector (<0 inside)
    dang = np.where(da > 0, rr * np.sin(np.radians(np.minimum(da, 90.0))), -rr * np.sin(np.radians(np.minimum(-da, 90.0))))
    d = np.maximum.reduce([(HUB_R - NOTCH["n"]) - rr, rr - (HUB_R + 5.0), NOTCH["z0"] - z, z - NOTCH["z1"], dang])
    return d


def _patch(LM):
    C = LM.LHModel
    own_sd = [c for c in C.__mro__ if "sd_cyl" in c.__dict__][0]
    if getattr(own_sd, "_kphase_patched", False): return
    orig = own_sd.__dict__["sd_cyl"]

    def sd_cyl(self, Pw, cen, ax, r=None):
        v = orig(self, Pw, cen, ax, r)
        cyl = getattr(self, "cyl", None) or {}
        if "hubK" not in cyl or r is None or abs(float(r) - float(self.cyl_r.get("hubK", -1))) > 1e-9: return v
        memK, cK, aK = cyl["hubK"]; eK, _ = frame(np.asarray(aK, float))
        fr = sys._getframe(1).f_locals
        if "XP" in fr and "plateC" in fr and np.allclose(cen, cK, atol=1e-9):          # the PLATE-hubK stroke gate (link 1b frame)
            REC["gate_calls"] += 1
            if NOTCH["bypass"]:
                REC["plateK"].append(float(np.min(v)))
                sel = np.asarray(v, float) < 1.0
                if sel.any():
                    e_, f_ = frame(np.asarray(aK, float)); w = np.asarray(Pw, float)[sel] - cen; z = w @ ax; rv = w - z[:, None] * ax
                    REC.setdefault("viol", []).append(np.c_[np.linalg.norm(rv, axis=1), np.degrees(np.arctan2(rv @ f_, rv @ e_)), z,
                                                           np.full(int(sel.sum()), float(np.degrees(fr["kgrid"][fr["j"]])) if "kgrid" in fr else -1.0)])
                return np.full_like(np.asarray(v, float), 99.0)
            if not NOTCH["on"]: return v
            return np.maximum(v, -sd_notch(Pw, cen, ax, eK))                          # the gate runs in link 1b's frame = the notch's body
        i = getattr(self, "_kph_pose", None)
        if i is None or not NOTCH["on"]: return v
        R, t = self.T(memK, i)
        if not (np.allclose(cen, R @ cK + t, atol=1e-6) and np.allclose(ax, R @ aK, atol=1e-6)): return v
        REC["pose_calls"] += 1
        Rb, _ = self.T(self.link_pts["L1b"][0], i)                                     # the notch is cut in link 1b's boss
        return np.maximum(v, -sd_notch(Pw, cen, ax, Rb @ eK))

    own_sd.sd_cyl = sd_cyl
    own_sd._kphase_patched = True
    own_c = [c for c in C.__mro__ if "collide" in c.__dict__][0]
    origc = own_c.__dict__["collide"]

    def collide(self, i):
        self._kph_pose = i
        try: return origc(self, i)
        finally: self._kph_pose = None

    own_c.collide = collide
    orig_rm = C._rod_metal

    def _rod_metal(self):
        orig_rm(self)
        if NOTCH["on"] and NOTCH["n"] > 0: notch_samples(self)

    C._rod_metal = _rod_metal


_ADDED = []


def notch_samples(M):
    """hub K's samples in the notch band move to link 1b (the upper member owns hub K's O20 above F+3.15: kstop's stop-A
    stack); rigid (in-band) samples inside the notch are projected radially onto the notch face (equal count); contact
    samples inside it are dropped and a dense notch solid (face r = 10 - n, side walls at a0 / a1, floor z0, ceiling z1,
    0.5 mm / 1 deg) is added on link 1b. A cut only removes metal; part-vs-part checks use the CSG solid (sd_cyl patch)."""
    memK, cK, aK = M.cyl["hubK"]; cK = np.asarray(cK, float); aK = np.asarray(aK, float); e, f = frame(aK); mLb = M.link_pts["L1b"][0]
    n, a0, a1, z0, z1 = NOTCH["n"], NOTCH["a0"], NOTCH["a1"], NOTCH["z0"], NOTCH["z1"]; rN = HUB_R - n
    def cyl(X):
        w = X - cK; z = w @ aK; rv = w - z[:, None] * aK; return np.linalg.norm(rv, axis=1), np.degrees(np.arctan2(rv @ f, rv @ e)), z
    def xyz(r, az, z):
        a = np.radians(az); return cK + np.outer(z, aK) + (r * np.cos(a))[:, None] * e + (r * np.sin(a))[:, None] * f
    def inside(r, az, z): return (r > rN + 1e-6) & (r <= HUB_R + 0.05) & (az >= a0) & (az <= a1) & (z >= z0) & (z <= z1)
    info = dict(n=n, a0=a0, a1=a1, z0=z0, z1=z1, rigid_projected=0, contact_dropped=0)
    for key in [k for k, (m, X) in M.rigid.items() if m == memK and k.lower().startswith("hubk")]:
        m, X = M.rigid[key]; X = np.asarray(X, float); r, az, z = cyl(X); ins = inside(r, az, z)
        if ins.any():
            Y = X.copy(); Y[ins] = xyz(np.full(int(ins.sum()), rN), az[ins], z[ins]); M.rigid[key] = (m, Y); info["rigid_projected"] += int(ins.sum())
    if any(any(X is A for A in _ADDED) for _, X in M.contact): M._kph_notch = info; return info
    new = []
    for m, X in M.contact:
        if m != memK or not len(X): new.append((m, X)); continue
        X = np.asarray(X, float); r, az, z = cyl(X); ins = inside(r, az, z) & (r <= HUB_R + 0.05)
        info["contact_dropped"] += int(ins.sum()); new.append((m, X[~ins]) if ins.any() else (m, X))
    zt = min(z1, CROWN); zz = np.unique(np.r_[np.arange(z0, zt + 1e-9, 0.5), zt]); aa = np.unique(np.r_[np.arange(a0, a1 + 1e-9, 1.0), a1]); rr = np.unique(np.r_[np.arange(rN, HUB_R + 1e-9, 0.5), HUB_R])
    A, Z = np.meshgrid(aa, zz); face = xyz(np.full(A.size, rN), A.ravel(), Z.ravel())
    sides = [xyz(R_.ravel(), np.full(R_.size, ae), Z_.ravel()) for ae in (a0, a1) for R_, Z_ in [np.meshgrid(rr, zz)]]
    caps = [xyz(R_.ravel(), A_.ravel(), np.full(R_.size, zc)) for zc in (z0, z1) if zc < CROWN - 1e-9 for R_, A_ in [np.meshgrid(rr, aa)]]
    sol = np.concatenate([face] + sides + caps); _ADDED.append(sol); new.append((mLb, sol))
    M.contact = new; info["solid_n"] = int(len(sol)); info["wall_over_MR117_mm"] = round(rN - 5.5, 3)
    info["wall_to_stopA_groove_mm"] = round(z0 - GRV_Z[1], 3) if (rN < GRV_R[1]) else None
    M._kph_notch = info
    return info


_H0 = KS._harness


def _harness():
    out = _H0(); _patch(out[2]); return out


KS._harness = _harness


def fit_fast(sets):
    T, V, LM, DS, S, PLAY = _harness(); PLAY.update(on=False)
    P = KS.params(T, LM, sets)
    os.environ.pop("CB_EXACT", None)
    B1 = V.CB.Bench(n_clip=60, n_ws=160)
    REC["plateK"] = []
    r1, M = LM._report_dc(B1, dict(P))
    return T, V, LM, DS, S, P, r1, M


def footprint(M, S):
    """the crank's plate (body 9: rigid 'plate' + ROD strap) in hub K's body frame and in link 1b's frame over the fit poses:
    samples within r <= 11.5 of uK, with z over F_K and az about uK"""
    memK, cK, aK = M.cyl["hubK"]; cK = np.asarray(cK, float); aK = np.asarray(aK, float); e, f = frame(aK)
    mLb = M.link_pts["L1b"][0]; mLa = M.link_pts["L1a"][0] if "L1a" in M.link_pts else None
    X9 = np.concatenate([np.asarray(M.rigid["plate"][1], float).reshape(-1, 3), np.asarray(M.strap["ROD"][1], float).reshape(-1, 3)])
    dK = np.degrees(np.abs(np.asarray(M.dK, float))); out = {}
    for nm, mb in (("hubK_body", memK), ("L1b", mLb)) + ((("L1a", mLa),) if mLa is not None and mLa != memK else ()):
        rows = []
        for i in np.nonzero(np.asarray(M.kin_ok, bool))[0]:
            R9, t9 = M.T(9, i); Rb, tb = M.T(mb, i); RK, tK = M.T(memK, i)
            Xw = X9 @ R9.T + t9
            cw = RK @ cK + tK; aw = RK @ aK                                  # hub K axis in world
            Xb = (Xw - tb) @ Rb; cb = (cw - tb) @ Rb; ab = aw @ Rb           # into body mb's frame
            eb = Rb.T @ (RK @ e) if mb == memK else e                        # reference az = hub K body's e (rest) in mb
            if mb != memK: eb = e                                            # mb's own rest-frame reference
            fb = np.cross(ab, eb)
            w = Xb - cb; z = w @ ab; rv = w - z[:, None] * ab; rr = np.linalg.norm(rv, axis=1); az = np.degrees(np.arctan2(rv @ fb, rv @ eb))
            sel = (rr <= 11.5) & (z > -1.0) & (z < CROWN + 1.0)
            for a_, r_, z_ in zip(az[sel], rr[sel], z[sel]): rows.append((float(a_), float(r_), float(z_), float(dK[i]), int(i)))
        if rows:
            A = np.array(rows); dw = A[A[:, 3] < 1.0]
            out[nm] = dict(n=len(A), az=[round(float(A[:, 0].min()), 1), round(float(A[:, 0].max()), 1)], r_min=round(float(A[:, 1].min()), 2),
                           z=[round(float(A[:, 2].min()), 2), round(float(A[:, 2].max()), 2)], K=[round(float(A[:, 3].min()), 1), round(float(A[:, 3].max()), 1)],
                           dwell=None if not len(dw) else dict(n=len(dw), az=[round(float(dw[:, 0].min()), 1), round(float(dw[:, 0].max()), 1)],
                                                                r_min=round(float(dw[:, 1].min()), 2), z=[round(float(dw[:, 2].min()), 2), round(float(dw[:, 2].max()), 2)]),
                           in_r10=None if not (A[:, 1] < HUB_R).any() else dict(n=int((A[:, 1] < HUB_R).sum()),
                               az=[round(float(A[A[:, 1] < HUB_R, 0].min()), 1), round(float(A[A[:, 1] < HUB_R, 0].max()), 1)],
                               z=[round(float(A[A[:, 1] < HUB_R, 2].min()), 2), round(float(A[A[:, 1] < HUB_R, 2].max()), 2)],
                               K=[round(float(A[A[:, 1] < HUB_R, 3].min()), 1), round(float(A[A[:, 1] < HUB_R, 3].max()), 1)]))
        else:
            out[nm] = dict(n=0)
    out["members"] = dict(memK=int(memK), L1b=int(mLb), L1a=None if mLa is None else int(mLa), crank=9)
    return out


def _info(M):
    si = getattr(M, "_sc_info", None) or {}; ds = si.get("desmo") or {}; s2 = ds.get("stage2B") or {}; sl = (ds.get("slop") or {}).get("slotB") or {}
    return dict(dK_lim=si.get("dK_lim"), why_lim=si.get("why_lim"), pa=(si.get("pa_crank_max_taken"), si.get("pa_horn_max_taken"), si.get("pa_eff_horn")),
                arc=si.get("arc_deg"), arm_len=si.get("arm_len"), contact_r=si.get("contact_r"), plate_len=s2.get("plate_len_mm"),
                clear_plate_hubK=s2.get("clear_plate_hubK"), clear_plate_hub2=s2.get("clear_plate_hub2"),
                pocket=(sl.get("pocket_pa_max_horn"), sl.get("pocket_pa_max_crank"), sl.get("pocket_pa_fail_K0")), slop=sl.get("slop_max"),
                lim_pa_by_mu=s2.get("dK_lim_pa_by_mu"), desmo_fail=list(getattr(M, "_desmo_fail", []) or []))


def probe(sets, outp, notch=None):
    if notch: NOTCH.update(notch)
    t = time.time()
    T, V, LM, DS, S, P, r1, M = fit_fast(sets)
    out = dict(sets=sets, notch=dict(NOTCH), fit={k: r1.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1")},
               info=_info(M), plateK_true_min=round(min(REC["plateK"]), 3) if REC["plateK"] else None, rec=dict(gate_calls=REC["gate_calls"], pose_calls=REC["pose_calls"]),
               footprint=footprint(M, S), secs=round(time.time() - t, 1))
    if REC.get("viol"):
        A = np.concatenate(REC["viol"]); out["gate_viol"] = dict(n=len(A), r_min=round(float(A[:, 0].min()), 3), az=[round(float(A[:, 1].min()), 1), round(float(A[:, 1].max()), 1)],
                                                                z=[round(float(A[:, 2].min()), 2), round(float(A[:, 2].max()), 2)], K=[round(float(A[:, 3].min()), 2), round(float(A[:, 3].max()), 2)])
        REC["viol"] = []
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps(out, default=float), flush=True)
    return out


def guard(sets, outp, notch=None):
    """fast fit -> frozen -> exact wear on the guard poses only (reduced Bench(110,360)); per-part minima like the judge's scans"""
    if notch: NOTCH.update(notch)
    T, V, LM, DS, S, PLAY = _harness()
    delta = sets.pop("delta", None)
    if delta is None: PLAY.update(on=False)
    else: PLAY.update(delta=float(delta), on=True, info={})
    CB = V.CB; _B0 = CB.Bench; KEEP = list(GUARD)

    class RB(_B0):
        def __init__(self, n_clip=110, n_ws=360, seed=0):
            super().__init__(n_clip, n_ws, seed)
            if (n_clip, n_ws) == (110, 360):
                kk = np.asarray(KEEP, int); self.idx = self.idx[kk]; self.kind = [self.kind[j] for j in kk]; self.clip = [self.clip[j] for j in kk]
                self.poses = [self.poses[j] for j in kk]; self.res = [None] * len(kk)
    CB.Bench = RB
    try:
        P = KS.params(T, LM, sets); t = time.time()
        os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
        fit, M1, M, B, r = LM.DS._frozen_model(dict(P), 110, 360)
    finally:
        CB.Bench = _B0; os.environ.pop("CB_EXACT", None)
    mem = {}
    for nm, (m, X) in M.rigid.items(): mem.setdefault(m, []).append(nm)
    sets_ = [("r:" + nm, m, X) for nm, (m, X) in M.rigid.items()] + [("L:" + nm, m, X) for nm, (m, X) in M.link_pts.items()] + \
            [("c%d:%s" % (ci, "/".join(mem.get(m, ["?"]))), m, X) for ci, (m, X) in enumerate(M.contact)]
    per = {}; dK = np.degrees(np.abs(np.asarray(M.dK, float)))
    for j, gi in enumerate(KEEP):
        if not M.kin_ok[j]: per[gi] = dict(why=str(M.why[j])); continue
        worst = []
        for nm, m, X in sets_:
            if len(X):
                d = float(B.dist(j, M.world(m, j, X)).min())
                if d < 0.8: worst.append((round(d, 3), nm))
        per[gi] = dict(dK=round(float(dK[j]), 2), taken=B.res[j] is not None and float(np.min(B.res[j])) >= 0, why=str(M.why[j]) if hasattr(M, "why") else None,
                       parts=sorted(worst)[:8])
    out = dict(sets=sets, delta=delta, notch=dict(NOTCH), fit={k: fit[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, info=_info(M1),
               notch_samples=getattr(M1, "_kph_notch", None), per=per, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps(out, default=float), flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    sets = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    notch = sets.pop("notch", None)
    if mode == "probe": probe(sets, sys.argv[3], notch)
    elif mode == "guard": guard(sets, sys.argv[3], notch)
