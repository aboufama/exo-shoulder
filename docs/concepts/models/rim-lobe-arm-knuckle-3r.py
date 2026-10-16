"""rim-lobe-arm-knuckle-3r: the verified winner geneva-tail-knuckle-pinknee-3r (rod embodiment: kit-rule B, pin knee,
phys q2 stop, near-touch objective, K slaved past the onset) with its drive REPLACED by a direct higher pair: link 1a
grows an integral lug that carries a follower (O5 roller, or an O3 pin in an O5 iglidur sleeve) at L_arm from K's axis,
and link 2 carries a 3 mm wire-EDM plate around hub 2 whose edge (roller) or slot (groove) drives the follower. No
rocker, no pushrod, no rod ends, no horn. 3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive
translations.

Loaded on docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py as its own module copy (its _ik_phys, kit fold rule,
continuity, VModel checks, capK cap, near-touch report and frozen() are reused unchanged); only law() and the metal
change.

THE LAW: dK = sp kK t over q2's stretched travel t past the onset q2hi (t grid 0..75 deg, 0.25 deg). The valid prefix
ends (= the q2 stop-B dowel) at the first t that fails: th monotone and rate dq2/dth <= 3.45, K <= stop B (a1max), no
lift-off (self-motion slope, as the parent), and the EXACT PAIR GATES computed on the sphere (all axes through GH, pitch
level r_law mm):
  * arm tip at stop A (link 1a frame): p_arm = R(uK, a0) R(uK x u2, L_arm / r_law) uK  (a0 = 0 aims it at J2);
  * link 1b frame: P(t) = R(uK, -dK(t)) p_arm; link 2 frame (the pitch curve): C(t) = R(u2, -q2(t)) P(t);
  * follower velocity v_f = dP/dt, cam velocity at P v_c = s_q u2 x P, relative v_r = v_f - v_c; contact normal n is
    perpendicular to v_r in the tangent plane, oriented n . v_f > 0; pressure angle pa = asin(|v_r^ . v_f^|) <= pa_max;
  * roller: the lobe material lies on the -n side and must face u2 (n points away from u2: a connected spiral lobe off
    link 2's ring); the convex pitch radius >= rr + 1 (no undercut); the follower clears hub 2's housing (pitch radius
    from u2 >= HUB_R + rr + 1);
  * lap check: the lobe material samples never come within rr - 0.3 mm of the follower centre at ANY q2 from the fold
    stop through the law (state A: K on stop A, the lobe turned away).
Groove: the slot (pitch +/- 2.6, walls 1.5: band +/- 4.1) runs over the dwell (C = R(u2, -q2) p_arm for every state-A
q2 from the fold stop q2lo to q2hi) and the rise; positive both ways (no spring, no stop A, capK 0, lift-off moot).

THE METAL (sampled like a link: skin, in band, near-touch, every part pair):
  * LUG (member 1, link 1a): an 8 mm strap (rows -3, -1, 1, 3) on the great circle from hub K's rim to L_arm + 3.5,
    skin-fitted with 60-deg ramps, joined to link 1a's level at hub K;
  * PLATE (member 2, link 2): FLAT 3 mm plate perpendicular to u2 (one level h_p along u2), every lobe / slot sample
    (2 mm grid) from hub 2's rim out to the cam surface (roller) or the slot band (groove);
  * FOLLOWER (member 1): O5 x 3 roller (MR52ZZ 2.5 + washer) / O5 sleeve, in the plate's layer.
  Layering (param lay):
  * 'low' (the designer's choice): the lug is the BOTTOM layer (skin-fitted), the follower stands up from its tip into
    the plate's layer: plate underside = lug-tip top + 1.0 (non-adjacent 1 mm), raised if the plate's own floors
    (link 2's ring level f2 + UP, link 1b's top + 1 over the plate's whole sweep about u2, the plate's skin need) are
    higher - then the lug tip rises with it;
  * 'high' (the spec's control): plate at its floors; the follower hangs from the lug into the plate's layer; lug
    underside >= plate top + 1.0 wherever the lug is inside the plate's swept radius; lug >= link 1b's top + 1 over
    its swing about uK.
  Pairs checked per pose (>= 1 mm): LUG vs hub 1 / hub 2 / hub 3 / L1b (outside hub K's zone + 4) / L2 / knee / pad /
  E / PLATE; PLATE vs hub 1 / hub K (incl. its cap) / hub 3 / L1a / L1b (outside hub 2's zone + 4) / knee / pad / E;
  FOLLOWER vs hub 1 / hub 2 / hub K / hub 3 / L1b / L2 / knee / pad / E.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/rim-lobe-arm-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/rim-lobe-arm-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("geneva_for_rimlobe", os.path.join(HERE, "geneva-tail-knuckle-pinknee-3r.py"))
G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
KR, KB, PK, S = G.KR, G.KB, G.PK, G.S
unit = S.unit; D2R = math.pi / 180
ID = "rim-lobe-arm-knuckle-3r"
RATE_MAX = G.RATE_MAX
FOLL_H = 3.0                                                  # MR52ZZ 2.5 wide + washer / O5 x 3 sleeve

# the verified winner's chain (rows/geneva-tail-knuckle-pinknee-3r.json best_params) with the judge's law (kK 0.6, smhi 28)
WIN = {"bk1": 31.2491, "bk2": 37.9937, "a1max": 58.3565, "smhi": 13.6865, "smlo": 5.2777, "az1": 93.5546, "el1": 67.3642,
       "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863,
       "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "capK": 6.0}
PARAMS = dict(G.PARAMS, **WIN)
PARAMS.update(cam=1, tail=1, emb_mode="pair", emb="roller", lay="low", kK=0.6, smhi=28.0, L_arm=23.5, a0=2.0, rr=2.5,
              r_law=62.0, pa_max=45.0, t_end=75.0, rho_max=1e9)


def _rot(ax, a):
    return S.rotm(ax, a)


class RLDesign(G.GDesign):
    def law(self):
        if getattr(self, "_law", None) is not None: return self._law
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg)
        def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        kK = float(P["kK"]); r = float(P["r_law"]); rr = float(P["rr"]); groove = P.get("emb") == "groove"
        ts = np.radians(np.arange(0.0, float(P.get("t_end", 75.0)) + 1e-9, 0.25)); q2t = q2hi + s_q * ts
        dK = sp * kK * ts
        RK = S.rotm(uK, dK); R2 = S.rotm(u2, q2t)
        th = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, np.einsum("nij,j->ni", R2, u3)) @ u1, -1, 1)))
        kabs = np.abs(dK); dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
        h = 1e-4
        def th_of(tt, kk):
            R = S.rotm(uK, sp * kk); R2_ = S.rotm(u2, q2hi + s_q * tt)
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
        lift = (sC > 1e-9) & (sC < dk - 1e-9) & (not groove)
        rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
        # --- the exact pair on the sphere ---
        axK2 = unit(np.cross(uK, u2)); p_arm = S.rotm(uK, float(P["a0"]) * D2R)[0] @ (S.rotm(axK2, float(P["L_arm"]) / r)[0] @ uK)
        Pt = np.einsum("nji,j->ni", RK, p_arm)                    # R(uK, -dK) p_arm = RK^T p_arm
        vf = -sp * kK * np.cross(uK, Pt); vc = s_q * np.cross(u2, Pt); vr = vf - vc
        n = np.cross(Pt, vr); n = n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
        n = np.where((np.einsum("ij,ij->i", n, vf) < 0)[:, None], -n, n)
        vfn = vf / np.maximum(np.linalg.norm(vf, axis=1), 1e-12)[:, None]; vrn = vr / np.maximum(np.linalg.norm(vr, axis=1), 1e-12)[:, None]
        pa = np.degrees(np.arcsin(np.clip(np.abs(np.einsum("ij,ij->i", vrn, vfn)), 0, 1)))
        tout = (Pt @ u2)[:, None] * Pt - u2; tout = tout / np.maximum(np.linalg.norm(tout, axis=1), 1e-12)[:, None]
        side = np.einsum("ij,ij->i", n, tout)                      # > 0: n points away from u2 (material toward u2)
        rho = np.arccos(np.clip(Pt @ u2, -1, 1)) * r                 # follower centre's distance from u2 (mm)
        Rm = S.rotm(u2, -q2t); C = np.einsum("nij,nj->ni", Rm, Pt); nc = np.einsum("nij,nj->ni", Rm, n)
        e2, f2_ = S.frame_of(u2)
        def plan(X):
            g = np.arccos(np.clip(X @ u2, -1, 1)) * r; az = np.arctan2(X @ f2_, X @ e2); return np.c_[g * np.cos(az), g * np.sin(az)]
        xy = plan(C); xn = plan(unit(C + 1e-3 * nc)) - xy; xn = xn / np.maximum(np.linalg.norm(xn, axis=1), 1e-12)[:, None]
        d1 = np.gradient(xy, axis=0); d2 = np.gradient(d1, axis=0)
        kap = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.maximum(np.linalg.norm(d1, axis=1) ** 3, 1e-12)
        NL = np.c_[-d1[:, 1], d1[:, 0]] / np.maximum(np.linalg.norm(d1, axis=1), 1e-12)[:, None]
        cen_side = np.sign(kap) * np.einsum("ij,ij->i", NL, xn)       # < 0: centre of curvature on the material side (convex)
        rad = 1.0 / np.maximum(np.abs(kap), 1e-9)
        convex_bad = (cen_side < 0) & (rad < rr + 1.0)
        good = (dth > 0) & (rate <= RATE_MAX) & ~lift & (kabs <= dKB + 1e-9) & (pa <= float(P["pa_max"])) & (rho >= S.HUB_R + rr + 1.0)
        good &= rho <= float(P.get("rho_max", 1e9))                 # plate size cap: the law (q2 stop B) ends where the follower passes rho_max
        if not groove: good &= (side > 0.05) & ~convex_bad
        good[0] = True
        if not (pa[0] <= float(P["pa_max"]) and rho[0] >= S.HUB_R + rr + 1.0 and (groove or side[0] > 0.05)): good[:] = False
        nval = int(np.argmin(good)) if not good.all() else len(good)
        why_end = None
        if nval < len(good):
            j = nval
            why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "liftoff" if lift[j] else "stopB" if kabs[j] > dKB else
                       "pressure" if pa[j] > float(P["pa_max"]) else "hub2" if rho[j] < S.HUB_R + rr + 1.0 else "rho_max" if rho[j] > float(P.get("rho_max", 1e9)) else "side" if side[j] <= 0.05 else "undercut")
        L = dict(ok=nval > 4, ts=ts[:nval], q2t=q2t[:nval], dK=dK[:nval], th=th[:nval], pa=pa[:nval], rate=rate[:nval], emb=P.get("emb"),
                 q2hi=q2hi, s_q=s_q, why_end=why_end, r_c=np.zeros(nval), side=0.0, Lt=0.0, phi_t=None,
                 dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                 th_max=float(th[nval - 1]) if nval else None, p_arm=p_arm)
        if not L["ok"]:
            self._law = L; return L
        C, nc, Pt = C[:nval], nc[:nval], Pt[:nval]
        L["rho_mm"] = (float(rho[0]), float(rho[nval - 1])); L["min_convex_r"] = float(rad[:nval][cen_side[:nval] < 0].min()) if (cen_side[:nval] < 0).any() else None
        # --- plate material directions (link 2 frame, unit vectors) ---
        q2lo = math.radians(self.q2_stops[0]) if getattr(self, "q2_stops", None) else q2hi - s_q * math.radians(100)
        g_ring = (S.HUB_R + 0.5) / r
        mats = []
        if not groove:
            Sx = unit(C - (rr / r) * nc)                                    # cam surface (unit), material inward
            for k in range(0, nval, 2):
                gs = math.acos(float(np.clip(Sx[k] @ u2, -1, 1)))
                if gs <= g_ring: continue
                axr = unit(np.cross(u2, Sx[k])); m = max(2, int(math.ceil((gs - g_ring) * r / 2.0)) + 1)
                for gg in np.linspace(g_ring, gs, m): mats.append(S.rotm(axr, gg)[0] @ u2)
            edge = Sx
        else:
            dq = q2hi - q2lo; nd = max(4, int(abs(math.degrees(dq)) / 1.0))
            Cd = np.einsum("nij,j->ni", S.rotm(u2, -(q2lo + np.linspace(0, 1, nd) * dq)), p_arm)
            band = np.r_[Cd, C]
            for k in range(len(band)):
                gb = math.acos(float(np.clip(band[k] @ u2, -1, 1))); axr = unit(np.cross(u2, band[k]))
                for off in (-4.1, -2.8, 2.8, 4.1):                              # the slot's two 1.5-mm walls
                    gg = gb + off / r
                    if gg > g_ring: mats.append(S.rotm(axr, gg)[0] @ u2)
            edge = None
        mats = np.array(mats) if mats else np.zeros((0, 3))
        if len(mats):                                                       # thin to ~1 sample / 2 mm
            keep = []; tree = None; Xm = mats * r
            order = np.arange(len(mats)); sel = np.ones(len(mats), bool)
            tr = cKDTree(Xm)
            for i_ in order:
                if not sel[i_]: continue
                keep.append(i_)
                for j_ in tr.query_ball_point(Xm[i_], 1.6):
                    if j_ != i_: sel[j_] = False
            mats = mats[keep]
        L["plate_dirs"] = mats
        # --- lap / undercut check: follower centre path in link 2's frame vs the material (roller only) ---
        if not groove and len(mats):
            qA = q2lo + np.linspace(0, 1, 120) * (q2hi - q2lo)
            pathA = np.einsum("nij,j->ni", S.rotm(u2, -qA), p_arm)
            path = np.r_[pathA, C]
            dmin = cKDTree(mats * r).query(path * r)[0]
            dense = cKDTree(np.r_[mats, edge] * r).query(path * r)[0] if edge is not None else dmin
            L["lap_min_mm"] = float(min(dmin.min(), dense.min()))
            if L["lap_min_mm"] < rr - 0.3:
                L["ok"] = False; L["why_end"] = "lap"
        # sector (deg of link 2) spanned by the plate
        if len(mats):
            az = np.degrees(np.arctan2(mats @ f2_, mats @ e2)); az = np.sort(np.mod(az, 360)); gaps = np.diff(np.r_[az, az[0] + 360])
            L["sector_deg"] = float(360 - gaps.max())
            L["plate_rmax_mm"] = float(np.degrees(np.arccos(np.clip(mats @ u2, -1, 1))).max() * D2R * r)
        self._law = L
        return L


G.KR.KB.KDesign = RLDesign


class RLModel(G.GModel):
    def fit(self):
        D = self.D; P = D.p; self._tail_rows = None
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
        L_ = D.law(); self._pair_ok = bool(L_.get("ok"))
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        if self._pair_ok:
            self._lug_rows = self._lug_geom(L_)
            for ri, (dv, sarc) in enumerate(self._lug_rows):
                items.append((1, np.zeros((len(dv), 3)), dv, 170.0, ())); idx.append(("LUG", ri))
            pd = L_["plate_dirs"]
            if len(pd): items.append((2, np.zeros((len(pd), 3)), pd, 170.0, ())); idx.append(("PLATE", 0))
            items.append((1, np.zeros((1, 3)), unit(L_["p_arm"])[None], 170.0, ())); idx.append(("FOLL", 0))
        res = self.needed(items, poses); Lq = {}
        for (nm, ri), r in zip(idx, res): Lq.setdefault(nm, []).append(r)
        Lq["E"] = [self._HE]
        self.Lneed = Lq
        self._greedy(keep0=keep1)
        self.finalize()

    def _lug_geom(self, L_):
        """LUG rows (link 1a frame): great circle from uK to the arm tip + 3.5 mm, 8 mm wide (rows -3, -1, 1, 3)"""
        D = self.D; uK = D.uK; r = float(D.p["r_law"]); tip = unit(L_["p_arm"])
        ang = math.acos(float(np.clip(uK @ tip, -1, 1))); bn = unit(np.cross(uK, tip))
        a_end = ang + 3.5 / r; a0 = S.HUB_R / r
        nn = max(4, int((a_end - a0) * r / S.SPACING) + 1); ss = np.linspace(a0, a_end, nn)
        dirs = np.array([S.rotm(bn, s)[0] @ uK for s in ss]); rows = []
        for v in (-3.0, -1.0, 1.0, 3.0):
            dv = unit(dirs + (v / r) * np.cross(dirs, bn) * -1.0); rows.append((dv, ss * r))
        self._lug_tip_s = ang * r
        return rows

    def finalize(self):
        super().finalize()
        D = self.D; P = D.p
        if not getattr(self, "_pair_ok", False) or "LUG" not in self.Lneed: return
        keep = ~self.drop; L_ = D.law(); k = math.tan(S.RAMP * D2R); u2, uK = D.u[1], D.uK
        fK, f2 = self.fK, self.f[1]; low = P.get("lay", "low") == "low"
        pd = L_["plate_dirs"]; c2 = pd @ u2
        def kmax(M): return M[keep].max(0) if keep.any() else M.max(0)
        need_pl = kmax(self.Lneed["PLATE"][0]) if "PLATE" in self.Lneed else np.zeros(0)
        need_f = float(kmax(self.Lneed["FOLL"][0])[0])
        # link 1b's samples (its own frame = link 2's frame up to the rotation about u2): the plate sweeps over every L1b sample
        # at the same distance from u2 -> plate underside >= that sample's top + 1 (outside hub 2's 4-mm zone)
        L1b = self.link_pts["L1b"][1]; rL = np.linalg.norm(L1b, axis=1); gL = np.arccos(np.clip(unit(L1b) @ u2, -1, 1))
        offL = np.linalg.norm(L1b - (L1b @ u2)[:, None] * u2, axis=1)
        gP = np.arccos(np.clip(c2, -1, 1))
        hfloor = (f2 + S.UP) * np.ones(len(pd))                       # link 2's ring level (plane along u2)
        hstack = np.zeros(len(pd))
        for j in range(len(pd)):
            sel = (np.abs(gL - gP[j]) * 62.0 <= 3.0) & (offL > S.HUB_R + 4.0)
            if sel.any(): hstack[j] = float(((rL[sel] + S.T_LINK + 1.0) * (unit(L1b[sel]) @ u2)).max())
        h_pl = float(max(hfloor.max(), hstack.max() if len(hstack) else 0.0, (need_pl * c2).max() if len(need_pl) else 0.0))
        # lug: skin need per row, ramps, joined to link 1a's level at K (fK), tip constraints by layering
        rows = self._lug_rows; Lneed = self.Lneed["LUG"]; tip_s = self._lug_tip_s
        cfo = float(unit(L_["p_arm"]) @ u2)
        def lug_levels(tip_lo):
            out = []
            for (dv, sarc), rn in zip(rows, Lneed):
                rr_ = kmax(rn).copy()
                rr_ = np.maximum(rr_, (fK / max(float(dv[0] @ uK), 0.2)) - k * np.abs(sarc - sarc[0]))
                near_tip = sarc >= tip_s - 4.0
                rr_ = np.where(near_tip, np.maximum(rr_, tip_lo), rr_)
                rr_ = np.max(rr_[None, :] - k * np.abs(sarc[:, None] - sarc[None, :]), axis=1)
                out.append(rr_)
            return out
        if low:
            # the follower stands on the lug tip; plate underside = lug-tip top + 1 (radially at the follower)
            lev = lug_levels(0.0); tip_u = max(float(r_[-3:].max()) for r_ in lev)
            plate_need_at_f = h_pl / max(cfo, 0.2)                    # plate underside radius at the follower
            tip_u = max(tip_u, plate_need_at_f - S.T_LINK - 1.2)
            lev = lug_levels(tip_u)
            h_pl = max(h_pl, (tip_u + S.T_LINK + 1.2) * cfo)
            foll_bot = tip_u + S.T_LINK + 0.5
        else:
            # plate at its floors; follower hangs into its layer from the lug; lug >= plate top + 1 where it is over the plate's sweep
            rmax = L_.get("plate_rmax_mm", 0.0) + 1.0
            tip_lo = (h_pl + S.T_LINK + 1.2) / max(cfo, 0.2)
            lev = lug_levels(tip_lo)
            # stack over link 1b along the lug (K swing about uK): L1b top + 1 at the same distance from uK
            gLK = np.arccos(np.clip(unit(L1b) @ uK, -1, 1)); offK = np.linalg.norm(L1b - (L1b @ uK)[:, None] * uK, axis=1)
            for ri, ((dv, sarc), rr_) in enumerate(zip(rows, lev)):
                gR = np.arccos(np.clip(dv @ uK, -1, 1)); add = np.zeros(len(dv))
                for j in range(len(dv)):
                    sel = (np.abs(gLK - gR[j]) * 62.0 <= 3.0) & (offK > S.HUB_R + 4.0)
                    if sel.any(): add[j] = float(((rL[sel] + S.T_LINK + 1.0)).max())
                rr_ = np.maximum(rr_, add); lev[ri] = np.max(rr_[None, :] - k * np.abs(sarc[:, None] - sarc[None, :]), axis=1)
            foll_bot = h_pl / max(cfo, 0.2)
        foll_bot = max(foll_bot, need_f)
        self._pair_lv = dict(plate_h=round(h_pl, 1), plate_floor_ring=round(float(hfloor.max()), 1), plate_floor_L1b=round(float(hstack.max()) if len(hstack) else 0.0, 1),
                             plate_skin=round(float((need_pl * c2).max()) if len(need_pl) else 0.0, 1), lug_tip=round(max(float(r_[-3:].max()) for r_ in lev), 1),
                             lug_max=round(max(float(r_.max()) for r_ in lev), 1), foll_bot=round(foll_bot, 1), fK=round(float(fK), 1), f2=round(float(f2), 1))
        lug = np.concatenate([dv * r_[:, None] for (dv, _), r_ in zip(rows, lev)])
        plate = pd * (h_pl / np.maximum(c2, 0.2))[:, None]
        self.rigid["lug"] = (1, lug); self.rigid["plate"] = (2, plate)
        fo = unit(L_["p_arm"]); e, f = S.frame_of(fo); dd = S.disc(2.5, 1.5)
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False); ring = 2.5 * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
        foll = np.concatenate([fo * z + ring for z in np.linspace(foll_bot, foll_bot + FOLL_H, 3)])
        if not low: self.rigid["foll"] = (1, fo * foll_bot + dd[:, :1] * e + dd[:, 1:] * f)
        self.contact.append((1, lug + S.T_LINK * unit(lug))); self.contact.append((2, plate + S.T_LINK * u2[None]))
        self.contact.append((1, foll))
        self.strap["LUG"] = (1, lug + (S.T_LINK / 2) * unit(lug)); self.strap["PLATE"] = (2, plate + (S.T_LINK / 2) * u2[None])
        self.strap["FOLL"] = (1, foll)

    def collide(self, i):
        out = super().collide(i)
        if "LUG" not in self.strap: return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        LUG = tf(*self.strap["LUG"]); PL = tf(*self.strap["PLATE"]); FO = tf(*self.strap["FOLL"]); c = {}
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def ss(A, Bq, extra=2 * h): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        capK = float(self.p.get("capK", 0) or 0)
        def vcylK(X, extra=0.0):
            cc, ax = cyl["hubK"]; w = X - cc; z = w @ ax; rr_ = np.linalg.norm(w - z[:, None] * ax, axis=1)
            dr = rr_ - S.HUB_R; dz = np.maximum(-z, z - (S.CROWN + capK))
            d = np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz)); return float(d.min()) - extra
        st = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1a", "L1b", "L2")}
        for hb in ("hub1", "hub2", "hub3"): c[f"LUG-{hb}"] = vcyl(LUG, hb, h)
        c["LUG-L1b"] = ss(far(LUG, "hubK", 4), far(st["L1b"], "hubK", 4)); c["LUG-L2"] = ss(LUG, st["L2"]); c["LUG-PLATE"] = ss(LUG, PL)
        for hb in ("hub1", "hub3"): c[f"PL-{hb}"] = vcyl(PL, hb, h)
        c["PL-hubK"] = vcylK(PL, h)
        c["PL-L1a"] = ss(PL, st["L1a"]); c["PL-L1b"] = ss(far(PL, "hub2", 4), far(st["L1b"], "hub2", 4))
        for hb in ("hub1", "hub2", "hub3"): c[f"FO-{hb}"] = vcyl(FO, hb)
        c["FO-hubK"] = vcylK(FO); c["FO-L1b"] = ss(FO, st["L1b"], h); c["FO-L2"] = ss(FO, st["L2"], h)
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]
            c[f"{nm}-LUG"] = float(self.sd_box(LUG, cen, R, half).min()) - h; c[f"{nm}-PL"] = float(self.sd_box(PL, cen, R, half).min()) - h
            c[f"{nm}-FO"] = float(self.sd_box(FO, cen, R, half).min())
        Em = tf(*self.Emid); c["E-LUG"] = ss(Em, LUG); c["E-PL"] = ss(Em, PL); c["E-FO"] = ss(Em, FO, h)
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


G.KR.KB.KModel = RLModel


def _report(B, params):
    p = dict(PARAMS, **params)
    if p.get("emb") == "groove": p.setdefault("capK", 0.0)
    r, M = G._report(B, p)
    D = M.D; L_ = D.law()
    dr = r.get("drive", {}) or {}
    dr.update(emb=p.get("emb"), lay=p.get("lay"), why_end=L_.get("why_end"), lap_min_mm=round(L_["lap_min_mm"], 2) if L_.get("lap_min_mm") is not None else None,
              rho_mm=[round(x, 1) for x in L_.get("rho_mm", ())], min_convex_r=round(L_["min_convex_r"], 2) if L_.get("min_convex_r") is not None else None,
              sector_deg=round(L_.get("sector_deg", 0.0), 1), plate_rmax_mm=round(L_.get("plate_rmax_mm", 0.0), 1),
              n_plate=int(len(L_.get("plate_dirs", ()))), levels=getattr(M, "_pair_lv", None))
    r["drive"] = dr
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(Pp, nc=110, nw=360):
    p = dict(PARAMS, **Pp)
    if p.get("emb") == "groove": p.setdefault("capK", 0.0)
    return KB.frozen(p, nc, nw)


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/rim-lobe-arm-knuckle-3r.js"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, par); D = M.D; P = D.p; L_ = D.law()
    R = lambda v, n=5: [round(float(x), n) for x in v]
    def pts(name, step=3):
        X = M.link_pts[name][1]; return [R(x, 2) for x in X[::step]]
    sub = slice(None, None, 8)
    lv = getattr(M, "_pair_lv", {}) or {}
    fo = unit(L_["p_arm"]) * (lv.get("foll_bot", M.fK) + FOLL_H / 2)
    G_ = dict(u=[R(x) for x in D.u], c=[R(x) for x in D.c], uK=R(D.uK), sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
              branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), capK=float(P.get("capK", 0)),
              tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3), RUN=S.RUN, A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]), eE=R(M.fr["eE"]),
              psiA=round(math.degrees(D.psiA), 4), thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(x, 4) for x in D.q2_stops],
              lawTh=R(L_["th"][sub], 3), lawDK=R(np.degrees(L_["dK"][sub]), 3), lawQ2=R(np.degrees(L_["q2t"][sub]), 3), emb=P.get("emb"),
              foll=R(fo, 2), lug=[R(x, 2) for x in M.rigid["lug"][1][::4]] if "lug" in M.rigid else [],
              plate=[R(x, 2) for x in M.rigid["plate"][1][::3]] if "plate" in M.rigid else [],
              L1a=pts("L1a"), L1b=pts("L1b"), L2=pts("L2", 6))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "a1max", "smhi", "smlo", "capK",
            "emb", "lay", "kK", "L_arm", "a0", "rr", "rho_max")
    return dict(P={k: P[k] for k in keys}, G=G_, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")})


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
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
