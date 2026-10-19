"""lead-relay-backbridge-4r (round 103 pick 2, lens 1 'relay under the lead', the PASS rule's 'larger a0' clause).

The verified lead conecut-knee-knuckle-3r (frozen shape fitted on Bench(60,160) fast, loaded UNCHANGED) rides on a 4th
counted joint J0: hub 0 (O20 v5, MR117-2RS pair, 12.25 stack) stands on the scapula handler on the back of the shoulder
at a0 from J1 (azimuth azu about u1, outside hub 2's orbit about J1), spring-centred with own-angle dowel stops
[lo, hi]; link 0 (12 x 3 Ti-6Al-4V bent bar) bridges from hub 0's crown over the chain's swept volume to hub 1's crown
(link 1a leaves hub 1 from its lower plate, so the top plate is free for the base side).

4 counted joints (J0 sprung + stopped, J1-J3 active), K slaved, knee pins passive rotations, 0 passive translations.

Relay policy (ii) (judge 103): a workspace pose the lead cannot close at q0 = 0 is relayed to the least |q0| inside the
window at which the chain closes (|dK| <= dK_lim, J3 stop, knee, sub-chain J0-J1-J3 margin >= 5 deg); a relayed pose
whose metal enters the skin is a CONTACT (a spring-centred J0 cannot refuse a relay); a part clash is 'parts'.

What this file adds over the ghost (zero-size J0): hub 0 and link 0 as REAL METAL - in-band samples, skin contact
(underside, wall, crown, link edges) and part clearance against every chain sample on every pose.
  * hub 0 underside r0: lowest radius at which the O20 disc clears the fit-bench skin by 2 mm on every pose and the
    chain samples by 1 mm on every taken fit pose;
  * link 0: stations every ~2 mm of arc along the c -> u1 great circle (or a planform turn through a side point),
    underside at each station = max(fit-bench skin + 2 mm under all 7 lateral samples, highest chain sample within
    the strap's half width + 2 mm laterally + 1 mm + strap half thickness), then the 60-deg climb-ramp envelope; ends
    land on hub 0's and hub 1's crowns.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lead-relay-backbridge-4r.py wear [a0] [azu] [route] [out.json]
    ... bound [out.json]          seat-grid lower bound (hub 0 in-band exact on the claim bench's clip frames,
                                  kinematic upper bound on new takes, link 0 at best case)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("SN_CELL", "lead")
_sp = importlib.util.spec_from_file_location("cc_for_backbridge", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
import concept_bench as CB                                   # noqa: E402
import concept_kit as CK                                     # noqa: E402

ID = "lead-relay-backbridge-4r"
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
P_LEAD = CC._clamp(dict(CC.PARAMS, **ROW))
HUB_R, STACK = 10.0, 12.25
W0, T0 = 12.0, 3.0                                           # link 0 bar width x thickness (mm)
RAMP = 60.0                                                  # climb-ramp limit (CAD ruling 2026-10-16)
SKIN_CLR, PART_CLR = 2.0, 1.0
FROZ_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf",
              "Emid", "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info")
PERPOSE = os.path.join(REPO, "docs", "alignment", "remeasure", "conecut-knee-knuckle-3r_bench_perpose.json")
_Z0 = CB._poses_all(); ZD = {k: _Z0[k] for k in _Z0.files}


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)
def wr(a): return (a + 180.0) % 360.0 - 180.0


def rot_mats(c, q_deg):
    a = np.radians(np.atleast_1d(np.asarray(q_deg, float))); c = unit(c)
    K = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * K[None] + (1 - np.cos(a))[:, None, None] * (K @ K)[None]


def frame_of(a):
    a = unit(a); e = unit(np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0])); return e, np.cross(a, e)


def sd_cyl(Pw, cen, ax, r, h):
    w = Pw - cen; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1); dr = rr - r; dz = np.maximum(-z, z - h)
    return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))


def seat_ok(U):
    """J1 seat rule (back of the shoulder + acromion top only), as the relay ghost used it"""
    U = np.atleast_2d(U); e = np.degrees(np.arcsin(np.clip(U[:, 1], -1, 1))); az = np.degrees(np.arctan2(U[:, 2], -U[:, 0]))
    return (az >= -110) & (az <= 135) & (e >= -20) & (U[:, 0] <= 0.20)


def seat_axis(u1, a0, azu):
    ef = unit(np.cross(u1, [0., 1., 0.])); ff = np.cross(u1, ef); ar, br = math.radians(a0), math.radians(azu)
    return unit(math.cos(ar) * u1 + math.sin(ar) * (math.cos(br) * ef + math.sin(br) * ff))


def travel(c, u1, T=60.0):
    QG = np.arange(-T, T + 0.01, 1.0); so = seat_ok(np.einsum("nij,j->ni", rot_mats(c, QG), u1))
    i0 = int(np.argmin(np.abs(QG))); lo = hi = i0
    while hi + 1 < len(QG) and so[hi + 1]: hi += 1
    while lo - 1 >= 0 and so[lo - 1]: lo -= 1
    return float(QG[lo]), float(QG[hi])


def fit_lead():
    B1 = CB.Bench(n_clip=60, n_ws=160); M1 = CC.CCModel(B1, dict(P_LEAD)); r1 = M1.run()
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]; return M1, P2, r1


class Kin:
    """closure test of the frozen lead at arbitrary humerus rotations (the lead's own ik + knee + J3 stop + dK)"""
    def __init__(s, M, dKlim): s.D = M.D; s.P = M.p; s.dKlim = dKlim

    def ok(s, Q):
        D, P = s.D, s.P
        q, ok, X1, X2, X3, sv = D.ik(Q); K = D.knee(sv)
        kok = K["ok"] & (np.abs(sv[:, 2]) <= P["R_tol"])
        R123 = X3[0]; cc = (np.einsum("nij,nij->n", R123, Q) - 1) / 2; res = np.degrees(np.arccos(np.clip(cc, -1, 1)))
        q3p = wr(np.degrees(q[:, 2] + K["phi"])); lo, hi = float(P["J3MIN"]), float(P["J3MAX"])
        st = (q3p >= lo) & ((q3p <= hi) if hi < 180 else True)
        dk = np.abs(np.asarray(D._dK, float))
        return ok & kok & (res < 0.5) & st & (dk <= s.dKlim + 1e-9)


def relay_candidates(M0, B, c, lo, hi, exclude):
    """policy (ii): per workspace pose not in `exclude`, the least-|q0| in [lo, hi] (1-deg grid) at which the frozen
    chain closes with the J0-J1-J3 sub-chain margin >= 5 deg; returns {bench index: q0}"""
    D = M0.D; u1, w = D.u[0], D.u[2]; a0 = math.degrees(math.acos(float(np.clip(c @ u1, -1, 1))))
    Kn = Kin(M0, float(M0._scg["dK_lim"])); kind = np.array(B.kind)
    Qall = ZD["HG"][B.idx].astype(float); ws = np.array([i for i in np.nonzero(kind == "ws")[0] if i not in exclude], int)
    if not len(ws): return {}
    QG = np.arange(lo, hi + 0.01, 1.0); QG = QG[np.argsort(np.abs(QG), kind="stable")]
    R_all = rot_mats(c, QG); U3 = Qall[ws] @ w; g = np.degrees(np.arccos(np.clip(U3 @ c, -1, 1))); out = {}
    for kq, q in enumerate(QG):
        if abs(q) < 0.5: continue
        left = np.array([j for j in range(len(ws)) if int(ws[j]) not in out], int)
        if not len(left): break
        F = Kn.ok(np.einsum("ji,njk->nik", R_all[kq], Qall[ws[left]]))
        TH = np.degrees(np.arccos(np.clip(U3[left] @ (R_all[kq] @ u1), -1, 1)))
        SUB = np.minimum(g[left] - np.abs(a0 - TH), a0 + TH - g[left])
        for j in left[F & (SUB >= 5.0)]: out[int(ws[j])] = float(q)
    return out


# ---------------------------------------------------------------- hub 0 + link 0 metal -------------------------------
def hub0_metal(c, r0):
    e, f = frame_of(c); D = CK.disc_xy(HUB_R, 2.0)
    under = r0 * c + D[:, :1] * e + D[:, 1:] * f
    ang = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f
    wall = np.concatenate([r0 * c + z * c + HUB_R * ring for z in np.linspace(0, STACK, 5)])
    crown = under + STACK * c
    return under, np.concatenate([wall, crown])


def chain_points(M, i, local=True):
    """every chain sample (hub surfaces, rigid, straps) at pose i, in link 0's frame (local) -> list of (name, X, h)"""
    T = (lambda m: CC.CCModel.T(M, m, i)) if local else (lambda m: M.T(m, i))
    out = []
    for k, (m, X) in M.cyl_surf.items(): R, t = T(m); out.append((k, X @ R.T + t, 0.0))
    for k, (m, X) in M.rigid.items():
        if k.startswith("hub") or k in ("hub0", "link0"): continue
        R, t = T(m); out.append((k, X @ R.T + t, 0.0))
    for k, (m, X) in M.strap.items(): R, t = T(m); out.append((k, np.asarray(X) @ R.T + t, T0 / 2))
    return out


def route_dirs(c, u1, r0, r1, side=0.0, step=2.0):
    """station directions of link 0 from hub 0's rim to hub 1's rim: the c -> u1 great circle, or (side != 0) a planform
    turn through the point `side` deg off the great circle's midpoint (two great-circle arcs, tangent-arc corner not
    modelled: the corner is shorter, so this is the conservative length)"""
    def arc(a, b, n):
        A = math.acos(float(np.clip(a @ b, -1, 1)))
        return np.array([unit(math.sin((1 - t) * A) * a + math.sin(t * A) * b) for t in np.linspace(0, 1, n)]) if A > 1e-6 else a[None]
    if side:
        mid = unit(c + u1); n_ = unit(np.cross(c, u1)); via = unit(math.cos(math.radians(side)) * mid + math.sin(math.radians(side)) * n_)
        pts = np.concatenate([arc(c, via, 200), arc(via, u1, 200)[1:]])
    else: pts = arc(c, u1, 400)
    ra = 0.5 * (r0 + r1)
    keep = (np.degrees(np.arccos(np.clip(pts @ c, -1, 1))) > math.degrees((HUB_R + 0.5) / (r0 + STACK))) & \
           (np.degrees(np.arccos(np.clip(pts @ u1, -1, 1))) > math.degrees((HUB_R + 0.5) / (r1 + STACK)))
    pts = pts[keep]
    s = np.r_[0, np.cumsum(np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", pts[1:], pts[:-1]), -1, 1))))] * math.pi / 180 * ra
    nst = max(3, int(s[-1] / step) + 1); idx = np.searchsorted(s, np.linspace(0, s[-1], nst)).clip(0, len(pts) - 1)
    d = pts[idx]; tg = np.gradient(d, axis=0); lat = unit(np.cross(d, tg))
    return d, lat, np.linspace(0, s[-1], nst)


def fit_link0(M, B1, c, r0, u1, r1, poses_chain, Rq, side=0.0):
    """underside radius per station (see module doc) on the FIT bench; returns (dirs, lat, s, rho)"""
    d, lat, s = route_dirs(c, u1, r0, r1, side)
    offs = np.linspace(-W0 / 2, W0 / 2, 7)
    rr = np.arange(40.0, 130.0, 0.5)
    # skin: lowest radius whose 7 lateral samples clear the fit-bench skin by 2 mm on every fit pose (link 0 frame:
    # relayed poses see the skin rotated by Rq^T)
    need_s = np.full(len(d), 40.0)
    for i in range(len(B1.idx)):
        R = Rq.get(i, np.eye(3))
        X = (rr[None, :, None, None] * d[:, None, None, :] + offs[None, None, :, None] * lat[:, None, None, :])  # st, r, lat, 3
        Xw = (X.reshape(-1, 3) @ R.T) @ M.RS[i].T
        dd = B1.dist(i, Xw).reshape(len(d), len(rr), len(offs)).min(2)
        okr = dd >= SKIN_CLR
        # lowest r such that every r' >= r clears (the bar must not pass through skin above it)
        bad = ~okr; last_bad = np.where(bad.any(1), len(rr) - 1 - np.argmax(bad[:, ::-1], 1), -1)
        r_need = np.where(last_bad >= 0, rr[np.minimum(last_bad + 1, len(rr) - 1)], rr[0])
        need_s = np.maximum(need_s, r_need)
    # chain: highest chain sample within half width + 2 mm laterally of the station line, over all taken fit poses
    need_c = np.zeros(len(d)); dn = unit(d)
    for i in poses_chain:
        for k, X, h in chain_points(M, i, local=True):
            if k == "hub1": continue                         # J1's housing carries link 0 (same body)
            Rn = np.linalg.norm(X, axis=1); Xu = X / Rn[:, None]
            # distance of the chain point from the station's radial line, measured at the point's radius
            cosang = np.clip(Xu @ dn.T, -1, 1); lat_mm = Rn[:, None] * np.sqrt(1 - cosang ** 2)
            near = lat_mm <= W0 / 2 + 2.0 + h
            top = np.where(near, (Rn * 1.0)[:, None] * cosang + PART_CLR + h, 0.0).max(0)
            need_c = np.maximum(need_c, top)
    rho = np.maximum(need_s, need_c)
    # the ends land on the crowns (hub 0 crown r0 + STACK, hub 1 crown r1 + STACK): ramps limited to RAMP deg
    tanr = math.tan(math.radians(RAMP))
    rho[0] = max(rho[0], r0 + STACK); rho[-1] = max(rho[-1], r1 + STACK)
    for _ in range(2):
        for k in range(1, len(rho)): rho[k] = max(rho[k], rho[k - 1] - tanr * (s[k] - s[k - 1]))
        for k in range(len(rho) - 2, -1, -1): rho[k] = max(rho[k], rho[k + 1] - tanr * (s[k + 1] - s[k]))
    return d, lat, s, rho, need_s, need_c


def link0_metal(d, lat, rho):
    offs = np.linspace(-W0 / 2, W0 / 2, 7)
    under = (rho[:, None, None] * d[:, None, :] + offs[None, :, None] * lat[:, None, :]).reshape(-1, 3)
    mid = ((rho + T0 / 2)[:, None, None] * d[:, None, :] + offs[None, :, None] * lat[:, None, :]).reshape(-1, 3)
    top = ((rho + T0)[:, None, None] * d[:, None, :] + offs[None, :, None] * lat[:, None, :]).reshape(-1, 3)
    edge = np.concatenate([(rho + z)[:, None] * d + sgn * (W0 / 2) * lat for z in (0.0, T0 / 2, T0) for sgn in (-1, 1)])
    return under, mid, np.concatenate([top, edge])


# ---------------------------------------------------------------- the relay model ------------------------------------
def make_model(M1, P2, B, c, Rc=None, metal=None):
    """frozen lead on bench B; Rc: {bench index: 3x3} relay rotations; metal: dict(hub0_under, hub0_cont, link0_under,
    link0_mid, link0_cont, r0) in link 0's frame (= scapula frame at q0 = 0)"""
    Rc = Rc or {}; Zm = dict(ZD)
    if Rc:
        HG = ZD["HG"].copy()
        for i, R in Rc.items(): gi = int(B.idx[i]); HG[gi] = (R.T @ HG[gi].astype(float)).astype(HG.dtype)
        Zm["HG"] = HG
    old = CB._poses_all; CB._poses_all = lambda: Zm
    try:
        class Relay(CC.CCModel):
            def fit(self):
                for a in FROZ_ATTRS:
                    if hasattr(M1, a): setattr(self, a, getattr(M1, a))
                self._sc = None; self.contact = list(M1.contact); self.rigid = dict(M1.rigid)
                if metal is not None:
                    self.rigid["hub0"] = (0, metal["hub0_under"]); self.rigid["link0"] = (0, metal["link0_under"])
                    self.contact += [(0, metal["hub0_cont"]), (0, metal["link0_cont"])]
                self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
                self._truncate()

            def T(self, m, i):
                R, t = super().T(m, i)
                if i in Rc: Rr = Rc[i]; return Rr @ R, Rr @ t
                return R, t

            def collide(self, i):
                cl = super().collide(i)
                if metal is None: return cl
                pts = chain_points(self, i, local=True)               # link 0's frame: hub 0 and link 0 are fixed there
                u1 = self.D.u[0]; r1 = float(self.f[0]); mins = {}
                tree = metal["_tree"]
                for k, X, h in pts:
                    if k != "hub1":
                        mins.setdefault("hub0", 1e9)
                        mins["hub0"] = min(mins["hub0"], float(sd_cyl(X, metal["r0"] * c, c, HUB_R, STACK).min()) - h)
                    if k == "hub1": continue
                    # J1 joint: member-1 parts inside hub 1's footprint (+4 mm) run against link 0's end eye (adjacent)
                    w_ = X - r1 * u1; far = np.linalg.norm(w_ - (w_ @ u1)[:, None] * u1, axis=1) > HUB_R + 4
                    if far.any():
                        dd, _ = tree.query(X[far]); mins[f"link0-{k}"] = float(dd.min()) - T0 / 2 - h
                worst = min(mins, key=mins.get); self.last_clear[worst] = round(mins[worst], 1)
                return min(cl, mins[worst])
        M = Relay(B, dict(P2))
    finally:
        CB._poses_all = old
    return M


def build_metal(M1, B1, c, extra_chain_models=()):
    """r0 and link 0's profile on the fit bench; returns the metal dict + a summary"""
    D = M1.D; u1 = D.u[0]; r1 = float(M1.f[0])
    tk = list(np.nonzero(M1.kin_ok)[0])
    # hub 0 underside r0: disc clears the fit skin by 2 mm on every fit pose and the chain samples by 1 mm
    under0, _ = hub0_metal(c, 0.0)
    rr = np.arange(40.0, 130.0, 0.5); r_skin = rr[0]
    for i in range(len(B1.idx)):
        X = np.concatenate([under0 + r * c for r in rr]) @ M1.RS[i].T
        dd = B1.dist(i, X).reshape(len(rr), -1).min(1); bad = dd < SKIN_CLR
        if bad.any(): r_skin = max(r_skin, rr[min(len(rr) - 1, int(np.nonzero(bad)[0].max()) + 1)])
    allc = [np.concatenate([X for k, X, h in chain_points(M1, i) if k != "hub1"]) for i in tk]
    # hub 0 must clear the chain AT its seat: count the taken fit poses whose chain enters hub 0 (+1 mm, + strap half
    # thickness) at r_skin; r_chain = the lowest r >= r_skin with no such pose (None if none up to 130 mm)
    def n_clash(r): return int(sum(float(sd_cyl(X, r * c, c, HUB_R, STACK).min()) < PART_CLR + T0 / 2 for X in allc))
    clash_at_skin = n_clash(r_skin); r_chain = float(r_skin) if clash_at_skin == 0 else None
    if clash_at_skin:
        for r in rr[rr > r_skin]:
            if n_clash(r) == 0: r_chain = float(r); break
    r0 = float(r_skin)                                          # the hub stays at the skin-set seat; clashes are lost poses
    build_metal.clash_at_skin = clash_at_skin
    return r0, float(r_skin), r_chain


def assemble(M1, B1, c, r0, side=0.0, Rq=None, poses_chain=None):
    u1 = M1.D.u[0]; r1 = float(M1.f[0])
    if poses_chain is None: poses_chain = list(np.nonzero(M1.kin_ok)[0])
    d, lat, s, rho, ns, nc = fit_link0(M1, B1, c, r0, u1, r1, poses_chain, Rq or {}, side)
    hu, hc = hub0_metal(c, r0); lu, lm, lc = link0_metal(d, lat, rho)
    metal = dict(hub0_under=hu, hub0_cont=hc, link0_under=lu, link0_mid=lm, link0_cont=lc, r0=r0, _tree=cKDTree(lm))
    # height of link 0's underside over the fit-bench rest skin, per station (rest = pose with the lowest elevation)
    prof = dict(len_mm=round(float(s[-1]), 1), n_st=len(s), rho=[round(float(x), 1) for x in rho],
                skin_need=[round(float(x), 1) for x in ns], chain_need=[round(float(x), 1) for x in nc])
    return metal, prof


def pick_window(M1, P2, B1, c, lo_t, hi_t, metal, lead_taken1):
    """window [lo, hi] picked on the FIT bench: least-|q0| relay candidates, worn with the metal, best fit-bench gap"""
    M0 = make_model(M1, P2, B1, c); M0.fit()
    cand = relay_candidates(M0, B1, c, lo_t, hi_t, set(np.nonzero(lead_taken1)[0].tolist()))
    if not cand: return (0.0, 0.0), dict(cand=0)
    Rq = {i: rot_mats(c, [q])[0] for i, q in cand.items()}
    M2 = make_model(M1, P2, B1, c, Rq, metal); M2.fit()
    st = {}
    for i, q in cand.items():
        if not M2.kin_ok[i] or i not in set(M2.poses_fit.tolist()): st[i] = "kin"; continue
        cl = M2.collide(i)
        if cl < PART_CLR: st[i] = "parts"; continue
        dm = min(float(B1.dist(i, M2.metal_points(i)).min()), min(float(B1.dist(i, M2.world(m, i, Pc)).min()) for m, Pc in M2.contact))
        st[i] = "ok" if dm >= 0 else "contact"
    base_t = int(lead_taken1[np.array(B1.kind) == "ws"].sum()); nws = int((np.array(B1.kind) == "ws").sum())
    qs = sorted(set([0.0] + list(cand.values()))); best = None
    for lo in [q for q in qs if q <= 0]:
        for hi in [q for q in qs if q >= 0]:
            tk = sum(1 for i, q in cand.items() if lo <= q <= hi and st[i] == "ok")
            ct = sum(1 for i, q in cand.items() if lo <= q <= hi and st[i] == "contact")
            gap = 100 * max(0, .9 - (base_t + tk) / nws) + 100 * ct / max(1, len(B1.idx))   # contact share: ws/clip pooled (fit only)
            key = (round(gap, 3), hi - lo)
            if best is None or key < best[0]: best = (key, (lo, hi), tk, ct)
    return best[1], dict(cand=len(cand), st={k: sum(1 for v in st.values() if v == k) for k in ("ok", "contact", "parts", "kin")},
                         new=best[2], new_contacts=best[3], fit_gap_part=best[0][0], q=cand, status=st)


def wear(a0=60.0, azu=330.0, side=0.0, out=None):
    t0 = time.time()
    M1, P2, r1fit = fit_lead(); B1 = M1.B; D = M1.D; u1 = D.u[0]
    c = seat_axis(u1, a0, azu); lo_t, hi_t = travel(c, u1)
    log = {"a0": a0, "azu": azu, "side": side, "c_bvec": [round(float(np.degrees(np.arctan2(c[2], -c[0]))), 1), round(float(np.degrees(np.arcsin(c[1]))), 1)],
           "travel": [lo_t, hi_t], "fit_lead": {k: r1fit[k] for k in ("gap", "reach", "inband14")}}
    print("seat", log, flush=True)
    r0, rs, rcn = build_metal(M1, B1, c); log.update(r0=r0, r0_skin=rs, r0_chain=rcn, hub0_chain_clash_fit_poses=build_metal.clash_at_skin); print("r0", r0, rs, rcn, round(time.time() - t0), flush=True)
    metal, prof = assemble(M1, B1, c, r0, side); log["link0_profile_q0"] = prof
    lead_taken1 = np.array([B1.res[i] is not None and float(np.min(B1.res[i])) >= 0 for i in range(len(B1.idx))])
    (lo, hi), pw = pick_window(M1, P2, B1, c, lo_t, hi_t, metal, lead_taken1)
    # the relayed fit poses also shape link 0 (chain and skin seen from link 0): re-fit the profile with them
    Rq1 = {i: rot_mats(c, [q])[0] for i, q in pw.get("q", {}).items() if lo <= q <= hi and pw["status"][i] in ("ok", "contact")}
    if Rq1:
        M2f = make_model(M1, P2, B1, c, Rq1); M2f.fit()
        pcs = list(np.nonzero(M1.kin_ok)[0]) + [i for i in Rq1 if M2f.kin_ok[i]]
        metal, prof = assemble(M2f, B1, c, r0, side, Rq1, pcs)
    log.update(window=[lo, hi], window_fit=dict((k, v) for k, v in pw.items() if k not in ("q", "status")), link0_profile=prof)
    print("window", lo, hi, log["window_fit"], "link0", prof["len_mm"], "mm rho", prof["rho"][:3], "...", round(time.time() - t0), flush=True)
    # ---- the claim wear: Bench(110,360) exact, frozen shape, relay policy (ii) inside the fit-bench window ----
    B = CB.Bench(n_clip=110, n_ws=360); kind = np.array(B.kind)
    pp = json.load(open(PERPOSE))["poses"]; lead_taken = np.array([r["taken"] for r in pp]); lead_contact = np.array([r["contact"] for r in pp])
    M0 = make_model(M1, P2, B, c); M0.fit()
    cand = relay_candidates(M0, B, c, lo, hi, set(np.nonzero(lead_taken | lead_contact)[0].tolist())) if (lo or hi) else {}
    Rc = {i: rot_mats(c, [q])[0] for i, q in cand.items()}
    res = {}
    for tag, met in (("with_metal", metal), ("ghost", None)):
        M = make_model(M1, P2, B, c, Rc, met); r = M.run()
        taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
        contact = np.array([B.res[i] is not None and float(np.min(B.res[i])) < 0 for i in range(len(B.idx))])
        el = np.array([B.poses[i]["elev"] for i in range(len(B.idx))])
        rel = {i: ("taken" if taken[i] else "contact" if contact[i] else (M.why[i] or "lost")) for i in cand}
        mm = [float(np.min(B.res[i])) for i in range(len(B.idx)) if taken[i]]
        near1 = CB.gap_of(r["inband14"], r["follow"], r["reach"],
                          float(sum(1 for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) < 1.0)) /
                          max(1, sum(1 for i in range(len(B.idx)) if B.res[i] is not None)))
        res[tag] = dict({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                        why=r.get("why"), parts_ib14=r.get("parts_ib14"), parts_pairs=r.get("parts_pairs"),
                        ws_taken=int((taken & (kind == "ws")).sum()), contacts=int(contact.sum()),
                        overhead=[int((taken & (kind == "ws") & (el >= 140)).sum()), int(((kind == "ws") & (el >= 140)).sum())],
                        relayed={k: sum(1 for v in rel.values() if v == k) for k in set(rel.values())},
                        min_metal=round(min(mm), 2) if mm else None, gap_near1=near1,
                        new_takes=[i for i in cand if taken[i]], new_contacts=[i for i in cand if contact[i]],
                        lost_vs_lead=[int(i) for i in np.nonzero(lead_taken & ~taken)[0]],
                        lost_why={k: int(sum(1 for i in np.nonzero(lead_taken & ~taken)[0] if (M.why[i] or ("contact" if contact[i] else "?")) == k))
                                  for k in set((M.why[i] or ("contact" if contact[i] else "?")) for i in np.nonzero(lead_taken & ~taken)[0])})
        if tag == "with_metal":
            # in-band without hub 0 / link 0 (dilution WATCH) and per-part; hub 0 / link 0 near-skin distances per clip frame
            pib = r.get("parts_ib14") or {}
            tot = sum(v[2] * 0 + 1 for v in pib.values())
            res[tag]["clearance_worst"] = {}
            h0 = []; l0 = []
            for i in range(len(B.idx)):
                if not taken[i]: continue
                h0.append(float(B.dist(i, M.world(0, i, metal["hub0_cont"])).min())); l0.append(float(B.dist(i, M.world(0, i, metal["link0_cont"])).min()))
            res[tag]["hub0_min_skin_all_mm"] = round(min(h0), 2); res[tag]["link0_min_skin_all_mm"] = round(min(l0), 2)
            # red team: the 6 taken poses where hub 0 is closest to the skin, with their pose angles
            order = np.argsort(h0)[:6]; ti = [i for i in range(len(B.idx)) if taken[i]]
            res[tag]["hub0_closest"] = [(int(ti[j]), [B.poses[ti[j]][k] for k in ("plane", "elev", "axial")], round(h0[j], 2)) for j in order]
        print(tag, json.dumps(res[tag], default=float)[:900], round(time.time() - t0), flush=True)
    # in-band of the lead's chain alone on the same bench (from the with-metal run's part table)
    pib = res["with_metal"]["parts_ib14"]
    if pib:
        n_in = sum(v[0] * v[2] for k, v in pib.items()); n_all = sum(v[2] for v in pib.values())
        n_in_c = sum(v[0] * v[2] for k, v in pib.items() if k not in ("hub0", "link0")); n_all_c = sum(v[2] for k, v in pib.items() if k not in ("hub0", "link0"))
        res["inband_check"] = dict(per_sample_weighted_all=round(n_in / n_all, 4), chain_only=round(n_in_c / n_all_c, 4),
                                   hub0=pib.get("hub0"), link0=pib.get("link0"))
        wm = res["with_metal"]
        res["gap_without_hub0_link0_inband"] = CB.gap_of(n_in_c / n_all_c, wm["follow"], wm["reach"], wm["contact"])
    log.update(res=res, n_relay_cand=len(cand), relay_q0={int(k): v for k, v in cand.items()}, secs=round(time.time() - t0), mode=B.mode)
    if out: json.dump(log, open(out, "w"), indent=1, default=float)
    return log


def bound(out=None, seats=None):
    """seat-grid lower bound on the frozen exact gap over the whole sweep space:
       in-band <= (chain in-band samples + hub 0 in-band samples + link 0 samples, all assumed in band) / (all)
       (hub 0 is scapula-fixed and axisymmetric: its skin distance on the clip frames is a property of the seat alone);
       reach <= (lead's 262 + every ws pose the frozen chain can close at ANY q0 in the legal travel, zero-size metal)/360;
       contact >= the lead's 4 contact poses / (376 + new)."""
    t0 = time.time(); M1, P2, _ = fit_lead(); B1 = M1.B; u1 = M1.D.u[0]
    B = CB.Bench(n_clip=110, n_ws=360); kind = np.array(B.kind)
    pp = json.load(open(PERPOSE))["poses"]; lead_taken = np.array([r["taken"] for r in pp]); lead_contact = np.array([r["contact"] for r in pp])
    M0 = make_model(M1, P2, B, u1); M0.fit()
    clips = [i for i in range(len(B.idx)) if kind[i] == "clip" and lead_taken[i]]
    n_ch_in, n_ch = 884.0, 981.0                                   # the lead's frozen part table (rows/conecut-knee-knuckle-3r.json)
    rows = []
    for a0, azu in (seats or [(a, z) for a in (55, 60, 70, 80) for z in (300, 315, 330, 345, 285, 0)]):
        c = seat_axis(u1, a0, azu)
        if not seat_ok(c)[0]: rows.append(dict(a0=a0, azu=azu, note="J0 seat rule fails")); continue
        lo_t, hi_t = travel(c, u1)
        r0, rs, rcn = build_metal(M1, B1, c)
        hu, _ = hub0_metal(c, r0)
        dd = np.concatenate([B.dist(i, M0.world(0, i, hu)) for i in clips])   # q0 = 0 on every clip frame (follow 1.0)
        f_in = float(((dd >= 2) & (dd <= 14)).mean())
        A = math.acos(float(np.clip(c @ u1, -1, 1))); L = max(0.0, A * 0.5 * (r0 + float(M1.f[0])) - 2 * HUB_R)
        n_l0 = 7 * (int(L / 2) + 1)
        ib_ub = (n_ch_in + 81 * f_in + n_l0) / (n_ch + 81 + n_l0)
        ib_hub_only = (n_ch_in + 81 * f_in) / (n_ch + 81)
        cand = relay_candidates(M0, B, c, lo_t, hi_t, set(np.nonzero(lead_taken | lead_contact)[0].tolist()))
        n_new = len(cand); reach_ub = (262 + n_new) / 360
        gap_lb = CB.gap_of(ib_ub, 1.0, reach_ub, 4 / (376 + n_new))
        row = dict(a0=a0, azu=azu, travel=[lo_t, hi_t], r0=r0, r0_skin=rs, r0_chain=rcn, hub0_chain_clash_fit_poses=build_metal.clash_at_skin, hub0_inband_clip=round(f_in, 3),
                   hub0_med_mm=round(float(np.median(dd)), 1), link0_len=round(L, 1), n_link0=n_l0, kin_new_ub=n_new,
                   ib_ub_link0_all_in=round(ib_ub, 4), ib_hub0_only=round(ib_hub_only, 4), gap_lb=gap_lb,
                   gap_lb_hub0_only=CB.gap_of(ib_hub_only, 1.0, reach_ub, 4 / (376 + n_new)))
        rows.append(row); print(json.dumps(row), round(time.time() - t0), flush=True)
        if out: json.dump(rows, open(out, "w"), indent=1)
    return rows


def viz_export(par=None): return CC.viz_export(par or {})


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "wear"
    if cmd == "wear":
        a0 = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0; azu = float(sys.argv[3]) if len(sys.argv) > 3 else 330.0
        side = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0; out = sys.argv[5] if len(sys.argv) > 5 else None
        wear(a0, azu, side, out)
    elif cmd == "bound":
        bound(sys.argv[2] if len(sys.argv) > 2 else None)
