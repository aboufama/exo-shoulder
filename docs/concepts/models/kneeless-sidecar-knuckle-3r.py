"""kneeless-sidecar-knuckle-3r: the verified lead (sidecar-longdyad-knuckle-3r: slaved knuckle K, strap-level RSSR
sidecar drive, kit fold rule, physical q2 stop, O20 hubs) with J3 put ON A GH RAY (b3 = 0) and the two-pin knee DELETED.

Why the knee can go (exact, not a fit): with J1, K, J2 and J3 all on GH rays every joint is a rotation about GH, so the
chain's orientation closure R1 RK R2 R3 = Q leaves member 3 with zero translation relative to the arm (the drift
s = Q^T t3 that the pin knee absorbed is identically zero). Member 3 is therefore rigid with the arm and the knee link,
its two iglidur pins and its two encoders become ONE rigid bent Ti bracket (3 mm Ti-6Al-4V, 10 wide, line/arc sketch):
hub 3's lower plate -> E strap (ramp) -> bend corner (the old O12 boss disc) -> flat plate (the old knee link) -> arm pad
on BOTTOM. 3 ACTIVE DOF (J1, J2, J3 encoded), K slaved (never read), 0 passive translations, 0 sensed passives.

What changes in the metal (honest, conservative side):
  * the knee plate drops from the pin stack level (tr + tp + RUN) to the bracket level tr, thickness 3.0 (was tp ~2.35);
    the pad is 3.0 thick too (stk fixed at 6 + RUN -> tp 3.0);
  * the knee-vs-E and knee-vs-hub3 ADJACENCY (0.15 mm) checks go (same body); the bracket plate vs hub 3's housing is kept
    as a NON-adjacent 1 mm check (the J3 stack turns with link 2); E vs link 2 stays the adjacent 0.15 mm check at J3;
    the bracket / pad vs every other part (hubs, links, crank, horn, rod) stay at 1 mm;
  * a pose whose drift leaves the bracket's rest shape by > 0.5 mm / 0.5 deg is NOT taken ('slide'; never happens at b3 0)
    and the report carries knee_ptp (the knee angle's range over the bench: must stay < 0.5 deg).
Objective: the 2 mm near-touch gap (round-9 rule, near2 = 1); reports plain, near1, near2, workspace in-band.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/kneeless-sidecar-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/kneeless-sidecar-knuckle-3r.py frozen '<json>' [out.json]
    python3 docs/concepts/models/kneeless-sidecar-knuckle-3r.py ghoff '<json>' [out.json]     (GH-offset red team)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("sidecar_for_kneeless", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
SC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SC)
FL, G, KR, KB, PK, S = SC.FL, SC.G, SC.KR, SC.KB, SC.PK, SC.S
unit = S.unit; D2R = math.pi / 180
ID = "kneeless-sidecar-knuckle-3r"
T_BR = 3.0                                                   # bracket plate thickness (3 mm Ti-6Al-4V bent bar)
DRIFT_TOL_MM, DRIFT_TOL_DEG = 0.5, 0.5

# the verified lead's best_params (rows/sidecar-longdyad-knuckle-3r.json) with b3 0 and the judge's re-seat (wd 75, wa -7)
LEAD = {"bk1": 28.9414, "bk2": 39.236, "a1max": 63.1774, "kK": 1.6232, "r_h": 14.8706, "beta": -86.447, "La": 16.5467,
        "s_arm": 4.3872, "hl": 3.15, "zr": 0.0, "r_lobe": 7.7447, "smhi": 16.5464, "smlo": 5.0, "az1": 96.6954, "el1": 67.5865,
        "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345, "ang_min": 26.8823, "lc": 25.6915,
        "phib": -60.7036, "gam": 0.0, "law_mode": "lin"}
SEED = dict(LEAD, b3=0.0, wd=75.0, wa=-7.0, stk=6.15, near2=1)
PARAMS = dict(SC.PARAMS, **SEED)
_sc_clamp = SC._clamp
_sc_report = SC._report


def _clamp(p):
    p["b3"] = 0.0                                            # J3 on a GH ray: the morphology
    p["stk"] = 2 * T_BR + S.RUN                              # tp = 3.0: the pad and the bracket are 3 mm plate
    p["ang_min"] = 0.0                                       # no knee window: the bracket is rigid, its bend is a shape
    p["lE"] = min(max(float(p["lE"]), 30.0), 95.0); p["lc"] = min(max(float(p["lc"]), 12.0), 45.0)
    return _sc_clamp(p)


class KLDesign(FL.FLDesign):
    def knee(self, s):
        """the bracket is rigid: the 'knee' is evaluated only to place the pad; a pose whose drift moves member 3 off the
        rest shape (|s - m| > 0.5 mm in hub 3's plane, or the bend angle off by > 0.5 deg) is refused"""
        K = super().knee(s)
        dev = np.linalg.norm(np.asarray(s)[:, :2] - self.m[None, :2], axis=1)
        K0 = super().knee(self.m[None, :].copy()); a0 = float(K0["ang"][0])
        K["ok"] = (dev <= DRIFT_TOL_MM) & (np.abs(K["ang"] - a0) <= DRIFT_TOL_DEG)
        K["ang0"] = a0; K["dev_max"] = float(dev.max()) if len(dev) else 0.0
        return K


G.KR.KB.KDesign = KLDesign


class KLModel(SC.SCModel):
    ADJ = 0.15

    def _geo(self):
        g = super()._geo(); P = self.D.p; off_k = float(P["tp"]) + S.RUN
        m, X, ax = g["knee"]; g["knee"] = (m, X - off_k * self.D.sn, ax)   # fit + finalize then put the plate at tr
        return g

    def _boxes_at(self, i):
        D = self.D; P = D.p; tr = self._tr_fit; fr = self.fr; lc = float(P["lc"]); tp = float(P["tp"]); out = {}
        Rk = np.stack([fr["eK"], fr["nK"], D.sn], 1); ck = fr["A0m"] + (lc / 2) * fr["eK"] + (tr + T_BR / 2) * D.sn
        R, t = self.T(6, i); out["knee"] = (R @ ck + t, R @ Rk, np.array([lc / 2 + PK.BOSS_R, PK.KNEE_W / 2, T_BR / 2]))
        Rp = np.stack([D.sa, D.st, D.sn], 1); cp = fr["Bm"] + (tr + tp / 2) * D.sn
        R, t = self.T(5, i); out["pad"] = (R @ cp + t, R @ Rp, np.array([PK.PAD_R, PK.PAD_R, tp / 2]))
        return out

    def _contact_only(self):
        super()._contact_only()
        D = self.D; P = D.p; tr = self.tr; fr = self.fr; sn = D.sn
        self.contact = [(m, X) for m, X in self.contact if m != 6]
        lc = float(P["lc"]); L = lc + 2 * PK.BOSS_R; W = PK.KNEE_W; pts = []
        for z in (tr, tr + T_BR):
            for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
            for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
        a = np.array(pts); cen = fr["A0m"] + (lc / 2) * fr["eK"]
        self.contact.append((6, cen + a[:, :1] * fr["eK"] + a[:, 1:2] * fr["nK"] + a[:, 2:] * sn))
        self.contact.append((6, self.rigid["knee"][1] + T_BR * sn))

    def collide(self, i):
        self.ADJ = -1e9                                          # parent adjacency (knee-E, knee-hub3, E-L2) off ...
        try: out = super().collide(i)
        finally: self.ADJ = KLModel.ADJ
        h = S.T_LINK / 2; R3, t3 = self.T(3, i); R2, t2 = self.T(2, i)
        m3, cen3, ax3 = self.cyl["hub3"]; c3 = R3 @ cen3 + t3; a3 = R3 @ ax3
        m2, L2 = self.strap["L2"]; L2w = L2 @ R2.T + t2; w = L2w - c3
        L2f = L2w[np.linalg.norm(w - (w @ a3)[:, None] * a3, axis=1) > self.cyl_r["hub3"] + 1]
        mE, Em = self.Emid; Emw = Em @ R3.T + t3
        eL2 = float(cKDTree(L2f).query(Emw)[0].min()) - 2 * h if len(L2f) else 1e9      # ... E vs link 2 kept: adjacent at J3
        kh3 = float(self.last_clear.get("knee-hub3", 1e9))       # bracket plate vs hub 3's housing: non-adjacent (1 mm)
        self.last_clear["E-L2"] = round(eL2, 2); self.last_clear.pop("knee-E", None)
        out = min(out, kh3)
        if eL2 < self.ADJ: out = min(out, -1.0)
        return out


SC.SCModel = KLModel; SC._clamp = _clamp; SC.PARAMS = PARAMS
G.KR.KB.KModel = KLModel; FL.FLModel_SC = KLModel


def ws_inband(B):
    """the unscored workspace in-band (round-9 rule, gaming pattern L2): in-band 2-14 / 2-10 over the metal of the TAKEN
    workspace poses, overall and at elevation 90-140 / >= 140, from the bench's own per-pose distances"""
    out = {}
    for nm, lo, hi in (("all", -1, 999), ("e90_140", 90, 140), ("ovh140", 140, 999)):
        d = [B.res[j] for j, k in enumerate(B.kind) if k == "ws" and B.res[j] is not None and float(np.min(B.res[j])) >= 0
             and lo <= float(B.poses[j]["elev"]) < hi]
        d = np.concatenate(d) if d else np.zeros(0)
        out[nm] = [round(float(np.mean((d >= 2) & (d <= 14))), 4), round(float(np.mean((d >= 2) & (d <= 10))), 4)] if len(d) else None
    return out


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = _sc_report(B, p)
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")} if "plain" not in r else r["plain"]
    r["ws_inband"] = ws_inband(B)
    if M.kin_ok.any():
        a = PK.audit(M, B); r["gap_near2"] = a.get("gap_near2"); r["near2_poses"] = a.get("near2_poses")
        r["gap_near1"] = a.get("gap_near1", r.get("gap_near1"))
        if p.get("near2") and r["gap_near2"] is not None: r["gap"] = r["gap_near2"]
    K = M.K; ko = M.kin_ok
    r["bracket"] = dict(knee_ptp=round(float(np.ptp(K["ang"][ko])), 4) if ko.any() else None, bend_deg=round(float(K.get("ang0", 0.0)), 2),
                        drift_max_mm=round(float(K.get("dev_max", 0.0)), 4), tr=round(float(getattr(M, "tr", 0.0)), 1),
                        f3=round(float(M.f[2]), 1) if hasattr(M, "f") else None)
    if ko.any() and r["bracket"]["knee_ptp"] > 0.5: r["honest"] = False; r["knee_moved"] = True
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    out = SC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
    return out


def frozen_held(P): return SC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)


def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)


def ghoff(par, mags=(3.0, 5.0, 10.0), nc=60, nw=160):
    """GH-offset red team (the bench cannot see it): the chain turns about its centre C (scapula-handler estimate of GH);
    the arm turns about the true head centre C + d. The chain matches the arm's orientation exactly (3 R through C), so the
    rigid bracket carries the pad along x -> R (x - C) + C while the arm carries the same point along x -> R (x - C - d) +
    C + d: the misfit at the cuff is (I - R) d per pose (R = the arm's rotation from the donning pose, rest). Reported for
    |d| = 3 / 5 / 10 mm over 26 directions (worst direction), on the taken poses: misfit total, its component along the
    humerus (what ONE passive slide along the arm would absorb), and the residual across the arm (what the liner takes)."""
    p = _clamp(dict(PARAMS, **par)); B = CB.Bench(n_clip=nc, n_ws=nw); r, M = _report(B, p)
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    Q = M.Q[taken]; kinds = np.array(B.kind)[taken]; elev = np.array([B.poses[i]["elev"] for i in range(len(B.idx))])[taken]
    el_all = np.array([B.poses[i]["elev"] for i in range(len(B.idx))]); i0 = int(np.argmin(el_all))
    Q0 = M.Q[i0]; Rr = np.einsum("nij,kj->nik", Q, Q0)          # rotation from the donning pose (lowest elevation, arm at the side)
    hum = np.array([0.0, -1.0, 0.0])                          # down-the-arm axis in the band HG frame (tools/concept_kit.py wdir)
    dirs = []
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            for c in (-1, 0, 1):
                if (a, b, c) != (0, 0, 0): dirs.append(unit(np.array([a, b, c], float)))
    dirs = np.array(dirs); out = {}
    for mag in mags:
        worst = None
        for d in dirs:
            dv = mag * d; mis = dv[None] - np.einsum("nij,j->ni", Rr, dv)      # (I - R) d in the scapula frame
            harm = np.einsum("nij,j->ni", Q, hum)                              # humerus axis in the scapula frame
            along = np.abs(np.einsum("ni,ni->n", mis, harm)); tot = np.linalg.norm(mis, axis=1); across = np.sqrt(np.maximum(tot ** 2 - along ** 2, 0))
            snw = np.einsum("nij,j->ni", Q, M.D.sn); knee_left = np.abs(np.einsum("ni,ni->n", mis, snw))   # a planar knee in hub 3's plane leaves only this
            row = dict(dir=[round(float(x), 3) for x in d], max_mm=round(float(tot.max()), 2), p95_mm=round(float(np.percentile(tot, 95)), 2),
                       mean_mm=round(float(tot.mean()), 2), across_max_mm=round(float(across.max()), 2), across_p95_mm=round(float(np.percentile(across, 95)), 2),
                       along_max_mm=round(float(along.max()), 2), clip_p95_mm=round(float(np.percentile(tot[kinds == "clip"], 95)), 2) if (kinds == "clip").any() else None,
                       ovh_max_mm=round(float(tot[elev >= 140].max()), 2) if (elev >= 140).any() else None,
                       knee_left_max_mm=round(float(knee_left.max()), 2), knee_left_p95_mm=round(float(np.percentile(knee_left, 95)), 2))
            if worst is None or row["p95_mm"] > worst["p95_mm"]: worst = row
        out[f"{mag:g}mm"] = worst
    out["n_taken"] = int(taken.sum()); out["note"] = "misfit = |(I - R) d|: the liner takes it (no knee); 'across' = left after one passive slide along the humerus"
    return out


def viz_export(par):
    SC._report = _report
    return SC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "ghoff":
        t = time.time(); out = ghoff(par); out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
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
                          reach=r["reach"], inband14=r["inband14"], inband10=r["inband10"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"),
                          ovh=r.get("overhead140"), ws_inband=r.get("ws_inband"), bracket=r.get("bracket"), parts=r.get("parts_ib14"),
                          pairs=r.get("parts_pairs"), drive=(r.get("drive") or {}).get("sidecar"), clear=getattr(M, "last_clear", None),
                          secs=round(time.time() - t)), default=float))
