"""Round 15 lens A fill: the kinematic window takes (th >= 5, plus the knee window where a pin knee has one) of the
verified pin-knee configs on Bench(110,360)'s 360 workspace poses, read from each model's own IK (no fit, no metal).
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/take_bound_3dof_kinfill.py
Writes docs/research/take_bound_3dof_kinfill.json."""
import importlib.util, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB  # noqa: E402


def load(name):
    sp = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(REPO, "docs/concepts/models", name + ".py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


B = CB.Bench(n_clip=110, n_ws=360); ws = np.array([k == "ws" for k in B.kind])
cells = [("H1 skin-normal-3r-pin-knee (verified best_params)", "skin-normal-3r-pin-knee",
          json.load(open(os.path.join(REPO, "docs/concepts/rows/skin-normal-3r-pin-knee.json")))["best_params"]),
         ("crest-knee-3r joggle (verified best_params_joggle)", "crest-knee-3r",
          json.load(open(os.path.join(REPO, "docs/concepts/rows/crest-knee-3r.json")))["best_params_joggle"])]
out = dict(bench="Bench(110,360) ws poses (360), model IK only (Model.__init__: kin_ok / why before any fit)", cells={})
for label, mod, par in cells:
    Mm = load(mod); M = Mm.Model(B, dict(par))
    why = np.array([w if w else "" for w in M.why], dtype=object)
    c = {k: int(((why == k) & ws).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop")}
    c["kin_ok_ws"] = int((np.asarray(M.kin_ok) & ws).sum())
    c["th_window_takes"] = int(ws.sum()) - c["fold"]
    out["cells"][label] = c; print(label, c, flush=True)
json.dump(out, open(os.path.join(HERE, "take_bound_3dof_kinfill.json"), "w"), indent=1)
