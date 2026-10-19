"""Skeptic re-wear of the crest-knee-3r frozen claim through the verifier's own fit_fast / worn / extra_checks (imported,
unchanged; NO dump written - the verifier's wear() would overwrite the per-pose file). Records per-sample metal of every
taken pose (ws and clip) -> ws in-band 2-14, over-14 share, per-part, overhead floors."""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("ckv2", os.path.join(REPO, "docs/concepts/verify/crest-knee-3r.py")); V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
CB = V.CB; t0 = time.time(); which = sys.argv[1]
P = dict(V.ROW["best_params"]); M1, P2, fit, ji = V.fit_fast(P)
B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
M = V.worn(M1, P2, B); r = M.run()
ex, bad = V.PV.extra_checks(M, B)
for i in bad: B.res[i] = None
rep = B.report()
cmin = getattr(M, "cmin", {}) or {}
def stats(ids):
    d = np.concatenate([np.asarray(B.res[i], float) for i in ids]) if ids else np.zeros(0)
    fl = [min(float(np.min(B.res[i])), float(cmin.get(i, 1e9))) for i in ids]
    return dict(n_taken=len(ids), ib14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                over14=round(float((d > 14).mean()), 4) if len(d) else None, dmax=round(float(d.max()), 2) if len(d) else None,
                floor_lt1=int(sum(f < 1 for f in fl)), floor_lt2=int(sum(f < 2 for f in fl)), floor_lt3=int(sum(f < 3 for f in fl)),
                floors_sorted=[round(f, 2) for f in sorted(fl)][:12])
tk = [i for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0]
el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
out = dict(wear=which, mode=B.mode, report={k: rep[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, removed=len(bad),
           ws=stats([i for i in tk if kind[i] == "ws"]), clip=stats([i for i in tk if kind[i] == "clip"]),
           ws_over140=dict(total=int(((kind == "ws") & (el >= 140)).sum()), **stats([i for i in tk if kind[i] == "ws" and el[i] >= 140])),
           clip_over140=dict(total=int(((kind == "clip") & (el >= 140)).sum()), **stats([i for i in tk if kind[i] == "clip" and el[i] >= 140])),
           ws_over90=dict(total=int(((kind == "ws") & (el >= 90)).sum()), n_taken=int(sum(1 for i in tk if kind[i] == "ws" and el[i] >= 90))),
           secs=round(time.time() - t0, 1))
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float); print(json.dumps(out, default=float))
