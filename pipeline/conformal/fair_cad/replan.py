"""Re-plan a band design's clip paths against the REAL part geometry (fair members incl. joint stacks and caps).

For every pose x spare-joint configuration the evaluator found feasible, test the fair members pairwise (radial intervals
skin side .. outer side incl. dome caps, per location): a configuration is out if two members overlap inside a hub core
(planes can't move: stack hits stack/hub) or anywhere by more than LIFT_MAX (local lifts handle the rest). Then the
same smooth DP as band_to_design (<= 180 deg/s per spare joint, hold-and-resume) picks new paths; clips.json is written
into the CAD design dir with the scapula-fixed base frame.

    python3 replan.py <key>
"""
import json, math, os, sys, time
import numpy as np
from scipy.ndimage import map_coordinates
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); FX = os.path.join(EXO, "full-exo")
KEY = sys.argv[1]; LIFT_MAX = float(os.environ.get("LIFT_MAX", 3.0))
SRC = os.path.join(HERE, "..", "band_cad", "inputs", f"{KEY}.json")
# ---- the proxy builder's kinematics + DP, verbatim (head of band_to_design.py up to the clip loop)
src = open(os.path.join(FX, "band_to_design.py")).read()
head = src[:src.index("clips = []; nfol = 0")]; loop = src[src.index("clips = []; nfol = 0"):src.index("# ---------------------------------------------------------------- proxy meshes")]
ns = {"__file__": os.path.join(FX, "band_to_design.py"), "__name__": "band_head"}; argv0 = sys.argv
sys.argv = ["band_to_design.py", SRC, "0", f"cad_{KEY}"]; _c = os.getcwd(); os.chdir(FX); exec(compile(head, "band_to_design_head", "exec"), ns); os.chdir(_c); sys.argv = argv0
sys.path.insert(0, HERE)
sys.argv = ["fair_build.py", KEY, "members"]; import fair_build as FB, members as MB, envelope as EV; sys.argv = argv0
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)
R = ns["R"]; N = R["n"]; P_, C_ = R["PC"]; FEAS0 = ns["FEAS"].copy(); POSE = ns["POSE"]; Qg = ns["Qg"]; GRP = ns["GRP"]

# ---- fixed base frame (same as make_cad_design: the base's tab = local -y = mount direction)
C_old = json.load(open(os.path.join(FB.CAD_DIR, "clips.json")))
f0 = C_old["clips"][0]["frames"][0]; Fb = ns["DS"].scapula(f0["p"][1]).T @ np.array(f0["G"]["base"]).reshape(3, 3)

# ---- provisional fair members (skin + band floor; geometry independent of the path to first order)
E = EV.Envelope(FB.CAD_DIR); off = np.r_[0, np.cumsum(R["sizes"])]; hh = np.array(R["h"]); kd = np.array(R["kind"])
def prov(mem):
    for n, m in mem.items():
        m.grid(); m.env = E.min_radius(n, m.D.reshape(-1, 3)).reshape(m.D.shape[:-1]); mi = 0 if n == "base" else int(n[1:])
        m.fields(m.env, baseline=MB.band_baseline(m, R["dirs_local"][mi], hh[off[mi]:off[mi + 1]], kd[off[mi]:off[mi + 1]]))
mem = FB.make_members(); prov(mem)
for _ in range(3):
    rr = FB.rim_raise(mem)
    if rr < 0.05: break
    FB.FACES[1] += rr; log(f"raised J1 by {rr:.2f} mm"); mem = FB.make_members(); prov(mem)
for n, m in mem.items():
    ins = m.sdf2(m.X, m.Y) <= 0; m.ins_grid = ins
    core = np.zeros_like(ins)
    for h_ in m.hubs:
        c = np.clip(m.D @ h_["axis"], 1e-3, 1); core |= h_["lv"]["S"] * np.sqrt(1 - c * c) / c <= MB.HUB_R + 0.5
    m.core = core
    sl = np.s_[::3, ::3]; sel = ins[sl]
    m.pts = m.D[sl][sel]; m.p_bot = m.bot[sl][sel]; m.p_top = m.top_hw[sl][sel]; m.p_core = core[sl][sel]; m.p_max = m.max_bot_at(m.pts); m.p_allow = m.lift_allow(m.pts)
log(f"{KEY}: members ready, sample points {[len(m.pts) for m in mem.values()]}")

def grid_lookup(m, D):
    """bot, top_hw, inside, core of member m along local dirs D (..., 3), bilinear on its grid"""
    xy = m.chart.xy(D); gx = (xy[..., 0] - m.xs[0]) / MB.GRID; gy = (xy[..., 1] - m.ys[0]) / MB.GRID
    co = np.stack([gx.ravel(), gy.ravel()])
    ins = map_coordinates(m.ins_grid.astype(float), co, order=1, cval=0.0).reshape(gx.shape) > 0.5
    bot = map_coordinates(m.bot, co, order=1, mode="nearest").reshape(gx.shape); top = map_coordinates(m.top_hw, co, order=1, mode="nearest").reshape(gx.shape)
    core = map_coordinates(m.core.astype(float), co, order=1, cval=0.0).reshape(gx.shape) > 0.5
    return bot, top, ins, core

# ---- member frames for every (pose, config)
t0 = time.time(); frames = {}; feas_idx = np.argwhere(FEAS0)
for p, c in feas_idx:
    HG, Rs = ns["pose_mats"](*POSE[p][:3]); pins = ns["chain"](HG, ns["qrad"](c))
    if pins is None: continue
    Fm = ns["frames_of_members"](pins); G = {g: Rs @ F_ for g, F_ in zip(GRP, Fm)}; G["base"] = Rs @ Fb
    frames[(p, c)] = G
log(f"{len(frames)} feasible (pose, config) states ({time.time() - t0:.0f}s)")

# ---- pairwise collision test, batched over states
keys = list(frames); hard = np.zeros(len(keys), bool); why = {}
names = list(mem)
ONLY = os.environ.get("ONLY_BASE") == "1"
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if ONLY and "base" not in (a, b): continue
        A_, B_ = mem[a], mem[b]; adj = FB.adjacent(A_, B_)
        sc = None
        if adj:                                                                         # shared stack core of a's samples
            sc = np.zeros(len(A_.pts), bool)
            for ha in A_.hubs:
                for hb in B_.hubs:
                    if ha["joint"] == hb["joint"]:
                        c = np.clip(A_.pts @ ha["axis"], 1e-3, 1); sc |= ha["lv"]["S"] * np.sqrt(1 - c * c) / c <= MB.HUB_R + 1.0
        near, up_ab = None, None
        for ha in A_.hubs:
            for hb in B_.hubs:
                if ha["joint"] == hb["joint"]:
                    c = np.clip(A_.pts @ ha["axis"], 1e-3, 1); near = ha["lv"]["S"] * np.sqrt(1 - c * c) / c <= MB.HUB_R + 15.0; up_ab = ha["role"] == "upper"
        nh = 0
        for k0 in range(0, len(keys), 512):
            ks = keys[k0:k0 + 512]
            Rab = np.array([frames[k][b].T @ frames[k][a] for k in ks])                 # a-local -> b-local
            Db = np.einsum("kij,nj->kni", Rab, A_.pts)
            bb, bt, bins, bcore = grid_lookup(B_, Db)
            ab, at = A_.p_bot[None], A_.p_top[None]
            ce = MB.CLEAR_MM + 1.0 if near is None else np.where(near[None], -0.05, MB.CLEAR_MM + 1.0)   # coaxial plates at a joint: stack gap
            ov = np.minimum(at, bt) - np.maximum(ab, bb) + ce                                # radial interval overlap (+ clearance)
            m_ = bins & (ov > 0)
            if sc is not None: m_ &= ~sc[None]
            bmax = B_.max_bot_at(Db); amax = A_.p_max[None]                              # same rule as the build: cheaper mover, <= LIFT_CAP
            cA = bt + ce - ab; okA = (bt + ce <= amax) & ((cA <= A_.p_allow[None]) | (cA <= 0.3))
            cB = at + ce - bb; okB = (at + ce <= bmax) & ((cB <= B_.lift_allow(Db)) | (cB <= 0.3))
            in_core = m_ & ~okA & ~okB
            if near is not None: in_core |= m_ & near[None] & np.where(up_ab, ~okA, ~okB)
            big = np.zeros_like(in_core)
            h_ = in_core.any(1)
            if os.environ.get("DBG") and h_.any() and not globals().get("_dumped"):
                j = int(np.nonzero(h_)[0][0]); q = np.nonzero(in_core[j])[0][:6]; globals()["_dumped"] = True
                rr = lambda P, hs: [[round(float(h__["lv"]["S"] * np.tan(np.arccos(np.clip(p @ h__["axis"], -1, 1)))), 1) for h__ in hs] for p in P]
                print("DBG", a, b, "state", ks[j], "near", None if near is None else near[q].tolist(), "up_ab", up_ab)
                print("  A r", rr(A_.pts[q], A_.hubs), "\n  B r", rr(Db[j][q], B_.hubs))
                print("  ab", ab[0][q].round(1), "at", at[0][q].round(1), "amax", np.round(amax[0][q], 1), "\n  bb", bb[j][q].round(1), "bt", bt[j][q].round(1), "bmax", np.round(bmax[j][q], 1))
                print("  cA", cA[j][q].round(1), "okA", okA[j][q], "cB", cB[j][q].round(1), "okB", okB[j][q])
            for j in np.nonzero(h_)[0]:
                kk = k0 + j
                if not hard[kk]: why[keys[kk]] = (a, b, "core" if in_core[j].any() else f"{float(ov[j][m_[j]].max()):.1f} mm")
            hard[k0:k0 + len(ks)] |= h_; nh += int(h_.sum())
        log(f"  {a} x {b}: {nh} colliding states ({100 * nh / max(1, len(keys)):.1f}%)")
log(f"hard collisions in {hard.sum()} of {len(keys)} feasible states ({100 * hard.mean():.1f}%)")
from collections import Counter
log("reasons:", Counter((a_, b_, "core" if r_ == "core" else "big") for a_, b_, r_ in why.values()).most_common())

if ONLY: sys.exit(0)
# ---- new feasibility -> DP with our own neighbourhood (one 12 deg grid step per 0.1 s in every coordinate)
FEAS = FEAS0.copy()
for k, hit in zip(keys, hard):
    if hit: FEAS[k] = False
for (p, c) in set(map(tuple, feas_idx)) - set(frames): FEAS[p, c] = False
QD = ns["QD"]; Qdeg = np.degrees(Qg) if QD else np.zeros((C_, 0)); step = float(R["q_step"]) * 1.0001
dif = np.abs(Qdeg[:, None, :] - Qdeg[None, :, :]); dif = np.minimum(dif, 360 - dif)
NBm = (dif <= step + 1e-6).all(-1); maxnb = NBm.sum(1).max()
NB = np.array([np.concatenate([np.nonzero(r)[0], np.full(maxnb - r.sum(), np.nonzero(r)[0][0])]).astype(int) for r in NBm], dtype=int)
ns["FEAS"] = FEAS; ns["NB"] = NB; ns["C_"] = C_
def my_path(ix):
    out = ns["dp"](ix)
    return out if out is not None else []
EXC = os.path.join(HERE, f"out_{KEY}", "exclude.json")
if os.path.exists(EXC):
    for p, c in json.load(open(EXC)): FEAS[p, c] = False
    log(f"excluded {len(json.load(open(EXC)))} states found colliding by verify_members")
ns["path_of"] = my_path; ns["dp"].__globals__.update(FEAS=FEAS, NB=NB)
_orig_dp = ns["dp"]; REC = []
def _dp_rec(ix):
    out = _orig_dp(ix); REC.append((list(map(int, ix)), out)); return out
ns["dp"] = _dp_rec
os.environ["OWN_DP"] = "1"
exec(compile(loop, "band_to_design_loop", "exec"), ns)
C = dict(subtitle=f"CAD {KEY} (re-planned on the real geometry)", clips=ns["clips"], axes=C_old["axes"], design=C_old.get("design", {}))
for cl in C["clips"]:
    for f in cl["frames"]: f["G"]["base"] = (ns["DS"].scapula(f["p"][1]) @ Fb).round(6).ravel().tolist()
json.dump(C, open(os.path.join(FB.CAD_DIR, "clips.json"), "w"), separators=(",", ":"))
json.dump({f"{p},{c}": v for (p, c), v in list(why.items())[:2000]}, open(os.path.join(HERE, f"out_{KEY}", "replan_collisions.json"), "w"))
chosen = [[int(ix[i]), int(c)] for ix, out in REC if out for i, (c, held) in enumerate(out) if held is None]
json.dump(chosen, open(os.path.join(HERE, f"out_{KEY}", "chosen.json"), "w"))
log("wrote", os.path.join(FB.CAD_DIR, "clips.json"), f"({len(chosen)} followed states)")
