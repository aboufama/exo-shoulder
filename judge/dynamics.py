"""JUDGE (dynamics): does the chain actually move when the arm drives it, with real joint friction, link inertia,
gravity and a soft cuff? (user, 2026-10-15: "if there's some slight friction perhaps it will be hard for a linkage to pass
over another because it's pressing from a bad action angle ... It needs to actually work"). MuJoCo 3.16, local CPU.

Model (SI units inside MuJoCo; the body rig frame: thorax, x anterior, y up, z right, origin = right GH centre):
  scapula  ball joint at the GH centre, driven kinematically along the clip's scapula law (huge armature + feed-forward
           PD: the chain sees the base's real angular velocity and acceleration, the base does not feel the chain).
           The base part rides it rigidly (the user's scapula handler is a separate part).
  links    l1..l(N-1): serial hinges J1..J(N-1) whose axes pass through the GH centre (design.json kinematics, the
           band evaluator's chain(): b = bvec(az, el), arcs a, branch); mass / COM / inertia from the L1 meshes in exo.glb
           per motion group (trimesh, welded closed components; Ti-6Al-4V 4.43 g/cm3, hardware by name, user parts 2.8).
  cuff     the arm-side member at JN (hinge about W, fixed on the arm), joined to the humerus bone through a 6-axis
           soft-tissue spring-damper at the upper-arm cuff (Schiebl et al. 2025, Sensors 25:4605: 3.5 N/mm across the
           arm, 2.1 N/mm along it, 0.2 N.m/deg bending, 0.03 N.m/deg torsion). The bone follows the clip kinematically
           (the motion the exo follows, "p", smoothed with PCHIP through the clip's knots). Interaction = the tissue wrench.
           The cuff member is light (20 g, gravity compensated): the user's arm parts are carried by the arm and their
           weight is reported, not added, so every N and N.m below is what the shoulder chain adds.
  joints   every hinge passive (MVP1 is unpowered, user 2026-10-15). Friction, exact Coulomb (frictionloss with the
           noslip solver - MuJoCo's default soft friction is viscous at low speed, see docs/research/dynamics_judge.md):
           MAIN: rolling bearings, load-dependent, tau_f = tau0 + mu_eff |M_perp| with mu_eff 0.002 / 0.005 and tau0 0.001 N.m
             (M_perp = the joint's reaction moment perpendicular to its axis about the bearing centre, from cfrc_int each step);
           COMPARISON: plain bearings, the same law with mu_eff 0.06-0.37, tau0 0.05 N.m (red team G6, pipeline/redteam/
             rt_wedge.py: wedging), tilt about the bearing centre (hub) and about GH (gh, rt_wedge.py's model);
           and the brief's constant torques 0.05 / 0.2 / 0.5 N.m per joint.
  contact  stacked links: hub discs as cylinders, ribbons as capsule chains at their real height and thickness (from the
           meshes), mu 0.2; the designed bearing (hub on hub, hub on the other member's hub-side ribbon root at a shared
           joint) is the hinge itself and is not a contact.
For N = 4 the passive chain's spare DOF is free: it does what friction, gravity and inertia make it do, and its drift from
the evaluator's planned path (which the geometric judges assume) is reported. Motor (back-driven gearmotor armature) and
servo (spare J1 on the plan) cases remain as --cases options; validate() uses the servo only as a numerical device.
Outputs per clip: interaction force (N) and moment (N.m) at the cuff and about GH, mean cuff pressure (kPa) on the cuff's
68 cm2 skin side vs the 14 kPa sustained budget, joint speeds / accelerations, cuff tracking (twist about the humerus,
swing), stalls, lock frames, link-link contact, the worst frames with their friction amplification and axis condition.

    python3 judge/dynamics.py <design id> [--friction 0.2] [--speed 1.0] [--mu_roll 0.002,0.005] [--mu_eff ...] [--jobs 4]
        -> <design>/judge/dynamics.json  (defaults: rolling 0.002 / 0.005 x speed 1, 2 (main); plain 0.06-0.37 x tilt
           hub, gh at speed 1; constant 0.05 / 0.2 / 0.5 x speed 1, 2; attribution runs; both validations.
           Comma lists; '' switches a sweep off; --quick: the nominal rolling-bearing case only)
"""
import argparse, contextlib, json, math, multiprocessing as mp, os, sys, time
import numpy as np
from common import design_dir, load_parts, PIPE

D2R = math.pi / 180
VERSION = "dynamics-2026-10-15b (MVP1: unpowered; rolling bearings main, plain bearings comparison)"
# ---------------------------------------------------------------- assumptions (all stated in docs/research/dynamics_judge.md)
TISSUE = dict(k_perp=3.5e3, k_ax=2.1e3,                   # N/m across / along the humerus (Schiebl 2025 medians 2.1-4.5 N/mm)
              kr_perp=0.20 / D2R, kr_ax=0.03 / D2R,       # N.m/rad bending / torsion (Schiebl 2025: 0.18-0.22, 0.03 N.m/deg)
              c_t=20.0, cr_perp=0.10, cr_ax=0.02)         # damping N.s/m, N.m.s/rad (assumed: Schiebl report it negligible)
CUFF_MM = 200.0             # cuff centre on the humerus axis, mm from GH (user's upper-arm cuff, cad_r13: 200 mm)
CUFF_MASS = 0.020           # kg, arm-side member at JN (gravity compensated; numerical only)
ARM_MOTOR = 0.03            # kg m^2 reflected: ~1.2e-5 kg m^2 rotor (45 mm flat BLDC class) x 50:1 gearhead
SERVO_WN = 2 * math.pi * 15.0
FRICTIONS = (0.05, 0.2, 0.5); SPEEDS = (1.0, 2.0)
DT = 2e-4; REC = 5; SETTLE = 0.5; MU_CONTACT = 0.2; HW = 7.0
MU_EFFS = (0.06, 0.15, 0.25, 0.37); TAU0 = 0.05      # plain bearings (comparison): load-dependent friction sweep (red team G6), no-load torque N.m
MU_ROLL = (0.002, 0.005); TAU0_ROLL = 0.001          # rolling bearings (MVP1 main case): mu_eff = mu_SKF d / L for a bearing pair, shielded no-load drag
CUFF_AREA_CM2 = 68.0        # skin side of the user's upper-arm cuff shell (cad_r13_n4_s1343_1, faces facing the humerus axis)
STRAP_KPA = 6.5             # strap preload that gives Schiebl's stiffness (65 mbar attachment pressure)
COMFORT_KPA = 14.0          # sustained (all-day) interface pressure budget at the cuff (lead / user, 2026-10-15)
THRESH = dict(free_moment_gh_peak_Nm=1.0, free_moment_gh_rms_Nm=0.5, free_force_peak_N=5.0, free_twist_peak_deg=5.0,
              free_spare_drift_deg=5.0, iso_ts_15066_upper_arm_N=150.0, lock_moment_gh_Nm=10.0)
LAG_DEG = 10.0              # a stall that misses >= this much planned joint travel: the exo is no longer where the geometric judges put it
G_CM3 = {"ti": 4.43, "iglidur": 1.46, "magnet": 7.5, "pcb": 1.85, "ic": 2.0, "steel": 7.9, "alsi10mg": 2.67, "7075": 2.81, "user": 2.8}

def density(group, name):
    n = name.lower()
    if "magnet" in n or "n52" in n or "n42" in n: return G_CM3["magnet"]
    if "igus" in n or "iglid" in n or "sleeve" in n or "washer" in n: return G_CM3["iglidur"]
    if "pcb" in n: return G_CM3["pcb"]
    if "sensor ic" in n: return G_CM3["ic"]
    if "screw" in n or "iso 10642" in n or "m1.6" in n or "m4" in n: return G_CM3["ti"] if " ti" in n else G_CM3["steel"]
    if "alsi10mg" in n: return G_CM3["alsi10mg"]
    if "7075" in n: return G_CM3["7075"]
    if "ti-6al-4v" in n or "(proxy)" in n or group not in ("H", "F"): return G_CM3["ti"]
    return G_CM3["user"]

# ---------------------------------------------------------------- small rotation helpers (numpy, batched)
def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def Ry(a): c, s = np.cos(a), np.sin(a); o, z = np.ones_like(a), np.zeros_like(a); return np.stack([np.stack([c, z, s], -1), np.stack([z, o, z], -1), np.stack([-s, z, c], -1)], -2)
def Rx(a): c, s = np.cos(a), np.sin(a); o, z = np.ones_like(a), np.zeros_like(a); return np.stack([np.stack([o, z, z], -1), np.stack([z, c, -s], -1), np.stack([z, s, c], -1)], -2)
def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax); a = np.asarray(a, float)[..., None, None]
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * K @ K
def vee(S): return np.stack([S[..., 2, 1] - S[..., 1, 2], S[..., 0, 2] - S[..., 2, 0], S[..., 1, 0] - S[..., 0, 1]], -1) / 2
def rotvec(R):
    """rotation vector of R (..., 3, 3)"""
    c = np.clip((np.trace(R, axis1=-2, axis2=-1) - 1) / 2, -1, 1); th = np.arccos(c); v = vee(R); s = np.sin(th)
    k = np.where(s > 1e-9, th / np.maximum(s, 1e-12), 1.0)
    return v * k[..., None]
def angle_about(R, u):
    """signed angle of the rotation R about the unit axis u (R assumed to be a rotation about u)"""
    return np.arctan2(vee(R) @ u, (np.trace(R, axis1=-2, axis2=-1) - 1) / 2)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(d, a): d, a = d * D2R, a * D2R; return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])
def scap(el, smooth=1.5):
    """scapula rotation in the thorax (body_pose.scap); smooth > 0 rounds the max(0, el - 20) kink over ~smooth deg
    (the rig's law has an angular-velocity step at 20 deg that would put an artificial impulse into the base)"""
    el = np.asarray(el, float); x = el - 20.0
    up = smooth * np.logaddexp(0.0, x / smooth) if smooth > 0 else np.maximum(0.0, x)
    n = [math.cos(30 * D2R), 0, -math.sin(30 * D2R)]
    return rot([0, 0, 1], 0.12 * el * D2R) @ rot(n, -0.36 * up * D2R)
def humerus(pose):
    """canonical humerus frame in the thorax for poses (..., >=3) [plane, elev, axial] deg (body_pose.segs)"""
    p = np.asarray(pose, float) * D2R; return Ry(p[..., 0]) @ Rx(-p[..., 1]) @ Ry(p[..., 2])

# ---------------------------------------------------------------- the chain (band_impl.chain, numpy)
class Chain:
    """spherical N-R chain of a design: pins = joint axes J1..JN in the scapula frame; N = 3 (pure 3R) or 4 (J1 spare)"""
    def __init__(self, kin):
        self.N = len(kin["a"]) + 1; self.A = [x * D2R for x in kin["a"]]; self.branch = float(kin["branch"])
        if self.N not in (3, 4): raise ValueError("dynamics judge: N = 3 or 4 joints (no sliding cuff)")
        self.b = bvec(kin["az"], kin["el"]); self.W = w_dir(*kin["w"])
        self.e = unit(np.cross(self.b, [0, 1.0, 0])); self.f = np.cross(self.b, self.e)
    def spare_of(self, p2):
        return np.arctan2(p2 @ self.f, p2 @ self.e)
    def pins(self, HG, q=None):
        """(n, N, 3) axes and closure ok (n,) for humerus-in-scapula rotations HG (n, 3, 3), spare J1 angles q (n,)"""
        n = HG.shape[0]; b = np.broadcast_to(self.b, (n, 3)); P = [b]
        if self.N == 4:
            P.append(math.cos(self.A[0]) * b + math.sin(self.A[0]) * (np.cos(q)[:, None] * self.e + np.sin(q)[:, None] * self.f))
        pa = P[-1]; pz = HG @ self.W; r1, r2 = self.A[self.N - 3], self.A[self.N - 2]
        dd = np.clip((pa * pz).sum(-1), -1, 1); nn = unit(np.cross(pa, pz)); den = 1 - dd ** 2 + 1e-12
        a = (math.cos(r1) - dd * math.cos(r2)) / den; bb = (math.cos(r2) - dd * math.cos(r1)) / den
        p = a[:, None] * pa + bb[:, None] * pz; h2 = 1 - (p * p).sum(-1)
        pc = p + self.branch * np.sqrt(np.clip(h2, 0, None))[:, None] * nn
        return np.stack(P + [pc, pz], 1), h2 > -2e-3
    @staticmethod
    def frame(a, c):
        n = unit(c - (a * c).sum(-1, keepdims=True) * a); return np.stack([a, n, np.cross(a, n)], -1)
    def frames(self, pins):
        """link frames l1..l(N-1) (n, 3, 3) in the scapula frame (band_to_design.frames_of_members)"""
        return [self.frame(pins[:, k - 1], pins[:, k]) for k in range(1, self.N)]

# ---------------------------------------------------------------- design: chain, clips, mass properties, contact primitives
def mass_props(parts):
    """(mass kg, com m (3,), inertia about com kg m^2 (3,3), volume cm3) of a list of (group, name, V mm, F) parts"""
    import trimesh
    M, S, I_o, vol = 0.0, np.zeros(3), np.zeros((3, 3)), 0.0
    for g, nm, V, F in parts:
        m = trimesh.Trimesh(V / 1000.0, F, process=False); m.merge_vertices(digits_vertex=7); m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
        rho = density(g, nm) * 1000.0
        for c in m.split(only_watertight=False):
            if c.area < 1e-6 or len(c.faces) < 4: continue                    # zero-area slivers of a merged B-rep tessellation (fair CAD BOTTOM): no mass, and qhull fails on them
            if not c.is_watertight:
                try: c = c.convex_hull                                        # open shell: its hull (never happens on L1 meshes)
                except Exception: continue
            trimesh.repair.fix_normals(c); c.density = rho; mpp = c.mass_properties
            mi, ci, Ii = float(mpp["mass"]), np.asarray(mpp["center_mass"]), np.asarray(mpp["inertia"])
            M += mi; S += mi * ci; vol += float(mpp["volume"]) * 1e6
            I_o += Ii + mi * (np.dot(ci, ci) * np.eye(3) - np.outer(ci, ci))  # about the frame origin
    com = S / max(M, 1e-12)
    return M, com, I_o - M * (np.dot(com, com) * np.eye(3) - np.outer(com, com)), vol

def primitives(V, axes, hub_r, plane_n=None, step_mm=5.0, row_mm=4.0):
    """contact primitives of one member from its mesh vertices V (mm, member frame): per joint axis (J, u) a hub
    cylinder (radius hub_r, axial extent of the vertices within hub_r of the axis); the rest as a capsule chain along
    the member's great circle (normal plane_n, else the PCA normal), per station the real radial height and thickness,
    rows across the width. Returns [(kind, J or None, p0 mm, p1 mm, radius mm)], kind 'hub' | 'rib'."""
    out = []; r = np.linalg.norm(V, axis=1); U = V / r[:, None]; hubbed = np.zeros(len(V), bool)
    for J, u in axes:
        u = np.asarray(u, float); z = V @ u; dperp = np.linalg.norm(V - z[:, None] * u, axis=1); sel = (dperp <= hub_r + 0.5) & (z > 0)
        hubbed |= sel
        if sel.sum() >= 4: out.append(("hub", J, u * z[sel].min(), u * z[sel].max(), hub_r))
    R_ = V[~hubbed]
    if len(R_) < 6: return out
    Ur = unit(R_); rr = np.linalg.norm(R_, axis=1)
    n = np.asarray(plane_n, float) if plane_n is not None else np.linalg.eigh(Ur.T @ Ur)[1][:, 0]
    e1 = unit(Ur.mean(0) - (Ur.mean(0) @ n) * n); e2 = np.cross(n, e1)
    phi = np.arctan2(Ur @ e2, Ur @ e1); psi = np.arcsin(np.clip(Ur @ n, -1, 1)); rm = float(np.median(rr))
    nb = max(2, int(math.ceil((phi.max() - phi.min()) * rm / step_mm))); edges = np.linspace(phi.min(), phi.max() + 1e-9, nb + 1)
    st = []
    for i in range(nb):
        m = (phi >= edges[i]) & (phi < edges[i + 1])
        if m.sum() < 3: continue
        st.append((0.5 * (edges[i] + edges[i + 1]), rr[m].min(), rr[m].max(), psi[m].min(), psi[m].max()))
    if len(st) < 2: return out
    nrow = max(1, max(int(math.ceil(max(0.0, (p1 - p0) * 0.5 * (a + b) - (b - a)) / row_mm)) + 1 for _, a, b, p0, p1 in st))
    def pt(ph, ps, rad): return rad * (math.cos(ps) * (math.cos(ph) * e1 + math.sin(ph) * e2) + math.sin(ps) * n)
    for (ph0, a0, b0, s0, t0), (ph1, a1, b1, s1, t1) in zip(st[:-1], st[1:]):
        rad = max(1.0, 0.5 * max(b0 - a0, b1 - a1)); c0, c1 = 0.5 * (a0 + b0), 0.5 * (a1 + b1)
        for k in range(nrow):
            f = 0.5 if nrow == 1 else k / (nrow - 1)
            lo0, hi0 = s0 + rad / c0, t0 - rad / c0; lo1, hi1 = s1 + rad / c1, t1 - rad / c1
            q0 = lo0 + f * (hi0 - lo0) if hi0 > lo0 else 0.5 * (s0 + t0); q1 = lo1 + f * (hi1 - lo1) if hi1 > lo1 else 0.5 * (s1 + t1)
            out.append(("rib", None, pt(ph0, q0, c0), pt(ph1, q1, c1), rad))
    return out

class Design:
    def __init__(self, arg):
        self.dd = design_dir(arg); self.id = os.path.basename(os.path.normpath(self.dd))
        D = json.load(open(os.path.join(self.dd, "design.json"))); self.kin = D["kinematics"]; self.ch = Chain(self.kin); N = self.N = self.ch.N
        C = json.load(open(os.path.join(self.dd, "clips.json"))); self.clips = C["clips"]; self.hub_r = float(C.get("design", {}).get("hub_r") or 11.5)
        L = json.load(open(os.path.join(PIPE, "avg", "body_mesh.json"))); RH = np.array(L["landmarks"]["rest_humerus"]); u_, _, vt_ = np.linalg.svd(RH); self.HR = u_ @ vt_
        self.groups = ["base"] + [f"l{k}" for k in range(1, N)]
        parts = load_parts(self.dd)
        # reference configuration = frame 0 of the first clip (exact pose, hard scapula law, as the clip's G was built)
        f0 = self.clips[0]["frames"][0]; Rs0 = scap(f0["p"][1], 0); G0 = {g: np.array(v).reshape(3, 3) for g, v in f0["G"].items()}
        self.Fb = Rs0.T @ G0["base"]                                            # base group frame in the scapula frame
        self.mp = {}; self.prims = {}; self.H_mass = 0.0
        byg = {}
        for g, nm, V, F in parts: byg.setdefault(g, []).append((g, nm, V, F))
        A = self.ch.A
        for g in self.groups:
            P = byg.get(g, [])
            if g == "base": P = [(gg, nm, V @ self.Fb.T, F) for gg, nm, V, F in P]          # -> scapula frame
            self.mp[g] = mass_props(P) if P else (1e-3, np.zeros(3), 1e-9 * np.eye(3), 0.0)
            Vall = np.concatenate([p[2] for p in P]) if P else np.zeros((0, 3))
            if g == "base": ax = [(1, self.ch.b)]; pn = None
            else:
                k = int(g[1:]); ax = [(k, [1.0, 0, 0]), (k + 1, [math.cos(A[k - 1]), math.sin(A[k - 1]), 0.0])]; pn = [0, 0, 1.0]
            self.prims[g] = primitives(Vall, ax, self.hub_r, pn) if len(Vall) else []
        Hp = byg.get("H", [])
        self.H_mass = sum(mass_props([p])[0] for p in Hp) if Hp else 0.0
        self.F_mass = sum(mass_props([p])[0] for p in byg.get("F", [])) if byg.get("F") else 0.0
        hub = [(g, nm, V @ self.HR, F) for g, nm, V, F in Hp if np.linalg.norm(V, axis=1).min() < 130.0]   # rest -> canonical humerus
        Vh = np.concatenate([p[2] for p in hub]) if hub else np.zeros((0, 3))
        if len(Vh):
            Vh = Vh[np.linalg.norm(Vh, axis=1) < 130.0]; z = Vh @ self.ch.W; dp = np.linalg.norm(Vh - z[:, None] * self.ch.W, axis=1); s = dp <= self.hub_r + 0.5
            self.prims["cuff"] = [("hub", N, self.ch.W * z[s].min(), self.ch.W * z[s].max(), self.hub_r)] if s.sum() >= 4 else []
        else: self.prims["cuff"] = []
        self.bearing_r = {}                                                  # mm from GH: mid-height of the hubs stacked at each joint
        for J in range(1, N + 1):
            z = [np.linalg.norm(x) for v in self.prims.values() for kd, JJ, p0, p1, _ in v if kd == "hub" and JJ == J for x in (p0, p1)]
            self.bearing_r[J] = 0.5 * (min(z) + max(z)) if z else 70.0

    def clip_traj(self, ci):
        """smooth path of clip ci: PCHIP through the knots of the piecewise-linear 30 fps pose (and the spare J1 angle
        from the clip's G, N = 4) -> callables pose(s), spare(s), dspare(s) of the path frame s; plus per-frame data"""
        from scipy.interpolate import PchipInterpolator
        c = self.clips[ci]; Fr = c["frames"]; n = len(Fr); P = np.array([f["p"][:3] for f in Fr], float)
        cols = [P]
        if self.N == 4:
            sp = []
            for f in Fr:
                Rs = scap(f["p"][1], 0); p2 = Rs.T @ np.array(f["G"]["l2"]).reshape(3, 3)[:, 0]; sp.append(self.ch.spare_of(p2))
            sp = np.unwrap(np.array(sp)); cols.append(np.degrees(sp)[:, None])
        X = np.concatenate(cols, 1); d2 = np.abs(X[2:] - 2 * X[1:-1] + X[:-2]).max(1)
        knots = np.r_[0, 1 + np.nonzero(d2 > 0.03)[0], n - 1]; knots = np.unique(knots)
        fx = PchipInterpolator(knots, X[knots], axis=0)
        held = np.array([bool(f.get("held")) for f in Fr])
        return dict(name=c["name"], n=n, fps=float(c.get("fps", 30.0)), f=fx, df=fx.derivative(), held=held, P=np.array([f["p"] for f in Fr], float), knots=len(knots))

    def ik_check(self):
        """max angle (deg) between this judge's chain frames and the clip's G, per group, over every frame"""
        worst = {g: 0.0 for g in self.groups[1:]}
        for c in self.clips:
            Fr = c["frames"]; P = np.array([f["p"] for f in Fr]); Rs = scap(P[:, 1], 0); H = humerus(P); HG = np.transpose(Rs, (0, 2, 1)) @ H
            q = None
            if self.N == 4: q = np.array([self.ch.spare_of(Rs[i].T @ np.array(f["G"]["l2"]).reshape(3, 3)[:, 0]) for i, f in enumerate(Fr)])
            pins, ok = self.ch.pins(HG, q); Fm = self.ch.frames(pins)
            for k, g in enumerate(self.groups[1:]):
                G = np.array([np.array(f["G"][g]).reshape(3, 3) for f in Fr]); E = np.transpose(Rs @ Fm[k], (0, 2, 1)) @ G
                worst[g] = max(worst[g], float(np.degrees(np.linalg.norm(rotvec(E), axis=1)).max()))
        return {g: round(v, 3) for g, v in worst.items()}

# ---------------------------------------------------------------- MuJoCo model
def option_xml(dt=DT, gravity=True):
    """solver options shared by the judge and its tests: noslip + stiff friction impedance make frictionloss exact
    Coulomb (MuJoCo's default soft friction behaves like a viscous damper at low speed: 0.001 of the set torque at 0.01 rad/s)"""
    return (f'<option timestep="{dt}" gravity="0 {-9.81 if gravity else 0} 0" integrator="implicitfast" solver="Newton" iterations="60" tolerance="1e-10" '
            f'noslip_iterations="20"><flag filterparent="disable"/></option><default><joint solreffriction="0.0004 1" solimpfriction="0.99 0.999 0.0001"/></default>')

def load_friction_update(m, d, child, jid, dofs, r_brg, root, tau0, mu, tilt_out=None):
    """plain-bearing friction: each hinge's frictionloss = tau0 + mu |M_perp| (the parent-on-child reaction moment about
    the bearing centre r_brg (m) on the joint axis, perpendicular to the axis); call after mj_step"""
    import mujoco
    mujoco.mj_rnePostConstraint(m, d); cc_ = d.subtree_com[root]
    for k in range(len(jid)):
        w_ = d.cfrc_int[child[k]]; u = d.xaxis[jid[k]]; rb = r_brg[k]
        a0, a1, a2 = cc_[0] - rb * u[0], cc_[1] - rb * u[1], cc_[2] - rb * u[2]
        m0 = w_[0] + a1 * w_[5] - a2 * w_[4]; m1 = w_[1] + a2 * w_[3] - a0 * w_[5]; m2 = w_[2] + a0 * w_[4] - a1 * w_[3]
        ma = m0 * u[0] + m1 * u[1] + m2 * u[2]; tp = math.sqrt(max(0.0, m0 * m0 + m1 * m1 + m2 * m2 - ma * ma))
        if tilt_out is not None: tilt_out[k] = tp
        m.dof_frictionloss[dofs[k]] = tau0 + mu * tp

def quat(R):
    import mujoco
    q = np.zeros(4); mujoco.mju_mat2Quat(q, np.asarray(R, float).ravel()); return q

MEMBERS = None
def members(des): return des.groups + ["cuff"]                                  # member index m: base 0, l1..l(N-1), cuff N; joint J(m, m+1) = m + 1

def geom_table(des):
    """[(name, member index, kind, J, p0 mm, p1 mm, radius mm, near-joint set)] for every contact primitive; near = the
    ribbon's midpoint within hub_r + half width + 1 mm of one of its member's joint axes (the hub-side ribbon root)"""
    out = []
    for mi, g in enumerate(members(des)):
        hubs = [(JJ, unit(np.asarray(q1, float)), rr) for kd, JJ, q0, q1, rr in des.prims.get(g, []) if kd == "hub"]
        for i, (kind, J, p0, p1, rad) in enumerate(des.prims.get(g, [])):
            mid = 0.5 * (np.asarray(p0) + np.asarray(p1))
            near = {JJ for JJ, u, rr in hubs if np.linalg.norm(mid - (mid @ u) * u) < rr + HW + 1.0} if kind == "rib" else set()
            out.append((f"{g}_{i}", mi, kind, J, np.asarray(p0, float), np.asarray(p1, float), rad, near))
    return out

def designed_bearing(a, b):
    """True for the pairs that are the joint itself at a shared joint J: hub on hub, hub on the other member's hub-side
    ribbon root (band_impl.collisions' exemptions)"""
    (_, ma, ka, Ja, *_, na), (_, mb, kb, Jb, *_, nb) = a, b
    J = max(ma, mb)                                                             # the joint between members m and m+1 is J = m + 1
    if abs(ma - mb) != 1: return False
    hub_a = ka == "hub" and Ja == J; hub_b = kb == "hub" and Jb == J
    return (hub_a and hub_b) or (hub_a and J in nb) or (hub_b and J in na)

def build_xml(des, friction, armature, R0, tissue_scale=1.0, gravity=True, contacts=True, dt=DT, servo=False, pairs=()):
    """R0: reference rotations at qpos = 0 {'l1'..: link frame in the scapula frame, 'cuff': HG}. Contact: members that
    are not adjacent collide automatically (member bits); adjacent members only through the explicit `pairs`
    [(geom name, geom name)] (judge: candidates from a full joint-angle sweep, minus the designed bearing, minus pairs
    that already interpenetrate on the clip's planned path)."""
    N = des.N; fmt = lambda v: " ".join(f"{x:.9g}" for x in np.ravel(v))
    ALL = (1 << (N + 1)) - 1; D = lambda m_: (1 << m_) if 0 <= m_ <= N else 0
    tab = {}
    for row in geom_table(des): tab.setdefault(row[1], []).append(row)
    attrs = f'condim="3" friction="{MU_CONTACT} 0.005 0.0001" margin="0" gap="0.001" solref="0.004 1"'
    def geoms(mi):
        out = []
        for name, _, kind, J, p0, p1, rad, _n in tab.get(mi, []):
            p0, p1 = p0 / 1000, p1 / 1000; rad = rad / 1000
            if np.linalg.norm(p1 - p0) < 1e-5: p1 = p0 + 1e-5 * unit(p0)
            typ = "cylinder" if kind == "hub" else "capsule"
            out.append(f'<geom name="{name}" type="{typ}" fromto="{fmt(p0)} {fmt(p1)}" size="{rad:.6g}" contype="{D(mi)}" conaffinity="{ALL & ~D(mi - 1) & ~D(mi + 1)}" {attrs} group="1"/>')
        return "\n".join(out) if contacts else ""
    def inertial(g):
        m, c, I, _ = des.mp[g]; I = 0.5 * (I + I.T)
        return f'<inertial pos="{fmt(c)}" mass="{max(m, 1e-4):.9g}" fullinertia="{I[0,0]:.9g} {I[1,1]:.9g} {I[2,2]:.9g} {I[0,1]:.9g} {I[0,2]:.9g} {I[1,2]:.9g}"/>'
    fl = (f'frictionloss="{friction:.6g}"' if friction > 0 else "")
    def arm_of(J): return armature if (not servo or J == 1) else 0.0
    body = [f'<body name="base"><joint name="scap" type="ball" armature="1000"/><inertial pos="0 0 0" mass="1" diaginertia="1e-3 1e-3 1e-3"/>{geoms(0)}']
    prev = np.eye(3)
    for k in range(1, N):
        g = f"l{k}"; Rr = prev.T @ R0[g]
        body.append(f'<body name="{g}" quat="{fmt(quat(Rr))}"><joint name="J{k}" type="hinge" axis="1 0 0" {fl} armature="{arm_of(k):.6g}"/>{inertial(g)}{geoms(k)}')
        prev = R0[g]
    Rr = prev.T @ R0["cuff"]; c = np.array([0, -CUFF_MM / 1000, 0])
    body.append(f'<body name="cuff" quat="{fmt(quat(Rr))}" gravcomp="1"><joint name="J{N}" type="hinge" axis="{fmt(des.ch.W)}" {fl} armature="{arm_of(N):.6g}"/>'
                f'<inertial pos="{fmt(c)}" mass="{CUFF_MASS}" diaginertia="2e-6 2e-6 2e-6"/>{geoms(N)}')
    pr = "".join(f'<pair geom1="{a}" geom2="{b}" {attrs.replace("condim", "condim")}/>' for a, b in pairs) if contacts else ""
    xml = f"""<mujoco model="{des.id}"><compiler angle="radian" autolimits="true"/>{option_xml(dt, gravity)}
<worldbody>{''.join(body)}{'</body>' * (N + 1)}</worldbody>{f'<contact>{pr}</contact>' if pr else ''}</mujoco>"""
    return xml

def adjacent_candidates(des, step_deg=3.0, near_mm=2.0):
    """geom pairs of adjacent members that come within near_mm at some angle of their shared joint (full-turn sweep;
    the relative pose of two adjacent members depends on that joint alone), minus the designed bearing pairs"""
    if getattr(des, "_cand", None) is not None: return des._cand
    import mujoco
    tr = des.clip_traj(0); X = tr["f"](np.array([0.0])); Rh = humerus(X[:, :3]); Rs = scap(X[:, 1]); HG = np.transpose(Rs, (0, 2, 1)) @ Rh
    pins0, _ = des.ch.pins(HG, None if des.N == 3 else np.radians(X[:, 3])); Fm0 = des.ch.frames(pins0)
    R0 = {f"l{k}": Fm0[k - 1][0] for k in range(1, des.N)}; R0["cuff"] = HG[0]
    m = mujoco.MjModel.from_xml_string(build_xml(des, 0.0, 0.0, R0)); d = mujoco.MjData(m); d.qpos[0:4] = quat(Rs[0])
    tab = geom_table(des); gid = {r[0]: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, r[0]) for r in tab}
    by = {}
    for r in tab: by.setdefault(r[1], []).append(r)
    cand, ft = [], np.zeros(6)
    for mi in range(des.N):
        P = [(a, b) for a in by.get(mi, []) for b in by.get(mi + 1, []) if not designed_bearing(a, b)]
        if not P: continue
        qa = m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"J{mi + 1}")]; best = np.full(len(P), np.inf)
        for th in np.radians(np.arange(0, 360, step_deg)):
            d.qpos[qa] = th; mujoco.mj_kinematics(m, d)
            for k, (a, b) in enumerate(P):
                if best[k] > -1: best[k] = min(best[k], mujoco.mj_geomDistance(m, d, gid[a[0]], gid[b[0]], near_mm / 1000, ft))
        cand += [(a[0], b[0]) for (a, b), x in zip(P, best) if x < near_mm / 1000]
        d.qpos[qa] = 0.0
    des._cand = cand; return cand

def planned(des, tr, s, R0):
    """the evaluator's configuration along path frames s: (joint angles (n, N) relative to the reference R0, closure ok,
    humerus frames, scapula frames)"""
    N = des.N; Xr = tr["f"](s); Rh_r = humerus(Xr[:, :3]); Rs_r = scap(Xr[:, 1]); HG_r = np.transpose(Rs_r, (0, 2, 1)) @ Rh_r
    pins_r, ok_r = des.ch.pins(HG_r, None if N == 3 else np.radians(Xr[:, 3])); Fm_r = des.ch.frames(pins_r)
    chainR = [np.broadcast_to(np.eye(3), Fm_r[0].shape)] + Fm_r + [HG_r]; refR = [np.eye(3)] + [R0[f"l{k}"] for k in range(1, N)] + [R0["cuff"]]
    axes_loc = [np.array([1.0, 0, 0])] * (N - 1) + [des.ch.W]; qp = []
    for k in range(1, N + 1):
        Roff = refR[k - 1].T @ refR[k]; Rrel = np.transpose(chainR[k - 1], (0, 2, 1)) @ chainR[k]
        qp.append(np.unwrap(angle_about(Roff.T @ Rrel, axes_loc[k - 1])))
    return np.stack(qp, 1), ok_r, Rh_r, Rs_r

def planned_overlaps(des, tr, R0, pairs, every=3):
    """candidate pairs that already interpenetrate on this clip's planned path (sampled every `every` clip frames):
    {(a, b): deepest mm} - the L1 geometry / primitives overlap by design there (R6's domain)"""
    import mujoco
    if not pairs: return {}
    m = mujoco.MjModel.from_xml_string(build_xml(des, 0.0, 0.0, R0)); d = mujoco.MjData(m); ft = np.zeros(6)
    sv = np.arange(0, tr["n"], every, dtype=float); qp, ok, _, Rs_r = planned(des, tr, sv, R0)
    jq = [m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"J{k}")] for k in range(1, des.N + 1)]
    gid = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, n) for ab in pairs for n in ab}; out = {}
    for i in range(len(sv)):
        d.qpos[0:4] = quat(Rs_r[i])
        for k, a in enumerate(jq): d.qpos[a] = qp[i, k]
        mujoco.mj_kinematics(m, d)
        for a, b in pairs:
            x = mujoco.mj_geomDistance(m, d, gid[a], gid[b], 0.0, ft)
            if x < -1e-5: out[(a, b)] = min(out.get((a, b), 0.0), x * 1000)
    return out

# ---------------------------------------------------------------- one run
def run(des, ci, friction=0.2, speed=1.0, case="passive", gravity=True, tissue_scale=1.0, contacts=True, dt=DT, traj=None, record=False,
        mu_eff=None, tau0=TAU0, tilt="hub"):
    """simulate clip ci; returns (summary dict, recorded series dict if record).
    friction: constant Coulomb torque per joint (N.m). mu_eff (not None): load-dependent plain-bearing friction instead
    (red team G6, pipeline/redteam/rt_wedge.py): every step each hinge's frictionloss = tau0 + mu_eff |M_perp|, M_perp =
    the joint's reaction moment perpendicular to its axis (cfrc_int after mj_rnePostConstraint, one step behind), taken
    about the bearing centre (tilt="hub": the hub stack's mid-height on the axis, so the pin carries the force) or about
    the GH centre (tilt="gh": rt_wedge.py's model, no R x F term)."""
    import mujoco
    N = des.N; tr = traj or des.clip_traj(ci); fps = tr["fps"]; nf = tr["n"]
    T = SETTLE + (nf - 1) / fps / speed; nsteps = int(round(T / dt)) + 1; t = np.arange(nsteps) * dt
    s = np.clip((t - SETTLE) * speed * fps, 0, nf - 1)
    X = tr["f"](s); pose = X[:, :3]; Rh = humerus(pose); Rs = scap(pose[:, 1])
    def omega(R):
        dR = np.gradient(R, dt, axis=0); return vee(dR @ np.transpose(R, (0, 2, 1)))
    wh, ws = omega(Rh), omega(Rs); als = np.gradient(ws, dt, axis=0)
    sp = np.radians(X[:, 3]) if N == 4 else None
    HG = np.transpose(Rs, (0, 2, 1)) @ Rh
    # reference (planned) configuration at t = 0
    pins0, _ = des.ch.pins(HG[:1], None if sp is None else sp[:1]); Fm0 = des.ch.frames(pins0)
    R0 = {f"l{k}": Fm0[k - 1][0] for k in range(1, N)}; R0["cuff"] = HG[0]
    servo = case == "servo"; arm = ARM_MOTOR if case in ("motor", "servo") else 0.0
    load = mu_eff is not None; f_xml = tau0 if load else friction
    cand = adjacent_candidates(des) if contacts else []; pov = planned_overlaps(des, tr, R0, cand) if contacts else {}
    pairs = [ab for ab in cand if ab not in pov]
    m = mujoco.MjModel.from_xml_string(build_xml(des, f_xml, arm, R0, tissue_scale, gravity, contacts, dt, servo, pairs)); d = mujoco.MjData(m)
    if load and f_xml <= 0: raise ValueError("load-dependent friction needs tau0 > 0 (frictionloss rows must exist)")
    jid = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"J{k}") for k in range(1, N + 1)]
    qa = [m.jnt_qposadr[j] for j in jid]; va = [m.jnt_dofadr[j] for j in jid]; bq, bv = m.jnt_qposadr[0], m.jnt_dofadr[0]
    cuff = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "cuff"); base = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base")
    child = [m.jnt_bodyid[j] for j in jid]; root = int(m.body_rootid[child[0]])
    r_brg = [0.0 if tilt == "gh" else des.bearing_r[k] / 1000 for k in range(1, N + 1)]; tilt_now = [0.0] * N
    body_member = {mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, g): g for g in des.groups + ["cuff"]}
    d.qpos[bq:bq + 4] = quat(Rs[0]); mujoco.mj_forward(m, d)
    Ts = TISSUE; ks = tissue_scale
    Kt = ks * np.array([Ts["k_perp"], Ts["k_ax"], Ts["k_perp"]]); Kr = ks * np.array([Ts["kr_perp"], Ts["kr_ax"], Ts["kr_perp"]])
    ct, cr = math.sqrt(ks) * Ts["c_t"], math.sqrt(ks) * np.array([Ts["cr_perp"], Ts["cr_ax"], Ts["cr_perp"]])
    cl = np.array([0, -CUFF_MM / 1000, 0]); A_b = 1000.0; kp_b, kd_b = (2 * math.pi * 30) ** 2, 2 * 2 * math.pi * 30
    if servo:
        q1p = sp - sp[0]; dq1p = np.gradient(q1p, dt); ddq1p = np.gradient(dq1p, dt); m1, c1, I1, _ = des.mp["l1"]; Im = arm + float(I1[0, 0] + m1 * (c1[1] ** 2 + c1[2] ** 2))   # J1 inertia about its axis
        kp_s, kd_s = Im * SERVO_WN ** 2, 2 * Im * SERVO_WN
    rec = {k: [] for k in ("t", "s", "F", "M", "Mgh", "q", "qd", "ax", "track", "con", "gap", "servo", "fric", "tilt", "cap")}
    # per-step data as python floats (the loop below is scalar maths: numpy on 3-vectors costs ~10x more)
    Rs_l = Rs.reshape(-1, 9).tolist(); Rh_l = Rh.reshape(-1, 9).tolist(); wh_l = wh.tolist()
    wloc_l = np.einsum("nji,nj->ni", Rs, ws).tolist(); aloc_l = np.einsum("nji,nj->ni", Rs, als).tolist()
    pb_a = Rh @ cl; pb_l = pb_a.tolist(); vb_l = np.cross(wh, pb_a).tolist()
    kt0, kt1, kt2 = Kt.tolist(); kr0, kr1, kr2 = Kr.tolist(); cr0, cr1, cr2 = cr.tolist(); dc = CUFF_MM / 1000
    res6 = np.zeros(6); cf = np.zeros(6); FR = mujoco.mjtConstraint.mjCNSTR_FRICTION_DOF; XB = mujoco.mjtObj.mjOBJ_XBODY
    qfa, xfr, xm, xp, xi, qv = d.qfrc_applied, d.xfrc_applied, d.xmat, d.xpos, d.xipos, d.qvel; tau_s = 0.0
    for i in range(nsteps):
        # base: prescribed scapula motion (feed-forward + PD on a huge armature; error = small-angle vee(Rb^T Rs))
        b = xm[base]; S_ = Rs_l[i]
        e0 = 0.5 * ((b[2] * S_[1] + b[5] * S_[4] + b[8] * S_[7]) - (b[1] * S_[2] + b[4] * S_[5] + b[7] * S_[8]))
        e1 = 0.5 * ((b[0] * S_[2] + b[3] * S_[5] + b[6] * S_[8]) - (b[2] * S_[0] + b[5] * S_[3] + b[8] * S_[6]))
        e2 = 0.5 * ((b[1] * S_[0] + b[4] * S_[3] + b[7] * S_[6]) - (b[0] * S_[1] + b[3] * S_[4] + b[6] * S_[7]))
        wl, al = wloc_l[i], aloc_l[i]
        qfa[bv] = A_b * (al[0] + kp_b * e0 + kd_b * (wl[0] - qv[bv])); qfa[bv + 1] = A_b * (al[1] + kp_b * e1 + kd_b * (wl[1] - qv[bv + 1]))
        qfa[bv + 2] = A_b * (al[2] + kp_b * e2 + kd_b * (wl[2] - qv[bv + 2]))
        # tissue wrench on the cuff member: anisotropic spring-damper in the bone frame at the cuff point
        c = xm[cuff].tolist(); o = xp[cuff].tolist(); ip = xi[cuff].tolist(); B = Rh_l[i]; wb = wh_l[i]; pb = pb_l[i]; vb = vb_l[i]
        mujoco.mj_objectVelocity(m, d, XB, cuff, res6, 0); wc0, wc1, wc2, l0, l1, l2 = res6.tolist()
        pc0, pc1, pc2 = o[0] - dc * c[1], o[1] - dc * c[4], o[2] - dc * c[7]; r0, r1, r2 = pc0 - o[0], pc1 - o[1], pc2 - o[2]
        vc0, vc1, vc2 = l0 + wc1 * r2 - wc2 * r1, l1 + wc2 * r0 - wc0 * r2, l2 + wc0 * r1 - wc1 * r0
        dp0, dp1, dp2 = pc0 - pb[0], pc1 - pb[1], pc2 - pb[2]
        fb0 = -kt0 * (B[0] * dp0 + B[3] * dp1 + B[6] * dp2); fb1 = -kt1 * (B[1] * dp0 + B[4] * dp1 + B[7] * dp2); fb2 = -kt2 * (B[2] * dp0 + B[5] * dp1 + B[8] * dp2)
        F0 = B[0] * fb0 + B[1] * fb1 + B[2] * fb2 - ct * (vc0 - vb[0]); F1 = B[3] * fb0 + B[4] * fb1 + B[5] * fb2 - ct * (vc1 - vb[1])
        F2 = B[6] * fb0 + B[7] * fb1 + B[8] * fb2 - ct * (vc2 - vb[2])
        E = [B[k] * c[j] + B[3 + k] * c[3 + j] + B[6 + k] * c[6 + j] for k in range(3) for j in range(3)]   # Rb^T Rc
        cs = max(-1.0, min(1.0, 0.5 * (E[0] + E[4] + E[8] - 1.0))); th = math.acos(cs); sn = math.sin(th); kk = th / sn if sn > 1e-9 else 1.0
        t0_, t1_, t2_ = 0.5 * kk * (E[7] - E[5]), 0.5 * kk * (E[2] - E[6]), 0.5 * kk * (E[3] - E[1])
        dw0, dw1, dw2 = wc0 - wb[0], wc1 - wb[1], wc2 - wb[2]
        mb0 = -kr0 * t0_ - cr0 * (B[0] * dw0 + B[3] * dw1 + B[6] * dw2); mb1 = -kr1 * t1_ - cr1 * (B[1] * dw0 + B[4] * dw1 + B[7] * dw2)
        mb2 = -kr2 * t2_ - cr2 * (B[2] * dw0 + B[5] * dw1 + B[8] * dw2)
        M0, M1, M2 = B[0] * mb0 + B[1] * mb1 + B[2] * mb2, B[3] * mb0 + B[4] * mb1 + B[5] * mb2, B[6] * mb0 + B[7] * mb1 + B[8] * mb2
        a0, a1, a2 = pc0 - ip[0], pc1 - ip[1], pc2 - ip[2]
        xfr[cuff] = (F0, F1, F2, M0 + a1 * F2 - a2 * F1, M1 + a2 * F0 - a0 * F2, M2 + a0 * F1 - a1 * F0)
        if servo:
            tau_s = Im * ddq1p[i] + kp_s * (q1p[i] - d.qpos[qa[0]]) + kd_s * (dq1p[i] - qv[va[0]]); qfa[va[0]] = tau_s
        if i % REC == 0:
            F = np.array([F0, F1, F2]); M = np.array([M0, M1, M2]); pc = np.array([pc0, pc1, pc2])
            rec["t"].append(t[i]); rec["s"].append(s[i]); rec["F"].append(F); rec["M"].append(M); rec["Mgh"].append(M + np.cross(pc, F))
            rec["q"].append([d.qpos[a] for a in qa]); rec["qd"].append([qv[a] for a in va]); rec["ax"].append(d.xaxis[jid].copy()); rec["track"].append((t0_, t1_, t2_))
            rec["servo"].append(tau_s)
            fr_ = np.zeros(N)
            for k in range(d.nefc):
                if d.efc_type[k] == FR and d.efc_id[k] in va: fr_[va.index(d.efc_id[k])] = d.efc_force[k]
            rec["fric"].append(fr_)
            fmax, gmin, pair = 0.0, np.inf, None
            for k in range(d.ncon):
                cc = d.contact[k]
                if cc.dist < gmin: gmin = cc.dist
                if cc.exclude == 0:
                    mujoco.mj_contactForce(m, d, k, cf)
                    if cf[0] > fmax: fmax, pair = cf[0], f"{body_member.get(m.geom_bodyid[cc.geom1])}-{body_member.get(m.geom_bodyid[cc.geom2])}"
            rec["con"].append((fmax, pair)); rec["gap"].append(gmin); rec["tilt"].append(list(tilt_now)); rec["cap"].append([m.dof_frictionloss[a] for a in va])
        mujoco.mj_step(m, d)
        if load: load_friction_update(m, d, child, jid, va, r_brg, root, tau0, mu_eff, tilt_now)   # plain bearing: friction grows with the tilt couple
        if i % 500 == 0 and not np.isfinite(d.qacc).all(): raise FloatingPointError(f"{des.id} clip {ci}: simulation diverged at t = {d.time:.3f} s")
    R = {k: (np.array(v) if k not in ("con",) else v) for k, v in rec.items()}
    R["fmax"] = np.array([c[0] for c in R["con"]]); R["pair"] = [c[1] for c in R["con"]]
    # planned configuration at the recorded samples
    sr = R["s"]; qp, ok_r, Rh_r, _ = planned(des, tr, sr, R0); R["qp"] = qp; R["ok"] = ok_r
    R["qdp"] = np.gradient(R["qp"], R["t"], axis=0)
    R["warm"] = R["t"] >= SETTLE; R["h"] = Rh_r @ np.array([0, -1.0, 0]); R["Rh"] = Rh_r
    wr = vee(np.gradient(Rh_r, R["t"], axis=0) @ np.transpose(Rh_r, (0, 2, 1))); R["warm_w"] = np.linalg.norm(wr, axis=1)
    R["frame"] = np.clip(np.round(sr).astype(int), 0, nf - 1); R["held"] = tr["held"][R["frame"]]
    summ = summarise(des, tr, R, friction if not load else tau0, speed, case)
    po = {}
    for (ga, gb), x in pov.items():
        k = f"{ga.rsplit('_', 1)[0]}-{gb.rsplit('_', 1)[0]}"; po[k] = round(min(po.get(k, 0.0), x), 2)
    summ["contact"]["planned_overlap_mm"] = po; summ["contact"]["adjacent_pairs_checked"] = len(pairs)
    if load: summ["load_friction"] = dict(mu_eff=mu_eff, tau0_Nm=tau0, tilt_ref=tilt, tilt_peak_Nm=[round(float(x), 3) for x in R["tilt"][R["warm"]].max(0)],
                                          friction_peak_Nm=[round(float(x), 3) for x in R["cap"][R["warm"]].max(0)])
    return summ, (R if record else None)

def amp_qs(U, s):
    """quasi-static moment per N.m of joint friction: U^T M = sgn(qdot) (least squares for N = 4, as transmission.py)"""
    return np.linalg.lstsq(U, s, rcond=None)[0]

def summarise(des, tr, R, friction, speed, case):
    N = des.N; w = R["warm"]; t = R["t"][w]; F = R["F"][w]; M = R["M"][w]; Mg = R["Mgh"][w]; h = R["h"][w]; th = R["track"][w]
    q, qd, qp, qdp = R["q"][w], R["qd"][w], R["qp"][w], R["qdp"][w]; fps = tr["fps"]
    Fn = np.linalg.norm(F, axis=1); Mn = np.linalg.norm(M, axis=1); Mgn = np.linalg.norm(Mg, axis=1); Max = np.abs((Mg * h).sum(1)); Mperp = np.sqrt(np.maximum(Mgn ** 2 - Max ** 2, 0))
    Mc_ax = np.abs((M * h).sum(1))
    tw = np.abs(th[:, 1]); sw = np.linalg.norm(th[:, [0, 2]], axis=1); tt = np.linalg.norm(th, axis=1)
    # joint rates: 5 ms moving average for accelerations
    dtr = float(np.median(np.diff(R["t"]))); k = max(1, int(round(0.005 / dtr)))
    qd_s = np.apply_along_axis(lambda x: np.convolve(x, np.ones(k) / k, mode="same"), 0, qd); qdd = np.gradient(qd_s, t, axis=0)
    warm_w = R["warm_w"][w]; mv = warm_w > math.radians(10)
    ratio = (np.abs(qd).max(1)[mv] / warm_w[mv]) if mv.any() else np.zeros(1)
    # stalls: a joint the arm drives (|planned rate| > 10 deg/s) moving backwards or stuck for > 50 ms
    stall_ev = []; thr = math.radians(10)
    for j in range(N):
        drive = np.abs(qdp[:, j]) > thr; rev = drive & (qd[:, j] * qdp[:, j] < 0); stuck = drive & (np.abs(qd[:, j]) < 0.2 * np.abs(qdp[:, j]))
        bad = rev | stuck; i = 0
        while i < len(bad):
            if bad[i]:
                j0 = i
                while i < len(bad) and bad[i]: i += 1
                dur = t[i - 1] - t[j0]
                if dur >= 0.05:
                    miss = abs(float(np.degrees((qp[i - 1, j] - q[i - 1, j]) - (qp[j0, j] - q[j0, j]))))
                    stall_ev.append(dict(joint=f"J{j + 1}", frame=int(R["frame"][w][j0]), ms=round(1000 * dur), missed_deg=round(miss, 1),
                                         kind=("lag>10" if miss >= LAG_DEG else "lag") + ("-reversal" if rev[j0:i].mean() > 0.5 else "-stuck")))
            i += 1
    fmax = R["fmax"][w]; pair = [p for p, ww in zip(R["pair"], w) if ww]; gap = R["gap"][w]
    touch = fmax > 1e-3; pairs = {}
    for p, f_ in zip(pair, fmax):
        if f_ > 1e-3: pairs[p] = max(pairs.get(p, 0.0), float(f_))
    # quasi-static friction amplification along the realised motion (realised axes, realised joint-rate signs)
    U = R["ax"][w]; sgn = np.sign(qd) * (np.abs(qd) > 1e-3); amp = np.array([np.linalg.norm(amp_qs(U[i], sgn[i])) for i in range(len(U))])
    cond = np.array([(lambda sv: sv[0] / max(sv[-1], 1e-9))(np.linalg.svd(U[i], compute_uv=False)) for i in range(len(U))])
    # worst frames: the 3 largest moments about GH, >= 0.3 s apart
    order = np.argsort(-Mgn); worst = []
    for i in order:
        if len(worst) >= 3: break
        if any(abs(t[i] - t[j]) < 0.3 for j in worst): continue
        worst.append(i)
    W = []
    for i in worst:
        fi = int(R["frame"][w][i])
        W.append(dict(frame=fi, t_s=round(float(t[i] - SETTLE), 3), pose=[round(float(x), 1) for x in tr["P"][fi][:4]], moment_gh_Nm=round(float(Mgn[i]), 3),
                      moment_gh_axial_Nm=round(float(Max[i]), 3), force_N=round(float(Fn[i]), 2), amp_qs=round(float(amp[i]), 2), friction_qs_Nm=round(float(amp[i] * friction), 3),
                      cond_U=round(float(cond[i]), 1), joint_speed_dps=[round(float(x), 1) for x in np.degrees(qd[i])], arm_speed_dps=round(float(np.degrees(warm_w[i])), 1),
                      twist_deg=round(float(np.degrees(tw[i])), 2)))
    rms = lambda x: float(np.sqrt(np.mean(x ** 2)))
    lockm = (Mgn > THRESH["lock_moment_gh_Nm"]) | (Fn > THRESH["iso_ts_15066_upper_arm_N"])     # the arm cannot reasonably drive it
    out = dict(duration_s=round(float(t[-1] - t[0]), 2), held_share=round(float(R["held"][w].mean()), 3),
               force_N=dict(peak=round(float(Fn.max()), 2), rms=round(rms(Fn), 2)),
               cuff_pressure_kPa=dict(peak=round(float(Fn.max()) / CUFF_AREA_CM2 * 10, 3), rms=round(rms(Fn) / CUFF_AREA_CM2 * 10, 3),
                                      axial_shear_peak=round(float(Mc_ax.max()) / (0.063 * CUFF_AREA_CM2 * 1e-4) / 1000, 3)),
               moment_cuff_Nm=dict(peak=round(float(Mn.max()), 3), rms=round(rms(Mn), 3), axial_peak=round(float(Mc_ax.max()), 3)),
               moment_gh_Nm=dict(peak=round(float(Mgn.max()), 3), rms=round(rms(Mgn), 3), perp_peak=round(float(Mperp.max()), 3), axial_peak=round(float(Max.max()), 3)),
               joint_speed_dps=[round(float(x), 1) for x in np.degrees(np.abs(qd).max(0))], arm_speed_dps=round(float(np.degrees(warm_w.max())), 1),
               speed_ratio_max=round(float(ratio.max()), 2), joint_acc_dps2=[round(float(x)) for x in np.degrees(np.abs(qdd).max(0))],
               tracking_deg=dict(peak=round(float(np.degrees(tt.max())), 2), rms=round(float(np.degrees(rms(tt))), 2), twist_peak=round(float(np.degrees(tw.max())), 2), swing_peak=round(float(np.degrees(sw.max())), 2)),
               config_dev_deg=[round(float(x), 2) for x in np.degrees(np.abs(q - qp).max(0))],
               amp_qs=dict(p95=round(float(np.percentile(amp, 95)), 2), max=round(float(amp.max()), 2)), cond_U_max=round(float(cond.max()), 1),
               stalls=dict(events=len(stall_ev), lags_over_10deg=sum(e["kind"].startswith("lag>10") for e in stall_ev), worst_ms=max([e["ms"] for e in stall_ev], default=0),
                           worst_missed_deg=max([e["missed_deg"] for e in stall_ev], default=0.0), list=sorted(stall_ev, key=lambda e: -e["missed_deg"])[:10]),
               drive=dict(frames_over_felt=round(float((Mgn > THRESH["free_moment_gh_peak_Nm"]).mean()), 3), frames_over_lock=round(float(lockm.mean()), 3),
                          first_lock_frame=(int(R["frame"][w][np.argmax(lockm)]) if lockm.any() else None), drives=bool(not lockm.any())),
               contact=dict(touch=bool(touch.any()), peak_N=round(float(fmax.max()), 3), time_s=round(float(touch.sum() * np.median(np.diff(t))), 3), pairs={k: round(v, 3) for k, v in pairs.items()},
                            min_gap_mm=round(float(gap.min() * 1000), 2) if np.isfinite(gap.min()) else None),
               worst=W)
    if N == 4: out["spare_drift_deg"] = round(float(np.degrees(np.abs(q[:, 0] - qp[:, 0]).max())), 2)
    if case == "servo": out["servo_peak_Nm"] = round(float(np.abs(R["servo"][w]).max()), 3)
    return out

# ---------------------------------------------------------------- validation against transmission.py (quasi-static, ideal joints)
def validate(des, clips=None, friction=0.05, speed=0.25, tissue_scale=20.0, dt=1e-4, log=print, jobs=1):
    """quasi-static check of the dynamics model: slow motion (x speed), no gravity, stiff cuff, contacts off, so the
    moment the arm applies about GH is joint friction only. N = 3: |M_GH| / friction vs transmission.py's friction
    amplification on its own 10 fps frames (band_poses.b64; clip frame = 3 x its frame index). N = 4: the spare J1 is
    servoed on the plan, the reference is the exact quasi-static moment of the 3 passive joints (U_p^-T sgn(qdot)) on the
    realised axes; transmission.py's least-squares number (4 joints) is reported alongside when the evaluator path exists.
    Frames within 0.15 s (path time) of a joint-rate sign change, with a joint at < 5 % of the fastest joint's rate, or
    held, are excluded: friction there is set-valued."""
    sys.path.insert(0, os.path.join(PIPE, "conformal", "analysis")); import transmission as TM
    P = TM.poses(); d = dict(des.kin, n=des.N); cfg = None; have_tm = des.N == 3
    if des.N == 4:
        src = os.path.join(PIPE, "conformal", "analysis", "designs_transmission.json")
        DT_ = json.load(open(src)) if os.path.exists(src) else []
        for x in (DT_["designs"] if isinstance(DT_, dict) else DT_):
            if x.get("_eval") and abs(x["az"] - des.kin["az"]) < 1e-6:
                f, i = x["_eval"]; cfg = json.load(open(os.path.join(PIPE, "conformal", f)))["results"][i]["cfg"]; d["q_step"] = x.get("q_step", 12); have_tm = True
    U_tm, ok_tm = TM.axes(P, d, cfg) if have_tm else (None, None); names = [str(x) for x in P["NAMES"]]; cid, fi = P["CID"], P["FI"]
    case = "passive" if des.N == 3 else "servo"; todo = [ci for ci, c in enumerate(des.clips) if clips is None or c["name"] in clips]
    kw = dict(friction=friction, speed=speed, case=case, gravity=False, tissue_scale=tissue_scale, contacts=False, dt=dt, record=True)
    global DES; DES = des
    with (mp.get_context("fork").Pool(min(jobs, len(todo))) if jobs > 1 else contextlib.nullcontext()) as pool:
        runs = dict(zip(todo, (pool.map if pool else map)(_vtask, [(ci, kw) for ci in todo])))
    rows = []
    for ci in todo:
        c = des.clips[ci]; R = runs[ci]; s = R["s"]; Mg = R["Mgh"]; qd = R["qd"]; U = R["ax"]; tt = R["t"]
        chg = np.zeros(len(s), bool); pj = list(range(des.N)) if des.N == 3 else list(range(1, des.N))   # N = 4: J1 is servoed, only J2..JN slide
        for j in pj:
            for x in np.nonzero(np.diff(np.sign(qd[:, j])) != 0)[0]: chg |= np.abs(tt - tt[x]) < 0.15 / speed
        k = names.index(c["name"]); idx = np.nonzero(cid == k)[0]; idx = idx[np.argsort(fi[idx])]
        w = TM.omega(P["HG"][idx], 10.0); w[0], w[-1] = w[1], w[-2]
        for j_, f_ in enumerate(idx):
            fr = 3 * int(fi[f_])
            if fr <= 0 or fr >= len(c["frames"]) - 1 or c["frames"][fr].get("held"): continue
            i = int(np.argmin(np.abs(s - fr)))
            if not R["warm"][i] or chg[i] or np.abs(qd[i][pj]).min() < 0.05 * np.abs(qd[i][pj]).max(): continue
            row = dict(clip=c["name"], frame=fr, amp_dynamics=round(float(np.linalg.norm(Mg[i]) / friction), 4))
            if have_tm and ok_tm[f_]:
                A = U_tm[f_].T; qdm = np.linalg.lstsq(A, w[j_], rcond=None)[0]; s_tm = np.sign(qdm)
                row["amp_transmission"] = round(float(np.linalg.norm(np.linalg.lstsq(A.T, s_tm, rcond=None)[0])), 4)
                row["same_signs"] = bool((np.sign(qd[i]) == s_tm).all()) if des.N == 3 else bool((np.sign(qd[i][1:]) == s_tm[1:]).all())
            if des.N == 4: row["amp_exact_servo"] = round(float(np.linalg.norm(np.linalg.solve(U[i][1:], np.sign(qd[i][1:])))), 4)
            rows.append(row)
    if not rows: return dict(ok=None, note="no comparable frames")
    ref = "amp_transmission" if des.N == 3 else "amp_exact_servo"
    use = [r for r in rows if ref in r and (des.N == 4 or r.get("same_signs", True))]       # N = 4: the exact reference uses the realised signs
    err = np.array([abs(r["amp_dynamics"] / r[ref] - 1) for r in use]) if use else np.array([np.nan])
    out = dict(method=f"speed x{speed}, gravity off, cuff stiffness x{tissue_scale}, friction {friction} N.m on every joint, contacts off, dt {dt}; |M_GH| / friction vs "
                      + ("transmission.py's amplification on its 10 fps frames" if des.N == 3 else "the exact quasi-static moment with J1 servoed (3 passive joints)"),
               reference=ref, frames_compared=len(use), frames_excluded_sign_mismatch=(len([r for r in rows if not r.get("same_signs", True)]) if des.N == 3 else 0),
               rel_err_median=round(float(np.median(err)), 4), rel_err_p95=round(float(np.percentile(err, 95)), 4), rel_err_max=round(float(np.max(err)), 4),
               ok=bool(np.percentile(err, 95) < 0.03), rows=rows)
    if des.N == 4 and have_tm:
        tm = [r for r in rows if "amp_transmission" in r]
        e2 = np.array([r["amp_exact_servo"] / r["amp_transmission"] - 1 for r in tm])
        out["transmission_lstsq_vs_exact_servo"] = dict(frames=len(tm), rel_diff_median=round(float(np.median(e2)), 3), rel_diff_min=round(float(e2.min()), 3), rel_diff_max=round(float(e2.max()), 3),
                                                        note="transmission.py's N = 4 number is a least-squares moment over all 4 joints (no exact equilibrium exists when all 4 slide); "
                                                             "the physical one depends on which joint is driven or sticks")
    return out

_SPH = None
def alpha_star(U, s):
    """rt_wedge.py's best worst action angle (deg) over the moving joints (same algorithm: 4000 seeded directions, then
    Nelder-Mead); the chain self-locks under tau_f = mu_eff |M_perp| iff tan(alpha*) <= mu_eff"""
    from scipy.optimize import minimize
    global _SPH
    if _SPH is None: _SPH = np.random.default_rng(0).normal(size=(4000, 3)); _SPH /= np.linalg.norm(_SPH, axis=1, keepdims=True)
    mv = s != 0
    if not mv.any(): return 90.0
    V = U[mv] * s[mv, None]; m0 = _SPH[np.argmax((_SPH @ V.T).min(1))]
    r = minimize(lambda x: -np.min(V @ (x / np.linalg.norm(x))), m0, method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-7, maxiter=400))
    return math.degrees(math.asin(np.clip(-r.fun, -1, 1)))

def qs_load_moment(U, s, mu, tau0):
    """quasi-static moment about GH that drives a 3R chain whose joints i slide with sign s_i under
    tau_f,i = tau0 + mu |M_perp,i| (M_perp about GH): solves u_i.M = s_i (tau0 + mu |M - (u_i.M) u_i|); None if locked"""
    from scipy.optimize import fsolve
    def f(M): return U @ M - s * (tau0 + mu * np.sqrt(np.maximum(M @ M - (U @ M) ** 2, 0)))
    M, _, ier, _ = fsolve(f, np.linalg.solve(U, s * tau0), full_output=True)
    return M if ier == 1 and np.abs(f(M)).max() < 1e-7 and (np.sign(U @ M) == s).all() else None

def validate_wedge(des, mus=(0.005, 0.15, 0.25, 0.37), tau0=TAU0, speed=0.25, tissue_scale=20.0, dt=1e-4, jobs=1, log=print, clips=None):
    """the load-dependent friction against rt_wedge.py's quasi-static wedge model, on transmission.py's 10 fps frames
    (N = 3 only: rt_wedge's 4R moves all four joints on the evaluator's path, a passive 4R does not). Slow, no gravity,
    stiff cuff, tilt about GH (rt_wedge's model). (a) frames well clear of a lock (tan alpha* >= 1.2 mu, no joint-rate
    sign change within 0.15 s, not within 1 s after a locked frame): |M_GH| vs the exact quasi-static solution;
    (b) frames rt_wedge.py calls locked (tan alpha* <= mu): the moment the arm needs vs the frame's constant-friction
    moment (tau0 x amplification) - a lock shows as a jump of an order of magnitude or more; (c) per clip, the first locked
    frame vs the first frame the dynamics needs > 10x that moment."""
    if des.N != 3: return dict(ok=None, note="N = 4: rt_wedge.py's 4R number assumes all four joints slide on the evaluator's path; a passive 4R picks its own (see the passive / servo runs)")
    sys.path.insert(0, os.path.join(PIPE, "conformal", "analysis")); import transmission as TM
    P = TM.poses(); U_tm, ok_tm = TM.axes(P, dict(des.kin, n=3)); names = [str(x) for x in P["NAMES"]]; cid, fi = P["CID"], P["FI"]
    todo = [ci for ci, c in enumerate(des.clips) if clips is None or c["name"] in clips]; global DES; DES = des
    pre = {}                                                                           # per clip: frames, signs, alpha*, constant-friction moment
    for ci in todo:
        c = des.clips[ci]; k = names.index(c["name"]); idx = np.nonzero(cid == k)[0]; idx = idx[np.argsort(fi[idx])]
        w = TM.omega(P["HG"][idx], 10.0); w[0], w[-1] = w[1], w[-2]; rows = []
        for j_, f_ in enumerate(idx):
            fr = 3 * int(fi[f_])
            if fr <= 0 or fr >= len(c["frames"]) - 1 or c["frames"][fr].get("held") or not ok_tm[f_] or np.linalg.norm(w[j_]) < 1e-3: continue
            A = U_tm[f_].T; qd = np.linalg.lstsq(A, w[j_], rcond=None)[0]; sg = np.sign(qd)
            if np.abs(qd).min() < 0.05 * np.abs(qd).max(): continue
            rows.append(dict(frame=fr, U=U_tm[f_], s=sg, tan_a=math.tan(math.radians(alpha_star(U_tm[f_], sg))), m_const=float(np.linalg.norm(np.linalg.solve(U_tm[f_], sg * tau0)))))
        pre[ci] = rows
    items = [(ci, dict(speed=speed, case="passive", gravity=False, tissue_scale=tissue_scale, contacts=False, dt=dt, record=True, mu_eff=mu, tau0=tau0, tilt="gh")) for mu in mus for ci in todo]
    with (mp.get_context("fork").Pool(min(jobs, len(items))) if jobs > 1 else contextlib.nullcontext()) as pool:
        runs = list((pool.map if pool else map)(_vtask, items))
    A_err, B_ratio, onset, out_rows = [], [], [], []
    for (ci, kw), R in zip(items, runs):
        mu = kw["mu_eff"]; c = des.clips[ci]; s_ = R["s"]; tt = R["t"]; qd = R["qd"]; chg = np.zeros(len(s_), bool)
        for j in range(3):
            for x in np.nonzero(np.diff(np.sign(qd[:, j])) != 0)[0]: chg |= np.abs(tt - tt[x]) < 0.15 / speed
        locked = [r["frame"] for r in pre[ci] if r["tan_a"] <= mu]; first_pred = min(locked) if locked else None; first_dyn = None
        for r in pre[ci]:
            i = int(np.argmin(np.abs(s_ - r["frame"]))); Md = float(np.linalg.norm(R["Mgh"][i]))
            if first_dyn is None and Md > 10 * r["m_const"]: first_dyn = r["frame"]
            if r["tan_a"] <= mu: B_ratio.append(Md / r["m_const"]); out_rows.append(dict(clip=c["name"], mu=mu, frame=r["frame"], tan_alpha=round(r["tan_a"], 3), locked=True, m_dyn=round(Md, 3), m_const=round(r["m_const"], 4)))
            elif r["tan_a"] >= 1.2 * mu and not chg[i] and not any(0 < r["frame"] - f <= 30 for f in locked) and (np.sign(qd[i]) == r["s"]).all():
                Mq = qs_load_moment(r["U"], r["s"], mu, tau0)
                if Mq is None: continue
                A_err.append(abs(Md / np.linalg.norm(Mq) - 1)); out_rows.append(dict(clip=c["name"], mu=mu, frame=r["frame"], tan_alpha=round(r["tan_a"], 3), locked=False, m_dyn=round(Md, 4), m_qs=round(float(np.linalg.norm(Mq)), 4)))
        if first_pred is not None or first_dyn is not None: onset.append(dict(clip=c["name"], mu=mu, first_locked_frame_rt_wedge=first_pred, first_frame_dyn_over_10x=first_dyn))
        log(f"  wedge validation mu {mu}: {c['name']}")
    A_err = np.array(A_err) if A_err else np.array([np.nan]); B = np.array(B_ratio) if B_ratio else np.array([np.nan])
    on_ok = [o for o in onset if o["first_locked_frame_rt_wedge"] is not None and o["first_frame_dyn_over_10x"] is not None and abs(o["first_locked_frame_rt_wedge"] - o["first_frame_dyn_over_10x"]) <= 6]
    return dict(method=f"speed x{speed}, gravity off, cuff x{tissue_scale}, tau0 {tau0} N.m, tilt about GH (rt_wedge.py's model), mu_eff {list(mus)}, dt {dt}",
                unlocked_frames=int(np.isfinite(A_err).sum()), unlocked_rel_err_median=round(float(np.nanmedian(A_err)), 4), unlocked_rel_err_p95=round(float(np.nanpercentile(A_err, 95)), 4),
                locked_frames=int(np.isfinite(B).sum()), locked_moment_over_constant_friction=dict(min=round(float(np.nanmin(B)), 1), median=round(float(np.nanmedian(B)), 1)),
                onset=onset, onset_agree_within_0p2s=f"{len(on_ok)}/{len(onset)}",
                ok=bool(np.nanpercentile(A_err, 95) < 0.05 and (not np.isfinite(B).any() or np.nanmedian(B) >= 10)), rows=out_rows)

def _vtask(item):
    ci, kw = item; return run(DES, ci, **kw)[1]

# ---------------------------------------------------------------- driver
DES = None
def _task(item):
    key, ci, kw = item
    try: return key, ci, run(DES, ci, **kw)[0], None
    except Exception as e: return key, ci, None, f"{type(e).__name__}: {e}"

def case_key(f, s, c): return f"{c}|f{f:g}|s{s:g}"
def load_key(mu, tau0, s, c, tilt): return f"{c}|mu{mu:g}|t{tau0:g}|s{s:g}|{tilt}"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("design")
    ap.add_argument("--friction", default=",".join(f"{x:g}" for x in FRICTIONS), help="constant Coulomb torques per joint, N.m ('' = off)")
    ap.add_argument("--speed", default=",".join(f"{x:g}" for x in SPEEDS))
    ap.add_argument("--cases", default="passive", help="passive (MVP1: unpowered); motor / servo kept as options")
    ap.add_argument("--clips", default=None); ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--mu_roll", default=",".join(f"{x:g}" for x in MU_ROLL), help="rolling bearings, load-dependent (main case); '' = off")
    ap.add_argument("--tau0_roll", type=float, default=TAU0_ROLL)
    ap.add_argument("--mu_eff", default=",".join(f"{x:g}" for x in MU_EFFS), help="plain bearings, load-dependent (comparison, red team G6); '' = off")
    ap.add_argument("--tau0", type=float, default=TAU0); ap.add_argument("--tilt", default="hub,gh", help="plain-bearing tilt couple about the bearing centre (hub) and/or GH (gh, rt_wedge.py)")
    ap.add_argument("--quick", action="store_true", help="nominal case only (rolling bearings mu_eff 0.005, speed 1), no validation")
    ap.add_argument("--no-validate", action="store_true"); ap.add_argument("--out", default=None)
    a = ap.parse_args(); global DES
    t0 = time.time(); DES = des = Design(a.design); N = des.N
    cases = [c for c in a.cases.split(",") if c]
    lst = lambda x: [float(v) for v in x.split(",") if v.strip()]
    fr, sp, mur, mus = lst(a.friction), lst(a.speed), lst(a.mu_roll), lst(a.mu_eff); tilts = [x for x in a.tilt.split(",") if x.strip()]
    nom_mu = max(mur) if mur else MU_ROLL[-1]
    if a.quick: fr, sp, mur, mus, cases = [], [1.0], [nom_mu], [], ["passive"]
    cl = [i for i, c in enumerate(des.clips) if a.clips is None or c["name"] in a.clips.split(",") or str(i) in a.clips.split(",")]
    print(f"dynamics {des.id}: N = {N}, link masses " + ", ".join(f"{g} {1000 * des.mp[g][0]:.1f} g" for g in des.groups[1:]) +
          f"; arm parts (H) {1000 * des.H_mass:.0f} g carried by the arm; {sum(len(v) for v in des.prims.values())} contact primitives", flush=True)
    ik = des.ik_check(); print(f"  chain vs the clips' G: max {max(ik.values()):.3f} deg {ik}", flush=True)
    todo = [(case_key(f, s, c), ci, dict(friction=f, speed=s, case=c)) for c in cases for f in fr for s in sp for ci in cl]                       # constant Coulomb (the brief)
    todo += [(load_key(mu, a.tau0_roll, s, c, "hub"), ci, dict(speed=s, case=c, mu_eff=mu, tau0=a.tau0_roll, tilt="hub")) for c in cases for mu in mur for s in sp for ci in cl]   # rolling (main)
    todo += [(load_key(mu, a.tau0, 1.0, c, tl), ci, dict(speed=1.0, case=c, mu_eff=mu, tau0=a.tau0, tilt=tl)) for c in cases for tl in tilts for mu in mus for ci in cl]       # plain (comparison)
    nom = load_key(nom_mu, a.tau0_roll, 1.0, "passive", "hub")
    if not a.quick:                                                                    # attribution: the same arm motion without friction / without gravity
        for s in sp:
            todo += [(f"passive|nofric|s{s:g}", ci, dict(friction=0.0, speed=s, case="passive")) for ci in cl]
            todo += [(f"passive|nofric|nograv|s{s:g}", ci, dict(friction=0.0, speed=s, case="passive", gravity=False)) for ci in cl]
    lcases = cases
    res = {}; errs = []
    with (mp.get_context("fork").Pool(a.jobs) if a.jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap_unordered(_task, todo) if pool else map(_task, todo)
        for n_, (key, ci, summ, err) in enumerate(it):
            if err: errs.append(f"{key} {des.clips[ci]['name']}: {err}"); print("  ERROR", errs[-1], flush=True); continue
            res.setdefault(key, {})[des.clips[ci]["name"]] = summ
            if (n_ + 1) % 16 == 0: print(f"  {n_ + 1}/{len(todo)} runs {time.time() - t0:.0f}s", flush=True)
    out = dict(version=VERSION, design=des.id, n_joints=N, seconds=None, jobs=a.jobs,
               model=dict(frame="thorax rig frame (x anterior, y up, z right, origin GH); gravity -y", timestep_s=DT, integrator="implicitfast, Newton, noslip 20 (exact Coulomb joint friction)",
                          scapula="ball joint at GH, prescribed: body_pose.scap law with the 20 deg kink rounded over 1.5 deg (softplus)",
                          arm="humerus follows the clip's followed pose p (PCHIP through the clip's knots), cuff on its axis",
                          cuff_mm=CUFF_MM, tissue=dict(TISSUE, source="Schiebl et al. 2025, Sensors 25(15):4605 (upper-arm interface, median stiffness); damping assumed"),
                          link_mass_g={g: round(1000 * des.mp[g][0], 2) for g in des.groups[1:]}, link_volume_cm3={g: round(des.mp[g][3], 3) for g in des.groups[1:]},
                          link_com_mm={g: [round(1000 * x, 1) for x in des.mp[g][1]] for g in des.groups[1:]},
                          link_inertia_about_gh_kgm2={g: round(float(np.trace(des.mp[g][2] + des.mp[g][0] * (np.dot(des.mp[g][1], des.mp[g][1]) * np.eye(3) - np.outer(des.mp[g][1], des.mp[g][1]))) / 2), 7) for g in des.groups[1:]},
                          arm_parts_mass_g=round(1000 * des.H_mass, 1), forearm_parts_mass_g=round(1000 * des.F_mass, 1), densities_g_cm3=G_CM3,
                          cases_run=cases, mvp1="unpowered (user, 2026-10-15): every joint passive, no motor / gear / cable; motor and servo cases exist only as --cases options",
                          cuff_pressure=dict(area_cm2=CUFF_AREA_CM2, strap_preload_kPa=STRAP_KPA, sustained_budget_kPa=COMFORT_KPA,
                                             rule="mean pressure = cuff force / skin-side shell area; the budget left for the exo is COMFORT - STRAP (edge peaks ~2x the mean)",
                                             arm_parts_weight_N=round(9.81 * des.H_mass, 2)),
                          contact=dict(mu=MU_CONTACT, primitives={g: len(v) for g, v in des.prims.items()}, hub_r_mm=des.hub_r, margin_mm=0.0, near_miss_band_mm=2.0,
                                       rule="every member pair incl. adjacent ones; at a shared joint the bearing (hub on hub, hub on the other member's hub-side ribbon root) is the hinge, not a contact")),
               load_friction=dict(model="tau_f,i = tau0 + mu_eff |M_perp,i| each step (red team G6, pipeline/redteam/rt_wedge.py); M_perp from cfrc_int one step behind",
                                  rolling=dict(mu_eff=mur, tau0_Nm=a.tau0_roll, tilt_ref="hub", speeds=sp,
                                               basis="pair of shielded deep-groove / needle bearings at the hub, bore d ~10 mm, spacing L ~5 mm: the tilt couple is a force couple M/L, "
                                                     "SKF simplified friction M_f = 0.5 mu P d per bearing (mu 0.0015 deep groove, 0.0025 needle) -> mu_eff = mu d / L = 0.003-0.005; tau0 = grease drag of 2 shielded bearings"),
                                  plain=dict(mu_eff=mus, tau0_Nm=a.tau0, tilt_refs=tilts, speed=1.0), cases=lcases,
                                  tilt_ref_note="hub: moment about the hub stack's mid-height on the axis (the pin carries the force); gh: about the GH centre, rt_wedge.py's model without R x F",
                                  bearing_r_mm={str(k): round(float(v), 1) for k, v in des.bearing_r.items()}),
               chain_vs_clip_G_max_deg=ik, thresholds=THRESH, nominal=nom, cases={}, errors=errs)
    for key in sorted(res):
        C = res[key]; out["cases"][key] = dict(clips=C, **rollup(C, N))
    if any(k.startswith("passive|nofric") for k in res):
        out["attribution"] = {f"s{s:g}": attribution(res, load_key(nom_mu, a.tau0_roll, s, "passive", "hub"), s) for s in sp}
    if nom in res: out["verdict"] = verdict(out, nom)
    path = a.out or os.path.join(des.dd, "judge", "dynamics.json"); os.makedirs(os.path.dirname(path), exist_ok=True)
    out["seconds"] = round(time.time() - t0); json.dump(out, open(path, "w"), indent=1)          # the runs are saved before the validations
    if not a.no_validate and not a.quick:
        print("  validating against transmission.py (quasi-static) ...", flush=True); out["validation"] = validate(des, jobs=a.jobs)
        v = out["validation"]; print(f"  validation: {v.get('frames_compared')} frames, rel. error median {v.get('rel_err_median')} p95 {v.get('rel_err_p95')} max {v.get('rel_err_max')} -> {'OK' if v.get('ok') else 'NOT OK'}", flush=True)
        if mus:
            print("  validating the load-dependent friction against rt_wedge.py (quasi-static wedge) ...", flush=True); out["validation_load_friction"] = vw = validate_wedge(des, jobs=a.jobs)
            if vw.get("ok") is not None:
                print(f"  wedge validation: unlocked {vw['unlocked_frames']} frames rel. error median {vw['unlocked_rel_err_median']} p95 {vw['unlocked_rel_err_p95']}; locked {vw['locked_frames']} frames need "
                      f"{vw['locked_moment_over_constant_friction']['median']}x (min {vw['locked_moment_over_constant_friction']['min']}x) the constant-friction moment; onset {vw['onset_agree_within_0p2s']} -> {'OK' if vw['ok'] else 'NOT OK'}", flush=True)
    out["seconds"] = round(time.time() - t0); json.dump(out, open(path, "w"), indent=1)
    print_report(out); print("wrote", path)

def rollup(C, N):
    """worst clip and the case's maxima"""
    wc = max(C, key=lambda n: C[n]["moment_gh_Nm"]["peak"])
    r = dict(worst_clip=wc, force_peak_N=max(c["force_N"]["peak"] for c in C.values()), force_rms_max_N=max(c["force_N"]["rms"] for c in C.values()),
             moment_gh_peak_Nm=max(c["moment_gh_Nm"]["peak"] for c in C.values()), moment_gh_rms_max_Nm=max(c["moment_gh_Nm"]["rms"] for c in C.values()),
             moment_cuff_peak_Nm=max(c["moment_cuff_Nm"]["peak"] for c in C.values()), twist_peak_deg=max(c["tracking_deg"]["twist_peak"] for c in C.values()),
             tracking_peak_deg=max(c["tracking_deg"]["peak"] for c in C.values()), joint_speed_peak_dps=max(max(c["joint_speed_dps"]) for c in C.values()),
             speed_ratio_max=max(c["speed_ratio_max"] for c in C.values()), joint_acc_peak_dps2=max(max(c["joint_acc_dps2"]) for c in C.values()),
             stall_events=sum(c["stalls"]["events"] for c in C.values()), lags_over_10deg=sum(c["stalls"]["lags_over_10deg"] for c in C.values()),
             worst_missed_deg=max(c["stalls"]["worst_missed_deg"] for c in C.values()),
             lock_clips=[n for n, c in C.items() if not c["drive"]["drives"]], frames_over_lock_max=max(c["drive"]["frames_over_lock"] for c in C.values()),
             frames_over_felt_max=max(c["drive"]["frames_over_felt"] for c in C.values()), contact_touch=any(c["contact"]["touch"] for c in C.values()),
             cuff_pressure_peak_kPa=max(c["cuff_pressure_kPa"]["peak"] for c in C.values()),
             contact_peak_N=max(c["contact"]["peak_N"] for c in C.values()), amp_qs_max=max(c["amp_qs"]["max"] for c in C.values()))
    if N == 4: r["spare_drift_max_deg"] = max(c.get("spare_drift_deg", 0) for c in C.values())
    if any("servo_peak_Nm" in c for c in C.values()): r["servo_peak_Nm"] = max(c.get("servo_peak_Nm", 0) for c in C.values())
    if any("load_friction" in c for c in C.values()):
        r["friction_peak_Nm"] = max(max(c["load_friction"]["friction_peak_Nm"]) for c in C.values()); r["tilt_peak_Nm"] = max(max(c["load_friction"]["tilt_peak_Nm"]) for c in C.values())
    return r

def attribution(res, nom, s):
    """per clip: the peak moment about GH of the nominal (rolling-bearing) run, of the same motion without friction
    (gravity + inertia) and without friction and gravity (inertia alone), each at its own peak"""
    out = {}
    for n, c in res.get(nom, {}).items():
        a = res.get(f"passive|nofric|s{s:g}", {}).get(n); b = res.get(f"passive|nofric|nograv|s{s:g}", {}).get(n)
        if not a or not b: continue
        out[n] = dict(total_peak_Nm=c["moment_gh_Nm"]["peak"], without_friction_peak_Nm=a["moment_gh_Nm"]["peak"], inertia_only_peak_Nm=b["moment_gh_Nm"]["peak"],
                      total_force_peak_N=c["force_N"]["peak"], without_friction_force_peak_N=a["force_N"]["peak"], inertia_only_force_peak_N=b["force_N"]["peak"])
    return out

def verdict(out, nom):
    T = THRESH; c = out["cases"][nom]; v = {}
    def free(x): return bool(x["moment_gh_peak_Nm"] <= T["free_moment_gh_peak_Nm"] and x["moment_gh_rms_max_Nm"] <= T["free_moment_gh_rms_Nm"] and x["force_peak_N"] <= T["free_force_peak_N"]
                             and x["lags_over_10deg"] == 0 and x["twist_peak_deg"] <= T["free_twist_peak_deg"] and x.get("spare_drift_max_deg", 0) <= T["free_spare_drift_deg"])
    v["moves_freely_nominal"] = free(c); v["drives_nominal"] = not c["lock_clips"]
    v["rule"] = (f"moves freely: |M_GH| peak <= {T['free_moment_gh_peak_Nm']} N.m and rms <= {T['free_moment_gh_rms_Nm']}, cuff force <= {T['free_force_peak_N']} N, cuff twist <= "
                 f"{T['free_twist_peak_deg']} deg, no stall missing >= {LAG_DEG} deg of planned joint travel, 4R spare drift <= {T['free_spare_drift_deg']} deg; "
                 f"drives: never |M_GH| > {T['lock_moment_gh_Nm']} N.m or cuff force > {T['iso_ts_15066_upper_arm_N']} N (ISO/TS 15066 upper arm)")
    v["nominal_case"] = nom
    v["cuff_pressure_nominal_kPa"] = dict(peak=round(c["force_peak_N"] / CUFF_AREA_CM2 * 10, 3), budget_for_exo=COMFORT_KPA - STRAP_KPA,
                                          with_arm_parts_weight=round((c["force_peak_N"] + 9.81 * DES.H_mass) / CUFF_AREA_CM2 * 10, 3))
    v["per_case"] = {k: dict(moment_gh_peak_Nm=x["moment_gh_peak_Nm"], force_peak_N=x["force_peak_N"], twist_peak_deg=x["twist_peak_deg"], lags_over_10deg=x["lags_over_10deg"],
                             contact=x["contact_touch"], spare_drift_deg=x.get("spare_drift_max_deg"), lock_clips=x["lock_clips"], free=free(x), drives=not x["lock_clips"],
                             cuff_pressure_peak_kPa=x["cuff_pressure_peak_kPa"], within_pressure_budget=bool(x["cuff_pressure_peak_kPa"] <= COMFORT_KPA - STRAP_KPA),
                             under_iso_15066=bool(x["force_peak_N"] < T["iso_ts_15066_upper_arm_N"])) for k, x in out["cases"].items() if "nofric" not in k}
    return v

def print_report(out):
    print(f"dynamics {out['design']} (N = {out['n_joints']})")
    for k, c in out["cases"].items():
        if "nofric" in k: continue
        print(f"  {k:30s} worst {c['worst_clip'][:20]:20s} M_GH peak {c['moment_gh_peak_Nm']:6.3f} (rms<= {c['moment_gh_rms_max_Nm']:5.3f}) N.m  F {c['force_peak_N']:6.2f} N  "
              f"twist {c['twist_peak_deg']:6.2f} deg  qdot {c['joint_speed_peak_dps']:6.1f} deg/s ({c['speed_ratio_max']:.2f}x)  lag>10 {c['lags_over_10deg']:2d}  lock {len(c['lock_clips'])} clips  "
              f"contact {c['contact_peak_N']:6.2f} N" + (f"  spare drift {c['spare_drift_max_deg']:6.1f}" if "spare_drift_max_deg" in c else "") + (f"  servo {c['servo_peak_Nm']:.2f} N.m" if "servo_peak_Nm" in c else ""))

if __name__ == "__main__":
    main()
