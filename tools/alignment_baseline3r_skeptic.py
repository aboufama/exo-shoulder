"""Skeptic re-measures of the baseline-3r alignment audit (2026-10-19), read-only: docs/concepts/models/baseline-3r-kit.py unchanged.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_baseline3r_skeptic.py fit60 <out.json>   # claim, th margin, per-member
        sample counts, hub1 / all-hub true-O20 what-if (cap_dirs call counter reset at EVERY build, not once per wear)
    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_baseline3r_skeptic.py fast <out.json>    # honest, sing_deg 5, q spread
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_baseline3r_skeptic.py wear bench|held <out_dir>
        # the auditor's adapter run with alignment_audit.REM redirected to <out_dir> (never overwrites the audit's files)
Outputs on file: docs/alignment/remeasure/baseline-3r_sk_fit60.json, _sk_fast2.json, _sk_exact.json.
"""
import sys, runpy
SRC = {"fit60": "_fit60", "fast": "_fast", "wear": "_wear"}

_fit60 = r"""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
os.environ.pop("CB_EXACT", None)
sp = importlib.util.spec_from_file_location("bk", REPO + "/docs/concepts/models/baseline-3r-kit.py"); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
K = mod.K
out = {}
B = K.bench(60, 160)
def taken(B): return np.array([B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
def thm(B, P):
    ch = B._kit_last["chain"]; j1 = K.unit(np.asarray(ch.joints["J1"], float)); j3 = K.unit(np.asarray(ch.joints["J3"], float))
    th = np.degrees(np.arccos(np.clip((j1 * j3).sum(-1), -1, 1))); a1, a2 = P["a1"], P["a2"]
    m = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th]); tk = taken(B)
    return dict(min=round(float(m[tk].min()), 3), n=int(tk.sum()), lt5=int((m[tk] < 5).sum()), min_all_ok=round(float(m[np.asarray(ch.ok, bool)].min()), 3))
t = time.time()
r = K.evaluate(B, mod.build, dict(mod.PARAMS), **mod.BASELINE)
ch = B._kit_last["chain"]
out["claim"] = dict(gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], audit=r.get("audit"),
                    inband_member=r.get("inband_member"), th=thm(B, mod.PARAMS), secs=round(time.time() - t, 1),
                    samples={m.name: int(np.asarray(m.dirs if hasattr(m, "dirs") else m.D).reshape(len(B.idx), -1, 3).shape[1]) if False else None for m in ch.members})
# member sample counts
cnt = {}
for m in ch.members:
    for attr in ("dirs", "D", "d"):
        if hasattr(m, attr):
            a = np.asarray(getattr(m, attr)); cnt[m.name] = int(a.shape[1]) if a.ndim == 3 else int(a.shape[0]); break
out["claim"]["samples"] = cnt
out["claim"]["prof_max"] = {k: round(float(np.max(v)), 2) for k, v in B._kit_last["prof"].items() if k.startswith("hub")}
print(json.dumps(out["claim"], default=float), flush=True)
# O20 what-if: hub radii from the claim fit
rad = [float(np.max(B._kit_last["prof"][f"hub{k + 1}"])) for k in range(3)]
orig_cap, orig_build = K.cap_dirs, mod.build
for which in ("hub1", "all"):
    state = {"n": 0}
    def cap(k, rad_=K.HUB_R, step=2.5, r_ref=70.0):
        i = state["n"]; state["n"] += 1
        return orig_cap(k, rad_, step, rad[i] if (which == "all" or i == 0) else r_ref)
    def build(B_, F, p):
        state["n"] = 0; K.cap_dirs = cap
        try: return orig_build(B_, F, p)
        finally: K.cap_dirs = orig_cap
    B2 = K.bench(60, 160); r2 = K.evaluate(B2, build, dict(mod.PARAMS), **mod.BASELINE)
    tk = taken(B2); ev = np.array([x is not None for x in B2.res])
    mins = np.array([float(np.min(x)) if x is not None and len(x) else np.nan for x in B2.res])
    out[which] = dict(gap=r2["gap"], reach=r2["reach"], inband14=r2["inband14"], contact=r2["contact"], audit=r2.get("audit"),
                      taken_lt2=int((tk & (mins < 2)).sum()), taken=int(tk.sum()),
                      prof_max={k: round(float(np.max(v)), 2) for k, v in B2._kit_last["prof"].items() if k.startswith("hub")})
    print(which, json.dumps(out[which], default=float), flush=True)
tk = taken(B); mins = np.array([float(np.min(x)) if x is not None and len(x) else np.nan for x in B.res])
out["claim"]["taken_lt2"] = int((tk & (mins < 2)).sum())
json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
print("DONE", out["claim"]["taken_lt2"])
"""
_fast = r"""
import importlib.util, json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools"); os.environ.pop("CB_EXACT", None)
sp = importlib.util.spec_from_file_location("bk", REPO + "/docs/concepts/models/baseline-3r-kit.py"); mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
K = mod.K; out = {}
for nm, P, kw in [("honest", mod.PARAMS, mod.HONEST), ("sing5", dict(mod.PARAMS, sing_deg=5.0), mod.BASELINE)] + \
                 [(f"q{q}", dict(mod.PARAMS, q=q), mod.BASELINE) for q in (0.6, 0.7, 0.8, 0.9, 0.95, 1.0)]:
    B = K.bench(60, 160); r = K.evaluate(B, mod.build, dict(P), **kw)
    out[nm] = {k: r.get(k) for k in ("gap", "reach", "inband14", "contact", "flips", "collide")}
    print(nm, out[nm], flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
"""
_wear = r"""
import sys, os
sys.path.insert(0, "/home/user/exo-shoulder/tools")
import alignment_audit as AA
AA.REM = sys.argv[2]
import alignment_baseline3r_rewear as BR
BR.run("claim", sys.argv[1], {})
"""

if __name__ == "__main__":
    mode = sys.argv[1]; sys.argv = [sys.argv[0]] + sys.argv[2:]
    exec(compile(globals()[SRC[mode]], f"alignment_baseline3r_skeptic:{mode}", "exec"), {"__name__": "__main__"})
