"""P0 base-mount physics (R10) on the body rig (avg/body_pose.py), every frame of the 8 design clips.

The pipeline holds the exo's base fixed in the scapula frame; physically it bolts to a thorax back plate. On the rig's
own girdle model (segs(): GH lift, scap(): scapula rotation about the GH centre) this measures:
  1. human:   GH centre and scapula (= the pipeline's base frame) relative to the thorax, per clip
  2. base:    how far the reference design's base part moves between the two models; its contact / gap with the exact
              posed skin (judge/sdist.py) when it is thorax-fixed
  3. chain:   the misalignment a thorax-fixed base causes for the reference design (GH centre vs the chain's fixed centre)
              and whether its 4R closure still exists when the base no longer turns with the scapula
  4. options: worst-frame GH misalignment of architectures within the DOF cap, including 3-DOF chains whose axes do not
              meet at the GH centre (girdle.py: axis points by exact minimax LP, directions by multi-start Nelder-Mead,
              singular margin >= 20 deg on the fitting clips)
  5. where the arm never points (the J1 axis of a 2R pointing shoulder)
  6. sensitivity of the fitted 3-DOF designs to other rhythm laws (synthetic - NOT data; the real check is OpenSim/OpenCap)
Fitting uses 6 clips; "Wave" and "Walking arm swing" are held out and only evaluated.

    python3 pipeline/girdle/p0_base_mount.py [design id=cad_r13_n4_s1343_1] [--quick]  -> pipeline/girdle/p0_results.json
"""
import json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "judge"))
import girdle as GD
from girdle import BP, D2R, unit
from common import design_dir, load_parts
from sdist import signed_distance
DES = next((a for a in sys.argv[1:] if not a.startswith("-")), "cad_r13_n4_s1343_1"); QUICK = "--quick" in sys.argv
HOLD_OUT = ("Wave", "Walking arm swing"); MARGIN = 20.0; BOUND = 60.0


def stats(x):
    x = np.asarray(x, float); return dict(max=round(float(x.max()), 2), p95=round(float(np.percentile(x, 95)), 2), mean=round(float(x.mean()), 2))


dd = design_dir(DES); C = json.load(open(os.path.join(dd, "clips.json")))
FR = [(c["name"], i, f["want"], f["p"], f["held"]) for c in C["clips"] for i, f in enumerate(c["frames"])]
CLIP = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float)
M = GD.Motion(WANT); LIFT, RS, RH = M.lift, M.RS, M.RH; FIT = ~np.isin(CLIP, HOLD_OUT); TEST = ~FIT
MF, MT = GD.Motion(WANT[FIT]), GD.Motion(WANT[TEST])
OUT = dict(design=DES, frames=len(FR), clips=[c["name"] for c in C["clips"]], hold_out=list(HOLD_OUT), rig="avg/body_pose.py segs()/scap()",
           frame="thorax, mm: x anterior, y up, z right, origin = right GH centre at rest")

# ------------------------------------------------------------------ 1. human: GH centre and scapula vs thorax
gh = np.linalg.norm(LIFT, axis=1); sca = np.array([GD.rot_angle(R) for R in RS])
OUT["human"] = dict(gh_translation_mm=stats(gh), gh_direction="pure +y (superior) in the rig: lift = 0.2*S*max(0, elev-30) mm, S=%.4f" % M.S,
                    scapula_rotation_deg=stats(sca),
                    per_clip={n: dict(elev_max=round(float(WANT[CLIP == n, 1].max()), 1), gh_max_mm=round(float(gh[CLIP == n].max()), 1),
                                      scap_max_deg=round(float(sca[CLIP == n].max()), 1)) for n in OUT["clips"]},
                    elev_at_gh_4mm=round(30 + 4 / (0.2 * M.S), 1), elev_at_gh_10mm=round(30 + 10 / (0.2 * M.S), 1))
print("1. GH vs thorax:", OUT["human"]["gh_translation_mm"], "| scapula rotation (deg):", OUT["human"]["scapula_rotation_deg"], flush=True)

# ------------------------------------------------------------------ 2. the base part: scapula-fixed (pipeline) vs thorax-fixed (physical)
parts = load_parts(dd); B = np.concatenate([P for g, n, P, _ in parts if g == "base"]); B = B[:: max(1, len(B) // 6000)]
f0 = C["clips"][0]["frames"][0]; G0 = BP.scap(f0["p"][1]).T @ np.array(f0["G"]["base"]).reshape(3, 3)   # base group frame -> canonical scapula
B = B @ G0.T                                                              # base vertices, canonical scapula frame (= thorax at rest)
disp = np.array([np.linalg.norm(B @ Rs.T - (B - lf), axis=1).max() for Rs, lf in zip(RS, LIFT)])   # world is GH-centred: trunk at -lift
idx = list(range(0, len(FR), 12 if QUICK else 3)); sd_s, sd_t = [], []
for k in idx:
    V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], WANT[k]))); ct = cKDTree(V[BP.F].mean(1))
    sd_s.append(float(signed_distance(B @ RS[k].T, V, BP.F, tree=ct).min())); sd_t.append(float(signed_distance(B - LIFT[k], V, BP.F, tree=ct).min()))
sd_s, sd_t = np.array(sd_s), np.array(sd_t); wk = idx[int(np.argmin(sd_t))]
OUT["base"] = dict(part_vertices=len(B), displacement_mm=stats(disp),
                   closest_skin_mm=dict(scapula_fixed=dict(min=round(float(sd_s.min()), 2), **stats(sd_s)), thorax_fixed=dict(min=round(float(sd_t.min()), 2), **stats(sd_t))),
                   thorax_fixed_enters_body=dict(frames=int((sd_t < -0.5).sum()), of=len(idx), depth_mm=round(float(max(0, -sd_t.min())), 1),
                                                 worst=[FR[wk][0], FR[wk][1], [round(v) for v in WANT[wk][:3]]]))
print("2. base displacement:", OUT["base"]["displacement_mm"], "| thorax-fixed base enters the body:", OUT["base"]["thorax_fixed_enters_body"], flush=True)

# ------------------------------------------------------------------ 3. reference chain on a thorax-fixed base
K = json.load(open(os.path.join(dd, "design.json")))["kinematics"]; A_ = [x * D2R for x in K["a"]]
b0 = GD.bvec(K["az"], K["el"]); Wd = GD.w_dir(*K["w"]); e_ = unit(np.cross(b0, [0.0, 1, 0])); f_ = np.cross(b0, e_)
def closes(Hg):
    """4R closure exists for some spare angle q (6 deg grid): kinematics only, no skin"""
    u4 = Hg @ Wd; q = np.radians(np.arange(0, 360, 6)); c2 = math.cos(A_[0]) * b0 + math.sin(A_[0]) * (np.cos(q)[:, None] * e_ + np.sin(q)[:, None] * f_)
    th = np.arccos(np.clip(c2 @ u4, -1, 1)); return bool(((th >= abs(A_[1] - A_[2])) & (th <= min(A_[1] + A_[2], 2 * math.pi - A_[1] - A_[2]))).any())
reach_s = np.array([closes(Rs.T @ Rh) for Rs, Rh in zip(RS, RH)]); reach_t = np.array([closes(Rh) for Rh in RH])
OUT["reference_chain"] = dict(misalignment_mm=dict(all=stats(gh), **{n: round(float(gh[CLIP == n].max()), 1) for n in OUT["clips"]}),
                              share_frames_over_mm={str(t): round(float((gh > t).mean()), 3) for t in (2, 4, 10)},
                              closure_exists=dict(scapula_fixed=round(float(reach_s.mean()), 3), thorax_fixed=round(float(reach_t.mean()), 3)),
                              clips_followed_share=round(float(1 - np.mean([f[4] for f in FR])), 3),
                              note="misalignment = GH centre vs the spherical chain's fixed centre; closure = kinematics only, before any skin check")
print("3. reference on a thorax base: GH misalignment", OUT["reference_chain"]["misalignment_mm"]["all"], "| share of frames > 4 / 10 mm:",
      OUT["reference_chain"]["share_frames_over_mm"]["4"], OUT["reference_chain"]["share_frames_over_mm"]["10"], flush=True)

# ------------------------------------------------------------------ 5. where the arm never points
cand = unit(np.random.default_rng(1).normal(size=(20000, 3))); ang = np.degrees(np.arccos(np.clip(np.abs(cand @ M.hdir.T), 0, 1))).min(1)
NEVER = cand[np.argmax(ang)]
OUT["never_points"] = dict(direction_thorax=NEVER.round(3).tolist(), min_angle_to_arm_axis_deg=round(float(ang.max()), 1),
                           note="the axis (either sense) farthest from every humerus direction of the 8 clips: best J1 for a 2R pointing shoulder at a1 = a2 = 90")
print("5. the arm never points within", OUT["never_points"]["min_angle_to_arm_axis_deg"], "deg of", OUT["never_points"]["direction_thorax"], flush=True)


# ------------------------------------------------------------------ 4. architectures
def prm_of(x, branch, ring):
    p = dict(b=(float(x[0]), float(x[1])), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=branch)
    p["w"] = None if ring else (float(x[4]), float(x[5])); return p

def objective(x, branch, ring, exact=False):
    ch = GD.Chain3(prm_of(x, branch, ring)); r = ch.kin(MF)
    if r is None: return 1e3
    A, mg, ok, *_ = r
    if not ok.all(): return 600 + 100 * (~ok).mean()
    pen = 10 * max(0.0, MARGIN - mg.min())
    res = GD.fit_minimax(A, LIFT[FIT], ring, BOUND)[1] if exact else GD.fit_lsq(A, LIFT[FIT], ring)[1]
    return float(res.max()) + pen

def search(ring, seeds, rng):
    if ring: starts = [GD.azel(s * NEVER) + [90.0, 90.0] for s in (1, -1)]
    else:
        starts = []
        for w in unit(rng.normal(size=(40, 3))):
            D = M.RH @ w; Bc = unit(rng.normal(size=(3000, 3))); a_ = np.degrees(np.arccos(np.clip(np.abs(Bc @ D.T), 0, 1))).min(1); k = int(np.argmax(a_))
            starts.append((a_[k], GD.azel(Bc[k]) + [90.0, 90.0] + GD.delaz(w)))
        starts = [s for _, s in sorted(starts, key=lambda t: -t[0])[:6]]
    cands = []
    for s in range(seeds):
        x0 = np.array(starts[s % len(starts)], float) + (rng.normal(0, 10, len(starts[0])) if s >= len(starts) * 2 else 0); br = [1, -1][(s // len(starts)) % 2]
        r = minimize(objective, x0, args=(br, ring, False), method="Nelder-Mead", options=dict(maxiter=500 if QUICK else 1500, xatol=0.1, fatol=0.01))
        cands.append((r.fun, r.x, br))
    cands.sort(key=lambda t: t[0]); best = (1e9, None, 1)
    for f, x, br in cands[:2 if QUICK else 4]:                          # polish with the exact minimax
        r = minimize(objective, x, args=(br, ring, True), method="Nelder-Mead", options=dict(maxiter=150 if QUICK else 600, xatol=0.05, fatol=0.005))
        if r.fun < best[0]: best = (r.fun, r.x, br)
    return prm_of(best[1], best[2], ring)

def report(name, prm, dof, note):
    ch = GD.Chain3(prm); A, mg, ok, *_ = ch.kin(MF); x, _ = GD.fit_minimax(A, LIFT[FIT], ch.coax, BOUND)
    out = dict(dof=dof, note=note, params={k: (None if v is None else (list(np.round(v, 1)) if isinstance(v, tuple) else round(float(v), 1))) for k, v in prm.items()})
    for tag, MM, y in (("fit_clips", MF, LIFT[FIT]), ("held_out_clips", MT, LIFT[TEST]), ("all", M, LIFT)):
        A, mg, ok, *_ = ch.kin(MM); res = GD.residual(A, x, y)
        out[tag] = dict(residual_mm=stats(res), singular_margin_deg_min=round(float(mg.min()), 1), closes=round(float(ok.mean()), 3))
    A, *_ = ch.kin(M); res = GD.residual(A, x, LIFT); el = WANT[:, 1]
    out["residual_by_elevation_mm"] = {f"{a}-{b}": round(float(res[(el >= a) & (el < b)].max()), 2) for a, b in ((0, 30), (30, 60), (60, 90), (90, 120), (120, 181)) if ((el >= a) & (el < b)).any()}
    dirs = [ch.b, ch.c0, GD.Rh_of(0, 0, 0) @ ch.w]                      # axis directions at the reference pose
    perp = [x[3 * i:3 * i + 3] - (x[3 * i:3 * i + 3] @ d) * d for i, d in enumerate(dirs)]   # the axis line's closest point to the GH centre
    out["axis_closest_point_to_GH_mm"] = [[round(float(v), 1) for v in q] for q in perp]
    out["axis_offset_from_GH_mm"] = [round(float(np.linalg.norm(q)), 1) for q in perp]; out["offset_max_mm"] = max(out["axis_offset_from_GH_mm"])
    out["joint_travel_deg"] = ch.joint_travel(M); out["_x"] = x.tolist()
    print(f"   {name:52s} worst {out['all']['residual_mm']['max']:6.2f}  p95 {out['all']['residual_mm']['p95']:6.2f} mm  held-out worst {out['held_out_clips']['residual_mm']['max']:6.2f}"
          f"  singular margin fit/held-out {out['fit_clips']['singular_margin_deg_min']:5.1f}/{out['held_out_clips']['singular_margin_deg_min']:5.1f} deg  |o|max {out['offset_max_mm']:5.1f}", flush=True)
    return out

print("4. architectures: worst-frame GH misalignment (all 8 clips; axis points fitted on 6, 2 held out):", flush=True)
arch = {}; gc = (LIFT.max(0) + LIFT.min(0)) / 2; hz = np.linalg.norm(LIFT[:, [0, 2]], axis=1)
arch["spherical chain, scapula-fixed base (the pipeline's model; no back plate can do this)"] = dict(dof="N", residual_mm=stats(np.zeros(len(FR))))
arch["spherical chain, thorax-fixed base, centre at GH rest (the reference as built)"] = dict(dof="N", residual_mm=stats(gh))
arch["spherical chain, thorax-fixed base, best fixed centre"] = dict(dof="N", residual_mm=stats(np.linalg.norm(LIFT - gc, axis=1)), centre_mm=gc.round(1).tolist())
arch["spherical chain + passive vertical base slide"] = dict(dof="N+1", residual_mm=stats(hz), note="0 only because the rig's GH lift is purely vertical")
for k, v in arch.items(): print(f"   {k:52s} worst {v['residual_mm']['max']:6.2f}  p95 {v['residual_mm']['p95']:6.2f} mm", flush=True)
rng = np.random.default_rng(7); t0 = time.time(); SEEDS = 4 if QUICK else 12
P_RING = search(True, SEEDS, rng)
arch["3 DOF: 2R shoulder (offset axes) + humeral-rotation ring"] = report("3 DOF: 2R shoulder (offset axes) + humeral-rotation ring", P_RING, 3,
                                                                         "J3 = the humerus axis (open ring on the upper arm); J1, J2 need not meet at GH")
P_3R = search(False, SEEDS, rng)
arch["3 DOF: 3R, offset axes"] = report("3 DOF: 3R, offset axes", P_3R, 3, "all three axes free in direction and position")
ch = GD.Chain3(P_RING); A, mg, *_ = ch.kin(M)
arch["3 DOF: 2R shoulder through GH + ring (no offsets)"] = dict(dof=3, residual_mm=stats(gh), singular_margin_deg_min=round(float(mg.min()), 1))
OUT["architectures"] = arch; OUT["search_seconds"] = round(time.time() - t0)

# ------------------------------------------------------------------ 6. sensitivity to the rhythm law (synthetic, NOT data)
def lift_law(slope=0.2, onset=30.0, ap=0.0):
    el, pl = WANT[:, 1], WANT[:, 0]
    y = slope * np.maximum(0, el - onset) * M.S; x = ap * np.sin(np.clip(pl, 0, 90) * D2R) * np.clip((el - onset) / 90, 0, 1)
    return np.c_[x, y, np.zeros_like(y)]
sens = {}
for name, key in (("2R+ring", "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring"), ("3R offset", "3 DOF: 3R, offset axes")):
    ch = GD.Chain3(P_RING if name == "2R+ring" else P_3R); A, *_ = ch.kin(M); x = np.array(arch[key]["_x"])
    for lab, kw in (("slope x0.75", dict(slope=0.15)), ("slope x1.25", dict(slope=0.25)), ("onset 20 deg", dict(onset=20)), ("onset 40 deg", dict(onset=40)),
                    ("+8 mm anterior in flexion", dict(ap=8.0))):
        sens[f"{name} | {lab}"] = stats(GD.residual(A, x, lift_law(**kw)))
OUT["sensitivity_synthetic"] = sens
print("6. the fitted 3-DOF designs under other rhythm laws (synthetic):", flush=True)
for k, v in sens.items(): print(f"   {k:40s} worst {v['max']:6.2f}  p95 {v['p95']:6.2f} mm", flush=True)
json.dump(OUT, open(os.path.join(HERE, "p0_results.json"), "w"), indent=1)
print("->", os.path.join(HERE, "p0_results.json"))
