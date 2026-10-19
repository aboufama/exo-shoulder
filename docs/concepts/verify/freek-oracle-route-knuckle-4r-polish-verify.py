#!/usr/bin/env python3
"""Independent verifier (skeptic) of the freek-oracle-route-knuckle-4r FINAL POLISH claim (2026-10-18,
docs/research/freek-oracle-route-knuckle-4r_final_polish.md: pick1 fe1-g10-7 / pick3 fe1-g8-5 vs the verified config).

What this file re-does on its own path (it never edits the row's verified fields, a model, a bench or a judge):
  * the VERIFIED config comes from the model's own params (FO.params({"q3max": 86}) = KR.PARAMS + the k33 priced file),
    not from the polisher's NOM + priced; a pick is its nominal file priced by tools/env_polish.priced (the shared pricing
    tool) and the script checks that the same tool reproduces the verified priced values from the verified nominal.
  * wear: RM.freeze (fit FAST, wear EXACT frozen) -> run -> near-touch -> the original verifier's flood_connected with
    its one fold reading kin_nodes_model (kinematic continuity) -> per-pose dump (alignment_paired._dump_bench).
  * contact-aware continuity on the wear bench: the kinematic flood's connected grid nodes, restricted to the grid poses
    the worn frozen design TAKES without contact, re-flooded from the rest seeds (the bench's ws poses are grid poses).
    Only the bench's own ws poses carry a contact reading, so a node off the bench counts as passable (an upper bound on
    connectivity; stated).
  * th fold margin from the MEMBER FRAMES M.T(m, i) (m 1 = link 1a + hub K, 7 = link 1b + hub 2, 2 = link 2): jK = R1 uK,
    j2 = R7 u2, j3 = R2 u3, th = angle(u1, j3); one reading per state's moving chain (0: J1-J2-J3; 1: min(J1-K-J3, J1-J2-J3);
    2: min(J1-K-J2, J1-J2-J3)) and the family reading (forced states: min(J1-K-J3, J1-J2-J3)).
  * the J3 stop's own angle at engaged poses (the original verifier's stop_report) and the stop-refusal side reading
    (the polisher's stop_refusal: refused poses worn without the dowel, same frozen shape; refusals that are kit contacts
    counted as contacts).

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 <this> claim <envh|fit60> <held|bench> <VER|pick.json> OUT.json
    CB_FOLD_MARGIN=5.5 python3 <this> heldcheck OUT.json        (envh / env draws vs held-out: identity + distance)
"""
import json, math, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_argv = sys.argv; sys.argv = [_argv[0]]
import freek_env_polish as FP                                  # noqa: E402  (bench_envh, stop_refusal; its V = the original verifier, unchanged)
sys.argv = _argv
V, FO, KR, RM, CB, KIT, EP, EB = FP.V, FP.FO, FP.KR, FP.RM, FP.CB, FP.KIT, FP.EP, FP.EB
V.VDesign.OWN = False
assert RM.kin_nodes is V.kin_nodes_model                       # one fold reading (the verified one)
FREE = list(FP.FREE)


def params_of(which):
    if which == "VER":
        P = FO.params({"q3max": 86.0}); P.pop("_seed", None); return P, dict(src="FO.params(q3max 86) (verified row path)")
    Pn = json.load(open(which)); Pp, info = EP.priced(KR, Pn)
    return Pp, dict(src=os.path.relpath(which, REPO), price=info, nominal={k: Pn[k] for k in FREE})


def pricing_check():
    """the shared pricing tool on the verified NOMINAL must give the verified PRICED values"""
    Pv, _ = params_of("VER"); Pp, info = EP.priced(KR, dict(FP.NOM))
    diff = {k: [Pv.get(k), Pp.get(k)] for k in set(Pv) | set(Pp) if not k.startswith("_") and
            (not isinstance(Pv.get(k), (int, float)) or not isinstance(Pp.get(k), (int, float)) or abs(float(Pv.get(k)) - float(Pp.get(k))) > 1e-3)}
    return dict(diff=diff, ok=not diff)


def member_margins(M, B, tk):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; st = np.asarray(M.kstate); dm = RM.dmargin; ang = RM.ang
    rows = []
    for i in tk:
        R1, _ = M.T(1, i); R7, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R7 @ u2; j3 = R2 @ u3; th = float(ang(u1, j3)); a1e = float(ang(u1, j2)); a2e = float(ang(j2, j3))
        b1 = float(ang(u1, jK)); cK3 = float(ang(jK, j3)); cK2 = float(ang(jK, j2))
        meff = float(dm(th, a1e, a2e)); msub = float(dm(th, b1, cK3)); kdy = float(dm(a1e, b1, cK2))
        s = int(st[i]); one = meff if s == 0 else (min(msub, meff) if s == 1 else min(kdy, meff)); fam = meff if s == 0 else min(msub, meff)
        rows.append((i, s, one, fam, float(np.degrees(np.arccos(np.clip(j2 @ (R2 @ u2), -1, 1))))))
    if not rows: return None
    one = np.array([r[2] for r in rows]); fam = np.array([r[3] for r in rows]); ax = np.array([r[4] for r in rows])
    w = rows[int(np.argmin(one))]
    return dict(one_min=round(float(one.min()), 2), one_lt5=int((one < 5 - 1e-6).sum()), one_min_at=dict(i=int(w[0]), state=w[1], kind=B.kind[w[0]]),
                family_min=round(float(fam.min()), 2), family_lt5=int((fam < 5 - 1e-6).sum()),
                j2_axis_link1b_vs_link2_maxdeg=round(float(ax.max()), 4), states={str(k): int(sum(r[1] == k for r in rows)) for k in (0, 1, 2)})


def contact_aware(Mk, B, tk, conn):
    """re-flood the kinematic graph with the bench's ws poses that are NOT taken (contact / refused) removed"""
    Z, Wg, POSE, HG = RM.ws_grid(); D = Mk.D; R_tol = float(Mk.p["R_tol"])
    okn, qq, sgn, st, own = RM.kin_nodes(D, HG, R_tol)
    key = {(float(x[0]), float(x[1]), float(x[2])): j for j, x in enumerate(POSE)}
    tks = set(tk); blocked = 0; nodes = okn.copy()
    for i in range(len(B.idx)):
        if B.kind[i] != "ws": continue
        j = key.get((float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])))
        if j is not None and i not in tks and nodes[j]: nodes[j] = False; blocked += 1
    seeds = nodes & (POSE[:, 1] == 0) & (st == 0)
    cn, stats = RM.flood(POSE, HG, nodes, seeds, D, R_tol)
    ck = {(float(POSE[j, 0]), float(POSE[j, 1]), float(POSE[j, 2])) for j in np.nonzero(cn)[0]}
    drop = [i for i in tk if B.kind[i] == "ws" and (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])) not in ck]
    res0 = list(B.res)
    for i in drop: B.res[i] = None
    rc = B.report(); B.res = res0
    return dict(blocked_nodes=blocked, connected=int(cn.sum()), dropped=len(drop), gap=rc["gap"], reach=rc["reach"])


def claim(fit, wear, which, outp):
    import alignment_paired as AP
    t0 = time.time(); P, src = params_of(which)
    FIT = FP.bench_envh() if fit == "envh" else RM.PV.fast_bench(60, 160); assert FIT.mode == "fast"
    W = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360); assert W.mode == "exact"
    Mk, fitr, M1, _ = RM.freeze(FIT, W, dict(P), FO.KModel); rk = Mk.run(); nt = RM.near_touch(Mk, W); tk = RM.taken_list(W)
    poses = AP._dump_bench(Mk, W); gp = AP.gap_parts(poses); depth = round(-sum(p["min_mm"] for p in poses if p["contact"]), 2)
    conn = V.flood_connected(Mk, W, tk)
    import traceback
    try: ca = contact_aware(Mk, W, tk, conn)
    except Exception as e: ca = dict(error=repr(e), trace=traceback.format_exc()[-800:])          # noqa: BLE001
    try: mm = member_margins(Mk, W, tk)
    except Exception as e: mm = dict(error=repr(e), trace=traceback.format_exc()[-800:])          # noqa: BLE001
    stop = V.stop_report(Mk, W)
    side, res1 = FP.stop_refusal(Mk, W, list(W.res))
    if res1 is not None:
        r0 = list(W.res); W.res = res1; side["gap_refusals_as_contacts"] = W.report()["gap"]; W.res = r0
    else: side["gap_refusals_as_contacts"] = rk["gap"]
    oh = [int(sum(1 for i in tk if W.kind[i] == "ws" and W.poses[i]["elev"] >= 140)), int(sum(1 for i in range(len(W.idx)) if W.kind[i] == "ws" and W.poses[i]["elev"] >= 140))]
    out = dict(id=FP.ID, verifier="independent (polish skeptic)", fit=fit, wear=wear, which=which if which == "VER" else os.path.relpath(which, REPO), params_src=src,
               priced={k: P.get(k) for k in FREE}, n=len(W.idx), fold_margin=KIT.FOLD_MARGIN, fit_report=fitr,
               static=dict({k: rk[k] for k in FO.KEYS}, near=nt["gap_near1"], near1_poses=nt["near1_poses"], min_mm=nt["min_mm"]),
               recomputed=gp, contact_poses=gp["contact_poses"], contact_depth_mm=depth, overhead140_ws=oh,
               connected=conn, contact_aware=ca, member_margins=mm, j3stop=stop, stop_refusal=side,
               gap=conn["gap"], near=conn["near"], secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    json.dump(dict(id=FP.ID, fit=fit, wear=wear, which=out["which"], poses=poses, recomputed=gp), open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    print(json.dumps({k: out[k] for k in ("fit", "wear", "which", "gap", "near", "contact_poses", "contact_depth_mm", "overhead140_ws", "member_margins", "contact_aware", "secs")}, default=float), flush=True)
    print(json.dumps(dict(stop=stop, side={k: side[k] for k in ("refused", "kit_contacts", "gap_refusals_as_contacts")}, dropped=conn["dropped"]), default=float), flush=True)


def heldcheck(outp):
    """every envh pose vs the held-out set: identity, coordinate (Chebyshev) and humerus-orientation distance; and the env draw
    code path: which inputs (no held-out outcomes) feed the draw"""
    Z = CB._poses_all(); hidx, _ = EB.held_idx(); B = FP.bench_envh(exact=True); idx = np.asarray(B.idx)
    ws = idx[[i for i, k in enumerate(B.kind) if k == "ws"]]; cl = idx[[i for i, k in enumerate(B.kind) if k == "clip"]]
    HP = Z["POSE"][hidx, :3].astype(float); P = Z["POSE"][ws, :3].astype(float)
    d = np.abs(P[:, None, :] - HP[None, :, :]); d[..., 2] = np.minimum(d[..., 2], 360 - d[..., 2]); cheb = d.max(-1).min(1)
    HG = Z["HG"].astype(float); Rh = HG[hidx]; Rw = HG[ws]
    tr = np.einsum("nij,mij->nm", Rw, Rh); geo = np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1))).min(1)
    HH = EB._hum_thorax(Z, hidx); HW = EB._hum_thorax(Z, ws); geoh = EB._geo(HW, HH).min(1)
    names = list(Z["NAMES"]); held_clips = {names.index(x) for x in ("Wave", "Walking arm swing")}
    out = dict(envh_ws=len(ws), envh_clip=len(cl), identical_to_held=int(len(set(idx.tolist()) & set(hidx.tolist()))),
               clips_from_held_clips=int(sum(int(c) in held_clips for c in Z["CID"][idx])),
               min_cheb_coord_deg=round(float(cheb.min()), 3), n_cheb_lt2=int((cheb < 2).sum()),
               min_geo_HG_glenohumeral_deg=round(float(geo.min()), 3), n_geo_lt2=int((geo < 2).sum()),
               min_geo_humerus_deg=round(float(geoh.min()), 3), n_geoh_lt2=int((geoh < 2).sum()))
    json.dump(out, open(outp, "w"), indent=1); print(json.dumps(out))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "claim": claim(a[1], a[2], a[3], a[4])
    elif a[0] == "heldcheck": heldcheck(a[1])
    elif a[0] == "pricing": print(json.dumps(pricing_check(), default=float))
    else: raise SystemExit(__doc__)
