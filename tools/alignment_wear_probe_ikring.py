"""Alignment probe for ikring-thinstack-knuckle-4r (read-only on the claim): wear the frozen claim's held-out CLIP frames.

Why: the design's held reading on file (docs/concepts/verify/ikring-thinstack-knuckle-4r/ik_heldws_specrule.json) wore every
held ws pose but only every 100th held clip frame (3 of 202), so its held in-band / follow (0.9713 on 3 frames) is not a
measurement, and the chain-only in-band the claim's gate uses was never read held out. The IK keeps every clip frame at
psi = 0 (lead-first rule, model docstring), so the claim's held clip frames ARE the ring-parked wear of those frames.
This probe runs the model's own fit() / subbench() / wear_phi() UNCHANGED at psi = 0 on all held clip frames and prints
phi40's summary (chain-only gate, pooled in-band, 1 / 2 mm readings) + the per-frame min metal. Changes no score, no row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_ikring.py <out.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = "ikring-thinstack-knuckle-4r"


def main(outp):
    t0 = time.time()
    sp = importlib.util.spec_from_file_location("ikring_probe", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
    M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
    base = dict(M.CLAIM); F = M.fit(base); hw = dict(base)
    os.environ["CB_EXACT"] = "1"
    Bf = M.AA.held_bench(); kd = np.array(Bf.kind); cl = np.nonzero(kd == "clip")[0]
    Bs = M.subbench(Bf, cl)
    o, S = M.wear_phi(F, Bs, np.zeros(len(M.AA.Z0["HG"])), hw)
    s = M.P4.summary(o); B = S["B"]
    mm = [None if B.res[j] is None else float(np.min(B.res[j])) for j in range(len(B.idx))]
    m = np.array([x for x in mm if x is not None])
    out = dict(id=ID, wear="held clip frames, psi = 0 (the claim's IK keeps clip frames at psi 0)", n_clip=int(len(cl)), fit=F["fit"],
               summary=s, ideal=S["ideal"], clip_min_mm=dict(under0=int((m < 0).sum()), under1=int((m < 1).sum()), under2=int((m < 2).sum()),
                                                            under3=int((m < 3).sum()), median=round(float(np.median(m)), 2), min=round(float(m.min()), 3)),
               frames=[dict(i=int(j), min_mm=None if mm[j] is None else round(mm[j], 3), elev=float(B.poses[j]["elev"])) for j in range(len(B.idx))],
               secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "frames"}, default=float), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
