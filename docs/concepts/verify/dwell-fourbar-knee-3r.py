"""Adversarial verifier for dwell-fourbar-knee-3r (2026-10-16). Re-measures one configuration with the model's own
frozen-shape protocol (fit on Bench(60,160) FAST, every underside / post frozen, worn on Bench(110,360); CB_EXACT=1 for
the exact path; K6 at 1 mm radial) plus the verifier's corrections:

  * K6 shared-joint exemption sized to the REAL joint: the kit exempts samples within HUB_R + 2 = 12 mm of a shared
    joint axis (sized for an O20 hub); at the O10 MR63ZZ pins P / K / Q only rpin + 2 = 7 mm is the bearing's own zone.
    Applied in the fit (`over` lifts) and in the check, so the frozen shape is honest under the same rule.
  * independent loop closure per pose (not the closed form the model solves with): every rigid body keeps its axis
    angles - link 1 {J1, J2, P}, L2a {J2, K}, rocker {P, Q}, L2b {K, Q, J3} - within 0.5 deg of the rest
    configuration; a pose that fails is not taken (verifier_closure_max_deg reported).
  * pin / knee / crank travel and the transmission-angle minimum over the taken poses (reported).

    CB_EXACT=1 python3 docs/concepts/verify/dwell-fourbar-knee-3r.py <out.json> '<json params>' [--own] [--lock]
    --own: the model's own checks only (no verifier correction) for the before / after comparison.
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_spec = importlib.util.spec_from_file_location("dwell_model", os.path.join(REPO, "docs", "concepts", "models", "dwell-fourbar-knee-3r.py"))
MD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MD)
K = MD.K
PIN_JOINTS = ("P", "K", "Q")
STATE = dict(rpin=5.0, clo_max=0.0, n_bad=0)


def _near_real(A, Bm, da, db, xa, xb, joints, shared, P, clear):
    """K._near with the shared-joint exemption radius of the REAL joint (pins rpin + 2, hubs HUB_R + 2)"""
    ma = np.ones(xa.shape, bool); mb = np.ones(xb.shape, bool); sa, sb = K._scale(A, xa), K._scale(Bm, xb)
    for j in shared:
        rj = (STATE["rpin"] if j in PIN_JOINTS else K.HUB_R) + 2.0
        k = K.unit(joints[j][P])
        ma &= np.arccos(np.clip(np.einsum("pmd,pd->pm", da, k), -1, 1)) * xa / sa > rj
        mb &= np.arccos(np.clip(np.einsum("pmd,pd->pm", db, k), -1, 1)) * xb / sb > rj
    ha, hb = A.hw * sa, Bm.hw * sb
    ca, cb = K.unit(da.mean(1)), K.unit(db.mean(1))
    ra = np.arccos(np.clip(np.einsum("pmd,pd->pm", da, ca).min(1), -1, 1)); rb = np.arccos(np.clip(np.einsum("pmd,pd->pm", db, cb).min(1), -1, 1))
    sep = np.arccos(np.clip((ca * cb).sum(-1), -1, 1))
    reach = (ha.max(1) + hb.max(1) + clear) / np.minimum(xa.min(1), xb.min(1))
    k = np.nonzero((sep <= ra + rb + reach + 1e-6) & ma.any(1) & mb.any(1))[0]
    if not len(k): return None
    dot = np.matmul(da[k].astype(np.float32), db[k].astype(np.float32).transpose(0, 2, 1))
    thr = ha[k] + hb[k].max(1)[:, None] + clear
    cmin = (1.0 - 0.5 * (thr / xa[k]) ** 2).astype(np.float32)
    near = (dot > cmin[:, :, None]) & mb[k][:, None, :]
    near &= ma[k][:, :, None]
    return k, near


_BUILD = MD.build


def build_checked(B, F, p):
    """the model's build + an independent rigid-body closure check per pose (axis angles of each body vs rest)"""
    ch = _BUILD(B, F, p)
    if p.get("lock"): return ch
    C = MD.curve(p)["C"]; R0 = MD.rotz(np.array([p["sref"]]))[0]
    home = dict(J1=C["u1"], J2=C["u2"], P=C["P"], K=R0 @ C["K0"], Q=R0 @ C["Q0"], J3=R0 @ C["J30"])
    pairs = [("J1", "J2"), ("J1", "P"), ("J2", "P"), ("J2", "K"), ("P", "Q"), ("K", "Q"), ("K", "J3"), ("Q", "J3")]
    J = {k: K.unit(np.asarray(v, float)) for k, v in ch.joints.items()}
    err = np.zeros(len(ch.ok))
    for a, b in pairs:
        e0 = float(MD.ang(home[a], home[b])); err = np.maximum(err, np.abs(MD.ang(J[a], J[b]) - e0))
    ok = np.asarray(ch.ok, bool); good = err < 0.5
    STATE["clo_max"] = max(STATE["clo_max"], float(err[ok].max()) if ok.any() else 0.0)
    STATE["n_bad"] = int((ok & ~good).sum())
    ch.ok = ok & good
    ch.info["verifier_closure_max_deg"] = round(float(err[ok].max()), 4) if ok.any() else None
    ch.info["verifier_closure_bad"] = int((ok & ~good).sum())
    return ch


def travel(B, p):
    """pin / joint travel (deg) over the taken poses of the last evaluation"""
    L = B._kit_last; ch, take = L["chain"], L["take"]
    if ch.q is None or not take.any(): return {}
    q = np.asarray(ch.q)[take]; names = ("q1", "crank_s", "knee", "q3", "pinP")
    out = {}
    for j, n in enumerate(names):
        x = np.unwrap(np.radians(q[:, j])); out[n] = round(float(np.degrees(x.max() - x.min())), 1)
    return out


if __name__ == "__main__":
    out = sys.argv[1]; par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    own = "--own" in sys.argv
    if "--lock" in sys.argv: par["lock"] = 1
    STATE["rpin"] = float(par.get("rpin", 5.0))
    if not own:
        K._near = _near_real                                   # used by K6 (collisions_sb) and by the `over` lifts
        MD.build = build_checked                               # model.evaluate / model.frozen resolve `build` at call time
    p0 = dict(MD.PARAMS, **par)
    res = MD.frozen(p0, out)
    res["verifier"] = dict(own_checks_only=own, exempt_pin_mm=None if own else STATE["rpin"] + 2.0, exempt_hub_mm=K.HUB_R + 2.0,
                           closure_max_deg=round(STATE["clo_max"], 4), closure_bad_last=STATE["n_bad"], fold_margin=K.FOLD_MARGIN,
                           o20_only=K.O20_ONLY)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("verifier", res["verifier"], flush=True)
