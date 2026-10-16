"""Independent verifier (skeptic) of geneva-tail-knuckle-pinknee-3r, rod embodiment (hub-2 rim lobe -> rocker on link 1b
-> O3 pushrod with M3 rod ends -> horn on K's cap; K slaved to q2, never read).

The claim's model (docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py) is loaded UNCHANGED as its own module copy.
What this harness changes (`corr`):

  1. THE HORN LEAVES THE SPRING CAP. The claim puts the horn's rod-end head at K's cap MID-height (fK + CROWN + capK / 2)
     at r_horn 2.49 mm from K's axis. That cap (+6 mm) is the clock spring's housing (0.3 x 5 mm strip, the kit-rule
     judge's real spring): an O10 rod-end head centred 2.5 mm off the axis would sit inside the spring's coils and arbor.
     Corrected: a 1.5 mm horn plate ON the cap top; the rod-end head (O10 x 5) sits on it, and the rod centreline meets
     both heads at their mid-height (the claim joined it to the heads' bottoms, so its underside ran 1.5 mm below them).
  2. ROD vs HUB K. The claim checks the rod against hub 1, hub 3, L1a, L2, knee, pad and E, but not against hub K (the cap
     it crosses). Added at the 1 mm non-adjacent rule (the rod is on link 1b, the cap on link 1a; the cylinder is
     symmetric about uK, so K's turn does not change the check).
  3. CONTINUITY FLOOD FILL (CLAUDE.md continuity rule): reach scored on the connected set, grids bench / knn / full
     (docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py flood(), unchanged).

    CB_EXACT=1 python3 docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py wear <claim|corr> <bench|held> <out.json> [--flood]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


G = _load("geneva_claim_v", os.path.join(REPO, "docs", "concepts", "models", "geneva-tail-knuckle-pinknee-3r.py"))
KR, KB, PK, S = G.KR, G.KB, G.PK, G.S
unit = S.unit

BEST = {"emb_mode": "rod", "kK": 3.1796, "r_horn": 2.4932, "r_lobe": 9.0, "bk1": 31.2491, "bk2": 37.9937, "a1max": 58.3565,
        "smhi": 13.6865, "smlo": 5.2777, "az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473,
        "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "capK": 6.0, "tail": 1}
HORN_PLATE, HEAD_H, HEAD_R = 1.5, 5.0, 5.0


class CorrModel(G.GModel):
    def _rod_metal(self):
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]; capK = float(P.get("capK", 0) or 0)
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0)
        ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max()) + S.T_LINK
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        self.rigid["rocker"] = (7, dR * lev + dd[:, :1] * e + dd[:, 1:] * f)
        eK, _ = S.frame_of(uK)
        hornP = uK * (fK + S.CROWN + capK + HORN_PLATE) + float(P["r_horn"]) * eK   # head bottom ON the horn plate on the cap top
        b = hornP + 0.5 * HEAD_H * uK                                                # rod centreline at the heads' mid-height
        # the rocker post is as tall as the straight rod needs to clear hub K's cap by 1 mm (rod on link 1b, cap on link 1a,
        # the cap is a cylinder about uK, so the clearance does not depend on the pose); the claim's 9 mm post ran the rod
        # 5.9 mm into the cap and its head 3 mm inside it
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


def frozen_wear(Model, P, wear="bench", flood=False):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    a1 = PK.audit(M1, B1); fit["gap_near1"] = a1.get("gap_near1")
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    if wear == "held":
        PV = _load("pk_polish_v_geneva", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ko, st = M.kin_ok, M.kstate
    drive = dict(stretched_kin=int((ko & (st == 1)).sum()), folded_kin=int((ko & (st == -1)).sum()),
                 dK_taken_max=round(float(np.degrees(np.abs(M.dK[ko & (st == 1)])).max()), 1) if (ko & (st == 1)).any() else 0.0,
                 res_max_deg=round(float(M.res_deg[ko].max()), 4) if ko.any() else None, rod=getattr(M, "_rod_info", None),
                 law=dict((k, (round(v, 2) if isinstance(v, float) else v)) for k, v in M.D.law().items() if k in ("ok", "dK_max", "t_max", "th_max", "why_end")))
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, drive=drive, min_clear_taken=r.get("min_clear_taken"))
    if flood:
        MECH = _load("minarc_mech_for_geneva", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "fit":                                       # smoke: Bench(60,160) fast, claim vs corrected metal
        B = CB.Bench(n_clip=60, n_ws=160); Model = CorrModel if sys.argv[2] == "corr" else G.GModel; t = time.time()
        M = Model(B, dict(G.PARAMS, **BEST)); r = M.run(); a = PK.audit(M, B)
        print(json.dumps(dict(which=sys.argv[2], **{k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, near1=a.get("gap_near1"),
                              why=r.get("why"), pairs=r.get("parts_pairs"), parts=r.get("parts_ib14"), rod=getattr(M, "_rod_info", None), secs=round(time.time() - t)), default=float))
    if sys.argv[1] == "wear":
        which, wear, path = sys.argv[2], sys.argv[3], sys.argv[4]
        Model = CorrModel if which == "corr" else G.GModel
        t = time.time(); out = frozen_wear(Model, dict(G.PARAMS, **BEST), wear, "--flood" in sys.argv)
        out.update(which=which, wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(which=which, wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"), why=out["why"],
                              drive=out["drive"], conn=out.get("connected"), secs=out["secs"]), default=float))
