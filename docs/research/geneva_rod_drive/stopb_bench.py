"""Workspace cost of moving K's stop B earlier (lobe-skin candidate (i), docs/research/geneva-rod-gen5_fix.md section 2): the
verifier's own harness (docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py, CorrModel + BEST, frozen wear on Bench(110,360)
exact, continuity flood fill) with ONLY a1max changed. a1max sets stop B (the model's law ends where |dK| passes
dKB = psi(a1max) - psiA, `why_end` "stopB"); the q2 dowel stop B moves with the law's end.

    CB_EXACT=1 python3 docs/research/geneva_rod_drive/stopb_bench.py <a1max> <out.json>
a1max 58.3565 = as verified (dK at stop B 53.42); 57.1226 -> 50, 56.064 -> 47, 54.9699 -> 44, 53.458 -> 40 deg (bk1 / bk2 of BEST).
"""
import importlib.util, json, os, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sp = importlib.util.spec_from_file_location("geneva_verify_stopb", os.path.join(REPO, "docs", "concepts", "verify", "geneva-tail-knuckle-pinknee-3r.py"))
VF = importlib.util.module_from_spec(sp); sys.argv = sys.argv[:1] + sys.argv[1:]; a1, path = float(sys.argv[1]), sys.argv[2]; sys.argv = sys.argv[:1]
sp.loader.exec_module(VF)
t = time.time(); P = dict(VF.G.PARAMS, **VF.BEST); P["a1max"] = a1
out = VF.frozen_wear(VF.CorrModel, P, "bench", flood=True)
out.update(a1max=a1, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
json.dump(out, open(path, "w"), indent=1, default=float)
print(json.dumps(dict(a1max=a1, frozen=out["frozen"], near1=out["audit"].get("gap_near1"), drive=out["drive"],
                      conn=(out.get("connected") or {}).get("connected_full"), secs=out["secs"]), default=float))
