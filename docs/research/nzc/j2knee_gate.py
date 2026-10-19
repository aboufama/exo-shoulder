"""Ray-parking gate for the VIRTUAL-J2 knee (near-zero-closure track, 2026-10-16).

Mechanism under test (the 'middle' member of the planar-closure family, see docs/research/nzc/closures.md):
J1 = active pin on a GH ray (hub 1 O20). J2 = a PLANAR TRIPLE of pins all parallel to w (the virtual J2 direction, at arc
a1 from J1): the active J2 pin P is fixed in link 1 at an in-plane offset rho_P from the w-line through GH, two passive
knee pins (a, b) close the planar loop to link 2, which carries J3 (active pin on a GH ray, hub 3 O20). The loop through
the wearer makes link 2 turn about the VIRTUAL w-line through GH, so orientation = the spherical 3R (u1, w, u3): the
fold law is unchanged, but hub 2 no longer has to sit on the w-ray - which is the zero-complexity class's measured cap
(docs/concepts/zc-frontier-3r.md: hub 2 F 60 -> 107 mm as a1 38 -> 62).

The gate (reach_attribution.md section 5: 'every new fold lever gets the ray-parking gate before any CMA'): for seats /
arcs whose fold-law window opens, where can a pin fixed in LINK 1 (P) and a pin fixed in LINK 2 (Pb) sit in band at one
level along w (disc centre ray marched along w from its in-plane offset, K3 march, single level = quantile q over the
closing poses, in band = level - requirement <= 12 mm), and how far apart do they get (the knee's reach)?

    OMP_NUM_THREADS=1 nice python3 docs/research/nzc/j2knee_gate.py [n_clip n_ws] > out.json
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K   # noqa: E402

Q = 0.97


def seat_ok(az, el):
    u = K.bvec(az, el); return bool(-110.0 <= az <= 135.0 and -20.0 <= el <= 90.0 and u[0] <= 0.20)


def band_map(B, I, w, e1, e2, rhos, psis, q=Q, rad=10.0):
    """share of poses I in band for a pin DISC (radius rad: centre + 8 rim points) at in-plane (rho, psi) in basis
    (e1, e2) (per pose), every sample marched along w from its true in-plane offset (K4); the disc level = max over its
    samples per pose, one level = quantile q over the poses"""
    out = {}
    n = len(I); rim = [(0.0, 0.0)] + [(rad * math.cos(t), rad * math.sin(t)) for t in np.radians(np.arange(0, 360, 45))]
    for rho in rhos:
        for psi in psis:
            c, s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
            O = rho * (c * e1 + s * e2)
            Os = np.concatenate([O + x * e1 + y * e2 for x, y in rim]); Is = np.tile(I, len(rim)); ws_ = np.tile(w, (len(rim), 1))
            R = K.requirement(B, Is, ws_, O=Os).reshape(len(rim), n)
            R = np.where(np.isfinite(R), R, 400.0).max(0)
            lev = float(np.quantile(R, q)) if q < 1 else float(R.max())
            share = float(np.mean((lev - R <= 12.0) & (R <= lev)))
            out[(rho, psi)] = (share, lev, O)
    return out


def main():
    nc, nw = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (60, 160)
    B = K.bench(nc, nw); F = K.frames(B); ws = F.ws
    seats1 = [(109.36, 65.94), (95.86, 65.21), (120.0, 55.0), (60.0, 70.0), (0.0, 40.0), (-30.0, 20.0)]
    seats3 = [(85.74, -16.19), (79.15, -13.37), (100.0, -30.0), (70.0, 10.0), (110.0, -60.0), (90.0, 30.0)]
    arcs = [(a1, a2) for a1 in (40, 46, 52, 58, 64) for a2 in (60, 70, 80, 90)]
    rhos = (0.0, 12.0, 20.0, 28.0, 36.0, 44.0); psis = tuple(range(0, 360, 30))
    if os.environ.get("GATE_SEAT1"): seats1 = [seats1[int(os.environ["GATE_SEAT1"])]]
    if os.environ.get("GATE_QUICK"):
        seats1, seats3, arcs = seats1[:1], seats3[:1], [(37, 69), (52, 70), (58, 80)]
    rows = []; t0 = time.time()
    for az, el in seats1:
        if not seat_ok(az, el): continue
        p1 = F.S(K.bvec(az, el))
        for wd, wa in seats3:
            p3 = F.HG(K.wdir(wd, wa))
            for a1, a2 in arcs:
                for sg in (-1, 1):
                    w, ok, _ = K.closure(p1, p3, a1, a2, sg, margin_deg=K.FOLD_MARGIN)
                    reach = float(ok[ws].mean())
                    if reach < 0.74: continue
                    I = np.nonzero(ok)[0]; wI = w[I]
                    e1 = K.unit(p1[I] - (p1[I] * wI).sum(1, keepdims=True) * wI); e2 = np.cross(wI, e1)
                    f1 = K.unit(p3[I] - (p3[I] * wI).sum(1, keepdims=True) * wI); f2 = np.cross(wI, f1)
                    mP = band_map(B, I, wI, e1, e2, rhos, psis, rad=10.0)     # the active J2 pin: O20 hub
                    mB = band_map(B, I, wI, f1, f2, rhos, psis, rad=6.0)      # knee pin b: O12 boss
                    hub2_ray = mP[(0.0, 0)]
                    # best pairs: both pins in band, knee spread (max - min distance) the knee can span
                    best = []
                    for kp, (sp, lp, OP) in mP.items():
                        if sp < 0.85: continue
                        P3 = lp * wI + OP                                              # hub 2 beside hub 1: >= 24 deg apart
                        if np.degrees(np.arccos(np.clip((K.unit(P3) * p1[I]).sum(1), -1, 1))).min() < 24.0: continue
                        for kb, (sb, lb, OB) in mB.items():
                            if sb < 0.85: continue
                            d = np.linalg.norm(OP - OB, axis=1); dl = abs(lp - lb)
                            if d.min() < 17.0 or d.max() / d.min() > 3.5: continue     # O20 + O12 + 1 mm; knee angle 30-150
                            best.append(dict(P=kp, Pb=kb, shareP=round(sp, 3), shareB=round(sb, 3), levP=round(lp, 1),
                                             levB=round(lb, 1), dmin=round(float(d.min()), 1), dmax=round(float(d.max()), 1),
                                             spread=round(float(d.max() - d.min()), 1), dlev=round(dl, 1)))
                    best.sort(key=lambda r: (-(min(r["shareP"], r["shareB"])), r["spread"]))
                    rows.append(dict(az=az, el=el, wd=wd, wa=wa, a1=a1, a2=a2, sigma=sg, reach_kin=round(reach, 4),
                                     hub2_on_ray=dict(share=round(hub2_ray[0], 3), level=round(hub2_ray[1], 1)),
                                     n_pairs=len(best), best=best[:5]))
                    print(f"[{time.time()-t0:6.0f}s] J1({az},{el}) J3({wd},{wa}) a {a1}/{a2} s{sg}: reach {reach:.3f} "
                          f"hub2-on-ray {hub2_ray[0]:.2f}@{hub2_ray[1]:.0f}  pairs>=0.85 {len(best)}"
                          + (f" best {best[0]}" if best else ""), file=sys.stderr, flush=True)
    json.dump(dict(bench=[nc, nw], q=Q, margin=K.FOLD_MARGIN, rows=rows), sys.stdout, indent=1)


if __name__ == "__main__":
    main()
