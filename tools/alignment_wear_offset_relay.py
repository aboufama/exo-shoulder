"""Alignment re-wear adapter for the proxtrack relay family (offset-shortcar-relay-4r and any row whose model exposes
prepare(base, nc, nw, exact) / wear(S, hw) / perpose(S) / summary(o) and CLAIM_PARENT, like
docs/concepts/models/offset-shortcar-relay-4r.py). tools/alignment_audit.py remeasure needs a model with frozen() and a
pin-knee audit(M, B) to wrap; this family has neither, so this adapter re-wears the row's claim with the model UNCHANGED
(its own prepare / wear / perpose, the row's best_params on top of the model's CLAIM_PARENT, as the row's verifier does)
and runs the auditor's deep_audit(M, B) on the wear the model leaves behind (near-touch at 1 / 2 / 3 mm on B.res, the
clip-frame metal histogram, the gap with the band read 3-14 mm, per-pose coordinate spans).

Writes docs/alignment/remeasure/<id>_<wear>.json (frozen / deep / parts_ib14 / relay) and <id>_<wear>_perpose.json
(the model's per-pose dump with frozen.gap = the row's claimed reading, the chain-only gate, so the T5 depth check can
pair it with the claim; frozen.gap_plain is the plain reading). Nothing here changes a bench, a model or a score.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_offset_relay.py offset-shortcar-relay-4r bench|held
"""
import importlib.util, json, os, subprocess, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
REM = os.path.join(REPO, "docs", "alignment", "remeasure")


def main(rid, wear):
    os.environ["CB_EXACT"] = "1"
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", rid + ".json")))
    sp = importlib.util.spec_from_file_location("aw_" + rid.replace("-", "_"), os.path.join(REPO, "docs", "concepts", "models", rid + ".py"))
    OM = importlib.util.module_from_spec(sp); sp.loader.exec_module(OM)
    import alignment_audit as AU
    hw = {k: v for k, v in (row.get("best_params") or {}).items() if k in OM.PT.DEF}
    base = dict(OM.CLAIM_PARENT, **hw)
    t0 = time.time()
    S = OM.prepare(base, 110, 360, exact=True) if wear == "bench" else OM.prepare(base, -1, -1, exact=True)
    o = OM.wear(S, base); sm = OM.summary(o)
    M, B = S["M"], S["B"]
    deep = AU.deep_audit(M, B)
    # per-part in-band over taken clip frames: chain parts by their sample blocks (rigid, then link sets: the model's
    # chain order), the relay's skin-facing hardware (shell inner face, bracket underside, flange) as one block
    names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, (m, X) in list(M.rigid.items()) + list(M.link_pts.items())]
    nC = int(sum(sizes)); acc = {n: [] for n in names}; acc["relay_hw_inband"] = []
    for i in range(len(B.idx)):
        if B.kind[i] != "clip" or B.res[i] is None or float(np.min(B.res[i])) < 0: continue
        r = np.asarray(B.res[i], float); k = 0
        for n, s in zip(names, sizes): acc[n].append(r[k:k + s]); k += s
        acc["relay_hw_inband"].append(r[nC:])
    pib = {}
    for n, L in acc.items():
        a = np.concatenate(L) if L else np.zeros(0)
        pib[n] = [round(float(((a >= 2) & (a <= 14)).mean()), 4) if len(a) else 0.0, round(float(np.median(a)), 2) if len(a) else None,
                  int(len(a) / max(1, len(L))) if L else 0]
    # taken poses with metal < 1 / 2 / 3 mm (workspace and overhead), deepest contacts
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    mins = {i: float(np.min(B.res[i])) for i in tk}
    shell = {f"lt{t:g}": dict(all=sum(1 for i in tk if mins[i] < t), ws=sum(1 for i in tk if mins[i] < t and kind[i] == "ws"),
                              overhead=sum(1 for i in tk if mins[i] < t and kind[i] == "ws" and el[i] >= 140)) for t in (1.0, 2.0, 3.0)}
    ws = kind == "ws"; take = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    reach_bands = {f"elev>={e}": [int((ws & take & (el >= e)).sum()), int((ws & (el >= e)).sum())] for e in (90, 120, 140, 160)}
    gate = o.get("gate_gap"); plain = o["wear"]["gap"]
    out = dict(id=rid, wear=wear, params=base, adapter="tools/alignment_wear_offset_relay.py",
               frozen=dict(gap=gate, gap_plain=plain, gate_chain_only=gate, reach=o["wear"]["reach"], follow=o["wear"]["follow"],
                           inband14=o["wear"]["inband14"], inband14_chain_only=o["hw"].get("ib14_chain_only"), contact=o["wear"]["contact"]),
               summary=sm, deep=deep, parts_ib14=pib, metal_shell_taken=shell, reach_by_elev=reach_bands,
               relayed=o.get("relayed"), continuity={k: v for k, v in (o.get("continuity") or {}).items() if k != "dropped"},
               jams=len(o["hw"]["jams"]), contacts=o["contacts"], secs=round(time.time() - t0, 1), exact=True,
               git=subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip())
    os.makedirs(REM, exist_ok=True)
    json.dump(out, open(os.path.join(REM, f"{rid}_{wear}.json"), "w"), indent=1, default=float)
    pp = OM.perpose(S); pp.update(wear=wear, params=base, exact=True, adapter=out["adapter"],
                                  frozen=dict(gap=gate, gap_plain=plain, note="gap = the row's claimed chain-only gate; same contact set as plain"))
    json.dump(pp, open(os.path.join(REM, f"{rid}_{wear}_perpose.json"), "w"), default=float)
    print(json.dumps(dict(id=rid, wear=wear, summary=sm, deep={k: v for k, v in deep.items() if k != "coord_spans"}, shell=shell,
                          reach_by_elev=reach_bands, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
