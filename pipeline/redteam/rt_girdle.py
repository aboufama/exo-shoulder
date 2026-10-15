"""ATTACK 2 - the P0 claim "a 3-DOF chain with offset axes absorbs the GH lift to ~5-7 mm".

A 3-DOF chain on a thorax base is fully determined by the arm's ORIENTATION, so the point where it carries the GH centre,
p(R) = A(R) x (girdle.py), is a function of orientation only. Anything that moves the GH centre at constant orientation
(shrug, load-carrying depression, protraction) or a girdle law other than the one x was fitted to goes straight into
the misalignment. Measured here, with the lead's own Chain3 / fit code:
  1. reproduce the lead's clip numbers (fixed published x)
  2. the whole everyday workspace under the rig's OWN law (x fitted on 6 clips) - and the best any x can do there (LP)
  3. same arm elevation, different planes: the residual spread at elevation 90 / 120 / 150
  4. shrug +15 / +20 mm, depression -10 mm (carrying a load) at constant arm pose, every clip frame
  5. other girdle laws (synthetic; NOT data): smooth onset from 0 deg, plane-dependent lift, protraction in cross-body
     reach, retraction in extension - residual with the published x, with x refit to that law (architecture limit),
     and one x robust to all laws at once (minimax LP over the union)
    python3 rt_girdle.py  -> results/girdle.json
"""
import math, time
import numpy as np
import rt_common as RC
from rt_common import GD, BP, D2R

t0 = time.time(); FR = RC.clips(); names = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float); FIT = ~np.isin(names, RC.HOLD_OUT)
S = GD.Motion(WANT[:1]).S
def rig_lift(P): P = np.atleast_2d(P); return np.c_[np.zeros(len(P)), 0.2 * S * np.maximum(0, P[:, 1] - 30), np.zeros(len(P))]
M = GD.Motion(WANT); assert np.allclose(M.lift, rig_lift(WANT), atol=1e-6)
CANDS = RC.load_candidates(); OUT = dict(candidates={k: dict(params=v["prm"], x_source=v["x_source"], x=np.round(v["x"], 2).tolist()) for k, v in CANDS.items()})
def st(r): r = np.asarray(r); return dict(max=round(float(r.max()), 2), p95=round(float(np.percentile(r, 95)), 2), mean=round(float(r.mean()), 2))

# workspace grid (as rt_jam), elbow 90
pl_g = np.arange(-90, 151, 5.0); el_g = np.arange(0, 171, 5.0); r_g = np.arange(-90, 91, 10.0)
PL, EL, RR = [a.ravel() for a in np.meshgrid(pl_g, el_g, r_g, indexing="ij")]; AX = RR - PL; PLAUS = RC.plausible(PL, EL)
GP = np.c_[PL, EL, AX, np.full(len(PL), 90.0), np.zeros(len(PL))][PLAUS]; MW = GD.Motion(GP, lift_fn=rig_lift)

def laws(P):
    """synthetic girdle laws (thorax frame, mm): name -> (T,3). NOT data - plausible alternatives to the rig's hinge law"""
    pl, el = P[:, 0], P[:, 1]; base = rig_lift(P); y = base[:, 1]
    ramp = np.clip(el / 150.0, 0, 1)
    return {
        "rig law (0.2*S*max(0, elev-30), +y)": base,
        "smooth onset: same 25 mm at 150 deg, quadratic from 0 deg": np.c_[0 * y, 25.3 * ramp ** 2, 0 * y],
        "linear from 0 deg (no 30 deg dead zone), 25 mm at 150": np.c_[0 * y, 25.3 * ramp, 0 * y],
        "plane-dependent: lift x(1 + 0.3 cos(plane)) (more in abduction)": np.c_[0 * y, y * (1 + 0.3 * np.cos(pl * D2R)), 0 * y],
        "+ protraction 15 mm antero-medial in cross-body reach (plane 90..150)": base + 15 * np.clip((pl - 60) / 90, 0, 1)[:, None] * np.clip(el / 60, 0, 1)[:, None] * np.array([0.8, 0, -0.6]),
        "+ retraction 10 mm posterior in extension (plane < -30)": base + 10 * np.clip((-pl - 30) / 60, 0, 1)[:, None] * np.clip(el / 40, 0, 1)[:, None] * np.array([-1.0, 0, 0]),
        **({"LITERATURE law (lead's girdle.lift_literature: Ludewig 2009 via 154 mm clavicle)": GD.lift_literature(P)} if hasattr(GD, "lift_literature") else {}),
    }

res = {}
for tag, c in CANDS.items():
    ch = GD.Chain3(c["prm"]); x = c["x"]; o = {}
    # 1. reproduce
    A, mg, ok, *_ = ch.kin(M); r0 = GD.residual(A, x, M.lift)
    o["clips_published_x"] = dict(all=st(r0), fit=st(r0[FIT]), held_out=st(r0[~FIT]), lead_reported=c["entry"].get("all", {}).get("residual_mm"))
    # 2. whole workspace, rig law
    Aw, mgw, okw, *_ = ch.kin(MW); rw = np.where(okw, GD.residual(Aw, x, MW.lift), np.nan); good = np.isfinite(rw)
    k = int(np.nanargmax(rw)); top = np.argsort(-np.nan_to_num(rw, nan=-1))[:400]; picked = []
    for i in top:
        if all(np.abs(GP[i, :2] - GP[j, :2]).max() >= 25 for j in picked): picked.append(i)
        if len(picked) >= 5: break
    o["workspace_rig_law_published_x"] = dict(poses=int(good.sum()), no_closure=int((~okw).sum()), **st(rw[good]),
                                              share_over_7mm=round(float((rw[good] > 7).mean()), 3), share_over_10mm=round(float((rw[good] > 10).mean()), 3),
                                              share_over_14mm=round(float((rw[good] > 14).mean()), 3),
                                              worst=[dict(plane=float(GP[i, 0]), elev=float(GP[i, 1]), axial=float(GP[i, 2]), r_rel=float(GP[i, 0] + GP[i, 2]), mm=round(float(rw[i]), 1),
                                                          task=RC.task_label(*GP[i, :3])) for i in picked],
                                              by_elevation={f"{a}-{b}": round(float(np.nanmax(rw[(GP[:, 1] >= a) & (GP[:, 1] < b)])), 1) for a, b in ((0, 30), (30, 60), (60, 90), (90, 120), (120, 150), (150, 171))})
    sub = np.flatnonzero(good)[:: max(1, good.sum() // 4000)]
    xw, rwf = GD.fit_minimax(Aw[sub], MW.lift[sub], ch.coax, 60.0); rw2 = GD.residual(Aw[good], xw, MW.lift[good])
    o["workspace_rig_law_best_any_x"] = dict(**st(rw2), note="x refit (minimax LP) on the whole plausible workspace: the architecture's limit with these axis directions")
    # 3. same elevation, different planes (r = 0)
    sp = {}
    for e in (60, 90, 120, 150):
        m = good & (GP[:, 1] == e) & (np.abs(GP[:, 0] + GP[:, 2]) < 1e-6)
        if m.any(): sp[str(e)] = dict(min=round(float(rw[m].min()), 1), max=round(float(rw[m].max()), 1), plane_at_max=float(GP[m, 0][np.argmax(rw[m])]), plane_at_min=float(GP[m, 0][np.argmin(rw[m])]))
    o["same_elevation_other_planes_r0"] = sp
    # 4. shrug / depression at constant arm pose (every clip frame)
    sh = {}
    for lab, dy in (("shrug +15 mm", 15.0), ("shrug +20 mm", 20.0), ("depressed -10 mm (carrying a load)", -10.0)):
        r = GD.residual(A, x, M.lift + np.array([0, dy, 0])); sh[lab] = dict(**st(r), min=round(float(r.min()), 2))
    rng_ = GD.residual(A, x, M.lift + np.array([0, 15.0, 0])); rdn = GD.residual(A, x, M.lift + np.array([0, -10.0, 0]))
    sh["best design point for a -10..+15 mm girdle range at fixed arm pose (lower bound, any x)"] = 12.5
    o["shrug"] = sh
    # 5. other laws: published x / refit per law / one robust x
    Lc = laws(WANT); Lw = laws(GP); per = {}; Ac = A
    allA, ally = [], []
    for lab in Lc:
        rp = GD.residual(Ac, x, Lc[lab]); rpw = np.where(okw, GD.residual(Aw, x, Lw[lab]), np.nan)
        xr, _ = GD.fit_minimax(Ac[FIT], Lc[lab][FIT], ch.coax, 60.0); rr_ = GD.residual(Ac, xr, Lc[lab])
        per[lab] = dict(clips_published_x=st(rp), workspace_published_x=st(rpw[good]), clips_refit_x=st(rr_))
        allA.append(Ac[FIT]); ally.append(Lc[lab][FIT])
    xrob, _ = GD.fit_minimax(np.concatenate(allA), np.concatenate(ally), ch.coax, 60.0)
    syn = [i for i, lab in enumerate(Lc) if not lab.startswith("LITERATURE")]
    xsyn, _ = GD.fit_minimax(np.concatenate([allA[i] for i in syn]), np.concatenate([ally[i] for i in syn]), ch.coax, 60.0)
    for lab in Lc: per[lab]["clips_robust_x"] = st(GD.residual(Ac, xrob, Lc[lab])); per[lab]["clips_robust_synthetic_only_x"] = st(GD.residual(Ac, xsyn, Lc[lab]))
    o["other_laws"] = per; o["robust_x"] = np.round(xrob, 2).tolist()
    res[tag] = o
    print(tag, "clips", o["clips_published_x"]["all"], "| workspace", {k_: o["workspace_rig_law_published_x"][k_] for k_ in ("max", "p95", "share_over_10mm")},
          "| best-x workspace", o["workspace_rig_law_best_any_x"]["max"], f"{time.time() - t0:.0f}s", flush=True)

# magnitude of each law on the clips (what is being absorbed)
OUT["law_magnitude_clips_mm"] = {lab: st(np.linalg.norm(v, axis=1)) for lab, v in laws(WANT).items()}
# reference spherical 4R on a thorax plate (centre at GH rest / best fixed centre), same scenarios
gh = np.linalg.norm(M.lift, axis=1); cen = (M.lift.max(0) + M.lift.min(0)) / 2
res["ref4R_spherical_thorax"] = dict(clips_centre_at_rest=st(gh), clips_best_centre=st(np.linalg.norm(M.lift - cen, axis=1)),
                                     shrug_15=st(np.linalg.norm(M.lift + [0, 15, 0], axis=1)), depressed_10=st(np.linalg.norm(M.lift - [0, 10, 0], axis=1)))
OUT["results"] = res; OUT["workspace_poses"] = int(PLAUS.sum())
RC.jdump(OUT, "girdle.json"); print("->", RC.OUT + "/girdle.json", f"{time.time() - t0:.0f}s")
for tag in CANDS:
    o = res[tag]; print("\n==", tag); print(" worst workspace poses:", o["workspace_rig_law_published_x"]["worst"][:3]); print(" by elev:", o["workspace_rig_law_published_x"]["by_elevation"])
    print(" same elevation other planes:", o["same_elevation_other_planes_r0"]); print(" shrug:", o["shrug"])
    for lab, v in o["other_laws"].items(): print(f"  {lab[:60]:60s} pub {v['clips_published_x']['max']:6.2f}  ws {v['workspace_published_x']['max']:6.2f}  refit {v['clips_refit_x']['max']:6.2f}  robust {v['clips_robust_x']['max']:6.2f}  robust-syn {v['clips_robust_synthetic_only_x']['max']:6.2f}")
print("law magnitudes", OUT["law_magnitude_clips_mm"]); print("ref4R", res["ref4R_spherical_thorax"])
for tag in CANDS: print(tag, "workspace", {k_: v for k_, v in res[tag]["workspace_rig_law_published_x"].items() if k_ not in ("worst", "by_elevation")}, "best-x", res[tag]["workspace_rig_law_best_any_x"])
