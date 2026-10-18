"""armarc-relay-knuckle-4r (round 104, lens A survivor): the verified lead conecut-knee-knuckle-3r UNCHANGED (seats, K drive,
metal, knee, J3 dowel stop) with a one-sided ARM-ARC RELAY at the cuff: BOTTOM's pad (knee pin b's boss) rides a carriage
on a circular Ti arc track, concentric with an arm-fixed axis a_r THROUGH GH, strapped to the upper arm. A constant-force
spring holds the carriage on its zero dowel; an end dowel caps it at PHI. The relay is a pure rotation of the whole
arm-side frame (pad, knee, E strap, J3's line) about a_r, so every chain axis still passes through GH.

RELAY SOLVE (physical, the judge's amendment): per frame (every fit-clip frame at 10 fps + every workspace pose), phi = 0
where the lead takes it; else the LEAST phi in [0, PHI] at which every kinematic gate of the lead passes (closure, K law
and stop B, fold margin, knee window, R_tol, J3 dowel stop, residual < 0.5 deg): 1-deg scan, bisection to 0.1 deg. A
spring relay cannot choose its wall, so this runs on EVERY lost pose (stretched, folded, knee, J3 stop). The relayed arm
frames HG' = HG R(a_r, phi) replace HG in CB._poses_all() while the model is built, fitted and run; the skin stays the
pose's own. A relayed pose whose metal enters the skin is a CONTACT; one whose parts collide is a JAM ('parts').

RELAY METAL (sampled, on the contact list and in ib14): the arc track (arm-fixed, unrotated frame), one radius R_t about
a_r = the highest skin radius over the arc (max over the fit-clip poses) + 4 liner + 1.5 shell, 8 wide x 2 thick, over
[theta0 - 14, theta0 + PHI + 14]; the 1.5 mm shell under it at the highest skin + 4; the carriage 24 x 14 x 7 (rotated
frame, at theta0 + phi). theta0 / s_cuff = the lead's pad centroid azimuth / station about a_r.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/armarc-relay-knuckle-4r.py check '<json>'      # Bench(60,160) fast
    CB_EXACT=1 ... frozen '<json>' [out.json]                                                                # Bench(110,360)
    hooks: bench_eval(B, params)
params: PHI (deg, one-sided +), tilt (deg of a_r from the humeral long axis), taz (deg, azimuth of the tilt: 0 lateral,
        90 anterior), sgn (+1 / -1: the relay's turning sense), hw (1 = relay metal on, 0 = the ideal relay, a bound),
        fit_relay (1 = the fit bench sees the relay too; 0 = the lead's shape frozen from a phi = 0 fit)
"""
import importlib.util, json, math, os, sys, time, contextlib
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("conecut_for_armarc", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
ID = "armarc-relay-knuckle-4r"
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
RELAY = dict(PHI=30.0, tilt=0.0, taz=0.0, sgn=1.0, hw=1, fit_relay=0)
_Z0 = CB._poses_all(); Z0 = {k: _Z0[k] for k in _Z0.files}; _ORIG = CB._poses_all
D2R = math.pi / 180


def wr(a): return (a + 180.0) % 360.0 - 180.0


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rotm(k, ang):
    """(n,3,3) rotation about unit axis k by ang (rad, array)"""
    ang = np.atleast_1d(ang); c, s = np.cos(ang), np.sin(ang); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3)[None] + s[:, None, None] * K[None] + (1 - c)[:, None, None] * (K @ K)[None]


def raxis(tilt, taz):
    """relay axis in the HG frame: +y (up the humeral long axis) tilted by tilt toward azimuth taz (0 lateral +z, 90 anterior +x)"""
    t, a = tilt * D2R, taz * D2R
    return unit(np.array([-math.sin(t) * math.sin(a), math.cos(t), -math.sin(t) * math.cos(a)]) * -1.0 * -1.0)


@contextlib.contextmanager
def patched(Z):
    CB._poses_all = (lambda: Z) if Z is not None else _ORIG
    try: yield
    finally: CB._poses_all = _ORIG


def relayed_Z(phi, ax):
    Z = dict(Z0); HG = Z0["HG"].astype(float).copy(); sel = np.abs(phi) > 1e-9
    if sel.any(): HG[sel] = HG[sel] @ rotm(ax, phi[sel] * D2R)
    Z["HG"] = HG; return Z


def gate(M, Q):
    """the lead's kinematic gates (everything in CCModel.__init__ but continuity) for humerus frames Q (n,3,3)"""
    D = M.D; P = M.p
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= P["R_tol"])
    q3p = wr(np.degrees(q[:, 2] + K["phi"])); lo, hi = float(P.get("J3MIN", -105)), float(P.get("J3MAX", 999))
    ok &= (q3p >= lo) & ((q3p <= hi) if hi < 180 else True)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    return ok


def solve_phi(M, rp, frames=None):
    """least phi in [0, PHI] (one-sided, sense sgn) per global frame at which the lead's gates pass; nan where none"""
    ax = raxis(rp["tilt"], rp["taz"]); PHI = float(rp["PHI"]); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    HG = Z0["HG"].astype(float); n = len(HG); fr = np.arange(n) if frames is None else np.asarray(frames)
    phi = np.full(n, np.nan); ok0 = gate(M, HG[fr]); phi[fr[ok0]] = 0.0
    todo = fr[~ok0]; lastfail = np.zeros(n)
    for f in np.arange(1.0, PHI + 1e-9, 1.0):
        if not len(todo): break
        okf = gate(M, HG[todo] @ rotm(ax, np.full(len(todo), sg * f * D2R)))
        hit = todo[okf]; phi[hit] = f; lastfail[todo[~okf]] = f; todo = todo[~okf]
    hit = np.nonzero(np.isfinite(phi) & (phi > 0))[0]
    lo, hi = phi[hit] - 1.0, phi[hit].copy()
    for _ in range(4):                                              # bisect to < 0.1 deg (least passing phi)
        mid = 0.5 * (lo + hi); okm = gate(M, HG[hit] @ rotm(ax, sg * mid * D2R))
        hi = np.where(okm, mid, hi); lo = np.where(okm, lo, mid)
    phi[hit] = hi
    return phi * sg, ax


# ---- relay metal --------------------------------------------------------------------------------------------------
def _basis(ax):
    e = unit(np.cross(ax, [0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0.0, 0.0])); f = np.cross(ax, e); return e, f


def relay_geometry(M1, B1, ax, rp):
    """pad centroid -> theta0, s_cuff; skin radius profile about ax at s_cuff (max over the fit-clip poses, HG frame)"""
    pad = np.asarray(M1.g["pad"][1], float); c = pad.mean(0); e, f = _basis(ax)
    s0 = float(c @ ax); th0 = math.degrees(math.atan2(float(c @ f), float(c @ e)))
    PHI = abs(float(rp["PHI"])); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    lo, hi = (th0 - 14.0, th0 + PHI + 14.0) if sg > 0 else (th0 - PHI - 14.0, th0 + 14.0)
    ths = np.arange(lo, hi + 1e-9, 2.0); ss = np.arange(s0 - 6.0, s0 + 6.0 + 1e-9, 2.0)
    clips = [i for i, k in enumerate(B1.kind) if k == "clip"][::3]
    Zp = CB._poses_all(); RS = Zp["RS"][B1.idx].astype(float); HG = Zp["HG"][B1.idx].astype(float)
    rr = np.arange(20.0, 90.0, 1.0); rmax = np.zeros((len(ss), len(ths)))
    for i in clips:
        R = RS[i] @ HG[i]
        for a, sv in enumerate(ss):
            for b, t in enumerate(ths):
                d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
                pts = (sv * ax)[None] + rr[:, None] * d[None]
                dd = B1.dist(i, pts @ R.T); out = np.nonzero(dd > 0)[0]
                r_s = float(rr[out[0]] - dd[out[0]]) if len(out) else rr[-1]
                rmax[a, b] = max(rmax[a, b], r_s)
    return dict(e=e, f=f, s0=s0, th0=th0, lo=lo, hi=hi, ths=ths, ss=ss, rskin=rmax, R_t=float(rmax.max()) + 5.5)


def relay_points(G, ax, phi_i):
    """(track+shell points in the arm frame, carriage points in the carriage frame) - HG-frame coordinates"""
    e, f, s0 = G["e"], G["f"], G["s0"]; out_arm = []
    Rt = G["R_t"]
    for t in np.arange(G["lo"], G["hi"] + 1e-9, 2.0 / max(Rt, 1) / D2R):      # 2 mm along the arc
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 4.0, s0 + 4.01, 2.0):
            out_arm.append(sv * ax + Rt * d)                                     # track underside
        b = int(np.argmin(np.abs(G["ths"] - t))); rsh = float(G["rskin"][:, b].max()) + 4.0
        for sv in np.arange(s0 - 6.0, s0 + 6.01, 2.0):
            out_arm.append(sv * ax + rsh * d)                                    # shell (on the 4 mm liner over the highest skin)
    car = []
    tc = G["th0"]; half = 12.0 / Rt / D2R
    for t in np.arange(tc - half, tc + half + 1e-9, 2.0 / Rt / D2R):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 7.0, s0 + 7.01, 2.0):
            car.append(sv * ax + (Rt - 1.0) * d)                                 # carriage / roller underside
            car.append(sv * ax + (Rt + 6.0) * d)                                 # carriage plate top
    return np.array(out_arm), np.array(car)


class _RelayBench:
    """wraps B.record: the relay metal joins every recorded (taken) pose's metal"""
    def __init__(self, B, G, ax, phi_b, RS, HG0):
        self.B, self.G, self.ax, self.phi_b = B, G, ax, phi_b
        self.arm, self.car = relay_points(G, ax, 0.0); self.RS, self.HG0 = RS, HG0; self._orig = B.record
        B.record = self.record

    def world(self, i):
        Ra = self.RS[i] @ self.HG0[i]; Rc = Ra @ rotm(self.ax, np.array([self.phi_b[i] * D2R]))[0]
        return np.r_[self.arm @ Ra.T, self.car @ Rc.T]

    def record(self, i, P):
        if P is None or not len(P): return self._orig(i, P)
        return self._orig(i, np.r_[np.asarray(P, float), self.world(i)])


def _frozen_lead(P, B1):
    M1 = CC.CCModel(B1, dict(P)); r1 = M1.run(); return M1, r1


def evaluate_relay(params, nc=60, nw=160, exact=False, verbose=False):
    """fit on Bench(60,160) fast (relay seen by the fit only if fit_relay), freeze, wear on Bench(nc,nw)"""
    t0 = time.time(); rp = dict(RELAY); rp.update({k: params[k] for k in RELAY if k in params})
    P = CC._clamp(dict(CC.PARAMS, **LEAD, **{k: v for k, v in params.items() if k not in RELAY}))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CB.Bench(n_clip=60, n_ws=160)
        M0 = CC.CCModel(B1, dict(P))                                         # init only: the lead's design, m reference
        P0 = dict(M0.p); P0["m_fix"] = [float(x) for x in M0.D.m]
        phi, ax = solve_phi(M0, rp)
        phi_fill = np.where(np.isfinite(phi), phi, 0.0)
        Zr = relayed_Z(phi_fill, ax)
        with patched(Zr if int(rp["fit_relay"]) else None):
            M1 = CC.CCModel(B1, dict(P0)); r1 = M1.run()
        fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    G = relay_geometry(M1, B1, ax, rp) if int(rp["hw"]) else None

    class Frozen(CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if exact: os.environ["CB_EXACT"] = "1"
    B = CB.Bench(n_clip=nc, n_ws=nw)
    phi_b = phi_fill[B.idx]
    with patched(Zr):
        M = Frozen(B, P2)
        if G is not None: _RelayBench(B, G, ax, phi_b, Zr["RS"][B.idx].astype(float), Z0["HG"][B.idx].astype(float))
        r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses])
    taken = np.isfinite(mins) & (mins >= 0); rel = phi_b != 0
    # the lead's own outcome per pose (phi = 0 everywhere): which relayed poses are new takes
    why = np.asarray(M.why)
    out = dict(fit_fast=fit, wear=rep, bench=[nc, nw], mode=B.mode, relay=dict(rp, axis=[round(float(x), 4) for x in ax]),
               why={k: int((why == k).sum()) for k in set(why.tolist())},
               ws_taken=int((ws & taken).sum()), ws=int(ws.sum()), overhead=[int((ws & taken & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())],
               relayed=dict(n=int((rel & ws).sum()), taken=int((rel & ws & taken).sum()), contact=int((rel & np.isfinite(mins) & (mins < 0)).sum()),
                            jam=int((rel & (why == "parts")).sum()), lost_other=int((rel & ws & ~np.isfinite(mins) & (why != "parts")).sum()),
                            clip_relayed=int((rel & ~ws).sum()),
                            phi_max=round(float(np.abs(phi_b).max()), 2) if rel.any() else 0.0),
               min_metal_taken=round(float(np.nanmin(np.where(taken, mins, np.nan))), 3) if taken.any() else None,
               near1_gap=None, secs=round(time.time() - t0, 1))
    # 1 mm near-touch reading: metal < 1 mm counts as contact
    ok1 = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 1.0
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]; wsl = [j for j, k in enumerate(B.kind) if k == "ws"]
    nz = [j for j in range(len(B.kind)) if B.res[j] is not None]
    reach1 = float(np.mean([ok1(j) for j in wsl])); fol1 = float(np.mean([ok1(j) for j in cl]))
    con1 = float(np.mean([float(np.min(B.res[j])) < 1.0 for j in nz])) if nz else 0.0
    out["near1_gap"] = CB.gap_of(rep["inband14"], fol1, reach1, con1)
    out["relayed_poses"] = [dict(i=int(j), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1),
                                 why=str(why[j]), min_mm=(round(float(mins[j]), 2) if np.isfinite(mins[j]) else None))
                            for j in range(len(B.idx)) if ws[j] and rel[j]]
    out["contacts"] = [dict(i=int(j), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1), min_mm=round(float(mins[j]), 2))
                       for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0]
    # continuity of phi along the fit clips (10 fps): max step between consecutive frames that are both taken kinematically
    names = list(Z0["NAMES"]); steps = []
    for nm in CB.FIT:
        ii = np.nonzero(Z0["CID"] == names.index(nm))[0]; ii = ii[np.argsort(Z0["FI"][ii], kind="stable")]
        p = phi[ii]; good = np.isfinite(p[1:]) & np.isfinite(p[:-1])
        if good.any(): steps.append(float(np.abs(np.diff(p))[good].max()))
    out["phi_clip_step_max"] = round(max(steps), 2) if steps else 0.0
    if G is not None: out["relay_hw"] = dict(R_t=round(G["R_t"], 1), s0=round(G["s0"], 1), th0=round(G["th0"], 1), arc=[round(G["lo"], 1), round(G["hi"], 1)],
                                              rskin=[round(float(G["rskin"].min()), 1), round(float(G["rskin"].max()), 1)])
    return out, M, B


def bench_eval(B, params):
    out, M, B2 = evaluate_relay(params); r = dict(out["wear"]); r.update(near1=out["near1_gap"]); return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen": out, M, B = evaluate_relay(par, 110, 360, exact=True)
    else: out, M, B = evaluate_relay(par)
    out["params"] = par; out["row"] = ID
    if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("relayed_poses",)}, default=float))
