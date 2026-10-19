"""Alignment probe for ikring-distalshell-knuckle-4r (read-only on the claim): wear the frozen claim's held-out CLIP frames.

Adapter of tools/alignment_wear_probe_ikring.py (pick 1) to this design's model (short knee + distal shell; it imports
pick 1's machinery read-only). Why: the held reading on file (docs/concepts/verify/ikring-distalshell-knuckle-4r/
ik_heldws.json) wore every held ws pose but only every 100th held clip frame (3 of 202), so its held in-band / follow
is not a measurement and the chain-only in-band the gate uses was never read held out. The IK keeps every clip frame at
psi = 0 (lead-first rule), so the held clip frames at psi 0 ARE the claim's held clip wear. Runs the model's own fit() and
pick 1's subbench() / wear_phi() UNCHANGED at psi = 0 on all held clip frames; caches redirected to a scratch dir.
Changes no score, no row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_ikring_distal.py <scratch_vdir> <out.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = "ikring-distalshell-knuckle-4r"


def main(scratch, outp):
    t0 = time.time(); os.makedirs(scratch, exist_ok=True)
    sp = importlib.util.spec_from_file_location("ikring_distal_probe", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
    MD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MD)
    IK = MD.IK; MD.VDIR = IK.VDIR = MD.PT.VDIR = MD.OS.VDIR = MD.P4.VDIR = scratch
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))
    base = dict(MD.CLAIM); base.update({k: v for k, v in row["best_params"].items() if k != "IK_RULE"})
    F = MD.fit(base); hw = dict(base); os.environ["CB_EXACT"] = "1"
    Bf = MD.AA.held_bench(); kd = np.array(Bf.kind); cl = np.nonzero(kd == "clip")[0]
    Bs = IK.subbench(Bf, cl)
    o, S = IK.wear_phi(F, Bs, np.zeros(len(MD.AA.Z0["HG"])), hw)
    s = MD.P4.summary(o); B = S["B"]
    mm = [None if B.res[j] is None else float(np.min(B.res[j])) for j in range(len(B.idx))]
    m = np.array([x for x in mm if x is not None])
    out = dict(id=ID, wear="held clip frames, psi = 0 (the claim's IK keeps clip frames at psi 0)", n_clip=int(len(cl)), fit=F["fit"],
               summary=s, ideal=S.get("ideal"), clip_min_mm=dict(under0=int((m < 0).sum()), under1=int((m < 1).sum()), under2=int((m < 2).sum()),
                                                                 under3=int((m < 3).sum()), median=round(float(np.median(m)), 2), min=round(float(m.min()), 3)),
               frames=[dict(i=int(j), min_mm=None if mm[j] is None else round(mm[j], 3), elev=float(B.poses[j]["elev"])) for j in range(len(B.idx))],
               secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "frames"}, default=float), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
