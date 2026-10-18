"""Stop-refusal side reading (audit proposal B, not a ruled gate), re-measured independently: wear the k33 KIT (no J3 dowel)
frozen exact on Bench(110,360), read the 6 poses cell B's dowel refuses (skipcheck: 343 372 399 423 426 448), and re-score cell
B's on-file per-pose dump with every refused pose that is a kit contact counted as an evaluated contact."""
import importlib.util, json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
sp = importlib.util.spec_from_file_location("fo_side", os.path.join(REPO, "docs/concepts/models/freek-oracle-route-knuckle-4r.py"))
FO = importlib.util.module_from_spec(sp); sp.loader.exec_module(FO)
import alignment_paired as AP
WEAR = sys.argv[1] if len(sys.argv) > 1 else "bench"
HERE = os.path.dirname(os.path.abspath(__file__))
REF = [r["i"] for r in json.load(open(os.path.join(HERE, f"reverify_skip_{WEAR}.json")))["recs"] if r["hit"] is None]
P = FO.params({}); P.pop("_seed", None); FO.ODesign.SLOT55 = False; FO.ODesign.TAB = None
fitB = FO.RM.PV.fast_bench(60, 160); B = FO.RM.PV.held_bench() if WEAR == "held" else FO.CB.Bench(n_clip=110, n_ws=360)
Mk, fitr, M1, _ = FO.RM.freeze(fitB, B, dict(P), FO.KModel); rk = Mk.run()
kit = {k: rk[k] for k in FO.KEYS}
st = {}
for i in REF:
    r = B.res[i]
    mm = None if r is None else min(float(np.min(r)), float(Mk.cmin.get(i, 1e9)))
    st[i] = dict(pose={k: B.poses[i][k] for k in ("plane", "elev", "axial")}, kind=B.kind[i], kit_min_mm=None if mm is None else round(mm, 2), kit_why=str(Mk.why[i]))
d = json.load(open(os.path.join(REPO, "docs/alignment/remeasure/freek-oracle-route-knuckle-4r_" + WEAR + "_static_perpose.json")))["poses"]
base = AP.gap_parts(d)
d2 = [dict(p) for p in d]
for i in REF:
    m = st[i]["kit_min_mm"]
    assert not d2[i]["ev"] and d2[i]["plane"] == st[i]["pose"]["plane"] and d2[i]["elev"] == st[i]["pose"]["elev"], (i, d2[i], st[i])
    if m is not None and m < 0: d2[i].update(ev=True, contact=True, taken=False)
side = AP.gap_parts(d2)
out = dict(wear=WEAR, kit=kit, refused=st, cellB_static=base, cellB_side_reading=side)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"reverify_side_{WEAR}.json"), "w"), indent=1, default=float)
print(json.dumps(out, default=float))
