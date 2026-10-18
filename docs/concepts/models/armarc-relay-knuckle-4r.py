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
RELAY = dict(PHI=30.0, tilt=0.0, taz=0.0, sgn=1.0, hw=1, hwv="plain", ds=0.0)
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
    g = getattr(M, "_scg", None)                                   # the drive's own range (J2 stop B): |dK| <= dK_lim
    if g is not None and "dK_lim" in g and getattr(D, "_dK", None) is not None and len(D._dK) == len(Q):
        ok &= np.abs(np.asarray(D._dK, float)) <= float(g["dK_lim"]) + 1e-9
    return ok


def solve_phi_Q(M, rp, HG):
    """least phi in [0, PHI] (one-sided, sense sgn) for humerus frames HG (n,3,3) at which the lead's gates pass; nan
    where none (1-deg scan, bisection to < 0.1 deg)"""
    ax = raxis(rp["tilt"], rp["taz"]); PHI = float(rp["PHI"]); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    n = len(HG); phi = np.full(n, np.nan); ok0 = gate(M, HG); phi[ok0] = 0.0
    todo = np.nonzero(~ok0)[0]
    for f in np.arange(1.0, PHI + 1e-9, 1.0):
        if not len(todo): break
        okf = gate(M, HG[todo] @ rotm(ax, np.full(len(todo), sg * f * D2R)))
        phi[todo[okf]] = f; todo = todo[~okf]
    hit = np.nonzero(np.isfinite(phi) & (phi > 0))[0]
    if len(hit):
        lo, hi = phi[hit] - 1.0, phi[hit].copy()
        for _ in range(4):                                          # bisect to < 0.1 deg (least passing phi)
            mid = 0.5 * (lo + hi); okm = gate(M, HG[hit] @ rotm(ax, sg * mid * D2R))
            hi = np.where(okm, mid, hi); lo = np.where(okm, lo, mid)
        phi[hit] = hi
    return phi * sg, ax


def solve_phi(M, rp, frames=None):
    """least phi per global frame (Z0 order); nan where none"""
    HG = Z0["HG"].astype(float); n = len(HG); fr = np.arange(n) if frames is None else np.asarray(frames)
    phi = np.full(n, np.nan); ph, ax = solve_phi_Q(M, rp, HG[fr]); phi[fr] = ph
    return phi, ax


def flood_relay(M, rp, step_deg=2.0, passive_jump=10.0, active_jump=25.0):
    """CONTINUITY RULE (CLAUDE.md; the lead's connected_full reading, minarc-stop-knuckle-4r-mechanism.py flood grid
    'full'): nodes = every pose of the 15-deg workspace envelope grid (Z0 'Workspace (envelope)', 1432 poses; the
    bench's 360 are a 1-in-4 subsample) at which the relayed lead closes (least phi in [0, PHI] exists); edges = grid
    neighbours whose 2-deg HG slerp closes at EVERY frame with the least-phi relay, the relay never steps > 10 deg,
    the passive K drive angle dK and knee pins qa / qb never > 10 deg, the actives never > 25 deg; seeds = phi = 0
    nodes in the lead's state A (kstate 0, as the lead's own flood). Kinematic only (skin is the bench's job).
    -> dict(global env index -> connected bool), phi per env node, stats"""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    names = list(Z0["NAMES"]); allw = np.nonzero(Z0["CID"] == names.index("Workspace (envelope)"))[0]
    Ha = Z0["HG"][allw].astype(float); ph, ax = solve_phi_Q(M, rp, Ha); feas = np.isfinite(ph)
    D = M.D
    Qa = Ha.copy(); Qa[feas] = Ha[feas] @ rotm(ax, ph[feas] * D2R)
    D.ik(Qa); sta = np.asarray(getattr(D, "_state", np.zeros(len(Qa))), float).copy()
    Pz = Z0["POSE"][allw]; keyf = {tuple(np.round(Pz[k, :3], 1)): k for k in range(len(allw)) if feas[k]}
    valsf = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]
    edges = []
    for a in keyf.values():
        x = tuple(np.round(Pz[a, :3], 1))
        for d in range(3):
            j = valsf[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(valsf[d]):
                    y = list(x); y[d] = valsf[d][jj]; b = keyf.get(tuple(y))
                    if b is not None and a < b: edges.append((a, b))
    segs = []; Hs_all = []; off = 0
    for a, b in edges:                                               # batch every edge's slerp frames
        R2 = Rot.from_matrix(np.stack([Ha[a], Ha[b]])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
        m = max(2, int(math.ceil(ang / step_deg)) + 1); Hs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
        segs.append((off, m)); Hs_all.append(Hs); off += m
    H = np.concatenate(Hs_all); phs, _ = solve_phi_Q(M, rp, H); okf = np.isfinite(phs)
    Qs = H.copy(); Qs[okf] = H[okf] @ rotm(ax, phs[okf] * D2R)
    q, ok, _, _, _, s = D.ik(Qs); dK = getattr(D, "_dK", None); Kn = D.knee(s)
    cols = [np.degrees(q[:, 0]), np.degrees(q[:, 1]), np.degrees(q[:, 2] + Kn["phi"]), phs]
    pas = [phs]
    if dK is not None and len(dK) == len(Qs): cols.append(np.degrees(np.asarray(dK, float))); pas.append(cols[-1])
    for k in ("qa", "qb"):
        if k in Kn: cols.append(np.degrees(np.asarray(Kn[k], float))); pas.append(cols[-1])
    eok = np.zeros(len(edges), bool); why = {"open": 0, "phi_jump": 0, "passive_jump": 0, "active_jump": 0}
    for e, (o, m) in enumerate(segs):
        sl = slice(o, o + m)
        if not okf[sl].all(): why["open"] += 1; continue
        if (np.abs(np.diff(phs[sl])) > passive_jump).any(): why["phi_jump"] += 1; continue
        dpas = max(float(np.abs(wr(np.diff(c[sl]))).max()) for c in pas[1:]) if len(pas) > 1 else 0.0
        dact = max(float(np.abs(wr(np.diff(c[sl]))).max()) for c in cols[:3])
        if dpas > passive_jump: why["passive_jump"] += 1; continue
        if dact > active_jump: why["active_jump"] += 1; continue
        eok[e] = True
    adj = {}
    for e, (a, b) in enumerate(edges):
        if eok[e]: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    conn = np.zeros(len(allw), bool); front = [k for k in keyf.values() if ph[k] == 0 and sta[k] == 0]
    for k in front: conn[k] = True
    while front:
        nxt = []
        for a in front:
            for b in adj.get(a, []):
                if not conn[b]: conn[b] = True; nxt.append(b)
        front = nxt
    rel = feas & (ph != 0)
    stats = dict(env=int(len(allw)), env_ok=int(feas.sum()), env_ok_phi0=int((feas & (ph == 0)).sum()), env_relayed=int(rel.sum()),
                 env_relayed_connected=int((rel & conn).sum()), env_phi0_connected=int((feas & (ph == 0) & conn).sum()),
                 edges=len(edges), edges_ok=int(eok.sum()), edge_fail=why, seeds=int(((ph == 0) & feas & (sta == 0)).sum()))
    return {int(allw[k]): bool(conn[k]) for k in range(len(allw))}, {int(allw[k]): float(ph[k]) for k in range(len(allw))}, stats


# ---- relay metal (post-run, explicit: the lead's run writes B.res itself, so a B.record hook is not enough) -------------
ARM_LIFT_MEMBERS = (5, 6)                                  # pad (arm member) and knee link: lifted fully onto the carriage


def _basis(ax):
    e = unit(np.cross(ax, [0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0.0, 0.0])); f = np.cross(ax, e); return e, f


def _rad(X, ax):
    return X - (X @ ax)[:, None] * ax[None]


def relay_geometry(M1, B1, ax, rp):
    """HG-frame geometry from the fitted lead (phi = 0): pad centroid azimuth theta0 and station s0 about ax; the skin
    radius about ax over the arc (ARM skin: first exit of a ray from the axis; p90 over the fit-bench clip poses - the
    liner is 4 mm compliance; contact at every bench pose is still checked on the real posed skin); the circular track /
    slotted shell radius R_t = max over the arc of (skin p90 + 4 liner + 1.5 shell) [+ 2 track for 'vroller'];
    carriage top = R_t + h_c; pad lift dh = carriage top - the lead's pad underside radius (>= 0)."""
    i0 = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip" and M1.kin_ok[j]][0]
    m, X = M1.rigid["pad"]; padS = M1.world(m, i0, X) @ M1.RS[i0]               # thorax -> scapula frame
    padH = padS @ M1.Q[i0]                                                       # -> HG frame (member 5 = Q)
    e, f = _basis(ax); c = padH.mean(0); s_pad = float(c @ ax); ds = float(rp.get("ds", 0.0)); s0 = s_pad + ds   # s0 = the track station
    th0 = math.degrees(math.atan2(float(c @ f), float(c @ e)))
    rpad = float(np.linalg.norm(_rad(padH, ax), axis=1).min())
    for nm in ("boss", "knee"):                                                  # the knee stack's lowest point rides on the carriage
        m_, X_ = M1.rigid[nm]; h_ = (M1.world(m_, i0, X_) @ M1.RS[i0]) @ M1.Q[i0]
        rpad = min(rpad, float(np.linalg.norm(_rad(h_, ax), axis=1).min()))
    PHI = abs(float(rp["PHI"])); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    hc = 0.5 * CAR_W / max(rpad, 30.0) / D2R
    lo, hi = (th0 - hc - 3.0, th0 + PHI + hc + 3.0) if sg > 0 else (th0 - PHI - hc - 3.0, th0 + hc + 3.0)
    ths = np.arange(lo, hi + 1e-9, 2.0); ss = np.arange(s0 - 0.5 * SH_W, s0 + 0.5 * SH_W + 1e-9, 2.0)
    clips = [j for j in range(len(B1.idx)) if B1.kind[j] == "clip"]
    rr = np.arange(10.0, 110.0, 1.0); prof = np.full((len(clips), len(ss), len(ths)), np.nan)
    for a, j in enumerate(clips):
        R = M1.RS[j] @ M1.Q[j]
        pts = []
        for sv in ss:
            for t in ths:
                d = math.cos(t * D2R) * e + math.sin(t * D2R) * f; pts.append((sv * ax)[None] + rr[:, None] * d[None])
        pts = np.concatenate(pts); dd = B1.dist(j, pts @ R.T).reshape(len(ss), len(ths), len(rr))
        inside = dd < 0
        for b in range(len(ss)):
            for k in range(len(ths)):
                ins = np.nonzero(inside[b, k])[0]
                if not len(ins): continue
                first_out = ins[0] + np.argmax(~inside[b, k, ins[0]:]) if (~inside[b, k, ins[0]:]).any() else len(rr) - 1
                prof[a, b, k] = rr[first_out] - dd[b, k, first_out]
    p90 = np.nanpercentile(prof, 90, axis=0)                                     # (ss, ths)
    hw = rp.get("hwv", "plain")
    R_liner = float(np.nanmax(p90)) + 4.0
    R_t = R_liner + 1.5 + (2.0 if hw == "vroller" else 0.0)
    h_c = 5.5 if hw == "vroller" else 1.7                                        # carriage above the track / shell top
    dh = max(0.0, R_t + h_c - rpad) if abs(ds) < 1e-9 else 0.0     # ds != 0: the pad hangs from a bracket, no lift
    # the movers (knee link 6, member 3's E strap / boss) that pass over the track band in ANY fit-bench pose must clear
    # its top + the carriage by 1 mm after one rigid lift (parts are rigid: the lift is the max over poses, not per pose)
    band_s = (s0 - 0.5 * SH_W - 2.0, s0 + 0.5 * SH_W + 2.0); need = 0.0
    for j in np.nonzero(M1.kin_ok)[0]:
        for nm in ("knee", "E", "boss"):
            m_, X_ = M1.rigid[nm]; h_ = (M1.world(m_, j, X_) @ M1.RS[j]) @ M1.Q[j]
            sv = h_ @ ax; az = np.degrees(np.arctan2(h_ @ f, h_ @ e)); azr = (az - lo + 180.0) % 360.0 - 180.0 + lo
            sel = (sv >= band_s[0]) & (sv <= band_s[1]) & (azr >= lo) & (azr <= hi)
            if sel.any(): need = max(need, R_t + 1.0 - float(np.linalg.norm(_rad(h_[sel], ax), axis=1).min()))
    dh = max(dh, need)
    return dict(e=e, f=f, s0=s0, s_pad=s_pad, ds=ds, th0=th0, lo=lo, hi=hi, ths=ths, ss=ss, p90=p90, R_liner=R_liner, R_t=R_t, h_c=h_c, dh=dh,
                rpad=rpad, hw=hw, sg=sg)


CAR_W, CAR_L, SH_W, TR_W = 24.0, 14.0, 12.0, 8.0


def relay_points(G, ax):
    """(shell + track points, arm-fixed HG frame), (carriage points, carriage frame = HG' at phi) - ~1 pt / 4 mm2"""
    e, f, s0, Rt = G["e"], G["f"], G["s0"], G["R_t"]; arm = []; aib = []; cib = []
    for t in np.arange(G["lo"], G["hi"] + 1e-9, 2.0 / Rt / D2R):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        b = int(np.argmin(np.abs(G["ths"] - t))); rsk = float(np.nanmax(G["p90"][:, b])) + 4.0
        for sv in np.arange(s0 - 0.5 * SH_W, s0 + 0.5 * SH_W + 0.01, 2.0):
            arm.append(sv * ax + (rsk if G["hw"] == "vroller" else Rt - 1.5) * d); aib.append(True)   # shell underside (plain: the slotted circular shell)
            arm.append(sv * ax + Rt * d); aib.append(False)                                            # track / shell top: contact / jam only
    car = []; half = 0.5 * CAR_W / Rt / D2R; tc = G["th0"]
    for t in np.arange(tc - half, tc + half + 1e-9, 2.0 / Rt / D2R):
        d = math.cos(t * D2R) * e + math.sin(t * D2R) * f
        for sv in np.arange(s0 - 0.5 * CAR_L, s0 + 0.5 * CAR_L + 0.01, 2.0):
            car.append(sv * ax + (Rt + 0.2) * d); cib.append(True); car.append(sv * ax + (Rt + G["h_c"]) * d); cib.append(False)
    if abs(G["ds"]) > 1e-9:                                   # bracket (2 mm Ti, 10 wide) from the carriage edge up/down the arm to the pad
        sg_ = 1.0 if G["s_pad"] > s0 else -1.0; s_a = s0 + sg_ * 0.5 * CAR_L; s_b = G["s_pad"]
        r_a = Rt + G["h_c"]; r_b = G["rpad"] + G["dh"]; hb = 5.0 / Rt / D2R
        for sv in np.arange(min(s_a, s_b), max(s_a, s_b) + 0.01, 2.0):
            r = r_a + (r_b - r_a) * (sv - s_a) / (s_b - s_a)
            for t in np.arange(tc - hb, tc + hb + 1e-9, 2.0 / Rt / D2R):
                d = math.cos(t * D2R) * e + math.sin(t * D2R) * f; car.append(sv * ax + r * d); cib.append(True)
    G["arm_ib"] = np.array(aib, bool); G["car_ib"] = np.array(cib, bool)
    return np.array(arm), np.array(car)


def lift_fn(G, ax):
    """radial lift about ax (HG' frame) of the arm-side chain metal onto the carriage: pad, knee link fully; member 3
    (E strap, pin b boss) by a ramp in s from s0 + 35 (no lift: hub 3 is at s > -45) to s0 + 15 (full)"""
    dh = G["dh"]; s_full, s_none = G["s_pad"] + 15.0, G["s_pad"] + 35.0
    def lift(m, Xh):
        if dh <= 0 or not len(Xh): return Xh
        if m in ARM_LIFT_MEMBERS: w = np.ones(len(Xh))
        elif m == 3: w = np.clip((s_none - Xh @ ax) / (s_none - s_full), 0.0, 1.0)
        else: return Xh
        r = _rad(Xh, ax); n = np.linalg.norm(r, axis=1, keepdims=True); n[n < 1e-9] = 1.0
        return Xh + (dh * w)[:, None] * r / n
    return lift


def rerecord(M, B, G, ax, phi_b, HG0):
    """recompute every recorded pose's metal: chain metal with the arm-side lift + relay hardware; jams (relay metal
    or lifted metal within 1 mm of a non-adjacent body) -> pose lost ('jam'); metal < 0 -> contact"""
    lift = lift_fn(G, ax) if G is not None else None
    arm, car = relay_points(G, ax) if G is not None else (np.zeros((0, 3)), np.zeros((0, 3)))
    names = list(M.rigid) + list(M.link_pts); parts = list(M.rigid.values()) + list(M.link_pts.values())
    why = np.asarray(M.why, dtype=object).copy(); jam = []; lift_ib = []; rel_ib = []
    for i in range(len(B.idx)):
        if B.res[i] is None and why[i] not in ("contact", "skin"): continue
        if B.res[i] is None: continue
        RS = M.RS[i]; Qp = M.Q[i]; Q0 = HG0[i]
        P = []; per = {}
        for nm, (m, X) in zip(names, parts):
            w = M.world(m, i, X)                                           # thorax frame
            if lift is not None and (m in ARM_LIFT_MEMBERS or m == 3):
                h = (w @ RS) @ Qp; h = lift(m, h); w = (h @ Qp.T) @ RS.T
            per[nm] = w; P.append(w)
        chain = np.concatenate(P)
        relay = np.zeros((0, 3))
        if len(arm):
            wa = (arm @ Q0.T) @ RS.T; wc = (car @ Qp.T) @ RS.T; relay = np.r_[wa, wc]
            # jam: track/shell vs the chain bodies that move over it (knee link 6, member 3 = E strap / boss / hub 3, link 2)
            from scipy.spatial import cKDTree
            tr = cKDTree(wa); tc_ = cKDTree(wc)
            dpt = {n: float(tr.query(per[n])[0].min()) - 1.0 for n in ("knee", "E", "boss", "hub3", "L2") if n in per}   # ~2 mm spacing: gap ~ d - 1
            dpc = {n: float(tc_.query(per[n])[0].min()) - 1.0 for n in ("E", "hub3", "L2") if n in per}
            dmin, dcar = min(dpt.values()), min(dpc.values())
            if min(dmin, dcar) < 1.0:
                jam.append(dict(i=i, kind=B.kind[i], track_mm=round(dmin, 2), track_part=min(dpt, key=dpt.get), carriage_mm=round(dcar, 2),
                                carriage_part=min(dpc, key=dpc.get), phi=round(float(phi_b[i]), 1)))
                B.res[i] = None; why[i] = "jam"; continue
        dall = B.dist(i, np.r_[chain, relay]); nC = len(chain)
        rib = np.r_[G["arm_ib"], G["car_ib"]] if len(arm) else np.zeros(0, bool)
        d = np.r_[dall[:nC], dall[nC:][rib]]                               # in-band samples: skin-facing surfaces only (1 per 4 mm2)
        dtop = dall[nC:][~rib] if len(arm) else np.zeros(0)                # tops: contact only
        dc = [float(dtop.min())] if len(dtop) else []
        for m, Pc in M.contact:
            w = M.world(m, i, Pc)
            if lift is not None and (m in ARM_LIFT_MEMBERS or m == 3):
                h = (w @ RS) @ Qp; h = lift(m, h); w = (h @ Qp.T) @ RS.T
            dc.append(float(B.dist(i, w).min()))
        dc = min(dc) if dc else 1e9
        B.res[i] = np.r_[d, dc] if dc < 0 else d
        if min(dc, float(d.min())) < 0: why[i] = "contact"
        elif why[i] == "contact": why[i] = ""
        if B.kind[i] == "clip" and float(d.min()) >= 0:
            lift_ib.append(d[:nC]); rel_ib.append(d[nC:])
    M.why = why
    ib = lambda a: round(float(((a >= 2) & (a <= 14)).mean()), 4) if len(a) else None
    lc = np.concatenate(lift_ib) if lift_ib else np.zeros(0); rc = np.concatenate(rel_ib) if rel_ib else np.zeros(0)
    return dict(jams=jam, ib14_chain_only=ib(lc), ib14_relay_metal=ib(rc), n_relay_pts=int(len(arm) + len(car)), n_relay_ib_pts=int(G["arm_ib"].sum() + G["car_ib"].sum()) if len(arm) else 0, model_v=2,
                relay_median_mm=round(float(np.median(rc)), 2) if len(rc) else None)


def held_bench():
    """the lead family's held-out bench (every fit-clip frame and ws pose not in Bench(110,360) / Bench(60,160); exact)"""
    sp_ = importlib.util.spec_from_file_location("pk_polish_v_armarc", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); return PVm.held_bench()


def evaluate_relay(params, nc=60, nw=160, exact=False, verbose=False):
    """fit the lead on Bench(60,160) fast at phi = 0 (frozen shape), solve phi per frame with the FITTED lead's gates,
    wear on Bench(nc,nw) with the relayed arm-side frames + the relay metal + the arm-side lift"""
    t0 = time.time(); rp = dict(RELAY); rp.update({k: params[k] for k in RELAY if k in params})
    P = CC._clamp(dict(CC.PARAMS, **LEAD, **{k: v for k, v in params.items() if k not in RELAY}))
    old = os.environ.pop("CB_EXACT", None)
    try:
        B1 = CB.Bench(n_clip=60, n_ws=160)
        M1 = CC.CCModel(B1, dict(P)); r1 = M1.run()
        fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        ax = raxis(rp["tilt"], rp["taz"])
        G = relay_geometry(M1, B1, ax, rp) if int(rp["hw"]) and float(rp["PHI"]) > 0 else None
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    phi, ax = solve_phi(M1, rp)
    phi_fill = np.where(np.isfinite(phi), phi, 0.0)
    Zr = relayed_Z(phi_fill, ax)

    class Frozen(CC.CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if exact: os.environ["CB_EXACT"] = "1"
    B = held_bench() if nc == -1 else CB.Bench(n_clip=nc, n_ws=nw)
    phi_b = phi_fill[B.idx]
    with patched(Zr):
        M = Frozen(B, P2); r = M.run()
    plain = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}     # ideal relay, no relay metal / lift
    hwrep = rerecord(M, B, G, ax, phi_b, Z0["HG"][B.idx].astype(float)) if G is not None else {}
    rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    conn_out = None
    if os.environ.get("ARMARC_FLOOD", "0") == "1" and float(rp["PHI"]) > 0:      # the continuity rule: reach on the CONNECTED set
        tf = time.time(); cmap, _, fst = flood_relay(M1, rp)
        ws_ = np.array(B.kind) == "ws"
        tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        drop = [j for j in tk if ws_[j] and phi_b[j] != 0 and not cmap.get(int(B.idx[j]), False)]
        drop0 = [j for j in tk if ws_[j] and phi_b[j] == 0 and not cmap.get(int(B.idx[j]), False)]
        static = dict(rep)
        for j in drop: B.res[j] = None
        rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        conn_out = dict(static=static, connected=dict(rep), dropped_relayed=len(drop), phi0_taken_not_connected=len(drop0),
                        dropped=[[B.poses[j][k] for k in ("plane", "elev", "axial")] + [round(float(phi_b[j]), 1)] for j in drop],
                        flood=fst, secs=round(time.time() - tf, 1))
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses])
    taken = np.isfinite(mins) & (mins >= 0); rel = phi_b != 0
    why = np.asarray(M.why)
    out = dict(fit_fast=fit, wear=rep, wear_ideal_relay=plain, bench=[nc, nw], mode=B.mode, relay=dict(rp, axis=[round(float(x), 4) for x in ax]),
               why={str(k): int((why == k).sum()) for k in set(why.tolist())},
               ws_taken=int((ws & taken).sum()), ws=int(ws.sum()), overhead=[int((ws & taken & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())],
               relayed=dict(n=int((rel & ws).sum()), taken=int((rel & ws & taken).sum()), contact=int((rel & np.isfinite(mins) & (mins < 0)).sum()),
                            jam=int((rel & ((why == "parts") | (why == "jam"))).sum()), lost_other=int((rel & ws & ~np.isfinite(mins) & (why != "parts") & (why != "jam")).sum()),
                            clip_relayed=int((rel & ~ws).sum()),
                            phi_max=round(float(np.abs(phi_b).max()), 2) if rel.any() else 0.0),
               min_metal_taken=round(float(np.nanmin(np.where(taken, mins, np.nan))), 3) if taken.any() else None,
               near1_gap=None, hw=hwrep, continuity=conn_out, secs=round(time.time() - t0, 1))
    ok1 = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 1.0
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]; wsl = [j for j, k in enumerate(B.kind) if k == "ws"]
    nz = [j for j in range(len(B.kind)) if B.res[j] is not None]
    reach1 = float(np.mean([ok1(j) for j in wsl])); fol1 = float(np.mean([ok1(j) for j in cl]))
    con1 = float(np.mean([float(np.min(B.res[j])) < 1.0 for j in nz])) if nz else 0.0
    out["near1_gap"] = CB.gap_of(rep["inband14"], fol1, reach1, con1)
    # lead's own wall per relayed pose (phi = 0 run of the same frozen shape is the PHI = 0 case; here: the kin gate split)
    out["relayed_poses"] = [dict(i=int(j), pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1),
                                 why=str(why[j]), min_mm=(round(float(mins[j]), 2) if np.isfinite(mins[j]) else None))
                            for j in range(len(B.idx)) if ws[j] and rel[j]]
    out["contacts"] = [dict(i=int(j), kind=B.kind[j], pose=[B.poses[j][k] for k in ("plane", "elev", "axial")], phi=round(float(phi_b[j]), 1), min_mm=round(float(mins[j]), 2))
                       for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0]
    names = list(Z0["NAMES"]); steps = []
    for nm in CB.FIT:
        ii = np.nonzero(Z0["CID"] == names.index(nm))[0]; ii = ii[np.argsort(Z0["FI"][ii], kind="stable")]
        p = phi[ii]; good = np.isfinite(p[1:]) & np.isfinite(p[:-1])
        if good.any(): steps.append(float(np.abs(np.diff(p))[good].max()))
    out["phi_clip_step_max"] = round(max(steps), 2) if steps else 0.0
    out["phi_clip_relayed"] = int(sum(int((np.isfinite(phi[np.nonzero(Z0["CID"] == names.index(nm))[0]]) & (phi[np.nonzero(Z0["CID"] == names.index(nm))[0]] != 0)).sum()) for nm in CB.FIT))
    if G is not None: out["relay_hw"] = dict(hw=G["hw"], R_t=round(G["R_t"], 1), R_liner=round(G["R_liner"], 1), h_c=G["h_c"], dh_lift=round(G["dh"], 2), rpad=round(G["rpad"], 1),
                                              s0=round(G["s0"], 1), s_pad=round(G["s_pad"], 1), ds=G["ds"], th0=round(G["th0"], 1), arc=[round(G["lo"], 1), round(G["hi"], 1)],
                                              skin_p90=[round(float(np.nanmin(G["p90"])), 1), round(float(np.nanmax(G["p90"])), 1)])
    out["_M"] = None
    return out, M, B


# ---- gravity determinacy (judge 1.4): generalised gravity torque along the relay's null space ------------------------
# moving-body masses (g) from the lead's gen-9 full CAD build (pipeline/full-exo/designs/user_conecut_knee/build.json):
# member 1 = link 1a + J1/K bearings, K cap + clock spring; 7 = link 1b + J2 bearings, cap, dowels, crank pin; 9 = bell
# crank + bearings + roller; 2 = link 2 + lobe ring + J3 bearings + cap; 3 = member 3 (J3 disc, E strap, boss, pin a);
# 6 = knee link + its MR63ZZ pair; 5 = pad mount + pin b + carriage (est. 8 g; BOTTOM's bar stays on the arm shell)
MASS_G = {1: 24.7, 7: 21.0, 9: 10.3, 2: 25.1, 3: 17.2, 6: 5.8, 5: 8.0}


def gravity_check(params, dphi=2.0):
    """finite difference of the moving bodies' potential energy along the relay (arm fixed, carriage turned by dphi):
    tau(phi=0) = -dPE/dphi per fit-bench pose closed at both phi; the spring preload must exceed 1.5 x max(tau+)"""
    rp = dict(RELAY); rp.update({k: params[k] for k in RELAY if k in params})
    P = CC._clamp(dict(CC.PARAMS, **LEAD)); old = os.environ.pop("CB_EXACT", None)
    B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P)); M1.run()
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]; ax = raxis(rp["tilt"], rp["taz"]); sg = 1.0 if float(rp.get("sgn", 1)) >= 0 else -1.0
    n = len(Z0["HG"]); com = {}
    for tag, ph in (("0", 0.0), ("d", sg * dphi)):
        Zr = relayed_Z(np.full(n, ph), ax)
        class Fz(CC.CCModel):
            def fit(self):
                for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                          "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "cyl_r"):
                    if hasattr(M1, a): setattr(self, a, getattr(M1, a))
                self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        B = CB.Bench(n_clip=60, n_ws=160)
        with patched(Zr):
            M = Fz(B, P2); M.fit()
        ok = np.asarray(M.kin_ok, bool); E = np.full(len(B.idx), np.nan)
        for i in np.nonzero(ok)[0]:
            e_ = 0.0
            for nm, (m, X) in list(M.rigid.items()) + list(M.link_pts.items()):
                if m in MASS_G: pass
            for m, mass in MASS_G.items():
                pts = [M.world(mm, i, X) for mm, X in list(M.rigid.values()) + list(M.link_pts.values()) if mm == m]
                if pts: e_ += mass * 1e-3 * 9.81 * float(np.concatenate(pts)[:, 1].mean()) * 1e-3     # J; world +y up
            E[i] = e_
        com[tag] = (E, ok, B)
    if old is not None: os.environ["CB_EXACT"] = old
    E0, ok0, B = com["0"]; Ed, okd, _ = com["d"]; both = ok0 & okd
    tau = -(Ed - E0) / (dphi * D2R)                            # N.m pushing phi up (positive = the relay would drift open)
    kind = np.array(B.kind)
    t = tau[both]
    return dict(n=int(both.sum()), tau_max_open=round(float(np.nanmax(t)), 4), tau_p95=round(float(np.nanpercentile(t, 95)), 4),
                tau_min=round(float(np.nanmin(t)), 4), tau_clip_max=round(float(np.nanmax(tau[both & (kind == "clip")])), 4),
                preload_needed_Nm=round(1.5 * max(0.0, float(np.nanmax(t))), 4), masses_g=MASS_G, dphi=dphi)


def bench_eval(B, params):
    out, M, B2 = evaluate_relay(params); r = dict(out["wear"]); r.update(near1=out["near1_gap"]); return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "gravity":
        print(json.dumps(gravity_check(par))); sys.exit(0)
    if mode == "floodonly":                                         # kinematic continuity flood only (the fitted lead, phi solve)
        rp = dict(RELAY); rp.update({k: par[k] for k in RELAY if k in par}); os.environ.pop("CB_EXACT", None)
        B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, CC._clamp(dict(CC.PARAMS, **LEAD))); M1.run()
        t = time.time(); cmap, phmap, st = flood_relay(M1, rp); st["secs"] = round(time.time() - t, 1)
        out = dict(params=par, flood=st, connected=[k for k, v in cmap.items() if v], phi={k: v for k, v in phmap.items() if np.isfinite(v)})
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), default=float)
        print(json.dumps(st)); sys.exit(0)
    if mode == "frozen": out, M, B = evaluate_relay(par, 110, 360, exact=True)
    elif mode == "held": out, M, B = evaluate_relay(par, -1, -1, exact=True)
    else: out, M, B = evaluate_relay(par)
    out.pop("_M", None)
    out["params"] = par; out["row"] = ID
    if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("relayed_poses",)}, default=float))
