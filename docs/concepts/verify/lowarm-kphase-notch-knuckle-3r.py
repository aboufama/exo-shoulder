#!/usr/bin/env python3
"""Independent verifier harness for lowarm-kphase-notch-knuckle-3r (round 15, lens C pick 4).

The claim's model (docs/concepts/models/lowarm-kphase-notch-knuckle-3r.py) is loaded UNCHANGED at its best config (beta -157,
hub-K notch n 2.45 / az 46-98 / F_K+6.0 to the crown in link 1b's boss, J2 dowel at K-eq 45.75) and worn through the
parent's frozen protocol (lowarm-kstop-knuckle-3r.py wear: fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360)
exact / held out, dwell K = law + delta). The verifier adds two metal corrections, each selectable:

  V-OWN  notch ownership. The model keeps hub K's skin-checked O20 samples (rings z 4.08 / 8.17 / 12.25 + the crown disk) on
         member 1 (link 1a, the hub's LOWER member) and drops the 15 of them inside the notch in link 1a's rest frame, while
         the notch solid it adds sits on member 7 (link 1b). The O20 above U0 (F+3.15: boss, bearings, cap) turns with the
         UPPER member (docs/HARDWARE.md v5 groups), and the claim itself puts the notch in link 1b's boss. At K != 0 (up to
         45.6 deg on taken poses) the model's hole therefore sits K degrees away from the real notch: real metal is missing
         from the skin check over a 52-deg sector of the upper wall and crown. --own moves every member-1 contact sample
         inside hub K's O20 above F+3.15 to member 7, then drops the ones inside the notch (link 1b's frame) - the real body.
  V-ARM  the crank's short-arm underside (docs/concepts/verify/lowarm-kstop-knuckle-3r.py, same code): --arm-t T adds the
         arm's skin-facing underside T below the sampled sheet (T = 1.38, the claim family's build spec).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lowarm-kphase-notch-knuckle-3r.py wear <delta> <bench|held> <out.json>
        [--own] [--arm-t 1.38] [--dump PATH] [--flood]
    python3 docs/concepts/verify/lowarm-kphase-notch-knuckle-3r.py combine <dumpA.json> <dumpB.json>   (per-pose worst + probes 0.1 / 0.2)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = _load("kphase_claim_for_verify", os.path.join(REPO, "docs", "concepts", "models", "lowarm-kphase-notch-knuckle-3r.py"))
KS = K.KS
BEST = dict(beta=-157.0)
NOTCH_BEST = dict(on=True, n=2.45, a0=46, a1=98, z0=6.0, z1=12.3)
DOWEL_BEST = 45.75
OPT = dict(own=False, arm_t=0.0)
INFO = {}
U0 = 3.15                                                     # docs/HARDWARE.md v5: upper hub (boss) underside over F
_ADDED_V = []


def notch_samples_own(M):
    """V-OWN: hub K's skin-checked O20 samples above U0 belong to link 1b (member of the notch); drop those inside the notch
    in that body's frame; add the claim's notch solid (same grid as the claim's notch_samples) on link 1b"""
    memK, cK, aK = M.cyl["hubK"]; cK = np.asarray(cK, float); aK = np.asarray(aK, float); e, f = K.frame(aK); mLb = M.link_pts["L1b"][0]
    N = K.NOTCH; n, a0, a1, z0, z1 = N["n"], N["a0"], N["a1"], N["z0"], N["z1"]; rN = K.HUB_R - n; CROWN = K.CROWN
    if any(any(X is A for A in _ADDED_V) for _, X in M.contact): return getattr(M, "_kph_notch", None)

    def cyl(X):
        w = X - cK; z = w @ aK; rv = w - z[:, None] * aK; return np.linalg.norm(rv, axis=1), np.degrees(np.arctan2(rv @ f, rv @ e)), z

    def xyz(r, az, z):
        a = np.radians(az); return cK + np.outer(z, aK) + (r * np.cos(a))[:, None] * e + (r * np.sin(a))[:, None] * f

    def inside(r, az, z): return (r > rN + 1e-6) & (r <= K.HUB_R + 0.05) & (az >= a0) & (az <= a1) & (z >= z0) & (z <= z1)
    info = dict(n=n, a0=a0, a1=a1, z0=z0, z1=z1, own="V-OWN", moved_to_L1b=0, contact_dropped=0)
    new = []
    for m, X in M.contact:
        if m != memK or not len(X): new.append((m, X)); continue
        X = np.asarray(X, float); r, az, z = cyl(X)
        up = (r <= K.HUB_R + 0.05) & (z >= U0 - 1e-6) & (z <= CROWN + 0.05)
        if not up.any(): new.append((m, X)); continue
        ins = inside(r, az, z) & up
        new.append((m, X[~up]))
        keep = up & ~ins
        if keep.any():
            Y = X[keep]; _ADDED_V.append(Y); new.append((mLb, Y))
        info["moved_to_L1b"] += int(keep.sum()); info["contact_dropped"] += int(ins.sum())
    zt = min(z1, CROWN); zz = np.unique(np.r_[np.arange(z0, zt + 1e-9, 0.5), zt]); aa = np.unique(np.r_[np.arange(a0, a1 + 1e-9, 1.0), a1])
    rr = np.unique(np.r_[np.arange(rN, K.HUB_R + 1e-9, 0.5), K.HUB_R])
    A, Z = np.meshgrid(aa, zz); face = xyz(np.full(A.size, rN), A.ravel(), Z.ravel())
    sides = [xyz(R_.ravel(), np.full(R_.size, ae), Z_.ravel()) for ae in (a0, a1) for R_, Z_ in [np.meshgrid(rr, zz)]]
    caps = [xyz(R_.ravel(), A_.ravel(), np.full(R_.size, zc)) for zc in (z0, z1) if zc < CROWN - 1e-9 for R_, A_ in [np.meshgrid(rr, aa)]]
    sol = np.concatenate([face] + sides + caps); _ADDED_V.append(sol); new.append((mLb, sol))
    M.contact = new; info["solid_n"] = int(len(sol)); info["wall_over_MR117_mm"] = round(rN - 5.5, 3)
    M._kph_notch = info; INFO["own"] = info
    return info


_orig_h = KS._harness                                         # the claim's harness (kstop's, with the notch patch)


def _h():
    T, V, LM, DS, S, PLAY = _orig_h()
    INFO["_V"] = V
    C = LM.LHModel
    if OPT["arm_t"] > 0 and not getattr(C, "_kphv_arm", False):
        b0 = C._desmo_build_B

        def b_arm(self):
            out = b0(self)
            g = self._scg; dm = self._desmo; dR = np.asarray(g["dR"], float); F0 = np.asarray(dm["F0"], float); s0 = float(dm["s0"])
            u2 = np.asarray(self.D.u[1], float); A0 = s0 * dR; seg = np.linspace(0, 1, 8)
            bn = np.cross(dR, F0 - A0); bn = bn / np.linalg.norm(bn); W = 3.0
            try: W = float(DS.ARM_W)
            except Exception: pass
            lo = np.array([A0 + t_ * (F0 - A0) + w_ * bn - (1.0 + OPT["arm_t"]) * u2 for t_ in seg for w_ in (-W / 2, 0.0, W / 2)])
            self.contact.append((9, lo))
            INFO["arm"] = dict(arm_t=OPT["arm_t"], n_added=len(lo), arm_W=W)
            return out

        C._desmo_build_B = b_arm; C._kphv_arm = True
    return T, V, LM, DS, S, PLAY


KS._harness = _h


def setup():
    K.NOTCH.update(NOTCH_BEST); KS.DOWEL_K = DOWEL_BEST
    if OPT["own"]: K.notch_samples = notch_samples_own


def flood(V):
    fit, M1, M, B, r = V.CAP["res"]
    MECH = _load("minarc_mech_for_kphase_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
    t1 = time.time(); cr = MECH.connected_report(M, B); cr["secs"] = round(time.time() - t1, 1)
    return {k: v for k, v in cr.items() if k != "static"}


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "combine":
        o = KS.combine(sys.argv[2:]); print(json.dumps(o, default=float)); sys.exit(0)
    if "--arm-t" in sys.argv: OPT["arm_t"] = float(sys.argv[sys.argv.index("--arm-t") + 1])
    OPT["own"] = "--own" in sys.argv
    setup()
    if mode == "wear":
        d, which, outp = float(sys.argv[2]), sys.argv[3], sys.argv[4]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        o = KS.wear(d, which, dump, dict(BEST))
        V = INFO.pop("_V")
        if "--flood" in sys.argv: o["connected"] = flood(V)
        o["verify"] = dict(opt=dict(OPT), notch=dict(K.NOTCH), dowel_K=KS.DOWEL_K, info={k: v for k, v in INFO.items()})
        json.dump(o, open(outp, "w"), indent=1, default=float)
        print(json.dumps({k: o.get(k) for k in ("delta", "wear", "frozen", "dowel", "named", "recomputed", "secs", "verify", "connected")}
                         | {"v": {k: (o["verifier"] or {}).get(k) for k in ("why", "overhead", "near1", "minmetal", "contacts")}}, default=float))
