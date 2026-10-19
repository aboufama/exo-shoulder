"""Alignment probe (read-only): per-part in-band of a kit model on Bench(60,160) fast, and the gap with the base bridge
(static, scapula-fixed metal) or every non-moving part left out - how much of the in-band the moving mechanism earns.
The model runs UNCHANGED through K.evaluate. OUTP=<out.json> OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_bridge_share.py
(written for clavicular-front-route, 2026-10-19 audit)."""
import json, os, sys, importlib.util
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
import alignment_audit as AA
sp = importlib.util.spec_from_file_location("cfr", REPO + "/docs/concepts/models/clavicular-front-route.py"); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
K = mod.K
row = json.load(open(REPO + "/docs/concepts/rows/clavicular-front-route.json")); P = dict(mod.PARAMS, **row["best_params"])
B = K.bench(60, 160); r = K.evaluate(B, mod.build, dict(P)); L = B._kit_last; ch = L["chain"]; pts = L["pts"]
take = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
clip = np.array([k == "clip" for k in B.kind]); sel = np.nonzero(take & clip)[0]
names = [m.name for m in ch.members]; sizes = [pts[n].shape[1] for n in names]
out = dict(sizes=dict(zip(names, sizes)))
o = 0; per = {}
D = np.stack([B.res[i] for i in sel])                     # (n, k) in member order
for n, s in zip(names, sizes):
    d = D[:, o:o + s]; o += s
    per[n] = dict(n=s, ib14=round(float(((d >= 2) & (d <= 14)).mean()), 4), med=round(float(np.median(d)), 2))
out["per"] = per
def ib(keep):
    cols = np.concatenate([np.arange(sum(sizes[:j]), sum(sizes[:j + 1])) for j, n in enumerate(names) if n in keep])
    d = D[:, cols]; return float(((d >= 2) & (d <= 14)).mean())
allp = ib(names); nob = ib([n for n in names if not n.startswith("bridge")]); mech = ib([n for n in names if n in ("hub1", "hub2", "hub3", "link1", "link2")])
out["inband_all"] = round(allp, 4); out["inband_no_bridge"] = round(nob, 4); out["inband_mechanism_only"] = round(mech, 4)
g = lambda x: AA.gap_of(x, r["follow"], r["reach"], r["contact"])
out["gap_all"] = g(allp); out["gap_no_bridge"] = g(nob); out["gap_mech_only"] = g(mech)
out["part_weighted_ib14"] = round(float(np.mean([per[n]["ib14"] for n in names])), 4)
q = np.asarray(ch.q, float)[take]
out["q_span_deg"] = {f"J{j+1}": [round(float(q[:, j].min()), 1), round(float(q[:, j].max()), 1)] for j in range(q.shape[1])}
# J1 hub level and where it sits relative to GH in the scapula frame
out["hub_levels_mm"] = {n: round(float(np.max(L["prof"][n])), 1) for n in names if n.startswith("hub")}
print(json.dumps(out, indent=1))
json.dump(out, open(os.environ["OUTP"], "w"), indent=1)
