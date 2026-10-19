"""deltoid-oval-track (kit model): J3 is a closed oval track fixed to the upper arm over the deltoid cap; the J2 hub
rides it on a bogie carriage; link 1 runs from the J1 hub on the acromion top to J2. 3 ACTIVE DOF (q1, q2, s), 0 passive.

Chain (scapula handler -> user's upper-arm cuff), every joint axis through GH (a spherical chain):
  J1 (ACTIVE)  O20 hub, axis b = bvec(b_az, b_el) fixed in the scapula; the handler boss is its lower member, link 1 the
               upper member (F1 + 3.15)
  link 1       w1 x 3 strap on the great circle b -> p2 (arc a1), K3 underside, K5 climb, passes OVER the track, carriage
               and neck (>= 1 mm, by construction)
  J2 (ACTIVE)  O20 hub, axis p2 = HG u(s) (radial through the carriage). Its lower member IS the carriage top plate:
               F2 = R_lo + 5.5 (track 5 mm + 0.5 mm running gap); link 1 is the upper member at F2 + 3.15
  J3 (ACTIVE)  bogie carriage (20 along x 16 across, radial [R_lo, F2 + 3]: plate + four V-rollers on the track edges)
               on a CLOSED oval track (8 wide x 5 radial, radial [R_lo, R_lo + 5]) fixed to the arm; s (arc position)
               is the joint value; no hub (declared hubless: a track carriage)
  arm end      the oval itself; a 14 x 6 K7 neck joins it (welded, pseudo-joint 'weld') to BOTTOM's bar
DOF: the closure is ONE equation angle(b, HG u(s)) = a1 (a 1-D root along the oval, branch sigma = sign(T . b), the
most transversal root on that branch); q1 = azimuth of p2 about b, q2 = azimuth of the oval tangent about p2. Nothing
free, nothing sags (the carriage is pinned by the closure).

SPEC CHANGES (docs/concepts/deltoid-oval-track.md):
  1. ONE track radius (the track is a curve on a sphere about GH). With J1, J2 through GH the carriage must move by
     rotations about GH; a skin-following radius (spec: K3 + 5 per sample) would need a passive radial slide at J2 and
     a pitch pivot in the bogie (+1 passive translation) - not taken.
  2. J2's lower member is the carriage plate (integrated O20), not a hub stacked on top of a 9 mm carriage: J2 and the
     link-1 end sit 3.5 mm lower than the spec's stack, at the same real parts.
  3. Branch = sign(T . b) at the root (roots alternate in it); the spec's sign((V x dV/dt) . b) is not a branch invariant.
  4. Transversality |T . b| / sin a1 >= sin(margin) (default 10 deg) instead of |delta f| per sample.
  5. Bogie: the oval's smallest turning radius at R_lay must be >= turn_min (15 mm) for a 20 mm bogie carriage.
     Track and carriage are laid out at r_lay (set it to the fitted R_lo: tools reports `track_R`).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/deltoid-oval-track.py          # seed on Bench(60,160)
"""
import math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "deltoid-oval-track"
NAME = "Deltoid oval track: J3 a closed cam track fixed to the arm"
D2R = math.pi / 180
TR_W, TR_T = 8.0, 5.0                     # track section (mm)
CAR_L, CAR_W = 20.0, 16.0                 # carriage footprint (mm)
RUN = 0.5                                 # carriage plate over the track top (mm)
PLATE = 3.0                               # O20 lower member plate
NT = 720                                  # oval polyline samples (kinematics)

PARAMS = dict(b_az=106.0, b_el=64.0, a1=70.0, d0=95.0, a0=-10.0, A=30.0, Bw=60.0, f2d=0.0, f2a=0.0, f3d=0.0, f3a=0.0,
              sigma=1, margin=10.0, w1=12.0, q=1.0, r_lay=62.0, turn_min=15.0)
_OV = {}


def oval(p):
    """closed oval on the unit sphere (humerus HG frame), arc-length resampled: U, T, N = U x T (NT, 3), L (rad), kg"""
    key = tuple(round(float(p[k]), 6) for k in ("d0", "a0", "A", "Bw", "f2d", "f2a", "f3d", "f3a"))
    if key in _OV: return _OV[key]
    t = np.linspace(0, 2 * math.pi, 4000, endpoint=False)
    d = p["d0"] + p["A"] * np.cos(t) + p["f2d"] * np.cos(2 * t) + p["f3d"] * np.cos(3 * t)
    a = p["a0"] + p["Bw"] * np.sin(t) + p["f2a"] * np.sin(2 * t) + p["f3a"] * np.sin(3 * t)
    P = K.wdir(d, a); seg = np.arccos(np.clip((P * np.roll(P, -1, 0)).sum(1), -1, 1)); cum = np.r_[0, np.cumsum(seg)]
    L = cum[-1]; s = np.linspace(0, L, NT, endpoint=False); Pc = np.r_[P, P[:1]]
    U = K.unit(np.stack([np.interp(s, cum, Pc[:, j]) for j in range(3)], 1))
    T = K.unit(np.roll(U, -1, 0) - np.roll(U, 1, 0)); T = K.unit(T - (T * U).sum(1, keepdims=True) * U); N = np.cross(U, T)
    dT = (np.roll(T, -1, 0) - np.roll(T, 1, 0)) / (2 * L / NT); kg = (dT * N).sum(1)
    out = dict(U=U, T=T, N=N, L=L, kg=kg, simple=bool(d.min() > 0 and d.max() < 180))
    if len(_OV) > 64: _OV.clear()
    _OV[key] = out; return out


def _interp(X, s):
    j = np.floor(s).astype(int) % NT; f = (s - np.floor(s))[:, None]; k = (j + 1) % NT
    return K.unit((1 - f) * X[j] + f * X[k])


def build(B, F, p):
    ov = oval(p); U, T, N, L = ov["U"], ov["T"], ov["N"], ov["L"]; n = len(F.RS); ar = np.arange(n)
    a1 = p["a1"] * D2R; sig = 1 if p["sigma"] > 0 else -1
    p1 = F.S(K.bvec(p["b_az"], p["b_el"]))                                   # J1 axis (thorax)
    bh = np.einsum("pji,pj->pi", F.RHG, p1)                                  # b in the humerus (HG) frame
    f = np.arccos(np.clip(bh @ U.T, -1, 1)) - a1; g = np.roll(f, -1, 1); Tb = bh @ T.T
    cand = ((f > 0) & (g <= 0)) if sig > 0 else ((f <= 0) & (g > 0))         # sigma = sign(T . b) at the root
    sc = np.where(cand, np.abs(Tb), -1.0); j = sc.argmax(1); found = sc[ar, j] > 0
    fj, gj = f[ar, j], g[ar, j]; s = j + np.where(found, fj / np.where(fj - gj == 0, 1, fj - gj), 0.0)
    for _ in range(3):                                                        # Newton on the interpolated oval
        u = _interp(U, s); t = _interp(T, s); c = np.clip((u * bh).sum(1), -1, 1)
        dfs = -(t * bh).sum(1) / np.maximum(np.sqrt(1 - c * c), 1e-6) * (L / NT)
        s = s - np.where(np.abs(dfs) > 1e-9, (np.arccos(c) - a1) / np.where(np.abs(dfs) > 1e-9, dfs, 1), 0.0)
    s = s % NT; u = _interp(U, s); t = _interp(T, s); t = K.unit(t - (t * u).sum(1, keepdims=True) * u); nn = np.cross(u, t)
    res = np.degrees(np.abs(np.arccos(np.clip((u * bh).sum(1), -1, 1)) - a1))
    cphi = (t * bh).sum(1) / math.sin(a1)
    turn = 1.0 / max(float(np.abs(ov["kg"]).max()), 1e-9) * p["r_lay"]      # smallest turning radius (mm) at r_lay
    ok = found & (np.sign(cphi) == sig) & (np.abs(cphi) >= math.sin(p["margin"] * D2R)) & (res < 0.5)
    ok &= ov["simple"] and turn >= p["turn_min"]
    p2 = np.einsum("pij,pj->pi", F.RHG, u)    # J2 axis = carriage position (thorax)
    t2 = np.einsum("pij,pj->pi", F.RHG, t); n2 = np.einsum("pij,pj->pi", F.RHG, nn)
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, t2), 360.0 * s / NT], -1)

    rl = p["r_lay"]                                                           # mm offsets laid out at r_lay
    na = max(8, int(math.ceil(L * rl / 2.0))); sa = np.linspace(0, NT, na, endpoint=False)
    cs = np.arange(-TR_W / 2, TR_W / 2 + 1e-6, 2.0)
    Dl = K.unit(_interp(U, sa)[:, None, :] + cs[None, :, None] * _interp(N, sa)[:, None, :] / rl).reshape(-1, 3)
    track = K.Member("track", F.HG(Dl), kind="cap", t=TR_T, width=TR_W, joints=("J3", "weld"), r_ref=rl,
                     cell=(L * rl / na) * 2.0)
    xy = K.rect_xy(CAR_L, CAR_W); xy = xy[np.abs(xy[:, 1]) > TR_W / 2 + 1e-6]           # wings beside the track (rollers)
    Dc = K.unit(p2[:, None, :] + (xy[None, :, :1] * t2[:, None, :] + xy[None, :, 1:] * n2[:, None, :]) / rl)
    car = K.Member("carriage", Dc, kind="cap", t=TR_T + RUN + PLATE, width=CAR_W, joints=("J3", "J2"), r_ref=rl,
                   ramps=[(np.ones(len(xy), bool), "track", 0.0)])
    hub1 = K.hub_member("hub1", p1, "J1")
    hub2 = K.hub_member("hub2", p2, "J2"); hub2.joints = ("J2", "J3")      # its lower plate is the carriage plate
    hub2.ramps = [(np.ones(len(hub2.xy), bool), "track", TR_T + RUN)]
    jw = int(np.argmax(U @ (np.einsum("ij,j->i", F.RHG[0].T @ F.RH[0], K.unit(K.BAR0_H)))))   # oval point nearest BOTTOM's bar
    weld = np.einsum("pij,j->pi", F.RHG, U[jw])
    neck = K.neck_member(F, weld, joints=("weld",), ramps=(("track", 0.0), (None, 0)))
    link1 = K.strap_member("link1", p1, p2, ("J1", "J2"), width=p["w1"], t=3.0, ramp_to=(("hub1", K.STACK), ("hub2", K.STACK)),
                           over=[("track", 1.0), ("carriage", 1.0), ("neck", 1.0)])
    info = dict(residual_deg=round(float(res[ok].max()), 4) if ok.any() else None, min_cphi=round(float(np.abs(cphi[ok]).min()), 3) if ok.any() else None,
                turn_mm=round(turn, 1), oval_len_deg=round(L / D2R, 1), s_range=[round(float(q[ok, 2].min()), 1), round(float(q[ok, 2].max()), 1)] if ok.any() else None)
    return K.Chain(members=[hub1, link1, hub2, car, track, neck], ok=ok, q=q,
                   joints=dict(J1=p1, J2=p2, J3=p2, weld=weld), info=info, hubless=("J3", "weld"))


if __name__ == "__main__":
    import json, time
    B = K.bench(60, 160); t0 = time.time()
    r = K.evaluate(B, build, PARAMS)
    last = B._kit_last; prof = last["prof"]
    r["levels"] = {k: [round(float(v.min()), 1), round(float(v.max()), 1)] for k, v in prof.items()}
    r["secs"] = round(time.time() - t0, 1)
    print(json.dumps({k: v for k, v in r.items() if k not in ("poses",)}, default=str))
