"""Independent verifier (skeptic) for underpass-bridge-relay-4r (claim: frozen exact Bench(110,360) chain-only gate 13.74 =
plain, score 95.00, at the envsel pick ant ii / delta 4.5 / up_clr 1.2 / postH 1.5 / tshc 2.5 / rl_fix 81.307 / hiE 49.0).

The claim model is imported UNCHANGED (docs/concepts/models/underpass-bridge-relay-4r.py, which patches the verified
offset-shortcar parent). On the same prepared wear this verifier adds the checks the model leaves out, then re-scores:

  X1  every chain part (all rigid and link sets AND the contact-only top / crown sets; no bump in this design) against
      every relay body: the raised shell sector [R_under, R_t], every support sector (posterior foot), the carriage sector,
      the T-nut flange as a carriage-frame SECTOR [R_under - 1, R_under] (the model reads the flange only against E and
      boss, by nearest sample - 1; the flange now hangs INTO the under-pass gap the chain runs through), the bracket
      (underside + 2 mm top layer) and the lug coil cylinder.
  X3  the constant-force coil's STRIP (diagnostic): the drum rides the carriage lug, so its strip runs from an arm-fixed
      anchor (the drum's bottom point at phi 0) to the drum's bottom point at phi - a straight chord in tension (no guide
      surface exists proximal of the shell band). Sampled 1 mm along x 1 mm across an 8 mm strip; skin and chain checked.
  rule: non-adjacent < 1 mm -> pose lost (unless its metal is in the skin: then it stays a contact, as the model does);
      the knee link vs the carriage-frame bodies (one body with the pad, pinned through pin b) at the 0.15 mm running gap;
      the pad is the carriage body's own part and is skipped against the carriage-frame bodies.
  drop (diagnostic): the shell underside, foot and flange lowered by the bridge's own 4 N tip deflection (uniform, an upper
      bound) - the jam rule read on the LOADED bridge.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/underpass-bridge-relay-4r-verify.py claim out.json
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/underpass-bridge-relay-4r-verify.py held out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("underpass_for_verify", os.path.join(REPO, "docs", "concepts", "models", "underpass-bridge-relay-4r.py"))
UP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(UP)
OM, PT, AA, CB = UP.OS, UP.PT, UP.AA, UP.CB
D2R = math.pi / 180
PICK = json.load(open(os.path.join(REPO, "docs", "concepts", "verify", "underpass-bridge-relay-4r", "pick.json")))
BASE = dict(UP.CLAIM_PARENT)


def _sector(Xw, RS, Qf, G, ax, r0, r1, sa, sb, ta, tb):
    h = (Xw @ RS) @ Qf; sv = h @ ax; rr = np.linalg.norm(AA._rad(h, ax), axis=1)
    az = np.degrees(np.arctan2(h @ G["f"], h @ G["e"])); mid = 0.5 * (ta + tb); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
    dr = np.maximum(0.0, np.maximum(rr - r1, r0 - rr)); dss = np.maximum(0.0, np.maximum(sa - sv, sv - sb))
    da = np.maximum(0.0, np.maximum(ta - azr, azr - tb)) * D2R * np.minimum(rr, r1)
    return float(np.sqrt(dr ** 2 + dss ** 2 + da ** 2).min())


def _strip_local(G, ax, width=8.0):
    """the CF strip's two end points in local coordinates (anchor = drum bottom at phi 0, arm frame; drum bottom, carriage
    frame) and the across offsets"""
    e, f = G["e"], G["f"]; s_c, az_c, r_c = G["coil_c"]; d = math.cos(az_c * D2R) * e + math.sin(az_c * D2R) * f
    P = s_c * ax + (r_c - 0.5 * G["coilD"]) * d
    return P, np.arange(-0.5 * width, 0.5 * width + 1e-9, 1.0)


def xcheck(S, hw, drop=0.0, strip=True):
    from scipy.spatial import cKDTree
    M, B, ax = S["M"], S["B"], S["ax"]
    rp = dict(S["rp"]); rp.update({k: hw[k] for k in hw if k in PT.DEF})
    G = PT.geometry(S["M1"], S["B1"], ax, rp); arm, car = PT.relay_points(G, ax)
    Ru, Rt, s0, hw_ = G["R_under"], G["R_t"], G["s0"], 0.5 * PT.SH_W
    br = car[G["car_tag"] == "bracket"]; rad = AA._rad(br, ax); rad /= np.maximum(np.linalg.norm(rad, axis=1, keepdims=True), 1e-9)
    br2 = np.r_[br, br + 2.0 * rad]
    HG0 = AA.Z0["HG"][B.idx].astype(float)
    names = list(M.rigid) + list(M.link_pts); kinds = ["rigid"] * len(M.rigid) + ["link"] * len(M.link_pts)
    parts = list(M.rigid.values()) + list(M.link_pts.values())
    sets = [(nm, m, X) for nm, (m, X) in zip(names, parts)]
    sets += [(f"c{k}:m{m}", m, Pc) for k, (m, Pc) in enumerate(M.contact) if len(Pc)]
    pad_m = M.rigid["pad"][0] if "pad" in M.rigid else None; knee_m = M.rigid["knee"][0] if "knee" in M.rigid else None
    nC = sum(len(X) for _, (m, X) in zip(names, parts))
    hcar = 0.5 * PT.CAR_W / Rt / D2R; tc = G["th0"]; sups = G.get("supports", [])
    Pst, offs = _strip_local(G, ax) if (strip and G.get("coil_frame") == "car") else (None, None)
    rows = []; worst = {}; pmin = {}; strip_rows = []; e_under = []
    for i in range(len(B.idx)):
        if B.res[i] is None: continue
        mn = float(np.min(B.res[i])); RS, Qp, Q0 = M.RS[i], M.Q[i], HG0[i]
        wbr = (br2 @ Qp.T) @ RS.T; tb_ = cKDTree(wbr); per = {}
        Ws = None
        if Pst is not None:                                   # X3 strip chord in world
            A = (Pst @ Q0.T) @ RS.T; Bp = (Pst @ Qp.T) @ RS.T; axw = (ax @ Q0.T) @ RS.T
            L = float(np.linalg.norm(Bp - A)); n = max(2, int(math.ceil(L / 1.0)) + 1)
            seg = A[None] + np.linspace(0, 1, n)[:, None] * (Bp - A)[None]
            Ws = (seg[:, None, :] + offs[None, :, None] * axw[None, None, :]).reshape(-1, 3) if L > 0.5 else None
        tst = cKDTree(Ws) if Ws is not None else None
        for nm, m, X in sets:
            w = M.world(m, i, X); adj = (m == knee_m); dd = {}
            dd["shell"] = _sector(w, RS, Q0, G, ax, Ru - drop, Rt - drop, s0 - hw_, s0 + hw_, G["lo"], G["hi"])
            for sp in sups: dd["sup_" + sp[0]] = _sector(w, RS, Q0, G, ax, sp[1] - drop, sp[2] - drop, *sp[3:])
            if m != pad_m:
                dd["car"] = _sector(w, RS, Qp, G, ax, Rt + 0.2 - drop, Rt + G["h_c"] - drop, s0 - 0.5 * PT.CAR_L, s0 + 0.5 * PT.CAR_L, tc - hcar, tc + hcar)
                if G.get("flange"): dd["flange"] = _sector(w, RS, Qp, G, ax, Ru - 1.0 - drop, Ru - drop, s0 - 4.0, s0 + 4.0, tc - hcar, tc + hcar)
                dd["bracket"] = float(tb_.query(w)[0].min()) - 1.0
                if G.get("coil_frame"): dd["coil"] = OM._coil_d(w, RS, Q0 if G["coil_frame"] == "arm" else Qp, G, ax)
                if tst is not None: dd["strip"] = float(tst.query(w)[0].min()) - 0.5
            per[nm] = (dd, adj)
            for k, v in dd.items():
                kk = f"{nm}|{k}"
                if v < worst.get(kk, (1e9,))[0]: worst[kk] = (round(v, 3), i)
        adjset = ("car", "flange", "bracket", "coil", "strip")
        cl_na = [(v, nm, k) for nm, (dd, adj) in per.items() for k, v in dd.items() if not (adj and k in adjset)]
        if cl_na:
            c0 = min(cl_na); pmin[i] = dict(mm=round(c0[0], 3), part=c0[1], hw=c0[2], metal=round(mn, 2))
        if "E" in per: e_under.append((round(per["E"][0]["shell"], 3), i))
        jam = []
        for nm, (dd, adj) in per.items():
            for k, v in dd.items():
                lim = 0.15 if (adj and k in adjset) else 1.0
                if v < lim: jam.append((nm, k, round(v, 3)))
        if Ws is not None:
            ds = float(B.dist(i, Ws).min())
            if ds < 1.0: strip_rows.append(dict(i=i, kind=B.kind[i], skin_mm=round(ds, 2), metal=round(mn, 2)))
            if ds < 0: jam.append(("skin", "strip", round(ds, 3)))
        if jam: rows.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")], metal_min=round(mn, 2),
                                 why=str(M.why[i]), jam=sorted(jam, key=lambda x: x[2])[:6]))
    # re-score: a NEW jam on a taken pose -> lost; the strip in the skin on a taken pose -> contact
    lost = [r["i"] for r in rows if r["metal_min"] >= 0 and any(j[0] != "skin" for j in r["jam"])]
    con = [r["i"] for r in rows if r["metal_min"] >= 0 and r["i"] not in lost and any(j[0] == "skin" for j in r["jam"])]
    keep = {j: B.res[j] for j in lost + con}
    for j in lost: B.res[j] = None
    for j in con: B.res[j] = np.r_[B.res[j], [-0.01]]
    rr_ = B.report(); rep = {k: rr_[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ch = [B.res[j][:nC] for j in range(len(B.idx)) if B.kind[j] == "clip" and B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    lc = np.concatenate(ch) if ch else np.zeros(0); ibc = round(float(((lc >= 2) & (lc <= 14)).mean()), 4) if len(lc) else 0.0
    gate = CB.gap_of(min(rep["inband14"], ibc), rep["follow"], rep["reach"], rep["contact"])
    ws = np.array(B.kind) == "ws"; tk = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    elev = np.array([p["elev"] for p in B.poses])
    for j, v in keep.items(): B.res[j] = v
    tkd = [j for j, v in pmin.items() if v["metal"] >= 0]
    margin = {f"lt{t:g}": int(sum(1 for j in tkd if pmin[j]["mm"] < t)) for t in (1.0, 1.1, 1.2, 1.5, 2.0)}
    margin["lowest"] = [dict(i=j, kind=B.kind[j], **pmin[j]) for j in sorted(tkd, key=lambda j: pmin[j]["mm"])[:15]]
    eu = sorted(v for v in e_under if B.res[v[1]] is not None and float(np.min(B.res[v[1]])) >= 0)
    e_tab = dict(min=eu[:8], lt1_1=sum(1 for v in eu if v[0] < 1.1), lt1_2=sum(1 for v in eu if v[0] < 1.2), lt1_31=sum(1 for v in eu if v[0] < 1.31),
                 lt1_5=sum(1 for v in eu if v[0] < 1.5), n=len(eu))
    return dict(drop=drop, nC=nC, R_under=Ru, R_t=Rt, defl=G.get("defl_mm"), clearance_margin_taken=margin, E_under_shell_taken=e_tab,
                extra_jam_rows=rows, n_extra_jam=len(rows), lost_new=len(lost), new_contacts=len(con), strip_near_skin=strip_rows[:30],
                rescored=dict(wear=rep, ib14_chain_only=ibc, gate_gap=round(gate, 2), ws_taken=int((ws & tk).sum()),
                              overhead=[int((ws & tk & (elev >= 140)).sum()), int((ws & (elev >= 140)).sum())]),
                closest={k: v for k, v in sorted(worst.items(), key=lambda kv: kv[1][0])[:40]})


def need_all(S, hw, use_bench=True):
    """the model's need scan, corrected: EVERY chain set incl. the contact-only top / crown sets (the E strap's top face is
    E + T_LINK along its skin normal: c23 on member 3), over the fit kin_ok frames (phi 0) and, if use_bench, this bench's
    poses the ideal relay takes (res0 >= 0; generous to the design: the bridge is placed on the bench it is read on)"""
    M1, M, B, ax = S["M1"], S["M"], S["B"], S["ax"]
    rp = dict(S["rp"]); rp.update({k: v for k, v in hw.items() if k in PT.DEF}); rp["rl_fix"] = 0.0
    G = PT.geometry(M1, S["B1"], ax, rp); e, f, s0, lo, hi, tc = G["e"], G["f"], G["s0"], G["lo"], G["hi"], G["th0"]
    hcar = math.degrees(0.5 * PT.CAR_W / G["R_t"]); HG0 = AA.Z0["HG"]
    frames = [(M1, int(j), M1.Q[j], M1.Q[j]) for j in np.nonzero(M1.kin_ok)[0]]
    if use_bench:
        frames += [(M, j, HG0[B.idx[j]].astype(float), M.Q[j]) for j in range(len(B.idx))
                   if S["res0"][j] is not None and float(np.min(S["res0"][j])) >= 0]
    out = {}
    for MM, j, Q0, Qp in frames:
        RS = MM.RS[j]
        sets = [(nm, m, X) for nm, (m, X) in list(MM.rigid.items()) + list(MM.link_pts.items())]
        sets += [(f"c{k}:m{m}", m, Pc) for k, (m, Pc) in enumerate(MM.contact) if len(Pc)]
        for nm, m, X in sets:
            w = MM.world(m, j, X) @ RS
            for tag, Qf, sw, a0, a1 in (("shell", Q0, 0.5 * PT.SH_W + 1.0, lo - 1.0, hi + 1.0), ("flange", Qp, 5.0, tc - hcar - 0.8, tc + hcar + 0.8)):
                h = w @ Qf; sv = h @ ax; az = np.degrees(np.arctan2(h @ f, h @ e)); mid = 0.5 * (a0 + a1); azr = (az - mid + 180.0) % 360.0 - 180.0 + mid
                ins = (np.abs(sv - s0) <= sw) & (azr >= a0) & (azr <= a1)
                if ins.any():
                    r = float(np.linalg.norm(AA._rad(h[ins], ax), axis=1).max())
                    if r > out.get(tag, (-1,))[0]: out[tag] = (round(r, 3), nm, j, "fit" if MM is M1 else "bench")
    return dict(skin=G["skin_R_liner"], **out)


def run_fix(outp, nc=110, nw=360, rls=None):
    """the corrected bridge: rl_fix from need_all (A: the design's own rule, up_clr 1.2 / flange + 3; B: the legal minimum
    up 1.0 / flange + 2), worn and X-checked on this bench; rls = a frozen list of rl_fix values (held)"""
    t0 = time.time(); S = UP.prepare(BASE, nc, nw, exact=True)
    res = dict(prepare_secs=round(time.time() - t0, 1), ideal=S["ideal"], mode="fix", bench=[nc, nw])
    print(json.dumps(dict(prepared=True, ideal=S["ideal"], secs=res["prepare_secs"])), flush=True)
    if rls is None:
        nd = need_all(S, dict(BASE, **PICK)); nd_fit = need_all(S, dict(BASE, **PICK), use_bench=False)
        res["need"] = nd; res["need_fit_only"] = nd_fit; print(json.dumps(dict(need=nd, need_fit_only=nd_fit)), flush=True)
        rls = [("A_up1.2", round(max(nd["skin"], nd["shell"][0] + 1.2, nd["flange"][0] + 3.0), 3)),
               ("B_up1.0", round(max(nd["skin"], nd["shell"][0] + 1.0, nd["flange"][0] + 2.0), 3))]
    for tag, rl in rls:
        hw = dict(PICK, rl_fix=rl); o = UP.wear(S, dict(BASE, **hw)); sm = UP.summary(o)
        print(json.dumps(dict(tag=tag, **sm), default=float), flush=True)
        x = xcheck(S, dict(BASE, **hw))
        print(json.dumps(dict(tag=tag, n_extra_jam=x["n_extra_jam"], lost_new=x["lost_new"], new_con=x["new_contacts"], rescored=x["rescored"],
                              margin={k: v for k, v in x["clearance_margin_taken"].items() if k != "lowest"}), default=float), flush=True)
        res[tag] = dict(rl_fix=rl, summary=sm, contacts=o["contacts"], underpass={k: v for k, v in o["underpass"].items() if k != "scan"}, xcheck=x)
        pp = UP.OS.perpose(S); pp.update(id=UP.ID, wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(BASE, **hw), exact=True, verifier=True, tag=tag)
        json.dump(pp, open(outp.replace(".json", f"_{tag}_perpose.json"), "w"), default=float)
        json.dump(res, open(outp, "w"), indent=1, default=float)
    print("done", round(time.time() - t0, 1), flush=True)


def run(mode, outp):
    nc, nw = (-1, -1) if mode == "held" else (110, 360)
    if mode == "cliff": nc, nw = 110, 360
    t0 = time.time(); S = UP.prepare(BASE, nc, nw, exact=True)
    res = dict(prepare_secs=round(time.time() - t0, 1), ideal=S["ideal"], params=dict(BASE, **PICK), mode=mode)
    print(json.dumps(dict(prepared=True, ideal=S["ideal"], secs=res["prepare_secs"])), flush=True)
    variants = [("pick", PICK, [0.0, None])]
    if mode == "cliff":                                       # the judge's pass clause: cliff margin >= 1.5 deg (delta + 0.5 / + 1.5, frozen bridge)
        variants = [("delta5.0", dict(PICK, delta=5.0), [0.0]), ("delta6.0", dict(PICK, delta=6.0), [0.0])]
    if mode == "claim":
        variants += [("foot12", dict(PICK, postL=12.0), [0.0]), ("foot20", dict(PICK, postL=20.0), [0.0])]
    for tag, hw, drops in variants:
        o = UP.wear(S, dict(BASE, **hw)); sm = UP.summary(o)
        print(json.dumps(dict(tag=tag, **sm), default=float), flush=True)
        r = dict(summary=sm, contacts=o["contacts"], why=o["why"], continuity={k: v for k, v in (o["continuity"] or {}).items() if k != "dropped"},
                 underpass={k: v for k, v in o["underpass"].items() if k != "scan"})
        if tag == "pick":
            try: r["th_margin"] = OM.BV.th_margin(S["M"], S["B"])
            except Exception as ex: r["th_margin"] = dict(err=repr(ex)[:200])
            pp = UP.OS.perpose(S); pp.update(id=UP.ID, wear=("held" if nc == -1 else f"bench({nc},{nw})"), params=dict(BASE, **hw), exact=True, verifier=True)
            json.dump(pp, open(outp.replace(".json", "_perpose.json"), "w"), default=float)
        for dr in drops:
            dv = float(o["underpass"]["defl_mm"]) if dr is None else dr
            x = xcheck(S, dict(BASE, **hw), drop=dv)
            print(json.dumps(dict(tag=tag, drop=dv, n_extra_jam=x["n_extra_jam"], lost_new=x["lost_new"], new_con=x["new_contacts"],
                                  rescored=x["rescored"], E=x["E_under_shell_taken"], margin={k: v for k, v in x["clearance_margin_taken"].items() if k != "lowest"}), default=float), flush=True)
            r[f"xcheck_drop{dv:g}"] = x
        res[tag] = r; json.dump(res, open(outp, "w"), indent=1, default=float)
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    os.environ["CB_EXACT"] = "1"
    if sys.argv[1] == "fix": run_fix(sys.argv[2])
    elif sys.argv[1] == "fixheld": run_fix(sys.argv[2], -1, -1, rls=json.loads(sys.argv[3]))
    else: run(sys.argv[1], sys.argv[2])
