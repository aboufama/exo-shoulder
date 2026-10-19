"""Adversarial verifier for isoceles-shortdyad-pinknee-3r (round 501, G1, 2026-10-19). The claim: the pre-registered
pick isoA-g18-0 (kj=1 joggled knee, a1 40.97 / a2 53.63, J2 seat re-solved, lE 115 on the clamp), fit on Bench(60,160)
FAST and worn frozen on Bench(110,360) exact = 27.91, held out 30.30.

This harness does NOT run the claimant's model file. It builds the claimed configuration (the claim read's
params_resolved: every key, so no default can differ) in the crest-knee verifier's OWN instance of the model
(docs/concepts/verify/crest-knee-3r.py -> crest-knee-3r.py -> skin-normal-3r-pin-knee.py, switched to CK.JogModel by
docs/concepts/verify/crest-knee-3r-joggle.py), and applies, on the frozen wear:

  * the model's own checks (closure, R_tol, knee window, clip continuity, part-part clearances incl. the fly-over E box,
    contact-only walls and crowns);
  * the pin-knee verifier's extra checks (independent 3D closure, knee vs hub 3 upper, E boss vs hubs / links);
  * the crest checks (J3 window, knee window [ang_min, 180 - ang_min], th fold margin, hub-centre distances, drift);
  * the joggle checks (every knee slice vs E strap / hub 3 / hubs / links, pad vs boss / strap, bent-bar feasibility);
  * this verifier's seat checks: the J2 re-solve (angle(d1, d2) = a1, angle(d2, d3) = a2 on the claimed branch), user
    ruling 4 for J1 (search seat_ok: az -110..135, el -20..90, anterior <= 0.20), O20 at every hub (ruling 2), MR63ZZ
    knee stack 6 mm and ang_min >= 25.22 (lead's build rule), the lE clamp;
  * the continuity flood (CLAUDE.md continuity rule; the knee branch and the J3 window are walls) on the full workspace
    grid, and the connected gap;
  * per-pose dumps (tools/alignment_paired.py format) under docs/alignment/remeasure/<id>_v_<wear>_perpose.json (T5 rule).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/isoceles-shortdyad-pinknee-3r.py wear <bench|held> <out.json>
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/isoceles-shortdyad-pinknee-3r.py flood <out.json> <bench_wear.json>
"""
import importlib.util, json, math, os, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("ck_joggle_verifier_for_iso", os.path.join(HERE, "crest-knee-3r-joggle.py"))
JV = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(JV)
V, CB, CK, PK, PV = JV.V, JV.CB, JV.CK, JV.PK, JV.PV
S = PK.S
ID = "isoceles-shortdyad-pinknee-3r"
assert V.CK.Model is V.CK.JogModel
CLAIM = json.load(open(os.path.join(HERE, f"{ID}_claim_bench_frozen.json")))
P = {k: v for k, v in CLAIM["params_resolved"].items() if k not in ("unresolved", "legal_j1", "h2clip")}
assert P["kj"] == 1 and P["stk"] == 6.0 and P["ang_min"] >= 25.22
V.ROW = {"best_params": P}                                   # the harness's flood reads ROW["best_params"]
KEYS = V.KEYS; REM = V.REM


def seat_checks():
    d1 = S.bvec(P["az1"], P["el1"]); d2 = S.bvec(P["az2"], P["el2"])
    ang = lambda a, b: math.degrees(math.acos(float(np.clip(a @ b, -1, 1))))
    D = PK.Design(dict(P)); u = D.u
    out = dict(a_design_deg=[round(math.degrees(a), 4) for a in D.A],
               a1_claim=P["a1"], a2_claim=P["a2"], angle_d1_d2=round(ang(d1, d2), 4), angle_u1_u2=round(ang(u[0], u[1]), 4),
               angle_u2_u3=round(ang(u[1], u[2]), 4), branch_sign=float(np.sign(u[1] @ np.cross(u[0], u[2]))), br_claim=P["br"],
               j1_seat=dict(az=P["az1"], el=P["el1"], anterior=round(float(d1[0]), 4),
                            ok=bool(-110 <= P["az1"] <= 135 and -20 <= P["el1"] <= 90 and d1[0] <= 0.20)),
               hub_r=[P["rad1"], P["rad2"], P["rad3"]], o20_all=all(float(P[f"rad{k}"]) == 10.0 for k in (1, 2, 3)),
               knee=dict(stk=P["stk"], ang_min=P["ang_min"]), lE=P["lE"], lE_on_clamp=bool(P["lE"] >= 115.0 - 1e-9),
               b=[P["b1"], P["b2"], P["b3"]])
    return out


def wear(which, outp):
    t0 = time.time()
    M1, P2, fit, ji = V.fit_fast(dict(P))
    B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else V.held_bench()
    M = V.worn(M1, P2, B); r = M.run(); model = {k: r[k] for k in KEYS}
    assert type(M).__mro__[1] is CK.JogModel
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    aud0 = PK.audit(M, B)
    ex, bad1 = PV.extra_checks(M, B)
    cc, marg = V.crest_checks(M, B, P2)
    jg, bad2 = JV.joggle_checks(M, B)
    bad = set(bad1) | set(bad2)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = PK.audit(M, B)
    import alignment_paired as AP
    poses = AP._dump_bench(M, B)
    for row in poses:
        i = row["i"]; row.update(why=str(M.why[i]), th_margin=round(float(marg[i]), 3), q3p=round(float(M.q3p[i]), 2), knee=round(float(M.K["ang"][i]), 2))
    try: git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: git = None
    dump = dict(id=ID, wear=which, params=P, frozen=corrected, report=rc, poses=poses, recomputed=AP.gap_parts(poses),
                secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=git,
                note="written by docs/concepts/verify/isoceles-shortdyad-pinknee-3r.py (crest-knee + pin-knee + joggle verifier checks applied)")
    os.makedirs(REM, exist_ok=True); dpath = os.path.join(REM, f"{ID}_v_{which}_perpose.json"); json.dump(dump, open(dpath, "w"), default=float)
    contacts = [dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                     depth=round(float(np.min(B.res[i])), 2)) for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) < 0]
    el = np.array([p["elev"] for p in B.poses]); ax = np.array([p["axial"] for p in B.poses]); kind = np.array(B.kind); tk = set(V.taken_list(B))
    ab = np.nonzero((np.abs(ax) >= 150) & (kind == "ws"))[0]; oh = np.nonzero((el >= 140) & (kind == "ws"))[0]
    # conditioning |u1 . (u2 x w)| over the corrected taken set (the round-501 judge's red-team number; H1's worst 0.233)
    D = M.D; u1, u2, u3 = D.u; w = np.einsum("nij,j->ni", M.Q, u3); p2 = S.rotm(u1, M.q[:, 0]) @ u2
    det = np.abs(np.einsum("j,nj->n", u1, np.cross(p2, w))); tkl = sorted(tk)
    cond = dict(det_min=round(float(det[tkl].min()), 4) if tkl else None, below_h1=int(sum(1 for i in tkl if det[i] < 0.233)))
    B.res = res0
    out = dict(wear=which, params=P, model_class="JogModel", mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, j3stop_fit=ji,
               model=model, why=why, model_audit=aud0, extra=ex, joggle=jg, removed=sorted(int(i) for i in bad), crest=cc, seats=seat_checks(),
               corrected=corrected, corrected_audit=aud, cond=cond, contacts=contacts,
               contact_depth_sum=round(float(sum(c["depth"] for c in contacts)), 2),
               axial150=dict(total=int(len(ab)), taken=int(sum(1 for i in ab if i in tk))),
               overhead=dict(total=int(len(oh)), taken=int(sum(1 for i in oh if i in tk))),
               dump=dict(path=os.path.relpath(dpath, REPO), recomputed=dump["recomputed"]), secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(wear=which, mode=B.mode, fit=fit, model=model, corrected=corrected, removed=len(bad), near1=aud.get("gap_near1"),
                          crest=cc, joggle=jg, seats=out["seats"], cond=cond, overhead=out["overhead"],
                          extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad", "spans_deg", "pad")},
                          recomputed=dump["recomputed"], contacts=contacts, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "wear": wear(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "flood": V.flood(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif sys.argv[1] == "seats": print(json.dumps(seat_checks(), default=float))
