"""Alignment re-wear adapter: the acromial-rocker-3r frozen claim worn on the DISJOINT held-out set.

The model (docs/concepts/models/acromial-rocker-3r.py) has frozen() but no frozen_held(), so
`tools/alignment_audit.py remeasure acromial-rocker-3r held` cannot run. This adapter runs the model's OWN frozen()
UNCHANGED (fit on Bench(60,160) fast incl. the stud refit, shape frozen, no refit) and only swaps the wear bench:
the second CB.Bench(...) frozen() builds (n_clip = n_ws = -7, a sentinel) is replaced by the pin-knee polish
verifier's held_bench() (docs/concepts/verify/skin-normal-3r-pin-knee-polish.py, imported unchanged: every fit-clip
frame and workspace pose outside Bench(110,360) and Bench(60,160), exact path; Wave / Walking stay out). The model's
audit() is wrapped by tools/alignment_audit.py deep_audit (near-touch 1 / 2 / 3 mm, metal histogram, coordinate spans),
exactly as `remeasure` does. Writes docs/alignment/remeasure/acromial-rocker-3r_held.json in the remeasure format.
Nothing is edited.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_acromial_rocker_held.py
"""
import importlib.util, json, os, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                  # noqa: E402
import concept_bench as CB                                    # noqa: E402

RID = "acromial-rocker-3r"


def main():
    P = dict(json.load(open(os.path.join(AA.ROWS, RID + ".json"))).get("best_params") or {})
    mod = AA._load("aa_acr_held", os.path.join(AA.MODELS, RID + ".py"))
    sp = importlib.util.spec_from_file_location("pk_polish_for_acr", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py"))
    H = importlib.util.module_from_spec(sp); sp.loader.exec_module(H)
    Orig = CB.Bench

    def Bench(n_clip=110, n_ws=360, seed=0):
        if n_clip == -7 and n_ws == -7: return H.held_bench()
        return Orig(n_clip=n_clip, n_ws=n_ws, seed=seed)
    mod.CB.Bench = Bench
    pk = mod.PK; orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B); box["deep"] = AA.deep_audit(M, B); box["mode"] = B.mode; box["n"] = len(B.idx); return a
    pk.audit = wrapped
    t = time.time()
    try:
        r = mod.frozen(P, nc=-7, nw=-7)
    finally:
        pk.audit = orig; mod.CB.Bench = Orig
    out = dict(id=RID, wear="held", params=P, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"), why=r.get("why"), parts_ib14=r.get("parts_ib14"),
               audit=r.get("audit"), deep=box.get("deep"), mode=box.get("mode"), n_wear_poses=box.get("n"), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"),
               harness="model frozen() unchanged; wear bench = skin-normal-3r-pin-knee-polish.py held_bench() (tools/alignment_acromial_rocker_held.py)")
    os.makedirs(AA.REM, exist_ok=True)
    path = os.path.join(AA.REM, f"{RID}_held.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(id=RID, wear="held", frozen=out["frozen"], deep={k: v for k, v in (out["deep"] or {}).items() if k != "coord_spans"}, secs=out["secs"]), default=float))


if __name__ == "__main__":
    main()
