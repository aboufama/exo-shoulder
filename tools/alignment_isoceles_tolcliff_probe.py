"""Probe (new file, alignment audit 2026-10-19, round 501 slice r501-A) for isoceles-shortdyad-pinknee-3r: two wearer
readings the verifier's files do not hold.

  1. NEW-tolcliff, metal-touch reading. docs/concepts/verify/isoceles-shortdyad-pinknee-3r_tolprobe.py counts taken poses
     whose knee-vs-E-strap clearance (every joggle slice) is below the 0.15 mm running gap + d (running-gap reading).
     This probe records the clearance distribution itself and the frozen gap when the poses whose clearance is below d
     (metal touch at a strap-level error d) are refused, for d = 0.2 / 0.3 / 0.4 / 0.5 mm, plus the running-gap reading
     for comparison. Same harness, same claimed parameters, same clearance formula as the verifier's tolprobe (imported).
  2. Conditioning drop. The round-501 judge's red-team number |u1 . (u2 x w)| (H1's worst 0.233): the frozen gap when the
     taken poses below 0.233 are refused (what the claim would read at H1's conditioning floor), and the det histogram.

The models and the verifier run UNCHANGED (imported; nothing is written to their files). Report only: this changes no
score, no gap and no row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_isoceles_tolcliff_probe.py bench|held
        -> docs/alignment/remeasure/isoceles-shortdyad-pinknee-3r_<wear>_tolcliff.json
"""
import importlib.util, json, os, subprocess, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RID = "isoceles-shortdyad-pinknee-3r"
_sp = importlib.util.spec_from_file_location("iso_v_for_tolcliff", os.path.join(REPO, "docs", "concepts", "verify", RID + ".py"))
I = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(I)
V, CB, S = I.V, I.CB, I.S


def main(which):
    t0 = time.time()
    M1, P2, fit, ji = V.fit_fast(dict(I.P))
    B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
    M = V.worn(M1, P2, B); r0 = M.run()
    tk = V.taken_list(B); h = S.T_LINK / 2; clr = {}
    sl = M._knee_slices()
    for i in tk:                                                     # the verifier tolprobe's clearance, verbatim
        R3, t3 = M.T(M.Emid[0], i)
        Em = M.Emid[1] @ R3.T + t3; R6, t6 = M.T(6, i)
        clr[i] = min(float(M.sd_box(Em, R6 @ c + t6, R6 @ Rk, hf).min()) - h for c, Rk, hf in sl)
    cv = np.array(list(clr.values()))
    res0 = list(B.res); base = B.report()

    def refuse(ids):
        B.res = list(res0)
        for i in ids: B.res[i] = None
        r = B.report(); B.res = list(res0)
        return dict(poses=len(ids), gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"])
    touch = {f"{d:g}": refuse([i for i, v in clr.items() if v < d]) for d in (0.2, 0.25, 0.3, 0.4, 0.5)}
    running = {f"{d:g}": refuse([i for i, v in clr.items() if v < M.ADJ + d]) for d in (0.05, 0.1, 0.15)}
    # conditioning |u1 . (u2 x w)| (the verifier's formula, verbatim)
    D = M.D; u1, u2, u3 = D.u; w = np.einsum("nij,j->ni", M.Q, u3); p2 = S.rotm(u1, M.q[:, 0]) @ u2
    det = np.abs(np.einsum("j,nj->n", u1, np.cross(p2, w)))
    kind = np.array(B.kind); el = np.array([p["elev"] for p in B.poses])
    low = [i for i in tk if det[i] < 0.233]
    cond = dict(det_min=round(float(det[tk].min()), 4), below_h1=len(low), below_h1_clip=int(sum(kind[i] == "clip" for i in low)),
                below_h1_poses=[dict(i=int(i), kind=str(kind[i]), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                                     det=round(float(det[i]), 4)) for i in sorted(low, key=lambda j: det[j])],
                refused_below_h1=refuse(low), refused_below_0p20=refuse([i for i in tk if det[i] < 0.20]),
                det_hist={f"{a}-{b}": int(sum(1 for i in tk if a <= det[i] < b)) for a, b in ((0, .15), (.15, .2), (.2, .233), (.233, .3), (.3, .5), (.5, 1.01))})
    try: git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: git = None
    out = dict(id=RID, wear=which, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", base={k: base[k] for k in ("gap", "reach", "follow", "inband14", "contact")},
               taken=len(tk), adj_mm=M.ADJ,
               knee_strap_clearance=dict(min=round(float(cv.min()), 4), p10=round(float(np.percentile(cv, 10)), 4), median=round(float(np.median(cv)), 4),
                                         max=round(float(cv.max()), 4),
                                         hist={f"{a}-{b}": int(((cv >= a) & (cv < b)).sum()) for a, b in ((0, .2), (.2, .25), (.25, .26), (.26, .3), (.3, .35), (.35, .5), (.5, 1), (1, 99))},
                                         overhead_taken_min=round(min([clr[i] for i in tk if el[i] >= 140] or [99]), 4)),
               metal_touch_at_strap_error_mm=touch, running_gap_at_strap_error_mm=running, conditioning=cond,
               secs=round(time.time() - t0, 1), git=git,
               note="tools/alignment_isoceles_tolcliff_probe.py: the verifier's harness and clearance formula imported unchanged; report only")
    p = os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_{which}_tolcliff.json"); json.dump(out, open(p, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "conditioning"} | {"cond": {k: v for k, v in cond.items() if k != "below_h1_poses"}}, default=float))


if __name__ == "__main__":
    assert sys.argv[1] in ("bench", "held")
    main(sys.argv[1])
