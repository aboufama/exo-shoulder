"""L1 keep-out CAD of minarc-stop-knuckle-4r config BDp (the generation-4 winner, verified 19.54 / score 92.89 on Bench(110,360)
exact, frozen shape, margin 5, continuity applied, buildable stops priced: docs/concepts/verify/minarc-bdp-judge.md) -> a
judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json, workspace.json, design.json, parts_full.json,
build.json). Derived from build_pinknee_l1.py (the gen-3 H1 L1): its E strap / boss, knee link, arm pad, pin stacks + E-clip
retainer lands, BOTTOM cut and pad-mount routing clear of the knee sweep are reused unchanged (its module functions, with this
file's chain / checks swapped in); what changes is the chain: link 1 splits at the passive, spring-held, sensed knuckle K.

The shape is the VERIFIED model's own frozen fit (docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py, kitrule 1, phys 1,
capK 6, m3e 1; params docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json with the judge's K stop B fix
a1max 54.748 = dK 34.47): fit on Bench(60,160) FAST (= the claim harness' and both lenses' "fit60" hand-over), the exact
shape (hub levels f1 fK f2 f3, knee level tr, link profiles, knee centre m) that the verifiers wore frozen on Bench(110,360)
exact. Member frames reproduce the model's exact kinematics (state A / stretched with J2 on its q2 dowel stop and K opened,
closed form): world = RS (R_m x + t_m) with (R_m, t_m) = the model's Model.T(m, i); members 0 scapula (base), 1 link 1a,
7 link 1b, 2 link 2, 3 member 3 (hub 3 lower plate + E strap + E boss), 6 knee link, 5 arm (pad).

Parts at their real size (O20 v5 hubs only: MR117-2RS pair, 12.25 mm stack):
  * J1: base = J1 upper boss + cap (the scapula handler carries the base DIRECTLY at the J1 hub ring, no tab); link 1a = J1
    lower plate (O20 x 3);
  * K: link 1a = K lower plate (O20 x 3) with the K stop slot; link 1b = K upper boss + the CLOCK-SPRING CAP, 6 mm taller
    (F+3.15 .. F+18.25: 0.3 x 5 mm 1.4310 +C1900 strip >= 145 mm, rate <= 0.015 N.m/rad, 0.08 N.m preload, in an O16
    annulus round an O5 arbor) + the K stop dowel; stop A (dK 0, the spring's rest) and stop B (dK = 34.47 deg, the judge's
    fix) are the two ends of an arc slot at r 7.75 mm in K's lower plate, the dowel pressed in K's upper boss;
  * J2: link 1b = J2 lower plate with the q2 slot (q2 -24.98 .. 100.84 deg: the dowel-in-arc-slot stop of the verified
    claim, drawn at the 5.0-deg J1-J3 margin; the slot ends are the stops); link 2 = J2 upper boss + cap + the q2 dowel;
  * dowels: ISO 8734 O3 m6 hardened (O2 fails the bending check at the jam push - build.json "dowel_check"), r 7.75 mm,
    from F+0.5 (0.5 mm above the plate's skin face) to F+6.15 (3 mm pressed into the upper boss); slot width 3.1 mm
    (0.05 mm radial running clearance), radial ends placed so the dowel touches at the stop angle (+0.02 mm);
  * links 1a, 1b, 2: 8 x 3 mm straps through the model's fitted underside samples, columns inside a hub's footprint
    (+2.5 mm) lifted to that hub's member level (lower plate 0, upper boss UP): the model's own link levels;
  * J3, E strap, E boss, knee link, arm pad, pin a / b retainers (DIN 6799 RS 3.2 e-clip land + 0.3 mm pin end), pad mount
    routed clear of the knee sweep, BOTTOM cut square to the arm clear of the sweep: build_pinknee_l1 unchanged.
The slot sector of each stop is turned (about the hub axis) to the side of the plate the lower member's strap does not cover,
so the dowel sweeps only the slot over the joint's whole travel.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_minarc_l1.py [--out l1_minarc-bdp] [--jobs 2] [--no-clips]
"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo")); sys.path.insert(0, HERE)
os.environ.pop("CB_EXACT", None)                     # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_pinknee_l1 as BASE                                                 # noqa: E402  (the gen-3 L1 builder: reused parts + clip / workspace drivers)
CB, REF = BASE.CB, BASE.REF


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ID = "minarc-stop-knuckle-4r"
KR = _load("minarc_kitrule_l1", os.path.join(REPO, "docs", "concepts", "models", ID + "-kitrule.py"))
KB = KR.KB; S = KB.S
PARAMS_FILE = os.path.join(REPO, "docs", "concepts", "verify", "minarc-kitrule", "params_floorBD5_phys_cap6.json")
A1MAX_FIX = 54.748                                                              # K stop B at dK 34.47 (judge's ruling, 0 bench cost)
FULL = BASE.FULL
CROWN, UP, T_LINK, W_LINK, RUN = S.CROWN, S.UP, S.T_LINK, S.W_LINK, S.RUN
BOSS_R, PAD_R, KNEE_W = KB.BOSS_R, KB.PAD_R, KB.KNEE_W
PLATE = 3.0; ADJ = BASE.ADJ; HR = BASE.HR; unit = S.unit
TI, STEEL = BASE.TI, BASE.STEEL
DOWEL_R, SLOT_RS, SLOT_CLR, END_CLR = 1.5, 7.75, 0.05, 0.02                     # O3 dowel at r 7.75; radial / end clearance (mm)
DOWEL_Z = (0.5, UP + 3.0)                                                       # 0.5 mm above the plate's skin face .. 3 mm into the upper boss
LVL = {("L1a", 0): 0.0, ("L1a", 1): 0.0, ("L1b", 1): UP, ("L1b", 2): 0.0, ("L2", 2): UP, ("L2", 3): UP}   # the model's link levels (finalize)


# ---------------------------------------------------------------------------------------------------- the fitted model
def params_from(a):
    if a.params: P = json.loads(a.params); src = "--params"
    else: P = json.load(open(a.params_file or PARAMS_FILE)); P = P.get("params", P); src = os.path.relpath(a.params_file or PARAMS_FILE, REPO)
    if a.a1max is not None: P["a1max"] = float(a.a1max); src += f" + a1max {a.a1max} (K stop B fix)"
    return P, src


def fit(P, bench=(60, 160)):
    """the frozen protocol's fit = the claim harness' fit60: the kit-rule model's own run on Bench(60,160) FAST"""
    B = CB.Bench(int(bench[0]), int(bench[1])); r, M = KR._report(B, dict(P))
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q)
    return M, r


def joints4(M):
    """J1, K, J2, J3: axes U, axis points C, hub levels F, radii (O20 only)"""
    D = M.D; U = [D.u[0], D.uK, D.u[1], D.u[2]]; C = [D.c[0], np.zeros(3), D.c[1], D.c[2]]
    F = [M.f[0], M.fK, M.f[1], M.f[2]]; R = [M.hr[0], S.HUB_R, M.hr[1], M.hr[2]]
    return U, C, F, R


def link_rows(M):
    """the model's finalize() link rows (KModel.finalize), every station kept (also inside the hub footprints)"""
    U, C, F4, _ = joints4(M); k = math.tan(S.RAMP * S.D2R); keep = ~M.drop
    rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in M.Lneed.items() if nm in ("L1a", "L1b", "L2")}; out = {}
    for lk in M.geo.links:
        rows = []
        for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
            r = r.copy(); Sx = sarc
            for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                idx = np.nonzero(keep_s)[0]
                if not len(idx): continue
                j = idx[0] if end == 0 else idx[-1]
                cen = C[kk] + F4[kk] * U[kk]; den = float(dv[j] @ U[kk])
                rc = (cen @ U[kk] + LVL[(lk["name"], kk)]) / max(den, 0.2)
                r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            rows.append((dv, keep_s, r))
        out[lk["name"]] = (lk, rows)
    return out


def link_solid(M, lk, rows):
    """8 x 3 mm strap through the model's fitted underside samples, one station past each hub rim; that station and every
    column inside a hub's footprint (+2.5 mm) lifted to the hub's member level (build_pinknee_l1.link_solid on 4 joints)"""
    U, C, F4, hr = joints4(M)
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r.copy() for _, _, r in rows]
    d_lo = unit(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
    cols_d = [d_lo] + dvs + [d_hi]; cols_r = [rs[0].copy()] + [r.copy() for r in rs] + [rs[-1].copy()]
    for kk, j in ((lk["ka"], j0), (lk["kb"], j1)):
        if j == (idx[0] if kk == lk["ka"] else idx[-1]): continue
        cen = C[kk] + F4[kk] * U[kk]
        for q in range(len(cols_d)):
            den = float(cols_d[q][j] @ U[kk])
            if den > 0.2: cols_r[q][j] = max(cols_r[q][j], (cen @ U[kk] + LVL[(lk["name"], kk)]) / den + 0.02)
    for kk in (lk["ka"], lk["kb"]):
        cen = C[kk] + F4[kk] * U[kk]; lv = LVL[(lk["name"], kk)] + 0.2
        for q in range(len(cols_d)):
            Pq = cols_d[q] * cols_r[q][:, None]; w = Pq - C[kk]
            off = np.linalg.norm(w - (w @ U[kk])[:, None] * U[kk], axis=1); den = cols_d[q] @ U[kk]
            sel = (off < hr[kk] + 2.5) & (den > 0.2)
            cols_r[q][sel] = np.maximum(cols_r[q][sel], (cen @ U[kk] + lv) / den[sel])
    J = np.arange(j0, j1 + 1)
    Bot = np.stack([cols_d[q][J] * cols_r[q][J][:, None] for q in range(len(cols_d))], 1)
    Off = T_LINK * np.stack([cols_d[q][J] for q in range(len(cols_d))], 1)
    return REF.grid_solid(Bot, Off)


# ---------------------------------------------------------------------------------------------------- stops (dowel in arc slot)
def extrude2d(V2, F2, cen, e, f, ax, z0, z1):
    """closed solid from a 2D triangle mesh (holes allowed) in the (e, f) plane, z0..z1 along ax (e, f, ax right-handed)"""
    V2 = np.asarray(V2, float); F2 = np.asarray(F2, int).copy()
    d1, d2 = V2[F2[:, 1]] - V2[F2[:, 0]], V2[F2[:, 2]] - V2[F2[:, 0]]; ar = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]; F2[ar < 0] = F2[ar < 0][:, ::-1]
    n = len(V2); to3 = lambda z: cen + V2[:, :1] * e + V2[:, 1:2] * f + z * ax
    V = np.r_[to3(z0), to3(z1)]; F = [F2[:, ::-1], F2 + n]
    E = np.r_[F2[:, [0, 1]], F2[:, [1, 2]], F2[:, [2, 0]]]; key = np.sort(E, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True); Eb = E[cnt[inv.ravel()] == 1]
    a, b = Eb[:, 0], Eb[:, 1]; F += [np.c_[a, b, b + n], np.c_[a, b + n, a + n]]
    m = trimesh.Trimesh(V, np.concatenate(F), process=True)
    return m


def slotted_plate(cen, ax, z0, z1, R, rs, w, a_lo, a_hi, n_ang=240):
    """O(2R) x (z1 - z0) plate about ax at cen with an arc slot: radii rs - w .. rs + w, angles a_lo .. a_hi (rad, frame_of(ax),
    a_hi - a_lo < 2 pi), radial ends; one watertight genus-1 solid (polar grid, extruded)"""
    e, f = S.frame_of(ax); f = np.cross(ax, e)
    tw = 2 * np.pi
    ang = np.unique(np.round(np.r_[np.linspace(0, tw, n_ang, endpoint=False), a_lo % tw, a_hi % tw], 9))
    radii = np.unique(np.r_[np.linspace(R / 6, rs - w, 4), rs - 0.5 * w, rs, rs + 0.5 * w, rs + w, np.linspace(rs + w, R, 3)])
    na, nr = len(ang), len(radii)
    V2 = [np.zeros(2)] + [np.array([r * math.cos(t), r * math.sin(t)]) for r in radii for t in ang]
    vid = lambda i, j: 1 + i * na + (j % na)
    F2 = [[0, vid(0, j), vid(0, j + 1)] for j in range(na)]
    span = (a_hi - a_lo) % tw
    for i in range(nr - 1):
        rm = 0.5 * (radii[i] + radii[i + 1]); in_band = (rm > rs - w - 1e-9) and (rm < rs + w + 1e-9)
        for j in range(na):
            t0, t1 = ang[j], ang[(j + 1) % na] + (tw if j == na - 1 else 0.0); tm = 0.5 * (t0 + t1)
            if in_band and ((tm - a_lo) % tw) < span: continue                  # the slot
            F2 += [[vid(i, j), vid(i + 1, j), vid(i + 1, j + 1)], [vid(i, j), vid(i + 1, j + 1), vid(i, j + 1)]]
    return extrude2d(np.array(V2), np.array(F2), cen, e, f, ax, z0, z1)


def slot_place(strap_pts, cen, ax, q_lo, q_hi, rs, w, r_d):
    """the dowel's home angle th (rad, frame_of(ax) in the UPPER member) so that the slot (dowel centre th + q, q in
    [q_lo, q_hi] rad, plus the dowel's angular half-width) keeps the most angle from the lower member's strap points in the
    slot's radial / height band. (th, a_lo, a_hi, clearance deg)"""
    e, f = S.frame_of(ax); f = np.cross(ax, e)
    w3 = strap_pts - cen; z = w3 @ ax; pl = w3 - np.outer(z, ax); r = np.linalg.norm(pl, axis=1)
    band = (z > -0.5) & (z < PLATE + 0.5) & (r > rs - w - 1.0) & (r < rs + w + 1.0)
    phi = np.arctan2(pl[band] @ f, pl[band] @ e)
    d = math.asin(min(1.0, (r_d + END_CLR) / rs)); best = None
    for th in np.radians(np.arange(0.0, 360.0, 1.0)):
        a_lo, a_hi = th + q_lo - d, th + q_hi + d; mid, half = 0.5 * (a_lo + a_hi), 0.5 * (a_hi - a_lo)
        gap = np.abs((phi - mid + np.pi) % (2 * np.pi) - np.pi) - half
        c = float(gap.min()) if len(gap) else np.pi
        if best is None or c > best[3]: best = (th, a_lo, a_hi, c)
    th, a_lo, a_hi, c = best
    return th, a_lo, a_hi, math.degrees(c)


def stop_specs(M):
    """the two stops' joint ranges in the joint's own relative-rotation angle (rad): J2's q2 (R_1b^T R_2 = rot(u2, q2)) between
    the dowel stops (the q2 window on the ik branch's half-turn, as the claim harness checks it) and K's dK (R_1a^T R_1b =
    rot(uK, dK)) between stop A (0) and stop B"""
    D = M.D; P = D.p
    lo, hi = D.q2_stops; q0 = math.degrees(D._q2c[2]); sg = D.q2sgn
    rel = lambda x: ((x - q0 + 180) % 360 - 180) * sg
    r_lo, r_hi = sorted((rel(lo), rel(hi)))
    qa, qb = sorted((q0 + sg * r_lo, q0 + sg * r_hi))
    b1, b2 = float(P["bk1"]), float(P["bk2"])
    cpsiB = (math.cos(float(P["a1max"]) * S.D2R) - math.cos(b1 * S.D2R) * math.cos(b2 * S.D2R)) / (math.sin(b1 * S.D2R) * math.sin(b2 * S.D2R))
    dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(D.psiA)); sK = float(np.sign(D.psiA))
    ka, kb = sorted((0.0, sK * dKB))
    return dict(J2=(math.radians(qa), math.radians(qb), dict(q2_stops_deg=[round(lo, 3), round(hi, 3)], window_deg=[round(qa, 3), round(qb, 3)])),
                K=(ka, kb, dict(stop_A_deg=0.0, stop_B_deg=round(math.degrees(sK * dKB), 3), a1max=float(P["a1max"]))))


def dowel_check(F_N=770.0, T_Nm=None):
    """hand calc of the stop dowels at the jam push (red team, buildability lens: ~6 N.m about the joint -> ~770 N at r 7.75 mm):
    dowel pressed in the upper boss, loaded over the slot depth: shear, bending at the boss face, bearing on the Ti slot end,
    and the bearing pair's static radial load (a single dowel's force is not a couple: the MR117 pair carries it radially)"""
    r = SLOT_RS / 1000.0; F = F_N if T_Nm is None else T_Nm / r
    lever = (UP - 0.5 * (DOWEL_Z[0] + PLATE))                                    # mm: boss face to the centre of the slot contact (0.5 .. 3.0)
    out = {}
    for d in (2.0, 3.0):
        A = math.pi * d ** 2 / 4; Z = math.pi * d ** 3 / 32; tau = F / A; sb = F * lever / Z
        out[f"O{d:g}"] = dict(shear_MPa=round(tau, 0), bending_MPa=round(sb, 0), bearing_on_Ti_MPa=round(F / (d * (PLATE - DOWEL_Z[0])), 0),
                              SF_bending_vs_1500MPa_yield=round(1500 / sb, 2), SF_shear_vs_0p58x1500=round(0.58 * 1500 / tau, 2))
    C0 = 280.0; out["bearing_pair_static"] = dict(radial_N=round(F, 0), per_bearing_N=round(F / 2, 0), C0_N_each=C0, s0=round(C0 / (F / 2), 2),
                                                  note="MR117 C0 ~0.28 kN (docs/HARDWARE.md); s0 < 1 = raceway brinelling at the jam push")
    out["load"] = dict(F_N=round(F, 0), r_mm=SLOT_RS, joint_torque_Nm=round(F * r, 2), lever_mm=round(lever, 2))
    return out


# ---------------------------------------------------------------------------------------------------- parts
def build_parts(M):
    """[(group, member, name, mesh in the MEMBER-LOCAL home frame, material)]; member 5 = arm-fixed (canonical arm frame)"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"])
    U, C, F4, hr = joints4(M); H = lambda k: C[k] + F4[k] * U[k]; out = []
    capK = float(P.get("capK", 0) or 0)
    prof = link_rows(M); straps = {}
    for nm in ("L1a", "L1b", "L2"):
        lk, rows = prof[nm]; straps[nm] = link_solid(M, lk, rows)
    out.append(("base", 0, "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member, carried directly by the scapula handler at the hub ring)",
                REF.cyl(H(0), U[0], UP, CROWN, r=hr[0]), "ti"))
    out.append(("l1a", 1, "J1 lower plate keep-out (O20 x 3, link 1a)", REF.cyl(H(0), U[0], 0.0, PLATE, r=hr[0]), "ti"))
    out.append(("l1a", 1, "link 1a strap keep-out (8 x 3 mm Ti, fitted underside, J1 -> K)", straps["L1a"], "ti"))
    sp = stop_specs(M); info = {}
    smp = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 4000, seed=2)[0]]
    for key, k, lower_strap, glo, mlo, gup, mup, label in (("K", 1, "L1a", "l1a", 1, "l1b", 7, "K"), ("J2", 2, "L1b", "l1b", 7, "l2", 2, "J2")):
        q_lo, q_hi, meta = sp[key]
        th, a_lo, a_hi, clr = slot_place(smp(straps[lower_strap]), H(k), U[k], q_lo, q_hi, SLOT_RS, DOWEL_R + SLOT_CLR, DOWEL_R)
        plate = slotted_plate(H(k), U[k], 0.0, PLATE, hr[k], SLOT_RS, DOWEL_R + SLOT_CLR, a_lo, a_hi)
        e, f = S.frame_of(U[k]); f = np.cross(U[k], e); pd = H(k) + SLOT_RS * (math.cos(th) * e + math.sin(th) * f)
        dw = REF.cyl(pd, U[k], DOWEL_Z[0], DOWEL_Z[1], r=DOWEL_R)
        travel = math.degrees(q_hi - q_lo)
        out.append((glo, mlo, f"{label} lower plate keep-out (O20 x 3, {'link 1a' if key == 'K' else 'link 1b'}) with the {label} stop slot "
                    f"(r {SLOT_RS} mm, {2 * (DOWEL_R + SLOT_CLR):.1f} wide, {travel:.1f} deg of travel + the dowel; its ends = the stops)", plate, "ti"))
        out.append((gup, mup, f"{label} stop dowel (ISO 8734 O{2 * DOWEL_R:g} m6 hardened, r {SLOT_RS} mm, F+{DOWEL_Z[0]}..F+{DOWEL_Z[1]:.2f}, pressed in the "
                    f"{label} upper boss)", dw, "steel"))
        info[key] = dict(meta, travel_deg=round(travel, 3), dowel_home_angle_deg=round(math.degrees(th), 2), slot_deg=[round(math.degrees(a_lo), 2), round(math.degrees(a_hi), 2)],
                         clearance_to_lower_strap_deg=round(clr, 2), dowel_mm=[2 * DOWEL_R, DOWEL_Z[0], DOWEL_Z[1]], slot_r_mm=SLOT_RS, slot_w_mm=2 * (DOWEL_R + SLOT_CLR),
                         end_clearance_mm=END_CLR, frame="angles in frame_of(axis) of the lower member: dowel centre = home angle + joint angle")
        if key == "K":
            out.append(("l1b", 7, f"K upper boss + clock-spring cap keep-out (O20, F+3.15..F+{CROWN + capK:.2f}: cap {capK:g} mm taller - 0.3 x 5 mm 1.4310 +C1900 "
                        f"strip >= 145 mm, <= 0.015 N.m/rad, 0.08 N.m preload; K sensed: 4th encoder)", REF.cyl(H(1), U[1], UP, CROWN + capK, r=hr[1]), "ti"))
            out.append(("l1b", 7, "link 1b strap keep-out (8 x 3 mm Ti, fitted underside, K -> J2)", straps["L1b"], "ti"))
    out.append(("l2", 2, "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(2), U[2], UP, CROWN, r=hr[2]), "ti"))
    out.append(("l2", 2, "link 2 strap keep-out (8 x 3 mm Ti, fitted underside, J2 -> J3)", straps["L2"], "ti"))
    out.append(("l2", 2, "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(3), U[3], UP, CROWN, r=hr[3]), "ti"))
    out.append(("l3", 3, "J3 lower plate keep-out (O20 x 3, member 3)", REF.cyl(H(3), U[3], 0.0, PLATE, r=hr[3]), "ti"))
    Em, Einfo = BASE.e_strap(M)
    out.append(("l3", 3, f"E strap keep-out (8 x 3 mm Ti, fitted underside, hub 3 plate -> pin a, thins to {tp:.2f} at the boss)", Em, "ti"))
    out.append(("l3", 3, f"E boss = pin a lower plate (O{2 * BOSS_R:.0f} x {tp:.2f} mm, tr..tr+tp, member 3)", REF.cyl(fr["A0"], sn, tr, tr + tp, r=BOSS_R), "ti"))
    z0 = tr + tp + RUN; ck = fr["A0m"] + (lc / 2) * fr["eK"] + (z0 + tp / 2) * sn
    out.append(("l4", 6, f"knee link keep-out (flat Ti bar {lc + 2 * BOSS_R:.1f} x {KNEE_W:.0f} x {tp:.2f} mm, pins a, b {BOSS_R:.0f} mm from its ends, tr+tp+0.5)",
                REF.box(ck, np.stack([fr["eK"], fr["nK"], sn], 1), [lc + 2 * BOSS_R, KNEE_W, tp]), "ti"))
    out.append(("H", 5, f"arm pad = pin b lower plate (O{2 * PAD_R:.0f} x {tp:.2f} mm, tr..tr+tp, arm-fixed on the cuff)", REF.cyl(fr["Bm"], sn, tr, tr + tp, r=PAD_R), "ti"))
    zr = z0 + tp + RUN; RET = BASE.RET
    out.append(("l3", 3, f"pin a retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["A0"], sn, zr, zr + RET, r=4.0), "steel"))
    out.append(("H", 5, f"pin b retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["Bm"], sn, zr, zr + RET, r=4.0), "steel"))
    stack = dict(pin_stack_mm=float(P["stk"]), plate_tp=tp, run=RUN, knee_level_tr=round(float(tr), 3), f=[round(float(x), 3) for x in M.f], fK=round(float(M.fK), 3),
                 capK_mm=capK, hubK_crown_mm=CROWN + capK, boss=[round(float(tr), 3), round(float(tr + tp), 3)], knee=[round(float(z0), 3), round(float(z0 + tp), 3)], E=Einfo,
                 knee_link_mm=[round(lc + 2 * BOSS_R, 2), KNEE_W, tp], hubs_r=list(hr), retainer=[round(float(zr), 3), round(float(zr + RET), 3)],
                 full_pin_stack_mm=round(float(zr + RET - tr), 3), stops=info)
    return out, stack


# ---------------------------------------------------------------------------------------------------- kinematics per pose
GROUPS = ((1, "l1a"), (7, "l1b"), (2, "l2"), (3, "l3"), (6, "l4"))


def chain(M, poses):
    """poses (n, 5) -> per pose: the kit-rule model's IK (state A / forced with J2 on its q2 stop and K opened), knee, closure
    residual, (G, T) per group from the model's own member transforms"""
    D = M.D; RS = np.array([S.scap(float(p[1])) for p in poses]); RH = np.array([S.humerus(p) for p in poses])
    Q = np.einsum("nji,njk->nik", RS, RH); q, ok, X1, X2, X3, s = D.ik(Q)
    X1b = D._X1b; dK = np.asarray(D._dK, float).copy(); st = np.asarray(D._state).copy(); m3e = np.asarray(D._m3e, float).copy()
    Kn = D.knee(s)
    R123 = X3[0]; res = np.degrees(np.arccos(np.clip((np.einsum("nij,nij->n", R123, Q) - 1) / 2, -1, 1)))
    kok = Kn["ok"] & (np.abs(s[:, 2]) <= M.p["R_tol"])
    K = dict(q=np.degrees(q), qr=q, ok=ok, kok=kok, res=res, s=s, Q=Q, RS=RS, X={1: X1, 2: X2, 3: X3, 7: X1b}, Kn=Kn, dK=dK, state=st, m3e=m3e,
             qq=np.degrees(np.c_[q[:, :2], q[:, 2] + Kn["phi"], Kn["qa"], Kn["qb"], dK]))
    n = len(Q); G = {"base": RS}; T = {"base": np.zeros((n, 3))}
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for m, g in GROUPS:
            Gm = np.zeros((n, 3, 3)); Tm = np.zeros((n, 3))
            for j in range(n):
                if not (ok[j] and np.isfinite(Kn["th"][j])): Gm[j] = RS[j]; continue
                R, t = M.T(m, j); Gm[j] = RS[j] @ R; Tm[j] = RS[j] @ t
            G[g] = Gm; T[g] = Tm
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    K["G"], K["T"] = G, T
    return K


def frame_dict(K, j, p, want, held, why=None):
    f = REF.frame_dict(K, j, p, want, held, why)
    f["knee"] = dict(phi=round(float(np.degrees(K["Kn"]["phi"][j])), 3), pin_a=round(float(np.degrees(K["Kn"]["qa"][j])), 3),
                     pin_b=round(float(np.degrees(K["Kn"]["qb"][j])), 3), angle=round(float(K["Kn"]["ang"][j]), 2))
    f["knuckle"] = dict(dK=round(float(np.degrees(K["dK"][j])), 3), state=int(K["state"][j]), m3e=round(float(K["m3e"][j]), 2))
    return f


def extra_checks(M, j):
    """the claim harness' added part checks at one pose (minarc-stop-knuckle-4r-remeasure.extra_checks_B): knee link vs hub 3
    ABOVE its lower plate (1 mm), E boss vs hubs 1 / K / 2 and links 1a / 1b (1 mm) and link 2 (adjacent at J3: 0.15 mm).
    (min clearance, adjacent clearance)"""
    from scipy.spatial import cKDTree
    D = M.D; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = D.p["tp"]; h = T_LINK / 2
    if not hasattr(M, "_xc"):
        _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; M._H3up = X[((X - cen3) @ u[2]) >= UP - 1e-6]
        e, f = S.frame_of(sn); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(BOSS_R, 1.0)
        M._boss = np.concatenate([fr["A0"] + z * sn + BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                                 + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)]); M._xc = True
    R3, t3 = M.T(3, j); bx = M._boxes_at_final(j); kc, kR, kh = bx["knee"]
    v = {"knee-hub3up": float(M.sd_box(M._H3up @ R3.T + t3, kc, kR, kh).min())}
    bw = M._boss @ R3.T + t3
    cyl = {k: (M.T(m, j)[0] @ cc + M.T(m, j)[1], M.T(m, j)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
    stp = {k: X @ M.T(m, j)[0].T + M.T(m, j)[1] for k, (m, X) in M.strap.items()}
    for hb in ("hub1", "hubK", "hub2"): v[f"boss-{hb}"] = float(M.sd_cyl(bw, *cyl[hb], r=M.cyl_r[hb]).min())
    for L in ("L1a", "L1b"):
        if len(stp[L]): v[f"boss-{L}"] = float(cKDTree(stp[L]).query(bw)[0].min()) - h
    c3w, ax3 = cyl["hub3"]; w = stp["L2"] - c3w; far = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > S.HUB_R + 1
    vL2 = float(cKDTree(stp["L2"][far]).query(bw)[0].min()) - h if far.any() else 1e9
    return min(v.values()), vL2


def set_adjacent(parts):
    """built-part pairs that move relative to each other and can meet (their real meshes): the chain pairs at J1-K-J2-J3 incl.
    each stop dowel vs its slotted plate and the lower member's strap, plus build_pinknee_l1's knee / pad / retainer pairs"""
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None) or next((p for p in parts if s in p[2]), None); BASE.ADJ_PAIRS.clear()
    pairs = (("link 1a strap", "link 1b strap"), ("link 1b strap", "link 1a strap"), ("link 1a strap", "K upper boss"), ("K upper boss", "link 1a strap"),
             ("link 1b strap", "K lower plate"), ("K lower plate", "link 1b strap"), ("K stop dowel", "K lower plate"), ("K stop dowel", "link 1a strap"),
             ("K stop dowel", "J1 lower plate"), ("link 1b strap", "link 2 strap"), ("link 2 strap", "link 1b strap"), ("link 2 strap", "J2 lower plate"),
             ("J2 lower plate", "link 2 strap"), ("link 1b strap", "J2 upper boss"), ("J2 stop dowel", "J2 lower plate"), ("J2 stop dowel", "link 1b strap"),
             ("link 1a strap", "link 2 strap"), ("link 2 strap", "link 1a strap"), ("link 2 strap", "J3 lower plate"), ("J3 lower plate", "link 2 strap"),
             ("E strap", "link 2 strap"), ("link 2 strap", "E strap"), ("E strap", "J3 upper boss"), ("J3 upper boss", "E strap"),
             ("knee link", "E strap"), ("E strap", "knee link"), ("knee link", "E boss"), ("knee link", "J3 upper boss"), ("knee link", "link 2 strap"),
             ("link 2 strap", "knee link"), ("arm pad", "E boss"), ("arm pad", "E strap"), ("E strap", "arm pad"), ("pad mount", "E boss"),
             ("pad mount", "E strap"), ("E strap", "pad mount"), ("E boss", "pad mount"), ("knee link", "pad mount"), ("arm pad", "J3"),
             ("pad mount", "J3 lower plate"), ("pad mount", "J3 upper boss"), ("link 2 strap", "arm pad"), ("link 2 strap", "pad mount"),
             ("pin a retainer", "knee link"), ("pin b retainer", "knee link"), ("pin a retainer", "link 2 strap"), ("pin b retainer", "link 2 strap"),
             ("pin a retainer", "J3 upper boss"), ("pin b retainer", "E strap"), ("pin b retainer", "E boss"), ("pin a retainer", "pad mount"))
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1]: continue
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


BASE.chain, BASE.frame_dict, BASE.extra_checks = chain, frame_dict, extra_checks       # the gen-3 drivers run this chain


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, parts, stack):
    """(a) the model's metal samples (hub discs, E strap, E boss, arm pad, knee link, link straps) posed by the model's own member
    transforms vs the posed exo.glb surface of their group (scene_export.frame_xforms on the frame dict = the judges' path);
    hub-disc samples over a stop slot are counted apart (the slot is a real void in the plate); (b) every built part's vertices
    posed by the model's member transforms vs posed by frame_xforms; (c) the dowels inside their slots at the pose's joint angle.
    Poses (fit bench, taken): arm at the side, the first, the middle, the highest two, behind the back, across the body, the
    overhead raise peak (plane 30, elev 150, axial -60: hub 2's 0.05 mm pinch) and the most-opened forced pose (K open)."""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    allp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    K = chain(M, allp)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    kin = [i for i in range(len(B.idx)) if K["ok"][i] and K["kok"][i] and K["res"][i] < 0.5]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": next(j for j in sorted(taken, key=el)[::-1] if j != max(taken, key=el))}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    tgt = np.array([30.0, 150.0, -60.0]); pick["overhead raise peak"] = min(kin, key=lambda i: float(np.linalg.norm(allp[i, :3] - tgt)))
    forced = [i for i in kin if K["state"][i] != 0]
    ft = [i for i in forced if i in set(taken)]
    if forced: pick["forced, K most open" + (" (taken)" if ft else " (closes, not taken)")] = max(ft or forced, key=lambda i: abs(K["dK"][i]))
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    grp_of = {0: "base", 1: "l1a", 7: "l1b", 2: "l2", 3: "l3", 6: "l4", 5: "H"}; out = []
    U, C, F4, hr = joints4(M); D = M.D
    st = stack["stops"]
    for lab, i in pick.items():
        pz = allp[i]; fr = frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; posed = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and not any(s_ in node for s_ in ("arm pad", "pad mount", "pin b retainer"))): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m); posed["|".join(node.split("|")[:2])] = m
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K); res = {}; slot_n = {}
        try:
            for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
                Pw = M.world(m, i, Xp); g = "l1a" if name == "hub1" else grp_of[m]
                d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                            np.ascontiguousarray(meshes[g].faces, np.int64))[0])
                if name in ("hubK", "hub2"):                                     # samples over the slot (a real void): counted apart
                    k = 1 if name == "hubK" else 2; cen = C[k] + F4[k] * U[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                    inslot = (rr > SLOT_RS - DOWEL_R - SLOT_CLR - 0.6) & (rr < SLOT_RS + DOWEL_R + SLOT_CLR + 0.6); slot_n[name] = int(inslot.sum())
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]
                    d = d[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4)]
                if name in ("L1a", "L1b", "L2"):
                    lk = next(x for x in M.geo.links if x["name"] == name); zone = np.zeros(len(Xp), bool)
                    for kk in (lk["ka"], lk["kb"]):
                        w = Xp - C[kk]; zone |= np.linalg.norm(w - (w @ U[kk])[:, None] * U[kk], axis=1) < hr[kk] + 2.5 + 0.5
                    res[name + " outside hub zones"] = [round(float(d[~zone].max()), 4) if (~zone).any() else None, int((~zone).sum())]
                    res[name + " hub zones (lifted)"] = [round(float(d[zone].max()), 4) if zone.any() else None, int(zone.sum())]
            fdev = 0.0
            for g, mem, nm, mesh, mat in parts:
                Vw = M.world(mem, i, np.asarray(mesh.vertices)); Pg = np.asarray(posed[f"{g}|{nm}"].vertices)
                fdev = max(fdev, float(np.abs(Vw - Pg).max()))
            # (c) joint angles from the member frames, dowel centre inside its slot
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
            from scipy.spatial.transform import Rotation as Rot
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                s_ = st[key]; c_ = s_["dowel_home_angle_deg"] + ang; a0, a1 = s_["slot_deg"]
                dd_ = math.degrees(math.asin((DOWEL_R + END_CLR) / SLOT_RS)); lo_, hi_ = a0 + dd_, a1 - dd_
                pos = (c_ - lo_) % 360.0
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(pos, 3), to_stop_hi_deg=round((hi_ - lo_) - pos, 3), inside=bool(pos <= (hi_ - lo_) + 0.01 or pos >= 360.0 - 0.01))
        finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
        worst = max(v[0] for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None)
        worst_l = max(v[0] for k, v in res.items() if k in ("L1a", "L1b", "L2"))
        worst_o = max((res[k][0] or 0) for k in ("L1a outside hub zones", "L1b outside hub zones", "L2 outside hub zones"))
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        rigid_samples_max_mm=round(worst, 4), strap_samples_max_mm=round(worst_l, 4), strap_samples_outside_hub_zones_max_mm=round(worst_o, 4),
                        per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4), knee_angle=round(float(K["Kn"]["ang"][i]), 1),
                        m3e=round(float(K["m3e"][i]), 2), stops=inside))
        print(f"  check {lab:30s} pose {i} {np.round(pz[:3], 1)} state {int(K['state'][i]):+d}: model rigid samples vs posed glb max {worst:.4f} mm, straps {worst_l:.3f} "
              f"({worst_o:.3f} outside the lifted hub zones), frames dev {fdev:.2e} mm, knee {K['Kn']['ang'][i]:.1f}, dK {inside['K']['angle_deg']:.2f} "
              f"q2 {inside['J2']['angle_deg']:.2f} dowels in slot {inside['K']['inside']} / {inside['J2']['inside']}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="l1_minarc-bdp")
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--a1max", type=float, default=A1MAX_FIX)
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time(); fb = (60, 160); fbs = "Bench(60,160)"
    import concept_kit as KIT
    dd = os.path.join(FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    P0, src = params_from(a); M, rep = fit(P0, fb); D = M.D; P = M.p
    if M.B.mode != "fast": print(f"WARNING: the fit bench {fbs} ran {M.B.mode}, not fast", flush=True)
    print(f"fit ({src}) on {fbs} {M.B.mode} (fold margin {KIT.FOLD_MARGIN}): near-touch gap {rep['gap']} plain {rep['plain']} ib10 {rep['inband10']} "
          f"f {np.round(M.f, 3).tolist()} fK {M.fK:.3f} tr {M.tr:.2f} m {np.round(D.m, 3)} q2 stops {np.round(D.q2_stops, 3)} kitrule {rep.get('kitrule')} ({time.time() - t0:.0f} s)", flush=True)
    parts, stack = build_parts(M)
    up = BASE.user_parts(); bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ HR
    dense = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 40000, seed=5)[0]]
    mc = trimesh.Trimesh(bottom_c, np.asarray(bot.faces), process=False)
    sweep, swrep = BASE.arm_sweep(M, parts); xc, crep = BASE.cut_bottom(M, dense(mc), sweep)
    if xc is not None:
        mc = BASE.slice_bottom(mc, M, xc)
        k = next(i for i, (g, n, m) in enumerate(up) if n.startswith("BOTTOM")); n0 = up[k][1]
        up[k] = (up[k][0], n0 + f" + cut square to the arm {xc:.1f} mm distal of pin b, clear of the knee sweep",
                 trimesh.Trimesh(np.asarray(mc.vertices) @ HR.T, mc.faces, process=False))
        crep["bottom_watertight_after_cut"] = bool(mc.is_watertight)
    bottom_c = dense(mc)
    print(f"knee sweep in the arm frame: {len(sweep)} points ({swrep}); BOTTOM {crep}", flush=True)
    mount, mrep = BASE.pad_mount_sweep(M, bottom_c, sweep)
    if mount is None: print(f"WARNING: {mrep['note']} -> the nearest-end mount (may meet the sweep)", flush=True); mount, mrep = BASE.pad_mount(M, bottom_c)
    mrep["bottom"] = crep; mrep["sweep"] = swrep
    if mount is not None: parts.append(("H", 5, f"pad mount to BOTTOM (proxy) ({P['tp']:.2f} mm slab at the pad level, arm pad -> the BOTTOM bar, routed clear of the knee sweep)", mount, "ti"))
    def export_mesh(g, mem, m):
        if mem != 5: return m
        return trimesh.Trimesh(np.asarray(m.vertices) @ HR.T, m.faces, process=False)
    sc = trimesh.Scene(); pf = []
    allp = [(g, n, export_mesh(g, mem, m), mat) for g, mem, n, m, mat in parts] + [(g, n, m, "user") for g, n, m in up]
    for i, (g, n, m, mat) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = mat == "user"; mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        rho = STEEL if mat == "steel" else TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else ("steel" if mat == "steel" else "Ti-6Al-4V"),
                       mass_g=None if user else round(vol / 1000 * rho, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)),
                       pieces=None if user else int(len(mm.split(only_watertight=False))), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L1 keep-out", FACES={"1": round(float(M.f[0]), 2), "K": round(float(M.fK), 2), "2": round(float(M.f[1]), 2), "3": round(float(M.f[2]), 2)},
                   parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in ours):.1f} g) + {len(up)} user parts; invalid: "
          f"{[p['name'] for p in ours if not p['valid'] or p['pieces'] != 1] or 'none'}; mount {mrep}; stops {json.dumps(stack['stops'])}", flush=True)
    u1, u2, u3 = D.u; w_d = math.degrees(math.acos(float(np.clip(-u3[1], -1, 1)))); w_a = math.degrees(math.atan2(u3[0], u3[2]))
    az = math.degrees(math.atan2(u1[2], -u1[0])); elv = math.degrees(math.asin(float(np.clip(u1[1], -1, 1))))
    chk = S.circ_int(S.bvec(az, elv), D.A[0], S.w_dir(w_d, w_a), D.A[1], D.branch)
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict((k_, P[k_]) for k_ in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")),
               knee=dict((k_, P[k_]) for k_ in ("lE", "lc", "phiE", "phib", "stk", "ang_min")), knee_mid_m_mm=np.round(D.m, 3).tolist(), hub_r_mm=list(M.hr),
               knuckle=dict(uK=np.round(D.uK, 6).tolist(), bk1=P["bk1"], bk2=P["bk2"], sK=P["sK"], psiA_deg=round(math.degrees(D.psiA), 3), a1max=P["a1max"],
                            dK_stop_B_deg=stack["stops"]["K"]["stop_B_deg"], q2_stops_deg=stack["stops"]["J2"]["q2_stops_deg"], smlo=P["smlo"], smhi=P["smhi"],
                            note="az/el/a/w = the 3R with K on stop A (state A, every clip frame but 8 of Wash opposite shoulder); K opens about uK through GH past J2's stop"))
    pr = {k_: v for k_, v in P0.items()}
    design = dict(id=a.out, source=f"docs/concepts/{ID}.md (Kit-rule re-optimisation, config BDp), {src}, fit on {fbs} {M.B.mode} at fold margin {KIT.FOLD_MARGIN} "
                                   f"= the shape the verifiers wore frozen on Bench(110,360) exact (docs/concepts/verify/minarc-bdp-judge.md: 19.54, score 92.89)",
                  params=pr, n_joints=4, sliding_cuff=False, dof=4,
                  passive=dict(count=2, translations=0, rotations=2, outside_dof_count=True,
                               kind="flat two-pin knee closing the loop at the cuff (pins a, b parallel to J3); set by loop closure, nothing sags. K (in the DOF count) "
                                    "is passive, spring-held on stop A by a clock spring and SENSED (4th encoder)",
                               components=[dict(pin="a", between="member 3 (E boss) / knee link", part="IGLIDUR-PIN: iglidur GSM sleeve + 2 GTM washers on an integral O4 Ti pin, DIN 6799 RS 3.2 e-clip land",
                                                stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]]),
                                           dict(pin="b", between="knee link / arm pad (cuff)", part="IGLIDUR-PIN (as pin a)", stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]])]),
                  joints=[dict(joint="J1", part="O20 x 12.25 v5 hub, MR117-2RS pair", axis_offset_mm=kin["axis_line_offsets_mm"][0]),
                          dict(joint="K", part=f"O20 v5 hub, MR117-2RS pair, cap {CROWN + float(P.get('capK', 0)):.2f} mm (clock spring 0.3 x 5 1.4310 +C1900 >= 145 mm, <= 0.015 N.m/rad, "
                                                f"0.08 N.m preload); stops A / B = O3 dowel in a {stack['stops']['K']['travel_deg']:.1f}-deg arc slot; encoder", axis_offset_mm=0.0, passive=True, sensed=True),
                          dict(joint="J2", part=f"O20 x 12.25 v5 hub, MR117-2RS pair; q2 stops = O3 dowel in a {stack['stops']['J2']['travel_deg']:.1f}-deg arc slot", axis_offset_mm=kin["axis_line_offsets_mm"][1]),
                          dict(joint="J3", part="O20 x 12.25 v5 hub, MR117-2RS pair", axis_offset_mm=kin["axis_line_offsets_mm"][2])],
                  kinematics=kin, base=dict(mount="girdle", chain="minarc_kitrule_bdp", note="base rides the scapula on the user's scapula handler, carried directly at the J1 hub ring (no tab)"),
                  built_with="pipeline/concept_l1/build_minarc_l1.py (L1 keep-out meshes: O20 hub keep-outs incl. hub K's 6 mm taller cap, fitted 8 x 3 straps 1a / 1b / 2, "
                             "stop dowels + arc slots, E strap + boss, knee link, arm pad, pin retainers)",
                  label=f"minarc-stop-knuckle-4r BDp (fit {fbs}, fold margin {KIT.FOLD_MARGIN:g}), L1 keep-out", fit_bench=list(fb), fold_margin=KIT.FOLD_MARGIN,
                  faces_mm=[round(float(x), 2) for x in M.f], fK_mm=round(float(M.fK), 2), tr=round(float(M.tr), 2), stack_mm=stack,
                  bench=dict(near_touch_gap=rep["gap"], **{k_: rep["plain"][k_] for k_ in ("gap", "reach", "follow", "inband14", "contact")}, inband10=rep["inband10"]),
                  note="R17's dynamics judge models the orientation-equivalent spherical 3R with K on stop A (kinematics az/el/a/w); K (opens past J2's stop on "
                       "8 frames of one clip, dK <= 2.2 deg), the J3 line offset and the knee's 2 passive pins are not in its MuJoCo model")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    set_adjacent(parts)
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(params=pr, source=src, bench=f"{fb[0]},{fb[1]}", mode=M.B.mode, fold_margin=KIT.FOLD_MARGIN,
                            report={k_: rep.get(k_) for k_ in ("gap", "plain", "gap_near1", "near1_poses", "min_metal_mm", "inband10", "why", "f", "min_clear_taken",
                                                               "parts_ib14", "knee", "knuckle", "kitrule", "hubs")},
                            m=np.round(D.m, 3).tolist(), tr=round(float(M.tr), 3), fK=round(float(M.fK), 3)),
                   stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"], dowel_check=dowel_check())
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = check_frames(M, dd, parts, stack)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        C, st = BASE.make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=max(M.hr), knuckle=True, **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        ko = {cl["name"]: dict(frames_K_open=sum(1 for f in cl["frames"] if not f["held"] and abs(f.get("knuckle", {}).get("dK", 0)) > 1e-3),
                               dK_max=round(max([abs(f.get("knuckle", {}).get("dK", 0)) for f in cl["frames"] if not f["held"]] or [0]), 2)) for cl in C["clips"]}
        for k_ in st: st[k_]["knuckle"] = ko.get(k_)
        rep_out["clips"] = st; json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"clips.json written ({time.time() - t0:.0f} s); K open on clips: { {k_: v for k_, v in ko.items() if v['frames_K_open']} }", flush=True)
        W = BASE.make_workspace(M, a.jobs); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4),
                                    forced_feasible=int(sum(1 for p in W["poses"] if p["eval_feasible"] and p["knuckle"]["state"] != 0)))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
