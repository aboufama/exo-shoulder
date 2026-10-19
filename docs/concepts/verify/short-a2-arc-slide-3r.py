"""Adversarial verifier for short-a2-arc-slide-3r (2026-10-16). Re-measures the claimed best configuration with the
model's own frozen-shape protocol (fit on Bench(60,160) FAST, every underside frozen, worn on Bench(110,360) with
CB_EXACT=1, K6 at 1 mm radial, flood fill on) plus the verifier's corrections:

  * --stack: the REAL slide stack under / on hub 3 (the model: hub 3's lower member slides on the Ti rail at a 0.15 mm
    running gap and the keeper plate is "flush" in an underside groove of the 3 mm rail).
      - Ti on Ti sliding galls; the iglidur flanged bushings the model names (GFM-0405, flange 0.75 mm) are the thrust
        face, so hub 3's sole sits flange-high on the rail: +0.75 instead of +0.15.
      - the two M4 shoulder screws (M3 thread) need a keeper / nut under the slot: a tapped 2 mm keeper in a 1 mm
        underside groove protrudes 1 mm below the slot zone (a 1 mm keeper cannot hold an M3 thread; the screw heads
        cannot sit on top of the sole, the J3 upper member runs 0.15 above it). The slot zone (rail_t, the cap) is
        therefore 1 mm deeper below, i.e. modelled as a 4 mm cap whose underside is the keeper, and hub 3 rides
        1 + 0.75 above the 3 mm plate's top.
  * independent per-pose kinematic checks of every taken pose from the chain's own axes (not the model's closed forms):
      angle(J1, J2) = a1 and the slide a2 = angle(J2, J3) inside [a2h, a2max] (0.5 deg), the J2 dihedral inside the
      physical stops [mu_lo, mu_hi] (0.5 deg), the sub-chain margin >= the fold margin; a failing pose is not taken.
  * slide continuity along each clip (consecutive frames, slide step) reported.

    CB_EXACT=1 python3 docs/concepts/verify/short-a2-arc-slide-3r.py <out.json> '<json params>' [--stack]
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_spec = importlib.util.spec_from_file_location("a2s_model", os.path.join(REPO, "docs", "concepts", "models", "short-a2-arc-slide-3r.py"))
MD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MD)
K = MD.K
STATS = []
KEEPER, FLANGE = 1.0, 0.75


def _dihedral(p1, p2, p3):
    a = K.unit(np.cross(p2, p1)); b = K.unit(np.cross(p2, p3))
    return np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))


_extras = MD.extras


def extras_checked(B, r, p):
    L = B._kit_last; ch = L["chain"]; J = ch.joints
    p1, p2, p3 = K.unit(J["J1"]), K.unit(J["J2"]), K.unit(J["J3"])
    a1m = np.degrees(np.arccos(np.clip((p1 * p2).sum(-1), -1, 1))); a2m = np.degrees(np.arccos(np.clip((p2 * p3).sum(-1), -1, 1)))
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    mu = _dihedral(p1, p2, p3); lo, hi = abs(p["a1"] - p["a2h"]) + p["m_stop"], p["a1"] + p["a2h"] - p["m_stop"]
    mu_lo, mu_hi = MD.dihedral(p["a1"], p["a2h"], lo), MD.dihedral(p["a1"], p["a2h"], hi)
    marg = np.minimum.reduce([th - np.abs(a1m - a2m), a1m + a2m - th, 360 - a1m - a2m - th])
    tk = np.array([B.res[j] is not None for j in range(len(B.res))])
    bad_a1 = np.abs(a1m - p["a1"]) > 0.5
    bad_a2 = (a2m < p["a2h"] - 0.5) | (a2m > p["a2max"] + 0.5)
    bad_mu = (mu < mu_lo - 0.5) | (mu > mu_hi + 0.5)
    bad_m = marg < K.FOLD_MARGIN - 0.01
    bad = tk & (bad_a1 | bad_a2 | bad_mu | bad_m)
    for j in np.nonzero(bad)[0]: B.res[j] = None
    L["take"] = L["take"].copy(); L["take"][bad] = False
    # slide continuity along each clip (consecutive frames)
    a2q = np.asarray(ch.q)[:, 3] / MD.QS; steps = []
    cl = [j for j in range(len(B.res)) if B.kind[j] != "ws"]
    for a, b in zip(cl[:-1], cl[1:]):
        if B.clip[a] == B.clip[b] and tk[a] and tk[b]: steps.append(abs(a2q[b] - a2q[a]))
    st = dict(n_taken_before=int(tk.sum()), dropped=int(bad.sum()), bad_a1=int((tk & bad_a1).sum()), bad_a2=int((tk & bad_a2).sum()),
              bad_mu=int((tk & bad_mu).sum()), bad_margin=int((tk & bad_m).sum()),
              a1_err_max=round(float(np.abs(a1m - p["a1"])[tk].max()), 4) if tk.any() else None,
              a2_range=[round(float(a2m[tk].min()), 3), round(float(a2m[tk].max()), 3)] if tk.any() else None,
              mu_range=[round(float(mu[tk].min()), 2), round(float(mu[tk].max()), 2)] if tk.any() else None,
              stops=[round(mu_lo, 2), round(mu_hi, 2)], min_margin=round(float(marg[tk].min()), 2) if tk.any() else None,
              clip_slide_step_max=round(float(max(steps)), 3) if steps else 0.0, bench=[len(cl), len(B.res) - len(cl)])
    STATS.append(st); print("verifier checks", st, flush=True)
    r = _extras(B, r, p); r["verifier_checks"] = st
    return r


MD.extras = extras_checked

if "--stack" in sys.argv:
    _strap = K.strap_member

    def strap_real(name, *a, **kw):
        if name == "rail_t": kw["t"] = kw.get("t", 3.0) + KEEPER        # keeper protrusion below the slot zone
        return _strap(name, *a, **kw)
    MD.K.strap_member = strap_real
    MD.GAP = KEEPER + FLANGE                                         # hub 3 sole: keeper offset + bushing flange


if __name__ == "__main__":
    out = sys.argv[1]; par = json.loads(sys.argv[2])
    res = MD.frozen(MD.snap(par), out)
    res["verifier"] = dict(stack="--stack" in sys.argv, keeper_mm=KEEPER if "--stack" in sys.argv else 0.0,
                           flange_mm=FLANGE if "--stack" in sys.argv else 0.15, checks=STATS)
    json.dump(res, open(out, "w"), indent=1, default=float)
