"""Auditor adapter (new file, 2026-10-18): re-wear freek-oracle-route-knuckle-4r CELL B for the alignment audit.

tools/alignment_audit.py remeasure needs a model-level frozen() / frozen_held(); this model has none (its claim runs
through its own `law` mode). This adapter runs THAT law path UNCHANGED (fit Bench(60,160) fast -> frozen exact
Bench(110,360) or the held-out set, J2 on its own priced slot, J3 own-angle dowel at q3max, the model's own kinematic
flood fill) and only reads more out of the finished run:
  * tools/alignment_audit.deep_audit on the static AND the connected set (near-touch 1 / 2 / 3 mm, clip metal histogram,
    band 3-14 mm, coordinate spans)
  * per pose dumps in tools/alignment_paired.py format (static and connected; the connected one is the claim's set)
  * the fold margin of every taken pose, read in th (the kit's dyad_margin of the effective dyad (a1e, a2), the metric
    the kitrule harness verifies), split by state (A / stretched / J3-stop engaged)
  * K (dK) and q3 spans over the taken poses, J3-stop engagements, the poses the J3 stop refuses
It never edits the model, a bench, a judge or a row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_remeasure_freek.py bench|held [q3max]
        -> docs/alignment/remeasure/freek-oracle-route-knuckle-4r_<wear>.json (+ _conn_perpose.json = connected = the claim's set,
           _static_perpose.json; NOT _perpose.json, which the design's verifier writes)
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_remeasure_freek.py margin bench|held   (after the above)
"""
import json, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA  # noqa: E402
import alignment_paired as AP  # noqa: E402

RID = "freek-oracle-route-knuckle-4r"
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")


def main(wear, q3max=86.0):
    t0 = time.time()
    mod = AA._load("aa_freek_adapter", os.path.join(AA.MODELS, RID + ".py"))
    RM, CB, KR = mod.RM, mod.CB, mod.KR
    P = mod.params({"q3max": q3max}); P.pop("_seed", None)
    mod.ODesign.SLOT55 = False; mod.ODesign.TAB = None            # exactly the model's `law` mode
    fitB = RM.PV.fast_bench(60, 160)
    B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
    Mk, fitr, M1, _ = RM.freeze(fitB, B, dict(P), mod.KModel); rk = Mk.run()
    static = {k: rk[k] for k in KEYS}; nt = RM.near_touch(Mk, B); tk = RM.taken_list(B)
    deep_s = AA.deep_audit(Mk, B); dump_s = AP._dump_bench(Mk, B)
    n = len(B.idx); el = np.array([p["elev"] for p in B.poses])
    # per-pose kinematic state of the frozen design (re-solve on the bench orientations, as the kit's _report does)
    D = Mk.D; q, okk, *_ = D.ik(Mk.Q)
    m3e = np.asarray(D._m3e, float); dK = np.degrees(np.abs(np.asarray(D._dK, float))); st = np.asarray(D._state)
    q3 = np.degrees(mod.PK.wrap(q[:, 2])); w = Mk.Q @ D.u[2]; th = np.degrees(np.arccos(np.clip(w @ D.u[0], -1, 1)))
    ks = np.asarray(getattr(Mk, "kstate", st))
    def span(a, idx):
        idx = [i for i in idx if np.isfinite(a[i])]
        return [round(float(np.min(a[idx])), 2), round(float(np.max(a[idx])), 2)] if idx else None
    marg = {}
    for lab, sel in (("all", tk), ("stateA", [i for i in tk if ks[i] == 0]), ("stretched", [i for i in tk if ks[i] == 1]),
                     ("j3stop", [i for i in tk if ks[i] == 2])):
        if sel:
            j = int(np.argmin(m3e[sel])); i = sel[j]
            marg[lab] = dict(n=len(sel), min_margin_th=round(float(m3e[i]), 3), at=dict(i=int(i), kind=B.kind[i], **{k: B.poses[i][k] for k in ("plane", "elev", "axial")}),
                             n_below5=int(sum(1 for x in sel if m3e[x] < 5.0)), n_below5p5=int(sum(1 for x in sel if m3e[x] < 5.5 - 1e-6)))
    # the poses the J3 stop refuses (q3 past q3max with no legal K): what were they in the kit?
    why = {k: int((Mk.why == k).sum()) for k in set(Mk.why.tolist()) if k}
    # continuity: the model's own flood (copied from its law branch, unchanged)
    Z, Wg, POSE, HG = RM.ws_grid(); R_tol = float(Mk.p["R_tol"]); _ = D.ik(HG[:2])
    okn, qq, sgn, stn, own = RM.kin_nodes(D, HG, R_tol); seeds = okn & (POSE[:, 1] == 0) & (stn == 0)
    cn, stats = RM.flood(POSE, HG, okn, seeds, D, R_tol)
    ck = {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}
    drop = [i for i in tk if B.kind[i] == "ws" and (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])) not in ck]
    res0 = list(B.res)
    for i in drop: B.res[i] = None
    rc = B.report(); conn = {k: rc[k] for k in KEYS}; deep_c = AA.deep_audit(Mk, B); dump_c = AP._dump_bench(Mk, B); B.res = res0
    tkc = [i for i in tk if i not in set(drop)]
    ov = dict(ws=int(sum(1 for i in range(n) if el[i] >= 140 and B.kind[i] == "ws")),
              taken_static=int(sum(1 for i in tk if el[i] >= 140 and B.kind[i] == "ws")),
              taken_connected=int(sum(1 for i in tkc if el[i] >= 140 and B.kind[i] == "ws")))
    raised = dict(ws=int(sum(1 for i in range(n) if el[i] >= 90 and B.kind[i] == "ws")),
                  taken_connected=int(sum(1 for i in tkc if el[i] >= 90 and B.kind[i] == "ws")))
    contacts = sorted([(float(min(np.min(B.res[i]), Mk.cmin.get(i, 1e9))), int(i)) for i in range(n) if B.res[i] is not None and float(np.min(B.res[i])) < 0])
    out = dict(id=RID, wear=wear, adapter="tools/alignment_remeasure_freek.py", params=dict(q3max=q3max, seed="k33", cell="B"),
               frozen=dict(**conn, near=deep_c.get("gap_near1"), ws_taken=sum(1 for i in tkc if B.kind[i] == "ws"), set="connected (the claim)"),
               frozen_static=dict(**static, near=nt["gap_near1"], ws_taken=sum(1 for i in tk if B.kind[i] == "ws")),
               fit_fast=fitr, deep=deep_c, deep_static=deep_s, why=why, fold_margin_th=marg, fold_margin_rule=float(mod.KIT.FOLD_MARGIN),
               spans_taken=dict(dK=span(dK, tk), q3=span(q3, tk), th=span(th, tk), dK_j3stop=span(dK, [i for i in tk if ks[i] == 2]),
                                q3_j3stop=span(q3, [i for i in tk if ks[i] == 2])),
               states_taken={str(s): int(sum(1 for i in tk if ks[i] == s)) for s in sorted(set(ks[tk].tolist()))} if tk else {},
               flood=dict(nodes=int(okn.sum()), seeds=int(seeds.sum()), connected=int(cn.sum()), islands=int((okn & ~cn).sum()), dropped=len(drop),
                          dropped_poses=[dict(i=int(i), **{k: B.poses[i][k] for k in ("plane", "elev", "axial")}) for i in drop], edges=stats),
               overhead140=ov, raised90=raised,
               contact_poses=[dict(mm=round(d, 3), i=i, kind=B.kind[i], **{k: B.poses[i][k] for k in ("plane", "elev", "axial")}) for d, i in contacts],
               secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    os.makedirs(AA.REM, exist_ok=True)
    json.dump(out, open(os.path.join(AA.REM, f"{RID}_{wear}.json"), "w"), indent=1, default=float)
    for lab, dmp, rep in (("_conn_perpose", dump_c, conn), ("_static_perpose", dump_s, static)):
        json.dump(dict(id=RID, wear=wear, params=out["params"], frozen=rep, report=rep, poses=dmp, recomputed=AP.gap_parts(dmp),
                       secs=out["secs"], exact=out["exact"], git=out["git"]), open(os.path.join(AA.REM, f"{RID}_{wear}{lab}.json"), "w"), default=float)
    print(json.dumps(dict(wear=wear, frozen=out["frozen"], static=out["frozen_static"], recomputed=AP.gap_parts(dump_c),
                          deep={k: v for k, v in deep_c.items() if k != "coord_spans"}, margin=marg, spans=out["spans_taken"], states=out["states_taken"],
                          flood={k: v for k, v in out["flood"].items() if k != "dropped_poses"}, overhead=ov, raised=raised, why=why, secs=out["secs"]), default=float))


def margin(wear, q3max=86.0):
    """the family fold-margin reading on every bench pose (RM.kin_nodes' 'own': min(m_sub, m_eff) wherever K is off its
    rest, the reading the flood fill and the lead verifier use) for the frozen design, crossed with the taken flags of the
    connected per-pose dump this adapter wrote (needs `main` first; no exact skin distances: only the fit + kinematics)"""
    mod = AA._load("aa_freek_adapter_m", os.path.join(AA.MODELS, RID + ".py")); RM, CB = mod.RM, mod.CB
    P = mod.params({"q3max": q3max}); P.pop("_seed", None); mod.ODesign.SLOT55 = False; mod.ODesign.TAB = None
    fitB = RM.PV.fast_bench(60, 160); B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
    Mk, fitr, M1, _ = RM.freeze(fitB, B, dict(P), mod.KModel)
    Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float); D = M1.D; R_tol = float(M1.p["R_tol"])
    ok, qq, sgn, st, own = RM.kin_nodes(D, Q, R_tol)
    dmp = json.load(open(os.path.join(AA.REM, f"{RID}_{wear}_conn_perpose.json")))["poses"]
    tk = [p["i"] for p in dmp if p["taken"]]
    bad5 = [i for i in tk if own[i] < 5.0 - 1e-6]; bad55 = [i for i in tk if own[i] < 5.5 - 1e-6]
    out = dict(wear=wear, n_taken=len(tk), own_min_taken=round(float(np.min(own[tk])), 3), states_taken={str(s): int(sum(1 for i in tk if st[i] == s)) for s in sorted(set(st[tk].tolist()))},
               taken_own_lt5=len(bad5), taken_own_lt5p5=len(bad55), taken_kin_refused=int(sum(1 for i in tk if not ok[i])),
               lt5=[dict(i=int(i), kind=dmp[i]["kind"], state=int(st[i]), own=round(float(own[i]), 2), **{k: dmp[i][k] for k in ("plane", "elev", "axial")}) for i in sorted(bad5, key=lambda j: own[j])],
               note="own = RM.kin_nodes margin (forced states: min(dmargin(th, b1, angle(jK, j3)), dmargin(th, a1e, a2e)); state A: dmargin(th, a1, a2)); "
                    "taken = the connected per-pose dump of this adapter")
    json.dump(out, open(os.path.join(AA.REM, f"{RID}_{wear}_familymargin.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "lt5"}, default=float), json.dumps(out["lt5"][:12], default=float))


if __name__ == "__main__":
    if sys.argv[1] == "margin": margin(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 86.0)
    else: main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 86.0)
