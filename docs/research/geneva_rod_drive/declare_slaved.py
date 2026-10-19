"""Write the geneva rod's slaved-K declaration into a built design's build.json (the dynamics judge's "slaved" interface,
judge/dynamics.py docstring "SLAVED COORDINATES"). The law is the build's own: the full CAD's drive_kin table (t, dK from
the exact RSSR + roller solution) when present, else the L1's linear law (kK, q2hi, t_end). Frame convention of the clips:
dK (knuckle.dK) is NEGATIVE when driven, q2 = q[1]; t = q2hi - q2 (s_q = -1). Builders emit the same key from now on.

    python3 docs/research/geneva_rod_drive/declare_slaved.py l1_geneva-rod user_geneva_rod
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def declaration(B):
    law = B.get("law") or {}
    if "drive_kin" in B:
        rows = B["drive_kin"]["rows"]; q2hi = float(B["stops"]["J2"]["q2_onset_deg"])
        T = [float(r["t_deg"]) for r in rows]; DK = [float(r["dK_deg"]) for r in rows]; src = "build.json drive_kin (exact RSSR + roller rows)"
    else:
        q2hi, kK, te = float(law["q2hi_deg"]), float(law["kK"]), float(law["t_end_deg"])
        T = [0.0, te]; DK = [0.0, kK * te]; src = "build.json law (kK, q2hi, t_end: linear)"
    X = [round(q2hi - t, 4) for t in T]; Y = [round(-d, 4) for d in DK]
    o = sorted(range(len(X)), key=lambda i: X[i])
    return {"slaved": ["l1a", "l1b"], "driver": ["l1b", "l2"], "x_key": "q.1", "y_key": "knuckle.dK",
            "law_x_deg": [X[i] for i in o], "law_y_deg": [Y[i] for i in o], "rest_y_deg": 0.0, "closure": "force",
            "drive_groups": {"dk": "l1b", "dr": "l1b"}, "source": src,
            "note": "K = law(q2) past the onset (lobe -> MR63ZZ roller -> bell crank -> pushrod -> horn on link 1a's arbor); "
                    "below it the clock spring holds K on stop A; the spring also keeps the roller on the lobe (force closure)"}

if __name__ == "__main__":
    for d in sys.argv[1:]:
        p = os.path.join(REPO, "pipeline", "full-exo", "designs", d, "build.json"); B = json.load(open(p))
        B["slaved"] = [declaration(B)]; json.dump(B, open(p, "w"), indent=1)
        print(d, B["slaved"][0]["source"], len(B["slaved"][0]["law_x_deg"]), "rows")
