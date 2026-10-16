#!/usr/bin/env python3
"""Stage 2 of the zc-frontier-3r CAD-context export: run the model on the VERIFIED configuration and write the skeleton
geometry (axes, hub stacks, link / neck metal) for an outside CAD tool.

    python3 docs/cad_context/zc-frontier-3r/scripts/export_geometry.py WEAR_DIR

WEAR_DIR = the output folder of scripts/fit_and_wear.py (wear.json: the verifier-protocol wear with the take mask). The
fit (Bench(60,160) fast, frozen) is re-run here and its sha256 must equal the one fit_and_wear.py wore.
Writes geometry.json, link_centrelines.csv and skeleton_views.png next to this scripts/ folder. No skin, scan or body
data is written: only the design's own metal, axes and the clearance rules as numbers on that geometry.
"""
import csv, hashlib, importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, HERE)
import fit_and_wear as FW                                                     # noqa: E402

M = FW.model(); K = M.K
import concept_bench as CB                                                    # noqa: E402  (on sys.path through the kit)

WEAR = json.load(open(os.path.join(sys.argv[1], "wear.json")))
P = M.snap(dict(FW.PARAMS))
R6 = lambda x: [round(float(v), 6) for v in np.ravel(x)]
R4 = lambda x: [round(float(v), 4) for v in np.ravel(x)]


def rot(k, deg):
    k = K.unit(np.asarray(k, float)); a = math.radians(deg); X = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * X + (1 - math.cos(a)) * X @ X


SG = np.array([1.0, 1.0, -1.0])                                              # theta = SG * q: distal body relative to proximal, right-hand


def wrap(d): return (np.asarray(d, float) + 180.0) % 360.0 - 180.0


# ---- 1. the fit (verifier protocol, frozen shape) ---------------------------------------------------------------------
B = FW.bench(M, 60, 160, exact=False); _, rf = M.evaluate(B, dict(FW.PARAMS))
PROF = {k: np.asarray(v, float) for k, v in B._kit_last["prof"].items()}
DIG = FW.prof_digest(PROF)
assert DIG == WEAR["profile_sha256"], (DIG, WEAR["profile_sha256"])
F60 = K.frames(B); C_HH = F60.RHG[0].T @ F60.RH[0]                            # constant band-HG -> body_pose humerus rotation
Z = CB._poses_all(); NAMES = [str(n) for n in Z["NAMES"]]; CID = Z["CID"]; POSE = Z["POSE"]


def frames_g(g):
    g = np.atleast_1d(np.asarray(g, int)); RS = Z["RS"][g].astype(float); RHG = RS @ Z["HG"][g].astype(float)
    return K.Frames(RS=RS, RHG=RHG, RH=RHG @ C_HH, clip=np.zeros(len(g), bool), ws=np.zeros(len(g), bool))


# sanity: our frames reproduce the kit's on the fit bench
Fb = frames_g(B.idx); assert np.allclose(Fb.RS, F60.RS) and np.allclose(Fb.RH, F60.RH, atol=1e-9)

# ---- 2. rest pose and the as-built frame -----------------------------------------------------------------------------
ws_id = NAMES.index("Workspace (envelope)")
cand = np.nonzero((CID == ws_id) & np.all(np.abs(POSE[:, :3]) < 1e-6, axis=1))[0]
G_REST = int(cand[0]); FR = frames_g(G_REST); RS0 = FR.RS[0]
CH0 = M.build(B, FR, P); assert bool(np.asarray(CH0.ok)[0]), "chain does not close at rest"
q_rest = np.asarray(CH0.q, float)[0]
AX = {j: K.unit(np.asarray(v, float)[0]) for j, v in CH0.joints.items()}
MEM = {m.name: m for m in CH0.members}
PTS0 = {n: K.member_points(m, PROF[n])[0] for n, m in MEM.items()}           # (m, 3) underside sample points at rest


def to_asbuilt(g, X):
    """thorax coords of pose g -> the as-built frame (base held at its rest attitude): X_ab = RS_rest RS_g^T X"""
    Rg = Z["RS"][g].astype(float); return (RS0 @ Rg.T @ np.asarray(X, float).T).T


# ---- 3. hub stacks -------------------------------------------------------------------------------------------------------
INV2, INV3 = int(P["inv2"]), int(P["inv3"])
STACK = {"J1": dict(lower="base (scapula-handler side, fixed)", upper="link 1"),
         "J2": dict(lower="link 2" if INV2 else "link 1", upper="link 1" if INV2 else "link 2"),
         "J3": dict(lower="link 2" if INV3 else "member 3 (arm-end plate + neck)", upper="member 3 (arm-end plate + neck)" if INV3 else "link 2")}
hubs = {}
for j, hn in (("J1", "hub1"), ("J2", "hub2"), ("J3", "hub3")):
    Fv = float(PROF[hn].max()); assert np.allclose(PROF[hn], Fv)
    k = AX[j]; hubs[j] = dict(
        axis_unit_rest=[round(float(x), 10) for x in k], F_mm=round(Fv, 4),
        F_definition="distance from GH along the axis (outward) to the skin-facing face of the LOWER plate of the stack",
        face_centre_F=[round(float(x), 8) for x in Fv * k], lower_plate_mm=[round(Fv, 4), round(Fv + 3.0, 4)], upper_member_underside=round(Fv + K.STACK, 4),
        crown=round(Fv + K.CROWN, 4), crown_centre=R4((Fv + K.CROWN) * k), stack_mid_centre=R4((Fv + K.CROWN / 2) * k),
        outer_diameter=2 * K.HUB_R, stack_height_F_to_crown=K.CROWN, cap_side="outward (away from GH): the crown at F + 12.25",
        lower_member=STACK[j]["lower"], upper_member_on_cap_side=STACK[j]["upper"])

# ---- 4. straps (link 1, link 2, neck) ----------------------------------------------------------------------------------
SPEC = dict(link1=dict(u="J1", v="J2", w=float(P["width"]), t=float(P["t_link"])), link2=dict(u="J2", v="J3", w=float(P["width"]), t=float(P["t_link"])),
            neck=dict(u="J3", v=None, w=14.0, t=6.0))
END = K.HUB_R + 2.0 + float(P["end_extra"])
bar_dir0 = K.unit((FR.RH[0] @ K.unit(K.BAR0_H)))
straps, csv_rows, CL = {}, [], {}
NM = {"link1": "link 1", "link2": "link 2", "neck": "member 3"}
for n, s in SPEC.items():
    m = MEM[n]; ns, nc = m.grid; rho = PROF[n].reshape(ns, nc); X = PTS0[n].reshape(ns, nc, 3)
    u = AX[s["u"]]; v = AX[s["v"]] if s["v"] else bar_dir0
    ang = math.acos(float(np.clip(u @ v, -1, 1))); nrm = K.unit(np.cross(u, v)); e2 = K.unit(np.cross(nrm, u))
    th = np.linspace(0, 1, ns) * ang; Dd = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2      # the centre great circle
    cs = np.arange(-s["w"] / 2, s["w"] / 2 + 1e-6, 2.0); mid = np.argsort(np.abs(cs))[:2 if nc % 2 == 0 else 1]
    rc = rho[:, mid].mean(1)                                                                        # centre underside radius
    under = Dd * rc[:, None]; top = Dd * (rc + s["t"])[:, None]
    # densify to <= 2 mm (slerp the direction, linear radius between two model samples)
    dense = []
    for i in range(ns):
        dense.append((i, 0.0, Dd[i], rc[i], 1))
        if i < ns - 1:
            L = float(np.linalg.norm(under[i + 1] - under[i])); kk = max(0, int(math.ceil(L / 1.0)) - 1)
            for f in np.linspace(0, 1, kk + 2)[1:-1]:
                dd = K.unit(math.sin((1 - f) * ang / (ns - 1)) * Dd[i] + math.sin(f * ang / (ns - 1)) * Dd[i + 1]); dense.append((i, f, dd, (1 - f) * rc[i] + f * rc[i + 1], 0))
    sarc = 0.0; prev = None; rows = []
    for (i, f, dd, r, src) in dense:
        pu = dd * r
        if prev is not None: sarc += float(np.linalg.norm(pu - prev))
        prev = pu; a_from = math.degrees((i + f) * ang / (ns - 1))
        rows.append(dict(member=n, sample=round(i + f, 3), model_sample=src, angle_from_start_axis_deg=round(a_from, 4), arc_mm=round(sarc, 3),
                         under_x=round(pu[0], 4), under_y=round(pu[1], 4), under_z=round(pu[2], 4),
                         top_x=round(dd[0] * (r + s["t"]), 4), top_y=round(dd[1] * (r + s["t"]), 4), top_z=round(dd[2] * (r + s["t"]), 4),
                         radius_underside=round(r, 4), width=s["w"], thickness=s["t"]))
    csv_rows += rows; CL[n] = np.array([[r["under_x"], r["under_y"], r["under_z"]] for r in rows])
    spacing = np.linalg.norm(np.diff(CL[n], axis=0), axis=1)
    n_end = int(math.ceil((END if n != "neck" else K.HUB_R + 2.0) / 2.0)) + 1
    # where the centreline crosses each hub's O20 rim (lateral distance from the axis = 10 mm)
    lands = {}
    for side, jn in (("start", s["u"]), ("end", s["v"])):
        if jn is None: continue
        k = AX[jn]; lat = np.linalg.norm(under - (under @ k)[:, None] * k, axis=1); idx = range(ns) if side == "start" else range(ns - 1, -1, -1)
        prev_i = None
        for i in idx:
            if lat[i] >= K.HUB_R:
                if prev_i is None: break
                f = (K.HUB_R - lat[prev_i]) / (lat[i] - lat[prev_i]); pnt = under[prev_i] + f * (under[i] - under[prev_i])
                lands[side] = dict(joint=jn, rim_point_underside=R4(pnt), level_along_axis=round(float(pnt @ k), 3)); break
            prev_i = i
    holds = {}
    for side, sl in (("start", slice(0, n_end)), ("end", slice(ns - n_end, ns))):
        jn = s["u"] if side == "start" else s["v"]
        if jn is None: continue
        hn = {"J1": "hub1", "J2": "hub2", "J3": "hub3"}[jn]
        holds[side] = dict(joint=jn, n_samples=n_end, angle_deg=round(math.degrees((n_end - 1) * ang / (ns - 1)), 3),
                           underside_radius_min=round(float(rho[sl].min()), 3), underside_radius_max=round(float(rho[sl].max()), 3),
                           hub_F=hubs[jn]["F_mm"], role="upper (cap-side) member" if STACK[jn]["upper"].startswith(NM[n]) else "lower (skin-side) member")
    straps[n] = dict(
        kind="strap on the great circle between two directions from GH, underside fitted per sample (radius from GH varies)",
        from_axis=s["u"], to=(s["v"] or "BOTTOM landing direction (see bottom_interface)"), arc_deg=round(math.degrees(ang), 4),
        section_width_x_thickness_mm=[s["w"], s["t"]], thickness_direction="radially outward from GH (underside sample r -> top r + t)",
        n_along=ns, n_across=nc, across_offsets_mm_at_r70=R4(cs), centre_columns=[int(c) for c in mid],
        underside_radius_centre_min_max=[round(float(rc.min()), 3), round(float(rc.max()), 3)],
        underside_radius_all_min_max=[round(float(rho.min()), 3), round(float(rho.max()), 3)],
        centreline_points=len(rows), centreline_max_spacing_mm=round(float(spacing.max()), 3),
        model_sample_grid_underside=[R4(x) for x in X.reshape(-1, 3)],
        model_sample_grid_order="row-major: along index (start -> end) outer, across index (offset -w/2 -> +w/2) inner",
        end_holds=holds, hub_rim_crossings=lands, climb_limit_deg=m.climb_deg)

# ---- 5. joint ranges over the TAKEN poses (verifier bench) and the fit clips (kinematic) ------------------------------
if "poses" not in WEAR:                                                         # dev fallback only: the fit bench's take (never committed)
    L_ = B._kit_last; tk_ = [bool(M.SPM._taken(B, j)) for j in range(len(B.res))]
    WEAR["poses"] = dict(kind=list(B.kind), clip=list(B.clip), global_idx=[int(i) for i in B.idx], plane=[p["plane"] for p in B.poses],
                         elev=[p["elev"] for p in B.poses], axial=[p["axial"] for p in B.poses], taken=tk_, q=np.asarray(L_["chain"].q, float).tolist())
    print("WARNING: no wear poses - using the fit bench (dev only)")
Pw = WEAR["poses"]; qw = np.array(Pw["q"], float); taken = np.array(Pw["taken"]); kinds = np.array(Pw["kind"]); clips = np.array(Pw["clip"])
el = np.array(Pw["elev"]); pl = np.array(Pw["plane"]); gidx = np.array(Pw["global_idx"])


def rng(q, sel):
    """min / max of theta = SG * q (unwrapped around the rest value), and of theta - theta_rest"""
    if not sel.any(): return None
    t0 = SG * q_rest; d = wrap(SG * (q[sel] - q_rest)); out = dict(n=int(sel.sum()))
    for i in range(3):
        out[f"theta{i + 1}"] = [round(float(t0[i] + d[:, i].min()), 2), round(float(t0[i] + d[:, i].max()), 2)]
        out[f"dtheta{i + 1}_from_rest"] = [round(float(d[:, i].min()), 2), round(float(d[:, i].max()), 2)]
    return out


ranges = dict(verifier_bench_taken_workspace=rng(qw, taken & (kinds == "ws")), verifier_bench_taken_clip_frames=rng(qw, taken & (kinds == "clip")),
              verifier_bench_taken_all=rng(qw, taken))
fit_ids = [NAMES.index(c) for c in CB.FIT]
gclip = np.nonzero(np.isin(CID, fit_ids))[0]; Fc = frames_g(gclip); chc = M.build(B, Fc, P); okc = np.asarray(chc.ok, bool); qc = np.asarray(chc.q, float)
ranges["all_fit_clip_frames_kinematic"] = dict(rng(qc, okc), frames=int(len(gclip)), closes=int(okc.sum()),
                                               note="every frame of the 6 fit clips (held-out clips excluded), chain closure + 5 deg fold margin only, no skin check")
per_clip = {}
for c in sorted(set(clips[kinds == "clip"])):
    per_clip[c] = rng(qw, taken & (clips == c))
ranges["verifier_bench_taken_by_clip"] = per_clip

# ---- 6. fold window -> J2 hard stops ----------------------------------------------------------------------------------
a1, a2, mg = float(P["a1"]), float(P["a2"]), float(P["margin"])
th_lo, th_hi = abs(a1 - a2) + mg, min(a1 + a2, 360 - a1 - a2) - mg
sgn = 1.0 if q_rest[1] >= 0 else -1.0


def q2_of_th(t):
    c = (math.cos(math.radians(t)) - math.cos(math.radians(a1)) * math.cos(math.radians(a2))) / (math.sin(math.radians(a1)) * math.sin(math.radians(a2)))
    return sgn * math.degrees(math.acos(max(-1.0, min(1.0, c))))


# check the mapping on the bench: th from the axes vs th from q2
Fw = frames_g(gidx); chw = M.build(B, Fw, P); p1w = np.asarray(chw.joints["J1"]); p3w = np.asarray(chw.joints["J3"])
th_w = np.degrees(np.arccos(np.clip((K.unit(p1w) * K.unit(p3w)).sum(-1), -1, 1)))
c2 = np.cos(np.radians(a1)) * np.cos(np.radians(a2)) + np.sin(np.radians(a1)) * np.sin(np.radians(a2)) * np.cos(np.radians(qw[:, 1]))
th_from_q2 = np.degrees(np.arccos(np.clip(c2, -1, 1)))
okw = np.asarray(chw.ok, bool); map_err = float(np.abs(th_w - th_from_q2)[okw].max())
fold = dict(metric="th = angle between the J1 and J3 axes (deg); a pose is allowed only if th lies in [|a1 - a2| + 5, min(a1 + a2, 360 - a1 - a2) - 5]",
            window_th_deg=[round(th_lo, 4), round(th_hi, 4)], margin_deg=mg,
            q2_relation="cos th = cos a1 cos a2 + sin a1 sin a2 cos q2 (q2 = J2 rotation, 0 = fully folded th = |a1 - a2|, +-180 = fully stretched th = a1 + a2)",
            q2_at_folded_stop_deg=round(q2_of_th(th_lo), 3), q2_at_stretched_stop_deg=round(q2_of_th(th_hi), 3),
            q2_sign_on_this_branch=int(sgn), q2_rest_deg=round(float(q_rest[1]), 3), th_rest_deg=None, mapping_check_max_err_deg=round(map_err, 6),
            taken_th_min_max=[round(float(th_w[taken].min()), 3), round(float(th_w[taken].max()), 3)],
            min_margin_on_taken_deg=round(float(np.minimum(th_w[taken] - th_lo + mg, th_hi + mg - th_w[taken]).min()), 3),
            hard_stops="dowel in an arc slot between link 1 and link 2 (the two bodies J2 connects), engaging at the two q2 values above")
fold["th_rest_deg"] = round(math.degrees(math.acos(float(np.clip(AX["J1"] @ AX["J3"], -1, 1)))), 4)

# ---- 7. forward kinematics in the as-built frame + reproduction check -------------------------------------------------
BODY = {"link1": 1, "link2": 2, "neck": 3}


def fk(dq):
    """dq = model q - q_rest (deg); theta = SG * q (theta3 = -q3: the model's q3 is link 2 seen from the arm)"""
    dt = SG * np.asarray(dq, float)
    R1 = rot(AX["J1"], dt[0]); R2 = R1 @ rot(AX["J2"], dt[1]); R3 = R2 @ rot(AX["J3"], dt[2]); return {0: np.eye(3), 1: R1, 2: R2, 3: R3}


def cyl_dist(X, k, F, r=K.HUB_R, h=K.CROWN):
    a = X @ k; rad = np.linalg.norm(X - a[:, None] * k, axis=1)
    return np.sqrt(np.maximum(0, rad - r) ** 2 + np.maximum(0, np.maximum(F - a, a - F - h)) ** 2)


def hub_solid_pts(k, F, n=24):
    a, b = K.plane_frame(k[None])[0][0], K.plane_frame(k[None])[1][0]; t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = np.cos(t)[:, None] * a + np.sin(t)[:, None] * b
    return np.concatenate([F * k + K.HUB_R * ring, (F + K.CROWN) * k + K.HUB_R * ring, [F * k, (F + K.CROWN) * k]])


def pose_record(label, j):
    g = int(gidx[j]); dq = wrap(qw[j] - q_rest); R = fk(dq)
    rec = dict(label=label, bench_pose=dict(kind=str(kinds[j]), clip=str(clips[j]), plane_deg=round(float(pl[j]), 2), elevation_deg=round(float(el[j]), 2),
                                            axial_deg=round(float(Pw["axial"][j]), 2)), taken=bool(taken[j]),
               q_model_deg=R4(qw[j]), theta_deg=R4(SG * qw[j]), dtheta_from_rest_deg=R4(SG * dq), th_deg=round(float(th_w[j]), 3))
    rec["axes_as_built"] = {jn: R6(R[b] @ AX[jn]) for jn, b in (("J1", 0), ("J2", 1), ("J3", 2))}
    rec["hub_face_centres_as_built"] = {jn: R4(R[b] @ AX[jn] * hubs[jn]["F_mm"]) for jn, b in (("J1", 0), ("J2", 1), ("J3", 2))}
    rec["hub_crown_centres_as_built"] = {jn: R4(R[b] @ AX[jn] * hubs[jn]["crown"]) for jn, b in (("J1", 0), ("J2", 1), ("J3", 2))}
    # reproduction check: model metal at this pose vs the exported rest metal moved by FK
    ch = M.build(B, frames_g(g), P); pts = {m.name: K.member_points(m, PROF[m.name])[0] for m in ch.members}
    err = {}
    for n, b in BODY.items():
        Xm = to_asbuilt(g, pts[n]); Xe = (R[b] @ np.round(PTS0[n], 4).T).T; err[n] = float(np.linalg.norm(Xm - Xe, axis=1).max())
    for jn, hn, b in (("J1", "hub1", 0), ("J2", "hub2", 1), ("J3", "hub3", 2)):
        m = [x for x in ch.members if x.name == hn][0]; cm = to_asbuilt(g, (m.K[0] * PROF[hn][0])[None])[0]
        err[hn + "_face_centre"] = float(np.linalg.norm(cm - R[b] @ AX[jn] * hubs[jn]["F_mm"]))
    jax = {jn: float(np.linalg.norm(to_asbuilt(g, K.unit(np.asarray(ch.joints[jn])[0])[None])[0] - R[b] @ AX[jn])) for jn, b in (("J1", 0), ("J2", 1), ("J3", 2))}
    rec["reproduction_check_max_err_mm"] = {k: round(v, 6) for k, v in err.items()}; rec["axis_check_max_err"] = {k: round(v, 9) for k, v in jax.items()}
    return rec


tk = np.nonzero(taken)[0]
j_over = int(tk[np.argmax(el[tk])])
acr = tk[(el[tk] >= 40)]; j_across = int(acr[np.argmax(pl[acr])])
beh = tk[np.array(["back" in clips[i].lower() for i in tk])]
j_behind = int(beh[np.argmax(np.abs(np.array(Pw["axial"])[beh]) + 0 * el[beh])]) if len(beh) else int(tk[np.argmin(pl[tk])])
rest_rec = dict(label="rest: arm hanging at the side, plane 0, elevation 0, axial rotation 0 (workspace-envelope pose)", q_model_deg=R4(q_rest),
                theta_deg=R4(SG * q_rest), dtheta_from_rest_deg=[0.0, 0.0, 0.0],
                axes_as_built={j: hubs[j]["axis_unit_rest"] for j in hubs}, hub_crown_centres_as_built={j: hubs[j]["crown_centre"] for j in hubs},
                th_deg=fold["th_rest_deg"], hub_face_centres_as_built={j: hubs[j]["face_centre_F"] for j in hubs})
key_poses = [rest_rec, pose_record("overhead raise peak (highest-elevation taken pose)", j_over),
             pose_record("across the body (largest plane of elevation among taken poses with elevation >= 40)", j_across),
             pose_record("behind the back (Reach back pocket clip, taken frame with the largest |axial rotation|)", j_behind)]
# also the 3 reproduction poses (the key ones) -> worst error
rep_err = max(max(r["reproduction_check_max_err_mm"].values()) for r in key_poses[1:])

# ---- 8. swept clearances (as-built, base fixed): link 2 / hub 2 / hub 3 / member 3 vs hub 1, link 1 vs hub 3 / member 3
q2s = np.linspace(q2_of_th(th_lo), q2_of_th(th_hi), 121)
d3 = wrap(qw[taken, 2] - q_rest[2]); q3_span = np.linspace(d3.min(), d3.max(), 37)
sweep = []
for q2 in q2s:
    dq2 = float(SG[1] * wrap(q2 - q_rest[1])); R2 = rot(AX["J2"], dq2)
    L2 = np.concatenate([R2 @ PTS0["link2"].T, R2 @ (PTS0["link2"] * (1 + SPEC["link2"]["t"] / np.linalg.norm(PTS0["link2"], axis=1))[:, None]).T], 1).T
    H3 = (R2 @ hub_solid_pts(AX["J3"], hubs["J3"]["F_mm"]).T).T; H2 = hub_solid_pts(AX["J2"], hubs["J2"]["F_mm"])
    d_l2 = float(cyl_dist(L2, AX["J1"], hubs["J1"]["F_mm"]).min()); d_h3 = float(cyl_dist(H3, AX["J1"], hubs["J1"]["F_mm"]).min())
    nk_min = np.inf
    for dq3 in q3_span:
        R3 = R2 @ rot(AX["J3"], float(SG[2] * dq3)); NK = np.concatenate([R3 @ PTS0["neck"].T, R3 @ (PTS0["neck"] * (1 + 6.0 / np.linalg.norm(PTS0["neck"], axis=1))[:, None]).T], 1).T
        nk_min = min(nk_min, float(cyl_dist(NK, AX["J1"], hubs["J1"]["F_mm"]).min()))
    L1 = np.concatenate([PTS0["link1"], PTS0["link1"] * (1 + 3.0 / np.linalg.norm(PTS0["link1"], axis=1))[:, None]])
    d_l1h3 = float(cyl_dist(L1, R2 @ AX["J3"], hubs["J3"]["F_mm"]).min())
    sweep.append(dict(q2=round(float(q2), 3), th=round(math.degrees(math.acos(float(np.clip(AX["J1"] @ (R2 @ AX["J3"]), -1, 1)))), 3),
                      link2_to_hub1=round(d_l2, 2), hub3_to_hub1=round(d_h3, 2), member3_to_hub1_over_q3=round(nk_min, 2), link1_to_hub3=round(d_l1h3, 2)))
th_tk_min = float(th_w[taken].min()); q2_tk = q2_of_th(th_tk_min)
fine = []
for q2 in np.linspace(q2_of_th(th_lo), q2_of_th(th_lo) + sgn * 30.0, 301):
    R2 = rot(AX["J2"], float(SG[1] * wrap(q2 - q_rest[1])))
    L2 = np.concatenate([R2 @ PTS0["link2"].T, R2 @ (PTS0["link2"] * (1 + 3.0 / np.linalg.norm(PTS0["link2"], axis=1))[:, None]).T], 1).T
    fine.append((float(q2), float(cyl_dist(L2, AX["J1"], hubs["J1"]["F_mm"]).min())))
q2_1mm = next((q for q, d in fine if d >= 1.0), None)
th_1mm = math.degrees(math.acos(math.cos(math.radians(a1)) * math.cos(math.radians(a2)) + math.sin(math.radians(a1)) * math.sin(math.radians(a2)) * math.cos(math.radians(q2_1mm)))) if q2_1mm is not None else None
link2_hub1_at_taken_min = dict(th=round(th_tk_min, 3), q2=round(q2_tk, 3), link2_to_hub1=round(min(d for q, d in fine if abs(q - q2_tk) <= 0.06) if any(abs(q - q2_tk) <= 0.06 for q, d in fine) else float("nan"), 2))
sw = dict(method="base held fixed; link 2 / hub 3 rotated about J2 from rest by q2 - q2_rest over the whole fold window (121 steps); member 3 also "
                 "rotated about J3 over the taken q3 span (37 steps); distance = metal sample points (underside and top faces, 2 mm grid) to the "
                 "O20 hub cylinder (r 10, F .. F + 12.25) of the other joint, mm (sample spacing <= 2 mm: true distance may be up to ~1 mm less)",
          at_folded_stop=sweep[0], at_stretched_stop=sweep[-1],
          minimum_over_window={k: min(r[k] for r in sweep) for k in ("link2_to_hub1", "hub3_to_hub1", "member3_to_hub1_over_q3", "link1_to_hub3")},
          q2_at_minimum={k: min(sweep, key=lambda r: r[k])["q2"] for k in ("link2_to_hub1", "hub3_to_hub1", "member3_to_hub1_over_q3", "link1_to_hub3")},
          table_every_10th=sweep[::10], link2_to_hub1_at_smallest_taken_th=link2_hub1_at_taken_min,
          q2_where_link2_clears_hub1_by_1mm=q2_1mm, th_where_link2_clears_hub1_by_1mm=None if th_1mm is None else round(th_1mm, 3),
          note_fold="near the folded stop link 2 swings past hub 1: the 1 mm part-part rule (K6) holds only for q2 at or beyond the value above")

# ---- 9. BOTTOM interface (the kit's K7 target, in the humerus frame) ----------------------------------------------------
neck = MEM["neck"]; ns_n, nc_n = neck.grid; rn = PROF["neck"].reshape(ns_n, nc_n)
land = PTS0["neck"].reshape(ns_n, nc_n, 3)[-1]
RHr = FR.RH[0]
bottom = dict(
    model_rule="K7: member 3's neck (14 wide x 6 thick Ti strap, underside fitted) runs on the great circle from the J3 axis to the direction "
               "of BOTTOM's bar start point; it is RIGID on BOTTOM (member 3 = hub-3 cap plate + neck + BOTTOM move together with the upper arm)",
    humerus_frame="body_pose humerus frame H (rotates with the upper arm, origin GH): at rest H_x, H_y, H_z map to the as-built directions given here",
    H_axes_at_rest_as_built=dict(Hx=R6(RHr[:, 0]), Hy=R6(RHr[:, 1]), Hz=R6(RHr[:, 2])),
    bar_outward_normal_WB_in_H=R6(K.WB), bar_down_the_arm_DB_in_H=R6(K.DB),
    bar_start_point_in_H_mm=R4(K.BAR0_H), bar_start_point_rule="67.5 mm out along WB + 40.0 mm down along DB from GH (H frame)",
    bar_start_point_as_built_rest=R4(RHr @ K.BAR0_H), landing_direction_as_built_rest=R6(bar_dir0),
    neck_end_row_underside_as_built_rest=[R4(x) for x in land], neck_end_underside_radius_min_max=[round(float(rn[-1].min()), 3), round(float(rn[-1].max()), 3)],
    neck_end_centre_underside_as_built_rest=R4(bar_dir0 * float(rn[-1][[3, 4]].mean())),
    bar_start_point_distance_from_GH=round(float(np.linalg.norm(K.BAR0_H)), 3),
    neck_end_above_bar_start_point_mm=round(float(rn[-1][[3, 4]].mean() - np.linalg.norm(K.BAR0_H)), 3),
    neck_end_gap_note="the model's neck end sits on the bar-start DIRECTION at its own fitted underside radius, i.e. this far further out from GH "
                      "than the K7 bar start point: the real part must drop from the neck end to BOTTOM's mating face (the repo's CAD does it "
                      "with a bend into BOTTOM's channel)",
    note="the model ends the neck at that direction at its fitted underside radius; the repo's L2 CAD (user style) fuses the arm-end strap into "
         "BOTTOM's channel (one 5-axis part, BOTTOM cut) or holds it by 2x / 4x M3 countersunk screws through BOTTOM's web; BOTTOM is the user's part "
         "and is not designed here")

# ---- 10. self-checks ----------------------------------------------------------------------------------------------------
A = np.stack([AX[j] for j in ("J1", "J2", "J3")]); Cn = np.stack([AX[j] * hubs[j]["F_mm"] for j in ("J1", "J2", "J3")])
M3 = sum(np.eye(3) - np.outer(a, a) for a in A); bvec_ = sum((np.eye(3) - np.outer(a, a)) @ c for a, c in zip(A, Cn))
meet = np.linalg.solve(M3, bvec_)
ends = {}
for n, s in SPEC.items():
    for side, jn, pt in (("start", s["u"], CL[n][0]), ("end", s["v"], CL[n][-1])):
        if jn is None: continue
        k = AX[jn]; ends[f"{n}_{side}_{jn}"] = dict(off_axis_mm=round(float(np.linalg.norm(pt - (pt @ k) * k)), 9), level=round(float(pt @ k), 3),
                                                     hub_F=hubs[jn]["F_mm"], hub_F_plus_dz_rule=round(hubs[jn]["F_mm"] + (K.STACK if STACK[jn]["upper"].startswith(NM[n]) else 0.0), 3))
ends["neck_end_landing"] = dict(off_landing_direction_mm=round(float(np.linalg.norm(CL["neck"][-1] - (CL["neck"][-1] @ bar_dir0) * bar_dir0)), 9))
Ae = np.stack([np.array(hubs[j]["axis_unit_rest"]) for j in ("J1", "J2", "J3")]); Ce = np.stack([np.array(hubs[j]["face_centre_F"]) for j in ("J1", "J2", "J3")])
off_e = [float(np.linalg.norm(c - (c @ K.unit(a)) * K.unit(a))) for a, c in zip(Ae, Ce)]
checks = dict(axes_meet_at=R6(meet), axes_meet_distance_from_GH_mm=float(np.linalg.norm(meet)), axes_meet_ok=bool(np.linalg.norm(meet) < 1e-6),
              exported_hub_centres_off_GH_axis_lines_mm=[float(x) for x in off_e], exported_axes_meet_ok=bool(max(off_e) < 1e-6),
              centreline_ends_on_hub_axes=ends, centreline_ends_ok=bool(all(v.get("off_axis_mm", v.get("off_landing_direction_mm", 0)) < 1e-3 for v in ends.values())),
              reproduction_max_err_mm=round(rep_err, 6), reproduction_ok=bool(rep_err <= 0.01),
              reproduction_poses=[r["label"] for r in key_poses[1:]],
              profile_sha256=DIG, fit_numbers=WEAR["fit"], wear_numbers=WEAR.get("wear"))

GEO = dict(
    design="zc-frontier-3r (zero-complexity spherical 3R: three active revolute joints whose axes meet at the glenohumeral centre GH)",
    units="mm, degrees",
    frame=dict(name="as-built frame = the model's thorax frame at the rest pose", origin="GH (centre of the right glenohumeral joint)",
               x="anterior (forward)", y="superior (up)", z="lateral to the right (away from the body's midline, right shoulder)",
               handedness="right-handed (x cross y = z)",
               model_definition="the bench's thorax frame (body_pose): x anterior, y up, z right, origin = right GH centre; the scapula frame S "
                                "(J1's base) and the humerus frame H rotate about GH per pose; 'as built' = the base (scapula) held at its rest "
                                "attitude, so every key pose below is given relative to the base",
               base_attitude_at_rest_RS=[R6(r) for r in RS0], base_attitude_note="scapula-frame direction u -> as-built RS @ u"),
    rest_pose=dict(definition="arm hanging at the side: plane of elevation 0, elevation 0, axial rotation 0 (elbow 90, irrelevant to the shoulder chain)",
                   q_model_deg=R4(q_rest), theta_deg=R4(np.array([1, 1, -1]) * q_rest)),
    params=dict(P, note="verified configuration (row docs/concepts/rows/zc-frontier-3r.json best_params; skeptic harness frozen fit60 -> 33.51)"),
    joint_angle_definitions=dict(
        theta="joint angles used here: theta = rotation of the DISTAL body relative to the PROXIMAL body, right-hand about the axis unit "
              "given (base -> link 1 about J1, link 1 -> link 2 about J2, link 2 -> member 3 about J3); theta1 = q1, theta2 = q2, theta3 = -q3 "
              "(model q below)",
        q1="J1: rotation of link 1 about the J1 axis (right-hand rule about the axis unit below), measured from the scapula's anterior direction to the J2 axis, both projected on the plane normal to J1",
        q2="J2: rotation of link 2 relative to link 1 about the J2 axis, from the J1 axis to the J3 axis (dihedral angle; 0 = folded)",
        q3="J3: rotation of member 3 (the arm) relative to link 2 about the J3 axis, from the humerus down-the-arm direction to the J2 axis",
        fk="as-built forward kinematics (base fixed): R1 = Rot(J1_rest, theta1 - theta1_rest); R2 = R1 Rot(J2_rest, theta2 - theta2_rest); R3 = R2 Rot(J3_rest, theta3 - theta3_rest); "
           "link 1 moves by R1, link 2 + hub 3 by R2, member 3 (and the upper arm) by R3; Rot = right-hand rotation about the unit axis"),
    arcs=dict(a1_deg=a1, a1_meaning="fixed angle between the J1 and J2 axes = link 1's arc on the sphere about GH",
              a2_deg=a2, a2_meaning="fixed angle between the J2 and J3 axes = link 2's arc", sigma=int(P["sigma"]),
              sigma_meaning="closure branch: sign of J2 . (J1 x J3) - which of the two J2 axes that satisfy both arcs the chain uses (kept for the whole motion)",
              J1_in_scapula_frame=dict(az=P["az"], el=P["el"], unit=R6(K.bvec(P["az"], P["el"])), rule="bvec(az, el) = (-cos el cos az, sin el, cos el sin az): az 0 posterior, 90 lateral"),
              J3_in_humerus_frame=dict(wd=P["wd"], wa=P["wa"], unit_band_HG=R6(K.wdir(P["wd"], P["wa"])), rule="wdir(d, a) = (sin d sin a, -cos d, sin d cos a): d from the down-the-arm axis, a 0 lateral, +90 anterior")),
    hubs=dict(hub_stack=dict(type="O20 v5 hub: preloaded MR117-2RS pair (7 x 11 x 3), threaded cap", outer_diameter=20.0,
                             levels_from_F_mm=dict(F_lower_plate_skin_face=0.0, lower_plate_seat=3.0, upper_member_underside=3.15, crown=12.25),
                             model_envelope="a solid disc O20 from F to F + 12.25 on the joint axis (all stack hardware and both members' plates live inside it)"),
              **hubs, stack_order=dict(inv2=INV2, inv3=INV3,
                                       meaning="inv3 = 1: at J3 link 2 is the LOWER plate (skin side, F .. F+3) and member 3 (the arm-end cap plate + neck) "
                                               "is on the cap side (from F + 3.15) and bridges OVER link 2 (>= 1 mm above link 2's top wherever they overlap); "
                                               "inv2 = 0: at J2 link 1 is the lower plate and link 2 the upper; at J1 the base is the lower plate, link 1 the upper")),
    links=straps, link_metal_note="the metal is a 12 x 3 strap whose UNDERSIDE follows the model's per-sample radius from GH (not a constant level); "
                                  "thickness 3 radially outward; its ends are held at >= the hub's F (lower member) or F + 3.15 (upper member) over the end hold, "
                                  "and climb <= 60 deg between samples",
    fold=fold, joint_ranges=ranges, key_poses=key_poses, swept_clearances=sw, bottom_interface=bottom, checks=checks,
    provenance=dict(model="docs/concepts/models/zc-frontier-3r.py on tools/concept_kit.py", scripts="docs/cad_context/zc-frontier-3r/scripts/",
                    protocol="fit Bench(60,160) fast (frozen) -> worn Bench(110,360) exact = the verifier protocol, 33.51",
                    profile_sha256=DIG))
json.dump(GEO, open(os.path.join(OUT, "geometry.json"), "w"), indent=1, default=float)
with open(os.path.join(OUT, "link_centrelines.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0])); w.writeheader(); w.writerows(csv_rows)
print(json.dumps(dict(checks={k: v for k, v in checks.items() if k not in ("centreline_ends_on_hub_axes", "fit_numbers", "wear_numbers")},
                      hubs={j: (h["F_mm"], h["axis_unit_rest"]) for j, h in hubs.items()}, q_rest=R4(q_rest), fold=fold, ranges=ranges,
                      sweep=sw["minimum_over_window"], spacing={n: s["centreline_max_spacing_mm"] for n, s in straps.items()}), default=float, indent=1))

# ---- 11. three orthographic views ------------------------------------------------------------------------------------
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt   # noqa: E402
COL = dict(link1="#2a78d6", link2="#eb6834", neck="#1baf7a", hub="#6b6a63", axis="#3d3d3a")
LBL = dict(link1="link 1 (J1-J2)", link2="link 2 (J2-J3)", neck="member 3 neck (to BOTTOM)")
views = [("view from anterior (+x), looking -x", 2, 1, True, "z  (lateral +, axis reversed: true front view)", "y  (superior +)"),
         ("view from lateral (+z), looking -z", 0, 1, False, "x  (anterior +)", "y  (superior +)"),
         ("view from above (+y), looking -y", 2, 0, False, "z  (lateral +)", "x  (anterior +)")]
fig, axs = plt.subplots(1, 3, figsize=(16.5, 6.2), facecolor="white")
for ax, (title, i, j, inv, xl, yl) in zip(axs, views):
    for jn in ("J1", "J2", "J3"):
        k = np.array(hubs[jn]["axis_unit_rest"]); L = hubs[jn]["crown"] + 18
        ax.plot([0, L * k[i]], [0, L * k[j]], ls=(0, (4, 3)), lw=1.0, color=COL["axis"], zorder=1)
        ax.annotate(jn, (L * k[i], L * k[j]), fontsize=10, color="#1a1a19", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
        Hs = hub_solid_pts(k, hubs[jn]["F_mm"], 72); ring0, ring1 = Hs[:72], Hs[72:144]
        from scipy.spatial import ConvexHull
        pts2 = np.concatenate([ring0, ring1])[:, [i, j]]; hull = ConvexHull(pts2)
        ax.fill(pts2[hull.vertices, 0], pts2[hull.vertices, 1], color=COL["hub"], alpha=0.28, lw=0, zorder=2)
        ax.plot(ring0[:, i], ring0[:, j], color=COL["hub"], lw=1.0, zorder=3)          # lower plate face F (skin side)
        ax.plot(ring1[:, i], ring1[:, j], color=COL["hub"], lw=2.0, zorder=3)          # crown (cap side)
        c0, c1 = hubs[jn]["F_mm"] * k, hubs[jn]["crown"] * k
        ax.plot([c0[i]], [c0[j]], "o", ms=4, color=COL["hub"], zorder=4)
    for n in ("link1", "link2", "neck"):
        U = CL[n]; t_ = SPEC[n]["t"]; T = U * (1 + t_ / np.linalg.norm(U, axis=1))[:, None]
        ax.plot(U[:, i], U[:, j], color=COL[n], lw=2.0, label=LBL[n] + " underside", zorder=5)
        ax.plot(T[:, i], T[:, j], color=COL[n], lw=1.0, ls=(0, (2, 2)), zorder=5)
    bp = np.array(bottom["bar_start_point_as_built_rest"]); ax.plot([bp[i]], [bp[j]], marker="s", ms=7, mfc="white", mec="#1a1a19", zorder=6)
    ax.plot([0], [0], marker="+", ms=12, mew=2, color="#1a1a19", zorder=6); ax.annotate("GH", (0, 0), xytext=(6, -12), textcoords="offset points", fontsize=9)
    ax.set_title(title, fontsize=11, color="#1a1a19"); ax.set_xlabel(xl, fontsize=9, color="#3d3d3a"); ax.set_ylabel(yl, fontsize=9, color="#3d3d3a")
    ax.set_aspect("equal"); ax.grid(True, color="#e4e3dd", lw=0.6); ax.tick_params(labelsize=8, colors="#3d3d3a")
    for sp in ax.spines.values(): sp.set_color("#c3c2b7")
    if inv: ax.invert_xaxis()
h, l = axs[1].get_legend_handles_labels()
from matplotlib.lines import Line2D                                                   # noqa: E402
h += [Line2D([], [], color=COL["hub"], lw=6, alpha=0.4), Line2D([], [], ls=(0, (4, 3)), color=COL["axis"]),
      Line2D([], [], marker="s", ls="", mfc="white", mec="#1a1a19"), Line2D([], [], color="#6b6a63", lw=1, ls=(0, (2, 2)))]
l += ["O20 hub stack: thin ring = lower plate face F (skin side), thick ring = crown F + 12.25 (cap side)", "joint axis through GH",
      "BOTTOM bar start point (neck target, K7)", "strap top face (dashed, colour of its member)"]
fig.legend(h, l, loc="lower center", ncol=4, fontsize=8.5, frameon=False)
fig.suptitle("zc-frontier-3r skeleton at rest (arm hanging), as-built frame: origin GH, x anterior, y superior, z lateral (right), mm - no body shown",
             fontsize=11.5, color="#1a1a19")
fig.tight_layout(rect=(0, 0.08, 1, 0.95)); fig.savefig(os.path.join(OUT, "skeleton_views.png"), dpi=150); print("png written")
