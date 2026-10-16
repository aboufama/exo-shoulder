"""Claim harness for minarc-stop-knuckle-4r variant B under the KIT fold rule (docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py).

It runs the independent re-measure verifier's own protocol (docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py, imported
UNCHANGED) with the verifier's model handle swapped to the kit-rule model: the same frozen fit60 -> wear hand-over, the same
verifier extra checks (closure per axis, K one-sided, J2 interior angle inside the (derived) stops, boss / knee clearances), the
same held-out bench (so H1 31.39 is comparable) and the same continuity flood fill (`conn`: 2-deg slerp edges over the 1432-pose
workspace grid, no q1 / q2 / q3' / pin a / pin b / dK step > 10 deg, knee branch constant, seeds at elevation 0 with K on stop A).
Added check: the kit's J1-J3 fold margin of the EFFECTIVE dyad (a1e, a2) over every taken pose in every state (>= FOLD_MARGIN, or
the pose is knocked out), reported as extra.kit_margin_all_states.

    OMP_NUM_THREADS=1 CB_EXACT=1 python3 docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py conn fit60 B conn.json '<json params>'
    OMP_NUM_THREADS=1 CB_EXACT=1 python3 docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py wear fit60 <bench|held> B out.json '<json params>' --conn conn.json
"""
import importlib.util, json, os, sys
import numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as KIT                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


VER = _load("minarc_remeasure_for_kitrule", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-remeasure.py"))
KR = _load("minarc_kitrule_model", os.path.join(HERE, "minarc-stop-knuckle-4r-kitrule.py"))
VER.KB = KR                                                   # KModel / KDesign / PARAMS / PK of the kit-rule model
_checks0 = VER.extra_checks_B


def extra_checks_kit(M, B):
    D = M.D; phys = bool(getattr(D, "phys", False))
    if phys:                                                  # the physical stop holds q2, not the virtual phi: phi only kept off its fold
        save = (D.p["phi_lo"], D.p["phi_hi"]); D.p["phi_lo"], D.p["phi_hi"] = 0.0, 180.0
    try: out, bad = _checks0(M, B)
    finally:
        if phys: D.p["phi_lo"], D.p["phi_hi"] = save
    D.ik(M.Q); m3 = np.asarray(D._m3e, float)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    low = [i for i in taken if m3[i] < KIT.FOLD_MARGIN - 1e-6]
    st = np.asarray(M.kstate)
    out["kit_margin_all_states"] = dict(min=round(float(m3[taken].min()), 2) if taken else None, below=len(low),
                                        lt10=int(sum(1 for i in taken if m3[i] < 10)),
                                        by_state={s: (round(float(m3[[i for i in taken if st[i] == v]].min()), 2) if any(st[i] == v for i in taken) else None)
                                                  for s, v in (("A", 0), ("stretched", 1), ("folded", -1))},
                                        stops=dict(phi_lo=round(D.p["phi_lo"], 2), phi_hi=round(D.p["phi_hi"], 2), smlo=D.p.get("smlo"), smhi=D.p.get("smhi")))
    badq2 = []
    if phys:                                                  # J2's own angle q2 from the member frames, inside the dowel slot
        lo, hi = D.q2_stops; q2s = []; q0 = np.degrees(D._q2c[2]); sg = D.q2sgn
        rel = lambda x: ((x - q0 + 180) % 360 - 180) * sg              # position on the branch's half-turn of q2 (0 .. 180)
        wlo, whi = sorted((rel(lo), rel(hi)))
        for i in taken:
            R1b, _ = M.T(7, i); R2, _ = M.T(2, i); rv = Rot.from_matrix(R1b.T @ R2).as_rotvec(); q2 = float(np.degrees(rv @ D.u[1]))
            q2s.append(q2); r_ = rel(q2)
            if r_ < wlo - 0.05 or r_ > whi + 0.05: badq2.append(i)
        out["j2_q2_phys"] = dict(stops=[round(lo, 3), round(hi, 3)], range_taken=[round(min(q2s), 3), round(max(q2s), 3)] if q2s else None, bad=len(badq2),
                                 note="phi check relaxed to [5, 175] under the physical stop; q2 (link 1b vs link 2) checked against the slot")
    return out, set(bad) | set(low) | set(badq2)


VER.extra_checks_B = extra_checks_kit

if __name__ == "__main__":
    a = sys.argv[1:]; cj = None
    if "--conn" in a: k = a.index("--conn"); cj = a[k + 1]; del a[k:k + 2]
    if a[0] == "wear": VER.wear(a[1], a[2], a[3], a[4], json.loads(a[5]) if len(a) > 5 else None, cj)
    elif a[0] in ("conn", "conn-taken"): VER.conn(a[1], a[2], a[3], json.loads(a[4]) if len(a) > 4 else None, taken_mode=a[0] == "conn-taken")
    else: raise SystemExit(__doc__)
