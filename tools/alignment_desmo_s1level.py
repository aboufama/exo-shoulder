#!/usr/bin/env python3
"""Alignment audit instrument (new file; the model, verifier and bench run UNCHANGED): re-wear desmo-conecut-knuckle-3r with
its stage-1 groove layer at a level OUTSIDE the model's own glev clamp.

Why: the gen-9 CAD found the verified stage-1 layer (hub 2's face + 0.11..1.61 mm, glev -1.0) inside link 1b's J2 lower plate
(F+0..F+3, the v5 lower member of tools/concept_kit.py line 24). The only level in the CAD's scan
(pipeline/full-exo/designs/user_desmo_conecut/stage1_level_scan.json) that clears the plate and keeps a feasible pin is groove
mid F+3.9 = glev +2.039 (pin a_s 9.8 / psi 150). The model clamps glev to [-1.0, 1.5]
(docs/concepts/models/desmo-slipper-knuckle-3r.py line 87, applied by _frozen_model), so `--set glev=2.039` through
tools/alignment_desmo_ring_frame.py silently runs at 1.5 (layer F+2.61..4.11, still 0.39 mm inside the plate). This wrapper
re-applies the requested glev AFTER the model's clamp and records the level the model really used. Everything else is
tools/alignment_desmo_ring_frame.py (ring2 sampled in link 2's true member frame unless --nofix; the verifier's --blend wear).

  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_desmo_s1level.py <bench|held> <out.json> --glev 2.039
        [--set a_s=9.8 --set psi=150] [--nofix] [--dump PATH]
"""
import importlib.util, json, math, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLEV = float(sys.argv[sys.argv.index("--glev") + 1])
if "--blend" not in sys.argv: sys.argv.append("--blend")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


RFT = _load("alignment_desmo_ring_frame_for_s1level", os.path.join(REPO, "tools", "alignment_desmo_ring_frame.py"))
V, DC = RFT.V, RFT.DC
DS, SC = DC.DS, DC.SC
USED = []


def _wrap(f):
    def g(p):
        q = f(p); q["glev"] = GLEV; return q
    return g


for mod in (DS, SC, DC):
    if hasattr(mod, "_clamp"): mod._clamp = _wrap(mod._clamp)
_b0 = DC.DCModel._desmo_build_B


def _build(self):
    out = _b0(self)
    d = getattr(self, "_desmo", None) or {}
    try:
        USED.append(dict(glev=float(self.p.get("glev")), hmid_minus_pivot=None))
    except Exception as e:
        USED.append(dict(err=repr(e)[:200]))
    return out


DC.DCModel._desmo_build_B = _build

if __name__ == "__main__":
    which, path = sys.argv[1], sys.argv[2]
    P = dict(V.BEST); sets = {"glev": GLEV}
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_); sets[k_] = float(v_)
    P["glev"] = GLEV
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    t = time.time()
    res = V.wear(P, which, False, dump)
    lvl = 0.861 + (GLEV + 1.0)
    res.update(exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets, blend=True, blend_ik=dict(V._BL), fix_ring_frame=RFT.FIX,
               ring_frame_log=RFT.LOG[-3:], glev_used=USED[-3:], n_builds=len(USED),
               stage1_layer_over_hub2_face_mm=[round(lvl - 0.75, 3), round(lvl + 0.75, 3)],
               note="glev re-applied after the model's [-1.0, 1.5] clamp; level = 0.861 + (glev + 1) over hub 2's face (build.json "
                    "stage1.levels_over_hub2_face_mm, model_groove_mid 0.861 at glev -1.0)",
               tool="tools/alignment_desmo_s1level.py", secs_total=round(time.time() - t, 1))
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "n_taken", "sets",
                                              "glev_used", "stage1_layer_over_hub2_face_mm", "secs_total")}
                     | {"gates": {k: (res.get("v1_fit_gates") or {}).get(k) for k in ("desmo_fail", "dK_lim", "why_lim", "stage1_pa", "stage1_rc_min")}},
                     default=float))
