"""Audit of onetooth-slowlaw-knuckle-3r (2026-10-18). Run: OMP_NUM_THREADS=1 python3 <this> 0.8 1.2 1.5
Upper bound on the K stroke ONE tooth-tooth pair (spherical involute-like, plane of action through the pole)
can carry with both kinematic pressure angles <= the gate, at the model's own axes (uK, u2) and law rho.
The pin scan in the row covers pins only (normal through the pin centre); this covers the other one-pair profile."""
import importlib.util, json, math, os, sys
os.environ["OT_CELL"] = "ghost"; sys.path.insert(0, "/home/user/exo-shoulder/tools")
import numpy as np
sp_ = importlib.util.spec_from_file_location("ot", "/home/user/exo-shoulder/docs/concepts/models/onetooth-slowlaw-knuckle-3r.py")
OT = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(OT)
S, FL, SN = OT.S, OT.FL, OT.SN


def bound(rho, mu=0.087):
    P = OT._clamp(dict(OT.PARAMS, rho=rho))
    D = FL.G.KR.KB.KDesign(P)
    if getattr(D, "q2sgn", None) is None: D.q2sgn = -1.0
    L = D.law(); u2, uK = D.u[1], D.uK; sp = float(np.sign(D.psiA)) or 1.0; s_q = float(L["s_q"])
    w1 = -sp * uK; w2 = (s_q / rho) * u2                      # per unit K, link 1b frame (same convention as flank())
    pole = S.unit(w1 - w2)
    if pole @ (uK + u2) < 0: pole = -pole
    gate = SN.pa_kin(mu)
    best = (0, None)
    e = S.unit(np.cross(pole, np.cross(uK - u2, pole)))       # tangent at the pole along the line of centres
    f = np.cross(pole, e)                                     # tangent at the pole across the line of centres
    sig = np.radians(np.arange(-80, 80.01, 0.05))
    for phi in np.arange(0.0, 90.01, 0.5):                    # tilt of the plane of action from the common tangent f
        t = math.cos(math.radians(phi)) * f + math.sin(math.radians(phi)) * e
        X = np.cos(sig)[:, None] * pole + np.sin(sig)[:, None] * t   # great circle through the pole
        n = -np.sin(sig)[:, None] * pole + np.cos(sig)[:, None] * t  # its tangent = the contact normal
        v1 = np.cross(w1, X); v2 = np.cross(w2, X)
        pa1 = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i", n, v1)) / np.maximum(np.linalg.norm(v1, axis=1), 1e-12), 0, 1)))
        pa2 = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i", n, v2)) / np.maximum(np.linalg.norm(v2, axis=1), 1e-12), 0, 1)))
        ok = (pa1 <= gate) & (pa2 <= gate)
        # involute realizability (no interference): contact only between the base-cone tangency points T1 (uK's foot)
        # and T2 (u2's foot) on the plane of action
        Nn = S.unit(np.cross(pole, t))
        def foot(u):
            q = S.unit(u - (u @ Nn) * Nn); return math.atan2(float(q @ t), float(q @ pole))
        s1, s2 = foot(uK), foot(u2); lo, hi = min(s1, s2), max(s1, s2)
        ok &= (sig >= lo) & (sig <= hi)
        # rate: dsigma / dK = n . v1 (the contact point advances along the normal with body 1's normal velocity)
        rate = np.abs(np.einsum("ij,ij->i", n, v1))
        # longest contiguous ok run, K travelled = integral dsigma / rate
        best_run = 0.0; j = 0; N = len(sig); ds = sig[1] - sig[0]
        while j < N:
            if ok[j]:
                j0 = j
                while j < N and ok[j]: j += 1
                K = float(np.sum(ds / np.maximum(rate[j0:j], 1e-9)))
                if K > best_run: best_run = K; span = (round(float(np.degrees(sig[j0])), 1), round(float(np.degrees(sig[j - 1])), 1))
            j += 1
        if best_run > best[0]: best = (best_run, dict(phi=float(phi), span_deg=span))
    ang = lambda a, b: round(math.degrees(math.acos(max(-1, min(1, float(a @ b))))), 2)
    return dict(rho=rho, gate=round(gate, 2), uK_u2=ang(uK, u2), pole_from_u2=ang(pole, u2), pole_from_uK=ang(pole, uK),
                K_range_max_deg=round(math.degrees(best[0]), 2), at=best[1])


if __name__ == "__main__":
    print(json.dumps([bound(float(r)) for r in sys.argv[1:]]))
