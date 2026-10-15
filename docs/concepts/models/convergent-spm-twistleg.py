"""convergent-spm-twistleg: Convergent 2+1 spherical parallel mechanism (concept screen, idealised geometry).

Topology (catalogue entry 'convergent-spm-twistleg', every joint axis through the GH centre):
  S (scapula base frame) -- three ACTIVE base revolutes, O20 hubs, axes u1, u2, u3 fixed in S
  legs 1, 2: crank k (arc a_k) -> passive elbow pin P14 (axis e_k) -> coupler k (arc c_k) -> passive pin about the
             SAME arm-fixed axis W (one double-row O16 arm pin: arm plate, coupler 1 +3.15, coupler 2 +6.3)
  leg 3:     crank 3 (arc a3) -> passive elbow pin P14 (axis e3) -> coupler 3 (arc c3) -> passive P14 pin about a
             second arm-fixed axis v3 (on the same arm plate, v3_off deg from W)
  arm plate (fixed to the humerus) -> neck toward the cuff / BOTTOM.
DOF: spherical Gruebler, 8 bodies (S, 3 cranks, 3 couplers, arm) and 9 revolutes: M = 3 (9 - 3 * (8 - 1 - 9) ... =
3 * (8 - 1) - 2 * 9 = 3). Three ACTIVE (the base hubs: sensed in MVP1, driven in MVP2), six passive pins all set by
the loop closures given the arm pose (nothing free, nothing sags): ACTIVE 3, passive 6.

Kinematics (closed form, the arm drives): per pose the humerus orientation in the scapula frame HG (the band
evaluator's convention, as tools/concept_baseline.py) gives W_t = HG W and v3_t = HG v3; elbow e_k = the two-circle
closure (cone a_k about u_k) x (cone c_k about the leg's arm axis) on the design's branch sigma_k (fixed). A pose is
kinematically taken iff every leg closes with >= `margin` deg from the fold / stretch (serial) singularity, the
parallel-singularity measure det[unit(e1 x W), unit(e2 x W), unit(e3 x v3)] keeps the sign it has at rest with
|det| >= det_min (the assembly mode the device is built in; a sign change needs a pass through the singularity), and
the three elbows stay >= `sep` deg apart. Along each fit clip the path between consecutive frames is re-solved on 4
slerp sub-steps (closure, margin and det sign must hold) and no joint value (3 base angles, 3 elbow angles, 3 arm-pin
angles) may jump > 25 deg between consecutive taken frames (K2): otherwise the frame is not followed.

Geometry (conventions of tools/concept_baseline.py: straps sampled with its arc_dirs / disc_dirs - 2 mm along and
across, ~1 point / 4 mm2 - every part rigid in its own body frame with a radial profile fitted over the kinematically
taken poses as the `pct` percentile of the OUTERMOST skin crossing under each sample + `clear`; poses where the skin
rises above a part are contact = not taken):
  * base hubs: O20 discs r 10 on u_k (flat at the max over the disc), lower member = the base frame (S), crank on top
    (+3.15), crown +12.25 (docs/HARDWARE.md v5);
  * base frame: 8 x 3 mm straps joining the three base hubs (minimum spanning tree on the dome), fixed in S;
  * cranks: w_crank x 3 mm straps on the great circle u_k -> e_k; at the elbow the crank is the lower member and
    carries the P14 pin disc (r 7, flat), the coupler rides +3.15, crown +8;
  * couplers: w_coup x 3 mm straps e_k -> W (legs 1, 2) / v3 (leg 3);
  * arm plate (fixed in the humerus, 4 mm): a 16 mm strap over W and v3, 8 mm beyond each pin, flat over the pin
    discs (O16 at W, crown +10; P14 at v3), coupler 1 at +3.15, coupler 2 at +6.3 over the plate at W;
  * neck: the baseline's arm-end strap, 8 mm wide, `neck_deg` from W toward the humerus axis, part of the arm plate.
  Every strap leaves its joint at the joint's stack level and may ramp down to its fitted profile at <= 45 deg outside
  a 2 mm land; strap samples inside a joint's disc footprint are replaced by that joint's lower member (disc / plate).
Self-collision (per pose; a collision = the pose is not taken): every pair of bodies that do not share a joint must
stay >= 1 mm apart (strap centre lines with their half-widths and radial intervals [rho, rho + t], joint cylinders
r x [F, F + crown]); bodies that share a joint are checked outside that joint's footprint (+2 mm).
Distances for the score: tools/concept_bench.py B.dist of every skin-facing sample (fast grid cache when built);
the profile fit uses a per-pose cube map of the outermost skin crossing (exact ray-triangle, .cache/concept_models).

    python3 docs/concepts/models/convergent-spm-twistleg.py check [n_clip n_ws]   # defaults on a bench, diagnostics
    python3 docs/concepts/models/convergent-spm-twistleg.py sweep                 # the sweep (writes sweeps/, rows/)
    python3 docs/concepts/models/convergent-spm-twistleg.py sketch                # docs/concepts/img/<id>.png
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                        # noqa: E402
import concept_baseline as CBL                                    # noqa: E402

ID = "convergent-spm-twistleg"
D2R = math.pi / 180
O20 = dict(r=10.0, up=3.15, crown=12.25)                          # base hubs (docs/HARDWARE.md v5)
P14 = dict(r=7.0, up=3.15, crown=8.0)                             # passive pin (catalogue P14)
O16 = dict(r=8.0, up=3.15, crown=10.0)                            # double-row arm pin at W (three bodies)
T_STRAP, T_PLATE, W_BF, W_PLATE, W_NECK = 3.0, 4.0, 8.0, 16.0, 8.0
CLR, LAND, SLOPE, R_REF = 1.0, 2.0, 1.0, 70.0
JUMP = 25.0                                                       # K2 continuity, deg
N_SUB = 4                                                         # slerp sub-steps between consecutive clip frames

PARAMS = dict(u=[[-75.0, 40.0], [-35.0, 40.0], [-45.0, 65.0]],    # base axes bvec(az, el) in S (az 0 post, 90 lat)
              a=[60.0, 60.0, 70.0], c=[120.0, 120.0, 85.0],      # crank / coupler arcs (deg)
              W=[71.38, 4.78],                                    # arm axis W = wdir(delta, az) (champion's)
              v3_off=45.0, v3_dir=45.0,                           # v3 = W turned v3_off deg toward v3_dir (0 ant, 90 up, 180 post)
              s=[-1, 1, 1],                                       # closure branches
              det_min=0.10, margin=8.0, sep=17.0,
              pct=95.0, clear=2.0, w_crank=10.0, w_coup=8.0, neck_deg=25.0,
              layers=["K0", "K1", "K2", "C0", "C1", "C2"], stack=True)   # stacking order of the moving bodies (bottom first)
SWEEP = dict(u_az=(-150, 180), u_el=(20, 85), a=(40, 90), c=(40, 130), W_d=(55, 115), W_az=(-60, 30),
             v3_off=(25, 50), v3_dir=(0, 360), s=(-1, 1), det_min=(0.05, 0.15), pct=(80, 100), w=(8, 12))


def bvec(az, el): return CBL.bvec(az, el)
def wdir(d, a): return CBL.w_dir(d, a)
def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def rotm(ax, ang):
    ax = unit(np.asarray(ax, float)); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def v3_of(W, off, dirdeg):
    """the second arm axis: W turned off deg toward dirdeg in W's tangent plane (0 = anterior / increasing azimuth,
    90 = away from the elbow, 180 = posterior, 270 = toward the elbow)"""
    down = np.array([0.0, -1.0, 0.0]); td = unit(-(down - (down @ W) * W)); ta = np.cross(W, td)
    if ta @ wdir(90, 90) < 0: ta = -ta
    t = math.cos(dirdeg * D2R) * ta + math.sin(dirdeg * D2R) * td
    return rotm(np.cross(W, t), off * D2R) @ W


def circ(c1, r1, c2, r2, s):
    """two-circle closure (= band_impl circ_int) and the serial margin (rad)"""
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2)); den = 1 - dd ** 2 + 1e-12
    a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    th = np.arccos(dd); m = np.minimum(np.minimum(th - abs(r1 - r2), r1 + r2 - th), 2 * math.pi - r1 - r2 - th)
    return p + s * np.sqrt(np.clip(h2, 0, None))[..., None] * n, m


def tang(x, y):
    """unit tangent at x toward y on the sphere"""
    return unit(y - (x * y).sum(-1, keepdims=True) * x)


def sang(a, b, ax):
    """signed angle a -> b about ax (deg)"""
    return np.degrees(np.arctan2((np.cross(a, b) * ax).sum(-1), (a * b).sum(-1)))


# ------------------------------------------------------------------------------------------------ pose data
class Rig:
    def __init__(self, B):
        Z = CB._poses_all(); self.B = B
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); self.cl = self.kind == "clip"
        self.order = B.clip_order()
        self.rest = min(np.nonzero(self.cl)[0], key=lambda j: B.poses[j]["elev"])
        self.harm = np.einsum("pij,j->pi", self.RS @ self.HG, np.array([0.0, -1.0, 0.0]))


def design(p):
    U = np.array([bvec(*x) for x in p["u"]]); W = wdir(*p["W"]); V = v3_of(W, p["v3_off"], p["v3_dir"])
    return U, W, V


def solve(p, HG):
    """closed-form IK over poses (HG (P, 3, 3)); everything in the scapula frame"""
    U, W, V = design(p); Wt = HG @ W; Vt = HG @ V; T = [Wt, Wt, Vt]; E = []; M = []
    for k in range(3):
        e, m = circ(np.broadcast_to(U[k], Wt.shape), p["a"][k] * D2R, T[k], p["c"][k] * D2R, p["s"][k]); E.append(e); M.append(m)
    E = np.stack(E, 1); M = np.stack(M, 1)
    n1 = unit(np.cross(E[:, 0], Wt)); n2 = unit(np.cross(E[:, 1], Wt)); n3 = unit(np.cross(E[:, 2], Vt))
    det = (np.cross(n1, n2) * n3).sum(-1)
    sep = np.min(np.stack([np.arccos(np.clip((E[:, i] * E[:, j]).sum(-1), -1, 1)) for i, j in ((0, 1), (0, 2), (1, 2))], 1), 1)
    return dict(U=U, W=W, V=V, Wt=Wt, Vt=Vt, E=E, M=M, det=det, sep=sep)


def joint_values(S, HG):
    """9 joint angles per pose (deg): base angles, elbow angles, arm-pin angles (C1, C2 about W; C3 about v3)"""
    U = S["U"]; E = S["E"]; Wt, Vt = S["Wt"], S["Vt"]; T = [Wt, Wt, Vt]
    out = []
    for k in range(3):
        u = U[k]; r1 = unit(np.cross(u, [0.0, 0.0, 1.0] if abs(u[2]) < 0.9 else [1.0, 0, 0]))
        out.append(sang(np.broadcast_to(r1, E[:, k].shape), tang(np.broadcast_to(u, E[:, k].shape), E[:, k]), np.broadcast_to(u, E[:, k].shape)))
    for k in range(3):
        out.append(sang(tang(E[:, k], np.broadcast_to(U[k], E[:, k].shape)), tang(E[:, k], T[k]), E[:, k]))
    ref = unit(np.cross(HG @ S["W"], HG @ np.array([0.0, -1.0, 0.0])))   # arm-fixed tangent reference at W / v3
    refv = unit(np.cross(HG @ S["V"], HG @ np.array([0.0, -1.0, 0.0])))
    for k, (t, r) in enumerate(((Wt, ref), (Wt, ref), (Vt, refv))):
        out.append(sang(r, tang(t, E[:, k]), t))
    return np.stack(out, 1)


def slerp(R0, R1, ts):
    D = R0.T @ R1; ang = math.acos(np.clip((np.trace(D) - 1) / 2, -1, 1))
    if ang < 1e-9: return np.array([R0 for _ in ts])
    ax = np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]])
    if np.linalg.norm(ax) < 1e-9:
        w, v = np.linalg.eigh((D + np.eye(3)) / 2); ax = v[:, -1]
    return np.array([R0 @ rotm(ax, ang * t) for t in ts])


def kinematics(p, rig):
    """per pose: kinematic validity (closure, margins, det sign at rest, elbow separation) + clip path continuity"""
    S = solve(p, rig.HG); mg = p["margin"] * D2R
    sg = np.sign(S["det"][rig.rest]) or 1.0
    ok_leg = (S["M"] >= mg).all(1)
    ok = ok_leg & (S["det"] * sg >= p["det_min"]) & (S["sep"] >= p["sep"] * D2R)
    J = joint_values(S, rig.HG)
    path = np.ones(len(ok), bool)
    for c, js in rig.order.items():
        prev = None
        for j in js:
            if not ok[j]: continue
            if prev is not None:
                d = np.abs((J[j] - J[prev] + 180) % 360 - 180)
                if d.max() > JUMP: path[j] = False
                else:
                    Rs = slerp(rig.HG[prev], rig.HG[j], np.linspace(0, 1, N_SUB + 2)[1:-1]); Ss = solve(p, Rs)
                    if not ((Ss["M"] >= mg).all() and (Ss["det"] * sg > 0.5 * p["det_min"]).all()): path[j] = False
            if path[j]: prev = j
    S.update(ok=ok & path, kin=ok, path=path, sign=sg, J=J, why=dict(leg=int((~ok_leg).sum()), det=int((ok_leg & (S["det"] * sg < p["det_min"])).sum()),
                                                                     sep=int((ok_leg & (S["sep"] < p["sep"] * D2R)).sum()), path=int((ok & ~path).sum())))
    return S


# ------------------------------------------------------------------------------------------------ skin maps (fit only)
def map_path(key):
    return os.path.join(REPO, ".cache", "concept_models", ID, f"rmapo_{key}_112.npy")


class Maps:
    """outermost skin crossing radius per pose and direction (cube maps of docs/concepts/models/deltoid-strut-tripod.py
    raymap_outer, channel 1), bilinear; used only to FIT profiles - scores come from B.dist"""
    def __init__(self, B):
        path = map_path(B.key)
        if not os.path.exists(path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("dst", os.path.join(HERE, "deltoid-strut-tripod.py")); dst = importlib.util.module_from_spec(spec); spec.loader.exec_module(dst)
            M = np.empty((len(B.poses), 6, dst.CM_N, dst.CM_N), np.float32); Fi = np.asarray(CB.BP.F); t = time.time()
            for i in range(len(B.poses)):
                M[i] = dst.raymap_outer(np.asarray(B._verts(i), float), Fi)[1]
                if i % 20 == 0: print(f"  map {i}/{len(B.poses)} {time.time() - t:.0f} s", flush=True)
            os.makedirs(os.path.dirname(path), exist_ok=True); np.save(path + ".tmp.npy", M); os.replace(path + ".tmp.npy", path)
        import importlib.util
        spec = importlib.util.spec_from_file_location("dst", os.path.join(HERE, "deltoid-strut-tripod.py")); self.dst = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.dst); self.M = np.load(path, mmap_mode="r")

    def r(self, I, D):
        """poses I (n,), unit directions D (n, m, 3) -> outermost skin radius (n, m) (inf: no exit within 270 mm)"""
        n, m = D.shape[:2]
        return self.dst.cm_lookup(self.M, D.reshape(-1, 3), np.repeat(np.asarray(I), m)).reshape(n, m)


# ------------------------------------------------------------------------------------------------ the model
def mst(U):
    d = np.arccos(np.clip(U @ U.T, -1, 1)); pairs = sorted([(d[i, j], i, j) for i in range(3) for j in range(i + 1, 3)])
    return [(i, j) for _, i, j in pairs[:2]]


class Model:
    """one configuration on one bench: kinematics, fitted rigid parts, metal(i) -> skin-facing samples or None"""
    def __init__(self, p, B, rig, maps):
        self.p = p = dict(PARAMS, **p); self.B, self.rig, self.maps = B, rig, maps
        self.K = K = kinematics(p, rig); self.ok = K["ok"].copy(); self.valid = np.nonzero(self.ok)[0]
        self.fail = None
        U, W, V = K["U"], K["W"], K["V"]
        ang_u = np.degrees(np.arccos(np.clip(U @ U.T, -1, 1)))
        if min(ang_u[0, 1], ang_u[0, 2], ang_u[1, 2]) * D2R * 60.0 < 2 * O20["r"] + CLR:
            self.fail = "base hubs overlap"; self.ok[:] = False; self.valid = self.valid[:0]
        if len(self.valid) < 8:
            self.fail = self.fail or "kinematics"; self.ok[:] = False; return
        self.build()

    # ---- geometry per pose (thorax frame) ----
    def axes(self, I):
        rig, K = self.rig, self.K; RS = rig.RS[I]
        Uw = np.einsum("pij,kj->pki", RS, K["U"]); Ew = np.einsum("pij,pkj->pki", RS, K["E"][I])
        Ww = np.einsum("pij,pj->pi", RS, K["Wt"][I]); Vw = np.einsum("pij,pj->pi", RS, K["Vt"][I])
        return Uw, Ew, Ww, Vw

    def parts_dirs(self, I, width_scale=1.0, centre=False):
        """{part: (dirs (n, ns, nc, 3), arc deg, (joint0, joint1), width)} for poses I; centre=True: centre lines only"""
        p = self.p; Uw, Ew, Ww, Vw = self.axes(I); RH = self.rig.RS[I] @ self.rig.HG[I]
        wd = (lambda w: 0.0) if centre else (lambda w: w)
        P = {}
        for (i, j) in mst(self.K["U"]):
            ang = math.degrees(math.acos(np.clip(self.K["U"][i] @ self.K["U"][j], -1, 1)))
            P[f"BF{i}{j}"] = (CBL.arc_dirs(Uw[:, i], Uw[:, j], ang * D2R, width=wd(W_BF)), ang, (f"HB{i}", f"HB{j}"), W_BF)
        T = [Ww, Ww, Vw]; TJ = ["HW", "HW", "HV"]
        for k in range(3):
            P[f"K{k}"] = (CBL.arc_dirs(Uw[:, k], Ew[:, k], p["a"][k] * D2R, width=wd(p["w_crank"])), p["a"][k], (f"HB{k}", f"HE{k}"), p["w_crank"])
            P[f"C{k}"] = (CBL.arc_dirs(Ew[:, k], T[k], p["c"][k] * D2R, width=wd(p["w_coup"])), p["c"][k], (f"HE{k}", TJ[k]), p["w_coup"])
        # arm plate: W -> v3 in the humerus frame, extended 8 mm beyond each pin
        ext = 8.0 / R_REF; off = p["v3_off"] * D2R; n = unit(np.cross(Ww, Vw))
        Wx = np.einsum("pij,pj->pi", np.array([rotm(a, -ext) for a in n]), Ww); Vx = np.einsum("pij,pj->pi", np.array([rotm(a, ext) for a in n]), Vw)
        P["AP"] = (CBL.arc_dirs(Wx, Vx, off + 2 * ext, width=wd(W_PLATE)), math.degrees(off + 2 * ext), ("HWx", "HVx"), W_PLATE)
        ng = p["neck_deg"] * D2R; harm = self.rig.harm[I]
        nk = unit(np.cos(ng) * Ww + np.sin(ng) * tang(Ww, harm))
        P["NK"] = (CBL.arc_dirs(Ww, nk, ng, width=wd(W_NECK)), p["neck_deg"], ("HW", None), W_NECK)
        return P

    def joint_axes(self, I):
        Uw, Ew, Ww, Vw = self.axes(I)
        J = {f"HB{k}": Uw[:, k] for k in range(3)} | {f"HE{k}": Ew[:, k] for k in range(3)}
        J["HW"] = Ww; J["HV"] = Vw; return J

    # joint table: lower member body, members, hardware, stack offset of each member above the lower face F
    def joints(self):
        J = {}
        for k in range(3):
            J[f"HB{k}"] = dict(hw=O20, lower="BF", off={"BF": 0.0, f"K{k}": O20["up"]})
            J[f"HE{k}"] = dict(hw=P14, lower=f"K{k}", off={f"K{k}": 0.0, f"C{k}": P14["up"]})
        J["HW"] = dict(hw=O16, lower="AP", off={"AP": 0.0, "C0": O16["up"], "C1": 2 * O16["up"]})
        J["HV"] = dict(hw=P14, lower="AP", off={"AP": 0.0, "C2": P14["up"]})
        return J

    @staticmethod
    def body(part):
        return "BF" if part.startswith("BF") else "AP" if part in ("AP", "NK") else part

    def layer(self, body):
        return 0 if body in ("BF", "AP") else 1 + list(self.p["layers"]).index(body)

    def jlayer(self, jn):
        return max(self.layer(b) for b in self.JT[jn]["off"])

    def centre(self, nm, D, prof):
        """centre line of part nm: unit directions (n, ns, 3), radial interval lo, hi (ns,), half-width"""
        t = T_PLATE if nm == "AP" else T_STRAP
        return unit(D.mean(2)), prof.min(1), prof.max(1) + t, self.meta[nm]["w"] / 2

    def build(self):
        """fit every part's radial profile over the taken poses (pct percentile of the outermost skin + clear), flat
        joint discs at their stack levels, 45 deg ramps, then stack the moving bodies in `layers` order: a body is
        raised over every lower body / joint crown it overlaps in the fit poses (same percentile), ramped at 45 deg"""
        p, I = self.p, self.valid
        P = self.parts_dirs(I); self.Pfit = P; JA = self.joint_axes(I); JT = self.joints(); self.JT = JT
        q = p["pct"]
        def agg(R): return np.max(R, 0) if q >= 100 else np.percentile(R, q, axis=0)
        def fit(D):
            R = self.maps.r(I, D); return agg(np.where(np.isfinite(R), R, 400.0)) + p["clear"]
        self.F = {}
        for nm, jt in JT.items():                                  # joint lower faces: max of the fit over the disc
            self.F[nm] = float(fit(CBL.disc_dirs(JA[nm], jt["hw"]["r"])).max())
        raw, self.meta = {}, {}
        for nm, (D, ang, js, w) in P.items():
            n, ns, nc, _ = D.shape; raw[nm] = fit(D.reshape(n, -1, 3)).reshape(ns, nc)
            rho = float(np.mean(raw[nm])); s = np.linspace(0, 1, ns)
            self.meta[nm] = dict(ang=ang, j=js, w=w, ns=ns, nc=nc, L=ang * D2R * rho, s=s)
        self.prof = {}
        order = ["BF" + "".join(map(str, e)) for e in mst(self.K["U"])] + ["AP", "NK"] + list(p["layers"])
        for nm in order:
            prof = raw[nm].copy(); m = self.meta[nm]; bd = self.body(nm); s = m["s"]; L = m["L"]; hide = np.zeros(m["ns"], bool)
            for jn, l in ((m["j"][0], s * L), (m["j"][1], (1 - s) * L)):
                if jn is None: continue
                if jn in ("HWx", "HVx"):                          # plate: flat over the pin discs
                    jj = "HW" if jn == "HWx" else "HV"; r = JT[jj]["hw"]["r"]; lp = l - 8.0 * np.mean(prof) / R_REF
                    flat = np.abs(lp) <= r; prof[flat] = np.maximum(prof[flat], self.F[jj]); continue
                jt = JT[jn]; r = jt["hw"]["r"]; lev = self.F[jn] + jt["off"][bd]
                prof = np.maximum(prof, (lev - SLOPE * np.maximum(0.0, l - r - LAND))[:, None])
                hide |= l < r                                     # over the joint's disc: the disc / plate is the face
            if self.layer(bd) > 0 and p.get("stack", True): prof = self.stack(nm, prof, JA)
            self.prof[nm] = prof; m["hide"] = hide
            if nm.startswith("K"):                                # the crank carries the elbow pin disc: level follows
                k = int(nm[1]); r = P14["r"]; near = (1 - s) * L < r
                self.F[f"HE{k}"] = max(self.F[f"HE{k}"], float(prof[near].max()))
        self.ok_fit = True

    def stack(self, nm, prof, JA):
        """raise part nm over the lower bodies and the joint crowns below its layer that it overlaps (fit poses)"""
        P = self.Pfit; bd = self.body(nm); ly = self.layer(bd); q = self.p["pct"]; m = self.meta[nm]
        Dx, lox, hix, hwx = self.centre(nm, P[nm][0], prof)
        req = np.full(Dx.shape[:2], -np.inf)
        names = list(self.JT)
        for on, opr in self.prof.items():
            ob = self.body(on)
            if ob == bd or self.layer(ob) >= ly: continue
            Do, loo, hio, hwo = self.centre(on, P[on][0], opr)
            G = np.arccos(np.clip(np.einsum("nai,nbi->nab", Dx, Do), -1, 1)) * 0.5 * (lox[None, :, None] + loo[None, None, :])
            ov = G < hwx + hwo + CLR
            for jn in names:                                      # shared joints: exempt inside the joint zone
                mem = self.JT[jn]["off"]
                if bd in mem and ob in mem:
                    r = self.JT[jn]["hw"]["r"] + 2.0; a = JA[jn]
                    zx = np.arccos(np.clip(np.einsum("nai,ni->na", Dx, a), -1, 1)) * lox[None] < r
                    zo = np.arccos(np.clip(np.einsum("nbi,ni->nb", Do, a), -1, 1)) * loo[None] < r
                    ov &= ~(zx[:, :, None] | zo[:, None, :])
            req = np.maximum(req, np.where(ov, hio[None, None, :] + CLR, -np.inf).max(-1))
        for jn in names:                                          # joint crowns below this layer
            if bd in self.JT[jn]["off"] or self.jlayer(jn) >= ly: continue
            hw = self.JT[jn]["hw"]; a = JA[jn]
            ov = np.arccos(np.clip(np.einsum("nai,ni->na", Dx, a), -1, 1)) * lox[None] < hw["r"] + hwx + CLR
            req = np.maximum(req, np.where(ov, self.F[jn] + hw["crown"] + CLR, -np.inf))
        if not np.isfinite(req).any(): return prof
        rq = np.max(req, 0) if q >= 100 else np.percentile(np.where(np.isfinite(req), req, -1e3), q, axis=0, method="higher")
        l = m["s"] * m["L"]; rq = np.max(rq[None, :] - SLOPE * np.abs(l[:, None] - l[None, :]), 1)     # 45 deg ramps
        return np.maximum(prof, rq[:, None])

    # ---- per pose ----
    def metal(self, i, detail=False):
        """skin-facing samples (k, 3) of pose i, or None (not taken: kinematics, path, collision)"""
        if not self.ok[i]: return ("kin",) if detail else None
        I = np.array([i]); P = self.parts_dirs(I); JA = {k: v[0] for k, v in self.joint_axes(I).items()}
        face = []
        for nm, (D, ang, js, w) in P.items():
            X = D[0] * self.prof[nm][..., None]; face.append(X[~self.meta[nm]["hide"]].reshape(-1, 3))
        for nm, jt in self.JT.items():
            if jt["lower"] == "AP": continue                       # the plate's own samples cover the arm pins
            face.append(CBL.disc_dirs(JA[nm][None], jt["hw"]["r"])[0] * self.F[nm])
        col = self.collide(P, JA)
        if col is not None: return ("collide",) + col if detail else None
        return np.concatenate(face)

    def collide(self, P, JA):
        """first colliding pair or None: centre-line samples with half-widths and radial intervals, joint cylinders;
        bodies sharing a joint are checked outside its footprint + 2 mm"""
        Ds, lo, hi, hw, bd = [], [], [], [], []
        for nm, (D, ang, js, w) in P.items():
            d, l_, h_, w_ = self.centre(nm, D, self.prof[nm]); Ds.append(d[0]); lo.append(l_); hi.append(h_); hw.append(np.full(len(l_), w_)); bd += [self.body(nm)] * len(l_)
        D, lo, hi, hw = np.concatenate(Ds), np.concatenate(lo), np.concatenate(hi), np.concatenate(hw)
        JT = self.JT; names = list(JT); Ax = np.array([JA[n] for n in names])
        ang_j = np.arccos(np.clip(D @ Ax.T, -1, 1))
        zone = ang_j * lo[:, None] < np.array([JT[n]["hw"]["r"] + 2.0 for n in names])[None]
        mem = [set(JT[n]["off"]) for n in names]
        bodies = sorted(set(bd)); bix = np.array([bodies.index(b) for b in bd])
        G = np.arccos(np.clip(D @ D.T, -1, 1)) * 0.5 * (lo[:, None] + lo[None])
        hit = (G < hw[:, None] + hw[None] + CLR) & (lo[:, None] < hi[None] + CLR) & (lo[None] < hi[:, None] + CLR)
        hit &= bix[:, None] != bix[None]
        for k, n in enumerate(names):
            inb = np.array([b in mem[k] for b in bd]); z = zone[:, k]
            hit &= ~((inb[:, None] & inb[None]) & (z[:, None] | z[None]))
        if hit.any():
            a, b = np.argwhere(hit)[0]; return (bd[a], bd[b])
        for k, n in enumerate(names):                              # joint cylinders vs straps of non-members
            r = JT[n]["hw"]["r"]; F = self.F[n]; top = F + JT[n]["hw"]["crown"]
            notm = np.array([b not in mem[k] for b in bd])
            h = notm & (ang_j[:, k] * lo < r + hw + CLR) & (lo < top + CLR) & (hi > F - CLR)
            if h.any(): return (n, bd[int(np.argmax(h))])
        for a in range(len(names)):                                # joint cylinders vs each other
            for b in range(a + 1, len(names)):
                if mem[a] & mem[b]: continue
                ra, rb = JT[names[a]]["hw"]["r"], JT[names[b]]["hw"]["r"]; Fa, Fb = self.F[names[a]], self.F[names[b]]
                ta, tb = Fa + JT[names[a]]["hw"]["crown"], Fb + JT[names[b]]["hw"]["crown"]
                g = math.acos(np.clip(Ax[a] @ Ax[b], -1, 1)) * 0.5 * (Fa + Fb)
                if g < ra + rb + CLR and Fa < tb + CLR and Fb < ta + CLR: return (names[a], names[b])
        return None


class ProxyBench:
    """the bench's bookkeeping with a cheap distance (radial gap to the outermost skin crossing): screening only"""
    record = CB.Bench.record; report = CB.Bench.report
    def __init__(self, B, maps):
        self.B, self.maps, self.kind, self.poses, self.mode = B, maps, B.kind, B.poses, "proxy"; self.reset()
    def reset(self): self.res = [None] * len(self.kind)
    def dist(self, i, P):
        P = np.asarray(P, float); r = np.linalg.norm(P, axis=1); R = self.maps.r(np.array([i]), (P / r[:, None])[None])[0]
        return r - np.where(np.isfinite(R), R, 400.0)


def evaluate(p, B, rig, maps):
    t0 = time.time(); B.reset(); M = Model(p, B, rig, maps)
    why = dict(M.K["why"]); why.update(collide=0, fail=M.fail)
    from collections import Counter
    pairs = Counter()
    for i in range(len(B.poses)):
        if not M.ok[i]: B.record(i, None); continue
        out = M.metal(i, detail=True)
        if isinstance(out, tuple):
            why["collide"] += 1; pairs[tuple(sorted(out[1:]))] += 1; B.record(i, None); continue
        B.record(i, out)
    r = B.report(); r["why"] = why; r["pairs"] = dict(pairs.most_common(4)); r["secs"] = round(time.time() - t0, 1)
    r["kin_ws"] = round(float(M.ok[~rig.cl].mean()), 3); r["kin_clip"] = round(float(M.ok[rig.cl].mean()), 3)
    return r, M


def jsonable(p):
    return json.loads(json.dumps(p))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (60, 160)
        B = CB.Bench(nc, nw); rig = Rig(B); maps = Maps(B); print("bench", B.mode, len(B.poses))
        r, M = evaluate({}, B, rig, maps); print(r)
        print({k: round(v, 1) for k, v in M.F.items()})
        for nm, pr in M.prof.items(): print(nm, np.percentile(pr, [0, 50, 100]).round(1))
