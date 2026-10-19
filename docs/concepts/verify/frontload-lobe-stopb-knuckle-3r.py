"""Independent verifier (skeptic) of frontload-lobe-stopb-knuckle-3r (the verified winner geneva-tail-knuckle-pinknee-3r,
rod embodiment, with a two-segment 'seg' lobe law, stop B up to bk1 + bk2 - 5 and re-fitted seats; best at i_rock 1.0,
i.e. the winner's 1:1 rocker post).

The claim's model (docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py) is loaded UNCHANGED as its own module copy
(its law, clamps, pin knee, stops and every check stay as claimed). What this harness changes (`corr`): the winner's
verified metal corrections (docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py), which the claim names as open:

  1. THE HORN LEAVES THE SPRING CAP. The claim still puts the horn's rod-end head at K's cap MID-height
     (fK + CROWN + capK / 2), inside the clock-spring housing (capK 6). Corrected: a 1.5 mm horn plate on the cap top,
     the rod centreline meets both O10 x 5 rod-end heads at mid-height.
  2. ROD vs HUB K's CAP. The claim's crown rule keeps the rod centre >= crown top + 2 within HUB_R + 2 of K's axis, but
     crown top = fK + CROWN ignores the 6 mm spring cap above it: a rod at crown + 2..3 runs through the cap. Corrected:
     the rocker post grows in 0.5 mm steps until the rod clears the cap cylinder (HUB_R, CROWN + capK) by >= 1 mm, and
     ROD-hubK is checked per pose at the 1 mm non-adjacent rule (RODK strap).
  3. CONTINUITY FLOOD FILL (connected_report of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py, unchanged).

The claim's best has i_rock 1.0 (no rocker arm), so the winner's corrected 1:1 metal applies exactly; a 2:1 config is
refused here (the 2:1 runs lost about 1.2 fast and are not the claim).

    CB_EXACT=1 python3 docs/concepts/verify/frontload-lobe-stopb-knuckle-3r.py wear <claim|corr> <bench|held> <out.json> [--flood]
    python3 docs/concepts/verify/frontload-lobe-stopb-knuckle-3r.py fit <claim|corr>
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


F = _load("frontload_claim_v", os.path.join(REPO, "docs", "concepts", "models", "frontload-lobe-stopb-knuckle-3r.py"))
G, KR, KB, PK, S = F.G, F.KR, F.KB, F.PK, F.S
unit = S.unit

BEST = {"law_mode": "seg", "kA": 2.9004, "t1": 6.9414, "kB": 2.7564, "i_rock": 1.0, "r_horn": 2.4709, "r_lobe": 7.3499, "a1max": 61.7215,
        "bk1": 30.0536, "bk2": 37.5707, "smhi": 14.7672, "smlo": 5.1723, "az1": 95.3594, "el1": 67.6187, "az2": 42.7487, "el2": 43.9031,
        "wd": 63.5262, "wa": -10.5604, "b3": 0.3825, "ang_min": 27.8606, "emb_mode": "rod", "capK": 6.0, "lE": 67.832, "lc": 25.8149,
        "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "crown_rule": 1}
HORN_PLATE, HEAD_H, HEAD_R = 1.5, 5.0, 5.0


class CorrModel(F.FLModel):
    def _rod_metal(self):
        D = self.D; P = D.p
        assert float(P.get("i_rock", 1.0)) == 1.0, "this harness corrects the 1:1 post only"
        u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]; capK = float(P.get("capK", 0) or 0)
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0)
        ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max()) + S.T_LINK
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        self.rigid["rocker"] = (7, dR * lev + dd[:, :1] * e + dd[:, 1:] * f)
        eK, _ = S.frame_of(uK)
        hornP = uK * (fK + S.CROWN + capK + HORN_PLATE) + float(P["r_horn"]) * eK
        b = hornP + 0.5 * HEAD_H * uK
        for hrk in np.arange(9.0, 40.01, 0.5):
            top = dR * (lev + hrk); a = top + 0.5 * HEAD_H * dR
            n = max(3, int(np.linalg.norm(b - a) / S.SPACING)); sg = np.linspace(0, 1, n)[:, None]
            rod = a[None] * (1 - sg) + b[None] * sg
            X = np.concatenate([rod - 1.5 * unit(rod)] + [rod + 1.5 * w for w in S.frame_of(unit(b - a))])
            if float(PK.Model.sd_cylr(X, uK * fK, uK, S.HUB_R, S.CROWN + capK).min()) >= 1.0: break
        self._rocker_h = float(hrk)
        self.rigid["rod"] = (7, rod - 1.5 * unit(rod))
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        def ring(c, r, axv): x, y = S.frame_of(axv); return c + r * (np.cos(ang)[:, None] * x + np.sin(ang)[:, None] * y)
        ends = np.concatenate([ring(top, HEAD_R, dR), ring(hornP, HEAD_R, uK), ring(top + HEAD_H * dR, HEAD_R, dR), ring(hornP + HEAD_H * uK, HEAD_R, uK)])
        cyl = np.concatenate([ring(dR * z, 5.0, dR) for z in np.linspace(lev, lev + hrk, max(4, int(hrk / 3) + 1))])
        plate = uK * (fK + S.CROWN + capK) + np.concatenate([ring(float(P["r_horn"]) * eK, rr, uK) for rr in (2.0, 4.0)])
        self.rigid["rodends"] = (7, np.concatenate([ring(top, HEAD_R, dR), ring(hornP, HEAD_R, uK)]))
        self._contact_only(); self._solids()
        self.contact.append((7, np.concatenate([ends, cyl, rod + 1.5 * unit(rod), plate + HORN_PLATE * uK])))
        self.strap["ROD"] = (7, np.concatenate([ends, cyl, rod, rod - 1.5 * unit(rod)]))
        self.strap["RODK"] = (7, np.concatenate([ring(hornP, HEAD_R, uK), ring(hornP + HEAD_H * uK, HEAD_R, uK), rod, rod - 1.5 * unit(rod)]))
        self._crown_ok = True
        self._viz_rod = dict(rocker=dR * lev, rockerAx=dR, rodA=a, rodB=b, armA=a, armB=a)
        self._rod_info = dict(rocker_level=round(lev, 1), horn_level=round(float(fK + S.CROWN + capK + HORN_PLATE), 1),
                              rod_len=round(float(np.linalg.norm(b - a)), 1), rocker_h=float(hrk), corrected=True)

    def collide(self, i):
        out = super().collide(i)
        if "RODK" not in self.strap: return out
        R, t = self.T(7, i)
        X = self.strap["RODK"][1] @ R.T + t
        m, cen, ax = self.cyl["hubK"]; Rk, tk = self.T(m, i)
        c = float(self.sd_cyl(X, Rk @ cen + tk, Rk @ ax, r=self.cyl_r["hubK"]).min())
        self.last_clear["ROD-hubK"] = round(c, 1)
        return min(out, c)


def claim_rod_vs_cap(M):
    """how deep the CLAIM's rod / horn head sit in K's cap cylinder (HUB_R, CROWN + capK): min signed distance (mm)"""
    P = M.D.p; uK = M.D.uK; capK = float(P.get("capK", 0) or 0)
    out = {}
    for nm in ("rod", "rodends"):
        if nm in M.rigid:
            X = M.rigid[nm][1]
            out[nm] = round(float(PK.Model.sd_cylr(X, uK * M.fK, uK, S.HUB_R, S.CROWN + capK).min()), 2)
    return out


def frozen_wear(Model, P, wear="bench", flood=False):
    P = F._clamp(dict(F.PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    a1 = PK.audit(M1, B1); fit["gap_near1"] = a1.get("gap_near1"); fit["rod_vs_cap"] = claim_rod_vs_cap(M1)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    if wear == "held":
        PV = _load("pk_polish_v_frontload_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    assert KB.KDesign is F.FLDesign, "design class re-patched"
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ko, st = M.kin_ok, M.kstate
    L_ = M.D.law()
    drive = dict(stretched_kin=int((ko & (st == 1)).sum()), folded_kin=int((ko & (st == -1)).sum()),
                 dK_taken_max=round(float(np.degrees(np.abs(M.dK[ko & (st == 1)])).max()), 1) if (ko & (st == 1)).any() else 0.0,
                 res_max_deg=round(float(M.res_deg[ko].max()), 4) if ko.any() else None, rod=getattr(M, "_rod_info", None),
                 law=dict((k, (round(v, 2) if isinstance(v, float) else v)) for k, v in L_.items()
                          if k in ("ok", "dK_max", "t_max", "th_max", "why_end", "lobe_r_max", "lift_max", "m3e_min", "dKB")),
                 pa_max=round(float(L_["pa"].max()), 2) if L_.get("ok") else None)
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, drive=drive, min_clear_taken=r.get("min_clear_taken"))
    if flood:
        MECH = _load("minarc_mech_for_frontload_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "fit":
        B = CB.Bench(n_clip=60, n_ws=160); Model = CorrModel if sys.argv[2] == "corr" else F.FLModel; t = time.time()
        M = Model(B, F._clamp(dict(F.PARAMS, **BEST))); r = M.run(); a = PK.audit(M, B)
        print(json.dumps(dict(which=sys.argv[2], **{k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, near1=a.get("gap_near1"),
                              why=r.get("why"), pairs=r.get("parts_pairs"), parts=r.get("parts_ib14"), rod=getattr(M, "_rod_info", None),
                              rod_vs_cap=claim_rod_vs_cap(M), secs=round(time.time() - t)), default=float))
    if sys.argv[1] == "wear":
        which, wear, path = sys.argv[2], sys.argv[3], sys.argv[4]
        Model = CorrModel if which == "corr" else F.FLModel
        t = time.time(); out = frozen_wear(Model, dict(BEST), wear, "--flood" in sys.argv)
        out.update(which=which, wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(which=which, wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"), why=out["why"],
                              drive=out["drive"], conn=out.get("connected"), secs=out["secs"]), default=float))
