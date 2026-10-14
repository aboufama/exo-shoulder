"""Whole right-arm exo, conformal shoulder, average body (1.75 m, 325 mm upper arm).

  shoulder: build_conformal.py links (skin-following ribbons between flat G2 hub plates) + joint hardware per stack:
            lower plate (integral Ø10 pin, DIN 509 relief, M4 tap) | GTM-1018-010 | upper plate (Ø12 bore, GSM-1012-05)
            | GTM-1018-010 | G2 dome cap + M4 ULP screw. Base: flat hub plate + mounting tab (2x M4).
  BOTTOM:   the user's channel bar up to s = S_CUT, then one machinable piece: a planar S-jog (Δ toward the arm, all faces
            extruded across the bar width: 3-axis, two setups) into a flat G2 hub plate = J4's lower member (axis = the
            bar normal = elbow axis direction, through the GH centre).
  user parts unchanged: TOP, MIDDLE, FOREARM CUFF, elbow hardware, screws. Upper-arm cuff: forearm cuff x1.24.
Frames: canonical pose-0 thorax (shoulder groups) and body rest (H / F groups), mm, origin = right GH.

    python3 build_full_conformal.py envelope.json OUTDIR
"""
import json, math, os, sys
import numpy as np
import cadquery as cq
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); FX = os.path.join(HERE, "..", "full-exo")
sys.path.insert(0, os.path.join(HERE, "..", "shoulder-d4")); sys.path.insert(0, FX)
env_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "envelope.json"))
OUTD = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "out")); os.makedirs(OUTD, exist_ok=True)
sys.argv = [sys.argv[0], env_path, OUTD]
exec(open(os.path.join(HERE, "build_conformal.py")).read().split('if __name__ == "__main__":')[0])   # links + helpers
import g2cad as G
_cwd = os.getcwd(); os.chdir(FX); import fit_arm as FA; os.chdir(_cwd)
from load_arm import load
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf

BJ = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); HR = np.array(BJ["landmarks"]["rest_humerus"])
FIT = json.load(open(os.path.join(FX, "arm_fit.json"))); R_UP, R_FO = np.array(FIT["R_up"]), np.array(FIT["R_fo"])
Fr = json.load(open(os.path.join(FX, "bottom_frame.json"))); u_c, v_c, ax_c = (np.array(Fr[k]) for k in ("u", "v", "ax"))
uB, vB, axB = R_UP @ u_c, R_UP @ v_c, R_UP @ ax_c; CB = np.array(FA.C_b)
def xform(shape, R, t):
    tr = gp_Trsf(); tr.SetValues(*R[0], t[0], *R[1], t[1], *R[2], t[2]); return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())
def cad_to_rest(shape, grp):
    R = R_UP if grp == "up" else R_FO; return xform(shape, R, CB - R @ np.array(FA.C_cad))
def cyl(axis, z0, z1, r, off=(0.0, 0.0)):
    n, x, y = frame_of(axis); return cq.Solid.makeCylinder(r, z1 - z0, V(n * z0 + x * off[0] + y * off[1]), V(n))
def cone(axis, z0, r0, z1, r1):
    n, _, _ = frame_of(axis); return cq.Solid.makeCone(r0, r1, z1 - z0, V(n * z0), V(n))
def torus(axis, z, R_, r_):
    n, _, _ = frame_of(axis); return cq.Solid.makeTorus(R_, r_, V(n * z), V(n))

# ---------------------------------------------------------------- joint stacks (shoulder frame = canonical pose 0)
CAP_R, CAP_H = 10.0, 2.5                    # v3 standard: Ø20 x 2.5 cap, 0.45 floor under the M4 ULP head
T_SEAT = SLV_L + 0.05                        # upper hub between its seats: sleeve flush (v3: 5.04); top seat spot-faced 0.45 into the 5.5 plate
R_SF = WASH_OD / 2 + 0.6                     # spot-face radius for washer B (v3 pocket radius)
def stack_heights(J):
    """lower face, lower plate thickness for joint J (1..4)"""
    if J == 4: return ZJ4, T_BOT
    return ZJ[J], T_LO
def pin_on(axis, z_seat, z_top):
    """integral pin Ø10 from below the seat to the cap face: DIN 509-style undercut (0.4 x 0.8) just above the seat,
    0.4 tip chamfer, M4 tap Ø3.3 x 7 with a 0.3 chamfer - all in one turned profile"""
    r = PIN_D / 2; z0 = z_seat - 1.2; hr, ch = 1.65, 0.3
    segs = [("line", (hr, z0), (r, z0)), ("line", (r, z0), (r, z_seat + 0.05)), ("line", (r, z_seat + 0.05), (r - 0.4, z_seat + 0.25)),
            ("line", (r - 0.4, z_seat + 0.25), (r - 0.4, z_seat + 0.65)), ("line", (r - 0.4, z_seat + 0.65), (r, z_seat + 0.85)),
            ("line", (r, z_seat + 0.85), (r, z_top - 0.4)), ("line", (r, z_top - 0.4), (r - 0.4, z_top)), ("line", (r - 0.4, z_top), (hr + ch, z_top)),
            ("line", (hr + ch, z_top), (hr, z_top - ch)), ("line", (hr, z_top - ch), (hr, z_top - 7.0)), ("line", (hr, z_top - 7.0), (0.0, z_top - 7.6)),
            ("line", (0.0, z_top - 7.6), (0.0, z0)), ("line", (0.0, z0), (hr, z0))]
    return G.revolve_profile(segs, axis)
def bore_tool(axis, z0, z1, r, ch=0.3, ext=3.0):
    """one revolved tool: through bore radius r between faces z0..z1 with 45 deg chamfers at both faces"""
    segs = [("line", (0, z0 - ext), (r + ch + ext, z0 - ext)), ("line", (r + ch + ext, z0 - ext), (r, z0 + ch)), ("line", (r, z0 + ch), (r, z1 - ch)),
            ("line", (r, z1 - ch), (r + ch + ext, z1 + ext)), ("line", (r + ch + ext, z1 + ext), (0, z1 + ext)), ("line", (0, z1 + ext), (0, z0 - ext))]
    return G.revolve_profile(segs, axis)
def joint_hw(J, axis):
    z0, tl = stack_heights(J); zA = z0 + tl; zU0 = zA + T_W; zU1 = zU0 + T_SEAT; zB1 = zU1 + T_W; zc0 = zB1 + 0.02
    out = {}
    out["washer A (igus GTM-1018-010)"] = G.revolve_profile([("line", (5, zA), (8.85, zA)), ("line", (8.85, zA), (9, zA + 0.15)), ("line", (9, zA + 0.15), (9, zA + 0.85)),
                                         ("line", (9, zA + 0.85), (8.85, zA + 1)), ("line", (8.85, zA + 1), (5, zA + 1)), ("line", (5, zA + 1), (5, zA))], axis)
    out["sleeve (igus GSM-1012-05)"] = G.revolve_profile([("line", (5, zU0), (5.7, zU0)), ("line", (5.7, zU0), (6, zU0 + 0.3)), ("line", (6, zU0 + 0.3), (6, zU0 + 4.7)),
                                         ("line", (6, zU0 + 4.7), (5.7, zU0 + 5)), ("line", (5.7, zU0 + 5), (5, zU0 + 5)), ("line", (5, zU0 + 5), (5, zU0))], axis)
    out["washer B (igus GTM-1018-010)"] = G.revolve_profile([("line", (5, zU1), (8.85, zU1)), ("line", (8.85, zU1), (9, zU1 + 0.15)), ("line", (9, zU1 + 0.15), (9, zU1 + 0.85)),
                                         ("line", (9, zU1 + 0.85), (8.85, zU1 + 1)), ("line", (8.85, zU1 + 1), (5, zU1 + 1)), ("line", (5, zU1 + 1), (5, zU1))], axis)
    segs = G.dome_cap_profile(R=CAP_R, H=CAP_H, r_lip=5.2, r_cb=3.8, d_cb=2.05, skirt=0.35)
    n_, _, _ = frame_of(axis)
    cap = G.revolve_profile([(s[0],) + tuple((q[0], q[1] + zc0) for q in s[1:]) if s[0] != "bez" else ("bez", [(q[0], q[1] + zc0) for q in s[1]]) for s in segs], axis)
    out["retaining cap (G2 dome)"] = cap
    zs = zc0 + CAP_H - 2.05; zt = zs + 2.0
    scr = G.revolve_profile([("line", (0, zs - 6), (1.85, zs - 6)), ("line", (1.85, zs - 6), (2.0, zs - 5.7)), ("line", (2.0, zs - 5.7), (2.0, zs)),
                             ("line", (2.0, zs), (3.55, zs)), ("line", (3.55, zs), (3.55, zt - 0.35)), ("line", (3.55, zt - 0.35), (3.2, zt)),
                             ("line", (3.2, zt), (0, zt)), ("line", (0, zt), (0, zs - 6))], axis)
    n_, x_, y_ = frame_of(axis)
    hexw = cq.Workplane(cq.Plane(origin=V(n_ * (zt - 1.3)), xDir=V(x_), normal=V(n_))).polygon(6, 2.5 / math.cos(math.pi / 6)).extrude(1.4).val()
    out["M4x6 ultra-low-profile screw (stainless)"] = scr.cut(hexw)
    return out, dict(z0=z0, zA=zA, zU0=zU0, zU1=zU1, zc0=zc0)

def upper_features(body, axis, zU0, zU1):
    """upper member, one revolved tool: Ø12 H7 sleeve bore (0.3 chamfer at the underside) up to the washer-B seat at zU1
    (sleeve flush, 0.3 chamfer), seat spot-faced Ø19.2 from zU1 through the plate top (0.3 chamfer at the mouth)"""
    r, ch, ext = SLV_OD / 2, 0.3, 3.0; zt = zU0 + T_UP
    segs = [("line", (0, zU0 - ext), (r + ch + ext, zU0 - ext)), ("line", (r + ch + ext, zU0 - ext), (r, zU0 + ch)),
            ("line", (r, zU0 + ch), (r, zU1 - ch)), ("line", (r, zU1 - ch), (r + ch, zU1)), ("line", (r + ch, zU1), (R_SF, zU1)),
            ("line", (R_SF, zU1), (R_SF, zt - ch)), ("line", (R_SF, zt - ch), (R_SF + ch + ext, zt + ext)),
            ("line", (R_SF + ch + ext, zt + ext), (0, zt + ext)), ("line", (0, zt + ext), (0, zU0 - ext))]
    return body.cut(G.revolve_profile(segs, axis))
def lower_features(body, axis, zA, zc0):
    return fuzzy_fuse(body, pin_on(axis, zA, zc0))

parts = []                                                                   # (group, name, shape)
HWJ = {}
for J in (1, 2, 3, 4): HWJ[J] = joint_hw(J, AX[J])
L = {}
for k in range(3):
    body, info = build_link(k)
    for end in (0, 1):
        J = k + 1 + end; ax_ = AX[J]; hz = HWJ[J][1]
        if J == 4 or not lower[(k, end)]: body = upper_features(body, ax_, hz["zU0"], hz["zU1"])
        else: body = lower_features(body, ax_, hz["zA"], hz["zc0"])
    if not body.isValid():
        from OCP.ShapeFix import ShapeFix_Shape
        sf = ShapeFix_Shape(body.wrapped); sf.Perform(); body = cq.Shape.cast(sf.Shape())
    L[k] = body
    print(f"link {k + 1}: valid {body.isValid()}", flush=True)
parts += [("l1", "D4-02 link 1 (Ti-6Al-4V)", L[0]), ("l2", "D4-03 link 2 (Ti-6Al-4V)", L[1]), ("l3", "D4-04 link 3 (Ti-6Al-4V)", L[2])]

# base: flat hub plate at J1 with a mounting tab toward the back / medial (2x M4), lower or upper member per order
nb = unit(P["b"]); base_low = order[0] == 1
sys.path.insert(0, os.path.join(HERE, "..", "avg")); _c = os.getcwd(); os.chdir(os.path.join(HERE, "..", "avg")); import conformal as CFm; os.chdir(_c)
def tab_clearance(d, L=40.0):
    """min radial room (r - clearance radius) along a base tab in direction d (all elevation bins, scapula frame)"""
    worst = 1e9
    for x in np.linspace(HUB_R, L, 12):
        for yy_ in (-11.0, 0.0, 11.0):
            e2_ = np.cross(nb, d); p = nb * zb0 + x * d + yy_ * e2_; r = np.linalg.norm(p); w = p / r
            for eb_ in range(CFm.T_R1C.shape[0]):
                Rs_ = __import__("design_search").scapula(float(CFm.ELEVS[eb_]))
                lo_ = CFm.T_R1C[eb_].ravel()[CFm.pix((Rs_ @ w)[None])][0]; worst = min(worst, r - lo_)
    return worst
t0_ = unit(np.cross(nb, [0, 1.0, 0])); t1_ = np.cross(nb, t0_); best_ = None
zb0 = ZJ[1] if order[0] == 1 else ZJ[1] + T_LO + T_W
for ang in range(0, 360, 15):
    d = math.cos(math.radians(ang)) * t0_ + math.sin(math.radians(ang)) * t1_; c_ = tab_clearance(d)
    if best_ is None or c_ > best_[0]: best_ = (c_, d)
tab_dir = best_[1]; print(f"base tab: best direction clearance {best_[0]:.1f} mm", flush=True)
def tab_sdf(x, y): return np.maximum(np.abs(y) - 11.0, np.maximum(x - TAB_L, -x))
zb0 = ZJ[1] if base_low else ZJ[1] + T_LO + T_W; tb = T_LO if base_low else T_UP
TAB_L = 40.0 if best_[0] >= 2.0 else 26.0
def base_plate():
    """base = the J1 hub plate alone (no tab: anything fixed to the scapula meets the moving deltoid / trapezius); 3x M3
    counterbored holes on a Ø26 circle, between the washer seat and the rim, bolt it to the scapular pad / harness"""
    d = t0_; e2 = np.cross(nb, d)
    def sdf2(x, y): return np.hypot(x, y) - HUB_R
    pl = G.flat_plate(sdf2, [0, 0, 0], d, e2, zb0, zb0 + tb, E_LO, (-HUB_R - 4, HUB_R + 4, -HUB_R - 4, HUB_R + 4))
    for k_ in range(3):
        ang = 2 * math.pi * k_ / 3 + math.pi / 6; off = 13.0 * (math.cos(ang) * d + math.sin(ang) * e2)
        tool = G.revolve_profile([("line", (0, zb0 - 2), (1.25, zb0 - 2)), ("line", (1.25, zb0 - 2), (1.25, zb0 + 1.6)), ("line", (1.25, zb0 + 1.6), (1.6, zb0 + 1.6)),
                                  ("line", (1.6, zb0 + 1.6), (2.0, zb0 + 2.0)), ("line", (2.0, zb0 + 2.0), (0, zb0 + 2.0)), ("line", (0, zb0 + 2.0), (0, zb0 - 2))], -nb * 0 + nb)
        pl = pl.cut(tool.moved(cq.Location(V(off))))
    hz = HWJ[1][1]
    pl = lower_features(pl, nb, hz["zA"], hz["zc0"]) if base_low else upper_features(pl, nb, hz["zU0"], hz["zU1"])
    return pl
parts.append(("base", "D4-01 scapula base plate (Ti-6Al-4V)", base_plate()))
for J in (1, 2, 3, 4):
    grp = {1: "l1", 2: "l2", 3: "l2", 4: "H"}[J]
    for nm, s in HWJ[J][0].items():
        if grp == "H": s = xform(s, HR, np.zeros(3))                          # canonical -> rest frame (rides on the arm)
        parts.append((grp, f"J{J} {nm}", s))

# ---------------------------------------------------------------- BOTTOM (machinable): bar + planar S-jog + hub plate
user = load(); B_cad = [p[2] for p in user if p[0] == "BOTTOM"][0]; B = cad_to_rest(B_cad, "up")
W_rest = unit(HR @ P["u4"]); assert abs(abs(W_rest @ axB) - 1) < 1e-3, "J4 axis must be the bar normal"
sgn = 1.0 if W_rest @ axB > 0 else -1.0                                       # +W points away from GH; ax_B points ...
gh_ax = (0 - CB) @ axB                                                        # GH's coordinate along the bar normal (negative: arm side)
s_post, y_post = (0 - CB) @ uB, (0 - CB) @ vB
face_hub = gh_ax + sgn * ZJ4                                                   # hub skin-side face along ax_B (rel. to CB)
DELTA = -2.8 - face_hub                                                        # jog toward the arm (mm)
S_CUT, S_J0, S_J1 = 265.0, 268.0, 290.0
print(f"BOTTOM: post at s {s_post:.1f} y {y_post:.1f}; jog {DELTA:.1f} mm toward the arm between s {S_J0}-{S_J1}", flush=True)
big = cq.Workplane(cq.Plane(origin=tuple(CB + S_CUT * uB), xDir=tuple(vB), normal=tuple(-uB))).rect(800, 800).extrude(800).val()
bar = B.intersect(big)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section as _Sec
sec = cq.Shape.cast(_Sec(bar.wrapped, cq.Face.makePlane(400, 400, basePnt=V(CB + S_CUT * uB), dir=V(uB)).wrapped).Shape())
bar_loop = chain_loop(sec.Edges(), 160, vB, -axB)                             # CCW in (v, away-from-arm)
# outer outline of the user's section in (y, z) about the bar mid-plane: use its convex outer boundary (channel closed)
q = bar_loop - (CB + S_CUT * uB); yy, zz = q @ vB, q @ axB
# the jog piece: sections along a planar path in (u, ax); section = solid version of the user's outline morphing into the
# hub plate's G2 section; hub plate = flat_plate (disc 17 + strip 15, smooth-min) in the jogged plane
def zoff(s):                                                                  # bar normal offset (toward the arm is negative)
    if s <= S_J0: return 0.0
    if s >= S_J1: return -DELTA
    t_ = (s - S_J0) / (S_J1 - S_J0); return -DELTA * (10 * t_ ** 3 - 15 * t_ ** 4 + 6 * t_ ** 5)
zt_bar = zz.max(); zb_bar = zz.min()                                          # 3.7 / -2.8 (channel side)
def user_outline(n=160):
    """the user's outer section with the channel closed: top corners rounded (as theirs), skin-side corners sharp"""
    pts = np.c_[yy, zz]; top = pts[pts[:, 1] > 0.5]
    hw_ = np.abs(yy).max(); rc = 2.4
    out = []
    for t_ in np.linspace(0, 1, 30, endpoint=False): out.append((hw_, zb_bar + t_ * (zt_bar - rc - zb_bar)))
    for a_ in np.linspace(0, math.pi / 2, 12, endpoint=False): out.append((hw_ - rc + rc * math.cos(a_), zt_bar - rc + rc * math.sin(a_)))
    for t_ in np.linspace(0, 1, 40, endpoint=False): out.append((hw_ - rc - t_ * 2 * (hw_ - rc), zt_bar))
    for a_ in np.linspace(math.pi / 2, math.pi, 12, endpoint=False): out.append((-hw_ + rc + rc * math.cos(a_), zt_bar - rc + rc * math.sin(a_)))
    for t_ in np.linspace(0, 1, 30, endpoint=False): out.append((-hw_, zt_bar - rc - t_ * (zt_bar - rc - zb_bar)))
    for t_ in np.linspace(0, 1, 36, endpoint=False): out.append((-hw_ + t_ * 2 * hw_, zb_bar))
    o = np.array(out); seg = np.linalg.norm(np.diff(np.r_[o, o[:1]], axis=0), axis=1); sl = np.r_[0, np.cumsum(seg)]
    tt = np.linspace(0, sl[-1], n, endpoint=False); return np.array([np.interp(tt, sl, np.r_[o[:, k], o[0, k]]) for k in range(2)]).T
UO = user_outline(); hw_bar = np.abs(yy).max(); T_BAR = zt_bar - zb_bar
ths = BRepOffsetAPI_ThruSections(True, False, 1e-6); ths.CheckCompatibility(False)
def add_sec(c, y_dir, z_dir, prof):
    pts = c + np.outer(prof[:, 0], y_dir) + np.outer(prof[:, 1], z_dir)
    q_ = pts - c; i0 = int(np.argmax(q_ @ y_dir + 0.3 * (q_ @ z_dir))); pts = np.roll(pts, -i0, 0)
    ths.AddWire(G.wire([BRepBuilderAPI_MakeEdge(G._periodic_curve(pts, G._shift())).Edge()]))
ss_bar = np.r_[np.linspace(S_CUT, S_J0, 2), np.linspace(S_J0, S_J1, 10)[1:], np.linspace(S_J1, s_post - HUB_R - 6, 4)[1:]]
for s in ss_bar:
    c = CB + s * uB + y_post * vB * 0 + zoff(s) * axB
    d0 = zoff(s + 0.01) - zoff(s - 0.01); T = unit(uB * 0.02 + d0 * axB); zdir = unit(axB - (axB @ T) * T)
    add_sec(c, vB, zdir, UO)
# into the hub: across the hub disc in the jogged plane (planform half-width: disc 17 + bar strip, smooth-min)
def hub_hw(x, k=8.0):
    def sdf2(xx, yy_):
        d1 = np.hypot(xx, yy_) - HUB_R; d2 = np.maximum(np.abs(yy_) - hw_bar, np.maximum(xx - 60, -xx - 200))
        h = np.maximum(k - np.abs(d1 - d2), 0) / k; return np.minimum(d1, d2) - h ** 3 * k / 6
    lo_, hi_ = 0.0, 40.0
    if sdf2(x, 0.0) >= 0: return 0.0
    for _ in range(40):
        m = 0.5 * (lo_ + hi_); lo_, hi_ = (m, hi_) if sdf2(x, m) < 0 else (lo_, m)
    return lo_
hub_c = CB + s_post * uB + y_post * vB - DELTA * axB                       # hub centre (in-plane) on the jogged mid-plane
for xh in np.r_[np.linspace(-HUB_R - 6 + 1e-3, HUB_R - 0.04, 16)]:
    hw_ = max(0.6, hub_hw(xh)); scale = hw_ / hw_bar
    prof = UO.copy(); prof[:, 0] *= scale
    if hw_ < hw_bar - 0.5: prof = section_outline(2 * hw_, T_BAR, max(0.2, min(1.3, hw_ - 0.1)), n=160) + np.array([0, (zt_bar + zb_bar) / 2])
    add_sec(hub_c + xh * uB, vB, axB, prof)
ths.Build(); jog = cq.Shape.cast(ths.Shape()); jog = jog.Solids()[0] if jog.Solids() else jog
bottom = fuzzy_fuse(bar, jog)
# J4 features on BOTTOM: pin (lower member), relief
hz4 = HWJ[4][1]; Wr = W_rest
bottom = fuzzy_fuse(bottom, xform(pin_on(P["u4"], hz4["zA"], hz4["zc0"]), HR, np.zeros(3)))
print("BOTTOM valid", bottom.isValid(), "solids", len(bottom.Solids()), flush=True)
parts.append(("H", "BOTTOM (user's bar, shortened + machinable jog + J4 hub)", bottom))

# ---------------------------------------------------------------- user parts + upper cuff (as build_full_exo)
for name, inst, s in user:
    if s.Volume() < 1 or name.startswith(("SHOULDER LINK", '0.245" ID')) or name in ("RETAINING CLAMP", "BOTTOM") \
       or name.startswith("DRY RUNNING") or name.startswith("M4 ULTRA LOW PROFILE SOCKET HEAD SCREW, 8mm"): continue
    grp = "F" if name in ("MIDDLE", "FOREARM CUFF") or name.startswith("Hex socket head countersunk") else "H"
    parts.append((grp, name, cad_to_rest(s, "up" if grp == "H" else "fore")))
cuff = cq.importers.importStep(os.path.join(FX, "upper_cuff_cad.step")).val()
parts.append(("H", "UPPER ARM CUFF (forearm cuff design x1.24)", cad_to_rest(cuff, "up")))
scr = [p for p in user if p[0].startswith("Hex socket head countersunk")][0][2]; sc_c = np.array(scr.Center().toTuple())
MID_c = [p[2] for p in user if p[0] == "MIDDLE"][0]; vm, _ = MID_c.tessellate(0.2); Pm = np.array([[q.x, q.y, q.z] for q in vm]); zface = (Pm @ ax_c).min()
off_axis = sc_c @ ax_c - zface
for s_ in (94.25, 124.25, 154.25):
    for y_ in (-8.75, 8.75):
        hole = CB + s_ * uB + y_ * vB - 2.8 * axB
        parts.append(("H", "Hex socket head countersunk screw M4x0.7x8 (upper cuff)", xform(scr, R_UP, hole + off_axis * axB - R_UP @ sc_c)))

# ---------------------------------------------------------------- export
assy = cq.Assembly(name="EXO right arm (conformal shoulder), average adult")
for k_, (g, nm, s) in enumerate(parts):
    assy.add(s, name=(f"{k_:02d}_{g}|{nm}".replace(" ", "_").replace("(", "").replace(")", "").replace(",", ""))[:120])
assy.save(os.path.join(OUTD, "full_exo.step"))
cq.exporters.export(cq.Workplane().add(bottom), os.path.join(OUTD, "bottom_mod.step"))
sc = trimesh.Scene()
for k_, (g, nm, s) in enumerate(parts):
    fine = g in ("base", "l1", "l2", "l3") or "BOTTOM" in nm or "CUFF" in nm or "cap" in nm
    vs, tr = s.tessellate(0.05 if fine else 0.12, 0.12)
    if not len(tr): print("no mesh", nm); continue
    m = trimesh.Trimesh(np.array([[q.x, q.y, q.z] for q in vs]), tr, process=False); _ = m.vertex_normals
    sc.add_geometry(m, node_name=f"{g}|{nm}|{k_}", geom_name=f"{g}|{nm}|{k_}")
sc.export(os.path.join(OUTD, "exo.glb"))
os.makedirs(os.path.join(OUTD, "shoulder"), exist_ok=True)
json.dump(dict(Q0=ENV["q_rest"], pins={k: P[k].tolist() for k in P}, DES=dict(ENV["design"], delta=ENV["design"]["delta"], waz=ENV["design"]["waz"]),
               stack=dict(R_I0=min(ZJ.values()), HUB_R=HUB_R, ZJ=ZJ)), open(os.path.join(OUTD, "shoulder", "display_pose.json"), "w"))
print("exported", len(parts), "parts to", OUTD)
