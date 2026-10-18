"""Auditor adapter (new file, 2026-10-18): re-wear the freek-oracle-route-knuckle-4r FINAL POLISH pick1 for the alignment audit.

It runs tools/alignment_remeasure_freek.py UNCHANGED (the model's own `law` path: fit Bench(60,160) fast -> frozen exact
Bench(110,360) or the held-out set, J2 on its own priced slot, J3 dowel at q3max, the model's own kinematic flood, the
kit's family fold reading in that flood) with two things swapped from outside:
  * the params: the model's own params() (KR.PARAMS + the k33 priced file) with the ROW's recorded polished_params_priced
    laid over them (q3max 84.7705 in the model's q3, smhi / smlo / a1max / bk1 / bk2 / az2 / el2 / wd / wa / b3). This
    path does not go through tools/env_polish.priced or tools/freek_env_polish.py (the polisher's tools); it checks that
    every other key of the nominal pick file equals the model's own value.
  * the output directory: docs/alignment/remeasure/freek_polish_pick1/ (the verified config's re-wear files stay as they are).
After the wear it reads, from the same frozen design (captured from RM.freeze, nothing re-fitted):
  * the stop-refusal side reading (audit proposal B), on its own code: the poses the J3 dowel refuses (the model's
    j3stop2 returns no crossing), worn by the same frozen shape with the dowel removed (q3max dropped), and the gap with
    each refused pose that is a contact without the dowel scored as that contact.
It never edits the model, a bench, a judge or a row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_remeasure_freek_polish.py bench|held
"""
import copy, json, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA  # noqa: E402
import alignment_remeasure_freek as ARF  # noqa: E402

RID = ARF.RID
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
PRICED = dict(ROW["polished_params_priced"])
NOMF = os.path.join(REPO, ROW["polished_params_nominal_file"])
OUTD = os.path.join(AA.REM, "freek_polish_pick1")
CAP = {}


def main(wear):
    t0 = time.time()
    _load0 = AA._load

    def _load(name, path):
        mod = _load0(name, path)
        p0 = mod.params

        def params(over=None):
            P = p0(dict(over or {}, q3max=PRICED["q3max"]))
            nom = json.load(open(NOMF)); diff = {}
            for k, v in nom.items():
                if k in PRICED or k.startswith("_"): continue
                if k not in P or (isinstance(v, (int, float)) and abs(float(P[k]) - float(v)) > 1e-6) or (not isinstance(v, (int, float)) and P[k] != v):
                    diff[k] = [P.get(k), v]
            CAP["nominal_diff_nonpriced"] = diff
            P.update(PRICED); CAP["params"] = {k: P[k] for k in PRICED}
            return P
        mod.params = params
        fr0 = mod.RM.freeze

        def freeze(fitB, B, P, KM):
            out = fr0(fitB, B, P, KM); CAP["Mk"], CAP["B"], CAP["mod"] = out[0], B, mod; return out
        mod.RM.freeze = freeze
        return mod
    AA._load = _load
    AA.REM = OUTD; os.makedirs(OUTD, exist_ok=True)
    ARF.main(wear, PRICED["q3max"])
    AA._load = _load0
    # ---- stop refusal on the captured frozen design (own code; same idea as audit proposal B)
    Mk, B, mod = CAP["Mk"], CAP["B"], CAP["mod"]; KR = mod.KR
    D = Mk.D; Q = Mk.Q
    q, ok, X1, X2, X3, s = KR.KRDesign._ik_phys(D, Q); js = D.j3stop2(Q, q, ok, s)
    refused = sorted(i for i, v in js.items() if v is None)
    rows = []; res1 = list(B.res)
    if refused:
        W2 = copy.copy(B); W2.idx = np.asarray(B.idx)[refused]; W2.kind = [B.kind[i] for i in refused]; W2.clip = [B.clip[i] for i in refused]
        W2.poses = [B.poses[i] for i in refused]; W2.res = [None] * len(refused); W2._skin = {}; W2._ex = {}; W2._frames = {}
        if getattr(B, "grid", None) is not None:
            W2.grid = B.grid[refused]; W2._V = B._V[refused] if getattr(B, "_V", None) is not None else None
        P2 = dict(Mk.p); P2.pop("q3max", None); Mkit = type(Mk)(W2, P2); Mkit.run()
        for k, i in enumerate(refused):
            r = W2.res[k]; m = None if r is None or not len(r) else float(min(np.min(r), Mkit.cmin.get(k, 1e9)))
            rows.append(dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                             taken_with_dowel=B.res[i] is not None, kit_min_mm=None if m is None else round(m, 2)))
            if m is not None and m < 0 and B.res[i] is None: res1[i] = np.array([m])
    r0 = list(B.res); B.res = res1; side = B.report(); B.res = r0; base = B.report()
    kc = [r for r in rows if r["kit_min_mm"] is not None and r["kit_min_mm"] < 0 and not r["taken_with_dowel"]]
    out = dict(id=RID, wear=wear, adapter="tools/alignment_remeasure_freek_polish.py (wraps tools/alignment_remeasure_freek.py)",
               params=CAP["params"], nominal_diff_nonpriced=CAP["nominal_diff_nonpriced"],
               static_gap=base["gap"], refused=len(refused), refused_kit_contacts=len(kc),
               refused_kit_contact_depth_mm=round(-sum(r["kit_min_mm"] for r in kc), 2),
               gap_refusals_as_contacts=side["gap"], side_report={k: side[k] for k in ("gap", "reach", "follow", "inband14", "contact")},
               refused_rows=rows, secs=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(OUTD, f"{RID}_{wear}_stoprefusal.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "refused_rows"}, default=float))


if __name__ == "__main__":
    main(sys.argv[1])
