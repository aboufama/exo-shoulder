"""crossed-skin-tracks: two skin-shaped tracks that cross at a radial swivel - no intermediate links at all.
(3 ACTIVE DOF: s, q2, t; 1 PASSIVE: the radial slide set by the closure.)

Topology (scapula handler -> user's upper-arm cuff), docs/concepts/catalogue.json entry `crossed-skin-tracks`:
    T_S  halo track fixed to the scapula handler: an iso-motion contour of the scapula-frame skin around the acromion
         summit (pipeline/conformal/analysis/skin_motion_map_14.json, thr mm), 8 x 5 mm rail section, running surface
         at rho_S (underside rho_S - 5 = the K3 requirement over the 16 mm carriage width)
    J1   carriage A (20 x 16, [rho_S - 5, rho_S + 4]) on T_S - coordinate s (arc along the halo)            ACTIVE
    J2   thin-section swivel bearing (axis p2 = the radial line through the crossing, OD 22, height hb)    ACTIVE
    P    radial slide, direction p2 (two rods beside the outer rail, bushings in carriage B)               PASSIVE
    J3   carriage B (20 x 16) HANGING BELOW the arm track T_H (its bottom plate 4 mm under the rail)        ACTIVE
    T_H  arm track fixed to the humerus (circle {angle(v, W) = a2} in the humerus frame, or the deltoid oval),
         8 x 5 rail, cantilevered from its end nearest BOTTOM's bar by a 14 x 6 neck strap
    -> BOTTOM bar / cuff (the user's parts, not modelled as metal).
DOF: the crossing of two curves on the sphere is isolated when transversal, so the arm orientation fixes s and t;
q2 is the angle between the two track tangents at the crossing. Three joints the arm drives and a sensor reads.
The slide value L = rho_H(t) - rho_S(s) - stack is fixed by the tracks' radii at the crossing (a translation along a
line through GH changes no orientation) -> passive, closure-set, cannot sag.

Spec corrections (docs/concepts/crossed-skin-tracks.md):
  * the swivel axis is the radial line through the crossing, which also passes through the OUTER rail: carriage B must
    hang below T_H (bottom plate under the rail) and the slide guide must sit beside the rail (a prismatic joint has a
    direction, not a line). Radial stack at L = 0: A over its rail 4 + bearing hb + B plate 4 + outer rail 5
    = 13 + hb = `stack` (spec: 9-13 + 5 margin; here 15-19).
  * the slide rods stick out above B, so nothing can hold T_H along its travel: T_H is an OPEN arc held at one end
    by the neck (a closed T_H is impossible); T_S may be closed (web-supported from the handler) or trimmed.
  * rails and carriages follow the track radius (bogies); each rail radius is slope-limited (<= 0.5 mm/mm).
Geometry (idealised, every part at its real size; skin-facing faces sampled on a 2 mm grid = 1 point / 4 mm2 at the
part's real radius, like tools/concept_baseline.py): K3 requirement = the first radius on a ray from GH with skin
distance >= 2 mm and no skin over the next 15 mm; a rigid member's radius per sample = quantile q of that over the
poses the chain closes in (clip + workspace bench poses; held-out clips never used).
Taken (bench rules): crossing of the design's sign, transversal (>= 20 deg between tangents), carriages inside their
track arcs, slide 0..Lmax, no interference between non-adjacent parts (>= 1 mm radial where angularly within the
half-widths + 1 mm), fit-clip frames followed on EVERY 10 fps frame (no jump > 25 deg in s, t (arc deg) or q2 since
the last followed frame), and no metal inside the body (B.dist; skin-facing samples + the worst top/side sample).

    python3 docs/concepts/models/crossed-skin-tracks.py check     # rest / overhead / across / behind on Bench(20, 40)
    python3 docs/concepts/models/crossed-skin-tracks.py sweep     # coarse -> refine sweep on Bench(60, 160)
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import concept_bench as CB                                                 # noqa: E402
import body_pose as BP                                                     # noqa: E402

ID = "crossed-skin-tracks"
D2R = math.pi / 180
SP = 2.0                       # mm sample grid (1 point / 4 mm2)
R_REF = 65.0                   # mm, reference radius for the fine (pre-fit) direction grids
RAIL_W, RAIL_H = 10.0, 3.0     # track section: a Ti strip 10 wide x 3 radial (the strip IS the guide: no separate rail)
CAR_L, CAR_W = 20.0, 14.0      # carriage footprint: iglidur C-slider, 2 mm walls each side of the strip
A_UP = 2.0                     # carriage A plate above the inner strip's top (running surface)
B_DN = 2.0                     # carriage B plate below the outer strip's underside
LIP = 1.5                      # slider lips hooking under the inner strip's edges (A) / over the outer strip's edges (B)
BRG_R = 9.0                    # swivel: 6700 bearing (10 x 15 x 4) in a 18 mm housing; hb = stack - A_UP - B_DN - RAIL_H
NECK_W, NECK_T = 14.0, 6.0     # neck strap (K7)
CLEAR = 2.0                    # K3 clearance
FREE = 15.0                    # K3: no skin over the next 15 mm of the ray
FLIP = 25.0                    # deg per 10 fps frame (K2)
TRANS = 20.0                   # deg, minimum angle between the two track tangents at the crossing
GAP = 1.0                      # mm between parts without a shared joint
SLOPE = 0.5                    # mm radius change per mm along a rail / strap (bogie)
MARGIN = 15.0                  # mm of track beyond the extreme carriage centre (half carriage + stop)
R_FOOT_I, R_FOOT_O = 45.0, 60.0  # mm: radii that convert the carriage half-length to track arc (<= the real radii: conservative)
RHO_TI = 4.43e-3               # g/mm3
BAR_WB = np.array([0.0, -0.0713, 0.9975]); BAR_DB = np.array([0.0, -0.9975, -0.0713])   # BOTTOM's bar (humerus frame)
BAR_P = 40.0 * BAR_DB + 67.5 * BAR_WB

PARAMS = dict(thr=13, el_off=0.0, f1c=0.0, f1s=0.0, f2c=0.0, f2s=0.0, trim_S=1,
              th="circle", W_d=115.0, W_a=-18.0, a2=55.0, o_d=95.0, o_a=-10.0, o_A=30.0, o_B=60.0,
              sigma=1, stack=11.0, Lmax=25.0, q=0.95, qH=0.95, slope=SLOPE, order="S_in", rmax=90.0)
SWEEP = dict(thr=(13, 20), el_off=(-6, 8), W_d=(0, 150), W_a=(-40, 55), a2=(55, 130), sigma=(-1, 1), stack=(11, 13),
             q=(0.93, 1.0), qH=(0.93, 1.0), trim_S=(0, 1), th=("circle", "oval"))


def bvec(az, el):
    az, el = np.asarray(az) * D2R, np.asarray(el) * D2R
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def wdir(d, a):
    d, a = np.asarray(d) * D2R, np.asarray(a) * D2R
    return np.stack([np.sin(d) * np.sin(a), -np.cos(d), np.sin(d) * np.cos(a)], -1)


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------- closed curves on the unit sphere
class Curve:
    """closed polyline of unit directions resampled at uniform arc angle (spacing ~ds mm at R_REF);
    s = arc angle (rad) from sample 0; T = unit tangent, N = U x T (across, in the tangent plane)"""
    def __init__(self, P, ds=1.5):
        P = unit(np.asarray(P, float)); Q = np.r_[P, P[:1]]
        seg = np.arccos(np.clip((Q[:-1] * Q[1:]).sum(-1), -1, 1)); cum = np.r_[0, np.cumsum(seg)]; self.per = cum[-1]
        n = max(16, int(math.ceil(self.per * R_REF / ds))); s = np.arange(n) * self.per / n
        k = np.clip(np.searchsorted(cum, s, side="right") - 1, 0, len(P) - 1); f = (s - cum[k]) / np.maximum(seg[k], 1e-12)
        self.U = unit(Q[k] * (1 - f)[:, None] + Q[k + 1] * f[:, None]); self.s = s; self.n = n
        T = np.roll(self.U, -1, 0) - np.roll(self.U, 1, 0); T -= (T * self.U).sum(-1, keepdims=True) * self.U
        self.T = unit(T); self.N = np.cross(self.U, self.T)

    def strip(self, width, r=R_REF, step=SP):
        """(n, m, 3) directions of a strap `width` mm wide centred on the curve (across offsets at radius r)"""
        c = np.linspace(-width / 2, width / 2, max(2, int(round(width / step)) + 1)) / r
        return unit(self.U[:, None] * np.cos(c)[None, :, None] + self.N[:, None] * np.sin(c)[None, :, None])

    def at(self, s):
        """direction, tangent, across at arc angles s (any shape), linear interpolation, wraps"""
        s = np.mod(s, self.per); x = s / self.per * self.n; k = np.floor(x).astype(int) % self.n; f = (x - np.floor(x))[..., None]
        k1 = (k + 1) % self.n
        U = unit(self.U[k] * (1 - f) + self.U[k1] * f); T = unit(self.T[k] * (1 - f) + self.T[k1] * f)
        T = unit(T - (T * U).sum(-1, keepdims=True) * U); return U, T, np.cross(U, T)

    def val(self, arr, s):
        """interpolate a per-sample array (n,) at arc angles s (wraps)"""
        s = np.mod(s, self.per); x = s / self.per * self.n; k = np.floor(x).astype(int) % self.n; f = x - np.floor(x)
        return arr[k] * (1 - f) + arr[(k + 1) % self.n] * f


def halo_curve(p):
    g = json.load(open(os.path.join(REPO, "pipeline", "conformal", "analysis", "skin_motion_map_14.json")))["scapula"]["grid"]
    a = np.array(g["a"], float); b = np.array(g["b"], float); m = np.array(g["motion"], float)
    el = np.empty(len(a))
    for k in range(len(a)):
        ok = (m[k] >= 0) & (m[k] <= p["thr"]); j = len(b) - 1
        while j >= 0 and ok[j]: j -= 1
        el[k] = b[min(j + 1, len(b) - 1)]
    el = np.convolve(np.r_[el[-4:], el, el[:4]], np.ones(9) / 9, mode="valid")          # 9-tap circular mean
    A = a * D2R
    el = el + 4.0 + p["el_off"] + p["f1c"] * np.cos(A) + p["f1s"] * np.sin(A) + p["f2c"] * np.cos(2 * A) + p["f2s"] * np.sin(2 * A)
    el = np.clip(el, -60, 88)
    return Curve(bvec(a, el)), el


def arm_curve(p):
    if p["th"] == "circle":
        W = wdir(p["W_d"], p["W_a"]); D = np.array([0.0, -1.0, 0.0])
        e1 = D - (D @ W) * W
        e1 = unit(e1) if np.linalg.norm(e1) > 1e-6 else unit(np.cross(W, [0, 0, 1.0]))
        e2 = np.cross(W, e1); t = np.arange(0, 360, 1.0) * D2R; a2 = p["a2"] * D2R
        return Curve(math.cos(a2) * W + math.sin(a2) * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2))
    t = np.arange(0, 360, 1.0) * D2R
    return Curve(wdir(p["o_d"] + p["o_A"] * np.cos(t), p["o_a"] + p["o_B"] * np.sin(t)))


# ---------------------------------------------------------------- K3 requirement (first exit with 2 mm + 15 mm free)
def requirement(B, i, D, t0=15.0, t1=220.0, it_max=90):
    D = np.asarray(D, float).reshape(-1, 3); n = len(D)
    cur = np.full(n, t0); cand = np.zeros(n); st = np.zeros(n, np.int8)        # 0 search, 1 verify, 2 done, 3 fail
    for _ in range(it_max):
        act = np.nonzero(st < 2)[0]
        if not len(act): break
        d = B.dist(i, D[act] * cur[act, None])
        s0 = st[act] == 0; s1 = ~s0
        # search: advance until d >= CLEAR
        a0 = act[s0]; d0 = d[s0]; hit = d0 >= CLEAR
        cand[a0[hit]] = cur[a0[hit]]; st[a0[hit]] = 1; cur[a0[hit]] += np.maximum(d0[hit], 0.25)
        cur[a0[~hit]] += np.maximum(CLEAR - d0[~hit], 0.25)
        # verify: no skin over [cand, cand + FREE]
        a1 = act[s1]; d1 = d[s1]; bad = d1 < 0
        st[a1[bad]] = 0; cur[a1[bad]] += CLEAR - d1[bad]
        g = a1[~bad]; cur[g] += np.maximum(d1[~bad], 0.25); st[g[cur[g] >= cand[g] + FREE]] = 2
        st[(st == 0) & (cur > t1)] = 3
    out = np.where(st == 3, t1, np.where(st == 0, t1, cand)); return out


# ---------------------------------------------------------------- crossings of two closed polylines on the sphere
def crossings(Us, Ts_, Vh, s_s, s_h, per_s, per_h):
    """all crossings of the closed polylines Us (n,3) and Vh (m,3): list of (s, t, p, tanS, tanH)"""
    U1 = np.roll(Us, -1, 0); V1 = np.roll(Vh, -1, 0)
    nU = np.cross(Us, U1); nV = np.cross(Vh, V1)
    M = Vh @ nU.T                     # (m, n): V_k . nU_j
    Nn = Us @ nV.T                    # (n, m): U_j . nV_k
    cV = (M * np.roll(M, -1, 0)) < 0  # V segment k crosses the great circle of U segment j  (m, n)
    cU = (Nn * np.roll(Nn, -1, 0)) < 0
    C = cV.T & cU & ((Us @ Vh.T) > 0)
    j, k = np.nonzero(C)
    if not len(j): return []
    a0 = Nn[j, k]; a1 = Nn[(j + 1) % len(Us), k]; fa = a0 / (a0 - a1)
    b0 = M[k, j]; b1 = M[(k + 1) % len(Vh), j]; fb = b0 / (b0 - b1)
    ds_s = np.mod(np.roll(s_s, -1) - s_s, per_s); ds_h = np.mod(np.roll(s_h, -1) - s_h, per_h)
    s = np.mod(s_s[j] + fa * ds_s[j], per_s); t = np.mod(s_h[k] + fb * ds_h[k], per_h)
    p = unit(Us[j] + fa[:, None] * (U1[j] - Us[j]))
    tS = unit(U1[j] - Us[j]); tH = unit(V1[k] - Vh[k])
    return [(s[q], t[q], p[q], tS[q], tH[q]) for q in range(len(j))]


def cross_info(c):
    s, t, p, tS, tH = c
    tS = unit(tS - (tS @ p) * p); tH = unit(tH - (tH @ p) * p)
    sn = float(p @ np.cross(tS, tH)); cs = float(tS @ tH)
    th = math.degrees(math.atan2(abs(sn), cs)); trans = min(th, 180 - th)
    return dict(s=float(s), t=float(t), p=p, tS=tS, tH=tH, sign=1 if sn > 0 else -1, trans=trans, q2=math.degrees(math.atan2(sn, cs)))


def cdist(a, b, per):
    d = np.mod(a - b, per); return np.minimum(d, per - d)


# ---------------------------------------------------------------- the model
class Model:
    def __init__(self, B, log=print):
        self.B = B; self.log = log
        Z = CB._poses_all(); self.names = list(Z["NAMES"]); self.cid = Z["CID"]; self.POSE = Z["POSE"]
        r = BP._rig(); self._rig = r
        self.RSb = np.stack([B.frames(i)["S"][0] for i in range(len(B.poses))])
        self.RHb = np.stack([B.frames(i)["H"][0] for i in range(len(B.poses))])
        self.clips = {}
        for n in CB.FIT:                                          # every 10 fps frame of every fit clip (kinematics only)
            ix = np.nonzero(self.cid == self.names.index(n))[0]
            RS, RH = [], []
            for j in ix:
                pz = self.POSE[j]; pose = dict(plane=float(pz[0]), elev=float(pz[1]), axial=float(pz[2]), flex=float(pz[3]), pron=float(pz[4]))
                (T, S, H, Fa, Pr), lift = BP.segs(r.L, r.s, pose); RS.append(S[0]); RH.append(H[0])
            self.clips[n] = (ix, np.stack(RS), np.stack(RH))
        self.bench_of = {int(z): i for i, z in enumerate(B.idx) if B.kind[i] == "clip"}
        rest = dict(plane=0.0, elev=0.0, axial=0.0, flex=12.0, pron=0.0); (T, S, H, Fa, Pr), _ = BP.segs(r.L, r.s, rest)
        self.rest = (S[0], H[0])
        self.req_cache = {}

    # -- K3 requirement arrays for a curve strip in a body frame, every bench pose (cached per shape)
    def req_strip(self, key, C, width, frame):
        if key in self.req_cache: return self.req_cache[key]
        D = C.strip(width); n, m = D.shape[:2]; R = self.RSb if frame == "S" else self.RHb
        out = np.zeros((len(self.B.poses), n, m)); t = time.time()
        for i in range(len(self.B.poses)):
            out[i] = requirement(self.B, i, (D.reshape(-1, 3) @ R[i].T)).reshape(n, m)
        self.log(f"  K3 {key[0]} {n}x{m} dirs x {len(self.B.poses)} poses: {time.time() - t:.0f} s")
        if len(self.req_cache) > 40: self.req_cache.clear()
        self.req_cache[key] = out; return out

    # -- kinematics: crossing of the design's sign for one frame (RS, RH), optionally tracked from `last`
    def cross_pose(self, CS, CH, RS, RH, sigma, last=None, home=None):
        cs = [cross_info(c) for c in crossings(CS.U @ RS.T, None, CH.U @ RH.T, CS.s, CH.s, CS.per, CH.per)]
        cs = [c for c in cs if c["sign"] == sigma]
        if not cs: return None
        ref = last if last is not None else home
        if ref is not None and len(cs) > 1:
            dd = [max(cdist(c["s"], ref["s"], CS.per), cdist(c["t"], ref["t"], CH.per)) for c in cs]; return cs[int(np.argmin(dd))]
        return max(cs, key=lambda c: c["trans"])

    def kinematics(self, p, CS, CH):
        sig = int(p["sigma"]); home = self.cross_pose(CS, CH, *self.rest, sig)
        B = self.B; N = len(B.poses); kin = [None] * N; why = {}
        def bump(w): why[w] = why.get(w, 0) + 1
        vis_s, vis_t = [], []
        for i in range(N):                                         # workspace poses: no history
            if B.kind[i] != "ws": continue
            c = self.cross_pose(CS, CH, self.RSb[i], self.RHb[i], sig, home=home)
            if c is None: bump("no crossing"); continue
            if c["trans"] < TRANS: bump("tangent crossing"); continue
            kin[i] = c; vis_s.append(c["s"]); vis_t.append(c["t"])
        clip_frames = 0; clip_ok = 0
        for n, (ix, RS, RH) in self.clips.items():                # fit clips: every 10 fps frame, tracked
            last = None
            for k, z in enumerate(ix):
                clip_frames += 1
                c = self.cross_pose(CS, CH, RS[k], RH[k], sig, last=last, home=home)
                ok = c is not None and c["trans"] >= TRANS; w = "no crossing" if c is None else "tangent crossing"
                if ok and last is not None:
                    jump = max(math.degrees(cdist(c["s"], last["s"], CS.per)), math.degrees(cdist(c["t"], last["t"], CH.per)),
                               abs((c["q2"] - last["q2"] + 180) % 360 - 180))
                    ok = jump <= FLIP; w = "flip"
                if ok:
                    last = c; clip_ok += 1; vis_s.append(c["s"]); vis_t.append(c["t"])
                if int(z) in self.bench_of:
                    i = self.bench_of[int(z)]
                    if ok: kin[i] = c
                    else: bump(w)
        return kin, why, np.array(vis_s), np.array(vis_t), clip_ok / max(clip_frames, 1)

    # -- design: fit the tracks and the neck, then per-pose metal
    def design(self, p, verbose=False):
        """order 'S_in' (spec): the halo is the inner track (on the skin) and the arm track rides over it at the crossing;
        'H_in': the arm track is inner and the halo rides over it. The inner track's carriage A sits on its rail (cheeks
        at the rail's underside level, 16 wide); the outer track's carriage B hangs under its rail."""
        t0 = time.time(); B = self.B
        CS, el = halo_curve(p); CH = arm_curve(p)
        kin, why, vs, vt, clip_follow = self.kinematics(p, CS, CH)
        valid = np.array([c is not None for c in kin])
        D = dict(p=p, CS=CS, CH=CH, kin=kin, why=why, valid=valid, clip_follow_all=clip_follow, ok=False)
        if valid.sum() < 5: D["fail"] = "closes in < 5 poses"; return D
        inn, out_ = ("S", "H") if p.get("order", "S_in") == "S_in" else ("H", "S")
        D["inner"], D["outer"] = inn, out_
        # track arcs: the visited range + MARGIN mm each end. Open unless it is the inner halo (web-supported, may be
        # closed); the outer track is held at its ends (the slide rods stick out above carriage B), T_H by the neck
        def arc(vals, per, rho, closed_ok):
            v = np.sort(np.mod(vals, per)); g = np.diff(np.r_[v, v[0] + per]); k = int(np.argmax(g))
            lo = v[(k + 1) % len(v)]; span = np.mod(v[k] - lo, per); m = MARGIN / rho
            if span + 2 * m >= per - 2 * m and closed_ok: return None                     # closed loop
            if span + 2 * m > per - 10 * D2R: m = max(0.0, (per - 10 * D2R - span) / 2)     # open arc, 10 deg cut
            return (lo - m, span + 2 * m)                                                  # start, length (rad)
        rf = dict(S=R_FOOT_I if inn == "S" else R_FOOT_O, H=R_FOOT_I if inn == "H" else R_FOOT_O)
        D["arcS"] = arc(vs, CS.per, rf["S"], inn == "S" and not p["trim_S"]) if (p["trim_S"] or inn != "S") else None
        D["arcH"] = arc(vt, CH.per, rf["H"], False)
        inS = lambda s: np.ones(np.shape(s), bool) if D["arcS"] is None else np.mod(np.asarray(s) - D["arcS"][0], CS.per) <= D["arcS"][1]
        inH = lambda t: np.mod(np.asarray(t) - D["arcH"][0], CH.per) <= D["arcH"][1]
        D["inS"], D["inH"] = inS, inH
        vi = np.nonzero(valid)[0]
        T = dict(S=dict(C=CS, frame="S", R=self.RSb, key="s", tan="tS", m=inS(CS.s), arc=D["arcS"], q=p["q"],
                        ck=("S", p["thr"], p["el_off"], p["f1c"], p["f1s"], p["f2c"], p["f2s"])),
                 H=dict(C=CH, frame="H", R=self.RHb, key="t", tan="tH", m=inH(CH.s), arc=D["arcH"], q=p["qH"],
                        ck=("H", p["th"], p["W_d"], p["W_a"], p["a2"], p["o_d"], p["o_a"], p["o_A"], p["o_B"])))
        D["T"] = T
        if p.get("rmax"):            # trim each track to its frame's safe zone: samples whose fitted requirement <= rmax mm
            for nm in ("S", "H"):
                Tk = T[nm]; C = Tk["C"]; w_ = CAR_W if nm == inn else RAIL_W
                rq = np.quantile(self.req_strip(Tk["ck"] + (w_,), C, w_, Tk["frame"])[vi].max(2), Tk["q"], axis=0)
                a_ = longest_run((rq <= p["rmax"]) & Tk["m"], C)
                if a_ is None: D["fail"] = f"T_{nm} has no safe arc"; return D
                D["arc" + nm] = a_; Tk["arc"] = a_; Tk["m"] = (inS if nm == "S" else inH)(C.s)
        I, O = T[inn], T[out_]
        # inner radius: K3 over the carriage width (16), quantile over the closing poses, + rail height, slope-limited
        Rq = self.req_strip(I["ck"] + (CAR_W,), I["C"], CAR_W, I["frame"])
        rho_i = np.quantile(Rq[vi].max(2), I["q"], axis=0) + LIP + RAIL_H         # lips under the strip edges at the requirement
        closed_i = I["arc"] is None
        rho_i = slope_limit(rho_i, I["C"].per * R_REF / I["C"].n, closed=closed_i, mask=None if closed_i else I["m"], slope=p["slope"])
        I["rho"] = rho_i
        # outer radius: K3 over the rail width (8), quantile; then the crossing constraints (hard, max over poses)
        Rq = self.req_strip(O["ck"] + (RAIL_W,), O["C"], RAIL_W, O["frame"])
        rho_o = np.quantile(Rq[vi].max(2), O["q"], axis=0) + RAIL_H
        Ci, Co = I["C"], O["C"]; mi, mo = I["m"], O["m"]; idx_o = np.nonzero(mo)[0]
        for i in vi:
            c = kin[i]; Ri, Ro = I["R"][i], O["R"][i]
            aTop = self.a_top(D, c)
            # carriage B's plate over its footprint (+-CAR_L/2 + 2 along the outer track): L >= 0
            near = cdist(Co.s, c[O["key"]], Co.per) * R_FOOT_O <= CAR_L / 2 + 2.0
            rho_o[near] = np.maximum(rho_o[near], aTop - A_UP + p["stack"])
            # overpass: outer rail over the inner rail wherever they come within (4 + 4 + 1) mm: underside >= top + GAP
            Uo = Co.U[mo] @ Ro.T; Ui = Ci.U[mi] @ Ri.T
            G = (Uo @ Ui.T) >= math.cos((RAIL_W + GAP) / 60.0)
            if G.any():
                need = np.where(G, rho_i[mi][None, :], -1).max(1) + GAP + RAIL_H
                rho_o[idx_o] = np.maximum(rho_o[idx_o], need)
            # outer rail over carriage A's footprint: underside >= A top + GAP
            P2, ta, na = self.a_frame(D, c); loc = Uo
            xa, ya, za = loc @ ta, loc @ na, loc @ P2
            inA = (za > 0) & (np.abs(xa) <= (CAR_L / 2 + RAIL_W / 2 + GAP) / 60.0) & (np.abs(ya) <= (CAR_W / 2 + RAIL_W / 2 + GAP) / 60.0)
            if inA.any(): rho_o[idx_o[inA]] = np.maximum(rho_o[idx_o[inA]], aTop + GAP + RAIL_H)
        rho_o = slope_limit(rho_o, Co.per * R_REF / Co.n, closed=False, mask=mo, slope=p["slope"])
        O["rho"] = rho_o
        D["rhoS"], D["rhoH"] = T["S"]["rho"], T["H"]["rho"]
        # rigid rail undersides in their own frames (rotated per pose)
        D["railS"] = rail_samples(CS, D["rhoS"], D["arcS"], RAIL_W, -RAIL_H, np.eye(3))
        D["railH"] = rail_samples(CH, D["rhoH"], D["arcH"], RAIL_W, -RAIL_H, np.eye(3))
        # neck: from the T_H arc end nearest the bar start to BOTTOM's bar, K3 in the humerus frame
        bdir = unit(BAR_P); ends = [D["arcH"][0], D["arcH"][0] + D["arcH"][1]]
        Ue = [CH.at(e)[0] for e in ends]; ke = int(np.argmax([u @ bdir for u in Ue])); tn = ends[ke]
        un = Ue[ke]; ang = math.acos(np.clip(un @ bdir, -1, 1)); rN0 = float(CH.val(D["rhoH"], tn)) - RAIL_H   # neck continues the rail
        D["neck"] = None
        if ang > 2 * D2R:
            ns = max(3, int(ang * 70.0 / SP) + 1); th = np.linspace(0, ang, ns); e2 = unit(bdir - (bdir @ un) * un)
            Cn = unit(np.cos(th)[:, None] * un + np.sin(th)[:, None] * e2); nrm = np.cross(un, e2)
            cN = np.linspace(-NECK_W / 2, NECK_W / 2, int(NECK_W / SP) + 1) / 70.0
            Dn = unit(Cn[:, None] * np.cos(cN)[None, :, None] + nrm[None, None] * np.sin(cN)[None, :, None])
            kN = ("N",) + T["H"]["ck"] + (round(tn, 3),)
            if kN not in self.req_cache:
                o = np.zeros((len(B.poses), ns, len(cN)))
                for i in range(len(B.poses)): o[i] = requirement(B, i, Dn.reshape(-1, 3) @ self.RHb[i].T).reshape(ns, len(cN))
                self.req_cache[kN] = o
            reqN = np.quantile(self.req_cache[kN][vi].max(2), p["qH"], axis=0)
            x = th * 70.0; ramp = rN0 - np.tan(60 * D2R) * np.maximum(x - NECK_W / 2, 0)    # leaves the rail end <= 60 deg
            rN = slope_limit(np.maximum(reqN, ramp), SP, closed=False)
            cc = np.arange(-NECK_W / 2, NECK_W / 2 + 1e-6, SP)
            Dl = unit(Cn[:, None] + nrm[None, None] * (cc[None, :, None] / rN[:, None, None]))
            D["neck"] = dict(C=Cn, nrm=nrm, ang=ang, r=rN, th=th, un=un, e2=e2, local=(Dl * rN[:, None, None]).reshape(-1, 3))
        D["ok"] = True; D["secs_fit"] = round(time.time() - t0, 1)
        return D

    # carriage A (inner track) frame at the crossing: (p2, inner tangent, across)
    def a_frame(self, D, c):
        t = c[D["T"][D["inner"]]["tan"]]; return (c["p"], t, np.cross(c["p"], t))

    def a_top(self, D, c):
        I = D["T"][D["inner"]]; C = I["C"]
        foot = cdist(C.s, c[I["key"]], C.per) * R_FOOT_I <= CAR_L / 2
        return float(I["rho"][foot].max()) + A_UP

    def b_bot(self, D, c):
        O = D["T"][D["outer"]]; C = O["C"]
        foot = cdist(C.s, c[O["key"]], C.per) * R_FOOT_O <= CAR_L / 2
        return float(O["rho"][foot].min()) - RAIL_H - B_DN

    # -- metal of one bench pose (None + reason when not taken)
    def metal(self, D, i, parts=False):
        c = D["kin"][i]
        if c is None: return None, "kinematics"
        return self.metal_c(D, c, self.RSb[i], self.RHb[i], i, parts)

    def metal_c(self, D, c, RS, RH, i=None, parts=False):
        p = D["p"]; I, O = D["T"][D["inner"]], D["T"][D["outer"]]
        for Tk, rf in ((I, R_FOOT_I), (O, R_FOOT_O)):                    # carriages inside their track arcs
            if Tk["arc"] is None: continue
            u = np.mod(c[Tk["key"]] - Tk["arc"][0], Tk["C"].per); e = (CAR_L / 2) / rf
            if u < e or u > Tk["arc"][1] - e: return None, "off track"
        P2, ta, na = self.a_frame(D, c); tb = c[O["tan"]]; nb = np.cross(P2, tb)
        aTop = self.a_top(D, c); bBot = self.b_bot(D, c)
        hb = p["stack"] - (A_UP + B_DN + RAIL_H)                       # bearing height: stack = A_UP + hb + B_DN + RAIL_H
        L = bBot - aTop - hb
        D.setdefault("L", []).append(L)
        if L < -1e-6 or L > p["Lmax"]: return None, "slide range"
        out = {}
        out["T_S"] = D["railS"] @ RS.T; out["T_H"] = D["railH"] @ RH.T
        # the outer rail's underside over carriage B's plate faces B, not the skin
        nmO = "T_" + D["outer"]; X = out[nmO]; u = unit(X); rr = np.linalg.norm(X, axis=1)
        xb = (u - (u @ P2)[:, None] * P2) @ tb; yb = u @ nb
        cov = (np.abs(xb * rr) <= CAR_L / 2) & (np.abs(yb * rr) <= CAR_W / 2) & (u @ P2 > 0)
        out[nmO] = X[~cov]
        # carriage A: cheeks beside its rail (|across| 4..8), bogie-shaped to the rail radius
        al = np.arange(-CAR_L / 2, CAR_L / 2 + 1e-6, SP); ac = np.array([-6.0, -4.0, 4.0, 6.0])   # walls + lips span |across| 3.5..7: two columns each side (2 mm grid)
        rA = I["C"].val(I["rho"], c[I["key"]] + al / (aTop - A_UP)) - RAIL_H - LIP     # walls + lips: underside 1.5 below the strip
        dA = unit(P2[None, None] + (al[:, None, None] * ta + ac[None, :, None] * na) / rA[:, None, None])
        out["car_A"] = (dA * rA[:, None, None]).reshape(-1, 3)
        # swivel ring + slide frame (bearing underside at A top), only the part outside A's footprint
        g = np.arange(-BRG_R, BRG_R + 1e-6, SP); Xg, Yg = np.meshgrid(g, g); k = (Xg ** 2 + Yg ** 2 <= BRG_R ** 2) & ((np.abs(Xg) > CAR_L / 2) | (np.abs(Yg) > CAR_W / 2))
        out["swivel"] = unit(P2[None] + (Xg[k][:, None] * ta + Yg[k][:, None] * na) / aTop) * aTop
        # carriage B plate underside (aligned with the outer track), outside A's footprint and the ring
        bl = np.arange(-CAR_L / 2, CAR_L / 2 + 1e-6, SP); bc = np.arange(-CAR_W / 2, CAR_W / 2 + 1e-6, SP); BL, BC = np.meshgrid(bl, bc)
        V = BL.ravel()[:, None] * tb + BC.ravel()[:, None] * nb; xa, ya = V @ ta, V @ na
        k = ~(((np.abs(xa) <= CAR_L / 2) & (np.abs(ya) <= CAR_W / 2)) | (xa ** 2 + ya ** 2 <= BRG_R ** 2))
        out["car_B"] = unit(P2[None] + V[k] / bBot) * bBot
        out["neck"] = D["neck"]["local"] @ RH.T if D["neck"] is not None else np.zeros((0, 3))
        # interference between parts without a shared joint (radial intervals where angularly close)
        w = self.interfere(D, c, RS, RH, aTop, bBot, p["Lmax"] - L)
        if w: return None, "interference " + w
        # top / side samples (checked for contact only): outer rail top, neck top, slide-rod tips over carriage B
        To = out[nmO]
        D_top = np.r_[To * (1 + RAIL_H / np.linalg.norm(To, axis=1))[:, None],
                      out["neck"] * (1 + NECK_T / np.maximum(np.linalg.norm(out["neck"], axis=1), 1))[:, None] if len(out["neck"]) else np.zeros((0, 3)),
                      P2[None] * (bBot + B_DN + RAIL_H + p["Lmax"] - L)]
        if parts: return out, D_top
        face = np.concatenate([v for v in out.values() if len(v)])
        if i is not None:
            dt = self.B.dist(i, D_top)
            if dt.min() < 0: face = np.r_[face, D_top[np.argmin(dt)][None]]
        return face, ""

    def interfere(self, D, c, RS, RH, aTop, bBot, rod):
        """neck (humerus) vs T_S rail (scapula) and vs the swivel block; the track/track and track/carriage pairs are
        cleared by construction of the outer radius (overpass + footprint constraints over the same poses)"""
        CS = D["CS"]; mS = D["inS"](CS.s)
        if D["neck"] is None: return ""
        nk = D["neck"]; Un = nk["C"] @ RH.T; rn = nk["r"]                         # neck centreline, underside radius
        Us = CS.U[mS] @ RS.T; rs = D["rhoS"][mS]
        G = (Un @ Us.T) >= math.cos((NECK_W / 2 + RAIL_W / 2 + GAP) / 60.0)
        if G.any():
            a, b = np.nonzero(G)
            bad = (rn[a] < rs[b] + GAP) & (rn[a] + NECK_T > rs[b] - RAIL_H - GAP)   # neck [rn, rn+6] vs T_S [rs-5, rs]
            if bad.any(): return "neck/T_S"
        dang = np.arccos(np.clip(Un @ c["p"], -1, 1)) * 60.0                      # neck vs the swivel block
        close = dang <= NECK_W / 2 + CAR_L / 2 * 1.42 + GAP
        if close.any():
            lo = aTop - A_UP - RAIL_H - LIP; hi = bBot + B_DN + RAIL_H + rod                  # + the slide rods over B
            if ((rn[close] < hi + GAP) & (rn[close] + NECK_T > lo - GAP)).any(): return "neck/swivel"
        return ""


def longest_run(m, C):
    """(start arc angle, length) of the longest circular run of True samples of curve C, or None"""
    m = np.asarray(m, bool); n = len(m)
    if m.sum() < 3: return None
    if m.all(): return (0.0, C.per - 10 * D2R)
    k0 = int(np.argmin(m)); mm = np.roll(m, -k0); best = (0, 0); cur = 0; st = 0
    for j in range(n):
        if mm[j]:
            if cur == 0: st = j
            cur += 1
            if cur > best[1]: best = (st, cur)
        else: cur = 0
    if best[1] < 3: return None
    return (float(C.s[(best[0] + k0) % n]), (best[1] - 1) * C.per / C.n)


def slope_limit(r, ds, closed, mask=None, slope=SLOPE):
    """raise-only: |dr/ds| <= slope (forward + backward passes; twice round a closed loop)"""
    r = np.array(r, float); n = len(r); step = slope * ds
    idx = np.arange(n) if mask is None else np.nonzero(mask)[0]
    if mask is not None and not closed:
        # open arc on a closed parameter: walk the masked samples in arc order (contiguous modulo n)
        k = idx; brk = np.nonzero(np.diff(k) > 1)[0]
        if len(brk): k = np.r_[k[brk[0] + 1:], k[:brk[0] + 1]]
        idx = k
    seq = r[idx]
    for _ in range(2 if closed else 1):
        for j in range(1, len(seq)): seq[j] = max(seq[j], seq[j - 1] - step)
        if closed: seq[0] = max(seq[0], seq[-1] - step)
        for j in range(len(seq) - 2, -1, -1): seq[j] = max(seq[j], seq[j + 1] - step)
        if closed: seq[-1] = max(seq[-1], seq[0] - step)
    r[idx] = seq; return r


def rail_samples(C, rho, arc, width, off, R):
    """underside samples (k, 3) in the thorax frame of a rail on curve C with running radius rho (per sample),
    underside at rho + off, every SP mm along (at its radius) and across; arc = (start, length) or None (closed)"""
    s0, ln = (0.0, C.per) if arc is None else arc
    # walk at SP mm of real arc length
    ss = [s0]; r0 = C.val(rho, s0) + off
    while ss[-1] - s0 < ln:
        r0 = C.val(rho, ss[-1]) + off; ss.append(ss[-1] + SP / max(r0, 20.0))
    ss = np.array(ss[:-1] if arc is None else ss); ss = ss[ss - s0 <= ln + 1e-9]
    U, T, N = C.at(ss); rr = C.val(rho, ss) + off
    cc = np.linspace(-width / 2, width / 2, int(round(width / SP)) + 1)
    Dd = unit(U[:, None] + N[:, None] * (cc[None, :, None] / rr[:, None, None]))
    return (Dd * rr[:, None, None]).reshape(-1, 3) @ R.T


# ---------------------------------------------------------------- evaluation
def run(M, p, verbose=False):
    t = time.time(); B = M.B; D = M.design(p); B.reset(); why = dict(D["why"])
    if not D["ok"]:
        r = dict(reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, gap=CB.gap_of(0, 0, 0), why=why, fail=D.get("fail"))
        return r, D
    per = {}
    for i in range(len(B.poses)):
        if D["kin"][i] is None: B.record(i, None); continue
        P, w = M.metal(D, i)
        if P is None:
            why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, P)
        if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        elif B.kind[i] == "clip" and verbose:
            parts, _ = M.metal(D, i, parts=True)
            for nm, Q in parts.items():
                if not len(Q): continue
                dq = B.dist(i, Q); a = per.setdefault(nm, [0, 0, 0, 0.0])
                a[0] += int(((dq >= 2) & (dq <= 14)).sum()); a[1] += int(((dq >= 2) & (dq <= 10)).sum()); a[2] += len(dq); a[3] += float(dq.sum())
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1); r["closure_share_clip_10fps"] = round(D["clip_follow_all"], 4)
    r["arcS_deg"] = None if D["arcS"] is None else round(math.degrees(D["arcS"][1]), 1); r["arcH_deg"] = round(math.degrees(D["arcH"][1]), 1)
    vi = D["valid"]
    r["rhoS"] = [round(float(np.min(D["rhoS"])), 1), round(float(np.max(D["rhoS"][D["inS"](D["CS"].s)])), 1)]
    r["rhoH"] = [round(float(np.min(D["rhoH"][D["inH"](D["CH"].s)])), 1), round(float(np.max(D["rhoH"][D["inH"](D["CH"].s)])), 1)]
    if per: r["per_part"] = {k: dict(ib14=round(v[0] / v[2], 3), ib10=round(v[1] / v[2], 3), n=v[2], mean=round(v[3] / v[2], 1)) for k, v in per.items()}
    r["mass_g"] = mass(D)
    return r, D


def mass(D):
    """Ti mass of the custom parts (rails 8 x 5, carriages 20 x 16 x 9, ring + slide ~6 g, neck 14 x 6)"""
    CS, CH = D["CS"], D["CH"]
    lS = (CS.per if D["arcS"] is None else D["arcS"][1]) * float(np.mean(D["rhoS"])); lH = D["arcH"][1] * float(np.mean(D["rhoH"]))
    ln = 0.0 if D["neck"] is None else D["neck"]["ang"] * float(np.mean(D["neck"]["r"]))
    v = (lS + lH) * RAIL_W * RAIL_H + 2 * CAR_L * CAR_W * 9.0 * 0.6 + ln * NECK_W * NECK_T
    return round(v * RHO_TI + 6.0, 1)


# ---------------------------------------------------------------- public API
_MODELS = {}


def metal(pose, frames, params=None):
    """metal sample points (k, 3) of the design `params` (fitted on Bench(60, 160)) for an arbitrary pose with frames
    dict(S=(R, t), H=(R, t)), or None when the chain cannot take it (crossing / transversal / track / slide / parts).
    The workspace rule picks the crossing (no clip history)."""
    p = dict(PARAMS, **(params or {})); key = json.dumps(p, sort_keys=True)
    if key not in _MODELS:
        M = Model(CB.Bench(60, 160), log=lambda *a: None); _MODELS[key] = (M, M.design(p))
    M, D = _MODELS[key]
    if not D["ok"]: return None
    RS, RH = frames["S"][0], frames["H"][0]
    home = M.cross_pose(D["CS"], D["CH"], *M.rest, int(p["sigma"]))
    c = M.cross_pose(D["CS"], D["CH"], RS, RH, int(p["sigma"]), home=home)
    if c is None or c["trans"] < TRANS: return None
    P, w = M.metal_c(D, c, RS, RH)
    return P


def sketch(M, D, path, probes=None):
    """matplotlib sketch: skin (grey) and the parts at rest and overhead (posterior and lateral views)"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    p = D["p"]; r_ = BP._rig(); B = M.B
    probes = probes or dict(rest=dict(plane=0, elev=5, axial=0, flex=12, pron=0), overhead=dict(plane=60, elev=150, axial=0, flex=12, pron=0))
    home = M.cross_pose(D["CS"], D["CH"], *M.rest, int(p["sigma"]))
    col = dict(T_S="#1f77b4", T_H="#d62728", car_A="#2ca02c", car_B="#9467bd", swivel="#ff7f0e", neck="#8c564b")
    fig, ax = plt.subplots(len(probes), 2, figsize=(10, 5 * len(probes)))
    for row, (nm, q) in enumerate(probes.items()):
        (T, S, H, Fa, Pr), lift = BP.segs(r_.L, r_.s, q); V = BP.posed(q)
        c = M.cross_pose(D["CS"], D["CH"], S[0], H[0], int(p["sigma"]), home=home)
        out = None; w = "no crossing"
        if c is not None:
            res = M.metal_c(D, c, S[0], H[0], parts=True); out, w = (res[0], "") if isinstance(res[0], dict) else (None, res[1])
        sel = np.linalg.norm(V, axis=1) < 170
        for k, (a, b, lab) in enumerate(((2, 1, "posterior view (z lateral, y up)"), (0, 1, "lateral view (x anterior, y up)"))):
            A = ax[row, k]; A.scatter(V[sel][:, a] * (1 if k else -1), V[sel][:, b], s=0.2, c="#bbbbbb")
            if out:
                for part, P in out.items():
                    if len(P): A.scatter(P[:, a] * (1 if k else -1), P[:, b], s=1.5, c=col[part], label=part)
            A.set_aspect("equal"); A.set_title(f"{nm}: {lab}" + ("" if out else f" - NOT TAKEN ({w})"), fontsize=9)
            if row == 0 and k == 0 and out: A.legend(markerscale=6, fontsize=7, loc="lower left")
    fig.suptitle(f"{ID}: {short(p)}", fontsize=9); fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


# ---------------------------------------------------------------- CLI
def bench_for(fast_only=False):
    B = CB.Bench(60, 160)
    if B.mode != "fast" and not fast_only: return B
    return B


def check(nc=20, nw=40):
    B = CB.Bench(nc, nw); print("bench", B.mode, len(B.poses)); M = Model(B)
    p = dict(PARAMS); r, D = run(M, p, verbose=True); print(json.dumps({k: v for k, v in r.items()}, default=str))
    probes = dict(rest=dict(plane=0, elev=5, axial=0, flex=12, pron=0), overhead=dict(plane=60, elev=160, axial=0, flex=12, pron=0),
                  across=dict(plane=130, elev=90, axial=0, flex=90, pron=0), behind=dict(plane=-60, elev=40, axial=-60, flex=90, pron=0),
                  abd90=dict(plane=0, elev=90, axial=0, flex=12, pron=0), flex90=dict(plane=90, elev=90, axial=0, flex=12, pron=0))
    r_ = BP._rig()
    for nm, q in probes.items():
        (T, S, H, Fa, Pr), _ = BP.segs(r_.L, r_.s, q)
        home = M.cross_pose(D["CS"], D["CH"], *M.rest, int(p["sigma"]))
        c = M.cross_pose(D["CS"], D["CH"], S[0], H[0], int(p["sigma"]), home=home)
        if c is None: print(nm, "no crossing"); continue
        P, w = M.metal_c(D, c, S[0], H[0])
        print(nm, f"s {math.degrees(c['s']):.0f} t {math.degrees(c['t']):.0f} q2 {c['q2']:.0f} trans {c['trans']:.0f}", "taken" if P is not None else w,
              "" if P is None else f"{len(P)} pts")


SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KIN_JSON = os.path.join(REPO, ".cache", "concept_models", ID, "kin_screen.json")


def kin_screen(M, p):
    """kinematic upper bound of a configuration: workspace share with a transversal crossing of the design's sign,
    bench clip frames followed (10 fps continuity) - no geometry"""
    CS, _ = halo_curve(p); CH = arm_curve(p); kin, why, vs, vt, cf = M.kinematics(p, CS, CH); B = M.B
    ws = [k for k in range(len(B.poses)) if B.kind[k] == "ws"]; cl = [k for k in range(len(B.poses)) if B.kind[k] == "clip"]
    rk = float(np.mean([kin[k] is not None for k in ws])); fk = float(np.mean([kin[k] is not None for k in cl]))
    return dict(reach_kin=round(rk, 4), follow_kin=round(fk, 4), gap_kin=round(100 * (max(0, .95 - fk) + max(0, .90 - rk)), 2), why=why)


def sweep(stages=("kin", "coarse", "refine")):
    B = CB.Bench(60, 160); print("bench", B.mode, len(B.poses), flush=True); M = Model(B)
    rows = json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) else []
    done = {json.dumps(r["params"], sort_keys=True): r for r in rows}

    def ev(p, stage):
        p = dict(PARAMS, **p); key = json.dumps(p, sort_keys=True)
        if key in done: return done[key]
        r, D = run(M, p)
        e = dict(k=len(rows), t=now(), params=p, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"], follow=r["follow"],
                 contact=r["contact"], gap=r["gap"], stage=stage, why=r.get("why"), arcS_deg=r.get("arcS_deg"), arcH_deg=r.get("arcH_deg"),
                 rhoS=r.get("rhoS"), rhoH=r.get("rhoH"), mass_g=r.get("mass_g"), secs=r.get("secs"), mode=B.mode)
        rows.append(e); done[key] = e
        os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
        json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=0); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        print(f"[{e['k']}] {stage} gap {e['gap']:.1f} reach {e['reach']:.3f} follow {e['follow']:.3f} ib14 {e['inband14']:.3f} "
              f"ib10 {e['inband10']:.3f} contact {e['contact']:.3f} | {short(p)} | {e['why']} {e['secs']} s", flush=True)
        return e

    kin = json.load(open(KIN_JSON)) if os.path.exists(KIN_JSON) else []
    if "kin" in stages:                                         # stage 0: kinematic screen of the arm track and halo
        seen = {json.dumps(k["params"], sort_keys=True) for k in kin}
        grid = []
        for thr in (13, 20):
            for Wd in (75, 90, 105, 120):
                for Wa in (-40, -10, 20, 55):
                    for a2 in (50, 70, 90, 115):
                        for sg in (1, -1):
                            grid.append(dict(PARAMS, thr=thr, W_d=float(Wd), W_a=float(Wa), a2=float(a2), sigma=sg))
        for thr in (13, 20):                                    # the deltoid-oval variant
            for (od, oa, oA, oB) in ((95, -10, 30, 60), (95, -10, 40, 80), (105, 0, 30, 60), (85, -20, 25, 70), (100, 10, 35, 90)):
                for sg in (1, -1):
                    grid.append(dict(PARAMS, thr=thr, th="oval", o_d=float(od), o_a=float(oa), o_A=float(oA), o_B=float(oB), sigma=sg))
        for p in grid:
            if json.dumps(p, sort_keys=True) in seen: continue
            k = kin_screen(M, p); k["params"] = p; kin.append(k)
            print("kin", short(p), k["reach_kin"], k["follow_kin"], k["gap_kin"], flush=True)
            os.makedirs(os.path.dirname(KIN_JSON), exist_ok=True); json.dump(kin, open(KIN_JSON, "w"), indent=0)
    if "coarse" in stages:                                      # stage 1: full bench on the kinematically best shapes
        kin.sort(key=lambda k: k["gap_kin"])
        picked = []
        for k in kin:
            sh = (k["params"]["th"], k["params"]["W_d"], k["params"]["W_a"], k["params"]["a2"], k["params"]["o_d"], k["params"]["o_B"], k["params"]["sigma"])
            if sh in [x[0] for x in picked]: continue
            picked.append((sh, k["params"]))
            if len(picked) >= 12: break
        for sh, p in picked:
            ev(dict(p), "coarse")
    if "refine" in stages:                                      # stage 2: around the best: radial stack, quantiles, halo trim / offset
        for _ in range(3):
            best = sorted(rows, key=lambda e: e["gap"])[:3]
            for e in best:
                p0 = e["params"]
                for ch in (dict(q=0.97), dict(q=0.93), dict(qH=0.97), dict(qH=0.93), dict(stack=15.0), dict(trim_S=1 - p0["trim_S"]),
                           dict(el_off=p0["el_off"] + 4), dict(el_off=p0["el_off"] - 4), dict(thr=33 - p0["thr"]) if p0["thr"] in (13, 20) else {},
                           dict(a2=p0["a2"] + 8), dict(a2=p0["a2"] - 8), dict(W_d=p0["W_d"] + 8), dict(W_d=p0["W_d"] - 8),
                           dict(W_a=p0["W_a"] + 12), dict(W_a=p0["W_a"] - 12)):
                    if not ch: continue
                    if p0["th"] == "oval" and any(k in ch for k in ("a2", "W_d", "W_a")): continue
                    ev(dict(p0, **ch), "refine")
    best = sorted(rows, key=lambda e: e["gap"])[0]
    print("BEST", json.dumps(best)); return best, rows


def short(p):
    s = f"thr{p['thr']} el{p['el_off']:+.0f} " + (f"W({p['W_d']:.0f},{p['W_a']:.0f}) a2 {p['a2']:.0f}" if p["th"] == "circle" else
                                                  f"oval({p['o_d']:.0f},{p['o_a']:.0f},{p['o_A']:.0f},{p['o_B']:.0f})")
    return s + f" sg{p['sigma']:+d} st{p['stack']:.0f} q{p['q']} qH{p['qH']} trim{p['trim_S']} rmax{p.get('rmax')} {p.get('order')}"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check": check()
    elif a[0] == "sweep": sweep(tuple(a[1:]) if len(a) > 1 else ("kin", "coarse", "refine"))
