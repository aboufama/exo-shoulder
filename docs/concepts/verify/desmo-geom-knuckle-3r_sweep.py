"""desmo-geom-knuckle-3r sweep driver (local, one niced process): evaluates configurations through the model's check() on
Bench(60,160) fast and APPENDS each to docs/concepts/sweeps/desmo-geom-knuckle-3r.json (k, t, params, plain metrics, near-touch).
Objective = the near-touch gap (metal < 1 mm counted as contact); a config failing any gate (robust rc, ring rim, boss, stage 2,
stop order) reads 275.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/desmo-geom-knuckle-3r_sweep.py list <configs.json> <tag>
    ... es <seed.json> <tag> <n_evals> <sigma> [rng_seed]      (elitist (1+6) evolution strategy with 1/5-rule step size; no cma
                                                               package on this box)
    a config with "auto_pin": true gets the robust-feasible stage-1 pin with the smallest pitch_hi at its crank geometry (s1grid)
"""
import fcntl, importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sp = importlib.util.spec_from_file_location("dgeom_model", os.path.join(REPO, "docs", "concepts", "models", "desmo-geom-knuckle-3r.py"))
M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
CB = M.CB
SWEEP = os.path.join(REPO, "docs", "concepts", "sweeps", "desmo-geom-knuckle-3r.json")
B = CB.Bench(60, 160)
# the CMA's free parameters and their scales
KEYS = dict(dR_delta=(13.75, 15.0, 0.15), dR_tau=(-6.0, 6.0, 1.5), g=(2.25, 2.6, 0.04), cprog=(-0.09, 0.0, 0.02), a_s=(8.5, 11.0, 0.1),
            psi=(135.0, 165.0, 1.0), blend=(8.0, 14.0, 1.0), r_c=(15.6, 16.6, 0.15), beta=(-180.0, -172.0, 1.0))


def append(row):
    with open(SWEEP + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        L = json.load(open(SWEEP)) if os.path.exists(SWEEP) else []
        row["k"] = len(L); L.append(row); json.dump(L, open(SWEEP, "w"), indent=1, default=float)
    return row["k"]


_MO = {}


def auto_pin(P):
    if "M" not in _MO:
        _, Mo, _ = M.check(dict(P, rc_gate=0, rim_gate=0), B); _MO["M"] = Mo
    rows = M.s1grid(_MO["M"], [float(P["dR_delta"])], [0.0], [float(P["g"])], [float(P["cprog"])], a_rng=(8.6, 10.8), step_a=0.05, step_psi=0.5,
                    psi_rng=(138.0, 165.0), extra=dict(mu=P.get("mu", 0.15), kdrive=P.get("kdrive", 47.5), blend=P.get("blend", 10.0)), rim=M.R_HI)
    rob = [r_ for r_ in rows[0]["robust"] if r_[5] >= float(P.get("pitch_lo_min", 7.40))]   # O11 wall >= 0.8 needs pitch_lo >= ~7.4 (measured)
    if not rob: return None
    pick = rob[0] if P.get("auto_pin") is True else min(rob, key=lambda r_: r_[2])     # True: smallest pitch_hi; "pa": lowest PA
    return dict(P, a_s=pick[0], psi=pick[1], auto_pin_pick=pick)


def ev(P, tag):
    t = time.time()
    if P.get("auto_pin"):
        Q = auto_pin(P)
        if Q is None:
            row = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tag=tag, params=P, gap=275.0, objective_near=275.0, fails=["no robust pin"])
            k = append(row); print(json.dumps(dict(k=k, tag=tag, fails=row["fails"])), flush=True); return 275.0, row
        P = {k_: v for k_, v in Q.items() if k_ != "auto_pin"}
    try:
        out, Mo, _ = M.check(P, B)
    except Exception as e:                                      # noqa: BLE001
        row = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tag=tag, params=P, error=repr(e)[:300], gap=275.0, near=275.0)
        append(row); return 275.0, row
    pl = out.get("plain") or {}; g = out["gates"]; geo = g.get("geom") or {}
    honest = bool(out.get("honest", True)) and not g.get("fail")
    near = float(out["gap"]) if honest else 275.0
    row = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), tag=tag, params=P, inband14=pl.get("inband14"), inband10=out.get("inband10"),
               reach=pl.get("reach"), follow=pl.get("follow"), contact=pl.get("contact"), gap=float(pl.get("gap", 275.0)) if honest else 275.0,
               gap_plain_raw=pl.get("gap"), gap_near1=float(out["gap"]), objective_near=near, honest=honest, fails=g.get("fail"),
               why=out.get("why"), dK_lim=g.get("dK_lim"), why_lim=g.get("why_lim"), pitch=g.get("pitch"), r_out=g.get("r_out"), kplay=g.get("kplay"),
               rc_robust=(geo.get("rc_robust") or {}).get("rc_min"), rc_nominal=(geo.get("rc_robust") or {}).get("rc_nominal"),
               boss_vs_hub2=geo.get("boss_vs_hub2"), ring2_n=geo.get("ring2_rigid_n"), crank_ib=(out.get("parts_ib14") or {}).get("crank"),
               ring_ib=(out.get("parts_ib14") or {}).get("ring2"), stop=((g.get("win") or {}).get("stop") or {}).get("margin"), secs=round(time.time() - t, 1))
    k = append(row)
    print(json.dumps(dict(k=k, tag=tag, near=round(near, 2), plain=row["gap"], ib14=row["inband14"], reach=row["reach"], fails=row["fails"],
                          rc=row["rc_robust"], crank=row["crank_ib"], P={kk: P.get(kk) for kk in KEYS})), flush=True)
    return near, row


if __name__ == "__main__":
    cmd, a1, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    if cmd == "list":
        for P in json.load(open(a1)): ev(P, tag)
    elif cmd == "es":
        seed = json.load(open(a1)); n = int(sys.argv[4]); sig = float(sys.argv[5]); rs = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        rng = np.random.default_rng(rs); ks = list(KEYS)
        def P_of(x): P = dict(seed); P.update({k: round(min(max(float(v), KEYS[k][0]), KEYS[k][1]), 4) for k, v in zip(ks, x)}); return P
        xb = np.array([float(seed[k]) for k in ks]); sc = np.array([KEYS[k][2] for k in ks])
        fb, _ = ev(P_of(xb), tag); used = 1
        while used < n:
            X = [xb + sig * sc * rng.standard_normal(len(ks)) for _ in range(6)]; F = []
            for x in X:
                f, _ = ev(P_of(x), tag); F.append(f); used += 1
            j = int(np.argmin(F))
            if F[j] < fb: xb, fb = np.array([min(max(float(v), KEYS[k][0]), KEYS[k][1]) for k, v in zip(ks, X[j])]), F[j]; sig *= 1.25
            else: sig *= 0.8
            print(json.dumps(dict(es_best=round(fb, 3), sigma=round(sig, 3), used=used)), flush=True)
