"""Task 4: compare the OpenSim Seth 2016 GH displacement (gh_seth.json) with the rig law (pipeline/avg/body_pose.py segs())
and the teammate's literature law (pipeline/girdle/girdle.py lift_literature), and decompose the difference to the
literature law step by step:
  A  lift_literature (quadratic fit of the rigid chain)
  B  the rigid chain itself (docs/research/gh_translation_literature.md section 2: 154 mm clavicle, rig AC->GH vector,
     scapula rotated about AC from Ludewig Table I rest), same Ludewig angles          B - A = quadratic-fit error
  C  B with the Seth clavicle (SC->AC joint, 125.2 mm)                                  C - B = clavicle length
  D  C with the Seth AC->GH vector (at its Table I rest fit)                            D - C = AC->GH vector
  E  D with the angles the Seth model actually reaches (its 3-DOF girdle cannot meet all 5 published angles)
                                                                                        E - D = constrained kinematics
  F  OpenSim Seth (primary)                                                             F - E = chain vs model (AC off the clavicle axis)
Runs in the repo's python (numpy 2.0.2):  python3 pipeline/girdle/opensim_seth/compare.py      -> compare.json + markdown tables
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, os.path.join(HERE, "..", "..", "avg"))
import girdle as G
import body_pose as BP
sys.path.insert(0, HERE)
import ludewig2009 as LW

J = json.load(open(os.path.join(HERE, "gh_seth.json")))
PL = J["plane_names"]; PD = J["planes_deg"]; EL = J["elev_deg"]; TH = [30, 60, 90, 120, 150]
rows = {(r["plane_name"], r["elev"]): r for r in J["table"]}
LS = json.load(open(os.path.join(HERE, "..", "..", "avg", "body_mesh.json"))); Lm, Sc = LS["landmarks"], LS["scale"]


def rig(th, plane): return BP.segs(Lm, Sc, dict(plane=plane, elev=th, axial=0, flex=0, pron=0))[1]
def lit(th, plane): return G.lift_literature(np.array([[plane, th]]))[0]
def var(v, p, th): return np.array(J["variants"][v]["gh_mm"][PL.index(p)][EL.index(th)])


# ---------------------------------------------------------------- rig geometry (as in the teammate's rig_geom.py)
def part(name):
    p = next(p for p in LS["parts"] if p["name"] == name); return BP.dec(p["pos"], np.int16).reshape(-1, 3).astype(float) / 10
cl = part("right clavicle"); c = cl.mean(0); ax = np.linalg.svd(cl - c)[2][0]; ax = ax if ax[2] > 0 else -ax; t = (cl - c) @ ax
SC_rig, AC_rig = cl[t < t.min() + 8].mean(0), cl[t > t.max() - 8].mean(0)               # rig origin = right GH centre
rest = J["rest_tableI"]; GHs, ACs, SCs = (np.array(rest[k]) for k in ["gh_abs_isb_mm", "ac_abs_isb_mm", "sc_abs_isb_mm"])
geo = dict(rig_SC_GH_mm=float(np.linalg.norm(SC_rig)), rig_clavicle_mm=float(np.linalg.norm(AC_rig - SC_rig)), rig_AC_GH_mm=(-AC_rig).round(1).tolist(),
           seth_SC_GH_mm=float(np.linalg.norm(GHs - SCs)), seth_clavicle_mm=float(np.linalg.norm(ACs - SCs)), seth_AC_GH_mm=(GHs - ACs).round(1).tolist())
s_rig = geo["rig_SC_GH_mm"] / geo["seth_SC_GH_mm"]; geo["scale_rig_over_seth_SC_GH"] = s_rig
geo["scale_rig_over_seth_clavicle"] = geo["rig_clavicle_mm"] / geo["seth_clavicle_mm"]

# ---------------------------------------------------------------- chain (gh_lit.py gh(), identical maths)
D = math.pi / 180
def Rx(a): c_, s_ = math.cos(a * D), math.sin(a * D); return np.array([[1, 0, 0], [0, c_, -s_], [0, s_, c_]])
def Ry(a): c_, s_ = math.cos(a * D), math.sin(a * D); return np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
def Rz(a): c_, s_ = math.cos(a * D), math.sin(a * D); return np.array([[c_, -s_, 0], [s_, c_, 0], [0, 0, 1]])
def Risb(a1, a2, a3): return Ry(a1) @ Rx(a2) @ Rz(a3)
def chain(a, L, r, ref):
    return Risb(-a["ret"], -a["elev"], 0) @ np.array([0, 0, L]) + Risb(a["IR"], -a["UR"], a["PT"]) @ Risb(ref["IR"], -ref["UR"], ref["PT"]).T @ r
R_RIG = np.array([16.2, -34.9, 24.5]); L_LIT = 154.0
r_seth, L_seth = GHs - ACs, geo["seth_clavicle_mm"]
ach_rest = rest["achieved_deg"]


def steps(p, th):
    a, _ = LW.angles(p, th); a0, _ = LW.angles(p, 0)
    ach, ach0 = rows[(p, th)]["achieved_deg"], rows[(p, 0)]["achieved_deg"]
    B = chain(a, L_LIT, R_RIG, LW.REST) - chain(a0, L_LIT, R_RIG, LW.REST)
    C = chain(a, L_seth, R_RIG, LW.REST) - chain(a0, L_seth, R_RIG, LW.REST)
    Dd = chain(a, L_seth, r_seth, LW.REST) - chain(a0, L_seth, r_seth, LW.REST)
    E = chain(ach, L_seth, r_seth, ach_rest) - chain(ach0, L_seth, r_seth, ach_rest)
    return dict(A=lit(th, LW.PLANE[p]), B=B, C=C, D=Dd, E=E, F=np.array(rows[(p, th)]["gh_mm"]))


f = lambda v: " / ".join(f"{x:.1f}" for x in v)
n = lambda v: f"{np.linalg.norm(v):.1f}"
out = dict(geometry=geo, rows=[], decomposition=[])
print("geometry:", json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in geo.items()}))
print("\n| plane | elev | Seth primary (ant/sup/lat) | Seth range: w_scap .. w_clav (sup) | clamped | rig | lift_literature | Seth-rig vec / abs | Seth-lit vec / abs | Seth x %.2f | Seth x s - lit abs |" % s_rig)
print("|---|---|---|---|---|---|---|---|---|---|---|")
for p in PL:
    for th in TH:
        F = np.array(rows[(p, th)]["gh_mm"]); Rg = rig(th, LW.PLANE[p]); Li = lit(th, LW.PLANE[p]); Fs = F * s_rig
        sup_rng = sorted([var(v, p, th)[1] for v in ["primary", "w_clav", "w_scap"]])
        ex = rows[(p, th)]["extrapolated"]; tag = "*" if ex else ""
        print(f"| {p} | {th}{tag} | {f(F)} | {sup_rng[0]:.1f} .. {sup_rng[-1]:.1f} | {f(var('clamped', p, th))} | {f(Rg)} | {f(Li)} | {f(F - Rg)} / {n(F - Rg)} | {f(F - Li)} / {n(F - Li)} | {f(Fs)} | {n(Fs - Li)} |")
        out["rows"].append(dict(plane=p, elev=th, extrapolated=ex, seth=F.tolist(), seth_clamped=var("clamped", p, th).tolist(), seth_w_clav=var("w_clav", p, th).tolist(),
                                seth_w_scap=var("w_scap", p, th).tolist(), rig=Rg.tolist(), lit=Li.tolist(), seth_minus_rig=(F - Rg).tolist(), seth_minus_lit=(F - Li).tolist(),
                                seth_scaled=Fs.tolist(), seth_scaled_minus_lit=(Fs - Li).tolist()))
print("\nDecomposition Seth (F) vs lift_literature (A), ant / sup / lat mm:")
print("| plane | elev | A lift_literature | B - A quad. fit | C - B clavicle 154->125 | D - C AC->GH vector | E - D angle residuals | F - E chain vs model | F |")
print("|---|---|---|---|---|---|---|---|---|")
for p in PL:
    for th in TH:
        st = steps(p, th)
        print(f"| {p} | {th} | {f(st['A'])} | {f(st['B'] - st['A'])} | {f(st['C'] - st['B'])} | {f(st['D'] - st['C'])} | {f(st['E'] - st['D'])} | {f(st['F'] - st['E'])} | {f(st['F'])} |")
        out["decomposition"].append(dict(plane=p, elev=th, **{k: v.tolist() for k, v in st.items()}))

# ---------------------------------------------------------------- sensitivity through the unconstrained chain (each angle on its own)
print("\nSensitivity, +-1 SD of each angle at the elevated posture (rest fixed): GH change through the rigid chain, ant / sup / lat mm")
print("(Seth geometry = L 125.2 mm + Seth AC->GH; rig geometry = the teammate's L 154 mm + rig AC->GH). Compare: gh_seth.json sensitivity (through the 3-DOF model fit)")
print("| plane | elev | geometry | d ret +-5 | d elev +-5 | d IR +-12.8 | d UR +-4.8 | d PT +-13 | RSS | abs RSS | fit-based abs RSS |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
out["chain_sensitivity"] = []
for p in PL:
    for th in [90, 120]:
        a, _ = LW.angles(p, th)
        for gname, L_, r_ in [("Seth", L_seth, r_seth), ("rig", L_LIT, R_RIG)]:
            g0 = chain(a, L_, r_, LW.REST); per = {}
            for k in LW.KEYS:
                dd = []
                for sg in (1, -1):
                    b = dict(a); b[k] += sg * LW.SD[k]; dd.append(chain(b, L_, r_, LW.REST) - g0)
                per[k] = dd
            big = np.array([np.maximum(np.abs(per[k][0]), np.abs(per[k][1])) for k in LW.KEYS]); rss = np.sqrt((big ** 2).sum(0))
            fit_rss = J["sensitivity"]["by_plane"][p][str(th)]["rss_norm_mm"]
            print(f"| {p} | {th} | {gname} | " + " | ".join(f"{f(per[k][0])} ; {f(per[k][1])}" for k in LW.KEYS) + f" | {f(rss)} | {np.linalg.norm(rss):.1f} | {fit_rss:.1f} |")
            out["chain_sensitivity"].append(dict(plane=p, elev=th, geometry=gname, per_angle={k: [v.tolist() for v in per[k]] for k in LW.KEYS},
                                                 rss_mm=rss.tolist(), rss_norm_mm=float(np.linalg.norm(rss)), fit_based_rss_norm_mm=fit_rss))
json.dump(out, open(os.path.join(HERE, "compare.json"), "w"), indent=1)
print("\nwrote", os.path.join(HERE, "compare.json"))
