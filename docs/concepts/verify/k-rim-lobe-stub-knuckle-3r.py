"""Independent verifier (skeptic) of k-rim-lobe-stub-knuckle-3r (lobe sector on link 1a around K, MR52ZZ roller on a
24 mm stub of link 2; K slaved to q2 by the direct pair, never read).

The claim's model (docs/concepts/models/k-rim-lobe-stub-knuckle-3r.py) is loaded UNCHANGED as its own module copy.
What this harness adds (`corr`):

  1. LOBE vs HUB 1 and LOBE vs HUB K's neighbours: the claim checks the lobe against hub 2, hub 3, L1b, L2, LT, knee,
     pad and E, not against hub 1 (non-adjacent body, 1 mm rule). Added.
  2. ROLLER vs LOBE INSIDE THE LAW: the claim exempts the roller-lobe pair on every law pose (state 1). The pair may
     touch only at the flank; an undercut (a concave flank tighter than the roller, or the web / back rows crossing the
     roller's path) would let the roller pass through lobe metal unseen. Checked geometrically over the whole valid law
     prefix (pitch point C(t) vs every lobe sample, great-circle mm at the lobe level; must be >= rr - 0.3 mm), and per
     pose: the roller disc vs the lobe samples NOT on the flank row (back rows + web) >= 0 mm (they sit >= 1.5 mm behind).
  3. FROZEN WEAR with every drive attribute carried over (the claim's KB.frozen copy list predates the stub; the metal is
     in strap / rigid / contact, which it does copy - this harness copies the drive's own fields too, so nothing is
     rebuilt or silently skipped), exact path on Bench(110,360), held-out clips optional.
  4. CONTINUITY FLOOD FILL (CLAUDE.md): reach on the connected set, grids bench / knn / full
     (docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py connected_report, unchanged).

    CB_EXACT=1 python3 docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py wear <claim|corr> <bench|held> <out.json> [--flood]
    python3 docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py fit <claim|corr>
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


C = _load("krim_claim_v", os.path.join(REPO, "docs", "concepts", "models", "k-rim-lobe-stub-knuckle-3r.py"))
G, KR, KB, PK, S = C.G, C.KR, C.KB, C.PK, C.S

BEST = {"L_stub": 24.487, "a0": 146.225, "kK": 0.825, "smhi": 22.126, "a1max": 48.0, "bk1": 33.191, "bk2": 39.926, "tip_tol": 3.087,
        "lobe_w": 3.493, "lobe_lev": 0, "rr": 2.5, "emb_mode": "kstub"}


def law_undercut(M):
    """min over the law prefix of (great-circle distance pitch point -> any lobe sample) - rr, at the lobe level (mm)"""
    D = M.D; L_ = D.law(); R = float(M._R_lobe); rr = float(D.p["rr"])
    ld = M._lobe_d
    if not L_.get("ok") or not len(ld): return None
    Cn = L_["C"] / np.linalg.norm(L_["C"], axis=1)[:, None]
    ang = np.arccos(np.clip(Cn @ ld.T, -1, 1)) * R
    return round(float(ang.min() - rr), 3)


class CorrModel(C.KSModel):
    def finalize(self):
        super().finalize()
        if "LOBE" not in getattr(self, "strap", {}): return
        # the lobe's non-flank samples (back rows + web): a lobe sample whose distance to the pitch curve exceeds rr + 0.75
        D = self.D; L_ = D.law(); R = float(self._R_lobe); rr = float(D.p["rr"])
        Cn = L_["C"] / np.linalg.norm(L_["C"], axis=1)[:, None]
        dmin = np.arccos(np.clip(self._lobe_d @ Cn.T, -1, 1)).min(1) * R
        back = self._lobe_d[dmin > rr + 0.75]
        self.strap["LOBEBK"] = (1, back * (R + S.T_LINK / 2))
        self._undercut = law_undercut(self)

    def collide(self, i):
        out = super().collide(i)
        if "LOBE" not in getattr(self, "strap", {}): return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        LO = tf(*self.strap["LOBE"]); c = {}
        m, cen, ax = self.cyl["hub1"]; Rh, th_ = self.T(m, i)
        c["LOBE-hub1"] = float(self.sd_cyl(LO, Rh @ cen + th_, Rh @ ax, r=self.cyl_r["hub1"]).min()) - h
        st = self.kstate[i] if hasattr(self, "kstate") else 0
        if st == 1 and "LOBEBK" in self.strap and len(self.strap["LOBEBK"][1]):
            RC = tf(*self.strap["ROLC"]); BK = tf(*self.strap["LOBEBK"])
            c["ROL-LOBEback"] = float(cKDTree(BK).query(RC)[0].min()) - h      # adjacent pair in rolling contact: >= 0
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


CARRY = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
         "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_tail_rows", "_tip_dir", "_LT_len", "_LT_need", "_TIP_need", "_floor_tip",
         "_roller_bottom", "_R_lobe", "_lobe_d", "_lobe_R0", "_stub_info", "_undercut", "_HE", "cyl_r")


def frozen_wear(Model, P, wear="bench", flood=False):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    a1 = PK.audit(M1, B1); fit["gap_near1"] = a1.get("gap_near1"); fit["why"] = r1.get("why"); fit["pairs"] = r1.get("parts_pairs")
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in CARRY:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    if wear == "held":
        PV = _load("pk_polish_v_krim", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ko, st = M.kin_ok, M.kstate
    drive = dict(stretched_kin=int((ko & (st == 1)).sum()), folded_kin=int((ko & (st == -1)).sum()),
                 dK_taken_max=round(float(np.degrees(np.abs(M.dK[ko & (st == 1)])).max()), 1) if (ko & (st == 1)).any() else 0.0,
                 res_max_deg=round(float(M.res_deg[ko].max()), 4) if ko.any() else None, stub=getattr(M1, "_stub_info", None),
                 undercut_mm=getattr(M1, "_undercut", law_undercut(M1)),
                 law=dict((k, (round(v, 2) if isinstance(v, float) else v)) for k, v in M.D.law().items() if k in ("ok", "dK_max", "t_max", "th_max", "why_end")))
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, drive=drive, min_clear_taken=r.get("min_clear_taken"))
    if flood:
        MECH = _load("minarc_mech_for_krim", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "fit":
        B = CB.Bench(n_clip=60, n_ws=160); Model = CorrModel if sys.argv[2] == "corr" else C.KSModel; t = time.time()
        M = Model(B, dict(C.PARAMS, **BEST)); r = M.run(); a = PK.audit(M, B)
        print(json.dumps(dict(which=sys.argv[2], mode=B.mode, **{k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                              near1=a.get("gap_near1"), why=r.get("why"), pairs=r.get("parts_pairs"), undercut=law_undercut(M),
                              stub=getattr(M, "_stub_info", None), secs=round(time.time() - t)), default=float))
    if sys.argv[1] == "wear":
        which, wear, path = sys.argv[2], sys.argv[3], sys.argv[4]
        Model = CorrModel if which == "corr" else C.KSModel
        t = time.time(); out = frozen_wear(Model, dict(C.PARAMS, **BEST), wear, "--flood" in sys.argv)
        out.update(which=which, wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(which=which, wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"), why=out["why"],
                              pairs=out["parts_pairs"], drive=out["drive"], conn=out.get("connected"), secs=out["secs"]), default=float))
