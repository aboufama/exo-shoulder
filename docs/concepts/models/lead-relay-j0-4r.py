"""lead-relay-j0-4r (round 103, lens 1 'relay under the lead', 4 counted joints): the verified lead conecut-knee-knuckle-3r
UNCHANGED from J1 to the cuff (SN_CELL=lead, row best_params, frozen shape fitted on Bench(60,160) fast), with J1's housing
no longer bolted to the scapula handler but carried by a fourth O20 v5 hub (hub 0, joint J0) through link 0.

  J0   axis c through GH, a0 deg from J1's axis u1 at azimuth azu in u1's frame (ef = u1 x y, ff = u1 x ef); spring-centred
       (preloaded double-leg torsion spring, q0 = 0 at rest) with own-angle dowel stops q0 in [lo, hi] (ISO 8734 2 m6 440C in
       an arc groove of hub 0's lower plate). Hub 0 is GROUNDED metal (its stator bolts to a post of the scapula handler):
       an O20 x 12.25 cylinder on c, underside at r0 = the lowest radius that clears (a) the skin by 2 mm on every fit-bench
       pose and (b) every chain sample by 1 mm on every fit-bench pose the lead takes (q0 = 0). r0 is DERIVED, never free.
  link 0  12 x 3 Ti-6Al-4V bar, rigid with J1's housing (member 0 of the lead, so it turns with q0): bolted under hub 0's
       rotor plate (a pad over the whole plate), running flat to a turned standoff post on J1's housing crown (the post stands
       inside hub 1's footprint, clear of hub K's sweep; the flat bar has climb 0).
       Its underside is skin-facing metal (in-band, skin); hub 0's underside samples it hides are dropped.

Relay kinematics (per pose): the chain sees Q' = Rc(q0)^T Q (Q = humerus rotation in the scapula frame), every member is
then turned by Rc(q0). Policy (ii) = the spring-centred clamp: q0 = 0 wherever the lead's chain closes (the lead's own
kin_ok), else the least |q0| inside the stop window [lo, hi] at which the chain closes (lead IK, knee window, closure
< 0.5 deg, J3 stop, |dK| <= dK_lim) with the J0-J1-J3 sub-chain >= 5 deg from its own fold. A relayed pose whose metal enters
the skin is a CONTACT (a spring-centred J0 cannot refuse the relay); one whose parts clash is lost ('parts', the kit rule);
one whose needed q0 is outside [lo, hi] is lost ('stop').

The window [lo, hi] is chosen on the FIT bench Bench(60,160) fast (policy (ii) composed for every (lo, hi) pair), never on
the claim bench; the claim wears that window frozen on exact Bench(110,360) (CB_EXACT=1). Every number is reported twice:
REAL (hub 0 + link 0 as metal: in-band, skin, part clash) and GHOST (zero-size J0, the proposer's idealisation).

DOF: 4 counted joints (J0 spring-centred + J1 J2 J3 active; the user prefers 3), K slaved, knee pins passive rotations
outside the count, 0 passive translations. No gears / pulleys / cables.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-j0-4r.py window [a0] [azu]      # fit bench, picks [lo, hi]
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-j0-4r.py claim a0 azu lo hi [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("cc_for_leadrelay", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
ID = "lead-relay-j0-4r"
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
P_LEAD = CC._clamp(dict(CC.PARAMS, **ROW))
FROZ = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
        "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info")
HUB_R, HUB_H = 10.0, 12.25                                    # O20 v5 stack (docs/HARDWARE.md)
BAR_W, BAR_T = 12.0, 3.0                                      # link 0: 12 x 3 Ti-6Al-4V
SKIN_CLR, PART_CLR = 2.0, 1.0
GROUND = 100                                                  # member id of hub 0's stator (never relayed)
_Z0 = CB._poses_all(); ZD = {k: _Z0[k] for k in _Z0.files}


def wr(a): return (a + 180.0) % 360.0 - 180.0
def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rot_mats(c, q_deg):
    a = np.radians(np.asarray(q_deg, float)); c = unit(c); K = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * K[None] + (1 - np.cos(a))[:, None, None] * (K @ K)[None]


def sd_cyl(X, cen, ax, r=HUB_R, h=HUB_H):
    w = X - cen; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1); dr = rr - r; dz = np.maximum(-z, z - h)
    return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))


def frame_of(a):
    a = unit(a); e = unit(np.cross(a, [1.0, 0, 0] if abs(a[0]) < 0.9 else [0, 1.0, 0])); return e, np.cross(a, e)


def fit_lead():
    """the lead's frozen shape: fit on Bench(60,160) FAST (CB_EXACT popped for the fit, as the claim protocol does)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = CC.CCModel(B1, dict(P_LEAD)); r1 = M1.run()
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    return M1, P2, {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}


def relay_axis(u1, a0, azu):
    ef = unit(np.cross(u1, [0.0, 1.0, 0.0])); ff = np.cross(u1, ef); ar, br = math.radians(a0), math.radians(azu)
    return unit(math.cos(ar) * u1 + math.sin(ar) * (math.cos(br) * ef + math.sin(br) * ff))


def make_model(M1, P2, B, Rc=None, extras=None):
    """the frozen lead on bench B; Rc: {bench index: 3x3 relay rotation} (the chain sees Rc^T Q, members turn by Rc);
    extras: dict(hub0=(cen, axis, under_pts, wall_pts), link0=pts on member 0) -> appended metal + clash + skin log"""
    Zm = dict(ZD)
    if Rc:
        HG = ZD["HG"].copy()
        for i, R in Rc.items():
            gi = int(B.idx[i]); HG[gi] = (R.T @ HG[gi].astype(float)).astype(HG.dtype)
        Zm["HG"] = HG
    old = CB._poses_all; CB._poses_all = lambda: Zm
    try:
        class Relay(CC.CCModel):
            def fit(self):
                for a in FROZ:
                    if hasattr(M1, a): setattr(self, a, getattr(M1, a))
                self._sc = None; self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]
                self.drop = np.zeros(len(self.poses_fit), bool); self._truncate()
                self.xlog = {}

            def T(self, m, i):
                if m == GROUND: return np.eye(3), np.zeros(3)
                R, t = super().T(m, i)
                if Rc and i in Rc: Rr = Rc[i]; return Rr @ R, Rr @ t
                return R, t

            def extra_pts(self, i):
                if not extras: return np.zeros((0, 3))
                R0, t0 = self.T(0, i)
                return np.concatenate([extras["hub0"][2], extras["link0"] @ R0.T + t0])

            def metal_points(self, i):                          # chain metal first (same order as the lead), extras last
                return np.concatenate([super().metal_points(i), self.extra_pts(i) @ self.RS[i].T])

            def collide(self, i):                               # the lead's checks; the extras' clash is LOGGED (composed later)
                out = super().collide(i)
                if extras:
                    cen, ax = extras["hub0"][0], extras["hub0"][1]; R0, t0 = self.T(0, i); G0 = extras["G"]
                    G = dict(mid=G0["mid"] @ R0.T + t0, post=G0["post"] @ R0.T + t0)
                    cmin = 1e9; who = None; lmin = 1e9; lwho = None
                    for k, X, h in member_pts(self, i):
                        d = float(sd_cyl(X, cen, ax).min()) - h
                        if d < cmin: cmin, who = d, k
                        if self._mem.get(k) == 0: continue          # link 0's own body (J1's housing, hub 1)
                        dd = link0_clear(G, X, h)
                        if dd < lmin: lmin, lwho = dd, k
                    wall = float(self.B.dist(i, extras["hub0"][3] @ self.RS[i].T).min())
                    self.xlog[i] = dict(hub0_clear=round(cmin, 2), hub0_who=who, link0_clear=round(lmin, 2), link0_who=lwho, hub0_wall=round(wall, 2))
                return out
        M = Relay(B, dict(P2))
    finally:
        CB._poses_all = old
    M.fit()
    M._mem = {k: m for k, (m, X) in list(M.cyl_surf.items()) + list(M.rigid.items()) + list(M.strap.items())}
    M.n_chain = None
    return M


def member_pts(M, i):
    """every chain sample at pose i in the scapula frame: hub surfaces, rigid parts, link straps (half thickness 1.5)"""
    out = []
    for k, (m, X) in M.cyl_surf.items(): R, t = M.T(m, i); out.append((k, X @ R.T + t, 0.0))
    for k, (m, X) in M.rigid.items():
        if k.startswith("hub"): continue
        R, t = M.T(m, i); out.append((k, X @ R.T + t, 0.0))
    for k, (m, X) in M.strap.items(): R, t = M.T(m, i); out.append((k, np.asarray(X) @ R.T + t, 1.5))
    return out


class Kin:
    """the lead's kinematic test on a batch of humerus rotations Q (the proposer's kin.Kin, reproduces kin_ok)"""
    def __init__(s, M, dK_lim): s.M = M; s.D = M.D; s.P = M.p; s.dK_lim = dK_lim

    def ok(s, Q):
        D, P = s.D, s.P
        q, ok, X1, X2, X3, sv = D.ik(Q); K = D.knee(sv)
        kok = K["ok"] & (np.abs(sv[:, 2]) <= P["R_tol"])
        c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; res = np.degrees(np.arccos(np.clip(c, -1, 1)))
        q3p = wr(np.degrees(q[:, 2] + K["phi"])); lo, hi = float(P["J3MIN"]), float(P["J3MAX"])
        st = (q3p >= lo) & ((q3p <= hi) if hi < 180 else True)
        dk = np.abs(np.asarray(D._dK, float))
        return ok & kok & (res < 0.5) & st & (dk <= s.dK_lim + 1e-9)


def seat_ok(U):
    U = np.atleast_2d(U); e = np.degrees(np.arcsin(np.clip(U[:, 1], -1, 1))); az = np.degrees(np.arctan2(U[:, 2], -U[:, 0]))
    return (az >= -110) & (az <= 135) & (e >= -20) & (U[:, 0] <= 0.20)


def link0_geom(M1, c, r0):
    """link 0 at hub-0 underside r0: a turned standoff POST on J1's housing crown (r 6, along u1, inside hub 1's footprint)
    up to the bar plane, then a flat 12 x 3 BAR under hub 0's rotor plate from the post top to hub 0's axis (climb 0:
    the bar is perpendicular to the bisector of c and u1). The post is a machined standoff (no bend rule applies)."""
    u1 = M1.D.u[0]; f1 = float(M1.f[0]); h = r0 - BAR_T / 2
    P1 = h * u1; P2 = h * c; L = float(np.linalg.norm(P2 - P1)); d = (P2 - P1) / L
    nrm = unit(c + u1); side = unit(np.cross(d, nrm))
    ss = np.arange(0.0, L + HUB_R - 1 + 1e-6, 2.0); ww = np.arange(-BAR_W / 2 + 1, BAR_W / 2, 2.0)   # pad under the whole rotor plate
    mid = np.array([P1 + s_ * d + w * side for s_ in ss for w in ww])
    under = mid - (BAR_T / 2) * nrm
    z1 = under @ u1; lat1 = np.linalg.norm(under - z1[:, None] * u1, axis=1)
    skin = under[lat1 >= HUB_R]                                # over hub 1's crown the bar is hidden (not skin-facing)
    post = np.array([z * u1 for z in np.arange(f1 + HUB_H, h + 1e-6, 1.0)])
    return dict(mid=mid, skin=skin, post=post, P1=P1, P2=P2, L=L, d=d, side=side, post_h=round(h - f1 - HUB_H, 1))


def link0_clear(G, X, h):
    from scipy.spatial import cKDTree
    if not len(X): return 1e9
    T = cKDTree(X)
    return min(float(T.query(G["mid"])[0].min()) - h - BAR_T / 2, float(T.query(G["post"])[0].min()) - h - 6.0)


def build_extras(M1, c, log=print):
    """hub 0 (grounded O20 on c) + link 0 (post + bar on J1's housing). r0 from the FIT bench only: hub 0's disc >= 2 mm
    off the skin on every pose; hub 0 and link 0 >= 1 mm off every chain sample on every pose the lead takes (q0 = 0)."""
    B1 = M1.B; u1 = M1.D.u[0]; e, f = frame_of(c); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    rim = np.array([r * (math.cos(a) * e + math.sin(a) * f) for r in (5.0, 10.0) for a in ang] + [np.zeros(3)])
    tk = [i for i in range(len(B1.idx)) if B1.res[i] is not None and float(np.min(B1.res[i])) >= 0]
    pts = [member_pts(M1, i) for i in tk]
    mem = {k: m for k, (m, X) in list(M1.cyl_surf.items()) + list(M1.rigid.items()) + list(M1.strap.items())}
    r0 = None
    for r in np.arange(38.0, 130.0, 0.5):
        if any(float(B1.dist(i, (r * c + rim) @ M1.RS[i].T).min()) < SKIN_CLR for i in range(len(B1.idx))): continue
        if any(float(sd_cyl(X, r * c, c).min()) - h < PART_CLR for P_ in pts for k, X, h in P_): continue
        G = link0_geom(M1, c, float(r))
        if any(link0_clear(G, X, h) < PART_CLR for P_ in pts for k, X, h in P_ if mem.get(k) != 0): continue
        r0 = float(r); break
    if r0 is None: raise RuntimeError("no hub-0 underside <= 130 mm clears the skin and the chain")
    G = link0_geom(M1, c, r0)
    import concept_kit as CK
    dxy = CK.disc_xy(HUB_R, 2.0); und = r0 * c + dxy[:, :1] * e + dxy[:, 1:] * f
    w_ = und - G["P1"]; s_ = w_ @ G["d"]; lat_ = np.abs(w_ @ G["side"])
    und = und[~((s_ >= 0) & (s_ <= G["L"] + HUB_R) & (lat_ <= BAR_W / 2))]   # the bar covers these (not skin-facing)
    wall = np.array([r0 * c + z * c + HUB_R * (math.cos(a) * e + math.sin(a) * f) for z in (0.0, 4.0, 8.0, HUB_H) for a in ang]
                    + [(r0 + HUB_H) * c + x * e + y * f for x, y in dxy])
    log(f"hub0: r0 {r0} (crown {r0 + HUB_H}), underside samples {len(und)}; link0 bar {G['L']:.1f} mm, {len(G['skin'])} skin samples, post {G['post_h']} mm")
    return dict(hub0=(r0 * c, c, und, wall), link0=G["skin"], G=G, r0=r0, link_len=round(G["L"], 1), climb=0.0, post_h=G["post_h"],
                n_x=len(und) + len(G["skin"]))


def relay_candidates(M0, c, a0, B, poses, T=60.0):
    """per pose: (q-, q+) = the feasible q0 nearest 0 on each side (policy (ii) in any window), None if none"""
    D = M0.D; u1 = D.u[0]; w = D.u[2]; QG = np.arange(-T, T + 0.01, 1.0)
    U1 = np.einsum("nij,j->ni", rot_mats(c, QG), u1); so = seat_ok(U1); i0 = int(np.argmin(np.abs(QG))); trav = np.zeros(len(QG), bool)
    k = i0
    while k < len(QG) and so[k]: trav[k] = True; k += 1
    k = i0
    while k >= 0 and so[k]: trav[k] = True; k -= 1
    Kn = Kin(M0, float(M0._scg["dK_lim"])); Qall = ZD["HG"][B.idx].astype(float)
    poses = np.asarray(poses, int); R_all = rot_mats(c, QG); U3 = Qall[poses] @ w
    F = np.zeros((len(poses), len(QG)), bool); TH = np.zeros((len(poses), len(QG)))
    for kq in range(len(QG)):
        if not trav[kq] or QG[kq] == 0: continue
        F[:, kq] = Kn.ok(np.einsum("ji,njk->nik", R_all[kq], Qall[poses]))
        TH[:, kq] = np.degrees(np.arccos(np.clip(U3 @ (R_all[kq] @ u1), -1, 1)))
    g = np.degrees(np.arccos(np.clip(U3 @ c, -1, 1))); SUB = np.minimum(g[:, None] - np.abs(a0 - TH), a0 + TH - g[:, None])
    F2 = F & (SUB >= 5.0)
    out = {}
    for j, i in enumerate(poses):
        ks = np.nonzero(F2[j])[0]
        if not len(ks): continue
        qs = QG[ks]; qn = qs[qs < 0]; qp = qs[qs > 0]
        out[int(i)] = (float(qn.max()) if len(qn) else None, float(qp.min()) if len(qp) else None,
                       float(SUB[j, ks].min()), float(TH[j, ks[np.argmin(np.abs(qs))]]))
    return out, float(min(abs(QG[trav].min()), QG[trav].max()))


def eval_pose(M, B, i):
    """the lead's run() logic for one pose (part clash -> lost; metal + contact-list samples vs the skin)"""
    cl = M.collide(i)
    if cl < PART_CLR: return dict(st="parts", cl=round(cl, 2), res=None)
    d = B.dist(i, M.metal_points(i)); dc = min(float(B.dist(i, M.world(m, i, Pc)).min()) for m, Pc in M.contact)
    res = np.r_[d, dc] if dc < 0 else d
    return dict(st="ok", cl=round(cl, 2), res=res)


def wear(B, M1, P2, a0, azu, log=print):
    """REAL + GHOST per-pose records on bench B: q0 = 0 (full run), then the q- / q+ relays of every pose the lead loses"""
    t = time.time(); u1 = M1.D.u[0]; c = relay_axis(u1, a0, azu); X = build_extras(M1, c, log)
    M0 = make_model(M1, P2, B, None, X); r0 = M0.run()
    n_tot = len(M0.metal_points(0)); n_x = X["n_x"]; n_ch = n_tot - n_x
    base = dict(res=list(B.res), why=list(np.asarray(M0.why)), xlog=dict(M0.xlog), kin=np.asarray(M0.kin_ok).copy())
    lost = [i for i in range(len(B.idx)) if i not in set(M0.poses_fit.tolist())]
    cand, Teff = relay_candidates(M0, c, a0, B, lost)
    log(f"q0=0 wear: gap {r0['gap']} reach {r0['reach']} ib14 {r0['inband14']} contact {r0['contact']}; lost {len(lost)}, relay candidates {len(cand)}, Teff {Teff} ({time.time() - t:.0f} s)")
    side = {}
    for sgn, col in (("neg", 0), ("pos", 1)):
        Rc = {i: rot_mats(c, [v[col]])[0] for i, v in cand.items() if v[col] is not None}
        if not Rc: continue
        M2 = make_model(M1, P2, B, Rc, X); pf = set(M2.poses_fit.tolist())
        for i in Rc:
            q = cand[i][col]
            if not M2.kin_ok[i] or i not in pf: side[(i, sgn)] = dict(st="kin", q0=q); continue
            e = eval_pose(M2, B, i); e.update(q0=q, x=M2.xlog.get(i)); side[(i, sgn)] = e
    log(f"relays evaluated: {len(side)} ({time.time() - t:.0f} s)")
    return dict(c=c, X=X, base=base, cand=cand, side=side, n_ch=n_ch, n_x=n_x, Teff=Teff, M0=M0, r_q0=r0)


def compose(B, W, lo, hi, ghost=False):
    """policy (ii) in window [lo, hi]: bench report + bookkeeping. REAL: hub 0 / link 0 samples in the record, their clash
    (< 1 mm) loses the pose, hub 0's wall into the skin is a contact. GHOST: zero-size J0 (extras stripped)."""
    n_ch, n_x = W["n_ch"], W["n_x"]

    def fix(res, x):
        if res is None: return None
        if ghost: return np.r_[res[:n_ch], res[n_ch + n_x:]]
        if x is not None and min(x["hub0_clear"], x["link0_clear"]) < PART_CLR: return "parts"
        if x is not None and x["hub0_wall"] < 0: return np.r_[res, x["hub0_wall"]]
        return res
    out = []; stat = dict(relayed=0, relay_taken=0, relay_contact=0, relay_parts=0, relay_stop=0, x_parts=0, q0=[])
    for i in range(len(B.idx)):
        if i in W["cand"]:
            qn, qp = W["cand"][i][:2]; opts = [(abs(q), s) for q, s in ((qn, "neg"), (qp, "pos")) if q is not None and lo <= q <= hi]
            if not opts: out.append(None); stat["relay_stop"] += 1; continue
            s = min(opts)[1]; e = W["side"].get((i, s))
            if e is None or e["st"] in ("kin", "parts"): out.append(None); stat["relay_parts"] += 1; continue
            r = fix(e["res"], e.get("x")); stat["relayed"] += 1; stat["q0"].append(e["q0"])
            if isinstance(r, str): out.append(None); stat["x_parts"] += 1; continue
            out.append(r)
            if float(np.min(r)) < 0: stat["relay_contact"] += 1
            else: stat["relay_taken"] += 1
        else:
            r = fix(W["base"]["res"][i], W["base"]["xlog"].get(i))
            if isinstance(r, str): out.append(None); stat["x_parts"] += 1; continue
            out.append(r)
    old = B.res; B.res = out
    try: rep = B.report()
    finally: B.res = old
    ws = np.array(B.kind) == "ws"; el = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    tk = np.array([r is not None and float(np.min(r)) >= 0 for r in out]); ct = np.array([r is not None and float(np.min(r)) < 0 for r in out])
    rep.update(ws_taken=int((tk & ws).sum()), contacts=int(ct.sum()), overhead=f"{int((tk & ws & (el >= 140)).sum())}/{int((ws & (el >= 140)).sum())}",
               window=[lo, hi], **{k: v for k, v in stat.items() if k != "q0"},
               q0_range=[min(stat["q0"]), max(stat["q0"])] if stat["q0"] else None)
    rep["_res"] = out
    return rep


def windows(W):
    qs = sorted(set([0.0] + [q for v in W["cand"].values() for q in v[:2] if q is not None]))
    return [(lo, hi) for lo in qs if lo <= 0 for hi in qs if hi >= 0]


def parts_inband(B, W, res):
    """in-band share of hub 0 + link 0 and of the chain over the taken clip frames"""
    n_ch, n_x = W["n_ch"], W["n_x"]; ch = []; xx = []
    for i, r in enumerate(res):
        if B.kind[i] != "clip" or r is None or float(np.min(r)) < 0: continue
        ch.append(r[:n_ch]); xx.append(r[n_ch:n_ch + n_x])
    if not ch: return {}
    a = np.concatenate(ch); b = np.concatenate(xx)
    f = lambda d: [round(float(((d >= 2) & (d <= 14)).mean()), 3), round(float(np.median(d)), 1), round(float(d.min()), 1)]
    return dict(chain=f(a), hub0_link0=f(b))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "window"
    t = time.time(); M1, P2, fit = fit_lead(); print("lead fit (Bench(60,160) fast):", fit, flush=True)
    a0 = float(sys.argv[2]) if len(sys.argv) > 2 and mode != "seats" else 20.0; azu = float(sys.argv[3]) if len(sys.argv) > 3 and mode != "seats" else 45.0
    if mode == "window":
        B = M1.B; W = wear(B, M1, P2, a0, azu)
        rows = []
        for lo, hi in windows(W):
            r = compose(B, W, lo, hi); g = compose(B, W, lo, hi, ghost=True)
            rows.append(dict(lo=lo, hi=hi, gap=r["gap"], ghost=g["gap"], **{k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "ws_taken", "contacts", "relay_taken", "relay_contact")}))
        rows.sort(key=lambda x: (x["gap"], x["hi"] - x["lo"]))
        out = dict(a0=a0, azu=azu, bench="Bench(60,160) " + B.mode, X={k: W["X"][k] for k in ("r0", "link_len", "post_h", "n_x")}, Teff=W["Teff"],
                   q0_wear=dict(gap=W["r_q0"]["gap"]), cand=len(W["cand"]), best=rows[:10], n_windows=len(rows),
                   ghost_best=min(rows, key=lambda x: x["ghost"]), secs=round(time.time() - t))
        print(json.dumps(out, default=float))
        if len(sys.argv) > 4: json.dump(dict(out, rows=rows), open(sys.argv[4], "w"), indent=1, default=float)
    elif mode == "seats":                                      # fit-bench seat scan with REAL metal, best window per seat
        import datetime
        out_json = sys.argv[2]; B = M1.B; u1 = M1.D.u[0]
        log = json.load(open(out_json)) if os.path.exists(out_json) else []
        done = {(e["params"]["a0"], e["params"]["azu"]) for e in log}
        for a0 in (10.0, 15.0, 20.0, 25.0, 30.0, 40.0):
            for azu in (0.0, 30.0, 45.0, 60.0, 90.0, 120.0, 180.0, 240.0, 270.0, 300.0, 330.0):
                if (a0, azu) in done: continue
                c = relay_axis(u1, a0, azu); e = dict(k=len(log), t=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                      params=dict(a0=a0, azu=azu), bench="Bench(60,160) fast")
                if not bool(seat_ok(c)[0]):
                    e.update(status="seat-illegal", gap=None)
                else:
                    try:
                        W = wear(B, M1, P2, a0, azu, log=lambda *x: None)
                        rows = [(compose(B, W, lo, hi), lo, hi) for lo, hi in windows(W)]
                        r, lo, hi = min(rows, key=lambda x: (x[0]["gap"], x[2] - x[1]))
                        g = min(compose(B, W, lo_, hi_, ghost=True)["gap"] for _, lo_, hi_ in rows)
                        e["params"].update(lo=lo, hi=hi, r0=W["X"]["r0"], post_h=W["X"]["post_h"])
                        e.update({k: r[k] for k in ("inband14", "inband10", "reach", "follow", "contact", "gap", "ws_taken", "contacts", "relay_taken", "relay_contact")},
                                 q0_zero_gap=W["r_q0"]["gap"], ghost_gap_best=g, status="ok")
                    except RuntimeError as ex:
                        e.update(status=str(ex)[:80], gap=None)
                log.append(e); json.dump(log, open(out_json, "w"), indent=1, default=float)
                print(json.dumps(e, default=float), flush=True)
    elif mode == "claim":
        lo, hi = float(sys.argv[4]), float(sys.argv[5])
        B = CB.Bench(n_clip=110, n_ws=360); W = wear(B, M1, P2, a0, azu)
        r = compose(B, W, lo, hi); g = compose(B, W, lo, hi, ghost=True); z = compose(B, W, 0.0, 0.0)
        pib = parts_inband(B, W, r["_res"])
        mins = [float(np.min(x)) for x in r["_res"] if x is not None]
        tk = [m for m in mins if m >= 0]
        rel = sorted([dict(i=i, q0=e["q0"], side=s, st=e["st"], x=e.get("x"), dmin=(round(float(np.min(e["res"])), 2) if e.get("res") is not None else None),
                           pose=[B.poses[i][k] for k in ("plane", "elev", "axial")]) for (i, s), e in W["side"].items()], key=lambda d: d["i"])
        out = dict(row=ID, a0=a0, azu=azu, window=[lo, hi], bench=[110, 360], mode=B.mode, fit_fast=fit,
                   real={k: v for k, v in r.items() if k != "_res"}, ghost={k: v for k, v in g.items() if k != "_res"},
                   q0_zero={k: v for k, v in z.items() if k != "_res"}, parts_inband=pib, near_touch_min_mm=round(min(tk), 3) if tk else None,
                   X={k: W["X"][k] for k in ("r0", "link_len", "post_h", "n_x")}, Teff=W["Teff"], relays=rel,
                   xlog_min=dict(hub0=min(v["hub0_clear"] for v in W["base"]["xlog"].values()), link0=min(v["link0_clear"] for v in W["base"]["xlog"].values()),
                                 wall=min(v["hub0_wall"] for v in W["base"]["xlog"].values())), secs=round(time.time() - t))
        print(json.dumps({k: out[k] for k in ("real", "ghost", "q0_zero", "parts_inband", "near_touch_min_mm", "X", "xlog_min", "secs")}, default=float))
        if len(sys.argv) > 6: json.dump(out, open(sys.argv[6], "w"), indent=1, default=float)
