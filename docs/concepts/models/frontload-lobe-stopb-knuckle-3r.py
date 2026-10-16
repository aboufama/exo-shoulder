"""frontload-lobe-stopb-knuckle-3r: the verified winner geneva-tail-knuckle-pinknee-3r (rod embodiment: kit-rule B, pin
knee, physical q2 stop, near-touch objective, K slaved past the onset by a hub-2 rim lobe -> rocker -> O3 pushrod -> horn
on K's cap) with two changes, no new joint:
  (a) K's stop B may move up to the K dyad's 5-deg margin: a1max <= bk1 + bk2 - 5 (the winner sits at 58.4, 10.9 short);
  (b) the rim lobe is re-cut FRONT-LOADED: K opens fast just past the onset, then slower. Two laws:
      * 'seg'   : |dK| = kA min(t, t1) + kB max(0, t - t1)  (t = q2 travel past the onset q2hi);
      * 'track' : |dK|(t) = the smallest opening that holds the effective dyad margin m3e = a1e + a2 - th at >= smt,
                  integrated forward with the gain clipped to the pressure-angle cap (monotone, never closes);
      * 'lin'   : the winner's dK = kK t (control).
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations.

THE 2:1 ROCKER (mandatory, lead note): the follower rides the lobe on the rocker's SHORT arm (5 mm), the rod end sits on
the LONG arm (5 i_rock mm), so for a lobe of base radius r_lobe and lift s(t):
    rod travel = r_horn |dK|,  follower lift s = r_horn |dK| / i_rock,  lobe radius r(t) = r_lobe + s(t),
    tan(pa(t)) = k(t) r_horn / (i_rock r(t)),  k(t) = d|dK|/dq2,   pa(t) <= pa_max (45),
and r_horn >= 2.45 (0.05 mm of rod-end play reads as <= 1.2 deg of K slop; at r_horn 1-1.5 it is 2-3 deg).
Extra per-t gates on the law prefix (the parent's stay: th monotone, rate dq2/dth <= 3.45, K <= stop B, no lift-off):
  * skirt: the lobe's outer radius r(t) <= HUB_R (the lobe stays inside hub 2's sampled O20 envelope);
  * r_horn >= 2.45, i_rock in [1, 2.5] (param clamps, reported).
The rocker's long arm (O10 x 9 boss as the parent + a 10 x 4 x 3 arm from the boss top along the tangent normal to the
rod, rod end at its tip) is sampled metal on link 1b (skin, in band, near-touch, the parent's ROD pair checks).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("geneva_for_frontload", os.path.join(HERE, "geneva-tail-knuckle-pinknee-3r.py"))
G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)
KR, KB, PK, S = G.KR, G.KB, G.PK, G.S
unit = S.unit; D2R = math.pi / 180
ID = "frontload-lobe-stopb-knuckle-3r"
RATE_MAX = G.RATE_MAX
R_HORN_MIN, I_ROCK_MAX, SHORT_ARM = 2.45, 2.5, 5.0

# the verified winner (rows/geneva-tail-knuckle-pinknee-3r.json best_params)
WIN = {"emb_mode": "rod", "kK": 3.1796, "r_horn": 2.4932, "r_lobe": 9.0, "bk1": 31.2491, "bk2": 37.9937, "a1max": 58.3565,
       "smhi": 13.6865, "smlo": 5.2777, "az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337,
       "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534,
       "ang_min": 27.8544, "capK": 6.0, "tail": 1}
PARAMS = dict(G.PARAMS, **WIN)
PARAMS.update(law_mode="seg", kA=6.0, t1=6.0, kB=2.0, smt=12.0, i_rock=2.0, r_horn=2.5, r_lobe=8.0, a1max=64.2, t_end=75.0, arm_lo=1.0, crown_rule=1)


class FLDesign(G.GDesign):
    def law(self):
        P = self.p
        if P.get("emb_mode") != "rod" or P.get("law_mode", "seg") == "lin":
            if P.get("emb_mode") == "rod":                         # control: the winner's law, rocker ratio honoured
                P["rod_low"] = 1 if float(P.get("i_rock", 1.0)) != 1.0 else P.get("rod_low", 0)
            return super().law()
        if getattr(self, "_law", None) is not None: return self._law
        u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg)
        def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        ir = min(max(float(P["i_rock"]), 1.0), I_ROCK_MAX); rh = max(float(P["r_horn"]), R_HORN_MIN); rl0 = float(P["r_lobe"])
        P["i_rock"], P["r_horn"] = ir, rh
        tpa = math.tan(float(P["pa_max"]) * D2R)
        dt = 0.1; ts = np.radians(np.arange(0.0, float(P.get("t_end", 75.0)) + 1e-6, dt)); q2t = q2hi + s_q * ts
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (
            math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))

        def th_of(tt, kk):
            R = S.rotm(uK, sp * np.asarray(kk)); R2_ = S.rotm(u2, q2hi + s_q * np.asarray(tt))
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))

        def a1e_of(kk):
            return np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", S.rotm(uK, sp * np.asarray(kk)), u2) @ u1, -1, 1)))

        mode = P.get("law_mode", "seg")
        if mode == "seg":
            t1 = float(P["t1"]) * D2R
            kabs = float(P["kA"]) * np.minimum(ts, t1) + float(P["kB"]) * np.maximum(0.0, ts - t1)
        else:                                                      # 'track': hold m3e >= smt with the least opening
            kgrid = np.radians(np.arange(0.0, math.degrees(dKB) + 0.2, 0.2)); nk = len(kgrid)
            a1g = a1e_of(kgrid)
            TT = np.repeat(ts, nk); KK = np.tile(kgrid, len(ts))
            thg = th_of(TT, KK).reshape(len(ts), nk)
            m3g = KR.dyad_margin(thg, a1g[None, :], self.a2)
            okg = m3g >= float(P["smt"])
            first = np.where(okg.any(1), np.argmax(okg, 1), nk - 1)
            kneed = kgrid[first]
            kabs = np.zeros(len(ts)); kmax_rate = ir * rl0 * tpa / rh   # gain cap at the base radius (refined by the pa gate)
            for j in range(1, len(ts)):
                kabs[j] = min(max(kabs[j - 1], kneed[j]), kabs[j - 1] + kmax_rate * dt * D2R)
        dK = sp * kabs
        th = th_of(ts, kabs)
        a1e = a1e_of(kabs)
        lift_mm = rh * kabs / ir; r_t = rl0 + lift_mm
        k_t = np.gradient(kabs, ts)
        pa = np.degrees(np.arctan(k_t * rh / (ir * r_t)))
        dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
        h = 1e-4
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
        lift = (sC > 1e-9) & (sC < dk - 1e-9)
        rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
        skirt = r_t <= S.HUB_R + 1.5 + 1e-9                         # lobe crest inside hub 2's O20 + 1.5 (the winner's 11.3 passed)
        good = (dth > 0) & (rate <= RATE_MAX) & (pa <= float(P["pa_max"]) + 1e-9) & ~lift & (kabs <= dKB + 1e-9) & skirt
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good)
        why_end = None
        if nval < len(good):
            j = nval
            why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "pressure" if pa[j] > float(P["pa_max"]) + 1e-9 else
                       "liftoff" if lift[j] else "stopB" if kabs[j] > dKB + 1e-9 else "skirt" if not skirt[j] else "sign")
        m3_law = KR.dyad_margin(th, a1e, self.a2)
        self._law = dict(ok=nval > 1, side=0.0, Lt=0.0, p0=u2.copy(), ts=ts[:nval], q2t=q2t[:nval], dK=dK[:nval], th=th[:nval],
                         pa=pa[:nval], r_c=np.zeros(nval), rate=rate[:nval], emb="rod", q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=1.0,
                         dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                         th_max=float(th[nval - 1]) if nval else None, phi_t=None, dKB=float(np.degrees(dKB)),
                         lobe_r_max=float(r_t[:nval].max()) if nval else rl0, lift_max=float(lift_mm[:nval].max()) if nval else 0.0,
                         m3e_min=float(m3_law[:nval].min()) if nval else None, k_max=float(k_t[:nval].max()) if nval else 0.0)
        return self._law


G.KR.KB.KDesign = FLDesign


class FLModel(G.GModel):
    def _rod_metal(self):
        """the parent's rod metal, with the 2:1 rocker: O10 x 9 boss on link 1b beside hub 2 (parent), a long arm
        5 i_rock mm x 4 x 3 from the boss top along the tangent normal to the rod (the side away from hub 2), the rod end on
        its tip, O3 rod to the horn on K's cap (r_horn, cap mid-height), M3 rod-end heads O10 x 5 at both ends"""
        D = self.D; P = D.p
        ir = float(P.get("i_rock", 1.0))
        if ir == 1.0 and not P.get("crown_rule", 1):               # 1:1 = the winner's post as the winner models it
            out = super()._rod_metal()
            u2, uK = D.u[1], D.uK; g0 = (S.HUB_R + 6.0) / max(self.f[1], 30.0); dR = unit(S.rotm(unit(np.cross(u2, uK)), g0)[0] @ u2)
            lev = self._rod_info["rocker_level"]; eK, _ = S.frame_of(uK)
            hornP = uK * (self.fK + S.CROWN + float(P.get("capK", 0) or 0) * 0.5) + float(P["r_horn"]) * eK
            self._viz_rod = dict(rocker=dR * lev, rockerAx=dR, rodA=dR * (lev + 9.0), rodB=hornP, armA=dR * (lev + 9.0), armB=dR * (lev + 9.0))
            return out
        u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]; capK = float(P.get("capK", 0) or 0)
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0)
        ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max()) + S.T_LINK
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        self.rigid["rocker"] = (7, dR * lev + dd[:, :1] * e + dd[:, 1:] * f)
        # long arm = a clevis fork (plates 1.5, M3 rod-end head 5 between them): its underside arm_lo above link 1b's top
        # (>= 1, washer), the rod-end eye (the rod line's start) at arm_lo + 4, the fork top at arm_lo + 8. The rod must
        # pass over hub K's crown: wherever the rod line is within HUB_R + 2 of K's axis its centre stays >= crown top + 2
        # (rod radius 1.5 + 0.5); arm_lo is raised in 0.5 steps until it does (reported as arm_lo_eff).
        La = SHORT_ARM * ir if ir > 1.0 else 0.0                   # 1:1: the rod end on the follower post (no arm)
        eK, _ = S.frame_of(uK); hornP = uK * (fK + S.CROWN + capK * 0.5) + float(P["r_horn"]) * eK
        crown_top = fK + S.CROWN
        arm_lo = min(max(float(P.get("arm_lo", 6.0)), 1.0), 7.5) if ir > 1.0 else 5.0   # 1:1: eye at lev + 9 (the winner's)
        while True:
            base = dR * (lev + arm_lo + 4.0)
            rd = unit(hornP - base); tp = unit(np.cross(dR, rd))
            cands = [base + s_ * max(La, 1e-3) * tp for s_ in (1.0, -1.0)]
            dist_u2 = [np.linalg.norm(c_ - (c_ @ u2) * u2) for c_ in cands]
            tip = cands[int(np.argmax(dist_u2))]
            sg_ = np.linspace(0, 1, 60)[:, None]; line = tip[None] * (1 - sg_) + hornP[None] * sg_
            rad = np.linalg.norm(line - (line @ uK)[:, None] * uK, axis=1); hz = line @ uK
            bad = (rad <= S.HUB_R + 2.0) & (hz < crown_top + 2.0)
            if not bad.any() or arm_lo >= 30.0: break
            arm_lo += 0.5
        self._crown_ok = not bad.any()
        self._arm_lo_eff = arm_lo
        self._viz_rod = dict(rocker=dR * lev, rockerAx=dR, rodA=tip, rodB=hornP, armA=base, armB=tip)
        tdir = unit(tip - base); bn = unit(np.cross(dR, tdir))
        ss = np.arange(0.0, La + 1e-6, 2.0) if La > 0 else np.zeros(0); ws_ = np.array([-1.5, 0.0, 1.5])
        arm = np.array([base + s_ * tdir + w_ * bn for s_ in ss for w_ in ws_]).reshape(-1, 3)
        self.rigid["rocker"] = (7, np.concatenate([self.rigid["rocker"][1], arm - 4.0 * dR]))   # + the fork's underside
        n = max(3, int(np.linalg.norm(hornP - tip) / S.SPACING)); sg = np.linspace(0, 1, n)[:, None]
        rod = tip[None] * (1 - sg) + hornP[None] * sg
        self.rigid["rod"] = (7, rod - 1.5 * unit(rod))
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        def ring(c, r, axv): a, b = S.frame_of(axv); return c + r * (np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b)
        ends = np.concatenate([ring(tip - 4.0 * dR, 5.0, dR), ring(hornP, 5.0, uK), ring(tip + 4.0 * dR, 5.0, dR), ring(hornP + 5.0 * uK, 5.0, uK)])
        hpost = max(9.0, arm_lo + 8.0) if La > 0 else arm_lo + 4.0      # the pin / post reaches the fork top (2:1) or the eye (1:1)
        cyl = np.concatenate([ring(dR * z, 5.0, dR) for z in np.linspace(lev, lev + hpost, max(4, int(hpost / 3) + 1))])
        self.rigid["rodends"] = (7, np.concatenate([ring(tip - 4.0 * dR, 5.0, dR), ring(hornP, 5.0, uK)]))
        self._contact_only(); self._solids()
        self.contact.append((7, np.concatenate([ends, cyl, rod + 1.5 * unit(rod), arm + 4.0 * dR])))
        self.strap["ROD"] = (7, np.concatenate([ends, cyl, rod, arm - 4.0 * dR, arm + 4.0 * dR]))
        self._rod_info = dict(rocker_level=round(lev, 1), horn_level=round(float(fK + S.CROWN + capK * 0.5), 1),
                              rod_len=round(float(np.linalg.norm(hornP - tip)), 1), arm_mm=round(La, 1), i_rock=ir, arm_lo_eff=arm_lo, post_mm=round(hpost, 1), crown_ok=self._crown_ok)


G.KR.KB.KModel = FLModel


def _clamp(p):
    """the component limits (CMA has no bounds): 2:1-class rocker 1-2.5 (< 1.05 -> the 1:1 post), horn >= 2.45, lobe base
    7-8.1 (inside the O20 skirt), gains >= 0, smt >= 5.2, a1max <= bk1 + bk2 - 5"""
    ir = float(p.get("i_rock", 1.0)); p["i_rock"] = 1.0 if ir < 1.05 else min(ir, I_ROCK_MAX)
    p["r_horn"] = max(float(p["r_horn"]), R_HORN_MIN); p["r_lobe"] = min(max(float(p["r_lobe"]), 7.0), 8.1)
    for k in ("kA", "kB", "kK"): p[k] = max(float(p[k]), 0.0)
    p["t1"] = max(float(p["t1"]), 0.5); p["smt"] = max(float(p["smt"]), 5.2); p["arm_lo"] = max(float(p.get("arm_lo", 1.0)), 1.0)
    p["a1max"] = min(float(p["a1max"]), float(p["bk1"]) + float(p["bk2"]) - 5.0)
    return p


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    a1lim = float(p["bk1"]) + float(p["bk2"]) - 5.0                # stop B at most at the K dyad's 5-deg margin
    r, M = G._report(B, p)
    L_ = M.D.law()
    if not getattr(M, "_crown_ok", True):                          # the rod cannot pass over hub K's crown: not buildable
        r["honest"] = False; r["crown_fail"] = True
    if "drive" in r:
        r["drive"].update(law_mode=p.get("law_mode"), i_rock=M.D.p.get("i_rock"), r_horn=M.D.p.get("r_horn"),
                          lobe_r_max=round(L_.get("lobe_r_max", 0.0), 2) if L_.get("lobe_r_max") else None,
                          lift_max=round(L_.get("lift_max", 0.0), 2) if L_.get("lift_max") is not None else None,
                          m3e_law_min=round(L_["m3e_min"], 2) if L_.get("m3e_min") is not None else None,
                          dKB=round(L_.get("dKB", 0.0), 1) if L_.get("dKB") else None, a1max=round(p["a1max"], 2), a1max_lim=round(a1lim, 2))
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    return KB.frozen(_clamp(dict(PARAMS, **P)), nc, nw)


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/frontload-lobe-stopb-knuckle-3r.js"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, par); D = M.D; P = D.p; L_ = D.law()
    R = lambda v, n=5: [round(float(x), n) for x in v]
    def pts(name, step=3):
        X = M.link_pts[name][1]; return [R(x, 2) for x in X[::step]]
    sub = slice(None, None, 8); vr = M._viz_rod
    G_ = dict(u=[R(x) for x in D.u], c=[R(x) for x in D.c], uK=R(D.uK), sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
              branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), capK=float(P.get("capK", 0)),
              tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3), RUN=S.RUN, A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]), eE=R(M.fr["eE"]),
              psiA=round(math.degrees(D.psiA), 4), thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(x, 4) for x in D.q2_stops],
              lawTh=R(L_["th"][sub], 3), lawDK=R(np.degrees(L_["dK"][sub]), 3), lawQ2=R(np.degrees(L_["q2t"][sub]), 3), emb="rod",
              rocker=R(vr["rocker"], 3), rockerAx=R(vr["rockerAx"]), rodA=R(vr["rodA"], 3), rodB=R(vr["rodB"], 3), armA=R(vr["armA"], 3), armB=R(vr["armB"], 3),
              L1a=pts("L1a"), L1b=pts("L1b"), L2=pts("L2", 6))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "a1max", "smhi", "smlo", "capK",
            "law_mode", "kA", "t1", "kB", "smt", "kK", "i_rock", "r_horn", "r_lobe", "arm_lo")
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
                          parts=r.get("parts_ib14"), secs=round(time.time() - t)), default=float))
