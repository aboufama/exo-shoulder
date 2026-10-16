"""geneva-tail-knuckle-pinknee-3r: minarc B (pin knee + spring knuckle K splitting link 1, kit fold rule, physical q2
stop) with the J2 stretched stop REPLACED by a one-tooth Geneva drive: link 2 continues backward past hub 2 as a rigid
tail; an MR63ZZ roller at its tip pushes ONE radial flank fixed to link 1a, so past the onset K's angle is a function of
q2 alone and the three encoders (J1, J2, J3) give the arm pose: 3 ACTIVE DOF, K never read, 0 passive translations.

Built on docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py (phys 1, kit rule, capK, near-touch objective), loaded
as its own module copy; only the stretched forced state, the tail metal and its checks change.

THE EXACT CONTACT LAW (replaces the proposer's dK = kK t, and the judge's planar atan(kK t)). Every axis passes through
GH, so the drive lives on the unit sphere. In link 1b's frame the roller centre is p(t) = R(u2, q2hi + s t) p0 (t = q2
travel past the onset q2hi, s = the stretching sense of q2); p0 is the tail tip: L_t deg from u2 on a great circle that
passes uK at its closest approach d (mm at r_law) when t = psi_c. The flank is a half-plane through K's axis (it contains
uK and GH), fixed to link 1a, so in link 1b's frame it turns by -dK. A plane through uK at azimuth az_pl is at distance
rho_n = rho / r_law from the roller centre iff az_pl = az(p) + s_m asin(rho_n / |p_perp|) (az, p_perp about uK):
    dK(t) = -[az_pl(t) - az_pl(0)],  s_m = sign(d az / dt) (the flank sits ahead of the roller),
exact in 3-D. The roller's side of K (L_t = bk2 - d "inside" or bk2 + d "outside") is chosen so the pushed flank opens K
(sign dK = sign psiA); a design where neither side does is not built. th_law(t) = angle(u1, R(uK, dK) R(u2, q2) u3) is
pose-independent, so a stretched pose (th > th_hi) is solved by inverting th_law on its valid prefix:
  * monotone: th_law strictly rising with rate dq2/dth <= RATE_MAX (3.45),
  * pressure angle (roller velocity vs flank normal) <= pa_max (45 deg),
  * the contact on the tooth: radius r_c from K's axis inside the tooth (crown embodiment: <= HUB_R on the cap face;
    beside embodiment: <= lug_max on link 1a's lug),
  * K <= stop B (a1max) and the forced chain's fold margins (msub, m3e >= 5, as the parent),
  * no lift-off: along the pose's self-motion curve (th fixed) K must not be able to sit off the roller at a smaller
    opening (the spring would put it there and q2 would no longer give K): slope 0 < d|dK|/dt|_C < d|dK|/dt|_law fails.
The end of the valid prefix is the physical q2 dowel stop B. The folded side has NO tooth: J2 stops on its q2lo dowel and
K stays on stop A (folded poses beyond it are not taken).

THE TAIL METAL (before any CMA, the judge's lead). Member 2 gets a second strap "LT" (8 x 3 Ti, rigid with link 2) from
hub 2 along the great circle to the tip, skin-fitted like every link (in-band and skin contact counted), ramping
(60 deg) from hub 2's upper level to a FLOOR at the tip:
  * crown embodiment (d < HUB_R + rho + 1: the roller passes over hub K): roller bottom >= K's cap top + 1 mm (a tooth
    blade on the cap face), tail underside = roller bottom + 3 (2.5 roller + washer);
  * beside embodiment (d >= HUB_R + rho + 1): the roller runs beside hub K at link 1a's level against a lug of link 1a
    (lug metal sampled), tail underside >= link 1a's top at K + 1 mm.
The roller boss (O8) hangs 3 mm below the tip (sampled, skin-checked, in band). Collisions: LT + roller vs hub 1, hub K
(cap included), hub 3, L1a, L1b (outside hub 2's zone), knee, pad, E at >= 1 mm.
K's stack is flipped (link 1a upper at K) so the cap with the tooth rides on link 1a, as the spec says.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("kitrule_for_geneva", os.path.join(HERE, "minarc-stop-knuckle-4r-kitrule.py"))
KR = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KR)
KB, PK, S = KR.KB, KR.PK, KR.S
unit = S.unit; D2R = math.pi / 180
ID = "geneva-tail-knuckle-pinknee-3r"
RATE_MAX = 3.45
ROLLER_H, BOSS_R = 3.0, 4.0                                   # MR63ZZ 2.5 wide + washer; O8 boss

# LB1 (the proposer's / judge's seats: the kit-rule B model at its best) + the drive
LB1 = {"o1a": 0.0, "o1c": 0.0, "o2a": 0.0, "o2c": 0.0, "o3a": 0.0, "o3c": 0.0, "S_a": 15.0, "S_t": 15.0, "R_r": 0.5, "drop": 1, "S_auto": 0,
       "jam_contact": 1, "remote": 0, "neck": 13.0, "ramp": 1, "slides": 1, "vfix": 1, "branch": 0, "flip3": 0, "az1": 94.7751, "el1": 67.1851,
       "b1": 0.0, "az2": 44.7138, "el2": 43.097, "b2": 0.0, "wd": 54.2545, "wa": -11.0155, "b3": 0.4056, "S_max": 25.0, "centre": 1, "R_tol": 0.5,
       "inv": 0, "lE": 63.8584, "lc": 25.501, "phiE": 1.5965, "phib": -74.4542, "stk": 4.8639, "ang_min": 27.7418, "rad1": 10.0, "rad2": 10.0,
       "rad3": 10.0, "bk1": 28.3208, "bk2": 46.7062, "sK": -1, "a1max": 67.5814, "mstop": 0, "kitrule": 1, "smhi": 8.0, "smlo": 5.0, "near": 1,
       "phys": 1, "capK": 6.0, "m3e": 1}
PARAMS = dict(KR.PARAMS, **LB1)
PARAMS.update(cam=1, d_mm=7.0, psi_c=0.0, side=0, rho=3.0, r_law=70.0, pa_max=45.0, lug_max=22.0, tail=1, flipK=1)


class GDesign(KR.KRDesign):
    def law(self):
        """the exact one-tooth contact law on a t grid (rad past the onset); cached per design"""
        if getattr(self, "_law", None) is not None: return self._law
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg)
        # stretching sense of q2: th rises with q2 past q2hi on the 3R
        def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        r_law = float(P["r_law"]); rho_n = float(P["rho"]) / r_law; d_deg = math.degrees(float(P["d_mm"]) / r_law)
        bk2 = float(P["bk2"]); e, f = S.frame_of(uK)
        best = None
        for side in ((-1.0, 1.0) if not P.get("side") else (float(np.sign(P["side"])),)):
            Lt = bk2 + side * d_deg
            if not (5.0 < Lt < 175.0): continue
            # closest-approach point: Lt from u2 toward uK on the great circle u2 -> uK
            ax = unit(np.cross(u2, uK)); m = S.rotm(ax, Lt * D2R)[0] @ u2
            q2c = q2hi + s_q * float(P["psi_c"]) * D2R
            p0 = S.rotm(u2, -q2c)[0] @ m                         # tail tip in link 2's reference frame (q2 = 0)
            ts = np.radians(np.arange(0.0, 60.01, 0.1)); q2t = q2hi + s_q * ts
            pt = np.einsum("nij,j->ni", S.rotm(u2, q2t), p0)
            pperp = pt - (pt @ uK)[:, None] * uK; rp = np.linalg.norm(pperp, axis=1)
            az = np.unwrap(np.arctan2(pperp @ f, pperp @ e)); daz = np.gradient(az)
            s_m = float(np.sign(daz[0])) or 1.0
            if abs(rp[0]) <= rho_n: continue
            azpl = az + s_m * np.arcsin(np.clip(rho_n / np.maximum(rp, 1e-9), -1, 1))
            dK = -(azpl - azpl[0])
            if np.sign(dK[5]) != sp: continue                  # this side's flank would close K: wrong side
            best = (side, Lt, p0, ts, q2t, pt, dK, rp, s_m, q2hi, s_q)
            break
        if best is None:
            self._law = dict(ok=False); return self._law
        side, Lt, p0, ts, q2t, pt, dK, rp, s_m, q2hi, s_q = best
        RK = S.rotm(uK, dK); R2 = S.rotm(u2, q2t)
        th = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, np.einsum("nij,j->ni", R2, u3)) @ u1, -1, 1)))
        # pressure angle: roller velocity (about u2, in link 1b's frame) vs the flank normal (in link 1b's frame)
        v = np.cross(u2, pt)
        # flank normal at azimuth az_pl + 90 deg (the plane contains uK and the azimuth direction)
        pperp = pt - (pt @ uK)[:, None] * uK
        az = np.unwrap(np.arctan2(pperp @ f, pperp @ e)); apl = az + s_m * np.arcsin(np.clip(rho_n / np.maximum(rp, 1e-9), -1, 1))
        nvec = -np.sin(apl)[:, None] * e + np.cos(apl)[:, None] * f
        pa = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i", nvec, v)) / np.maximum(np.linalg.norm(v, axis=1), 1e-12), 0, 1)))
        r_c = np.sqrt(np.maximum(rp ** 2 - rho_n ** 2, 0)) * float(P["r_law"])     # contact radius on the flank (mm)
        kabs = np.abs(dK); dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
        # lift-off: self-motion slope at fixed th: d|dK|/dt|_C = -(dth/dt|_dK) / (dth/d|dK| |_t)
        h = 1e-4
        def th_of(tt, kk):
            R = S.rotm(uK, sp * kk); R2_ = S.rotm(u2, q2hi + s_q * tt)
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
        lift = (sC > 1e-9) & (sC < dk - 1e-9)
        rate = 1.0 / np.maximum(np.radians(dth) * 1.0, 1e-12)     # dq2/dth (both rad)
        if float(P["d_mm"]) < S.HUB_R + float(P["rho"]) + 1.0: emb, rmax = "crown", S.HUB_R
        else: emb, rmax = "beside", float(P["lug_max"])
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
        good = (dth > 0) & (rate <= RATE_MAX) & (pa <= float(P["pa_max"])) & (r_c <= rmax) & ~lift & (kabs <= dKB + 1e-9) & (np.sign(dK) * sp >= 0)
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good)   # valid prefix (q2 dowel stop B at its end)
        why_end = None
        if nval < len(good):
            j = nval
            why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "pressure" if pa[j] > float(P["pa_max"]) else
                       "tooth" if r_c[j] > rmax else "liftoff" if lift[j] else "stopB" if kabs[j] > dKB else "sign")
        self._law = dict(ok=nval > 1, side=side, Lt=Lt, p0=p0, ts=ts[:nval], q2t=q2t[:nval], dK=dK[:nval], th=th[:nval], pa=pa[:nval], r_c=r_c[:nval],
                         rate=rate[:nval], emb=emb, q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=s_m,
                         dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                         th_max=float(th[nval - 1]) if nval else None, phi_t=None)
        # planform bend of the tail at hub 2 (deg about u2 from link 2's own backward extension)
        ext = unit(S.rotm(unit(np.cross(u3, u2)), Lt * D2R)[0] @ u2)
        a_ = unit(ext - (ext @ u2) * u2); b_ = unit(p0 - (p0 @ u2) * u2)
        self._law["phi_t"] = float(np.degrees(math.atan2(float(np.cross(a_, b_) @ u2), float(a_ @ b_))))
        return self._law

    def _ik_phys(self, Q):
        if not self.p.get("cam"): return super()._ik_phys(Q)
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN
        b1 = float(P["bk1"])
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        save = (P["phi_lo"], P["phi_hi"], P["a1max"]); P["phi_lo"], P["phi_hi"] = S.SING, 180 - S.SING
        try: qA, okA, X1A, X2A, X3A, sA = super(KR.KRDesign, self).ik(Q)      # the variant-B closure (K on stop A)
        finally: P["phi_lo"], P["phi_hi"], P["a1max"] = save
        dKA = self._dK.copy()
        A, R, q0 = self._q2c
        rel = np.degrees(PK.wrap(qA[:, 1] - q0))
        if self.q2sgn is None:
            sel = okA & (np.abs(dKA) < 1e-9) & (np.abs(rel) > 1)
            self.q2sgn = float(np.sign(np.median(rel[sel]))) if sel.any() else 1.0; P["q2sgn"] = self.q2sgn
        sg = self.q2sgn
        q2hi, q2lo = self._q2_at(self.th_hi, sg), self._q2_at(self.th_lo, sg)
        self.q2_stops = (math.degrees(q2lo), math.degrees(q2hi))
        inA = okA & (np.abs(dKA) < 1e-9) & (np.sign(rel) == sg) & (th >= self.th_lo - 1e-6) & (th <= self.th_hi + 1e-6)
        L = self.law()
        st = np.where(th > self.th_hi, 1, np.where(th < self.th_lo, -1, 0)); st = np.where(inA, 0, st)
        if L.get("ok"):
            thL = L["th"]; tt = np.interp(th, thL, L["ts"]); inlaw = (st == 1) & (th <= thL[-1] + 1e-9)
            dKf = np.interp(tt, L["ts"], L["dK"]); q2s = q2hi + L["s_q"] * tt
        else:
            inlaw = np.zeros(n, bool); dKf = np.zeros(n); q2s = np.full(n, q2hi); tt = np.zeros(n)
        q2s = np.where(st == 1, q2s, q2lo); dK = np.where(inlaw, dKf, 0.0)
        Rq = S.rotm(u2, q2s) if n else np.zeros((0, 3, 3)); p = Rq @ u3
        RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w)
        R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ RK @ Rq; vv = KR.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        fA = st == 0; fa = fA[:, None]; fa3 = fA[:, None, None]
        q = np.where(fa, qA, np.stack([q1, q2s, q3], 1))
        R1m = np.where(fa3, X1A[0], R1); R2m = np.where(fa3, X2A[0], R12); R3m = np.where(fa3, X3A[0], R123); t3m = np.where(fa, X3A[1], t3)
        RKm = np.where(fa3, np.eye(3)[None], RK); dKm = np.where(fA, 0.0, dK)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RKm, u2) @ u1, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1)))
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        m3e = KR.dyad_margin(th, a1e, self.a2)
        ok = np.where(fA, inA, inlaw & (msub >= m - 1e-6)) & bool(self.k_ok) & bool(self.stops_ok)
        if P.get("m3e", 1): ok &= m3e >= m - 1e-6
        # closure residual of the law solution (must close: th_law(t) = th)
        Z0 = np.zeros((n, 3)); X1 = (R1m, Z0); X1b = (R1m @ RKm, Z0); X2 = (R2m, Z0); X3 = (R3m, t3m)
        sv = np.einsum("nji,nj->ni", Q, t3m); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        self._X1b, self._dK, self._state, self._a1e, self._msub, self._m3e = X1b, dKm, st, a1e, np.where(fA, 99.0, msub), m3e
        self._camt = np.where(st == 1, np.degrees(tt), 0.0); self._q2now = q[:, 1]
        return q, ok, X1, X2, X3, s


KR.KB.KDesign = GDesign; KR.KRDesign_G = GDesign


class GModel(KR.KModel):
    """+ the tail strap LT (member 2), the roller boss, the tooth lug (beside embodiment), K's flipped stack"""

    def fit(self):
        D = self.D; P = D.p
        if not (P.get("cam") and P.get("tail", 1)): return super().fit()
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hubK", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[nm][0], g[nm][1], np.broadcast_to(g[nm][2], g[nm][1].shape).copy(), 140.0) for nm in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hubK": res["hubK"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self._greedy(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); fK = H["hubK"][keep1].max(); f2 = H["hub2"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = KB.KGeo(D, self.hr); geo.add_links(f1, fK, f2, f3); self.geo = geo
        self._tr_fit = H["stack"][keep1].max()
        L_ = D.law()
        self._tail_rows = self._tail_geom(L_) if L_.get("ok") else []
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        for ri, (dv, keep, sarc) in enumerate(self._tail_rows):
            items.append((2, np.zeros((len(dv), 3)), dv, 170.0, ())); idx.append(("LT", ri))
        if L_.get("ok"):
            items.append((2, np.zeros((1, 3)), self._tip_dir[None], 170.0, ())); idx.append(("TIP", 0))
        res = self.needed(items, poses); Lq = {}
        for (nm, ri), r in zip(idx, res): Lq.setdefault(nm, []).append(r)
        Lq["E"] = [self._HE]; self.Lneed = Lq                    # LT rows + TIP join the greedy pose drop like every link
        self._greedy(keep0=keep1)
        self.finalize()

    def _tail_geom(self, L_):
        """LT rows: great circle from hub 2's axis to the tail tip, 8 mm wide (rows -3, -1, 1, 3 mm), outside hub 2"""
        D = self.D; u2 = D.u[1]; tip = unit(L_["p0"]); self._tip_dir = tip
        ang = math.acos(float(np.clip(u2 @ tip, -1, 1))); bn = unit(np.cross(u2, tip)); R = 65.0
        nn = max(4, int(R * ang / S.SPACING)); ts = (np.arange(nn) + 0.5) / nn
        dirs = np.array([unit(math.sin((1 - t) * ang) * u2 + math.sin(t * ang) * tip) for t in ts]); rows = []
        for v in (-3.0, -1.0, 1.0, 3.0):
            dv = unit(dirs + (v / R) * bn); pts = R * dv; w = pts
            keep = np.linalg.norm(w - (w @ u2)[:, None] * u2, axis=1) > S.HUB_R
            rows.append((dv, keep, ts * R * ang))
        self._LT_len = R * ang
        return rows

    def finalize(self):
        super().finalize()
        D = self.D; P = D.p
        if not (P.get("cam") and P.get("tail", 1)) or not getattr(self, "_tail_rows", None): return
        keep = ~self.drop; L_ = D.law(); k = math.tan(S.RAMP * D2R)
        self._LT_need = self.Lneed.get("LT", []); self._TIP_need = self.Lneed.get("TIP", [None])[0]
        capK = float(P.get("capK", 0) or 0); fK = self.fK; f2 = self.f[1]; u2 = D.u[1]
        if L_["emb"] == "crown": floor_tip = fK + S.CROWN + capK + 1.0 + ROLLER_H
        else: floor_tip = fK + S.UP + S.T_LINK + 1.0
        self._floor_tip = floor_tip; pts_all = []
        # stacking over link 1b: the tail turns about u2, so at angular distance g from u2 it sweeps over every point of
        # link 1b at the same g; its underside clears link 1b's top there by 1 mm (outside hub 2's 4-mm zone, the
        # adjacent running gap applies inside it)
        L1b = self.link_pts["L1b"][1]; gL = np.degrees(np.arccos(np.clip(unit(L1b) @ u2, -1, 1))); rL1b = np.linalg.norm(L1b, axis=1)
        def stack_floor(dirs):
            gT = np.degrees(np.arccos(np.clip(dirs @ u2, -1, 1))); out = np.zeros(len(dirs))
            for j, gg in enumerate(gT):
                sel = np.abs(gL - gg) <= 3.0
                if sel.any(): out[j] = (rL1b[sel] + S.T_LINK + 1.0).max() / max(float(dirs[j] @ unit(L1b[sel][np.argmax(rL1b[sel])])), 0.5)
            return out
        tipneed = float(self._TIP_need[keep].max()) if self._TIP_need is not None and keep.any() else 0.0
        for (dv, keep_s, sarc), rr in zip(self._tail_rows, self._LT_need):
            r = (rr[keep].max(0) if keep.any() else rr.max(0)).copy(); Sx = sarc
            idx = np.nonzero(keep_s)[0]
            if not len(idx): continue
            j0 = idx[0]; rc = (f2 + S.UP) / max(float(dv[j0] @ u2), 0.2)
            r = np.maximum(r, rc - k * np.abs(Sx - Sx[j0]))
            r = np.maximum(r, np.where(np.linalg.norm(np.cross(dv * 65.0, u2), axis=1) > S.HUB_R + 4.0, stack_floor(dv), 0.0))
            Send = Sx[-1]; r = np.maximum(r, np.where(Sx >= Send - BOSS_R, floor_tip, floor_tip - k * (Send - BOSS_R - Sx)))
            r = np.maximum(r, tipneed + ROLLER_H - k * np.maximum(0, Send - BOSS_R - Sx))   # roller bottom clears the skin under the tip
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            pts_all.append(dv[keep_s] * r[keep_s][:, None])
        self.link_pts["LT"] = (2, np.concatenate(pts_all))
        rtip = max(floor_tip, tipneed + ROLLER_H) - ROLLER_H        # roller bottom radius
        e, f = S.frame_of(self._tip_dir); dd = S.disc(BOSS_R, 2.0)
        self.rigid["roller"] = (2, self._tip_dir * rtip + dd[:, :1] * e + dd[:, 1:] * f)
        self._roller_bottom = rtip
        if L_["emb"] == "beside":                                # the tooth lug on link 1a at K (upper level)
            uK = D.uK; n0 = D.law()
            # lug along the flank at stop A: from the hub rim to lug_max, 6 mm wide, at link 1a's level at K
            p0 = S.rotm(u2, L_["q2hi"])[0] @ L_["p0"]; pp = unit(p0 - (p0 @ uK) * uK); tv = unit(np.cross(uK, pp))
            rs = np.arange(S.HUB_R, float(P["lug_max"]) + 1e-6, 2.0); ws = np.arange(-3.0, 3.01, 2.0)
            lev = fK + S.UP
            lug = np.array([lev * uK + r_ * pp + w_ * tv for r_ in rs for w_ in ws])
            self.rigid["lug"] = (1, lug)
        self._contact_only(); self._solids()
        # roller: contact rings (crown side) + its own collision samples
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False); ring = BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
        self.contact.append((2, np.concatenate([self._tip_dir * z + ring for z in (rtip, rtip + ROLLER_H)])))
        self.strap["ROL"] = (2, np.concatenate([self._tip_dir * z + ring for z in np.linspace(rtip, rtip + ROLLER_H, 3)]))

    def _contact_only(self):
        super()._contact_only()
        if "lug" in getattr(self, "rigid", {}):
            mem, X = self.rigid["lug"]; self.contact.append((mem, X + S.T_LINK * self.D.uK))

    def collide(self, i):
        out = super().collide(i)
        if "LT" not in self.strap: return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        LT = tf(*self.strap["LT"]); ROL = tf(*self.strap["ROL"]); c = {}
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def ss(A, Bq, extra=2 * h): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        L_ = self.D.law(); st = self.kstate[i] if hasattr(self, "kstate") else 0
        touching = bool(st == 1)                                  # the law says roller and tooth touch (only then exempt)
        for hb in ("hub1", "hubK", "hub3"):
            c[f"LT-{hb}"] = vcyl(LT, hb, h)
            if not (hb == "hubK" and L_["emb"] == "crown" and touching): c[f"ROL-{hb}"] = vcyl(ROL, hb)
        strap = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1a", "L1b")}
        c["LT-L1a"] = ss(LT, strap["L1a"]); c["ROL-L1a"] = ss(ROL, strap["L1a"], h)
        c["LT-L1b"] = ss(far(LT, "hub2", 4), far(strap["L1b"], "hub2", 4)); c["ROL-L1b"] = ss(ROL, strap["L1b"], h)
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]
            c[f"{nm}-LT"] = float(self.sd_box(LT, cen, R, half).min()) - h; c[f"{nm}-ROL"] = float(self.sd_box(ROL, cen, R, half).min())
        Em = tf(*self.Emid); c["E-LT"] = ss(Em, LT); c["E-ROL"] = ss(Em, ROL, h)
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


KR.KB.KModel = GModel


def _report(B, params):
    p = dict(PARAMS, **params)
    r, M = KR._report(B, p)
    D = M.D
    if p.get("cam"):
        L_ = D.law(); ko = M.kin_ok; st = M.kstate
        r["drive"] = dict(ok=bool(L_.get("ok")), emb=L_.get("emb"), side=L_.get("side"), L_t=round(L_.get("Lt", 0), 2) if L_.get("ok") else None,
                          phi_t=round(L_["phi_t"], 1) if L_.get("phi_t") is not None else None, dK_law_max=round(L_.get("dK_max", 0), 1),
                          t_max=round(L_.get("t_max", 0), 1), th_hi=round(D.th_hi, 2) if hasattr(D, "th_hi") else None,
                          th_max=round(L_["th_max"], 2) if L_.get("th_max") is not None else None, why_end=L_.get("why_end"),
                          pa_max_used=round(float(L_["pa"].max()), 1) if L_.get("ok") else None, rc_max=round(float(L_["r_c"].max()), 1) if L_.get("ok") else None,
                          rate_max_used=round(float(L_["rate"].max()), 2) if L_.get("ok") else None,
                          stretched_kin=int((ko & (st == 1)).sum()), folded_kin=int((ko & (st == -1)).sum()),
                          dK_taken_max=round(float(np.degrees(np.abs(M.dK[ko & (st == 1)])).max()), 1) if (ko & (st == 1)).any() else 0.0,
                          floor_tip=round(getattr(M, "_floor_tip", 0.0), 1), roller_bottom=round(getattr(M, "_roller_bottom", 0.0), 1),
                          LT_len_mm=round(getattr(M, "_LT_len", 0.0), 1), fK=round(float(getattr(M, "fK", 0)), 1))
        if hasattr(M, "link_pts") and "LT" in getattr(M, "link_pts", {}):
            # in-band share of the tail alone over the taken clip frames
            tk = [i for i in range(len(B.idx)) if B.kind[i] == "clip" and B.res[i] is not None and float(np.min(B.res[i])) >= 0]
            if tk:
                dd = np.concatenate([B.dist(i, M.world(2, i, M.link_pts["LT"][1])) for i in tk[::3]])
                r["drive"]["LT_ib14"] = round(float(((dd >= 2) & (dd <= 14)).mean()), 3); r["drive"]["LT_med_mm"] = round(float(np.median(dd)), 1)
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    out = KB.frozen(dict(PARAMS, **P), nc, nw)
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=a.get("overhead140"), parts=out.get("parts_ib14"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], contact=r["contact"], why=r.get("why"), ovh=r.get("overhead140"), drive=r.get("drive"),
                          parts=r.get("parts_ib14"), pairs=r.get("parts_pairs"), secs=round(time.time() - t)), default=float))
