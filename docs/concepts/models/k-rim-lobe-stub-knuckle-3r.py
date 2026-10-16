"""k-rim-lobe-stub-knuckle-3r: the round-6 winner's chain (pin knee + spring knuckle K splitting link 1, kit fold rule,
physical q2 stops, capK 6) with the rod drive (rim lobe -> rocker -> O3 pushrod -> horn) REPLACED by ONE direct higher
pair, inverted: a LOBE plate rides on link 1a around hub K (it turns only with K, <= dK_max), and an MR52ZZ roller
(O5 x 2.5, O2 pin) hangs from a short STUB of link 2 at hub 2, aimed back at K. Past the stretched q2 stop onset the
roller enters the lobe and opens K with the LINEAR law dK = sp kK t (t = q2 travel past the onset); K is slaved, never
read: 3 ACTIVE (J1, J2, J3), K + 2 knee pins passive, 0 passive translations, one closed loop through the contact.

Built on docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py (loaded as its own module copy): the state machine
(state A / law / folded stop), the stub strap = its tail strap (skin-fitted 8 x 3 Ti from hub 2 to the stub tip, ramps
60 deg), the roller boss and the LT / ROL collision pairs are reused; what is new here:

  * THE LAW AND ITS GATES (exact, on the unit sphere; every axis passes through GH, the roller axis is radial, the lobe
    flank is a radial ruled surface): roller centre P(t) = R(u2, q2hi + s_q t) p_stub in link 1b's frame, p_stub = the
    stub tip in link 2's frame at q2 = 0: L_stub (mm at r_law) from u2 along the great circle at azimuth a0 about u2
    measured from link 2's own direction (u2 -> u3). Lobe pitch curve in link 1a's frame C(t) = R(uK, dK(t)) P(t) (the
    model's convention x_1a = R(uK, dK) x_1b). Per t: relative roller velocity v_rel = s_q u2 x P + sp kK uK x P, pitch
    normal n = P x v_rel, lobe point velocity v_l = -sp kK uK x P; the lobe lies on the side n_l (n_l . v_l > 0: the roller
    pushes K open, the clock spring keeps the lobe on the roller), pressure angle pa = angle(n_l, v_l) <= pa_max.
    Valid prefix (the q2 dowel stop B at its end): th rising, rate <= 3.45, pa <= pa_max, no lift-off (self-motion slope,
    as the parent), K <= stop B, pitch-curve geodesic radius >= rr + curv_min wherever the lobe is convex, and the stub
    end boss (O6) >= HUB_R + 1 mm off hub K's axis at the nominal radius (the per-pose 3-D check is in collide).
  * THE LOBE METAL (member 1): a spherical-shell sector (5-axis machined from solid Ti-6Al-4V, stated on the part, 3 mm)
    from the flank (pitch curve offset rr toward n_l) back lobe_w mm, plus a web along the great circle to hub K's rim.
    Its level R_lobe = max(link 1b's top under it + 1 mm (link 1b is the UPPER member at K in this chain), its own skin
    need over the fit poses (joins the greedy pose drop), roller-tip skin need - 1). The roller spans R_lobe + 1 .. + 4
    (2 mm overlap with the 3 mm plate), the stub strap's underside at the tip sits at R_lobe + 4 (1 mm over the lobe).
  * PART PAIRS (>= 1 mm): LOBE vs hub 2, hub 3, L1b (outside hub K's 4 mm zone), L2, the stub strap LT, knee, pad, E;
    ROL vs LOBE >= 1 mm whenever the law does not say they touch (state A / folded: the stub must turn away); LT / ROL vs
    hub 1, hub K (cap included, NO exemption), hub 3, L1a, L1b, knee, pad, E (parent).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/k-rim-lobe-stub-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/k-rim-lobe-stub-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("geneva_for_krim", os.path.join(HERE, "geneva-tail-knuckle-pinknee-3r.py"))
G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
KR, KB, PK, S = G.KR, G.KB, G.PK, G.S
unit = S.unit; D2R = math.pi / 180
ID = "k-rim-lobe-stub-knuckle-3r"
G.BOSS_R = 3.0                                                # MR52ZZ O5 roller on an O2 pin: O6 stub-end boss
G.ROLLER_H = 3.0                                              # 2.5 wide + 0.5 shim
ROLLER_H, BOSS_R = G.ROLLER_H, G.BOSS_R

# the verified winner's seats (docs/concepts/rows/geneva-tail-knuckle-pinknee-3r.json best_params) + this drive
W = {"bk1": 31.2491, "bk2": 37.9937, "a1max": 58.3565, "smhi": 13.6865, "smlo": 5.2777, "az1": 93.5546, "el1": 67.3642,
     "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863,
     "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "capK": 6.0}
PARAMS = dict(G.PARAMS, **W)
PARAMS.update(emb_mode="kstub", tail=1, cam=1, kK=1.0, smhi=20.0, a1max=50.0, L_stub=24.0, a0=168.0, rr=2.5, r_law=60.0,
              lobe_w=4.0, pa_max=45.0, curv_min=1.0, tip_tol=2.0, lobe_lev=0)


class KSDesign(G.GDesign):
    def law(self):
        P = self.p
        if P.get("emb_mode") != "kstub": return super().law()
        if getattr(self, "_law", None) is not None: return self._law
        u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg); q2lo = self._q2_at(self.th_lo, sg)
        def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        r_law = float(P["r_law"]); kK = float(P["kK"]); rr = float(P["rr"])
        Lang = float(P["L_stub"]) / r_law
        t0 = unit(u3 - (u3 @ u2) * u2)
        d0 = S.rotm(u2, float(P["a0"]) * D2R)[0] @ t0
        p0 = unit(math.cos(Lang) * u2 + math.sin(Lang) * d0)       # stub tip (roller centre) in link 2's frame, q2 = 0
        ts = np.radians(np.arange(0.0, 60.01, 0.1)); q2t = q2hi + s_q * ts
        pt = np.einsum("nij,j->ni", S.rotm(u2, q2t), p0)          # roller centre in link 1b's frame
        dK = sp * kK * ts
        RK = S.rotm(uK, dK)
        th = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, np.einsum("nij,j->ni", S.rotm(u2, q2t), u3)) @ u1, -1, 1)))
        vrel = s_q * np.cross(u2, pt) + sp * kK * np.cross(uK, pt)
        vl = -sp * kK * np.cross(uK, pt)
        n = np.cross(pt, vrel); n = n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
        sgn = np.sign(np.einsum("ij,ij->i", n, vl)); sgn[sgn == 0] = 1.0
        nl = n * sgn[:, None]                                      # lobe side (link 1b's frame)
        pa = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", nl, vl) / np.maximum(np.linalg.norm(vl, axis=1), 1e-12), -1, 1)))
        # pitch curve and lobe side in link 1a's frame
        C = np.einsum("nij,nj->ni", RK, pt); NL = np.einsum("nij,nj->ni", RK, nl)
        # geodesic curvature of the pitch curve (at r_law, mm)
        X = C * r_law; dX = np.gradient(X, axis=0); ds = np.maximum(np.linalg.norm(dX, axis=1), 1e-9)
        T = dX / ds[:, None]; dT = np.gradient(T, axis=0) / ds[:, None]
        kg = dT - (np.einsum("ij,ij->i", dT, C))[:, None] * C
        kmag = np.linalg.norm(kg, axis=1); convex = np.einsum("ij,ij->i", kg, NL) > 0
        rho_c = 1.0 / np.maximum(kmag, 1e-9)
        curv_ok = ~convex | (rho_c >= rr + float(P.get("curv_min", 1.0)))
        # stub end boss vs hub K (nominal radius; the per-pose 3-D check is in collide)
        dKax = r_law * np.sin(np.arccos(np.clip(pt @ uK, -1, 1)))
        clr_ok = dKax >= S.HUB_R + 1.0 + BOSS_R
        kabs = np.abs(dK); dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
        h = 1e-4
        def th_of(tt, kk):
            R = S.rotm(uK, sp * kk); R2_ = S.rotm(u2, q2hi + s_q * tt)
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
        lift = (sC > 1e-9) & (sC < dk - 1e-9)
        rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
        good = (dth > 0) & (rate <= G.RATE_MAX) & (pa <= float(P["pa_max"])) & curv_ok & clr_ok & ~lift & (kabs <= dKB + 1e-9)
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good)
        why_end = None
        if nval < len(good):
            j = nval
            why_end = ("rate" if not (dth[j] > 0 and rate[j] <= G.RATE_MAX) else "pressure" if pa[j] > float(P["pa_max"]) else
                       "curvature" if not curv_ok[j] else "hubK" if not clr_ok[j] else "liftoff" if lift[j] else "stopB")
        # state-A sweep of the roller (K on stop A, lobe fixed): signed offset from the pitch band, and hub K clearance
        tA = np.radians(np.linspace(0.0, abs(math.degrees(q2hi - q2lo)) + 0.0, 181)); qA = q2hi - s_q * tA
        pA = np.einsum("nij,j->ni", S.rotm(u2, qA), p0)
        self._law = dict(ok=nval > 1, side=0.0, Lt=math.degrees(Lang), p0=p0, ts=ts[:nval], q2t=q2t[:nval], dK=dK[:nval], th=th[:nval],
                         pa=pa[:nval], r_c=dKax[:nval], rate=rate[:nval], emb="kstub", q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=1.0,
                         dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                         th_max=float(th[nval - 1]) if nval else None, phi_t=None, C=C[:nval], NL=NL[:nval],
                         rho_min=float(rho_c[:nval][convex[:nval]].min()) if (convex[:nval]).any() else None,
                         hubK_min_nom=float(min(dKax[:nval].min(), (r_law * np.sin(np.arccos(np.clip(pA @ uK, -1, 1)))).min())),
                         pA=pA)
        return self._law


KR.KB.KDesign = KSDesign


class KSModel(G.GModel):
    """+ the lobe sector on link 1a (member 1), its level, its pairs; the stub = the parent's tail strap"""

    def _lobe_dirs(self, R_ref):
        """lobe sample directions (link 1a's frame): flank band rr .. rr + lobe_w behind the pitch curve + web to hub K"""
        D = self.D; P = D.p; L_ = D.law(); uK = D.uK
        C, NL = L_["C"], L_["NL"]; rr = float(P["rr"]); w = float(P["lobe_w"])
        # resample the pitch curve every ~1.5 mm
        X = C * R_ref; s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(X, axis=0), axis=1))]
        ss = np.arange(0, s[-1] + 1e-6, 1.5) if s[-1] > 0 else np.array([0.0])
        idx = np.clip(np.searchsorted(s, ss), 0, len(C) - 1)
        out = []
        for j in idx:
            for d in np.arange(rr, rr + w + 1e-6, 1.5):
                out.append(unit(C[j] + (d / R_ref) * NL[j]))
        out = np.array(out)
        # web: from the body sample closest to K's axis along the great circle to hub K's rim, 4 mm wide
        g = np.arccos(np.clip(out @ uK, -1, 1)); k = int(np.argmin(g)); v = out[k]
        gs = np.arange(S.HUB_R / R_ref, g[k], 1.5 / R_ref); ax = unit(np.cross(uK, v)); web = []
        for gg in gs:
            base = unit(math.cos(gg) * uK + math.sin(gg) * unit(v - (v @ uK) * uK))
            for o in (-2.0, 0.0, 2.0): web.append(unit(base + (o / R_ref) * ax))
        return np.concatenate([out, np.array(web).reshape(-1, 3)]) if web else out

    def fit(self):
        D = self.D; P = D.p
        if P.get("emb_mode") != "kstub": return super().fit()
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
        self._lobe_R0 = fK + S.UP + S.T_LINK + 1.0
        self._lobe_d = self._lobe_dirs(self._lobe_R0) if L_.get("ok") else np.zeros((0, 3))
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        for ri, (dv, keep, sarc) in enumerate(self._tail_rows):
            items.append((2, np.zeros((len(dv), 3)), dv, 170.0, ())); idx.append(("LT", ri))
        if L_.get("ok"):
            items.append((2, np.zeros((1, 3)), self._tip_dir[None], 170.0, ())); idx.append(("TIP", 0))
            items.append((1, np.zeros((len(self._lobe_d), 3)), self._lobe_d, 170.0, ())); idx.append(("LOBE", 0))
        res = self.needed(items, poses); Lq = {}
        for (nm, ri), r in zip(idx, res): Lq.setdefault(nm, []).append(r)
        Lq["E"] = [self._HE]
        self.Lneed = Lq
        self._greedy(keep0=keep1)
        if L_.get("ok"):
            # the roller and the lobe are ONE level (R_lobe): a pose whose roller-tip or lobe skin need lifts it more than
            # tip_tol mm above its base (1 mm over link 1b at K) is dropped (recorded as skin), else it would lift the
            # whole lobe + stub for every pose (measured: 5 state-A poses at q2 76-91 lifted the lobe 6.5 mm)
            keep = ~self.drop; fKk = H["hubK"][keep].max()
            base = (fKk if int(P.get("lobe_lev", 0)) == 1 else fKk + S.UP + S.T_LINK + 1.0); tol = float(P.get("tip_tol", 2.0))
            tipn = Lq["TIP"][0][:, 0]; lobn = Lq["LOBE"][0].max(1)
            self.drop |= (tipn - 1.0 > base + tol) | (lobn > base + tol)
        self.finalize()

    def finalize(self):
        D = self.D; P = D.p
        if P.get("emb_mode") != "kstub": return super().finalize()
        super(G.GModel, self).finalize()                          # hubs, links, E (the kit-rule chain)
        if not getattr(self, "_tail_rows", None): return
        keep = ~self.drop; L_ = D.law(); k = math.tan(S.RAMP * D2R); u2, uK = D.u[1], D.uK
        self._LT_need = self.Lneed.get("LT", []); self._TIP_need = self.Lneed.get("TIP", [None])[0]
        fK = self.fK; f2 = self.f[1]
        L1b = self.link_pts["L1b"][1]; dL = unit(L1b); rL1b = np.linalg.norm(L1b, axis=1)
        def stack_floor_pt(d):                                   # link 1b's top + 1 mm anywhere the stub tip sweeps (angle from u2)
            gT = math.degrees(math.acos(max(-1.0, min(1.0, float(d @ u2))))); gL_ = np.degrees(np.arccos(np.clip(dL @ u2, -1, 1)))
            sel = np.abs(gL_ - gT) <= 3.0 + math.degrees((BOSS_R + 1.0) / 65.0)
            return float((rL1b[sel] + S.T_LINK + 1.0).max()) if sel.any() else 0.0
        # lobe level: over link 1b's top (+1 mm) under its footprint, its own skin need, the roller's skin need - 1
        ld = self._lobe_d
        near = np.array([(rL1b[np.linalg.norm(dL - d, axis=1) * 65.0 <= 4.0 + 4.0] + S.T_LINK + 1.0).max(initial=0.0) for d in ld]) if len(ld) else np.zeros(0)
        lobe_need = self.Lneed["LOBE"][0][keep].max() if keep.any() else self.Lneed["LOBE"][0].max()
        tipneed = float(self._TIP_need[keep].max()) if self._TIP_need is not None and keep.any() else 0.0
        side = int(P.get("lobe_lev", 0)) == 1
        if side:
            # lobe at link 1a's own level at K (link 1a is the LOWER member at K), BESIDE link 1b (LOBE-L1b checks it);
            # the roller rides on an O2 post under the stub, which crosses link 1b (stack_floor) and the lobe (+1 mm)
            R_lobe = max(fK, float(np.max(lobe_need, initial=0.0)), tipneed - 0.5)
        else:
            R_lobe = max(fK + S.UP + S.T_LINK + 1.0, float(near.max(initial=0.0)), float(np.max(lobe_need, initial=0.0)), tipneed - 1.0)
        self._R_lobe = R_lobe
        ld = self._lobe_d = self._lobe_dirs(R_lobe)
        floor_tip = R_lobe + S.T_LINK + 1.0
        if side:
            floor_tip = max(floor_tip, float(stack_floor_pt(self._tip_dir)))
        self._floor_tip = floor_tip
        gL = np.degrees(np.arccos(np.clip(dL @ u2, -1, 1)))
        def stack_floor(dirs):
            gT = np.degrees(np.arccos(np.clip(dirs @ u2, -1, 1))); out = np.zeros(len(dirs))
            for j, gg in enumerate(gT):
                sel = np.abs(gL - gg) <= 3.0
                if sel.any(): out[j] = (rL1b[sel] + S.T_LINK + 1.0).max() / max(float(dirs[j] @ unit(L1b[sel][np.argmax(rL1b[sel])])), 0.5)
            return out
        pts_all = []
        for (dv, keep_s, sarc), rr_ in zip(self._tail_rows, self._LT_need):
            r = (rr_[keep].max(0) if keep.any() else rr_.max(0)).copy(); Sx = sarc
            idx = np.nonzero(keep_s)[0]
            if not len(idx): continue
            j0 = idx[0]; rc = (f2 + S.UP) / max(float(dv[j0] @ u2), 0.2)
            r = np.maximum(r, rc - k * np.abs(Sx - Sx[j0]))
            r = np.maximum(r, np.where(np.linalg.norm(np.cross(dv * 65.0, u2), axis=1) > S.HUB_R + 4.0, stack_floor(dv), 0.0))
            # flat at the tip floor wherever lobe metal can pass under it (outside hub 2's 4 mm zone): the lobe turns
            # under the stub as K opens, so a ramp toward hub 2 would dip into it (measured: LOBE-LT on every law pose)
            Send = Sx[-1]; out2 = np.linalg.norm(np.cross(dv * 65.0, u2), axis=1) > S.HUB_R + 4.0
            r = np.maximum(r, np.where(out2, floor_tip, floor_tip - k * np.maximum(0.0, (S.HUB_R + 4.0) - np.linalg.norm(np.cross(dv * 65.0, u2), axis=1))))
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            pts_all.append(dv[keep_s] * r[keep_s][:, None])
        self.link_pts["LT"] = (2, np.concatenate(pts_all))
        rtip = R_lobe + 1.0 if not side else R_lobe + 0.25         # roller bottom: >= 2 mm overlap with the 3 mm lobe plate
        post = floor_tip - (rtip + ROLLER_H)                        # O2 post from the stub down to the roller (side level)
        e, f = S.frame_of(self._tip_dir); dd = S.disc(BOSS_R, 2.0)
        self.rigid["roller"] = (2, self._tip_dir * rtip + dd[:, :1] * e + dd[:, 1:] * f)
        self._roller_bottom = rtip
        self.rigid["lobe"] = (1, ld * R_lobe)
        self._contact_only(); self._solids()
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False); ring = BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
        self.contact.append((2, np.concatenate([self._tip_dir * z + ring for z in (rtip, rtip + ROLLER_H)])))
        self.contact.append((1, ld * (R_lobe + S.T_LINK)))
        self.strap["ROL"] = (2, np.concatenate([self._tip_dir * z + ring for z in np.linspace(rtip, max(rtip + ROLLER_H, floor_tip), 3 + int(max(0.0, post) // 1.5))]))
        self.strap["LOBE"] = (1, ld * (R_lobe + S.T_LINK / 2))
        # the roller's own disc at the lobe level (for ROL-LOBE in state A): radius rr
        self.strap["ROLC"] = (2, np.concatenate([self._tip_dir * z + (float(P["rr"]) / BOSS_R) * ring for z in np.linspace(rtip, rtip + ROLLER_H, 3)]))
        # report: physical stub length and closest stub-boss approach to hub K's axis over q2's whole range (link 1b's frame)
        rmid = rtip + ROLLER_H / 2; allp = np.r_[L_["pA"], np.einsum("nij,j->ni", S.rotm(u2, L_["q2t"]), L_["p0"])]
        self._stub_info = dict(lev="side" if side else "over", post_mm=round(max(0.0, post), 1), R_lobe=round(R_lobe, 1), roller_mid=round(rmid, 1), stub_len_mm=round(rmid * math.radians(L_["Lt"]), 1),
                               hubK_axis_min_mm=round(float((rmid * np.sin(np.arccos(np.clip(allp @ uK, -1, 1)))).min()), 2),
                               hubK_rim_gap_boss_mm=round(float((rmid * np.sin(np.arccos(np.clip(allp @ uK, -1, 1)))).min()) - S.HUB_R - BOSS_R, 2),
                               lobe_extent_mm=round(float((R_lobe * np.sin(np.arccos(np.clip(ld @ uK, -1, 1)))).max()), 1),
                               n_lobe=int(len(ld)))

    def collide(self, i):
        out = super().collide(i)
        if "LOBE" not in getattr(self, "strap", {}): return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def ss(A, Bq, extra=2 * h): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        LO = tf(*self.strap["LOBE"]); c = {}
        for hb in ("hub2", "hub3"): c[f"LOBE-{hb}"] = vcyl(LO, hb, h)
        strap = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1b", "L2", "LT")}
        c["LOBE-L1b"] = ss(far(LO, "hubK", 4), far(strap["L1b"], "hubK", 4))
        c["LOBE-L2"] = ss(LO, strap["L2"]); c["LOBE-LT"] = ss(LO, strap["LT"])
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]; c[f"{nm}-LOBE"] = float(self.sd_box(LO, cen, R, half).min()) - h
        Em = tf(*self.Emid); c["E-LOBE"] = ss(Em, LO)
        st = self.kstate[i] if hasattr(self, "kstate") else 0
        if st != 1:                                               # off the law the roller must stand clear of the lobe
            RC = tf(*self.strap["ROLC"]); c["ROL-LOBE"] = ss(RC, LO, h)
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


KR.KB.KModel = KSModel


def _report(B, params):
    p = dict(PARAMS, **params)
    r, M = G._report(B, p)
    if "drive" in r:
        L_ = M.D.law()
        r["drive"]["stub"] = getattr(M, "_stub_info", None)
        r["drive"]["rho_min"] = round(L_["rho_min"], 2) if L_.get("rho_min") is not None else None
        r["drive"]["hubK_nom_min"] = round(L_.get("hubK_min_nom", 0.0), 2)
        if hasattr(M, "link_pts") and "lobe" in getattr(M, "rigid", {}):
            tk = [i for i in range(len(B.idx)) if B.kind[i] == "clip" and B.res[i] is not None and float(np.min(B.res[i])) >= 0]
            if tk:
                dd = np.concatenate([B.dist(i, M.world(1, i, M.rigid["lobe"][1])) for i in tk[::3]])
                r["drive"]["LOBE_ib14"] = round(float(((dd >= 2) & (dd <= 14)).mean()), 3); r["drive"]["LOBE_med_mm"] = round(float(np.median(dd)), 1)
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    return KB.frozen(dict(PARAMS, **P), nc, nw)


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
