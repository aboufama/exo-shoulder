"""Export-only companion of user_style.py for the engineering drawings (modelling paused: nothing here re-fits or changes
the CAD). For the built design param2_r20_n3_s1414_4 it writes, to drawings/2026-10-15_user_style_3R/:

  step/D6-05_upper_arm_cuff.step   the UPPER ARM CUFF B-rep from user_style.upper_cuff(E) with main()'s own inputs (the
                                   export skips names starting 'UPPER ARM' as user parts, so it never reached step/)
  step/D6-01..04_*.step            the four custom parts, copied from the design's step/ with clean names
  step/ASSEMBLY_rest_pose.step     every part of exo.glb at the REST pose (plane 0, elev 0, axial 0, elbow at the rig's
                                   rest flexion), one frame: origin GH, x anterior, y up, z lateral (right), mm; one named
                                   solid per part + construction axes J1, J2, J3 through GH and a GH marker
  layout.json / layout.md          axes at rest, angles, hub faces, GH in BOTTOM's bar frame, J3 vs the bar, J1 vs the
                                   scapula base's mounting face - measured on the re-loaded STEP solids

Every exported solid is re-loaded and checked against exo.glb's mesh of the same part (posed at the rest frame).

    python3 export_drawing_steps.py
"""
import json, math, os, shutil, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.argv = sys.argv[:1]
import user_style as US                                                                   # noqa: E402  (imports param_build, sketch2d)
import cadquery as cq                                                                     # noqa: E402
import trimesh, igl                                                                       # noqa: E402
PB, FR, AE = US.PB, US.FR, US.AE
import body_pose as BP                                                                    # noqa: E402
sys.path.insert(0, FR.FULL); from load_arm import load as load_xcaf                       # noqa: E402

DES = os.path.join(FR.FULL, "designs", "param2_r20_n3_s1414_4")
OUTD = os.path.join(FR.REPO, "drawings", "2026-10-15_user_style_3R"); STEPD = os.path.join(OUTD, "step")
os.makedirs(STEPD, exist_ok=True)
unit = lambda v: np.asarray(v, float) / np.linalg.norm(v)
D2R = math.pi / 180


def mesh_of(s, tol=0.005, ang=0.1):
    vs, fs = s.tessellate(tol, ang); return np.array([[v.x, v.y, v.z] for v in vs]), np.array(fs, dtype=np.int64)


def one_way(P, V, F):
    """max / mean distance of points P to the triangle mesh (V, F)"""
    d2, _, _ = igl.point_mesh_squared_distance(np.ascontiguousarray(P, float), np.ascontiguousarray(V, float), np.ascontiguousarray(F, np.int64))
    d = np.sqrt(d2); return float(d.max()), float(d.mean())


def compare(shape, Pg, Fg):
    """glb mesh (Pg, Fg) vs B-rep: glb vertices -> B-rep (fine tessellation, 5 um chord) and B-rep -> glb mesh"""
    V, F = mesh_of(shape); a = one_way(Pg, V, F); b = one_way(V, Pg, Fg)
    return dict(glb_to_brep_max=a[0], glb_to_brep_mean=a[1], brep_to_glb_max=b[0], brep_to_glb_mean=b[1], hausdorff=max(a[0], b[0]))


# ---------------------------------------------------------------- the rest pose and its group transforms
LM = json.load(open(os.path.join(FR.REPO, "pipeline", "avg", "body_mesh.json")))
REST_P = [0.0, 0.0, 0.0, float(LM["landmarks"]["rest_flex"]), 0.0]                       # the rig's rest: arm hanging, elbow at rest flexion
WS = json.load(open(os.path.join(DES, "workspace.json")))
iw = [i for i, p in enumerate(WS["poses"]) if p["p"][:3] == [0.0, 0.0, 0.0] and "G" in p][0]  # the chain at the same humerus pose
sg, _ = BP.segs(LM["landmarks"], LM["scale"], dict(zip(["plane", "elev", "axial", "flex", "pron"], REST_P)))
X = {g: (np.array(G).reshape(3, 3), np.zeros(3)) for g, G in WS["poses"][iw]["G"].items()}
X["H"] = (np.array(sg[2][0]), np.array(sg[2][1])); X["F"] = (np.array(sg[3][0]), np.array(sg[3][1]))
for g, (R, t) in X.items():
    assert abs(np.linalg.det(R) - 1) < 1e-9 and np.abs(R @ R.T - np.eye(3)).max() < 1e-9, g
assert np.abs(X["S"][0] - np.eye(3)).max() < 1e-9                                         # the scapula frame is the thorax frame at rest


def to_rest(shape, g):
    R, t = X[g]; return PB.xform(shape, R, t)


GLB = trimesh.load(os.path.join(DES, "exo.glb"))
NODES = {}
for n in GLB.graph.nodes_geometry:
    T_, gn = GLB.graph[n]; g, name, k = n.split("|"); m = GLB.geometry[gn].copy(); m.apply_transform(T_)
    R, t = X[g]; NODES[int(k)] = (g, name, m.vertices @ R.T + t, np.asarray(m.faces, np.int64), m.vertices.copy())
log = {}
t0 = time.time()

# ---------------------------------------------------------------- (1) the upper-arm cuff, exactly as main() builds it
E = PB.Envelope(os.path.join(FR.FULL, "designs", PB.BAND))                                 # main()'s E (upper_cuff takes it, unused inside)
AE.S_CUT = US.S_CUT2; AE.LAP_HOLES = []                                                     # main() sets these before upper_cuff (build.json holes [])
cuff_parts, cuff_rep = US.upper_cuff(E)
cuff = cuff_parts[0][2]
cq.exporters.export(cq.Workplane().add(cuff), os.path.join(STEPD, "D6-05_upper_arm_cuff.step"))
cuff_re = cq.importers.importStep(os.path.join(STEPD, "D6-05_upper_arm_cuff.step")).val()
built = json.load(open(os.path.join(DES, "build.json")))["upper cuff"]
kc = [k for k, v in NODES.items() if v[1].startswith("UPPER ARM CUFF")][0]
c_loc = compare(cuff_re, NODES[kc][4], NODES[kc][3])                                        # in the H-local (arm rest) frame, as built
log["cuff"] = dict(rep=cuff_rep, build_json=built, same_params=all(abs(float(cuff_rep[k]) - float(built[k])) < 1e-9 for k in built if k != "valid"),
                   valid=cuff_re.isValid(), solids=len(cuff_re.Solids()), faces=len(cuff_re.Faces()), volume_mm3=cuff_re.Volume(),
                   cylinder_holes=sorted({round(f._geomAdaptor().Cylinder().Radius(), 3) for f in cuff_re.Faces() if f.geomType() == "CYLINDER"}),
                   cone_faces=sum(f.geomType() == "CONE" for f in cuff_re.Faces()), vs_glb=c_loc)
print("cuff:", json.dumps(log["cuff"], default=float)[:600], f"({time.time() - t0:.0f} s)")

# ---------------------------------------------------------------- (2) the four custom parts with clean names
SRC = {"D6-02_link_1.step": "00_D6-02_link_1.step", "D6-03_link_2.step": "01_D6-03_link_2.step",
       "D6-01_scapula_base.step": "02_D6-01_scapula_base.step", "D6-04_BOTTOM_arm_end.step": "03_D6-04_BOTTOM_+_arm_end,_one_5-axis_part_.step"}
for dst, src in SRC.items(): shutil.copyfile(os.path.join(DES, "step", src), os.path.join(STEPD, dst))

# ---------------------------------------------------------------- (3) the assembly at rest
parts = []                                                                                 # (k, group, name, shape in the group's local frame)
for f in sorted(os.listdir(os.path.join(DES, "step"))):
    k = int(f[:2]); parts.append((k, NODES[k][0], NODES[k][1], cq.importers.importStep(os.path.join(DES, "step", f)).val()))
k = 22
for g, n, s in AE.user_parts():                                                            # main()'s order: user parts after the hardware
    if n.startswith(("UPPER ARM CUFF", "M4x6 ISO 10642 countersunk (upper cuff)", "BOTTOM")): continue
    assert NODES[k][1] == n and NODES[k][0] == g, (k, n, NODES[k][:2]); parts.append((k, g, n, s)); k += 1
for g, n, s in cuff_parts:
    assert NODES[k][1] == n, (k, n, NODES[k][1]); parts.append((k, g, n, cuff_re if k == kc else s)); k += 1
assert sorted(p[0] for p in parts) == sorted(NODES), "every exo.glb node has a solid"

# construction axes (thin rods from 10 mm behind GH to 25 mm beyond each hub face) and a GH marker
J3H = FR.axis_in(*FR.load(PB.BAND), "J3", "H"); assert J3H[1] < 1e-6
AX = {"J1": X["base"][0] @ np.array([1.0, 0, 0]), "J2": X["l2"][0] @ np.array([1.0, 0, 0]),
      "J3": X["l2"][0] @ np.array(json.load(open(os.path.join(DES, "clips.json")))["axes"][3][1])}
assert np.degrees(math.acos(np.clip(AX["J3"] @ (X["H"][0] @ J3H[0]), -1, 1))) < 1e-4       # the chain closes on the humerus at rest
FACES = built_faces = json.load(open(os.path.join(DES, "build.json")))["faces"]
COL = {"custom": (0.72, 0.72, 0.75), "hw": (0.55, 0.57, 0.60), "user": (0.85, 0.45, 0.10), "J1": (0.85, 0.1, 0.1), "J2": (0.1, 0.65, 0.1), "J3": (0.1, 0.25, 0.9)}
assy = cq.Assembly(name="exo_3R_rest_pose_GH_origin_x_ant_y_up_z_lat")
placed = []
CLEAN = {0: "D6-02 link 1", 1: "D6-03 link 2", 2: "D6-01 scapula base", 3: "D6-04 BOTTOM + arm end", kc: "D6-05 upper arm cuff"}
for k, g, n, s in sorted(parts, key=lambda p: p[0]):
    w = to_rest(s, g); kind = "custom" if k in CLEAN else ("hw" if k < 22 or "(upper cuff)" in n else "user")
    nm = f"{k:02d} {CLEAN.get(k, n)} [{g}]"
    assy.add(w, name=nm, color=cq.Color(*COL[kind])); placed.append((k, nm, w))
for j, a in AX.items():
    L = float(FACES[j]) + 25.0
    assy.add(cq.Solid.makeCylinder(0.3, L + 10.0, PB.V(-10.0 * a), PB.V(a)), name=f"AXIS {j} through GH (construction, r 0.3)", color=cq.Color(*COL[j]))
assy.add(cq.Solid.makeSphere(1.5, angleDegrees1=-90, angleDegrees2=90), name="GH centre (construction, O3)", color=cq.Color(0.1, 0.1, 0.1))
ASM = os.path.join(STEPD, "ASSEMBLY_rest_pose.step")
assy.save(ASM, exportType="STEP")
print(f"assembly written: {len(placed)} parts + 3 axes + GH ({time.time() - t0:.0f} s)")

# re-load and check every solid against exo.glb at the rest frame
back = load_xcaf(ASM)
byname = {}
for nm, inst, s in back: byname.setdefault(inst if inst != "?" else nm, []).append(s)
chk = []
for k, nm, _ in placed:
    ss = byname.get(nm) or [s for n_, i_, s in back if nm in (n_, i_)]
    assert len(ss) == 1, (nm, len(ss), list(byname)[:5])
    s = ss[0]; g, name, Pg, Fg, _ = NODES[k]; c = compare(s, Pg, Fg)
    chk.append(dict(k=k, name=nm, group=g, solids=len(s.Solids()), valid=s.isValid(), **c))
names_back = sorted(byname)
log["assembly"] = dict(file=os.path.relpath(ASM, FR.REPO), n_parts=len(placed), n_named_back=len(names_back), checks=chk,
                       worst_glb_to_brep=max(c["glb_to_brep_max"] for c in chk), worst_hausdorff=max(c["hausdorff"] for c in chk))
print("assembly check: worst glb->brep %.4f mm, worst two-way %.4f mm (%s)" % (log["assembly"]["worst_glb_to_brep"], log["assembly"]["worst_hausdorff"],
      max(chk, key=lambda c: c["hausdorff"])["name"]))
SHAPE = {k: s for k, nm, s in placed}
for nm in names_back:
    if nm.startswith("AXIS"):
        s = byname[nm][0]; j = nm.split()[1]; cyl = [f for f in s.Faces() if f.geomType() == "CYLINDER"][0]
        a = np.array(cyl._geomAdaptor().Cylinder().Axis().Direction().Coord()); o = np.array(cyl._geomAdaptor().Cylinder().Axis().Location().Coord())
        log.setdefault("axes_back", {})[j] = dict(angle_err_deg=float(np.degrees(math.acos(min(1, abs(a @ AX[j]))))), offset_from_GH_mm=float(np.linalg.norm(np.cross(o, AX[j]))))


# ---------------------------------------------------------------- (4) layout, measured on the re-loaded solids
def cyl_faces(s):
    out = []
    for f in s.Faces():
        if f.geomType() != "CYLINDER": continue
        c = f._geomAdaptor().Cylinder(); out.append((c.Radius(), np.array(c.Axis().Direction().Coord()), np.array(c.Axis().Location().Coord()), f))
    return out


def plane_faces(s):
    out = []
    for f in s.Faces():
        if f.geomType() != "PLANE": continue
        p = f._geomAdaptor().Plane(); n = np.array(p.Axis().Direction().Coord()); o = np.array(p.Location().Coord())
        out.append((n, o, f))
    return out


re_shape = {k: byname[nm][0] for k, nm, _ in placed}
ang = lambda a, b: float(np.degrees(math.acos(np.clip(a @ b, -1, 1))))
b_vec = lambda az, el: np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
w_dir = lambda d, a: np.array([math.sin(d * D2R) * math.sin(a * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(a * D2R)])
kin = json.load(open(os.path.join(DES, "design.json")))["kinematics"]
Z = np.load(__import__("io").BytesIO(__import__("gzip").decompress(__import__("base64").b64decode(open(os.path.join(PB.CONF, "band_poses.b64")).read()))))
ip = int(np.argmin(np.abs(Z["POSE"] - np.array(REST_P)).sum(1)))
ev = dict(pose=Z["POSE"][ip].tolist(), J1=(Z["RS"][ip] @ b_vec(kin["az"], kin["el"])).tolist(), J3=(Z["RS"][ip] @ Z["HG"][ip] @ w_dir(*kin["w"])).tolist())

# hub axes and faces measured on the hubs: the cylinders of radius 10 (O20 hub) coaxial with each joint, and the planar
# faces normal to it (the lowest = the joint face F: underside of the lower pad)
hub = {}
own = {"J1": (2, 0), "J2": (0, 1), "J3": (3, 1)}                                           # (upper member k, lower member k)
for j, (ku, kl) in own.items():
    a = AX[j]; r = {}
    for kk in (ku, kl):
        cs = [(R_, d_, o_) for R_, d_, o_, _ in cyl_faces(re_shape[kk]) if abs(abs(d_ @ a) - 1) < 1e-6 and np.linalg.norm(np.cross(o_, a)) < 1e-4]
        ps = sorted(float(o_ @ n_ * np.sign(n_ @ a)) for n_, o_, _ in plane_faces(re_shape[kk]) if abs(abs(n_ @ a) - 1) < 1e-9)
        r[kk] = dict(coaxial_cylinders=sorted({round(R_, 3) for R_, _, _ in cs}), planes_normal_to_axis_mm_from_GH=[round(p, 3) for p in ps])
    hub[j] = dict(face_build_json=float(FACES[j]), lower_member_lowest_plane=r[kl]["planes_normal_to_axis_mm_from_GH"][0], members=r)

# BOTTOM's bar frame (H-local = arm rest frame) and its rest-world image
RH = X["H"][0]; CB, uB, vB, axB = (np.asarray(v, float) for v in (AE.CB, AE.uB, AE.vB, AE.axB))
orth = float(np.abs(np.array([uB, vB, axB]) @ np.array([uB, vB, axB]).T - np.eye(3)).max())
GHb = -CB; k3H = RH.T @ AX["J3"]
bar = dict(origin_CB_H_local=CB.tolist(), uB_up_bar=uB.tolist(), vB_across=vB.tolist(), axB_hinge_axis_bar_normal=axB.tolist(), orthonormal_err=orth,
           CB_rest_world=(RH @ CB).tolist(), uB_rest_world=(RH @ uB).tolist(), vB_rest_world=(RH @ vB).tolist(), axB_rest_world=(RH @ axB).tolist(),
           bar_top_plane_normal_offset=AE.Z_TOP_BAR, bar_skin_side_plane_normal_offset=AE.Z_SKIN_BAR, bottom_cut_s=US.S_CUT2)
GH_bar = dict(s_along_bar_from_elbow_hinge=float(GHb @ uB), lateral_vB=float(GHb @ vB), normal_axB=float(GHb @ axB))
t_top = (AE.Z_TOP_BAR + CB @ axB) / (k3H @ axB); p_top = t_top * k3H - CB
J3_bar = dict(components_uB_vB_axB=[float(k3H @ uB), float(k3H @ vB), float(k3H @ axB)],
              angle_to_bar_normal_axB_deg=ang(k3H, axB), angle_to_bar_axis_uB_deg=ang(k3H, uB), angle_to_across_vB_deg=ang(k3H, vB),
              tilt_about_uB_deg=float(np.degrees(math.atan2(k3H @ vB, k3H @ axB))), tilt_about_vB_deg=float(np.degrees(math.atan2(k3H @ uB, k3H @ axB))),
              hub_face_centre_in_bar_frame=dict(zip(("s", "lateral", "normal"), (float((FACES["J3"] * k3H - CB) @ e) for e in (uB, vB, axB)))),
              axis_meets_bar_top_plane_at=dict(s=float(p_top @ uB), lateral=float(p_top @ vB), mm_from_GH=float(t_top)))

# the scapula base's mounting face: the tab's 2x M4 (O4.3) holes; counterbores (O7.3) on the outer face, so the tab
# is screwed from outside onto the handler under it - the mounting face is the tab's inner (skin-side) face
base = re_shape[2]; holes = [(d_, o_) for R_, d_, o_, _ in cyl_faces(base) if abs(R_ - 2.15) < 1e-3]
assert all(abs(abs(unit(d_) @ unit(holes[0][0])) - 1) < 1e-9 for d_, _ in holes)
nh = unit(holes[0][0]); cen = [o_ for _, o_ in holes]                                    # hole axis; axis points (reduced to the face below)
P_tab = [(n_, o_) for n_, o_, _ in plane_faces(base) if abs(abs(n_ @ nh) - 1) < 1e-6]
pc = [np.asarray(f.Center().toTuple()) for n_, o_, f in plane_faces(base) if abs(abs(n_ @ nh) - 1) < 1e-6]
outer_dir = nh if np.mean(pc, 0) @ nh > 0 else -nh                                         # radially outward (away from GH)
lev_o = sorted({round(float(o_ @ outer_dir), 4) for n_, o_ in P_tab})
cb = [R_ for R_, d_, o_, _ in cyl_faces(base) if abs(R_ - 3.65) < 1e-3]
inner_lev, outer_lev = lev_o[0], lev_o[-1]
hc = [c - (c @ outer_dir - inner_lev) * outer_dir for c in cen]                              # hole centres on the mounting face
hc = sorted({tuple(np.round(h, 6)) for h in hc}); hc = [np.array(h) for h in hc]
assert len(hc) == 2, hc
O = (hc[0] + hc[1]) / 2; zf = -outer_dir; xf = unit(hc[1] - hc[0]); yf = np.cross(zf, xf)
inF = lambda p: [float((p - O) @ e) for e in (xf, yf, zf)]; dF = lambda v: [float(v @ e) for e in (xf, yf, zf)]
k1 = AX["J1"]; tpl = ((O - 0) @ zf) / (k1 @ zf) if abs(k1 @ zf) > 1e-9 else None
mount = dict(note="mounting face = the tab's inner (skin-side) face; the 2x M4 counterbores are on the outer face, so the tab is screwed from outside onto the handler",
             face_frame=dict(origin_mid_between_holes_world=O.tolist(), x_hole_to_hole=xf.tolist(), y=yf.tolist(), z_face_normal_out_of_part_toward_handler=zf.tolist()),
             hole_spacing_mm=float(np.linalg.norm(hc[1] - hc[0])), hole_dia=4.3, counterbore_dia=7.3 if cb else None, counterbore_depth=1.2,
             tab_planes_along_outward_normal_mm_from_GH=lev_o, tab_thickness=float(outer_lev - inner_lev), face_distance_from_GH=float(abs(O @ zf)),
             J1_in_face_frame=dF(k1), angle_J1_to_face_normal_deg=ang(k1, zf), angle_J1_to_face_plane_deg=90.0 - ang(k1, zf) if ang(k1, zf) <= 90 else ang(k1, zf) - 90.0,
             GH_in_face_frame=inF(np.zeros(3)), J1_hub_face_centre_in_face_frame=inF(FACES["J1"] * k1),
             J1_axis_meets_face_plane_at=None if tpl is None else dict(zip(("x", "y"), inF(tpl * k1)[:2]), mm_from_GH_along_J1=float(tpl)))

angles = {"J1-J2": ang(AX["J1"], AX["J2"]), "J2-J3": ang(AX["J2"], AX["J3"]), "J1-J3": ang(AX["J1"], AX["J3"])}
layout = dict(design="param2_r20_n3_s1414_4",
              frame="rest pose world: origin = GH centre, x anterior, y up, z lateral (right); mm. Rest pose = plane 0, elevation 0, axial 0, elbow at the rig's rest flexion %.2f deg (arm hanging); the chain (S, l1, l2) from workspace.json pose %d (same humerus pose)" % (REST_P[3], iw),
              rest_pose=REST_P,
              kinematics=dict(kin, convention="b = bvec(az, el) fixed in the scapula, W = wdir(delta, az) fixed in the humerus, J2 from the two-circle closure on branch -1 (tools/concept_baseline.py)"),
              axes_rest=dict({j: a.tolist() for j, a in AX.items()}, J3_in_humerus_frame=k3H.tolist(), evaluator_rest_pose_cross_check=dict(ev, J1_err_deg=ang(np.array(ev["J1"]), AX["J1"]), J3_err_deg=ang(np.array(ev["J3"]), AX["J3"]))),
              angles_deg=dict(angles, design_arc_J1_J2=kin["a"][0], design_arc_J2_J3=kin["a"][1]),
              hub_faces_mm_from_GH={j: float(FACES[j]) for j in FACES}, hubs_measured=hub,
              stack_levels_mm_above_face=dict(PB.LV), hub_dia=2 * PB.HUB_R, link_section=f"{PB.W:g} x {PB.T:g}",
              GH_in_BOTTOM_bar_frame=GH_bar, BOTTOM_bar_frame=bar, J3_vs_BOTTOM_bar=J3_bar, J1_vs_scapula_base_mounting_face=mount,
              cuff=log["cuff"], assembly_check=dict(file=log["assembly"]["file"], parts=log["assembly"]["n_parts"], worst_glb_to_brep_mm=log["assembly"]["worst_glb_to_brep"],
                                                    worst_two_way_mm=log["assembly"]["worst_hausdorff"], per_part=chk, axes_back=log.get("axes_back")))
json.dump(layout, open(os.path.join(OUTD, "layout.json"), "w"), indent=1, default=float)
print(json.dumps({k: layout[k] for k in ("axes_rest", "angles_deg", "hub_faces_mm_from_GH", "GH_in_BOTTOM_bar_frame", "J3_vs_BOTTOM_bar", "J1_vs_scapula_base_mounting_face")}, indent=1, default=float))
print("hubs", json.dumps(hub, default=float))
print(f"done in {time.time() - t0:.0f} s")
