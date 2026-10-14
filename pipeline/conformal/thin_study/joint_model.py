"""Joint interfaces, load cases and post-processing for one member (link or scapula base) of a band design.

Joint model per hub (as built, v3 stack): see fe_core docstring. Constants:
  iglidur G E = 7800 MPa (igus data sheet), nu 0.4; washers t_w (1.0 or 0.5 mm); sleeve wall 1.0 mm, length = hub - 0.05.
  Lower hub (pin integral): pin column nodes (bore ring r = 5) tied rigidly to pin master P; washer A = elastic layer
  between the hub's top face (5 < r < 9) and the joint master E (= the other member's hub); washer B + cap + sleeve =
  6x6 spring E <-> P with washer A's stiffness, so the tilt couple splits 50 / 50 as it does in a no-preload duplex.
  Upper hub: washer A (bottom face), washer B (top face), both 6 < r < 9, and the sleeve (bore r = 6, radial) are elastic
  layers between the hub and E (the pin assembly of the other member, rigid).
  Loaded end: washers normal-only (+1e-4 tangential to keep the free joint spin regular). Fixed end: washers bonded
  (tangential G/t too) so the support also takes the moment about its own axis (cantilever, as fea_link.py did).
Load cases at the loaded hub's joint master (reference point on the pin axis at the upper member's mid-plane):
  D1  25 N.m moment, worst direction perpendicular to the joint axis (a passive revolute cannot carry an axial moment)
  D2  200 N force through the shoulder centre O (all joint axes pass through O), worst direction = F at the pin plus
      r x F (11-18 N.m at the hubs)
  D3  200 N at the pin itself (cantilever), worst direction - reference only
  design = D1 + D2 acting together (von Mises is a norm, so vm(D1 + D2) <= vm(D1) + vm(D2): conservative bound)
"""
import math
import numpy as np
import fe_core as F

E_IG, NU_IG = 7800.0, 0.40
P_RAD, P_TAP_R, P_TAP_L = 5.0, 1.65, 7.0


def series(*k): return 1.0 / sum(1.0 / x for x in k)


def frame(n, d):
    n = F_unit(n); l = F_unit(d - (d @ n) * n); t = np.cross(n, l); return n, t, l


def F_unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)


def K6_in(n, t, l, k_ax, k_rad, k_tilt, k_spin):
    """6x6 (F, M) spring about a common reference point, diagonal in the joint frame (n axial, t / l transverse)"""
    R = np.c_[n, t, l]; Kt = R @ np.diag([k_ax, k_rad, k_rad]) @ R.T; Kr = R @ np.diag([k_spin, k_tilt, k_tilt]) @ R.T
    K = np.zeros((6, 6)); K[:3, :3] = Kt; K[3:, 3:] = Kr; return K


def hub_faces(msh, hi, n1=6):
    """quads (node index lists) of hub hi: washer-zone bottom / top faces and the bore face"""
    H, ht, nl = msh["H"], msh["htags"], msh["nl"]
    mine = ht[:, 0] == hi; inner = mine & (ht[:, 2] < n1)
    bot = H[inner & (ht[:, 1] == 0)][:, [0, 1, 2, 3]]; top = H[inner & (ht[:, 1] == nl - 1)][:, [4, 5, 6, 7]]
    bore = H[mine & (ht[:, 2] == 0)][:, [0, 1, 5, 4]]
    return bot, top, bore


def setup_hub(model, msh, hi, fixed, G, cap_k, tw=None, t_sleeve=1.0):
    """adds the joint interface of hub hi; returns dict(E=master index, P=pin master or None, cJ, frame, ...)"""
    hub = msh["hubs"][hi]; X = msh["X"]; n = hub.n; tw = G.T_W if tw is None else tw
    nn_, t_, l_ = frame(n, hub.d)
    if hub.low: z_ref = hub.z0 + hub.tp + tw + G.T_SEAT / 2
    else: z_ref = hub.z0 + hub.tp / 2
    cJ = n * z_ref
    E = model.add_master(cJ, f"E{hi}")
    kn = E_IG / tw; kt = (E_IG / (2 * (1 + NU_IG)) / tw) if fixed else 1e-4 * kn
    bot, top, bore = hub_faces(msh, hi)
    def layer(quads, k_n, k_t):
        w, _ = F.face_areas(X, quads); nodes = np.unique(quads); A = w[nodes]
        model.add_springs(nodes, np.repeat(n[None], len(nodes), 0), k_n * A, E)
        if k_t > 0:
            model.add_springs(nodes, np.repeat(t_[None], len(nodes), 0), k_t * A, E)
            model.add_springs(nodes, np.repeat(l_[None], len(nodes), 0), k_t * A, E)
        return nodes, A
    info = dict(E=E, P=None, cJ=cJ, n=nn_, t=t_, l=l_, low=hub.low, z_ref=z_ref)
    if hub.low:
        nodes, A = layer(top, kn, kt); info["washerA_area"] = float(A.sum())
        P = model.add_master(cJ, f"P{hi}")
        tied = np.unique(bore); model.tie(tied, P)
        A_w = math.pi * (9.0 ** 2 - 5.0 ** 2); I_w = math.pi / 4 * (9.0 ** 4 - 5.0 ** 4); L_s = G.T_SEAT - 0.05
        # equal split: with 0.02 mm float (no preload) washer A and washer B each take one compression half, so the
        # couple forces are equal (F_A = F_B) whatever the cap compliance -> the pin path is given washer A's stiffness.
        # (The joint hardware's own tilt stiffness, incl. the cap, is computed separately in joint_hw.py.)
        k_ax = E_IG * A_w / tw; k_tl = E_IG * I_w / tw + E_IG * 10.0 * L_s ** 3 / 12 / t_sleeve
        k_rad = E_IG * 10.0 * L_s / t_sleeve
        k_sp = (E_IG / (2 * (1 + NU_IG)) * math.pi / 2 * (9 ** 4 - 5 ** 4) / tw) if fixed else 1e-3 * k_tl
        model.add_mspring(E, P, K6_in(nn_, t_, l_, k_ax, k_rad, k_tl, k_sp))
        info.update(P=P, k_c=dict(ax=k_ax, tilt=k_tl, rad=k_rad))
    else:
        nb, Ab = layer(bot, kn, kt); ntp, At = layer(top, kn, kt)
        w, _ = F.face_areas(X, bore); bn = np.unique(bore); Ab_ = w[bn]
        rr = X[bn] - np.outer(X[bn] @ n, n); rr /= np.linalg.norm(rr, axis=1, keepdims=True)
        model.add_springs(bn, rr, E_IG / t_sleeve * Ab_, E)
        info["washer_area"] = float(Ab.sum())
    if fixed: model.fix_master(E)
    return info


def analyse(msh, G, cap_k, loaded=1, fixed=0, tw=None, base_bolts=None):
    """run the 5 unit load cases on member mesh msh. loaded / fixed: hub indices (fixed=None: base bolts)"""
    X, H = msh["X"], msh["H"]; m = F.Model(X, H)
    hubs = msh["hubs"]
    infoL = setup_hub(m, msh, loaded, False, G, cap_k, tw)
    infoF = None
    if fixed is not None: infoF = setup_hub(m, msh, fixed, True, G, cap_k, tw)
    if base_bolts is not None:
        hub = hubs[0]; bolt_nodes = []
        for xb in base_bolts:
            c = hub.n * hub.z0 + xb * hub.d
            # skin-side face nodes (layer 0) within 3.0 mm of the bolt axis (M3 head / washer contact on the pad)
            layer0 = msh["tags"][:, 2] == 0
            dd = X - c; dd = dd - np.outer(dd @ hub.n, hub.n); near = np.linalg.norm(dd, axis=1) < 3.0
            bolt_nodes.append(np.nonzero(layer0 & near)[0])
        m.fix_nodes(np.concatenate(bolt_nodes)); infoF = dict(bolts=[len(b) for b in bolt_nodes])
    n, t, l, cJ, E = infoL["n"], infoL["t"], infoL["l"], infoL["cJ"], infoL["E"]
    unit_loads = [np.r_[n, 0, 0, 0], np.r_[t, 0, 0, 0], np.r_[l, 0, 0, 0], np.r_[0, 0, 0, t], np.r_[0, 0, 0, l]]
    sols = m.solve([{"master": {E: v}} for v in unit_loads])
    S = [m.nodal_stress(U)[0] for U, _ in sols]
    SFn, SFt, SFl, SMt, SMl = S
    # D2: unit force e at O -> at cJ: F = e, M = (O - cJ) x e = -cJ x e
    D2f = []
    for e, SF in ((n, SFn), (t, SFt), (l, SFl)):
        Mv = -np.cross(cJ, e); D2f.append(SF + (Mv @ t) * SMt + (Mv @ l) * SMl)
    vm_D1 = F.worst_vm([SMt, SMl], 25e3); vm_D2 = F.worst_vm(D2f, 200.0); vm_D3 = F.worst_vm([SFn, SFt, SFl], 200.0)
    vm_des = vm_D1 + vm_D2
    # stiffness: master rotation (total, incl. washers) and link-only (hub rings 9..10.5 rigid fits)
    C_tot = np.zeros((2, 2)); C_link = np.zeros((2, 2))
    tg = msh["tags"]
    ringB = np.nonzero((tg[:, 0] == loaded) & (tg[:, 1] > 9.0 - 1e-6) & (tg[:, 1] < 10.6))[0]
    ringA = np.nonzero((tg[:, 0] == fixed) & (tg[:, 1] > 9.0 - 1e-6) & (tg[:, 1] < 10.6))[0] if fixed is not None else None
    for k, (U, Um) in enumerate(sols[3:]):
        C_tot[:, k] = [Um[E, 3:] @ t, Um[E, 3:] @ l]
        rb = F.rigid_fit(X, U, ringB, cJ)[3:]
        ra = F.rigid_fit(X, U, ringA, cJ)[3:] if ringA is not None else np.zeros(3)
        C_link[:, k] = [(rb - ra) @ t, (rb - ra) @ l]
    def kdeg(C):
        ev = np.linalg.eigvalsh(0.5 * (C + C.T)); return [float(1.0 / e / 1e3 * math.pi / 180) for e in ev[::-1]]   # soft, stiff
    # deflection of the loaded pin under 200 N (D3), worst direction (mm)
    dmax = 0.0
    Cf = np.array([[Um[E, :3] @ v for v in (n, t, l)] for U, Um in sols[:3]]).T
    dmax = float(np.sqrt(np.linalg.eigvalsh(Cf.T @ Cf)[-1]) * 200.0)
    # washer-B path share at a lower loaded hub (pin-root moment per 25 N.m, worst direction)
    pin = None
    if infoL["P"] is not None:
        P = infoL["P"]; Kc = m.mspr[0][2] if m.mspr else None
        Ms = []
        for U, Um in sols[3:]:
            dl = Um[E] - Um[P]; f = Kc @ dl; Ms.append(np.array([f[3:] @ t, f[3:] @ l]))
        Mm = np.array(Ms).T                                                       # pin-path moment per unit applied moment
        share = float(np.sqrt(np.linalg.eigvalsh(Mm.T @ Mm)[-1]))
        Fax = []
        for U, Um in sols[3:]:
            dl = Um[E] - Um[P]; f = Kc @ dl; Fax.append(f[:3] @ n)
        pin = dict(moment_share=share, pin_root_moment_Nm=share * 25.0, axial_per_Nm=float(np.max(np.abs(Fax)) * 1e3))
    return dict(vm_D1=vm_D1, vm_D2=vm_D2, vm_D3=vm_D3, vm_des=vm_des, k_tot=kdeg(C_tot), k_link=kdeg(C_link), defl_D3=dmax,
                pin=pin, ndof=m.ndof, secs=m.t_total, infoL=infoL, infoF=infoF)


def zones(msh, res, loaded, fixed):
    """peak stresses per zone (node sets), MPa"""
    tg = msh["tags"]; hubs = msh["hubs"]; out = {}
    hub_of = tg[:, 0].astype(int); rho = tg[:, 1]; ring = tg[:, 3].astype(int)
    body = (hub_of < 0) | (rho > 9.5)
    for name, key in (("D1", "vm_D1"), ("D2", "vm_D2"), ("D3", "vm_D3"), ("des", "vm_des")):
        v = res[key]; z = {}
        z["body"] = float(v[body].max()); z["body_p995"] = float(np.percentile(v[body], 99.5))
        for hi, h in enumerate(hubs):
            mine = hub_of == hi
            if h.low:
                z[f"hub{hi}_pinroot"] = float(v[mine & (rho <= 9.5) & (ring >= 1)].max())
                z[f"hub{hi}_pinroot_corner"] = float(v[mine & (ring == 0)].max())
            else:
                z[f"hub{hi}_seat"] = float(v[mine & (rho <= 9.5)].max())
            z[f"hub{hi}_body"] = float(v[mine & (rho > 9.5)].max())
        if (hub_of < 0).any(): z["ribbon"] = float(v[hub_of < 0].max())
        out[name] = z
    # where is the body peak (for the report): hub index / rho / ribbon
    v = res["vm_des"]; i = int(np.argmax(np.where(body, v, -1)))
    out["peak_at"] = dict(hub=int(hub_of[i]), rho=float(rho[i]), layer=int(tg[i, 2]), xyz=[float(c) for c in msh["X"][i]])
    return out
