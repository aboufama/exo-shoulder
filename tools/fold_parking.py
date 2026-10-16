"""Hub parking on the fold frontier (docs/concepts/fold-sph3r.md): for every frontier.json layout with a1 + a2 in 85-140
(both branches) plus two reference 3R axis sets, the K3 march requirement of each hub's CENTRE ray (J1, J2, J3 through
GH) over the bench poses where the chain closes (fold margin 10 deg). A rigid hub sits at the max over poses (400 = a
pose where the ray never clears skin within 220 mm: the ray runs inside the arm / trunk); it is in band in pose i
roughly iff max - req_i <= 12. Orientation + centre ray only: a necessary condition, links not included.

    OMP_NUM_THREADS=1 python3 tools/fold_parking.py docs/research/fold/hub_parking.json
"""
import json, os, sys, numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K
B = K.bench(60, 160); F = K.frames(B); ws = np.array([k == "ws" for k in B.kind])
fr = json.load(open(os.path.join(REPO, "docs/research/fold/frontier.json")))
rows = [r for r in fr["rows"] if 85 <= r["a1"] + r["a2"] <= 140]
extra = [dict(a1=80.7101, a2=62.9326, az1=0.6452, el1=76.8246, wd=93.8197, wa=-4.2, tag="k1530"),
         dict(a1=76.90180446920043, a2=66.74921235407174, az1=2.4305071427308924, el1=80.67633718429899, wd=86.32769021001913, wa=21.829657347343378, tag="champion")]
out = []
P = len(B.idx)
for r in rows + extra:
    p1 = F.S(K.bvec(r["az1"], r["el1"])); p3 = F.HG(K.wdir(r["wd"], r["wa"]))
    for s in (1, -1):
        p2, ok, _ = K.closure(p1, p3, r["a1"], r["a2"], s, margin_deg=10.0)
        Pi = np.nonzero(ok)[0]
        if not len(Pi): continue
        e = dict(a1=r["a1"], a2=r["a2"], az=r["az1"], el=r["el1"], wd=r["wd"], wa=r["wa"], sigma=s, tag=r.get("tag"), closure=round(float(ok.mean()), 3))
        for name, ax in (("hub1", p1), ("hub2", p2), ("hub3", p3)):
            R = K.requirement(B, Pi, ax[Pi]); R = np.where(np.isfinite(R), R, 400.0)
            mx = R.max(); e[name] = dict(max=round(float(mx), 1), med=round(float(np.median(R)), 1), p90=round(float(np.percentile(R, 90)), 1),
                                        inband=round(float((mx - R <= 12).mean()), 3), inf=round(float((R >= 399).mean()), 3),
                                        best_q90_inband=round(float((np.percentile(R, 90) - R[R <= np.percentile(R, 90)] <= 12).mean()), 3))
        out.append(e)
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(len(out))
