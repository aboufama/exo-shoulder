#!/usr/bin/env python3
"""Alignment audit instrument (new file; the model, verifier and bench run UNCHANGED): lowarm-halfring-knuckle-3r's stage-1
groove layer against link 1b's J2 lower plate, and a re-wear with stage 1 at a level OUTSIDE the model's own glev clamp.

Why: the desmo-slipper audit (docs/alignment/desmo-slipper-knuckle-3r.md, ledger 2026-10-18T06:26:41Z) and the desmo-conecut
CAD-triggered audit found the family's stage-1 level formula hmid = PV.u2 + 3.15 + glev
(docs/concepts/models/desmo-conecut-knuckle-3r.py line 182) puts the groove inside link 1b's J2 lower plate (F+0..F+3,
tools/concept_kit.py line 24) for every glev in the clamp box [-1.0, 1.5], because the crank pivot PV does not sit on hub
2's face. lowarm-halfring-knuckle-3r loads desmo-conecut's _desmo_build_B (patched only for the half ring) and its row
cells A and B both run glev -1.0, the box's lower edge. This tool measures where cell A's (or B's) stage 1 really sits and
re-wears it through the row's own verifier (docs/concepts/verify/lowarm-halfring-knuckle-3r.py, linear IK as verified)
with glev re-applied AFTER the model's clamp.

  geom: the frozen protocol's fit model (Bench(60,160)) and, along u2 over hub 2's face H2 = c2.u2 + f[1]: the crank pivot,
        the groove layer, the pin band, the short arm, link 1b's sampled metal near the hub, the stage-1 gates.
  wear: the verifier's own wear() with glev re-applied after the clamp; --level L puts the groove mid-plane at H2 + L
        (glev = L - pmf - 3.15, pmf = PV.u2 - H2 from geom, passed as --pmf).

  OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_lowarm_s1level.py geom <out.json> [--cell A] [--glev G | --level L --pmf P] [--set k=v]
  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_lowarm_s1level.py wear <bench|held> <out.json> [--cell A]
        (--glev G | --level L --pmf P) [--set a_s=.. --set psi=..] [--dump PATH]
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("lowarm_verify_s1level", os.path.join(REPO, "docs", "concepts", "verify", "lowarm-halfring-knuckle-3r.py"))
LM, DC, DS = V.LM, V.DC, V.DS
GLEV = [None]
_c0 = LM._clamp


def _clamp_w(p):
    q = _c0(p)
    if GLEV[0] is not None: q["glev"] = float(GLEV[0])
    return q


for _m in [LM, DC, DS, LM.SC] + list(sys.modules.values()):
    try:
        if getattr(_m, "_clamp", None) is _c0: _m._clamp = _clamp_w
    except Exception:
        pass
REC = []
_b0 = LM.LHModel._desmo_build_B


def _build(self):
    out = _b0(self)
    try:
        D = self.D; u2 = np.asarray(D.u[1], float); c2 = np.asarray(D.c[1], float); perp = c2 - (c2 @ u2) * u2
        H2 = float(c2 @ u2 + float(self.f[1])); g = self._scg; PV = np.asarray(g["PV"], float); dR = np.asarray(g["dR"], float)
        dm = self._desmo; F0 = np.asarray(dm["F0"], float); hmid = float(dm["hmid"]); s0 = float(dm["s0"])
        r = dict(glev=float(self.p.get("glev")), H2=round(H2, 4), J2_axis_off_GH_mm=round(float(np.linalg.norm(perp)), 6),
                 pivot_minus_face_mm=round(float(PV @ u2) - H2, 4), groove_mid_over_face_mm=round(hmid - H2, 4),
                 groove_layer_over_face_mm=[round(hmid - 0.75 - H2, 3), round(hmid + 0.75 - H2, 3)],
                 pin_band_over_face_mm=[round(float(F0 @ u2) - 0.75 - H2, 3), round(float(F0 @ u2) + 0.75 - H2, 3)],
                 pin_radius_about_u2_mm=round(float(np.linalg.norm(F0 - (F0 @ u2) * u2)), 3),
                 arm_root_over_face_mm=round(float((s0 * dR) @ u2) - 1.0 - H2, 3), arm_pin_end_over_face_mm=round(float(F0 @ u2) - 1.0 - H2, 3),
                 pivot_radius_about_u2_mm=round(float(np.linalg.norm(PV - (PV @ u2) * u2)), 3), r_out=dm.get("r_out"),
                 dR_dot_u2=round(float(dR @ u2), 4), lower_plate_over_face_mm=[0.0, 3.0], link2_member_from_mm=3.15,
                 owd=getattr(self, "_owd", None))
        try:
            mLb, X = self.link_pts["L1b"]; X = np.asarray(X, float)
            if X.ndim == 3: X = X.reshape(-1, 3)
            rr = np.linalg.norm(X - (X @ u2)[:, None] * u2, axis=1); hz = X @ u2 - H2
            sel = rr <= 12.0
            r["l1b_samples_r_le_12"] = dict(n=int(sel.sum()), level_over_face_mm=[round(float(hz[sel].min()), 3), round(float(hz[sel].max()), 3)] if sel.any() else None)
        except Exception as e:
            r["l1b_samples_err"] = repr(e)[:200]
        info = (getattr(self, "_sc_info", None) or {})
        r["stage1"] = ((info.get("desmo") or {}).get("stage1")); r["dK_lim"] = info.get("dK_lim"); r["why_lim"] = info.get("why_lim")
        r["desmo_fail"] = list(getattr(self, "_desmo_fail", []) or [])
        r["lowarm"] = getattr(self, "_lowarm", None)
        REC.append(r)
    except Exception as e:
        REC.append(dict(err=repr(e)[:300]))
    return out


LM.LHModel._desmo_build_B = _build


def _args():
    P = dict(V.BEST); sets = {}
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_); sets[k_] = float(v_)
    return P, sets


if __name__ == "__main__":
    mode = sys.argv[1]
    P, sets = _args()
    if "--glev" in sys.argv: GLEV[0] = float(sys.argv[sys.argv.index("--glev") + 1])
    if "--level" in sys.argv:
        L = float(sys.argv[sys.argv.index("--level") + 1]); pmf = float(sys.argv[sys.argv.index("--pmf") + 1])
        GLEV[0] = L - pmf - 3.15
    if GLEV[0] is not None: P["glev"] = GLEV[0]; sets["glev"] = GLEV[0]
    cell = "A" if ("--cell" in sys.argv and sys.argv[sys.argv.index("--cell") + 1] == "A") else "B"
    t = time.time()
    if mode == "geom":
        path = sys.argv[2]
        os.environ.pop("CB_EXACT", None)
        B1 = V.CB.Bench(n_clip=60, n_ws=160)
        r1, M1 = LM._report_dc(B1, dict(P))
        res = dict(mode="geom", cell=cell, params=P, sets=sets,
                   fit_fast={k: r1.get(k) for k in ("gap", "reach", "follow", "inband14", "contact", "desmo_fail", "why")},
                   rec=REC[-2:], n_builds=len(REC), secs=round(time.time() - t, 1), tool="tools/alignment_lowarm_s1level.py")
        json.dump(res, open(path, "w"), indent=1, default=float); print(json.dumps(res, default=float)[:3000]); sys.exit()
    which, path = sys.argv[2], sys.argv[3]
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    res = V.wear(P, which, False, dump)
    res.update(wear=which, cell=cell, exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets, blend=False,
               glev_used=[r.get("glev") for r in REC[-3:]], s1_geom=REC[-1] if REC else None, n_builds=len(REC),
               tool="tools/alignment_lowarm_s1level.py",
               note="glev re-applied after the model's [-1.0, 1.5] clamp; verifier harness unchanged (linear IK, as verified)",
               secs_total=round(time.time() - t, 1))
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res.get(k) for k in ("frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "n_taken", "sets", "glev_used", "secs_total")}
                     | {"s1": {k: (res.get("s1_geom") or {}).get(k) for k in ("groove_layer_over_face_mm", "pin_band_over_face_mm", "arm_root_over_face_mm",
                                                                              "arm_pin_end_over_face_mm", "desmo_fail", "dK_lim", "why_lim")}}, default=float))
