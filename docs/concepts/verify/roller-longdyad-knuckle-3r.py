"""Independent verifier (skeptic) of roller-longdyad-knuckle-3r (the verified roller-flank knuckle re-worn on a free K dyad:
hub-2 rim lobe -> bell crank on link 1b -> bent arm -> MR63 roller on an integral stub (retaining head counted) ->
conjugate flank milled into a boss of link 1a; PA_MAX 43; 2 mm near-touch search objective).

The claim's model (docs/concepts/models/roller-longdyad-knuckle-3r.py, on sidecar-roller-flank-knuckle-3r.py) is loaded
UNCHANGED. This harness re-uses the round's roller-flank verifier (docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py:
frozen protocol fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out; cam closure in the
world, roller vs lug, K sense, pressure angles at each taken pose, real lobe pressure angle, drive-idle rule, continuity
flood) retargeted at this claim's model class, clamp, params and best config, and ADDS:

  8. FOLD MARGIN in the one metric (CLAUDE.md): the own-state J1-J3 margin per taken pose from the member frames
     (tools/sidecar_env_polish.py th_margin, copied): min, poses < 5.
  9. PA rule at both readings: the per-pose check at the claim's 43 deg AND the round-9 judge's 45 deg gate.
 --head: the lug's flank-edge strip that the parent sampling deletes + a O5 head (the claim already counts O4.5).

    CB_EXACT=1 python3 docs/concepts/verify/roller-longdyad-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--head]
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


RL = _load("roller_longdyad_claim_v", os.path.join(REPO, "docs", "concepts", "models", "roller-longdyad-knuckle-3r.py"))
H = _load("roller_flank_verifier_for_rl", os.path.join(HERE, "sidecar-roller-flank-knuckle-3r.py"))
# retarget the parent verifier at THIS claim: model class, clamp, params; the cam helpers are the claim's RF (unchanged)
H.RF = types.SimpleNamespace(phi_of=RL.RF.phi_of, dphi_of=RL.RF.dphi_of, ROLL_R=RL.RF.ROLL_R, _ring=RL.RF._ring,
                             RFModel=RL.RLModel, _clamp=RL._clamp, PARAMS=RL.PARAMS)
H.SC, H.S, H.PK = RL.SC, RL.S, RL.PK
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "roller-longdyad-knuckle-3r.json")))["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
H.BEST = BEST
H.PA_MAX = 43.0                     # the claim's own rule (RL.RF.PA_MAX); 45 is re-read below


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m_plain = _dm(th, a1, a2); m_eff = _dm(th, a1e, a2e); m_sub = _dm(th, b1, c)
        rows.append((min(m_sub, m_eff) if forced else m_plain, forced, m_plain, m_eff, m_sub, i, th))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]; lo = min(rows)
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)),
                forced=int(sum(r[1] for r in rows)), th_max_taken=round(max(r[6] for r in rows), 2),
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[5]], **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}))


_extra0 = H.extra_checks


def extra_checks(M, Mfit, B):
    out = _extra0(M, Mfit, B)
    try: out["th_margin"] = th_margin(M, B)
    except Exception as e: out["th_margin"] = dict(error=repr(e)[:300])
    H.PA_MAX = 45.0
    try: out["at_pa45"] = {k: _extra0(M, Mfit, B)[k] for k in ("poses_failing", "why_failing", "corrected")}
    finally: H.PA_MAX = 43.0
    out["cam_claim"] = {k: (getattr(Mfit, "_sc_info", None) or {}).get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken",
                                                                                     "clear_hubK_min", "clear_roll_hubK_min", "stub_head")}
    return out


H.extra_checks = extra_checks

if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = H.frozen_wear(dict(BEST), wear, "--flood" in sys.argv, "--head" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, head=out["head"], fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"),
                              why=out["why"], extra=out["extra"], conn=out.get("connected"), secs=out["secs"]), default=float))
