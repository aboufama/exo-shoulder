"""kfree-o20pin-highexit-relay-4r (round 401 K1, judge pick 3, lens B; the steered stop cell merged): the plain knee-less
O20 3R at the lead's J1 / J2 seats (K WELDED, drive stripped, knee-side samples dropped), J3 on a GH ray at the champion
seat wdir(77.25, -8.2) with b3 0, and member 3 (hub 3's lower plate + one bent 10 x 3 Ti bar) swinging on a FOURTH
O20 v5 stack R4 whose axis is the GH-through line wdir(55, 45) (= armarc raxis(55, 45) = kit relay_axis(55, -135):
the same line). R4's lower plate is carried by BOTTOM through a 10 x 3 Ti lug. R4 is the counted 4th revolute, one-sided
[0, PHI] (clock spring to a zero dowel, PHI dowel on R4's own angle): least-phi physics (the arm turns member 3 only
when the plain dyad leaves its welded window, to the least phi at which every gate passes, the J2 / J3 own-angle dowels
INSIDE the gate - the steering is the solve's, not a clamp after it).

STEP 0 (the judge's pre-registered gate: ideal bound > 14.0 kills; hardware > 17.0 kills): the IDEAL bound = the
lead-quality chain through insertion-cband-relay-4r.py's ideal path (kfree lead_eval, frozen protocol, J3 seat asserted
in M1.p, knee-less readings) with the relay about raxis(55, 45) and NO R4 / bar / lug metal.
STEP 1 (hw 1): R4 / bar / lug as sampled metal on the same frozen wear:
  * boss  = the R4 O20 stack: FLAT underside disc r 10 normal to the line at rB = the q_boss quantile (1.0) over the fit
            poses of the height along the line at which every disc point (centre + rims r 5 / 10) clears the skin by
            `standoff` (the spec's 'max exit + 2 mm', read on the disc, not only the axis), + the side wall (r 10) at
            F + 1 and F + 6; rotation-invariant about the line (lug half and member-3 half are coaxial); in-band;
  * bar   = member 3's bent 10 x 3 Ti bar on the great circle hub 3 -> the line (member-3 frame = relayed HG), underside
            at the q_bar requirement along GH rays over the fit poses (relayed), 10 mm ramps into hub 3's lower plate
            and R4's crown plate (rB + 12.25 - 3); in-band;
  * lug   = BOTTOM's 10 x 3 Ti lug on the great circle BOTTOM's bar top (K.BAR0_H) -> the line (arm frame, unrelayed),
            underside at the q_lug requirement, ramps into BOTTOM's bar top and R4's lower plate; CONTACT ONLY (like a
            cuff shell: it is part of BOTTOM);
  * jams  = bar / boss vs hub 1, hub 2, hub K, link 1a / 1b, link 2 < 1 mm, lug vs those + hub 3 < 1 mm, lug vs bar < 1 mm
            outside the R4 stack (r > 13 mm from the line): a jammed pose is lost.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/kfree-o20pin-highexit-relay-4r.py run '<json>' envsel|b110|fast [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("icb_for_o20pin", os.path.join(HERE, "insertion-cband-relay-4r.py"))
ICB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(ICB)
K, CB, KF, EB = ICB.K, ICB.CB, ICB.KF, ICB.EB

ID = "kfree-o20pin-highexit-relay-4r"
NAME = "O20 axis-exit pin relay at the high anterolateral exit: knee-less O20 3R + R4 on the GH-through line wdir(55, 45)"
BASE = dict(PHI=75.0, tilt=55.0, taz=45.0, sgn=1.0, hw=0, drive=0, wd=77.25, wa=-8.2, b3=0.0, psi2=-14.0)
HW = dict(standoff=2.0, q_boss=1.0, boss_r=10.0, stack=12.25, bar_w=10.0, bar_t=3.0, q_bar=1.0, lug_w=10.0, lug_t=3.0, q_lug=1.0,
          clr=2.0, step=2.0, out_mm=15.0, bar_low=0)
D2R = math.pi / 180


def _basis(ax):
    a = K.unit(np.cross(ax, [0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0.0, 0.0])); return a, np.cross(ax, a)


def _arc(u0, u1, w, st, r_ref):
    """great-circle strap directions u0 -> u1 (unit, HG-type frame), width w: (n, 3) dirs and their arc fraction s"""
    ang = math.acos(float(np.clip(u0 @ u1, -1, 1))); n_ = K.unit(np.cross(u0, u1)); e2 = K.unit(np.cross(n_, u0))
    L = ang * r_ref; ns = max(3, int(L / st) + 1); tt = np.linspace(0, 1, ns); ww = np.arange(-w / 2, w / 2 + 1e-6, st) / r_ref
    D, S = [], []
    for t_ in tt:
        c = math.cos(t_ * ang) * u0 + math.sin(t_ * ang) * e2
        for x in ww: D.append(K.unit(c * math.cos(x) + n_ * math.sin(x))); S.append(t_)
    return np.array(D), np.array(S), L


def _fitted(B1, Rw, poses, D, clr, q, out_mm):
    I = np.repeat(poses, len(D)); Dw = np.einsum("pij,nj->pni", Rw, D).reshape(-1, 3)
    t = K.requirement(B1, I, Dw, clr=clr).reshape(len(poses), len(D)); t = np.where(np.isfinite(t), t, np.nan)
    med = np.nanmedian(t, 0); t = np.where(t <= med[None, :] + out_mm, t, np.nan)     # rays that meet the torso / forearm first
    return np.nanmax(t, 0) if q >= 1 else np.nanquantile(t, q, 0)


def r4_geometry(AR, M1, B1, phi, ax, h):
    """R4 boss (line frame: rotation-invariant), bar (member-3 frame), lug (arm frame), fitted on the fit bench poses
    that close (Bench(60,160) fast, the lead's own fit set)"""
    F1 = K.frames(B1); phi1 = phi[B1.idx]; fit = np.nonzero(np.isfinite(phi1))[0]; R1 = AR.rotm(ax, np.nan_to_num(phi1) * D2R)
    st = float(h["step"]); rb = float(h["boss_r"])
    ax = -np.asarray(ax, float)                  # the relay vector raxis(55, 45) points up the arm into the trunk; R4 sits where the
    e, f = _basis(ax)                            # SAME line leaves the anterolateral arm, along -raxis = wdir(55, 45)
    # boss underside height along the line: every disc point (centre + rims r 5 / 10, 12 az) clears skin by standoff
    O = [np.zeros(3)] + [r * (math.cos(t) * e + math.sin(t) * f) for r in (5.0, rb) for t in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
    O = np.array(O); I = np.repeat(fit, len(O)); Rw = F1.RHG[fit]
    Dw = np.repeat((Rw @ ax)[:, None, :], len(O), 1).reshape(-1, 3); Ow = np.einsum("pij,nj->pni", Rw, O).reshape(-1, 3)
    t = K.requirement(B1, I, Dw, clr=float(h["standoff"]), O=Ow).reshape(len(fit), len(O)); t = np.where(np.isfinite(t), t, np.nan)
    tq = np.nanmax(t, 0) if float(h["q_boss"]) >= 1 else np.nanquantile(t, float(h["q_boss"]), 0)
    rB = float(np.nanmax(tq)); exit_axis = t[:, 0] - float(h["standoff"])
    disc = np.array([rB * ax + x * e + y * f for x, y in K.disc_xy(rb, st)])
    wall = np.array([(rB + z) * ax + rb * (math.cos(a) * e + math.sin(a) * f) for z in (1.0, 6.0) for a in np.linspace(0, 2 * math.pi, 32, endpoint=False)])
    boss = np.r_[disc, wall]
    # hub 3 centre in the member-3 (relayed HG) frame (the lead's fitted hub-3 samples at a phi-0 fit pose)
    j0 = int(fit[np.argmin(np.abs(phi1[fit]))]); m3, X3 = M1.rigid["hub3"]
    W3 = M1.world(m3, j0, X3); h3 = (np.linalg.inv(F1.RHG[j0] @ R1[j0]) @ np.asarray(W3).T).T.mean(0)
    # bar: hub 3 -> the line, member-3 frame
    D, S, L = _arc(K.unit(h3), ax, float(h["bar_w"]), st, 0.5 * (np.linalg.norm(h3) + rB))
    rq = _fitted(B1, np.einsum("pij,pjk->pik", F1.RHG[fit], R1[fit]), fit, D, float(h["clr"]), float(h["q_bar"]), float(h["out_mm"]))
    lowbar = int(h.get("bar_low", 0))           # 1: the bar joins R4's LOWER plate (underside at F = rB) and the lug its crown plate
    r0, r1 = float(np.linalg.norm(h3)) - 6.125, (rB if lowbar else rB + float(h["stack"]) - float(h["bar_t"]))
    bl = np.clip(np.minimum(S * L, (1 - S) * L) / 10.0, 0, 1); rl = r0 + (r1 - r0) * S
    rS = np.where(np.isfinite(rq), bl * np.maximum(rq, 0) + (1 - bl) * rl, rl); bar = D * rS[:, None]
    # lug: BOTTOM's bar top (H frame BAR0_H, per pose C = RHG^T RH) -> the line, arm frame (unrelayed)
    C = np.einsum("pji,pjk->pik", F1.RHG[fit], F1.RH[fit]); c0 = K.unit(np.median(K.unit(C @ K.unit(K.BAR0_H)), 0))
    rc = float(np.linalg.norm(K.BAR0_H))
    Dl, Sl, Ll = _arc(c0, ax, float(h["lug_w"]), st, 0.5 * (rc + rB))
    rql = _fitted(B1, F1.RHG[fit], fit, Dl, float(h["clr"]), float(h["q_lug"]), float(h["out_mm"]))
    l1 = rB + float(h["stack"]) - 3.0 if lowbar else rB   # lug underside at R4's other plate; the first 12 mm from BOTTOM's bar top are BOTTOM's own boss (dropped, not
    bll = np.clip((1 - Sl) * Ll / 10.0, 0, 1)    # lug metal); the rest sits at its fitted requirement, ramping into R4's lower plate
    rqf = np.where(np.isfinite(rql), np.maximum(rql, 0), np.nanmax(rql)); rL = bll * rqf + (1 - bll) * np.maximum(l1, rqf)
    keep = Sl * Ll >= 12.0; lug = (Dl * rL[:, None])[keep]; rL = rL[keep]
    exf = exit_axis[np.isfinite(exit_axis)]
    return dict(boss=boss, bar=bar, lug=lug, rB=round(rB, 2), exit_axis_min_p50_max=[round(float(np.min(exf)), 1), round(float(np.median(exf)), 1), round(float(np.max(exf)), 1)],
                bar_len_mm=round(L, 1), lug_len_mm=round(Ll, 1), hub3=[round(float(x), 1) for x in h3], hub3_r=round(float(np.linalg.norm(h3)), 1),
                bar_r=[round(float(np.min(rS)), 1), round(float(np.median(rS)), 1), round(float(np.max(rS)), 1)],
                lug_r=[round(float(np.min(rL)), 1), round(float(np.median(rL)), 1), round(float(np.max(rL)), 1)],
                n=dict(boss=len(boss), bar=len(bar), lug=len(lug)), obliquity_deg=None)


def r4_wear(AR, M, B, G, phi_b, ax):
    """exact distance of every R4 sample per pose; jams (non-adjacent < 1 mm)"""
    F = K.frames(B); R = AR.rotm(ax, np.nan_to_num(phi_b) * D2R); out = {}; jam = {}; jwho = {}; ax = -np.asarray(ax, float)   # exit side
    src = dict(M.rigid); src.update(M.link_pts)
    chain = [n for n in ("hub1", "hub2", "hubK", "L1a", "L1b", "L2") if n in src]
    nb, nr = len(G["boss"]), len(G["bar"])
    for j in range(len(B.idx)):
        if B.res[j] is None: continue
        Wb = (F.RHG[j] @ G["boss"].T).T; Wr = ((F.RHG[j] @ R[j]) @ G["bar"].T).T; Wl = (F.RHG[j] @ G["lug"].T).T
        d = B.dist(j, np.concatenate([Wb, Wr, Wl])); db, dr, dl = d[:nb], d[nb:nb + nr], d[nb + nr:]
        lug_c = float(dl.min())
        out[j] = dict(d=np.r_[db, dr] if lug_c >= 0 else np.r_[db, dr, lug_c], boss=float(db.min()), bar=float(dr.min()), lug=lug_c, boss_d=db, bar_d=dr)
        Om = {n: np.asarray(M.world(src[n][0], j, src[n][1])) for n in chain + ["hub3"] if n in src and len(src[n][1])}
        Oc = np.concatenate([Om[n] for n in chain if n in Om])
        dm = lambda A, Bm: float(np.sqrt(((A[:, None, :] - Bm[None, :, :]) ** 2).sum(-1)).min()) if len(A) and len(Bm) else 99.0
        axw = F.RHG[j] @ ax; far = lambda X: X[np.linalg.norm(X - (X @ axw)[:, None] * axw[None, :], axis=1) > float(G.get("rstack", 13.0))]
        cands = dict(bar_chain=dm(Wr, Oc), boss_chain=dm(Wb, Oc), lug_chain=dm(Wl, np.concatenate([Oc, Om["hub3"]]) if "hub3" in Om else Oc),
                     lug_bar=dm(far(Wl), far(Wr)))
        k = min(cands, key=cands.get); jam[j] = cands[k]; jwho[j] = k
    return out, jam, jwho


def run(params, which="envsel", flood=False):
    """the ideal path of insertion-cband-relay-4r.ideal (same lines; relay axis / seat from params) + R4 hardware (hw 1)"""
    AR = KF._ar(); CBm = AR.CB; t0 = time.time(); prm = dict(BASE, **params)
    if not hasattr(AR, "_gate_weld"): AR._gate_weld = AR.gate
    q2max = prm.get("q2max")
    if q2max is None: AR.gate = AR._gate_weld
    else:
        def _gq(M, Q, _g=AR._gate_weld, _m=float(q2max)):
            ok = _g(M, Q); q = M.D.ik(Q)[0]; return ok & (np.degrees(q[:, 1]) <= _m)
        AR.gate = _gq
    rp = dict(KF.LPAR); rp.update({k: prm[k] for k in KF.LPAR if k in prm})
    xp = {k: v for k, v in prm.items() if k not in KF.LPAR and k not in ("psi2", "q2max") and k not in HW}
    if float(prm.get("psi2", 0.0)):
        L0 = dict(AR.CC.PARAMS, **AR.LEAD); u1 = K.bvec(L0["az1"], L0["el1"]); u2 = K.bvec(L0["az2"], L0["el2"]); ps = math.radians(float(prm["psi2"]))
        v = K.unit(math.cos(ps) * u2 + math.sin(ps) * np.cross(u1, u2) + (1 - math.cos(ps)) * (u1 @ u2) * u1)
        xp.update(az2=math.degrees(math.atan2(v[2], -v[0])), el2=math.degrees(math.asin(float(np.clip(v[1], -1, 1)))))
    P = dict(AR.CC.PARAMS); P.update(AR.LEAD); P.update(smhi=5.0); P.update(xp); P = AR.CC._clamp(P)
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CBm.Bench(n_clip=60, n_ws=160); M1 = AR.CC.CCModel(B1, dict(P)); r1 = M1.run()
        for k in ("wd", "wa", "b3"):                                # the seat is asserted in the FITTED model
            assert abs(float(M1.p[k]) - float(prm[k])) < 1e-6, (k, M1.p[k], prm[k])
        for k in ("J3MIN", "J3MAX"):
            if k in prm: assert abs(float(M1.p[k]) - float(prm[k])) < 1e-6, (k, M1.p[k], prm[k])
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    phi, ax = AR.solve_phi(M1, rp); phi_fill = np.where(np.isfinite(phi), phi, 0.0); Zr = AR.relayed_Z(phi_fill, ax)

    class Frozen(AR.CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.rigid = dict(M1.rigid); self._sc = None; self.contact = list(M1.contact)
            KF._strip_drive(self)
            self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
    B = ICB._bench(which); phi_b = phi[B.idx]
    with AR.patched(Zr):
        M = Frozen(B, P2); M.run()
    why = np.asarray(M.why, dtype=object).copy(); nok = ~np.isfinite(phi_b)
    for i in np.nonzero(nok)[0]:
        B.res[i] = None
        if why[i] in ("", "contact", "skin"): why[i] = "kfold"
    M.why = why
    rd = ICB.readings(M, B, phi_b); ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses])
    rel = np.isfinite(phi_b) & (phi_b != 0)
    out = dict(params=prm, bench=which, mode=B.mode, n=len(B.idx), a1a2=[round(float(M1.D.a1), 3), round(float(M1.D.a2), 3)],
               axis=[round(float(x), 4) for x in ax], fit_lead_phi0={k: r1[k] for k in ("gap", "reach", "inband14", "contact")},
               why_ws={str(k): int(((why == k) & ws).sum()) for k in set(why.tolist())},
               relayed_ws=int((ws & rel).sum()), kin_ws=int((ws & np.isfinite(phi_b)).sum()),
               kin_overhead=[int((ws & np.isfinite(phi_b) & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())],
               phi_max=round(float(np.nanmax(np.abs(phi_b))), 2) if np.isfinite(phi_b).any() else 0.0,
               phi_p90_relayed=round(float(np.percentile(np.abs(phi_b[rel & ws]), 90)), 1) if (rel & ws).any() else 0.0)
    tk = np.isfinite(rd["kneeless"]["_mins"]) & (rd["kneeless"]["_mins"] >= 0)
    out["th"] = ICB.th_margin(M1, B, phi_b, ax, tk)
    if int(prm.get("hw", 0)):
      try:
        G = r4_geometry(AR, M1, B1, phi, ax, dict(HW, **{k: prm[k] for k in HW if k in prm}))
        ex, jam, jwho = r4_wear(AR, M, B, G, phi_b, ax)
        hwr = ICB.readings(M, B, phi_b, extra=ex, jam=jam)
        tkh = np.isfinite(hwr["kneeless"]["_mins"]) & (hwr["kneeless"]["_mins"] >= 0)
        R4 = {}
        for nm in ("boss", "bar", "lug"):
            v = np.array([ex[j][nm] for j in ex if tkh[j]]); va = np.array([ex[j][nm] for j in ex if jam.get(j, 9) >= 1.0])
            vr = np.array([ex[j][nm] for j in ex if tkh[j] and rel[j]])
            R4[nm] = dict(min=round(float(v.min()), 2) if len(v) else None, n_lt0=int((va < 0).sum()), n_lt2_taken=int((v < 2).sum()),
                          relayed_taken_lt2=int((vr < 2).sum()), contact_ws=int(sum(1 for j in ex if jam.get(j, 9) >= 1.0 and ex[j][nm] < 0 and ws[j])),
                          depth_max=round(float(-va.min()), 2) if len(va) and va.min() < 0 else 0.0)
        for nm in ("boss", "bar"):
            dd = np.concatenate([ex[j][nm + "_d"] for j in ex if tkh[j]]) if tkh.any() else np.zeros(1)
            R4[nm]["ib14"] = round(float(((dd >= 2) & (dd <= 14)).mean()), 3); R4[nm]["ib10"] = round(float(((dd >= 2) & (dd <= 10)).mean()), 3)
            R4[nm]["p5_50_95"] = np.percentile(dd, [5, 50, 95]).round(2).tolist()
        jl = [j for j, v in jam.items() if v < 1.0]
        R4["jams"] = len(jl); R4["jams_ws"] = int(sum(1 for j in jl if ws[j])); R4["jam_by"] = {k: sum(1 for j in jl if jwho[j] == k) for k in set(jwho[j] for j in jl)}
        R4["jams_relayed"] = int(sum(1 for j in jl if rel[j]))
        R4["geom"] = {k: v for k, v in G.items() if k not in ("boss", "bar", "lug")}
        out["hw_tk"] = tkh
        for t_ in hwr.values(): t_.pop("_mins", None)
        rd["hw"] = hwr["kneeless"]; rd["hw_noK"] = hwr["kneeless_noK"]; out["R4"] = R4; out["_G"] = G
      except Exception as ex_:                                    # keep the ideal reading if the hardware pass fails
        import traceback; traceback.print_exc(); out["hw_error"] = repr(ex_)
        try:
            import pickle; pickle.dump(dict(prm=prm, phi=phi, ax=ax), open(os.path.join(os.environ.get("O20_DUMP", "/tmp"), "o20_fail.pkl"), "wb"))
        except Exception: pass
    for t_ in rd.values(): t_.pop("_mins", None)
    out.update(rd)
    if flood:
        fr = AR.flood_relay(M1, rp); out["flood"] = fr[2] if isinstance(fr, tuple) else str(fr)[:300]
        if isinstance(fr, tuple):
            conn, ph = fr[0], fr[1]; out["flood"]["static_env"] = int(sum(1 for k in ph if np.isfinite(ph[k]))); out["flood"]["connected_env"] = int(sum(conn.values()))
    out["secs"] = round(time.time() - t0, 1)
    return out


def append_sweep(o, path=None):
    path = path or os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
    try: S_ = json.load(open(path))
    except Exception: S_ = []
    w = o["hw"] if "hw" in o else o["kneeless"]
    e = dict(k=len(S_), t=K.now(), params={k: v for k, v in o["params"].items()}, bench=o["bench"], mode=o["mode"],
             step="hardware (R4 boss + bar + lug)" if "hw" in o else "ideal (no R4 metal, knee-less readings)",
             inband14=w["inband14"], inband10=w["inband10"], reach=w["reach"], follow=w["follow"], contact=w["contact"], gap=w["gap"],
             gap_near1=w["near1"], gap_near2=w["near2"], overhead=w["overhead"], n_contact=w["n_contact"], depth_sum=w["depth_sum"],
             min_metal_taken=w["min_metal_taken"], ideal_gap=o["kneeless"]["gap"], a1a2=o["a1a2"], why_ws=o["why_ws"], th=o["th"],
             kin_ws=o["kin_ws"], kin_overhead=o["kin_overhead"], relayed_ws=o["relayed_ws"])
    if "R4" in o: e["R4"] = {k: v for k, v in o["R4"].items() if k != "geom"}; e["R4_geom"] = o["R4"]["geom"]
    if o.get("note"): e["note"] = o["note"]
    S_.append(e); json.dump(S_, open(path, "w"), indent=0, default=float)


def summary(o):
    s = {k: v for k, v in o.items() if k not in ("full", "kneeless", "kneeless_noK", "hw", "hw_noK", "_G", "hw_tk")}
    for k in ("kneeless", "hw"):
        if k in o: s[k] = {kk: vv for kk, vv in o[k].items() if kk not in ("contacts",)}
    s["full_gap"] = o["full"]["gap"]
    return s


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "run":
        prm = json.loads(a[1]) if len(a) > 1 else {}; which = a[2] if len(a) > 2 else "envsel"
        fl = bool(prm.pop("flood", 0)); o = run(prm, which, flood=fl)
        if os.environ.get("O20_APPEND", "1") == "1": append_sweep(o)
        if len(a) > 3: json.dump({k: v for k, v in o.items() if k not in ("_G", "hw_tk")}, open(a[3], "w"), indent=0, default=lambda x: x.tolist() if hasattr(x, "tolist") else float(x))
        print(json.dumps(summary(o), default=lambda x: x.tolist() if hasattr(x, "tolist") else float(x)), flush=True)
    elif a[0] == "append":                                       # append saved run outputs to the sweep, in the order given
        for fn in a[1:]: append_sweep(json.load(open(fn))); print("appended", fn)
