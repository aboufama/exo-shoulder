"""Skeptic (2026-10-18) of the 20:52 audit of underpass-bridge-relay-4r (M3 'gamed' on claim 13.74): try to refute the
strap-top-inside-shell finding. Model imported unchanged; fit Bench(60,160) fast prepare (the selection bench the frozen
R_under came from), phi 0 fit kin_ok frames. For the E strap's top face (contact set on member 3 with E's point count =
E + T_LINK) and E's underside, inside the shell footprint shrunk by an EDGE margin (0 / 1 / 2 mm along the axis and the
same arc length in azimuth, so a hit is not a footprint-edge artefact), report per frame the penetration
(top radius - R_under) and count frames with penetration > 0, > 0.5, > 1.0 mm.
    OMP_NUM_THREADS=1 nice python3 docs/alignment/remeasure/underpass-bridge-relay-4r_skeptic2052_striptop.py"""
import importlib.util, json, math, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("up_skep", os.path.join(REPO, "docs/concepts/models/underpass-bridge-relay-4r.py"))
UP = importlib.util.module_from_spec(sp); sp.loader.exec_module(UP)
PT, AA = UP.PT, UP.AA
PICK = json.load(open(os.path.join(REPO, "docs/concepts/verify/underpass-bridge-relay-4r/pick.json")))
BASE = dict(UP.CLAIM_PARENT)
S = UP.prepare(BASE, 60, 160, exact=False)
M1, ax = S["M1"], S["ax"]
rp = dict(S["rp"]); rp.update({k: v for k, v in dict(BASE, **PICK).items() if k in PT.DEF}); rp["rl_fix"] = 0.0
G = PT.geometry(M1, S["B1"], ax, rp); e, f, s0, lo, hi = G["e"], G["f"], G["s0"], G["lo"], G["hi"]
RU = float(PICK["rl_fix"]); RT = RU + 2.5
Etop = [k for k, (m, P) in enumerate(M1.contact) if m == 3 and len(P) == len(M1.rigid["E"][1])]
out = dict(R_under_frozen=RU, R_top_shell=RT, etop_sets=Etop, SH_W=PT.SH_W, az_window=[round(float(lo), 2), round(float(hi), 2)])
res = {}
for edge in (0.0, 1.0, 2.0):
    pen = []; under = []; nfr = 0
    for j in np.nonzero(M1.kin_ok)[0]:
        RS = M1.RS[j]; Q0 = M1.Q[j]; nfr += 1; best = {}
        for tag, (m, X) in (("E", M1.rigid["E"]), ("top", M1.contact[Etop[0]])):
            h = (M1.world(m, j, X) @ RS) @ Q0; sv = h @ ax; az = np.degrees(np.arctan2(h @ f, h @ e))
            mid = 0.5 * (lo + hi); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
            daz = math.degrees(edge / RU)
            ins = (np.abs(sv - s0) <= 0.5 * PT.SH_W - edge) & (azr >= lo + daz) & (azr <= hi - daz)
            best[tag] = float(np.linalg.norm(AA._rad(h[ins], ax), axis=1).max()) if ins.any() else None
        if best["top"] is not None: pen.append((round(best["top"] - RU, 3), int(j)))
        if best["E"] is not None: under.append((round(RU - best["E"], 3), int(j)))
    p = np.array([x for x, _ in pen]) if pen else np.zeros(0)
    res[str(edge)] = dict(frames=nfr, frames_with_top_in_footprint=len(pen),
                          pen_gt0=int((p > 0).sum()), pen_gt0_5=int((p > 0.5).sum()), pen_gt1=int((p > 1.0).sum()),
                          pen_max=max(pen) if pen else None, pen_median=float(np.median(p)) if len(p) else None,
                          E_underside_clear_min=min(under) if under else None,
                          top_inside_shell_metal=int(((p > 0) & (p < 2.5)).sum()))
out["by_edge_margin_mm"] = res
out["t"] = "2026-10-18 skeptic"
json.dump(out, open(os.path.join(REPO, "docs/alignment/remeasure/underpass-bridge-relay-4r_skeptic2052_striptop.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
