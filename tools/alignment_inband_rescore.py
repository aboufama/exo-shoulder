"""Alignment re-score of an inband-rssr-knuckle-3r config through the envelope polish's own claim harness
(tools/inband_env_polish.py `claim`, imported UNCHANGED), with optional in-memory measurement overrides:

  --dedup-ear      the ear (clay 1) is sampled twice where its pivot disc S.disc(6, 2) and its 2 mm strip overlap
                   (0.50 samples/mm2 against 0.29-0.42 on every other plate; tools/alignment_part_density.py). This drops
                   every ear sample within 1.42 mm (sqrt(2) x half the 2 mm spacing) of an earlier ear sample, so the
                   overlap is sampled once; the strip and the disc keep their own 2 mm grids elsewhere.
  --er X           the ball-link socket ring radius SC.ER (model 3.5 = O7; the catalogue igus KBRM-02 head O9 -> 4.5)
  --zb Z           the horn-end ball centre's height over the lug top SC.ZB (model 3.0; a spacer raises it)
  --set k=v        a parameter override on the config (e.g. r_h=15.9, the sidecar red team's fix for the ROD-hubK pair)
  --fitonly        only the fit bench Bench(60,160) FAST reading (seconds; a screen, not a claim)

The model file, the benches, the kit and the row are never edited: every override lives in this process only. The result
is a MEASUREMENT for an alignment audit / proposal (docs/ALIGNMENT.md section 4), never an input to a score.

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_inband_rescore.py \
        <fit60|env> <bench|held> <params.json> OUT.json [--dedup-ear] [--er 4.5] [--set r_h=15.9] [--fitonly]
"""
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
import inband_env_polish as EP                                # noqa: E402  (loads the model unchanged)

IB, S, SC = EP.IB, EP.S, EP.SC
DEDUP_D = 1.42
STATS = dict(calls=0, ear_before=[], ear_after=[])


def thin(X, d=DEDUP_D):
    keep = []
    for i, x in enumerate(X):
        if not keep or float(np.min(np.linalg.norm(X[keep] - x, axis=1))) >= d: keep.append(i)
    return X[keep]


def install_dedup():
    orig = IB.IBModel._ib_rod_metal

    def wrapped(self, *a, **k):
        out = orig(self, *a, **k)
        if "ear" in self.rigid:
            m, E = self.rigid["ear"]; E2 = thin(np.asarray(E, float)); self.rigid["ear"] = (m, E2)
            STATS["calls"] += 1; STATS["ear_before"].append(len(E)); STATS["ear_after"].append(len(E2))
        return out
    IB.IBModel._ib_rod_metal = wrapped


def density(M):
    from scipy.spatial import ConvexHull
    out = {}
    for kk, v in M.rigid.items():
        X = np.asarray(v[1], float)
        if len(X) < 4: continue
        C = X - X.mean(0); _, _, vt = np.linalg.svd(C, full_matrices=False); Y = C @ vt[:2].T
        try: a = float(ConvexHull(Y).volume)
        except Exception: continue
        out[kk] = dict(n=len(X), area_mm2=round(a, 1), per_mm2=round(len(X) / a, 3))
    return out


def main():
    a = sys.argv[1:]
    fit, wb, src, outp = a[0], a[1], a[2], a[3]
    P = json.load(open(src)); P = P.get("params", P)
    sets = {}
    for i, x in enumerate(a):
        if x == "--set": k, v = a[i + 1].split("="); sets[k] = float(v)
    P.update(sets)
    if "--er" in a: SC.ER = float(a[a.index("--er") + 1])
    if "--zb" in a: SC.ZB = float(a[a.index("--zb") + 1])      # ball centre over the lug top (a spacer under the stud)
    if "--dedup-ear" in a: install_dedup()
    tmp = outp.replace(".json", "_params.json"); json.dump(dict(params=P), open(tmp, "w"), indent=1)
    meta = dict(src=src, sets=sets, er=SC.ER, zb=SC.ZB, dedup_ear="--dedup-ear" in a, margin=EP.KIT.FOLD_MARGIN,
                noprice=os.environ.get("ENVP_NOPRICE") == "1")
    if "--fitonly" in a:
        Pp, pinfo = EP.priced(EP.params_of(tmp))
        r1, M1 = EP._rep(EP._fit_bench(fit), Pp)
        res = dict(meta=meta, fit_fast={k: r1.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "gap_near2")},
                   why=r1.get("why"), cam=EP.cam_of(M1, r1), density=density(M1), ear=STATS)
        json.dump(res, open(outp, "w"), indent=1, default=float); print(json.dumps(dict(meta=meta, fit=res["fit_fast"], why=res["why"], ear=STATS), default=float)); return
    EP.claim(fit, wb, tmp, outp)
    res = json.load(open(outp)); res["alignment_meta"] = meta; res["ear_dedup_stats"] = dict(calls=STATS["calls"],
        before=sorted(set(STATS["ear_before"])), after=sorted(set(STATS["ear_after"])))
    json.dump(res, open(outp, "w"), indent=1, default=float)
    print("META", json.dumps(meta), json.dumps(res["ear_dedup_stats"]))


if __name__ == "__main__":
    main()
