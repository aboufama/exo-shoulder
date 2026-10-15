"""Parametric B-rep CAD of a searched spherical 3R (CadQuery / OCC), built from scratch - no fitted sheets, no meshes.

Every joint part is a solid of revolution about its joint's exact axis (all three axes meet at the GH centre), so the
hubs, bearings, spacers, nut and cap are coaxial by construction. Links are constant 8 x 3 mm sections (the evaluated
design's hw 4, t_link 3) lofted through stations on the great circle between their two joint axes; each station's
underside sits at the skin envelope (fair_cad/envelope.py: the dense skin maps, 2 mm clearance, every followed frame of
the fit clips) with a 60 deg climb limit, and meets its hub at the hub's own level. Joint faces are the evaluator's
fitted faces (input json "faces"), raised only if the envelope needs it. v5 joint stack (docs/HARDWARE.md): O20 hub,
lower member 0..3.00 with an integral O7 pin (O8.2 collar), upper boss 3.15..8.75 + M18 spigot, 2x MR117-2RS
(7 x 11 x 3) with 0.6 spacers, M7 ring nut, threaded O20 G2-dome cap to 12.25.

Members (design order [0, 1, 1], evaluator lower map {J1: link 1, J2: link 1}; J3: the arm end under link 2):
  J1: lower = link 1, upper = scapula base       J2: lower = link 1, upper = link 2       J3: lower = arm end, upper = link 2
Every part is designed in WORLD coordinates at the reference frame f0 and moved into its group's local frame
(frames.py), so scene_export.py and the judges pose it exactly like the old pipeline's parts.

    python3 param_build.py [key=r20_n3_s1414_4]  -> pipeline/full-exo/designs/param_<key>/ (exo.glb, step/, clips.json,
                                                     design.json, parts_full.json, build.json)
"""
import json, math, os, shutil, sys, time
import numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import frames as FR                                                                       # noqa: E402
CONF = os.path.join(FR.REPO, "pipeline", "conformal")
sys.path.insert(0, os.path.join(CONF, "fair_cad")); sys.path.insert(0, os.path.join(CONF, "band_cad")); sys.path.insert(0, os.path.join(FR.REPO, "pipeline", "shoulder-d4"))
from envelope import Envelope                                                             # noqa: E402
_c = os.getcwd(); os.chdir(os.path.join(CONF, "band_cad")); import arm_end as AE; os.chdir(_c)   # noqa: E402

KEY = sys.argv[1] if len(sys.argv) > 1 else "r20_n3_s1414_4"
BAND = f"band_{KEY}"; OUT = os.path.join(FR.FULL, "designs", f"param_{KEY}")
INP = json.load(open(os.path.join(CONF, "band_cad", "inputs", f"{KEY}.json")))["results"][0]
HUB_R, W, T = 10.0, 2 * float(INP.get("hw", 4.0)), float(INP.get("t_link", 3.0))
CLEAR, CLIMB = 2.0, math.radians(float(INP.get("ramp_deg", 60.0)))
LV = dict(F=0.0, S=3.00, U0=3.15, L1=3.65, B1=6.65, B2=7.25, H1=8.75, U1=10.25, N1=11.15, top=12.25, SPIG=10.22)


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)
def V(p): return cq.Vector(*map(float, p))


def xform(shape, R, t=np.zeros(3)):
    from OCP.gp import gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    tr = gp_Trsf(); tr.SetValues(*R[0], float(t[0]), *R[1], float(t[1]), *R[2], float(t[2]))
    return cq.Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())


def axis_frame(k):
    """rotation whose third column is the joint axis k (world)"""
    k = unit(k); a = np.array([0.0, 0.0, 1.0]) if abs(k[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = unit(np.cross(a, k)); e2 = np.cross(k, e1); return np.stack([e1, e2, k], 1)


def revolved(profile, k, F):
    """solid of revolution about the world axis k through GH; profile = [(r, z)] closed polygon in the joint frame,
    z measured from the joint face F (so the part sits at F + z along k)"""
    pts = [(r, z + F) for r, z in profile]
    s = cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()
    return xform(s, axis_frame(k))


def cap_shape(k, F):
    """threaded O20 cap: skirt over the boss from H1+0.05, flange face at U1, G2-like dome to the crown at `top`"""
    z0, z1, zt = LV["H1"] + 0.05 + F, LV["U1"] + F, LV["top"] + F
    wp = (cq.Workplane("XZ").moveTo(9.0, z0).lineTo(HUB_R, z0).lineTo(HUB_R, z1 + 0.35)
          .spline([(7.0, zt - 0.55), (0.0, zt)], tangents=[(0, 1), (-1, 0)], includeCurrent=True)
          .lineTo(0.0, zt - 0.5).lineTo(4.5, zt - 0.5).lineTo(4.5, z1).lineTo(9.0, z1).close())
    return xform(wp.revolve(360, (0, 0, 0), (0, 1, 0)).val(), axis_frame(k))


def joint_parts(J, k, F, lower, upper):
    """the v5 stack of joint J about world axis k at face F: [(group, name, shape)]"""
    P = []
    lo_pad = revolved([(0, 0), (HUB_R, 0), (HUB_R, LV["S"]), (4.1, LV["S"]), (4.1, LV["L1"]), (3.5, LV["L1"]), (3.5, LV["N1"]), (0, LV["N1"])], k, F)
    P.append((lower, f"{J} pad + integral O7 pin (lower member)", lo_pad))
    boss = revolved([(4.9, LV["U0"]), (HUB_R, LV["U0"]), (HUB_R, LV["H1"]), (9.0, LV["H1"]), (9.0, LV["SPIG"]), (5.5, LV["SPIG"]),
                     (5.5, LV["L1"]), (4.9, LV["L1"])], k, F)
    P.append((upper, f"{J} boss O20 + M18x0.5 spigot (upper member)", boss))
    for b, (z0, z1) in enumerate(((LV["L1"], LV["B1"]), (LV["B2"], LV["U1"]))):
        P.append((upper, f"{J} bearing {b + 1} MR117-2RS 7x11x3", revolved([(3.5, z0), (5.5, z0), (5.5, z1), (3.5, z1)], k, F)))
    P.append((upper, f"{J} outer spacer 17-4PH", revolved([(4.9, LV["B1"]), (5.5, LV["B1"]), (5.5, LV["B2"]), (4.9, LV["B2"])], k, F)))
    P.append((lower, f"{J} inner spacer (ground, preload)", revolved([(3.5, LV["B1"]), (4.1, LV["B1"]), (4.1, LV["B2"]), (3.5, LV["B2"])], k, F)))
    P.append((lower, f"{J} ring nut M7x0.5 (Ti-6Al-4V)", revolved([(3.5, LV["U1"]), (4.3, LV["U1"]), (4.3, LV["N1"]), (3.5, LV["N1"])], k, F)))
    P.append((upper, f"{J} cap O20 G2 dome, threaded (Ti-6Al-4V)", cap_shape(k, F)))
    return P


def disc_face(E, group, k_loc, F0, it=4):
    """lowest face distance F at which a O20 disc about local axis k_loc clears the skin envelope (2 mm) in every followed frame"""
    R = axis_frame(k_loc); g = np.arange(-HUB_R, HUB_R + 1e-6, 1.5); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= HUB_R ** 2
    off = (R[:, :2] @ np.stack([X[m], Y[m]])).T; F = F0
    for _ in range(it):
        P = F * k_loc + off; d = unit(P); need = E.min_radius(group, d, clear=CLEAR)
        F = float(max(F0, (need * (d @ k_loc)).max()))
    return F


def strap_stations(E, group, a_loc, b_loc, la, lb, n=36):
    """underside radius per station of a strap on the great circle a -> b (member-local unit axes), ending at hub levels
    la (face at a), lb (face at b): skin envelope over the strap's width + clearance, climb-limited, flush with each
    hub's plane inside the hub radius. Returns (theta (n,), dirs (n,3), normal (3,), under (n,))"""
    ang = math.acos(np.clip(a_loc @ b_loc, -1, 1)); nrm = unit(np.cross(a_loc, b_loc)); e2 = unit(np.cross(nrm, a_loc))
    th = np.linspace(0, ang, n); D = np.cos(th)[:, None] * a_loc + np.sin(th)[:, None] * e2
    need = np.zeros(n)
    for c in np.linspace(-W / 2, W / 2, 5):
        Dc = unit(D + (c / 70.0) * nrm); need = np.maximum(need, E.min_radius(group, Dc, clear=CLEAR))
    plane_a = la / np.maximum(np.cos(th), 1e-3); plane_b = lb / np.maximum(np.cos(ang - th), 1e-3)
    in_a = np.tan(th) * la <= HUB_R + 1.0; in_b = np.tan(ang - th) * lb <= HUB_R + 1.0
    lb_ = np.where(in_a, plane_a, np.where(in_b, plane_b, need))                          # flush with the hubs, else the skin
    kslope = math.tan(CLIMB) * np.mean([la, lb]) * (th[1] - th[0])                      # mm per station at the climb limit
    idx = np.arange(n); u = np.max(lb_[None, :] - kslope * np.abs(idx[:, None] - idx[None, :]), axis=1)
    u = np.where(in_a, plane_a, np.where(in_b, plane_b, u))
    return th, D, nrm, u, need


def strap_solid(Dw, nw, u, w=W, t=T):
    """lofted strap: rectangle (w across along nw, t radially) at each station (world dirs Dw, undersides u)"""
    wires = []
    for d, r in zip(Dw, u):
        q = [r * d - w / 2 * nw, r * d + w / 2 * nw, (r + t) * d + w / 2 * nw, (r + t) * d - w / 2 * nw]
        wires.append(cq.Wire.makePolygon([V(p) for p in q], close=True))
    return cq.Solid.makeLoft(wires, ruled=False)


def main():
    t0 = time.time(); C, ax = FR.load(BAND); E = Envelope(os.path.join(FR.FULL, "designs", BAND))
    ci, fi, f0 = next(FR.followed(C)); X0 = FR.frame_of(f0)                                 # reference frame f0
    loc = lambda g, w: X0[g][0].T @ w                                                    # world dir -> group-local dir
    J1w = X0["base"][0] @ ax["J1"][1]; J2w = X0["l2"][0] @ ax["J2"][1]; J3w = X0["l2"][0] @ ax["J3"][1]
    RH, tH = X0["H"]; GH_H = RH.T @ (-tH)                                                # GH in the arm's rest frame
    print(f"reference: clip {C['clips'][ci]['name']} frame {fi}; GH in the H rest frame {np.round(GH_H, 3)}")
    # ---- joint faces: the evaluator's, raised only if the envelope needs it
    fc = INP["faces"]; F = {"J1": float(fc["1"]), "J2": float(fc["2"]), "J3": float(fc.get("zj4", fc["3"]))}
    HR = AE.HR                                                                            # arm rest <- canonical humerus frame
    can = lambda w: HR.T @ (RH.T @ w)                                                    # world dir -> canonical humerus dir at f0
    F["J1"] = max(F["J1"], disc_face(E, "l1", loc("l1", J1w), F["J1"]))
    F["J2"] = max(F["J2"], disc_face(E, "l1", loc("l1", J2w), F["J2"]))
    F["J3"] = max(F["J3"], disc_face(E, "can", can(J3w), F["J3"]))
    print("joint faces (mm from GH):", {j: round(v, 2) for j, v in F.items()}, "evaluator:", {k: round(v, 2) for k, v in fc.items()})
    parts = []
    parts += joint_parts("J1", J1w, F["J1"], "l1", "base")
    parts += joint_parts("J2", J2w, F["J2"], "l1", "l2")
    parts += joint_parts("J3", J3w, F["J3"], "H", "l2")
    rep = {"faces": F}
    # ---- link 1 (lower at J1 and J2), link 2 (upper at J2 and J3): strap + its hub(s) fused into one part
    for name, g, (a, b), (la, lb) in (("link 1", "l1", (J1w, J2w), (F["J1"], F["J2"])),
                                      ("link 2", "l2", (J2w, J3w), (F["J2"] + LV["U0"], F["J3"] + LV["U0"]))):
        th, D, nrm, u, need = strap_stations(E, g, loc(g, a), loc(g, b), la, lb)
        Rg = X0[g][0]; s = strap_solid((Rg @ D.T).T, Rg @ nrm, u)
        rep[name] = dict(under_mm=np.round(u, 2).tolist(), need_mm=np.round(need, 2).tolist(), arc_deg=round(math.degrees(th[-1]), 2),
                         rise_over_skin_mm=round(float((u - need)[(u - need) < 50].max()), 2))
        parts.append((g, f"D5 {name} strap 8x3 (Ti-6Al-4V)", s))
        print(f"{name}: arc {math.degrees(th[-1]):.1f} deg, underside {u.min():.1f}..{u.max():.1f} mm, max height over the skin need {(u - need).max():.1f} mm")
    # ---- fuse each member's own hub bodies into it (one machined part per member)
    def fuse(group, keys, newname):
        idx = [i for i, (g, n, _) in enumerate(parts) if g == group and any(k in n for k in keys)]
        s = parts[idx[0]][2]
        for i in idx[1:]: s = s.fuse(parts[i][2])
        s = s.clean(); keep = [p for i, p in enumerate(parts) if i not in idx]; keep.append((group, newname, s)); return keep
    parts = fuse("l1", ("link 1 strap", "J1 pad", "J2 pad"), "D5-02 link 1: strap + J1/J2 pads + integral pins (Ti-6Al-4V)")
    parts = fuse("l2", ("link 2 strap", "J2 boss", "J3 boss"), "D5-03 link 2: strap + J2/J3 bosses (Ti-6Al-4V)")
    # ---- scapula base (upper at J1): boss + a mounting tab toward the user's scapula handler
    tab_dir = unit(np.array(json.load(open(os.path.join(FR.FULL, "designs", f"cad_{KEY}", "design.json"))).get("base_tab", [0.0, 0.6, -0.8])))
    a_loc = loc("base", J1w); tdir = unit(tab_dir - (tab_dir @ a_loc) * a_loc); tip = unit(math.cos(math.radians(32)) * a_loc + math.sin(math.radians(32)) * tdir)
    th, D, nrm, u, need = strap_stations(E, "base", a_loc, tip, F["J1"] + LV["U0"], F["J1"] + LV["U0"], n=20)
    u = np.maximum(u, need); Rb = X0["base"][0]
    tab = strap_solid((Rb @ D.T).T, Rb @ nrm, u, w=16.0, t=3.0)
    end = (Rb @ D[-1]) * (u[-1] + 1.5)
    for c in (-4.5, 4.5):                                                                  # 2x M4 clearance holes at the tab end
        p = end + c * (Rb @ nrm); hole = cq.Solid.makeCylinder(2.2, 12, V(p - 6 * (Rb @ D[-1])), V(Rb @ D[-1])); tab = tab.cut(hole)
    parts = [(g, n, s) for g, n, s in parts]
    i = [k for k, (g, n, _) in enumerate(parts) if g == "base" and "boss" in n][0]
    parts[i] = ("base", "D5-01 scapula base: J1 boss + handler tab, 2x M4 (Ti-6Al-4V)", parts[i][2].fuse(tab).clean())
    # ---- arm end (lower at J3): pad + neck to the lap pad on BOTTOM's bar (4x M3 countersunk, arm_end.LAP_HOLES)
    c_can, ub_can, vb_can, up_can = AE.bar_lap_frame()                                   # canonical frame
    to_w = lambda p_can: RH @ (HR @ np.asarray(p_can)) + tH                               # canonical point -> world at f0
    to_wd = lambda d_can: RH @ (HR @ np.asarray(d_can))
    c_w, ub_w, vb_w, up_w = to_w(c_can), to_wd(ub_can), to_wd(vb_can), to_wd(up_can)
    # lap plate: 26 (along the bar) x 18 x 3 on the bar top
    Rl = np.stack([ub_w, vb_w, up_w], 1)
    lap = xform(cq.Workplane("XY").box(26, 18, 3.0, centered=(True, True, False)).edges("|Z").fillet(3.0).val(), Rl, c_w)
    pad_edge = F["J3"] * unit(J3w)                                                        # pad centre on the J3 axis
    k3 = unit(J3w); d_to = unit((c_w - pad_edge) - ((c_w - pad_edge) @ k3) * k3)
    p0 = pad_edge + (HUB_R - 2.0) * d_to + 3.0 * k3; p3 = c_w + 3.0 * up_w + 9.0 * ub_w        # neck top flush with the pad / lap tops
    p1 = p0 + 0.35 * np.linalg.norm(p3 - p0) * d_to; p2 = p3 + 0.35 * np.linalg.norm(p3 - p0) * ub_w
    secs = []
    for s_ in np.linspace(0, 1, 14):
        b = (1 - s_) ** 3 * p0 + 3 * (1 - s_) ** 2 * s_ * p1 + 3 * (1 - s_) * s_ ** 2 * p2 + s_ ** 3 * p3
        tg = unit(3 * (1 - s_) ** 2 * (p1 - p0) + 6 * (1 - s_) * s_ * (p2 - p1) + 3 * s_ ** 2 * (p3 - p2))
        upv = unit((1 - s_) * k3 + s_ * up_w); upv = unit(upv - (upv @ tg) * tg); lat = np.cross(tg, upv)
        q = [b - 6 * lat - 3 * upv, b + 6 * lat - 3 * upv, b + 6 * lat, b - 6 * lat]          # 12 x 3, under link 2's level
        secs.append(cq.Wire.makePolygon([V(x) for x in q], close=True))
    neck = cq.Solid.makeLoft(secs, ruled=False)
    i = [k for k, (g, n, _) in enumerate(parts) if g == "H" and "J3 pad" in n][0]
    arm = parts[i][2].fuse(neck).fuse(lap).clean()
    for s_, y_ in AE.LAP_HOLES:                                                          # 4x M3 countersunk, on BOTTOM's tapped holes
        pc = RH @ (AE.CB + s_ * AE.uB + y_ * AE.vB) + tH                                  # rest frame -> world
        pc = pc + ((c_w - pc) @ up_w) * up_w                                              # onto the bar top
        arm = arm.cut(cq.Solid.makeCylinder(1.7, 12.0, V(pc - 4.0 * up_w), V(up_w)))
        arm = arm.cut(cq.Solid.makeCone(1.7, 3.3, 1.6, V(pc + 1.45 * up_w), V(up_w)))
    parts[i] = ("H", "D5-04 arm end: J3 pad + pin + neck + lap plate on BOTTOM (Ti-6Al-4V)", arm)
    rep["neck"] = dict(length_mm=round(float(np.linalg.norm(p3 - p0)), 1))
    # ---- world -> group local, + the user's arm parts (already in the H / F rest frames)
    out = []
    for g, n, s in parts:
        R, t = X0[g]; out.append((g, n, xform(s, R.T, -R.T @ t)))
    for g, n, s in AE.user_parts(): out.append((g, n, s))
    print(f"{len(out)} parts built in {time.time() - t0:.0f} s")
    return out, rep, C


def export(parts, rep, C):
    import trimesh
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    shutil.copy(os.path.join(FR.FULL, "designs", BAND, "clips.json"), os.path.join(OUT, "clips.json"))
    d = json.load(open(os.path.join(FR.FULL, "designs", f"cad_{KEY}", "design.json")))
    d.update(id=f"param_{KEY}", built_with="pipeline/conformal/param_cad/param_build.py (parametric B-rep, v5 joints, 8x3 straps)",
             label=f"3R champion {KEY}, parametric CAD")
    json.dump(d, open(os.path.join(OUT, "design.json"), "w"), indent=1)
    sc = trimesh.Scene(); info = []
    for i, (g, n, s) in enumerate(parts):
        ok = s.isValid(); vol = s.Volume()
        if not n.startswith(("BOTTOM", "TOP", "MIDDLE", "FOREARM", "UPPER ARM", "Hex", "M4", "IGUS", "5mm", "Revolve", "CirPattern")):
            cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, "step", f"{i:02d}_{n.split(':')[0].replace('/', '_').replace(' ', '_')[:40]}.step"))
        vs, fs = s.tessellate(0.02 if n.startswith(('J', 'D5')) else 0.08, 0.2 if n.startswith(('J', 'D5')) else 0.4)
        m = trimesh.Trimesh(np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs), process=False)
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        info.append(dict(group=g, name=n, valid=bool(ok), volume_mm3=round(vol, 1)))
    sc.export(os.path.join(OUT, "exo.glb"))
    json.dump(dict(rep, parts=info), open(os.path.join(OUT, "build.json"), "w"), indent=1)
    USER = ("BOTTOM", "TOP", "MIDDLE", "FOREARM", "UPPER ARM", "Hex", "M4", "IGUS", "5mm", "Revolve", "CirPattern")
    def mat(n):
        if n.startswith(USER): return "user part", None
        if "bearing" in n or "17-4PH" in n: return ("bearing steel" if "bearing" in n else "17-4PH"), 7.8
        return "Ti-6Al-4V", 4.43
    pf = []
    for k, (p_, (g, n, s)) in enumerate(zip(info, parts)):
        m_, rho = mat(n); pf.append(dict(k=k, group=g, name=n, vol_cm3=round(p_["volume_mm3"] / 1000, 3), material=m_,
                                         mass_g=None if rho is None else round(p_["volume_mm3"] / 1000 * rho, 2), valid=p_["valid"], faces=len(s.Faces())))
    json.dump(dict(key=KEY, n=3, FACES={"1": rep["faces"]["J1"], "2": rep["faces"]["J2"], "3": rep["faces"]["J3"]}, parts=pf),
              open(os.path.join(OUT, "parts_full.json"), "w"), indent=1)
    ws = os.path.join(FR.FULL, "designs", f"cad_{KEY}", "workspace.json")
    if os.path.exists(ws): shutil.copy(ws, os.path.join(OUT, "workspace.json"))
    print("custom-part mass", round(sum(q["mass_g"] or 0 for q in pf), 1), "g")
    bad = [p for p in info if not p["valid"]]
    print(f"exported {len(info)} parts -> {OUT}; invalid solids: {[p['name'] for p in bad] or 'none'}")


if __name__ == "__main__":
    P, rep, C = main()
    export(P, rep, C)
