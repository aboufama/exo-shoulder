#!/usr/bin/env python3
"""Alignment re-wear (read-only adapter, 2026-10-19): ikring-distalshell-knuckle-4r's HELD reading with its OWN k-table.

Why: the held reading on file (docs/concepts/verify/ikring-distalshell-knuckle-4r/ik_heldws.json, gate 15.62, 32 contacts,
20 of them hardware at the shell ends) wears pick 1's held IK choice (ikring-thinstack-knuckle-4r/ik_heldws.json, chosen
for pick 1's metal) on this design's short knee + distal shell. Its ik.mismatch lists the 20 held ws poses where pick 1's
table said 'take at k' and this metal says contact / lost. The claim bench had the same defect (11.76 imported) and was
fixed by the model's own fixk() (10.54). This adapter runs exactly that fixk procedure on the held set (the model's
fixk() is hard-wired to Bench(110,360)): this design's own k-table k = 0..PHI on the held mismatches, the take-only rule
(max min metal among takes, ties -> smaller k; no take -> 0), then one final wear of the held ws sample through pick 1's
ik_run(..., "heldws", choice_from=...). The model, the bench, the kit and the row are run UNCHANGED; caches go to a
private scratch dir (VDIR redirected; the verifier's rebuilt flood for this knee is copied in), outputs to
docs/alignment/remeasure/. It never changes a score.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_ikring_distal_heldfix.py <scratch_vdir>
"""
import importlib.util, json, os, shutil, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID = "ikring-distalshell-knuckle-4r"
V = os.path.join(REPO, "docs", "concepts", "verify", ID)
OUT = os.path.join(REPO, "docs", "alignment", "remeasure")


def main(scratch):
    os.makedirs(scratch, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    fl = "ikflood_PHI40_t8.5_a243_k2.5.json"
    if not os.path.exists(os.path.join(scratch, fl)): shutil.copy(os.path.join(V, "verifier", fl), os.path.join(scratch, fl))
    sp = importlib.util.spec_from_file_location("ikring_distal_audit", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
    MD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MD)
    IK, PT, OS, P4, AA, CB = MD.IK, MD.PT, MD.OS, MD.P4, MD.AA, MD.CB
    MD.VDIR = IK.VDIR = PT.VDIR = OS.VDIR = P4.VDIR = scratch            # never write into the design's verify dir
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))
    base = dict(MD.CLAIM); base.update({k: v for k, v in row["best_params"].items() if k not in ("IK_RULE",)})
    prev = json.load(open(os.path.join(V, "ik_heldws.json"))); mis = [int(j) for j in prev["ik"]["mismatch"]]
    F = MD.fit(base); hw = dict(base); os.environ["CB_EXACT"] = "1"; KS = IK.kgrid(float(F["rp"]["PHI"]))
    Bf = AA.held_bench(); kd0 = np.array(Bf.kind)
    Bf = IK.subbench(Bf, np.r_[np.nonzero(kd0 == "clip")[0][::100], np.nonzero(kd0 == "ws")[0]]); kd = np.array(Bf.kind)
    cl = np.nonzero(kd == "clip")[0][:6]; sel = np.r_[cl, np.array(mis, int)]; Bs = IK.subbench(Bf, sel); nZ = len(AA.Z0["HG"]); tab = {}
    for k in KS:
        phi = np.zeros(nZ); phi[Bf.idx[mis]] = k; o_, Sk = IK.wear_phi(F, Bs, phi, hw); mm, wy = IK.pose_state(Bs, Sk["M"])
        tab[k] = [mm[len(cl) + q] for q in range(len(mis))]; print(json.dumps(dict(k=k, mm=tab[k])), flush=True)
    choice = dict(prev["ik"]["choice"]); fixed = {}
    for q, j in enumerate(mis):
        tks = [(tab[k][q], k) for k in KS if tab[k][q] is not None and tab[k][q] >= 0]
        if tks: m, k = max(tks, key=lambda x: (round(x[0], 6), -x[1])); c = dict(k=k, mm=m, n_take_k=len(tks), takes={str(kk): round(mv, 2) for mv, kk in tks})
        else: c = dict(k=0.0, mm=tab[0.0][q], n_take_k=0, takes={}, reverted=True)
        if str(j) in choice or c["k"] != 0: choice[str(j)] = c
        fixed[str(j)] = dict(k=c["k"], mm=c["mm"], n_take_k=c["n_take_k"], table={str(k): tab[k][q] for k in KS})
    outp = os.path.join(OUT, ID + "_heldfix.json"); tf = outp.replace(".json", "_choice.json")
    json.dump(dict(ik=dict(choice=choice, k0=prev["ik"]["k0"]), fixed=fixed), open(tf, "w"), default=float)
    o = IK.ik_run(base, "heldws", outp, choice_from=tf); o["ik"]["fixk"] = fixed
    o["audit_note"] = ("alignment re-wear: held ws sample (every held ws pose + every 100th held clip frame) with this design's own "
                       "k-table on the 20 imported-table mismatches (tools/alignment_ikring_distal_heldfix.py); model unchanged")
    json.dump(o, open(outp, "w"), default=float)
    print(json.dumps(dict(done=True, gate=o.get("gate_gap"), wear=o.get("wear"), contacts=len(o.get("contacts") or []))), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
