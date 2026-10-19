"""Usage: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r-v3.py <bench|held>
Independent re-verification (round-3 skeptic) of crest-knee-3r flat cell: reuses the committed harness's fit/wear
path, adds own-angle checks from body transforms (J2 branch arcs, J3 window on the true relative angle, knee pins),
sample-density audit, pin-a stack check; writes per-pose dumps to the scratchpad."""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot
from scipy.spatial import cKDTree
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")); OUT = os.path.join(REPO, "docs", "alignment", "remeasure"); VOUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("ckv", os.path.join(REPO, "docs/concepts/verify/crest-knee-3r.py"))
V = importlib.util.module_from_spec(sp); sp.loader.exec_module(V); V.REM = OUT
CB = V.CB; CK = V.CK; PK = V.PK; S = PK.S
which = sys.argv[1]; P = dict(V.ROW["best_params"]); t0 = time.time()
M1, P2, fit, ji = V.fit_fast(P)
B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
M = V.worn(M1, P2, B); r = M.run(); model = {k: r[k] for k in V.KEYS}
why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
ex, bad = PV_ex = V.PV.extra_checks(M, B)
cc, marg = V.crest_checks(M, B, P2)
tk = V.taken_list(B); D = M.D; u = D.u
def signed(Rrel, ax):
    rv = Rot.from_matrix(Rrel).as_rotvec(); ang = np.linalg.norm(rv, axis=-1)
    axn = rv / np.maximum(ang, 1e-12)[:, None]; dev = np.degrees(np.arccos(np.clip(np.abs(axn @ ax), -1, 1)))
    s = np.sign(axn @ ax); return np.degrees(ang * s), np.where(ang > 1e-6, dev, 0.0)
mine = {}
kin = np.nonzero(M.kin_ok)[0] if hasattr(M, "kin_ok") else np.arange(len(B.idx))
allp = np.arange(len(B.idx))
R1 = np.stack([M.T(1, i)[0] for i in allp]); R2 = np.stack([M.T(2, i)[0] for i in allp]); R3 = np.stack([M.T(3, i)[0] for i in allp])
R5 = np.stack([M.T(5, i)[0] for i in allp]); R6 = np.stack([M.T(6, i)[0] for i in allp])
q2t, dev2 = signed(np.einsum("nji,njk->nik", R1, R2), u[1])
q3t, dev3 = signed(np.einsum("nji,njk->nik", R2, R3), u[2])
pa, deva = signed(np.einsum("nji,njk->nik", R3, R6), D.sn)
pb, devb = signed(np.einsum("nji,njk->nik", R6, R5), D.sn)
th = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", M.Q, u[2]) @ u[0], -1, 1)))
a1, a2 = [math.degrees(a) for a in D.A]
tkk = np.array(tk)
# J2: th(q2) is symmetric about the fold / stretch q2; split the taken poses by the side of the fold they sit on
sgn = np.sign(np.sin(np.radians(q2t - q2t[tkk][np.argmin(th[tkk])])))   # crude, refined below
# exact: th from q2 alone -> find q2 of the fold (th min) by scanning
qq = np.radians(np.arange(-180, 180, 0.25)); Rq = Rot.from_rotvec(qq[:, None] * u[1][None]).as_matrix()
w = np.einsum("nij,j->ni", Rq, u[2]); thq = np.degrees(np.arccos(np.clip(w @ u[0], -1, 1)))
qf = math.degrees(qq[np.argmin(thq)]); qs = math.degrees(qq[np.argmax(thq)])
rel = (q2t - qf) % 360; side = np.where((rel > 0) & (rel < (qs - qf) % 360), "+", "-")
mine["J2"] = dict(axis_dev_deg_max=round(float(dev2[tkk].max()), 4), q2_fold=round(qf, 2), q2_stretch=round(qs, 2), th_range_q=[round(float(thq.min()), 2), round(float(thq.max()), 2)],
                  taken_side_counts={s: int((side[tkk] == s).sum()) for s in "+-"}, kin_side_counts={s: int((side[kin] == s).sum()) for s in "+-"},
                  q2_taken_range=[round(float(q2t[tkk].min()), 2), round(float(q2t[tkk].max()), 2)],
                  th_from_q2_vs_model_maxerr=round(float(np.abs(np.interp(((q2t[tkk] + 180) % 360) - 180, np.degrees(qq), thq) - th[tkk]).max()), 3))
lo, wid = P2["j3win"]; off = (q3t - M.q3p + 180) % 360 - 180
mine["J3"] = dict(axis_dev_deg_max=round(float(dev3[tkk].max()), 4), q3true_minus_q3p_spread=round(float(np.ptp(np.unwrap(np.radians(off[tkk])) * 180 / math.pi)), 4),
                  q3true_minus_q3p_mean=round(float(off[tkk].mean()), 3), q3p_taken_inside_window=int(sum(((M.q3p[i] - lo) % 360) <= wid for i in tk)), n_taken=len(tk))
mine["knee_pins"] = dict(pin_a_axis_dev=round(float(deva[tkk].max()), 4), pin_b_axis_dev=round(float(devb[tkk].max()), 4),
                         pin_a_range=[round(float(pa[tkk].min()), 2), round(float(pa[tkk].max()), 2)], pin_b_range=[round(float(pb[tkk].min()), 2), round(float(pb[tkk].max()), 2)])
# sample density per part (median / max nearest-neighbour spacing, mm)
dens = {}
for nm, (m, X) in M.rigid.items():
    if len(X) > 2:
        d = cKDTree(X).query(X, k=2)[0][:, 1]; dens[nm] = dict(n=int(len(X)), nn_med=round(float(np.median(d)), 2), nn_max=round(float(d.max()), 2))
for nm, (m, X) in M.link_pts.items():
    if len(X) > 2:
        d = cKDTree(X).query(X, k=2)[0][:, 1]; dens[nm] = dict(n=int(len(X)), nn_med=round(float(np.median(d)), 2), nn_max=round(float(d.max()), 2))
mine["sample_density"] = dens
mine["contact_only_sets"] = [dict(member=int(m), n=int(len(X))) for (m, X) in M.contact]
# pin a stack (flat knee): E strap top within 8.5 mm of pin a vs the knee link underside
tp = M.p["tp"]; lE = float(M.p["lE"]); xs = M._Ex; hx = M.hEx
near = xs >= lE - 8.5; out_boss = (xs >= lE - 8.5) & (xs < lE - PK.BOSS_R)
mine["pin_a_stack"] = dict(knee_underside=round(float(M.tr + tp + S.RUN), 3), strap_top_max_near=round(float(hx[near].max() + S.T_LINK), 3),
                           strap_top_max_outside_boss=round(float(hx[out_boss].max() + S.T_LINK), 3) if out_boss.any() else None,
                           clearance_near=round(float(M.tr + tp + S.RUN - hx[near].max() - S.T_LINK), 3))
# fold margin and J3 margin on the true angles
mine["th_margin_min_taken"] = round(float(marg[tkk].min()), 3)
for i in bad: B.res[i] = None
rc = B.report(); corrected = {k: rc[k] for k in V.KEYS}; aud = PK.audit(M, B)
import alignment_paired as AP
poses = AP._dump_bench(M, B)
for row in poses:
    i = row["i"]; row.update(why=str(M.why[i]), th_margin=round(float(marg[i]), 3), q3p=round(float(M.q3p[i]), 2), knee=round(float(M.K["ang"][i]), 2), j2side=str(side[i]))
contacts = [dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"], depth=round(float(np.min(B.res[i])), 2))
            for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) < 0]
el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
ov = [i for i in range(len(B.idx)) if kind[i] == "ws" and el[i] >= 140]
out = dict(wear=which, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", params=P, fit_fast=fit, j3win=P2.get("j3win"), model=model, why=why,
           removed=sorted(int(i) for i in bad), corrected=corrected, near1=aud.get("gap_near1"), near2=aud.get("gap_near2"),
           extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad") if k in ex}, crest=cc, mine=mine,
           contacts=contacts, contact_depth_sum=round(float(sum(c["depth"] for c in contacts)), 2),
           overhead_ws=dict(total=len(ov), taken=int(sum(1 for i in ov if i in set(tk)))), recomputed=AP.gap_parts(poses), secs=round(time.time() - t0, 1))
json.dump(dict(id=CK.ID, wear=which, params=P, frozen=corrected, poses=poses, recomputed=out["recomputed"], exact=out["exact"]),
          open(os.path.join(OUT, f"crest-knee-3r_v3_{which}_perpose.json"), "w"), default=float)
json.dump(out, open(os.path.join(VOUT, f"crest-knee-3r-v3_{which}.json"), "w"), indent=1, default=float)
print(json.dumps(out, default=float)[:4000], flush=True)
