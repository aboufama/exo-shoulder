# independent auditor check: radius of the E strap's underside (rigid E) vs its top face (contact set (3, E + T_LINK sn))
# about the relay axis, inside the shell footprint, over the fit kin_ok frames (phi 0); compares with the frozen R_under.
import importlib.util, json, math, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("up_audit", os.path.join(REPO, "docs/concepts/models/underpass-bridge-relay-4r.py"))
UP = importlib.util.module_from_spec(sp); sp.loader.exec_module(UP)
PT, AA = UP.PT, UP.AA
PICK = json.load(open(os.path.join(REPO, "docs/concepts/verify/underpass-bridge-relay-4r/pick.json")))
BASE = dict(UP.CLAIM_PARENT)
S = UP.prepare(BASE, 60, 160, exact=False)
M1, ax = S["M1"], S["ax"]
rp = dict(S["rp"]); rp.update({k: v for k, v in dict(BASE, **PICK).items() if k in PT.DEF}); rp["rl_fix"] = 0.0
G = PT.geometry(M1, S["B1"], ax, rp); e, f, s0, lo, hi = G["e"], G["f"], G["s0"], G["lo"], G["hi"]
Etop = [k for k, (m, P) in enumerate(M1.contact) if m == 3 and len(P) == len(M1.rigid["E"][1])]
out = dict(R_under_frozen=PICK["rl_fix"], etop_sets=Etop, frames=0)
best = {"E": (-1, None), "top": (-1, None)}; n_in = 0
for j in np.nonzero(M1.kin_ok)[0]:
    RS = M1.RS[j]; Q0 = M1.Q[j]; out["frames"] += 1
    for tag, (m, X) in (("E", M1.rigid["E"]), ("top", M1.contact[Etop[0]])):
        h = (M1.world(m, j, X) @ RS) @ Q0; sv = h @ ax; az = np.degrees(np.arctan2(h @ f, h @ e))
        mid = 0.5 * (lo + hi); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
        ins = (np.abs(sv - s0) <= 0.5 * PT.SH_W) & (azr >= lo) & (azr <= hi)
        if ins.any():
            r = float(np.linalg.norm(AA._rad(h[ins], ax), axis=1).max())
            if r > best[tag][0]: best[tag] = (round(r, 3), int(j))
            if tag == "top" and r > PICK["rl_fix"]: n_in += 1
out.update(E_underside_max=best["E"], E_top_max=best["top"], frames_top_above_R_under=n_in)
print(json.dumps(out))
