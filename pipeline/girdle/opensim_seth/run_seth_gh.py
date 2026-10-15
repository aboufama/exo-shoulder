"""Tasks 2, 3, 5: drive the Seth 2016 model with published mean shoulder-rhythm angles (Ludewig 2009, ludewig2009.py) and
record the GH centre, AC joint, clavicle tip and acromial angle in the thorax per plane and elevation. Writes gh_seth.json.

Per plane (abduction 0, scaption 40, flexion 90) and humerothoracic elevation 0..150 deg (10 deg steps; below 15 and
beyond 132-138 deg = extrapolated angle curves, flagged):
  1. girdle: least squares over the 6 girdle coordinates (clav_prot, clav_elev, 4 scapulothoracic) of the 5 ISB angle
     errors (clavicle retraction / elevation, scapula IR / UR / PT; equal weights 1/deg) with the AC point constraint
     (penalty 100/mm, then OpenSim's assembler closes it exactly). The girdle has 6 - 3 = 3 DOF, so 5 angles cannot all be
     met: the residuals are reported.
  2. humerus: shoulder_elv and plane_of_elev (axial_rot = 0) so that the humerus long axis has the target ISB
     plane / elevation (no effect on the GH centre, which is fixed in the scapula; reported for completeness).
  3. GH = humerus origin, in the ISB thorax frame built from the model's IJ/C7/PX/T8 markers, minus the plane's 0 deg
     posture (arm hanging; the teammate's chain uses the same per-plane anchor).
Variants: 'primary' = equal weights, girdle coordinate ranges relaxed to +-90 deg (the distributed +-45 deg clamp stops
scapula_upward_rot at ~90 deg elevation); 'clamped' = ranges as distributed; 'w_clav' / 'w_scap' = clavicle or scapula
angles weighted 10x (fit-choice sensitivity). Sensitivity: each published angle +-1 SD (ludewig2009.SD) at the elevated
posture, rest fixed; and the same offset applied to rest and elevated posture.
Run: .cache/opensim-venv/bin/python pipeline/girdle/opensim_seth/run_seth_gh.py      (single process, ~1 min)
"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opensim as osim
from seth_model import Seth, GIRDLE, GHC, ANG, HERE, MODEL, REPO
import ludewig2009 as LW

PLANES = ["abduction", "scaption", "flexion"]
ELEV = list(range(0, 151, 10))
SENS_ELEV = [30, 60, 90, 120, 150]
D = math.pi / 180
SM = {"clamped": Seth(), "relaxed": Seth(relax_deg=90)}             # model as distributed / girdle ranges +-90 deg, unclamped
S = SM["relaxed"]
W = {"primary": np.ones(5), "clamped": np.ones(5), "w_clav": np.array([10, 10, 1, 1, 1.0]), "w_scap": np.array([1, 1, 10, 10, 10.0])}


def set_ranges(variant):
    global S
    S = SM["clamped"] if variant == "clamped" else SM["relaxed"]


def reset():
    S.s = S.m.initSystem()


def tvec(a): return np.array([a[k] for k in ANG])


def record(r, h=None):
    q = r["pts"]; iso = lambda n: S.to_isb(q[n])
    out = dict(gh=iso("GH"), ac=iso("ACj_c"), clav_tip=iso("acc"), aa=iso("aa"), sc=iso("SC"), ang=r["ang"], res=r["res"], x=r["x"],
               ac_err=r["ac_err"], qerr=r["qerr"], over45=[GIRDLE[i] for i in range(6) if abs(r["x"][i]) > 45 * D + 1e-6],
               at_bound=[GIRDLE[i] for i in range(6) if min(r["x"][i] - S.lo[i], S.hi[i] - r["x"][i]) < 1e-4])
    if h: out.update(hum=h["ang"], ghq=h["x"], hum_dir_err=h["dir_err_deg"])
    return out


def sweep(variant, planes=PLANES, elev=ELEV):
    set_ranges(variant); res = {}
    for p in planes:
        reset(); x0, g0 = None, None; rows = []
        for th in elev:
            a, flag = LW.angles(p, th)
            r = S.fit_girdle(tvec(a), w=W[variant], q0=x0); x0 = r["x"]
            h = S.fit_humerus(LW.PLANE[p], th, q0=g0); g0 = h["x"][:2]
            rec = record(r, h); rec.update(elev=th, flag=flag, target=tvec(a)); rows.append(rec)
        res[p] = rows
    return res


t0 = time.time()
RES = {v: sweep(v) for v in ["primary", "clamped", "w_clav", "w_scap"]}
print(f"sweeps done {time.time() - t0:.1f} s")

# common rest = Ludewig Table I relaxed standing (alternative anchor)
set_ranges("primary"); reset()
rest = record(S.fit_girdle(tvec(LW.REST)))

# ---------------------------------------------------------------- sensitivity (primary settings)
set_ranges("primary"); SENS = {}
for p in PLANES:
    nom = {r["elev"]: r for r in RES["primary"][p]}; SENS[p] = {}
    for th in SENS_ELEV:
        a, _ = LW.angles(p, th); t = tvec(a); g_nom = nom[th]["gh"]; x_nom = nom[th]["x"]; d = {}
        for i, k in enumerate(ANG):
            dd = {}
            for sg in (+1, -1):
                t2 = t.copy(); t2[i] += sg * LW.SD[k]
                r = S.fit_girdle(t2, q0=x_nom); dd[sg] = (S.to_isb(r["pts"]["GH"]) - g_nom, r["ang"] - nom[th]["ang"])
            d[k] = dict(sd=LW.SD[k], d_plus=dd[1][0].tolist(), d_minus=dd[-1][0].tolist(), mm_per_deg=((dd[1][0] - dd[-1][0]) / (2 * LW.SD[k])).tolist(),
                        achieved_change_plus_deg=dd[1][1].tolist(), achieved_change_minus_deg=dd[-1][1].tolist())
        big = np.array([np.maximum(np.abs(d[k]["d_plus"]), np.abs(d[k]["d_minus"])) for k in ANG])
        SENS[p][th] = dict(per_angle=d, rss_mm=np.sqrt((big ** 2).sum(0)).tolist(), rss_norm_mm=float(np.sqrt((big ** 2).sum())),
                           box_sum_mm=big.sum(0).tolist())
# offset (same +SD on the rest and the elevated posture): how much of an inter-subject offset survives the subtraction
OFFS = {}
for p in PLANES:
    nom = {r["elev"]: r for r in RES["primary"][p]}; OFFS[p] = {}
    for th in [90, 120]:
        a, _ = LW.angles(p, th); a0, _ = LW.angles(p, 0); OFFS[p][th] = {}
        for i, k in enumerate(ANG):
            t, t0_ = tvec(a), tvec(a0); t[i] += LW.SD[k]; t0_[i] += LW.SD[k]
            r0 = S.fit_girdle(t0_, q0=nom[0]["x"]); g0 = S.to_isb(r0["pts"]["GH"])
            r1 = S.fit_girdle(t, q0=nom[th]["x"]); g1 = S.to_isb(r1["pts"]["GH"])
            OFFS[p][th][k] = ((g1 - g0) - (nom[th]["gh"] - nom[0]["gh"])).tolist()
print(f"sensitivity done {time.time() - t0:.1f} s")


# ---------------------------------------------------------------- output
def disp(rows, key="gh", ref=None):
    r0 = rows[0][key] if ref is None else ref
    return [(r[key] - r0).round(3).tolist() for r in rows]


def grid(v, key="gh"): return [disp(RES[v][p], key) for p in PLANES]


facts = json.load(open(os.path.join(HERE, "model_facts.json"))) if os.path.exists(os.path.join(HERE, "model_facts.json")) else {}
RT = S.RT
table = []
for p in PLANES:
    rows = RES["primary"][p]; rc = RES["clamped"][p]; g0 = rows[0]["gh"]
    for j, r in enumerate(rows):
        d = r["gh"] - g0
        table.append(dict(plane=LW.PLANE[p], plane_name=p, elev=r["elev"], extrapolated=r["flag"],
                          gh_mm=d.round(2).tolist(), gh_mm_clamped=(rc[j]["gh"] - rc[0]["gh"]).round(2).tolist(),
                          gh_mm_model_thorax=(RT @ d).round(2).tolist(), gh_mm_rel_tableI_rest=(r["gh"] - rest["gh"]).round(2).tolist(),
                          ac_mm=(r["ac"] - rows[0]["ac"]).round(2).tolist(), clav_tip_mm=(r["clav_tip"] - rows[0]["clav_tip"]).round(2).tolist(),
                          aa_mm=(r["aa"] - rows[0]["aa"]).round(2).tolist(),
                          gh_abs_isb_mm=r["gh"].round(3).tolist(), ac_abs_isb_mm=r["ac"].round(3).tolist(),
                          target_deg=dict(zip(ANG, np.round(r["target"], 3).tolist())), achieved_deg=dict(zip(ANG, np.round(r["ang"], 4).tolist())),
                          residual_deg=dict(zip(ANG, np.round(r["res"], 2).tolist())), residual_rms_deg=round(float(np.sqrt((r["res"] ** 2).mean())), 2),
                          residual_deg_clamped=dict(zip(ANG, np.round(rc[j]["res"], 2).tolist())), ac_constraint_err_mm_clamped=rc[j]["ac_err"],
                          girdle_coords_deg=dict(zip(GIRDLE, np.round(np.degrees(r["x"]), 2).tolist())), coords_beyond_45deg=r["over45"],
                          clamped_at_bound=rc[j]["at_bound"],
                          gh_coords_deg=dict(zip(GHC, np.round(np.degrees(r["ghq"]), 2).tolist())),
                          humerus_isb_deg=dict(zip(["plane", "elev", "axial"], np.round(r["hum"], 2).tolist())), humerus_dir_err_deg=round(r["hum_dir_err"], 4),
                          ac_constraint_err_mm=r["ac_err"], qerr_max=r["qerr"]))

out = dict(
    meta=dict(
        what="GH-centre displacement vs the thorax during arm elevation: OpenSim 4.6, Seth et al. 2016 scapulothoracic shoulder model "
             "(generic, unscaled) driven by published mean shoulder-rhythm angles (Ludewig et al. 2009, means read off Fig. 5)",
        frame="ISB thorax of the Seth model (Wu 2005 from its IJ/C7/PX/T8 markers): mm, x anterior, y superior, z lateral (right). "
              "gh_mm_model_thorax = the same vector in the model's thorax body frame (ISB frame rotated +7.86 deg about z).",
        anchor="displacement from the plane's 0 deg (arm hanging) posture, whose angles extrapolate the 15-30 deg slope (as the teammate's chain); "
               "gh_mm_rel_tableI_rest = from Ludewig Table I relaxed standing (one rest for all planes)",
        planes="ISB plane of elevation: 0 abduction, 40 scaption, 90 flexion",
        primary="equal angle weights, girdle coordinate ranges relaxed to +-90 deg; gh_mm_clamped = ranges as distributed (+-45 deg)",
        extrapolated="'below_15': angle curves extrapolated below 15 deg; 'above_end_rom': beyond the last data point (abduction 135, scaption 138, flexion 132 deg)",
        model=os.path.relpath(MODEL, REPO), opensim=osim.GetVersion(),
        model_citation="Seth A, Matias R, Veloso AP, Delp SL (2016) A biomechanical model of the scapulothoracic joint to accurately capture scapular "
                       "kinematics during shoulder movements. PLoS One 11(1):e0141028. doi:10.1371/journal.pone.0141028",
        model_licence="CC BY-NC-SA 3.0 (Stanford Digital Repository purl.stanford.edu/br087nj9017); accepted by the user",
        data_restriction="no bone-pin subject data used (Ludewig lab data, IK .mot files and subject models were deleted and not used); "
                         "only the generic model and published summary means",
        angle_source="Ludewig PM et al. (2009) J Bone Joint Surg Am 91(2):378-389, Fig. 5-A/5-C means (read off the figure, +-1 deg) and Table I; "
                     "SDs for sensitivity: McClure PW et al. (2001) J Shoulder Elbow Surg 10:269-277 (scapula), 5 deg where none given (clavicle)",
        scripts=["seth_model.py", "ludewig2009.py", "model_facts.py", "run_seth_gh.py", "compare.py", "seth_law.py"]),
    planes_deg=[LW.PLANE[p] for p in PLANES], plane_names=PLANES, elev_deg=ELEV,
    gh_mm=grid("primary"),
    extrapolated=[[r["flag"] for r in RES["primary"][p]] for p in PLANES],
    table=table,
    variants={v: dict(gh_mm=grid(v), ac_mm=grid(v, "ac"),
                      residual_deg=[[np.round(r["res"], 2).tolist() for r in RES[v][p]] for p in PLANES],
                      weights=W[v].tolist()) for v in RES},
    rest_tableI=dict(target_deg=LW.REST, achieved_deg=dict(zip(ANG, np.round(rest["ang"], 2).tolist())), residual_deg=dict(zip(ANG, np.round(rest["res"], 2).tolist())),
                     gh_abs_isb_mm=rest["gh"].round(3).tolist(), ac_abs_isb_mm=rest["ac"].round(3).tolist(), sc_abs_isb_mm=rest["sc"].round(3).tolist(),
                     clav_tip_abs_isb_mm=rest["clav_tip"].round(3).tolist()),
    sensitivity=dict(method="each Ludewig mean angle +-1 SD at the elevated posture (rest fixed), refit (primary settings); d = GH(perturbed) - GH(nominal), mm, ISB thorax",
                     sd_deg=LW.SD, sd_source=LW.SD_SOURCE, by_plane=SENS,
                     offset_same_on_rest_and_elevated_mm=OFFS),
    model_geometry=dict(clavicle_SC_ACjoint_mm=float(np.linalg.norm(RES["primary"]["scaption"][0]["ac"] - RES["primary"]["scaption"][0]["sc"])),
                        AC_to_GH_isb_at_0deg_mm={p: (RES["primary"][p][0]["gh"] - RES["primary"][p][0]["ac"]).round(2).tolist() for p in PLANES},
                        SC_to_GH_isb_at_0deg_mm={p: (RES["primary"][p][0]["gh"] - RES["primary"][p][0]["sc"]).round(2).tolist() for p in PLANES},
                        SC_isb_mm=RES["primary"]["scaption"][0]["sc"].round(2).tolist(),
                        isb_thorax_axes_in_model_thorax=RT.round(6).tolist()),
)
json.dump(out, open(os.path.join(HERE, "gh_seth.json"), "w"), indent=1)
print("wrote", os.path.join(HERE, "gh_seth.json"), f"{time.time() - t0:.1f} s")

np.set_printoptions(precision=1, suppress=True)
for v in RES:
    print(f"\n== {v}: GH displacement (ant, sup, lat) mm and RMS angle residual (deg)")
    for p in PLANES:
        rows = RES[v][p]
        print(f"  {p:9s} " + "  ".join(f"{r['elev']:3d}:{np.array2string(r['gh'] - rows[0]['gh'], precision=1, suppress_small=True)} r{np.sqrt((r['res'] ** 2).mean()):.1f}"
                                         for r in rows if r["elev"] in (30, 60, 90, 120, 150)))
