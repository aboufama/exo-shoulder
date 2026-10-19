"""Independent verifier (skeptic) of kneeless-roller-knuckle-3r (the round-9 roller-flank knuckle on the free K dyad with
J3 put on a GH ray, b3 0, and the two-pin knee replaced by ONE rigid 3 mm Ti bracket from hub 3's lower plate to the arm
pad; rodless drive: hub-2 rim lobe -> bell crank on link 1b -> bent arm -> MR63 roller on an integral stub -> conjugate
flank milled into a boss of link 1a).

The claim's model (docs/concepts/models/kneeless-roller-knuckle-3r.py, on roller-longdyad-knuckle-3r.py and
sidecar-roller-flank-knuckle-3r.py) is loaded UNCHANGED. The protocol is the claim's frozen one (fit Bench(60,160) fast,
shape frozen, worn on Bench(110,360) exact / held out). This harness re-uses the round's roller verifiers
(docs/concepts/verify/roller-longdyad-knuckle-3r.py on sidecar-roller-flank-knuckle-3r.py: cam closure in the world,
roller vs lug, K sense, per-pose pressure angles at 43 and at 45 deg, real lobe pressure angle, drive-idle rule, th fold
margin, continuity flood) retargeted at THIS claim's model class / clamp / params / best config, and ADDS on every taken
pose of the worn bench (from the kneeless-sidecar verifier, docs/concepts/verify/kneeless-sidecar-knuckle-3r.py):

  R1. RIGID BRACKET measured from the transforms (not from the model's own knee report): member 3 (hub 3 + E + boss) and
      member 6 (the bracket plate) expressed in the pad (member 5) frame must keep one pose: drift > 0.5 mm fails the pose;
  R2. every taken pose re-collided with the claim's part-pair check: min non-adjacent clearance >= 1 mm, adjacent pairs
      (E vs link 2, bracket vs hub 3) >= 0.15 mm (a pose failing is lost); per-pair minima reported.
  The corrected report removes the union of the drive-check failures (at the claim's 43 deg) and R1 / R2 failures.

    CB_EXACT=1 python3 docs/concepts/verify/kneeless-roller-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--head]
"""
import importlib.util, json, os, sys, time, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KL = _load("kneeless_roller_claim_v", os.path.join(REPO, "docs", "concepts", "models", "kneeless-roller-knuckle-3r.py"))
RLV = _load("roller_longdyad_verifier_for_kl", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
KSV = _load("kneeless_sidecar_verifier_for_kl", os.path.join(HERE, "kneeless-sidecar-knuckle-3r.py"))
H = RLV.H
H.RF = types.SimpleNamespace(phi_of=KL.RF.phi_of, dphi_of=KL.RF.dphi_of, ROLL_R=KL.RF.ROLL_R, _ring=KL.RF._ring,
                             RFModel=KL.KLModel, _clamp=KL._clamp, PARAMS=KL.PARAMS)
H.SC, H.S, H.PK = KL.SC, KL.S, KL.PK
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "kneeless-roller-knuckle-3r.json")))["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
H.BEST = BEST
_rl_extra = RLV.extra_checks


def extra_checks(M, Mfit, B):
    out = _rl_extra(M, Mfit, B)
    assert type(M).__mro__[1].__name__ == "KLModel" or type(M).__name__ == "KLModel", type(M).__mro__
    if M is Mfit: return out
    bc = KSV.bracket_and_clear(M, B); out["bracket"] = bc
    drive_bad = set(out.get("poses_failing_ids", []))
    if out.get("poses_failing", 0) > len(drive_bad): out["warn_ids_truncated"] = True
    bad = sorted(drive_bad | set(bc["poses_failing"])); out["n_removed_all"] = len(bad)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    out["corrected_all"] = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    B.res = res0
    K = M.K; ko = np.asarray(M.kin_ok, bool)
    out["knee_model"] = dict(ang_ptp=round(float(np.ptp(np.asarray(K["ang"], float)[ko])), 4) if ko.any() else None,
                             s_max_mm=round(float(np.abs(np.asarray(M.s, float)[ko]).max()), 4) if ko.any() else None)
    out["ws_inband"] = KL.ws_inband(B)
    return out


H.extra_checks = extra_checks

if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = H.frozen_wear(dict(BEST), wear, "--flood" in sys.argv, "--head" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        ex = {k: v for k, v in out["extra"].items() if k not in ("poses_failing_ids",)}
        print(json.dumps(dict(wear=wear, head=out["head"], fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"),
                              why=out["why"], extra=ex, conn=out.get("connected"), secs=out["secs"]), default=float))
