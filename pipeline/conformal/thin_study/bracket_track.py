"""Parametric FEA of the two arm-end parts whose CAD is still in progress:

  NECK  Ti-6Al-4V bracket from the bolted lap on the user's aluminium bar to the last joint hub: a straight bar,
        width w x thickness t, free span L (lap edge -> hub centre), root clamped over the lap edge, hub end loaded
        through a rigid washer-seat insert (r <= 9, the v3 joint's washer OD). Swept: t 3.5..6.5, L 50/70/90, w 30 / 20.
  TRACK sliding-cuff arc guide: ring segment about the humerus axis (radius 80.4 mm at the track top for 4c_best),
        section = 90 deg V-head 12 wide x 4 deep (V tips at mid-depth) on an 8 mm wide keel of total depth D, cantilevered
        from a 4 mm clamped lap at one end; the carriage (4 V-wheels at +-11 mm of arc, both flanks) at arc span S from the
        clamp. Swept: D 4..19, S 50/65/80 mm.
Loads (at the joint reference point, on the joint axis at the upper member's mid-plane, 6.8 mm above the hub plate's
mid-plane / 7.3 mm above the track top):
  D1 25 N.m worst direction perpendicular to the joint axis; D2 200 N through the shoulder centre O (O on the joint axis,
  ZJ4 = 82 mm below the joint for the neck; on the humerus axis for the track); D3 200 N at the joint (cantilever);
  design = D1 + D2 (von Mises bound).
Stress reported at nodes >= 1.5 mm from the clamp edge and outside the load inserts (both are singular in a linear model);
the clamp-edge value is listed separately (a real lap has a pressure edge, not a sharp clamp).

    python3 -B bracket_track.py           # writes bracket_track.json
"""
import sys, json, math, time
sys.dont_write_bytecode = True
import numpy as np
import fe_core as F

MATS = {"Ti-6Al-4V": (113.8e3, 0.342, 880.0, 4.43), "17-4PH H900": (197e3, 0.27, 1170.0, 7.8), "7075-T6": (71.7e3, 0.33, 503.0, 2.81)}


def grid_hex(P):
    """P (n0, n1, n2, 3) structured node block -> X, H"""
    n0, n1, n2, _ = P.shape; X = P.reshape(-1, 3)
    nid = lambda i, j, k: (i * n1 + j) * n2 + k
    I, J, K = np.meshgrid(np.arange(n0 - 1), np.arange(n1 - 1), np.arange(n2 - 1), indexing="ij"); I, J, K = I.ravel(), J.ravel(), K.ravel()
    H = np.stack([nid(I, J, K), nid(I + 1, J, K), nid(I + 1, J + 1, K), nid(I, J + 1, K), nid(I, J, K + 1), nid(I + 1, J, K + 1),
                  nid(I + 1, J + 1, K + 1), nid(I, J + 1, K + 1)], 1)
    if F.hex_volume(X, H[:1])[0] < 0: H = H[:, [1, 0, 3, 2, 5, 4, 7, 6]]
    return X, H


def post(m, sols, E, n, t, l, cJ, O, ok):
    S = [m.nodal_stress(U)[0] for U, _ in sols]
    SFn, SFt, SFl, SMt, SMl = S
    D2f = []
    for e, SF in ((n, SFn), (t, SFt), (l, SFl)):
        Mv = np.cross(O - cJ, e); D2f.append(SF + (Mv @ t) * SMt + (Mv @ l) * SMl + (Mv @ n) * 0.0)
    v1 = F.worst_vm([SMt, SMl], 25e3); v2 = F.worst_vm(D2f, 200.0); v3 = F.worst_vm([SFn, SFt, SFl], 200.0)
    C = np.array([[sols[3 + j][1][E, 3:] @ v for j in range(2)] for v in (t, l)])
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    Cf = np.array([[Um[E, :3] @ v for v in (n, t, l)] for U, Um in sols[:3]]).T
    defl = float(np.sqrt(np.linalg.eigvalsh(Cf.T @ Cf)[-1]) * 200.0)
    return dict(D1=float(v1[ok].max()), D2=float(v2[ok].max()), D3=float(v3[ok].max()), des=float((v1 + v2)[ok].max()),
                des_all=float((v1 + v2).max()), k_soft=float(1 / ev[-1] / 1e3 * math.pi / 180), k_stiff=float(1 / ev[0] / 1e3 * math.pi / 180),
                defl_200N=defl)


def neck(t, L, w=30.0, h=1.0, nl=4, ZJ=82.2):
    """straight bar along x: x = 0 clamp edge (lap edge), hub centre at x = L, bar ends at L + 13"""
    xs = np.r_[np.linspace(-6.0, 0.0, 5)[:-1], np.linspace(0, L + 13.0, int(math.ceil((L + 13) / h)) + 1)]
    ys = np.linspace(-w / 2, w / 2, int(math.ceil(w / h)) + 1); zs = np.linspace(-t / 2, t / 2, nl + 1)
    P = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1); X, H = grid_hex(P)
    m = F.Model(X, H, *MATS["Ti-6Al-4V"][:2])
    m.fix_nodes(np.nonzero(X[:, 0] <= 1e-9)[0])                                    # lap region x <= 0 clamped
    cJ = np.array([L, 0.0, t / 2 + 1.0 + 2.5]); E = m.add_master(cJ)
    r = np.hypot(X[:, 0] - L, X[:, 1]); m.tie(np.nonzero(r <= 9.0)[0], E)
    n, tt, l = np.array([0, 0, 1.0]), np.array([0, 1.0, 0]), np.array([1.0, 0, 0])
    loads = [np.r_[n, 0, 0, 0], np.r_[tt, 0, 0, 0], np.r_[l, 0, 0, 0], np.r_[0, 0, 0, tt], np.r_[0, 0, 0, l]]
    sols = m.solve([{"master": {E: v}} for v in loads])
    O = cJ - n * ZJ
    ok = (X[:, 0] >= 1.5) & (r > 10.5)
    res = post(m, sols, E, n, tt, l, cJ, O, ok)
    edge = (X[:, 0] >= 0) & (X[:, 0] < 1.5)
    S = [m.nodal_stress(U)[0] for U, _ in sols]
    res["des_clamp_edge"] = float((F.worst_vm([S[3], S[4]], 25e3) + F.worst_vm(S[:3], 200.0))[edge].max())
    res["mass_g_per_span"] = float(w * t * (L + 13) * F.RHO_TI)
    beam = dict(flat_D1=6 * 25e3 / (w * t * t), root_D3=6 * 200 * L / (w * t * t))
    res.update(t=t, L=L, w=w, ndof=m.ndof, beam=beam)
    return res


def track(D, S_arc, rho=80.4, z_off=-16.9, h=1.0, keel_hw=4.0, ZJ_above=7.3):
    """ring segment about the z axis (= humerus axis); track top at radius rho, axial position z_off; depth radial inward.
    phi = 0 at the clamp end; carriage centre at phi_c = S_arc / rho."""
    phic = S_arc / rho; phi_end = phic + (11.0 + 6.0 + 2.0) / rho                    # track continues past the far wheels
    phis = np.r_[np.linspace(-4.0 / rho, 0.0, 6)[:-1], np.linspace(0.0, phi_end, int(math.ceil(phi_end * rho / h)) + 1)]
    nd = max(4, int(math.ceil(D / 0.8))); ds = np.linspace(0.0, D, nd + 1)
    if D > 4.0:                                                                        # make d = 2 and d = 4 grid lines
        ds = np.unique(np.r_[np.linspace(0, 2, 3), np.linspace(2, 4, 3), np.linspace(4, D, max(2, int(math.ceil((D - 4) / 0.8))) + 1)])
    else:
        ds = np.unique(np.r_[np.linspace(0, 2, 3), np.linspace(2, D, 3)])
    def hw(d): return np.where(d <= 4.0, keel_hw + 2.0 * (1.0 - np.abs(d - 2.0) / 2.0), keel_hw)   # V tips at d = 2 (+-6)
    xi = np.linspace(-1, 1, 13)
    PH, DD, XI = np.meshgrid(phis, ds, xi, indexing="ij")
    rr = rho - DD; zz = z_off + XI * hw(DD)
    P = np.stack([rr * np.cos(PH), rr * np.sin(PH), zz], -1); X, H = grid_hex(P)
    m = F.Model(X, H, *MATS["Ti-6Al-4V"][:2])
    phin = np.arctan2(X[:, 1], X[:, 0]); rn = np.hypot(X[:, 0], X[:, 1]); dn = rho - rn
    m.fix_nodes(np.nonzero(phin <= 1e-9)[0])                                         # clamped lap (2x M3 into the track)
    # carriage: 4 wheels at phi_c +- 11/rho on the V flanks (d in 0.5..3.5, |m| > keel_hw + 0.3), contact +-2 mm of arc
    cJ = np.array([(rho + ZJ_above) * math.cos(phic), (rho + ZJ_above) * math.sin(phic), z_off]); E = m.add_master(cJ)
    flank = (dn > 0.3) & (dn < 3.7) & (np.abs(X[:, 2] - z_off) > keel_hw + 0.2)
    patch = np.zeros(len(X), bool)
    for s in (-1, 1):
        patch |= flank & (np.abs(phin - (phic + s * 11.0 / rho)) * rho < 2.0)
    m.tie(np.nonzero(patch)[0], E)
    n = np.array([math.cos(phic), math.sin(phic), 0.0]); l = np.array([-math.sin(phic), math.cos(phic), 0.0]); tt = np.array([0, 0, 1.0])
    loads = [np.r_[n, 0, 0, 0], np.r_[tt, 0, 0, 0], np.r_[l, 0, 0, 0], np.r_[0, 0, 0, tt], np.r_[0, 0, 0, l]]
    sols = m.solve([{"master": {E: v}} for v in loads])
    O = np.zeros(3)
    near_patch = np.zeros(len(X), bool)
    for s in (-1, 1): near_patch |= np.abs(phin - (phic + s * 11.0 / rho)) * rho < 3.5
    ok = (phin * rho >= 1.5) & ~(near_patch & (dn < 4.5))
    res = post(m, sols, E, n, tt, l, cJ, O, ok)
    area = float(np.trapz(2 * hw(np.linspace(0, D, 200)), np.linspace(0, D, 200)))
    res.update(D=D, S_arc=S_arc, area_mm2=area, ndof=m.ndof,
               mass_g={k: area * (phi_end + 4 / rho) * rho * v[3] / 1000 for k, v in MATS.items()})
    # wheel loads (rigid carriage, 4 wheels, two per flank pair, 22 mm apart along the arc, flanks 2 x 10.5 apart)
    res["wheel_N_D1"] = max(25e3 / 22.0 / 2, 25e3 / 21.0 / 2)
    return res


if __name__ == "__main__":
    out = dict(neck=[], track=[])
    for w in (30.0, 20.0):
        for L in (50.0, 70.0, 90.0):
            for t in (3.5, 4.5, 5.5, 6.5):
                if w == 20.0 and L != 70.0: continue
                t0 = time.time(); r = neck(t, L, w); out["neck"].append(r)
                print(f"neck w {w:.0f} L {L:.0f} t {t}: D1 {r['D1']:.0f} D2 {r['D2']:.0f} D3 {r['D3']:.0f} des {r['des']:.0f} (clamp edge {r['des_clamp_edge']:.0f})"
                      f" MPa | SF_y(des) {880 / r['des']:.2f} | k {r['k_soft']:.1f}/{r['k_stiff']:.1f} N.m/deg | 200N defl {r['defl_200N']:.2f} mm"
                      f" | beam D1 {r['beam']['flat_D1']:.0f} | {time.time() - t0:.0f}s", flush=True)
                json.dump(out, open("bracket_track.json", "w"), indent=1)
    for S in (50.0, 65.0, 80.0):
        for D in (4.0, 7.0, 10.0, 13.0, 16.0, 19.0):
            t0 = time.time(); r = track(D, S); out["track"].append(r)
            print(f"track S {S:.0f} D {D:.0f}: D1 {r['D1']:.0f} D2 {r['D2']:.0f} D3 {r['D3']:.0f} des {r['des']:.0f} MPa | SF Ti {880 / r['des']:.2f}"
                  f" 17-4 {1170 / r['des']:.2f} 7075 {503 / r['des']:.2f} | k(Ti) {r['k_soft']:.1f}/{r['k_stiff']:.1f} N.m/deg | 200N defl {r['defl_200N']:.2f} mm"
                  f" | {time.time() - t0:.0f}s", flush=True)
            json.dump(out, open("bracket_track.json", "w"), indent=1)
