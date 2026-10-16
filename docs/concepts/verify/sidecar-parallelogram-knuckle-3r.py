"""Independent verifier (skeptic) of sidecar-parallelogram-knuckle-3r (round 8 pick 1: the verified lead's chain and K
dyad UNCHANGED, bk1 30.05 / bk2 37.57 / a1max 61.72, with the strap-level sidecar drive of sidecar-longdyad-knuckle-3r:
hub-2 rim lobe -> bell crank on link 1b -> O3 rod on two M2 ball links -> horn lug of link 1a at hub K).

The claim's model (docs/concepts/models/sidecar-parallelogram-knuckle-3r.py, a wrapper on the shared core
docs/concepts/models/sidecar-longdyad-knuckle-3r.py) is loaded UNCHANGED through its own _prep (lead dyad, r_h floor
15.5, RC ball-link envelope). The protocol is the claim's frozen one (fit Bench(60,160) fast, shape frozen, worn on
Bench(110,360) exact or the held-out set), run through the core verifier's harness
(docs/concepts/verify/sidecar-longdyad-knuckle-3r.py, frozen_wear + extra_checks, which this file re-points at the
claim's module instance). Checks ADDED on every taken pose of the worn bench (not in the claim):
  1. world-frame RSSR closure (rod meets the horn ball and the crank-tip ball, < 0.5 mm);
  2. M2 ball-link tilt <= 30 deg at both studs;
  3. the real lobe pressure angle <= 45 deg (exact RSSR phi(dK), not the small-angle law gate);
  4. the idle-drive rule on the WORN bench (the drive must carry >= 30 deg of K over the taken poses);
  5. continuity flood fill (connected_report of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py).
Sensitivity (red team, not a correction): ball centre ZB 4.0 / 4.5 mm over the arm / lug tops (the claim uses 3.0, the
low end for an M2 ball stud + acetal socket).

    CB_EXACT=1 python3 docs/concepts/verify/sidecar-parallelogram-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--zb 4.0]
"""
import importlib.util, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


PG = _load("sidecar_parallelogram_claim_v", os.path.join(REPO, "docs", "concepts", "models", "sidecar-parallelogram-knuckle-3r.py"))
V = _load("sidecar_longdyad_verifier_for_pg", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
V.SC, V.S, V.PK = PG.SC, PG.SC.S, PG.SC.PK                   # the harness now builds the claim's own module instance
BEST = {"kK": 1.3487, "r_h": 15.5, "beta": -95.8268, "La": 14.8984, "s_arm": 4.3996, "hl": 3.15, "zr": 0.0, "r_lobe": 7.0578,
        "smhi": 19.3517, "smlo": 5.0, "az1": 97.8797, "el1": 67.0092, "az2": 40.8897, "el2": 44.7465, "wd": 69.9552, "wa": -10.525,
        "b3": 0.3702, "ang_min": 24.7893, "lc": 28.8341, "phib": -59.0793, "chain": "lead", "ends": "rc", "law_mode": "lin"}

if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        P = PG._prep(dict(BEST))
        if "--zb" in sys.argv: PG.SC.ZB = float(sys.argv[sys.argv.index("--zb") + 1])
        t = time.time(); out = V.frozen_wear(P, wear, "--flood" in sys.argv)
        ex = out["extra"]; out["idle_worn"] = ex.get("dK_taken_max_deg") is not None and ex["dK_taken_max_deg"] < PG.DK_IDLE
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", ZB=PG.SC.ZB, ER=PG.SC.ER,
                   dyad={k: P[k] for k in ("bk1", "bk2", "a1max")}, r_h=P["r_h"])
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"), why=out["why"], extra=ex,
                              idle_worn=out["idle_worn"], conn=out.get("connected"), parts=out.get("parts_ib14"), secs=out["secs"]), default=float))
