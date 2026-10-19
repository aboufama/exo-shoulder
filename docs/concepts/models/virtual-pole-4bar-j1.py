"""Concept model: VIRTUAL-POLE SPHERICAL FOUR-BAR as J1 (id virtual-pole-4bar-j1). The base on the scapula carries the
four-bar's ground pins A0, B0; the coupler IS link 1 and turns about a virtual pole (the crossing of the two crank great
circles, = the J1 axis at home) that walks along the fixed centrode; link 1 carries J2 (O20 hub), link 2 J3.
The implementation (closure, members, mobility proof, `jac` rank check) is shared with virtual-pole-4bar-j2.py (at=1).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/virtual-pole-4bar-j1.py [check|jac] ['<json params>']
"""
import importlib.util, json, os, sys
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("vp4bar_core", os.path.join(_here, "virtual-pole-4bar-j2.py"))
_core = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_core)
K = _core.K
ID = "virtual-pole-4bar-j1"
NAME = "Virtual-pole spherical four-bar as J1 (base pins on scapula skin, all-pin 3-DOF chain, no slide)"
# at=1 seed: the fold frontier's J1 bvec(132, 16), arcs 50 / 50, J3 wdir(75, 24) (fold-free 96 %, but its hub 1 sat
# over the rising anterior deltoid); the four-bar's pins sit up on the acromion side of that pole
PARAMS = dict(_core.PARAMS, at=1, az=132.0, el=16.0, a1=50.0, a2=50.0, wd=75.0, wa=24.0, zeta=0.0, beta=0.0,
              psiA=150.0, dA0=40.0, dA1=18.0, psiB=-150.0, dB0=40.0, dB1=18.0, sigma=1)


def build(B, F, p): return _core.build(B, F, dict(PARAMS, **p))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = dict(PARAMS, **(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}))
    if mode == "jac":
        import numpy as np
        r = _core.jac(par); print("min / median sigma_min/sigma_max:", r.min() if len(r) else None, np.median(r) if len(r) else None); sys.exit()
    B = K.bench(60, 160); rep = K.evaluate(B, build, par)
    print({k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide",
                                    "honest", "audit", "residual_deg", "pin_sep_deg", "theta_span", "min_cross_deg", "mass_g")})
    print(rep["inband_member"])
