"""Task 1: load the Seth 2016 model in OpenSim 4.6 and print its structure, the AC constraint, the scapulothoracic ellipsoid,
the ISB frames built from its markers and the derived girdle geometry. Checks:
  (a) OpenSim 4.6's built-in ScapulothoracicJoint reproduces the 3.2 plugin's definition (ScapulothoracicJointPlugin/
      source/ScapulothoracicJoint.cpp addToSystem: Simbody Ellipsoid mobilizer + winging Pin + Weld), re-implemented here
      in numpy, at random coordinates;
  (b) the GH joint centre = the humerus body origin (no GH translation; sphere fit of the humeral head mesh);
  (c) the default (assembled) posture's ISB angles.
Writes model_facts.json next to this file.   Run: .cache/opensim-venv/bin/python pipeline/girdle/opensim_seth/model_facts.py
"""
import json, math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opensim as osim
from seth_model import Seth, GIRDLE, GHC, MODEL, HERE, v3, unit

S = Seth(); m, s = S.m, S.s
facts = dict(model_file=os.path.relpath(MODEL, os.path.join(HERE, "..", "..", "..")), opensim=osim.GetVersion(),
             nq=s.getNQ(), nu=s.getNU())
print("OpenSim", osim.GetVersion(), "| model", m.getName(), "| nq", s.getNQ(), "nu", s.getNU(),
      "(the Ellipsoid mobiliser reserves 4 q slots for 3 Euler angles)")
print("\nBODIES (mass kg, COM m):")
for b in m.getBodySet(): print(f"  {b.getName():9s} {b.getMass():7.4f}  com {np.round(v3(b.getMassCenter()), 4)}")
print("\nJOINTS (parent offset frame -> child offset frame; translation m, orientation body-XYZ rad):")
J = {}
for j in m.getJointSet():
    pf, cf = osim.PhysicalOffsetFrame.safeDownCast(j.getParentFrame()), osim.PhysicalOffsetFrame.safeDownCast(j.getChildFrame())
    rec = dict(type=j.getConcreteClassName(), parent=pf.getParentFrame().getName(), child=cf.getParentFrame().getName(),
               parent_offset=dict(t=v3(pf.get_translation()).tolist(), r=v3(pf.get_orientation()).tolist()),
               child_offset=dict(t=v3(cf.get_translation()).tolist(), r=v3(cf.get_orientation()).tolist()), coords=[])
    cj = osim.CustomJoint.safeDownCast(j)
    if cj:
        st = cj.getSpatialTransform()
        for i in range(6):
            ta = st.getTransformAxis(i); cn = ta.getCoordinateNamesInArray()
            if cn.getSize(): rec["coords"].append(dict(axis_name=ta.getName(), coord=cn.get(0), axis=v3(ta.getAxis()).round(5).tolist()))
    J[j.getName()] = rec
    print(f"  {j.getName():16s} {rec['type']:21s} {rec['parent']:8s} t={np.round(rec['parent_offset']['t'], 5)} r={np.round(rec['parent_offset']['r'], 4)}"
          f" -> {rec['child']:8s} t={np.round(rec['child_offset']['t'], 5)} r={np.round(rec['child_offset']['r'], 4)}")
    for c in rec["coords"]: print(f"      {c['axis_name']}: {c['coord']:14s} axis {c['axis']}")
facts["joints"] = J
st = osim.ScapulothoracicJoint.safeDownCast(m.getJointSet().get("scapulothoracic"))
ell = dict(radii_xyz_m=v3(st.get_thoracic_ellipsoid_radii_x_y_z()).tolist(),
           winging_axis_origin=[st.get_scapula_winging_axis_origin(0), st.get_scapula_winging_axis_origin(1)],
           winging_axis_direction_rad=st.get_scapula_winging_axis_direction(),
           centre_in_thorax_m=J["scapulothoracic"]["parent_offset"]["t"], orientation_in_thorax_rad=J["scapulothoracic"]["parent_offset"]["r"])
facts["ellipsoid"] = ell
print("\nSCAPULOTHORACIC ELLIPSOID:", ell)
# check against the file
txt = open(MODEL).read()
assert re.search(r"<thoracic_ellipsoid_radii_x_y_z>\s*0.07 0.15 0.07", txt)
print("\nCOORDINATES (deg; range, default, clamped, locked):")
C = {}
for c in m.getCoordinateSet():
    C[c.getName()] = dict(range_deg=[math.degrees(c.getRangeMin()), math.degrees(c.getRangeMax())], default_deg=math.degrees(c.getDefaultValue()),
                          clamped=c.getDefaultClamped(), locked=c.getDefaultLocked(), joint=c.getJoint().getName())
    r = C[c.getName()]
    print(f"  {c.getName():22s} {r['joint']:16s} [{r['range_deg'][0]:7.1f}, {r['range_deg'][1]:6.1f}] def {r['default_deg']:6.1f}"
          f"  clamped={r['clamped']!s:5s} locked={r['locked']}")
facts["coordinates"] = C
print("\nCONSTRAINTS:")
for k in m.getConstraintSet(): print(" ", k.getName(), k.getConcreteClassName())
print(f"  AC PointConstraint: {S.ac_bodies[0]} point {S.ac_clav} m  ==  {S.ac_bodies[1]} point {S.ac_scap} m")
facts["AC_constraint"] = dict(body_1=S.ac_bodies[0], point_1_m=S.ac_clav.tolist(), body_2=S.ac_bodies[1], point_2_m=S.ac_scap.tolist())
lim = {}
for f in m.getForceSet():
    cl = osim.CoordinateLimitForce.safeDownCast(f)
    if cl: lim[cl.getName()] = dict(coord=cl.get_coordinate(), lower_deg=cl.get_lower_limit(), upper_deg=cl.get_upper_limit())
facts["coordinate_limit_forces"] = lim; print("  CoordinateLimitForces (soft limits, dynamics only):", lim)
print("\nMARKERS (body, location m):"); facts["markers"] = {}
for n, (b, loc) in S.mk.items(): print(f"  {n:24s} {b:9s} {np.round(loc, 5)}"); facts["markers"][n] = dict(body=b, loc_m=loc.tolist())

# ---------------------------------------------------------------- ISB thorax vs model thorax
tilt = math.degrees(math.atan2(-S.RT[0, 1], S.RT[1, 1]))
print(f"\nISB thorax (from ij, c7, px, t8): Xt {S.RT[:, 0].round(4)} Yt {S.RT[:, 1].round(4)} Zt {S.RT[:, 2].round(4)}"
      f"  -> rotated {tilt:+.2f} deg about the model z (Yt leans posteriorly)")
facts["isb_thorax"] = dict(axes_in_model_thorax_columns=S.RT.tolist(), origin_IJ_mm=S.IJ.tolist(), tilt_about_z_deg=tilt)
# ISB segment frames expressed in the model's body frames (from the markers, which are body-fixed)
mkb = lambda n: S.mk[n][1] * 1000
AA, TS, AI = mkb("aa"), mkb("ts"), mkb("ai"); Zs = unit(AA - TS); Xs = unit(np.cross(AA - TS, AI - TS)); Ys = np.cross(Zs, Xs)
GHh, EL, EM = mkb("gu"), mkb("EpL"), mkb("EpM"); Yh = unit(GHh - (EL + EM) / 2); Xh = unit(np.cross(EL - GHh, EM - GHh)); Zh = np.cross(Xh, Yh); Xh = np.cross(Yh, Zh)
Zc = unit(mkb("acc") - mkb("sc"))
ang = lambda R: math.degrees(math.acos(max(-1, min(1, (np.trace(R) - 1) / 2))))
fm = dict(scapula_isb_axes_in_scapula_body=np.c_[Xs, Ys, Zs].round(4).tolist(), scapula_body_to_isb_rotation_deg=ang(np.c_[Xs, Ys, Zs]),
          humerus_isb_axes_in_humerus_body=np.c_[Xh, Yh, Zh].round(4).tolist(), humerus_body_to_isb_rotation_deg=ang(np.c_[Xh, Yh, Zh]),
          clavicle_isb_Zc_in_clavicle_body=Zc.round(4).tolist(),
          note="ISB frames are built from the model's own bony-landmark markers (thorax ij/c7/px/t8, clavicle sc/acc, scapula aa/ts/ai, humerus gu/EpL/EpM), "
               "so the body-frame conventions of the model do not enter the angles; these are the fixed rotations between them")
facts["frame_mapping"] = fm
print(f"ISB scapula axes (columns X,Y,Z) in the scapula body frame:\n{np.c_[Xs, Ys, Zs].round(3)}  (body -> ISB rotation {fm['scapula_body_to_isb_rotation_deg']:.1f} deg)")
print(f"ISB humerus axes (columns X,Y,Z) in the humerus body frame:\n{np.c_[Xh, Yh, Zh].round(3)}  (body -> ISB rotation {fm['humerus_body_to_isb_rotation_deg']:.1f} deg)")
print(f"ISB clavicle Zc (SC->acc) in the clavicle body frame: {Zc.round(3)}; Xc is perpendicular to Zc and Yt, so it is not body-fixed")

# ---------------------------------------------------------------- (a) ST joint vs the 3.2 plugin definition (numpy)
def rx(a): c, s_ = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]])
def ry(a): c, s_ = math.cos(a), math.sin(a); return np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])
def rz(a): c, s_ = math.cos(a), math.sin(a); return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])
def bxyz(v): return rx(v[0]) @ ry(v[1]) @ rz(v[2])
def rodr(u, a): u = unit(u); K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]]); return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def T(R, p): M = np.eye(4); M[:3, :3] = R; M[:3, 3] = p; return M
def inv(M): R, p = M[:3, :3], M[:3, 3]; return T(R.T, -R.T @ p)
oip, lip = np.array(J["scapulothoracic"]["parent_offset"]["r"]), np.array(J["scapulothoracic"]["parent_offset"]["t"])
oc, lc = np.array(J["scapulothoracic"]["child_offset"]["r"]), np.array(J["scapulothoracic"]["child_offset"]["t"])
rad = np.array(ell["radii_xyz_m"]); radF = np.array([rad[1], rad[0], rad[2]])         # plugin swaps x and y radii
wd, wo = ell["winging_axis_direction_rad"], ell["winging_axis_origin"]


def plugin_scapula(q):
    X_GF = T(bxyz([oip[0], oip[1], oip[2] + math.pi / 2]), lip)
    R_FM = bxyz(q[:3]); n = R_FM[:, 2]                                    # Simbody Ellipsoid mobiliser: body-XYZ Euler q, M origin =
    p_FM = radF * n                                                       # semi-axes * (M z axis) - on the surface, z only ~ normal
    X_B1M = T(rz(math.pi / 2), np.zeros(3)); X_GB1 = X_GF @ T(R_FM, p_FM) @ inv(X_B1M)
    d = np.array([-math.sin(wd), math.cos(wd), 0]); o = np.array([wo[0], wo[1], 0])
    X_B1B2 = T(rodr(d, q[3]), o - rodr(d, q[3]) @ o)                       # pin about d through o (both frames identical)
    return X_GB1 @ X_B1B2 @ inv(T(bxyz(oc), lc))


rng = np.random.default_rng(1); worst = 0.0
for _ in range(200):
    q = rng.uniform(-0.6, 0.6, 4); S.set_q(GIRDLE[2:], q)
    Ts = S.body["scapula"].getTransformInGround(s); Mo = T(S.R_of(Ts), v3(Ts.p())); Mp = plugin_scapula(q)
    worst = max(worst, np.abs(Mo[:3, 3] - Mp[:3, 3]).max() * 1000, np.abs(Mo[:3, :3] - Mp[:3, :3]).max() * 1000)
print(f"\n(a) OpenSim 4.6 ScapulothoracicJoint vs the 3.2 plugin's maths, 200 random postures: max |diff| {worst:.2e} (mm / 1e-3 rotation-matrix units)")
facts["check_st_joint_vs_plugin_max_diff"] = worst
# contact point stays on the ellipsoid
S.set_q(GIRDLE[2:], [0.3, -0.2, 0.4, 0.5]); qq = S.points()
cp = qq["ScapulaThoracicContactPt"] / 1000; RF = bxyz([oip[0], oip[1], oip[2]]); pl = RF.T @ (cp - lip)
print(f"    scapula contact point on the ellipsoid (x/a)^2+(y/b)^2+(z/c)^2 = {((pl / rad) ** 2).sum():.6f}")

# ---------------------------------------------------------------- (b) GH centre = humerus origin
S.m.assemble(s); s0 = s
P0 = S.pose(); RS0, pS0 = P0["scapula"]; GH0 = RS0.T @ (P0["humerus"][1] - pS0)
mv = 0.0
for x in rng.uniform(-1.2, 1.2, (50, 3)):
    S.set_q(GHC, x); P = S.pose(); mv = max(mv, np.linalg.norm(RS0.T @ (P["humerus"][1] - pS0) - GH0))
gh_loc = np.array(J["glenohumeral"]["parent_offset"]["t"]) * 1000
print(f"(b) humerus origin in the scapula frame {GH0.round(3)} mm = GH joint location in the scapula {gh_loc}; moves {mv:.1e} mm"
      " over 50 random GH postures; marker 'gu' (GH) =", S.mk["gu"])
vtp = open(os.path.join(os.path.dirname(MODEL), "Geometry", "humerus.vtp")).read()
blk = re.search(r'<Points>.*?format="ascii">(.*?)</DataArray>', vtp, re.S).group(1)
V = np.array(blk.split(), float).reshape(-1, 3) * 1000
c = np.zeros(3)
for _ in range(10):                                                       # humeral-head sphere fit: points within 30 mm of c
    sel = V[np.linalg.norm(V - c, axis=1) < 30]; sel = sel[(sel - c)[:, 1] > -8]           # head cap above the anatomical neck
    A = np.c_[2 * sel, np.ones(len(sel))]; b = (sel ** 2).sum(1); x = np.linalg.lstsq(A, b, rcond=None)[0]
    c = x[:3]; r = math.sqrt(x[3] + c @ c)
rms = np.sqrt(((np.linalg.norm(sel - c, axis=1) - r) ** 2).mean())
print(f"    humeral head sphere fit (humerus.vtp, {len(sel)} vertices): centre {c.round(1)} mm from the humerus origin, r {r:.1f} mm, rms {rms:.1f} mm")
facts["check_gh_centre"] = dict(humerus_origin_in_scapula_mm=GH0.tolist(), gh_joint_location_in_scapula_mm=gh_loc.tolist(),
                                max_move_over_gh_coords_mm=mv, head_sphere_centre_mm=c.tolist(), head_sphere_r_mm=r, head_sphere_rms_mm=rms)

# ---------------------------------------------------------------- (c) default assembled posture, derived geometry
s = S.m.initSystem(); S.s = s; S.m.realizePosition(s); q = S.points()
qe = s.getQErr(); print("\n(c) default posture after initSystem (assembled): girdle coords (deg)",
                        dict(zip(GIRDLE, np.degrees(S.get_q(GIRDLE)).round(2))), "| max |qerr|", max(abs(qe.get(i)) for i in range(qe.size())))
ang = S.girdle_angles(q); hum = S.humerus_angles(q)
print("    ISB angles: clavicle retraction %.1f elevation %.1f | scapula IR %.1f UR %.1f PT %.1f | humerus plane %.1f elevation %.1f axial %.1f" % (*ang, *hum))
print("    (Ludewig 2009 Table I relaxed standing: retraction 19.2, elevation 5.9, IR 41.1, UR 5.4, PT -13.5)")
L_acc = np.linalg.norm(q["acc"] - q["sc"]); L_acj = np.linalg.norm(q["ACj_c"] - q["SC"])
r_isb = S.dir_isb(q["GH"] - q["ACj_s"]); sc_gh = S.dir_isb(q["GH"] - q["SC"]); ij_gh = S.to_isb(q["GH"])
print(f"    clavicle SC->acc {L_acc:.1f} mm, SC->AC joint centre {L_acj:.1f} mm (rig 156.4, Xu 2016 154 mm)")
print(f"    AC joint -> GH (ISB thorax, default posture) {r_isb.round(1)} |.| {np.linalg.norm(r_isb):.1f} mm (rig (16.2, -34.9, 24.5) |46.0|)")
print(f"    SC -> GH {sc_gh.round(1)} |.| {np.linalg.norm(sc_gh):.1f} mm ; IJ -> GH {ij_gh.round(1)} |.| {np.linalg.norm(ij_gh):.1f} mm (rig 170.5 / 190.6)")
facts["default_posture"] = dict(girdle_coords_deg=dict(zip(GIRDLE, np.degrees(S.get_q(GIRDLE)).tolist())), isb_girdle_deg=dict(zip(["ret", "elev", "IR", "UR", "PT"], ang.tolist())),
                                isb_humerus_deg=dict(zip(["plane", "elev", "axial"], hum.tolist())))
facts["geometry"] = dict(clavicle_SC_acc_mm=L_acc, clavicle_SC_ACjoint_mm=L_acj, AC_to_GH_isb_default_mm=r_isb.tolist(), SC_to_GH_isb_default_mm=sc_gh.tolist(),
                         IJ_to_GH_isb_default_mm=ij_gh.tolist())
json.dump(facts, open(os.path.join(HERE, "model_facts.json"), "w"), indent=1)
print("\nwrote", os.path.join(HERE, "model_facts.json"))
