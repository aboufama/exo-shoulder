#!/usr/bin/env python3
"""Alignment audit instrument (new file; the model, verifier, bench and tools/sample_density.py run UNCHANGED): the exact
confirmation of the S6 density re-weight for desmo-conecut-knuckle-3r, through the VERIFIER's own harness (--blend IK, the
verified 18.98's wear: docs/concepts/verify/desmo-conecut-knuckle-3r.py wear).

Why a new file: the row's recorded confirmation command (`CB_EXACT=1 python3 tools/sample_density.py rewear
desmo-conecut-knuckle-3r bench|held`, tools/sample_density.py 2026-10-18.1) crashes before any wear: fitted() calls
_thin(M1, *thin) with thin = (names, step, wear), three arguments into _thin(M, names, step) (TypeError, reproduced by the
2026-10-18 ~22:40 audit of this row). This adapter does the same thinning (tools/sample_density.py _thin: greedy 2 mm
Poisson-disc subsample of the named parts, in place) when the Frozen wear model's fit() calls _truncate(), i.e. after it took
the fitted M1's rigid / link_pts and before any wear pose is scored; the fast fit itself runs unthinned, so the frozen shape
is the claim's (check: every unthinned part's in-band equals the verifier's file). Contact samples (M.contact) are not
touched. Same approach as tools/alignment_density_rewear_desmo.py (desmo-slipper), written for this row's verifier.

  CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_density_rewear_conecut.py <bench|held> <out.json>
        [--thin horn,ring2] [--no-thin] [--glev G --set a_s=9.8 --set psi=150]
--glev wears the plate-clearing stage-1 level through tools/alignment_desmo_s1level.py (glev re-applied after the model's
clamp; ring2 in link 2's true frame unless --nofix, as that tool's 20.50 re-wear ran).
"""
import importlib.util, json, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
if "--blend" not in sys.argv: sys.argv.append("--blend")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


SD = _load("sd_for_conecut_rewear", os.path.join(REPO, "tools", "sample_density.py"))
GL = "--glev" in sys.argv
if GL:
    S1 = _load("s1_for_conecut_rewear", os.path.join(REPO, "tools", "alignment_desmo_s1level.py"))
    V, DC = S1.V, S1.DC
else:
    S1 = None
    V = _load("desmoconecut_verify_density", os.path.join(REPO, "docs", "concepts", "verify", "desmo-conecut-knuckle-3r.py"))
    DC = V.DC
BOX = {}
_tr0 = DC.DCModel._truncate


def _truncate(self, *a, **k):
    if type(self).__name__ == "Frozen" and not BOX.get("done") and BOX.get("names"):
        BOX["info"] = SD._thin(self, BOX["names"], SD.KIT_STEP); BOX["done"] = True
    return _tr0(self, *a, **k)


DC.DCModel._truncate = _truncate

if __name__ == "__main__":
    which, path = sys.argv[1], sys.argv[2]
    P = dict(V.BEST); sets = {}
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_); sets[k_] = float(v_)
    if GL: P["glev"] = S1.GLEV; sets["glev"] = S1.GLEV
    names = sys.argv[sys.argv.index("--thin") + 1].split(",") if "--thin" in sys.argv else ["horn", "ring2"]
    BOX["names"] = [] if "--no-thin" in sys.argv else names
    t = time.time()
    res = V.wear(P, which, False, None)
    keep = ("fit_fast", "frozen", "mode", "n", "n_taken", "why", "overhead", "near1", "near2", "minmetal", "contacts", "v1_fit_gates", "v3_th_margin")
    out = {k: res.get(k) for k in keep}
    out["parts_ib14"] = (res.get("claim_frozen_out") or {}).get("parts_ib14")
    out.update(id="desmo-conecut-knuckle-3r", wear=which, exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets,
               thinned=BOX.get("info"), thin_names=BOX["names"], thin_at="Frozen._truncate", blend=True,
               glev_used=(S1.USED[-3:] if GL else None), fix_ring_frame=(S1.RFT.FIX if GL else False),
               secs=round(time.time() - t, 1), tool="tools/alignment_density_rewear_conecut.py",
               note="verifier harness unchanged (--blend); thinning = tools/sample_density.py _thin at 2 mm on the fitted shape before the wear")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: out.get(k) for k in ("wear", "frozen", "fit_fast", "thinned", "sets", "secs")}
                     | {"pib": {k: (out.get("parts_ib14") or {}).get(k) for k in ("horn", "ring2", "hub2", "crank")}}, default=float))
