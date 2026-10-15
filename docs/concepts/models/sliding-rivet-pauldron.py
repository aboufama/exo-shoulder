"""sliding-rivet-pauldron: hubless nested plates with follower-in-slot joints (3 ACTIVE DOF, 0 passive).

Topology (scapula handler -> user's upper-arm cuff), the spec of docs/concepts/catalogue.json:
    S cap (plate on top of the scapula, fixed in the scapula frame S) --J1: rollers on L1 run in arc slots of the S cap,
    circles about b--> L1 (small 'guide' disc) --J2: rollers on L1 run in arc slot(s) of the L2 band, circles about
    p2--> L2 (band at polar A1 about p2 + ramped strap + arm-end disc) --J3: rollers on the H saddle run in arc slots of
    L2's arm-end disc, circles about W--> H saddle (+ BOTTOM stub) on the user's cuff.
Kinematics = the champion's spherical 3R (axes b, p2, W through GH; two-circle closure on one branch); every joint is a
pair of needle cam followers in slots instead of a hub. Plates are spherical shells about GH, nested: S cap (R_S), L1
(R_S + t + g), L2 band (R_S + 2 (t + g)); H saddle (R_H) under L2's arm-end disc (R_H + t + g).

DOF: J1, J2, J3 are revolutes (two rollers in circular slots about the same axis, see the correction below), so the
chain is a spherical 3R: the arm's 3 rotations fix theta1, phi_g, theta3 uniquely on the design branch. No spare
coordinate, nothing passive (the cuff liner / self-aligning cuff slides of the user stay outside the count).

SPEC CORRECTIONS (said in docs/concepts/sliding-rivet-pauldron.md):
  1. Follower layout. Two rollers in circular slots about one axis make a revolute only if their azimuths about that
     axis differ by neither 0 nor 180 deg: a roller constrains only the motion normal to its slot, and two rollers at
     azimuths a and a + 180 (spec J1 / J3) or on one meridian (spec J2: polar A1 +- 6 at the same azimuth phi_g)
     constrain the same direction twice - the plate can slide / rock along the slots at first order (play ~
     sqrt(2 r c) ~ 1.2 mm for 0.1 mm slot clearance). Here the two rollers of a joint sit fsep (default 90) deg apart
     in azimuth about the joint axis; on J2 they are D2 deg apart along the band (one slot, or two staggered slots).
  2. Roller stack. An O8 x 4 mm roller cannot sit inside a 2 mm plate: it protrudes 4 - t - g = 1.5 mm beyond the
     slotted plate, ending in an O10 x 1.5 retaining flange that grips the slotted plate (the flanges carry the
     normal / tilt loads). Studs are flush (countersunk) in the follower plate. J1's rollers point DOWN into the S cap
     (spec), so their flanges are skin-facing metal under the S cap (R_S >= their envelope + clearance + 1.5);
     J2 / J3 flanges sit on top of L2.
  3. Slots and outlines. Slot = 8.2 mm wide arc spanning the joint range + one roller radius + 0.5 mm each end; plate
     outlines are enlarged to keep a 4 mm rim around every slot and follower; two slots on one plate must not cross
     (radial web >= 2 mm or disjoint arcs); a through-slot longer than 330 deg cuts its plate in two (design invalid).
  4. Variant 'post' (an improvement inside the morphology): the J2 rollers stand on O6 posts on L1, so the band sits
     at its own radius R_B = max(band envelope + clearance, R_S + 2 (t + g)) instead of raising the S cap and L1 with
     it ('nested', the spec).
Envelope (the baseline's convention, tools/concept_baseline.py): the radius of the skin under every skin-facing
sample, per pose, over the kinematically valid bench poses; per sample the p-th percentile (pct); a constant-radius
plate sits at the max of that over its samples + clear. The skin radius along a ray is the LOCAL outer skin: march
out from 20 mm (inside) to the first exit, continue through re-entries closer than 15 mm (narrow folds), ignore body
parts farther out (the neck / head; a part that reaches them is caught by the bench's contact test).
Samples: skin-facing faces (plate undersides minus the slot holes, strap / stub undersides, J1 flanges) on a 2 mm
grid (~1 point / 4 mm2) - in-band and contact; tops, edges, rollers, posts - contact and interference only.
Taken: closure on the branch with a sing-deg margin; every roller inside its slot (the slot spans cover the fit-clip
frames, plus the workspace at quantile cov_ws); along each fit clip (all frames, 10 fps) no joint jump > 30 deg since
the last followed frame (a flip is a frame not followed); no interference (non-adjacent members >= 1 mm, adjacent
members >= 0.2 mm outside their own joint); no metal inside the body (bench contact).

    python3 docs/concepts/models/sliding-rivet-pauldron.py check [n_clip n_ws]   # default params + 4 named poses
    python3 docs/concepts/models/sliding-rivet-pauldron.py sweep                 # coarse -> refine, Bench(60, 160)
    python3 docs/concepts/models/sliding-rivet-pauldron.py plot  '<params json>' # docs/concepts/img/<id>.png
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "avg"))
import concept_bench as CB                                                  # noqa: E402

ID = "sliding-rivet-pauldron"
D2R = math.pi / 180
SP = 2.0                     # skin-facing sample grid (mm) -> ~1 point / 4 mm2
SP_O = 3.0                   # tops / edges (contact + interference only)
FLIP = 30.0                  # deg per 10 fps frame
R_TOP, R_ARM = 57.0, 65.0    # nominal radii (mm) used to turn mm sizes into angles before the envelope is known
WEB = 2.0                    # min metal between two slots (mm)

AXES = dict(r18=dict(b_az=32.55, b_el=80.56, w_d=71.38, w_az=4.78, A1=77.41, A2=81.45, branch=-1),     # spec champion (cad_r18)
            r20=dict(b_az=2.4305, b_el=80.6763, w_d=86.3277, w_az=21.8297, A1=76.9018, A2=66.7492, branch=-1))  # bench baseline
PARAMS = dict(AXES["r18"], sing=5.0, t=2.0, g=0.5, roller_d=8.0, roller_w=4.0, flange_d=10.0, slot_w=8.2, rim=4.0,
              n1=2, g1a=8.0, g1b=19.0, fsep1=90.0,           # J1: slot polar radii about b (deg), roller azimuth separation
              n2=1, d2=6.0, D2=30.0,                         # J2: 1 slot at A1 (or 2 at A1 -+ d2), rollers D2 deg apart about p2
              n3=2, g3a=8.0, g3b=17.0, fsep3=90.0,           # J3: slot polar radii about W
              capS=0.0, cap1=0.0, wB=26.0, cap3=0.0,         # extra outline beyond the minimum (deg), band width (mm)
              cov_ws=0.0, pct=100.0, clear=2.0, top="nested", arm_layer="env", stub_len=40.0, stub_w=14.0, stub_t=6.0)
SWEEP = dict(axes=("r18", "r20"), g1a=(6, 12), g1b=(14, 20), g3a=(6, 10), g3b=(12, 18), d2=(4, 8), D2=(20, 40),
             wB=(20, 40), t=(1.5, 2.5), cov_ws=(0.0, 0.9), pct=(90, 100), top=("nested", "post"), n1=(1, 2), n2=(1, 2), n3=(1, 2))


# ---------------------------------------------------------------- vectors
def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def wrap(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def bvec(az, el):
    a, e = az * D2R, el * D2R
    return np.array([-math.cos(e) * math.cos(a), math.sin(e), math.cos(e) * math.sin(a)])


def w_dir(d, az):
    d, a = d * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def circ_int(c1, r1, c2, r2, sign):
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return unit(p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n), h2 > 0


def basis(u):
    """orthonormal (u, a, c) with c = u x a; a deterministic"""
    u = unit(np.asarray(u, float)); ref = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    a = unit(np.cross(u, ref)); return u, a, np.cross(u, a)


def sph(X, u, a, c):
    """polar angle (rad) about u and azimuth (deg, from a toward c) of points X; and |X|"""
    r = np.linalg.norm(X, axis=-1) + 1e-12
    pol = np.arccos(np.clip(X @ u / r, -1, 1)); az = np.arctan2(X @ c, X @ a) / D2R
    return pol, az, r


def from_sph(pol, az_deg, u, a, c):
    az = np.asarray(az_deg) * D2R
    return (np.cos(pol)[..., None] * u + np.sin(pol)[..., None] * (np.cos(az)[..., None] * a + np.sin(az)[..., None] * c))


def arc_range(vals):
    """circular range (lo, hi) deg (hi - lo may exceed 360) of the angles vals"""
    v = np.asarray(vals, float)
    m = math.atan2(np.sin(v * D2R).mean(), np.cos(v * D2R).mean()) / D2R; dv = wrap(v - m)
    return float(m + dv.min()), float(m + dv.max())


def in_arc(a, lo, hi):
    if hi - lo >= 360 - 1e-9: return np.ones(np.shape(a), bool)
    return ((np.asarray(a) - lo) % 360.0) <= (hi - lo)


def arcs_overlap(a, b):
    if a[1] - a[0] + b[1] - b[0] >= 360: return True
    return bool(in_arc(b[0], *a) or in_arc(b[1], *a) or in_arc(a[0], *b))


# ---------------------------------------------------------------- kinematics
POSES = CB._poses_all()
HG_ALL = POSES["HG"].astype(float); RS_ALL = POSES["RS"].astype(float)
_NAMES = list(POSES["NAMES"]); CID = POSES["CID"]
FIT_IDS = [_NAMES.index(n) for n in CB.FIT]; WS_ID = _NAMES.index("Workspace (envelope)")


def axes_of(p):
    b = bvec(p["b_az"], p["b_el"]); W0 = w_dir(p["w_d"], p["w_az"]); return b, W0


def chain(p, HG):
    """IK in the scapula frame S for humerus rotations HG (P, 3, 3) (canonical humerus in S). Returns the member frames
    (columns = local axes in S) and the joint values: th1 = azimuth of p2 about b (S basis), phig = azimuth of b about p2
    in L2 (from W), th3 = azimuth of p2 about W in the humerus (canonical basis)."""
    b, W0 = axes_of(p); A1, A2 = p["A1"] * D2R, p["A2"] * D2R; Pn = len(HG)
    W = HG @ W0; B_ = np.broadcast_to(b, (Pn, 3))
    p2, ok = circ_int(B_, A1, W, A2, float(p["branch"]))
    sep = np.arccos(np.clip(W @ b, -1, 1)); s = p["sing"] * D2R
    ok &= (sep >= abs(A1 - A2) + s) & (sep <= min(A1 + A2, 2 * math.pi - A1 - A2) - s)
    m = unit(p2 - (p2 @ b)[:, None] * b); n = np.cross(B_, m)
    RL1 = np.stack([B_, m, n], -1)
    e2 = unit(W - (W * p2).sum(-1, keepdims=True) * p2); e3 = np.cross(p2, e2)
    RL2 = np.stack([p2, e2, e3], -1)
    _, q1, q2 = basis(b); th1 = np.arctan2(m @ q2, m @ q1) / D2R
    phig = np.arctan2((B_ * e3).sum(-1), (B_ * e2).sum(-1)) / D2R
    pc = np.einsum("pji,pj->pi", HG, p2); _, r1, r2 = basis(W0)
    pcp = unit(pc - (pc @ W0)[:, None] * W0); th3 = np.arctan2(pcp @ r2, pcp @ r1) / D2R
    return dict(ok=ok, p2=p2, W=W, RL1=RL1, RL2=RL2, th1=th1, phig=phig, th3=th3, sep=sep / D2R)


# ---------------------------------------------------------------- sample grids (member-local unit directions)
def cap_grid(u, a, c, rho, R, step=SP):
    """unit directions on a spherical cap of polar radius rho (rad) about u, ~step mm apart at radius R"""
    h = step / R; g = np.arange(-rho, rho + 1e-9, h); X, Y = np.meshgrid(g, g); X, Y = X.ravel(), Y.ravel()
    pol = np.hypot(X, Y); keep = pol <= rho; az = np.arctan2(Y[keep], X[keep]) / D2R
    return from_sph(pol[keep], az, u, a, c)


def band_grid(u, a, c, pol_lo, pol_hi, az_lo, az_hi, R, step=SP):
    """unit directions on a band about u: polar [pol_lo, pol_hi] (rad), azimuth [az_lo, az_hi] (deg from a)"""
    pols = np.linspace(pol_lo, pol_hi, max(2, int(math.ceil((pol_hi - pol_lo) * R / step)) + 1))
    out = []
    for pl in pols:
        circ = R * math.sin(pl); n = max(2, int(math.ceil((az_hi - az_lo) * D2R * circ / step)) + 1)
        az = np.linspace(az_lo, az_hi, n); out.append(from_sph(np.full(n, pl), az, u, a, c))
    return np.concatenate(out)


def strap_grid(u0, u1, s0, s1, width, R, step=SP):
    """unit directions on a strap along the great circle u0 -> u1, arc angle [s0, s1] (rad) from u0, width mm.
    returns dirs (k, 3), station index (k,), stations (ns,)"""
    nrm = unit(np.cross(u0, u1)); e2 = unit(np.cross(nrm, u0))
    ss = np.linspace(s0, s1, max(2, int(math.ceil((s1 - s0) * R / step)) + 1))
    ws = np.arange(-width / 2 + step / 2, width / 2, step) / R
    S_, Wd = np.meshgrid(ss, ws, indexing="ij"); st = np.repeat(np.arange(len(ss)), len(ws))
    D = np.cos(S_.ravel())[:, None] * u0 + np.sin(S_.ravel())[:, None] * e2
    D = unit(D * np.cos(Wd.ravel())[:, None] + nrm * np.sin(Wd.ravel())[:, None])
    return D, st, ss, (u0, e2, nrm)


def disc_pts(center_dir, radius_mm, R, step=1.5):
    """unit directions on a small flat disc (radius_mm) around center_dir at radius R"""
    u, a, c = basis(center_dir); g = np.arange(-radius_mm, radius_mm + 1e-9, step); X, Y = np.meshgrid(g, g)
    k = X ** 2 + Y ** 2 <= radius_mm ** 2
    return unit(u * R + X[k][:, None] * a + Y[k][:, None] * c)


# ---------------------------------------------------------------- local-outer skin radius (envelope)
def skin_exit(B, i, D, r0=20.0, r_max=150.0, fold=15.0):
    """radius of the local outer skin along thorax unit directions D (k, 3) from GH in bench pose i: march out from r0
    (inside) to the first exit, continue through any re-entry closer than `fold` mm, stop at r_max"""
    k = len(D); r = np.full(k, r0); ex = np.full(k, np.nan); st = np.zeros(k, np.int8)   # 0 inside, 1 outside, 2 done
    for _ in range(200):
        a = np.nonzero(st < 2)[0]
        if not len(a): break
        d = B.dist(i, D[a] * r[a, None])
        ins = d < 0
        newly = ins & (st[a] == 1)                                             # re-entered (a fold)
        out_now = (~ins) & (st[a] == 0)                                        # just exited
        ex[a[out_now]] = r[a[out_now]]; st[a[out_now]] = 1; st[a[newly]] = 0
        r[a[ins]] += np.maximum(-d[ins], 0.3)
        o = ~ins; r[a[o]] += np.maximum(d[o], 0.5)
        done = (st[a] == 1) & (r[a] > ex[a] + fold); st[a[done]] = 2
        big = r[a] > r_max; st[a[big]] = 2; ex[a[big & np.isnan(ex[a])]] = r_max
    return np.where(np.isnan(ex), r_max, ex)


# ---------------------------------------------------------------- parts
class Part:
    """a member-fixed part: skin-facing samples (dirs, radii), other samples, and an inside test in member coordinates.
    kind 'shell': constant-radius spherical piece with a footprint test; 'prof': strap with a station radius profile"""
    def __init__(self, name, member, face_dirs, face_r, other, inside, r_lo, r_hi):
        self.name, self.member = name, member
        self.face_dirs, self.face_r = face_dirs, face_r
        self.other = other; self.inside = inside; self.r_lo, self.r_hi = r_lo, r_hi

    def face(self):
        return self.face_dirs * self.face_r[:, None]


def shell_part(name, member, dirs_all, keep_face, R, t, foot):
    """spherical shell [R, R + t] over dirs_all; keep_face = mask of metal (False = hole); foot(dirs, margin_rad) -> in"""
    fd = dirs_all[keep_face]
    other = np.r_[fd[::2] * (R + t)] if len(fd) else np.zeros((0, 3))

    def inside(X, m):
        r = np.linalg.norm(X, axis=1); return foot(X / r[:, None], m / np.maximum(r, 1)) & (r >= R - m) & (r <= R + t + m)
    return Part(name, member, fd, np.full(len(fd), float(R)), other, inside, R, R + t)


def cyl_part(name, member, center_dir, rad, r0, r1, face):
    """small cylinder along the radial direction center_dir, radius rad (mm), radial span [r0, r1]; face: its lower end
    faces the skin"""
    u = unit(np.asarray(center_dir, float)); D = disc_pts(u, rad, r0)
    ends = np.r_[D * r1]; rings = []
    _, a, c = basis(u)
    for rr in np.arange(r0, r1 + 1e-6, 1.0):
        th = np.linspace(0, 2 * math.pi, 16, endpoint=False)
        rings.append(unit(u * rr + rad * (np.cos(th)[:, None] * a + np.sin(th)[:, None] * c)) * rr)
    other = np.r_[ends, np.concatenate(rings)]
    if not face: other = np.r_[D * r0, other]

    def inside(X, m):
        r = np.linalg.norm(X, axis=1); ax = X @ u; lat = np.linalg.norm(X - ax[:, None] * u, axis=1)
        return (lat <= rad + m) & (ax >= r0 - m) & (ax <= r1 + m)
    fd = D if face else np.zeros((0, 3)); fr = np.full(len(fd), float(r0))
    return Part(name, member, fd, fr, other, inside, r0 - rad * 0.2, r1)


def prof_part(name, member, D, st, ss, frame, prof, t, width):
    """strap: dirs D at stations st (ss: station angles), underside radius prof[station], thickness t"""
    u0, e2, nrm = frame; fr = prof[st]
    other = np.r_[D[::2] * (fr[::2] + t)[:, None]]

    def inside(X, m):
        x = X @ u0; y = X @ e2; z = X @ nrm; rho = np.hypot(x, y); s = np.arctan2(y, x)
        rp = np.interp(s, ss, prof)
        return ((s >= ss[0] - m / np.maximum(rho, 1)) & (s <= ss[-1] + m / np.maximum(rho, 1)) & (np.abs(z) <= width / 2 + m)
                & (rho >= rp - m) & (rho <= rp + t + m))
    return Part(name, member, D, fr, other, inside, float(prof.min()), float(prof.max() + t))


# ---------------------------------------------------------------- the design
MEMBERS = ("S", "L1", "L2", "H")
ADJ = {("S", "L1"), ("L1", "L2"), ("L2", "H")}
JOINT_EXEMPT = {("scap", "j1fl"), ("scap", "j1rol"), ("band", "j2rol"), ("band", "j2fl"), ("armend", "j3rol"), ("armend", "j3fl"),
                ("l1", "j1rol"), ("l1", "j2rol"), ("l1", "j1fl"), ("saddle", "j3rol"), ("l1", "j2post"), ("band", "j2post")}


class Design:
    def __init__(self, p, B, log=print):
        self.p = p = dict(PARAMS, **p); self.B = B; self.log = log; self.invalid = ""
        t, g = p["t"], p["g"]; self.pitch = t + g; self.fl = max(p["roller_w"] - t - g, 1.0)   # roller end + flange beyond the slotted plate
        b, W0 = axes_of(p); self.b, self.W0 = b, W0; A1, A2 = p["A1"] * D2R, p["A2"] * D2R
        # ---- joint ranges over the fit-clip frames (all) + workspace (quantile cov_ws), closure-valid only
        fit = np.isin(CID, FIT_IDS); ws = CID == WS_ID
        C = chain(p, HG_ALL); self.C_all = C; ok = C["ok"]
        self.fit_closure = float(ok[fit].mean())
        def span(v):
            """shortest arc that holds every fit-clip value and a share cov_ws of the workspace values"""
            lo, hi = arc_range(v[fit & ok]); q = p["cov_ws"]
            if q <= 0: return lo, hi
            w = v[ws & ok]; out = ((w - lo) % 360.0) > (hi - lo)
            need = int(math.ceil(q * len(w))) - int((~out).sum())
            if need <= 0: return lo, hi
            dl = np.sort((lo - w[out]) % 360.0); dr_by = ((w[out] - hi) % 360.0)[np.argsort((lo - w[out]) % 360.0)]
            best = (np.inf, 0.0, 0.0)
            for i in range(0, min(need, len(dl)) + 1):                     # i points covered by the left extension
                a = dl[i - 1] if i else 0.0; k = need - i
                if k <= 0: b = 0.0
                else:
                    rest = dr_by[i:]
                    if len(rest) < k: continue
                    b = float(np.partition(rest, k - 1)[k - 1])
                if a + b < best[0]: best = (a + b, a, b)
            return lo - best[1], hi + best[2]
        self.rng1, self.rngg, self.rng3 = span(C["th1"]), span(C["phig"]), span(C["th3"])
        # ---- J1: rollers on L1 at polar g1a / g1b about b, azimuths -+ fsep1/2 from p2's meridian; slots in the S cap
        sw = p["slot_w"]; rr = p["roller_d"] / 2 + 0.5
        n1 = int(p["n1"]); g1 = (p["g1a"], p["g1b"]) if n1 == 2 else (p["g1a"], p["g1a"])
        self.j1 = [(g1[0] * D2R, -p["fsep1"] / 2), (g1[1] * D2R, p["fsep1"] / 2)]          # (polar rad, azimuth deg in L1)
        self.slots1 = self._slots(self.j1, self.rng1, R_TOP, n1)
        # ---- J2: rollers on L1 at polar A1 (or A1 -+ d2) about p2, azimuths -+ D2/2 from b about p2; slots in the band
        n2 = int(p["n2"]); d2 = p["d2"] * D2R if n2 == 2 else 0.0
        self.j2 = [(A1 - d2, -p["D2"] / 2), (A1 + d2, p["D2"] / 2)]
        self.slots2 = self._slots(self.j2, self.rngg, R_TOP, n2)
        # ---- J3: rollers on H at polar g3a / g3b about W0, azimuths alpha -+ fsep3/2 (canonical); slots in L2's arm end
        n3 = int(p["n3"]); g3 = (p["g3a"], p["g3b"]) if n3 == 2 else (p["g3a"], p["g3a"])
        mid3 = 0.5 * (self.rng3[0] + self.rng3[1]); self.alpha3 = mid3 + 180.0     # slots centred opposite p2 (and the strap)
        self.j3 = [(g3[0] * D2R, self.alpha3 - p["fsep3"] / 2), (g3[1] * D2R, self.alpha3 + p["fsep3"] / 2)]
        # in L2 the roller azimuth about W (from p2's projection) is alpha - th3
        self.slots3 = self._slots([(pl, 0.0) for pl, _ in self.j3], (-self.rng3[1], -self.rng3[0]), R_ARM, n3,
                                  offs=[az for _, az in self.j3])
        for nm, sl in (("J1", self.slots1), ("J2", self.slots2), ("J3", self.slots3)):
            why = self._check_slots(sl, R_TOP if nm != "J3" else R_ARM)
            if why: self.invalid = f"{nm} {why}"; return
        # ---- outlines (polar radii, rad) with the rim
        rim = p["rim"]
        self.rhoS = max(max(s["pol"] for s in self.slots1) + (sw / 2 + rim) / R_TOP, 20 * D2R) + p["capS"] * D2R
        j2_from_b = max(math.acos(np.clip(math.cos(A1) * math.cos(pl) + math.sin(A1) * math.sin(pl) * math.cos(az * D2R), -1, 1))
                        for pl, az in self.j2)
        self.rho1 = max(max(pl for pl, _ in self.j1), j2_from_b) + (3.0 + rim) / R_TOP + p["cap1"] * D2R      # O6 stud boss + rim
        pols2 = [s["pol"] for s in self.slots2]
        self.hwB = max(p["wB"] / 2 / R_TOP, max(abs(x - A1) for x in pols2) + (sw / 2 + rim) / R_TOP)   # band half-width (rad)
        self.bandaz = (min(s["lo"] for s in self.slots2) - rim / (R_TOP * math.sin(A1)) / D2R,
                       max(s["hi"] for s in self.slots2) + rim / (R_TOP * math.sin(A1)) / D2R)
        self.rho3 = max(max(s["pol"] for s in self.slots3) + (sw / 2 + rim) / R_ARM, 18 * D2R) + p["cap3"] * D2R
        self._geometry()
        self._envelope()

    # ---- slots
    def _slots(self, rollers, rng, R, n, offs=None):
        """slot arcs (one per roller; with n = 1 both rollers share one slot) in the slotted member: azimuth = joint value
        + the roller's offset, widened by the roller radius + 0.5 mm"""
        out = []
        for k, (pl, az) in enumerate(rollers):
            off = az if offs is None else offs[k]
            circ = max(R * math.sin(pl), 1.0); m = (self.p["roller_d"] / 2 + 0.5) / circ / D2R
            out.append(dict(pol=pl, lo=rng[0] + off - m, hi=rng[1] + off + m, circ=circ))
        if n == 1:
            s = dict(pol=out[0]["pol"], lo=min(o["lo"] for o in out), hi=max(o["hi"] for o in out), circ=out[0]["circ"])
            if abs(out[0]["pol"] - out[1]["pol"]) > 1e-9: s = None
            out = [s] if s else out
        return out

    def _check_slots(self, sl, R):
        for s in sl:
            if s["hi"] - s["lo"] >= 330: return f"slot {s['hi'] - s['lo']:.0f} deg >= 330 (plate cut in two)"
            if R * math.sin(s["pol"]) - self.p["slot_w"] / 2 < 2.0: return "slot crosses the joint axis"
        if len(sl) == 2:
            a, b = sl
            if abs(a["pol"] - b["pol"]) * R < self.p["slot_w"] + WEB and arcs_overlap((a["lo"], a["hi"]), (b["lo"], b["hi"])):
                return "the two slots cross"
        return ""

    @staticmethod
    def _in_slots(pol, az, slots, R, sw):
        h = np.zeros(len(pol), bool)
        for s in slots:
            h |= (np.abs(pol - s["pol"]) <= sw / 2 / R) & in_arc(az, s["lo"], s["hi"])
        return h

    # ---- member-local sample geometry
    def _geometry(self):
        p = self.p; A1, A2 = p["A1"] * D2R, p["A2"] * D2R; sw = p["slot_w"]
        ex = np.array([1.0, 0, 0]); ey = np.array([0, 1.0, 0]); ez = np.array([0, 0, 1.0])
        G = {}
        # S cap (S frame, about b)
        bS = basis(self.b); D = cap_grid(*bS, self.rhoS, R_TOP); pol, az, _ = sph(D, *bS)
        G["scap"] = ("S", D, ~self._in_slots(pol, az, self.slots1, R_TOP, sw), bS, self.rhoS)
        # L1 (L1-local: x = b, y = toward p2)
        D = cap_grid(ex, ey, ez, self.rho1, R_TOP); G["l1"] = ("L1", D, np.ones(len(D), bool), (ex, ey, ez), self.rho1)
        self.j1_dirs = [from_sph(np.array([pl]), np.array([az]), ex, ey, ez)[0] for pl, az in self.j1]
        p2l = np.array([math.cos(A1), math.sin(A1), 0.0]); u2 = unit(ex - math.cos(A1) * p2l); v2 = np.cross(p2l, u2)
        self.j2_dirs = [from_sph(np.array([pl]), np.array([az]), p2l, u2, v2)[0] for pl, az in self.j2]
        # L2 (L2-local: x = p2, y = toward W, W at polar A2 azimuth 0)
        lo, hi = self.bandaz
        D = band_grid(ex, ey, ez, A1 - self.hwB, A1 + self.hwB, lo, hi, R_TOP); pol, az, _ = sph(D, ex, ey, ez)
        G["band"] = ("L2", D, ~self._in_slots(pol, az, self.slots2, R_TOP, sw), (ex, ey, ez), None)
        Wl = np.array([math.cos(A2), math.sin(A2), 0.0]); self.Wl = Wl
        uW = unit(ex - math.cos(A2) * Wl); vW = np.cross(Wl, uW); self.bW = (Wl, uW, vW)
        D = cap_grid(Wl, uW, vW, self.rho3, R_ARM); pol, az, _ = sph(D, Wl, uW, vW)
        G["armend"] = ("L2", D, ~self._in_slots(pol, az, self.slots3, R_ARM, sw), self.bW, self.rho3)
        # strap: from the arm-end disc edge to the band's near (lo) end, on the great circle W -> c(lo)
        cend = from_sph(np.array([A1]), np.array([lo + 0.0]), ex, ey, ez)[0]
        dWe = math.acos(np.clip(Wl @ cend, -1, 1)); self.strap_len = dWe - self.rho3
        wS = min(2 * self.hwB * R_TOP, 2 * self.rho3 * R_ARM)
        if self.strap_len > 1.0 / R_TOP:
            Dst, st, ss, fr = strap_grid(Wl, cend, self.rho3 - 1.0 / R_ARM, dWe + 1.0 / R_TOP, wS, R_TOP)
            self.strap = (Dst, st, ss, fr, wS)
        else: self.strap = None
        # H (canonical humerus frame): saddle about W0, J3 rollers, BOTTOM stub toward the humerus axis
        bH = basis(self.W0); _, r1, r2 = basis(self.W0); self.bH = (self.W0, r1, r2)
        D = cap_grid(self.W0, r1, r2, self.rho3, R_ARM); G["saddle"] = ("H", D, np.ones(len(D), bool), self.bH, self.rho3)
        self.j3_dirs = [from_sph(np.array([pl]), np.array([az]), self.W0, r1, r2)[0] for pl, az in self.j3]
        hum = np.array([0.0, -1.0, 0.0])
        s0 = self.rho3 + 0.5 / R_ARM; s1 = self.rho3 + p["stub_len"] / R_ARM                  # from the saddle edge
        self.stub = strap_grid(self.W0, hum, s0, s1, p["stub_w"], R_ARM) + (p["stub_w"],)
        self.G = G

    # ---- rotations member -> S for chain values C at index k
    @staticmethod
    def rot(C, k, member):
        if member == "S": return np.eye(3)
        if member == "L1": return C["RL1"][k]
        if member == "L2": return C["RL2"][k]
        return C["HG"][k]

    def _kin_ok(self, C, k):
        if not C["ok"][k]: return "closure"
        for nm, val, rngv in (("J1", C["th1"][k], self.rng1), ("J2", C["phig"][k], self.rngg), ("J3", C["th3"][k], self.rng3)):
            if not in_arc(val, rngv[0] - 1e-6, rngv[1] + 1e-6): return nm + " limit"
        return ""

    # ---- envelope: per-sample skin radius over the valid bench poses -> radii
    def _envelope(self):
        p = self.p; B = self.B; t0 = time.time()
        HGb = HG_ALL[B.idx]; RSb = RS_ALL[B.idx]; C = chain(p, HGb); C["HG"] = HGb; self.Cb = C
        self.kin = [self._kin_ok(C, k) for k in range(len(B.idx))]
        valid = [k for k in range(len(B.idx)) if not self.kin[k]]
        sets = []                                                                # (name, member, local dirs)
        for nm, (mem, D, keep, *_r) in self.G.items(): sets.append((nm, mem, D[keep]))
        for k, d in enumerate(self.j1_dirs): sets.append((f"j1fl{k}", "L1", disc_pts(d, p["flange_d"] / 2, R_TOP)))
        if self.strap is not None: sets.append(("strap", "L2", self.strap[0]))
        sets.append(("stub", "H", self.stub[0]))
        E = {nm: np.zeros((len(valid), len(D))) for nm, _, D in sets}
        for j, k in enumerate(valid):
            allD = np.concatenate([RSb[k] @ self.rot(C, k, mem) @ D.T for _, mem, D in sets], axis=1).T
            rr = skin_exit(B, k, allD); o = 0
            for nm, _, D in sets: E[nm][j] = rr[o:o + len(D)]; o += len(D)
        self.valid = valid; self.env_secs = time.time() - t0
        q = p["pct"]; c = p["clear"]
        env = {nm: (np.percentile(v, q, axis=0) if len(valid) else np.full(v.shape[1], 60.0)) for nm, v in E.items()}
        self.env = env
        mx = lambda nm: float(env[nm].max()) if nm in env and env[nm].size else -np.inf
        e_fl = max(mx("j1fl0"), mx("j1fl1"))
        pitch = self.pitch
        if p["top"] == "nested":
            self.RS = max(mx("scap") + c, mx("l1") + c - pitch, mx("band") + c - 2 * pitch, e_fl + c + self.fl)
            self.RB = self.RS + 2 * pitch
        else:
            self.RS = max(mx("scap") + c, mx("l1") + c - pitch, e_fl + c + self.fl)
            self.RB = max(mx("band") + c, self.RS + 2 * pitch)
        self.RH = max(mx("saddle") + c, mx("armend") + c - pitch)
        if p["arm_layer"] == "over":                                            # the arm-end pair rides above the top stack
            self.RH = max(self.RH, self.RB + p["t"] + self.fl + 1.0)
        elif p["arm_layer"] == "under":                                         # ... or the top stack above the arm end
            lift = self.RH + pitch + p["t"] + self.fl + 1.0 + self.fl - self.RS
            if lift > 0: self.RS += lift; self.RB += lift
        self.RA = self.RH + pitch
        if p["arm_layer"] == "band_over":                                       # the band (L2) passes over the arm-end pair + J3 flanges
            need = self.RA + p["t"] + self.fl + 0.5
            if need > self.RB:
                if p["top"] == "nested": self.RS += need - self.RB
                self.RB = need
        if self.strap is not None:                                              # ramp from the arm end to the band, >= env + c
            Dst, st, ss, fr, wS = self.strap; nst = len(ss)
            es = np.full(nst, -np.inf); np.maximum.at(es, st, env["strap"] + c)
            ramp = np.interp(ss, [ss[0], ss[-1]], [self.RA, self.RB]); self.strap_prof = np.maximum(ramp, es)
        Dsb, stb, ssb, frb, wb = self.stub
        eb = np.full(len(ssb), -np.inf); np.maximum.at(eb, stb, env["stub"] + c); self.stub_prof = eb

    # ---- parts of one pose (member-local), then S frame
    def parts_local(self):
        p = self.p; t = p["t"]; P = {}
        for nm, (mem, D, keep, bas, rho) in self.G.items():
            R = dict(scap=self.RS, l1=self.RS + self.pitch, band=self.RB, armend=self.RA, saddle=self.RH)[nm]
            if nm == "band":
                A1 = p["A1"] * D2R; hw = self.hwB; lo, hi = self.bandaz
                def foot(u, m, A1=A1, hw=hw, lo=lo, hi=hi, bas=bas):
                    pl, az, _ = sph(u, *bas); mm = np.max(m) / D2R / math.sin(A1) if np.size(m) else 0.0
                    return (np.abs(pl - A1) <= hw + m) & in_arc(az, lo - mm, hi + mm)
            else:
                foot = lambda u, m, bas=bas, rho=rho: sph(u, *bas)[0] <= rho + m
            P[nm] = shell_part(nm, mem, D, keep, R, t, foot)
        fl_h = self.fl; rd = p["roller_d"] / 2; fd = p["flange_d"] / 2
        for k, d in enumerate(self.j1_dirs):                                     # J1: roller down through the S cap, flange below
            P[f"j1fl{k}"] = cyl_part(f"j1fl{k}", "L1", d, fd, self.RS - fl_h, self.RS, face=True)
            P[f"j1rol{k}"] = cyl_part(f"j1rol{k}", "L1", d, rd, self.RS, self.RS + self.pitch, face=False)
        for k, d in enumerate(self.j2_dirs):                                     # J2: roller up through the band, flange on top
            r_l1top = self.RS + self.pitch + t
            if self.RB - r_l1top > p["g"] + 0.01:
                P[f"j2post{k}"] = cyl_part(f"j2post{k}", "L1", d, 3.0, r_l1top, self.RB, face=False)
            P[f"j2rol{k}"] = cyl_part(f"j2rol{k}", "L1", d, rd, self.RB - p["g"], self.RB + t, face=False)
            P[f"j2fl{k}"] = cyl_part(f"j2fl{k}", "L1", d, fd, self.RB + t, self.RB + t + fl_h, face=False)
        for k, d in enumerate(self.j3_dirs):
            P[f"j3rol{k}"] = cyl_part(f"j3rol{k}", "H", d, rd, self.RH + t, self.RA + t, face=False)
            P[f"j3fl{k}"] = cyl_part(f"j3fl{k}", "H", d, fd, self.RA + t, self.RA + t + fl_h, face=False)
        if self.strap is not None:
            Dst, st, ss, fr, wS = self.strap; P["strap"] = prof_part("strap", "L2", Dst, st, ss, fr, self.strap_prof, t, wS)
        Dsb, stb, ssb, frb, wb = self.stub; P["stub"] = prof_part("stub", "H", Dsb, stb, ssb, frb, self.stub_prof, p["stub_t"], wb)
        return P

    def pose_parts(self, C, k, PL=None):
        """{name: (face points S (k,3), other points S, member)} for chain index k"""
        PL = PL or self.parts_local(); out = {}
        for nm, pt in PL.items():
            R = self.rot(C, k, pt.member); out[nm] = (pt.face() @ R.T, pt.other @ R.T, pt.member, R)
        return out, PL


def _base(nm):
    return nm.rstrip("0123456789")


def interference(Dz, C, k, PL, posed):
    """first interfering pair or '' (non-adjacent members >= 1 mm, adjacent >= 0.2 mm outside their joint)"""
    names = list(PL)
    for a_i, a in enumerate(names):
        A = PL[a]
        for b in names[a_i + 1:]:
            Bp = PL[b]
            if A.member == Bp.member: continue
            key = tuple(sorted((A.member, Bp.member), key=MEMBERS.index))
            if key in ADJ:
                if (_base(a), _base(b)) in JOINT_EXEMPT or (_base(b), _base(a)) in JOINT_EXEMPT: continue
                m = 0.2
            else: m = 1.0
            if A.r_hi + m < Bp.r_lo or Bp.r_hi + m < A.r_lo: continue
            fa, oa, _, Ra = posed[a]; fb, ob, _, Rb = posed[b]
            XA = np.r_[fa, oa]; XB = np.r_[fb, ob]
            if Bp.inside(XA @ Rb, m).any() or A.inside(XB @ Ra, m).any(): return f"{a}/{b}"
    return ""


# ---------------------------------------------------------------- model on the bench
class Model:
    def __init__(self, p, B, log=print):
        self.B = B; self.D = Design(p, B, log); self.p = self.D.p
        if not self.D.invalid: self._clips()

    def _clips(self):
        """continuity on every frame of every fit clip (10 fps): followed iff kinematically ok and no joint jump > FLIP
        since the last followed frame"""
        D = self.D; C = D.C_all; self.status = {}
        for cid in FIT_IDS:
            ix = np.nonzero(CID == cid)[0]; last = None
            for j in ix:
                why = D._kin_ok(C, j)
                if why: self.status[int(j)] = why; continue
                q = np.array([C["th1"][j], C["phig"][j], C["th3"][j]])
                if last is not None and np.abs(wrap(q - last)).max() > FLIP: self.status[int(j)] = "flip"; last = q; continue
                self.status[int(j)] = ""; last = q

    def metal(self, i, detail=False):
        B = self.B; D = self.D
        if D.invalid: return None, "invalid: " + D.invalid
        why = self.status.get(int(B.idx[i]), "missing") if B.kind[i] == "clip" else D.kin[i]
        if why: return None, why
        C = D.Cb; posed, PL = D.pose_parts(C, i, getattr(self, "_PL", None)); self._PL = PL
        w = interference(D, C, i, PL, posed)
        if w: return None, "interference " + w
        RSi = RS_ALL[B.idx[i]]
        face = np.concatenate([v[0] for v in posed.values()]) @ RSi.T
        other = np.concatenate([v[1] for v in posed.values()]) @ RSi.T
        if detail: return (face, other, posed), ""
        do = B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        return face, ""

    def run(self):
        B = self.B; B.reset(); why = {}
        for i in range(len(B.poses)):
            P, w = self.metal(i)
            if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
            d = B.record(i, P)
            if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        r = B.report(); r["why"] = why; return r


_CACHE = {}


def metal(pose, frames, params):
    """task API: metal sample points (k, 3) in the thorax frame for one bench pose, or None. The design is fitted per
    params on a bench: params['_bench'] (default Bench(60, 160)); the pose is looked up in it."""
    B = params.get("_bench") or _CACHE.setdefault("_B", CB.Bench(60, 160))
    q = {k: v for k, v in params.items() if not k.startswith("_")}; key = json.dumps(q, sort_keys=True)
    if _CACHE.get("key") != key: _CACHE["key"] = key; _CACHE["M"] = Model(q, B)
    i = next(j for j, x in enumerate(B.poses) if x == pose)
    return _CACHE["M"].metal(i)[0]


# ---------------------------------------------------------------- evaluation / sweep
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KEYS = ("b_az", "b_el", "w_d", "w_az", "A1", "A2", "n1", "g1a", "g1b", "n2", "d2", "D2", "n3", "g3a", "g3b", "wB", "t", "cov_ws", "pct", "top", "arm_layer", "clear")


def evaluate(p, B):
    t = time.time(); M = Model(p, B); D = M.D
    if D.invalid: return dict(invalid=D.invalid, secs=round(time.time() - t, 1))
    r = M.run()
    r.update(RS=round(D.RS, 1), RB=round(D.RB, 1), RH=round(D.RH, 1), rhoS=round(D.rhoS / D2R, 1), rho1=round(D.rho1 / D2R, 1),
             rho3=round(D.rho3 / D2R, 1), bandw=round(2 * D.hwB * R_TOP, 1), band_arc=round(D.bandaz[1] - D.bandaz[0], 1),
             spans=[round(s["hi"] - s["lo"]) for s in D.slots1 + D.slots2 + D.slots3], fit_closure=round(D.fit_closure, 3),
             strap=round(D.strap_len / D2R, 1), secs=round(time.time() - t, 1), env_secs=round(D.env_secs, 1))
    return r


def sweep(configs, B, out=SWEEP_OUT, tag=""):
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r = evaluate(p, B)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        if "invalid" in r:
            print(f"[--] invalid: {r['invalid']} | " + " ".join(f"{k}={p[k]}" for k in KEYS), flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], mode=r["mode"], stage=tag,
                   shape={k: r[k] for k in ("RS", "RB", "RH", "rhoS", "rho1", "rho3", "bandw", "band_arc", "spans", "fit_closure", "strap")})
        rows.append(row); os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | RS {r['RS']} RB {r['RB']} RH {r['RH']} spans {r['spans']} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in KEYS), flush=True)
    return rows


def named_poses(B):
    """bench indices of 4 named poses: rest (lowest elevation clip frame), overhead (highest elevation), across the body
    (largest plane angle with elev 60-120), behind the back (Reach back pocket, last third)"""
    P = np.array([[q["plane"], q["elev"], q["axial"]] for q in B.poses]); kc = np.array(B.kind) == "clip"
    ix = np.arange(len(P)); out = {}
    out["rest"] = int(ix[kc][np.argmin(P[kc, 1])]); out["overhead"] = int(np.argmax(P[:, 1]))
    m = (P[:, 1] > 60) & (P[:, 1] < 120); out["across"] = int(ix[m][np.argmax(P[m, 0])])
    bp = [j for j in ix if B.clip[j] == "Reach back pocket"]; out["behind"] = int(bp[2 * len(bp) // 3]) if bp else int(np.argmin(P[:, 0]))
    return out


COLORS = dict(scap="#1f77b4", l1="#2ca02c", band="#d62728", strap="#ff7f0e", armend="#9467bd", saddle="#8c564b", stub="#e377c2",
              j1fl="#17becf", j1rol="#17becf", j2rol="#bcbd22", j2fl="#bcbd22", j2post="#bcbd22", j3rol="#7f7f7f", j3fl="#7f7f7f")


def plot(p, B, out_png):
    """side (x-y) and back (z-y) views of the metal on the skin (|v| < 140 mm) at the 4 named poses"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    M = Model(p, B); D = M.D; names = named_poses(B)
    fig, axs = plt.subplots(2, 4, figsize=(16, 8.4))
    for c, (lab, i) in enumerate(names.items()):
        V, _ = B.skin(i); V = np.asarray(V); V = V[np.linalg.norm(V, axis=1) < 140][::3]
        C = D.Cb; posed, PL = D.pose_parts(C, i); RSi = RS_ALL[B.idx[i]]
        _, why = M.metal(i)
        for r, (ax_i, ax_j, ttl) in enumerate(((0, 1, "side: x anterior, y up"), (2, 1, "front: z lateral, y up"))):
            ax = axs[r, c]; ax.scatter(V[:, ax_i], V[:, ax_j], s=0.3, c="#bbbbbb", alpha=0.5, lw=0)
            for nm, (fc, oc, mem, R) in posed.items():
                X = np.r_[fc, oc] @ RSi.T
                ax.scatter(X[:, ax_i], X[:, ax_j], s=0.6, c=COLORS.get(_base(nm), "k"), lw=0, label=_base(nm) if r == 0 and c == 0 else None)
            ax.set_aspect("equal"); ax.set_xlim(-110, 110); ax.set_ylim(-90, 130); ax.grid(alpha=0.2)
            q = B.poses[i]
            ax.set_title(f"{lab} ({B.clip[i][:18]}; plane {q['plane']:.0f} elev {q['elev']:.0f} ax {q['axial']:.0f})\n{ttl}; "
                         + ("taken" if not why else why), fontsize=7.5)
    h, l = axs[0, 0].get_legend_handles_labels(); seen = {}
    for hh, ll in zip(h, l): seen.setdefault(ll, hh)
    fig.legend(list(seen.values()), list(seen.keys()), loc="lower center", ncol=8, markerscale=12, fontsize=8)
    fig.suptitle(f"{ID}: R_S {D.RS:.1f}  R_B {D.RB:.1f}  R_H {D.RH:.1f} mm (skin grey, metal coloured by part)", fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97)); fig.savefig(out_png, dpi=110); plt.close(fig)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        B = CB.Bench(n_clip=nc, n_ws=nw); print("bench", B.mode, len(B.poses))
        r = evaluate(dict(PARAMS), B); print(json.dumps(r, indent=0, default=str))
    elif a[0] == "sweep":                    # sweep [A|B|C]: coarse -> one-at-a-time around the best -> local random
        stage = a[1] if len(a) > 1 else "A"; B = CB.Bench(n_clip=60, n_ws=160); print("bench", B.mode, len(B.poses), flush=True)
        rows = json.load(open(SWEEP_OUT)) if os.path.exists(SWEEP_OUT) else []
        best = min(rows, key=lambda r: r["gap"])["params"] if rows else dict(PARAMS)
        if stage == "A":
            cfg = [dict(AXES[ax], top=top, arm_layer=al, cov_ws=cv, pct=pc) for ax in ("r18", "r20") for top in ("nested", "post")
                   for al in ("env", "over", "band_over") for cv in (0.0, 0.95) for pc in (100.0, 95.0)]
        elif stage == "B":
            base = {k: best[k] for k in PARAMS}
            var = [dict(pct=x) for x in (85.0, 90.0, 97.0, 100.0)] + [dict(cov_ws=x) for x in (0.9, 0.97, 0.99)]
            var += [dict(g1a=x, g1b=y) for x, y in ((6.0, 17.0), (10.0, 21.0), (12.0, 23.0))] + [dict(n1=1, g1a=x) for x in (8.0, 10.0, 12.0)]
            var += [dict(g3a=x, g3b=y) for x, y in ((6.0, 16.0), (10.0, 19.0))] + [dict(n3=1, g3a=x) for x in (8.0, 10.0)]
            var += [dict(D2=x) for x in (20.0, 40.0)] + [dict(n2=2, d2=x) for x in (5.0, 7.0)] + [dict(wB=x) for x in (20.0, 34.0)]
            var += [dict(t=x) for x in (1.5, 2.5)] + [dict(clear=x) for x in (1.5, 3.0)] + [dict(sing=x) for x in (3.0, 10.0)]
            var += [dict(top=x) for x in ("nested", "post") if x != base["top"]] + [dict(arm_layer=x) for x in ("env", "over", "under", "band_over") if x != base["arm_layer"]]
            cfg = [dict(base, **v) for v in var]
        else:                                # C: local random around the best of A + B (one-at-a-time winners combined)
            rng = np.random.default_rng(int(a[2]) if len(a) > 2 else 0); base = {k: best[k] for k in PARAMS}; cfg = []
            for _ in range(int(a[3]) if len(a) > 3 else 30):
                q = dict(base)
                q["pct"] = float(np.clip(base["pct"] + rng.choice([-5, -2.5, 0, 2.5]), 80, 100))
                q["cov_ws"] = float(rng.choice([0.9, 0.95, 0.97, 0.98]))
                q["g1a"] = float(base["g1a"] + rng.choice([-2, 0, 2])); q["g1b"] = q["g1a"] + float(rng.choice([11, 12, 13]))
                q["g3a"] = float(base["g3a"] + rng.choice([-2, 0, 2])); q["g3b"] = q["g3a"] + float(rng.choice([9, 10, 11]))
                q["D2"] = float(np.clip(base["D2"] + rng.choice([-10, 0, 10]), 16, 44)); q["wB"] = float(np.clip(base["wB"] + rng.choice([-4, 0, 4]), 18, 40))
                q["clear"] = float(rng.choice([1.5, 2.0, 2.5])); q["t"] = float(rng.choice([1.5, 2.0]))
                for k, dv in (("b_az", 10), ("b_el", 5), ("w_d", 6), ("w_az", 8), ("A1", 4), ("A2", 4)):
                    q[k] = round(float(base[k] + rng.uniform(-dv, dv)), 2)
                cfg.append(q)
        sweep(cfg, B, tag=stage)
    elif a[0] == "plot":
        B = CB.Bench(n_clip=60, n_ws=160); p = json.loads(a[1]) if len(a) > 1 else dict(PARAMS)
        os.makedirs(os.path.join(REPO, "docs", "concepts", "img"), exist_ok=True)
        plot(p, B, os.path.join(REPO, "docs", "concepts", "img", ID + ".png"))
