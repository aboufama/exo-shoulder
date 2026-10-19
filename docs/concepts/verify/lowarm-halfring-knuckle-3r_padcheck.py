"""Skeptic check (cell A) for lowarm-halfring-knuckle-3r: the crank STOP PAD on link 1b as metal.

The claim's model only checks that the crank arm's phi = 0 centreline passes 'over' link 1b with a lenient test (an arm
point counts as over when it lies within W_LINK / 2 + 1 = 5 mm of ANY link-1b sample, and link 1b is sampled over its
full 8 mm width, so a point up to ~5 mm beside the link edge passes) and never samples the pad. Here:

  P1. the pad seat for real: per arm sample at phi = 0, the tangential distance to link 1b's nearest sample and whether
      link-1b samples lie on both lateral sides (= inside the planform); the true pad lever (largest lever from the crank
      axis among arm samples truly over link 1b) and the K play the claim's own pad-lap formula gives at that lever;
  P2. the pad as a block (3 mm along the arm x 2 mm, on the arm's -sig side so it stops phi < 0, from link 1b's top face
      to the arm's top), worn per pose (link 1b's frame) vs link 2 (underside + top copy), link 1a (incl. its horn / boss),
      the crank (member 9) at the pose's own phi, and hub 2 / hub K axes (radial distance from the axis);
  P3. the pad's skin side: a pad that stands beside link 1b (not over it) faces the skin: its underside's distance to
      link 1b's top face is reported.

usage: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lowarm-halfring-knuckle-3r_padcheck.py <taken-dump.json|-> <out.json> --cell A --blend
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("lowarm_v_for_pad", os.path.join(REPO, "docs/concepts/verify/lowarm-halfring-knuckle-3r.py"))
LM, DS, S = V.LM, V.DS, V.S
import concept_bench as CB  # noqa: E402
unit = S.unit
t0 = time.time()
P = DS._clamp(dict(DS.PARAMS, **dict(V.BEST)))
old = os.environ.pop("CB_EXACT", None)
try: B1 = CB.Bench(n_clip=60, n_ws=160)
finally:
    if old is not None: os.environ["CB_EXACT"] = old
M1 = DS.DSModel(B1, dict(P)); r1 = M1.run()
fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
g = M1._scg; dR = np.asarray(g["dR"], float); PV = np.asarray(g["PV"], float); sig = float(g["sig"])
lw = getattr(M1, "_lowarm", {}) or {}
# ---- P1: arm samples at phi = 0 (crank rigid set) vs link 1b's planform
m7, L1b = M1.link_pts["L1b"]; L1b = np.asarray(L1b, float); L1d = unit(L1b)
vz = M1._viz_rod; arm = np.asarray(vz["armPts"], float).reshape(-1, 3)
mc, CR = M1.rigid["crank"]; CR = np.asarray(CR, float)
nn = cKDTree(L1b).query(L1b, k=2)[0][:, 1]; spacing = float(np.median(nn))
# link-1b local lateral direction: principal in-surface direction of the link (its length) at the nearest sample
def over_link(x):
    """tangential distance to the nearest L1b sample + whether samples lie on both sides across the link's length"""
    xd = unit(x); ang = np.arccos(np.clip(L1d @ xd, -1, 1)) * np.linalg.norm(x)
    j = int(np.argmin(ang)); near = L1b[np.linalg.norm(L1b - L1b[j], axis=1) < 12.0]
    if len(near) < 4: return float(ang[j]), False, None
    C = near - near.mean(0); n_ = unit(near.mean(0)); C = C - np.outer(C @ n_, n_)
    w_, v_ = np.linalg.eigh(C.T @ C); along = v_[:, -1]; lat = unit(np.cross(n_, along))
    s = (near - x) @ lat; a = (near - x) @ along; band = np.abs(a) < max(2.0, spacing)
    inside = bool(band.any() and (s[band] > 0).any() and (s[band] < 0).any())
    half = float(np.abs(s[band]).max()) if band.any() else None
    return float(ang[j]), inside, half
arm_rows = []
for x in CR:
    d, ins, half = over_link(x)
    lev = float(np.linalg.norm(x - (x @ dR) * dR - (PV - (PV @ dR) * dR))) if False else float(np.linalg.norm((x - PV) - ((x - PV) @ dR) * dR))
    arm_rows.append((lev, d, ins, x))
crk_over = [r for r in arm_rows if r[2]]
true_lever = max((r[0] for r in crk_over), default=None)
claim_lever = (lw.get("pad") or {}).get("lever_mm") if isinstance(lw, dict) else None
dpk = float(lw.get("dphi_dK", 0) or 0); pad_tol = float(P.get("pad_tol", 0.03))
k_pad = lambda L: math.degrees(pad_tol / L / max(dpk, 1e-9)) if L else None
play = (lw.get("dwell_K_play") or {}) if isinstance(lw, dict) else {}
p1 = dict(L1b_spacing_mm=round(spacing, 2), n_crank_samples=len(CR), n_crank_truly_over_L1b=len(crk_over),
          true_pad_lever_mm=round(true_lever, 2) if true_lever else None, claim_pad_lever_mm=claim_lever,
          claim_pad=lw.get("pad") if isinstance(lw, dict) else None, dphi_dK=dpk,
          k_pad_at_claim_lever=round(k_pad(claim_lever), 3) if claim_lever else None, k_pad_at_true_lever=round(k_pad(true_lever), 3) if true_lever else None,
          claim_play=play)
if true_lever and claim_lever and play:
    p1["total_play_at_true_lever"] = round(float(play["total"]) - float(play["pad_lap"]) + k_pad(true_lever), 3)
# ---- P2: the pad block (design frame = link 1b at rest, crank at phi = 0)
if crk_over:
    rr = max(crk_over, key=lambda r: r[0]); x0 = rr[3]
else:
    rr = max(arm_rows, key=lambda r: -r[1]); x0 = rr[3]
# arm centreline point at the pad: crank samples within 1 mm of x0's lever, averaged
lev_all = np.array([r[0] for r in arm_rows]); sel = np.abs(lev_all - rr[0]) < 1.0
xc = CR[sel].mean(0); under = float(np.linalg.norm(CR[sel], axis=1).min())
tdir = unit(-sig * np.cross(dR, xc)); tdir = unit(tdir - (tdir @ unit(xc)) * unit(xc))   # direction a phi < 0 rotation moves the arm
adir = unit(np.cross(unit(xc), tdir))
jn = int(np.argmin(np.linalg.norm(L1d - unit(xc), axis=1))); ref = float(np.linalg.norm(L1b[jn]))
pad = []
for a in np.linspace(-1.5, 1.5, 4):
    for t in np.linspace(3.0, 5.0, 3):                       # arm half-width 3 mm, pad 2 mm thick beyond the arm's side
        for h in np.linspace(ref + S.T_LINK, under + 3.0, 4):
            pad.append(unit(xc + a * adir + t * tdir) * h)
pad = np.array(pad)
p2 = dict(pad_centre_level_ref=round(ref, 2), arm_underside=round(under, 2), pad_base=round(ref + S.T_LINK, 2), pad_top=round(under + 3.0, 2), n_pad=len(pad))
# pad over link 1b? its own footprint vs the planform
p2["pad_footprint_over_L1b"] = [bool(over_link(unit(x) * ref)[1]) for x in pad[::12]]
# taken poses: from a verifier dump (bench, frozen exact) if given, else the fit bench's taken set on a frozen Bench(110,360)
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]


class Frozen(DS.DSModel):
    def fit(self):
        for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                  "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_desmo"):
            if hasattr(M1, a): setattr(self, a, getattr(M1, a))
        self._sc = None
        self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        self._truncate()


B = CB.Bench(n_clip=110, n_ws=360)
M = Frozen(B, dict(P2)); M.fit()
if sys.argv[1] != "-":
    dump = json.load(open(sys.argv[1])); taken = [p["i"] for p in dump["poses"] if p["taken"]]
else:
    taken = [int(i) for i in np.nonzero(M.kin_ok)[0]]
m2, X2 = M.link_pts["L2"]; X2 = np.concatenate([X2, X2 + S.T_LINK * unit(X2)])
m1a, X1a = M.link_pts.get("L1a", M.link_pts.get("L1", (1, np.zeros((0, 3)))))
A1 = [np.asarray(X1a, float)] + [np.asarray(X, float) for k, (m, X) in M.rigid.items() if m == 1] + [np.asarray(X, float) for m, X in M.contact if m == 1]
A1 = np.concatenate([a for a in A1 if len(a)])
C9 = np.concatenate([np.asarray(X, float) for m, X in M.contact if m == 9] + [np.asarray(X, float) for k, (m, X) in M.rigid.items() if m == 9])
cyl = {k: v for k, v in M.cyl.items()}
rows = []
for i in taken:
    Rb, tb = M.T(m7, i); Pw = pad @ Rb.T + tb
    R2, t2 = M.T(m2, i); d2 = float(cKDTree(X2 @ R2.T + t2).query(Pw)[0].min())
    R1, t1 = M.T(1, i); d1 = float(cKDTree(A1 @ R1.T + t1).query(Pw)[0].min())
    R9, t9 = M.T(9, i); C9w = C9 @ R9.T + t9; d9 = float(cKDTree(C9w).query(Pw)[0].min())
    hub = {}
    for nm, (mm, cen, ax) in cyl.items():
        Rm, tm = M.T(mm, i); c_ = Rm @ cen + tm; a_ = Rm @ ax; w_ = Pw - c_
        hub[nm] = float(np.linalg.norm(w_ - np.outer(w_ @ a_, a_), axis=1).min())
    rows.append(dict(i=int(i), kind=B.kind[i], dK=round(abs(math.degrees(float(M.dK[i]))), 2), L2=round(d2, 3), L1a=round(d1, 3), crank=round(d9, 3),
                     **{f"r_{k}": round(v, 2) for k, v in hub.items()}))
def mn(k): return min(rows, key=lambda r: r[k]) if rows else None
dw = [r for r in rows if r["dK"] < 1e-3]; fo = [r for r in rows if r["dK"] >= 1e-3]
p2.update(n_taken=len(rows), min_L2=mn("L2"), min_L1a=mn("L1a"), min_crank_forced=min(fo, key=lambda r: r["crank"]) if fo else None,
          min_crank_dwell=min(dw, key=lambda r: r["crank"]) if dw else None,
          hub_axis_r_min={k: min(r[f"r_{k}"] for r in rows) for k in cyl} if rows else None,
          L2_lt1=int(sum(1 for r in rows if r["L2"] < 1.0)), L1a_lt1=int(sum(1 for r in rows if r["L1a"] < 1.0)),
          crank_forced_lt0_15=int(sum(1 for r in fo if r["crank"] < 0.15)))
out = dict(id=LM.ID, cell="A", params=V.BEST, fit_fast=fit, lowarm_gate=lw, P1_pad_seat=p1, P2_pad_metal=p2, secs=round(time.time() - t0, 1),
           note="pad = 3 x 2 mm block beside the arm on its -sig side at the largest lever where the arm truly crosses link 1b, from link 1b's top to the arm's top; nearest-sample distances; non-adjacent rule 1 mm")
json.dump(out, open(sys.argv[2], "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ("note", "params", "lowarm_gate")}, default=float))
