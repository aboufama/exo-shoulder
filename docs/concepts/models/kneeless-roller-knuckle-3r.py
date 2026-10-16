"""kneeless-roller-knuckle-3r (round 9, lens 3): the verified roller-flank knuckle (sidecar-roller-flank-knuckle-3r: J1
acromion top, link 1a with the flank lug, K slaved by the hub-2 rim lobe -> bell crank -> MR63ZZ roller -> conjugate
spherical flank, link 1b, J2, link 2, J3) with J3's axis ON A GH RAY (b3 0) and the two-pin knee DELETED: member 3
(hub 3's lower plate + the E strap + the former knee link) is ONE rigid Ti bracket bolted to the arm pad on BOTTOM.
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, 0 sensed passives.

WHY THE KNEE CARRIES NOTHING (exact, asserted on every bench): with J1, J2 (b1 = b2 = 0) and J3 (b3 = 0) on GH rays the
three hub lines meet at GH, c3 = 0, the drift t3 = R12 (c3 - R3 c3) = 0 and s = Q^T t3 = 0 on every pose: member 3
moves with the arm. The knee closure at s = 0 is the rest configuration, so the knee angle is constant; the model
asserts ptp(knee angle) < 0.5 deg over every pose of the bench and |s| < 0.05 mm ('knee_moved' -> dishonest otherwise).

WHAT THIS FILE CHANGES (everything else - the round-9 roller wrapper roller-longdyad-knuckle-3r.py: PA <= 43, roller
stub head as metal, 2 mm near-touch objective, workspace in-band, contact split; and under it the verified roller-flank
model: cam synthesis per 0.25 deg of K, drive-range truncation, kit fold rule, O20 stacks, every part pair - is loaded
unchanged):
  * b3 = 0 forced in the clamp; chain 'free' with the roller row's dyad allowed (bk2 34-48);
  * the knee window (ang_min, the planar RRR's reach limits) is dropped: a rigid bracket has no knee angle to keep;
  * the former knee link is re-sampled as part of the bracket at the boss / pad level tr (no pin stack above it:
    it drops by tp + RUN ~ 2.5 mm and is re-fitted against the skin), 3 mm thick (T_LINK), 10 wide; its contact-only
    edges and top, and its box for the part-pair checks, are rebuilt at that level;
  * the adjacency knee-vs-E (same body now) and pad-vs-E (bolted, same body) are dropped; the bracket keeps >= 0.15 mm
    to hub 3's cylinder (link 2's half of hub 3 turns over it) and >= 1 mm to hub 1 / hub K / hub 2 / L1a / L1b / L2 /
    crank / roller / lug, as the knee and pad did; the pad stays sampled as metal (the bracket's bolted end).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/kneeless-roller-knuckle-3r.py [check|split] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("roller_round9_for_kneeless", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
RL = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RL)
RF, SC, FL, PK, S = RL.RF, RL.SC, RL.FL, RL.PK, RL.S
KR = FL.G.KR; KB = KR.KB
unit = S.unit; D2R = math.pi / 180
ID = "kneeless-roller-knuckle-3r"
BR_T = S.T_LINK                                              # bracket plate thickness (3 mm Ti-6Al-4V)
KNEE_TOL_DEG, S_TOL_MM = 0.5, 0.05
REPORT_KEYS = ("plain", "gap_near1", "gap_near2", "min_metal_mm", "knee_rigid", "why", "parts_ib14", "ws_inband", "cam", "overhead140")

# the verified roller-flank row's best (rows/sidecar-roller-flank-knuckle-3r.json best_params) with b3 0 and the
# proposer's crude J3 re-seat (wd 75, wa -9)
ROLLER_BEST = {"g": 2.2817, "beta": -174.7209, "r_c": 15.6711, "lift": 1.414, "hl": 1.3491, "zr": 3.0123, "s_arm": 4.4442,
               "r_lobe": 8.1395, "kK": 2.5246, "cprog": 0.0, "bk1": 27.7251, "bk2": 35.7114, "a1max": 56.5633, "smhi": 19.4644,
               "smlo": 5.0, "az1": 95.3929, "el1": 67.8974, "az2": 44.0485, "el2": 41.9575, "wd": 66.8053, "wa": -11.4207,
               "b3": 0.3621, "ang_min": 26.5397, "lc": 20.7075, "phib": -66.0451}
DRIVE_KEYS = ("g", "beta", "r_c", "lift", "hl", "zr", "s_arm", "r_lobe")
SEED = dict(ROLLER_BEST, b3=0.0, wd=75.0, wa=-9.0, ang_min=0.0, law_mode="lin", chain="free", near2=1)
PARAMS = dict(RL.PARAMS, **SEED)


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p["chain"] = "free"; p["law_mode"] = "lin"; p["b3"] = 0.0; p["ang_min"] = 0.0
    p["bk1"] = _c(p["bk1"], 24.0, 32.0); p["bk2"] = _c(p["bk2"], 34.0, 48.0)
    p["g"] = _c(p["g"], 1.8, 3.0); p["r_c"] = _c(p["r_c"], 14.5, 19.5); p["lift"] = _c(p.get("lift", 0.0), 0.0, min(float(p.get("lift_max", 4.0)), 8.0))
    b = float(p["beta"]); b = b - 360.0 if b > 0 else b; p["beta"] = _c(b, -180.0, -150.0)
    p["cprog"] = 0.0
    p["lE"] = _c(p.get("lE", 60.0), 35.0, 95.0); p["lc"] = _c(p["lc"], 6.0, 45.0)
    return RF._clamp(p)


class KLDesign(KB.KDesign):
    def knee(self, s):
        K = super().knee(s)
        K["ok"] = np.ones(len(np.atleast_2d(s)), bool)              # a rigid bracket: no knee window, no reach limit
        return K


KB.KDesign = KLDesign


class KLModel(RL.RLModel):
    def _geo(self):
        g = super()._geo(); D = self.D; P = D.p; off_k = P["tp"] + S.RUN
        mem, pts, ax = g["knee"]; g["knee"] = (mem, pts - off_k * D.sn, ax)  # finalize puts it at tr + off_k -> the bracket at tr
        return g

    def _boxes_at(self, i):
        out = super()._boxes_at(i); D = self.D; P = D.p; fr = self.fr; lc = float(P["lc"]); tr = self._tr_fit
        Rk = np.stack([fr["eK"], fr["nK"], D.sn], 1); ck = fr["A0m"] + (lc / 2) * fr["eK"] + (tr + BR_T / 2) * D.sn
        R, t = self.T(6, i); out["knee"] = (R @ ck + t, R @ Rk, np.array([lc / 2 + PK.BOSS_R, PK.KNEE_W / 2, BR_T / 2]))
        return out

    def _contact_only(self):
        super()._contact_only()
        D = self.D; P = D.p; tr = self.tr; fr = self.fr; sn = D.sn
        out = [c for c in self.contact if c[0] != 6]
        lc = float(P["lc"]); L = lc + 2 * PK.BOSS_R; W = PK.KNEE_W; pts = []
        for z in (tr, tr + BR_T):
            for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
            for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
        a = np.array(pts); cen = fr["A0m"] + (lc / 2) * fr["eK"]
        out.append((6, cen + a[:, :1] * fr["eK"] + a[:, 1:2] * fr["nK"] + a[:, 2:] * sn))
        out.append((6, self.rigid["knee"][1] + BR_T * sn))
        self.contact = out


def _collide_kb(self, i):
    """= the pin-knee knuckle's part-pair check (minarc-stop-knuckle-4r-pinknee.py KModel.collide) with the knee link as
    part of the rigid bracket: knee-vs-E and pad-vs-E dropped (one body), knee-vs-hub3 kept (>= 0.15: link 2's half of
    hub 3 turns over the bracket), every non-adjacent pair >= 1 mm as before"""
    h = S.T_LINK / 2
    def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
    cyl = {}
    for k, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k] = (R @ cen + t, R @ ax)
    surf = {k: tf(m, X) for k, (m, X) in self.cyl_surf.items()}
    strap = {k: tf(m, X) for k, (m, X) in self.strap.items()}
    Em = tf(*self.Emid); bx = self._boxes_at_final(i)
    def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
    def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
    def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
    def ss(A, Bq): return float(cKDTree(Bq).query(A)[0].min()) - 2 * h if len(A) and len(Bq) else 1e9
    c, adj = {}, {}
    hn = ["hub1", "hubK", "hub2", "hub3"]
    for a in range(4):
        for b in range(a + 1, 4): c[f"{hn[a]}-{hn[b]}"] = vcyl(surf[hn[b]], hn[a])
    for L, ends in (("L1a", ("hub1", "hubK")), ("L1b", ("hubK", "hub2")), ("L2", ("hub2", "hub3"))):
        for hb in hn:
            if hb not in ends: c[f"{L}-{hb}"] = vcyl(strap[L], hb, h)
    c["L1a-L2"] = ss(strap["L1a"], strap["L2"])
    c["L1a-L1b"] = ss(far(strap["L1a"], "hubK", 4), far(strap["L1b"], "hubK", 4))
    c["L1b-L2"] = ss(far(strap["L1b"], "hub2", 4), far(strap["L2"], "hub2", 4))
    for nm in ("knee", "pad"):
        for hb in ("hub1", "hubK", "hub2"): c[f"{nm}-{hb}"] = vbox(surf[hb], nm)
        for L in ("L1a", "L1b", "L2"): c[f"{nm}-{L}"] = vbox(strap[L], nm, h)
    c["pad-hub3"] = vbox(surf["hub3"], "pad")
    for hb in ("hub1", "hubK", "hub2"): c[f"E-{hb}"] = vcyl(Em, hb, h)
    c["E-L1a"] = ss(Em, strap["L1a"]); c["E-L1b"] = ss(Em, strap["L1b"])
    L2f = far(strap["L2"], "hub3", 1)
    if len(L2f): adj["E-L2"] = ss(Em, L2f)
    adj["knee-hub3"] = vbox(surf["hub3"], "knee")
    self.last_clear = {k: round(v, 1) for k, v in list(c.items()) + list(adj.items())}
    out = min(c.values())
    if min(adj.values()) < self.ADJ: out = min(out, -1.0)
    return out


KR._KModel0.collide = _collide_kb                             # this module's own copy of the chain only
SC.SCModel = KLModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS; RL.PARAMS = PARAMS
FL.G.KR.KB.KModel = KLModel; FL.FLModel_SC = KLModel


def knee_check(M):
    """the knee-carries-nothing assertion: constant knee angle and zero drift over every pose of the bench"""
    ang = np.asarray(M.K["ang"], float); s = np.asarray(M.s, float)
    fin = np.isfinite(ang) & np.isfinite(s).all(1)
    ptp = float(np.ptp(ang[fin])) if fin.any() else 0.0; smax = float(np.abs(s[fin]).max()) if fin.any() else 0.0
    c3 = float(np.linalg.norm(M.D.c[2]))
    return dict(ang_ptp_deg=round(ptp, 4), s_max_mm=round(smax, 4), c3_mm=round(c3, 5), ang=round(float(ang[fin][0]), 2) if fin.any() else None,
                ok=bool(ptp < KNEE_TOL_DEG and smax < S_TOL_MM))


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = RL._report(B, p)
    kc = knee_check(M); r["knee_rigid"] = kc
    if not kc["ok"]: r["honest"] = False; r["knee_moved"] = True
    return r, M


contact_split = RL.contact_split
ws_inband = RL.ws_inband


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360): return SC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
def frozen_held(P): return SC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)
def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)


def redteam_gh(par=None, nc=110, nw=360, mags=(3.0, 5.0, 10.0), liner=3.0):
    """GH-offset red team (the misfit the deleted knee used to absorb): the chain is spherical about the NOMINAL GH, the
    arm turns about the TRUE centre g (scapula-handler tracking error / humeral-head translation, constant here). With the
    bracket bolted at rest, an arm point moves R (p - g) + g while the bracket moves R p, R = Q Q0^T: misfit (I - R) g,
    |misfit| = 2 |g_perp| sin(theta / 2). Over every pose of Bench(nc, nw) and 26 directions of g per magnitude: the
    misfit's median / p90 / max, the share of poses within the liner budget, and the same with ONE cuff slide along the
    humerus (the axial component in the arm frame removed), and what a planar knee in hub 3's plane would leave (only the
    component along hub 3's axis u3) for comparison with the knee designs"""
    D = KLDesign(_clamp(dict(PARAMS, **(par or {})))); u3 = D.u[2]
    Z = CB._poses_all(); B = CB.Bench(n_clip=nc, n_ws=nw); Q = Z["HG"][B.idx].astype(float)
    sp_ = importlib.util.spec_from_file_location("osn_for_kneeless_rt", os.path.join(HERE, "offset-skin-normal-3r.py"))
    OSN = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(OSN); Q0 = OSN.rest()["Q0"]
    dirs = np.array([[x, y, z] for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)], float)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    Rr = np.einsum("nij,kj->nik", Q, Q0)                          # Q Q0^T
    ax_arm = np.array([0.0, -1.0, 0.0])                          # humerus axis in the band humerus frame (rest: along -y)
    out = {}
    for mg in mags:
        mis = np.einsum("nij,kj->nki", np.eye(3)[None] - Rr, dirs * mg)        # (n poses, 26 dirs, 3) scapula frame
        mag = np.linalg.norm(mis, axis=2); worst = mag.max(1)
        armf = np.einsum("nji,nkj->nki", Q, mis)                               # in the arm frame
        perp = armf - (armf @ ax_arm)[..., None] * ax_arm; wp = np.linalg.norm(perp, axis=2).max(1)
        kn = np.abs(armf @ u3).max(1)
        out[f"{mg:g}mm"] = dict(knee_equiv_median=round(float(np.median(kn)), 2), knee_equiv_max=round(float(kn.max()), 2),
                                knee_equiv_within_liner=round(float((kn <= liner).mean()), 3),median=round(float(np.median(worst)), 2), p90=round(float(np.percentile(worst, 90)), 2), max=round(float(worst.max()), 2),
                                within_liner=round(float((worst <= liner).mean()), 3),
                                slide_median=round(float(np.median(wp)), 2), slide_p90=round(float(np.percentile(wp, 90)), 2), slide_max=round(float(wp.max()), 2),
                                slide_within_liner=round(float((wp <= liner).mean()), 3))
    th = np.degrees(np.arccos(np.clip((np.einsum("nii->n", Rr) - 1) / 2, -1, 1)))
    out["rotation_from_rest_deg"] = dict(median=round(float(np.median(th)), 1), p90=round(float(np.percentile(th, 90)), 1), max=round(float(th.max()), 1))
    out["n_poses"] = int(len(Q)); out["liner_mm"] = liner
    return out


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "redteam_gh":
        print(json.dumps(redteam_gh(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), parts=out.get("parts_ib14"),
                              connected=out.get("connected"), sidecar=out.get("sidecar"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          knee=r.get("knee_rigid"), idle=r.get("drive_idle"), cam_short=r.get("cam_short"), pa_fail=r.get("pa_fail"), why=r.get("why"),
                          ovh=r.get("overhead140"), ws_inband=r.get("ws_inband"), cam=r.get("cam"), parts=r.get("parts_ib14"), pairs=r.get("parts_pairs"),
                          split=contact_split(M, B) if mode == "split" else None,
                          clear=getattr(M, "last_clear", None), secs=round(time.time() - t)), default=float))
