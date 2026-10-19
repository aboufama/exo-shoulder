#!/usr/bin/env python3
"""Alignment audit instrument (new file; the model, verifier, bench and tools/sample_density.py run UNCHANGED): the exact
confirmation of the S6 density re-weight for desmo-slipper-knuckle-3r, through the VERIFIER's own harness (--blend IK).

Why a new file: `tools/sample_density.py rewear` (2026-10-18.1) crashes before any wear - it calls _thin(M1, *thin) with
thin = (names, step, wear), three arguments into a two-argument signature (TypeError), and its held path patches the
first Bench it sees, which on this model's held wear is the polish file's Bench(20, 20), not the fit bench. This adapter
does the same thinning (tools/sample_density.py _thin: greedy 2 mm Poisson-disc subsample of the named parts, in place,
after the fit and before the wear, so the frozen shape is the claim's). Default (--at truncate): the Frozen wear model is
thinned when its fit() calls _truncate(), i.e. right after it copied the fitted M1's rigid / link_pts and before any wear
pose is scored; the fit itself (fit_fast) runs unthinned and must equal the control's. --at run (the first version, kept
for the record): the first non-Frozen DSModel.run to return is thinned; on this model that is a nested model inside M1's
run, so the fast fit report is read on thinned parts too (the frozen shape still matches: every unthinned part's in-band
equals the control's). Contact samples (M.contact) are not touched. --no-thin is the control through the identical path.

It loads tools/alignment_desmo_slipper_s1level.py (which loads the verifier with --blend and re-applies glev after the
model's clamp), so --glev G wears the plate-clearing level too (the 2026-10-18 audit's F+3.9: --glev 2.0497 --set a_s=9.8).
The placement defaults to the row's verification.verified_config (a_s 9.5 / psi 150), NOT best_params: best_params is the
refuted claim placement 9.25 / 154, and this adapter's first run wore it by accident (18.77 thinned there; not a reading
of the verified design).

  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_density_rewear_desmo.py <bench|held> <out.json>
        [--glev G] [--set k=v ...] [--thin roller,horn,ring2] [--no-thin] [--at truncate|run]
"""
import importlib.util, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


SD = _load("sd_for_desmo_rewear", os.path.join(REPO, "tools", "sample_density.py"))
SL = _load("sl_for_desmo_rewear", os.path.join(REPO, "tools", "alignment_desmo_slipper_s1level.py"))   # appends --blend
V, DS = SL.V, SL.DS
BOX = {}
_run0 = DS.DSModel.run


def _run(self, *a, **k):
    out = _run0(self, *a, **k)
    if BOX.get("at") == "run" and type(self).__name__ != "Frozen" and not BOX.get("done") and BOX.get("names"):
        BOX["info"] = SD._thin(self, BOX["names"], SD.KIT_STEP); BOX["done"] = True
    return out


_tr0 = DS.DSModel._truncate


def _truncate(self, *a, **k):
    if BOX.get("at") == "truncate" and type(self).__name__ == "Frozen" and not BOX.get("done") and BOX.get("names"):
        BOX["info"] = SD._thin(self, BOX["names"], SD.KIT_STEP); BOX["done"] = True
    return _tr0(self, *a, **k)


DS.DSModel.run = _run
DS.DSModel._truncate = _truncate

if __name__ == "__main__":
    which, path = sys.argv[1], sys.argv[2]
    P, sets = SL._args()
    # the row's best_params is the REFUTED claim placement (a_s 9.25 / psi 154); the verified 18.95 is
    # verification.verified_config (9.5 / 150). Default to the verified placement; --set still overrides.
    VC = (json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "desmo-slipper-knuckle-3r.json"))).get("verification") or {}).get("verified_config") or {}
    for k_, v_ in VC.items():
        if isinstance(v_, (int, float)) and not isinstance(v_, bool) and k_ not in sets: P[k_] = float(v_)
    if "--glev" in sys.argv:
        SL.GLEV[0] = float(sys.argv[sys.argv.index("--glev") + 1]); P["glev"] = SL.GLEV[0]; sets["glev"] = SL.GLEV[0]
    names = sys.argv[sys.argv.index("--thin") + 1].split(",") if "--thin" in sys.argv else ["roller", "horn", "ring2"]
    BOX["names"] = [] if "--no-thin" in sys.argv else names
    BOX["at"] = sys.argv[sys.argv.index("--at") + 1] if "--at" in sys.argv else "truncate"
    V.retarget(P); t = time.time()
    res = V.wear(P, which, False, None)
    keep = ("fit_fast", "frozen", "mode", "n", "why", "parts_ib14", "overhead", "dK_lim", "why_lim", "contacts")
    out = {k: res.get(k) for k in keep}
    out["audit"] = {k: (res.get("audit") or {}).get(k) for k in ("gap_near1", "near1_poses", "gap_near2", "near2_poses", "near_touch_min_mm")}
    out.update(id="desmo-slipper-knuckle-3r", wear=which, exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets,
               thinned=BOX.get("info"), thin_names=BOX["names"], thin_at=BOX["at"], blend=True, glev_used=[r.get("glev") for r in SL.REC[-3:]],
               secs=round(time.time() - t, 1), tool="tools/alignment_density_rewear_desmo.py",
               note="verifier harness unchanged (--blend); thinning = tools/sample_density.py _thin at 2 mm on the fitted shape before the wear")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: out.get(k) for k in ("wear", "frozen", "thinned", "sets", "secs")}
                     | {"pib": {k: (out.get("parts_ib14") or {}).get(k) for k in ("roller", "horn", "ring2")}}, default=float))
