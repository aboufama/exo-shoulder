"""Full user-style CAD of the generation-9 winner desmo-conecut-knuckle-3r (round 13's verified winner, not the lead: frozen exact
Bench(110,360) 18.98 / score 93.10 with the built groove's blended law in the IK, claim 19.04 linear IK, held out 23.19, complexity
16.5, ledger WATCH: docs/alignment/desmo-conecut-knuckle-3r.md) -> pipeline/full-exo/designs/user_desmo_conecut/.

desmo-conecut = the gen-8 lead conecut-knee-knuckle-3r with ONLY the K drive changed to the spring-free, roller-free desmodromic drive
(cell B). So this builder is the gen-8 full-CAD builder (user_style_conecut, imported unchanged: the slot-end fix, link 2's 70-deg drop
(machined from solid), link 1a's seat overlap, the J3 stop, the D3 crank stack idea, its checks) on the gen-9 L1's retargeting
(build_desmo_l1, imported unchanged: the VERIFIER's DCModel loaded with --blend, fit on Bench(60,160) fast on the row's best_params =
l1_desmo-conecut), with the drive swapped:

  K hub      plain v5 O20 hub: integral O7 pin on link 1a, MR117 pair, the v5 cap (no clock spring, no arbor, no sensor: K is slaved
             both ways by the drive, never read).
  stage 2    (inverted, cell B) ISO 8734 1.5 m6 x 5 440C nose dowel (a-C:H DLC) pressed radially 2.5 mm in an O5 x 3 Ti boss on link 1a
             at the seat C0 (r_c 16.176, beta -177.169), the boss carried by a 4 x 3 root from hub K's lower plate (60-deg rule ramp);
             it runs in a 1.52-wide slot through the crank's 2.5 mm tip plate (the nose's path in the crank frame, closed end = stop A,
             far end = stop B at dK 46.5). The CAD draws the plate's mid-thickness section extruded along the plate normal; the drawing
             cuts the exact ruled walls (radial lines through GH) by 4-axis UV wire EDM (red team: a straight 2-axis cut is 49 um off).
  crank      (group dk) Ti-6Al-4V, 5-axis machined from solid: O10 x 6 boss on an O3 pivot pin in link 1b (2 x MR63ZZ, D3 axial stack:
             ground inner-ring spacer on an O5 land, shim + wave washer under the DIN 6799 clip), the bent 6 x 3 arm (straight run
             through the model's stations + the arc about hub K, TRIMMED where its section clears the slot by 0.3) ending in the tip
             plate, and the 3 x 1.5 short arm to the stage-1 pin (a_s 9.529, psi 149.71).
  stage 1    a crowned (R 4) O1.5 440C pin pressed through the short arm along u2 runs in a 1.52-wide groove: a 2-axis wire-EDM THROUGH
             slot in a 1.5 mm 440C insert (58-60 HRC) keyed into link 2's J2 ring. THE STACK FIX (the L1's finding 1 / 5 / 6): the
             model puts the groove at the crank pivot level + 3.15 + glev = F2+0.11..1.61, inside link 1b's J2 lower plate, and the
             short arm UNDER link 1b's strap (as modelled stage 1 cannot move in a real stack: every L1 clip frame jams). Built here the
             whole of stage 1 rides ABOVE link 1b (its plate top F+3.0, its strap top <= F+3.16 under the arm): the short arm in a
             relief cut into the underside of link 2's J2 pad over the arm's sweep (in link 2's frame), the insert in a pocket above it,
             link 2's ring as the roof (+ a 0.8 lip over the insert's 0.96 mm outside O20). The groove is cut on the locus of the
             pin's point AT THE BUILT LEVEL through the model's own blended law (dR, phi = |dK| / g, sig, q_on, s_th, blend 10, cut at
             dK_lim): the K law is the verified one exactly; the stage-1 metal sits DELTA higher along u2 than the verified model's
             (glev-equivalent -1.0 + DELTA, build.json stage1) - a metal change for the verifier to re-measure (away from the skin).

Every other part is the gen-8 builder's on THIS model's fit: v5 O20 hubs, link 1a line/arc chain, 4-strip machined bars 1b / 2, O3
dowel-in-arc-slot K (opposed pair) / J2 stops with the slot-end fix, the J3 stop (O2 dowel in member 3, R1.05-ended groove under link
2's J3 ring), member 3 + E strap, the re-proportioned knee link with MR63ZZ-pair bosses + knee stop, BOTTOM cut + pad mount, cuff,
base directly at the J1 hub ring. The judged clips.json / workspace.json are the L1's (l1_desmo-conecut), asserted the same fit.

    OMP_NUM_THREADS=1 nice -n 15 python3 pipeline/conformal/param_cad/user_style_desmo.py [--out user_desmo_conecut] [--l1 l1_desmo-conecut]
        [--skip-base-search] [--no-checks | --checks-only]
"""
import argparse, json, math, os, shutil, sys, time
MY_ARGV = sys.argv[1:]; sys.argv = sys.argv[:1]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "pipeline", "concept_l1"))
os.environ.setdefault("PK_LINK1_MACHINED", "1"); os.environ.setdefault("PK_LINK2_MACHINED", "1")
import user_style_conecut as UC                                                            # noqa: E402  gen-8 full CAD (its import-time fixes; asserts conecut)
import build_desmo_l1 as DL1                                                               # noqa: E402  gen-9 L1: retargets build_slipper_l1 at the verifier's DCModel
USS = UC.USS
assert USS.RL1 is DL1.SL and USS.RL1.ID == "desmo-conecut-knuckle-3r" and USS.RL1.fit is DL1.fit, "build_slipper_l1 not retargeted at desmo"
import numpy as np, cadquery as cq, trimesh                                                # noqa: E402
USM, USP, US, BM, PB = USS.USM, USS.USP, USS.US, USS.BM, USS.PB
RL1 = USS.RL1; LV = USS.LV; T = USS.T; disc, rev, plane, at, xform = USS.disc, USS.rev, USS.plane, USS.at, USS.xform
FULL = USS.FULL; unit = USS.unit
GROUPS = dict(USS.GROUPS)
ID = DL1.ID; PFULL = DL1.PFULL; DS = DL1.DS; RF = DL1.RF; S = DL1.S
J3MIN, J3MAX = DL1.J3MIN, DL1.J3MAX
UP = float(LV["U0"])                                                                       # 3.15: the upper member's underside over the joint face
RUNG = float(DL1.RUNG)                                                                     # 0.15 running gap
GW, RW, PIN_D, SARM_W = DS.GROOVE_W, DS.RING_WALL, DS.PIN_D, DS.ARM_W                      # 1.52 groove, 0.8 ring wall, O1.5 pin, short arm 3 wide
GD, ROOF, S1_T = 1.5, 0.8, 1.5                                                             # insert thickness (= groove depth, through slot), roof lip, short arm
INS_RIN = 6.05                                                                             # insert inner edge (bearing seat r 5.5 + 0.55 wall; groove >= 6.455)
REL_RIN = 6.05                                                                             # relief inner edge in link 2's J2 pad
PIN_TIP_CLR, CROWN_R = 0.10, 4.0                                                           # pin tip under the roof (+ the drift), crown radius
BOSS_R, BOSS_H = 5.0, float(DL1.SL.BOSS_H)                                                 # crank boss O10 x 6 (the model's / L1's)
BRG_R, BRG_W, PIN_R, BORE_R = 3.0, 2.5, 1.5, 1.6                                           # 2 x MR63ZZ 3x6x2.5 seats at both boss ends, O3 pin, O3.2 web bore
SPACER_RI, SPACER_RO, SPACER_T, LAND_R = 1.55, 1.95, 0.175, 2.5                            # D3 spacer O3.1 x O3.9 (MR63ZZ inner ring) on an O5 land
SHIM_T, WAVE_T, WAVE_RO, CLIP_DZ, CLIP_T = 0.10, 0.20, 2.9, 0.30, 0.6                     # D3 shim + wave washer, clip at ztop + 0.30
PLATE_T, NOSE_LO, NOSE_TIP_CLR = DL1.PLATE_T, DL1.NOSE_LO, DL1.NOSE_TIP_CLR                # tip plate 2.5; nose dowel C0-1.0 .. plate top - 0.15
RC_GROOVE = 1.0                                                                            # the verified groove's centreline radius (1.007: ridge 0.247) - reported against
SHORT_ROOT = float(DL1.SL.ARM_ROOT)                                                        # 4.0: the short arm starts inside the boss wall


# ---------------------------------------------------------------------------------------------------- sketch helper: a slot of half width hw
def _turn(T2, a, b):
    return abs(math.atan2(T2[a, 0] * T2[b, 1] - T2[a, 1] * T2[b, 0], float(T2[a] @ T2[b])))


def slot_wire(wp, C2, hw, max_turn=math.radians(10.0), max_len=0.8, caps=True):
    """closed contour (lines + 3-point arcs) of the slot of half width hw about the dense planar centreline C2 (n x 2): both offsets
    as arcs through each segment's start / mid / end offset points (segments <= max_turn of turning and <= max_len long), semicircular
    end caps. Returns (workplane with the closed wire, report)"""
    C2 = np.asarray(C2, float); L0 = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(C2, axis=0), axis=1))]
    ss = np.linspace(0.0, L0[-1], max(int(L0[-1] / 0.02), 60) + 1)                         # uniform in arc length (drops sub-0.02 mm hooks: the
    C2 = np.c_[np.interp(ss, L0, C2[:, 0]), np.interp(ss, L0, C2[:, 1])]                    # nose path's relative pole at stop A)
    d = np.gradient(C2, axis=0); T2 = d / np.linalg.norm(d, axis=1)[:, None]; N2 = np.c_[-T2[:, 1], T2[:, 0]]
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(C2, axis=0), axis=1))]; n = len(C2); idx = [0]
    for i in range(2, n):
        if s[i] - s[idx[-1]] >= max_len or _turn(T2, idx[-1], i) >= max_turn: idx.append(i)
    if n - 1 - idx[-1] < 2: idx[-1] = n - 1
    else: idx.append(n - 1)
    R_, L_ = C2 - hw * N2, C2 + hw * N2

    def seg(w, P, a, b):
        m = (a + b) // 2; p0, p1, p2 = P[a], P[m], P[b]
        cr = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])
        return w.lineTo(*map(float, p2)) if abs(cr) < 1e-9 or m in (a, b) else w.threePointArc(tuple(map(float, p1)), tuple(map(float, p2)))
    w = wp.moveTo(*map(float, R_[0]))
    for a, b in zip(idx[:-1], idx[1:]): w = seg(w, R_, a, b)
    w = w.threePointArc(tuple(map(float, C2[-1] + hw * T2[-1])), tuple(map(float, L_[-1])))
    for a, b in reversed(list(zip(idx[:-1], idx[1:]))): w = seg(w, L_, b, a)
    w = w.threePointArc(tuple(map(float, C2[0] - hw * T2[0])), tuple(map(float, R_[0])))
    # the arcs' deviation from the exact offsets (each arc vs the dense offset points it spans)
    dev = 0.0
    for P in (R_, L_):
        for a, b in zip(idx[:-1], idx[1:]):
            m = (a + b) // 2; c = _circ(P[a], P[m], P[b])
            if c is None: continue
            dev = max(dev, float(np.abs(np.linalg.norm(P[a:b + 1] - c[0], axis=1) - c[1]).max()))
    return w.close(), dict(arcs_per_side=len(idx) - 1, max_dev_from_exact_offset_mm=round(dev, 5), length_mm=round(float(s[-1]), 3))


def _circ(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c; dd = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(dd) < 1e-12: return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / dd
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / dd
    cc = np.array([ux, uy]); return cc, float(np.linalg.norm(np.asarray(a) - cc))


def sector(pl, r0, r1, a0, a1, h):
    """annular sector r0..r1 over a0..a1 (rad) in the plane pl (two arcs + two radial lines), extruded h"""
    P = lambda r, a: (r * math.cos(a), r * math.sin(a)); m = 0.5 * (a0 + a1)
    wp = (cq.Workplane(pl).moveTo(*P(r0, a0)).lineTo(*P(r1, a0)).threePointArc(P(r1, m), P(r1, a1)).lineTo(*P(r0, a1))
          .threePointArc(P(r0, m), P(r0, a0)).close())
    return wp.extrude(h).val()


def valid1(s): return bool(s.isValid() and len(s.Solids()) == 1)


def clean(s):
    try:
        c = s.clean(); return c if c.isValid() else s
    except Exception: return s


# ---------------------------------------------------------------------------------------------------- hubs: K plain (no clock spring)
def hubs(M):
    """v5 O20 hubs at J1 / K / J2 / J3 with the v5 cap (torispherical dome) on each; K: NO clock spring, no arbor (slaved, never read)"""
    Uu, C, F4, hr = BM.joints4(M); out = []; rep = {}
    for J, j, lo, hi in (("J1", 0, "l1a", "base"), ("K", 1, "l1a", "l1b"), ("J2", 2, "l1b", "l2"), ("J3", 3, "l3", "l2")):
        for g, n, s in US.hardware(J, Uu[j], F4[j], lo, hi):
            if " cap " in n: continue
            out.append((g, n, at(s, C[j])))
        cap, Rc = USM.cap_v5(Uu[j], F4[j]); rep.setdefault("caps", {})[J] = "flat" if Rc is None else f"dome R{Rc:.1f}"
        nm = (f"{J} cap O20, torispherical dome R{Rc:.1f} / R1 (tangent arcs)" if Rc else f"{J} cap O20 x crown F+12.25, flat crown") + ", threaded M18x0.5 (Ti-6Al-4V)"
        if J == "K": nm = nm.replace("(Ti-6Al-4V)", "- NO clock spring: K is held both ways by the desmo drive (slaved to q2, never read) (Ti-6Al-4V)")
        out.append((hi, nm, at(cap, C[j])))
    rep["K"] = "plain v5 hub + cap: no clock spring, no arbor, no sensor (desmo: positive both ways)"
    return out, rep


# ---------------------------------------------------------------------------------------------------- link 1a: plain K pin + the nose boss
def link1a_body(M, stops, lug):
    """UC.link1a_body (copied) with link 1a's K pin the plain v5 integral O7 pin (US.lower_pin: no spring arbor, no slit) and the nose
    boss + its root fused (lug); K's opposed stop slots cut after"""
    Uu, C, F4, hr = BM.joints4(M); H = lambda j: C[j] + F4[j] * Uu[j]
    ex, ey, start, segs, info = USS.link1a_path(M)
    bar = US.bar_swept(ex, ey, start, segs, t=T, w=USS.W, r=0.3)
    padA = USP.plate_R(Uu[0], F4[0], ey, USS.W, hr[0], L=info["seat_J1_mm"], rf=USS.L1A["rf"])
    sd_b = info["sd_b"][0] * ex + info["sd_b"][1] * ey
    padB = USP.plate_R(Uu[1], F4[1], sd_b, USS.W, hr[1], L=info["seat_K_mm"] + UC.SEAT_K_OVERLAP, rf=USS.L1A["rf"])
    body = US.glue(US.glue(padA, bar), padB)
    body = body.fuse(US.lower_pin(Uu[0], F4[0])).fuse(at(US.lower_pin(Uu[1], F4[1]), C[1]))
    if lug is not None:
        for s_ in lug: body = body.fuse(s_)
    q_lo, q_hi = stops["K"]["q"]
    for th in stops["K"]["homes"]: body = body.cut(USM.arc_slot_cutter(H(1), Uu[1], th + q_lo, th + q_hi, -1.0, BM.PLATE + 0.1))
    body = clean(body)
    info.update(vs_model=USS.link1a_vs_model(M, ex, ey, start, segs), valid=body.isValid(), solids=len(body.Solids()), seat_K_overlap_mm=UC.SEAT_K_OVERLAP)
    info.pop("sd_b")
    return body, info


USS.link1a_body = link1a_body                                                              # USS.build_links calls it by its module-global name


def nose_boss(M, G):
    """link 1a's O5 x 3 nose boss (radial at C0, R0 -1.5..+1.5) + its 4 x 3 root: a side-view sketch (lines + R2 tangent arcs) in the
    plane (hub K's axis, the radial direction to C0), extruded 4 across: flush with the K lower plate (F+0..3) out to r 10.4 (under
    link 1b's K member at F+3.15), a <= 40-deg ramp outside hub K's O20 to the boss underside, then level under the boss; the nose
    dowel's reamed O1.5 hole (radial, 2.5 deep from C0 - 1.0)"""
    Uu, C, F4, hr = BM.joints4(M); uK = unit(Uu[1]); FK = float(F4[1]); C0 = np.asarray(G["C0"], float); cr = unit(C0); R0 = float(G["R0"]); rb = float(G["rb"])
    boss = disc(C0, cr, rb, -1.5, 1.5)
    db = unit(C0 - (C0 @ uK) * uK); wb = np.cross(uK, db); sC = float(C0 @ db); zC = float(C0 @ uK) - FK
    zb_bot = float((C0 * (R0 - 1.5) / R0) @ uK) - FK                                       # the boss underside centre over hub K's face
    s_ramp0 = S.HUB_R + 0.4; z_top = zb_bot - 0.6; s_ramp1 = s_ramp0 + max(z_top / math.tan(math.radians(40.0)), 0.5)
    pts = [(9.5, 0.0), (s_ramp0, 0.0), (s_ramp1, z_top), (sC + 1.0, z_top), (sC + 1.0, z_top + 3.0), (s_ramp1 - 0.3, z_top + 3.0),
           (s_ramp0 - 0.4, 3.0), (9.5, 3.0)]
    pts = [(s_, z_ + FK) for s_, z_ in pts]
    rad = [0.0, 2.0, 2.0, 0.0, 0.0, 2.0, 2.0, 0.0]; rad = USP.safe_radii(pts, rad)
    root = USP.prism(np.zeros(3), db, uK, pts, rad, 2 * (rb - 0.5), both=True)
    hole = disc(C0, cr, PIN_D / 2, NOSE_LO - 0.3, 1.6)
    info = dict(boss_d_mm=2 * rb, boss_radial_mm=[round(R0 - 1.5, 3), round(R0 + 1.5, 3)], boss_rK_mm=round(sC, 3), boss_centre_over_hubK_face_mm=round(zC, 3),
                root=dict(w_mm=2 * (rb - 0.5), flush_with_K_plate_to_r_mm=s_ramp0, ramp_deg=round(math.degrees(math.atan2(z_top, s_ramp1 - s_ramp0)), 1),
                          level_under_boss_mm=[round(z_top, 3), round(z_top + 3.0, 3)]))
    return boss, root, hole, info


def nose_dowel(G):
    C0 = np.asarray(G["C0"], float); cr = unit(C0); r = float(G["nr2"]); z0, z1 = NOSE_LO, (G["rPu"] + PLATE_T - NOSE_TIP_CLR) - G["R0"]; ch = 0.1
    return rev([(0, z0), (r - ch, z0), (r, z0 + ch), (r, z1 - ch), (r - ch, z1), (0, z1)], C0, cr), [z0, z1]


# ---------------------------------------------------------------------------------------------------- stage 1 at the BUILT level
def pin_search(M, G, hm_abs, a_ref, psi_ref):
    """the stage-1 pin point at the BUILT groove level hm_abs (along u2 from GH): the model's own parametrisation F = s0 dR + a_s v(psi)
    with s0 set by the level (the model's glev rule), searched over (a_s, psi) for the lowest pressure angle on the model's own formula
    (pin side paF over the stroke, cap / back-drive side paC past the blend, gate 43 - atan mu) with the pitch inside the model's
    gates [R_LO, R_HI] and the groove's outer wall inside the verified r_out (pitch <= 9.40), drift <= 0.6. The groove is then
    re-synthesised for that pin through the SAME blended law (dwell, blend, rise, cut at dK_lim): the K law is the verified one exactly;
    the force geometry is re-gated here (the model's pin extended along its own axis to this level fails the gate from K 24: PA 52.9)"""
    g = M._scg; D = M.D; u2 = unit(D.u[1]); dR, sig, gg, cc, kgrid = g["dR"], g["sig"], g["g"], g.get("c", 0.0), g["kgrid"]; lim = float(g["dK_lim"])
    mu = float(D.p.get("mu", 0.15)); PAC = 43.0 - math.degrees(math.atan(mu)); s_th = float(G["s_th"])
    hb = math.radians(float(D.p["blend"])) / abs(s_th) / 2.0                                  # the blend's end in K (rad)
    jt = int(np.searchsorted(kgrid, lim + 1e-12)); k = kgrid[:jt]; nk = len(k)
    ph = sig * RF.phi_of(k, gg, cc); dph = sig * RF.dphi_of(k, gg, cc); RC = S.rotm(dR, ph)
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); R_HI_B = min(DS.R_HI, 9.40)
    # the groove planform per candidate (link 2's frame, the blended law over the J2 window) for its curvature: rc >= RC_GROOVE (no cusp;
    # the model's own groove: rc 1.01-1.37 over the blend, ridge >= 0.25 for the red team's Hertz)
    q_on = float(G["q_on"]); qa, qb = [float(x) for x in M._lg["J2"][:2]]; sa = abs(s_th)
    xg = np.arange(min((qa - q_on) / s_th, (qb - q_on) / s_th) - math.radians(1.0) / sa, lim + 1e-9, math.radians(0.1) / sa)
    Kx = np.minimum(np.where(xg <= -hb, 0.0, np.where(xg >= hb, xg, (xg + hb) ** 2 / (4 * hb))), lim)
    Mx = np.einsum("xij,xjk->xik", S.rotm(u2, -(q_on + s_th * xg)), S.rotm(dR, sig * RF.phi_of(Kx, gg, cc))); ge2, gf2 = USM.frame2(u2)
    def rc_min_of(Fp):
        Gx = np.einsum("xij,pj->pxi", Mx, Fp); X, Y = Gx @ ge2, Gx @ gf2
        dx, dy = np.gradient(X, axis=1), np.gradient(Y, axis=1); ddx, ddy = np.gradient(dx, axis=1), np.gradient(dy, axis=1)
        kap = np.abs(dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); return 1.0 / np.maximum(kap.max(1), 1e-9)
    def evaluate(a, ps):
        v = np.cos(ps)[:, None] * e1 + np.sin(ps)[:, None] * e2; s0 = (hm_abs - a * (v @ u2)) / float(dR @ u2); Fp = s0[:, None] * dR + a * v   # (np, 3)
        C = np.einsum("kij,pj->pki", RC, Fp)                                                  # (np, nk, 3)
        vF = dph[None, :, None] * np.cross(dR, C); vcap = s_th * np.cross(u2, C); n1 = np.cross(vF - vcap, u2); n1 /= np.linalg.norm(n1, axis=2, keepdims=True)
        ang = lambda A, B: np.degrees(np.arccos(np.clip(np.einsum("pki,pki->pk", A, B) / (np.linalg.norm(A, axis=2) * np.linalg.norm(B, axis=2) + 1e-12), -1, 1)))
        paF = DS._fold(ang(n1, vF)); paC = DS._fold(ang(n1, vcap)); rho = np.linalg.norm(C - (C @ u2)[..., None] * u2, axis=2); z = C @ u2 - hm_abs
        return Fp, paF, paC, rho, z
    best = None; rows = []
    for a in np.arange(7.0, 12.0001, 0.05):
        ps = np.radians(np.arange(40.0, 260.0001, 0.5)); Fp, paF, paC, rho, z = evaluate(a, ps)
        ok = (rho.min(1) >= DS.R_LO) & (rho.max(1) <= R_HI_B) & (np.abs(z).max(1) <= DS.DRIFT_MAX)
        m = np.maximum(paF.max(1), np.where(k[None, :] >= hb, paC, 0.0).max(1))
        ok &= m <= PAC                                                                     # the drive must MOVE at the claim's mu (no bind)
        rcm = np.full(len(ps), 0.0)
        if ok.any(): rcm[ok] = rc_min_of(Fp[ok]); ok &= rcm > GW / 2 + 0.01                 # no cusp (the groove can be cut)
        obj = -rcm + 0.002 * m                                                             # then the roundest groove (the ridge carries the Hertz)
        for j in np.nonzero(ok)[0]:
            if best is None or obj[j] < best[0]: best = (float(obj[j]), float(a), float(ps[j]), Fp[j], float(paF[j].max()), float(np.where(k >= hb, paC[j], 0).max()),
                                                         float(paC[j].max()), [float(rho[j].min()), float(rho[j].max())], float(np.abs(z[j]).max()), float(rcm[j]))
    if best is None: raise RuntimeError("stage-1 pin search: no (a_s, psi) at this level passes the model's pitch / drift / PA gates without a cusp")
    o, a, ps, Fp, pF, pC, pCall, pr, dz, rcb = best
    # stage-1 crank-free K play (the red team's / model's reading): the pin floats c per side across the groove (crank free, q2 held) ->
    # the crank turns c / (|dR x C| cos paF) -> K turns g times that (the model's 0.174 deg at c 0.01 reproduces this way)
    _, paF1, _, _, _ = evaluate(a, np.array([ps])); C1 = np.einsum("kij,j->ki", RC, Fp); arm = np.linalg.norm(np.cross(dR, C1), axis=1)
    play = lambda c_: float(np.degrees(gg * c_ / (arm * np.cos(np.radians(paF1[0]))).max()))
    _, paFm, _, _, _ = evaluate(float(M.D.p["a_s"]), np.array([math.radians(float(M.D.p["psi"]))]))
    Fm = np.asarray(G["F0"], float); Cm = np.einsum("kij,j->ki", RC, Fm); armm = np.linalg.norm(np.cross(dR, Cm), axis=1)
    play_m = float(np.degrees(gg * 0.01 / (armm * np.cos(np.radians(paFm[0]))).max()))
    kplay = dict(crank_free_nominal_c0p01_deg=round(play(0.01), 3), crank_free_worst_c0p015_deg=round(play(0.015), 3), model_pin_same_rule_deg=round(play_m, 3),
                 rule="dK = g c / (|dR x C| cos paF) over the stroke, max; + the stage-2 slot slop 0.04 (crank held; stage 2 unchanged)",
                 band_nominal_deg=round(play(0.01) + 0.04, 3), band_worst_deg=round(play(0.015) + 0.04 * 1.5, 3))
    return Fp, dict(a_s=round(a, 3), psi_deg=round(math.degrees(ps), 2), model_a_s=round(a_ref, 3), model_psi_deg=round(psi_ref, 2), pa_pin_max=round(pF, 2),
                    pa_cap_max_past_blend=round(pC, 2), pa_cap_max_in_blend=round(pCall, 2), pa_gate_mu=round(PAC, 2), mu=mu,
                    gates_by_mu={f"{m_:g}": round(43.0 - math.degrees(math.atan(m_)), 2) for m_ in (0.087, 0.12, 0.15, 0.17)}, pitch_mm=[round(x, 3) for x in pr],
                    drift_mm=round(dz, 3), blend_end_K_deg=round(math.degrees(hb), 2), k_play=kplay, groove_rc_min_search_mm=round(rcb, 3),
                    model_groove_rc_min_mm=round(float(rc_min_of(np.asarray(G["F0"], float)[None])[0]), 3), rc_gate_mm=RC_GROOVE,
                    note="the model's pin (a_s 9.529, psi 149.71) at the model level: pa_pin_max 33.74, pa_cap 35.05 (in the blend, ungated); the same pin "
                         "EXTENDED along its own axis to this level: pa_pin 52.86 (over the gate from K 24: binds) - so the built pin is re-placed")


def level_scan(M, G, levels, step_a=0.1, step_psi=1.0):
    """can stage 1 be LIFTED out of link 1b's J2 lower-plate layer at the verified law? For each groove mid-plane level (over hub 2's
    face), the pin point re-placed over (a_s 7..12, psi 40..260) through the model's own formula: max pressure angle (pin side over the
    stroke, cap side past the blend) vs the gate 43 - atan(mu 0.15) = 34.47, and the re-synthesised groove's min centreline radius vs the
    verified groove's 1.007 (ridge 0.247: the red team's Hertz case); pitch in the model's [R_LO, R_HI], drift <= 0.6. Rows [a_s, psi,
    max PA, rc_min, pitch lo, pitch hi]"""
    g = M._scg; D = M.D; u2 = unit(D.u[1]); dR, sig, gg, cc, kgrid = g["dR"], g["sig"], g["g"], g.get("c", 0.0), g["kgrid"]; lim = float(g["dK_lim"])
    mu = float(D.p.get("mu", 0.15)); PAC = 43.0 - math.degrees(math.atan(mu)); s_th = float(G["s_th"]); hb = math.radians(float(D.p["blend"])) / abs(s_th) / 2.0
    jt = int(np.searchsorted(kgrid, lim + 1e-12)); k = kgrid[:jt]; ph = sig * RF.phi_of(k, gg, cc); dph = sig * RF.dphi_of(k, gg, cc); RC = S.rotm(dR, ph)
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); q_on = float(G["q_on"]); qa, qb = [float(x) for x in M._lg["J2"][:2]]; sa = abs(s_th)
    xg = np.arange(min((qa - q_on) / s_th, (qb - q_on) / s_th) - math.radians(1.0) / sa, lim + 1e-9, math.radians(0.1) / sa)
    Kx = np.minimum(np.where(xg <= -hb, 0.0, np.where(xg >= hb, xg, (xg + hb) ** 2 / (4 * hb))), lim)
    Mx = np.einsum("xij,xjk->xik", S.rotm(u2, -(q_on + s_th * xg)), S.rotm(dR, sig * RF.phi_of(Kx, gg, cc))); ge2, gf2 = USM.frame2(u2)
    Uu, C, F4, hr = BM.joints4(M); H2 = float((np.asarray(C[2], float) + F4[2] * unit(Uu[2])) @ u2); out = []
    for lev in levels:
        hm = H2 + lev; R = []
        for a in np.arange(7.0, 12.0001, step_a):
            ps = np.radians(np.arange(40.0, 260.0001, step_psi)); v = np.cos(ps)[:, None] * e1 + np.sin(ps)[:, None] * e2
            Fp = ((hm - a * (v @ u2)) / float(dR @ u2))[:, None] * dR + a * v; Cc = np.einsum("kij,pj->pki", RC, Fp)
            vF = dph[None, :, None] * np.cross(dR, Cc); vcap = s_th * np.cross(u2, Cc); n1 = np.cross(vF - vcap, u2); n1 /= np.linalg.norm(n1, axis=2, keepdims=True)
            ang = lambda A, B: np.degrees(np.arccos(np.clip(np.einsum("pki,pki->pk", A, B) / (np.linalg.norm(A, axis=2) * np.linalg.norm(B, axis=2) + 1e-12), -1, 1)))
            paF = DS._fold(ang(n1, vF)); paC = DS._fold(ang(n1, vcap)); rho = np.linalg.norm(Cc - (Cc @ u2)[..., None] * u2, axis=2); z = Cc @ u2 - hm
            ok = (rho.min(1) >= DS.R_LO) & (rho.max(1) <= DS.R_HI) & (np.abs(z).max(1) <= DS.DRIFT_MAX)
            m = np.maximum(paF.max(1), np.where(k[None, :] >= hb, paC, 0.0).max(1))
            Gx = np.einsum("xij,pj->pxi", Mx, Fp); X, Y = Gx @ ge2, Gx @ gf2; dx, dy = np.gradient(X, axis=1), np.gradient(Y, axis=1)
            kap = np.abs(dx * np.gradient(dy, axis=1) - dy * np.gradient(dx, axis=1)) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc = 1.0 / np.maximum(kap.max(1), 1e-9)
            for j in np.nonzero(ok)[0]: R.append((a, math.degrees(ps[j]), m[j], rc[j], rho[j].min(), rho[j].max()))
        R = np.array(R); f1 = R[R[:, 2] <= PAC] if len(R) else R; f2 = R[R[:, 3] >= RC_GROOVE] if len(R) else R
        out.append(dict(level_over_hub2_face_mm=lev, candidates=int(len(R)), pa_ok=int(len(f1)), rc_ok=int(len(f2)),
                        feasible_pa_and_rc=int(((R[:, 2] <= PAC) & (R[:, 3] >= RC_GROOVE)).sum()) if len(R) else 0,
                        best_rc_with_pa_ok=(np.round(f1[np.argmax(f1[:, 3])], 3).tolist() if len(f1) else None),
                        best_pa_with_rc_ok=(np.round(f2[np.argmin(f2[:, 2])], 3).tolist() if len(f2) else None)))
        print(f"  level scan F+{lev:.2f}: {out[-1]}", flush=True)
    return dict(rule=level_scan.__doc__.split("?")[1].strip(), gate_deg=round(PAC, 2), rc_floor_mm=RC_GROOVE, model_level_mm=round(float(G["hmid"]) - H2, 3), levels=out)


def stage1_layout(M, G, l1b_body, dg):
    """the stage-1 levels (over hub 2's face F2, along u2) from the BUILT link 1b: the short arm's footprint over the crank's swing,
    link 1b's highest metal under it (its J2 plate top F+3.0, its strap), + RUNG + the pin's axial drift -> arm, relief, insert, pin;
    the pin point re-searched at the built groove level (pin_search); DELTA = the built groove mid-plane - the model's"""
    from scipy.spatial import cKDTree
    D = M.D; u2 = unit(D.u[1]); Uu, C, F4, hr = BM.joints4(M); c2 = np.asarray(C[2], float); perp = c2 - (c2 @ u2) * u2
    assert np.linalg.norm(perp) < 1e-6, f"J2 axis must pass through GH (off by {perp})"
    H2 = float((c2 + F4[2] * unit(Uu[2])) @ u2)                                            # hub 2's face along u2 from GH
    dR, gg, cc, sig = G["dR"], M._scg["g"], M._scg.get("c", 0.0), M._scg["sig"]
    used = G["Kb"] <= G["lim"] + 1e-12; dz = float(np.abs(G["z"][used]).max())
    F0 = np.asarray(G["F0"], float); hmid = float(G["hmid"])
    vs, fs = l1b_body.tessellate(0.05, 0.3); V = np.array([[v.x, v.y, v.z] for v in vs]); m1b = trimesh.Trimesh(V, np.array(fs), process=False)
    P1b = np.r_[V, trimesh.sample.sample_surface_even(m1b, 80000, seed=7)[0]]
    e2, f2 = USM.frame2(u2); Tp = cKDTree(np.c_[P1b @ e2, P1b @ f2]); h1b = P1b @ u2
    phis = sig * RF.phi_of(np.linspace(0.0, float(G["lim"]), 24), gg, cc)

    def arm_geo_for(Fpin):
        def arm_geo(hlev):
            A0 = (H2 + hlev) / float(dR @ u2) * dR; Fp = Fpin - (Fpin @ u2) * u2 + (H2 + hlev) * u2
            al = unit((Fp - A0) - ((Fp - A0) @ u2) * u2); ac = np.cross(u2, al); L = float(np.linalg.norm((Fp - A0) - ((Fp - A0) @ u2) * u2))
            return A0, al, ac, L
        return arm_geo

    def levels(Fpin, dz_):
        A0, al, ac, L = arm_geo_for(Fpin)(4.0)
        fp = np.array([A0 + t_ * al + w_ * ac for t_ in np.linspace(SHORT_ROOT, L + SARM_W / 2, 30) for w_ in np.linspace(-SARM_W / 2, SARM_W / 2, 5)])
        tops = []
        for ph in phis:
            R = S.rotm(dR, float(ph))[0]; Q = fp @ R.T
            for nb in Tp.query_ball_point(np.c_[Q @ e2, Q @ f2], 0.5):
                if nb: tops.append(float(h1b[nb].max()) - H2)
        top = max(tops) if tops else 3.0
        h_ab = max(top, 3.0) + RUNG + dz_; h_at = h_ab + S1_T; h_rel = h_at + RUNG + dz_; h_ins = h_rel + GD
        return dict(l1b_top_under_arm=top, h_ab=h_ab, h_at=h_at, h_rel=h_rel, h_ins=h_ins, h_tip=h_ins - PIN_TIP_CLR - dz_, hmid_new=h_rel + GD / 2)
    P = M.D.p; Lv = levels(F0, dz); Fp, srch = None, None
    for it in range(3):
        Fp, srch = pin_search(M, G, H2 + Lv["hmid_new"], float(P["a_s"]), float(P["psi"]))
        dz_n = max(srch["drift_mm"], 0.05); Lv2 = levels(Fp, dz_n)
        if abs(Lv2["hmid_new"] - Lv["hmid_new"]) < 0.02: Lv = Lv2; dz = dz_n; break
        Lv = Lv2; dz = dz_n
    delta = (H2 + Lv["hmid_new"]) - hmid
    return dict(u2=u2, H2=H2, dz=dz, delta=delta, F0n=Fp, pin_search=srch, arm_geo=arm_geo_for(Fp), **Lv)


def stage1_layout_model(M, G):
    """stage 1 AT THE VERIFIED MODEL'S LEVELS (the L1's): groove mid-plane = the crank pivot level + 3.15 + glev (F2+0.861), the 440C
    groove layer F+0.11..1.61 under a Ti roof to F+3.65 (one with link 2's J2 pad), the short arm 1.5 thick from the model's pin point
    down (F-1.83..-0.33), the pin F-1.83..+1.22 (tip 0.10 + the drift under the roof): the verified metal. It crosses link 1b's J2
    lower plate and strap (the L1's finding 1 / 5); build.json stage1_level_scan says why no buildable level was found"""
    D = M.D; u2 = unit(D.u[1]); Uu, C, F4, hr = BM.joints4(M); H2 = float((np.asarray(C[2], float) + F4[2] * unit(Uu[2])) @ u2)
    used = G["Kb"] <= G["lim"] + 1e-12; dz = float(np.abs(G["z"][used]).max()); hmid = float(G["hmid"]) - H2; F0 = np.asarray(G["F0"], float); dR = G["dR"]
    h_rel = hmid - GD / 2; h_ins = h_rel + GD; h_at = h_rel - RUNG - dz; h_ab = h_at - S1_T; h_tip = h_ins - PIN_TIP_CLR - dz

    def arm_geo(hlev):
        A0 = (H2 + hlev) / float(dR @ u2) * dR; Fp = F0 - (F0 @ u2) * u2 + (H2 + hlev) * u2
        al = unit((Fp - A0) - ((Fp - A0) @ u2) * u2); ac = np.cross(u2, al); L = float(np.linalg.norm((Fp - A0) - ((Fp - A0) @ u2) * u2))
        return A0, al, ac, L
    return dict(u2=u2, H2=H2, dz=dz, delta=0.0, F0n=F0, pin_search=None, arm_geo=arm_geo, l1b_top_under_arm=None, h_ab=h_ab, h_at=h_at, h_rel=h_rel,
                h_ins=h_ins, h_tip=h_tip, hmid_new=hmid, mode="model", roof_top=UP + 0.5)


def groove_line(M, G, lay, lg):
    """the stage-1 groove centreline in link 2's home frame for the pin's point at the BUILT level (F0 + DELTA u2), through the model's
    own blended law (desmo_geom's x / blend / cut at dK_lim) with the dwell run over the whole J2 window (+-1 deg of q2: the L1's
    finding 7, the dwell stopped 6.2 deg short of the folded stop); returns the dense 2D centreline (e2, f2) about hub 2's axis"""
    u2 = lay["u2"]; P = M.D.p; g = M._scg; dR, sig, gg, cc = g["dR"], g["sig"], g["g"], g.get("c", 0.0); lim = float(g["dK_lim"])
    s_th, q_on = G["s_th"], G["q_on"]; sa = max(abs(s_th), 1e-6); bw = math.radians(float(P["blend"])); hb = bw / abs(s_th) / 2.0 if bw > 0 else 0.0
    qa, qb = [x for x in lg["J2"][:2]]
    x_lo = min((qa - q_on) / s_th, (qb - q_on) / s_th, float(G["x"][0])) - math.radians(1.0) / sa
    x = np.arange(x_lo, lim + 1e-9, math.radians(0.05) / sa); qs = q_on + s_th * x
    Kb = np.where(x <= -hb, 0.0, np.where(x >= hb, x, (x + hb) ** 2 / (4 * hb))) if hb > 0 else np.maximum(x, 0.0)
    Kb = np.minimum(Kb, lim)
    keep = Kb < lim - 1e-12; keep[np.argmax(~keep) if (~keep).any() else -1] = True; x, qs, Kb = x[keep], qs[keep], Kb[keep]
    F0n = lay["F0n"]
    Cq = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)), F0n)
    G2 = np.einsum("nij,nj->ni", S.rotm(u2, -qs), Cq)
    e2, f2 = USM.frame2(u2); P2 = np.c_[G2 @ e2, G2 @ f2]; z = G2 @ u2 - (lay["H2"] + lay["hmid_new"])
    return dict(P2=P2, G2=G2, Kb=Kb, qs=qs, z=z, e2=e2, f2=f2, q2_deg=[round(math.degrees(float(qs.min())), 3), round(math.degrees(float(qs.max())), 3)])


def stage1_parts(M, G, lay, gl, lg, dg):
    """the 440C groove insert (l2), link 2's relief + pocket + roof lip cutters, the short arm (dk, fused with the crank) and the crowned pin"""
    u2, H2 = lay["u2"], lay["H2"]; e2, f2 = gl["e2"], gl["f2"]; P2 = gl["P2"]
    az = np.unwrap(np.arctan2(P2[:, 1], P2[:, 0])); rho = np.linalg.norm(P2, axis=1); hw = GW / 2
    i0, i1 = int(np.argmin(az)), int(np.argmax(az))
    m0 = math.asin(min(1.0, (hw + RW) / float(rho[i0]))) + math.radians(0.5); m1 = math.asin(min(1.0, (hw + RW) / float(rho[i1]))) + math.radians(0.5)
    a0, a1 = float(az.min()) - max(m0, math.radians(3)), float(az.max()) + max(m1, math.radians(3))
    r_out = float(rho.max()) + hw + RW
    pl = lambda h: plane(H2 * u2 + h * u2, e2, f2)
    ins = sector(pl(lay["h_rel"]), INS_RIN, r_out, a0, a1, GD)
    wpS, sl_rep = slot_wire(cq.Workplane(pl(lay["h_rel"] - 0.2)), P2, hw)
    slot = wpS.extrude(GD + 0.4).val(); ins0 = ins
    ins = clean(ins.cut(slot))
    dbg = dict(sector_valid=valid1(ins0), slot_valid=bool(slot.isValid()), slot_solids=len(slot.Solids()), insert_valid=bool(ins.isValid()), insert_solids=len(ins.Solids()))
    print(f"  insert debug: {dbg}", flush=True)
    # the built groove centreline's smallest radius of curvature (the red team's ridge: radius - GW/2 on the inner wall)
    dx, dy = np.gradient(P2[:, 0]), np.gradient(P2[:, 1]); ddx, ddy = np.gradient(dx), np.gradient(dy)
    kap = np.abs(dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc_min = float(1.0 / max(kap.max(), 1e-9))
    # the short arm's sweep in link 2's frame: crank swing phi(K(q2)) about dR, then -q2 about u2, over the J2 window +-1 deg
    A0, al, ac, L = lay["arm_geo"](0.5 * (lay["h_ab"] + lay["h_at"]))
    pin_c = A0 + L * al
    fp = np.array([A0 + t_ * al + w_ * ac for t_ in np.linspace(SHORT_ROOT, L + SARM_W / 2, 40) for w_ in np.linspace(-SARM_W / 2, SARM_W / 2, 7)])
    g = M._scg; dR, sig, gg, cc = g["dR"], g["sig"], g["g"], g.get("c", 0.0); lim = float(g["dK_lim"])
    qa, qb = [x for x in lg["J2"][:2]]; s_th, q_on = G["s_th"], G["q_on"]; bw = math.radians(float(M.D.p["blend"])); hb = bw / abs(s_th) / 2.0
    azs = []
    for q in np.linspace(min(qa, qb) - math.radians(1), max(qa, qb) + math.radians(1), 240):
        x = (q - q_on) / s_th; K = 0.0 if x <= -hb else (x if x >= hb else (x + hb) ** 2 / (4 * hb)); K = min(K, lim)
        R = S.rotm(u2, -q)[0] @ S.rotm(dR, sig * float(RF.phi_of(np.array([K]), gg, cc)[0]))[0]
        Q = fp @ R.T; rr = np.linalg.norm(Q - np.outer(Q @ u2, u2), axis=1); Qn = Q[rr < S.HUB_R + 1.2]
        if len(Qn): azs.append(np.arctan2(Qn @ f2, Qn @ e2))
    # the sweep as one interval: the largest empty gap on the circle is its complement
    a_s = np.sort(np.mod(np.concatenate(azs), 2 * math.pi)); gaps = np.diff(np.r_[a_s, a_s[0] + 2 * math.pi]); k = int(np.argmax(gaps))
    r_lo, r_hi = a_s[(k + 1) % len(a_s)], a_s[k]
    if r_hi < r_lo: r_hi += 2 * math.pi
    marg = math.radians(2.0); ra0, ra1 = r_lo - marg, r_hi + marg
    while ra0 > a0: ra0 -= 2 * math.pi; ra1 -= 2 * math.pi
    while ra1 < a0: ra0 += 2 * math.pi; ra1 += 2 * math.pi
    relief = sector(pl(UP - 0.4), REL_RIN, S.HUB_R + 2.5, ra0, ra1, lay["h_rel"] - UP + 0.4 + 0.01)
    pocket = sector(pl(lay["h_rel"] - 0.01), INS_RIN, r_out + 0.3, a0, a1, GD + 0.01)
    if lay.get("mode") == "model": lip = sector(pl(lay["h_ins"]), INS_RIN, r_out, a0, a1, lay["roof_top"] - lay["h_ins"])   # the model's roof to F+3.65 (one with link 2's pad)
    else: lip = sector(pl(lay["h_ins"]), INS_RIN + 0.5, r_out, a0, a1, ROOF)              # the roof lip over the insert's 0.96 outside O20 (link 2)
    # short arm (crank frame = link 1b at phi 0): stadium from the root to 1.5 past the pin, 1.5 thick from h_ab, along u2
    org = A0 + SHORT_ROOT * al; org = org - (org @ u2) * u2 + (H2 + lay["h_ab"]) * u2
    arm = USP.stadium(org, al, ac, L - SHORT_ROOT, SARM_W / 2, S1_T)
    # the crowned pin: shank O1.5 from the arm underside to the gap, crown R4 over the groove band, tip chamfer 0.1
    pc = pin_c - (pin_c @ u2) * u2; r = PIN_D / 2; zg0, zt = lay["h_rel"], lay["h_tip"]; zc = 0.5 * (zg0 + zt)
    dr = lambda z_: (z_ - zc) ** 2 / (2 * CROWN_R); ch = 0.1
    prof = [(0.0, lay["h_ab"]), (r, lay["h_ab"]), (r, lay["h_at"]), (r - dr(zg0), zg0)]
    pts = [(0.0, lay["h_ab"]), (r, lay["h_ab"]), (r, lay["h_at"])]
    wp = (cq.Workplane("XZ").moveTo(0.0, lay["h_ab"]).lineTo(r, lay["h_ab"]).lineTo(r, lay["h_at"]).lineTo(r - dr(zg0), zg0)
          .threePointArc((r, zc), (r - dr(zt - ch), zt - ch)).lineTo(r - dr(zt - ch) - ch, zt).lineTo(0.0, zt).close())
    pin = xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), PB.axis_frame(u2), pc + H2 * u2)
    hole = disc(pc + H2 * u2, u2, r, lay["h_ab"] - 0.2, lay["h_at"] + 0.2)
    # J2 dowel / link-2 strap vs the relief: azimuths in link 2's frame (reported)
    info = dict(levels_over_hub2_face_mm=dict(link1b_top_under_arm=(round(lay["l1b_top_under_arm"], 3) if lay["l1b_top_under_arm"] is not None else None), short_arm=[round(lay["h_ab"], 3), round(lay["h_at"], 3)],
                                              relief=[UP, round(lay["h_rel"], 3)], insert=[round(lay["h_rel"], 3), round(lay["h_ins"], 3)],
                                              roof_lip=[round(lay["h_ins"], 3), round(lay.get("roof_top", lay["h_ins"] + ROOF), 3)], pin=[round(lay["h_ab"], 3), round(lay["h_tip"], 3)],
                                              groove_mid=round(lay["hmid_new"], 3), model_groove_mid=round(float(G["hmid"]) - H2, 3)),
                delta_mm=round(lay["delta"], 3), glev_equivalent=round(float(M.D.p["glev"]) + lay["delta"], 3), axial_drift_mm=round(lay["dz"], 3),
                pin_into_groove_mm=round(lay["h_tip"] - lay["h_rel"], 3), pin_into_groove_at_worst_drift_mm=round(lay["h_tip"] - lay["h_rel"] - lay["dz"], 3),
                a_s=round(L, 3), pitch_mm=[round(float(rho.min()), 3), round(float(rho.max()), 3)], groove_r_mm=[round(float(rho.min()) - hw, 3), round(float(rho.max()) + hw, 3)],
                insert_r_mm=[INS_RIN, round(r_out, 3)], past_O20_mm=round(r_out - S.HUB_R, 3), insert_deg=[round(math.degrees(a0), 2), round(math.degrees(a1), 2)],
                insert_sector_deg=round(math.degrees(a1 - a0), 2), relief_deg=[round(math.degrees(ra0), 2), round(math.degrees(ra1), 2)],
                relief_sector_deg=round(math.degrees(ra1 - ra0), 2), groove_q2_deg=gl["q2_deg"], slot=sl_rep, insert_valid=valid1(ins), insert_debug=dbg,
                groove_rc_min_mm=round(rc_min, 3), ridge_r_mm=round(rc_min - GW / 2, 3), pin_search=lay["pin_search"],
                crown=dict(R_mm=CROWN_R, band=[round(zg0, 3), round(zt, 3)], end_drop_mm=round(max(dr(zg0), dr(zt)), 4)))
    # what of link 2 sits in the relief's azimuths (reported): the J2 dowel home angle and link 2's bar root, frame_of(u2) of link 2
    info["relief_vs_link2"] = dict(note="relief (link 2 frame) must miss the J2 stop dowel and link 2's bar root")
    info["mode"] = lay.get("mode", "raised")
    return dict(insert=ins, relief=relief, pocket=pocket, lip=lip, arm=arm, pin=pin, hole=hole, frame=(e2, f2), a=(a0, a1), ra=(ra0, ra1), mode=lay.get("mode", "raised")), info


# ---------------------------------------------------------------------------------------------------- the crank
def tip_plate(G):
    """the crank's tip plate: the nose path Z (crank frame, radius R0) centrally projected onto the plane at the plate's mid radius
    (normal = the radial at the slot centre), the stadium annulus hw_in .. hw_out about it (lines + 3-point arcs), extruded
    +-PLATE_T / 2 along the normal (the drawing: exact ruled walls by 4-axis UV wire EDM)"""
    Z = np.asarray(G["Z"], float); jl = len(Z) - 1; zc = Z[jl // 2]; nrm = unit(zc); e = unit(Z[-1] - Z[0]); e = unit(e - (e @ nrm) * nrm); f = np.cross(nrm, e)
    rm = G["rPu"] + PLATE_T / 2; Pm = Z * (rm / (Z @ nrm))[:, None]; o = rm * nrm; P2 = np.c_[(Pm - o) @ e, (Pm - o) @ f]
    sel = np.r_[0, np.arange(1, len(P2) - 1)[np.linalg.norm(np.diff(P2, axis=0), axis=1)[:-1] > 1e-4], len(P2) - 1]; P2 = P2[np.unique(sel)]
    pl = plane(o - PLATE_T / 2 * nrm, e, f)
    # the plate's outline: a stadium on the slot's chord (lines + 2 arcs), half width hw_out + the path's sag off the chord (walls >= wall2 everywhere)
    ch = P2[-1] - P2[0]; Lc = float(np.linalg.norm(ch)); tc = ch / Lc; nc = np.array([-tc[1], tc[0]]); sag = float(np.abs((P2 - P2[0]) @ nc).max()); hwo = G["hw_out"] + sag
    ang = math.atan2(tc[1], tc[0]); cpl = plane(o - PLATE_T / 2 * nrm + P2[0][0] * e + P2[0][1] * f, math.cos(ang) * e + math.sin(ang) * f, -math.sin(ang) * e + math.cos(ang) * f)
    outer = USP.stadium(np.asarray(cpl.origin.toTuple()), np.asarray(cpl.xDir.toTuple()), np.asarray(cpl.yDir.toTuple()), Lc, hwo, PLATE_T)
    ro = dict(max_dev_from_exact_offset_mm=0.0, chord_mm=round(Lc, 3), sag_mm=round(sag, 4), half_width_mm=round(hwo, 3))
    wi, ri = slot_wire(cq.Workplane(plane(o - (PLATE_T / 2 + 0.2) * nrm, e, f)), P2, G["hw_in"]); inner = wi.extrude(PLATE_T + 0.4).val()
    plate = outer.cut(inner)
    return plate, inner, dict(slot_len_mm=ri["length_mm"], slot_w_mm=round(2 * G["hw_in"], 3), plate_w_mm=round(2 * hwo, 3), plate_len_mm=round(Lc + 2 * hwo, 3),
                              plate_valid=bool(plate.isValid()), plate_solids=len(plate.Solids()), radial_mid_mm=round(rm, 3), outline=ro,
                              arcs=ri["arcs_per_side"], arc_dev_mm=max(ri["max_dev_from_exact_offset_mm"], ro["max_dev_from_exact_offset_mm"]),
                              note="mid-thickness section extruded along the slot-centre radial; drawing: exact ruled walls (radial lines through GH), 4-axis UV wire EDM")


def crank_parts(M, dg, G, zb, s1, l1b_body):
    """the bell crank D9-01 (boss + short arm + straight run + trimmed arc + tip plate, one 5-axis part) + 2 x MR63ZZ, the stage-1 pin,
    the pivot pin (link 1b) and the D3 stack"""
    dR = unit(dg["dR"]); ztop = zb + BOSS_H
    boss = rev([(BORE_R, BRG_W), (BRG_R, BRG_W), (BRG_R, 0.0), (BOSS_R, 0.0), (BOSS_R, BOSS_H), (BRG_R, BOSS_H), (BRG_R, BOSS_H - BRG_W), (BORE_R, BOSS_H - BRG_W)], zb * dR, dR)
    lay_ = dict(dR=dR, zb=zb, l1b_top=None)
    straight, sinfo = USS.arm_profile(dg, lay_, l1b_body)
    _m, tinfo = DL1.trim_arm(dg, G, zb)                                                    # the L1's trim: the arc ends where its section clears the slot by 0.3
    beta_t = math.radians(tinfo["ends_at_beta_deg"]); dg2 = dict(dg, beta=beta_t)
    arc, ainfo = USS.arm_arc(dg2, lay_)
    plate, slot_cut, pinfo = tip_plate(G)
    crank = boss; fuse_rep = {}; sep_arm = s1.get("mode") == "model"
    for lab, part in ((() if sep_arm else (("short arm", s1["arm"]),)) + (("straight run", straight), ("arc", arc), ("tip plate", plate))):
        try: crank = US.glue(crank, part); fuse_rep[lab] = "glued"
        except RuntimeError: crank = crank.fuse(part); fuse_rep[lab] = f"fused ({len(crank.Solids())} solids)"
    print(f"  crank fuse: {fuse_rep}; plate valid {plate.isValid()} solids {len(plate.Solids())}, arc valid {arc.isValid()}, straight valid {straight.isValid()}, "
          f"short arm valid {s1['arm'].isValid()}; crank now valid {crank.isValid()} solids {len(crank.Solids())}", flush=True)
    crank = crank.cut(slot_cut)                                                                # the arc's end must not reach into the slot
    crank = crank.cut(disc(np.zeros(3), dR, BRG_R, zb - 1.0, zb + BRG_W))
    crank = crank.cut(disc(np.zeros(3), dR, BRG_R, ztop - BRG_W, ztop + 1.0))
    crank = crank.cut(disc(np.zeros(3), dR, BORE_R, zb - 1.0, ztop + 1.0))
    crank = crank.cut(s1["hole"])
    arm_sep = clean(s1["arm"].cut(s1["hole"])) if sep_arm else None
    brg = [rev([(PIN_R, 0.0), (BRG_R, 0.0), (BRG_R, BRG_W), (PIN_R, BRG_W)], (zb + z0) * dR, dR) for z0 in (0.0, BOSS_H - BRG_W)]
    top_sp = USS.l1b_top_under(l1b_body, dR, SPACER_RO + 0.05, zb - 6.0, zb + 1.0)
    z_land = zb - SPACER_T
    if top_sp is None: top_sp = z_land - 0.5
    if top_sp < z_land - 0.05:
        land = disc(np.zeros(3), dR, LAND_R, top_sp - 1.0, z_land)
        l1b_new = clean(l1b_body.fuse(land)); ok_land = valid1(l1b_new)
        if not ok_land: l1b_new = l1b_body
    else: l1b_new, ok_land = l1b_body, "not built: link 1b's strap rises through the boss level (the model's boss sits inside the strap)"
    lev = float(dg["lev"])
    ppin = rev([(0.0, lev), (PIN_R, lev), (PIN_R, ztop + 1.4), (0.0, ztop + 1.4)], np.zeros(3), dR)
    spacer = rev([(SPACER_RI, z_land), (SPACER_RO, z_land), (SPACER_RO, zb), (SPACER_RI, zb)], np.zeros(3), dR)
    shim = rev([(SPACER_RI, ztop), (SPACER_RO, ztop), (SPACER_RO, ztop + SHIM_T), (SPACER_RI, ztop + SHIM_T)], np.zeros(3), dR)
    wave = rev([(1.6, ztop + SHIM_T), (WAVE_RO, ztop + SHIM_T), (WAVE_RO, ztop + SHIM_T + WAVE_T), (1.6, ztop + SHIM_T + WAVE_T)], np.zeros(3), dR)
    z_c = ztop + CLIP_DZ
    clip = rev([(1.15, z_c), (3.0, z_c), (3.0, z_c + CLIP_T), (1.15, z_c + CLIP_T)], np.zeros(3), dR)
    info = dict(boss_mm=[round(zb, 3), round(ztop, 3)], boss_model_mm=round(float(dg["zboss"]), 3), raised_over_model_mm=round(zb - float(dg["zboss"]), 3),
                straight_run=sinfo, arc=ainfo, trim=tinfo, plate=pinfo, crank_valid=crank.isValid(), crank_solids=len(crank.Solids()), fuse=fuse_rep,
                land=dict(top_mm=round(z_land, 4), rise_over_l1b_mm=round(z_land - top_sp, 4), fused=ok_land), spacer_t_mm=SPACER_T,
                pivot_pin_mm=[round(lev, 3), round(ztop + 1.4, 3)], clip_mm=[round(z_c, 3), round(z_c + CLIP_T, 3)])
    parts = [("dk", f"D9-01 drive bell crank (Ti-6Al-4V, 5-axis machined from solid): boss O10 x {BOSS_H:g} (2 x MR63ZZ seats O6 x 2.5 at both ends, O3.2 web), "
                    f"short arm 3 x {S1_T:g} to the stage-1 pin at a_s {PFULL['a_s']:.3f} / psi {PFULL['psi']:.2f} (O1.5 H7 bore), bent arm 6 x 3 (straight run through the "
                    f"model's stations + the arc about hub K at r_c {dg['rc']:.2f}, trimmed {tinfo['ends_at_beta_deg']:.2f} deg) ending in the {pinfo['plate_w_mm']:.2f} x "
                    f"{PLATE_T:g} tip plate with the stage-2 slot {pinfo['slot_w_mm']:.2f} x {pinfo['slot_len_mm']:.2f} (closed end = stop A, far end = stop B at dK "
                    f"{math.degrees(G['lim']):.1f}; 4-axis UV wire EDM, a-C:H DLC); all bores one setup +-5 um", crank),
             ("dk", "drive crank bearing 1 MR63ZZ 3x6x2.5 (polished)", brg[0]), ("dk", "drive crank bearing 2 MR63ZZ 3x6x2.5, preloaded 5-10 N by the wave washer through the inner-ring shim (polished)", brg[1]),
             ("dk", f"drive stage-1 pin ISO 8734 1.5 m6 440C (58-60 HRC) ground +-0.002, CROWNED R{CROWN_R:g} over the groove band, pressed H7/m6 through the short arm "
                    f"along u2, {s1['info']['pin_into_groove_mm']:.2f} into the groove, tip {PIN_TIP_CLR:g} + the {s1['info']['axial_drift_mm']:.2f} axial drift under the roof, greased (polished)", s1["pin"]),
             ("l1b", f"drive crank pivot pin O3 h5 17-4PH H900, pressed in link 1b, clip groove at the boss top + {CLIP_DZ:.2f} (polished)", ppin),
             ("l1b", f"drive crank pivot pin clip DIN 6799 RS 2.3 at the boss top + {CLIP_DZ:.2f} (groove O2.3 x 0.6 H13, land {ztop + 1.4 - z_c - CLIP_T:.2f} to the pin end) over the preload stack (polished)", clip),
             ("l1b", f"drive crank inner-ring spacer O3.1 x O3.9 x {SPACER_T:.3f} ground stainless 1.4310 (select-fit 0.15-0.20): on link 1b's O5 spot-faced land under the lower MR63ZZ inner ring (D3) (polished)", spacer),
             ("l1b", f"drive crank preload inner-ring shim O3.1 x O3.9 x {SHIM_T:.2f} stainless (polished)", shim),
             ("l1b", f"drive crank preload wave washer O3.2 x O5.8 (stainless spring shim, drawn at its {WAVE_T:.2f} working height: 5-10 N) (polished)", wave)]
    if arm_sep is not None:
        lv = s1["info"]["levels_over_hub2_face_mm"]["short_arm"]
        parts.insert(1, ("dk", f"D9-03 drive stage-1 short arm 3 x {S1_T:g} Ti AS MODELLED (F2{lv[0]:+.2f}..F2{lv[1]:+.2f}: the verified model's level, UNDER link 1b's strap and J2 "
                               "lower plate; no attachment to the crank boss can pass link 1b's strap - the open stage-1 item, build.json stage1_level_scan), "
                               "O1.5 H7 pin bore", arm_sep))
        info["short_arm_separate"] = dict(valid=bool(arm_sep.isValid()), solids=len(arm_sep.Solids()), why="model level: under link 1b's strap (the L1's finding 5)")
    return parts, info, l1b_new


# ---------------------------------------------------------------------------------------------------- fits (the drawing)
def fits(s1i, ci):
    drop = ("stage-1 pin in", "stage-1 groove in", "stage-2 slot in", "K free play", "crank pivot bearings", "crank pivot axial stack", "crank-to-link 1a",
            "stop dowels (K pair, J2)", "desmo drive wear test", "J3 stop groove under link 2's ring")
    out = [dict(f) for f in DL1.FITS if not f["where"].startswith(drop)]
    lv = s1i["levels_over_hub2_face_mm"]
    out += [
        dict(where="stop dowels (K pair, J2) and their arc slots", fit=next(f["fit"] for f in UC.fits() if f["where"].startswith("stop dowels"))),
        dict(where="J3 stop groove under link 2's ring", fit=next(f["fit"] for f in UC.fits() if f["where"].startswith("J3 stop groove"))),
        dict(where="stage-1 groove insert (link 2, hub 2)", fit=(f"440C ring sector, through-hardened 58-60 HRC, {GD:g} thick, r {INS_RIN:g}..{s1i['insert_r_mm'][1]:.2f} over "
             f"{s1i['insert_sector_deg']:.1f} deg ({s1i['past_O20_mm']:.2f} past O20 under link 2's 0.8 roof lip); the groove = a 2-axis wire-EDM THROUGH slot 1.520 +-0.003 wide, "
             f"walls parallel to u2, centreline = the pin's locus at the built level F+{lv['groove_mid']:.2f} through the model's blended law (profile +-0.005 to the J2 bore; "
             f"{s1i['slot']['arcs_per_side']} arcs a side in the CAD, {s1i['slot']['max_dev_from_exact_offset_mm'] * 1000:.1f} um from the exact offset); pressed in link 2's pocket "
             "F+{:.2f}..F+{:.2f}, keyed by an ISO 8734 1 m6 x 4 dowel reamed at assembly; K LEAD +0.25 deg: phase the key +0.116 deg of q2 (red team)".format(lv["insert"][0], lv["insert"][1]))),
        dict(where="stage-1 relief in link 2's J2 pad", fit=(f"r >= {REL_RIN:g} over {s1i['relief_sector_deg']:.1f} deg, F+{UP:g}..F+{lv['relief'][1]:.2f} (the short arm's sweep "
             "in link 2's frame + 2 deg): 3+2-axis from below with an O3 end mill; leaves 0.55 mm of the MR117 seat wall over the sector (unpowered MVP1; check the bearing "
             "press with a plug gauge)")),
        dict(where="stage-1 pin in the crank's short arm", fit=(f"ISO 8734 1.5 m6 440C ground +-0.002, crowned R{CROWN_R:g} over the groove band (end drop {s1i['crown']['end_drop_mm']:.3f} "
             "vs the 4.76-deg tilt mismatch), pressed H7/m6 (reamed 1.500 -0.005/0) through the 1.5 mm short arm along u2, Ra <= 0.1, greased; true position to the crank bore "
             "0.01 (a_s 9.529 +-0.01: a hole error is a K-law error, +-0.095 deg)")),
        dict(where="stage-2 slot in the crank's tip plate", fit=("width 1.52 +0.01/0, 4-axis UV wire EDM (the walls are ruled by radial lines through GH, turning 0-2.24 deg; "
             "a straight 2-axis cut is 49 um off at the plate faces against a 10 um running clearance); the CAD shows the mid-thickness section extruded along the radial; "
             "cut to kslot 46.9 (red team: K lead) with J2's own stop B at K_law 46.30 (q2 -14.22); plate 17-4PH H900 or a-C:H DLC")),
        dict(where="crank pivot bearings + axial stack (2 x MR63ZZ in the O10 x 6 boss; D3)", fit=("pin O3 h5 17-4PH H900 (pressed H7/m6 in link 1b), housings O6 J6 at "
             f"both boss ends with a 1.0 mm web; ground inner-ring spacer O3.1 x O3.9 x {SPACER_T:.3f} (select 0.15-0.20) on link 1b's spot-faced O5 land, inner-ring shim "
             f"0.10 + wave washer (5-10 N) under the DIN 6799 RS 2.3 clip at the boss top + {CLIP_DZ:.2f}")),
        dict(where="crank running faces (D9-01 against links 1a / 1b / 2, the insert and the facing pads; D1)", fit=("profile +-0.02 mm on the crank's boss faces, short "
             "arm faces and plate sides and on the facing pads / relief / insert faces (worst two-face stack 0.04 < the smallest posed running gap, build.json drive_posed)")),
        dict(where="K free play (no spring preload; red team)", fit=("one-sided band 0.217 / 0.276 deg (wire-EDM fits nominal / worst); build a +0.25 deg K lead (insert key "
             "+0.116 deg of q2, slot to kslot 46.9, J2 stop B at K_law 46.30, K stop-A dowel at K -0.25): held-out th >= 5.004, 0 poses under 5 (red team re-solve); "
             "every stop load bypasses stage 1 (stops on their own joint angles)")),
        dict(where="desmo drive wear test (pass line)", fit=("stage-1 forward pressure-angle bind not before K 46.5 at the MEASURED mu after the wear run (claim mu 0.15; "
             "the family's 43-deg rule first fails at mu 0.17 at K 45.98; efficiency 0.84 at mu 0.15); 440C insert + crowned 440C pin + grease, DLC dowel in a 17-4PH / "
             "DLC slot (bare Ti on 440C galls: ~0.5 mm of groove per 1e6 strokes)")),
    ]
    return out


# ---------------------------------------------------------------------------------------------------- checks
def posed_pairs(dd, frames=None, n=60):
    """signed distance (mm, < 0 = metal in metal) between drive / stack parts on the clip frames (the L1's frames), worst + the dK there"""
    import igl
    src = trimesh.load(os.path.join(dd, "exo.glb")); C = json.load(open(os.path.join(dd, "clips.json"))) if frames is None else dict(clips=[dict(name="given", frames=frames)])
    by = {}
    for node in src.graph.nodes_geometry:
        T_, gn = src.graph[node]; g, nm = node.split("|")[:2]; m = src.geometry[gn].copy(); m.apply_transform(T_); by[nm] = (g, m)
    def get(sub): return next(v for k, v in by.items() if k.startswith(sub))
    pairs = [("drive stage-1 pin", "drive stage-1 groove insert"), ("drive stage-1 pin", "D8-03"), ("D9-01", "D8-03"), ("D9-01", "drive stage-1 groove insert"),
             ("D9-01", "D8-02b"), ("D9-01", "D8-02a"), ("D9-01", "J2 cap"), ("D9-01", "K cap"), ("drive nose dowel", "D9-01"), ("drive nose dowel", "D8-02b"),
             ("drive nose dowel", "K cap"), ("drive stage-1 groove insert", "D8-02b"), ("D8-03", "D8-02b"), ("drive stage-1 pin", "D8-02b"),
             ("drive crank pivot pin clip", "D9-01"), ("drive crank inner-ring spacer", "D9-01"), ("drive crank preload wave washer", "D9-01"),
             ("drive crank pivot pin clip", "D8-03"), ("drive crank pivot pin clip", "drive stage-1 groove insert"), ("drive crank pivot pin", "D8-03"),
             ("D8-02a", "D8-02b"), ("D8-02a", "K cap"), ("J2 stop dowel", "D9-01"), ("J3 stop dowel", "D8-03")]
    frs = [f for c in C["clips"] for f in c["frames"]]
    pick = (frs[::max(1, len(frs) // n)] + sorted(frs, key=lambda f: -abs(f.get("knuckle", {}).get("dK", 0.0)))[:12]) if frames is None else frs
    res = {}
    for a_, b_ in pairs:
        try: (ga, ma), (gb, mb) = get(a_), get(b_)
        except StopIteration: res[f"{a_} | {b_}"] = "missing"; continue
        if ga == gb: res[f"{a_} | {b_}"] = "same group"; continue
        XA = np.r_[np.asarray(ma.vertices), trimesh.sample.sample_surface_even(ma, 3000, seed=4)[0]]; worst = (1e9, None)
        for f in pick:
            G = lambda g: np.array(f["G"][g]).reshape(3, 3) if g in f["G"] else np.eye(3); T_ = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
            Xb = ((XA @ G(ga).T + T_(ga)) - T_(gb)) @ G(gb)
            d = float(igl.signed_distance(np.ascontiguousarray(Xb), np.ascontiguousarray(mb.vertices, float), np.ascontiguousarray(mb.faces, np.int64))[0].min())
            if d < worst[0]: worst = (round(d, 3), round(float(f.get("knuckle", {}).get("dK", 0.0)), 2))
        res[f"{a_} | {b_}"] = worst
    return res


def law_closure(dd, M, G, lay, gl):
    """on every clip frame: the pin's point at the built level (crank frame F0 + DELTA u2) read in link 2's posed frame vs the built
    groove centreline (2D, nearest), and the nose centre (link 1a, C0) read in the crank's posed frame vs the slot path at |dK| (mm)"""
    from scipy.spatial import cKDTree
    C = json.load(open(os.path.join(dd, "clips.json"))); frs = [f for c in C["clips"] for f in c["frames"]]
    u2 = lay["u2"]; e2, f2 = gl["e2"], gl["f2"]; Tg = cKDTree(gl["P2"]); F0n = lay["F0n"]; C0 = np.asarray(G["C0"], float)
    kdeg = np.degrees(G["kp"]); g1, g2, gz = [], [], []
    for f in frs:
        Gm = lambda g: np.array(f["G"][g]).reshape(3, 3); T_ = lambda g: np.array(f.get("T", {}).get(g, [0, 0, 0]), float)
        if "dk" not in f["G"]: continue
        pw = Gm("dk") @ F0n + T_("dk"); p2 = Gm("l2").T @ (pw - T_("l2"))
        g1.append(float(Tg.query(np.array([p2 @ e2, p2 @ f2]))[0])); gz.append(float(p2 @ u2 - (lay["H2"] + lay["hmid_new"])))
        nw = Gm("l1a") @ C0 + T_("l1a"); nz = Gm("dk").T @ (nw - T_("dk")); dK = abs(float(f.get("knuckle", {}).get("dK", 0.0)))
        ref = np.array([np.interp(dK, kdeg, G["Z"][:, k]) for k in range(3)]); g2.append(float(np.linalg.norm(nz - ref)))
    return dict(frames=len(g1), groove_closure_max_mm=round(max(g1), 4) if g1 else None, pin_axial_from_groove_mid_mm=[round(min(gz), 3), round(max(gz), 3)] if gz else None,
                slot_closure_max_mm=round(max(g2), 4) if g2 else None,
                rule="pin point (built level) in link 2's posed frame vs the built groove centreline; nose (C0) in the crank's posed frame vs the slot path at |dK|")


def check_frames(M, dd, stops, g3, s1i):
    """UC.check_frames (the model's member transforms vs the posed parts at the gen-8 check poses + the J3 dowel reading) with the
    desmo's drive keys; hub 2's samples inside the stage-1 relief band are read separately (the relief is a stated stack change)"""
    D = M.D; u2 = unit(D.u[1]); Uu, C, F4, hr = BM.joints4(M); H2 = float((np.asarray(C[2], float) + F4[2] * unit(Uu[2])) @ u2); e2, f2 = USM.frame2(u2)
    ra0, ra1 = [math.radians(x) for x in s1i["relief_deg"]]; h1 = s1i["levels_over_hub2_face_mm"]["relief"][1]
    mem, Xp = M.rigid["hub2"]; h = Xp @ u2 - H2; r = np.linalg.norm(Xp - np.outer(Xp @ u2, u2), axis=1)
    a = np.mod(np.arctan2(Xp @ f2, Xp @ e2) - ra0, 2 * math.pi)
    inrel = (a <= (ra1 - ra0)) & (h > UP - 0.3) & (h < h1 + 0.3) & (r > REL_RIN - 0.6)
    M.rigid["hub2"] = (mem, Xp[~inrel])
    try: out = UC.check_frames(M, dd, stops, g3)
    finally: M.rigid["hub2"] = (mem, Xp)
    for c in out: c["hub2_relief_samples_excluded"] = int(inrel.sum())
    print(f"  hub 2: {int(inrel.sum())} of {len(Xp)} model samples inside the stage-1 relief read separately (a stated stack change)", flush=True)
    return out


def run_checks(M, dd, stops, rep, t0, g3, G, lay, gl):
    W = lambda: json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    try: rep["j3_stop_built"] = UC.j3_sweep_built(dd, M, g3)
    except Exception as e_: rep["j3_stop_built"] = f"error {e_!r}"[:300]
    print(f"J3 stop (built): {rep['j3_stop_built']}", flush=True); W()
    try: rep["stop_engagement_built"] = UC.stop_engagement(dd, rep)
    except Exception as e_: rep["stop_engagement_built"] = f"error {e_!r}"[:300]
    print(f"stop engagement (built): {rep['stop_engagement_built']}", flush=True); W()
    rep["law_closure"] = law_closure(dd, M, G, lay, gl); print(f"law closure: {rep['law_closure']}", flush=True); W()
    rep["drive_posed"] = posed_pairs(dd); print(f"drive posed (mm, at dK): {rep['drive_posed']}", flush=True); W()
    try:
        rep["check"] = check_frames(M, dd, stops, g3, rep["stage1"])
        keys = sorted({k for r in rep["check"] for k in r["per_part"] if " " not in k})
        outside = {k: max(float(r["per_part"][k][2]) for r in rep["check"] if k in r["per_part"]) for k in keys}
        rep["kinematics_exact"] = dict(poses=len(rep["check"]), joint_features_and_frames_within_0p5=all(r["within_0p5"] for r in rep["check"]),
                                       joint_features_within_0p5_poses=sum(1 for r in rep["check"] if r["within_0p5"]),
                                       model_metal_outside_built_max_mm={k: round(v, 3) for k, v in outside.items()},
                                       max_frame_dev_mm=max(r["frame_dev_mm"] for r in rep["check"]), max_joint_feature_mm=max(r["joint_features_max_mm"] for r in rep["check"]),
                                       per_pose_joint_features_mm={r["label"]: r["joint_features_max_mm"] for r in rep["check"]},
                                       dowels_in_slots=all(r["stops"]["K"]["inside"] and r["stops"]["J2"]["inside"] and r["stops"]["J3"]["inside"] for r in rep["check"]),
                                       q3p_frames_vs_model_max_deg=max(r["stops"]["J3"]["frame_vs_model_deg"] for r in rep["check"]),
                                       note=("hub2 includes the model's O20 samples inside the stage-1 relief (r >= 6.05 over the relief sector, F+3.15..F+%.2f): a stated "
                                             "stack change (the stage 1 rides above link 1b); ring2 / crank / plate / horn are the drive's model samples (ring2 = the model's "
                                             "lip at the model's level, DELTA %.2f below the built one)" % (s1i["levels_over_hub2_face_mm"]["relief"][1], s1i["delta_mm"])))
    except Exception as e_:
        import traceback; traceback.print_exc(); rep["kinematics_exact"] = f"error {e_!r}"[:400]
    W(); print(f"kinematics: {rep.get('kinematics_exact')} ({time.time() - t0:.0f} s)", flush=True)
    if os.environ.get("DESMO_DRIVE_SKIN") == "1":
        try: rep["drive_skin"] = USS.drive_skin(dd); W(); print(f"drive skin: { {k: v for k, v in rep['drive_skin'].items() if k != 'per_clip'} }", flush=True)
        except Exception as e_: rep["drive_skin"] = f"error {e_!r}"[:300]; W()
    else: rep["drive_skin"] = "not run in this pass (2-process cap; R2 judges every part on every clip frame): DESMO_DRIVE_SKIN=1 --checks-only"; W()
    print(f"checks done in {time.time() - t0:.0f} s", flush=True)


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="user_desmo_conecut"); ap.add_argument("--l1", default="l1_desmo-conecut")
    ap.add_argument("--skip-base-search", action="store_true"); ap.add_argument("--checks-only", action="store_true"); ap.add_argument("--no-checks", action="store_true")
    ap.add_argument("--link-margin", type=float, default=0.0); ap.add_argument("--l1b-margin", type=float, default=0.1)
    ap.add_argument("--stop-after-drive", default=None, help="export hubs + links + drive to this glb and stop (a quick geometry look)")
    ap.add_argument("--level-scan", default=None, help="comma list of groove levels over hub 2's face: run level_scan, write <out>/stage1_level_scan.json, stop")
    ap.add_argument("--stage1", default="model", choices=("model", "raised"), help="model: stage 1 at the verified model's levels (the verified metal; "
                    "crosses link 1b, R6); raised: above link 1b in a relief of link 2 with the pin re-searched (no feasible pin found at F+6.03: errors)")
    a = ap.parse_args(MY_ARGV); t0 = time.time(); dd = os.path.join(FULL, "designs", a.out); os.makedirs(os.path.join(dd, "step"), exist_ok=True)
    import concept_kit as KIT
    M, rep0 = RL1.fit(); D = M.D; lg = RL1.law_geom(M); M._lg = lg; dg = RL1.drive_geom(M); G = dg["desmo"]
    Bf = M.B; M._bench_K = BM.chain(M, np.array([[Bf.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(Bf.idx))]))
    L1D = os.path.join(FULL, "designs", a.l1)
    l1d = json.load(open(os.path.join(L1D, "design.json"))); l1b = json.load(open(os.path.join(L1D, "build.json")))
    same = all(abs(float(l1d["params"][k]) - float(v)) < 1e-6 for k, v in PFULL.items() if isinstance(v, (int, float)) and k in l1d["params"])
    assert same, f"the L1 design {a.l1} was built from other params"
    assert abs(float(l1b["fit"]["tr"]) - float(M.tr)) < 1e-2 and np.allclose(l1b["fit"]["m"], D.m, atol=1e-2), "the fit differs from the L1's"
    assert np.allclose(l1b["stack"]["f"], M.f, atol=1e-2) and abs(l1b["stack"]["fK"] - M.fK) < 1e-2
    Uu, C, F4, hr = BM.joints4(M)
    if a.level_scan:
        r_ = level_scan(M, G, [float(x) for x in a.level_scan.split(",")]); json.dump(r_, open(os.path.join(dd, "stage1_level_scan.json"), "w"), indent=1, default=float); return
    print(f"fit (the verifier's DCModel --blend on BEST) on Bench(60,160) {M.B.mode} at fold margin {KIT.FOLD_MARGIN}: near-touch gap {rep0['gap']}; hub levels "
          f"{np.round(F4, 2).tolist()} (J1 K J2 J3) tr {M.tr:.2f}; dK_lim {math.degrees(G['lim']):.2f} ({time.time() - t0:.0f} s)", flush=True)
    l1_stops = l1d["stack_mm"]["stops"]; stops = {}
    for key in ("K", "J2"):
        q_lo, q_hi, meta = lg[key]; homes = [math.radians(x) for x in l1_stops[key]["dowel_home_angles_deg"]]
        stops[key] = dict(q=(q_lo, q_hi), meta=meta, homes=homes, pair_placed_in_l1=bool(l1_stops[key].get("pair")))
    l1_j3 = l1b["stack"]["stops"]["J3"]
    if a.checks_only:
        rep = json.load(open(os.path.join(dd, "build.json"))); g3 = UC.j3_geom(M, l1_j3)
        lay = rep["_lay"]; lay = dict(lay, u2=np.array(lay["u2"]), F0n=np.array(lay["F0n"]))
        gl = groove_line(M, G, lay, lg); run_checks(M, dd, stops, rep, t0, g3, G, lay, gl); return
    rep = dict(fit=dict(params=dict(PFULL), source=f"docs/concepts/rows/{ID}.json best_params on the verifier's DCModel (--blend; = {a.l1})",
                        gap_near_touch=rep0["gap"], hub_levels_J1_K_J2_J3=[float(x) for x in F4], tr=float(M.tr), m=[float(x) for x in D.m], hubs=[float(x) for x in hr],
                        fold_margin_deg=float(KIT.FOLD_MARGIN), l1_design=a.l1),
               style="user (line/arc sketches, extrudes, revolves, single-section sweeps on line/arc paths; no lofts, no splines)",
               stops={k: dict(q_deg=[round(math.degrees(x), 3) for x in v["q"]], homes_deg=[round(math.degrees(x) % 360, 2) for x in v["homes"]], **v["meta"]) for k, v in stops.items()},
               j2_push_limit=USM.j2_push_limit(), law=lg["law"])
    parts = []
    hw, rep["hubs"] = hubs(M); parts += hw
    USS.LINK_MARGIN.update(l1b=a.l1b_margin, l2=a.link_margin)
    bo, ro, hole_n, rep["nose_boss"] = nose_boss(M, G)
    lk, rep["links"] = USS.build_links(M, stops, [bo, ro])
    rep["links"]["link 2"]["climb_max_deg_allowed"] = UC.L2_CLIMB; rep["links"]["link 2"]["climb_used_deg"] = UC.CLIMB_USED
    i_1a = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-02a")); b1a = clean(lk[i_1a][2].cut(hole_n))
    lk[i_1a] = (lk[i_1a][0], lk[i_1a][1].replace("K pin continued as the O5 spring arbor (0.4 mm slit, no magnet: K is slaved)", "plain K pin (no clock spring: K is slaved)")
                .replace("the flank lug (the r 1.25 conjugate flank: 4 tangent arcs; 4-axis UV wire-EDM ruled surface, a-C:H DLC) + its web",
                         f"the O5 x 3 nose boss at the seat C0 (r_c {G['rK0']:.2f} from hub K's axis) on a 4 x 3 root from the K pad ({rep['nose_boss']['root']['ramp_deg']:.0f}-deg ramp), "
                         "the nose dowel's reamed O1.5 H7 hole"), b1a)
    print(f"  link 1a with the nose boss: valid {b1a.isValid()}, solids {len(b1a.Solids())}", flush=True)
    i_1b = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-02b")); l1b_body = lk[i_1b][2]
    top = USS.l1b_top_under(l1b_body, unit(dg["dR"]), BOSS_R + 0.6, dg["zboss"] - 6.0, dg["zboss"] + 12.0)
    if a.stage1 == "raised":
        zb = max(float(dg["zboss"]), (top if top is not None else -1e9) + RUNG); lay = stage1_layout(M, G, l1b_body, dg)
    else:                                                                                  # the L1's boss (on link 1b's strap + RUNG); the model's short arm
        zb = max(float(dg["zboss"]), (top if top is not None else -1e9) + RUNG); lay = stage1_layout_model(M, G)   # hangs under the strap: a separate part
    rep["stage1_mode"] = a.stage1
    gl = groove_line(M, G, lay, lg)
    s1, s1i = stage1_parts(M, G, lay, gl, lg, dg); s1["info"] = s1i; rep["stage1"] = s1i
    print(f"stage 1 (built level): {json.dumps(s1i, default=float)[:1500]}", flush=True)
    cp, rep["crank"], l1b_land = crank_parts(M, dg, G, zb, s1, l1b_body)
    print(f"crank: { {k: v for k, v in rep['crank'].items() if k not in ('straight_run',)} }", flush=True)
    lk[i_1b] = (lk[i_1b][0], lk[i_1b][1].replace("carries the crank pivot pin", f"carries the crank pivot pin on an O{2 * LAND_R:g} land spot-faced at the boss underside - {SPACER_T:g} (D3)"), l1b_land)
    z_pp = rep["crank"]["pivot_pin_mm"]
    try:
        b_ = lk[i_1b][2].cut(disc(np.zeros(3), unit(dg["dR"]), PIN_R, z_pp[0] - 1.0, z_pp[0] + T + 1.0))
        bad_, zero_, ns_ = USM.step_bad_faces(b_); ok_ = valid1(b_) and bad_ == 0 and ns_ == 1
    except Exception as e_: ok_, bad_, zero_ = False, str(e_), None
    if ok_:
        lk[i_1b] = (lk[i_1b][0], lk[i_1b][1].replace("carries the crank pivot pin", "carries the crank pivot pin in an O3 H7 bore"), b_)
        rep["crank"]["pivot_pin"] = f"O3 h6 pressed in an O3 H7 bore through link 1b (bore cut; STEP round trip 0 bad faces, {zero_} zero-area)"
    else: rep["crank"]["pivot_pin"] = f"O3 h6 pressed in link 1b: drawn as the press fit; the bore cut fails R7's STEP round trip ({bad_})"
    # link 2: the roof lip + its rim wall, then the relief (the short arm's sweep) and the insert pocket
    i_2 = next(i for i, (g, n, s) in enumerate(lk) if n.startswith("D8-03")); b2 = lk[i_2][2]; v0 = b2.Volume()
    try: b2 = US.glue(b2, s1["lip"])
    except RuntimeError: b2 = b2.fuse(s1["lip"])
    if a.stage1 == "raised": b2 = clean(b2.cut(s1["relief"]).cut(s1["pocket"]))
    else: b2 = clean(b2)
    b2, sl2 = USM.sliver_free(b2, "link 2 (stage-1 relief)")
    clu = [c_ for v in UC.CLIMB_USED.values() for c_ in v if c_ is not None]
    rep["link2_stage1"] = dict(valid=b2.isValid(), solids=len(b2.Solids()), slivers=sl2, volume_change_mm3=round(b2.Volume() - v0, 2))
    lk[i_2] = (lk[i_2][0], lk[i_2][1].replace("D8-03 link 2:", f"D8-03 link 2 (5-axis / 3+2 machined from solid Ti-6Al-4V, drop {max(clu) if clu else 0:.1f} deg at J2 (<= {UC.L2_CLIMB:g}: "
                                                           "CAD ruling 2, tighter transition on a part machined from solid)):")
               .replace("J2 dowel hole,", (f"J2 dowel hole, the stage-1 relief under the J2 pad (r >= {REL_RIN:g}, {s1i['relief_sector_deg']:.1f} deg, F+{UP:g}..F+"
                                          f"{s1i['levels_over_hub2_face_mm']['relief'][1]:.2f}) + the groove insert's pocket and 0.8 roof lip ({s1i['past_O20_mm']:.2f} past O20),")
                        if a.stage1 == "raised" else
                        (f"J2 dowel hole, the stage-1 cap-ring sector hanging under the J2 pad (Ti roof F+{s1i['levels_over_hub2_face_mm']['roof_lip'][0]:.2f}.."
                         f"F+{s1i['levels_over_hub2_face_mm']['roof_lip'][1]:.2f}, r {INS_RIN:g}..{s1i['insert_r_mm'][1]:.2f}, {s1i['insert_sector_deg']:.1f} deg: the verified "
                         "model's level, inside link 1b's J2 lower-plate layer - see build.json stage1_level_scan),")), b2)
    print(f"link 2 + stage-1 relief: {rep['link2_stage1']}", flush=True)
    if a.stop_after_drive:                                                                     # quick look: the drive + links + hubs to a scratch glb
        sc = trimesh.Scene(); dn = [(g, n, s) for g, n, s in hw + lk + cp] + [("l2", "drive stage-1 groove insert", s1["insert"])]
        for i, (g, n, s) in enumerate(dn): sc.add_geometry(USS.tess_safe(s, fine=False), node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        sc.export(a.stop_after_drive); json.dump(rep, open(a.stop_after_drive + ".json", "w"), indent=1, default=float)
        print(f"stop after drive: {a.stop_after_drive} ({time.time() - t0:.0f} s)", flush=True); return
    parts += lk
    parts.append(("l2", f"drive stage-1 groove insert: 440C, 58-60 HRC, {GD:g} thick, r {INS_RIN:g}..{s1i['insert_r_mm'][1]:.2f} over {s1i['insert_sector_deg']:.1f} deg, the groove = a "
                        f"2-axis wire-EDM through slot 1.520 +-0.003 on the pin's locus at F+{s1i['levels_over_hub2_face_mm']['groove_mid']:.2f} (the model's blended law), pressed "
                        "in link 2's pocket under the roof, keyed by an ISO 8734 1 m6 x 4 dowel (polished)", s1["insert"]))
    parts += cp
    dw_n, dzn = nose_dowel(G)
    parts.append(("l1a", f"drive nose dowel ISO 8734 1.5 m6 x 5, 440C, a-C:H DLC: pressed radially 2.5 mm in link 1a's O5 boss (reamed 1.500 -0.005/0), C0{dzn[0]:+.1f}..C0+{dzn[1]:.2f}, "
                         f"runs in the crank's slot {NOSE_TIP_CLR:g} under the plate top (polished)", dw_n))
    USP.pin_stack = USS.knee_pin_bb
    m3, rep["member 3"] = USP.member3(M); parts += [(g, n, s) for g, _, n, s in m3]
    g_, _, n_, s_ = USS.knee_link_bb(M)
    ks_deg = (l1d.get("build_fixes") or {}).get("knee_stop_deg")
    if ks_deg is not None:
        s_, rep["knee stop"] = USM.knee_stop_on(M, s_, ks_deg, M._bench_K)
        n_ = n_.replace(" (Ti-6Al-4V)", f" + knee stop tooth behind pin a (its face meets the E strap's side at knee angle {ks_deg:g} deg = 180 - ang_min {PFULL['ang_min']}; "
                                        "+-0.02 on the tooth and the E strap's side face) (Ti-6Al-4V)")
    parts.append((g_, n_, s_))
    parts, rep["j3_stop"], g3 = UC.j3_apply(M, parts, l1_j3)
    Cc = json.load(open(os.path.join(L1D, "clips.json")))
    cposes = [f["p"] for cl in Cc["clips"] for fi, f in enumerate(cl["frames"]) if fi % 3 == 0]
    arm, users, rep["arm side"] = USP.arm_side(M, l1b["mount"], cposes); parts += [(g, n, s) for g, _, n, s in arm]
    Wj = json.load(open(os.path.join(L1D, "workspace.json"))); frames = []; rel = []
    allf = [f for cl in Cc["clips"] for f in cl["frames"]] + [p for p in Wj["poses"] if p.get("eval_feasible")]
    for fi, f in enumerate(allf):
        gg = lambda k: np.array(f["G"][k]).reshape(3, 3); t_ = lambda k: np.array(f.get("T", {}).get(k, [0, 0, 0]), float)
        Gb, Tb, G1, T1 = gg("base"), t_("base"), gg("l1a"), t_("l1a"); rel.append((Gb.T @ G1, Gb.T @ (T1 - Tb)))
        if fi % 3 == 0: frames.append((Gb, Tb, G1, T1))
    E = PB.Envelope(os.path.join(FULL, "designs", PB.BAND))
    for p, G_ in E.frames: G_["S"] = E.RS[p]
    l1_body = next(s for g, n, s in parts if n.startswith("D8-02a"))
    if a.skip_base_search: USP.EAR_DZ = ()
    try: bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames)
    except (FileNotFoundError, OSError) as e_:
        print(f"base: ear search needs {e_} - built without ears", flush=True)
        USP.EAR_DZ = (); bp, rep["base"] = USP.base_part(M, E, l1_body, rel, frames); rep["base"]["ear_search"] = f"not run: {e_}"
    parts.append((bp[0], bp[2], bp[3]))
    print(f"parts built ({time.time() - t0:.0f} s)", flush=True)
    NAMEFIX = {"+ integral O4 pin a": "+ the O3 H7 seat of pin a (ISO 8734 m6 pressed; MR63ZZ-pair knee)",
               "+ integral O4 h9 pin, hard-anodised": "+ the O3 H7 seat of pin b (ISO 8734 m6 pressed; MR63ZZ-pair knee), clear anodised (never black)"}
    for i_, (g, n, s) in enumerate(parts):
        for o_, n2_ in NAMEFIX.items(): n = n.replace(o_, n2_)
        parts[i_] = (g, n, s)
    rep["step_clean"] = {}; USER0 = ("TOP", "MIDDLE", "FOREARM", "Hex", "M4 ULTRA", "IGUS", "5mm", "Revolve", "CirPattern")
    for i_, (g, n, s) in enumerate(parts):
        if n.startswith(USER0): continue
        s2, r_ = USS.step_clean(s, n[:40]); rep["step_clean"][n[:60]] = r_
        if s2 is not s: parts[i_] = (g, n, s2)
    nb_ = sum(1 for v in rep["step_clean"].values() if (v.get("after") or v).get("bad_faces_after_step", 0) or (v.get("after") or v).get("solids_after_step", 1) != 1)
    print(f"step round trip: {len(rep['step_clean'])} parts, {nb_} with bad faces / not one solid after STEP ({time.time() - t0:.0f} s)", flush=True)
    HR = BM.HR
    allp = [(g, n, xform(s, HR, np.zeros(3)) if g == "H" else s, GROUPS[g]) for g, n, s in parts] + [(g, n, s, None) for g, n, s in users]
    for f in os.listdir(os.path.join(dd, "step")):
        if os.path.isfile(os.path.join(dd, "step", f)): os.remove(os.path.join(dd, "step", f))
    sd_stock = os.path.join(dd, "step", "stock"); os.makedirs(sd_stock, exist_ok=True)
    for f in os.listdir(sd_stock): os.remove(os.path.join(sd_stock, f))
    USER = USER0; sc = trimesh.Scene(); pf = []
    for i, (g, n, s, mem) in enumerate(allp):
        user = n.startswith(USER); hwr = not n.startswith(("D8-", "D9-")) and any(k in n.lower() for k in ("screw", "m4x6", "clip"))
        if not user and not hwr:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(dd, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        elif hwr and not user:
            cq.exporters.export(cq.Workplane().add(s), os.path.join(sd_stock, f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_').replace('.', 'p')[:60]}.step"))
        trep = {}; m = USS.tess_safe(s, fine=not user, report=trep)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else s.Volume()
        mat, rho = USS.material(n, user)
        if n.startswith("drive stage-1 groove insert") or n.startswith("drive stage-1 pin") or n.startswith("drive nose dowel"): mat, rho = "440C (1.4125) hardened", 7.75
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material=mat, mass_g=None if rho is None else round(vol / 1000 * rho, 2),
                       valid=bool(s.isValid()), faces=len(s.Faces()), solids=len(s.Solids()), watertight_judge_units=trep.get("watertight_judge_units")))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L2 user-style", FACES={"1": round(float(F4[0]), 2), "K": round(float(F4[1]), 2), "2": round(float(F4[2]), 2),
                                                                 "3": round(float(F4[3]), 2)}, parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    for fn in ("clips.json", "workspace.json"):
        J = json.load(open(os.path.join(L1D, fn))); frs = [f for c in J["clips"] for f in c["frames"]] if fn == "clips.json" else J["poses"]
        assert all("dk" in f["G"] for f in frs if "G" in f and "l1b" in f["G"]), f"{fn}: the L1's frames lack group dk"
        shutil.copy(os.path.join(L1D, fn), os.path.join(dd, fn))
    d = dict(l1d); d.update(id=a.out, row_id=ID, l1_design=a.l1,
                            label=(f"desmo-conecut-knuckle-3r (verified config: conecut-knee + J3 stop [{J3MIN:.2f}, {J3MAX:.2f}] + the spring-free desmo K drive cell B; verified "
                                   "18.98 / held 23.19), full CAD in the user's style"),
                            level="L2 user-style (full CAD of the generation-9 winner)",
                            build_fixes_2026_10_18=dict(stage1_raised=dict(delta_mm=s1i["delta_mm"], glev_equivalent=s1i["glev_equivalent"],
                                                                           why="the model's stage 1 (groove F+0.11..1.61, short arm F-1.83..-0.33) sits inside link 1b's J2 lower "
                                                                               "plate and under its strap: built above link 1b in a relief of link 2's J2 pad, the groove "
                                                                               "re-cut on the pin's locus at the built level through the same blended law (K law unchanged)"),
                                                        k_cap="plain v5 cap, no clock spring", link_margin_mm=dict(l1b=USS.LINK_MARGIN["l1b"], l2=USS.LINK_MARGIN["l2"]),
                                                        link2_climb_max_deg=UC.L2_CLIMB),
                            built_with=("pipeline/conformal/param_cad/user_style_desmo.py (imports user_style_conecut (gen-8 full CAD: slot-end fix, link 2 70-deg drop, J3 "
                                        "stop, checks) then build_desmo_l1 (gen-9 L1: the verifier's DCModel --blend), user_style_slipper's parts unchanged: v5 O20 hubs (K plain, no "
                                        "spring), link 1a chain + nose boss, 4-strip machined bars 1b / 2, O3 dowel-in-arc-slot K / J2 stops, the J3 stop, member 3 + E strap, knee "
                                        f"link with MR63ZZ-pair bosses + knee stop, BOTTOM fused with the pad mount; the desmo drive) on the L1 design's frames ({a.l1})"))
    d["fits"] = fits(s1i, rep["crank"])
    d["drive_build"] = dict(kind=("desmo cell B (spring-free, roller-free, positive both ways): stage 1 = crowned O1.5 440C pin on the bell crank's short arm in a 1.52 "
                                  "wire-EDM through slot of a 440C insert in link 2's J2 ring (BUILT ABOVE link 1b: the stack fix); bell crank on link 1b (2 x MR63ZZ on an O3 "
                                  "pin, D3 stack); stage 2 = ISO 8734 O1.5 440C nose (link 1a's boss) in the 1.52 slot of the crank's tip plate (UV wire EDM)"),
                            mu=float(PFULL.get("mu", 0.15)), stage1=s1i, crank={k: v for k, v in rep["crank"].items() if k not in ("straight_run", "arc")},
                            nose_boss=rep["nose_boss"], verified=DL1.VERIFIED)
    d["j3_stop"] = dict(l1d.get("j3_stop") or {}, built=rep["j3_stop"])
    json.dump(d, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    ours = [p for p in pf if p["material"] != "user part"]
    rep["mass_g"] = dict(custom=round(sum(p["mass_g"] or 0 for p in ours if "7075" not in p["material"]), 1),
                         bottom_plus_mount=round(sum(p["mass_g"] or 0 for p in ours if "7075" in p["material"]), 1))
    bad = [p["name"] for p in ours if not p["valid"] or p["solids"] != 1]
    rep["parts"] = pf; rep["invalid_or_multi_solid"] = bad; rep["slaved"] = l1b["slaved"]
    rep["_lay"] = {k: (np.round(v, 6).tolist() if isinstance(v, np.ndarray) else v) for k, v in lay.items() if k != "arm_geo"}
    rep["ring_root_skipped"] = list(USP.RING_ROOT_SKIPPED)
    json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"exported {len(pf)} parts -> {dd}; mass {rep['mass_g']}; invalid or multi-solid: {bad or 'none'} ({time.time() - t0:.0f} s)", flush=True)
    if a.no_checks:
        rep["checks"] = "not run in this pass (--no-checks): run --checks-only"; json.dump(rep, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float); return
    run_checks(M, dd, stops, rep, t0, g3, G, lay, gl)


if __name__ == "__main__":
    main()
