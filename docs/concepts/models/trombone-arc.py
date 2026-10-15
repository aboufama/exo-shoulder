"""trombone-arc: one curved Ti band (on the arm-side member) sliding through a swivelling guide on top of the scapula.
3 ACTIVE DOF, 0 passive (the user's liner / optional self-aligning cuff slides stay outside the count, as for the baseline).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre (a spherical 3R):
    S  (scapula base on the user's handler) = lower housing of the J1 ring
    J1 swivel about b (S-fixed axis): a thin-section ring (KAA15XL0 class, 38.1 x 47.6 x 4.76, in housings ->
       annulus 18-27 mm from the b axis, 6 mm axial) flat on the S-top skin; its upper race carries
    L1 the guide (keep-out box 30 along the band x 22 across x [R_a-3, R_a+7] radial, needle cam-follower pairs) joined
       to the upper race by two arms across the band (inside the ring bore)
    J2 rotation about p2: the band is a circle about p2 at polar angle A1 (b lies on it), so sliding it through the guide
       IS a rotation about p2 (p2 fixed in L1 and in L2). No metal at p2's pierce point.
    L2 the band (10 wide x 4 radial Ti, constant radius R_a from GH: a rigid body turning about an axis through GH keeps
       every point's distance to GH, so a band that slides through ONE guide must sit at one radius) + a connector strap
       (8 x 3, the baseline's link section) from the band's arm-side end to J3
    J3 O20 v5 hub about W (humerus-fixed): keep-out disc r 10 x 12.25 stack; lower member = the arm-side BOTTOM stub
       (the baseline's 25 deg x 8 mm neck strap toward the humerus axis), upper member = the connector.
DOF: J1 (swivel), J2 (band position), J3 (hub) - three rotations about b, p2, W, all through GH. W is fixed in S by the arm,
p2 follows from the two-circle closure (angle A1 to b, A2 to W) on the design's branch, so all three joint values are
unique functions of the arm pose: 3 active, no spare, nothing sags unpowered.

Spec changes (stated in docs/concepts/trombone-arc.md):
  * ring-band clearance: the spec's "R_a >= z1 + 9" lets the spherical band dip into the flat ring where it crosses the
    annulus (the band at radius R_a is only sqrt(R_a^2 - rho^2) high over the b axis at lateral rho); enforced here:
    R_a >= sqrt((z1 + 6 + 1)^2 + 27^2) (1 mm over the ring top at its outer edge) and R_a - 3 >= the guide's own fit.
  * the guide box (30 x 22, diagonal 37 mm) does not reach the ring race (bore 38): two 10 mm arms join it to the upper
    race across the band; guide + arms face the skin through the bore and are sampled.
  * skin radius under a sample = the FIRST exit of the body along the ray (not the outermost skin as in
    concept_baseline.skin_radius): the band's tail runs toward the neck / head, where the outermost-skin rule would put
    the band outside the head. Contact anywhere along the metal is still caught by the bench distance.
  * the guide's angular half-length is taken at a nominal 56 mm (conservative when R_a > 56: the arc is longer than
    needed); the arc's ends are set by the guide positions the poses need (fit clips, optionally + workspace share).
  * connector / neck: shaped straps (per-sample fitted profile), ends lifted onto the J3 levels (lower member skin
    face R_W, upper member + 6.15 = the baseline's stack + plate).

Geometry (idealised; every skin-facing face sampled on a ~2 mm grid = 1 point / 4 mm2, tools/concept_baseline.py):
  band underside (radius R_a), ring underside (flat, axial height z1 over the b-axis plane), guide + arms underside
  (flat, R_a - 3), J3 hub underside (cap at R_W), connector + neck undersides (per-sample profile). Top / side faces
  (band top, guide top + sides, ring top + rims, hub crown + rim) are checked for contact only (any inside -> contact).
Fit (the baseline's rule): per sample, the p-th percentile over the kinematically valid bench poses of the skin radius /
height under it, + 2 mm. Flat / constant-radius parts take the max over their samples (the band optionally a
quantile qs over its samples + an offset dR: trading a few contact poses for in-band, as the baseline's p does).
Taken (bench rules): closure on the branch with the band evaluator's 10 deg singularity margin; the guide inside the
arc (both ends); fit-clip frames followed on EVERY 10 fps frame of the clip (no joint jump > FLIP deg since the last
followed frame); no interference >= 1 mm between parts without a joint between them (ring vs band analytic; others by
2 mm samples with a 2 mm threshold = 1 mm clearance + sampling allowance); no metal inside the body.

    python3 docs/concepts/models/trombone-arc.py check     # default config on Bench(20, 40) + pose checks
    python3 docs/concepts/models/trombone-arc.py sweep     # coarse -> refine sweep on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "trombone-arc"
D2R = math.pi / 180
SP = 2.0                     # sample grid mm (1 point / 4 mm2)
FLIP = 30.0                  # deg per 10 fps frame: larger joint jump = branch flip (as seed-arc-rails)
UP = 6.15                    # baseline: upper member over lower member at a joint (stack 3.15 + 3 mm plate)
HUB_R, HUB_H = 10.0, 12.25   # O20 v5 hub keep-out
GAP_PART = 2.0               # mm between samples of parts without a joint between them (1 mm clearance + sampling)
R_NOM = 56.0                 # mm: radius at which the guide's angular half-length is taken (conservative)
Y_ARM = np.array([0.0, -1.0, 0.0])

PARAMS = dict(az=2.43, el=80.68, A1=76.9, A2=66.75, wd=86.33, wa=21.83, branch=-1, sing=10.0,
              ws_cov=0.0, p=95.0, qs=1.0, dR=0.0, clear=2.0, width=10.0, band_t=4.0,
              j1="ring", ring_ri=18.0, ring_ro=27.0, ring_t=6.0, guide_L=30.0, guide_W=22.0, guide_dn=3.0, guide_up=7.0,
              link_w=8.0, link_t=3.0, neck_deg=25.0)
SWEEP = dict(az=(0, 60), el=(60, 90), A1=(60, 95), A2=(60, 95), wd=(55, 95), wa=(-20, 30), branch=(-1, 1),
             ws_cov=(0, 0.95), p=(80, 100), qs=(0.85, 1.0), dR=(-4, 4), width=(8, 12), j1=("ring", "hub"))


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def circ_int(c1, r1, c2, r2, sign):                                          # = concept_baseline.circ_int
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 0


def basis(u):
    """two unit vectors completing u (3,) or (n, 3) to a right-handed frame"""
    ref = np.where(np.abs(u[..., 0:1]) < 0.9, np.array([1.0, 0, 0]), np.array([0, 0, 1.0]))
    a = unit(np.cross(u, ref)); return a, np.cross(u, a)


def arc_dirs(u, v, width, r_ref):
    """strap on the great circle u -> v (n, 3): unit dirs (n, ns, nc, 3), sampled every SP mm at r_ref"""
    ang = np.arccos(np.clip((u * v).sum(-1), -1, 1)); amax = float(ang.max())
    ns = max(3, int(amax * r_ref / SP) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); th = s[None, :] * ang[:, None]
    D = np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None]
    cs = np.arange(-width / 2, width / 2 + 1e-6, SP) / r_ref
    return unit(D[:, :, None, :] * np.cos(cs)[None, None, :, None] + nrm[:, None, None, :] * np.sin(cs)[None, None, :, None])


def disc_dirs(u, rad, r_ref, step=SP):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rad ** 2
    X, Y = X[k] / r_ref, Y[k] / r_ref; a, c = basis(u)
    return unit(u[:, None] + X[None, :, None] * a[:, None] + Y[None, :, None] * c[:, None])


def first_exit(B, i, O, U, t0=12.0, t1=230.0):
    """distance t along rays O + t U (thorax, (k, 3)) of the first exit from the body after t0; rays that start
    outside fall back to the outermost skin (inward trace from t1). 0 if none."""
    k = len(U); t = np.full(k, t0); act = np.ones(k, bool); out = np.zeros(k)
    d0 = B.dist(i, O + t[:, None] * U); start_out = d0 > 0.3; act &= ~start_out
    for _ in range(80):
        if not act.any(): break
        a = np.nonzero(act)[0]; d = B.dist(i, O[a] + t[a, None] * U[a])
        done = d >= -0.3; out[a[done]] = t[a[done]]; act[a[done]] = False
        t[a[~done]] += np.maximum(-d[~done], 0.5)
        far = t > t1; out[far & act] = 0.0; act &= ~far
    if start_out.any():                                                     # outermost skin, as the baseline
        a = np.nonzero(start_out)[0]; t2 = np.full(len(a), t1); live = np.ones(len(a), bool); hit = np.zeros(len(a), bool)
        for _ in range(80):
            if not live.any(): break
            j = np.nonzero(live)[0]; d = B.dist(i, O[a[j]] + t2[j, None] * U[a[j]])
            dn = d < 0.3; hit[j[dn]] = True; live[j[dn]] = False; t2[j[~dn]] -= np.maximum(d[~dn], 0.5)
            low = t2 < t0; live &= ~low
        out[a] = np.where(hit, t2, 0.0)
    return out


_TOK = itertools.count()


class Design:
    def __init__(self, p, B, HG, RS, clipstat):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.n = len(HG)
        self.b = bvec(p["az"], p["el"]); self.W0 = w_dir(p["wd"], p["wa"]); self.A1 = p["A1"] * D2R; self.A2 = p["A2"] * D2R
        self.ba, self.bc = basis(self.b); self.wa_, self.wc_ = basis(self.W0)
        self.gh = (p["guide_L"] / 2) / (R_NOM * math.sin(self.A1)) / D2R    # guide half-length in band azimuth (deg)
        self.K = self.ik(HG); self.token = next(_TOK)
        self.range_from(clipstat)
        self.status = clipstat.status(self)                                # {pose-file row: (ok, why)} for fit-clip frames
        K = self.K; self.valid = np.zeros(self.n, bool); self.why = [""] * self.n
        for i in range(self.n):
            if B.kind[i] == "clip":
                ok, w = self.status.get(int(B.idx[i]), (False, "missing"))
            else:
                ok = bool(K["ok"][i]); w = "closure" if not ok else ""
                if ok and not self.in_arc(K["phi"][i:i + 1])[0]: ok, w = False, "off arc"
            self.valid[i] = ok; self.why[i] = w
        self.fit()

    # ---- kinematics --------------------------------------------------------------------------------------------
    def ik(self, HG):
        p = self.p; b = np.broadcast_to(self.b, (len(HG), 3)); W = HG @ self.W0
        p2, ok = circ_int(b, self.A1, W, self.A2, float(p["branch"]))
        sep = np.arccos(np.clip(W @ self.b, -1, 1)); s = p["sing"] * D2R
        ok &= (sep >= abs(self.A1 - self.A2) + s) & (sep <= min(self.A1 + self.A2, 2 * math.pi - self.A1 - self.A2) - s)
        e2 = unit(W - (W * p2).sum(-1, keepdims=True) * p2); e3 = np.cross(p2, e2)
        phi = np.arctan2(e3 @ self.b, e2 @ self.b) / D2R                  # guide position along the band (J2)
        m = unit(p2 - (p2 @ self.b)[:, None] * self.b)                    # guide orientation about b (J1)
        q1 = np.arctan2(m @ self.bc, m @ self.ba) / D2R
        p2h = np.einsum("nji,nj->ni", HG, p2)                              # p2 in the humerus frame (J3 about W0)
        q3 = np.arctan2(p2h @ self.wc_, p2h @ self.wa_) / D2R
        return dict(p2=p2, W=W, e2=e2, e3=e3, phi=phi, q=np.stack([q1, phi, q3], 1), ok=ok, sep=sep / D2R)

    def range_from(self, cs):
        """band extent from the guide positions the fit clips need (+ a central share of the workspace poses)"""
        K = cs.kin(self); ph = K["phi"][K["ok"]]
        self.sgn = 1.0 if (np.median(ph) if len(ph) else 1.0) >= 0 else -1.0
        ph = self.sgn * ph; lo, hi = (ph.min(), ph.max()) if len(ph) else (30.0, 120.0)
        c = self.p["ws_cov"]
        if c > 0:
            w = np.array([k == "ws" for k in self.B.kind]) & self.K["ok"]; pw = self.sgn * self.K["phi"][w]
            if len(pw): ql, qh = np.quantile(pw, [(1 - c) / 2, 1 - (1 - c) / 2]); lo, hi = min(lo, ql), max(hi, qh)
        self.ph_lo, self.ph_hi = float(lo - self.gh), float(hi + self.gh)  # band ends (deg, L2 frame, signed by sgn)

    def in_arc(self, phi):
        s = self.sgn * np.asarray(phi)
        return (s >= self.ph_lo + self.gh - 1e-6) & (s <= self.ph_hi - self.gh + 1e-6)

    # ---- geometry: directions (S frame) per pose ---------------------------------------------------------------
    def band_dirs(self, idx, r_ref=58.0):
        K = self.K; e1 = K["p2"][idx]; e2 = K["e2"][idx]; e3 = self.sgn * K["e3"][idx]
        rc = r_ref * math.sin(self.A1); n_ph = max(3, int((self.ph_hi - self.ph_lo) * D2R * rc / SP) + 1)
        ph = np.linspace(self.ph_lo, self.ph_hi, n_ph) * D2R
        cs = np.arange(-self.p["width"] / 2, self.p["width"] / 2 + 1e-6, SP) / r_ref; th = self.A1 + cs
        C = (np.cos(th)[None, None, :, None] * e1[:, None, None, :]
             + np.sin(th)[None, None, :, None] * (np.cos(ph)[None, :, None, None] * e2[:, None, None, :] + np.sin(ph)[None, :, None, None] * e3[:, None, None, :]))
        self.band_ph = ph / D2R; return C                                     # (n, n_ph, n_c, 3)

    def static(self):
        """S-fixed / member-fixed lateral grids"""
        p = self.p; g = np.arange(-p["ring_ro"], p["ring_ro"] + 1e-6, SP); X, Y = np.meshgrid(g, g); X, Y = X.ravel(), Y.ravel()
        rho = np.hypot(X, Y)
        if p["j1"] == "ring":
            k = (rho >= p["ring_ri"]) & (rho <= p["ring_ro"]); self.ring_xy = np.c_[X[k], Y[k]]
            inner = p["ring_ri"]
        else:                                                               # O20 hub at b: a disc r 10
            k = rho <= HUB_R; self.ring_xy = np.c_[X[k], Y[k]]; inner = 1e9
        # guide (+ arms across the band to the race), in (s along band, c across) coordinates, inside the bore
        gs = np.arange(-p["guide_L"] / 2, p["guide_L"] / 2 + 1e-6, SP); gc = np.arange(-p["ring_ro"], p["ring_ro"] + 1e-6, SP)
        S_, C_ = np.meshgrid(gs, gc); S_, C_ = S_.ravel(), C_.ravel()
        box = (np.abs(C_) <= p["guide_W"] / 2) | ((np.abs(S_) <= 5.0) & (np.abs(C_) <= p["ring_ri"] + 1))
        keep = box & (np.hypot(S_, C_) <= inner)
        if p["j1"] == "hub": keep = (np.abs(C_) <= p["guide_W"] / 2) & (np.hypot(S_, C_) > HUB_R)
        self.guide_sc = np.c_[S_[keep], C_[keep]]

    def guide_frame(self, idx):
        """guide tangent t (along the band at b) and across m, (n, 3) each, S frame"""
        p2 = self.K["p2"][idx]; m = unit(p2 - (p2 @ self.b)[:, None] * self.b); t = np.cross(self.b, m)
        return t, m

    def neck_dirs(self, idx):
        W = self.K["W"][idx]; harm = self.HG[idx] @ Y_ARM; ng = self.p["neck_deg"] * D2R
        v = unit(math.cos(ng) * W + math.sin(ng) * unit(harm - (harm * W).sum(-1, keepdims=True) * W))
        return arc_dirs(W, v, self.p["link_w"], 58.0)

    def conn_dirs(self, idx):
        K = self.K; e1 = K["p2"][idx]; e2 = K["e2"][idx]; e3 = self.sgn * K["e3"][idx]; a = self.ph_lo * D2R
        u = unit(math.cos(self.A1) * e1 + math.sin(self.A1) * (math.cos(a) * e2 + math.sin(a) * e3))
        return arc_dirs(u, K["W"][idx], self.p["link_w"], 58.0)

    def dirs(self, idx):
        """all radial / axial sample geometry for poses idx (S frame)"""
        b = self.b; t, m = self.guide_frame(idx); n = len(idx)
        G = dict(band=self.band_dirs(idx), conn=self.conn_dirs(idx), neck=self.neck_dirs(idx),
                 hub=np.einsum("nij,kj->nki", self.HG[idx], disc_dirs(self.W0[None], HUB_R, 58.0)[0]))   # humerus-fixed disc
        G["ring_q"] = np.broadcast_to(self.ring_xy[:, 0:1] * self.ba + self.ring_xy[:, 1:2] * self.bc, (n, len(self.ring_xy), 3))
        G["guide_q"] = self.guide_sc[None, :, 0:1] * t[:, None] + self.guide_sc[None, :, 1:2] * m[:, None]
        return G

    # ---- envelope fit ------------------------------------------------------------------------------------------
    def fit(self):
        p = self.p; B = self.B; self.static(); v = np.nonzero(self.valid)[0]; self.vidx = v
        if len(v) < 3: self.dead = "too few valid poses"; return
        self.dead = ""
        G = self.dirs(np.arange(self.n)); self.G = G
        names = ("band", "conn", "neck", "hub"); R = {k: [] for k in names + ("ring_q", "guide_q")}
        for i in v:
            RSi = self.RS[i]; Ds = []; sizes = []
            for k in names:
                D = G[k][i].reshape(-1, 3); Ds.append(D); sizes.append(len(D))
            Dall = np.concatenate(Ds) @ RSi.T
            rr = first_exit(B, int(i), np.zeros_like(Dall), Dall); o = 0
            for k, s in zip(names, sizes): R[k].append(rr[o:o + s]); o += s
            for k in ("ring_q", "guide_q"):
                Q = G[k][i] @ RSi.T; U = np.broadcast_to(RSi @ self.b, Q.shape)
                R[k].append(first_exit(B, int(i), Q, U, t0=8.0))
        self.Rraw = {k: np.array(x) for k, x in R.items()}; self.set_fit()

    def set_fit(self, **kw):
        """radii from the stored skin radii (kw: p, qs, dR, clear override the design's fit parameters)"""
        self.p.update(kw); p = self.p; R = self.Rraw; G = self.G
        if self.dead: return
        pc = lambda k: np.percentile(R[k], p["p"], axis=0) + p["clear"]
        self.z1 = float(pc("ring_q").max())                                 # ring / J1 hub underside (axial height along b)
        zg = float(pc("guide_q").max()) if R["guide_q"].shape[1] else 0.0
        band = pc("band"); Ra = float(np.quantile(band, p["qs"])) + p["dR"]
        if p["j1"] == "ring":
            need = math.sqrt((self.z1 + p["ring_t"] + 1.0) ** 2 + p["ring_ro"] ** 2)
            self.zg = None; Ra = max(Ra, need, zg + p["guide_dn"])
        else:                                                               # guide = the hub's upper member, band over the crown
            need = math.sqrt((self.z1 + HUB_H + 1.0) ** 2 + HUB_R ** 2)
            self.zg = max(zg, self.z1 + 3.15); Ra = max(Ra, need)
        self.Ra = Ra; self.RW = float(pc("hub").max())
        nk = pc("neck").reshape(G["neck"].shape[1:3]); e = max(2, nk.shape[0] // 6)
        nk[:e] = np.maximum(nk[:e], self.RW); self.prof_neck = nk.reshape(-1)
        cn = pc("conn").reshape(G["conn"].shape[1:3]); e = max(2, cn.shape[0] // 6)
        cn[:e] = np.maximum(cn[:e], Ra); cn[-e:] = np.maximum(cn[-e:], self.RW + UP); self.prof_conn = cn.reshape(-1)
        self.band_prof_raw = band

    # ---- per-pose metal ----------------------------------------------------------------------------------------
    def parts(self, i):
        """dict part -> (skin-facing samples (k, 3), other surface samples (m, 3)), S frame"""
        p = self.p; G = self.G; b = self.b
        out = {}
        D = G["band"][i]; Ra = self.Ra
        face = (D * Ra).reshape(-1, 3); top = np.concatenate([D[:, 0], D[:, -1], D[0], D[-1]]) * (Ra + p["band_t"])
        out["band"] = (face, np.r_[top, (D[:, ::2] * (Ra + p["band_t"])).reshape(-1, 3)])
        Dc = G["conn"][i].reshape(-1, 3); out["conn"] = (Dc * self.prof_conn[:, None], Dc * (self.prof_conn[:, None] + p["link_t"]))
        Dn = G["neck"][i].reshape(-1, 3); out["neck"] = (Dn * self.prof_neck[:, None], Dn * (self.prof_neck[:, None] + p["link_t"]))
        Dh = G["hub"][i]; out["hub"] = (Dh * self.RW, Dh * (self.RW + HUB_H))
        q = G["ring_q"][i]
        if p["j1"] == "ring":
            ring = q + self.z1 * b; rtop = q + (self.z1 + p["ring_t"]) * b
            out["ring"] = (ring, np.r_[rtop, ring[::3] + 3.0 * b])
            gq = G["guide_q"][i]; gl = self.Ra - p["guide_dn"]
            out["guide"] = (gq + gl * b, np.r_[gq + (self.Ra + p["guide_up"]) * b, self._guide_sides(i, gl)])
        else:
            out["ring"] = (q + self.z1 * b, q + (self.z1 + HUB_H) * b)
            gq = G["guide_q"][i]; out["guide"] = (gq + self.zg * b, np.r_[gq + (self.Ra + p["guide_up"]) * b, self._guide_sides(i, self.zg)])
        return out

    def _guide_sides(self, i, z0):
        p = self.p; t, m = self.guide_frame(np.array([i])); t, m = t[0], m[0]; L, Wd = p["guide_L"] / 2, p["guide_W"] / 2
        zs = np.arange(z0, self.Ra + p["guide_up"] + 1e-6, SP); pts = []
        for s in np.arange(-L, L + 1e-6, SP):
            for c in (-Wd, Wd): pts.append(s * t + c * m)
        for c in np.arange(-Wd, Wd + 1e-6, SP):
            for s in (-L, L): pts.append(s * t + c * m)
        P = np.array(pts); return (P[:, None, :] + zs[None, :, None] * self.b).reshape(-1, 3)

    def interfere(self, P, i):
        """1 mm between parts with no joint between them; returns '' or the pair"""
        p = self.p
        # ring (S) vs band (L2), analytic in the band's spherical coordinates about p2
        Q = np.r_[P["ring"][0], P["ring"][1]]; K = self.K
        e1 = K["p2"][i]; e2 = K["e2"][i]; e3 = self.sgn * K["e3"][i]
        r = np.linalg.norm(Q, axis=1); th = np.arccos(np.clip(Q @ e1 / r, -1, 1)); ph = np.arctan2(Q @ e3, Q @ e2) / D2R
        hw = p["width"] / 2 / self.Ra
        dr = np.maximum.reduce([self.Ra - r, r - self.Ra - p["band_t"], np.zeros_like(r)])
        dt = np.maximum(np.abs(th - self.A1) - hw, 0) * r
        dp = np.maximum.reduce([self.ph_lo - ph, ph - self.ph_hi, np.zeros_like(r)]) * D2R * r * np.sin(th)
        if np.sqrt(dr ** 2 + dt ** 2 + dp ** 2).min() < 1.0: return "ring-band"
        pairs = (("ring", "conn"), ("ring", "hub"), ("ring", "neck"), ("guide", "hub"), ("guide", "neck"), ("band", "neck"), ("band", "hub"))
        nc = self.G["band"].shape[2]
        for a, c in pairs:
            A = np.r_[P[a][0], P[a][1]]; C = np.r_[P[c][0], P[c][1]]
            if a == "band" and c == "hub": A = P[a][0][3 * nc:]                # the band's first 6 mm carry the connector to the hub
            ca, cc = A.mean(0), C.mean(0)
            if np.linalg.norm(ca - cc) > np.linalg.norm(A - ca, axis=1).max() + np.linalg.norm(C - cc, axis=1).max() + 5: continue
            if cKDTree(C).query(A, k=1)[0].min() < GAP_PART: return f"{a}-{c}"
        return ""

    def metal(self, i, detail=False):
        if self.dead or not self.valid[i]: return (None, self.why[i] or self.dead) if not detail else (None, self.why[i] or self.dead, None)
        P = self.parts(i); w = self.interfere(P, i)
        if w: return (None, "interference " + w) if not detail else (None, "interference " + w, None)
        RSi = self.RS[i]
        face = np.concatenate([v[0] for v in P.values()]) @ RSi.T; other = np.concatenate([v[1] for v in P.values()]) @ RSi.T
        do = self.B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        if detail:
            lab = np.concatenate([[k] * len(v[0]) for k, v in P.items()])
            return face, "", lab
        return face, ""


# ---------------------------------------------------------------- clip continuity on every 10 fps frame
class ClipStatus:
    def __init__(self):
        Z = CB._poses_all(); self.names = list(Z["NAMES"]); self.cid = Z["CID"]; self.HG = Z["HG"].astype(float)
        self.rows = {n: np.nonzero(self.cid == self.names.index(n))[0] for n in CB.FIT}; self._k = {}; self._s = {}

    def kin(self, D):
        if D.token not in self._k:
            ix = np.concatenate(list(self.rows.values())); self._k = {D.token: D.ik(self.HG[ix])}
        return self._k[D.token]

    def status(self, D):
        if D.token in self._s: return self._s[D.token]
        K = self.kin(D); st = {}; o = 0
        for n, ix in self.rows.items():
            last = None
            for k, jj in enumerate(ix):
                kk = o + k
                if not K["ok"][kk]: st[int(jj)] = (False, "closure"); continue
                if not D.in_arc(K["phi"][kk:kk + 1])[0]: st[int(jj)] = (False, "off arc"); continue
                q = K["q"][kk]
                if last is not None and np.abs(wrapd(q - last)).max() > FLIP: st[int(jj)] = (False, "flip"); continue
                st[int(jj)] = (True, ""); last = q
            o += len(ix)
        self._s = {D.token: st}; return st


def run(p, B, HG, RS, cs, D=None):
    t = time.time()
    if D is None: D = Design(p, B, HG, RS, cs)
    else: D.set_fit(**{k: p[k] for k in ("p", "qs", "dR", "clear")})
    B.reset(); why = {}
    lab_in = {}; tail = []
    for i in range(len(B.poses)):
        P, w, lab = D.metal(i, detail=True)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None); continue
        d = B.record(i, P)
        if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        elif B.kind[i] == "clip":
            for k in np.unique(lab):
                dk = d[:len(lab)][lab == k]; a = lab_in.setdefault(k, [0, 0, 0]); a[0] += int(((dk >= 2) & (dk <= 14)).sum()); a[1] += len(dk)
                a[2] += int(((dk >= 2) & (dk <= 10)).sum())
        if not D.dead and D.valid[i]: tail.append((D.ph_hi - D.sgn * D.K["phi"][i]) * D2R * D.Ra * math.sin(D.A1) - D.p["guide_L"] / 2)
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1)
    if not D.dead:
        r["shape"] = dict(Ra=round(D.Ra, 1), band_raw=[round(float(D.band_prof_raw.min()), 1), round(float(D.band_prof_raw.max()), 1)],
                          z1=round(D.z1, 1), RW=round(D.RW, 1), arc=[round(D.ph_lo, 1), round(D.ph_hi, 1)],
                          arc_mm=round((D.ph_hi - D.ph_lo) * D2R * D.Ra * math.sin(D.A1), 0),
                          tail_mm=[round(float(np.min(tail)), 0), round(float(np.max(tail)), 0)] if tail else None,
                          kin_valid=round(float(D.valid.mean()), 3))
        r["parts"] = {k: dict(ib14=round(v[0] / max(v[1], 1), 3), ib10=round(v[2] / max(v[1], 1), 3), share=round(v[1] / max(1, sum(x[1] for x in lab_in.values())), 3))
                      for k, v in lab_in.items()}
    else:
        r["shape"] = dict(dead=D.dead)
    return r, D


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _cache:
        Z = CB._poses_all(); _cache.clear(); _cache[key] = Design(prm, B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float), ClipStatus())
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KEYS = ("az", "el", "A1", "A2", "wd", "wa", "branch", "ws_cov", "p", "qs", "dR", "width", "j1")


def sweep(configs, B, out=SWEEP_OUT, tag=""):
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); cs = ClipStatus()
    rows = json.load(open(out)) if os.path.exists(out) else []
    D = None; kin_key = None
    for p in configs:
        p = dict(PARAMS, **p); kk = json.dumps({k: v for k, v in p.items() if k not in ("p", "qs", "dR", "clear")}, sort_keys=True)
        try:
            r, D = run(p, B, HG, RS, cs, D if (kk == kin_key and D is not None) else None); kin_key = kk
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); D = None; kin_key = None; continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"], parts=r.get("parts"),
                   mode=r["mode"], stage=tag)
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r.get('parts')} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in KEYS), flush=True)
    return rows


def sketch(p, B, png, poses=None):
    """matplotlib sketch: skin near the shoulder (grey) + the metal coloured by distance to the skin, at rest and overhead"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    D = Design(p, B, HG, RS, ClipStatus())
    ok = [i for i in range(len(B.poses)) if D.valid[i]]
    el = np.array([B.poses[i]["elev"] for i in ok])
    if poses is None: poses = [ok[int(np.argmin(el))], ok[int(np.argmax(el))]]
    fig = plt.figure(figsize=(12, 6))
    for k, i in enumerate(poses):
        ax = fig.add_subplot(1, len(poses), k + 1, projection="3d")
        V, F = B.skin(i); V = np.asarray(V); s = V[np.linalg.norm(V, axis=1) < 130][::6]
        ax.scatter(s[:, 2], s[:, 0], s[:, 1], s=0.3, c="0.75", alpha=0.35)
        P, w, lab = D.metal(i, detail=True)
        if P is not None:
            d = B.dist(i, P)[:len(lab)]; P = P[:len(lab)]
            sc = ax.scatter(P[:, 2], P[:, 0], P[:, 1], s=2, c=np.clip(d, 0, 20), cmap="viridis_r", vmin=0, vmax=20)
        ax.set_title(f"pose {i} ({B.kind[i]}): elev {B.poses[i]['elev']:.0f} plane {B.poses[i]['plane']:.0f} axial {B.poses[i]['axial']:.0f}"
                     + ("" if P is not None else f" - not taken: {w}"), fontsize=8)
        ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_xlim(-60, 120); ax.set_ylim(-90, 90); ax.set_zlim(-90, 90); ax.view_init(18, -60)
    if P is not None: fig.colorbar(sc, ax=fig.axes, shrink=0.6, label="metal to skin, mm")
    fig.suptitle(f"{ID}: R_a {D.Ra:.1f} mm, arc {D.ph_lo:.0f}..{D.ph_hi:.0f} deg", fontsize=10)
    fig.savefig(png, dpi=110); plt.close(fig); return D


R18 = dict(az=32.55, el=80.56, A1=77.41, A2=81.45, wd=71.38, wa=4.78, branch=-1)   # catalogue's champion (cad_r18_n3_s1392_1_f300)
FITV = [dict(p=pp, qs=q) for pp in (90.0, 95.0, 100.0) for q in (1.0, 0.95, 0.9)]


def best_rows(out=SWEEP_OUT, n=1):
    rows = json.load(open(out)) if os.path.exists(out) else []
    return sorted(rows, key=lambda r: r["gap"])[:n]


def stage_a():
    cf = []
    for kin in ({}, R18):
        for wc in (0.0, 0.9):
            cf += [dict(kin, ws_cov=wc, **v) for v in FITV]
    return cf


def stage_b(best, steps):
    """one coordinate pass around best (each with the fit variants that matter)"""
    cf = []; base = {k: best[k] for k in KEYS if k in best}
    for k, dv in steps:
        for sgn in (-1, 1):
            c = dict(base); c[k] = round(c[k] + sgn * dv, 2)
            cf += [dict(c, p=pp, qs=q) for pp, q in ((95.0, 1.0), (100.0, 1.0), (95.0, 0.95))]
    return cf


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=int(os.environ.get("NC", 20)), n_ws=int(os.environ.get("NW", 40)))
        print("bench mode", B.mode, len(B.poses))
        sweep([dict(PARAMS)], B, out=os.path.join(os.environ.get("TA_TMP", "/tmp"), "trombone_check.json"), tag="check")
    elif a[0] == "sweep":
        B = CB.Bench(n_clip=60, n_ws=160); print("bench mode", B.mode, len(B.poses), flush=True)
        st = a[1] if len(a) > 1 else "A"
        if st == "A": sweep(stage_a(), B, tag="A coarse: two champion axis sets x arc range x fit")
        elif st.startswith("B"):
            b0 = best_rows()[0]["params"]
            steps = [("az", 12), ("el", 5), ("A1", 6), ("A2", 6), ("wd", 8), ("wa", 10)]
            sweep(stage_b(b0, steps), B, tag="B axis coordinate pass")
        elif st == "C":
            b0 = best_rows()[0]["params"]; cf = []
            for v in (dict(j1="hub"), dict(width=8.0), dict(width=12.0), dict(branch=-b0["branch"])):
                cf += [dict(b0, **v, p=pp, qs=q) for pp, q in ((95.0, 1.0), (100.0, 1.0), (95.0, 0.95))]
            sweep(cf, B, tag="C realisation: J1 hub, band width, branch")
        elif st == "D":
            b0 = best_rows()[0]["params"]
            cf = [dict(b0, p=pp, qs=q, dR=dr) for pp in (90.0, 95.0, 100.0) for q in (1.0, 0.95, 0.9, 0.8) for dr in (-2.0, 0.0)]
            sweep(cf, B, tag="D fit refine")
    elif a[0] == "sketch":
        B = CB.Bench(n_clip=60, n_ws=160); b0 = best_rows()[0]["params"]
        sketch(b0, B, os.path.join(REPO, "docs", "concepts", "img", ID + ".png"))
