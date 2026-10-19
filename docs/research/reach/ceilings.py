"""Kinematic reach ceilings on Bench(110,360)'s 360 workspace poses (orientation level, no skin): what the J2 fold alone
allows, at the leaders' own seats and over all seats, and what a per-pose-free J1 rocker / a two-state arc relay could add.
Writes docs/research/reach/ceilings.json. docs/research/reach_attribution.md reads it.

  * fold law (any 3R, offsets and slides included): a pose closes iff th = angle(u1, u3) lies in
    [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m]; u1 scapula-fixed, u3 humerus-fixed (the models' K.bvec / K.wdir).
  * at the leaders' seats: th percentiles, share in band at m = 10 / 7 / 5 / 2 / 0, the shortest th interval holding
    90 % / 95 % of the workspace (-> the shorter arc it needs: (width + 2 m) / 2), best arcs at these seats.
  * all seats (u1 lines az 6 / el 4 deg over the upper half sphere + far ends, u3 wd 5 / wa 6): best share per a1 + a2 at
    m = 10, and at the leaders' arcs exactly (are the leaders seat-limited or arc-limited?).
  * per-pose-free rocker: J1 turned about a pivot axis c through GH by any angle in [-beta, beta] chosen per pose (the
    stop-relay rocker / any J1 re-seat with that travel); ceiling = share of poses with SOME angle in band; c scanned.
  * two-state relay on one arc (a2 -> a2' per pose): union of the two bands, a2' scanned.

    OMP_NUM_THREADS=1 CB_QUIET_EXACT=1 nice -n 10 python3 docs/research/reach/ceilings.py
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, HERE)
os.environ.setdefault("CB_QUIET_EXACT", "1")
import concept_bench as CB, concept_kit as K                 # noqa: E402

D2R = math.pi / 180


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def leader_seats():
    """u1 (scapula frame), u3 (humerus band frame, home), a1, a2 of the four verified configurations"""
    A = _load("attr", os.path.join(HERE, "attribute.py")); out = {}
    MD = os.path.join(REPO, "docs", "concepts", "models")
    for L in ("pin-knee", "raglan", "knuckle"):
        P = A.verified_params(L)
        if L == "pin-knee": D = _load("pk_c", os.path.join(MD, "skin-normal-3r-pin-knee.py")).Design(P)
        elif L == "raglan": RK = _load("rk_c", os.path.join(MD, "raglan-knee-3r.py")); D = RK.PK.Design(RK.clean(P))
        else: D = _load("kc_c", os.path.join(MD, "skin-normal-3r-knuckle-cufflink.py")).Design(P)
        out[L] = dict(u1=np.array(D.u[0]), u3=np.array(D.u[2]), a1=math.degrees(D.A[0]), a2=math.degrees(D.A[1]))
    P = A.verified_params("spine")
    out["spine"] = dict(u1=K.bvec(P["az"], P["el"]), u3=K.wdir(P["wd"], P["wa"]), a1=P["a1"], a2=P["a2"])
    return out


def band(a1, a2, m): return abs(a1 - a2) + m, min(a1 + a2, 360 - a1 - a2) - m


def shortest(th, frac):
    s = np.sort(th); n = len(s); k = int(math.ceil(frac * n)) - 1
    w = s[k:] - s[:n - k]; j = int(np.argmin(w)); return float(s[j]), float(s[j + k])


def rot(c, phi):
    """(n_phi, 3, 3) rotations about unit c"""
    c = np.asarray(c, float); Kx = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    ph = np.asarray(phi, float)[:, None, None]
    return np.eye(3)[None] + np.sin(ph) * Kx[None] + (1 - np.cos(ph)) * (Kx @ Kx)[None]


def main():
    t0 = time.time()
    B = CB.Bench(n_clip=110, n_ws=360); Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float)
    kind = np.array(B.kind); ws = kind == "ws"; el = np.array([p["elev"] for p in B.poses]); ov = ws & (el >= 140)
    pl = np.array([p["plane"] for p in B.poses]); acr = ws & (pl >= 100) & (el >= 40)
    beh = ws & np.array([("back" in str(B.clip[i]).lower()) or (pl[i] < -30 and el[i] > 20) for i in range(len(B.idx))])
    out = dict(bench=[110, 360], n_ws=int(ws.sum()), n_overhead=int(ov.sum()), leaders={})
    share = lambda ok, m: round(float(ok[m].mean()), 4)
    for L, s in leader_seats().items():
        W = Q @ s["u3"]; th = np.degrees(np.arccos(np.clip(W @ s["u1"], -1, 1))); a1, a2 = s["a1"], s["a2"]
        r = dict(a1=round(a1, 2), a2=round(a2, 2), th_ws_pct={str(q): round(float(np.percentile(th[ws], q)), 1) for q in (1, 5, 10, 50, 90, 95, 99)},
                 th_overhead_range=[round(float(th[ov].min()), 1), round(float(th[ov].max()), 1)])
        r["in_band"] = {}
        for m in (10, 7, 5, 2, 0):
            lo, hi = band(a1, a2, m); ok = (th >= lo) & (th <= hi)
            r["in_band"][str(m)] = dict(band=[round(lo, 1), round(hi, 1)], ws=share(ok, ws), overhead=share(ok, ov), across=share(ok, acr),
                                        behind=share(ok, beh), folded=int(((th < lo) & ws).sum()), stretched=int(((th > hi) & ws).sum()))
        for f in (0.80, 0.90, 0.95):
            lo, hi = shortest(th[ws], f); r[f"window_{int(f * 100)}"] = dict(th=[round(lo, 1), round(hi, 1)], width=round(hi - lo, 1),
                                                                            shorter_arc_m10=round((hi - lo + 20) / 2, 1))
        # best arcs at these seats (a1, a2 on a 1-deg grid), unconstrained and at a1 + a2 <= the leader's sum
        best = {}
        for cap in (a1 + a2, a1 + a2 + 10, a1 + a2 + 20, 180):
            bb = (0, None)
            for x in range(10, 120):
                for y in range(10, 150):
                    if x + y > cap + 1e-9: break
                    lo, hi = band(x, y, 10); v = float(((th >= lo) & (th <= hi))[ws].mean())
                    if v > bb[0]: bb = (v, (x, y))
            best[f"sum<={cap:.0f}"] = dict(ws=round(bb[0], 4), arcs=bb[1])
        r["best_arcs_at_seats_m10"] = best
        # per-pose-free rocker about pivot c (scan), travel beta
        lo, hi = band(a1, a2, 10); rk = {}
        C = [K.bvec(az, e) for az in range(-180, 180, 15) for e in range(-75, 90, 15)]
        for beta in (5, 10, 15, 20, 30):
            phis = np.radians(np.arange(-beta, beta + 0.01, 1.0)); bestc = (0, None)
            for c in C:
                U = np.einsum("fij,j->fi", rot(c, phis), s["u1"])          # (nphi, 3)
                T = np.degrees(np.arccos(np.clip(W[ws] @ U.T, -1, 1)))      # (nws, nphi)
                v = float(((T >= lo) & (T <= hi)).any(1).mean())
                if v > bestc[0]: bestc = (v, c)
            c = bestc[1]; U = np.einsum("fij,j->fi", rot(c, phis), s["u1"]); T = np.degrees(np.arccos(np.clip(W @ U.T, -1, 1)))
            okp = ((T >= lo) & (T <= hi)).any(1)
            rk[str(beta)] = dict(ws=round(bestc[0], 4), overhead=share(okp, ov), pivot=[round(float(x), 3) for x in c],
                                 bound_shift_only=share((th >= lo - beta) & (th <= hi + beta), ws))
        r["rocker_free_m10"] = rk
        # two-state relay on a2 (or a1): union of the bands
        rl = {}
        for which in ("a1", "a2"):
            bb = (0, None)
            for alt in range(10, 150):
                x, y = (alt, a2) if which == "a1" else (a1, alt)
                lo2, hi2 = band(x, y, 10); ok = ((th >= lo) & (th <= hi)) | ((th >= lo2) & (th <= hi2))
                v = float(ok[ws].mean())
                if v > bb[0]: bb = (v, alt, share(ok, ov))
            rl[which] = dict(ws=round(bb[0], 4), alt=bb[1], overhead=bb[2])
        r["relay_two_state_m10"] = rl
        out["leaders"][L] = r
        print(L, json.dumps(r)[:900], flush=True)
    # all seats: best share per a1 + a2 (m 10), and at the leaders' arcs
    H1 = [(az, e) for az in range(-180, 180, 6) for e in range(-88, 89, 4)]
    H3 = [(wd, wa) for wd in range(5, 176, 5) for wa in range(-180, 180, 6)]
    U1 = np.array([K.bvec(az, e) for az, e in H1]); U3 = np.array([K.wdir(wd, wa) for wd, wa in H3])
    Wa = np.einsum("pij,kj->kpi", Q[ws], U3)                              # (n3, nws, 3)
    nb = 181; best_sum = {}; arcs = {L: (v["a1"], v["a2"]) for L, v in out["leaders"].items()}; best_arc = {L: (0, None) for L in arcs}
    sums = list(range(60, 181, 10))
    for i, u1 in enumerate(U1):
        th = np.degrees(np.arccos(np.clip(Wa @ u1, -1, 1)))                # (n3, nws)
        b = np.clip(np.rint(th).astype(np.int32), 0, nb - 1)
        H = np.bincount((np.arange(len(U3))[:, None] * (nb + 1) + b + 1).ravel(), minlength=len(U3) * (nb + 1)).reshape(len(U3), nb + 1)
        Cm = np.cumsum(H, 1)
        n = th.shape[1]
        for S in sums:
            for d in range(0, S + 1, 10):
                x, y = (S + d) / 2, (S - d) / 2
                lo, hi = band(x, y, 10)
                if hi <= lo: continue
                v = (Cm[:, int(math.floor(hi)) + 1] - Cm[:, int(math.ceil(lo))]) / n; j = int(np.argmax(v))
                if v[j] > best_sum.get(S, (0,))[0]: best_sum[S] = (float(v[j]), x, y, H1[i], H3[j])
        for L, (x, y) in arcs.items():
            lo, hi = band(x, y, 10); v = (Cm[:, int(math.floor(hi)) + 1] - Cm[:, int(math.ceil(lo))]) / n; j = int(np.argmax(v))
            if v[j] > best_arc[L][0]: best_arc[L] = (float(v[j]), H1[i], H3[j])
    out["all_seats_best_by_sum_m10"] = {str(S): dict(ws=round(v[0], 4), a1=v[1], a2=v[2], j1=v[3], j3=v[4]) for S, v in sorted(best_sum.items())}
    out["all_seats_best_at_leader_arcs_m10"] = {L: dict(ws=round(v[0], 4), j1=v[1], j3=v[2]) for L, v in best_arc.items()}
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "ceilings.json"), "w"), indent=1, default=float)
    print("by sum", out["all_seats_best_by_sum_m10"]); print("at arcs", out["all_seats_best_at_leader_arcs_m10"]); print(out["secs"], "s")


if __name__ == "__main__":
    main()
