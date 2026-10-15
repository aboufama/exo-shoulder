"""ATTACK 4 - the 2R + humeral-rotation-ring candidate: can its ring track live on LINK 2 without hitting the trunk?

J3 = the humerus long axis. The track is fixed to link 2, the carriage to the arm (cuff). Per clip frame (the person's
wanted pose; the candidate is assumed to follow), phi(t) = rotation of the arm relative to link 2 about the humerus axis
(girdle.Chain3.kin: R2^T RA). A carriage at arm angle theta_c (half width WC) needs a track that, in link-2 coordinates,
covers theta_c - phi(t) for every t; at frame t the track therefore occupies arm angles
    [theta_c - phi_max + phi(t) - WC,  theta_c - phi_min + phi(t) + WC]           (theta: 0 = lateral, + posterior)
Track cross-section: inner face 3 mm (liner/clearance) above the arm's swept skin envelope (max over clip frames, every
direction it ever faces), TRACK_T thick, at a station s0 (mm from GH along the humerus), TRACK_W wide.
Per frame: exact signed distance (judge/sdist.py) of the track's outer and inner faces to the TRUNK skin (non-arm faces)
and to the FOREARM; baseline = the bare upper-arm skin's own distance to the trunk (the rig lets the arm pass into the
chest in "wash opposite shoulder" - FINDINGS - those frames are flagged, not blamed on the track).
Compared with an arm-fixed ring (the FINDINGS wing-window method) of the same length.
    python3 rt_ring.py [STEP=4]  -> results/ring.json
"""
import math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
import rt_common as RC
from rt_common import GD, BP, D2R
from sdist import signed_distance

STEP = int(next((a for a in sys.argv[1:] if a.isdigit()), 4)); t0 = time.time()
LINER, TRACK_T, TRACK_W, WC, CLEAR = 3.0, 6.0, 12.0, 12.0, 15.0
FR = RC.clips(); names = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float)
CANDS = {k: v for k, v in RC.load_candidates().items() if k.startswith("ring")}; M = GD.Motion(WANT)
def theta_of(v): return np.degrees(np.arctan2(-v[..., 0], v[..., 2]))            # canonical arm frame: 0 = +z lateral, +90 = -x posterior
def phi_of(c):
    ch = GD.Chain3(c["prm"]); A, mg, ok, R1, R2, RA = ch.kin(M); assert ch.coax
    d0 = np.array([0.0, 0, 1.0]); Rrel = np.einsum("tji,tjk->tik", RA, R2)       # RA^T R2: link-2 -> arm
    PHI = theta_of(np.einsum("tij,j->ti", Rrel, d0)); out = np.zeros_like(PHI)
    for n in dict.fromkeys(names):                                               # unwrap within each clip
        m = names == n; out[m] = np.degrees(np.unwrap(np.radians(PHI[m])))
    return out - np.median(out)

REGS = RC.skin_regions(); dom = REGS["dom"]; F = BP.F
TRF = F[(dom[F] <= 1).all(1)]; FOF = F[(dom[F] >= 3).all(1)]; UA = np.flatnonzero(dom == 2)
TH = np.arange(-180, 180, 4.0); SS = np.arange(70, 211, 10.0); DTH = 4.0; DRL = np.arange(3.0, 44.0, 4.0)   # arm chart; radial layers above the envelope
idx = list(range(0, len(FR), STEP))

# pass 1: swept upper-arm envelope r_env(theta, s) (max over frames) in the canonical arm frame
env = np.zeros((len(TH), len(SS)))
for k in ([] if "--reuse" in sys.argv else idx[::2]):
    w = WANT[k]; V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], w))); X = V[UA] @ GD.Rh_of(*w[:3])     # world -> canonical: Rh^T x
    th = theta_of(X); s = -X[:, 1]; r = np.hypot(X[:, 0], X[:, 2])
    it = np.round((th + 180) / DTH).astype(int) % len(TH); is_ = np.round((s - SS[0]) / 10).astype(int); m = (is_ >= 0) & (is_ < len(SS))
    np.maximum.at(env, (it[m], is_[m]), r[m])
for j in range(len(SS)):                                                            # fill empty bins from neighbours (circular)
    col = env[:, j]; good = col > 0
    if good.any() and not good.all(): env[~good, j] = np.interp(np.flatnonzero(~good), np.flatnonzero(good), col[good], period=len(TH))
print("envelope done", f"{time.time() - t0:.0f}s", "r range", env.min().round(1), env.max().round(1), flush=True)

# pass 2: per frame, distance maps of candidate track points (inner / outer face, every theta, s) to trunk and forearm
def pts(theta, s, r):
    t = np.radians(theta); return np.stack([-np.sin(t) * r, -s * np.ones_like(r), np.cos(t) * r], -1)
TT, SG = np.meshgrid(TH, SS, indexing="ij")
DT = np.zeros((len(idx), len(DRL), len(TH), len(SS)), np.float32); DF = np.zeros_like(DT); BASE = np.zeros((len(idx), len(TH), len(SS)), np.float32)
CACHE = os.path.join(RC.OUT, "ring_maps.npz")
if "--reuse" in sys.argv and os.path.exists(CACHE):
    Z = np.load(CACHE); DT, DF, BASE, env = Z["DT"], Z["DF"], Z["BASE"], Z["env"]; assert list(Z["idx"]) == idx
for n_, k in ([] if "--reuse" in sys.argv and os.path.exists(CACHE) else enumerate(idx)):
    w = WANT[k]; V = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], w))); Rh = GD.Rh_of(*w[:3])
    ct = cKDTree(V[TRF].mean(1)); cf = cKDTree(V[FOF].mean(1)); call = cKDTree(V[F].mean(1)); vt = cKDTree(V)
    for L_, dr in enumerate(DRL):
        P = pts(TT, SG, env + dr).reshape(-1, 3) @ Rh.T
        # magnitude: unsigned distance to the trunk (forearm) faces; sign: inside the CLOSED body and the nearest skin vertex is trunk (forearm)
        sfull = signed_distance(P, V, F, tree=call); _, vn = vt.query(P); dn = dom[vn]; ins = sfull < 0
        dT = np.abs(signed_distance(P, V, TRF, tree=ct)); dF = np.abs(signed_distance(P, V, FOF, tree=cf))
        DT[n_, L_] = np.where(ins & (dn <= 1), sfull, np.where(ins & (dn == 2), np.minimum(dT, 0.0) + dT, dT)).reshape(TT.shape)
        DF[n_, L_] = np.where(ins & (dn >= 3), sfull, dF).reshape(TT.shape)
    # the bare upper arm (s >= 110 mm) touching the trunk in this frame: unsigned distance of its skin vertices to trunk faces
    X = V[UA] @ Rh; th = theta_of(X); s = -X[:, 1]; it = np.round((th + 180) / DTH).astype(int) % len(TH); is_ = np.round((s - SS[0]) / 10).astype(int)
    m = (is_ >= 0) & (is_ < len(SS)); d = np.abs(signed_distance(V[UA][m], V, TRF, tree=ct)); b = np.full(TT.shape, 99.0, np.float32); np.minimum.at(b, (it[m], is_[m]), d)
    BASE[n_] = b
    if n_ % 40 == 0: print(f"{n_}/{len(idx)} {time.time() - t0:.0f}s", flush=True)
if "--reuse" not in sys.argv: np.savez_compressed(CACHE, DT=DT, DF=DF, BASE=BASE, env=env, idx=np.array(idx))
CL = names[idx]
arm_touch = (BASE[:, :, SS >= 110] < 1.0).any(axis=(1, 2))                          # the bare upper arm (s >= 110 mm) touches the trunk (arm at the side: real contact)
arm_in_trunk = CL == "Wash opposite shoulder"                                       # FINDINGS: the rig's arm passes INTO the chest in this clip (no contact model) - reported separately

def arc_mask(lo, hi):
    """(n_frames, len(TH)) occupied theta for per-frame arcs [lo, hi] (deg, may wrap)"""
    d = ((TH[None] - lo[:, None]) % 360); return d <= ((hi - lo)[:, None] % 360 + 1e-9) if np.all(hi - lo < 360) else np.ones((len(lo), len(TH)), bool)

def evaluate(theta_c, s0, mode, PH, pmin, pmax):
    """per frame: min distance of the track (inner + outer face) to trunk / forearm. link2: a RIGID track whose inner radius
    at link-2 angle lam is LINER + the envelope's max over every arm angle lam passes (lam + pmin .. lam + pmax)"""
    js = np.flatnonzero(np.abs(SS - s0) <= TRACK_W / 2 + 1e-9); n = len(PH); nT = len(TH)
    if mode == "link2":
        lo = theta_c - pmax + PH - WC; hi = theta_c - pmin + PH + WC
        k = int(np.ceil((pmax - pmin) / DTH)) + 1; win = np.stack([np.roll(env, -int(round(pmin / DTH)) - i, axis=0) for i in range(k)]).max(0)   # win[l] = max env over [TH[l]+pmin, TH[l]+pmax]
        lam_idx = (np.arange(nT)[None, :] - np.round(PH / DTH).astype(int)[:, None]) % nT      # (n, TH): link-2 angle index of arm angle TH at frame t
        off_in = (win[lam_idx][:, :, js] + LINER) - env[None][:, :, js]                          # (n, TH, js) offset above the local envelope
    else:
        half = (pmax - pmin) / 2 + WC; lo = np.full(n, theta_c - half); hi = np.full(n, theta_c + half); off_in = np.full((n, nT, len(js)), LINER)
    li = np.clip(np.round((off_in - DRL[0]) / 4).astype(int), 0, len(DRL) - 1); lo_ = np.clip(np.round((off_in + TRACK_T - DRL[0]) / 4).astype(int), 0, len(DRL) - 1)
    fi = np.arange(n)[:, None, None]; ti = np.arange(nT)[None, :, None]; si = js[None, None, :]
    dtt = np.minimum(DT[fi, li, ti, si], DT[fi, lo_, ti, si]).min(2); dff = np.minimum(DF[fi, li, ti, si], DF[fi, lo_, ti, si]).min(2)
    occ = arc_mask(lo, hi)                                                          # (n, TH)
    dt = np.where(occ, dtt, 99); df = np.where(occ, dff, 99)
    worst_t = dt.min(1); worst_f = df.min(1)
    return worst_t, worst_f, dt, lo, hi

ALL = {}
for tag, c in CANDS.items():
    PHI = phi_of(c); PH = PHI[idx]; pmin, pmax = float(PHI.min()), float(PHI.max())
    print(tag, f"ring travel (link 2 -> arm) {pmin:.1f} .. {pmax:.1f} deg, span {pmax - pmin:.1f}", flush=True)
    grid = []
    for s0 in (80.0, 110.0, 140.0, 170.0, 200.0):
        for tc in np.arange(-90, 181, 15.0):
            for mode in ("link2", "arm-fixed"):
                wt, wf, dt, lo, hi = evaluate(tc, s0, mode, PH, pmin, pmax); ok_ = ~arm_in_trunk if (~arm_in_trunk).any() else np.ones(len(PH), bool)
                grid.append(dict(mode=mode, s0=s0, theta_c=float(tc), trunk_min=round(float(wt[ok_].min()), 1), trunk_min_all=round(float(wt.min()), 1),
                                 frames_trunk_lt_15=int((wt[ok_] < CLEAR).sum()), frames_trunk_lt_0=int((wt[ok_] < 0).sum()), forearm_min=round(float(wf.min()), 1),
                                 frames_forearm_lt_0=int((wf < 0).sum())))
    best = {}
    for mode in ("link2", "arm-fixed"):
        g = [x for x in grid if x["mode"] == mode]; b = max(g, key=lambda x: (x["trunk_min"], -x["frames_trunk_lt_15"])); best[mode] = b
        b2 = min(g, key=lambda x: (x["frames_trunk_lt_15"], -x["trunk_min"])); best[mode + "_fewest_frames_lt_15"] = b2
    # detail for the best link-2 placement: which frames / clips / directions come within 15 mm
    b = best["link2"]; wt, wf, dt, lo, hi = evaluate(b["theta_c"], b["s0"], "link2", PH, pmin, pmax)
    bad = np.flatnonzero(wt < CLEAR); per_clip = {}
    for n_ in bad:
        th_bad = TH[dt[n_] < CLEAR]; pc = per_clip.setdefault(str(CL[n_]), dict(frames=0, min_mm=99.0, theta_close=[], pose=None))
        pc["frames"] += 1; pc["of"] = int((CL == CL[n_]).sum()); pc["bare_arm_touches_trunk_frames"] = int((arm_touch & (CL == CL[n_])).sum())
        if wt[n_] < pc["min_mm"]: pc.update(min_mm=round(float(wt[n_]), 1), pose=[round(v) for v in WANT[idx[n_]][:4]], frame=int(FR[idx[n_]][1]),
                                            track_arc=[round(float(lo[n_])), round(float(hi[n_]))], theta_close=[round(float(th_bad.min())), round(float(th_bad.max()))] if len(th_bad) else [])
    out = dict(candidate=dict(params=c["prm"], x_source=c["x_source"]), ring_travel_deg=dict(min=round(pmin, 1), max=round(pmax, 1), span=round(pmax - pmin, 1)),
               assumptions=dict(liner_mm=LINER, track_thickness_mm=TRACK_T, track_width_mm=TRACK_W, carriage_half_width_deg=WC, clearance_target_mm=CLEAR, frames=len(idx), step=STEP),
               track_arc_length_deg=round(pmax - pmin + 2 * WC, 1), rig_artifact_frames_arm_in_trunk=int(arm_in_trunk.sum()), bare_arm_touches_trunk_frames=int(arm_touch.sum()),
               bare_arm_touch_by_clip={str(k): int(v) for k, v in zip(*np.unique(CL[arm_touch], return_counts=True))},
               best=best, best_link2_detail=per_clip, grid=grid, envelope_radius_mm=dict(min=round(float(env.min()), 1), max=round(float(env.max()), 1)))
    ALL[tag] = out
RC.jdump(ALL, "ring.json"); print("->", RC.OUT + "/ring.json", f"{time.time() - t0:.0f}s")
for tag, out in ALL.items():
    print("==", tag, "travel", out["ring_travel_deg"], "arc", out["track_arc_length_deg"], "artifact frames", out["bare_arm_touches_trunk_frames"], out["bare_arm_touch_by_clip"])
    for k_, v in out["best"].items(): print("  ", k_, v)
    print("   best link-2 placement, frames < 15 mm by clip:", out["best_link2_detail"])
