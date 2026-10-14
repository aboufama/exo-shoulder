"""Joint hardware checks for the thin stack: retaining cap FE (dome profile as built), washer pressure, pin root, screw,
retaining-ring alternative, and the stack-height table.

    python3 -B joint_hw.py          # writes joint_hw.json
"""
import sys, os, math, json
sys.dont_write_bytecode = True
import numpy as np
import fe_core as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "shoulder-d4"))
E_IG, NU_IG = 7800.0, 0.40


def bez(cp, n=40):
    cp = np.asarray(cp, float); u = np.linspace(0, 1, n)[:, None]; m = len(cp) - 1
    return sum(math.comb(m, i) * (1 - u) ** (m - i) * u ** i * cp[i] for i in range(m + 1))


def dome_thickness(H=2.5, R=10.0, r_lip=5.2, r_cb=3.8, d_cb=2.05, skirt=0.35, r_hole=2.25):
    """cap height t(r) (flat underside) from the G2 dome profile used in the CAD (g2cad.dome_cap_profile)"""
    import g2cad as G
    k_lip = 1.0 / max(0.4, (r_lip - r_cb)); up, inn, down, out = (0, 1.0), (-1.0, 0), (0, -1.0), (1.0, 0)
    dome = bez([np.r_[p] for p in G.g2_blend((R, skirt), up, 0.0, inn, (r_lip, H), inn, k_lip, down, frac=0.42)], 200)
    lip = bez([np.r_[p] for p in G.g2_blend((r_lip, H), inn, k_lip, down, (r_cb, H - (r_lip - r_cb)), down, 0.0, out, frac=0.36)], 200)
    pts = np.r_[dome, lip]; o = np.argsort(pts[:, 0]); rr, zz = pts[o, 0], pts[o, 1]
    def t(r):
        r = np.asarray(r, float)
        return np.where(r < r_cb, H - d_cb, np.interp(r, rr, zz))
    return t


def cap_fe(H=2.5, d_cb=2.05, t_w=1.0, r_clamp=4.6, r_head=3.55, n_th=72, nr=40, nl=4):
    """cap on the pin: underside r <= r_clamp bonded to the pin top (screw preload), web top r <= r_head clamped by the
    screw head; washer B (5..9) as an elastic layer to a rigid master W (the upper hub's top face).
    Returns tilt / axial stiffness of washer B + cap together, and the cap von Mises per unit W moment / force."""
    tf = dome_thickness(H=H, d_cb=d_cb); r_hole, R = 2.25, 10.0
    rs = np.unique(np.r_[np.linspace(r_hole, r_head, 5), np.linspace(r_head, 3.8, 3), np.linspace(3.8, r_clamp, 4),
                         np.linspace(r_clamp, 5.0, 3), np.linspace(5.0, 9.0, 17), np.linspace(9.0, R - 0.05, 6)])
    th = np.linspace(0, 2 * np.pi, n_th + 1)[:-1]
    RR, TT = np.meshgrid(rs, th, indexing="ij"); tt = np.maximum(tf(RR), 0.3)
    X = np.zeros((len(rs), n_th, nl + 1, 3))
    for l in range(nl + 1):
        X[..., l, 0] = RR * np.cos(TT); X[..., l, 1] = RR * np.sin(TT); X[..., l, 2] = tt * l / nl
    nid = lambda i, j, k: (i * n_th + j % n_th) * (nl + 1) + k
    I, J, K = np.meshgrid(np.arange(len(rs) - 1), np.arange(n_th), np.arange(nl), indexing="ij"); I, J, K = I.ravel(), J.ravel(), K.ravel()
    Hh = np.stack([nid(I, J, K), nid(I + 1, J, K), nid(I + 1, J + 1, K), nid(I, J + 1, K), nid(I, J, K + 1), nid(I + 1, J, K + 1),
                   nid(I + 1, J + 1, K + 1), nid(I, J + 1, K + 1)], 1)
    Xf = X.reshape(-1, 3)
    if F.hex_volume(Xf, Hh[:1])[0] < 0: Hh = Hh[:, [1, 0, 3, 2, 5, 4, 7, 6]]
    m = F.Model(Xf, Hh); r_n = np.hypot(Xf[:, 0], Xf[:, 1]); z_n = Xf[:, 2]; lay = np.tile(np.arange(nl + 1), len(rs) * n_th)
    clamp = np.nonzero(((lay == 0) & (r_n <= r_clamp + 1e-6)) | ((lay == nl) & (r_n <= r_head + 1e-6)))[0]
    m.fix_nodes(clamp)
    W = m.add_master([0, 0, 0], "W")
    sel = (I >= 0) & (rs[I] >= 5.0 - 1e-6) & (rs[I + 1] <= 9.0 + 1e-6) & (K == 0)
    quads = Hh[sel][:, [0, 1, 2, 3]]; w, _ = F.face_areas(Xf, quads); nodes = np.unique(quads)
    m.add_springs(nodes, np.repeat([[0, 0, 1.0]], len(nodes), 0), E_IG / t_w * w[nodes], W)
    # small in-plane springs so W is not singular in-plane
    m.add_springs(nodes, np.repeat([[1.0, 0, 0]], len(nodes), 0), 1e-4 * E_IG / t_w * w[nodes], W)
    m.add_springs(nodes, np.repeat([[0, 1.0, 0]], len(nodes), 0), 1e-4 * E_IG / t_w * w[nodes], W)
    m.add_mspring(W, None, np.diag([0, 0, 0, 0, 0, 1.0]))                               # spin about the axis (free joint)
    # washer B pushes the cap OUTWARD (+z) on one side under a tilt: unit moment about x and unit outward force
    sols = m.solve([{"master": {W: np.r_[0, 0, 0, 1.0, 0, 0]}}, {"master": {W: np.r_[0, 0, 1.0, 0, 0, 0]}}])
    (U1, Um1), (U2, Um2) = sols
    k_tilt = 1.0 / Um1[W, 3]; k_ax = 1.0 / Um2[W, 2]
    S1, _ = m.nodal_stress(U1); S2, _ = m.nodal_stress(U2)
    ok = r_n > r_clamp + 0.25                                                             # off the clamp edge (contact corner)
    vm1 = F.vm(S1); vm2 = F.vm(S2)
    return dict(H=H, d_cb=d_cb, t_w=t_w, k_tilt_comb=float(k_tilt), k_ax_comb=float(k_ax),
                vm_per_Nmm=float(vm1[ok].max()), vm_per_Nmm_corner=float(vm1.max()), vm_per_N=float(vm2[ok].max()),
                vol=float(F.hex_volume(Xf, Hh).sum()))


def washer_stiffness(t_w, ri=5.0, ro=9.0):
    A = math.pi * (ro ** 2 - ri ** 2); I = math.pi / 4 * (ro ** 4 - ri ** 4)
    return E_IG * A / t_w, E_IG * I / t_w


def cap_k(H=2.5, d_cb=2.05, t_w=1.0):
    """cap-only stiffness (series inverse of the combined washer B + cap) for joint_model.setup_hub"""
    r = cap_fe(H=H, d_cb=d_cb, t_w=t_w); kax_w, ktl_w = washer_stiffness(t_w)
    return dict(ax=1.0 / max(1.0 / r["k_ax_comb"] - 1.0 / kax_w, 1e-12), tilt=1.0 / max(1.0 / r["k_tilt_comb"] - 1.0 / ktl_w, 1e-12), fe=r)


def duplex_force(M, ri, ro):
    """no-preload duplex sandwich: tilt M reacted by compression on opposite half-annuli of washers A and B,
    pressure linear in x. Returns (resultant per washer N, peak edge pressure MPa, centroid lever mm)"""
    xbar = (math.pi / 8) * (ro ** 4 - ri ** 4) / ((2.0 / 3.0) * (ro ** 3 - ri ** 3))
    Fw = M / (2 * xbar); p0 = Fw / ((2.0 / 3.0) * (ro ** 3 - ri ** 3) / ro)
    return Fw, p0, xbar


def pin_root(M_pin, F_ax, d=10.0, d_rel=9.2, d_tap=3.3, Kt=2.2):
    I = math.pi / 64 * (d_rel ** 4 - d_tap ** 4); A = math.pi / 4 * (d_rel ** 2 - d_tap ** 2)
    s_nom = M_pin * (d_rel / 2) / I + F_ax / A
    return dict(nominal=s_nom, peak=Kt * s_nom, Kt=Kt)


if __name__ == "__main__":
    out = {}
    # ---------------- cap FE (dome as built, and lower variants)
    caps = []
    for H, d_cb, tw, note in ((2.5, 2.05, 1.0, "as built: M4 ULP head 2.0"), (2.5, 2.05, 0.5, "as built, 0.5 washers"),
                              (2.0, 1.55, 0.5, "M4 ULP head 1.5 (Fastenright class)"), (1.8, 1.35, 0.5, "M4 ULP head 1.3 (NV)"),
                              (1.5, 1.05, 0.5, "head 1.0 - no catalogued M4 found")):
        r = cap_fe(H=H, d_cb=d_cb, t_w=tw); r["note"] = note; caps.append(r)
        print(f"cap H {H} cb {d_cb} tw {tw}: k_tilt(wB+cap) {r['k_tilt_comb'] / 1e3 * math.pi / 180:.1f} N.m/deg, k_ax {r['k_ax_comb'] / 1e3:.0f} kN/mm,"
              f" vm {r['vm_per_Nmm'] * 1e3:.1f} MPa per N.m ({r['vm_per_Nmm_corner'] * 1e3:.1f} at the clamp edge), {r['vol'] * F.RHO_TI:.2f} g", flush=True)
    out["caps"] = caps
    # ---------------- duplex washers at 25 N.m
    wash = {}
    for nm, ri, ro in (("GTM-1018 (10/18)", 5.0, 9.0), ("GTM-0815 (8/15)", 4.0, 7.5)):
        Fw, p0, xb = duplex_force(25e3, ri, ro); wash[nm] = dict(F_per_washer_N=Fw, p_edge_MPa=p0, xbar=xb)
        print(f"{nm}: washer resultant {Fw:.0f} N, edge pressure {p0:.0f} MPa (iglidur G 80 MPa static, X 150)")
    out["washers_25Nm"] = wash
    # ---------------- joint hardware tilt stiffness (no-preload duplex: equal couple forces F at +-xbar)
    hw_k = {}
    for tw in (1.0, 0.5):
        cap = [c for c in caps if c["t_w"] == tw][0]
        kax_w, ktl_w = washer_stiffness(tw); k_cap_tilt = 1 / (1 / cap["k_tilt_comb"] - 1 / ktl_w); k_cap_ax = 1 / (1 / cap["k_ax_comb"] - 1 / kax_w)
        Fw, p0, xb = duplex_force(1.0, 5.0, 9.0); A_h = math.pi * (81 - 25) / 2
        kh = E_IG * A_h / tw
        dA = Fw / kh; dB = Fw / kh + Fw * xb * xb / k_cap_tilt + Fw / k_cap_ax
        th = (dA + dB) / (2 * xb); hw_k[f"t_w {tw}"] = dict(k_Nm_deg=1.0 / th / 1e3 * math.pi / 180)
        print(f"joint hardware tilt stiffness (washers {tw} + cap 2.5): {hw_k[f't_w {tw}']['k_Nm_deg']:.0f} N.m/deg")
    out["hardware_tilt_stiffness"] = hw_k
    # ---------------- pin root, screw, ring at 25 N.m (half the couple through the pin: compression-only duplex)
    Fw, p0, xb = duplex_force(25e3, 5.0, 9.0)
    pr10 = pin_root(Fw * xb, Fw, d=10.0, d_rel=9.2, d_tap=3.3, Kt=2.2)
    Fw8, p08, xb8 = duplex_force(25e3, 4.0, 7.5)
    pr8 = pin_root(Fw8 * xb8, Fw8, d=8.0, d_rel=7.4, d_tap=2.5, Kt=2.2)
    out["pin_root_25Nm"] = {"d10 (M4 tap, DIN 509 F0.4x0.2)": pr10, "d8 (M3 tap)": pr8}
    print(f"pin root d10: M {Fw * xb / 1e3:.1f} N.m + {Fw:.0f} N -> nominal {pr10['nominal']:.0f} MPa, x Kt 2.2 = {pr10['peak']:.0f} MPa;"
          f" d8: nominal {pr8['nominal']:.0f}, peak {pr8['peak']:.0f}")
    screws = {"M4 A2-70": 3950.0, "M4 A2-50": 1840.0, "M4 10.9": 7300.0, "M4 12.9": 8500.0}
    out["screw_25Nm"] = dict(F_washerB_N=Fw, yield_load_N=screws,
                             note="cap is pulled off the pin top by the washer-B couple force; preload must exceed it (A2-70 ULP is marginal)")
    print("screw: washer-B force %.0f N vs yield load " % Fw + ", ".join(f"{k} {v / 1e3:.1f} kN" for k, v in screws.items()))
    out["din471_d10"] = dict(ring_thrust_kN=4.0, groove_thrust_kN_sharp=1.0, groove_thrust_kN_chamfered=2.4, groove_basis="200 MPa yield steel",
                             F_one_sided_25Nm_N=Fw, height_above_washerB_mm=1.1 + 0.6, axial_play_mm="0.10-0.16 (groove 1.1 vs ring 0.94-1.00)")
    # ---------------- stack height options (above the lower plate's skin face at the pin)
    def h(t_lo, tw, t_up, ret): return t_lo + tw + t_up + tw + 0.02 + ret
    stacks = [
        ("as built", 3.5, 1.0, 5.05, 2.5, "GTM-1018-010 x2, GSM-1012-05, dome cap 2.5 + M4 ULP (head 2.0)"),
        ("0.5 mm washers", 3.5, 0.5, 5.05, 2.5, "GTM-1018-005 x2 (igus, verified)"),
        ("+ 4 mm sleeve", 3.5, 0.5, 4.05, 2.5, "GSM-1012-04 (verified)"),
        ("+ 3 mm sleeve", 3.5, 0.5, 3.05, 2.5, "GSM-1012-03 (verified)"),
        ("+ cap 2.0", 3.5, 0.5, 3.05, 2.0, "M4 ULP with 1.5 mm head (head height not verified)"),
        ("+ lower plate 3.0", 3.0, 0.5, 3.05, 2.0, "seat zone 3.0 (FE)"),
        ("ring instead of cap", 3.0, 0.5, 3.05, 1.70, "DIN 471-10 ring in a pin groove (1.1 groove + 0.6 end margin); lash 0.1-0.16 mm"),
        ("lower plate 2.5", 2.5, 0.5, 3.05, 2.0, "seat zone 2.5 (FE)"),
    ]
    out["stacks"] = [dict(name=n, t_lo=a, t_w=b, t_up=c, retention=d, note=e, height=h(a, b, c, d)) for n, a, b, c, d, e in stacks]
    for st in out["stacks"]: print(f"  {st['name']:22s} {st['height']:.2f} mm  ({st['note']})")
    json.dump(out, open("joint_hw.json", "w"), indent=1)
