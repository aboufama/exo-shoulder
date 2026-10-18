"""posteromedial-knuckle-3r (2026-10-18, the one legal-seat cell the 3-DOF take-bound table left unmeasured; skeptic F1 of
docs/alignment/take_bound_3dof_skeptic.md): the verified lead conecut-knee-knuckle-3r (docs/concepts/models/
conecut-knee-knuckle-3r.py imported UNCHANGED: slipper-nose K drive and its rules, conecut knee, J3 own-angle dowel stop,
O20 hubs, metal, sampling, 5 deg fold margin in th, near-touch rules) with J1 RE-SEATED on the POSTEROMEDIAL back of the
shoulder: bvec(az1, el1) with az1 in [-52.5, 0] and el1 in [0, 45] (tools/concept_kit.py bvec: az 0 posterior, 90 lateral,
-90 medial; el 0 horizontal). Every such seat is inside ruling 4 ("J1 seats: back of the shoulder + acromion top only");
seat_legal() applies the scapula-handler rule of docs/concepts/models/cap-nullspace-4r.py seat_ok (az -110..135, el >= -20,
never anterior of the frontal plane by > 0.20: no front / clavicle seat).

Because J1 moves ~90-150 deg of arc from the acromion top, the J3 seat (wd, wa, b3: the arm-fixed hub) and the J2 seat are
re-chosen, not kept: J2's seat ray is RE-SOLVED (as acroant-conecut-knuckle-3r does) from J1, J3 and the dyad arcs
a1 = A1_LEAD + d_a1, a2 = A2_LEAD + d_a2 on branch br (+-1), so a CMA moves the J3 seat and the arcs while the J2 seat
stays consistent (b1 = b2 = 0: seat axes are the rays). The K dyad parts (bk1 / bk2 / a1max), the drive synthesis and
its clamps are the lead's code; a1max / kK are free inside those clamps.

DOF: 3 ACTIVE (J1, J2, J3), K slaved and never read, knee pins a / b passive rotations (outside the count), 0 passive
translations, no gears / pulleys / cables. No new part: the lead's parts at a new seat (complexity = the lead's record).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/posteromedial-knuckle-3r.py [check] ['<json>']
    ... seed <az1> <el1>                      kinematic J3-seat seeding on the FIT bench (Bench(60,160)) only
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("conecut_for_posteromedial", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
CB, S, SN, PK = CC.CB, CC.S, CC.SN, CC.PK
OSN = CC.PK.OSN
ID = "posteromedial-knuckle-3r"
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
BASE = CC._clamp(dict(CC.PARAMS, **LEAD))                    # the verified lead, every parameter
AZ_BOX, EL_BOX = (-52.5, 0.0), (0.0, 45.0)                   # the posteromedial cell (task box)
D_ARC = 12.0                                                 # |d_a1|, |d_a2| <= 12 deg
LEAD_WIN = (24.67, 110.99)                                   # the lead family's th window (fold_ceiling kin_ceiling.json leader_seats)
TH0_LEAD, TH0_TOL = 83.233, 4.0                              # the lead's rest th (deg) and the seed tolerance (amendment 1)
R2_MAX = 120.0                                               # J2 seat radius cap (mm, amendment 2)
REST_M = 5.5                                                 # rest-pose fold margin for a valid J2 resolution (deg)


def _rays(P):
    R = OSN.rest()
    d1 = OSN.seat(S.bvec(P["az1"], P["el1"]), P.get("b1", 0.0))[1]; d2 = OSN.seat(S.bvec(P["az2"], P["el2"]), P.get("b2", 0.0))[1]
    d3 = OSN.seat(R["Q0"] @ S.w_dir(P["wd"], P["wa"]), P["b3"])[1]
    return d1, d2, d3


_D0 = {}
def lead_dyad():
    if not _D0:
        d1, d2, d3 = _rays(BASE)
        _D0.update(a1=math.degrees(math.acos(float(np.clip(d1 @ d2, -1, 1)))), a2=math.degrees(math.acos(float(np.clip(d2 @ d3, -1, 1)))),
                   br=float(np.sign(d2 @ np.cross(d1, d3)) or 1.0))
    return _D0


def resolve_j2(d1, d3, a1, a2, br):
    """J2's seat ray with angle(d1, d2) = a1, angle(d2, d3) = a2 on branch br = sign(d2 . (d1 x d3)) -> az2, el2, ok"""
    c1, c2 = math.cos(math.radians(a1)), math.cos(math.radians(a2)); dd = float(np.clip(d1 @ d3, -1, 1))
    n = np.cross(d1, d3); n = n / (np.linalg.norm(n) + 1e-12); den = max(1 - dd ** 2, 1e-9)
    a = (c1 - dd * c2) / den; b = (c2 - dd * c1) / den; p_ = a * d1 + b * d3; h2 = 1 - float(p_ @ p_)
    d2 = p_ + br * math.sqrt(max(h2, 0.0)) * n; d2 = d2 / np.linalg.norm(d2)
    el2 = math.degrees(math.asin(float(np.clip(d2[1], -1, 1)))); az2 = math.degrees(math.atan2(float(d2[2]), float(-d2[0])))
    th0 = math.degrees(math.acos(dd))                        # the rest pose must close with the fold margin (+0.5) on stop A
    return az2, el2, bool(h2 > 1e-4 and abs(a1 - a2) + REST_M <= th0 <= a1 + a2 - REST_M)


def seat_legal(az, el):
    """scapula-handler seat rule (cap-nullspace-4r seat_ok): back of the shoulder / acromion top, never front / clavicle"""
    u = np.asarray(S.bvec(az, el), float)
    return bool(-110 <= az <= 135 and el >= -20 and u[0] <= 0.20)


def _clamp(p):
    p = dict(p)
    p["az1"] = min(max(float(p.get("az1", -52.5)), AZ_BOX[0]), AZ_BOX[1]); p["el1"] = min(max(float(p.get("el1", 17.5)), EL_BOX[0]), EL_BOX[1])
    p["b1"] = 0.0; p["b2"] = 0.0
    p["d_a1"] = min(max(float(p.get("d_a1", 0.0)), -D_ARC), D_ARC); p["d_a2"] = min(max(float(p.get("d_a2", 0.0)), -D_ARC), D_ARC)
    p["br"] = 1.0 if float(p.get("br", lead_dyad()["br"])) >= 0 else -1.0
    p["wd"] = min(max(float(p.get("wd", BASE["wd"])), 40.0), 120.0); p["wa"] = CC.wr(float(p.get("wa", BASE["wa"])))
    p["b3"] = min(max(float(p.get("b3", BASE["b3"])), 0.0), 0.8)
    Y = lead_dyad(); d1 = OSN.seat(S.bvec(p["az1"], p["el1"]), 0.0)[1]; R = OSN.rest(); d3 = OSN.seat(R["Q0"] @ S.w_dir(p["wd"], p["wa"]), p["b3"])[1]
    p["az2"], p["el2"], ok = resolve_j2(d1, d3, Y["a1"] + p["d_a1"], Y["a2"] + p["d_a2"], p["br"])
    p["pm_unresolved"] = not ok
    p["pm_legal"] = seat_legal(p["az1"], p["el1"])
    return CC._clamp(p)


PARAMS = dict(BASE, az1=-52.5, el1=17.5, d_a1=0.0, d_a2=0.0, br=1.0)

# NUMERICAL NOTE (not physics): the knuckle base (minarc-stop-knuckle-4r-pinknee KDesign) asserts |c[0]|, |c[1]| < 1e-6 mm
# (J1, J2 on GH rays). With b1 = b2 = 0 that holds by construction, but at these seats the rest-pose IK (float32 rest
# rotation Q0, a J2 ray closer to the J1-J3 great circle than the lead's) leaves c[1] at ~1e-4 mm (rest_err ~1e-4 deg).
# Offsets < SNAP_MM are set to exactly 0 (a < 1 micron change of the hub-2 offset); anything larger is left alone, so
# the base's assertion still guards a real off-ray seat. The largest snap of the last design is kept in SNAPPED.
SNAP_MM = 1e-3
SNAPPED = [0.0]
_KB = CC.FL.G.KR.KB
_osn_init = _KB.PK.OSN.Design.__init__


def _osn_init_snap(self, params=None):
    _osn_init(self, params)
    for k in (0, 1):
        n = float(np.linalg.norm(self.c[k]))
        if 0 < n < SNAP_MM: self.c[k] = np.zeros(3); SNAPPED[0] = max(SNAPPED[0], n)


_KB.PK.OSN.Design.__init__ = _osn_init_snap


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CC._report(B, p)
    try:
        d1, d2, d3 = _rays(M.p)
        r["seats"] = dict(az1=round(p["az1"], 3), el1=round(p["el1"], 3), az2=round(p["az2"], 3), el2=round(p["el2"], 3), wd=round(p["wd"], 3),
                          wa=round(p["wa"], 3), b3=round(p["b3"], 3), br=p["br"], legal=p["pm_legal"], unresolved=p["pm_unresolved"],
                          a1=round(math.degrees(math.acos(float(np.clip(d1 @ d2, -1, 1)))), 3), a2=round(math.degrees(math.acos(float(np.clip(d2 @ d3, -1, 1)))), 3))
    except Exception as e: r["seats"] = dict(err=str(e)[:100])
    return r, M


def evaluate(B, params):
    """objective = the 1 mm near-touch gap (CLAUDE.md search rule); r['plain'] keeps the plain gap"""
    r, M = _report(B, params)
    if r.get("gap_near1") is not None: r["gap"] = r["gap_near1"]
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    q = _clamp(dict(PARAMS, **params))
    if q["pm_unresolved"] or not q["pm_legal"]: r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    for k in ("d_a1", "d_a2", "br"): p[k] = q[k]
    return p, r


REPORT_KEYS = ("plain", "gap_near1", "gap_near2", "why", "seats", "knee", "overhead140", "parts_ib14")


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def seed(az1, el1, top=3, wa_abs_max=180.0):
    """kinematic seeding on the FIT bench only (Bench(60,160): its 60 clip frames + 160 workspace poses; never the claim
    bench, never held out): th = angle(u1, Q u3) per pose; J3 seats wd 45..110 x wa -180..170 (5 / 10 deg) ranked by the
    share of fit poses inside the lead family's th window LEAD_WIN (the dyad is the lead's at d_a1 = d_a2 = 0); a seat
    whose rest pose does not close on stop A with the fold margin (J2 unresolvable on both branches) is skipped. Returns
    the top valid seats (with the branches that resolve)."""
    Z = CB._poses_all(); ix = CB._select(60, 160)[0]; Q = Z["HG"][ix].astype(float)
    u1 = np.asarray(S.bvec(az1, el1), float); Y = lead_dyad(); R = OSN.rest(); d1 = OSN.seat(u1, 0.0)[1]
    WD, WA = np.meshgrid(np.arange(45.0, 111.0, 5.0), np.arange(-180.0, 180.0, 10.0), indexing="ij"); WD, WA = WD.ravel(), WA.ravel()
    import concept_kit as KIT; U3 = np.asarray(KIT.wdir(WD, WA), float)       # = S.w_dir, vectorised
    th = np.degrees(np.arccos(np.clip(np.einsum("pij,sj,i->sp", Q, U3, u1), -1, 1)))
    share = ((th >= LEAD_WIN[0]) & (th <= LEAD_WIN[1])).mean(1)
    # AMENDMENT 1 (before any CMA): the rest pose must sit at the lead's rest th (83.23 deg, +-TH0_TOL), so the dyad's
    # rest configuration and hence the K drive's phase (crank / lobe / flank) is the lead's. Without it the first seed
    # (-52.5, 17.5 / wd 80 wa -140, rest th 26.7) gave the drive idle: crank pressure angle 86.8 deg at rest (gate 38).
    thr = np.degrees(np.arccos(np.clip((np.einsum("ij,sj->si", R["Q0"], U3)) @ u1, -1, 1)))      # ray approximation
    out = []
    for k in np.argsort(-share, kind="stable"):
        if abs(thr[k] - TH0_LEAD) > TH0_TOL + 3.0 or abs(WA[k]) > wa_abs_max: continue
        d3 = OSN.seat(R["Q0"] @ U3[k], BASE["b3"])[1]; th0 = math.degrees(math.acos(float(np.clip(d1 @ d3, -1, 1))))
        if abs(th0 - TH0_LEAD) > TH0_TOL: continue
        # AMENDMENT 2 (before any CMA): J2's seat must lie on the shoulder's skin, r2 <= R2_MAX from GH (OSN.seat marches
        # the ray in from 260 mm; r2 = 260 means the J2 ray runs into the trunk, i.e. no buildable hub-2 seat). Each
        # (seat, branch) is a separate candidate.
        for br in (1.0, -1.0):
            az2, el2, ok = resolve_j2(d1, d3, Y["a1"], Y["a2"], br)
            if not ok: continue
            r2 = float(np.linalg.norm(OSN.seat(S.bvec(az2, el2), 0.0)[0]))
            if r2 > R2_MAX: continue
            out.append(dict(share=round(float(share[k]), 4), wd=float(WD[k]), wa=float(WA[k]), th_rest=round(th0, 2), br=br,
                            az2=round(az2, 2), el2=round(el2, 2), r1=round(float(np.linalg.norm(OSN.seat(u1, 0.0)[0])), 1), r2=round(r2, 1)))
        if len(out) >= top: break
    return out


def frozen(P, nc=110, nw=360): return CC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
def frozen_held(P): return CC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)
def frozen_flood(P, nc=110, nw=360): return CC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)
def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "seed":
        print(json.dumps(seed(float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 3,
                              float(sys.argv[5]) if len(sys.argv) > 5 else 180.0))); sys.exit()
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), knee=out.get("knee"),
                              split=out.get("split"), contacts=out.get("contact_poses"), stopped=out.get("stopped"),
                              connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    p, r = evaluate(B, par)
    print(json.dumps(dict(row=ID, obj_near1=r["gap"], plain=r.get("plain"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), seats=r.get("seats"), knee=r.get("knee"), parts=r.get("parts_ib14"),
                          secs=round(time.time() - t)), default=float))
