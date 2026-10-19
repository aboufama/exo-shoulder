#!/usr/bin/env python3
"""Friction red-team probe for lowarm-kphase-notch-knuckle-3r vs its parent lowarm-kstop-knuckle-3r (new audit file; read-only;
the models run UNCHANGED, only their own `mu` parameter is set, the knob their own code reads for the pocket pressure-angle
cap PAC = 43 - atan(mu) in desmo-conecut's _desmo_build_B and for the parent's stage-1 bind gate at mu 0.17).

Why: the claim phases stage 2 (beta -177 -> -157) and reports pa_eff_horn 42.6 against the 43 cap at the model's mu 0.15
(0.4 deg margin) while the parent family reads 33.0 (10 deg margin). The family's own red-team friction is mu 0.17
(lowarm-kstop gates(): "bind first-fail >= 47.35 ... at mu 0.17"). This probe reads, on the claim's fast fit Bench(60,160)
(the protocol's fit bench), the stroke limit dK_lim, its cause, the pressure angles and the fit gap at mu 0.12-0.20, for
the claim's config (beta -157, the notch, J2 dowel 45.75) and for the parent's config (beta -177, no notch, dowel 46.35).

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_mu_probe_kphase.py <out.json>
"""
import importlib.util, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def main(outp):
    rows = []
    KP = _load("kphase_for_mu", os.path.join(REPO, "docs", "concepts", "models", "lowarm-kphase-notch-knuckle-3r.py"))
    notch = dict(on=True, n=2.45, a0=46, a1=98, z0=6.0, z1=12.3, bypass=False)
    for mu in (0.12, 0.15, 0.16, 0.17, 0.20):
        KP.NOTCH.update(notch); t = time.time()
        T, V, LM, DS, S, P, r1, M = KP.fit_fast({"beta": -157.0, "mu": mu})
        rows.append(dict(design="lowarm-kphase-notch-knuckle-3r", mu=mu, P_mu=P.get("mu"), fit={k: r1.get(k) for k in ("gap", "reach", "inband14", "contact")},
                         info=KP._info(M), secs=round(time.time() - t, 1)))
        print(json.dumps(rows[-1], default=float), flush=True)
    KS = _load("kstop_for_mu", os.path.join(REPO, "docs", "concepts", "models", "lowarm-kstop-knuckle-3r.py"))
    for mu in (0.15, 0.17, 0.20):
        t = time.time(); T, V, LM, DS, S, PLAY = KS._harness(); PLAY.update(on=False)
        P = KS.params(T, LM, {"mu": mu}); os.environ.pop("CB_EXACT", None)
        r1, M = LM._report_dc(V.CB.Bench(n_clip=60, n_ws=160), dict(P))
        rows.append(dict(design="lowarm-kstop-knuckle-3r", mu=mu, P_mu=P.get("mu"), fit={k: r1.get(k) for k in ("gap", "reach", "inband14", "contact")},
                         info=KP._info(M), secs=round(time.time() - t, 1)))
        print(json.dumps(rows[-1], default=float), flush=True)
    json.dump(dict(rows=rows, note="fast fit Bench(60,160), the claim protocol's fit bench; PAC = 43 - atan(mu) (desmo-conecut _desmo_build_B); "
                                   "the model's own default mu is LM.CELL_A's"), open(outp, "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1])
