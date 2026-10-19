"""J3 hard-stop red team (conecut-knee-knuckle-3r, gen-8 winner): wear the VERIFIED config (rows/conecut-knee-knuckle-3r.json
best_params) through the claim's own model, loaded unchanged (docs/concepts/models/conecut-knee-knuckle-3r.py, SN_CELL=lead),
fit on Bench(60,160) fast as the claim protocol does, and pull the stop's kinematics from the FROZEN shape (no distance
calls are needed for any of these, so the held-out bench is read kinematically only):

  1. q3' (= J3's own angle, link 2 -> member 3) on every pose of the fit bench, Bench(110,360) and the held-out bench,
     with the claim's why-label, so the gap between the deepest taken pose and the nearest stopped pose is on file;
  2. the E-strap vs link-2 clearance as a function of q3' alone (members 2 and 3 are rigid and turn about J3 only, C1
     of the verifier), measured the way the model's collide() measures it (E mid-surface vs link-2 strap points more
     than r3 + 1 from the J3 axis, minus 2 x half thickness) - this is the "natural" stop the dowel replaces;
  3. per pose the world axes u1, u2, u3 (from the hubs' members) -> s3 = |unit(u1 x u2) . u3|: with J1 / J2 free and J3
     on the stop, the moment the chain passes to the base lies along u1 x u2 and its J3 share is s3;
  4. the CAD angles in hub 3's plane: link 2's bar root and the E strap's root about the J3 axis, and the stop ends.

    SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/conecut_mechanism/extract.py [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("SN_CELL", "lead")
os.environ.pop("CB_EXACT", None)
import concept_bench as CB                                   # noqa: E402
from scipy.spatial import cKDTree                            # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


CC = _load("conecut_x", os.path.join(REPO, "docs/concepts/models/conecut-knee-knuckle-3r.py"))
BEST = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-knee-knuckle-3r.json")))["best_params"]
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "stop_geo.json")
P = CC._clamp(dict(CC.PARAMS, **BEST))
t0 = time.time()
B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = CC.CCModel(B1, dict(P)); r1 = M1.run()
fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
print("fit", fit, round(time.time() - t0), flush=True)
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rot(ax, a):
    ax = unit(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


h = CC.S.T_LINK / 2
memL2, L2loc = M1.strap["L2"]
m3, Emloc = M1.Emid
mc3, cen3, ax3 = M1.cyl["hub3"]
r3 = float(M1.hr[2])
print("members: L2", memL2, "E", m3, "hub3", mc3, "hub r3", r3, "f", [round(float(x), 3) for x in M1.f], flush=True)


def world(M, m, i, X): R, t = M.T(m, i); return X @ R.T + t


def pose_table(M, B, label):
    n = len(B.idx); rows = []
    q3p = np.asarray(M.q3p, float) if hasattr(M, "q3p") else CC.wr(np.degrees(M.q[:, 2] + M.K["phi"]))
    for i in range(n):
        R1c, _ = M.T(M1.cyl["hub1"][0], i); R2c, _ = M.T(M1.cyl["hub2"][0], i); R3c, _ = M.T(mc3, i)
        u1 = R1c @ unit(M1.cyl["hub1"][2]); u2 = R2c @ unit(M1.cyl["hub2"][2]); u3 = R3c @ unit(ax3)
        n12 = np.cross(u1, u2); s12 = float(np.linalg.norm(n12)); s3 = float(abs(unit(n12) @ u3)) if s12 > 1e-6 else float("nan")
        rows.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")], q3p=round(float(q3p[i]), 3),
                         why=str(M.why[i]), kin=bool(M.kin_ok[i]) if hasattr(M.kin_ok, "__len__") else None,
                         s3=round(s3, 4), sin12=round(s12, 4),
                         ang_u3_u1=round(math.degrees(math.acos(np.clip(u1 @ u3, -1, 1))), 2),
                         ang_u3_u2=round(math.degrees(math.acos(np.clip(u2 @ u3, -1, 1))), 2)))
    return rows


class Frozen(CC.CCModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))


out = dict(fit_fast=fit, params=BEST, r3=r3, f=[float(x) for x in M1.f], tr=float(M1.tr))
out["fit_bench"] = pose_table(M1, B1, "fit")

# --- E vs link 2 clearance as a function of q3' (link-2 local frame)
taken1 = [i for i in range(len(B1.idx)) if M1.kin_ok[i] and B1.res[i] is not None]
i0 = min(taken1, key=lambda i: M1.q3p[i])          # the most negative taken q3' on the fit bench
i1 = max(taken1, key=lambda i: M1.q3p[i])
def to_l2(i, X): R, t = M1.T(memL2, i); return (X - t) @ R
c3_l2 = to_l2(i0, (M1.T(mc3, i0)[0] @ cen3 + M1.T(mc3, i0)[1])[None])[0]
a3_l2 = unit(M1.T(memL2, i0)[0].T @ (M1.T(mc3, i0)[0] @ unit(ax3)))
E0 = to_l2(i0, world(M1, m3, i0, Emloc)); E1 = to_l2(i1, world(M1, m3, i1, Emloc))
dq = math.radians(M1.q3p[i1] - M1.q3p[i0])
err = {s: float(np.abs((E0 - c3_l2) @ rot(a3_l2, s * dq).T + c3_l2 - E1).max()) for s in (1, -1)}
sgn = min(err, key=err.get)
print("sign", sgn, err, flush=True)
w = L2loc - c3_l2; far = np.linalg.norm(w - (w @ a3_l2)[:, None] * a3_l2, axis=1) > r3 + 1
tree = cKDTree(L2loc[far])
sweep = []
for q in np.arange(-140.0, -95.0 + 1e-9, 0.25):
    d = math.radians(q - M1.q3p[i0]); Eq = (E0 - c3_l2) @ rot(a3_l2, sgn * d).T + c3_l2
    sweep.append((round(float(q), 2), round(float(tree.query(Eq)[0].min()) - 2 * h, 3)))
for q in np.arange(100.0, 180.0 + 1e-9, 0.5):
    d = math.radians(q - M1.q3p[i0]); Eq = (E0 - c3_l2) @ rot(a3_l2, sgn * d).T + c3_l2
    sweep.append((round(float(q), 2), round(float(tree.query(Eq)[0].min()) - 2 * h, 3)))
out["E_L2_clear_vs_q3p"] = sweep
out["E_L2_ref"] = dict(i0=int(i0), q3p_i0=float(M1.q3p[i0]), i1=int(i1), q3p_i1=float(M1.q3p[i1]), sign=sgn, sign_err_mm=err)

# --- CAD angles in hub 3's plane (link 2 local frame at q3' = 0): link-2 bar root, E strap root
e_ = unit(np.cross(a3_l2, [1.0, 0, 0]) if abs(a3_l2[0]) < 0.9 else np.cross(a3_l2, [0, 1.0, 0])); f_ = np.cross(a3_l2, e_)
def ang_of(X):
    w = X - c3_l2; w = w - (w @ a3_l2)[:, None] * a3_l2; r = np.linalg.norm(w, axis=1)
    sel = (r > r3) & (r < r3 + 8); v = w[sel].mean(0) if sel.any() else w.mean(0)
    return math.degrees(math.atan2(v @ f_, v @ e_)), int(sel.sum())
d0 = math.radians(0.0 - M1.q3p[i0]); E_q0 = (E0 - c3_l2) @ rot(a3_l2, sgn * d0).T + c3_l2
out["cad_angles_l2frame_deg"] = dict(frame="link-2 local; origin hub-3 axis, e = unit(a3 x x) / f = a3 x e; positive = right-handed about a3 (the J3 axis, lower -> upper)",
                                     L2_root=ang_of(L2loc), E_root_at_q3p0=ang_of(E_q0), q3p_sense=sgn,
                                     note="E root angle(q3') = E_root_at_q3p0 + q3p_sense * q3'")
json.dump(out, open(OUT, "w"), indent=1, default=float)

# --- Bench(110,360) and held out, kinematics only (frozen shape; no distance calls)
for lab in ("bench110", "held"):
    t = time.time()
    if lab == "held":
        PV = _load("pk_polish_v_conecut_x", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, dict(P2))
    out[lab] = pose_table(M, B, lab)
    print(lab, len(B.idx), round(time.time() - t), flush=True)
    json.dump(out, open(OUT, "w"), indent=1, default=float)
print("done", round(time.time() - t0), flush=True)
